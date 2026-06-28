    # 当 G=2 时，batch size 必须至少为 num_prompts_per_step * 2
    per_device_train_batch_size=2,
)


trainer = GRPOTrainer(
    model=model,
    reward_funcs=[reward_fn],
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\begin{warningbox}[Caveats of 2-GRPO]
With $G=2$, advantage normalisation is over only two values, so the normalised advantages are always $\{+1, -1\}$ (or $\{0, 0\}$ if rewards are equal). This means the gradient magnitude is fixed regardless of the reward gap. For tasks where the \emph{magnitude} of the reward difference matters (e.g., partial credit), larger $G$ may still be beneficial.
\end{warningbox}
\begin{warningbox}[2-GRPO 的注意事项]
当 $G=2$ 时，优势归一化仅针对两个值，因此归一化后的优势始终为 $\{+1, -1\}$（如果奖励相等则为 $\{0, 0\}$）。这意味着梯度大小固定，不受奖励差距影响。对于奖励差异的 \emph{幅度} 重要的任务（例如部分得分），更大的 $G$ 可能仍然有益。
\end{warningbox}

## SAPO -- Soft Adaptive Policy Optimization
## SAPO —— 软自适应策略优化
\label{sec:sapo}

\begin{intuitionbox}[The Brittleness of Hard Clipping]
PPO-style clipping creates a discontinuous gradient: the gradient is zero outside the clip band and non-zero inside. This ``cliff edge'' can cause instability near the boundary and makes the trust region sensitive to the choice of $\epsilon$. SAPO~\cite{han2025sapo} replaces the hard clip with a smooth, temperature-controlled gate function.
\end{intuitionbox}
\begin{intuitionbox}[硬裁剪的脆弱性]
PPO（近端策略优化）风格的裁剪会产生不连续的梯度：裁剪带之外梯度为零，之内非零。这种“悬崖边缘”会在边界附近导致不稳定，并使信任区域对 $\epsilon$ 的选择敏感。SAPO~\cite{han2025sapo} 用平滑的、温度控制的门控函数替代了硬裁剪。
\end{intuitionbox}

SAPO replaces the $\min(\rho A, \mathrm{clip}(\rho,\cdot)\,A)$ objective with a smooth surrogate:
SAPO 将 $\min(\rho A, \mathrm{clip}(\rho,\cdot)\,A)$ 目标替换为平滑的替代函数：

\[
\boxed{
    \mathcal{L}_{\text{SAPO}}(\rho, A) =
    \begin{cases}
      -A \cdot \sigma\!\left(\dfrac{\rho - 1}{\tau_+}\right) \cdot \rho
        & \text{if } A > 0 \\[8pt]
      -A \cdot \sigma\!\left(\dfrac{1 - \rho}{\tau_-}\right) \cdot \rho
        & \text{if } A \le 0
    \end{cases}
  }
\]

where $\sigma$ is the sigmoid function and $\tau_+, \tau_-$ are asymmetric temperature parameters. A higher temperature produces a softer gate (more exploration); a lower temperature approaches hard clipping.
其中 $\sigma$ 是 Sigmoid 函数，$\tau_+, \tau_-$ 是非对称温度参数。温度越高产生越软的门控（更多探索）；温度越低则趋近于硬裁剪。

\begin{keybox}[SAPO Temperature Intuition]
\begin{itemize}
  \item $\tau_+ = 1.0$: moderate gate for positive advantages (allow exploration).
  \item $\tau_+ = 1.0$：对正优势的适中门控（允许探索）。
  \item $\tau_- = 1.05$: slightly softer gate for negative advantages (avoid over-suppression).
  \item $\tau_- = 1.05$：对负优势的稍软门控（避免过度抑制）。
  \item As $\tau \to 0$: recovers hard PPO clipping.
  \item 当 $\tau \to 0$ 时：恢复硬 PPO 裁剪。
  \item As $\tau \to \infty$: recovers unclipped policy gradient.
  \item 当 $\tau \to \infty$ 时：恢复未裁剪的策略梯度。
\end{itemize}
\end{keybox}

\begin{examplebox}[SAPO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    loss_type="sapo",
    sapo_temperature_pos=1.0,    # tau_+ for positive advantages
    sapo_temperature_neg=1.05,   # tau_- for negative advantages
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
\begin{examplebox}[TRL 中的 SAPO]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    loss_type="sapo",
    sapo_temperature_pos=1.0,    # 正优势的 tau_+
    sapo_temperature_neg=1.05,   # 负优势的 tau_-
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

## TIS and MIS -- Truncated and Masked Importance Sampling
## TIS 与 MIS —— 截断与掩码重要性采样
\label{sec:tis-mis}

\begin{warningbox}[The Silent vLLM Probability Mismatch]
When using vLLM for fast generation, the log-probabilities returned by vLLM differ from those computed during the training forward pass~\cite{zhong2025tismis}. This is \emph{not} a bug -- it arises from different CUDA kernels, different floating-point precision, and different attention implementations (e.g., FlashAttention vs PagedAttention). The mismatch silently breaks the on-policy assumption: the ``old policy'' probabilities used to compute importance ratios are wrong, leading to biased gradient estimates.
\end{warningbox}
\begin{warningbox}[无声的 vLLM 概率不匹配]
当使用 vLLM 进行快速生成时，vLLM 返回的对数概率与训练前向传播期间计算的对数概率不同~\cite{zhong2025tismis}。这\emph{不是}一个 bug——它源于不同的 CUDA 内核、不同的浮点精度以及不同的注意力实现（例如 FlashAttention 与 PagedAttention）。这种不匹配静默地破坏了同策略假设：用于计算重要性比率的“旧策略”概率是错误的，导致有偏的梯度估计。
\end{warningbox}

## Truncated Importance Sampling (TIS)
## 截断重要性采样 (TIS)
\label{truncated-importance-sampling-tis}

TIS corrects the bias by multiplying the gradient by a truncated correction factor:
TIS 通过将梯度乘以截断的校正因子来校正偏差：

\[
\boxed{
    w_{\text{TIS}}(o_i) = \min\!\left(C,\; \frac{\pi_{\text{train}}(o_i|q)}{\pi_{\text{vllm}}(o_i|q)}\right),
  }
\]

where $\pi_{\text{train}}$ is the probability from the training forward pass and $\pi_{\text{vllm}}$ is the probability reported by vLLM. The truncation at $C$ prevents extreme corrections from destabilising training.
其中 $\pi_{\text{train}}$ 是训练前向传播的概率，$\pi_{\text{vllm}}$ 是 vLLM 报告的概率。在 $C$ 处截断可防止极端的校正破坏训练稳定性。

## Masked Importance Sampling (MIS)
## 掩码重要性采样 (MIS)
\label{masked-importance-sampling-mis}

MIS takes a harder approach: it zeros out the gradient for any sequence where the correction ratio exceeds a threshold $C$:
MIS 采用更严格的方法：它将校正比率超过阈值 $C$ 的任何序列的梯度置零：

\[
w_{\text{MIS}}(o_i) = \mathbf{1}\!\left[\frac{\pi_{\text{train}}(o_i|q)}{\pi_{\text{vllm}}(o_i|q)} \le C\right].
\]

This is more conservative but avoids the risk of large (even truncated) correction weights.
这更加保守，但避免了大的（即使是截断的）校正权重的风险。

## Sequence-Level vs Token-Level IS
## 序列级与 Token 级重要性采样
\label{sequence-level-vs-token-level-is}

Both TIS and MIS can be applied at the token level or the sequence level:
TIS 和 MIS 都可以在 token 级或序列级应用：

\begin{itemize}
  \item \textbf{Sequence-level}: compute the ratio as the geometric mean over all tokens (as in GSPO). Theoretically correct but higher variance.
  \item \textbf{序列级}：将比率计算为所有 token 的几何均值（如 GSPO 中）。理论上正确但方差较高。
  \item \textbf{Token-level}: compute a separate ratio for each token. Biased (the product of per-token corrections is not the sequence correction) but lower variance.
  \item \textbf{Token 级}：为每个 token 计算单独的比率。有偏（逐 token 校正的乘积不是序列校正）但方差较低。
\end{itemize}

\begin{examplebox}[TIS and MIS in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


