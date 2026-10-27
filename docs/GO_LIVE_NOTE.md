# Go-live note to Harbour Pharmacy owner

**StockGuard AI — fictional pilot handover**

StockGuard is a WhatsApp-style inventory-checking assistant for a store manager. At closing time, the manager chooses a product and counts the physical packs or units without first seeing the system's expected balance. StockGuard compares the entered count with recorded opening stock, deliveries, sales and adjustments, requests a recount if there is a difference, and—with manager approval—records an investigation case for owner review. This can help identify missing stock earlier and provide consistent documentation.

**What it does not do:** It cannot prove theft or identify responsible employees. A discrepancy can reflect recording errors, delays or genuine stock movements. The current prototype uses fictional pharmacy inventory, not your live point-of-sale or stock records. It never changes inventory balances, dispenses medicines, or gives clinical advice. An “owner notification” is only a queued database item; the owner is **not** automatically messaged.

**Before using with real customers or staff:** Connect to the real POS and stock system with reconciled, timestamped movement records and consistent pack/unit definitions; authenticate each manager and enforce store-level access; secure API keys and WhatsApp business registration; enable reliable outbound owner alerts, error monitoring, backups and escalation when any tool or message fails; define how pending sales, returns and recount disputes are handled; and add pharmacy-specific batch/expiry and regulatory safeguards as appropriate. Pilot in one store with parallel manual counts first, then measure count completion, exception rates and time-to-resolution before expanding.

**Recommendation:** Treat the present build as a technical proof of concept, not a production stock-control or fraud-detection system.
