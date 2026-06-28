    # 不需要 ref_model！
)


trainer = DPOTrainer(
    model=model,
    ref_model=None,    # SimPO 是无参考模型的
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}
---

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
