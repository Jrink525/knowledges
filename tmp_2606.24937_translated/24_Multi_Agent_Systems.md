```markdown
\chapter{Multi-Agent Systems}
\chapter{多智能体系统}
\label{sec:multi-agent-systems}

\section{Motivation: Why Multiple Agents?}
\section{动机：为什么需要多个智能体？}
\label{subsec:mas-motivation}

The history of artificial intelligence is, in many ways, a history of scale. Early AI systems were monolithic: a single program, a single knowledge base, a single inference engine. As problems grew more complex, researchers discovered that no single agent---however capable---could efficiently handle every aspect of a rich, open-ended task. This insight, long established in distributed AI and multi-agent systems (MAS) research~\cite{weiss1999multiagent, wooldridge2009introduction}, has found renewed urgency in the era of large language models.
人工智能的历史在很大程度上是一部规模不断扩大的历史。早期的AI系统是单体的：一个程序、一个知识库、一个推理引擎。随着问题变得日益复杂，研究人员发现，没有一个单一的智能体——无论能力多强——能够高效地处理一个丰富、开放任务的每一个方面。这一在分布式人工智能和多智能体系统（MAS）研究~\cite{weiss1999multiagent, wooldridge2009introduction}中早已确立的观点，在大语言模型时代重新变得紧迫。

\begin{intuitionbox}[The Core Intuition]
\begin{intuitionbox}[核心直觉]

A single LLM, no matter how large, is a generalist. A team of specialized LLMs, each focused on a narrow sub-problem and communicating their results, can outperform the generalist on complex, multi-faceted tasks---just as a team of human specialists outperforms a single generalist on a complex engineering project.
单个LLM，无论多大，都是一个通才。一组专门的LLM，各自专注于一个狭窄的子问题并相互沟通结果，可以在复杂的、多方面的任务上胜过那个通才——就像一组人类专家在复杂的工程项目上胜过单个通才一样。

\end{intuitionbox}
\end{intuitionbox}

Four fundamental motivations drive the shift from monolithic agents to \emph{agent societies}:
从单体智能体转向\emph{智能体社会（agent societies）}有四个基本动机：

\paragraph{Specialization.}
\paragraph{专门化（Specialization）。}
\label{specialization.}

Different sub-tasks benefit from different capabilities, prompting strategies, and even different base models. A code-generation agent can be fine-tuned on programming corpora; a fact-checking agent can be grounded with retrieval tools; a creative-writing agent can be prompted for stylistic diversity. Forcing a single agent to excel at all of these simultaneously is both inefficient and often impossible.
不同的子任务受益于不同的能力、提示策略，甚至不同的基础模型。一个代码生成智能体可以在编程语料库上进行微调；一个事实核查智能体可以借助检索工具进行接地；一个创意写作智能体可以被提示以获得风格多样性。强迫一个单一的智能体同时擅长所有这些任务既低效又往往不可能。

\paragraph{Parallelism.}
\paragraph{并行性（Parallelism）。}
\label{parallelism.}

Many real-world tasks decompose into independent sub-tasks that can be executed concurrently. A research pipeline that requires literature review, data analysis, and report writing can run all three in parallel, dramatically reducing wall-clock time. Sequential single-agent processing is a bottleneck that multi-agent parallelism eliminates.
许多现实世界的任务可以分解为可并发执行的独立子任务。一个需要文献综述、数据分析和报告撰写的研究流程可以并行运行这三者，从而大幅减少挂钟时间。串行的单智能体处理是一个瓶颈，而多智能体并行性消除了这一瓶颈。

\paragraph{Robustness.}
\paragraph{鲁棒性（Robustness）。}
\label{robustness.}

A single agent is a single point of failure. If it hallucinates, gets stuck in a loop, or produces a subtly wrong answer, there is no check. Multi-agent systems introduce redundancy: a second agent can verify, critique, or independently re-derive results. Adversarial agents can probe for weaknesses before outputs are trusted.
单个智能体是单点故障。如果它产生幻觉、陷入循环或给出一个微妙的错误答案，就没有检查机制。多智能体系统引入了冗余：另一个智能体可以验证、批评或独立重新推导结果。对抗性智能体可以在输出被信任之前探测弱点。

\paragraph{Emergent Capabilities.}
\paragraph{涌现能力（Emergent Capabilities）。}
\label{emergent-capabilities.}

Perhaps most intriguingly, agent collectives can exhibit capabilities that no individual agent possesses. Through debate, negotiation, and iterative refinement, multi-agent systems can arrive at solutions that transcend what any single agent could produce alone---a computational analog to the emergent intelligence of social organisms.
也许最引人入胜的是，智能体集体可以表现出任何单个智能体都不具备的能力。通过辩论、协商和迭代优化，多智能体系统可以达成超越任何单个智能体独自所能产生的解决方案——这是对社会生物涌现智能的计算模拟。

\begin{keybox}[Historical Context]
\begin{keybox}[历史背景]

Multi-agent systems research dates to the 1980s, with foundational work on distributed problem solving~\cite{durfee1989distributed}, the Contract Net Protocol~\cite{smith1980contract}, and FIPA agent communication standards~\cite{fipa2002acl}. The shift to LLM-based agents reanimates these classical ideas with a new substrate: instead of hand-coded agents with symbolic reasoning, we now have agents whose ``cognition'' emerges from learned neural representations. The core architectural patterns---hierarchies, markets, blackboards, message passing---remain remarkably relevant.
多智能体系统研究可追溯到1980年代，其基础工作包括分布式问题求解~\cite{durfee1989distributed}、合同网协议~\cite{smith1980contract}和FIPA智能体通信标准~\cite{fipa2002acl}。向基于LLM的智能体的转变以新的基质复活了这些经典思想：我们不再拥有通过符号推理手工编码的智能体，而是拥有了其“认知”从学习到的神经表示中涌现的智能体。核心架构模式——层次结构、市场、黑板、消息传递——仍然非常相关。

\end{keybox}
\end{keybox}

The transition from monolithic agents to agent societies mirrors a broader pattern in complex systems: as the problem space grows, distributed, modular architectures consistently outperform centralized, monolithic ones. The question is no longer \emph{whether} to use multiple agents, but \emph{how} to organize them.
从单体智能体向智能体社会的转变反映了复杂系统中的一个更广泛模式：随着问题空间的增长，分布式的、模块化的架构始终优于集中的、单体的架构。问题不再是\emph{是否}使用多个智能体，而是\emph{如何}组织它们。

\section{Multi-Agent Architectures}
\section{多智能体架构}
\label{subsec:mas-architectures}

The topology of a multi-agent system---how agents are connected and how authority flows among them---is the most consequential architectural decision. Four canonical patterns have emerged, each with distinct trade-offs.
多智能体系统的拓扑结构——智能体如何连接以及权威如何在它们之间流动——是最关键的架构决策。已经出现了四种典型模式，每种都有不同的权衡。

\subsection{Centralized (Supervisor/Manager) Architecture}
\subsection{集中式（监督者/管理者）架构}
\label{subsubsec:centralized}

In a centralized architecture, a single \emph{orchestrator} agent (variously called supervisor, manager, or planner) holds global state, decomposes tasks, delegates sub-tasks to worker agents, and aggregates their results. The topology is a \textbf{hub-and-spoke}: all communication flows through the central node.
在集中式架构中，一个单一的\emph{编排（orchestrator）}智能体（有时称为监督者、管理者或规划者）持有全局状态，分解任务，将子任务委托给工作智能体，并聚合它们的结果。其拓扑结构是\textbf{星型（hub-and-spoke）}：所有通信都流经中心节点。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.65\textwidth]{figures/fig_069_centralized-arch.png}
\caption{Centralized (Supervisor) architecture. The manager delegates tasks to specialized workers and aggregates their outputs. All communication flows through the central hub.}
\caption{集中式（监督者）架构。管理者将任务委托给专门的工作者并聚合它们的输出。所有通信流经中心集线器。}
\label{fig:centralized-arch}
\end{figure}

The manager’s responsibilities include:
管理者的职责包括：

\begin{itemize}
  \item \textbf{Task routing}: deciding which worker is best suited for each sub-task
  \item \textbf{任务路由（Task routing）}：决定每个子任务最适合哪个工作者
  \item \textbf{Context management}: providing each worker with the relevant subset of global context
  \item \textbf{上下文管理（Context management）}：为每个工作者提供全局上下文的相关子集
  \item \textbf{Result aggregation}: synthesizing worker outputs into a coherent whole
  \item \textbf{结果聚合（Result aggregation）}：将工作者的输出综合成一个连贯的整体
  \item \textbf{Error handling}: detecting worker failures and re-routing or retrying
  \item \textbf{错误处理（Error handling）}：检测工作者的失败并重新路由或重试
\end{itemize}

\begin{examplebox}[Supervisor Pattern in LangGraph]
\begin{examplebox}[LangGraph中的监督者模式]

\begin{lstlisting}[style=pythonstyle]
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal


class TeamState(TypedDict):
    task: str
    plan: str
    code: str
    tests: str
    review: str
    next_agent: str
    final_output: str


def supervisor_node(state: TeamState) -> TeamState:
    """Central orchestrator: decides which agent to invoke next."""
    """中心编排器：决定接下来调用哪个智能体。"""
    messages = [
        {"role": "system", "content": SUPERVISOR_PROMPT},
        {"role": "user",   "content": f"Task: {state['task']}\n"
                                      f"Plan: {state.get('plan','')}\n"
                                      f"Code: {state.get('code','')}\n"
                                      f"Tests: {state.get('tests','')}\n"
                                      "Which agent should act next? "
                                      "Options: planner, coder, tester, reviewer, FINISH"}
        {"role": "system", "content": SUPERVISOR_PROMPT},
        {"role": "user",   "content": f"Task: {state['task']}\n"
                                      f"Plan: {state.get('plan','')}\n"
                                      f"Code: {state.get('code','')}\n"
                                      f"Tests: {state.get('tests','')}\n"
                                      "Which agent should act next? "
                                      "Options: planner, coder, tester, reviewer, FINISH"}
                                      "哪个智能体应该下一步行动？"
                                      "选项：planner, coder, tester, reviewer, FINISH"}
    ]
    response = llm.invoke(messages)
    return {**state, "next_agent": response.content.strip()}


def route(state: TeamState) -> Literal["planner","coder","tester","reviewer","__end__"]:
    return state["next_agent"] if state["next_agent"] != "FINISH" else END


builder = StateGraph(TeamState)
builder.add_node("supervisor", supervisor_node)
builder.add_node("planner",    planner_node)
builder.add_node("coder",      coder_node)
builder.add_node("tester",     tester_node)
builder.add_node("reviewer",   reviewer_node)


builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", route)
for agent in ["planner", "coder", "tester", "reviewer"]:
    builder.add_edge(agent, "supervisor")   # always return to supervisor
    builder.add_edge(agent, "supervisor")   # 总是返回监督者


graph = builder.compile()
\end{lstlisting}
\end{examplebox}
\end{examplebox}

\begin{warningbox}[Centralized Architecture Trade-offs]
\begin{warningbox}[集中式架构的权衡]

\textbf{Pros:} Simple control flow; clear accountability; easy to debug (all decisions in one place); straightforward to implementation.\\
\textbf{优点：}控制流简单；责任明确；易于调试（所有决策都在一处）；实现直接。

\textbf{Cons:} Single point of failure---if the manager hallucinates or gets confused, the entire system fails; the manager becomes a bottleneck under high load; the manager’s context window must hold the global state, limiting scalability.
\textbf{缺点：}单点故障——如果管理者产生幻觉或混乱，整个系统就会失败；在高负载下管理者成为瓶颈；管理者的上下文窗口必须容纳全局状态，限制了可扩展性。

\end{warningbox}
\end{warningbox}

\subsection{Decentralized (Peer-to-Peer) Architecture}
\subsection{去中心化（对等）架构}
\label{subsubsec:decentralized}

In a decentralized architecture, agents interact directly with one another without a central coordinator. The topology is a \textbf{mesh}: any agent can communicate with any other. Coordination emerges from local interactions rather than global planning.
在去中心化架构中，智能体之间直接交互，没有中央协调者。其拓扑结构是\textbf{网状（mesh）}：任何智能体都可以与任何其他智能体通信。协调来自局部交互，而非全局规划。

[Note: The original content ends here. The rest of the translation should continue similarly if more content were provided.]
[注意：原始内容在此结束。如果提供更多内容，翻译应类似地继续。]
```

\begin{figure}[ht!]
\centering
\includegraphics[width=0.65\textwidth]{figures/fig_070_decentralized-arch.png}
\caption{Decentralized (peer-to-peer) architecture. Agents communicate directly; coordination emerges from local interactions.}
\label{fig:decentralized-arch}
\end{figure}
\begin{figure}[ht!]
\centering
\includegraphics[width=0.65\textwidth]{figures/fig_070_decentralized-arch.png}
\caption{去中心化（对等）架构。智能体直接通信；协调从局部交互中涌现。}
\label{fig:decentralized-arch}
\end{figure}

Emergent coordination in peer-to-peer systems arises through mechanisms such as:
对等系统中的涌现协调通过以下机制产生：

\begin{itemize}
  \item \textbf{Negotiation}: agents bid for tasks or resources
  \item \textbf{Stigmergy}: agents modify shared state that others observe (see Section~\ref{subsubsec:stigmergy})
  \item \textbf{Gossip protocols}: agents propagate information through the network
  \item \textbf{Local consensus}: small groups of agents reach agreement without global coordination
\end{itemize}
\begin{itemize}
  \item \textbf{协商（Negotiation）}：智能体对任务或资源进行竞标
  \item \textbf{印记（Stigmergy）}：智能体修改其他智能体能观察到的共享状态（参见第\ref{subsubsec:stigmergy}节）
  \item \textbf{八卦协议（Gossip protocols）}：智能体通过网络传播信息
  \item \textbf{局部共识（Local consensus）}：小群智能体在没有全局协调的情况下达成一致
\end{itemize}

\begin{warningbox}[Decentralized Architecture Trade-offs]
\textbf{Pros:} Resilient to individual agent failures; scales naturally as agents are added; no bottleneck.\\

\textbf{Cons:} Hard to debug---emergent behavior is difficult to trace; potential for conflicts when agents have inconsistent views of state; coordination overhead grows as $O(n^2)$ with naive message passing; difficult to guarantee global consistency.
\end{warningbox}
\begin{warningbox}[去中心化架构的权衡]
\textbf{优点：} 对单个智能体故障具有弹性；随着智能体增加自然扩展；无瓶颈。\\

\textbf{缺点：} 难以调试——涌现行为难以追踪；智能体状态视图不一致时可能发生冲突；朴素消息传递下协调开销呈 $O(n^2)$ 增长；难以保证全局一致性。
\end{warningbox}

\subsection{Hierarchical Architecture}
\label{subsubsec:hierarchical}
\subsection{层次化架构（Hierarchical Architecture）}
\label{subsubsec:hierarchical}

Hierarchical architectures generalize the centralized pattern into a \textbf{tree structure} with multiple levels of management. A top-level orchestrator delegates to domain-specific sub-managers, who in turn delegate to specialized workers. This mirrors the organizational structure of large enterprises.
层次化架构将集中式模式推广为具有多个管理层的\textbf{树状结构}。顶层协调器将任务委派给特定领域的子管理者，子管理者再委派给专业工作者。这镜像了大型企业的组织结构。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_071_hierarchical-arch.png}
\caption{Hierarchical architecture. A top-level orchestrator delegates to domain sub-managers, who delegate to specialized workers. Dashed arrow shows an escalation path.}
\label{fig:hierarchical-arch}
\end{figure}
\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_071_hierarchical-arch.png}
\caption{层次化架构。顶层协调器将任务委派给领域子管理者，子管理者再委派给专业工作者。虚线箭头表示升级路径。}
\label{fig:hierarchical-arch}
\end{figure}

Key features of hierarchical systems:
层次化系统的关键特征：

\begin{itemize}
  \item \textbf{Delegation chains}: authority and context flow down the tree; results flow up
  \item \textbf{Escalation paths}: workers can escalate unresolvable issues to their manager
  \item \textbf{Domain isolation}: sub-managers maintain domain-specific context, reducing the cognitive load on the top-level orchestrator
  \item \textbf{Scope limitation}: each agent only needs to know about its immediate superiors and subordinates
\end{itemize}
\begin{itemize}
  \item \textbf{委派链（Delegation chains）}：权威和上下文沿树向下流动；结果向上流动
  \item \textbf{升级路径（Escalation paths）}：工作者可以将无法解决的问题升级给管理者
  \item \textbf{领域隔离（Domain isolation）}：子管理者维护特定领域的上下文，减少顶层协调器的认知负荷
  \item \textbf{范围限制（Scope limitation）}：每个智能体只需知道其直接上级和下级
\end{itemize}

The enterprise analogy is apt: a CEO (top orchestrator) sets strategy; VPs (sub-managers) translate strategy into domain plans; individual contributors (workers) execute. The hierarchy enables scale while preserving accountability.
企业类比很贴切：CEO（顶层协调器）制定战略；副总裁（子管理者）将战略转化为领域计划；个人贡献者（工作者）执行。层次结构在保持问责制的同时实现了规模化。

\subsection{Swarm Architecture}
\label{subsubsec:swarm}
\subsection{群体架构（Swarm Architecture）}
\label{subsubsec:swarm}

Swarm architectures, inspired by biological systems (ant colonies, bird flocking), consist of many \textbf{loosely coupled agents} that follow simple local rules, producing complex global behavior without any central coordinator or global state.
群体架构受生物系统（蚁群、鸟群）启发，由许多\textbf{松散耦合的智能体}组成，它们遵循简单的局部规则，在没有任何中央协调器或全局状态的情况下产生复杂的全局行为。

OpenAI’s \textbf{Swarm} framework~\cite{openai2024swarm} (now superseded by the OpenAI Agents SDK, but its conceptual primitives remain influential) operationalizes this with two primitives:
OpenAI 的\textbf{Swarm}框架~\cite{openai2024swarm}（现已被 OpenAI Agents SDK 取代，但其概念原语仍具影响力）通过两个原语实现了这一点：

\begin{itemize}
  \item \textbf{Routines}: sequences of instructions an agent follows to complete a sub-task
  \item \textbf{Handoffs}: an agent transferring control (and relevant context) to another agent
\end{itemize}
\begin{itemize}
  \item \textbf{例程（Routines）}：智能体完成子任务所遵循的指令序列
  \item \textbf{移交（Handoffs）}：智能体将控制权（及相关上下文）转移给另一个智能体
\end{itemize}

\begin{examplebox}[OpenAI Swarm: Routines and Handoffs]
\begin{lstlisting}[style=pythonstyle]
from swarm import Swarm, Agent


client = Swarm()


def transfer_to_billing():
    """Handoff: transfer control to the billing specialist."""
    return billing_agent


def transfer_to_technical():
    """Handoff: transfer control to the technical support agent."""
    return technical_agent


triage_agent = Agent(
    name="Triage Agent",
    instructions="""You are a customer service triage agent.
    Determine the nature of the customer's issue:
    - For billing questions, transfer to billing.
    - For technical issues, transfer to technical support.
    - For general questions, answer directly.""",
    functions=[transfer_to_billing, transfer_to_technical],
)


billing_agent = Agent(
    name="Billing Specialist",
    instructions="You handle billing inquiries. "
                 "Access account data and resolve payment issues.",
    functions=[lookup_account, process_refund],
)


technical_agent = Agent(
    name="Technical Support",
    instructions="You resolve technical issues. "
                 "Diagnose problems and provide step-by-step solutions.",
    functions=[run_diagnostics, escalate_to_engineering],
)


# No global state --- each agent operates on its local context
response = client.run(
    agent=triage_agent,
    messages=[{"role": "user", "content": "My invoice is wrong"}]
)
\end{lstlisting}
\end{examplebox}
\begin{examplebox}[OpenAI Swarm：例程与移交]
\begin{lstlisting}[style=pythonstyle]
from swarm import Swarm, Agent


client = Swarm()


def transfer_to_billing():
    """移交：将控制权转移给账单专员。"""
    return billing_agent


def transfer_to_technical():
    """移交：将控制权转移给技术支持代理。"""
    return technical_agent


triage_agent = Agent(
    name="分诊代理",
    instructions="""你是一个客户服务分诊代理。
    确定客户问题的性质：
    - 账单问题，转至账单代理。
    - 技术问题，转至技术支持代理。
    - 一般问题，直接回答。""",
    functions=[transfer_to_billing, transfer_to_technical],
)


billing_agent = Agent(
    name="账单专员",
    instructions="你处理账单查询。"
                 "访问账户数据并解决支付问题。",
    functions=[lookup_account, process_refund],
)


technical_agent = Agent(
    name="技术支持",
    instructions="你解决技术问题。"
                 "诊断问题并提供逐步解决方案。",
    functions=[run_diagnostics, escalate_to_engineering],
)


# 无全局状态——每个智能体在其局部上下文中运行
response = client.run(
    agent=triage_agent,
    messages=[{"role": "user", "content": "我的发票有误"}]
)
\end{lstlisting}
\end{examplebox}

\begin{keybox}[Swarm Properties]
\begin{itemize}
  \item \textbf{No global state}: each agent maintains only its local context window
  \item \textbf{Local decisions}: routing decisions are made by the current agent, not a central planner
  \item \textbf{Task completion through collective behavior}: complex tasks are completed through a chain of handoffs, each agent contributing its specialty
  \item \textbf{Lightweight}: no orchestration overhead; agents are stateless between handoffs
\end{itemize}
\end{keybox}
\begin{keybox}[群体架构特性]
\begin{itemize}
  \item \textbf{无全局状态}：每个智能体仅维护其局部上下文窗口
  \item \textbf{局部决策}：路由决策由当前智能体做出，而非中央规划器
  \item \textbf{通过集体行为完成任务}：复杂任务通过一系列移交完成，每个智能体贡献其专长
  \item \textbf{轻量级}：无编排开销；智能体在移交之间是无状态的
\end{itemize}
\end{keybox}

\section{Coordination Mechanisms}
\label{subsec:coordination-mechanisms}
\section{协调机制（Coordination Mechanisms）}
\label{subsec:coordination-mechanisms}

How agents coordinate---how they share information, divide work, and resolve conflicts---is as important as the topology. Six canonical coordination mechanisms apply to LLM-based multi-agent systems.
智能体如何协调——它们如何共享信息、分工和解决冲突——与拓扑结构同等重要。六种典型的协调机制适用于基于 LLM 的多智能体系统。

\subsection{Shared State (Global Blackboard)}
\label{subsubsec:shared-state}
\subsection{共享状态（全局黑板，Shared State / Global Blackboard）}
\label{subsubsec:shared-state}

The \textbf{blackboard architecture}~\cite{hayes1985blackboard} provides a shared data structure that all agents can read from and write to. In LLM systems, this is typically implemented as a shared dictionary, database, or structured document.
\textbf{黑板架构（blackboard architecture）}~\cite{hayes1985blackboard} 提供了一个所有智能体都可读写的共享数据结构。在 LLM 系统中，这通常实现为共享字典、数据库或结构化文档。

\begin{lstlisting}[style=pythonstyle, caption={Shared blackboard with conflict resolution}]
import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class BlackboardEntry:
    value: Any
    author: str
    timestamp: float
    confidence: float = 1.0


class Blackboard:
    """Thread-safe shared state for multi-agent coordination."""

    def __init__(self):
        self._data: Dict[str, BlackboardEntry] = {}
        self._lock = threading.RLock()
        self._subscribers: Dict[str, List[Callable]] = {}

    def write(self, key: str, value: Any, author: str,
              confidence: float = 1.0) -> bool:
        """Write to blackboard; higher-confidence entries win conflicts."""
        with self._lock:
            existing = self._data.get(key)
            if existing and existing.confidence > confidence:
                return False  # Conflict: existing entry wins
            import time
            self._data[key] = BlackboardEntry(
                value=value, author=author,
                timestamp=time.time(), confidence=confidence
            )
            self._notify(key, value)
            return True

    def read(self, key: str) -> Any:
        with self._lock:
            entry = self._data.get(key)
            return entry.value if entry else None

    def subscribe(self, key: str, callback: Callable):
        """Agents subscribe to changes on specific keys."""
        self._subscribers.setdefault(key, []).append(callback)

    def _notify(self, key: str, value: Any):
        for cb in self._subscribers.get(key, []):
            cb(key, value)
\end{lstlisting}
\begin{lstlisting}[style=pythonstyle, caption={带冲突解决的共享黑板}]
import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class BlackboardEntry:
    value: Any
    author: str
    timestamp: float
    confidence: float = 1.0


class Blackboard:
    """用于多智能体协调的线程安全共享状态。"""

    def __init__(self):
        self._data: Dict[str, BlackboardEntry] = {}
        self._lock = threading.RLock()
        self._subscribers: Dict[str, List[Callable]] = {}

    def write(self, key: str, value: Any, author: str,
              confidence: float = 1.0) -> bool:
        """写入黑板；置信度更高的条目在冲突中获胜。"""
        with self._lock:
            existing = self._data.get(key)
            if existing and existing.confidence > confidence:
                return False  # 冲突：现有条目获胜
            import time
            self._data[key] = BlackboardEntry(
                value=value, author=author,
                timestamp=time.time(), confidence=confidence
            )
            self._notify(key, value)
            return True

    def read(self, key: str) -> Any:
        with self._lock:
            entry = self._data.get(key)
            return entry.value if entry else None

    def subscribe(self, key: str, callback: Callable):
        """智能体订阅特定键的变化。"""
        self._subscribers.setdefault(key, []).append(callback)

    def _notify(self, key: str, value: Any):
        for cb in self._subscribers.get(key, []):
            cb(key, value)
\end{lstlisting}

\subsection{Message Passing}
\label{subsubsec:message-passing}
\subsection{消息传递（Message Passing）}
\label{subsubsec:message-passing}

Message passing is the most natural coordination mechanism for LLM agents: agents communicate by sending structured text messages to one another. Key design decisions include:
消息传递是 LLM 智能体最自然的协调机制：智能体通过相互发送结构化文本来通信。关键设计决策包括：

\begin{itemize}
  \item \textbf{Message format}: structured (JSON schema) vs. natural language vs. hybrid
  \item \textbf{消息格式}：结构化（JSON 模式） vs. 自然语言 vs. 混合
  \item \textbf{Routing}: direct (agent-to-agent) vs. broadcast vs. topic-based pub/sub
  \item \textbf{路由}：直接（智能体对智能体） vs. 广播 vs. 基于主题的发布/订阅
  \item \textbf{Conversation threads}: maintaining context across multi-turn exchanges
  \item \textbf{对话线程}：在多轮交互中维护上下文
  \item \textbf{Acknowledgment}: whether senders require confirmation of receipt/processing
  \item \textbf{确认机制}：发送方是否需要接收/处理确认
\end{itemize}

\subsection{Planning and Decomposition}
\subsection{规划与分解}
\label{subsubsec:planning-decomp}

A manager agent decomposes a high-level task into a \textbf{directed acyclic graph (DAG)} of sub-tasks, assigns each to an appropriate worker, and tracks dependencies. This is the multi-agent analog of classical hierarchical task network (HTN) planning.
管理者智能体将高层任务分解为子任务的 \textbf{有向无环图（DAG）}，将每个子任务分配给合适的工作者，并跟踪依赖关系。这是经典层次任务网络（HTN）规划的多智能体对应物。

\begin{lstlisting}[style=pythonstyle, caption={Task DAG decomposition}]
\begin{lstlisting}[style=pythonstyle, caption={任务 DAG 分解}]
from dataclasses import dataclass, field
from typing import List, Optional
import asyncio


@dataclass
class Task:
    id: str
    description: str
    assigned_to: str
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"   # pending | running | done | failed
    status: str = "pending"   # pending | running | done | failed（待处理 | 运行中 | 完成 | 失败）
    result: Optional[str] = None


class TaskDAG:
    def __init__(self):
        self.tasks: dict[str, Task] = {}

    def add_task(self, task: Task):
        self.tasks[task.id] = task

    def ready_tasks(self) -> List[Task]:
        """Return tasks whose dependencies are all completed."""
        """返回所有依赖项均已完成的就绪任务列表。"""
        return [
            t for t in self.tasks.values()
            if t.status == "pending"
            and all(self.tasks[d].status == "done"
                    for d in t.dependencies)
        ]

    async def execute(self, agent_pool: dict):
        while any(t.status != "done" for t in self.tasks.values()):
            ready = self.ready_tasks()
            if not ready:
                await asyncio.sleep(0.1)
                continue
            # Execute ready tasks in parallel
            # 并行执行就绪任务
            await asyncio.gather(*[
                self._run_task(t, agent_pool[t.assigned_to])
                for t in ready
            ])

    async def _run_task(self, task: Task, agent):
        task.status = "running"
        try:
            task.result = await agent.execute(task.description)
            task.status = "done"
        except Exception as e:
            task.status = "failed"
            raise
\end{lstlisting}

\subsection{Voting and Consensus}
\subsection{投票与共识}
\label{subsubsec:voting}

When multiple agents produce conflicting outputs, voting mechanisms aggregate their responses into a single decision. Common schemes include:
当多个智能体产生冲突的输出时，投票机制将其响应聚合为单一决策。常见方案包括：

\begin{itemize}
  \item \textbf{Majority voting}: the most common answer wins; effective for factual questions
  \item \textbf{多数投票}：最常见的答案获胜；适用于事实性问题
  \item \textbf{Weighted voting}: agents with higher track records or confidence scores receive more weight
  \item \textbf{加权投票}：历史表现更好或置信度分数更高的智能体获得更高权重
  \item \textbf{Debate-based resolution}: agents argue for their positions; a judge agent decides
  \item \textbf{基于辩论的裁决}：智能体为自己的立场辩论；由裁判智能体做出决定
  \item \textbf{Delphi method}: iterative rounds where agents revise their answers after seeing others’ reasoning
  \item \textbf{德尔菲法}：多轮迭代，智能体在查看其他智能体的推理后修改自己的答案
\end{itemize}

Formally, given $n$ agents producing outputs $\{o_1, \ldots, o_n\}$ with weights $\{w_1, \ldots, w_n\}$, the weighted consensus is: 
形式上，给定 $n$ 个智能体产生输出 $\{o_1, \ldots, o_n\}$ 并带有权重 $\{w_1, \ldots, w_n\}$，加权共识为：
\begin{equation}
  o^* = \arg\max_{o} \sum_{i=1}^{n} w_i \cdot \mathbf{1}[o_i = o]
\end{equation}
 For continuous outputs (e.g., probability estimates), weighted averaging applies: 
对于连续输出（如概率估计），采用加权平均：
\begin{equation}
  \hat{p} = \frac{\sum_{i=1}^{n} w_i \cdot p_i}{\sum_{i=1}^{n} w_i}
\end{equation}

\subsection{Market-Based Coordination}
\subsection{基于市场的协调}
\label{subsubsec:market-based}

Market mechanisms allocate tasks and resources through \textbf{auctions and bidding}. The Contract Net Protocol~\cite{smith1980contract}, one of the oldest multi-agent coordination mechanisms, is a task auction:
市场机制通过\textbf{拍卖与投标}来分配任务和资源。合同网协议（Contract Net Protocol）~\cite{smith1980contract} 是最古老的多智能体协调机制之一，它是一种任务拍卖：

\begin{enumerate}
  \item A \emph{manager} broadcasts a task announcement with requirements
  \item \emph{管理者}广播带有需求的任务公告
  \item \emph{Contractor} agents submit bids (capability declarations + cost estimates)
  \item \emph{承包商}智能体提交投标（能力声明 + 成本估算）
  \item The manager awards the contract to the best bidder
  \item 管理者将合同授予最佳投标者
  \item The winning contractor executes and reports results
  \item 中标承包商执行任务并报告结果
\end{enumerate}

In LLM systems, bids can be expressed in natural language (``I can complete this in 3 steps with high confidence'') or structured formats. Market mechanisms are particularly effective for resource-constrained settings where API costs must be minimized.
在 LLM 系统中，投标可以用自然语言（如“我可以在 3 步内以高置信度完成此任务”）或结构化格式表达。市场机制在需要最小化 API 成本的资源受限场景中特别有效。

\subsection{Stigmergy: Indirect Communication Through Environment}
\subsection{Stigmergy（环境间接通信）}
\label{subsubsec:stigmergy}

\textbf{Stigmergy}~\cite{grassé1959reconstruction} replaces explicit agent-to-agent messaging with a simpler mechanism: each agent modifies the shared environment as a side effect of its work, and other agents react to those modifications rather than to direct signals. The classic illustration is a foraging ant depositing pheromone on its return path; subsequent ants amplify successful routes without any ant ``talking'' to another.
\textbf{Stigmergy（环境信息素机制）}~\cite{grassé1959reconstruction} 用更简单的机制替代了显式的智能体间消息传递：每个智能体在工作的副作用中修改共享环境，其他智能体对这些修改做出反应，而不是直接接收信号。经典的例子是觅食蚂蚁在返回路径上留下信息素；后续蚂蚁放大成功路线，而没有任何蚂蚁“交谈”。

In LLM multi-agent systems, stigmergy manifests as:
在 LLM 多智能体系统中，stigmergy 表现为：

\begin{itemize}
  \item \textbf{Shared documents}: agents write to a shared document; others read and build upon it
  \item \textbf{共享文档}：智能体向共享文档写入内容；其他智能体读取并在此基础上构建
  \item \textbf{Code repositories}: one agent commits code; another reads and extends it
  \item \textbf{代码仓库}：一个智能体提交代码；另一个智能体读取并扩展它
  \item \textbf{Annotation layers}: agents annotate shared artifacts (highlight errors, add comments)
  \item \textbf{注释层}：智能体对共享制品进行注释（高亮错误、添加评论）
  \item \textbf{Task queues}: agents add and consume tasks from a shared queue
  \item \textbf{任务队列}：智能体从共享队列中添加和消费任务
\end{itemize}

Stigmergy enables coordination without explicit communication overhead---agents simply observe the state of the shared environment and act accordingly.
Stigmergy 使得无需显式通信开销即可实现协调——智能体只需观察共享环境的状态并采取相应行动。

\section{Communication Protocols}
\section{通信协议}
\label{subsec:communication-protocols}

Effective multi-agent systems require well-defined communication protocols: agreed-upon formats, semantics, and patterns for agent-to-agent messages. (For the standardized inter-agent protocol, see Chapter~\ref{sec:a2a}.)
有效的多智能体系统需要明确定义的通信协议：智能体间消息的约定格式、语义和模式。（关于标准化智能体间协议，参见第~\ref{sec:a2a} 章。）

\subsection{Structured Message Formats}
\subsection{结构化消息格式}
\label{structured-message-formats}

Messages between LLM agents should be structured to enable reliable parsing and routing. A minimal message schema:
LLM 智能体之间的消息应该结构化，以便可靠地解析和路由。一个最小消息模式如下：

\begin{lstlisting}[style=pythonstyle, caption={Agent message schema}]
\begin{lstlisting}[style=pythonstyle, caption={智能体消息模式}]
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any
from datetime import datetime, timezone
import uuid


PerformativeType = Literal[
    "inform",    # Share information
    "inform",    # 分享信息
    "request",   # Request an action
    "request",   # 请求一个动作
    "propose",   # Propose a course of action
    "propose",   # 提议一个行动方案
    "accept",    # Accept a proposal
    "accept",    # 接受一个提议
    "reject",    # Reject a proposal
    "reject",    # 拒绝一个提议
    "query",     # Ask a question
    "query",     # 提问
    "confirm",   # Confirm receipt/completion
    "confirm",   # 确认接收/完成
    "failure",   # Report a failure
    "failure",   # 报告失败
]


class AgentMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str          # Groups related messages
    conversation_id: str          # 分组相关消息
    sender: str                   # Agent identifier
    sender: str                   # 智能体标识符
    receiver: str                 # Target agent (or "broadcast")
    receiver: str                 # 目标智能体（或 "broadcast"）
    performative: PerformativeType
    content: str                  # Natural language content
    content: str                  # 自然语言内容
    metadata: Dict[str, Any] = {} # Structured payload
    metadata: Dict[str, Any] = {} # 结构化负载
    reply_to: Optional[str] = None  # message_id being replied to
    reply_to: Optional[str] = None  # 被回复的 message_id
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_llm_prompt(self) -> str:
        """Render message as a prompt fragment for the receiving agent."""
        """将消息渲染为接收智能体的提示片段。"""
        return (
            f"[MESSAGE from {self.sender}]\n"
            f"Type: {self.performative}\n"
            f"Content: {self.content}\n"
            + (f"Metadata: {self.metadata}\n" if self.metadata else "")
        )
\end{lstlisting}

\subsection{Performative Types (FIPA-ACL Inspired)}
\subsection{言语行为类型（受 FIPA-ACL 启发）}
\label{performative-types-fipa-acl-inspired}

Drawing from the FIPA Agent Communication Language~\cite{fipa2002acl}, modernized for LLM agents:
借鉴 FIPA 智能体通信语言（FIPA Agent Communication Language）~\cite{fipa2002acl}，并针对 LLM 智能体进行了现代化改造：

```markdown
\begin{table}[ht!]
\centering
\caption{FIPA-ACL-inspired performative types for LLM agent messages.}
\caption{受FIPA-ACL启发的LLM智能体消息施为类型}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Performative} & \textbf{Semantics} & \textbf{Example Use} \\
\textbf{施为类型} & \textbf{语义} & \textbf{使用示例} \\
\midrule
\texttt{inform} & Sender believes $\phi$ is true & Share research findings \\
\texttt{inform} & 发送者相信 $\phi$ 为真 & 分享研究发现 \\
\texttt{request} & Sender wants receiver to do $\alpha$ & Delegate a sub-task \\
\texttt{request} & 发送者希望接收者执行 $\alpha$ & 委派子任务 \\
\texttt{propose} & Sender proposes plan $\pi$ & Suggest an approach \\
\texttt{propose} & 发送者提出方案 $\pi$ & 建议一种方法 \\
\texttt{accept} & Receiver agrees to proposal & Confirm task assignment \\
\texttt{accept} & 接收者同意提案 & 确认任务分配 \\
\texttt{reject} & Receiver declines proposal & Refuse incompatible task \\
\texttt{reject} & 接收者拒绝提案 & 拒绝不兼容的任务 \\
\texttt{query} & Sender wants to know $\phi$ & Ask for clarification \\
\texttt{query} & 发送者想知道 $\phi$ & 请求澄清 \\
\texttt{confirm} & Sender confirms $\phi$ occurred & Acknowledge completion \\
\texttt{confirm} & 发送者确认 $\phi$ 已发生 & 确认完成 \\
\texttt{failure} & Sender failed to achieve $\alpha$ & Report error \\
\texttt{failure} & 发送者未能实现 $\alpha$ & 报告错误 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Context Sharing Strategies}
\subsection{上下文共享策略}
\label{context-sharing-strategies}

A critical challenge in multi-agent communication is \textbf{context management}: how much history does each agent need? Three strategies:
多智能体通信中的一个关键挑战是 \textbf{上下文管理}：每个智能体需要多少历史信息？有三种策略：

\begin{itemize}
  \item \textbf{Full history}: pass the entire conversation history to each agent. Maximally informative but expensive; context windows fill quickly.
  \item \textbf{完整历史}：将整个对话历史传递给每个智能体。信息量最大，但成本高昂；上下文窗口会迅速填满。
  \item \textbf{Summary}: a summarizer agent condenses prior exchanges into a compact summary. Efficient but lossy; important details may be dropped.
  \item \textbf{摘要}：一个摘要智能体将之前的交流浓缩成紧凑的摘要。高效但有损；重要细节可能被遗漏。
  \item \textbf{Relevant excerpt}: retrieve only the most relevant prior messages using semantic search. Balances cost and informativeness; requires a retrieval mechanism.
  \item \textbf{相关摘录}：使用语义搜索仅检索最相关的先前消息。平衡了成本和信息量；需要检索机制。
\end{itemize}

\begin{keybox}[Context Sharing Rule of Thumb]
\keybox 标题：上下文共享经验法则
Use \textbf{full history} for short conversations ($<$10 turns); \textbf{summaries} for medium-length conversations; \textbf{retrieval-augmented excerpts} for long-running agent sessions. Always include the most recent $k$ messages verbatim to preserve immediate context.
对于简短对话（$<$10轮），使用\textbf{完整历史}；对于中等长度对话，使用\textbf{摘要}；对于长时间运行的智能体会话，使用\textbf{检索增强的摘录}。始终逐字包含最近的$k$条消息，以保留即时上下文。
\end{keybox}

\section{Role Design and Specialization}
\section{角色设计与专业化}
\label{subsec:role-design}

The design of agent roles---their capabilities, personas, and responsibilities---is as much an art as a science. Well-designed roles enable specialization; poorly designed roles create confusion and redundancy.
智能体角色（能力、人设和职责）的设计既是科学也是艺术。设计得当的角色能够实现专业化；设计不当的角色则会造成混乱和冗余。

\subsection{Defining Agent Roles}
\subsection{定义智能体角色}
\label{defining-agent-roles}

Common roles in LLM multi-agent systems:
LLM多智能体系统中的常见角色：

\begin{table}[ht!]
\centering
\caption{Common agent roles in LLM multi-agent systems.}
\caption{LLM多智能体系统中的常见智能体角色}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Role} & \textbf{Primary Capability} & \textbf{Typical Tools} \\
\textbf{角色} & \textbf{主要能力} & \textbf{典型工具} \\
\midrule
Researcher & Information gathering, synthesis & Web search, RAG, databases \\
研究者 & 信息收集与综合 & 网络搜索、RAG、数据库 \\
Planner & Task decomposition, scheduling & None (reasoning only) \\
规划者 & 任务分解、调度 & 无（仅推理） \\
Coder & Code generation, debugging & Code interpreter, linter \\
编码者 & 代码生成、调试 & 代码解释器、linter \\
Reviewer & Quality assessment, critique & None (reasoning only) \\
审查者 & 质量评估、批评 & 无（仅推理） \\
Tester & Test generation, execution & Test runner, coverage tools \\
测试者 & 测试生成与执行 & 测试运行器、覆盖率工具 \\
Writer & Prose generation, editing & Grammar checker, style guide \\
写作者 & 散文生成、编辑 & 语法检查器、风格指南 \\
Critic & Adversarial evaluation & None (reasoning only) \\
评论者 & 对抗性评估 & 无（仅推理） \\
Orchestrator & Coordination, delegation & All agent interfaces \\
编排者 & 协调、委派 & 所有智能体接口 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Capability-Based vs.~Role-Based Assignment}
\subsection{基于能力与基于角色的分配}
\label{capability-based-vs.-role-based-assignment}

Two philosophies for task assignment:
任务分配的两种理念：

\begin{itemize}
  \item \textbf{Role-based}: tasks are assigned based on predefined role labels. Simple and predictable; may be suboptimal when a task spans multiple roles.
  \item \textbf{基于角色}：根据预定义的角色标签分配任务。简单且可预测；但当任务跨越多个角色时可能不是最优的。
  \item \textbf{Capability-based}: tasks are assigned based on a dynamic assessment of each agent’s capabilities relative to the task requirements. More flexible; requires a capability registry and matching mechanism.
  \item \textbf{基于能力}：根据每个智能体相对于任务要求的动态能力评估来分配任务。更灵活；需要能力注册表和匹配机制。
\end{itemize}

\subsection{Dynamic Role Reassignment}
\subsection{动态角色重分配}
\label{dynamic-role-reassignment}

In long-running systems, static role assignments become suboptimal. Dynamic reassignment allows agents to take on new roles based on:
在长时间运行的系统中，静态角色分配会变得次优。动态重分配允许智能体根据以下因素承担新角色：

\begin{itemize}
  \item Current workload (load balancing)
  \item 当前工作负载（负载均衡）
  \item Demonstrated performance on recent tasks
  \item 在最近任务中表现出的性能
  \item Changing task requirements
  \item 不断变化的任务需求
  \item Agent failures requiring coverage
  \item 智能体故障需要覆盖
\end{itemize}

\subsection{Persona Design for Diversity of Thought}
\subsection{促进思维多样性的角色人设设计}
\label{persona-design-for-diversity-of-thought}

A subtle but powerful technique: give agents \textbf{distinct personas} that encourage diverse perspectives. Rather than five identical ``assistant'' agents, design:
一种微妙但强大的技巧：赋予智能体\textbf{不同的人设}，以鼓励多样化的视角。与其使用五个相同的“助手”智能体，不如设计：

\begin{itemize}
  \item An \emph{optimist} who emphasizes opportunities
  \item 一个强调机会的\textit{乐观者}
  \item A \emph{skeptic} who challenges assumptions
  \item 一个挑战假设的\textit{怀疑者}
  \item A \emph{pragmatist} who focuses on implementation
  \item 一个关注实现的\textit{实用主义者}
  \item A \emph{visionary} who thinks long-term
  \item 一个思考长期的\textit{远见者}
  \item A \emph{devil’s advocate} who argues the opposite position
  \item 一个持对立立场的\textit{唱反调者}
\end{itemize}

This diversity of thought, inspired by techniques like Six Thinking Hats~\cite{debono1985six}, reduces groupthink and produces more robust collective reasoning.
这种思维多样性受“六顶思考帽”~\cite{debono1985six}等技术启发，减少了群体思维，并产生更稳健的集体推理。

\begin{warningbox}[Role Conflict Resolution]
\warningbox 标题：角色冲突解决
When agents have overlapping responsibilities, conflicts arise. Resolve them with explicit \textbf{priority rules}: define which role takes precedence for each task type. Alternatively, use a \textbf{meta-agent} whose sole responsibility is conflict arbitration. Never leave role conflicts implicit---they will manifest as contradictory outputs or infinite loops.
当智能体有重叠职责时，就会产生冲突。通过明确的\textbf{优先级规则}来解决：为每种任务类型定义哪个角色优先。或者，使用一个仅负责冲突仲裁的\textbf{元智能体}。永远不要让角色冲突变得隐式——它们会表现为矛盾输出或无限循环。
\end{warningbox}

\section{Multi-Agent Patterns for LLMs}
\section{LLM的多智能体模式}
\label{subsec:mas-patterns}

Beyond architectural topologies, several \textbf{interaction patterns} have proven particularly effective for LLM-based multi-agent systems. (These complement the single-agent design patterns in Chapter~\ref{sec:agent-design-patterns}.)
除了架构拓扑之外，几种\textbf{交互模式}已被证明对基于LLM的多智能体系统特别有效。（这些模式补充了第~\ref{sec:agent-design-patterns}章中的单智能体设计模式。）

\subsection{Debate Pattern}
\subsection{辩论模式}
\label{debate-pattern}

Multiple agents argue for different positions; a judge agent evaluates the arguments and decides. Debate has been shown to improve factual accuracy and reduce hallucinations~\cite{du2023improving}.
多个智能体为不同立场进行辩论；一个裁判智能体评估论点并做出决定。辩论已被证明能提高事实准确性并减少幻觉~\cite{du2023improving}。

\begin{lstlisting}[style=pythonstyle, caption={Debate pattern implementation}]
async def debate_round(question: str, agents: list, judge: Agent,
                       rounds: int = 2) -> str:
    """Run a multi-agent debate and return the judge's verdict."""
    """运行多智能体辩论并返回裁判的裁决。"""
    positions = {a.name: await a.generate_position(question)
                 for a in agents}

    for round_num in range(rounds):
        # Each agent sees others' positions and can rebut
        # 每个智能体看到其他智能体的立场并可以反驳
        rebuttals = {}
        for agent in agents:
            others = {k: v for k, v in positions.items()
                      if k != agent.name}
            rebuttals[agent.name] = await agent.rebut(
                question, positions[agent.name], others
            )
        positions = rebuttals

    # Judge evaluates all final positions
    # 裁判评估所有最终立场
    verdict = await judge.evaluate(question, positions)
    return verdict
\end{lstlisting}

\subsection{Reflection Pattern}
\subsection{反思模式}
\label{reflection-pattern}

One agent generates an output; a second agent critiques it; the first agent revises based on the critique. This implements a generate-critique-revise loop that iteratively improves quality.
一个智能体生成输出；第二个智能体对其进行批评；第一个智能体根据批评进行修改。这实现了一个生成-批评-修改的循环，迭代地提高质量。

\begin{lstlisting}[style=pythonstyle, caption={Reflection pattern}]
async def reflection_loop(task: str, generator: Agent,
                          critic: Agent, max_rounds: int = 3) -> str:
    draft = await generator.generate(task)

    for _ in range(max_rounds):
        critique = await critic.critique(task, draft)
        if critique.is_satisfactory:
            break
        draft = await generator.revise(task, draft, critique.feedback)

    return draft
\end{lstlisting}

\subsection{Division of Labor Pattern}
\subsection{分工模式}
\label{division-of-labor-pattern}

The task is decomposed into independent sub-tasks executed in parallel. Results are aggregated by a synthesis agent. This pattern maximizes throughput for embarrassingly parallel tasks.
任务被分解为独立子任务并行执行。结果由综合智能体聚合。该模式对于易并行任务最大化吞吐量。

\subsection{Pipeline Pattern}
\subsection{流水线模式}
\label{pipeline-pattern}
```

## Motivation: Why Multiple Agents?
## 动机：为何需要多智能体？

Agents form a sequential processing chain: each agent transforms the output of the previous agent. Analogous to Unix pipes. Effective for tasks with clear sequential dependencies (e.g., research $\to$ outline $\to$ draft $\to$ edit $\to$ format).
智能体构成一个顺序处理链：每个智能体对前一个智能体的输出进行转换。类似于Unix管道。适用于具有明确顺序依赖关系的任务（例如，研究 $\to$ 大纲 $\to$ 草稿 $\to$ 编辑 $\to$ 格式）。

## Ensemble Pattern
## 集成模式

Multiple agents independently solve the same problem; a selection mechanism picks the best answer (best-of-$N$) or aggregates answers (mixture-of-experts style). Improves reliability at the cost of compute.
多个智能体独立解决同一问题；一个选择机制挑选最佳答案（best-of-$N$）或聚合答案（混合专家风格）。以计算代价换取可靠性提升。

\begin{equation}
  o^* = \arg\max_{o \in \{o_1,\ldots,o_N\}} \text{score}(o, \text{task})
\end{equation}

where $\text{score}$ can be a reward model, a judge LLM, or a verifier.
其中 $\text{score}$ 可以是奖励模型、评判大语言模型（judge LLM）或验证器（verifier）。

## Teacher-Student Pattern
## 师生模式

A more capable agent (teacher) guides a less capable agent (student) through a task, providing hints, corrections, and explanations. This pattern enables knowledge distillation at inference time and can be used to fine-tune the student agent.
一个能力更强的智能体（教师）引导一个能力较弱的智能体（学生）完成任务，提供提示、纠正和解释。该模式在推理时实现知识蒸馏（knowledge distillation），并可用于微调学生智能体。

## Red Team Pattern
## 红队模式

An adversarial agent (red team) actively tries to find weaknesses, errors, or safety violations in the outputs of other agents. The red team agent is prompted to be maximally critical and creative in its attacks. This pattern is essential for safety-critical applications.
一个对抗性智能体（红队）主动寻找其他智能体输出中的弱点、错误或安全违规行为。红队智能体被提示要在攻击中做到极度批判和富有创意。该模式对安全关键型应用至关重要。

\begin{examplebox}[Red Team Agent Prompt]
\begin{lstlisting}[style=pythonstyle]
RED_TEAM_PROMPT = """You are a red team agent. Your job is to find
flaws, errors, biases, safety violations, and failure modes in the
following output. Be adversarial, creative, and thorough.


Consider:
1. Factual errors or hallucinations
2. Logical inconsistencies
3. Safety and ethical concerns
4. Edge cases the solution doesn't handle
5. Ways a malicious user could exploit this output
6. Unintended consequences


Output: {agent_output}


Provide a detailed critique with specific examples of each flaw found."""
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[红队智能体提示词]
\begin{lstlisting}[style=pythonstyle]
RED_TEAM_PROMPT = """你是一个红队智能体。你的工作是找出
以下输出中的缺陷、错误、偏见、安全违规和故障模式。要具有对抗性、创造性和彻底性。


考虑：
1. 事实错误或幻觉
2. 逻辑不一致
3. 安全与伦理问题
4. 解决方案未处理的边界情况
5. 恶意用户可能利用此输出的方式
6. 非预期的后果


输出: {agent_output}


提供详细的批评，并针对发现的每个缺陷给出具体示例。"""
\end{lstlisting}
\end{examplebox}

## Training Multi-Agent Systems with Reinforcement Learning
## 使用强化学习训练多智能体系统

Training multi-agent systems with RL introduces challenges that go beyond single-agent RL. The fundamental difficulty is that each agent’s environment includes other learning agents, making the environment \textbf{non-stationary} from any single agent’s perspective.
使用强化学习（RL）训练多智能体系统带来了超出单智能体RL的挑战。根本困难在于，每个智能体的环境都包含其他正在学习的智能体，这使得从任何单个智能体的视角来看，环境是\textbf{非平稳的}（non-stationary）。

### Mathematical Formulation
### 数学形式化

A multi-agent system is formalized as a \textbf{Markov Game} (also called a stochastic game)~\cite{shapley1953stochastic}:
多智能体系统被形式化为一个\textbf{马尔可夫博弈}（Markov Game，也称为随机博弈）~\cite{shapley1953stochastic}：

\begin{equation}
  \mathcal{G} = \langle \mathcal{N}, \mathcal{S}, \{\mathcal{A}^i\}_{i \in \mathcal{N}}, \mathcal{T}, \{R^i\}_{i \in \mathcal{N}}, \gamma \rangle
\end{equation}

where $\mathcal{N} = \{1, \ldots, n\}$ is the set of agents, $\mathcal{S}$ is the shared state space, $\mathcal{A}^i$ is agent $i$’s action space, $\mathcal{T}: \mathcal{S} \times \mathcal{A}^1 \times \cdots \times \mathcal{A}^n \to \Delta(\mathcal{S})$ is the transition function, $R^i: \mathcal{S} \times \mathcal{A}^1 \times \cdots \times \mathcal{A}^n \to \mathbb{R}$ is agent $i$’s reward function, and $\gamma$ is the discount factor.
其中 $\mathcal{N} = \{1, \ldots, n\}$ 是智能体集合，$\mathcal{S}$ 是共享状态空间，$\mathcal{A}^i$ 是智能体 $i$ 的动作空间，$\mathcal{T}: \mathcal{S} \times \mathcal{A}^1 \times \cdots \times \mathcal{A}^n \to \Delta(\mathcal{S})$ 是转移函数，$R^i: \mathcal{S} \times \mathcal{A}^1 \times \cdots \times \mathcal{A}^n \to \mathbb{R}$ 是智能体 $i$ 的奖励函数，$\gamma$ 是折扣因子。

Each agent $i$ seeks to maximize its expected discounted return: 
每个智能体 $i$ 旨在最大化其期望折扣回报：
\begin{equation}
  J^i(\pi^1, \ldots, \pi^n) = \mathbb{E}_{\pi^1,\ldots,\pi^n}\left[\sum_{t=0}^{\infty} \gamma^t R^i(s_t, a_t^1, \ldots, a_t^n)\right]
\end{equation}

### Independent Learning
### 独立学习

The simplest approach: each agent $i$ treats other agents as part of its environment and optimizes its own policy $\pi^i$ independently using standard single-agent RL (e.g., PPO, REINFORCE).
最简单的方法：每个智能体 $i$ 将其他智能体视为其环境的一部分，并使用标准单智能体RL（如PPO、REINFORCE）独立优化自己的策略 $\pi^i$。

\begin{equation}
  \nabla_{\theta^i} J^i \approx \mathbb{E}\left[\nabla_{\theta^i} \log \pi^i(a^i_t | o^i_t) \cdot \hat{A}^i_t\right]
\end{equation}

\begin{warningbox}[Non-Stationarity Problem]
Independent learning violates the Markov assumption: as other agents update their policies, the transition and reward distributions seen by agent $i$ change. This can cause training instability, oscillation, and failure to converge. Independent learning works in practice for simple cooperative tasks but struggles in competitive or complex cooperative settings.
\end{warningbox}

\begin{warningbox}[非平稳性问题]
独立学习违反了马尔可夫假设：随着其他智能体更新其策略，智能体 $i$ 所观察到的转移和奖励分布会发生变化。这可能导致训练不稳定、振荡以及无法收敛。独立学习在简单的合作任务中实践可行，但在竞争性或复杂的合作环境中表现不佳。
\end{warningbox}

### Centralized Training, Decentralized Execution (CTDE)
### 集中式训练、分散式执行（CTDE）

CTDE~\cite{lowe2017multi, rashid2018qmix} is the dominant paradigm for cooperative multi-agent RL. During training, a centralized critic has access to the global state $s$ and all agents’ actions $\mathbf{a} = (a^1, \ldots, a^n)$. During execution, each agent acts using only its local observation $o^i$.
CTDE~\cite{lowe2017multi, rashid2018qmix}是合作多智能体RL的主流范式。训练时，一个集中式评论家（centralized critic）可以访问全局状态 $s$ 和所有智能体的动作 $\mathbf{a} = (a^1, \ldots, a^n)$。执行时，每个智能体仅使用其局部观测 $o^i$ 进行行动。

The centralized critic for agent $i$: 
智能体 $i$ 的集中式评论家：
\begin{equation}
  Q^i_\phi(s, \mathbf{a}) = Q^i_\phi(s, a^1, \ldots, a^n)
\end{equation}

The decentralized actor for agent $i$: 
智能体 $i$ 的分散式演员（decentralized actor）：
\begin{equation}
  \pi^i_{\theta^i}(a^i | o^i)
\end{equation}

The policy gradient with centralized critic: 
带有集中式评论家的策略梯度：
\begin{equation}
  \nabla_{\theta^i} J^i = \mathbb{E}\left[\nabla_{\theta^i} \log \pi^i(a^i | o^i) \cdot Q^i_\phi(s, \mathbf{a})\right]
\end{equation}

CTDE resolves non-stationarity during training (the centralized critic sees the full joint state) while preserving decentralized execution (no communication required at inference time).
CTDE解决了训练过程中的非平稳性问题（集中式评论家看到完整的联合状态），同时保留了分散式执行（推理时无需通信）。

### Communication Learning
### 通信学习

Rather than using fixed communication protocols, agents can \textbf{learn what to communicate}. In differentiable communication frameworks~\cite{sukhbaatar2016learning, das2019tarmac}, agents produce continuous communication vectors $m^i_t$ that are passed to other agents:
智能体可以\textbf{学习通信内容}，而不是使用固定的通信协议。在可微分通信框架~\cite{sukhbaatar2016learning, das2019tarmac}中，智能体生成连续的通信向量 $m^i_t$，并将其传递给其他智能体：

\begin{equation}
  a^i_t, m^i_t = \pi^i_{\theta^i}(o^i_t, \{m^j_{t-1}\}_{j \neq i})
\end{equation}

The communication vectors are optimized end-to-end via backpropagation through the joint reward signal. For LLM agents, this is approximated by training agents to produce structured natural language messages that maximize task performance.
通信向量通过联合奖励信号的反向传播进行端到端优化。对于LLM智能体，这通过训练智能体生成结构化的自然语言消息来近似实现，以最大化任务性能。

### Emergent Communication
### 涌现通信

When agents are trained from scratch with only a reward signal (no predefined language), they can develop \textbf{emergent communication protocols}~\cite{lazaridou2020emergent}: shared symbol systems that encode task-relevant information. While fascinating scientifically, emergent communication in LLM systems is typically undesirable---we want agents to communicate in human-interpretable language.
当智能体仅使用奖励信号（无预定义语言）从头开始训练时，它们可以发展出\textbf{涌现通信协议}（emergent communication protocols）~\cite{lazaridou2020emergent}：一种编码任务相关信息的共享符号系统。尽管从科学角度看令人着迷，但在LLM系统中，涌现通信通常是不希望的——我们希望智能体用人类可理解的语言进行通信。

### Self-Play
### 自我对弈

In competitive or mixed-motive settings, \textbf{self-play}~\cite{silver2017mastering} trains agents by having them compete against copies of themselves. This generates an automatic curriculum: as the agent improves, its opponent (a previous version of itself) becomes harder to beat.
在竞争性或混合动机场景中，\textbf{自我对弈}（self-play）~\cite{silver2017mastering}通过让智能体与自己副本竞争来训练智能体。这会产生一个自动课程：随着智能体改进，其对手（自身的一个先前版本）变得更难击败。

For LLM agents, self-play is used in:
对于LLM智能体，自我对弈用于：

\begin{itemize}
  \item Red team vs.~blue team training
  \item Debate training (agents argue against each other)
  \item Negotiation training (agents negotiate with each other)
\end{itemize}

\begin{itemize}
  \item 红队 vs.~蓝队训练
  \item 辩论训练（智能体相互辩论）
  \item 协商训练（智能体相互协商）
\end{itemize}

### Population-Based Training
### 基于种群的训练

\textbf{Population-Based Training (PBT)}~\cite{jaderberg2019human} maintains a diverse population of agents with different policies, hyperparameters, and specializations. Agents are periodically evaluated; underperforming agents are replaced by mutated copies of high-performing agents.
\textbf{基于种群的训练}（Population-Based Training, PBT）~\cite{jaderberg2019human}维护一个多样化的智能体种群，包含不同的策略、超参数和专业化方向。智能体定期被评估；表现不佳的智能体被高性能智能体的变异副本替换。

For multi-agent LLM systems, PBT enables:
对于多智能体LLM系统，PBT实现了：

\begin{itemize}
  \item Automatic discovery of effective role specializations
  \item Robustness to individual agent failures (diverse population)
  \item Avoidance of local optima through population diversity
\end{itemize}

\begin{itemize}
  \item 自动发现有效的角色专业化
  \item 对单个智能体故障的鲁棒性（多样化种群）
  \item 通过种群多样性避免局部最优
\end{itemize}

### Social Welfare and Nash Equilibrium
### 社会福利与纳什均衡

In multi-agent settings, the notion of optimality is more complex than in single-agent settings. Two key solution concepts:
在多智能体环境中，最优性的概念比单智能体环境更为复杂。两个关键解概念：

## \section{Challenges and Solutions}
## \section{挑战与解决方案}
\label{subsec:mas-challenges}

## \subsection{Coordination Overhead}
## \subsection{协调开销}
\label{coordination-overhead}

Every inter‑agent message consumes tokens—and therefore time and money. In a naive implementation, agents communicate constantly, even when unnecessary.
每个智能体间的消息都会消耗 token——从而消耗时间和金钱。在朴素实现中，智能体即使在不必要时也会持续通信。

\begin{keybox}[When NOT to Communicate]
\begin{keybox}[何时不该通信]
\begin{itemize}
  \item When the information is already in the shared blackboard
  \item 当信息已在共享黑板上时
  \item When the receiving agent doesn’t need the information for its current task
  \item 当接收方智能体当前任务不需要该信息时
  \item When the message would duplicate information already sent
  \item 当消息会重复已发送的信息时
  \item When the task is simple enough for a single agent
  \item 当任务简单到单个智能体即可完成时
\end{itemize}

\textbf{Rule}: communicate only when the expected value of the information exceeds the cost of the message.
\textbf{规则}：仅当信息的预期价值超过消息成本时才通信。
\end{keybox}

Quantifying communication cost: if a message costs $c$ tokens and the receiving agent’s task has value $v$, communicate only if the expected improvement in task value $\Delta v > c \cdot \text{cost\_per\_token}$.
量化通信成本：若一条消息花费 $c$ 个 token，接收方智能体任务的价值为 $v$，则仅当任务价值的预期提升 $\Delta v > c \cdot \text{cost\_per\_token}$ 时才通信。

## \subsection{Redundancy vs.~Efficiency}
## \subsection{冗余 vs. 效率}
\label{redundancy-vs.-efficiency}

Multiple agents may independently solve the same sub‑problem, wasting compute. Solutions:
多个智能体可能独立求解同一个子问题，浪费计算资源。解决方案：

\begin{itemize}
  \item \textbf{Duplicate detection}: before starting a task, check the blackboard for existing results
  \item \textbf{重复检测}：在开始任务前，检查黑板上已有的结果
  \item \textbf{Result caching}: store completed sub‑task results with semantic keys for retrieval
  \item \textbf{结果缓存}：用语义键存储已完成的子任务结果以便检索
  \item \textbf{Task locking}: mark tasks as ``in progress'' to prevent duplicate execution
  \item \textbf{任务锁定}：将任务标记为“进行中”以防止重复执行
\end{itemize}

## \subsection{Attribution}
## \subsection{归因}
\label{attribution}

When a multi‑agent system succeeds or fails, which agent is responsible? Attribution is critical for:
当多智能体系统成功或失败时，哪个智能体应负责？归因对以下方面至关重要：

\begin{itemize}
  \item RL reward assignment (credit assignment problem)
  \item 强化学习奖励分配（信用分配问题）
  \item Debugging and improvement
  \item 调试与改进
  \item Trust calibration (which agents to rely on)
  \item 信任校准（应依赖哪些智能体）
\end{itemize}

The \textbf{counterfactual credit assignment} approach estimates each agent’s contribution by asking: “How much would the outcome have changed if this agent had acted differently?”
\textbf{反事实信用分配}方法通过提问“若该智能体行为不同，结果会改变多少？”来估算每个智能体的贡献。

\begin{equation}
  \text{credit}^i = J(\pi^1, \ldots, \pi^n) - J(\pi^1, \ldots, \pi^{i}_{\text{default}}, \ldots, \pi^n)
\label{eq:counterfactual-credit}
\end{equation}

## \subsection{Scalability}
## \subsection{可扩展性}
\label{scalability}

Naive message passing scales as $O(n^2)$ with the number of agents. Solutions:
朴素的消息传递随智能体数量呈 $O(n^2)$ 增长。解决方案：

\begin{itemize}
  \item \textbf{Hierarchical communication}: agents communicate only within their subtree
  \item \textbf{层次化通信}：智能体仅在其子树内通信
  \item \textbf{Topic‑based pub/sub}: agents subscribe only to relevant message topics
  \item \textbf{基于主题的发布/订阅}：智能体仅订阅相关消息主题
  \item \textbf{Sparse communication graphs}: only connect agents that need to interact
  \item \textbf{稀疏通信图}：仅连接需要交互的智能体
  \item \textbf{Asynchronous communication}: agents don’t block waiting for responses
  \item \textbf{异步通信}：智能体不阻塞等待响应
\end{itemize}

## \subsection{Emergent Behavior and Safety}
## \subsection{涌现行为与安全性}
\label{emergent-behavior-and-safety}

Multi‑agent systems can exhibit unexpected emergent behaviors—interactions between agents that produce outcomes no individual agent was designed to produce. This is both a feature (emergent capabilities) and a risk (emergent failures).
多智能体系统可能展现出意外的涌现行为——智能体间的交互产生了任何单个智能体都未设计要产生的结果。这既是功能（涌现能力）也是风险（涌现故障）。

\begin{warningbox}[Safety Concerns in Multi‑Agent Systems]
\begin{warningbox}[多智能体系统中的安全问题]
\begin{itemize}
  \item \textbf{Prompt injection cascades}: a malicious input to one agent propagates through the system
  \item \textbf{提示注入级联}：一个智能体收到的恶意输入在整个系统中传播
  \item \textbf{Reward hacking}: agents find unexpected ways to maximize reward that violate intent
  \item \textbf{奖励黑客}：智能体发现违反原意的意外方式来最大化奖励
  \item \textbf{Collusion}: in competitive settings, agents may develop implicit collusion strategies
  \item \textbf{合谋}：在竞争环境中，智能体可能发展出隐式合谋策略
  \item \textbf{Amplification}: errors or biases in one agent are amplified by downstream agents
  \item \textbf{放大}：一个智能体的错误或偏见被下游智能体放大
\end{itemize}

Always include a \textbf{safety monitor agent} that observes all inter‑agent communications and can halt the system if unsafe behavior is detected.
始终包含一个\textbf{安全监控智能体}，它观察所有智能体间通信，并在检测到不安全行为时中止系统。
\end{warningbox}

## \subsection{Evaluation}
## \subsection{评估}
\label{evaluation}

Evaluating multi‑agent systems requires metrics at multiple levels:
评估多智能体系统需要在多个层面使用指标：

\begin{table}[ht!]
\centering
\caption{Multi‑level evaluation metrics for multi‑agent systems.}
\caption{多智能体系统的多层次评估指标。}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Level} & \textbf{Metric} & \textbf{Example} \\
\textbf{层级} & \textbf{指标} & \textbf{示例} \\
\midrule
System & Task completion rate & \% of tasks completed correctly \\
系统 & 任务完成率 & 正确完成任务的百分比 \\
System & End‑to‑end latency & Time from task to final output \\
系统 & 端到端延迟 & 从任务到最终输出的时间 \\
System & Total token cost & Tokens consumed across all agents \\
系统 & 总 token 成本 & 所有智能体消耗的 token 总数 \\
Agent & Individual accuracy & Per‑agent task success rate \\
智能体 & 个体准确率 & 每个智能体的任务成功率 \\
Agent & Communication efficiency & Useful messages / total messages \\
智能体 & 通信效率 & 有用消息数 / 总消息数 \\
Agent & Contribution score & Counterfactual credit (Eq.~\ref{eq:counterfactual-credit}) \\
智能体 & 贡献得分 & 反事实信用（式~\ref{eq:counterfactual-credit}） \\
Emergent & Coordination quality & Degree of task overlap / gaps \\
涌现 & 协调质量 & 任务重叠 / 缺口程度 \\
\bottomrule
\end{tabular}
\end{table}

## \section{Real‑World Multi‑Agent Applications}
## \section{真实世界的多智能体应用}
\label{subsec:mas-applications}

## \subsection{Software Development Team}
## \subsection{软件开发团队}
\label{software-development-team}

A multi‑agent software development team mirrors a real engineering organization:
一个多智能体软件开发团队模拟了真实的工程组织：

\begin{lstlisting}[style=pythonstyle]
from dataclasses import dataclass
from typing import Optional
import asyncio

@dataclass
class SoftwareTeamState:
    requirements: str
    architecture: Optional[str] = None
    code: Optional[str] = None
    tests: Optional[str] = None
    review_feedback: Optional[str] = None
    final_code: Optional[str] = None
    approved: bool = False
\end{lstlisting}

---

注意：上述代码块中的注释已被省略，原代码中无注释。按规则仅翻译注释，此处无注释，故保持原样。

```markdown
\subsection{Software Development Team}
\subsection{软件开发团队}

\begin{lstlisting}[language=Python]
class SoftwareDevelopmentTeam:
    """
    Multi-agent software team:
      Architect -> Coder -> Tester -> Reviewer -> (iterate or ship)
    """
    """
    多智能体软件团队：
      架构师 -> 编码员 -> 测试员 -> 审查员 ->（迭代或交付）
    """

    def __init__(self, llm_factory):
        self.architect = llm_factory(
            system_prompt="""You are a software architect. Given requirements,
            produce a clear technical design: components, interfaces, data
            structures, and implementation plan."""
        )
        self.architect = llm_factory(
            system_prompt="""你是一名软件架构师。根据需求，
            提供清晰的技术设计：组件、接口、数据结构
            以及实现计划。"""
        )
        self.coder = llm_factory(
            system_prompt="""You are an expert software engineer. Given a
            technical design, write clean, well-documented, production-ready
            code. Follow best practices for the language."""
        )
        self.coder = llm_factory(
            system_prompt="""你是一名专家级软件工程师。根据
            技术设计，编写干净、文档完善、可投入生产的
            代码。遵循该语言的最佳实践。"""
        )
        self.tester = llm_factory(
            system_prompt="""You are a QA engineer. Given code, write
            comprehensive tests: unit tests, edge cases, integration tests.
            Identify potential bugs and failure modes."""
        )
        self.tester = llm_factory(
            system_prompt="""你是一名QA工程师。根据代码，编写
            全面的测试：单元测试、边界案例、集成测试。
            识别潜在的缺陷和故障模式。"""
        )
        self.reviewer = llm_factory(
            system_prompt="""You are a senior code reviewer. Evaluate code
            for correctness, security, performance, and maintainability.
            Provide specific, actionable feedback. Approve only if excellent."""
        )
        self.reviewer = llm_factory(
            system_prompt="""你是一名高级代码审查员。评估代码
            的正确性、安全性、性能和可维护性。
            提供具体、可操作的反馈。仅在代码优秀时批准。"""
        )

    async def build(self, requirements: str,
                    max_iterations: int = 3) -> SoftwareTeamState:
        state = SoftwareTeamState(requirements=requirements)

        # Phase 1: Architecture
        state.architecture = await self.architect.invoke(
            f"Requirements:\n{requirements}\n\nProduce technical design."
        )
        # 阶段1：架构设计
        state.architecture = await self.architect.invoke(
            f"需求：\n{requirements}\n\n提供技术设计。"
        )

        for iteration in range(max_iterations):
            # Phase 2: Implementation
            prompt = (f"Design:\n{state.architecture}\n\n"
                      + (f"Previous feedback:\n{state.review_feedback}\n\n"
                         if state.review_feedback else "")
                      + "Write the implementation.")
            state.code = await self.coder.invoke(prompt)
            # 阶段2：实现
            prompt = (f"设计：\n{state.architecture}\n\n"
                      + (f"先前反馈：\n{state.review_feedback}\n\n"
                         if state.review_feedback else "")
                      + "编写实现代码。")
            state.code = await self.coder.invoke(prompt)

            # Phase 3: Testing
            state.tests = await self.tester.invoke(
                f"Code:\n{state.code}\n\nWrite comprehensive tests."
            )
            # 阶段3：测试
            state.tests = await self.tester.invoke(
                f"代码：\n{state.code}\n\n编写全面的测试。"
            )

            # Phase 4: Review
            review = await self.reviewer.invoke(
                f"Code:\n{state.code}\n\nTests:\n{state.tests}\n\n"
                "Review this code. End with APPROVED or NEEDS_REVISION."
            )
            # 阶段4：审查
            review = await self.reviewer.invoke(
                f"代码：\n{state.code}\n\n测试：\n{state.tests}\n\n"
                "审查这段代码。以APPROVED或NEEDS_REVISION结尾。"
            )

            if "APPROVED" in review:
                state.final_code = state.code
                state.approved = True
                break
            else:
                state.review_feedback = review

        return state

    async def run(self, requirements: str) -> str:
        state = await self.build(requirements)
        if state.approved:
            return f"# Final Implementation\n\n{state.final_code}"
        else:
            return f"# Best Attempt (not approved)\n\n{state.code}"
\end{lstlisting}

\subsection{Research Team}
\subsection{研究团队}

\label{research-team}
\label{research-team}

A research team agent society mirrors academic collaboration:
一个研究团队智能体社会模仿了学术合作：

\begin{itemize}
  \item \textbf{Literature Reviewer}: searches and synthesizes existing work
  \item \textbf{文献审查员(Literature Reviewer)}：搜索并综合现有工作
  \item \textbf{Hypothesis Generator}: proposes novel research directions
  \item \textbf{假设生成器(Hypothesis Generator)}：提出新颖的研究方向
  \item \textbf{Experimentalist}: designs and runs experiments (via code execution)
  \item \textbf{实验员(Experimentalist)}：设计并运行实验（通过代码执行）
  \item \textbf{Statistician}: analyzes results and assesses significance
  \item \textbf{统计学家(Statistician)}：分析结果并评估显著性
  \item \textbf{Writer}: synthesizes findings into a coherent report
  \item \textbf{写作者(Writer)}：将发现综合成一份连贯的报告
\end{itemize}

\subsection{Customer Service System}
\subsection{客户服务系统}

\label{customer-service-system}
\label{customer-service-system}

A tiered customer service system:
一个分层的客户服务系统：

\begin{itemize}
  \item \textbf{Router}: classifies incoming requests and routes to specialists
  \item \textbf{路由器(Router)}：分类传入的请求并路由给专家
  \item \textbf{Billing Specialist}: handles payment and account issues
  \item \textbf{账单专家(Billing Specialist)}：处理支付和账户问题
  \item \textbf{Technical Specialist}: resolves product/service issues
  \item \textbf{技术专家(Technical Specialist)}：解决产品/服务问题
  \item \textbf{Escalation Agent}: handles complex cases requiring human judgment
  \item \textbf{升级代理(Escalation Agent)}：处理需要人工判断的复杂案例
\end{itemize}

\subsection{Creative Team}
\subsection{创意团队}

\label{creative-team}
\label{creative-team}

A creative production pipeline:
一个创意生产流程：

\begin{itemize}
  \item \textbf{Brainstormer}: generates diverse ideas without self-censorship
  \item \textbf{头脑风暴者(Brainstormer)}：不受自我审查地生成多样化创意
  \item \textbf{Drafter}: develops the most promising ideas into full drafts
  \item \textbf{起草者(Drafter)}：将最有潜力的创意发展成完整的草稿
  \item \textbf{Editor}: refines drafts for clarity, style, and coherence
  \item \textbf{编辑(Editor)}：细化草稿以提高清晰度、风格和连贯性
  \item \textbf{Critic}: provides adversarial feedback to strengthen the work
  \item \textbf{评论家(Critic)}：提供对抗性反馈以增强作品
\end{itemize}

\section{Architecture Comparison}
\section{架构比较}

\label{subsec:mas-comparison}
\label{subsec:mas-comparison}

\begin{table}[ht!]
\centering
\caption{Multi-agent architecture patterns compared across key dimensions. Ratings: \textbf{H}igh / \textbf{M}edium / \textbf{L}ow.}
\caption{多智能体架构模式在关键维度上的比较。评级：\textbf{H}（高）/ \textbf{M}（中）/ \textbf{L}（低）。}
\resizebox{\textwidth}{!}{
\begin{tabular}{@{}llllll@{}}
\toprule
\textbf{Architecture} & \textbf{Scalability} & \textbf{Debug} & \textbf{Coord.~Cost} & \textbf{Fault Tol.} & \textbf{Best For} \\
\textbf{架构} & \textbf{可扩展性} & \textbf{可调试性} & \textbf{协调成本} & \textbf{容错性} & \textbf{最佳适用场景} \\
\midrule
Centralized (Supervisor) & M & H & L & L & Simple pipelines; clear task decomposition; small teams \\
集中式（监督者） & M & H & L & L & 简单流水线；任务分解明确；小团队 \\
Decentralized (P2P) & H & L & H & H & Dynamic environments; resilience-critical; large-scale \\
去中心化（P2P） & H & L & H & H & 动态环境；对弹性要求高；大规模 \\
Hierarchical & H & M & M & M & Enterprise workflows; complex multi-domain tasks \\
层次式 & H & M & M & M & 企业工作流；复杂的多领域任务 \\
Swarm & H & L & L & H & Customer service routing; simple handoff chains \\
群体式 & H & L & L & H & 客户服务路由；简单的交接链 \\
Pipeline & M & H & L & L & Sequential processing; clear stage dependencies \\
流水线式 & M & H & L & L & 顺序处理；阶段依赖关系明确 \\
Ensemble & L & H & H & H & High-stakes decisions; reliability over efficiency \\
集成式 & L & H & H & H & 高风险决策；可靠性优先于效率 \\
\bottomrule
\end{tabular}
}
\end{table}

\begin{keybox}[Choosing an Architecture]
\begin{keybox}[选择架构]

\begin{itemize}
  \item \textbf{Independent sub-tasks} $\rightarrow$ parallel architectures (division of labor, ensemble).
  \item \textbf{独立子任务} $\rightarrow$ 并行架构（分工、集成）。
  \item \textbf{Sequential with clear dependencies} $\rightarrow$ pipeline.
  \item \textbf{顺序执行且依赖关系明确} $\rightarrow$ 流水线。
  \item \textbf{Fault tolerance required} $\rightarrow$ avoid centralized; prefer hierarchical or decentralized.
  \item \textbf{需要容错性} $\rightarrow$ 避免集中式；优先选择层次式或去中心化。
  \item \textbf{Debuggability critical} $\rightarrow$ centralized or pipeline (all decisions traceable).
  \item \textbf{可调试性至关重要} $\rightarrow$ 集中式或流水线（所有决策可追溯）。
  \item \textbf{$<$5 agents} $\rightarrow$ centralized is simplest. \textbf{$>$20 agents} $\rightarrow$ hierarchical or swarm.
  \item \textbf{少于5个智能体} $\rightarrow$ 集中式最简单。\textbf{超过20个智能体} $\rightarrow$ 层次式或群体式。
\end{itemize}

In practice, most production systems use \textbf{hierarchical} architectures: a top-level supervisor delegates to domain-specific sub-supervisors, who manage small teams of specialized workers.
在实践中，大多数生产系统使用\textbf{层次式}架构：顶层监督者将任务委托给特定领域的子监督者，再由子监督者管理由专业工作者组成的小团队。
\end{keybox}

\section{Summary}
\section{总结}

\label{subsec:mas-summary}
\label{subsec:mas-summary}

Multi-agent systems represent a fundamental shift in how we deploy LLMs: from isolated assistants to collaborative societies of specialized agents. The key insights from this section:
多智能体系统代表了我们在部署LLM（大语言模型）方面的根本性转变：从孤立助手转变为由专业智能体组成的协作社会。本节的关键见解如下：

\begin{keybox}[Multi-Agent Systems: Key Takeaways]
\begin{keybox}[多智能体系统：关键要点]

\begin{enumerate}
  \item \textbf{Architecture matters}: the topology of agent connections determines scalability, debuggability, and fault tolerance. Choose based on task structure and operational requirements.
  \item \textbf{架构至关重要}：智能体连接的拓扑结构决定了可扩展性、可调试性和容错性。根据任务结构和运营需求进行选择。
  \item \textbf{Coordination is expensive}: every inter-agent message costs tokens. Design communication protocols to minimize overhead while preserving necessary information flow.
  \item \textbf{协调成本高昂}：每次智能体间的消息都会消耗令牌。设计通信协议以最小化开销，同时保留必要的信息流。
  \item \textbf{Specialization enables quality}: agents with focused roles and tailored prompts consistently outperform generalist agents on complex tasks.
  \item \textbf{专业化提升质量}：具有明确角色和定制提示的智能体在复杂任务上始终优于通用型智能体。
  \item \textbf{RL training is hard}: multi-agent RL introduces non-stationarity, credit assignment challenges, and emergent behaviors. CTDE is the current best practice for cooperative settings.
  \item \textbf{强化学习训练困难}：多智能体强化学习引入了非平稳性、信用分配挑战和涌现行为。CTDE（集中训练分散执行）是目前协作场景的最佳实践。
  \item \textbf{Safety requires explicit design}: multi-agent systems can amplify errors and exhibit unexpected emergent behaviors. Safety monitoring must be a first-class architectural concern.
  \item \textbf{安全性需要明确设计}：多智能体系统可能放大错误并表现出意外的涌现行为。安全监控必须成为架构的一等公民。
  \item \textbf{Start simple}: begin with a centralized supervisor pattern, measure its limitations, and evolve toward more complex architectures only when necessary.
  \item \textbf{从简单开始}：从集中式监督者模式入手，衡量其局限性，仅当必要时才向更复杂的架构演进。
\end{enumerate}
\end{keybox}

The field of multi-agent LLM systems is evolving rapidly. The patterns and techniques described here represent the current state of the art, but new architectures, coordination mechanisms, and training algorithms are emerging continuously. The foundational principles---specialization, coordination, emergent behavior, and the tension between efficiency and robustness---will remain relevant regardless of how the specific implementations evolve.
多智能体LLM系统领域正在快速发展。这里描述的模式和技术代表了当前的最高水平，但新的架构、协调机制和训练算法不断涌现。无论具体实现如何演变，基础原则——专业化、协调、涌现行为，以及效率与鲁棒性之间的张力——将始终保持其相关性。
```