import pytest
from stockguard_core import connect,start,submit,recount,investigate,expected

@pytest.fixture
def db():
    d=connect(':memory:')
    yield d
    d.close()

def test_blind_count_and_shortage(db):
    a=start(db,'AMOX500')
    assert 'expected' not in a
    first=submit(db,a['audit_id'],68)
    assert (first['expected'],first['shortage'],first['estimated_retail_exposure_naira'])==(75,7,10500)
    assert first['status']=='awaiting_recount'
    again=recount(db,a['audit_id'],68)
    assert again['status']=='discrepancy_confirmed'
    case=investigate(db,a['audit_id'])
    assert case['investigation']['shortage']==7
    assert case['notification']['status']=='queued_for_review'
    assert investigate(db,a['audit_id'])['duplicate_prevented'] is True

def test_recount_resolution(db):
    a=start(db,'INHALER')
    assert submit(db,a['audit_id'],25)['status']=='awaiting_recount'
    assert recount(db,a['audit_id'],28)['status']=='resolved_on_recount'
    with pytest.raises(ValueError): investigate(db,a['audit_id'])

def test_invalid_and_duplicate(db):
    a=start(db,'VITC')
    with pytest.raises(ValueError): submit(db,a['audit_id'],-1)
    assert submit(db,a['audit_id'],20)['status']=='matched'
    with pytest.raises(ValueError): submit(db,a['audit_id'],20)
    with pytest.raises(ValueError): investigate(db,a['audit_id'])

def test_investigation_is_persisted_and_reusable(db):
    audit = start(db, 'AMOX500')
    submit(db, audit['audit_id'], 68)
    recount(db, audit['audit_id'], 68)
    created = investigate(db, audit['audit_id'])
    assert created['investigation']['status'] == 'pending_owner_review'
    assert created['investigation']['retail_exposure_naira'] == 10500
    assert created['notification']['investigation_id'] == created['investigation']['id']
    assert db.execute('SELECT COUNT(*) FROM investigations').fetchone()[0] == 1
    second = investigate(db, audit['audit_id'])
    assert second['duplicate_prevented'] is True
    assert second['investigation']['id'] == created['investigation']['id']
    assert db.execute('SELECT COUNT(*) FROM investigations').fetchone()[0] == 1

def test_invalid_count_types_and_unknown_product(db):
    for invalid in [-1, 2.5, True, '10']:
        a = start(db, 'VITC')
        with pytest.raises(ValueError):
            submit(db, a['audit_id'], invalid)
    with pytest.raises(ValueError):
        start(db, 'UNKNOWN')

def test_surplus_does_not_create_shortage_case(db):
    a = start(db, 'INHALER')
    first = submit(db, a['audit_id'], 30)
    assert first['variance'] == 2
    assert first['estimated_retail_exposure_naira'] == 0
    assert recount(db, a['audit_id'], 30)['status'] == 'discrepancy_confirmed'
    with pytest.raises(ValueError, match='No shortage'):
        investigate(db, a['audit_id'])
