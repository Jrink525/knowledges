            # 日志警告：工具调用失败（第 {attempt+1}/{max_retries} 次尝试）：{e}。将在 {wait_time:.1f} 秒后重试...
            await asyncio.sleep(wait_time)
\end{lstlisting}


\section{The MCP Ecosystem}
\section{MCP 生态系统}
\label{sec:mcp:ecosystem}


Since its release, MCP has attracted a rapidly growing ecosystem of servers, clients, and tooling.2
自发布以来，MCP 已吸引了由服务器、客户端和工具组成的快速增长生态系统。2


\subsection{Popular MCP Servers}
\subsubsection{流行的 MCP 服务器}
\label{popular-mcp-servers}


\begin{keybox}[Notable MCP Servers (Official and Community)]
\begin{keybox}[知名的 MCP 服务器（官方与社区）]
{\small
\begin{tabular}{@{}llp{7.5cm}@{}}
\toprule
\textbf{Server} & \textbf{Category} & \textbf{Key Capabilities} \\
\textbf{服务器} & \textbf{类别} & \textbf{关键能力} \\
\midrule
\texttt{server-filesystem} & Local I/O & Read/write files, directory listing, search \\
\texttt{server-filesystem} & 本地 I/O & 读写文件、目录列表、搜索 \\
\texttt{server-github} & Version Control & Issues, PRs, commits, code search, file access \\
\texttt{server-github} & 版本控制 & Issues、PRs、commits、代码搜索、文件访问 \\
\texttt{server-postgres} & Database & Read-only SQL queries, schema inspection \\
\texttt{server-postgres} & 数据库 & 只读 SQL 查询、模式检查 \\
\texttt{server-sqlite} & Database & Full SQLite access, schema management \\
\texttt{server-sqlite} & 数据库 & 完整的 SQLite 访问、模式管理 \\
\texttt{server-brave-search} & Web & Web search, news search via Brave API \\
\texttt{server-brave-search} & 网络 & 通过 Brave API 进行网页搜索、新闻搜索 \\
\texttt{server-slack} & Communication & Post messages, read channels, search \\
\texttt{server-slack} & 通讯 & 发送消息、读取频道、搜索 \\
\texttt{server-google-maps} & Geospatial & Geocoding, directions, place search \\
\texttt{server-google-maps} & 地理空间 & 地理编码、导航、地点搜索 \\
\texttt{server-puppeteer} & Browser & Web scraping, screenshot, form interaction \\
\texttt{server-puppeteer} & 浏览器 & 网页抓取、截图、表单交互 \\
\texttt{server-memory} & Knowledge & Persistent knowledge graph across sessions \\
\texttt{server-memory} & 知识 & 跨会话的持久化知识图谱 \\
\texttt{server-sequential-thinking} & Reasoning & Structured multi-step reasoning scaffolding \\
\texttt{server-sequential-thinking} & 推理 & 结构化的多步推理框架 \\
\bottomrule
\end{tabular}
}
\end{keybox}


\subsection{MCP in Production Applications}
\subsubsection{MCP 在生产应用程序中的应用}
\label{mcp-in-production-applications}


MCP has been adopted by several major AI development tools:
MCP 已被多个主要 AI 开发工具所采用：


\textbf{Claude Desktop}
\textbf{Claude Desktop（Claude 桌面版）}


Anthropic’s desktop application3 was the first major MCP host. Users configure servers in a JSON config file; Claude can then use tools from all connected servers in any conversation.
Anthropic 的桌面应用程序3是第一个主要的 MCP 主机。用户在 JSON 配置文件中配置服务器；随后 Claude 可以在任意对话中使用所有已连接服务器的工具。


\textbf{Cursor}
\textbf{Cursor}


The AI-powered code editor4 supports MCP servers, allowing developers to connect their development tools (databases, issue trackers, documentation systems) directly to the coding assistant.
这款 AI 驱动的代码编辑器4支持 MCP 服务器，允许开发者将其开发工具（数据库、问题追踪器、文档系统）直接连接到编码助手。


\textbf{VS Code (GitHub Copilot)}
\textbf{VS Code（GitHub Copilot）}


Microsoft added MCP support5 to GitHub Copilot in VS Code, enabling the coding assistant to access project-specific tools and data sources.
微软已在 VS Code 的 GitHub Copilot 中添加了 MCP 支持5，使编码助手能够访问项目特定的工具和数据源。


\textbf{Custom Agents}
\textbf{自定义智能体}


The open-source community has built MCP support into frameworks like LangChain6, LlamaIndex7, and AutoGen8, enabling any agent built on these frameworks to use MCP servers.
开源社区已将 MCP 支持集成到 LangChain6、LlamaIndex7 和 AutoGen8 等框架中，使得基于这些框架构建的任何智能体都能使用 MCP 服务器。


\subsection{Server Registries and Discovery}
\subsubsection{服务器注册与发现}
\label{server-registries-and-discovery}


The MCP ecosystem is developing infrastructure for server discovery:
MCP 生态系统正在建设用于服务器发现的基础设施：


\begin{itemize}
  \item \textbf{MCP Registry}9: An official curated list of verified MCP servers maintained by Anthropic.
  \item \textbf{MCP 注册表}9：由 Anthropic 维护的官方精选已验证 MCP 服务器列表。
  \item \textbf{npm}: Many JavaScript/TypeScript MCP servers are published as npm packages under the \texttt{@modelcontextprotocol} scope.
  \item \textbf{npm}：许多 JavaScript/TypeScript MCP 服务器以 \texttt{@modelcontextprotocol} 作用域下的 npm 包形式发布。
  \item \textbf{PyPI}: Python servers are published as pip packages (e.g., \texttt{pip install mcp-server-sqlite}).
  \item \textbf{PyPI}：Python 服务器以 pip 包形式发布（例如 \texttt{pip install mcp-server-sqlite}）。
  \item \textbf{GitHub}: The \texttt{modelcontextprotocol/servers}10 repository maintains a reference collection of official servers.
  \item \textbf{GitHub}：\texttt{modelcontextprotocol/servers}10 仓库维护了官方服务器的参考集合。
  \item \textbf{Python SDK documentation}11: Full API reference and examples for building servers and clients.
  \item \textbf{Python SDK 文档}11：包含构建服务器和客户端的完整 API 参考与示例。
\end{itemize}


\section{MCP vs.~Alternatives}
\section{MCP 与替代方案的比较}
\label{sec:mcp:alternatives}


\begin{keybox}[MCP vs. Alternative Tool Integration Approaches]
\begin{keybox}[MCP 与替代工具集成方法的对比]
{\footnotesize
\begin{tabular}{@{}lllll@{}}
\toprule
\textbf{Feature} & \textbf{MCP} & \textbf{OpenAI Functions} & \textbf{LangChain Tools} & \textbf{Direct API} \\
\textbf{特性} & \textbf{MCP} & \textbf{OpenAI Functions} & \textbf{LangChain Tools} & \textbf{直接 API} \\
\midrule
Standardized & \checkmark{} & Partial & $\times$ & $\times$ \\
标准化 & \checkmark{} & 部分 & $\times$ & $\times$ \\
Multi-vendor & \checkmark{} & $\times$ & Partial & $\times$ \\
多供应商 & \checkmark{} & $\times$ & 部分 & $\times$ \\
Stateful sessions & \checkmark{} & $\times$ & $\times$ & Varies \\
有状态会话 & \checkmark{} & $\times$ & $\times$ & 视情况而定 \\
Resource streaming & \checkmark{} & $\times$ & $\times$ & Varies \\
资源流式传输 & \checkmark{} & $\times$ & $\times$ & 视情况而定 \\
Server push & \checkmark{} & $\times$ & $\times$ & Varies \\
服务器推送 & \checkmark{} & $\times$ & $\times$ & 视情况而定 \\
Sampling (reverse) & \checkmark{} & $\times$ & $\times$ & $\times$ \\
采样（反向） & \checkmark{} & $\times$ & $\times$ & $\times$ \\
Ecosystem size & Growing & Large & Large & Unlimited \\
生态系统规模 & 增长中 & 大 & 大 & 无限 \\
Setup complexity & Medium & Low & Low & High \\
设置复杂度 & 中等 & 低 & 低 & 高 \\
Vendor lock-in & None & OpenAI & LangChain & None \\
供应商锁定 & 无 & OpenAI & LangChain & 无 \\
\bottomrule
\end{tabular}
}
\end{keybox}


\subsection{When to Use MCP vs.~Custom Integration}
\subsubsection{何时使用 MCP 而非自定义集成}
\label{when-to-use-mcp-vs.-custom-integration}


\textbf{Use MCP when:}
\textbf{在以下情况下使用 MCP：}
```

## Use MCP when:
## 使用 MCP 的场景：

\begin{itemize}
  \item You want your tools to work with multiple LLM providers or agent frameworks
  \item 您希望工具能够与多个 LLM 提供商或智能体框架协同工作
  \item You are building tools that others will use (open-source or enterprise distribution)
  \item 您正在构建供他人使用的工具（开源或企业分发）
  \item You need stateful sessions, resource subscriptions, or server-push capabilities
  \item 您需要有状态会话、资源订阅或服务器推送能力
  \item You want to leverage the existing ecosystem of MCP servers
  \item 您希望利用现有的 MCP 服务器生态系统
\end{itemize}

\textbf{Use custom integration when:}
\textbf{在以下场景使用自定义集成：}

\begin{itemize}
  \item You have a single, tightly-coupled LLM provider and no plans to switch
  \item 您有单一且紧密耦合的 LLM 提供商，且不打算更换
  \item You need extremely low latency and cannot afford the protocol overhead
  \item 您需要极低延迟，无法承受协议开销
  \item Your tool interface is so unusual that MCP primitives do not map well
  \item 您的工具接口非常特殊，MCP 原语难以良好映射
  \item You are in early prototyping and want to minimize dependencies
  \item 您正处于早期原型阶段，希望最小化依赖
\end{itemize}

\subsection{Migration Paths}
\subsection{迁移路径}
\label{migration-paths}

Migrating from OpenAI function calling to MCP is straightforward: the JSON Schema format for tool parameters is identical. The main changes are:
从 OpenAI 函数调用迁移到 MCP 非常直接：工具参数的 JSON Schema 格式完全相同。主要变化如下：

\begin{enumerate}
  \item Wrap tool implementations in an MCP server (using the Python or TypeScript SDK)
  \item 将工具实现封装在 MCP 服务器中（使用 Python 或 TypeScript SDK）
  \item Replace direct API calls with \texttt{session.call\_tool()} in the client
  \item 在客户端中使用 \texttt{session.call\_tool()} 替代直接的 API 调用
  \item Add capability negotiation and lifecycle management
  \item 增加能力协商和生命周期管理
\end{enumerate}

LangChain tools can be wrapped in MCP servers using the \texttt{langchain-mcp-adapters} package, which provides automatic conversion between LangChain’s \texttt{BaseTool} interface and MCP tool definitions.
LangChain 工具可以使用 \texttt{langchain-mcp-adapters} 包封装到 MCP 服务器中，该包在 LangChain 的 \texttt{BaseTool} 接口与 MCP 工具定义之间提供自动转换。

\section{MCP for Agent Training}
\section{MCP 用于智能体训练}
\label{sec:mcp:training}

Beyond deployment, MCP has significant implications for \emph{training} tool-using agents. This section explores how MCP can serve as infrastructure for reinforcement learning and supervised fine-tuning of LLMs.
除了部署，MCP 对于训练使用工具的智能体具有重要影响。本节探讨 MCP 如何作为强化学习和 LLM 监督微调的基础设施。

\subsection{MCP Servers as RL Environment Interfaces}
\subsection{MCP 服务器作为强化学习环境接口}
\label{mcp-servers-as-rl-environment-interfaces}

In reinforcement learning for LLMs (see Section~\ref{sec:rl}), the agent must interact with an environment to receive rewards. MCP servers provide a natural, standardized interface for this:
在 LLM 的强化学习中（参见第~\ref{sec:rl}节），智能体必须与环境交互以获取奖励。MCP 服务器为此提供了自然且标准化的接口：

\begin{itemize}
  \item \textbf{Action space}: The set of available tools defines the agent’s action space. MCP’s \texttt{tools/list} endpoint provides a structured, machine-readable action space that can be dynamically updated.
  \item \textbf{动作空间}：可用工具集定义了智能体的动作空间。MCP 的 \texttt{tools/list} 端点提供了结构化、机器可读且可动态更新的动作空间。
  \item \textbf{Observation space}: MCP resources provide structured observations. A coding environment might expose the current file contents, test results, and error messages as resources.
  \item \textbf{观测空间}：MCP 资源提供结构化观测。编码环境可以将当前文件内容、测试结果和错误消息作为资源暴露。
  \item \textbf{Reward signals}: Tool call results can encode reward signals. A test-running tool might return \verb|{"passed": 8, "failed": 2, "reward": 0.8}| alongside the test output.
  \item \textbf{奖励信号}：工具调用结果可以编码奖励信号。测试运行工具可能返回 \verb|{"passed": 8, "failed": 2, "reward": 0.8}| 以及测试输出。
  \item \textbf{Environment reset}: A \texttt{reset\_environment} tool can restore the environment to its initial state between episodes.
  \item \textbf{环境重置}：\texttt{reset\_environment} 工具可以在回合之间将环境恢复到初始状态。
\end{itemize}

\begin{examplebox}[SWE-bench as an MCP Environment]
\begin{examplebox}[SWE-bench 作为 MCP 环境]

The SWE-bench benchmark (software engineering tasks from real GitHub issues) can be implemented as an MCP server:
SWE-bench 基准测试（来自真实 GitHub 问题的软件工程任务）可以实现为 MCP 服务器：

\begin{itemize}
  \item \textbf{Tools}: \texttt{read\_file}, \texttt{write\_file}, \texttt{run\_tests}, \texttt{apply\_patch}, \texttt{search\_codebase}
  \item \textbf{工具}：\texttt{read\_file}、\texttt{write\_file}、\texttt{run\_tests}、\texttt{apply\_patch}、\texttt{search\_codebase}
  \item \textbf{Resources}: Current file tree, failing test output, issue description
  \item \textbf{资源}：当前文件树、失败测试输出、问题描述
  \item \textbf{Reward}: Fraction of tests passing after the agent’s changes
  \item \textbf{奖励}：智能体修改后通过的测试比例
\end{itemize}

Any RL training framework that speaks MCP can train on SWE-bench without custom environment code.
任何支持 MCP 的强化学习训练框架都可以在 SWE-bench 上训练，无需自定义环境代码。
\end{examplebox}

\subsection{Standardized Action Spaces via MCP}
\subsection{通过 MCP 实现标准化动作空间}
\label{standardized-action-spaces-via-mcp}

One challenge in training tool-using agents is that different environments have different action spaces, making it difficult to transfer learned policies. MCP provides a \textbf{universal action space abstraction}:
训练使用工具的智能体面临的一个挑战是不同环境具有不同的动作空间，使得已学策略难以迁移。MCP 提供了**通用动作空间抽象**：

\begin{equation}
\mathcal{A}_{\text{MCP}} = \bigcup_{s \in \mathcal{S}} \text{Tools}(s)
\end{equation}

where $\mathcal{S}$ is the set of connected MCP servers and $\text{Tools}(s)$ is the tool set of server $s$. The agent learns a policy $\pi(a \mid o, \mathcal{A}_{\text{MCP}})$ that conditions on the available action set, enabling zero-shot generalization to new tool sets.
其中 $\mathcal{S}$ 是已连接的 MCP 服务器集合，$\text{Tools}(s)$ 是服务器 $s$ 的工具集。智能体学习一个依赖于可用动作集的策略 $\pi(a \mid o, \mathcal{A}_{\text{MCP}})$，从而能够零样本泛化到新的工具集。

The JSON Schema format for tool parameters provides a \textbf{structured action representation} that the LLM can parse and generate reliably. This is more tractable than free-form API documentation and enables systematic exploration of the action space during training.
工具参数的 JSON Schema 格式提供了**结构化动作表示**，LLM 可以可靠地解析和生成。这比自由形式的 API 文档更易于处理，并能在训练过程中系统性地探索动作空间。

\subsection{Recording Tool-Use Trajectories for SFT}
\subsection{记录工具使用轨迹用于监督微调}
\label{recording-tool-use-trajectories-for-sft}

MCP’s structured protocol makes it easy to record high-quality tool-use trajectories for supervised fine-tuning:
MCP 的结构化协议使得记录高质量的工具使用轨迹用于监督微调变得容易：

\begin{lstlisting}[style=pythonstyle, caption={Trajectory Recording Middleware for SFT Data Collection}]
\begin{lstlisting}[style=pythonstyle, caption={用于监督微调数据收集的轨迹记录中间件}]
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Any
from mcp import ClientSession


@dataclass
class ToolCallRecord:
    timestamp: float
    tool_name: str
    arguments: dict[str, Any]
    result: dict[str, Any]
    duration_ms: float
    is_error: bool


@dataclass
class Trajectory:
    task_description: str
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    final_answer: str = ""
    success: bool = False
    total_reward: float = 0.0


class RecordingMCPClient:
    """Wraps an MCP session to record all tool calls for SFT data."""
    """封装 MCP 会话以记录所有工具调用，用于监督微调数据。"""

    def __init__(self, session: ClientSession, trajectory: Trajectory):
        self.session = session
        self.trajectory = trajectory

    async def call_tool(self, name: str, arguments: dict) -> Any:
        start = time.monotonic()
        result = await self.session.call_tool(name, arguments)
        duration = (time.monotonic() - start) * 1000

        self.trajectory.tool_calls.append(ToolCallRecord(
            timestamp=time.time(),
            tool_name=name,
            arguments=arguments,
            result={"content": [c.text for c in result.content
                                 if hasattr(c, "text")]},
            duration_ms=duration,
            is_error=result.isError
        ))
        return result

    def save_trajectory(self, path: str):
        with open(path, "w") as f:
            json.dump(asdict(self.trajectory), f, indent=2)
\end{lstlisting}

Recorded trajectories can be converted to instruction-following training examples:
记录的轨迹可以转换为指令遵循训练样本：

\begin{lstlisting}[style=pythonstyle, caption={Converting MCP Trajectories to SFT Training Examples}]
\begin{lstlisting}[style=pythonstyle, caption={将 MCP 轨迹转换为监督微调训练样本}]
def trajectory_to_sft_example(traj: Trajectory) -> dict:
    """Convert a recorded MCP trajectory to a chat-format SFT example."""
    """将记录的 MCP 轨迹转换为聊天格式的监督微调样本。"""
    messages = [
        {"role": "system", "content": (
            "You are a helpful assistant with access to tools. "
            "Use tools to complete tasks step by step."
        )},
        {"role": "user", "content": traj.task_description}
    ]

    for i, call in enumerate(traj.tool_calls):
        call_id = f"call_{i:04d}"
