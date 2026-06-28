# pi_new/pi_old 超过 [1-eps, 1+eps]
\end{lstlisting}
\end{examplebox}

\begin{warningbox}[DPPO is Research-Stage]
DPPO is a recent research contribution and is not yet integrated into mainstream RL libraries. It is most useful when you observe that standard ratio clipping is failing (e.g., on tasks with highly skewed token probability distributions).
\end{warningbox}

\begin{warningbox}[DPPO 处于研究阶段]
DPPO 是一项最新的研究贡献，尚未集成到主流 RL 库中。当你观察到标准比率裁剪失效时（例如，在 token 概率分布高度偏斜的任务上），它最为有用。
\end{warningbox}

\subsection{ScaleRL and CISPO}
\subsection{ScaleRL 与 CISPO}

\label{sec:scalerl-cispo}

\begin{intuitionbox}[Scaling Laws for RL]
The ScaleRL paper~\cite{luo2025scalerl} conducts a systematic study of what makes RL training for LLMs scale effectively. The key finding is that two modifications -- batch-level reward scaling and DAPO-style token-level loss -- together unlock strong performance at scale, while neither alone is sufficient. CISPO (Clipped IS Policy Optimization) is the resulting algorithm.
\end{intuitionbox}

\begin{intuitionbox}[RL 的缩放定律]
ScaleRL 论文~\cite{luo2025scalerl} 系统研究了使 LLM 的 RL 训练有效扩展的因素。关键发现是：两个修改——批次级别的奖励缩放和 DAPO 风格的 token 级别损失——共同在规模化下释放了强大性能，而单独任何一个都不足以实现。CISPO（裁剪的重要性采样策略优化，Clipped IS Policy Optimization）是最终得到的算法。
\end{intuitionbox}

\subsubsection*{Batch-Level Reward Scaling}
\subsubsection*{批次级别奖励缩放}

\label{batch-level-reward-scaling}

Standard GRPO normalises rewards within a group of $G$ completions for a single prompt. CISPO normalises rewards across the \emph{entire batch}:

标准 GRPO 对单个提示的一组 $G$ 个完成中的奖励进行归一化。而 CISPO 在 \emph{整个批次} 上对奖励进行归一化：

\[
\hat{A}_i = \frac{r_i - \mu_{\text{batch}}}{\sigma_{\text{batch}} + \epsilon},
\]

where $\mu_{\text{batch}}$ and $\sigma_{\text{batch}}$ are computed over all rewards in the current training batch. This provides a more stable baseline and prevents any single prompt from dominating the gradient.

其中 $\mu_{\text{batch}}$ 和 $\sigma_{\text{batch}}$ 是在当前训练批次中的所有奖励上计算的。这提供了更稳定的基线，并防止任何单个提示主导梯度。

\subsubsection*{CISPO Loss}
\subsubsection*{CISPO 损失}

\label{cispo-loss}

CISPO combines batch-level scaling with DAPO's token-level loss aggregation and asymmetric clipping:

CISPO 将批次级别缩放与 DAPO 的 token 级别损失聚合以及非对称裁剪相结合：

\[
\mathcal{L}_{\text{CISPO}} =
    -\frac{1}{\sum_{i,t} m_{i,t}}
    \sum_{i=1}^G \sum_{t=1}^{|o_i|} m_{i,t} \cdot
    \min\!\bigl(\rho_{i,t}\hat{A}_i,\;
               \mathrm{clip}_{\text{DAPO}}(\rho_{i,t},\hat{A}_i)\,\hat{A}_i\bigr),
\]

where $m_{i,t}$ is the overlong-filtering mask.

其中 $m_{i,t}$ 是超长过滤掩码。

\begin{examplebox}[CISPO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    loss_type="cispo",
    scale_rewards="batch",          # batch-level reward normalisation
    mask_truncated_completions=True,
    epsilon=0.2,
    epsilon_high=5.0,               # epsilon_max for CISPO (ScaleRL paper)
    num_generations=8,
)


trainer = GRPOTrainer(
    model=model,
    reward_funcs=[reward_fn],
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[TRL 中的 CISPO]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    loss_type="cispo",
    scale_rewards="batch",          # 批次级别奖励归一化
    mask_truncated_completions=True,
    epsilon=0.2,
    epsilon_high=5.0,               # CISPO 的 epsilon_max（ScaleRL 论文）
    num_generations=8,
)


trainer = GRPOTrainer(
    model=model,
    reward_funcs=[reward_fn],
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\begin{keybox}[ScaleRL Key Findings]
\begin{enumerate}
  \item Batch-level reward scaling alone: modest improvement.
  \item Token-level loss alone: modest improvement.
  \item Both together: \textbf{synergistic} -- significantly better than either alone.
  \item Larger batch sizes benefit more from batch-level scaling.
  \item CISPO is the recommended default for large-scale RL training.
\end{enumerate}
\end{keybox}

\begin{keybox}[ScaleRL 关键发现]
\begin{enumerate}
  \item 仅批次级别奖励缩放：适度改进。
  \item 仅 token 级别损失：适度改进。
  \item 两者结合：\textbf{协同} —— 显著优于单独的任一方法。
  \item 更大的批次大小从批次级别缩放中获益更多。
  \item CISPO 是大规模 RL 训练的推荐默认选项。
\end{enumerate}
\end{keybox}

\subsection{GDPO -- Group Reward-Decoupled Policy Optimization}
\subsection{GDPO -- 组奖励解耦策略优化}

\label{sec:gdpo}

\begin{intuitionbox}[The Multi-Reward Collapse Problem]
In multi-objective RL (e.g., optimising for both correctness and format), standard GRPO normalises the \emph{combined} reward. If one reward has much higher variance than another, it dominates the normalised advantage, effectively ignoring the other reward. This is \emph{advantage collapse}: the low-variance reward contributes near-zero gradient. GDPO~\cite{zhong2025gdpo} normalises each reward \emph{independently} before aggregating.
\end{intuitionbox}

\begin{intuitionbox}[多奖励崩溃问题]
在多目标 RL 中（例如，同时优化正确性和格式），标准 GRPO 对\emph{组合}奖励进行归一化。如果一个奖励的方差远高于另一个，它会主导归一化优势，实际上忽略了另一个奖励。这就是\emph{优势崩溃}：低方差奖励贡献近乎为零的梯度。GDPO~\cite{zhong2025gdpo} 在聚合之前\emph{独立地}归一化每个奖励。
\end{intuitionbox}

The core mechanism normalises each reward \emph{independently} before aggregating:

核心机制是在聚合之前\emph{独立地}归一化每个奖励：

\[
\boxed{
    \hat{A}_n^{(i)} = \frac{r_n^{(i)} - \mu_n}{\sigma_n + \epsilon}, \qquad
    \hat{A}^{(i)} = \sum_{n=1}^N w_n \hat{A}_n^{(i)},
  }
\]

where $r_n^{(i)}$ is the $n$-th reward for completion $i$, $\mu_n$ and $\sigma_n$ are the mean and standard deviation of reward $n$ within the group, and $w_n$ are user-specified weights.

其中 $r_n^{(i)}$ 是完成 $i$ 的第 $n$ 个奖励，$\mu_n$ 和 $\sigma_n$ 是该组内第 $n$ 个奖励的均值和标准差，$w_n$ 是用户指定的权重。

\begin{keybox}[GDPO vs Standard Multi-Reward GRPO（GDPO对比标准多奖励GRPO）]
\begin{itemize}
  \item \textbf{Standard}: $\hat{A}^{(i)} = \frac{\sum_n w_n r_n^{(i)} - \mu_{\text{combined}}}{\sigma_{\text{combined}}}$. High-variance rewards dominate.
  \item \textbf{标准方法}：$\hat{A}^{(i)} = \frac{\sum_n w_n r_n^{(i)} - \mu_{\text{combined}}}{\sigma_{\text{combined}}}$。高方差的奖励主导。
  \item \textbf{GDPO}: normalise each reward separately, then combine. Each reward contributes proportionally to its weight $w_n$.
  \item \textbf{GDPO}：分别对每个奖励进行归一化，然后组合。每个奖励按其权重 $w_n$ 成比例贡献。
  \item GDPO is essential when rewards have very different scales or variances.
  \item 当奖励的量纲或方差差异很大时，GDPO 是必不可少的。
\end{itemize}
\end{keybox}

\begin{examplebox}[GDPO in TRL（TRL中的GDPO）]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    multi_objective_aggregation="normalize_then_sum",
    reward_weights=[1.0, 0.5],   # weights for [correctness, format]  # [正确性, 格式]的权重
    num_generations=8,
)


def correctness_reward(completions, **kwargs):
    return [1.0 if is_correct(c) else 0.0 for c in completions]


def format_reward(completions, **kwargs):
    return [0.1 if has_good_format(c) else 0.0 for c in completions]


trainer = GRPOTrainer(
    model=model,
    reward_funcs=[correctness_reward, format_reward],
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}


\subsection{GOPO -- Group Ordinal Policy Optimization}
\subsection{GOPO —— 群体序数策略优化（Group Ordinal Policy Optimization）}
\label{gopo-group-ordinal-policy-optimization}


GOPO~\cite{choi2025gopo} starts from a simple observation: reward models are trained with pairwise comparisons (``is A better than B?''), so only the \textbf{rank order} of their outputs is trustworthy---the raw numeric scores carry no inherent meaning. Yet GRPO feeds those raw magnitudes directly into the advantage calculation. For tasks with non-verifiable rewards---summarization, open-ended chat, instruction following---this mismatch introduces noise, because a gap of 0.6 reward points might reflect genuine quality in one region of the output space and mean nothing in another.
GOPO~\cite{choi2025gopo} 从一个简单的观察出发：奖励模型是通过成对比较（“A比B更好吗？”）训练的，因此其输出的\textbf{排名顺序}才是可信的——原始的数值分数没有内在含义。然而 GRPO 却将这些原始量值直接用于优势计算。对于具有不可验证奖励的任务（摘要、开放对话、指令遵循），这种错配会引入噪声，因为 0.6 个奖励点的差距可能在输出空间的某个区域反映真实质量，在另一个区域却毫无意义。


\textbf{Key Insight}: Discard reward magnitudes entirely. Use only the \textbf{ordinal ranking} of rewards within a group.
\textbf{关键洞察}：完全丢弃奖励量值。只使用组内奖励的\textbf{序数排名}。


\textbf{Algorithm}: Given a group of $N$ responses $\{o_1, \ldots, o_N\}$ with rewards $\{r_1, \ldots, r_N\}$:
\textbf{算法}：给定一组 $N$ 个回复 $\{o_1, \ldots, o_N\}$ 及其奖励 $\{r_1, \ldots, r_N\}$：


\begin{enumerate}
  \item Rank responses by reward: assign rank $\text{rank}(o_i) \in \{1, \ldots, N\}$ (1 = worst, $N$ = best).
  \item 按奖励对回复排序：分配排名 $\text{rank}(o_i) \in \{1, \ldots, N\}$（1 表示最差，$N$ 表示最好）。
  \item Replace raw advantages with rank-based scores: 
  \item 用基于排名的分数替换原始优势：
\begin{equation}
\boxed{\hat{A}_i^{\text{GOPO}} = f\!\left(\frac{\text{rank}(o_i)}{N}\right)}
\end{equation}
 where $f$ is a monotonic transformation (e.g., linear mapping to $[-1, 1]$ or quantile normalization).
 其中 $f$ 是单调变换（例如线性映射到 $[-1, 1]$ 或分位数归一化）。
  \item Apply PPO-style clipped objective using rank-based advantages.
  \item 使用基于排名的优势应用 PPO 风格的裁剪目标。
\end{enumerate}


\textbf{Comparison with GRPO}:
\textbf{与 GRPO 的比较}：


\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Aspect} & \textbf{GRPO} & \textbf{GOPO} \\
\textbf{方面} & \textbf{GRPO} & \textbf{GOPO} \\
\midrule
Advantage signal & $\hat{A}_i = (r_i - \mu)/\sigma$ (uses magnitudes) & $\hat{A}_i = f(\text{rank}_i / N)$ (uses ordinal rank only) \\
优势信号 & $\hat{A}_i = (r_i - \mu)/\sigma$（使用量值） & $\hat{A}_i = f(\text{rank}_i / N)$（仅使用序数排名） \\
Sensitivity to reward scale & High --- miscalibrated RM scores distort advantages & None --- invariant to monotonic reward transformations \\
对奖励量纲的敏感性 & 高 —— 未校准的 RM 分数会扭曲优势 & 无 —— 对奖励的单调变换不变 \\
Best for & Verifiable rewards (binary, well-calibrated) & Non-verifiable rewards (RM-based, noisy magnitudes) \\
最适合 & 可验证奖励（二值、良好校准） & 不可验证奖励（基于 RM、量值有噪声） \\
\bottomrule
\end{tabular}


\textbf{Empirical gains} (over GRPO on non-verifiable tasks):
\textbf{实证收益}（在不可验证任务上相对于 GRPO）：


\begin{itemize}
  \item Reward curves (both training and held-out) sit above GRPO throughout optimization
  \item 奖励曲线（训练集和保留集）在整个优化过程中均位于 GRPO 之上
  \item Win-rates judged by a separate LLM evaluator improve at most training checkpoints
  \item 由独立 LLM 评估器判定的胜率在大多数训练检查点上有所提升
  \item Convergence is markedly faster---matching GRPO’s final quality with fewer gradient steps
  \item 收敛速度明显更快——用更少的梯度步数即可达到 GRPO 的最终质量
  \item The advantage grows as the reward model becomes noisier or more poorly calibrated
  \item 当奖励模型变得更嘈杂或校准更差时，优势会进一步增大
\end{itemize}


\begin{intuitionbox}[When to Use GOPO vs. GRPO（何时使用GOPO vs. GRPO）]
\begin{itemize}
  \item \textbf{Use GRPO}: When rewards are verifiable and exact (math correctness, code tests pass/fail, binary signals). Magnitudes carry meaningful information.
  \item \textbf{使用 GRPO}：当奖励是可验证且精确时（数学正确性、代码测试通过/失败、二值信号）。量值携带有意义的信息。
  \item \textbf{Use GOPO}: When rewards come from a learned reward model on subjective tasks (helpfulness, style, safety). The RM’s relative ordering is trustworthy but its absolute scores are arbitrary.
  \item \textbf{使用 GOPO}：当奖励来自针对主观任务（有用性、风格、安全性）学习的奖励模型时。RM 的相对排序是可信的，但其绝对分数是任意的。
\end{itemize}
\end{intuitionbox}
---

## Chapter Title
## 章节标题

## Preference Optimization Variants
## 偏好优化变体

\label{ch:po-variants}

This chapter covers the family of methods that extend or replace DPO with different objectives, data assumptions, or architectural trade-offs. Each addresses a specific limitation of standard offline DPO: distribution shift (Online DPO), the need for paired data (KTO), overfitting to noisy labels (IPO), reference model memory cost (ORPO), or training complexity (Best-of-N).

本章涵盖了一系列方法，它们通过不同的目标、数据假设或架构权衡来扩展或替代 DPO。每种方法都解决了标准离线 DPO 的特定局限性：分布偏移（Online DPO，在线 DPO）、对配对数据的需求（KTO，卡尼曼-特沃斯基优化）、对噪声标签的过拟合（IPO，身份偏好优化）、参考模型内存成本（ORPO）或训练复杂性（Best-of-N，最佳 N 个）。

\section{Online DPO}
\section{在线 DPO}

\label{sec:online-dpo}

\subsection{Motivation}
\subsection{动机}

\label{motivation}

Standard DPO’s primary limitation: the preference data was generated by a \emph{different} model (often an older checkpoint or even a different model family). As training progresses, the policy generates text that looks nothing like the training pairs $\rightarrow$ the loss is optimizing on an irrelevant distribution.

标准 DPO 的主要局限性：偏好数据是由一个\emph{不同的}模型生成的（通常是旧的检查点，甚至是不同的模型家族）。随着训练的进行，策略生成的文本与训练对截然不同 $\rightarrow$ 损失函数正在优化一个无关的分布。

\textbf{Online DPO solution}~\cite{guo2024direct}: Generate fresh preference pairs from the \emph{current} policy at every step, judge them with a reward model, then apply the DPO loss.

\textbf{在线 DPO 解决方案}~\cite{guo2024direct}：每一步从\emph{当前}策略生成新的偏好对，用奖励模型对它们进行评判，然后应用 DPO 损失。

\subsection{Algorithm}
\subsection{算法}

\label{algorithm}

\begin{enumerate}
  \item Generate $K$ responses per prompt from current $\pi_\theta$
  \item 从当前 $\pi_\theta$ 为每个提示生成 $K$ 个响应
  \item Score all responses with reward model $r_\phi$
  \item 使用奖励模型 $r_\phi$ 对所有响应进行评分
  \item Create pairs: highest-scoring = chosen, lowest-scoring = rejected
  \item 创建配对：最高得分 = 被选中的响应，最低得分 = 被拒绝的响应
  \item Apply DPO loss on these fresh pairs
  \item 在这些新生成的配对上应用 DPO 损失
  \item Repeat (new generation every step)
  \item 重复（每一步都进行新的生成）
\end{enumerate}

\begin{intuitionbox}[Online DPO = Best of Both Worlds]
\begin{intuitionbox}[在线 DPO = 两全其美]

\begin{itemize}
  \item From DPO: simple supervised loss, no value function, no GAE, stable optimization
  \item 来自 DPO：简单的监督损失，无价值函数，无 GAE，优化稳定
  \item From PPO: on-policy data, self-improvement beyond dataset, no distribution shift
  \item 来自 PPO：在线策略数据，超越数据集的自我改进，无分布偏移
  \item Key difference from GRPO: uses DPO loss (pair-based) instead of PPO loss (per-sample advantage)
  \item 与 GRPO 的关键区别：使用 DPO 损失（基于配对）而非 PPO 损失（每个样本的优势）
\end{itemize}

\textbf{Trade-off}: Needs a reward model (DPO doesn’t), but no value head (PPO does). Middle ground complexity.
\textbf{权衡}：需要奖励模型（DPO 不需要），但无需价值头（PPO 需要）。复杂度折中。
\end{intuitionbox}

\subsection{TRL Implementation}
\subsection{TRL 实现}

\label{trl-implementation}

The following shows a minimal working example using HuggingFace TRL.
以下展示了使用 HuggingFace TRL 的最小工作示例。

\begin{lstlisting}[style=pythonstyle]
from trl import OnlineDPOConfig, OnlineDPOTrainer
from transformers import AutoModelForCausalLM, AutoModelForSequenceClassification

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B-Instruct",
    torch_dtype=torch.bfloat16)
reward_model = AutoModelForSequenceClassification.from_pretrained(
    "RLHFlow/ArmoRM-Llama3-8B-v0.1", torch_dtype=torch.bfloat16)

online_dpo_config = OnlineDPOConfig(
    output_dir="./online_dpo_output",
    learning_rate=5e-7,
    beta=0.1,                    # DPO beta (same meaning as standard DPO)
