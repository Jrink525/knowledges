                           # 用于 token 加权所必需
    reward_funcs=[reward_fn],
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\begin{keybox}[When to Use Dr. GRPO]
\begin{itemize}
  \item When training on tasks with a large vocabulary mismatch between pretraining and RL.
  \item 当训练的任务在预训练和强化学习之间存在较大的词汇表不匹配时。
  \item When you observe that common filler tokens dominate the gradient.
  \item 当观察到常见的填充词主导梯度时。
  \item Pairs well with a reference model that is close to the initial policy.
  \item 与接近初始策略的参考模型配合良好。
\end{itemize}
\end{keybox}

## 2-GRPO -- Minimal Two-Rollout GRPO
## 2-GRPO —— 最小双生成 GRPO
\label{sec:2grpo}

\begin{intuitionbox}[“It Takes Two” Insight]
The ``It Takes Two'' paper~\cite{xu2025twograpo} demonstrates empirically and theoretically that GRPO with $G=2$ (just two completions per prompt) matches or exceeds GRPO with $G=16$ on most reasoning benchmarks. This is surprising -- why would fewer samples be sufficient?
\end{intuitionbox}
\begin{intuitionbox}[“二人成戏”洞察]
《It Takes Two》论文~\cite{xu2025twograpo} 从经验和理论上证明，在大多数推理基准上，$G=2$（每个提示仅两次补全）的 GRPO 匹配或超过 $G=16$ 的 GRPO。这令人惊讶——为什么更少的样本就足够了呢？
\end{intuitionbox}

The key insight is that GRPO’s effectiveness does \emph{not} primarily come from accurate advantage estimation (which requires large $G$). Instead, it comes from an implicit \emph{contrastive objective} that is structurally similar to DPO:
关键洞察在于，GRPO 的有效性主要并非来自精确的优势估计（这需要大的 $G$），而是来自一个与 DPO 结构相似的隐式 \emph{对比目标}：

\[
\mathcal{L}_{\text{2-GRPO}} \approx
  -\mathbb{E}_{(o^+, o^-) \sim \pi_\theta}\!\left[
    \log \sigma\!\left(
      \beta \log \frac{\pi_\theta(o^+|q)}{\pi_{\text{old}}(o^+|q)}
      - \beta \log \frac{\pi_\theta(o^-|q)}{\pi_{\text{old}}(o^-|q)}
    \right)
  \right],
\]

where $o^+$ is the higher-reward completion and $o^-$ the lower-reward one. With $G=2$, this contrastive structure is explicit. With $G=16$, the same signal is present but diluted by redundant pairs.
其中 $o^+$ 是高奖励补全，$o^-$ 是低奖励补全。当 $G=2$ 时，这种对比结构是显式的。当 $G=16$ 时，同样的信号存在但被冗余对稀释。

\begin{keybox}[Compute Savings from 2-GRPO]
\begin{itemize}
  \item $G=2$ vs $G=16$: \textbf{8$\times$ less generation compute}.
  \item $G=2$ 对比 $G=16$：\textbf{生成计算量减少 8 倍}。
  \item Generation is typically the bottleneck (60--80\% of wall-clock time).
  \item 生成通常是瓶颈（占挂钟时间的 60--80%）。
  \item Total training speedup: approximately 4--6$\times$ end-to-end.
  \item 总训练加速：端到端约 4--6 倍。
  \item No accuracy loss on GSM8K, MATH, and code benchmarks.
  \item 在 GSM8K、MATH 和代码基准上无精度损失。
\end{itemize}
\end{keybox}

\begin{examplebox}[2-GRPO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    num_generations=2,      # The key change -- just two rollouts
    loss_type="grpo",       # Standard GRPO loss is fine
    epsilon=0.2,
