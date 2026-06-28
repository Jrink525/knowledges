    # 每个提示生成的 K 个响应
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    max_new_tokens=512,
    temperature=0.7,
    bf16=True,
    num_train_epochs=1,
    logging_steps=10,
)

trainer = OnlineDPOTrainer(
    model=model,
    reward_model=reward_model,
    args=online_dpo_config,
    train_dataset=prompt_dataset,
    tokenizer=tokenizer,
)
trainer.train()
\end{lstlisting}

\subsection{Online DPO vs Offline DPO vs PPO}
\subsection{在线 DPO vs 离线 DPO vs PPO}

\label{online-dpo-vs-offline-dpo-vs-ppo}

\begin{tabular}{@{}llp{4.5cm}lp{4.5cm}@{}}
\toprule
 & \textbf{Data} & \textbf{Models} & \textbf{Loss} & \textbf{Best For} \\
 & \textbf{数据} & \textbf{模型} & \textbf{损失} & \textbf{最适合} \\
\midrule
Offline DPO & Static pairs & 2 (policy + reference) & DPO & Quick alignment, limited compute \\
离线 DPO & 静态配对 & 2（策略 + 参考） & DPO & 快速对齐，计算资源有限 \\
Online DPO & Fresh from $\pi_\theta$ & 3 (policy + reference + reward model) & DPO & When DPO plateaus, need exploration \\
在线 DPO & 从 $\pi_\theta$ 新鲜生成 & 3（策略 + 参考 + 奖励模型） & DPO & 当 DPO 性能停滞，需要探索时 \\
PPO & Fresh from $\pi_\theta$ & 4 (policy + reference + reward model + value head) & PPO clip & Max quality, complex reasoning \\
PPO & 从 $\pi_\theta$ 新鲜生成 & 4（策略 + 参考 + 奖励模型 + 价值头） & PPO 裁剪 & 最高质量，复杂推理 \\
\bottomrule
\end{tabular}

\section{KTO --- Kahneman-Tversky Optimization}
\section{KTO --- 卡尼曼-特沃斯基优化}

\label{sec:kto}

\subsection{Motivation}
\subsection{动机}

\label{motivation-1}

DPO requires \emph{paired} preferences: for the same prompt, you need both a good and bad response. In practice, most feedback is \emph{unpaired}: users give thumbs up/down on individual responses, with no matched pair.

DPO 需要\emph{配对}的偏好：对于同一个提示，你需要一个好的和一个差的响应。实际上，大多数反馈是\emph{未配对的}：用户对单个响应给出点赞/点踩，没有匹配的对。

\textbf{KTO’s insight}~\cite{ethayarajh2024kto}: Use prospect theory (from behavioral economics). Humans feel losses more strongly than gains. A ``thumbs down'' should produce a stronger gradient than a ``thumbs up.''

\textbf{KTO 的洞见}~\cite{ethayarajh2024kto}：运用前景理论（来自行为经济学）。人类对损失的感觉比收益更强烈。“点踩”应该比“点赞”产生更强的梯度。

\subsection{Loss Function}
\subsection{损失函数}

\label{loss-function}

\begin{equation}
\boxed{\mathcal{L}_\text{KTO} = \mathbb{E}_{y_w}\left[\lambda_w (1 - v(x, y_w))\right] + \mathbb{E}_{y_l}\left[\lambda_l \cdot v(x, y_l)\right]}
\end{equation}
 where $v(x,y) = \sigma\left(\beta \log\frac{\pi_\theta(y|x)}{\pi_\text{ref}(y|x)} - z_\text{ref}\right)$, and $z_\text{ref}$ is the expected KL divergence (a running baseline).

其中 $v(x,y) = \sigma\left(\beta \log\frac{\pi_\theta(y|x)}{\pi_\text{ref}(y|x)} - z_\text{ref}\right)$，$z_\text{ref}$ 是期望的 KL 散度（一个运行基线）。

\begin{intuitionbox}[KTO Intuition via Prospect Theory]
\begin{intuitionbox}[通过前景理论理解 KTO 直觉]

\textbf{Desirable responses} ($y_w$): The model gets ``utility'' from increasing their probability. But with diminishing returns --- once it’s already quite likely, don’t push harder.

\textbf{期望的响应} ($y_w$)：模型从增加其概率中获得“效用”。但存在边际递减效应——一旦已经相当可能，就不要过度推动。

\textbf{Undesirable responses} ($y_l$): Loss aversion means the penalty for generating bad text is weighted more strongly than the reward for good text. Default: $\lambda_l = 1.0$, $\lambda_w = 1.0$, but you can set $\lambda_l > \lambda_w$.

\textbf{不期望的响应} ($y_l$)：损失厌恶意味着对生成差文本的惩罚比好文本的奖励权重更大。默认：$\lambda_l = 1.0$，$\lambda_w = 1.0$，但你可以设置 $\lambda_l > \lambda_w$。

\textbf{Key advantage}: Each training example is independent! No need to find matched pairs. Can use thumbs-up/down data directly.

\textbf{关键优势}：每个训练样本都是独立的！无需寻找匹配的配对。可以直接使用点赞/点踩数据。
\end{intuitionbox}

\begin{examplebox}[KTO Data Format]
\begin{examplebox}[KTO 数据格式]

Unlike DPO which needs: \verb|{"prompt": ..., "chosen": ..., "rejected": ...}|

与 DPO 不同，DPO 需要：\verb|{"prompt": ..., "chosen": ..., "rejected": ...}|

KTO only needs: \verb|{"prompt": ..., "completion": ..., "label": true/false}|

KTO 只需要：\verb|{"prompt": ..., "completion": ..., "label": true/false}|

This means you can use:

这意味着你可以使用：

\begin{itemize}
  \item Thumbs up/down from production traffic
  \item 来自生产流量的点赞/点踩
  \item Upvotes/downvotes from forums
  \item 论坛上的投票/反对票
  \item Human ratings binarized (4--5 stars = good, 1--2 = bad)
  \item 二值化的人工评分（4--5 星 = 好，1--2 星 = 差）
  \item Any per-response quality signal
  \item 任何基于响应的质量信号
\end{itemize}
\end{examplebox}

\subsection{TRL Implementation}
\subsection{TRL 实现}

\label{trl-implementation-1}

The following shows a minimal working example using HuggingFace TRL.
以下展示了使用 HuggingFace TRL 的最小工作示例。

\begin{lstlisting}[style=pythonstyle]
from trl import KTOConfig, KTOTrainer

