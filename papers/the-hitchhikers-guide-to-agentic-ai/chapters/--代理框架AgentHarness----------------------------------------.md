# -- 代理框架（Agent Harness）----------------------------------------

```python
class AgentHarness:
    """
    Production agent harness implementing the ReAct loop
    with full context management, tool integration,
    error handling, and observability.
    """
    """
    生产级智能体框架，实现ReAct循环，
    包含完整的上下文管理、工具集成、
    错误处理和可观测性。
    """
    MAX_ITERATIONS = 50

    def __init__(
        self,
        model:        str,
        system_prompt: str,
        tools:        list[ToolDefinition],
        max_tokens:   int = 128_000,
        approval_cb:  Optional[Callable] = None,
        client:       Optional[AsyncOpenAI] = None,
    ):
        self.model   = model
        self.client  = client or AsyncOpenAI()
        self.ctx_mgr = ContextManager(model, max_tokens)
        self.executor = ToolExecutor(tools, approval_cb)
        self.loop_det = LoopDetector()
        self.tools    = tools

