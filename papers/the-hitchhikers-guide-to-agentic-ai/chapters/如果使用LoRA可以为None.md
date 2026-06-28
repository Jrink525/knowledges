    # 如果使用 LoRA 可以为 None
    args=kto_config,
    train_dataset=kto_dataset,
    tokenizer=tokenizer,
)
trainer.train()
\end{lstlisting}

\subsection{When to Choose KTO}
\subsection{何时选择 KTO}

\label{when-to-choose-kto}

\begin{itemize}
  \item You have binary feedback but \emph{not} matched pairs
  \item 你有二元反馈，但\emph{没有}匹配的配对
  \item Production thumbs-up/down data at scale
  \item 大规模生产环境中的点赞/点踩数据
  \item One class dominates (e.g., 90\% good, 10\% bad) --- KTO handles imbalance better
  \item 某一类占主导（例如 90% 好，10% 坏）——KTO 能更好地处理不平衡
  \item Rapid iteration with noisy labels (more robust than DPO to noise)
  \item 使用噪声标签快速迭代（比 DPO 对噪声更鲁棒）
\end{itemize}

\section{IPO --- Identity Preference Optimization}
\section{IPO --- 身份偏好优化}

\label{ipo-identity-preference-optimization}

\subsection{Motivation}
\subsection{动机}

\label{motivation-2}

DPO has a degenerate solution: it can achieve zero loss by making the margin between chosen and rejected \emph{infinitely large}. In practice, this means DPO overfits --- pushing chosen probability to 1 and rejected to 0, memorizing training data.

DPO 存在一个退化解：它可以通过使被选中响应和被拒绝响应之间的间隔\emph{无限大}来实现零损失。实际上，这意味着 DPO 会过拟合——将被选中响应的概率推到 1，将被拒绝响应的概率推到 0，从而记住训练数据。

\textbf{IPO’s fix}~\cite{azar2024general}: Instead of log-sigmoid (which saturates), use a squared loss that targets a \emph{specific} margin. The loss is minimized at a finite gap, not at infinity.

\textbf{IPO 的修复}~\cite{azar2024general}：使用针对\emph{特定}间隔的平方损失，而不是对数 sigmoid（它会饱和）。损失在有限间隔处最小化，而不是在无穷大处。

\subsection{Loss Function}
\subsection{损失函数}

\label{loss-function-1}

\begin{equation}
\boxed{\mathcal{L}_\text{IPO} = \mathbb{E}\left[\left(\log\frac{\pi_\theta(y_w|x)}{\pi_\text{ref}(y_w|x)} - \log\frac{\pi_\theta(y_l|x)}{\pi_\text{ref}(y_l|x)} - \frac{1}{2\beta}\right)^2\right]}
\end{equation}

\begin{intuitionbox}[IPO vs DPO: Regularization Through Target Margin]
\boxed{\mathcal{L}_\text{IPO} = \mathbb{E}\left[\left(\log\frac{\pi_\theta(y_w|x)}{\pi_\text{ref}(y_w|x)} - \log\frac{\pi_\theta(y_l|x)}{\pi_\text{ref}(y_l|x)} - \frac{1}{2\beta}\right)^2\right]}
\end{equation}

\begin{intuitionbox}[IPO vs DPO: 通过目标间隔进行正则化]
DPO: $\sigma(\text{margin}) \to 1$ optimally. Margin $\to \infty$. No natural stopping point.

DPO: $\sigma(\text{margin}) \to 1$ 最优。Margin $\to \infty$。没有自然的停止点。

IPO: Margin $\to \frac{1}{2\beta}$ optimally. Squared loss penalizes \textbf{both} too-small and too-large margins.

IPO: Margin $\to \frac{1}{2\beta}$ 最优。平方损失会\textbf{同时}惩罚过小和过大的间隔。

Result: IPO is more robust to noisy labels (a mislabeled pair gets bounded influence), and generalizes better because it doesn’t memorize.

结果：IPO对噪声标签更加鲁棒（错误标注的样本对影响有限），并且泛化能力更好，因为它不会记忆。
\end{intuitionbox}


\subsection{TRL Implementation}
\label{trl-implementation-2}

\subsection{TRL 实现}
\label{trl-implementation-2}

The following shows a minimal working example using HuggingFace TRL.

以下展示一个使用 HuggingFace TRL 的最小工作示例。

\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


