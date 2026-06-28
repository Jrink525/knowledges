# 掩码 IS 校正
config_mis = GRPOConfig(
    use_vllm=True,
    vllm_importance_sampling_correction=True,
    vllm_importance_sampling_mode="sequence_mask",      # MIS
    vllm_importance_sampling_cap=3.0,
)
\end{lstlisting}
\end{examplebox}

\begin{keybox}[When to Use TIS/MIS]
\begin{itemize}
  \item \textbf{Always} consider enabling when using vLLM for generation.
  \item \textbf{始终}考虑在使用 vLLM 进行生成时启用。
  \item TIS is preferred when the mismatch is small (same model, different precision).
  \item 当不匹配较小时（相同模型，不同精度），首选 TIS。
  \item MIS is preferred when the mismatch is large or unpredictable.
  \item 当不匹配较大或不可预测时，首选 MIS。
  \item Sequence-level IS is theoretically preferred; token-level is a practical compromise.
  \item 序列级 IS 在理论上更优；token 级是实用的折衷方案。
\end{itemize}
\end{keybox}

## VESPO -- Variational Sequence-Level Soft Policy Optimization
## VESPO -- 变分序列级软策略优化

\label{sec:vespo}

\begin{intuitionbox}[Principled Reward Reshaping]
Most GRPO variants modify the clipping mechanism heuristically. VESPO derives a principled reward-reshaping kernel from a variational inference framework, treating policy optimisation as approximate posterior inference. VESPO~\cite{luo2025vespo} derives a resulting kernel that is smooth, asymmetric, and naturally handles staleness in asynchronous or off-policy training.
\end{intuitionbox}

\begin{intuitionbox}[基于原则的奖励重塑]
大多数 GRPO 变体启发式地修改裁剪机制。VESPO 从变分推理框架中推导出一个有原则的奖励重塑核，将策略优化视为近似后验推理。VESPO~\cite{luo2025vespo} 导出的核是平滑的、非对称的，并且自然地处理异步或离策略训练中的陈旧性。
\end{intuitionbox}

VESPO derives a weighting function $W(\tau)$ for each trajectory $\tau$ from the variational objective. The final gradient weight takes the form:

VESPO 从变分目标中为每个轨迹 $\tau$ 推导出一个加权函数 $W(\tau)$。最终的梯度权重形式如下：

\[
\boxed{
    g(\tau) = W(\tau)^k \cdot \exp\!\bigl(\lambda(1 - W(\tau))\bigr),
  }
\]

where $W(\tau) = \pi_\theta(\tau)/\pi_{\text{old}}(\tau)$ is the sequence-level importance weight, $k$ controls the sharpness of the weighting, and $\lambda$ controls the exponential decay for stale (low-weight) trajectories. This kernel:

其中 $W(\tau) = \pi_\theta(\tau)/\pi_{\text{old}}(\tau)$ 是序列级别的重要性权重，$k$ 控制加权的锐度，$\lambda$ 控制对陈旧（低权重）轨迹的指数衰减。该核：

\begin{itemize}
  \item Is smooth everywhere (no discontinuous gradient at clip boundaries).
  \item Naturally down-weights stale trajectories ($W \ll 1$) via the exponential term.
  \item Is asymmetric: high-weight trajectories ($W > 1$) are treated differently from low-weight ones.
\end{itemize}

\begin{itemize}
  \item 处处平滑（在裁剪边界处无梯度不连续）。
  \item 通过指数项自然地降低陈旧轨迹（$W \ll 1$）的权重。
  \item 非对称：高权重轨迹（$W > 1$）与低权重轨迹的处理方式不同。
\end{itemize}

\begin{examplebox}[VESPO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    loss_type="vespo",
    vespo_k_pos=2.0,         # sharpness exponent (positive advantages)
    vespo_lambda_pos=3.0,    # staleness decay (positive advantages)
    num_generations=8,
    steps_per_generation=2,  # off-policy; VESPO handles staleness
)


trainer = GRPOTrainer(
    model=model,
    reward_funcs=[reward_fn],
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[TRL 中的 VESPO]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    loss_type="vespo",
    vespo_k_pos=2.0,         # 锐度指数（正优势）
    vespo_lambda_pos=3.0,    # 陈旧性衰减（正优势）
    num_generations=8,
    steps_per_generation=2,  # 离策略；VESPO 处理陈旧性
)


trainer = GRPOTrainer(
    model=model,
    reward_funcs=[reward_fn],
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\subsection{DPPO -- Direct Policy Divergence Policy Optimization}
\subsection{DPPO -- 直接策略散度策略优化}

\label{sec:dppo}

\begin{intuitionbox}[The Problem with Ratio Clipping]
PPO's ratio clipping is a proxy for constraining the KL divergence between old and new policy. But the proxy is imperfect: clipping over-penalises low-probability tokens (where a small absolute change in probability corresponds to a large ratio change) and under-penalises high-probability tokens (where a large absolute change corresponds to a small ratio change). DPPO~\cite{an2025dppo} replaces ratio clipping with \emph{direct divergence estimates}.
\end{intuitionbox}

\begin{intuitionbox}[比率裁剪的问题]
PPO 的比率裁剪是约束新旧策略之间 KL 散度的一种代理。但该代理并不完美：裁剪过度惩罚了低概率 token（概率的微小绝对变化对应比率的巨大变化），而欠惩罚了高概率 token（概率的大幅绝对变化对应比率的微小变化）。DPPO~\cite{an2025dppo} 用 \emph{直接散度估计} 取代了比率裁剪。
\end{intuitionbox}

DPPO computes the trust region constraint directly using either Total Variation (TV) or KL divergence between the old and new policy distributions:

DPPO 直接使用新旧策略分布之间的总变差（TV）或 KL 散度来计算信任区域约束：

\[
\mathcal{L}_{\text{DPPO}} = -\mathbb{E}\!\left[
    \hat{A} \cdot \pi_\theta(o|q) \cdot \mathbf{1}[D(\pi_\theta \| \pi_{\text{old}}) \le \delta]
  \right],
\]

where $D$ is the chosen divergence measure. In practice, DPPO approximates this with token-level binary or top-$k$ masks:

其中 $D$ 是所选散度度量。在实践中，DPPO 通过 token 级别的二值掩码或 top-$k$ 掩码来近似：

\begin{itemize}
  \item \textbf{binary\_tv}: mask tokens where $|\pi_\theta - \pi_{\text{old}}| > \delta$.
  \item \textbf{binary\_kl}: mask tokens where $\pi_\theta \log(\pi_\theta/\pi_{\text{old}}) > \delta$.
  \item \textbf{topk\_tv}: keep only the top-$k$ tokens by TV contribution.
  \item \textbf{topk\_kl}: keep only the top-$k$ tokens by KL contribution.
\end{itemize}

\begin{itemize}
  \item \textbf{binary\_tv}: 掩码掉 $|\pi_\theta - \pi_{\text{old}}| > \delta$ 的 token。
  \item \textbf{binary\_kl}: 掩码掉 $\pi_\theta \log(\pi_\theta/\pi_{\text{old}}) > \delta$ 的 token。
  \item \textbf{topk\_tv}: 仅保留 TV 贡献最大的 top-$k$ 个 token。
  \item \textbf{topk\_kl}: 仅保留 KL 贡献最大的 top-$k$ 个 token。
\end{itemize}

\begin{examplebox}[DPPO – Conceptual Implementation]
DPPO is not yet available as a built-in TRL trainer. A custom implementation would use GRPOTrainer with a modified loss that clips based on distributional divergence (TV or KL) rather than the standard probability ratio:

\begin{lstlisting}[style=pythonstyle]
