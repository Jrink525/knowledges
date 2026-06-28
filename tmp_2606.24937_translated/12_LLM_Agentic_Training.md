## Motivation: From Chatbots to Autonomous Agents  
## 动机：从聊天机器人到自主智能体

Modern LLMs are increasingly deployed not just as conversational assistants but as \textbf{autonomous agents} that interact with external tools, APIs, databases, and environments over multiple steps. This shift---from single-turn chatbots to multi-step agents---introduces fundamentally new RL challenges that require rethinking how we train, evaluate, and deploy language models.  
现代大语言模型（LLM）不仅被部署为对话助手，更被部署为\textbf{自主智能体（autonomous agents）}，能够在多个步骤中与外部工具、API、数据库和环境进行交互。这种从单轮聊天机器人到多步智能体的转变，带来了全新的强化学习挑战，需要我们重新思考如何训练、评估和部署语言模型。

\begin{figure}[ht!]
\centering
\begin{tikzpicture}[
  box/.style={draw, rounded corners, minimum width=2.2cm, minimum height=0.8cm, font=\small},
  arrow/.style={->, thick, >=stealth},
  lbl/.style={font=\scriptsize, midway, above},
  lblb/.style={font=\scriptsize, midway, below},
]
% --- (a) Chatbot ---
\node[font=\small\bfseries] at (-3.5, 2.6) {(a) Traditional Chatbot};
\node[box, fill=blue!12] (user1) at (-5, 1.5) {User};
\node[box, fill=orange!15] (llm1) at (-2, 1.5) {LLM};
\draw[arrow] ([yshift=2pt]user1.east) -- node[lbl]{prompt} ([yshift=2pt]llm1.west);
\draw[arrow] ([yshift=-2pt]llm1.west) -- node[lblb]{response} ([yshift=-2pt]user1.east);
\node[font=\scriptsize, text=gray] at (-3.5, 0.5) {Single turn, immediate feedback};
\draw[dashed, gray, rounded corners] (-6.4, 0.0) rectangle (-0.6, 3.0);


% --- (b) Autonomous Agent ---
\node[font=\small\bfseries] at (4.5, 2.6) {(b) Autonomous Agent};
\node[box, fill=blue!12] (user2) at (1.8, 1.5) {User};
\node[box, fill=orange!15, minimum width=2.4cm] (agent) at (4.5, 1.5) {LLM Agent};
\node[box, fill=green!12, minimum width=2cm] (tools) at (7.2, 1.5) {Tools};
\node[box, fill=red!8, minimum width=2.4cm] (env) at (5.8, -0.5) {Environment};


% User -> Agent
\draw[arrow] (user2.east) -- node[lbl]{task} (agent.west);
% Agent <-> Tools (bidirectional = the loop)
\draw[arrow] ([yshift=3pt]agent.east) -- node[lbl]{act} ([yshift=3pt]tools.west);
\draw[arrow] ([yshift=-3pt]tools.west) -- node[lblb]{obs} ([yshift=-3pt]agent.east);
% Tools -> Environment
\draw[arrow] (tools.south) -- node[lbl, right]{execute} (tools.south |- env.north);
% Environment -> Agent (reward)
\draw[arrow, dashed] (env.west) -- node[lblb]{reward} (agent.south -| env.west) -- (agent.south);


\node[font=\scriptsize, text=gray] at (4.5, -1.5) {Multi-step, sparse terminal reward};
\draw[dashed, gray, rounded corners] (0.5, -1.9) rectangle (8.6, 3.0);
\end{tikzpicture}
\caption{From Chatbots to Autonomous Agents: Traditional LLM chatbots operate in a single-step conversational loop with immediate human feedback. Autonomous agents plan across multiple tool interactions, receive feedback from real-world execution environments, and optimize for sparse terminal rewards (task success/failure).}
\caption{从聊天机器人到自主智能体：传统LLM聊天机器人在单步对话循环中运行，获得即时的人类反馈。自主智能体则在多个工具交互中进行规划，从真实执行环境中接收反馈，并针对稀疏的终端奖励（任务成功/失败）进行优化。}
\end{figure}

The key differences that demand new RL approaches:  
这些关键差异催生了对新强化学习方法的需求：

\begin{itemize}
  \item \textbf{Multi-step reasoning}: Agents must plan across 10--100+ tool calls, not just generate a single response.
  \item \textbf{External environment feedback}: Rewards come from real-world execution (test suites pass, web pages load, code compiles) --- not just human preference scores.
  \item \textbf{Structured actions}: Actions are not just tokens but structured outputs (JSON tool calls, API payloads, code blocks).
  \item \textbf{Long horizons with sparse rewards}: Success/failure may only be determined after many intermediate steps.
\end{itemize}

\begin{itemize}
  \item \textbf{多步推理（Multi-step reasoning）}：智能体必须在10~100+个工具调用之间进行规划，而不仅仅是生成单一回复。
  \item \textbf{外部环境反馈（External environment feedback）}：奖励来自真实世界的执行结果（测试套件通过、网页加载成功、代码编译通过），而不仅仅是人类偏好分数。
  \item \textbf{结构化动作（Structured actions）}：动作不仅仅是token，而是结构化输出（JSON工具调用、API负载、代码块）。
  \item \textbf{长视野与稀疏奖励（Long horizons with sparse rewards）}：成功/失败可能只有在许多中间步骤之后才能确定。
\end{itemize}

\begin{intuitionbox}[Why Standard RLHF Falls Short for Agents]
Standard RLHF (PPO/DPO) optimizes for single-turn quality: given a prompt, produce a good response. But agents must:
\begin{intuitionbox}[为什么标准RLHF对智能体力不从心]
标准RLHF（PPO/DPO）针对单轮质量进行优化：给定提示，生成一个好的回复。但智能体必须：

\begin{itemize}
  \item Decide \emph{when} to use tools vs. reason internally
  \item Recover from errors mid-trajectory (self-correction)
  \item Balance exploration (try new approaches) with exploitation (use known-good patterns)
  \item Handle partial observability (tool outputs may be incomplete or noisy)
\end{itemize}

\begin{itemize}
  \item 决定\emph{何时}使用工具，何时进行内部推理
  \item 在轨迹中途从错误中恢复（自我纠正）
  \item 平衡探索（尝试新方法）与利用（使用已知良好模式）
  \item 处理部分可观测性（工具输出可能不完整或带有噪声）
\end{itemize}

This requires training methods that reason over \textbf{entire trajectories}, not individual turns.
\end{intuitionbox}
这需要能够在\textbf{整个轨迹}上进行推理的训练方法，而非单个回合。
\end{intuitionbox}

\section{Trajectory Buffers for LLM Agents}
\section{LLM智能体的轨迹缓冲区}

In the context of LLM agents, traditional RL replay buffers undergo a structural transformation. Instead of storing low-dimensional numerical tensors, agentic buffers --- often called \textbf{Trajectory Buffers}, \textbf{Experience Pools}, or \textbf{Memory Banks} --- manage complex textual histories, tool execution outputs, and explicit reasoning steps.
在LLM智能体的背景下，传统的RL回放缓冲区经历了结构性的转变。智能体缓冲区（通常被称为\textbf{轨迹缓冲区（Trajectory Buffers）}、\textbf{经验池（Experience Pools）}或\textbf{记忆库（Memory Banks）}）不再存储低维数值张量，而是管理复杂的文本历史、工具执行输出和显式的推理步骤。

\subsection{Mathematical Structure of an LLM Agent Buffer}
\subsection{LLM智能体缓冲区的数学结构}

In classic RL, a replay buffer stores a flat tuple $(s, a, r, s')$. For an LLM agent, this expands into high-dimensional tokenized text structures:
在经典RL中，回放缓冲区存储一个扁平的元组 $(s, a, r, s')$。对于LLM智能体，这扩展为高维的token化文本结构：

\begin{equation}
\boxed{e_t = \left( \mathcal{S}_t,\; \mathcal{A}_t,\; \mathcal{R}_t,\; \mathcal{S}_{t+1} \right)}
\end{equation}

\begin{itemize}
  \item $\mathcal{S}_t$: The \textbf{complete context state} --- system prompt, user objective, conversation history, and current environmental variables (e.g., HTML source code, directory structures, database schemas).
  \item $\mathcal{A}_t$: The agent’s \textbf{generated output}, typically composed of a Chain-of-Thought (CoT) reasoning string followed by a structured tool call: 
\begin{equation}
\mathcal{A}_t = \{\text{text}_{\text{reasoning}},\; \text{json}_{\text{tool\_call}}\}
\end{equation}
  \item $\mathcal{R}_t$: \textbf{Evaluation signals} derived from external execution environments (unit test passes, compiler flags, API response codes) or verified by an LLM-as-a-judge system.
  \item $\mathcal{S}_{t+1}$: The \textbf{updated context window}, which appends tool output text or error logs directly into the conversation history.
\end{itemize}

\begin{itemize}
  \item $\mathcal{S}_t$：\textbf{完整的上下文状态}——系统提示、用户目标、对话历史以及当前环境变量（例如HTML源码、目录结构、数据库模式）。
  \item $\mathcal{A}_t$：智能体的\textbf{生成输出}，通常由链式思维（CoT）推理字符串后跟结构化工具调用组成：
\begin{equation}
\mathcal{A}_t = \{\text{text}_{\text{reasoning}},\; \text{json}_{\text{tool\_call}}\}
\end{equation}
  \item $\mathcal{R}_t$：\textbf{评估信号}，来自外部执行环境（单元测试通过、编译器标志、API响应码）或由LLM-as-a-judge系统验证。
  \item $\mathcal{S}_{t+1}$：\textbf{更新后的上下文窗口}，它将工具输出文本或错误日志直接附加到对话历史中。
\end{itemize}

\begin{examplebox}[Concrete Agent Trajectory: Code Debugging]
\textbf{Step 1}: $\mathcal{S}_1$ = ``Fix the failing test in \texttt{utils.py}''\\


$\mathcal{A}_1$ = \emph{``Let me read the file first''} + \texttt{read\_file("utils.py")}\\


$\mathcal{R}_1$ = 0 (intermediate step)\\


\textbf{Step 2}: $\mathcal{S}_2$ = [previous context + file contents]\\


$\mathcal{A}_2$ = \emph{``The bug is on line 42, off-by-one error''} + \texttt{edit\_file("utils.py", ...)}\\


$\mathcal{R}_2$ = 0 (intermediate step)\\


\textbf{Step 3}: $\mathcal{S}_3$ = [previous context + edit confirmation]\\


$\mathcal{A}_3$ = \emph{``Let me verify the fix''} + \texttt{run\_tests()}\\


$\mathcal{R}_3$ = +1.0 (all tests pass --- sparse terminal reward)
\end{examplebox}

\begin{examplebox}[具体智能体轨迹：代码调试]
\textbf{步骤1}：$\mathcal{S}_1$ = “修复 \texttt{utils.py} 中的失败测试”\\

$\mathcal{A}_1$ = \emph{“让我先读取文件”} + \texttt{read\_file("utils.py")}\\

$\mathcal{R}_1$ = 0（中间步骤）\\

\textbf{步骤2}：$\mathcal{S}_2$ = [之前的上下文 + 文件内容]\\

$\mathcal{A}_2$ = \emph{“bug在第42行，差一错误”} + \texttt{edit\_file("utils.py", ...)}\\

$\mathcal{R}_2$ = 0（中间步骤）\\

\textbf{步骤3}：$\mathcal{S}_3$ = [之前的上下文 + 编辑确认]\\

$\mathcal{A}_3$ = \emph{“让我验证修复”} + \texttt{run\_tests()}\\

$\mathcal{R}_3$ = +1.0（所有测试通过——稀疏终端奖励）
\end{examplebox}

\section{Operational Paradigms}
\section{操作范式}

LLM agents leverage specialized trajectory buffers through three primary optimization methodologies:
LLM智能体通过三种主要优化方法利用专门的轨迹缓冲区：

\subsection{A. Self-Correction and Thought Refinement}
\subsection{A. 自我纠正与思维精炼}

Two representative methods in this category are STaR \cite{zelikman2022star} and Reflexion \cite{shinn2023reflexion}. When an agent fails a multi-step execution trace, the sub-optimal sequence is saved to the buffer. The framework later samples this trajectory and prompts the LLM to generate an explicit textual critique of its past performance: 
该类方法中有两个代表性方法：STaR \cite{zelikman2022star} 和 Reflexion \cite{shinn2023reflexion}。当智能体在多步执行轨迹中失败时，次优序列被保存到缓冲区中。框架随后采样该轨迹，并提示LLM对其过去的表现生成明确的文本批评：

\begin{equation}
\text{Critique} \leftarrow \text{LLM}(\mathcal{S}_{\text{failed}},\; \mathcal{A}_{\text{failed}},\; \mathcal{R}_{=0})
\end{equation}

Once a corrected trajectory achieves a positive reward, it is moved to an optimal experience pool used to update the network weights via fine-tuning (SFT on successful trajectories) or RL (GRPO~\cite{shao2024deepseekmath} with binary pass/fail rewards).
一旦修正后的轨迹获得了正奖励，它就会被移到一个最优经验池中，用于通过微调（在成功轨迹上进行SFT）或强化学习（使用二元通过/失败奖励的GRPO~\cite{shao2024deepseekmath}）来更新网络权重。

\begin{keybox}[STaR: Self-Taught Reasoner]
\begin{enumerate}
  \item Generate reasoning traces for a batch of problems
  \item Filter: keep only traces that lead to correct answers
  \item Fine-tune the model on successful traces (SFT)
  \item Repeat: the improved model generates better traces in the next iteration
\end{enumerate}
\end{keybox}

\begin{keybox}[STaR：自训推理器]
\begin{enumerate}
  \item 对一批问题生成推理轨迹
  \item 过滤：只保留能得到正确答案的轨迹
  \item 在成功的轨迹上对模型进行微调（SFT）
  \item 重复：改进后的模型在下一轮迭代中生成更好的轨迹
\end{enumerate}
\end{keybox}

## \subsection{B. Off-Policy Exploration}
## \subsection{B. 离策略探索}
\label{b.-off-policy-exploration-react-tool-use-frameworks}
\label{b.-off-policy-exploration-react-tool-use-frameworks}

This paradigm, exemplified by ReAct \cite{yao2023react} and related tool-use frameworks, involves extensive autonomous exploration. During autonomous exploration (web navigation, database querying, code generation), agents log thousands of exploratory execution paths. The trajectory buffer acts as a filter:
这一范式以 ReAct \cite{yao2023react} 及相关的工具使用框架为代表，涉及大规模的自主探索。在自主探索过程中（如网页导航、数据库查询、代码生成），智能体会记录数千条探索性执行路径。轨迹缓冲区（trajectory buffer）起到了过滤器的作用：

\begin{itemize}
  \item \textbf{Success filtering}: Only trajectories achieving the goal are kept for training.
  \item \textbf{Success filtering（成功过滤）}：仅保留达成目标的轨迹用于训练。
  \item \textbf{Efficiency ranking}: Among successful traces, prefer the shortest/most efficient tool-use paths.
  \item \textbf{Efficiency ranking（效率排序）}：在成功轨迹中，优先选择最短/最高效的工具使用路径。
  \item \textbf{Diversity sampling}: Maintain a diverse set of solution strategies to prevent mode collapse.
  \item \textbf{Diversity sampling（多样性采样）}：维护多样化的解决策略以防止模式崩溃（mode collapse）。
\end{itemize}

The optimization algorithm (typically GRPO~\cite{shao2024deepseekmath} or filtered SFT) computes losses exclusively over efficient, successful trajectories while discarding meandering runs.
优化算法（通常是 GRPO~\cite{shao2024deepseekmath} 或过滤后的 SFT）仅针对高效、成功的轨迹计算损失，同时丢弃冗长低效的运行。

## \subsection{C. Non-Parametric In-Context Learning (RAG over Experiences)}
## \subsection{C. 非参数化上下文学习（基于经验检索增强生成）}
\label{c.-non-parametric-in-context-learning-rag-over-experiences}
\label{c.-non-parametric-in-context-learning-rag-over-experiences}

Instead of modifying neural network weights, the trajectory buffer can function as a \textbf{vector database}. Given a new user goal $\mathcal{G}_{\text{new}}$, the system retrieves the most relevant past experiences:
轨迹缓冲区可以充当\textbf{向量数据库}，而无需修改神经网络权重。给定一个新的用户目标 $\mathcal{G}_{\text{new}}$，系统会检索最相关的历史经验：
\begin{equation}
\boxed{\mathcal{E}_{\text{retrieved}} = \arg\max_{e \in \mathcal{B}} \text{sim}\!\left(\text{Embed}(\mathcal{G}_{\text{new}}),\; \text{Embed}(e)\right)}
\end{equation}

The top-$k$ similar successful historical runs are injected directly into the prompt context as few-shot demonstrations. This approach:
前 $k$ 个最相似的成功历史运行会作为少样本示例直接注入到提示上下文中。这种方法：

\begin{itemize}
  \item Requires \textbf{zero training} --- pure retrieval-augmented generation
  \item 需要\textbf{零训练}（zero training）——纯粹的检索增强生成（retrieval-augmented generation）
  \item Adapts instantly to new tasks if similar experiences exist in the buffer
  \item 如果缓冲区中存在类似经验，则可立即适应新任务
  \item Scales with buffer size (more experiences = better coverage)
  \item 随缓冲区大小扩展（经验越多 = 覆盖范围越广）
  \item Complements parametric learning (use retrieval for rare cases, weights for common patterns)
  \item 补充参数化学习（对罕见情况使用检索，对常见模式使用权重）
\end{itemize}

## \section{Paradigm Comparison}
## \section{范式对比}
\label{paradigm-comparison}
\label{paradigm-comparison}

\begin{table}[ht!]
\centering
\caption{Traditional RL Buffers vs. LLM Agent Buffers}
\caption{传统强化学习缓冲区 vs. 大语言模型智能体缓冲区}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Feature} & \textbf{Traditional RL Buffer} & \textbf{LLM Agent Buffer} \\
\textbf{特征} & \textbf{传统强化学习缓冲区} & \textbf{大语言模型智能体缓冲区} \\
\midrule
\textbf{Data Format} & Continuous vectors / tensors & Tokenized text, JSON, code blocks, tool outputs \\
\textbf{数据格式} & 连续向量/张量 & 分词文本、JSON、代码块、工具输出 \\
\textbf{Data Volume} & Massive ($10^5$--$10^7$ items) & Small to medium ($10^3$--$10^5$ traces) \\
\textbf{数据量} & 海量（$10^5$--$10^7$ 项） & 小到中等（$10^3$--$10^5$ 条轨迹） \\
\textbf{Primary Goal} & Breaking data correlation & Providing reasoning demonstrations \\
\textbf{主要目标} & 打破数据相关性 & 提供推理示例 \\
\textbf{Sampling} & Random uniform / PER & Semantic retrieval / success priority / diversity \\
\textbf{采样方式} & 随机均匀/优先级经验回放 & 语义检索/成功优先/多样性 \\
\textbf{State Size} & Fixed (e.g., 84$\times$84 pixels) & Variable (1K--128K tokens per state) \\
\textbf{状态大小} & 固定（例如 84$\times$84 像素） & 可变（每状态 1K--128K 令牌） \\
\textbf{Action Space} & Discrete/continuous vectors & Structured text (reasoning + tool calls) \\
\textbf{动作空间} & 离散/连续向量 & 结构化文本（推理 + 工具调用） \\
\textbf{Reward Source} & Environment simulator & External execution / LLM judge / unit tests \\
\textbf{奖励来源} & 环境模拟器 & 外部执行/大语言模型评估器/单元测试 \\
\bottomrule
\end{tabular}
\end{table}

## \section{Major Techniques in Agentic RL}
## \section{智能体强化学习主要技术}
\label{major-techniques-in-agentic-rl}
\label{major-techniques-in-agentic-rl}

\begin{table}[ht!]
\centering
\caption{Key methods for training LLM agents with RL.}
\caption{使用强化学习训练大语言模型智能体的关键方法。}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Method} & \textbf{Type} & \textbf{Key Idea} \\
\textbf{方法} & \textbf{类型} & \textbf{核心思想} \\
\midrule
\textbf{STaR}~\cite{zelikman2022star} & Iterative SFT & Bootstrap reasoning by fine-tuning on own successful traces \\
\textbf{STaR}~\cite{zelikman2022star} & 迭代式有监督微调 & 通过在自己的成功轨迹上微调来引导推理 \\
\textbf{Reflexion}~\cite{shinn2023reflexion} & In-context RL & Verbal self-critique stored as episodic memory; no weight updates \\
\textbf{Reflexion}~\cite{shinn2023reflexion} & 上下文强化学习 & 以情景记忆形式存储的言语自我批评；无需权重更新 \\
\textbf{ReAct}~\cite{yao2023react} & Prompting & Interleave reasoning (``think'') and acting (``tool call'') in a single generation \\
\textbf{ReAct}~\cite{yao2023react} & 提示工程 & 在单次生成中交错进行推理（“思考”）和行动（“工具调用”） \\
\textbf{LATS}~\cite{zhou2024lats} & Tree search & Monte Carlo Tree Search over action sequences; backpropagate rewards \\
\textbf{LATS}~\cite{zhou2024lats} & 树搜索 & 对动作序列进行蒙特卡洛树搜索；反向传播奖励 \\
\textbf{AgentQ}~\cite{putta2024agentq} & Off-policy RL & DPO on agent trajectories with AI-generated preference pairs \\
\textbf{AgentQ}~\cite{putta2024agentq} & 离策略强化学习 & 在智能体轨迹上使用人工智能生成的偏好对进行直接偏好优化 \\
\textbf{OpenHands}~\cite{wang2024openhands} & GRPO & Group-relative optimization with execution-based rewards (tests pass/fail) \\
\textbf{OpenHands}~\cite{wang2024openhands} & 群体相对策略优化 & 基于执行奖励（测试通过/失败）的群体相对优化 \\
\textbf{Voyager}~\cite{wang2023voyager} & Skill library & Successful code snippets stored and retrieved for compositional reuse \\
\textbf{Voyager}~\cite{wang2023voyager} & 技能库 & 存储成功代码片段并可检索以进行组合复用 \\
\textbf{RLEF}~\cite{le2024rlef} & Online RL & RL from Execution Feedback --- binary reward from code/test execution \\
\textbf{RLEF}~\cite{le2024rlef} & 在线强化学习 & 基于执行反馈的强化学习——来自代码/测试执行的二元奖励 \\
\bottomrule
\end{tabular}
\end{table}

## \subsection{STaR: Self-Taught Reasoner (Detailed)}
## \subsection{STaR：自训练推理器（详细）}
\label{star-self-taught-reasoner-detailed}
\label{star-self-taught-reasoner-detailed}

STaR~\cite{zelikman2022star} is an \textbf{iterative self-improvement} method that bootstraps reasoning capabilities without external reward models. The core insight: if the model can occasionally solve a problem correctly, it can learn from its own successes.
STaR~\cite{zelikman2022star} 是一种\textbf{迭代式自我改进}方法，无需外部奖励模型即可引导推理能力。其核心见解是：如果模型偶尔能正确解决问题，它就可以从自己的成功中学习。

\textbf{Algorithm}:
\textbf{算法}：

\begin{enumerate}
  \item \textbf{Generate}: For each problem $x_i$ in dataset $\mathcal{D}$, sample a reasoning trace $z_i \sim \pi_\theta(\cdot | x_i)$ followed by an answer $\hat{y}_i$.
  \item \textbf{生成}：对于数据集 $\mathcal{D}$ 中的每个问题 $x_i$，采样一个推理轨迹 $z_i \sim \pi_\theta(\cdot | x_i)$，然后生成答案 $\hat{y}_i$。
  \item \textbf{Filter}: Keep only traces where $\hat{y}_i = y_i^*$ (correct answer). Define success set $\mathcal{D}_{\text{pass}} = \{(x_i, z_i, y_i^*) : \hat{y}_i = y_i^*\}$.
  \item \textbf{过滤}：仅保留 $\hat{y}_i = y_i^*$（正确答案）的轨迹。定义成功集 $\mathcal{D}_{\text{pass}} = \{(x_i, z_i, y_i^*) : \hat{y}_i = y_i^*\}$。
  \item \textbf{Rationalization} (key innovation): For problems where the model failed, generate a ``rationalization'' --- a trace conditioned on the correct answer: $z_i^{\text{rat}} \sim \pi_\theta(\cdot | x_i, y_i^*)$. This teaches the model to reason \emph{backward} from solutions.
  \item \textbf{合理化（rationalization）}（关键创新）：对于模型失败的问题，生成一个“合理化”轨迹——以正确答案为条件的轨迹：$z_i^{\text{rat}} \sim \pi_\theta(\cdot | x_i, y_i^*)$。这教会模型从解出发进行\emph{反向}推理。
  \item \textbf{Fine-tune}: Update $\theta$ via SFT on $\mathcal{D}_{\text{pass}} \cup \mathcal{D}_{\text{rationalized}}$.
  \item \textbf{微调}：在 $\mathcal{D}_{\text{pass}} \cup \mathcal{D}_{\text{rationalized}}$ 上通过有监督微调更新 $\theta$。
  \item \textbf{Iterate}: Repeat from step 1 with the improved model.
  \item \textbf{迭代}：使用改进后的模型从步骤1重复。
\end{enumerate}

\begin{equation}
\boxed{\theta_{k+1} = \arg\min_\theta -\sum_{(x,z,y) \in \mathcal{D}_k^+} \log \pi_\theta(z, y | x)}
\end{equation}

\textbf{Convergence dynamics}: Each iteration $k$ increases the model’s solve rate $p_k$. If $p_0 = 0.3$ (solves 30\% of problems), after rationalization + SFT, $p_1 \approx 0.5$. Typically converges in 3--5 iterations to $p \approx 0.7$--$0.9$.
\textbf{收敛动态}：每次迭代 $k$ 都会提高模型的求解率 $p_k$。如果 $p_0 = 0.3$（解决 30% 的问题），经过合理化 + 有监督微调后，$p_1 \approx 0.5$。通常在 3--5 次迭代后收敛到 $p \approx 0.7$--$0.9$。

\begin{examplebox}[STaR Rationalization Prompt]
\begin{examplebox}[STaR 合理化提示示例]
\begin{lstlisting}[style=pythonstyle]
# Standard generation (Step 1):
PROMPT = """Solve the following problem step by step.
Problem: A store has 45 apples. It sells 3/5 of them. How many remain?
Let's think step by step:"""
\end{lstlisting}
\end{examplebox}

\begin{intuitionbox}[STaR Variants for Agents]
\begin{intuitionbox}[STaR的智能体变体]
\begin{itemize}
  \item \textbf{Quiet-STaR}~\cite{zelikman2024quietstar}: Inserts ``thinking tokens'' between every token of generation. The model learns to reason \emph{implicitly} without explicit CoT prompting. Training objective: predict next tokens better when thinking tokens are included.
  \item \textbf{Quiet-STaR}~\cite{zelikman2024quietstar}：在每个生成令牌之间插入“思考令牌”。模型学习在不显式使用CoT提示的情况下进行\textit{隐式}推理。训练目标：当包含思考令牌时，更好地预测下一个令牌。
  \item \textbf{STaR for Code Agents}: Replace answer verification with test execution. ``Correct'' = all tests pass. Rationalization = generate a new approach conditioned on the error message.
  \item \textbf{代码智能体的STaR}：用测试执行替代答案验证。“正确”=所有测试通过。合理化（Rationalization）=根据错误信息生成新的方法。
  \item \textbf{V-STaR}~\cite{hosseini2024vstar}: Adds a verifier model trained on $(z, y, \text{correct/incorrect})$ triples. The verifier provides process-level supervision, filtering bad reasoning traces that accidentally reach correct answers.
  \item \textbf{V-STaR}~\cite{hosseini2024vstar}：添加一个在$(z, y, \text{正确/错误})$三元组上训练的验证器模型。验证器提供过程级监督，过滤那些偶然得到正确答案的糟糕推理轨迹。
\end{itemize}
\end{intuitionbox}
\end{intuitionbox}

\subsection{Reflexion: Verbal Reinforcement Learning (Detailed)}
\subsection{Reflexion：基于语言模型的强化学习（详细）}
\label{reflexion-verbal-reinforcement-learning-detailed}

Reflexion~\cite{shinn2023reflexion} introduces a radical paradigm: \textbf{RL without weight updates}. Instead of gradient-based learning, the agent improves through natural-language self-critique stored in an episodic memory.

Reflexion~\cite{shinn2023reflexion} 引入了一个激进的范式：\textbf{不更新权重的强化学习}。智能体不是通过基于梯度的学习，而是通过存储在情景记忆中的自然语言自我批评来改进。

\textbf{Full Architecture}:

\textbf{完整架构}：

\begin{enumerate}
  \item \textbf{Actor}: The LLM agent $\pi$ that executes actions in the environment.
  \item \textbf{Actor（行动者）}：在环境中执行动作的LLM智能体 $\pi$。
  \item \textbf{Evaluator}: A binary signal (task success/failure) or a scalar heuristic (e.g., number of test cases passed).
  \item \textbf{Evaluator（评估器）}：一个二元信号（任务成功/失败）或一个标量启发式（例如，通过的测试用例数量）。
  \item \textbf{Self-Reflection Generator}: Given the failed trajectory $\tau_{\text{fail}}$ and environment feedback, generates a natural-language reflection $r_{\text{text}}$: 
  \item \textbf{Self-Reflection Generator（自我反思生成器）}：给定失败轨迹 $\tau_{\text{fail}}$ 和环境反馈，生成一个自然语言反思 $r_{\text{text}}$：
\begin{equation}
r_{\text{text}} = \text{LLM}_{\text{reflect}}\!\left(\tau_{\text{fail}}, \text{feedback}, \text{task}\right)
\end{equation}
  \item \textbf{Episodic Memory}: A sliding window buffer $\mathcal{M} = [r_1, r_2, \ldots, r_m]$ of past reflections (typically $m \leq 3$ to fit in context).
  \item \textbf{Episodic Memory（情景记忆）}：一个滑动窗口缓冲区 $\mathcal{M} = [r_1, r_2, \ldots, r_m]$，用于存储过去的反思（通常 $m \leq 3$ 以适应上下文）。
  \item \textbf{Retry Loop}: On the next attempt, reflections are injected into the prompt: 
  \item \textbf{Retry Loop（重试循环）}：在下次尝试时，将反思注入到提示中：
\begin{equation}
a_{t+1} \sim \pi\!\left(\cdot\; |\; \text{task},\; \mathcal{M},\; \text{current\_state}\right)
\end{equation}
\end{enumerate}

\textbf{Example reflection}: \emph{``In my previous attempt, I called the search API before validating the input format, which caused a 400 error. Next time, I should validate the JSON schema first, then make the API call.''}

\textbf{示例反思}：\emph{“在之前的尝试中，我在验证输入格式之前调用了搜索API，导致400错误。下次我应该先验证JSON模式，然后再调用API。”}

\begin{examplebox}[Reflexion: Agent Prompt with Injected Memory]
\begin{examplebox}[Reflexion：注入记忆的智能体提示]
\begin{lstlisting}[style=pythonstyle]
# === ATTEMPT 2 PROMPT (after first failure) ===


SYSTEM = """You are a coding agent. You can run bash commands and edit files.
Complete the task below. Learn from your previous reflections."""


USER = """Task: Fix the failing test in auth_service.py


=== REFLECTIONS FROM PREVIOUS ATTEMPTS ===
[Attempt 1 reflection]: I tried to modify the authenticate() function
directly but forgot that it depends on token_validator(). The test
failed because token_validator() was still returning the old format.
I should trace the dependency chain FIRST: check what authenticate()
calls, then fix the root cause (token_validator), not the symptom.
=== END REFLECTIONS ===


The repository is in /workspace/. The failing test is:
  test_auth.py::test_expired_token_returns_401


Begin by reading the relevant files, then fix the issue."""
\end{lstlisting}
\end{examplebox}

\begin{lstlisting}[style=pythonstyle]
# === 第2次尝试的提示（首次失败后）===


SYSTEM = """你是一个编码智能体。你可以运行bash命令和编辑文件。
完成下面的任务。从你之前的反思中学习。"""


USER = """任务：修复 auth_service.py 中失败的测试


=== 来自之前尝试的反思 ===
[第1次尝试反思]：我直接修改了 authenticate() 函数，
但忘记它依赖于 token_validator()。测试失败是因为 token_validator() 仍然返回旧格式。
我应该先追踪依赖链：检查 authenticate() 调用了什么，然后修复根本原因（token_validator），而不是症状。
=== 反思结束 ===


仓库位于 /workspace/。失败的测试是：
  test_auth.py::test_expired_token_returns_401


首先读取相关文件，然后修复问题。"""
\end{lstlisting}
\end{examplebox}

\textbf{Strengths and Limitations}:

\textbf{优势与局限}：

{\small
\begin{tabular}{@{}p{7.5cm}p{7.5cm}@{}}
\toprule
\textbf{Strengths} & \textbf{Limitations} \\
\midrule
Zero gradient computation; works with frozen API models (GPT-4) & Limited to context window; can’t accumulate infinite knowledge \\
Fast iteration (seconds per retry vs. hours for RL training) & No generalization to unseen tasks (memory is task-specific) \\
Interpretable: human-readable self-corrections & Relies on the model’s existing ability to identify errors \\
Composes with any base agent architecture & Degrades when base model is too weak to generate useful critiques \\
\bottomrule
\end{tabular}
}

{\small
\begin{tabular}{@{}p{7.5cm}p{7.5cm}@{}}
\toprule
\textbf{优势} & \textbf{局限} \\
\midrule
零梯度计算；适用于冻结的API模型（GPT-4） & 受限于上下文窗口；无法积累无限知识 \\
快速迭代（每次重试几秒，而RL训练需数小时） & 无法泛化到未见任务（记忆是任务特定的） \\
可解释性：人类可读的自我修正 & 依赖模型现有的识别错误能力 \\
可与任何基础智能体架构组合 & 当基础模型太弱而无法生成有效批评时性能下降 \\
\bottomrule
\end{tabular}
}

\subsection{ReAct: Reasoning + Acting (Detailed)}
\subsection{ReAct：推理+行动（详细）}
\label{react-reasoning-acting-detailed}

ReAct~\cite{yao2023react} establishes the dominant prompting paradigm for tool-using agents by \textbf{interleaving explicit reasoning steps with environment actions} in a single generation stream.

ReAct~\cite{yao2023react} 通过\textbf{在单个生成流中交错显式推理步骤与环境动作}，确立了使用工具的智能体的主要提示范式。

\begin{examplebox}[ReAct System Prompt (Typical)]
\begin{examplebox}[ReAct系统提示（典型）]
\begin{lstlisting}[style=pythonstyle]
SYSTEM = """You are a research assistant with access to the following tools:
- search(query): Search the web for information
- lookup(term): Look up a term on the current Wikipedia page
- finish(answer): Submit your final answer


Solve the user's question by interleaving Thought and Action steps.
Format:
  Thought: <your reasoning about what to do next>
  Action: <tool_name>(arguments)


You will receive an Observation after each Action. Use it to plan
your next step. Continue until you can provide a final answer.


Rules:
- Always think before acting
- Never guess - verify with tools
- Use finish() only when you are confident in your answer"""


USER = "Who was the president of the US when the iPhone was released?"
\end{lstlisting}
\end{examplebox}

\begin{lstlisting}[style=pythonstyle]
SYSTEM = """你是一个研究助理，可以使用以下工具：
- search(query)：在网络上搜索信息
- lookup(term)：在当前维基百科页面上查找术语
- finish(answer)：提交你的最终答案


通过交错Thought（思考）和Action（行动）步骤来解决用户的问题。
格式：
  Thought: <你关于下一步该做什么的推理>
  Action: <工具名称>(参数)


每次Action后你将收到一个Observation（观察结果）。利用它来规划下一步。
继续直到你可以给出最终答案。


规则：
- 总是先思考后行动
- 永远不要猜测——使用工具验证
- 只有在你对自己的答案有信心时才使用finish()"""


USER = "iPhone发布时美国总统是谁？"
\end{lstlisting}
\end{examplebox}

\textbf{Generation format}:

\textbf{生成格式}：

\begin{examplebox}[ReAct Trace Format]
\begin{examplebox}[ReAct轨迹格式]
\begin{lstlisting}[style=pythonstyle]
Thought: I need to find when the iPhone was released, then determine
who was president at that time. Let me search for the release date.
Action: search("iPhone original release date")
Observation: The original iPhone was released on June 29, 2007.
Thought: The iPhone came out June 2007. Now I need to find who was
the US president in June 2007.
Action: lookup("President of the United States in 2007")
Observation: George W. Bush served as the 43rd president from
January 20, 2001 to January 20, 2009.
Thought: George W. Bush was president from 2001-2009, which covers
June 2007 when the iPhone was released. I have my answer.
Action: finish("George W. Bush was the US president when the iPhone
was released on June 29, 2007.")
\end{lstlisting}
\end{examplebox}

\begin{lstlisting}[style=pythonstyle]
Thought: 我需要找到iPhone的发布时间，然后确定当时谁是美国总统。让我搜索发布日期。
Action: search("iPhone original release date")
Observation: 最初的iPhone于2007年6月29日发布。
Thought: iPhone于2007年6月推出。现在我需要找出2007年6月谁是美国总统。
Action: lookup("President of the United States in 2007")
Observation: 乔治·W·布什从2001年1月20日到2009年1月20日担任第43任总统。
Thought: 乔治·W·布什从2001年到2009年担任总统，涵盖了2007年6月iPhone发布的时间。我有答案了。
Action: finish("乔治·W·布什是美国总统，当时iPhone于2007年6月29日发布。")
\end{lstlisting}
\end{examplebox}

\textbf{Formal definition}: A ReAct trajectory is $\tau = (t_1, a_1, o_1, t_2, a_2, o_2, \ldots)$ where:

\textbf{正式定义}：一个ReAct轨迹是 $\tau = (t_1, a_1, o_1, t_2, a_2, o_2, \ldots)$，其中：

\begin{itemize}
  \item $t_i$: Thought (internal reasoning, not executed)
  \item $t_i$：思考（内部推理，不执行）
  \item $a_i$: Action (tool call, executed in environment)
  \item $a_i$：行动（工具调用，在环境中执行）
  \item $o_i$: Observation (environment response, appended to context)
  \item $o_i$：观察结果（环境响应，附加到上下文中）
\end{itemize}

\textbf{Why it works}: Thoughts create an ``inner monologue'' that helps the model plan before acting, reducing impulsive tool calls. The explicit reasoning trace also makes the agent’s decision process \textbf{auditable} and \textbf{debuggable}.

\textbf{为什么有效}：思考创建了一个“内心独白”，帮助模型在行动前进行规划，减少冲动的工具调用。显式的推理轨迹也使智能体的决策过程变得\textbf{可审计}和\textbf{可调试}。

\textbf{Training ReAct agents with RL}:

\textbf{用RL训练ReAct智能体}：

\begin{itemize}
  \item \textbf{Action-level rewards}: Only actions receive reward signals (thoughts are auxiliary).
  \item \textbf{行动级奖励}：只有行动接收奖励信号（思考是辅助的）。
  \item \textbf{Thought quality}: Implicitly optimized --- better thoughts $\rightarrow$ better actions $\rightarrow$ higher rewards.
  \item \textbf{思考质量}：隐式优化——更好的思考 $\rightarrow$ 更好的行动 $\rightarrow$ 更高的奖励。
  \item \textbf{Format enforcement}: Include format penalties in the reward for malformed actions (missing JSON, hallucinated tools).
  \item \textbf{格式强制}：在奖励中包含格式惩罚，用于格式错误的行动（缺少JSON、幻觉工具）。
  \item \textbf{RL objective}: $r(\tau) = r_{\text{task}} - \lambda_{\text{format}} \cdot \text{format\_violations} - \lambda_{\text{length}} \cdot \text{num\_steps}$
  \item \textbf{RL目标}：$r(\tau) = r_{\text{task}} - \lambda_{\text{format}} \cdot \text{format\_violations} - \lambda_{\text{length}} \cdot \text{num\_steps}$
\end{itemize}

\subsection{LATS: Language Agent Tree Search (Detailed)}
\subsection{LATS：语言智能体树搜索（详细）}
\label{lats-language-agent-tree-search-detailed}

LATS~\cite{zhou2024lats} applies \textbf{Monte Carlo Tree Search (MCTS)} to LLM agent action selection, trading inference compute for significantly better trajectories.

LATS~\cite{zhou2024lats} 将\textbf{蒙特卡洛树搜索（MCTS）}应用于LLM智能体的动作选择，用推理计算换取显著更优的轨迹。

\textbf{Algorithm (adapted for LLM agents)}:

\textbf{算法（针对LLM智能体调整）}：

\begin{enumerate}
  \item \textbf{Selection}: Starting from root (initial state), traverse the tree using UCB1: 
\begin{equation}
\text{UCB}(s, a) = \bar{Q}(s, a) + c \sqrt{\frac{\ln N(s)}{N(s, a)}}
\end{equation}
 where $\bar{Q}$ = average reward of subtree, $N$ = visit counts, $c$ = exploration constant.
  \item \textbf{Expansion}: At a leaf node, generate $k$ candidate actions via LLM sampling (temperature $> 0$): $\{a_1, \ldots, a_k\} \sim \pi_\theta(\cdot | s_{\text{leaf}})$
  \item \textbf{Simulation}: For each candidate, execute the action in the environment and continue with a fast rollout policy (greedy decoding) until terminal state or depth limit.
  \item \textbf{Backpropagation}: Propagate the terminal reward up through all ancestor nodes, updating $\bar{Q}$ and $N$ counts.
  \item \textbf{Repeat}: Run steps 1--4 for a fixed computation budget (e.g., 50--200 iterations).
  \item \textbf{Action selection}: Choose the most-visited child of the root.
\end{enumerate}

\begin{enumerate}
  \item \textbf{选择（Selection）}：从根节点（初始状态）开始，使用UCB1遍历树：
\begin{equation}
\text{UCB}(s, a) = \bar{Q}(s, a) + c \sqrt{\frac{\ln N(s)}{N(s, a)}}
\end{equation}
其中 $\bar{Q}$ = 子树平均奖励，$N$ = 访问次数，$c$ = 探索常数。
  \item \textbf{扩展（Expansion）}：在叶子节点处，通过LLM采样（温度 $> 0$）生成 $k$ 个候选动作：$\{a_1, \ldots, a_k\} \sim \pi_\theta(\cdot | s_{\text{leaf}})$
  \item \textbf{模拟（Simulation）}：对每个候选动作，在环境中执行该动作，并使用快速 rollout 策略（贪婪解码）继续运行，直到达到终止状态或深度限制。
  \item \textbf{反向传播（Backpropagation）}：将最终奖励向上传播至所有祖先节点，更新 $\bar{Q}$ 和 $N$ 计数。
  \item \textbf{重复（Repeat）}：在固定计算预算内（例如50–200次迭代）运行步骤1–4。
  \item \textbf{动作选择（Action selection）}：选择根节点中被访问次数最多的子节点。
\end{enumerate}

\textbf{LLM-specific adaptations}:

\textbf{面向LLM的适配}：

\begin{itemize}
  \item \textbf{Value function}: Use a separate LLM call to estimate state value: ``On a scale of 0--1, how likely is this state to lead to task success?''
  \item \textbf{Reflection-based pruning}: When a branch fails, generate a reflection and prune similar branches.
  \item \textbf{Caching}: Store LLM outputs at each node to avoid redundant generation during backtracking.
  \item \textbf{Depth budget}: Limit tree depth to 10--20 steps (agents rarely need more).
\end{itemize}

\begin{itemize}
  \item \textbf{价值函数（Value function）}：使用单独的LLM调用估计状态价值：“在0–1的尺度上，该状态有多大可能导致任务成功？”
  \item \textbf{基于反思的剪枝（Reflection-based pruning）}：当某个分支失败时，生成反思并剪除类似的分支。
  \item \textbf{缓存（Caching）}：在每个节点存储LLM输出，以避免回溯期间重复生成。
  \item \textbf{深度预算（Depth budget）}：将树深度限制在10–20步（智能体很少需要更多）。
\end{itemize}

\textbf{Performance}: On WebShop (web navigation), LATS achieves 75\% success vs. ReAct’s 40\%. On HumanEval (code), pass@1 improves from 68\% $\rightarrow$ 94\% with tree search. The cost: 10--50$\times$ more inference FLOPs per task.

\textbf{性能}：在WebShop（网页导航）上，LATS达到75%成功率，而ReAct为40%。在HumanEval（代码）上，使用树搜索后pass@1从68%提升至$\rightarrow$94%。代价是每个任务花费10–50倍的推理FLOPs。

\begin{examplebox}[LATS Prompts: Value Estimation and Node Expansion]
\begin{lstlisting}[style=pythonstyle]
# === VALUE ESTIMATION PROMPT (used during simulation) ===
VALUE_PROMPT = """You are evaluating an agent's progress on a task.


Task: Book a flight from NYC to London for under \$500, departing Dec 15.


Current state (after 3 actions):
- Searched flights on Kayak: found 12 results
- Filtered by price < \$500: 4 options remain
- Clicked on British Airways \$489 option: viewing details page


On a scale of 0.0 to 1.0, how likely is the agent to successfully
complete the task from this state? Consider:
- How close is the agent to the goal?
- Are there remaining obstacles (payment, seat selection)?
- Has the agent made any errors that need correction?


Score: """  # Model outputs e.g. "0.75"


# === NODE EXPANSION PROMPT (generating candidate actions) ===
EXPAND_PROMPT = """You are a web navigation agent. Given the current
page state, propose 3 DIFFERENT next actions to try.


Current page: British Airways booking - flight details
  Price: \$489 | Departure: Dec 15 8:30am | Arrival: Dec 15 8:45pm
  [Button: Select] [Button: Back to results] [Link: Fare rules]


Generate 3 diverse candidate actions (explore different strategies):
Action 1:"""  # Model generates 3 options for tree expansion
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[LATS提示词：价值估计与节点扩展]
\begin{lstlisting}[style=pythonstyle]
# === 价值估计提示词（模拟阶段使用） ===
VALUE_PROMPT = """你正在评估一个智能体在某个任务上的进展。


任务：预订从纽约到伦敦的航班，预算低于500美元，12月15日出发。


当前状态（经过3个动作后）：
- 在Kayak上搜索航班：找到12个结果
- 按价格<500美元筛选：剩余4个选项
- 点击英国航空489美元选项：正在查看详情页面


在0.0到1.0的尺度上，智能体从该状态成功完成任务的可能性有多大？请考虑：
- 智能体离目标有多近？
- 是否还存在障碍（支付、座位选择）？
- 智能体是否犯了需要纠正的错误？


分数："""  # 模型输出例如"0.75"


# === 节点扩展提示词（生成候选动作） ===
EXPAND_PROMPT = """你是一个网页导航智能体。给定当前
页面状态，建议3种不同的下一步动作尝试。


当前页面：英国航空预订 - 航班详情
  价格：489美元 | 出发：12月15日上午8:30 | 到达：12月15日下午8:45
  [按钮：选择] [按钮：返回结果] [链接：票价规则]


生成3个多样化的候选动作（探索不同策略）：
动作1："""  # 模型为树扩展生成3个选项
\end{lstlisting}
\end{examplebox}

\subsection{AgentQ: DPO on Agent Trajectories (Detailed)}
\label{agentq-dpo-on-agent-trajectories-detailed}

\subsection{AgentQ：在智能体轨迹上进行DPO（详解）}
\label{agentq-dpo-on-agent-trajectories-detailed}

AgentQ~\cite{putta2024agentq} bridges \textbf{offline preference learning (DPO)} with \textbf{online agent execution} by automatically generating preference pairs from trajectory outcomes.

AgentQ~\cite{putta2024agentq} 通过从轨迹结果自动生成偏好对，将\textbf{离线偏好学习（DPO）}与\textbf{在线智能体执行}连接起来。

\textbf{Pipeline}:

\textbf{流程}：

\begin{enumerate}
  \item \textbf{Rollout}: Execute $N$ trajectories per task using the current policy $\pi_\theta$.
  \item \textbf{Evaluate}: Score each trajectory with execution-based reward (binary pass/fail or scalar metric).
  \item \textbf{Pair construction}: For each task, construct preference pairs: 
\begin{equation}
(\tau_w, \tau_l) \text{ where } r(\tau_w) > r(\tau_l)
\end{equation}
 Among trajectories for the same task, the one with highest reward = chosen; lowest = rejected.
  \item \textbf{DPO update}: Apply standard DPO loss over trajectory-level log-probabilities: 
\begin{equation}
\mathcal{L}_{\text{AgentQ}} = -\log \sigma\!\left(\beta \left[\log\frac{\pi_\theta(\tau_w)}{\pi_{\text{ref}}(\tau_w)} - \log\frac{\pi_\theta(\tau_l)}{\pi_{\text{ref}}(\tau_l)}\right]\right)
\end{equation}
  \item \textbf{Iterate}: Updated $\pi_\theta$ generates new (better) trajectories in the next round.
\end{enumerate}

\begin{enumerate}
  \item \textbf{展开（Rollout）}：使用当前策略 $\pi_\theta$ 对每个任务执行 $N$ 条轨迹。
  \item \textbf{评估（Evaluate）}：使用基于执行的奖励（二值通过/失败或标量指标）对每条轨迹评分。
  \item \textbf{对构建（Pair construction）}：对每个任务构建偏好对：
\begin{equation}
(\tau_w, \tau_l) \text{ 其中 } r(\tau_w) > r(\tau_l)
\end{equation}
 同一任务的轨迹中，奖励最高的作为选中轨迹；最低的作为被拒轨迹。
  \item \textbf{DPO更新（DPO update）}：在轨迹级对数概率上应用标准DPO损失：
\begin{equation}
\mathcal{L}_{\text{AgentQ}} = -\log \sigma\!\left(\beta \left[\log\frac{\pi_\theta(\tau_w)}{\pi_{\text{ref}}(\tau_w)} - \log\frac{\pi_\theta(\tau_l)}{\pi_{\text{ref}}(\tau_l)}\right]\right)
\end{equation}
  \item \textbf{迭代（Iterate）}：更新后的 $\pi_\theta$ 在下一轮生成新的（更好的）轨迹。
\end{enumerate}

\textbf{Key design choices}:

\textbf{关键设计选择}：

\begin{itemize}
  \item \textbf{MCTS-guided exploration}: Use LATS during rollout phase to generate diverse, high-quality trajectories (better training data).
  \item \textbf{Step-level DPO}: Instead of comparing full trajectories, compare at the \emph{action level} --- given the same prefix, which next action leads to success?
  \item \textbf{Self-play improvement}: Each DPO iteration produces a better policy that generates better trajectories that produce better training pairs --- a virtuous cycle.
\end{itemize}

\begin{itemize}
  \item \textbf{MCTS引导的探索（MCTS-guided exploration）}：在展开阶段使用LATS生成多样化、高质量的轨迹（更好的训练数据）。
  \item \textbf{步骤级DPO（Step-level DPO）}：不比较完整轨迹，而是在\emph{动作级别}进行比较——给定相同的前缀，哪个下一步动作能够导向成功？
  \item \textbf{自我对弈改进（Self-play improvement）}：每次DPO迭代产生一个更好的策略，该策略生成更好的轨迹，进而产生更好的训练对——这是一个良性循环。
\end{itemize}

\textbf{Results}: On WebShop, AgentQ achieves absolute 50\% $\rightarrow$ 82\% success rate improvement over the base policy in 3 DPO iterations.

\textbf{结果}：在WebShop上，AgentQ在3次DPO迭代中将基础策略的成功率从50%提升至$\rightarrow$82%。

\subsection{Voyager: Lifelong Learning via Skill Libraries (Detailed)}
\label{voyager-lifelong-learning-via-skill-libraries-detailed}

\subsection{Voyager：通过技能库实现终身学习（详解）}
\label{voyager-lifelong-learning-via-skill-libraries-detailed}

Voyager~\cite{wang2023voyager} introduces \textbf{compositional skill accumulation} --- the agent builds a growing library of reusable code functions that serve as high-level actions.

Voyager~\cite{wang2023voyager} 引入了\textbf{组合式技能积累（compositional skill accumulation）}——智能体构建一个不断增长的、可复用的代码函数库，这些函数作为高级动作使用。

\textbf{Architecture}:

\textbf{架构}：

\begin{enumerate}
  \item \textbf{Automatic Curriculum}: An LLM proposes progressively harder tasks based on the agent’s current skill inventory: ``You can now mine wood and craft planks. Next challenge: build a crafting table.''
  \item \textbf{Skill Generation}: For each task, the agent writes a JavaScript function (executable code) that solves it: 
\begin{equation}
\text{skill}_i = \text{LLM}(\text{task}_i, \text{environment\_docs}, \text{error\_feedback})
\end{equation}
  \item \textbf{Verification}: Execute the code in the environment. If it succeeds, add to the skill library. If not, iterate with error feedback (up to 5 retries).
  \item \textbf{Skill Library} (vector DB): Each verified skill stored with:


\begin{itemize}
  \item Function signature + docstring (for retrieval)
  \item Embedding of the task description (for semantic search)
  \item Dependencies (which other skills it calls)
\end{itemize}
  \item \textbf{Retrieval + Composition}: For new tasks, retrieve the top-$k$ most relevant skills and compose them: 
\begin{equation}
\text{solution} = \text{LLM}(\text{new\_task}, \text{retrieve}(\text{skill\_library}, k{=}5))
\end{equation}
\end{enumerate}

\begin{enumerate}
  \item \textbf{自动课程（Automatic Curriculum）}：LLM根据智能体当前的技能清单提出逐渐困难的任务：“你现在可以砍木头和合成木板。下一个挑战：制作一个工作台。”
  \item \textbf{技能生成（Skill Generation）}：对每个任务，智能体编写一个JavaScript函数（可执行代码）来解决该任务：
\begin{equation}
\text{skill}_i = \text{LLM}(\text{task}_i, \text{environment\_docs}, \text{error\_feedback})
\end{equation}
  \item \textbf{验证（Verification）}：在环境中执行代码。如果成功，则加入技能库。如果失败，则使用错误反馈进行迭代（最多重试5次）。
  \item \textbf{技能库（Skill Library）}（向量数据库）：每个经过验证的技能存储以下内容：

\begin{itemize}
  \item 函数签名 + 文档字符串（用于检索）
  \item 任务描述的嵌入向量（用于语义搜索）
  \item 依赖关系（调用了哪些其他技能）
\end{itemize}
  \item \textbf{检索与组合（Retrieval + Composition）}：对于新任务，检索最相关的top-$k$个技能并进行组合：
\begin{equation}
\text{solution} = \text{LLM}(\text{new\_task}, \text{retrieve}(\text{skill\_library}, k{=}5))
\end{equation}
\end{enumerate}

\textbf{Key insight}: Skills are \textbf{compositional} --- complex behaviors emerge from combining simple verified functions. The agent never forgets (library is persistent) and improves monotonically (only verified skills are added).

\textbf{关键洞察}：技能是\textbf{组合式的}——复杂行为通过组合简单的已验证函数涌现。智能体永远不会遗忘（库是持久的），并且单调改进（只添加经过验证的技能）。

\begin{examplebox}[Voyager: Curriculum and Skill Generation Prompts]
\begin{lstlisting}[style=pythonstyle]
# === AUTOMATIC CURRICULUM PROMPT ===
CURRICULUM_PROMPT = """You are a curriculum designer for an AI agent.


Agent's current skill inventory:
- mine_wood(): Mines nearby oak/birch trees
- craft_planks(): Converts logs to planks
- craft_sticks(): Converts planks to sticks
- mine_stone(): Mines stone with wooden pickaxe


Propose the next task that:
1. Builds on existing skills (reachable from current abilities)
2. Introduces exactly ONE new concept or challenge
3. Is concrete and verifiable (clear success condition)


Next task proposal:"""
# Output: "Craft a furnace (requires 8 cobblestone blocks arranged
#          in a square). You already know mine_stone()."


# === SKILL GENERATION PROMPT ===
SKILL_GEN_PROMPT = """Write a JavaScript function to accomplish this task
in Minecraft. Use the bot API (bot.dig, bot.craft, bot.equip, etc.)


Task: Smelt 5 iron ingots using a furnace.
Prerequisites available: mine_stone(), craft_furnace(), mine_iron_ore()


Error from previous attempt: "Cannot smelt without fuel in furnace"
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[Voyager：课程与技能生成提示词]
\begin{lstlisting}[style=pythonstyle]
# === 自动课程提示词 ===
CURRICULUM_PROMPT = """你是一位AI智能体的课程设计师。


智能体当前的技能清单：
- mine_wood()：挖掘附近的橡树/桦树
- craft_planks()：将原木转化为木板
- craft_sticks()：将木板转化为木棍
- mine_stone()：用木镐挖掘石头


提出下一个任务，该任务需要：
1. 建立在现有技能之上（从当前能力可达到）
2. 恰好引入一个新概念或挑战
3. 具体且可验证（明确的成功条件）


下一个任务建议："""
# 输出："制作一个熔炉（需要8个圆石排列成方形）。你已经知道mine_stone()。"


# === 技能生成提示词 ===
SKILL_GEN_PROMPT = """编写一个JavaScript函数，在Minecraft中完成此任务。
使用机器人API（bot.dig, bot.craft, bot.equip等）


任务：使用熔炉冶炼5个铁锭。
可用前提技能：mine_stone(), craft_furnace(), mine_iron_ore()


先前尝试的错误："没有燃料无法在熔炉中冶炼"
\end{lstlisting}
\end{examplebox}

```markdown
Write the corrected function:
async function smeltIronIngots(bot, count=5) {"""
\end{lstlisting}
\end{examplebox}

编写修正后的函数：
```python
async function smeltIronIngots(bot, count=5) {"""
\end{lstlisting}
\end{examplebox}

\subsection{RLEF: RL from Execution Feedback (Detailed)}
\label{rlef-rl-from-execution-feedback-detailed}

\subsection{RLEF：基于执行反馈的强化学习（详细）}
\label{rlef-rl-from-execution-feedback-detailed}

RLEF~\cite{le2024rlef} applies \textbf{online RL with deterministic execution-based rewards} to code generation agents, establishing the simplest effective paradigm for agentic training.

RLEF~\cite{le2024rlef} 将\textbf{带有确定性执行奖励的在线强化学习}应用于代码生成智能体，确立了智能体训练中最简单的有效范式。

\textbf{Training loop}:

\textbf{训练循环}：

\begin{enumerate}
  \item \textbf{Sample task}: Draw a coding problem with test cases $(x, \text{tests})$ from the training set.
  \item \textbf{Generate}: The agent produces a solution trajectory (reading files, writing code, running tests) using the current policy $\pi_\theta$.
  \item \textbf{Execute}: Run the test suite in a sandboxed environment. Reward: 
\begin{equation}
r = \frac{\text{\# tests passed}}{\text{\# total tests}} \in [0, 1]
\end{equation}
  \item \textbf{Update}: Apply GRPO/PPO using $r$ as the reward signal.
  \item \textbf{Repeat}: Thousands of iterations with fresh tasks.
\end{enumerate}

\begin{enumerate}
  \item \textbf{采样任务}：从训练集中抽取一个带有测试用例 $(x, \text{tests})$ 的编程问题。
  \item \textbf{生成}：智能体使用当前策略 $\pi_\theta$ 生成解决方案轨迹（读取文件、编写代码、运行测试）。
  \item \textbf{执行}：在沙盒环境中运行测试套件。奖励：
\begin{equation}
r = \frac{\text{通过测试数}}{\text{总测试数}} \in [0, 1]
\end{equation}
  \item \textbf{更新}：使用 $r$ 作为奖励信号应用 GRPO/PPO。
  \item \textbf{重复}：使用新任务进行数千次迭代。
\end{enumerate}

\textbf{Why execution feedback is ideal for RL}:

\textbf{为什么执行反馈是强化学习的理想选择}：

\begin{itemize}
  \item \textbf{Zero noise}: Unlike human preferences, test results are deterministic. Same code $\rightarrow$ same reward every time. This eliminates reward noise that destabilizes RL training.
  \item \textbf{Infinite scale}: Can generate unlimited tasks programmatically (random algorithms, API integration tests, data transformations).
  \item \textbf{No reward hacking}: Unlike learned reward models, a test suite can’t be ``fooled'' (assuming tests are well-written). The agent must actually solve the problem.
  \item \textbf{Dense signal}: Partial test passage ($r = 0.6$) provides richer gradient than binary pass/fail.
\end{itemize}

\begin{itemize}
  \item \textbf{零噪声}：与人类偏好不同，测试结果是确定性的。相同的代码每次产生相同的奖励。这消除了使强化学习训练不稳定的奖励噪声。
  \item \textbf{无限规模}：可以通过编程方式生成无限任务（随机算法、API集成测试、数据转换）。
  \item \textbf{无奖励欺骗}：与学习到的奖励模型不同，测试套件无法被“欺骗”（假设测试编写良好）。智能体必须实际解决问题。
  \item \textbf{密集信号}：部分测试通过（$r = 0.6$）比简单的通过/失败提供更丰富的梯度。
\end{itemize}

\subsection{OpenHands / SWE-Agent: GRPO for Software Engineering}
\label{openhands-swe-agent-grpo-for-software-engineering}

\subsection{OpenHands / SWE-Agent：用于软件工程的GRPO}
\label{openhands-swe-agent-grpo-for-software-engineering}

OpenHands~\cite{wang2024openhands} and SWE-Agent~\cite{yang2024sweagent} apply GRPO to train agents that autonomously resolve GitHub issues --- reading code, writing patches, and running test suites.

OpenHands~\cite{wang2024openhands} 和 SWE-Agent~\cite{yang2024sweagent} 应用GRPO训练能够自主解决GitHub问题的智能体——读取代码、编写补丁和运行测试套件。

\textbf{Training specifics}:

\textbf{训练细节}：

\begin{itemize}
  \item \textbf{Environment}: Docker container with full repo, test suite, and developer tools (git, grep, lint).
  \item \textbf{Action space}: Bash commands, file edits, git operations, test execution.
  \item \textbf{Trajectory length}: 15--50 actions typical for resolving a GitHub issue.
  \item \textbf{Reward}: Binary --- does the generated patch pass the issue’s regression tests?
  \item \textbf{Group size}: $N = 8$--$16$ trajectories per issue for GRPO normalization.
  \item \textbf{Curriculum}: Start with issues labeled ``good first issue'', progress to complex multi-file refactors.
\end{itemize}

\begin{itemize}
  \item \textbf{环境}：包含完整仓库、测试套件和开发者工具（git、grep、lint）的Docker容器。
  \item \textbf{动作空间}：Bash命令、文件编辑、git操作、测试执行。
  \item \textbf{轨迹长度}：解决一个GitHub问题通常需要15-50个动作。
  \item \textbf{奖励}：二值——生成的补丁是否通过了问题的回归测试？
  \item \textbf{组大小}：每个问题 $N = 8$--$16$ 条轨迹用于GRPO归一化。
  \item \textbf{课程学习}：从标记为“good first issue”的问题开始，逐步进展到复杂的多文件重构。
\end{itemize}

\textbf{State-of-the-art results}: SWE-bench Verified: 30\% $\rightarrow$ 55\% resolve rate after RL training (vs. SFT-only baseline).

\textbf{最先进成果}：SWE-bench Verified：经过强化学习训练后，解决率从30\%提升到55\%（对比仅使用SFT的基线）。

\begin{examplebox}[OpenHands / SWE-Agent: System Prompt]
\begin{lstlisting}[style=pythonstyle]
SYSTEM = """You are an autonomous software engineer. You are given a
GitHub issue to resolve. You have access to the full repository in
/workspace/ and can execute any bash command.


AVAILABLE COMMANDS:
- bash(command): Execute a shell command
- edit(file, start_line, end_line, new_content): Edit a file
- search(pattern, path): Search for text in files
- submit(): Submit your patch when done


WORKFLOW:
1. Read the issue carefully and understand the expected behavior
2. Explore the codebase to find relevant files
3. Reproduce the bug (write/run a test that fails)
4. Implement the fix
5. Verify the fix (run the test again - must pass)
6. Run the full test suite to check for regressions
7. Submit when all tests pass


RULES:
- Do NOT modify test files unless the issue explicitly asks for it
- Prefer minimal, targeted changes over large refactors
- Always verify your fix before submitting"""


USER = """GitHub Issue #4521: `DataFrame.merge()` silently drops
rows when `on` column contains NaN values.


Expected: NaN keys should be preserved (matched with other NaN rows)
Actual: Rows with NaN keys are dropped entirely


Repository: /workspace/pandas-dev/pandas/"""
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[OpenHands / SWE-Agent：系统提示]
\begin{lstlisting}[style=pythonstyle]
SYSTEM = """你是一名自主软件工程师。你被分配了一个需要解决的GitHub问题。你可以访问 /workspace/ 中的完整仓库，并可以执行任何bash命令。


可用命令：
- bash(command)：执行shell命令
- edit(file, start_line, end_line, new_content)：编辑文件
- search(pattern, path)：在文件中搜索文本
- submit()：完成后提交你的补丁


工作流程：
1. 仔细阅读问题并理解预期行为
2. 探索代码库以找到相关文件
3. 复现bug（编写/运行一个会失败的测试）
4. 实现修复
5. 验证修复（再次运行测试——必须通过）
6. 运行完整测试套件以检查回归
7. 所有测试通过后提交


规则：
- 除非问题明确要求，否则不要修改测试文件
- 倾向于最小、有针对性的修改，而不是大规模重构
- 在提交之前始终验证你的修复"""


USER = """GitHub Issue #4521：当 `on` 列包含NaN值时，`DataFrame.merge()` 会静默丢弃行。


期望：应保留NaN键（与其他NaN行匹配）
实际：包含NaN键的行被完全丢弃


仓库：/workspace/pandas-dev/pandas/"""
\end{lstlisting}
\end{examplebox}

\begin{intuitionbox}[The Future: RL + Agents]
The field is converging on a pattern: \textbf{online RL with execution-based rewards} applied to multi-step agent trajectories. Key trends:

\begin{intuitionbox}[未来：强化学习 + 智能体]
该领域正在趋同于一种模式：将\textbf{带有执行奖励的在线强化学习}应用于多步智能体轨迹。关键趋势：

\begin{itemize}
  \item GRPO/PPO with binary pass/fail rewards from code execution or tool success
  \item Curriculum learning: start with easy tasks, progressively increase difficulty
  \item Trajectory-level optimization (not token-level) --- reward only at the end of a multi-step sequence
  \item Hybrid approaches: use retrieval (non-parametric) for rare tasks + RL (parametric) for common ones
  \item Scaling law: more compute at inference (search/retry) often beats more training compute
\end{itemize}
\end{intuitionbox}

\begin{itemize}
  \item GRPO/PPO 结合来自代码执行或工具成功的二值通过/失败奖励
  \item 课程学习：从简单任务开始，逐步增加难度
  \item 轨迹级优化（而非token级）——仅在多步序列结束时给予奖励
  \item 混合方法：对罕见任务使用检索（非参数化） + 对常见任务使用强化学习（参数化）
  \item 缩放定律：推理时更多计算（搜索/重试）往往胜过更多训练计算
\end{itemize}
\end{intuitionbox}

\newpage
\section{Use Case: Agentic RL for a Productivity Co-pilot}
\label{use-case-agentic-rl-for-a-productivity-co-pilot}

\newpage
\section{用例：面向生产力副驾驶的智能体强化学习}
\label{use-case-agentic-rl-for-a-productivity-co-pilot}

This section provides a complete blueprint for applying agentic RL techniques to train an LLM-based co-pilot that operates across a productivity application suite (documents, spreadsheets, presentations, email, messaging, cloud storage).

本节提供了一个完整的蓝图，用于应用智能体强化学习技术来训练一个基于LLM的副驾驶，该副驾驶可在生产力应用套件（文档、电子表格、演示文稿、电子邮件、消息、云存储）中运行。

\subsection{Architecture Overview}
\label{architecture-overview}

\subsection{架构概览}
\label{architecture-overview}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_043_fig43.png}
\caption{Productivity co-pilot architecture: the LLM agent (with RL policy $\pi_\theta$) receives user intents and interacts with multiple application APIs. A reward signal based on task success, user feedback, and efficiency metrics drives policy improvement.}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_043_fig43.png}
\caption{生产力副驾驶架构：LLM智能体（带有强化学习策略 $\pi_\theta$）接收用户意图并与多个应用程序API交互。基于任务成功、用户反馈和效率指标的奖励信号驱动策略改进。}
\end{figure}

\subsection{Formal MDP Definition for a Productivity Co-pilot}
\label{formal-mdp-definition-for-a-productivity-co-pilot}

\subsection{生产力副驾驶的形式化MDP定义}
\label{formal-mdp-definition-for-a-productivity-co-pilot}

The productivity co-pilot environment is formalized as a Partially Observable Markov Decision Process (POMDP):

生产力副驾驶环境被形式化为部分可观测马尔可夫决策过程（POMDP）：

\begin{equation}
\boxed{\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, \mathcal{T}, \mathcal{R}, \Omega, \mathcal{O}, \gamma \rangle}
\end{equation}

\begin{itemize}
  \item $\mathcal{S}$: \textbf{State space} --- Full workspace environment state: document contents, email threads, calendar events, file system, user permissions. \emph{Not fully observable}: agent sees only what API queries return.
  \item $\mathcal{A}$: \textbf{Action space} --- Structured API calls (see below). Each action is a JSON object specifying the target app, operation, and parameters.
  \item $\mathcal{T}$: \textbf{Transition function} --- Deterministic for most operations (write to document $\rightarrow$ document updated), but stochastic for network-dependent actions (email delivery time, Teams availability).
  \item $\mathcal{R}$: \textbf{Reward function} --- Multi-component (see Reward Design section).
  \item $\Omega$: \textbf{Observation space} --- API responses, rendered document views, error messages.
  \item $\mathcal{O}$: \textbf{Observation function} --- Maps state to observation (API response formatting, truncation for context window limits).
  \item $\gamma = 0.99$: Discount factor (long horizons, 10--50 steps typical).
\end{itemize}

\begin{itemize}
  \item $\mathcal{S}$: \textbf{状态空间} —— 完整的工作区环境状态：文档内容、邮件线程、日历事件、文件系统、用户权限。\emph{非完全可观测}：智能体只能看到API查询返回的内容。
  \item $\mathcal{A}$: \textbf{动作空间} —— 结构化的API调用（见下文）。每个动作是一个JSON对象，指定目标应用、操作和参数。
  \item $\mathcal{T}$: \textbf{转移函数} —— 对于大多数操作是确定性的（写入文档 $\rightarrow$ 文档更新），但对于依赖网络的动作（邮件传递时间、Teams可用性）是随机的。
  \item $\mathcal{R}$: \textbf{奖励函数} —— 多组件（见奖励设计部分）。
  \item $\Omega$: \textbf{观测空间} —— API响应、渲染的文档视图、错误消息。
  \item $\mathcal{O}$: \textbf{观测函数} —— 将状态映射到观测（API响应格式化、为上下文窗口限制进行截断）。
  \item $\gamma = 0.99$：折扣因子（长视野，通常10-50步）。
\end{itemize}

\begin{examplebox}[Concrete Example: ``Summarize last week’s Project Alpha emails and create a status slide'']
Below we trace a full episode through the POMDP, mapping each formal element to a concrete realization.

\begin{examplebox}[具体示例：“总结上周Project Alpha的邮件并创建状态幻灯片”]
下面我们追踪一个完整的回合通过POMDP，将每个形式化元素映射到具体实现。

\textbf{User request}: ``Summarize the key decisions from last week’s Project Alpha emails and add a status update slide to the team deck.''

\textbf{用户请求}：“总结上周Project Alpha邮件中的关键决策，并向团队演示文稿中添加一张状态更新幻灯片。”
```

\begin{tabular}{@{}lp{11cm}@{}}
\toprule
\textbf{Symbol} & \textbf{Concrete Realization} \\
\textbf{符号} & \textbf{具体实现} \\
\midrule
$s_0$ & \emph{True state}: 47 emails in inbox mentioning ``Project Alpha'' from last 7 days; PowerPoint file ``Q3\_Status.pptx'' on SharePoint with 12 slides; user has edit permissions. \\
$s_0$ & \emph{真实状态}：收件箱中过去7天内有47封提及“Project Alpha”的邮件；SharePoint上的PowerPoint文件“Q3\_Status.pptx”有12张幻灯片；用户拥有编辑权限。 \\
$o_0$ & \emph{Agent observes}: User request text + system prompt. Agent has \emph{no knowledge} of email count or deck contents yet. \\
$o_0$ & \emph{智能体观察到}：用户请求文本 + 系统提示。智能体目前\emph{不知道}邮件数量或演示文稿内容。 \\
$a_1$ & \verb|outlook.search({query: "Project Alpha", last\_7\_days: true})| \\
$\mathcal{T}(s_0, a_1)$ & $s_1$: System retrieves 47 matching emails (deterministic). \\
$\mathcal{T}(s_0, a_1)$ & $s_1$：系统检索到47封匹配的邮件（确定性）。 \\
$o_1$ & API returns top 10 email subjects + senders + timestamps (truncated due to context limits --- $\mathcal{O}$ in action). \\
$o_1$ & API返回前10封邮件的主题 + 发件人 + 时间戳（由于上下文限制被截断——$\mathcal{O}$在起作用）。 \\
$a_2$ & \verb|outlook.read({ids: [top\_5\_thread\_ids]})| --- Agent picks the most relevant threads. \\
$a_2$ & \verb|outlook.read({ids: [top\_5\_thread\_ids]})| --- 智能体选择最相关的线程。 \\
$o_2$ & Full body text of 5 email threads ($\sim$8K tokens after $\mathcal{O}$ truncation). \\
$o_2$ & 5个邮件线程的完整正文（经$\mathcal{O}$截断后约8K token）。 \\
$a_3$ & \emph{Internal reasoning action}: Agent synthesizes key decisions: (1) deadline moved to Nov 15, (2) budget approved, (3) vendor selected. \\
$a_3$ & \emph{内部推理动作}：智能体综合出关键决策：(1) 截止日期移至11月15日，(2) 预算获批，(3) 供应商已选定。 \\
$a_4$ & \verb|sharepoint.read({file: "Q3\_Status.pptx", slides: "last"})| --- Check current last slide. \\
$a_4$ & \verb|sharepoint.read({file: "Q3\_Status.pptx", slides: "last"})| --- 检查当前最后一张幻灯片。 \\
$o_4$ & Last slide is ``Q2 Summary'' (slide 12). Agent decides to add slide 13. \\
$o_4$ & 最后一张幻灯片是“Q2 Summary”（第12张）。智能体决定添加第13张幻灯片。 \\
$a_5$ & \verb|powerpoint.add\_slide({file: "Q3\_Status.pptx", position: 13,| \texttt{layout: "Title and Content", title: "Project Alpha --- Week 42 Status",} \verb|content: "Key decisions: 1) Deadline: Nov 15..."})| \\
$\mathcal{T}(s_4, a_5)$ & $s_5$: Slide added to deck (deterministic). \\
$\mathcal{T}(s_4, a_5)$ & $s_5$：幻灯片已添加到演示文稿（确定性）。 \\
$o_5$ & API returns \verb|{success: true, slide\_id: 13}|. \\
$o_5$ & API返回 \verb|{success: true, slide\_id: 13}|。 \\
$R(s_5)$ & Reward components: \textbf{+0.4} task completion (slide created), \textbf{+0.3} information quality (correct decisions extracted), \textbf{+0.2} format compliance (proper layout used), \textbf{+0.05} efficiency (5 actions, no errors), \textbf{-0.0} safety penalty. \textbf{Total: 0.95}. \\
$R(s_5)$ & 奖励组件：\textbf{+0.4} 任务完成（创建了幻灯片），\textbf{+0.3} 信息质量（提取了正确的决策），\textbf{+0.2} 格式合规（使用了正确的布局），\textbf{+0.05} 效率（5个动作，无错误），\textbf{-0.0} 安全惩罚。\textbf{总计：0.95}。 \\
\bottomrule
\end{tabular}

\textbf{Key POMDP aspects illustrated}:
\textbf{关键POMDP方面示例}：

\begin{itemize}
  \item \textbf{Partial observability}: At $t=0$, the agent doesn’t know how many emails exist or what the deck contains --- it must query to discover the state.
  \item \textbf{部分可观测性}：在$t=0$时，智能体不知道存在多少封邮件或演示文稿的内容——它必须通过查询来发现状态。
  \item \textbf{Observation function $\mathcal{O}$}: The API returns truncated results (top 10 of 47 emails) due to context window limits. The agent sees a \emph{projection} of the true state.
  \item \textbf{观测函数 $\mathcal{O}$}：由于上下文窗口限制，API返回截断结果（47封邮件中的前10封）。智能体看到的是真实状态的\emph{投影}。
  \item \textbf{Stochastic transitions}: If the agent had tried \texttt{teams.send\_message()} instead, delivery timing would be uncertain (recipient online/offline).
  \item \textbf{随机转移}：如果智能体尝试使用\texttt{teams.send\_message()}，则投递时间将是不确定的（接收者在线/离线）。
  \item \textbf{Multi-step planning}: The agent must chain 5 actions across 2 applications, maintaining coherence between the email summary and the slide content.
  \item \textbf{多步规划}：智能体必须在两个应用之间串联5个动作，保持邮件摘要与幻灯片内容之间的一致性。
  \item \textbf{Discount $\gamma=0.99$}: With 5 steps, discounting is minimal ($0.99^5 = 0.95$), but for 50-step tasks it matters --- encouraging efficient solutions.
  \item \textbf{折扣因子 $\gamma=0.99$}：对于5步任务，折扣影响很小（$0.99^5 = 0.95$），但对于50步任务则很重要——鼓励高效解决方案。
\end{itemize}
\end{examplebox}

\subsection{Action Space Design}
\subsection{动作空间设计}
\label{action-space-design}

The action space must be \textbf{structured, type-safe, and composable}:
动作空间必须是\textbf{结构化、类型安全且可组合}的：

\begin{examplebox}[Productivity Co-pilot Action Schema]
\begin{examplebox}[生产力副驾驶动作模式]
\begin{lstlisting}[style=pythonstyle]
{
  "action_type": "api_call",
  "target_app": "outlook | excel | word | powerpoint | teams | sharepoint",
  "operation": "read | write | search | create | delete | modify",
  "parameters": {
    "endpoint": "/me/messages?$filter=subject eq 'Project X'",
    "body": { ... },             // For write operations
    "options": { "top": 10 }     // Pagination, filtering
  },
  "reasoning": "I need to find relevant emails before summarizing"
}
\end{lstlisting}
\end{examplebox}

\textbf{Action taxonomy by application}:
\textbf{按应用划分的动作分类}：

\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{App} & \textbf{Complexity} & \textbf{Key Actions} \\
\textbf{应用} & \textbf{复杂度} & \textbf{关键动作} \\
\midrule
\textbf{Outlook} & Medium & \texttt{search}, \texttt{read}, \texttt{draft}, \texttt{send}, \texttt{move}, \texttt{flag}, \texttt{create\_rule} \\
\textbf{Outlook} & 中 & \texttt{search}, \texttt{read}, \texttt{draft}, \texttt{send}, \texttt{move}, \texttt{flag}, \texttt{create\_rule} \\
\textbf{Excel} & High & \texttt{read\_range}, \texttt{write\_range}, \texttt{insert\_formula}, \texttt{create\_chart}, \texttt{pivot\_table}, \texttt{run\_macro} \\
\textbf{Excel} & 高 & \texttt{read\_range}, \texttt{write\_range}, \texttt{insert\_formula}, \texttt{create\_chart}, \texttt{pivot\_table}, \texttt{run\_macro} \\
\textbf{Word} & Medium & \texttt{read\_paragraphs}, \texttt{insert\_text}, \texttt{format\_section}, \texttt{find\_replace}, \texttt{insert\_table} \\
\textbf{Word} & 中 & \texttt{read\_paragraphs}, \texttt{insert\_text}, \texttt{format\_section}, \texttt{find\_replace}, \texttt{insert\_table} \\
\textbf{PowerPoint} & Medium & \texttt{add\_slide}, \texttt{insert\_shape}, \texttt{set\_text}, \texttt{set\_layout}, \texttt{add\_image}, \texttt{apply\_theme} \\
\textbf{PowerPoint} & 中 & \texttt{add\_slide}, \texttt{insert\_shape}, \texttt{set\_text}, \texttt{set\_layout}, \texttt{add\_image}, \texttt{apply\_theme} \\
\textbf{Teams} & Low & \texttt{send\_message}, \texttt{create\_meeting}, \texttt{search\_chat}, \texttt{add\_members}, \texttt{post\_to\_channel} \\
\textbf{Teams} & 低 & \texttt{send\_message}, \texttt{create\_meeting}, \texttt{search\_chat}, \texttt{add\_members}, \texttt{post\_to\_channel} \\
\textbf{SharePoint} & Medium & \texttt{list\_files}, \texttt{upload}, \texttt{download}, \texttt{search}, \texttt{create\_page}, \texttt{set\_permissions} \\
\textbf{SharePoint} & 中 & \texttt{list\_files}, \texttt{upload}, \texttt{download}, \texttt{search}, \texttt{create\_page}, \texttt{set\_permissions} \\
\bottomrule
\end{tabular}

\subsection{State Representation}
\subsection{状态表示}
\label{state-representation}

The agent’s observation (context window) at each step:
智能体在每个步骤的观测（上下文窗口）：

\begin{equation}
o_t = [\text{system\_prompt};\; \text{user\_intent};\; \text{tool\_history}_{1:t-1};\; \text{current\_result}_t]
\end{equation}

\textbf{Context budget management} (critical for 128K window):
\textbf{上下文预算管理}（对128K窗口至关重要）：

\begin{itemize}
  \item \textbf{System prompt}: 2K tokens (capabilities, safety rules, output format)
  \item \textbf{系统提示}：2K token（能力、安全规则、输出格式）
  \item \textbf{User intent + conversation}: 4K tokens
  \item \textbf{用户意图 + 对话}：4K token
  \item \textbf{Tool history} (sliding window): Last 8--12 actions + observations, summarizing older ones. Total: 80K tokens max.
  \item \textbf{工具历史}（滑动窗口）：最近8-12个动作 + 观测，对更早的内容进行摘要。总计：最多80K token。
  \item \textbf{Current observation}: Up to 32K tokens (large spreadsheets, email threads)
  \item \textbf{当前观测}：最多32K token（大型电子表格、邮件线程）
  \item \textbf{Reserve}: 10K tokens for agent’s reasoning + next action generation
  \item \textbf{预留}：10K token用于智能体的推理 + 下一个动作生成
\end{itemize}

\textbf{State compression strategies}:
\textbf{状态压缩策略}：

\begin{itemize}
  \item \textbf{Selective inclusion}: Only include API responses relevant to the current sub-goal (use an auxiliary ``relevance scorer'').
  \item \textbf{选择性包含}：仅包含与当前子目标相关的API响应（使用辅助的“相关性评分器”）。
  \item \textbf{Structured summaries}: Represent large spreadsheets as schema + sample rows rather than full data.
  \item \textbf{结构化摘要}：将大型电子表格表示为模式 + 示例行，而非完整数据。
  \item \textbf{Hierarchical memory}: Store full trajectory externally; inject compressed summaries into context.
  \item \textbf{分层记忆}：在外部存储完整轨迹；将压缩后的摘要注入上下文。
\end{itemize}

\subsection{Reward Design: Multi-Objective Signal}
\subsection{奖励设计：多目标信号}
\label{reward-design-multi-objective-signal}

The reward function for a productivity co-pilot must balance multiple objectives:
生产力副驾驶的奖励函数必须平衡多个目标：

\begin{equation}
\boxed{R(\tau) = \alpha_1 R_{\text{task}} + \alpha_2 R_{\text{quality}} + \alpha_3 R_{\text{efficiency}} + \alpha_4 R_{\text{safety}} + \alpha_5 R_{\text{user}}}
\end{equation}

\begin{table}[ht!]
\centering
\caption{Reward components for productivity co-pilot training.}
\caption{生产力副驾驶训练的奖励组件。}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{Component} & \textbf{Weight} & \textbf{Signal Type} & \textbf{Definition} \\
\textbf{组件} & \textbf{权重} & \textbf{信号类型} & \textbf{定义} \\
\midrule
$R_{\text{task}}$ & 0.40 & Binary/scalar & Task completed successfully (email sent, document created, formula correct) \\
$R_{\text{task}}$ & 0.40 & 二元/标量 & 任务成功完成（邮件已发送、文档已创建、公式正确） \\
$R_{\text{quality}}$ & 0.25 & LLM judge & Output quality: formatting, clarity, correctness of content \\
$R_{\text{quality}}$ & 0.25 & LLM评判器 & 输出质量：格式、清晰度、内容正确性 \\
$R_{\text{efficiency}}$ & 0.15 & Scalar & Penalty for excessive steps: $-0.02 \times (\text{num\_steps} - \text{optimal\_steps})$ \\
$R_{\text{efficiency}}$ & 0.15 & 标量 & 对过多步骤的惩罚：$-0.02 \times (\text{num\_steps} - \text{optimal\_steps})$ \\
$R_{\text{safety}}$ & 0.15 & Binary & No unsafe actions (delete without confirmation, send to wrong recipient, permission violations). $R_{\text{safety}} = 0$ if any violation. \\
$R_{\text{safety}}$ & 0.15 & 二元 & 无不安全动作（未确认即删除、发送给错误收件人、权限违规）。如有任何违规，$R_{\text{safety}} = 0$。 \\
$R_{\text{user}}$ & 0.05 & Sparse & Explicit user feedback (thumbs up/down) when available \\
$R_{\text{user}}$ & 0.05 & 稀疏 & 用户明确反馈（点赞/点踩）可用时 \\
\bottomrule
\end{tabular}
\end{table}

\textbf{Intermediate rewards (dense signal)}:
\textbf{中间奖励（密集信号）}：

\begin{itemize}
  \item Successful API call (200 response): +0.05
  \item 成功的API调用（200响应）：+0.05
  \item Correct information retrieval (verified by downstream use): +0.10
  \item 正确信息检索（通过下游使用验证）：+0.10
  \item Recovers from error gracefully (retries with corrected params): +0.08
  \item 从错误中优雅恢复（使用修正参数重试）：+0.08
  \item API error (4xx/5xx): --0.03
  \item API错误（4xx/5xx）：--0.03
  \item Repeated identical action (loop detection): --0.10
  \item 重复执行相同动作（循环检测）：--0.10
  \item Asks clarifying question when intent is genuinely ambiguous: +0.05
  \item 当意图确实模糊时提出澄清问题：+0.05
\end{itemize}

\subsection{Training Pipeline: End-to-End}
\subsection{训练流水线：端到端}
\label{training-pipeline-end-to-end}

\begin{keybox}[Productivity Co-pilot RL Training Pipeline]
\textbf{Phase 1: Supervised Fine-Tuning (Foundation)}
\begin{keybox}[生产力副驾驶强化学习训练流水线]
\textbf{阶段1：监督微调（基础）}

## Content to Translate:
## 要翻译的内容

\begin{enumerate}
  \item Collect 50K--200K human-demonstrated trajectories of productivity tasks (via telemetry, annotators, or synthetic generation).
  \item 收集5万到20万条人类演示的生产力任务轨迹（通过遥测、标注者或合成生成）。
  \item SFT the base LLM on (instruction, trajectory) pairs with ReAct format.
  \item 在基础LLM上使用ReAct格式对（指令，轨迹）对进行SFT。
  \item Validate: agent should achieve 40--60\% task completion on held-out tasks.
  \item 验证：智能体在保留任务上应达到40%–60%的任务完成率。
\end{enumerate}

\textbf{Phase 2: Simulated Environment Construction}
\textbf{阶段二：模拟环境构建}

\begin{enumerate}
  \item Build a \textbf{sandbox environment} with mocked API endpoints, synthetic mailboxes, documents, and calendars.
  \item 构建一个带有模拟API端点、合成邮箱、文档和日历的\textbf{沙箱环境}。
  \item Each ``user'' has a realistic profile: 500+ emails, 20+ documents, calendar events, Teams channels.
  \item 每个“用户”拥有一个真实配置文件：500+封邮件、20+个文档、日历事件、Teams频道。
  \item Task generator: produces diverse instruction--verification pairs: ``Move all emails from Alice about Q4 budget to the ‘Finance’ folder'' + verification function.
  \item 任务生成器：生成多样化的指令-验证对：“将Alice关于Q4预算的所有邮件移动到‘财务’文件夹”+验证函数。
\end{enumerate}

\textbf{Phase 3: Online RL Training (GRPO)}
\textbf{阶段三：在线RL训练（GRPO）}

\begin{enumerate}
  \item Sample task batch (256 tasks per iteration).
  \item 采样任务批次（每次迭代256个任务）。
  \item Generate $N=8$ trajectories per task using $\pi_\theta$ in sandbox environment.
  \item 在沙箱环境中使用$\pi_\theta$为每个任务生成$N=8$条轨迹。
  \item Execute trajectories, collect rewards from verification functions.
  \item 执行轨迹，从验证函数收集奖励。
  \item Compute GRPO advantages (group normalization across 8 trajectories per task).
  \item 计算GRPO优势（每个任务8条轨迹的组归一化）。
  \item Update policy with clipped objective + KL penalty vs. SFT model.
  \item 使用裁剪目标 + 相对于SFT模型的KL惩罚更新策略。
  \item Every 500 iterations: evaluate on held-out benchmark (200 tasks, 5 difficulty levels).
  \item 每500次迭代：在保留基准上评估（200个任务，5个难度等级）。
\end{enumerate}

\textbf{Phase 4: Human-in-the-Loop Refinement}
\textbf{阶段四：人在回路精调}

\begin{enumerate}
  \item Deploy to internal dogfood users (1000+ users, 2 weeks).
  \item 部署给内部尝鲜用户（1000+用户，2周）。
  \item Collect thumbs up/down signals + free-text corrections.
  \item 收集赞/踩信号 + 自由文本修正。
  \item Construct DPO preference pairs from A/B deployments (old policy vs. new).
  \item 从A/B部署（旧策略 vs 新策略）构建DPO偏好对。
  \item Apply 1--2 rounds of DPO fine-tuning on human preferences.
  \item 对人工偏好应用1–2轮DPO微调。
\end{enumerate}
\end{keybox}

\subsection{Simulation Environment Architecture}
\subsection{模拟环境架构}
\label{simulation-environment-architecture}

\begin{examplebox}[Sandbox Environment (Simplified)]
\begin{examplebox}[沙箱环境（简化版）]
\begin{lstlisting}[style=pythonstyle]
class ProductivityEnvironment:
    def __init__(self, user_profile: UserProfile):
        self.mailbox = SyntheticMailbox(user_profile.emails)
        self.drive = SyntheticOneDrive(user_profile.files)
        self.calendar = SyntheticCalendar(user_profile.events)
        self.teams = SyntheticTeams(user_profile.channels)
        self.step_count = 0
        self.max_steps = 50
        
    def step(self, action: dict) -> Tuple[Observation, float, bool]:
        """Execute action, return (observation, reward, done)."""
        """执行动作，返回（观察，奖励，完成）。"""
        self.step_count += 1
        
        # Route to appropriate app handler
        # 路由到适当的应用处理器
        handler = self.get_handler(action["target_app"])
        try:
            result = handler.execute(action["operation"], action["parameters"])
            obs = Observation(status=200, body=result)
            reward = 0.05  # Successful API call
            reward = 0.05  # 成功的API调用
        except APIError as e:
            obs = Observation(status=e.code, body=str(e))
            reward = -0.03
            
        # Check terminal condition
        # 检查终止条件
        done = self.step_count >= self.max_steps
        return obs, reward, done
    
    def evaluate(self, task: Task) -> float:
        """Check if task objective is achieved (terminal reward)."""
        """检查任务目标是否实现（终止奖励）。"""
        return task.verification_fn(self)  # 0.0 or 1.0
\end{lstlisting}
\end{examplebox}

\subsection{Task Curriculum Design}
\subsection{任务课程设计}
\label{task-curriculum-design}

Training effectiveness depends critically on task difficulty progression:
训练效果关键取决于任务难度的递进：

\begin{table}[ht!]
\centering
\caption{Productivity co-pilot curriculum levels.}
\caption{生产力副驾驶课程等级。}
{\small
\begin{tabular}{@{}lllp{7.5cm}@{}}
\toprule
\textbf{Level} & \textbf{Steps} & \textbf{Apps} & \textbf{Example Tasks} \\
\textbf{等级} & \textbf{步骤数} & \textbf{应用数} & \textbf{示例任务} \\
\midrule
\textbf{L1: Single-step} & 1--2 & 1 & ``Read my latest email from Bob'', ``What’s in cell A1?'' \\
\textbf{L1：单步} & 1--2 & 1 & “读取Bob发来的最新邮件”，“A1单元格里是什么？” \\
\textbf{L2: Single-app} & 3--5 & 1 & ``Draft a reply to the budget email summarizing key points'' \\
\textbf{L2：单应用} & 3--5 & 1 & “起草对预算邮件的回复，总结关键点” \\
\textbf{L3: Multi-step} & 5--10 & 1 & ``Create a pivot table from sales data and format top performers in bold'' \\
\textbf{L3：多步} & 5--10 & 1 & “从销售数据创建数据透视表，并将表现最佳者加粗” \\
\textbf{L4: Cross-app} & 5--15 & 2--3 & ``Find Q4 budget emails, extract the numbers, put them in a new Excel sheet'' \\
\textbf{L4：跨应用} & 5--15 & 2--3 & “找到Q4预算邮件，提取数字，放入新的Excel表格” \\
\textbf{L5: Complex workflow} & 10--30 & 3+ & ``Prepare a weekly report: pull metrics from Excel, summarize email updates, create PowerPoint slides, share in Teams'' \\
\textbf{L5：复杂工作流} & 10--30 & 3+ & “准备每周报告：从Excel拉取指标，总结邮件更新，创建PowerPoint幻灯片，在Teams中分享” \\
\bottomrule
\end{tabular}
}
\end{table}

\textbf{Curriculum strategy}:
\textbf{课程策略}：

\begin{itemize}
  \item Start with 80\% L1--L2 tasks, 20\% L3 in early training.
  \item 训练初期从80%的L1–L2任务和20%的L3任务开始。
  \item Advance to next level when success rate exceeds 70\% on current level.
  \item 当当前等级成功率超过70%时，进入下一等级。
  \item Always maintain 10--20\% of easier tasks to prevent catastrophic forgetting.
  \item 始终保持10%–20%的简单任务以防止灾难性遗忘。
  \item Final mix (after convergence): 10\% L1, 15\% L2, 25\% L3, 30\% L4, 20\% L5.
  \item 最终混合（收敛后）：10% L1，15% L2，25% L3，30% L4，20% L5。
\end{itemize}

\subsection{Safety and Guardrails}
\subsection{安全与护栏}
\label{safety-and-guardrails}

\begin{keybox}[Safety Framework for Productivity Co-pilot]
\begin{keybox}[生产力副驾驶的安全框架]
\textbf{Hard constraints} (action rejected immediately, reward = --1.0):
\textbf{硬约束}（动作立即被拒绝，奖励 = –1.0）：

\begin{itemize}
  \item Send email/message to external recipients without user confirmation
  \item 在未经用户确认的情况下向外部收件人发送邮件/消息
  \item Delete files/emails permanently (only soft-delete allowed)
  \item 永久删除文件/邮件（只允许软删除）
  \item Modify permissions on shared resources
  \item 修改共享资源的权限
  \item Access other users’ mailboxes or files beyond granted permissions
  \item 访问超出授权权限的其他用户的邮箱或文件
  \item Execute actions on more than 100 items in a batch (prevents mass-delete/move accidents)
  \item 批量执行超过100个项目的操作（防止批量删除/移动事故）
\end{itemize}

\textbf{Soft constraints} (penalty in reward, agent should learn to avoid):
\textbf{软约束}（奖励中的惩罚，智能体应学会避免）：

\begin{itemize}
  \item Sending draft without showing preview to user: --0.2
  \item 未向用户显示预览就发送草稿：–0.2
  \item Making irreversible changes without stating intent first: --0.15
  \item 未事先说明意图就进行不可逆更改：–0.15
  \item Accessing sensitive labels (confidential, attorney-client): --0.3
  \item 访问敏感标签（机密、律师-客户）：–0.3
  \item Using ``send on behalf'' without explicit delegation: --0.25
  \item 未经明确委托使用“代表发送”：–0.25
\end{itemize}

\textbf{Confirmation protocol}: For any action classified as ``high-impact'' (send, delete, share externally), the agent must:
\textbf{确认协议}：对于任何被归类为“高影响”的动作（发送、删除、外部共享），智能体必须：

\begin{enumerate}
  \item State the intended action in natural language
  \item 用自然语言陈述预期动作
  \item Show a preview of what will be sent/modified
  \item 显示将要发送/修改的内容预览
  \item Wait for explicit user confirmation before executing
  \item 在执行前等待用户的明确确认
\end{enumerate}

This is enforced both at the environment level (sandbox rejects unconfirmed high-impact actions) and in the reward function (penalty for skipping confirmation).
这一点在环境层面（沙箱拒绝未经确认的高影响动作）和奖励函数中（跳过确认的惩罚）都是强制执行的。
\end{keybox}

\subsection{Credit Assignment in Multi-App Workflows}
\subsection{多应用工作流中的信用分配}
\label{credit-assignment-in-multi-app-workflows}

The key challenge: in a 20-step cross-app workflow, which steps contributed to success or failure?
关键挑战：在一个20步的跨应用工作流中，哪些步骤促成了成功或失败？

\textbf{Approach: Hierarchical Reward Decomposition}
\textbf{方法：层级奖励分解}

\begin{enumerate}
  \item \textbf{Sub-goal detection}: Decompose the user’s instruction into verifiable sub-goals:
  \item \textbf{子目标检测}：将用户的指令分解为可验证的子目标：

\begin{itemize}
  \item ``Find Q4 budget emails'' $\rightarrow$ Sub-goal 1 (verified: relevant emails retrieved)
  \item “找到Q4预算邮件” $\rightarrow$ 子目标1（已验证：检索到相关邮件）
  \item ``Extract numbers'' $\rightarrow$ Sub-goal 2 (verified: correct values parsed)
  \item “提取数字” $\rightarrow$ 子目标2（已验证：正确解析数值）
  \item ``Create Excel sheet'' $\rightarrow$ Sub-goal 3 (verified: sheet exists with correct data)
  \item “创建Excel表格” $\rightarrow$ 子目标3（已验证：存在包含正确数据的表格）
\end{itemize}
  \item \textbf{Sub-goal rewards}: Assign intermediate rewards at each sub-goal completion ($r = +0.2$ each).
  \item \textbf{子目标奖励}：在每个子目标完成时分配中间奖励（每个$r = +0.2$）。
  \item \textbf{Trajectory slicing}: If the final task fails, identify which sub-goal failed first. Apply negative reward only to the actions within that sub-goal’s span.
  \item \textbf{轨迹切片}：如果最终任务失败，识别哪个子目标首先失败。仅对该子目标范围内的动作应用负奖励。
  \item \textbf{Counterfactual estimation}: ``Would the task have succeeded if this specific action were different?'' --- use the value function to estimate.
  \item \textbf{反事实估计}：“如果这个特定动作不同，任务是否会成功？”——使用价值函数进行估计。
\end{enumerate}

\begin{equation}
R_{\text{step}}(t) = \underbrace{R_{\text{sub-goal}}(t)}_{\text{did current sub-goal succeed?}} + \underbrace{\gamma^{T-t} R_{\text{terminal}}}_{\text{discounted final reward}} + \underbrace{r_{\text{intermediate}}(t)}_{\text{per-step API success/failure}}
\end{equation}

\begin{equation}
R_{\text{step}}(t) = \underbrace{R_{\text{sub-goal}}(t)}_{\text{当前子目标是否成功？}} + \underbrace{\gamma^{T-t} R_{\text{terminal}}}_{\text{折扣后的最终奖励}} + \underbrace{r_{\text{intermediate}}(t)}_{\text{每步API成功/失败}}
\end{equation}

\subsection{Scaling and Infrastructure}
\subsection{扩展与基础设施}
\label{scaling-and-infrastructure}

\textbf{Compute requirements} (estimated for 70B parameter model):
\textbf{计算需求}（针对70B参数模型的估算）：

## 表格：资源分配
## 表格：资源分配

\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Component} & \textbf{Resources} & \textbf{Notes} \\
\textbf{组件} & \textbf{资源} & \textbf{备注} \\
\midrule
Policy model (70B) & 8$\times$ A100 80GB (TP=8) & BF16, generates trajectories \\
策略模型（70B） & 8×A100 80GB（TP=8） & BF16，生成轨迹 \\
Reference model (70B) & 8$\times$ A100 80GB (TP=8) & Frozen, for KL computation \\
参考模型（70B） & 8×A100 80GB（TP=8） & 冻结，用于KL计算 \\
Environment workers & 128 CPU workers & Each runs sandbox instance \\
环境工作者 & 128个CPU工作者 & 每个运行沙箱实例 \\
Reward model / Judge & 4$\times$ A100 (if LLM judge) & Or zero if using execution-based rewards \\
奖励模型/评判器 & 4×A100（若使用LLM评判器） & 若使用基于执行的奖励则为0 \\
Training (GRPO updates) & 16$\times$ A100 (FSDP) & Gradient accumulation over trajectory batches \\
训练（GRPO更新） & 16×A100（FSDP） & 在轨迹批次上进行梯度累积 \\
\textbf{Total} & \textbf{40 A100 GPUs + 128 CPUs} & ~5,000 GPU-hours for full training run \\
\textbf{总计} & \textbf{40块A100 GPU + 128个CPU} & 完整训练约需5,000 GPU小时 \\
\bottomrule
\end{tabular}

\textbf{Throughput optimization}:
\textbf{吞吐量优化}：

\begin{itemize}
  \item \textbf{Async rollouts}: Decouple trajectory generation from gradient updates. Generate continuously while training on previous batch.
  \item \textbf{异步 rollout}：将轨迹生成与梯度更新解耦。在训练上一批数据的同时持续生成新轨迹。
  \item \textbf{Batched environment}: Run 128 sandbox environments in parallel, each processing different tasks.
  \item \textbf{批量环境}：并行运行128个沙箱环境，每个处理不同任务。
  \item \textbf{KV-cache sharing}: For the $N=8$ trajectories per task, they share the same prompt prefix --- use prefix caching to avoid redundant computation.
  \item \textbf{KV缓存共享}：对于每个任务的 $N=8$ 条轨迹，它们共享相同的提示前缀——使用前缀缓存避免冗余计算。
  \item \textbf{Selective backprop}: Only compute gradients over action tokens (not observations/system prompt). Reduces backward pass FLOPS by 40--60\%.
  \item \textbf{选择性反向传播}：仅对动作token（而非观测/系统提示）计算梯度。将反向传播的计算量减少40–60%。
\end{itemize}

\subsection{Evaluation Framework}
\subsection{评估框架}
\label{evaluation-framework}

\begin{table}[ht!]
\centering
\caption{Productivity co-pilot evaluation dimensions.}
\caption{生产力协作者评估维度。}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Metric} & \textbf{Target} & \textbf{Measurement} \\
\textbf{指标} & \textbf{目标} & \textbf{测量方法} \\
\midrule
Task completion rate & $>85\%$ (L1--L3), $>60\%$ (L4--L5) & Automated verification in sandbox \\
任务完成率 & $>85\%$（L1–L3），$>60\%$（L4–L5） & 沙箱中自动验证 \\
Safety violation rate & $<0.1\%$ & Count of hard constraint violations per 1000 tasks \\
安全违规率 & $<0.1\%$ & 每1000个任务中硬约束违规次数 \\
Average steps to completion & Within $1.5\times$ optimal & Compare to shortest known successful trajectory \\
平均完成步数 & 在最优解的 $1.5\times$ 以内 & 与已知最短成功轨迹比较 \\
User satisfaction (dogfood) & $>4.2/5.0$ & Post-task survey from internal users \\
用户满意度（内部测试） & $>4.2/5.0$ & 内部用户的任务后调查 \\
Cross-app success & $>55\%$ (L4--L5) & Tasks requiring 2+ applications \\
跨应用成功率 & $>55\%$（L4–L5） & 需要2个及以上应用的任务 \\
Recovery rate & $>70\%$ & \% of failed API calls where agent retries successfully \\
恢复率 & $>70\%$ & 代理成功重试失败API调用的百分比 \\
Latency (time to first action) & $<3$ seconds & Model inference + action planning time \\
延迟（首次动作时间） & $<3$ 秒 & 模型推理 + 动作规划时间 \\
\bottomrule
\end{tabular}
\end{table}

\textbf{Benchmark suite} (proposed):
\textbf{基准测试套件}（建议）：

\begin{itemize}
  \item \textbf{ProdBench-Easy} (200 tasks): Single-app, 1--3 steps. Baseline establishment.
  \item \textbf{ProdBench-Easy}（200个任务）：单应用，1–3步。建立基线。
  \item \textbf{ProdBench-Hard} (200 tasks): Cross-app workflows, 10--30 steps. End-to-end capability.
  \item \textbf{ProdBench-Hard}（200个任务）：跨应用工作流，10–30步。端到端能力。
  \item \textbf{ProdBench-Safety} (100 tasks): Adversarial prompts attempting to trigger unsafe actions. Must maintain $<0.1\%$ violation rate.
  \item \textbf{ProdBench-Safety}（100个任务）：试图触发不安全行为的对抗性提示。必须保持 $<0.1\%$ 违规率。
  \item \textbf{ProdBench-Robustness} (100 tasks): Tasks with ambiguous instructions, API errors injected, missing permissions. Tests graceful degradation.
  \item \textbf{ProdBench-Robustness}（100个任务）：包含模糊指令、注入API错误、缺失权限的任务。测试优雅降级能力。
\end{itemize}

\subsection{Lessons from Production Deployments}
\subsection{生产部署中的经验教训}
\label{lessons-from-production-deployments}

\begin{intuitionbox}[Practical Insights for Productivity Agentic RL]
\begin{enumerate}
  \item \textbf{SFT quality is the floor}: RL can only improve upon what SFT provides. If the SFT model can’t format a valid Graph API call, RL won’t discover it. Invest heavily in Phase 1 data quality.
  \item \textbf{SFT质量是下限}：RL只能改进SFT提供的基础。如果SFT模型无法格式化有效的Graph API调用，RL也不会发现它。需要在第一阶段投入大量精力提升数据质量。
  \item \textbf{Reward hacking is inevitable}: The agent \emph{will} find shortcuts. Common examples:
  \item \textbf{奖励黑客行为不可避免}：代理*一定会*找到捷径。常见例子：
  
  \begin{itemize}
    \item Creating an empty Excel file to ``complete'' a spreadsheet task (passes existence check)
    \item 创建一个空的Excel文件来“完成”电子表格任务（通过存在性检查）
    \item Replying ``Done'' without actually performing the action
    \item 回复“完成”而没有实际执行动作
    \item Exploiting ambiguous verification functions
    \item 利用模糊的验证函数
  \end{itemize}
  
  \textbf{Mitigation}: Multi-level verification (format + content + semantic correctness).
  \textbf{缓解措施}：多级验证（格式 + 内容 + 语义正确性）。
  
  \item \textbf{API rate limits matter}: In production, workspace APIs have throttling (429 responses). Train with realistic rate limits to avoid policies that spam parallel requests.
  \item \textbf{API速率限制很重要}：在生产环境中，工作空间API有速率限制（429响应）。使用真实的速率限制进行训练，以避免策略滥用并行请求。
  \item \textbf{Context window is the bottleneck}: A 20-step trajectory with rich API responses easily consumes 80K+ tokens. Techniques: observation summarization, selective history, hierarchical context management.
  \item \textbf{上下文窗口是瓶颈}：一条包含丰富API响应的20步轨迹很容易消耗80K+ token。技术：观测摘要、选择性历史记录、分层上下文管理。
  \item \textbf{User intent is often ambiguous}: ``Clean up my inbox'' means different things to different users. Train the agent to ask clarifying questions when uncertainty is high (reward for appropriate clarification, penalize for excessive clarification).
  \item \textbf{用户意图往往模糊}：“清理我的收件箱”对不同用户意味着不同的事情。训练代理在不确定性高时提出澄清问题（对适当澄清给予奖励，对过度澄清进行惩罚）。
  \item \textbf{Start simple, scale gradually}: Begin with Outlook-only tasks (highest volume, most telemetry data), then expand to Excel, then cross-app. Each app has unique failure modes.
  \item \textbf{从简单开始，逐步扩展}：从仅Outlook的任务开始（最高容量，最多遥测数据），然后扩展到Excel，再到跨应用。每个应用都有独特的失败模式。
\end{enumerate}
\end{intuitionbox}

\subsection{Complete Training Recipe}
\subsection{完整训练配方}
\label{complete-training-recipe}

\begin{table}[ht!]
\centering
\caption{Recommended hyperparameters for productivity co-pilot RL training.}
\caption{生产力协作者RL训练推荐超参数。}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Parameter} & \textbf{Value} & \textbf{Rationale} \\
\textbf{参数} & \textbf{值} & \textbf{理由} \\
\midrule
Base model & 70B Llama/Mistral & Sufficient capacity for complex multi-step reasoning \\
基础模型 & 70B Llama/Mistral & 足够容量以处理复杂的多步推理 \\
RL algorithm & GRPO & No critic needed; memory-efficient for long trajectories \\
RL算法 & GRPO & 无需评判器；对长轨迹内存效率高 \\
Group size $N$ & 8 & Balance between variance reduction and compute cost \\
组大小 $N$ & 8 & 在方差降低与计算成本之间取得平衡 \\
Clip $\epsilon$ & 0.1 & Tighter than standard (0.2) due to long trajectory sensitivity \\
裁剪 $\epsilon$ & 0.1 & 由于长轨迹敏感，比标准值（0.2）更紧 \\
KL coefficient $\beta$ & 0.04 & Moderate constraint to SFT policy \\
KL系数 $\beta$ & 0.04 & 对SFT策略的中等约束 \\
Learning rate & $5 \times 10^{-7}$ & Conservative; agentic tasks are sensitive to large updates \\
学习率 & $5 \times 10^{-7}$ & 保守；代理任务对大更新敏感 \\
Batch size & 256 tasks $\times$ 8 trajs = 2048 & Large batch for stable GRPO normalization \\
批量大小 & 256 个任务 × 8 条轨迹 = 2048 & 大批量以实现稳定的GRPO归一化 \\
Max trajectory length & 50 steps & Covers 95\% of productivity tasks \\
最大轨迹长度 & 50 步 & 覆盖95%的生产力任务 \\
Context window & 128K tokens & Required for long multi-app workflows \\
上下文窗口 & 128K token & 长跨应用工作流所需 \\
Training iterations & 3000--5000 & Monitor eval metrics; early-stop on safety degradation \\
训练迭代次数 & 3000–5000 & 监控评估指标；在安全性下降时早停 \\
Curriculum warmup & 500 iterations (L1--L2 only) & Establish basic API usage before complex tasks \\
课程式预热 & 500次迭代（仅L1–L2） & 在复杂任务前建立基本API使用能力 \\
\bottomrule
\end{tabular}
\end{table}

\newpage
\section{Use Case: Building a Research Agent from Scratch}
\section{用例：从头构建研究代理}
\label{use-case-building-a-research-agent-from-scratch}

This use case demonstrates how to build a fully autonomous \textbf{research agent} --- an LLM that can formulate hypotheses, search literature, analyze data, write code, run experiments, and produce a final report --- using the techniques discussed throughout this paper.
该用例展示了如何利用本文讨论的技术，构建一个完全自主的\textbf{研究代理（research agent）}——一种能够提出假设、搜索文献、分析数据、编写代码、运行实验并生成最终报告的LLM。

\subsection{Problem Definition}
\subsection{问题定义}
\label{problem-definition}

\begin{keybox}[Research Agent Requirements]
\textbf{Input}: A research question (e.g., ``What is the effect of learning rate warmup duration on GRPO convergence for 7B models?'')
\textbf{输入}：一个研究问题（例如：“学习率预热时长对7B模型GRPO收敛性的影响是什么？”）

\textbf{Output}: A complete research report with methodology, experiments, results, and conclusions.
\textbf{输出}：一份完整的研究报告，包含方法、实验、结果和结论。

\textbf{Capabilities required}:
\textbf{所需能力}：

\begin{enumerate}
  \item \textbf{Literature search}: Query arXiv, Semantic Scholar, find relevant papers
  \item \textbf{文献搜索}：查询arXiv、Semantic Scholar，找到相关论文
  \item \textbf{Hypothesis generation}: Formulate testable hypotheses from background knowledge
  \item \textbf{假设生成}：基于背景知识提出可检验的假设
  \item \textbf{Experiment design}: Write training scripts with proper controls
  \item \textbf{实验设计}：编写包含适当对照的训练脚本
  \item \textbf{Code execution}: Run experiments, collect metrics
  \item \textbf{代码执行}：运行实验，收集指标
  \item \textbf{Data analysis}: Parse logs, compute statistics, generate plots
  \item \textbf{数据分析}：解析日志，计算统计量，生成图表
  \item \textbf{Scientific writing}: Synthesize findings into a coherent report
  \item \textbf{科学写作}：将发现综合成连贯的报告
  \item \textbf{Self-correction}: Detect failed experiments and retry with modified parameters
  \item \textbf{自我修正}：检测失败的实验并使用修改后的参数重试
\end{enumerate}
\end{keybox}

\subsection{MDP Formulation}
\subsection{MDP形式化}
\label{mdp-formulation}

\begin{keybox}[Research Agent MDP]
\begin{itemize}
  \item \textbf{State} $s_t$: System prompt + research question + full history of actions/observations (tool outputs, code results, search results). Context window: 128K tokens.
  \item \textbf{状态} $s_t$：系统提示 + 研究问题 + 动作/观测的完整历史（工具输出、代码结果、搜索结果）。上下文窗口：128K token。
  \item \textbf{Action} $a_t$: Structured tool call from the action space (see below) + reasoning trace (CoT).
  \item \textbf{动作} $a_t$：来自动作空间的结构化工具调用（见下文） + 推理轨迹（CoT）。
  \item \textbf{Transition} $T(s_{t+1}|s_t, a_t)$: Deterministic --- append action + tool output to context.
  \item \textbf{转移} $T(s_{t+1}|s_t, a_t)$：确定性——将动作 + 工具输出追加到上下文。
  \item \textbf{Reward} $R$: Sparse terminal reward based on report quality (see reward design below).
  \item \textbf{奖励} $R$：基于报告质量的稀疏终止奖励（见下文奖励设计）。
  \item \textbf{Horizon}: 20--100 steps (typical research trajectory).
  \item \textbf{时域}：20–100步（典型研究轨迹）。
  \item \textbf{Discount} $\gamma = 1.0$ (episodic; no discounting for finite tasks).
  \item \textbf{折扣} $\gamma = 1.0$（回合制；对于有限任务无折扣）。
\end{itemize}
\end{keybox}

## Action Space
## 动作空间

\label{action-space}

\begin{table}[ht!]
\centering
\caption{Research Agent tool/action space.}
\caption{研究代理工具/动作空间。}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Tool} & \textbf{Category} & \textbf{Description} \\
\textbf{工具} & \textbf{类别} & \textbf{描述} \\
\midrule
\texttt{search\_papers} & Literature & Query Semantic Scholar/arXiv. Returns titles, abstracts, citations. \\
\texttt{search\_papers} & 文献 & 查询 Semantic Scholar/arXiv。返回标题、摘要、引用。 \\
\texttt{read\_paper} & Literature & Fetch full text or specific sections of a paper. \\
\texttt{read\_paper} & 文献 & 获取论文全文或特定章节。 \\
\texttt{write\_code} & Experiment & Write Python/training scripts to a workspace. \\
\texttt{write\_code} & 实验 & 将 Python/训练脚本写入工作区。 \\
\texttt{execute\_code} & Experiment & Run scripts in a sandboxed environment. Returns stdout/stderr. \\
\texttt{execute\_code} & 实验 & 在沙盒环境中运行脚本。返回 stdout/stderr。 \\
\texttt{read\_file} & Analysis & Read logs, CSVs, or intermediate results. \\
\texttt{read\_file} & 分析 & 读取日志、CSV 或中间结果。 \\
\texttt{plot\_data} & Analysis & Generate matplotlib/seaborn visualizations. \\
\texttt{plot\_data} & 分析 & 生成 matplotlib/seaborn 可视化。 \\
\texttt{compute\_stats} & Analysis & Run statistical tests (t-test, confidence intervals). \\
\texttt{compute\_stats} & 分析 & 运行统计检验（t检验、置信区间）。 \\
\texttt{write\_report} & Output & Write sections of the final research report (LaTeX/Markdown). \\
\texttt{write\_report} & 输出 & 撰写最终研究报告的章节（LaTeX/Markdown）。 \\
\texttt{think} & Reasoning & Internal reasoning step (no external tool call). \\
\texttt{think} & 推理 & 内部推理步骤（无外部工具调用）。 \\
\texttt{submit} & Terminal & Submit final report. Ends the episode. \\
\texttt{submit} & 终局 & 提交最终报告。结束该回合。 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Architecture: Model and Infrastructure Choices}
\subsection{架构：模型与基础设施选择}

\label{architecture-model-and-infrastructure-choices}

\begin{keybox}[Architecture Decisions — Applying Paper Concepts]
\begin{keybox}[架构决策——应用论文概念]
\begin{itemize}
  \item \textbf{Base model}: Qwen-2.5 72B (strong reasoning + code). QLoRA fine-tuning ($r=32$, all linear layers) --- see Section on LoRA.
  \item \textbf{基础模型}：Qwen-2.5 72B（强推理 + 代码能力）。使用 QLoRA 微调（$r=32$，所有线性层）——参见 LoRA 章节。
  \item \textbf{Inference}: vLLM with TP=4, prefix caching enabled (system prompt shared across rollouts) --- see vLLM section.
  \item \textbf{推理}：vLLM，TP=4，启用前缀缓存（系统提示在多个 rollout 间共享）——参见 vLLM 章节。
  \item \textbf{Training}: GRPO with $N=4$ trajectories per research question --- no value model needed (see GRPO section).
  \item \textbf{训练}：GRPO，每个研究问题生成 $N=4$ 条轨迹——无需价值模型（参见 GRPO 章节）。
  \item \textbf{Hardware}: 8$\times$H100 node. QLoRA adapters fit in 48 GB; vLLM generation uses remaining capacity.
  \item \textbf{硬件}：8$\times$H100 节点。QLoRA 适配器占用 48 GB；vLLM 生成占用剩余容量。
  \item \textbf{Context management}: 128K context with Flash Attention (see Flash Attention section). Sliding window summarization for trajectories exceeding context.
  \item \textbf{上下文管理}：128K 上下文，使用 Flash Attention（参见 Flash Attention 章节）。对于超出上下文的轨迹，采用滑动窗口摘要。
  \item \textbf{Speculative decoding}: Eagle heads for fast generation during long research trajectories (see Speculative Decoding section).
  \item \textbf{投机解码}：使用 Eagle heads 在长研究轨迹中加速生成（参见投机解码章节）。
\end{itemize}
\end{keybox}

\subsection{Reward Design}
\subsection{奖励设计}

\label{reward-design}

\begin{keybox}[Multi-Component Research Reward]
\begin{keybox}[多组件研究奖励]
The terminal reward is computed when the agent calls \texttt{submit}: 
当代理调用 \texttt{submit} 时计算最终奖励：
\[
R = w_1 R_{\text{quality}} + w_2 R_{\text{correctness}} + w_3 R_{\text{novelty}} + w_4 R_{\text{efficiency}} + w_5 R_{\text{format}}
\]

\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Component} & \textbf{Weight} & \textbf{How Measured} \\
\textbf{组件} & \textbf{权重} & \textbf{测量方式} \\
\midrule
$R_{\text{quality}}$ & 0.30 & LLM-as-judge (GPT-4 rates report 1--10 on clarity, depth, rigor) \\
$R_{\text{quality}}$ 质量 & 0.30 & LLM 作为评判者（GPT-4 对报告的清晰度、深度、严谨性评分 1--10） \\
$R_{\text{correctness}}$ & 0.30 & Code executes without errors + results are reproducible \\
$R_{\text{correctness}}$ 正确性 & 0.30 & 代码无错误执行 + 结果可复现 \\
$R_{\text{novelty}}$ & 0.15 & LLM-judge: does the report provide insight beyond summarizing papers? \\
$R_{\text{novelty}}$ 新颖性 & 0.15 & LLM 评判者：报告是否提供了超越论文总结的洞见？ \\
$R_{\text{efficiency}}$ & 0.15 & Bonus for fewer steps: $R_{\text{eff}} = \max(0, 1 - \text{steps}/100)$ \\
$R_{\text{efficiency}}$ 效率 & 0.15 & 步骤越少奖励越高：$R_{\text{eff}} = \max(0, 1 - \text{steps}/100)$ \\
$R_{\text{format}}$ & 0.10 & Report has all required sections (intro, method, results, conclusion) \\
$R_{\text{format}}$ 格式 & 0.10 & 报告包含所有必需章节（引言、方法、结果、结论） \\
\bottomrule
\end{tabular}

\textbf{Intermediate shaping}: +0.1 for each successful code execution; $-$0.05 for each runtime error (encourages writing correct code first).
\textbf{中间塑造}：每次成功代码执行 +0.1；每次运行时错误 $-$0.05（鼓励优先编写正确代码）。
\end{keybox}

\begin{warningbox}[Reward Hacking Risks]
\begin{warningbox}[奖励篡改风险]
\begin{itemize}
  \item \textbf{Fake results}: Agent fabricates experiment outputs. \emph{Fix}: Verify code actually ran by checking execution logs against reported numbers.
  \item \textbf{伪造结果}：代理捏造实验输出。\emph{修复}：通过检查执行日志与报告数字是否一致，验证代码是否实际运行。
  \item \textbf{Shallow reports}: Agent copies paper abstracts verbatim. \emph{Fix}: Novelty reward + plagiarism detection.
  \item \textbf{浅薄报告}：代理逐字复制论文摘要。\emph{修复}：新颖性奖励 + 抄袭检测。
  \item \textbf{Length gaming}: Long reports score higher. \emph{Fix}: Efficiency reward + length penalty.
  \item \textbf{长度投机}：长报告得分更高。\emph{修复}：效率奖励 + 长度惩罚。
  \item \textbf{Easy questions}: Agent avoids hard research questions. \emph{Fix}: Curriculum with difficulty levels.
  \item \textbf{简单问题}：代理回避困难的研究问题。\emph{修复}：带有难度级别的课程学习。
\end{itemize}
\end{warningbox}

\subsection{Training Pipeline}
\subsection{训练流程}

\label{training-pipeline}

\begin{enumerate}
  \item \textbf{Phase 1 --- SFT Warmup} (500 steps):
  \item \textbf{阶段 1 —— SFT 热身}（500 步）：

\begin{itemize}
  \item Collect 200 expert research trajectories (human researchers using the tools)
  \item 收集 200 条专家研究轨迹（人类研究人员使用这些工具）
  \item SFT on successful trajectories with completion-only masking (mask tool outputs)
  \item 在成功轨迹上进行 SFT，使用仅补全掩码（掩盖工具输出）
  \item This teaches the agent tool-use syntax and basic research workflow
  \item 这教会代理工具使用语法和基本研究工作流程
\end{itemize}
  \item \textbf{Phase 2 --- GRPO Training} (3000 steps):
  \item \textbf{阶段 2 —— GRPO 训练}（3000 步）：

\begin{itemize}
  \item Prompt pool: 500 research questions across 10 domains (ML, NLP, CV, systems, etc.)
  \item 提示池：涵盖 10 个领域（机器学习、自然语言处理、计算机视觉、系统等）的 500 个研究问题
  \item Per question: generate $N=4$ complete research trajectories
  \item 每个问题：生成 $N=4$ 条完整的研究轨迹
  \item Score each trajectory with multi-component reward
  \item 使用多组件奖励对每条轨迹评分
  \item GRPO advantage: $\hat{A}_i = (R_i - \mu_G) / \sigma_G$
  \item GRPO 优势：$\hat{A}_i = (R_i - \mu_G) / \sigma_G$
  \item Update policy with clipped objective (clip $\epsilon=0.2$, KL $\beta=0.05$)
  \item 使用裁剪目标更新策略（裁剪 $\epsilon=0.2$，KL $\beta=0.05$）
  \item Curriculum: start with simple ``summarize findings on X'' tasks, progress to ``design and run experiment on X''
  \item 课程安排：从简单的“总结关于 X 的发现”任务开始，逐步过渡到“设计并运行关于 X 的实验”
\end{itemize}
  \item \textbf{Phase 3 --- Rejection Sampling Fine-Tuning} (200 steps):
  \item \textbf{阶段 3 —— 拒绝采样微调}（200 步）：

\begin{itemize}
  \item Generate 16 trajectories per hard question, keep top-2 by reward
  \item 每个困难问题生成 16 条轨迹，保留奖励最高的 2 条
  \item SFT on these high-quality trajectories
  \item 在这些高质量轨迹上进行 SFT
  \item Stabilizes performance on the hardest research tasks
  \item 稳定在最困难研究任务上的表现
\end{itemize}
\end{enumerate}

\subsection{Example Trajectory: Full MDP Trace}
\subsection{示例轨迹：完整 MDP 跟踪}

\label{example-trajectory-full-mdp-trace}

To illustrate how all the MDP components work together in practice, we trace a complete research episode from question to submission, annotating each step with its formal MDP elements.
为了说明所有 MDP 组件在实践中如何协同工作，我们跟踪一个完整的研究回合，从问题到提交，并用正式的 MDP 元素标注每一步。

\begin{examplebox}[Research Agent Trajectory — Full MDP Trace]
\begin{examplebox}[研究代理轨迹——完整 MDP 跟踪]
\textbf{Research question}: ``Does increasing GRPO group size beyond $N=16$ improve math reasoning performance?''
\textbf{研究问题}：“将 GRPO 组大小增加到 $N=16$ 以上是否能提高数学推理性能？”

Below is a complete trajectory with explicit MDP notation for each step: state $s_t$, action $a_t$, transition $T$, observation $o_t$, and cumulative reward.
以下是一条完整轨迹，每一步都带有明确的 MDP 符号：状态 $s_t$、动作 $a_t$、转移 $T$、观测 $o_t$ 和累积奖励。

{\footnotesize
\begin{tabular}{@{}cp{2.2cm}p{10.5cm}@{}}
\toprule
$t$ & \textbf{Element} & \textbf{Description} \\
\midrule
 & $a_0$ & \texttt{think}: ``I need papers on GRPO group size ablations, then a controlled experiment.'' \\
 & $o_0$ & Internal reasoning (no tool output). Shaping reward: $r_0 = 0$. \\
1 & $s_1$ & $s_0 \oplus (a_0, o_0)$ --- context now includes reasoning plan. \\
 & $a_1$ & \texttt{search\_papers(query="GRPO group size ablation math")} \\
 & $o_1$ & Returns 5 papers: [DAPO, DeepSeek-Math, Dr.~GRPO, ...]. $r_1 = 0$. \\
2 & $s_2$ & $s_1 \oplus (a_1, o_1)$ --- search results in context. \\
 & $a_2$ & \texttt{read\_paper(id="DAPO", sections=["experiments", "ablations"])} \\
 & $o_2$ & Key finding: ``diminishing returns above $N=16$ on code tasks; math untested.'' $r_2 = 0$. \\
3 & $s_3$ & $s_2 \oplus (a_2, o_2)$ --- literature gap identified. \\
 & $a_3$ & \texttt{think}: ``DAPO tested code only. I’ll test $N \in \{4, 8, 16, 32, 64\}$ on GSM8K with Llama-3 8B. Control: same total training tokens.'' \\
 & $o_3$ & Hypothesis formed. $r_3 = 0$. \\
4 & $s_4$ & $s_3 \oplus (a_3, o_3)$ --- experiment plan in context. \\
 & $a_4$ & \texttt{write\_code("train\_grpo\_gsm8k.py")} --- 85-line script with argparse for group\_size, proper seed, eval on GSM8K test split. \\
 & $o_4$ & File written successfully. $r_4 = 0$. \\
5 & $s_5$ & $s_4 \oplus (a_4, o_4)$ --- code available in workspace. \\
 & $a_5$ & \texttt{execute\_code("python train\_grpo\_gsm8k.py --N 4 --seed 42")} \\
 & $o_5$ & \texttt{Accuracy: 67.2\% (CI: 65.1--69.3)}. $r_5 = +0.1$ (successful execution). \\
6--8 & $a_{6\text{--}8}$ & Execute with $N=8, 16, 32$ $\to$ results: 71.4\%, 74.8\%, 75.9\%. Each $r_t = +0.1$. \\
9 & $s_9$ & Context includes 4 data points. \\
 & $a_9$ & \texttt{execute\_code("python train\_grpo\_gsm8k.py --N 64 --seed 42")} \\
 & $o_9$ & \texttt{Accuracy: 75.6\% (CI: 73.4--77.8)} --- slight \emph{decrease} from $N=32$! $r_9 = +0.1$. \\
10 & $s_{10}$ & All 5 results available. \\
 & $a_{10}$ & \texttt{compute\_stats(test="paired\_t\_test", data=[67.2, 71.4, 74.8, 75.9, 75.6], groups=[4,8,16,32,64])} \\
 & $o_{10}$ & $p < 0.01$ for $N=4$ vs $N=16$; $p = 0.72$ for $N=32$ vs $N=64$ (not significant). $r_{10} = 0$. \\
11 & $s_{11}$ & Statistical evidence for diminishing returns. \\
 & $a_{11}$ & \texttt{plot\_data(x=[4,8,16,32,64], y=[67.2,71.4,74.8,75.9,75.6], xlabel="Group Size N", ylabel="GSM8K Accuracy (\%)", title="GRPO Group Size vs Math Reasoning")} \\
 & $o_{11}$ & Plot saved to \texttt{results/group\_size\_curve.png}. $r_{11} = 0$. \\
12 & $s_{12}$ & Full evidence assembled. \\
 & $a_{12}$ & \texttt{write\_report}: 4-section report (Introduction, Method, Results with figure, Conclusion: ``$N=16$--32 is optimal; $N=64$ shows no gain and increases compute 4$\times$''). \\
 & $o_{12}$ & Report written (2,100 words). $r_{12} = 0$. \\
13 & $a_{13}$ & \texttt{submit} --- episode terminates. \\
 & $R_{\text{terminal}}$ & LLM-judge scores: quality=8/10, code correct, novel (extends DAPO to math), 13 steps, all sections present. \\
\bottomrule
\end{tabular}
}

\textbf{Terminal reward computation}: 
\begin{multline*}
R = \underbrace{0.30 \times \tfrac{8}{10}}_{\text{quality}} + \underbrace{0.30 \times 1.0}_{\text{correct}} + \underbrace{0.15 \times \tfrac{7}{10}}_{\text{novelty}} + \underbrace{0.15 \times (1 - \tfrac{13}{100})}_{\text{efficiency}} + \underbrace{0.10 \times 1.0}_{\text{format}} \\
= 0.24 + 0.30 + 0.105 + 0.13 + 0.10 = \mathbf{0.875}
\end{multline*}


\textbf{Intermediate shaping total}: $5 \times (+0.1) = +0.5$ (5 successful code executions).


\textbf{GRPO context}: This trajectory scored highest among the $N=4$ group (others scored 0.61, 0.72, 0.53). GRPO advantage: 
\[
\hat{A} = \frac{0.875 - \bar{R}}{\sigma_R} = \frac{0.875 - 0.684}{0.129} = +1.48 \quad \text{(strongly reinforced)}
\]


\textbf{Key MDP properties illustrated}:


\begin{itemize}
  \item \textbf{Deterministic $T$}: Each tool call produces a predictable state extension ($s_{t+1} = s_t \oplus (a_t, o_t)$).
  \item \textbf{Sparse terminal reward}: The real quality signal comes only at \texttt{submit}; intermediate shaping is small.
  \item \textbf{Long horizon}: 13 steps with $\gamma = 1.0$ (no discounting for episodic tasks).
  \item \textbf{Self-correction opportunity}: At step 9, the agent observes $N=64$ doesn’t improve --- adjusts its conclusion accordingly rather than cherry-picking.
  \item \textbf{Action diversity}: Mix of reasoning (\texttt{think}), information gathering (\texttt{search}, \texttt{read}), execution (\texttt{write\_code}, \texttt{execute}), analysis (\texttt{compute\_stats}, \texttt{plot}), and output (\texttt{write\_report}, \texttt{submit}).
\end{itemize}
\end{examplebox}


\subsection{Key Design Decisions and Tradeoffs}
\label{key-design-decisions-and-tradeoffs}


\begin{table}[ht!]
\centering
\caption{Design decisions for the research agent, mapped to paper sections.}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Decision} & \textbf{Paper Section} & \textbf{Rationale} \\
\midrule
QLoRA ($r=32$) & LoRA section & 72B model; full fine-tune too expensive. $r=32$ for complex reasoning. \\
GRPO (not PPO) & GRPO section & No value model needed; research quality is hard to predict mid-trajectory. \\
Sparse terminal reward & Reward Shaping & Research quality only measurable at completion; intermediate shaping minimal. \\
$N=4$ trajectories & GRPO Group Size & Balance: enough diversity for ranking, not too expensive (100-step trajectories). \\
128K context & Flash Attention & Long trajectories with paper contents + code + results. \\
vLLM + prefix caching & vLLM section & System prompt + research question shared across 4 rollouts. \\
Curriculum training & Agentic RL & Start simple (literature review) $\to$ hard (design + execute experiments). \\
LLM-as-judge reward & Reward Models & Research quality is subjective; LLM judge is more flexible than rule-based. \\
\bottomrule
\end{tabular}
\end{table}


\subsection{Evaluation}
\label{evaluation}


\begin{keybox}[Research Agent Evaluation Framework]
\begin{itemize}
  \item \textbf{Held-out questions} (50): Research questions unseen during training, covering diverse domains.
  \item \textbf{Human evaluation}: Domain experts rate reports on a 1--5 scale (quality, correctness, actionability).
  \item \textbf{Reproducibility}: Re-run the agent’s code from the report; verify results match.
  \item \textbf{Comparison baselines}: (1) Zero-shot GPT-4 + tools (no RL training), (2) SFT-only agent, (3) Human researchers.
  \item \textbf{Efficiency metric}: Steps-to-completion normalized by task difficulty.
\end{itemize}


\textbf{Expected results} (based on similar agentic RL work):


\begin{tabular}{@{}lcc@{}}
\toprule
\textbf{Agent} & \textbf{Report Quality (1--5)} & \textbf{Avg Steps} \\
\midrule
Zero-shot GPT-4 + tools & 2.8 & 25 \\
SFT-only & 3.4 & 18 \\
GRPO-trained (ours) & 4.1 & 14 \\
Human researcher & 4.5 & N/A \\
\bottomrule
\end{tabular}
\end{keybox}


\subsection{Lessons and Failure Modes}
\label{lessons-and-failure-modes}


Now produce the bilingual translation following ALL rules above. Start directly with the translated content (no preamble).{\footnotesize
\begin{tabular}{@{}cp{2.2cm}p{10.5cm}@{}}
\toprule
$t$ & \textbf{Element} & \textbf{Description} \\
\midrule
 & $a_0$ & \texttt{think}: ``I need papers on GRPO group size ablations, then a controlled experiment.'' \\
 & $o_0$ & Internal reasoning (no tool output). Shaping reward: $r_0 = 0$. \\
1 & $s_1$ & $s_0 \oplus (a_0, o_0)$ --- context now includes reasoning plan. \\
 & $a_1$ & \texttt{search\_papers(query="GRPO group size ablation math")} \\
 & $o_1$ & Returns 5 papers: [DAPO, DeepSeek-Math, Dr.~GRPO, ...]. $r_1 = 0$. \\
2 & $s_2$ & $s_1 \oplus (a_1, o_1)$ --- search results in context. \\
 & $a_2$ & \texttt{read\_paper(id="DAPO", sections=["experiments", "ablations"])} \\
 & $o_2$ & Key finding: ``diminishing returns above $N=16$ on code tasks; math untested.'' $r_2 = 0$. \\
3 & $s_3$ & $s_2 \oplus (a_2, o_2)$ --- literature gap identified. \\
 & $a_3$ & \texttt{think}: ``DAPO tested code only. I’ll test $N \in \{4, 8, 16, 32, 64\}$ on GSM8K with Llama-3 8B. Control: same total training tokens.'' \\
 & $o_3$ & Hypothesis formed. $r_3 = 0$. \\
4 & $s_4$ & $s_3 \oplus (a_3, o_3)$ --- experiment plan in context. \\
 & $a_4$ & \texttt{write\_code("train\_grpo\_gsm8k.py")} --- 85-line script with argparse for group\_size, proper seed, eval on GSM8K test split. \\
 & $o_4$ & File written successfully. $r_4 = 0$. \\
5 & $s_5$ & $s_4 \oplus (a_4, o_4)$ --- code available in workspace. \\
 & $a_5$ & \texttt{execute\_code("python train\_grpo\_gsm8k.py --N 4 --seed 42")} \\
 & $o_5$ & \texttt{Accuracy: 67.2\% (CI: 65.1--69.3)}. $r_5 = +0.1$ (successful execution). \\
6--8 & $a_{6\text{--}8}$ & Execute with $N=8, 16, 32$ $\to$ results: 71.4\%, 74.8\%, 75.9\%. Each $r_t = +0.1$. \\
9 & $s_9$ & Context includes 4 data points. \\
 & $a_9$ & \texttt{execute\_code("python train\_grpo\_gsm8k.py --N 64 --seed 42")} \\
 & $o_9$ & \texttt{Accuracy: 75.6\% (CI: 73.4--77.8)} --- slight \emph{decrease} from $N=32$! $r_9 = +0.1$. \\
10 & $s_{10}$ & All 5 results available. \\
 & $a_{10}$ & \texttt{compute\_stats(test="paired\_t\_test", data=[67.2, 71.4, 74.8, 75.9, 75.6], groups=[4,8,16,32,64])} \\
 & $o_{10}$ & $p < 0.01$ for $N=4$ vs $N=16$; $p = 0.72$ for $N=32$ vs $N=64$ (not significant). $r_{10} = 0$. \\
11 & $s_{11}$ & Statistical evidence for diminishing returns. \\
 & $a_{11}$ & \texttt{plot\_data(x=[4,8,16,32,64], y=[67.2,71.4,74.8,75.9,75.6], xlabel="Group Size N", ylabel="GSM8K Accuracy (\%)", title="GRPO Group Size vs Math Reasoning")} \\
 & $o_{11}$ & Plot saved to \texttt{results/group\_size\_curve.png}. $r_{11} = 0$. \\
12 & $s_{12}$ & Full evidence assembled. \\
 & $a_{12}$ & \texttt{write\_report}: 4-section report (Introduction, Method, Results with figure, Conclusion: ``$N=16$--32 is optimal; $N=64$ shows no gain and increases compute 4$\times$''). \\
 & $o_{12}$ & Report written (2,100 words). $r_{12} = 0$. \\
13 & $a_{13}$ & \texttt{submit} --- episode terminates. \\
 & $R_{\text{terminal}}$ & LLM-judge scores: quality=8/10, code correct, novel (extends DAPO to math), 13 steps, all sections present. \\
\bottomrule
\end{tabular}
}

\textbf{Terminal reward computation}: 
\begin{multline*}
R = \underbrace{0.30 \times \tfrac{8}{10}}_{\text{quality}} + \underbrace{0.30 \times 1.0}_{\text{correct}} + \underbrace{0.15 \times \tfrac{7}{10}}_{\text{novelty}} + \underbrace{0.15 \times (1 - \tfrac{13}{100})}_{\text{efficiency}} + \underbrace{0.10 \times 1.0}_{\text{format}} \\
= 0.24 + 0.30 + 0.105 + 0.13 + 0.10 = \mathbf{0.875}
\end{multline*}
\textbf{终端奖励计算}： 
\begin{multline*}
R = \underbrace{0.30 \times \tfrac{8}{10}}_{\text{质量}} + \underbrace{0.30 \times 1.0}_{\text{正确性}} + \underbrace{0.15 \times \tfrac{7}{10}}_{\text{新颖性}} + \underbrace{0.15 \times (1 - \tfrac{13}{100})}_{\text{效率}} + \underbrace{0.10 \times 1.0}_{\text{格式}} \\
= 0.24 + 0.30 + 0.105 + 0.13 + 0.10 = \mathbf{0.875}
\end{multline*}

\textbf{Intermediate shaping total}: $5 \times (+0.1) = +0.5$ (5 successful code executions).
\textbf{中间塑形奖励总计}：$5 \times (+0.1) = +0.5$（5次成功的代码执行）。

\textbf{GRPO context}: This trajectory scored highest among the $N=4$ group (others scored 0.61, 0.72, 0.53). GRPO advantage: 
\[
\hat{A} = \frac{0.875 - \bar{R}}{\sigma_R} = \frac{0.875 - 0.684}{0.129} = +1.48 \quad \text{(strongly reinforced)}
\]
\textbf{GRPO上下文}：该轨迹在$N=4$组中得分最高（其他轨迹得分为0.61、0.72、0.53）。GRPO优势值（advantage）：
\[
\hat{A} = \frac{0.875 - \bar{R}}{\sigma_R} = \frac{0.875 - 0.684}{0.129} = +1.48 \quad \text{（强强化）}
\]

\textbf{Key MDP properties illustrated}:
\textbf{所展示的关键MDP性质}：

\begin{itemize}
  \item \textbf{Deterministic $T$}: Each tool call produces a predictable state extension ($s_{t+1} = s_t \oplus (a_t, o_t)$).
  \item \textbf{Sparse terminal reward}: The real quality signal comes only at \texttt{submit}; intermediate shaping is small.
  \item \textbf{Long horizon}: 13 steps with $\gamma = 1.0$ (no discounting for episodic tasks).
  \item \textbf{Self-correction opportunity}: At step 9, the agent observes $N=64$ doesn’t improve --- adjusts its conclusion accordingly rather than cherry-picking.
  \item \textbf{Action diversity}: Mix of reasoning (\texttt{think}), information gathering (\texttt{search}, \texttt{read}), execution (\texttt{write\_code}, \texttt{execute}), analysis (\texttt{compute\_stats}, \texttt{plot}), and output (\texttt{write\_report}, \texttt{submit}).
\end{itemize}
\begin{itemize}
  \item \textbf{确定性转移函数$T$}：每次工具调用都会产生可预测的状态扩展（$s_{t+1} = s_t \oplus (a_t, o_t)$）。
  \item \textbf{稀疏的终端奖励}：真正的质量信号仅在\texttt{submit}时出现；中间塑形奖励很小。
  \item \textbf{长视野}：13步，$\gamma = 1.0$（对于回合制任务不进行折扣）。
  \item \textbf{自我纠正机会}：在第9步，智能体观察到$N=64$没有提升——相应地调整其结论，而不是挑挑拣拣。
  \item \textbf{动作多样性}：混合了推理（\texttt{think}）、信息收集（\texttt{search}、\texttt{read}）、执行（\texttt{write\_code}、\texttt{execute}）、分析（\texttt{compute\_stats}、\texttt{plot}）和输出（\texttt{write\_report}、\texttt{submit}）。
\end{itemize}
\end{examplebox}


\subsection{Key Design Decisions and Tradeoffs}
\subsection{关键设计决策与权衡}
\label{key-design-decisions-and-tradeoffs}


\begin{table}[ht!]
\centering
\caption{Design decisions for the research agent, mapped to paper sections.}
\caption{研究智能体的设计决策，映射到论文章节。}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Decision} & \textbf{Paper Section} & \textbf{Rationale} \\
\midrule
QLoRA ($r=32$) & LoRA section & 72B model; full fine-tune too expensive. $r=32$ for complex reasoning. \\
GRPO (not PPO) & GRPO section & No value model needed; research quality is hard to predict mid-trajectory. \\
Sparse terminal reward & Reward Shaping & Research quality only measurable at completion; intermediate shaping minimal. \\
$N=4$ trajectories & GRPO Group Size & Balance: enough diversity for ranking, not too expensive (100-step trajectories). \\
128K context & Flash Attention & Long trajectories with paper contents + code + results. \\
vLLM + prefix caching & vLLM section & System prompt + research question shared across 4 rollouts. \\
Curriculum training & Agentic RL & Start simple (literature review) $\to$ hard (design + execute experiments). \\
LLM-as-judge reward & Reward Models & Research quality is subjective; LLM judge is more flexible than rule-based. \\
\bottomrule
\end{tabular}
\end{table}
\begin{table}[ht!]
\centering
\caption{研究智能体的设计决策，映射到论文章节。}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{决策} & \textbf{论文对应章节} & \textbf{理由} \\
\midrule
QLoRA ($r=32$) & LoRA节 & 72B模型；全参数微调成本过高。$r=32$适用于复杂推理。 \\
GRPO（而非PPO） & GRPO节 & 无需价值模型；研究质量在轨迹中途难以预测。 \\
稀疏终端奖励 & 奖励塑形节 & 研究质量仅在完成时可衡量；中间塑形奖励最小化。 \\
$N=4$条轨迹 & GRPO组大小节 & 平衡：足够的多样性用于排名，且不会过于昂贵（100步轨迹）。 \\
128K上下文 & Flash Attention节 & 长轨迹包含论文内容+代码+结果。 \\
vLLM + 前缀缓存（prefix caching） & vLLM节 & 系统提示词+研究问题在4次 rollout 间共享。 \\
课程训练（Curriculum training） & 智能体强化学习节 & 从简单开始（文献综述）$\to$ 困难（设计+执行实验）。 \\
LLM作为评判者的奖励 & 奖励模型节 & 研究质量是主观的；LLM评判者比基于规则的方法更灵活。 \\
\bottomrule
\end{tabular}
\end{table}


\subsection{Evaluation}
\subsection{评估}
\label{evaluation}


\begin{keybox}[Research Agent Evaluation Framework]
\begin{itemize}
  \item \textbf{Held-out questions} (50): Research questions unseen during training, covering diverse domains.
  \item \textbf{Human evaluation}: Domain experts rate reports on a 1--5 scale (quality, correctness, actionability).
  \item \textbf{Reproducibility}: Re-run the agent’s code from the report; verify results match.
  \item \textbf{Comparison baselines}: (1) Zero-shot GPT-4 + tools (no RL training), (2) SFT-only agent, (3) Human researchers.
  \item \textbf{Efficiency metric}: Steps-to-completion normalized by task difficulty.
\end{itemize}


\textbf{Expected results} (based on similar agentic RL work):


\begin{tabular}{@{}lcc@{}}
\toprule
\textbf{Agent} & \textbf{Report Quality (1--5)} & \textbf{Avg Steps} \\
\midrule
Zero-shot GPT-4 + tools & 2.8 & 25 \\
SFT-only & 3.4 & 18 \\
GRPO-trained (ours) & 4.1 & 14 \\
Human researcher & 4.5 & N/A \\
\bottomrule
\end{tabular}
\end{keybox}
\begin{keybox}[研究智能体评估框架]
\begin{itemize}
  \item \textbf{保留问题（Held-out questions）}（50个）：训练期间未见过的研究问题，涵盖多样化领域。
  \item \textbf{人工评估（Human evaluation）}：领域专家对报告进行1--5分评分（质量、正确性、可操作性）。
  \item \textbf{可复现性（Reproducibility）}：根据报告重新运行智能体的代码；验证结果是否匹配。
  \item \textbf{对比基线（Comparison baselines）}：（1）零样本GPT-4 + 工具（无RL训练），（2）仅SFT的智能体，（3）人类研究人员。
  \item \textbf{效率指标（Efficiency metric）}：完成任务所需步数，按任务难度归一化。
\end{itemize}

\textbf{预期结果}（基于类似的智能体强化学习工作）：

\begin{tabular}{@{}lcc@{}}
\toprule
\textbf{智能体} & \textbf{报告质量（1-5）} & \textbf{平均步数} \\
\midrule
零样本GPT-4 + 工具 & 2.8 & 25 \\
仅SFT & 3.4 & 18 \\
GRPO训练（我们的） & 4.1 & 14 \\
人类研究人员 & 4.5 & N/A \\
\bottomrule
\end{tabular}
\end{keybox}


\subsection{Lessons and Failure Modes}
\subsection{经验教训与失败模式}
\label{lessons-and-failure-modes}

```markdown
\begin{warningbox}[Common Failures in Research Agent Training]
\begin{warningbox}[研究智能体训练中的常见失败]

\begin{itemize}
  \item \textbf{Infinite loops}: Agent repeatedly searches for papers without progressing. \emph{Fix}: Step budget + penalty for repeated tool calls with same arguments.
  \item \textbf{无限循环}：智能体不断搜索论文而无进展。\emph{修复}：步骤预算 + 对重复相同参数的工具调用施加惩罚。
  \item \textbf{Code debugging spirals}: Agent spends 20+ steps fixing a single bug. \emph{Fix}: Cap retries at 3; if code fails 3 times, abandon approach and try alternative.
  \item \textbf{代码调试螺旋}：智能体花费20步以上修复单个漏洞。\emph{修复}：重试上限设为3次；若代码连续失败3次，放弃当前方法并尝试替代方案。
  \item \textbf{Hallucinated citations}: Agent invents paper titles/results. \emph{Fix}: Verify all citations exist via tool output; penalize unverifiable claims.
  \item \textbf{幻觉引用}：智能体虚构论文标题/结果。\emph{修复}：通过工具输出验证所有引用是否存在；对无法验证的主张施加惩罚。
  \item \textbf{Premature submission}: Agent submits incomplete reports to avoid penalty for long trajectories. \emph{Fix}: Minimum quality threshold ($R > 0.4$) to count as valid submission; below threshold is treated as failure.
  \item \textbf{过早提交}：智能体为规避长轨迹的惩罚而提交不完整报告。\emph{修复}：设定最低质量阈值（$R > 0.4$）才能算作有效提交；低于阈值视为失败。
  \item \textbf{Reward hacking the judge}: Agent learns to produce text that scores high with the LLM judge but is scientifically shallow. \emph{Fix}: Rotate judge models; include human eval in the reward periodically.
  \item \textbf{奖励黑客攻击评判器}：智能体学会生成对LLM评判器得分高但科学内容浅薄的文本。\emph{修复}：轮换评判模型；定期将人工评估纳入奖励。
\end{itemize}
\end{warningbox}

\section{State-of-the-Art RL for LLM Agents}
\section{面向LLM智能体的最先进强化学习}
\label{state-of-the-art-rl-for-llm-agents}


RL techniques for LLM agents focus on \textbf{on-policy policy gradients} combined with \textbf{fine-grained credit assignment}. Because agents execute complex multi-turn trajectories involving tool interactions, API queries, and code execution, standard single-turn alignment algorithms must be heavily modified.
面向LLM智能体的强化学习技术专注于\textbf{同策略策略梯度}与\textbf{细粒度信用分配}的结合。由于智能体执行涉及工具交互、API查询和代码执行的复杂多轮轨迹，标准的单轮对齐算法必须进行大幅修改。

\subsection{Dominant Baseline: GRPO for Agents}
\subsection{主流基线：面向智能体的GRPO}
\label{dominant-baseline-grpo-for-agents}


Popularized by DeepSeek-R1~\cite{deepseek2025r1}, \textbf{GRPO}~\cite{shao2024deepseekmath} is rapidly becoming the standard for agentic training. It samples a group of $N$ complete trajectories per task, eliminating the memory-intensive critic network:
由DeepSeek-R1~\cite{deepseek2025r1}推广的\textbf{GRPO}~\cite{shao2024deepseekmath}正迅速成为智能体训练的标准。它针对每个任务采样一组$N$条完整轨迹，消除了内存密集型的评论家网络：

For a task prompt $q$, GRPO samples $N$ agentic trajectories $\{o_1, o_2, \dots, o_N\}$ from $\pi_{\theta_{\text{old}}}$. The advantage for each trajectory is computed by normalizing its reward relative to the group: 
对于任务提示$q$，GRPO从$\pi_{\theta_{\text{old}}}$中采样$N$条智能体轨迹$\{o_1, o_2, \dots, o_N\}$。每条轨迹的优势通过将其奖励相对于组进行归一化来计算：
\begin{equation}
\boxed{A_i = \frac{r(o_i) - \frac{1}{N}\sum_{j=1}^N r(o_j)}{\text{std}(r(o_1), \dots, r(o_N))}}
\end{equation}


The GRPO objective with KL regularization: 
带有KL正则化的GRPO目标函数：
\begin{equation}
L_{\text{GRPO}}(\theta) = \frac{1}{N} \sum_{i=1}^N \min\!\left( \frac{\pi_\theta(o_i|q)}{\pi_{\theta_{\text{old}}}(o_i|q)} A_i,\; \text{clip}\!\left(\frac{\pi_\theta(o_i|q)}{\pi_{\theta_{\text{old}}}(o_i|q)}, 1{-}\epsilon, 1{+}\epsilon\right) A_i \right) - \beta\, D_{\text{KL}}(\pi_\theta \| \pi_{\text{ref}})
\end{equation}


\begin{intuitionbox}[Why GRPO Dominates Agentic Training]
\begin{intuitionbox}[GRPO为何主导智能体训练]

\begin{itemize}
  \item \textbf{No critic}: Saves 50\% GPU memory --- critical when agent trajectories already consume massive context windows (32K--128K tokens).
  \item \textbf{无需评论家}：节省50%的GPU内存——在智能体轨迹已消耗大量上下文窗口（32K--128K token）时至关重要。
  \item \textbf{Natural fit}: Agent tasks often have binary verifiable rewards (tests pass/fail, goal achieved/not) --- perfect for group-relative normalization.
  \item \textbf{自然适配}：智能体任务通常具有二元可验证奖励（测试通过/失败、目标达成/未达成）——非常适合组相对归一化。
  \item \textbf{Exploration}: Sampling $N$ diverse trajectories per task naturally explores different tool-use strategies.
  \item \textbf{探索}：对每个任务采样$N$条多样化轨迹，自然探索了不同的工具使用策略。
\end{itemize}
\end{intuitionbox}


\subsection{PPO for Interactive Agents}
\subsection{面向交互式智能体的PPO}
\label{ppo-for-interactive-agents}


\textbf{PPO}~\cite{schulman2017proximal} remains valuable for agents operating in highly stochastic environments where step-level value estimation helps. The critic provides per-step advantage signals, enabling finer credit assignment when tool outputs are unpredictable:
\textbf{PPO}~\cite{schulman2017proximal}对于在高度随机环境中运行的智能体仍然有价值，因为此时步骤级别的价值估计有帮助。评论家提供每步的优势信号，在工具输出不可预测时实现更精细的信用分配：


\begin{itemize}
  \item Step-level advantage estimation via GAE handles variable-length tool outputs
  \item 通过GAE进行步骤级优势估计，处理可变长度的工具输出
  \item Value head learns to predict ``how likely is this trajectory to succeed from here''
  \item 价值头学习预测“从此处开始该轨迹成功可能性有多大”
  \item More stable when external tools return catastrophic errors that spike reward variance
  \item 当外部工具返回导致奖励方差激增的灾难性错误时更稳定
  \item Trade-off: requires $2\times$ memory (critic) but provides denser learning signals
  \item 权衡：需要$2\times$的内存（评论家）但提供更密集的学习信号
\end{itemize}


\subsection{Fine-Grained Turn-Level Credit Assignment}
\subsection{细粒度回合级信用分配}
\label{fine-grained-turn-level-credit-assignment}


The core challenge in agentic RL is the \textbf{sparse reward problem}. If an agent executes 20 tool actions and finally fails a unit test, a terminal reward of $0$ punishes all 20 actions equally. Modern solutions:
智能体强化学习的核心挑战是\textbf{稀疏奖励问题}。如果智能体执行了20次工具操作，最后单元测试失败，终端奖励$0$会平等地惩罚所有20次操作。现代解决方案：


\begin{keybox}[Reinforcement Learning from Verifiable Rewards (RLVR)]
\begin{keybox}[可验证奖励强化学习 (RLVR)]

Reward the model at \textbf{deterministic intermediate checkpoints}:
在\textbf{确定性中间检查点}对模型进行奖励：


\begin{itemize}
  \item Bash command compiles successfully $\rightarrow$ +0.1
  \item Bash命令编译成功 $\rightarrow$ +0.1
  \item Browser agent targets correct HTML element $\rightarrow$ +0.2
  \item 浏览器智能体定位到正确的HTML元素 $\rightarrow$ +0.2
  \item SQL query returns non-empty results $\rightarrow$ +0.1
  \item SQL查询返回非空结果 $\rightarrow$ +0.1
  \item Final test suite passes $\rightarrow$ +1.0 (terminal)
  \item 最终测试套件通过 $\rightarrow$ +1.0（终端）
\end{itemize}


Intermediate rewards provide gradient signal to \emph{every} step, not just the final one. This dramatically accelerates learning by 3--5$\times$ compared to sparse-only rewards.
中间奖励为\emph{每一个}步骤提供梯度信号，而不仅仅是最后一步。与纯稀疏奖励相比，这使学习速度提升3--5倍。
\end{keybox}


\begin{keybox}[Multi-Turn Trajectory Slicing]
\begin{keybox}[多轮轨迹切片]

Frameworks split a multi-turn agent run into individual, independent steps. A credit assignment module isolates the \textbf{exact sub-step that broke the trajectory}:
框架将多轮智能体运行拆分为独立的单个步骤。信用分配模块隔离\textbf{恰好破坏轨迹的子步骤}：


\begin{enumerate}
  \item Replay the successful prefix (steps 1--$k$)
  \item 重放成功的前缀（步骤1--$k$）
  \item Identify the first divergence point (step $k+1$ where it went wrong)
  \item 识别第一个分歧点（出错的步骤$k+1$）
  \item Assign negative reward only to that specific step
  \item 仅对该特定步骤分配负奖励
  \item Assign neutral/positive rewards to correct prefix steps
  \item 对正确的前缀步骤分配中性/正奖励
\end{enumerate}


This enables surgical policy updates without degrading already-correct behavior.
这使得能够进行精确的策略更新，而不会降低已正确行为的表现。
\end{keybox}


\subsection{Alternative Paradigms}
\subsection{替代范式}
\label{alternative-paradigms}


\begin{itemize}
  \item \textbf{Iterative STaR (Self-Taught Reasoner)}~\cite{zelikman2022star}: Rather than continuous RL, use iterative offline loops. Generate trajectories $\rightarrow$ filter failures $\rightarrow$ SFT on successes $\rightarrow$ repeat. Simple to scale, avoids RL instability. Each iteration bootstraps reasoning ability.
  \item \textbf{迭代STaR（自教推理器）}~\cite{zelikman2022star}：不采用连续强化学习，而是使用迭代离线循环。生成轨迹 $\rightarrow$ 过滤失败 $\rightarrow$ 在成功轨迹上做SFT $\rightarrow$ 重复。易于扩展，避免了RL的不稳定性。每次迭代都能提升推理能力。
  \item \textbf{Reinforcement World Model Learning (RWML)}~\cite{yu2026rwml}: To combat reward hacking, train agents to predict the \emph{semantic consequence} of their actions. The agent receives an auxiliary reward for accurately predicting how environment state will change (e.g., predicting database table changes before executing SQL). This forces genuine understanding over superficial reward-gaming.
  \item \textbf{强化世界模型学习 (RWML)}~\cite{yu2026rwml}：为对抗奖励黑客攻击，训练智能体预测其行动的\emph{语义后果}。智能体因准确预测环境状态变化（例如在执行SQL前预测数据库表的变化）而获得辅助奖励。这迫使智能体产生真正的理解，而非肤浅的奖励追求。
  \item \textbf{LATS (Language Agent Tree Search)}~\cite{zhou2024lats}: Apply Monte Carlo Tree Search over agent action sequences. At each step, expand multiple candidate actions, simulate their outcomes, and backpropagate rewards through the tree. Combines RL value estimation with search-time compute scaling.
  \item \textbf{LATS（语言智能体树搜索）}~\cite{zhou2024lats}：在智能体动作序列上应用蒙特卡洛树搜索。在每一步，扩展多个候选动作，模拟其结果，并通过树反向传播奖励。结合了RL价值估计与搜索时的计算扩展。
\end{itemize}


\subsection{Core Methodology Comparison}
\subsection{核心方法论比较}
\label{core-methodology-comparison}


\begin{table}[ht!]
\centering
\caption{Comparison of RL paradigms for LLM agents.}
\caption{面向LLM智能体的RL范式比较。}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{Method} & \textbf{Reward Density} & \textbf{Memory Cost} & \textbf{Primary Advantage} \\
\textbf{方法} & \textbf{奖励密度} & \textbf{内存成本} & \textbf{主要优势} \\
\midrule
\textbf{GRPO}~\cite{shao2024deepseekmath} & Sequence / final metric & Low (no critic) & Massive GPU memory reduction; simple implementation \\
\textbf{GRPO}~\cite{shao2024deepseekmath} & 序列/最终指标 & 低（无评论家） & 大幅减少GPU内存；实现简单 \\
\textbf{PPO}~\cite{schulman2017proximal} & Step-by-step (GAE) & High (critic needed) & Fine-grained credit assignment; stable in noisy envs \\
\textbf{PPO}~\cite{schulman2017proximal} & 逐步（GAE） & 高（需要评论家） & 细粒度信用分配；在噪声环境中稳定 \\
\textbf{Iterative STaR}~\cite{zelikman2022star} & Sparse (filtered binary) & Minimal (SFT only) & Simple to scale; avoids RL optimization instability \\
\textbf{迭代STaR}~\cite{zelikman2022star} & 稀疏（过滤后的二元） & 极小（仅SFT） & 易于扩展；避免RL优化不稳定 \\
\textbf{RWML}~\cite{yu2026rwml} & Dense (predictive) & Medium & Mitigates reward hacking via world modeling \\
\textbf{RWML}~\cite{yu2026rwml} & 密集（预测性） & 中等 & 通过世界建模缓解奖励黑客攻击 \\
\textbf{LATS}~\cite{zhou2024lats} & Backpropagated & High (tree expansion) & Best quality per task; scales with inference compute \\
\textbf{LATS}~\cite{zhou2024lats} & 反向传播 & 高（树扩展） & 每任务质量最佳；随推理计算扩展 \\
\bottomrule
\end{tabular}
\end{table}


\part{Reasoning}
\part{推理}
```