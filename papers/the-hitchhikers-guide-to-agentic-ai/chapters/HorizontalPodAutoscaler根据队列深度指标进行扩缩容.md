# HorizontalPodAutoscaler 根据队列深度指标进行扩缩容
hpa_config = {
    "apiVersion": "autoscaling/v2",
    "kind": "HorizontalPodAutoscaler",
    "metadata": {"name": "research-agent-hpa", "namespace": "agents"},
    "spec": {
        "scaleTargetRef": {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "name": "research-agent",
        },
        "minReplicas": 2,
        "maxReplicas": 20,
        "metrics": [{
            "type": "External",
            "external": {
                "metric": {"name": "agent_task_queue_depth"},
                "target": {"type": "AverageValue", "averageValue": "10"},
            }
        }]
    }
}
```

## \begin{warningbox}[Production Checklist]
## \begin{warningbox}[生产检查清单]

Before deploying an agent to production, verify:

在将代理部署到生产环境之前，请确认：

\begin{itemize}
  \item All tools have retry logic and error handling
  \item 所有工具具备重试逻辑和错误处理
  \item Maximum iteration limits are enforced
  \item 强制实施最大迭代次数限制
  \item Sensitive data is not logged in traces
  \item 跟踪中不记录敏感数据
  \item Rate limiting is configured per tenant
  \item 按租户配置速率限制
  \item Checkpointing is enabled for long-running tasks
  \item 为长时间运行的任务启用检查点
  \item Behavioral tests pass (no harmful outputs)
  \item 行为测试通过（无有害输出）
  \item Cost and latency bounds are validated
  \item 验证成本和延迟边界
  \item Rollback procedure is documented and tested
  \item 回滚流程已记录并测试
  \item On-call runbook covers common failure modes
  \item 值班运行手册涵盖常见故障模式
\end{itemize}
\end{warningbox}


## \section{Summary}
## \section{总结}
\label{subsec:agent-dev-summary}


Agent development frameworks have matured significantly, providing structured solutions to the engineering challenges of building production-grade AI agents. The key takeaways from this section are:

代理开发框架已经显著成熟，为构建生产级AI代理的工程挑战提供了结构化解决方案。本节的关键要点如下：

\begin{enumerate}
  \item \textbf{Framework selection matters}: Different frameworks optimize for different concerns. LangGraph excels at complex, controllable workflows; AutoGen at multi-agent collaboration; CrewAI at role-based simplicity; DSPy at automated optimization.
  \item \textbf{框架选择很重要}: 不同框架针对不同关注点进行优化。LangGraph在复杂、可控的工作流方面表现出色；AutoGen在多代理协作方面；CrewAI在基于角色的简洁性方面；DSPy在自动化优化方面。
  \item \textbf{Testing is non-negotiable}: The non-deterministic nature of LLM-based agents makes comprehensive testing---unit, integration, behavioral, and performance---essential for production reliability.
  \item \textbf{测试是不可妥协的}: 基于LLM的代理的非确定性特性使得全面测试——单元测试、集成测试、行为测试和性能测试——对于生产环境的可靠性至关重要。
  \item \textbf{Observability enables iteration}: Without detailed traces of agent execution, diagnosing failures and improving performance is guesswork. Invest in observability infrastructure early.
  \item \textbf{可观测性赋能迭代}: 没有代理执行的详细跟踪，诊断故障和改进性能就变成了猜测。尽早投资可观测性基础设施。
  \item \textbf{Async execution is the norm}: Production agents are long-running processes that require queue-based execution, checkpointing, and graceful failure handling.
  \item \textbf{异步执行是常态}: 生产环境中的代理是长时间运行的进程，需要基于队列的执行、检查点和优雅的失败处理。
  \item \textbf{Cost management is critical}: LLM API costs scale with usage. Model routing, caching, and early termination can reduce costs by 50--90\% without sacrificing quality.
  \item \textbf{成本管理至关重要}: LLM API成本随使用量增长。模型路由、缓存和提前终止可以在不牺牲质量的情况下将成本降低50-90%。
  \item \textbf{The lifecycle is iterative}: Agent development is not a one-time effort. Continuous monitoring, failure analysis, and improvement are essential for maintaining performance as the world changes.
  \item \textbf{生命周期是迭代的}: 代理开发不是一次性的工作。随着世界的变化，持续监控、故障分析和改进对于保持性能至关重要。
\end{enumerate}


The field is evolving rapidly, with new frameworks, tools, and best practices emerging regularly. The principles covered in this section---explicit state management, comprehensive testing, deep observability, and systematic iteration---provide a stable foundation regardless of which specific tools are in vogue.

该领域正在快速发展，新的框架、工具和最佳实践不断涌现。本节涵盖的原则——显式状态管理、全面测试、深度可观测性和系统迭代——无论当前流行哪种具体工具，都提供了一个稳定的基础。
---

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
