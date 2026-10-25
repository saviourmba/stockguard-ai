"""Chord-compatible Streamable HTTP MCP service. Run: python server.py"""
import os
import hmac
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from stockguard_core import connect, products, start, submit, recount, investigate

mcp = FastMCP('StockGuard Demo', host='0.0.0.0', port=int(os.getenv('PORT', '8000')), stateless_http=True, json_response=True)

@mcp.tool()
def list_products() -> dict:
    """List fictional physical-store products available for a blind stock count."""
    with connect() as db:
        return {'products': products(db)}

@mcp.tool()
def start_stock_check(product_code: str) -> dict:
    """Open an audit and return its ID WITHOUT disclosing expected stock."""
    with connect() as db:
        return start(db, product_code)

@mcp.tool()
def submit_count(audit_id: str, physical_quantity: int) -> dict:
    """Save the first physical count, calculate expected stock, and require recount on mismatch."""
    with connect() as db:
        return submit(db, audit_id, physical_quantity)

@mcp.tool()
def submit_recount(audit_id: str, physical_quantity: int) -> dict:
    """Save a recount and confirm or resolve the variance."""
    with connect() as db:
        return recount(db, audit_id, physical_quantity)

@mcp.tool()
def create_investigation(audit_id: str) -> dict:
    """Persist a confirmed shortage case plus queued owner notification record; does not deliver a message."""
    with connect() as db:
        return investigate(db, audit_id)

# TLS is terminated by Render. Bearer authentication protects tool discovery and calls.
# Restrict allowed hostnames as an additional safeguard before production use.
mcp.settings.transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)
_mcp_app = mcp.streamable_http_app()

class TokenProtectedApp:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            if scope.get('path') == '/health':
                body = b'{"status":"ok"}'
                await send({'type': 'http.response.start', 'status': 200, 'headers': [(b'content-type', b'application/json')]})
                await send({'type': 'http.response.body', 'body': body})
                return
            key = os.getenv('STOCKGUARD_API_TOKEN', '')
            auth = dict(scope.get('headers', [])).get(b'authorization', b'').decode('utf-8', errors='replace')
            if not key or not hmac.compare_digest(auth, 'Bearer ' + key):
                await send({'type': 'http.response.start', 'status': 401, 'headers': [(b'content-type', b'application/json'), (b'www-authenticate', b'Bearer')]})
                await send({'type': 'http.response.body', 'body': b'{"error":"Unauthorized"}'})
                return
        await self.wrapped(scope, receive, send)

app = TokenProtectedApp(_mcp_app)

if __name__ == '__main__':
    import uvicorn
    if not os.getenv('STOCKGUARD_API_TOKEN'):
        raise RuntimeError('STOCKGUARD_API_TOKEN must be set before serving HTTP requests')
    if not os.getenv('DATABASE_URL'):
        raise RuntimeError('DATABASE_URL must be set for persistent hosted storage')
    uvicorn.run(app, host='0.0.0.0', port=int(os.getenv('PORT', '8000')))
