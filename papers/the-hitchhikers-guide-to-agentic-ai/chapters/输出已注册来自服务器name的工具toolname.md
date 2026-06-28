            # 输出：已注册来自服务器 '{name}' 的工具 '{tool.name}'

    async def call_tool(self, tool_name: str, arguments: dict):
        """Route a tool call to the appropriate server."""
        """将工具调用路由到对应的服务器。"""
        if tool_name not in self.tool_registry:
            raise ValueError(f"Unknown tool: {tool_name}")
