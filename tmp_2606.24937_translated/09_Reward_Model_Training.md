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


# Load model with scalar head (num_labels=1)
model = AutoModelForSequenceClassification.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    num_labels=1,
)


config = RewardConfig(
    output_dir="reward_model",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=1e-5,
    num_train_epochs=1,
    # Margin loss
    center_rewards_coefficient=0.01,
)


trainer = RewardTrainer(
    model=model,
    args=config,
    train_dataset=dataset,  # must have chosen/rejected columns
)
trainer.train()
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[TRL 中的奖励模型训练]
\begin{lstlisting}[style=pythonstyle]
from trl import RewardConfig, RewardTrainer
from transformers import AutoModelForSequenceClassification


# 加载带有标量头的模型 (num_labels=1)
model = AutoModelForSequenceClassification.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    num_labels=1,
)


config = RewardConfig(
    output_dir="reward_model",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=1e-5,
    num_train_epochs=1,
    # 边际损失
    center_rewards_coefficient=0.01,
)


trainer = RewardTrainer(
    model=model,
    args=config,
    train_dataset=dataset,  # 必须包含 chosen/rejected 列
)
trainer.train()
\end{lstlisting}
\end{examplebox}

## Section: Reward Model Training Tricks
## 节：奖励模型训练技巧

### Reward Centering
### 奖励居中

Raw reward model outputs can have arbitrary scale and offset. Centering the rewards (subtracting the mean) stabilises RL training:
原始奖励模型输出可能具有任意的尺度和偏移。对奖励进行居中（减去均值）可以稳定 RL 训练：

\[
r_{\text{centered}}(y, q) = r_\phi(y, q) - \mathbb{E}_{y' \sim \pi_\theta}[r_\phi(y', q)].
\]

In TRL, this is implemented via the \texttt{center\_rewards\_coefficient} parameter, which adds a regularisation term to the reward model loss that penalises non-zero mean rewards.
在 TRL 中，这是通过 \texttt{center\_rewards\_coefficient} 参数实现的，该参数向奖励模型损失添加了一个正则化项，惩罚非零均值奖励。

### Length Bias Correction
### 长度偏差校正

Reward models are known to exhibit \emph{length bias}: they tend to assign higher rewards to longer responses, regardless of quality. This can be corrected by:
众所周知，奖励模型存在\emph{长度偏差}：无论质量如何，它们都倾向于给更长的回答分配更高的奖励。这可以通过以下方式校正：

\begin{enumerate}
  \item \textbf{Length normalisation}: divide the reward by the response length.
  \item \textbf{Length-controlled training}: include length as a feature and train the model to be length-invariant.
  \item \textbf{Calibration}: post-hoc regression to remove the length effect.
\end{enumerate}

\begin{enumerate}
  \item \textbf{长度归一化（Length normalisation）}：将奖励除以回答长度。
  \item \textbf{长度控制训练（Length-controlled training）}：将长度作为一个特征，训练模型使其对长度不敏感。
  \item \textbf{校准（Calibration）}：事后回归以消除长度效应。
\end{enumerate}

### Margin Losses
### 边际损失

Adding a margin $m$ to the Bradley-Terry loss ensures the reward model assigns meaningfully different scores to preferred and dispreferred responses:
向 Bradley-Terry 损失添加边际 $m$ 可确保奖励模型为偏好回答和非偏好回答分配有意义的差异分数：

\[
\mathcal{L}_{\text{margin}} = \max\!\bigl(0,\; m - (r_w - r_l)\bigr).
\]

## Section: Process Reward Models vs Outcome Reward Models
## 节：过程奖励模型 vs 结果奖励模型

\begin{keybox}[PRM vs ORM Comparison]
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Property} & \textbf{ORM} & \textbf{PRM} \\
\midrule
Reward signal & Final answer only & Each reasoning step \\
Training data & (prompt, answer, correct?) & (prompt, steps, step labels) \\
Annotation cost & Low & High \\
Credit assignment & Sparse & Dense \\
Reward hacking & Easier to hack & Harder to hack \\
Best for & Simple tasks & Multi-step reasoning \\
Inference cost & Low & High (score each step) \\
\bottomrule
\end{tabular}
\end{keybox}

\begin{keybox}[PRM 与 ORM 比较]
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{属性} & \textbf{ORM} & \textbf{PRM} \\
\midrule
奖励信号 & 仅最终答案 & 每个推理步骤 \\
训练数据 & (提示, 回答, 正确?) & (提示, 步骤, 步骤标签) \\
标注成本 & 低 & 高 \\
信用分配 & 稀疏 & 密集 \\
奖励黑客攻击 & 更容易被攻击 & 更难被攻击 \\
最适合 & 简单任务 & 多步推理 \\
推理成本 & 低 & 高（每个步骤评分） \\
\bottomrule
\end{tabular}
\end{keybox}

\begin{intuitionbox}[When to Use PRMs]
Process Reward Models are most valuable when:
\begin{itemize}
  \item The task requires multi-step reasoning (math, code, logic).
  \item The final answer is binary (correct/incorrect) but intermediate steps vary in quality.
  \item You want to use the reward model for \emph{search} (e.g., beam search with step scores).
  \item You have access to step-level annotations (or can generate them automatically).
\end{itemize}
For simple tasks (sentiment, toxicity, factuality), ORMs are sufficient and much cheaper.
\end{intuitionbox}

\begin{intuitionbox}[何时使用 PRM]
过程奖励模型最有价值的情况包括：
\begin{itemize}
  \item 任务需要多步推理（数学、代码、逻辑）。
  \item 最终答案是二元的（正确/错误），但中间步骤质量参差不齐。
  \item 你想将奖励模型用于\emph{搜索}（例如，带步骤分数的束搜索）。
  \item 你可以访问步骤级标注（或可以自动生成它们）。
\end{itemize}
对于简单任务（情感、毒性、事实性），ORM 已经足够且便宜得多。
\end{intuitionbox}

\begin{examplebox}[PBRS in RLHF for LLMs]
\textbf{Original reward}: Binary correctness (1 if final answer is right, 0 otherwise) --- extremely sparse for multi-step reasoning.

\textbf{Potential function}: $\Phi(s) =$ partial credit from a verifier (e.g., fraction of intermediate reasoning steps that are logically valid).

\textbf{Shaped reward}: Agent gets incremental signal for each valid reasoning step while preserving the guarantee that the optimal policy still maximizes final-answer correctness.

\textbf{Practical implementations}:
\begin{itemize}
  \item Process reward models (PRMs) that score each step in a chain-of-thought
  \item Intermediate compilation checks in code generation
  \item Partial match scores for multi-part answers
\end{itemize}

This is a direct application of Potential-Based Reward Shaping (PBRS)~\cite{ng1999policy} to the LLM setting---the theoretical guarantee that shaped rewards preserve the optimal policy makes PRMs a principled approach to dense reward in reasoning tasks.
\end{examplebox}

\begin{examplebox}[面向 LLM 的 RLHF 中的 PBRS]
\textbf{原始奖励}：二元正确性（最终答案正确为1，否则为0）——对于多步推理来说极其稀疏。

\textbf{势函数}：$\Phi(s) =$ 来自验证器的部分信用（例如，中间推理步骤中逻辑有效的比例）。

\textbf{塑形奖励}：智能体在每个有效推理步骤中获得增量信号，同时保留最优策略仍能最大化最终答案正确性的保证。

\textbf{实际实现}：
\begin{itemize}
  \item 过程奖励模型（PRM），对思维链中的每个步骤进行评分
  \item 代码生成中的中间编译检查
  \item 多部分答案的部分匹配得分
\end{itemize}

这是基于势的奖励塑形（PBRS）~\cite{ng1999policy} 在 LLM 场景中的直接应用——塑形奖励保留最优策略的理论保证使得 PRM 成为推理任务中密集奖励的一种有原则的方法。
\end{examplebox}

### Automatic PRM Annotation
### 自动 PRM 标注

Step-level annotations can be generated automatically using:
步骤级标注可以使用以下方法自动生成：

\begin{enumerate}
  \item \textbf{Monte Carlo rollouts}: for each intermediate step, sample multiple completions and use the fraction that reach the correct answer as the step reward.
  \item \textbf{Monte Carlo展开}：对于每个中间步骤，采样多个补全，并使用达到正确答案的比例作为步骤奖励。
  \item \textbf{LLM-as-judge}: use a strong LLM to evaluate each step.
  \item \textbf{作为评判者的LLM}：使用一个强大的LLM来评估每个步骤。
  \item \textbf{Formal verification}: for math/code, use a verifier to check each step.
  \item \textbf{形式化验证}：对于数学/代码，使用验证器检查每个步骤。
\end{enumerate}

\section{Rule-Based Rewards for RLVR}
\label{sec:rule-based-rewards}
## 基于规则的RLVR奖励
## \label{sec:rule-based-rewards}

Reinforcement Learning from Verifiable Rewards (RLVR) uses deterministic, rule-based reward functions instead of learned reward models. This substantially reduces reward hacking (though models can still exploit format tricks, edge cases, or test memorization) and is the approach used in DeepSeek-R1~\cite{deepseek2025r1}.
基于可验证奖励的强化学习（Reinforcement Learning from Verifiable Rewards，RLVR）使用确定性、基于规则的奖励函数，而非学得的奖励模型。这大幅减少了奖励欺骗（尽管模型仍可能利用格式技巧、边界情况或测试记忆化），并且是DeepSeek-R1~\cite{deepseek2025r1}所采用的方法。

\begin{examplebox}[Rule-Based Reward Functions in TRL]
\begin{examplebox}[TRL中的基于规则奖励函数]
\begin{lstlisting}[style=pythonstyle]
import re


def format_reward(completions, **kwargs):
    """Reward for using <think>...</think><answer>...</answer> format."""
    rewards = []
    pattern = r"<think>.*?</think>\s*<answer>.*?</answer>"
    for completion in completions:
        text = completion[0]["content"]
        rewards.append(1.0 if re.fullmatch(pattern, text, re.DOTALL) else 0.0)
    return rewards


def format_reward(completions, **kwargs):
    """奖励使用 <think>...</think><answer>...</answer> 格式。"""
    rewards = []
    pattern = r"<think>.*?</think>\s*<answer>.*?</answer>"
    for completion in completions:
        text = completion[0]["content"]
        rewards.append(1.0 if re.fullmatch(pattern, text, re.DOTALL) else 0.0)
    return rewards


def correctness_reward(completions, ground_truth, **kwargs):
    """Reward for correct final answer."""
    rewards = []
    for completion, gt in zip(completions, ground_truth):
        text = completion[0]["content"]
        match = re.search(r"<answer>(.*?)</answer>", text, re.DOTALL)
        if match:
            answer = match.group(1).strip()
            rewards.append(1.0 if answer == gt else 0.0)
        else:
            rewards.append(0.0)
    return rewards


def correctness_reward(completions, ground_truth, **kwargs):
    """奖励正确的最终答案。"""
    rewards = []
    for completion, gt in zip(completions, ground_truth):
        text = completion[0]["content"]
        match = re.search(r"<answer>(.*?)</answer>", text, re.DOTALL)
        if match:
            answer = match.group(1).strip()
            rewards.append(1.0 if answer == gt else 0.0)
        else:
            rewards.append(0.0)
    return rewards


def code_execution_reward(completions, test_cases, **kwargs):
    """Reward for code that passes test cases."""
    import subprocess, tempfile, os
    rewards = []
    for completion, tests in zip(completions, test_cases):
        code = completion[0]["content"]
        passed = 0
        for test in tests:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as f:
                f.write(code + "\n" + test)
                fname = f.name
            try:
                result = subprocess.run(
                    ["python", fname], capture_output=True,
                    timeout=5, text=True
                )
                passed += int(result.returncode == 0)
            except Exception:
                pass
            finally:
                os.unlink(fname)
        rewards.append(passed / len(tests))
    return rewards


def code_execution_reward(completions, test_cases, **kwargs):
    """奖励通过测试用例的代码。"""
    import subprocess, tempfile, os
    rewards = []
    for completion, tests in zip(completions, test_cases):
        code = completion[0]["content"]
        passed = 0
        for test in tests:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as f:
                f.write(code + "\n" + test)
                fname = f.name
            try:
                result = subprocess.run(
                    ["python", fname], capture_output=True,
                    timeout=5, text=True
                )
                passed += int(result.returncode == 0)
            except Exception:
                pass
            finally:
                os.unlink(fname)
        rewards.append(passed / len(tests))
    return rewards
\end{lstlisting}
\end{examplebox}


\begin{warningbox}[Rule-Based Reward Pitfalls]
\begin{warningbox}[基于规则奖励的陷阱]
\begin{itemize}
  \item \textbf{Format gaming}: models learn to produce the correct format without correct content. Always combine format and correctness rewards.
  \item \textbf{格式欺骗}：模型学会了生成正确格式但内容错误。始终将格式奖励与正确性奖励结合使用。
  \item \textbf{Test case leakage}: if test cases are in the training data, the model memorises them.
  \item \textbf{测试用例泄露}：如果测试用例存在于训练数据中，模型会记忆它们。
  \item \textbf{Timeout exploitation}: models may generate code that times out (avoiding failure). Use strict timeouts and penalise timeouts explicitly.
  \item \textbf{超时利用}：模型可能生成超时的代码（从而避免失败）。使用严格的超时限制并显式惩罚超时。
  \item \textbf{Reward sparsity}: binary rewards (0/1) can be too sparse for complex tasks. Consider partial credit or intermediate rewards.
  \item \textbf{奖励稀疏性}：二元奖励（0/1）对于复杂任务可能过于稀疏。考虑部分得分或中间奖励。
\end{itemize}
\end{warningbox}


\section{Multi-Objective Rewards -- Combination Strategies}
\label{sec:multi-objective-rewards}
## 多目标奖励——组合策略
## \label{sec:multi-objective-rewards}

When training with multiple reward signals, the combination strategy significantly affects the final policy.
在使用多个奖励信号进行训练时，组合策略会显著影响最终策略。

\begin{keybox}[Multi-Reward Combination Strategies]
\begin{keybox}[多奖励组合策略]
\begin{enumerate}
  \item \textbf{Weighted sum}: $r = \sum_n w_n r_n$. Simple but sensitive to scale.
  \item \textbf{加权求和}：$r = \sum_n w_n r_n$。简单但对尺度敏感。
  \item \textbf{Normalise then sum (GDPO)}: normalise each reward to zero mean and unit variance within the group, then sum with weights. Scale-invariant.
  \item \textbf{归一化后求和（GDPO）}：将每个奖励在组内归一化为零均值和单位方差，然后加权求和。尺度不变。
  \item \textbf{Lexicographic}: optimise rewards in priority order; only consider lower-priority rewards when higher-priority ones are tied.
  \item \textbf{词典序优化}：按优先级顺序优化奖励；仅在更高优先级奖励相同时才考虑较低优先级的奖励。
  \item \textbf{Constrained}: maximise primary reward subject to constraints on secondary rewards.
  \item \textbf{约束优化}：在次要奖励的约束下最大化主要奖励。
  \item \textbf{Pareto}: maintain a Pareto front of policies and select based on preference.
  \item \textbf{帕累托优化}：维护策略的帕累托前沿，并根据偏好进行选择。
\end{enumerate}
\end{keybox}


\begin{examplebox}[Multi-Reward Training in TRL]
\begin{examplebox}[TRL中的多奖励训练]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    # GDPO: normalise each reward independently
    multi_objective_aggregation="normalize_then_sum",
    reward_weights=[1.0, 0.3, 0.1],  # correctness, format, length
    num_generations=8,
)


config = GRPOConfig(
    # GDPO: 独立归一化每个奖励
    multi_objective_aggregation="normalize_then_sum",
    reward_weights=[1.0, 0.3, 0.1],  # 正确性，格式，长度
    num_generations=8,
)


trainer = GRPOTrainer(
    model=model,
    reward_funcs=[
        correctness_reward,
        format_reward,
        length_penalty_reward,
    ],
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}


\section{Listwise Rank-Based Rewards}
\label{listwise-rank-based-rewards}
## 基于列表排名的奖励
## \label{listwise-rank-based-rewards}

While the Bradley-Terry model handles \emph{pairwise} preferences ($y_w \succ y_l$), many practical scenarios involve ranking multiple responses simultaneously. Listwise reward models learn from complete orderings, providing richer training signal and enabling better calibration.
虽然Bradley-Terry模型处理的是\textit{成对}偏好（$y_w \succ y_l$），但许多实际场景需要对多个响应同时进行排序。列表奖励模型从完整的排序中学习，提供更丰富的训练信号并实现更好的校准。

\subsubsection*{Motivation: Beyond Pairwise}
\label{motivation-beyond-pairwise}
## 动机：超越成对
## \label{motivation-beyond-pairwise}

\begin{intuitionbox}[Why Listwise?]
\begin{intuitionbox}[为何使用列表排序？]
\begin{itemize}
  \item \textbf{Richer signal}: A ranking of $K$ responses contains $\binom{K}{2}$ implicit pairwise comparisons, but also captures \emph{relative margins} (how much better rank 1 is vs.~rank 3).
  \item \textbf{更丰富的信号}：$K$个响应的排序包含$\binom{K}{2}$个隐式成对比较，还捕捉了\textit{相对差距}（排名1比排名3好多少）。
  \item \textbf{Better calibration}: Pairwise BT models only learn \emph{differences} in reward; listwise models learn absolute reward scale.
  \item \textbf{更好的校准}：成对BT模型仅学习奖励的\textit{差异}；列表模型学习绝对的奖励尺度。
  \item \textbf{Natural fit for GRPO}: GRPO generates $N$ responses per prompt and ranks them --- listwise rewards align directly with this workflow.
  \item \textbf{与GRPO自然契合}：GRPO对每个提示生成$N$个响应并排序——列表奖励直接与该工作流程对齐。
  \item \textbf{Annotator efficiency}: Ranking 5 responses is faster than labeling all 10 possible pairs independently.
  \item \textbf{标注效率}：对5个响应排序比独立标注所有10个可能对更快。
\end{itemize}
\end{intuitionbox}


\subsubsection*{Plackett-Luce Model}
\label{plackett-luce-model}
## Plackett-Luce模型
## \label{plackett-luce-model}

The Plackett-Luce (PL) model~\cite{plackett1975analysis} is the standard extension of Bradley-Terry to full rankings. Given $K$ responses $y_1, \ldots, y_K$ with ranking $\pi$ (where $\pi(1)$ is the best):
Plackett-Luce（PL）模型~\cite{plackett1975analysis}是Bradley-Terry模型到完整排序的标准扩展。给定$K$个响应$y_1, \ldots, y_K$及其排序$\pi$（其中$\pi(1)$是最优的）：

\begin{keybox}[Plackett-Luce Likelihood]
\begin{keybox}[Plackett-Luce似然]
\[
P(\pi \mid q) = \prod_{i=1}^{K} \frac{e^{r_\phi(y_{\pi(i)}, q)}}{\sum_{j=i}^{K} e^{r_\phi(y_{\pi(j)}, q)}}
\]
 \textbf{Intuition}: Sequentially select the best remaining item. At each step, the probability of selecting item $\pi(i)$ is softmax over the remaining items.
 \textbf{直觉}：依次选择剩余的最佳项。每一步，选择项$\pi(i)$的概率是剩余项上的softmax。

\textbf{Loss function}: 
\textbf{损失函数}：
\[
\mathcal{L}_{\text{PL}}(\phi) = -\frac{1}{|\mathcal{D}|} \sum_{(q, \pi) \in \mathcal{D}} \sum_{i=1}^{K-1} \left[ r_\phi(y_{\pi(i)}, q) - \log \sum_{j=i}^{K} e^{r_\phi(y_{\pi(j)}, q)} \right]
\]
\end{keybox}


\begin{intuitionbox}[Plackett-Luce Reduces to Bradley-Terry]
\begin{intuitionbox}[Plackett-Luce退化为Bradley-Terry]
For $K=2$, the PL model gives: $P(y_1 \succ y_2) = \frac{e^{r(y_1)}}{e^{r(y_1)} + e^{r(y_2)}} = \sigma(r(y_1) - r(y_2))$ --- exactly the Bradley-Terry model. PL is a strict generalization.
对于$K=2$，PL模型给出：$P(y_1 \succ y_2) = \frac{e^{r(y_1)}}{e^{r(y_1)} + e^{r(y_2)}} = \sigma(r(y_1) - r(y_2))$ —— 正是Bradley-Terry模型。PL是其严格推广。
\end{intuitionbox}


\subsubsection*{ListMLE and Rank-Based Losses}
\label{listmle-and-rank-based-losses}
## ListMLE与基于排序的损失
## \label{listmle-and-rank-based-losses}

\begin{keybox}[Listwise Loss Functions]
\begin{itemize}
  \item \textbf{ListMLE}~\cite{xia2008listwise}: Directly maximizes the PL likelihood of the ground-truth ranking. Simple and effective.
  \item \textbf{ListMLE}~\cite{xia2008listwise}：直接最大化真实排序的PL似然。简单且有效。
  \item \textbf{ListNet}~\cite{cao2007listnet}: Minimizes KL divergence between the model’s top-1 probability distribution and the ground-truth: 
\[
\mathcal{L}_{\text{ListNet}} = -\sum_{i=1}^{K} P_{\text{true}}(y_i \text{ is best}) \cdot \log P_{\text{model}}(y_i \text{ is best})
\]
 where $P_{\text{model}}(y_i \text{ is best}) = \frac{e^{r_\phi(y_i)}}{\sum_j e^{r_\phi(y_j)}}$.
  \item \textbf{ListNet}~\cite{cao2007listnet}：最小化模型top-1概率分布与真实分布之间的KL散度：
\[
\mathcal{L}_{\text{ListNet}} = -\sum_{i=1}^{K} P_{\text{true}}(y_i \text{ is best}) \cdot \log P_{\text{model}}(y_i \text{ is best})
\]
 其中 $P_{\text{model}}(y_i \text{ is best}) = \frac{e^{r_\phi(y_i)}}{\sum_j e^{r_\phi(y_j)}}$。
  \item \textbf{LambdaRank}~\cite{burges2006lambdarank}: Weights pairwise gradients by the change in ranking metric (e.g., NDCG). Useful when ranking quality matters more at the top.
  \item \textbf{LambdaRank}~\cite{burges2006lambdarank}：通过排序指标（如NDCG）的变化加权成对梯度。当排名质量在顶部更为重要时非常有用。
  \item \textbf{RankNet}~\cite{burges2005ranknet}: Pairwise cross-entropy summed over all pairs --- equivalent to BT on all $\binom{K}{2}$ pairs extracted from the ranking.
  \item \textbf{RankNet}~\cite{burges2005ranknet}：对所有配对求和成对交叉熵——等价于在从排序中提取的所有$\binom{K}{2}$个配对上应用Bradley-Terry模型。
\end{itemize}
\end{keybox}

\subsubsection*{Listwise Rewards for GRPO and Rejection Sampling}
\subsubsection*{用于GRPO和拒绝采样的列表式奖励}
\label{listwise-rewards-for-grpo-and-rejection-sampling}

\begin{keybox}[Integration with GRPO]
GRPO naturally produces ranked groups: for each prompt, $N$ responses are scored and ranked. A listwise reward model can be trained directly on these rankings:

GRPO自然产生排序组：对每个提示，对$N$个响应进行评分和排序。列表式奖励模型可以直接在这些排序上训练：

\begin{enumerate}
  \item \textbf{Generate}: Sample $N=8$ responses per prompt from the policy.
  \item \textbf{生成}：从策略中为每个提示采样$N=8$个响应。
  \item \textbf{Rank}: Use an existing reward model (or human annotators) to produce a full ranking $\pi$.
  \item \textbf{排序}：使用现有的奖励模型（或人工标注员）产生完整排序$\pi$。
  \item \textbf{Train listwise RM}: Optimize the PL loss on $(q, \pi)$ tuples.
  \item \textbf{训练列表式RM}：在$(q, \pi)$元组上优化PL损失。
  \item \textbf{Use in GRPO}: The listwise RM assigns scalar rewards $r(y_i, q)$ to each response; GRPO computes advantages as $\hat{A}_i = (r_i - \mu) / \sigma$.
  \item \textbf{在GRPO中使用}：列表式RM为每个响应分配标量奖励$r(y_i, q)$；GRPO计算优势为$\hat{A}_i = (r_i - \mu) / \sigma$。
\end{enumerate}

\textbf{Advantage over pairwise}: The listwise RM sees all $N$ responses simultaneously, learning that rank-1 should have much higher reward than rank-$N$ (not just ``slightly better than one other response'').

\textbf{相对于成对方法的优势}：列表式RM同时看到所有$N$个响应，学习到排名第1的奖励应远高于排名第$N$的奖励（而不仅仅是“比另一个响应稍好”）。
\end{keybox}

\subsubsection*{Practical Considerations}
\subsubsection*{实践考虑}
\label{practical-considerations}

\begin{warningbox}[Listwise Training Challenges]
\begin{itemize}
  \item \textbf{Annotation cost}: Full rankings are expensive. Partial rankings (top-3 out of 8) reduce cost with minimal quality loss.
  \item \textbf{标注成本}：完整排序成本高昂。部分排序（如8个中取前3）在质量损失极小的情况下降低成本。
  \item \textbf{Ties}: Real rankings often have ties. Use the Plackett-Luce extension for ties: assign equal probability mass to tied items.
  \item \textbf{平局}：实际排序中常有平局。使用Plackett-Luce的平局扩展：为平局项分配相等概率质量。
  \item \textbf{Position bias}: Annotators tend to prefer items shown first. Randomize presentation order and train debiasing.
  \item \textbf{位置偏差}：标注员倾向于偏好先显示的项。随机化呈现顺序并训练去偏。
  \item \textbf{List length}: Training on $K=4$--8 is typical. Longer lists ($K>16$) add noise without much benefit.
  \item \textbf{列表长度}：通常在$K=4$--8上训练。更长的列表（$K>16$）增加噪声而收益不大。
  \item \textbf{Consistency}: Rankings from different annotators may disagree. Use inter-annotator agreement ($\kappa > 0.6$) as a quality filter.
  \item \textbf{一致性}：不同标注员的排序可能不一致。使用标注员间一致性（$\kappa > 0.6$）作为质量过滤器。
\end{itemize}
\end{warningbox}

\begin{examplebox}[Plackett-Luce Training Code]
\begin{lstlisting}[style=pythonstyle]
import torch
import torch.nn.functional as F


def plackett_luce_loss(rewards, rankings):
    """
    Args:
        rewards: (batch, K) - predicted scalar rewards for K responses
        rankings: (batch, K) - ground-truth ranking indices (0 = best)
    Returns:
        scalar loss
    """
    # 参数：
    #   rewards: (batch, K) - 对K个响应预测的标量奖励
    #   rankings: (batch, K) - 真实排序索引（0为最佳）
    # 返回：
    #   标量损失
    batch_size, K = rewards.shape
    # Sort rewards by ground-truth ranking order
    sorted_rewards = torch.gather(rewards, 1, rankings)  # (batch, K)
    
    # 按真实排序顺序排序奖励
    # PL log-likelihood: sum over positions
    loss = 0.0
    for i in range(K - 1):
        # Log-softmax over remaining items (position i to K)
        remaining = sorted_rewards[:, i:]           # (batch, K-i)
        log_probs = remaining[:, 0] - torch.logsumexp(remaining, dim=1)
        loss -= log_probs.mean()
    
    return loss / (K - 1)


# PL对数似然：对所有位置求和
# Example: 8 responses per prompt, ranked by annotator
rewards = reward_model(responses)          # (batch, 8)
rankings = torch.argsort(human_scores, descending=True)  # best first
loss = plackett_luce_loss(rewards, rankings)
loss.backward()
# 示例：每个提示8个响应，由标注员排序
\end{lstlisting}
\end{examplebox}