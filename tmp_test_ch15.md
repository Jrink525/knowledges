\chapter{Introduction to Agentic AI}
\label{introduction-to-agentic-ai}

## Chapter 15: Introduction to Agentic AI
## 第15章：智能体AI导论

The previous parts equipped us with the algorithmic toolkit---how to train, align, and reason with LLMs. We covered transformer architectures and GPU systems (Part I), the reinforcement learning methods that align models with human intent (Part II), the reasoning capabilities that emerge from RL training (Part III), and evaluation methodology (Part IV). This part turns to the central question of modern AI engineering: how do we \emph{deploy} these models as autonomous agents that perceive, plan, act, and learn in open-ended environments?

前面的部分为我们提供了算法工具包——如何训练、对齐和推理大型语言模型（LLM）。我们涵盖了Transformer架构和GPU系统（第一部分）、将模型与人类意图对齐的强化学习方法（第二部分）、从RL训练中涌现的推理能力（第三部分）以及评估方法论（第四部分）。本部分转向现代AI工程的核心问题：我们如何将这些模型部署为能够在开放环境中感知、规划、行动和学习的自主智能体？

An \textbf{agentic AI system} is one where an LLM operates in a loop: it receives observations from an environment (user messages, tool outputs, sensor data), reasons about what to do next, takes actions (tool calls, code execution, API requests), and iterates until a goal is achieved or it explicitly asks for human input. This contrasts with the ``single-turn chatbot'' paradigm where the model produces one response and waits.

一个\textbf{智能体AI系统（agentic AI system）}是指LLM在一个循环中运行：它从环境中接收观察（用户消息、工具输出、传感器数据），推理下一步该做什么，采取行动（工具调用、代码执行、API请求），并迭代直到目标达成或明确请求人类输入。这与“单轮聊天机器人”范式形成对比，后者中模型生成一次响应后就等待。

The shift from chatbot to agent introduces several fundamental challenges that a single model call cannot address:

从聊天机器人到智能体的转变带来了几个单一模型调用无法解决的根本性挑战：

\begin{itemize}
  \item \textbf{Persistence}: An agent must remember what it has done, what failed, and what context was established---across turns, sessions, and even days.
  \item \textbf{持久性（Persistence）}：智能体必须记住它做过什么、什么失败了、以及建立了什么上下文——跨越轮次、会话甚至数天。
  \item \textbf{Grounding}: The agent must access up-to-date, domain-specific knowledge that was not present in its training data.
  \item \textbf{接地（Grounding）}：智能体必须访问训练数据中不存在的最新、特定领域知识。
  \item \textbf{Action}: The agent must interact with external systems---databases, APIs, file systems, browsers---through well-defined interfaces.
  \item \textbf{行动（Action）}：智能体必须通过定义良好的接口与外部系统（数据库、API、文件系统、浏览器）交互。
  \item \textbf{Coordination}: Complex tasks often exceed what a single agent can handle; multiple specialized agents must collaborate, delegate, and negotiate.
  \item \textbf{协调（Coordination）}：复杂任务往往超出单个智能体的处理能力；多个专用智能体必须协作、委派和协商。
  \item \textbf{Safety}: Autonomous action requires guardrails, human oversight, and graceful degradation when the agent is uncertain.
  \item \textbf{安全性（Safety）}：自主行动需要护栏、人类监督，以及在智能体不确定时的优雅降级。
\end{itemize}

To address these challenges, production agentic systems are built as a layered architecture. Each layer solves a specific problem, and the chapters that follow cover the full stack from bottom to top:

为了应对这些挑战，生产级智能体系统被构建为分层架构。每一层解决一个特定问题，后续章节将从下到上覆盖整个栈：

\begin{itemize}
  \item \textbf{Chapter 16: RAG (Retrieval-Augmented Generation)} --- The knowledge layer. RAG gives agents access to dynamic external knowledge by retrieving relevant documents at query time. This solves the grounding problem: agents can answer questions about proprietary data, recent events, or domain-specific content that the model never saw during training. We cover embedding models, vector databases, chunking strategies, hybrid retrieval, and advanced patterns like agentic RAG where the agent decides \emph{when} and \emph{what} to retrieve.
  \item \textbf{第16章：RAG（检索增强生成）} —— 知识层。RAG通过查询时检索相关文档，为智能体提供动态外部知识的访问。这解决了接地问题：智能体可以回答关于专有数据、近期事件或模型在训练中从未见过的领域特定内容的问题。我们涵盖嵌入模型、向量数据库、分块策略、混合检索以及高级模式（如智能体RAG，其中智能体决定\emph{何时}以及\emph{什么}需要检索）。
  \item \textbf{Chapter 17: Memory} --- The persistence layer. Memory enables agents to recall information across interactions---from short-term working memory within a single task, to long-term episodic memory spanning months. We cover memory architectures (buffer, summary, vector-indexed, knowledge graphs), memory consolidation, and how to design memory systems that scale without drowning the context window.
  \item \textbf{第17章：记忆（Memory）} —— 持久层。记忆使智能体能够跨交互回忆信息——从单个任务内的短期工作记忆，到跨越数月的情景记忆。我们涵盖记忆架构（缓冲区、摘要、向量索引、知识图谱）、记忆巩固（memory consolidation），以及如何设计可扩展而不淹没上下文窗口的记忆系统。
  \item \textbf{Chapter 18: Harness \& Orchestration} --- The runtime layer. The orchestration harness is the ``operating system'' for agents: it manages the agent loop, context window budget, tool dispatch, error recovery, state persistence, and observability. We cover context management strategies (summarization, sliding window, hierarchical), execution control (sequential, parallel, branching), guardrails, and human-in-the-loop patterns.
  \item \textbf{第18章：框架与编排（Harness \& Orchestration）} —— 运行时层。编排框架是智能体的“操作系统”：它管理智能体循环、上下文窗口预算、工具调度、错误恢复、状态持久化和可观测性。我们涵盖上下文管理策略（摘要、滑动窗口、分层）、执行控制（顺序、并行、分支）、护栏以及人在回路模式。
  \item \textbf{Chapter 19: Design Patterns} --- The architecture layer. Canonical patterns for structuring agents: ReAct (reason + act interleaving), plan-then-execute, reflection loops, tool-augmented generation, and multi-step workflows. We analyze when each pattern applies, their failure modes, and how to combine them for complex real-world tasks.
  \item \textbf{第19章：设计模式（Design Patterns）} —— 架构层。构建智能体的经典模式：ReAct（推理与行动交织）、先计划后执行、反思循环、工具增强生成以及多步骤工作流。我们分析每种模式的适用场景、失败模式，以及如何将它们组合以应对复杂的现实任务。
  \item \textbf{Chapter 20: Environments \& Benchmarks} --- The evaluation layer. Where and how to evaluate agentic behaviour. We cover web navigation benchmarks, coding environments, tool-use evaluation suites, and the unique challenges of evaluating multi-step autonomous systems (partial credit, trajectory quality, safety violations).
  \item \textbf{第20章：环境与基准（Environments \& Benchmarks）} —— 评估层。在哪里以及如何评估智能体行为。我们涵盖网页导航基准、编码环境、工具使用评估套件，以及评估多步自主系统的独特挑战（部分得分、轨迹质量、安全违规）。
  \item \textbf{Chapter 21: MCP (Model Context Protocol)} --- The tool integration standard. MCP standardizes how agents discover and invoke tools---analogous to USB for hardware. We cover the protocol specification, server/client architecture, resource management, and how MCP eliminates the N$\times$M integration problem between agents and tools.
  \item \textbf{第21章：MCP（模型上下文协议）} —— 工具集成标准。MCP标准化了智能体发现和调用工具的方式——类似于USB对于硬件的作用。我们涵盖协议规范、服务器/客户端架构、资源管理，以及MCP如何消除智能体与工具之间的N$\times$M集成问题。
  \item \textbf{Chapter 22: Agent Skills} --- The capability layer. How agents acquire and compose specialized capabilities beyond basic tool use, including skill libraries, skill selection, and compositional task solving.
  \item \textbf{第22章：智能体技能（Agent Skills）} —— 能力层。智能体如何获取和组合超越基本工具使用的专门能力，包括技能库、技能选择和组合式任务求解。
  \item \textbf{Chapter 23: A2A (Agent-to-Agent Communication)} --- The inter-agent protocol. When tasks require multiple specialists, A2A provides a standardized protocol for agent discovery, task delegation, progress streaming, and result aggregation---enabling heterogeneous agents (from different vendors, frameworks, or organizations) to collaborate.
  \item \textbf{第23章：A2A（智能体间通信）} —— 智能体间协议。当任务需要多个专家时，A2A提供了智能体发现、任务委派、进度流和结果聚合的标准化协议——使异构智能体（来自不同供应商、框架或组织）能够协作。
  \item \textbf{Chapter 24: Multi-Agent Systems} --- The coordination layer. Architectures for multi-agent collaboration: hierarchical delegation, peer-to-peer negotiation, debate and consensus, swarm intelligence, and emergent behaviour. We cover when to use single-agent vs. multi-agent designs and how to debug coordination failures.
  \item \textbf{第24章：多智能体系统（Multi-Agent Systems）} —— 协调层。多智能体协作的架构：层级委派、点对点协商、辩论与共识、群体智能以及涌现行为。我们涵盖何时使用单智能体与多智能体设计，以及如何调试协调失败。
  \item \textbf{Chapter 25: Frameworks} --- The implementation layer. Production toolkits that implement the above concepts: LangGraph (stateful graph-based orchestration), CrewAI (role-based multi-agent), OpenAI Agents SDK, AutoGen, and others. We compare their trade-offs, architecture decisions, and suitability for different use cases.
  \item \textbf{第25章：框架（Frameworks）} —— 实现层。实现上述概念的生产级工具包：LangGraph（基于有状态图的编排）、CrewAI（基于角色的多智能体）、OpenAI Agents SDK、AutoGen等。我们比较它们的权衡、架构决策以及对不同用例的适用性。
  \item \textbf{Chapter 26: Agentic UI} --- The interaction layer. How users interact with and supervise agents: streaming interfaces, progressive disclosure, approval workflows, status dashboards, and the UX patterns that build appropriate trust in autonomous systems.
  \item \textbf{第26章：智能体UI（Agentic UI）} —— 交互层。用户如何与智能体交互并监督它们：流式界面、渐进式披露、审批工作流、状态仪表板，以及在自主系统中建立适当信任的UX模式。
\end{itemize}

These layers do not operate in isolation---they form a tightly integrated system where each component depends on and enhances the others:

这些层并非孤立运作——它们构成了一个紧密集成的系统，其中每个组件都依赖并增强其他组件：

\begin{itemize}
  \item The \textbf{agent core} (an LLM with reasoning capabilities from Parts II--III) sits at the center, executing a perceive--reason--act loop.
  \item \textbf{智能体核心（agent core）}（一个具备第二部分至第三部分推理能力的LLM）位于中心，执行感知-推理-行动循环。
  \item \textbf{RAG} feeds the agent with relevant knowledge before each reasoning step, while \textbf{Memory} provides continuity across steps and sessions.
  \item \textbf{RAG}在每个推理步骤之前为智能体提供相关知识，而\textbf{记忆（Memory）}则提供跨步骤和会话的连续性。
  \item The \textbf{Orchestration Harness} coordinates everything: it decides when to retrieve, when to call tools, when to delegate to sub-agents, and when to ask the human for guidance.
  \item \textbf{编排框架（Orchestration Harness）}协调一切：它决定何时检索、何时调用工具、何时委派给子智能体，以及何时向人类请求指导。
  \item \textbf{MCP} provides the standardized interface through which the agent accesses all external tools, and \textbf{A2A} provides the equivalent interface for inter-agent communication.
  \item \textbf{MCP}提供了智能体访问所有外部工具的标准接口，而\textbf{A2A}则提供了智能体间通信的等效接口。
  \item \textbf{Design Patterns} define the high-level strategy (ReAct, plan-and-execute, reflection), while \textbf{Frameworks} provide the concrete implementation of these patterns.
  \item \textbf{设计模式（Design Patterns）}定义了高层策略（ReAct、计划与执行、反思），而\textbf{框架（Frameworks）}则提供了这些模式的具体实现。
  \item The \textbf{UI layer} closes the loop by connecting the agent back to the human---for oversight, correction, and collaborative problem-solving.
  \item \textbf{UI层}通过将智能体与人类连接起来来闭合循环——用于监督、纠正和协作解决问题。
\end{itemize}

Throughout, we maintain the systems perspective: agentic AI is not just about prompting---it requires careful engineering of context management, error handling, safety guardrails, and observability at every layer. The figure below shows how these components fit together architecturally.

贯穿始终，我们保持系统视角：智能体AI不仅仅是提示工程——它需要在每一层对上下文管理、错误处理、安全护栏和可观测性进行精心设计。下图展示了这些组件在架构上如何组合在一起。

\begin{figure}[ht]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_049_agentic-stack.png}
\caption{The Agentic AI architecture stack. The \textbf{Agent Core} executes a perceive--reason--act loop, coordinated by the \textbf{Harness \& Orchestration} layer which manages context, state, guardrails, and observability. The agent interacts downward with \textbf{External Systems}---RAG for knowledge retrieval, Memory for persistence, Tools via MCP, and other Agents via A2A---all grounded in an \textbf{Environment}. The \textbf{User} provides goals, feedback, and oversight from above. Arrows indicate bidirectional data flow; the blue loop arrows show the iterative agentic cycle.}
\caption{Agentic AI 架构栈。\textbf{Agent Core (智能体核心)} 执行感知--推理--行动循环，由 \textbf{Harness \& Orchestration (编排层)} 层协调，该层管理上下文、状态、护栏和可观测性。智能体向下与 \textbf{External Systems (外部系统)} 交互——通过 \textbf{RAG (检索增强生成)} 进行知识检索，通过 \textbf{Memory (记忆)} 实现持久化，通过 \textbf{MCP (模型上下文协议)} 使用工具，以及通过 \textbf{A2A (智能体到智能体)} 与其他智能体通信——所有这些都基于 \textbf{Environment (环境)}。\textbf{User (用户)} 从上方提供目标、反馈和监督。箭头表示双向数据流；蓝色循环箭头表示迭代的智能体循环。}
\label{fig:agentic-stack}
\end{figure}