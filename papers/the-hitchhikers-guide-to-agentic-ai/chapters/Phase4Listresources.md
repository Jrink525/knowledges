            # Phase 4: List resources
            resources = await session.list_resources()
            print(f"\nAvailable resources: {len(resources.resources)}")


asyncio.run(main())
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={MCP 客户端：连接并调用工具}]
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
