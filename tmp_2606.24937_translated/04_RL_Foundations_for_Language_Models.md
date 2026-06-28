## RL Foundations for Language Models
## 语言模型的强化学习基础

Supervised fine-tuning (SFT) teaches a model to imitate demonstrations, but imitation has a ceiling: the model can never exceed the quality of its training data. Reinforcement learning breaks this barrier. By generating novel text, receiving reward feedback, and updating toward higher-reward behaviours, an RL-trained model can \emph{discover} strategies that no human demonstrator wrote---producing outputs that are more helpful, more accurate, and better aligned with human preferences~\cite{ouyang2022training}.
监督式微调（SFT）教会模型模仿示范，但模仿存在天花板：模型永远无法超越其训练数据的质量。强化学习打破了这一壁垒。通过生成新颖文本、接收奖励反馈并向高奖励行为更新，经过RL训练的模型能够\emph{发现}没有任何人类示范者编写的策略——从而产生更有用、更准确且与人类偏好更一致的输出~\cite{ouyang2022training}。

This is the mechanism behind every frontier model: GPT-4~\cite{openai2023gpt4}, Claude, Llama-3~\cite{grattafiori2024llama3}, and DeepSeek-R1~\cite{deepseek2025r1} all apply RL after SFT as the critical step that transforms a capable but unsteered model into an aligned assistant.
这正是每个前沿模型背后的机制：GPT-4~\cite{openai2023gpt4}、Claude、Llama-3~\cite{grattafiori2024llama3}和DeepSeek-R1~\cite{deepseek2025r1}都在SFT之后应用RL，作为将能力强但未经引导的模型转化为对齐助手的至关重要的一步。

## Two Paradigms for RL in LLMs
## 大语言模型中RL的两种范式

RL methods for language models fall into two broad paradigms, each suited to different goals:
语言模型的强化学习方法分为两大范式，各自适用于不同目标：

\paragraph{Paradigm 1: Alignment via Human Preferences (RLHF/DPO).}
The original motivation for applying RL to LLMs was \textbf{alignment}---making models helpful, harmless, and honest. \textbf{Reinforcement Learning from Human Feedback (RLHF)}~\cite{ouyang2022training, ziegler2019fine, christiano2017deep} trains a reward model from pairwise human judgments (``which response is better?'') and then optimizes the policy to maximize that learned reward. \textbf{DPO}~\cite{rafailov2023direct} simplifies this by eliminating the reward model entirely, converting preferences directly into a supervised loss. Both approaches produce aligned assistants that follow instructions and respect safety constraints.
\paragraph{范式一：通过人类偏好进行对齐（RLHF/DPO）。}
将RL应用于LLM的最初动机是\textbf{对齐}——让模型变得有帮助、无害且诚实。\textbf{基于人类反馈的强化学习（RLHF）}~\cite{ouyang2022training, ziegler2019fine, christiano2017deep}通过成对的人类判断（“哪个回答更好？”）训练一个奖励模型，然后优化策略以最大化该学习到的奖励。\textbf{DPO}~\cite{rafailov2023direct}通过完全消除奖励模型来简化这一过程，将偏好直接转化为监督损失。两种方法都能产生遵循指令并尊重安全约束的对齐助手。

\paragraph{Paradigm 2: Capability Enhancement via Verifiable Rewards (RLVR).}
More recently, RL has been used not just for alignment but for \textbf{teaching new capabilities}---particularly reasoning, mathematics, and code generation. Here the reward comes not from human preferences but from \textbf{verifiable outcomes}: did the model produce the correct answer? Did the code pass all tests? DeepSeek-R1~\cite{deepseek2025r1} demonstrated that GRPO with rule-based rewards (format correctness + answer accuracy) can train models to develop sophisticated chain-of-thought reasoning \emph{without any human preference data}. This paradigm---RL from Verifiable Rewards (RLVR)---is now the dominant approach for building reasoning models and agentic systems.
\paragraph{范式二：通过可验证奖励提升能力（RLVR）。}
最近，RL不仅用于对齐，还用于\textbf{教导新能力}——特别是推理、数学和代码生成。这里的奖励并非来自人类偏好，而是来自\textbf{可验证的结果}：模型是否给出了正确答案？代码是否通过了所有测试？DeepSeek-R1~\cite{deepseek2025r1}证明，使用基于规则的奖励（格式正确性+答案准确性）的GRPO可以在\textbf{没有任何人类偏好数据}的情况下训练模型发展出复杂的思维链推理。这一范式——基于可验证奖励的强化学习（RLVR）——现在已成为构建推理模型和智能体系统的主流方法。

\begin{keybox}[The Shared Foundation]
Despite their different goals, both paradigms share the same core machinery:
\begin{itemize}
  \item A \textbf{policy} $\pi_\theta$ (the LLM) that generates text autoregressively
  \item A \textbf{reward signal} $r(x, y)$ (learned from preferences or computed from verification)
  \item A \textbf{KL constraint} against a reference policy to prevent degenerate solutions
  \item \textbf{Policy gradient optimization} (PPO or GRPO) to update the model toward higher reward
\end{itemize}
The chapters in this part develop each component in detail.
\end{keybox}
\begin{keybox}[共同基础]
尽管目标不同，但两种范式共享相同的核心机制：
\begin{itemize}
  \item 一个\textbf{策略} $\pi_\theta$（即LLM），它自回归地生成文本
  \item 一个\textbf{奖励信号} $r(x, y)$（从偏好中学习或通过验证计算得出）
  \item 一个针对参考策略的\textbf{KL约束}，以防止退化解
  \item \textbf{策略梯度优化}（PPO或GRPO），用于将模型向更高奖励更新
\end{itemize}
本部分的各章节将详细阐述每个组件。
\end{keybox}

## Text Generation as an MDP
## 将文本生成视为一个MDP

The key insight that makes RL applicable to language models is recasting autoregressive generation as a Markov Decision Process:
使RL适用于语言模型的关键洞察是将自回归生成重新定义为马尔可夫决策过程：

\begin{intuitionbox}[The LLM-as-Agent Analogy]
Think of the LLM as an \textbf{agent} writing a response one token at a time. At each step, it looks at everything written so far (the \emph{state}), chooses the next word (the \emph{action}), and the page grows by one token (the \emph{transition}). When the response is complete, a judge scores it (the \emph{reward}). The goal: learn a writing strategy (a \emph{policy}) that consistently earns high scores.
\end{intuitionbox}
\begin{intuitionbox}[LLM作为智能体的类比]
将LLM想象成一个\textbf{智能体}，一次一个词元地撰写回答。每一步，它观察到目前为止已写的内容（\emph{状态}），选择下一个词（\emph{动作}），页面增加一个词元（\emph{转移}）。当回答完成时，一个评判者为其打分（\emph{奖励}）。目标：学习一个持续获得高分的写作策略（\emph{策略}）。
\end{intuitionbox}

Formally, the MDP for text generation is:
形式上，文本生成的MDP如下：

\begin{itemize}
  \item \textbf{State} $s_t = (x, y_1, \ldots, y_{t-1})$: the prompt concatenated with all tokens generated so far.
  \item \textbf{Action} $a_t \in \{1, \ldots, |\mathcal{V}|\}$: choosing the next token from the vocabulary (32K--128K options).
  \item \textbf{Transition} $P(s_{t+1}|s_t, a_t)$: deterministic---just append the chosen token. No environment stochasticity.
  \item \textbf{Reward} $r$: typically given only at the end of generation (sparse). For RLHF: the reward model score. For RLVR: correctness of the final answer.
  \item \textbf{Policy} $\pi_\theta(a_t|s_t)$: the LLM's next-token probability distribution---exactly what the softmax output already computes.
  \item \textbf{Discount} $\gamma = 1.0$: episodes are finite (one response), so no discounting needed.
\end{itemize}
\begin{itemize}
  \item \textbf{状态} $s_t = (x, y_1, \ldots, y_{t-1})$：提示词与迄今为止生成的所有词元拼接而成。
  \item \textbf{动作} $a_t \in \{1, \ldots, |\mathcal{V}|\}$：从词表中选取下一个词元（32K–128K个选项）。
  \item \textbf{转移} $P(s_{t+1}|s_t, a_t)$：确定性的——只需追加所选词元。环境无随机性。
  \item \textbf{奖励} $r$：通常在生成结束时才给出（稀疏奖励）。对于RLHF：奖励模型得分。对于RLVR：最终答案的正确性。
  \item \textbf{策略} $\pi_\theta(a_t|s_t)$：LLM的下一个词元概率分布——正是softmax输出已经计算的内容。
  \item \textbf{折扣} $\gamma = 1.0$：回合是有限的（一个回答），因此无需折现。
\end{itemize}

This mapping is powerful because the LLM \emph{already is} a policy---its softmax output defines $\pi_\theta(a_t|s_t)$ for every state. We don't need to build a separate policy network; we just need to adjust the weights $\theta$ so the model assigns higher probability to token sequences that earn higher reward.
这种映射之所以强大，是因为LLM\emph{本身就是一个策略}——其softmax输出了每个状态下的$\pi_\theta(a_t|s_t)$。我们无需构建单独的策略网络，只需调整权重$\theta$，使模型对能获得更高奖励的词元序列赋予更高概率。

## The RLHF Pipeline
## RLHF流程

The classic RLHF pipeline~\cite{ouyang2022training} consists of four stages:
经典的RLHF流程~\cite{ouyang2022training}包含四个阶段：

\begin{enumerate}
  \item \textbf{Supervised Fine-Tuning (SFT)}: Train a base model on high-quality demonstrations to produce a policy $\pi_{\text{SFT}}$ that can follow instructions.
  \item \textbf{Reward Model Training}: Collect human preference comparisons ($y_w \succ y_l$ for the same prompt) and train a reward model $R_\phi(x, y)$ using the Bradley-Terry objective.
  \item \textbf{RL Optimization}: Use the reward model as a signal to optimize the policy via PPO or GRPO, subject to a KL constraint against $\pi_{\text{SFT}}$.
  \item \textbf{Evaluation and Iteration}: Evaluate the aligned model, collect new failure cases, and iterate.
\end{enumerate}
\begin{enumerate}
  \item \textbf{监督式微调（SFT）}：在高质量示范上训练基础模型，得到能够遵循指令的策略$\pi_{\text{SFT}}$。
  \item \textbf{奖励模型训练}：收集人类偏好比较（同一提示下$y_w \succ y_l$），并使用Bradley-Terry目标训练奖励模型$R_\phi(x, y)$。
  \item \textbf{RL优化}：以奖励模型为信号，通过PPO或GRPO优化策略，同时施加针对$\pi_{\text{SFT}}$的KL约束。
  \item \textbf{评估与迭代}：评估对齐后的模型，收集新的失败案例，并迭代。
\end{enumerate}

For RLVR (reasoning/agentic training), stages 1--2 are replaced: the SFT model is trained on reasoning traces, and the reward model is replaced by a verifier (e.g., checking mathematical correctness). Stage 3 remains the same---PPO or GRPO optimization against the reward signal.
对于RLVR（推理/智能体训练），阶段1-2被替换：SFT模型在推理轨迹上训练，奖励模型被验证器（例如检查数学正确性）取代。阶段3保持不变——针对奖励信号进行PPO或GRPO优化。

\begin{intuitionbox}[How LLM RL Differs from Classical RL]
The LLM setting differs from classical RL in important ways:
\begin{itemize}
  \item \textbf{Deterministic transitions}: The ``next state'' is just the concatenation of previous tokens---no stochastic environment.
  \item \textbf{Sparse reward}: Feedback is typically given once at the end of generation (outcome reward) or at key steps (process reward).
  \item \textbf{Massive action space}: 32K--128K possible tokens at every step, but exploration is implicit via temperature sampling.
  \item \textbf{KL anchor}: LLM RL is constrained to stay close to the SFT policy, preventing reward hacking at the cost of reduced exploration.
  \item \textbf{No value function needed}: GRPO eliminates the critic network entirely, using group-relative normalization of rewards instead.
\end{itemize}
These differences explain why PPO and GRPO dominate over DQN-style approaches for LLMs.
\end{intuitionbox}
\begin{intuitionbox}[LLM RL与经典RL的不同之处]
LLM设置与经典RL在重要方面有所不同：
\begin{itemize}
  \item \textbf{确定性转移}：“下一个状态”仅仅是先前词元的拼接——没有随机环境。
  \item \textbf{稀疏奖励}：反馈通常在生成结束时给出（结果奖励）或在关键步骤给出（过程奖励）。
  \item \textbf{巨大的动作空间}：每一步都有32K–128K个可能的词元，但通过温度采样隐含地实现探索。
  \item \textbf{KL锚点}：LLM RL被约束在SFT策略附近，以防止奖励破解，但代价是探索减少。
  \item \textbf{无需价值函数}：GRPO完全消除了评论家网络，改用奖励的组相对归一化。
\end{itemize}
这些差异解释了为什么PPO和GRPO在LLM中主导了DQN风格的方法。
\end{intuitionbox}

## Roadmap of This Part
## 本部分路线图

The chapters ahead build the complete RL-for-LLMs toolkit:
接下来的章节将构建完整的LLM强化学习工具包：

Now produce the bilingual translation following ALL rules above. Start directly with the translated content (no preamble).
现在按照上述所有规则生成双语翻译。直接开始翻译内容（无需前言）。

\begin{enumerate}
  \item \textbf{PPO} (Chapter~5) --- The clipped surrogate objective, GAE for advantage estimation, the critic network, and the full RLHF training loop. The workhorse behind GPT-4 and Claude.
  \item \textbf{PPO}（第5章）——裁剪替代目标、用于优势估计的GAE、评论家网络以及完整的RLHF训练循环。这是GPT-4和Claude背后的主力算法。

  \item \textbf{DPO} (Chapter~6) --- Bypassing RL entirely by converting preferences into a contrastive supervised loss. Simpler but less flexible than online RL.
  \item \textbf{DPO}（第6章）——通过将偏好转换为对比监督损失来完全绕过强化学习。比在线RL更简单但灵活性较低。

  \item \textbf{GRPO} (Chapter~7) --- DeepSeek's critic-free algorithm that uses group-level reward normalization. The method behind DeepSeek-R1 and the dominant choice for reasoning model training.
  \item \textbf{GRPO}（第7章）——DeepSeek的无评论家算法，使用组级奖励归一化。这是DeepSeek-R1背后的方法，也是推理模型训练的主流选择。

  \item \textbf{Preference optimization variants} (Chapter~8) --- Online DPO, KTO, Best-of-N, and guidance on method selection.
  \item \textbf{偏好优化变体}（第8章）——在线DPO、KTO、Best-of-N以及方法选择指南。

  \item \textbf{Reward modeling} (Chapter~9) --- Bradley-Terry models, process vs.~outcome rewards, rule-based rewards for RLVR, and multi-objective combinations.
  \item \textbf{奖励建模}（第9章）——Bradley-Terry模型、过程奖励与结果奖励、用于RLVR的基于规则的奖励以及多目标组合。

  \item \textbf{SFT best practices} (Chapter~10) --- Sequence packing, chat templates, data mixing, and how SFT quality determines the RL ceiling.
  \item \textbf{SFT最佳实践}（第10章）——序列打包、聊天模板、数据混合以及SFT质量如何决定强化学习的天花板。

  \item \textbf{Systems engineering} (Chapter~11) --- Distributed training at scale: parallelism strategies, generation--training decoupling, and infrastructure for hundreds of GPUs.
  \item \textbf{系统工程}（第11章）——大规模分布式训练：并行策略、生成-训练解耦以及面向数百个GPU的基础设施。
\end{enumerate}