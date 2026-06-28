# 步骤 3：使用更新后的模型重复步骤 1（迭代式 RFT）
\end{lstlisting}


\subsection{Scaling Laws for Best-of-N}
\subsection{Best-of-N 的缩放定律}
\label{scaling-laws-for-best-of-n}


\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
$N$ & \textbf{Quality Gain} & \textbf{Cost} & \textbf{Notes} \\
\midrule
1 & Baseline & $1\times$ & Standard sampling \\
4 & +5--8\% win-rate & $4\times$ & Minimum useful. Good cost/quality ratio \\
16 & +10--15\% win-rate & $16\times$ & Strong. Often matches PPO quality \\
64 & +15--20\% win-rate & $64\times$ & Diminishing returns start \\
256 & +18--22\% win-rate & $256\times$ & Only for critical applications \\
\bottomrule
\end{tabular}


\begin{keybox}[Best-of-N as Baseline]
Always compare your RL method against Best-of-N with the same compute budget. If PPO with 64 GPU-hours doesn’t beat Best-of-N with 64 GPU-hours of generation, your PPO has a bug.
\end{keybox}
\begin{keybox}[将 Best-of-N 作为基线]
始终将你的强化学习方法与相同计算预算下的 Best-of-N 进行比较。如果使用 64 GPU 小时的 PPO 未能击败使用 64 GPU 小时生成的 Best-of-N，那么你的 PPO 存在缺陷。
\end{keybox}


\section{Summary: Choosing an Alignment Method}
\section{总结：选择对齐方法}
\label{sec:method-comparison}


We have now surveyed the full landscape of preference optimization and RL-based alignment methods. This section consolidates the key trade-offs into a single reference to help practitioners select the right approach for their constraints.
我们现已全面审视了偏好优化和基于强化学习的对齐方法。本节将关键权衡汇总为单一参考，以帮助从业者根据自身约束选择合适的方法。


\begin{table}[ht!]
\centering
\caption{Cross-method comparison of alignment approaches.}
\caption{对齐方法的跨方法比较。}
{\footnotesize
\begin{tabular}{@{}llllll@{}}
\toprule
\textbf{Method} & \textbf{Models} & \textbf{Data} & \textbf{Compute} & \textbf{Stability} & \textbf{Best For} \\
\textbf{方法} & \textbf{模型数} & \textbf{数据} & \textbf{计算量} & \textbf{稳定性} & \textbf{最适合场景} \\
\midrule
PPO & 4 & Online (gen) & Very high & Low & Max quality, complex reasoning \\
PPO & 4 & 在线（生成） & 非常高 & 低 & 最高质量、复杂推理 \\
GRPO & 2 (no critic) & Online (gen) & High & Medium & Math/code (verifiable rewards) \\
GRPO & 2（无批评者） & 在线（生成） & 高 & 中 & 数学/代码（可验证奖励） \\
DPO & 2 & Offline pairs & Low & High & Style/safety, limited compute \\
DPO & 2 & 离线成对数据 & 低 & 高 & 风格/安全，计算资源有限 \\
Online DPO & 3 & Online (gen) & Medium & Medium-High & DPO without distribution shift \\
在线 DPO & 3 & 在线（生成） & 中 & 中-高 & 无分布偏移的 DPO \\
KTO & 2 & Unpaired binary & Low & High & Production feedback, thumbs up/down \\
KTO & 2 & 非配对二元反馈 & 低 & 高 & 生产环境反馈，点赞/踩 \\
IPO & 2 & Offline pairs & Low & Very high & Noisy labels, anti-overfitting \\
IPO & 2 & 离线成对数据 & 低 & 非常高 & 噪声标签，抗过拟合 \\
ORPO & 1 & Offline pairs & Very low & High & Memory-limited, SFT+align combined \\
ORPO & 1 & 离线成对数据 & 非常低 & 高 & 内存受限，SFT+对齐结合 \\
Best-of-N & 1+RM & Online (gen) & Medium & Perfect & Strong baseline, data generation \\
Best-of-N & 1+奖励模型 & 在线（生成） & 中 & 完美 & 强基线，数据生成 \\
\bottomrule
\end{tabular}
}
\end{table}


\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_029_fig29.png}
\caption{Approximate quality vs.~compute frontier. Methods above the SFT ceiling line improve beyond what supervised fine-tuning alone achieves. Position is illustrative and model-dependent.}
\caption{近似质量-计算前沿。位于 SFT 上限线上方的方法超越了仅进行监督微调所能达到的效果。位置仅为示意，且依赖于模型。}
\end{figure}


\begin{keybox}[Decision Tree: Which Method to Use?]
\begin{enumerate}
  \item \textbf{Do you have verifiable rewards?} (math/code) $\rightarrow$ \textbf{GRPO}
  \item \textbf{你有可验证的奖励吗？}（数学/代码）$\rightarrow$ \textbf{GRPO}
  \item \textbf{Do you need max quality on complex tasks?} $\rightarrow$ \textbf{PPO}
  \item \textbf{你需要在复杂任务上达到最高质量吗？} $\rightarrow$ \textbf{PPO}
  \item \textbf{Do you have paired preferences?} $\rightarrow$ \textbf{DPO} (or IPO if noisy)
  \item \textbf{你有成对的偏好数据吗？} $\rightarrow$ \textbf{DPO}（如果噪声大则用 IPO）
  \item \textbf{Only unpaired binary feedback?} $\rightarrow$ \textbf{KTO}
  \item \textbf{只有非配对的二元反馈？} $\rightarrow$ \textbf{KTO}
  \item \textbf{Memory-limited, starting from base model?} $\rightarrow$ \textbf{ORPO}
  \item \textbf{内存受限，从基础模型开始？} $\rightarrow$ \textbf{ORPO}
  \item \textbf{DPO plateauing, want on-policy?} $\rightarrow$ \textbf{Online DPO}
  \item \textbf{DPO 遇到瓶颈，想要在线策略？} $\rightarrow$ \textbf{在线 DPO}
  \item \textbf{Need a strong baseline quickly?} $\rightarrow$ \textbf{Best-of-N / RFT}
  \item \textbf{需要快速得到一个强基线？} $\rightarrow$ \textbf{Best-of-N / RFT}
\end{enumerate}
\end{keybox}
---

## Chapter: Reward Model Training
## 第章：奖励模型训练

Reward models are the bridge between human preferences and the RL training signal. A well-trained reward model is essential for successful RLHF; a poorly trained one leads to reward hacking and misaligned behaviour. This section covers the theoretical foundations, practical training techniques, and architectural choices for reward models.
奖励模型是人类偏好与强化学习训练信号之间的桥梁。一个训练良好的奖励模型对于成功的 RLHF 至关重要；而训练不佳的模型会导致奖励黑客攻击（reward hacking）和失调行为（misaligned behaviour）。本节涵盖了奖励模型的理论基础、实际训练技术和架构选择。

## Section: Bradley-Terry Model -- Full Derivation
## 节：Bradley-Terry 模型 —— 完整推导

The Bradley-Terry model~\cite{bradley1952rank} is the standard probabilistic framework for pairwise preference learning. Given two responses $y_1$ and $y_2$ to a prompt $q$, the model assumes:
Bradley-Terry 模型~\cite{bradley1952rank} 是成对偏好学习（pairwise preference learning）的标准概率框架。给定对提示 $q$ 的两个回答 $y_1$ 和 $y_2$，该模型假设：

\[
P(y_1 \succ y_2 \mid q) = \sigma(r(y_1, q) - r(y_2, q))
    = \frac{e^{r(y_1,q)}}{e^{r(y_1,q)} + e^{r(y_2,q)}},
\]

where $r: \mathcal{Y} \times \mathcal{Q} \to \mathbb{R}$ is the scalar reward function and $\sigma$ is the sigmoid function.
其中 $r: \mathcal{Y} \times \mathcal{Q} \to \mathbb{R}$ 是标量奖励函数（scalar reward function），$\sigma$ 是 sigmoid 函数。

### Maximum Likelihood Estimation
### 最大似然估计

Given a dataset $\mathcal{D} = \{(q^{(k)}, y_w^{(k)}, y_l^{(k)})\}_{k=1}^N$ of preference pairs, the MLE objective is:
给定一个偏好对数据集 $\mathcal{D} = \{(q^{(k)}, y_w^{(k)}, y_l^{(k)})\}_{k=1}^N$，最大似然估计（MLE）的目标函数为：

\[
\mathcal{L}_{\text{BT}}(\phi) =
    -\frac{1}{N}\sum_{k=1}^N \log \sigma\!\bigl(r_\phi(y_w^{(k)}, q^{(k)}) - r_\phi(y_l^{(k)}, q^{(k)})\bigr),
\]

where $r_\phi$ is a neural network parameterised by $\phi$. This is a binary cross-entropy loss where the ``positive'' class is the preferred response.
其中 $r_\phi$ 是一个由参数 $\phi$ 参数化的神经网络。这是一个二元交叉熵损失（binary cross-entropy loss），其中“正类”是更受偏好的回答。

\begin{keybox}[Bradley-Terry Assumptions]
\begin{enumerate}
  \item Preferences are \emph{transitive}: if $y_1 \succ y_2$ and $y_2 \succ y_3$, then $y_1 \succ y_3$.
  \item Preferences are determined by a \emph{scalar} reward (no multi-dimensional preferences).
  \item The preference probability depends only on the \emph{difference} in rewards.
  \item Preferences are \emph{independent} across pairs (no annotator effects).
\end{enumerate}

\begin{keybox}[Bradley-Terry 假设]
\begin{enumerate}
  \item 偏好是\emph{传递的}：如果 $y_1 \succ y_2$ 且 $y_2 \succ y_3$，则 $y_1 \succ y_3$。
  \item 偏好由\emph{标量}奖励决定（没有多维偏好）。
  \item 偏好概率仅取决于奖励的\emph{差值}。
  \item 偏好在不同对之间是\emph{独立的}（没有标注者效应）。
\end{enumerate}

These assumptions are often violated in practice, motivating extensions like Plackett-Luce models for ranking and multi-dimensional reward models.
这些假设在实践中经常被违反，从而催生了诸如用于排序的 Plackett-Luce 模型和多维奖励模型等扩展。
\end{keybox}

### Margin Loss Extension
### 边际损失扩展

A common extension adds a margin $m$ to ensure a minimum gap between winning and losing rewards:
一个常见的扩展是添加一个边际 $m$，以确保获胜奖励和失败奖励之间存在最小差距：

\[
\mathcal{L}_{\text{margin}} =
    -\frac{1}{N}\sum_{k=1}^N \log \sigma\!\bigl(r_\phi(y_w^{(k)}, q^{(k)}) - r_\phi(y_l^{(k)}, q^{(k)}) - m\bigr).
\]

## Section: Reward Model Architectures
## 节：奖励模型架构

\begin{intuitionbox}[Classification Head on LLM]
The standard reward model architecture takes a pretrained LLM and replaces the language modelling head (which maps hidden states to vocabulary logits) with a scalar regression head (which maps the final hidden state to a single reward value).
\end{intuitionbox}

\begin{intuitionbox}[LLM 上的分类头]
标准奖励模型架构采用预训练的 LLM，并将语言建模头（将隐藏状态映射到词汇 logits）替换为标量回归头（将最终隐藏状态映射到单个奖励值）。
\end{intuitionbox}

The architecture is:
架构如下：

\begin{enumerate}
  \item \textbf{Backbone}: a pretrained LLM (e.g., Llama, Mistral) that encodes the prompt-response pair into a sequence of hidden states.
  \item \textbf{Pooling}: extract the hidden state at the last token position (for decoder-only models) or the \texttt{[CLS]} token (for encoder models).
  \item \textbf{Regression head}: a linear layer $W \in \mathbb{R}^{d \times 1}$ that maps the pooled hidden state to a scalar reward.
\end{enumerate}

\begin{enumerate}
  \item \textbf{骨干网络（Backbone）}：一个预训练的 LLM（例如 Llama、Mistral），它将提示-回答对编码为隐藏状态序列。
  \item \textbf{池化（Pooling）}：提取最后一个 token 位置的隐藏状态（对于仅解码器模型）或 \texttt{[CLS]} token（对于编码器模型）。
  \item \textbf{回归头（Regression head）}：一个线性层 $W \in \mathbb{R}^{d \times 1}$，将池化后的隐藏状态映射为标量奖励。
\end{enumerate}

\begin{examplebox}[Reward Model Training in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import RewardConfig, RewardTrainer
from transformers import AutoModelForSequenceClassification


