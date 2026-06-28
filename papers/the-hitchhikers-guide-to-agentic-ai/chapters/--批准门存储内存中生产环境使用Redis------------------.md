# -- 批准门存储（内存中；生产环境使用Redis）------------------


approval_store: dict[str, asyncio.Event] = {}
approval_results: dict[str, dict] = {}


