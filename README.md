# StockGuard AI — TSG Labs Chord Build Exercise (Starter)

This project creates a **fictional pharmacy inventory reconciliation agent**: a manager counts stock through WhatsApp; Chord calls a custom MCP service; the service saves the count, computes the variance, asks for a recount, and persists a case for owner review when a shortage is confirmed. No employee is accused of theft. No patient/customer data is used.

## Files
- `SKILL.md`: upload as the teammate's skill and instruction file.
- `server.py`: Streamable HTTP MCP server with five custom tools.
- `stockguard_core.py`: SQLite-backed inventory, audit, investigation and notification logic.
- `tests/test_stockguard.py`: business logic tests.
- `requirements.txt`: Python dependencies.

## Run locally
Python 3.11+ recommended.
```bash
python -m pip install -r requirements.txt
pytest -q
python server.py
```
The MCP endpoint is `http://localhost:8000/mcp` for local testing. Chord **cannot** reach localhost: deploy the server to a persistent HTTPS host first and point Chord to `https://YOUR-HOST/mcp`.

Set `STOCKGUARD_DB` to a persistent writable SQLite path on your host. Important: temporary/ephemeral host storage loses audits and cases on restart. Use persistent disk or replace SQLite with a hosted persistent database for the demo. **Do not use real customer data.**

### Chord setup
1. In Chord: **Teammates → Create a teammate**; upload `SKILL.md`, review, publish and activate.
2. Host `server.py` publicly over HTTPS with dependencies installed. For a production-style deployment, restrict access with a remote bearer token or other supported authentication; never expose write actions without protection on a public internet endpoint. A private MCP host cannot be reached by Chord.
3. In workspace MCP settings, register your `https://HOST/mcp` server with Streamable HTTP and appropriate credentials. Enable it; scope the server to StockGuard; confirm tool discovery and health.
4. In teammate settings → Tools, ensure tools are on and connected. Test in teammate chat, then use the TSG Labs WhatsApp simulator.
5. Verify the actual SQLite `audits`, `investigations`, and `notifications` records after running the simulator. A healthy MCP connection is not proof that a business tool executed.

### Example demo scenario
- “Start today's stock check.”
- Select `AMOX500`.
- First count: `68` packs (expected 75, hidden until first submission).
- Recount: `68` packs.
- “Yes, open an investigation.”
- Confirm the tool returns `INV-...` and a queued owner-review record. This is not an actual delivered alert.

### Sample inventory and movement records
| Code | Opening | Received | Returns | Sold | Transfers out | Write-offs | Expected | Retail unit value |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| AMOX500 | 100 | 20 | 0 | 40 | 0 | 5 | 75 | ₦1,500 |
| INHALER | 40 | 0 | 0 | 12 | 0 | 0 | 28 | ₦9,000 |
| VITC | 25 | 5 | 0 | 10 | 0 | 0 | 20 | ₦500 |

This data is fixed demo data rather than a live POS integration. Expected stock = opening + received + returns − sold − transfers out − write-offs. Retail exposure = shortage × selling price, **not confirmed lost revenue**.

### Boundaries and production gaps
- Simulator user is assumed to be a manager; production needs manager authentication, secure store-level tenancy and audit logs.
- Owner alerts are queued database **records**, not real WhatsApp notifications.
- No batch-level pharmaceutical controls, controlled medicine workflows, live stock adjustments, or medical guidance.
- No real POS connection; an actual deployment needs authenticated movement feeds and corrections for backdated transactions.
- Avoid public hosting without server-side auth and persistence.

### AI use disclosure
Used ChatGPT to draft the initial business skill, prototype code, dataset and automated tests. Review the code and record any additional AI assistance and manual changes before submission.
