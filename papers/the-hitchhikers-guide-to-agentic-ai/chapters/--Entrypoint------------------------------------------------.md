# -- Entry point ----------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()  # defaults to stdio transport
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={完整 MCP 服务器：笔记管理工具（FastMCP）}]
#!/usr/bin/env python3
"""
一个简单的 MCP 服务器，提供笔记管理工具和资源。
安装：pip install "mcp[cli]"
运行：mcp run notes_server.py        (标准输入输出)
      mcp run notes_server.py --transport streamable-http  (HTTP)
"""
from pathlib import Path
from mcp.server.fastmcp import FastMCP


