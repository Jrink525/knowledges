```markdown
# Quiz Questions & Detailed Answers
# 测验题与详细解答

\label{quiz-questions-detailed-answers}

This chapter provides a comprehensive set of questions designed to test and reinforce your understanding of the material covered throughout this guide. Each question targets a key concept, algorithm, or system design decision---the kind of knowledge that distinguishes surface-level familiarity from genuine expertise. Use these questions for self-assessment: attempt your own answer before reading the detailed solution. The questions progress from foundational concepts (LLM architecture, reinforcement learning basics) through core algorithms (PPO, DPO, GRPO) to advanced system design and agentic AI topics.

本章提供了一套全面的问题，旨在测试并巩固你对本书所涵盖内容的理解。每个问题都针对一个关键概念、算法或系统设计决策——这些知识能够区分浅层熟悉与真正的专业知识。请使用这些问题进行自评：在阅读详细解答之前先尝试自己作答。问题从基础概念（LLM架构、强化学习基础）逐步过渡到核心算法（PPO、DPO、GRPO），再到高级系统设计和智能体AI主题。

\section{Foundations Questions}
\section{基础问题}

\label{foundations-questions}

\begin{questionbox}[Q0a: What is the role of the attention mechanism in a decoder-only Transformer? Why is it causal?]
\textbf{Answer}: The attention mechanism allows each token to attend to (i.e., compute a weighted combination of) representations from other tokens. In a decoder-only Transformer, attention is \textbf{causal} (also called \emph{autoregressive}): token $t$ can only attend to tokens $1, \ldots, t$, never to future tokens $t+1, \ldots, T$.

\textbf{答案}：注意力机制允许每个token关注（即计算加权组合）来自其他token的表示。在仅有解码器的Transformer中，注意力是\textbf{因果的}（也称为\emph{自回归的}）：token $t$ 只能关注token $1, \ldots, t$，绝不能关注未来的token $t+1, \ldots, T$。

\textbf{Why causal?} Because the model generates text left-to-right. At inference time, future tokens literally do not exist yet. The causal mask during training simulates this constraint so that the model learns to predict each token using only its left context. Mathematically, the attention matrix is masked: 
\[
\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}} + M\right) V
\]
 where $M_{ij} = -\infty$ for $j > i$ (future positions), forcing those attention weights to zero.

\textbf{为什么是因果的？}因为模型从左到右生成文本。在推理时，未来的token实际上还不存在。训练期间的因果掩码模拟了这一约束，使得模型学会仅使用左侧上下文来预测每个token。数学上，注意力矩阵被掩码：
\[
\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}} + M\right) V
\]
其中 $M_{ij} = -\infty$ 当 $j > i$（未来位置），迫使这些注意力权重为零。

\textbf{Practical implication}: This enables the KV-cache optimization at inference---since past tokens’ keys and values never change, they can be cached and reused, reducing generation from $O(T^2)$ to $O(T)$ per new token.

\textbf{实际意义}：这使得推理时能够进行KV缓存优化——由于过去token的键和值从不改变，它们可以被缓存并重用，将每个新token的生成从 $O(T^2)$ 降低到 $O(T)$。

\emph{\textbf{Review:} Chapter~1 (LLM Architecture and Optimization Methods).}
\emph{\textbf{回顾：}第1章（LLM架构与优化方法）。}
\end{questionbox}

\begin{questionbox}[Q0b: Explain Flash Attention. What problem does it solve and how?]
\textbf{Answer}: Standard attention computes the full $T \times T$ attention matrix, which requires $O(T^2)$ memory and is \textbf{memory-bandwidth bound}---the GPU spends most of its time moving data between HBM (slow, large) and SRAM (fast, small), not doing actual computation.

\textbf{答案}：标准注意力计算完整的 $T \times T$ 注意力矩阵，这需要 $O(T^2)$ 内存，并且是\textbf{内存带宽受限}的——GPU大部分时间都在HBM（慢、大）和SRAM（快、小）之间移动数据，而不是进行实际计算。

\textbf{Flash Attention’s insight}: Never materialize the full attention matrix in HBM. Instead, tile the computation into blocks that fit in SRAM, compute attention \emph{block by block} using an online softmax algorithm, and write only the final output to HBM.

\textbf{Flash Attention的洞见}：永远不要在HBM中物化完整的注意力矩阵。而是将计算分块为适合SRAM的块，使用在线softmax算法\emph{逐块}计算注意力，并仅将最终输出写入HBM。

\textbf{Key techniques}:

\textbf{关键技术}：

\begin{enumerate}
  \item \textbf{Tiling}: Split Q, K, V into blocks of size $B_r \times B_c$ that fit in SRAM
  \item \textbf{Online softmax}: Track running max and sum to compute softmax incrementally without the full row
  \item \textbf{Recomputation}: In the backward pass, recompute attention from Q, K, V (cheap) rather than storing the $T \times T$ matrix (expensive)
\end{enumerate}

\begin{enumerate}
  \item \textbf{分块}：将Q、K、V拆分为尺寸为 $B_r \times B_c$ 的块，使其适合SRAM
  \item \textbf{在线softmax}：追踪运行中的最大值和总和，逐步计算softmax而无需完整行
  \item \textbf{重计算}：在反向传播中，从Q、K、V重新计算注意力（廉价），而不是存储 $T \times T$ 矩阵（昂贵）
\end{enumerate}

\textbf{Result}: $O(T)$ HBM memory (instead of $O(T^2)$), 2--4$\times$ wall-clock speedup, exact same numerical output (not an approximation).

\textbf{结果}：$O(T)$ HBM内存（而非 $O(T^2)$），2--4倍的实际时间加速，数值输出完全相同（非近似）。

\emph{\textbf{Review:} Chapters~1--2 (LLM Architecture; Systems Foundations).}
\emph{\textbf{回顾：}第1-2章（LLM架构；系统基础）。}
\end{questionbox}

\begin{questionbox}[Q0c: What is the difference between SFT, RLHF, and DPO at a high level? When do you use each?]
\textbf{Answer}:

\textbf{答案}：

\begin{itemize}
  \item \textbf{SFT (Supervised Fine-Tuning)}: Train the model to imitate high-quality demonstrations. Loss: next-token prediction on curated data. Teaches \emph{format} and \emph{style}.
  \item \textbf{RLHF}: Train a reward model from human preferences, then optimize the policy against it using RL (PPO). The model explores beyond the demonstration data. Teaches \emph{what humans prefer}.
  \item \textbf{DPO}: Skip the reward model. Directly optimize the policy on preference pairs $(y_w, y_l)$ using a contrastive loss. Same goal as RLHF but simpler pipeline.
\end{itemize}

\begin{itemize}
  \item \textbf{SFT（监督微调）}：训练模型模仿高质量示例。损失：对精选数据进行下一个token预测。教导\emph{格式}和\emph{风格}。
  \item \textbf{RLHF（基于人类反馈的强化学习）}：从人类偏好训练奖励模型，然后使用RL（PPO）优化策略。模型探索超出演示数据范围。教导\emph{人类偏好什么}。
  \item \textbf{DPO（直接偏好优化）}：跳过奖励模型。直接使用对比损失在偏好对 $(y_w, y_l)$ 上优化策略。目标与RLHF相同但流程更简单。
\end{itemize}

\textbf{Typical pipeline}: SFT first (gives the model a good starting point), then RLHF or DPO (refines preferences). SFT alone tends to produce verbose, hedge-heavy responses. RLHF/DPO makes outputs more direct and aligned with human intent.

\textbf{典型流程}：先进行SFT（为模型提供良好的起点），然后进行RLHF或DPO（细化偏好）。仅SFT往往会产生冗长、充满模糊措辞的回复。RLHF/DPO使输出更直接，更符合人类意图。

\textbf{When to use each}: SFT when you have gold-standard outputs. DPO when you have preference pairs but limited compute. RLHF (PPO) when you need maximum quality and can afford the infrastructure.

\textbf{何时使用每种方法}：当你拥有黄金标准输出时使用SFT。当你有偏好对但计算资源有限时使用DPO。当你需要最高质量且能承担基础设施成本时使用RLHF（PPO）。

\emph{\textbf{Review:} Chapters~5, 6, and~10 (PPO; DPO; SFT Best Practices).}
\emph{\textbf{回顾：}第5、6和10章（PPO；DPO；SFT最佳实践）。}
\end{questionbox}

\begin{questionbox}[Q0d: What is a reward model? How is it trained and what can go wrong?]
\textbf{Answer}: A reward model (RM) is a neural network that takes a (prompt, response) pair and outputs a scalar score indicating quality. It is trained on human preference data: given pairs $(y_w, y_l)$ where $y_w$ is preferred, the RM learns to assign $R(y_w) > R(y_l)$.

\textbf{答案}：奖励模型（Reward Model, RM）是一个神经网络，它接收（提示，回复）对并输出一个标量分数以指示质量。它在人类偏好数据上进行训练：给定对 $(y_w, y_l)$，其中 $y_w$ 是更受偏好的，RM学习分配 $R(y_w) > R(y_l)$。

\textbf{Training}: Bradley-Terry loss: $\mathcal{L} = -\log\sigma(R(y_w) - R(y_l))$. Architecture: typically the same transformer as the policy, with the LM head replaced by a scalar projection.

\textbf{训练}：Bradley-Terry损失：$\mathcal{L} = -\log\sigma(R(y_w) - R(y_l))$。架构：通常与策略相同的transformer，将语言模型头部替换为标量投影。

\textbf{What can go wrong}:

\textbf{可能出现的问题}：

\begin{enumerate}
  \item \textbf{Reward hacking}: The policy finds outputs that score high on the RM but are actually low quality (e.g., excessively long, repetitive, or containing specific phrases the RM was biased toward)
  \item \textbf{Distribution shift}: The RM was trained on outputs from an earlier policy. As training progresses, the current policy generates out-of-distribution outputs the RM cannot score accurately
  \item \textbf{Label noise}: Human annotators disagree, are tired, or apply inconsistent criteria. This noise propagates into RM predictions
  \item \textbf{Overconfidence}: The RM assigns extreme scores to outputs it has never seen, providing misleading gradient signal
\end{enumerate}

\begin{enumerate}
  \item \textbf{奖励篡改}：策略找到在RM上得分高但实际质量低的输出（例如，过长、重复或包含RM有偏见的特定短语）
  \item \textbf{分布偏移}：RM是在早期策略的输出上训练的。随着训练进行，当前策略生成分布外的输出，RM无法准确评分
  \item \textbf{标签噪声}：人类标注者意见不一致、疲劳或应用不一致的标准。这种噪声会传播到RM的预测中
  \item \textbf{过度自信}：RM为从未见过的输出分配极端分数，提供误导性的梯度信号
\end{enumerate}

\emph{\textbf{Review:} Chapter~9 (Reward Model Training).}
\emph{\textbf{回顾：}第9章（奖励模型训练）。}
\end{questionbox}

\begin{questionbox}[Q0e: Explain the exploration-exploitation trade-off in RL. How does it manifest in LLM training?]
\textbf{Answer}: In RL, an agent must balance:

\textbf{答案}：在RL中，智能体必须平衡：

\begin{itemize}
  \item \textbf{Exploitation}: choosing actions known to yield high reward (greedy behavior)
  \item \textbf{Exploration}: trying new actions that might yield even higher reward (but might also fail)
\end{itemize}

\begin{itemize}
  \item \textbf{利用}：选择已知能获得高奖励的动作（贪婪行为）
  \item \textbf{探索}：尝试可能获得更高奖励（但也可能失败）的新动作
\end{itemize}

\textbf{In LLM training}: The policy is the language model. ``Actions'' are token choices. ``Exploitation'' means generating responses similar to what already scored well. ``Exploration'' means trying novel phrasings, structures, or reasoning paths.

\textbf{在LLM训练中}：策略是语言模型。“动作”是token选择。“利用”意味着生成与已获得高分相似的回复。“探索”意味着尝试新的措辞、结构或推理路径。

\textbf{How it manifests}:

\textbf{其表现方式}：

\begin{itemize}
  \item \textbf{Temperature during generation}: Higher temperature = more exploration. GRPO uses temperature 1.0 to get diverse samples within each group.
  \item \textbf{KL penalty}: Acts as an anti-exploration brake---prevents the policy from straying too far from the reference model. Without it, the policy might collapse to a single high-reward template (mode collapse).
  \item \textbf{Group sampling in GRPO}: Generating $G$ responses per prompt explicitly explores the output space, then reinforces above-average responses.
\end{itemize}

\begin{itemize}
  \item \textbf{生成时的温度}：温度越高=探索越多。GRPO使用温度1.0以在每组内获得多样化的样本。
  \item \textbf{KL惩罚}：充当反探索的刹车——防止策略偏离参考模型过远。没有它，策略可能坍缩到单一的高奖励模板（模式坍缩）。
  \item \textbf{GRPO中的组采样}：为每个提示生成 $G$ 个回复，明确探索输出空间，然后强化高于平均水平的回复。
\end{itemize}

\textbf{The tension}: Too little exploration $\rightarrow$ the model gets stuck in local optima (always giving the same safe answer). Too much $\rightarrow$ training is unstable, quality fluctuates wildly.

\textbf{这种张力}：探索过少 → 模型陷入局部最优（总是给出相同的安全答案）。探索过多 → 训练不稳定，质量剧烈波动。

\emph{\textbf{Review:} Chapters~3 and~7 (Introduction to RL; GRPO).}
\emph{\textbf{回顾：}第3章和第7章（RL简介；GRPO）。}
\end{questionbox}

\section{Core Algorithm Questions}
\section{核心算法问题}

\label{core-algorithm-questions}
```

## Q1: Explain PPO’s clipped objective. Why does it work better than vanilla PG?
## Q1：解释PPO的裁剪目标。为什么它比原始策略梯度（vanilla PG）效果更好？

\textbf{Answer}: Vanilla policy gradient: $\nabla J = \mathbb{E}[\nabla\log\pi(a|s) \cdot \hat{A}]$. Problem: one lucky/unlucky sample can produce a huge gradient $\rightarrow$ policy jumps to a bad region $\rightarrow$ generates garbage $\rightarrow$ next gradient makes it worse $\rightarrow$ unrecoverable ``death spiral.''
\textbf{答案}：原始策略梯度（vanilla policy gradient）：$\nabla J = \mathbb{E}[\nabla\log\pi(a|s) \cdot \hat{A}]$。问题：一个幸运/不幸的样本可能产生巨大的梯度 $\rightarrow$ 策略跳到坏区域 $\rightarrow$ 生成垃圾 $\rightarrow$ 下一个梯度使其更糟 $\rightarrow$ 不可恢复的“死亡螺旋”。

\textbf{PPO’s solution}: Clip the probability ratio $r = \pi_\text{new}/\pi_\text{old}$ to $[0.8, 1.2]$.
\textbf{PPO的解决方案}：将概率比 $r = \pi_\text{new}/\pi_\text{old}$ 裁剪到 $[0.8, 1.2]$。

\textbf{Mechanics}: For good actions ($\hat{A}>0$): objective is $\min(r\hat{A}, 1.2\hat{A})$. Once $r$ exceeds 1.2, no further benefit --- stops the policy from over-committing to one example. For bad actions ($\hat{A}<0$): objective is $\min(r\hat{A}, 0.8\hat{A})$. Once $r$ drops below 0.8, penalty stops growing --- prevents catastrophic forgetting.
\textbf{机制}：对于好动作（$\hat{A}>0$）：目标是 $\min(r\hat{A}, 1.2\hat{A})$。一旦 $r$ 超过1.2，不再有额外收益——阻止策略过度依赖单个样本。对于坏动作（$\hat{A}<0$）：目标是 $\min(r\hat{A}, 0.8\hat{A})$。一旦 $r$ 低于0.8，惩罚停止增长——防止灾难性遗忘。

\textbf{Key insight}: It’s a first-order approximation of TRPO’s KL constraint, but without expensive second-order optimization. Each update changes the policy by at most $\pm$20\%.
\textbf{关键洞见}：它是TRPO的KL约束的一阶近似，但省去了昂贵的二阶优化。每次更新最多改变策略 $\pm$20\%。

\textbf{For LLMs specifically}: The token-level ratio $r_t = \pi_\theta(y_t|y_{<t})/\pi_\text{old}(y_t|y_{<t})$ prevents any single token’s probability from changing too drastically, preserving coherent generation.
\textbf{专门针对大语言模型（LLM）}：词元级别的比例 $r_t = \pi_\theta(y_t|y_{<t})/\pi_\text{old}(y_t|y_{<t})$ 防止任何单个词元的概率变化过于剧烈，从而保持生成的连贯性。

\emph{\textbf{Review:} Chapter~5 (PPO).}
\emph{\textbf{回顾：} 第5章（PPO）。}

---

## Q2: Derive DPO from first principles. What assumptions does it make?
## Q2：从基本原理推导DPO。它做了哪些假设？

\textbf{Answer}: Start with RLHF objective: $\max_\pi \mathbb{E}[r(x,y)] - \beta D_\text{KL}[\pi\|\pi_\text{ref}]$.
\textbf{答案}：从RLHF目标开始：$\max_\pi \mathbb{E}[r(x,y)] - \beta D_\text{KL}[\pi\|\pi_\text{ref}]$。

\textbf{Step 1}: Write the KKT conditions. Optimal policy has closed form: $\pi^*(y|x) \propto \pi_\text{ref}(y|x)\exp(r(x,y)/\beta)$.
\textbf{第1步}：写出KKT条件。最优策略有闭式解：$\pi^*(y|x) \propto \pi_\text{ref}(y|x)\exp(r(x,y)/\beta)$。

\textbf{Step 2}: Invert to express reward: $r(x,y) = \beta\log(\pi^*/\pi_\text{ref}) + \beta\log Z(x)$.
\textbf{第2步}：反解以表达奖励：$r(x,y) = \beta\log(\pi^*/\pi_\text{ref}) + \beta\log Z(x)$。

\textbf{Step 3}: Substitute into Bradley-Terry model $P(y_w \succ y_l) = \sigma(r(y_w) - r(y_l))$. The partition function $Z(x)$ cancels (same prompt).
\textbf{第3步}：代入Bradley-Terry模型 $P(y_w \succ y_l) = \sigma(r(y_w) - r(y_l))$。配分函数 $Z(x)$ 抵消（同一提示）。

\textbf{Step 4}: Replace $\pi^*$ with $\pi_\theta$ (parameterized policy we’re training): $\mathcal{L} = -\mathbb{E}[\log\sigma(\beta\log\frac{\pi_\theta(y_w)}{\pi_\text{ref}(y_w)} - \beta\log\frac{\pi_\theta(y_l)}{\pi_\text{ref}(y_l)})]$.
\textbf{第4步}：用 $\pi_\theta$（我们正在训练的参数化策略）替换 $\pi^*$：$\mathcal{L} = -\mathbb{E}[\log\sigma(\beta\log\frac{\pi_\theta(y_w)}{\pi_\text{ref}(y_w)} - \beta\log\frac{\pi_\theta(y_l)}{\pi_\text{ref}(y_l)})]$。

\textbf{Assumptions}:
\textbf{假设}：

\begin{enumerate}
  \item Bradley-Terry preference model (pairwise, no ties, transitive)
  \item Optimal policy is achievable by $\pi_\theta$ (sufficient capacity)
  \item Preferences are generated from the same distribution as training data (no distribution shift)
  \item Reference model is fixed and reasonable
\end{enumerate}

\begin{enumerate}
  \item Bradley-Terry偏好模型（成对、无平局、可传递）
  \item 最优策略可由 $\pi_\theta$ 实现（足够容量）
  \item 偏好与训练数据来自同一分布（无分布偏移）
  \item 参考模型固定且合理
\end{enumerate}

\textbf{When assumptions break}: Real preferences aren’t transitive, data shifts during training, labels are noisy $\rightarrow$ that’s why Online DPO and IPO exist.
\textbf{假设失效时}：真实偏好并非可传递，训练中数据偏移，标签存在噪声 $\rightarrow$ 这就是在线DPO（Online DPO）和IPO存在的原因。

\emph{\textbf{Review:} Chapter~6 (DPO).}
\emph{\textbf{回顾：} 第6章（DPO）。}

---

## Q3: GRPO vs PPO — when would you choose each? What’s the trade-off?
## Q3：GRPO与PPO——何时选择哪一个？权衡是什么？

\textbf{Answer}:
\textbf{答案}：

\textbf{GRPO advantages}:
\textbf{GRPO优势}：

\begin{itemize}
  \item No value function needed: saves one model’s worth of memory and complexity
  \item Simpler: fewer hyperparameters, more intuitive (above-mean = good, below-mean = bad)
  \item Better for verifiable rewards: math/code where $r \in \{0, 1\}$ gives crisp signal
  \item DeepSeek-R1 proved it can teach emergent reasoning with just binary rewards
\end{itemize}

\begin{itemize}
  \item 无需价值函数：节省一个模型的显存和复杂度
  \item 更简单：超参数更少，更直观（高于均值=好，低于均值=坏）
  \item 更适合可验证奖励：数学/代码中 $r \in \{0, 1\}$ 给出清晰信号
  \item DeepSeek-R1证明其仅用二元奖励就能教会涌现推理
\end{itemize}

\textbf{PPO advantages}:
\textbf{PPO优势}：

\begin{itemize}
  \item Per-token credit assignment: value function assigns reward to each token, not just sequence-level
  \item More sample efficient: GAE uses value predictions to estimate advantage without generating $G$ samples
  \item Better for nuanced rewards: when reward is continuous and varies significantly across tokens
  \item More mature: battle-tested at OpenAI, Anthropic, etc.
\end{itemize}

\begin{itemize}
  \item 每个词元的信用分配：价值函数将奖励分配给每个词元，而不仅是序列级别
  \item 样本效率更高：GAE利用价值预测估计优势，无需生成 $G$ 个样本
  \item 更适合细微差别的奖励：当奖励连续且跨词元变化显著时
  \item 更成熟：在OpenAI、Anthropic等公司经过实战检验
\end{itemize}

\textbf{Rule of thumb}: If rewards are verifiable (right/wrong) $\rightarrow$ GRPO. If rewards are nuanced (RM scores) and you need max quality $\rightarrow$ PPO. If compute is limited $\rightarrow$ GRPO (no critic training).
\textbf{经验法则}：如果奖励可验证（对/错）$\rightarrow$ 选择GRPO。如果奖励细微（奖励模型分数）且需要最高质量 $\rightarrow$ 选择PPO。如果计算资源有限 $\rightarrow$ 选择GRPO（无需训练评论家）。

\textbf{Compute comparison}: GRPO generates $G$ responses per prompt (8$\times$ more generation), but skips value function training. Net: similar total compute but distributed differently (more gen, less training).
\textbf{计算比较}：GRPO每个提示生成 $G$ 个响应（生成量多8倍），但跳过价值函数训练。净效果：总计算量相似，但分布不同（更多生成，更少训练）。

\emph{\textbf{Review:} Chapters~5 and~7 (PPO; GRPO).}
\emph{\textbf{回顾：} 第5章和第7章（PPO；GRPO）。}

---

## Q4: How does GAE work? Walk through a concrete example for LLMs.
## Q4：GAE如何工作？为大语言模型（LLM）给出一个具体例子。

\textbf{Answer}: GAE = weighted sum of $n$-step TD errors: $\hat{A}_t = \sum_{l=0}^{T-t} (\gamma\lambda)^l \delta_{t+l}$.
\textbf{答案}：GAE = $n$步时序差分误差（TD error）的加权和：$\hat{A}_t = \sum_{l=0}^{T-t} (\gamma\lambda)^l \delta_{t+l}$。

\textbf{Concrete example}: Response has 5 tokens. Reward only at end ($r_5 = 0.8$). Value predictions: $V_1=0.5, V_2=0.55, V_3=0.6, V_4=0.65, V_5=0.7$.
\textbf{具体例子}：响应有5个词元。奖励仅在末尾（$r_5 = 0.8$）。价值预测：$V_1=0.5, V_2=0.55, V_3=0.6, V_4=0.65, V_5=0.7$。

TD errors ($\gamma=1$): $\delta_1 = 0 + V_2 - V_1 = 0.05$, $\delta_2 = 0 + V_3 - V_2 = 0.05$, ..., $\delta_5 = 0.8 + 0 - 0.7 = 0.1$.
TD误差（$\gamma=1$）：$\delta_1 = 0 + V_2 - V_1 = 0.05$，$\delta_2 = 0 + V_3 - V_2 = 0.05$，...，$\delta_5 = 0.8 + 0 - 0.7 = 0.1$。

With $\lambda = 0.95$: $\hat{A}_5 = 0.1$ (just the final TD error), $\hat{A}_4 = 0.05 + 0.95 \times 0.1 = 0.145$, $\hat{A}_3 = 0.05 + 0.95 \times 0.145 = 0.188$, etc.
取 $\lambda = 0.95$：$\hat{A}_5 = 0.1$（仅最终TD误差），$\hat{A}_4 = 0.05 + 0.95 \times 0.1 = 0.145$，$\hat{A}_3 = 0.05 + 0.95 \times 0.145 = 0.188$，等等。

\textbf{Interpretation}: Token 3 gets advantage 0.188 because it contributed to a sequence that got higher reward than expected. Earlier tokens get credit through the exponential decay.
\textbf{解释}：词元3获得优势0.188，因为它对一个得到比预期更高奖励的序列做出了贡献。较早的词元通过指数衰减获得信用。

\textbf{For LLMs}: $\gamma=1.0$ (all tokens matter, finite horizon). The advantage at token $t$ answers: ``given what followed this token, was this token choice better or worse than expected?''
\textbf{对于大语言模型（LLM）}：$\gamma=1.0$（所有词元都重要，有限视界）。在词元 $t$ 处的优势回答了：“考虑到该词元之后的内容，这个词元的选择比预期更好还是更差？”

\emph{\textbf{Review:} Chapter~5 (PPO).}
\emph{\textbf{回顾：} 第5章（PPO）。}

---

## Q5: How do you prevent reward hacking? Give a layered defense strategy.
## Q5：如何防止奖励黑客（reward hacking）？给出分层防御策略。

\textbf{Answer}: \textbf{Detection signals}: RM score rising but win-rate flat/declining. Response length growing monotonically. KL divergence $>$ 15. Diversity (unique n-grams) dropping. Reading high-reward outputs reveals exploits.
\textbf{答案}：\textbf{检测信号}：奖励模型分数上升但胜率持平/下降。响应长度单调增长。KL散度 $>$ 15。多样性（唯一n-gram）下降。阅读高奖励输出可揭示漏洞。

\textbf{Layered defense (in priority order)}:
\textbf{分层防御（按优先级）}：

\begin{enumerate}
  \item \textbf{KL penalty} (primary): Adaptive controller targets KL $\approx$ 6. If KL rises, $\beta$ increases automatically. Prevents drifting too far from reference.
  \item \textbf{Reward model ensemble} (3--5 models): Use min or mean of scores. Individual models have different blind spots --- exploits that fool one rarely fool all.
  \item \textbf{Length penalty}: $r' = r - c \cdot \max(0, \text{length} - L_\text{target})$. Prevents ``just generate longer = higher score'' exploit.
  \item \textbf{Periodic RM refresh}: Every 2000 steps, generate data from current policy, relabel, add to RM training set. Closes the exploit as model finds it.
  \item \textbf{Win-rate based stopping}: Track win-rate against SFT baseline. If RM score rises but win-rate stalls for 200+ steps, stop training. The model is exploiting, not improving.
\end{enumerate}

\begin{enumerate}
  \item \textbf{KL惩罚}（主要）：自适应控制器以KL $\approx$ 6为目标。如果KL上升，$\beta$自动增加。防止偏离参考模型太远。
  \item \textbf{奖励模型集成}（3--5个模型）：使用分数的最小值或均值。单个模型有不同的盲点——能欺骗一个模型的漏洞很少能欺骗所有模型。
  \item \textbf{长度惩罚}：$r' = r - c \cdot \max(0, \text{长度} - L_\text{目标})$。防止“生成更长=更高分数”的漏洞。
  \item \textbf{定期更新奖励模型}：每2000步，从当前策略生成数据，重新标注，加入奖励模型训练集。在模型发现漏洞时关闭它。
  \item \textbf{基于胜率的停止}：跟踪与监督微调（SFT）基线的胜率。如果奖励模型分数上升但胜率停滞超过200步，停止训练。模型在利用漏洞而非改进。
\end{enumerate}

\textbf{Post-detection recovery}: Roll back to last ``clean'' checkpoint. Increase $\beta$ by 2$\times$. Add the discovered exploit to the RM’s negative examples.
\textbf{检测后恢复}：回滚到最后一个“干净”的检查点。将 $\beta$ 增加2倍。将发现的漏洞加入奖励模型的负例中。

\emph{\textbf{Review:} Chapters~9 and~11 (Reward Model Training; System Architecture).}
\emph{\textbf{回顾：} 第9章和第11章（奖励模型训练；系统架构）。}

---

# System Design Questions
# 系统设计问题

\label{system-design-questions}

---

## Q6: Design an RLHF system for training a 70B model. Walk through every component.
## Q6：设计一个用于训练70B模型的RLHF系统。逐一说明每个组件。

\textbf{Answer}: Three-cluster decoupled architecture on 72 A100-80GB GPUs:
\textbf{答案}：在72块A100-80GB GPU上的三集群解耦架构：

\textbf{Cluster 1 --- Generation (32 GPUs)}:
\textbf{集群1 --- 生成（32块GPU）}：

\begin{itemize}
  \item 8 vLLM instances, TP=4 each. PagedAttention + speculative decoding (1B draft model).
  \item Continuous batching, max 256 sequences in flight. INT8 weights for bandwidth.
  \item Output: (prompt, response, per-token log-probs). Throughput: $\sim$500 responses/minute.
  \item Stateless: just loads latest weights from shared store. Trivial recovery.
\end{itemize}

\begin{itemize}
  \item 8个vLLM实例，每个张量并行度（TP）=4。PagedAttention + 推测解码（1B草稿模型）。
  \item 连续批处理，最多256个序列在运行。INT8权重以节省带宽。
  \item 输出：（提示、响应、每个词元的对数概率）。吞吐量：约500个响应/分钟。
  \item 无状态：仅从共享存储加载最新权重。恢复简单。
\end{itemize}

\textbf{Cluster 2 --- Scoring (8 GPUs)}:
\textbf{集群2 --- 评分（8块GPU）}：

\begin{itemize}
  \item Reward model (70B, INT8 = 70GB) on 4 GPUs (TP=4).
  \item Reference model (70B, INT8) on 4 GPUs (TP=4). Computes per-token log-probs for KL.
  \item Output: reward scores + KL per token. Lightweight, batch inference.
\end{itemize}

\begin{itemize}
  \item 奖励模型（70B，INT8 = 70GB）占用4块GPU（TP=4）。
  \item 参考模型（70B，INT8）占用4块GPU（TP=4）。计算每个词元的对数概率用于KL。
  \item 输出：奖励分数 + 每个词元的KL。轻量级，批量推理。
\end{itemize}

\textbf{Cluster 3 --- Training (32 GPUs)}:
\textbf{集群3 --- 训练（32块GPU）}：

\begin{questionbox}[Q7: How do you handle the generation bottleneck? Quantify the solutions.]
\begin{questionbox}[Q7: 如何处理生成瓶颈？量化解决方案。]

\textbf{Answer}: Generation = 60--70\% of total RLHF wall-clock time. Root cause: autoregressive decoding is memory-bandwidth bound (arithmetic intensity $\approx 1$ FLOP/byte vs roofline of 156 FLOP/byte on A100).
\textbf{答案}：生成占RLHF总挂钟时间的60-70%。根本原因：自回归解码受限于内存带宽（算术强度 $\approx 1$ FLOP/字节，而A100的理论峰值可达156 FLOP/字节）。

\textbf{Solutions ranked by impact}:
\textbf{按影响排序的解决方案}：

\textbf{1. Decouple gen from training} (1.3--1.5$\times$ end-to-end): Run generation on separate hardware, overlap with training. The single biggest architectural win.
\textbf{1. 将生成与训练解耦}（端到端1.3-1.5倍）：在独立硬件上运行生成，与训练重叠。这是最大的架构收益。

\textbf{2. vLLM with PagedAttention} (2--4$\times$): Eliminates 60--80\% KV cache memory waste from internal fragmentation. Enables 3--4$\times$ larger batches = better bandwidth utilization.
\textbf{2. 使用PagedAttention的vLLM}（2-4倍）：消除因内部碎片造成的60-80% KV缓存内存浪费。支持3-4倍更大的批次 = 更好的带宽利用率。

\textbf{3. Continuous batching} (1.5--2$\times$): Don’t wait for longest sequence to finish. Start new sequences immediately in freed slots. Keeps GPUs busy.
\textbf{3. 连续批处理}（1.5-2倍）：不等最长序列完成。在空闲槽中立即开始新序列。保持GPU繁忙。

\textbf{4. Speculative decoding} (2--3$\times$): 1B draft model proposes 5 tokens. 70B model verifies all 5 in one forward pass (parallel!). Accept 3--4 on average $\rightarrow$ 3--4 tokens per forward pass instead of 1.
\textbf{4. 推测解码}（2-3倍）：1B草稿模型提出5个token。70B模型在一次前向传播中验证全部5个（并行！）。平均接受3-4个 $\rightarrow$ 每次前向传播生成3-4个token而非1个。

\textbf{5. INT8/FP8 for generation weights} (2$\times$): Halves the 140GB weight read per token. Quality loss is minimal because (a) we’re sampling with temperature anyway, and (b) only generation uses INT8, training stays BF16.
\textbf{5. 生成权重使用INT8/FP8}（2倍）：将每次token读取的140GB权重减半。质量损失极小，因为(a)我们本就在使用温度采样，(b)只有生成使用INT8，训练保持BF16。

\textbf{6. CUDA graphs + kernel fusion} (1.1--1.3$\times$): Eliminate Python/CUDA launch overhead. Fuse layernorm+attention+MLP into fewer kernels.
\textbf{6. CUDA图 + 内核融合}（1.1-1.3倍）：消除Python/CUDA启动开销。将layernorm+attention+MLP融合为更少的内核。

\textbf{Combined}: $1.5 \times 3 \times 1.5 \times 2.5 \times 2 \times 1.2 = 40\times$ over naive. In practice, diminishing returns limit total to $\sim$10--20$\times$ over naive implementation.
\textbf{综合效果}：相比于朴素实现，$1.5 \times 3 \times 1.5 \times 2.5 \times 2 \times 1.2 = 40$倍。实际上，边际收益递减使得总加速比限制在朴素实现的$\sim$10-20倍。

\emph{\textbf{Review:} Chapters~2 and~11 (Systems Foundations; System Architecture).}
\emph{\textbf{回顾：}第2章和第11章（系统基础；系统架构）。}

\end{questionbox}
\end{questionbox}

\begin{questionbox}[Q8: Explain weight synchronization in a decoupled system. How much staleness can you tolerate?]
\begin{questionbox}[Q8: 解释解耦系统中的权重同步。你能容忍多少陈旧性？]

\textbf{Answer}:
\textbf{答案}：

\textbf{The problem}: Generation cluster uses policy weights to produce responses. Training cluster updates those weights. They’re on different hardware. How to keep them in sync?
\textbf{问题}：生成集群使用策略权重生成响应。训练集群更新这些权重。它们位于不同的硬件上。如何保持同步？

\textbf{Why perfect sync is wasteful}: Full sync of 70B BF16 = 140GB. At InfiniBand 400Gb/s (50GB/s): 2.8s per sync. If you sync every step (every 50--90s), you spend 3--5\% of time on weight transfer. Acceptable, but unnecessary.
\textbf{为什么完美同步是浪费的}：70B BF16完全同步=140GB。在InfiniBand 400Gb/s（50GB/s）下：每次同步2.8秒。如果每一步同步（每50-90秒），你会花费3-5%的时间在权重传输上。可以接受，但并非必要。

\textbf{Staleness tolerance analysis}:
\textbf{陈旧性容忍度分析}：

\begin{itemize}
  \item Per-step policy change: $\sim$0.1\% (measured by mean param delta)
  \item 每步策略变化：$\sim$0.1%（通过平均参数变化量测量）
  \item 50 steps: $\sim$5\% cumulative drift
  \item 50步：$\sim$5%累积漂移
  \item PPO clip range: handles up to 20\% probability ratio deviation
  \item PPO裁剪范围：可处理高达20%的概率比偏差
  \item Empirical: 50-step staleness $\rightarrow$ $<$2\% quality degradation (measured by win-rate)
  \item 经验：50步陈旧性 $\rightarrow$ 质量下降$<$2%（通过胜率测量）
\end{itemize}

\textbf{Production strategy}:
\textbf{生产策略}：

\begin{enumerate}
  \item Every 50 training steps: push full BF16 checkpoint to shared store (2.8s transfer)
  \item 每50个训练步骤：将完整BF16检查点推送到共享存储（2.8秒传输）
  \item Generation cluster: non-blocking weight reload between batches
  \item 生成集群：在批次间进行非阻塞权重重载
  \item Delta compression (optional): Only send changed parameters (INT8 delta $\approx$ 5GB), apply as offset. 10$\times$ less bandwidth.
  \item 差分压缩（可选）：仅发送变化的参数（INT8差分约5GB），作为偏移量应用。带宽减少10倍。
  \item For very large scale (256+ GPUs): streaming sync --- continuously send small chunks in background. Average staleness: 5--10 steps.
  \item 对于超大规模（256+ GPU）：流式同步——在后台持续发送小块。平均陈旧性：5-10步。
\end{enumerate}

\textbf{Important subtlety}: Log-probs computed during generation use stale weights. The PPO ratio $\pi_\text{new}/\pi_\text{old}$ computes $\pi_\text{old}$ using these stale log-probs. This is fine because PPO is designed for off-policy corrections.
\textbf{重要细节}：生成期间计算的对数概率使用陈旧权重。PPO比率$\pi_\text{new}/\pi_\text{old}$使用这些陈旧的对数概率计算$\pi_\text{old}$。这没问题，因为PPO是为离策略修正设计的。

\emph{\textbf{Review:} Chapter~11 (System Architecture \& Infrastructure at Scale).}
\emph{\textbf{回顾：}第11章（系统架构与大规模基础设施）。}

\end{questionbox}
\end{questionbox}

\begin{questionbox}[Q9: How would you make this fault-tolerant at 512 GPUs?]
\begin{questionbox}[Q9: 如何在512 GPU规模下使其具备容错能力？]

\textbf{Answer}: At 512 GPUs, MTBF is 4--8 hours. A 5-day training run will see 15--30 failures.
\textbf{答案}：在512 GPU下，平均无故障时间（MTBF）为4-8小时。一次5天的训练运行将遇到15-30次故障。

\textbf{Architecture-level resilience}:
\textbf{架构级韧性}：

\begin{itemize}
  \item Generation cluster = stateless. Failed instance restarts in $<$60s (just load weights, no state).
  \item 生成集群 = 无状态。故障实例在$<$60秒内重启（仅加载权重，无状态）。
  \item Training cluster = stateful. Needs checkpoint-based recovery.
  \item 训练集群 = 有状态。需要基于检查点的恢复。
  \item Scoring cluster = stateless. Same as generation.
  \item 评分集群 = 无状态。与生成相同。
\end{itemize}

\textbf{Checkpointing strategy}:
\textbf{检查点策略}：

\begin{itemize}
  \item Frequency: Every 50--100 steps (5--10 min of training).
  \item 频率：每50-100步（训练5-10分钟）。
  \item Method: Async (non-blocking). Background thread writes while next step proceeds. Uses FSDP’s distributed save (each rank saves its shard in parallel).
  \item 方法：异步（非阻塞）。后台线程在下一步进行时写入。使用FSDP的分布式保存（每个rank并行保存其分片）。
  \item Contents: Model weights, optimizer states (Adam m/v), LR scheduler, RNG states, KL adaptive coefficient, global step counter, replay buffer pointer.
  \item 内容：模型权重、优化器状态（Adam m/v）、学习率调度器、随机数生成器状态、KL自适应系数、全局步数计数器、回放缓冲区指针。
  \item Storage: Local NVMe (fast, 30s for 70B) + async copy to S3/shared FS (durable).
  \item 存储：本地NVMe（快速，70B模型30秒）+ 异步复制到S3/共享文件系统（持久）。
  \item Retention: Keep last 3 checkpoints. Auto-delete older ones.
  \item 保留：保留最近3个检查点。自动删除更旧的。
\end{itemize}

\textbf{Detection and recovery flow}:
\textbf{检测与恢复流程}：

\begin{enumerate}
  \item NCCL collective timeout (60s) or heartbeat miss (10s) $\rightarrow$ failure detected.
  \item NCCL集合超时（60秒）或心跳丢失（10秒）$\rightarrow$ 检测到故障。
  \item Identify failed node(s) via NVML health check.
  \item 通过NVML健康检查识别故障节点。
  \item Option A (fast, $<$2 min): Torch Elastic shrinks world size, redistributes shards, continue with $N-1$ nodes. Request replacement in background.
  \item 方案A（快速，$<$2分钟）：Torch Elastic缩小world size，重新分配分片，以$N-1$个节点继续。后台请求替换。
  \item Option B (clean, $\sim$5 min): Bring up replacement node, rebuild process group, load last checkpoint, resume.
  \item 方案B（干净，$\sim$5分钟）：启动替换节点，重建进程组，加载最新检查点，恢复。
  \item Experience buffer is persisted --- no regeneration needed.
  \item 经验缓冲区已持久化——无需重新生成。
\end{enumerate}

\textbf{Prevention}: Pre-screening stress test (GEMM, memory, NVLink). ECC error monitoring (preemptive migration if errors spike). Hot spare nodes (pre-loaded with environment). Dual-rail InfiniBand for network redundancy.
\textbf{预防}：预筛选压力测试（GEMM、内存、NVLink）。ECC错误监控（如果错误激增则主动迁移）。热备节点（预加载环境）。双路InfiniBand实现网络冗余。

\emph{\textbf{Review:} Chapter~11 (System Architecture \& Infrastructure at Scale).}
\emph{\textbf{回顾：}第11章（系统架构与大规模基础设施）。}

\end{questionbox}
\end{questionbox}

\begin{questionbox}[Q10: How do you scale from 7B to 70B to 405B? What changes at each scale?]
\begin{questionbox}[Q10: 如何从7B扩展到70B再到405B？每个规模有哪些变化？]

\textbf{Answer}:
\textbf{答案}：

\textbf{7B (single 8-GPU node, hours)}:
\textbf{7B（单节点8 GPU，数小时）}：

\begin{itemize}
  \item Architecture: Monolithic (TRL default). All models on same GPUs.
  \item 架构：单体式（TRL默认）。所有模型在同一GPU上。
  \item Memory: LoRA + INT8 ref/RM fits in 8$\times$80GB easily.
  \item 内存：LoRA + INT8 参考模型/奖励模型轻松适配8$\times$80GB。
  \item Parallelism: DP=8 or FSDP within node. No network communication.
  \item 并行：DP=8或节点内FSDP。无网络通信。
  \item Hyperparams: LR=$5\times10^{-6}$, aggressive $\beta$=0.02, 50K--100K steps.
  \item 超参数：学习率=$5\times10^{-6}$，激进$\beta$=0.02，50K-100K步。
  \item Time: 4--12 hours per run. Fast iteration.
  \item 时间：每次运行4-12小时。快速迭代。
\end{itemize}

\textbf{70B (32--64 GPUs, 2--5 days)}:
\textbf{70B（32-64 GPU，2-5天）}：

\begin{itemize}
  \item Architecture: Semi-decoupled. vLLM generation + FSDP training.
  \item 架构：半解耦。vLLM生成 + FSDP训练。
  \item Memory: ZeRO-3 essential. Gradient checkpointing. INT8 ref/RM.
  \item 内存：ZeRO-3必不可少。梯度检查点。INT8参考模型/奖励模型。
  \item Parallelism: TP=8 intra-node (gen), FSDP inter-node (training).
  \item 并行：节点内张量并行TP=8（生成），节点间FSDP（训练）。
  \item Hyperparams: LR=$1.5\times10^{-6}$, moderate $\beta$=0.05, 10K--30K steps.
  \item 超参数：学习率=$1.5\times10^{-6}$，中等$\beta$=0.05，10K-30K步。
  \item Fault tolerance: Async checkpoints, monitoring, but manageable manually.
  \item 容错：异步检查点、监控，但可手动管理。
\end{itemize}

\textbf{405B (256--512 GPUs, 1--3 weeks)}:
\textbf{405B（256-512 GPU，1-3周）}：

(Content continues below...)
（内容如下文继续...）

\end{questionbox}
\end{questionbox}

```markdown
\begin{itemize}
  \item Architecture: Fully decoupled. Separate clusters. Weight store + queue.
  \item 架构：完全解耦。独立的集群。权重存储 + 队列。
  \item Memory: ZeRO-3 + TP=8 + PP=2 for training. INT4 generation.
  \item 内存：训练时使用 ZeRO-3 + TP=8 + PP=2。推理时使用 INT4 生成。
  \item Parallelism: 3D parallelism (TP$\times$PP$\times$DP = 8$\times$2$\times$16 = 256 GPUs training).
  \item 并行策略：三维并行（TP$\times$PP$\times$DP = 8$\times$2$\times$16 = 256 块 GPU 训练）。
  \item Hyperparams: LR=$5\times10^{-7}$, very conservative $\beta$=0.1, 2K--5K steps.
  \item 超参数：学习率 = $5\times10^{-7}$，非常保守的 $\beta$=0.1，训练步数 2K--5K。
  \item Fault tolerance: Mandatory. Elastic training, redundant checkpoints, hot spares.
  \item 容错：必需。弹性训练、冗余检查点、热备。
  \item Key change: Much less RL training needed (model is already very capable from pretraining). But each step is 50$\times$ more expensive, so instability is catastrophic.
  \item 关键变化：所需的 RL 训练量大大减少（模型经过预训练已经非常强大）。但每一步的成本是原来的 50 倍，因此不稳定性是灾难性的。
\end{itemize}

\textbf{Paradox}: Larger models are actually \emph{easier to RL-train per step} (more stable, smoother loss landscape). But the cost of instability scales with model size --- a bad run at 405B wastes \$100K+ in compute.
\textbf{悖论}：更大的模型实际上在每一步上 \emph{更容易进行 RL 训练}（更稳定，损失曲面更平滑）。但不稳定性的成本随模型规模增长——一次失败的 405B 模型运行会浪费超过 10 万美元的计算资源。

\emph{\textbf{Review:} Chapter~11 (System Architecture \& Infrastructure at Scale).}
\emph{\textbf{回顾：}第 11 章（系统架构与大规模基础设施）。}
\end{questionbox}


\section{Practical and Debugging Questions}
\label{practical-and-debugging-questions}
\section{实践与调试问题}
\label{practical-and-debugging-questions}


\begin{questionbox}[Q11: Reward score is increasing but model quality is declining. Diagnose and fix.]
\textbf{Answer}: Classic \textbf{reward hacking / Goodhart’s Law}.
\textbf{答案}：经典的 \textbf{奖励黑客（reward hacking）/ 古德哈特定律（Goodhart’s Law）}。

\textbf{Diagnostic protocol}:
\textbf{诊断流程}：

\begin{enumerate}
  \item \textbf{Check response length}: Plot mean length over training. Growing monotonically? = Length exploit (RM gives higher scores to longer responses).
  \item \textbf{检查回复长度}：绘制训练过程中平均回复长度的曲线。是否单调增长？= 长度利用（奖励模型对更长的回复给出更高分数）。
  \item \textbf{Check KL divergence}: $>$15? = Policy has diverged too far from reference. Lost capabilities.
  \item \textbf{检查 KL 散度}：是否大于 15？= 策略偏离参考模型过远，能力丢失。
  \item \textbf{Check diversity}: Unique trigrams per response. Dropping? = Mode collapse (repeating same high-reward pattern).
  \item \textbf{检查多样性}：每条回复中独特的三元组数量。是否在下降？= 模式坍缩（重复相同的高奖励模式）。
  \item \textbf{Manual inspection}: Read 20 highest-reward responses. What pattern do they share? (e.g., all start with ``Great question!'', all use bullet points, excessive hedging).
  \item \textbf{人工检查}：阅读 20 条最高奖励的回复。它们有什么共同模式？（例如，都以“好问题！”开头、全部使用项目符号、过度含糊其辞）。
  \item \textbf{Win-rate}: Evaluate against SFT baseline on held-out prompts. If flat/declining while RM rises = confirmed exploit.
  \item \textbf{胜率}：在保留的提示上对比 SFT 基线进行评估。如果胜率持平或下降而奖励模型分数上升，则确认存在利用行为。
\end{enumerate}

\textbf{Immediate fixes}:
\textbf{即时修复措施}：

\begin{itemize}
  \item Roll back to last checkpoint where win-rate was improving
  \item 回滚到胜率仍在提升的最后一个检查点
  \item Increase $\beta$ by 2--3$\times$ (stronger KL penalty)
  \item 将 $\beta$ 增大 2--3 倍（更强的 KL 惩罚）
  \item Add explicit length penalty: $r' = r - 0.001 \cdot \max(0, \text{len} - 500)$
  \item 添加显式的长度惩罚：$r' = r - 0.001 \cdot \max(0, \text{len} - 500)$
\end{itemize}

\textbf{Structural fixes (prevent recurrence)}:
\textbf{结构性修复（防止复发）}：

\begin{itemize}
  \item RM ensemble: Train 3--5 RMs on different data splits. Use min or mean. Exploits are model-specific.
  \item 奖励模型集成：在不同数据划分上训练 3--5 个奖励模型。使用最小值或均值。利用行为具有模型特异性。
  \item RM refresh: Every 2000 steps, generate from current policy, get human labels, retrain RM.
  \item 奖励模型刷新：每 2000 步，用当前策略生成回复，获取人工标注，重新训练奖励模型。
  \item Multi-objective reward: Combine helpfulness + harmlessness + conciseness with separate RMs.
  \item 多目标奖励：用独立的奖励模型组合有用性、无害性和简洁性。
  \item Early stopping on win-rate (not RM score). The metric you optimize should differ from training signal.
  \item 基于胜率（而非奖励模型分数）进行早停。优化的指标应与训练信号不同。
\end{itemize}

\emph{\textbf{Review:} Chapters~9 and~11 (Reward Model Training; System Architecture).}
\emph{\textbf{回顾：}第 9 章和第 11 章（奖励模型训练；系统架构）。}
\end{questionbox}


\begin{questionbox}[Q12: How do you decide the prompt distribution for RL training?]
\textbf{Answer}: Prompt quality is the most underrated factor in RLHF. Bad prompts = no learning signal.
\textbf{答案}：提示质量是 RLHF 中最被低估的因素。糟糕的提示 = 无学习信号。

\textbf{Composition (my default mix)}:
\textbf{构成（我的默认混合比例）}：

\begin{itemize}
  \item 40\% real user traffic (represents actual use cases)
  \item 40\% 真实用户流量（代表实际使用场景）
  \item 30\% synthetic (LLM-generated, fills gaps in coverage --- rare topics, edge cases)
  \item 30\% 合成数据（由 LLM 生成，填补覆盖空白——罕见主题、边缘情况）
  \item 20\% curriculum (graduated difficulty --- start easy, increase complexity as model improves)
  \item 20\% 课程式数据（难度递进——从简单开始，随模型改进增加复杂度）
  \item 10\% adversarial (red-team prompts, jailbreak attempts, ambiguous instructions)
  \item 10\% 对抗性数据（红队提示、越狱尝试、模糊指令）
\end{itemize}

\textbf{Critical: The Goldilocks Filter}:
\textbf{关键：金发姑娘过滤器（Goldilocks Filter）}：

\begin{enumerate}
  \item For each candidate prompt, generate 4--8 responses with current model.
  \item 对每个候选提示，用当前模型生成 4--8 条回复。
  \item Score with RM. Compute pass rate (fraction above threshold).
  \item 用奖励模型评分。计算通过率（超过阈值的比例）。
  \item Keep only prompts with 20--80\% pass rate:
  \item 仅保留通过率在 20\%--80\% 的提示：
\end{enumerate}

\begin{itemize}
  \item $<$20\%: Too hard. Model almost always fails $\rightarrow$ all negative advantages $\rightarrow$ no useful gradient.
  \item 低于 20\%：太难。模型几乎总是失败 $\rightarrow$ 全部为负优势 $\rightarrow$ 无有用梯度。
  \item $>$80\%: Too easy. Model almost always succeeds $\rightarrow$ all positive advantages $\rightarrow$ no contrast.
  \item 高于 80\%：太易。模型几乎总是成功 $\rightarrow$ 全部为正优势 $\rightarrow$ 无对比。
  \item 20--80\%: Perfect. Mix of successes and failures $\rightarrow$ clear signal about what works.
  \item 20\%--80\%：完美。成功与失败混合 $\rightarrow$ 关于有效策略的清晰信号。
\end{itemize}

\begin{enumerate}
  \setcounter{enumi}{3}
  \item Re-filter every 500 training steps (model improves, difficulty distribution shifts).
  \item 每 500 训练步重新过滤一次（模型性能提升，难度分布发生变化）。
\end{enumerate}

\textbf{Topic diversity}: Ensure no single topic dominates ($<$10\% per category). Use embedding clustering to verify coverage. Otherwise the model over-optimizes for dominant topics.
\textbf{主题多样性}：确保没有单一主题占主导（每个类别少于 10\%）。使用嵌入聚类验证覆盖范围。否则模型会过度优化主导主题。

\emph{\textbf{Review:} Chapters~7 and~9 (GRPO; Reward Model Training).}
\emph{\textbf{回顾：}第 7 章和第 9 章（GRPO；奖励模型训练）。}
\end{questionbox}


\begin{questionbox}[Q13: LoRA vs full fine-tuning for RLHF. When would you use each?]
\textbf{Answer}:
\textbf{答案}：

\textbf{LoRA} (Low-Rank Adaptation, $r$=64, $\alpha$=16):
\textbf{LoRA（低秩适配，Low-Rank Adaptation）}，$r$=64，$\alpha$=16：

\begin{itemize}
  \item Trainable params: $\sim$0.2\% of model (200M for 70B)
  \item 可训练参数：约模型参数的 0.2\%（对于 70B 模型约为 2 亿）
  \item Memory savings: No separate reference model needed (base model = reference)! Saves 140GB.
  \item 内存节省：无需独立参考模型（基础模型即为参考模型）！节省 140GB。
  \item Stability: Inherently more stable (low-rank constraint limits how far policy can drift)
  \item 稳定性：天生更稳定（低秩约束限制了策略的漂移范围）
  \item Speed: Faster per-step (fewer params to update), but may need more steps
  \item 速度：每步更快（需更新的参数更少），但可能需要更多步数
  \item Quality ceiling: 90--95\% of full FT quality typically
  \item 质量上限：通常达到全量微调质量的 90\%--95\%
\end{itemize}

\textbf{Full fine-tuning}:
\textbf{全量微调}：

\begin{itemize}
  \item All parameters updated. Maximum expressiveness.
  \item 所有参数更新。表达力最强。
  \item Needs separate reference model copy (140GB for 70B). Or very frequent checkpointing to ``anchor.''
  \item 需要独立的参考模型副本（70B 模型需 140GB）。或非常频繁地检查点作为“锚点”。
  \item Higher risk of catastrophic forgetting. Need lower LR ($3\times$ lower than LoRA) and stronger $\beta$.
  \item 灾难性遗忘风险更高。需要更低的学习率（比 LoRA 低 3 倍）和更强的 $\beta$。
  \item Better when: large distributional shift needed (new language, very different style), LoRA hits capacity limit.
  \item 更适用于：需要大的分布偏移（新语言、非常不同的风格），LoRA 达到容量上限时。
\end{itemize}

\textbf{My decision framework}:
\textbf{我的决策框架}：

\begin{enumerate}
  \item Start with LoRA ($r$=64). It’s 3$\times$ cheaper and more stable.
  \item 从 LoRA（$r$=64）开始。它便宜 3 倍且更稳定。
  \item Monitor gradient norms on LoRA matrices. If consistently $>$1.0 (high relative to parameter count): LoRA is capacity-limited.
  \item 监控 LoRA 矩阵上的梯度范数。如果持续大于 1.0（相对于参数数量偏高），说明 LoRA 受限于容量。
  \item Switch to full FT only when: win-rate plateaus AND gradient analysis suggests capacity limitation.
  \item 仅在以下情况切换到全量微调：胜率停滞，且梯度分析表明存在容量限制。
  \item For full FT: use $\text{LR}/3$, $\beta \times 2$, more frequent checkpointing, and early stopping based on win-rate.
  \item 对于全量微调：使用 $\text{LR}/3$、$\beta \times 2$、更频繁的检查点以及基于胜率的早停。
\end{enumerate}

\textbf{Hybrid}: LoRA for alignment/safety (small behavioral shift) + Full FT for capabilities/reasoning (large shift needed).
\textbf{混合方案}：LoRA 用于对齐/安全（较小行为变化）+ 全量微调用于能力/推理（需要较大变化）。

\emph{\textbf{Review:} Chapters~1 and~10 (LLM Architecture; SFT Best Practices).}
\emph{\textbf{回顾：}第 1 章和第 10 章（LLM 架构；SFT 最佳实践）。}
\end{questionbox}


\begin{questionbox}[Q14: Process Reward Models (PRM) vs Outcome Reward Models (ORM). Design a PRM system.]
\textbf{Answer}:
\textbf{答案}：

\textbf{ORM}: Scores the final answer only. ``Is the response good overall?'' Simple but can’t identify \emph{where} reasoning went wrong.
\textbf{ORM（结果奖励模型，Outcome Reward Model）}：仅对最终答案评分。“整体回复好吗？”简单但无法识别推理出错的具体位置。

\textbf{PRM}: Scores each intermediate step. ``Is step 3 of this derivation correct?'' Much more informative but harder to train.
\textbf{PRM（过程奖励模型，Process Reward Model）}：对每个中间步骤评分。“这个推导的第 3 步正确吗？”信息量大得多但训练更困难。

\textbf{PRM advantages for reasoning}:
\textbf{PRM 在推理上的优势}：

\begin{itemize}
  \item Identifies exactly where reasoning fails (step-level credit assignment)
  \item 精确定位推理失败的位置（步骤级信用分配）
  \item Enables tree search: expand only branches with high step scores
  \item 支持树搜索：仅扩展步骤得分高的分支
  \item Less reward hacking: can’t get high score from wrong steps + lucky final answer
  \item 更少的奖励黑客行为：无法通过错误步骤 + 幸运最终答案获得高分
  \item PRM + best-of-N beats ORM + best-of-N by 10--20\% on MATH benchmarks
  \item PRM + best-of-N 在 MATH 基准上比 ORM + best-of-N 高出 10\%--20\%
\end{itemize}

\textbf{Training a PRM}:
\textbf{训练 PRM}：

\begin{enumerate}
  \item \textbf{Data collection} (Monte Carlo approach):
  \item \textbf{数据收集}（蒙特卡洛方法）：
\end{enumerate}

\begin{itemize}
  \item For each problem, generate reasoning trace step by step
  \item 对每个问题，逐步生成推理轨迹
  \item At each step $k$, complete the solution $M$ times ($M=32$) from that point
  \item 在每一步 $k$，从该点起完成解决方案 $M$ 次（$M=32$）
  \item Step score = fraction of completions that reach correct answer
  \item 步骤得分 = 能到达正确答案的完成比例
  \item Steps where score drops significantly = the ``mistake'' steps
  \item 得分显著下降的步骤 = “错误”步骤
\end{itemize}

\begin{enumerate}
  \setcounter{enumi}{1}
  \item \textbf{Labeling}: Step is ``correct'' if its completion rate $>$ 50\%, ``incorrect'' if $<$ 20\%.
  \item \textbf{标注}：如果步骤的完成率 > 50\%，则标记为“正确”；如果 < 20\%，则标记为“错误”。
  \item \textbf{Model}: Same architecture as base model + classification head per token position. Train with binary cross-entropy on step labels.
  \item \textbf{模型}：与基础模型相同的架构 + 每个 token 位置的分类头。使用步骤标签上的二元交叉熵损失进行训练。
  \item \textbf{Inference}: Score each step. If any step scores $<$0.3, flag the trace as flawed.
  \item \textbf{推理}：对每个步骤进行评分。如果任何步骤得分 < 0.3，则将轨迹标记为有缺陷。
\end{enumerate}
```

**Using PRM in RLHF**: Per-token rewards from PRM feed directly into GAE. Each token gets immediate feedback, not just end-of-sequence. This dramatically improves credit assignment for long reasoning chains.

**在RLHF中使用PRM**：来自PRM的每令牌奖励直接馈入GAE。每个令牌都能获得即时反馈，而不仅仅是序列结束。这极大地改善了长推理链中的信用分配。

\emph{\textbf{Review:} Chapters~9 and~13 (Reward Model Training; RL for Large Reasoning Models).}
\end{questionbox}

\emph{\textbf{复习：}第9章和第13章（奖励模型训练；大型推理模型的强化学习）。}
\end{questionbox}

\begin{questionbox}[Q15: How do you evaluate whether RL actually improved the model?]
\textbf{Answer}: Multi-faceted evaluation (no single metric captures ``quality''):

\begin{questionbox}[Q15：如何评估强化学习是否真正改进了模型？]
\textbf{答案}：多维度评估（没有单一指标能捕捉“质量”）：

\textbf{1. Win-rate} (most important, most reliable):

\textbf{1. 胜率}（最重要，最可靠）：

\begin{itemize}
  \item 500+ diverse prompts. LLM judge (GPT-4 or Claude) picks winner in blind A/B comparison vs SFT baseline.
  \item Target: $>$55\% win-rate = meaningful improvement. $>$65\% = strong improvement.
  \item Use position-debiasing (swap A/B order, average). Report confidence intervals.
\end{itemize}

\begin{itemize}
  \item 500+多样化的提示词。LLM评判器（GPT-4或Claude）在盲A/B比较中选出胜者，与SFT基线对比。
  \item 目标：胜率>55% = 有意义的改进。>65% = 强烈改进。
  \item 使用位置去偏（交换A/B顺序，取平均）。报告置信区间。
\end{itemize}

\textbf{2. Capability benchmarks} (regression detection):

\textbf{2. 能力基准测试}（回归检测）：

\begin{itemize}
  \item MMLU (knowledge), HumanEval (code), MATH (reasoning), MT-Bench (multi-turn).
  \item Any $>$2\% drop = concerning alignment tax. Investigate which categories degraded.
\end{itemize}

\begin{itemize}
  \item MMLU（知识）、HumanEval（代码）、MATH（推理）、MT-Bench（多轮）。
  \item 任何下降>2% = 值得关注的对齐代价。调查哪些类别退化。
\end{itemize}

\textbf{3. Category-specific evals}:

\textbf{3. 类别特定评估}：

\begin{itemize}
  \item Safety: refusal rate on harmful prompts (should increase)
  \item Truthfulness: TruthfulQA score (should increase or stay flat)
  \item Helpfulness: task completion rate on instruction-following benchmarks
\end{itemize}

\begin{itemize}
  \item 安全性：对有害提示词的拒绝率（应增加）
  \item 真实性：TruthfulQA得分（应增加或持平）
  \item 有用性：指令遵循基准测试中的任务完成率
\end{itemize}

\textbf{4. Distributional metrics}:

\textbf{4. 分布指标}：

\begin{itemize}
  \item Response length distribution (shouldn’t shift dramatically)
  \item Vocabulary diversity (unique tokens per response)
  \item Format compliance (if trained for specific format)
\end{itemize}

\begin{itemize}
  \item 响应长度分布（不应显著偏移）
  \item 词汇多样性（每次响应的唯一令牌数）
  \item 格式合规性（如果针对特定格式训练）
\end{itemize}

\textbf{5. Human evaluation} (gold standard, expensive):

\textbf{5. 人工评估}（黄金标准，昂贵）：

\begin{itemize}
  \item Blind A/B with 3+ skilled annotators per example. Inter-annotator agreement $>$ 70\%.
  \item Only for final model selection, not during training (too slow/expensive).
\end{itemize}

\begin{itemize}
  \item 对每个示例进行盲A/B评估，由3名以上熟练标注员参与。标注员间一致性>70%。
  \item 仅用于最终模型选择，不用于训练期间（太慢/太贵）。
\end{itemize}

\textbf{Red flags}: RM score up + win-rate flat = reward hacking, not real improvement. Win-rate up + benchmarks down = alignment tax too high, reduce RL strength.

\textbf{警示信号}：RM分数上升 + 胜率持平 = 奖励破解，并非真正的改进。胜率上升 + 基准测试下降 = 对齐代价过高，降低强化学习强度。

\emph{\textbf{Review:} Chapter~14 (LLM Evaluation).}
\end{questionbox}

\emph{\textbf{复习：}第14章（LLM评估）。}
\end{questionbox}

\begin{questionbox}[Q16: Describe the reward model training pipeline end-to-end.]
\textbf{Answer}:

\begin{questionbox}[Q16：端到端描述奖励模型训练流程。]
\textbf{答案}：

\textbf{Phase 1 --- Data Generation}:

\textbf{阶段1 --- 数据生成}：

\begin{itemize}
  \item Collect 50K--100K diverse prompts (real traffic + synthetic)
  \item Generate 4--8 responses per prompt at varying temperatures (0.3, 0.7, 1.0) and from multiple models (diversity is key --- if all responses are similar, preferences are uninformative)
  \item Total: 200K--800K candidate responses
\end{itemize}

\begin{itemize}
  \item 收集5万--10万个多样化提示词（真实流量+合成数据）
  \item 对每个提示词在不同温度（0.3、0.7、1.0）下并来自多个模型生成4--8个响应（多样性是关键——如果所有响应相似，则偏好信息无效）
  \item 总计：20万--80万个候选响应
\end{itemize}

\textbf{Phase 2 --- Preference Collection}:

\textbf{阶段2 --- 偏好收集}：

\begin{itemize}
  \item Option A (expensive, best quality): Human annotators compare pairs. 3 annotators per pair. Cost: \$2--5 per comparison.
  \item Option B (cheap, 85--90\% agreement with humans): LLM judge (GPT-4/Claude). 10$\times$ cheaper. Good for scale.
  \item Format: (prompt, chosen response, rejected response). Pairs with annotator disagreement ($<$70\% agreement) are discarded.
  \item Final dataset: 100K--500K pairs.
\end{itemize}

\begin{itemize}
  \item 选项A（昂贵，质量最佳）：人工标注员比较成对。每对3名标注员。成本：每次比较2--5美元。
  \item 选项B（便宜，与人类一致性85--90%）：LLM评判器（GPT-4/Claude）。便宜10倍。适合规模化。
  \item 格式：（提示词，选定响应，拒绝响应）。标注员意见不一致（一致性<70%）的对被丢弃。
  \item 最终数据集：10万--50万对。
\end{itemize}

\textbf{Phase 3 --- Training}:

\textbf{阶段3 --- 训练}：

\begin{itemize}
  \item Architecture: Same as base LLM + scalar head (one regression output per sequence).
  \item Loss: $\mathcal{L} = -\mathbb{E}[\log\sigma(r(x,y_w) - r(x,y_l))]$ (Bradley-Terry).
  \item Training: \textbf{1 epoch only!} RMs overfit extremely fast. Validation accuracy 68--75\% is good (higher often means overfitting to annotation artifacts).
  \item Tricks: Center rewards around 0 (subtract running mean). Check for length bias (if correlation between length and score $>$ 0.3, add length penalty to training).
\end{itemize}

\begin{itemize}
  \item 架构：与基础LLM相同 + 标量头（每个序列一个回归输出）。
  \item 损失函数：$\mathcal{L} = -\mathbb{E}[\log\sigma(r(x,y_w) - r(x,y_l))]$（Bradley-Terry模型）。
  \item 训练：\textbf{仅1个epoch！}RM过拟合极快。验证准确率68--75%即为良好（更高通常意味着过度拟合标注伪影）。
  \item 技巧：将奖励中心化为0（减去运行均值）。检查长度偏差（如果长度与分数的相关性>0.3，则在训练中添加长度惩罚）。
\end{itemize}

\textbf{Phase 4 --- Validation}:

\textbf{阶段4 --- 验证}：

\begin{itemize}
  \item Hold-out preference pairs: accuracy should be 68--75\%.
  \item Agreement with humans on new data: $>$ 80\%.
  \item Length bias check: correlation between response length and RM score should be $<$ 0.2.
  \item Consistency check: same prompt, paraphrased responses should get similar scores.
\end{itemize}

\begin{itemize}
  \item 保留的偏好对：准确率应为68--75%。
  \item 与新数据的人工一致性：> 80%。
  \item 长度偏差检查：响应长度与RM分数之间的相关性应 < 0.2。
  \item 一致性检查：相同提示词，改写后的响应应获得相似分数。
\end{itemize}

\emph{\textbf{Review:} Chapter~9 (Reward Model Training).}
\end{questionbox}

\emph{\textbf{复习：}第9章（奖励模型训练）。}
\end{questionbox}

\begin{questionbox}[Q17: What happens when KL divergence explodes? Root cause and fix.]
\textbf{Answer}:

\begin{questionbox}[Q17：当KL散度爆炸时会发生什么？根本原因和修复方法。]
\textbf{答案}：

\textbf{What KL measures}: Average log-ratio between current policy and reference: $D_\text{KL} = \mathbb{E}_{y\sim\pi_\theta}[\log(\pi_\theta(y|x)/\pi_\text{ref}(y|x))]$. KL=0 means identical to reference. KL=10 means the policy puts 10 nats more probability on its preferred outputs.

\textbf{KL衡量什么}：当前策略与参考策略之间的平均对数比率：$D_\text{KL} = \mathbb{E}_{y\sim\pi_\theta}[\log(\pi_\theta(y|x)/\pi_\text{ref}(y|x))]$。KL=0表示与参考策略相同。KL=10表示策略在其偏好的输出上多了10个nat的概率。

\textbf{Healthy range}: 3--10 during training. Slowly increasing is fine. Sudden spike = problem.

\textbf{健康范围}：训练期间3--10。缓慢增加是可以的。突然激增=问题。

\textbf{Root causes of KL explosion}:

\textbf{KL爆炸的根本原因}：

\begin{enumerate}
  \item \textbf{Learning rate too high}: Policy takes giant step, diverges from reference. Fix: reduce LR by 2--5$\times$.
  \item \textbf{Reward hacking}: Found an exploit that gets high reward far from reference behavior. Fix: increase $\beta$, add RM ensemble.
  \item \textbf{Mode collapse}: Policy concentrates on one response template. KL is high at that template, low everywhere else. Fix: increase entropy bonus, increase temperature.
  \item \textbf{Bad batch}: One unlucky batch with extreme advantages pushed the policy. Fix: gradient clipping, reduce mini-batch size.
  \item \textbf{Value function diverged}: Wrong advantage estimates cause wrong updates. Fix: reduce value function LR, or switch to GRPO (no value function).
\end{enumerate}

\begin{enumerate}
  \item \textbf{学习率过高}：策略迈出大步，偏离参考策略。修复：将学习率降低2--5倍。
  \item \textbf{奖励破解}：发现了远离参考行为却能获得高奖励的漏洞。修复：增加$\beta$，添加RM集成。
  \item \textbf{模式坍缩}：策略集中于一个响应模板。该模板上的KL高，其他地方低。修复：增加熵奖励，提高温度。
  \item \textbf{不良批次}：一个不幸的批次带有极端优势值，导致策略偏离。修复：梯度裁剪，减小小批量大小。
  \item \textbf{价值函数发散}：错误的优势估计导致错误的更新。修复：降低价值函数的学习率，或改用GRPO（无价值函数）。
\end{enumerate}

\textbf{Recovery protocol}:

\textbf{恢复协议}：

\begin{enumerate}
  \item Detect: KL $>$ 15 for 50+ steps, or KL jumps $>$5 in one step.
  \item Immediate: Load last clean checkpoint (KL $<$ 10).
  \item Adjust: Reduce LR by 50\%. Increase $\beta$ by 2$\times$. Lower cliprange to 0.1.
  \item Resume: Monitor closely for first 200 steps.
\end{enumerate}

\begin{enumerate}
  \item 检测：KL > 15持续50步以上，或KL单步跳升>5。
  \item 立即：加载最后一个干净的检查点（KL < 10）。
  \item 调整：将学习率降低50%。将$\beta$提高2倍。将裁剪范围降低至0.1。
  \item 恢复：在前200步中密切监控。
\end{enumerate}

\emph{\textbf{Review:} Chapters~5 and~7 (PPO; GRPO).}
\end{questionbox}

\emph{\textbf{复习：}第5章和第7章（PPO；GRPO）。}
\end{questionbox}

\begin{questionbox}[Q18: Compare monolithic vs decoupled RLHF architectures. When does each make sense?]
\textbf{Answer}:

\begin{questionbox}[Q18：比较整体式与解耦式RLHF架构。每种分别适用于什么情况？]
\textbf{答案}：

\textbf{Monolithic} (TRL default: single process, all models on same GPUs):

\textbf{整体式}（TRL默认：单进程，所有模型在相同GPU上）：

\begin{itemize}
  \item Pros: Simple code. No distributed systems complexity. Easy debugging.
  \item Cons: GPUs idle 60\% of time (compute idle during gen, bandwidth idle during training). Doesn’t scale past $\sim$16 GPUs efficiently. All models compete for same memory.
  \item Use when: Model $\leq$ 13B, single node, research/prototyping.
\end{itemize}

\begin{itemize}
  \item 优点：代码简单。无分布式系统复杂性。易于调试。
  \item 缺点：GPU有60%的时间空闲（生成期间计算空闲，训练期间带宽空闲）。无法高效扩展到约16个GPU以上。所有模型争夺相同的内存。
  \item 适用场景：模型≤13B，单节点，研究/原型开发。
\end{itemize}

\textbf{Semi-decoupled} (vLLM gen + FSDP training, same cluster):

\textbf{半解耦式}（vLLM生成 + FSDP训练，同一集群）：

\begin{itemize}
  \item Pros: Better utilization (gen and training can partially overlap). Scales to 64 GPUs.
  \item Cons: Still shares hardware, can’t optimize independently. More complex than monolithic.
  \item Use when: 13B--70B, 2--8 nodes, production experiments.
\end{itemize}

\begin{itemize}
  \item 优点：利用率更高（生成和训练可部分重叠）。可扩展到64个GPU。
  \item 缺点：仍共享硬件，无法独立优化。比整体式更复杂。
  \item 适用场景：13B--70B，2--8个节点，生产实验。
\end{itemize}

\textbf{Fully decoupled} (separate clusters connected by queues):

\textbf{全解耦式}（通过队列连接的独立集群）：

\begin{itemize}
  \item Pros: Each cluster optimized for its workload. Gen scales independently from training. Gen cluster is stateless (trivial fault tolerance). Scales to hundreds of GPUs.
  \item Cons: Distributed systems complexity. Weight staleness. Queue management. Network overhead.
  \item Use when: $\geq$ 70B production training. Need scale, fault tolerance, high utilization.
\end{itemize}

\begin{itemize}
  \item 优点：每个集群针对其工作负载优化。生成可独立于训练扩展。生成集群是无状态的（容错简单）。可扩展到数百个GPU。
  \item 缺点：分布式系统复杂性。权重陈旧性。队列管理。网络开销。
  \item 适用场景：≥70B的生产训练。需要规模、容错、高利用率。
\end{itemize}

\textbf{The key insight}: Generation is bandwidth-bound, training is compute-bound. Same hardware can’t optimize for both. Decoupling lets gen nodes have: more memory bandwidth, INT8 weights, large batch. Training nodes have: full BF16 precision, Flash Attention, FSDP sharding.

\textbf{关键见解}：生成受带宽限制，训练受计算限制。同一硬件无法同时优化两者。解耦使生成节点能够拥有：更高的内存带宽、INT8权重、大批量。训练节点拥有：完整的BF16精度、Flash Attention、FSDP分片。

\emph{\textbf{Review:} Chapter~11 (System Architecture \& Infrastructure at Scale).}
\end{questionbox}

\emph{\textbf{复习：}第11章（系统架构与大规模基础设施）。}
\end{questionbox}

\begin{questionbox}[Q19: How do you set up curriculum learning for RL training?]
\textbf{Answer}: Curriculum = gradually increasing difficulty so the model learns progressively.

\begin{questionbox}[Q19：如何为强化学习训练设置课程学习？]
\textbf{答案}：课程学习 = 逐步增加难度，使模型渐进式学习。

## Why it matters: If you throw the hardest prompts at a weak model, it gets all-negative rewards $\rightarrow$ no learning signal (everything is equally bad). If you start easy, the model develops basic capabilities, then builds on them.
## 为什么重要：如果你把最难的问题扔给一个弱模型，它只会得到全部为负的奖励 $\rightarrow$ 没有学习信号（所有东西都一样糟糕）。如果你从简单的开始，模型就会发展出基本能力，然后在这基础上逐步构建。

## Implementation:
## 实现方式：

\begin{enumerate}
  \item \textbf{Difficulty scoring}: Rate each prompt by current model’s pass rate (from Goldilocks filtering). Easy = $>$80\% pass, Medium = 30--80\%, Hard = $<$30\%.
  \item \textbf{难度评分}：根据当前模型的通过率（来自 Goldilocks 过滤）对每个提示进行评分。简单 = 通过率 $>$80\%，中等 = 30--80\%，困难 = $<$30\%。
  \item \textbf{Schedule}: Steps 0--1000: 70\% easy, 20\% medium, 10\% hard. Steps 1000--5000: 30\% easy, 50\% medium, 20\% hard. Steps 5000+: 10\% easy, 40\% medium, 50\% hard.
  \item \textbf{训练计划}：步骤 0--1000：70\% 简单，20\% 中等，10\% 困难。步骤 1000--5000：30\% 简单，50\% 中等，20\% 困难。步骤 5000+：10\% 简单，40\% 中等，50\% 困难。
  \item \textbf{Dynamic adjustment}: Every 500 steps, re-evaluate difficulty distribution. Prompts the model has ``mastered'' (pass rate $>$ 95\%) get retired. New harder prompts are introduced.
  \item \textbf{动态调整}：每 500 步重新评估难度分布。模型已“掌握”（通过率 $>$ 95\%）的提示会被淘汰。引入新的更难提示。
  \item \textbf{For GRPO specifically}: Curriculum ensures groups always have a mix of successes and failures. Without curriculum, hard prompts give all-zero groups (useless).
  \item \textbf{特别针对 GRPO}：课程学习确保每个组始终包含成功和失败的样本。没有课程学习，困难提示会产生全零组（无用）。
\end{enumerate}

## Evidence: DeepSeek-R1 used implicit curriculum --- starting with easy math/code problems, the model developed basic reasoning, then solved progressively harder problems without explicit scheduling.
## 证据：DeepSeek-R1 使用了隐式课程——从简单的数学/代码问题开始，模型发展了基本推理能力，然后无需显式调度就能解决逐渐变难的问题。

\emph{\textbf{Review:} Chapters~7 and~12 (GRPO; LLM Agentic Training).}
\emph{\textbf{复习：}第 7 章和第 12 章（GRPO；LLM 智能体训练）。}
\end{questionbox}

\begin{questionbox}[Q20: You have a budget of 64 A100-80GB GPUs and need to RL-train a 70B model. Design the allocation.]
\begin{questionbox}[Q20：你拥有 64 块 A100-80GB GPU，需要 RL 训练一个 70B 模型。请设计分配方案。]

\textbf{Answer}: 8 nodes $\times$ 8 GPUs = 64 total. Need to split across generation, scoring, and training.
\textbf{答案}：8 个节点 $\times$ 8 块 GPU = 共 64 块。需要在生成、评分和训练之间分配。

\textbf{My allocation}:
\textbf{我的分配方案}：

\begin{itemize}
  \item \textbf{Generation}: 24 GPUs (3 nodes). 6 vLLM instances with TP=4. INT8 weights = 70GB/model, leaves room for KV cache. Continuous batching, batch $\approx$ 128 total.
  \item \textbf{生成}：24 块 GPU（3 个节点）。6 个 vLLM 实例，TP=4。INT8 权重 = 70GB/模型，为 KV 缓存留出空间。连续批处理，总 batch $\approx$ 128。
  \item \textbf{Scoring}: 8 GPUs (1 node). RM (INT8, TP=4) + Reference model (INT8, TP=4) on same node. Or share 4 GPUs with TP=4 alternating between RM and ref.
  \item \textbf{评分}：8 块 GPU（1 个节点）。在同一节点上运行 RM（INT8，TP=4）+ 参考模型（INT8，TP=4）。或者共享 4 块 GPU 使用 TP=4，在 RM 和参考模型之间交替。
  \item \textbf{Training}: 32 GPUs (4 nodes). FSDP across all 32. Each GPU holds $\sim$70B/32 = 2.2GB params + optimizer fraction. Plenty of headroom for activations. Gradient checkpointing for safety.
  \item \textbf{训练}：32 块 GPU（4 个节点）。FSDP 跨所有 32 块 GPU。每块 GPU 持有 $\sim$70B/32 = 2.2GB 参数 + 优化器部分。为激活值留有充足余量。使用梯度检查点确保安全。
\end{itemize}

\textbf{Expected throughput}:
\textbf{预期吞吐量}：

\begin{itemize}
  \item Generation: 6 instances $\times$ $\sim$80 responses/min = 480 responses/min
  \item 生成：6 个实例 $\times$ $\sim$80 条响应/分钟 = 480 条响应/分钟
  \item Training: Batch of 128, one step every $\sim$15s (training only, no gen wait)
  \item 训练：batch 为 128，每 $\sim$15 秒一步（仅训练，不等待生成）
  \item Overlap: While training step $N$ (15s), generation produces $\sim$120 responses for step $N+1$. Perfect pipeline.
  \item 重叠：在训练第 $N$ 步（15 秒）的同时，生成为第 $N+1$ 步产生 $\sim$120 条响应。完美的流水线。
\end{itemize}

\textbf{Bottleneck analysis}: Generation takes $\sim$45s for 128 responses. Training takes $\sim$15s. Scoring takes $\sim$5s. Generation is bottleneck. Could move 8 GPUs from training to gen (40 gen, 24 training) to balance, but then training is bottleneck. Current allocation is near-optimal.
\textbf{瓶颈分析}：生成 128 条响应耗时 $\sim$45 秒。训练耗时 $\sim$15 秒。评分耗时 $\sim$5 秒。生成是瓶颈。可以将 8 块 GPU 从训练移到生成（40 生成，24 训练）来平衡，但那样训练会成为瓶颈。当前分配接近最优。

\textbf{Alternative if memory-tight}: Move scoring onto training nodes (time-share: score during gen, train during training). Saves 8 GPUs. Slightly worse pipelining but works.
\textbf{如果内存紧张时的替代方案}：将评分移到训练节点（时间共享：生成时评分，训练时训练）。节省 8 块 GPU。流水线稍差但可行。

\emph{\textbf{Review:} Chapters~2 and~11 (Systems Foundations; System Architecture).}
\emph{\textbf{复习：}第 2 章和第 11 章（系统基础；系统架构）。}
\end{questionbox}

\section{GRPO Variants and Advanced RL Questions}
\section{GRPO 变体与高级强化学习问题}
\label{grpo-variants-and-advanced-rl-questions}

\begin{questionbox}[Q21: What is DAPO and how does it improve over standard GRPO?]
\begin{questionbox}[Q21：什么是 DAPO？它如何改进标准 GRPO？]

\textbf{Answer}: DAPO (Dynamic Adaptive Policy Optimization) introduces 5 key modifications:
\textbf{答案}：DAPO（动态自适应策略优化）引入了 5 个关键改进：

\textbf{1. Clip-Higher (asymmetric clipping)}: Standard PPO/GRPO clips both directions equally at $\epsilon=0.2$. DAPO uses $\epsilon_\text{low}=0.2$ but $\epsilon_\text{high}=0.28$. This allows the model to \emph{increase} good action probabilities more aggressively while still restricting how much it suppresses bad ones. Intuition: exploration needs more room than exploitation.
\textbf{1. 更高裁剪（非对称裁剪）}：标准 PPO/GRPO 在 $\epsilon=0.2$ 处对称地双向裁剪。DAPO 使用 $\epsilon_\text{low}=0.2$ 但 $\epsilon_\text{high}=0.28$。这使得模型能够更积极地 \emph{提高} 好动作的概率，同时仍然限制它对坏动作的抑制程度。直觉：探索比利用需要更多空间。

\textbf{2. Overlong Filtering}: If a response hits the max length limit (truncated, no EOS token), it’s masked entirely from the loss. Rationale: truncated responses contain no natural stopping signal --- training on them teaches the model that ``stopping mid-sentence'' is acceptable.
\textbf{2. 过长过滤}：如果一条响应达到最大长度限制（被截断，无 EOS 标记），则从损失中完全屏蔽它。理由：截断的响应不包含自然的停止信号——在这些响应上训练会教会模型“在句子中间停止”是可接受的。

\textbf{3. Token-level Loss}: Loss is normalized by total token count across all sequences, not by number of sequences. This prevents longer sequences from dominating the gradient.
\textbf{3. 词元级损失}：损失按所有序列的总词元数量归一化，而不是按序列数量。这防止了较长序列主导梯度。

\textbf{4. Soft Overlong Punishment}: Instead of binary truncation filtering, apply a gradual penalty as responses approach max length. $r_\text{soft} = -c \cdot \max(0, \text{len} - L_\text{soft})/(L_\text{max} - L_\text{soft})$.
\textbf{4. 软性过长惩罚}：使用渐进式惩罚，而不是二值截断过滤。当响应接近最大长度时施加惩罚。$r_\text{soft} = -c \cdot \max(0, \text{len} - L_\text{soft})/(L_\text{max} - L_\text{soft})$。

\textbf{5. Dynamic Sampling}: Resample prompts during training to ensure each batch has a mix of success/failure (not yet in TRL).
\textbf{5. 动态采样}：在训练期间重新采样提示，以确保每个批次包含成功/失败的混合（尚未在 TRL 中实现）。

\textbf{When to use}: Large-scale reasoning RL where you need maximum exploration and long completions (32K+ tokens). The asymmetric clipping is particularly valuable.
\textbf{使用时机}：大规模推理强化学习，需要最大探索和长补全（32K+ 词元）。非对称裁剪尤其有价值。

\emph{\textbf{Review:} Chapters~7 and~8 (GRPO; Preference Optimization Variants).}
\emph{\textbf{复习：}第 7 章和第 8 章（GRPO；偏好优化变体）。}
\end{questionbox}

\begin{questionbox}[Q22: Explain the vLLM train-inference mismatch. Why does it happen and how do TIS/MIS fix it?]
\begin{questionbox}[Q22：解释 vLLM 训练-推理不匹配问题。它为什么发生？TIS/MIS 如何修复它？]

\textbf{Answer}: \textbf{The problem}: When using vLLM for generation and a training framework (DeepSpeed/FSDP) for updates, the same model with the same weights produces \emph{different} token probabilities. This happens because:
\textbf{答案}：\textbf{问题}：当使用 vLLM 进行生成，使用训练框架（DeepSpeed/FSDP）进行更新时，同一个模型、相同的权重会产生 \emph{不同的} 词元概率。原因是：

\begin{itemize}
  \item Different numerical kernels (vLLM uses custom CUDA kernels optimized for throughput)
  \item 不同的数值内核（vLLM 使用针对吞吐量优化的自定义 CUDA 内核）
  \item Different attention implementations (Flash Attention in training vs PagedAttention in vLLM)
  \item 不同的注意力实现（训练中的 Flash Attention 与 vLLM 中的 PagedAttention）
  \item Different precision handling (FP8/INT8 in vLLM vs BF16 in training)
  \item 不同的精度处理（vLLM 中的 FP8/INT8 与训练中的 BF16）
  \item Batching differences affecting layer normalization numerics
  \item 批处理差异影响层归一化的数值
\end{itemize}

This silently breaks PPO’s on-policy assumption: we compute the ratio $\pi_\theta/\pi_\text{old}$ using $\pi_\text{old}$ from vLLM but $\pi_\theta$ from the training framework. The ratio is wrong from step zero!
这会静默地破坏 PPO 的在策略假设：我们使用 vLLM 的 $\pi_\text{old}$ 和训练框架的 $\pi_\theta$ 计算比率 $\pi_\theta/\pi_\text{old}$。从一开始比率就是错的！

\textbf{TIS (Truncated Importance Sampling)}: Correct the gradient by multiplying by $\min(\pi_\text{train}/\pi_\text{inference}, C)$. The $\min$ with cap $C$ prevents extreme corrections from destabilizing training. Typical $C=2.0$.
\textbf{TIS（截断重要性采样）}：通过乘以 $\min(\pi_\text{train}/\pi_\text{inference}, C)$ 来校正梯度。使用上限 $C$ 的 $\min$ 防止极端校正破坏训练稳定性。典型值 $C=2.0$。

\textbf{MIS (Masked Importance Sampling)}: More aggressive --- simply discard any token where $\pi_\text{train}/\pi_\text{inference} > C$. Zero contribution to gradient. Prevents any badly-estimated token from affecting the update.
\textbf{MIS（掩码重要性采样）}：更激进——直接丢弃任何满足 $\pi_\text{train}/\pi_\text{inference} > C$ 的词元。对梯度的贡献为零。防止任何估计较差的词元影响更新。

\textbf{Sequence vs Token level}: Sequence-level IS is theoretically correct (unbiased); token-level IS is biased but lower variance. In practice, sequence-level with truncation works best.
\textbf{序列级 vs 词元级}：序列级 IS 在理论上正确（无偏）；词元级 IS 有偏但方差更低。实践中，带截断的序列级方法效果最好。

\emph{\textbf{Review:} Chapters~7 and~11 (GRPO; System Architecture).}
\emph{\textbf{复习：}第 7 章和第 11 章（GRPO；系统架构）。}
\end{questionbox}

\begin{questionbox}[Q23: GSPO vs GRPO — what’s the fundamental difference and when does it matter?]
\begin{questionbox}[Q23：GSPO 与 GRPO 的根本区别是什么？什么时候需要关注？]

\textbf{Answer}: \textbf{GRPO}: Computes importance ratio \emph{per token}: $w_{i,t} = \pi_\theta(o_{i,t}|q, o_{i,<t}) / \pi_\text{old}(o_{i,t}|q, o_{i,<t})$, then clips each token independently.
\textbf{答案}：\textbf{GRPO}：\emph{逐词元}计算重要性比率：$w_{i,t} = \pi_\theta(o_{i,t}|q, o_{i,<t}) / \pi_\text{old}(o_{i,t}|q, o_{i,<t})$，然后独立裁剪每个词元。

\textbf{GSPO}: Computes importance ratio at the \emph{sequence level}: $s_i(\theta) = (\pi_\theta(o_i|q)/\pi_\text{old}(o_i|q))^{1/|o_i|}$ --- the geometric mean of token probabilities. Clips this single sequence-level ratio.
\textbf{GSPO}：在\emph{序列级}计算重要性比率：$s_i(\theta) = (\pi_\theta(o_i|q)/\pi_\text{old}(o_i|q))^{1/|o_i|}$ —— 词元概率的几何平均值。裁剪这个单一的序列级比率。

\textbf{Why it matters}: GRPO’s per-token clipping treats each token as independent, but in language they’re deeply correlated. A small per-token change early in the sequence compounds exponentially over many tokens. GSPO captures this by looking at the full sequence probability.
\textbf{为什么重要}：GRPO 的逐词元裁剪将每个词元视为独立，但在语言中它们高度相关。序列早期的一个微小逐词元变化会在多个词元上呈指数级累积。GSPO 通过查看完整序列概率来捕捉这一点。

\textbf{Length normalization}: The $1/|o_i|$ exponent ensures fair comparison across different-length sequences. Without it, longer sequences would always have lower probability ratios.
\textbf{长度归一化}：指数 $1/|o_i|$ 确保在不同长度的序列之间进行公平比较。没有它，较长的序列总是具有较低的概率比率。

\textbf{When to use GSPO}: When training goes off-policy (\texttt{steps\_per\_generation > 1} or \texttt{num\_iterations > 1}). If fully on-policy (ratio $\approx 1$), GRPO and GSPO are equivalent.
\textbf{何时使用 GSPO}：当训练偏离策略时（\texttt{steps\_per\_generation > 1} 或 \texttt{num\_iterations > 1}）。如果完全在策略（比率 $\approx 1$），GRPO 和 GSPO 是等价的。

\emph{\textbf{Review:} Chapters~7 and~8 (GRPO; Preference Optimization Variants).}
\emph{\textbf{复习：}第 7 章和第 8 章（GRPO；偏好优化变体）。}
\end{questionbox}

\begin{questionbox}[Q24: The paper ``It Takes Two'' shows G=2 matches G=16. How is that possible?]
\begin{questionbox}[Q24：论文《It Takes Two》表明 G=2 能达到与 G=16 相当的效果。这是如何实现的？]

\textbf{Answer}: The key insight is that GRPO’s effectiveness doesn’t come from accurate advantage estimation (which would need large $G$), but from an \textbf{implicit contrastive objective}.
\textbf{答案}：关键洞察在于，GRPO 的有效性并非源于精确的优势估计（这需要较大的 $G$），而是来自一个**隐式的对比目标**。

With $G=2$ and binary rewards (one correct, one wrong): $\hat{A}_\text{correct} = +1$, $\hat{A}_\text{wrong} = -1$ (after normalization). The loss becomes: increase probability of correct response, decrease probability of wrong response. This is essentially a DPO-style contrastive loss!
当 $G=2$ 且奖励为二元值（一个正确，一个错误）时（归一化后）：$\hat{A}_\text{correct} = +1$，$\hat{A}_\text{wrong} = -1$。损失函数变为：增加正确响应的概率，降低错误响应的概率。这本质上是一种 DPO 风格的对比损失！

\textbf{Why large $G$ doesn’t help much}: The normalized advantage $\hat{A}_i = (r_i - \mu)/\sigma$ already creates a contrast between good and bad. More samples give a better $\mu$ estimate, but the gradient direction is dominated by the \emph{contrast} between best and worst, not the mean accuracy.
\textbf{为什么较大的 $G$ 作用不大}：归一化优势 $\hat{A}_i = (r_i - \mu)/\sigma$ 已经在好坏之间建立了对比。更多样本可以提供更好的 $\mu$ 估计，但梯度方向主要受最优与最劣之间的**对比**支配，而非平均准确率。

\textbf{Compute savings}: $G=2$ means 8$\times$ less generation compute than $G=16$. Since generation is 60\% of training time, this translates to $\sim$4$\times$ faster training.
\textbf{计算成本节省}：$G=2$ 意味着生成计算量是 $G=16$ 的 1/8。由于生成占训练时间的 60%，这相当于训练速度提升约 4 倍。

\textbf{Caveat}: Works best when pass rate is 30--70\%. If pass rate is very low ($<$10\%), $G=2$ often gives two failures (no signal). Need larger $G$ for hard problems.
\textbf{注意事项}：在通过率为 30%–70% 时效果最佳。如果通过率非常低（<10%），$G=2$ 通常会得到两个失败样本（无信号）。对于困难问题需要更大的 $G$。

\emph{\textbf{Review:} Chapter~7 (GRPO).}
\emph{\textbf{回顾：}第 7 章（GRPO）。}
\end{questionbox}

\begin{questionbox}[Q25: What is SAPO and how does its soft gating differ from hard clipping?]
\begin{questionbox}[Q25：什么是 SAPO？其软门控与硬裁剪有何不同？]

\textbf{Answer}: Standard PPO/GRPO uses hard clipping: $\text{clip}(r, 1-\epsilon, 1+\epsilon)$. At the boundary, the gradient suddenly drops to zero. This creates a ``dead zone'' where the model receives no learning signal.
\textbf{答案}：标准 PPO/GRPO 使用硬裁剪：$\text{clip}(r, 1-\epsilon, 1+\epsilon)$。在边界处，梯度突然降为零。这会产生一个“死区”，模型在此处接收不到学习信号。

\textbf{SAPO} replaces this with a smooth sigmoid gate: the gradient is gradually attenuated as the ratio moves away from 1, never suddenly zeroed out. It uses asymmetric temperatures:
\textbf{SAPO} 将其替换为平滑的 sigmoid 门控：当比率偏离 1 时，梯度逐渐衰减，绝不会突然归零。它使用非对称温度：

\begin{itemize}
  \item $\tau_+ = 1.0$ for positive advantages (standard attenuation)
  \item $\tau_- = 1.05$ for negative advantages (slightly more aggressive attenuation for suppression)
\end{itemize}
\begin{itemize}
  \item $\tau_+ = 1.0$ 用于正优势（标准衰减）
  \item $\tau_- = 1.05$ 用于负优势（稍强的衰减用于抑制）
\end{itemize}

\textbf{Benefits}: (1) No ``cliff'' in gradient landscape. (2) Tokens slightly outside the clip range still contribute (attenuated, not zeroed). (3) More stable optimization trajectory. (4) Sequence-coherent --- considers the full sequence context.
\textbf{优势}：(1) 梯度景观中无“悬崖”。(2) 略超出裁剪范围的 token 仍会贡献（衰减而非归零）。(3) 优化轨迹更稳定。(4) 序列连贯——考虑完整的序列上下文。

\textbf{Trade-off}: Slightly less restrictive trust region than hard clipping, so requires careful temperature tuning. But more robust to hyperparameter choices overall.
\textbf{权衡}：信任区域比硬裁剪略宽松，因此需要仔细调节温度。但整体上对超参数选择更鲁棒。

\emph{\textbf{Review:} Chapters~7 and~8 (GRPO; Preference Optimization Variants).}
\emph{\textbf{回顾：}第 7 章和第 8 章（GRPO；偏好优化变体）。}
\end{questionbox}

\section{DPO Extensions Questions}
\section{DPO 扩展问题}
\label{dpo-extensions-questions}

\begin{questionbox}[Q26: Compare f-DPO divergence choices. When would you use forward KL vs JS vs reverse KL?]
\begin{questionbox}[Q26：比较 f-DPO 散度选择。何时使用前向 KL、JS 还是反向 KL？]

\textbf{Answer}: Standard DPO uses reverse KL implicitly ($D_\text{KL}[\pi_\theta \| \pi_\text{ref}]$):
\textbf{答案}：标准 DPO 隐式使用反向 KL（$D_\text{KL}[\pi_\theta \| \pi_\text{ref}]$）：

\begin{itemize}
  \item \textbf{Reverse KL} (default): Mode-seeking. The policy concentrates probability where the reference is high. Avoids generating text the reference wouldn’t. Good for safety (conservative).
  \item \textbf{Forward KL}: Mass-covering. The policy tries to cover all modes of the reference, even low-probability ones. Good for diversity but can generate low-quality outputs.
  \item \textbf{Jensen-Shannon}: Symmetric compromise between forward and reverse. Balanced mode-coverage and mode-seeking. Often best for general alignment.
  \item \textbf{Alpha-divergence} ($\alpha=0.5$): Interpolates between forward ($\alpha=0$) and reverse ($\alpha=1$). Tunable.
\end{itemize}
\begin{itemize}
  \item \textbf{反向 KL}（默认）：模式寻求。策略将概率集中在参考分布高的区域。避免生成参考分布不会生成的文本。有利于安全性（保守）。
  \item \textbf{前向 KL}：质量覆盖。策略试图覆盖参考分布的所有模式，即使是低概率模式。有利于多样性，但可能产生低质量输出。
  \item \textbf{Jensen-Shannon}：前向与反向之间的对称折衷。平衡了模式覆盖和模式寻求。通常最适合通用对齐。
  \item \textbf{Alpha 散度}（$\alpha=0.5$）：在前向（$\alpha=0$）和反向（$\alpha=1$）之间插值。可调节。
\end{itemize}

\textbf{Practical recommendation}: Start with reverse KL (standard DPO). If the model is too conservative (won’t try creative solutions), switch to JS divergence. If diversity is critical (creative writing, brainstorming), try forward KL.
\textbf{实用建议}：从反向 KL（标准 DPO）开始。如果模型过于保守（不愿尝试创造性解决方案），则切换到 JS 散度。如果多样性至关重要（创意写作、头脑风暴），则尝试前向 KL。

\emph{\textbf{Review:} Chapters~6 and~8 (DPO; Preference Optimization Variants).}
\emph{\textbf{回顾：}第 6 章和第 8 章（DPO；偏好优化变体）。}
\end{questionbox}

\begin{questionbox}[Q27: Your DPO preference data has 15\% label noise. What do you do?]
\begin{questionbox}[Q27：你的 DPO 偏好数据存在 15% 的标签噪声，该怎么办？]

\textbf{Answer}: Three options in order of sophistication:
\textbf{答案}：按复杂程度排序的三种选项：

\textbf{1. Robust DPO} (best for known noise rate): Analytically debiases the loss: $\mathcal{L}_\text{robust} = \frac{(1-\varepsilon)\mathcal{L}_\text{DPO}(y_w, y_l) - \varepsilon \mathcal{L}_\text{DPO}(y_l, y_w)}{1 - 2\varepsilon}$. Set $\varepsilon = 0.15$. This provably recovers the clean DPO objective in expectation. TRL: \texttt{loss\_type="robust", label\_smoothing=0.15}.
\textbf{1. 鲁棒 DPO}（最适合已知噪声率）：解析地去偏损失：$\mathcal{L}_\text{robust} = \frac{(1-\varepsilon)\mathcal{L}_\text{DPO}(y_w, y_l) - \varepsilon \mathcal{L}_\text{DPO}(y_l, y_w)}{1 - 2\varepsilon}$。设 $\varepsilon = 0.15$。这可以证明在期望上恢复干净的 DPO 目标。TRL：\texttt{loss\_type="robust", label\_smoothing=0.15}。

\textbf{2. IPO} (best when noise rate unknown): Squared loss with target margin. Mislabeled pairs have bounded influence (the squared loss doesn’t diverge). More robust to arbitrary noise patterns without needing to know $\varepsilon$. TRL: \texttt{loss\_type="ipo"}.
\textbf{2. IPO}（噪声率未知时最佳）：带目标间隔的平方损失。错误标注的配对具有有界影响（平方损失不会发散）。无需知道 $\varepsilon$ 即可对任意噪声模式更鲁棒。TRL：\texttt{loss\_type="ipo"}。

\textbf{3. TR-DPO} (best for distribution shift): Updates the reference model via EMA during training. Even if early data is noisy, the evolving reference helps the model self-correct. TRL: \texttt{sync\_ref\_model=True, ref\_model\_mixup\_alpha=0.6}.
\textbf{3. TR-DPO}（最适合分布偏移）：在训练期间通过 EMA 更新参考模型。即使早期数据有噪声，不断演化的参考也有助于模型自我纠正。TRL：\texttt{sync\_ref\_model=True, ref\_model\_mixup\_alpha=0.6}。

\textbf{Data-side fixes}: (1) Filter pairs with $<$70\% inter-annotator agreement. (2) Use RM to score pairs; discard those where RM disagrees with label. (3) Active learning: re-label the most uncertain pairs.
\textbf{数据端修复}：(1) 过滤标注者间一致性低于 70% 的配对。(2) 使用奖励模型对配对评分；丢弃奖励模型与标签不一致的配对。(3) 主动学习：对最不确定的配对重新标注。

\emph{\textbf{Review:} Chapters~6 and~8 (DPO; Preference Optimization Variants).}
\emph{\textbf{回顾：}第 6 章和第 8 章（DPO；偏好优化变体）。}
\end{questionbox}

\begin{questionbox}[Q28: What is SimPO and why is being reference-free advantageous?]
\begin{questionbox}[Q28：什么是 SimPO？为什么无参考模型具有优势？]

\textbf{Answer}: SimPO uses the average log-probability of a response as an implicit reward signal: $r(x,y) = \frac{1}{|y|}\sum_t \log \pi_\theta(y_t|x, y_{<t})$ --- no reference model needed.
\textbf{答案}：SimPO 使用响应的平均对数概率作为隐式奖励信号：$r(x,y) = \frac{1}{|y|}\sum_t \log \pi_\theta(y_t|x, y_{<t})$——无需参考模型。

The loss adds a target margin $\gamma$: the chosen response should have average log-prob at least $\gamma$ higher than rejected.
损失函数增加了一个目标间隔 $\gamma$：选定响应的平均对数概率应至少比拒绝响应高 $\gamma$。

\textbf{Why reference-free matters}:
\textbf{为什么无参考模型很重要}：

\begin{enumerate}
  \item \textbf{Memory}: No reference model = 70--140GB saved for 70B models. Can train larger models on same hardware.
  \item \textbf{Simplicity}: No need to manage/load/serve a second model copy.
  \item \textbf{No stale reference}: DPO’s reference becomes increasingly irrelevant as training progresses. SimPO doesn’t have this problem.
  \item \textbf{Length normalization built in}: The $1/|y|$ naturally prevents length bias (DPO needs explicit handling).
\end{enumerate}
\begin{enumerate}
  \item \textbf{内存}：无参考模型意味着对于 70B 模型可节省 70–140GB。可以在相同硬件上训练更大的模型。
  \item \textbf{简单性}：无需管理/加载/服务第二个模型副本。
  \item \textbf{无过时参考}：DPO 的参考模型随着训练推进逐渐变得无关。SimPO 没有这个问题。
  \item \textbf{内置长度归一化}：$1/|y|$ 自然防止长度偏差（DPO 需要显式处理）。
\end{enumerate}

\textbf{Trade-off}: Without a reference anchor, the model has more freedom to collapse or drift. The $\gamma$ margin and length normalization partially mitigate this, but SimPO can be less stable than DPO for aggressive training.
\textbf{权衡}：没有参考锚点，模型更容易坍缩或漂移。$\gamma$ 间隔和长度归一化部分缓解了这一问题，但 SimPO 在激进训练时可能不如 DPO 稳定。

\emph{\textbf{Review:} Chapter~8 (Preference Optimization Variants).}
\emph{\textbf{回顾：}第 8 章（偏好优化变体）。}
\end{questionbox}

\begin{questionbox}[Q29: Explain Iterative RPO. Why combine DPO with NLL loss for reasoning?]
\begin{questionbox}[Q29：解释迭代 RPO。为什么在推理任务中将 DPO 与 NLL 损失结合？]

\textbf{Answer}: Standard DPO for reasoning has a subtle failure mode: it learns to \emph{discriminate} (assign higher implicit reward to correct traces) but doesn’t necessarily learn to \emph{generate} them.
\textbf{答案}：标准 DPO 在推理中存在一个微妙的失败模式：它学会了**区分**（给正确轨迹分配更高的隐式奖励），但不一定能学会**生成**它们。

\textbf{Why}: DPO’s gradient pushes chosen probability up and rejected probability down. But the chosen response might be so different from what the model would generate that increasing its probability doesn’t teach the model how to produce similar reasoning patterns.
\textbf{原因}：DPO 的梯度将选定概率推高，拒绝概率压低。但选定响应可能与模型原本会生成的响应差异很大，以至于增加其概率并不能教会模型如何产生类似的推理模式。

\textbf{RPO’s fix}: Add a negative log-likelihood (NLL/SFT) loss on the chosen response: $\mathcal{L} = \mathcal{L}_\text{DPO} + \alpha \cdot \mathcal{L}_\text{NLL}(y_w)$.
\textbf{RPO 的修复}：在选定响应上添加负对数似然（NLL/SFT）损失：$\mathcal{L} = \mathcal{L}_\text{DPO} + \alpha \cdot \mathcal{L}_\text{NLL}(y_w)$。

The NLL term explicitly trains the model to generate the winning response step by step. The DPO term ensures it also learns to avoid the losing response. Combined: the model learns both ``how to reason correctly'' (NLL) and ``what to avoid'' (DPO).
NLL 项显式地训练模型逐步生成获胜响应。DPO 项确保模型也学会避免失败响应。两者结合：模型同时学会“如何正确推理”（NLL）和“避免什么”（DPO）。

\textbf{Iterative}: Generate responses $\rightarrow$ check correctness $\rightarrow$ create pairs $\rightarrow$ train with RPO $\rightarrow$ repeat. Each iteration the model gets better at generating correct reasoning, creating higher-quality training data for the next round.
\textbf{迭代}：生成响应 $\rightarrow$ 检查正确性 $\rightarrow$ 创建配对 $\rightarrow$ 使用 RPO 训练 $\rightarrow$ 重复。每一轮迭代，模型生成正确推理的能力都会提升，从而为下一轮创建更高质量的训练数据。

TRL: \texttt{loss\_type=["sigmoid", "sft"], loss\_weights=[1.0, 1.0]}
TRL: \texttt{loss\_type=["sigmoid", "sft"], loss\_weights=[1.0, 1.0]}

\emph{\textbf{Review:} Chapters~8 and~13 (Preference Optimization Variants; RL for Large Reasoning Models).}
\emph{\textbf{回顾：}第 8 章和第 13 章（偏好优化变体；大型推理模型的强化学习）。}
\end{questionbox}

## GPU Architecture and Hardware Questions
## GPU 架构与硬件问题

\begin{questionbox}[Q30: Explain the GPU memory hierarchy. Why does it matter for LLM inference?]
\textbf{Answer}: From fastest to slowest:
\textbf{答案}：从最快到最慢：

\begin{enumerate}
  \item \textbf{Registers}: Per-thread, $\sim$256 KB/SM. Instant access (0 cycles latency).
  \item \textbf{寄存器}：每线程，$\sim$256 KB/SM。即时访问（0周期延迟）。
  \item \textbf{SRAM (Shared Memory)}: Per-SM, $\sim$192--228 KB/SM (A100: 164 KB configurable). Bandwidth: $\sim$19 TB/s aggregate. Latency: $\sim$20 cycles.
  \item \textbf{SRAM（共享内存）}：每SM，$\sim$192--228 KB/SM（A100：164 KB可配置）。带宽：$\sim$19 TB/s聚合。延迟：$\sim$20周期。
  \item \textbf{L2 Cache}: Shared across GPU, 40--60 MB (H100: 50 MB). Bandwidth: $\sim$5 TB/s. Latency: $\sim$200 cycles.
  \item \textbf{L2缓存}：GPU共享，40--60 MB（H100：50 MB）。带宽：$\sim$5 TB/s。延迟：$\sim$200周期。
  \item \textbf{HBM}: Main GPU memory, 80 GB (A100). Bandwidth: 2--3.35 TB/s. Latency: $\sim$400 cycles.
  \item \textbf{HBM}：GPU主内存，80 GB（A100）。带宽：2--3.35 TB/s。延迟：$\sim$400周期。
  \item \textbf{CPU DRAM}: Via PCIe, 512 GB+. Bandwidth: 32--64 GB/s. Latency: $\sim$10K cycles.
  \item \textbf{CPU DRAM}：通过PCIe，512 GB+。带宽：32--64 GB/s。延迟：$\sim$10K周期。
\end{enumerate}

\textbf{Why it matters for LLMs}: Autoregressive generation reads the full model weights ($\sim$140 GB for 70B) for every single token. At 2 TB/s HBM bandwidth, that’s 70ms just to stream the weights. The actual computation (one matrix-vector multiply) takes only 0.5ms. The GPU is 99\% waiting for data.
\textbf{为何对LLM至关重要}：自回归生成中，每个token都需要读取完整的模型权重（70B模型约$\sim$140 GB）。以2 TB/s的HBM带宽计算，仅传输权重就需要70ms。实际计算（一次矩阵-向量乘法）仅需0.5ms。GPU有99\%的时间在等待数据。

\textbf{Flash Attention exploits this}: By keeping intermediate results (QK scores, softmax) in SRAM (19 TB/s) instead of writing them to HBM (2 TB/s), it eliminates 90\% of the memory traffic for attention. The compute is the same, but HBM reads/writes drop 10$\times$.
\textbf{Flash Attention利用了这一点}：通过将中间结果（QK分数、softmax）保留在SRAM（19 TB/s）中，而非写入HBM（2 TB/s），它消除了注意力计算中90\%的内存流量。计算量相同，但HBM读写降低了10倍。

\emph{\textbf{Review:} Chapter~2 (Systems Foundations for LLMs).}
\emph{\textbf{复习：} 第2章（LLM系统基础）。}
\end{questionbox}

\begin{questionbox}[Q31: How does Flash Attention work? What is the online softmax trick?]
\textbf{Answer}: \textbf{Problem}: Standard attention materializes the $n \times n$ attention matrix in HBM. For $n=8192$: $8192^2 \times 2 = 134$ MB per head, 4.3 GB per layer with 32 heads. Must write to HBM then read back for softmax and multiply --- 3 full HBM round-trips.
\textbf{答案}：\textbf{问题}：标准注意力机制会在HBM中实例化$n \times n$的注意力矩阵。对于$n=8192$：每头$8192^2 \times 2 = 134$ MB，32头则每层4.3 GB。必须写入HBM，再读回进行softmax和乘法——共3次完整的HBM往返。

\textbf{Flash Attention solution}: Never store the full $n \times n$ matrix. Process in tiles that fit in SRAM.
\textbf{Flash Attention解决方案}：绝不存储完整的$n \times n$矩阵。将处理过程分解为适合SRAM的图块。

\textbf{Algorithm}:
\textbf{算法}：

\begin{enumerate}
  \item Split $Q$ into blocks of size $B_r$ rows, $K/V$ into blocks of $B_c$ rows.
  \item 将$Q$拆分为大小为$B_r$行的块，$K/V$拆分为大小为$B_c$行的块。
  \item For each $Q$ block: iterate over all $K$ blocks, computing partial attention scores.
  \item 对于每个$Q$块：遍历所有$K$块，计算部分注意力分数。
  \item \textbf{Online softmax trick}: Maintain running max $m$ and running sum $\ell$ for softmax normalization. When processing a new $K$ block, update: $m_\text{new} = \max(m_\text{old}, \max(\text{scores}))$, rescale previous accumulator by $e^{m_\text{old} - m_\text{new}}$, add new contribution.
  \item \textbf{在线softmax技巧}：维护动态最大值$m$和动态和$\ell$用于softmax归一化。处理新的$K$块时，更新：$m_\text{new} = \max(m_\text{old}, \max(\text{分数}))$，用$e^{m_\text{old} - m_\text{new}}$重新缩放之前的累加器，添加新的贡献。
  \item Output is accumulated incrementally --- never needs the full $n \times n$ matrix.
  \item 输出逐步累积——永远不需要完整的$n \times n$矩阵。
\end{enumerate}

\textbf{Key insight}: Softmax is normally a global operation ($\max$ and $\sum$ over all elements). The online trick decomposes it into local updates with a correction factor. Mathematically exact --- no approximation.
\textbf{关键洞察}：softmax通常是全局操作（对所有元素进行$\max$和$\sum$）。在线技巧将其分解为带有修正因子的局部更新。数学上精确——无近似。

\textbf{Result}: Memory $O(n)$ instead of $O(n^2)$. Speed 2--4$\times$ faster (fewer HBM accesses, more time in SRAM).
\textbf{结果}：内存从$O(n^2)$降至$O(n)$。速度提升2--4倍（HBM访问减少，更多时间在SRAM中）。

\textbf{Flash Attention 2}: Better work partitioning across warps, reduces non-matmul FLOPs by 2$\times$.
\textbf{Flash Attention 2}：更好的跨warp工作划分，非矩阵乘FLOPs减少2倍。

\textbf{Flash Attention 3} (H100/Hopper): Uses Tensor Memory Accelerator (TMA) for async loads, warp specialization (producer/consumer warps), FP8 support.
\textbf{Flash Attention 3}（H100/Hopper）：使用张量内存加速器（TMA）进行异步加载，warp专业化（生产者/消费者warp），支持FP8。

\emph{\textbf{Review:} Chapters~1 and~2 (LLM Architecture; Systems Foundations).}
\emph{\textbf{复习：} 第1章和第2章（LLM架构；系统基础）。}
\end{questionbox}

\begin{questionbox}[Q32: Explain PagedAttention. How does it solve the KV cache problem?]
\textbf{Answer}: \textbf{The problem}: During generation, each sequence needs a KV cache (stores K and V tensors for all previous tokens). For a 70B model: each token needs $2 \times n_\text{layers} \times d_\text{model} \times 2$ bytes = $2 \times 80 \times 8192 \times 2 \approx 2.5$ MB per token. A 2048-token sequence: $\sim$5 GB of KV cache.
\textbf{答案}：\textbf{问题}：在生成过程中，每个序列都需要一个KV缓存（存储所有先前token的K和V张量）。对于70B模型：每个token需要$2 \times n_\text{layers} \times d_\text{model} \times 2$字节 = $2 \times 80 \times 8192 \times 2 \approx 2.5$ MB。一个2048 token的序列：约$\sim$5 GB的KV缓存。

\textbf{Traditional allocation}: Pre-allocate max\_sequence\_length for each active sequence. If max=2048 but average=500, you waste 75\% of allocated memory. With 50 concurrent sequences, that’s hundreds of GB wasted.
\textbf{传统分配方式}：为每个活跃序列预分配max\_sequence\_length。如果最大值为2048但平均为500，则浪费分配内存的75\%。50个并发序列会浪费数百GB。

\textbf{PagedAttention}: Inspired by OS virtual memory:
\textbf{PagedAttention}：受操作系统虚拟内存启发：

\begin{enumerate}
  \item KV cache is split into fixed-size \emph{blocks} (pages), each holding KV for 16 tokens.
  \item KV缓存被分割为固定大小的\emph{块}（页面），每个块保存16个token的KV。
  \item A \emph{block table} (like a page table) maps logical token positions to physical memory blocks.
  \item 一个\emph{块表}（类似于页表）将逻辑token位置映射到物理内存块。
  \item Blocks are allocated on demand as the sequence grows. No pre-allocation waste.
  \item 当序列增长时按需分配块。无预分配浪费。
  \item Freed blocks return to a pool immediately when sequences finish.
  \item 序列完成后，释放的块立即返回池中。
\end{enumerate}

\textbf{Extra benefits}:
\textbf{额外优势}：

\begin{itemize}
  \item \textbf{Prefix sharing}: Multiple sequences with the same system prompt share KV cache blocks (copy-on-write). Saves 30--50\% memory for chat applications.
  \item \textbf{前缀共享}：多个具有相同系统提示的序列共享KV缓存块（写时复制）。为聊天应用节省30--50\%内存。
  \item \textbf{Preemption}: Can ``swap out'' a low-priority sequence’s blocks to CPU, freeing GPU memory for higher-priority requests.
  \item \textbf{抢占}：可以将低优先级序列的块“换出”到CPU，释放GPU内存用于更高优先级的请求。
  \item \textbf{Near-zero fragmentation}: Internal fragmentation limited to last block ($<$16 tokens). External fragmentation eliminated (any free block can be used anywhere).
  \item \textbf{近乎零碎片}：内部碎片仅限于最后一个块（$<$16 token）。消除了外部碎片（任何空闲块可用于任何位置）。
\end{itemize}

\textbf{Result}: 3--5$\times$ more concurrent sequences in the same memory $\rightarrow$ 3--5$\times$ better throughput for serving.
\textbf{结果}：相同内存中并发序列数增加3--5倍 $\rightarrow$ 服务吞吐量提升3--5倍。

\emph{\textbf{Review:} Chapter~2 (Systems Foundations for LLMs).}
\emph{\textbf{复习：} 第2章（LLM系统基础）。}
\end{questionbox}

\begin{questionbox}[Q33: Compare NVLink vs InfiniBand. When do you use each in RLHF training?]
\textbf{Answer}:
\textbf{答案}：

\textbf{NVLink} (intra-node, GPU-to-GPU):
\textbf{NVLink}（节点内，GPU到GPU）：

\begin{itemize}
  \item Bandwidth: 600 GB/s (A100), 900 GB/s (H100) --- total bidirectional
  \item 带宽：600 GB/s（A100），900 GB/s（H100）——总双向
  \item Latency: $\sim$1 $\mu$s
  \item 延迟：$\sim$1 $\mu$s
  \item Scope: Within one physical node (8 GPUs connected via NVSwitch)
  \item 范围：在一个物理节点内（8个GPU通过NVSwitch连接）
  \item Use case: \textbf{Tensor Parallelism} (TP=8). Each layer’s matrix multiply is split across GPUs, requiring AllReduce after every layer. Needs ultra-high bandwidth + low latency.
  \item 使用场景：\textbf{张量并行}（TP=8）。每层的矩阵乘法在GPU间拆分，每层后需要AllReduce。需要超高带宽+低延迟。
\end{itemize}

\textbf{InfiniBand NDR} (inter-node, node-to-node):
\textbf{InfiniBand NDR}（节点间，节点到节点）：

\begin{itemize}
  \item Bandwidth: 400 Gb/s = 50 GB/s per port. With 8 ports (GPUDirect RDMA): 400 GB/s aggregate per node.
  \item 带宽：400 Gb/s = 50 GB/s每端口。8端口（GPUDirect RDMA）：每节点聚合400 GB/s。
  \item Latency: $\sim$1--5 $\mu$s (RDMA)
  \item 延迟：$\sim$1--5 $\mu$s（RDMA）
  \item Scope: Between nodes in a cluster. Requires switches (fat-tree topology).
  \item 范围：集群中节点之间。需要交换机（胖树拓扑）。
  \item Use case: \textbf{Data Parallelism / FSDP} gradient synchronization. AllReduce of gradients happens once per training step (not per layer), so latency tolerance is higher.
  \item 使用场景：\textbf{数据并行 / FSDP}梯度同步。梯度AllReduce每训练步发生一次（而非每层），因此延迟容忍度更高。
\end{itemize}

\textbf{In RLHF specifically}:
\textbf{在RLHF中的具体应用}：

\begin{itemize}
  \item \emph{Generation}: TP=8 over NVLink within node. Multiple vLLM instances across nodes don’t communicate (embarrassingly parallel).
  \item \emph{生成}：节点内TP=8通过NVLink。跨节点的多个vLLM实例不通信（易并行）。
  \item \emph{Training}: TP=8 over NVLink intra-node + FSDP over InfiniBand inter-node. Gradients synced after full backward pass.
  \item \emph{训练}：节点内NVLink上的TP=8 + 节点间InfiniBand上的FSDP。完整反向传播后同步梯度。
  \item \emph{Weight sync}: Training $\to$ Generation uses InfiniBand (140 GB transfer, async, takes $\sim$3s at 50 GB/s).
  \item \emph{权重同步}：训练 $\to$ 生成使用InfiniBand（140 GB传输，异步，50 GB/s下约需$\sim$3秒）。
\end{itemize}

\emph{\textbf{Review:} Chapters~2 and~11 (Systems Foundations; System Architecture).}
\emph{\textbf{复习：} 第2章和第11章（系统基础；系统架构）。}
\end{questionbox}

\section{Optimization and Training Questions}
\section{优化与训练问题}

\begin{questionbox}[Q34: Explain Adam vs AdamW. Why does the difference matter for LLMs?]
\textbf{Answer}: \textbf{Adam with L2 regularization}: $\theta_{t+1} = \theta_t - \alpha \cdot (\hat{m}_t / (\sqrt{\hat{v}_t} + \epsilon) + \lambda\theta_t)$. The weight decay term $\lambda\theta_t$ is \emph{inside} the adaptive scaling. Parameters with large gradients (large $v_t$) get \emph{less} weight decay (divided by $\sqrt{v_t}$). This is not true weight decay --- it’s scale-dependent.
\textbf{答案}：\textbf{带L2正则化的Adam}：$\theta_{t+1} = \theta_t - \alpha \cdot (\hat{m}_t / (\sqrt{\hat{v}_t} + \epsilon) + \lambda\theta_t)$。权重衰减项$\lambda\theta_t$位于自适应缩放\emph{内部}。梯度大（$v_t$大）的参数获得\emph{更少}的权重衰减（除以$\sqrt{v_t}$）。这不是真正的权重衰减——它依赖于尺度。

\textbf{AdamW (decoupled weight decay)}: $\theta_{t+1} = (1 - \alpha\lambda)\theta_t - \alpha \cdot \hat{m}_t / (\sqrt{\hat{v}_t} + \epsilon)$. Weight decay is applied \emph{outside} and \emph{before} the adaptive update. Every parameter gets the same proportional decay regardless of gradient history.
\textbf{AdamW（解耦权重衰减）}：$\theta_{t+1} = (1 - \alpha\lambda)\theta_t - \alpha \cdot \hat{m}_t / (\sqrt{\hat{v}_t} + \epsilon)$。权重衰减在自适应更新\emph{之前}且\emph{之外}应用。每个参数获得相同的比例衰减，与梯度历史无关。

\textbf{Why it matters for LLMs}:
\textbf{为何对LLM至关重要}：

（原文此处中断，但按照规则继续翻译后续内容。由于输入到此为止，后续内容未提供。请确认是否需要继续？）

```markdown
\begin{enumerate}
  \item LLMs have parameters spanning many orders of magnitude (embedding layers vs attention vs FFN). Adam’s coupled L2 effectively penalizes small-gradient params more than large-gradient ones --- wrong behavior.
  \item 大语言模型（LLM）的参数跨越多个数量级（嵌入层 vs 注意力层 vs 前馈网络）。Adam 的耦合 L2 实际上对小梯度参数的惩罚大于大梯度参数——这是错误的行为。
  \item Decoupled WD provides uniform regularization across all layers, preventing some layers from growing unbounded while others over-shrink.
  \item 解耦的权重衰减（Decoupled WD）在所有层上提供统一的正则化，防止某些层无界增长而其他层过度收缩。
  \item Empirically: AdamW gives 2--5\% better perplexity on long pretraining runs compared to Adam+L2 with the same effective regularization.
  \item 经验上：在相同的有效正则化下，AdamW 在长预训练运行中相比 Adam+L2 可获得 2--5\% 的困惑度改善。
\end{enumerate}

\textbf{For RL specifically}: Often use $\lambda = 0$ (no weight decay). The KL penalty provides regularization. But for SFT: $\lambda = 0.01$--$0.1$ with AdamW is standard.

\textbf{特别针对强化学习（RL）}：通常使用 $\lambda = 0$（无权重衰减）。KL 惩罚提供正则化。但对于监督微调（SFT）：标准做法是使用 AdamW 并设置 $\lambda = 0.01$--$0.1$。

\emph{\textbf{Review:} Chapter~1 (LLM Architecture and Optimization Methods).}
\emph{\textbf{复习：} 第~1 章（大语言模型架构与优化方法）。}
\end{questionbox}


\begin{questionbox}[Q35: Why is learning rate warmup necessary? What happens without it?]
\textbf{Answer}: \textbf{The problem}: Adam’s second moment estimate $v_t = \beta_2 v_{t-1} + (1-\beta_2)g_t^2$ starts at $v_0 = 0$. The bias correction $\hat{v}_t = v_t/(1-\beta_2^t)$ compensates mathematically, but in practice:

\textbf{问题}：Adam 的二阶矩估计 $v_t = \beta_2 v_{t-1} + (1-\beta_2)g_t^2$ 从 $v_0 = 0$ 开始。偏差校正 $\hat{v}_t = v_t/(1-\beta_2^t)$ 在数学上进行了补偿，但在实践中：

\begin{itemize}
  \item First few steps: $v_t$ is based on 1--5 gradient samples. Highly inaccurate estimate of true variance.
  \item 前几步：$v_t$ 基于 1--5 个梯度样本。对真实方差的估计非常不准确。
  \item If a parameter happens to get a small gradient initially, $v_t$ is tiny $\rightarrow$ effective LR is huge $\rightarrow$ catastrophic update.
  \item 如果某个参数初始时恰好得到小梯度，$v_t$ 会非常小 $\rightarrow$ 有效学习率巨大 $\rightarrow$ 灾难性更新。
  \item The bias correction amplifies early updates: at step 1, $\hat{v}_1 = v_1/(1-0.999) = 1000 \cdot v_1$.
  \item 偏差校正放大了早期更新：在第 1 步，$\hat{v}_1 = v_1/(1-0.999) = 1000 \cdot v_1$。
\end{itemize}

\textbf{Without warmup}: First 10--100 steps often have gradient spikes that permanently damage the model. Early representations get scrambled before the optimizer stabilizes.

\textbf{无预热（warmup）}：前 10--100 步常出现梯度尖峰，对模型造成永久性损伤。在优化器稳定之前，早期表示会被打乱。

\textbf{Warmup fix}: Start with LR $\approx 0$ and linearly increase to target over $W$ steps (typically 3--10\% of training). By the time LR reaches full value, $v_t$ has accumulated enough samples to be accurate.

\textbf{预热修复}：从 LR $\approx 0$ 开始，在 $W$ 步（通常为训练的 3--10\%）内线性增加到目标值。当 LR 达到完整值时，$v_t$ 已积累足够样本从而变得准确。

\textbf{Typical settings}:

\textbf{典型设置}：

\begin{itemize}
  \item Pretraining: 2000 steps warmup ($\sim$1\% of 200K steps)
  \item 预训练：2000 步预热（约为 200K 步的 1%）
  \item SFT: 100 steps warmup ($\sim$5\% of 2000 steps)
  \item 监督微调（SFT）：100 步预热（约为 2000 步的 5%）
  \item RL (PPO/GRPO): 20--50 steps warmup (short, model already stable from SFT)
  \item 强化学习（PPO/GRPO）：20--50 步预热（较短，模型已从 SFT 稳定）
\end{itemize}

\emph{\textbf{Review:} Chapters~1 and~10 (LLM Architecture; SFT Best Practices).}
\emph{\textbf{复习：} 第~1 章和第~10 章（大语言模型架构；SFT 最佳实践）。}
\end{questionbox}


\begin{questionbox}[Q36: Compare learning rate schedules. Which would you choose for RL fine-tuning?]
\textbf{Answer}:

\textbf{Cosine decay}: $\eta_t = \eta_\text{min} + \frac{1}{2}(\eta_\text{max} - \eta_\text{min})(1 + \cos(\pi t/T))$. Standard for pretraining and SFT. Smooth decay, most time at moderate LR.

\textbf{余弦衰减（Cosine decay）}：$\eta_t = \eta_\text{min} + \frac{1}{2}(\eta_\text{max} - \eta_\text{min})(1 + \cos(\pi t/T))$。预训练和 SFT 的标准做法。平滑衰减，大部分时间处于中等 LR。

\textbf{Linear decay}: $\eta_t = \eta_\text{max}(1 - t/T)$. Simpler, similar results to cosine for short runs.

\textbf{线性衰减（Linear decay）}：$\eta_t = \eta_\text{max}(1 - t/T)$。更简单，短时间运行时结果与余弦相似。

\textbf{WSD (Warmup-Stable-Decay)}: Warmup $\rightarrow$ constant LR for 80\% $\rightarrow$ rapid decay in last 20\%. New standard for pretraining. The ``stable'' phase gives consistent learning; the final decay squeezes out remaining gains.

\textbf{WSD（预热-稳定-衰减）}：预热 $\rightarrow$ 80% 时间恒定 LR $\rightarrow$ 最后 20% 快速衰减。预训练的新标准。“稳定”阶段提供一致的学习；最终衰减榨取剩余收益。

\textbf{Constant}: No decay. $\eta_t = \eta_\text{max}$ after warmup.

\textbf{常数（Constant）}：无衰减。预热后 $\eta_t = \eta_\text{max}$。

\textbf{For RL fine-tuning (PPO/GRPO), I’d choose: Constant with short warmup}. Reasons:

\textbf{对于强化学习微调（PPO/GRPO），我会选择：短预热 + 常数学习率}。原因：

\begin{enumerate}
  \item RL training length is highly unpredictable (you stop based on win-rate, not epochs).
  \item 强化学习训练长度高度不可预测（根据胜率而非轮次停止）。
  \item Cosine/linear decay assumes you know the total steps in advance.
  \item 余弦/线性衰减假设你提前知道总步数。
  \item The LR is already very low ($10^{-6}$), further decay makes updates invisible.
  \item 学习率已经很低（$10^{-6}$），进一步衰减会使更新不可见。
  \item PPO’s adaptive KL controller already modulates the effective step size.
  \item PPO 的自适应 KL 控制器已经调节了有效步长。
  \item If you must decay: use linear decay over a generous budget, stop early when metrics plateau.
  \item 如果必须衰减：在宽松的预算内使用线性衰减，当指标平台时提前停止。
\end{enumerate}

\emph{\textbf{Review:} Chapters~1 and~5 (LLM Architecture; PPO).}
\emph{\textbf{复习：} 第~1 章和第~5 章（大语言模型架构；PPO）。}
\end{questionbox}


\begin{questionbox}[Q37: Why is gradient clipping critical for RL training but less important for SFT?]
\textbf{Answer}: \textbf{SFT}: Supervised loss is smooth and well-behaved. Gradient norms are consistent across batches (typically 0.1--1.0). Clipping at 1.0 rarely activates --- it’s a safety net.

\textbf{答案}：\textbf{监督微调（SFT）}：监督损失平滑且行为良好。梯度范数在不同批次间一致（通常为 0.1--1.0）。在 1.0 处裁剪很少激活——它是一个安全网。

\textbf{RL (PPO/GRPO)}: Gradient norms are highly variable because:

\textbf{强化学习（PPO/GRPO）}：梯度范数高度可变，因为：

\begin{enumerate}
  \item \textbf{Reward variance}: One batch might have all high-reward responses, next might have all low. The advantage $\hat{A}$ swings wildly.
  \item \textbf{奖励方差}：一个批次可能全是高奖励响应，下一个批次可能全是低奖励。优势 $\hat{A}$ 剧烈波动。
  \item \textbf{Ratio explosion}: If a rare token’s probability changed a lot, $r_t = \pi_\text{new}/\pi_\text{old}$ can be very large $\rightarrow$ large gradient before clipping kicks in.
  \item \textbf{比率爆炸}：如果稀有 token 的概率变化很大，$r_t = \pi_\text{new}/\pi_\text{old}$ 可能非常大 $\rightarrow$ 在裁剪生效前产生大梯度。
  \item \textbf{Sparse reward}: In GRPO with binary rewards, some prompts give all-correct (advantage $\approx 0$) then suddenly a hard prompt gives extreme advantages.
  \item \textbf{稀疏奖励}：在具有二元奖励的 GRPO 中，某些提示给出全部正确（优势 $\approx 0$），然后突然一个困难提示给出极端优势。
  \item \textbf{KL term}: The KL penalty gradient can spike when policy diverges.
  \item \textbf{KL 项}：当策略发散时，KL 惩罚梯度可能尖峰。
\end{enumerate}

\textbf{Without clipping}: A single bad batch can produce a gradient 100$\times$ normal magnitude $\rightarrow$ destroys the model in one step. Recovery is impossible (catastrophic forgetting of all pretraining).

\textbf{无裁剪}：单个不良批次可能产生正常量级 100 倍的梯度 $\rightarrow$ 一步摧毁模型。恢复不可能（灾难性遗忘所有预训练内容）。

\textbf{Typical setting}: \texttt{max\_grad\_norm=1.0}. Some use 0.5 for extra safety in early RL training. The norm is computed globally across all parameters (not per-layer).

\textbf{典型设置}：\texttt{max\_grad\_norm=1.0}。有些在早期 RL 训练中使用 0.5 以增强安全性。范数是跨所有参数全局计算的（非逐层）。

\textbf{Monitoring}: If clipping activates more than 20\% of steps, your LR is probably too high or your batch size too small.

\textbf{监控}：如果裁剪在超过 20% 的步骤中被激活，你的学习率可能过高或批量大小过小。

\emph{\textbf{Review:} Chapters~5 and~7 (PPO; GRPO).}
\emph{\textbf{复习：} 第~5 章和第~7 章（PPO；GRPO）。}
\end{questionbox}


\begin{questionbox}[Q38: BF16 vs FP16 for training. When does the choice matter?]
\textbf{Answer}:

\textbf{FP16}: 1 sign + 5 exponent + 10 mantissa bits. Range: $\pm 65504$. Precision: $\sim$3.3 decimal digits.

\textbf{FP16}：1 位符号 + 5 位指数 + 10 位尾数。范围：$\pm 65504$。精度：约 3.3 位十进制数字。

\textbf{BF16}: 1 sign + 8 exponent + 7 mantissa bits. Range: $\pm 3.4 \times 10^{38}$ (same as FP32!). Precision: $\sim$2.4 decimal digits.

\textbf{BF16}：1 位符号 + 8 位指数 + 7 位尾数。范围：$\pm 3.4 \times 10^{38}$（与 FP32 相同！）。精度：约 2.4 位十进制数字。

\textbf{Why BF16 wins for LLMs}:

\textbf{为什么 BF16 对 LLM 更优}：

\begin{enumerate}
  \item \textbf{No loss scaling needed}: FP16’s small range ($\pm$65K) means gradients and activations frequently overflow/underflow. Requires dynamic loss scaling (multiply loss by 1024, divide gradients back). BF16 has FP32’s range --- overflow is essentially impossible.
  \item \textbf{无需损失缩放}：FP16 的小范围（$\pm$65K）意味着梯度和激活频繁上溢/下溢。需要动态损失缩放（将损失乘以 1024，再除以梯度）。BF16 具有 FP32 的范围——上溢基本不可能。
  \item \textbf{Simpler code}: No loss scaler, no inf/nan checking, no dynamic scaling adjustment.
  \item \textbf{代码更简单}：无需损失缩放器，无需检查 inf/nan，无需动态缩放调整。
  \item \textbf{Critical for RL}: RL gradients are noisier and spikier than SFT. FP16 loss scaling often fails (picks wrong scale, causes NaN). BF16 ``just works.''
  \item \textbf{对 RL 至关重要}：RL 梯度比 SFT 更嘈杂且更尖峰。FP16 损失缩放经常失败（选错缩放，导致 NaN）。BF16 “直接可用”。
\end{enumerate}

\textbf{When FP16 might be better}: If you need maximum precision (some scientific computing tasks) and can manage the loss scaling. FP16 has 3 more mantissa bits = slightly more accurate results.

\textbf{何时 FP16 可能更好}：如果你需要最大精度（某些科学计算任务）并能管理损失缩放。FP16 多 3 位尾数 = 结果稍精确。

\textbf{FP32 master weights}: Even with BF16 forward/backward, accumulate gradient updates in FP32 to prevent rounding errors from compounding over thousands of small steps. Standard practice for all LLM training.

\textbf{FP32 主权重}：即使使用 BF16 前向/反向传播，也要在 FP32 中累积梯度更新，以防止舍入误差在数千个小步骤中累积。所有 LLM 训练的标准做法。

\emph{\textbf{Review:} Chapter~2 (Systems Foundations for LLMs).}
\emph{\textbf{复习：} 第~2 章（大语言模型的系统基础）。}
\end{questionbox}


\section{Reward Model and SFT Questions}
\section{奖励模型与 SFT 问题}
\label{reward-model-and-sft-questions}


\begin{questionbox}[Q39: Derive the Bradley-Terry reward model loss. What are its limitations?]
\textbf{Answer}: \textbf{Bradley-Terry model}: Given two responses, the probability the better one ($y_w$) is preferred: $P(y_w \succ y_l | x) = \sigma(r(x, y_w) - r(x, y_l))$ where $\sigma$ is the sigmoid.

\textbf{答案}：\textbf{Bradley-Terry 模型}：给定两个响应，更优响应（$y_w$）被偏好的概率为：$P(y_w \succ y_l | x) = \sigma(r(x, y_w) - r(x, y_l))$，其中 $\sigma$ 是 sigmoid 函数。

\textbf{MLE derivation}: Given $N$ preference pairs, maximize likelihood: $\prod_i P(y_w^i \succ y_l^i)$. Take negative log: $\mathcal{L} = -\sum_i \log\sigma(r(x_i, y_w^i) - r(x_i, y_l^i))$.

\textbf{MLE 推导}：给定 $N$ 个偏好对，最大化似然：$\prod_i P(y_w^i \succ y_l^i)$。取负对数：$\mathcal{L} = -\sum_i \log\sigma(r(x_i, y_w^i) - r(x_i, y_l^i))$.

\textbf{Limitations}:

\textbf{局限性}：

\begin{enumerate}
  \item \textbf{No ties}: BT can’t model ``equally good'' --- forces a strict preference.
  \item \textbf{无平局}：BT 无法建模“同样好”——强制严格偏好。
  \item \textbf{Transitivity}: Assumes if A$>$B and B$>$C then A$>$C. Humans aren’t transitive.
  \item \textbf{传递性}：假设如果 A$>$B 且 B$>$C，则 A$>$C。人类并非可传递的。
  \item \textbf{Context-free}: Same reward regardless of what alternatives were available.
  \item \textbf{无上下文}：无论可用替代品是什么，奖励相同。
  \item \textbf{Scalar collapse}: Compresses all quality dimensions into one number. A response can be safe but unhelpful --- RM must trade off.
  \item \textbf{标量坍缩}：将所有质量维度压缩成一个数字。一个响应可能安全但无帮助——奖励模型（RM）必须权衡。
  \item \textbf{Length bias}: Longer responses get higher scores (more information = more likely to contain what annotator wanted). Must explicitly decorrelate.
  \item \textbf{长度偏差}：较长的响应获得更高分数（更多信息 = 更可能包含注释者想要的内容）。必须显式去相关。
\end{enumerate}
```

## Foundations Questions
## 基础问题

\textbf{Mitigations}: Margin loss (require minimum gap $\delta$), reward centering (subtract running mean), length penalty during training, multi-head RM (separate scores for helpfulness/safety/accuracy).
\textbf{缓解措施}：边际损失（要求最小间隔 $\delta$）、奖励中心化（减去运行均值）、训练中的长度惩罚、多头奖励模型（分别为有用性/安全性/准确性打分）。

\emph{\textbf{Review:} Chapter~9 (Reward Model Training).}
\emph{\textbf{回顾：} 第9章（奖励模型训练）。》
\end{questionbox}
\end{questionbox}

\begin{questionbox}[Q40: What is sequence packing in SFT and why does it matter?]
\begin{questionbox}[Q40: 什么是SFT中的序列打包（sequence packing）？它为什么重要？]
\textbf{Answer}: \textbf{Problem}: Training examples have variable length. Standard batching pads all examples to max\_length. If max=4096 but average=500, you waste 88\% of compute on padding tokens (which contribute zero gradient).
\textbf{答案}：\textbf{问题}：训练样本长度不一。标准批处理将所有样本填充到 max\_length。如果 max=4096 而平均长度为 500，那么 88% 的计算量都浪费在了填充标记上（这些标记的梯度为零）。

\textbf{Packing solution}: Concatenate multiple short examples into a single max\_length sequence. Separate with EOS tokens. Train on all examples simultaneously.
\textbf{打包解决方案}：将多个短样本拼接成一个 max\_length 序列。用 EOS 标记分隔。同时训练所有样本。

Example: Instead of 4 sequences padded to 4096 (16K tokens, 14K padding), pack into 1 sequence of 4096 with 4 examples end-to-end (4096 real tokens, 0 padding). \textbf{4$\times$ more efficient.}
示例：原本 4 个序列填充到 4096（共 16K 标记，14K 填充），现在打包成 1 个 4096 序列，包含 4 个完整样本（4096 个真实标记，0 填充）。\textbf{效率提升 4 倍。}

\textbf{Critical detail --- block-diagonal attention mask}: Without special handling, example 2 attends to example 1’s tokens (cross-contamination). Must use a block-diagonal attention mask that restricts each example to only attend to its own tokens.
\textbf{关键细节——分块对角注意力掩码}：如果没有特殊处理，样本2会关注样本1的标记（交叉污染）。必须使用分块对角注意力掩码，限制每个样本只关注自身标记。

\textbf{In TRL}: \texttt{SFTConfig(packing=True, max\_seq\_length=4096)}. Handles mask automatically.
\textbf{在 TRL 中}：\texttt{SFTConfig(packing=True, max\_seq\_length=4096)}。自动处理掩码。

\textbf{Caveats}: (1) Longer examples still need their own batch entries (can’t split mid-sequence). (2) Slight implementation complexity for position embeddings (reset per example). (3) Some argue packing changes the effective batch size (more examples per step) --- adjust LR accordingly.
\textbf{注意事项}：(1) 较长样本仍需独立批次项（不能在序列中间拆分）。(2) 位置嵌入实现稍复杂（每个样本需重置）。(3) 有人认为打包改变了有效批大小（每步样本更多）——需相应调整学习率。

\emph{\textbf{Review:} Chapter~10 (SFT Best Practices and Techniques).}
\emph{\textbf{回顾：} 第10章（SFT最佳实践与技术）。》
\end{questionbox}
\end{questionbox}

\begin{questionbox}[Q41: Explain completion-only masking for SFT. What happens if you don’t use it?]
\begin{questionbox}[Q41: 解释SFT的仅完成掩码（completion-only masking）。如果不使用它会发生什么？]
\textbf{Answer}: In chat-format SFT data: \texttt{[system] + [user message] + [assistant response]}. Standard NLL loss computes loss on all tokens including the system prompt and user message.
\textbf{答案}：在聊天格式的SFT数据中：\texttt{[系统提示] + [用户消息] + [助手回复]}。标准的负对数似然损失会计算所有标记的损失，包括系统提示和用户消息。

\textbf{Problem without masking}: The model wastes capacity learning to predict the user’s message (which it will never need to generate at inference). Worse: if the training data has diverse user messages, the model gets confused about ``whose turn is it?''
\textbf{不使用掩码的问题}：模型浪费容量去学习预测用户的消息（推理时永远不需要生成）。更糟的是：如果训练数据包含多样化的用户消息，模型会对“该谁发言了”感到困惑。

\textbf{Completion-only masking}: Set loss weight to 0 for all tokens in the prompt (system + user). Only compute loss on assistant response tokens.
\textbf{仅完成掩码}：将提示（系统+用户）中所有标记的损失权重设为0。仅计算助手回复标记的损失。

TRL: \texttt{DataCollatorForCompletionOnlyLM(response\_template="<|assistant|>")}
TRL: \texttt{DataCollatorForCompletionOnlyLM(response\_template="<|assistant|>")}

\textbf{Impact}: Typically 5--15\% better on instruction-following benchmarks. Faster convergence (gradient signal is concentrated on useful tokens). No change to compute cost.
\textbf{影响}：在指令遵循基准上通常提升 5–15%。收敛更快（梯度信号集中在有用标记上）。计算成本不变。

\textbf{Subtlety}: Must include the response template token in the loss (teaches the model to start responding). But exclude everything before it.
\textbf{微妙之处}：必须将回复模板标记包含在损失中（教会模型开始回复）。但排除它之前的所有内容。

\emph{\textbf{Review:} Chapter~10 (SFT Best Practices and Techniques).}
\emph{\textbf{回顾：} 第10章（SFT最佳实践与技术）。》
\end{questionbox}
\end{questionbox}

\begin{questionbox}[Q42: How does SFT quality affect the RL ceiling? What is the pass@k diagnostic?]
\begin{questionbox}[Q42: SFT质量如何影响RL的上限？什么是 pass@k 诊断？]
\textbf{Answer}: \textbf{Ceiling theorem (informal)}: RL can only reinforce behaviors the model can already produce with non-negligible probability. If the SFT model has 0\% chance of generating a correct solution, RL will never find it.
\textbf{答案}：\textbf{上限定理（非正式）}：RL只能强化模型已经能够以不可忽略概率产生的行为。如果SFT模型生成正确解的概率为0%，RL将永远无法找到它。

\textbf{Why}: GRPO/PPO sample from the current policy and reinforce good samples. If good samples don’t exist in the distribution, there’s nothing to reinforce. RL is exploration-limited by the base policy’s support.
\textbf{原因}：GRPO/PPO 从当前策略采样并强化好样本。如果分布中不存在好样本，就没有东西可强化。RL的探索受限于基础策略的支持范围。

\textbf{pass@k diagnostic}: Generate $k$ responses per prompt, check if \emph{any} is correct:
\textbf{pass@k 诊断}：为每个提示生成 $k$ 个回复，检查是否\emph{任一}正确：

\begin{itemize}
  \item pass@1: Model’s typical performance (greedy/low temp).
  \item pass@1: 模型的典型性能（贪心/低温度）。
  \item pass@8: Upper bound of what GRPO with $G=8$ can achieve.
  \item pass@8: GRPO 在 $G=8$ 时能达到的上限。
  \item pass@64: Upper bound for aggressive Best-of-N.
  \item pass@64: 激进 Best-of-N 的上限。
  \item pass@256: Approximate ceiling for RL improvement.
  \item pass@256: RL改进的近似上限。
\end{itemize}

\textbf{Interpretation}:
\textbf{解读}：

\begin{itemize}
  \item pass@1=20\%, pass@64=80\%: Great! 4$\times$ headroom for RL. Strong gains expected.
  \item pass@1=20\%, pass@64=80\%: 很好！RL有4倍提升空间。预期收益显著。
  \item pass@1=20\%, pass@64=25\%: Almost no headroom. RL won’t help much. Need better SFT first.
  \item pass@1=20\%, pass@64=25\%: 几乎没有提升空间。RL帮助不大。需要先改进SFT。
  \item pass@1=5\%, pass@64=60\%: Model \emph{can} solve it but rarely does. Perfect case for RL (reinforce the rare successes).
  \item pass@1=5\%, pass@64=60\%: 模型\emph{能够}解决但很少做到。RL的完美场景（强化罕见成功）。
\end{itemize}

\textbf{Rule}: If pass@64 $<$ 1.5$\times$ pass@1, invest in better SFT data before starting RL.
\textbf{规则}：如果 pass@64 $<$ 1.5$\times$ pass@1，在开始RL之前先投资更好的SFT数据。

\emph{\textbf{Review:} Chapters~7 and~10 (GRPO; SFT Best Practices).}
\emph{\textbf{回顾：} 第7章和第10章（GRPO；SFT最佳实践）。》
\end{questionbox}
\end{questionbox}

\begin{questionbox}[Q43: Design a multi-objective reward system for a chat model. How do you balance helpfulness vs safety?]
\begin{questionbox}[Q43: 为聊天模型设计一个多目标奖励系统。如何平衡有用性与安全性？]
\textbf{Answer}: \textbf{Architecture}: Separate reward models for each objective:
\textbf{答案}：\textbf{架构}：为每个目标使用独立的奖励模型：

\begin{itemize}
  \item $r_\text{helpful}$: Trained on helpfulness preferences (quality, accuracy, completeness)
  \item $r_\text{helpful}$：在有用性偏好上训练（质量、准确性、完整性）
  \item $r_\text{safe}$: Trained on safety preferences (refusals, harmlessness, no hallucination)
  \item $r_\text{safe}$：在安全性偏好上训练（拒绝回答、无害性、无幻觉）
  \item $r_\text{format}$: Rule-based (follows instructions, proper formatting, appropriate length)
  \item $r_\text{format}$：基于规则（遵循指令、格式正确、长度适当）
\end{itemize}

\textbf{Combination strategies}:
\textbf{组合策略}：

\begin{enumerate}
  \item \textbf{Weighted sum} (simplest): $r = w_1 r_\text{helpful} + w_2 r_\text{safe} + w_3 r_\text{format}$. Problem: safety can be outweighed by helpfulness.
  \item \textbf{加权和}（最简单）：$r = w_1 r_\text{helpful} + w_2 r_\text{safe} + w_3 r_\text{format}$。问题：安全性可能被有用性压倒。
  \item \textbf{Constrained} (safer): Maximize $r_\text{helpful}$ subject to $r_\text{safe} > \tau$. Implemented via: $r = r_\text{helpful} - \lambda \cdot \max(0, \tau - r_\text{safe})$ with large $\lambda$.
  \item \textbf{约束法}（更安全）：在 $r_\text{safe} > \tau$ 约束下最大化 $r_\text{helpful}$。通过 $r = r_\text{helpful} - \lambda \cdot \max(0, \tau - r_\text{safe})$ 实现，其中 $\lambda$ 很大。
  \item \textbf{GDPO normalization} (best for GRPO): Normalize each reward independently within group, then combine: $\hat{A} = w_1 \hat{A}_\text{helpful} + w_2 \hat{A}_\text{safe}$. Prevents one reward from dominating due to scale differences.
  \item \textbf{GDPO归一化}（最适合GRPO）：在组内独立归一化每个奖励，然后组合：$\hat{A} = w_1 \hat{A}_\text{helpful} + w_2 \hat{A}_\text{safe}$。防止某个奖励因尺度差异而主导。
  \item \textbf{Lexicographic}: Safety is hard constraint (must pass), then optimize helpfulness. Train in stages: safety alignment first, then helpfulness.
  \item \textbf{字典序法}：安全性是硬约束（必须通过），然后优化有用性。分阶段训练：先安全对齐，再有用性。
\end{enumerate}

\textbf{Practical weights}: Start with $w_\text{safe}=2.0, w_\text{helpful}=1.0, w_\text{format}=0.5$. Safety gets 2$\times$ weight because its failure mode (harmful content) is much worse than helpfulness failure (mediocre answer).
\textbf{实际权重}：从 $w_\text{safe}=2.0, w_\text{helpful}=1.0, w_\text{format}=0.5$ 开始。安全性权重设为2倍，因为其失败模式（有害内容）比有用性失败（平庸回答）严重得多。

\emph{\textbf{Review:} Chapters~9 and~12 (Reward Model Training; LLM Agentic Training).}
\emph{\textbf{回顾：} 第9章和第12章（奖励模型训练；LLM智能体训练）。》
\end{questionbox}
\end{questionbox}

\section{System Architecture Extension Questions}
\section{系统架构扩展问题}
\label{system-architecture-extension-questions}
\label{system-architecture-extension-questions}

\begin{questionbox}[Q44: How does speculative decoding work? When does it help for RLHF?]
\begin{questionbox}[Q44: 推测解码（speculative decoding）如何工作？它对RLHF有什么帮助？]
\textbf{Answer}: \textbf{Problem}: Large model generates one token per forward pass ($\sim$70ms for 70B). Slow.
\textbf{答案}：\textbf{问题}：大模型每次前向传播仅生成一个标记（70B模型约70ms）。速度慢。

\textbf{Speculative decoding}:
\textbf{推测解码}：

\begin{enumerate}
  \item \textbf{Draft}: Small model (1--7B) generates $k$ candidate tokens quickly ($\sim$5ms for all $k$).
  \item \textbf{草稿}：小模型（1–7B）快速生成 $k$ 个候选标记（全部 $k$ 个约5ms）。
  \item \textbf{Verify}: Large model does one forward pass scoring all $k$ tokens in parallel. Accepts tokens where $p_\text{large}(t_i) \geq p_\text{draft}(t_i)$ (always). Probabilistically accepts others.
  \item \textbf{验证}：大模型进行一次前向传播，并行评分所有 $k$ 个标记。接受满足 $p_\text{large}(t_i) \geq p_\text{draft}(t_i)$ 的标记（始终接受）。以概率方式接受其他标记。
  \item \textbf{Result}: On average, 3--4 tokens accepted per verification step. Speedup: 2--3$\times$.
  \item \textbf{结果}：平均每次验证步骤接受 3–4 个标记。加速比：2–3 倍。
\end{enumerate}

\textbf{Key property}: The output distribution is \emph{identical} to sampling from the large model alone. No quality loss. The draft model only affects speed, not output.
\textbf{关键性质}：输出分布与单独从大模型采样\emph{完全相同}。无质量损失。草稿模型仅影响速度，不影响输出。

\textbf{For RLHF specifically}: Generation is 60\% of compute. 2--3$\times$ speedup on generation = 1.5--2$\times$ end-to-end speedup. Combined with vLLM + INT8: generation goes from the bottleneck to parity with training.
\textbf{专门针对RLHF}：生成占计算量的60%。生成速度提升2–3倍 = 端到端加速1.5–2倍。结合 vLLM + INT8：生成从瓶颈变为与训练相当。

\textbf{Limitations}: (1) Draft model must share tokenizer. (2) Less effective at high temperature (draft model less accurate). (3) Needs additional GPU memory for draft model. (4) Diminishing returns beyond $k=5$ (acceptance rate drops).
\textbf{局限性}：(1) 草稿模型必须共享分词器。(2) 高温下效果较差（草稿模型准确性降低）。(3) 需要额外GPU内存存放草稿模型。(4) $k>5$ 时收益递减（接受率下降）。

\emph{\textbf{Review:} Chapters~2 and~11 (Systems Foundations; System Architecture).}
\emph{\textbf{回顾：} 第2章和第11章（系统基础；系统架构）。》
\end{questionbox}
\end{questionbox}

\begin{questionbox}[Q45: Explain the roofline model. How do you determine if a kernel is compute-bound or memory-bound?]
\begin{questionbox}[Q45: 解释屋顶线模型（roofline model）。如何判断一个内核是计算密集型还是内存密集型？]
\textbf{Answer}: The roofline model plots achievable performance (FLOPS) as a function of arithmetic intensity (FLOPS per byte of memory traffic).
\textbf{答案}：屋顶线模型将可达性能（FLOPS）绘制为运算强度（每字节内存流量的FLOPS）的函数。

\textbf{Two regimes}:
\textbf{两种区域}：

## Foundations Questions
## 基础问题

\begin{itemize}
  \item \textbf{Memory-bound} (left of crossover): Performance limited by how fast you can feed data to compute units. Actual FLOPS = bandwidth $\times$ arithmetic intensity. GPU utilization $<$ 100\%.
  \item \textbf{内存受限}（位于交叉点左侧）：性能受限于向计算单元输送数据的速度。实际FLOPS = 带宽 $\times$ 算术强度。GPU利用率 $<$ 100%。
  \item \textbf{Compute-bound} (right of crossover): Performance limited by peak FLOPS. Memory is fast enough. GPU at max utilization.
  \item \textbf{计算受限}（位于交叉点右侧）：性能受限于峰值FLOPS。内存足够快。GPU处于最大利用率。
\end{itemize}

\textbf{Crossover point}: Peak FLOPS / Peak Bandwidth. For A100: 312 TF / 2 TB/s = 156 FLOP/byte.
\textbf{交叉点}：峰值FLOPS / 峰值带宽。以A100为例：312 TF / 2 TB/s = 156 FLOP/字节。

\textbf{LLM operations}:
\textbf{大语言模型运算}：

\begin{itemize}
  \item \textbf{Autoregressive generation} (batch=1): Read 140GB weights, do 140G FLOPs = 1 FLOP/byte. \emph{Extremely} memory-bound (156$\times$ below crossover). Only 0.6\% GPU utilization.
  \item \textbf{自回归生成}（批大小=1）：读取140GB权重，执行140G FLOP = 1 FLOP/字节。\emph{极度}内存受限（低于交叉点156倍）。仅0.6% GPU利用率。
  \item \textbf{Training forward pass} (batch=128, seq=2048): Arithmetic intensity $\approx 200$+ FLOP/byte. Compute-bound. Near peak utilization.
  \item \textbf{训练前向传播}（批大小=128，序列长度=2048）：算术强度 $\approx 200$+ FLOP/字节。计算受限。接近峰值利用率。
  \item \textbf{Attention} (long sequence): $O(n^2 d)$ FLOPs / $O(n^2 + nd)$ bytes. For long $n$: compute-bound. For short $n$: memory-bound. Flash Attention keeps it in SRAM regardless.
  \item \textbf{注意力机制}（长序列）：$O(n^2 d)$ FLOP / $O(n^2 + nd)$ 字节。当 $n$ 较长时：计算受限。当 $n$ 较短时：内存受限。Flash Attention 无论长短都将其保留在SRAM中。
\end{itemize}

\textbf{Practical use}: If your kernel is memory-bound, reduce memory traffic (quantization, caching, tiling). If compute-bound, reduce FLOPs (pruning, distillation, lower precision).
\textbf{实际应用}：如果你的内核是内存受限的，减少内存流量（量化、缓存、分块）。如果是计算受限的，减少FLOP（剪枝、蒸馏、低精度）。

\emph{\textbf{Review:} Chapter~2 (Systems Foundations for LLMs).}
\emph{\textbf{复习：} 第2章（大语言模型的系统基础）。}
\end{questionbox}

\begin{questionbox}[Q46: How does continuous batching work and why is it essential for RLHF generation?]
\begin{questionbox}[Q46：连续批处理如何工作？为何它对基于人类反馈的强化学习（RLHF）生成至关重要？]

\textbf{Answer}: \textbf{Static batching}: Start $B$ sequences. Wait for ALL to finish. If one sequence generates 500 tokens and another generates 50 tokens, the 50-token sequence’s GPU slot sits idle for 450 tokens.
\textbf{答案}：\textbf{静态批处理}：启动 $B$ 个序列。等待所有序列完成。如果一个序列生成500个token，另一个生成50个token，那么生成50个token的序列的GPU槽位会在450个token期间闲置。

\textbf{Continuous batching} (iteration-level scheduling): After each generation step, check which sequences are done. Immediately insert new sequences into freed slots. GPU slots are never idle.
\textbf{连续批处理}（迭代级调度）：在每个生成步骤之后，检查哪些序列已完成。立即将新序列插入已释放的槽位。GPU槽位永不闲置。

\textbf{Why essential for RLHF}:
\textbf{为何对RLHF至关重要}：

\begin{enumerate}
  \item RLHF generates diverse outputs (high temperature). Length variance is huge --- some responses are 50 tokens, others 2000+.
  \item RLHF生成多样化输出（高温度）。长度差异巨大——有些回答是50个token，另一些则是2000+。
  \item Without continuous batching: average utilization $\sim$40--50\% (waiting for slowest sequence).
  \item 没有连续批处理：平均利用率 $\sim$40--50\%（等待最慢的序列）。
  \item With continuous batching: utilization $>$90\%. Throughput 2--3$\times$ higher.
  \item 采用连续批处理：利用率 $>$90\%。吞吐量提高2--3倍。
  \item RLHF needs large batches (128+ responses per step). Generating 128 responses with static batching requires max\_tokens $\times$ 128 sequential steps. Continuous batching amortizes this.
  \item RLHF需要大批量（每步128+个回答）。使用静态批处理生成128个回答需要 max\_tokens $\times$ 128 个连续步骤。连续批处理分摊了这一开销。
\end{enumerate}

\textbf{Implementation}: vLLM’s scheduler checks after every decode step. Preemption: if a new high-priority request arrives and memory is full, can swap out a low-priority sequence’s KV cache to CPU and resume later.
\textbf{实现}：vLLM的调度器在每次解码步骤后检查。抢占：如果新的高优先级请求到达且内存已满，可以将低优先级序列的KV缓存交换到CPU，稍后恢复。

\emph{\textbf{Review:} Chapters~2 and~11 (Systems Foundations; System Architecture).}
\emph{\textbf{复习：} 第2章和第11章（系统基础；系统架构）。}
\end{questionbox}

\section{Transformer Architecture Questions}
\section{Transformer 架构问题}
\label{transformer-architecture-questions}

\begin{questionbox}[Q: Why does RoPE dominate over learned absolute positional embeddings in modern LLMs?]
\begin{questionbox}[问：为何旋转位置编码（RoPE）在现代大语言模型中优于学习的绝对位置嵌入？]

\textbf{Answer}: RoPE encodes \emph{relative} position directly into the Q/K dot product via rotation matrices. Key advantages:
\textbf{答案}：RoPE通过旋转矩阵直接将\emph{相对}位置编码到Q/K点积中。关键优势：

\begin{enumerate}
  \item Attention scores depend only on relative distance $i-j$, not absolute position --- this generalizes better to unseen sequence lengths.
  \item 注意力分数仅依赖于相对距离 $i-j$，而非绝对位置——这能更好地泛化到未见过的序列长度。
  \item Can be extended beyond training length via frequency scaling (NTK-aware, YaRN) without retraining.
  \item 可通过频率缩放（NTK-aware、YaRN）扩展到训练长度之外，无需重新训练。
  \item No additional parameters (rotations are deterministic from position index).
  \item 无额外参数（旋转由位置索引确定性决定）。
  \item Learned absolute embeddings are fixed to training length and don’t extrapolate --- a model trained at 4K context fails at 8K.
  \item 学习的绝对嵌入固定于训练长度，无法外推——在4K上下文中训练的模型在8K时失败。
\end{enumerate}

\emph{\textbf{Review:} Chapter~1 (LLM Architecture and Optimization Methods).}
\emph{\textbf{复习：} 第1章（大语言模型架构与优化方法）。}
\end{questionbox}

\begin{questionbox}[Q: Explain SwiGLU and why it replaced ReLU in modern transformers.]
\begin{questionbox}[问：解释SwiGLU，以及为何它取代了现代Transformer中的ReLU。]

\textbf{Answer}: SwiGLU: $\text{FFN}(x) = W_2 (\text{Swish}(W_1 x) \odot W_3 x)$, where $\text{Swish}(x) = x \cdot \sigma(x)$.
\textbf{答案}：SwiGLU：$\text{FFN}(x) = W_2 (\text{Swish}(W_1 x) \odot W_3 x)$，其中 $\text{Swish}(x) = x \cdot \sigma(x)$。

\textbf{Why it’s better}:
\textbf{为何更好}：

\begin{itemize}
  \item The \emph{gating} mechanism ($\odot W_3 x$) allows the network to selectively suppress or amplify dimensions --- more expressive than pointwise ReLU.
  \item \emph{门控}机制 ($\odot W_3 x$) 允许网络有选择地抑制或放大维度——比逐点ReLU更具表现力。
  \item Swish is smooth (no dead neurons like ReLU’s zero-gradient region).
  \item Swish是平滑的（没有像ReLU零梯度区域那样的死亡神经元）。
  \item Empirically: 1--2\% improvement on language modeling benchmarks at same FLOP count.
  \item 经验上：在相同FLOP计数下，语言建模基准提升1--2\%。
  \item Tradeoff: requires 3 weight matrices instead of 2 (solved by reducing hidden dim from $4d$ to $8d/3$).
  \item 权衡：需要3个权重矩阵而非2个（通过将隐藏维度从 $4d$ 减少到 $8d/3$ 解决）。
\end{itemize}

\emph{\textbf{Review:} Chapter~1 (LLM Architecture and Optimization Methods).}
\emph{\textbf{复习：} 第1章（大语言模型架构与优化方法）。}
\end{questionbox}

\begin{questionbox}[Q: What is Grouped Query Attention (GQA) and why does Llama-3 use it?]
\begin{questionbox}[问：什么是分组查询注意力（GQA）？为何Llama-3使用它？]

\textbf{Answer}: Standard MHA: $H$ query heads, $H$ key heads, $H$ value heads. GQA: $H$ query heads but only $G < H$ key/value heads (shared across query groups).
\textbf{答案}：标准多头注意力（MHA）：$H$ 个查询头，$H$ 个键头，$H$ 个值头。GQA：$H$ 个查询头，但只有 $G < H$ 个键/值头（在查询组间共享）。

Llama-3 70B: 64 query heads, 8 KV heads (each KV head shared by 8 query heads).
Llama-3 70B：64个查询头，8个KV头（每个KV头被8个查询头共享）。

\textbf{Benefits}:
\textbf{优势}：

\begin{itemize}
  \item KV cache size reduced by $H/G = 8\times$ --- critical for inference (KV cache is the dominant memory cost at long sequences).
  \item KV缓存大小减少 $H/G = 8$倍——对推理至关重要（KV缓存是长序列中的主要内存开销）。
  \item Minimal quality loss ($<$0.5\% on benchmarks) because KV patterns are highly correlated across heads.
  \item 质量损失极小（基准测试中 $<$0.5\%），因为KV模式在不同头之间高度相关。
  \item Inference throughput increases proportionally to KV cache reduction (more sequences fit in memory = higher batch size).
  \item 推理吞吐量随KV缓存减少而成比例增加（内存中容纳更多序列 = 更高批大小）。
\end{itemize}

\emph{\textbf{Review:} Chapter~1 (LLM Architecture and Optimization Methods).}
\emph{\textbf{复习：} 第1章（大语言模型架构与优化方法）。}
\end{questionbox}

\begin{questionbox}[Q: Why did decoder-only architectures win over encoder-decoder for LLMs?]
\begin{questionbox}[问：为何仅有解码器的架构在大语言模型中胜过了编码器-解码器架构？]

\textbf{Answer}:
\textbf{答案}：

\begin{enumerate}
  \item \textbf{Unified objective}: Pretraining = fine-tuning = inference all use next-token prediction. No architectural mismatch.
  \item \textbf{统一目标}：预训练 = 微调 = 推理均使用下一个token预测。无架构不匹配。
  \item \textbf{Parameter efficiency}: All parameters contribute to generation. In encoder-decoder, encoder params are ``wasted'' during pure generation tasks.
  \item \textbf{参数效率}：所有参数都贡献于生成。在编码器-解码器中，编码器参数在纯生成任务中被“浪费”。
  \item \textbf{Simpler scaling}: One model, one loss function, one set of hyperparameters to tune.
  \item \textbf{更简单的扩展}：一个模型，一个损失函数，一组超参数需要调整。
  \item \textbf{KV cache efficiency}: Decoder-only has one KV cache; encoder-decoder has two (encoder + decoder cross-attention).
  \item \textbf{KV缓存效率}：仅有解码器有一个KV缓存；编码器-解码器有两个（编码器 + 解码器交叉注意力）。
  \item \textbf{Emergent few-shot}: Decoder-only naturally supports in-context learning (prepend examples to the prompt).
  \item \textbf{涌现的少样本能力}：仅有解码器自然支持上下文学习（在提示前添加示例）。
\end{enumerate}

Encoder-decoder still wins for seq2seq tasks with fixed input length (translation), but these are a shrinking fraction of LLM use cases.
编码器-解码器在固定输入长度的序列到序列任务（翻译）中仍然占优，但这些任务在大语言模型用例中的占比正在缩小。

\emph{\textbf{Review:} Chapter~1 (LLM Architecture and Optimization Methods).}
\emph{\textbf{复习：} 第1章（大语言模型架构与优化方法）。}
\end{questionbox}

\section{Flash Attention Questions}
\section{Flash Attention 问题}
\label{flash-attention-questions}

\begin{questionbox}[Q: Flash Attention computes the same result as standard attention but is 2--4$\times$ faster. How is this possible if it does the same number of FLOPs?]
\begin{questionbox}[问：Flash Attention 计算的结果与标准注意力相同，但速度快2--4倍。如果它执行相同数量的FLOP，这怎么可能？]

\textbf{Answer}: Flash Attention is faster because it reduces \emph{HBM memory traffic}, not FLOPs. Standard attention materializes the $n \times n$ attention matrix in HBM (slow), reads it back for softmax, reads again for $PV$ multiply --- 4 HBM round-trips over $O(n^2)$ data.
\textbf{答案}：Flash Attention 更快是因为它减少了\emph{HBM内存流量}，而非FLOP。标准注意力在HBM（慢）中实例化 $n \times n$ 注意力矩阵，读回进行softmax，再次读取进行 $PV$ 乘法——对 $O(n^2)$ 数据进行了4次HBM往返。

Flash Attention tiles the computation so the $n \times n$ matrix is computed and consumed entirely in SRAM (fast, 19 TB/s) without ever writing it to HBM (2 TB/s). The ``online softmax'' trick enables this by maintaining running statistics.
Flash Attention 将计算分块，使得 $n \times n$ 矩阵完全在SRAM（快，19 TB/s）中计算和消耗，从未写入HBM（2 TB/s）。通过维护运行统计，“在线softmax”技巧实现了这一点。

Result: HBM traffic drops from $O(n^2 d)$ to $O(n^2 d / M)$ where $M$ is SRAM size. Same FLOPs, 10--50$\times$ less memory traffic $\to$ 2--4$\times$ wall-clock speedup.
结果：HBM流量从 $O(n^2 d)$ 降至 $O(n^2 d / M)$，其中 $M$ 是SRAM大小。相同FLOP，内存流量减少10--50倍 $\to$ 实际时间加速2--4倍。

\emph{\textbf{Review:} Chapters~1 and~2 (LLM Architecture; Systems Foundations).}
\emph{\textbf{复习：} 第1章和第2章（大语言模型架构；系统基础）。}
\end{questionbox}

\begin{questionbox}[Q: Why doesn’t Flash Attention help the FFN layers?]
\begin{questionbox}[问：为何Flash Attention对前馈神经网络（FFN）层没有帮助？]

\textbf{Answer}: FFN layers are \emph{compute-bound}, not memory-bound. Their arithmetic intensity ($I \approx 300$ FLOP/byte for large batch GEMMs) is already above the roofline ridge point (156 FLOP/byte on A100).
\textbf{答案}：FFN层是\emph{计算受限}的，而非内存受限。其算术强度（大批量通用矩阵乘法（GEMM）的 $I \approx 300$ FLOP/字节）已高于Roofline模型脊点（A100上为156 FLOP/字节）。

Flash Attention helps attention because attention is deeply memory-bound ($I \approx 1$--$60$ FLOP/byte). By keeping data in SRAM, it removes the memory bottleneck.
Flash Attention有助于注意力机制，因为注意力是深度内存受限的（$I \approx 1$--$60$ FLOP/字节）。通过将数据保留在SRAM中，它消除了内存瓶颈。

\emph{\textbf{Review:} Chapters~1 and~2 (LLM Architecture; Systems Foundations).}
\emph{\textbf{复习：} 第1章和第2章（大语言模型架构；系统基础）。}
\end{questionbox}

For FFN: the bottleneck is already the Tensor Cores (not memory bandwidth), so reducing memory traffic doesn't help. Instead, FFN benefits from quantization (reduces weight size $\to$ higher arithmetic intensity) and larger batch sizes.

对于FFN：瓶颈已经是张量核心（而非内存带宽），因此减少内存流量并无帮助。相反，FFN受益于量化（减小权重尺寸 $\to$ 更高算术强度）和更大的批处理大小。

\emph{\textbf{Review:} Chapters~1 and~2 (LLM Architecture; Systems Foundations).}
\emph{\textbf{复习：} 第1章和第2章（LLM架构；系统基础）。}
\end{questionbox}

\begin{questionbox}[Q: Explain the online softmax trick and why it's essential for Flash Attention.]
\textbf{Answer}: Standard softmax needs the global maximum $m = \max_j x_j$ before computing any output --- this requires seeing all $n$ attention scores first, forcing materialization of the full $n \times n$ matrix.

\begin{questionbox}[问：解释在线softmax技巧以及它为何对Flash Attention至关重要。]
\textbf{答案}：标准softmax在计算任何输出之前需要全局最大值 $m = \max_j x_j$ —— 这意味着必须先看到所有 $n$ 个注意力分数，从而迫使整个 $n \times n$ 矩阵实例化。

The online softmax trick processes blocks sequentially, maintaining a running $(m, \ell, O)$ state:

在线softmax技巧顺序处理块，维护一个运行的 $(m, \ell, O)$ 状态：

\begin{enumerate}
  \item Process new block $\to$ update running max: $m_{\text{new}} = \max(m_{\text{old}}, \max(s_{\text{new}}))$
  \item 处理新块 $\to$ 更新运行最大值：$m_{\text{new}} = \max(m_{\text{old}}, \max(s_{\text{new}}))$
  \item Rescale old sum: $\ell_{\text{new}} = e^{m_{\text{old}} - m_{\text{new}}} \cdot \ell_{\text{old}} + \text{new terms}$
  \item 重新缩放旧和：$\ell_{\text{new}} = e^{m_{\text{old}} - m_{\text{new}}} \cdot \ell_{\text{old}} + \text{新项}$
  \item Rescale output: $O_{\text{new}} = \text{rescaled}(O_{\text{old}}) + \text{new contribution}$
  \item 重新缩放输出：$O_{\text{new}} = \text{rescaled}(O_{\text{old}}) + \text{新贡献}$
\end{enumerate}

This is mathematically exact --- no approximation. It enables block-by-block processing where each block fits in SRAM, never needing the full $n \times n$ matrix in memory.

这在数学上是精确的——没有近似。它支持逐块处理，其中每个块适合SRAM，从未需要将整个 $n \times n$ 矩阵存储在内存中。

\emph{\textbf{Review:} Chapters~1 and~2 (LLM Architecture; Systems Foundations).}
\emph{\textbf{复习：} 第1章和第2章（LLM架构；系统基础）。}
\end{questionbox}

\section{LoRA and PEFT Questions}
\label{lora-and-peft-questions}

\section{LoRA与PEFT问题}
\label{lora-and-peft-questions}

\begin{questionbox}[Q: Why does LoRA work? What theoretical insight justifies low-rank updates?]
\textbf{Answer}: Aghajanyan et al.~\cite{aghajanyan2020intrinsic} showed that fine-tuning operates in a very low \emph{intrinsic dimensionality} --- the effective parameter space for a fine-tuning task is far smaller than the model's total parameter count. A 175B model may have intrinsic dimensionality $<$10,000 for a given task.

\begin{questionbox}[问：LoRA为何有效？什么理论洞察证明了低秩更新的合理性？]
\textbf{答案}：Aghajanyan等人~\cite{aghajanyan2020intrinsic}表明，微调在非常低的\emph{内在维度}上运行——微调任务的有效参数空间远小于模型的总参数量。一个175B模型对于给定任务的内在维度可能小于$10000$。

LoRA directly exploits this: by constraining updates to rank $r$ ($W' = W + BA$, $B \in \mathbb{R}^{d \times r}$), it restricts learning to an $r$-dimensional subspace per weight matrix. Since the true task subspace is low-dimensional, this loses almost nothing while reducing trainable parameters by 100--1000$\times$.

LoRA直接利用了这一点：通过将更新限制在秩 $r$（$W' = W + BA$，$B \in \mathbb{R}^{d \times r}$），它将学习限制在每个权重矩阵的 $r$ 维子空间内。由于真实任务子空间是低维的，这几乎不损失什么，同时将可训练参数减少100--1000倍。

\textbf{Intuition}: Fine-tuning doesn't change what the model ``knows'' (the full-rank $W$ stays frozen); it only adjusts \emph{how} existing knowledge is combined for the new task --- a low-rank perturbation.

\textbf{直觉}：微调不会改变模型“知道”的内容（满秩的 $W$ 保持冻结）；它仅调整现有知识如何被组合用于新任务——一种低秩扰动。

\emph{\textbf{Review:} Chapter~1 (LLM Architecture and Optimization Methods).}
\emph{\textbf{复习：} 第1章（LLM架构与优化方法）。}
\end{questionbox}

\begin{questionbox}[Q: Compare QLoRA vs. full LoRA vs. full fine-tuning for a 70B model. When would you choose each?]
\textbf{Answer}:

\begin{questionbox}[问：针对70B模型，比较QLoRA、全LoRA和全微调。何时选择哪一种？]
\textbf{答案}：

{\small
\begin{tabular}{@{}llllp{4.5cm}@{}}
\toprule
\textbf{Method} & \textbf{Memory} & \textbf{GPUs} & \textbf{Quality} & \textbf{Use When} \\
\midrule
Full fine-tune & 560+ GB & 8+ A100 & Best & Unlimited budget; pre-training continuation \\
LoRA ($r=16$) & 145 GB & 2 A100 & 95--98\% & Good budget; general fine-tuning \\
QLoRA ($r=16$) & 44 GB & 1$\times$48GB & 93--96\% & Single-GPU; prototyping; constrained resources \\
\bottomrule
\end{tabular}
}

{\small
\begin{tabular}{@{}llllp{4.5cm}@{}}
\toprule
\textbf{方法} & \textbf{内存} & \textbf{GPU数} & \textbf{质量} & \textbf{使用场景} \\
\midrule
全微调 & 560+ GB & 8+ A100 & 最佳 & 预算无限；预训练延续 \\
LoRA ($r=16$) & 145 GB & 2 A100 & 95--98\% & 预算良好；通用微调 \\
QLoRA ($r=16$) & 44 GB & 1$\times$48GB & 93--96\% & 单GPU；原型开发；资源受限 \\
\bottomrule
\end{tabular}
}

\textbf{Decision tree}: (1) If task requires deep knowledge change $\to$ full fine-tune. (2) If adapting to new style/format $\to$ LoRA. (3) If memory-constrained or rapid iteration $\to$ QLoRA. (4) If rank matters: start $r=16$; increase if training loss plateaus above full fine-tune level.

\textbf{决策树}：(1) 如果任务需要深层知识改变 $\to$ 全微调。(2) 如果适应新风格/格式 $\to$ LoRA。(3) 如果内存受限或快速迭代 $\to$ QLoRA。(4) 如果秩重要：从 $r=16$ 开始；如果训练损失在高于全微调水平时停滞，则增加秩。

\emph{\textbf{Review:} Chapters~1 and~10 (LLM Architecture; SFT Best Practices).}
\emph{\textbf{复习：} 第1章和第10章（LLM架构；SFT最佳实践）。}
\end{questionbox}

\begin{questionbox}[Q: What is DoRA and why does it outperform standard LoRA?]
\textbf{Answer}: DoRA (Weight-Decomposed Low-Rank Adaptation) decomposes $W$ into magnitude $\|W\|$ and direction $W/\|W\|$, then applies LoRA only to the direction component: 
\[
W' = m \odot \frac{W + BA}{\|W + BA\|}
\]
 where $m$ (magnitude) is also trainable but as a simple scalar per output neuron.

\begin{questionbox}[问：什么是DoRA？为什么它优于标准LoRA？]
\textbf{答案}：DoRA（权重分解低秩适配）将 $W$ 分解为幅度 $\|W\|$ 和方向 $W/\|W\|$，然后仅对方向分量应用LoRA：
\[
W' = m \odot \frac{W + BA}{\|W + BA\|}
\]
其中 $m$（幅度）也可训练，但作为每个输出神经元的简单标量。

\textbf{Why it helps}: Full fine-tuning naturally updates both magnitude and direction independently. Standard LoRA couples them (the low-rank update changes both simultaneously in a constrained way). DoRA decouples them, giving LoRA the same ``degrees of freedom'' structure as full fine-tuning. Result: 1--3\% improvement on reasoning tasks with no extra compute at inference (merge adapters).

\textbf{为何有帮助}：全微调自然独立地更新幅度和方向。标准LoRA将它们耦合（低秩更新以受限方式同时改变两者）。DoRA将它们解耦，赋予LoRA与全微调相同的“自由度”结构。结果：在推理任务上提升1-3%，且推理时无额外计算（合并适配器）。

\emph{\textbf{Review:} Chapter~1 (LLM Architecture and Optimization Methods).}
\emph{\textbf{复习：} 第1章（LLM架构与优化方法）。}
\end{questionbox}

\section{Model Compression Questions}
\label{model-compression-questions}

\section{模型压缩问题}
\label{model-compression-questions}

\begin{questionbox}[Q: Explain AWQ. Why does protecting 1\% of weights preserve 99\% of quality?]
\textbf{Answer}: AWQ (Activation-Aware Weight Quantization) observes that weight importance is highly non-uniform: weights that multiply large activations contribute disproportionately to the output.

\begin{questionbox}[问：解释AWQ。为什么保护1%的权重能保留99%的质量？]
\textbf{答案}：AWQ（激活感知权重量化）观察到权重重要性高度非均匀：与大的激活值相乘的权重对输出贡献不成比例。

The key insight: $\|W \cdot X\|$ depends on both $W$ and $X$. A small weight multiplied by a large activation matters more than a large weight multiplied by a near-zero activation.

关键洞察：$\|W \cdot X\|$ 取决于 $W$ 和 $X$ 两者。一个小权重乘以一个大激活比一个大权重乘以一个接近零的激活更重要。

AWQ identifies the top 1\% of ``salient'' channels (those with consistently large activation magnitudes across calibration data) and protects them by scaling: multiply salient channels by a factor $s > 1$ before quantization (then divide by $s$ in the activation). This reduces relative quantization error for important channels.

AWQ识别出前1%的“显著”通道（那些在校准数据中激活幅度持续较大的通道）并通过缩放保护它们：在量化前将显著通道乘以因子 $s > 1$（然后在激活中除以 $s$）。这减小了重要通道的相对量化误差。

Result: 4-bit quantization with $<$1\% quality loss on 70B models, because the 99\% of non-salient weights can tolerate aggressive quantization.

结果：在70B模型上实现4位量化，质量损失小于1%，因为99%的非显著权重可以容忍激进的量化。

\emph{\textbf{Review:} Chapters~1 and~2 (LLM Architecture; Systems Foundations).}
\emph{\textbf{复习：} 第1章和第2章（LLM架构；系统基础）。}
\end{questionbox}

\begin{questionbox}[Q: When should you use FP8 vs. 4-bit quantization vs. BF16?]
\textbf{Answer}:

\begin{questionbox}[问：何时应使用FP8、4位量化或BF16？]
\textbf{答案}：

\begin{itemize}
  \item \textbf{BF16}: Training (policy model in RLHF), when precision matters. Default for any model being updated by gradients.
  \item \textbf{BF16}：训练（RLHF中的策略模型），当精度重要时。任何通过梯度更新的模型的默认选项。
  \item \textbf{FP8 (E4M3)}: H100 training with Transformer Engine (2$\times$ throughput, $<$0.5\% quality loss). Also for inference on H100 when you need maximum throughput.
  \item \textbf{FP8 (E4M3)}：使用Transformer Engine的H100训练（2倍吞吐量，质量损失小于0.5%）。也适用于H100上需要最大吞吐量的推理。
  \item \textbf{INT8/FP8 inference}: Frozen models in RLHF (reference model, reward model) --- not being trained, so reduced precision is safe.
  \item \textbf{INT8/FP8推理}：RLHF中的冻结模型（参考模型、奖励模型）——不被训练，因此降低精度是安全的。
  \item \textbf{4-bit (AWQ/GPTQ)}: Inference serving at scale. Best memory/quality tradeoff for deployment. Also for QLoRA base model.
  \item \textbf{4位 (AWQ/GPTQ)}：大规模推理服务。部署时最佳内存/质量权衡。也适用于QLoRA基模型。
  \item \textbf{2-bit}: Experimental; edge deployment where memory is extreme constraint. Quality loss 5--10\%.
  \item \textbf{2位}：实验性；内存极度受限的边缘部署。质量损失5-10%。
\end{itemize}

\textbf{Rule}: quantize as aggressively as possible for inference, keep BF16 (or FP8 on H100) for training.

\textbf{规则}：推理时尽可能激进地量化，训练时保持BF16（或在H100上使用FP8）。

\emph{\textbf{Review:} Chapter~2 (Systems Foundations for LLMs).}
\emph{\textbf{复习：} 第2章（LLM系统基础）。}
\end{questionbox}

\begin{questionbox}[Q: Explain NVIDIA 2:4 structured sparsity. What's the speedup and constraint?]
\textbf{Answer}: 2:4 sparsity means: in every group of 4 consecutive elements, exactly 2 must be zero. This is enforced at the weight level.

\begin{questionbox}[问：解释NVIDIA 2:4结构化稀疏性。加速比和约束是什么？]
\textbf{答案}：2:4稀疏性意味着：在每4个连续元素的组中，恰好有2个必须为零。这是在权重级别强制执行的。

\textbf{Hardware support}: A100/H100 Tensor Cores have dedicated 2:4 sparse GEMM instructions that skip the zero elements, achieving exactly \textbf{2$\times$ throughput} with no software overhead.

\textbf{硬件支持}：A100/H100张量核心具有专门的2:4稀疏GEMM指令，跳过零元素，精确实现\textbf{2倍吞吐量}，无软件开销。

\textbf{Constraint}: You must achieve \emph{exactly} 50\% sparsity in this specific pattern. You can't have 30\% or 70\% sparsity; you can't have arbitrary sparsity patterns. The pruning must respect the 4-element group structure.

\textbf{约束}：必须在此特定模式下实现\emph{恰好}50%的稀疏性。不能有30%或70%的稀疏性；不能有任意稀疏模式。剪枝必须尊重4元素组结构。

\textbf{How to achieve it}: After training (or during fine-tuning), for each group of 4 weights, zero out the 2 smallest by magnitude. Then fine-tune for a few hundred steps to recover quality. Quality loss: typically $<$1\% for large models (70B+).

\textbf{如何实现}：在训练后（或在微调期间），对于每组4个权重，将幅度最小的2个置零。然后微调几百步以恢复质量。质量损失：对于大模型（70B+）通常小于1%。

\emph{\textbf{Review:} Chapter~2 (Systems Foundations for LLMs).}
\emph{\textbf{复习：} 第2章（LLM系统基础）。}
\end{questionbox}

\section{Mixture of Experts Questions}
\label{mixture-of-experts-questions}

\section{混合专家模型问题}
\label{mixture-of-experts-questions}

\begin{questionbox}[Q: Mixtral 8x7B has 47B total parameters but only 13B active per token. Explain how this works and why it's efficient.]
\textbf{Answer}: Mixtral replaces each FFN layer with 8 parallel expert FFNs (each $\sim$7B params for the FFN portion). A router network selects the Top-2 experts per token.

\begin{questionbox}[问：Mixtral 8x7B总参数量为47B，但每个token仅激活13B。解释这如何工作以及为何高效。]
\textbf{答案}：Mixtral将每个FFN层替换为8个并行的专家FFN（每个在FFN部分约有7B参数）。一个路由器网络为每个token选择Top-2专家。

\begin{questionbox}
\textbf{Why 47B total}: Attention layers are shared (not replicated) = $\sim$5B. FFN experts: 8 $\times$ $\sim$5.25B = 42B. Total: $\sim$47B.

\textbf{为什么总计47B}：注意力层（Attention layers）是共享的（非复制）≈ $\sim$5B。FFN专家（FFN experts）：8 $\times$ $\sim$5.25B = 42B。总计：$\sim$47B。

\textbf{Why 13B active}: Per token, only 2 experts fire. Active params = attention ($\sim$5B) + 2 FFN experts ($\sim$2 $\times$ 5.25B) $\approx$ 13B.

\textbf{为什么13B活跃}：每个token只有2个专家（experts）被激活。活跃参数（Active params）= 注意力层（$\sim$5B）+ 2个FFN专家（$\sim$2 $\times$ 5.25B）≈ 13B。

\textbf{Why efficient}: Compute cost scales with \emph{active} params (13B), matching a 13B dense model. But capacity (knowledge stored) scales with \emph{total} params (47B), matching much larger models. Result: Mixtral matches Llama-2 70B quality at 13B compute cost.

\textbf{为什么高效}：计算成本随\emph{活跃}参数（13B）缩放，与13B密集模型（dense model）相当。但容量（存储的知识）随\emph{总}参数（47B）缩放，与更大的模型相当。结果：Mixtral在13B计算成本下达到了Llama-2 70B的质量。

\textbf{Memory cost}: Still need all 47B params in memory (all experts loaded), so memory = 47B model, but compute = 13B model.

\textbf{内存成本}：仍需将所有47B参数加载到内存中（所有专家都被加载），因此内存消耗相当于47B模型，但计算量相当于13B模型。

\emph{\textbf{Review:} Chapter~1 (LLM Architecture and Optimization Methods).}
\emph{\textbf{回顾：}第1章（LLM架构与优化方法）。}
\end{questionbox}

\begin{questionbox}[Q: What is the load balancing problem in MoE and how is it solved?]
\label{question-load-balancing-moe}
\textbf{Answer}: Without constraints, the router tends to send most tokens to 1--2 ``popular'' experts (rich-get-richer dynamics). This causes:

\begin{itemize}
  \item Capacity waste: 6 of 8 experts are unused, model effectively shrinks to 2-expert size.
  \item 能力浪费：8个专家中有6个未被使用，模型实际上缩小到2个专家的大小。
  \item Compute imbalance: If each expert is on a different GPU, popular experts become bottlenecks while others idle.
  \item 计算不平衡：如果每个专家位于不同的GPU上，流行专家成为瓶颈，而其他专家闲置。
\end{itemize}

\textbf{Solution}: Auxiliary load-balancing loss: $\mathcal{L}_{\text{bal}} = \alpha \cdot N \sum_{i=1}^N f_i \cdot p_i$, where $f_i$ = fraction of tokens routed to expert $i$, $p_i$ = mean router probability for expert $i$. This penalizes uneven distributions.

\textbf{解决方案}：辅助负载均衡损失（Auxiliary load-balancing loss）：$\mathcal{L}_{\text{bal}} = \alpha \cdot N \sum_{i=1}^N f_i \cdot p_i$，其中$f_i$ = 路由到专家$i$的token比例，$p_i$ = 专家$i$的平均路由器概率。这会惩罚不均匀分布。

\textbf{Alternative}: Expert capacity factor --- hard cap on max tokens per expert per batch. Overflow tokens are dropped or re-routed.

\textbf{替代方案}：专家容量因子（Expert capacity factor）——每个批次每个专家的最大token数硬上限。溢出的token被丢弃或重新路由。

Typical $\alpha$: 0.01--0.1 (small enough not to hurt main loss, large enough to prevent collapse).

典型$\alpha$值：0.01--0.1（足够小以免损害主损失，足够大以防止崩溃）。

\emph{\textbf{Review:} Chapter~1 (LLM Architecture and Optimization Methods).}
\emph{\textbf{回顾：}第1章（LLM架构与优化方法）。}
\end{questionbox}

## Diversity in Training Questions
## 训练问题中的多样性
\label{diversity-in-training-questions}

\begin{questionbox}[Q: What happens if all N responses in a GRPO group are identical?]
\label{question-all-responses-identical}
\textbf{Answer}: If all $N$ responses are identical: all rewards $r_i$ are equal, so $\sigma_G = 0$ and advantages $\hat{A}_i = (r_i - \mu_G)/\sigma_G$ are undefined (division by zero). In practice, implementations set $\hat{A}_i = 0$ for all, meaning \textbf{zero learning signal} --- the step is wasted.

\textbf{答案}：如果所有$N$个回答（responses）都相同：所有奖励$r_i$相等，因此$\sigma_G = 0$且优势$\hat{A}_i = (r_i - \mu_G)/\sigma_G$未定义（除以零）。实践中，实现将所有$\hat{A}_i$设为0，意味着\textbf{零学习信号}——该步被浪费。

\textbf{Prevention}:

\begin{enumerate}
  \item \textbf{Temperature}: Use $\tau = 0.7$--$1.0$ during generation (not greedy).
  \item \textbf{温度}：在生成过程中使用$\tau = 0.7$--$1.0$（非贪婪）。
  \item \textbf{Large $N$}: $N=8$--$16$ increases probability of diverse responses.
  \item \textbf{较大的$N$}：$N=8$--$16$增加了多样化回答的概率。
  \item \textbf{Duplicate rejection}: DAPO’s approach --- reject duplicate responses and resample.
  \item \textbf{重复拒绝}：DAPO的方法——拒绝重复回答并重新采样。
  \item \textbf{Frequency penalty}: Penalize repeated n-grams during generation.
  \item \textbf{频率惩罚}：在生成过程中惩罚重复的n-gram。
  \item \textbf{Monitor}: Track unique-response ratio per group. If $<$50\%, increase temperature.
  \item \textbf{监控}：跟踪每组唯一回答比例。如果$<$50%，提高温度。
\end{enumerate}

\emph{\textbf{Review:} Chapter~7 (GRPO).}
\emph{\textbf{回顾：}第7章（GRPO）。}
\end{questionbox}

\begin{questionbox}[Q: Explain the diversity-quality tradeoff in RLHF. How do you detect mode collapse?]
\label{question-diversity-quality-tradeoff}
\textbf{Answer}: \textbf{Tradeoff}: High diversity (high entropy/temperature) = varied but potentially random/low-quality responses. Low diversity = consistent but repetitive, reward-hacked responses.

\textbf{答案}：\textbf{权衡}：高多样性（高熵/温度）意味着多样化但可能随机/低质量的回答。低多样性意味着一致但重复、奖励作弊（reward-hacked）的回答。

\textbf{Detecting mode collapse} (all should be monitored during training):

\begin{enumerate}
  \item \textbf{Response entropy}: Compute per-token entropy $H = -\sum p_i \log p_i$. If dropping rapidly $\to$ collapse.
  \item \textbf{回答熵}：计算每个token的熵$H = -\sum p_i \log p_i$。如果快速下降$\to$模式坍塌。
  \item \textbf{Unique n-gram ratio}: Fraction of unique 4-grams across responses to same prompt. Healthy: $>$0.6.
  \item \textbf{唯一n-gram比例}：对同一提示的所有回答中唯一4-gram的比例。健康值：$>$0.6。
  \item \textbf{Reward distribution width}: If $\sigma(\text{rewards})$ shrinks to near-zero $\to$ all responses are the same quality $\to$ likely identical.
  \item \textbf{奖励分布宽度}：如果$\sigma(\text{rewards})$缩小到接近零$\to$所有回答质量相同$\to$可能完全相同。
  \item \textbf{KL divergence}: If $D_\text{KL}[\pi_\theta \| \pi_\text{ref}]$ is growing rapidly, the policy is moving far from reference $\to$ often toward a narrow mode.
  \item \textbf{KL散度}：如果$D_\text{KL}[\pi_\theta \| \pi_\text{ref}]$快速增长，策略正在远离参考$\to$通常朝向狭窄模式。
  \item \textbf{Length histogram}: If all responses converge to same length $\to$ template behavior.
  \item \textbf{长度直方图}：如果所有回答收敛到相同长度$\to$模板行为。
\end{enumerate}

\textbf{Fix}: Increase KL coefficient $\beta$, increase entropy bonus, increase sampling temperature, or rollback to earlier checkpoint.

\textbf{修复}：增加KL系数$\beta$，增加熵奖励，提高采样温度，或回滚到更早的检查点。

\emph{\textbf{Review:} Chapters~7 and~9 (GRPO; Reward Model Training).}
\emph{\textbf{回顾：}第7章和第9章（GRPO；奖励模型训练）。}
\end{questionbox}

## Speculative Decoding Questions
## 投机解码问题
\label{speculative-decoding-questions}

\begin{questionbox}[Q: Speculative decoding claims ``no quality loss.'' How can generating tokens differently produce identical output distribution?]
\label{question-speculative-decoding-no-quality-loss}
\textbf{Answer}: The acceptance/rejection scheme guarantees distributional equivalence:

For each draft token $\hat{x}$ with draft probability $q(\hat{x})$ and target probability $p(\hat{x})$:

\begin{itemize}
  \item Accept with probability $\min(1, p(\hat{x})/q(\hat{x}))$
  \item 以概率$\min(1, p(\hat{x})/q(\hat{x}))$接受
  \item On rejection: sample from the \emph{residual distribution} $\propto \max(0, p(x) - q(x))$
  \item 拒绝时：从\emph{残差分布} $\propto \max(0, p(x) - q(x))$中采样
\end{itemize}

This is mathematically equivalent to sampling directly from $p$ (the target). Proof sketch: the probability of outputting token $x$ is $q(x) \cdot \min(1, p(x)/q(x)) + P(\text{reject}) \cdot \frac{\max(0, p(x)-q(x))}{\sum_y \max(0, p(y)-q(y))} = p(x)$.

这在数学上等价于直接从$p$（目标分布）中采样。证明梗概：输出token $x$的概率为$q(x) \cdot \min(1, p(x)/q(x)) + P(\text{拒绝}) \cdot \frac{\max(0, p(x)-q(x))}{\sum_y \max(0, p(y)-q(y))} = p(x)$。

The speedup comes from amortizing: when the draft is good (high acceptance), multiple tokens are confirmed in one target forward pass. The guarantee holds regardless of draft quality --- bad drafts just give lower speedup (more rejections), not worse quality.

加速来自于摊销：当草稿质量好（接受率高）时，多个token在一次目标前向传播中被确认。该保证不依赖于草稿质量——糟糕的草稿只会导致较低加速（更多拒绝），而不是更差的质量。

\emph{\textbf{Review:} Chapter~2 (Systems Foundations for LLMs).}
\emph{\textbf{回顾：}第2章（LLM系统基础）。}
\end{questionbox}

\begin{questionbox}[Q: Compare Medusa vs. Eagle for speculative decoding. When would you choose each?]
\label{question-medusa-vs-eagle}
\textbf{Answer}:

\textbf{Medusa}: Adds $k$ parallel prediction heads to the target model. Each head independently predicts token at position $t+i$. \emph{Pro}: No separate model, $<$1\% memory overhead. \emph{Con}: Heads predict independently --- cannot condition position $t+2$ on what was predicted at $t+1$. Acceptance rate: 60--80\%.

\textbf{答案}：

\textbf{Medusa}：向目标模型添加$k$个并行预测头。每个头独立预测位置$t+i$处的token。\emph{优点}：无需独立模型，内存开销小于1%。\emph{缺点}：头独立预测——无法根据$t+1$的预测结果对$t+2$进行条件化。接受率：60--80%。

\textbf{Eagle}: Lightweight autoregressive decoder on target model’s hidden states. Draft tokens are generated autoregressively (each conditioned on previous). \emph{Pro}: Captures inter-token dependencies $\to$ 85--95\% acceptance rate. \emph{Con}: Slightly more memory (small decoder) and sequential draft generation.

\textbf{Eagle}：基于目标模型隐藏状态的轻量级自回归解码器。草稿token以自回归方式生成（每个token依赖前一个）。\emph{优点}：捕捉token间依赖关系$\to$ 85--95\%接受率。\emph{缺点}：内存略高（小型解码器）且草稿生成是顺序的。

\textbf{Choose Medusa when}: Memory is extremely tight; simple integration; moderate speedup is sufficient (2--2.5$\times$).

\textbf{选择Medusa的场景}：内存极度紧张；集成简单；中等加速即可满足（2--2.5倍）。

\textbf{Choose Eagle when}: Maximum speedup needed (3--4$\times$); can afford small extra model; latency-critical single-stream generation.

\textbf{选择Eagle的场景}：需要最大加速（3--4倍）；可承受额外的小模型；延迟关键的单流生成。

\textbf{Choose N-gram when}: Repetitive outputs (code, structured data); zero cost; no training needed.

\textbf{选择N-gram的场景}：重复性输出（代码、结构化数据）；零成本；无需训练。

\emph{\textbf{Review:} Chapter~2 (Systems Foundations for LLMs).}
\emph{\textbf{回顾：}第2章（LLM系统基础）。}
\end{questionbox}

\begin{questionbox}[Q: Why does speculative decoding NOT help at high batch sizes?]
\label{question-speculative-decoding-high-batch}
\textbf{Answer}: At high batch sizes ($\geq$64), autoregressive generation is already \emph{compute-efficient}: the weight-read cost is amortized across many sequences. The arithmetic intensity approaches the roofline ridge point.

\textbf{答案}：在高批量大小（$\geq$64）时，自回归生成已经是\emph{计算高效}的：权重读取成本被分摊到多个序列上。算术强度接近屋顶线（roofline）的脊点。

Speculative decoding adds overhead:

\begin{enumerate}
  \item Draft generation cost (even if small model, it’s not free at high batch)
  \item 草稿生成成本（即使模型较小，在高批量下也不是免费的）
  \item Verification forward pass processes $k$ extra tokens per sequence (batch $\times$ $k$ tokens)
  \item 验证前向传播处理每个序列额外$k$个token（批量 $\times$ $k$ token）
  \item Memory for draft model or Medusa heads
  \item 草稿模型或Medusa头的内存
  \item Rejected tokens waste compute
  \item 被拒绝的token浪费计算
\end{enumerate}

At batch=1 (latency-bound, memory-bound): speculation turns 1 token/step into 3--4 tokens/step --- huge win.

在批量=1（延迟受限、内存受限）时：投机将每步1个token变为每步3--4个token——巨大收益。

At batch=128 (already compute-efficient): the extra tokens from speculation barely help throughput because the GPU is already near-saturated. The overhead may even \emph{reduce} throughput.

在批量=128（已计算高效）时：投机带来的额外token对吞吐量几乎没有帮助，因为GPU已接近饱和。开销甚至可能\emph{降低}吞吐量。

\textbf{Rule}: Speculative decoding is for latency (small batch); batching is for throughput (large batch). Don’t combine them.

\textbf{规则}：投机解码用于降低延迟（小批量）；批处理用于提高吞吐量（大批量）。不要组合使用。

\emph{\textbf{Review:} Chapter~2 (Systems Foundations for LLMs).}
\emph{\textbf{回顾：}第2章（LLM系统基础）。}
\end{questionbox}

## Agentic RL Questions
## 智能体强化学习问题
\label{agentic-rl-questions}

\begin{questionbox}[Q: Why does standard RLHF (single-turn PPO/DPO) fail for multi-step agents?]
\begin{questionbox}[问：为什么标准 RLHF（单轮 PPO/DPO）对多步智能体失效？]

\textbf{Answer}: Standard RLHF optimizes for single-turn quality: given a prompt, produce one good response. Multi-step agents face fundamentally different challenges:
\textbf{答案}：标准 RLHF 优化的是单轮质量：给定一个提示，生成一个良好回复。多步智能体面临着根本不同的挑战：

\begin{enumerate}
  \item \textbf{Credit assignment}: In a 50-step trajectory, which step caused the failure? Single-turn reward assigns credit to the entire response uniformly; multi-step needs \emph{per-step} credit.
  \item \textbf{信用分配}：在一条 50 步的轨迹中，哪一步导致了失败？单轮奖励将信用均匀分配给整个回复；多步则需要 \emph{每步} 信用。
  \item \textbf{Sparse rewards}: Success/failure only at trajectory end. PPO’s GAE assumes intermediate rewards; without them, advantage estimates are noisy.
  \item \textbf{稀疏奖励}：成功/失败仅出现在轨迹末尾。PPO 的 GAE（泛化优势估计）假设存在中间奖励；若缺失，优势估计会有噪声。
  \item \textbf{Action space}: Actions are structured tool calls (JSON), not just token sequences. The model must learn syntax + semantics + strategy simultaneously.
  \item \textbf{动作空间}：动作是结构化的工具调用（JSON），而不仅仅是 token 序列。模型必须同时学习语法、语义和策略。
  \item \textbf{Non-stationarity}: The environment changes with each action (tool outputs modify state). Each step has a different ``prompt'' unlike single-turn where input is fixed.
  \item \textbf{非平稳性}：环境随每个动作而改变（工具输出修改状态）。每一步都有不同的“提示”，与输入固定的单轮不同。
  \item \textbf{Exploration}: Agent must discover novel tool-use strategies, not just rephrase text.
  \item \textbf{探索}：智能体必须发现新的工具使用策略，而不仅仅是改写文本。
\end{enumerate}

\textbf{Solution}: Trajectory-level GRPO (rank complete trajectories), process reward models (per-step feedback), or filtered SFT on successful trajectories.
\textbf{解决方案}：轨迹级 GRPO（对完整轨迹排序）、过程奖励模型（每步反馈）或在成功轨迹上进行过滤式 SFT。

\emph{\textbf{Review:} Chapter~12 (LLM Agentic Training).}
\emph{\textbf{回顾：} 第~12 章（LLM 智能体训练）。}
\end{questionbox}

\begin{questionbox}[Q: Explain how GRPO is adapted for agentic training. What are the key differences from single-turn GRPO?]
\begin{questionbox}[问：解释 GRPO 如何适应智能体训练。与单轮 GRPO 相比有哪些关键差异？]

\textbf{Answer}: Single-turn GRPO: generate $N$ responses to a prompt, rank by reward, compute advantages.
\textbf{答案}：单轮 GRPO：针对一个提示生成 $N$ 个回复，按奖励排序，计算优势。

\textbf{Agentic GRPO} differences:
\textbf{智能体 GRPO} 的差异：

\begin{enumerate}
  \item \textbf{Unit of generation}: A full \emph{trajectory} (10--100 steps) instead of a single response. Each trajectory is one ``sample'' in the group.
  \item \textbf{生成单元}：完整的 \emph{轨迹}（10--100 步）而非单个回复。每条轨迹是组中的一个“样本”。
  \item \textbf{Reward}: Terminal (task success/failure) or trajectory-level (sum of step rewards). NOT per-token.
  \item \textbf{奖励}：最终奖励（任务成功/失败）或轨迹级（步奖励之和）。不是每 token 奖励。
  \item \textbf{Masking}: Only compute policy loss on the agent’s outputs (reasoning + tool calls). Mask tool \emph{outputs} (environment responses) from gradient computation.
  \item \textbf{掩码}：仅对智能体的输出（推理 + 工具调用）计算策略损失。将工具 \emph{输出}（环境响应）从梯度计算中掩蔽。
  \item \textbf{Group size}: Typically smaller ($N=4$--8) because trajectories are expensive (many forward passes per trajectory).
  \item \textbf{组大小}：通常较小（$N=4$--8），因为轨迹代价高（每条轨迹需多次前向传播）。
  \item \textbf{KL penalty}: Applied per-step to prevent drift from SFT policy at each decision point.
  \item \textbf{KL 惩罚}：每步应用，以防止在每个决策点偏离 SFT 策略。
  \item \textbf{Length normalization}: Normalize by number of agent \emph{actions} (not tokens) to avoid penalizing thorough reasoning.
  \item \textbf{长度归一化}：按智能体 \emph{动作} 数（而非 token 数）归一化，以避免惩罚详尽推理。
\end{enumerate}

\emph{\textbf{Review:} Chapters~7 and~12 (GRPO; LLM Agentic Training).}
\emph{\textbf{回顾：} 第~7 章和第~12 章（GRPO；LLM 智能体训练）。}
\end{questionbox}

\begin{questionbox}[Q: Compare STaR and Reflexion and ReAct for agents.]
\begin{questionbox}[问：比较用于智能体的 STaR、Reflexion 和 ReAct。]

\textbf{Answer}:
\textbf{答案}：

\textbf{STaR (Self-Taught Reasoner)}: Generate reasoning chains $\to$ filter by correctness $\to$ fine-tune on correct ones. \emph{Use when}: You have verifiable tasks (math, code) and want to bootstrap reasoning from a base model without RL.
\textbf{STaR（自教推理器）}：生成推理链 $\to$ 按正确性过滤 $\to$ 对正确的进行微调。\emph{何时使用}：拥有可验证任务（数学、代码）且希望从基础模型启动推理而不使用 RL。

\textbf{Reflexion}: After failure, generate verbal feedback (``What went wrong?'') $\to$ retry with reflection in context. No weight updates. \emph{Use when}: Inference-time improvement; limited compute for training; tasks where self-diagnosis is possible.
\textbf{Reflexion}：失败后，生成语言反馈（“出了什么问题？”）$\to$ 在上下文中带着反思重试。不更新权重。\emph{何时使用}：推理时改进；训练计算有限；可自我诊断的任务。

\textbf{ReAct}: Interleave Reasoning (think) + Acting (tool use) in a structured loop. \emph{Use when}: Multi-step tool use tasks; you need transparency (reasoning traces are interpretable); the agent must decide between thinking and acting.
\textbf{ReAct}：在结构化循环中交错推理（思考）和行动（工具使用）。\emph{何时使用}：多步工具使用任务；需要透明性（推理轨迹可解释）；智能体必须在思考和行动之间做决定。

\textbf{Key differences}:
\textbf{关键差异}：

\resizebox{\textwidth}{!}{%
\begin{tabular}{@{}llll@{}}
\toprule
 & \textbf{STaR} & \textbf{Reflexion} & \textbf{ReAct} \\
\midrule
Updates weights? & Yes (SFT) & No (in-context) & No (prompting) \\
更新权重？ & 是（SFT） & 否（上下文内） & 否（提示） \\
Multi-step? & No (single reasoning chain) & Yes (retry loops) & Yes (think-act cycles) \\
多步？ & 否（单条推理链） & 是（重试循环） & 是（思考-行动周期） \\
Tools? & No & Optional & Yes (required) \\
工具？ & 否 & 可选 & 是（必需） \\
Best for & Reasoning improvement & Error recovery & Tool-augmented tasks \\
最适合 & 推理改进 & 错误恢复 & 工具增强任务 \\
\bottomrule
\end{tabular}}

\emph{\textbf{Review:} Chapters~12 and~18 (LLM Agentic Training; Agent Design Patterns).}
\emph{\textbf{回顾：} 第~12 章和第~18 章（LLM 智能体训练；智能体设计模式）。}
\end{questionbox}

\begin{questionbox}[Q: Why is GRPO preferred over PPO for a research agent?]
\begin{questionbox}[问：为什么研究型智能体更倾向于使用 GRPO 而非 PPO？]

\textbf{Answer}: For a research agent with 20--100 step trajectories:
\textbf{答案}：对于一个轨迹包含 20--100 步的研究型智能体：

\textbf{PPO requires a value model}: $V(s_t)$ must predict expected total reward from the current state. For research (where state = 128K tokens of context including papers, code, and results), training an accurate value function is extremely difficult --- the value of ``having read 3 papers and written partial code'' is hard to predict.
\textbf{PPO 需要一个价值模型}：$V(s_t)$ 必须从当前状态预测期望总奖励。对于研究场景（状态 = 包含论文、代码和结果的 128K token 上下文），训练一个准确的价值函数极其困难 —— “已阅读 3 篇论文并编写了部分代码”的价值难以预测。

\textbf{GRPO avoids value estimation entirely}: It generates $N$ complete trajectories per research question and uses within-group ranking as the advantage. No need to predict intermediate value --- just compare outcomes.
\textbf{GRPO 完全避免了价值估计}：它为每个研究问题生成 $N$ 条完整轨迹，并使用组内排名作为优势。无需预测中间价值 —— 只需比较结果。

\textbf{Additional reasons}:
\textbf{其他原因}：

\begin{itemize}
  \item Research quality is binary-ish (good report vs.~bad report) --- ranking is natural.
  \item 研究质量是近二元的（好报告 vs. 坏报告）—— 排名自然。
  \item Trajectories are long and expensive; GRPO’s $N=4$ is manageable; PPO would need many rollouts for stable value estimates.
  \item 轨迹长且代价高；GRPO 的 $N=4$ 是可控的；PPO 需要大量展开才能获得稳定的价值估计。
  \item Terminal reward is sparse; GAE with sparse rewards gives noisy per-step advantages anyway.
  \item 最终奖励稀疏；使用稀疏奖励的 GAE 无论如何都会给出有噪声的每步优势。
\end{itemize}

\emph{\textbf{Review:} Chapters~7 and~12 (GRPO; LLM Agentic Training).}
\emph{\textbf{回顾：} 第~7 章和第~12 章（GRPO；LLM 智能体训练）。}
\end{questionbox}

\begin{questionbox}[Q: Design a reward function for a coding agent. What reward hacking risks exist?]
\begin{questionbox}[问：为编码智能体设计一个奖励函数。存在哪些奖励破解风险？]

\textbf{Answer}: \textbf{Reward design}: 
\textbf{答案}：\textbf{奖励设计}：
\[
R = 0.5 \cdot R_{\text{tests}} + 0.2 \cdot R_{\text{quality}} + 0.2 \cdot R_{\text{efficiency}} + 0.1 \cdot R_{\text{safety}}
\]

\begin{itemize}
  \item $R_{\text{tests}}$: Fraction of unit tests passing (0--1). Ground-truth verifiable.
  \item $R_{\text{tests}}$：通过单元测试的比例（0--1）。可基于真实值验证。
  \item $R_{\text{quality}}$: LLM judge on code style, documentation, maintainability.
  \item $R_{\text{quality}}$：LLM 对代码风格、文档、可维护性的评判。
  \item $R_{\text{efficiency}}$: $\max(0, 1 - \text{steps}/30)$ --- bonus for finishing quickly.
  \item $R_{\text{efficiency}}$：$\max(0, 1 - \text{steps}/30)$ —— 快速完成的奖励。
  \item $R_{\text{safety}}$: No dangerous operations (rm -rf, network access outside sandbox).
  \item $R_{\text{safety}}$：无危险操作（rm -rf、沙箱外网络访问）。
\end{itemize}

\textbf{Reward hacking risks}:
\textbf{奖励破解风险}：

\begin{enumerate}
  \item \textbf{Hardcoded outputs}: Agent learns to print expected test outputs directly without computing them. \emph{Fix}: Randomize test inputs; test on held-out cases.
  \item \textbf{硬编码输出}：智能体学会直接打印预期测试输出而不进行计算。\emph{修复}：随机化测试输入；在留出案例上测试。
  \item \textbf{Test deletion}: Agent modifies/deletes failing tests. \emph{Fix}: Sandbox tests as read-only.
  \item \textbf{测试删除}：智能体修改/删除失败的测试。\emph{修复}：将测试沙箱设为只读。
  \item \textbf{Trivial solutions}: Agent writes minimal code that passes tests but doesn’t generalize. \emph{Fix}: Large, diverse test suites; property-based testing.
  \item \textbf{简单解决方案}：智能体编写通过测试但不具备泛化能力的最小化代码。\emph{修复}：大型多样化的测试套件；基于属性的测试。
  \item \textbf{Efficiency gaming}: Agent skips reasoning steps to maximize efficiency bonus. \emph{Fix}: Minimum quality threshold before efficiency bonus applies.
  \item \textbf{效率投机}：智能体跳过推理步骤以最大化效率奖励。\emph{修复}：在效率奖励生效前设置最低质量标准。
\end{enumerate}

\emph{\textbf{Review:} Chapters~9, 12, and~19 (Reward Model Training; LLM Agentic Training; Agentic Environments).}
\emph{\textbf{回顾：} 第~9 章、第~12 章和第~19 章（奖励模型训练；LLM 智能体训练；智能体环境）。}
\end{questionbox}

\section{Listwise Rewards and Advanced RM Questions}
\section{列表级奖励与高级奖励模型问题}
\label{listwise-rewards-and-advanced-rm-questions}

\begin{questionbox}[Q: Explain the Plackett-Luce model. How does it generalize Bradley-Terry?]
\begin{questionbox}[问：解释 Plackett-Luce 模型。它如何推广 Bradley-Terry？]

\textbf{Answer}: Bradley-Terry models \emph{pairwise} preferences: $P(y_1 \succ y_2) = \sigma(r(y_1) - r(y_2))$.
\textbf{答案}：Bradley-Terry 建模 \emph{成对} 偏好：$P(y_1 \succ y_2) = \sigma(r(y_1) - r(y_2))$。

Plackett-Luce models \emph{full rankings} of $K$ items as sequential selection: 
\[
P(\pi) = \prod_{i=1}^K \frac{e^{r(y_{\pi(i)})}}{\sum_{j=i}^K e^{r(y_{\pi(j)})}}
\]
Plackett-Luce 将 $K$ 个项的 \emph{完整排名} 建模为顺序选择：
\[
P(\pi) = \prod_{i=1}^K \frac{e^{r(y_{\pi(i)})}}{\sum_{j=i}^K e^{r(y_{\pi(j)})}}
\]

Interpretation: Sequentially pick the best remaining item. Position 1 = softmax over all $K$; position 2 = softmax over remaining $K-1$; etc.
解释：顺序挑选剩余最佳项。位置 1 = 对所有 $K$ 个项计算 softmax；位置 2 = 对剩余 $K-1$ 个项计算 softmax；以此类推。

\textbf{Generalization}: For $K=2$, PL reduces exactly to BT: $P(y_1 \succ y_2) = \frac{e^{r(y_1)}}{e^{r(y_1)} + e^{r(y_2)}} = \sigma(r(y_1) - r(y_2))$.
\textbf{推广}：当 $K=2$ 时，PL 精确退化为 BT：$P(y_1 \succ y_2) = \frac{e^{r(y_1)}}{e^{r(y_1)} + e^{r(y_2)}} = \sigma(r(y_1) - r(y_2))$。

\textbf{Advantage}: A ranking of $K=8$ items provides $\binom{8}{2} = 28$ implicit pairwise comparisons plus relative margin information --- much richer training signal than a single pair.
\textbf{优势}：$K=8$ 个项的排名提供了 $\binom{8}{2} = 28$ 个隐式成对比较以及相对间隔信息 —— 比单个对丰富得多的训练信号。

\emph{\textbf{Review:} Chapter~9 (Reward Model Training).}
\emph{\textbf{回顾：} 第~9 章（奖励模型训练）。}
\end{questionbox}

\begin{questionbox}[Q: What is a Process Reward Model (PRM) and when is it better than an Outcome Reward Model (ORM)?]
\begin{questionbox}[问：什么是过程奖励模型 (PRM)，它何时优于结果奖励模型 (ORM)？]

\textbf{Answer}: \textbf{ORM}: Scores the final output only. $r(x, y_{\text{final}})$ = one scalar for the complete response.
\textbf{答案}：\textbf{ORM}：仅对最终输出评分。$r(x, y_{\text{final}})$ = 一个标量，代表完整回复。
\end{questionbox}

\textbf{PRM}: Scores each \emph{step} of reasoning. $r(x, y_{\text{step } t})$ = scalar per intermediate step.
\textbf{PRM}：对推理的每个\emph{步骤}进行评分。$r(x, y_{\text{step } t})$ = 每个中间步骤的标量值。

\textbf{PRM is better when}:
\textbf{PRM 更适用于}：

\begin{enumerate}
  \item \textbf{Long reasoning chains}: Math problems with 10+ steps. ORM can’t tell which step went wrong; PRM provides per-step credit assignment.
  \item \textbf{长推理链}：具有 10 个或以上步骤的数学问题。ORM 无法判断哪一步出错；PRM 提供逐步骤的信用分配。
  \item \textbf{Search/verification}: PRM enables tree search (beam search over reasoning steps, prune branches with low step-reward).
  \item \textbf{搜索/验证}：PRM 支持树搜索（对推理步骤进行束搜索，剪枝步骤奖励低的枝干）。
  \item \textbf{Training signal density}: PRM gives $T$ rewards per trajectory (one per step) vs.~ORM’s single reward $\to$ lower variance advantage estimates.
  \item \textbf{训练信号密度}：PRM 每条轨迹给出 $T$ 个奖励（每步一个），而 ORM 只有一个奖励 $\to$ 优势估计方差更低。
\end{enumerate}

\textbf{ORM is better when}: Tasks are short (single-turn); step boundaries are unclear; annotation cost for per-step labels is prohibitive.
\textbf{ORM 更适用于}：任务较短（单回合）；步骤边界不清晰；逐步骤标注的成本过高。

\textbf{PRM annotation}: Can be automated via ``Math-Shepherd'' approach: for each step, complete the solution from that point multiple times. If completions from step $t$ succeed but completions from step $t+1$ fail, step $t+1$ is likely wrong.
\textbf{PRM 标注}：可通过“Math-Shepherd”方法自动化：对于每个步骤，从该点多次完成解答。如果从步骤 $t$ 开始的完成能成功，但从步骤 $t+1$ 开始的完成失败，则步骤 $t+1$ 很可能是错误的。

\emph{\textbf{Review:} Chapters~9 and~13 (Reward Model Training; RL for Large Reasoning Models).}
\emph{\textbf{回顾：}第 9 章和第 13 章（奖励模型训练；面向大型推理模型的强化学习）。}
\end{questionbox}
\end{questionbox}

\section{RL for Large Reasoning Models Questions}
\section{面向大型推理模型的强化学习问题}
\label{rl-for-large-reasoning-models-questions}
\label{rl-for-large-reasoning-models-questions}

\begin{questionbox}[Q: Why does DeepSeek-R1 not use a Process Reward Model despite training on long reasoning chains?]
\begin{questionbox}[问：为什么 DeepSeek-R1 在长推理链上训练却不使用过程奖励模型？]
\textbf{Answer}: DeepSeek-R1 uses only \textbf{outcome-based rewards} (accuracy + format) for several reasons:
\textbf{答案}：DeepSeek-R1 仅使用基于结果的奖励（准确率+格式），原因如下：

\begin{enumerate}
  \item \textbf{Verifiable tasks}: Math and code have deterministic ground-truth answers. The binary accuracy reward provides sufficient signal even for long chains.
  \item \textbf{可验证任务}：数学和代码具有确定性的真实答案。即使是长链条，二元准确率奖励也能提供足够的信号。
  \item \textbf{PRM failure modes}: Step-level reward models introduce their own reward hacking --- the model can learn to produce steps that ``look correct'' to the PRM without actually being correct.
  \item \textbf{PRM 失效模式}：步骤级奖励模型会引入自身的奖励破解——模型可能学会生成对 PRM 而言“看起来正确”但实际上并不正确的步骤。
  \item \textbf{GRPO’s group normalization}: By sampling $G$ completions per prompt and normalizing advantages within each group, GRPO naturally provides relative signal about which reasoning \emph{strategies} work, even without per-step rewards.
  \item \textbf{GRPO 的群体归一化}：通过对每个提示采样 $G$ 个完成结果并在每组内归一化优势，GRPO 即使没有逐步骤奖励也能自然提供关于哪些推理\emph{策略}有效的相对信号。
  \item \textbf{Emergent self-correction}: With outcome-only rewards, the model learns to self-correct within chains (the ``aha moment''), which wouldn’t emerge if per-step rewards micromanage the reasoning process.
  \item \textbf{涌现的自我纠正}：仅使用结果奖励时，模型学会在链条内自我纠正（“顿悟时刻”），而如果逐步骤奖励对推理过程进行微观管理，则不会出现这种现象。
\end{enumerate}

\textbf{Key insight}: The verifiability of the task domain is what makes PRMs unnecessary --- for subjective tasks (creative writing), outcome-only rewards may not suffice.
\textbf{关键见解}：任务领域的可验证性使得 PRM 变得不必要——对于主观任务（如创意写作），仅使用结果奖励可能不够。

\emph{\textbf{Review:} Chapter~13 (RL for Large Reasoning Models).}
\emph{\textbf{回顾：}第 13 章（面向大型推理模型的强化学习）。}
\end{questionbox}
\end{questionbox}

\begin{questionbox}[Q: Explain the test-time compute scaling law and its implications for model deployment]
\begin{questionbox}[问：解释测试时计算扩展规律及其对模型部署的影响]
\textbf{Answer}: The test-time compute scaling law states: 
\[
\text{Accuracy}(C_{\text{train}}, C_{\text{test}}) \approx f(\alpha \log C_{\text{train}} + \beta \log C_{\text{test}})
\]
\textbf{答案}：测试时计算扩展规律表述为：
\[
\text{Accuracy}(C_{\text{train}}, C_{\text{test}}) \approx f(\alpha \log C_{\text{train}} + \beta \log C_{\text{test}})
\]

\textbf{Implications}:
\textbf{含义}：

\begin{enumerate}
  \item \textbf{Compute equivalence}: A 7B model with 64$\times$ more inference tokens can match a 70B model with 1$\times$ tokens on reasoning tasks.
  \item \textbf{计算等价性}：一个使用 64$\times$ 更多推理 token 的 7B 模型，可以在推理任务上匹配一个使用 1$\times$ token 的 70B 模型。
  \item \textbf{Adaptive allocation}: Easy questions get short chains (cheap); hard questions get long chains (expensive). Average cost is lower than always using a large model.
  \item \textbf{自适应分配}：简单问题获得短链条（廉价）；困难问题获得长链条（昂贵）。平均成本低于始终使用大型模型。
  \item \textbf{Deployment flexibility}: Instead of one large model, deploy a smaller reasoning model and scale inference compute per-query based on difficulty.
  \item \textbf{部署灵活性}：部署一个较小的推理模型，并根据难度对每个查询的推理计算进行缩放，而不是使用一个大型模型。
  \item \textbf{Diminishing returns}: The log relationship means doubling test-time compute gives diminishing accuracy gains --- there’s an optimal allocation between training and inference compute.
  \item \textbf{收益递减}：对数关系意味着加倍测试时计算会带来递减的准确率收益——训练计算和推理计算之间存在最优分配。
\end{enumerate}

\textbf{The ``overthinking'' failure}: Very long chains can \emph{decrease} accuracy due to error accumulation and attention dilution. Optimal chain length depends on problem difficulty.
\textbf{“过度思考”失效}：过长的链条可能由于错误累积和注意力分散而\emph{降低}准确率。最优链条长度取决于问题难度。

\emph{\textbf{Review:} Chapter~13 (RL for Large Reasoning Models).}
\emph{\textbf{回顾：}第 13 章（面向大型推理模型的强化学习）。}
\end{questionbox}
\end{questionbox}

\begin{questionbox}[Q: How does MCTS (Monte Carlo Tree Search) apply to LLM reasoning?]
\begin{questionbox}[问：MCTS（蒙特卡洛树搜索）如何应用于大语言模型推理？]
\textbf{Answer}: MCTS for reasoning treats each partial solution as a tree node:
\textbf{答案}：用于推理的 MCTS 将每个部分解视为一个树节点：

\textbf{Four phases per iteration}:
\textbf{每次迭代的四个阶段}：

\begin{enumerate}
  \item \textbf{Selection}: Navigate from root using UCB: $\text{UCB}(s) = Q(s) + c\sqrt{\frac{\ln N(\text{parent})}{N(s)}}$
  \item \textbf{选择}：使用 UCB 从根节点导航：$\text{UCB}(s) = Q(s) + c\sqrt{\frac{\ln N(\text{parent})}{N(s)}}$
  \item \textbf{Expansion}: Generate new reasoning steps (child nodes) from the LLM
  \item \textbf{扩展}：从大语言模型生成新的推理步骤（子节点）
  \item \textbf{Simulation}: Complete the solution from the new node (rollout)
  \item \textbf{模拟}：从新节点完成解答（展开）
  \item \textbf{Backpropagation}: Update Q-values along the path based on final correctness
  \item \textbf{反向传播}：根据最终正确性沿路径更新 Q 值
\end{enumerate}

\textbf{Key differences from game MCTS}:
\textbf{与游戏 MCTS 的关键区别}：

\begin{itemize}
  \item \textbf{Branching factor}: Reasoning has enormous branching factor (any next sentence is possible). Practical implementations use the LLM’s top-k outputs to limit branches.
  \item \textbf{分支因子}：推理具有极大的分支因子（任何下一个句子都有可能）。实际实现使用大语言模型的 top-k 输出限制分支。
  \item \textbf{Value function}: A trained PRM estimates partial solution quality, replacing random rollouts.
  \item \textbf{值函数}：一个训练好的 PRM 估计部分解的质量，替代随机展开。
  \item \textbf{Step granularity}: Each ``step'' might be one sentence, one equation, or one logical inference --- choosing granularity matters.
  \item \textbf{步骤粒度}：每个“步骤”可以是一个句子、一个方程或一个逻辑推理——选择粒度很重要。
\end{itemize}

\textbf{Used by}: AlphaProof (math olympiad), and hypothesized for OpenAI o1/o3’s hidden reasoning.
\textbf{使用方}：AlphaProof（数学奥林匹克），并被推测用于 OpenAI o1/o3 的隐藏推理。

\emph{\textbf{Review:} Chapter~13 (RL for Large Reasoning Models).}
\emph{\textbf{回顾：}第 13 章（面向大型推理模型的强化学习）。}
\end{questionbox}
\end{questionbox}

\begin{questionbox}[Q: Compare distillation vs direct RL for creating small reasoning models]
\begin{questionbox}[问：比较蒸馏与直接强化学习在创建小型推理模型上的差异]
\textbf{Answer}:
\textbf{答案}：

\textbf{Distillation} (DeepSeek-R1-Distill approach):
\textbf{蒸馏}（DeepSeek-R1-Distill 方法）：

\begin{itemize}
  \item Generate reasoning chains from large model (R1-671B)
  \item 从大型模型（R1-671B）生成推理链
  \item SFT small model on these chains
  \item 在这些链条上对小型模型进行监督微调
  \item Result: Small model mimics large model’s reasoning \emph{format}
  \item 结果：小型模型模仿大型模型的推理\emph{格式}
  \item Pro: Cheap (just SFT). Con: May learn surface patterns not true reasoning.
  \item 优点：成本低（仅需 SFT）。缺点：可能学到表面模式而非真正的推理。
\end{itemize}

\textbf{Direct RL} on small model:
\textbf{在小模型上直接进行强化学习}：

\begin{itemize}
  \item Train small model with GRPO/PPO against verifiable rewards
  \item 使用 GRPO/PPO 基于可验证奖励训练小型模型
  \item Model discovers its own reasoning strategies
  \item 模型发现自己的推理策略
  \item Pro: Genuine capability. Con: Much more compute; may not converge for very small models.
  \item 优点：真正的能力。缺点：计算量大得多；对于极小的模型可能不收敛。
\end{itemize}

\textbf{Empirical finding}: R1-Distill-7B (distilled) outperforms direct-RL-7B on most benchmarks. The reasoning chains from the large model provide such strong supervision that SFT alone is competitive. However, distilled models show less generalization to truly novel problem types.
\textbf{实证发现}：R1-Distill-7B（蒸馏）在大多数基准测试上优于直接强化学习的 7B 模型。来自大型模型的推理链提供了如此强大的监督，以至于仅 SFT 就具有竞争力。然而，蒸馏模型对真正新颖的问题类型泛化能力较差。

\textbf{Best practice}: Distill first (cheap baseline), then optionally run RL on the distilled model for further gains (``distill + RL'' combo used by Qwen).
\textbf{最佳实践}：先蒸馏（低成本基线），然后可选地在蒸馏模型上运行强化学习以获得进一步收益（通义千问使用的“蒸馏+强化学习”组合）。

\emph{\textbf{Review:} Chapter~13 (RL for Large Reasoning Models).}
\emph{\textbf{回顾：}第 13 章（面向大型推理模型的强化学习）。}
\end{questionbox}
\end{questionbox}

\section{LLM Evaluation Questions}
\section{大语言模型评估问题}
\label{llm-evaluation-questions}
\label{llm-evaluation-questions}

\begin{questionbox}[Q: Derive the ELO rating update rule and explain why Chatbot Arena uses it]
\begin{questionbox}[问：推导 ELO 评分更新规则并解释为什么 Chatbot Arena 使用它]
\textbf{Answer}: \textbf{ELO derivation}:
\textbf{答案}：\textbf{ELO 推导}：

Expected score of player A vs B: $E_A = \frac{1}{1 + 10^{(R_B - R_A)/400}}$ (logistic model).
玩家 A 对玩家 B 的期望得分：$E_A = \frac{1}{1 + 10^{(R_B - R_A)/400}}$（逻辑斯谛模型）。

After a match with actual score $S_A \in \{0, 0.5, 1\}$: $R_A' = R_A + K(S_A - E_A)$
在得到实际得分 $S_A \in \{0, 0.5, 1\}$ 的一场比赛后：$R_A' = R_A + K(S_A - E_A)$

The $K$-factor controls update magnitude (higher $K$ = more reactive to recent results).
$K$ 因子控制更新幅度（$K$ 越高 = 对最近结果反应越灵敏）。

\textbf{Why Chatbot Arena uses ELO}:
\textbf{为什么 Chatbot Arena 使用 ELO}：

\begin{enumerate}
  \item \textbf{Transitivity}: If model A beats B and B beats C, ELO predicts A beats C. This gives a total ordering from pairwise comparisons.
  \item \textbf{传递性}：如果模型 A 击败 B，B 击败 C，则 ELO 预测 A 击败 C。这给出了从成对比较中得出的全序。
  \item \textbf{Online updates}: New models can be added without re-evaluating all pairs. Each new comparison updates ratings incrementally.
  \item \textbf{在线更新}：可以添加新模型而无需重新评估所有配对。每次新比较都会增量更新评分。
  \item \textbf{Confidence}: After $N$ comparisons, rating uncertainty shrinks as $O(1/\sqrt{N})$. Standard error: $\text{SE} \approx \frac{400}{\sqrt{N}}$.
  \item \textbf{信心}：经过 $N$ 次比较后，评分不确定性按 $O(1/\sqrt{N})$ 缩减。标准误差：$\text{SE} \approx \frac{400}{\sqrt{N}}$。
  \item \textbf{Human preference capture}: Real users provide honest preferences without needing to articulate criteria. The aggregate reveals true model quality.
  \item \textbf{捕捉人类偏好}：真实用户无需阐述标准即可提供诚实的偏好。聚合结果揭示真实的模型质量。
\end{enumerate}

\textbf{Chatbot Arena specifics}: Uses Bradley-Terry MLE (equivalent to ELO at convergence) with bootstrap confidence intervals. Style-controlled ELO removes length/formatting bias.
\textbf{Chatbot Arena 具体细节}：使用 Bradley-Terry 最大似然估计（收敛时等价于 ELO）结合自助法置信区间。风格控制的 ELO 消除了长度/格式偏差。

\emph{\textbf{Review:} Chapter~14 (LLM Evaluation).}
\emph{\textbf{回顾：}第 14 章（大语言模型评估）。}
\end{questionbox}
\end{questionbox}

## Section Title
## 章节标题

\begin{questionbox}[Q: What is the pass@k metric for code generation and why is the unbiased estimator important?]
\textbf{Answer}: \textbf{pass@k} = probability that at least one of $k$ generated samples passes all test cases.

\textbf{Naive (biased) estimator}: Generate $k$ samples, check if any passes. Problem: high variance, expensive (need many trials per problem).


\textbf{Unbiased estimator} (Chen et al., 2021): Generate $n \geq k$ samples, count $c$ that pass: 
\[
\text{pass@}k = 1 - \frac{\binom{n-c}{k}}{\binom{n}{k}}
\]


\textbf{Why unbiased matters}:


\begin{enumerate}
  \item Generates $n$ samples once (e.g., $n=200$) and computes pass@1, pass@10, pass@100 from the same samples
  \item No need to repeat the entire evaluation $k$ times
  \item Statistically exact (combinatorial argument: fraction of $k$-subsets with no correct sample)
  \item Numerically stable computation via log-space: $\text{pass@}k = 1 - \exp\left(\sum_{i=0}^{k-1} \log(n-c-i) - \log(n-i)\right)$
\end{enumerate}


\textbf{Intuition}: If 50/200 samples pass ($c=50$, $n=200$), pass@1 $\approx 0.25$, pass@10 $\approx 0.94$. The estimator counts what fraction of $k$-sized draws would contain at least one success.


\emph{\textbf{Review:} Chapters~14 and~19 (LLM Evaluation; Agentic Environments).}
\end{questionbox}

\begin{questionbox}[Q: 代码生成中的pass@k指标是什么？为什么无偏估计很重要？]
\textbf{答案}：\textbf{pass@k} = 生成的 $k$ 个样本中至少有一个通过所有测试用例的概率。

\textbf{朴素（有偏）估计器}：生成 $k$ 个样本，检查是否有任一通过。问题：方差大，成本高（每个问题需要多次试验）。

\textbf{无偏估计器}（Chen等人，2021）：生成 $n \geq k$ 个样本，统计通过的个数 $c$：
\[
\text{pass@}k = 1 - \frac{\binom{n-c}{k}}{\binom{n}{k}}
\]

\textbf{为何无偏很重要}：

\begin{enumerate}
  \item 只需生成一次 $n$ 个样本（例如 $n=200$），即可从同一批样本中计算 pass@1、pass@10、pass@100
  \item 无需将整个评估重复 $k$ 次
  \item 统计上精确（组合论证：在 $k$ 大小的子集中不包含任何正确样本的比例）
  \item 通过对数空间进行数值稳定计算：$\text{pass@}k = 1 - \exp\left(\sum_{i=0}^{k-1} \log(n-c-i) - \log(n-i)\right)$
\end{enumerate}

\textbf{直观理解}：如果 50/200 个样本通过（$c=50$, $n=200$），则 pass@1 $\approx 0.25$，pass@10 $\approx 0.94$。该估计器统计 $k$ 大小的抽取中包含至少一个成功的比例。

\emph{\textbf{复习：} 第14章和第19章（LLM评估；智能体环境）。}
\end{questionbox}

\begin{questionbox}[Q: How do you detect and mitigate benchmark contamination?]
\textbf{Answer}: \textbf{Contamination}: Training data contains benchmark test examples (or close paraphrases), inflating scores.


\textbf{Detection methods}:


\begin{enumerate}
  \item \textbf{N-gram overlap}: Check if training data contains exact or near-exact matches to test items. 8-gram overlap with $>$80\% coverage is suspicious.
  \item \textbf{Canary strings}: Insert unique identifiers in test sets; check if model can reproduce them.
  \item \textbf{Rephrased benchmarks}: Create semantically equivalent but textually different versions of benchmarks. Large accuracy drops suggest memorization.
  \item \textbf{Temporal analysis}: Model performance on pre-training-cutoff vs post-cutoff test items. Unusually high performance on old items suggests contamination.
  \item \textbf{Membership inference}: Statistical tests for whether specific examples were in training data.
\end{enumerate}


\textbf{Mitigation}:


\begin{itemize}
  \item \textbf{Dynamic benchmarks}: Regularly generate new test items (LiveCodeBench, Chatbot Arena)
  \item \textbf{Private test sets}: Keep test items secret (LMSYS)
  \item \textbf{Decontamination during training}: Remove detected overlaps from training data
  \item \textbf{Report contamination analysis}: Disclose overlap metrics alongside benchmark scores
\end{itemize}


\emph{\textbf{Review:} Chapter~14 (LLM Evaluation).}
\end{questionbox}

\begin{questionbox}[Q: 如何检测和缓解基准污染？]
\textbf{答案}：\textbf{污染}：训练数据包含基准测试示例（或近似改写），从而虚高分数。

\textbf{检测方法}：

\begin{enumerate}
  \item \textbf{N-gram 重叠}：检查训练数据是否包含与测试项精确或近乎精确的匹配。8-gram 重叠且覆盖率 >80% 则值得怀疑。
  \item \textbf{Canary 字符串}：在测试集中插入唯一标识符；检查模型是否能复现它们。
  \item \textbf{改写基准}：创建语义等价但文本不同的基准版本。准确率大幅下降暗示记忆。
  \item \textbf{时间分析}：比较模型在训练截止前与截止后的测试项上的表现。在旧项上异常高的表现暗示污染。
  \item \textbf{成员推断}：通过统计检验判断特定示例是否在训练数据中。
\end{enumerate}

\textbf{缓解措施}：

\begin{itemize}
  \item \textbf{动态基准}：定期生成新的测试项（LiveCodeBench, Chatbot Arena）
  \item \textbf{私有测试集}：保密测试项（LMSYS）
  \item \textbf{训练时去污染}：从训练数据中移除检测到的重叠
  \item \textbf{报告污染分析}：在基准分数旁公开重叠指标
\end{itemize}

\emph{\textbf{复习：} 第14章（LLM评估）。}
\end{questionbox}

\begin{questionbox}[Q: Explain position bias in LLM-as-Judge and how to mitigate it]
\textbf{Answer}: \textbf{Position bias}: When using an LLM to judge two responses (A vs B), the model systematically prefers the response in a particular position (usually first or last), regardless of quality.


\textbf{Empirical magnitude}: GPT-4 shows 10--15\% position bias; Claude shows 5--10\%. Smaller models show larger bias.


\textbf{Mitigation strategies}:


\begin{enumerate}
  \item \textbf{Position swapping}: Judge each pair twice (A-B and B-A). Final decision = majority. If disagreement, mark as ``tie.'' This eliminates systematic position bias but doubles cost.
  \item \textbf{Multi-judge panels}: Use 3+ different models as judges. Majority vote reduces individual model biases.
  \item \textbf{Reference-guided}: Provide a rubric or reference answer. Judges score each response independently against the rubric, then compare scores (eliminates pairwise comparison entirely).
  \item \textbf{Calibrated prompting}: Add explicit instruction: ``The order of presentation is random and should not influence your judgment.''
\end{enumerate}


\textbf{Additional biases}: Verbosity bias (prefers longer responses), self-enhancement bias (models prefer their own outputs), authority bias (defers to responses that cite sources).


\emph{\textbf{Review:} Chapter~14 (LLM Evaluation).}
\end{questionbox}

\begin{questionbox}[Q: 解释LLM作为评判者中的位置偏差及其缓解方法]
\textbf{答案}：\textbf{位置偏差}：当使用LLM评判两个回复（A vs B）时，模型系统性地偏好特定位置（通常是第一个或最后一个）的回复，而与质量无关。

\textbf{经验幅度}：GPT-4表现出10--15%的位置偏差；Claude表现出5--10%。较小的模型偏差更大。

\textbf{缓解策略}：

\begin{enumerate}
  \item \textbf{位置交换}：对每对评判两次（A-B和B-A）。最终决策取多数。若不一致，标记为“平局”。这消除了系统性位置偏差，但成本翻倍。
  \item \textbf{多评判者小组}：使用3个以上不同模型作为评判者。多数投票减少单个模型偏差。
  \item \textbf{参考引导}：提供评分标准或参考答案。评判者根据标准独立对每个回复打分，然后比较分数（完全消除成对比较）。
  \item \textbf{校准提示}：添加明确指令：“呈现顺序是随机的，不应影响你的判断。”
\end{enumerate}

\textbf{其他偏差}：冗长偏差（偏好更长的回复）、自我增强偏差（模型偏好自己的输出）、权威偏差（倾向于引用来源的回复）。

\emph{\textbf{复习：} 第14章（LLM评估）。}
\end{questionbox}

\section{Agentic Memory Questions}
\label{agentic-memory-questions}
\section{智能体记忆问题}
\label{agentic-memory-questions}

\begin{questionbox}[Q: Compare the four types of agentic memory and when each is critical]
\textbf{Answer}:


\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{Type} & \textbf{What it stores} & \textbf{Access pattern} & \textbf{Critical when} \\
\midrule
Working & Current context/scratchpad & Always in context & Complex multi-step reasoning \\
Episodic & Past experiences & Retrieved by similarity & Learning from past mistakes \\
Semantic & Facts and knowledge & Retrieved by concept & Domain-specific tasks \\
Procedural & Skills and patterns & Triggered by task type & Repeated tool-use \\
\bottomrule
\end{tabular}


\textbf{Key insight}: These aren’t independent --- they interact. Episodic memory feeds semantic memory (generalizing from episodes to facts). Procedural memory is refined by episodic feedback (learning which tool sequences work). Working memory orchestrates retrieval from all other types.


\textbf{MemGPT analogy}: Working = hot (in-context), Episodic/Semantic = warm (vector store), Procedural = cold (archived policies). The agent itself decides when to page information in/out.


\emph{\textbf{Review:} Chapter~16 (Agentic Memory Systems).}
\end{questionbox}

\begin{questionbox}[Q: 比较四种智能体记忆类型及其各自的关键应用场景]
\textbf{答案}：

\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{类型} & \textbf{存储内容} & \textbf{访问模式} & \textbf{关键场景} \\
\midrule
工作记忆 & 当前上下文/草稿 & 始终在上下文中 & 复杂多步推理 \\
情景记忆 & 过去经验 & 按相似度检索 & 从过去错误中学习 \\
语义记忆 & 事实与知识 & 按概念检索 & 领域特定任务 \\
程序记忆 & 技能与模式 & 按任务类型触发 & 重复工具使用 \\
\bottomrule
\end{tabular}

\textbf{关键洞察}：这些并非独立存在——它们相互交互。情景记忆为语义记忆提供素材（从情景中归纳出事实）。程序记忆通过情景反馈得到优化（学习哪些工具序列有效）。工作记忆协调从其他所有类型的检索。

\textbf{MemGPT类比}：工作记忆 = 热（上下文中），情景/语义记忆 = 温（向量存储），程序记忆 = 冷（归档策略）。智能体自行决定何时调入/调出信息。

\emph{\textbf{复习：} 第16章（智能体记忆系统）。}
\end{questionbox}

\begin{questionbox}[Q: How does temporal decay work in memory retrieval and why is it important?]
\textbf{Answer}: \textbf{Temporal decay} down-weights older memories during retrieval: 
\[
\text{score}(m) = \alpha \cdot \text{similarity}(q, m) + (1 - \alpha) \cdot \text{recency}(m)
\]
 where $\text{recency}(m) = e^{-\lambda \cdot \Delta t}$ with $\Delta t$ = time since last access.


\textbf{Why it’s important}:


\begin{enumerate}
  \item \textbf{Relevance decay}: User preferences change. A preference from 6 months ago may be outdated.
  \item \textbf{Contradiction resolution}: When old and new information conflict, recency bias naturally prefers current truth.
  \item \textbf{Retrieval efficiency}: Without decay, memory grows unbounded and retrieval returns increasingly irrelevant ancient items.
  \item \textbf{Cognitive plausibility}: Humans forget too --- recent events are more accessible. This mirrors the spacing effect.
\end{enumerate}


\textbf{Access-based refresh}: When a memory is retrieved and used, its timestamp updates (similar to LRU caching). Frequently-accessed memories stay ``fresh'' regardless of creation date.


\textbf{Decay rate tuning}: $\lambda$ depends on domain. Customer service: high decay (preferences change fast). Legal/medical: low decay (facts persist). Can be learned via RL.


\emph{\textbf{Review:} Chapter~16 (Agentic Memory Systems).}
\end{questionbox}

\begin{questionbox}[Q: 时间衰减在记忆检索中如何工作？为什么它很重要？]
\textbf{答案}：\textbf{时间衰减}在检索时降低较久记忆的权重：
\[
\text{score}(m) = \alpha \cdot \text{similarity}(q, m) + (1 - \alpha) \cdot \text{recency}(m)
\]
其中 $\text{recency}(m) = e^{-\lambda \cdot \Delta t}$，$\Delta t$ 为自上次访问以来的时间。

\textbf{为何重要}：

\begin{enumerate}
  \item \textbf{相关性衰减}：用户偏好会变化。6个月前的偏好可能已过时。
  \item \textbf{矛盾解决}：当新旧信息冲突时，近因偏差自然倾向当前真相。
  \item \textbf{检索效率}：若无衰减，记忆无限制增长，检索会返回越来越不相关的古老项。
  \item \textbf{认知合理性}：人类也会遗忘——近期事件更易获取。这反映了间隔效应。
\end{enumerate}

\textbf{基于访问的刷新}：当记忆被检索并使用后，其时间戳更新（类似于LRU缓存）。频繁访问的记忆无论创建日期如何都保持“新鲜”。

\textbf{衰减速率调优}：$\lambda$ 取决于领域。客户服务：高衰减（偏好变化快）。法律/医疗：低衰减（事实持久）。可通过强化学习学习。

\emph{\textbf{复习：} 第16章（智能体记忆系统）。}
\end{questionbox}

\begin{questionbox}[Q: How can RL be used to train memory operations?]
\textbf{Answer}: Memory operations (write/read/update/delete) can be actions in the agent’s MDP:


\textbf{Formulation}:


\begin{itemize}
  \item \textbf{State}: Current context + memory state
  \item \textbf{Actions}: Standard actions + \texttt{memory\_write(key/value)}, \texttt{memory\_read(query)}, \texttt{memory\_delete(key)}
  \item \textbf{Reward}: Task success (did memory help?) + memory efficiency penalty (fewer reads = better)
\end{itemize}


\textbf{What RL learns}:


\begin{enumerate}
  \item \textbf{What to store}: Important information (API keys/user preferences) vs ephemeral details
  \item \textbf{When to retrieve}: Before answering domain questions vs during general chat
  \item \textbf{Compression policy}: When to summarize old memories vs keep verbatim
  \item \textbf{Forgetting}: When old information is stale and should be removed
\end{enumerate}

\emph{\textbf{Review:} Chapter~16 (Agentic Memory Systems).}
\end{questionbox}

\begin{questionbox}[Q: 如何使用强化学习训练记忆操作？]
\textbf{答案}：记忆操作（写入/读取/更新/删除）可以作为智能体MDP中的动作：

\textbf{形式化}：

\begin{itemize}
  \item \textbf{状态}：当前上下文 + 记忆状态
  \item \textbf{动作}：标准动作 + \texttt{memory\_write(key/value)}、\texttt{memory\_read(query)}、\texttt{memory\_delete(key)}
  \item \textbf{奖励}：任务成功（记忆是否有帮助？）+ 记忆效率惩罚（读取次数少 = 更好）
\end{itemize}

\textbf{强化学习学到什么}：

\begin{enumerate}
  \item \textbf{存储什么}：重要信息（API密钥/用户偏好）vs 临时细节
  \item \textbf{何时检索}：在回答领域问题前 vs 在一般对话中
  \item \textbf{压缩策略}：何时总结旧记忆 vs 保留原文
  \item \textbf{遗忘}：何时旧信息过时应该移除
\end{enumerate}

\emph{\textbf{复习：} 第16章（智能体记忆系统）。}
\end{questionbox}

## Agent Orchestration Questions  
## 智能体编排问题  

\begin{questionbox}[Q: Explain the context budget problem and how to solve it with dynamic allocation]  
**Answer**: \textbf{The problem}: An agent has context window $L$ tokens but needs space for:  
\[
C = S + M + T + H + R \leq L
\]  
where $S$ = system prompt, $M$ = memory/retrieved context, $T$ = tool descriptions, $H$ = conversation history, $R$ = reserved for response.  

\textbf{答案}：\textbf{问题}：智能体拥有上下文窗口 $L$ 个令牌，但需要为以下内容预留空间：  
\[
C = S + M + T + H + R \leq L
\]  
其中 $S$ = 系统提示词，$M$ = 记忆/检索到的上下文，$T$ = 工具描述，$H$ = 对话历史，$R$ = 为响应预留的空间。  

As conversations grow, $H$ increases and pushes out other components.  

随着对话增长，$H$ 不断增大，挤占了其他组件的空间。  

\textbf{Dynamic allocation strategy}:  

\textbf{动态分配策略}：  

\begin{enumerate}
  \item \textbf{Fixed minimums}: $S_{\min}$, $R_{\min}$ are non-negotiable  
  \item \textbf{Adaptive history}: Summarize old turns when $H > H_{\max}$. Keep last $k$ turns verbatim; summarize the rest.  
  \item \textbf{On-demand tools}: Only include tool descriptions relevant to current query (not all 50 tools). Use a classifier or embedding similarity to select top-$k$ tools.  
  \item \textbf{Lazy memory}: Retrieve memory only when needed (after analyzing the query) rather than pre-loading.  
\end{enumerate}  

\begin{enumerate}
  \item \textbf{固定最小值}：$S_{\min}$、$R_{\min}$ 不可协商  
  \item \textbf{自适应历史}：当 $H > H_{\max}$ 时，对旧轮次进行摘要。保留最近 $k$ 轮的原文；其余进行摘要。  
  \item \textbf{按需工具}：仅包含与当前查询相关的工具描述（而非全部 50 个工具）。使用分类器或嵌入相似度选择 top-$k$ 工具。  
  \item \textbf{惰性记忆}：仅在需要时（分析查询后）检索记忆，而非预加载。  
\end{enumerate}  

\textbf{Overflow handling}: When total exceeds $L$ even after compression:  

\textbf{溢出处理}：当压缩后总量仍超过 $L$ 时：  

\begin{itemize}
  \item Drop least-important tool descriptions  
  \item Aggressively summarize history to 1-sentence-per-turn  
  \item Reduce memory slots  
  \item If still over: truncate with warning to user  
\end{itemize}  

\begin{itemize}
  \item 丢弃最不重要的工具描述  
  \item 激进地将历史摘要为每轮一句话  
  \item 减少记忆槽位  
  \item 如果仍然超出：截断并向用户发出警告  
\end{itemize}  

\textbf{Pre-flight check}: Always count tokens BEFORE calling the LLM. Never discover overflow at inference time.  

\textbf{预检检查}：在调用 LLM 之前始终计算令牌数量。绝不要在推理时才发现溢出。  

\emph{\textbf{Review:} Chapter~17 (Agent Harness -- Context Management and Orchestration).}  
\emph{\textbf{复习：} 第 17 章（智能体框架——上下文管理与编排）。}  
\end{questionbox}  

\begin{questionbox}[Q: Compare ReAct vs Plan-and-Execute orchestration patterns]  
\textbf{Answer}:  

\textbf{答案}：  

\textbf{ReAct} (Reason + Act):  

\textbf{ReAct}（推理 + 行动）：  

\begin{itemize}
  \item Loop: Thought $\to$ Action $\to$ Observation $\to$ Thought $\to$ \ldots{}  
  \item Each step decides the next action based on all previous observations  
  \item \textbf{Pro}: Adaptive --- can change direction based on tool outputs  
  \item \textbf{Con}: Myopic --- no upfront planning; can get stuck in loops; each LLM call sees entire history (expensive)  
\end{itemize}  

\begin{itemize}
  \item 循环：思考 $\to$ 行动 $\to$ 观察 $\to$ 思考 $\to$ \ldots{}  
  \item 每一步根据之前的所有观察决定下一步行动  
  \item \textbf{优点}：自适应——可根据工具输出调整方向  
  \item \textbf{缺点}：短视——没有预先规划；可能陷入循环；每次 LLM 调用都需查看整个历史（成本高）  
\end{itemize}  

\textbf{Plan-and-Execute}:  

\textbf{计划与执行}：  

\begin{itemize}
  \item Phase 1: Generate full plan (list of steps)  
  \item Phase 2: Execute steps sequentially (simpler executor; possibly cheaper model)  
  \item Phase 3: Re-plan if execution fails  
  \item \textbf{Pro}: Efficient (planning once is cheaper than reasoning every step); parallelizable independent steps  
  \item \textbf{Con}: Brittle plans --- if early steps fail the plan may be invalid. Re-planning adds latency.  
\end{itemize}  

\begin{itemize}
  \item 阶段 1：生成完整计划（步骤列表）  
  \item 阶段 2：按顺序执行步骤（执行器更简单；可能使用更便宜的模型）  
  \item 阶段 3：如果执行失败则重新计划  
  \item \textbf{优点}：高效（一次规划比每步推理更便宜）；独立步骤可并行化  
  \item \textbf{缺点}：计划脆弱——如果早期步骤失败，计划可能无效。重新计划会增加延迟。  
\end{itemize}  

\textbf{When to use which}:  

\textbf{何时使用哪种模式}：  

\begin{itemize}
  \item ReAct: Exploratory tasks; unknown environments; tasks where each step’s result determines the next  
  \item Plan-and-Execute: Well-defined tasks; known tool set; parallelizable sub-tasks; cost-sensitive deployments  
  \item \textbf{Hybrid}: Plan at high level then ReAct within each plan step (LangGraph’s recommended pattern)  
\end{itemize}  

\begin{itemize}
  \item ReAct：探索性任务；未知环境；每一步结果决定下一步的任务  
  \item 计划与执行：定义明确的任务；已知工具集；可并行化的子任务；对成本敏感的部署  
  \item \textbf{混合模式}：高层计划，然后在每个计划步骤内使用 ReAct（LangGraph 推荐模式）  
\end{itemize}  

\emph{\textbf{Review:} Chapters~17 and~18 (Agent Harness; Agent Design Patterns).}  
\emph{\textbf{复习：} 第 17 章和第 18 章（智能体框架；智能体设计模式）。}  
\end{questionbox}  

\begin{questionbox}[Q: How do you detect and prevent infinite loops in agent execution?]  
\textbf{Answer}: Agents can enter infinite loops when they repeat the same action expecting different results.  

\textbf{答案}：智能体在重复相同行动却期望不同结果时，可能陷入无限循环。  

\textbf{Detection methods}:  

\textbf{检测方法}：  

\begin{enumerate}
  \item \textbf{Max iteration guard}: Hard limit (e.g., 25 steps). Simple but loses work on genuinely long tasks.  
  \item \textbf{Action hash window}: Hash the last $k$ (action/observation) pairs. If current hash matches a hash from the last $w$ steps then loop detected.  
  \item \textbf{Semantic similarity}: Embed recent actions. If cosine similarity between consecutive actions exceeds threshold ($>$0.95) then likely stuck.  
  \item \textbf{Progress monitoring}: Define task-specific progress metrics. If no progress in $N$ steps then intervene.  
\end{enumerate}  

\begin{enumerate}
  \item \textbf{最大迭代防护}：硬限制（例如 25 步）。简单但会丢失真正长任务中的工作。  
  \item \textbf{动作哈希窗口}：对最近 $k$ 个（动作/观察）对进行哈希。如果当前哈希与最近 $w$ 步中的某个哈希匹配，则检测到循环。  
  \item \textbf{语义相似度}：嵌入最近的行动。如果连续行动间的余弦相似度超过阈值（$>$0.95），则可能陷入停滞。  
  \item \textbf{进度监控}：定义特定任务的进度指标。如果在 $N$ 步内无进展，则进行干预。  
\end{enumerate}  

\textbf{Recovery strategies}:  

\textbf{恢复策略}：  

\begin{enumerate}
  \item \textbf{Inject hint}: Add system message: ``You seem to be repeating actions. Try a different approach.''  
  \item \textbf{Force different action}: Mask the repeated action from the action space for the next step.  
  \item \textbf{Escalate}: Return to user with partial results and ask for guidance.  
  \item \textbf{Backtrack}: Reset to a checkpoint before the loop began and try alternative path.  
\end{enumerate}  

\begin{enumerate}
  \item \textbf{注入提示}：添加系统消息：“你似乎在重复行动。请尝试不同的方法。”  
  \item \textbf{强制不同行动}：在下一步中屏蔽重复的动作，使其不可用。  
  \item \textbf{升级处理}：向用户返回部分结果并请求指导。  
  \item \textbf{回溯}：重置到循环开始前的检查点，尝试替代路径。  
\end{enumerate}  

\textbf{Best practice}: Combine max iterations (safety net) + hash-based detection (early intervention) + graceful escalation (preserve user trust).  

\textbf{最佳实践}：结合最大迭代次数（安全网）+ 基于哈希的检测（早期干预）+ 优雅的升级处理（维护用户信任）。  

\emph{\textbf{Review:} Chapters~17 and~18 (Agent Harness; Agent Design Patterns).}  
\emph{\textbf{复习：} 第 17 章和第 18 章（智能体框架；智能体设计模式）。}  
\end{questionbox}  

\newpage  
## MCP Protocol Questions  
## MCP 协议问题  

\begin{questionbox}[Q: Explain MCP’s N+M architecture and why it matters for the agent ecosystem]  
\textbf{Answer}: \textbf{The N$\times$M problem}: Without MCP, $N$ agent frameworks must each implement integrations with $M$ tools = $N \times M$ total integrations. Adding one new tool requires $N$ implementations.  

\textbf{答案}：\textbf{N $\times$ M 问题}：没有 MCP 时，$N$ 个智能体框架每个都需要实现与 $M$ 个工具的集成，总集成数为 $N \times M$。添加一个新工具需要 $N$ 个实现。  

\textbf{MCP’s N+M solution}: Standardize the interface. Each agent implements one MCP client ($N$ total). Each tool implements one MCP server ($M$ total). Total integrations = $N + M$.  

\textbf{MCP 的 N+M 解决方案}：标准化接口。每个智能体实现一个 MCP 客户端（共 $N$ 个）。每个工具实现一个 MCP 服务器（共 $M$ 个）。总集成数 = $N + M$。  

\textbf{Concrete example}: 5 agent frameworks (LangChain/AutoGen/CrewAI/Claude/custom) $\times$ 20 tools (GitHub/Slack/DB/filesystem/\ldots{}) = 100 integrations without MCP. With MCP: 5 clients + 20 servers = 25 implementations.  

\textbf{具体示例}：5 个智能体框架（LangChain/AutoGen/CrewAI/Claude/自定义）$\times$ 20 个工具（GitHub/Slack/数据库/文件系统/\ldots{}） = 无 MCP 时 100 个集成。使用 MCP：5 个客户端 + 20 个服务器 = 25 个实现。  

\textbf{Why it matters}:  

\textbf{为何重要}：  

\begin{enumerate}
  \item \textbf{Tool reuse}: Build a tool server once; use from any MCP-compatible agent  
  \item \textbf{Agent portability}: Switch from Claude to a custom agent without rewriting tool integrations  
  \item \textbf{Ecosystem growth}: Lower barrier to adding new tools incentivizes the community to build more  
  \item \textbf{Composability}: Connect multiple servers to one agent dynamically at runtime  
\end{enumerate}  

\begin{enumerate}
  \item \textbf{工具复用}：构建一次工具服务器；可从任何兼容 MCP 的智能体使用  
  \item \textbf{智能体可移植性}：从 Claude 切换到自定义智能体时无需重写工具集成  
  \item \textbf{生态增长}：降低添加新工具的障碍，激励社区构建更多工具  
  \item \textbf{可组合性}：运行时动态将多个服务器连接到一个智能体  
\end{enumerate}  

\textbf{Analogy}: USB standardized peripheral connections. Before USB: every device had a proprietary connector. After USB: one port fits all. MCP does the same for agent-tool connections.  

\textbf{类比}：USB 标准化了外设连接。USB 之前：每个设备都有专有连接器。USB 之后：一个端口通用。MCP 对智能体-工具连接做了同样的事。  

\emph{\textbf{Review:} Chapter~20 (Model Context Protocol).}  
\emph{\textbf{复习：} 第 20 章（模型上下文协议）。}  
\end{questionbox}  

\begin{questionbox}[Q: What are MCP’s four core primitives and when do you use each?]  
\textbf{Answer}:  

\textbf{答案}：  

\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{Primitive} & \textbf{Direction} & \textbf{Purpose} & \textbf{Example} \\
\cmidrule
Tools & Client $\to$ Server & Execute actions & \texttt{create\_issue}; \texttt{query\_db} \\
Resources & Client $\to$ Server & Read data & File contents; DB records \\
Prompts & Client $\to$ Server & Get templates & ``Summarize this PR'' template \\
Sampling & Server $\to$ Client & Request LLM gen & Server asks LLM to classify \\
\bottomrule
\end{tabular}  

\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{基本元素} & \textbf{方向} & \textbf{目的} & \textbf{示例} \\
\cmidrule
工具 & 客户端 $\to$ 服务器 & 执行动作 & \texttt{create\_issue}; \texttt{query\_db} \\
资源 & 客户端 $\to$ 服务器 & 读取数据 & 文件内容；数据库记录 \\
提示词 & 客户端 $\to$ 服务器 & 获取模板 & “总结此 PR” 模板 \\
采样 & 服务器 $\to$ 客户端 & 请求 LLM 生成 & 服务器请求 LLM 进行分类 \\
\bottomrule
\end{tabular}  

\textbf{Key distinctions}:  

\textbf{关键区别}：  

\begin{itemize}
  \item \textbf{Tools vs Resources}: Tools have \emph{side effects} (create/modify/delete). Resources are \emph{read-only}. This distinction matters for safety --- an agent can freely read resources but must get approval for tools.  
  \item \textbf{Sampling} reverses the direction: normally the client (agent) calls the server (tool). With Sampling the server asks the client’s LLM for help. Use case: a code analysis server needs the LLM to interpret a code snippet.  
  \item \textbf{Prompts} are metadata (reusable templates) not execution. They help the agent formulate better tool calls.  
\end{itemize}  

\begin{itemize}
  \item \textbf{工具与资源}：工具有\emph{副作用}（创建/修改/删除）。资源是\emph{只读的}。这一区别关乎安全——智能体可以自由读取资源，但使用工具必须获得批准。  
  \item \textbf{采样} 反转了方向：通常客户端（智能体）调用服务器（工具）。使用采样时，服务器请求客户端的 LLM 提供帮助。用例：代码分析服务器需要 LLM 解释代码片段。  
  \item \textbf{提示词} 是元数据（可复用的模板），而非执行。它们帮助智能体制定更好的工具调用。  
\end{itemize}  

\emph{\textbf{Review:} Chapter~20 (Model Context Protocol).}  
\emph{\textbf{复习：} 第 20 章（模型上下文协议）。}  
\end{questionbox}

## Agent Communication (A2A) Questions
## 智能体通信（A2A）问题

\label{agent-communication-a2a-questions}

\begin{questionbox}[Q: How does Google’s A2A protocol differ from MCP and when do you need both?]
\textbf{Answer}: \textbf{Core distinction}:
\begin{itemize}
  \item \textbf{MCP}: Agent $\leftrightarrow$ Tool (structured function calls with defined schemas)
  \item \textbf{A2A}: Agent $\leftrightarrow$ Agent (opaque task delegation --- you don’t know how the other agent works)
\end{itemize}
\textbf{Key A2A concepts}:
\begin{itemize}
  \item \textbf{Agent Cards}: JSON describing what an agent can do (like a resume). Discovery mechanism.
  \item \textbf{Opaque execution}: Requester doesn’t see internal reasoning of the delegate. Just sends task and gets result.
  \item \textbf{Task lifecycle}: submitted $\to$ working $\to$ completed/failed (with streaming updates via SSE)
\end{itemize}
\textbf{When you need both}:
\begin{enumerate}
  \item An orchestrator agent uses \textbf{A2A} to delegate ``research this topic'' to a research agent
  \item The research agent uses \textbf{MCP} to call web search and file read and database tools
  \item Results flow back via A2A to the orchestrator
\end{enumerate}
\textbf{Architecture}: A2A sits at the \emph{inter-agent} layer; MCP sits at the \emph{agent-tool} layer. A complete system uses both: A2A for coordination between agents and MCP for each agent’s tool access.
\emph{\textbf{Review:} Chapters~20 and~22 (MCP; Agent-to-Agent Communication).}
\end{questionbox}

\begin{questionbox}[Q: What is the Contract Net Protocol and how does it apply to LLM agents?]
\textbf{Answer}: The \textbf{Contract Net Protocol} (CNP) is a task allocation mechanism from distributed AI:
\textbf{Steps}:
\begin{enumerate}
  \item \textbf{Announce}: Manager broadcasts task description to all available agents
  \item \textbf{Bid}: Agents assess their capability and submit bids (confidence; estimated cost; estimated time)
  \item \textbf{Award}: Manager selects best bid(s) based on criteria (capability/cost/availability)
  \item \textbf{Execute}: Winning agent(s) perform the task
  \item \textbf{Report}: Agent reports results back to manager
\end{enumerate}
\textbf{For LLM agents}:
\begin{itemize}
  \item \textbf{Bidding = self-assessment}: Each agent LLM evaluates ``can I do this task well?'' and provides a confidence score. This requires calibrated self-knowledge.
  \item \textbf{Specialization emerges}: Code agents bid high on code tasks; research agents bid high on research tasks. No central routing logic needed.
  \item \textbf{Load balancing}: If one agent is busy (high estimated time) others win the contract.
  \item \textbf{Failure handling}: If awarded agent fails then re-announce to remaining agents (automatic failover).
\end{itemize}
\textbf{Limitation for LLMs}: LLMs often overestimate their capabilities (hallucinate confidence). Bids should incorporate track record (historical success rate on similar tasks) not just self-reported confidence.
\emph{\textbf{Review:} Chapters~22 and~23 (A2A; Multi-Agent Systems).}
\end{questionbox}

\section{Multi-Agent Systems Questions}
\section{多智能体系统问题}
\label{multi-agent-systems-questions}

\begin{questionbox}[Q: Compare centralized vs decentralized multi-agent architectures for LLMs]
\textbf{Answer}:
\textbf{Centralized (Supervisor)}:
\begin{itemize}
  \item One orchestrator LLM routes tasks to specialist workers
  \item Clear control flow; easy to debug (inspect supervisor decisions)
  \item Single point of failure; supervisor becomes token bottleneck
  \item Best for: well-defined workflows; small agent teams (3--5 agents)
\end{itemize}
\textbf{Decentralized (Peer-to-Peer)}:
\begin{itemize}
  \item Agents communicate directly; no central coordinator
  \item Resilient (no single point of failure); scales horizontally
  \item Hard to debug (emergent behavior); potential for conflicts and deadlocks
  \item Communication scales $O(n^2)$ without structure
  \item Best for: resilient systems; large agent populations; creative tasks where emergent behavior is desired
\end{itemize}
\textbf{Hybrid (Hierarchical)}: Tree structure with sub-managers. Combines benefits: local autonomy within groups and global coordination at the top. Communication scales $O(n \log n)$.
\textbf{Decision framework}: Use centralized if you need predictability and auditability. Use decentralized if you need resilience and creativity. Use hierarchical for large ($>$10 agent) systems.
\emph{\textbf{Review:} Chapter~23 (Multi-Agent Systems).}
\end{questionbox}

\begin{questionbox}[Q: What is CTDE and why is it important for training multi-agent LLM systems?]
\textbf{Answer}: \textbf{CTDE} = Centralized Training; Decentralized Execution.
\textbf{The problem}: In multi-agent RL each agent’s environment is non-stationary (other agents are changing their policies simultaneously). This makes independent training unstable.
\textbf{CTDE solution}:
\begin{itemize}
  \item \textbf{During training}: A centralized critic has access to all agents’ observations and actions: $V(s_1, s_2, \ldots, s_n, a_1, a_2, \ldots, a_n)$. This stabilizes training by removing non-stationarity from the value function.
  \item \textbf{During execution}: Each agent acts based only on its own observation: $a_i = \pi_i(o_i)$. No communication overhead at inference time.
\end{itemize}
\textbf{For LLM agents}: The centralized critic can be a reward model that evaluates the \emph{joint} output of all agents (e.g., did the team of agents produce a correct software system?) while each agent is trained to maximize its contribution to the team reward using counterfactual credit assignment.
\textbf{Practical challenge}: Full CTDE requires all agents to train simultaneously with shared state --- expensive for LLMs. Approximations: train agents in rounds (freeze others and train one) or use population-based training with periodic synchronization.
\emph{\textbf{Review:} Chapter~23 (Multi-Agent Systems).}
\end{questionbox}

\section{Agent Development Framework Questions}
\section{智能体开发框架问题}
\label{agent-development-framework-questions}

\begin{questionbox}[Q: Compare LangGraph vs AutoGen vs CrewAI for building multi-agent systems]
\textbf{Answer}:
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Dimension} & \textbf{LangGraph} & \textbf{AutoGen / CrewAI} \\
\midrule
Orchestration & Explicit state graph (nodes + edges) & Implicit (conversation / role-based) \\
State mgmt & TypedDict schemas; checkpointing & Conversation history as state \\
Multi-agent & Graph with conditional routing & GroupChat / Crew \\
Debugging & Graph visualization; step replay & Chat logs \\
HITL & First-class (interrupt nodes) & Via approval tools \\
Production & LangGraph Cloud; persistence & Limited (AutoGen); growing (CrewAI) \\
Learning curve & High (graph concepts) & Low (AutoGen); Very low (CrewAI) \\
\bottomrule
\end{tabular}
\textbf{Choose LangGraph when}: You need fine-grained control; complex conditional flows; production deployment with persistence and human-in-the-loop.
\textbf{Choose AutoGen when}: Rapid prototyping of multi-agent conversations; code execution agents; research experimentation.
\textbf{Choose CrewAI when}: Simple role-based teams; sequential task execution; quick demos; minimal code.
\textbf{Choose none (custom) when}: You need maximum performance/control; don’t want framework lock-in; or have non-standard orchestration patterns.
\emph{\textbf{Review:} Chapter~24 (Agent Development Frameworks).}
\end{questionbox}

\begin{questionbox}[Q: How do you test and evaluate an agent system in production?]
\textbf{Answer}: Agent testing follows a \textbf{testing pyramid}:
\textbf{Level 1 --- Unit Tests} (fast; many):

\begin{itemize}
  \item Test individual tools in isolation (mock LLM; verify tool logic)
  \item 单独测试各个工具（模拟 LLM；验证工具逻辑）
  \item Test prompt templates (given context; verify correct prompt construction)
  \item 测试提示模板（给定上下文；验证提示是否正确构建）
  \item Test parsers (given LLM output; verify correct extraction)
  \item 测试解析器（给定 LLM 输出；验证是否正确提取）
\end{itemize}

\textbf{Level 2 --- Integration Tests} (medium speed):
\textbf{第 2 级——集成测试}（中等速度）：

\begin{itemize}
  \item Test complete agent loops with deterministic inputs
  \item 使用确定性输入测试完整的 Agent 循环
  \item ``Golden trajectory'' tests: known-good execution traces that must reproduce
  \item “黄金轨迹”测试：必须能够复现的已知正确执行轨迹
  \item Tool chain tests: verify multi-tool sequences work end-to-end
  \item 工具链测试：验证多工具序列的端到端工作
\end{itemize}

\textbf{Level 3 --- Behavioral Tests} (slow; few):
\textbf{第 3 级——行为测试}（慢速；少量）：

\begin{itemize}
  \item Does the agent follow safety constraints? (adversarial inputs)
  \item Agent 是否遵守安全约束？（对抗性输入）
  \item Does it ask for clarification when appropriate?
  \item 它在适当的时候是否请求澄清？
  \item Does it stay within token/cost budgets?
  \item 它是否保持在 Token/成本预算内？
\end{itemize}

\textbf{Production evaluation}:
\textbf{生产评估}：

\begin{itemize}
  \item \textbf{A/B testing}: Route 5\% of traffic to new agent version
  \item \textbf{A/B 测试}：将 5\% 流量路由到新 Agent 版本
  \item \textbf{Shadow mode}: Run new agent alongside old; compare outputs without serving
  \item \textbf{影子模式}：新 Agent 与旧 Agent 并行运行；比较输出但不对外服务
  \item \textbf{LLM-as-judge}: Automated quality scoring of agent responses
  \item \textbf{LLM 作为裁判}：对 Agent 响应进行自动质量评分
  \item \textbf{User satisfaction}: Thumbs up/down; task completion rate; time-to-resolution
  \item \textbf{用户满意度}：点赞/点踩；任务完成率；解决时间
\end{itemize}

\textbf{Key metric}: \textbf{Task Success Rate} (TSR) --- fraction of tasks the agent completes correctly without human intervention.
\textbf{关键指标}：\textbf{任务成功率}（TSR）——Agent 无需人工干预而正确完成的任务比例。

\emph{\textbf{Review:} Chapters~14 and~24 (LLM Evaluation; Agent Development Frameworks).}
\emph{\textbf{回顾：}第 14 章和第 24 章（LLM 评估；Agent 开发框架）。}
\end{questionbox}

\section{Agentic Environments Questions}
\section{Agentic Environments（智能体环境）问题}
\label{agentic-environments-questions}

\begin{questionbox}[Q: Design a reward function for a web browsing agent environment]
\questionbox[Q: 为网页浏览 Agent 环境设计奖励函数]

\textbf{Answer}: For WebArena-style tasks (e.g., ``find the cheapest flight from NYC to SF on Dec 15''):
\textbf{回答}：对于 WebArena 风格的任务（例如“找到 12 月 15 日从纽约到旧金山最便宜的航班”）：

\textbf{Sparse reward} (simple but hard to learn from): 
\textbf{稀疏奖励}（简单但难以从中学习）：
\[
r = \begin{cases} 1 & \text{if final page/state matches ground truth} \\ 0 & \text{otherwise} \end{cases}
\]

\textbf{Dense reward} (better for training; harder to design):
\textbf{密集奖励}（更适合训练；更难设计）：

\begin{enumerate}
  \item \textbf{Progress reward}: $+0.1$ for each page that brings agent closer to goal (measured by text similarity to target state)
  \item \textbf{进度奖励}：每使 Agent 更接近目标（通过文本相似度与目标状态衡量）的页面给予 $+0.1$
  \item \textbf{Efficiency penalty}: $-0.01$ per action (encourages shorter trajectories)
  \item \textbf{效率惩罚}：每个动作 $-0.01$（鼓励更短的轨迹）
  \item \textbf{Milestone rewards}: $+0.3$ for reaching intermediate goals (e.g., navigating to flight search page)
  \item \textbf{里程碑奖励}：达到中间目标（例如导航到航班搜索页面）给予 $+0.3$
  \item \textbf{Invalid action penalty}: $-0.05$ for actions that produce errors (404; form validation failures)
  \item \textbf{无效动作惩罚}：对产生错误（404；表单验证失败）的动作给予 $-0.05$
\end{enumerate}

\textbf{Potential-based shaping} (preserves optimal policy): 
\textbf{基于势能的塑形}（保持最优策略）：
\[
r_{\text{shaped}}(s, a, s') = r(s, a, s') + \gamma \Phi(s') - \Phi(s)
\]
 where $\Phi(s) = -\text{min\_steps\_to\_goal}(s)$ (estimated by heuristic or learned value function).
其中 $\Phi(s) = -\text{min\_steps\_to\_goal}(s)$（通过启发式或学习到的价值函数估计）。

\textbf{Challenges}: Partial observability (can’t always tell if you’re closer to goal); stochastic environments (page content changes); reward hacking (agent finds shortcuts that satisfy reward but not user intent).
\textbf{挑战}：部分可观测性（无法始终判断是否更接近目标）；随机环境（页面内容变化）；奖励篡改（Agent 找到满足奖励但不符合用户意图的捷径）。

\emph{\textbf{Review:} Chapters~12 and~19 (LLM Agentic Training; Agentic Environments).}
\emph{\textbf{回顾：}第 12 章和第 19 章（LLM 智能体训练；智能体环境）。}
\end{questionbox}

\begin{questionbox}[Q: What makes SWE-bench a particularly challenging agent benchmark?]
\questionbox[Q: 是什么让 SWE-bench 成为一个特别具有挑战性的 Agent 基准？]

\textbf{Answer}: SWE-bench tests agents on real GitHub issues from popular Python repositories:
\textbf{回答}：SWE-bench 在流行的 Python 仓库的真实 GitHub issue 上测试 Agent：

\textbf{Why it’s hard}:
\textbf{为什么难}：

\begin{enumerate}
  \item \textbf{Repository-scale context}: Agent must understand codebases with 100K+ lines. Cannot fit in context window --- must explore and search and navigate.
  \item \textbf{仓库级上下文}：Agent 必须理解拥有 10 万行以上代码的代码库。无法放入上下文窗口——必须探索、搜索和导航。
  \item \textbf{Underspecified tasks}: Issues are written by humans with implicit context. Agent must infer what’s actually needed.
  \item \textbf{任务说明不足}：Issue 由人类编写，包含隐式上下文。Agent 必须推断实际需求。
  \item \textbf{Multi-file edits}: Solutions often span multiple files with cascading dependencies.
  \item \textbf{多文件编辑}：解决方案通常跨多个文件，存在级联依赖。
  \item \textbf{Test verification}: Must pass existing tests AND new tests that verify the fix.
  \item \textbf{测试验证}：必须通过现有测试以及验证修复的新测试。
  \item \textbf{No hand-holding}: Unlike HumanEval (single function) SWE-bench requires full software engineering workflow: read issue $\to$ explore code $\to$ localize bug $\to$ implement fix $\to$ verify.
  \item \textbf{无手把手指导}：与 HumanEval（单个函数）不同，SWE-bench 需要完整的软件工程工作流：阅读 issue $\to$ 探索代码 $\to$ 定位 bug $\to$ 实现修复 $\to$ 验证。
\end{enumerate}

\textbf{State of the art} (2024--2025): Best agents solve $\sim$50\% of SWE-bench Verified (curated subset). Full SWE-bench: $\sim$30\%.
\textbf{当前最优水平}（2024--2025）：最佳 Agent 能解决约 50\% 的 SWE-bench Verified（精选子集）。完整 SWE-bench：约 30\%。

\textbf{Key insight for training}: SWE-bench exposes the gap between ``coding ability'' (writing correct functions) and ``software engineering ability'' (understanding systems; navigating codebases; making minimal changes). RL training on SWE-bench-style environments teaches agents exploration and planning strategies not just code generation.
\textbf{训练的关键见解}：SWE-bench 揭示了“编码能力”（编写正确函数）与“软件工程能力”（理解系统、导航代码库、做最小改动）之间的差距。在 SWE-bench 风格的环境中进行强化学习训练，教会 Agent 探索和规划策略，而不仅仅是代码生成。

\emph{\textbf{Review:} Chapter~19 (Agentic Environments and Benchmarks).}
\emph{\textbf{回顾：}第 19 章（智能体环境与基准）。}
\end{questionbox}

\section{Agentic UI Framework Questions}
\section{Agentic UI 框架问题}
\label{agentic-ui-framework-questions}

\begin{questionbox}[Q: Compare chat-based vs canvas-based UI paradigms for agents]
\questionbox[Q: 比较基于聊天与基于画布的 Agent UI 范式]

\textbf{Answer}:
\textbf{回答}：

\textbf{Chat-based} (ChatGPT; Claude default):
\textbf{基于聊天}（ChatGPT；Claude 默认）：

\begin{itemize}
  \item Linear message stream: user $\to$ assistant $\to$ user $\to$ \ldots{}
  \item 线性消息流：用户 $\to$ 助手 $\to$ 用户 $\to$ \ldots{}
  \item \textbf{Pro}: Familiar UX; natural for exploration and Q\&A; easy to implement
  \item \textbf{优点}：熟悉的用户体验；适合探索和问答；易于实现
  \item \textbf{Con}: Generated artifacts (code/documents) are buried in conversation. Hard to iterate on a specific artifact. Context gets lost in long conversations.
  \item \textbf{缺点}：生成的工件（代码/文档）埋没在对话中。难以针对特定工件进行迭代。长对话中上下文丢失。
\end{itemize}

\textbf{Canvas/Artifact-based} (Claude Artifacts; ChatGPT Canvas; Cursor):
\textbf{基于画布/工件}（Claude Artifacts；ChatGPT Canvas；Cursor）：

\begin{itemize}
  \item Side panel displays generated content; chat panel for instructions
  \item 侧面板显示生成的内容；聊天面板用于指令
  \item Agent can create and edit and iterate on persistent artifacts
  \item Agent 可以创建、编辑和迭代持久化工件
  \item \textbf{Pro}: Artifacts persist independently of chat. Direct editing by user. Version history.
  \item \textbf{优点}：工件独立于聊天持久化。用户可直接编辑。支持版本历史。
  \item \textbf{Con}: More complex UI; requires artifact type detection; harder to implement streaming to both panels.
  \item \textbf{缺点}：UI 更复杂；需要工件类型检测；更难实现向两个面板同时流式传输。
\end{itemize}

\textbf{When to use which}:
\textbf{何时使用哪种}：

\begin{itemize}
  \item Chat: brainstorming; Q\&A; quick tasks; mobile interfaces
  \item 聊天：头脑风暴；问答；快速任务；移动界面
  \item Canvas: code generation; document writing; data analysis --- any task with persistent output that needs iteration
  \item 画布：代码生成；文档编写；数据分析——任何需要持久化输出并迭代的任务
  \item \textbf{Hybrid} (most modern UIs): Chat by default; auto-elevate to canvas when detecting code/document/visualization output
  \item \textbf{混合模式}（大多数现代 UI）：默认聊天；检测到代码/文档/可视化输出时自动提升为画布
\end{itemize}

\textbf{For agent training}: The UI paradigm affects the reward signal. Canvas UIs provide explicit edit feedback (user modifies the artifact) which can be used for online learning.
\textbf{对于 Agent 训练}：UI 范式影响奖励信号。画布 UI 提供明确的编辑反馈（用户修改工件），可用于在线学习。

\emph{\textbf{Review:} Chapter~25 (Agentic UI Frameworks).}
\emph{\textbf{回顾：}第 25 章（智能体 UI 框架）。}
\end{questionbox}

\begin{questionbox}[Q: How do you design approval gates for human-in-the-loop agent systems?]
\questionbox[Q: 如何为人在环 Agent 系统设计审批关卡？]

\textbf{Answer}: Approval gates pause agent execution at critical points for human review.
\textbf{回答}：审批关卡在关键点暂停 Agent 执行，等待人工审核。

\textbf{Three-tier model}:
\textbf{三层模型}：

\begin{enumerate}
  \item \textbf{Auto-approve} (no gate): Safe reversible actions. Read operations; searches; calculations.
  \item \textbf{自动批准}（无关卡）：安全的可逆操作。读取操作；搜索；计算。
  \item \textbf{Notify} (soft gate): Potentially impactful but recoverable. Send email; create draft; modify file. Agent proceeds but user is notified and can undo.
  \item \textbf{通知}（软关卡）：可能有影响但可恢复。发送邮件；创建草稿；修改文件。Agent 继续执行，但用户收到通知并可撤销。
  \item \textbf{Block} (hard gate): Irreversible or high-stakes. Delete data; send money; publish content; execute code with side effects. Agent MUST wait for explicit approval.
  \item \textbf{阻止}（硬关卡）：不可逆或高风险。删除数据；转账；发布内容；执行有副作用的代码。Agent 必须等待明确批准。
\end{enumerate}

\textbf{Design principles}:
\textbf{设计原则}：

\begin{itemize}
  \item \textbf{Minimize interruptions}: Too many gates = user abandons the agent. The 3-tier model lets most actions flow while catching dangerous ones.
  \item \textbf{最小化中断}：关卡过多 = 用户放弃 Agent。三层模型允许大多数动作流畅执行，同时拦截危险动作。
  \item \textbf{Show context}: At approval gate display: what action; why (agent’s reasoning); what will change; how to undo.
  \item \textbf{展示上下文}：在审批关卡显示：什么动作；为什么（Agent 的推理）；会有什么变化；如何撤销。
  \item \textbf{Batch approvals}: If agent needs 5 file writes present them together not one by one.
  \item \textbf{批量审批}：如果 Agent 需要写 5 个文件，一起呈现，而不是逐个呈现。
  \item \textbf{Timeout handling}: If user doesn’t respond within $T$ minutes either retry notification or proceed with safe default or abort gracefully.
  \item \textbf{超时处理}：如果用户在 $T$ 分钟内未响应，则重试通知，或按安全默认执行，或优雅终止。
  \item \textbf{Learning from approvals}: Track approval/rejection patterns. If users always approve a certain action type consider auto-promoting it.
  \item \textbf{从审批中学习}：跟踪批准/拒绝模式。如果用户总是批准某种动作类型，考虑自动提升其权限。
\end{itemize}

\textbf{Implementation}: Tool annotations (MCP’s \texttt{destructiveHint} and \texttt{readOnlyHint}) drive automatic gate assignment. Custom rules can override based on context.
\textbf{实现}：工具注解（MCP 的 \texttt{destructiveHint} 和 \texttt{readOnlyHint}）驱动自动关卡分配。自定义规则可根据上下文覆盖。

```markdown
\emph{\textbf{Review:} Chapters~17 and~25 (Agent Harness; Agentic UI Frameworks).}
\emph{\textbf{回顾：} 第 17 章和第 25 章（Agent Harness；Agentic UI Frameworks）。}
\end{questionbox}

\section{RAG and Agentic RAG Questions}
\section{RAG 与 Agentic RAG 问题}
\label{rag-and-agentic-rag-questions}

\begin{questionbox}[Q: Explain Reciprocal Rank Fusion (RRF) and why it works for hybrid retrieval]
**Answer**: RRF combines rankings from multiple retrieval systems without needing score calibration: 
\[
\text{RRF}(d) = \sum_{r \in R} \frac{1}{k + r(d)}
\]
 where $r(d)$ is the rank of document $d$ in retriever $r$, and $k=60$ is a constant that prevents high-ranked documents from dominating.

**答案**：RRF 在不需分数校准的情况下，将多个检索系统的排名进行融合：
\[
\text{RRF}(d) = \sum_{r \in R} \frac{1}{k + r(d)}
\]
其中 $r(d)$ 是文档 $d$ 在检索器 $r$ 中的排名，$k=60$ 是一个常数，用于防止排名靠前的文档占据主导地位。

**Why it works**:

**为何有效**：

\begin{enumerate}
  \item \textbf{No score normalization needed}: BM25 scores are unbounded; dense similarity is in $[-1, 1]$. RRF uses only ranks, making them directly comparable.
  \item \textbf{Robust to outliers}: A single retriever giving anomalously high scores doesn’t dominate because $1/(k+1) \approx 0.016$ even for rank 1.
  \item \textbf{Complementary signals}: BM25 catches exact keyword matches; dense retrieval catches semantic similarity. Documents ranked highly by both get boosted.
\end{enumerate}

\begin{enumerate}
  \item \textbf{无需分数归一化}：BM25 的分数无界；密集相似度在 $[-1, 1]$ 范围内。RRF 仅使用排名，使它们可以直接比较。
  \item \textbf{对异常值鲁棒}：单个检索器给出异常高分不会占据主导，因为即使排名为 1，$1/(k+1) \approx 0.016$。
  \item \textbf{互补信号}：BM25 捕捉精确的关键词匹配；密集检索捕捉语义相似性。在两个检索器中都排名靠前的文档会得到提升。
\end{enumerate}

\textbf{Example}: Document $d$ is rank 3 in BM25 and rank 7 in dense. RRF score $= 1/(60+3) + 1/(60+7) = 0.0159 + 0.0149 = 0.0308$. A document at rank 1 in one but rank 100 in the other gets $1/61 + 1/160 = 0.0226$ --- lower despite having a top-1 ranking.

\textbf{示例}：文档 $d$ 在 BM25 中排名第 3，在密集检索中排名第 7。RRF 得分 $= 1/(60+3) + 1/(60+7) = 0.0159 + 0.0149 = 0.0308$。一个在一个检索器中排名第 1、但在另一个中排名第 100 的文档得分为 $1/61 + 1/160 = 0.0226$ —— 尽管有一个最高排名，但得分更低。

\textbf{In practice}: Hybrid (BM25 + dense + RRF) outperforms either alone on 85\%+ of benchmarks.

\textbf{在实践中}：混合检索（BM25 + 密集检索 + RRF）在 85% 以上的基准测试中优于单独使用任何一种检索方式。

\emph{\textbf{Review:} Chapter~15 (Retrieval-Augmented Generation).}
\emph{\textbf{回顾：} 第 15 章（检索增强生成）。}
\end{questionbox}

\begin{questionbox}[Q: What is Agentic RAG and how does it differ from standard RAG?]
**Answer**: \textbf{Standard RAG} follows a fixed pipeline: query $\to$ retrieve $\to$ generate. It has no ability to:

**答案**：\textbf{标准 RAG} 遵循固定的流水线：查询 $\to$ 检索 $\to$ 生成。它不具备以下能力：

\begin{itemize}
  \item Decide whether retrieval is needed at all
  \item Evaluate if retrieved documents are sufficient
  \item Reformulate queries when retrieval fails
  \item Combine information from multiple retrieval steps
\end{itemize}

\begin{itemize}
  \item 判断是否需要进行检索
  \item 评估检索到的文档是否足够
  \item 在检索失败时重新表述查询
  \item 合并来自多个检索步骤的信息
\end{itemize}

\textbf{Agentic RAG} treats retrieval as an \emph{action} in the agent’s MDP:

\textbf{Agentic RAG} 将检索视为智能体 MDP 中的一个\emph{动作}：

\begin{itemize}
  \item \textbf{Retrieve-or-not decision}: Agent assesses if it already knows the answer (skip retrieval for factual questions in its training data)
  \item \textbf{Query planning}: Decomposes complex questions into sub-queries (``What year did X happen?'' + ``Who was president then?'')
  \item \textbf{Self-evaluation}: After retrieval, grades relevance. If insufficient, reformulates query or tries different source.
  \item \textbf{Multi-hop reasoning}: Retrieves $\to$ reasons $\to$ identifies knowledge gaps $\to$ retrieves again
  \item \textbf{Source routing}: Routes queries to appropriate knowledge bases (web for current events; internal docs for company info; code search for programming)
\end{itemize}

\begin{itemize}
  \item \textbf{是否检索决策}：智能体评估是否已经知道答案（对于训练数据中的事实性问题，跳过检索）
  \item \textbf{查询规划}：将复杂问题分解为子查询（“X 发生在哪一年？”+“谁当时是总统？”）
  \item \textbf{自我评估}：检索后评估相关性。如果不足，则重新表述查询或尝试不同的来源。
  \item \textbf{多跳推理}：检索 $\to$ 推理 $\to$ 识别知识缺口 $\to$ 再次检索
  \item \textbf{来源路由}：将查询路由到适当的知识库（当前事件用网络；公司信息用内部文档；编程任务用代码搜索）
\end{itemize}

\textbf{Key architectural difference}: Standard RAG = deterministic pipeline. Agentic RAG = state machine with conditional transitions (LangGraph pattern with retrieve/grade/rewrite/generate nodes).

\textbf{关键架构差异}：标准 RAG = 确定性流水线。Agentic RAG = 带有条件转换的状态机（LangGraph 模式，包含检索/评估/重写/生成节点）。

\textbf{Trade-off}: Agentic RAG is more accurate on complex queries but adds latency (multiple LLM calls for routing/grading). Use standard RAG for simple factual lookups; agentic RAG for multi-hop or ambiguous queries.

\textbf{权衡}：Agentic RAG 在复杂查询上更精确，但增加了延迟（多次 LLM 调用用于路由/评估）。对于简单的事实查询使用标准 RAG；对于多跳或模糊查询使用 agentic RAG。

\emph{\textbf{Review:} Chapters~15 and~17 (RAG; Agent Harness).}
\emph{\textbf{回顾：} 第 15 章和第 17 章（RAG；Agent Harness）。}
\end{questionbox}

\begin{questionbox}[Q: Compare Self-RAG and CRAG approaches to improving retrieval quality]
**Answer**:

**答案**：

\textbf{Self-RAG} (Asai et al., 2023):

\textbf{Self-RAG}（Asai 等人，2023）：

\begin{itemize}
  \item Trains special \emph{reflection tokens} into the LLM vocabulary
  \item At inference, model outputs tokens like [Retrieve], [IsRel], [IsSup], [IsUse]
  \item Model decides \emph{when} to retrieve (not every query needs it)
  \item After retrieval, model self-grades: Is the retrieved passage relevant? Does my answer follow from it?
  \item \textbf{Training}: SFT on data augmented with reflection labels from GPT-4
  \item \textbf{Pro}: Single model handles everything. \textbf{Con}: Requires custom training.
\end{itemize}

\begin{itemize}
  \item 在 LLM 词汇中训练特殊的\emph{反射标记}
  \item 推理时，模型输出诸如 [Retrieve]、[IsRel]、[IsSup]、[IsUse] 等标记
  \item 模型决定\emph{何时}检索（并非每个查询都需要检索）
  \item 检索后，模型自我评估：检索到的段落是否相关？我的答案是否源于它？
  \item \textbf{训练}：在由 GPT-4 生成的反射标签增强的数据上进行 SFT
  \item \textbf{优点}：单个模型处理所有事情。\textbf{缺点}：需要定制训练。
\end{itemize}

\textbf{CRAG} (Corrective RAG, Yan et al., 2024):

\textbf{CRAG}（纠正性 RAG，Yan 等人，2024）：

\begin{itemize}
  \item Uses a lightweight \emph{retrieval evaluator} (separate model) to grade retrieved docs
  \item Three actions based on confidence: \texttt{Correct} (use as-is), \texttt{Ambiguous} (augment with web search), \texttt{Incorrect} (discard; fallback to web)
  \item Adds a \emph{knowledge refinement} step: extract only relevant sentences from retrieved docs
  \item \textbf{Pro}: Works with any frozen LLM. \textbf{Con}: Extra model for evaluation; added latency.
\end{itemize}

\begin{itemize}
  \item 使用轻量级的\emph{检索评估器}（独立模型）来评估检索到的文档
  \item 基于置信度的三种动作：\texttt{Correct}（原样使用）、\texttt{Ambiguous}（通过网络搜索增强）、\texttt{Incorrect}（丢弃；回退到网络搜索）
  \item 添加一个\emph{知识精炼}步骤：仅从检索到的文档中提取相关句子
  \item \textbf{优点}：可与任何冻结的 LLM 一起使用。\textbf{缺点}：额外的评估模型；增加延迟。
\end{itemize}

\textbf{Key difference}: Self-RAG embeds retrieval decisions into the LLM itself (requires training). CRAG is a pipeline approach that wraps around any LLM (no training needed). Self-RAG is more elegant; CRAG is more practical for production with existing models.

\textbf{关键区别}：Self-RAG 将检索决策嵌入到 LLM 本身（需要训练）。CRAG 是一种流水线方法，可以包装任何 LLM（无需训练）。Self-RAG 更优雅；CRAG 对于使用现有模型的生产环境更实用。

\emph{\textbf{Review:} Chapter~15 (Retrieval-Augmented Generation).}
\emph{\textbf{回顾：} 第 15 章（检索增强生成）。}
\end{questionbox}

\begin{questionbox}[Q: What is the lost-in-the-middle problem and how do you mitigate it?]
**Answer**: \textbf{The problem}: When retrieved context is long (many passages), LLMs disproportionately attend to information at the \emph{beginning} and \emph{end} of the context, ignoring information in the middle. If the answer is in passage 5 of 10, the model may miss it.

**答案**：\textbf{问题}：当检索到的上下文很长（大量段落）时，LLM 会不成比例地关注上下文的\emph{开头}和\emph{结尾}，而忽略中间的信息。如果答案在 10 个段落中的第 5 段，模型可能会错过它。

\textbf{Empirical evidence}: Liu et al. (2023) showed that for 20-document retrieval, accuracy drops by 15--20\% when the relevant document is in positions 5--15 vs positions 1--3.

\textbf{经验证据}：Liu 等人（2023）表明，对于 20 个文档的检索，当相关文档位于第 5--15 位时，与位于第 1--3 位相比，准确率下降 15--20%。

\textbf{Mitigation strategies}:

\textbf{缓解策略}：

\begin{enumerate}
  \item \textbf{Re-rank and truncate}: Use a cross-encoder to re-rank, then only include top-3 most relevant passages (fewer = less lost-in-middle).
  \item \textbf{Strategic ordering}: Place highest-relevance passages at the start AND end of context, low-relevance in the middle.
  \item \textbf{Contextual compression}: Summarize each passage to 1--2 sentences before insertion. Less text = less position bias.
  \item \textbf{Map-reduce}: Process each passage independently (map), then combine answers (reduce). Eliminates position effects entirely.
  \item \textbf{Citation prompting}: Ask model to cite which passage it used. This forces attention to all passages.
  \item \textbf{Chunk size reduction}: Smaller chunks mean fewer total chunks needed to cover the answer.
\end{enumerate}

\begin{enumerate}
  \item \textbf{重新排序并截断}：使用交叉编码器重新排序，然后只包含最相关的 top-3 段落（更少段落 = 更少中间丢失）。
  \item \textbf{策略性排序}：将最高相关性的段落放在上下文的开头和结尾，低相关性的放在中间。
  \item \textbf{上下文压缩}：在插入之前将每个段落总结为 1--2 句话。更少的文本 = 更少的位置偏差。
  \item \textbf{Map-reduce}：独立处理每个段落（map），然后合并答案（reduce）。完全消除位置影响。
  \item \textbf{引用提示}：要求模型引用它使用了哪个段落。这强制模型关注所有段落。
  \item \textbf{减少块大小}：更小的块意味着覆盖答案所需的总块数更少。
\end{enumerate}

\textbf{Best practice}: Retrieve many (20+), re-rank to top 3--5, order by relevance (best first). This sidesteps the problem entirely for most use cases.

\textbf{最佳实践}：检索大量（20+），重新排序到 top 3--5，按相关性排序（最佳在前）。这可以在大多数用例中完全规避该问题。

\emph{\textbf{Review:} Chapter~15 (Retrieval-Augmented Generation).}
\emph{\textbf{回顾：} 第 15 章（检索增强生成）。}
\end{questionbox}
```