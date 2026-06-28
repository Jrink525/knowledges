```markdown
\chapter{Agent Design Patterns}
\label{sec:agent-design-patterns}

\chapter{Agent设计模式}
\label{sec:agent-design-patterns}

Building effective agents requires more than a powerful model and a set of tools. The \emph{architecture}---how the LLM is orchestrated, how tasks are decomposed, and how control flows between components---determines whether an agent is reliable, debuggable, and cost-effective. This chapter presents the canonical design patterns that have emerged from production deployments at Anthropic, OpenAI, Google, and the open-source community.

构建有效的Agent不仅仅需要强大的模型和一组工具。\emph{架构}——即LLM如何编排、任务如何分解、组件之间的控制流如何流动——决定了Agent是否可靠、可调试且具有成本效益。本章介绍了从Anthropic、OpenAI、Google和开源社区的生产部署中涌现出的经典设计模式。

\begin{intuitionbox}[When to Use Agents vs. Workflows]
Not every task requires an autonomous agent. The key distinction:

\begin{intuitionbox}[何时使用Agent vs. 工作流]
并非每个任务都需要自主Agent。关键区别在于：

\begin{itemize}
  \item \textbf{Workflows}: Predefined control flow, LLM calls at specific steps. Predictable, testable, cheaper. Use when the task structure is known.
  \item \textbf{Agents}: LLM dynamically decides what to do next. Flexible, handles novel situations. Use when tasks require adaptive decision-making.
\end{itemize}

\begin{itemize}
  \item \textbf{工作流（Workflows）}：预定义的控制流，在特定步骤进行LLM调用。可预测、可测试、成本更低。当任务结构已知时使用。
  \item \textbf{Agent（Agents）}：LLM动态决定下一步做什么。灵活，处理新情况。当任务需要自适应决策时使用。
\end{itemize}

\textbf{Start with workflows.} Graduate to agents only when the task genuinely requires dynamic routing or open-ended exploration.
\end{intuitionbox}

\textbf{从工作流开始。}只有当任务确实需要动态路由或开放式探索时，才升级到Agent。
\end{intuitionbox}

\section{Workflow Patterns}
\label{workflow-patterns}

\section{工作流模式（Workflow Patterns）}
\label{workflow-patterns}

These patterns---adapted from Anthropic’s taxonomy of agentic building blocks~\cite{anthropic2024buildingagents}---use LLMs within a \emph{predefined} control flow. The system (not the model) decides the execution order.

这些模式改编自Anthropic的Agent构建模块分类法~\cite{anthropic2024buildingagents}，它们在\emph{预定义}的控制流中使用LLM。由系统（而非模型）决定执行顺序。

\subsection{Prompt Chaining}
\label{prompt-chaining}

\subsection{提示链（Prompt Chaining）}
\label{prompt-chaining}

The simplest pattern: break a complex task into a fixed sequence of LLM calls, piping the result of one call as context into the next. Validation gates between steps catch errors early before they propagate downstream.

最简单的模式：将复杂任务分解为固定序列的LLM调用，将一次调用的结果作为上下文传递到下一次调用。步骤之间的验证门控在错误向下游传播之前及早捕获它们。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_060_fig60.png}
\caption{Prompt chaining with quality gates. Each step is a separate LLM call. Gates can be LLM-based or programmatic.}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_060_fig60.png}
\caption{带有质量门控的提示链。每一步都是一个独立的LLM调用。门控可以是基于LLM的或程序化的。}
\end{figure}

\textbf{When to use}: Tasks that are naturally sequential---content generation, data transformation, multi-stage analysis.

\textbf{何时使用}：自然顺序的任务——内容生成、数据转换、多阶段分析。

\textbf{Key advantage}: Each step can use a different prompt, model, or temperature. Intermediate results are inspectable and debuggable.

\textbf{关键优势}：每一步可以使用不同的提示、模型或温度。中间结果可检查、可调试。

\subsection{Routing}
\label{routing}

\subsection{路由（Routing）}
\label{routing}

A classifier (LLM or traditional) examines the input and dispatches to a specialized handler.

分类器（LLM或传统方法）检查输入并将其分派到专门的处理器。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_061_fig61.png}
\caption{Routing pattern: input is classified once, then handled by a specialist.}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_061_fig61.png}
\caption{路由模式：输入被分类一次，然后由专门处理器处理。}
\end{figure}

\textbf{When to use}: Distinct task types with different optimal prompts, tools, or models. Customer support triage, multi-modal input handling.

\textbf{何时使用}：具有不同最优提示、工具或模型的截然不同的任务类型。例如客户支持分类、多模态输入处理。

\subsection{Parallelization}
\label{parallelization}

\subsection{并行化（Parallelization）}
\label{parallelization}

Multiple LLM calls run concurrently, with a programmatic layer combining their outputs. Two sub-patterns emerge:

多个LLM调用并发运行，由程序化层合并它们的输出。有两种子模式：

\begin{itemize}
  \item \textbf{Sectioning (fan-out)}: Partition the input into disjoint chunks and process each independently---e.g., run security, performance, and style checks on a codebase simultaneously.
  \item \textbf{Voting (redundancy)}: Issue the same prompt $N$ times with different seeds or temperatures, then select the best result via majority vote~\cite{wang2022selfconsistency}, reward-model scoring, or LLM-as-judge.
\end{itemize}

\begin{itemize}
  \item \textbf{分段（Sectioning，扇出）}：将输入划分为不相交的块，并独立处理每个块——例如，同时对代码库运行安全、性能和风格检查。
  \item \textbf{投票（Voting，冗余）}：使用不同的种子或温度发出相同的提示 $N$ 次，然后通过多数投票~\cite{wang2022selfconsistency}、奖励模型评分或LLM作为评判员来选择最佳结果。
\end{itemize}

\begin{examplebox}[Parallelization Example: Code Review]
\begin{enumerate}
  \item \textbf{Parallel calls}: Security review $\|$ Performance review $\|$ Style review
  \item \textbf{Aggregation}: Merge all findings, deduplicate, rank by severity
\end{enumerate}

\begin{examplebox}[并行化示例：代码审查]
\begin{enumerate}
  \item \textbf{并行调用}：安全审查 $\|$ 性能审查 $\|$ 风格审查
  \item \textbf{聚合}：合并所有发现，去重，按严重性排序
\end{enumerate}

Latency = $\max$(individual calls) rather than $\sum$(individual calls).
\end{examplebox}

延迟 = $\max$（单个调用）而非 $\sum$（单个调用）。
\end{examplebox}

\subsection{Orchestrator-Workers}
\label{orchestrator-workers}

\subsection{编排器-工作者（Orchestrator-Workers）}
\label{orchestrator-workers}

Here the LLM itself decides how to split the work. An orchestrator model analyzes the task, produces a plan of subtasks, dispatches each subtask to a worker LLM (potentially with different prompts or tools), and finally merges their outputs into a coherent result. The key difference from parallelization is that the decomposition logic is model-generated, not hard-coded.

这里，LLM自己决定如何拆分工作。编排器模型分析任务，生成子任务计划，将每个子任务分派给工作者LLM（可能使用不同的提示或工具），最后将它们的输出合并成一个连贯的结果。与并行化的关键区别在于，分解逻辑是由模型生成的，而不是硬编码的。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_062_fig62.png}
\caption{Orchestrator-workers: the LLM decides how to decompose the task and synthesizes worker results.}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_062_fig62.png}
\caption{编排器-工作者：LLM决定如何分解任务并综合工作者结果。}
\end{figure}

\textbf{When to use}: Open-ended problems where the number and nature of subtasks cannot be enumerated at design time---e.g., ``refactor this codebase'' requires first understanding the dependency graph before deciding which files to modify.

\textbf{何时使用}：开放性问题，其中子任务的数量和性质在设计时无法枚举——例如，“重构这个代码库”需要先理解依赖关系图，然后才能决定修改哪些文件。

\subsection{Evaluator-Optimizer}
\label{evaluator-optimizer}

\subsection{评估器-优化器（Evaluator-Optimizer）}
\label{evaluator-optimizer}

A two-model feedback loop~\cite{madaan2023selfrefine}: a generator produces candidate outputs while a separate evaluator scores them against explicit criteria. If the score falls below a threshold, the evaluator’s critique is appended to the generator’s context and the cycle repeats until the quality bar is met or a retry budget is exhausted.

一个双模型反馈循环~\cite{madaan2023selfrefine}：生成器产生候选输出，同时一个独立的评估器根据显式标准对它们进行评分。如果分数低于阈值，评估器的批评意见被附加到生成器的上下文中，循环重复，直到满足质量要求或重试预算耗尽。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_063_fig63.png}
\caption{Evaluator-optimizer: iterative refinement without training.}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_063_fig63.png}
\caption{评估器-优化器：无需训练的迭代优化。}
\end{figure}

\textbf{When to use}: Tasks with clear quality criteria---code that must pass tests, translations that must preserve meaning, writing that must match a style guide.

\textbf{何时使用}：具有明确质量标准的任务——必须通过测试的代码、必须保留含义的翻译、必须符合风格指南的写作。

\section{Autonomous Agent Patterns}
\label{autonomous-agent-patterns}

\section{自主Agent模式（Autonomous Agent Patterns）}
\label{autonomous-agent-patterns}

These patterns give the LLM control over the execution flow itself.

这些模式让LLM控制执行流程本身。

\subsection{ReAct (Reason + Act)}
\label{react-reason-act}

\subsection{ReAct（推理+行动）}
\label{react-reason-act}

The foundational agent pattern~\cite{yao2023react}. The LLM alternates between thinking (internal reasoning), acting (tool calls), and observing (processing results) in a loop until it produces a final answer.

基础的Agent模式~\cite{yao2023react}。LLM在思考（内部推理）、行动（工具调用）和观察（处理结果）之间交替循环，直到产生最终答案。

\begin{keybox}[ReAct Implementation Essentials]
\begin{itemize}
  \item \textbf{Scratchpad}: The ``Thought'' step is logged but not shown to the user.
  \item \textbf{Tool parsing}: The harness extracts structured tool calls from model output.
  \item \textbf{Max iterations}: Always cap the loop (typical: 10--25 iterations).
  \item \textbf{Termination}: Model outputs a special action (e.g., \texttt{final\_answer}) or no tool call is detected.
\end{itemize}
\end{keybox}

\begin{keybox}[ReAct实现要点]
\begin{itemize}
  \item \textbf{草稿区（Scratchpad）}：“思考”步骤被记录但不对用户显示。
  \item \textbf{工具解析}：框架从模型输出中提取结构化工具调用。
  \item \textbf{最大迭代次数}：始终限制循环（典型值：10--25次迭代）。
  \item \textbf{终止条件}：模型输出特殊动作（例如 \texttt{final\_answer}）或未检测到工具调用。
\end{itemize}
\end{keybox}

\subsection{Planning Agents}
\label{planning-agents}

\subsection{规划Agent（Planning Agents）}
\label{planning-agents}

The agent generates an explicit plan before executing, and can revise the plan mid-execution~\cite{wang2023planandsolve}.

Agent在执行前生成显式计划，并可以在执行过程中修改计划~\cite{wang2023planandsolve}。

\begin{table}[ht!]
\centering
\caption{Planning strategies compared}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Strategy} & \textbf{Replanning} & \textbf{Characteristics} \\
\midrule
Plan-then-Execute & Never & Simple; fragile to unexpected results \\
Adaptive & On failure & Replans only when a step fails; moderate cost \\
Continuous & Every step & Full re-evaluation after each observation; expensive but robust \\
Hierarchical & On sub-plan done & High-level plan fixed; sub-plans generated dynamically \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[ht!]
\centering
\caption{规划策略对比}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{策略} & \textbf{重新规划} & \textbf{特点} \\
\midrule
先规划后执行 & 从不 & 简单；对意外结果脆弱 \\
自适应 & 失败时 & 仅在步骤失败时重新规划；成本适中 \\
连续 & 每一步 & 每次观察后全面重新评估；昂贵但稳健 \\
分层 & 子计划完成时 & 高层计划固定；子计划动态生成 \\
\bottomrule
\end{tabular}
\end{table}

\begin{examplebox}[Planning Agent: Research Report Generation]
\textbf{User request}: ``Write a 2-page report comparing transformer architectures for time-series forecasting.''

\begin{examplebox}[规划Agent：研究报告生成]
\textbf{用户请求}：“写一份2页的报告，比较用于时间序列预测的Transformer架构。”

\textbf{Step 1 --- Plan generation} (single LLM call):

\textbf{步骤1 --- 计划生成}（单次LLM调用）：

\begin{lstlisting}[style=pythonstyle]
plan = [
    {"id": 1, "task": "Search for recent transformer-based "
                      "time-series models (2023-2025)",
     "tool": "search_web", "deps": []},
    {"id": 2, "task": "Read top 5 papers, extract key methods",
     "tool": "read_papers", "deps": [1]},
    {"id": 3, "task": "Build comparison table (architecture, "
                      "dataset, metrics)",
     "tool": "none", "deps": [2]},
    {"id": 4, "task": "Write introduction + methodology section",
     "tool": "none", "deps": [2]},
    {"id": 5, "task": "Write results + conclusion",
     "tool": "none", "deps": [3, 4]},
    {"id": 6, "task": "Review and polish final report",
     "tool": "none", "deps": [5]},
]
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle]
plan = [
    {"id": 1, "task": "搜索近期基于Transformer的"
                      "时间序列模型（2023-2025）",
     "tool": "search_web", "deps": []},
    {"id": 2, "task": "阅读前5篇论文，提取关键方法",
     "tool": "read_papers", "deps": [1]},
    {"id": 3, "task": "构建比较表（架构、"
                      "数据集、指标）",
     "tool": "none", "deps": [2]},
    {"id": 4, "task": "撰写引言+方法论部分",
     "tool": "none", "deps": [2]},
    {"id": 5, "task": "撰写结果+结论",
     "tool": "none", "deps": [3, 4]},
    {"id": 6, "task": "审阅并润色最终报告",
     "tool": "none", "deps": [5]},
]
\end{lstlisting}

\end{examplebox}

\end{examplebox}
```

## \textbf{Step 2 --- Execution with adaptive replanning}: The agent executes steps in dependency order. After step~1, the search returns only 3 relevant papers. The agent \emph{replans}: it adds a sub-step to broaden the search to adjacent domains (e.g., PatchTST, iTransformer). The revised plan continues from step~2 with the expanded corpus.
## \textbf{步骤 2 —— 带自适应重规划的执行}：智能体按依赖顺序执行步骤。在步骤~1 之后，搜索仅返回 3 篇相关论文。智能体\emph{重新规划}：它添加了一个子步骤，将搜索范围扩大到相邻领域（例如 PatchTST、iTransformer）。修订后的计划从步骤~2 开始，使用扩展后的语料库继续执行。

\textbf{Key insight}: The plan is a \emph{living document}---it provides structure but adapts to observations. The harness tracks dependencies as a DAG and only executes steps whose predecessors have completed.
\textbf{关键洞察}：计划是一份\emph{活文档}——它提供结构，但会根据观察结果进行调整。工作流引擎将依赖关系跟踪为有向无环图（DAG），并且仅执行其前置步骤已完成的步骤。
\end{examplebox}


\subsection{Reflection and Self-Critique}
\subsection{反思与自我批判}
\label{reflection-and-self-critique}


The agent pauses to evaluate its own trajectory and correct course:
智能体会暂停以评估自身轨迹并纠正方向：


\begin{enumerate}
  \item \textbf{Output validation}: ``Is this correct? Did I miss anything?''
  \item \textbf{输出验证}：“这正确吗？我是否遗漏了什么？”
  \item \textbf{Trajectory review}: Review last $k$ steps, identify mistakes or inefficiencies.
  \item \textbf{轨迹回顾}：回顾最近 $k$ 步，识别错误或低效之处。
  \item \textbf{Strategy revision}: Reconsider the overall approach (``Am I solving the right problem?'').
  \item \textbf{策略修正}：重新考虑整体方法（“我是在解决正确的问题吗？”）。
\end{enumerate}


\begin{intuitionbox}[Reflexion: Learning from Failure]
\textbf{Reflexion (反思)：从失败中学习}
The \textbf{Reflexion} pattern~\cite{shinn2023reflexion} maintains a persistent ``reflection memory.'' After each failed attempt, the agent writes a natural-language reflection (``I failed because I didn’t check the edge case''). On the next attempt, these reflections are included in the prompt---enabling learning across episodes without weight updates.
\textbf{Reflexion} 模式~\cite{shinn2023reflexion} 维护一个持久的“反思记忆”。每次尝试失败后，智能体会用自然语言写下反思（“我失败了，因为我没有检查边缘情况”）。在下次尝试时，这些反思会被包含在提示中——从而在不更新权重的情况下实现跨回合的学习。
\end{intuitionbox}


\subsection{Tool-Use Patterns}
\subsection{工具使用模式}
\label{tool-use-patterns}


How an agent invokes tools significantly affects its reliability, latency, and cost. Five canonical patterns have emerged~\cite{schick2023toolformer}:
智能体如何调用工具会显著影响其可靠性、延迟和成本。目前已经出现了五种典型模式~\cite{schick2023toolformer}：


\begin{table}[ht!]
\centering
\caption{Tool invocation patterns}
\caption{工具调用模式}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Pattern} & \textbf{Description} & \textbf{Example} \\
\textbf{模式} & \textbf{描述} & \textbf{示例} \\
\midrule
Single-turn & One tool call per LLM response & Simple Q\&A with search \\
单次调用 & 每次 LLM 响应一次工具调用 & 带搜索的简单问答 \\
Multi-tool & Multiple parallel tool calls in one response & Search + calculate + format \\
多工具调用 & 一次响应中并行多次工具调用 & 搜索 + 计算 + 格式化 \\
Sequential & Tool output feeds into next tool call & Search $\to$ read $\to$ extract \\
顺序调用 & 工具输出馈入下一次工具调用 & 搜索 $\to$ 阅读 $\to$ 提取 \\
Nested & Tool call triggers another agent & Code agent calls test-runner \\
嵌套调用 & 工具调用触发另一个智能体 & 代码智能体调用测试运行器 \\
Fallback & Preferred tool fails; try alternative & API $\to$ scrape $\to$ cache \\
回退调用 & 首选工具失败；尝试备选 & API $\to$ 爬取 $\to$ 缓存 \\
\bottomrule
\end{tabular}
\end{table}


\paragraph{Single-Turn Tool Use.}
\paragraph{单次工具调用 (Single-Turn Tool Use).}
\label{single-turn-tool-use.}


The simplest pattern: the model issues one tool call, receives the result, and produces a final answer. Sufficient for factual lookups, unit conversions, or single API queries. The harness makes exactly two LLM calls (one to decide on the tool, one to synthesize the result).
最简单的模式：模型发起一次工具调用，接收结果，然后生成最终答案。适用于事实查询、单位换算或单一 API 查询。工作流引擎恰好进行两次 LLM 调用（一次决定使用哪个工具，一次合成结果）。


\paragraph{Multi-Tool (Parallel).}
\paragraph{多工具调用（并行）(Multi-Tool (Parallel)).}
\label{multi-tool-parallel.}


Modern APIs (OpenAI, Anthropic) allow the model to request multiple tool calls in a single response. The harness executes them concurrently and returns all results together. This dramatically reduces latency for tasks requiring independent information from multiple sources---e.g., fetching stock price, weather, and calendar simultaneously. The key constraint: the tools must be \emph{independent} (no tool’s output is needed as input to another).
现代 API（OpenAI、Anthropic）允许模型在一次响应中请求多次工具调用。工作流引擎并发执行这些调用，并一次性返回所有结果。这显著降低了需要从多个来源获取独立信息的任务的延迟——例如同时获取股票价格、天气和日历。关键约束：工具必须是\emph{独立的}（没有哪个工具的输出需要作为另一个工具的输入）。


\paragraph{Sequential (Pipeline).}
\paragraph{顺序调用（流水线）(Sequential (Pipeline)).}
\label{sequential-pipeline.}


Each tool’s output feeds into the next tool’s input, forming a data pipeline. The model decides the next tool based on the previous result. Common in research workflows: \texttt{search} $\to$ \texttt{fetch\_page} $\to$ \texttt{extract\_data} $\to$ \texttt{analyze}. The harness must track the growing context and may need to summarize intermediate results to stay within budget.
每个工具的输出馈入下一个工具的输入，形成数据流水线。模型根据前一个结果决定下一个工具。常见于研究工作流：\texttt{search} $\to$ \texttt{fetch\_page} $\to$ \texttt{extract\_data} $\to$ \texttt{analyze}。工作流引擎必须跟踪不断增长的上下文，并可能需要总结中间结果以保持在预算内。


\paragraph{Nested (Agent-as-Tool).}
\paragraph{嵌套调用（智能体即工具）(Nested (Agent-as-Tool)).}
\label{nested-agent-as-tool.}


A tool call invokes an entirely separate agent---with its own prompt, tools, and context. The parent agent treats the sub-agent as a black-box function. This enables specialization: a research agent delegates code execution to a coding agent, which has access to a sandbox and test runner. The Swarm pattern~\cite{openai2024swarm} generalizes this via handoffs between specialized agents.
一次工具调用会调用一个完全独立的智能体——它拥有自己的提示、工具和上下文。父智能体将子智能体视为黑盒函数。这实现了专业化：研究智能体将代码执行委托给代码智能体，后者可以访问沙箱和测试运行器。Swarm 模式~\cite{openai2024swarm} 通过专业智能体之间的交接来泛化这一方式。


\paragraph{Fallback (Graceful Degradation).}
\paragraph{回退调用（优雅降级）(Fallback (Graceful Degradation)).}
\label{fallback-graceful-degradation.}


The harness tries tools in priority order: if the preferred tool fails (timeout, rate limit, API error), it automatically falls back to an alternative. The model need not be aware of the fallback logic---the harness handles it transparently. Example: primary search API $\to$ backup search $\to$ cached results $\to$ inform model that search is unavailable.
工作流引擎按优先级顺序尝试工具：如果首选工具失败（超时、速率限制、API 错误），它会自动回退到备选工具。模型无需感知回退逻辑——工作流引擎透明地处理它。示例：主搜索 API $\to$ 备用搜索 $\to$ 缓存结果 $\to$ 通知模型搜索不可用。


\section{Design Principles}
\section{设计原则}
\label{design-principles}


The following principles, distilled from Anthropic’s guide to building effective agents~\cite{anthropic2024buildingagents}, apply across all patterns:
以下原则提炼自 Anthropic 关于构建有效智能体的指南~\cite{anthropic2024buildingagents}，适用于所有模式：


\begin{enumerate}
  \item \textbf{Keep it simple.} Use the simplest architecture that works. Add complexity only when demonstrated necessary. A prompt chain that solves the problem is always preferable to a multi-agent system that might.
  \item \textbf{保持简单。}使用最简单的可行架构。仅在证明必要时才增加复杂性。能够解决问题的提示链总是优于可能解决问题的多智能体系统。
  \item \textbf{Transparency over cleverness.} Every step should be inspectable. Avoid hidden state or implicit reasoning. When an agent fails, you need to understand \emph{why}---opaque architectures make debugging impossible.
  \item \textbf{透明优于巧妙。}每一步都应可检查。避免隐藏状态或隐式推理。当智能体失败时，你需要理解\emph{为什么}——不透明的架构使得调试变得不可能。
  \item \textbf{Provide good tools.} Well-documented, well-typed tools with clear error messages are force multipliers. A tool with a vague description will be misused; a tool with a precise schema and usage guidance will be selected correctly.
  \item \textbf{提供好工具。}文档完善、类型明确、错误消息清晰的工具是力量倍增器。描述模糊的工具会被误用；具有精确模式和用法指导的工具会被正确选用。
  \item \textbf{Plan for failure.} Every tool call can fail. Build retry logic, fallbacks, and graceful degradation at the harness level so the model does not need to reason about infrastructure failures.
  \item \textbf{为失败做好计划。}每次工具调用都可能失败。在工作流引擎层面构建重试逻辑、回退和优雅降级，这样模型就不需要推理基础设施故障。
  \item \textbf{Use structured outputs.} Constrained generation (JSON schema, function calling) prevents parse failures. An agent that produces free-form text requiring regex parsing is fragile; one that produces validated JSON is robust.
  \item \textbf{使用结构化输出。}受限生成（JSON 模式、函数调用）可以防止解析失败。产生需要正则表达式解析的自由文本的智能体是脆弱的；产生经过验证的 JSON 的智能体是健壮的。
  \item \textbf{Test with diverse inputs.} Agent behaviour is more variable than single-turn chat. The same prompt can produce different tool-call sequences on different runs. Test adversarially, with edge cases, ambiguous requests, and malformed inputs.
  \item \textbf{使用多样化的输入进行测试。}智能体行为比单轮对话更具变异性。相同的提示在不同运行中可能产生不同的工具调用序列。要进行对抗性测试，包含边缘情况、模糊请求和畸形输入。
\end{enumerate}


\section{Pattern Selection Guide}
\section{模式选择指南}
\label{pattern-selection-guide}


Choosing the right pattern depends on three factors: (1)~how predictable the task structure is, (2)~how many LLM calls you can afford in latency and cost, and (3)~whether quality requires iteration. Use the table below as a decision matrix---start from the top (simplest) and move down only when the simpler pattern demonstrably fails.
选择合适的模式取决于三个因素：(1) 任务结构的可预测性如何，(2) 在延迟和成本方面你能承受多少 LLM 调用，以及 (3) 质量是否需要迭代。使用下表作为决策矩阵——从顶部（最简单）开始，只有当更简单的模式被证明失败时才向下移动。


\begin{table}[ht!]
\centering
\caption{When to use each agent design pattern}
\caption{何时使用每种智能体设计模式}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{Pattern} & \textbf{Complexity} & \textbf{LLM Calls} & \textbf{Best For} \\
\textbf{模式} & \textbf{复杂度} & \textbf{LLM 调用次数} & \textbf{最适用于} \\
\midrule
Prompt chaining & Low & $N$ (fixed) & Sequential tasks, content pipelines \\
提示链 & 低 & $N$（固定） & 顺序任务，内容流水线 \\
Routing & Low & 1 + 1 & Multi-type inputs, triage \\
路由 & 低 & 1 + 1 & 多类型输入，分流 \\
Parallelization & Low & $N$ (parallel) & Independent subtasks, voting \\
并行化 & 低 & $N$（并行） & 独立子任务，投票 \\
Orchestrator-workers & Medium & Variable & Unknown decomposition \\
编排器-工作者 & 中 & 可变 & 未知分解 \\
Evaluator-optimizer & Medium & 2--10 (loop) & Quality-critical outputs \\
评估器-优化器 & 中 & 2--10（循环） & 质量关键型输出 \\
ReAct & Medium & 3--25 (loop) & General tool-use, exploration \\
ReAct & 中 & 3--25（循环） & 通用工具使用，探索 \\
Planning agent & High & 5--50+ & Long-horizon, multi-step tasks \\
规划智能体 & 高 & 5--50+ & 长周期，多步骤任务 \\
Reflection & High & +50\% overhead & Tasks where first attempt often fails \\
反思 & 高 & 增加 50\% 开销 & 首次尝试经常失败的任务 \\
Multi-agent & High & Many & Complex domains, specialization \\
多智能体 & 高 & 大量 & 复杂领域，专业化 \\
\bottomrule
\end{tabular}
\end{table}


Patterns are composable: a planning agent may use prompt chaining for individual steps, an evaluator-optimizer within its review phase, and routing to dispatch subtasks to specialists. The art is knowing when to stop adding layers.
模式是可组合的：规划智能体可以在单个步骤中使用提示链，在其审查阶段使用评估器-优化器，并使用路由将子任务分派给专家。艺术在于知道何时停止添加层。