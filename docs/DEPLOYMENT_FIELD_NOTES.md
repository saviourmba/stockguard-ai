# StockGuard AI — Deployment field notes

**Scope:** Chord teammate, custom Streamable HTTP MCP server, Python, Render and PostgreSQL. All inventory records are fictional.

## Issue 1 — Render startup failed because of an incompatible MCP SDK
- **What happened:** Initial Render build succeeded, but the service exited with status 1 when starting `python server.py`.
- **Evidence:** `ModuleNotFoundError: No module named 'mcp.server.fastmcp'`. The logs said MCP v2 moved FastMCP to `MCPServer`.
- **How isolated:** The traceback failed on the MCP import before handling any tool calls; `requirements.txt` allowed `mcp>=1.9,<3`, which included an incompatible major release.
- **Fix:** Restricted the dependency to `mcp>=1.9,<2` (commit `77af5ac`); redeployment became **Live**.
- **Product/documentation improvement:** Provide a copyable minimal MCP server template with version-pinned dependencies, explicit compatibility guidance, and an import/startup validation step before deploy.
- **Outcome:** Resolved. Render displayed a live service and Chord subsequently discovered all five tools.

## Issue 2 — Chord billing settlement error on attempted agent response
- **What happened:** In Chord direct chat, the manager asked to retrieve today's products. No assistant answer appeared; UI displayed `Billing settlement failed after the model completed; do not retry automatically`.
- **How investigated:** Reviewed Chord billing statement (one observed confirmed debit of 0.03 credits) and teammate Activity; workspace credits had fallen from 50 to 43.85 over broader activity (not attributable solely to this request). Render logs showed `ListToolsRequest` and successful `POST /mcp 200` responses. Chord Health showed **ok, 258 ms** with all five tools discovered. A successful `CallToolRequest` for the failed Chord conversation was **not verified**.
- **Fix/workaround:** Avoided repeated chargeable retries, emailed the TSG Labs contact, and validated the same hosted tools independently using an authenticated GitHub Actions MCP client. Awaiting Chord response; issue remains open.
- **Product improvement:** Show a correlation ID, settlement state, charged amount, whether the model responded and whether tool calls committed, and safe retry guidance for non-idempotent actions; link errors to detailed execution traces.
- **Outcome:** Chord conversation still unverified; independent hosted MCP end-to-end test subsequently passed.

## Issue 3 — Live smoke test used an outdated MCP client call signature
- **What happened:** First GitHub Actions live MCP integration workflow failed (exit 1).
- **Evidence:** `TypeError: streamable_http_client() got an unexpected keyword argument 'headers'`.
- **How isolated:** Read full GitHub Actions job logs. Dependency installation and GitHub Actions secret injection had succeeded; exception occurred in the test harness before tool execution.
- **Fix:** Passed the Bearer header through an `httpx.AsyncClient` supplied via `http_client` (commit `fee3955`).
- **Product/docs improvement:** Publish a working, versioned authenticated Streamable HTTP client example and an example integration smoke test.
- **Outcome:** GitHub Actions `StockGuard live MCP integration #2` completed successfully in 21 seconds (commit `fee3955`), testing product lookup, blind audit, first count, recount, investigation and duplicate-case prevention.

## Additional implementation improvement — Investigation transaction lifecycle
- **Finding:** Code review identified a possible attempt to read investigation records after a PostgreSQL adapter context manager had closed its connection.
- **Resolution:** Updated case creation to commit and then read back records before the outer caller closes the connection; added regression tests.
- **Evidence:** GitHub backend test workflow passed. The live MCP workflow later passed, covering case creation.

## Remaining verification
- A complete live Chord **WhatsApp simulator** conversation has not been established.
- The queued owner notification is a database record, **not** a delivered owner alert.
- Free hosting may spin down and the free database has a limited life; this is a short-term demo.
