    # 输出：可用工具总数：{len(all_tools)}

    await host.close()


asyncio.run(main())
\end{lstlisting}


\subsection{Error Recovery and Reconnection}
\subsubsection{错误恢复与重连}
\label{error-recovery-and-reconnection}


Production MCP clients must handle server crashes and network interruptions:
生产环境中的 MCP 客户端必须处理服务器崩溃和网络中断：


\begin{lstlisting}[style=pythonstyle, caption={Resilient MCP Connection with Retry Logic}]
\begin{lstlisting}[style=pythonstyle, caption={带有重试逻辑的弹性 MCP 连接}]
import asyncio
import logging
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


logger = logging.getLogger(__name__)


async def resilient_tool_call(
    params: StdioServerParameters,
    tool_name: str,
    arguments: dict,
    max_retries: int = 3,
    backoff_base: float = 1.0
):
    """Call a tool with automatic reconnection on failure."""
    """在失败时自动重连调用工具。"""
    for attempt in range(max_retries):
        try:
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return await session.call_tool(tool_name, arguments)

        except (ConnectionError, TimeoutError, OSError) as e:
            if attempt == max_retries - 1:
                raise
            wait_time = backoff_base * (2 ** attempt)
            logger.warning(
                f"Tool call failed (attempt {attempt+1}/{max_retries}): {e}. "
                f"Retrying in {wait_time:.1f}s..."
            )
