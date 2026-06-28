## GRPO --- Group Relative Policy Optimization
## GRPO —— 组相对策略优化

Group Relative Policy Optimization (GRPO)~\cite{shao2024deepseekmath} is a reinforcement learning algorithm designed specifically for language models that eliminates the need for a separate value network (critic). Introduced by DeepSeek as part of their DeepSeekMath work and later scaled to DeepSeek-R1~\cite{deepseek2025r1}, GRPO has rapidly become the dominant RL method for LLM training---adopted by most open-source alignment frameworks (TRL, OpenRLHF, veRL) as the default algorithm.
组相对策略优化（Group Relative Policy Optimization, GRPO）~\cite{shao2024deepseekmath} 是一种专为语言模型设计的强化学习算法，它消除了对独立价值网络（critic）的需求。该算法由DeepSeek在其DeepSeekMath工作中引入，随后扩展到DeepSeek-R1~\cite{deepseek2025r1}，并迅速成为LLM训练中占主导地位的强化学习方法——被大多数开源对齐框架（TRL、OpenRLHF、veRL）采纳为默认算法。

The core idea is deceptively simple: instead of training a neural network to predict expected reward (the critic in PPO), GRPO \emph{estimates} it empirically by generating multiple responses to the same prompt and using the group’s reward statistics as a baseline. This removes an entire model from memory, halves the engineering complexity, and---surprisingly---often outperforms PPO because empirical baselines are more accurate than a poorly-trained value function.
其核心思想看似简单：GRPO 并非训练一个神经网络来预测期望奖励（即PPO中的critic），而是通过为同一提示生成多个响应，并利用该组奖励的统计量作为基线，来\emph{经验性地估计}奖励。这样可以从内存中移除整个模型，将工程复杂度减半，而且——令人惊讶的是——它常常优于PPO，因为经验基线比训练欠佳的价值函数更加准确。

GRPO is particularly effective for:
GRPO 特别适用于以下场景：

\begin{itemize}
  \item \textbf{Reasoning tasks} with verifiable rewards (math, code) where binary correctness provides a clean signal.
  \item \textbf{Reasoning tasks (推理任务)} 具有可验证奖励（数学、代码），此时二元正确性提供了清晰的信号。
  \item \textbf{Large models} (70B+) where the memory savings from removing the critic are critical.
  \item \textbf{Large models (大型模型)} (70B+)，此时移除critic所节省的内存至关重要。
  \item \textbf{Multi-turn and agentic settings} where value estimation across tool calls is intractable.
  \item \textbf{Multi-turn and agentic settings (多轮与智能体场景)}，此时跨工具调用的价值估计难以处理。
\end{itemize}

This chapter covers GRPO’s motivation, algorithm, key variants (Dr.~GRPO, DAPO, 2-GRPO, GDPO), and practical implementation with TRL.
本章涵盖GRPO的动机、算法、关键变体（Dr.~GRPO、DAPO、2-GRPO、GDPO）以及基于TRL的实践实现。

\section{Motivation}
\section{动机}

PPO’s value model (critic) has three major problems for language:
PPO的价值模型（critic）在语言任务中面临三个主要问题：

\begin{enumerate}
  \item \textbf{Memory}: The value head shares the policy backbone (140GB for 70B). Doubles memory if separate.
  \item \textbf{Memory (内存)}：价值头与策略主干共享（70B模型为140GB）。若分离则内存翻倍。
  \item \textbf{Accuracy}: Predicting expected reward for a partial sequence is extremely hard. The value function is often wrong $\rightarrow$ wrong advantages $\rightarrow$ wrong gradient direction.
  \item \textbf{Accuracy (准确性)}：对部分序列预测期望奖励极其困难。价值函数常常错误 $\rightarrow$ 错误的优势函数 $\rightarrow$ 错误的梯度方向。
  \item \textbf{Training}: Value head needs many samples to converge. During early RL, it gives noisy predictions that destabilize policy learning.
  \item \textbf{Training (训练)}：价值头需要大量样本才能收敛。在强化学习早期，它给出噪声预测，破坏策略学习的稳定性。
\end{enumerate}

\textbf{GRPO’s key insight}~\cite{shao2024deepseekmath}: Instead of learning $V(s)$, \emph{estimate} it empirically from a group of samples. Generate $G$ responses to the same prompt, compute their rewards, and use the group statistics as the baseline.
\textbf{GRPO的关键洞察}~\cite{shao2024deepseekmath}：不学习 $V(s)$，而是从一组样本中经验性地\emph{估计}它。为同一提示生成 $G$ 个响应，计算其奖励，并使用组统计量作为基线。

\section{Algorithm}
\section{算法}

\begin{enumerate}
  \item For each prompt $x$, sample $G$ completions: $\{y_1, \ldots, y_G\} \sim \pi_\theta(\cdot|x)$
  \item 对于每个提示 $x$，采样 $G$ 个补全：$\{y_1, \ldots, y_G\} \sim \pi_\theta(\cdot|x)$
  \item Score each: $r_i = R(x, y_i)$
  \item 评分每个：$r_i = R(x, y_i)$
  \item Normalize within group: $\hat{A}_i = \frac{r_i - \mu_G}{\sigma_G}$ where $\mu_G = \frac{1}{G}\sum_j r_j$, $\sigma_G = \text{std}(\{r_j\})$
  \item 组内归一化：$\hat{A}_i = \frac{r_i - \mu_G}{\sigma_G}$，其中 $\mu_G = \frac{1}{G}\sum_j r_j$，$\sigma_G = \text{std}(\{r_j\})$
  \item Apply PPO-style clipped update using these advantages
  \item 使用这些优势值应用PPO风格的裁剪更新
\end{enumerate}

\begin{equation}
\boxed{\hat{A}_i = \frac{r_i - \mu_G}{\sigma_G}, \qquad L = \mathbb{E}\left[\min\left(r_t(\theta)\hat{A}_i,\; \text{clip}(r_t(\theta), 1{\pm}\epsilon)\hat{A}_i\right)\right] - \beta D_\text{KL}[\pi_\theta\|\pi_\text{ref}]}
\end{equation}

\begin{intuitionbox}[Why Group Normalization Works]
\textbf{The group mean approximates $V(s)$}: If you sample enough responses to the same prompt, their average reward is a Monte Carlo estimate of the expected reward = value function.
\textbf{组均值近似 $V(s)$}：如果为同一提示采样足够多的响应，它们的平均奖励就是期望奖励（即价值函数）的蒙特卡洛估计。

\textbf{Above mean = good move}: $\hat{A}_i > 0$ means this response is better than average for this prompt. Reinforce it.
\textbf{高于均值 = 好动作}：$\hat{A}_i > 0$ 表示该响应优于该提示的平均水平。强化它。

\textbf{Below mean = bad move}: $\hat{A}_i < 0$ means worse than average. Suppress it.
\textbf{低于均值 = 坏动作}：$\hat{A}_i < 0$ 表示差于平均水平。抑制它。

\textbf{Normalization}: Dividing by $\sigma_G$ ensures advantages are scale-invariant across prompts with different reward ranges.
\textbf{归一化}：除以 $\sigma_G$ 可确保优势值在具有不同奖励范围的提示之间具有尺度不变性。

\textbf{DeepSeek-R1 breakthrough}~\cite{deepseek2025r1}: Pure GRPO with binary correctness rewards ($r = 1$ if answer correct, $r = 0$ otherwise) trained on math/code spontaneously developed chain-of-thought reasoning, self-verification, and error correction --- without any explicit instruction to do so.
\textbf{DeepSeek-R1 突破}~\cite{deepseek2025r1}：纯GRPO配合二元正确性奖励（答案正确时 $r = 1$，否则 $r = 0$）在数学/代码上训练，自发形成了思维链推理、自我验证和纠错能力——没有任何明确的指令要求这样做。
\end{intuitionbox}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_029_fig29.png}
\caption{GRPO in action: $G{=}5$ responses are sampled for a single math prompt. Three are correct ($r{=}1$), two are wrong ($r{=}0$). The group mean $\mu_G{=}0.6$ acts as the baseline; correct responses receive positive advantage (reinforced), wrong ones receive negative advantage (suppressed).}
\caption{GRPO 运行示意：针对单个数学提示采样了 $G{=}5$ 个响应。其中三个正确（$r{=}1$），两个错误（$r{=}0$）。组均值 $\mu_G{=}0.6$ 作为基线；正确的响应获得正优势（被强化），错误的响应获得负优势（被抑制）。}
\end{figure}

\section{TRL Implementation}
\section{TRL 实现}

The following shows a minimal working example using HuggingFace TRL.
以下展示一个使用 HuggingFace TRL 的最小工作示例。

\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer
from transformers import AutoModelForCausalLM, AutoTokenizer


model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B-Instruct",
    torch_dtype=torch.bfloat16, attn_implementation="flash_attention_2")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")


grpo_config = GRPOConfig(
    output_dir="./grpo_output",
    num_generations=8,           # G = group size
    temperature=1.0,             # High temp for diversity within group
    max_completion_length=2048,  # Max response length
    beta=0.04,                   # KL penalty coefficient
    learning_rate=1e-6,
    per_device_train_batch_size=2,  # Prompts per device (x8 gens = 16 responses)
    gradient_accumulation_steps=8,
    num_train_epochs=2,
    bf16=True,
    gradient_checkpointing=True,
    max_grad_norm=0.5,
    logging_steps=10,
    # vLLM generation for speed (critical for GRPO due to 8x generation)
    use_vllm=True,
    vllm_gpu_memory_utilization=0.7,
)


# Reward function: binary correctness for math
def reward_fn(completions, prompts, **kwargs):
    """Return list of floats: 1.0 if correct, 0.0 if wrong."""
    """返回浮点数列表：正确则为1.0，错误则为0.0。"""
    rewards = []
    for completion, prompt in zip(completions, prompts):
        answer = extract_answer(completion)
        expected = get_ground_truth(prompt)
        rewards.append(1.0 if answer == expected else 0.0)
    return rewards


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
# Verbalized Sampling: prompt model to output distribution
def verbalized_sample(model, tokenizer, task, n=5):
    prompt = (
        f"{task}\n\n"
        f"Generate {n} different responses and assign a probability "
        f"to each (probabilities should sum to 1.0). "
        f"Format: [response] (probability: X.XX)"
    )
    output = model.generate(
        tokenizer(prompt, return_tensors="pt").input_ids,
        max_new_tokens=1024,
        temperature=0.7,
        do_sample=True,
    )
    # Parse responses and probabilities from output
    responses, probs = parse_verbalized_distribution(
        tokenizer.decode(output[0])
    )
    # Sample from the verbalized distribution
    import random
    chosen = random.choices(responses, weights=probs, k=1)[0]
    return chosen
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle]
# 言语化采样：提示模型输出分布
def verbalized_sample(model, tokenizer, task, n=5):
    prompt = (
        f"{task}\n\n"
        f"Generate {n} different responses and assign a probability "
        f"to each (probabilities should sum to 1.0). "
        f"Format: [response] (probability: X.XX)"
    )
    output = model.generate(
        tokenizer(prompt, return_tensors="pt").input_ids,
        max_new_tokens=1024,
        temperature=0.7,
        do_sample=True,
    )
    # 从输出中解析响应和概率
    responses, probs = parse_verbalized_distribution(
        tokenizer.decode(output[0])
    )
    # 从言语化分布中采样
    import random
    chosen = random.choices(responses, weights=probs, k=1)[0]
    return chosen
\end{lstlisting}

\begin{intuitionbox}[Why Verbalized Sampling Works]
\begin{intuitionbox}[为何言语化采样有效]
\begin{itemize}
  \item \textbf{Bypasses mode collapse}: Standard sampling from aligned models heavily concentrates on one or two ``safe'' responses. VS forces the model to articulate alternatives it \emph{knows} but wouldn’t normally surface.
  \item \textbf{绕过模式坍缩}：从对齐模型进行的标准采样高度集中于一两个“安全”响应。VS迫使模型表达它\emph{知道}但通常不会呈现的替代方案。
  \item \textbf{Diversity is semantic}: Unlike temperature scaling (lexical noise), VS produces genuinely different approaches---the model reasons about distinct options.
  \item \textbf{多样性是语义层面的}：与温度缩放（词汇噪声）不同，VS生成真正不同的方法——模型对不同的选项进行推理。
  \item \textbf{Scales with capability}: More capable models produce better-calibrated verbalized distributions---they benefit \emph{more} from VS (1.6--2.1$\times$ diversity gain in creative writing).
  \item \textbf{随能力扩展}：能力更强的模型能产生校准更好的言语化分布——它们从VS中获益\emph{更多}（创意写作中多样性提升1.6--2.1倍）。
  \item \textbf{Training-free}: No fine-tuning or modified decoding; works with any instruction-following model at inference time.
  \item \textbf{无需训练}：无需微调或修改解码；推理时适用于任何指令遵循模型。
  \item \textbf{For GRPO}: Use VS to generate the $G$ response candidates per prompt---ensures the group contains semantically diverse approaches rather than surface-level variations.
  \item \textbf{对于GRPO}：使用VS为每个提示生成 $G$ 个候选响应——确保组内包含语义多样的方法，而非表面级变化。
\end{itemize}
\end{intuitionbox}


Before diving into the extensions, let us briefly recap the base GRPO algorithm established in the previous sections. The core mechanism---sampling a group of completions, normalizing their rewards, and applying a clipped policy gradient---is elegant in its simplicity. However, practitioners quickly discovered specific failure modes: pretraining bias diluting gradients (Dr.~GRPO), symmetric clipping limiting exploration (DAPO), wasteful large group sizes (2-GRPO), and reward-scale imbalance in multi-objective settings (GDPO). The following sections address each of these in turn.
在深入探讨扩展之前，让我们简要回顾一下前文建立的基础GRPO算法。其核心机制——采样一组补全、对奖励进行归一化、并应用裁剪策略梯度——简洁而优雅。然而，实践者很快发现了特定的失败模式：预训练偏置稀释梯度（Dr.~GRPO）、对称裁剪限制探索（DAPO）、浪费的大组规模（2-GRPO）以及多目标场景中的奖励尺度不平衡（GDPO）。接下来的章节将逐一解决这些问题。

\begin{keybox}[GRPO Baseline Recap]
\begin{keybox}[GRPO 基线回顾]
Given a prompt $q$, sample $G$ completions $\{o_1,\dots,o_G\}$ from the current policy $\pi_\theta$. Compute rewards $\{r_1,\dots,r_G\}$ and normalise: 
给定一个提示 $q$，从当前策略 $\pi_\theta$ 中采样 $G$ 个补全 $\{o_1,\dots,o_G\}$。计算奖励 $\{r_1,\dots,r_G\}$ 并归一化：
\[
\hat{A}_i = \frac{r_i - \mu_r}{\sigma_r + \epsilon}, \qquad
  \mu_r = \frac{1}{G}\sum_{i=1}^G r_i, \quad
  \sigma_r = \sqrt{\frac{1}{G}\sum_{i=1}^G (r_i-\mu_r)^2}.
\]
 The clipped surrogate loss (per token) is: 
 裁剪后的替代损失（每token）为：
\[
\mathcal{L}_{\text{GRPO}} = -\frac{1}{G}\sum_{i=1}^G \frac{1}{|o_i|}
    \sum_{t=1}^{|o_i|}
    \min\!\Bigl(
      \rho_{i,t}\,\hat{A}_i,\;
      \mathrm{clip}(\rho_{i,t},1{-}\epsilon,1{+}\epsilon)\,\hat{A}_i
    \Bigr),
\]
 where $\rho_{i,t} = \pi_\theta(o_{i,t}|q,o_{i,<t})\,/\,\pi_{\text{old}}(o_{i,t}|q,o_{i,<t})$.
 其中 $\rho_{i,t} = \pi_\theta(o_{i,t}|q,o_{i,<t})\,/\,\pi_{\text{old}}(o_{i,t}|q,o_{i,<t})$。
\end{keybox}


\subsection{DAPO -- Dynamic Adaptive Policy Optimization}
\subsection{DAPO——动态自适应策略优化（Dynamic Adaptive Policy Optimization）}
\label{sec:dapo}
\label{sec:dapo}


\begin{intuitionbox}[Why DAPO?]
\begin{intuitionbox}[为什么需要DAPO？]
Base GRPO uses \emph{symmetric} clipping: the policy is equally constrained whether it wants to increase or decrease the probability of a token. But exploration and exploitation have different risk profiles. Increasing the probability of a good token is generally safe; suppressing a token that happened to appear in a bad completion can be catastrophically wrong if the token itself is neutral. DAPO~\cite{yu2025dapo} introduces five targeted fixes that together substantially improve training stability and final performance.
基础GRPO使用\emph{对称}裁剪：无论策略想要增加还是减少某个token的概率，它都受到同等约束。但探索与利用具有不同的风险特征。增加好token的概率通常是安全的；而抑制一个恰好出现在坏补全中的token，如果该token本身是中性的，则可能造成灾难性错误。DAPO~\cite{yu2025dapo} 引入了五个针对性的修复，共同显著提升了训练稳定性和最终性能。
\end{intuitionbox}

\subsubsection*{Component 1 -- Asymmetric Clipping (Clip-Higher)}
\subsubsection*{组件1 -- 非对称裁剪（Clip-Higher）}
\label{component-1-asymmetric-clipping-clip-higher}

Standard PPO/GRPO clips the importance ratio symmetrically at $[1-\epsilon, 1+\epsilon]$. DAPO replaces this with an asymmetric band:
标准 PPO/GRPO 在 $[1-\epsilon, 1+\epsilon]$ 范围内对称裁剪重要性比率。DAPO 将其替换为非对称区间：

\[
\boxed{
    \mathrm{clip}_{\text{DAPO}}(\rho, A) =
    \begin{cases}
      \mathrm{clip}(\rho,\, 1-\epsilon,\, 1+\epsilon_{\text{high}}) & \text{if } A > 0 \\
      \mathrm{clip}(\rho,\, 1-\epsilon,\, 1+\epsilon) & \text{if } A \le 0
    \end{cases}
  }
\]

where $\epsilon_{\text{high}} > \epsilon$ (typical values: $\epsilon=0.2$, $\epsilon_{\text{high}}=0.28$). When the advantage is positive the policy is allowed to move further toward the good token; when the advantage is negative the usual conservative clipping applies to avoid over-suppression.
其中 $\epsilon_{\text{high}} > \epsilon$（典型值：$\epsilon=0.2$，$\epsilon_{\text{high}}=0.28$）。当优势为正时，策略被允许向好的 token 移动得更远；当优势为负时，应用常规的保守裁剪以避免过度抑制。

\subsubsection*{Component 2 -- Token-Level Loss Aggregation}
\subsubsection*{组件2 -- Token级损失聚合}
\label{component-2-token-level-loss-aggregation}

Base GRPO divides the loss by the \emph{number of sequences} $G$. DAPO divides by the \emph{total number of tokens} across all sequences:
基础 GRPO 将损失除以**序列数量** $G$。DAPO 除以所有序列中的**总 token 数**：

\[
\mathcal{L}_{\text{token}} =
    -\frac{1}{\sum_{i=1}^G |o_i|}
    \sum_{i=1}^G \sum_{t=1}^{|o_i|}
    \min\!\bigl(\rho_{i,t}\hat{A}_i,\;
                \mathrm{clip}_{\text{DAPO}}(\rho_{i,t},\hat{A}_i)\,\hat{A}_i\bigr).
\]

This prevents long completions from dominating the gradient signal simply because they contain more tokens.
这可以防止长完成由于包含更多 token 而主导梯度信号。

\subsubsection*{Component 3 -- Overlong Filtering}
\subsubsection*{组件3 -- 过长过滤}
\label{component-3-overlong-filtering}

When a completion is truncated (no EOS token within the maximum length budget), it provides \emph{misleading} signal: the model is penalised for tokens that were generated correctly but happened to appear before the truncation boundary. DAPO masks these completions entirely:
当完成被截断（在最大长度预算内没有 EOS token）时，它会提供**误导性**信号：模型因被正确生成但恰好在截断边界之前出现的 token 而受到惩罚。DAPO 完全屏蔽这些完成：

\[
m_i = \mathbf{1}[\text{EOS} \in o_i], \qquad
  \mathcal{L}_{\text{filtered}} =
    -\frac{\sum_{i=1}^G m_i \sum_t (\cdots)}{\sum_{i=1}^G m_i |o_i|}.
\]

\subsubsection*{Component 4 -- Soft Overlong Punishment}
\subsubsection*{组件4 -- 软性过长惩罚}
\label{component-4-soft-overlong-punishment}

Rather than a hard mask, a softer variant applies a length penalty that grows smoothly as completions approach the maximum length $L_{\max}$:
与硬屏蔽不同，一种更柔和的变体应用了长度惩罚，该惩罚随着完成接近最大长度 $L_{\max}$ 而平滑增长：

\[
r_i \leftarrow r_i - \lambda \cdot \max\!\left(0,\, \frac{|o_i| - L_{\text{cache}}}{L_{\max} - L_{\text{cache}}}\right),
\]

where $L_{\text{cache}}$ is a ``safe'' length threshold.
其中 $L_{\text{cache}}$ 是一个“安全”长度阈值。

\subsubsection*{Component 5 -- Dynamic Sampling}
\subsubsection*{组件5 -- 动态采样}
\label{component-5-dynamic-sampling}

DAPO re-samples prompts whose entire group of completions receives the same reward (all correct or all incorrect), because such groups contribute zero gradient after normalisation. This keeps the effective batch size stable throughout training.
DAPO 会重新采样那些整组完成获得相同奖励（全对或全错）的提示，因为此类组在归一化后贡献的梯度为零。这使有效批量大小在整个训练过程中保持稳定。

\begin{examplebox}[DAPO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer

config = GRPOConfig(
    # Asymmetric clipping
    # 非对称裁剪
    epsilon=0.2,
    epsilon_high=0.28,          # Clip-Higher
    # Token-level loss
    # Token级损失
    loss_type="dapo",           # enables token-level aggregation
                                # 启用token级聚合
    # Overlong filtering
    # 过长过滤
    mask_truncated_completions=True,
    # Generation budget
    # 生成预算
    max_completion_length=1024,
    num_generations=8,
    # Note: DAPO loss internally handles zero-variance group filtering
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
    # Sequence-level importance sampling
    # 序列级重要性采样
    importance_sampling_level="sequence",   # GSPO mode
                                            # GSPO 模式
    # Off-policy: reuse each batch for multiple gradient steps
    # 离策略：将每个批次用于多个梯度步
    steps_per_generation=4,
    num_generations=8,
    epsilon=0.2,
)

trainer = GRPOTrainer(
    model=model,
    reward_funcs=[reward_fn],
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\begin{warningbox}[When to Use GSPO]
GSPO is most beneficial when \texttt{steps\_per\_generation > 1} (off-policy training). For purely on-policy training ($\text{steps\_per\_generation}=1$) the difference from GRPO is negligible. Off-policy training can dramatically reduce generation cost (the most expensive step), making GSPO + off-policy a strong efficiency choice.
GSPO 在 \texttt{steps\_per\_generation > 1}（离策略训练）时最为有益。对于纯在策略训练（$\text{steps\_per\_generation}=1$），与 GRPO 的差异可以忽略不计。离策略训练可以显著降低生成成本（最昂贵的步骤），使 GSPO + 离策略成为高效的选择。
\end{warningbox}

\subsection{Dr.~GRPO -- Debiased Reward GRPO}
\subsection{Dr.~GRPO -- 去偏奖励 GRPO}
\label{sec:dr-grpo}

\begin{intuitionbox}[The Pretraining Bias Problem]
Standard GRPO normalises advantages within a group, but the \emph{pretraining distribution} introduces a systematic bias: tokens that are common in pretraining data receive large gradients even when they carry no task-relevant information. Dr.~GRPO~\cite{liu2024drgrpo} identifies and corrects this bias, focusing gradient signal on \emph{informative} tokens.
标准 GRPO 对组内的优势进行归一化，但**预训练分布**引入了一种系统性偏差：在预训练数据中常见的 token 即使不携带任何任务相关信息，也会获得较大的梯度。Dr.~GRPO~\cite{liu2024drgrpo} 识别并纠正了这种偏差，将梯度信号聚焦在**信息性** token 上。
\end{intuitionbox}

Dr.~GRPO modifies the per-token gradient weight to account for the token’s marginal contribution to the reward signal. Tokens that the model already assigns high probability to (regardless of the reward) are down-weighted:
Dr.~GRPO 修改了每个 token 的梯度权重，以考虑 token 对奖励信号的边际贡献。模型已经赋予高概率的 token（无论奖励如何）被降低权重：

\[
w_{i,t} = \hat{A}_i \cdot \bigl(1 - \pi_{\text{ref}}(o_{i,t}|q,o_{i,<t})\bigr),
\]

where $\pi_{\text{ref}}$ is the reference (pretrained) model. This is a form of \emph{token efficiency}: the gradient is concentrated on tokens where the policy genuinely needs to change.
其中 $\pi_{\text{ref}}$ 是参考（预训练）模型。这是一种**token 效率**的形式：梯度集中在策略真正需要改变的 token 上。

\begin{examplebox}[Dr.~GRPO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer

config = GRPOConfig(
    loss_type="dr_grpo",
    num_generations=8,
    beta=0.04,   # KL penalty coefficient
                 # KL 惩罚系数
)

trainer = GRPOTrainer(
    model=model,
    ref_model=ref_model,   # required for token weighting
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
    # With G=2, batch size must be at least 2 * num_prompts_per_step
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
\begin{examplebox}[TRL 中的 2-GRPO]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    num_generations=2,      # 关键变化——仅两次生成
    loss_type="grpo",       # 标准 GRPO 损失即可
    epsilon=0.2,
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


# Truncated IS correction for vLLM probability mismatch
config_tis = GRPOConfig(
    use_vllm=True,
    vllm_importance_sampling_correction=True,
    vllm_importance_sampling_mode="sequence_truncate",  # TIS
    vllm_importance_sampling_cap=5.0,                   # C threshold
)


# Masked IS correction
config_mis = GRPOConfig(
    use_vllm=True,
    vllm_importance_sampling_correction=True,
    vllm_importance_sampling_mode="sequence_mask",      # MIS
    vllm_importance_sampling_cap=3.0,
)
\end{lstlisting}
\end{examplebox}
\begin{examplebox}[TRL 中的 TIS 和 MIS]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


# 针对 vLLM 概率不匹配的截断 IS 校正
config_tis = GRPOConfig(
    use_vllm=True,
    vllm_importance_sampling_correction=True,
    vllm_importance_sampling_mode="sequence_truncate",  # TIS
    vllm_importance_sampling_cap=5.0,                   # C 阈值
)


# 掩码 IS 校正
config_mis = GRPOConfig(
    use_vllm=True,
    vllm_importance_sampling_correction=True,
    vllm_importance_sampling_mode="sequence_mask",      # MIS
    vllm_importance_sampling_cap=3.0,
)
\end{lstlisting}
\end{examplebox}

\begin{keybox}[When to Use TIS/MIS]
\begin{itemize}
  \item \textbf{Always} consider enabling when using vLLM for generation.
  \item \textbf{始终}考虑在使用 vLLM 进行生成时启用。
  \item TIS is preferred when the mismatch is small (same model, different precision).
  \item 当不匹配较小时（相同模型，不同精度），首选 TIS。
  \item MIS is preferred when the mismatch is large or unpredictable.
  \item 当不匹配较大或不可预测时，首选 MIS。
  \item Sequence-level IS is theoretically preferred; token-level is a practical compromise.
  \item 序列级 IS 在理论上更优；token 级是实用的折衷方案。
\end{itemize}
\end{keybox}

## VESPO -- Variational Sequence-Level Soft Policy Optimization
## VESPO -- 变分序列级软策略优化

\label{sec:vespo}

\begin{intuitionbox}[Principled Reward Reshaping]
Most GRPO variants modify the clipping mechanism heuristically. VESPO derives a principled reward-reshaping kernel from a variational inference framework, treating policy optimisation as approximate posterior inference. VESPO~\cite{luo2025vespo} derives a resulting kernel that is smooth, asymmetric, and naturally handles staleness in asynchronous or off-policy training.
\end{intuitionbox}

\begin{intuitionbox}[基于原则的奖励重塑]
大多数 GRPO 变体启发式地修改裁剪机制。VESPO 从变分推理框架中推导出一个有原则的奖励重塑核，将策略优化视为近似后验推理。VESPO~\cite{luo2025vespo} 导出的核是平滑的、非对称的，并且自然地处理异步或离策略训练中的陈旧性。
\end{intuitionbox}

VESPO derives a weighting function $W(\tau)$ for each trajectory $\tau$ from the variational objective. The final gradient weight takes the form:

VESPO 从变分目标中为每个轨迹 $\tau$ 推导出一个加权函数 $W(\tau)$。最终的梯度权重形式如下：

\[
\boxed{
    g(\tau) = W(\tau)^k \cdot \exp\!\bigl(\lambda(1 - W(\tau))\bigr),
  }
\]

where $W(\tau) = \pi_\theta(\tau)/\pi_{\text{old}}(\tau)$ is the sequence-level importance weight, $k$ controls the sharpness of the weighting, and $\lambda$ controls the exponential decay for stale (low-weight) trajectories. This kernel:

其中 $W(\tau) = \pi_\theta(\tau)/\pi_{\text{old}}(\tau)$ 是序列级别的重要性权重，$k$ 控制加权的锐度，$\lambda$ 控制对陈旧（低权重）轨迹的指数衰减。该核：

\begin{itemize}
  \item Is smooth everywhere (no discontinuous gradient at clip boundaries).
  \item Naturally down-weights stale trajectories ($W \ll 1$) via the exponential term.
  \item Is asymmetric: high-weight trajectories ($W > 1$) are treated differently from low-weight ones.
\end{itemize}

\begin{itemize}
  \item 处处平滑（在裁剪边界处无梯度不连续）。
  \item 通过指数项自然地降低陈旧轨迹（$W \ll 1$）的权重。
  \item 非对称：高权重轨迹（$W > 1$）与低权重轨迹的处理方式不同。
\end{itemize}

\begin{examplebox}[VESPO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    loss_type="vespo",
    vespo_k_pos=2.0,         # sharpness exponent (positive advantages)
    vespo_lambda_pos=3.0,    # staleness decay (positive advantages)
    num_generations=8,
    steps_per_generation=2,  # off-policy; VESPO handles staleness
)


trainer = GRPOTrainer(
    model=model,
    reward_funcs=[reward_fn],
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[TRL 中的 VESPO]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    loss_type="vespo",
    vespo_k_pos=2.0,         # 锐度指数（正优势）
    vespo_lambda_pos=3.0,    # 陈旧性衰减（正优势）
    num_generations=8,
    steps_per_generation=2,  # 离策略；VESPO 处理陈旧性
)


trainer = GRPOTrainer(
    model=model,
    reward_funcs=[reward_fn],
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\subsection{DPPO -- Direct Policy Divergence Policy Optimization}
\subsection{DPPO -- 直接策略散度策略优化}

\label{sec:dppo}

\begin{intuitionbox}[The Problem with Ratio Clipping]
PPO's ratio clipping is a proxy for constraining the KL divergence between old and new policy. But the proxy is imperfect: clipping over-penalises low-probability tokens (where a small absolute change in probability corresponds to a large ratio change) and under-penalises high-probability tokens (where a large absolute change corresponds to a small ratio change). DPPO~\cite{an2025dppo} replaces ratio clipping with \emph{direct divergence estimates}.
\end{intuitionbox}

\begin{intuitionbox}[比率裁剪的问题]
PPO 的比率裁剪是约束新旧策略之间 KL 散度的一种代理。但该代理并不完美：裁剪过度惩罚了低概率 token（概率的微小绝对变化对应比率的巨大变化），而欠惩罚了高概率 token（概率的大幅绝对变化对应比率的微小变化）。DPPO~\cite{an2025dppo} 用 \emph{直接散度估计} 取代了比率裁剪。
\end{intuitionbox}

DPPO computes the trust region constraint directly using either Total Variation (TV) or KL divergence between the old and new policy distributions:

DPPO 直接使用新旧策略分布之间的总变差（TV）或 KL 散度来计算信任区域约束：

\[
\mathcal{L}_{\text{DPPO}} = -\mathbb{E}\!\left[
    \hat{A} \cdot \pi_\theta(o|q) \cdot \mathbf{1}[D(\pi_\theta \| \pi_{\text{old}}) \le \delta]
  \right],
\]

where $D$ is the chosen divergence measure. In practice, DPPO approximates this with token-level binary or top-$k$ masks:

其中 $D$ 是所选散度度量。在实践中，DPPO 通过 token 级别的二值掩码或 top-$k$ 掩码来近似：

\begin{itemize}
  \item \textbf{binary\_tv}: mask tokens where $|\pi_\theta - \pi_{\text{old}}| > \delta$.
  \item \textbf{binary\_kl}: mask tokens where $\pi_\theta \log(\pi_\theta/\pi_{\text{old}}) > \delta$.
  \item \textbf{topk\_tv}: keep only the top-$k$ tokens by TV contribution.
  \item \textbf{topk\_kl}: keep only the top-$k$ tokens by KL contribution.
\end{itemize}

\begin{itemize}
  \item \textbf{binary\_tv}: 掩码掉 $|\pi_\theta - \pi_{\text{old}}| > \delta$ 的 token。
  \item \textbf{binary\_kl}: 掩码掉 $\pi_\theta \log(\pi_\theta/\pi_{\text{old}}) > \delta$ 的 token。
  \item \textbf{topk\_tv}: 仅保留 TV 贡献最大的 top-$k$ 个 token。
  \item \textbf{topk\_kl}: 仅保留 KL 贡献最大的 top-$k$ 个 token。
\end{itemize}

\begin{examplebox}[DPPO – Conceptual Implementation]
DPPO is not yet available as a built-in TRL trainer. A custom implementation would use GRPOTrainer with a modified loss that clips based on distributional divergence (TV or KL) rather than the standard probability ratio:

\begin{lstlisting}[style=pythonstyle]
# Pseudocode: DPPO requires a custom trainer subclass
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    num_generations=8,
    beta=0.04,
)
# Override the loss computation to use distributional clipping:
# clip when TV(pi_new || pi_old) > delta, rather than when
# pi_new/pi_old exceeds [1-eps, 1+eps]
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[DPPO – 概念性实现]
DPPO 尚未作为内置 TRL 训练器提供。自定义实现将使用 GRPOTrainer，并修改损失函数，使其基于分布散度（TV 或 KL）而非标准概率比率进行裁剪：

\begin{lstlisting}[style=pythonstyle]
# 伪代码：DPPO 需要自定义训练器子类
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    num_generations=8,
    beta=0.04,
)
# 覆盖损失计算以使用分布裁剪：
# 当 TV(pi_new || pi_old) > delta 时裁剪，而不是
# pi_new/pi_old 超过 [1-eps, 1+eps]
\end{lstlisting}
\end{examplebox}

\begin{warningbox}[DPPO is Research-Stage]
DPPO is a recent research contribution and is not yet integrated into mainstream RL libraries. It is most useful when you observe that standard ratio clipping is failing (e.g., on tasks with highly skewed token probability distributions).
\end{warningbox}

\begin{warningbox}[DPPO 处于研究阶段]
DPPO 是一项最新的研究贡献，尚未集成到主流 RL 库中。当你观察到标准比率裁剪失效时（例如，在 token 概率分布高度偏斜的任务上），它最为有用。
\end{warningbox}

\subsection{ScaleRL and CISPO}
\subsection{ScaleRL 与 CISPO}

\label{sec:scalerl-cispo}

\begin{intuitionbox}[Scaling Laws for RL]
The ScaleRL paper~\cite{luo2025scalerl} conducts a systematic study of what makes RL training for LLMs scale effectively. The key finding is that two modifications -- batch-level reward scaling and DAPO-style token-level loss -- together unlock strong performance at scale, while neither alone is sufficient. CISPO (Clipped IS Policy Optimization) is the resulting algorithm.
\end{intuitionbox}

\begin{intuitionbox}[RL 的缩放定律]
ScaleRL 论文~\cite{luo2025scalerl} 系统研究了使 LLM 的 RL 训练有效扩展的因素。关键发现是：两个修改——批次级别的奖励缩放和 DAPO 风格的 token 级别损失——共同在规模化下释放了强大性能，而单独任何一个都不足以实现。CISPO（裁剪的重要性采样策略优化，Clipped IS Policy Optimization）是最终得到的算法。
\end{intuitionbox}

\subsubsection*{Batch-Level Reward Scaling}
\subsubsection*{批次级别奖励缩放}

\label{batch-level-reward-scaling}

Standard GRPO normalises rewards within a group of $G$ completions for a single prompt. CISPO normalises rewards across the \emph{entire batch}:

标准 GRPO 对单个提示的一组 $G$ 个完成中的奖励进行归一化。而 CISPO 在 \emph{整个批次} 上对奖励进行归一化：

\[
\hat{A}_i = \frac{r_i - \mu_{\text{batch}}}{\sigma_{\text{batch}} + \epsilon},
\]

where $\mu_{\text{batch}}$ and $\sigma_{\text{batch}}$ are computed over all rewards in the current training batch. This provides a more stable baseline and prevents any single prompt from dominating the gradient.

其中 $\mu_{\text{batch}}$ 和 $\sigma_{\text{batch}}$ 是在当前训练批次中的所有奖励上计算的。这提供了更稳定的基线，并防止任何单个提示主导梯度。

\subsubsection*{CISPO Loss}
\subsubsection*{CISPO 损失}

\label{cispo-loss}

CISPO combines batch-level scaling with DAPO's token-level loss aggregation and asymmetric clipping:

CISPO 将批次级别缩放与 DAPO 的 token 级别损失聚合以及非对称裁剪相结合：

\[
\mathcal{L}_{\text{CISPO}} =
    -\frac{1}{\sum_{i,t} m_{i,t}}
    \sum_{i=1}^G \sum_{t=1}^{|o_i|} m_{i,t} \cdot
    \min\!\bigl(\rho_{i,t}\hat{A}_i,\;
               \mathrm{clip}_{\text{DAPO}}(\rho_{i,t},\hat{A}_i)\,\hat{A}_i\bigr),
\]

where $m_{i,t}$ is the overlong-filtering mask.

其中 $m_{i,t}$ 是超长过滤掩码。

\begin{examplebox}[CISPO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    loss_type="cispo",
    scale_rewards="batch",          # batch-level reward normalisation
    mask_truncated_completions=True,
    epsilon=0.2,
    epsilon_high=5.0,               # epsilon_max for CISPO (ScaleRL paper)
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

\begin{examplebox}[TRL 中的 CISPO]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    loss_type="cispo",
    scale_rewards="batch",          # 批次级别奖励归一化
    mask_truncated_completions=True,
    epsilon=0.2,
    epsilon_high=5.0,               # CISPO 的 epsilon_max（ScaleRL 论文）
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

\begin{keybox}[ScaleRL Key Findings]
\begin{enumerate}
  \item Batch-level reward scaling alone: modest improvement.
  \item Token-level loss alone: modest improvement.
  \item Both together: \textbf{synergistic} -- significantly better than either alone.
  \item Larger batch sizes benefit more from batch-level scaling.
  \item CISPO is the recommended default for large-scale RL training.
\end{enumerate}
\end{keybox}

\begin{keybox}[ScaleRL 关键发现]
\begin{enumerate}
  \item 仅批次级别奖励缩放：适度改进。
  \item 仅 token 级别损失：适度改进。
  \item 两者结合：\textbf{协同} —— 显著优于单独的任一方法。
  \item 更大的批次大小从批次级别缩放中获益更多。
  \item CISPO 是大规模 RL 训练的推荐默认选项。
\end{enumerate}
\end{keybox}

\subsection{GDPO -- Group Reward-Decoupled Policy Optimization}
\subsection{GDPO -- 组奖励解耦策略优化}

\label{sec:gdpo}

\begin{intuitionbox}[The Multi-Reward Collapse Problem]
In multi-objective RL (e.g., optimising for both correctness and format), standard GRPO normalises the \emph{combined} reward. If one reward has much higher variance than another, it dominates the normalised advantage, effectively ignoring the other reward. This is \emph{advantage collapse}: the low-variance reward contributes near-zero gradient. GDPO~\cite{zhong2025gdpo} normalises each reward \emph{independently} before aggregating.
\end{intuitionbox}

\begin{intuitionbox}[多奖励崩溃问题]
在多目标 RL 中（例如，同时优化正确性和格式），标准 GRPO 对\emph{组合}奖励进行归一化。如果一个奖励的方差远高于另一个，它会主导归一化优势，实际上忽略了另一个奖励。这就是\emph{优势崩溃}：低方差奖励贡献近乎为零的梯度。GDPO~\cite{zhong2025gdpo} 在聚合之前\emph{独立地}归一化每个奖励。
\end{intuitionbox}

The core mechanism normalises each reward \emph{independently} before aggregating:

核心机制是在聚合之前\emph{独立地}归一化每个奖励：

\[
\boxed{
    \hat{A}_n^{(i)} = \frac{r_n^{(i)} - \mu_n}{\sigma_n + \epsilon}, \qquad
    \hat{A}^{(i)} = \sum_{n=1}^N w_n \hat{A}_n^{(i)},
  }
\]

where $r_n^{(i)}$ is the $n$-th reward for completion $i$, $\mu_n$ and $\sigma_n$ are the mean and standard deviation of reward $n$ within the group, and $w_n$ are user-specified weights.

其中 $r_n^{(i)}$ 是完成 $i$ 的第 $n$ 个奖励，$\mu_n$ 和 $\sigma_n$ 是该组内第 $n$ 个奖励的均值和标准差，$w_n$ 是用户指定的权重。

\begin{keybox}[GDPO vs Standard Multi-Reward GRPO（GDPO对比标准多奖励GRPO）]
\begin{itemize}
  \item \textbf{Standard}: $\hat{A}^{(i)} = \frac{\sum_n w_n r_n^{(i)} - \mu_{\text{combined}}}{\sigma_{\text{combined}}}$. High-variance rewards dominate.
  \item \textbf{标准方法}：$\hat{A}^{(i)} = \frac{\sum_n w_n r_n^{(i)} - \mu_{\text{combined}}}{\sigma_{\text{combined}}}$。高方差的奖励主导。
  \item \textbf{GDPO}: normalise each reward separately, then combine. Each reward contributes proportionally to its weight $w_n$.
  \item \textbf{GDPO}：分别对每个奖励进行归一化，然后组合。每个奖励按其权重 $w_n$ 成比例贡献。
  \item GDPO is essential when rewards have very different scales or variances.
  \item 当奖励的量纲或方差差异很大时，GDPO 是必不可少的。
\end{itemize}
\end{keybox}

\begin{examplebox}[GDPO in TRL（TRL中的GDPO）]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    multi_objective_aggregation="normalize_then_sum",
    reward_weights=[1.0, 0.5],   # weights for [correctness, format]  # [正确性, 格式]的权重
    num_generations=8,
)


def correctness_reward(completions, **kwargs):
    return [1.0 if is_correct(c) else 0.0 for c in completions]


def format_reward(completions, **kwargs):
    return [0.1 if has_good_format(c) else 0.0 for c in completions]


trainer = GRPOTrainer(
    model=model,
    reward_funcs=[correctness_reward, format_reward],
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}


\subsection{GOPO -- Group Ordinal Policy Optimization}
\subsection{GOPO —— 群体序数策略优化（Group Ordinal Policy Optimization）}
\label{gopo-group-ordinal-policy-optimization}


GOPO~\cite{choi2025gopo} starts from a simple observation: reward models are trained with pairwise comparisons (``is A better than B?''), so only the \textbf{rank order} of their outputs is trustworthy---the raw numeric scores carry no inherent meaning. Yet GRPO feeds those raw magnitudes directly into the advantage calculation. For tasks with non-verifiable rewards---summarization, open-ended chat, instruction following---this mismatch introduces noise, because a gap of 0.6 reward points might reflect genuine quality in one region of the output space and mean nothing in another.
GOPO~\cite{choi2025gopo} 从一个简单的观察出发：奖励模型是通过成对比较（“A比B更好吗？”）训练的，因此其输出的\textbf{排名顺序}才是可信的——原始的数值分数没有内在含义。然而 GRPO 却将这些原始量值直接用于优势计算。对于具有不可验证奖励的任务（摘要、开放对话、指令遵循），这种错配会引入噪声，因为 0.6 个奖励点的差距可能在输出空间的某个区域反映真实质量，在另一个区域却毫无意义。


\textbf{Key Insight}: Discard reward magnitudes entirely. Use only the \textbf{ordinal ranking} of rewards within a group.
\textbf{关键洞察}：完全丢弃奖励量值。只使用组内奖励的\textbf{序数排名}。


\textbf{Algorithm}: Given a group of $N$ responses $\{o_1, \ldots, o_N\}$ with rewards $\{r_1, \ldots, r_N\}$:
\textbf{算法}：给定一组 $N$ 个回复 $\{o_1, \ldots, o_N\}$ 及其奖励 $\{r_1, \ldots, r_N\}$：


\begin{enumerate}
  \item Rank responses by reward: assign rank $\text{rank}(o_i) \in \{1, \ldots, N\}$ (1 = worst, $N$ = best).
  \item 按奖励对回复排序：分配排名 $\text{rank}(o_i) \in \{1, \ldots, N\}$（1 表示最差，$N$ 表示最好）。
  \item Replace raw advantages with rank-based scores: 
  \item 用基于排名的分数替换原始优势：
\begin{equation}
\boxed{\hat{A}_i^{\text{GOPO}} = f\!\left(\frac{\text{rank}(o_i)}{N}\right)}
\end{equation}
 where $f$ is a monotonic transformation (e.g., linear mapping to $[-1, 1]$ or quantile normalization).
 其中 $f$ 是单调变换（例如线性映射到 $[-1, 1]$ 或分位数归一化）。
  \item Apply PPO-style clipped objective using rank-based advantages.
  \item 使用基于排名的优势应用 PPO 风格的裁剪目标。
\end{enumerate}


\textbf{Comparison with GRPO}:
\textbf{与 GRPO 的比较}：


\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Aspect} & \textbf{GRPO} & \textbf{GOPO} \\
\textbf{方面} & \textbf{GRPO} & \textbf{GOPO} \\
\midrule
Advantage signal & $\hat{A}_i = (r_i - \mu)/\sigma$ (uses magnitudes) & $\hat{A}_i = f(\text{rank}_i / N)$ (uses ordinal rank only) \\
优势信号 & $\hat{A}_i = (r_i - \mu)/\sigma$（使用量值） & $\hat{A}_i = f(\text{rank}_i / N)$（仅使用序数排名） \\
Sensitivity to reward scale & High --- miscalibrated RM scores distort advantages & None --- invariant to monotonic reward transformations \\
对奖励量纲的敏感性 & 高 —— 未校准的 RM 分数会扭曲优势 & 无 —— 对奖励的单调变换不变 \\
Best for & Verifiable rewards (binary, well-calibrated) & Non-verifiable rewards (RM-based, noisy magnitudes) \\
最适合 & 可验证奖励（二值、良好校准） & 不可验证奖励（基于 RM、量值有噪声） \\
\bottomrule
\end{tabular}


\textbf{Empirical gains} (over GRPO on non-verifiable tasks):
\textbf{实证收益}（在不可验证任务上相对于 GRPO）：


\begin{itemize}
  \item Reward curves (both training and held-out) sit above GRPO throughout optimization
  \item 奖励曲线（训练集和保留集）在整个优化过程中均位于 GRPO 之上
  \item Win-rates judged by a separate LLM evaluator improve at most training checkpoints
  \item 由独立 LLM 评估器判定的胜率在大多数训练检查点上有所提升
  \item Convergence is markedly faster---matching GRPO’s final quality with fewer gradient steps
  \item 收敛速度明显更快——用更少的梯度步数即可达到 GRPO 的最终质量
  \item The advantage grows as the reward model becomes noisier or more poorly calibrated
  \item 当奖励模型变得更嘈杂或校准更差时，优势会进一步增大
\end{itemize}


\begin{intuitionbox}[When to Use GOPO vs. GRPO（何时使用GOPO vs. GRPO）]
\begin{itemize}
  \item \textbf{Use GRPO}: When rewards are verifiable and exact (math correctness, code tests pass/fail, binary signals). Magnitudes carry meaningful information.
  \item \textbf{使用 GRPO}：当奖励是可验证且精确时（数学正确性、代码测试通过/失败、二值信号）。量值携带有意义的信息。
  \item \textbf{Use GOPO}: When rewards come from a learned reward model on subjective tasks (helpfulness, style, safety). The RM’s relative ordering is trustworthy but its absolute scores are arbitrary.
  \item \textbf{使用 GOPO}：当奖励来自针对主观任务（有用性、风格、安全性）学习的奖励模型时。RM 的相对排序是可信的，但其绝对分数是任意的。
\end{itemize}
\end{intuitionbox}