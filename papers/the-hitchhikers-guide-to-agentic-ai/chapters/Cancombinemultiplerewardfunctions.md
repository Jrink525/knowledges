# Can combine multiple reward functions!
def format_reward_fn(completions, **kwargs):
    """Bonus for using proper LaTeX formatting."""
    """使用正确LaTeX格式的奖励加分。"""
    return [0.5 if "\\boxed{" in c else 0.0 for c in completions]


trainer = GRPOTrainer(
    model=model,
    args=grpo_config,
    reward_funcs=[reward_fn, format_reward_fn],  # Multi-objective!
    train_dataset=math_dataset,
    tokenizer=tokenizer,
)
trainer.train()
\end{lstlisting}

\section{Group Size Analysis}
\section{组大小分析}

\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
$G$ & \textbf{Signal Quality} & \textbf{Compute} & \textbf{When to Use} \\
$G$ & \textbf{信号质量} & \textbf{计算量} & \textbf{使用时机} \\
\midrule
2 & Very noisy (coin flip) & Low & Never recommended --- too noisy for stable learning \\
2 & 非常嘈杂（如同抛硬币） & 低 & 绝不推荐——噪声太大，无法稳定学习 \\
4 & Moderate & Moderate & Quick experiments, easy tasks (pass rate $>$ 50\%) \\
4 & 中等 & 中等 & 快速实验、简单任务（通过率 $>$ 50\%） \\
8 & Good (standard) & High & Default. Good balance for most tasks \\
8 & 良好（标准） & 高 & 默认值。对大多数任务而言平衡良好 \\
16 & Excellent & Very high & Hard tasks (pass rate $<$ 20\%), need many attempts to get positives \\
16 & 优秀 & 非常高 & 困难任务（通过率 $<$ 20\%），需要多次尝试才能获得正例 \\
32 & Near-perfect & Extreme & Only if you have massive compute and very hard task \\
32 & 近乎完美 & 极高 & 仅在拥有海量计算资源和非常困难的任务时使用 \\
\bottomrule
\end{tabular}

\begin{keybox}[Critical: Group Must Contain Both Successes and Failures]
If all $G$ responses are correct ($r_i = 1 \;\forall i$): all advantages = 0, no learning signal!\\
如果所有 $G$ 个响应都正确（$r_i = 1 \;\forall i$）：所有优势值均为 0，无学习信号！

If all wrong: same problem. The prompt’s difficulty must match model’s capability.\\
如果全部错误：同样的问题。提示的难度必须与模型能力匹配。

\textbf{Goldilocks rule}: Filter prompts to 20--80\% pass rate for current model. Re-filter every 500 steps as model improves.
\textbf{金发姑娘规则}：将提示过滤至当前模型 20\%--80\% 的通过率。随模型改进，每 500 步重新过滤。
\end{keybox}

\section{GRPO Variants and Extensions}
\section{GRPO 变体与扩展}

\subsection{Diversity in GRPO Groups}
\subsection{GRPO 组内的多样性}

\begin{intuitionbox}[Mode Collapse in RL Training]
Without diversity pressure, RL-trained LLMs collapse to a narrow set of high-reward responses:
在缺乏多样性压力的情况下，经过RL训练的LLM会崩溃至一小部分高奖励响应：


Now produce the bilingual translation following ALL rules above. Start directly with the translated content (no preamble).
现在按照所有上述规则生成双语翻译。直接以翻译后的内容开头（无需前言）。

\begin{itemize}
  \item The model learns one ``template'' answer for each question type
  \item 模型针对每种问题类型学习一个“模板”答案
  \item Entropy drops rapidly; the model becomes deterministic
  \item 熵迅速下降；模型变得确定化
  \item Reward hacking becomes easier (narrow outputs are easier to exploit)
  \item 奖励破解（Reward Hacking）变得更容易（窄输出更易被利用）
  \item Generalization suffers: the model memorizes reward patterns, not reasoning
  \item 泛化能力受损：模型记忆奖励模式，而非推理过程
\end{itemize}

The KL penalty $\beta D_\text{KL}[\pi_\theta \| \pi_\text{ref}]$ is the primary diversity mechanism, but it’s not sufficient alone.
KL惩罚项 $\beta D_\text{KL}[\pi_\theta \| \pi_\text{ref}]$ 是主要的多样性机制，但单独使用并不足够。
\end{intuitionbox}


\begin{keybox}[GRPO Group Diversity]
\begin{keybox}[GRPO 组多样性]
GRPO generates $N$ responses per prompt and uses within-group ranking. Diversity within the group is critical:
GRPO 为每个提示生成 $N$ 个响应，并使用组内排序。组内多样性至关重要：

\begin{itemize}
  \item \textbf{High temperature} ($\tau=0.8$--$1.0$): Ensures varied responses for meaningful comparison
  \item \textbf{高温度}（$\tau=0.8$--$1.0$）：确保响应多样，以便进行有意义的比较
  \item \textbf{Large $N$} (8--16): More samples = more likely to include both good and bad approaches
  \item \textbf{较大的 $N$}（8--16）：样本越多，越可能同时包含好的和坏的方法
  \item \textbf{DAPO’s ``No Repeat'' penalty}: Rejects duplicate responses within a group to force exploration
  \item \textbf{DAPO 的“无重复”惩罚项}：拒绝组内重复的响应，以强制探索
  \item If all $N$ responses are identical: advantage is zero, no learning signal
  \item 如果所有 $N$ 个响应都相同：优势为零，无学习信号
  \item If responses are too diverse (random): reward signal is noisy, slow learning
  \item 如果响应过于多样（随机）：奖励信号噪声大，学习缓慢
\end{itemize}

\textbf{Sweet spot}: Temperature that gives distinct approaches while staying on-topic.
\textbf{最佳点}：既能生成不同方法，又能保持主题相关的温度设置。
\end{keybox}


\begin{table}[ht!]
\centering
\caption{Diversity-promoting methods for RL training.}
\caption{RL训练中促进多样性的方法。}
\begin{tabular}{@{}lp{11cm}@{}}
\toprule
\textbf{Method} & \textbf{How It Promotes Diversity} \\
\textbf{方法} & \textbf{如何促进多样性} \\
\midrule
Entropy bonus & Add $\alpha H(\pi_\theta)$ to the reward. Directly penalizes low-entropy (deterministic) policies. \\
熵奖励 & 将 $\alpha H(\pi_\theta)$ 加入奖励。直接惩罚低熵（确定化）策略。 \\
KL penalty & $-\beta D_\text{KL}[\pi_\theta \| \pi_\text{ref}]$ prevents collapse toward a single mode. \\
KL惩罚项 & $-\beta D_\text{KL}[\pi_\theta \| \pi_\text{ref}]$ 防止坍缩到单一模式。 \\
Rejection sampling & Generate many candidates, keep top-$k$ by reward. Naturally selects for diverse high-quality responses. \\
拒绝采样 & 生成大量候选，按奖励保留前 $k$ 个。自然选择多样化的高质量响应。 \\
Best-of-N & At inference: generate $N$ responses, score all, return the best. Diversity comes from sampling. \\
最佳N选一 & 推理时：生成 $N$ 个响应，对全部打分，返回最佳。多样性来自采样。 \\
DPO with diverse pairs & Train on pairs where chosen/rejected differ in \emph{approach}, not just quality. \\
使用多样化成对的DPO & 在“选中/拒绝”成对数据上训练，这些对在\emph{方法}上不同，而不仅仅是质量。 \\
Multi-reward & Use multiple reward models (safety, helpfulness, code quality). Prevents collapsing to one dimension. \\
多奖励 & 使用多个奖励模型（安全性、有用性、代码质量）。防止坍缩到单一维度。 \\
\bottomrule
\end{tabular}
\end{table}


\begin{warningbox}[Diversity vs. Quality Tradeoff]
\begin{warningbox}[多样性与质量的权衡]
More diversity is not always better:
并非多样性越多越好：

\begin{itemize}
  \item Too much diversity (high entropy) = random, unhelpful responses
  \item 多样性过多（高熵）= 随机、无帮助的响应
  \item Too little diversity (low entropy) = repetitive, reward-hacked responses
  \item 多样性过少（低熵）= 重复、奖励破解的响应
  \item \textbf{Monitor}: Track response entropy, unique n-gram ratio, and reward distribution width during training. If all three are dropping simultaneously, you have a collapse problem.
  \item \textbf{监测}：训练期间追踪响应熵、唯一 n-gram 比例和奖励分布宽度。如果三者同时下降，则存在坍缩问题。
\end{itemize}
\end{warningbox}


\subsubsection{Verbalized Sampling for RL Data Collection}
\subsubsection{用于RL数据收集的言语化采样（Verbalized Sampling）}
\label{verbalized-sampling-for-rl-data-collection}
\label{verbalized-sampling-for-rl-data-collection}

Post-training alignment (RLHF, DPO) often reduces output diversity due to \emph{typicality bias}: human annotators systematically prefer familiar, ``typical'' text over novel alternatives. This mode collapse is a data-level phenomenon, not purely algorithmic.
训练后对齐（RLHF、DPO）常因\emph{典型性偏差（Typicality Bias）}而降低输出多样性：人工标注者系统性地偏好熟悉、“典型”的文本，而非新颖的替代方案。这种模式坍缩（Mode Collapse）是数据层面的现象，而非纯算法问题。

Verbalized Sampling (VS)~\cite{zhang2025verbalized} is a training-free prompting strategy that circumvents this collapse by asking the model to \textbf{explicitly verbalize a probability distribution} over multiple responses in a single generation.
言语化采样（Verbalized Sampling, VS）~\cite{zhang2025verbalized} 是一种无需训练的提示策略，通过要求模型在单次生成中\textbf{明确言语化一个概率分布}（覆盖多个响应）来规避此坍缩。

\begin{keybox}[Verbalized Sampling – Core Idea]
\begin{keybox}[言语化采样 – 核心思想]
Instead of sampling a single response (which collapses to the mode), prompt the model to output \emph{multiple candidate responses along with their probabilities}:
不采样单一响应（这会坍缩到众数），而是提示模型输出\emph{多个候选响应及其概率}：

\texttt{‘‘Generate 5 jokes about coffee and their corresponding probabilities.’’}
\texttt{“生成5个关于咖啡的笑话及其对应的概率。”}

The model produces a list like:
模型生成如下列表：

\begin{enumerate}
  \item Joke A (probability: 0.35)
  \item 笑话 A（概率：0.35）
  \item Joke B (probability: 0.25)
  \item 笑话 B（概率：0.25）
  \item Joke C (probability: 0.20)
  \item 笑话 C（概率：0.20）
  \item Joke D (probability: 0.12)
  \item 笑话 D（概率：0.12）
  \item Joke E (probability: 0.08)
  \item 笑话 E（概率：0.08）
\end{enumerate}

Then sample from this verbalized distribution. Because the model explicitly represents the full distribution (not just the argmax), lower-probability but creative/diverse responses become accessible.
然后从这个言语化分布中采样。由于模型显式地表示了完整分布（而不仅仅是 argmax），低概率但具有创造性和多样性的响应也变得可访问。
\end{keybox}


\begin{lstlisting}[style=pythonstyle]
