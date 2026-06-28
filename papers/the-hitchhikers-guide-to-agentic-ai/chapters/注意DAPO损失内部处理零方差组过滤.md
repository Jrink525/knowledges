    # 注意：DAPO损失内部处理零方差组过滤
)

trainer = GRPOTrainer(
    model=model,
    reward_funcs=[reward_fn],
    args=config,
    train_dataset=dataset,
)
trainer.train()
\end{lstlisting}
\end{examplebox}

\begin{keybox}[When to Use DAPO]
\begin{itemize}
  \item Long-form reasoning tasks where completions frequently hit the length limit.
  \item 长形式推理任务，其中完成频繁达到长度限制。
  \item Any setting where you observe reward variance collapsing mid-training.
  \item 任何观察到奖励方差在训练中途崩溃的设置。
  \item When base GRPO shows instability (loss spikes, entropy collapse).
  \item 当基础GRPO显示不稳定性（损失尖峰、熵崩溃）时。
  \item Recommended as a \emph{drop-in improvement} over base GRPO for most tasks.
  \item 推荐作为大多数任务中基础GRPO的**即插即用改进**。
\end{itemize}
\end{keybox}

\subsection{GSPO -- Group Sequence Policy Optimization}
\subsection{GSPO -- 分组序列策略优化}
\label{sec:gspo}

\begin{intuitionbox}[The Off-Policy Problem]
GRPO clips importance ratios \emph{per token}. But a sequence of 500 tokens can have a product of per-token ratios that is astronomically large or small, even if each individual ratio is within $[1-\epsilon, 1+\epsilon]$. When training for multiple gradient steps on the same batch (off-policy), this mismatch grows rapidly and the clipping bound becomes meaningless at the sequence level.
GRPO 对**每个 token** 进行重要性比率裁剪。但是一个包含 500 个 token 的序列，其每个 token 比率的乘积可能大得惊人或小得惊人，即使每个单独的比率都在 $[1-\epsilon, 1+\epsilon]$ 范围内。当在同一个批次上进行多个梯度步的训练时（离策略），这种不匹配会迅速增长，裁剪边界在序列级别变得毫无意义。
\end{intuitionbox}

GSPO~\cite{chen2025gspo} defines a \emph{sequence-level} importance weight as the geometric mean of per-token ratios, which equals the $|o_i|$-th root of the full sequence probability ratio:
GSPO~\cite{chen2025gspo} 将**序列级**重要性权重定义为每个 token 比率的几何平均值，等于完整序列概率比的 $|o_i|$ 次根：

\[
\boxed{
    s_i(\theta) = \left(\frac{\pi_\theta(o_i \mid q)}{\pi_{\text{old}}(o_i \mid q)}\right)^{1/|o_i|}
    = \exp\!\left(\frac{1}{|o_i|}\sum_{t=1}^{|o_i|} \log \frac{\pi_\theta(o_{i,t}|q,o_{i,<t})}{\pi_{\text{old}}(o_{i,t}|q,o_{i,<t})}\right).
  }
\]

This is the \emph{length-normalised} sequence probability ratio. The GSPO loss clips this single scalar per sequence:
这就是**长度归一化**的序列概率比。GSPO 损失对每个序列的这个单一标量进行裁剪：

\[
\mathcal{L}_{\text{GSPO}} = -\frac{1}{G}\sum_{i=1}^G
    \min\!\Bigl(s_i(\theta)\,\hat{A}_i,\;
               \mathrm{clip}(s_i(\theta),1{-}\epsilon,1{+}\epsilon)\,\hat{A}_i\Bigr).
\]

\begin{keybox}[GSPO vs GRPO Clipping]
\begin{itemize}
  \item \textbf{GRPO}: clips each of the $|o_i|$ per-token ratios independently. A sequence can have all ratios within bounds yet have a product ratio of $10^{50}$.
  \item **GRPO**：独立裁剪每个 $|o_i|$ 个 token 比率。一个序列可能所有比率都在界限内，但乘积比率却达到 $10^{50}$。
  \item \textbf{GSPO}: clips the geometric mean once per sequence. Guarantees the \emph{sequence-level} policy shift is bounded.
  \item **GSPO**：每个序列只裁剪一次几何平均值。保证**序列级**策略偏移是有界的。
  \item GSPO is theoretically correct for off-policy IS; GRPO is an approximation.
  \item GSPO 在理论上对于离策略重要性采样是正确的；GRPO 是一种近似。
\end{itemize}
\end{keybox}

\begin{examplebox}[GSPO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer

config = GRPOConfig(
