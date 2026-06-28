\chapter{RL for Large Reasoning Models}
\label{sec:rl_reasoning}
\chapter{面向大型推理模型的强化学习}
\label{sec:rl_reasoning}

The emergence of large reasoning models represents one of the most significant developments in modern AI. Unlike standard language model training, which optimizes for next-token prediction, reasoning-focused RL teaches models to \emph{think before answering}---allocating additional computation at inference time to explore, verify, and refine intermediate steps. This section provides a comprehensive technical treatment of the methods, architectures, and scaling laws that underpin this paradigm.
大型推理模型的出现是现代人工智能最重要的进展之一。与优化下一个词元预测的标准语言模型训练不同，聚焦推理的强化学习教会模型在回答之前先思考——在推理时分配额外的计算资源来探索、验证和优化中间步骤。本节将全面、技术性地介绍支撑这一范式的方法、架构和缩放定律。

\section{Motivation and Background}
\label{subsec:reasoning_motivation}
\section{动机与背景}
\label{subsec:reasoning_motivation}

\subsection{Why Reasoning Requires Different RL Approaches}
\label{why-reasoning-requires-different-rl-approaches}
\subsection{为何推理需要不同的强化学习方法}
\label{why-reasoning-requires-different-rl-approaches}

Standard RLHF (Section~\ref{the-rlhf-pipeline}) optimizes a single scalar reward over a complete response. For tasks requiring multi-step reasoning---mathematics, formal verification, competitive programming, scientific derivation---this formulation is insufficient for several reasons:
标准的强化学习人类反馈（RLHF，第~\ref{the-rlhf-pipeline}节）优化的是完整响应上的单一标量奖励。对于需要多步推理的任务——数学、形式化验证、竞赛编程、科学推导——这种形式化因以下几个原因而不够充分：

\begin{itemize}
  \item \textbf{Sparse rewards}: A math problem may require 20 intermediate steps; a single outcome reward provides no gradient signal for the intermediate steps that led to an error.
  \item \textbf{Long horizons}: Reasoning chains can span hundreds to thousands of tokens, creating severe credit assignment problems.
  \item \textbf{Combinatorial search}: The space of valid reasoning paths is exponentially large; the model must learn to search this space efficiently.
  \item \textbf{Verifiability}: Unlike subjective text quality, mathematical and logical correctness is objectively verifiable, enabling automated reward computation without human annotation.
\end{itemize}
\begin{itemize}
  \item \textbf{稀疏奖励}：一个数学问题可能需要20个中间步骤；单一结果奖励无法为导致错误的中间步骤提供梯度信号。
  \item \textbf{长程推理}：推理链可能跨越数百甚至数千个词元，造成严重的信用分配问题。
  \item \textbf{组合搜索}：有效推理路径的空间呈指数级增长；模型必须学会高效地搜索这一空间。
  \item \textbf{可验证性}：与主观的文本质量不同，数学和逻辑正确性是可客观验证的，从而无需人工标注即可自动计算奖励。
\end{itemize}

\begin{keybox}[Key Insight: Reasoning as a Search Problem]
Multi-step reasoning can be framed as a \textbf{search problem} over a tree of partial solutions. Each node in the tree is a reasoning state (prefix of the chain-of-thought), each edge is a reasoning step (a token or sentence), and the leaves are final answers. RL for reasoning teaches the model to navigate this tree efficiently---exploring promising branches, backtracking from dead ends, and allocating compute where it matters most.
\begin{keybox}[核心洞察：推理作为搜索问题]
多步推理可以归结为在部分解树上进行的\textbf{搜索问题}。树中的每个节点都是一个推理状态（思维链的前缀），每条边是一个推理步骤（一个词元或句子），叶子节点则是最终答案。基于推理的强化学习教会模型高效地遍历这棵树——探索有希望的枝干，从死胡同回溯，并将计算资源分配给最需要的地方。
\end{keybox}

\subsection{Chain-of-Thought: Emergent Behavior vs.~Trained Capability}
\label{chain-of-thought-emergent-behavior-vs.-trained-capability}
\subsection{思维链：涌现行为 vs. 训练能力}
\label{chain-of-thought-emergent-behavior-vs.-trained-capability}

Chain-of-thought (CoT) reasoning was first observed as an \emph{emergent} capability in sufficiently large language models~\cite{wei2022chain}: when prompted with step-by-step examples, large models (typically $\geq$100B parameters) spontaneously produced intermediate reasoning steps that improved accuracy. This raised a fundamental question: is CoT an emergent property of scale, or can it be explicitly trained?
思维链（CoT）推理最初是在足够大的语言模型中被观察为一种\emph{涌现}能力~\cite{wei2022chain}：当给出逐步示例时，大型模型（通常 $\geq$100B 参数）会自发产生中间推理步骤，从而提高准确率。这引出了一个根本性问题：思维链是规模带来的涌现属性，还是可以被显式训练出来？

The answer, as demonstrated by DeepSeek-R1 and related work, is \textbf{both}---but with important nuances:
正如 DeepSeek-R1 及相关工作所证明的那样，答案是\textbf{两者兼有}——但存在重要的细微差别：

\begin{itemize}
  \item \textbf{Emergent CoT} arises from in-context learning and requires large base models. It is brittle, prompt-sensitive, and does not generalize robustly.
  \item \textbf{Trained CoT} via RL produces models that \emph{intrinsically} generate reasoning chains as part of their generation process, independent of prompting style. These chains are longer, more exploratory, and exhibit qualitatively different behaviors (self-correction, backtracking, verification).
\end{itemize}
\begin{itemize}
  \item \textbf{涌现式思维链}源于上下文学习，并且需要大型基础模型。它脆弱、对提示敏感，且不能鲁棒地泛化。
  \item \textbf{通过强化学习训练的思维链}所生成的模型会\emph{内在地}将推理链作为其生成过程的一部分，与提示风格无关。这些推理链更长、更具探索性，并展现出质量上不同的行为（自我纠正、回溯、验证）。
\end{itemize}

\begin{intuitionbox}[The ``Aha Moment'' Phenomenon (DeepSeek-AI et al. 2025)]
During RL training of reasoning models, researchers at DeepSeek observed a striking emergent behavior: at a certain point in training, models spontaneously began to \emph{reconsider} their initial approaches mid-chain, using phrases like ``Wait, let me reconsider\ldots{}'' or ``Actually, I think I made an error\ldots{}''. This self-correction behavior---which was \emph{not} explicitly trained---emerged purely from the RL objective of maximizing final-answer accuracy. It suggests that RL can discover meta-cognitive strategies that are instrumentally useful for solving hard problems.
\begin{intuitionbox}[“顿悟时刻”现象 (DeepSeek-AI 等, 2025)]
在推理模型的强化学习训练过程中，DeepSeek 的研究人员观察到一种引人注目的涌现行为：在训练的某个时间点，模型自发地在推理链中途开始\emph{重新考虑}其初始方法，使用诸如“等等，让我重新考虑……”或“实际上，我认为我犯了一个错误……”之类的短语。这种自我纠正行为——\emph{并非}显式训练的——纯粹是从最大化最终答案准确率的强化学习目标中涌现出来的。这表明强化学习能够发现对解决难题有工具性价值的元认知策略。
\end{intuitionbox}

\subsection{Test-Time Compute Scaling Laws}
\label{test-time-compute-scaling-laws}
\subsection{测试时计算缩放定律}
\label{test-time-compute-scaling-laws}

A central empirical finding motivating reasoning model research is that \textbf{test-time compute scales predictably with performance}. Let $C_{\text{train}}$ denote training compute (FLOPs) and $C_{\text{test}}$ denote inference compute (tokens generated). The key observation is:
一个激励推理模型研究的核心经验发现是：\textbf{测试时计算量随性能可预测地缩放}。令 $C_{\text{train}}$ 表示训练计算量（FLOPs），$C_{\text{test}}$ 表示推理计算量（生成的词元数）。关键观察是：

\begin{equation}
    \text{Accuracy}(C_{\text{train}}, C_{\text{test}}) \approx f\!\left(\alpha \log C_{\text{train}} + \beta \log C_{\text{test}}\right)
\end{equation}
\begin{equation}
    \text{准确率}(C_{\text{train}}, C_{\text{test}}) \approx f\!\left(\alpha \log C_{\text{train}} + \beta \log C_{\text{test}}\right)
\end{equation}

for some monotone function $f$ and constants $\alpha, \beta > 0$. This implies that a smaller model with more inference compute can match a larger model with less inference compute---a fundamental shift in the compute-performance tradeoff.
其中 $f$ 是某个单调函数，$\alpha, \beta > 0$ 为常数。这意味着一个较小的模型若拥有更多推理计算量，可以匹配一个较大模型但推理计算量较少的情况——这是计算-性能权衡中的根本性转变。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_044_test_time_scaling.png}
\caption{Schematic test-time compute scaling curves. Performance improves log-linearly with inference tokens across model sizes, and smaller models with more compute can approach larger models with less compute.}
\label{fig:test_time_scaling}
\end{figure}
\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_044_test_time_scaling.png}
\caption{测试时计算缩放曲线示意图。对于不同模型大小，性能随推理词元数呈对数线性提升；较小的模型使用更多计算量可以接近较大模型使用较少计算量的表现。}
\label{fig:test_time_scaling}
\end{figure}

The practical implication is profound: \textbf{reasoning models trade training compute for inference compute}. Rather than always deploying the largest possible model, one can deploy a smaller, reasoning-capable model and allocate more tokens to ``thinking'' on hard problems.
这一实际含义是深远的：\textbf{推理模型用训练计算量换取推理计算量}。与其总是部署尽可能大的模型，不如部署一个较小的、具备推理能力的模型，并在难题上分配更多词元用于“思考”。

\section{Test-Time Scaling Methods}
\label{sec:test_time_methods}
\section{测试时缩放方法}
\label{sec:test_time_methods}

The scaling laws above show that investing more compute at inference can dramatically improve reasoning performance. This section provides a comprehensive treatment of the \textbf{methods} that operationalize test-time scaling --- from simple chain-of-thought to sophisticated tree and graph search algorithms. These methods form a spectrum trading inference cost for accuracy, and understanding their structure is essential for designing modern reasoning systems.
上述缩放定律表明，在推理时投入更多计算可以显著提升推理性能。本节将全面介绍使测试时缩放可操作的\textbf{方法}——从简单的思维链到复杂的树搜索和图搜索算法。这些方法构成了一个以推理成本换取准确率的光谱，理解其结构对于设计现代推理系统至关重要。

\begin{figure}[ht!]
\centering
\includegraphics[width=\textwidth]{figures/fig_045_test_time_spectrum.png}
\caption{Spectrum of test-time scaling methods. Each method trades additional inference compute for improved reasoning accuracy. Methods build on each other conceptually: CoT introduces explicit reasoning, Self-Consistency adds sampling, ToT adds structured search, GoT adds merging operations, and MCTS adds learned value guidance.}
\label{fig:test_time_spectrum}
\end{figure}
\begin{figure}[ht!]
\centering
\includegraphics[width=\textwidth]{figures/fig_045_test_time_spectrum.png}
\caption{测试时缩放方法的光谱。每种方法以额外的推理计算换取更高的推理准确率。这些方法在概念上层层递进：思维链引入显式推理，自一致性增加采样，思维树增加结构化搜索，思维图增加合并操作，蒙特卡洛树搜索增加学到的价值指导。}
\label{fig:test_time_spectrum}
\end{figure}

\subsection{Chain-of-Thought (CoT)}
\label{subsec:cot_method}
\subsection{思维链 (CoT)}
\label{subsec:cot_method}

Chain-of-Thought prompting~\cite{wei2022chain} is the foundation of all test-time scaling methods. Rather than directly outputting an answer, the model generates intermediate reasoning steps that decompose complex problems into manageable sub-problems.
思维链提示~\cite{wei2022chain} 是所有测试时缩放方法的基础。模型不是直接输出答案，而是生成中间推理步骤，将复杂问题分解为可管理的子问题。

\paragraph{Zero-Shot CoT.}
\label{zero-shot-cot.}
\paragraph{零样本思维链。}
\label{zero-shot-cot.}

Kojima et al.~\cite{kojima2022large} demonstrated that appending ``Let’s think step by step'' to a prompt elicits reasoning behavior without any exemplars. This simple trigger activates latent reasoning capabilities in sufficiently large models ($\geq$100B parameters).
Kojima 等人~\cite{kojima2022large} 证明，在提示后附加“让我们一步一步思考”可以在没有任何示例的情况下引发推理行为。这个简单的触发词激活了足够大模型（$\geq$100B 参数）中的潜在推理能力。

\paragraph{Few-Shot CoT.}
\label{few-shot-cot.}
\paragraph{少样本思维链。}
\label{few-shot-cot.}

Wei et al.~\cite{wei2022chain} showed that providing a few exemplars with explicit reasoning traces enables smaller models to reason effectively: 
\begin{equation}
\text{Prompt} = [(x_1, z_1, y_1), (x_2, z_2, y_2), \ldots, (x_k, z_k, y_k), (x_{\text{test}}, \texttt{?})]
\end{equation}
 where $z_i$ are hand-written reasoning traces for exemplar $(x_i, y_i)$.
Wei 等人~\cite{wei2022chain} 表明，提供几个带有显式推理痕迹的示例可以使较小的模型有效推理：
\begin{equation}
\text{提示} = [(x_1, z_1, y_1), (x_2, z_2, y_2), \ldots, (x_k, z_k, y_k), (x_{\text{test}}, \texttt{?})]
\end{equation}
其中 $z_i$ 是示例 $(x_i, y_i)$ 的手写推理痕迹。

\paragraph{Formal characterization.}
\label{formal-characterization.}
\paragraph{形式化描述。}
\label{formal-characterization.}

## CoT converts a single-step prediction $p(y|x)$ into a multi-step sequential generation: 
## CoT 将单步预测 $p(y|x)$ 转换为多步顺序生成：

\begin{equation}
p(y|x) = \sum_{z} p(y|x, z) \cdot p(z|x) \approx p(y|x, z^*) \cdot p(z^*|x)
\end{equation}
 where $z^* = (z_1, z_2, \ldots, z_T)$ is the greedy reasoning chain. The summation over all possible chains is intractable; standard CoT uses a single sample (greedy or temperature sampling).
其中 $z^* = (z_1, z_2, \ldots, z_T)$ 是贪婪推理链。对所有可能链的求和难以处理；标准 CoT 使用单个样本（贪婪采样或温度采样）。

\paragraph{Limitations.}
\paragraph{局限性。}

\label{limitations.}
\label{limitations.}

Single-chain CoT is fragile: if an early reasoning step is wrong, all subsequent steps build on a flawed foundation with no mechanism for recovery.
单链 CoT 很脆弱：如果早期推理步骤出错，后续所有步骤都建立在有缺陷的基础上，且无法恢复。

\subsection{Self-Consistency (Majority Voting)}
\subsection{自一致性（多数投票）}

\label{self-consistency-majority-voting}
\label{self-consistency-majority-voting}

Self-Consistency~\cite{wang2023selfconsistency} addresses CoT’s single-chain fragility by sampling \textbf{multiple independent reasoning chains} and taking a majority vote over the final answers: 
自一致性（Self-Consistency）~\cite{wang2023selfconsistency} 通过采样 \textbf{多个独立推理链} 并对最终答案进行多数投票来解决 CoT 的单链脆弱性：

\begin{equation}
\hat{y} = \arg\max_{y} \sum_{i=1}^{N} \mathbf{1}[y_i = y], \quad \text{where } (z_i, y_i) \sim p(\cdot | x), \; T > 0
\end{equation}

\textbf{Key properties}:
\textbf{关键特性}：

\begin{itemize}
  \item Uses temperature $T > 0$ sampling to generate diverse chains (typically $T = 0.7$--$1.0$)
  \item 使用温度 $T > 0$ 采样生成多样化的链（通常 $T = 0.7$--$1.0$）
  \item No interaction between chains --- fully parallelizable
  \item 链之间无交互 --- 完全可并行化
  \item Accuracy improves monotonically with $N$ (diminishing returns after $N \approx 40$)
  \item 准确率随 $N$ 单调提升（$N \approx 40$ 后收益递减）
  \item On GSM8K: CoT = 56.5\%, Self-Consistency ($N$=40) = 74.4\% (with PaLM-540B~\cite{chowdhery2022palm})
  \item 在 GSM8K 上：CoT = 56.5\%，自一致性（$N$=40）= 74.4\%（使用 PaLM-540B~\cite{chowdhery2022palm}）
  \item Equivalent to \textbf{Best-of-N with outcome reward} (majority vote acts as implicit ORM)
  \item 等价于 \textbf{带结果奖励的 Best-of-N}（多数投票充当隐式 ORM）
\end{itemize}

\begin{intuitionbox}[Why Majority Voting Works]
\begin{intuitionbox}[为什么多数投票有效]

If the model has probability $p > 0.5$ of generating a correct reasoning chain, then by the law of large numbers, majority voting over $N$ independent samples approaches 100\% accuracy as $N \to \infty$. Even with $p = 0.3$ (model is usually wrong), if correct answers concentrate on one value while incorrect answers are diverse, majority voting still recovers the correct answer. This is the statistical foundation of test-time scaling.
如果模型生成正确推理链的概率 $p > 0.5$，那么根据大数定律，对 $N$ 个独立样本进行多数投票，当 $N \to \infty$ 时准确率趋近 100\%。即使 $p = 0.3$（模型通常错误），如果正确答案集中在一个值上而错误答案多样化，多数投票仍能恢复正确答案。这是测试时扩展（test-time scaling）的统计基础。
\end{intuitionbox}
\end{intuitionbox}

\subsection{Tree-of-Thoughts (ToT)}
\subsection{思维树（ToT）}

\label{subsec:tot_method}
\label{subsec:tot_method}

Tree-of-Thoughts~\cite{yao2024tree} generalizes CoT from a \textbf{linear chain} to a \textbf{tree structure}, enabling the model to explore multiple reasoning paths, evaluate intermediate states, and backtrack from unpromising branches. This introduces deliberate planning into the reasoning process.
思维树（Tree-of-Thoughts，ToT）~\cite{yao2024tree} 将 CoT 从 \textbf{线性链} 推广到 \textbf{树结构}，使模型能够探索多条推理路径、评估中间状态，并从没有前景的分支中回溯。这为推理过程引入了有意识的规划。

\paragraph{Core Abstraction.}
\paragraph{核心抽象。}

\label{core-abstraction.}
\label{core-abstraction.}

A reasoning problem is decomposed into a search over a tree where:
一个推理问题被分解为对一棵树的搜索，其中：

\begin{itemize}
  \item \textbf{Root}: Initial problem statement $x$
  \item \textbf{根节点}：初始问题陈述 $x$
  \item \textbf{Nodes}: Partial reasoning states $s = (x, z_1, \ldots, z_k)$
  \item \textbf{节点}：部分推理状态 $s = (x, z_1, \ldots, z_k)$
  \item \textbf{Edges}: Individual reasoning steps (``thoughts'') $z_{k+1}$
  \item \textbf{边}：单个推理步骤（“思维”）$z_{k+1}$
  \item \textbf{Leaves}: Complete solutions with final answers
  \item \textbf{叶子节点}：包含最终答案的完整解
  \item \textbf{Value function}: $V(s)$ estimates how promising a partial solution is
  \item \textbf{价值函数}：$V(s)$ 估计部分解的前景
\end{itemize}

\paragraph{Formal Definition.}
\paragraph{形式化定义。}

\label{formal-definition.}
\label{formal-definition.}

\begin{equation}
\text{ToT} = (\mathcal{G}, \mathcal{E}, V, \pi_\theta, \text{Search})
\end{equation}
 where:
其中：

\begin{itemize}
  \item $\mathcal{G}$: \textbf{Thought generator} --- produces $b$ candidate next thoughts: $\{z^{(1)}, \ldots, z^{(b)}\} \sim \pi_\theta(\cdot | s)$
  \item $\mathcal{G}$：\textbf{思维生成器} --- 生成 $b$ 个候选下一步思维：$\{z^{(1)}, \ldots, z^{(b)}\} \sim \pi_\theta(\cdot | s)$
  \item $\mathcal{E}$: \textbf{State evaluator} --- scores partial solutions: $V(s) \in \{$\emph{sure}, \emph{maybe}, \emph{impossible}$\}$ or $V(s) \in [0, 1]$
  \item $\mathcal{E}$：\textbf{状态评估器} --- 对部分解打分：$V(s) \in \{$\emph{确定}, \emph{可能}, \emph{不可能}$\}$ 或 $V(s) \in [0, 1]$
  \item $\pi_\theta$: The language model generating thoughts
  \item $\pi_\theta$：生成思维的语言模型
  \item $\text{Search}$: Search algorithm (BFS or DFS)
  \item $\text{Search}$：搜索算法（BFS 或 DFS）
\end{itemize}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_046_tot_example.png}
\caption{Tree-of-Thoughts on the ``Game of 24'' task: use operations on {4, 9, 10, 13} to make 24. At each level, the model generates $b=3$ candidate thoughts, evaluates each (sure/maybe/impossible), prunes unpromising branches, and expands the most promising ones. The green path leads to a solution; red paths are pruned early.}
\caption{在“24 点游戏”任务上的思维树：对 {4, 9, 10, 13} 使用运算得到 24。在每一层，模型生成 $b=3$ 个候选思维，评估每个（确定/可能/不可能），剪去没有前景的分支，并扩展最有前景的分支。绿色路径通向解；红色路径被提前剪枝。}
\end{figure}

\paragraph{Search Algorithms.}
\paragraph{搜索算法。}

\label{search-algorithms.}
\label{search-algorithms.}

\textbf{BFS (Breadth-First Search):}
\textbf{广度优先搜索（BFS）：}

\begin{enumerate}
  \item Generate $b$ candidate thoughts for each node at current depth
  \item 为当前深度的每个节点生成 $b$ 个候选思维
  \item Evaluate all candidates with $V(\cdot)$
  \item 用 $V(\cdot)$ 评估所有候选
  \item Keep top-$k$ most promising states (beam search)
  \item 保留 top-$k$ 个最有前景的状态（束搜索）
  \item Advance all $k$ states to the next level
  \item 将所有 $k$ 个状态推进到下一层
  \item Repeat until a solution is found or depth limit reached
  \item 重复直到找到解或达到深度限制
\end{enumerate}

\textbf{DFS (Depth-First Search):}
\textbf{深度优先搜索（DFS）：}

\begin{enumerate}
  \item Generate $b$ candidate thoughts for current state
  \item 为当前状态生成 $b$ 个候选思维
  \item Evaluate: if $V(s) =$ \emph{impossible}, backtrack immediately
  \item 评估：如果 $V(s) =$ \emph{不可能}，立即回溯
  \item If $V(s) =$ \emph{sure/maybe}, recurse deeper (pick the most promising)
  \item 如果 $V(s) =$ \emph{确定/可能}，更深递归（选择最有前景的）
  \item If depth limit reached without solution, backtrack
  \item 如果达到深度限制仍未找到解，回溯
  \item Continue until solution found or all branches explored
  \item 继续直到找到解或探索完所有分支
\end{enumerate}

\begin{examplebox}[ToT: Value Evaluation Prompt]
\begin{examplebox}[ToT：价值评估提示]

\begin{lstlisting}[style=pythonstyle]
# The LLM evaluates partial reasoning states:
EVAL_PROMPT = """Evaluate if this partial solution can reach 24.


Numbers remaining: [4, 4, 10]
Steps so far: 13 - 9 = 4


Can these remaining numbers (4, 4, 10) be combined using +,-,*,/
to make 24?


Analysis: 4 * (10 - 4) = 4 * 6 = 24. Yes!


Judge: sure/maybe/impossible
Answer: sure"""


# Thought generation prompt:
GEN_PROMPT = """Input: 4 9 10 13
Possible next steps:
1. 13 - 9 = 4 (left: 4 4 10)
2. 10 + 13 = 23 (left: 4 9 23)
3. 9 - 4 = 5 (left: 5 10 13)
..."""
\end{lstlisting}
\end{examplebox}
\end{examplebox}

\paragraph{Computational Cost.}
\paragraph{计算成本。}

\label{computational-cost.}
\label{computational-cost.}

For ToT with branching factor $b$, depth $d$, and beam width $k$: 
对于分支因子 $b$、深度 $d$ 和束宽 $k$ 的 ToT：

\begin{equation}
\text{LLM calls (BFS)} = \underbrace{k \cdot b}_{\text{generation}} + \underbrace{k \cdot b}_{\text{evaluation}} = 2kb \text{ per level} \implies \text{Total} = 2kbd
\end{equation}
 For the 24 game: $b=3, k=2, d=3 \implies 36$ LLM calls vs.~1 for standard CoT.
对于 24 点游戏：$b=3, k=2, d=3 \implies 36$ 次 LLM 调用，而标准 CoT 为 1 次。

\paragraph{Results.}
\paragraph{结果。}

\label{results.}
\label{results.}

On the Game of 24 (a challenging arithmetic reasoning task), ToT achieves 74\% success rate vs.~CoT’s 4\% --- a massive improvement from structured search over the same base model (GPT-4).
在 24 点游戏（一项具有挑战性的算术推理任务）上，ToT 达到 74\% 的成功率，而 CoT 为 4\% —— 相比同一基础模型（GPT-4），结构化搜索带来了巨大提升。

\subsection{Graph-of-Thoughts (GoT)}
\subsection{思维图（GoT）}

\label{subsec:got_method}
\label{subsec:got_method}

Graph-of-Thoughts~\cite{besta2024graph} extends ToT from a tree to a \textbf{directed acyclic graph (DAG)}, introducing a critical capability: \textbf{merging} partial solutions from different branches. This allows the model to synthesize insights from multiple reasoning paths into a single refined solution.
思维图（Graph-of-Thoughts，GoT）~\cite{besta2024graph} 将 ToT 从树扩展到 \textbf{有向无环图（DAG）}，引入了一个关键能力：\textbf{合并}来自不同分支的部分解。这使得模型能够将来自多条推理路径的见解综合成一个精炼的解。

\paragraph{Key Operations.}
\paragraph{关键操作。}

\label{key-operations.}
\label{key-operations.}

GoT introduces three operations beyond ToT:
GoT 在 ToT 的基础上引入了三种操作：

\begin{itemize}
  \item \textbf{Generate}: Produce new thoughts from a state (same as ToT)
  \item \textbf{生成}：从状态产生新思维（与 ToT 相同）
  \item \textbf{Aggregate/Merge}: Combine multiple thoughts into one refined thought --- this is impossible in a tree
  \item \textbf{聚合/合并}：将多个思维组合成一个精炼的思维 --- 这在树中是不可能的
  \item \textbf{Refine}: Iteratively improve a thought based on feedback
  \item \textbf{精炼}：基于反馈迭代改进一个思维
  \item \textbf{Score}: Evaluate thought quality (same as ToT’s value function)
  \item \textbf{评分}：评估思维质量（与 ToT 的价值函数相同）
\end{itemize}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_047_got_comparison.png}
\caption{Comparison of CoT (linear chain), ToT (tree --- branches but no merging), and GoT (DAG --- branches can merge). For a sorting task, GoT can split the array into sub-problems, solve them independently (parallel), then \textbf{merge} the results --- impossible in a pure tree structure. This enables divide-and-conquer reasoning.}
\caption{CoT（线性链）、ToT（树——有分支但无合并）和 GoT（DAG——分支可以合并）的比较。对于排序任务，GoT 可以将数组拆分为子问题，独立求解（并行），然后 \textbf{合并} 结果——这在纯树结构中是不可能的。这实现了分治推理。}
\label{fig:got_comparison}
\end{figure}

\paragraph{Graph Operations (formal).}
\paragraph{图操作（形式化）。}

\label{graph-operations-formal.}
\label{graph-operations-formal.}

## 原文标题（无）
## 中文标题（无）

Let $\mathcal{V} = \{v_1, \ldots, v_n\}$ be thought vertices and $\mathcal{E} \subseteq \mathcal{V} \times \mathcal{V}$ be directed edges. GoT supports: 
设 $\mathcal{V} = \{v_1, \ldots, v_n\}$ 为思维顶点，$\mathcal{E} \subseteq \mathcal{V} \times \mathcal{V}$ 为有向边。GoT（思维图）支持：
\begin{align}
\textbf{Generate}(v) &: v \to \{v_{c_1}, \ldots, v_{c_b}\} && \text{(create children)} \\
\textbf{Aggregate}(v_1, \ldots, v_k) &\to v_{\text{merged}} && \text{(merge $k$ thoughts into one)} \\
\textbf{Refine}(v, n) &\to v' && \text{(improve $v$ through $n$ iterations)} \\
\textbf{Score}(v) &\to s \in [0, 1] && \text{(evaluate thought quality)}
\end{align}

\begin{align}
\textbf{Generate}(v) &: v \to \{v_{c_1}, \ldots, v_{c_b}\} && \text{(创建子节点)} \\
\textbf{Aggregate}(v_1, \ldots, v_k) &\to v_{\text{merged}} && \text{(合并 $k$ 个想法为一个)} \\
\textbf{Refine}(v, n) &\to v' && \text{(通过 $n$ 次迭代改进 $v$)} \\
\textbf{Score}(v) &\to s \in [0, 1] && \text{(评估想法质量)}
\end{align}

The \textbf{Aggregate} operation is the key differentiator: it creates edges from multiple parent nodes to a single child, forming a DAG rather than a tree. This enables:
\textbf{Aggregate}（聚合）操作是关键区别：它从多个父节点创建到单个子节点的边，形成有向无环图（DAG）而非树。这带来了：

\begin{itemize}
  \item \textbf{Divide-and-conquer}: Split problem $\to$ solve sub-problems in parallel $\to$ merge solutions
  \item \textbf{Ensemble reasoning}: Generate multiple perspectives, then synthesize the best ideas
  \item \textbf{Iterative refinement}: Feed evaluation results back to improve earlier thoughts
\end{itemize}

\begin{itemize}
  \item \textbf{分治（Divide-and-conquer）}：拆分问题 $\to$ 并行求解子问题 $\to$ 合并解决方案
  \item \textbf{集成推理（Ensemble reasoning）}：生成多个视角，然后综合最佳想法
  \item \textbf{迭代优化（Iterative refinement）}：将评估结果反馈以改进早期想法
\end{itemize}

\paragraph{Results.}
\label{results.-1}

\paragraph{结果。}
\label{results.-1}

On sorting (a task requiring merging), GoT achieves 62\% cost reduction vs.~ToT at equivalent quality. On set intersection and keyword counting, GoT matches ToT quality with 30--40\% fewer LLM calls due to the merge operation enabling more efficient decomposition.
在排序（需要合并的任务）上，GoT 在同等质量下相比 ToT（思维树）实现了 62\% 的成本降低。在集合交集和关键词计数上，GoT 以 30--40\% 更少的 LLM 调用达到与 ToT 相同的质量，这得益于合并操作实现了更高效的分解。

\subsection{Best-of-N with Reward Models}
\label{subsec:bon_method}

## Best-of-N with Reward Models
## 带奖励模型的 Best-of-N

Best-of-N (BoN)~\cite{nakano2021webgpt, stiennon2020learning} is the simplest scaling method that uses a \textbf{learned reward model} to select among candidates: 
Best-of-N（BoN）~\cite{nakano2021webgpt, stiennon2020learning} 是最简单的扩展方法，它使用一个 \textbf{学习到的奖励模型（learned reward model）} 来从候选解中选择：
\begin{equation}
y^* = \arg\max_{y \in \{y_1, \ldots, y_N\}} R_\phi(x, y), \quad y_i \sim \pi_\theta(\cdot | x)
\end{equation}

\textbf{Variants by reward model type}:
\textbf{按奖励模型类型的变体}：

\begin{itemize}
  \item \textbf{BoN with ORM}: Score complete solutions; select the highest-scoring one. Equivalent to Self-Consistency when ORM $\approx$ correctness check.
  \item \textbf{BoN with PRM}: Score at each reasoning step; select the solution with highest minimum step score (least likely to have an error at any step).
  \item \textbf{Weighted BoN}: Weight candidates by reward: $y^* \sim \text{softmax}(R(y_1)/\tau, \ldots, R(y_N)/\tau)$.
\end{itemize}

\begin{itemize}
  \item \textbf{带 ORM（结果奖励模型）的 BoN}：对完整解决方案打分；选取得分最高的。当 ORM $\approx$ 正确性检查时，等同于自一致性（Self-Consistency）。
  \item \textbf{带 PRM（过程奖励模型）的 BoN}：在每个推理步骤打分；选取最小步骤得分最高的解（即在任何步骤出错可能性最小的解）。
  \item \textbf{加权 BoN（Weighted BoN）}：按奖励对候选解加权：$y^* \sim \text{softmax}(R(y_1)/\tau, \ldots, R(y_N)/\tau)$。
\end{itemize}

\begin{keybox}[BoN Scaling Law]
For a model with per-sample accuracy $p$, the probability of at least one correct sample in $N$ tries: 
\begin{equation}
P(\text{success with BoN}) = 1 - (1-p)^N
\end{equation}
 With a perfect reward model (oracle that always selects correctly):
对于单样本准确率为 $p$ 的模型，在 $N$ 次尝试中至少有一个正确样本的概率为：
\begin{equation}
P(\text{使用 BoN 的成功概率}) = 1 - (1-p)^N
\end{equation}
使用完美奖励模型（始终能正确选择的 oracle）时：
\begin{itemize}
  \item $p = 0.3, N = 10$: success = $97\%$
  \item $p = 0.1, N = 50$: success = $99.5\%$
\end{itemize}
\begin{itemize}
  \item $p = 0.3, N = 10$：成功率 = $97\%$
  \item $p = 0.1, N = 50$：成功率 = $99.5\%$
\end{itemize}

In practice, imperfect reward models cap the effective $N$ --- beyond $N \approx 64$--$256$, reward model errors dominate and accuracy plateaus or decreases (\textbf{reward hacking}).
\end{keybox}

在实际中，不完美的奖励模型限制了有效的 $N$——当 $N \approx 64$--$256$ 之后，奖励模型的误差占主导，准确率趋于平稳或下降（\textbf{奖励黑客（reward hacking）}）。
\end{keybox}

\subsection{Monte Carlo Tree Search (MCTS) for Reasoning}
\label{monte-carlo-tree-search-mcts-for-reasoning}

## Monte Carlo Tree Search (MCTS) for Reasoning
## 蒙特卡洛树搜索（MCTS）用于推理

MCTS~\cite{kocsis2006bandit, silver2016mastering} combines the structured exploration of ToT with \textbf{learned value estimates} and \textbf{visit-count statistics} to allocate inference compute optimally. Originally developed for game-playing (AlphaGo~\cite{silver2016mastering}), MCTS has been adapted for LLM reasoning by systems including AlphaProof~\cite{alphaproof2024} and rStar~\cite{qi2024mutual}.
MCTS~\cite{kocsis2006bandit, silver2016mastering} 将 ToT 的结构化探索与 \textbf{学习到的价值估计（learned value estimates）} 和 \textbf{访问次数统计（visit-count statistics）} 相结合，以最优方式分配推理计算。MCTS 最初为游戏（AlphaGo~\cite{silver2016mastering}）开发，已被 AlphaProof~\cite{alphaproof2024} 和 rStar~\cite{qi2024mutual} 等系统改编用于 LLM 推理。

\paragraph{Algorithm (adapted for LLM reasoning).}
\label{algorithm-adapted-for-llm-reasoning.}

\paragraph{算法（针对 LLM 推理改编）。}
\label{algorithm-adapted-for-llm-reasoning.}

Each MCTS iteration consists of four phases:
每次 MCTS 迭代包含四个阶段：

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_048_mcts_phases.png}
\caption{Four phases of MCTS for reasoning: (1) \textbf{Selection}: traverse tree using UCB to find a promising leaf; (2) \textbf{Expansion}: generate new reasoning steps from the leaf; (3) \textbf{Simulation}: complete the reasoning to a terminal state and evaluate; (4) \textbf{Backpropagation}: update value estimates along the path.}
\label{fig:mcts_phases}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_048_mcts_phases.png}
\caption{MCTS 用于推理的四个阶段：(1) \textbf{选择（Selection）}：使用 UCB 遍历树以找到有前景的叶节点；(2) \textbf{扩展（Expansion）}：从叶节点生成新的推理步骤；(3) \textbf{模拟（Simulation）}：完成推理至终端状态并评估；(4) \textbf{反向传播（Backpropagation）}：沿路径更新价值估计。}
\label{fig:mcts_phases}
\end{figure}

\paragraph{UCB for Reasoning.}
\label{ucb-for-reasoning.}

\paragraph{用于推理的 UCB。}
\label{ucb-for-reasoning.}

Node selection uses PUCT (Predictor + UCB applied to Trees): 
\begin{equation}
a^* = \arg\max_a \left[ Q(s, a) + c_{\text{puct}} \cdot P(s, a) \cdot \frac{\sqrt{\sum_b N(s,b)}}{1 + N(s, a)} \right]
\end{equation}
 where $P(s,a) = \pi_\theta(a|s)$ is the LLM’s prior probability of generating step $a$ from state $s$. This biases exploration toward steps the LLM already considers likely, while the UCB term encourages trying under-explored alternatives.
节点选择使用 PUCT（预测器 + 应用于树的 UCB）：
\begin{equation}
a^* = \arg\max_a \left[ Q(s, a) + c_{\text{puct}} \cdot P(s, a) \cdot \frac{\sqrt{\sum_b N(s,b)}}{1 + N(s, a)} \right]
\end{equation}
其中 $P(s,a) = \pi_\theta(a|s)$ 是 LLM 从状态 $s$ 生成步骤 $a$ 的先验概率。这使探索偏向于 LLM 已经认为可能的步骤，而 UCB 项则鼓励尝试探索不足的替代方案。

\begin{examplebox}[MCTS for Math Reasoning: Running Example]
\textbf{Problem}: Prove that $\sqrt{2}$ is irrational.

\textbf{Iteration 1} (Selection $\to$ root, Expansion):
\begin{itemize}
  \item Generate 3 candidate first steps:
\begin{enumerate}
  \item ``Assume for contradiction that $\sqrt{2} = p/q$ in lowest terms.'' ($P = 0.7$)
  \item ``Consider the decimal expansion of $\sqrt{2}$ = 1.414...'' ($P = 0.15$)
  \item ``Use the fundamental theorem of arithmetic.'' ($P = 0.10$)
\end{enumerate}
  \item Rollout from $z_1$: reaches correct proof in 4 steps $\to$ $r = 1.0$
  \item Rollout from $z_2$: fails (decimal doesn’t prove irrationality) $\to$ $r = 0.0$
  \item Backprop: $Q(s_0, z_1) = 1.0$, $N(s_0, z_1) = 1$
\end{itemize}

\textbf{Iteration 2} (Selection: pick $z_1$ by UCB):
\begin{itemize}
  \item Expand from state ``Assume $\sqrt{2} = p/q$...'':
\begin{enumerate}
  \item ``Then $2 = p^2/q^2$, so $p^2 = 2q^2$.'' ($P = 0.8$)
  \item ``Then $p$ and $q$ share no common factors.'' ($P = 0.15$)
\end{enumerate}
  \item Rollout from $z_4$: correct continuation $\to r = 1.0$
  \item Backprop: $Q(s_0, z_1) = 1.0$, $Q(s_1, z_4) = 1.0$
\end{itemize}

\textbf{After 20 iterations}: The tree has explored 8 distinct reasoning paths. The most-visited path is selected as the final proof: $z_1 \to z_4 \to z_6 \to z_8$ (classical proof by contradiction via even/odd argument).
\end{examplebox}

\begin{examplebox}[MCTS 用于数学推理：运行示例]
\textbf{问题}：证明 $\sqrt{2}$ 是无理数。

\textbf{迭代 1}（选择 $\to$ 根节点，扩展）：
\begin{itemize}
  \item 生成 3 个候选第一步：
\begin{enumerate}
  \item “假设矛盾，$\sqrt{2} = p/q$ 为最简分数。” ($P = 0.7$)
  \item “考虑 $\sqrt{2}$ 的小数展开 = 1.414... ” ($P = 0.15$)
  \item “使用算术基本定理。” ($P = 0.10$)
\end{enumerate}
  \item 从 $z_1$ 推出：4 步到达正确证明 $\to$ $r = 1.0$
  \item 从 $z_2$ 推出：失败（小数不能证明无理数）$\to$ $r = 0.0$
  \item 反向传播：$Q(s_0, z_1) = 1.0$, $N(s_0, z_1) = 1$
\end{itemize}

\textbf{迭代 2}（选择：通过 UCB 选取 $z_1$）：
\begin{itemize}
  \item 从状态“假设 $\sqrt{2} = p/q$...”扩展：
\begin{enumerate}
  \item “那么 $2 = p^2/q^2$，所以 $p^2 = 2q^2$。” ($P = 0.8$)
  \item “那么 $p$ 和 $q$ 没有公因子。” ($P = 0.15$)
\end{enumerate}
  \item 从 $z_4$ 推出：正确延续 $\to r = 1.0$
  \item 反向传播：$Q(s_0, z_1) = 1.0$, $Q(s_1, z_4) = 1.0$
\end{itemize}

\textbf{20 次迭代后}：树已探索了 8 条不同的推理路径。选择访问最多的路径作为最终证明：$z_1 \to z_4 \to z_6 \to z_8$（通过奇偶论证的经典反证法）。
\end{examplebox}

\paragraph{Comparison: ToT vs.~MCTS.}
\label{comparison-tot-vs.-mcts.}

\paragraph{比较：ToT 与 MCTS。}
\label{comparison-tot-vs.-mcts.}

\begin{table}[ht!]
\centering
\caption{Tree-of-Thoughts vs.~Monte Carlo Tree Search for reasoning.}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Dimension} & \textbf{ToT} & \textbf{MCTS} \\
\midrule
Value estimation & LLM prompt (``sure/maybe/impossible'') & Learned value network + rollout statistics \\
Exploration & Fixed beam width; no revisiting & UCB adaptively allocates budget to promising nodes \\
Compute allocation & Uniform across depth levels & Focused: more simulations on harder sub-problems \\
Training integration & No training; pure prompting & Can distill MCTS policy into the base model~\cite{silver2016mastering} \\
Best for & Simple branching problems (24 game) & Complex problems requiring deep exploration (proofs, code) \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[ht!]
\centering
\caption{思维树（Tree-of-Thoughts）与蒙特卡洛树搜索（Monte Carlo Tree Search）用于推理的比较。}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{维度} & \textbf{ToT} & \textbf{MCTS} \\
\midrule
价值估计 & LLM 提示（“确定/可能/不可能”） & 学习到的价值网络 + rollout 统计 \\
探索 & 固定束宽；不重新访问 & UCB 自适应地将预算分配给有前景的节点 \\
计算分配 & 各深度均匀 & 有重点：对更难的子问题进行更多模拟 \\
训练集成 & 无需训练；纯提示 & 可将 MCTS 策略蒸馏到基础模型~\cite{silver2016mastering} \\
最佳场景 & 简单分支问题（24 点游戏） & 需要深度探索的复杂问题（证明、代码） \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Beam Search over Reasoning Steps}
\label{subsec:beam_reasoning}

## Beam Search over Reasoning Steps
## 对推理步骤的束搜索

Beam search --- long standard in NMT and text generation --- can be applied at the \emph{reasoning step} level rather than the token level. Instead of tracking the top-$k$ token sequences, we track the top-$k$ \textbf{reasoning prefixes}:
束搜索（Beam search）——在神经机器翻译（NMT）和文本生成中长期作为标准——可以应用于 \emph{推理步骤} 级别而非词元级别。我们不跟踪 top-$k$ 词元序列，而是跟踪 top-$k$ \textbf{推理前缀（reasoning prefixes）}：

\begin{equation}
\mathcal{B}_d = \text{top-}k\left\{ (s_1, \ldots, s_d) : \sum_{i=1}^d \log \pi_\theta(s_i | s_{<i}) + \lambda \cdot V_\phi(s_1, \ldots, s_d) \right\}
\end{equation}

where the scoring combines the LLM log-probability (fluency) with a value model estimate (correctness). This is effectively ToT-BFS with a learned value function rather than a prompted one.
其中评分结合了 LLM 对数概率（流畅性）与价值模型估计（正确性）。这实际上是带有学习到的价值函数（而非提示式价值函数）的 ToT-BFS（思维树-广度优先搜索）。

\subsection{Iterative Refinement and Self-Correction}
\label{iterative-refinement-and-self-correction}

## Iterative Refinement and Self-Correction
## 迭代优化与自我修正

Rather than exploring \emph{breadth} (multiple parallel chains), iterative refinement invests compute in \emph{ depth} --- repeatedly improving a single solution:
迭代优化不是探索 \emph{广度}（多条并行链），而是将计算投入 \emph{深度}——反复改进单一解：

\begin{equation}
y^{(t+1)} = \text{LLM}\!\left(\text{``Improve this solution:''}, y^{(t)}, \text{``Errors found:''}, e^{(t)}\right)
\end{equation}

where $e^{(t)}$ may come from:
其中 $e^{(t)}$ 可能来自：

\begin{equation}
y^{(t+1)} = \text{LLM}\!\left(\text{“改进这个解：”}, y^{(t)}, \text{“发现的错误：”}, e^{(t)}\right)
\end{equation}

其中 $e^{(t)}$ 可能来自：

\begin{itemize}
  \item \textbf{Self-verification}: Ask the model to check its own answer
  \item \textbf{External verification}: Run code, check math symbolically
  \item \textbf{Critic model}: A separate model identifies errors
\end{itemize}
\begin{itemize}
  \item \textbf{自验证（Self-verification）}：让模型检查自己的答案
  \item \textbf{外部验证（External verification）}：运行代码，符号化检查数学
  \item \textbf{评论家模型（Critic model）}：一个单独的模型识别错误
\end{itemize}

Notable methods: \textbf{Self-Refine}~\cite{madaan2023selfrefine} (iterative self-feedback), \textbf{Reflexion}~\cite{shinn2023reflexion} (verbal RL via reflections stored in memory), and \textbf{LATS}~\cite{zhou2024lats} (tree search + reflection-based pruning).
值得注意的方法：\textbf{Self-Refine}~\cite{madaan2023selfrefine}（迭代自反馈），\textbf{Reflexion}~\cite{shinn2023reflexion}（通过存储在记忆中的反思进行口头强化学习），以及 \textbf{LATS}~\cite{zhou2024lats}（树搜索 + 基于反思的剪枝）。

\subsection{Method Comparison and Selection Guide}
\label{method-comparison-and-selection-guide}
\subsection{方法对比与选择指南}
\label{method-comparison-and-selection-guide}

\begin{table}[ht!]
\centering
\caption{Comprehensive comparison of test-time scaling methods.}
{\footnotesize
\begin{tabular}{@{}llllll@{}}
\toprule
\textbf{Method} & \textbf{Structure} & \textbf{LLM Calls} & \textbf{Parallelizable} & \textbf{Needs RM?} & \textbf{Best For} \\
\midrule
CoT~\cite{wei2022chain} & Chain & 1 & N/A & No & Easy--medium problems \\
Self-Consistency~\cite{wang2023selfconsistency} & Parallel chains & $N$ & \checkmark{} Fully & No (majority vote) & Math with discrete answers \\
Best-of-N + ORM & Parallel chains & $N$ + 1 & \checkmark{} Fully & Yes (ORM) & General tasks with good RM \\
Best-of-N + PRM & Parallel chains & $N$ + $N{\cdot}K$ & \checkmark{} Fully & Yes (PRM) & Complex multi-step reasoning \\
ToT~\cite{yao2024tree} & Tree (BFS/DFS) & $O(kbd)$ & Partial & LLM-as-judge & Structured search problems \\
GoT~\cite{besta2024graph} & DAG & $O(kbd)$ & Partial & LLM-as-judge & Decomposable problems \\
MCTS~\cite{kocsis2006bandit} & Tree + values & $O(N_{\text{sim}} \cdot d)$ & Partial & Yes (value net) & Hard proofs, coding \\
Self-Refine~\cite{madaan2023selfrefine} & Linear (iterative) & $2T$ & No & Self-critic & Open-ended generation \\
LATS~\cite{zhou2024lats} & Tree + reflection & $O(N \cdot d)$ & Partial & LLM-as-judge & Agent tasks \\
\bottomrule
\end{tabular}
}
\end{table}

\begin{table}[ht!]
\centering
\caption{测试时扩展方法的全面对比。}
{\footnotesize
\begin{tabular}{@{}llllll@{}}
\toprule
\textbf{方法} & \textbf{结构} & \textbf{LLM调用次数} & \textbf{可并行化} & \textbf{需要奖励模型？} & \textbf{最适合} \\
\midrule
CoT~\cite{wei2022chain} & 链式 & 1 & 不适用 & 否 & 简单到中等难度问题 \\
Self-Consistency~\cite{wang2023selfconsistency} & 并行链 & $N$ & \checkmark{} 完全 & 否（多数投票） & 有离散答案的数学问题 \\
Best-of-N + ORM & 并行链 & $N$ + 1 & \checkmark{} 完全 & 是（ORM） & 有良好奖励模型的通用任务 \\
Best-of-N + PRM & 并行链 & $N$ + $N{\cdot}K$ & \checkmark{} 完全 & 是（PRM） & 复杂的多步推理 \\
ToT~\cite{yao2024tree} & 树（BFS/DFS） & $O(kbd)$ & 部分 & LLM作为裁判 & 结构化搜索问题 \\
GoT~\cite{besta2024graph} & DAG & $O(kbd)$ & 部分 & LLM作为裁判 & 可分解的问题 \\
MCTS~\cite{kocsis2006bandit} & 树 + 值 & $O(N_{\text{sim}} \cdot d)$ & 部分 & 是（值网络） & 困难证明、代码 \\
Self-Refine~\cite{madaan2023selfrefine} & 线性（迭代） & $2T$ & 否 & 自批判 & 开放式生成 \\
LATS~\cite{zhou2024lats} & 树 + 反思 & $O(N \cdot d)$ & 部分 & LLM作为裁判 & 智能体任务 \\
\bottomrule
\end{tabular}
}
\end{table}

\begin{keybox}[When to Use Which Method]
\begin{itemize}
  \item \textbf{Budget $<$ 5$\times$ base cost}: Use CoT or Self-Consistency. Maximum bang for the buck.
  \item \textbf{Budget 5--50$\times$}: Use Best-of-N with PRM (if you have a good reward model) or ToT-BFS with $b=3, k=2$.
  \item \textbf{Budget 50--500$\times$}: Use MCTS with a trained value function. This is the regime where DeepSeek-R1 and OpenAI o1 operate --- long reasoning chains with implicit tree search.
  \item \textbf{Parallelism required}: Self-Consistency and Best-of-N are fully parallel; ToT/MCTS require sequential depth expansion.
  \item \textbf{No reward model available}: Use Self-Consistency (majority vote) or ToT with LLM-as-judge evaluation.
  \item \textbf{Decomposable problems}: GoT excels when the problem has natural sub-problems (sorting, multi-document synthesis, code with modules).
\end{itemize}
\end{keybox}

\begin{keybox}[何时使用哪种方法]
\begin{itemize}
  \item \textbf{预算 $<$ 5$\times$ 基础成本}：使用 CoT 或 Self-Consistency。性价比最高。
  \item \textbf{预算 5--50$\times$}：使用带有 PRM 的 Best-of-N（如果你有好的奖励模型）或 ToT-BFS，其中 $b=3, k=2$。
  \item \textbf{预算 50--500$\times$}：使用带有训练好的值函数的 MCTS。这是 DeepSeek-R1 和 OpenAI o1 运行的区间——通过隐式树搜索进行长推理链。
  \item \textbf{需要并行化}：Self-Consistency 和 Best-of-N 可完全并行；ToT/MCTS 需要顺序深度扩展。
  \item \textbf{没有可用奖励模型}：使用 Self-Consistency（多数投票）或带 LLM 作为裁判评估的 ToT。
  \item \textbf{可分解的问题}：当问题有自然子问题（排序、多文档合成、带模块的代码）时，GoT 表现出色。
\end{itemize}
\end{keybox}

\begin{intuitionbox}[The Implicit Test-Time Scaling in Reasoning Models]
Modern reasoning models (DeepSeek-R1~\cite{deepseek2025r1}, OpenAI o1/o3~\cite{openai2024o1, openai2025o3}) perform \textbf{implicit test-time scaling} via long chain-of-thought generation. Their ``thinking'' tokens serve a function analogous to MCTS rollouts: the model explores multiple approaches, backtracks (``Wait, let me reconsider...''), verifies intermediate steps, and allocates more tokens to harder sub-problems. The key insight of R1/o1 training is that GRPO/RL teaches the model to perform this implicit search \emph{within a single generation}, eliminating the need for external orchestration (ToT prompts, MCTS infrastructure). The model becomes its own search algorithm.
\end{intuitionbox}

\begin{intuitionbox}[推理模型中的隐式测试时扩展]
现代推理模型（DeepSeek-R1~\cite{deepseek2025r1}，OpenAI o1/o3~\cite{openai2024o1, openai2025o3}）通过长思维链生成执行 \textbf{隐式测试时扩展（implicit test-time scaling）}。它们的“思考”标记起到了类似于 MCTS 展开（rollouts）的作用：模型探索多种方法，回溯（“等等，让我重新考虑...”），验证中间步骤，并将更多标记分配给更难的子问题。R1/o1 训练的关键见解是：GRPO/RL 教会模型\emph{在单次生成内}执行这种隐式搜索，消除了外部编排（ToT 提示、MCTS 基础设施）的需要。模型本身成为了自己的搜索算法。
\end{intuitionbox}

\section{DeepSeek-R1}
\label{subsec:deepseek_r1}
\section{DeepSeek-R1}
\label{subsec:deepseek_r1}

DeepSeek-R1~\cite{deepseek2025r1} is the first fully open-source large reasoning model to match or exceed OpenAI o1 on major benchmarks. Its training pipeline is technically transparent and has become the de facto reference implementation for RL-based reasoning.
DeepSeek-R1~\cite{deepseek2025r1} 是首个完全开源的大型推理模型，在主要基准测试上达到或超过 OpenAI o1。其训练流程在技术上透明，并已成为基于强化学习推理的事实标准参考实现。

\subsection{Two-Stage Training Pipeline}
\label{two-stage-training-pipeline}
\subsection{两阶段训练流程}
\label{two-stage-training-pipeline}

\paragraph{Stage 1: Cold-Start Supervised Fine-Tuning}
\label{stage-1-cold-start-supervised-fine-tuning}
\paragraph{阶段一：冷启动监督微调}
\label{stage-1-cold-start-supervised-fine-tuning}

The base model (DeepSeek-V3) is first fine-tuned on a small, carefully curated dataset of long chain-of-thought examples. This ``cold start'' phase serves two purposes:
基础模型（DeepSeek-V3）首先在一个精心策划的小型长思维链示例数据集上进行微调。这个“冷启动”阶段有两个目的：

\begin{enumerate}
  \item \textbf{Format initialization}: The model learns to produce reasoning in the \texttt{<think>...</think>} format before emitting a final answer.
  \item \textbf{Stability}: Without cold-start SFT, pure RL from scratch on the base model produces unstable training dynamics and degenerate outputs (e.g., language mixing, repetitive loops).
\end{enumerate}
\begin{enumerate}
  \item \textbf{格式初始化}：模型学会在输出最终答案之前，以 \texttt{<think>...</think>} 格式生成推理过程。
  \item \textbf{稳定性}：如果没有冷启动 SFT，直接在基础模型上从头进行纯强化学习会产生不稳定的训练动态和退化的输出（例如语言混用、重复循环）。
\end{enumerate}

The cold-start dataset contains only $\sim$thousands of examples, deliberately kept small to avoid over-constraining the reasoning style that RL will later discover.
冷启动数据集仅包含约数千个示例，故意保持较小规模，以避免过度限制强化学习后续将发现的推理风格。

\paragraph{Stage 2: GRPO-Based Reinforcement Learning}
\label{stage-2-grpo-based-reinforcement-learning}
\paragraph{阶段二：基于 GRPO 的强化学习}
\label{stage-2-grpo-based-reinforcement-learning}

After cold-start SFT, the model undergoes large-scale RL using Group Relative Policy Optimization (GRPO). The full GRPO objective as used in R1 is described in Section~\ref{subsubsec:grpo_r1_math}.
在冷启动 SFT 之后，模型使用组相对策略优化（Group Relative Policy Optimization, GRPO）进行大规模强化学习。R1 中使用的完整 GRPO 目标函数在 Section~\ref{subsubsec:grpo_r1_math} 中描述。

\newpage
\begin{keybox}[R1 Training Pipeline Summary]
\begin{enumerate}
  \item \textbf{Base model}: DeepSeek-V3 (671B MoE, 37B active parameters)
  \item \textbf{Cold-start SFT}: $\sim$thousands of long-CoT examples, format: \texttt{<think>...</think><answer>...</answer>}
  \item \textbf{RL phase}: GRPO with verifiable rewards on math + code problems
  \item \textbf{Rejection sampling}: Generate multiple solutions, keep correct ones
  \item \textbf{SFT on RL outputs}: Fine-tune on high-quality RL-generated chains
  \item \textbf{Final RL}: Second RL phase for alignment + helpfulness
\end{enumerate}
\end{keybox}
\newpage
\begin{keybox}[R1 训练流程总结]
\begin{enumerate}
  \item \textbf{基础模型}：DeepSeek-V3（671B MoE，37B 激活参数）
  \item \textbf{冷启动 SFT}：约数千个长思维链示例，格式：\texttt{<think>...</think><answer>...</answer>}
  \item \textbf{强化学习阶段}：使用 GRPO 对数学和代码问题进行可验证奖励
  \item \textbf{拒绝采样}：生成多个解，保留正确的解
  \item \textbf{对强化学习输出进行 SFT}：在高品质强化学习生成的链上进行微调
  \item \textbf{最终强化学习}：第二次强化学习阶段，用于对齐和有用性
\end{enumerate}
\end{keybox}

\subsection{Reward Design: Accuracy and Format Rewards}
\label{reward-design-accuracy-and-format-rewards}
\subsection{奖励设计：准确性奖励与格式奖励}
\label{reward-design-accuracy-and-format-rewards}

A key design choice in R1 is the \textbf{absence of a process reward model}. Instead, R1 uses two simple, automatically computable rewards:
R1 中的一个关键设计选择是\textbf{没有过程奖励模型（process reward model）}。相反，R1 使用两个简单、自动可计算的奖励：

\paragraph{Accuracy Reward}
\label{accuracy-reward}
\paragraph{准确性奖励}
\label{accuracy-reward}

For math problems with verifiable answers: 
\begin{equation}
    r_{\text{acc}}(y, y^*) = \begin{cases} 1 & \text{if } \texttt{verify}(y, y^*) = \texttt{True} \\ 0 & \text{otherwise} \end{cases}
\end{equation}
 where $y$ is the model’s final answer (extracted from \texttt{<answer>} tags) and $y^*$ is the ground-truth answer. The \texttt{verify} function uses symbolic math comparison (e.g., SymPy) to handle equivalent forms.
对于有可验证答案的数学问题：
\begin{equation}
    r_{\text{acc}}(y, y^*) = \begin{cases} 1 & \text{if } \texttt{verify}(y, y^*) = \texttt{True} \\ 0 & \text{otherwise} \end{cases}
\end{equation}
其中 $y$ 是模型的最终答案（从 \texttt{<answer>} 标签中提取），$y^*$ 是真实答案。\texttt{verify} 函数使用符号数学比较（例如 SymPy）来处理等价形式。

For code problems, the accuracy reward is determined by passing test cases: 
\begin{equation}
    r_{\text{acc}}^{\text{code}}(y, \mathcal{T}) = \frac{1}{|\mathcal{T}|} \sum_{t \in \mathcal{T}} \mathbf{1}[\texttt{execute}(y, t) = \texttt{expected}(t)]
\end{equation}
对于代码问题，准确性奖励通过测试用例是否通过来确定：
\begin{equation}
    r_{\text{acc}}^{\text{code}}(y, \mathcal{T}) = \frac{1}{|\mathcal{T}|} \sum_{t \in \mathcal{T}} \mathbf{1}[\texttt{execute}(y, t) = \texttt{expected}(t)]
\end{equation}

\paragraph{Format Reward}
\label{format-reward}
\paragraph{格式奖励}
\label{format-reward}

To enforce the \texttt{<think>...</think>} structure: 
\begin{equation}
    r_{\text{fmt}}(y) = \begin{cases} 1 & y \text{ has valid <think> and <answer> tags} \\ 0 & \text{otherwise} \end{cases}
\end{equation}
为了强制 \texttt{<think>...</think>} 结构：
\begin{equation}
    r_{\text{fmt}}(y) = \begin{cases} 1 & y \text{ has valid <think> and <answer> tags} \\ 0 & \text{otherwise} \end{cases}
\end{equation}

\paragraph{Combined Reward}
\label{combined-reward}
\paragraph{组合奖励}
\label{combined-reward}

\begin{equation}
    r(y, y^*) = r_{\text{acc}}(y, y^*) + \lambda_{\text{fmt}} \cdot r_{\text{fmt}}(y)
\end{equation}
 with $\lambda_{\text{fmt}} = 0.1$ in the original implementation (small enough not to dominate, large enough to prevent format collapse).
\begin{equation}
    r(y, y^*) = r_{\text{acc}}(y, y^*) + \lambda_{\text{fmt}} \cdot r_{\text{fmt}}(y)
\end{equation}
其中原始实现中 $\lambda_{\text{fmt}} = 0.1$（足够小以免主导，又足够大以防止格式崩溃）。

\begin{warningbox}[No Process Reward Model]
A notable and surprising finding of R1 is that \textbf{no process reward model (PRM) is needed}. Despite the long reasoning chains, outcome-only rewards are sufficient for RL to discover high-quality reasoning strategies. The authors hypothesize that the verifiable nature of math/code rewards provides sufficient signal, and that PRMs introduce their own failure modes (reward hacking at the step level). This contrasts with the approach taken by OpenAI (Section~\ref{subsec:openai_o1}).
\end{warningbox}

\begin{warningbox}[无过程奖励模型]
R1 的一个显著且令人惊讶的发现是：\textbf{不需要过程奖励模型（PRM）}。尽管有很长的推理链，但仅凭结果奖励就足以让强化学习发现高质量的推理策略。作者假设，数学/代码奖励的可验证性提供了足够的信号，而 PRM 会引入自身的失败模式（在步骤级别上的奖励黑客行为）。这与 OpenAI 采取的方法形成对比（Section~\ref{subsec:openai_o1}）。
\end{warningbox}

\subsection{GRPO Formulation for R1}
\label{subsubsec:grpo_r1_math}
\subsection{R1 的 GRPO 公式}
\label{subsubsec:grpo_r1_math}

## GRPO~\cite{shao2024deepseekmath} is a policy gradient method that avoids training a separate value network by estimating advantages from a *group* of sampled responses. For a question $q$, GRPO samples $G$ responses $\{y_1, y_2, \ldots, y_G\}$ from the current policy $\pi_\theta$ and computes advantages relative to the group mean.
## GRPO~\cite{shao2024deepseekmath} 是一种策略梯度方法，通过从一组采样响应中估计优势来避免训练单独的价值网络。对于问题 $q$，GRPO 从当前策略 $\pi_\theta$ 中采样 $G$ 个响应 $\{y_1, y_2, \ldots, y_G\}$，并计算相对于组均值的优势。

\paragraph{Group Sampling and Advantage Normalization}
\paragraph{分组采样与优势归一化}

\label{group-sampling-and-advantage-normalization}
\label{group-sampling-and-advantage-normalization}

Given question $q$, sample $G$ outputs: 
对于给定问题 $q$，采样 $G$ 个输出：
\begin{equation}
    \{y_i\}_{i=1}^G \sim \pi_\theta(\cdot \mid q)
\end{equation}

Compute rewards $\{r_i\}_{i=1}^G$ using the reward function from Eq.~[eq:r1\_combined\_reward]. The normalized advantage for response $i$ is: 
使用公式 [eq:r1\_combined\_reward] 中的奖励函数计算奖励 $\{r_i\}_{i=1}^G$。响应 $i$ 的归一化优势为：
\begin{equation}
    \hat{A}_i = \frac{r_i - \mu_r}{\sigma_r + \epsilon}
\end{equation}
 where $\mu_r = \frac{1}{G}\sum_{i=1}^G r_i$, $\sigma_r = \sqrt{\frac{1}{G}\sum_{i=1}^G (r_i - \mu_r)^2}$, and $\epsilon = 10^{-8}$ for numerical stability.
其中 $\mu_r = \frac{1}{G}\sum_{i=1}^G r_i$，$\sigma_r = \sqrt{\frac{1}{G}\sum_{i=1}^G (r_i - \mu_r)^2}$，并且 $\epsilon = 10^{-8}$ 用于数值稳定性。

\paragraph{GRPO Objective}
\paragraph{GRPO 目标函数}

\label{grpo-objective}
\label{grpo-objective}

The GRPO objective clips the probability ratio (as in PPO) and adds a KL penalty against a reference policy $\pi_{\text{ref}}$:
GRPO 目标函数对概率比进行裁剪（如 PPO 中），并添加针对参考策略 $\pi_{\text{ref}}$ 的 KL 惩罚：

\begin{multline}
\mathcal{L}_{\text{GRPO}}(\theta) = -\mathbb{E}_{q \sim \mathcal{D},\, \{y_i\} \sim \pi_\theta(\cdot|q)} \Bigg[ \frac{1}{G} \sum_{i=1}^{G} \frac{1}{|y_i|} \sum_{t=1}^{|y_i|} \\
\min\!\left( \rho_{i,t}\, \hat{A}_i,\; \text{clip}(\rho_{i,t}, 1{-}\varepsilon, 1{+}\varepsilon)\, \hat{A}_i \right) - \beta\, \mathbb{D}_{\mathrm{KL}}\!\left[\pi_\theta \,\|\, \pi_{\text{ref}}\right] \Bigg]
\label{eq:grpo_full}
\end{multline}

where:
其中：

\begin{itemize}
  \item $\rho_{i,t} = \dfrac{\pi_\theta(y_{i,t} \mid q, y_{i,<t})}{\pi_{\theta_{\text{old}}}(y_{i,t} \mid q, y_{i,<t})}$ is the per-token probability ratio
  \item $\rho_{i,t} = \dfrac{\pi_\theta(y_{i,t} \mid q, y_{i,<t})}{\pi_{\theta_{\text{old}}}(y_{i,t} \mid q, y_{i,<t})}$ 是每个词元的概率比
  \item $\varepsilon \in \{0.1, 0.2\}$ is the PPO clipping parameter
  \item $\varepsilon \in \{0.1, 0.2\}$ 是 PPO 裁剪参数
  \item $\beta > 0$ controls the KL penalty strength
  \item $\beta > 0$ 控制 KL 惩罚强度
  \item $|y_i|$ is the length of response $i$ (length normalization prevents bias toward short responses)
  \item $|y_i|$ 是响应 $i$ 的长度（长度归一化可防止对短响应的偏差）
\end{itemize}

\paragraph{KL Penalty Formulation}
\paragraph{KL 惩罚公式}
\label{kl-penalty-formulation}
\label{kl-penalty-formulation}

The KL divergence term is computed token-by-token: 
KL 散度项按词元逐个计算：
\begin{equation}
    \mathbb{D}_{\mathrm{KL}}\!\left[\pi_\theta \,\|\, \pi_{\text{ref}}\right] = \mathbb{E}_{y \sim \pi_\theta(\cdot|q)} \left[ \sum_{t=1}^{|y|} \log \frac{\pi_\theta(y_t \mid q, y_{<t})}{\pi_{\text{ref}}(y_t \mid q, y_{<t})} \right]
\end{equation}

In practice, R1 uses an unbiased estimator of the KL that avoids computing $\pi_{\text{ref}}$ at every step by using the approximation: 
在实践中，R1 使用 KL 的无偏估计，通过以下近似避免每一步都计算 $\pi_{\text{ref}}$：
\begin{equation}
    \mathbb{D}_{\mathrm{KL}}\!\left[\pi_\theta \,\|\, \pi_{\text{ref}}\right] \approx \frac{\pi_{\text{ref}}(y_t \mid q, y_{<t})}{\pi_\theta(y_t \mid q, y_{<t})} - \log \frac{\pi_{\text{ref}}(y_t \mid q, y_{<t})}{\pi_\theta(y_t \mid q, y_{<t})} - 1
\end{equation}
 which is always non-negative and equals zero when $\pi_\theta = \pi_{\text{ref}}$.
该近似值始终非负，并在 $\pi_\theta = \pi_{\text{ref}}$ 时为零。

\begin{examplebox}[GRPO in Practice: Group Size and Stability]
\begin{examplebox}[GRPO 实践：分组大小与稳定性]
In R1’s training, $G = 8$ responses are sampled per question. This is a critical hyperparameter:
在 R1 的训练中，每个问题采样 $G = 8$ 个响应。这是一个关键超参数：

\begin{itemize}
  \item Too small ($G=2$): High variance in advantage estimates; training is noisy.
  \item 太小（$G=2$）：优势估计方差大；训练噪声大。
  \item Too large ($G=32$): Computational cost scales linearly; diminishing returns.
  \item 太大（$G=32$）：计算成本线性增长；收益递减。
  \item $G=8$: Empirically found to balance variance reduction and compute cost.
  \item $G=8$：经验上在方差降低和计算成本之间取得了平衡。
\end{itemize}

The group sampling also provides a natural \textbf{curriculum signal}: as training progresses, the model’s average reward $\mu_r$ increases, and the variance $\sigma_r$ decreases. Problems where all $G$ responses are correct (or all wrong) contribute zero gradient, naturally focusing learning on problems at the frontier of the model’s capability.
分组采样还提供了自然的\textbf{课程信号}：随着训练进行，模型的平均奖励 $\mu_r$ 增加，方差 $\sigma_r$ 减小。所有 $G$ 个响应都正确（或都错误）的问题产生零梯度，从而自然地将学习聚焦于模型能力边界上的问题。
\end{examplebox}

\subsection{Distillation: The R1-Distill Series}
\subsection{蒸馏：R1-Distill 系列}

\label{distillation-the-r1-distill-series}
\label{distillation-the-r1-distill-series}

A major practical contribution of R1 is demonstrating that \textbf{reasoning capabilities can be distilled into much smaller models} via supervised fine-tuning on R1-generated chains. The R1-Distill series (1.5B, 7B, 8B, 14B, 32B, 70B parameters) is trained by:
R1 的一个重要实际贡献是证明了\textbf{推理能力可以通过对 R1 生成的推理链进行监督微调蒸馏到更小的模型中}。R1-Distill 系列（1.5B、7B、8B、14B、32B、70B 参数）通过以下方式训练：

\begin{enumerate}
  \item Generating long-CoT solutions to a large problem set using R1 (671B)
  \item 使用 R1（671B）为大量问题集生成长 CoT 解决方案
  \item Filtering to keep only correct solutions
  \item 过滤以仅保留正确解决方案
  \item Fine-tuning smaller base models (Qwen2.5, Llama-3) on these solutions
  \item 在这些解决方案上微调较小的基础模型（Qwen2.5、Llama-3）
\end{enumerate}

\begin{keybox}[Distillation vs. RL for Small Models]
\begin{keybox}[蒸馏 vs. 小模型的强化学习]
A striking finding: \textbf{distillation outperforms RL training from scratch on small models}. DeepSeek-R1-Distill-Qwen-7B achieves higher MATH benchmark scores than a 7B model trained with GRPO directly. This suggests that:
一个惊人的发现：\textbf{蒸馏在小型模型上优于从头开始的强化学习训练}。DeepSeek-R1-Distill-Qwen-7B 达到了比直接使用 GRPO 训练的 7B 模型更高的 MATH 基准分数。这表明：

\begin{itemize}
  \item Small models lack the capacity to discover reasoning strategies via RL exploration
  \item 小型模型缺乏通过强化学习探索发现推理策略的能力
  \item But they \emph{can} learn to imitate reasoning strategies discovered by larger models
  \item 但它们\textit{能够}学习模仿由较大模型发现的推理策略
  \item The bottleneck for small models is \emph{exploration}, not \emph{representation}
  \item 小型模型的瓶颈是\textit{探索}，而不是\textit{表示}
\end{itemize}
\end{keybox}

The distillation approach raises an important question about the nature of reasoning: is the small model truly “reasoning,” or is it pattern-matching on the surface form of reasoning chains? Empirically, distilled models show some generalization to novel problem types, suggesting genuine internalization of reasoning strategies rather than pure memorization.
蒸馏方法提出了一个关于推理本质的重要问题：小型模型是真的在“推理”，还是在推理链的表层形式上进行模式匹配？经验上，蒸馏模型展示出对新颖问题类型的一定泛化能力，这表明它们真正内化了推理策略，而非纯粹记忆。

\section{OpenAI o1/o3 Series}
\section{OpenAI o1/o3 系列}

\label{subsec:openai_o1}
\label{subsec:openai_o1}

OpenAI’s o1~\cite{openai2024o1} (released September 2024) and subsequent o3/o4-mini~\cite{openai2025o3} models represent the commercial frontier of reasoning model development. While full technical details remain proprietary, the published system cards, technical reports, and empirical observations provide substantial insight into the methodology.
OpenAI 的 o1~\cite{openai2024o1}（2024年9月发布）以及随后的 o3/o4-mini~\cite{openai2025o3} 模型代表了推理模型开发的商业前沿。虽然完整的技术细节仍属专有，但已发布的系统卡、技术报告和经验观察为该方法提供了大量洞见。

\subsection{Chain-of-Thought RL with Hidden Reasoning Tokens}
\subsection{带隐藏推理词元的思维链强化学习}
\label{chain-of-thought-rl-with-hidden-reasoning-tokens}
\label{chain-of-thought-rl-with-hidden-reasoning-tokens}

The defining architectural choice of o1 is the use of \textbf{hidden reasoning tokens}: the model generates an internal chain-of-thought (called a “reasoning trace” or “thinking tokens”) that is not shown to the user. Only the final answer is returned. This design has several implications:
o1 的决定性架构选择是使用\textbf{隐藏的推理词元}：模型生成内部思维链（称为“推理轨迹”或“思考词元”），但这些内容不展示给用户，仅返回最终答案。这种设计具有多个含义：

\begin{itemize}
  \item \textbf{No format constraints}: The hidden reasoning can use any format, including scratchpad notation, pseudocode, or even non-English reasoning.
  \item \textbf{无格式约束}：隐藏推理可以使用任何格式，包括草稿表示法、伪代码，甚至非英语推理。
  \item \textbf{No reward hacking on style}: Since users never see the reasoning, there is no pressure to make it look “good” rather than be useful.
  \item \textbf{无风格方面的奖励篡改}：由于用户从不看到推理过程，因此没有压力让它看起来“好”而不是有用。
  \item \textbf{Proprietary protection}: The reasoning process is not exposed, preventing direct imitation.
  \item \textbf{专有保护}：推理过程不暴露，防止直接模仿。
\end{itemize}

The training procedure is described as “training models to reason using RL,” with the RL objective applied to the complete (hidden reasoning + final answer) sequence, rewarded only on the quality of the final answer.
训练过程被描述为“使用强化学习训练模型进行推理”，强化学习目标应用于完整的（隐藏推理 + 最终答案）序列，仅根据最终答案的质量进行奖励。

\subsection{Process Reward Models vs.~Outcome Reward Models}
\subsection{过程奖励模型 vs. 结果奖励模型}
\label{process-reward-models-vs.-outcome-reward-models}
\label{process-reward-models-vs.-outcome-reward-models}

OpenAI’s approach is believed to use \textbf{Process Reward Models (PRMs)}~\cite{lightman2023lets} in addition to outcome rewards, in contrast to DeepSeek-R1’s outcome-only approach. This inference is based on OpenAI’s published PRM research (PRM800K dataset, “Let’s Verify Step by Step”) and the o1 system card’s description of RL training on reasoning chains, though the exact o1/o3 training recipe has not been publicly disclosed.
据信 OpenAI 的方法除了结果奖励外还使用了\textbf{过程奖励模型 (PRMs)}~\cite{lightman2023lets}，这与 DeepSeek-R1 仅使用结果奖励的方法形成对比。这一推断基于 OpenAI 已发布的 PRM 研究（PRM800K 数据集、“Let’s Verify Step by Step”）以及 o1 系统卡中关于推理链强化学习训练的描述，尽管 o1/o3 的具体训练配方尚未公开披露。

\paragraph{Outcome Reward Model (ORM)}
\paragraph{结果奖励模型 (ORM)}
\label{outcome-reward-model-orm}
\label{outcome-reward-model-orm}

An ORM scores the complete response $(q, y)$: 
ORM 对完整响应 $(q, y)$ 进行评分：
\begin{equation}
    R_{\text{ORM}}(q, y) \in [0, 1]
\end{equation}
 For verifiable tasks (math, code), this reduces to exact-match verification. For open-ended tasks, a learned reward model is used.
对于可验证任务（数学、代码），这简化为精确匹配验证。对于开放式任务，则使用学习到的奖励模型。

\paragraph{Process Reward Model (PRM)}
\paragraph{过程奖励模型 (PRM)}
\label{process-reward-model-prm}
\label{process-reward-model-prm}

## 原英文标题 (见下文)
## 中文标题

A PRM assigns a reward to each reasoning step $s_k$ in the chain $y = (s_1, s_2, \ldots, s_K)$: 
\begin{equation}
    R_{\text{PRM}}(q, y) = \sum_{k=1}^{K} \gamma^{K-k} \cdot r_k(q, s_1, \ldots, s_k)
\end{equation}
 where $r_k \in [0,1]$ is the step-level reward and $\gamma \in (0,1]$ is a discount factor. The step-level reward $r_k$ estimates the probability that the partial solution $(s_1, \ldots, s_k)$ leads to a correct final answer: 
\begin{equation}
    r_k(q, s_1, \ldots, s_k) = P(\text{correct final answer} \mid q, s_1, \ldots, s_k)
\end{equation}

一个过程奖励模型（PRM）为链 $y = (s_1, s_2, \ldots, s_K)$ 中的每个推理步骤 $s_k$ 分配一个奖励：
\begin{equation}
    R_{\text{PRM}}(q, y) = \sum_{k=1}^{K} \gamma^{K-k} \cdot r_k(q, s_1, \ldots, s_k)
\end{equation}
其中 $r_k \in [0,1]$ 是步骤级奖励，$\gamma \in (0,1]$ 是折扣因子。步骤级奖励 $r_k$ 估计部分解 $(s_1, \ldots, s_k)$ 导致正确最终答案的概率：
\begin{equation}
    r_k(q, s_1, \ldots, s_k) = P(\text{正确最终答案} \mid q, s_1, \ldots, s_k)
\end{equation}

\begin{intuitionbox}[PRM vs. ORM: The Credit Assignment Tradeoff]
\textbf{ORM} provides clean, unambiguous rewards but suffers from severe credit assignment problems: a single wrong step early in a 50-step chain receives the same zero reward as a completely random response.

\textbf{PRM} provides dense rewards that directly address credit assignment, but introduces new challenges:

\begin{itemize}
  \item \textbf{Training data}: Step-level labels require human annotation or automated generation (Math-Shepherd, Section~\ref{subsubsec:prm_methods}).
  \item \textbf{Reward hacking}: Models can learn to produce steps that \emph{look} correct to the PRM without actually being correct.
  \item \textbf{Distribution shift}: PRMs trained on one distribution of reasoning chains may not generalize to the novel chains produced by RL.
\end{itemize}

The empirical evidence suggests PRMs are beneficial for \emph{search} (selecting among candidate solutions) but their benefit for \emph{training} is less clear.
\end{intuitionbox}

\begin{intuitionbox}[PRM 与 ORM：信用分配权衡]
\textbf{ORM} 提供清晰、明确的奖励，但遭受严重的信用分配问题：在一个50步链中早期的一个错误步骤与完全随机的响应获得相同的零奖励。

\textbf{PRM} 提供密集的奖励，直接解决信用分配问题，但引入了新的挑战：

\begin{itemize}
  \item \textbf{训练数据}：步骤级标签需要人工标注或自动生成（Math-Shepherd，第~\ref{subsubsec:prm_methods}节）。
  \item \textbf{奖励篡改}：模型可能学会生成在PRM看来 \emph{正确} 但实际上并不正确的步骤。
  \item \textbf{分布偏移}：在一种推理链分布上训练的PRM可能无法泛化到RL产生的新链。
\end{itemize}

经验证据表明，PRM 对 \emph{搜索}（候选解的选择）有益，但其对 \emph{训练} 的益处尚不明确。
\end{intuitionbox}

\subsection{Inference-Time Compute Scaling}
\label{inference-time-compute-scaling}

\subsection{推理时计算扩展}
\label{inference-time-compute-scaling}

The o1 technical report demonstrates a clear scaling law: \textbf{more thinking tokens monotonically improve performance} on hard reasoning tasks. This is operationalized through a ``thinking budget'' parameter that controls the maximum number of hidden reasoning tokens.

o1技术报告展示了一个清晰的缩放定律：在困难推理任务上，\textbf{更多的思考token单调地提升性能}。这通过一个“思考预算”参数来实现，该参数控制隐藏推理token的最大数量。

Let $T$ be the thinking token budget. The empirical scaling law observed is approximately: 
\begin{equation}
    \text{Pass@1}(T) \approx a - b \cdot T^{-c}
\end{equation}
 for constants $a, b, c > 0$, where $a$ represents the asymptotic accuracy ceiling and $c$ characterizes the rate of improvement. For AIME 2024, o1 with full thinking budget achieves $\sim$83\% accuracy, compared to $\sim$13\% for GPT-4o (which uses no extended thinking).

设 $T$ 为思考token预算。观察到的经验缩放定律近似为：
\begin{equation}
    \text{Pass@1}(T) \approx a - b \cdot T^{-c}
\end{equation}
其中 $a, b, c > 0$ 为常数，$a$ 表示渐近精度上限，$c$ 描述提升速率。对于AIME 2024，使用完整思考预算的o1达到约83%的准确率，而GPT-4o（不使用扩展思考）仅为约13%。

\subsection{Training Compute vs.~Test-Time Compute}
\label{training-compute-vs.-test-time-compute}

\subsection{训练计算 vs. 测试时计算}
\label{training-compute-vs.-test-time-compute}

A fundamental insight from the o1/o3 series is the \textbf{compute equivalence principle}: there exists a tradeoff curve between training compute $C_{\text{train}}$ and test-time compute $C_{\text{test}}$ such that points on the curve achieve similar performance:

来自o1/o3系列的一个基本见解是 \textbf{计算等价原理}：训练计算 $C_{\text{train}}$ 与测试时计算 $C_{\text{test}}$ 之间存在一个权衡曲线，使得曲线上的点达到相似性能：

\begin{equation}
    \text{Performance}(C_{\text{train}}, C_{\text{test}}) = g\!\left(\alpha C_{\text{train}}^{p} + \beta C_{\text{test}}^{q}\right)
\end{equation}

Empirically, $p \approx q$ for reasoning tasks, suggesting that training and test-time compute are roughly substitutable. This has profound implications for deployment: a smaller, cheaper model with extended thinking can match a larger model on hard problems, at the cost of higher latency.

经验上，对于推理任务 $p \approx q$，表明训练计算和测试时计算大致可互换。这对部署有深远影响：一个更小、更便宜的模型通过扩展思考可以在困难问题上匹配更大的模型，代价是更高的延迟。

\subsection{o3 and o4-mini Architecture Insights}
\label{o3-and-o4-mini-architecture-insights}

\subsection{o3 与 o4-mini 架构见解}
\label{o3-and-o4-mini-architecture-insights}

While o3 and o4-mini details remain largely proprietary, several observations have emerged:

尽管o3和o4-mini的细节大部分是专有的，但出现了一些观察结果：

\begin{itemize}
  \item \textbf{o3}: Substantially larger thinking budgets than o1; achieves near-human performance on ARC-AGI (87.5\% with high compute). Believed to use more sophisticated search strategies during inference.
  \item \textbf{o4-mini}: Demonstrates that \emph{smaller} models with RL-trained reasoning can be highly competitive. Achieves 93\% on AIME 2025 with extended thinking, suggesting that model size is less important than reasoning capability for math.
  \item \textbf{Tool use}: o3/o4-mini integrate tool use (code execution, web search) into the reasoning process, allowing the model to verify intermediate steps programmatically.
\end{itemize}

\begin{itemize}
  \item \textbf{o3}：比o1大得多的思考预算；在ARC-AGI上达到接近人类的表现（高计算下87.5%）。据信在推理中使用了更复杂的搜索策略。
  \item \textbf{o4-mini}：展示了通过RL训练推理的 \emph{更小} 模型可以极具竞争力。通过扩展思考在AIME 2025上达到93%，表明对于数学，模型大小不如推理能力重要。
  \item \textbf{工具使用}：o3/o4-mini将工具使用（代码执行、网络搜索）整合到推理过程中，使模型能够通过编程方式验证中间步骤。
\end{itemize}

\section{QwQ and Qwen Reasoning Models}
\label{subsec:qwq_qwen}

\section{QwQ 与 Qwen 推理模型}
\label{subsec:qwq_qwen}

Alibaba’s Qwen team has developed a series of reasoning models (QwQ-32B~\cite{qwen2024qwq}, Qwen3~\cite{qwen2025qwen3}) that represent the open-source frontier alongside DeepSeek-R1. Their approach differs in several key respects.

阿里巴巴的Qwen团队开发了一系列推理模型（QwQ-32B~\cite{qwen2024qwq}，Qwen3~\cite{qwen2025qwen3}），与DeepSeek-R1一起代表了开源前沿。他们的方法在几个关键方面有所不同。

\subsection{Multi-Stage RL Pipeline}
\label{multi-stage-rl-pipeline}

\subsection{多阶段RL流程}
\label{multi-stage-rl-pipeline}

The Qwen reasoning pipeline uses a more elaborate multi-stage approach:

Qwen推理流程采用更精细的多阶段方法：

\begin{enumerate}
  \item \textbf{Base pretraining}: Qwen2.5 base model with strong mathematical and coding capabilities
  \item \textbf{SFT on diverse reasoning}: Fine-tuning on a broad mixture of reasoning tasks (math, code, science, logic)
  \item \textbf{Rejection sampling fine-tuning (RFT)}: Generate $N$ solutions per problem, keep correct ones, fine-tune
  \item \textbf{RL phase 1}: GRPO on math and code with verifiable rewards
  \item \textbf{RL phase 2}: Broader RL including instruction following and safety
\end{enumerate}

\begin{enumerate}
  \item \textbf{基础预训练}：Qwen2.5基础模型，具有强大的数学和编码能力
  \item \textbf{多样化推理上的SFT}：在广泛的推理任务混合（数学、代码、科学、逻辑）上进行微调
  \item \textbf{拒绝采样微调（RFT）}：每个问题生成 $N$ 个解，保留正确的，进行微调
  \item \textbf{RL阶段1}：在数学和代码上使用GRPO，具有可验证的奖励
  \item \textbf{RL阶段2}：更广泛的RL，包括指令遵循和安全
\end{enumerate}

\subsection{Rejection Sampling + RL Combination}
\label{rejection-sampling-rl-combination}

\subsection{拒绝采样 + RL 组合}
\label{rejection-sampling-rl-combination}

A key innovation in the Qwen approach is the \textbf{iterative combination of rejection sampling and RL}:

Qwen方法中的一个关键创新是 \textbf{拒绝采样与RL的迭代组合}：

\begin{enumerate}
  \item \textbf{Initialize}: Policy $\pi_0$ from SFT model.
  \item \textbf{Rejection Sampling}: Sample $N$ solutions: $\{y_i\}_{i=1}^N \sim \pi_{k-1}(\cdot \mid q)$. Keep correct solutions: $\mathcal{Y}^+(q) = \{y_i : r(y_i, y^*) = 1\}$.
  \item \textbf{SFT update}: $\pi_k^{\text{SFT}} \leftarrow \text{SFT}(\pi_{k-1}, \bigcup_q \mathcal{Y}^+(q))$
  \item \textbf{RL update}: $\pi_k \leftarrow \text{GRPO}(\pi_k^{\text{SFT}}, \mathcal{D})$
  \item \textbf{Repeat} steps 2--4 for $K$ iterations to obtain final policy $\pi_K$.
\end{enumerate}

\begin{enumerate}
  \item \textbf{初始化}：策略 $\pi_0$ 来自SFT模型。
  \item \textbf{拒绝采样}：采样 $N$ 个解：$\{y_i\}_{i=1}^N \sim \pi_{k-1}(\cdot \mid q)$。保留正确的解：$\mathcal{Y}^+(q) = \{y_i : r(y_i, y^*) = 1\}$。
  \item \textbf{SFT更新}：$\pi_k^{\text{SFT}} \leftarrow \text{SFT}(\pi_{k-1}, \bigcup_q \mathcal{Y}^+(q))$
  \item \textbf{RL更新}：$\pi_k \leftarrow \text{GRPO}(\pi_k^{\text{SFT}}, \mathcal{D})$
  \item \textbf{重复} 步骤2--4共 $K$ 次迭代，得到最终策略 $\pi_K$。
\end{enumerate}

The rejection sampling step provides high-quality positive examples that anchor the policy, while RL explores beyond the current distribution. This combination is more stable than pure RL and more capable than pure SFT.

拒绝采样步骤提供了高质量的正例来锚定策略，而RL则探索当前分布之外。这种组合比纯RL更稳定，比纯SFT更有能力。

\subsection{Tool-Integrated Reasoning}
\label{tool-integrated-reasoning}

\subsection{工具集成推理}
\label{tool-integrated-reasoning}

QwQ-32B and Qwen3 models support \textbf{tool-integrated reasoning}: the model can invoke external tools (Python interpreter, search engine, calculator) during its reasoning chain. This is implemented via special tokens:

QwQ-32B和Qwen3模型支持 \textbf{工具集成推理}：模型可以在其推理链中调用外部工具（Python解释器、搜索引擎、计算器）。这通过特殊标记实现：

\begin{lstlisting}[style=pythonstyle, caption={Tool-integrated reasoning format in QwQ}]
<think>
Let me solve this step by step.
First, I'll compute the eigenvalues of the matrix.


<tool_call>
{"name": "python", "arguments": {"code": "import numpy as np\nA = np.array([[2,1],[1,3]])\neigenvalues = np.linalg.eigvals(A)\nprint(eigenvalues)"}}
</tool_call>


<tool_response>
[1.38196601 3.61803399]
</tool_response>


The eigenvalues are approximately 1.382 and 3.618.
These are (5 +/- sqrt5)/2, which are the golden ratio and its conjugate...
</think>
<answer>The eigenvalues are (5 +/- sqrt5)/2</answer>
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={QwQ 中的工具集成推理格式}]
<think>
让我逐步解决这个问题。
首先，我将计算矩阵的特征值。


<tool_call>
{"name": "python", "arguments": {"code": "import numpy as np\nA = np.array([[2,1],[1,3]])\neigenvalues = np.linalg.eigvals(A)\nprint(eigenvalues)"}}
</tool_call>


<tool_response>
[1.38196601 3.61803399]
</tool_response>


特征值近似为 1.382 和 3.618。
它们是 (5 +/- sqrt5)/2，即黄金比例及其共轭...
</think>
<answer>特征值为 (5 +/- sqrt5)/2</answer>
\end{lstlisting}

The RL training reward is computed on the final answer, but the model learns to use tools strategically because tool use improves the probability of reaching the correct answer.

RL训练奖励基于最终答案计算，但模型学会策略性地使用工具，因为使用工具提高了达到正确答案的概率。

\section{Key Methods with Mathematical Foundations}
\label{subsec:reasoning_methods}

\section{具有数学基础的关键方法}
\label{subsec:reasoning_methods}

\subsection{Monte Carlo Tree Search for Reasoning}
\label{subsubsec:mcts_reasoning}

\subsection{用于推理的蒙特卡洛树搜索}
\label{subsubsec:mcts_reasoning}

Monte Carlo Tree Search (MCTS) provides a principled framework for reasoning as tree search. In the AlphaProof~\cite{alphaproof2024} and related systems, MCTS is applied over reasoning steps rather than game moves.

蒙特卡洛树搜索（MCTS）为作为树搜索的推理提供了一个有原则的框架。在AlphaProof~\cite{alphaproof2024}及相关系统中，MCTS应用于推理步骤而非游戏动作。

\paragraph{State and Action Space}
\label{state-and-action-space}

\paragraph{状态与动作空间}
\label{state-and-action-space}

## \begin{itemize}
## \begin{itemize}

\item \textbf{State} $s_k$: The partial reasoning chain $(q, r_1, r_2, \ldots, r_k)$ where $r_i$ are reasoning steps
\item \textbf{Action} $a$: The next reasoning step (a sentence or paragraph)
\item \textbf{Terminal state}: A state containing a final answer
\item \textbf{Reward}: $R(s_{\text{terminal}}) = r_{\text{acc}}$ (Eq.~[eq:r1\_accuracy\_reward])
\end{itemize}

\item \textbf{状态} $s_k$：部分推理链 $(q, r_1, r_2, \ldots, r_k)$，其中 $r_i$ 为推理步骤
\item \textbf{动作} $a$：下一个推理步骤（一个句子或段落）
\item \textbf{终止状态}：包含最终答案的状态
\item \textbf{奖励}：$R(s_{\text{terminal}}) = r_{\text{acc}}$（式~[eq:r1\_accuracy\_reward]）
\end{itemize}

\paragraph{Value Function for Partial Solutions}
\label{value-function-for-partial-solutions}

\paragraph{部分解的价值函数}
\label{value-function-for-partial-solutions}

A value function $V(s_k)$ estimates the probability of reaching a correct answer from partial state $s_k$: 
\begin{equation}
    V(s_k) = P(\text{correct answer} \mid s_k) \approx \frac{1}{M} \sum_{m=1}^{M} R(\text{rollout}_m(s_k))
\end{equation}
 where $\text{rollout}_m(s_k)$ is a Monte Carlo rollout from $s_k$ to a terminal state using the current policy.

价值函数 $V(s_k)$ 估计从部分状态 $s_k$ 到达正确答案的概率：
\begin{equation}
    V(s_k) = P(\text{正确答案} \mid s_k) \approx \frac{1}{M} \sum_{m=1}^{M} R(\text{rollout}_m(s_k))
\end{equation}
其中 $\text{rollout}_m(s_k)$ 是从 $s_k$ 到终止状态的蒙特卡洛展开（使用当前策略）。

\paragraph{UCB Exploration}
\label{ucb-exploration}

\paragraph{UCB 探索}
\label{ucb-exploration}

Node selection uses the Upper Confidence Bound (UCB) formula adapted for reasoning: 
\begin{equation}
    \text{UCB}(s_k, a) = Q(s_k, a) + c_{\text{puct}} \cdot \pi_\theta(a \mid s_k) \cdot \frac{\sqrt{N(s_k)}}{1 + N(s_k, a)}
\end{equation}
 where:

节点选择使用适用于推理的上置信界（UCB）公式：
\begin{equation}
    \text{UCB}(s_k, a) = Q(s_k, a) + c_{\text{puct}} \cdot \pi_\theta(a \mid s_k) \cdot \frac{\sqrt{N(s_k)}}{1 + N(s_k, a)}
\end{equation}
其中：

\begin{itemize}
  \item $Q(s_k, a) = \frac{1}{N(s_k,a)} \sum_{\text{visits}} V(s_{k+1})$ is the mean value of child states
  \item $\pi_\theta(a \mid s_k)$ is the policy prior (language model probability of step $a$)
  \item $N(s_k)$ is the visit count of state $s_k$
  \item $N(s_k, a)$ is the visit count of the $(s_k, a)$ edge
  \item $c_{\text{puct}}$ is the exploration constant
\end{itemize}

\begin{itemize}
  \item $Q(s_k, a) = \frac{1}{N(s_k,a)} \sum_{\text{visits}} V(s_{k+1})$ 是子状态的平均价值
  \item $\pi_\theta(a \mid s_k)$ 是策略先验（步骤 $a$ 的语言模型概率）
  \item $N(s_k)$ 是状态 $s_k$ 的访问次数
  \item $N(s_k, a)$ 是 $(s_k, a)$ 边的访问次数
  \item $c_{\text{puct}}$ 是探索常数
\end{itemize}

\paragraph{MCTS-Guided Training}
\label{mcts-guided-training}

\paragraph{基于 MCTS 的训练}
\label{mcts-guided-training}

MCTS can be used to generate high-quality training data: 
\begin{equation}
    \mathcal{L}_{\text{MCTS}}(\theta) = -\sum_{k} \sum_{a} \pi_{\text{MCTS}}(a \mid s_k) \log \pi_\theta(a \mid s_k)
\end{equation}
 where $\pi_{\text{MCTS}}(a \mid s_k) \propto N(s_k, a)^{1/\tau}$ is the MCTS policy (visit count distribution with temperature $\tau$).

MCTS 可用于生成高质量训练数据：
\begin{equation}
    \mathcal{L}_{\text{MCTS}}(\theta) = -\sum_{k} \sum_{a} \pi_{\text{MCTS}}(a \mid s_k) \log \pi_\theta(a \mid s_k)
\end{equation}
其中 $\pi_{\text{MCTS}}(a \mid s_k) \propto N(s_k, a)^{1/\tau}$ 是 MCTS 策略（带温度 $\tau$ 的访问次数分布）。

\subsection{Process Reward Models}
\label{subsubsec:prm_methods}

\subsection{过程奖励模型（Process Reward Models, PRM）}
\label{subsubsec:prm_methods}

\paragraph{Math-Shepherd: Automated PRM Training}
\label{math-shepherd-automated-prm-training}

\paragraph{Math-Shepherd：自动 PRM 训练}
\label{math-shepherd-automated-prm-training}

Math-Shepherd~\cite{wang2024mathshepherd} proposes an automated method for training PRMs without human step-level annotations. The key insight is to use \textbf{outcome-based estimation}: a step $s_k$ is labeled as correct if there exists a completion from $s_k$ that reaches the correct answer.

Math-Shepherd~\cite{wang2024mathshepherd} 提出了一种自动训练 PRM 的方法，无需人工步骤级标注。关键思想是使用 \textbf{基于结果的估计}：如果存在从 $s_k$ 出发的补全能到达正确答案，则步骤 $s_k$ 被标记为正确。

Formally, for a partial solution $(s_1, \ldots, s_k)$: 
\begin{equation}
    \hat{r}_k = \mathbf{1}\!\left[\exists\, (s_{k+1}, \ldots, s_K) : \text{verify}(s_K, y^*) = 1\right]
\end{equation}

形式上，对于部分解 $(s_1, \ldots, s_k)$：
\begin{equation}
    \hat{r}_k = \mathbf{1}\!\left[\exists\, (s_{k+1}, \ldots, s_K) : \text{verify}(s_K, y^*) = 1\right]
\end{equation}

In practice, this is estimated by sampling $M$ completions from $s_k$ and checking if any are correct: 
\begin{equation}
    \hat{r}_k \approx \mathbf{1}\!\left[\sum_{m=1}^{M} \text{verify}(\text{complete}_m(s_k), y^*) > 0\right]
\end{equation}

实践中，通过从 $s_k$ 采样 $M$ 个补全并检查是否有任何一个是正确的来估计：
\begin{equation}
    \hat{r}_k \approx \mathbf{1}\!\left[\sum_{m=1}^{M} \text{verify}(\text{complete}_m(s_k), y^*) > 0\right]
\end{equation}

The PRM is then trained with binary cross-entropy: 
\begin{equation}
    \mathcal{L}_{\text{PRM}}(\phi) = -\sum_{k=1}^{K} \left[ \hat{r}_k \log r_\phi(s_k) + (1-\hat{r}_k) \log(1 - r_\phi(s_k)) \right]
\end{equation}

然后使用二元交叉熵训练 PRM：
\begin{equation}
    \mathcal{L}_{\text{PRM}}(\phi) = -\sum_{k=1}^{K} \left[ \hat{r}_k \log r_\phi(s_k) + (1-\hat{r}_k) \log(1 - r_\phi(s_k)) \right]
\end{equation}

\paragraph{PRM for Best-of-N Selection}
\label{prm-for-best-of-n-selection}

\paragraph{用于 Best-of-N 选择的 PRM}
\label{prm-for-best-of-n-selection}

A primary application of PRMs is \textbf{best-of-N selection}: generate $N$ candidate solutions and select the one with the highest PRM score: 
\begin{equation}
    y^* = \arg\max_{y \in \{y_1, \ldots, y_N\}} R_{\text{PRM}}(q, y)
\end{equation}

PRM 的一个主要应用是 \textbf{最佳N选一（Best-of-N Selection）}：生成 $N$ 个候选解，选择 PRM 分数最高的那个：
\begin{equation}
    y^* = \arg\max_{y \in \{y_1, \ldots, y_N\}} R_{\text{PRM}}(q, y)
\end{equation}

This is more effective than majority voting (which uses ORM) because PRM can distinguish between solutions that reach the same answer via different quality reasoning paths.

这比多数投票（使用 ORM）更有效，因为 PRM 能够区分通过不同质量推理路径到达同一答案的解。

\subsection{Outcome Reward Models and Majority Voting}
\label{outcome-reward-models-and-majority-voting}

\subsection{结果奖励模型（ORM）与多数投票}
\label{outcome-reward-models-and-majority-voting}

\paragraph{Majority Voting (Self-Consistency)}
\label{majority-voting-self-consistency}

\paragraph{多数投票（自一致性）}
\label{majority-voting-self-consistency}

The simplest form of test-time compute scaling is majority voting~\cite{wang2023selfconsistency}: generate $N$ solutions and return the most common answer: 
\begin{equation}
    y^* = \arg\max_{a} \sum_{i=1}^{N} \mathbf{1}[y_i = a]
\end{equation}

测试时计算扩展的最简单形式是多数投票~\cite{wang2023selfconsistency}：生成 $N$ 个解，返回出现频率最高的答案：
\begin{equation}
    y^* = \arg\max_{a} \sum_{i=1}^{N} \mathbf{1}[y_i = a]
\end{equation}

Under the assumption that each solution is independently correct with probability $p > 0.5$, the probability that majority voting is correct is: 
\begin{equation}
    P(\text{majority correct}) = \sum_{k=\lceil N/2 \rceil}^{N} \binom{N}{k} p^k (1-p)^{N-k} \xrightarrow{N \to \infty} 1
\end{equation}

假设每个解独立正确的概率为 $p > 0.5$，则多数投票正确的概率为：
\begin{equation}
    P(\text{多数正确}) = \sum_{k=\lceil N/2 \rceil}^{N} \binom{N}{k} p^k (1-p)^{N-k} \xrightarrow{N \to \infty} 1
\end{equation}

\paragraph{Weighted Majority Voting with ORM}
\label{weighted-majority-voting-with-orm}

\paragraph{基于 ORM 的加权多数投票}
\label{weighted-majority-voting-with-orm}

An ORM can improve majority voting by weighting votes by confidence: 
\begin{equation}
    y^* = \arg\max_{a} \sum_{i=1}^{N} R_{\text{ORM}}(q, y_i) \cdot \mathbf{1}[y_i = a]
\end{equation}

ORM 可以通过置信度加权来改进多数投票：
\begin{equation}
    y^* = \arg\max_{a} \sum_{i=1}^{N} R_{\text{ORM}}(q, y_i) \cdot \mathbf{1}[y_i = a]
\end{equation}

\subsection{Self-Play for Reasoning}
\label{self-play-for-reasoning}

\subsection{用于推理的自对弈（Self-Play）}
\label{self-play-for-reasoning}

Self-play methods generate training data by having the model play both the \emph{generator} and \emph{verifier} roles.

自对弈方法通过让模型扮演 \emph{生成器} 和 \emph{验证器} 两种角色来生成训练数据。

\paragraph{STaR: Self-Taught Reasoner}
\label{star-self-taught-reasoner}

\paragraph{STaR：自学推理器}
\label{star-self-taught-reasoner}

STaR~\cite{zelikman2022star} bootstraps reasoning capabilities iteratively:

STaR~\cite{zelikman2022star} 迭代式地自举推理能力：

\begin{enumerate}
  \item Generate reasoning chains for a problem set
  \item Keep chains that lead to correct answers (rejection sampling)
  \item Fine-tune on kept chains
  \item Repeat with the improved model
\end{enumerate}

\begin{enumerate}
  \item 为问题集生成推理链
  \item 保留导向正确答案的链（拒绝采样）
  \item 在保留的链上微调
  \item 使用改进后的模型重复上述过程
\end{enumerate}

The key insight is that the model can \emph{rationalize} correct answers: even if it cannot solve a problem from scratch, it can generate a plausible reasoning chain given the answer, which can then be used as training data.

关键思想在于模型能够对正确答案进行 \emph{合理化}：即使模型无法从头解决问题，它也可以根据答案生成合理的推理链，并以此作为训练数据。

\paragraph{Self-Play RL}
\label{self-play-rl}

\paragraph{自对弈强化学习（Self-Play RL）}
\label{self-play-rl}

In self-play RL for reasoning, the model generates both problems and solutions: 
\begin{equation}
    \mathcal{L}_{\text{self-play}}(\theta) = \mathbb{E}_{q \sim \pi_\theta^{\text{gen}}} \mathbb{E}_{y \sim \pi_\theta^{\text{solve}}(\cdot|q)} \left[ r(y, y^*) \right]
\end{equation}
 where $\pi_\theta^{\text{gen}}$ generates problems and $\pi_\theta^{\text{solve}}$ solves them. The generator is rewarded for producing problems that are challenging but solvable.

在用于推理的自对弈强化学习中，模型既生成问题也生成解答：
\begin{equation}
    \mathcal{L}_{\text{self-play}}(\theta) = \mathbb{E}_{q \sim \pi_\theta^{\text{gen}}} \mathbb{E}_{y \sim \pi_\theta^{\text{solve}}(\cdot|q)} \left[ r(y, y^*) \right]
\end{equation}
其中 $\pi_\theta^{\text{gen}}$ 生成问题，$\pi_\theta^{\text{solve}}$ 解答问题。生成器因生成具有挑战性但可解的问题而获得奖励。

\subsection{Reinforcement Learning from Verifiable Rewards (RLVR)}
\label{subsubsec:rlvr}

\subsection{基于可验证奖励的强化学习（RLVR）}
\label{subsubsec:rlvr}

RLVR~\cite{lambert2024tulu3} is a framework that uses \textbf{ground-truth verification} as the reward signal, applicable to any domain where correctness can be automatically checked.

RLVR~\cite{lambert2024tulu3} 是一个使用 \textbf{真实验证} 作为奖励信号的框架，适用于任何可以自动检查正确性的领域。

\paragraph{Verifiable Domains}
\label{verifiable-domains}

\paragraph{可验证领域}
\label{verifiable-domains}

\begin{itemize}
  \item \textbf{Mathematics}: Symbolic verification via SymPy, Lean, or Isabelle
  \item \textbf{Code}: Unit test execution
  \item \textbf{Formal logic}: Proof checking
  \item \textbf{Factual QA}: Database lookup
  \item \textbf{Games}: Win/loss outcome
\end{itemize}

\begin{itemize}
  \item \textbf{数学}：通过 SymPy、Lean 或 Isabelle 进行符号验证
  \item \textbf{代码}：单元测试执行
  \item \textbf{形式逻辑}：证明检查
  \item \textbf{事实问答}：数据库查询
  \item \textbf{游戏}：胜负结果
\end{itemize}

\paragraph{RLVR Objective}
\label{rlvr-objective}

\paragraph{RLVR 目标}
\label{rlvr-objective}

\begin{equation}
    \mathcal{L}_{\text{RLVR}}(\theta) = -\mathbb{E}_{(q, y^*) \sim \mathcal{D}} \mathbb{E}_{y \sim \pi_\theta(\cdot|q)} \left[ \text{verify}(y, y^*) \right] + \beta \mathbb{D}_{\mathrm{KL}}\!\left[\pi_\theta \,\|\, \pi_{\text{ref}}\right]
\end{equation}

\begin{equation}
    \mathcal{L}_{\text{RLVR}}(\theta) = -\mathbb{E}_{(q, y^*) \sim \mathcal{D}} \mathbb{E}_{y \sim \pi_\theta(\cdot|q)} \left[ \text{verify}(y, y^*) \right] + \beta \mathbb{D}_{\mathrm{KL}}\!\left[\pi_\theta \,\|\, \pi_{\text{ref}}\right]
\end{equation}

The key advantage of RLVR over RLHF is the \textbf{absence of reward model error}: since the reward is computed by a deterministic verifier rather than a learned model, there is no reward hacking against a flawed reward model. The only failure mode is if the model finds solutions that pass verification but are not genuinely correct (e.g., exploiting test case weaknesses in code evaluation).

RLVR 相比 RLHF 的关键优势在于 \textbf{没有奖励模型误差}：由于奖励是由确定性验证器而非学习模型计算，因此不存在针对有缺陷奖励模型的奖励作弊（reward hacking）。唯一的失败模式是模型找到通过验证但并非真正正确的解（例如，在代码评估中利用测试用例的弱点）。

\begin{examplebox}[RLVR for Code: Reward Hacking Challenges]
In code generation, the verifier is a test suite. A model trained with RLVR can learn to:

\begin{examplebox}[RLVR 用于代码：奖励作弊挑战]
在代码生成中，验证器是一个测试套件。经过 RLVR 训练的模型可能会学会：

\begin{itemize}
  \item \textbf{Hardcode test outputs}: Return the expected output for each test input without implementing the actual algorithm
  \item \textbf{Exploit weak tests}: Pass all provided tests while failing on edge cases
\end{itemize}

\begin{itemize}
  \item \textbf{硬编码测试输出}：为每个测试输入返回预期输出，而不实现实际算法
  \item \textbf{利用弱测试}：通过所有提供的测试，但在边缘情况下失败
\end{itemize}

Mitigations include: using large, diverse test suites; including adversarial test cases; using execution-based rewards that penalize hardcoding (e.g., checking that the solution runs in $O(n \log n)$ time).
\end{examplebox}

缓解措施包括：使用大型、多样化的测试套件；包含对抗性测试用例；使用基于执行的奖励来惩罚硬编码（例如，检查解是否在 $O(n \log n)$ 时间内运行）。
\end{examplebox}

\subsection{Journey Learning}
\label{journey-learning}

\subsection{旅程学习（Journey Learning）}
\label{journey-learning}

## Journey Learning
## Journey Learning（旅程学习）

Journey Learning~\cite{qin2024o1journey} proposes training on the \textbf{full reasoning trajectory}, including failed attempts and corrections, rather than only successful final solutions.
Journey Learning（旅程学习）~\cite{qin2024o1journey} 提出在\textbf{完整推理轨迹}上进行训练，包括失败的尝试和修正，而不仅仅是成功的最终解决方案。

\paragraph{Motivation}
\paragraph{动机}

\label{motivation}

Standard rejection sampling discards failed attempts. But failed attempts contain valuable information:
标准拒绝采样丢弃了失败尝试。但失败尝试含有宝贵信息：

\begin{itemize}
  \item Which approaches don’t work (negative examples)
  \item 哪些方法不奏效（负面示例）
  \item How to recognize and recover from errors (correction patterns)
  \item 如何识别并从错误中恢复（修正模式）
  \item The structure of the problem space (exploration data)
  \item 问题空间的结构（探索数据）
\end{itemize}

\paragraph{Journey Learning Objective}
\paragraph{旅程学习目标}

\label{journey-learning-objective}

Given a trajectory $\tau = (s_0, a_0, s_1, a_1, \ldots, s_T)$ that may include backtracking: 
给定一个可能包含回溯的轨迹 $\tau = (s_0, a_0, s_1, a_1, \ldots, s_T)$：
\begin{equation}
    \mathcal{L}_{\text{journey}}(\theta) = -\sum_{t=0}^{T} w_t \log \pi_\theta(a_t \mid s_t)
\end{equation}
 where the weights $w_t$ are designed to emphasize:
其中权重 $w_t$ 被设计用来强调：

\begin{itemize}
  \item Steps that lead to eventual success ($w_t > 1$)
  \item 通往最终成功的步骤（$w_t > 1$）
  \item Correction steps after errors ($w_t > 1$)
  \item 错误后的修正步骤（$w_t > 1$）
  \item Steps in failed branches ($w_t < 1$, but $> 0$)
  \item 失败分支中的步骤（$w_t < 1$，但 $> 0$）
\end{itemize}

\subsection{Quiet-STaR: Reasoning at Every Token}
\subsection{Quiet-STaR（安静-STaR）：在每个token进行推理}

\label{quiet-star-reasoning-at-every-token}

Quiet-STaR~\cite{zelikman2024quietstar} extends the reasoning paradigm to \textbf{every token position}: rather than generating a reasoning chain only before the final answer, the model generates a ``thought'' at every token position.
Quiet-STaR（安静-STaR）~\cite{zelikman2024quietstar} 将推理范式扩展到\textbf{每个token位置}：模型不是在最终答案之前仅生成一个推理链，而是在每个token位置生成一个“思考”。

\paragraph{Formulation}
\paragraph{形式化描述}

\label{formulation}

For each token position $t$, the model generates a hidden thought $z_t$ before predicting the next token $x_{t+1}$: 
对于每个token位置 $t$，模型在预测下一个token $x_{t+1}$ 之前生成一个隐藏思考 $z_t$：
\begin{equation}
    P(x_{t+1} \mid x_{\leq t}) = \mathbb{E}_{z_t \sim \pi_\theta(\cdot | x_{\leq t})} \left[ \pi_\theta(x_{t+1} \mid x_{\leq t}, z_t) \right]
\end{equation}

In practice, this is approximated by mixing the predictions with and without the thought: 
在实践中，这通过混合有思考和无思考的预测来近似：
\begin{equation}
    P(x_{t+1} \mid x_{\leq t}) = \alpha \cdot \pi_\theta(x_{t+1} \mid x_{\leq t}, z_t) + (1-\alpha) \cdot \pi_\theta(x_{t+1} \mid x_{\leq t})
\end{equation}

\paragraph{Training with REINFORCE}
\paragraph{使用REINFORCE（强化策略梯度）进行训练}

\label{training-with-reinforce}

Since the thought $z_t$ is a discrete latent variable, the gradient is estimated using REINFORCE: 
由于思考 $z_t$ 是一个离散隐变量，梯度使用REINFORCE（强化策略梯度）进行估计：
\begin{equation}
    \nabla_\theta \mathcal{L}_{\text{QS}} = \mathbb{E}_{z_t} \left[ \nabla_\theta \log \pi_\theta(z_t \mid x_{\leq t}) \cdot \left( \log P(x_{t+1} \mid x_{\leq t}, z_t) - b_t \right) \right]
\end{equation}
 where $b_t$ is a baseline (e.g., the no-thought prediction $\log \pi_\theta(x_{t+1} \mid x_{\leq t})$).
其中 $b_t$ 是一个基线（例如，无思考预测 $\log \pi_\theta(x_{t+1} \mid x_{\leq t})$）。

\begin{warningbox}[Computational Cost of Quiet-STaR]
\begin{warningbox}[Quiet-STaR的计算成本]

Quiet-STaR increases inference cost by a factor of $L_z + 1$ where $L_z$ is the thought length, applied at \emph{every} token position. For a sequence of length $T$ with thoughts of length $L_z = 8$, this is a $9\times$ increase in compute. This makes Quiet-STaR impractical for long sequences without significant engineering optimizations (e.g., speculative decoding for thoughts, caching).
Quiet-STaR将推理成本增加 $L_z + 1$ 倍，其中 $L_z$ 是思考长度，应用于\emph{每个}token位置。对于长度为 $T$ 且思考长度 $L_z = 8$ 的序列，这意味着计算量增加 $9\times$。这使得Quiet-STaR在缺乏显著工程优化（例如，对思考进行推测解码、缓存）的情况下，对于长序列不实用。

\end{warningbox}
\end{warningbox}

\section{Scaling Laws for Reasoning}
\section{推理的缩放定律（Scaling Laws）}

\label{subsec:reasoning_scaling}

Recent work~\cite{snell2024scaling, wu2024empirical} has established that test-time compute scales predictably with reasoning performance, extending the classical scaling laws~\cite{kaplan2020scaling} into the inference regime.
近期工作~\cite{snell2024scaling, wu2024empirical} 已经证实，测试时计算量随推理性能可预测地扩展，将经典的缩放定律（scaling laws）~\cite{kaplan2020scaling} 延伸到了推理领域。

\subsection{Training Compute vs.~Test-Time Compute Tradeoff}
\subsection{训练计算量与测试时计算量的权衡}

\label{training-compute-vs.-test-time-compute-tradeoff}

The fundamental scaling question for reasoning models is: \textbf{given a fixed total compute budget $C_{\text{total}} = C_{\text{train}} + N \cdot C_{\text{test}}$ (where $N$ is the number of queries), how should compute be allocated?}
推理模型的根本缩放问题是：\textbf{给定固定的总计算预算 $C_{\text{total}} = C_{\text{train}} + N \cdot C_{\text{test}}$（其中 $N$ 是查询数量），应如何分配计算？}

Let $\mathcal{A}(C_{\text{train}}, C_{\text{test}})$ denote the accuracy of a model trained with $C_{\text{train}}$ FLOPs and given $C_{\text{test}}$ inference FLOPs per query. Empirically:
令 $\mathcal{A}(C_{\text{train}}, C_{\text{test}})$ 表示使用 $C_{\text{train}}$ FLOPs训练且每个查询给定 $C_{\text{test}}$ 推理FLOPs的模型的准确率。根据经验：

\begin{equation}
    \mathcal{A}(C_{\text{train}}, C_{\text{test}}) \approx 1 - \exp\!\left(-a \cdot C_{\text{train}}^{\alpha} \cdot C_{\text{test}}^{\beta}\right)
\end{equation}

for constants $a, \alpha, \beta > 0$. The optimal allocation for a fixed total budget $C_{\text{total}}$ satisfies the condition that marginal return per FLOP is equalized between training and inference: 
其中常数 $a, \alpha, \beta > 0$。对于固定总预算 $C_{\text{total}}$，最优分配满足训练和推理之间每FLOP边际收益相等的条件：
\begin{equation}
    \frac{\partial \mathcal{A}}{\partial C_{\text{train}}} = \frac{1}{N} \cdot \frac{\partial \mathcal{A}}{\partial C_{\text{test}}}
\end{equation}

Intuitively: one FLOP of training benefits all $N$ queries, while one FLOP of test-time benefits only one query. At the optimum, the per-query marginal value of test-time compute is $N$ times larger than training compute (because training is amortized). Applying this to Eq.~[eq:reasoning\_scaling\_law] gives the optimal training compute fraction: 
直观上：一个FLOP的训练受益于所有 $N$ 个查询，而一个FLOP的测试时计算仅受益于一个查询。在最优状态下，每个查询的测试时计算边际值是训练计算边际值的 $N$ 倍（因为训练成本被分摊）。将此应用于方程[eq:reasoning\_scaling\_law]得到最优训练计算比例：
\begin{equation}
    \frac{C_{\text{train}}^*}{C_{\text{total}}} = \frac{\alpha}{\alpha + \beta}
\end{equation}

For the specific budget structure $C_{\text{total}} = C_{\text{train}} + N \cdot C_{\text{test}}$, this fraction is independent of $N$ under the multiplicative accuracy model. However, in practice $\alpha$ and $\beta$ are problem-dependent: for high-volume deployments (large $N$), even small improvements in the base model dominate, favoring training investment. For low-volume, high-stakes queries (small $N$), test-time compute is more cost-effective.
对于特定的预算结构 $C_{\text{total}} = C_{\text{train}} + N \cdot C_{\text{test}}$，在乘法准确率模型下，此比例与 $N$ 无关。然而，在实践中 $\alpha$ 和 $\beta$ 是依赖于问题的：对于大规模部署（大 $N$），基础模型即使微小的改进也占主导地位，因此倾向于训练投入。对于小规模、高风险的查询（小 $N$），测试时计算更具成本效益。

\subsection{When to Invest in Longer Chains vs.~Better Base Models}
\subsection{何时投资于更长的链 vs. 更好的基础模型}

\label{when-to-invest-in-longer-chains-vs.-better-base-models}

\begin{keybox}[Reasoning Chain Length vs. Model Capacity]
\begin{keybox}[推理链长度 vs. 模型容量]

The optimal reasoning chain length $L^*$ for a model of capacity $C$ on a problem of difficulty $D$ satisfies: 
对于容量为 $C$ 的模型在难度为 $D$ 的问题上，最优推理链长度 $L^*$ 满足：
\begin{equation}
    L^* \propto \frac{D}{C^{\gamma}}
\end{equation}
 for some $\gamma > 0$. This implies:
其中 $\gamma > 0$。这意味着：

\begin{itemize}
  \item \textbf{Hard problems} require longer chains regardless of model size
  \item \textbf{困难问题}无论模型大小都需要更长的链
  \item \textbf{Larger models} require shorter chains for the same problem difficulty
  \item \textbf{更大的模型}对于相同难度的问题需要更短的链
  \item \textbf{Diminishing returns}: Beyond $L^*$, additional tokens provide no benefit and may hurt (overthinking)
  \item \textbf{收益递减}：超过 $L^*$ 后，额外的token没有益处，反而可能有害（过度思考）
\end{itemize}
\end{keybox}

The ``overthinking'' phenomenon---where models with very long reasoning chains perform \emph{worse} than those with moderate chains---has been empirically observed and is attributed to:
“过度思考”现象——即具有非常长推理链的模型表现\emph{更差}于中等长度链的模型——已被经验观察到，并归因于：

\begin{itemize}
  \item Accumulation of errors in long chains (error propagation)
  \item 长链中错误的累积（错误传播）
  \item Distraction from the main solution path
  \item 偏离主要解决路径
  \item Overconfidence in incorrect intermediate conclusions
  \item 对错误中间结论的过度自信
\end{itemize}

\subsection{Optimal Token Budget Allocation}
\subsection{最优Token预算分配}

\label{optimal-token-budget-allocation}

For a model with a fixed token budget $B$, the allocation between ``thinking'' tokens $T_{\text{think}}$ and ``answering'' tokens $T_{\text{answer}}$ should satisfy: 
对于具有固定token预算 $B$ 的模型，在“思考”token $T_{\text{think}}$ 和“回答”token $T_{\text{answer}}$ 之间的分配应满足：
\begin{equation}
    T_{\text{think}}^* = \arg\max_{T} \mathcal{A}(T, B - T)
\end{equation}

Empirically, the optimal split is problem-dependent:
根据经验，最优分配取决于问题：

\begin{itemize}
  \item \textbf{Simple problems}: $T_{\text{think}}^* / B \approx 0.3$ (30\% thinking)
  \item \textbf{简单问题}：$T_{\text{think}}^* / B \approx 0.3$（30%思考）
  \item \textbf{Hard problems}: $T_{\text{think}}^* / B \approx 0.8$ (80\% thinking)
  \item \textbf{困难问题}：$T_{\text{think}}^* / B \approx 0.8$（80%思考）
  \item \textbf{Very hard problems}: $T_{\text{think}}^* / B \approx 0.95$ (95\% thinking, minimal answer)
  \item \textbf{很难问题}：$T_{\text{think}}^* / B \approx 0.95$（95%思考，最小化回答）
\end{itemize}

This motivates \textbf{adaptive thinking budgets}: allocating more tokens to harder problems, which can be estimated by the model’s uncertainty on initial solution attempts.
这激发了\textbf{自适应思考预算}：将更多token分配给更困难的问题，这可以通过模型对初始解决尝试的不确定性来估计。

\section{Comparison of Reasoning Models}
\section{推理模型的比较}

\label{subsec:reasoning_comparison}

\begin{table}[ht!]
\centering
\caption{Comparison of training methodologies for reasoning models.}
\caption{推理模型训练方法对比。}
\begin{tabular}{@{}lp{2.1cm}p{2.1cm}p{2.1cm}p{2.1cm}p{2.1cm}p{2.1cm}@{}}
\toprule
\textbf{Method} & \textbf{PRM} & \textbf{ORM} & \textbf{MCTS} & \textbf{Distill} & \textbf{Tool} & \textbf{Open} \\
\textbf{方法} & \textbf{过程奖励模型} & \textbf{结果奖励模型} & \textbf{蒙特卡洛树搜索} & \textbf{蒸馏} & \textbf{工具} & \textbf{开放} \\
\midrule
OpenAI o1/o3 & \checkmark{} & \checkmark{} & Unknown & -- & \checkmark{} & $\times$ \\
OpenAI o1/o3 & \checkmark{} & \checkmark{} & 未知 & -- & \checkmark{} & $\times$ \\
DeepSeek-R1 & $\times$ & \checkmark{} & $\times$ & \checkmark{} & $\times$ & \checkmark{} \\
DeepSeek-R1 & $\times$ & \checkmark{} & $\times$ & \checkmark{} & $\times$ & \checkmark{} \\
QwQ / Qwen3 & Partial & \checkmark{} & $\times$ & $\times$ & \checkmark{} & \checkmark{} \\
QwQ / Qwen3 & 部分 & \checkmark{} & $\times$ & $\times$ & \checkmark{} & \checkmark{} \\
AlphaProof & \checkmark{} & \checkmark{} & \checkmark{} & -- & \checkmark{} & $\times$ \\
AlphaProof & \checkmark{} & \checkmark{} & \checkmark{} & -- & \checkmark{} & $\times$ \\
Math-Shepherd & \checkmark{} & \checkmark{} & $\times$ & -- & $\times$ & \checkmark{} \\
Math-Shepherd & \checkmark{} & \checkmark{} & $\times$ & -- & $\times$ & \checkmark{} \\
STaR / Quiet-STaR & $\times$ & \checkmark{} & $\times$ & -- & $\times$ & \checkmark{} \\
STaR / Quiet-STaR & $\times$ & \checkmark{} & $\times$ & -- & $\times$ & \checkmark{} \\
\bottomrule
\end{tabular}
\end{table}

\section{Summary and Open Problems}
\section{总结与开放问题}
\label{subsec:reasoning_summary}

The field of RL for reasoning models has advanced remarkably rapidly. Several key lessons have emerged:
强化学习用于推理模型的领域发展极为迅速。以下是一些关键经验教训：

\begin{enumerate}
  \item \textbf{Verifiable rewards are sufficient}: For domains with ground-truth verification (math, code), outcome-only rewards are sufficient for RL to discover sophisticated reasoning strategies, without requiring process reward models.
  \item \textbf{可验证的奖励已足够}：对于具有真实值验证的领域（数学、代码），仅使用结果奖励就足以让强化学习发现复杂的推理策略，无需过程奖励模型。
  \item \textbf{Test-time compute is a new axis}: Reasoning models introduce a new dimension of scaling---inference compute---that is roughly substitutable with training compute for hard reasoning tasks.
  \item \textbf{测试时计算是一个新维度}：推理模型引入了一个新的扩展维度——推理计算——对于困难的推理任务，它大致可与训练计算相互替代。
  \item \textbf{Distillation is highly effective}: Large reasoning models can transfer their capabilities to much smaller models via supervised fine-tuning on generated chains, often outperforming direct RL training of small models.
  \item \textbf{蒸馏非常有效}：大型推理模型可以通过对生成的推理链进行监督微调，将其能力迁移至更小的模型，通常优于直接对小型模型进行强化学习训练。
  \item \textbf{Emergent meta-cognition}: RL training on reasoning tasks produces emergent self-correction and verification behaviors that were not explicitly trained.
  \item \textbf{涌现的元认知}：在推理任务上进行强化学习训练会涌现出自我纠正和验证行为，而这些行为并未被显式训练过。
\end{enumerate}

\begin{questionbox}[Open Problems in RL for Reasoning]
\begin{questionbox}[强化学习用于推理的开放问题]
Several fundamental questions remain open:
几个基本问题依然悬而未决：

\begin{itemize}
  \item \textbf{Generalization}: Do reasoning capabilities trained on math/code transfer to other domains (scientific reasoning, planning, social reasoning)?
  \item \textbf{泛化性}：在数学/代码上训练的推理能力能否迁移到其他领域（科学推理、规划、社会推理）？
  \item \textbf{Faithfulness}: Are the generated reasoning chains causally responsible for the final answer, or are they post-hoc rationalizations?
  \item \textbf{保真性}：生成的推理链是否在因果上对最终答案负责，还是事后合理化？
  \item \textbf{Optimal search}: What is the optimal search strategy during inference---beam search, MCTS, or something else?
  \item \textbf{最优搜索}：推理过程中的最优搜索策略是什么——束搜索、蒙特卡洛树搜索，还是其他方法？
  \item \textbf{Reward design}: For domains without ground-truth verifiers, how can we design reliable reward signals for reasoning?
  \item \textbf{奖励设计}：对于没有真实值验证器的领域，我们如何为推理设计可靠的奖励信号？
  \item \textbf{Overthinking}: How can models learn to allocate the \emph{right} amount of thinking---neither too little nor too much?
  \item \textbf{过度思考}：模型如何学会分配\emph{恰到好处}的思考量——既不过少也不过多？
  \item \textbf{Compositional reasoning}: Can RL-trained reasoning models solve problems that require composing multiple distinct reasoning skills?
  \item \textbf{组合推理}：经过强化学习训练的推理模型能否解决需要组合多种不同推理技能的问题？
\end{itemize}
\end{questionbox}

The development of reasoning models represents a paradigm shift: from language models that \emph{know} things to language models that can \emph{figure things out}. The RL methods described in this section are the primary engine driving this shift, and their continued development is likely to be a central focus of AI research in the coming years.
推理模型的发展代表了一种范式转变：从\emph{知道}事物的语言模型转向能够\emph{弄明白}事物的语言模型。本节描述的强化学习方法正是驱动这一转变的主要引擎，其持续发展很可能成为未来几年人工智能研究的核心焦点。

\part{Evaluation}
\part{评估}