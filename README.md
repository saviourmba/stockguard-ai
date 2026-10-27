# StockGuard AI — Chord Custom MCP Backend

Demo inventory reconciliation agent for **Harbour Pharmacy Demo**, using fictional data only.

## Requirements
- Python 3.11+
- Chord teammate with `SKILL.md` uploaded
- Render Web Service and Render Postgres (a free database may expire after 30 days)

## Local checks
```bash
pip install -r requirements.txt
pytest -q
```
Tests use temporary SQLite databases. The hosted service uses PostgreSQL.

## Deploy to Render
1. Create a Render Postgres database in the same region as the Web Service.
2. On the Postgres page, copy the **Internal Database URL**. It is secret; never commit it or include it in screenshots.
3. In your Render Web Service, set build command `pip install -r requirements.txt` and start command `python server.py`.
4. Add environment variables in Render:
   - `DATABASE_URL`: the internal PostgreSQL URL.
   - `STOCKGUARD_API_TOKEN`: a randomly generated high-entropy secret (use Render's Generate button).
5. Deploy and verify `https://<your-service>.onrender.com/health` responds with `{"status":"ok"}`.
6. In Chord, register custom MCP server URL `https://<your-service>.onrender.com/mcp`. Configure an Authorization header with `Bearer <STOCKGUARD_API_TOKEN>` if supported. **Do not put the secret in the skill file or GitHub.**
7. Test the five exposed tools with Chord's tool connection and WhatsApp simulator.

**If Chord cannot send a bearer token to a custom MCP server, do not disable authentication.** Check the supported authentication settings and adapt the server if necessary.

## Demo scenario
- Product: `AMOX500`
- Expected stock: 100 opening + 20 received - 40 sold - 5 write-offs = **75 packs**.
- Count: 68; recount: 68; shortage: 7 packs; estimated retail exposure: **₦10,500**.
- Investigation creates a case and **queued notification record**, not an actual message to the owner.

## Security and limitations
- MCP requires `Authorization: Bearer <STOCKGUARD_API_TOKEN>`; `/health` is public.
- One shared demo credential; no individual user authentication or roles. The simulator assumes an authorised manager.
- PostgreSQL retains records across Web Service restarts; free Render Postgres instances can have expiry limitations.
- Free Web Services may spin down when idle.
- Fictional seeded inventory, not a live POS integration or real customer data.
- No medical advice, inventory adjustments or theft accusations.
- If PostgreSQL is unavailable, the tools fail instead of fabricating stock data.

## AI assistance
AI helped draft skill instructions, design the prototype, and write implementation and tests. End-to-end Chord validation remains required.

## Assessment evidence and handover
- [Deployment field notes](docs/DEPLOYMENT_FIELD_NOTES.md)
- [Business owner go-live note](docs/GO_LIVE_NOTE.md)
- [Backend regression test workflow](.github/workflows/tests.yml)
- [Manual hosted MCP integration test](.github/workflows/live-mcp.yml)

The hosted MCP integration test passed in GitHub Actions run #2 on 27 October 2026, but a complete Chord WhatsApp simulator conversation has **not yet** been verified due to a billing settlement error. Treat the script as a rehearsal until the simulator demonstration succeeds. The repository is private: grant reviewers access when sharing the code.
