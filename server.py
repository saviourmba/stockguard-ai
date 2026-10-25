"""Chord-compatible Streamable HTTP MCP service. Run: python server.py"""
import os
from mcp.server.fastmcp import FastMCP
from stockguard_core import connect, products, start, submit, recount, investigate

mcp = FastMCP('StockGuard Demo', host='0.0.0.0', port=int(os.getenv('PORT','8000')), stateless_http=True, json_response=True)

@mcp.tool()
def list_products() -> dict:
    """List fictional physical-store products available for a blind stock count."""
    with connect() as db: return {'products': products(db)}

@mcp.tool()
def start_stock_check(product_code: str) -> dict:
    """Open an audit and return its ID WITHOUT disclosing expected stock."""
    with connect() as db: return start(db,product_code)

@mcp.tool()
def submit_count(audit_id: str, physical_quantity: int) -> dict:
    """Save the first physical count, calculate expected stock, and require recount on mismatch."""
    with connect() as db: return submit(db,audit_id,physical_quantity)

@mcp.tool()
def submit_recount(audit_id: str, physical_quantity: int) -> dict:
    """Save a recount and confirm or resolve the variance."""
    with connect() as db: return recount(db,audit_id,physical_quantity)

@mcp.tool()
def create_investigation(audit_id: str) -> dict:
    """Persist a confirmed shortage case plus queued owner notification record; does not deliver a message."""
    with connect() as db: return investigate(db,audit_id)

if __name__ == '__main__': mcp.run(transport='streamable-http')
