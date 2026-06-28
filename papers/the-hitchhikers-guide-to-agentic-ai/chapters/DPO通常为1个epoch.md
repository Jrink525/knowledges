                                  # DPO 通常为 1 个 epoch
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
)


dpo_trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=dpo_config,
    train_dataset=dataset,
    tokenizer=tokenizer,
)
dpo_trainer.train()
\end{lstlisting}

## MoE Considerations for RL Training
## 强化学习训练中的 MoE 注意事项

\begin{intuitionbox}[MoE for RLHF]
\begin{intuitionbox}[用于 RLHF 的 MoE]
Mixture-of-Experts (MoE) models~\cite{fedus2022switch} are increasingly used in RLHF:
混合专家（MoE）模型~\cite{fedus2022switch} 在 RLHF 中使用日益增多：

\begin{itemize}
  \item \textbf{Advantage}: 3--4$\times$ more capacity at same compute cost. Better for reward models (more capacity to judge).
  \item \textbf{优势}：在相同计算成本下容量提升 3-4 倍。更适合奖励模型（有更多容量进行判断）。
  \item \textbf{Challenge}: Expert parallelism requires all-to-all communication (tokens routed across GPUs). This conflicts with pipeline parallelism.
  \item \textbf{挑战}：专家并行需要全对全通信（令牌跨 GPU 路由）。这与流水线并行冲突。
  \item \textbf{GRPO with MoE}: Works well since generation cost is dominated by active params (not total params).
  \item \textbf{结合 MoE 的 GRPO}：效果良好，因为生成成本由活跃参数（而非总参数）主导。
  \item \textbf{LoRA for MoE}: Can apply LoRA to router + shared layers only, or to all experts (expensive).
  \item \textbf{面向 MoE 的 LoRA}：可以仅对路由器+共享层应用 LoRA，或对所有专家应用（代价昂贵）。
\end{itemize}
\end{intuitionbox}

\begin{intuitionbox}[The RL Optimizer Mantra]
\begin{intuitionbox}[RL 优化器口诀]
For RL fine-tuning: \textbf{small LR, no weight decay, constant schedule, FP32 master weights, aggressive clipping}. Let the KL penalty handle regularization---the optimizer’s job is just to follow the policy gradient without overshooting.
对于强化学习微调：\textbf{小学习率，无权重衰减，恒定调度，FP32 主权重，激进裁剪}。让 KL 惩罚处理正则化——优化器的工作仅仅是跟随策略梯度而不越界。
\end{intuitionbox}
---

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
