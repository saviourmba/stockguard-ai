"""Deterministic, persistent demo inventory reconciliation backend."""
import os
import sqlite3
import uuid
from datetime import datetime, timezone

PRODUCTS = [
    ('AMOX500', 'Amoxicillin 500mg', 'pack', 100, 20, 0, 40, 0, 5, 1500),
    ('INHALER', 'Demo salbutamol inhaler', 'unit', 40, 0, 0, 12, 0, 0, 9000),
    ('VITC', 'Vitamin C tablets', 'bottle', 25, 5, 0, 10, 0, 0, 500),
]

def connect(db_path=None):
    if db_path is None and os.getenv('DATABASE_URL'):
        return connect_postgres(os.environ['DATABASE_URL'])
    path = db_path or os.getenv('STOCKGUARD_DB', 'stockguard.db')
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript("""
    CREATE TABLE IF NOT EXISTS products(code TEXT PRIMARY KEY,name TEXT,unit TEXT,opening INTEGER,received INTEGER,returns INTEGER,sold INTEGER,transfers_out INTEGER,writeoffs INTEGER,price_naira INTEGER);
    CREATE TABLE IF NOT EXISTS audits(id TEXT PRIMARY KEY,product_code TEXT NOT NULL,first_count INTEGER,recount INTEGER,status TEXT NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(product_code) REFERENCES products(code));
    CREATE TABLE IF NOT EXISTS investigations(id TEXT PRIMARY KEY,audit_id TEXT UNIQUE NOT NULL,status TEXT NOT NULL,shortage INTEGER NOT NULL,retail_exposure_naira INTEGER NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(audit_id) REFERENCES audits(id));
    CREATE TABLE IF NOT EXISTS notifications(id TEXT PRIMARY KEY,investigation_id TEXT UNIQUE NOT NULL,recipient TEXT NOT NULL,status TEXT NOT NULL,FOREIGN KEY(investigation_id) REFERENCES investigations(id));
    """)
    db.executemany('INSERT OR IGNORE INTO products VALUES (?,?,?,?,?,?,?,?,?,?)', PRODUCTS)
    db.commit()
    return db

def now():
    return datetime.now(timezone.utc).isoformat()

def dump(row):
    return dict(row) if row else None

def products(db):
    return [{'code': r['code'], 'name': r['name'], 'unit': r['unit']}
            for r in db.execute('SELECT code,name,unit FROM products ORDER BY code')]

def expected(p):
    return p['opening'] + p['received'] + p['returns'] - p['sold'] - p['transfers_out'] - p['writeoffs']

def _audit(db, audit_id):
    a = db.execute('SELECT * FROM audits WHERE id=?', (audit_id,)).fetchone()
    if not a:
        raise ValueError('Unknown audit ID')
    p = db.execute('SELECT * FROM products WHERE code=?', (a['product_code'],)).fetchone()
    return a, p

def start(db, code):
    p = db.execute('SELECT * FROM products WHERE code=?', (code.upper().strip(),)).fetchone()
    if not p:
        raise ValueError('Unknown product code; use list_products')
    aid = 'AUD-' + uuid.uuid4().hex[:8].upper()
    db.execute('INSERT INTO audits VALUES (?,?,?,?,?,?)', (aid, p['code'], None, None, 'awaiting_count', now()))
    db.commit()
    return {'audit_id': aid, 'product_code': p['code'], 'product_name': p['name'],
            'unit': p['unit'], 'status': 'awaiting_count'}

def validate_count(quantity):
    if type(quantity) is not int or quantity < 0:
        raise ValueError('Quantity must be a nonnegative whole number')

def result(a, p, count):
    e = expected(p)
    diff = count - e
    return {'audit_id': a['id'], 'product_code': p['code'], 'expected': e,
            'physical_count': count, 'variance': diff, 'shortage': max(-diff, 0),
            'estimated_retail_exposure_naira': max(-diff, 0) * p['price_naira'],
            'status': a['status'], 'unit': p['unit']}

def submit(db, audit_id, quantity):
    validate_count(quantity)
    a, p = _audit(db, audit_id)
    if a['status'] != 'awaiting_count':
        raise ValueError('First count already submitted')
    status = 'matched' if quantity == expected(p) else 'awaiting_recount'
    db.execute('UPDATE audits SET first_count=?,status=? WHERE id=?', (quantity, status, audit_id))
    db.commit()
    a, p = _audit(db, audit_id)
    return result(a, p, quantity)

def recount(db, audit_id, quantity):
    validate_count(quantity)
    a, p = _audit(db, audit_id)
    if a['status'] != 'awaiting_recount':
        raise ValueError('Audit is not awaiting a recount')
    status = 'resolved_on_recount' if quantity == expected(p) else 'discrepancy_confirmed'
    db.execute('UPDATE audits SET recount=?,status=? WHERE id=?', (quantity, status, audit_id))
    db.commit()
    a, p = _audit(db, audit_id)
    return result(a, p, quantity)

def investigate(db, audit_id):
    a, p = _audit(db, audit_id)
    prior = db.execute('SELECT * FROM investigations WHERE audit_id=?', (audit_id,)).fetchone()
    if prior:
        notice = db.execute('SELECT * FROM notifications WHERE investigation_id=?', (prior['id'],)).fetchone()
        return {'investigation': dump(prior), 'notification': dump(notice), 'duplicate_prevented': True}
    if a['status'] != 'discrepancy_confirmed':
        raise ValueError('Investigation requires a confirmed mismatch after recount')
    gap = max(expected(p) - a['recount'], 0)
    if gap == 0:
        raise ValueError('No shortage to investigate')
    iid = 'INV-' + uuid.uuid4().hex[:8].upper()
    nid = 'NOT-' + uuid.uuid4().hex[:8].upper()
    db.execute('INSERT INTO investigations VALUES (?,?,?,?,?,?)',
               (iid, audit_id, 'pending_owner_review', gap, gap * p['price_naira'], now()))
    db.execute('INSERT INTO notifications VALUES (?,?,?,?)',
               (nid, iid, 'store_owner', 'queued_for_review'))
    db.execute('UPDATE audits SET status=? WHERE id=?', ('investigation_open', audit_id))
    db.commit()
    return {'investigation': dump(db.execute('SELECT * FROM investigations WHERE id=?', (iid,)).fetchone()),
            'notification': dump(db.execute('SELECT * FROM notifications WHERE investigation_id=?', (iid,)).fetchone()),
            'duplicate_prevented': False}

class PostgresDB:
    """Small PostgreSQL adapter preserving the SQLite business logic."""
    def __init__(self, connection):
        self.connection = connection

    def execute(self, statement, parameters=()):
        sql = statement.replace('?', '%s')
        if sql.startswith('INSERT OR IGNORE INTO products VALUES'):
            sql = sql.replace('INSERT OR IGNORE', 'INSERT', 1) + ' ON CONFLICT (code) DO NOTHING'
        return self.connection.execute(sql, parameters)

    def executemany(self, statement, parameter_sets):
        for parameters in parameter_sets:
            self.execute(statement, parameters)

    def commit(self):
        self.connection.commit()

    def __enter__(self):
        return self

    def __exit__(self, typ, value, traceback):
        try:
            if typ is None:
                self.connection.commit()
            else:
                self.connection.rollback()
        finally:
            self.connection.close()

def connect_postgres(url):
    import psycopg
    from psycopg.rows import dict_row
    connection = psycopg.connect(url, row_factory=dict_row, connect_timeout=10)
    db = PostgresDB(connection)
    try:
        connection.execute("CREATE TABLE IF NOT EXISTS products(code TEXT PRIMARY KEY,name TEXT,unit TEXT,opening INTEGER,received INTEGER,returns INTEGER,sold INTEGER,transfers_out INTEGER,writeoffs INTEGER,price_naira INTEGER)")
        connection.execute("CREATE TABLE IF NOT EXISTS audits(id TEXT PRIMARY KEY,product_code TEXT NOT NULL REFERENCES products(code),first_count INTEGER,recount INTEGER,status TEXT NOT NULL,created_at TEXT NOT NULL)")
        connection.execute("CREATE TABLE IF NOT EXISTS investigations(id TEXT PRIMARY KEY,audit_id TEXT UNIQUE NOT NULL REFERENCES audits(id),status TEXT NOT NULL,shortage INTEGER NOT NULL,retail_exposure_naira INTEGER NOT NULL,created_at TEXT NOT NULL)")
        connection.execute("CREATE TABLE IF NOT EXISTS notifications(id TEXT PRIMARY KEY,investigation_id TEXT UNIQUE NOT NULL REFERENCES investigations(id),recipient TEXT NOT NULL,status TEXT NOT NULL)")
        db.executemany('INSERT OR IGNORE INTO products VALUES (?,?,?,?,?,?,?,?,?,?)', PRODUCTS)
        db.commit()
        return db
    except Exception:
        connection.rollback()
        connection.close()
        raise
