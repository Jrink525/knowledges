# 训练立即继续；仅在需要时调用 future.result() 阻塞
\end{lstlisting}


\begin{keybox}[Checkpoint Hygiene for RLHF]
\begin{keybox}[RLHF的检查点卫生]
RLHF checkpoints must capture \emph{more} than standard pre-training:
RLHF检查点必须捕获比标准预训练 \emph{更多} 的内容：


\begin{itemize}
  \item Policy model weights + optimizer states (standard)
  \item 策略模型权重 + 优化器状态（标准）
  \item KL coefficient ($\beta$) and its schedule state
  \item KL系数 ($\beta$) 及其调度状态
  \item Replay buffer contents (for off-policy corrections)
  \item 回放缓冲区内容（用于离策略校正）
  \item RNG states for all GPUs (reproducibility)
  \item 所有GPU的随机数生成器状态（可复现性）
  \item Prompt iterator position (avoid re-processing prompts)
  \item 提示迭代器位置（避免重复处理提示）
  \item Reward model version tag (for auditability)
  \item 奖励模型版本标签（用于可审计性）
  \item Wandb/metrics run ID (for continuous logging)
  \item Wandb/指标运行ID（用于持续日志记录）
\end{itemize}
\end{keybox}


\section{Hardware Selection Guide}
\section{硬件选择指南}
\label{sec:hardware-guide}


Choosing the right hardware depends on model size, budget, and training phase.
选择合适的硬件取决于模型规模、预算和训练阶段。


\begin{table}[ht!]
\centering
\caption{Hardware recommendations by model scale and training phase}
\caption{按模型规模和训练阶段的硬件推荐}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{Model Size} & \textbf{Training Phase} & \textbf{Recommended} & \textbf{Configuration} \\
\textbf{模型规模} & \textbf{训练阶段} & \textbf{推荐硬件} & \textbf{配置} \\
\midrule
$\leq$7B & SFT + RLHF & 1--2$\times$ A100 & Single node, no parallelism needed \\
$\leq$7B & SFT + RLHF & 1--2$\times$ A100 & 单节点，无需并行 \\
7--13B & SFT + RLHF & 4--8$\times$ A100 & FSDP, optional TP=2 for gen \\
7--13B & SFT + RLHF & 4--8$\times$ A100 & FSDP，可选TP=2用于生成 \\
13--34B & SFT + RLHF & 8--16$\times$ A100/H100 & FSDP + TP=4 for gen \\
13--34B & SFT + RLHF & 8--16$\times$ A100/H100 & FSDP + TP=4用于生成 \\
70B & RLHF (full) & 32--64$\times$ A100/H100 & Decoupled, FSDP + TP=8 \\
70B & RLHF（完整） & 32--64$\times$ A100/H100 & 解耦，FSDP + TP=8 \\
70B & RLHF (LoRA) & 8--16$\times$ A100/H100 & No ref model, LoRA adapters \\
70B & RLHF（LoRA） & 8--16$\times$ A100/H100 & 无参考模型，LoRA适配器 \\
$>$100B & RLHF & 128+$\times$ H100 & 3D parallelism (TP+PP+DP) \\
$>$100B & RLHF & 128+$\times$ H100 & 3D并行（TP+PP+DP） \\
\bottomrule
\end{tabular}
\end{table}


\begin{intuitionbox}[H100 vs A100: When is the Upgrade Worth It?]
\begin{intuitionbox}[H100 vs A100：什么时候升级值得？]
H100 provides:
H100提供：


\begin{itemize}
  \item $\sim$1.6$\times$ peak FLOPS (989 vs 624 TFLOPS for BF16 with sparsity; 495 vs 312 without sparsity)
  \item $\sim$1.6$\times$峰值FLOPS（有稀疏性时BF16为989 vs 624 TFLOPS；无稀疏性时495 vs 312）
  \item $\sim$2$\times$ memory bandwidth (3.35 vs 2.0 TB/s)
  \item $\sim$2$\times$内存带宽（3.35 vs 2.0 TB/s）
  \item FP8 support (additional 2$\times$ for inference)
  \item FP8支持（推理时额外2倍）
  \item NVLink 4.0 (900 vs 600 GB/s)
  \item NVLink 4.0（900 vs 600 GB/s）
\end{itemize}


\textbf{For training}: $\sim$1.8--2.2$\times$ faster end-to-end (FP8 support and higher bandwidth amplify the raw FLOPS advantage).
\textbf{训练方面}：端到端速度提升约1.8--2.2倍（FP8支持和更高带宽放大了原始FLOPS优势）。


\textbf{For generation}: $\sim$1.7$\times$ faster (bandwidth-bound, so 2$\times$ BW $\approx$ 1.7$\times$ throughput with overhead).
\textbf{生成方面}：速度提升约1.7倍（受带宽限制，因此2倍带宽带来约1.7倍吞吐量，考虑开销后）。


\textbf{Cost-performance}: At 1.5$\times$ the price, H100 is almost always better value for training. For inference-only (generation clusters), A100 at spot pricing can be more cost-effective.
\textbf{性价比}：在价格1.5倍的情况下，H100在训练时几乎总是更划算。对于纯推理（生成集群），使用竞价价格的A100可能更具成本效益。
\end{intuitionbox}


\section{Optimizer Configuration for RL Training}
\section{RL训练的优化器配置}
\label{sec:rl-optimizer-config}


RL training (PPO, GRPO, DPO) imposes unique demands on the optimizer compared to pretraining or SFT. The loss landscape is non-stationary (the policy changes what data is generated), gradients are noisier (reward signal variance), and training is more prone to catastrophic forgetting or reward hacking. This section consolidates RL-specific optimizer guidance, using AdamW~\cite{loshchilov2019adamw} as the default optimizer.
与预训练或SFT相比，RL训练（PPO、GRPO、DPO）对优化器提出了独特的要求。损失景观是非平稳的（策略改变了生成的数据），梯度噪声更大（奖励信号方差），训练更容易出现灾难性遗忘或奖励破解。本节总结了RL特定的优化器指南，使用AdamW~\cite{loshchilov2019adamw}作为默认优化器。


\subsection{Why RL Requires Different Optimizer Settings}
\subsection{为什么RL需要不同的优化器设置}
\label{why-rl-requires-different-optimizer-settings}


\begin{keybox}[RL vs. SFT Optimization – Key Differences]
\begin{keybox}[RL与SFT优化——关键差异]
\begin{itemize}
  \item \textbf{Non-stationary data distribution}: unlike SFT where the dataset is fixed, RL generates new rollouts each iteration---the data distribution shifts with the policy.
  \item \textbf{非平稳数据分布}：与数据集固定的SFT不同，RL每次迭代生成新的轨迹——数据分布随策略变化。
  \item \textbf{High gradient variance}: reward signals are sparse and noisy; gradients have much higher variance than cross-entropy on curated data.
  \item \textbf{高梯度方差}：奖励信号稀疏且有噪声；梯度方差远高于在精心整理的数据上计算交叉熵时的方差。
  \item \textbf{Smaller updates required}: the policy must stay close to the reference model (KL constraint), so learning rates are 10--100$\times$ smaller than SFT.
  \item \textbf{需要更小的更新量}：策略必须保持接近参考模型（KL约束），因此学习率比SFT小10--100倍。
  \item \textbf{No weight decay}: regularization comes from the KL penalty, not weight decay. Adding WD on top can fight the KL constraint.
  \item \textbf{无权重衰减}：正则化来自KL惩罚，而非权重衰减。额外添加权重衰减可能与KL约束冲突。
  \item \textbf{Shorter warmup}: RL starts from a converged SFT checkpoint---the optimizer state needs minimal warmup.
  \item \textbf{更短的预热}：RL从已收敛的SFT检查点开始——优化器状态只需极少的预热。
\end{itemize}
\end{keybox}


\subsection{Recommended Hyperparameters by RL Method}
\subsection{按RL方法推荐超参数}
\label{recommended-hyperparameters-by-rl-method}


\begin{table}[ht!]
\centering
\caption{Optimizer settings for RL training phases. All use $\beta_1=0.9$, $\beta_2=0.95$, $\epsilon=10^{-8}$, \texttt{max\_grad\_norm}=1.0, BF16.}
\caption{RL训练阶段的优化器设置。所有设置均使用 $\beta_1=0.9$，$\beta_2=0.95$，$\epsilon=10^{-8}$，\texttt{max\_grad\_norm}=1.0，BF16。}
{\footnotesize
\begin{tabular}{@{}llllll@{}}
\toprule
\textbf{Method} & \textbf{Optimizer} & \textbf{LR} & \textbf{WD} & \textbf{Warmup} & \textbf{Schedule} \\
\textbf{方法} & \textbf{优化器} & \textbf{学习率} & \textbf{权重衰减} & \textbf{预热步数} & \textbf{调度策略} \\
\midrule
DPO & AdamW & $5\text{e-}7$ & 0.0 & 50 steps & Constant or Linear \\
DPO & AdamW & $5\text{e-}7$ & 0.0 & 50步 & 常数或线性 \\
PPO (policy) & AdamW & $1\text{e-}6$ & 0.0 & 20 steps & Constant \\
PPO（策略） & AdamW & $1\text{e-}6$ & 0.0 & 20步 & 常数 \\
PPO (critic) & AdamW & $1\text{e-}6$ & 0.0 & 20 steps & Constant \\
PPO（评论家） & AdamW & $1\text{e-}6$ & 0.0 & 20步 & 常数 \\
GRPO & AdamW & $1\text{e-}6$ & 0.0 & 20 steps & Constant \\
GRPO & AdamW & $1\text{e-}6$ & 0.0 & 20步 & 常数 \\
\bottomrule
\end{tabular}
}
\end{table}


\begin{intuitionbox}[Why Constant Schedule for RL?]
\begin{intuitionbox}[为什么RL使用常数调度？]
Cosine and linear-decay schedules assume a fixed training horizon and monotonically decreasing loss. RL training has neither: reward may plateau, spike, or oscillate unpredictably. A constant LR (after brief warmup) keeps the optimizer responsive throughout training. If you must decay, use a very gentle linear schedule with a high minimum LR ratio ($\geq 0.5$).
余弦和线性衰减调度假设固定的训练步数和单调递减的损失。RL训练两者都不具备：奖励可能停滞、突增或不可预测地振荡。常数学习率（经过短暂预热后）使优化器在整个训练过程中保持响应。如果必须衰减，请使用非常平缓的线性调度，并设置较高的最小学习率比例（$\geq 0.5$）。
\end{intuitionbox}

## Beta-2 = 0.95 for RL: Faster Adaptation
## 强化学习中 Beta-2 = 0.95：更快的自适应

The default Adam $\beta_2 = 0.999$ gives a very long memory for the second moment ($\sim$1000-step effective window). In RL training, the loss landscape changes rapidly as the policy evolves---the gradient variance from 1000 steps ago is irrelevant. Using $\beta_2 = 0.95$ shortens the window to $\sim$20 steps, making the adaptive learning rate respond quickly to changing gradient statistics.
默认的 Adam $\beta_2 = 0.999$ 为二阶矩提供了非常长的记忆（有效窗口约为 1000 步）。在强化学习训练中，损失函数地形随着策略的演化而快速变化——1000 步之前的梯度方差已无关紧要。使用 $\beta_2 = 0.95$ 可将窗口缩短至约 20 步，使自适应学习率能够快速响应变化的梯度统计量。

\begin{warningbox}[When beta2 = 0.95 Hurts]
\begin{warningbox}[何时 beta2 = 0.95 会造成损害]
For very small batch sizes (e.g., batch=1 in online RL), $\beta_2 = 0.95$ can make the second moment estimates too noisy. In this regime, use $\beta_2 = 0.99$ as a compromise, or increase the effective batch size via gradient accumulation.
对于非常小的批次大小（例如在线 RL 中 batch=1），$\beta_2 = 0.95$ 会使二阶矩估计过于嘈杂。在这种情况下，作为一种折中方案使用 $\beta_2 = 0.99$，或者通过梯度累积增加有效批次大小。
\end{warningbox}

## Mixed Precision for RL: FP32 Master Weights Are Critical
## 强化学习中的混合精度：FP32 主权重至关重要

RL training is particularly sensitive to numerical precision:
强化学习训练对数值精度特别敏感：

\begin{itemize}
  \item Gradients are noisier---small updates must accumulate accurately over many steps
  \item 梯度更嘈杂——小的更新必须在多步中精确累积
  \item Learning rates are very small ($10^{-6}$--$10^{-7}$), making $\Delta\theta \ll \theta$
  \item 学习率非常小（$10^{-6}$--$10^{-7}$），使得 $\Delta\theta \ll \theta$
  \item BF16 mantissa (7 bits $\approx$ 0.8\% relative precision) cannot represent updates of magnitude $10^{-6}$ relative to weights of magnitude $10^{0}$
  \item BF16 的尾数（7 位，相对精度约 0.8%）无法表示相对于量级为 $10^{0}$ 的权重量级为 $10^{-6}$ 的更新
\end{itemize}

\textbf{Always use FP32 master weights for RL training.} BF16-only training (no FP32 copy) reliably causes reward collapse in PPO/GRPO after 100--500 steps.
\textbf{始终在强化学习训练中使用 FP32 主权重。} 纯 BF16 训练（无 FP32 副本）在 PPO/GRPO 中 100-500 步后必然导致奖励崩溃。

## Gradient Clipping is Critical for RL
## 梯度裁剪对强化学习至关重要

In PPO and GRPO, the reward signal can be highly variable, especially early in training. A single bad batch can produce gradients with norm $>100$, which would completely destroy the model weights. \texttt{max\_grad\_norm=1.0} is the standard setting. For SFT, clipping is less critical but still recommended.
在 PPO 和 GRPO 中，奖励信号可能高度可变，尤其是在训练早期。单个坏批次可能产生范数 $>100$ 的梯度，这会完全破坏模型权重。\texttt{max\_grad\_norm=1.0} 是标准设置。对于 SFT，裁剪不那么关键但仍推荐使用。

\begin{warningbox}[Never Disable Gradient Clipping for RL]
\begin{warningbox}[切勿在强化学习中禁用梯度裁剪]
Unlike SFT where gradient norms are typically stable (0.1--1.0 range), RL gradients are spiky because: (1)~reward variance propagates through the policy gradient, (2)~rare high-reward trajectories create outsized updates, and (3)~the KL penalty term can produce large gradients when the policy drifts. A single unclipped step with $\|\nabla\| > 50$ can undo hundreds of training steps.
与 SFT 中梯度范数通常稳定（0.1-1.0 范围）不同，RL 梯度呈尖峰状，因为：(1) 奖励方差通过策略梯度传播；(2) 罕见的高奖励轨迹会产生过大的更新；(3) 当策略漂移时，KL 惩罚项可能产生大的梯度。一个未裁剪的 $\|\nabla\| > 50$ 的单步可以抵消数百步的训练。
\end{warningbox}

## Diagnosing RL Training Instability
## 诊断强化学习训练不稳定性

\begin{examplebox}[Red Flags and Fixes for RL Optimization]
\begin{examplebox}[强化学习优化的危险信号与修复措施]
{\small
\begin{tabular}{@{}lp{9.5cm}@{}}
\toprule
\textbf{Symptom} & \textbf{Likely Cause and Fix} \\
\textbf{症状} & \textbf{可能原因与修复} \\
\midrule
Reward improves then collapses & LR too high or KL coefficient too low. Reduce LR by 2--5$\times$ or increase $\beta_\text{KL}$. \\
奖励提升后崩溃 & 学习率过高或 KL 系数过低。将学习率降低 2-5 倍或增加 $\beta_\text{KL}$。 \\
Gradient norm constantly at clip threshold & Updates too aggressive. Reduce LR (clipping means you’re losing gradient direction info every step). \\
梯度范数持续处于裁剪阈值 & 更新过于激进。降低学习率（裁剪意味着每一步都在丢失梯度方向信息）。 \\
KL divergence explodes ($>$15 nats) & LR too high. Reduce by 10$\times$ or add adaptive KL penalty. \\
KL 散度爆炸（$>$15 nats） & 学习率过高。降低 10 倍或添加自适应 KL 惩罚。 \\
Reward stuck at baseline & LR too low, or reward model has low signal. Try 2--5$\times$ higher LR. Check reward model calibration. \\
奖励停滞在基线 & 学习率过低，或奖励模型信号弱。尝试将学习率提高 2-5 倍。检查奖励模型校准。 \\
Loss NaN after 100+ steps & FP32 master weights missing, or grad norm overflow. Enable FP32 master weights; verify BF16 mode. \\
100 步后损失 NaN & FP32 主权重缺失，或梯度范数溢出。启用 FP32 主权重；检查 BF16 模式。 \\
\bottomrule
\end{tabular}
}
\end{examplebox}

## HuggingFace TRL Configuration for RL
## 用于强化学习的 HuggingFace TRL 配置

The TRL library~\cite{vonwerra2022trl} provides production-ready implementations of PPO, DPO, and other RL methods for LLMs.
TRL 库~\cite{vonwerra2022trl} 为 LLM 提供了 PPO、DPO 以及其他 RL 方法的生产级实现。

\begin{lstlisting}[style=pythonstyle, caption={Complete PPO and DPO optimizer configuration using TRL.}]
\begin{lstlisting}[style=pythonstyle, caption={使用 TRL 的完整 PPO 和 DPO 优化器配置。}]
from trl import PPOConfig, PPOTrainer, DPOConfig, DPOTrainer


