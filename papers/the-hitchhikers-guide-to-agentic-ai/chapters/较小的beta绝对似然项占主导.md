                 # 较小的 beta：绝对似然项占主导
)


trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\begin{keybox}[When to Use NCA]
\begin{itemize}
  \item When you observe the winning response probability decreasing during DPO training.
  \item For tasks where absolute response quality matters, not just relative ranking.
  \item Use small $\beta$ (e.g., 0.01) to give the absolute likelihood term more weight.
\end{itemize}
\begin{keybox}[何时使用 NCA]
\begin{itemize}
  \item 当观察到 DPO 训练中获胜回复概率下降时。
  \item 对于绝对回复质量（而非仅相对排序）至关重要的任务。
  \item 使用较小的 $\beta$（例如 0.01）以赋予绝对似然项更多权重。
\end{itemize}
\end{keybox}

\subsection{SLiC-HF -- Sequence Likelihood Calibration}
\subsection{SLiC-HF——序列似然校准}
\label{sec:slic}

\begin{intuitionbox}[Hinge Loss as a Simpler Alternative]
The log-sigmoid loss in DPO is smooth but can be slow to converge when the margin is large. SLiC-HF~\cite{zhao2023slichf} uses a hinge loss, which is zero when the margin exceeds a threshold and linear otherwise. This is simpler, faster, and surprisingly competitive.
\begin{intuitionbox}[作为更简单替代方案的合页损失]
DPO 中的对数 sigmoid 损失是平滑的，但当间隔较大时可能收敛缓慢。SLiC-HF（序列似然校准-合页）~\cite{zhao2023slichf} 使用合页损失，当间隔超过阈值时损失为零，否则为线性。这更简单、更快，且出人意料地具有竞争力。
\end{intuitionbox}

The SLiC-HF loss is:
SLiC-HF 损失为：

\[
\mathcal{L}_{\text{SLiC}} = \max\!\left(0,\;
    \delta - \beta\log\frac{\pi_\theta(y_w|q)}{\pi_{\text{ref}}(y_w|q)}
    + \beta\log\frac{\pi_\theta(y_l|q)}{\pi_{\text{ref}}(y_l|q)}
  \right),
\]

where $\delta$ is the margin threshold. When the model already assigns a margin of $\delta$ between winning and losing responses, the loss is zero.
其中 $\delta$ 是间隔阈值。当模型已在获胜和失败回复之间分配了 $\delta$ 的间隔时，损失为零。

\begin{examplebox}[SLiC-HF in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


config = DPOConfig(
    loss_type="hinge",
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

\subsection{Iterative RPO -- Reasoning Preference Optimisation}
\subsection{Iterative RPO——推理偏好优化}
\label{sec:rpo}

\begin{intuitionbox}[DPO Forgets How to Generate]
Standard DPO trains the model to \emph{discriminate} between winning and losing responses. But for reasoning tasks, the model also needs to \emph{generate} correct reasoning traces. A model that can discriminate but not generate is useless at inference time. RPO adds an NLL (negative log-likelihood) term on the winning response to ensure the model learns to generate it.
\end{intuitionbox}

\begin{intuitionbox}[DPO 遗忘如何生成]
标准的 DPO 训练模型在获胜回答和失败回答之间进行 \emph{判别}。但对于推理任务，模型还需要 \emph{生成} 正确的推理轨迹。一个能判别但不能生成的模型在推理时毫无用处。RPO 在获胜回答上添加了一个 NLL（负对数似然）项，以确保模型学会生成它。
\end{intuitionbox}

The RPO loss combines DPO and SFT:

RPO 损失结合了 DPO 和 SFT：

\[
\mathcal{L}_{\text{RPO}} =
    \lambda_1 \mathcal{L}_{\text{DPO}}(y_w, y_l)
    + \lambda_2 \mathcal{L}_{\text{NLL}}(y_w),
\]

where $\mathcal{L}_{\text{NLL}}(y_w) = -\log \pi_\theta(y_w|q)$ is the standard language modelling loss on the winning response.

其中 $\mathcal{L}_{\text{NLL}}(y_w) = -\log \pi_\theta(y_w|q)$ 是在获胜回答上的标准语言建模损失。

\begin{examplebox}[Iterative RPO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


config = DPOConfig(
    loss_type="sigmoid",            # Standard DPO loss
    rpo_alpha=1.0,                  # NLL regularisation weight (RPO)
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

\begin{examplebox}[TRL 中的迭代 RPO]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


config = DPOConfig(
    loss_type="sigmoid",            # 标准 DPO 损失
    rpo_alpha=1.0,                  # NLL 正则化权重 (RPO)
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

\begin{keybox}[When to Use RPO]
\begin{itemize}
  \item Reasoning tasks (math, code, logic) where the model must generate step-by-step solutions.
  \item When DPO training causes the model to lose fluency or generation quality.
  \item Iterative pipelines: generate rollouts, label them, train with RPO, repeat.
  \item The NLL term acts as a regulariser, preventing the policy from collapsing.
\end{itemize}
\end{keybox}

\begin{keybox}[何时使用 RPO]
\begin{itemize}
  \item 推理任务（数学、代码、逻辑），其中模型必须生成逐步的解决方案。
  \item 当 DPO 训练导致模型失去流畅性或生成质量时。
  \item 迭代流程：生成轨迹，标记它们，用 RPO 训练，重复。
  \item NLL 项起到正则化作用，防止策略崩溃。
\end{itemize}
\end{keybox}

\subsection{SimPO -- Simple Preference Optimisation}
\label{sec:simpo}

## SimPO -- Simple Preference Optimisation
## SimPO——简单偏好优化

\begin{intuitionbox}[Reference-Free Preference Learning]
DPO requires a reference model to compute the implicit reward. This doubles memory usage and adds complexity. SimPO~\cite{meng2024simpo} eliminates the reference model by using the \emph{average log-probability} of the response as an implicit reward, with a length normalisation term to prevent the model from preferring short responses.
\end{intuitionbox}

\begin{intuitionbox}[无参考模型偏好学习]
DPO 需要参考模型来计算隐式奖励。这会使内存使用翻倍并增加复杂性。SimPO~\cite{meng2024simpo} 通过使用回答的 \emph{平均对数概率} 作为隐式奖励，并加入长度归一化项来防止模型偏好短回答，从而消除了参考模型。
\end{intuitionbox}

SimPO defines the implicit reward as:

SimPO 将隐式奖励定义为：

\[
r_{\text{SimPO}}(y|q) = \frac{\beta}{|y|} \log \pi_\theta(y|q),
\]

and the loss as:

损失函数定义为：

\[
\boxed{
    \mathcal{L}_{\text{SimPO}} = -\mathbb{E}\!\left[
      \log \sigma\!\left(
        \frac{\beta}{|y_w|}\log\pi_\theta(y_w|q)
        - \frac{\beta}{|y_l|}\log\pi_\theta(y_l|q)
        - \gamma
      \right)
    \right],
  }
\]

where $\gamma > 0$ is a target reward margin that ensures the winning response has strictly higher reward than the losing response by at least $\gamma$.

其中 $\gamma > 0$ 是目标奖励边际，确保获胜回答的奖励至少比失败回答高 $\gamma$。

\begin{keybox}[SimPO vs DPO vs ORPO]
\begin{itemize}
  \item \textbf{DPO}: uses reference model; ratio-based implicit reward.
  \item \textbf{ORPO}: reference-free; adds odds-ratio term to SFT loss.
  \item \textbf{SimPO}: reference-free; length-normalised log-prob reward + margin.
  \item SimPO is simpler than DPO (no reference model) and more principled than ORPO.
  \item The length normalisation in SimPO is critical: without it, the model prefers long responses.
\end{itemize}
\end{keybox}

\begin{keybox}[SimPO vs DPO vs ORPO]
\begin{itemize}
  \item \textbf{DPO}：使用参考模型；基于比值的隐式奖励。
  \item \textbf{ORPO}：无参考模型；在 SFT 损失中添加优势比项。
  \item \textbf{SimPO}：无参考模型；长度归一化的对数概率奖励 + 边际。
  \item SimPO 比 DPO 更简单（无参考模型），且比 ORPO 更具原则性。
  \item SimPO 中的长度归一化至关重要：没有它，模型会偏好长回答。
\end{itemize}
\end{keybox}

\begin{examplebox}[SimPO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


config = DPOConfig(
    loss_type="simpo",
    simpo_gamma=0.5,   # target reward margin gamma
    beta=2.5,          # length normalisation coefficient
