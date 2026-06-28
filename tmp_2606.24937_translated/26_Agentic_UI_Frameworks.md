## Agentic UI Frameworks
## 代理式用户界面框架

\label{sec:agentic-ui}

As large language models transition from passive text generators to active agents capable of planning, tool use, and multi-step reasoning, the interfaces through which humans interact with them must evolve in parallel. Traditional chat interfaces---designed for single-turn or short-context conversations---are ill-suited to the demands of agentic workflows: long-running tasks, branching decision trees, parallel tool invocations, and the need for meaningful human oversight. This section surveys the landscape of \emph{agentic UI frameworks}: the design paradigms, component libraries, and implementation patterns that enable rich, transparent, and trustworthy human-agent collaboration.

随着大型语言模型从被动的文本生成器转变为能够进行规划、使用工具和多步推理的主动代理（agent），人类与它们交互的界面必须同步进化。传统的聊天界面——专为单轮或短上下文对话设计——无法满足代理式工作流（agentic workflows）的需求：长时间运行的任务、分支决策树、并行工具调用以及有意义的人类监督需求。本节概述了*代理式用户界面框架（agentic UI frameworks）*的领域：这些设计范式、组件库和实现模式，能够实现丰富、透明且可信赖的人机协作。

\section{Motivation: Beyond the Chat Box}
\label{subsec:ui-motivation}

## Motivation: Beyond the Chat Box
## 动机：超越聊天框

\label{subsec:ui-motivation}

\begin{intuitionbox}[Why Agents Need Specialized Interfaces]
A chat bubble conveys a \emph{result}. An agentic UI conveys a \emph{process}---the reasoning, the tools invoked, the decisions made, and the points where human judgment is required. Without this visibility, users cannot trust, correct, or learn from the agent.
\end{intuitionbox}

\begin{intuitionbox}[为什么代理需要专门的界面]
聊天气泡传递的是*结果*。代理式用户界面传递的是*过程*——推理、调用的工具、做出的决策以及需要人类判断的节点。没有这种可见性，用户就无法信任、纠正或从代理中学习。
\end{intuitionbox}

The gap between a chat interface and an agentic interface mirrors the gap between a vending machine and a skilled collaborator. When an agent executes a 20-step research task, browses the web, writes and runs code, and synthesizes a report, the user needs answers to questions that a simple text response cannot provide:

聊天界面与代理式界面之间的差距，类似于自动售货机与熟练协作者之间的差距。当代理执行一个包含20步的研究任务、浏览网页、编写并运行代码、综合生成报告时，用户需要回答简单文本回复无法提供的问题：

\begin{itemize}
  \item \textbf{What is the agent doing right now?} Long-running tasks require progress feedback; silence breeds distrust.
  \item \textbf{Why did the agent make this decision?} Transparency into reasoning enables users to catch errors early.
  \item \textbf{Which tools were used, and with what inputs?} Tool provenance is essential for verifying factual claims and auditing behavior.
  \item \textbf{Where should I intervene?} Agents must surface decision points that warrant human judgment without overwhelming users with every micro-decision.
  \item \textbf{Can I undo this?} Irreversible actions (sending emails, modifying files, executing code) require explicit confirmation and rollback paths.
\end{itemize}

\begin{itemize}
  \item \textbf{代理当前在做什么？}长时间运行的任务需要进度反馈；沉默会滋生不信任。
  \item \textbf{代理为什么做出这个决定？}推理过程的透明性使用户能够及早发现错误。
  \item \textbf{使用了哪些工具？输入了什么？}工具溯源（tool provenance）对于验证事实声明和审计行为至关重要。
  \item \textbf{我应该在何处干预？}代理必须呈现值得人类判断的决策点，而不让用户被每个微决策淹没。
  \item \textbf{我能撤销这个操作吗？}不可逆操作（如发送邮件、修改文件、执行代码）需要明确的确认和回滚路径。
\end{itemize}

\begin{warningbox}[The Automation Bias Risk]
Research on human-automation interaction consistently shows that users over-trust automated systems, especially when those systems present outputs confidently and without uncertainty signals~\cite{parasuraman1997humans}. Agentic UIs must actively counteract automation bias by surfacing uncertainty, showing reasoning, and making it easy to question or override agent decisions.
\end{warningbox}

\begin{warningbox}[自动化偏差风险]
人机交互研究一致表明，用户过度信任自动化系统，尤其是当这些系统自信地呈现输出且不包含不确定性信号时~\cite{parasuraman1997humans}。代理式用户界面必须通过揭示不确定性、展示推理过程、并让质疑或覆盖代理决策变得容易，来主动对抗自动化偏差（automation bias）。
\end{warningbox}

The design of agentic UIs thus sits at the intersection of human-computer interaction (HCI), explainable AI (XAI), and software engineering. The core design goals are:

因此，代理式用户界面的设计处于人机交互（HCI）、可解释人工智能（XAI）和软件工程的交叉点。核心设计目标是：

\begin{enumerate}
  \item \textbf{Transparency}: Make the agent’s internal state legible to the user.
  \item \textbf{Control}: Provide meaningful intervention points without requiring constant supervision.
  \item \textbf{Trust Calibration}: Help users develop accurate mental models of agent capabilities and limitations.
  \item \textbf{Efficiency}: Minimize cognitive load; surface the right information at the right time.
  \item \textbf{Recoverability}: Make mistakes cheap to detect and reverse.
\end{enumerate}

\begin{enumerate}
  \item \textbf{透明性（Transparency）}：让代理的内部状态对用户可读。
  \item \textbf{可控性（Control）}：提供有意义的干预点，而不需要持续监督。
  \item \textbf{信任校准（Trust Calibration）}：帮助用户建立关于代理能力与局限的准确心理模型。
  \item \textbf{效率（Efficiency）}：最小化认知负荷；在正确的时间呈现正确的信息。
  \item \textbf{可恢复性（Recoverability）}：让错误易于发现和逆转。
\end{enumerate}

\section{UI Paradigms for Agents}
\label{subsec:ui-paradigms}

## UI Paradigms for Agents
## 代理的用户界面范式

\label{subsec:ui-paradigms}

No single UI paradigm suits all agentic use cases. The appropriate interface depends on task duration, required human involvement, output type, and user expertise. The spectrum ranges from fully conversational chat interfaces to fully autonomous dashboards with minimal human interaction.

没有任何一种用户界面范式适合所有代理式用例。合适的界面取决于任务持续时间、所需的人类参与程度、输出类型以及用户专业知识。其范围涵盖从完全对话式的聊天界面到几乎无需人工交互的完全自主仪表板。

\subsection{Chat-Based Interfaces}
\label{chat-based-interfaces}

### Chat-Based Interfaces
### 基于聊天的界面

\label{chat-based-interfaces}

The chat paradigm---message bubbles, a text input, and a scrolling history---remains the most familiar entry point for LLM interaction. Its strengths are low learning curve and natural language flexibility. For agentic use, chat interfaces are augmented with:

聊天范式——消息气泡、文本输入框和滚动历史记录——仍然是与LLM交互最熟悉的入口。其优势在于低学习曲线和自然语言的灵活性。对于代理式用途，聊天界面通过以下方式增强：

\begin{itemize}
  \item \textbf{Streaming responses}: Tokens appear as they are generated, providing immediate feedback and reducing perceived latency. Implemented via Server-Sent Events (SSE) or WebSockets.
  \item \textbf{Inline tool indicators}: Small badges or expandable sections within the message stream show when a tool was called (e.g., ``\texttt{[Searched the web for: climate change 2024]}'').
  \item \textbf{Typing indicators and status messages}: ``Agent is thinking\ldots{}'', ``Running Python code\ldots{}'', ``Fetching results\ldots{}'' keep users informed during latency gaps.
  \item \textbf{Message threading}: For multi-turn agentic tasks, collapsible sub-threads can contain intermediate steps without cluttering the main conversation.
\end{itemize}

\begin{itemize}
  \item \textbf{流式响应（Streaming responses）}：标记在生成时立即出现，提供即时反馈并降低感知延迟。通过服务器推送事件（Server-Sent Events, SSE）或WebSockets实现。
  \item \textbf{内联工具指示器（Inline tool indicators）}：消息流中的小型徽章或可展开区域显示何时调用了工具（例如：``\texttt{[在网络上搜索：气候变化 2024]}''）。
  \item \textbf{打字指示器和状态消息（Typing indicators and status messages）}：``代理正在思考\ldots{}''、``正在运行Python代码\ldots{}''、``正在获取结果\ldots{}''让用户在延迟间隙保持知情。
  \item \textbf{消息线程（Message threading）}：对于多轮代理式任务，可折叠的子线程可以包含中间步骤，而不会使主对话变得杂乱。
\end{itemize}

\begin{keybox}[Chat UI Limitations for Agents]
Chat interfaces serialize inherently parallel processes. When an agent fans out to five tools simultaneously, a linear message stream misrepresents the actual execution graph. For complex agentic workflows, chat should be augmented with---or replaced by---richer paradigms.
\end{keybox}

\begin{keybox}[聊天界面用于代理的局限性]
聊天界面将原本并行的过程序列化。当代理同时分发给五个工具时，线性的消息流会歪曲实际的执行图。对于复杂的代理式工作流，聊天应被更丰富的范式增强或取代。
\end{keybox}

\subsection{Canvas and Artifact-Based Interfaces}
\label{canvas-and-artifact-based-interfaces}

### Canvas and Artifact-Based Interfaces
### 画布与工件界面

\label{canvas-and-artifact-based-interfaces}

The canvas paradigm, popularized by Claude Artifacts\textsuperscript{1} and ChatGPT Canvas\textsuperscript{2}, introduces a \emph{split-pane} layout: the left pane hosts the conversation, while the right pane (the ``canvas'' or ``artifact panel'') displays generated content---code, documents, diagrams, spreadsheets---as a live, editable artifact.

画布范式由Claude Artifacts\textsuperscript{1}和ChatGPT Canvas\textsuperscript{2}推广，引入了*分栏*布局：左侧栏承载对话，右侧栏（“画布”或“工件面板”）将生成的内容——代码、文档、图表、电子表格——显示为实时可编辑的工件（artifact）。

Key characteristics:

关键特性：

\begin{itemize}
  \item \textbf{Persistent artifacts}: Generated content persists across turns and can be iteratively refined through natural language instructions (``make the chart blue'', ``add error handling to the function'').
  \item \textbf{In-place editing}: Users can directly edit the artifact, and the agent can observe and respond to those edits.
  \item \textbf{Version history}: Artifacts maintain a revision history, enabling rollback to any prior state.
  \item \textbf{Multi-artifact workspaces}: Advanced implementations support multiple simultaneous artifacts (e.g., a code file, its test suite, and a documentation page).
\end{itemize}

\begin{itemize}
  \item \textbf{持久化工件（Persistent artifacts）}：生成的内容跨轮次持久存在，并可通过自然语言指令（“把图表变蓝”、“给函数添加错误处理”）进行迭代优化。
  \item \textbf{原地编辑（In-place editing）}：用户可以直接编辑工件，代理可以观察并响应这些编辑。
  \item \textbf{版本历史（Version history）}：工件维护修订历史，允许回滚到任何先前状态。
  \item \textbf{多工件工作区（Multi-artifact workspaces）}：高级实现支持同时处理多个工件（例如，一个代码文件、其测试套件和一个文档页面）。
\end{itemize}

The canvas paradigm is particularly well-suited to \emph{co-creation} tasks: writing, coding, data analysis, and design, where the output is a document or artifact rather than a conversational answer.

画布范式特别适合*共同创作（co-creation）*任务：写作、编码、数据分析和设计，在这些任务中，输出是一个文档或工件，而不是对话式答案。

\subsection{Workflow Visualization}
\label{workflow-visualization}

### Workflow Visualization
### 工作流可视化

\label{workflow-visualization}

For agents that execute structured plans---sequences or graphs of steps---workflow visualization UIs make the plan explicit and trackable. This paradigm is common in:

对于执行结构化计划（步骤序列或图）的代理，工作流可视化界面使计划明确且可追踪。该范式常见于：

\begin{itemize}
  \item \textbf{Agentic pipelines} (LangGraph, AutoGen, CrewAI): The agent’s execution graph is rendered as a directed acyclic graph (DAG) or flowchart, with nodes representing steps and edges representing data flow or control flow.
  \item \textbf{Task decomposition views}: The agent’s high-level plan is shown as a checklist or Gantt-style timeline, with each sub-task expanding to reveal its own steps.
  \item \textbf{Live progress tracking}: Nodes change color or display spinners as they execute; completed nodes show outputs; failed nodes show error details.
\end{itemize}

\begin{itemize}
  \item \textbf{代理式流水线（Agentic pipelines）}（LangGraph, AutoGen, CrewAI）：代理的执行图被渲染为有向无环图（DAG）或流程图，节点表示步骤，边表示数据流或控制流。
  \item \textbf{任务分解视图（Task decomposition views）}：代理的高级计划显示为检查清单或甘特图风格的时间线，每个子任务可展开以显示其自己的步骤。
  \item \textbf{实时进度跟踪（Live progress tracking）}：节点在执行时改变颜色或显示旋转图标；完成的节点显示输出；失败的节点显示错误详情。
\end{itemize}

LangGraph Studio\textsuperscript{3} is the canonical example of this paradigm, providing a graph-based debugger and visualizer for LangGraph agents. Users can inspect the state at each node, replay executions, and inject modified state to test alternative paths.

LangGraph Studio\textsuperscript{3} 是该范式的典型例子，为LangGraph代理提供基于图的调试器和可视化工具。用户可以检查每个节点的状态、重放执行过程，并注入修改后的状态以测试替代路径。

\subsection{Dashboard and Monitoring Interfaces}
\label{dashboard-and-monitoring-interfaces}

### Dashboard and Monitoring Interfaces
### 仪表板与监控界面

\label{dashboard-and-monitoring-interfaces}

For long-running or production agents, dashboard UIs provide an operational view:

对于长时间运行或生产环境的代理，仪表板界面提供操作视图：

```markdown
\begin{itemize}
  \item \textbf{Real-time status}: Which agents are running, idle, or failed; current task and step.
  \item \textbf{实时状态}：哪些代理正在运行、空闲或失败；当前任务和步骤。

  \item \textbf{Resource metrics}: Token consumption, API call counts, latency histograms, cost estimates.
  \item \textbf{资源指标}：Token消耗、API调用次数、延迟直方图、成本估算。

  \item \textbf{Queue management}: Pending tasks, priority ordering, rate limit status.
  \item \textbf{队列管理}：待处理任务、优先级排序、速率限制状态。

  \item \textbf{Alert and anomaly detection}: Unusual behavior (excessive retries, cost spikes, repeated failures) surfaced as notifications.
  \item \textbf{告警与异常检测}：异常行为（过度重试、成本激增、反复失败）以通知形式呈现。

  \item \textbf{Historical analytics}: Task completion rates, average duration, error frequency over time.
  \item \textbf{历史分析}：任务完成率、平均持续时间、随时间变化的错误频率。
\end{itemize}

Dashboard UIs are typically built with tools like Grafana,4 custom React dashboards, or Streamlit, and are aimed at \emph{operators} rather than end users.
仪表盘UI通常使用Grafana\^{4}、自定义React仪表盘或Streamlit等工具构建，面向的是\emph{运维人员}而非最终用户。

\subsection{Collaborative Interfaces}
\label{collaborative-interfaces}
## Collaborative Interfaces
## 协作界面

Collaborative UIs treat the agent as a peer contributor to a shared workspace---a document, codebase, or design canvas---alongside human collaborators. Key features include:
协作式UI将代理视为与人类协作者同等的贡献者，共同参与共享工作空间——文档、代码库或设计画布。主要特性包括：

\begin{itemize}
  \item \textbf{Presence indicators}: The agent appears as a named cursor or avatar in the shared workspace.
  \item \textbf{存在指示器}：代理在共享工作区中以命名光标或头像形式出现。

  \item \textbf{Change attribution}: Edits made by the agent are visually distinguished from human edits (e.g., color-coded diffs).
  \item \textbf{变更归属}：代理所做的编辑在视觉上与人类编辑区分开（例如，颜色编码的差异对比）。

  \item \textbf{Inline suggestions}: The agent proposes changes as tracked edits or comments, which humans can accept, reject, or modify.
  \item \textbf{内联建议}：代理以修订或评论形式提出更改，人类可接受、拒绝或修改。

  \item \textbf{Conflict resolution}: When the agent and a human edit the same region simultaneously, the UI surfaces the conflict and facilitates resolution.
  \item \textbf{冲突解决}：当代理和人类同时编辑同一区域时，UI会显示冲突并促进解决。
\end{itemize}

This paradigm is emerging in tools like Cursor5 (collaborative code editing with AI), Notion AI,6 and Google Docs with Gemini integration.7
这种范式正在Cursor\^{5}（AI协作代码编辑）、Notion AI\^{6}以及集成Gemini的Google Docs\^{7}等工具中兴起。

\subsection{Autonomous with Checkpoints}
\label{autonomous-with-checkpoints}
## Autonomous with Checkpoints
## 带检查点的自主模式

At the far end of the autonomy spectrum, some agents run largely independently---browsing the web, writing code, executing commands---and surface only at predefined \emph{checkpoints} requiring human approval. This paradigm is used in:
在自主谱系的另一端，某些代理在很大程度上独立运行——浏览网页、编写代码、执行命令——仅在需要人工批准的预定义\emph{检查点}才呈现给用户。这种范式用于：

\begin{itemize}
  \item \textbf{Computer-use agents} (Anthropic Computer Use,8 OpenAI Operator9): The agent controls a browser or desktop; the UI shows a live screen feed and pauses for approval before irreversible actions.
  \item \textbf{计算机使用代理}（Anthropic Computer Use\^{8}、OpenAI Operator\^{9}）：代理控制浏览器或桌面；UI显示实时屏幕画面，并在执行不可逆操作前暂停等待批准。

  \item \textbf{Automated pipelines with gates}: CI/CD-style workflows where the agent completes a phase and waits for a human ``merge'' before proceeding.
  \item \textbf{带门控的自动化流水线}：CI/CD风格的工作流，代理完成一个阶段后等待人工“合并”再继续。

  \item \textbf{Scheduled agents}: Agents that run on a schedule and report results asynchronously, with a notification-based UI for reviewing outputs and approving follow-on actions.
  \item \textbf{定时代理}：按计划运行并异步报告结果的代理，通过基于通知的UI审查输出并批准后续操作。
\end{itemize}

\begin{examplebox}[Checkpoint UI in Practice]
An agent tasked with ``clean up my email inbox'' might autonomously categorize and archive 500 emails, then pause and present a summary: ``I found 23 emails that appear to be from mailing lists you haven’t opened in 6 months. Shall I unsubscribe from all, some, or none?'' The user reviews a list, makes selections, and the agent proceeds. This pattern---autonomous execution punctuated by human decision points---balances efficiency with control.
\begin{examplebox}[实践中的检查点UI]
一个被赋予“清理我的电子邮件收件箱”任务的代理可能会自主分类并归档500封邮件，然后暂停并呈现摘要：“我发现了23封看似来自你已有6个月未打开的邮件列表的邮件。是否要退订全部、部分或都不退订？”用户查看列表、做出选择，代理继续执行。这种模式——自主执行中穿插人类决策点——平衡了效率与控制。
\end{examplebox}

\section{Key UI Components for Agents}
\label{subsec:ui-components}
## Key UI Components for Agents
## 代理的关键UI组件

Regardless of the overarching paradigm, agentic UIs share a set of recurring components. This section catalogs the most important, with design guidance for each.
无论采用何种总体范式，代理型UI都共享一组反复出现的组件。本节列出最重要的组件，并提供针对每个组件的设计指导。

\subsection{Thought and Reasoning Display}
\label{thought-and-reasoning-display}
## Thought and Reasoning Display
## 思维与推理展示

Modern LLMs, particularly those trained with chain-of-thought or extended thinking (e.g., OpenAI o1/o3, Anthropic Claude with extended thinking), generate substantial internal reasoning before producing a final response. Surfacing this reasoning is a double-edged sword: it increases transparency but can overwhelm users with verbose internal monologue.
现代大语言模型（LLM），尤其是经过思维链（chain-of-thought）或扩展思考（extended thinking）训练的模型（如OpenAI o1/o3、具有扩展思考能力的Anthropic Claude），在生成最终回复之前会进行大量的内部推理。展示这种推理是一把双刃剑：它提高了透明度，但冗长的内心独白可能会让用户不知所措。

Best practices:
最佳实践：

\begin{itemize}
  \item \textbf{Collapsible reasoning blocks}: Show a summary (``Thought for 12 seconds'') with an expand toggle for users who want details.
  \item \textbf{可折叠的推理块}：显示摘要（“思考了12秒”），并带有展开按钮供需要细节的用户查看。

  \item \textbf{Progressive disclosure}: Show only the final conclusion by default; reasoning is available on demand.
  \item \textbf{渐进式披露}：默认只显示最终结论；推理内容按需提供。

  \item \textbf{Structured reasoning}: If the model produces structured thoughts (hypotheses, evidence, conclusions), render them with visual hierarchy rather than as a wall of text.
  \item \textbf{结构化推理}：如果模型生成结构化思考（假设、证据、结论），应以视觉层次呈现，而非文本堆砌。

  \item \textbf{Reasoning vs.~response distinction}: Clearly visually distinguish internal reasoning (which may contain errors or false starts) from the final response.
  \item \textbf{推理与回复的区分}：在视觉上清晰地区分内部推理（可能包含错误或错误起点）与最终回复。
\end{itemize}

\subsection{Tool Use Visualization}
\label{tool-use-visualization}
## Tool Use Visualization
## 工具使用可视化

Tool calls are the primary mechanism by which agents interact with the world. Visualizing them is essential for trust and debugging.
工具调用是代理与世界交互的主要机制。将其可视化对于建立信任和调试至关重要。

\begin{keybox}[Tool Call Anatomy]
Each tool invocation has four components worth displaying: (1) the \textbf{tool name} and icon, (2) the \textbf{input arguments} (potentially large JSON), (3) the \textbf{output/result} (potentially large), and (4) \textbf{timing} (latency). The UI must balance completeness with readability.
\begin{keybox}[工具调用解剖]
每次工具调用有四个值得显示的组成部分：(1) \textbf{工具名称}和图标，(2) \textbf{输入参数}（可能为大型JSON），(3) \textbf{输出/结果}（可能很大），(4) \textbf{时序}（延迟）。UI必须在完整性与可读性之间取得平衡。
\end{keybox}

Design patterns for tool visualization:
工具可视化的设计模式：

\begin{itemize}
  \item \textbf{Inline tool cards}: Compact cards within the message stream showing tool name, a one-line summary of inputs, and status (running/success/error). Expandable for full details.
  \item \textbf{内联工具卡片}：消息流中的紧凑卡片，显示工具名称、输入的一行摘要及状态（运行中/成功/错误）。可展开查看完整详情。

  \item \textbf{Tool timeline}: A horizontal timeline showing all tool calls in a turn, with durations, enabling identification of bottlenecks.
  \item \textbf{工具时间线}：水平时间线显示单轮中所有工具调用及其耗时，便于识别瓶颈。

  \item \textbf{Input/output diff}: For tools that modify state (e.g., file editing), show a before/after diff.
  \item \textbf{输入/输出差异}：对于修改状态的工具（如文件编辑），显示修改前后的差异。

  \item \textbf{Tool icons and branding}: Recognizable icons for common tools (web search, code execution, file system, APIs) enable rapid scanning.
  \item \textbf{工具图标与品牌标识}：为常见工具（网络搜索、代码执行、文件系统、API）使用易于识别的图标，便于快速扫描。

  \item \textbf{Error highlighting}: Failed tool calls shown in red with the error message and any retry attempts.
  \item \textbf{错误高亮}：失败的调用以红色显示，附有错误信息及任何重试尝试。
\end{itemize}

\subsection{Progress Indicators}
\label{progress-indicators}
## Progress Indicators
## 进度指示器

Multi-step agentic tasks require rich progress feedback:
多步代理型任务需要丰富的进度反馈：

\begin{itemize}
  \item \textbf{Step-level progress}: A numbered list of planned steps with checkmarks as each completes. For dynamic plans, steps can be added or removed as the agent adapts.
  \item \textbf{步骤级进度}：计划步骤的编号列表，每步完成后打勾。对于动态计划，步骤可随代理适应而添加或移除。

  \item \textbf{Token streaming indicators}: A blinking cursor or animated ellipsis during generation; a token-per-second counter for power users.
  \item \textbf{Token流指示器}：生成过程中的闪烁光标或动画省略号；为高级用户提供每秒Token数计数器。

  \item \textbf{Estimated completion}: Where feasible, an ETA based on task complexity and historical performance. Displayed with appropriate uncertainty (``approximately 2--5 minutes'').
  \item \textbf{预计完成时间}：在可行时，基于任务复杂度和历史性能的预计完成时间。显示时附有适当的不确定性（“大约2-5分钟”）。

  \item \textbf{Subtask nesting}: For hierarchical tasks, a tree-structured progress view with expandable subtasks.
  \item \textbf{子任务嵌套}：对于分层任务，采用树状结构的进度视图，子任务可展开。

  \item \textbf{Cancellation}: A clearly visible ``Stop'' button that gracefully halts the agent and summarizes work completed so far.
  \item \textbf{取消}：一个清晰可见的“停止”按钮，可优雅地终止代理并总结已完成的工作。
\end{itemize}

\subsection{Approval Gates}
\label{approval-gates}
## Approval Gates
## 审批门控

Approval gates are the primary mechanism for human-in-the-loop control. They must be designed to be \emph{informative} (giving users enough context to make a good decision) without being \emph{fatiguing} (requiring approval for every trivial action).
审批门控是人机协同控制的主要机制。它们的设计必须\emph{信息充分}（为用户提供足够的决策上下文），同时又不能\emph{疲劳轰炸}（要求对每个琐碎操作都进行审批）。

\begin{warningbox}[Alert Fatigue in Approval Gates]
If an agent requests approval too frequently, users will begin approving reflexively without reading---defeating the purpose of the gate. Tiered approval policies (see Section~\ref{subsec:hitl-design}) are essential to maintain meaningful oversight.
\begin{warningbox}[审批门控中的告警疲劳]
如果代理过于频繁地请求审批，用户将开始不假思索地批准——这便违背了门控的初衷。分层审批策略（参见第~\ref{subsec:hitl-design}节）对于保持有意义的监督至关重要。
\end{warningbox}

Approval gate UI elements:
审批门控UI元素：
```

```markdown
\begin{itemize}
  \item \textbf{Action summary}: Plain-language description of what the agent wants to do (``Send an email to john@example.com with the attached report'').
  \item \textbf{Risk indicator}: Visual signal of action reversibility (green = easily undoable, yellow = hard to undo, red = irreversible).
  \item \textbf{Approve / Reject / Modify}: Three-option interface; ``Modify'' opens an editor for the action parameters before approval.
  \item \textbf{Context panel}: Expandable section showing why the agent wants to take this action (relevant reasoning, prior steps).
  \item \textbf{Timeout behavior}: Clear indication of what happens if the user doesn’t respond (agent pauses, not proceeds).
\end{itemize}

\begin{itemize}
  \item \textbf{动作摘要}：用通俗语言描述智能体想要执行的操作（例如“发送一封包含附件的邮件至 john@example.com”）。
  \item \textbf{风险指示器}：动作可逆性的视觉信号（绿色 = 容易撤销，黄色 = 难以撤销，红色 = 不可逆）。
  \item \textbf{批准 / 拒绝 / 修改}：三选项界面；“修改”会在批准前打开一个动作参数编辑器。
  \item \textbf{上下文面板}：一个可展开的区域，显示智能体为何要执行此动作（相关推理、先前步骤）。
  \item \textbf{超时行为}：清晰说明用户未响应时会发生什么（智能体暂停，而非继续执行）。
\end{itemize}

\subsection{Context Display}
\label{context-display}
\subsection{上下文显示}
\label{context-display}

Agents maintain internal state---memory, active tools, retrieved documents, conversation history---that influences their behavior. Making this state visible helps users understand and predict agent behavior.

智能体维护内部状态——记忆、活跃工具、检索到的文档、对话历史——这些状态会影响其行为。让这些状态可见有助于用户理解和预测智能体的行为。

\begin{itemize}
  \item \textbf{Memory panel}: Shows what the agent currently ``remembers'' about the user, task, and prior interactions. Editable by the user.
  \item \textbf{Active tools list}: Which tools are currently available to the agent, with enable/disable toggles.
  \item \textbf{Retrieved context}: Documents or data chunks currently in the agent’s context window, with source citations.
  \item \textbf{Token budget indicator}: How much of the context window is consumed, helping users understand when to start a new session.
\end{itemize}

\begin{itemize}
  \item \textbf{记忆面板}：显示智能体当前关于用户、任务和先前交互的“记忆”。用户可编辑。
  \item \textbf{活跃工具列表}：当前可供智能体使用的工具，带有启用/禁用开关。
  \item \textbf{检索到的上下文}：当前位于智能体上下文窗口中的文档或数据片段，附带来源引用。
  \item \textbf{Token 预算指示器}：已消耗的上下文窗口比例，帮助用户了解何时应开始新会话。
\end{itemize}

\subsection{Error and Recovery UI}
\label{error-and-recovery-ui}
\subsection{错误与恢复界面}
\label{error-and-recovery-ui}

Agents fail---tools return errors, models hallucinate, plans become infeasible. The UI must handle failures gracefully:

智能体会失败——工具返回错误、模型产生幻觉、计划变得不可行。UI 必须优雅地处理失败：

\begin{itemize}
  \item \textbf{Error cards}: Inline display of failures with the error type, message, and the agent’s interpretation.
  \item \textbf{Retry controls}: Manual retry button with optional parameter adjustment.
  \item \textbf{Alternative approaches}: When the primary approach fails, the agent proposes alternatives; the UI presents them as selectable options.
  \item \textbf{Partial results}: If a multi-step task fails midway, the UI shows completed steps and their outputs, preserving partial value.
  \item \textbf{Escalation path}: A clear path to human support or manual completion when the agent cannot proceed.
\end{itemize}

\begin{itemize}
  \item \textbf{错误卡片}：内联显示失败信息，包括错误类型、消息以及智能体的解释。
  \item \textbf{重试控件}：手动重试按钮，可附带参数调整选项。
  \item \textbf{替代方案}：当主要方法失败时，智能体提出替代方案；UI 将其呈现为可选项。
  \item \textbf{部分结果}：如果多步骤任务中途失败，UI 显示已完成步骤及其输出，保留部分价值。
  \item \textbf{升级路径}：当智能体无法继续时，提供明确的路径转向人工支持或手动完成。
\end{itemize}

\subsection{Confidence Indicators}
\label{confidence-indicators}
\subsection{置信度指示器}
\label{confidence-indicators}

LLMs are probabilistic systems with calibrated (or miscalibrated) uncertainty. Surfacing confidence helps users know when to trust and when to verify:

大语言模型 (LLMs) 是具有校准（或未校准）不确定性的概率系统。呈现置信度有助于用户知道何时信任、何时验证：

\begin{itemize}
  \item \textbf{Verbal hedging display}: Highlight phrases like ``I’m not certain'' or ``you may want to verify'' to draw attention to low-confidence claims.
  \item \textbf{Source quality indicators}: For retrieved information, show source recency, authority, and relevance scores.
  \item \textbf{Explicit uncertainty requests}: A ``How confident are you?'' button that prompts the agent to self-assess and explain its uncertainty.
  \item \textbf{Verification suggestions}: For high-stakes outputs, the agent proactively suggests verification steps (``I recommend checking this calculation independently'').
\end{itemize}

\begin{itemize}
  \item \textbf{语言模糊性显示}：高亮显示诸如“我不确定”或“您可能需要验证”等短语，以引起对低置信度陈述的注意。
  \item \textbf{来源质量指示器}：对于检索到的信息，显示来源的时效性、权威性和相关性分数。
  \item \textbf{显式不确定性请求}：“您有多大把握？”按钮，提示智能体自我评估并解释其不确定性。
  \item \textbf{验证建议}：对于高风险的输出，智能体主动建议验证步骤（“我建议独立检查此计算结果”）。
\end{itemize}

\section{Frameworks and Libraries}
\label{subsec:ui-frameworks}
\section{框架与库}
\label{subsec:ui-frameworks}

A growing ecosystem of frameworks accelerates the development of agentic UIs. We survey the most widely adopted, organized by primary language and use case.

越来越多的框架生态正在加速智能体用户界面 (agentic UI) 的开发。我们按照主要语言和用例整理了最广泛采用的框架。

\subsection{Vercel AI SDK}
\label{vercel-ai-sdk}
\subsection{Vercel AI SDK}
\label{vercel-ai-sdk}

The Vercel AI SDK~\cite{vercel2024aisdk} is a TypeScript/JavaScript library for building streaming AI interfaces in React, Next.js, Svelte, and Vue. It is the most widely used framework for production web-based agent UIs.

Vercel AI SDK~\cite{vercel2024aisdk} 是一个 TypeScript/JavaScript 库，用于在 React、Next.js、Svelte 和 Vue 中构建流式 AI 界面。它是生产环境中基于 Web 的智能体 UI 最广泛使用的框架。

\textbf{Core abstractions:}

\textbf{核心抽象：}

\begin{itemize}
  \item \texttt{useChat}: A React hook managing a chat conversation with streaming support, message history, and loading states.
  \item \texttt{useCompletion}: A hook for single-turn text completion with streaming.
  \item \texttt{useObject}: Streams structured JSON objects, enabling progressive rendering of complex outputs.
  \item \texttt{streamText} / \texttt{streamObject}: Server-side functions that stream LLM responses over HTTP.
\end{itemize}

\begin{itemize}
  \item \texttt{useChat}：一个 React 钩子 (hook)，管理带有流式支持、消息历史和加载状态的聊天对话。
  \item \texttt{useCompletion}：一个用于单轮文本补全并支持流式的钩子。
  \item \texttt{useObject}：流式传输结构化 JSON 对象，实现对复杂输出的渐进式渲染。
  \item \texttt{streamText} / \texttt{streamObject}：通过 HTTP 流式传输 LLM 响应的服务端函数。
\end{itemize}

\textbf{Generative UI (AI SDK RSC):} The most distinctive feature of the Vercel AI SDK is its support for \emph{generative UI} via React Server Components (RSC). Rather than returning text, the LLM can invoke tools whose results are rendered as arbitrary React components---a weather widget, a stock chart, a booking form---streamed directly into the UI. This is discussed further in Section~\ref{subsec:generative-ui}.

\textbf{生成式 UI (AI SDK RSC)：} Vercel AI SDK 最显著的特点是支持通过 React Server Components (RSC) 实现\emph{生成式 UI (generative UI)}。LLM 不是返回文本，而是可以调用工具，工具的结果被渲染为任意 React 组件——天气小部件、股票图表、预订表单——并直接流式传输到 UI 中。这将在第~\ref{subsec:generative-ui} 节进一步讨论。

\subsection{Chainlit}
\label{chainlit}
\subsection{Chainlit}
\label{chainlit}

Chainlit~\cite{chainlit2024} is a Python framework for building production-ready agent UIs with minimal boilerplate. It is particularly popular in the LangChain and LlamaIndex ecosystems.

Chainlit~\cite{chainlit2024} 是一个 Python 框架，用于以最少的样板代码构建生产就绪的智能体 UI。它在 LangChain 和 LlamaIndex 生态系统中尤其流行。

\textbf{Key features:}

\textbf{主要特性：}

\begin{itemize}
  \item \textbf{Step visualization}: Chainlit natively renders LangChain and LlamaIndex execution steps as a collapsible tree, showing each chain call, retrieval, and tool invocation.
  \item \textbf{Multi-modal support}: File uploads, image display, audio playback, and PDF rendering out of the box.
  \item \textbf{Authentication and sessions}: Built-in user authentication, persistent conversation history, and multi-user support.
  \item \textbf{Custom elements}: React components can be registered and rendered from Python, enabling rich custom visualizations.
  \item \textbf{Feedback collection}: Built-in thumbs up/down feedback with optional comments, stored to a database.
\end{itemize}

\begin{itemize}
  \item \textbf{步骤可视化}：Chainlit 原生将 LangChain 和 LlamaIndex 的执行步骤渲染为可折叠的树状结构，显示每次链式调用、检索和工具调用。
  \item \textbf{多模态支持}：开箱即用地支持文件上传、图像显示、音频播放和 PDF 渲染。
  \item \textbf{认证与会话}：内置用户认证、持久化对话历史以及多用户支持。
  \item \textbf{自定义元素}：可以从 Python 注册并渲染 React 组件，从而实现丰富的自定义可视化。
  \item \textbf{反馈收集}：内置点赞/点踩反馈，可附带评论，并存储到数据库中。
\end{itemize}

\begin{lstlisting}[style=pythonstyle, caption={Minimal Chainlit agent with step visualization}]
import chainlit as cl
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

agent = create_react_agent(
    ChatOpenAI(model="gpt-4o"), tools=[search]
)

@cl.on_message
async def on_message(message: cl.Message):
    # Chainlit automatically renders each step as a collapsible UI element
    # when using the callback handler
    async with cl.Step(name="Agent", type="run") as step:
        step.input = message.content
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": message.content}]},
            config={"callbacks": [cl.LangchainCallbackHandler()]}
        )
        output = result["messages"][-1].content
        step.output = output

    await cl.Message(content=output).send()
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={最小化 Chainlit 智能体，包含步骤可视化}]
import chainlit as cl
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

@tool
def search(query: str) -> str:
    """搜索信息。"""
    return f"Results for: {query}"

agent = create_react_agent(
    ChatOpenAI(model="gpt-4o"), tools=[search]
)

@cl.on_message
async def on_message(message: cl.Message):
    # 使用回调处理器时，Chainlit 自动将每个步骤渲染为可折叠的 UI 元素
    async with cl.Step(name="Agent", type="run") as step:
        step.input = message.content
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": message.content}]},
            config={"callbacks": [cl.LangchainCallbackHandler()]}
        )
        output = result["messages"][-1].content
        step.output = output

    await cl.Message(content=output).send()
\end{lstlisting}

\subsection{Gradio}
\label{gradio}
\subsection{Gradio}
\label{gradio}

Gradio~\cite{abid2019gradio} is a Python library for rapidly building ML demos and agent interfaces. Its \texttt{gr.ChatInterface} and \texttt{gr.Blocks} API enable quick prototyping of conversational agents with minimal code.

Gradio~\cite{abid2019gradio} 是一个 Python 库，用于快速构建机器学习演示和智能体界面。其 \texttt{gr.ChatInterface} 和 \texttt{gr.Blocks} API 可以用最少的代码快速原型化对话式智能体。

\textbf{Strengths for agentic UIs:}

\textbf{在智能体 UI 方面的优势：}

\begin{itemize}
  \item \textbf{Zero-configuration deployment}: One-line sharing via Hugging Face Spaces.
  \item \textbf{Custom components}: The Gradio Custom Components system allows building React components that integrate seamlessly with Python backends.
  \item \textbf{Multi-modal inputs}: File upload, image, audio, video, and webcam inputs with minimal configuration.
  \item \textbf{Streaming}: Native support for generator-based streaming responses.
\end{itemize}

\begin{itemize}
  \item \textbf{零配置部署}：通过 Hugging Face Spaces 一键共享。
  \item \textbf{自定义组件}：Gradio 自定义组件系统允许构建与 Python 后端无缝集成的 React 组件。
  \item \textbf{多模态输入}：文件上传、图像、音频、视频和摄像头输入，配置极少。
  \item \textbf{流式传输}：原生支持基于生成器的流式响应。
\end{itemize}

\textbf{Limitations:} Gradio’s layout system is less flexible than full React frameworks, and its state management is session-scoped, making complex multi-agent coordination challenging.

\textbf{局限性：} Gradio 的布局系统不如完整的 React 框架灵活，且其状态管理局限于会话范围，使得复杂的多智能体协调变得具有挑战性。

\subsection{Streamlit}
\label{streamlit}
\subsection{Streamlit}
\label{streamlit}

Streamlit~\cite{streamlit2024} is a Python framework for data applications that has been widely adopted for agent dashboards and monitoring UIs. Its reactive execution model---the entire script reruns on each interaction---is simple but can be limiting for complex agentic workflows.

Streamlit~\cite{streamlit2024} 是一个用于数据应用的 Python 框架，已广泛用于智能体仪表盘和监控 UI。它的响应式执行模型（每次交互整个脚本重新运行）虽然简单，但对于复杂的智能体工作流可能有限制。

\textbf{Agentic use cases:}

\textbf{智能体用例：}
```

\begin{itemize}
  \item \textbf{Agent dashboards}: Real-time metrics, task queues, and status displays using \texttt{st.metric}, \texttt{st.dataframe}, and \texttt{st.status}.
  \item \textbf{代理仪表盘 (Agent dashboards)}：使用 \texttt{st.metric}、\texttt{st.dataframe} 和 \texttt{st.status} 实现实时指标、任务队列和状态显示。
  \item \textbf{Session state}: \texttt{st.session\_state} persists agent state across reruns, enabling multi-turn conversations.
  \item \textbf{会话状态 (Session state)}：\texttt{st.session\_state} 在多次重运行之间持久化代理状态，支持多轮对话。
  \item \textbf{Streaming}: \texttt{st.write\_stream} renders generator outputs progressively.
  \item \textbf{流式输出 (Streaming)}：\texttt{st.write\_stream} 逐步渲染生成器的输出。
  \item \textbf{Fragments}: \texttt{@st.fragment} decorator enables partial reruns, improving performance for live-updating dashboards.
  \item \textbf{片段 (Fragments)}：\texttt{@st.fragment} 装饰器支持部分重运行，提升实时更新仪表盘的性能。
\end{itemize}

\subsection{OpenAI Assistants Playground}
\label{openai-assistants-playground}
\subsection{OpenAI Assistants Playground}
\label{openai-assistants-playground}

The OpenAI Assistants Playground serves as a reference implementation for agentic UI design. It demonstrates:
OpenAI Assistants Playground 作为代理 UI 设计的参考实现，展示了以下功能：

\begin{itemize}
  \item Thread-based conversation management with persistent history.
  \item 基于线程的对话管理，支持持久化历史记录。
  \item File attachment and retrieval visualization.
  \item 文件附件与检索的可视化。
  \item Code interpreter execution with output display (stdout, images, files).
  \item 代码解释器执行与输出显示（标准输出、图像、文件）。
  \item Function call display with input/output inspection.
  \item 函数调用显示，支持输入/输出检查。
  \item Run step visualization showing the sequence of model calls and tool invocations.
  \item 运行步骤可视化，展示模型调用和工具调用的序列。
\end{itemize}

While not a framework for building custom UIs, the Playground’s design patterns are widely emulated.
虽然它并非用于构建自定义 UI 的框架，但 Playground 的设计模式被广泛借鉴。

\subsection{LangGraph Studio}
\label{langgraph-studio}
\subsection{LangGraph Studio}
\label{langgraph-studio}

LangGraph Studio~\cite{langgraph2024studio} is a desktop application providing a visual IDE for LangGraph agents. It is the most sophisticated tool-use and workflow visualization environment currently available.
LangGraph Studio~\cite{langgraph2024studio} 是一款桌面应用程序，为 LangGraph 代理提供可视化 IDE。它是目前最完善的工具使用和工作流可视化环境。

\textbf{Features:}
\textbf{特性：}

\begin{itemize}
  \item \textbf{Graph visualization}: Interactive rendering of the agent’s state machine, with nodes representing agent steps and edges representing transitions.
  \item \textbf{图可视化 (Graph visualization)}：交互式渲染代理状态机，节点表示代理步骤，边表示转换。
  \item \textbf{State inspection}: At any point in execution, the full agent state (all variables, memory, tool results) can be inspected as structured JSON.
  \item \textbf{状态检查 (State inspection)}：在执行过程中的任意时刻，可查看完整的代理状态（所有变量、记忆、工具结果）作为结构化 JSON。
  \item \textbf{Time-travel debugging}: Replay any prior execution step, modify the state, and re-run from that point.
  \item \textbf{时间旅行调试 (Time-travel debugging)}：重放任意先前的执行步骤，修改状态，然后从该点重新运行。
  \item \textbf{Human-in-the-loop integration}: Breakpoints can be set on any node; execution pauses and waits for human input before proceeding.
  \item \textbf{人在回路集成 (Human-in-the-loop integration)}：可在任意节点设置断点；执行暂停并等待人工输入后再继续。
  \item \textbf{Multi-agent support}: Visualizes supervisor-subagent hierarchies and inter-agent message passing.
  \item \textbf{多代理支持 (Multi-agent support)}：可视化主管-子代理层级以及代理间消息传递。
\end{itemize}

\subsection{Framework Comparison}
\label{framework-comparison}
\subsection{框架比较}
\label{framework-comparison}

Table~\ref{tab:ui-framework-comparison} summarizes the key characteristics of the frameworks discussed above.
表~\ref{tab:ui-framework-comparison} 总结了上述框架的关键特征。

\begin{table}[ht!]
\centering
\caption{Agentic UI framework comparison.}
\caption{代理 UI 框架比较。}
\label{tab:ui-framework-comparison}
{\footnotesize
\begin{tabular}{@{}llccccc@{}}
\toprule
\textbf{Framework} & \textbf{Language} & \textbf{Stream} & \textbf{Tool Viz} & \textbf{Multi-Ag.} & \textbf{Gen UI} & \textbf{Prod} \\
\textbf{框架} & \textbf{语言} & \textbf{流式} & \textbf{工具可视化} & \textbf{多代理} & \textbf{生成式 UI} & \textbf{生产可用} \\
\midrule
Vercel AI SDK & TypeScript & \checkmark{} & Partial & Partial & \checkmark{} & \checkmark{} \\
Vercel AI SDK & TypeScript & \checkmark{} & 部分 & 部分 & \checkmark{} & \checkmark{} \\
Chainlit & Python & \checkmark{} & \checkmark{} & Partial & Partial & \checkmark{} \\
Chainlit & Python & \checkmark{} & \checkmark{} & 部分 & 部分 & \checkmark{} \\
Gradio & Python & \checkmark{} & $\circ$ & $\times$ & $\circ$ & \checkmark{} \\
Gradio & Python & \checkmark{} & $\circ$ & $\times$ & $\circ$ & \checkmark{} \\
Streamlit & Python & \checkmark{} & $\circ$ & $\times$ & $\times$ & \checkmark{} \\
Streamlit & Python & \checkmark{} & $\circ$ & $\times$ & $\times$ & \checkmark{} \\
OAI Playground & N/A (hosted) & \checkmark{} & \checkmark{} & $\times$ & $\times$ & $\times$ \\
OAI Playground & N/A (托管) & \checkmark{} & \checkmark{} & $\times$ & $\times$ & $\times$ \\
LangGraph Studio & Python/TS & \checkmark{} & \checkmark{} & \checkmark{} & $\times$ & Partial \\
LangGraph Studio & Python/TS & \checkmark{} & \checkmark{} & \checkmark{} & $\times$ & 部分 \\
\bottomrule
\end{tabular}
}
\end{table}

\section{Generative UI}
\label{subsec:generative-ui}
\section{生成式 UI (Generative UI)}
\label{subsec:generative-ui}

\begin{intuitionbox}[The Generative UI Concept]
Traditional LLM interfaces render model outputs as text or markdown. \emph{Generative UI} inverts this: the model’s tool calls \emph{generate} UI components. The model decides not just \emph{what} to say, but \emph{how} to present it---as a chart, a form, a map, a calendar widget---based on the content type and user intent.
\end{intuitionbox}
\begin{intuitionbox}[生成式 UI 概念]
传统 LLM 接口将模型输出渲染为文本或 Markdown。\emph{生成式 UI (Generative UI)} 则颠覆了这一模式：模型的工具调用\emph{生成} UI 组件。模型不仅决定\emph{说什么}，还根据内容类型和用户意图决定\emph{如何呈现}——以图表、表单、地图、日历控件等形式。
\end{intuitionbox}

Generative UI represents a fundamental shift in the relationship between LLMs and interfaces. Rather than the developer pre-specifying all possible UI states, the model dynamically selects and parameterizes UI components appropriate to the current context.
生成式 UI 代表了 LLM 与界面关系的根本转变。开发者不再需要预先指定所有可能的 UI 状态，而是由模型根据当前上下文动态选择并参数化合适的 UI 组件。

\subsection{React Server Components for Dynamic Interfaces}
\label{react-server-components-for-dynamic-interfaces}
\subsection{用于动态界面的 React 服务端组件}
\label{react-server-components-for-dynamic-interfaces}

The Vercel AI SDK’s RSC (React Server Components\footnote{React Server Components}) integration is the most mature implementation of generative UI. The architecture works as follows:
Vercel AI SDK 的 RSC（React 服务端组件 (React Server Components)）集成是生成式 UI 最成熟的实现。其架构工作流程如下：

\begin{enumerate}
  \item The user sends a message to a Next.js\footnote{Next.js} server action.
  \item 用户向 Next.js 服务端操作 (Server Action) 发送消息。
  \item The server calls the LLM with a set of tools, each associated with a React component.
  \item 服务端调用 LLM，并传入一组工具，每个工具都与一个 React 组件相关联。
  \item When the LLM calls a tool (e.g., \texttt{show\_weather}), the server renders the corresponding React component with the tool’s output as props.
  \item 当 LLM 调用某个工具（例如 \texttt{show\_weather}）时，服务端渲染对应的 React 组件，并将工具的输出作为 props 传入。
  \item The rendered component is streamed to the client as a React Server Component, appearing inline in the chat.
  \item 渲染后的组件作为 React 服务端组件流式传输到客户端，在聊天中内联显示。
\end{enumerate}

\begin{lstlisting}[style=pythonstyle, caption={Generative UI with Vercel AI SDK RSC (TypeScript)}]
\begin{lstlisting}[style=pythonstyle, caption={使用 Vercel AI SDK RSC 的生成式 UI (TypeScript)}]
// app/actions.tsx (Server Action)
import { streamUI } from 'ai/rsc';
import { openai } from '@ai-sdk/openai';
import { WeatherCard } from '@/components/WeatherCard';
import { StockChart } from '@/components/StockChart';

export async function chat(userMessage: string) {
  const result = await streamUI({
    model: openai('gpt-4o'),
    messages: [{ role: 'user', content: userMessage }],
    tools: {
      show_weather: {
        description: 'Display current weather for a location',
        parameters: z.object({
          location: z.string(),
          unit: z.enum(['celsius', 'fahrenheit']),
        }),
        // Tool result rendered as a React component
        generate: async ({ location, unit }) => {
          const data = await fetchWeather(location, unit);
          return <WeatherCard data={data} />;
        },
      },
      show_stock: {
        description: 'Display stock price chart',
        parameters: z.object({ ticker: z.string() }),
        generate: async ({ ticker }) => {
          const data = await fetchStockData(ticker);
          return <StockChart ticker={ticker} data={data} />;
        },
      },
    },
  });
  return result.value;
}
\end{lstlisting}
\end{lstlisting}

\subsection{Adaptive Interfaces Based on Content Type}
\label{adaptive-interfaces-based-on-content-type}
\subsection{基于内容类型的自适应界面}
\label{adaptive-interfaces-based-on-content-type}

Generative UI enables interfaces that adapt to the nature of the content being presented:
生成式 UI 使界面能够根据所呈现内容的性质进行自适应调整：

\begin{itemize}
  \item \textbf{Tabular data} $\rightarrow$ sortable, filterable data table with export options.
  \item \textbf{表格数据 (Tabular data)} $\rightarrow$ 可排序、可筛选的数据表，并支持导出选项。
  \item \textbf{Geographic data} $\rightarrow$ interactive map with markers and layers.
  \item \textbf{地理数据 (Geographic data)} $\rightarrow$ 带有标记和图层的交互式地图。
  \item \textbf{Time series} $\rightarrow$ zoomable line chart with annotations.
  \item \textbf{时间序列 (Time series)} $\rightarrow$ 可缩放且带注释的折线图。
  \item \textbf{Code} $\rightarrow$ syntax-highlighted editor with run button.
  \item \textbf{代码 (Code)} $\rightarrow$ 语法高亮编辑器，附带运行按钮。
  \item \textbf{Documents} $\rightarrow$ formatted document viewer with annotation tools.
  \item \textbf{文档 (Documents)} $\rightarrow$ 格式化文档查看器，带有注释工具。
  \item \textbf{Forms/structured input} $\rightarrow$ dynamically generated form fields.
  \item \textbf{表单/结构化输入 (Forms/structured input)} $\rightarrow$ 动态生成的表单字段。
\end{itemize}

The model acts as a \emph{UI orchestrator}, selecting the most appropriate presentation for each piece of information. This reduces the need for developers to anticipate every possible output type and pre-build corresponding components.
模型充当\emph{UI 编排器 (UI orchestrator)}，为每条信息选择最合适的展示方式。这减少了开发者需要预判所有可能的输出类型并预先构建对应组件的需求。

\begin{questionbox}[Limits of Generative UI]
How much UI generation should be delegated to the model? Fully model-driven UI risks inconsistency, accessibility failures, and security vulnerabilities (e.g., a model generating a form that submits data to an unexpected endpoint). In practice, generative UI works best when the model selects from a \emph{curated library} of pre-built, accessible, and secure components rather than generating arbitrary HTML or JSX.
\end{questionbox}
\begin{questionbox}[生成式 UI 的局限性]
应该将多少 UI 生成工作委托给模型？完全由模型驱动的 UI 存在不一致性、无障碍性失败以及安全漏洞的风险（例如，模型生成的表单将数据提交到意外的端点）。在实践中，当模型从预构建、无障碍且安全的\emph{精选组件库 (curated library)} 中进行选择，而非生成任意 HTML 或 JSX 时，生成式 UI 的效果最佳。
\end{questionbox}

\section{Streaming and Real-Time Patterns}
\label{subsec:streaming-patterns}
\section{流式与实时模式}
\label{subsec:streaming-patterns}

Streaming is foundational to agentic UIs: it transforms the experience from ``wait for a result'' to ``watch the agent work.'' This section covers the key streaming patterns and their implementation considerations.
流式传输是代理 UI 的基础：它将体验从“等待结果”转变为“观察代理工作”。本节涵盖关键的流式模式及其实现考虑因素。

\subsection{Token Streaming}
\label{token-streaming}
\subsection{令牌流式传输 (Token Streaming)}
\label{token-streaming}

## Motivation: Beyond the Chat Box
## 动机：超越聊天框

Token streaming delivers LLM output incrementally as tokens are generated, rather than waiting for the complete response. Two transport mechanisms are commonly used:
Token streaming（令牌流）在生成令牌时逐步传递 LLM 输出，而不是等待完整响应。常用两种传输机制：

\begin{itemize}
  \item \textbf{Server-Sent Events (SSE)}12: A unidirectional HTTP stream from server to client. Each event carries a chunk of tokens. SSE is simple, works over standard HTTP/1.1, and is automatically reconnected by browsers. It is the dominant mechanism for LLM streaming APIs (OpenAI, Anthropic, Google all use SSE).
  \item \textbf{Server-Sent Events（SSE）}：从服务器到客户端的单向 HTTP 流。每个事件携带一个令牌块。SSE 简单，基于标准 HTTP/1.1，浏览器自动重连，是 LLM 流式 API 的主流机制（OpenAI、Anthropic、Google 均使用 SSE）。
  \item \textbf{WebSockets}: Bidirectional persistent connections. More complex to implement but necessary for interactive streaming scenarios where the client needs to send data mid-stream (e.g., interrupting the agent, providing mid-generation feedback).
  \item \textbf{WebSockets}：双向持久连接。实现更复杂，但对于客户端需要在流中发送数据的交互式流场景（例如中断智能体、提供生成中反馈）是必要的。
\end{itemize}

\begin{lstlisting}[style=pythonstyle, caption={SSE token streaming with FastAPI}]
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
import json


app = FastAPI()
client = AsyncOpenAI()


async def token_stream(prompt: str):
    """Generator that yields SSE-formatted token chunks."""
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            # SSE format: "data: <json>\n\n"
            yield f"data: {json.dumps({'token': delta.content})}\n\n"
        elif chunk.choices[0].finish_reason:
            yield f"data: {json.dumps({'done': True})}\n\n"


@app.get("/stream")
async def stream_endpoint(prompt: str):
    return StreamingResponse(
        token_stream(prompt),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
\end{lstlisting}

\subsection{Tool Call Streaming}
\label{tool-call-streaming}
\subsection{工具调用流式 (Tool Call Streaming)}
\label{tool-call-streaming}

Modern LLM APIs support streaming tool calls: the tool name and arguments are streamed incrementally, enabling the UI to show ``Agent is calling \texttt{search\_web} with query: ‘climate change 2024’\ldots{}'' before the tool has even been invoked. This requires parsing partial JSON, which can be done with streaming JSON parsers.
现代 LLM API 支持流式工具调用：工具名称和参数逐步流式传输，使得 UI 能够在工具被实际调用前就显示“智能体正在调用 \texttt{search\_web}，查询为：‘climate change 2024’……”。这需要解析部分 JSON，可使用流式 JSON 解析器完成。

Patterns for tool call streaming:
工具调用流式的模式：

\begin{itemize}
  \item \textbf{Progressive argument display}: Show tool arguments as they stream in, even before the call is complete.
  \item \textbf{渐进式参数显示}：在调用完成前，随着参数流式输入逐步显示工具参数。
  \item \textbf{Parallel tool call indicators}: When the model calls multiple tools simultaneously, show all of them as pending, then update each as results arrive.
  \item \textbf{并行工具调用指示器}：当模型同时调用多个工具时，将它们全部显示为待处理状态，然后随着结果到达分别更新。
  \item \textbf{Tool result streaming}: Some tools (e.g., code execution, web scraping) can themselves stream results; pipe these through to the UI progressively.
  \item \textbf{工具结果流式传输}：某些工具（如代码执行、网页抓取）自身可以流式传输结果；将这些结果逐步传递到 UI。
\end{itemize}

\subsection{Multi-Agent Streaming}
\label{multi-agent-streaming}
\subsection{多智能体流式 (Multi-Agent Streaming)}
\label{multi-agent-streaming}

In multi-agent systems, multiple agents may be generating output simultaneously. The UI must handle parallel streams:
在多智能体系统中，多个智能体可能同时生成输出。UI 必须处理并行流：

\begin{itemize}
  \item \textbf{Agent-labeled streams}: Each stream is tagged with the agent’s identity; the UI renders them in separate lanes or panels.
  \item \textbf{智能体标记流}：每个流带有智能体身份标签；UI 将其渲染在单独的通道或面板中。
  \item \textbf{Stream merging}: For supervisor-subagent patterns, the supervisor’s stream may interleave with subagent streams; the UI must maintain coherent ordering.
  \item \textbf{流合并}：对于监督者-子智能体模式，监督者的流可能与子智能体的流交错；UI 必须保持一致的顺序。
  \item \textbf{Backpressure}: If the UI cannot render as fast as streams arrive (e.g., multiple agents generating simultaneously), a backpressure mechanism must prevent buffer overflow. Strategies include: dropping intermediate tokens (showing only the latest), batching updates, or pausing slower streams.
  \item \textbf{背压 (Backpressure)}：如果 UI 的渲染速度跟不上流到达的速度（例如多个智能体同时生成），必须采用背压机制防止缓冲区溢出。策略包括：丢弃中间令牌（仅显示最新）、批量更新或暂停较慢的流。
\end{itemize}

\subsection{Optimistic UI Updates}
\label{optimistic-ui-updates}
\subsection{乐观 UI 更新 (Optimistic UI Updates)}
\label{optimistic-ui-updates}

Optimistic UI updates improve perceived responsiveness by immediately reflecting user actions in the UI before server confirmation:
乐观 UI 更新通过在服务器确认之前立即在 UI 中反映用户操作，提升感知响应速度：

\begin{itemize}
  \item When a user sends a message, it appears immediately in the chat history (optimistically) while the request is in flight.
  \item 当用户发送消息时，该消息会立即（乐观地）出现在聊天历史中，同时请求正在传输中。
  \item When an approval gate is accepted, the UI immediately shows the action as ``approved'' and begins showing the agent’s next steps, even before the server has processed the approval.
  \item 当批准门控被接受时，UI 立即显示该操作为“已批准”，并开始展示智能体的后续步骤，即使服务器尚未处理该批准。
  \item If the server returns an error, the optimistic update is rolled back and an error state is shown.
  \item 如果服务器返回错误，则回滚乐观更新并显示错误状态。
\end{itemize}

\subsection{Backpressure Handling}
\label{backpressure-handling}
\subsection{背压处理 (Backpressure Handling)}
\label{backpressure-handling}

In high-throughput agentic scenarios, the rate of incoming data can exceed the UI’s rendering capacity. Strategies for managing backpressure:
在高吞吐量的智能体场景中，传入数据速率可能超过 UI 的渲染能力。管理背压的策略如下：

\begin{itemize}
  \item \textbf{Token batching}: Buffer tokens for 50--100ms and render in batches rather than one-by-one, reducing DOM update frequency.
  \item \textbf{令牌批处理}：将令牌缓冲 50--100ms 后分批渲染，而非逐个渲染，从而降低 DOM 更新频率。
  \item \textbf{Virtual scrolling}: For long outputs, render only the visible portion of the content, discarding off-screen DOM nodes.
  \item \textbf{虚拟滚动}：对于长输出，仅渲染内容的可见部分，丢弃屏幕外的 DOM 节点。
  \item \textbf{Throttled updates}: For metrics and status displays, update at a fixed rate (e.g., 10 Hz) regardless of the incoming data rate.
  \item \textbf{节流更新}：对于指标和状态显示，以固定速率（例如 10 Hz）更新，不受传入数据速率影响。
  \item \textbf{Progressive detail}: Show a summary view during high-throughput periods; full detail available on demand.
  \item \textbf{渐进式细节}：在高吞吐量期间显示摘要视图；按需提供完整细节。
\end{itemize}

\section{Human-in-the-Loop UI Design}
\label{subsec:hitl-design}
\section{人在回路中 UI 设计 (Human-in-the-Loop UI Design)}
\label{subsec:hitl-design}

Human-in-the-loop (HITL) interaction is one of the most consequential design challenges in agentic UIs. The goal is to maintain meaningful human oversight without creating a bottleneck that negates the efficiency benefits of automation.
人在回路中（HITL）交互是智能体 UI 中最关键的设计挑战之一。目标是保持有意义的人类监督，同时避免形成抵消自动化效率优势的瓶颈。

\subsection{When to Interrupt the Agent}
\label{when-to-interrupt-the-agent}
\subsection{何时中断智能体 (When to Interrupt the Agent)}
\label{when-to-interrupt-the-agent}

Not all agent actions warrant human review. A principled interruption policy considers:
并非所有智能体行为都需要人工审查。有原则的中断策略需考虑：

\begin{itemize}
  \item \textbf{Reversibility}: Irreversible actions (deleting files, sending emails, making purchases) always warrant approval. Reversible actions (reading files, searching the web) generally do not.
  \item \textbf{可逆性}：不可逆操作（删除文件、发送邮件、购买）始终需要批准。可逆操作（读取文件、搜索网络）通常不需要。
  \item \textbf{Scope}: Actions affecting external systems or other people warrant more scrutiny than purely local actions.
  \item \textbf{范围}：影响外部系统或其他人的操作比纯本地操作需要更严格的审查。
  \item \textbf{Confidence}: When the agent’s confidence in its interpretation of the user’s intent is low, it should ask for clarification rather than proceed.
  \item \textbf{置信度}：当智能体对用户意图解释的置信度较低时，应请求澄清而非继续执行。
  \item \textbf{Cost}: High-cost actions (large API calls, expensive computations) warrant approval.
  \item \textbf{成本}：高成本操作（大量 API 调用、昂贵计算）需要批准。
  \item \textbf{Novelty}: Actions the agent has not taken before in this context warrant more scrutiny than routine actions.
  \item \textbf{新颖性}：智能体在此上下文中未执行过的操作比常规操作需要更多审查。
\end{itemize}

\subsection{Tiered Approval Workflows}
\label{tiered-approval-workflows}
\subsection{分层审批工作流 (Tiered Approval Workflows)}
\label{tiered-approval-workflows}

A tiered approval policy balances oversight with efficiency:
分层审批策略在监督与效率之间取得平衡：

\begin{keybox}[Three-Tier Approval Model]
\textbf{Tier 1 (Auto-approve):} Low-risk, reversible, routine actions. Examples: web search, reading files, calling read-only APIs. The agent proceeds without interruption; actions are logged for audit.

\textbf{第1层（自动批准）：}低风险、可逆、常规操作。例如：网络搜索、读取文件、调用只读 API。智能体无需中断继续执行；操作记录在日志中供审计。

\textbf{Tier 2 (Notify):} Medium-risk actions. The UI shows a non-blocking notification (``Agent sent a draft email to your Drafts folder'') that the user can review asynchronously. A brief window (e.g., 30 seconds) allows cancellation before the action is finalized.

\textbf{第2层（通知）：}中等风险操作。UI 显示非阻塞通知（“智能体将草稿邮件发送到您的草稿箱”），用户可异步审查。在操作最终确定前有短暂窗口（例如 30 秒）允许取消。

\textbf{Tier 3 (Require approval):} High-risk, irreversible, or high-cost actions. The agent pauses and presents a blocking approval gate. The user must explicitly approve, reject, or modify before the agent continues.

\textbf{第3层（需批准）：}高风险、不可逆或高成本操作。智能体暂停并呈现阻塞式批准门控。用户必须明确批准、拒绝或修改后，智能体才能继续。
\end{keybox}

The thresholds between tiers can be configured by the user (``always ask before sending emails'') or learned from user behavior (if the user always approves web searches, auto-approve them in the future).
各层之间的阈值可由用户配置（“发送邮件前始终询问”）或从用户行为中学习（如果用户始终批准网络搜索，则未来自动批准）。

\subsection{Feedback Mechanisms}
\label{feedback-mechanisms}
\subsection{反馈机制 (Feedback Mechanisms)}
\label{feedback-mechanisms}

Beyond approval gates, agentic UIs should provide rich feedback mechanisms that help the agent improve over time:
除了批准门控，智能体 UI 还应提供丰富的反馈机制，帮助智能体随时间改进：

\begin{itemize}
  \item \textbf{Thumbs up/down}: Simple binary feedback on responses, stored and used for RLHF fine-tuning or preference learning.
  \item \textbf{Thumbs up/down（点赞/点踩）}：对响应的简单二元反馈，存储并用于RLHF微调或偏好学习。
  \item \textbf{Inline corrections}: Users can directly edit agent outputs; the delta between the original and corrected output is a training signal.
  \item \textbf{Inline corrections（内联修正）}：用户可以直接编辑智能体的输出；原始输出与修正输出之间的差异即为训练信号。
  \item \textbf{Preference selection}: When the agent offers multiple options, the user’s selection is a preference signal.
  \item \textbf{Preference selection（偏好选择）}：当智能体提供多个选项时，用户的选择即为偏好信号。
  \item \textbf{Explicit instruction}: ``Don’t do this again'', ``Always ask before X'', ``Prefer approach Y over Z''---natural language instructions that update the agent’s behavioral policy.
  \item \textbf{Explicit instruction（显式指令）}：“别再这样做了”、“在X之前始终询问”、“优先采用方法Y而非Z”——这些自然语言指令用于更新智能体的行为策略。
  \item \textbf{Rating with rationale}: Optional free-text explanation accompanying a rating, providing richer signal than binary feedback.
  \item \textbf{Rating with rationale（带理由的评分）}：评分时附带的可选自由文本解释，提供比二元反馈更丰富的信号。
\end{itemize}

\subsection{Teaching the Agent Through UI Interaction}
\subsection{通过UI交互教导智能体}
\label{teaching-the-agent-through-ui-interaction}

The most sophisticated HITL UIs treat every interaction as a teaching opportunity:
最先进的HITL UI将每一次交互都视为教学机会：

\begin{itemize}
  \item \textbf{Demonstration}: The user performs a task manually; the agent observes and learns the preferred approach.
  \item \textbf{Demonstration（示范）}：用户手动执行任务；智能体观察并学习偏好方法。
  \item \textbf{Correction with generalization}: When the user corrects an agent action, the UI asks ``Should I always do this differently?'' to generalize the correction.
  \item \textbf{Correction with generalization（带泛化的修正）}：当用户修正智能体的某个行为时，UI会询问“我是否应当始终以不同方式执行此操作？”以泛化该修正。
  \item \textbf{Preference elicitation}: Periodic prompts asking the user to compare two agent behaviors and indicate which is preferred.
  \item \textbf{Preference elicitation（偏好引示）}：定期提示用户比较两种智能体行为，并指出更偏好哪一种。
  \item \textbf{Behavioral profiles}: The UI maintains a visible ``preferences'' profile that the user can review and edit, making the agent’s learned behaviors transparent and controllable.
  \item \textbf{Behavioral profiles（行为档案）}：UI维护一个可见的“偏好”档案，用户可以查看和编辑，使智能体习得的行为透明可控。
\end{itemize}

\section{Accessibility and Trust}
\section{可访问性与信任}
\label{subsec:ui-trust}

Trust is not a feature---it is an emergent property of a system that consistently behaves as expected, explains itself clearly, and recovers gracefully from failures. Agentic UIs must be designed with trust as a first-class concern.
信任并非一项功能——而是系统持续按预期运作、清晰解释自身行为、并从故障中优雅恢复时涌现出的属性。智能体UI在设计时必须将信任作为首要考量。

\subsection{Explaining Agent Decisions}
\subsection{解释智能体决策}
\label{explaining-agent-decisions}

Explainability in agentic UIs goes beyond showing chain-of-thought. It requires:
智能体UI中的可解释性不仅限于展示思维链。它要求：

\begin{itemize}
  \item \textbf{Decision rationale}: For consequential decisions, the agent should explain not just \emph{what} it decided but \emph{why}---which factors were considered, what alternatives were rejected, and what assumptions were made.
  \item \textbf{Decision rationale（决策理由）}：对于有重大影响的决策，智能体不仅应解释其 \emph{做了什么}决策，还应说明 \emph{为什么}——考虑了哪些因素、拒绝了哪些备选方案、以及做出了哪些假设。
  \item \textbf{Source attribution}: Claims should be linked to their sources; retrieved documents should be citable.
  \item \textbf{Source attribution（来源归因）}：主张应链接至其来源；检索到的文档应可引用。
  \item \textbf{Counterfactual explanations}: ``If you had said X instead of Y, I would have done Z''---helping users understand the agent’s decision boundary.
  \item \textbf{Counterfactual explanations（反事实解释）}：“如果你当时说X而不是Y，我会做Z”——帮助用户理解智能体的决策边界。
  \item \textbf{Uncertainty quantification}: Explicit statements of confidence, with the factors driving uncertainty.
  \item \textbf{Uncertainty quantification（不确定性量化）}：明确给出置信度声明，并说明导致不确定性的因素。
\end{itemize}

\subsection{Showing Confidence Levels}
\subsection{展示置信水平}
\label{showing-confidence-levels}

Confidence indicators must be calibrated and meaningful:
置信度指标必须经过校准且具有实际意义：

\begin{itemize}
  \item \textbf{Verbal confidence}: Natural language expressions (``I’m fairly confident'', ``I’m not sure about this'') are more interpretable than numerical probabilities for most users.
  \item \textbf{Verbal confidence（言语置信度）}：对大多数用户而言，自然语言表达（“我相当确信”、“我不太确定这一点”）比数值概率更易理解。
  \item \textbf{Visual confidence}: Color coding (green/yellow/red), icon variants, or font weight can encode confidence without adding text.
  \item \textbf{Visual confidence（视觉置信度）}：颜色编码（绿/黄/红）、图标变体或字体粗细可在不增加文字的情况下编码置信度。
  \item \textbf{Confidence by claim}: For multi-claim responses, per-claim confidence indicators (e.g., inline footnotes) are more informative than a single response-level score.
  \item \textbf{Confidence by claim（逐条置信度）}：对于包含多条主张的响应，逐条置信度指示（例如内联脚注）比单一的整体响应分数信息量更大。
\end{itemize}

\subsection{Undo and Rollback Capabilities}
\subsection{撤销与回滚能力}
\label{undo-and-rollback-capabilities}

Every consequential agent action should be undoable where technically feasible:
在技术可行的情况下，每一项有重大影响的智能体操作都应可撤销：

\begin{itemize}
  \item \textbf{Action log with undo}: A chronological log of all agent actions with an ``Undo'' button for each reversible action.
  \item \textbf{Action log with undo（带撤销的操作日志）}：按时间顺序记录所有智能体操作，并为每个可逆操作提供“撤销”按钮。
  \item \textbf{Snapshot-based rollback}: For stateful tasks (e.g., code editing, document writing), periodic snapshots enable rollback to any prior state.
  \item \textbf{Snapshot-based rollback（基于快照的回滚）}：对于有状态的任务（如代码编辑、文档撰写），定期快照可回滚到任意先前状态。
  \item \textbf{Dry-run mode}: Before executing a plan, the agent can simulate it and show the predicted state changes, allowing the user to approve or modify before any real action is taken.
  \item \textbf{Dry-run mode（试运行模式）}：在执行计划之前，智能体可以模拟运行并显示预测的状态变化，允许用户在实际执行前批准或修改。
  \item \textbf{Graceful degradation}: When an undo is not possible (e.g., an email has been sent), the UI clearly communicates this and offers the best available alternative (e.g., sending a follow-up).
  \item \textbf{Graceful degradation（优雅降级）}：当无法撤销时（例如邮件已发送），UI明确告知用户，并提供最佳的可行替代方案（例如发送后续邮件）。
\end{itemize}

\subsection{Audit Trails in the UI}
\subsection{UI中的审计追踪}
\label{audit-trails-in-the-ui}

For enterprise and regulated use cases, audit trails are essential:
对于企业和受监管的使用场景，审计追踪至关重要：

\begin{itemize}
  \item \textbf{Immutable action log}: Every agent action, tool call, and human approval is logged with timestamp, user identity, and full parameters.
  \item \textbf{Immutable action log（不可变操作日志）}：每一次智能体操作、工具调用和人工审批均记录时间戳、用户身份和完整参数。
  \item \textbf{Exportable history}: The audit trail can be exported as JSON, CSV, or PDF for compliance reporting.
  \item \textbf{Exportable history（可导出的历史记录）}：审计追踪可导出为JSON、CSV或PDF格式，用于合规报告。
  \item \textbf{Diff views}: For document or code modifications, the audit trail includes before/after diffs.
  \item \textbf{Diff views（差异视图）}：对于文档或代码修改，审计追踪包含修改前后的差异对比。
  \item \textbf{Session replay}: The ability to replay an entire agent session, step by step, for debugging or compliance review.
  \item \textbf{Session replay（会话重放）}：能够逐步重放完整的智能体会话，用于调试或合规审查。
\end{itemize}

\subsection{Managing User Expectations}
\subsection{管理用户期望}
\label{managing-user-expectations}

Miscalibrated expectations are a primary source of user distrust. Agentic UIs should actively manage expectations:
期望失准是用户不信任的主要来源。智能体UI应主动管理期望：

\begin{itemize}
  \item \textbf{Capability disclosure}: Clear, accessible documentation of what the agent can and cannot do.
  \item \textbf{Capability disclosure（能力披露）}：清晰易懂地记录智能体能够做什么和不能做什么。
  \item \textbf{Limitation acknowledgment}: When the agent encounters a task outside its capabilities, it says so clearly rather than attempting and failing silently.
  \item \textbf{Limitation acknowledgment（局限性承认）}：当智能体遇到超出其能力的任务时，应明确告知，而不是尝试后无声失败。
  \item \textbf{Uncertainty communication}: Proactive communication of uncertainty, rather than waiting for the user to discover errors.
  \item \textbf{Uncertainty communication（不确定性沟通）}：主动沟通不确定性，而不是等待用户发现错误。
  \item \textbf{Consistent persona}: A consistent agent identity and communication style builds familiarity and predictability.
  \item \textbf{Consistent persona（一致的角色形象）}：一致的智能体身份和沟通风格可建立熟悉感和可预测性。
\end{itemize}

\begin{examplebox}[Trust-Building Through Transparency: A Case Study]
Consider an agent tasked with booking a flight. A low-trust UI presents: ``I’ve booked your flight. Confirmation: AA1234.'' A high-trust UI presents: (1) a summary of the search parameters used, (2) the alternatives considered and why this flight was selected, (3) the exact actions taken (API calls to the booking system), (4) the confirmation details with a link to the booking, (5) an undo option valid for the next 24 hours, and (6) a note about what the agent cannot do (e.g., ``I cannot modify this booking; you’ll need to call the airline directly''). The second UI takes more screen space but builds the user’s confidence that the agent acted correctly and gives them the information needed to verify and recover if needed.
\begin{examplebox}[通过透明度建立信任：一个案例研究]
设想一个负责预订航班的智能体。低信任度的UI显示：“我已为您预订了航班。确认号：AA1234。”高信任度的UI则展示：(1) 所使用的搜索参数摘要，(2) 考虑过的备选方案以及选择该航班的原因，(3) 执行的具体操作（对预订系统的API调用），(4) 包含预订链接的确认详情，(5) 未来24小时内有效的撤销选项，以及(6) 关于智能体不能做什么的说明（例如“我无法修改此预订；您需要直接联系航空公司”）。第二种UI占用更多屏幕空间，但能让用户确信智能体操作正确，并提供验证和必要时恢复所需的信息。
\end{examplebox}

\section{Implementation Example: A Full-Stack Agentic UI}
\section{实现示例：一个全栈智能体UI}
\label{subsec:ui-implementation}

We now present a concrete implementation example combining streaming, tool visualization, and approval gates in a Python/React stack. The backend uses FastAPI with LangGraph; the frontend uses React with the Vercel AI SDK patterns adapted for a custom backend.
我们现在展示一个具体的实现示例，它结合了流式传输、工具可视化和审批门控，采用Python/React技术栈。后端使用FastAPI与LangGraph；前端使用React，并适配Vercel AI SDK模式以支持自定义后端。

\subsection{Backend: FastAPI + LangGraph with Streaming and Approval Gates}
\subsection{后端：带流式传输和审批门控的FastAPI + LangGraph}
\label{backend-fastapi-langgraph-with-streaming-and-approval-gates}

\begin{lstlisting}[style=pythonstyle, caption={FastAPI backend with streaming and approval gates}]
# backend/main.py
import asyncio
import json
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool


app = FastAPI()


# -- Tool definitions ----------------------------------------------------------


@tool
def web_search(query: str) -> str:
    """Search the web for information."""
    return f"Search results for '{query}': [simulated results]"


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email. REQUIRES HUMAN APPROVAL."""
    return f"Email sent to {to} with subject '{subject}'"
\end{lstlisting}

```python
@tool
def read_file(path: str) -> str:
    """Read a file from the filesystem."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {path}"

# Tools requiring approval (Tier 3)
APPROVAL_REQUIRED_TOOLS = {"send_email"}


# -- Approval gate store (in-memory; use Redis in production) ------------------


approval_store: dict[str, asyncio.Event] = {}
approval_results: dict[str, dict] = {}


# -- LLM setup -----------------------------------------------------------------


llm = ChatOpenAI(model="gpt-4o", streaming=True)
tools = [web_search, send_email, read_file]
llm_with_tools = llm.bind_tools(tools)


def should_request_approval(tool_name: str) -> bool:
    return tool_name in APPROVAL_REQUIRED_TOOLS


# -- Streaming endpoint --------------------------------------------------------


async def agent_stream(
    session_id: str,
    user_message: str,
) -> AsyncGenerator[str, None]:
    """Stream agent events as SSE."""

    def sse(event_type: str, data: dict) -> str:
        return f"data: {json.dumps({'type': event_type, **data})}\n\n"

    yield sse("status", {"message": "Agent starting..."})

    # Simulate multi-step agent execution
    steps = [
        ("thinking", {"content": "Analyzing the request..."}),
        ("tool_call", {
            "tool": "web_search",
            "input": {"query": user_message},
            "tier": 1,  # Auto-approve
        }),
        ("tool_result", {
            "tool": "web_search",
            "output": f"Results for: {user_message}",
            "duration_ms": 342,
        }),
    ]

    for event_type, data in steps:
        await asyncio.sleep(0.5)  # Simulate processing time
        yield sse(event_type, data)

    # Simulate a Tier 3 action requiring approval
    approval_id = f"{session_id}_email_001"
    approval_event = asyncio.Event()
    approval_store[approval_id] = approval_event

    yield sse("approval_required", {
        "approval_id": approval_id,
        "tool": "send_email",
        "tier": 3,
        "risk": "irreversible",
        "action_summary": "Send summary email to user@example.com",
        "parameters": {
            "to": "user@example.com",
            "subject": f"Research results: {user_message}",
            "body": "Here are the findings...",
        },
    })

    # Wait for human approval (timeout after 5 minutes)
    try:
        await asyncio.wait_for(approval_event.wait(), timeout=300)
        result = approval_results.get(approval_id, {})

        if result.get("approved"):
            yield sse("tool_call", {
                "tool": "send_email",
                "input": result.get("parameters", {}),
                "tier": 3,
                "approved_by": "human",
            })
            await asyncio.sleep(0.3)
            yield sse("tool_result", {
                "tool": "send_email",
                "output": "Email sent successfully",
                "duration_ms": 128,
            })
        else:
            yield sse("action_rejected", {
                "tool": "send_email",
                "reason": result.get("reason", "User rejected"),
            })
    except asyncio.TimeoutError:
        yield sse("approval_timeout", {
            "approval_id": approval_id,
            "message": "Approval timed out; action skipped",
        })

    # Final response
    yield sse("token", {"content": "I've completed the research. "})
    yield sse("token", {"content": "Here's a summary of what I found..."})
    yield sse("done", {"total_tokens": 847, "duration_ms": 2341})


@app.get("/chat/stream")
async def chat_stream(session_id: str, message: str):
    return StreamingResponse(
        agent_stream(session_id, message),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


class ApprovalRequest(BaseModel):
    approval_id: str
    approved: bool
    parameters: dict | None = None
    reason: str | None = None


@app.post("/chat/approve")
async def handle_approval(req: ApprovalRequest):
    if req.approval_id not in approval_store:
        raise HTTPException(status_code=404, detail="Approval not found")
    approval_results[req.approval_id] = {
        "approved": req.approved,
        "parameters": req.parameters,
        "reason": req.reason,
    }
    approval_store[req.approval_id].set()
    return {"status": "ok"}
```

```python
@tool
def read_file(path: str) -> str:
    """从文件系统读取文件。"""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {path}"

# 需要批准的工具（第3级）
APPROVAL_REQUIRED_TOOLS = {"send_email"}


# -- 批准门存储（内存中；生产环境使用Redis）------------------


approval_store: dict[str, asyncio.Event] = {}
approval_results: dict[str, dict] = {}


# -- LLM设置-----------------------------------------------------------------


llm = ChatOpenAI(model="gpt-4o", streaming=True)
tools = [web_search, send_email, read_file]
llm_with_tools = llm.bind_tools(tools)


def should_request_approval(tool_name: str) -> bool:
    return tool_name in APPROVAL_REQUIRED_TOOLS


# -- 流式端点--------------------------------------------------------


async def agent_stream(
    session_id: str,
    user_message: str,
) -> AsyncGenerator[str, None]:
    """以SSE格式流式传输智能体事件。"""

    def sse(event_type: str, data: dict) -> str:
        return f"data: {json.dumps({'type': event_type, **data})}\n\n"

    yield sse("status", {"message": "Agent starting..."})

    # 模拟多步智能体执行
    steps = [
        ("thinking", {"content": "Analyzing the request..."}),
        ("tool_call", {
            "tool": "web_search",
            "input": {"query": user_message},
            "tier": 1,  # 自动批准
        }),
        ("tool_result", {
            "tool": "web_search",
            "output": f"Results for: {user_message}",
            "duration_ms": 342,
        }),
    ]

    for event_type, data in steps:
        await asyncio.sleep(0.5)  # 模拟处理时间
        yield sse(event_type, data)

    # 模拟需要批准的第3级操作
    approval_id = f"{session_id}_email_001"
    approval_event = asyncio.Event()
    approval_store[approval_id] = approval_event

    yield sse("approval_required", {
        "approval_id": approval_id,
        "tool": "send_email",
        "tier": 3,
        "risk": "irreversible",
        "action_summary": "Send summary email to user@example.com",
        "parameters": {
            "to": "user@example.com",
            "subject": f"Research results: {user_message}",
            "body": "Here are the findings...",
        },
    })

    # 等待人工批准（超时5分钟）
    try:
        await asyncio.wait_for(approval_event.wait(), timeout=300)
        result = approval_results.get(approval_id, {})

        if result.get("approved"):
            yield sse("tool_call", {
                "tool": "send_email",
                "input": result.get("parameters", {}),
                "tier": 3,
                "approved_by": "human",
            })
            await asyncio.sleep(0.3)
            yield sse("tool_result", {
                "tool": "send_email",
                "output": "Email sent successfully",
                "duration_ms": 128,
            })
        else:
            yield sse("action_rejected", {
                "tool": "send_email",
                "reason": result.get("reason", "User rejected"),
            })
    except asyncio.TimeoutError:
        yield sse("approval_timeout", {
            "approval_id": approval_id,
            "message": "Approval timed out; action skipped",
        })

    # 最终响应
    yield sse("token", {"content": "I've completed the research. "})
    yield sse("token", {"content": "Here's a summary of what I found..."})
    yield sse("done", {"total_tokens": 847, "duration_ms": 2341})


@app.get("/chat/stream")
async def chat_stream(session_id: str, message: str):
    return StreamingResponse(
        agent_stream(session_id, message),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


class ApprovalRequest(BaseModel):
    approval_id: str
    approved: bool
    parameters: dict | None = None
    reason: str | None = None


@app.post("/chat/approve")
async def handle_approval(req: ApprovalRequest):
    if req.approval_id not in approval_store:
        raise HTTPException(status_code=404, detail="Approval not found")
    approval_results[req.approval_id] = {
        "approved": req.approved,
        "parameters": req.parameters,
        "reason": req.reason,
    }
    approval_store[req.approval_id].set()
    return {"status": "ok"}
```

## Frontend: React with Streaming and Tool Visualization
## 前端：带有流式传输和工具可视化的React

```typescript
// frontend/AgentChat.tsx
import { useState, useEffect, useRef } from 'react';


// -- Types ---------------------------------------------------------------------


type AgentEvent =
  | { type: 'status'; message: string }
  | { type: 'thinking'; content: string }
  | { type: 'token'; content: string }
  | { type: 'tool_call'; tool: string; input: object; tier: number }
  | { type: 'tool_result'; tool: string; output: string; duration_ms: number }
  | { type: 'approval_required'; approval_id: string; tool: string;
      tier: number; risk: string; action_summary: string; parameters: object }
  | { type: 'action_rejected'; tool: string; reason: string }
  | { type: 'done'; total_tokens: number; duration_ms: number };


// -- Tool Card Component -------------------------------------------------------


function ToolCard({ event }: { event: AgentEvent & { type: 'tool_call' } }) {
  const [expanded, setExpanded] = useState(false);
  const tierColors = { 1: '#22c55e', 2: '#f59e0b', 3: '#ef4444' };
  const color = tierColors[event.tier as keyof typeof tierColors] || '#6b7280';

  return (
    <div style={{ border: `1px solid ${color}`, borderRadius: 8, padding: 8,
                  margin: '4px 0', fontSize: 13 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ color, fontWeight: 600 }}>[gear] {event.tool}</span>
        <span style={{ color: '#6b7280', fontSize: 11 }}>
          Tier {event.tier} . {event.tier === 1 ? 'Auto' : 'Approved'}
        </span>
        <button onClick={() => setExpanded(!expanded)}
                style={{ marginLeft: 'auto', fontSize: 11 }}>
          {expanded ? 'Hide' : 'Details'}
        </button>
      </div>
      {expanded && (
        <pre style={{ marginTop: 8, fontSize: 11, background: '#f3f4f6',
                      padding: 8, borderRadius: 4, overflow: 'auto' }}>
          {JSON.stringify(event.input, null, 2)}
        </pre>
      )}
    </div>
  );
}


// -- Approval Gate Component ---------------------------------------------------
```

```typescript
// 前端/AgentChat.tsx
import { useState, useEffect, useRef } from 'react';


// -- 类型---------------------------------------------------------------------


type AgentEvent =
  | { type: 'status'; message: string }
  | { type: 'thinking'; content: string }
  | { type: 'token'; content: string }
  | { type: 'tool_call'; tool: string; input: object; tier: number }
  | { type: 'tool_result'; tool: string; output: string; duration_ms: number }
  | { type: 'approval_required'; approval_id: string; tool: string;
      tier: number; risk: string; action_summary: string; parameters: object }
  | { type: 'action_rejected'; tool: string; reason: string }
  | { type: 'done'; total_tokens: number; duration_ms: number };


// -- 工具卡片组件-------------------------------------------------------


function ToolCard({ event }: { event: AgentEvent & { type: 'tool_call' } }) {
  const [expanded, setExpanded] = useState(false);
  const tierColors = { 1: '#22c55e', 2: '#f59e0b', 3: '#ef4444' };
  const color = tierColors[event.tier as keyof typeof tierColors] || '#6b7280';

  return (
    <div style={{ border: `1px solid ${color}`, borderRadius: 8, padding: 8,
                  margin: '4px 0', fontSize: 13 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ color, fontWeight: 600 }}>[gear] {event.tool}</span>
        <span style={{ color: '#6b7280', fontSize: 11 }}>
          Tier {event.tier} . {event.tier === 1 ? 'Auto' : 'Approved'}
        </span>
        <button onClick={() => setExpanded(!expanded)}
                style={{ marginLeft: 'auto', fontSize: 11 }}>
          {expanded ? 'Hide' : 'Details'}
        </button>
      </div>
      {expanded && (
        <pre style={{ marginTop: 8, fontSize: 11, background: '#f3f4f6',
                      padding: 8, borderRadius: 4, overflow: 'auto' }}>
          {JSON.stringify(event.input, null, 2)}
        </pre>
      )}
    </div>
  );
}


// -- 批准门组件-------------------------------------------------------
```

```markdown
\begin{lstlisting}
function ApprovalGate({
  event,
  onDecision,
}: {
  event: AgentEvent & { type: 'approval_required' };
  onDecision: (approved: boolean, params?: object) => void;
}) {
  const riskColors = { reversible: '#22c55e', 'hard-to-undo': '#f59e0b',
                       irreversible: '#ef4444' };
  const riskColor = riskColors[event.risk as keyof typeof riskColors] || '#6b7280';

  return (
    <div style={{ border: `2px solid ${riskColor}`, borderRadius: 8,
                  padding: 16, margin: '8px 0', background: '#fef9f0' }}>
      <div style={{ fontWeight: 700, color: riskColor, marginBottom: 8 }}>
        [!] Approval Required: {event.tool}
      </div>
      <div style={{ marginBottom: 8 }}>{event.action_summary}</div>
      <div style={{ fontSize: 12, color: '#6b7280', marginBottom: 12 }}>
        Risk level: <span style={{ color: riskColor }}>{event.risk}</span>
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <button
          onClick={() => onDecision(true, event.parameters)}
          style={{ background: '#22c55e', color: 'white', border: 'none',
                   borderRadius: 6, padding: '8px 16px', cursor: 'pointer' }}>
          [OK] Approve
        </button>
        <button
          onClick={() => onDecision(false)}
          style={{ background: '#ef4444', color: 'white', border: 'none',
                   borderRadius: 6, padding: '8px 16px', cursor: 'pointer' }}>
          [X] Reject
        </button>
      </div>
    </div>
  );
}

// -- Main Chat Component -------------------------------------------------------


export function AgentChat() {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [response, setResponse] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [input, setInput] = useState('');
  const sessionId = useRef(`session_${Date.now()}`);

  const sendMessage = async () => {
    if (!input.trim() || isStreaming) return;
    setEvents([]);
    setResponse('');
    setIsStreaming(true);

    const url = `/chat/stream?session_id=${sessionId.current}`
              + `&message=${encodeURIComponent(input)}`;
    const es = new EventSource(url);

    es.onmessage = (e) => {
      const event: AgentEvent = JSON.parse(e.data);
      if (event.type === 'token') {
        setResponse(prev => prev + event.content);
      } else if (event.type === 'done') {
        setIsStreaming(false);
        es.close();
      } else {
        setEvents(prev => [...prev, event]);
      }
    };

    es.onerror = () => { setIsStreaming(false); es.close(); };
    setInput('');
  };

  const handleApproval = async (
    approvalId: string,
    approved: boolean,
    parameters?: object,
  ) => {
    await fetch('/chat/approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approval_id: approvalId, approved, parameters }),
    });
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: 16 }}>
      <div style={{ minHeight: 400, border: '1px solid #e5e7eb',
                    borderRadius: 8, padding: 16, marginBottom: 16 }}>
        {events.map((event, i) => {
          if (event.type === 'tool_call')
            return <ToolCard key={i} event={event} />;
          if (event.type === 'approval_required')
            return (
              <ApprovalGate key={i} event={event}
                onDecision={(approved, params) =>
                  handleApproval(event.approval_id, approved, params)} />
            );
          if (event.type === 'status' || event.type === 'thinking')
            return (
              <div key={i} style={{ color: '#6b7280', fontSize: 12,
                                    fontStyle: 'italic', margin: '4px 0' }}>
                {event.type === 'thinking' ? event.content : event.message}
              </div>
            );
          return null;
        })}
        {response && (
          <div style={{ marginTop: 8, lineHeight: 1.6 }}>
            {response}
            {isStreaming && <span className="cursor-blink">|</span>}
          </div>
        )}
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="Ask the agent..."
          style={{ flex: 1, padding: '8px 12px', borderRadius: 6,
                   border: '1px solid #d1d5db', fontSize: 14 }}
        />
        <button onClick={sendMessage} disabled={isStreaming}
                style={{ padding: '8px 16px', background: '#3b82f6',
                         color: 'white', border: 'none', borderRadius: 6,
                         cursor: isStreaming ? 'not-allowed' : 'pointer' }}>
          {isStreaming ? 'Running...' : 'Send'}
        </button>
      </div>
    </div>
  );
}
\end{lstlisting}
\begin{lstlisting}
function ApprovalGate({
  event,
  onDecision,
}: {
  event: AgentEvent & { type: 'approval_required' };
  onDecision: (approved: boolean, params?: object) => void;
}) {
  const riskColors = { reversible: '#22c55e', 'hard-to-undo': '#f59e0b',
                       irreversible: '#ef4444' };
  const riskColor = riskColors[event.risk as keyof typeof riskColors] || '#6b7280';

  return (
    <div style={{ border: `2px solid ${riskColor}`, borderRadius: 8,
                  padding: 16, margin: '8px 0', background: '#fef9f0' }}>
      <div style={{ fontWeight: 700, color: riskColor, marginBottom: 8 }}>
        [!] Approval Required: {event.tool}
      </div>
      <div style={{ marginBottom: 8 }}>{event.action_summary}</div>
      <div style={{ fontSize: 12, color: '#6b7280', marginBottom: 12 }}>
        Risk level: <span style={{ color: riskColor }}>{event.risk}</span>
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <button
          onClick={() => onDecision(true, event.parameters)}
          style={{ background: '#22c55e', color: 'white', border: 'none',
                   borderRadius: 6, padding: '8px 16px', cursor: 'pointer' }}>
          [OK] Approve
        </button>
        <button
          onClick={() => onDecision(false)}
          style={{ background: '#ef4444', color: 'white', border: 'none',
                   borderRadius: 6, padding: '8px 16px', cursor: 'pointer' }}>
          [X] Reject
        </button>
      </div>
    </div>
  );
}

// -- 主聊天组件 -------------------------------------------------------


export function AgentChat() {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [response, setResponse] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [input, setInput] = useState('');
  const sessionId = useRef(`session_${Date.now()}`);

  const sendMessage = async () => {
    if (!input.trim() || isStreaming) return;
    setEvents([]);
    setResponse('');
    setIsStreaming(true);

    const url = `/chat/stream?session_id=${sessionId.current}`
              + `&message=${encodeURIComponent(input)}`;
    const es = new EventSource(url);

    es.onmessage = (e) => {
      const event: AgentEvent = JSON.parse(e.data);
      if (event.type === 'token') {
        setResponse(prev => prev + event.content);
      } else if (event.type === 'done') {
        setIsStreaming(false);
        es.close();
      } else {
        setEvents(prev => [...prev, event]);
      }
    };

    es.onerror = () => { setIsStreaming(false); es.close(); };
    setInput('');
  };

  const handleApproval = async (
    approvalId: string,
    approved: boolean,
    parameters?: object,
  ) => {
    await fetch('/chat/approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approval_id: approvalId, approved, parameters }),
    });
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: 16 }}>
      <div style={{ minHeight: 400, border: '1px solid #e5e7eb',
                    borderRadius: 8, padding: 16, marginBottom: 16 }}>
        {events.map((event, i) => {
          if (event.type === 'tool_call')
            return <ToolCard key={i} event={event} />;
          if (event.type === 'approval_required')
            return (
              <ApprovalGate key={i} event={event}
                onDecision={(approved, params) =>
                  handleApproval(event.approval_id, approved, params)} />
            );
          if (event.type === 'status' || event.type === 'thinking')
            return (
              <div key={i} style={{ color: '#6b7280', fontSize: 12,
                                    fontStyle: 'italic', margin: '4px 0' }}>
                {event.type === 'thinking' ? event.content : event.message}
              </div>
            );
          return null;
        })}
        {response && (
          <div style={{ marginTop: 8, lineHeight: 1.6 }}>
            {response}
            {isStreaming && <span className="cursor-blink">|</span>}
          </div>
        )}
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="Ask the agent..."
          style={{ flex: 1, padding: '8px 12px', borderRadius: 6,
                   border: '1px solid #d1d5db', fontSize: 14 }}
        />
        <button onClick={sendMessage} disabled={isStreaming}
                style={{ padding: '8px 16px', background: '#3b82f6',
                         color: 'white', border: 'none', borderRadius: 6,
                         cursor: isStreaming ? 'not-allowed' : 'pointer' }}>
          {isStreaming ? 'Running...' : 'Send'}
        </button>
      </div>
    </div>
  );
}
\end{lstlisting}

\begin{examplebox}[What This Implementation Demonstrates]
The code above illustrates several key agentic UI patterns working together:

\begin{itemize}
  \item \textbf{SSE streaming}: The backend streams events of different types (status, thinking, tool calls, tokens) over a single HTTP connection.
  \item \textbf{Typed event protocol}: A discriminated union of event types enables the frontend to render each event appropriately.
  \item \textbf{Tool visualization}: \texttt{ToolCard} renders tool calls with tier indicators and expandable input details.
  \item \textbf{Approval gates}: \texttt{ApprovalGate} blocks the stream and waits for human input before the agent proceeds with irreversible actions.
  \item \textbf{Async approval}: The backend uses \texttt{asyncio.Event} to pause the stream while waiting for the frontend's approval POST request, cleanly decoupling the approval UI from the streaming logic.
\end{itemize}
\end{examplebox}
\begin{examplebox}[此实现所展示的要点]
上述代码展示了几个关键智能体UI（agentic UI）模式协同工作：

\begin{itemize}
  \item \textbf{SSE streaming（SSE流式传输）}：后端通过单个HTTP连接流式传输不同类型的事件（状态、思考、工具调用、令牌）。
  \item \textbf{Types event protocol（类型化事件协议）}：事件类型的判别联合使得前端能够适当地渲染每个事件。
  \item \textbf{Tool visualization（工具可视化）}：\texttt{ToolCard} 使用层级指示器和可展开的输入详情来渲染工具调用。
  \item \textbf{Approval gates（审批门）}：\texttt{ApprovalGate} 阻塞流式传输，在智能体执行不可逆操作前等待人工输入。
  \item \textbf{Async approval（异步审批）}：后端使用 \texttt{asyncio.Event} 暂停流式传输，同时等待前端的审批 POST 请求，将审批UI与流式传输逻辑干净地解耦。
\end{itemize}
\end{examplebox}

\section{Summary}
\label{subsec:ui-summary}
\section{摘要}
\label{subsec:ui-summary}

Agentic UI frameworks represent a new frontier in human-computer interaction, demanding a rethinking of interface design from first principles. The key insights from this section are:
智能体UI框架代表了人机交互的新前沿，需要从第一性原理重新思考界面设计。本节的关键洞察如下：

\begin{enumerate}
  \item \textbf{Paradigm selection matters}: The appropriate UI paradigm (chat, canvas, workflow, dashboard, collaborative, autonomous) depends on task structure, required human involvement, and output type. Most production systems combine multiple paradigms.
  \item \textbf{Transparency is non-negotiable}: Users cannot trust what they cannot see. Thought display, tool visualization, and context panels are not optional features---they are the foundation of trustworthy agentic systems.
  \item \textbf{Streaming is the baseline}: Users expect to see agents work in real time. Token streaming, tool call streaming, and multi-agent streaming are table-stakes capabilities.
  \item \textbf{Approval gates must be tiered}: Flat approval policies (approve everything or approve nothing) fail in practice. Tiered policies that auto-approve safe actions and gate dangerous ones maintain oversight without creating bottlenecks.
  \item \textbf{Generative UI is the frontier}: The ability for LLMs to generate not just text but UI components---charts, forms, maps, widgets---enables interfaces that adapt to content rather than forcing content into a fixed template.
  \item \textbf{Trust is earned through consistency and recoverability}: Undo capabilities, audit trails, and calibrated confidence indicators are as important as raw capability for building user trust.
\end{enumerate}
\begin{enumerate}
  \item \textbf{Paradigm selection（范式选择）至关重要}：适当的UI范式（聊天、画布、工作流、仪表盘、协作、自主）取决于任务结构、所需的人类参与程度以及输出类型。大多数生产系统会组合多种范式。
  \item \textbf{Transparency（透明性）不可妥协}：用户无法信任他们看不见的东西。思考展示、工具可视化和上下文面板并非可选功能——它们是可信智能体系统的基础。
  \item \textbf{Streaming（流式传输）是基线}：用户期望看到智能体实时工作。令牌流式传输、工具调用流式传输和多智能体流式传输是必备能力。
  \item \textbf{审批门必须分层}：扁平化的审批策略（全部批准或全部拒绝）在实践中会失败。自动批准安全操作并阻断危险操作的分层策略能在保持监督的同时避免瓶颈。
  \item \textbf{Generative UI（生成式UI）是前沿}：LLM不仅能生成文本，还能生成UI组件（图表、表单、地图、小部件），这使得界面能够适应内容，而非将内容强行塞入固定模板。
  \item \textbf{信任通过一致性和可恢复性赢得}：撤销能力、审计轨迹和校准后的置信度指标对于建立用户信任而言与原始能力同等重要。
\end{enumerate}

\begin{keybox}[Design Principle: The Agent as a Transparent Collaborator]
The north star for agentic UI design is the \emph{transparent collaborator}: an agent whose actions are always visible, whose reasoning is always accessible, whose mistakes are always recoverable, and whose capabilities and limitations are always clear. Every UI decision should be evaluated against this standard.
\end{keybox}
\begin{keybox}[设计原则：智能体作为透明协作伙伴]
智能体UI设计的北极星是 \emph{transparent collaborator（透明协作伙伴）}：一个行为始终可见、推理始终可查、错误始终可恢复、能力与局限始终清晰的智能体。每一个UI决策都应以此标准来评估。
\end{keybox}
```

The frameworks and patterns described in this section---Vercel AI SDK, Chainlit, Gradio, Streamlit, LangGraph Studio---provide the building blocks. The challenge for practitioners is to combine them thoughtfully, guided by the specific needs of their users and the specific risks of their domain.
本节描述的框架和模式——Vercel AI SDK、Chainlit、Gradio、Streamlit、LangGraph Studio——提供了构建模块。实践者面临的挑战是，根据用户的具体需求和所在领域的特定风险，深思熟虑地组合这些工具。

# \part{Assessment \& Reference}
# 评估与参考