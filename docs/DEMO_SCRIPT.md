# StockGuard AI — three-minute demonstration script

**Business:** Harbour Pharmacy Demo (fictional single-branch physical pharmacy).  
**Status:** Presenter script only. Chord WhatsApp simulator end-to-end test is **not yet verified** due to a billing settlement error. Do not portray this script as a completed recording.

## 0:00–0:25 — Problem and product
“Physical retailers can discover stock shortages only at the end of a shift. A mismatch can result from a missed sale, counting mistake or an unexplained stock movement, so the goal is to detect exceptions quickly without accusing staff. StockGuard gives a manager a guided WhatsApp blind count and creates a documented case for the owner to review.”

Show the published StockGuard teammate and its skill in Chord.

## 0:25–0:45 — Connection
Show the **StockGuard Inventory Server** under Chord Custom Tools (MCP). Point out the successful health check and five discovered tools. Do not show the API token.

## 0:45–2:25 — Full simulator conversation (to execute once Chord billing is fixed)
Send each *manager* message as the simulator user; let StockGuard respond in its own words and show the actual tool calls.

1. Manager: “Hi StockGuard. I’m the Harbour Pharmacy Demo manager. Start today’s stock check.”
   - Expected agent action: `list_products` returns seeded demo items.
2. Manager: “Check AMOX500.”
   - Expected action: `start_stock_check`; StockGuard gives an audit ID and requests a blind physical count **without revealing the expected 75 packs**.
3. Manager: “I counted 68 packs.”
   - Expected action: `submit_count`; tool reports 75 expected, 7 missing, **₦10,500 estimated retail value of shortage**. Agent requests a recount.
4. Manager: “I counted again. Still 68 packs.”
   - Expected action: `submit_recount`; mismatch confirmed; agent asks permission before escalating.
5. Manager: “Yes, create an investigation for owner review.”
   - Expected action: `create_investigation`; agent gives the **actual** returned investigation reference and queued notification status. It must **not** claim a WhatsApp/email alert was delivered or that theft occurred.

## 2:25–2:45 — Proof of saved action
Show actual tool output / recorded investigation reference from the live session. If that fails, do not substitute an invented case number.

## 2:45–3:00 — Honest constraints
“This is a fictional data MVP: no real point-of-sale integration or customer information, no inventory write-offs, no employee accusation and no delivered owner notification. Production would need POS connectivity, identity controls, monitoring, and message delivery.”

## Recording checklist
- Capture screen and voice; keep API tokens and database URLs hidden.
- Record the simulator **only after** completing the real conversation.
- If Chord still errors, record a clearly labeled *technical fallback demo* of the passing GitHub live MCP test and explain that the required simulator conversation is outstanding. Do not call the fallback a compliant WhatsApp demo.
