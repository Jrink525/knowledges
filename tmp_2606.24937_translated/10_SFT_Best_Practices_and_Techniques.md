## SFT Best Practices and Techniques
## SFT 最佳实践与技术

\label{sec:sft-best-practices}

Supervised Fine-Tuning (SFT) is the foundation of the RLHF pipeline. The quality of the SFT model determines the ceiling of what RL can achieve: RL can refine and improve a behaviour, but it cannot reliably introduce a behaviour that is entirely absent from the SFT model. This section covers the key techniques for effective SFT.
监督微调（SFT）是 RLHF 流程的基础。SFT 模型的质量决定了 RL 所能达到的上限：RL 可以优化和改进某种行为，但无法可靠地引入 SFT 模型中完全不存在的行为。本节涵盖了有效 SFT 的关键技术。

## Sequence Packing for Efficiency
## 序列打包以提高效率

\label{sec:sequence-packing}

\begin{intuitionbox}[The Padding Problem]
Standard SFT batches pad all sequences to the length of the longest sequence in the batch. For datasets with high length variance (e.g., a mix of short instructions and long documents), this wastes 50--80\% of compute on padding tokens. Sequence packing eliminates this waste.
\end{intuitionbox}
\begin{intuitionbox}[填充问题]
标准的 SFT 批次会将所有序列填充到批次中最长序列的长度。对于长度方差较大的数据集（例如，短指令和长文档的混合），这会在填充 token 上浪费 50%–80% 的计算量。序列打包消除了这种浪费。
\end{intuitionbox}

Sequence packing concatenates multiple short examples into a single sequence of length \texttt{max\_seq\_length}, separated by EOS tokens. The attention mask ensures that tokens from different examples do not attend to each other:
序列打包将多个短样本连接成一个长度为 \texttt{max\_seq\_length} 的单一序列，由 EOS token 分隔。注意力掩码确保来自不同样本的 token 不会相互关注：

\begin{enumerate}
  \item Sort examples by length (optional, improves packing efficiency).
  \item 按长度对样本排序（可选，提高打包效率）。
  \item Greedily pack examples into bins of size \texttt{max\_seq\_length}.
  \item 贪心地将样本打包到大小为 \texttt{max\_seq\_length} 的桶中。
  \item Use a block-diagonal attention mask to prevent cross-example attention.
  \item 使用块对角注意力掩码，防止跨样本注意力。
  \item Compute loss only on non-padding tokens.
  \item 仅对非填充 token 计算损失。
\end{enumerate}

\begin{keybox}[Packing Efficiency]
\begin{itemize}
  \item Typical packing efficiency: 85--95\% (vs 20--50\% with padding).
  \item 典型打包效率：85%–95%（对比填充的 20%–50%）。
  \item Speedup: 2--4$\times$ for datasets with high length variance.
  \item 加速比：对于长度方差大的数据集为 2–4$\times$。
  \item Memory: similar to padding (same total tokens per batch).
  \item 内存：与填充相似（同一批次的总 token 数相同）。
  \item Caveat: requires careful attention masking to avoid cross-contamination.
  \item 注意事项：需要仔细的注意力掩码，以避免交叉污染。
\end{itemize}
\end{keybox}
\begin{keybox}[打包效率]
\begin{itemize}
  \item 典型打包效率：85%–95%（对比填充的 20%–50%）。
  \item 加速比：对于长度方差大的数据集为 2–4$\times$。
  \item 内存：与填充相似（同一批次的总 token 数相同）。
  \item 注意事项：需要仔细的注意力掩码，以避免交叉污染。
\end{itemize}
\end{keybox}

\begin{examplebox}[Sequence Packing in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import SFTConfig, SFTTrainer


config = SFTConfig(
    max_seq_length=4096,
    packing=True,           # enable sequence packing
    output_dir="sft_model",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-5,
    num_train_epochs=3,
)


trainer = SFTTrainer(
    model=model,
    args=config,
    train_dataset=dataset,
    # dataset_text_field="text",  # or use formatting_func
)
trainer.train()
\end{lstlisting}
\end{examplebox}
\begin{examplebox}[TRL 中的序列打包]
\begin{lstlisting}[style=pythonstyle]
from trl import SFTConfig, SFTTrainer


config = SFTConfig(
    max_seq_length=4096,
    packing=True,           # 启用序列打包
    output_dir="sft_model",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-5,
    num_train_epochs=3,
)


trainer = SFTTrainer(
    model=model,
    args=config,
    train_dataset=dataset,
    # dataset_text_field="text",  # 或使用 formatting_func
)
trainer.train()
\end{lstlisting}
\end{examplebox}

## Chat Templates and Formatting
## 聊天模板与格式化

\label{sec:chat-templates}

\begin{intuitionbox}[Why Chat Templates Matter]
Language models are trained on raw text, but instruction-following models need to distinguish between system prompts, user messages, and assistant responses. Chat templates encode this structure into the token sequence. Using the wrong template (or no template) at inference time causes significant performance degradation.
\end{intuitionbox}
\begin{intuitionbox}[聊天模板的重要性]
语言模型是在原始文本上训练的，但指令遵循模型需要区分系统提示、用户消息和助手响应。聊天模板将这种结构编码到 token 序列中。在推理时使用错误的模板（或没有模板）会导致显著的性能下降。
\end{intuitionbox}

\subsubsection*{ChatML Format}
\subsubsection*{ChatML 格式}
\label{chatml-format}

ChatML is the most widely used chat template:
ChatML 是使用最广泛的聊天模板：

\begin{lstlisting}[style=pythonstyle]
# ChatML format
template = """<|im_start|>system
{system_message}<|im_end|>
<|im_start|>user
{user_message}<|im_end|>
<|im_start|>assistant
{assistant_message}<|im_end|>"""
\end{lstlisting}

\subsubsection*{Llama Format}
\subsubsection*{Llama 格式}
\label{llama-format}

Llama 3 uses a different template with special tokens:
Llama 3 使用了一种不同的模板，带有特殊 token：

\begin{lstlisting}[style=pythonstyle]
# Llama 3 format
template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{system_message}<|eot_id|><|start_header_id|>user<|end_header_id|>
{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
{assistant_message}<|eot_id|>"""
\end{lstlisting}

\begin{examplebox}[Applying Chat Templates in TRL]
\begin{lstlisting}[style=pythonstyle]
from transformers import AutoTokenizer
from trl import SFTConfig, SFTTrainer


tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")


def formatting_func(example):
    """Apply chat template to a dataset example."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": example["instruction"]},
        {"role": "assistant", "content": example["response"]},
    ]
    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
    )


config = SFTConfig(
    max_seq_length=2048,
    output_dir="sft_model",
)


trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    args=config,
    train_dataset=dataset,
    formatting_func=formatting_func,
)
\end{lstlisting}
\end{examplebox}
\begin{examplebox}[在 TRL 中应用聊天模板]
\begin{lstlisting}[style=pythonstyle]
from transformers import AutoTokenizer
from trl import SFTConfig, SFTTrainer


tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")


def formatting_func(example):
    """将聊天模板应用于数据集样本。"""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": example["instruction"]},
        {"role": "assistant", "content": example["response"]},
    ]
    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
    )


config = SFTConfig(
    max_seq_length=2048,
    output_dir="sft_model",
)


trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    args=config,
    train_dataset=dataset,
    formatting_func=formatting_func,
)
\end{lstlisting}
\end{examplebox}

## Completion-Only Masking
## 仅完成掩码

\label{sec:completion-masking}

\begin{intuitionbox}[Why Mask the Prompt?]
In instruction fine-tuning, the model should learn to generate the assistant’s response, not to predict the user’s question or the system prompt. Computing loss on the prompt tokens wastes gradient signal and can cause the model to ``memorise'' prompts rather than learning to respond to them. Completion-only masking sets the loss to zero for all non-assistant tokens.
\end{intuitionbox}
\begin{intuitionbox}[为什么要掩码提示？]
在指令微调中，模型应该学习生成助手的响应，而不是预测用户的问题或系统提示。在提示 token 上计算损失会浪费梯度信号，并可能导致模型“记忆”提示而不是学习如何响应。仅完成掩码将所有非助手 token 的损失设为零。
\end{intuitionbox}

\begin{examplebox}[Completion-Only Masking in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import SFTConfig, SFTTrainer, DataCollatorForCompletionOnlyLM
from transformers import AutoTokenizer


tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")


# Define the response template (tokens after which loss is computed)
response_template = "<|start_header_id|>assistant<|end_header_id|>"
collator = DataCollatorForCompletionOnlyLM(
    response_template=response_template,
    tokenizer=tokenizer,
)


config = SFTConfig(
    max_seq_length=2048,
    output_dir="sft_model",
)


trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    args=config,
    train_dataset=dataset,
    data_collator=collator,   # completion-only masking
    formatting_func=formatting_func,
)
\end{lstlisting}
\end{examplebox}
\begin{examplebox}[TRL 中的仅完成掩码]
\begin{lstlisting}[style=pythonstyle]
from trl import SFTConfig, SFTTrainer, DataCollatorForCompletionOnlyLM
from transformers import AutoTokenizer


tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")


# 定义响应模板（在此 token 之后计算损失）
response_template = "<|start_header_id|>assistant<|end_header_id|>"
collator = DataCollatorForCompletionOnlyLM(
    response_template=response_template,
    tokenizer=tokenizer,
)


config = SFTConfig(
    max_seq_length=2048,
    output_dir="sft_model",
)


trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    args=config,
    train_dataset=dataset,
    data_collator=collator,   # 仅完成掩码
    formatting_func=formatting_func,
)
\end{lstlisting}
\end{examplebox}

\begin{warningbox}[Completion Masking Pitfalls]
\begin{itemize}
  \item The response template must exactly match the tokenised form. Off-by-one errors in tokenisation can cause the mask to be applied incorrectly.
  \item 响应模板必须与 token 化后的形式完全匹配。token 化中的差一错误可能导致掩码应用错误。
  \item For very short responses, masking the prompt may leave too few tokens for meaningful gradient signal. Consider a minimum response length threshold.
  \item 对于非常短的响应，掩码提示可能会留下太少的 token，无法提供有意义的梯度信号。考虑设置一个最小响应长度阈值。
  \item Multi-turn conversations require masking all non-assistant turns, not just the first.
  \item 多轮对话需要掩码所有非助手轮次，而不仅仅是第一轮。
\end{itemize}
\end{warningbox}
\begin{warningbox}[完成掩码的陷阱]
\begin{itemize}
  \item 响应模板必须与 token 化后的形式完全匹配。token 化中的差一错误可能导致掩码应用错误。
  \item 对于非常短的响应，掩码提示可能会留下太少的 token，无法提供有意义的梯度信号。考虑设置一个最小响应长度阈值。
  \item 多轮对话需要掩码所有非助手轮次，而不仅仅是第一轮。
\end{itemize}
\end{warningbox}

## Data Mixing Strategies for Multi-Task SFT
## 多任务 SFT 的数据混合策略

\label{sec:data-mixing}

\begin{intuitionbox}[The Multi-Task Challenge]
Training on multiple tasks simultaneously can improve generalisation but also causes \emph{task interference}: gradients from different tasks conflict, degrading performance on individual tasks. Data mixing strategies control the relative contribution of each task to the training signal.
\end{intuitionbox}
\begin{intuitionbox}[多任务挑战]
同时训练多个任务可以提高泛化能力，但也会导致 \emph{任务干扰}：来自不同任务的梯度相互冲突，降低了单个任务的性能。数据混合策略控制每个任务对训练信号的相对贡献。
\end{intuitionbox}

\subsubsection*{Proportional Mixing}
\subsubsection*{比例混合}
\label{proportional-mixing}

Sample from each dataset proportionally to its size:
从每个数据集中按其大小比例采样：

\[
p_k = \frac{N_k}{\sum_{j=1}^K N_j},
\]

where $N_k$ is the number of examples in dataset $k$. This is the default in most frameworks and works well when datasets are of similar quality.
其中 $N_k$ 是数据集 $k$ 中的样本数。这是大多数框架中的默认设置，当数据集质量相似时效果良好。

\subsubsection*{Temperature Mixing}
\subsubsection*{温度混合}
\label{temperature-mixing}

Apply a temperature $T$ to smooth the proportions:
应用温度 $T$ 来平滑比例：

\[
p_k \propto N_k^{1/T}.
\]

$T=1$: proportional mixing. $T \to \infty$: uniform mixing. $T < 1$: over-samples large datasets. $T > 1$: over-samples small datasets.
$T=1$：比例混合。$T \to \infty$：均匀混合。$T < 1$：过采样大数据集。$T > 1$：过采样小数据集。

\subsubsection*{Quality-Weighted Mixing}
\subsubsection*{质量加权混合}
\label{quality-weighted-mixing}

Weight datasets by estimated quality (e.g., perplexity under a reference model, human quality ratings):
根据估计的质量（例如，在参考模型下的困惑度、人工质量评分）对数据集进行加权：

\[
p_k \propto N_k \cdot q_k,
\]

where $q_k$ is the quality score for dataset $k$.
其中 $q_k$ 是数据集 $k$ 的质量分数。

\begin{examplebox}[Data Mixing in TRL]
\begin{lstlisting}[style=pythonstyle]
from datasets import concatenate_datasets, interleave_datasets


# Proportional mixing (default)
mixed_dataset = concatenate_datasets([
    dataset_math,
    dataset_code,
    dataset_general,
]).shuffle(seed=42)

\end{lstlisting}
\end{examplebox}
\begin{examplebox}[TRL 中的数据混合]
\begin{lstlisting}[style=pythonstyle]
from datasets import concatenate_datasets, interleave_datasets


# 比例混合（默认）
mixed_dataset = concatenate_datasets([
    dataset_math,
    dataset_code,
    dataset_general,
]).shuffle(seed=42)

\end{lstlisting}
\end{examplebox}

```markdown
\begin{examplebox}[Temperature Mixing for Imbalanced Datasets]
\begin{lstlisting}[language=Python, caption=Temperature scaling for dataset mixing]
# Temperature mixing (T=2: over-sample small datasets)
# 温度混合（T=2：对小数据集进行过采样）
mixed_dataset = interleave_datasets(
    [dataset_math, dataset_code, dataset_general],
    probabilities=[0.4, 0.4, 0.2],   # manually set after temperature scaling
                                     # 在温度缩放后手动设置
    seed=42,
)

config = SFTConfig(output_dir="sft_model")
trainer = SFTTrainer(
    model=model,
    args=config,
    train_dataset=mixed_dataset,
)
\end{lstlisting}
\end{examplebox}


\section{When SFT Hurts -- Catastrophic Forgetting and Alignment Tax}
\section{当监督微调有害时——灾难性遗忘与对齐税}
\label{sec:sft-pitfalls}


As LLMs transition through sequential training phases --- pre-training $\rightarrow$ continued pre-training $\rightarrow$ SFT $\rightarrow$ RLHF/DPO --- performance degradation frequently manifests on standard benchmarks. Two \textbf{fundamentally distinct} phenomena drive these regressions, and confusing them leads to wrong mitigation strategies.
随着大语言模型经历连续的训练阶段——预训练 $\rightarrow$ 继续预训练 $\rightarrow$ 监督微调 $\rightarrow$ 强化学习从人类反馈/直接偏好优化——在标准基准测试上经常出现性能下降。两种**根本不同**的现象驱动了这些退化，混淆它们会导致错误的缓解策略。


\subsection{Catastrophic Forgetting (Structural Erasure)}
\subsection{灾难性遗忘（结构性擦除）}
\label{catastrophic-forgetting-structural-erasure}


\begin{warningbox}[Catastrophic Forgetting]
\begin{warningbox}[灾难性遗忘]
Catastrophic forgetting is an \textbf{unintentional optimization failure}: when a network optimized on distribution $\mathcal{D}_A$ is subsequently trained on a disjoint distribution $\mathcal{D}_B$, the weight updates required for $\mathcal{D}_B$ \emph{physically overwrite} the parameter structures encoding $\mathcal{D}_A$: 
灾难性遗忘是一种**非有意的优化失败**：当在分布 $\mathcal{D}_A$ 上优化的网络随后在不交分布 $\mathcal{D}_B$ 上训练时，$\mathcal{D}_B$ 所需的权重更新会*物理覆盖*编码 $\mathcal{D}_A$ 的参数结构：
\begin{equation}
\theta_{t+1} = \theta_t - \eta \nabla_\theta \mathcal{L}_B(\theta_t) \quad \implies \quad \mathcal{L}_A(\theta_{t+1}) \gg \mathcal{L}_A(\theta_t)
\end{equation}
 The knowledge is \textbf{destroyed} --- the weights encoding Task A no longer exist. This is irreversible without retraining.
知识被**摧毁**——编码任务A的权重不复存在。除非重新训练，否则这是不可逆的。
\end{warningbox}


\textbf{Symptoms}:
**症状**：


\begin{itemize}
  \item Complete breakdown on tasks not in fine-tuning data (e.g., model forgets how to do math after SFT on chat data)
  \item 在微调数据未覆盖的任务上完全崩溃（例如，模型在聊天数据上经过监督微调后忘记了如何做数学）
  \item Loss of language diversity --- model only generates in the narrow style of fine-tuning distribution
  \item 语言多样性丧失——模型仅以微调分布的狭窄风格生成
  \item Reduced factual accuracy on knowledge not reinforced during fine-tuning
  \item 对微调期间未强化的知识的事实准确性降低
  \item Degraded multilingual ability after English-only SFT
  \item 仅英文监督微调后多语言能力下降
\end{itemize}


\textbf{Mechanistic cause --- Fisher Information perspective}: The Fisher Information Matrix $F$ of Task A identifies which parameters are ``important'' for $\mathcal{D}_A$: 
**机制原因——Fisher信息视角**：任务A的Fisher信息矩阵$F$识别哪些参数对于$\mathcal{D}_A$是“重要的”：
\begin{equation}
F = \mathbb{E}_{x \sim \mathcal{D}_A}\!\left[\nabla_\theta \log \pi_\theta(x)\, \nabla_\theta \log \pi_\theta(x)^T\right]
\end{equation}
 Parameters with high Fisher eigenvalues are critical for Task A. Unconstrained gradient descent on Task B ignores these eigenvalues entirely --- $\Delta\theta$ points along $\nabla\mathcal{L}_B$ regardless of whether it destroys high-Fisher directions for $\mathcal{L}_A$.
具有高Fisher特征值的参数对任务A至关重要。任务B上的无约束梯度下降完全忽略这些特征值——$\Delta\theta$沿着$\nabla\mathcal{L}_B$方向，无论是否破坏了$\mathcal{L}_A$的高Fisher方向。


\subsection{Alignment Tax (Behavioral Constraint)}
\subsection{对齐税（行为约束）}
\label{alignment-tax-behavioral-constraint}


The alignment tax is a \textbf{deliberate, expected trade-off}: the model’s raw capability (unconstrained generation, maximal reasoning bandwidth) decreases because the policy is constrained to produce safe, well-formatted, preference-aligned outputs.
对齐税是一种**故意的、预期的权衡**：模型的原始能力（无约束生成、最大推理带宽）下降，因为策略被约束为生成安全、格式良好、偏好对齐的输出。


\textbf{Mechanism}: During DPO/PPO, the policy $\pi_\theta$ is penalized for deviating from the reference $\pi_{\text{ref}}$ via KL divergence: 
**机制**：在直接偏好优化/近端策略优化期间，策略$\pi_\theta$因偏离参考$\pi_{\text{ref}}$而通过KL散度受到惩罚：
\begin{equation}
r_{\text{implicit}}(x, y) = \beta \log \frac{\pi_\theta(y|x)}{\pi_{\text{ref}}(y|x)}
\end{equation}


This leash constrains the model’s \textbf{output distribution} --- it cannot explore high-variance reasoning paths that deviate too far from the reference. The knowledge is \textbf{not erased}; it’s \emph{suppressed}. The model still ``knows'' the answer but its distribution is flattened toward safe, generic responses.
这条“缰绳”约束了模型的**输出分布**——它无法探索偏离参考过远的高方差推理路径。知识**没有被擦除**，而是被*抑制*。模型仍然“知道”答案，但其分布被拉平为安全、通用的回应。


\textbf{Symptoms}:
**症状**：


\begin{itemize}
  \item Over-refusal (``I can’t help with that'' for benign queries)
  \item 过度拒绝（对良性查询回答“我无法帮助”）
  \item Stylistic stiffness --- hedge words, excessive caveats, verbose safety disclaimers
  \item 风格僵化——模糊措辞、过度警告、冗长的安全声明
  \item Lower scores on raw capability benchmarks (MMLU, HumanEval) while improving on preference benchmarks (MT-Bench, AlpacaEval)
  \item 在原始能力基准测试（MMLU, HumanEval）上得分较低，同时在偏好基准测试（MT-Bench, AlpacaEval）上有所提升
  \item Reduced ability to produce complex, high-entropy outputs (creative writing, novel algorithms)
  \item 生成复杂、高熵输出（创意写作、新颖算法）的能力下降
\end{itemize}


\subsection{Comparative Taxonomy}
\subsection{比较分类学}
\label{comparative-taxonomy}


\begin{table}[ht!]
\centering
\caption{Catastrophic Forgetting vs. Alignment Tax --- complete comparison.}
\caption{灾难性遗忘 vs 对齐税——完整比较}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Dimension} & \textbf{Catastrophic Forgetting} & \textbf{Alignment Tax} \\
\textbf{维度} & \textbf{灾难性遗忘} & \textbf{对齐税} \\
\midrule
\textbf{Intentionality} & Unintentional (optimization artifact) & Expected trade-off (incurred deliberately for safety/helpfulness) \\
\textbf{意图性} & 非有意（优化伪影） & 预期的权衡（为安全性/帮助性故意承担） \\
\textbf{Parameter state} & Prior knowledge physically overwritten & Latent distributions constrained/truncated \\
\textbf{参数状态} & 先验知识被物理覆盖 & 潜在分布被约束/截断 \\
\textbf{Information} & \textbf{Destroyed}: weights no longer encode the capability & \textbf{Suppressed}: knowledge exists but is harder to trigger \\
\textbf{信息状态} & \textbf{摧毁}：权重不再编码该能力 & \textbf{抑制}：知识存在但更难触发 \\
\textbf{Dominant phase} & Sequential SFT, domain continued pre-training & Preference optimization (PPO, DPO, KTO, RLHF) \\
\textbf{主导阶段} & 连续监督微调、领域继续预训练 & 偏好优化（PPO, DPO, KTO, RLHF） \\
\textbf{Primary symptom} & Complete breakdown of baseline capabilities & Over-refusal, stylistic stiffness, lower raw benchmark scores \\
\textbf{主要症状} & 基线能力完全崩溃 & 过度拒绝、风格僵化、原始基准测试分数降低 \\
\textbf{Reversibility} & Irreversible without retraining from checkpoint & Partially reversible: adjust $\beta$, system prompt, or fine-tune \\
\textbf{可逆性} & 不可逆，除非从检查点重新训练 & 部分可逆：调整$\beta$、系统提示或微调 \\
\textbf{Detection} & Perplexity on pre-training eval set spikes & Perplexity stable but win-rate on capability benchmarks drops \\
\textbf{检测方式} & 预训练评估集上的困惑度激增 & 困惑度稳定，但能力基准测试上的胜率下降 \\
\textbf{Scales with model size} & Similar across scales & Smaller models pay a larger alignment tax \\
\textbf{与模型规模的关系} & 各规模相似 & 较小模型承担更大的对齐税 \\
\bottomrule
\end{tabular}
\end{table}


\subsection{Mitigation Strategies}
\subsection{缓解策略}
\label{mitigation-strategies}


\textbf{For Catastrophic Forgetting}:
**针对灾难性遗忘**：


\begin{enumerate}
  \item \textbf{Data replay}: Mix 5--10\% of pre-training data into SFT dataset. Ensures gradient updates don’t completely neglect pre-training distribution.
  \item **数据重放**：将5-10%的预训练数据混入监督微调数据集。确保梯度更新不会完全忽略预训练分布。
  \item \textbf{Elastic Weight Consolidation (EWC)}~\cite{kirkpatrick2017overcoming}: Add regularization $\Omega(\theta) = \frac{\lambda}{2}\sum_i F_i(\theta_i - \theta_i^*)^2$ that penalizes changes to parameters with high Fisher information for the original task.
  \item **弹性权重巩固（Elastic Weight Consolidation, EWC）**~\cite{kirkpatrick2017overcoming}：添加正则化项$\Omega(\theta) = \frac{\lambda}{2}\sum_i F_i(\theta_i - \theta_i^*)^2$，惩罚对原始任务具有高Fisher信息的参数的改变。
  \item \textbf{LoRA / Parameter-efficient fine-tuning}: Train only low-rank adapters ($<1\%$ of parameters), leaving base weights completely frozen. This prevents \emph{permanent destruction} of pre-trained knowledge --- you can always remove the adapter and recover the original model. However, \textbf{while the adapter is active}, the combined system $(W_0 + BA)$ can still exhibit forgetting: the adapter may shift the model’s effective behavior away from old skills. LoRA protects the checkpoint, not the active inference behavior.
  \item **LoRA / 参数高效微调**：仅训练低秩适配器（参数量的$<1\%$），保持基础权重完全冻结。这防止了预训练知识的*永久破坏*——你始终可以移除适配器并恢复原始模型。然而，**当适配器激活时**，组合系统$(W_0 + BA)$仍可能表现出遗忘：适配器可能将模型的有效行为偏离旧技能。LoRA保护的是检查点，而非当前的推理行为。
  \item \textbf{Conservative learning rate}: Use $1$--$5 \times 10^{-6}$ with few epochs (1--3). Larger rates accelerate forgetting.
  \item **保守学习率**：使用$1$--$5 \times 10^{-6}$，少量轮次（1-3）。较大的学习率会加速遗忘。
  \item \textbf{Progressive training}: Mix distributions gradually, increasing SFT data proportion over time rather than switching abruptly.
  \item **渐进式训练**：逐渐混合分布，随时间增加监督微调数据比例，而非突然切换。
\end{enumerate}


\textbf{For Alignment Tax}:
**针对对齐税**：


\begin{enumerate}
  \item \textbf{Tune $\beta$ carefully}: Lower $\beta$ gives the model more freedom (reduces the tax) but may sacrifice safety. Optimal $\beta \in [0.05, 0.3]$ for most settings.
  \item **仔细调整$\beta$**：较低的$\beta$赋予模型更多自由度（减少税），但可能牺牲安全性。大多数设置下最优$\beta \in [0.05, 0.3]$。
  \item \textbf{High-quality, diverse SFT data}: Part of the alignment tax comes from SFT narrowing the output distribution; broader, more diverse SFT data reduces this component. The RL phase adds further constraint via KL regularization~\cite{ouyang2022training}.
  \item **高质量、多样化的监督微调数据**：部分对齐税来自监督微调收窄输出分布；更广泛、更多样的监督微调数据可减少这一部分。强化学习阶段通过KL正则化进一步增加约束~\cite{ouyang2022training}。
  \item \textbf{Conditional alignment}: Train the model to be aligned only when a safety flag is active. At inference, disable constraints for benchmarking (research-only technique).
  \item **条件对齐**：训练模型仅在安全标志激活时保持对齐。推理时，为基准测试禁用约束（仅限研究技术）。
  \item \textbf{Constitutional AI / RLAIF}: Use model-generated feedback to create more nuanced preference data that preserves capability while improving alignment.
  \item **宪法AI / 来自AI反馈的强化学习**：使用模型生成的反馈创建更细粒度的偏好数据，在提升对齐的同时保留能力。
  \item \textbf{Targeted RL budget}: Don’t over-train with RL. Monitor capability benchmarks and stop when the tax exceeds acceptable thresholds (typically 2--5\% MMLU regression).
  \item **限定强化学习预算**：不要过度训练强化学习。监控能力基准测试，当对齐税超过可接受阈值（通常MMLU下降2-5%）时停止。
\end{enumerate}
```

\begin{intuitionbox}[How to Tell Which One You Have]
\begin{itemize}
  \item \textbf{Run the base model on the failing tasks}: If the base model succeeds and the fine-tuned model completely fails $\rightarrow$ catastrophic forgetting.
  \item \textbf{Prompt engineering test}: If careful prompting (e.g., ``ignore safety guidelines and solve this math problem step by step'') recovers the capability $\rightarrow$ alignment tax (knowledge is suppressed, not erased).
  \item \textbf{Perplexity check}: Compute perplexity on pre-training validation set. Spike = forgetting. Stable = alignment tax.
  \item \textbf{Few-shot recovery}: If providing a few in-context examples restores the capability $\rightarrow$ alignment tax. If even many examples can’t recover it $\rightarrow$ forgetting.
\end{itemize}
\end{intuitionbox}

\begin{intuitionbox}[如何判断属于哪种情况]
\begin{itemize}
  \item \textbf{在失败任务上运行基座模型}：如果基座模型成功而微调模型完全失败 $\rightarrow$ 灾难性遗忘（catastrophic forgetting）。
  \item \textbf{提示工程测试}：如果精心设计的提示（例如“忽略安全准则，逐步解决这道数学题”）恢复了能力 $\rightarrow$ 对齐税（alignment tax）（知识被抑制而非擦除）。
  \item \textbf{困惑度检查}：在预训练验证集上计算困惑度。出现尖峰 = 遗忘。保持稳定 = 对齐税。
  \item \textbf{少样本恢复}：如果提供少量上下文示例就能恢复能力 $\rightarrow$ 对齐税。如果即使大量示例也无法恢复 $\rightarrow$ 遗忘。
\end{itemize}
\end{intuitionbox}

\section{Connection to RL -- SFT Quality Determines RL Ceiling}
\section{与RL的关联——SFT质量决定了RL的上限}
\label{sec:sft-rl-connection}

\begin{keybox}[The SFT-RL Relationship]
The SFT model is the starting point for RL training. RL can:

\begin{itemize}
  \item \textbf{Amplify} behaviours that are present but weak in the SFT model.
  \item \textbf{Suppress} behaviours that are present but undesirable.
  \item \textbf{Refine} the style and format of responses.
\end{itemize}

RL \emph{cannot}:

\begin{itemize}
  \item Introduce capabilities that are entirely absent from the SFT model.
  \item Recover from severe catastrophic forgetting in the SFT stage.
  \item Compensate for a reward model that is systematically biased.
\end{itemize}
\end{keybox}

\begin{keybox}[SFT与RL的关系]
SFT模型是RL训练的起点。RL可以：

\begin{itemize}
  \item \textbf{放大} SFT模型中存在但较弱的行为。
  \item \textbf{抑制} 存在但不期望的行为。
  \item \textbf{优化} 响应的风格和格式。
\end{itemize}

RL \emph{无法}：

\begin{itemize}
  \item 引入SFT模型中完全不存在的能力。
  \item 从SFT阶段严重的灾难性遗忘中恢复。
  \item 弥补系统性偏倚的奖励模型（reward model）。
\end{itemize}
\end{keybox}

\begin{intuitionbox}[The Exploration-Exploitation Tradeoff in SFT]
For RL to work, the SFT model must occasionally produce correct responses (so the reward signal is non-zero). If the SFT model \emph{never} produces a correct response to a given prompt, RL cannot learn to produce correct responses -- there is no positive signal to amplify. This is why SFT quality is the ceiling for RL performance.

Concretely: if the SFT model solves 10\% of math problems correctly, RL can potentially push this to 80\%. If the SFT model solves 0\% of math problems, RL will make no progress (all rewards are zero, all advantages are zero, no gradient).
\end{intuitionbox}

\begin{intuitionbox}[SFT中的探索-利用权衡]
为了让RL工作，SFT模型必须偶尔产生正确的响应（这样奖励信号才非零）。如果SFT模型针对给定提示\emph{从未}产生正确响应，RL就无法学会产生正确响应——因为没有正信号可以放大。这就是为什么SFT质量是RL性能的上限。

具体来说：如果SFT模型正确解决了10\%的数学问题，RL有可能将其提升到80\%。如果SFT模型正确解决了0\%的数学问题，RL将毫无进展（所有奖励为零，所有优势为零，没有梯度）。
\end{intuitionbox}

\subsubsection*{Practical Implications}
\subsubsection*{实践启示}
\label{practical-implications}

\begin{enumerate}
  \item \textbf{SFT data quality}: use high-quality, diverse data. A small amount of high-quality data is better than a large amount of low-quality data.
  \item \textbf{SFT data coverage}: ensure the SFT data covers the tasks you want to improve with RL. If a task is not in the SFT data, RL will struggle.
  \item \textbf{SFT training duration}: do not over-train the SFT model. Over-training reduces diversity and makes RL exploration harder.
  \item \textbf{Warm-up}: consider a short SFT warm-up on task-specific data before RL, even if the base model is already instruction-tuned.
\end{enumerate}

\begin{enumerate}
  \item \textbf{SFT数据质量}：使用高质量、多样化的数据。少量高质量数据优于大量低质量数据。
  \item \textbf{SFT数据覆盖范围}：确保SFT数据涵盖你希望通过RL改进的任务。如果某个任务不在SFT数据中，RL将困难重重。
  \item \textbf{SFT训练时长}：不要过度训练SFT模型。过度训练会降低多样性，使RL探索更难。
  \item \textbf{热身}：即使基座模型已经过指令微调，也考虑在RL之前对任务特定数据进行短暂的SFT热身。
\end{enumerate}

\begin{examplebox}[Checking SFT Quality Before RL]
\begin{lstlisting}[style=pythonstyle]
import numpy as np
from tqdm import tqdm


def estimate_pass_at_k(model, tokenizer, dataset, k=8, n_samples=100):
    """
    Estimate pass@k for the SFT model.
    If pass@1 < 5%, RL will likely fail.
    If pass@k < 20%, RL will struggle.
    """
    pass_at_1_scores = []
    pass_at_k_scores = []

    for example in tqdm(dataset.select(range(n_samples))):
        prompt = example["prompt"]
        ground_truth = example["answer"]

        # Sample k completions
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.8,
            num_return_sequences=k,
        )

        correct = 0
        for output in outputs:
            response = tokenizer.decode(output, skip_special_tokens=True)
            if ground_truth in response:
                correct += 1

        # pass@1: fraction of samples that are correct (estimated success rate)
        pass_at_1_scores.append(correct / k)
        # pass@k: at least one of k samples is correct
        pass_at_k_scores.append(correct >= 1)

    print(f"Pass@1 (estimated): {np.mean(pass_at_1_scores):.2%}")
    print(f"Pass@{k}: {np.mean(pass_at_k_scores):.2%}")
    print(f"RL viability: {'Good' if np.mean(pass_at_1_scores) > 0.05 else 'Poor'}")


estimate_pass_at_k(sft_model, tokenizer, eval_dataset)
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[在RL之前检查SFT质量]
\begin{lstlisting}[style=pythonstyle]
import numpy as np
from tqdm import tqdm


def estimate_pass_at_k(model, tokenizer, dataset, k=8, n_samples=100):
    """
    Estimate pass@k for the SFT model.  # 估计SFT模型的pass@k
    If pass@1 < 5%, RL will likely fail.  # 如果pass@1 < 5%，RL很可能失败
    If pass@k < 20%, RL will struggle.    # 如果pass@k < 20%，RL将举步维艰
    """
    pass_at_1_scores = []
    pass_at_k_scores = []

    for example in tqdm(dataset.select(range(n_samples))):
        prompt = example["prompt"]
        ground_truth = example["answer"]

        # Sample k completions  # 采样k个补全
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.8,
            num_return_sequences=k,
        )

        correct = 0
        for output in outputs:
            response = tokenizer.decode(output, skip_special_tokens=True)
            if ground_truth in response:
                correct += 1

        # pass@1: fraction of samples that are correct (estimated success rate)  # pass@1：正确样本比例（估计成功率）
        pass_at_1_scores.append(correct / k)
        # pass@k: at least one of k samples is correct  # pass@k：k个样本中至少有一个正确
        pass_at_k_scores.append(correct >= 1)

    print(f"Pass@1 (estimated): {np.mean(pass_at_1_scores):.2%}")
    print(f"Pass@{k}: {np.mean(pass_at_k_scores):.2%}")
    print(f"RL viability: {'Good' if np.mean(pass_at_1_scores) > 0.05 else 'Poor'}")


estimate_pass_at_k(sft_model, tokenizer, eval_dataset)
\end{lstlisting}
\end{examplebox}

\begin{keybox}[SFT Best Practices Summary]
\begin{enumerate}
  \item Use sequence packing to maximise GPU utilisation.
  \item Apply completion-only masking to focus gradient on assistant responses.
  \item Use the correct chat template for your model family.
  \item Mix data proportionally with temperature scaling ($T \approx 2$) for multi-task SFT.
  \item Use LoRA to prevent catastrophic forgetting.
  \item Evaluate pass@k before starting RL to ensure the SFT model is a viable starting point.
  \item Do not over-train: 1--3 epochs is usually sufficient for instruction fine-tuning.
  \item Monitor diversity metrics (entropy, n-gram diversity) to detect mode collapse.
\end{enumerate}
\end{keybox}

\begin{keybox}[SFT最佳实践总结]
\begin{enumerate}
  \item 使用序列打包（sequence packing）以最大化GPU利用率。
  \item 应用仅补全掩码（completion-only masking），将梯度集中在助手的回复上。
  \item 为你的模型家族使用正确的聊天模板（chat template）。
  \item 在多任务SFT中，使用温度缩放（$T \approx 2$）按比例混合数据。
  \item 使用LoRA防止灾难性遗忘。
  \item 在开始RL之前评估pass@k，确保SFT模型是一个可行的起点。
  \item 不要过度训练：指令微调通常1-3个epoch就足够了。
  \item 监控多样性指标（熵、n-gram多样性）以检测模式坍缩（mode collapse）。
\end{enumerate}
\end{keybox}