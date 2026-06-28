# -- Approval gate store (in-memory; use Redis in production) ------------------


approval_store: dict[str, asyncio.Event] = {}
approval_results: dict[str, dict] = {}


