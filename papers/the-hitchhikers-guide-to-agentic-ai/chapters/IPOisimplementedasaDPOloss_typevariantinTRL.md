# IPO is implemented as a DPO loss_type variant in TRL
ipo_config = DPOConfig(
    output_dir="./ipo_output",
    beta=0.1,
    loss_type="ipo",             # The key difference!
    learning_rate=5e-7,
    max_length=2048,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    bf16=True,
    num_train_epochs=1,
)


trainer = DPOTrainer(
    model=model, ref_model=None, args=ipo_config,
    train_dataset=pref_dataset, tokenizer=tokenizer, peft_config=lora_config,
)
trainer.train()
\end{lstlisting}


\subsection{When to Choose IPO over DPO}
\label{when-to-choose-ipo-over-dpo}

\subsection{何时选择 IPO 而非 DPO}
\label{when-to-choose-ipo-over-dpo}

\begin{itemize}
  \item Noisy preference data (crowdsourced, AI-judged with errors)
  \item 噪声偏好数据（众包、AI 评判存在错误）
  \item Observing DPO overfitting (train loss $\to$ 0 but eval degrades)
  \item 观察到 DPO 过拟合（训练损失 $\to$ 0 但评估指标下降）
  \item Want more conservative, robust alignment
  \item 希望进行更保守、更鲁棒的 alignment
  \item Multiple epochs needed (DPO degrades after epoch 1; IPO is more stable)
  \item 需要多个 epoch（DPO 在 epoch 1 后性能下降；IPO 更稳定）
\end{itemize}


\section{ORPO --- Odds Ratio Preference Optimization}
\label{sec:orpo}

\section{ORPO --- 优势比偏好优化}
\label{sec:orpo}

\subsection{Motivation}
\label{motivation-3}

\subsection{动机}
\label{motivation-3}

All methods so far need a reference model --- either as a separate copy (doubles memory) or implicitly via LoRA. ORPO~\cite{hong2024orpo} eliminates the reference entirely by combining SFT and preference alignment in a single loss.

到目前为止，所有方法都需要一个参考模型——要么作为一个单独的副本（内存翻倍），要么通过 LoRA 隐式实现。ORPO~\cite{hong2024orpo} 通过将 SFT 和偏好 alignment 合并到一个损失函数中，完全消除了参考模型。

\textbf{Key insight}: Use the \emph{odds ratio} of generating chosen vs rejected as the preference signal. The SFT component naturally prevents collapse (no need for KL regularization).

\textbf{关键见解}：使用生成 chosen 与 rejected 的 \emph{优势比} 作为偏好信号。SFT 组件自然防止了坍缩（无需 KL 正则化）。

\subsection{Loss Function}
\label{loss-function-2}

\subsection{损失函数}
\label{loss-function-2}

\begin{equation}
\boxed{\mathcal{L}_\text{ORPO} = \underbrace{\mathcal{L}_\text{SFT}(y_w)}_{\text{standard NLL on chosen}} - \lambda \cdot \underbrace{\log\sigma\left(\log\frac{\text{odds}_\theta(y_w|x)}{\text{odds}_\theta(y_l|x)}\right)}_{\text{preference alignment via odds ratio}}}
\end{equation}
 where $\text{odds}_\theta(y|x) = \frac{P_\theta(y|x)}{1 - P_\theta(y|x)}$.

\begin{equation}
\boxed{\mathcal{L}_\text{ORPO} = \underbrace{\mathcal{L}_\text{SFT}(y_w)}_{\text{对 chosen 的标准 NLL}} - \lambda \cdot \underbrace{\log\sigma\left(\log\frac{\text{odds}_\theta(y_w|x)}{\text{odds}_\theta(y_l|x)}\right)}_{\text{通过优势比的偏好 alignment}}}
\end{equation}
其中 $\text{odds}_\theta(y|x) = \frac{P_\theta(y|x)}{1 - P_\theta(y|x)}$。

\begin{intuitionbox}[ORPO: SFT + Alignment in One Shot]
\textbf{Key insight}: Use the \emph{odds ratio} of generating chosen vs rejected as the preference signal. The SFT component naturally prevents collapse (no need for KL regularization).

\textbf{关键见解}：使用生成 chosen 与 rejected 的 \emph{优势比} 作为偏好信号。SFT 组件自然防止了坍缩（无需 KL 正则化）。

\subsection{Loss Function}
\label{loss-function-2}

\subsection{损失函数}
\label{loss-function-2}

\begin{equation}
\boxed{\mathcal{L}_\text{ORPO} = \underbrace{\mathcal{L}_\text{SFT}(y_w)}_{\text{standard NLL on chosen}} - \lambda \cdot \underbrace{\log\sigma\left(\log\frac{\text{odds}_\theta(y_w|x)}{\text{odds}_\theta(y_l|x)}\right)}_{\text{preference alignment via odds ratio}}}
\end{equation}
 where $\text{odds}_\theta(y|x) = \frac{P_\theta(y|x)}{1 - P_\theta(y|x)}$.

\begin{equation}
\boxed{\mathcal{L}_\text{ORPO} = \underbrace{\mathcal{L}_\text{SFT}(y_w)}_{\text{对 chosen 的标准 NLL}} - \lambda \cdot \underbrace{\log\sigma\left(\log\frac{\text{odds}_\theta(y_w|x)}{\text{odds}_\theta(y_l|x)}\right)}_{\text{通过优势比的偏好 alignment}}}
\end{equation}
其中 $\text{odds}_\theta(y|x) = \frac{P_\theta(y|x)}{1 - P_\theta(y|x)}$。

\begin{intuitionbox}[ORPO: SFT + Alignment in One Shot]
\textbf{SFT term}: Trains the model to generate the chosen response well (standard language modeling).

\textbf{SFT 项}：训练模型生成 chosen 响应（标准语言建模）。

\textbf{Odds ratio term}: Additionally pushes the model to prefer chosen over rejected. The odds ratio is a natural contrast that doesn’t require a reference model.

\textbf{优势比项}：额外推动模型偏好 chosen 而非 rejected。优势比是一种自然的对比，不需要参考模型。

\textbf{Why no reference needed?}: The SFT loss already anchors the model to reasonable text. It serves the same role as KL-to-reference in other methods. One model, one forward pass, one loss. 50\% less memory!

\textbf{为什么不需要参考？}：SFT 损失已经将模型锚定到合理的文本上。它起到了与其他方法中 KL-to-reference 相同的作用。一个模型，一次前向传播，一个损失。内存减少 50%！
\end{intuitionbox}


\subsection{TRL Implementation}
\label{trl-implementation-3}

\subsection{TRL 实现}
\label{trl-implementation-3}

The following shows a minimal working example using HuggingFace TRL.

以下展示一个使用 HuggingFace TRL 的最小工作示例。

\begin{lstlisting}[style=pythonstyle]
from trl import ORPOConfig, ORPOTrainer


orpo_config = ORPOConfig(
    output_dir="./orpo_output",
    beta=0.1,                    # Odds ratio weight (lambda)
    learning_rate=5e-7,
    max_length=2048,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    bf16=True,
    num_train_epochs=1,
    gradient_checkpointing=True,
)


trainer = ORPOTrainer(
    model=model,                 # No ref_model needed!
    args=orpo_config,
    train_dataset=pref_dataset,  # Same format as DPO: prompt/chosen/rejected
    tokenizer=tokenizer,
    peft_config=lora_config,
)
trainer.train()
\end{lstlisting}


\subsection{When to Choose ORPO}
\label{when-to-choose-orpo}

\subsection{何时选择 ORPO}
\label{when-to-choose-orpo}

\begin{itemize}
  \item Memory-constrained: can’t afford reference model copy (saves 70--140GB for 70B)
  \item 内存受限：无法承担参考模型副本（对于 70B 模型可节省 70--140GB）
  \item Starting from base model (not SFT’d yet) --- ORPO does SFT simultaneously
  \item 从基础模型开始（尚未经过 SFT）——ORPO 同时进行 SFT
  \item Want simplest possible pipeline: one model, one loss, one training run
  \item 希望使用最简单的流程：一个模型，一个损失，一次训练
  \item Good preference data available from the start
  \item 从开始就有高质量的偏好数据
\end{itemize}


\begin{warningbox}[ORPO Limitations]
\begin{warningbox}[ORPO 的限制]
\begin{itemize}
  \item Less studied than DPO/PPO --- fewer proven recipes at 70B+ scale
  \item 比 DPO/PPO 研究得少——在 70B+ 规模上经过验证的方案较少
  \item The SFT component means it needs high-quality chosen responses (not just relative preference)
  \item SFT 组件意味着它需要高质量的 chosen 响应（不仅仅是相对偏好）
  \item Harder to debug: two loss components can conflict
  \item 更难调试：两个损失组件可能冲突
\end{itemize}
\end{warningbox}


\begin{keybox}[See Also: SimPO]
\textbf{SimPO}~\cite{meng2024simpo} is another reference-free preference method that uses length-normalized log-probability as an implicit reward, eliminating the reference model entirely. It is covered in Section~\ref{sec:simpo} alongside other DPO extensions due to its shared reference-free philosophy.
\end{keybox}

\begin{keybox}[另见：SimPO]
\textbf{SimPO}~\cite{meng2024simpo} 是另一种无参考偏好方法，它使用长度归一化的对数概率作为隐式奖励，完全消除了参考模型。由于它共享无参考的哲学，因此将在第~\ref{sec:simpo} 节中与其他 DPO 扩展一起介绍。
\end{keybox}


\section{Best-of-N Sampling (Rejection Sampling)}
\label{best-of-n-sampling-rejection-sampling}

\section{Best-of-N 采样（拒绝采样）}
\label{best-of-n-sampling-rejection-sampling}

\subsection{Motivation}
\label{motivation-4}

\subsection{动机}
\label{motivation-4}

Sometimes the simplest approach wins. Best-of-N~\cite{nakano2021webgpt} requires \emph{no training at all} during the RL phase --- just generate multiple candidates and pick the best one.

有时最简单的方法胜出。Best-of-N~\cite{nakano2021webgpt} 在 RL 阶段完全\emph{不需要训练}——只需生成多个候选并选择最佳的一个。

\subsection{Algorithm}
\label{algorithm-1}

\subsection{算法}
\label{algorithm-1}

\begin{enumerate}
  \item For each prompt, generate $N$ responses from the policy (typically $N = 4$--$64$)
  \item 对于每个提示，从策略中生成 $N$ 个响应（通常 $N = 4$--$64$）
  \item Score all responses with a reward model
  \item 使用奖励模型对所有响应进行评分
  \item Select the highest-scoring response
  \item 选择得分最高的响应
  \item (Optional) Use selected responses as SFT data for the next iteration
  \item （可选）将选中的响应作为下一次迭代的 SFT 数据
\end{enumerate}


\begin{equation}
\boxed{\text{Best-of-N response}: \quad y^* = \arg\max_{y_i \sim \pi_\theta(\cdot|x)} r_\phi(x, y_i)}
\end{equation}

\begin{equation}
\boxed{\text{Best-of-N 响应}: \quad y^* = \arg\max_{y_i \sim \pi_\theta(\cdot|x)} r_\phi(x, y_i)}
\end{equation}

\begin{intuitionbox}[Why Best-of-N is a Legitimate ``RL'' Method]
\textbf{At inference time}: Best-of-N improves output quality without changing model weights. With $N=64$, win-rate improves 10--20\% over greedy --- sometimes matching or exceeding PPO.

\textbf{在推理时}：Best-of-N 在不改变模型权重的情况下提高输出质量。当 $N=64$ 时，胜率比贪心提高 10--20\%——有时匹配或超过 PPO。

\textbf{As a training method} (Rejection Sampling Fine-Tuning / RFT):

\textbf{作为一种训练方法}（拒绝采样微调 / RFT）：

\begin{enumerate}
  \item Generate many responses, select best ones
  \item 生成大量响应，选择最好的
  \item SFT on the selected responses
  \item 对选中的响应进行 SFT
  \item Repeat (iterative refinement)
  \item 重复（迭代优化）
\end{enumerate}

This is how many production models are trained: simpler than PPO, almost as effective, completely stable.

许多生产模型就是这样训练的：比 PPO 更简单，效果几乎一样好，完全稳定。

\textbf{Theoretical connection}~\cite{gao2023scaling}: Best-of-N implements an implicit KL-constrained policy: $\pi_\text{BoN}(y|x) \propto \pi_\theta(y|x)^{1-1/N} \cdot r(x,y)^{1/N}$.

\textbf{理论联系}~\cite{gao2023scaling}：Best-of-N 实现了一个隐式的 KL 约束策略：$\pi_\text{BoN}(y|x) \propto \pi_\theta(y|x)^{1-1/N} \cdot r(x,y)^{1/N}$。
\end{intuitionbox}


\subsection{TRL Implementation}
\label{trl-implementation-4}

\subsection{TRL 实现}
\label{trl-implementation-4}

The following shows a minimal working example using HuggingFace TRL.

以下展示一个使用 HuggingFace TRL 的最小工作示例。

\begin{lstlisting}[style=pythonstyle]
from transformers import pipeline
import numpy as np


