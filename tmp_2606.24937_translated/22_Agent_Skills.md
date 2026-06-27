```markdown
\chapter{Agent Skills}
\label{sec:agent-skills}
\chapter{智能体技能}
\label{sec:agent-skills}

As agents evolve from monolithic prompt-and-tool systems into modular architectures, a key design question emerges: \emph{how should an agent’s capabilities be organized, discovered, and composed?} The answer increasingly converges on the concept of \textbf{skills} --- discrete, reusable units of behaviour that can be loaded, combined, and swapped without retraining.
随着智能体从单一的提示-工具系统演变为模块化架构，一个关键设计问题浮现：\emph{智能体的能力应该如何被组织、发现和组合？} 答案日益集中于\textbf{skills (技能)}的概念上——一种离散的、可复用的行为单元，可以在无需重新训练的情况下加载、组合和替换。

The idea was popularized by Voyager~\cite{wang2023voyager}, which demonstrated that an LLM agent in Minecraft could accumulate a growing library of executable code skills, each verified and stored for later reuse. The same principle applies to production agents: skills encapsulate domain expertise in a composable, versionable format that scales beyond what any single prompt can hold. Skills frequently wrap MCP servers (Chapter~\ref{sec:mcp}) for tool access, connecting the skill abstraction to the standardized tool layer.
这一理念由Voyager~\cite{wang2023voyager}推广开来，该工作展示了Minecraft中的LLM智能体可以积累一个不断增长的可执行代码技能库，每个技能经验证后存储供后续复用。同样的原则适用于生产环境中的智能体：技能以可组合、可版本化的格式封装领域专长，其规模远超任何单一提示所能承载。技能通常包装MCP服务器（第~\ref{sec:mcp}章）以访问工具，从而将技能抽象层连接到标准化的工具层。

\section{What Is a Skill?}
\label{what-is-a-skill}
\section{什么是技能？}
\label{what-is-a-skill}

A \textbf{skill} is a self-contained capability module that gives an agent expertise in a specific domain or task. Unlike a raw tool (which exposes a single function), a skill encompasses:
一个\textbf{skill (技能)}是一个自包含的能力模块，为智能体提供特定领域或任务的专长。与原始工具（仅暴露单一函数）不同，技能包含：

\begin{itemize}
  \item \textbf{System prompt augmentation}: Domain-specific instructions, constraints, and persona elements injected into the agent’s context.
  \item \textbf{System prompt augmentation (系统提示增强)}：注入到智能体上下文中的领域特定指令、约束和角色元素。
  \item \textbf{Tool bindings}: One or more tools the skill requires (APIs, MCP servers, local commands).
  \item \textbf{Tool bindings (工具绑定)}：技能所需的一个或多个工具（API、MCP服务器、本地命令）。
  \item \textbf{Knowledge}: Reference material, examples, or few-shot demonstrations the agent needs to execute the skill correctly.
  \item \textbf{Knowledge (知识)}：智能体正确执行技能所需的参考资料、示例或少样本演示。
  \item \textbf{Workflow logic}: Multi-step procedures, decision trees, or conditional flows that guide the agent through complex tasks.
  \item \textbf{Workflow logic (工作流逻辑)}：引导智能体完成复杂任务的多步骤流程、决策树或条件分支。
  \item \textbf{Guardrails}: Skill-specific safety constraints, output format requirements, and validation rules.
  \item \textbf{Guardrails (护栏)}：技能特定的安全约束、输出格式要求和验证规则。
\end{itemize}

\begin{keybox}[Skill vs. Tool vs. Agent]
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Concept} & \textbf{Scope} & \textbf{Example} \\
\midrule
\textbf{Tool} & Single function call & \texttt{web\_search(query)} \\
\textbf{Skill} & Coherent capability (prompts + tools + knowledge) & ``Research Analyst'' skill \\
\textbf{Agent} & Autonomous entity with multiple skills & A coding assistant \\
\bottomrule
\end{tabular}

A tool is a hammer. A skill is knowing \emph{how to frame a house}. An agent is the carpenter who selects which skills to apply.
\end{keybox}
\begin{keybox}[技能 vs. 工具 vs. 智能体]
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{概念} & \textbf{范围} & \textbf{示例} \\
\midrule
\textbf{工具} & 单一函数调用 & \texttt{web\_search(query)} \\
\textbf{技能} & 连贯能力（提示+工具+知识） & “研究分析师”技能 \\
\textbf{智能体} & 拥有多种技能的自主实体 & 编程助手 \\
\bottomrule
\end{tabular}

工具是一把锤子。技能是知道\emph{如何搭建房屋框架}。智能体是选择应用哪些技能的木匠。
\end{keybox}

\section{Skill Architecture Patterns}
\label{skill-architecture-patterns}
\section{技能架构模式}
\label{skill-architecture-patterns}

\subsection{Static Skill Loading}
\label{static-skill-loading}
\subsection{静态技能加载}
\label{static-skill-loading}

The simplest pattern: skills are loaded at agent initialization based on configuration. The agent always has access to all its skills.
最简单的模式：技能在智能体初始化时根据配置加载。智能体始终可以访问其所有技能。

\begin{lstlisting}[style=pythonstyle]
# Pseudocode -- framework-agnostic pattern
agent = Agent(
    model="claude-sonnet-4-20250514",
    skills=["code-review", "documentation", "testing"],
    # Each skill adds prompts, tools, and knowledge to the agent
)
\end{lstlisting}
\begin{lstlisting}[style=pythonstyle]
# 伪代码——框架无关模式
agent = Agent(
    model="claude-sonnet-4-20250514",
    skills=["code-review", "documentation", "testing"],
    # 每个技能向智能体添加提示、工具和知识
)
\end{lstlisting}

\textbf{Pros:} Simple, predictable, low latency.\\
\textbf{优点：}简单、可预测、低延迟。

\textbf{Cons:} Context window waste when skills are unused; doesn’t scale to hundreds of skills.
\textbf{缺点：}技能未使用时浪费上下文窗口；无法扩展到数百个技能。

\subsection{Dynamic Skill Discovery}
\label{dynamic-skill-discovery}
\subsection{动态技能发现}
\label{dynamic-skill-discovery}

The agent selects which skills to activate based on the current task. A skill router (often a lightweight classifier or embedding-based matcher) determines relevance:
智能体根据当前任务选择要激活的技能。技能路由器（通常是轻量级分类器或基于嵌入的匹配器）确定相关性：

\begin{lstlisting}[style=pythonstyle]
# Pseudocode -- framework-agnostic pattern
relevant_skills = skill_router.match(
    user_request=message,
    available_skills=skill_registry,
    max_skills=3
)
agent.activate(relevant_skills)
\end{lstlisting}
\begin{lstlisting}[style=pythonstyle]
# 伪代码——框架无关模式
relevant_skills = skill_router.match(
    user_request=message,
    available_skills=skill_registry,
    max_skills=3
)
agent.activate(relevant_skills)
\end{lstlisting}

\textbf{Pros:} Scales to large skill libraries; context-efficient.\\
\textbf{优点：}可扩展到大型技能库；上下文高效。

\textbf{Cons:} Routing errors can miss relevant skills; adds latency.
\textbf{缺点：}路由错误可能遗漏相关技能；增加延迟。

\subsection{Hierarchical Skill Composition}
\label{hierarchical-skill-composition}
\subsection{层次化技能组合}
\label{hierarchical-skill-composition}

Skills can depend on other skills, forming a DAG. A high-level skill (e.g., ``Deploy Application'') may invoke sub-skills (``Run Tests'', ``Build Docker Image'', ``Update DNS''):
技能可以依赖其他技能，形成有向无环图。高级技能（例如“部署应用”）可能调用子技能（“运行测试”、“构建Docker镜像”、“更新DNS”）：

\begin{itemize}
  \item Skills declare dependencies explicitly
  \item The orchestrator resolves the dependency graph before execution
  \item Sub-skills can be shared across multiple parent skills
\end{itemize}
\begin{itemize}
  \item 技能显式声明依赖关系
  \item 编排器在执行前解析依赖图
  \item 子技能可以在多个父技能间共享
\end{itemize}

\section{Case Study: Anthropic’s Agent Design}
\label{case-study-anthropics-agent-design}
\section{案例研究：Anthropic的智能体设计}
\label{case-study-anthropics-agent-design}

Anthropic’s approach to agent architecture~\cite{anthropic2024buildingagents} provides one of the clearest articulations of skill-based agent design in production. Their philosophy emphasizes \textbf{simplicity over complexity} and \textbf{composable building blocks over monolithic frameworks}. (These patterns are also covered from an orchestration perspective in Chapter~\ref{sec:agent-design-patterns}.)
Anthropic对智能体架构的方法~\cite{anthropic2024buildingagents}提供了生产环境中基于技能的智能体设计最清晰的阐述之一。其理念强调\textbf{简单优于复杂}和\textbf{可组合的构建块优于单一框架}。（这些模式也在第~\ref{sec:agent-design-patterns}章从编排角度进行了讨论。）

\subsection{Core Principles}
\label{core-principles}
\subsection{核心原则}
\label{core-principles}

\begin{enumerate}
  \item \textbf{Start with the simplest solution.} Don’t reach for agentic patterns until simpler approaches (single LLM call, retrieval + generation) have been tried and found insufficient.
  \item \textbf{从最简单的解决方案开始。}在尝试更简单的方法（单一LLM调用、检索+生成）并发现其不足之前，不要直接使用智能体模式。
  \item \textbf{Workflows vs. agents.} Anthropic distinguishes between:
  \item \textbf{工作流 vs. 智能体。}Anthropic区分以下两者：
\end{enumerate}

\begin{itemize}
  \item \textbf{Workflows}: Predefined orchestration of LLM calls --- deterministic control flow with LLM steps at specific nodes. More predictable, easier to debug.
  \item \textbf{Workflows (工作流)}：预定义的LLM调用编排——在特定节点具有LLM步骤的确定性控制流。更可预测，更易调试。
  \item \textbf{Agents}: The LLM dynamically decides what to do next --- tool selection, iteration count, and stopping criteria are all model-driven. More flexible, harder to control.
  \item \textbf{Agents (智能体)}：LLM动态决定下一步做什么——工具选择、迭代次数和停止条件均由模型驱动。更灵活，更难以控制。
\end{itemize}

\begin{enumerate}
\setcounter{enumi}{2}
  \item \textbf{Augmented LLM as the atomic unit.} The primitive is never a bare model---it is always a model bundled with its retrieval sources, callable tools, and persistent memory. This composite unit is, in practice, a skill-equipped model.
  \item \textbf{增强型LLM作为原子单元。}原语从来不是裸模型——而是与检索源、可调用工具和持久记忆捆绑在一起的模型。这个复合单元实际上就是配备技能的模型。
\end{enumerate}

\subsection{Building Block Patterns}
\label{building-block-patterns}
\subsection{构建块模式}
\label{building-block-patterns}

Anthropic identifies five composable workflow patterns that function as skill templates:
Anthropic识别出五种可作为技能模板的可组合工作流模式：

\begin{table}[ht!]
\centering
\caption{Anthropic’s composable agent patterns.}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Pattern} & \textbf{Mechanism} & \textbf{When to Use} \\
\midrule
\textbf{Prompt Chaining} & Sequential LLM calls where each step’s output feeds the next. Gates between steps validate intermediate results. & Multi-step transformations with clear decomposition \\
\textbf{Routing} & A classifier or LLM directs input to a specialized handler (skill) based on task type. & Distinct task categories requiring different expertise \\
\textbf{Parallelization} & Multiple LLM calls run simultaneously --- either sectioning (split task) or voting (same task, aggregate). & Independent subtasks; or confidence via consensus \\
\textbf{Orchestrator--Workers} & A central LLM breaks the task into subtasks, delegates to worker LLMs, then synthesizes results. & Complex tasks where subtasks aren’t predictable in advance \\
\textbf{Evaluator--Optimizer} & One LLM generates, another evaluates; iterate until quality threshold is met. & Tasks with clear quality criteria (code, writing) \\
\bottomrule
\end{tabular}
\end{table}
\begin{table}[ht!]
\centering
\caption{Anthropic的可组合智能体模式。}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{模式} & \textbf{机制} & \textbf{适用场景} \\
\midrule
\textbf{提示链} & 顺序LLM调用，每一步的输出作为下一步输入。步骤之间的门控验证中间结果。 & 具有清晰分解的多步转换 \\
\textbf{路由} & 分类器或LLM根据任务类型将输入导向专用处理器（技能）。 & 需要不同专长的不同任务类别 \\
\textbf{并行化} & 多个LLM调用同时运行——要么分段（拆分任务），要么投票（相同任务，聚合结果）。 & 独立子任务；或通过共识增强置信度 \\
\textbf{编排器-工作者} & 中央LLM将任务拆分为子任务，委托给工作者LLM，然后综合结果。 & 子任务不可预知的复杂任务 \\
\textbf{评估器-优化器} & 一个LLM生成，另一个评估；迭代直到满足质量阈值。 & 具有明确质量标准的任务（代码、写作） \\
\bottomrule
\end{tabular}
\end{table}

\subsection{The Augmented LLM}
\label{the-augmented-llm}
\subsection{增强型LLM}
\label{the-augmented-llm}

In Anthropic’s framing, the fundamental unit is not the bare model but the \textbf{augmented LLM}:
在Anthropic的框架中，基本单元不是裸模型，而是\textbf{增强型LLM (augmented LLM)}：

\[
\text{Augmented LLM} = \text{Model} + \text{Retrieval} + \text{Tools} + \text{Memory}
\]

This maps directly to the skill concept: each skill configures which retrieval sources, tools, and memory stores the model has access to for a specific task. The skill boundary defines what the model \emph{can see and do} within a particular invocation.
这直接映射到技能概念：每个技能配置模型在特定任务中可以访问的检索源、工具和记忆存储。技能边界定义了模型在特定调用中\emph{能看到和做什么}。

\subsection{Practical Implications}
\label{practical-implications}
\subsection{实践启示}
\label{practical-implications}

\begin{intuitionbox}[Anthropic’s Key Insight]
The most effective agents aren’t the most complex ones. They are \textbf{simple loops with good tools}:
\end{intuitionbox}
\begin{intuitionbox}[Anthropic的关键见解]
最高效的智能体并非最复杂的那些。它们是\textbf{带有好工具的简单循环}：
\end{intuitionbox}

\begin{lstlisting}[style=pythonstyle]
while not done:
    action = llm.decide(context, tools)
    result = execute(action)
    context.append(result)
    done = llm.should_stop(context)
\end{lstlisting}
\begin{lstlisting}[style=pythonstyle]
while not done:
    action = llm.decide(context, tools)
    result = execute(action)
    context.append(result)
    done = llm.should_stop(context)
\end{lstlisting}
```

## What Is a Skill?

The intelligence comes from (1) the model’s capability, (2) the quality of tool descriptions, and (3) the clarity of the task framing --- not from elaborate orchestration logic. Skills provide the structure for (2) and (3).
智能来自于（1）模型的能力、（2）工具描述的质量，以及（3）任务框架的清晰度——而非精心设计的编排逻辑。技能为（2）和（3）提供了结构支撑。

\end{intuitionbox}

\paragraph{Design recommendations from Anthropic’s approach:}
\paragraph{来自Anthropic方法的设计建议：}

\label{design-recommendations-from-anthropics-approach}


\begin{itemize}
  \item \textbf{Keep agent loops simple}: Avoid over-engineering the control flow. Let the model decide.
  \item \textbf{保持智能体循环简单}：避免过度设计控制流。让模型做决策。
  \item \textbf{Invest in tool quality}: Detailed, unambiguous tool descriptions are more valuable than complex routing logic.
  \item \textbf{投入工具质量}：详细、明确的工具描述比复杂的路由逻辑更有价值。
  \item \textbf{Use structured outputs}: Force the model to output decisions in parseable formats (JSON, function calls) --- reduces skill execution errors.
  \item \textbf{使用结构化输出}：强制模型以可解析的格式（JSON、函数调用）输出决策——减少技能执行错误。
  \item \textbf{Build in recovery}: Skills should handle errors gracefully --- retry with different parameters, ask for clarification, or escalate to a human.
  \item \textbf{内置恢复机制}：技能应优雅地处理错误——用不同参数重试、请求澄清，或升级到人工。
  \item \textbf{Limit scope per skill}: A skill that tries to do everything will do nothing well. Narrow, well-defined skills compose better than broad ones.
  \item \textbf{限制每个技能的 scope（范围）}：试图包揽一切的技能往往一事无成。狭窄而定义清晰的技能比宽泛的技能更易于组合。
\end{itemize}


## Skill Lifecycle
## 技能生命周期

\label{skill-lifecycle}


\begin{enumerate}
  \item \textbf{Discovery}: The system identifies which skills are available (registry, marketplace, local definitions).
  \item \textbf{发现（Discovery）}：系统识别哪些技能可用（注册表、市场、本地定义）。
  \item \textbf{Selection}: Based on the user request, relevant skills are matched and loaded.
  \item \textbf{选择（Selection）}：根据用户请求，匹配并加载相关技能。
  \item \textbf{Activation}: Skill prompts, tools, and knowledge are injected into the agent’s context.
  \item \textbf{激活（Activation）}：将技能提示词、工具和知识注入智能体的上下文。
  \item \textbf{Execution}: The agent uses the skill’s capabilities to accomplish the task.
  \item \textbf{执行（Execution）}：智能体利用技能的能力完成任务。
  \item \textbf{Deactivation}: Skill context is removed to free context window space for subsequent tasks.
  \item \textbf{停用（Deactivation）}：移除技能上下文，为后续任务释放上下文窗口空间。
  \item \textbf{Learning}: Execution results may update the skill’s few-shot examples or fine-tune routing.
  \item \textbf{学习（Learning）}：执行结果可能会更新技能的 few-shot（少样本）示例，或微调路由。
\end{enumerate}


## Skill Registries and Marketplaces
## 技能注册表与市场

\label{skill-registries-and-marketplaces}


Production skill systems require infrastructure:
生产级技能系统需要基础设施：


\begin{itemize}
  \item \textbf{Skill manifest}: A structured description (name, capabilities, required tools, input/output schema) enabling automatic discovery and routing.
  \item \textbf{技能清单（Skill manifest）}：结构化描述（名称、能力、所需工具、输入/输出模式），支持自动发现和路由。
  \item \textbf{Version control}: Skills evolve; agents need to pin specific versions for reproducibility.
  \item \textbf{版本控制（Version control）}：技能会演变；智能体需要锁定特定版本以确保可复现性。
  \item \textbf{Dependency resolution}: Skills may require specific MCP servers, API keys, or other skills.
  \item \textbf{依赖解析（Dependency resolution）}：技能可能依赖特定的 MCP 服务器、API 密钥或其他技能。
  \item \textbf{Permission model}: Not all agents should have access to all skills (security, cost, capability boundaries).
  \item \textbf{权限模型（Permission model）}：并非所有智能体都应能访问所有技能（安全性、成本、能力边界）。
  \item \textbf{Marketplace}: Organizations can publish, share, and install skills --- analogous to package managers for code.
  \item \textbf{市场（Marketplace）}：组织可以发布、共享和安装技能——类似于代码的包管理器。
\end{itemize}


\begin{examplebox}[Skill Manifest Example]
A skill manifest declares everything an orchestrator needs to load and invoke a skill. No industry-standard schema exists yet; below is an illustrative format that captures common fields across real implementations (Anthropic MCP, OpenAI function specs, LangChain tool definitions):
技能清单声明了编排器加载和调用技能所需的一切。目前尚不存在行业标准模式；下面是说明性格式，涵盖了实际实现（Anthropic MCP、OpenAI 函数规范、LangChain 工具定义）中的常见字段：


\begin{lstlisting}[style=pythonstyle]
// Illustrative schema -- not a specific SDK format
// 说明性模式——并非特定 SDK 格式
{
  "name": "code-review",
  "description": "Review code changes for bugs, style, and security issues",
  "version": "2.1.0",
  "requires": {
    "tools": ["file_read", "grep", "git_diff"],
    "mcp_servers": ["github"],
    "models": ["claude-sonnet-4-20250514"]
  },
  "input_schema": {
    "type": "object",
    "properties": {
      "repo": {"type": "string"},
      "pr_number": {"type": "integer"}
    }
  },
  "prompts": ["skills/code-review/system.md"],
  "knowledge": ["skills/code-review/style-guide.md"]
}
\end{lstlisting}
\end{examplebox}


## Skills vs.~Fine-Tuning
## 技能与微调（Fine-Tuning）的比较

\label{skills-vs.-fine-tuning}


A natural question: why use runtime skill injection instead of fine-tuning the model?
一个自然的问题：为什么使用运行时技能注入，而不是微调模型？


\begin{table}[ht!]
\centering
\caption{Skills (in-context) vs.~fine-tuning for adding capabilities.}
\caption{技能（上下文中）与微调在添加能力方面的对比。}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Dimension} & \textbf{Skills (In-Context)} & \textbf{Fine-Tuning} \\
\textbf{维度} & \textbf{技能（上下文内）} & \textbf{微调} \\
\midrule
Deployment speed & Instant & Hours--days \\
部署速度 & 即时 & 数小时至数天 \\
Flexibility & Swap/combine at runtime & Fixed at training time \\
灵活性 & 运行时交换/组合 & 训练时固定 \\
Context cost & Uses context window & Zero runtime cost \\
上下文成本 & 占用上下文窗口 & 运行时成本为零 \\
Deep behavior change & Limited by context length & Deep parametric change \\
深度行为改变 & 受上下文长度限制 & 深度参数变化 \\
Multi-tenant & Different skills per user & Same model for all \\
多租户 & 每个用户不同技能 & 所有用户相同模型 \\
Maintenance & Update text files & Retrain on new data \\
维护 & 更新文本文件 & 在新数据上重新训练 \\
\bottomrule
\end{tabular}
\end{table}


In practice, the two approaches are complementary: fine-tuning provides \emph{base capabilities} (instruction following, tool use format, reasoning), while skills provide \emph{task-specific expertise} layered on top at runtime.
在实践中，这两种方法是互补的：微调提供 \emph{基础能力}（指令遵循、工具使用格式、推理），而技能则在运行时提供叠加在其上的 \emph{任务特定专业知识}。