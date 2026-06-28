# Alpha divergence (alpha=0: forward KL, alpha=1: reverse KL)
config_alpha = DPOConfig(
    f_divergence_type="alpha_divergence",
    f_alpha_divergence_coef=0.5,   # alpha parameter
    beta=0.1,
)


trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}


\begin{keybox}[When to Use f-DPO]
\begin{keybox}[何时使用f-DPO]
\begin{itemize}
  \item Use \textbf{JS divergence} when you want a balance between diversity and quality.
  \item 当你需要在多样性和质量之间取得平衡时，使用\textbf{JS散度}。
  \item Use \textbf{forward KL} for creative tasks where diversity is paramount.
  \item 对于多样性至关重要的创意任务，使用\textbf{正向KL}。
  \item Use \textbf{reverse KL} (standard DPO) for tasks with a single correct answer.
  \item 对于只有一个正确答案的任务，使用\textbf{反向KL}（标准DPO）。
  \item Use \textbf{alpha divergence} to continuously interpolate and tune the trade-off.
  \item 使用\textbf{alpha散度}来连续插值和调节权衡。
\end{itemize}
\end{keybox}

## Robust DPO
## 鲁棒 DPO

\label{sec:robust-dpo}

\begin{intuitionbox}[Noisy Labels in Preference Data]
Human preference annotations are noisy. Annotators disagree, make mistakes, and sometimes flip the preferred/dispreferred labels. Standard DPO treats all labels as ground truth, which can cause the model to overfit to noise. Robust DPO~\cite{chowdhury2024robustdpo} analytically debiases the loss under a known noise model.
\begin{intuitionbox}[偏好数据中的噪声标签]
人类偏好标注存在噪声。标注者意见不一、会出错，有时甚至颠倒偏好/非偏好标签。标准 DPO 将所有标签视为真实标签，这可能导致模型过拟合噪声。Robust DPO（鲁棒DPO）~\cite{chowdhury2024robustdpo} 在已知噪声模型下对损失函数进行解析去偏。
\end{intuitionbox}

Assume each label is flipped with probability $\epsilon$ (the noise rate). The debiased loss is:
假设每个标签以概率 $\epsilon$（噪声率）被翻转。去偏后的损失函数为：

\[
\boxed{
    \mathcal{L}_{\text{robust}} =
    \frac{(1-\epsilon)\,\mathcal{L}_{\text{DPO}}(y_w, y_l)
          - \epsilon\,\mathcal{L}_{\text{DPO}}(y_l, y_w)}{1 - 2\epsilon},
  }
\]

where $\mathcal{L}_{\text{DPO}}(y_w, y_l)$ is the standard DPO loss treating $y_w$ as preferred, and $\mathcal{L}_{\text{DPO}}(y_l, y_w)$ is the loss with labels flipped. This correction removes the bias introduced by label noise.
其中 $\mathcal{L}_{\text{DPO}}(y_w, y_l)$ 是将 $y_w$ 视为优选的标准 DPO 损失，而 $\mathcal{L}_{\text{DPO}}(y_l, y_w)$ 是标签翻转后的损失。这一修正消除了标签噪声引入的偏差。

\begin{keybox}[Intuition for Robust DPO]
The formula is a linear combination that ``subtracts out'' the contribution of flipped labels. When $\epsilon=0$, it reduces to standard DPO. When $\epsilon=0.5$, the denominator goes to zero -- the labels are pure noise and no learning is possible. In practice, $\epsilon \in [0.05, 0.2]$ covers most real annotation noise levels.
\begin{keybox}[鲁棒DPO的直观理解]
该公式是一个线性组合，它“减去”了翻转标签的贡献。当 $\epsilon=0$ 时，它退化为标准 DPO。当 $\epsilon=0.5$ 时，分母为零——标签为纯噪声，无法进行学习。实践中，$\epsilon \in [0.05, 0.2]$ 覆盖了大多数真实的标注噪声水平。
\end{keybox}

\begin{examplebox}[Robust DPO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


config = DPOConfig(
    loss_type="robust",
    label_smoothing=0.1,   # corresponds to epsilon = 0.1
