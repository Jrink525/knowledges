    # "completed" | "failed" | "rejected"
    duration_ms: int
    error_code: str | None
\end{lstlisting}


\section{Implementation Example: Multi-Agent Research Workflow}
\section{实现示例：多 Agent 研究工作流}
\label{sec:a2a:implementation}


The following example demonstrates a complete multi-agent research workflow using A2A: an \texttt{OrchestratorAgent} decomposes a research question, delegates to specialist agents, and synthesizes their results.
以下示例展示了使用 A2A 的完整多 Agent 研究工作流：\texttt{OrchestratorAgent} 分解研究问题，委托给专业 agent，并综合它们的结果。


\begin{lstlisting}[style=pythonstyle]
"""
Multi-agent research workflow using A2A protocol.
Demonstrates: Agent Cards, A2A client/server, task lifecycle,
multi-turn interaction, and agent handoffs.
"""
"""
使用 A2A 协议的多 Agent 研究工作流。
演示：Agent Cards、A2A 客户端/服务器、任务生命周期、
多轮交互和 agent 交接。
"""


import asyncio
import json
import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone


import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field


