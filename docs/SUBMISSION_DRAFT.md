# TSG Labs — StockGuard AI submission (draft)

**Role preference:** Product Management / Technical Product Management (confirm intended preference before submission).

**Problem statement (4 sentences):**
Harbour Pharmacy Demo is a fictional single-branch physical pharmacy used to model a real operational problem in small retailers. At day-end, managers often lack a quick, consistent way to compare physical shelf counts against recorded sales and stock movements, leaving discrepancies unidentified or poorly documented. StockGuard AI guides blind counts over WhatsApp, asks for a recount, and creates a case for owner review when shortages remain—saving manager time and improving loss visibility without accusing staff. I deliberately excluded POS integration, real alerts, employee investigations and clinical or medicine-dispensing decisions to keep the MVP focused and safe.

**Agent:** StockGuard AI on Chord; published `SKILL.md` and a custom MCP inventory server.

**Code:** https://github.com/saviourmba/stockguard-ai (currently private; provide TSG Labs reviewer access before submission).

**Backend:** https://stockguard-ai-78wg.onrender.com/health

**Evidence:** GitHub Actions backend regression tests passed, and `StockGuard live MCP integration #2` passed after a client signature fix. Chord MCP Health passed (258 ms), with five discovered tools. **A completed Chord WhatsApp simulator conversation is not yet verified.**

**Recording:** TODO — record the completed simulator demonstration if Chord billing is resolved. Do not present a backend smoke-test recording as a simulator demonstration.

**Field notes:** `docs/DEPLOYMENT_FIELD_NOTES.md`.

**Go-live note:** `docs/GO_LIVE_NOTE.md`.

**AI usage disclosure:** AI assisted with concept scoping, skill drafting, implementation, tests, debugging and documentation. GitHub Actions and Render provided the execution evidence; the actual Chord simulator outcome must be reported separately.

**Submission blockers:** Chord showed “Billing settlement failed after the model completed; do not retry automatically”; support has been contacted. Preserve access, secrets, and free-service availability during the review window.
