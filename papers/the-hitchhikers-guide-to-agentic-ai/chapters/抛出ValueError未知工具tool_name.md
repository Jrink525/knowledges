            # 抛出 ValueError：未知工具：{tool_name}

        server_name, _ = self.tool_registry[tool_name]
        session = self.sessions[server_name]
        return await session.call_tool(tool_name, arguments)

    async def get_all_tools(self) -> list:
        """Return all tools across all connected servers."""
        """返回所有已连接服务器上的全部工具。"""
        return [tool for _, tool in self.tool_registry.values()]

    async def close(self):
        await self._exit_stack.aclose()

async def main():
    host = MCPHost()

