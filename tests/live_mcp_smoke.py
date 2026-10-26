"""Manual hosted MCP smoke test; creates a fictional inventory audit and case."""
import asyncio
import json
import os
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

URL = os.getenv("STOCKGUARD_MCP_URL", "https://stockguard-ai-78wg.onrender.com/mcp")
TOKEN = os.environ["STOCKGUARD_API_TOKEN"]

def payload(response):
    if response.isError:
        raise AssertionError("MCP tool execution failed: " + repr(response.content)[:500])
    structured = getattr(response, "structuredContent", None)
    if structured:
        return structured
    for item in response.content:
        if getattr(item, "type", "") == "text":
            return json.loads(item.text)
    raise AssertionError("MCP tool did not return a JSON response")

async def main():
    async with streamable_http_client(URL, headers={"Authorization": "Bearer " + TOKEN}) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            available = {tool.name for tool in (await session.list_tools()).tools}
            required = {"list_products", "start_stock_check", "submit_count",
                        "submit_recount", "create_investigation"}
            assert required <= available, f"Missing tools: {required - available}"

            async def invoke(name, **arguments):
                return payload(await session.call_tool(name, arguments=arguments))

            listing = await invoke("list_products")
            assert any(p["code"] == "AMOX500" for p in listing["products"])
            audit = await invoke("start_stock_check", product_code="AMOX500")
            assert "expected" not in audit, "Blind audit exposed expected stock"
            aid = audit["audit_id"]
            first = await invoke("submit_count", audit_id=aid, physical_quantity=68)
            assert first["expected"] == 75 and first["shortage"] == 7, first
            assert first["estimated_retail_exposure_naira"] == 10500
            recounted = await invoke("submit_recount", audit_id=aid, physical_quantity=68)
            assert recounted["status"] == "discrepancy_confirmed"
            case = await invoke("create_investigation", audit_id=aid)
            assert case["investigation"]["audit_id"] == aid
            assert case["notification"]["status"] == "queued_for_review"
            duplicate = await invoke("create_investigation", audit_id=aid)
            assert duplicate["duplicate_prevented"]
            assert duplicate["investigation"]["id"] == case["investigation"]["id"]
            print("PASS: hosted MCP tools and persistent PostgreSQL writes")
            print("Audit reference:", aid)
            print("Investigation reference:", case["investigation"]["id"])
            print("Shortage: 7 packs; estimated retail exposure: NGN 10,500")
            print("Duplicate investigation prevented")

if __name__ == "__main__":
    asyncio.run(main())
