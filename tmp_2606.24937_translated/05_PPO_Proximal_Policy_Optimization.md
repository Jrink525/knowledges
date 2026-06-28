```markdown
\chapter{PPO --- Proximal Policy Optimization}
\chapter{PPO —— 近端策略优化}
\label{ppo-proximal-policy-optimization}


\section{Motivation and History}
\section{动机与历史}
\label{motivation-and-history}


\textbf{Problem}: Vanilla policy gradient updates have no constraint on step size. A single unlucky batch can push the policy into a region where it generates garbage $\rightarrow$ garbage gets low rewards $\rightarrow$ next gradient makes things worse $\rightarrow$ unrecoverable collapse.
\textbf{问题}：原始的策略梯度更新对步长没有约束。一个不幸的批次就可能将策略推入生成垃圾数据的区域 $\rightarrow$ 垃圾数据获得低奖励 $\rightarrow$ 下一次梯度使情况更糟 $\rightarrow$ 不可恢复的崩溃。

\textbf{Solution history}:
\textbf{解决方案历史}：

\begin{enumerate}
  \item \textbf{TRPO}~\cite{schulman2015trust} (2015): Constrain KL divergence between old and new policy. Works perfectly but requires expensive second-order optimization (Fisher information matrix, conjugate gradients).
  \item \textbf{TRPO}~\cite{schulman2015trust} (2015)：约束新旧策略之间的KL散度。效果完美，但需要昂贵的二阶优化（Fisher信息矩阵，共轭梯度法）。
  \item \textbf{PPO} (2017)~\cite{schulman2017proximal}: Achieve similar stability with a simple first-order clipped objective. 10$\times$ simpler to implement, works almost as well, scales to distributed training trivially.
  \item \textbf{PPO} (2017)~\cite{schulman2017proximal}：通过一个简单的一阶裁剪目标实现类似的稳定性。实现简单10倍，效果几乎一样好，并且可以轻松扩展到分布式训练。
\end{enumerate}


\section{The Clipped Objective}
\section{裁剪目标函数}
\label{the-clipped-objective}


The core innovation of PPO is a clipped surrogate objective that prevents destructively large policy updates while remaining simple to implement.
PPO的核心创新是一个裁剪的替代目标函数，它能够防止破坏性的大规模策略更新，同时保持实现简单。

\begin{equation}
\boxed{L^{\text{CLIP}}(\theta) = \mathbb{E}_t\left[\min\left(r_t(\theta)\hat{A}_t,\; \text{clip}(r_t(\theta), 1{-}\epsilon, 1{+}\epsilon)\hat{A}_t\right)\right]}
\end{equation}
 where $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_\text{old}}(a_t|s_t)}$ is the probability ratio.
其中 $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_\text{old}}(a_t|s_t)}$ 是概率比率。

\begin{intuitionbox}[Clipping Intuition — The Key Insight]
\begin{intuitionbox}[裁剪直觉 —— 关键洞见]
The $\min$ operator creates a \textbf{pessimistic bound}:
$\min$ 算子创建了一个\textbf{悲观边界}：

\begin{itemize}
  \item \textbf{Good action ($\hat{A} > 0$)}: We want to increase its probability. The surrogate $r\hat{A}$ grows as $r$ increases. But clip caps benefit at $r = 1 + \epsilon$. \emph{``Don’t get greedy on one good example.''}
  \item \textbf{好的动作 ($\hat{A} > 0$)}：我们希望增加它的概率。替代项 $r\hat{A}$ 随着 $r$ 增加而增长。但裁剪将收益上限限制在 $r = 1 + \epsilon$。\emph{“不要因为一个好的例子而变得贪婪。”}
  \item \textbf{Bad action ($\hat{A} < 0$)}: We want to decrease its probability. $r\hat{A}$ improves as $r$ decreases. But clip caps benefit at $r = 1 - \epsilon$. \emph{``Don’t forget too aggressively based on one bad example.''}
  \item \textbf{坏的动作 ($\hat{A} < 0$)}：我们希望降低它的概率。$r\hat{A}$ 随着 $r$ 减小而改善。但裁剪将收益上限限制在 $r = 1 - \epsilon$。\emph{“不要因为一个坏例子而过于激进地遗忘。”}
\end{itemize}


Net effect: policy changes by at most $\pm$20\% per update step. Prevents both catastrophic collapse and overconfident specialization.
净效果：每次更新步长中策略最多改变 $\pm$20%。防止了灾难性崩溃和过度自信的专化。
\end{intuitionbox}


\section{Full PPO Loss}
\section{完整的PPO损失函数}
\label{full-ppo-loss}


\begin{equation}
L = L^{\text{CLIP}} - c_1 \underbrace{(V_\theta(s_t) - V^{\text{target}}_t)^2}_{\text{value loss}} + c_2 \underbrace{H[\pi_\theta(\cdot|s_t)]}_{\text{entropy bonus}}
\end{equation}


\begin{itemize}
  \item \textbf{Value loss} ($c_1 = 0.1$): Trains the critic to predict returns. Also clipped for stability.
  \item \textbf{价值损失} ($c_1 = 0.1$)：训练评论家（critic）预测回报。也进行了裁剪以保证稳定性。
  \item \textbf{Entropy bonus} ($c_2 = 0.01$): Prevents premature convergence to deterministic policy. Critical for exploration.
  \item \textbf{熵奖励} ($c_2 = 0.01$)：防止过早收敛到确定性策略。对探索至关重要。
\end{itemize}


\section{Derivation of the PPO Gradient and Update Rule}
\section{PPO梯度与更新规则的推导}
\label{derivation-of-the-ppo-gradient-and-update-rule}


This section traces the mathematical path from the RL objective to the PPO update rule, showing \emph{why} the clipped surrogate works.
本节追踪从强化学习目标到PPO更新规则的数学路径，展示裁剪替代项\textit{为什么}有效。

\subsection{Step 1: The RL Objective}
\subsection{第1步：强化学习目标}
\label{step-1-the-rl-objective}


The goal is to maximize expected cumulative reward under the policy: 
目标是最大化策略下的期望累积奖励：
\begin{equation}
J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}\left[\sum_{t=0}^T r_t\right]
\end{equation}


\subsection{Step 2: Policy Gradient Theorem}
\subsection{第2步：策略梯度定理}
\label{step-2-policy-gradient-theorem}


The gradient of $J(\theta)$ with respect to policy parameters: 
$J(\theta)$ 关于策略参数的梯度：
\begin{equation}
\boxed{\nabla_\theta J(\theta) = \mathbb{E}_{\pi_\theta}\left[\sum_{t=0}^T \nabla_\theta \log \pi_\theta(a_t|s_t) \cdot \hat{A}_t\right]}
\end{equation}


where $\hat{A}_t$ is the advantage function (how much better action $a_t$ was compared to the average action in state $s_t$). This replaces the full return with the advantage to reduce variance.
其中 $\hat{A}_t$ 是优势函数（动作 $a_t$ 相比于状态 $s_t$ 下平均动作好多少）。这里用优势替代完整回报以降低方差。

\subsection{Step 3: Importance Sampling for Off-Policy Data}
\subsection{第3步：离策略数据的重要性采样}
\label{step-3-importance-sampling-for-off-policy-data}


PPO collects data using $\pi_{\theta_{\text{old}}}$ but updates $\pi_\theta$. To correct for this distribution mismatch, apply importance sampling: 
PPO 使用 $\pi_{\theta_{\text{old}}}$ 收集数据，但更新 $\pi_\theta$。为修正这种分布不匹配，应用重要性采样：
\begin{equation}
\nabla_\theta J(\theta) = \mathbb{E}_{\pi_{\theta_{\text{old}}}}\left[\frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{\text{old}}}(a_t|s_t)} \nabla_\theta \log \pi_\theta(a_t|s_t) \cdot \hat{A}_t\right]
\end{equation}


Define the probability ratio $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{\text{old}}}(a_t|s_t)}$. Using the identity $\nabla_\theta \log f = \frac{\nabla_\theta f}{f}$, we get: 
定义概率比率 $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{\text{old}}}(a_t|s_t)}$。利用恒等式 $\nabla_\theta \log f = \frac{\nabla_\theta f}{f}$，我们得到：
\begin{equation}
\nabla_\theta J(\theta) = \mathbb{E}_{\pi_{\theta_{\text{old}}}}\left[\nabla_\theta\, r_t(\theta) \cdot \hat{A}_t\right]
\end{equation}


This means maximizing the \textbf{surrogate objective}: 
这意味着最大化\textbf{替代目标函数}：
\begin{equation}
L^{\text{CPI}}(\theta) = \mathbb{E}_t\left[r_t(\theta) \cdot \hat{A}_t\right]
\end{equation}


\subsection{Step 4: The Problem with Unconstrained Surrogates}
\subsection{第4步：无约束替代项的问题}
\label{step-4-the-problem-with-unconstrained-surrogates}


$L^{\text{CPI}}$ is a valid objective, but without constraints, a single gradient step can push $r_t(\theta)$ far from 1.0, causing:
$L^{\text{CPI}}$ 是一个有效的目标函数，但若无约束，一个梯度步长就可能将 $r_t(\theta)$ 推离1.0很远，从而导致：

\begin{itemize}
  \item Importance weights become extreme $\rightarrow$ high variance
  \item 重要性权重变得极端 $\rightarrow$ 高方差
  \item Policy enters untested regions $\rightarrow$ reward model gives unreliable scores
  \item 策略进入未测试区域 $\rightarrow$ 奖励模型给出不可靠的分数
  \item Catastrophic collapse: policy generates garbage, can’t recover
  \item 灾难性崩溃：策略生成垃圾数据，无法恢复
\end{itemize}


\textbf{TRPO solution}: Constrain $D_{\text{KL}}(\pi_{\theta_{\text{old}}} \| \pi_\theta) \leq \delta$. Requires second-order methods (expensive).
\textbf{TRPO解决方案}：约束 $D_{\text{KL}}(\pi_{\theta_{\text{old}}} \| \pi_\theta) \leq \delta$。需要二阶方法（昂贵）。

\subsection{Step 5: PPO’s Clipped Surrogate (First-Order Approximation)}
\subsection{第5步：PPO的裁剪替代项（一阶近似）}
\label{step-5-ppos-clipped-surrogate-first-order-approximation}


PPO replaces the hard KL constraint with a \textbf{clipped objective} that achieves similar behavior using only first-order gradients:
PPO 用\textbf{裁剪目标函数}替代了硬KL约束，该目标仅使用一阶梯度就能实现类似行为：

\begin{equation}
\boxed{L^{\text{CLIP}}(\theta) = \mathbb{E}_t\left[\min\!\left(r_t(\theta)\hat{A}_t,\;\text{clip}(r_t(\theta), 1{-}\epsilon, 1{+}\epsilon)\hat{A}_t\right)\right]}
\end{equation}


\textbf{Derivation of the gradient}:
\textbf{梯度的推导}：


Let $L_t = \min(r_t \hat{A}_t,\; \bar{r}_t \hat{A}_t)$ where $\bar{r}_t = \text{clip}(r_t, 1{-}\epsilon, 1{+}\epsilon)$.
令 $L_t = \min(r_t \hat{A}_t,\; \bar{r}_t \hat{A}_t)$，其中 $\bar{r}_t = \text{clip}(r_t, 1{-}\epsilon, 1{+}\epsilon)$。

\begin{equation}
\nabla_\theta L_t = \begin{cases}
\nabla_\theta r_t(\theta) \cdot \hat{A}_t & \text{if } r_t \hat{A}_t < \bar{r}_t \hat{A}_t \text{ (unclipped term is smaller)} \\
0 & \text{if } r_t \hat{A}_t \geq \bar{r}_t \hat{A}_t \text{ (clipped term is smaller, gradient = 0)}
\end{cases}
\end{equation}


Expanding the conditions:
展开条件：

\begin{itemize}
  \item \textbf{When $\hat{A}_t > 0$ and $r_t < 1+\epsilon$}: Gradient flows normally --- policy is encouraged to increase $\pi_\theta(a_t|s_t)$.
  \item \textbf{当 $\hat{A}_t > 0$ 且 $r_t < 1+\epsilon$ 时}：梯度正常流动 —— 鼓励策略增加 $\pi_\theta(a_t|s_t)$。
  \item \textbf{When $\hat{A}_t > 0$ and $r_t \geq 1+\epsilon$}: Gradient is \textbf{zero} --- policy has already increased enough, stop pushing.
  \item \textbf{当 $\hat{A}_t > 0$ 且 $r_t \geq 1+\epsilon$ 时}：梯度为 \textbf{零} —— 策略已经增加得足够多，停止推动。
  \item \textbf{When $\hat{A}_t < 0$ and $r_t > 1-\epsilon$}: Gradient flows normally --- policy is encouraged to decrease $\pi_\theta(a_t|s_t)$.
  \item \textbf{当 $\hat{A}_t < 0$ 且 $r_t > 1-\epsilon$ 时}：梯度正常流动 —— 鼓励策略降低 $\pi_\theta(a_t|s_t)$。
  \item \textbf{When $\hat{A}_t < 0$ and $r_t \leq 1-\epsilon$}: Gradient is \textbf{zero} --- policy has already decreased enough, stop pushing.
  \item \textbf{当 $\hat{A}_t < 0$ 且 $r_t \leq 1-\epsilon$ 时}：梯度为 \textbf{零} —— 策略已经降低得足够多，停止推动。
\end{itemize}


\subsection{Step 6: The Complete PPO Update Rule}
\subsection{第6步：完整的PPO更新规则}
\label{step-6-the-complete-ppo-update-rule}


Combining the clipped policy loss, value loss, and entropy bonus: 
结合裁剪的策略损失、价值损失和熵奖励：
\begin{equation}
\boxed{\theta_{k+1} = \theta_k + \alpha \cdot \nabla_\theta \left[L^{\text{CLIP}}(\theta) - c_1 L^{\text{VF}}(\theta) + c_2 H[\pi_\theta]\right]}
\end{equation}


where: 
其中：
\begin{align}
L^{\text{VF}}(\theta) &= \left(V_\theta(s_t) - V_t^{\text{target}}\right)^2 & &\text{(value function regression loss)} \\
H[\pi_\theta] &= -\sum_a \pi_\theta(a|s_t)\log\pi_\theta(a|s_t) & &\text{(entropy of the policy)}
\end{align}
\begin{align}
L^{\text{VF}}(\theta) &= \left(V_\theta(s_t) - V_t^{\text{target}}\right)^2 & &\text{（价值函数回归损失）} \\
H[\pi_\theta] &= -\sum_a \pi_\theta(a|s_t)\log\pi_\theta(a|s_t) & &\text{（策略的熵）}
\end{align}
```

## Summary: Why This Works
## 总结：为何有效？

\begin{enumerate}
  \item \textbf{Policy gradient theorem} gives us the direction to improve the policy.
  \item \textbf{策略梯度定理（Policy Gradient Theorem）} 为我们提供了改进策略的方向。
  \item \textbf{Importance sampling} lets us reuse data from $\pi_{\theta_{\text{old}}}$ across multiple epochs.
  \item \textbf{重要性采样（Importance Sampling）} 使我们能够跨多个周期重复使用来自 $\pi_{\theta_{\text{old}}}$ 的数据。
  \item \textbf{Clipping} prevents the importance weights from becoming extreme, keeping updates safe.
  \item \textbf{裁剪（Clipping）} 防止重要性权重变得极端，从而保证更新的安全性。
  \item \textbf{The min operator} ensures we always take the more conservative of (clipped, unclipped) --- a pessimistic lower bound on improvement.
  \item \textbf{最小值运算符（Min Operator）} 确保我们始终采用（裁剪后的、未裁剪的）中更保守的值——这是一个悲观的改进下界。
  \item \textbf{Result}: Monotonic improvement with probability 1, using only first-order gradients. No Hessians, no conjugate gradients, no line searches.
  \item \textbf{结果}：以概率 1 实现单调改进，且仅使用一阶梯度。无需海森矩阵、共轭梯度或线性搜索。
\end{enumerate}

## Rollout Buffer and Rollouts
## 滚动缓冲区与轨迹收集

In PPO, data management relies on a specialized, short-term storage system known as a \textbf{Rollout Buffer}. Unlike off-policy algorithms (DQN) that store experiences indefinitely in a replay buffer, PPO requires an ephemeral structure to satisfy its on-policy mathematical constraints.

在 PPO 中，数据管理依赖于一个专门的短期存储系统，称为 \textbf{滚动缓冲区（Rollout Buffer）}。与将经验无限期存储在回放缓冲区中的离策略算法（如 DQN）不同，PPO 需要一个临时结构来满足其在线策略的数学约束。

\subsection{What is a Rollout?}
\subsection{什么是轨迹收集（Rollout）？}

A \textbf{rollout} (trajectory) is a sequence of interactions generated by the agent running its current policy in the environment:

\textbf{轨迹收集（Rollout）}（也称轨迹）是智能体在当前策略下与环境进行交互所产生的一系列步骤：

\begin{itemize}
  \item \textbf{The process}: The agent observes a state, selects an action, receives a reward, and moves to the next state. It repeats for a fixed number of steps or until the episode ends.
  \item \textbf{过程}：智能体观察状态、选择动作、获得奖励并转移到下一状态。重复进行固定步数或直到回合结束。
  \item \textbf{In LLMs/RLHF}: A rollout consists of taking a prompt from a dataset and letting the language model generate a complete sequence of tokens token-by-token until an end-of-text marker is hit. Each token is one ``step.''
  \item \textbf{在 LLM/RLHF 中}：轨迹收集包括从数据集中获取一个提示，并让语言模型逐 token 生成完整的 token 序列，直到遇到文本结束标记。每个 token 就是一个“步骤”。
\end{itemize}

\subsection{The Rollout Buffer}
\subsection{滚动缓冲区（The Rollout Buffer）}

The rollout buffer temporarily stores all data collected during the rollout phase. For every generated token/step, it records: 
\begin{equation}
\boxed{\mathcal{B} = \left\{ \left(s_t,\; a_t,\; \log\pi_{\theta_{\text{old}}}(a_t|s_t),\; r_t,\; V(s_t)\right) \right\}_{t=1}^{T}}
\end{equation}

滚动缓冲区临时存储轨迹收集阶段收集的所有数据。对于每个生成的 token/步骤，它记录：
\begin{equation}
\boxed{\mathcal{B} = \left\{ \left(s_t,\; a_t,\; \log\pi_{\theta_{\text{old}}}(a_t|s_t),\; r_t,\; V(s_t)\right) \right\}_{t=1}^{T}}
\end{equation}

\begin{itemize}
  \item $s_t, a_t, r_t$: State, action taken, and reward at step $t$.
  \item $\log\pi_{\theta_{\text{old}}}(a_t|s_t)$: Log-probability of taking that action under the exact policy that generated it (needed for ratio computation).
  \item $V(s_t)$: Value function’s baseline prediction (needed for GAE advantage computation).
  \item $s_t, a_t, r_t$：步骤 $t$ 的状态、执行的动作和奖励。
  \item $\log\pi_{\theta_{\text{old}}}(a_t|s_t)$：在生成该动作的原始策略下该动作的对数概率（用于比率计算）。
  \item $V(s_t)$：价值函数的基线预测（用于 GAE 优势计算）。
\end{itemize}

\subsection{The Rollout Buffer Lifecycle}
\subsection{滚动缓冲区的生命周期}

The buffer operates in a strict three-phase clockwork cycle:

该缓冲区按照严格的三阶段周期运行：

\begin{enumerate}
  \item \textbf{Collect}: The active policy interacts with the environment to fill the buffer with fresh trajectories (for a 70B model with batch=128, max\_tokens=512: up to 65K token-level transitions per rollout).
  \item \textbf{收集}：当前策略与环境交互，用新轨迹填充缓冲区（对于 70B 模型，batch=128，max\_tokens=512：每次轨迹收集最多 65K 个 token 级转移）。
  \item \textbf{Train}: Compute GAE advantages across trajectories. Run $K$ epochs (typically 3--10) of mini-batch gradient descent to update policy weights using the clipped objective.
  \item \textbf{训练}：跨轨迹计算 GAE 优势。运行 $K$ 个周期（通常为 3--10）的小批量梯度下降，使用裁剪后的目标更新策略权重。
  \item \textbf{Purge}: The entire buffer is \textbf{completely wiped clean}. Because PPO is on-policy, data generated by the old policy cannot be safely reused for the next update cycle --- the ratio $r_t(\theta)$ would become stale and the clipping guarantees would break.
  \item \textbf{清除}：整个缓冲区被\textbf{完全清空}。由于 PPO 是在线策略，旧策略生成的数据不能安全地用于下一次更新周期——比率 $r_t(\theta)$ 会过时，裁剪保证会被破坏。
\end{enumerate}

\begin{warningbox}[Rollout Buffer vs Replay Buffer]
\textbf{Replay Buffer} (DQN, SAC): Off-policy. Stores millions of transitions indefinitely. Random sampling. Data reused across many updates.

\textbf{回放缓冲区（Replay Buffer）}（DQN, SAC）：离策略。无限期存储数百万个转移。随机采样。数据跨多次更新重复使用。

\textbf{Rollout Buffer} (PPO, GRPO): On-policy. Stores one batch of trajectories. Used for a few epochs, then discarded entirely. Fresh data required every cycle.

\textbf{滚动缓冲区（Rollout Buffer）}（PPO, GRPO）：在线策略。存储一批轨迹。使用几个周期后完全丢弃。每个周期都需要新数据。

This is why PPO requires continuous generation --- the buffer is emptied after every update, demanding fresh rollouts. This makes the generation bottleneck (60--70\% of wall-clock time) particularly painful.

这就是为什么 PPO 需要持续生成——每次更新后缓冲区被清空，需要新的轨迹收集。这使得生成瓶颈（占挂钟时间的 60--70%）尤为突出。
\end{warningbox}

\begin{intuitionbox}[vLLM in RLHF Context]
In RLHF training, vLLM is used for the \textbf{generation phase} (60--70\% of wall-clock time). The policy model generates rollouts that are then scored by the reward model. Key benefits:

在 RLHF 训练中，vLLM 用于\textbf{生成阶段}（占挂钟时间的 60--70%）。策略模型生成轨迹，然后由奖励模型评分。主要优势：

\begin{itemize}
  \item \textbf{Batched generation}: Generate 256+ responses in parallel across prompts.
  \item \textbf{批量生成}：跨提示并行生成 256 个以上响应。
  \item \textbf{Memory efficiency}: Fit more concurrent generations $\rightarrow$ higher GPU utilization during the generation bottleneck.
  \item \textbf{内存效率}：容纳更多并发生成 $\rightarrow$ 在生成瓶颈期间提高 GPU 利用率。
  \item \textbf{Prefix sharing}: When generating $N=8$ responses per prompt (GRPO), the prompt KV is computed once and shared across all 8 --- no redundant prefill.
  \item \textbf{前缀共享}：当每个提示生成 $N=8$ 个响应（GRPO）时，提示 KV 只需计算一次，并在所有 8 个响应中共享——无需冗余预填充。
  \item \textbf{Integration}: Frameworks like OpenRLHF and TRL use vLLM as the generation backend, separating generation workers (vLLM) from training workers (DeepSpeed/FSDP).
  \item \textbf{集成}：OpenRLHF 和 TRL 等框架将 vLLM 用作生成后端，将生成工作器（vLLM）与训练工作器（DeepSpeed/FSDP）分离。
\end{itemize}
\end{intuitionbox}

## PPO for RLHF: The Full Loop
## 用于 RLHF 的 PPO：完整循环

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_025_fig25.png}
\end{figure}

\begin{examplebox}[Concrete PPO Step for a 70B Chat Model]
\textbf{Setup}: Batch of 128 prompts, Llama-3-70B policy, 512 max tokens.

\textbf{设置}：128 个提示的批次，Llama-3-70B 策略，最大 512 个 token。

\textbf{Step 1 --- Generate}: Sample 128 responses (temperature=0.7, top-p=0.9). This takes 60\% of time.

\textbf{步骤 1 —— 生成}：采样 128 个响应（温度=0.7，top-p=0.9）。这一步占用 60% 的时间。

\textbf{Step 2 --- Score}: Reward model scores each (prompt, response) pair. Range: 0.2--0.95.

\textbf{步骤 2 —— 评分}：奖励模型对每个（提示，响应）对进行评分。范围：0.2--0.95。

\textbf{Step 3 --- KL}: Compute per-token KL: $\text{KL}_t = \log\pi_\theta(y_t|y_{<t}) - \log\pi_\text{ref}(y_t|y_{<t})$. Mean KL across tokens: typically 3--8.

\textbf{步骤 3 —— KL}：计算每个 token 的 KL：$\text{KL}_t = \log\pi_\theta(y_t|y_{<t}) - \log\pi_\text{ref}(y_t|y_{<t})$。所有 token 的平均 KL：通常为 3--8。

\textbf{Step 4 --- Final reward}: $R = r_\text{RM} - 0.05 \times \text{mean\_KL}$ (only at last token).

\textbf{步骤 4 —— 最终奖励}：$R = r_\text{RM} - 0.05 \times \text{mean\_KL}$（仅在最后一个 token 处）。

\textbf{Step 5 --- GAE}: Compute $\hat{A}_t$ for each token position using value head predictions. Whiten advantages (zero mean, unit variance).

\textbf{步骤 5 —— GAE}：使用价值头部预测计算每个 token 位置的 $\hat{A}_t$。对优势进行白化（零均值，单位方差）。

\textbf{Step 6 --- Update}: 4 epochs of SGD on mini-batches of 16. Clip ratio $\epsilon = 0.2$. Gradient norm clipping at 1.0.

\textbf{步骤 6 —— 更新}：对大小为 16 的小批量进行 4 个周期的 SGD。裁剪比率 $\epsilon = 0.2$。梯度范数裁剪为 1.0。

\textbf{Result}: Policy improves by $\sim$0.005 win-rate per step. After 10K steps: 5--10\% absolute improvement over SFT.

\textbf{结果}：策略每步提升约 0.005 的胜率。经过 10K 步后：相对于 SFT 绝对提升 5--10%。
\end{examplebox}

\begin{warningbox}[Tokenization Pitfalls in RL for LLMs]
When computing per-token KL penalties and advantages, remember that tokenization determines what a ``step'' is. A single conceptual action (e.g., outputting ``2024'') might span 1--4 tokens depending on the tokenizer. This creates subtle issues:

在计算逐 token 的 KL 惩罚和优势时，请记住 tokenization 决定了什么是“步骤”。一个概念上的单个动作（例如输出“2024”）可能跨越 1--4 个 token，具体取决于 tokenizer。这会产生一些微妙的问题：

\begin{itemize}
  \item \textbf{KL accounting}: Per-token KL sums to different totals for the same semantic content tokenized differently (e.g., rare words split into more subwords get higher total KL penalty).
  \item \textbf{KL 计算}：对于相同语义内容的不同 tokenization，逐 token 的 KL 总和会不同（例如，稀有词被拆分为更多子词，会获得更高的 KL 惩罚总和）。
  \item \textbf{Credit assignment}: GAE assigns advantage per token position---but semantic ``decisions'' often span multiple tokens. The model only truly ``decides'' at the first token of a word; subsequent subword tokens are largely deterministic.
  \item \textbf{信用分配}：GAE 为每个 token 位置分配优势——但语义上的“决策”通常跨越多个 token。模型仅在单词的第一个 token 处真正“决定”；后续的子词 token 在很大程度上是确定性的。
  \item \textbf{Reward placement}: Placing reward only at the final token means all preceding tokens must propagate credit backward through GAE---longer responses suffer from more diluted signal.
  \item \textbf{奖励放置}：仅在最后一个 token 处放置奖励意味着所有前面的 token 必须通过 GAE 向后传播信用——较长的响应会面临更稀释的信号。
\end{itemize}

\textbf{Mitigation}: Some systems normalize KL by sequence length, use word-level reward shaping, or apply reward at semantic boundaries rather than the final token.

\textbf{缓解措施}：一些系统按序列长度归一化 KL，使用词级奖励塑造，或者在语义边界而不是最后一个 token 处施加奖励。
\end{warningbox}

## Detailed Mechanics: Logits and Policy Updates
## 详细机制：Logits 与策略更新

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_026_fig26.png}
\caption{PPO end-to-end: from prompt batch through generation, reward scoring, KL computation, advantage estimation, to clipped policy update. The feedback loop shows the updated policy being used for the next generation step.}
\end{figure}

PPO manages two distinct parameter states in memory, which share the same neural network topology but hold different weight values during optimization:

PPO 在内存中管理两个不同的参数状态，它们共享相同的神经网络拓扑，但在优化过程中持有不同的权重值：

```markdown
\begin{keybox}[Core Architecture: Two Networks]
\begin{keybox}[核心架构：双网络]

\begin{enumerate}
  \item \textbf{The Policy Network ($\pi_\theta$):} The active, live network parameterized by weights $\theta$. Continuously updated via backpropagation during optimization.
  \item \textbf{策略网络（$\pi_\theta$）：}由权重$\theta$参数化的活跃网络，在优化过程中通过反向传播持续更新。
  \item \textbf{The Old Policy Network ($\pi_{\theta_{\text{old}}}$):} A frozen snapshot parameterized by weights $\theta_{\text{old}}$. Acts as a static anchor during a single optimization cycle to prevent the policy from shifting too drastically.
  \item \textbf{旧策略网络（$\pi_{\theta_{\text{old}}}$）：}由权重$\theta_{\text{old}}$参数化的冻结快照，在单次优化周期中充当静态锚点，防止策略发生剧烈偏移。
\end{enumerate}
\end{keybox}

\subsection{Phase 1: Rollout (Data Collection)}
\subsection{阶段一：Rollout（数据收集）}
\label{phase-1-rollout-data-collection}

During data collection, the agent interacts with the environment for $T$ steps. At each time-step $t$:
在数据收集过程中，智能体与环境交互$T$步。在每个时间步$t$：

\begin{enumerate}
  \item The environment yields the current state/observation $s_t$ (for LLMs: prompt + tokens generated so far).
  \item 环境产生当前状态/观测$s_t$（对于大语言模型：提示词 + 已生成的所有token）。
  \item State $s_t$ is passed through the current network snapshot ($\theta_{\text{old}}$).
  \item 状态$s_t$被传入当前网络快照（$\theta_{\text{old}}$）。
  \item The network outputs raw unnormalized values --- \textbf{logits} $z_{\text{old}}$ --- a vector of size $|V|$ (vocabulary size 32K--128K).
  \item 网络输出原始未归一化值——\textbf{logits} $z_{\text{old}}$——一个大小为$|V|$的向量（词汇表大小32K–128K）。
  \item Probabilities are computed via Softmax: 
  \item 通过Softmax计算概率：
\begin{equation}
\boxed{P(a \mid s_t) = \text{Softmax}(z_{\text{old}}) = \frac{\exp(z_{\text{old}, a})}{\sum_{j=1}^{|V|} \exp(z_{\text{old}, j})}}
\end{equation}
  \item An action $a_t$ (next token) is sampled from $P(a \mid s_t)$, and the transition tuple $\langle s_t, a_t, r_t, s_{t+1} \rangle$ along with $\log \pi_{\theta_{\text{old}}}(a_t \mid s_t)$ is stored in the rollout buffer.
  \item 从$P(a \mid s_t)$中采样一个动作$a_t$（下一个token），转移元组$\langle s_t, a_t, r_t, s_{t+1} \rangle$以及$\log \pi_{\theta_{\text{old}}}(a_t \mid s_t)$被存入rollout缓冲区。
\end{enumerate}

\begin{intuitionbox}[Why Store Log-Probabilities?]
\begin{intuitionbox}[为何存储对数概率？]
Storing $\log \pi_{\theta_{\text{old}}}(a_t \mid s_t)$ as a scalar during rollout avoids re-running the frozen network during optimization. This saves one full forward pass per mini-batch --- significant for 70B models.
在rollout过程中将$\log \pi_{\theta_{\text{old}}}(a_t \mid s_t)$存储为标量，可以避免在优化阶段重新运行冻结的网络。这为每个小批次节省了一次完整的前向传播——对于70B模型意义重大。
\end{intuitionbox}

\subsection{Phase 2: Optimization Loop (Mini-Batch Updates)}
\subsection{阶段二：优化循环（小批次更新）}
\label{phase-2-optimization-loop-mini-batch-updates}

Once the rollout buffer is full, PPO runs $K$ epochs (typically 3--10) over mini-batches. For every gradient step, logits are generated for both policies using the stored state $s_t$:
一旦rollout缓冲区填满，PPO会在小批次上运行$K$个epoch（通常为3–10）。对于每个梯度步骤，使用存储的状态$s_t$为两个策略生成logits：

\textbf{Old Policy Evaluation} (frozen): 
\textbf{旧策略评估（冻结）：}
\begin{equation}
z_{\text{old}} = f(s_t; \theta_{\text{old}}) \quad \longrightarrow \quad \log \pi_{\theta_{\text{old}}}(a_t \mid s_t) = \text{LogSoftmax}(z_{\text{old}})[a_t]
\end{equation}

\emph{Implementation shortcut: reuse the stored scalar from rollout instead of re-computing.}
\emph{实现捷径：重复使用rollout中存储的标量，而非重新计算。}

\textbf{Live Policy Evaluation} (updating): 
\textbf{实时策略评估（正在更新）：}
\begin{equation}
z_{\text{new}} = f(s_t; \theta) \quad \longrightarrow \quad \log \pi_\theta(a_t \mid s_t) = \text{LogSoftmax}(z_{\text{new}})[a_t]
\end{equation}

Because $\theta$ updates after every mini-batch gradient step, $z_{\text{new}}$ changes continuously throughout the optimization loop, whereas $z_{\text{old}}$ remains perfectly static.
由于$\theta$在每个小批次梯度步骤后会更新，$z_{\text{new}}$在整个优化循环中持续变化，而$z_{\text{old}}$则完全保持静态。

\subsection{From Logits to Probability Ratio}
\subsection{从Logits到概率比率}
\label{from-logits-to-probability-ratio}

The core PPO ratio measures how much more or less likely an action is under the new policy vs the old: 
PPO的核心比率衡量一个动作在新策略下相对于旧策略的可能性增加或减少的程度：
\begin{equation}
\boxed{r_t(\theta) = \frac{\pi_\theta(a_t \mid s_t)}{\pi_{\theta_{\text{old}}}(a_t \mid s_t)}}
\end{equation}

To avoid catastrophic numerical underflow/overflow from dividing raw probabilities, the calculation is performed in \textbf{log-space}: 
为了避免直接相除原始概率造成的灾难性数值下溢/上溢，计算在\textbf{对数空间}中进行：
\begin{align}
\log \pi_\theta(a_t \mid s_t) &= \text{LogSoftmax}(z_{\text{new}})[a_t] \\
\log \pi_{\theta_{\text{old}}}(a_t \mid s_t) &= \text{LogSoftmax}(z_{\text{old}})[a_t]
\end{align}

The ratio is recovered via exponentiation of the difference: 
通过差的指数化恢复比率：
\begin{equation}
\boxed{r_t(\theta) = \exp\!\left(\log \pi_\theta(a_t \mid s_t) - \log \pi_{\theta_{\text{old}}}(a_t \mid s_t)\right)}
\end{equation}

This ratio is injected into the PPO clipping objective: 
该比率被注入PPO的裁剪目标函数：
\begin{equation}
\boxed{\mathcal{L}^{\text{CLIP}}(\theta) = \hat{\mathbb{E}}_t \left[ \min\!\left(r_t(\theta)\hat{A}_t, \;\text{clip}(r_t(\theta),\, 1{-}\epsilon,\, 1{+}\epsilon)\,\hat{A}_t\right) \right]}
\end{equation}

\begin{intuitionbox}[How Clipping Works]
\begin{intuitionbox}[裁剪的工作原理]
\begin{itemize}
  \item If $\hat{A}_t > 0$ (good action): ratio is clipped at $1+\epsilon$ --- cannot over-exploit good actions.
  \item 如果$\hat{A}_t > 0$（好动作）：比率被裁剪为$1+\epsilon$——不能过度利用好动作。
  \item If $\hat{A}_t < 0$ (bad action): ratio is clipped at $1-\epsilon$ --- cannot over-penalize bad actions.
  \item 如果$\hat{A}_t < 0$（坏动作）：比率被裁剪为$1-\epsilon$——不能过度惩罚坏动作。
  \item The $\min(\cdot)$ ensures we always take the more conservative estimate.
  \item $\min(\cdot)$确保我们始终采用更保守的估计。
\end{itemize}

Result: monotonic improvement within a trust region --- no catastrophic collapses.
结果：在信任区域内实现单调改进——没有灾难性崩溃。
\end{intuitionbox}

\subsection{The PPO Weight Lifecycle}
\subsection{PPO权重的生命周期}
\label{the-ppo-weight-lifecycle}

\begin{table}[ht!]
\centering
\caption{Evolution of $\theta$ and $\theta_{\text{old}}$ across PPO training phases.}
\caption{$\theta$和$\theta_{\text{old}}$在PPO训练各阶段的演变。}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{Phase} & \textbf{Live $\theta$} & \textbf{Old $\theta_{\text{old}}$} & \textbf{Ratio $r_t(\theta)$} \\
\textbf{阶段} & \textbf{实时$\theta$} & \textbf{旧$\theta_{\text{old}}$} & \textbf{比率$r_t(\theta)$} \\
\midrule
1. Rollout Start & Active copy & Same active copy & Always $1.0$ (by identity) \\
1. Rollout开始 & 活跃副本 & 相同活跃副本 & 始终为$1.0$（恒等） \\
2. Batch Step 1 & Computes gradients & Frozen & $1.0$ (initial step) \\
2. 批次步骤1 & 计算梯度 & 冻结 & $1.0$（初始步骤） \\
3. Batch Step $N$ & Modifying ($\theta \neq \theta_{\text{old}}$) & Frozen & Deviates from $1.0$ (e.g., $1.06$, $0.94$) \\
3. 批次步骤$N$ & 正在修改（$\theta \neq \theta_{\text{old}}$） & 冻结 & 偏离$1.0$（例如$1.06$, $0.94$） \\
4. Clipping Active & Bounded by $\epsilon$ & Frozen & Trapped at bound ($1 \pm \epsilon$) \\
4. 裁剪激活 & 受$\epsilon$限制 & 冻结 & 被限制在边界（$1 \pm \epsilon$） \\
5. Optimization End & Highly optimized & Discarded & N/A \\
5. 优化结束 & 高度优化 & 被丢弃 & 不适用 \\
6. Next Cycle & $\theta \rightarrow \theta_{\text{old}}$ & Receives fresh $\theta$ & Resets back to $1.0$ \\
6. 下一循环 & $\theta \rightarrow \theta_{\text{old}}$ & 接收新的$\theta$ & 重置回$1.0$ \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Continuous Action Spaces Extension}
\subsection{连续动作空间扩展}
\label{continuous-action-spaces-extension}

For continuous action spaces (not typical for LLMs, but important for robotics RL), the network outputs distribution parameters instead of discrete logits:
对于连续动作空间（在大语言模型中不典型，但对机器人强化学习很重要），网络输出分布参数而非离散logits：

\begin{itemize}
  \item Predicted mean vector $\mu$
  \item 预测均值向量$\mu$
  \item Predicted standard deviation vector $\sigma$
  \item 预测标准差向量$\sigma$
\end{itemize}

Log-probabilities are computed via the Gaussian log-PDF: 
通过对数高斯概率密度函数计算对数概率：
\begin{equation}
\boxed{\log \pi(a_t \mid s_t) = -\frac{1}{2}\left(\frac{a_t - \mu}{\sigma}\right)^{\!2} - \log(\sigma) - \frac{1}{2}\log(2\pi)}
\end{equation}

The ratio $r_t(\theta) = \exp(\log \pi_\theta - \log \pi_{\theta_{\text{old}}})$ is then computed identically and fed into the same clipping objective.
然后以相同方式计算比率$r_t(\theta) = \exp(\log \pi_\theta - \log \pi_{\theta_{\text{old}}})$，并输入到相同的裁剪目标函数中。

\section{TRL Implementation}
\section{TRL实现}
\label{trl-implementation}

The HuggingFace TRL library~\cite{vonwerra2022trl} provides production-ready implementations of all major RL methods for LLMs.
HuggingFace TRL库~\cite{vonwerra2022trl}为所有主要的面向大语言模型的强化学习方法提供了生产级实现。

\begin{lstlisting}[style=pythonstyle]
from trl import PPOConfig, PPOTrainer, AutoModelForCausalLMWithValueHead
from transformers import AutoTokenizer
from peft import LoraConfig

# Model setup
# 模型设置
model = AutoModelForCausalLMWithValueHead.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    torch_dtype=torch.bfloat16, device_map="auto",
    peft_config=LoraConfig(r=64, lora_alpha=16, target_modules=["q_proj","v_proj","k_proj","o_proj"])
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")

# PPO config with all critical hyperparameters
# PPO配置，包含所有关键超参数
ppo_config = PPOConfig(
    learning_rate=1.5e-6,        # Low LR for stability
    learning_rate=1.5e-6,        # 低学习率以保证稳定性
    batch_size=128,              # Prompts per step
    batch_size=128,              # 每步的提示词数量
    mini_batch_size=16,          # Gradient accumulation unit
    mini_batch_size=16,          # 梯度累积单元
    ppo_epochs=4,                # Epochs per batch (reuse data)
    ppo_epochs=4,                # 每个批次的epoch数（重用数据）
    gamma=1.0,                   # No discounting (single turn)
    gamma=1.0,                   # 无折扣（单轮交互）
    lam=0.95,                    # GAE lambda
    lam=0.95,                    # 广义优势估计lambda
    cliprange=0.2,               # PPO epsilon
    cliprange=0.2,               # PPO epsilon
    cliprange_value=0.2,         # Value function clipping
    cliprange_value=0.2,         # 价值函数裁剪
    vf_coef=0.1,                 # Value loss coefficient
    vf_coef=0.1,                 # 价值损失系数
    init_kl_coef=0.05,           # Initial KL penalty
    init_kl_coef=0.05,           # 初始KL惩罚
    target_kl=6.0,               # Adaptive KL target
    target_kl=6.0,               # 自适应KL目标
    whiten_rewards=True,         # Normalize advantages
    whiten_rewards=True,         # 标准化优势
    gradient_accumulation_steps=4,
    gradient_accumulation_steps=4,
    max_grad_norm=1.0,
)

ppo_trainer = PPOTrainer(config=ppo_config, model=model, tokenizer=tokenizer,
    dataset=prompt_dataset, data_collator=collator)
```

## Training loop
## 训练循环

```latex
# Training loop
for batch in ppo_trainer.dataloader:
    # 1. Generate responses
    query_tensors = batch["input_ids"]
    response_tensors = ppo_trainer.generate(
        query_tensors, max_new_tokens=512, temperature=0.7, top_p=0.9, do_sample=True
    )
    # 2. Score with reward model
    texts = [tokenizer.decode(r, skip_special_tokens=True) for r in response_tensors]
    rewards = [torch.tensor(reward_model.score(q, r)) for q, r in zip(batch["query"], texts)]
    # 3. PPO update (handles KL, GAE, clipping internally)
    stats = ppo_trainer.step(query_tensors, response_tensors, rewards)
    # Monitor: stats["ppo/mean_scores"], stats["ppo/policy/approx_kl"]
\end{lstlisting}
```

```latex
# 训练循环
for batch in ppo_trainer.dataloader:
    # 1. 生成响应
    query_tensors = batch["input_ids"]
    response_tensors = ppo_trainer.generate(
        query_tensors, max_new_tokens=512, temperature=0.7, top_p=0.9, do_sample=True
    )
    # 2. 使用奖励模型评分
    texts = [tokenizer.decode(r, skip_special_tokens=True) for r in response_tensors]
    rewards = [torch.tensor(reward_model.score(q, r)) for q, r in zip(batch["query"], texts)]
    # 3. PPO 更新（内部处理 KL、GAE、裁剪）
    stats = ppo_trainer.step(query_tensors, response_tensors, rewards)
    # 监控：stats["ppo/mean_scores"], stats["ppo/policy/approx_kl"]
\end{lstlisting}
```

## Critical Hyperparameters
## 关键超参数

\label{critical-hyperparameters}

\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Parameter} & \textbf{Typical} & \textbf{Effect of Getting It Wrong} \\
\midrule
\texttt{cliprange} & 0.2 & Too low: no learning. Too high: instability. \\
\texttt{init\_kl\_coef} & 0.01--0.1 & Too low: reward hacking. Too high: stuck at SFT. \\
\texttt{target\_kl} & 4--8 & Adaptive controller target. Lower = conservative. \\
\texttt{ppo\_epochs} & 4 & Too many: overfits to batch. Too few: wastes gen compute. \\
\texttt{learning\_rate} & $1{-}5 \times 10^{-6}$ & Too high: catastrophic forgetting. \\
\texttt{batch\_size} & 64--256 & Larger = smoother gradients, more gen compute. \\
\texttt{temperature} & 0.7--1.0 & Lower: less exploration. Higher: noisier advantages. \\
\bottomrule
\end{tabular}

\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{参数} & \textbf{典型值} & \textbf{参数设置错误的后果} \\
\midrule
\texttt{cliprange} & 0.2 & 过低：无法学习。过高：不稳定。 \\
\texttt{init\_kl\_coef} & 0.01--0.1 & 过低：奖励欺骗（reward hacking）。过高：停留在 SFT 阶段。 \\
\texttt{target\_kl} & 4--8 & 自适应控制器的目标值。越小越保守。 \\
\texttt{ppo\_epochs} & 4 & 过多：对批次过拟合。过少：浪费生成计算资源。 \\
\texttt{learning\_rate} & $1{-}5 \times 10^{-6}$ & 过高：灾难性遗忘。 \\
\texttt{batch\_size} & 64--256 & 越大：梯度越平滑，但生成计算量更大。 \\
\texttt{temperature} & 0.7--1.0 & 越低：探索越少。越高：优势估计噪声越大。 \\
\bottomrule
\end{tabular}