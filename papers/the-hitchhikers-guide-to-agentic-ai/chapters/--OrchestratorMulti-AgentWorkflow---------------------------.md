# -- Orchestrator: Multi-Agent Workflow ----------------------------------------
```

```python
class ResearchAgent:
    """
    一个专门的研究智能体，用于搜索文献并总结关于给定主题的发现。
    """

    AGENT_CARD = {
        "name": "ResearchAgent",
        "description": "搜索学术文献并综合研究结果。",
        "url": "https://research-agent.example.com/a2a",
        "version": "1.0.0",
        "capabilities": {
            "streaming": True,  # 支持流式输出
            "pushNotifications": False,  # 不支持推送通知
            "stateTransitionHistory": True  # 记录状态转换历史
        },
        "authentication": {"schemes": ["Bearer"]},
        "skills": [{
            "id": "literature-search",
            "name": "文献搜索",
            "description": "搜索并总结关于某个主题的学术论文。",
            "tags": ["research", "literature", "academic", "papers"],  # 标签不变
            "examples": [
                "总结最近关于Transformer注意力机制的论文。",
                "关于RLHF用于代码生成的文献怎么说？"
            ],
            "inputModes": ["text"],
            "outputModes": ["text", "data"]
        }]
    }

    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.app = FastAPI(title="ResearchAgent A2A Server")
        self._register_routes()

    def _register_routes(self):
        @self.app.get("/.well-known/agent.json")
        async def agent_card():
            return self.AGENT_CARD

        @self.app.post("/tasks/send")
        async def send_task(request: Request):
            body = await request.json()
            task = await self._create_and_run_task(body)
            return task.model_dump()

        @self.app.post("/tasks/sendSubscribe")
        async def send_subscribe(request: Request):
            body = await request.json()
            return StreamingResponse(
                self._stream_task(body),
                media_type="text/event-stream"
            )

        @self.app.get("/tasks/{task_id}")
        async def get_task(task_id: str):
            if task_id not in self.tasks:
                raise HTTPException(status_code=404, detail="任务未找到")
            return self.tasks[task_id].model_dump()

    async def _create_and_run_task(self, body: dict) -> Task:
        task_id = body.get("id", str(uuid.uuid4()))
        message = Message(**body["message"])

        task = Task(
            id=task_id,
            status=TaskStatus(state="submitted"),
            messages=[message],
            metadata=body.get("metadata", {})
        )
        self.tasks[task_id] = task

