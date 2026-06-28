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
---

## \chapter{LLM Evaluation}
## \chapter{LLM 评估（大语言模型评估）}

Evaluation is the backbone of any rigorous machine learning pipeline, yet it is perhaps the most underappreciated component in the development of large language models. Unlike classical supervised learning, where a held-out test set with ground-truth labels provides a clean signal, evaluating LLMs requires grappling with open-ended generation, subjective quality judgments, multi-step reasoning chains, and the ever-present risk of benchmark contamination. This section provides a systematic treatment of the evaluation landscape: from the taxonomy of evaluation types and the mechanics of human annotation, through the mathematics of ranking metrics and the practicalities of LLM-as-judge, to the pitfalls that silently corrupt evaluation pipelines.
评估是任何严谨机器学习流程的支柱，然而它可能是大语言模型开发中最被低估的环节。与经典监督学习（其中保留的测试集和真实标签提供清晰的信号）不同，评估 LLM 需要应对开放式生成、主观质量判断、多步推理链以及始终存在的基准污染风险。本节系统性地阐述了评估领域：从评估类型的分类法和人工标注的机制，到排名指标的数学原理和 LLM-as-judge（大模型作为裁判）的实践，再到那些悄然破坏评估流程的陷阱。

\begin{keybox}[Why Evaluation is Hard for LLMs]
\begin{keybox}[为什么 LLM 评估是困难的]

\textbf{Three fundamental challenges} distinguish LLM evaluation from classical ML evaluation:
\textbf{三大根本挑战} 将 LLM 评估与经典机器学习评估区分开来：

\begin{enumerate}
  \item \textbf{Output space is unbounded.} A language model can produce any string; there is rarely a single correct answer.
  \item \textbf{输出空间是无界的。}语言模型可以生成任意字符串；很少存在唯一正确答案。
  \item \textbf{Quality is multidimensional.} Helpfulness, factuality, safety, coherence, and style are distinct axes that may trade off against each other.
  \item \textbf{质量是多维的。}有用性、事实性、安全性、连贯性和风格是不同的维度，它们之间可能相互权衡。
  \item \textbf{Evaluation is itself a language task.} Judging whether a response is good requires understanding, which means evaluation is susceptible to the same failure modes as generation.
  \item \textbf{评估本身也是一项语言任务。}判断一个回复是否良好需要理解，这意味着评估容易受到与生成相同的故障模式的影响。
\end{enumerate}
\end{keybox}

\section{Evaluation Scheme Design}
\section{评估方案设计}
\label{subsec:eval-scheme}

Before collecting a single data point, practitioners must decide \emph{what} to measure and \emph{how} to measure it. A principled taxonomy prevents the common mistake of choosing metrics by convenience rather than by alignment with the deployment objective.
在收集任何一个数据点之前，从业者必须决定\emph{衡量什么}以及\emph{如何衡量}。一个原则性的分类法可以防止常见的错误：即为了方便而非与部署目标对齐来选择指标。

\subsection{Taxonomy of Evaluation Types}
\subsection{评估类型分类法}
\label{taxonomy-of-evaluation-types}

\paragraph{Intrinsic vs.~Extrinsic Evaluation.}
\paragraph{内在评估 vs. 外在评估。}
\label{intrinsic-vs.-extrinsic-evaluation.}

\emph{Intrinsic} evaluation measures properties of the model output in isolation, without reference to a downstream application. Perplexity on a held-out corpus, BLEU score against reference translations, and pass@$k$ on coding benchmarks are all intrinsic. \emph{Extrinsic} evaluation measures the impact of the model on a real-world task or system: does integrating the LLM into a customer-service pipeline reduce ticket escalation rates? Does the coding assistant increase developer velocity?
\emph{内在评估}孤立地衡量模型输出的属性，不参考下游应用。在保留语料库上的困惑度（Perplexity）、与参考翻译对照的 BLEU 分数、以及在编程基准上的 pass@$k$ 都属于内在评估。\emph{外在评估}衡量模型对真实任务或系统的影响：将 LLM 集成到客服流程中是否能降低工单升级率？编程助手是否能提高开发者的速度？

\begin{intuitionbox}[The Intrinsic–Extrinsic Gap]
\begin{intuitionbox}[内在-外在差距]

Intrinsic metrics are cheap and reproducible but often poorly correlated with real-world utility. A model with lower perplexity is not necessarily more helpful. Extrinsic metrics are expensive and slow but directly measure what we care about. A mature evaluation strategy uses intrinsic metrics for rapid iteration and extrinsic metrics for final validation.
内在指标成本低、可重复，但通常与实际效用相关性较差。一个困惑度较低的模型不一定更有用。外在指标成本高、速度慢，但直接衡量我们所关心的内容。成熟的评估策略使用内在指标进行快速迭代，使用外在指标进行最终验证。
\end{intuitionbox}

\paragraph{Automatic vs.~Human Evaluation.}
\paragraph{自动评估 vs. 人工评估。}
\label{automatic-vs.-human-evaluation.}

\emph{Automatic} evaluation uses deterministic functions (BLEU, exact match) or learned models (BERTScore, LLM-as-judge) to score outputs without human involvement. \emph{Human} evaluation involves annotators rating or ranking model outputs. Table~\ref{tab:eval-taxonomy} summarises the trade-offs.
\emph{自动评估}使用确定性函数（BLEU、精确匹配）或学习模型（BERTScore、LLM-as-judge）对输出进行评分，无需人工参与。\emph{人工评估}由标注者评分或对模型输出进行排名。表~\ref{tab:eval-taxonomy} 总结了权衡。

\begin{table}[ht!]
\centering
\caption{Taxonomy of evaluation approaches with key trade-offs.}
\caption{评估方法分类及关键权衡}
\label{tab:eval-taxonomy}
\begin{tabular}{@{}lp{3cm}p{3.2cm}p{3.2cm}p{3.5cm}@{}}
\toprule
\textbf{Type} & \textbf{Cost} & \textbf{Speed} & \textbf{Reproducibility} & \textbf{Validity} \\
\textbf{类型} & \textbf{成本} & \textbf{速度} & \textbf{可复现性} & \textbf{有效性} \\
\midrule
Automatic (rule-based) & Very low & Very fast & Perfect & Low--Medium \\
自动（基于规则） & 非常低 & 非常快 & 完美 & 低-中 \\
Automatic (model-based) & Low & Fast & High & Medium--High \\
自动（基于模型） & 低 & 快 & 高 & 中-高 \\
Crowdsourced human & Medium & Days & Medium & Medium \\
众包人工 & 中 & 数天 & 中 & 中 \\
Expert human & High & Weeks & Low--Medium & High \\
专家人工 & 高 & 数周 & 低-中 & 高 \\
Extrinsic / A/B test & Very high & Months & Low & Very high \\
外在 / A/B 测试 & 非常高 & 数月 & 低 & 非常高 \\
\bottomrule
\end{tabular}
\end{table}

\paragraph{Reference-Based vs.~Reference-Free Evaluation.}
\paragraph{基于参考的评估 vs. 无参考的评估。}
\label{reference-based-vs.-reference-free-evaluation.}

Reference-based metrics (BLEU, ROUGE, BERTScore) compare model output to one or more gold-standard references. Reference-free metrics (perplexity, LLM-as-judge, human preference) assess quality without a reference. Reference-free approaches are essential when the output space is too large for exhaustive reference collection, as in open-ended dialogue.
基于参考的指标（BLEU、ROUGE、BERTScore）将模型输出与一个或多个黄金标准参考进行比较。无参考指标（困惑度、LLM-as-judge、人工偏好）无需参考即可评估质量。当输出空间太大而无法收集详尽的参考时（例如开放式对话），无参考方法至关重要。

\subsection{When to Use What}
\subsection{何时使用何种评估}
\label{when-to-use-what}

\begin{examplebox}[Evaluation Strategy for a Dialogue Assistant]
\begin{examplebox}[对话助手的评估策略]

\textbf{Development phase:} Use automatic metrics (perplexity, ROUGE on summarisation sub-tasks, pass@$k$ on tool-use) for rapid iteration. Run nightly benchmarks on standard suites (MMLU, HellaSwag, HumanEval).
\textbf{开发阶段：}使用自动指标（困惑度、摘要子任务的 ROUGE、工具使用的 pass@$k$）进行快速迭代。在标准套件（MMLU、HellaSwag、HumanEval）上运行夜间基准测试。

\textbf{Pre-release phase:} Conduct a human preference study comparing the new model to the previous checkpoint. Use LLM-as-judge for scalable pairwise comparison on a diverse prompt set.
\textbf{预发布阶段：}进行人工偏好研究，将新模型与之前的检查点进行比较。使用 LLM-as-judge 在多样化的提示集上进行可扩展的成对比较。

\textbf{Post-release phase:} Monitor extrinsic metrics (user satisfaction scores, task completion rates) and watch for distribution shift in production prompts.
\textbf{发布后阶段：}监控外在指标（用户满意度分数、任务完成率），并留意生产环境中提示的分布偏移。
\end{examplebox}

A useful decision framework:
一个有用的决策框架：

\begin{itemize}
  \item If the task has a clear correct answer (math, code, factual QA): use exact match or execution-based metrics.
  \item 如果任务有明确的正确答案（数学、代码、事实问答）：使用精确匹配或基于执行的指标。
  \item If the task is open-ended but has reference outputs: use reference-based metrics as a lower bound, supplement with LLM-as-judge.
  \item 如果任务是开放式的但有参考输出：使用基于参考的指标作为下限，并用 LLM-as-judge 补充。
  \item If the task is subjective (helpfulness, tone, creativity): use human evaluation or a well-calibrated LLM judge.
  \item 如果任务是主观的（有用性、语气、创造力）：使用人工评估或经过良好校准的 LLM 裁判。
  \item If the task involves multi-step agent behaviour: use task success rate and trajectory efficiency (Section~\ref{subsec:agentic-metrics}).
  \item 如果任务涉及多步智能体行为：使用任务成功率和轨迹效率（第~\ref{subsec:agentic-metrics}节）。
\end{itemize}

\section{Data Collection for Evaluation}
\section{评估数据收集}
\label{subsec:data-collection}

High-quality evaluation data is the foundation of trustworthy benchmarks. This section covers the design of human annotation pipelines, statistical measures of annotation quality, and the choice between crowdsourcing and expert annotation.
高质量的评估数据是可信基准的基础。本节涵盖人工标注流程的设计、标注质量的统计度量，以及众包与专家标注之间的选择。

\subsection{Human Annotation Pipelines}
\subsection{人工标注流程}
\label{human-annotation-pipelines}

A robust annotation pipeline consists of five stages:
一个稳健的标注流程包含五个阶段：

\begin{enumerate}
  \item \textbf{Task definition.} Specify the annotation task precisely: what is being rated, on what scale, and with what criteria. Ambiguity at this stage propagates into noisy labels.
  \item \textbf{任务定义。}精确指定标注任务：评什么内容、使用什么尺度、依据什么标准。此阶段的歧义会传播成噪声标签。
  \item \textbf{Guideline development.} Write annotation guidelines with worked examples covering edge cases. Iterate with a small pilot group before full deployment.
  \item \textbf{指南制定。}编写标注指南，包含覆盖边缘案例的实例。在全面部署之前与一个小型试点小组进行迭代。
  \item \textbf{Annotator recruitment and training.} Select annotators with appropriate background knowledge. Conduct a calibration session where annotators label the same examples and discuss disagreements.
  \item \textbf{标注者招募与培训。}选择具有适当背景知识的标注者。举办校准会议，让标注者对相同示例进行标注并讨论分歧。
  \item \textbf{Quality control.} Embed gold-standard examples with known labels into the annotation queue. Flag annotators whose accuracy on gold examples falls below a threshold.
  \item \textbf{质量控制。}将带有已知标签的黄金标准示例嵌入标注队列中。对黄金示例准确率低于阈值的标注者进行标记。
  \item \textbf{Aggregation.} Combine multiple annotations per item using majority vote, averaging, or a probabilistic model (e.g., Dawid--Skene).
  \item \textbf{聚合。}通过多数投票、平均或概率模型（例如 Dawid--Skene）合并每个项目的多个标注。
\end{enumerate}

\subsection{Inter-Annotator Agreement}
\subsection{标注者间一致性}
\label{inter-annotator-agreement}

Raw agreement (fraction of items where all annotators agree) is an inadequate measure because it does not account for chance agreement. Two standard chance-corrected measures are Cohen’s $\kappa$~\cite{cohen1960coefficient} (two annotators) and Fleiss’ $\kappa$~\cite{fleiss1971measuring} (multiple annotators).
原始一致性（所有标注者一致同意的项目比例）是一个不充分的度量，因为它没有考虑随机一致性。两种标准的校正了随机一致性的度量是 Cohen 的 $\kappa$~\cite{cohen1960coefficient}（适用于两位标注者）和 Fleiss 的 $\kappa$~\cite{fleiss1971measuring}（适用于多位标注者）。

\paragraph{Cohen’s Kappa.}
\paragraph{Cohen 的 Kappa。}
\label{cohens-kappa.}

## Evaluation Scheme Design
## 评估方案设计

Given two annotators labelling $N$ items into $k$ categories, let $p_o$ be the observed agreement and $p_e$ be the expected agreement under independence: 
给定两个标注者对 $N$ 个项进行 $k$ 类别标注，设 $p_o$ 为观测一致率，$p_e$ 为独立假设下的期望一致率：
\begin{equation}
    \kappa = \frac{p_o - p_e}{1 - p_e}
\label{eq:cohens-kappa}
\end{equation}
 where 
其中
\begin{equation}
    p_o = \frac{1}{N}\sum_{i=1}^{N} \mathbf{1}[\text{annotator 1 agrees with annotator 2 on item } i]
\end{equation}
 and 
以及
\begin{equation}
    p_e = \sum_{c=1}^{k} p_{1c} \cdot p_{2c}
\end{equation}
 with $p_{jc}$ being the proportion of items assigned to category $c$ by annotator $j$. Cohen’s $\kappa$ ranges from $-1$ (perfect disagreement) through $0$ (chance agreement) to $1$ (perfect agreement). Values above $0.6$ are generally considered acceptable; above $0.8$ is strong agreement.
其中 $p_{jc}$ 是标注者 $j$ 将项分配给类别 $c$ 的比例。Cohen’s $\kappa$ 的取值范围从 $-1$（完全不一致）经 $0$（随机一致）到 $1$（完全一致）。大于 $0.6$ 的值通常认为可接受；大于 $0.8$ 则为强一致。

\paragraph{Fleiss’ Kappa.}
\paragraph{Fleiss’ Kappa（弗莱斯 Kappa）.}
\label{fleiss-kappa.}


For $n$ annotators labelling $N$ items into $k$ categories, let $n_{ij}$ be the number of annotators who assigned item $i$ to category $j$. Define: 
对于 $n$ 个标注者对 $N$ 个项进行 $k$ 类别标注，设 $n_{ij}$ 是将项 $i$ 分配给类别 $j$ 的标注者数量。定义：
\begin{equation}
    \bar{P}_i = \frac{1}{n(n-1)} \sum_{j=1}^{k} n_{ij}(n_{ij} - 1), \qquad \bar{P} = \frac{1}{N}\sum_{i=1}^{N}\bar{P}_i
\end{equation}
 
\begin{equation}
    \bar{P}_j^e = \frac{1}{Nn}\sum_{i=1}^{N} n_{ij}, \qquad P_e = \sum_{j=1}^{k} \left(\bar{P}_j^e\right)^2
\end{equation}
 
\begin{equation}
    \kappa_F = \frac{\bar{P} - P_e}{1 - P_e}
\end{equation}


\begin{warningbox}[Kappa Limitations]
\begin{warningbox}[Kappa 的局限性]
Kappa is sensitive to the prevalence of categories: when one category dominates, kappa can be low even when raw agreement is high (the \emph{kappa paradox}). For ordinal scales, weighted kappa (which penalises disagreements proportionally to their distance) is more appropriate. For LLM evaluation, where ratings are often on a 1--5 Likert scale, always report weighted kappa.
Kappa 对类别的 prevalence（流行率）敏感：当某个类别占主导时，即使原始一致率很高，kappa 也可能很低（即 \emph{kappa 悖论}）。对于有序量表，加权 kappa（按距离比例惩罚不一致）更为合适。在 LLM 评估中，评分通常采用 1--5 的 Likert 量表，应始终报告加权 kappa。
\end{warningbox}


\subsection{Annotation Guideline Design}
\subsection{标注指南设计}
\label{annotation-guideline-design}


Effective annotation guidelines share several properties:
有效的标注指南具有以下几个共同特性：

\begin{itemize}
  \item \textbf{Operationalised criteria.} Replace vague terms like ``helpful'' with concrete, observable behaviours: ``The response directly addresses the user’s question and provides all information needed to complete the stated task.''
  \item \textbf{操作化标准。} 用具体、可观察的行为替换模糊术语（如“有帮助”）： “回答直接回应用户的问题，并提供完成所述任务所需的所有信息。”
  \item \textbf{Worked examples.} Provide at least two examples per rating level, including borderline cases.
  \item \textbf{示例说明。} 每个评分等级至少提供两个示例，包括边界情况。
  \item \textbf{Decision trees.} For complex tasks, a flowchart that guides annotators through a sequence of binary decisions reduces cognitive load and improves consistency.
  \item \textbf{决策树。} 对于复杂任务，使用流程图引导标注者通过一系列二元决策，可减少认知负荷并提高一致性。
  \item \textbf{Explicit scope.} State what annotators should \emph{not} consider (e.g., ``Do not penalise for stylistic preferences; focus only on factual accuracy'').
  \item \textbf{明确范围。} 说明标注者 \emph{不应} 考虑哪些因素（例如，“不要因风格偏好而扣分；只关注事实准确性”）。
\end{itemize}


\subsection{Crowdsourcing vs.~Expert Annotation}
\subsection{众包 vs. 专家标注}
\label{crowdsourcing-vs.-expert-annotation}


\begin{table}[ht!]
\centering
\caption{Comparison of crowdsourcing and expert annotation for LLM evaluation.}
\caption{众包与专家标注在 LLM 评估中的比较。}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Dimension} & \textbf{Crowdsourcing} & \textbf{Expert Annotation} \\
\textbf{维度} & \textbf{众包} & \textbf{专家标注} \\
\midrule
Cost per item & Low (\$0.01--\$0.10) & High (\$1--\$50) \\
每项成本 & 低（\$0.01--\$0.10） & 高（\$1--\$50） \\
Throughput & Very high & Low \\
吞吐量 & 非常高 & 低 \\
Domain knowledge & Low & High \\
领域知识 & 低 & 高 \\
Consistency & Variable & High \\
一致性 & 可变 & 高 \\
Suitable tasks & Simple preference, fluency & Technical accuracy, safety \\
适用任务 & 简单偏好、流畅性 & 技术准确性、安全性 \\
Platforms & MTurk, Prolific, Scale AI & Domain specialists, in-house \\
平台 & MTurk, Prolific, Scale AI & 领域专家、内部人员 \\
Quality control & Gold examples, attention checks & Calibration sessions, peer review \\
质量控制 & 黄金样本、注意力检查 & 校准会议、同行评审 \\
\bottomrule
\end{tabular}
\end{table}


For safety-critical evaluation (e.g., detecting harmful outputs, evaluating medical advice), expert annotation is non-negotiable. For large-scale preference collection (e.g., building a reward model training set), crowdsourcing with rigorous quality control is often the only feasible option.
对于安全关键的评估（例如检测有害输出、评估医疗建议），专家标注是不可妥协的。对于大规模偏好收集（例如构建奖励模型训练集），采用严格质量控制的众包通常是唯一可行的选择。

\section{Synthetic Data Generation for Evaluation}
\section{用于评估的合成数据生成}
\label{subsec:synthetic-data}


Human annotation is expensive and slow. Synthetic data generation uses LLMs themselves to produce evaluation data at scale. This section covers the major paradigms.
人工标注昂贵且缓慢。合成数据生成利用 LLM 自身来大规模生成评估数据。本节介绍主要范式。

\subsection{LLM-as-Judge for Calibration}
\subsection{基于 LLM 作为评估者的校准}
\label{llm-as-judge-for-calibration}


When using an LLM to generate evaluation labels, calibration is essential: the judge’s scores must be aligned with human judgments. Let $h_i \in [0,1]$ be the human preference score for item $i$ and $\hat{h}_i$ be the judge’s predicted score. Calibration error is measured by the Expected Calibration Error (ECE)~\cite{guo2017calibration}: 
当使用 LLM 生成评估标签时，校准至关重要：评估者的分数必须与人类判断一致。设 $h_i \in [0,1]$ 为项 $i$ 的人类偏好分数，$\hat{h}_i$ 为评估者的预测分数。校准误差通过期望校准误差（Expected Calibration Error, ECE）~\cite{guo2017calibration} 度量：
\begin{equation}
    \text{ECE} = \sum_{b=1}^{B} \frac{|B_b|}{n} \left| \text{acc}(B_b) - \text{conf}(B_b) \right|
\end{equation}
 where $B_b$ is the $b$-th confidence bin, $\text{acc}(B_b)$ is the fraction of items in the bin where the judge agrees with humans, and $\text{conf}(B_b)$ is the mean judge confidence in that bin.
其中 $B_b$ 是第 $b$ 个置信区间，$\text{acc}(B_b)$ 是该区间内评估者与人类一致的项目比例，$\text{conf}(B_b)$ 是该区间内评估者的平均置信度。


A well-calibrated judge satisfies $\mathbb{E}[\hat{h}_i \mid \hat{h}_i = p] = p$ for all $p \in [0,1]$. Calibration can be improved by temperature scaling: replacing the judge’s raw logit $z$ with $z/T$ where $T$ is tuned on a held-out calibration set to minimise negative log-likelihood.
一个良好校准的评估者满足 $\mathbb{E}[\hat{h}_i \mid \hat{h}_i = p] = p$ 对所有 $p \in [0,1]$ 成立。可以通过温度缩放（temperature scaling）改善校准：将评估者的原始 logit $z$ 替换为 $z/T$，其中 $T$ 在保留的校准集上调整以最小化负对数似然。

\subsection{Self-Instruct}
\subsection{Self-Instruct（自指导）}
\label{self-instruct}


Self-Instruct~\cite{wang2022selfinstruct} bootstraps instruction-following data from a seed set of human-written tasks. The algorithm:
Self-Instruct~\cite{wang2022selfinstruct} 从一组人工编写的种子任务中引导生成指令遵循数据。算法如下：

\begin{enumerate}
  \item Maintain a task pool initialised with $175$ seed tasks.
  \item 维护一个初始包含 $175$ 个种子任务的任务池。
  \item Sample $8$ tasks from the pool; use them as few-shot examples to prompt the LLM to generate new tasks.
  \item 从池中采样 $8$ 个任务；将它们作为少样本示例，提示 LLM 生成新任务。
  \item Filter generated tasks: remove near-duplicates (ROUGE-L similarity $> 0.7$ with any existing task), classify as classification vs.~non-classification, and generate input--output instances.
  \item 过滤生成的任务：移除近重复项（与任何现有任务的 ROUGE-L 相似度 $> 0.7$），分类为分类任务或非分类任务，并生成输入-输出实例。
  \item Add accepted tasks to the pool.
  \item 将接受的任务添加到池中。
  \item Repeat until the desired pool size is reached.
  \item 重复直到达到所需的池大小。
\end{enumerate}


\begin{examplebox}[Self-Instruct Prompt Template]
\begin{examplebox}[Self-Instruct 提示模板]
\begin{lstlisting}[style=pythonstyle]
system_prompt = """
Come up with a series of tasks:
Task 1: {seed_task_1_instruction}
Task 2: {seed_task_2_instruction}
...
Task 8: {seed_task_8_instruction}
Task 9:"""
\end{lstlisting}


The model completes the prompt, generating a new task instruction. A separate prompt then generates input--output pairs for the new task.
模型补全提示，生成新的任务指令。随后使用另一个提示为新任务生成输入-输出对。
\end{examplebox}


\subsection{Evol-Instruct}
\subsection{Evol-Instruct（进化指导）}
\label{evol-instruct}


Evol-Instruct~\cite{xu2023wizardlm} evolves a seed instruction set by iteratively rewriting instructions to be more complex or diverse. Two evolution operators are applied:
Evol-Instruct~\cite{xu2023wizardlm} 通过迭代重写指令使其更复杂或更多样化，从而进化种子指令集。应用两种进化算子：

\begin{itemize}
  \item \textbf{In-depth evolution:} Add constraints, increase reasoning steps, concretise abstractions, deepen domain knowledge requirements.
  \item \textbf{深度进化：} 增加约束、增加推理步骤、具体化抽象概念、加深领域知识要求。
  \item \textbf{In-breadth evolution:} Generate a new instruction on a related but different topic, increasing topic diversity.
  \item \textbf{广度进化：} 在相关但不同的主题上生成新指令，增加主题多样性。
\end{itemize}


An instruction is accepted if it passes an elimination filter: the evolved instruction must not be a simple copy, must not contain ``I’m sorry'' or similar refusals, and must not be shorter than the original.
指令通过消除过滤器后才被接受：进化后的指令不能是简单的复制，不能包含“I’m sorry”或类似的拒绝语句，并且不能比原始指令更短。

\subsection{Constitutional AI Data Generation}
\subsection{Constitutional AI（宪法式 AI）数据生成}
\label{constitutional-ai-data-generation}


Constitutional AI (CAI)~\cite{bai2022constitutional} generates preference data by having the model critique and revise its own outputs according to a set of principles (the ``constitution''). The pipeline:
Constitutional AI（CAI）~\cite{bai2022constitutional} 通过让模型根据一组原则（“宪法”）对自己的输出进行批评和修订来生成偏好数据。流程如下：

\begin{enumerate}
  \item \textbf{Supervised learning phase:} Sample a harmful prompt, generate an initial response, then prompt the model to critique the response according to a constitutional principle and revise it. Use the revised response as a supervised fine-tuning target.
  \item \textbf{监督学习阶段：} 抽样一个有害提示，生成初始回复，然后提示模型根据宪法原则批评并修订该回复。将修订后的回复作为监督微调目标。
  \item \textbf{RL phase:} Generate pairs of responses (original vs.~revised), use the model to label which is more constitutional, and train a preference model on these labels. Use the preference model as a reward signal for RLHF.
  \item \textbf{强化学习阶段：} 生成回复对（原始 vs. 修订版），使用模型标记哪个更符合宪法，并基于这些标签训练偏好模型。将偏好模型作为 RLHF 的奖励信号。
\end{enumerate}


This approach generates preference data without human labelling of harmful content, reducing annotator exposure to distressing material.
这种方法无需人工标注有害内容即可生成偏好数据，减少了标注者接触令人不适的材料。

\subsection{Distillation for Evaluation Data}
\subsection{用于评估数据的蒸馏}
\label{distillation-for-evaluation-data}

## Evaluation Scheme Design
## 评估方案设计

A powerful teacher model (e.g., GPT-4) can generate high-quality evaluation data for training a smaller judge model. The distillation pipeline:
一个强大的教师模型（例如 GPT-4）可以生成高质量的评价数据，用于训练较小的评判模型。其蒸馏流程如下：

\begin{enumerate}
  \item Collect a diverse set of prompts and model responses.
  \item Use the teacher to generate detailed judgments (scores + rationales).
  \item Fine-tune a smaller model on (prompt, response, judgment) triples.
  \item Validate the student judge against held-out human annotations.
\end{enumerate}

\begin{enumerate}
  \item 收集多样化的提示词和模型响应。
  \item 使用教师模型生成详细的评判（分数+理由）。
  \item 在（提示词、响应、评判）三元组上微调一个较小的模型。
  \item 将学生评判模型与保留的人工标注进行验证。
\end{enumerate}

\begin{warningbox}[Distillation Bias]
A student judge distilled from a single teacher inherits the teacher’s biases, including verbosity bias (preferring longer responses), self-enhancement bias (if the teacher is also the model being evaluated), and positional bias. Always validate distilled judges against independent human annotations.
\end{warningbox}

\begin{warningbox}[蒸馏偏差]
从单一教师模型中蒸馏得到的学生评判模型会继承教师模型的偏差，包括冗长偏差（偏好更长的响应）、自我增强偏差（如果教师模型同时也是被评估的模型）以及位置偏差。务必使用独立的人工标注来验证蒸馏得到的评判模型。
\end{warningbox}

\subsection{Arena-Style Pairwise Generation}
\label{arena-style-pairwise-generation}

## Arena 风格的成对生成
## \label{arena-style-pairwise-generation}

Chatbot Arena~\cite{zheng2023judging} generates evaluation data through a crowdsourced battle platform where users submit prompts and vote on which of two anonymised model responses they prefer. This produces a large-scale, naturally diverse dataset of pairwise preferences. The key design choices:
Chatbot Arena~\cite{zheng2023judging} 通过众包对战平台生成评估数据，用户提交提示词，然后对两个匿名模型响应中更偏好的一个进行投票。这产生了大规模、自然多样的成对偏好数据集。关键设计选择如下：

\begin{itemize}
  \item \textbf{Anonymisation:} Model identities are hidden to prevent brand bias.
  \item \textbf{User-submitted prompts:} Ensures prompt diversity and real-world relevance.
  \item \textbf{Tie handling:} Users can declare a tie or indicate that both responses are bad.
  \item \textbf{Deduplication:} Near-duplicate prompts are filtered to prevent over-representation of common queries.
\end{itemize}

\begin{itemize}
  \item \textbf{匿名化：} 隐藏模型身份以防止品牌偏见。
  \item \textbf{用户提交的提示词：} 确保提示词的多样性和现实相关性。
  \item \textbf{平局处理：} 用户可以声明平局或指出两个响应都不好。
  \item \textbf{去重：} 过滤近似重复的提示词，防止常见查询的过度代表。
\end{itemize}

\section{Metrics for Ranking Tasks}
\label{subsec:ranking-metrics}

## 排名任务指标
## \label{subsec:ranking-metrics}

When the goal is to rank models by quality, pairwise comparison data is more reliable than absolute scores. This section derives the major ranking systems used in LLM evaluation.
当目标是按质量对模型进行排名时，成对比较数据比绝对分数更可靠。本节推导了LLM评估中使用的主要排名系统。

\subsection{ELO Rating System}
\label{elo-rating-system}

## ELO 评分系统
## \label{elo-rating-system}

The ELO system~\cite{elo1978rating}, originally developed for chess, assigns each player (model) a scalar rating $R$ such that the expected score of player $A$ against player $B$ is: 
\begin{equation}
    E_A = \frac{1}{1 + 10^{(R_B - R_A)/400}}
\end{equation}
ELO系统~\cite{elo1978rating}最初为国际象棋开发，为每位玩家（模型）分配一个标量评分 $R$，使得玩家 $A$ 对阵玩家 $B$ 的期望得分为：
\begin{equation}
    E_A = \frac{1}{1 + 10^{(R_B - R_A)/400}}
\end{equation}

\paragraph{Derivation.}
\label{derivation.}

\paragraph{推导.}
\label{derivation.}

The ELO model assumes that each player’s performance on a given game is a random variable drawn from a logistic distribution centred at their rating. The probability that $A$ beats $B$ is: 
\begin{equation}
    P(A \succ B) = \sigma\!\left(\frac{R_A - R_B}{s}\right) = \frac{1}{1 + e^{-(R_A - R_B)/s}}
\end{equation}
 where $s = 400/\ln(10) \approx 173.7$ is a scale parameter chosen so that a 400-point difference corresponds to a $10:1$ odds ratio. After each game with outcome $S_A \in \{0, 0.5, 1\}$ (loss, draw, win), ratings are updated: 
\begin{equation}
    R_A \leftarrow R_A + K(S_A - E_A), \qquad R_B \leftarrow R_B + K(S_B - E_B)
\end{equation}
 where $K$ is the $K$-factor controlling the learning rate. In Chatbot Arena, $K = 4$ is used.
ELO模型假设每位玩家在单场比赛中的表现是一个随机变量，取自以其评分为中心的逻辑分布。$A$ 击败 $B$ 的概率为：
\begin{equation}
    P(A \succ B) = \sigma\!\left(\frac{R_A - R_B}{s}\right) = \frac{1}{1 + e^{-(R_A - R_B)/s}}
\end{equation}
其中 $s = 400/\ln(10) \approx 173.7$ 是一个尺度参数，选择它使得400分的差异对应 $10:1$ 的赔率。每场比赛结束后，根据结果 $S_A \in \{0, 0.5, 1\}$（输、平、赢），评分更新如下：
\begin{equation}
    R_A \leftarrow R_A + K(S_A - E_A), \qquad R_B \leftarrow R_B + K(S_B - E_B)
\end{equation}
其中 $K$ 是控制学习速率的 $K$ 因子。在Chatbot Arena中，使用 $K = 4$。

\begin{intuitionbox}[ELO Intuition]
ELO is a stochastic gradient descent update on the log-likelihood of the observed outcomes under the logistic model. Each game provides a noisy gradient signal; the $K$-factor controls the step size. A large $K$ adapts quickly but is noisy; a small $K$ is stable but slow to reflect true skill changes.
\end{intuitionbox}

\begin{intuitionbox}[ELO 直觉理解]
ELO是对逻辑模型下观测结果的似然对数进行随机梯度下降更新。每场比赛提供一个带噪声的梯度信号；$K$因子控制步长。大的$K$值适应迅速但噪声大；小的$K$值稳定但反映真实技能变化缓慢。
\end{intuitionbox}

\paragraph{Bootstrap Confidence Intervals for ELO.}
\label{bootstrap-confidence-intervals-for-elo.}

\paragraph{ELO 的 Bootstrap 置信区间.}
\label{bootstrap-confidence-intervals-for-elo.}

Because ELO ratings depend on the order in which games are processed, confidence intervals are computed by bootstrap resampling: resample the battle log with replacement $B = 1000$ times, recompute ELO ratings from scratch for each resample, and report the 2.5th and 97.5th percentiles as the 95\% confidence interval.
由于ELO评分依赖于比赛处理的顺序，置信区间通过Bootstrap重采样计算：对对战日志进行有放回的重采样 $B = 1000$ 次，对每个重采样样本从头重新计算ELO评分，并将第2.5百分位和第97.5百分位报告为95%置信区间。

\subsection{Bradley--Terry Model}
\label{bradleyterry-model}

## Bradley--Terry 模型
## \label{bradleyterry-model}

The Bradley--Terry (BT) model~\cite{bradley1952rank} is a maximum-likelihood alternative to ELO. Given $n$ models with strength parameters $\beta_1, \ldots, \beta_n > 0$, the probability that model $i$ beats model $j$ is: 
\begin{equation}
    P(i \succ j) = \frac{\beta_i}{\beta_i + \beta_j}
\end{equation}
Bradley--Terry (BT) 模型~\cite{bradley1952rank} 是ELO的一种最大似然替代方法。给定 $n$ 个模型，其强度参数 $\beta_1, \ldots, \beta_n > 0$，模型 $i$ 击败模型 $j$ 的概率为：
\begin{equation}
    P(i \succ j) = \frac{\beta_i}{\beta_i + \beta_j}
\end{equation}

Given a set of pairwise outcomes $\{(i_k, j_k, y_k)\}_{k=1}^{M}$ where $y_k = 1$ if $i_k$ beats $j_k$ and $y_k = 0$ otherwise, the log-likelihood is: 
\begin{equation}
    \ell(\boldsymbol{\beta}) = \sum_{k=1}^{M} \left[ y_k \log \frac{\beta_{i_k}}{\beta_{i_k} + \beta_{j_k}} + (1-y_k) \log \frac{\beta_{j_k}}{\beta_{i_k} + \beta_{j_k}} \right]
\end{equation}
给定一组成对结果 $\{(i_k, j_k, y_k)\}_{k=1}^{M}$，其中如果 $i_k$ 击败 $j_k$ 则 $y_k = 1$，否则 $y_k = 0$，对数似然为：
\begin{equation}
    \ell(\boldsymbol{\beta}) = \sum_{k=1}^{M} \left[ y_k \log \frac{\beta_{i_k}}{\beta_{i_k} + \beta_{j_k}} + (1-y_k) \log \frac{\beta_{j_k}}{\beta_{i_k} + \beta_{j_k}} \right]
\end{equation}

The MLE $\hat{\boldsymbol{\beta}}$ is found by iterative scaling or gradient ascent. The BT model is identifiable only up to a multiplicative constant; a common normalisation is $\sum_i \log \beta_i = 0$. Working in log-space with $\theta_i = \log \beta_i$ gives: 
\begin{equation}
    P(i \succ j) = \sigma(\theta_i - \theta_j)
\end{equation}
 which is equivalent to a logistic regression with item-specific intercepts. The BT model is preferred over ELO when the full battle history is available, as it uses all data simultaneously rather than processing games sequentially.
MLE $\hat{\boldsymbol{\beta}}$ 通过迭代缩放或梯度上升求得。BT模型仅在乘以一个常数时是可识别的；常用的归一化是 $\sum_i \log \beta_i = 0$。在对数空间中使用 $\theta_i = \log \beta_i$ 可得：
\begin{equation}
    P(i \succ j) = \sigma(\theta_i - \theta_j)
\end{equation}
这等价于具有项目特定截距的逻辑回归。当完整的对战历史可用时，BT模型优于ELO，因为它同时使用所有数据，而不是顺序处理比赛。

\subsection{TrueSkill}
\label{trueskill}

## TrueSkill
## \label{trueskill}

TrueSkill~\cite{herbrich2006trueskill} is a Bayesian skill rating system that models each player’s skill as a Gaussian random variable $s_i \sim \mathcal{N}(\mu_i, \sigma_i^2)$. The performance of player $i$ in a game is $p_i = s_i + \epsilon_i$ where $\epsilon_i \sim \mathcal{N}(0, \beta^2)$ is game-specific noise. Player $i$ beats player $j$ if $p_i > p_j$.
TrueSkill~\cite{herbrich2006trueskill} 是一个贝叶斯技能评分系统，将每位玩家的技能建模为高斯随机变量 $s_i \sim \mathcal{N}(\mu_i, \sigma_i^2)$。玩家 $i$ 在比赛中的表现为 $p_i = s_i + \epsilon_i$，其中 $\epsilon_i \sim \mathcal{N}(0, \beta^2)$ 是特定比赛的噪声。如果 $p_i > p_j$，则玩家 $i$ 击败玩家 $j$。

The posterior update after observing $i \succ j$ is computed via expectation propagation (EP). The key update equations for the winner are: 
\begin{equation}
    \mu_i \leftarrow \mu_i + \frac{\sigma_i^2}{c} \cdot v\!\left(\frac{\mu_i - \mu_j}{c}\right)
\end{equation}
 
\begin{equation}
    \sigma_i^2 \leftarrow \sigma_i^2 \left[1 - \frac{\sigma_i^2}{c^2} \cdot w\!\left(\frac{\mu_i - \mu_j}{c}\right)\right]
\end{equation}
 where $c = \sqrt{2\beta^2 + \sigma_i^2 + \sigma_j^2}$, and $v(t) = \phi(t)/\Phi(t)$, $w(t) = v(t)(v(t) + t)$ are the truncated Gaussian correction factors ($\phi$ and $\Phi$ are the standard normal PDF and CDF). TrueSkill’s uncertainty estimate $\sigma_i$ is particularly useful for identifying models that need more evaluation data.
观测到 $i \succ j$ 后的后验更新通过期望传播 (EP) 计算。获胜者的关键更新公式为：
\begin{equation}
    \mu_i \leftarrow \mu_i + \frac{\sigma_i^2}{c} \cdot v\!\left(\frac{\mu_i - \mu_j}{c}\right)
\end{equation}
\begin{equation}
    \sigma_i^2 \leftarrow \sigma_i^2 \left[1 - \frac{\sigma_i^2}{c^2} \cdot w\!\left(\frac{\mu_i - \mu_j}{c}\right)\right]
\end{equation}
其中 $c = \sqrt{2\beta^2 + \sigma_i^2 + \sigma_j^2}$，而 $v(t) = \phi(t)/\Phi(t)$, $w(t) = v(t)(v(t) + t)$ 是截断高斯校正因子（$\phi$ 和 $\Phi$ 为标准正态的概率密度函数和累积分布函数）。TrueSkill的不确定性估计 $\sigma_i$ 对于识别需要更多评估数据的模型特别有用。

\subsection{Win Rate with Confidence Intervals}
\label{win-rate-with-confidence-intervals}

## 胜率与置信区间
## \label{win-rate-with-confidence-intervals}

The simplest ranking metric is the win rate: the fraction of pairwise comparisons in which model $A$ is preferred. Given $n$ comparisons with $w$ wins, the win rate is $\hat{p} = w/n$. A Wilson score confidence interval~\cite{wilson1927probable} is preferred over the naive Wald interval because it has better coverage near $p = 0$ and $p = 1$: 
\begin{equation}
    \text{CI} = \frac{\hat{p} + \frac{z^2}{2n} \pm z\sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}
\end{equation}
 where $z = 1.96$ for a 95\% interval. For multi-way comparisons, win rate should be computed against a fixed baseline model to ensure comparability.
最简单的排名指标是胜率：模型 $A$ 被偏好的成对比较比例。给定 $n$ 次比较，其中 $w$ 次获胜，胜率为 $\hat{p} = w/n$。Wilson得分置信区间~\cite{wilson1927probable} 优于朴素的Wald区间，因为它在 $p=0$ 和 $p=1$ 附近具有更好的覆盖范围：
\begin{equation}
    \text{CI} = \frac{\hat{p} + \frac{z^2}{2n} \pm z\sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}
\end{equation}
其中 $z = 1.96$ 对应95%置信区间。对于多方比较，胜率应针对固定的基线模型计算，以确保可比性。

\subsection{Chatbot Arena Methodology}
\label{chatbot-arena-methodology}

## Chatbot Arena 方法论
## \label{chatbot-arena-methodology}

Chatbot Arena~\cite{zheng2023judging} combines the above elements into a production-scale evaluation system:
Chatbot Arena~\cite{zheng2023judging} 将上述要素结合成一个生产规模的评估系统：

\begin{enumerate}
  \item Users submit prompts and receive responses from two anonymised models.
  \item Users vote for the preferred response (or declare a tie).
  \item Votes are aggregated using the BT model to produce a leaderboard.
  \item Bootstrap confidence intervals are reported for each model’s score.
  \item Models with overlapping confidence intervals are considered statistically indistinguishable.
\end{enumerate}

\begin{enumerate}
  \item 用户提交提示词，并从两个匿名模型接收响应。
  \item 用户对偏好的响应进行投票（或声明平局）。
  \item 使用BT模型聚合投票，生成排行榜。
  \item 报告每个模型得分的Bootstrap置信区间。
  \item 置信区间重叠的模型被视为统计上不可区分。
\end{enumerate}

As of 2024, Chatbot Arena has collected over one million human preference votes, making it the largest publicly available LLM preference dataset.
截至2024年，Chatbot Arena已收集超过一百万个人类偏好投票，使其成为最大的公开可用LLM偏好数据集。

\section{Metrics for Generation Tasks}
\label{subsec:generation-metrics}

## 生成任务指标
## \label{subsec:generation-metrics}

Generation metrics quantify the quality of model outputs for tasks with reference answers or well-defined correctness criteria.
生成任务指标量化模型在具有参考答案或明确定义的正确性标准的任务中的输出质量。

## BLEU
## BLEU

BLEU (Bilingual Evaluation Understudy)~\cite{papineni2002bleu} measures $n$-gram precision between a hypothesis $h$ and one or more references $\mathcal{R}$:
BLEU（双语评估替补）~\cite{papineni2002bleu} 衡量假设 $h$ 与一个或多个参考 $\mathcal{R}$ 之间的 $n$-gram 精确率：
\begin{equation}
    \text{BLEU} = \text{BP} \cdot \exp\!\left(\sum_{n=1}^{N} w_n \log p_n\right)
\end{equation}
 where $p_n$ is the modified $n$-gram precision, $w_n = 1/N$ are uniform weights, and BP is the brevity penalty:
其中 $p_n$ 是修正的 $n$-gram 精确率，$w_n = 1/N$ 是均匀权重，BP 是简短惩罚：
\begin{equation}
    \text{BP} = \begin{cases} 1 & \text{if } |h| > |r| \\ e^{1 - |r|/|h|} & \text{if } |h| \leq |r| \end{cases}
\end{equation}
 with $|r|$ being the length of the closest reference. Modified $n$-gram precision clips each $n$-gram count to its maximum count in any reference:
其中 $|r|$ 是最近参考的长度。修正的 $n$-gram 精确率将每个 $n$-gram 计数裁剪到它在任何参考中的最大计数：
\begin{equation}
    p_n = \frac{\sum_{\text{ngram} \in h} \min\!\left(\text{count}(\text{ngram}, h),\, \max_{r \in \mathcal{R}} \text{count}(\text{ngram}, r)\right)}{\sum_{\text{ngram} \in h} \text{count}(\text{ngram}, h)}
\end{equation}

\begin{warningbox}[BLEU Limitations]
BLEU Limitations
BLEU was designed for machine translation with multiple references. For open-ended generation with a single reference, BLEU scores are often near zero even for high-quality outputs. BLEU does not capture semantic similarity, penalises valid paraphrases, and is sensitive to tokenisation. Use BLEU only when multiple diverse references are available and the task has low output diversity.
BLEU 的局限性
BLEU 是为多参考的机器翻译设计的。对于只有一个参考的开放式生成，即使输出质量很高，BLEU 分数也常常接近零。BLEU 不能捕获语义相似性，会惩罚有效的释义，并且对分词敏感。仅当有多个多样化的参考且任务输出多样性较低时才使用 BLEU。
\end{warningbox}

## ROUGE
## ROUGE

ROUGE (Recall-Oriented Understudy for Gisting Evaluation)~\cite{lin2004rouge} is a family of recall-oriented metrics designed for summarisation:
ROUGE（面向召回率的摘要评估替补）~\cite{lin2004rouge} 是一组面向召回率的度量，专为摘要而设计：
\begin{align}
    \text{ROUGE-N} &= \frac{\sum_{r \in \mathcal{R}} \sum_{\text{ngram} \in r} \min(\text{count}(\text{ngram}, h), \text{count}(\text{ngram}, r))}{\sum_{r \in \mathcal{R}} \sum_{\text{ngram} \in r} \text{count}(\text{ngram}, r)} \\[6pt]
    \text{ROUGE-L} &= \frac{\text{LCS}(h, r)}{|r|}
\end{align}
 where LCS denotes the longest common subsequence. ROUGE-1 and ROUGE-2 measure unigram and bigram recall; ROUGE-L captures sentence-level structure. The F-measure variant balances precision and recall:
其中 LCS 表示最长公共子序列。ROUGE-1 和 ROUGE-2 衡量一元和二元召回率；ROUGE-L 捕获句子级结构。F 度量变体平衡精确率和召回率：
\begin{equation}
    \text{ROUGE-N}_F = \frac{(1+\beta^2) \cdot P \cdot R}{\beta^2 P + R}
\end{equation}
 with $\beta = 1$ for equal weighting.
其中 $\beta = 1$ 表示等权重。

## BERTScore
## BERTScore

BERTScore~\cite{zhang2020bertscore} computes token-level similarity using contextual embeddings from a pre-trained BERT model. Given hypothesis tokens $\hat{\mathbf{x}} = \langle \hat{x}_1, \ldots, \hat{x}_m \rangle$ and reference tokens $\mathbf{x} = \langle x_1, \ldots, x_n \rangle$ with embeddings $\hat{\mathbf{e}}_i$ and $\mathbf{e}_j$:
BERTScore~\cite{zhang2020bertscore} 使用预训练 BERT 模型的上下文嵌入计算词元级相似度。给定假设词元 $\hat{\mathbf{x}} = \langle \hat{x}_1, \ldots, \hat{x}_m \rangle$ 和参考词元 $\mathbf{x} = \langle x_1, \ldots, x_n \rangle$，其嵌入分别为 $\hat{\mathbf{e}}_i$ 和 $\mathbf{e}_j$：
\begin{align}
    R_{\text{BERT}} &= \frac{1}{|x|} \sum_{x_j \in \mathbf{x}} \max_{\hat{x}_i \in \hat{\mathbf{x}}} \frac{\hat{\mathbf{e}}_i^\top \mathbf{e}_j}{\|\hat{\mathbf{e}}_i\| \|\mathbf{e}_j\|} \\[4pt]
    P_{\text{BERT}} &= \frac{1}{|\hat{x}|} \sum_{\hat{x}_i \in \hat{\mathbf{x}}} \max_{x_j \in \mathbf{x}} \frac{\hat{\mathbf{e}}_i^\top \mathbf{e}_j}{\|\hat{\mathbf{e}}_i\| \|\mathbf{e}_j\|} \\[4pt]
    F_{\text{BERT}} &= 2 \cdot \frac{P_{\text{BERT}} \cdot R_{\text{BERT}}}{P_{\text{BERT}} + R_{\text{BERT}}}
\end{align}

BERTScore correlates better with human judgments than BLEU and ROUGE, particularly for paraphrases and semantically equivalent but lexically different outputs. Importance weighting using inverse document frequency (IDF) further improves correlation:
BERTScore 与人类判断的相关性优于 BLEU 和 ROUGE，尤其是对于释义和语义等价但词汇不同的输出。使用逆文档频率（IDF）进行重要性加权进一步提高了相关性：
\begin{equation}
    R_{\text{BERT}}^{\text{idf}} = \frac{\sum_{x_j \in \mathbf{x}} \text{idf}(x_j) \max_{\hat{x}_i} \cos(\hat{\mathbf{e}}_i, \mathbf{e}_j)}{\sum_{x_j \in \mathbf{x}} \text{idf}(x_j)}
\end{equation}

## METEOR
## METEOR

METEOR~\cite{banerjee2005meteor} addresses BLEU’s recall blindness by computing an F-score over unigram matches, with additional modules for stemming and synonym matching:
METEOR~\cite{banerjee2005meteor} 通过计算一元匹配的 F 分数来解决 BLEU 的召回率盲区，并附加了词干提取和同义词匹配模块：
\begin{equation}
    \text{METEOR} = F_{\text{mean}} \cdot (1 - \text{Pen})
\end{equation}
 where $F_{\text{mean}} = \frac{10PR}{R + 9P}$ (recall-weighted harmonic mean) and the fragmentation penalty $\text{Pen} = 0.5 \cdot (c/u_m)^3$ penalises non-contiguous matches ($c$ = number of chunks, $u_m$ = number of matched unigrams).
其中 $F_{\text{mean}} = \frac{10PR}{R + 9P}$（召回率加权调和平均），碎片惩罚 $\text{Pen} = 0.5 \cdot (c/u_m)^3$ 惩罚非连续匹配（$c$ = 块数，$u_m$ = 匹配的一元数量）。

## Perplexity
## 困惑度

Perplexity measures how well a language model predicts a held-out text sequence $w_1, w_2, \ldots, w_T$:
困惑度衡量语言模型预测一个保留文本序列 $w_1, w_2, \ldots, w_T$ 的效果：
\begin{equation}
    \text{PPL}(w_{1:T}) = \exp\!\left(-\frac{1}{T}\sum_{t=1}^{T} \log P_\theta(w_t \mid w_{1:t-1})\right)
\end{equation}

Lower perplexity indicates better predictive performance. Perplexity is useful for comparing models on the same tokenisation and test set, but is not directly comparable across models with different vocabularies or tokenisers. For evaluation purposes, perplexity is most useful as a sanity check and for detecting distribution shift.
较低的困惑度表示更好的预测性能。困惑度适用于在相同分词和测试集上比较模型，但对于具有不同词汇表或分词器的模型不能直接比较。在评估中，困惑度最常用作合理性检查以及检测分布漂移。

## Pass@k for Code
## 代码的 Pass@k

For code generation, functional correctness is measured by executing generated code against test cases. The pass@$k$ metric~\cite{chen2021evaluating} estimates the probability that at least one of $k$ generated samples passes all tests:
对于代码生成，功能正确性是通过对测试用例执行生成的代码来衡量的。pass@$k$ 度量~\cite{chen2021evaluating} 估计 $k$ 个生成样本中至少有一个通过所有测试的概率：
\begin{equation}
    \text{pass@}k = \mathbb{E}_{\text{problems}}\!\left[1 - \frac{\binom{n-c}{k}}{\binom{n}{k}}\right]
\end{equation}
 where $n$ is the total number of samples generated per problem and $c$ is the number that pass. This unbiased estimator avoids the high variance of the naive estimator (which samples exactly $k$ solutions and checks if any pass). In practice, $n = 200$ samples are generated and pass@1, pass@10, pass@100 are reported.
其中 $n$ 是每个问题生成的样本总数，$c$ 是通过的样本数。这个无偏估计避免了朴素估计器（即正好采样 $k$ 个解并检查是否有任何通过）的高方差。实践中，生成 $n = 200$ 个样本，并报告 pass@1、pass@10 和 pass@100。

\begin{examplebox}[Pass@k Computation]
Pass@k 计算
\begin{lstlisting}[style=pythonstyle]
import numpy as np
from scipy.special import comb


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased estimator for pass@k.
    无偏的 pass@k 估计器。
    
    Args:
        n: total samples generated per problem
        n: 每个问题生成的样本总数
        c: number of samples that pass all tests
        c: 通过所有测试的样本数
        k: number of samples to consider
        k: 要考虑的样本数
    """
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k, exact=True) / comb(n, k, exact=True)


