```markdown
\chapter{Agent-to-Agent Communication (A2A)}
\chapter{智能体间通信（A2A）}
\label{sec:a2a}


As large language models evolve from isolated assistants into collaborative networks of specialized agents, the question of \emph{how agents talk to each other} becomes as important as how they reason internally. This section covers the protocols, patterns, and engineering practices that enable multi-agent systems to coordinate, delegate, and collectively solve problems that no single agent could handle alone.
随着大型语言模型从独立的助手演变为由专业智能体组成的协作网络，\emph{智能体之间如何相互通信}这一问题变得与其内部推理方式同等重要。本节将介绍使多智能体系统能够协调、委托并共同解决单个智能体无法单独处理的问题的协议、模式及工程实践。

\section{Motivation: Why Agents Must Communicate}
\section{动机：为什么智能体必须通信}
\label{sec:a2a:motivation}


\begin{intuitionbox}[The Specialization Imperative]
\begin{intuitionbox}[专业化的必要性]
A single generalist agent faces a fundamental tension: breadth of knowledge versus depth of capability. Real-world tasks---legal document review, multi-step scientific research, enterprise software development---demand both. Agent-to-agent communication resolves this tension by allowing a \emph{network} of specialists to collaborate, each contributing its strengths while delegating weaknesses.
单个通才型智能体面临一个根本性的矛盾：知识的广度与能力的深度。现实世界的任务——法律文档审阅、多步骤科学研究、企业级软件开发——两者都需要。智能体间通信通过让一个由专家组成的\emph{网络}进行协作来解决这一矛盾，每个专家贡献自身优势，同时委托弱点。
\end{intuitionbox}


Several forces drive the need for structured inter-agent communication:
多种因素推动了对结构化智能体间通信的需求：

\paragraph{Cognitive Load and Context Limits.}
\paragraph{认知负载与上下文限制。}
\label{cognitive-load-and-context-limits.}


Every LLM operates within a finite context window. Complex workflows---spanning hundreds of documents, tool calls, and reasoning steps---quickly exceed what a single agent can hold in memory. By decomposing tasks across agents, each agent operates within a manageable context, and the orchestrating agent maintains only high-level state.
每个大语言模型都在有限的上下文窗口内运行。复杂的工作流程——涵盖数百份文档、工具调用和推理步骤——很快会超出单个智能体的记忆容量。通过将任务分解到多个智能体，每个智能体在可管理的上下文内运行，而编排智能体仅维护高层状态。

\paragraph{Specialization and Expertise.}
\paragraph{专业化与专业知识。}
\label{specialization-and-expertise.}


Different agents may be fine-tuned, prompted, or tool-equipped for specific domains: a \texttt{CodeAgent} with access to compilers and test runners, a \texttt{LegalAgent} with access to case-law databases, a \texttt{DataAgent} with statistical libraries. Routing subtasks to the right specialist improves both quality and efficiency.
不同的智能体可能针对特定领域进行微调、提示或配备工具：一个能够访问编译器和测试运行器的 \texttt{CodeAgent}，一个能够访问判例法数据库的 \texttt{LegalAgent}，一个带有统计库的 \texttt{DataAgent}。将子任务路由到合适的专家能够提高质量和效率。

\paragraph{Parallelism and Throughput.}
\paragraph{并行性与吞吐量。}
\label{parallelism-and-throughput.}


Independent subtasks can be dispatched to multiple agents simultaneously. A research orchestrator might fan out literature searches across five specialized agents in parallel, then synthesize their results---dramatically reducing wall-clock time.
独立的子任务可以同时分派给多个智能体。一个研究编排器可能会将文献搜索并行分发给五个专业智能体，然后综合它们的结果——从而大幅减少墙上时钟时间（实际耗时）。

\paragraph{Fault Isolation and Resilience.}
\paragraph{故障隔离与弹性。}
\label{fault-isolation-and-resilience.}


When one agent fails, a well-designed multi-agent system can retry with a different agent, fall back to a simpler approach, or escalate to a human---without collapsing the entire workflow.
当一个智能体失败时，设计良好的多智能体系统可以改用另一个智能体重试，回退到更简单的方法，或是上报给人工——而不会导致整个工作流崩溃。

\paragraph{Delegation and Handoff.}
\paragraph{委托与交接。}
\label{delegation-and-handoff.}


Long-running tasks may need to be handed off between agents as context shifts. An initial \texttt{PlannerAgent} decomposes a goal, hands subtasks to \texttt{ExecutorAgents}, and a final \texttt{ReviewerAgent} validates outputs---each agent receiving exactly the context it needs.
长时间运行的任务可能需要在智能体之间进行交接，因为上下文会发生变化。初始的 \texttt{PlannerAgent} 分解目标，将子任务交给 \texttt{ExecutorAgents}，最后由 \texttt{ReviewerAgent} 验证输出——每个智能体获得它正好需要的上下文。

\begin{keybox}[Core Requirements for A2A Communication]
\begin{keybox}[A2A通信的核心需求]
\begin{enumerate}
  \item \textbf{Discoverability}: Agents must be able to find other agents and understand their capabilities.
  \item \textbf{Discoverability（可发现性）}：智能体必须能够找到其他智能体并理解其能力。
  \item \textbf{Interoperability}: Agents built by different teams or vendors must speak a common protocol.
  \item \textbf{Interoperability（互操作性）}：由不同团队或供应商构建的智能体必须使用共同协议进行通信。
  \item \textbf{Asynchrony}: Long-running tasks must not block the caller; results arrive via callbacks or polling.
  \item \textbf{Asynchrony（异步性）}：长时间运行的任务不得阻塞调用方；结果通过回调或轮询到达。
  \item \textbf{Security}: Agents must authenticate each other and enforce authorization boundaries.
  \item \textbf{Security（安全性）}：智能体必须相互认证并实施授权边界。
  \item \textbf{Observability}: Every message exchange must be traceable for debugging and auditing.
  \item \textbf{Observability（可观测性）}：每次消息交换都必须可追溯，以便调试和审计。
\end{enumerate}
\end{keybox}


\section{The Google A2A Protocol}
\section{Google A2A 协议}
\label{sec:a2a:google}


In April 2025, Google (with contributions from over 50 technology partners) released the \textbf{Agent-to-Agent (A2A) Protocol}~\cite{google-a2a-2025}, an open specification for interoperable communication between AI agents. The protocol was subsequently donated to the \textbf{Linux Foundation} and has grown to over 150 supporting organizations as of 2026. A2A is designed around a set of core principles that distinguish it from earlier ad-hoc approaches.
2025年4月，Google（与超过50家技术合作伙伴共同贡献）发布了\textbf{智能体间通信（A2A）协议}~\cite{google-a2a-2025}，这是一项用于AI智能体之间互操作通信的开放规范。该协议随后被捐赠给\textbf{Linux基金会}，截至2026年已获得超过150家组织的支持。A2A围绕一套核心原则进行设计，使其区别于之前临时性的方法。

\subsection{Design Philosophy}
\subsection{设计理念}
\label{design-philosophy}


The A2A specification articulates five guiding principles (adapted from the official spec~\cite{google-a2a-2025}, §1.2):
A2A规范阐述了五项指导原则（改编自官方规范~\cite{google-a2a-2025}，§1.2）：

\begin{keybox}[A2A Design Principles]
\begin{keybox}[A2A设计原则]
Opaque execution
不透明的执行

Calling agents never inspect the internals of a remote agent---they interact solely through the declared interface. Whether the target is GPT-4, Gemini, or a rule-based system is irrelevant to the protocol, enabling genuinely heterogeneous agent ecosystems.
调用方智能体从不检查远程智能体的内部实现——它们仅通过声明的接口进行交互。无论目标是GPT-4、Gemini还是基于规则的系统，对协议而言都无关紧要，从而实现了真正异构的智能体生态。

Enterprise readiness
企业就绪

Authentication (OAuth 2.0, API keys, JWT), audit logging, and regulatory compliance are not afterthoughts---they are integrated at the protocol level from the outset.
身份验证（OAuth 2.0、API密钥、JWT）、审计日志记录和法规合规性并非事后添加——它们从一开始就被集成到协议层面。

Modality agnosticism
模态无关性

A single message may combine text, binary files, and structured JSON payloads, accommodating agents that operate on images, audio, code, or documents without protocol extensions.
单条消息可以组合文本、二进制文件和结构化JSON负载，从而容纳处理图像、音频、代码或文档的智能体，而无需协议扩展。

Simplicity via existing standards
通过现有标准实现简单性

Rather than inventing new transports, A2A reuses HTTP/HTTPS with JSON-RPC~2.0 messages, Server-Sent Events (SSE) for streaming, and gRPC as an alternative binding---technologies that every infrastructure team already operates.
A2A没有发明新的传输层，而是复用了HTTP/HTTPS与JSON-RPC 2.0消息、用于流式传输的服务器推送事件（SSE），以及作为替代绑定的gRPC——这些都是每个基础设施团队已经在使用的技术。

Async-first task model
异步优先的任务模型

Long-running operations are the norm, not the exception. Push notifications and polling are both first-class mechanisms, so callers never need to hold open a connection for hours.
长时间运行的操作是常态而非例外。推送通知和轮询都是一等机制，因此调用方无需保持长时间的连接打开状态。
\end{keybox}


\subsection{Agent Cards}
\subsection{智能体卡片}
\label{agent-cards}


The foundation of A2A discoverability is the \textbf{Agent Card}---a machine-readable JSON manifest hosted at a well-known endpoint (\texttt{/.well-known/agent.json}). It advertises what the agent can do, how to authenticate, and where to send tasks---analogous to an OpenAPI spec but for autonomous agents rather than REST endpoints.
A2A可发现性的基础是\textbf{智能体卡片}（Agent Card）——一份机器可读的JSON清单，托管在众所周知的端点（\texttt{/.well-known/agent.json}）。它宣告了智能体能够做什么、如何认证以及将任务发送到哪里——类似于OpenAPI规范，但针对的是自主智能体而非REST端点。

\begin{examplebox}[Agent Card Structure]
\begin{examplebox}[智能体卡片结构]
\begin{lstlisting}[style=pythonstyle]
# Agent Card served at https://agent.example.com/.well-known/agent.json
# 在 https://agent.example.com/.well-known/agent.json 提供的智能体卡片
agent_card = {
    "name": "DataAnalysisAgent",
    "description": "Analyzes structured datasets, produces statistical summaries, "
                   "generates visualizations, and answers data questions.",
    "description": "分析结构化数据集，生成统计摘要，创建可视化，并回答数据相关问题。",
    "url": "https://agent.example.com/a2a",
    "version": "1.2.0",
    "capabilities": {
        "streaming": True,
        "pushNotifications": True,
        "stateTransitionHistory": True
    },
    "authentication": {
        "schemes": ["Bearer", "ApiKey"]
    },
    "skills": [
        {
            "id": "statistical-analysis",
            "name": "Statistical Analysis",
            "name": "统计分析",
            "description": "Compute descriptive statistics, run hypothesis tests, "
                           "fit regression models on tabular data.",
            "description": "计算描述性统计，运行假设检验，在表格数据上拟合回归模型。",
            "tags": ["statistics", "data", "analysis", "regression"],
            "examples": [
                "What is the correlation between columns A and B?",
                "Run a t-test comparing these two groups.",
                "Fit a linear regression predicting sales from ad spend."
            ],
            "inputModes": ["text", "data"],
            "outputModes": ["text", "data", "file"]
        },
        {
            "id": "visualization",
            "name": "Data Visualization",
            "name": "数据可视化",
            "description": "Generate charts, plots, and dashboards from data.",
            "description": "根据数据生成图表、图形和仪表盘。",
            "tags": ["charts", "plots", "visualization", "dashboard"],
            "examples": [
                "Create a bar chart of monthly revenue.",
                "Plot the distribution of customer ages."
            ],
            "inputModes": ["text", "data"],
            "outputModes": ["file", "text"]
        }
    ],
    "defaultInputModes": ["text"],
    "defaultOutputModes": ["text"]
}
\end{lstlisting}
\end{examplebox}


Agent Cards enable \emph{capability-based routing}: an orchestrator agent can fetch cards from a registry, semantically match a subtask to the most appropriate agent, and dispatch accordingly---all without hardcoded routing logic.
智能体卡片实现了\emph{基于能力的路由}：编排智能体可以从注册中心获取卡片，将子任务语义匹配到最合适的智能体，并相应地分派——全部无需硬编码的路由逻辑。
```

## Task Lifecycle
## 任务生命周期

A2A models all work as \textbf{Tasks}. A task progresses through a well-defined state machine:
A2A 将所有工作建模为 \textbf{任务（Tasks）}。一个任务会经过一个定义良好的状态机进行推进：

\texttt{submitted}
\texttt{submitted}

The client has sent the task; the server has acknowledged receipt.
客户端已发送任务；服务器已确认收到。

\texttt{working}
\texttt{working}

The agent is actively processing. The client may poll or await SSE events.
智能体正在积极处理中。客户端可以轮询或等待 SSE 事件。

\texttt{input-required}
\texttt{input-required}

The agent needs additional information from the user or calling agent before it can proceed (e.g., a clarifying question, a missing credential).
智能体需要从用户或调用智能体处获取额外信息后才能继续（例如，一个澄清问题、一个缺失的凭证）。

\texttt{completed}
\texttt{completed}

The task finished successfully; results are available in the response.
任务成功完成；结果可在响应中获取。

\texttt{failed}
\texttt{failed}

An unrecoverable error occurred; an error message explains the cause.
发生了不可恢复的错误；错误消息解释了原因。

\texttt{rejected}
\texttt{rejected}

The agent declined the task (e.g., outside its capabilities or unauthorized). Added in A2A v1.0.
智能体拒绝了任务（例如，超出其能力范围或未经授权）。在 A2A v1.0 中新增。

\texttt{canceled}
\texttt{canceled}

The task was aborted, either by the client or by the server.
任务被中止，由客户端或服务器发起。

## Streaming via Server-Sent Events
## 通过服务器发送事件（Server-Sent Events）进行流式传输

For tasks that produce incremental output (e.g., a long report being written, a code file being generated), A2A uses \textbf{Server-Sent Events (SSE)}. The client opens a persistent HTTP connection and receives a stream of JSON events:
对于产生增量输出的任务（例如，正在撰写的长报告、正在生成的代码文件），A2A 使用 \textbf{服务器发送事件（Server-Sent Events, SSE）}。客户端打开一个持久的 HTTP 连接，并接收一串 JSON 事件流：

\begin{examplebox}[SSE Event Stream Example]
\begin{examplebox}[SSE 事件流示例]

\begin{lstlisting}[style=pythonstyle]
# Each SSE event carries a TaskStatusUpdateEvent or TaskArtifactUpdateEvent
# Example stream for a "write a research report" task:
# 每个 SSE 事件携带一个 TaskStatusUpdateEvent 或 TaskArtifactUpdateEvent
# 针对"撰写研究报告"任务的示例流：

# Event 1: status update
# 事件 1：状态更新
data: {
  "id": "task-abc123",
  "status": {"state": "working"},
  "final": false
}

# Event 2: partial artifact (streaming text)
# 事件 2：部分工件（流式文本）
data: {
  "id": "task-abc123",
  "artifact": {
    "parts": [{"type": "text", "text": "## Introduction\n\nRecent advances in..."}],
    "index": 0,
    "append": false,
    "lastChunk": false
  },
  "final": false
}

# Event 3: more text appended
# 事件 3：追加更多文本
data: {
  "id": "task-abc123",
  "artifact": {
    "parts": [{"type": "text", "text": " reinforcement learning have shown..."}],
    "index": 0,
    "append": true,   # append to existing artifact
    "lastChunk": false
  },
  "final": false
}

# Final event: task complete
# 最终事件：任务完成
data: {
  "id": "task-abc123",
  "status": {"state": "completed"},
  "final": true
}
\end{lstlisting}
\end{examplebox}
\end{examplebox}

## Push Notifications for Long-Running Tasks
## 长时间运行任务的推送通知

When a task may take minutes or hours, maintaining an open SSE connection is impractical. A2A supports \textbf{push notifications}: the client registers a webhook URL, and the server POSTs status updates as the task progresses.
当任务可能需要几分钟或几小时才能完成时，保持一个开放的 SSE 连接是不切实际的。A2A 支持 \textbf{推送通知（push notifications）}：客户端注册一个 webhook URL，服务器在任务进展过程中以 POST 方式发送状态更新。

\begin{lstlisting}[style=pythonstyle]
# Client registers a push notification endpoint when submitting the task
# 客户端在提交任务时注册一个推送通知端点
task_request = {
    "id": "task-xyz789",
    "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "Analyze Q3 sales data and produce a report."}]
    },
    "pushNotification": {
        "url": "https://my-orchestrator.example.com/webhooks/a2a",
        "token": "secret-hmac-token-for-verification",
        "authentication": {
            "schemes": ["Bearer"],
            "credentials": "eyJhbGciOiJIUzI1NiJ9..."
        }
    }
}
# The server will POST TaskStatusUpdateEvent objects to the webhook URL
# as the task transitions through states.
# 当任务在各个状态之间转换时，服务器会向 webhook URL 发送 POST 请求，携带 TaskStatusUpdateEvent 对象。
\end{lstlisting}

## Message Format
## 消息格式

A2A messages consist of a \textbf{role} (\texttt{user} or \texttt{agent}) plus a list of typed \textbf{parts} (text, file, or structured data). The full message schema, multi-modal examples, and context-passing guidelines are covered in Section~\ref{sec:a2a:messages}.
A2A 消息由一个 \textbf{角色（role）}（\texttt{user} 或 \texttt{agent}）加上一个带类型的 \textbf{部件（parts）}列表（文本、文件或结构化数据）组成。完整的消息模式、多模态示例以及上下文传递指南将在第~\ref{sec:a2a:messages} 节中介绍。

## Authentication and Authorization
## 身份认证与授权

A2A supports multiple authentication schemes, declared in the Agent Card and enforced per-request:
A2A 支持多种身份认证方案，这些方案在 Agent Card（智能体卡片）中声明，并在每个请求中强制执行：

\begin{itemize}
  \item \textbf{Bearer tokens (JWT/OAuth 2.0)}: Standard for enterprise deployments; tokens carry scopes that limit what the calling agent is permitted to request.
  \item \textbf{Bearer 令牌（JWT/OAuth 2.0）}：企业部署的标准；令牌携带作用域（scopes），限制调用智能体被允许请求的内容。
  \item \textbf{API keys}: Simpler scheme for internal or trusted environments.
  \item \textbf{API 密钥}：适用于内部或可信环境的更简单的方案。
  \item \textbf{Mutual TLS (mTLS)}: Certificate-based authentication for high-security deployments.
  \item \textbf{双向 TLS（mTLS）}：基于证书的身份认证，适用于高安全性的部署。
  \item \textbf{OpenID Connect}: Federated identity, enabling cross-organization agent communication.
  \item \textbf{OpenID Connect}：联合身份，支持跨组织智能体通信。
\end{itemize}

\begin{warningbox}[Authorization Scope Enforcement]
\begin{warningbox}[授权作用域执行]

An agent receiving a task must verify not only \emph{who} is calling (authentication) but \emph{what they are allowed to request} (authorization). A \texttt{ReportingAgent} might accept read-only data queries from any authenticated agent, but restrict write operations to agents holding a specific OAuth scope. Failing to enforce this creates privilege escalation vulnerabilities in multi-agent systems.
接收任务的智能体不仅需要验证调用者的 \emph{身份}（身份认证），还需要验证调用者 \emph{被允许请求什么}（授权）。一个 \texttt{ReportingAgent} 可能接受来自任何已认证智能体的只读数据查询，但将写操作限制为持有特定 OAuth 作用域的智能体。未能强制执行这一点会造成多智能体系统中的权限提升漏洞。
\end{warningbox}
\end{warningbox}

\section{Communication Patterns}
\section{通信模式}

Multi-agent systems employ a variety of communication patterns depending on the nature of the task, latency requirements, and the number of agents involved.
多智能体系统根据任务的性质、延迟要求和涉及的智能体数量，采用多种通信模式。

## Request-Response
## 请求-响应

The simplest pattern: Agent A sends a task to Agent B and waits for a complete response. Suitable for short, well-defined subtasks where the result is needed before proceeding.
最简单的模式：智能体 A 发送一个任务给智能体 B，并等待完整的响应。适用于简短、定义明确的子任务，这些任务需要在继续之前获取结果。

## Streaming
## 流式传输

Agent A opens an SSE connection; Agent B streams partial results as they are produced. Ideal for long-form generation (reports, code), real-time collaboration, or progressive UI updates.
智能体 A 打开一个 SSE 连接；智能体 B 在生成部分结果时将其流式传输。适用于长文本生成（报告、代码）、实时协作或渐进式 UI 更新。

\begin{examplebox}[Streaming Pattern Use Case]
\begin{examplebox}[流式传输模式使用案例]

An orchestrator asks a \texttt{WritingAgent} to draft a 10-page technical document. Rather than waiting 2 minutes for the complete document, the orchestrator streams each section as it is written, allowing a \texttt{ReviewAgent} to begin reviewing early sections while later sections are still being generated---a pipeline that reduces total latency by 40--60\%.
一个协调器（orchestrator）要求一个 \texttt{WritingAgent} 起草一份 10 页的技术文档。协调器不等待 2 分钟获取完整文档，而是在每个章节被写好后立即流式传输，从而允许一个 \texttt{ReviewAgent} 在后面的章节仍在生成时就开始审阅前面的章节——这种流水线可将总延迟减少 40\% 到 60\%。
\end{examplebox}
\end{examplebox}

## Multi-Turn Interaction
## 多轮交互

Some tasks require iterative refinement. The agent enters \texttt{input-required} state, the orchestrator provides clarification, and the task resumes. This mirrors human collaborative workflows: draft $\to$ feedback $\to$ revision.
某些任务需要迭代改进。智能体进入 \texttt{input-required} 状态，协调器提供澄清，然后任务继续。这反映了人类协作工作流：草稿 $\to$ 反馈 $\to$ 修订。

\begin{lstlisting}[style=pythonstyle]
# Multi-turn: orchestrator handles input-required state
# 多轮交互：协调器处理 input-required 状态
async def run_multiturn_task(client, initial_message):
    task = await client.send_task(message=initial_message)

    while task.status.state not in ("completed", "failed", "canceled"):
        if task.status.state == "input-required":
            # Agent needs clarification
            # 智能体需要澄清
            clarification_needed = task.status.message
            print(f"Agent asks: {clarification_needed}")

            # Orchestrator generates or forwards a clarifying response
            # 协调器生成或转发一个澄清响应
            user_reply = await get_clarification(clarification_needed)

            # Send the reply to continue the task
            # 发送回复以继续任务
            task = await client.send_task(
                task_id=task.id,
                message={"role": "user",
                         "parts": [{"type": "text", "text": user_reply}]}
            )
        else:
            # Still working --- poll after a delay
            # 仍在工作中——延迟后轮询
            await asyncio.sleep(2)
            task = await client.get_task(task.id)

    return task
\end{lstlisting}

## Broadcast
## 广播

An orchestrator sends the same message to multiple agents simultaneously---useful for announcements, distributing shared context, or triggering parallel independent workflows.
协调器同时向多个智能体发送相同的消息——用于公告、分发共享上下文或触发并行的独立工作流。

## Publish-Subscribe (Pub-Sub)
## 发布-订阅（Pub-Sub）

Agents subscribe to event channels (e.g., \texttt{new-document-uploaded}, \texttt{model-retrained}). When an event fires, all subscribed agents are notified. This decouples producers from consumers and enables reactive, event-driven architectures.
智能体订阅事件通道（例如，\texttt{new-document-uploaded}，\texttt{model-retrained}）。当事件触发时，所有订阅的智能体会收到通知。这使生产者和消费者解耦，并支持响应式的事件驱动架构。

## Negotiation
## 协商

```markdown
## Motivation: Why Agents Must Communicate
## 动机：为什么智能体必须通信

Two agents exchange proposals and counter-proposals to reach agreement on a plan, resource allocation, or approach. Common in multi-agent planning systems where agents have different objectives or constraints.
两个智能体交换提议和反提议，以就计划、资源分配或方法达成一致。常见于智能体具有不同目标或约束的多智能体规划系统中。

\begin{examplebox}[Negotiation Pattern]
\begin{examplebox}[协商模式]
A \texttt{PlannerAgent} proposes a 5-step research plan. A \texttt{ResourceAgent} responds that Step 3 (running a large simulation) would exceed the compute budget. The \texttt{PlannerAgent} counter-proposes a scaled-down simulation. The \texttt{ResourceAgent} approves. The agreed plan is then dispatched to executor agents.
一个 \texttt{PlannerAgent} 提出一个5步研究计划。一个 \texttt{ResourceAgent} 回应说第3步（运行大型模拟）将超出计算预算。\texttt{PlannerAgent} 提出一个缩小规模的模拟作为反提议。\texttt{ResourceAgent} 批准。然后商定的计划被分发给执行智能体。
\end{examplebox}

\subsection{Auction-Based Task Allocation}
\subsection{基于拍卖的任务分配}
\label{auction-based-task-allocation}

The orchestrator announces a task with requirements; candidate agents submit bids (estimated completion time, confidence, cost); the orchestrator awards the task to the winning bidder. This enables dynamic, market-based load balancing across a pool of agents.
协调者宣布一个带有需求的任务；候选智能体提交出价（预计完成时间、置信度、成本）；协调者将任务授予中标者。这实现了跨智能体池的动态、基于市场的负载均衡。

\begin{table}[ht!]
\centering
\caption{Summary of A2A communication patterns.}
\caption{A2A通信模式总结。}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Pattern} & \textbf{Latency} & \textbf{Best For} \\
\textbf{模式} & \textbf{延迟} & \textbf{最佳适用场景} \\
\midrule
Request-Response & Low & Short, well-defined subtasks \\
请求-响应 & 低 & 简短、定义明确的子任务 \\
Streaming & Low (first token) & Long-form generation, real-time UI \\
流式 & 低（首个 token） & 长文本生成、实时界面 \\
Multi-Turn & Medium & Ambiguous tasks requiring clarification \\
多轮 & 中 & 需要澄清的模糊任务 \\
Broadcast & Low & Shared context distribution \\
广播 & 低 & 共享上下文分发 \\
Pub-Sub & Variable & Event-driven reactive workflows \\
发布-订阅 & 可变 & 事件驱动的响应式工作流 \\
Negotiation & Medium--High & Resource-constrained planning \\
协商 & 中-高 & 资源受限的规划 \\
Auction & Medium & Dynamic load balancing \\
拍卖 & 中 & 动态负载均衡 \\
\bottomrule
\end{tabular}
\end{table}

\section{Agent Discovery and Routing}
\section{智能体发现与路由}
\label{sec:a2a:discovery}

Before an agent can communicate with another, it must \emph{find} it. Agent discovery is the process of locating agents that can handle a given task.
在智能体能够与另一个智能体通信之前，它必须先“找到”它。智能体发现是定位能够处理给定任务的智能体的过程。

\subsection{Agent Registries}
\subsection{智能体注册表}
\label{agent-registries}

An \textbf{agent registry} is a directory service that indexes Agent Cards and provides search and lookup APIs. Two deployment models exist:
\textbf{智能体注册表}是一种目录服务，它索引智能体卡片（Agent Cards）并提供搜索和查找 API。存在两种部署模型：

Centralized Registry
集中式注册表

A single authoritative registry (e.g., an enterprise service catalog) indexes all agents. Simple to operate but creates a single point of failure and may not scale to cross-organization deployments.
一个单一的权威注册表（例如企业服务目录）索引所有智能体。操作简单，但会造成单点故障，并且可能无法扩展到跨组织部署。

Federated Registry
联邦式注册表

Multiple registries, each authoritative for a domain or organization, with cross-registry search protocols. More resilient and privacy-preserving, but requires standardized federation protocols.
多个注册表，每个注册表对一个领域或组织具有权威性，并具备跨注册表搜索协议。更具弹性和隐私保护性，但需要标准化的联邦协议。

\subsection{Capability-Based Routing}
\subsection{基于能力的路由}
\label{capability-based-routing}

Rather than hardcoding agent URLs, orchestrators perform \textbf{capability-based routing}: they query the registry for agents matching required skills, then select the best match.
协调者不硬编码智能体 URL，而是执行\textbf{基于能力的路由}：他们查询注册表以查找匹配所需技能的智能体，然后选择最佳匹配。

\begin{lstlisting}[style=pythonstyle]
class AgentRouter:
    """Routes tasks to agents based on capability matching."""
    """根据能力匹配将任务路由到智能体。"""

    def __init__(self, registry_url: str):
        self.registry_url = registry_url
        self._cache: dict[str, list[AgentCard]] = {}

    async def find_agents(self, required_skill: str,
                          tags: list[str] | None = None) -> list[AgentCard]:
        """Query registry for agents with the required skill."""
        """查询注册表以获取具有所需技能的智能体。"""
        params = {"skill": required_skill}
        if tags:
            params["tags"] = ",".join(tags)
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.registry_url}/agents", params=params)
            return [AgentCard(**card) for card in resp.json()["agents"]]

    async def route(self, task_description: str) -> AgentCard:
        """Semantically match a task description to the best available agent."""
        """将任务描述语义匹配到最佳可用智能体。"""
        # Embed the task description
        # 嵌入任务描述
        task_embedding = await embed(task_description)

        # Fetch all registered agents
        # 获取所有注册的智能体
        all_agents = await self.find_agents(required_skill="*")

        # Score each agent by cosine similarity of task to agent description
        # 通过任务与智能体描述的余弦相似度对每个智能体评分
        scored = []
        for agent in all_agents:
            agent_embedding = await embed(agent.description)
            score = cosine_similarity(task_embedding, agent_embedding)
            scored.append((score, agent))

        # Return the highest-scoring agent
        # 返回得分最高的智能体
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]
\end{lstlisting}

\subsection{Load Balancing Across Equivalent Agents}
\subsection{跨等价智能体的负载均衡}
\label{load-balancing-across-equivalent-agents}

When multiple agents offer the same capability, the router must distribute load. Common strategies:
当多个智能体提供相同能力时，路由器必须分配负载。常见策略包括：

\begin{itemize}
  \item \textbf{Round-robin}: Distribute tasks evenly across all available agents.
  \item \textbf{轮询}：将所有可用智能体之间的任务均匀分配。
  \item \textbf{Least-loaded}: Route to the agent with the fewest active tasks (requires health/metrics endpoints).
  \item \textbf{最少负载}：路由到活跃任务最少的智能体（需要健康/指标端点）。
  \item \textbf{Latency-aware}: Route to the agent with the lowest recent response time.
  \item \textbf{延迟感知}：路由到最近响应时间最低的智能体。
  \item \textbf{Affinity-based}: Route related tasks to the same agent to exploit cached context.
  \item \textbf{亲和性}：将相关任务路由到同一智能体，以利用缓存的上下文。
\end{itemize}

\subsection{Version Management and Compatibility}
\subsection{版本管理与兼容性}
\label{version-management-and-compatibility}

Agent Cards include a \texttt{version} field. Orchestrators should specify minimum version requirements and handle graceful degradation when only older versions are available. Semantic versioning~\cite{preston2024semver} (\texttt{MAJOR.MINOR.PATCH}) is recommended: breaking interface changes increment \texttt{MAJOR}, new capabilities increment \texttt{MINOR}.
智能体卡片包含一个 \texttt{version} 字段。协调者应指定最低版本要求，并在只有旧版本可用时处理优雅降级。建议使用语义化版本控制~\cite{preston2024semver}（\texttt{MAJOR.MINOR.PATCH}）：破坏性的接口更改递增 \texttt{MAJOR}，新增能力递增 \texttt{MINOR}。

\begin{warningbox}[Version Skew in Long-Running Systems]
\begin{warningbox}[长期运行系统中的版本偏差]
In production multi-agent systems, different agents may be updated at different times, creating version skew. An orchestrator compiled against Agent Card v2.1 may encounter agents still running v1.3. Always implement backward-compatible message handling and test cross-version scenarios explicitly.
在生产级多智能体系统中，不同的智能体可能在不同时间更新，从而产生版本偏差。针对智能体卡片 v2.1 编译的协调者可能会遇到仍运行 v1.3 的智能体。务必实现向后兼容的消息处理，并显式测试跨版本场景。
\end{warningbox}

\section{Message Formats and Schemas}
\section{消息格式与模式}
\label{sec:a2a:messages}

\subsection{Structured vs.~Unstructured Messages}
\subsection{结构化消息 vs. 非结构化消息}
\label{structured-vs.-unstructured-messages}

A2A supports a spectrum from fully unstructured (plain text) to fully structured (typed JSON schemas). The right choice depends on the agents involved:
A2A 支持从完全非结构化（纯文本）到完全结构化（类型化 JSON 模式）的区间。正确的选择取决于所涉及的智能体：

\begin{table}[ht!]
\centering
\caption{Structured vs.~unstructured A2A message trade-offs.}
\caption{结构化 vs. 非结构化 A2A 消息权衡。}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Message Type} & \textbf{Advantages} & \textbf{Disadvantages} \\
\textbf{消息类型} & \textbf{优势} & \textbf{劣势} \\
\midrule
Plain text & Flexible, human-readable, easy to generate & Hard to parse reliably, no schema validation \\
纯文本 & 灵活、人类可读、易于生成 & 难以可靠解析、无模式验证 \\
Structured JSON & Machine-parseable, validatable, typed & Requires schema agreement, less flexible \\
结构化 JSON & 机器可解析、可验证、类型化 & 需要模式约定、灵活性较低 \\
Hybrid (text + data) & Human-readable intent + machine-parseable payload & More complex to construct and parse \\
混合（文本+数据） & 人类可读的意图 + 机器可解析的有效载荷 & 构建和解析更复杂 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Multi-Modal Messages}
\subsection{多模态消息}
\label{multi-modal-messages}

A2A messages are structured as a \textbf{role} (\texttt{user} or \texttt{agent}) plus a list of typed \textbf{parts}:
A2A 消息被结构化为一个\textbf{角色}（\texttt{user} 或 \texttt{agent}）加上一个类型化\textbf{部分}列表：

\begin{table}[ht!]
\centering
\caption{A2A message part types (wire format uses \texttt{"type": "text"|"file"|"data"}).}
\caption{A2A 消息部分类型（线路格式使用 \texttt{"type": "text"|"file"|"data"}）。}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Part Type} & \textbf{Fields} & \textbf{Use Case} \\
\textbf{部分类型} & \textbf{字段} & \textbf{使用场景} \\
\midrule
\texttt{TextPart} & \texttt{text: string} & Natural language instructions, responses \\
\texttt{TextPart} & \texttt{text: string} & 自然语言指令、响应 \\
\texttt{FilePart} & \texttt{mimeType}, \texttt{uri} or \texttt{bytes} & Documents, images, audio, code files \\
\texttt{FilePart} & \texttt{mimeType}, \texttt{uri} 或 \texttt{bytes} & 文档、图片、音频、代码文件 \\
\texttt{DataPart} & \texttt{data: object} & Structured JSON (tool results, schemas) \\
\texttt{DataPart} & \texttt{data: object} & 结构化 JSON（工具结果、模式） \\
\bottomrule
\end{tabular}
\end{table}

Modern agents increasingly work with non-text modalities. A2A’s \texttt{FilePart} supports any MIME type, enabling rich multi-modal workflows:
现代智能体越来越多地处理非文本模态。A2A 的 \texttt{FilePart} 支持任何 MIME 类型，从而实现丰富的多模态工作流：
```

\begin{examplebox}[Multi-Modal A2A Message: Data Analysis]
\begin{lstlisting}[style=pythonstyle]
# A message combining text instructions with a data payload and a file
message = {
    "role": "user",
    "parts": [
        {
            "type": "text",
            "text": "Analyze the attached CSV and the schema below. "
                    "Identify anomalies and produce a summary report."
        },
        {
            "type": "file",
            "mimeType": "text/csv",
            "uri": "https://storage.example.com/data/sales_q3.csv"
        },
        {
            "type": "data",
            "data": {
                "schema": {
                    "columns": ["date", "region", "product", "revenue", "units"],
                    "types":   ["date", "string", "string", "float", "int"]
                },
                "expectedRowCount": 15000,
                "anomalyThreshold": 3.0  # z-score threshold
            }
        }
    ]
}
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[多模态 A2A 消息：数据分析]
\begin{lstlisting}[style=pythonstyle]
# 一条结合文本指令、数据负载和文件的消息
message = {
    "role": "user",
    "parts": [
        {
            "type": "text",
            "text": "分析附带的 CSV 文件和以下模式。"
                    "识别异常并生成摘要报告。"
        },
        {
            "type": "file",
            "mimeType": "text/csv",
            "uri": "https://storage.example.com/data/sales_q3.csv"
        },
        {
            "type": "data",
            "data": {
                "schema": {
                    "columns": ["date", "region", "product", "revenue", "units"],
                    "types":   ["date", "string", "string", "float", "int"]
                },
                "expectedRowCount": 15000,
                "anomalyThreshold": 3.0  # z-score 阈值
            }
        }
    ]
}
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[Multi-Modal A2A Message: Image Analysis]
\begin{lstlisting}[style=pythonstyle]
# Multi-modal message: text + image + structured data
multimodal_message = {
    "role": "user",
    "parts": [
        {"type": "text",
         "text": "Describe what is wrong with this chart and suggest fixes."},
        {"type": "file",
         "mimeType": "image/png",
         "bytes": base64.b64encode(chart_image_bytes).decode()},
        {"type": "data",
         "data": {
             "chartType": "bar",
             "dataSource": "Q3 Revenue by Region",
             "knownIssues": ["y-axis does not start at zero",
                             "missing error bars"]
         }}
    ]
}
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[多模态 A2A 消息：图像分析]
\begin{lstlisting}[style=pythonstyle]
# 多模态消息：文本 + 图像 + 结构化数据
multimodal_message = {
    "role": "user",
    "parts": [
        {"type": "text",
         "text": "描述这张图表有什么问题，并建议修复方法。"},
        {"type": "file",
         "mimeType": "image/png",
         "bytes": base64.b64encode(chart_image_bytes).decode()},
        {"type": "data",
         "data": {
             "chartType": "bar",
             "dataSource": "Q3 Revenue by Region",
             "knownIssues": ["y-axis does not start at zero",
                             "missing error bars"]
         }}
    ]
}
\end{lstlisting}
\end{examplebox}

\subsection{Context Passing: What to Share vs.~What to Keep Private}
\label{context-passing-what-to-share-vs.-what-to-keep-private}

\subsection{上下文传递：共享什么 vs. 保留什么}
\label{context-passing-what-to-share-vs.-what-to-keep-private}

A critical design decision in multi-agent systems is \emph{context scoping}: how much of the conversation history and internal state to pass to a sub-agent.

多智能体系统中的一个关键设计决策是 \emph{上下文范围限定}：将多少对话历史和内部状态传递给子智能体。

\begin{keybox}[Context Scoping Principles]
Minimal Context


Pass only what the sub-agent needs to complete its task. Reduces token usage, latency, and the risk of leaking sensitive information.


Summarized Context


Instead of passing raw conversation history, pass a structured summary: goals, constraints, decisions made, and relevant facts.


Private State


Internal reasoning, intermediate drafts, and user PII should generally \emph{not} be forwarded to sub-agents unless explicitly required.


Correlation IDs


Always pass a \texttt{correlationId} so that sub-agent actions can be traced back to the originating workflow in logs and audit trails.
\end{keybox}

\begin{keybox}[上下文范围限定原则]
最小上下文


仅传递子智能体完成任务所需的内容。减少令牌使用量、延迟以及敏感信息泄露的风险。


摘要上下文


不传递原始对话历史，而是传递结构化摘要：目标、约束条件、已做出的决策以及相关事实。


私有状态


内部推理、中间草稿和用户个人身份信息通常 \emph{不} 应转发给子智能体，除非明确要求。


关联ID


始终传递 \texttt{correlationId}，以便在日志和审计跟踪中将子智能体的操作追溯到原始工作流。
\end{keybox}

\subsection{Conversation Threading and Correlation IDs}
\label{conversation-threading-and-correlation-ids}

\subsection{对话线程与关联ID}
\label{conversation-threading-and-correlation-ids}

In complex workflows, many tasks may be in flight simultaneously. \textbf{Correlation IDs} link related tasks across agents:

在复杂工作流中，许多任务可能同时进行。\textbf{关联ID} 将智能体之间的相关任务链接起来：

\begin{lstlisting}[style=pythonstyle]
import uuid


class WorkflowContext:
    """Carries correlation metadata through a multi-agent workflow."""

    def __init__(self, workflow_id: str | None = None):
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.span_id = str(uuid.uuid4())
        self.parent_span_id: str | None = None

    def child_context(self) -> "WorkflowContext":
        """Create a child context for a sub-task."""
        child = WorkflowContext(workflow_id=self.workflow_id)
        child.parent_span_id = self.span_id
        return child

    def to_metadata(self) -> dict:
        return {
            "x-workflow-id": self.workflow_id,
            "x-span-id": self.span_id,
            "x-parent-span-id": self.parent_span_id
        }


# Usage: attach to every A2A task submission
ctx = WorkflowContext()
task = await client.send_task(
    message=message,
    metadata=ctx.to_metadata()
)
# Sub-tasks use child contexts for tracing
sub_ctx = ctx.child_context()
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle]
import uuid


class WorkflowContext:
    """在多智能体工作流中携带关联元数据。"""

    def __init__(self, workflow_id: str | None = None):
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.span_id = str(uuid.uuid4())
        self.parent_span_id: str | None = None

    def child_context(self) -> "WorkflowContext":
        """为子任务创建子上下文。"""
        child = WorkflowContext(workflow_id=self.workflow_id)
        child.parent_span_id = self.span_id
        return child

    def to_metadata(self) -> dict:
        return {
            "x-workflow-id": self.workflow_id,
            "x-span-id": self.span_id,
            "x-parent-span-id": self.parent_span_id
        }


# 用法：附加到每个 A2A 任务提交中
ctx = WorkflowContext()
task = await client.send_task(
    message=message,
    metadata=ctx.to_metadata()
)
# 子任务使用子上下文进行跟踪
sub_ctx = ctx.child_context()
\end{lstlisting}

\section{Coordination Protocols}
\label{sec:a2a:coordination}

\section{协调协议}
\label{sec:a2a:coordination}

Beyond point-to-point communication, multi-agent systems benefit from higher-level \textbf{coordination protocols}---structured interaction patterns that enable collective decision-making and problem-solving.

除了点对点通信，多智能体系统还受益于更高级别的\textbf{协调协议}——一种结构化的交互模式，能够实现集体决策和问题解决。

\subsection{Contract Net Protocol}
\label{contract-net-protocol}

\subsection{合同网协议}
\label{contract-net-protocol}

The \textbf{Contract Net Protocol (CNP)}~\cite{smith1980contract} is a classic multi-agent coordination mechanism adapted for LLM-based systems:

\textbf{合同网协议 (CNP)}~\cite{smith1980contract} 是一种经典的多智能体协调机制，适用于基于大语言模型（LLM）的系统：

\begin{enumerate}
  \item \textbf{Announcement}: The manager agent broadcasts a task announcement to all potential contractor agents, including task requirements and evaluation criteria.
  \item \textbf{Announcement（公告）}: 管理智能体向所有潜在的承包智能体广播任务公告，包括任务需求和评估标准。
  \item \textbf{Bidding}: Contractor agents evaluate the task against their capabilities and submit bids containing estimated completion time, confidence, and resource requirements.
  \item \textbf{Bidding（投标）}: 承包智能体根据自身能力评估任务，并提交包含预计完成时间、置信度和资源需求的投标。
  \item \textbf{Award}: The manager selects the winning bid (or multiple bids for parallel subtasks) and awards the contract.
  \item \textbf{Award（授标）}: 管理智能体选择中标（或多个中标用于并行子任务）并授予合同。
  \item \textbf{Execution and Reporting}: The contractor executes the task and reports results back to the manager.
  \item \textbf{Execution and Reporting（执行与报告）}: 承包智能体执行任务并向管理智能体报告结果。
\end{enumerate}

\begin{examplebox}[Contract Net Protocol Implementation]
\begin{lstlisting}[style=pythonstyle]
import dataclasses


class ContractNetManager:
    """Implements the Contract Net Protocol for task allocation."""

    async def allocate_task(self, task: Task,
                            candidate_agents: list[AgentCard]) -> AgentCard:
        # Phase 1: Announce task to all candidates
        announcement = {
            "type": "task-announcement",
            "task": dataclasses.asdict(task),
            "deadline": (datetime.now(timezone.utc) + timedelta(seconds=10)).isoformat(),
            "evaluationCriteria": ["confidence", "estimatedTime", "cost"]
        }

        # Phase 2: Collect bids
        bids = await asyncio.gather(*[
            self._request_bid(agent, announcement)
            for agent in candidate_agents
        ], return_exceptions=True)

        valid_bids = [(agent, bid) for agent, bid in zip(candidate_agents, bids)
                      if not isinstance(bid, Exception) and bid is not None]

        if not valid_bids:
            raise RuntimeError(f"No agents bid on task {task.id}")

        # Phase 3: Award to best bidder (highest confidence, lowest time)
        def score_bid(agent_bid):
            _, bid = agent_bid
            return bid["confidence"] - 0.1 * bid["estimatedSeconds"]

        winner_agent, winning_bid = max(valid_bids, key=score_bid)

        # Notify winner and losers
        await self._award_contract(winner_agent, task)
        await asyncio.gather(*[
            self._reject_bid(agent, task.id)
            for agent, _ in valid_bids if agent != winner_agent
        ])

        return winner_agent

    async def _request_bid(self, agent: AgentCard,
                           announcement: dict) -> dict | None:
        """Ask an agent to bid on a task."""
        try:
            result = await self.client.send_task(
                agent_url=agent.url,
                message={"role": "user",
                         "parts": [{"type": "data", "data": announcement}]}
            )
            return result.artifacts[0].parts[0]["data"]
        except Exception:
            return None
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[合同网协议实现]
\begin{lstlisting}[style=pythonstyle]
import dataclasses


class ContractNetManager:
    """实现用于任务分配的合同网协议。"""

    async def allocate_task(self, task: Task,
                            candidate_agents: list[AgentCard]) -> AgentCard:
        # 阶段1：向所有候选智能体公告任务
        announcement = {
            "type": "task-announcement",
            "task": dataclasses.asdict(task),
            "deadline": (datetime.now(timezone.utc) + timedelta(seconds=10)).isoformat(),
            "evaluationCriteria": ["confidence", "estimatedTime", "cost"]
        }

        # 阶段2：收集投标
        bids = await asyncio.gather(*[
            self._request_bid(agent, announcement)
            for agent in candidate_agents
        ], return_exceptions=True)

        valid_bids = [(agent, bid) for agent, bid in zip(candidate_agents, bids)
                      if not isinstance(bid, Exception) and bid is not None]

        if not valid_bids:
            raise RuntimeError(f"No agents bid on task {task.id}")

        # 阶段3：授予最佳投标者（最高置信度、最低时间）
        def score_bid(agent_bid):
            _, bid = agent_bid
            return bid["confidence"] - 0.1 * bid["estimatedSeconds"]

        winner_agent, winning_bid = max(valid_bids, key=score_bid)

        # 通知中标者和未中标者
        await self._award_contract(winner_agent, task)
        await asyncio.gather(*[
            self._reject_bid(agent, task.id)
            for agent, _ in valid_bids if agent != winner_agent
        ])

        return winner_agent

    async def _request_bid(self, agent: AgentCard,
                           announcement: dict) -> dict | None:
        """请求智能体对任务进行投标。"""
        try:
            result = await self.client.send_task(
                agent_url=agent.url,
                message={"role": "user",
                         "parts": [{"type": "data", "data": announcement}]}
            )
            return result.artifacts[0].parts[0]["data"]
        except Exception:
            return None
\end{lstlisting}
\end{examplebox}

\subsection{Blackboard Systems}
\label{blackboard-systems}

\subsection{黑板系统}
\label{blackboard-systems}

A \textbf{blackboard system}~\cite{hayes1985blackboard} provides a shared workspace (the ``blackboard'') where agents post partial solutions, observations, and hypotheses. Other agents monitor the blackboard and contribute when they can add value---an \emph{opportunistic} problem-solving approach.

\textbf{黑板系统}~\cite{hayes1985blackboard} 提供了一个共享工作空间（“黑板”），智能体在此发布部分解决方案、观察结果和假设。其他智能体监控黑板，并在能够增加价值时做出贡献——这是一种\textemph{机会主义}的问题解决方法。

Blackboard systems are well-suited to problems where the solution path is not known in advance and different agents may contribute at different stages---such as scientific hypothesis generation, complex debugging, or multi-source intelligence analysis.

黑板系统非常适合那些解决路径未知且不同智能体可能在不同阶段做出贡献的问题——例如科学假设生成、复杂调试或多源情报分析。

\subsection{Consensus Protocols}
\label{consensus-protocols}

\subsection{共识协议}
\label{consensus-protocols}

## Section Title
## 章节标题

When multiple agents must agree on a decision (e.g., which plan to execute, whether a result is correct), \textbf{consensus protocols} provide structured voting mechanisms:
当多个智能体必须就某个决策达成一致时（例如，执行哪个计划、某个结果是否正确），\textbf{共识协议 (Consensus Protocols)} 提供了结构化的投票机制：

Simple Majority Voting
简单多数投票

Each agent votes; the option with $> 50\%$ of votes wins. Fast but vulnerable to correlated errors if agents share the same base model.
每个智能体投票；得票数超过 $50\%$ 的选项获胜。速度快，但如果智能体共享相同的基础模型，则容易受到关联错误的影响。

Weighted Voting
加权投票

Votes are weighted by agent confidence or historical accuracy. More robust but requires calibrated confidence estimates.
投票权重根据智能体的置信度或历史准确性分配。更鲁棒，但需要校准的置信度估计。

Quorum-Based
基于法定人数

A decision requires agreement from at least $k$ of $n$ agents. Provides fault tolerance: up to $n-k$ agents can fail or disagree without blocking.
决策需要至少 $k$ 个智能体（共 $n$ 个）达成一致。提供容错能力：最多 $n-k$ 个智能体可以失败或不同意而不阻塞流程。

Delphi Method
德尔菲法

Agents vote, see anonymized results, revise their votes, and repeat until convergence. Reduces anchoring bias and encourages genuine deliberation.
智能体投票，查看匿名结果，修改投票，重复直至收敛。减少锚定偏差并鼓励真正的协商。

\begin{lstlisting}[style=pythonstyle]
async def quorum_vote(agents: list[AgentCard], question: str,
                      options: list[str], quorum: int) -> str | None:
    """Run a quorum vote across agents. Returns winning option or None."""
    """在多个智能体之间运行法定人数投票。返回获胜选项或 None。"""
    votes = await asyncio.gather(*[
        ask_agent_to_vote(agent, question, options)
        for agent in agents
    ])

    counts: dict[str, int] = {}
    for vote in votes:
        if vote in options:
            counts[vote] = counts.get(vote, 0) + 1

    # Return first option that reaches quorum
    # 返回第一个达到法定人数的选项
    for option, count in sorted(counts.items(), key=lambda x: -x[1]):
        if count >= quorum:
            return option
    return None  # No quorum reached
    return None  # 未达到法定人数
\end{lstlisting}

\subsection{Leader Election}
\subsection{领导者选举}
\label{leader-election}

In dynamic multi-agent systems, a \textbf{leader} (orchestrator) may need to be elected at runtime---for example, when the original orchestrator fails or when agents self-organize without a pre-assigned coordinator. Classic distributed systems algorithms (Bully, Ring) can be adapted for agent networks, with agents exchanging capability scores or priority tokens to elect the most capable available agent as leader.
在动态多智能体系统中，可能需要在运行时选举一个\textbf{领导者 (Leader)}（协调器）——例如，当原始协调器故障或智能体在没有预先指定协调器的情况下自组织时。经典的分布式系统算法（霸凌算法、环形算法）可以适用于智能体网络，智能体通过交换能力分数或优先级令牌来选举最有能力的可用智能体作为领导者。

\section{A2A vs.~MCP: Complementary Protocols}
\section{A2A 与 MCP：互补协议}
\label{sec:a2a:vs_mcp}

A common source of confusion is the relationship between A2A and the \textbf{Model Context Protocol (MCP)}~\cite{anthropic-mcp-2024}. These protocols are \emph{complementary}, not competing:
一个常见的困惑来源是 A2A 与 \textbf{模型上下文协议 (Model Context Protocol, MCP)}~\cite{anthropic-mcp-2024} 之间的关系。这些协议是\emph{互补}的，而非竞争关系：

\begin{keybox}[The Core Distinction]
\begin{keybox}[核心区别]
\begin{itemize}
  \item \textbf{MCP} is the \emph{vertical} protocol: it extends an agent downward into the world of databases, APIs, file systems, and code executors. Only the agent reasons; MCP endpoints are deterministic services.
  \item \textbf{A2A} is the \emph{horizontal} protocol: it links one reasoning agent to another. Both sides are intelligent actors capable of reasoning, planning, and tool use.
\end{itemize}
\begin{itemize}
  \item \textbf{MCP} 是\emph{垂直}协议：它将智能体向下扩展到数据库、API、文件系统和代码执行器的世界。只有智能体进行推理；MCP 端点是确定性服务。
  \item \textbf{A2A} 是\emph{水平}协议：它将一个推理智能体与另一个连接起来。双方都是能够进行推理、规划和工具使用的智能行为体。
\end{itemize}
\end{keybox}

\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Dimension} & \textbf{MCP} & \textbf{A2A} \\
\midrule
\textbf{Participants} & Agent $\leftrightarrow$ Tool/Resource & Agent $\leftrightarrow$ Agent \\
\textbf{Intelligence} & One side (agent) is intelligent & Both sides are intelligent \\
\textbf{Statefulness} & Typically stateless tool calls & Stateful tasks with lifecycle \\
\textbf{Streaming} & Limited (tool results) & First-class SSE streaming \\
\textbf{Discovery} & Tool manifests & Agent Cards \\
\textbf{Auth model} & Server-controlled & Mutual, OAuth 2.0 \\
\textbf{Typical latency} & Milliseconds & Seconds to minutes \\
\textbf{Use case} & ``Search the web'', ``Run SQL'' & ``Delegate to specialist'' \\
\bottomrule
\end{tabular}

\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{维度} & \textbf{MCP} & \textbf{A2A} \\
\midrule
\textbf{参与者} & 智能体 $\leftrightarrow$ 工具/资源 & 智能体 $\leftrightarrow$ 智能体 \\
\textbf{智能性} & 一侧（智能体）具有智能 & 双方都具备智能 \\
\textbf{有状态性} & 通常是无状态的工具调用 & 有状态的任务，具有生命周期 \\
\textbf{流式传输} & 有限（工具结果） & 一流的 SSE 流式传输 \\
\textbf{发现机制} & 工具清单 & 智能体卡片 \\
\textbf{认证模型} & 服务器控制 & 双向认证，OAuth 2.0 \\
\textbf{典型延迟} & 毫秒级 & 秒到分钟级 \\
\textbf{用例} & “搜索网页”、“运行 SQL” & “委派给专家” \\
\bottomrule
\end{tabular}

\subsection{When to Use Which}
\subsection{何时使用哪种协议}
\label{when-to-use-which}

\begin{itemize}
  \item Use \textbf{MCP} when the remote endpoint is a deterministic function: a database query, an API call, a code execution sandbox. The agent controls the interaction entirely.
  \item Use \textbf{A2A} when the remote endpoint needs to \emph{reason} about the request: interpret ambiguous instructions, make judgment calls, use its own tools, or engage in multi-turn dialogue.
  \item Use \textbf{both} in the same system: an orchestrator agent uses A2A to delegate to specialist agents, and each specialist agent uses MCP to access its tools.
\end{itemize}
\begin{itemize}
  \item 当远程端点是确定性函数时使用 \textbf{MCP}：数据库查询、API 调用、代码执行沙箱。智能体完全控制交互。
  \item 当远程端点需要对请求进行\emph{推理}时使用 \textbf{A2A}：解释模糊指令、做出判断、使用自己的工具或进行多轮对话。
  \item 在同一个系统中同时使用\textbf{两者}：协调器智能体使用 A2A 将任务委派给专家智能体，每个专家智能体使用 MCP 访问其工具。
\end{itemize}

\subsection{Combined Architecture}
\subsection{组合架构}
\label{combined-architecture}

In production multi-agent systems, A2A and MCP work together at different layers: \textbf{A2A} handles inter-agent delegation and coordination (horizontal communication between peers), while \textbf{MCP} handles each agent’s connection to its tools and data sources (vertical integration with capabilities). This separation of concerns is key to building scalable agentic architectures.
在生产级多智能体系统中，A2A 和 MCP 在不同层次上协同工作：\textbf{A2A} 处理智能体间的委派与协调（对等体之间的水平通信），而 \textbf{MCP} 处理每个智能体与其工具和数据源的连接（与能力的垂直集成）。这种关注点分离是构建可扩展智能体架构的关键。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_068_combined-a2a-mcp.png}
\caption{Combined A2A + MCP architecture. The orchestrator delegates to specialist agents via A2A; each agent accesses its tools via MCP servers.}
\caption{组合的 A2A + MCP 架构。协调器通过 A2A 将任务委派给专家智能体；每个智能体通过 MCP 服务器访问其工具。}
\label{fig:combined-a2a-mcp}
\end{figure}

\begin{tcolorbox}
\begin{itemize}
  \item \textbf{A2A for delegation}: When an agent needs capabilities it doesn’t have, it delegates to another agent via A2A task messages. Each agent is a self-contained service with its own Agent Card.
  \item \textbf{MCP for tool access}: Each agent connects to its tools through MCP servers. This means tools are never exposed directly to other agents --- only through the owning agent’s interface.
  \item \textbf{Separation of trust boundaries}: The orchestrator trusts specialist agents (verified via A2A authentication). Each specialist trusts its own MCP servers (local or authenticated). No transitive tool access.
  \item \textbf{Independent scaling}: Code-heavy workloads can scale CodeAgent instances; data workloads scale DataAgent. The orchestrator remains lightweight.
\end{itemize}
\begin{itemize}
  \item \textbf{A2A 用于委派}：当智能体缺少某些能力时，它通过 A2A 任务消息委派给另一个智能体。每个智能体都是一个自包含的服务，拥有自己的智能体卡片。
  \item \textbf{MCP 用于工具访问}：每个智能体通过 MCP 服务器连接到其工具。这意味着工具永远不会直接暴露给其他智能体——只能通过所属智能体的接口访问。
  \item \textbf{信任边界分离}：协调器信任专家智能体（通过 A2A 认证验证）。每个专家智能体信任自己的 MCP 服务器（本地或经过认证的）。没有传递性的工具访问。
  \item \textbf{独立扩展}：代码密集型工作负载可以扩展 CodeAgent 实例；数据工作负载扩展 DataAgent。协调器保持轻量级。
\end{itemize}
\end{tcolorbox}

\section{Security and Trust in Multi-Agent Systems}
\section{多智能体系统中的安全与信任}
\label{sec:a2a:security}

Multi-agent systems introduce unique security challenges. When Agent A delegates to Agent B, which delegates to Agent C, the chain of trust must be carefully managed.
多智能体系统带来了独特的安全挑战。当智能体 A 委派给智能体 B，而智能体 B 又委派给智能体 C 时，信任链必须被仔细管理。

\subsection{Agent Identity Verification}
\subsection{智能体身份验证}
\label{agent-identity-verification}

Each agent must have a verifiable identity. Options include:
每个智能体都必须有一个可验证的身份。选项包括：

\begin{itemize}
  \item \textbf{JWT tokens}~\cite{rfc7519} signed by a trusted identity provider, carrying the agent’s ID, issuer, and expiry. Verified by the receiving agent using the provider’s public key.
  \item \textbf{mTLS certificates}~\cite{rfc8705} issued by an internal CA, providing both authentication and transport encryption.
  \item \textbf{Decentralized identifiers (DIDs)}~\cite{w3c-did-2022} for cross-organization scenarios where no single trusted authority exists.
\end{itemize}
\begin{itemize}
  \item \textbf{JWT 令牌 (JWT tokens)}~\cite{rfc7519}：由可信身份提供者签名，包含智能体的 ID、签发者和过期时间。接收智能体使用提供者的公钥进行验证。
  \item \textbf{mTLS 证书}~\cite{rfc8705}：由内部 CA 签发，提供身份验证和传输加密。
  \item \textbf{去中心化标识符 (DIDs)}~\cite{w3c-did-2022}：适用于跨组织场景，其中不存在单一可信权威机构。
\end{itemize}

\subsection{Message Integrity and Encryption}
\subsection{消息完整性与加密}
\label{message-integrity-and-encryption}

\begin{itemize}
  \item All A2A communication should occur over \textbf{TLS 1.3}~\cite{rfc8446} to prevent eavesdropping and man-in-the-middle attacks.
  \item For sensitive payloads, \textbf{end-to-end encryption} (e.g., JWE) ensures that intermediate infrastructure (load balancers, proxies) cannot read message content.
  \item \textbf{Message signing} (JWS) provides non-repudiation: the receiving agent can prove that a specific message came from a specific sender.
\end{itemize}
\begin{itemize}
  \item 所有 A2A 通信应通过 \textbf{TLS 1.3}~\cite{rfc8446} 进行，以防止窃听和中间人攻击。
  \item 对于敏感负载，\textbf{端到端加密 (End-to-End Encryption)}（例如 JWE）确保中间基础设施（负载均衡器、代理）无法读取消息内容。
  \item \textbf{消息签名 (Message Signing)}（JWS）提供不可否认性：接收智能体可以证明特定消息来自特定发送者。
\end{itemize}

\subsection{Authorization Scopes}
\subsection{授权范围}
\label{authorization-scopes}

Not every agent should be able to ask every other agent to do anything. OAuth~2.0 authorization scopes~\cite{rfc6749} define the boundaries:
并非每个智能体都应能够要求任何其他智能体做任何事情。OAuth 2.0 授权范围~\cite{rfc6749} 定义了边界：

\begin{lstlisting}[style=pythonstyle]
# Example OAuth 2.0 scopes for a DataAgent
SCOPES = {
    "data:read":        "Read data from connected databases",
    "data:write":       "Write or modify data in connected databases",
    "data:export":      "Export data to external systems",
    "analysis:run":     "Execute statistical analyses",
    "analysis:schedule":"Schedule recurring analyses",
    "admin:config":     "Modify agent configuration"
}
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle]
# DataAgent 的 OAuth 2.0 范围示例
SCOPES = {
    "data:read":        "从连接的数据库读取数据",
    "data:write":       "在连接的数据库中写入或修改数据",
    "data:export":      "将数据导出到外部系统",
    "analysis:run":     "执行统计分析",
    "analysis:schedule":"安排定期分析",
    "admin:config":     "修改智能体配置"
}
\end{lstlisting}

```markdown
# A ReportingAgent might hold only: data:read, analysis:run
# An ETL pipeline agent might hold: data:read, data:write, data:export
# Only a human admin holds: admin:config
# 一个 ReportingAgent 可能仅持有：data:read, analysis:run
# 一个 ETL 流水线 agent 可能持有：data:read, data:write, data:export
# 只有人类管理员持有：admin:config

class A2AServer:
    def verify_authorization(self, token: str, required_scope: str) -> bool:
        """Verify that the calling agent holds the required scope."""
        """验证调用 agent 是否持有所需的 scope。"""
        claims = jwt.decode(token, self.public_key, algorithms=["RS256"])
        granted_scopes = claims.get("scope", "").split()
        if required_scope not in granted_scopes:
            raise PermissionError(
                f"Caller lacks required scope '{required_scope}'. "
                f"Granted: {granted_scopes}"
            )
        return True
\end{lstlisting}


\subsection{Audit Trails and Accountability}
\subsection{审计追踪与问责}
\label{audit-trails-and-accountability}


\begin{warningbox}[The Accountability Gap]
In a chain of agent delegations, it can become unclear \emph{who} is responsible for an action. If Agent A asks Agent B to delete a file, and Agent B does so, who is accountable? Every A2A interaction must be logged with: the calling agent’s identity, the task description, the authorization token used, the timestamp, and the outcome. This audit trail is essential for incident response, compliance, and debugging.
\end{warningbox}

\begin{warningbox}[问责缺口]
在一连串的 agent 委托链中，\emph{谁}对某个行为负责可能变得不清晰。如果 Agent A 要求 Agent B 删除一个文件，而 Agent B 照做了，那么谁应承担责任？每次 A2A 交互都必须记录：调用 agent 的身份、任务描述、所使用的授权令牌、时间戳以及结果。该审计追踪对于事件响应、合规性和调试至关重要。
\end{warningbox}


Every A2A server should emit structured audit logs:
每个 A2A 服务器都应发出结构化的审计日志：


\begin{lstlisting}[style=pythonstyle]
@dataclass
class A2AAuditEvent:
    timestamp: str          # ISO 8601
    # ISO 8601
    workflow_id: str        # Correlation ID for the top-level workflow
    # 顶级工作流的相关性 ID
    span_id: str            # This task's span
    # 当前任务的跨度
    parent_span_id: str     # Calling task's span (for delegation chains)
    # 调用任务的跨度（用于委托链）
    caller_agent_id: str    # Verified identity of the calling agent
    # 调用 agent 的已验证身份
    callee_agent_id: str    # This agent's identity
    # 当前 agent 的身份
    task_id: str
    skill_invoked: str
    authorization_scopes: list[str]
    outcome: str            # "completed" | "failed" | "rejected"
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


# -- Data Models --------------------------------------------------------------
# -- 数据模型 --------------------------------------------------------------


class Part(BaseModel):
    type: str           # "text" | "file" | "data"
    # "text" | "file" | "data"
    text: str | None = None
    data: dict | None = None
    mimeType: str | None = None
    uri: str | None = None


class Message(BaseModel):
    role: str           # "user" | "agent"
    # "user" | "agent"
    parts: list[Part]


class TaskStatus(BaseModel):
    state: str          # submitted | working | input-required | completed | failed
    # submitted | working | input-required | completed | failed
    message: str | None = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class Artifact(BaseModel):
    parts: list[Part]
    index: int = 0
    append: bool = False
    lastChunk: bool = True


class Task(BaseModel):
    id: str
    status: TaskStatus
    messages: list[Message] = []
    artifacts: list[Artifact] = []
    metadata: dict = {}


# -- A2A Client (HTTP/REST binding) --------------------------------------------
# -- A2A 客户端（HTTP/REST 绑定） --------------------------------------------
# Note: A2A v1.0 defines three protocol bindings: JSON-RPC 2.0, gRPC, and
# HTTP+JSON/REST. This example uses the REST binding for readability.
# 注意：A2A v1.0 定义了三种协议绑定：JSON-RPC 2.0、gRPC 和
# HTTP+JSON/REST。本示例为了可读性使用了 REST 绑定。


class A2AClient:
    """Client for sending tasks to A2A-compliant agents."""
    """用于向符合 A2A 的 agent 发送任务的客户端。"""

    def __init__(self, agent_url: str, auth_token: str):
        self.agent_url = agent_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

    async def get_agent_card(self) -> dict:
        """Fetch the agent's capability card."""
        """获取 agent 的能力卡。"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.agent_url}/.well-known/agent.json",
                headers=self.headers
            )
            resp.raise_for_status()
            return resp.json()

    async def send_task(self, message: Message,
                        task_id: str | None = None,
                        metadata: dict | None = None) -> Task:
        """Submit a task and return the initial task object."""
        """提交一个任务并返回初始任务对象。"""
        payload = {
            "id": task_id or str(uuid.uuid4()),
            "message": message.model_dump(),
            "metadata": metadata or {}
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.agent_url}/tasks/send",
                json=payload,
                headers=self.headers,
                timeout=30.0
            )
            resp.raise_for_status()
            return Task(**resp.json())

    async def stream_task(self, message: Message,
                          metadata: dict | None = None) -> AsyncIterator[dict]:
        """Submit a task and stream SSE events."""
        """提交一个任务并流式传输 SSE 事件。"""
        payload = {
            "id": str(uuid.uuid4()),
            "message": message.model_dump(),
            "metadata": metadata or {}
        }
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.agent_url}/tasks/sendSubscribe",
                json=payload,
                headers={**self.headers, "Accept": "text/event-stream"},
                timeout=300.0
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        event_data = json.loads(line[6:])
                        yield event_data
                        if event_data.get("final"):
                            break

    async def get_task(self, task_id: str) -> Task:
        """Poll for task status."""
        """轮询任务状态。"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.agent_url}/tasks/{task_id}",
                headers=self.headers
            )
            resp.raise_for_status()
            return Task(**resp.json())

    async def wait_for_completion(self, task: Task,
                                  poll_interval: float = 2.0) -> Task:
        """Poll until task reaches a terminal state."""
        """轮询直到任务达到终止状态。"""
        terminal_states = {"completed", "failed", "canceled"}
        while task.status.state not in terminal_states:
            await asyncio.sleep(poll_interval)
            task = await self.get_task(task.id)
        return task


# -- A2A Server (FastAPI) -----------------------------------------------------
# -- A2A 服务器（FastAPI） -----------------------------------------------------




```

```python
class ResearchAgent:
    """
    A specialist research agent that searches literature and
    summarizes findings on a given topic.
    """

    AGENT_CARD = {
        "name": "ResearchAgent",
        "description": "Searches academic literature and synthesizes research findings.",
        "url": "https://research-agent.example.com/a2a",
        "version": "1.0.0",
        "capabilities": {
            "streaming": True,
            "pushNotifications": False,
            "stateTransitionHistory": True
        },
        "authentication": {"schemes": ["Bearer"]},
        "skills": [{
            "id": "literature-search",
            "name": "Literature Search",
            "description": "Search and summarize academic papers on a topic.",
            "tags": ["research", "literature", "academic", "papers"],
            "examples": [
                "Summarize recent papers on transformer attention mechanisms.",
                "What does the literature say about RLHF for code generation?"
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
                raise HTTPException(status_code=404, detail="Task not found")
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

        # Run asynchronously
        asyncio.create_task(self._execute_task(task_id))
        return task

    async def _execute_task(self, task_id: str):
        task = self.tasks[task_id]
        task.status = TaskStatus(state="working")

        try:
            # Extract the research question from the message
            question = task.messages[0].parts[0].text

            # Simulate literature search (replace with real search tool)
            await asyncio.sleep(1)  # Simulated latency
            findings = await self._search_literature(question)

            # Produce artifact
            task.artifacts = [Artifact(parts=[
                Part(type="text", text=findings["summary"]),
                Part(type="data", data={"papers": findings["papers"],
                                        "query": question})
            ])]
            task.status = TaskStatus(state="completed")

        except Exception as e:
            task.status = TaskStatus(state="failed", message=str(e))

        self.tasks[task_id] = task

    async def _search_literature(self, question: str) -> dict:
        """Placeholder: in production, calls a real search API."""
        return {
            "summary": f"Based on a search of recent literature regarding "
                       f"'{question}', key findings include: ...",
            "papers": [
                {"title": "Attention Is All You Need", "year": 2017,
                 "relevance": 0.95},
                {"title": "RLHF: Training Language Models to Follow Instructions",
                 "year": 2022, "relevance": 0.88}
            ]
        }

    async def _stream_task(self, body: dict) -> AsyncIterator[str]:
        task = await self._create_and_run_task(body)

        # Stream status updates
        yield f"data: {json.dumps({'id': task.id, 'status': {'state': 'submitted'}, 'final': False})}\n\n"
        yield f"data: {json.dumps({'id': task.id, 'status': {'state': 'working'}, 'final': False})}\n\n"

        # Wait for completion
        while task.status.state not in ("completed", "failed", "canceled"):
            await asyncio.sleep(0.5)
            task = self.tasks[task.id]

        # Stream the artifact
        if task.artifacts:
            for part in task.artifacts[0].parts:
                event = {
                    "id": task.id,
                    "artifact": {
                        "parts": [part.model_dump()],
                        "index": 0,
                        "append": False,
                        "lastChunk": True
                    },
                    "final": False
                }
                yield f"data: {json.dumps(event)}\n\n"

        # Final status
        yield f"data: {json.dumps({'id': task.id, 'status': task.status.model_dump(), 'final': True})}\n\n"

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

        # 异步运行
        asyncio.create_task(self._execute_task(task_id))
        return task

    async def _execute_task(self, task_id: str):
        task = self.tasks[task_id]
        task.status = TaskStatus(state="working")

        try:
            # 从消息中提取研究问题
            question = task.messages[0].parts[0].text

            # 模拟文献搜索（用真实搜索工具替换）
            await asyncio.sleep(1)  # 模拟延迟
            findings = await self._search_literature(question)

            # 生成产物
            task.artifacts = [Artifact(parts=[
                Part(type="text", text=findings["summary"]),
                Part(type="data", data={"papers": findings["papers"],
                                        "query": question})
            ])]
            task.status = TaskStatus(state="completed")

        except Exception as e:
            task.status = TaskStatus(state="failed", message=str(e))

        self.tasks[task_id] = task

    async def _search_literature(self, question: str) -> dict:
        """占位符：生产环境中会调用真实的搜索API。"""
        return {
            "summary": f"基于对最近文献的搜索，关于'{question}'的主要发现包括：……",
            "papers": [
                {"title": "Attention Is All You Need", "year": 2017,
                 "relevance": 0.95},
                {"title": "RLHF: Training Language Models to Follow Instructions",
                 "year": 2022, "relevance": 0.88}
            ]
        }

    async def _stream_task(self, body: dict) -> AsyncIterator[str]:
        task = await self._create_and_run_task(body)

        # 流式状态更新
        yield f"data: {json.dumps({'id': task.id, 'status': {'state': 'submitted'}, 'final': False})}\n\n"
        yield f"data: {json.dumps({'id': task.id, 'status': {'state': 'working'}, 'final': False})}\n\n"

        # 等待完成
        while task.status.state not in ("completed", "failed", "canceled"):
            await asyncio.sleep(0.5)
            task = self.tasks[task.id]

        # 流式输出产物
        if task.artifacts:
            for part in task.artifacts[0].parts:
                event = {
                    "id": task.id,
                    "artifact": {
                        "parts": [part.model_dump()],
                        "index": 0,
                        "append": False,
                        "lastChunk": True
                    },
                    "final": False
                }
                yield f"data: {json.dumps(event)}\n\n"

        # 最终状态
        yield f"data: {json.dumps({'id': task.id, 'status': task.status.model_dump(), 'final': True})}\n\n"

# -- 编排器：多智能体工作流 ----------------------------------------
```

## Summary
## 总结

\begin{keybox}[Key Takeaways: Agent-to-Agent Communication]
\begin{enumerate}
  \item \textbf{A2A enables specialization at scale}: By routing tasks to specialist agents, multi-agent systems achieve depth and breadth simultaneously. (Chapter~\ref{sec:multi-agent-systems} covers multi-agent architectures in depth.)
  \item \textbf{Google’s A2A Protocol} provides a production-ready, open standard for interoperable agent communication, with Agent Cards, task lifecycle management, SSE streaming, and enterprise authentication.
  \item \textbf{Communication patterns} range from simple request-response to complex negotiation and auction-based allocation---choose based on task complexity and latency needs.
  \item \textbf{A2A and MCP are complementary}: A2A connects agents to agents; MCP connects agents to tools. Most production systems use both.
  \item \textbf{Security is non-negotiable}: Agent identity verification, authorization scopes, and audit trails are essential in any multi-agent deployment.
  \item \textbf{Coordination protocols} (Contract Net, Blackboard, Consensus) provide structured mechanisms for collective decision-making beyond simple delegation.
  \item \textbf{Observability through correlation IDs} is critical for debugging and auditing complex multi-agent workflows spanning many agents and tools.
\end{enumerate}
\end{keybox}

\begin{keybox}[关键要点：智能体间通信]
\begin{enumerate}
  \item \textbf{A2A 实现大规模专业化}：通过将任务路由到专业智能体，多智能体系统同时获得深度和广度。（第~\ref{sec:multi-agent-systems} 章深入介绍了多智能体架构。）
  \item \textbf{Google 的 A2A 协议} 提供了一个生产就绪的、开放的标准，用于互操作的智能体通信，包含智能体卡片（Agent Cards）、任务生命周期管理、SSE 流式传输和企业级认证。
  \item \textbf{通信模式} 从简单的请求-响应到复杂的协商和基于拍卖的分配——根据任务复杂性和延迟需求进行选择。
  \item \textbf{A2A 和 MCP 是互补的}：A2A 连接智能体到智能体；MCP 连接智能体到工具。大多数生产系统同时使用两者。
  \item \textbf{安全是不可妥协的}：智能体身份验证、授权范围和审计追踪在任何多智能体部署中都是至关重要的。
  \item \textbf{协调协议}（合同网、黑板、共识）提供了超越简单委托的集体决策结构化机制。
  \item \textbf{通过关联 ID 实现可观测性} 对于调试和审计涉及多个智能体和工具的复杂多智能体工作流至关重要。
\end{enumerate}
\end{keybox}

\begin{questionbox}[Open Research Questions in A2A]
\begin{itemize}
  \item How should agents handle \emph{conflicting instructions} from multiple orchestrators in a hierarchy? What conflict resolution mechanisms are most effective?
  \item Can agents \emph{learn} better routing and delegation strategies through experience, rather than relying on static capability declarations?
  \item How do we prevent \emph{prompt injection attacks} where a malicious agent manipulates a downstream agent by embedding adversarial instructions in its messages?
  \item What are the right \emph{privacy boundaries} for context passing---how much conversation history should a sub-agent see, and how do we enforce these boundaries technically?
  \item As agent networks grow to hundreds or thousands of agents, how do we maintain \emph{coherent global state} without creating bottlenecks or consistency violations?
\end{itemize}
\end{questionbox}

\begin{questionbox}[A2A 中的开放研究问题]
\begin{itemize}
  \item 智能体应如何处理来自层级结构中多个编排器的 \emph{冲突指令}？哪些冲突解决机制最有效？
  \item 智能体能否通过经验 \emph{学习} 更好的路由和委托策略，而不是依赖静态能力声明？
  \item 如何防止 \emph{提示注入攻击}（恶意智能体通过在消息中嵌入对抗性指令来操控下游智能体）？
  \item 上下文传递的合适 \emph{隐私边界} 是什么——子智能体应看到多少对话历史，以及如何从技术上强制执行这些边界？
  \item 当智能体网络扩展到数百或数千个智能体时，如何维护 \emph{一致的全局状态} 而不产生瓶颈或一致性违规？
\end{itemize}
\end{questionbox}