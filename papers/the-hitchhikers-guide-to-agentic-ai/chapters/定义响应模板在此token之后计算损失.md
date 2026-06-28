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


