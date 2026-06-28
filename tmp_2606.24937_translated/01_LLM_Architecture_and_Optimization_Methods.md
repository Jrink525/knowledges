# LLM Architecture and Optimization Methods
\label{llm-architecture-and-optimization-methods}
# LLM 架构与优化方法

This section covers the foundational architecture of large language models and the key optimization techniques that make training and inference efficient. Topics are ordered as a curriculum: we begin with the transformer itself, then cover how to train it efficiently, how to adapt it cheaply, how to compress it, how to scale it, and how to accelerate its inference.
本节涵盖大型语言模型的基础架构，以及使训练和推理高效的关键优化技术。主题按课程顺序排列：我们从Transformer本身开始，然后介绍如何高效训练、如何低成本适配、如何压缩、如何扩展以及如何加速推理。

## How LLMs Work: An Intuitive Overview
\label{how-llms-work-an-intuitive-overview}
## LLM 工作原理：直观概述

Before diving into architectural details, let us build intuition for how a large language model transforms text into text. The entire process follows a simple pipeline: \textbf{text $\to$ tokens $\to$ representations $\to$ tokens $\to$ text}.
在深入架构细节之前，我们先建立对大型语言模型如何将文本转换为文本的直觉。整个过程遵循一个简单的流水线：\textbf{文本 $\to$ 令牌 $\to$ 表示 $\to$ 令牌 $\to$ 文本}。

\begin{figure}[ht!]
\centering
\begin{tikzpicture}[
  node distance=0.4cm,
  box/.style={draw, rounded corners=3pt, minimum height=0.9cm, minimum width=1.8cm, align=center, font=\small},
  arr/.style={->, thick, >=stealth},
  darr/.style={->, thick, >=stealth, dashed}
]
% Nodes
\node[box, fill=gray!15] (text) {Raw\\Text};
\node[box, fill=blue!12, right=of text] (tok) {Tokenizer};
\node[box, fill=green!12, right=of tok] (ids) {Token\\IDs};
\node[box, fill=orange!12, right=of ids] (emb) {Embedding\\Layer};
\node[box, fill=red!10, right=of emb] (tf) {Transformer\\Layers ($\times L$)};
\node[box, fill=purple!10, right=of tf] (logits) {Vocab\\Logits};
\node[box, fill=cyan!12, right=of logits] (dec) {Decode};
\node[box, fill=gray!15, right=of dec] (out) {Output\\Text};

% Forward arrows
\draw[arr] (text) -- (tok);
\draw[arr] (tok) -- (ids);
\draw[arr] (ids) -- (emb);
\draw[arr] (emb) -- (tf);
\draw[arr] (tf) -- (logits);
\draw[arr] (logits) -- (dec);
\draw[arr] (dec) -- (out);

% Autoregressive loop
\draw[darr, rounded corners=6pt] (out.south) -- ++(0,-0.7) -| node[below, pos=0.25, font=\scriptsize\itshape] {autoregressive loop (append token to input)} (text.south);
\end{tikzpicture}
\caption{LLM 流水线：文本被分词为子词单元，转换为整数 ID，嵌入为稠密向量，经过 Transformer 层处理，投影到词汇表 logits，并解码回文本。虚线循环表示自回归生成——每个输出令牌被追加到输入中用于下一次前向传播。}
\label{fig:llm-pipeline}
\end{figure}

\begin{keybox}[四个关键阶段]
\begin{enumerate}
  \item \textbf{Tokenization (分词)}: Raw text is split into subword pieces (not characters, not full words) using a learned vocabulary. ``unhappiness'' might become [``un'', ``happiness''] or [``unhapp'', ``iness''].
  \item \textbf{分词}: 原始文本使用学习得到的词汇表分割成子词片段（不是字符，也不是完整单词）。“unhappiness”可能变成 [“un”, “happiness”] 或 [“unhapp”, “iness”]。
  \item \textbf{Embedding (嵌入)}: Each token ID indexes into a learned embedding table, producing a dense vector in $\mathbb{R}^d$ (typically $d = 4096$). These vectors capture semantic meaning---similar words get similar vectors.
  \item \textbf{嵌入}: 每个令牌 ID 索引到一个学习得到的嵌入表中，生成一个 $\mathbb{R}^d$ 中的稠密向量（通常 $d = 4096$）。这些向量捕获语义含义——相似单词得到相似向量。
  \item \textbf{Contextual Processing (上下文处理)}: The transformer stack processes all embeddings in parallel, using self-attention to let each position ``read'' from all other positions. After $L$ layers, each position’s hidden state encodes rich contextual information.
  \item \textbf{上下文处理}: Transformer 堆栈并行处理所有嵌入，使用自注意力让每个位置从所有其他位置“读取”。经过 $L$ 层后，每个位置的隐藏状态编码了丰富的上下文信息。
  \item \textbf{Prediction (预测)}: The final hidden state is projected to a probability distribution over the full vocabulary, and a decoding strategy selects the next token.
  \item \textbf{预测}: 最终的隐藏状态被投影到整个词汇表上的概率分布，解码策略选择下一个令牌。
\end{enumerate}
\end{keybox}

\section{Tokenization}
\label{sec:tokenization}
## 分词

Tokenization is the critical first step that converts raw text into the discrete symbols a language model operates on. The choice of tokenizer directly affects model quality, multilingual capability, and computational efficiency.
分词是将原始文本转换为语言模型操作的离散符号的关键第一步。分词器的选择直接影响模型质量、多语言能力和计算效率。

\begin{intuitionbox}[为什么用子词？]
Character-level models need very long sequences (expensive attention). Word-level models cannot handle rare or novel words. Subword tokenization strikes the ideal balance: common words are single tokens (``the'' $\to$ [the]), rare words decompose into known pieces (``cryptocurrency'' $\to$ [``crypt'', ``ocur'', ``rency'']), and the vocabulary stays manageable (32K--128K tokens).
字符级模型需要非常长的序列（注意力计算昂贵）。词级模型无法处理罕见或新词。子词分词达到了理想的平衡：常见词是单个令牌（“the” $\to$ [the]），罕见词分解为已知片段（“cryptocurrency” $\to$ [“crypt”, “ocur”, “rency”]），词汇表保持可管理（32K--128K 令牌）。
\end{intuitionbox}

\subsection{Why Not Characters or Words?}
\label{why-not-characters-or-words}
### 为什么不用字符或单词？

\begin{table}[ht!]
\centering
\caption{不同分词粒度的权衡。}
\begin{tabular}{@{}llll@{}}
\toprule
\textbf{粒度} & \textbf{词汇表大小} & \textbf{序列长度} & \textbf{问题} \\
\midrule
字符 & $\sim$256 & 非常长 & 注意力代价 $O(n^2)$；难以学习长程语义 \\
单词 & $\sim$500K+ & 短 & 无法处理罕见/新词；嵌入表巨大 \\
子词 & 32K--128K & 中等 & 最佳权衡：序列短，开放词汇 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Byte-Pair Encoding (BPE)}
\label{byte-pair-encoding-bpe}
### 字节对编码（BPE）

BPE~\cite{sennrich2016bpe} is the dominant tokenization algorithm used by GPT, Llama, Mistral, and most modern LLMs.
BPE~\cite{sennrich2016bpe} 是 GPT、Llama、Mistral 及大多数现代 LLM 使用的主要分词算法。

\begin{keybox}[BPE 算法]
\begin{enumerate}
  \item Start with a vocabulary of individual characters (bytes)
  \item 从单个字符（字节）的词汇表开始
  \item Count all adjacent symbol pairs in the training corpus
  \item 统计训练语料中所有相邻符号对
  \item Merge the most frequent pair into a new symbol
  \item 将最频繁的对合并为一个新符号
  \item Repeat steps 2--3 for $k$ iterations (until desired vocabulary size)
  \item 重复步骤 2--3 共 $k$ 次迭代（直到达到所需词汇表大小）
\end{enumerate}
\end{keybox}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.65\textwidth]{figures/fig_003_fig3.png}
\caption{BPE 分词示例：从字符开始，算法迭代合并最频繁的相邻对，直到单词变成单个令牌或词汇表预算耗尽。}
\end{figure}

\newpage
\subsection{Other Tokenization Methods}
\label{other-tokenization-methods}
### 其他分词方法

\begin{table}[ht!]
\centering
\caption{子词分词算法比较。}
\begin{tabular}{@{}lp{4cm}p{7cm}@{}}
\toprule
\textbf{方法} & \textbf{使用者} & \textbf{核心思想} \\
\midrule
BPE & GPT-4~\cite{openai2023gpt4}, Llama-3~\cite{grattafiori2024llama3}, Mistral~\cite{jiang2023mistral} & 自底向上合并频繁对；确定性 \\
WordPiece & BERT~\cite{devlin2019bert}, DistilBERT~\cite{sanh2019distilbert} & 类似 BPE，但最大化训练数据似然 \\
Unigram LM & SentencePiece (T5~\cite{raffel2020t5}, XLNet~\cite{yang2019xlnet}) & 自顶向下：从大词汇表开始，按似然影响剪枝 \\
Byte-level BPE & GPT-2~\cite{radford2019gpt2}+ & 对原始字节进行 BPE（不产生未知令牌）；256 个基础词汇 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Tokenization Best Practices}
\label{tokenization-best-practices}
### 分词最佳实践

\begin{enumerate}
  \item \textbf{Vocabulary size matters}: 32K is minimal; 128K enables better multilingual coverage and code handling. Llama-3 uses 128K tokens.
  \item \textbf{词汇表大小很重要}: 32K 是最低要求；128K 能更好地支持多语言覆盖和代码处理。Llama-3 使用 128K 令牌。
  \item \textbf{Special tokens}: Always include \texttt{<bos>}, \texttt{<eos>}, \texttt{<pad>}, \texttt{<unk>}. For instruction-tuned models, add role markers (\texttt{<|user|>}, \texttt{<|assistant|>}).
  \item \textbf{特殊令牌}: 始终包含 \texttt{<bos>}, \texttt{<eos>}, \texttt{<pad>}, \texttt{<unk>}。对于指令微调模型，添加角色标记（\texttt{<|user|>}, \texttt{<|assistant|>}）。
  \item \textbf{Fertility}: Measure tokens-per-word across languages. High fertility (many tokens per word) indicates poor coverage for that language.
  \item \textbf{生育率}: 测量跨语言的每词令牌数。高生育率（每词很多令牌）表明该语言覆盖较差。
  \item \textbf{Never tokenize across boundaries}: Spaces, punctuation, and digits should be handled consistently. Most modern tokenizers prepend a space marker (``the'') to distinguish word-initial vs.~continuation tokens.
  \item \textbf{绝不跨边界分词}: 空格、标点和数字应一致处理。大多数现代分词器会添加空格标记（“the”）以区分词首与后续令牌。
  \item \textbf{Numbers}: Consider digit-level tokenization for arithmetic tasks. ``2024'' as [``2'',``0'',``2'',``4''] enables digit-by-digit reasoning.
  \item \textbf{数字}: 对于算术任务考虑使用数字级分词。“2024” 作为 [“2”,“0”,“2”,“4”] 支持逐位推理。
  \item \textbf{Code}: Ensure whitespace (indentation) is tokenized efficiently. Llama-3 tokenizes runs of spaces as single tokens.
  \item \textbf{代码}: 确保空白（缩进）被高效分词。Llama-3 将连续空格视为单个令牌。
\end{enumerate}

\subsection{Tokenization in Practice: HuggingFace Example}
\label{tokenization-in-practice-huggingface-example}
### 分词实践：HuggingFace 示例

The \texttt{transformers} library provides a unified interface for all tokenizers. The following demonstrates encoding and decoding with a modern LLM tokenizer:
\texttt{transformers} 库为所有分词器提供了统一接口。以下演示使用现代 LLM 分词器进行编码和解码：

\begin{lstlisting}[style=pythonstyle, caption={使用 HuggingFace Transformers 进行分词编码/解码。}]
from transformers import AutoTokenizer

# 加载分词器（此处使用 GPT-2 为例）
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# 编码：文本 -> 令牌 ID
text = "Hello, how are you?"
encoded = tokenizer.encode(text)
print("Encoded:", encoded)  # 输出 ID 列表

# 解码：令牌 ID -> 文本
decoded = tokenizer.decode(encoded)
print("Decoded:", decoded)  # 还原为原始文本
\end{lstlisting}

```markdown
\begin{lstlisting}[style=pythonstyle, caption={Tokenization example with Llama-3 tokenizer (byte-level BPE).}]
# Load Llama-3 tokenizer (128K vocabulary, byte-level BPE)
# 加载 Llama-3 分词器（128K 词表，字节级 BPE）
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")

text = "Reinforcement learning optimizes long-term rewards."


# Encode: text -> token IDs
# 编码：文本 -> 令牌 ID
token_ids = tokenizer.encode(text)
print(token_ids)
# [128000, 29934, 262, 11008, 4815, 6900, 1317, 9860, 21845, 13]


# Decode individual tokens to see subword splits
# 解码单个令牌以查看子词拆分
tokens = tokenizer.convert_ids_to_tokens(token_ids)
print(tokens)
# ['<|begin_of_text|>', 'Re', 'inforce', 'ment', ' learning',
#  ' optimizes', ' long', '-term', ' rewards', '.']


# Decode back to text (round-trip)
# 解码回文本（往返验证）
reconstructed = tokenizer.decode(token_ids, skip_special_tokens=True)
assert reconstructed == text  # Perfect reconstruction
# 完美重建


# Tokenize with attention mask (for batched inputs with padding)
# 使用注意力掩码进行分词（用于带填充的批处理输入）
batch = tokenizer(
    ["Short text.", "A much longer input sentence for comparison."],
    padding=True, return_tensors="pt"
)
print(batch.keys())  # dict_keys(['input_ids', 'attention_mask'])
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={使用 Llama-3 分词器（字节级 BPE）的分词示例。}]
# 加载 Llama-3 分词器（128K 词表，字节级 BPE）
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")

text = "Reinforcement learning optimizes long-term rewards."
text = "强化学习优化长期奖励。"

# 编码：文本 -> 令牌 ID
token_ids = tokenizer.encode(text)
print(token_ids)
# [128000, 29934, 262, 11008, 4815, 6900, 1317, 9860, 21845, 13]

# 解码单个令牌以查看子词拆分
tokens = tokenizer.convert_ids_to_tokens(token_ids)
print(tokens)
# ['<|begin_of_text|>', 'Re', 'inforce', 'ment', ' learning',
#  ' optimizes', ' long', '-term', ' rewards', '.']

# 解码回文本（往返验证）
reconstructed = tokenizer.decode(token_ids, skip_special_tokens=True)
assert reconstructed == text  # 完美重建

# 使用注意力掩码进行分词（用于带填充的批处理输入）
batch = tokenizer(
    ["Short text.", "A much longer input sentence for comparison."],
    padding=True, return_tensors="pt"
)
print(batch.keys())  # dict_keys(['input_ids', 'attention_mask'])
\end{lstlisting}

## Special Tokens and Structured Prompts
## 特殊令牌（Special Tokens）与结构化提示

Special tokens are reserved vocabulary entries that carry structural meaning rather than linguistic content. They are critical for controlling model behavior.

特殊令牌（Special Tokens）是保留的词汇表条目，它们携带结构意义而非语言内容。它们对于控制模型行为至关重要。

\begin{table}[ht!]
\centering
\caption{Common special tokens across LLM families.}
\begin{tabular}{@{}lll@{}}
\toprule
\textbf{Token} & \textbf{Alias} & \textbf{Purpose} \\
\midrule
\texttt{<bos>} / \texttt{<|begin\_of\_text|>} & BOS & Marks start of sequence \\
\texttt{<eos>} / \texttt{<|end\_of\_text|>} & EOS & Marks end of sequence; stops generation \\
\texttt{<|user|>} & --- & Marks start of user turn in chat \\
\texttt{<|assistant|>} & --- & Marks start of assistant turn in chat \\
\texttt{<pad>} & PAD & Fills batch to uniform length; masked in attention \\
\texttt{<unk>} & UNK & Out-of-vocabulary placeholder (rare with BPE) \\
\texttt{[SEP]} & SEP & Separates segments (BERT-style) \\
\texttt{[CLS]} & CLS & Classification token (BERT) \\
\texttt{[MASK]} & MASK & Masked token for MLM pretraining \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[ht!]
\centering
\caption{各 LLM 系列中常见的特殊令牌。}
\begin{tabular}{@{}lll@{}}
\toprule
\textbf{令牌} & \textbf{别名} & \textbf{用途} \\
\midrule
\texttt{<bos>} / \texttt{<|begin\_of\_text|>} & BOS & 标记序列开始 \\
\texttt{<eos>} / \texttt{<|end\_of\_text|>} & EOS & 标记序列结束；停止生成 \\
\texttt{<|user|>} & --- & 标记对话中用户轮次的开始 \\
\texttt{<|assistant|>} & --- & 标记对话中助手轮次的开始 \\
\texttt{<pad>} & PAD & 将批次填充到统一长度；在注意力中屏蔽 \\
\texttt{<unk>} & UNK & 词表外占位符（在 BPE 中很少见） \\
\texttt{[SEP]} & SEP & 分隔片段（BERT 风格） \\
\texttt{[CLS]} & CLS & 分类令牌（BERT） \\
\texttt{[MASK]} & MASK & 用于 MLM 预训练的掩码令牌 \\
\bottomrule
\end{tabular}
\end{table}

\paragraph{Role Markers for Instruction-Tuned Models.}
\label{role-markers-for-instruction-tuned-models.}

**Role Markers for Instruction-Tuned Models.**
\label{role-markers-for-instruction-tuned-models.}

Modern chat models use special tokens to delineate conversational structure. These are \textbf{not} trained to carry semantic meaning---they are structural delimiters that the model learns to parse:

现代聊天模型使用特殊令牌来划定对话结构。这些内容 \textbf{并非} 经过训练以携带语义信息——它们是模型学会解析的结构界定符：

\begin{lstlisting}[style=pythonstyle, caption={Chat template with special tokens (Llama-3 format).}]
# Llama-3 chat template
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain PPO in one sentence."},
]


# apply_chat_template handles all special token insertion
prompt = tokenizer.apply_chat_template(messages, tokenize=False)
print(prompt)
# <|begin_of_text|><|start_header_id|>system<|end_header_id|>
#
# You are a helpful assistant.<|eot_id|><|start_header_id|>user<|end_header_id|>
#
# Explain PPO in one sentence.<|eot_id|><|start_header_id|>assistant<|end_header_id|>
#
#
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={包含特殊令牌的对话模板（Llama-3 格式）。}]
# Llama-3 对话模板
messages = [
    {"role": "system", "content": "你是一个有用的助手。"},
    {"role": "user", "content": "用一句话解释 PPO（近端策略优化）。"},
]

# apply_chat_template 处理所有特殊令牌的插入
prompt = tokenizer.apply_chat_template(messages, tokenize=False)
print(prompt)
# <|begin_of_text|><|start_header_id|>system<|end_header_id|>
#
# 你是一个有用的助手。<|eot_id|><|start_header_id|>user<|end_header_id|>
#
# 用一句话解释 PPO（近端策略优化）。<|eot_id|><|start_header_id|>assistant<|end_header_id|>
#
#
\end{lstlisting}

\begin{keybox}[特殊令牌最佳实践]
\begin{itemize}
  \item \textbf{Never split special tokens}: They must be atomic---ensure your tokenizer treats them as single units, not character sequences.
  \item \textbf{绝不分拆特殊令牌}：它们必须是原子性的——确保你的分词器将它们视为单个单元，而非字符序列。
  \item \textbf{Mask loss on special tokens}: During SFT, do not compute loss on structural tokens (role markers, separators). The model should not ``learn'' to predict formatting.
  \item \textbf{在特殊令牌上掩码损失}：在 SFT（监督微调）期间，不对结构令牌（角色标记、分隔符）计算损失。模型不应“学习”预测格式。
  \item \textbf{Use templates for structure}: Encode task semantics via special tokens rather than natural language instructions. E.g., \texttt{<|tool\_call|>} is more reliable than ``Now I will call a tool:''.
  \item \textbf{使用模板进行结构化}：通过特殊令牌而非自然语言指令编码任务语义。例如，\texttt{<|tool\_call|>} 比“现在我将调用一个工具：”更可靠。
  \item \textbf{Tool/function calling}: Define dedicated tokens like \texttt{<|function|>}, \texttt{<|result|>} to create unambiguous boundaries between reasoning and action.
  \item \textbf{工具/函数调用}：定义专用令牌，如 \texttt{<|function|>}、\texttt{<|result|>}，以在推理和动作之间创建无歧义的边界。
  \item \textbf{Consistent handling in RL}: During PPO/GRPO, ensure the reference model and policy model use identical tokenization and special token handling---mismatches corrupt KL computation.
  \item \textbf{在强化学习（RL）中一致处理}：在 PPO/GRPO 期间，确保参考模型和策略模型使用相同的分词和特殊令牌处理——不匹配会破坏 KL 计算。
  \item \textbf{EOS handling}: During generation, ensure EOS is included in the action space. If the model cannot emit EOS, responses grow unbounded (common RL failure mode).
  \item \textbf{EOS 处理}：在生成期间，确保 EOS 包含在动作空间中。如果模型无法输出 EOS，响应将无限增长（常见的 RL 失败模式）。
\end{itemize}
\end{keybox}

# The Transformer Architecture
# 变压器架构（The Transformer Architecture）

The Transformer~\cite{vaswani2017attention} is the foundation of all modern LLMs. Understanding its components is essential for grasping every optimization and training method in this guide.

Transformer~\cite{vaswani2017attention} 是所有现代 LLM 的基础。理解其组件对于掌握本指南中的每种优化和训练方法至关重要。

## High-Level Structure
## 高层结构

A decoder-only transformer processes tokens sequentially through embedding, repeated attention+FFN blocks, and a final projection to vocabulary logits. Figure~\ref{fig:decoder-only} shows the complete architecture.

仅解码器（Decoder-only）变压器通过嵌入、重复的注意力+FFN（前馈网络）块，以及最终投影到词汇表 logits，按顺序处理令牌。图~\ref{fig:decoder-only} 展示了完整架构。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.55\textwidth]{figures/fig_004_decoder-only.png}
\caption{Decoder-only Transformer block (GPT-style, Pre-Norm variant). Each sub-layer (attention, FFN) is preceded by LayerNorm and followed by a residual addition: $\mathbf{x} + \text{SubLayer}(\text{LN}(\mathbf{x}))$. This Pre-Norm ordering (used by Llama, GPT-3, Mistral) stabilizes training without warmup, unlike the original Post-Norm (which applies LayerNorm after the addition). $L$ identical blocks are stacked, followed by a final LayerNorm and linear projection to vocabulary logits.}
\label{fig:decoder-only}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.55\textwidth]{figures/fig_004_decoder-only.png}
\caption{仅解码器 Transformer 块（GPT 风格，Pre-Norm 变体）。每个子层（注意力、FFN）之前有 LayerNorm，之后有残差相加：$\mathbf{x} + \text{SubLayer}(\text{LN}(\mathbf{x}))$。这种 Pre-Norm 排序（由 Llama、GPT-3、Mistral 使用）无需预热即可稳定训练，与原始的 Post-Norm（在相加后应用 LayerNorm）不同。$L$ 个相同的块堆叠在一起，之后是最终的 LayerNorm 和线性投影到词汇表 logits。}
\label{fig:decoder-only}
\end{figure}

## The Original Encoder-Decoder Transformer
## 原始编码器-解码器 Transformer

The Transformer was originally introduced~\cite{vaswani2017attention} as an \textbf{encoder-decoder} architecture for sequence-to-sequence tasks (machine translation, summarization). While modern LLMs predominantly use decoder-only variants (GPT-style), understanding the full architecture is essential because cross-attention and masked self-attention --- both originating here --- remain fundamental building blocks.

Transformer 最初被引入~\cite{vaswani2017attention} 作为用于序列到序列任务（机器翻译、摘要）的 \textbf{编码器-解码器} 架构。虽然现代 LLM 主要使用仅解码器变体（GPT 风格），但理解完整架构至关重要，因为交叉注意力和掩码自注意力——两者都源于此处——仍然是基本构建块。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_005_transformer-original.png}
\caption{The original Transformer architecture (Vaswani et al., 2017). The encoder (left) processes the full input with bidirectional self-attention. The decoder (right) generates tokens autoregressively using masked self-attention and cross-attention to encoder representations. Dashed boxes indicate the repeated layer block ($\times N$); gray lines show residual connections bypassing each sub-layer. Note: the original work uses \textbf{Post-Norm} (LayerNorm applied \emph{after} the residual addition: $\text{LN}(\mathbf{x} + \text{SubLayer}(\mathbf{x}))$), unlike modern LLMs which use Pre-Norm.}
\label{fig:transformer-original}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_005_transformer-original.png}
\caption{原始 Transformer 架构（Vaswani 等人，2017）。编码器（左侧）使用双向自注意力处理完整输入。解码器（右侧）使用掩码自注意力和对编码器表示的交叉注意力自回归生成令牌。虚线框表示重复的层块（$\times N$）；灰色线表示绕过每个子层的残差连接。注意：原始工作使用 \textbf{Post-Norm}（LayerNorm 应用在残差相加 \emph{之后}：$\text{LN}(\mathbf{x} + \text{SubLayer}(\mathbf{x}))$），这与现代 LLM 使用的 Pre-Norm 不同。}
\label{fig:transformer-original}
\end{figure}

\paragraph{Encoder.}
\label{encoder.}

**Encoder.**
\label{encoder.}

The encoder processes the entire input sequence \emph{bidirectionally} --- each token attends to all other tokens (no causal mask). This produces a rich contextual representation $\mathbf{H}^{\text{enc}} \in \mathbb{R}^{n \times d}$ where each position encodes information about the full input:

编码器 \emph{双向地} 处理整个输入序列——每个令牌关注所有其他令牌（无因果掩码）。这产生了一个丰富的上下文表示 $\mathbf{H}^{\text{enc}} \in \mathbb{R}^{n \times d}$，其中每个位置编码了整个输入的信息：

\begin{itemize}
  \item \textbf{Input}: Token embeddings + sinusoidal positional encodings
  \item \textbf{输入}：令牌嵌入 + 正弦位置编码
  \item \textbf{Each layer}: Multi-Head Self-Attention $\to$ Add \& Norm $\to$ FFN $\to$ Add \& Norm
  \item \textbf{每个层}：多头自注意力 $\to$ 相加与归一化 $\to$ FFN $\to$ 相加与归一化
  \item \textbf{No causal mask}: Position $i$ attends to all positions $1, \ldots, n$
  \item \textbf{无因果掩码}：位置 $i$ 关注所有位置 $1, \ldots, n$
  \item \textbf{Output}: Contextual representations of the full input sequence
  \item \textbf{输出}：完整输入序列的上下文表示
\end{itemize}

\paragraph{Decoder --- Masked Multi-Head Self-Attention.}
\label{decoder-masked-multi-head-self-attention.}

**Decoder — Masked Multi-Head Self-Attention.**
\label{decoder-masked-multi-head-self-attention.}

The decoder generates output tokens one at a time (autoregressively). To prevent the model from ``seeing the future,'' the self-attention in the decoder uses a \textbf{causal mask}:

解码器一次生成一个输出令牌（自回归）。为了防止模型“看到未来”，解码器中的自注意力使用了一个 \textbf{因果掩码}：

\begin{equation}
  \text{MaskedAttn}(Q, K, V) = \text{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}} + M\right) V
\end{equation}

\begin{equation}
  \text{掩码注意力}(Q, K, V) = \text{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}} + M\right) V
\end{equation}
```

## where the mask $M$ is: 
## 其中掩码 $M$ 定义为：

\[
M_{ij} = \begin{cases} 0 & \text{if } i \geq j \text{ (can attend)} \\ -\infty & \text{if } i < j \text{ (future token --- blocked)} \end{cases}
\]

\begin{intuitionbox}[Why Masking Matters]
During training, the decoder processes the entire target sequence in parallel (teacher forcing), but each position must only attend to previous positions to maintain the autoregressive property. The mask ensures that generating token $t$ uses only information from tokens $1, \ldots, t{-}1$. At inference, tokens are generated one-by-one so the mask is implicit --- but during training it enables parallel computation while preserving causality.
\end{intuitionbox}

\begin{intuitionbox}[为什么掩码很重要]
在训练过程中，解码器并行处理整个目标序列（教师强制），但每个位置必须只关注前面的位置，以保持自回归特性。掩码确保生成 token $t$ 时只使用来自 token $1, \ldots, t{-}1$ 的信息。推理时，token 是逐个生成的，因此掩码是隐式的——但在训练时，它可以在保持因果性的同时实现并行计算。
\end{intuitionbox}

\paragraph{Decoder --- Cross-Attention.}
\label{decoder-cross-attention.}

\paragraph{解码器——交叉注意力}
\label{decoder-cross-attention.}

After masked self-attention, each decoder layer applies \textbf{cross-attention} where the decoder attends to the encoder's output representations. This is the mechanism by which the decoder ``reads'' the input:

在掩码自注意力之后，每个解码器层应用\textbf{交叉注意力}，其中解码器关注编码器的输出表示。这是解码器“读取”输入的机制：

\begin{equation}
  \text{CrossAttn}(Q_{\text{dec}}, K_{\text{enc}}, V_{\text{enc}}) = \text{softmax}\!\left(\frac{Q_{\text{dec}} K_{\text{enc}}^T}{\sqrt{d_k}}\right) V_{\text{enc}}
\end{equation}

\begin{itemize}
  \item \textbf{Queries} come from the decoder's previous sublayer (the masked self-attention output)
  \item \textbf{Keys and Values} come from the encoder's final output $\mathbf{H}^{\text{enc}}$
  \item \textbf{No mask} is applied --- every decoder position can attend to every encoder position
  \item This allows the decoder to dynamically focus on different parts of the input at each generation step (e.g., attending to ``cat'' when translating to ``gato'' in English$\to$Spanish)
\end{itemize}

\begin{itemize}
  \item \textbf{查询} 来自解码器上一个子层（掩码自注意力输出）
  \item \textbf{键和值} 来自编码器的最终输出 $\mathbf{H}^{\text{enc}}$
  \item 不应用\textbf{掩码} —— 每个解码器位置都可以关注每个编码器位置
  \item 这使得解码器能够在每个生成步骤动态关注输入的不同部分（例如，在英译西时关注“cat”以翻译成“gato”）
\end{itemize}

\paragraph{Full Decoder Layer.}
\label{full-decoder-layer.}

\paragraph{完整的解码器层}
\label{full-decoder-layer.}

Each decoder layer contains three sublayers (vs.~two in the encoder):

每个解码器层包含三个子层（而编码器有两个）：

\begin{enumerate}
  \item \textbf{Masked Multi-Head Self-Attention} + Residual + LayerNorm
  \item \textbf{Multi-Head Cross-Attention} (to encoder output) + Residual + LayerNorm
  \item \textbf{Feed-Forward Network} + Residual + LayerNorm
\end{enumerate}

\begin{enumerate}
  \item \textbf{掩码多头自注意力} + 残差 + 层归一化
  \item \textbf{多头交叉注意力}（针对编码器输出） + 残差 + 层归一化
  \item \textbf{前馈网络} + 残差 + 层归一化
\end{enumerate}

\paragraph{From Encoder-Decoder to Decoder-Only.}
\label{from-encoder-decoder-to-decoder-only.}

\paragraph{从编码器-解码器到仅解码器}
\label{from-encoder-decoder-to-decoder-only.}

Modern LLMs (GPT, Llama, Qwen) use only the decoder, removing both the encoder and cross-attention layers entirely. The key insight: for generative language modeling, a single causal (masked) self-attention stack is sufficient --- the model learns to encode context and generate continuations in a single pass. This simplifies architecture, training, and inference while scaling more effectively. Encoder-decoder models (T5, BART) remain relevant for tasks with distinct input/output structure (translation, summarization), and cross-attention reappears in multimodal models where vision encoders provide keys/values to language decoders.

现代大语言模型（GPT、Llama、Qwen）仅使用解码器，完全去除了编码器和交叉注意力层。关键洞察：对于生成式语言建模，单个因果（掩码）自注意力堆栈就足够了——模型可以在单次前向传播中学习编码上下文并生成后续内容。这简化了架构、训练和推理，同时扩展性更好。编码器-解码器模型（T5、BART）在具有明确输入/输出结构的任务（翻译、摘要）中仍然有用，而交叉注意力在多模态模型中重新出现，其中视觉编码器为语言解码器提供键和值。

\subsection{Decoder-Only vs Encoder-Decoder}
\label{decoder-only-vs-encoder-decoder}

\subsection{仅解码器 vs 编码器-解码器}
\label{decoder-only-vs-encoder-decoder}

Modern LLMs almost exclusively use decoder-only architectures, but understanding the trade-offs with encoder-decoder designs clarifies why.

现代大语言模型几乎全部使用仅解码器架构，但理解与编码器-解码器设计的权衡有助于说明原因。

\begin{tabular}{@{}lp{5cm}p{6.5cm}@{}}
\toprule
\textbf{Architecture} & \textbf{Examples} & \textbf{Use Case} \\
\midrule
Decoder-only & GPT-4~\cite{openai2023gpt4}, Llama~\cite{grattafiori2024llama3}, Mistral~\cite{jiang2023mistral}, Qwen~\cite{qwen2024qwen25} & Autoregressive generation; dominant for chat/reasoning \\
Encoder-decoder & T5~\cite{raffel2020t5}, BART~\cite{lewis2020bart}, Flan-T5~\cite{chung2022flan} & Seq2seq (translation, summarization); less common now \\
Encoder-only & BERT~\cite{devlin2019bert}, RoBERTa~\cite{liu2019roberta} & Classification/embeddings; not for generation \\
\bottomrule
\end{tabular}

\begin{tabular}{@{}lp{5cm}p{6.5cm}@{}}
\toprule
\textbf{架构} & \textbf{示例} & \textbf{使用场景} \\
\midrule
仅解码器 & GPT-4~\cite{openai2023gpt4}, Llama~\cite{grattafiori2024llama3}, Mistral~\cite{jiang2023mistral}, Qwen~\cite{qwen2024qwen25} & 自回归生成；在聊天/推理中占主导地位 \\
编码器-解码器 & T5~\cite{raffel2020t5}, BART~\cite{lewis2020bart}, Flan-T5~\cite{chung2022flan} & Seq2seq（翻译、摘要）；现在较少使用 \\
仅编码器 & BERT~\cite{devlin2019bert}, RoBERTa~\cite{liu2019roberta} & 分类/嵌入；不用于生成 \\
\bottomrule
\end{tabular}

\begin{warningbox}[Why Decoder-Only Won]
Decoder-only models are simpler (one model, one loss), scale better (all parameters contribute to generation), and support unified training (pretraining = next-token prediction = fine-tuning objective). Encoder-decoder models waste capacity on the encoder for pure generation tasks.
\end{warningbox}

\begin{warningbox}[为什么仅解码器胜出]
仅解码器模型更简单（一个模型、一个损失），扩展性更好（所有参数都贡献给生成），并且支持统一训练（预训练 = 下一个 token 预测 = 微调目标）。编码器-解码器模型在纯生成任务上浪费了编码器的容量。
\end{warningbox}

\subsection{Embeddings: From Discrete Tokens to Continuous Space}
\label{embeddings-from-discrete-tokens-to-continuous-space}

\subsection{嵌入：从离散 token 到连续空间}
\label{embeddings-from-discrete-tokens-to-continuous-space}

Before any attention or computation happens, the transformer must convert discrete token IDs into continuous vectors that neural networks can process. This is the role of the \textbf{embedding layer}.

在任何注意力或计算发生之前，Transformer 必须将离散的 token ID 转换为神经网络可以处理的连续向量。这就是\textbf{嵌入层}的作用。

\paragraph{What is an Embedding?}
\label{what-is-an-embedding}

\paragraph{什么是嵌入？}
\label{what-is-an-embedding}

An embedding is a learned dense vector representation of a discrete symbol. Instead of representing the word ``king'' as a one-hot vector of size $|\mathcal{V}| = 128{,}000$ (mostly zeros), we represent it as a compact vector in $\mathbb{R}^d$ (e.g., $d = 4096$) that captures its \emph{meaning}.

嵌入是对离散符号学习到的稠密向量表示。我们不将单词“king”表示为大小为 $|\mathcal{V}| = 128{,}000$ 的 one-hot 向量（大部分为零），而是将其表示为 $\mathbb{R}^d$（例如 $d = 4096$）中的紧凑向量，该向量捕捉其\emph{含义}。

The key insight: \textbf{similar concepts get nearby vectors}. In a well-trained embedding space:

关键洞察：\textbf{相似的概念获得相邻的向量}。在训练良好的嵌入空间中：

\begin{itemize}
  \item ``king'' and ``queen'' are close (both royalty)
  \item ``king'' and ``bicycle'' are far apart (unrelated)
  \item Vector arithmetic captures relationships: $\vec{\text{king}} - \vec{\text{man}} + \vec{\text{woman}} \approx \vec{\text{queen}}$
\end{itemize}

\begin{itemize}
  \item ``king'' 和 ``queen'' 很近（都是王室成员）
  \item ``king'' 和 ``bicycle'' 很远（不相关）
  \item 向量算术捕捉关系：$\vec{\text{king}} - \vec{\text{man}} + \vec{\text{woman}} \approx \vec{\text{queen}}$
\end{itemize}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_006_fig6.png}
\caption{Embedding space visualization (2D projection): semantically similar words cluster together. The embedding table learns these positions during pretraining, capturing meaning purely from co-occurrence patterns in text.}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_006_fig6.png}
\caption{嵌入空间可视化（二维投影）：语义相似的词汇聚集在一起。嵌入表在预训练期间学习这些位置，纯粹从文本中的共现模式捕捉含义。}
\end{figure}

\paragraph{The Embedding Table.}
\label{the-embedding-table.}

\paragraph{嵌入表}
\label{the-embedding-table.}

In practice, the embedding layer is simply a matrix $\mathbf{E} \in \mathbb{R}^{|\mathcal{V}| \times d}$ where row $i$ stores the embedding vector for token $i$:

在实践中，嵌入层只是一个矩阵 $\mathbf{E} \in \mathbb{R}^{|\mathcal{V}| \times d}$，其中第 $i$ 行存储 token $i$ 的嵌入向量：

\begin{equation}
\text{embed}(x_t) = \mathbf{E}[x_t] \in \mathbb{R}^d
\end{equation}

For a sequence of token IDs $[x_1, x_2, \ldots, x_n]$, embedding is a simple table lookup (indexing operation): 
\[
\mathbf{H}_0 = [\mathbf{E}[x_1];\; \mathbf{E}[x_2];\; \ldots;\; \mathbf{E}[x_n]] \in \mathbb{R}^{n \times d}
\]

对于 token ID 序列 $[x_1, x_2, \ldots, x_n]$，嵌入是一个简单的表查找（索引操作）：
\[
\mathbf{H}_0 = [\mathbf{E}[x_1];\; \mathbf{E}[x_2];\; \ldots;\; \mathbf{E}[x_n]] \in \mathbb{R}^{n \times d}
\]

\begin{keybox}[Embedding Table in Transformers]
\begin{itemize}
  \item \textbf{Size}: $|\mathcal{V}| \times d$. For Llama-3: $128{,}256 \times 4{,}096 = 525$M parameters (6.5\% of 8B model).
  \item \textbf{Initialization}: Random (Xavier/normal), then learned via backpropagation.
  \item \textbf{Weight tying}: Many models \emph{share} the embedding matrix with the output projection head: $W_{\text{head}} = \mathbf{E}^T$. This saves parameters and creates a symmetric encode-decode structure.
  \item \textbf{Input}: Token ID (integer) $\to$ \textbf{Output}: Dense vector in $\mathbb{R}^d$.
  \item \textbf{Gradient flow}: During training, only the rows corresponding to tokens in the current batch receive gradient updates (sparse update).
\end{itemize}
\end{keybox}

\begin{keybox}[Transformer 中的嵌入表]
\begin{itemize}
  \item \textbf{大小}：$|\mathcal{V}| \times d$。对于 Llama-3：$128{,}256 \times 4{,}096 = 525$M 参数（占 8B 模型的 6.5%）。
  \item \textbf{初始化}：随机（Xavier/正态分布），然后通过反向传播学习。
  \item \textbf{权重绑定}：许多模型将嵌入矩阵与输出投影头\emph{共享}：$W_{\text{head}} = \mathbf{E}^T$。这节省了参数，并创建了对称的编码-解码结构。
  \item \textbf{输入}：token ID（整数）$\to$ \textbf{输出}：$\mathbb{R}^d$ 中的稠密向量。
  \item \textbf{梯度流}：训练期间，只有当前批次中 token 对应的行接收梯度更新（稀疏更新）。
\end{itemize}
\end{keybox}

\begin{intuitionbox}[Why Embeddings Work]
The embedding table is learned end-to-end with the rest of the model. Because the model is trained to predict the next token, it must learn representations where tokens that appear in similar contexts get similar vectors. This is the distributional hypothesis: ``you shall know a word by the company it keeps''~\cite{firth1957synopsis}. The embedding layer compresses this statistical structure into dense geometry.
\end{intuitionbox}

\begin{intuitionbox}[为什么嵌入有效]
嵌入表与模型的其余部分进行端到端学习。因为模型被训练来预测下一个 token，所以它必须学习这样的表示：出现在相似上下文中的 token 获得相似的向量。这就是分布假说：“词由其所伴随的语境而定”~\cite{firth1957synopsis}。嵌入层将此统计结构压缩为稠密的几何形状。
\end{intuitionbox}

\paragraph{The Anisotropy Problem.}
\label{the-anisotropy-problem.}

\paragraph{各向异性问题}
\label{the-anisotropy-problem.}

A critical issue arises when using pretrained embeddings (e.g., from BERT or GPT-2) for downstream tasks like retrieval (RAG) or bootstrapping recommender systems: the learned representations are highly \textbf{anisotropic}---they occupy a narrow cone in the embedding space rather than being uniformly distributed across all directions~\cite{ethayarajh2019contextual}.

当使用预训练嵌入（例如来自 BERT 或 GPT-2）进行检索（RAG）或引导推荐系统等下游任务时，会出现一个关键问题：学到的表示高度\textbf{各向异性}——它们在嵌入空间中占据一个狭窄的锥体，而不是在所有方向上均匀分布~\cite{ethayarajh2019contextual}。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_007_fig7.png}
\caption{Isotropy vs. anisotropy in embedding spaces. Left: isotropic embeddings spread uniformly, making cosine similarity a reliable measure of semantic relatedness. Right: anisotropic embeddings (as found in BERT) cluster in a narrow cone, causing all pairs to have high cosine similarity regardless of semantic content. Whitening transforms the space to restore isotropy.}
\caption{嵌入空间中的各向同性（Isotropy）与各向异性（Anisotropy）。左图：各向同性嵌入均匀分布，使余弦相似度成为衡量语义相关性的可靠指标。右图：各向异性嵌入（如BERT中）聚集在一个狭窄的锥形区域内，导致所有向量对的余弦相似度都很高，无论语义内容如何。白化（Whitening）通过变换空间来恢复各向同性。}
\end{figure}

\textbf{Why this matters for applications:}
\textbf{这对应用的重要性：}

\begin{itemize}
  \item \textbf{RAG / Retrieval}: If all embeddings have cosine similarity $>0.7$ regardless of content, retrieval rankings become nearly random---the system cannot distinguish relevant from irrelevant passages.
  \item \textbf{RAG / 检索（Retrieval）}：如果所有嵌入的余弦相似度都大于 $0.7$，无论内容如何，检索排名将近乎随机——系统无法区分相关段落与不相关段落。
  \item \textbf{Recommender systems}: Using pretrained LLM embeddings to represent items/users only works if the geometry preserves meaningful similarity structure.
  \item \textbf{推荐系统（Recommender systems）}：使用预训练LLM嵌入来表示物品或用户，仅在几何结构保留了有意义的相似性关系时才能有效工作。
  \item \textbf{Clustering}: Anisotropic embeddings collapse clusters, making it impossible to discover natural groupings.
  \item \textbf{聚类（Clustering）}：各向异性嵌入会使聚类坍塌，导致无法发现自然的分组结构。
\end{itemize}

\paragraph{Resolution: Whitening.}
\paragraph{解决方案：白化（Whitening）。}
\label{resolution-whitening.}

A simple and effective fix is \textbf{whitening}~\cite{su2021whitening}---a linear transformation that makes the embedding distribution isotropic (zero mean, identity covariance):
一个简单而有效的修复方法是 \textbf{白化（whitening）}~\cite{su2021whitening}——这是一种线性变换，使嵌入分布各向同性（零均值，单位协方差）：

\begin{equation}
\tilde{\mathbf{h}} = \mathbf{D}^{-1/2} \mathbf{U}^T (\mathbf{h} - \boldsymbol{\mu})
\end{equation}

where $\boldsymbol{\mu}$ is the mean embedding, and $\mathbf{U}\mathbf{D}\mathbf{U}^T$ is the eigendecomposition of the covariance matrix $\Sigma = \frac{1}{N}\sum_i (\mathbf{h}_i - \boldsymbol{\mu})(\mathbf{h}_i - \boldsymbol{\mu})^T$.
其中 $\boldsymbol{\mu}$ 是平均嵌入，$\mathbf{U}\mathbf{D}\mathbf{U}^T$ 是协方差矩阵 $\Sigma = \frac{1}{N}\sum_i (\mathbf{h}_i - \boldsymbol{\mu})(\mathbf{h}_i - \boldsymbol{\mu})^T$ 的特征分解。

\begin{keybox}[Whitening in Practice]
\begin{keybox}[白化实践]

\begin{itemize}
  \item \textbf{What it does}: Rotates and scales the embedding space so all directions have equal variance (unit covariance).
  \item \textbf{作用}：旋转并缩放嵌入空间，使所有方向具有相等的方差（单位协方差）。
  \item \textbf{Effect}: Cosine similarity becomes meaningful---semantically similar pairs score high, dissimilar pairs score low.
  \item \textbf{效果}：余弦相似度变得有意义——语义相似的向量对得分高，不相似的得分低。
  \item \textbf{Bonus}: Can simultaneously reduce dimensionality by keeping only the top-$k$ eigenvectors (similar to PCA), making retrieval faster.
  \item \textbf{额外好处}：可以同时降低维度，仅保留前 $k$ 个特征向量（类似于PCA），从而加速检索。
  \item \textbf{Cost}: Requires computing the covariance matrix over a representative corpus (one-time, $O(N \cdot d^2)$). The transform itself is a simple matrix multiply at inference.
  \item \textbf{代价}：需要在代表性语料库上计算协方差矩阵（一次性，$O(N \cdot d^2)$）。变换本身在推理时只是一个简单的矩阵乘法。
  \item \textbf{Alternative approaches}: Contrastive fine-tuning (SimCSE), flow-based normalization, or training with isotropy-promoting regularizers.
  \item \textbf{替代方法}：对比微调（SimCSE）、基于流的规范化，或使用促进各向同性的正则化器进行训练。
\end{itemize}
\end{keybox}

\subsection{Self-Attention Mechanism}
\subsection{自注意力机制（Self-Attention Mechanism）}
\label{self-attention-mechanism}

Self-attention is the core operation that allows each token to attend to every other token in the sequence, computing a weighted combination based on relevance.
自注意力是允许每个token关注序列中所有其他token的核心操作，基于相关性计算加权组合。

\begin{keybox}[Scaled Dot-Product Attention]
\begin{keybox}[缩放点积注意力（Scaled Dot-Product Attention）]

Given input sequence $X \in \mathbb{R}^{n \times d}$, we compute: 
给定输入序列 $X \in \mathbb{R}^{n \times d}$，我们计算：
\[
Q = XW_Q, \quad K = XW_K, \quad V = XW_V \quad (W_Q, W_K, W_V \in \mathbb{R}^{d \times d_k})
\]
 
\[
\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}} + M\right) V
\]
 where $M$ is the \textbf{causal mask} (for autoregressive models): $M_{ij} = 0$ if $i \geq j$, else $-\infty$.
其中 $M$ 是 \textbf{因果掩码（causal mask）}（用于自回归模型）：当 $i \geq j$ 时 $M_{ij} = 0$，否则为 $-\infty$。

\textbf{Intuition}: Each token ``attends'' to all previous tokens, computing a weighted average of their values based on query-key similarity.
\textbf{直观理解}：每个token“关注”所有之前的token，基于查询-键相似度计算它们值的加权平均。
\end{keybox}

\paragraph{Computational Complexity.}
\paragraph{计算复杂度（Computational Complexity）。}
\label{computational-complexity.}

The naive attention computation has \textbf{quadratic cost} in sequence length:
朴素注意力计算在序列长度上具有 \textbf{二次代价}：

\begin{itemize}
  \item \textbf{Time}: $O(n^2 \cdot d)$ --- computing $QK^T$ requires $n^2$ dot products, each of dimension $d_k$.
  \item \textbf{时间}：$O(n^2 \cdot d)$ —— 计算 $QK^T$ 需要 $n^2$ 次点积，每个点积维度为 $d_k$。
  \item \textbf{Memory}: $O(n^2)$ --- the full attention matrix must be materialized to apply softmax.
  \item \textbf{内存}：$O(n^2)$ —— 必须实例化完整的注意力矩阵才能应用softmax。
\end{itemize}

For a 128K-token context with $d = 4096$, the attention matrix alone is $128\text{K} \times 128\text{K} = 16.4$ billion entries (64 GB in FP32). This quadratic scaling is the fundamental bottleneck for long-context LLMs.
对于一个128K token的上下文，当 $d = 4096$ 时，仅注意力矩阵就有 $128\text{K} \times 128\text{K} = 164$ 亿个条目（FP32下64 GB）。这种二次缩放是长上下文LLM的根本瓶颈。

\vspace{6pt}
\begin{table}[ht!]
\centering
\caption{Attention cost scaling: why naive implementation is prohibitive for long sequences.}
\caption{注意力成本缩放：为什么朴素实现对于长序列不可行。}
\begin{tabular}{@{}lllll@{}}
\toprule
\textbf{Seq Length} & \textbf{Attention Ops} & \textbf{Matrix Size} & \textbf{Practical Impact} \\
\textbf{序列长度} & \textbf{注意力操作数} & \textbf{矩阵大小} & \textbf{实际影响} \\
\midrule
2K & 4M & 16 MB & Fast; fits in SRAM \\
2K & 4M & 16 MB & 快速；适合SRAM \\
8K & 64M & 256 MB & Manageable with FlashAttention \\
8K & 64M & 256 MB & 使用FlashAttention可管理 \\
32K & 1B & 4 GB & Requires memory-efficient kernels \\
32K & 10亿 & 4 GB & 需要内存高效内核 \\
128K & 16B & 64 GB & Exceeds single GPU HBM \\
128K & 160亿 & 64 GB & 超过单个GPU HBM \\
1M & 1T & 4 TB & Impossible without sub-quadratic methods \\
1M & 1万亿 & 4 TB & 没有次二次方法则不可能 \\
\bottomrule
\end{tabular}
\end{table}

\paragraph{Approaches to Taming Attention Cost.}
\paragraph{驯服注意力成本的方法（Approaches to Taming Attention Cost）。}
\label{approaches-to-taming-attention-cost.}

Several families of solutions address this quadratic bottleneck:
几类解决方案解决了这个二次瓶颈：

\begin{enumerate}
  \item \textbf{Exact attention with IO-awareness (FlashAttention~\cite{dao2022flashattention})}: Does not reduce computational complexity but eliminates the need to materialize the $n \times n$ matrix in HBM by computing attention in tiles that fit in SRAM. Crucially, FlashAttention is \textbf{orthogonal} to the sparse patterns below---it is an execution engine, not an attention pattern. Production systems routinely combine FlashAttention with sliding windows or block-sparse masks, getting both IO efficiency and reduced FLOPs. We cover the algorithm in detail in Section~\ref{flash-attention-algorithm-and-hardware-awareness}.
  \item \textbf{具有IO意识的精确注意力（FlashAttention~\cite{dao2022flashattention}）}：不降低计算复杂度，但通过将注意力计算拆分为适合SRAM的分块，消除了在HBM中实例化 $n \times n$ 矩阵的需要。关键在于，FlashAttention 与下面的稀疏模式是 \textbf{正交} 的——它是一个执行引擎，而不是一种注意力模式。生产系统通常将FlashAttention与滑动窗口或块稀疏掩码结合使用，既获得IO效率又减少FLOPs。我们将在第~\ref{flash-attention-algorithm-and-hardware-awareness} 节详细讨论该算法。
  \item \textbf{Sliding window / local attention}: Each token only attends to the $w$ nearest tokens (e.g., $w = 4096$). Cost becomes $O(n \cdot w)$---linear in $n$. Used by Mistral~\cite{jiang2023mistral} (window $= 4096$) and Longformer~\cite{beltagy2020longformer}. Trades global context for efficiency; works well because most attention is local in practice. In modern stacks, the sliding-window mask is executed \emph{inside} a FlashAttention kernel.
  \item \textbf{滑动窗口 / 局部注意力}：每个token只关注最近的 $w$ 个token（例如 $w = 4096$）。代价变为 $O(n \cdot w)$——关于 $n$ 线性。被Mistral~\cite{jiang2023mistral}（窗口 $= 4096$）和Longformer~\cite{beltagy2020longformer} 使用。以全局上下文换取效率；在实践中效果良好，因为大多数注意力是局部的。在现代技术栈中，滑动窗口掩码是在FlashAttention内核 \emph{内部} 执行的。
  \item \textbf{Sparse attention patterns}: Combine local windows with periodic global tokens (e.g., every 512th token attends to all). BigBird~\cite{zaheer2020bigbird} and LongT5~\cite{guo2022longt5} use this. Preserves some long-range connectivity at $O(n\sqrt{n})$ cost. Again, FlashAttention serves as the underlying kernel for the non-zero attention blocks.
  \item \textbf{稀疏注意力模式}：结合局部窗口和周期性全局token（例如每第512个token关注所有token）。BigBird~\cite{zaheer2020bigbird} 和 LongT5~\cite{guo2022longt5} 使用此方法。以 $O(n\sqrt{n})$ 的代价保留了一些长距离连接。同样，FlashAttention作为非零注意力块的底层内核。
  \item \textbf{Linear attention / state-space models}: Replace $\text{softmax}(QK^T)V$ with $\phi(Q)(\phi(K)^T V)$ using associativity, or reformulate as a recurrence (Mamba~\cite{gu2023mamba}, RWKV~\cite{peng2023rwkv}). Theoretically $O(n \cdot d^2)$ total. Unlike approaches 2--3 above, these are \emph{architectural replacements} that alter model expressiveness---softmax-free attention is fundamentally less expressive, and empirically these models still lag behind transformers on tasks requiring precise long-range retrieval or complex reasoning.
  \item \textbf{线性注意力 / 状态空间模型}：利用结合律将 $\text{softmax}(QK^T)V$ 替换为 $\phi(Q)(\phi(K)^T V)$，或重新表述为循环形式（Mamba~\cite{gu2023mamba}，RWKV~\cite{peng2023rwkv}）。理论上总复杂度 $O(n \cdot d^2)$。与上述方法2-3不同，这些是 \emph{架构替换}，改变了模型表达能力——无softmax的注意力本质上表达能力较弱，且实验表明这些模型在需要精确长距离检索或复杂推理的任务上仍落后于Transformer。
  \item \textbf{KV cache compression}: At inference, compress or evict old KV pairs to bound memory. Techniques include: H$_2$O~\cite{zhang2023h2o} (heavy-hitter oracle---keep only high-attention keys), StreamingLLM~\cite{xiao2024streamingllm} (keep initial ``attention sink'' tokens + recent window), and quantized KV caches~\cite{liu2024kivi}.
  \item \textbf{KV缓存压缩}：推理时，压缩或驱逐旧的KV对以限制内存。技术包括：H$_2$O~\cite{zhang2023h2o}（重击者预言——只保留高注意力的键），StreamingLLM~\cite{xiao2024streamingllm}（保留初始“注意力汇”token+最近窗口），以及量化KV缓存~\cite{liu2024kivi}。
\end{enumerate}

\begin{intuitionbox}[FlashAttention + Sparse Patterns = Best of Both Worlds]
\begin{intuitionbox}[FlashAttention + 稀疏模式 = 两全其美]

A common misconception is that FlashAttention is an \emph{alternative} to sparse attention. It is not---it is an IO optimization for the attention kernel that composes freely with any attention mask. Modern production systems (e.g., Mistral, DeepSeek) use FlashAttention as the execution engine \emph{underneath} a sliding-window or block-sparse mask. This gives you both reduced FLOPs (from sparsity) and optimal memory access patterns (from tiling). RingAttention~\cite{liu2023ringattention} extends this further to multi-device settings, distributing the tiled computation across GPUs along the sequence dimension.
一个常见的误解是，FlashAttention 是稀疏注意力的 \emph{替代方案}。事实并非如此——它是一种针对注意力内核的IO优化，可以与任何注意力掩码自由组合。现代生产系统（例如Mistral、DeepSeek）将FlashAttention作为滑动窗口或块稀疏掩码 \emph{底层} 的执行引擎。这既带来了更少的FLOPs（来自稀疏性），又实现了最优的内存访问模式（来自分块）。RingAttention~\cite{liu2023ringattention} 进一步将其扩展到多设备设置，沿序列维度将分块计算分布到多个GPU上。

\end{intuitionbox}

## Linear attention and state-space models (Mamba, RWKV) are a genuinely different architectural choice---they sacrifice the full pairwise interaction for $O(n)$ compute. While theoretically elegant, they have not matched transformer quality on knowledge-intensive or long-range reasoning tasks, and frontier labs continue to use exact attention (with FlashAttention + sparsity) as the backbone.  
## 线性注意力与状态空间模型（Mamba、RWKV）是一种截然不同的架构选择——它们牺牲了全对偶交互，换取了 $O(n)$ 的计算复杂度。尽管理论优雅，但在知识密集型或长程推理任务上尚未达到 transformer 的质量，前沿实验室仍以精确注意力（结合 FlashAttention 与稀疏性）作为骨干。

\end{intuitionbox}

## Multi-Head Attention  
## 多头注意力

Rather than computing a single attention function, multi-head attention runs several attention operations in parallel, each learning to focus on different aspects of the input (syntax, semantics, position, etc.).  
多头注意力并非只计算一个注意力函数，而是并行运行多个注意力操作，每个操作学习聚焦输入的不同方面（句法、语义、位置等）。

\begin{keybox}[Multi-Head Attention]
Instead of one attention function with $d$-dimensional keys/values, use $H$ parallel heads with dimension $d_k = d/H$: 
\[
\text{MultiHead}(X) = \text{Concat}(\text{head}_1, \ldots, \text{head}_H) W_O
\]
 Each head can learn different attention patterns (e.g., one head for syntax, another for semantics, another for positional proximity).
不使用单一的 $d$ 维键/值注意力函数，而是采用 $H$ 个并行头，每个头维度为 $d_k = d/H$：
\[
\text{MultiHead}(X) = \text{Concat}(\text{head}_1, \ldots, \text{head}_H) W_O
\]
每个头可以学习不同的注意力模式（例如，一个头关注句法，另一个关注语义，另一个关注位置邻近性）。

\textbf{Grouped Query Attention (GQA)}: Llama-3~\cite{grattafiori2024llama3} uses fewer K,V heads than Q heads (e.g., 8 KV heads shared across 32 Q heads). This reduces KV cache size by $4\times$ with minimal quality loss.
\textbf{分组查询注意力（GQA）}：Llama-3~\cite{grattafiori2024llama3} 使用的 K、V 头数量少于 Q 头（例如，32 个 Q 头共享 8 个 KV 头）。这使 KV 缓存大小减少 $4\times$，而质量损失极小。
\end{keybox}

## Positional Encodings  
## 位置编码

Transformers are permutation-equivariant by construction --- without positional information, the model cannot distinguish ``the cat sat on the mat'' from ``mat the on sat cat the''. Positional encodings inject sequence-order signal so that attention can reason about token distance and direction.  
Transformer 在结构上是排列等变的——没有位置信息，模型无法区分“the cat sat on the mat”和“mat the on sat cat the”。位置编码注入序列顺序信号，使注意力能够推理 token 的距离与方向。

\begin{table}[ht!]
\centering
\caption{Positional encoding methods in modern LLMs.}
\caption{现代 LLM 中的位置编码方法。}
\begin{tabular}{@{}lp{5cm}p{6.5cm}@{}}
\toprule
\textbf{Method} & \textbf{Used By} & \textbf{Key Idea} \\
\midrule
Sinusoidal & Original Transformer & Fixed $\sin/\cos$ at different frequencies. Not learned. \\
Learned Absolute & GPT-2~\cite{radford2019gpt2}, BERT~\cite{devlin2019bert} & Learned embedding per position. Limited to training length. \\
RoPE (Rotary) & Llama~\cite{grattafiori2024llama3}, Qwen~\cite{qwen2024qwen25}, Mistral~\cite{jiang2023mistral} & Rotate Q,K vectors by position-dependent angle. Extrapolates via NTK-aware scaling. \\
ALiBi & BLOOM~\cite{workshop2023bloom}, MPT~\cite{mosaicml2023mpt} & No position embedding; add linear bias $-m|i-j|$ to attention scores. Simple, extrapolates well. \\
\bottomrule
\end{tabular}
\begin{tabular}{@{}lp{5cm}p{6.5cm}@{}}
\toprule
\textbf{方法} & \textbf{使用模型} & \textbf{核心理念} \\
\midrule
正弦波 & 原始 Transformer & 固定频率的 $\sin/\cos$，非学习得到。 \\
可学习绝对位置 & GPT-2~\cite{radford2019gpt2}, BERT~\cite{devlin2019bert} & 每个位置的可学习嵌入，受限于训练长度。 \\
RoPE（旋转） & Llama~\cite{grattafiori2024llama3}, Qwen~\cite{qwen2024qwen25}, Mistral~\cite{jiang2023mistral} & 根据位置角度旋转 Q、K 向量，通过 NTK 感知缩放外推。 \\
ALiBi & BLOOM~\cite{workshop2023bloom}, MPT~\cite{mosaicml2023mpt} & 无位置嵌入，在注意力分数上添加线性偏置 $-m|i-j|$，简单且外推效果好。 \\
\bottomrule
\end{tabular}
\end{table}

\paragraph{Sinusoidal (Fixed) Positional Encoding.}
\paragraph{正弦波（固定）位置编码。}

Introduced in the original Transformer~\cite{vaswani2017attention}, this method uses fixed sinusoidal functions at geometrically-spaced frequencies: 
\[
\text{PE}(pos, 2i) = \sin\!\Bigl(\frac{pos}{10000^{2i/d}}\Bigr), \qquad
  \text{PE}(pos, 2i{+}1) = \cos\!\Bigl(\frac{pos}{10000^{2i/d}}\Bigr)
\]
 where $pos$ is the token position, $i$ is the dimension index, and $d$ is the model dimension.
该方法在原始 Transformer~\cite{vaswani2017attention} 中引入，使用几何间隔频率上的固定正弦函数：
\[
\text{PE}(pos, 2i) = \sin\!\Bigl(\frac{pos}{10000^{2i/d}}\Bigr), \qquad
  \text{PE}(pos, 2i{+}1) = \cos\!\Bigl(\frac{pos}{10000^{2i/d}}\Bigr)
\]
其中 $pos$ 是 token 位置，$i$ 是维度索引，$d$ 是模型维度。

\textbf{Motivation:} Each frequency encodes position at a different scale (analogous to binary counting). The authors hypothesised that the model could learn to attend to relative positions because $\text{PE}(pos+k)$ can be expressed as a linear function of $\text{PE}(pos)$.
\textbf{动机：}每个频率以不同的尺度编码位置（类似于二进制计数）。作者假设模型能学会关注相对位置，因为 $\text{PE}(pos+k)$ 可以表示为 $\text{PE}(pos)$ 的线性函数。

\textbf{Pros:} Zero learned parameters; deterministic; theoretically supports arbitrary lengths.\\
\textbf{优点：}零可学习参数；确定性；理论上支持任意长度。

\textbf{Cons:} In practice, does not extrapolate well beyond training lengths; the model must learn to decode relative position from absolute signals indirectly; largely superseded.
\textbf{缺点：}在实践中无法很好地外推到训练长度之外；模型必须间接地从绝对信号中解码相对位置；已基本被取代。

\paragraph{Learned Absolute Positional Embedding.}
\paragraph{可学习绝对位置嵌入。}

Used by GPT-2~\cite{radford2019gpt2} and BERT~\cite{devlin2019bert}: a learnable embedding matrix $\mathbf{E}_{\text{pos}} \in \mathbb{R}^{L_{\max} \times d}$ is added to token embeddings: 
\[
h_0^{(pos)} = \text{TokenEmbed}(x_{pos}) + \mathbf{E}_{\text{pos}}[pos]
\]
GPT-2~\cite{radford2019gpt2} 和 BERT~\cite{devlin2019bert} 使用该方法：一个可学习的嵌入矩阵 $\mathbf{E}_{\text{pos}} \in \mathbb{R}^{L_{\max} \times d}$ 被加到 token 嵌入上：
\[
h_0^{(pos)} = \text{TokenEmbed}(x_{pos}) + \mathbf{E}_{\text{pos}}[pos]
\]

\textbf{Motivation:} Let the model learn whatever positional representation is optimal for the task, rather than imposing a fixed structure.
\textbf{动机：}让模型学习对任务最优的任何位置表示，而不是强加固定结构。

\textbf{Pros:} Maximum flexibility; simple implementation; often outperforms sinusoidal for short sequences.\\
\textbf{优点：}最大灵活性；实现简单；在短序列上通常优于正弦波。

\textbf{Cons:} Hard-coded maximum length $L_{\max}$; no generalisation beyond it; embeddings near the end of $L_{\max}$ are under-trained; adds $L_{\max} \times d$ parameters.
\textbf{缺点：}硬编码的最大长度 $L_{\max}$；无法推广到更长的长度；$L_{\max}$ 末尾的嵌入训练不足；增加 $L_{\max} \times d$ 个参数。

\paragraph{Rotary Position Embedding (RoPE).}
\paragraph{旋转位置嵌入（RoPE）。}

RoPE~\cite{su2024roformer} encodes position by \emph{rotating} query and key vectors in 2D subspaces: 
\[
\text{RoPE}(x_m, m) = \begin{pmatrix} x_m^{(1)} \\ x_m^{(2)} \\ \vdots \\ x_m^{(d-1)} \\ x_m^{(d)} \end{pmatrix}
  \odot
  \begin{pmatrix} \cos m\theta_1 \\ \cos m\theta_1 \\ \vdots \\ \cos m\theta_{d/2} \\ \cos m\theta_{d/2} \end{pmatrix}
  +
  \begin{pmatrix} -x_m^{(2)} \\ x_m^{(1)} \\ \vdots \\ -x_m^{(d)} \\ x_m^{(d-1)} \end{pmatrix}
  \odot
  \begin{pmatrix} \sin m\theta_1 \\ \sin m\theta_1 \\ \vdots \\ \sin m\theta_{d/2} \\ \sin m\theta_{d/2} \end{pmatrix}
\]
 where $\theta_i = 10000^{-2i/d}$ and $m$ is the position index. The key property is that the dot product between rotated queries and keys depends only on relative position: 
\[
\langle \text{RoPE}(q_m, m),\; \text{RoPE}(k_n, n) \rangle = f(q_m, k_n, m-n)
\]
RoPE~\cite{su2024roformer} 通过在二维子空间中 \emph{旋转} 查询和键向量来编码位置：
\[
\text{RoPE}(x_m, m) = \begin{pmatrix} x_m^{(1)} \\ x_m^{(2)} \\ \vdots \\ x_m^{(d-1)} \\ x_m^{(d)} \end{pmatrix}
  \odot
  \begin{pmatrix} \cos m\theta_1 \\ \cos m\theta_1 \\ \vdots \\ \cos m\theta_{d/2} \\ \cos m\theta_{d/2} \end{pmatrix}
  +
  \begin{pmatrix} -x_m^{(2)} \\ x_m^{(1)} \\ \vdots \\ -x_m^{(d)} \\ x_m^{(d-1)} \end{pmatrix}
  \odot
  \begin{pmatrix} \sin m\theta_1 \\ \sin m\theta_1 \\ \vdots \\ \sin m\theta_{d/2} \\ \sin m\theta_{d/2} \end{pmatrix}
\]
其中 $\theta_i = 10000^{-2i/d}$，$m$ 是位置索引。关键性质是，旋转后的查询与键之间的点积仅取决于相对位置：
\[
\langle \text{RoPE}(q_m, m),\; \text{RoPE}(k_n, n) \rangle = f(q_m, k_n, m-n)
\]

\textbf{Motivation:} Achieve relative position encoding without explicit bias terms, while maintaining compatibility with linear attention and KV-caching.
\textbf{动机：}实现无需显式偏置项的相对位置编码，同时保持与线性注意力和 KV 缓存的兼容性。

\textbf{Pros:} Naturally relative; no extra parameters; compatible with efficient inference; can be extended to longer contexts via NTK-aware scaling~\cite{peng2023yarn} or YaRN (adjusting $\theta$ base or interpolating frequencies).\\
\textbf{优点：}天然相对；无额外参数；兼容高效推理；可通过 NTK 感知缩放~\cite{peng2023yarn} 或 YaRN（调整 $\theta$ 基数或插值频率）扩展到更长的上下文。

\textbf{Cons:} Slightly more compute per attention operation (rotation + interleaving); extrapolation requires explicit scaling strategies; rotation in 2D subspaces imposes structure that may not be optimal for all tasks.
\textbf{缺点：}每次注意力操作的计算量略高（旋转 + 交错）；外推需要显式缩放策略；二维子空间中的旋转施加的结构可能并非对所有任务最优。

\begin{intuitionbox}[RoPE Length Extension]
To extend a RoPE model trained at $L$ to context length $L' > L$:
要将一个在 $L$ 上训练的 RoPE 模型扩展到上下文长度 $L' > L$：

\begin{itemize}
  \item \textbf{Position interpolation:} Scale positions by $L/L'$ so all positions fit in $[0, L]$. Simple but compresses resolution.
  \item \textbf{NTK-aware scaling:} Increase the $\theta$ base (e.g.~$10000 \to 10000 \cdot (L'/L)^{d/(d-2)}$), effectively stretching high-frequency components while preserving low-frequency ones.
  \item \textbf{YaRN}~\cite{peng2023yarn}: Combines NTK scaling with an attention temperature correction $t = 0.1 \ln(s) + 1$ to compensate for increased entropy at longer distances.
  \item \textbf{位置插值：}将位置按 $L/L'$ 缩放，使所有位置落在 $[0, L]$ 内。简单但会压缩分辨率。
  \item \textbf{NTK 感知缩放：}增大 $\theta$ 基数（例如 $10000 \to 10000 \cdot (L'/L)^{d/(d-2)}$），有效地拉伸高频分量同时保持低频分量。
  \item \textbf{YaRN}~\cite{peng2023yarn}：将 NTK 缩放与注意力温度校正 $t = 0.1 \ln(s) + 1$ 结合，以补偿长距离下的熵增加。
\end{itemize}
\end{intuitionbox}

\paragraph{ALiBi (Attention with Linear Biases).}
\paragraph{ALiBi（线性偏置注意力）。}

ALiBi~\cite{press2022train} takes a radically different approach: \emph{no positional embedding at all}. Instead, a static linear penalty is subtracted from attention scores: 
\[
\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}} - m \cdot \bigl[|i-j|\bigr]_{i,j}\right) V
\]
 where $m$ is a head-specific slope (set geometrically: $m_h = 2^{-8h/H}$ for head $h$ of $H$ total). The bias $-m|i-j|$ creates a soft local attention window whose width varies by head.
ALiBi~\cite{press2022train} 采用了一种截然不同的方法：\emph{完全没有位置嵌入}。相反，从注意力分数中减去一个静态线性惩罚：
\[
\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}} - m \cdot \bigl[|i-j|\bigr]_{i,j}\right) V
\]
其中 $m$ 是每个头特有的斜率（按几何级数设置：对于总头数 $H$ 中的第 $h$ 个头，$m_h = 2^{-8h/H}$）。偏置 $-m|i-j|$ 创建了一个软局部注意力窗口，其宽度随头变化。

\textbf{Motivation:} Position should bias attention toward nearby tokens (recency prior) without interfering with the embedding space. By operating purely in attention-score space, ALiBi avoids polluting token representations with positional signal.
\textbf{动机：}位置应该使注意力偏向附近的 token（近因先验），同时不干扰嵌入空间。通过在注意力分数空间中纯粹操作，ALiBi 避免了用位置信号污染 token 表示。

\textbf{Pros:} Excellent length extrapolation (trained at 1k, works at 8k+); zero parameters; trivial to implement; head-specific slopes give multi-scale locality.\\
\textbf{优点：}极佳的长度外推能力（1k 训练，8k+ 可用）；零参数；实现简单；头特有斜率提供了多尺度局部性。

\textbf{Cons:} Less expressive for tasks requiring precise long-range positional reasoning (e.g.~``what was the 5th word?''); the linear decay is a strong inductive bias that may not suit all domains; largely overtaken by RoPE in recent models due to RoPE’s better short-context performance.
\textbf{缺点：}对于需要精确长程位置推理的任务（例如“第5个词是什么？”）表达能力较弱；线性衰减是一种强归纳偏置，可能不适合所有领域；由于 RoPE 在短上下文上表现更好，在当前模型中已基本被 RoPE 超越。

## 3.4 位置编码
## 3.4 Positional Encoding

\begin{table}[ht!]
\centering
\caption{位置编码比较：实际权衡。}
\caption{Positional encoding comparison: practical trade-offs.}
\begin{tabular}{@{}lp{2.5cm}p{2.8cm}p{2.8cm}p{2.8cm}@{}}
\toprule
 & \textbf{正弦 Sinusoidal} & \textbf{可学习绝对 Learned Abs.} & \textbf{RoPE} & \textbf{ALiBi} \\
\midrule
额外参数 Extra parameters & 无 None & $L_{\max} \times d$ & 无 None & 无 None \\
位置类型 Position type & 绝对 Absolute & 绝对 Absolute & 相对 Relative & 相对（隐式）Relative (implicit) \\
长度外推 Length extrapolation & 差 Poor & 无 None & 良好（有缩放）Good (w/ scaling) & 极好 Excellent \\
计算开销 Compute overhead & 可忽略 Negligible & 可忽略 Negligible & 较小 Small & 可忽略 Negligible \\
主导时期 Dominant era & 2017--19 & 2018--20 & 2022--至今 & 2022--23 \\
\bottomrule
\end{tabular}
\end{table}

\paragraph{扩展到超长上下文（100K--1M+ Token）。}
\paragraph{Scaling to Extremely Long Contexts (100K--1M+ Tokens).}
\label{scaling-to-extremely-long-contexts-100k1m-tokens.}

现代前沿模型（Claude~\cite{anthropic2024claude3} 具有200K--1M上下文，Gemini 1.5~\cite{geminiteam2024gemini15} 达到1M+，GPT-4~\cite{openai2023gpt4} 为128K）要求位置编码在远超训练长度的范围内保持忠实。当前的解决方案主要有：
Modern frontier models (Claude~\cite{anthropic2024claude3} with 200K--1M context, Gemini 1.5~\cite{geminiteam2024gemini15} at 1M+, GPT-4~\cite{openai2023gpt4} at 128K) require positional encodings that remain faithful far beyond training lengths. The dominant solutions today:

\begin{enumerate}
  \item \textbf{带频率缩放的RoPE}：将RoPE扩展到训练长度以外的标准方法。无需重新训练，而是重新缩放基础频率 $\theta$：
\[
\theta'_i = \theta_i \cdot \left(\frac{L_{\text{target}}}{L_{\text{train}}}\right)^{2i/d}
\]
变体包括：
  \item \textbf{RoPE with frequency scaling}: The standard approach for extending RoPE beyond training length. Rather than retraining, the base frequency $\theta$ is rescaled: 
\[
\theta'_i = \theta_i \cdot \left(\frac{L_{\text{target}}}{L_{\text{train}}}\right)^{2i/d}
\]
 Variants include:

\begin{itemize}
  \item \textbf{线性缩放}（位置插值）\cite{chen2023extending}：简单地将位置索引除以因子 $s$。计算成本低，但在高扩展比下会降低质量。
  \item \textbf{Linear scaling} (Position Interpolation)~\cite{chen2023extending}: Simply divide position indices by a factor $s$. Cheap but degrades quality at high extension ratios.
  \item \textbf{NTK感知缩放}\cite{peng2023yarn}：将基础频率缩放为 $\theta = 10000 \to 10000 \cdot s^{d/(d-2)}$。保留高频（局部）信息同时扩展低频（全局）范围。
  \item \textbf{NTK-aware scaling}~\cite{peng2023yarn}: Scale the base frequency $\theta = 10000 \to 10000 \cdot s^{d/(d-2)}$. Preserves high-frequency (local) information while extending low-frequency (global) range.
  \item \textbf{YaRN}\cite{peng2023yarn}（Yet another RoPE extensioN）：结合NTK缩放与注意力温度校正，并在小型长上下文语料上进行微调。Llama-3使用此方法将训练长度从8K扩展到部署时的128K。
  \item \textbf{YaRN}~\cite{peng2023yarn} (Yet another RoPE extensioN): Combines NTK scaling with an attention temperature correction and fine-tuning on a small long-context corpus. Used by Llama-3 to extend from 8K training to 128K deployment.
  \item \textbf{动态NTK}\cite{peng2023yarn}：在推理时根据实际序列长度动态调整缩放因子。无需固定的扩展比——模型随上下文增长而自适应。
  \item \textbf{Dynamic NTK}~\cite{peng2023yarn}: Adjusts the scaling factor on-the-fly based on actual sequence length at inference. No fixed extension ratio needed---the model adapts as context grows.
\end{itemize}
  \item \textbf{在长数据上继续预训练}：即使采用RoPE缩放，模型也受益于在长文档上进行短期的继续预训练阶段（1--5B token）。这教会模型实际\emph{使用}远处的上下文，而不仅仅是位置上的容忍。Llama-3.1使用了渐进式安排：8K $\to$ 64K $\to$ 128K。
  \item \textbf{Continued pretraining on long data}: Even with RoPE scaling, models benefit from a short continued pretraining phase (1--5B tokens) on long documents. This teaches the model to actually \emph{use} distant context, not just tolerate it positionally. Llama-3.1 used a progressive schedule: 8K $\to$ 64K $\to$ 128K.
  \item \textbf{环形注意力/分块并行}\cite{liu2023ringattention}：对于超过单GPU内存的序列（1M+ token），环形注意力将序列以环形拓扑分布在多个GPU上。每个GPU持有一个块，并在环上传递KV块，计算局部注意力瓦片。这使得内存随GPU数量线性扩展，同时保持精确注意力。
  \item \textbf{Ring Attention / Blockwise Parallel}~\cite{liu2023ringattention}: For sequences exceeding single-GPU memory (1M+ tokens), Ring Attention distributes the sequence across GPUs in a ring topology. Each GPU holds a block and passes KV blocks around the ring, computing local attention tiles. This enables linear memory scaling with GPU count while preserving exact attention.
  \item \textbf{混合架构}：一些系统将局部滑动窗口（例如4K）用于大多数层，而在选定层（例如每4层）使用全注意力。这样大部分计算的成本为 $O(n \cdot w)$，同时保持全局信息流。
  \item \textbf{Hybrid architectures}: Some systems combine a local sliding window (e.g., 4K) for most layers with full attention at select layers (e.g., every 4th layer). This provides $O(n \cdot w)$ cost for most computation while maintaining global information flow.
\end{enumerate}

\begin{warningbox}[长上下文 $\neq$ 长上下文利用 Long Context $\neq$ Long Context Usage]
具有1M上下文长度的模型并不\emph{一定}能有效利用全部1M token。``中间丢失''现象\cite{liu2024lost}表明，模型倾向于关注长上下文的开头和结尾，而未能充分利用中间的信息。有效的长上下文利用既需要位置编码的支持，也需要在奖励长距离检索的任务上进行训练。
A model with 1M context length does \emph{not} necessarily use all 1M tokens effectively. The ``lost in the middle'' phenomenon~\cite{liu2024lost} shows that models tend to focus on the beginning and end of long contexts, underutilizing information in the middle. Effective long-context utilization requires both positional encoding support \emph{and} training on tasks that reward long-range retrieval.
\end{warningbox}

\subsection{前馈网络（MLP）}
\subsection{Feed-Forward Network (MLP)}
\label{feed-forward-network-mlp}

每个Transformer块包含一个独立应用于每个位置的MLP：
Each transformer block contains an MLP applied independently to each position: 
\[
\text{FFN}(x) = W_2 \cdot \sigma(W_1 x + b_1) + b_2
\]
其中 $W_1 \in \mathbb{R}^{d \times 4d}$，$W_2 \in \mathbb{R}^{4d \times d}$。现代LLM使用：
 where $W_1 \in \mathbb{R}^{d \times 4d}$, $W_2 \in \mathbb{R}^{4d \times d}$. Modern LLMs use:

\begin{itemize}
  \item \textbf{SwiGLU激活函数}：$\text{FFN}(x) = W_2 (\text{Swish}(W_1 x) \odot W_3 x)$ —— 由Llama\cite{grattafiori2024llama3}、Mistral\cite{jiang2023mistral}使用。需要3个权重矩阵，但性能更好。
  \item \textbf{SwiGLU activation}: $\text{FFN}(x) = W_2 (\text{Swish}(W_1 x) \odot W_3 x)$ --- used by Llama~\cite{grattafiori2024llama3}, Mistral~\cite{jiang2023mistral}. Requires 3 weight matrices but gives better performance.
  \item 隐藏维度通常为 $8/3 \times d$（为了Tensor Core效率，向上取整为256的倍数）。
  \item Hidden dimension is typically $8/3 \times d$ (rounded to multiples of 256 for Tensor Core efficiency).
\end{itemize}

\begin{intuitionbox}[FFN作为记忆 FFN as Memory]
最近的工作\cite{geva2021transformer}表明，FFN层充当\emph{键值记忆}：$W_1$的行是键（要匹配的模式），$W_2$的列是值（要输出的信息）。FFN根据当前隐藏状态``检索''存储的知识。
Recent work~\cite{geva2021transformer} suggests the FFN layers act as a \emph{key-value memory}: $W_1$ rows are keys (patterns to match), $W_2$ columns are values (information to output). The FFN ``retrieves'' stored knowledge based on the current hidden state.
\end{intuitionbox}

\subsection{层归一化}
\subsection{Layer Normalization}
\label{layer-normalization}

层归一化通过在特征维度上归一化激活来稳定训练。它与注意力/FFN子层的相对位置显著影响训练动态。
Layer normalization stabilizes training by normalizing activations across the feature dimension. Its placement relative to the attention/FFN sublayers significantly affects training dynamics.

\paragraph{LayerNorm 如何工作。}
\paragraph{How LayerNorm Works.}
\label{how-layernorm-works.}

给定隐藏状态向量 $\mathbf{x} \in \mathbb{R}^d$（单个token的表示），LayerNorm\cite{ba2016layernorm}计算：
Given a hidden state vector $\mathbf{x} \in \mathbb{R}^d$ (a single token’s representation), LayerNorm~\cite{ba2016layernorm} computes:

\begin{equation}
\text{LayerNorm}(\mathbf{x}) = \gamma \odot \frac{\mathbf{x} - \mu}{\sqrt{\sigma^2 + \epsilon}} + \beta
\end{equation}

其中：
where:

\begin{itemize}
  \item $\mu = \frac{1}{d}\sum_{i=1}^{d} x_i$（$d$个特征维度上的均值）
  \item $\mu = \frac{1}{d}\sum_{i=1}^{d} x_i$ (mean across the $d$ feature dimensions)
  \item $\sigma^2 = \frac{1}{d}\sum_{i=1}^{d} (x_i - \mu)^2$（特征上的方差）
  \item $\sigma^2 = \frac{1}{d}\sum_{i=1}^{d} (x_i - \mu)^2$ (variance across features)
  \item $\gamma, \beta \in \mathbb{R}^d$ 是\emph{可学习}的缩放和偏移参数（每个维度一个）
  \item $\gamma, \beta \in \mathbb{R}^d$ are \textbf{learned} scale and shift parameters (per-dimension)
  \item $\epsilon \approx 10^{-5}$ 防止除以零
  \item $\epsilon \approx 10^{-5}$ prevents division by zero
\end{itemize}

\textbf{与BatchNorm的关键区别}：LayerNorm是对单个样本的\emph{特征维度}进行归一化，而不是跨批次。这使得它与批量大小无关，在训练和推理时行为相同。
\textbf{Key distinction from BatchNorm}: LayerNorm normalizes across the \emph{feature dimension} of a single example, not across the batch. This makes it independent of batch size and works identically at training and inference.

\paragraph{RMSNorm——现代简化版。}
\paragraph{RMSNorm --- The Modern Simplification.}
\label{rmsnorm-the-modern-simplification.}

RMSNorm\cite{zhang2019rmsnorm}去掉了均值中心化步骤，仅通过均方根进行归一化：
RMSNorm~\cite{zhang2019rmsnorm} drops the mean-centering step, normalizing only by the root-mean-square:

\begin{equation}
\text{RMSNorm}(\mathbf{x}) = \gamma \odot \frac{\mathbf{x}}{\text{RMS}(\mathbf{x})}, \qquad \text{RMS}(\mathbf{x}) = \sqrt{\frac{1}{d}\sum_{i=1}^{d} x_i^2}
\end{equation}

没有$\beta$（偏移）参数，也没有减去均值——只有缩放。这为每个token节省了一次归约操作，在GPU上速度提高约5--10%，同时达到相当的模型质量。所有现代LLM（Llama、Mistral、Qwen）都使用RMSNorm。
No $\beta$ (shift) parameter and no mean subtraction --- just scale. This saves one reduction operation per token and is $\sim$5--10\% faster on GPUs while achieving equivalent model quality. All modern LLMs (Llama, Mistral, Qwen) use RMSNorm.

\begin{keybox}[Pre-LN vs Post-LN]
\begin{itemize}
  \item \textbf{Post-LN}（原始Transformer）：$h + \text{LayerNorm}(\text{Attn}(h))$。需要仔细的预热；训练可能不稳定。
  \item \textbf{Pre-LN}（GPT-2+，所有现代LLM）：$h + \text{Attn}(\text{LayerNorm}(h))$。稳定训练；允许更高的学习率。
  \item \textbf{RMSNorm}（Llama\cite{grattafiori2024llama3}、Mistral\cite{jiang2023mistral}）：简化的LayerNorm，没有均值中心化：$\text{RMSNorm}(x) = x / \text{RMS}(x) \cdot \gamma$。稍快，质量相同。
  \item \textbf{Post-LN} (original Transformer): $h + \text{LayerNorm}(\text{Attn}(h))$. Requires careful warmup; training can be unstable.
  \item \textbf{Pre-LN} (GPT-2+, all modern LLMs): $h + \text{Attn}(\text{LayerNorm}(h))$. Stabilizes training; enables higher learning rates.
  \item \textbf{RMSNorm} (Llama~\cite{grattafiori2024llama3}, Mistral~\cite{jiang2023mistral}): Simplified LayerNorm without mean-centering: $\text{RMSNorm}(x) = x / \text{RMS}(x) \cdot \gamma$. Slightly faster, same quality.
\end{itemize}
\end{keybox}

\begin{intuitionbox}[为什么归一化对深层网络很重要 Why Normalization Matters for Deep Networks]
如果没有归一化，激活值在层间会呈指数级增长或缩小（梯度爆炸/消失）。一个128层的Transformer如果不使用LayerNorm，第一层和最后一层之间的数值规模会相差$10^{30}$倍。归一化将每一层的输出限制在可预测的范围内，从而实现稳定的梯度流，并允许优化器在整个网络中使用一致的学习率。
Without normalization, activations tend to grow or shrink exponentially through layers (exploding/vanishing activations). A 128-layer transformer without LayerNorm would see magnitudes vary by $10^{30}\times$ between the first and last layer. Normalization constrains each layer’s output to a predictable range, enabling stable gradient flow and allowing the optimizer to use consistent learning rates throughout the network.
\end{intuitionbox}

\subsection{模型尺寸参考}
\subsection{Model Size Reference}
\label{model-size-reference}

下表总结了广泛使用的开放权重模型（截至2025年的最新版本）的关键架构参数，为理解规模和设计选择提供快速参考。
The following table summarizes key architectural parameters for widely-used open-weight models (latest versions as of 2025), providing a quick reference for understanding scale and design choices.

```markdown
\begin{table}[ht!]
\centering
\caption{Architecture parameters for popular open-weight LLMs (2024--2025 generation).}
\begin{tabular}{@{}lp{1.8cm}p{1.8cm}p{1.8cm}p{1.8cm}p{1.8cm}p{1.8cm}@{}}
\toprule
\textbf{Model} & \textbf{Params} & \textbf{Layers} & \textbf{$d$} & \textbf{Heads} & \textbf{KV Heads} & \textbf{Context} \\
\midrule
Llama-3.1 8B~\cite{grattafiori2024llama3} & 8B & 32 & 4096 & 32 & 8 & 128K \\
Llama-3.1 405B~\cite{grattafiori2024llama3} & 405B & 126 & 16384 & 128 & 8 & 128K \\
Llama-4 Maverick~\cite{meta2025llama4} & 400B (17B active) & 48 & 5120 & 40 & 8 & 1M \\
Mistral Large 2~\cite{jiang2024mistrallarge2} & 123B & 88 & 12288 & 96 & 8 & 128K \\
Qwen-2.5 72B~\cite{qwen2024qwen25} & 72B & 80 & 8192 & 64 & 8 & 128K \\
DeepSeek-V3~\cite{deepseekv3} & 671B (37B active) & 61 & 7168 & 128 & MLA & 128K \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[ht!]
\centering
\caption{流行开源权重LLM的架构参数（2024-2025代）。}
\begin{tabular}{@{}lp{1.8cm}p{1.8cm}p{1.8cm}p{1.8cm}p{1.8cm}p{1.8cm}@{}}
\toprule
\textbf{模型} & \textbf{参数量} & \textbf{层数} & \textbf{$d$} & \textbf{注意力头数} & \textbf{KV头数} & \textbf{上下文长度} \\
\midrule
Llama-3.1 8B~\cite{grattafiori2024llama3} & 8B & 32 & 4096 & 32 & 8 & 128K \\
Llama-3.1 405B~\cite{grattafiori2024llama3} & 405B & 126 & 16384 & 128 & 8 & 128K \\
Llama-4 Maverick~\cite{meta2025llama4} & 400B（17B激活） & 48 & 5120 & 40 & 8 & 1M \\
Mistral Large 2~\cite{jiang2024mistrallarge2} & 123B & 88 & 12288 & 96 & 8 & 128K \\
Qwen-2.5 72B~\cite{qwen2024qwen25} & 72B & 80 & 8192 & 64 & 8 & 128K \\
DeepSeek-V3~\cite{deepseekv3} & 671B（37B激活） & 61 & 7168 & 128 & MLA & 128K \\
\bottomrule
\end{tabular}
\end{table}

\emph{Note}: Models marked with ``active'' parameters use Mixture-of-Experts (MoE) architecture---total parameters indicate model capacity, while active parameters reflect per-token compute cost. DeepSeek-V3 uses Multi-head Latent Attention (MLA) instead of standard GQA, compressing KV into a low-rank latent space.

\emph{注意}：标注“激活”参数量的模型使用了混合专家（Mixture-of-Experts, MoE）架构——总参数量表示模型容量，而激活参数量反映每个token的计算成本。DeepSeek-V3使用多头潜在注意力（Multi-head Latent Attention, MLA）替代标准GQA，将KV压缩到低秩潜在空间中。

\subsection{Attention Pathologies}
\subsection{注意力病理}

\label{attention-pathologies}

While the attention mechanism is powerful, it exhibits systematic failure modes that practitioners must understand---especially when scaling to long contexts or interpreting model behaviour.

尽管注意力机制非常强大，但它表现出一些系统性的失败模式，从业者必须理解这些模式——尤其是在扩展到长上下文或解释模型行为时。

\subsubsection{Attention Sink}
\subsubsection{注意力沉没}

\label{attention-sink}

\paragraph{The phenomenon.}
\paragraph{现象。}

\label{the-phenomenon.}

Xiao et al.~\cite{xiao2024efficient} discovered that transformer models allocate disproportionately high attention scores to the \emph{first token} in the sequence---regardless of its semantic content. Even when the first token is a meaningless \texttt{<BOS>} marker, attention heads across all layers consistently attend to it, sometimes with 20--50\% of total attention mass.

Xiao等人~\cite{xiao2024efficient}发现，Transformer模型会分配不成比例的高注意力分数给序列中的\emph{第一个token}——无论其语义内容如何。即使第一个token是一个无意义的\texttt{<BOS>}标记，所有层的注意力头都会持续关注它，有时甚至会占用20%–50%的总注意力质量。

\paragraph{Why it happens.}
\paragraph{为什么会发生。}

\label{why-it-happens.}

Softmax attention must produce a valid probability distribution ($\sum_j \alpha_j = 1$). When no key is particularly relevant to a query, the model needs a ``dump'' location for unused attention mass. During training, the first token becomes this default sink because it is always present and positionally predictable. It functions as a \emph{no-op attention target}---the model has learned to route irrelevant attention there rather than distributing it unpredictably.

Softmax注意力必须产生一个有效的概率分布（$\sum_j \alpha_j = 1$）。当没有键与某个查询特别相关时，模型需要一个“倾倒”位置来放置未使用的注意力质量。在训练过程中，第一个token成为这个默认的沉没问题，因为它始终存在且位置可预测。它充当了一个\emph{无操作注意力目标}——模型学会了将不相关的注意力引导到那里，而不是以不可预测的方式分布。

\[
\alpha_{\text{sink}} = \frac{\exp(q^\top k_0 / \sqrt{d})}{\sum_{j} \exp(q^\top k_j / \sqrt{d})} \gg \frac{1}{n} \quad \text{(even when } k_0 \text{ is semantically irrelevant)}
\]

\[
\alpha_{\text{sink}} = \frac{\exp(q^\top k_0 / \sqrt{d})}{\sum_{j} \exp(q^\top k_j / \sqrt{d})} \gg \frac{1}{n} \quad \text{（即使 } k_0 \text{ 在语义上无关）}
\]

\paragraph{Consequences.}
\paragraph{后果。}

\label{consequences.}

\begin{itemize}
  \item \textbf{Streaming inference failure}: When using sliding-window KV caches, evicting the first token causes perplexity to spike catastrophically---the model loses its attention sink.
  \item \textbf{流式推理失败}：使用滑动窗口KV缓存时，驱逐第一个token会导致困惑度灾难性地飙升——模型失去了它的注意力沉没问题。
  \item \textbf{Misleading interpretability}: Naive attention visualizations suggest the first token is ``important'' when it is merely a mathematical artefact.
  \item \textbf{误导的可解释性}：简单的注意力可视化会让人认为第一个token“重要”，而它只是一个数学伪像。
  \item \textbf{Context window waste}: The sink token occupies a KV cache slot without carrying useful information.
  \item \textbf{上下文窗口浪费}：沉没token占据了一个KV缓存槽位，却不携带有用信息。
\end{itemize}

\paragraph{Solutions.}
\paragraph{解决方案。}

\label{solutions.}

\begin{itemize}
  \item \textbf{StreamingLLM}~\cite{xiao2024efficient}: Always keep the first $k$ tokens (``attention sinks'') in the KV cache alongside the recent sliding window. Enables infinite-length generation with bounded memory.
  \item \textbf{StreamingLLM}~\cite{xiao2024efficient}：始终在KV缓存中保留前$k$个token（“注意力沉没”），同时保留最近的滑动窗口。能够在有限内存下实现无限长度生成。
  \item \textbf{Sink tokens by design}: Some models (e.g., Mistral) prepend dedicated sink tokens during training that are explicitly meant to absorb residual attention.
  \item \textbf{设计上的沉没token}：一些模型（例如Mistral）在训练时预先附加专门的沉没token，这些token明确用于吸收残余注意力。
  \item \textbf{Softmax alternatives}: Replace softmax with ReLU attention or sigmoid gating, where zero attention is representable without requiring a dump target.
  \item \textbf{Softmax替代方案}：用ReLU注意力或Sigmoid门控替换softmax，其中零注意力可以直接表示，无需倾倒目标。
\end{itemize}

\subsubsection{Attention Dilution}
\subsubsection{注意力稀释}

\label{attention-dilution}

\paragraph{The phenomenon.}
\paragraph{现象。}

\label{the-phenomenon.-1}

As sequence length $n$ grows, each query must distribute its attention budget across more keys. The average attention weight per token decreases as $O(1/n)$, making it progressively harder for the model to concentrate on the few truly relevant positions---a problem known as \emph{attention dilution} or \emph{attention diffusion}~\cite{liu2024lost}.

随着序列长度$n$的增长，每个查询必须将其注意力预算分配到更多的键上。每个token的平均注意力权重按$O(1/n)$递减，使得模型越来越难以集中在少数真正相关的位置上——这个问题被称为\emph{注意力稀释}或\emph{注意力扩散}~\cite{liu2024lost}。

\paragraph{The ``Lost in the Middle'' effect.}
\paragraph{“迷失在中间”效应。}

\label{the-lost-in-the-middle-effect.}

Liu et al.~\cite{liu2024lost} showed that LLMs exhibit a U-shaped retrieval curve: information placed at the \emph{beginning} or \emph{end} of long contexts is retrieved reliably, but information in the \emph{middle} is often ignored. This is a direct consequence of attention dilution compounded with positional biases from RoPE/ALiBi.

Liu等人~\cite{liu2024lost}表明，LLM表现出U形检索曲线：放置在长上下文\emph{开头}或\emph{结尾}的信息可以被可靠地检索，但\emph{中间}的信息常常被忽略。这是注意力稀释与RoPE/ALiBi的位置偏差叠加的直接结果。

\paragraph{Why it happens.}
\paragraph{为什么会发生。}

\label{why-it-happens.-1}

\begin{itemize}
  \item \textbf{Softmax saturation}: With many keys, the softmax temperature effectively decreases, making the distribution more uniform (entropic).
  \item \textbf{Softmax饱和}：当键数量很多时，softmax的温度有效降低，使得分布更加均匀（熵增大）。
  \item \textbf{Positional decay}: RoPE’s relative positional encoding introduces a natural decay with distance, suppressing attention to middle positions that are far from both start and end.
  \item \textbf{位置衰减}：RoPE的相对位置编码引入了随距离的自然衰减，抑制了对远离开头和结尾的中间位置的注意力。
  \item \textbf{Training distribution}: Models trained on shorter sequences develop attention patterns biased toward recent context.
  \item \textbf{训练分布}：在较短序列上训练的模型会形成偏向于近期上下文的注意力模式。
\end{itemize}

\paragraph{Mitigation strategies.}
\paragraph{缓解策略。}

\label{mitigation-strategies.}

\begin{itemize}
  \item \textbf{Explicit retrieval}: Place relevant context at the beginning or end of the prompt; use RAG to avoid relying on middle positions.
  \item \textbf{显式检索}：将相关上下文放置在提示的开头或结尾；使用RAG避免依赖中间位置。
  \item \textbf{Long-context training}: Train on long documents with varied placement of key information~\cite{fu2024data}.
  \item \textbf{长上下文训练}：在关键信息放置位置多变的长文档上训练~\cite{fu2024data}。
  \item \textbf{Hierarchical attention}: Architectures like Mamba~\cite{gu2024mamba} or RWKV that avoid the $O(n^2)$ attention bottleneck entirely.
  \item \textbf{分层注意力}：像Mamba~\cite{gu2024mamba}或RWKV这样的架构完全避免了$O(n^2)$的注意力瓶颈。
  \item \textbf{Landmark tokens}: Insert retrievable markers in the context that act as ``signposts'' for attention.
  \item \textbf{地标token}：在上下文中插入可检索的标记，作为注意力的“路标”。
  \item \textbf{Temperature scaling}: Some implementations scale the attention logits by $\log n$ to counteract dilution in long sequences.
  \item \textbf{温度缩放}：一些实现通过$\log n$缩放注意力logits，以抵消长序列中的稀释效应。
\end{itemize}

\subsubsection{Other Attention Phenomena}
\subsubsection{其他注意力现象}

\label{other-attention-phenomena}

\begin{table}[ht!]
\centering
\caption{Additional attention patterns observed in large transformers.}
\begin{tabular}{@{}lp{5cm}p{6.5cm}@{}}
\toprule
\textbf{Pattern} & \textbf{Description} & \textbf{Implication} \\
\midrule
\textbf{Attention heads specialization} & Different heads learn distinct roles: syntax heads, co-reference heads, positional heads~\cite{voita2019analyzing} & Not all heads are equally important; many can be pruned \\
\textbf{Induction heads} & Heads that implement [A][B]...[A] $\to$ [B] copying~\cite{olsson2022context} & Critical for in-context learning; emerge in 2-layer+ models \\
\textbf{Attention collapse} & In deep networks, attention distributions can converge (all heads attend same positions) & Hurts expressivity; addressed by attention diversity losses \\
\textbf{Retrieval heads} & Specific heads specialize in retrieving factual information from context~\cite{wu2024retrieval} & Explains why pruning certain heads causes hallucination spikes \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[ht!]
\centering
\caption{大型Transformer中观察到的其他注意力模式。}
\begin{tabular}{@{}lp{5cm}p{6.5cm}@{}}
\toprule
\textbf{模式} & \textbf{描述} & \textbf{含义} \\
\midrule
\textbf{注意力头特化} & 不同头学习不同的角色：语法头、共指头、位置头~\cite{voita2019analyzing} & 并非所有头都同等重要；许多可以被剪枝 \\
\textbf{归纳头} & 实现[A][B]...[A] $\to$ [B]复制功能的头~\cite{olsson2022context} & 对上下文学习至关重要；出现在2层以上模型中 \\
\textbf{注意力坍塌} & 在深层网络中，注意力分布可能收敛（所有头关注相同位置） & 损害表达力；通过注意力多样性损失解决 \\
\textbf{检索头} & 特定头专门从上下文中检索事实信息~\cite{wu2024retrieval} & 解释了为什么剪枝某些头会导致幻觉激增 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Visualizing Attention for Explainability}
\subsection{可视化注意力以实现可解释性}

\label{visualizing-attention-for-explainability}

Attention weights provide a window into model reasoning---but must be interpreted carefully.

注意力权重为模型推理提供了一扇窗口——但必须谨慎解读。

\subsubsection{Attention Visualization Methods}
\subsubsection{注意力可视化方法}

\label{attention-visualization-methods}

\paragraph{Raw attention maps.}
\paragraph{原始注意力图。}

\label{raw-attention-maps.}

The simplest approach: plot the $n \times n$ attention matrix $A = \text{softmax}(QK^\top/\sqrt{d})$ as a heatmap for each head and layer. Tools like BertViz~\cite{vig2019bertviz} render interactive multi-head visualizations.

最简单的方法：将$n \times n$的注意力矩阵$A = \text{softmax}(QK^\top/\sqrt{d})$绘制为每个头和层的热力图。像BertViz~\cite{vig2019bertviz}这样的工具可以渲染交互式多头可视化。

\paragraph{Attention rollout.}
\paragraph{注意力展开。}

\label{attention-rollout.}

The raw attention map only reflects direct attention between two layers. To compute the total influence from the input to the output through the entire network, we need to aggregate attention across layers. This is the idea behind \emph{attention rollout}~\cite{abnar2020quantifying}: recursively multiply the attention matrices across layers (optionally including residual connections) to obtain the effective attention distribution between input and output tokens.

原始注意力图仅反映两层之间的直接注意力。为了计算从输入到输出经过整个网络的总影响，我们需要跨层聚合注意力。这就是\emph{注意力展开}~\cite{abnar2020quantifying}背后的思想：递归地跨层相乘注意力矩阵（可选地包含残差连接），以获得输入与输出token之间的有效注意力分布。

\[
\tilde{A}^{(l)} = \begin{cases} 
A^{(l)} & \text{if } l = 1 \\
A^{(l)} \cdot \tilde{A}^{(l-1)} & \text{otherwise}
\end{cases}
\]

\[
\tilde{A}^{(l)} = \begin{cases} 
A^{(l)} & \text{如果 } l = 1 \\
A^{(l)} \cdot \tilde{A}^{(l-1)} & \text{否则}
\end{cases}
\]

Where $A^{(l)}$ is the $n \times n$ attention matrix of layer $l$ (averaged over heads or combined with residual weighting). The final matrix $\tilde{A}^{(L)}$ represents how much each input token contributes to each output token through the full transformer stack.

其中$A^{(l)}$是第$l$层的$n \times n$注意力矩阵（在头上平均或与残差权重结合）。最终矩阵$\tilde{A}^{(L)}$表示每个输入token通过整个Transformer栈对每个输出token的贡献程度。

\paragraph{Limitations of attention visualization.}
\paragraph{注意力可视化的局限性。}

\label{limitations-of-attention-visualization.}

While intuitively appealing, attention weights are not necessarily explanations~\cite{jain2019attention}. Key reasons include:

虽然直观上吸引人，但注意力权重并不一定是解释~\cite{jain2019attention}。主要原因包括：

\begin{itemize}
  \item \textbf{Multi-head averaging obscures function}: Different heads within the same layer often encode conflicting patterns; averaging them hides this complexity.
  \item \textbf{多头部平均掩盖了功能}：同一层内不同的头常常编码相互冲突的模式；平均它们会隐藏这种复杂性。
  \item \textbf{Attention is a distribution, not a measure of importance}: A token can have low attention weight but still be causally critical (e.g., modifying it changes the output dramatically).
  \item \textbf{注意力是一个分布，而不是重要性的度量}：一个token的注意力权重可能很低，但仍然在因果上至关重要（例如，修改它会极大改变输出）。
  \item \textbf{Residual connections dilute attention}: In transformers with residual connections, the contribution of self-attention is indirect; the output also depends on the value vectors and subsequent MLP layers.
  \item \textbf{残差连接稀释了注意力}：在具有残差连接的Transformer中，自注意力的贡献是间接的；输出还依赖于值向量和后续的MLP层。
  \item \textbf{Attention to special tokens is inflated}: As discussed in Section~\ref{attention-sink}, attention to sink tokens or separator tokens can be high without meaningful semantics.
  \item \textbf{对特殊token的注意力被夸大}：如第~\ref{attention-sink}节所述，对沉没token或分隔token的注意力可能很高，但缺乏有意义的语义。
\end{itemize}

\paragraph{Better practices for attention interpretability.}
\paragraph{注意力可解释性的更好实践。}

\label{better-practices-for-attention-interpretability.}

To avoid over-interpreting attention weights, researchers recommend:

为避免过度解读注意力权重，研究人员推荐：

\begin{itemize}
  \item Combine attention analysis with gradient-based methods (e.g., attention $\times$ gradient~\cite{serrano2019attention}).
  \item 将注意力分析与基于梯度的方法结合（例如，注意力$\times$梯度~\cite{serrano2019attention}）。
  \item Validate attention-based insights through causal intervention (e.g., patching~\cite{wang2022interpretability} or ablation).
  \item 通过因果干预（例如，修补~\cite{wang2022interpretability}或消融）验证基于注意力的见解。
  \item Examine attention patterns across multiple layers and heads, rather than relying on a single layer's average.
  \item 检查跨多个层和头的注意力模式，而不是仅依赖单层的平均值。
  \item Use context-dependent interpretation: the same token can have different roles in different contexts.
  \item 使用上下文相关的解释：同一token在不同上下文中可能具有不同的角色。
\end{itemize}

\subsection{Practical Takeaways}
\subsection{实践要点}

\label{practical-takeaways}
```

## How LLMs Work: An Intuitive Overview
## LLM 工作原理：直观概述

Raw attention at a single layer is misleading because information flows through residual connections across \emph{all} layers. Abnar and Zuidema~\cite{abnar2020quantifying} propose \emph{attention rollout}: multiply attention matrices across layers to approximate the total information flow from input to output: 
\[
R^{(l)} = A^{(l)} \cdot R^{(l-1)}, \quad R^{(0)} = I
\]
 where $A^{(l)}$ is the (averaged across heads) attention matrix at layer $l$, adjusted to include the residual connection: $A^{(l)} = 0.5 \cdot A^{(l)}_{\text{raw}} + 0.5 \cdot I$.

单一层的原始注意力具有误导性，因为信息通过残差连接流经\emph{所有}层。Abnar 和 Zuidema~\cite{abnar2020quantifying} 提出了\emph{注意力传播（attention rollout）}：将各层的注意力矩阵相乘，以近似从输入到输出的总信息流：
\[
R^{(l)} = A^{(l)} \cdot R^{(l-1)}, \quad R^{(0)} = I
\]
其中 $A^{(l)}$ 是第 $l$ 层（跨头平均后的）注意力矩阵，经过调整以包含残差连接：$A^{(l)} = 0.5 \cdot A^{(l)}_{\text{raw}} + 0.5 \cdot I$。

\paragraph{Gradient-weighted attention.}
\label{gradient-weighted-attention.}

\paragraph{梯度加权注意力。}
\label{gradient-weighted-attention.}

Combine attention weights with gradient information to identify which attended tokens actually \emph{influence} the output~\cite{barkan2021grad}: 
\[
\text{Relevance}(i) = \alpha_i \cdot \left|\frac{\partial y}{\partial h_i}\right|
\]
 This addresses the criticism that high attention $\neq$ high influence (a token can receive high attention but be processed through a near-zero-weight path).

将注意力权重与梯度信息相结合，以识别哪些被关注的 token 实际上\emph{影响}了输出~\cite{barkan2021grad}：
\[
\text{Relevance}(i) = \alpha_i \cdot \left|\frac{\partial y}{\partial h_i}\right|
\]
这解决了关于高注意力 $\neq$ 高影响力的批评（一个 token 可能获得高注意力，但通过近乎零权重的路径进行处理）。

\begin{warningbox}[Attention Is Not Explanation]
Jain and Wallace~\cite{jain2019attention} showed that attention weights often do not correlate with gradient-based feature importance and that adversarial attention distributions can produce identical outputs. Use attention visualization as a \emph{hypothesis generator}, not as a faithful explanation. For causal attribution, prefer gradient-based methods, probing, or mechanistic interpretability.
\end{warningbox}

\begin{warningbox}[注意力并非解释]
Jain 和 Wallace~\cite{jain2019attention} 表明，注意力权重通常与基于梯度的特征重要性不相关，并且对抗性注意力分布可以产生相同的输出。请将注意力可视化用作\emph{假设生成工具}，而非可靠的解释。对于因果归因，建议优先选择基于梯度的方法、探针（probing）或机械可解释性（mechanistic interpretability）。
\end{warningbox}

\subsubsection{Mechanistic Interpretability with Sparse Autoencoders (SAEs)}
\label{mechanistic-interpretability-with-sparse-autoencoders-saes}

\subsubsection{基于稀疏自编码器（SAE）的机械可解释性}
\label{mechanistic-interpretability-with-sparse-autoencoders-saes}

\paragraph{The interpretability problem.}
\label{the-interpretability-problem.}

\paragraph{可解释性问题。}
\label{the-interpretability-problem.}

Individual neurons in transformer MLPs and residual streams are typically \emph{polysemantic}---a single neuron activates for multiple unrelated concepts (e.g., ``the colour blue AND academic citations AND the word ‘the’''). This makes direct neuron-level interpretation unreliable.

Transformer 中 MLP 和残差流中的单个神经元通常是\emph{多义性（polysemantic）}的——单个神经元会针对多个不相关的概念激活（例如，“蓝色 AND 学术引用 AND 单词‘the’”）。这使得直接进行神经元级别的解释不可靠。

\paragraph{Sparse Autoencoders.}
\label{sparse-autoencoders.}

\paragraph{稀疏自编码器（Sparse Autoencoders）。}
\label{sparse-autoencoders.}

Cunningham et al.~\cite{cunningham2023sparse} and Bricken et al.~\cite{bricken2023monosemanticity} demonstrated that training a sparse autoencoder (SAE) on model activations can decompose polysemantic representations into \emph{monosemantic features}---interpretable directions that each correspond to a single concept:

Cunningham 等人~\cite{cunningham2023sparse} 以及 Bricken 等人~\cite{bricken2023monosemanticity} 证明，在模型激活上训练稀疏自编码器（SAE）可以将多义性表示分解为\emph{单义性特征（monosemantic features）}——每个特征对应一个概念的可解释方向：

\[
h = W_{\text{dec}} \cdot \text{ReLU}(W_{\text{enc}} \cdot x + b_{\text{enc}}) + b_{\text{dec}}
\]

where $W_{\text{enc}} \in \mathbb{R}^{m \times d}$ with $m \gg d$ (overcomplete basis), and the ReLU + sparsity penalty ensures only a few features activate per input.

其中 $W_{\text{enc}} \in \mathbb{R}^{m \times d}$，且 $m \gg d$（过完备基），ReLU 加稀疏惩罚确保每个输入只激活少量特征。

\paragraph{Key findings from SAE interpretability:}
\label{key-findings-from-sae-interpretability}

\paragraph{SAE 可解释性的关键发现：}
\label{key-findings-from-sae-interpretability}

\begin{itemize}
  \item Features are \emph{monosemantic}: each encodes a single human-interpretable concept (``code in Python,'' ``mentions of the Golden Gate Bridge,'' ``first-person narrative'')~\cite{bricken2023monosemanticity}.
  \item Features are \emph{steerable}: clamping a feature’s activation high/low directly controls model behaviour (e.g., forcing the ``Golden Gate Bridge'' feature on makes the model mention it in every response)~\cite{templeton2024scaling}.
  \item Features compose: complex behaviours emerge from combinations of simple features.
  \item SAEs scale: Templeton et al.~\cite{templeton2024scaling} trained SAEs with up to 34M features on Claude 3 Sonnet, finding interpretable features for safety-relevant concepts (deception, sycophancy, dangerous requests).
\end{itemize}

\begin{itemize}
  \item 特征是\emph{单义性}的：每个特征编码一个人类可解释的概念（“Python 代码”、“提到金门大桥”、“第一人称叙事”）~\cite{bricken2023monosemanticity}。
  \item 特征是\emph{可操控}的：将特征的激活值钳制在高/低水平可直接控制模型行为（例如，强制激活“金门大桥”特征会使模型在每个回复中都提到它）~\cite{templeton2024scaling}。
  \item 特征可组合：复杂的行为由简单特征的组合涌现。
  \item SAE 可扩展：Templeton 等人~\cite{templeton2024scaling} 在 Claude 3 Sonnet 上训练了具有多达 3400 万个特征的 SAE，发现了与安全相关概念（欺骗、谄媚、危险请求）的可解释特征。
\end{itemize}

\begin{keybox}[SAE Training Recipe]
\begin{enumerate}
  \item Collect activations from a specific model layer across a large corpus.
  \item Train a sparse autoencoder with $L_1$ penalty on the hidden layer: $\mathcal{L} = \|x - \hat{x}\|_2^2 + \lambda \|z\|_1$.
  \item The learned encoder directions ($W_{\text{enc}}$ rows) are candidate features.
  \item Validate: for each feature, find max-activating examples and check semantic coherence.
  \item Optionally: measure \emph{feature absorption} and \emph{dead features} to assess SAE quality.
\end{enumerate}
\end{keybox}

\begin{keybox}[SAE 训练方案]
\begin{enumerate}
  \item 从大型语料库中收集特定模型层的激活。
  \item 训练一个稀疏自编码器，对隐藏层施加 $L_1$ 惩罚：$\mathcal{L} = \|x - \hat{x}\|_2^2 + \lambda \|z\|_1$。
  \item 学习到的编码器方向（$W_{\text{enc}}$ 的行）即为候选特征。
  \item 验证：对每个特征，找到最大激活示例并检查语义一致性。
  \item 可选：测量\emph{特征吸收（feature absorption）}和\emph{死特征（dead features）}以评估 SAE 质量。
\end{enumerate}
\end{keybox}

\subsubsection{Natural Language Autoencoders (Anthropic, 2026)}
\label{natural-language-autoencoders-anthropic-2026}

\subsubsection{自然语言自编码器（Anthropic, 2026）}
\label{natural-language-autoencoders-anthropic-2026}

While SAEs decompose activations into interpretable \emph{vectors}, their features still require human inspection of max-activating examples to understand. Anthropic’s Natural Language Autoencoders (NLAEs)~\cite{anthropic2026nla} take a fundamentally different approach: they replace the sparse bottleneck with \emph{natural language descriptions}, making interpretability automatic.

虽然 SAE 将激活分解为可解释的\emph{向量}，但其特征仍需人工检查最大激活示例才能理解。Anthropic 的自然语言自编码器（NLAE）~\cite{anthropic2026nla} 采用了一种根本不同的方法：它们用\emph{自然语言描述}取代稀疏瓶颈，使可解释性自动化。

\paragraph{How NLAEs work.}
\label{how-nlaes-work.}

\paragraph{NLAE 的工作原理。}
\label{how-nlaes-work.}

\begin{enumerate}
  \item \textbf{Encoder}: A language model reads the hidden activations (or the input text) and produces a natural language description of the active concepts: e.g., ``The text discusses French cuisine and uses formal academic tone.''
  \item \textbf{Decoder}: A second language model reads the natural language description and reconstructs the original activations (or predicts the next token).
  \item \textbf{Training}: Both encoder and decoder are trained end-to-end to minimize reconstruction loss, with the bottleneck being a variable-length natural language string rather than a sparse vector.
\end{enumerate}

\begin{enumerate}
  \item \textbf{编码器（Encoder）}：一个语言模型读取隐藏激活（或输入文本），并生成对激活概念的自然语言描述：例如，“文本讨论了法国美食，并使用正式学术语气。”
  \item \textbf{解码器（Decoder）}：第二个语言模型读取自然语言描述，并重建原始激活（或预测下一个 token）。
  \item \textbf{训练（Training）}：编码器和解码器端到端地训练以最小化重构损失，瓶颈是一个可变长度的自然语言字符串，而不是稀疏向量。
\end{enumerate}

\paragraph{Advantages over SAEs.}
\label{advantages-over-saes.}

\paragraph{相比 SAE 的优势。}
\label{advantages-over-saes.}

\begin{itemize}
  \item \textbf{Self-interpreting}: Features are \emph{literally} natural language---no manual labelling needed.
  \item \textbf{Compositional}: Can express complex, relational concepts (``a sarcastic response to a factual claim'') that SAE features cannot represent as single directions.
  \item \textbf{Hierarchical}: Descriptions can capture both fine-grained (word-level) and coarse (document-level) properties in the same representation.
  \item \textbf{Auditable}: The bottleneck description is human-readable, enabling direct inspection of what information the model ``thinks'' is present.
\end{itemize}

\begin{itemize}
  \item \textbf{自解释（Self-interpreting）}：特征\emph{直接}就是自然语言——无需手动标注。
  \item \textbf{组合性（Compositional）}：能够表达复杂的、关系型的概念（例如“对事实性声明的讽刺回应”），而 SAE 特征无法作为单一方向来表示。
  \item \textbf{分层性（Hierarchical）}：描述可以在同一表示中同时捕获细粒度（词级）和粗粒度（文档级）的属性。
  \item \textbf{可审计（Auditable）}：瓶颈描述是人类可读的，从而可以直接检查模型“认为”存在哪些信息。
\end{itemize}

\paragraph{Limitations.}
\label{limitations.}

\paragraph{局限性。}
\label{limitations.}

NLAEs introduce a language-model-in-the-loop, making them computationally expensive and potentially subject to the same faithfulness concerns as any model-generated explanation. They also cannot easily represent sub-symbolic features (geometric patterns, exact numerical values) that SAEs handle naturally as activation magnitudes.

NLAE 引入了语言模型在环（language-model-in-the-loop）机制，使其计算成本高昂，并且可能面临与任何模型生成的解释相同的忠实性问题。它们还难以轻松表示亚符号特征（如几何模式、精确数值），而 SAE 可以自然地通过激活幅度来处理这些特征。

\begin{intuitionbox}[The Interpretability Stack]
Think of interpretability tools as a hierarchy:

\begin{enumerate}
  \item \textbf{Attention maps}: ``What is the model looking at?'' (cheapest, least faithful)
  \item \textbf{Probing classifiers}: ``What information is encoded at this layer?''
  \item \textbf{Sparse Autoencoders}: ``What monosemantic features are active?'' (scalable, requires human labelling)
  \item \textbf{Natural Language Autoencoders}: ``What does the model think is happening?'' (self-interpreting, expensive)
  \item \textbf{Causal tracing / patching}: ``Which components actually cause this output?'' (most faithful, most expensive)
\end{enumerate}

Each level trades off between cost, scalability, and faithfulness of explanation.
\end{intuitionbox}

\begin{intuitionbox}[可解释性堆栈]
将可解释性工具视为一个层次结构：

\begin{enumerate}
  \item \textbf{注意力图（Attention maps）}：“模型在看什么？”（最便宜，最不忠实）
  \item \textbf{探针分类器（Probing classifiers）}：“这一层编码了哪些信息？”
  \item \textbf{稀疏自编码器（Sparse Autoencoders）}：“哪些单义性特征被激活？”（可扩展，需要人工标注）
  \item \textbf{自然语言自编码器（Natural Language Autoencoders）}：“模型认为发生了什么？”（自解释，昂贵）
  \item \textbf{因果追踪/修补（Causal tracing / patching）}：“哪些组件实际上导致了这一输出？”（最忠实，最昂贵）
\end{enumerate}

每一层都在成本、可扩展性和解释忠实性之间进行权衡。
\end{intuitionbox}

\section{Prediction Heads: What Transformers Output}
\label{prediction-heads-what-transformers-output}

\section{预测头：Transformer 输出什么}
\label{prediction-heads-what-transformers-output}

The transformer body produces contextual hidden states $\mathbf{h}_t \in \mathbb{R}^d$ for each position. What we \emph{do} with these hidden states---the \textbf{prediction head}---defines the task. The same transformer backbone can serve radically different purposes simply by swapping the head.

Transformer 主体为每个位置生成上下文隐藏状态 $\mathbf{h}_t \in \mathbb{R}^d$。我们\emph{如何}处理这些隐藏状态——即\textbf{预测头（prediction head）}——决定了任务。相同的 Transformer 主干只需更换预测头即可实现截然不同的目的。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_008_prediction-heads.png}
\caption{The same transformer backbone supports different tasks by swapping the prediction head. All three heads used in this paper share identical architecture below the final projection layer.}
\label{fig:prediction-heads}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_008_prediction-heads.png}
\caption{相同的 Transformer 主干通过更换预测头支持不同的任务。本文使用的三个预测头在最终投影层之下共享相同的架构。}
\label{fig:prediction-heads}
\end{figure}

## Language Modeling Head (Pretraining)
## 语言建模头（预训练）

The standard LM head projects the final hidden state to vocabulary logits and trains with cross-entropy loss over the next token:
标准的语言模型（LM）头将最终隐藏状态投影到词汇表logits，并使用下一个token上的交叉熵损失进行训练：

\begin{equation}
P(x_{t+1} | x_{\leq t}) = \text{softmax}(\mathbf{W}_{\text{head}} \cdot \mathbf{h}_t + \mathbf{b})
\end{equation}

where $\mathbf{W}_{\text{head}} \in \mathbb{R}^{|\mathcal{V}| \times d}$ (often tied with the embedding matrix: $\mathbf{W}_{\text{head}} = \mathbf{E}^T$).
其中 $\mathbf{W}_{\text{head}} \in \mathbb{R}^{|\mathcal{V}| \times d}$（通常与嵌入矩阵共享权重：$\mathbf{W}_{\text{head}} = \mathbf{E}^T$）。

\begin{keybox}[LM Head Properties]
\begin{itemize}
  \item \textbf{Training objective}: Causal language modeling (predict next token for every position)
  \item \textbf{训练目标}：因果语言建模（预测每个位置的下一个token）
  \item \textbf{Loss}: $\mathcal{L}_{\text{LM}} = -\frac{1}{T}\sum_{t=1}^{T} \log P(x_t | x_{<t})$
  \item \textbf{损失}：$\mathcal{L}_{\text{LM}} = -\frac{1}{T}\sum_{t=1}^{T} \log P(x_t | x_{<t})$
  \item \textbf{Label}: Every token is both input (shifted right) and target (shifted left)
  \item \textbf{标签}：每个token既是输入（右移）也是目标（左移）
  \item \textbf{Used during}: Pretraining on large corpora (trillions of tokens)
  \item \textbf{使用阶段}：在大规模语料库上进行预训练（数万亿token）
  \item \textbf{Key insight}: The model learns general language understanding as a byproduct of next-token prediction
  \item \textbf{关键见解}：模型通过next-token预测的副产品来学习通用语言理解
\end{itemize}
\end{keybox}

## Conditional Generation Head (SFT / Instruction Following)
## 条件生成头（SFT / 指令遵循）

For supervised fine-tuning (SFT), the architecture is \emph{identical} to the LM head---the same linear projection to vocabulary logits. The difference is purely in \emph{what we compute loss on}:
对于监督微调（Supervised Fine-Tuning，SFT），其架构与LM头\emph{完全相同}——相同的线性投影到词汇表logits。唯一的区别在于\emph{我们在什么上面计算损失}：

\begin{equation}
\mathcal{L}_{\text{SFT}} = -\frac{1}{|y|}\sum_{t=1}^{|y|} \log P(y_t | x_{\text{prompt}}, y_{<t})
\end{equation}

\begin{keybox}[Conditional Head – Key Differences from LM Head]
\begin{itemize}
  \item \textbf{Loss masking}: Only compute loss on the \emph{response} tokens, not the prompt/instruction. The prompt provides context but no gradient signal.
  \item \textbf{损失掩码}：仅在\emph{回复}token上计算损失，而不是在提示/指令上。提示提供上下文但不提供梯度信号。
  \item \textbf{Conditioning}: The model learns to generate responses \emph{conditioned on} specific instruction formats (system prompts, user queries, tool calls).
  \item \textbf{条件化}：模型学会\emph{基于}特定指令格式（系统提示、用户查询、工具调用）生成回复。
  \item \textbf{Format tokens}: Special tokens (\texttt{<|user|>}, \texttt{<|assistant|>}) guide the model to produce structured outputs.
  \item \textbf{格式token}：特殊token（\texttt{<|user|>}、\texttt{<|assistant|>}）引导模型生成结构化输出。
  \item \textbf{Used during}: SFT on curated instruction-response pairs; also during RL policy generation (the policy head that produces actions/responses).
  \item \textbf{使用阶段}：在精选的指令-回复对上进行SFT；也用于强化学习策略生成（产生动作/回复的policy头）。
\end{itemize}
\end{keybox}

\begin{intuitionbox}[Same Head – Different Training Signal]
The LM head and SFT head are architecturally identical (same $\mathbf{W}_{\text{head}}$). The only difference is that during SFT, we mask the loss on prompt tokens. This subtle change transforms a general text predictor into a instruction-following assistant. The head learns to ``activate'' different generation modes based on the conditioning context.
\end{intuitionbox}

\begin{intuitionbox}[相同头 – 不同训练信号]
LM头和SFT头在结构上完全相同（相同的 $\mathbf{W}_{\text{head}}$）。唯一的区别在于，在SFT期间，我们掩码了提示token上的损失。这一细微变化将一个通用的文本预测器转变为一个指令遵循助手。该头学会了根据条件上下文“激活”不同的生成模式。
\end{intuitionbox}

## Value Head (Regression for RL)
## 值头（面向强化学习的回归）

In reinforcement learning (PPO, GRPO), we need to estimate \emph{how good} a state is---this requires a scalar output, not vocabulary logits. The \textbf{value head} replaces the LM projection with a simple regression layer:
在强化学习（PPO、GRPO）中，我们需要估计一个状态\emph{有多好}——这需要一个标量输出，而不是词汇表logits。\textbf{值头}将LM投影替换为一个简单的回归层：

\begin{equation}
V(s_t) = \mathbf{w}_{\text{value}}^T \cdot \mathbf{h}_t + b \in \mathbb{R}
\end{equation}

where $\mathbf{w}_{\text{value}} \in \mathbb{R}^d$ and $b \in \mathbb{R}$.
其中 $\mathbf{w}_{\text{value}} \in \mathbb{R}^d$ 且 $b \in \mathbb{R}$。

\begin{keybox}[Value Head Properties]
\begin{itemize}
  \item \textbf{Output}: Single scalar (expected cumulative reward from this state)
  \item \textbf{输出}：单个标量（从该状态期望的累积奖励）
  \item \textbf{Loss}: MSE between predicted and actual returns: $\mathcal{L}_V = \frac{1}{T}\sum_t (V(s_t) - R_t)^2$
  \item \textbf{损失}：预测收益与实际收益之间的均方误差：$\mathcal{L}_V = \frac{1}{T}\sum_t (V(s_t) - R_t)^2$
  \item \textbf{Architecture}: Linear layer $\mathbb{R}^d \to \mathbb{R}^1$ (sometimes with a small MLP: $d \to 256 \to 1$)
  \item \textbf{架构}：线性层 $\mathbb{R}^d \to \mathbb{R}^1$（有时带一个小型MLP：$d \to 256 \to 1$）
  \item \textbf{Backbone sharing}: Often shares the transformer body with the policy (with a separate value head), or uses a completely separate critic network
  \item \textbf{主干共享}：通常与策略共享Transformer主体（带独立的值头），或者使用完全独立的critic网络
  \item \textbf{Used during}: PPO advantage estimation (GAE), reward model scoring
  \item \textbf{使用阶段}：PPO优势估计（GAE）、奖励模型评分
\end{itemize}
\end{keybox}

## Head Selection Summary
## 头选择总结

\begin{table}[ht!]
\centering
\caption{Prediction heads used throughout this paper and their training contexts.}
\caption{本文使用的预测头及其训练场景。}
\begin{tabular}{@{}lp{2.5cm}p{2.8cm}p{2.8cm}p{2.8cm}@{}}
\toprule
\textbf{Head} & \textbf{Output} & \textbf{Loss} & \textbf{Stage} & \textbf{Purpose} \\
\textbf{头} & \textbf{输出} & \textbf{损失} & \textbf{阶段} & \textbf{目的} \\
\midrule
LM Head & $\mathbb{R}^{|\mathcal{V}|}$ & Cross-entropy (all tokens) & Pretraining & Learn language from raw text \\
LM头 & $\mathbb{R}^{|\mathcal{V}|}$ & 交叉熵（所有token） & 预训练 & 从原始文本学习语言 \\
Conditional Head & $\mathbb{R}^{|\mathcal{V}|}$ & Cross-entropy (response only) & SFT & Learn to follow instructions \\
条件头 & $\mathbb{R}^{|\mathcal{V}|}$ & 交叉熵（仅回复） & SFT & 学习遵循指令 \\
Value Head & $\mathbb{R}^1$ & MSE & RL (PPO) & Estimate state value for advantage \\
值头 & $\mathbb{R}^1$ & 均方误差 & 强化学习（PPO） & 估计状态价值以计算优势 \\
Reward Head & $\mathbb{R}^1$ & Pairwise ranking & RM training & Score response quality \\
奖励头 & $\mathbb{R}^1$ & 成对排序 & 奖励模型训练 & 评分回复质量 \\
\bottomrule
\end{tabular}
\end{table}

\begin{warningbox}[Head Initialization Matters]
When adding a value head to a pretrained LM, initialize it near zero (small random weights). If initialized with large values, the initial value estimates will be wildly wrong, causing huge advantages and unstable PPO updates. Common practice: initialize the final linear layer with $\mathcal{N}(0, 1/\sqrt{d})$ or simply zeros.
\end{warningbox}

\begin{warningbox}[头初始化至关重要]
当向预训练LM添加值头时，将其初始化为接近零（小的随机权重）。如果初始化为大值，初始价值估计将严重错误，导致巨大的优势和不稳定的PPO更新。常见做法：使用 $\mathcal{N}(0, 1/\sqrt{d})$ 或直接初始化为零。
\end{warningbox}

## HuggingFace Implementation
## HuggingFace实现

\begin{lstlisting}[style=pythonstyle, caption={Loading and using different prediction heads with HuggingFace.}]
from transformers import (
    AutoModelForCausalLM,          # LM head (pretraining + SFT)
    AutoModelForSequenceClassification,  # Reward head
    AutoTokenizer,
)
from trl import AutoModelForCausalLMWithValueHead  # Value head (PPO)
import torch


model_name = "meta-llama/Llama-3.1-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)


# === 1. LM Head (Pretraining / SFT) ===
# The default CausalLM model -- projects hidden states to vocab logits
lm_model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
# lm_model.lm_head: Linear(hidden_size -> vocab_size)
# Output: logits of shape (batch, seq_len, vocab_size)


inputs = tokenizer("The capital of France is", return_tensors="pt")
outputs = lm_model(**inputs)
next_token_logits = outputs.logits[:, -1, :]  # (batch, vocab_size)
probs = torch.softmax(next_token_logits, dim=-1)


# === 2. Conditional Head (SFT) ===
# Architecturally identical to LM head -- difference is in loss masking
# During SFT, we only compute loss on response tokens:
messages = [
    {"role": "user", "content": "What is 2+2?"},
    {"role": "assistant", "content": "4"},
]
formatted = tokenizer.apply_chat_template(messages, return_tensors="pt")
labels = formatted.clone()
# Mask prompt tokens (set to -100 so cross-entropy ignores them)
prompt_len = len(tokenizer.apply_chat_template(messages[:1]))
labels[:, :prompt_len] = -100
loss = lm_model(input_ids=formatted, labels=labels).loss


# === 3. Value Head (PPO Critic) ===
# Adds a Linear(hidden_size -> 1) on top of the LM backbone
value_model = AutoModelForCausalLMWithValueHead.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
# value_model.v_head: Linear(hidden_size -> 1)
# Returns both LM logits AND per-token value estimates


inputs = tokenizer("Explain quantum computing", return_tensors="pt")
lm_logits, loss, values = value_model(
    **inputs, return_dict=False
)
# values shape: (batch, seq_len, 1) -- scalar estimate per token


# === 4. Reward Head (Reward Model) ===
# Classification head: Linear(hidden_size -> 1) on last token
reward_model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=1,              # single scalar output
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
# Scores entire sequence by pooling the last token's hidden state
inputs = tokenizer("Good response here", return_tensors="pt")
reward_score = reward_model(**inputs).logits  # shape: (batch, 1)
\end{lstlisting}

\begin{intuitionbox}[Weight Tying: LM Head = Embedding Matrix Transposed]
Most modern LLMs \emph{tie} the LM head weights with the input embedding matrix: \texttt{lm\_head.weight = model.embed\_tokens.weight}. This means the LM head is \emph{not} a separately learned layer---it reuses the embedding table. Benefits: fewer parameters ($|\mathcal{V}| \times d$ saved), better generalization, and the geometric structure of the embedding space directly determines token probabilities. You can verify this in HuggingFace: \texttt{model.lm\_head.weight is model.model.embed\_tokens.weight} returns \texttt{True} for most models.
\end{intuitionbox}

\begin{intuitionbox}[权重绑定：LM头 = 嵌入矩阵转置]
大多数现代LLM将LM头的权重与输入嵌入矩阵\emph{绑定}：\texttt{lm\_head.weight = model.embed\_tokens.weight}。这意味着LM头\emph{不是}一个单独学习的层——它复用了嵌入表。好处：参数更少（节省了$|\mathcal{V}| \times d$）、泛化更好，并且嵌入空间的几何结构直接决定了token概率。你可以在HuggingFace中验证：对于大多数模型，\texttt{model.lm\_head.weight is model.model.embed\_tokens.weight}返回\texttt{True}。
\end{intuitionbox}

\newpage
\section{Optimization Theory for LLM Training}
\section{LLM训练的优化理论}
\label{optimization-theory-for-llm-training}

Training a large language model means finding the set of parameters $\theta$ (billions of weights) that minimizes the loss function $\mathcal{L}(\theta)$ --- typically the negative log-likelihood of the next token. This is an optimization problem in extraordinarily high-dimensional space, and the algorithm used to navigate this space determines whether training succeeds, diverges, or stalls.

训练大型语言模型意味着找到一组参数$\theta$（数十亿个权重），使损失函数$\mathcal{L}(\theta)$最小化——通常是下一个token的负对数似然。这是一个在极高维空间中的优化问题，而用于导航该空间的算法决定了训练是成功、发散还是停滞。

\subsection{Gradient Descent: The Foundation}
\subsection{梯度下降：基础}
\label{gradient-descent-the-foundation}

\paragraph{What is a Gradient?}
\paragraph{什么是梯度？}
\label{what-is-a-gradient}

The gradient $\nabla_\theta \mathcal{L}$ is a vector that points in the direction of \emph{steepest increase} of the loss. Each component $\frac{\partial \mathcal{L}}{\partial \theta_i}$ tells us how much the loss would change if we slightly increased parameter $\theta_i$. To \emph{decrease} the loss, we move in the opposite direction:

梯度$\nabla_\theta \mathcal{L}$是一个指向损失\emph{最陡增加}方向的向量。每个分量$\frac{\partial \mathcal{L}}{\partial \theta_i}$告诉我们如果稍微增加参数$\theta_i$，损失会变化多少。为了\emph{减小}损失，我们向相反方向移动：

\begin{equation}
\theta_{t+1} = \theta_t - \eta \nabla_\theta \mathcal{L}(\theta_t)
\end{equation}

where $\eta > 0$ is the \textbf{learning rate} --- the step size. This is \textbf{gradient descent}~\cite{rumelhart1986learning}.

其中$\eta > 0$是\textbf{学习率}——步长。这就是\textbf{梯度下降}~\cite{rumelhart1986learning}。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.7\textwidth]{figures/fig_009_fig9.png}
\caption{Gradient descent: starting from a random initialization $\theta_0$, each step moves the parameters in the direction that reduces the loss, with step size controlled by the learning rate $\eta$. The process converges toward a (local) minimum.}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.7\textwidth]{figures/fig_009_fig9.png}
\caption{梯度下降：从随机初始化$\theta_0$开始，每一步将参数向减少损失的方向移动，步长由学习率$\eta$控制。该过程收敛到（局部）最小值。}
\end{figure}

\paragraph{Why Full Gradient Descent is Impractical.}
\paragraph{为什么全批量梯度下降不可行。}
\label{why-full-gradient-descent-is-impractical.}

Computing the exact gradient requires evaluating the loss over the \emph{entire} training dataset (trillions of tokens for LLMs). This is computationally prohibitive --- a single gradient step would require a full pass over all data.

计算精确梯度需要对\emph{整个}训练数据集（对于LLM来说是数万亿个token）评估损失。这在计算上是不可行的——单个梯度步骤需要对所有数据进行一次完整遍历。

\paragraph{Stochastic Gradient Descent (SGD).}
\paragraph{随机梯度下降（SGD）。}
\label{stochastic-gradient-descent-sgd.}

The solution: estimate the gradient from a small random subset (\textbf{mini-batch}) of the data~\cite{robbins1951stochastic}: 
\[
\nabla_\theta \mathcal{L}(\theta) \approx \frac{1}{B}\sum_{i=1}^{B} \nabla_\theta \ell(\theta; x_i)
\]
 where $B$ is the batch size (typically 1K--4M tokens for LLMs). The mini-batch gradient is a \emph{noisy but unbiased} estimate of the true gradient.

解决方案：从数据的一个小的随机子集（\textbf{小批量}）估计梯度~\cite{robbins1951stochastic}：
\[
\nabla_\theta \mathcal{L}(\theta) \approx \frac{1}{B}\sum_{i=1}^{B} \nabla_\theta \ell(\theta; x_i)
\]
其中$B$是批量大小（对于LLM通常是1K--4M个token）。小批量梯度是真实梯度的\emph{有噪声但无偏}的估计。

\begin{keybox}[Why Mini-Batch SGD Works]
\begin{itemize}
  \item \textbf{Computational efficiency}: Each step costs $O(B)$ instead of $O(N_{\text{total}})$. With $B = 4096$ tokens and 15T total tokens, each step is $\sim$4 billion$\times$ cheaper.
  \item \textbf{Noise as regularization}: The stochastic noise helps escape sharp local minima, finding flatter regions that generalize better.
  \item \textbf{GPU utilization}: Mini-batches are large enough to saturate GPU parallelism (matrix multiplications become compute-bound rather than memory-bound).
  \item \textbf{Convergence}: Theoretically converges to a local minimum at rate $O(1/\sqrt{T})$ (slower than exact GD’s $O(1/T)$, but each step is millions of times cheaper).
\end{itemize}
\end{keybox}

\begin{keybox}[为什么小批量SGD有效]
\begin{itemize}
  \item \textbf{计算效率}：每一步的代价是$O(B)$而不是$O(N_{\text{total}})$。当$B = 4096$个token且总token数为15T时，每一步便宜约40亿倍。
  \item \textbf{噪声作为正则化}：随机噪声有助于逃离尖锐的局部最小值，找到泛化更好的平坦区域。
  \item \textbf{GPU利用率}：小批量足够大，可以饱和GPU并行度（矩阵乘法变成计算密集型而非内存密集型）。
  \item \textbf{收敛性}：理论上以$O(1/\sqrt{T})$的速率收敛到局部最小值（比精确GD的$O(1/T)$慢，但每一步便宜数百万倍）。
\end{itemize}
\end{keybox}

\paragraph{From SGD to Adaptive Methods.}
\paragraph{从SGD到自适应方法。}
\label{from-sgd-to-adaptive-methods.}

While SGD with momentum works well for vision models (CNNs), LLM training requires \textbf{adaptive optimizers} --- algorithms that maintain a per-parameter learning rate.

虽然带动量的SGD在视觉模型（CNN）上效果很好，但LLM训练需要\textbf{自适应优化器}——为每个参数维护一个学习率的算法。

\subsection{Why Vanilla SGD Fails for LLMs}
\subsection{为什么普通SGD对LLM失败}
\label{why-vanilla-sgd-fails-for-llms}

Stochastic Gradient Descent updates weights as: 
\[
\theta_{t+1} = \theta_t - \eta \nabla_\theta \mathcal{L}(\theta_t)
\]

随机梯度下降按如下方式更新权重：
\[
\theta_{t+1} = \theta_t - \eta \nabla_\theta \mathcal{L}(\theta_t)
\]

\begin{warningbox}[SGD Problems for LLMs]
\begin{itemize}
  \item \textbf{Different gradient scales per layer:} Early layers in a transformer have much smaller gradients than later layers (vanishing gradients). A single learning rate $\eta$ is too large for some parameters and too small for others.
  \item \textbf{Sparse gradients:} Embedding layers receive gradients only for tokens in the current batch. Most embedding rows have zero gradient. SGD with momentum wastes momentum on zero-gradient rows.
  \item \textbf{Saddle points:} High-dimensional loss landscapes have many saddle points. SGD can stall; adaptive methods escape faster.
  \item \textbf{Sensitivity to learning rate:} SGD requires careful tuning; a 2$\times$ change in $\eta$ can cause divergence.
\end{itemize}
\end{warningbox}

\begin{warningbox}[SGD对LLM的问题]
\begin{itemize}
  \item \textbf{每层梯度规模不同：}Transformer中的早期层梯度比后期层小得多（梯度消失）。单一学习率$\eta$对某些参数太大，对另一些参数太小。
  \item \textbf{稀疏梯度：}嵌入层只接收当前批量中token的梯度。大多数嵌入行梯度为零。带动量的SGD在零梯度行上浪费动量。
  \item \textbf{鞍点：}高维损失景观中有许多鞍点。SGD可能会停滞；自适应方法能更快逃离。
  \item \textbf{对学习率敏感：}SGD需要仔细调参；$\eta$变化2倍可能导致发散。
\end{itemize}
\end{warningbox}

\subsection{Adam -- Adaptive Moment Estimation}
\subsection{Adam——自适应矩估计}
\label{adam-adaptive-moment-estimation}

Adam~\cite{kingma2015adam} maintains per-parameter estimates of the first moment (mean of gradients) and second moment (uncentered variance of gradients).

Adam~\cite{kingma2015adam}维护每个参数的一阶矩（梯度的均值）和二阶矩（梯度的非中心方差）的估计。

\begin{keybox}[Adam Update Equations]
Given gradient $g_t = \nabla_\theta \mathcal{L}(\theta_t)$, hyperparameters $\beta_1, \beta_2, \epsilon, \eta$:

\begin{keybox}[Adam更新方程]
给定梯度$g_t = \nabla_\theta \mathcal{L}(\theta_t)$，超参数$\beta_1, \beta_2, \epsilon, \eta$：

\textbf{Step 1 -- Update biased first moment estimate:} 
\[
m_t = \beta_1 m_{t-1} + (1 - \beta_1) g_t
\]

\textbf{步骤1——更新有偏一阶矩估计：}
\[
m_t = \beta_1 m_{t-1} + (1 - \beta_1) g_t
\]

\textbf{Step 2 -- Update biased second moment estimate:} 
\[
v_t = \beta_2 v_{t-1} + (1 - \beta_2) g_t^2
\]

\textbf{步骤2——更新有偏二阶矩估计：}
\[
v_t = \beta_2 v_{t-1} + (1 - \beta_2) g_t^2
\]

\textbf{Step 3 -- Bias correction:} 
\[
\hat{m}_t = \frac{m_t}{1 - \beta_1^t}, \qquad \hat{v}_t = \frac{v_t}{1 - \beta_2^t}
\]

\textbf{步骤3——偏差校正：}
\[
\hat{m}_t = \frac{m_t}{1 - \beta_1^t}, \qquad \hat{v}_t = \frac{v_t}{1 - \beta_2^t}
\]

\textbf{Step 4 -- Parameter update:} 
\[
\theta_{t+1} = \theta_t - \eta \cdot \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}
\]

\textbf{步骤4——参数更新：}
\[
\theta_{t+1} = \theta_t - \eta \cdot \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}
\]

\textbf{Typical values:} $\beta_1 = 0.9$, $\beta_2 = 0.95$ or $0.999$, $\epsilon = 10^{-8}$, $\eta = 10^{-4}$ to $10^{-5}$.
\end{keybox}

\textbf{典型值：} $\beta_1 = 0.9$, $\beta_2 = 0.95$ 或 $0.999$, $\epsilon = 10^{-8}$, $\eta = 10^{-4}$ 到 $10^{-5}$。
\end{keybox}

\newpage
\begin{intuitionbox}[What Each Term Does]
\begin{itemize}
  \item $m_t$ (\textbf{momentum}): Exponential moving average of gradients. Smooths out noisy gradient estimates. $\beta_1 = 0.9$ means the current gradient contributes 10\% and the history contributes 90\%.
  \item $v_t$ (\textbf{adaptive LR}): EMA of squared gradients. Parameters with consistently large gradients get a smaller effective learning rate ($\eta / \sqrt{v_t}$). Parameters with small gradients get a larger effective LR. This is the key to handling different gradient scales per layer.
  \item $\hat{m}_t, \hat{v}_t$ (\textbf{bias correction}): At $t=1$, $m_1 = (1-\beta_1)g_1$ is much smaller than the true mean. Dividing by $(1-\beta_1^t)$ corrects this initialization bias. Without it, early steps are too small.
  \item $\epsilon$ (\textbf{numerical stability}): Prevents division by zero. Also acts as a floor on the effective learning rate.
\end{itemize}
\end{intuitionbox}

\begin{intuitionbox}[每个项的作用]
\begin{itemize}
  \item $m_t$（\textbf{动量}）：梯度的指数移动平均。平滑有噪声的梯度估计。$\beta_1 = 0.9$意味着当前梯度贡献10%，历史贡献90%。
  \item $v_t$（\textbf{自适应学习率}）：平方梯度的指数移动平均。梯度持续大的参数获得较小的有效学习率（$\eta / \sqrt{v_t}$）。梯度小的参数获得较大的有效学习率。这是处理每层不同梯度规模的关键。
  \item $\hat{m}_t, \hat{v}_t$（\textbf{偏差校正}）：在$t=1$时，$m_1 = (1-\beta_1)g_1$远小于真实均值。除以$(1-\beta_1^t)$校正了这种初始化偏差。没有它，早期步长会太小。
  \item $\epsilon$（\textbf{数值稳定性}）：防止除零。同时也作为有效学习率的下限。
\end{itemize}
\end{intuitionbox}

\subsection{AdamW -- Decoupled Weight Decay}
\subsection{AdamW——解耦权重衰减}
\label{adamw-decoupled-weight-decay}

AdamW~\cite{loshchilov2019adamw} fixes a subtle but important issue with how weight decay interacts with adaptive optimizers.

AdamW~\cite{loshchilov2019adamw}修复了一个微妙但重要的问题，即权重衰减与自适应优化器的交互方式。

\begin{keybox}[Why L2 Regularization $\neq$ Weight Decay in Adam]
With L2 regularization, the loss becomes $\mathcal{L} + \frac{\lambda}{2}\|\theta\|^2$, so the gradient is $g_t + \lambda \theta_t$. In Adam, this regularization gradient is \emph{scaled by the adaptive factor} $1/\sqrt{\hat{v}_t}$: 
\[
\theta_{t+1} = \theta_t - \eta \cdot \frac{\hat{m}_t + \lambda \theta_t}{\sqrt{\hat{v}_t} + \epsilon}
\]
 Parameters with large $v_t$ (large gradient variance) get \emph{less} regularization. This is not what we want -- weight decay should be uniform.
\end{keybox}

\begin{keybox}[为什么L2正则化 $\neq$ Adam中的权重衰减]
使用L2正则化时，损失变为$\mathcal{L} + \frac{\lambda}{2}\|\theta\|^2$，因此梯度为$g_t + \lambda \theta_t$。在Adam中，这个正则化梯度被自适应因子$1/\sqrt{\hat{v}_t}$\emph{缩放}：
\[
\theta_{t+1} = \theta_t - \eta \cdot \frac{\hat{m}_t + \lambda \theta_t}{\sqrt{\hat{v}_t} + \epsilon}
\]
具有大$v_t$（大梯度方差）的参数获得的\emph{更少}的正则化。这不是我们想要的——权重衰减应该是均匀的。
\end{keybox}

\begin{keybox}[AdamW – Decoupled Weight Decay]
\begin{keybox}[AdamW – 解耦权重衰减]

AdamW (Loshchilov \& Hutter, 2017) applies weight decay \emph{directly} to the parameters, outside the adaptive scaling: 
AdamW（Loshchilov \& Hutter, 2017）将权重衰减 \emph{直接} 应用于参数，独立于自适应缩放：

\[
\theta_{t+1} = \theta_t - \eta \cdot \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}
  - \eta \lambda \theta_t
\]

The weight decay term $\eta \lambda \theta_t$ is not divided by $\sqrt{\hat{v}_t}$. This gives uniform regularization across all parameters regardless of their gradient history.
权重衰减项 $\eta \lambda \theta_t$ 不会被 $\sqrt{\hat{v}_t}$ 除。这使得所有参数获得统一的正则化，与它们的梯度历史无关。

\textbf{Typical value:} $\lambda = 0.1$ for LLM training.
\textbf{典型值：} LLM 训练中 $\lambda = 0.1$。
\end{keybox}


\begin{warningbox}[Always Use AdamW – Never Plain Adam – for LLMs]
\begin{warningbox}[LLM 训练始终使用 AdamW – 切勿使用普通 Adam]

The difference between Adam and AdamW is subtle but matters. With Adam + L2, the effective weight decay is stronger for parameters with small gradient variance (e.g., biases, LayerNorm parameters) and weaker for parameters with large gradient variance (e.g., attention weights). AdamW gives the intended uniform regularization. Most frameworks default to AdamW; double-check your optimizer class.
Adam 与 AdamW 的差异虽细微但至关重要。使用 Adam + L2 时，梯度方差较小的参数（如偏置、LayerNorm 参数）的有效权重衰减更强，而梯度方差较大的参数（如注意力权重）则更弱。AdamW 实现了预期的统一正则化。大多数框架默认使用 AdamW；请务必检查你的优化器类。
\end{warningbox}


\newpage
\subsection{Learning Rate -- The Most Important Hyperparameter}
\subsection{学习率——最重要的超参数}
\label{learning-rate-the-most-important-hyperparameter}


\begin{keybox}[Typical Learning Rates by Training Phase]
\begin{keybox}[各训练阶段的典型学习率]
\begin{tabular}{@{}lp{4cm}p{5.5cm}@{}}
\toprule
\textbf{Phase} & \textbf{Typical LR} & \textbf{Notes} \\
\textbf{阶段} & \textbf{典型学习率} & \textbf{说明} \\
\midrule
Pretraining (from scratch) & $1\text{e-}4$ to $3\text{e-}4$ & Large model, large batch \\
预训练（从头开始） & $1\text{e-}4$ 至 $3\text{e-}4$ & 大模型，大批量 \\
Continued pretraining & $1\text{e-}5$ to $1\text{e-}4$ & Smaller LR to preserve knowledge \\
继续预训练 & $1\text{e-}5$ 至 $1\text{e-}4$ & 较小学习率以保留知识 \\
SFT (supervised fine-tune) & $1\text{e-}5$ to $2\text{e-}5$ & Standard range \\
SFT（监督微调） & $1\text{e-}5$ 至 $2\text{e-}5$ & 标准范围 \\
LoRA fine-tuning & $1\text{e-}4$ to $3\text{e-}4$ & Higher LR for adapter weights \\
LoRA 微调 & $1\text{e-}4$ 至 $3\text{e-}4$ & 适配器权重使用较高学习率 \\
\bottomrule
\end{tabular}


\smallskip
\noindent\emph{For RL learning rates (PPO, DPO, GRPO) see §\ref{sec:rl-optimizer-config}.}
\noindent\emph{关于强化学习率（PPO、DPO、GRPO），参见第 §\ref{sec:rl-optimizer-config} 节。}
\end{keybox}


\subsection{Learning Rate Warmup}
\subsection{学习率预热}
\label{learning-rate-warmup}


\begin{keybox}[Why Warmup is Necessary]
\begin{keybox}[为什么需要预热]
At the start of training, $v_t$ (the second moment estimate) is initialized to zero. After bias correction: $\hat{v}_t = v_t / (1 - \beta_2^t)$. At $t=1$ with $\beta_2 = 0.999$: $\hat{v}_1 = v_1 / (1 - 0.999) = 1000 v_1$. This means the effective learning rate is $\eta / \sqrt{1000 v_1}$ -- much smaller than intended.
训练开始时，$v_t$（二阶矩估计）初始化为零。经过偏差校正后：$\hat{v}_t = v_t / (1 - \beta_2^t)$。当 $t=1$ 且 $\beta_2 = 0.999$ 时：$\hat{v}_1 = v_1 / (1 - 0.999) = 1000 v_1$。这意味着有效学习率为 $\eta / \sqrt{1000 v_1}$ —— 远小于预期值。

However, if the first gradient is unusually large (common at initialization), the second moment estimate can be dominated by this outlier, causing erratic early steps. Warmup mitigates this by starting with a very small LR and gradually increasing it, giving $v_t$ time to accumulate a reliable estimate.
然而，如果第一个梯度异常大（这在初始化时很常见），二阶矩估计可能会被这个异常值主导，导致早期步骤不稳定。预热通过从一个非常小的学习率开始并逐渐增加来缓解这一问题，使 $v_t$ 有时间累积一个可靠的估计。
\end{keybox}


\begin{itemize}
  \item \textbf{Linear warmup:} $\eta_t = \eta_{\max} \times t / T_{\text{warmup}}$
  \item \textbf{线性预热：} $\eta_t = \eta_{\max} \times t / T_{\text{warmup}}$
  \item \textbf{Typical warmup duration:} 1--5\% of total steps for pretraining; 3--10\% for fine-tuning (shorter runs need proportionally more warmup)
  \item \textbf{典型预热时长：} 预训练为总步数的 1--5%；微调为 3--10%（较短运行需要按比例增加预热）
  \item \textbf{For SFT:} 50--200 warmup steps is typical
  \item \textbf{对于 SFT：} 典型为 50--200 预热步
\end{itemize}


\subsection{Learning Rate Schedules}
\subsection{学习率调度}
\label{learning-rate-schedules}


\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_010_fig10.png}
\caption{Common learning rate schedules. All include a linear warmup phase. WSD (Warmup-Stable-Decay) is the emerging standard for pretraining.}
\caption{常见学习率调度。所有调度都包含线性预热阶段。WSD（预热-稳定-衰减）正在成为预训练的行业标准。}
\end{figure}


\paragraph{(a) Constant.}
\paragraph{(a) 常数。}
\label{a-constant.}


Simplest schedule. Good for short fine-tuning runs where you want to avoid over-decaying the LR. Risk: no annealing means the model may not converge to the sharpest minimum.
最简单的调度。适用于希望避免学习率过度衰减的短时微调。风险：没有退火意味着模型可能不会收敛到最尖锐的最小值。


\paragraph{(b) Cosine Decay.}
\paragraph{(b) 余弦衰减。}
\label{b-cosine-decay.}


\[
\eta_t = \eta_{\min} + \frac{1}{2}(\eta_{\max} - \eta_{\min})
  \left(1 + \cos\!\left(\frac{t - T_{\text{warmup}}}{T - T_{\text{warmup}}} \pi\right)\right)
\]
 Standard for pretraining and SFT. Smooth decay avoids abrupt LR changes. $\eta_{\min}$ is typically $\eta_{\max} / 10$.
预训练和 SFT 的标准选择。平滑衰减避免了学习率的突变。$\eta_{\min}$ 通常为 $\eta_{\max} / 10$。


\paragraph{(c) Linear Decay.}
\paragraph{(c) 线性衰减。}
\label{c-linear-decay.}


Simpler than cosine, similar empirical results. Preferred when you want predictable LR at any step.
比余弦更简单，经验结果相似。当你希望在任何步骤都有可预测的学习率时，优先选择。


\paragraph{(d) WSD -- Warmup-Stable-Decay.}
\paragraph{(d) WSD——预热-稳定-衰减。}
\label{d-wsd-warmup-stable-decay.}


The new standard for large-scale pretraining~\cite{hu2024minicpm, grattafiori2024llama3}. Three phases:
大规模预训练的新标准~\cite{hu2024minicpm, grattafiori2024llama3}。包含三个阶段：

\begin{enumerate}
  \item \textbf{Warmup:} Linear ramp to $\eta_{\max}$ (1--5\% of steps)
  \item \textbf{预热：} 线性增加到 $\eta_{\max}$（占步数的 1--5%）
  \item \textbf{Stable:} Constant $\eta_{\max}$ for the majority of training
  \item \textbf{稳定阶段：} 大部分训练过程保持恒定 $\eta_{\max}$
  \item \textbf{Decay:} Fast cosine or linear decay to $\eta_{\min}$ (last 10--20\% of steps)
  \item \textbf{衰减阶段：} 快速余弦或线性衰减至 $\eta_{\min}$（最后 10--20% 的步数）
\end{enumerate}


Key advantage: the stable phase allows checkpointing at any point and continuing training. The decay phase can be applied at the end of any run.
关键优势：稳定阶段允许在任何点进行检查点保存并继续训练。衰减阶段可以在任何训练运行的末尾应用。


\paragraph{(e) Cosine with Restarts (SGDR).}
\paragraph{(e) 带重启的余弦（SGDR）。}
\label{e-cosine-with-restarts-sgdr.}


Periodic restarts reset the LR to $\eta_{\max}$. Can help escape local minima. Less common for LLMs; more useful for smaller models.
周期性重启将学习率重置为 $\eta_{\max}$。有助于逃离局部最小值。在 LLM 中不太常见；对较小模型更有用。


\subsection{Gradient Clipping}
\subsection{梯度裁剪}
\label{gradient-clipping}


\begin{keybox}[Gradient Clipping]
\begin{keybox}[梯度裁剪]
Gradient clipping rescales the gradient if its global norm exceeds a threshold: 
梯度裁剪会在梯度的全局范数超过阈值时重新缩放梯度：
\[
g_t \leftarrow g_t \cdot \min\!\left(1,\; \frac{\tau}{\|g_t\|_2}\right)
\]
 where $\tau$ is \texttt{max\_grad\_norm} (typically 1.0).
其中 $\tau$ 为 \texttt{max\_grad\_norm}（通常为 1.0）。
\end{keybox}


\begin{intuitionbox}[Gradient Clipping vs. LR Reduction]
\begin{intuitionbox}[梯度裁剪 vs. 降低学习率]
Gradient clipping and reducing the learning rate both limit the size of parameter updates. The difference: clipping preserves the \emph{direction} of the gradient (just scales the magnitude), while a smaller LR scales all updates uniformly. Clipping is better for handling occasional large gradients without slowing down normal training steps.
梯度裁剪和降低学习率都限制了参数更新的幅度。区别在于：裁剪保留了梯度的 \emph{方向}（仅缩放大小），而较小的学习率均匀缩放所有更新。裁剪更适合处理偶尔出现的大梯度，同时不拖慢正常训练步。
\end{intuitionbox}


\subsubsection{Putting It Together: HuggingFace Optimizer Configuration}
\subsubsection{综合应用：HuggingFace 优化器配置}
\label{putting-it-together-huggingface-optimizer-configuration}


The following snippet shows how the concepts from this section---AdamW with decoupled weight decay (§1.6.6), cosine learning-rate scheduling with linear warmup (§1.6.7), and gradient clipping (§1.6.8)---come together in practice using the HuggingFace \texttt{transformers} library.
以下代码片段展示了本节的概念——解耦权重衰减的 AdamW（第 1.6.6 节）、带线性预热的余弦学习率调度（第 1.6.7 节）和梯度裁剪（第 1.6.8 节）——如何通过 HuggingFace \texttt{transformers} 库在实践中组合使用。

\begin{lstlisting}[style=pythonstyle, caption={Complete optimizer configuration combining AdamW -- cosine schedule -- and gradient clipping.}]
\begin{lstlisting}[style=pythonstyle, caption={完整的优化器配置：结合 AdamW、余弦调度和梯度裁剪。}]
from transformers import TrainingArguments, Trainer
from transformers import get_cosine_schedule_with_warmup
import torch


# --- Option 1: Using TrainingArguments (recommended) ---
# --- 选项 1：使用 TrainingArguments（推荐） ---
training_args = TrainingArguments(
    output_dir="./checkpoints",

    # AdamW optimizer (decoupled weight decay, S1.6.6)
    # AdamW 优化器（解耦权重衰减，第 1.6.6 节）
    optim="adamw_torch",
    learning_rate=2e-5,           # peak LR after warmup
                                  # 预热后的峰值学习率
    adam_beta1=0.9,               # first moment decay
                                  # 一阶矩衰减
    adam_beta2=0.999,             # second moment decay
                                  # 二阶矩衰减
    adam_epsilon=1e-8,            # numerical stability
                                  # 数值稳定性
    weight_decay=0.01,           # decoupled L2 penalty
                                  # 解耦 L2 惩罚

    # Learning rate schedule (S1.6.7)
    # 学习率调度（第 1.6.7 节）
    lr_scheduler_type="cosine",  # cosine decay to 0
                                 # 余弦衰减至 0
    warmup_ratio=0.1,            # 10% of steps = linear warmup
                                 # 10% 的步数 = 线性预热

    # Gradient clipping (S1.6.8)
    # 梯度裁剪（第 1.6.8 节）
    max_grad_norm=1.0,           # clip by global L2 norm
                                 # 按全局 L2 范数裁剪

    # Mixed precision (S1.6.9)
    # 混合精度（第 1.6.9 节）
    bf16=True,                   # use BFloat16 on Ampere+ GPUs
                                 # 在 Ampere+ GPU 上使用 BFloat16

    # Training duration
    # 训练时长
    num_train_epochs=3,
    per_device_train_batch_size=8,
    gradient_accumulation_steps=4,  # effective batch = 8*4 = 32
                                     # 有效批量 = 8*4 = 32
)


trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)
trainer.train()


# --- Option 2: Manual control (for custom training loops) ---
# --- 选项 2：手动控制（用于自定义训练循环） ---
from torch.optim import AdamW


# Separate weight-decay groups (don't regularize biases/norms)
# 分离权重衰减组（不对偏置/归一化层进行正则化）
no_decay = ["bias", "LayerNorm.weight", "layernorm.weight"]
param_groups = [
    {
        "params": [p for n, p in model.named_parameters()
                   if not any(nd in n for nd in no_decay)],
        "weight_decay": 0.01,
    },
    {
        "params": [p for n, p in model.named_parameters()
                   if any(nd in n for nd in no_decay)],
        "weight_decay": 0.0,
    },
]


optimizer = AdamW(param_groups, lr=2e-5, betas=(0.9, 0.999))
```

```markdown
# Cosine schedule with linear warmup
# 余弦调度与线性预热

```python
total_steps = len(train_dataloader) * num_epochs
warmup_steps = int(0.1 * total_steps)
scheduler = get_cosine_schedule_with_warmup(
    optimizer,
    num_warmup_steps=warmup_steps,
    num_training_steps=total_steps,
)
```

```python
total_steps = len(train_dataloader) * num_epochs
warmup_steps = int(0.1 * total_steps)
scheduler = get_cosine_schedule_with_warmup(
    optimizer,
    num_warmup_steps=warmup_steps,
    num_training_steps=total_steps,
)
```

# Training loop with gradient clipping
# 带梯度裁剪的训练循环

```python
for batch in train_dataloader:
    outputs = model(**batch)
    loss = outputs.loss
    loss.backward()

    # Clip gradients before optimizer step
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

    optimizer.step()
    scheduler.step()
    optimizer.zero_grad()
```

```python
for batch in train_dataloader:
    outputs = model(**batch)
    loss = outputs.loss
    loss.backward()

    # 在优化器步骤前裁剪梯度
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

    optimizer.step()
    scheduler.step()
    optimizer.zero_grad()
```

\end{lstlisting}

\begin{keybox}[Practical Tips]
\begin{itemize}
  \item \textbf{Weight decay exclusion}: bias terms and layer-norm weights should not be regularized---they have few parameters and regularizing them hurts performance \cite{loshchilov2019adamw}.
  \item \textbf{Warmup ratio}: 5--10\% of total steps is standard; too little warmup with a high LR can destabilize early training.
  \item \textbf{Gradient accumulation}: simulates larger batches on limited GPU memory; clipping applies to the \emph{accumulated} gradient.
  \item \textbf{BF16 vs.~FP16}: prefer \texttt{bf16=True} on Ampere+ GPUs (wider dynamic range avoids loss scaling); fall back to \texttt{fp16=True} on older hardware.
\end{itemize}
\end{keybox}

\begin{keybox}[实用技巧]
\begin{itemize}
  \item \textbf{权重衰减排除}: 偏置项和层归一化权重不应进行正则化——它们的参数很少，正则化会损害性能 \cite{loshchilov2019adamw}.
  \item \textbf{预热比例}: 总步数的5-10%是标准；预热过少且学习率过高会破坏早期训练的稳定性。
  \item \textbf{梯度累积}: 在有限的GPU内存上模拟更大的批次；裁剪应用于\emph{累积}梯度。
  \item \textbf{BF16 vs.~FP16}: 在Ampere+ GPU上优先使用 \texttt{bf16=True}（更宽的动态范围避免了损失缩放）；在较旧硬件上回退到 \texttt{fp16=True}.
\end{itemize}
\end{keybox}

\subsection{Mixed Precision Training}
\subsection{混合精度训练}

\label{mixed-precision-training}

\begin{keybox}[BF16 vs. FP16]
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{4cm}@{}}
\toprule
\textbf{Format} & \textbf{Exponent bits} & \textbf{Mantissa bits} & \textbf{Dynamic range} \\
\midrule
FP32 & 8 & 23 & $\sim 10^{-38}$ to $10^{38}$ \\
BF16 & 8 & 7 & Same as FP32 (same exponent) \\
FP16 & 5 & 10 & $\sim 6 \times 10^{-5}$ to $65504$ \\
\bottomrule
\end{tabular}
\end{keybox}

\begin{keybox}[BF16 vs. FP16]
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{4cm}@{}}
\toprule
\textbf{格式} & \textbf{指数位} & \textbf{尾数位} & \textbf{动态范围} \\
\midrule
FP32 & 8 & 23 & $\sim 10^{-38}$ 至 $10^{38}$ \\
BF16 & 8 & 7 & 与FP32相同（指数相同） \\
FP16 & 5 & 10 & $\sim 6 \times 10^{-5}$ 至 $65504$ \\
\bottomrule
\end{tabular}
\end{keybox}

\begin{intuitionbox}[BF16 Over FP16: Why Range Beats Precision in LLM Training]
BF16 has the same exponent range as FP32, so it can represent the same range of values (just with less precision in the mantissa). FP16 has a much smaller dynamic range -- gradients or activations that exceed 65504 cause overflow (NaN/Inf). This is why FP16 training requires \emph{loss scaling} (multiplying the loss by a large constant to keep gradients in FP16 range), while BF16 training typically does not. A100 and H100 support BF16 natively; use BF16 unless you have a specific reason for FP16.
\end{intuitionbox}

\begin{intuitionbox}[BF16优于FP16：为什么在LLM训练中范围胜过精度]
BF16具有与FP32相同的指数范围，因此它可以表示相同范围的值（只是尾数精度较低）。FP16的动态范围小得多——超过65504的梯度或激活会导致溢出（NaN/Inf）。这就是为什么FP16训练需要\emph{损失缩放}（将损失乘以一个大常数以保持梯度在FP16范围内），而BF16训练通常不需要。A100和H100原生支持BF16；除非有特定原因使用FP16，否则请使用BF16。
\end{intuitionbox}

\paragraph{Loss Scaling (FP16 only).}
\paragraph{损失缩放（仅FP16）}

\label{loss-scaling-fp16-only.}

\begin{enumerate}
  \item Multiply loss by scale factor $S$ (e.g., $S = 2^{15}$)
  \item Compute gradients in FP16 (scaled by $S$)
  \item Before optimizer step, divide gradients by $S$
  \item Check for overflow (NaN/Inf); if found, skip step and reduce $S$
  \item If no overflow for $N$ consecutive steps, increase $S$
\end{enumerate}

\begin{enumerate}
  \item 将损失乘以缩放因子 $S$（例如 $S = 2^{15}$）
  \item 在FP16中计算梯度（已缩放 $S$）
  \item 在优化器步骤前，将梯度除以 $S$
  \item 检查溢出（NaN/Inf）；如果发现，跳过该步骤并降低 $S$
  \item 如果连续 $N$ 步没有溢出，则增加 $S$
\end{enumerate}

\paragraph{FP32 Master Weights.}
\paragraph{FP32主权重}

\label{fp32-master-weights.}

In mixed precision training, weights are stored in FP32 (master copy) and cast to BF16/FP16 for the forward/backward pass. The optimizer step is done in FP32. This is important because:

在混合精度训练中，权重以FP32（主副本）存储，并在前向/反向传播中转换为BF16/FP16。优化器步骤在FP32中完成。这很重要，因为：

\begin{itemize}
  \item Small gradient updates ($\Delta\theta \ll \theta$) would be lost in BF16 precision (7 mantissa bits $\approx$ 0.8\% relative precision)
  \item FP32 master weights ensure accurate accumulation of small updates over many steps
  \item Memory cost: 2$\times$ weight storage (FP32 + BF16 copy)
\end{itemize}

\begin{itemize}
  \item 小的梯度更新 ($\Delta\theta \ll \theta$) 会在BF16精度中丢失（7位尾数 $\approx$ 0.8%的相对精度）
  \item FP32主权重确保小更新在多个步骤中的准确累积
  \item 内存成本：2倍权重存储（FP32 + BF16副本）
\end{itemize}

\begin{warningbox}[When FP32 Master Weights Are Critical]
FP32 master weights are most important for:

\begin{itemize}
  \item Long training runs (many small gradient steps accumulate)
  \item Small learning rates (updates are tiny relative to weight magnitude)
\end{itemize}

For short SFT runs with large LR, BF16-only training (no FP32 master weights) often works fine and saves memory. For RL training, FP32 master weights are essential---see §\ref{sec:rl-optimizer-config}.
\end{warningbox}

\begin{warningbox}[何时需要FP32主权重]
FP32主权重在以下情况下最为重要：

\begin{itemize}
  \item 长时间训练运行（许多小梯度步骤累积）
  \item 小学习率（更新相对于权重幅度很小）
\end{itemize}

对于使用大学习率的短SFT运行，仅使用BF16训练（无FP32主权重）通常效果良好并节省内存。对于强化学习训练，FP32主权重是必不可少的——参见§\ref{sec:rl-optimizer-config}.
\end{warningbox}

\subsubsection{Mixed Precision in Practice: HuggingFace}
\subsubsection{混合精度实践：HuggingFace}

\label{mixed-precision-in-practice-huggingface}

\begin{lstlisting}[style=pythonstyle, caption={Mixed precision training with HuggingFace and manual PyTorch AMP.}]
# === HuggingFace TrainingArguments (simplest approach) ===
from transformers import TrainingArguments

# BF16 on Ampere+ GPUs (A100, H100, RTX 30xx/40xx)
args_bf16 = TrainingArguments(
    output_dir="./out",
    bf16=True,               # BF16 forward/backward; FP32 master weights
    bf16_full_eval=True,     # also use BF16 during evaluation
    # No loss scaling needed -- BF16 has FP32-equivalent range
)

# FP16 on older GPUs (V100, T4, RTX 20xx)
args_fp16 = TrainingArguments(
    output_dir="./out",
    fp16=True,               # FP16 forward/backward
    fp16_full_eval=False,    # keep eval in FP32 for accuracy
    # Loss scaling is automatic via PyTorch GradScaler
)

# === Manual PyTorch AMP (for custom training loops) ===
import torch

# Setup (PyTorch 2.x API)
use_fp16 = not torch.cuda.is_bf16_supported()
scaler = torch.amp.GradScaler("cuda", enabled=use_fp16)  # only needed for FP16
optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
dtype = torch.float16 if use_fp16 else torch.bfloat16

for batch in train_dataloader:
    optimizer.zero_grad()

    # Autocast: run forward pass in reduced precision
    with torch.autocast("cuda", dtype=dtype):
        outputs = model(**batch)
        loss = outputs.loss

    if use_fp16:
        # FP16 path: scale loss to prevent gradient underflow
        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)          # unscale before clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(optimizer)              # skips step on overflow
        scaler.update()                     # adjust scale factor
    else:
        # BF16 path: no scaling needed
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

    scheduler.step()
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={使用HuggingFace和手动PyTorch AMP进行混合精度训练。}]
# === HuggingFace TrainingArguments（最简单方法） ===
from transformers import TrainingArguments

# 在Ampere+ GPU上使用BF16（A100, H100, RTX 30xx/40xx）
args_bf16 = TrainingArguments(
    output_dir="./out",
    bf16=True,               # BF16前向/反向；FP32主权重
    bf16_full_eval=True,     # 评估时也使用BF16
    # 无需损失缩放——BF16具有与FP32等效的范围
)

# 在较旧GPU上使用FP16（V100, T4, RTX 20xx）
args_fp16 = TrainingArguments(
    output_dir="./out",
    fp16=True,               # FP16前向/反向
    fp16_full_eval=False,    # 评估时保持FP32精度
    # 通过PyTorch GradScaler自动进行损失缩放
)

# === 手动PyTorch AMP（用于自定义训练循环） ===
import torch

# 设置（PyTorch 2.x API）
use_fp16 = not torch.cuda.is_bf16_supported()
scaler = torch.amp.GradScaler("cuda", enabled=use_fp16)  # 仅FP16需要
optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
dtype = torch.float16 if use_fp16 else torch.bfloat16

for batch in train_dataloader:
    optimizer.zero_grad()

    # 自动混合精度：以降低的精度运行前向传播
    with torch.autocast("cuda", dtype=dtype):
        outputs = model(**batch)
        loss = outputs.loss

    if use_fp16:
        # FP16路径：缩放损失以防止梯度下溢
        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)          # 在裁剪前取消缩放
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(optimizer)              # 如果溢出则跳过该步骤
        scaler.update()                     # 调整缩放因子
    else:
        # BF16路径：无需缩放
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

    scheduler.step()
\end{lstlisting}

\begin{intuitionbox}[Key Differences: BF16 vs. FP16 in Code]
\begin{itemize}
  \item \textbf{BF16}: just wrap with \texttt{autocast(dtype=torch.bfloat16)}---no scaler needed. Simpler code and more numerically stable.
  \item \textbf{FP16}: requires \texttt{GradScaler} to prevent gradient underflow. The scaler dynamically adjusts a multiplier; if overflow is detected (NaN), the optimizer step is skipped and the scale is reduced.
  \item \textbf{Gradient clipping + FP16}: you \emph{must} call \texttt{scaler.unscale\_(optimizer)} before \texttt{clip\_grad\_norm\_}, otherwise you’re clipping scaled gradients (wrong threshold).
  \item \textbf{Memory savings}: \% reduction in activation memory (activations stored in 16-bit); weight memory depends on whether you keep FP32 master copies.
\end{itemize}
\end{intuitionbox}

\begin{intuitionbox}[关键区别：代码中BF16 vs. FP16]
\begin{itemize}
  \item \textbf{BF16}: 只需用 \texttt{autocast(dtype=torch.bfloat16)} 包裹——无需缩放器。代码更简单，数值更稳定。
  \item \textbf{FP16}: 需要 \texttt{GradScaler} 以防止梯度下溢。缩放器动态调整乘数；如果检测到溢出（NaN），则跳过优化器步骤并降低缩放。
  \item \textbf{梯度裁剪 + FP16}: 你\emph{必须}在 \texttt{clip\_grad\_norm\_} 之前调用 \texttt{scaler.unscale\_(optimizer)}，否则你裁剪的是缩放后的梯度（阈值错误）。
  \item \textbf{内存节省}: 激活内存的减少百分比（激活以16位存储）；权重内存取决于是否保留FP32主副本。
\end{itemize}
\end{intuitionbox}

\subsection{Practical Optimizer Settings by Training Phase}
\subsection{按训练阶段的实际优化器设置}

\label{practical-optimizer-settings-by-training-phase}

\begin{keybox}[Optimizer Hyperparameter Reference Table]
\begin{tabular}{@{}lp{2.2cm}p{2.2cm}p{2.2cm}p{2.2cm}p{2.2cm}@{}}
\toprule
\textbf{Phase} & \textbf{Optimizer} & \textbf{LR} & \textbf{WD} & \textbf{Warmup} & \textbf{Schedule} \\
\midrule
Pretraining & AdamW & $3\text{e-}4$ & 0.1 & 2000 steps & WSD or Cosine \\
SFT & AdamW & $2\text{e-}5$ & 0.01 & 100 steps & Cosine \\
LoRA SFT & AdamW & $2\text{e-}4$ & 0.01 & 100 steps & Cosine \\
\bottomrule
\end{tabular}

\emph{All use: $\beta_1{=}0.9$, $\beta_2{=}0.95$, $\epsilon{=}10^{-8}$, \texttt{max\_grad\_norm}=1.0, BF16. For RL settings see §\ref{sec:rl-optimizer-config}.}
\end{keybox}

\begin{keybox}[优化器超参数参考表]
\begin{tabular}{@{}lp{2.2cm}p{2.2cm}p{2.2cm}p{2.2cm}p{2.2cm}@{}}
\toprule
\textbf{阶段} & \textbf{优化器} & \textbf{学习率} & \textbf{权重衰减} & \textbf{预热步数} & \textbf{调度策略} \\
\midrule
预训练 & AdamW & $3\text{e-}4$ & 0.1 & 2000步 & WSD或余弦 \\
SFT & AdamW & $2\text{e-}5$ & 0.01 & 100步 & 余弦 \\
LoRA SFT & AdamW & $2\text{e-}4$ & 0.01 & 100步 & 余弦 \\
\bottomrule
\end{tabular}

\emph{所有阶段使用: $\beta_1{=}0.9$, $\beta_2{=}0.95$, $\epsilon{=}10^{-8}$, \texttt{max\_grad\_norm}=1.0, BF16. 强化学习设置见§\ref{sec:rl-optimizer-config}.}
\end{keybox}

\begin{examplebox}[Diagnosing Training Instability]
\begin{lstlisting}[style=pythonstyle]
# Monitor these metrics to diagnose optimizer issues:
# 1. Gradient norm -- should be < max_grad_norm most of the time
# 2. Loss scale (FP16) -- should be stable, not constantly decreasing
# 3. Parameter update norm -- should be << parameter norm

import torch
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[诊断训练不稳定性]
\begin{lstlisting}[style=pythonstyle]
# 监控以下指标以诊断优化器问题：
# 1. 梯度范数 —— 大多数时间应小于 max_grad_norm
# 2. 损失缩放（FP16） —— 应保持稳定，不持续下降
# 3. 参数更新范数 —— 应远小于参数范数

import torch
\end{lstlisting}
\end{examplebox}
```

```markdown
def log_optimizer_stats(model, optimizer, step):
    # Gradient norm (before clipping)
    total_norm = 0.0
    for p in model.parameters():
        if p.grad is not None:
            total_norm += p.grad.data.norm(2).item() ** 2
    total_norm = total_norm ** 0.5

    # Adam second moment stats (proxy for adaptive LR)
    v_norms = []
    for group in optimizer.param_groups:
        for p in group['params']:
            state = optimizer.state[p]
            if 'exp_avg_sq' in state:
                v_norms.append(state['exp_avg_sq'].mean().item())

    print(f"Step {step}: grad_norm={total_norm:.3f}, "
          f"mean_v={sum(v_norms)/len(v_norms):.6f}")

# Red flags:
# grad_norm >> 1.0 repeatedly -> reduce LR or increase warmup
# grad_norm == 0.0 -> gradient vanishing or wrong loss
# loss_scale decreasing -> FP16 overflow, switch to BF16
# v very small -> Adam not warmed up yet, extend warmup

def log_optimizer_stats(model, optimizer, step):
    # 梯度范数（裁剪前）
    total_norm = 0.0
    for p in model.parameters():
        if p.grad is not None:
            total_norm += p.grad.data.norm(2).item() ** 2
    total_norm = total_norm ** 0.5

    # Adam 二阶矩统计（自适应学习率的代理）
    v_norms = []
    for group in optimizer.param_groups:
        for p in group['params']:
            state = optimizer.state[p]
            if 'exp_avg_sq' in state:
                v_norms.append(state['exp_avg_sq'].mean().item())

    print(f"Step {step}: grad_norm={total_norm:.3f}, "
          f"mean_v={sum(v_norms)/len(v_norms):.6f}")

# 红色警报：
# grad_norm >> 1.0 持续出现 -> 降低学习率或增加预热步数
# grad_norm == 0.0 -> 梯度消失或损失函数错误
# loss_scale 持续下降 -> FP16 溢出，切换到 BF16
# v 非常小 -> Adam 尚未预热，延长预热步数
\end{lstlisting}
\end{examplebox}


\begin{intuitionbox}[The Learning Rate is the Most Important Hyperparameter]
In practice, getting the learning rate right matters more than any other hyperparameter. A rule of thumb for LLM fine-tuning:

\begin{itemize}
  \item Start with the values in the table above
  \item If loss diverges (increases after initial decrease): LR is too high
  \item If loss decreases very slowly and plateaus early: LR is too low
  \item If loss is unstable (oscillates): LR is too high or warmup is too short
\end{itemize}

The second most important hyperparameter is batch size (affects gradient noise and effective LR via the linear scaling rule). Everything else is secondary.
\end{intuitionbox}

\begin{intuitionbox}[学习率是最重要的超参数]
在实践中，正确设置学习率比其他任何超参数都更重要。LLM微调的经验法则：

\begin{itemize}
  \item 从上面表格中的值开始
  \item 如果损失发散（在初始下降后增加）：学习率过高
  \item 如果损失下降非常缓慢且早期停滞：学习率过低
  \item 如果损失不稳定（震荡）：学习率过高或预热步数不足
\end{itemize}

第二重要的超参数是批次大小（通过线性缩放规则影响梯度噪声和有效学习率）。其他一切都是次要的。
\end{intuitionbox}

\section{Flash Attention -- Algorithm and Hardware Awareness}
\label{flash-attention-algorithm-and-hardware-awareness}

\section{Flash Attention —— 算法与硬件感知}
\label{flash-attention-algorithm-and-hardware-awareness}

Flash Attention~\cite{dao2022flashattention, dao2023flashattention2} is one of the most impactful algorithmic innovations in deep learning since the transformer itself. It does not change the mathematical result of attention -- it computes \emph{exactly} the same output -- but it restructures the memory access pattern so that the GPU's limited fast SRAM does all the heavy lifting, cutting HBM footprint from $O(n^2)$ to $O(n)$ and delivering 2--4$\times$ end-to-end wall-clock gains on typical workloads.

Flash Attention~\cite{dao2022flashattention, dao2023flashattention2} 是自Transformer以来深度学习中最具影响力的算法创新之一。它不改变注意力的数学结果 —— 它计算出的输出 **完全相同** —— 而是重构了内存访问模式，使得GPU有限的快速SRAM承担所有繁重工作，将HBM占用从 $O(n^2)$ 削减到 $O(n)$，在典型工作负载上实现2–4倍的端到端加速。

\subsection{The Standard Attention Memory Problem}
\label{the-standard-attention-memory-problem}

\subsection{标准注意力的内存问题}
\label{the-standard-attention-memory-problem}

Standard scaled dot-product attention is: 
\[
\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}}\right) V
\]

标准缩放点积注意力为：
\[
\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}}\right) V
\]

\begin{keybox}[Standard Attention Memory Complexity]
For sequence length $n$ and head dimension $d$:

\begin{itemize}
  \item $Q, K, V \in \mathbb{R}^{n \times d}$: $O(nd)$ memory
  \item $S = QK^T \in \mathbb{R}^{n \times n}$: \textbf{$O(n^2)$ memory} -- the bottleneck
  \item $P = \text{softmax}(S) \in \mathbb{R}^{n \times n}$: another $O(n^2)$
  \item $O = PV \in \mathbb{R}^{n \times d}$: $O(nd)$
\end{itemize}

At $n=8192$, $d=128$, BF16: the attention matrix alone is $8192^2 \times 2 \approx 134$ MB \emph{per head}. With 32 heads, that is 4.3 GB just for one layer's attention scores.
\end{keybox}

\begin{keybox}[标准注意力的内存复杂度]
对于序列长度 $n$ 和头维度 $d$：

\begin{itemize}
  \item $Q, K, V \in \mathbb{R}^{n \times d}$：$O(nd)$ 内存
  \item $S = QK^T \in \mathbb{R}^{n \times n}$：\textbf{$O(n^2)$ 内存} —— 瓶颈
  \item $P = \text{softmax}(S) \in \mathbb{R}^{n \times n}$：又一个 $O(n^2)$
  \item $O = PV \in \mathbb{R}^{n \times d}$：$O(nd)$
\end{itemize}

当 $n=8192$, $d=128$, BF16 时：仅注意力矩阵就是 $8192^2 \times 2 \approx 134$ MB \emph{每头}。有 32 个注意力头，那么仅一层注意力分数就需要 4.3 GB。
\end{keybox}

\begin{intuitionbox}[Why $O(n^2)$ is Catastrophic]
The attention matrix must be written to HBM (it does not fit in SRAM for long sequences), then read back for the softmax, then read again for the $PV$ product. Each of these HBM round-trips is slow. For $n=32768$ (32K context), the attention matrix is $32768^2 \times 2 \approx 2$ GB \emph{per head} -- completely infeasible to store.
\end{intuitionbox}

\begin{intuitionbox}[为什么 $O(n^2)$ 是灾难性的]
注意力矩阵必须写入 HBM（对于长序列它无法放入 SRAM），然后为了 softmax 读取回来，再为了 $PV$ 乘积读取一次。每一次 HBM 往返都很慢。对于 $n=32768$（32K 上下文），注意力矩阵是 $32768^2 \times 2 \approx 2$ GB \emph{每头} —— 完全无法存储。
\end{intuitionbox}

\subsection{The Flash Attention Key Insight -- Tiling and Online Softmax}
\label{the-flash-attention-key-insight-tiling-and-online-softmax}

\subsection{Flash Attention 的关键洞察 —— 分块与在线 Softmax}
\label{the-flash-attention-key-insight-tiling-and-online-softmax}

The core insight is: \textbf{we never need the full $n \times n$ matrix in memory at once}. We can compute the output $O$ block-by-block if we use the \emph{online softmax} trick.

核心洞察是：**我们永远不需要一次性将完整的 $n \times n$ 矩阵放入内存**。如果使用 *在线 softmax* 技巧，我们可以逐块计算输出 $O$。

\paragraph{Online Softmax.}
\label{online-softmax.}

\paragraph{在线 Softmax。}
\label{online-softmax.}

Recall that softmax requires a global maximum for numerical stability: 
\[
\text{softmax}(x_i) = \frac{e^{x_i - m}}{\sum_j e^{x_j - m}}, \quad m = \max_j x_j
\]

回忆一下，softmax 需要全局最大值以保证数值稳定性：
\[
\text{softmax}(x_i) = \frac{e^{x_i - m}}{\sum_j e^{x_j - m}}, \quad m = \max_j x_j
\]

The trick: we can \emph{update} the running maximum and normalization factor as we process new blocks, without ever materializing the full row.

技巧：在处理新块时，我们可以**更新**运行中的最大值和归一化因子，而不必实现完整的行。

\begin{keybox}[Online Softmax Update Rule]
Given a running state $(m_{\text{old}}, \ell_{\text{old}}, O_{\text{old}})$ and a new block of scores $s_{\text{new}}$:

\begin{enumerate}
  \item $m_{\text{new}} = \max(m_{\text{old}},\; \max(s_{\text{new}}))$
  \item $\ell_{\text{new}} = e^{m_{\text{old}} - m_{\text{new}}} \cdot \ell_{\text{old}}
        + \sum\_j e^{s\_{\text{new},j} - m\_{\text{new}}}$
  \item $O_{\text{new}} = \frac{1}{\ell_{\text{new}}} \left(
        e^{m\_{\text{old}} - m_{\text{new}}} \cdot \ell\_{\text{old}} \cdot O\_{\text{old}}
        + e^{s\_{\text{new}} - m\_{\text{new}}} \cdot V\_{\text{new}} \right)$
\end{enumerate}

This is mathematically equivalent to computing softmax over all blocks at once.
\end{keybox}

\begin{keybox}[在线 Softmax 更新规则]
给定一个运行状态 $(m_{\text{old}}, \ell_{\text{old}}, O_{\text{old}})$ 和一个新的分数块 $s_{\text{new}}$：

\begin{enumerate}
  \item $m_{\text{new}} = \max(m_{\text{old}},\; \max(s_{\text{new}}))$
  \item $\ell_{\text{new}} = e^{m_{\text{old}} - m_{\text{new}}} \cdot \ell_{\text{old}}
        + \sum\_j e^{s\_{\text{new},j} - m\_{\text{new}}}$
  \item $O_{\text{new}} = \frac{1}{\ell_{\text{new}}} \left(
        e^{m\_{\text{old}} - m_{\text{new}}} \cdot \ell\_{\text{old}} \cdot O\_{\text{old}}
        + e^{s\_{\text{new}} - m\_{\text{new}}} \cdot V\_{\text{new}} \right)$
\end{enumerate}

这在数学上等价于一次性对所有块计算 softmax。
\end{keybox}

\subsection{The Flash Attention Algorithm}
\label{the-flash-attention-algorithm}

\subsection{Flash Attention 算法}
\label{the-flash-attention-algorithm}

\begin{examplebox}[Flash Attention Forward Pass – Block Tiling]
\textbf{Setup:} SRAM size $M$. Block sizes $B_r = \lceil M / (4d) \rceil$, $B_c = \min(\lceil M / (4d) \rceil, d)$.

\begin{enumerate}
  \item Divide $Q$ into $T_r = \lceil n / B_r \rceil$ blocks $Q_1, \ldots, Q_{T_r}$
  \item Divide $K, V$ into $T_c = \lceil n / B_c \rceil$ blocks $K_1, \ldots, K_{T_c}$
  \item Initialize output $O \in \mathbb{R}^{n \times d}$, running max $m \in \mathbb{R}^n$, running sum $\ell \in \mathbb{R}^n$ (all in HBM)
  \item \textbf{Outer loop} over $j = 1, \ldots, T_c$:
  \begin{enumerate}
    \item Load $K_j, V_j$ from HBM to SRAM
    \item \textbf{Inner loop} over $i = 1, \ldots, T_r$:
    \begin{enumerate}
      \item Load $Q_i, O_i, m_i, \ell_i$ from HBM to SRAM
      \item Compute $S_{ij} = Q_i K_j^T / \sqrt{d}$ (stays in SRAM)
      \item Apply online softmax update to get new $m_i, \ell_i, O_i$
      \item Write $O_i, m_i, \ell_i$ back to HBM
    \end{enumerate}
  \end{enumerate}
  \item Return $O$
\end{enumerate}

\textbf{Key:} $S_{ij}$ (the attention tile) is computed and discarded in SRAM. It is \emph{never written to HBM}.
\end{examplebox}

\begin{examplebox}[Flash Attention 前向传播 —— 块分块]
\textbf{设置：} SRAM 大小 $M$。块大小 $B_r = \lceil M / (4d) \rceil$，$B_c = \min(\lceil M / (4d) \rceil, d)$。

\begin{enumerate}
  \item 将 $Q$ 划分为 $T_r = \lceil n / B_r \rceil$ 个块 $Q_1, \ldots, Q_{T_r}$
  \item 将 $K, V$ 划分为 $T_c = \lceil n / B_c \rceil$ 个块 $K_1, \ldots, K_{T_c}$
  \item 初始化输出 $O \in \mathbb{R}^{n \times d}$，运行中的最大值 $m \in \mathbb{R}^n$，运行中的和 $\ell \in \mathbb{R}^n$（全部在 HBM 中）
  \item \textbf{外层循环} 遍历 $j = 1, \ldots, T_c$：
  \begin{enumerate}
    \item 将 $K_j, V_j$ 从 HBM 加载到 SRAM
    \item \textbf{内层循环} 遍历 $i = 1, \ldots, T_r$：
    \begin{enumerate}
      \item 将 $Q_i, O_i, m_i, \ell_i$ 从 HBM 加载到 SRAM
      \item 计算 $S_{ij} = Q_i K_j^T / \sqrt{d}$（保留在 SRAM 中）
      \item 应用在线 softmax 更新以获得新的 $m_i, \ell_i, O_i$
      \item 将 $O_i, m_i, \ell_i$ 写回 HBM
    \end{enumerate}
  \end{enumerate}
  \item 返回 $O$
\end{enumerate}

\textbf{关键：} $S_{ij}$（注意力块）在 SRAM 中计算并丢弃。它 **从未被写入 HBM**。
\end{examplebox}

\begin{keybox}[Flash Attention Complexity]
\begin{tabular}{@{}lp{5cm}p{6.5cm}@{}}
\toprule
 & \textbf{Standard Attention} & \textbf{Flash Attention} \\
\midrule
Memory (HBM) & $O(n^2)$ & $O(n)$ \\
HBM reads/writes & $O(n^2 d)$ & $O(n^2 d / M)$ \\
FLOPs & $O(n^2 d)$ & $O(n^2 d)$ (same) \\
Speedup & 1$\times$ & 2--4$\times$ \\
\bottomrule
\end{tabular}

In the forward pass, the total FLOPs remain $O(n^2 d)$ -- identical to standard attention. Flash Attention gains speed entirely by slashing slow HBM traffic, not by reducing arithmetic. (The backward pass actually performs \emph{more} FLOPs due to recomputation, but the wall-clock time is still lower because the saved memory bandwidth dominates.)
\end{keybox}

\begin{keybox}[Flash Attention 复杂度]
\begin{tabular}{@{}lp{5cm}p{6.5cm}@{}}
\toprule
 & \textbf{标准注意力} & \textbf{Flash Attention} \\
\midrule
内存（HBM） & $O(n^2)$ & $O(n)$ \\
HBM 读写次数 & $O(n^2 d)$ & $O(n^2 d / M)$ \\
FLOPs & $O(n^2 d)$ & $O(n^2 d)$（相同） \\
加速比 & 1$\times$ & 2--4$\times$ \\
\bottomrule
\end{tabular}

在前向传播中，总 FLOPs 仍然是 $O(n^2 d)$ —— 与标准注意力相同。Flash Attention 完全通过削减慢速 HBM 流量来获得速度，而不是减少算术运算。（由于重计算，反向传播实际上执行了 *更多* 的 FLOPs，但挂钟时间仍然更低，因为节省的内存带宽占主导。）
\end{keybox}

\subsection{Flash Attention 2 -- Better Parallelism}
\label{flash-attention-2-better-parallelism}

\subsection{Flash Attention 2 —— 更好的并行性}
\label{flash-attention-2-better-parallelism}

Flash Attention 2~\cite{dao2023flashattention2} made three key improvements:

\begin{enumerate}
  \item \textbf{Reduced non-matmul FLOPs:} The original FA had unnecessary rescaling operations in the inner loop. FA2 restructures the loop to minimize these. On A100, Tensor Core matrix multiplications outpace scalar operations by roughly 16$\times$, so even a small fraction of non-matmul work in the inner loop becomes the latency bottleneck.
  \item \textbf{Better parallelism across sequence dimension:} FA1 parallelized over batch and heads only. FA2 also parallelizes over the query sequence dimension, enabling better GPU utilization for long sequences with small batch sizes.
  \item \textbf{Causal masking optimization:} For autoregressive (causal) attention, roughly half the blocks are fully masked. FA2 skips these blocks entirely, giving $\sim$2$\times$ speedup for causal attention vs.~bidirectional.
\end{enumerate}

Flash Attention 2~\cite{dao2023flashattention2} 做出了三项关键改进：

\begin{enumerate}
  \item \textbf{减少非矩阵乘法 FLOPs：} 原始 FA 在内循环中有不必要的重缩放操作。FA2 重构循环以最小化这些操作。在 A100 上，Tensor Core 矩阵乘法的速度约为标量运算的 16 倍，因此内循环中即使很小的非矩阵乘法工作量也会成为延迟瓶颈。
  \item \textbf{沿序列维度的更好并行性：} FA1 仅对批处理和注意力头进行并行化。FA2 还对查询序列维度进行并行化，从而在小批次大小的长序列上实现更好的 GPU 利用率。
  \item \textbf{因果掩码优化：} 对于自回归（因果）注意力，大约一半的块是完全掩码的。FA2 完全跳过这些块，使得因果注意力相比双向注意力获得 $\sim$2 倍的加速。
\end{enumerate}
```

\subsection{Flash Attention 3 -- Hopper Architecture}
\subsection{Flash Attention 3 -- Hopper 架构}
\label{flash-attention-3-hopper-architecture}

Flash Attention 3~\cite{shah2024flashattention3} is designed specifically for H100 and exploits three Hopper-specific features:
Flash Attention 3~\cite{shah2024flashattention3} 专门为 H100 设计，利用了 Hopper 的三个特有功能：

\begin{itemize}
  \item \textbf{TMA (Tensor Memory Accelerator):} H100 has a dedicated hardware unit for asynchronous bulk data movement between HBM and SRAM. FA3 uses TMA to overlap data loading with computation, hiding memory latency.
  \item \textbf{TMA（张量内存加速器）：} H100 拥有专用硬件单元，用于在 HBM 和 SRAM 之间进行异步批量数据移动。FA3 使用 TMA 将数据加载与计算重叠，从而隐藏内存延迟。
  \item \textbf{Warp-specialization:} FA3 assigns different warps to different roles (producer warps load data via TMA; consumer warps compute MMA). This is a software pipelining technique that keeps both the memory system and Tensor Cores busy simultaneously.
  \item \textbf{Warp 专业化：} FA3 将不同的 warp 分配给不同的角色（生产者 warp 通过 TMA 加载数据；消费者 warp 计算 MMA）。这是一种软件流水线技术，可同时保持内存系统和 Tensor Core 忙碌。
  \item \textbf{FP8 support:} H100 supports FP8 (E4M3/E5M2) Tensor Core operations at 2$\times$ the throughput of BF16. FA3 supports FP8 attention with per-block quantization to maintain accuracy.
  \item \textbf{FP8 支持：} H100 支持 FP8（E4M3/E5M2）Tensor Core 运算，吞吐量是 BF16 的 2$\times$。FA3 支持 FP8 注意力，并通过逐块量化来保持精度。
\end{itemize}

FA3 achieves up to \textbf{75\% of H100 theoretical peak} for FP16 attention, compared to $\sim$35\% for FA2.
对于 FP16 注意力，FA3 达到了 H100 理论峰值的 \textbf{75\%}，而 FA2 约为 35\%。

\subsection{Flash Attention 4 -- Blackwell Architecture}
\subsection{Flash Attention 4 -- Blackwell 架构}
\label{flash-attention-4-blackwell-architecture}

Flash Attention 4~\cite{zadouri2026flashattention4} targets NVIDIA’s Blackwell GPUs (B200/GB200), which double Tensor Core throughput to 2.25 PFLOP/s (BF16) while non-matmul units (exponential, shared memory bandwidth) scale at a slower rate. This \emph{asymmetric hardware scaling} means that the bottleneck shifts: on Blackwell, attention is limited not by matmul but by the softmax exponentials and shared memory traffic surrounding them.
Flash Attention 4~\cite{zadouri2026flashattention4} 针对 NVIDIA 的 Blackwell GPU（B200/GB200），其 Tensor Core 吞吐量翻倍至 2.25 PFLOP/s（BF16），而非矩阵乘法单元（指数运算、共享内存带宽）的扩展速度较慢。这种 \emph{非对称硬件扩展} 意味着瓶颈发生了转移：在 Blackwell 上，注意力不受矩阵乘法限制，而是受软最大指数运算及其周围的共享内存流量限制。

FA4 addresses this with four key techniques:
FA4 通过四项关键技术来解决这一问题：

\begin{itemize}
  \item \textbf{Fully asynchronous MMA pipelines:} Blackwell’s MMA instructions are fully asynchronous (unlike Hopper’s wgmma which still blocked on completion). FA4 redesigns the pipeline to overlap MMA, TMA loads, and softmax rescaling across larger tile sizes, keeping all hardware units saturated.
  \item \textbf{完全异步的 MMA 流水线：} Blackwell 的 MMA 指令是完全异步的（与 Hopper 的 wgmma 仍在完成时阻塞不同）。FA4 重新设计了流水线，以在更大的 tile 尺寸上重叠 MMA、TMA 加载和软最大重新缩放，使所有硬件单元保持饱和。
  \item \textbf{Software-emulated exponential:} Instead of calling the hardware \texttt{ex2} unit (which is the throughput bottleneck), FA4 emulates $e^x$ using polynomial approximations executed on the much faster Tensor Cores themselves. This trades extra matmul instructions for exponential-unit stalls.
  \item \textbf{软件模拟的指数运算：} FA4 不调用硬件 \texttt{ex2} 单元（这是吞吐量瓶颈），而是在速度更快的 Tensor Core 上使用多项式近似来模拟 $e^x$。这相当于用额外的矩阵乘法指令换取指数单元的停顿。
  \item \textbf{Conditional softmax rescaling:} Standard FlashAttention rescales the running $\max$ every tile. FA4 skips the rescaling when the new tile’s max does not exceed the running max (common in practice), saving both register shuffles and synchronization barriers.
  \item \textbf{条件软最大重新缩放：} 标准的 FlashAttention 在每个 tile 上重新缩放运行中的 $\max$。当新 tile 的最大值不超过运行中的最大值时（实践中常见），FA4 跳过重新缩放，从而节省寄存器重排和同步屏障。
  \item \textbf{Tensor Memory + 2-CTA MMA mode (backward pass):} The backward pass uses Blackwell’s \emph{Tensor Memory} (a per-SM scratchpad larger than shared memory) and a 2-CTA cooperative mode that fuses $dQ$ accumulation across two thread-block clusters, halving shared memory round-trips.
  \item \textbf{Tensor Memory + 2-CTA MMA 模式（反向传播）：} 反向传播使用 Blackwell 的 \emph{Tensor Memory}（一种比共享内存更大的每 SM 暂存器）和一种 2-CTA 协作模式，该模式将两个线程块簇的 $dQ$ 累加融合，将共享内存往返次数减半。
\end{itemize}

\begin{keybox}[FA4 Implementation: CuTe-DSL]
FA4 is the first FlashAttention version written in \textbf{CuTe-DSL}, a Python-embedded domain-specific language for GPU kernels (part of CUTLASS 4.x). CuTe-DSL compiles 20--30$\times$ faster than C++ CUTLASS templates while retaining full control over register allocation and pipeline scheduling. This dramatically lowers the iteration time for kernel development.
\end{keybox}

\begin{keybox}[FA4 实现：CuTe-DSL]
FA4 是第一个用 \textbf{CuTe-DSL} 编写的 FlashAttention 版本，CuTe-DSL 是一种嵌入 Python 的 GPU 内核领域特定语言（属于 CUTLASS 4.x 的一部分）。CuTe-DSL 的编译速度比 C++ CUTLASS 模板快 20--30$\times$，同时保持对寄存器分配和流水线调度的完全控制。这大大降低了内核开发的迭代时间。
\end{keybox}

\paragraph{Results.}
\paragraph{结果}
\label{results.}

On B200 with BF16 head-dim 128 (causal, seq-len 8K):
在 B200 上，使用 BF16，头维度 128（因果，序列长度 8K）：

\begin{itemize}
  \item \textbf{1613 TFLOP/s} -- 71\% of Blackwell peak utilization
  \item \textbf{1613 TFLOP/s} —— Blackwell 峰值利用率的 71\%
  \item \textbf{1.3$\times$} faster than cuDNN~9.13 (NVIDIA’s proprietary fused kernel)
  \item \textbf{1.3$\times$} 比 cuDNN~9.13（NVIDIA 专有的融合内核）更快
  \item \textbf{2.7$\times$} faster than Triton on the same hardware
  \item \textbf{2.7$\times$} 比相同硬件上的 Triton 更快
\end{itemize}

\begin{intuitionbox}[Hardware--Software Co-evolution]
The FlashAttention series illustrates a key principle: each GPU generation shifts the bottleneck, demanding new algorithmic ideas rather than just re-compilation. A80 $\to$ memory bandwidth limited (FA1/FA2: tiling + recomputation). H100 $\to$ data movement limited (FA3: TMA + warp-specialization). B200 $\to$ non-matmul compute limited (FA4: software-emulated exp + conditional rescaling). Understanding \emph{where the hardware bottleneck lies} is the prerequisite for writing efficient kernels.
\end{intuitionbox}

\begin{intuitionbox}[硬件-软件协同演进]
FlashAttention 系列说明了一个关键原则：每一代 GPU 都会改变瓶颈，需要新的算法思想而不仅仅是重新编译。A80 $\to$ 受内存带宽限制（FA1/FA2：分块 + 重计算）。H100 $\to$ 受数据移动限制（FA3：TMA + warp 专业化）。B200 $\to$ 受非矩阵乘法计算限制（FA4：软件模拟指数 + 条件重新缩放）。理解 \emph{硬件瓶颈所在} 是编写高效内核的前提。
\end{intuitionbox}

\section{Pretraining: Best Practices}
\section{预训练：最佳实践}
\label{sec:pretraining}

Pretraining is the most expensive phase of LLM development---consuming millions of GPU-hours and requiring careful orchestration of data, compute, and hyperparameters. This section distills key lessons from Llama-3~\cite{grattafiori2024llama3}, Chinchilla~\cite{hoffmann2022chinchilla}, and GPT-4~\cite{openai2023gpt4}.
预训练是 LLM 开发中最昂贵的阶段——消耗数百万 GPU 小时，需要精心协调数据、计算和超参数。本节提炼了来自 Llama-3~\cite{grattafiori2024llama3}、Chinchilla~\cite{hoffmann2022chinchilla} 和 GPT-4~\cite{openai2023gpt4} 的关键经验。

\subsection{Training Objective}
\subsection{训练目标}
\label{training-objective}

All modern decoder-only LLMs use \textbf{causal language modeling} (CLM): 
所有现代仅解码器的 LLM 都使用 \textbf{因果语言建模}（CLM）：
\[
\mathcal{L}_\text{CLM} = -\frac{1}{T}\sum_{t=1}^T \log P_\theta(x_t \mid x_{<t})
\]
 This simple objective---with enough data and scale---produces emergent capabilities (in-context learning, reasoning, instruction following) without explicit supervision~\cite{brown2020language}.
这个简单的目标——在足够的数据和规模下——无需显式监督即可产生涌现能力（上下文学习、推理、指令遵循）~\cite{brown2020language}。

\subsection{Data Pipeline}
\subsection{数据流水线}
\label{data-pipeline}

\begin{keybox}[Pretraining Data Recipe]
\begin{itemize}
  \item \textbf{Scale}: 1--15 trillion tokens for frontier models (Llama-3: 15T tokens)
  \item \textbf{规模}：前沿模型需要 1--15 万亿个 token（Llama-3：15T tokens）
  \item \textbf{Sources}: Web crawl (80\%), code (10\%), books/papers (5\%), curated (5\%)
  \item \textbf{来源}：网页爬取（80\%）、代码（10\%）、书籍/论文（5\%）、精选数据（5\%）
  \item \textbf{Deduplication}: MinHash + exact substring dedup reduces memorization~\cite{lee2022deduplicating}
  \item \textbf{去重}：MinHash + 精确子串去重减少记忆化~\cite{lee2022deduplicating}
  \item \textbf{Quality filtering}: Perplexity-based classifier, heuristic filters (length, language ID, toxicity)
  \item \textbf{质量过滤}：基于困惑度的分类器、启发式过滤器（长度、语言 ID、有害性）
  \item \textbf{Data mixing}: Temperature-weighted sampling across domains; upweight code and math for reasoning
  \item \textbf{数据混合}：跨领域的温度加权采样；提高代码和数学的权重以增强推理能力
\end{itemize}
\end{keybox}

\subsection{Scaling Laws}
\subsection{缩放定律}
\label{scaling-laws}

Hoffmann et al.~\cite{hoffmann2022chinchilla} showed that compute-optimal training requires balancing model size $N$ and data size $D$: $N_\text{opt} \propto C^{0.50}$, $D_\text{opt} \propto C^{0.50}$. A 70B model is compute-optimal at $\sim$1.4T tokens. In practice, models are \emph{over-trained} (more tokens than Chinchilla-optimal) because inference cost scales with model size, not training tokens---smaller over-trained models are cheaper to deploy.
Hoffmann 等人~\cite{hoffmann2022chinchilla} 表明，计算最优训练需要平衡模型大小 $N$ 和数据大小 $D$：$N_\text{opt} \propto C^{0.50}$，$D_\text{opt} \propto C^{0.50}$。一个 70B 模型在约 1.4T tokens 时达到计算最优。在实践中，模型会被 \emph{过度训练}（token 数超过 Chinchilla 最优值），因为推理成本随模型大小而非训练 token 数增长——较小的过度训练模型部署成本更低。

\subsection{Key Hyperparameters}
\subsection{关键超参数}
\label{key-hyperparameters}

\begin{table}[ht!]
\centering
\caption{Pretraining hyperparameters from published models.}
\caption{已发布模型的预训练超参数。}
\begin{tabular}{@{}lp{2.5cm}p{2.8cm}p{2.8cm}p{2.8cm}@{}}
\toprule
\textbf{Setting} & \textbf{Llama-3 405B} & \textbf{Llama-3 8B} & \textbf{Qwen-2.5 72B} & \textbf{Mistral 7B} \\
\textbf{设置} & \textbf{Llama-3 405B} & \textbf{Llama-3 8B} & \textbf{Qwen-2.5 72B} & \textbf{Mistral 7B} \\
\midrule
Tokens & 15T & 15T & 18T & 8T \\
Token 数 & 15T & 15T & 18T & 8T \\
Batch size (tokens) & 16M & 4M & 4M & 4M \\
批量大小（token） & 16M & 4M & 4M & 4M \\
Peak LR & $8\text{e-}5$ & $3\text{e-}4$ & $3\text{e-}4$ & $3\text{e-}4$ \\
峰值学习率 & $8\text{e-}5$ & $3\text{e-}4$ & $3\text{e-}4$ & $3\text{e-}4$ \\
Schedule & WSD & WSD & Cosine & Cosine \\
调度策略 & WSD & WSD & 余弦 & 余弦 \\
Weight decay & 0.1 & 0.1 & 0.1 & 0.1 \\
权重衰减 & 0.1 & 0.1 & 0.1 & 0.1 \\
Context length & 8192 & 8192 & 4096$\to$32K & 8192 \\
上下文长度 & 8192 & 8192 & 4096$\to$32K & 8192 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Common Failure Modes}
\subsection{常见失败模式}
\label{common-failure-modes}

\begin{warningbox}[Pretraining Pitfalls]
\begin{itemize}
  \item \textbf{Loss spikes}: Sudden loss increases from bad data batches or numerical instability. Llama-3 reports rolling back to checkpoints and skipping offending batches.
  \item \textbf{损失尖峰}：由不良数据批次或数值不稳定性导致的损失突然增加。Llama-3 报告回滚到检查点并跳过有问题的批次。
  \item \textbf{Memorization}: Model regurgitates training data verbatim. Fix: deduplicate aggressively; monitor extraction attacks.
  \item \textbf{记忆化}：模型逐字复述训练数据。修复方法：积极去重；监控提取攻击。
  \item \textbf{Context length}: Training on short sequences then deploying at long context fails. Use continued pretraining on long documents + RoPE scaling.
  \item \textbf{上下文长度}：在短序列上训练然后在长上下文中部署会失败。使用在长文档上的持续预训练 + RoPE 缩放。
\end{itemize}
\end{warningbox}

\section{Supervised Fine-Tuning (SFT)}
\section{监督微调（SFT）}
\label{sec:sft}

SFT transforms a pretrained language model into an instruction-following assistant by training on curated prompt--response pairs. This is the bridge between raw language modeling and RLHF.
SFT 通过在精选的提示-响应对上进行训练，将预训练语言模型转变为指令遵循助手。这是原始语言建模与 RLHF 之间的桥梁。

\subsection{SFT Objective}
\subsection{SFT 目标}
\label{sft-objective}

The loss is identical to CLM, but computed only on \textbf{response tokens}: 
\[
\mathcal{L}_\text{SFT} = -\frac{1}{|y|}\sum_{t=1}^{|y|} \log P_\theta(y_t \mid x_\text{prompt}, y_{<t})
\]
 Prompt tokens provide context but receive no gradient (labels set to $-100$).

该损失与因果语言模型（CLM）相同，但仅在\textbf{响应token}上计算：
\[
\mathcal{L}_\text{SFT} = -\frac{1}{|y|}\sum_{t=1}^{|y|} \log P_\theta(y_t \mid x_\text{prompt}, y_{<t})
\]
提示 token 提供上下文但不接收梯度（标签设为 $-100$）。

\subsection{Data Quality: The LIMA Principle}
\subsection{数据质量：LIMA原则}
\label{data-quality-the-lima-principle}

Zhou et al.~\cite{zhou2023lima} demonstrated that 1,000 carefully curated examples can match models trained on 50K+ noisy examples. Key requirements:

周等人~\cite{zhou2023lima} 证明，1,000个精心策划的示例可以匹配在50K以上噪声示例上训练的模型。关键要求：

\begin{itemize}
  \item \textbf{Diversity}: Cover QA, summarization, code, math, creative writing, multi-turn dialogue
  \item \textbf{多样性}：涵盖问答、摘要、代码、数学、创意写作、多轮对话
  \item \textbf{Correctness}: Every response must be factually accurate and well-formatted
  \item \textbf{正确性}：每个响应必须事实准确且格式良好
  \item \textbf{Length balance}: Mix short (1-sentence) and long (multi-paragraph) responses
  \item \textbf{长度平衡}：混合短（单句）和长（多段落）响应
  \item \textbf{Decontamination}: Remove overlap with evaluation benchmarks
  \item \textbf{去污染}：移除与评估基准的重叠
\end{itemize}

\subsection{Training Configuration}
\subsection{训练配置}
\label{training-configuration}

\begin{lstlisting}[style=pythonstyle]
from trl import SFTTrainer, SFTConfig

sft_config = SFTConfig(
    output_dir="./sft_output",
    max_seq_length=4096,
    packing=True,              # Pack short examples into full sequences
    learning_rate=2e-5,
    lr_scheduler_type="cosine",
    warmup_ratio=0.1,
    weight_decay=0.01,
    max_grad_norm=1.0,
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    bf16=True,
    gradient_checkpointing=True,
)
trainer = SFTTrainer(model=model, args=sft_config,
                     train_dataset=dataset, processing_class=tokenizer)
trainer.train()
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle]
from trl import SFTTrainer, SFTConfig

sft_config = SFTConfig(
    output_dir="./sft_output",
    max_seq_length=4096,
    packing=True,              # 将短示例打包成完整序列
    learning_rate=2e-5,
    lr_scheduler_type="cosine",
    warmup_ratio=0.1,
    weight_decay=0.01,
    max_grad_norm=1.0,
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    bf16=True,
    gradient_checkpointing=True,
)
trainer = SFTTrainer(model=model, args=sft_config,
                     train_dataset=dataset, processing_class=tokenizer)
trainer.train()
\end{lstlisting}

\subsection{Efficient Training Solutions}
\subsection{高效训练方案}
\label{efficient-training-solutions}

Standard HuggingFace training leaves significant performance on the table. Several libraries provide drop-in efficiency gains for SFT workloads:

标准 HuggingFace 训练会留下显著的性能提升空间。多个库为 SFT 工作负载提供了即插即用的效率提升：

\paragraph{Liger Kernel~\cite{hsu2024liger}.}
\paragraph{Liger Kernel~\cite{hsu2024liger}}
\label{liger-kernel-.}

An open-source set of \textbf{Triton-fused kernels} from LinkedIn that replace standard PyTorch operators during training. Key fusions include:

来自 LinkedIn 的一套开源\textbf{Triton 融合内核}，在训练期间替换标准 PyTorch 算子。关键融合包括：

\begin{itemize}
  \item \textbf{Fused Cross-Entropy}: Merges the final linear projection, softmax, and loss computation into a single kernel---avoids materializing the full $(\text{batch} \times \text{seq} \times \text{vocab})$ logit tensor.
  \item \textbf{融合交叉熵}：将最后的线性投影、softmax 和损失计算合并为单个内核——避免实例化完整的 $(\text{batch} \times \text{seq} \times \text{vocab})$ logit 张量。
  \item \textbf{Fused RMSNorm / SwiGLU / RoPE}: Eliminates intermediate memory allocations for common LLM building blocks.
  \item \textbf{融合 RMSNorm / SwiGLU / RoPE}：消除常见 LLM 构建块的中间内存分配。
  \item \textbf{Chunked operations}: Processes large tensors in tiles to keep peak memory bounded.
  \item \textbf{分块操作}：将大张量分块处理以维持峰值内存有界。
\end{itemize}

\textbf{Result}: 20\% higher throughput and up to 60\% memory reduction with a one-line integration (\texttt{apply\_liger\_kernel\_to\_llama()}). Compatible with FSDP, DeepSpeed, and LoRA.

\textbf{结果}：通过一行集成（\texttt{apply\_liger\_kernel\_to\_llama()}）即可实现20%的吞吐量提升和高达60%的内存减少。兼容 FSDP、DeepSpeed 和 LoRA。

\paragraph{Unsloth~\cite{unsloth2024}.}
\paragraph{Unsloth~\cite{unsloth2024}}
\label{unsloth-.}

A specialized fine-tuning library that combines \textbf{custom CUDA/Triton kernels} with aggressive memory optimization:

一个专门的微调库，结合了\textbf{自定义 CUDA/Triton 内核}和激进的内存优化：

\begin{itemize}
  \item Manual backpropagation through LoRA layers (avoids autograd overhead).
  \item 手动反向传播通过 LoRA 层（避免自动求导开销）。
  \item 4-bit QLoRA with fused dequantization---trains 70B models on a single 48~GB GPU.
  \item 带融合反量化的 4 位 QLoRA——在单张 48 GB GPU 上训练 70B 模型。
  \item Intelligent RoPE and attention kernel fusion specific to each architecture (Llama, Mistral, Qwen, Gemma).
  \item 针对每种架构（Llama、Mistral、Qwen、Gemma）的智能 RoPE 和注意力内核融合。
\end{itemize}

\textbf{Result}: 2--5$\times$ faster than vanilla HuggingFace + PEFT, with 60--70\% less VRAM. Particularly impactful for single-GPU and consumer-hardware workflows.

\textbf{结果}：比原始 HuggingFace + PEFT 快 2--5 倍，显存减少 60--70%。对单 GPU 和消费级硬件工作流尤其有效。

\paragraph{torchtune~\cite{torchtune2024}.}
\paragraph{torchtune~\cite{torchtune2024}}
\label{torchtune-.}

Meta’s native PyTorch fine-tuning library (development wound down in 2025), designed around \textbf{composability} rather than monolithic abstractions:

Meta 的原生 PyTorch 微调库（开发于2025年收尾），围绕\textbf{可组合性}而非整体抽象设计：

\begin{itemize}
  \item Pure PyTorch---no trainer class; recipes are readable single-file scripts.
  \item 纯 PyTorch——无训练器类；配方是可读的单文件脚本。
  \item Native integration with \texttt{torch.compile}, FSDP2, and activation checkpointing.
  \item 原生集成 \texttt{torch.compile}、FSDP2 和激活检查点。
  \item First-class support for QLoRA, full fine-tuning, and knowledge distillation.
  \item 一流的 QLoRA、全微调和知识蒸馏支持。
  \item Built-in quantization-aware training (QAT) for post-training compression.
  \item 内置训练后压缩的量化感知训练（QAT）。
\end{itemize}

\textbf{Result}: Comparable speed to custom solutions but with full debuggability and no framework lock-in.

\textbf{结果}：速度与自定义方案相当，但具有完全可调试性且无框架锁定。

\begin{keybox}[Choosing an Efficiency Stack]
\begin{itemize}
  \item \textbf{Quick LoRA/QLoRA on $\leq$1 GPU}: Unsloth (fastest time-to-train, minimal setup)
  \item \textbf{Multi-GPU full fine-tune}: TRL/DeepSpeed + Liger Kernel (best throughput at scale)
  \item \textbf{Research / custom training loops}: torchtune (transparent, hackable, native PyTorch)
\end{itemize}

These are \emph{complementary}: Liger kernels can be used inside both TRL and torchtune workflows.
\end{keybox}

\begin{keybox}[选择效率堆栈]
\begin{itemize}
  \item \textbf{在$\leq$1 GPU上快速LoRA/QLoRA}：Unsloth（训练时间最短，设置最少）
  \item \textbf{多GPU全微调}：TRL/DeepSpeed + Liger Kernel（规模下吞吐量最佳）
  \item \textbf{研究/自定义训练循环}：torchtune（透明、可入侵、原生PyTorch）
\end{itemize}

这些是\emph{互补的}：Liger内核可以在TRL和torchtune工作流中使用。
\end{keybox}

\subsection{Best Practices}
\subsection{最佳实践}
\label{best-practices}

\begin{table}[ht!]
\centering
\caption{SFT training guidelines.}
\begin{tabular}{@{}lp{11cm}@{}}
\toprule
\textbf{Practice} & \textbf{Details} \\
\midrule
Packing & Concatenate multiple short examples into one sequence (separated by EOS). Avoids padding waste. \\
NEFTune~\cite{jain2024neftune} & Add uniform noise to embeddings ($\alpha=5$). Improves MT-Bench by 5--15\% at zero cost. \\
Chat template & Always use the model’s native template. Mismatched templates degrade quality. \\
Epochs & 2--3 for large datasets; up to 5 for small ($<$10K) curated sets. Over-training causes format memorization. \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[ht!]
\centering
\caption{SFT训练指南}
\begin{tabular}{@{}lp{11cm}@{}}
\toprule
\textbf{实践} & \textbf{详情} \\
\midrule
打包 & 将多个短示例连接成一个序列（由EOS分隔）。避免填充浪费。 \\
NEFTune~\cite{jain2024neftune} & 向嵌入添加均匀噪声（$\alpha=5$）。以零成本将MT-Bench提升5--15\%。 \\
聊天模板 & 始终使用模型的原生模板。不匹配的模板会降低质量。 \\
轮数 & 大数据集2-3轮；小数据集（$<$10K）精选集最多5轮。过度训练会导致格式记忆。 \\
\bottomrule
\end{tabular}
\end{table}

\begin{intuitionbox}[SFT Is Not Enough]
SFT teaches format and basic instruction following, but cannot reliably teach: \emph{preference} (which response is better---needs RLHF/DPO), \emph{refusal} (when not to answer---needs safety training), \emph{calibration} (saying ``I don’t know''---needs RL with truthfulness rewards), or \emph{complex reasoning} (multi-step chains---needs RL with verifiable rewards). The full pipeline is: Pretrain $\to$ SFT $\to$ RLHF/DPO.
\end{intuitionbox}

\begin{intuitionbox}[SFT不够]
SFT教会格式和基本的指令遵循，但不能可靠地教会：\emph{偏好}（哪个响应更好——需要RLHF/DPO）、\emph{拒绝}（何时不应回答——需要安全训练）、\emph{校准}（说“我不知道”——需要带诚实奖励的RL）、或\emph{复杂推理}（多步链——需要带可验证奖励的RL）。完整流程是：预训练 $\to$ SFT $\to$ RLHF/DPO。
\end{intuitionbox}

\section{LoRA and Parameter-Efficient Fine-Tuning}
\section{LoRA与参数高效微调}
\label{lora-and-parameter-efficient-fine-tuning}

Full fine-tuning of a 70B model requires storing 70B trainable parameters plus their optimizer states (560+ GB of memory). LoRA~\cite{hu2021lora} (Low-Rank Adaptation) provides a way to fine-tune with $<$1\% of the parameters while achieving comparable quality.

对70B模型进行全微调需要存储700亿可训练参数及其优化器状态（560+ GB内存）。LoRA~\cite{hu2021lora}（低秩适应）提供了一种用$<$1\%的参数进行微调并达到可比质量的方法。

\subsection{The LoRA Insight}
\subsection{LoRA洞察}
\label{the-lora-insight}

\begin{keybox}[LoRA Core Idea]
Instead of updating a full weight matrix $W \in \mathbb{R}^{d \times d}$, learn a low-rank perturbation: 
\[
W' = W + \frac{\alpha}{r} \cdot BA, \quad B \in \mathbb{R}^{d \times r}, \; A \in \mathbb{R}^{r \times d}
\]

\begin{itemize}
  \item $W$ is \textbf{frozen} (no gradients, no optimizer states)
  \item Only $B$ and $A$ are trained: $2 \times d \times r$ parameters instead of $d^2$
  \item At rank $r=16$, $d=4096$: LoRA adds $2 \times 4096 \times 16 = 131K$ params per layer vs.~$16.8M$ for full matrix
  \item $\alpha/r$ scaling controls the magnitude of the update
\end{itemize}
\end{keybox}

\begin{keybox}[LoRA核心思想]
不更新完整的权重矩阵 $W \in \mathbb{R}^{d \times d}$，而是学习一个低秩扰动：
\[
W' = W + \frac{\alpha}{r} \cdot BA, \quad B \in \mathbb{R}^{d \times r}, \; A \in \mathbb{R}^{r \times d}
\]

\begin{itemize}
  \item $W$ 被\textbf{冻结}（无梯度，无优化器状态）
  \item 仅训练 $B$ 和 $A$：$2 \times d \times r$ 个参数而非 $d^2$
  \item 当秩 $r=16$，$d=4096$：LoRA 每层添加 $2 \times 4096 \times 16 = 131K$ 参数，而全矩阵为 $16.8M$
  \item $\alpha/r$ 缩放控制更新的幅度
\end{itemize}
\end{keybox}

\begin{intuitionbox}[Why Low-Rank Works]
Aghajanyan et al.~\cite{aghajanyan2020intrinsic} showed that fine-tuning operates in a very low-dimensional subspace --- the ``intrinsic dimensionality'' of the fine-tuning task is much smaller than the model’s parameter count. A 175B model’s fine-tuning task may have intrinsic dimensionality $<$10,000. LoRA exploits this directly: rank $r$ constrains the update to an $r$-dimensional subspace per weight matrix.
\end{intuitionbox}

\begin{intuitionbox}[为何低秩有效]
Aghajanyan等人~\cite{aghajanyan2020intrinsic}表明，微调在一个非常低维的子空间中进行——微调任务的“固有维度”远小于模型的参数量。175B模型的微调任务可能具有$<$10,000的固有维度。LoRA直接利用这一点：秩 $r$ 将每个权重矩阵的更新约束到一个 $r$ 维子空间。
\end{intuitionbox}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_011_lora-decomposition.png}
\caption{LoRA decomposes the weight update $\Delta W$ into two small matrices $B \times A$. The original weight $W$ remains frozen; only $B$ and $A$ receive gradients. At inference, the product $BA$ can be merged into $W$ with zero overhead.}
\label{fig:lora-decomposition}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_011_lora-decomposition.png}
\caption{LoRA将权重更新$\Delta W$分解为两个小矩阵$B \times A$。原始权重$W$保持冻结；仅$B$和$A$接收梯度。推理时，乘积$BA$可以零开销合并到$W$中。}
\label{fig:lora-decomposition}
\end{figure}

\begin{intuitionbox}[Why the $\alpha/r$ Scaling Matters]
Without scaling, doubling the rank $r$ would roughly double the magnitude of $\Delta W = BA$ (more columns in $B$ contribute to the sum). This means changing rank would also change how much the model is perturbed---you’d need to re-tune the learning rate every time you adjust $r$.

The $\alpha/r$ factor \textbf{normalizes the update magnitude} so that it stays approximately constant regardless of rank: 
\[
W' = W + \frac{\alpha}{r} \cdot BA
\]


\begin{itemize}
  \item \textbf{Fix $\alpha$, sweep $r$}: The effective update magnitude stays $\sim\alpha$ regardless of rank. You can try $r \in \{8, 16, 32, 64\}$ without re-tuning LR.
  \item \textbf{Common practice}: Set $\alpha = r$ (so $\alpha/r = 1$) or $\alpha = 2r$ (so $\alpha/r = 2$). This is a convenient default where the scaling factor is a small integer.
  \item \textbf{Why not just tune LR?} You could, but $\alpha/r$ provides a \emph{rank-independent} knob. Teams can share LR recipes across experiments with different ranks.
  \item \textbf{rsLoRA insight}~\cite{kalajdzievski2023rslora}: At high ranks ($r \geq 64$), empirical evidence shows $\alpha/\sqrt{r}$ is more stable than $\alpha/r$, because the variance of $BA$ scales with $\sqrt{r}$, not $r$.
\end{itemize}
\end{intuitionbox}

\begin{intuitionbox}[为什么 $\alpha/r$ 缩放很重要]
如果没有缩放，将秩 $r$ 加倍会使 $\Delta W = BA$ 的幅值大致加倍（$B$ 中更多的列对求和有贡献）。这意味着改变秩也会改变模型被扰动的程度——每次调整 $r$ 时都需要重新调整学习率。

$\alpha/r$ 因子\textbf{归一化了更新幅值}，使其在不同秩下大致保持恒定：
\[
W' = W + \frac{\alpha}{r} \cdot BA
\]


\begin{itemize}
  \item \textbf{固定 $\alpha$，扫描 $r$}：有效更新幅值在不同秩下保持约为 $\alpha$。你可以尝试 $r \in \{8, 16, 32, 64\}$ 而无需重新调整学习率。
  \item \textbf{常见做法}：设置 $\alpha = r$（即 $\alpha/r = 1$）或 $\alpha = 2r$（即 $\alpha/r = 2$）。这是一种方便的默认设置，缩放因子为一个小整数。
  \item \textbf{为什么不仅仅调整学习率？}你可以这样做，但 $\alpha/r$ 提供了一个\textit{与秩无关}的调节旋钮。团队可以在不同秩的实验之间共享学习率配方。
  \item \textbf{rsLoRA 的洞见}~\cite{kalajdzievski2023rslora}：在高秩 ($r \geq 64$) 下，经验证据表明 $\alpha/\sqrt{r}$ 比 $\alpha/r$ 更稳定，因为 $BA$ 的方差随 $\sqrt{r}$ 而非 $r$ 缩放。
\end{itemize}
\end{intuitionbox}


\subsection{LoRA Hyperparameters}
\label{lora-hyperparameters}
\subsection{LoRA 超参数}
\label{lora-hyperparameters}


Choosing LoRA hyperparameters correctly is critical --- the wrong rank or alpha can either under-fit (too constrained) or waste memory (too expressive).
正确选择 LoRA 超参数至关重要——错误的秩或 alpha 要么导致欠拟合（过于受限），要么浪费内存（过于表达力强）。


\begin{table}[ht!]
\centering
\caption{LoRA hyperparameter guide.}
\caption{LoRA 超参数指南。}
\begin{tabular}{@{}lp{5cm}p{6.5cm}@{}}
\toprule
\textbf{Hyperparameter} & \textbf{Typical Values} & \textbf{Guidance} \\
\textbf{超参数} & \textbf{典型值} & \textbf{指导建议} \\
\midrule
\texttt{r} (rank) & 8, 16, 32, 64 & Higher = more capacity but more memory. Start with 16. \\
\texttt{r} (秩) & 8, 16, 32, 64 & 越高=能力越强但内存越多。从 16 开始。 \\
\texttt{lora\_alpha} & 16, 32 (often $= r$ or $2r$) & Controls update magnitude via $\alpha/r$ scaling. \\
\texttt{lora\_alpha} & 16, 32 (通常 $= r$ 或 $2r$) & 通过 $\alpha/r$ 缩放控制更新幅值。 \\
\texttt{target\_modules} & \texttt{q\_proj, k\_proj, v\_proj, o\_proj} & All attention projections. Add \texttt{gate\_proj, up\_proj, down\_proj} for full coverage. \\
\texttt{target\_modules} & \texttt{q\_proj, k\_proj, v\_proj, o\_proj} & 所有注意力投影。添加 \texttt{gate\_proj, up\_proj, down\_proj} 以获得完整覆盖。 \\
\texttt{lora\_dropout} & 0.0--0.1 & Regularization. Usually 0.05 for small datasets. \\
\texttt{lora\_dropout} & 0.0--0.1 & 正则化。小数据集通常用 0.05。 \\
\texttt{bias} & \texttt{"none"} & Training biases adds minimal params but rarely helps. \\
\texttt{bias} & \texttt{"none"} & 训练偏置项增加极少量参数但很少有帮助。 \\
Learning rate & $1\text{e-}4$ to $3\text{e-}4$ & Higher than full fine-tuning (only adapters update). \\
学习率 & $1\text{e-}4$ 到 $3\text{e-}4$ & 高于全量微调（只有适配器更新）。 \\
\bottomrule
\end{tabular}
\end{table}


\begin{warningbox}[Rank Selection Rules of Thumb]
\begin{itemize}
  \item \textbf{r=8}: Simple tasks (single-domain chat, classification). Very memory-efficient.
  \item \textbf{r=16}: General-purpose fine-tuning. Good default.
  \item \textbf{r=32--64}: Complex tasks (math, code, multi-turn reasoning). Approaches full fine-tune quality.
  \item \textbf{r=128+}: Diminishing returns; consider full fine-tuning or QLoRA with higher rank.
  \item \textbf{Key indicator}: If training loss plateaus well above full fine-tune loss, increase rank.
\end{itemize}
\end{warningbox}

\begin{warningbox}[秩选择经验法则]
\begin{itemize}
  \item \textbf{r=8}：简单任务（单领域对话、分类）。非常节省内存。
  \item \textbf{r=16}：通用微调。良好的默认值。
  \item \textbf{r=32--64}：复杂任务（数学、代码、多轮推理）。接近全量微调质量。
  \item \textbf{r=128+}：收益递减；考虑全量微调或使用更高秩的 QLoRA。
  \item \textbf{关键指标}：如果训练损失明显高于全量微调损失并出现平台期，则增加秩。
\end{itemize}
\end{warningbox}


\subsection{LoRA Variants}
\label{lora-variants}
\subsection{LoRA 变体}
\label{lora-variants}


\begin{table}[ht!]
\centering
\caption{LoRA variants and their innovations.}
\caption{LoRA 变体及其创新点。}
\begin{tabular}{@{}lp{5cm}p{6.5cm}@{}}
\toprule
\textbf{Method} & \textbf{Key Innovation} & \textbf{When to Use} \\
\textbf{方法} & \textbf{关键创新} & \textbf{何时使用} \\
\midrule
\textbf{QLoRA}~\cite{dettmers2023qlora} & 4-bit quantized base + LoRA in BF16. NF4 data type + double quantization. & Fine-tune 70B on single 48GB GPU. \\
\textbf{QLoRA}~\cite{dettmers2023qlora} & 4 位量化基座 + BF16 下的 LoRA。NF4 数据类型 + 双重量化。 & 在单张 48GB GPU 上微调 70B 模型。 \\
\textbf{DoRA}~\cite{liu2024dora} & Decomposes $W$ into magnitude and direction; LoRA updates direction only. & Better generalization for reasoning. \\
\textbf{DoRA}~\cite{liu2024dora} & 将 $W$ 分解为幅值和方向；LoRA 仅更新方向。 & 在推理任务上获得更好的泛化能力。 \\
\textbf{LoRA+}~\cite{hayou2024loraplus} & Different LRs for $A$/$B$ ($\eta_B = \lambda \eta_A$, $\lambda \approx 16$). & Free 2\% gain; no extra cost. \\
\textbf{LoRA+}~\cite{hayou2024loraplus} & 对 $A$/$B$ 使用不同的学习率 ($\eta_B = \lambda \eta_A$, $\lambda \approx 16$)。 & 免费获得 2\% 提升；无额外成本。 \\
\textbf{AdaLoRA}~\cite{zhang2023adalora} & Dynamic rank budget across layers (SVD-based importance). & Very tight compute budget. \\
\textbf{AdaLoRA}~\cite{zhang2023adalora} & 各层动态分配秩预算（基于 SVD 的重要性评估）。 & 计算预算非常紧张时使用。 \\
\textbf{rsLoRA}~\cite{kalajdzievski2023rslora} & Scales by $\alpha/\sqrt{r}$ instead of $\alpha/r$. Stable at high ranks. & When using $r \geq 64$. \\
\textbf{rsLoRA}~\cite{kalajdzievski2023rslora} & 使用 $\alpha/\sqrt{r}$ 而非 $\alpha/r$ 进行缩放。在高秩下稳定。 & 当使用 $r \geq 64$ 时。 \\
\textbf{VeRA}~\cite{kopiczko2024vera} & Shared frozen random $A, B$; trains diagonal scaling only. & Extreme param efficiency. \\
\textbf{VeRA}~\cite{kopiczko2024vera} & 共享冻结的随机 $A, B$；仅训练对角缩放。 & 极端参数效率场景。 \\
\textbf{LoRA-FA} & Freezes $A$ after init; only trains $B$. Halves LoRA memory. & Memory-constrained scenarios. \\
\textbf{LoRA-FA} & 初始化后冻结 $A$；仅训练 $B$。将 LoRA 内存减半。 & 内存受限的场景。 \\
\bottomrule
\end{tabular}
\end{table}


\subsubsection{Key Extensions Explained}
\label{key-extensions-explained}
\subsubsection{关键扩展详解}
\label{key-extensions-explained}


\paragraph{DoRA -- Weight-Decomposed Low-Rank Adaptation.}
\label{dora-weight-decomposed-low-rank-adaptation.}
\paragraph{DoRA——权重解耦低秩适配}
\label{dora-weight-decomposed-low-rank-adaptation.}


DoRA~\cite{liu2024dora} observes that full fine-tuning tends to change the \emph{direction} of weight vectors more than their magnitude. Standard LoRA conflates both. DoRA decomposes each weight column into magnitude $m = \|W\|_\text{col}$ and direction $\hat{V} = W / \|W\|_\text{col}$, then applies LoRA only to the direction: 
\[
W' = m \odot \hat{V}', \quad \hat{V}' = \frac{W + BA}{\|W + BA\|_\text{col}}
\]
 Magnitude $m$ is a separate learnable vector (one scalar per column). This consistently outperforms LoRA by 1--3\% on reasoning and instruction-following benchmarks with no additional inference cost (merged at deployment).
DoRA~\cite{liu2024dora} 观察到全量微调倾向于更多地改变权重向量的\textit{方向}而非幅值。标准 LoRA 将两者混为一谈。DoRA 将每个权重列分解为幅值 $m = \|W\|_\text{col}$ 和方向 $\hat{V} = W / \|W\|_\text{col}$，然后仅对方向应用 LoRA：
\[
W' = m \odot \hat{V}', \quad \hat{V}' = \frac{W + BA}{\|W + BA\|_\text{col}}
\]
 幅值 $m$ 是一个单独的可学习向量（每列一个标量）。在推理和指令遵循的基准测试上，它始终比 LoRA 高出 1--3\%，且不增加推理成本（部署时合并）。


\newpage
\paragraph{LoRA+ -- Asymmetric Learning Rates.}
\label{lora-asymmetric-learning-rates.}
\newpage
\paragraph{LoRA+——非对称学习率}
\label{lora-asymmetric-learning-rates.}


Hayou et al.~\cite{hayou2024loraplus} show that matrices $A$ and $B$ in LoRA have different optimal learning rates. Since $B$ is initialized to zero, it starts in a very different regime than $A$ (initialized from $\mathcal{N}(0, \sigma^2)$). Setting $\eta_B \approx 16 \times \eta_A$ improves convergence speed and final quality by $\sim$2\% --- a free gain requiring only a one-line config change:
Hayou 等人~\cite{hayou2024loraplus} 表明 LoRA 中的矩阵 $A$ 和 $B$ 具有不同的最优学习率。由于 $B$ 初始化为零，它开始的运行状态与 $A$（从 $\mathcal{N}(0, \sigma^2)$ 初始化）非常不同。设置 $\eta_B \approx 16 \times \eta_A$ 可将收敛速度和最终质量提高约 2\%——这是一个只需一行配置更改的免费收益：


\begin{lstlisting}[style=pythonstyle]
# LoRA+ in PEFT: set different LRs per matrix
optimizer_grouped_parameters = [
    {"params": [p for n, p in model.named_parameters() if "lora_B" in n],
     "lr": 2e-4 * 16},   # B matrix: higher LR
    {"params": [p for n, p in model.named_parameters() if "lora_A" in n],
     "lr": 2e-4},         # A matrix: base LR
]
# LoRA+ in PEFT: 为每个矩阵设置不同学习率
optimizer_grouped_parameters = [
    {"params": [p for n, p in model.named_parameters() if "lora_B" in n],
     "lr": 2e-4 * 16},   # B 矩阵：更高学习率
    {"params": [p for n, p in model.named_parameters() if "lora_A" in n],
     "lr": 2e-4},         # A 矩阵：基础学习率
]
\end{lstlisting}


\paragraph{VeRA -- Vector-based Random Matrix Adaptation.}
\label{vera-vector-based-random-matrix-adaptation.}
\paragraph{VeRA——基于向量的随机矩阵适配}
\label{vera-vector-based-random-matrix-adaptation.}


VeRA~\cite{kopiczko2024vera} takes parameter efficiency to the extreme: instead of learning $A$ and $B$, it \emph{freezes} them as shared random matrices across all layers and only trains two diagonal scaling vectors $d_b \in \mathbb{R}^r$ and $d_a \in \mathbb{R}^d$: 
\[
\Delta W = B \cdot \text{diag}(d_b) \cdot A \cdot \text{diag}(d_a)
\]
 This reduces trainable parameters by $\sim$10$\times$ vs.~LoRA (only $r + d$ params per layer) while achieving 90--95\% of LoRA quality. Best for scenarios where you need hundreds of task-specific adapters with minimal storage.
VeRA~\cite{kopiczko2024vera} 将参数效率推向了极致：它不是学习 $A$ 和 $B$，而是将它们\textit{冻结}为跨所有层共享的随机矩阵，仅训练两个对角缩放向量 $d_b \in \mathbb{R}^r$ 和 $d_a \in \mathbb{R}^d$：
\[
\Delta W = B \cdot \text{diag}(d_b) \cdot A \cdot \text{diag}(d_a)
\]
 这使可训练参数比 LoRA 减少了约 10 倍（每层仅 $r + d$ 个参数），同时达到 LoRA 质量的 90--95\%。最适合需要数百个任务特定适配器且存储最小的场景。


\begin{examplebox}[QLoRA Memory Savings]
\textbf{70B model full fine-tune}: 140 GB (weights) + 280 GB (optimizer) + 140 GB (gradients) = 560 GB (7$\times$ A100-80GB).


\textbf{70B QLoRA (r=16, all linear layers)}:


\begin{itemize}
  \item Base model in NF4: $70\text{B} \times 0.5 = 35$ GB
  \item LoRA adapters in BF16: $\sim$160 MB
  \item Optimizer states (only for adapters): $\sim$320 MB
  \item Activations (gradient checkpointing): $\sim$8 GB
  \item \textbf{Total: $\sim$44 GB} --- fits in a single 48GB GPU!
\end{itemize}
\end{examplebox}

\begin{examplebox}[QLoRA 内存节省]
\textbf{70B 模型全量微调}：140 GB（权重）+ 280 GB（优化器）+ 140 GB（梯度）= 560 GB（7$\times$ A100-80GB）。


\textbf{70B QLoRA (r=16, 所有线性层)}：


\begin{itemize}
  \item NF4 格式的基座模型：$70\text{B} \times 0.5 = 35$ GB
  \item BF16 格式的 LoRA 适配器：约 160 MB
  \item 优化器状态（仅适配器）：约 320 MB
  \item 激活值（梯度检查点）：约 8 GB
  \item \textbf{总计：约 44 GB}——可放入单张 48GB GPU！
\end{itemize}
\end{examplebox}


\begin{lstlisting}[style=pythonstyle]
# QLoRA configuration with PEFT
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import BitsAndBytesConfig
import torch


# 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",           # NormalFloat4 - optimal for weights
    bnb_4bit_compute_dtype=torch.bfloat16, # Compute in BF16
    bnb_4bit_use_double_quant=True,       # Quantize the quantization constants
)
# 使用 PEFT 的 QLoRA 配置
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import BitsAndBytesConfig
import torch


# 4 位量化配置
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",           # NormalFloat4 - 权重最优
    bnb_4bit_compute_dtype=torch.bfloat16, # 在 BF16 中计算
    bnb_4bit_use_double_quant=True,       # 对量化常数进行量化
)
\end{lstlisting}

```markdown
# LoRA config
# LoRA 配置

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,                        # alpha/r = 2x scaling
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = prepare_model_for_kbit_training(model)  # Prepare for QLoRA
model = get_peft_model(model, lora_config)       # Add LoRA adapters
model.print_trainable_parameters()
# Output: trainable params: 83,886,080 || all params: 70,553,706,496 || 0.12%
\end{lstlisting}
# 输出: trainable params: 83,886,080 || all params: 70,553,706,496 || 0.12%
\end{lstlisting}


\subsection{Other PEFT Approaches}
\subsection{其他 PEFT 方法}
\label{other-peft-approaches}


LoRA dominates modern practice, but it is not the only parameter-efficient method. For completeness, the main alternatives:
LoRA 主导了现代实践，但它并非唯一的参数高效方法。为完整起见，以下是主要替代方案：


\begin{table}[ht!]
\centering
\caption{PEFT method families. LoRA is the de facto standard for LLM fine-tuning; the others are included for historical context and niche use cases.}
\caption{PEFT 方法族。LoRA 是 LLM 微调的事实标准；其他方法则因历史背景和特定用例而收录。}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{4cm}@{}}
\toprule
\textbf{Method} & \textbf{Mechanism} & \textbf{Pros / Cons} & \textbf{Status} \\
\textbf{方法} & \textbf{机制} & \textbf{优点/缺点} & \textbf{状态} \\
\midrule
\textbf{LoRA}~\cite{hu2021lora} (and variants) & Low-rank matrices added to existing weights & Mergeable at inference (zero overhead); well-supported; works for all architectures & \textbf{Standard} \\
\textbf{LoRA}~\cite{hu2021lora}（及变体） & 向现有权重添加低秩矩阵 & 推理时可合并（零开销）；支持良好；适用于所有架构 & \textbf{标准} \\
\textbf{Adapters}~\cite{houlsby2019adapters} & Small bottleneck MLPs inserted between layers & Modular; stackable; adds inference latency (extra sequential layers) & Rarely used \\
\textbf{适配器 (Adapters)}~\cite{houlsby2019adapters} & 在层间插入小型瓶颈 MLP & 模块化；可堆叠；增加推理延迟（额外的顺序层） & 很少使用 \\
\textbf{Prefix Tuning}~\cite{li2021prefix} & Learnable ``virtual tokens'' prepended to keys/values at each layer & No weight modification; effective for generation tasks; consumes context length & Niche \\
\textbf{前缀微调 (Prefix Tuning)}~\cite{li2021prefix} & 在每个层的键/值前添加可学习的“虚拟令牌” & 不修改权重；对生成任务有效；消耗上下文长度 & 小众 \\
\textbf{Prompt Tuning}~\cite{lester2021prompt} & Learnable soft prompt embeddings prepended to input & Extremely few params ($<$0.01\%); weaker than LoRA for complex tasks & Niche \\
\textbf{提示微调 (Prompt Tuning)}~\cite{lester2021prompt} & 在输入前添加可学习的软提示嵌入 & 参数极少（$<$0.01\%）；在复杂任务上弱于 LoRA & 小众 \\
\textbf{IA3}~\cite{liu2022ia3} & Learned vectors that rescale keys, values, and FFN activations & Even fewer params than LoRA; mergeable; limited capacity & Deprecated \\
\textbf{IA3}~\cite{liu2022ia3} & 学习缩放键、值和 FFN 激活的向量 & 参数比 LoRA 更少；可合并；容量有限 & 已弃用 \\
\textbf{BitFit}~\cite{zaken2022bitfit} & Train only bias terms & Near-zero params; surprisingly effective for simple tasks; limited expressiveness & Historical \\
\textbf{BitFit}~\cite{zaken2022bitfit} & 仅训练偏置项 & 参数接近零；对简单任务出奇有效；表达能力有限 & 历史 \\
\bottomrule
\end{tabular}
\end{table}


\begin{intuitionbox}[Why LoRA Won]
\begin{intuitionbox}[LoRA 为何胜出]
LoRA became the standard because it uniquely combines: (1)~\textbf{zero inference overhead} --- adapters merge into base weights, unlike Adapters or Prefix Tuning which add latency or consume context; (2)~\textbf{composability} --- multiple LoRA adapters can be swapped at serving time for multi-tenant deployments; (3)~\textbf{ecosystem support} --- HuggingFace PEFT, TRL, vLLM, and all major frameworks have first-class LoRA support; (4)~\textbf{proven at scale} --- used in production by Meta, Google, and most open-source fine-tunes on HuggingFace. Unless you have a specific constraint that LoRA cannot satisfy, it should be your default choice.
LoRA 成为标准是因为它独特地结合了：(1)~\textbf{零推理开销} —— 适配器可合并到基权重中，不像适配器 (Adapters) 或前缀微调 (Prefix Tuning) 那样增加延迟或消耗上下文；(2)~\textbf{可组合性} —— 服务时可切换多个 LoRA 适配器以实现多租户部署；(3)~\textbf{生态系统支持} —— HuggingFace PEFT、TRL、vLLM 以及所有主流框架都对 LoRA 提供了一流支持；(4)~\textbf{大规模验证} —— 已被 Meta、Google 以及 HuggingFace 上的大多数开源微调模型在生产中使用。除非你有 LoRA 无法满足的特定约束，否则它应该是你的默认选择。
\end{intuitionbox}


\clearpage
\section{Mixture of Experts (MoE)}
\section{混合专家 (Mixture of Experts, MoE)}
\label{mixture-of-experts-moe}


Mixture of Experts models~\cite{shazeer2017outrageously, jiang2024mixtral} scale model capacity without proportionally scaling compute cost by activating only a subset of parameters for each token.
混合专家 (Mixture of Experts, MoE) 模型~\cite{shazeer2017outrageously, jiang2024mixtral} 通过仅为每个令牌激活一部分参数，在不按比例增加计算成本的情况下扩展模型容量。


\subsection{Architecture}
\subsection{架构}
\label{architecture}


\begin{keybox}[MoE Layer]
\begin{keybox}[MoE 层]
In a MoE transformer, the FFN layer in each block is replaced by $N$ parallel ``expert'' FFNs plus a \textbf{router} that selects which experts to use: 
在 MoE 变换器中，每个块中的 FFN 层被替换为 $N$ 个并行的“专家”FFN 加上一个 \textbf{路由器}，该路由器选择使用哪些专家：
\[
\text{MoE}(x) = \sum_{i=1}^{N} g_i(x) \cdot E_i(x), \quad g(x) = \text{TopK}(\text{softmax}(W_r x))
\]


\begin{itemize}
  \item $E_i$ are expert networks (standard FFN layers)
  \item $g_i(x)$ are gating weights from the router (only top-$K$ are non-zero)
  \item Typically $K=2$ out of $N=8$--64 experts are active per token
  \item Total params scale with $N$; \textbf{active params} scale with $K/N$ of FFN size
\end{itemize}
\begin{itemize}
  \item $E_i$ 是专家网络（标准 FFN 层）
  \item $g_i(x)$ 是路由器的门控权重（仅 top-$K$ 非零）
  \item 通常每个令牌激活 $N=8$--64 个专家中的 $K=2$ 个
  \item 总参数随 $N$ 扩展；\textbf{活跃参数} 随 FFN 大小的 $K/N$ 扩展
\end{itemize}
\end{keybox}


\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_012_fig12.png}
\caption{MoE layer with 8 experts and Top-2 routing. Only the two highest-gated experts are computed per token; the rest are skipped entirely.}
\caption{具有 8 个专家和 Top-2 路由的 MoE 层。每个令牌仅计算门控得分最高的两个专家；其余专家被完全跳过。}
\end{figure}


\subsection{Load Balancing}
\subsection{负载均衡}
\label{load-balancing}


\begin{warningbox}[The Load Balancing Problem]
\begin{warningbox}[负载均衡问题]
Without constraints, the router may send most tokens to the same 1--2 experts (``expert collapse''). This wastes capacity and creates compute imbalance across GPUs (each expert typically lives on a different GPU).
在没有约束的情况下，路由器可能将大多数令牌发送给相同的 1--2 个专家（“专家崩溃”）。这会浪费容量并在 GPU 之间造成计算不平衡（每个专家通常位于不同的 GPU 上）。


\textbf{Solution}: Add an auxiliary load-balancing loss: 
\textbf{解决方案}：添加一个辅助负载均衡损失：
\[
\mathcal{L}_{\text{bal}} = \alpha \cdot N \sum_{i=1}^{N} f_i \cdot p_i
\]
 where $f_i$ = fraction of tokens routed to expert $i$, $p_i$ = mean router probability for expert $i$. This encourages uniform expert utilization.
其中 $f_i$ = 路由到专家 $i$ 的令牌比例，$p_i$ = 专家 $i$ 的平均路由器概率。这鼓励专家利用率均匀分布。
\end{warningbox}


\subsection{Noisy Top-K Gating: Making Discrete Routing Trainable}
\subsection{带噪声的 Top-K 门控：使离散路由可训练}
\label{noisy-top-k-gating-making-discrete-routing-trainable}


The core challenge in MoE is that \textbf{top-$k$ selection is not differentiable} --- you can’t backpropagate through a hard ``pick the top 2'' operation. The field has developed two key tricks to solve this:
MoE 的核心挑战是 \textbf{top-$k$ 选择不可微} —— 你无法通过硬性的“选择前 top 2”操作进行反向传播。该领域已开发出两种关键技巧来解决这个问题：


\begin{intuitionbox}[The Routing Differentiability Problem]
\begin{intuitionbox}[路由可微性问题]
The router computes logits $h(x) = W_r \cdot x$ for each expert, then selects the top-$k$. But:
路由器为每个专家计算 logits $h(x) = W_r \cdot x$，然后选择 top-$k$。但是：


\begin{itemize}
  \item The \emph{selected} experts get gradients through their gate weights (softmax over selected)
  \item The \emph{selection decision itself} (which $k$ to pick) has zero gradient
  \item Without a trick, the router can get stuck: an expert never selected $\rightarrow$ never gets a gradient signal $\rightarrow$ never gets selected
\end{itemize}
\begin{itemize}
  \item \emph{被选中的}专家通过其门控权重（对选定者做 softmax）获得梯度
  \item \emph{选择决策本身}（选择哪个 $k$）的梯度为零
  \item 没有技巧的话，路由器可能陷入困境：一个专家从未被选中 $\rightarrow$ 从未获得梯度信号 $\rightarrow$ 永远不被选中
\end{itemize}
\end{intuitionbox}


\paragraph{Approach 1: Noisy Top-K Gating~\cite{shazeer2017outrageously}.}
\paragraph{方法 1：带噪声的 Top-K 门控 (Noisy Top-K Gating)~\cite{shazeer2017outrageously}。}
\label{approach-1-noisy-top-k-gating-.}


Add learnable Gaussian noise to the router logits \emph{before} the top-$k$ selection:
在 top-$k$ 选择\emph{之前}向路由器 logits 添加可学习的高斯噪声：


\begin{align}
  h(x) &= W_g \cdot x \tag{clean logits} \\
  H(x) &= h(x) + \epsilon \cdot \text{Softplus}(W_{\text{noise}} \cdot x), \quad \epsilon \sim \mathcal{N}(0, 1) \tag{noisy logits} \\
  \text{TopK}(v, k)_i &= \begin{cases} v_i & \text{if } v_i \text{ is in the top } k \\ -\infty & \text{otherwise} \end{cases} \\
  g(x) &= \text{softmax}\big(\text{TopK}(H(x),\, k)\big) \tag{sparse gates}
\end{align}
\begin{align}
  h(x) &= W_g \cdot x \tag{干净的 logits} \\
  H(x) &= h(x) + \epsilon \cdot \text{Softplus}(W_{\text{noise}} \cdot x), \quad \epsilon \sim \mathcal{N}(0, 1) \tag{带噪声的 logits} \\
  \text{TopK}(v, k)_i &= \begin{cases} v_i & \text{if } v_i \text{ is in the top } k \\ -\infty & \text{otherwise} \end{cases} \\
  g(x) &= \text{softmax}\big(\text{TopK}(H(x),\, k)\big) \tag{稀疏门控}
\end{align}


\begin{itemize}
  \item $W_{\text{noise}}$ is a \emph{learned} noise magnitude --- the model learns how much exploration each expert needs
  \item During training, noise occasionally promotes ``underdog'' experts into the top-$k$, giving them gradient signal
  \item At inference, noise is removed: use clean logits $h(x)$ for deterministic routing
  \item The Softplus ensures noise scale is always positive
\end{itemize}
\begin{itemize}
  \item $W_{\text{noise}}$ 是一个\emph{可学习的}噪声幅度——模型学习每个专家需要多少探索
  \item 在训练期间，噪声偶尔会将“弱势”专家提升到 top-$k$ 中，从而为它们提供梯度信号
  \item 在推理时，移除噪声：使用干净的 logits $h(x)$ 进行确定性路由
  \item Softplus 确保噪声尺度始终为正
\end{itemize}


\paragraph{Approach 2: Gumbel-Softmax Trick (for differentiable discrete sampling).}
\paragraph{方法 2：Gumbel-Softmax 技巧（用于可微的离散采样）。}
\label{approach-2-gumbel-softmax-trick-for-differentiable-discrete-sampling.}


An alternative from the variational inference literature~\cite{jang2017categorical}. The \textbf{Gumbel-Max trick} provides exact sampling from a categorical distribution:
另一种方法来自变分推断文献~\cite{jang2017categorical}。\textbf{Gumbel-Max 技巧}提供了从分类分布中精确采样的方法：


\begin{equation}
  z = \arg\max_i \left[ \log \pi_i + G_i \right], \quad G_i \sim \text{Gumbel}(0,1)
\end{equation}


where Gumbel noise is generated as $G_i = -\log(-\log(U_i)),\; U_i \sim \text{Uniform}(0,1)$.
其中 Gumbel 噪声生成方式为 $G_i = -\log(-\log(U_i)),\; U_i \sim \text{Uniform}(0,1)$。


For \textbf{top-$k$ routing}: taking the top-$k$ of $(\log \pi_i + G_i)$ gives $k$ samples \emph{without replacement} from the categorical distribution defined by $\pi$.
对于 \textbf{top-$k$ 路由}：取 $(\log \pi_i + G_i)$ 的前 top-$k$ 个，得到从 $\pi$ 定义的分类分布中\emph{无放回}的 $k$ 个样本。


Since $\arg\max$ is non-differentiable, the \textbf{Gumbel-Softmax} relaxation replaces it with a temperature-controlled softmax:
由于 $\arg\max$ 不可微，\textbf{Gumbel-Softmax} 松弛将其替换为受温度控制的 softmax：


\begin{equation}
  \hat{g}_i = \frac{\exp\left((\log \pi_i + G_i) / \tau\right)}{\sum_j \exp\left((\log \pi_j + G_j) / \tau\right)}
\end{equation}
```

\begin{itemize}
  \item $\tau \to 0$: approaches a hard one-hot (exact but non-differentiable)
  \item $\tau \to 0$：趋近于硬独热（精确但不可微）
  \item $\tau \to \infty$: approaches uniform (differentiable but uninformative)
  \item $\tau \to \infty$：趋近于均匀分布（可微但信息量低）
  \item In practice, anneal $\tau$ from 1.0 down to 0.1--0.5 during training
  \item 在实际训练中，将 $\tau$ 从 1.0 退火至 0.1--0.5
  \item \textbf{Straight-through estimator（直通估计器）}: use hard top-$k$ in the forward pass, but Gumbel-Softmax gradients in the backward pass --- best of both worlds
  \item \textbf{Straight-through estimator（直通估计器）}：在前向传播中使用硬 top-$k$，但在反向传播中使用 Gumbel-Softmax 梯度——两全其美
\end{itemize}

\begin{keybox}[实践中使用哪种方法？]
\begin{itemize}
  \item \textbf{Sparsely-Gated MoE~\cite{shazeer2017outrageously}, Mixtral~\cite{jiang2024mixtral}, DeepSeek-V2~\cite{deepseekv2}}: Use Noisy Top-K with Gaussian noise. Simple, effective, well-proven at scale.
  \item \textbf{Sparsely-Gated MoE~\cite{shazeer2017outrageously}、Mixtral~\cite{jiang2024mixtral}、DeepSeek-V2~\cite{deepseekv2}}：使用带高斯噪声的Noisy Top-K。简单、有效，在大规模上得到了充分验证。
  \item \textbf{Switch Transformer~\cite{fedus2022switch}}: Simplified to Top-1 with no noise (relies on load-balancing loss alone).
  \item \textbf{Switch Transformer~\cite{fedus2022switch}}：简化为无噪声的Top-1（仅依赖于负载均衡损失）。
  \item \textbf{Research / smaller-scale MoE}: Some use Gumbel-Softmax for fully differentiable routing, especially when learning the routing itself is the research objective.
  \item \textbf{研究/小规模MoE}：有些使用Gumbel-Softmax实现完全可微路由，尤其是当学习路由本身是研究目标时。
  \item \textbf{Key insight}: Both approaches solve the same problem (making discrete selection trainable) via noise injection. Gaussian noise is simpler; Gumbel noise has stronger theoretical guarantees for categorical sampling.
  \item \textbf{关键洞察}：这两种方法都通过注入噪声解决了同一个问题（使离散选择可训练）。高斯噪声更简单；Gumbel噪声在类别采样方面具有更强的理论保证。
\end{itemize}
\end{keybox}

\subsection{Notable MoE Models}
\subsection{值得关注的MoE模型}
\label{notable-moe-models}

\begin{tabular}{@{}lp{2.5cm}p{2.8cm}p{2.8cm}p{2.8cm}@{}}
\toprule
\textbf{Model} & \textbf{Total Params} & \textbf{Active Params} & \textbf{Experts} & \textbf{Innovation} \\
\textbf{模型} & \textbf{总参数量} & \textbf{激活参数量} & \textbf{专家数} & \textbf{创新点} \\
\midrule
Switch Transformer~\cite{fedus2022switch} & 1.6T & 100B & 128, Top-1 & First large-scale MoE; simplified routing \\
Switch Transformer~\cite{fedus2022switch} & 1.6T & 100B & 128, Top-1 & 首个大规模MoE；简化路由 \\
Mixtral 8x7B~\cite{jiang2024mixtral} & 47B & 13B & 8, Top-2 & Open-weight; matches Llama-2 70B quality \\
Mixtral 8x7B~\cite{jiang2024mixtral} & 47B & 13B & 8, Top-2 & 开源权重；匹配Llama-2 70B质量 \\
DeepSeek-V2~\cite{deepseekv2} & 236B & 21B & 160, Top-6 & DeepSeekMoE with shared + routed experts \\
DeepSeek-V2~\cite{deepseekv2} & 236B & 21B & 160, Top-6 & DeepSeekMoE结合共享专家和路由专家 \\
Qwen-MoE~\cite{qwen2024qwen25} & 14.3B & 2.7B & 60, Top-4 & Fine-grained experts for efficiency \\
Qwen-MoE~\cite{qwen2024qwen25} & 14.3B & 2.7B & 60, Top-4 & 细粒度专家以提高效率 \\
DBRX~\cite{databricks2024dbrx} & 132B & 36B & 16, Top-4 & Fine-grained with 4 experts per block \\
DBRX~\cite{databricks2024dbrx} & 132B & 36B & 16, Top-4 & 每个块4个专家的细粒度结构 \\
\bottomrule
\end{tabular}

\section{Diversity in LLM Training}
\section{LLM训练中的多样性}
\label{diversity-in-llm-training}

Diversity --- in training data, model outputs, and optimization trajectories --- is critical for preventing mode collapse and ensuring robust, general-purpose LLMs. This section covers the key diversity mechanisms applicable to all LLM training phases.
多样性——在训练数据、模型输出和优化轨迹中——对于防止模式崩溃和确保稳健、通用的LLM至关重要。本节涵盖了适用于所有LLM训练阶段的关键多样性机制。

\subsection{Sampling Diversity}
\subsection{采样多样性}
\label{sampling-diversity}

\begin{keybox}[多样生成的采样策略]
\begin{itemize}
  \item \textbf{Temperature $\tau$}: $P(x_i) \propto \exp(\text{logit}_i / \tau)$. Higher $\tau$ = more uniform distribution = more diverse. Typical: $\tau=0.7$--$1.0$ for RLHF generation.
  \item \textbf{温度 $\tau$}：$P(x_i) \propto \exp(\text{logit}_i / \tau)$。更高的 $\tau$ = 更均匀的分布 = 更多样化。典型值：RLHF生成中 $\tau=0.7$--$1.0$。
  \item \textbf{Top-$k$}: Only sample from the $k$ highest-probability tokens. Prevents degenerate low-probability tokens.
  \item \textbf{Top-$k$}：仅从概率最高的 $k$ 个token中采样。防止出现退化的低概率token。
  \item \textbf{Top-$p$ (nucleus)}: Sample from the smallest set of tokens whose cumulative probability $\geq p$. Adaptive: more diverse when the model is uncertain.
  \item \textbf{Top-$p$（核心采样）}：从累积概率 $\geq p$ 的最小token集合中采样。自适应：当模型不确定时更多样化。
  \item \textbf{Min-$p$}: Only keep tokens with $P \geq p_{\min} \times P_{\max}$. More principled than top-$k$.
  \item \textbf{Min-$p$}：仅保留 $P \geq p_{\min} \times P_{\max}$ 的token。比 top-$k$ 更合理。
  \item \textbf{Frequency/presence penalty}: Penalize tokens that appeared in the response. Encourages lexical diversity.
  \item \textbf{频率/出现惩罚}：惩罚在响应中出现过的token。鼓励词汇多样性。
\end{itemize}
\end{keybox}

\subsection{Training Data Diversity}
\subsection{训练数据多样性}
\label{training-data-diversity}

\begin{itemize}
  \item \textbf{Prompt diversity（提示多样性）}: Cover different domains, difficulty levels, and formats. The Goldilocks principle: prompts should have 20--80\% success rate.
  \item \textbf{Prompt diversity（提示多样性）}：覆盖不同领域、难度级别和格式。金发姑娘原则：提示应具有20--80%的成功率。
  \item \textbf{Deduplication}: Remove near-duplicate training examples (MinHash, n-gram overlap). Duplicates cause overfitting to specific patterns.
  \item \textbf{去重}：移除近似重复的训练样本（MinHash、n-gram重叠）。重复会导致对特定模式的过拟合。
  \item \textbf{Data mixing}: Balance across tasks/domains using temperature-weighted sampling or curriculum strategies.
  \item \textbf{数据混合}：使用温度加权采样或课程策略来平衡不同任务/领域。
\end{itemize}

\subsection{Diversity-Promoting Methods}
\subsection{促进多样性的方法}
\label{diversity-promoting-methods}

\begin{tabular}{@{}lp{11cm}@{}}
\toprule
\textbf{Method} & \textbf{How It Promotes Diversity} \\
\textbf{方法} & \textbf{如何促进多样性} \\
\midrule
Temperature scaling & Higher $\tau$ flattens the distribution; more tokens become plausible. \\
温度缩放 & 更高的 $\tau$ 使分布更平坦；更多token变得可行。 \\
Top-$p$ / Min-$p$ & Adaptive thresholds allow wider sampling when the model is uncertain. \\
Top-$p$ / Min-$p$ & 自适应阈值允许在模型不确定时进行更广泛的采样。 \\
Frequency penalty & Penalizes repeated tokens, forcing lexical variety within a response. \\
频率惩罚 & 惩罚重复的token，强制在响应中产生词汇多样性。 \\
Data deduplication & Removing near-duplicates from training data prevents overfitting to specific patterns. \\
数据去重 & 从训练数据中移除近似重复项可防止对特定模式的过拟合。 \\
Multi-domain mixing & Temperature-weighted sampling across domains ensures broad coverage. \\
多领域混合 & 跨领域的温度加权采样确保广泛覆盖。 \\
Verbalized sampling & Prompt the model to explicitly verbalize a probability distribution over responses~\cite{zhang2025verbalized}. See §\ref{grpo-variants-and-extensions}. \\
口头化采样 & 提示模型明确口头表达对响应的概率分布~\cite{zhang2025verbalized}。参见§\ref{grpo-variants-and-extensions}。 \\
\bottomrule
\end{tabular}

\section{Text Generation: Decoding Methods}
\section{文本生成：解码方法}
\label{text-generation-decoding-methods}

A trained language model outputs a probability distribution over the vocabulary at each step: $P(x_t | x_{<t})$. The \textbf{decoding strategy} determines how we select the next token from this distribution. This choice profoundly affects output quality, diversity, and coherence.
训练好的语言模型在每个步骤输出词汇表上的概率分布：$P(x_t | x_{<t})$。\textbf{解码策略}决定了我们如何从该分布中选择下一个token。这一选择深刻影响输出质量、多样性和连贯性。

\subsection{Greedy Decoding}
\subsection{贪心解码}
\label{greedy-decoding}

The simplest strategy: always pick the highest-probability token. 
\[
x_t = \arg\max_{v \in \mathcal{V}} P(v | x_{<t})
\]
最简单的策略：总是选择概率最高的token。 
\[
x_t = \arg\max_{v \in \mathcal{V}} P(v | x_{<t})
\]

\textbf{Int

\textbf{Intuition:} After ``The cat sat on the...'', only consider the top $k$ plausible continuations (``mat'', ``floor'', ``couch'', ...) and ignore extremely unlikely ones (``quantum'', ``archipelago'').

\textbf{直觉：} 在“The cat sat on the...”之后，只考虑最可能的 $k$ 个续词（“mat”、“floor”、“couch”……），忽略极不可能的续词（“quantum”、“archipelago”）。

\textbf{Pros:} Removes tail noise; simple to implement.\\

\textbf{优点：} 去除尾部噪声；实现简单。\\

\textbf{Cons:} Fixed $k$ is too restrictive for peaked distributions (wastes probability mass) and too permissive for flat distributions (lets in garbage tokens).

\textbf{缺点：} 固定的 $k$ 对于尖峰分布（概率质量浪费）过于严格，对于平坦分布（允许垃圾词进入）过于宽松。

\subsection{Top-$p$ (Nucleus) Sampling}
\subsection{Top-$p$（核）采样}
\label{top-p-nucleus-sampling}

Sample from the smallest set of tokens whose cumulative probability exceeds $p$: 
\[
\text{Top-}p = \min \left\{ S \subseteq \mathcal{V} : \sum_{v \in S} P(v | x_{<t}) \geq p \right\}
\]
 where tokens are sorted by descending probability and added until the threshold $p$ is reached.

从累积概率超过 $p$ 的最小词元集合中采样：
\[
\text{Top-}p = \min \left\{ S \subseteq \mathcal{V} : \sum_{v \in S} P(v | x_{<t}) \geq p \right\}
\]
其中词元按概率降序排列并逐个添加，直到达到阈值 $p$。

\textbf{Intuition:} Adaptively resize the candidate pool. If the model is confident (``Paris'' at 95\%), the nucleus is tiny. If uncertain (``The movie was...''), the nucleus expands to include many plausible adjectives.

\textbf{直觉：} 自适应调整候选池大小。如果模型很确信（“Paris”概率为95%），则核很小。如果不确定（“The movie was...”），则核会扩大以包含许多可能的形容词。

\textbf{Pros:} Adapts to distribution shape; widely used default ($p=0.9$--$0.95$).\\

\textbf{优点：} 适应分布形状；广泛使用的默认值（$p=0.9$--$0.95$）。\\

\textbf{Cons:} Still includes some low-quality tokens at the tail of the nucleus; the threshold is a single global hyperparameter.

\textbf{缺点：} 仍包含核尾部的一些低质量词元；阈值是单一的全局超参数。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_014_fig14.png}
\caption{Top-$p$ (nucleus) sampling: tokens are sorted by probability and included until cumulative mass reaches $p=0.9$. The nucleus (dark blue) adapts its size to the distribution shape --- here 5 tokens suffice.}
\caption{Top-$p$（核）采样：词元按概率排序并加入，直到累积质量达到 $p=0.9$。核（深蓝色）根据分布形状自适应调整大小——此处5个词元即够。}
\end{figure}

\begin{intuitionbox}[Top-kk vs. Top-pp]
Consider predicting the next word:

\begin{intuitionbox}[Top-kk vs. Top-pp]
考虑预测下一个词：

\begin{itemize}
  \item After ``2 + 2 ='': distribution is peaked --- top-1 token (``4'') has 99\% mass. Top-$k$=50 wastefully considers 49 wrong answers. Top-$p$=0.9 correctly picks just ``4''.
  \item After ``I enjoy eating'': distribution is flat --- many foods are plausible. Top-$k$=5 is too restrictive. Top-$p$=0.9 might include 50+ tokens, matching the actual uncertainty.
\end{itemize}

\begin{itemize}
  \item 在“2 + 2 =”之后：分布是尖峰型——top-1词元（“4”）占99%质量。Top-$k$=50浪费地考虑了49个错误答案。Top-$p$=0.9正确只选择“4”。
  \item 在“I enjoy eating”之后：分布平坦——很多食物都可能。Top-$k$=5过于严格。Top-$p$=0.9可能包含50+个词元，符合实际不确定性。
\end{itemize}

Top-$p$ adapts; top-$k$ doesn’t. In practice, both are often combined: sample from top-$p$ intersected with top-$k$.
\end{intuitionbox}

Top-$p$ 自适应；top-$k$ 不会。实践中常将两者结合：从 top-$p$ 与 top-$k$ 的交集中采样。
\end{intuitionbox}

\subsection{Min-$p$ Sampling}
\subsection{Min-$p$ 采样}
\label{min-p-sampling}

A recent alternative that sets a \textbf{relative} probability floor~\cite{nguyen2024minp}: 
\[
\text{Min-}p = \left\{ v \in \mathcal{V} : P(v | x_{<t}) \geq p_{\min} \cdot \max_{v'} P(v' | x_{<t}) \right\}
\]
 Only tokens with probability at least $p_{\min}$ times the top token’s probability are kept.

一种近期的替代方案，设定一个**相对**概率下限~\cite{nguyen2024minp}：
\[
\text{Min-}p = \left\{ v \in \mathcal{V} : P(v | x_{<t}) \geq p_{\min} \cdot \max_{v'} P(v' | x_{<t}) \right\}
\]
只保留概率至少为 top 词元概率 $p_{\min}$ 倍的词元。

\textbf{Intuition:} ``Only consider tokens that are at least 10\% as likely as the best token.'' If the top token has probability 0.8, only tokens above 0.08 survive. If the top token has probability 0.05 (very uncertain), tokens above 0.005 survive --- naturally expanding the pool.

\textbf{直觉：} “只考虑概率至少为最佳词元10%的词元。”如果 top 词元概率为0.8，则只有大于0.08的词元保留。如果 top 词元概率为0.05（非常不确定），则大于0.005的词元保留——自然地扩大词元池。

\textbf{Pros:} Scales naturally with model confidence; fewer degenerate samples than top-$p$ on peaked distributions; single intuitive parameter.\\

\textbf{优点：} 随模型置信度自然缩放；在尖峰分布上比 top-$p$ 产生更少的退化样本；单个直观参数。\\

\textbf{Cons:} Newer, less battle-tested; not yet standard in all inference frameworks.

\textbf{缺点：} 较新，测试不够充分；尚未成为所有推理框架的标准。

\subsection{Temperature Scaling}
\subsection{温度缩放}
\label{temperature-scaling}

Before applying any sampling strategy, logits are divided by temperature $T$: 
\[
P_T(v | x_{<t}) = \frac{\exp(z_v / T)}{\sum_{v'} \exp(z_{v'} / T)}
\]

在应用任何采样策略之前，logits 被温度 $T$ 除：
\[
P_T(v | x_{<t}) = \frac{\exp(z_v / T)}{\sum_{v'} \exp(z_{v'} / T)}
\]

\begin{itemize}
  \item $T < 1$: Sharpens distribution $\to$ more deterministic, focused outputs.
  \item $T = 1$: Unmodified model distribution.
  \item $T > 1$: Flattens distribution $\to$ more random, creative outputs.
  \item $T \to 0$: Becomes greedy decoding. $T \to \infty$: Becomes uniform sampling.
\end{itemize}

\begin{itemize}
  \item $T < 1$：锐化分布 $\to$ 更确定、更聚焦的输出。
  \item $T = 1$：未修改的模型分布。
  \item $T > 1$：展平分布 $\to$ 更随机、更具创造性的输出。
  \item $T \to 0$：变为贪心解码。$T \to \infty$：变为均匀采样。
\end{itemize}

\textbf{Common settings:} $T=0.7$ for factual tasks, $T=1.0$--$1.2$ for creative writing, $T=0.0$ (greedy) for code/math.

\textbf{常用设置：} 事实性任务 $T=0.7$，创意写作 $T=1.0$--$1.2$，代码/数学 $T=0.0$（贪心）。

\subsection{Contrastive Decoding}
\subsection{对比解码}
\label{contrastive-decoding}

Contrastive decoding~\cite{li2023contrastive} exploits the difference between a strong model (expert) and a weak model (amateur) to amplify the expert’s unique knowledge: 
\[
x_t = \arg\max_{v \in \mathcal{V}(x_{<t})} \left[ \log P_{\text{expert}}(v | x_{<t}) - \log P_{\text{amateur}}(v | x_{<t}) \right]
\]
 where $\mathcal{V}(x_{<t}) = \{v : P_{\text{expert}}(v | x_{<t}) \geq \alpha \cdot \max_{v'} P_{\text{expert}}(v' | x_{<t})\}$ is an adaptive plausibility constraint.

对比解码~\cite{li2023contrastive} 利用强模型（专家）与弱模型（业余者）之间的差异来放大专家的独特知识：
\[
x_t = \arg\max_{v \in \mathcal{V}(x_{<t})} \left[ \log P_{\text{expert}}(v | x_{<t}) - \log P_{\text{amateur}}(v | x_{<t}) \right]
\]
其中 $\mathcal{V}(x_{<t}) = \{v : P_{\text{expert}}(v | x_{<t}) \geq \alpha \cdot \max_{v'} P_{\text{expert}}(v' | x_{<t})\}$ 是一个自适应合理性约束。

\textbf{Intuition:} The amateur model captures generic, obvious patterns (common words, repetition). Subtracting its log-probabilities removes this ``generic signal,'' leaving the expert’s distinctive knowledge and reasoning. Like removing background noise from a recording to hear the signal.

\textbf{直觉：} 业余者模型捕捉通用、明显的模式（常见词、重复）。减去其对数概率可去除这种“通用信号”，留下专家的独特知识和推理。就像从录音中去除背景噪声以听到信号。

\textbf{Pros:} Reduces repetition and generic phrasing; improves factuality and coherence without additional training; works with any model pair.\\

\textbf{优点：} 减少重复和通用措辞；无需额外训练即可提高事实性和连贯性；适用于任何模型对。\\

\textbf{Cons:} Requires running two models (2$\times$ compute); sensitive to amateur model choice; the plausibility threshold $\alpha$ needs tuning.

\textbf{缺点：} 需要运行两个模型（2倍计算）；对业余者模型选择敏感；合理性阈值 $\alpha$ 需要调优。

\subsection{Repetition Penalties}
\subsection{重复惩罚}
\label{repetition-penalties}

Orthogonal to the sampling strategy, repetition penalties discourage the model from repeating tokens. Given the raw logit $z_v$ for token $v$ (i.e., the unnormalized score output by the LM head \emph{before} softmax), the penalized logit is: 
\[
z_v' = \begin{cases}
    z_v / \theta & \text{if } v \in \text{generated tokens and } z_v > 0 \\
    z_v \cdot \theta & \text{if } v \in \text{generated tokens and } z_v < 0
  \end{cases}
\]
 where $\theta > 1$ is the penalty factor (typically 1.1--1.3). In both cases, the effect is to push the logit toward zero---reducing the probability of previously generated tokens. Frequency and presence penalties are simpler additive variants used by OpenAI APIs: 
\[
z_v' = z_v - \alpha \cdot \text{count}(v) - \beta \cdot \mathbf{1}[v \in \text{generated}]
\]
 where $\alpha$ is the frequency penalty (proportional to how many times $v$ appeared) and $\beta$ is the presence penalty (flat penalty for any prior occurrence).

与采样策略正交，重复惩罚阻止模型重复词元。给定词元 $v$ 的原始 logit $z_v$（即语言模型头部在 softmax \emph{之前}输出的未归一化分数），惩罚后的 logit 为：
\[
z_v' = \begin{cases}
    z_v / \theta & \text{if } v \in \text{generated tokens and } z_v > 0 \\
    z_v \cdot \theta & \text{if } v \in \text{generated tokens and } z_v < 0
  \end{cases}
\]
其中 $\theta > 1$ 是惩罚系数（通常为 1.1--1.3）。两种情况下，效果都是将 logit 推向零——降低先前生成词元的概率。频率惩罚和存在惩罚是 OpenAI API 使用的更简单的加法变体：
\[
z_v' = z_v - \alpha \cdot \text{count}(v) - \beta \cdot \mathbf{1}[v \in \text{generated}]
\]
其中 $\alpha$ 是频率惩罚（与 $v$ 出现的次数成正比），$\beta$ 是存在惩罚（对任何先前出现施加固定惩罚）。

\subsection{Practical Comparison}
\subsection{实际比较}
\label{practical-comparison}

\begin{table}[ht!]
\centering
\caption{Decoding method comparison for LLM text generation.}
\caption{LLM文本生成的解码方法比较。}
\begin{tabular}{@{}lp{2.5cm}p{2.8cm}p{2.8cm}p{2.8cm}@{}}
\toprule
\textbf{Method} & \textbf{Deterministic} & \textbf{Diversity} & \textbf{Quality} & \textbf{Best For} \\
\midrule
Greedy & Yes & None & Medium & Code, factual QA \\
Beam Search ($B$=4--8) & Yes & Low & High (narrow) & Translation, summarization \\
Diverse Beam Search & Yes & Medium & High & Candidate generation for reranking \\
Top-$k$ ($k$=50) & No & Medium & Medium & General-purpose generation \\
Top-$p$ ($p$=0.9) & No & Adaptive & High & Default for open-ended tasks \\
Min-$p$ ($p_{\min}$=0.1) & No & Adaptive & High & Robust alternative to top-$p$ \\
Contrastive & Yes & Low & Very High & Factual, coherent long-form \\
\bottomrule
\end{tabular}
\begin{tabular}{@{}lp{2.5cm}p{2.8cm}p{2.8cm}p{2.8cm}@{}}
\toprule
\textbf{方法} & \textbf{确定性} & \textbf{多样性} & \textbf{质量} & \textbf{最佳用途} \\
\midrule
贪心 & 是 & 无 & 中等 & 代码、事实性问答 \\
束搜索（$B$=4--8） & 是 & 低 & 高（狭窄） & 翻译、摘要 \\
多样化束搜索 & 是 & 中等 & 高 & 用于重排的候选生成 \\
Top-$k$（$k$=50） & 否 & 中等 & 中等 & 通用生成 \\
Top-$p$（$p$=0.9） & 否 & 自适应 & 高 & 开放式任务的默认选择 \\
Min-$p$（$p_{\min}$=0.1） & 否 & 自适应 & 高 & top-$p$ 的稳健替代 \\
对比解码 & 是 & 低 & 非常高 & 事实性、连贯的长文本 \\
\bottomrule
\end{tabular}
\end{table}

\begin{examplebox}[Decoding in Practice: ``Once upon a time'']
Given the prompt ``Once upon a time,'':

\begin{examplebox}[解码实践：“Once upon a time”]
给定提示“Once upon a time,”：

\begin{itemize}
  \item \textbf{Greedy}: ``there was a young girl who lived in a small village...'' (generic fairy tale)
  \item \textbf{Top-$p$=0.9, $T$=1.0}: ``the rivers ran backwards and the fish learned to fly...'' (creative, surprising)
  \item \textbf{Top-$p$=0.9, $T$=0.3}: ``there was a kingdom ruled by a wise and just king...'' (coherent, conventional)
  \item \textbf{Contrastive}: ``in the amber-lit corridors of a collapsing star, two minds argued about the nature of time...'' (distinctive, avoids clichés)
\end{itemize}

\begin{itemize}
  \item \textbf{贪心}：“there was a young girl who lived in a small village...” （通用童话）
  \item \textbf{Top-$p$=0.9, $T$=1.0}：“the rivers ran backwards and the fish learned to fly...” （创意、出人意料）
  \item \textbf{Top-$p$=0.9, $T$=0.3}：“there was a kingdom ruled by a wise and just king...” （连贯、传统）
  \item \textbf{对比解码}：“in the amber-lit corridors of a collapsing star, two minds argued about the nature of time...” （独特、避免陈词滥调）
\end{itemize}

Same model, same prompt --- decoding strategy determines the character of the output.
\end{examplebox}

相同模型、相同提示——解码策略决定了输出的特征。
\end{examplebox}

\subsection{Constrained Decoding (Structured Generation)}
\subsection{约束解码（结构化生成）}
\label{sec:constrained-decoding}

All methods above sample from the \emph{full} vocabulary at each step. \textbf{Constrained decoding} restricts the set of allowed tokens so that the output is \emph{guaranteed} to conform to a formal grammar---typically a JSON schema, regex, or context-free grammar (CFG).

上述所有方法都在每一步从*完整*词表中采样。**约束解码**限制允许的词元集合，使得输出*保证*符合某种形式文法——通常是 JSON 模式、正则表达式或上下文无关文法（CFG）。

\paragraph{Core mechanism.}
\paragraph{核心机制}
\label{core-mechanism.}

\label{core-mechanism.}

## Section Title
## 章节标题

At each decoding step $t$, a \textbf{token mask} $M_t \subseteq \mathcal{V}$ is computed from the current parser state. Only tokens in $M_t$ receive their original logits; all others are set to $-\infty$ before softmax: 
\[
P'(v | x_{<t}) = \begin{cases}
    P(v | x_{<t}) / Z & \text{if } v \in M_t \\
    0 & \text{otherwise}
  \end{cases}
\]
 where $Z = \sum_{v \in M_t} P(v | x_{<t})$ renormalizes. Because the mask changes every step (it depends on what has been generated so far), the constraint is enforced \emph{incrementally}---the model cannot produce an invalid prefix at any point.

在每个解码步骤 $t$ 中，从当前解析器状态计算出一个 \textbf{令牌掩码 (token mask)} $M_t \subseteq \mathcal{V}$。只有 $M_t$ 中的令牌保留其原始 logits；其他所有令牌在 softmax 之前被设置为 $-\infty$：
\[
P'(v | x_{<t}) = \begin{cases}
    P(v | x_{<t}) / Z & \text{如果 } v \in M_t \\
    0 & \text{否则}
  \end{cases}
\]
其中 $Z = \sum_{v \in M_t} P(v | x_{<t})$ 进行重新归一化。由于掩码每步都在变化（取决于目前已生成的内容），约束是以 \emph{增量} 方式实现的——模型在任何时刻都不能产生无效前缀。

\paragraph{From schema to mask.}
\label{from-schema-to-mask.}

\paragraph{从模式到掩码。}
\label{from-schema-to-mask.}

The compilation pipeline is: 
\[
\text{JSON Schema} \;\xrightarrow{\text{compile}}\; \text{Regex}
  \;\xrightarrow{\text{compile}}\; \text{FSM (DFA)}
  \;\xrightarrow{\text{index}}\; \text{Token Mask per State}
\]
 The FSM states correspond to positions in the regex. For each state, all vocabulary tokens that would keep the string in the language are precomputed into an index (a one-time cost per schema). At runtime, looking up the mask is an $O(1)$ table access---adding negligible latency to each decoding step.

编译流水线如下：
\[
\text{JSON Schema} \;\xrightarrow{\text{编译}}\; \text{Regex}
  \;\xrightarrow{\text{编译}}\; \text{FSM (DFA)}
  \;\xrightarrow{\text{索引}}\; \text{每个状态的 Token Mask}
\]
FSM 的状态对应正则表达式中的位置。对于每个状态，所有能够使字符串保持在语言中的词汇令牌被预先计算并存入一个索引（每个模式的一次性成本）。在运行时，查找掩码是一个 $O(1)$ 的表访问——为每个解码步骤增加可忽略的延迟。

\paragraph{Key libraries.}
\label{key-libraries.}

\paragraph{关键库。}
\label{key-libraries.}

\begin{itemize}
  \item \textbf{Outlines}~\cite{willard2023outlines}: Compiles JSON schemas and regexes into interleaved FSM-guided generation. Supports any model with a logits interface.
  \item \textbf{Outlines}~\cite{willard2023outlines}：将 JSON 模式和正则表达式编译成交错的 FSM 引导生成。支持任何具有 logits 接口的模型。
  \item \textbf{lm-format-enforcer}\footnote{\url{https://github.com/noamgat/lm-format-enforcer}}: Similar FSM approach with a focus on integration with serving frameworks (vLLM, TGI).
  \item \textbf{lm-format-enforcer}\footnote{\url{https://github.com/noamgat/lm-format-enforcer}}：类似的 FSM 方法，专注于与推理框架（vLLM、TGI）的集成。
  \item \textbf{Guidance}\footnote{\url{https://github.com/guidance-ai/guidance}} (Microsoft): Interleaves constrained generation with control flow (loops, conditions), enabling complex structured outputs beyond flat schemas.
  \item \textbf{Guidance}\footnote{\url{https://github.com/guidance-ai/guidance}}（微软）：将约束生成与控制流（循环、条件）交错结合，支持超越平面模式的复杂结构化输出。
  \item \textbf{XGrammar}~\cite{dong2024xgrammar}: Pushdown-automaton-based engine supporting full context-free grammars (not just regular languages), used in MLC-LLM and vLLM for grammar-mode decoding.
  \item \textbf{XGrammar}~\cite{dong2024xgrammar}：基于下推自动机的引擎，支持完整的上下文无关文法（不仅仅是正则语言），用于 MLC-LLM 和 vLLM 中的文法模式解码。
\end{itemize}

\paragraph{Trade-offs.}
\label{trade-offs.}

\paragraph{权衡。}
\label{trade-offs.}

Constrained decoding \emph{guarantees} syntactic validity---no post-hoc parsing failures, no retries. However:

约束解码 \emph{保证}句法有效性——没有事后解析失败，无需重试。然而：

\begin{itemize}
  \item \textbf{Semantic quality}: Forcing structure can degrade content quality if the model’s probability mass for the ``correct'' answer lies outside the grammar. In practice this is rare for well-trained models on well-designed schemas.
  \item \textbf{语义质量}：如果模型对“正确”答案的概率质量位于文法之外，强制结构可能会降低内容质量。在实践中，对于训练良好的模型和设计良好的模式，这种情况很少见。
  \item \textbf{Compilation cost}: The FSM index must be built per schema. For complex schemas this can take 1--5 s, but it is amortized over all requests using that schema.
  \item \textbf{编译成本}：必须为每个模式构建 FSM 索引。对于复杂模式，这可能需要 1-5 秒，但该成本会分摊到使用该模式的所有请求中。
  \item \textbf{Grammar coverage}: Regex/FSM handles JSON, YAML, SQL fragments, and most structured formats. Full CFGs (via XGrammar or LALR parsers) cover languages like Python or XML.
  \item \textbf{文法覆盖范围}：正则表达式/FSM 处理 JSON、YAML、SQL 片段以及大多数结构化格式。完整的 CFG（通过 XGrammar 或 LALR 解析器）覆盖 Python 或 XML 等语言。
\end{itemize}

\begin{keybox}[When to Use Constrained Decoding]
Use constrained decoding whenever the consumer of the model’s output is a program rather than a human. Tool-calling agents, API backends, and data-extraction pipelines all benefit from \emph{guaranteed} valid structure. For free-form prose or creative text, unconstrained sampling remains appropriate.
\end{keybox}

\begin{keybox}[何时使用约束解码]
每当模型输出的使用者是程序而非人类时，请使用约束解码。工具调用智能体、API 后端和数据提取流水线都能从 \emph{保证}有效的结构中受益。对于自由形式的散文或创意文本，无约束采样仍然适用。
\end{keybox}

\section{Prompt Engineering}
\label{sec:prompt-engineering}

\section{提示工程 (Prompt Engineering)}
\label{sec:prompt-engineering}

Prompt engineering is the discipline of designing inputs to LLMs that reliably elicit desired behaviour---without changing model weights. While fine-tuning modifies the model, prompt engineering exploits the model’s \emph{existing} capabilities through careful framing, examples, and structure. It is the fastest, cheapest, and most accessible lever for improving LLM outputs, and remains essential even when using fine-tuned models.

提示工程是一门设计 LLM 输入以可靠地引发所需行为（无需改变模型权重）的学科。微调修改模型，而提示工程则通过精心设计的框架、示例和结构来利用模型的 \emph{现有}能力。它是改进 LLM 输出最快、最便宜且最易获取的杠杆，即使在使用微调模型时也仍然必不可少。

\subsection{In-Context Learning (ICL)}
\label{in-context-learning-icl}

\subsection{上下文学习 (In-Context Learning, ICL)}
\label{in-context-learning-icl}

In-context learning~\cite{brown2020language} is the remarkable ability of large language models to learn tasks at inference time purely from examples provided in the prompt---with no gradient updates. The model implicitly infers the task from the pattern of input--output pairs and generalizes to new inputs.

上下文学习~\cite{brown2020language} 是大型语言模型在推理时仅通过提示中提供的示例来学习任务的卓越能力——无需梯度更新。模型从输入-输出对的模式中隐式推断任务，并泛化到新输入。

\begin{keybox}[Why In-Context Learning Works]
\begin{itemize}
  \item \textbf{Implicit Bayesian inference}: The model has seen millions of tasks during pretraining. The prompt examples \emph{locate} the relevant task in the model’s learned distribution~\cite{xie2022explanation}.
  \item \textbf{Induction heads}: Specific attention heads learn to copy patterns (``A is to B as C is to ''), enabling in-context generalization~\cite{olsson2022context}.
  \item \textbf{Task vectors}: ICL creates implicit task representations in the residual stream that steer generation toward the demonstrated format and content~\cite{todd2024function}.
\end{itemize}
\end{keybox}

\begin{keybox}[上下文学习为何有效]
\begin{itemize}
  \item \textbf{隐式贝叶斯推理}：模型在预训练期间见过数百万个任务。提示中的示例 \emph{定位}了模型学习到的分布中的相关任务~\cite{xie2022explanation}。
  \item \textbf{归纳头 (Induction heads)}：特定的注意力头学习复制模式（“A 之于 B 如同 C 之于 ”），从而实现上下文泛化~\cite{olsson2022context}。
  \item \textbf{任务向量 (Task vectors)}：ICL 在残差流中创建隐式任务表示，引导生成朝向演示的格式和内容~\cite{todd2024function}。
\end{itemize}
\end{keybox}

\paragraph{Scaling behaviour.}
\label{scaling-behaviour.}

\paragraph{缩放行为。}
\label{scaling-behaviour.}

ICL emerges primarily in models above $\sim$1B parameters and improves log-linearly with model scale~\cite{brown2020language}. Smaller models can memorize examples but struggle to generalize to novel inputs within the same context window.

ICL 主要出现在参数超过 $\sim$10 亿的模型中，并随着模型规模的增大呈对数线性改善~\cite{brown2020language}。较小的模型可以记住示例，但难以在相同上下文窗口内泛化到新输入。

\subsection{Zero-Shot Prompting}
\label{zero-shot-prompting}

\subsection{零样本提示 (Zero-Shot Prompting)}
\label{zero-shot-prompting}

Zero-shot prompting provides \emph{no} examples---only a task description or instruction. The model must rely entirely on its pretrained knowledge and instruction-tuning to produce the correct format and content.

零样本提示不提供 \emph{任何}示例——仅提供任务描述或指令。模型必须完全依赖其预训练知识和指令微调来生成正确的格式和内容。

\begin{examplebox}[Zero-Shot Classification]
\begin{lstlisting}
Classify the following movie review as POSITIVE or NEGATIVE.


Review: "The cinematography was breathtaking but the plot 
felt rushed and predictable."


Sentiment:
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[零样本分类]
\begin{lstlisting}
将以下电影评论分类为 POSITIVE 或 NEGATIVE。


评论："The cinematography was breathtaking but the plot 
felt rushed and predictable."


情感：
\end{lstlisting}
\end{examplebox}

\paragraph{When zero-shot works well:}
\label{when-zero-shot-works-well}

\paragraph{零样本何时表现良好：}
\label{when-zero-shot-works-well}

\begin{itemize}
  \item Tasks the model has seen extensively during pretraining/SFT (translation, summarization, sentiment)
  \item Well-specified instructions with unambiguous output format
  \item Instruction-tuned models (e.g., ChatGPT, Claude, Llama-3-Instruct) significantly outperform base models at zero-shot tasks~\cite{ouyang2022training}
\end{itemize}

\begin{itemize}
  \item 模型在预训练/SFT 期间广泛见过的任务（翻译、摘要、情感分析）
  \item 指定明确、输出格式无歧义的指令
  \item 指令微调模型（例如 ChatGPT、Claude、Llama-3-Instruct）在零样本任务上显著优于基础模型~\cite{ouyang2022training}
\end{itemize}

\paragraph{When zero-shot fails:}
\label{when-zero-shot-fails}

\paragraph{零样本何时失败：}
\label{when-zero-shot-fails}

Novel formats, domain-specific labeling schemes, or ambiguous tasks where the model cannot infer your exact requirements from the instruction alone.

新奇的格式、特定领域的标注方案，或任务模糊时，模型无法仅从指令中推断出你的确切要求。

\subsection{Few-Shot Prompting}
\label{few-shot-prompting}

\subsection{少样本提示 (Few-Shot Prompting)}
\label{few-shot-prompting}

Few-shot prompting~\cite{brown2020language} provides $k$ input--output examples (``shots'') before the actual query. This is the most common form of in-context learning and remains one of the most effective prompting strategies.

少样本提示~\cite{brown2020language} 在实际查询之前提供 $k$ 个输入-输出示例（“样本”）。这是上下文学习最常见的形式，并且仍然是最有效的提示策略之一。

\begin{examplebox}[Few-Shot Named Entity Recognition]
\begin{lstlisting}
Extract named entities from the text. Format: [ENTITY](TYPE)


Text: "Apple released the iPhone 15 in Cupertino."
Entities: [Apple](ORG), [iPhone 15](PRODUCT), [Cupertino](LOC)


Text: "Elon Musk announced Tesla's new factory in Berlin."
Entities: [Elon Musk](PER), [Tesla](ORG), [Berlin](LOC)


Text: "OpenAI partnered with Microsoft to deploy GPT-4."
Entities:
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[少样本命名实体识别]
\begin{lstlisting}
从文本中提取命名实体。格式：[实体](类型)


文本："Apple released the iPhone 15 in Cupertino."
实体：[Apple](ORG), [iPhone 15](PRODUCT), [Cupertino](LOC)


文本："Elon Musk announced Tesla's new factory in Berlin."
实体：[Elon Musk](PER), [Tesla](ORG), [Berlin](LOC)


文本："OpenAI partnered with Microsoft to deploy GPT-4."
实体：
\end{lstlisting}
\end{examplebox}

\paragraph{Key design principles for few-shot examples:}
\label{key-design-principles-for-few-shot-examples}

\paragraph{少样本示例的关键设计原则：}
\label{key-design-principles-for-few-shot-examples}

\begin{enumerate}
  \item \textbf{Diversity}: Cover the range of expected inputs (different lengths, edge cases, categories).
  \item \textbf{Ordering}: Place harder or more representative examples last (recency bias)~\cite{lu2022fantastically}.
  \item \textbf{Label balance}: If classifying, include examples from all classes to avoid majority-class bias.
  \item \textbf{Format consistency}: Every example must follow the \emph{exact} same structure. The model mimics the pattern.
  \item \textbf{Relevance}: Use examples semantically similar to the target query for best results~\cite{liu2022makes}.
\end{enumerate}

\begin{enumerate}
  \item \textbf{多样性}：覆盖预期输入的范围（不同长度、边缘情况、类别）。
  \item \textbf{排序}：将较难或更具代表性的示例放在最后（近因偏差）~\cite{lu2022fantastically}。
  \item \textbf{标签平衡}：如果进行分类，请包含所有类别的示例，以避免多数类偏见。
  \item \textbf{格式一致性}：每个示例必须遵循 \emph{完全}相同的结构。模型会模仿该模式。
  \item \textbf{相关性}：使用与目标查询语义相似的示例以获得最佳结果~\cite{liu2022makes}。
\end{enumerate}

\paragraph{How many shots?}
\label{how-many-shots}

\paragraph{使用多少个样本？}
\label{how-many-shots}

## How LLMs Work: An Intuitive Overview
## 大型语言模型的工作原理：直观概述

Performance typically improves from 0 to 4--8 examples, then plateaus. Beyond $\sim$20 examples, gains are marginal and you risk filling the context window. Min et al.~\cite{min2022rethinking} showed that the \emph{format} and \emph{label space} of examples matter more than label correctness---even random labels help (though correct labels help more).
性能通常从0个示例增加到4--8个示例时提升，之后趋于平稳。超过$\sim$20个示例后，收益微乎其微，且可能填满上下文窗口。Min等人~\cite{min2022rethinking} 表明，示例的\emph{格式}和\emph{标签空间}比标签正确性更重要——即使是随机标签也有帮助（尽管正确标签效果更好）。

\subsection{Instruction-Following Prompts}
\subsection{指令遵循提示（Instruction-Following Prompts）}
\label{instruction-following-prompts}
\label{instruction-following-prompts}

Instruction-tuned models respond best to clear, structured instructions. The key insight: treat the prompt as a \emph{specification}, not a suggestion.
经过指令微调的模型对清晰、结构化的指令响应最佳。关键要点：将提示视为\emph{规范}（specification），而非建议。

\begin{keybox}[Anatomy of an Effective Instruction Prompt]
\begin{keybox}[有效指令提示的构成要素]
\begin{enumerate}
  \item \textbf{Role/Persona}: Define who the model is (``You are a senior data scientist...'')
  \item \textbf{Task}: What to do, stated clearly and unambiguously
  \item \textbf{Context}: Background information the model needs
  \item \textbf{Constraints}: Length limits, tone, what to avoid, output format
  \item \textbf{Examples} (optional): Show the desired output format
  \item \textbf{Input}: The actual data to process
\end{enumerate}
\begin{enumerate}
  \item \textbf{角色/身份（Role/Persona）}：定义模型的身份（“你是一名资深数据科学家……”）
  \item \textbf{任务（Task）}：清晰明确地说明要做什么
  \item \textbf{上下文（Context）}：模型所需的背景信息
  \item \textbf{约束条件（Constraints）}：长度限制、语气、应避免的内容、输出格式
  \item \textbf{示例（Examples）}（可选）：展示期望的输出格式
  \item \textbf{输入（Input）}：待处理的实际数据
\end{enumerate}
\end{keybox}

\begin{examplebox}[Instruction Prompt with Constraints]
\begin{examplebox}[带约束条件的指令提示]
\begin{lstlisting}
Role: You are a medical literature reviewer.
角色：你是一名医学文献审阅者。

Task: Summarize the following research abstract for a 
general audience.
任务：为普通读者总结以下研究摘要。

Constraints:
- Maximum 3 sentences
- No jargon (explain any technical terms)
- Include the key finding and its clinical implication
- Do NOT speculate beyond what the abstract states
约束条件：
- 最多3句话
- 不使用专业术语（如有技术术语需解释）
- 包含关键发现及其临床意义
- 不要超出摘要内容进行推测

Abstract: [...]
摘要：[...]
\end{lstlisting}
\end{examplebox}

\paragraph{System prompts vs.~user prompts.}
\paragraph{系统提示（System prompts） vs. 用户提示（user prompts）}
\label{system-prompts-vs.-user-prompts.}
\label{system-prompts-vs.-user-prompts.}

Modern chat APIs separate the \emph{system} prompt (persistent instructions, role definition) from the \emph{user} message (per-turn input). System prompts are processed with higher attention priority in most models and provide a natural place for role definitions, constraints, and output format specifications~\cite{openai2023gpt4}.
现代聊天API将\emph{系统}提示（system prompt，持久的指令、角色定义）与\emph{用户}消息（user message，每轮输入）分开。在大多数模型中，系统提示以更高的注意力优先级处理，为角色定义、约束条件和输出格式规范提供了自然的位置~\cite{openai2023gpt4}。

\subsection{Structured Output Prompts (JSON/XML)}
\subsection{结构化输出提示（Structured Output Prompts，JSON/XML）}
\label{structured-output-prompts-jsonxml}
\label{structured-output-prompts-jsonxml}

For programmatic use, the most critical prompting technique is enforcing structured output---particularly JSON.
对于程序化使用，最关键提示技术是强制结构化输出——尤其是JSON。

\begin{examplebox}[JSON Output Prompt]
\begin{examplebox}[JSON输出提示]
\begin{lstlisting}
Extract the following information from the customer email.
Respond ONLY with valid JSON, no other text.
从客户邮件中提取以下信息。仅以有效JSON格式回复，不附带其他文本。

Schema:
{
  "intent": "refund|complaint|question|praise",
  "urgency": "low|medium|high",
  "product_mentioned": "string or null",
  "summary": "one sentence summary"
}
模式：
{
  "intent": "refund|complaint|question|praise",
  "urgency": "low|medium|high",
  "product_mentioned": "string or null",
  "summary": "one sentence summary"
}

Email: [...]
邮件：[...]
\end{lstlisting}
\end{examplebox}

\paragraph{Techniques for reliable structured output:}
\paragraph{实现可靠结构化输出的技术：}
\label{techniques-for-reliable-structured-output}
\label{techniques-for-reliable-structured-output}

\begin{itemize}
  \item \textbf{Schema-first}: Show the exact JSON schema \emph{before} the input. The model treats it as a template.
  \item \textbf{Constrained decoding}: Use grammar-based sampling (e.g., Outlines~\cite{willard2023outlines}, Guidance) to guarantee syntactically valid JSON at the token level.
  \item \textbf{XML tags}: For nested or multi-part outputs, XML tags (e.g., \texttt{<thinking>...</thinking>}) provide unambiguous delimiters that models follow reliably.
  \item \textbf{Pydantic/TypeScript types}: Providing type definitions helps models understand field constraints (OpenAI’s function calling uses JSON Schema internally).
\end{itemize}
\begin{itemize}
  \item \textbf{模式优先（Schema-first）}：在输入\emph{之前}展示精确的JSON模式。模型将其视为模板。
  \item \textbf{约束解码（Constrained decoding）}：使用基于语法的采样（例如Outlines~\cite{willard2023outlines}、Guidance）来保证在token级别生成语法有效的JSON。
  \item \textbf{XML标签（XML tags）}：对于嵌套或多部分输出，XML标签（例如\texttt{<thinking>...</thinking>}）提供了模型能可靠遵循的无歧义分隔符。
  \item \textbf{Pydantic/TypeScript类型（Pydantic/TypeScript types）}：提供类型定义有助于模型理解字段约束（OpenAI的函数调用内部使用JSON Schema）。
\end{itemize}

\begin{warningbox}[JSON in Prompts — Common Pitfalls]
\begin{warningbox}[提示中的JSON——常见陷阱]
\begin{itemize}
  \item Models may add markdown fences (\texttt{```json ... ```}) --- instruct explicitly to output raw JSON.
  \item Nested objects and arrays increase hallucination risk --- flatten schemas where possible.
  \item Enum fields (fixed choices) are much more reliable than free-text fields.
  \item Always validate outputs programmatically; no prompt guarantees 100\% compliance without constrained decoding.
\end{itemize}
\begin{itemize}
  \item 模型可能会添加markdown代码块标记（\texttt{```json ... ```}）——明确指示输出原始JSON。
  \item 嵌套对象和数组会增加幻觉风险——尽可能扁平化模式。
  \item 枚举字段（固定选项）比自由文本字段可靠得多。
  \item 始终以编程方式验证输出；没有约束解码时，任何提示都无法保证100%符合要求。
\end{itemize}
\end{warningbox}

\paragraph{JSON Prompting: Structuring the Input.}
\paragraph{JSON提示（JSON Prompting）：结构化输入}
\label{json-prompting-structuring-the-input.}
\label{json-prompting-structuring-the-input.}

A distinct but complementary technique is \emph{JSON prompting}---formatting the prompt \emph{itself} as JSON rather than natural language. This exploits the model’s extensive pre-training on structured data (APIs, configs, code) to improve instruction adherence, reduce ambiguity, and enable deterministic parsing of multi-field requests.
一种不同但互补的技术是\emph{JSON提示（JSON prompting）}——将提示\emph{本身}格式化为JSON而非自然语言。这利用了模型在结构化数据（API、配置文件、代码）上广泛预训练的经验，以提高指令遵循度、减少歧义，并实现对多字段请求的确定性解析。

\begin{examplebox}[JSON Prompting with System Prompt]
\begin{examplebox}[带系统提示的JSON提示]
\begin{lstlisting}
=== SYSTEM ===
You are a senior code reviewer. Analyze code for bugs, 
security issues, and style violations. Always respond 
in the JSON schema provided.
=== 系统 ===
你是一名资深代码审查员。分析代码中的错误、
安全问题和风格违规。始终以提供的JSON模式回复。

=== USER (JSON prompt) ===
{
  "task": "code_review",
  "language": "python",
  "severity_filter": "high",
  "code": "def login(user, pw):\n    query = ...",
  "output_schema": {
    "issues": [{
      "line": "int",
      "severity": "critical|high|medium|low",
      "category": "security|bug|style|performance",
      "description": "string",
      "fix": "string"
    }],
    "overall_risk": "critical|high|medium|low"
  }
}
=== 用户（JSON提示） ===
{
  "task": "code_review",
  "language": "python",
  "severity_filter": "high",
  "code": "def login(user, pw):\n    query = ...",
  "output_schema": {
    "issues": [{
      "line": "int",
      "severity": "critical|high|medium|low",
      "category": "security|bug|style|performance",
      "description": "string",
      "fix": "string"
    }],
    "overall_risk": "critical|high|medium|low"
  }
}
\end{lstlisting}

\textbf{Why JSON prompting works:}
\textbf{为什么JSON提示有效：}

\begin{itemize}
  \item \textbf{Unambiguous field boundaries}: No confusion about where one instruction ends and another begins.
  \item \textbf{Typed constraints}: Fields like \texttt{"severity\_filter": "high"} are clearer than ``only show high severity issues.''
  \item \textbf{Schema-as-contract}: Including \texttt{output\_schema} in the input mirrors API design patterns the model has seen extensively during pre-training.
  \item \textbf{System prompt still essential}: The system message provides \emph{role}, \emph{tone}, and \emph{behavioral constraints} that don’t fit naturally in a JSON payload.
\end{itemize}
\begin{itemize}
  \item \textbf{无歧义的字段边界}：不会混淆一条指令在哪里结束、另一条指令在哪里开始。
  \item \textbf{类型约束}：像\texttt{"severity\_filter": "high"}这样的字段比“仅显示高严重性问题”更清晰。
  \item \textbf{模式即契约（Schema-as-contract）}：在输入中包含\texttt{output\_schema}反映了模型在预训练期间广泛见过的API设计模式。
  \item \textbf{系统提示仍然必不可少}：系统消息提供了\emph{角色}、\emph{语气}和\emph{行为约束}，这些自然不适合放在JSON负载中。
\end{itemize}
\end{examplebox}

\subsection{Chain-of-Thought (CoT) Prompting}
\subsection{思维链提示（Chain-of-Thought, CoT Prompting）}
\label{chain-of-thought-cot-prompting}
\label{chain-of-thought-cot-prompting}

Chain-of-thought prompting~\cite{wei2022chain} asks the model to produce intermediate reasoning steps before giving a final answer. This simple technique dramatically improves performance on tasks requiring multi-step reasoning: arithmetic, logic, commonsense inference, and code generation.
思维链提示（Chain-of-thought prompting）~\cite{wei2022chain} 要求模型在给出最终答案之前产生中间推理步骤。这一简单技术显著提高了需要多步推理的任务（算术、逻辑、常识推理和代码生成）上的性能。

\paragraph{Why CoT works:}
\paragraph{为什么CoT有效：}
\label{why-cot-works}
\label{why-cot-works}

\begin{itemize}
  \item \textbf{Serializes computation}: Transformers have fixed depth but variable-length generation. CoT converts parallel (hard) problems into sequential (easy) steps, effectively increasing the model’s computational budget.
  \item \textbf{Reduces compounding errors}: Each step is a simpler sub-problem with lower per-step error rate.
  \item \textbf{Exposes intermediate state}: Makes reasoning auditable and debuggable.
\end{itemize}
\begin{itemize}
  \item \textbf{序列化计算（Serializes computation）}：Transformer具有固定深度但可变长度的生成能力。CoT将并行（困难）问题转化为顺序（简单）步骤，有效增加了模型的计算预算。
  \item \textbf{减少复合错误（Reduces compounding errors）}：每一步都是更简单的子问题，每步错误率更低。
  \item \textbf{暴露中间状态（Exposes intermediate state）}：使推理过程可审计、可调试。
\end{itemize}

\begin{keybox}[Chain-of-Thought Variants]
\begin{keybox}[思维链变体]
\small
\begin{tabular}{@{}ll@{}}
\toprule
\textbf{Method} & \textbf{Description} \\
\textbf{方法} & \textbf{描述} \\
\midrule
Zero-shot CoT~\cite{kojima2022large} & Append ``Let's think step by step'' to any prompt \\
零样本CoT~\cite{kojima2022large} & 在任何提示后附加“让我们一步步思考” \\
Few-shot CoT~\cite{wei2022chain} & Provide examples with explicit reasoning chains \\
少样本CoT~\cite{wei2022chain} & 提供带有显式推理链的示例 \\
Self-Consistency~\cite{wang2023selfconsistency} & Sample $N$ CoT paths; majority-vote the final answer \\
自一致性~\cite{wang2023selfconsistency} & 采样$N$条CoT路径；对最终答案进行多数投票 \\
Tree of Thoughts~\cite{yao2023tree} & Explore multiple reasoning branches with backtracking \\
思维树~\cite{yao2023tree} & 探索多个推理分支并支持回溯 \\
Plan-and-Solve~\cite{wang2023planandsolve} & First plan the steps; then execute each step \\
计划-求解~\cite{wang2023planandsolve} & 先规划步骤，然后执行每一步 \\
ReAct~\cite{yao2023react} & Interleave Reasoning and Acting (tool use) \\
ReAct~\cite{yao2023react} & 交错推理与行动（工具使用） \\
\bottomrule
\end{tabular}
\end{keybox}

\begin{examplebox}[Zero-Shot Chain-of-Thought]
\begin{examplebox}[零样本思维链示例]
\begin{lstlisting}
Q: A store has 45 apples. They sell 3/5 of them in the 
morning and 1/3 of the remaining in the afternoon. 
How many apples are left?
问：一家商店有45个苹果。上午售出3/5，下午售出剩余部分的1/3。还剩多少个苹果？

Let's think step by step.
让我们一步步思考。

A: Morning sales: 45 * 3/5 = 27 apples sold.
Remaining after morning: 45 - 27 = 18.
Afternoon sales: 18 * 1/3 = 6 apples sold.
Remaining: 18 - 6 = 12 apples.
答：上午售出：45 * 3/5 = 27个苹果。
上午剩余：45 - 27 = 18个。
下午售出：18 * 1/3 = 6个苹果。
剩余：18 - 6 = 12个苹果。
\end{lstlisting}
\end{examplebox}

\paragraph{Self-Consistency.}
\paragraph{自一致性（Self-Consistency）}
\label{self-consistency.}
\label{self-consistency.}

Wang et al.~\cite{wang2023selfconsistency} showed that sampling multiple chain-of-thought reasoning paths and taking a majority vote over final answers significantly outperforms single-path CoT. The intuition: correct reasoning paths tend to converge on the same answer, while errors are typically idiosyncratic. This trades compute (generating $N$ samples) for accuracy---practical when latency is less important than correctness.

Wang等人~\cite{wang2023selfconsistency} 表明，对多个思维链推理路径进行采样并对最终答案进行多数投票，其效果显著优于单路径CoT。直觉上：正确的推理路径往往收敛于同一个答案，而错误通常是独特的。这是用计算资源（生成 $N$ 个样本）来换取准确性——在延迟不如正确性重要时很实用。

\paragraph{When CoT hurts.}
\label{when-cot-hurts.}

\paragraph{CoT何时有害。}
\label{when-cot-hurts.}

CoT is not universally beneficial. For simple tasks (single-step classification, retrieval, formatting), CoT adds unnecessary tokens, increases latency, and can even introduce errors through overthinking. Use CoT selectively for tasks where you expect multi-step reasoning to be required.

CoT并非普遍有益。对于简单任务（单步分类、检索、格式化），CoT会增加不必要的令牌，增加延迟，甚至可能因过度思考而引入错误。请仅在预期需要多步骤推理的任务中有选择地使用CoT。

\subsection{Advanced Prompting Techniques}
\label{advanced-prompting-techniques}

\subsection{高级提示技巧}
\label{advanced-prompting-techniques}

\paragraph{Retrieval-Augmented Generation (RAG).}
\label{retrieval-augmented-generation-rag.}

\paragraph{检索增强生成（RAG）。}
\label{retrieval-augmented-generation-rag.}

Rather than relying solely on the model’s parametric memory, RAG~\cite{lewis2020retrieval} retrieves relevant documents and includes them in the prompt:

与其仅依赖模型的参数化记忆，RAG~\cite{lewis2020retrieval} 会检索相关文档并将其包含在提示中：

\begin{lstlisting}
Context (retrieved): [document chunks]
Question: [user query]
Answer based ONLY on the provided context.
\end{lstlisting}

\begin{lstlisting}
上下文（检索到的）：[文档片段]
问题：[用户查询]
仅基于提供的上下文进行回答。
\end{lstlisting}

This grounds the model’s responses in verifiable sources and dramatically reduces hallucinations for knowledge-intensive tasks.

这使模型的响应基于可验证的源，并显著减少知识密集型任务中的幻觉。

\paragraph{Prompt Chaining and Decomposition.}
\label{prompt-chaining-and-decomposition.}

\paragraph{提示链与分解。}
\label{prompt-chaining-and-decomposition.}

Complex tasks benefit from being broken into a pipeline of simpler prompts, where the output of one becomes the input to the next:

复杂任务可通过分解为一系列更简单的提示来获益，其中前一个提示的输出成为下一个提示的输入：

\begin{enumerate}
  \item \emph{Extract} key facts from document
  \item \emph{Reason} over extracted facts
  \item \emph{Format} final answer
\end{enumerate}

\begin{enumerate}
  \item 从文档中\emph{提取}关键事实
  \item 对提取的事实进行\emph{推理}
  \item \emph{格式化}最终答案
\end{enumerate}

Each step can use a different prompt template, model, or temperature setting. This is more controllable than a single monolithic prompt and enables targeted debugging.

每一步可以使用不同的提示模板、模型或温度设置。这比单个庞大的提示更具可控性，并支持有针对性的调试。

\paragraph{Constitutional AI / Self-Critique.}
\label{constitutional-ai-self-critique.}

\paragraph{宪法AI / 自我批评。}
\label{constitutional-ai-self-critique.}

Bai et al.~\cite{bai2022constitutional} introduce prompts that ask the model to critique and revise its own output against a set of principles:

Bai等人~\cite{bai2022constitutional} 引入了提示，要求模型根据一组原则对自己的输出进行批评和修改：

\begin{lstlisting}
[Generate initial response]
Critique: Does this response violate any of the following 
principles? [list principles]
Revision: Rewrite the response addressing the critique.
\end{lstlisting}

\begin{lstlisting}
[生成初始响应]
批评：此响应是否违反了以下任何原则？[列出原则]
修订：根据批评重写响应。
\end{lstlisting}

\paragraph{Meta-Prompting and Prompt Optimization.}
\label{meta-prompting-and-prompt-optimization.}

\paragraph{元提示与提示优化。}
\label{meta-prompting-and-prompt-optimization.}

Rather than hand-crafting prompts, recent work automates prompt design:

最近的工作不再手工制作提示，而是自动化提示设计：

\begin{itemize}
  \item \textbf{APE}~\cite{zhou2023large}: Uses an LLM to generate and score candidate prompts automatically.
  \item \textbf{DSPy}~\cite{khattab2023dspy}: Compiles declarative task descriptions into optimized prompt pipelines with learned few-shot examples.
  \item \textbf{OPRO}~\cite{yang2024large}: Treats prompt optimization as an optimization problem, using an LLM as the optimizer.
\end{itemize}

\begin{itemize}
  \item \textbf{APE}~\cite{zhou2023large}: 使用LLM自动生成和评分候选提示。
  \item \textbf{DSPy}~\cite{khattab2023dspy}: 将声明式任务描述编译为优化的提示流水线，并带有学到的少样本示例。
  \item \textbf{OPRO}~\cite{yang2024large}: 将提示优化视为一个优化问题，使用LLM作为优化器。
\end{itemize}

\paragraph{Attentive Reasoning Queries (ARQ).}
\label{attentive-reasoning-queries-arq.}

\paragraph{注意力推理查询（ARQ）。}
\label{attentive-reasoning-queries-arq.}

ARQ~\cite{yang2025arq} addresses a fundamental weakness of standard prompting: as context length grows, models increasingly ``lose'' critical information in the middle of the prompt (the \emph{lost-in-the-middle} effect). ARQ mitigates this by decomposing a complex query into multiple focused sub-queries, each designed to direct the model’s attention to a specific part of the context:

ARQ~\cite{yang2025arq} 解决了标准提示的一个根本弱点：随着上下文长度增长，模型会越来越“丢失”提示中间的关键信息（即\emph{中间丢失}效应）。ARQ通过将复杂查询分解为多个聚焦的子查询来缓解这一问题，每个子查询旨在将模型的注意力引导到上下文的特定部分：

\begin{enumerate}
  \item \textbf{Query decomposition}: Break the user question into atomic sub-questions that each target a narrow aspect.
  \item \textbf{Attentive retrieval}: For each sub-query, retrieve or highlight only the relevant context slice---forcing the model to attend to it.
  \item \textbf{Aggregation}: Combine sub-answers into a coherent final response.
\end{enumerate}

\begin{enumerate}
  \item \textbf{查询分解}：将用户问题分解为原子子问题，每个子问题针对一个狭窄方面。
  \item \textbf{注意力检索}：对于每个子查询，仅检索或高亮相关的上下文片段——迫使模型关注它。
  \item \textbf{聚合}：将子答案组合成连贯的最终响应。
\end{enumerate}

This is particularly effective for long-document QA, multi-hop reasoning over large retrieval sets, and agentic tasks where the context window contains many tool outputs. ARQ can be seen as a structured form of chain-of-thought that explicitly manages \emph{where} the model looks, not just \emph{how} it reasons.

这对于长文档问答、大型检索集上的多跳推理以及上下文窗口包含许多工具输出的智能体任务尤为有效。ARQ可以看作是一种结构化的思维链形式，它显式地管理模型\emph{看向何处}，而不仅仅是\emph{如何推理}。

\subsection{Best Practices: Crafting Effective Prompts}
\label{best-practices-crafting-effective-prompts}

\subsection{最佳实践：构建有效提示}
\label{best-practices-crafting-effective-prompts}

Based on empirical findings across the literature and practitioner experience, the following principles reliably improve prompt quality:

基于文献中的实证发现和实践者经验，以下原则能可靠地提高提示质量：

\begin{keybox}[The Prompt Engineering Checklist]
\begin{enumerate}
  \item \textbf{Be specific and unambiguous}: Replace ``summarize this'' with ``summarize in 2--3 bullet points, each under 20 words, focusing on actionable findings.''
  \item \textbf{Show, don’t tell}: One good example is worth 100 words of instruction. When in doubt, add a few-shot example.
  \item \textbf{Define the output format explicitly}: Specify JSON schema, bullet points, table format, or exact delimiters. Never leave format to interpretation.
  \item \textbf{Use delimiters for input data}: Wrap user inputs in clear delimiters (\texttt{"""}, \texttt{<input>...</input>}, \texttt{---}) to separate instructions from data.
  \item \textbf{Assign a role}: ``You are a [domain expert] who [specific behaviour]'' primes relevant knowledge and tone.
  \item \textbf{Specify what NOT to do}: Negative constraints (``do not explain your reasoning'', ``never output more than 5 items'') are often more effective than positive ones.
  \item \textbf{Add chain-of-thought for reasoning tasks}: Append ``Think step by step'' or provide worked examples for math, logic, or multi-hop questions.
  \item \textbf{Control temperature appropriately}: Use $T \approx 0$ for factual/deterministic tasks; $T \approx 0.7$--$1.0$ for creative/diverse outputs.
  \item \textbf{Iterate empirically}: Treat prompts as code---version them, A/B test them, and measure performance on representative eval sets.
  \item \textbf{Leverage recency bias}: Place the most critical instructions and examples at the \emph{end} of the prompt (closest to the generation point).
\end{enumerate}
\end{keybox}

\begin{keybox}[提示工程检查清单]
\begin{enumerate}
  \item \textbf{具体且无歧义}：将“总结这个”替换为“用2-3个要点总结，每点不超过20词，侧重于可操作的结果。”
  \item \textbf{展示，而非告知}：一个好的示例胜过100词的指令。如有疑问，添加少样本示例。
  \item \textbf{明确定义输出格式}：指定JSON模式、要点、表格格式或确切分隔符。切勿让模型自行解读格式。
  \item \textbf{为输入数据使用分隔符}：使用清晰的分隔符（\texttt{"""}, \texttt{<input>...</input>}, \texttt{---}）包裹用户输入，以区分指令和数据。
  \item \textbf{分配角色}：“你是一位[领域专家]，其[具体行为]”能够激发相关知识和语调。
  \item \textbf{指定不要做什么}：否定约束（“不要解释你的推理”，“最多输出5项”）通常比肯定约束更有效。
  \item \textbf{为推理任务添加思维链}：对于数学、逻辑或多跳问题，附加“逐步思考”或提供已完成的示例。
  \item \textbf{适当控制温度}：对于事实性/确定性任务使用 $T \approx 0$；对于创造性/多样性输出使用 $T \approx 0.7$--$1.0$。
  \item \textbf{经验性迭代}：将提示视为代码——进行版本控制、A/B测试，并在代表性评估集上衡量性能。
  \item \textbf{利用近因偏差}：将最关键指令和示例放在提示的\emph{末尾}（最接近生成点）。
\end{enumerate}
\end{keybox}

\begin{table}[ht!]
\centering
\caption{Common prompting failure modes and solutions.}
\begin{tabular}{@{}lp{5cm}p{6.5cm}@{}}
\toprule
\textbf{Failure Mode} & \textbf{Symptom} & \textbf{Solution} \\
\midrule
Instruction amnesia & Model ignores constraints in long prompts & Move constraints to end; repeat key rules; use system prompt \\
Format drift & Output starts correct but degrades over long generations & Use constrained decoding; break into shorter chained prompts \\
Sycophancy & Model agrees with incorrect premises in the prompt & Add ``challenge assumptions if incorrect''; use system-level instruction \\
Hallucinated details & Model invents facts not in provided context & Add ``if unknown, say I don’t know''; use RAG with source attribution \\
Refusal over-triggering & Model refuses benign requests due to safety training & Rephrase to clarify legitimate intent; provide explicit context for why the request is appropriate \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[ht!]
\centering
\caption{常见提示失败模式及解决方案。}
\begin{tabular}{@{}lp{5cm}p{6.5cm}@{}}
\toprule
\textbf{失败模式} & \textbf{症状} & \textbf{解决方案} \\
\midrule
指令遗忘 & 模型忽略长提示中的约束 & 将约束移至末尾；重复关键规则；使用系统提示 \\
格式漂移 & 输出开始时正确，但在长生成过程中退化 & 使用约束解码；拆分为更短的链式提示 \\
谄媚 & 模型同意提示中的错误前提 & 添加“如果错误则质疑假设”；使用系统级指令 \\
虚构细节 & 模型编造不在提供的上下文中的事实 & 添加“如果不知道，请说我不知道”；使用带来源归属的RAG \\
过度触发拒绝 & 模型因安全训练而拒绝良性请求 & 重新措辞以澄清合法意图；提供明确上下文说明请求为何适当 \\
\bottomrule
\end{tabular}
\end{table}

\begin{intuitionbox}[The Prompt Engineering Mindset]
Think of prompt engineering as \emph{programming in natural language}. The model is a powerful but literal interpreter---it will do exactly what you ask, interpreted in the most likely way given its training distribution. Common principles from software engineering apply:

\begin{itemize}
  \item \textbf{DRY (Don’t Repeat Yourself)}: Unless fighting attention decay in long contexts
  \item \textbf{Separation of concerns}: Different prompt sections for role, constraints, examples, and input
  \item \textbf{Test-driven development}: Define expected outputs before writing the prompt
  \item \textbf{Version control}: Track prompt iterations and their eval scores
  \item \textbf{Modularity}: Build reusable prompt templates; parameterize variable parts
\end{itemize}
\end{intuitionbox}

\begin{intuitionbox}[提示工程思维模式]
将提示工程视为\emph{用自然语言编程}。模型是一个强大但字面解释的执行者——它会严格按照你的要求去做，并根据其训练分布以最可能的方式解释你的指令。软件工程中的常见原则同样适用：

\begin{itemize}
  \item \textbf{DRY（不要重复自己）}：除非是为了对抗长上下文中的注意力衰减
  \item \textbf{关注点分离}：为角色、约束、示例和输入设置不同的提示部分
  \item \textbf{测试驱动开发}：在编写提示之前定义预期输出
  \item \textbf{版本控制}：追踪提示迭代及其评估分数
  \item \textbf{模块化}：构建可重用的提示模板；对可变部分进行参数化
\end{itemize}
\end{intuitionbox}

## Model Compression Methods
## 模型压缩方法

Model compression reduces model size and inference cost while preserving quality. Three main approaches: quantization (reduce precision), pruning (remove parameters), and distillation (train a smaller model to mimic a larger one).
模型压缩在保持质量的同时减小模型大小和推理成本。主要方法有三种：量化（降低精度）、剪枝（移除参数）和蒸馏（训练一个较小的模型来模仿较大的模型）。

### Quantization
### 量化

Quantization reduces model size and inference cost by representing weights (and optionally activations) in lower-precision formats. The core trade-off is compression ratio versus quality degradation.
量化通过以较低精度格式表示权重（以及可选的激活值）来减小模型大小和推理成本。核心权衡是压缩比与质量损失之间的关系。

\begin{keybox}[Quantization Overview]
Quantization reduces the numerical precision of model weights (and optionally activations) from FP32/BF16 to lower-bit formats: 
\[
x_q = \text{round}\!\left(\frac{x - z}{s}\right), \quad x_{\text{dequant}} = s \cdot x_q + z
\]
 where $s$ is the scale factor and $z$ is the zero-point.
\end{keybox}
\begin{keybox}[量化概览]
量化将模型权重（以及可选的激活值）的数值精度从 FP32/BF16 降低到更低比特格式：
\[
x_q = \text{round}\!\left(\frac{x - z}{s}\right), \quad x_{\text{dequant}} = s \cdot x_q + z
\]
其中 $s$ 是缩放因子，$z$ 是零点偏移。
\end{keybox}

\begin{table}[ht!]
\centering
\caption{Quantization methods for LLMs.}
\begin{tabular}{@{}llll@{}}
\toprule
\textbf{Method} & \textbf{Bits} & \textbf{Type} & \textbf{Key Idea} \\
\midrule
\textbf{GPTQ}~\cite{frantar2023gptq} & 4-bit & PTQ, weight-only & \parbox[t]{5.5cm}{Layer-wise quantization minimizing $\|WX - \hat{W}X\|^2$ via optimal brain surgeon.} \\[4pt]
\textbf{AWQ}~\cite{lin2024awq} & 4-bit & PTQ, weight-only & \parbox[t]{5.5cm}{Protects salient weights (those with large activations). 1\% of weights carry 99\% importance.} \\[4pt]
\textbf{GGUF}~\cite{gerganov2023gguf} & 2--8 bit & PTQ, weight-only & \parbox[t]{5.5cm}{CPU-optimized format (llama.cpp). Per-block quantization with multiple types.} \\[4pt]
\textbf{FP8} (E4M3) & 8-bit & Training + inference & \parbox[t]{5.5cm}{Native H100 support. 2$\times$ throughput vs BF16.} \\[4pt]
\textbf{SmoothQuant}~\cite{xiao2023smoothquant} & W8A8 & PTQ, weight+act. & \parbox[t]{5.5cm}{Smooths activation outliers into weights before quantization. Enables INT8 GEMM.} \\[4pt]
\textbf{QAT}~\cite{liu2023llmqat} & 4-bit & QAT & \parbox[t]{5.5cm}{Trains with simulated quantization. Highest quality but expensive.} \\[4pt]
\textbf{AQLM}~\cite{egiazarian2024aqlm} & 2-bit & PTQ, additive codes & \parbox[t]{5.5cm}{Extreme compression via learned additive quantization codebooks.} \\
\bottomrule
\end{tabular}
\end{table}
\begin{table}[ht!]
\centering
\caption{大语言模型的量化方法}
\begin{tabular}{@{}llll@{}}
\toprule
\textbf{方法} & \textbf{比特数} & \textbf{类型} & \textbf{核心思想} \\
\midrule
\textbf{GPTQ}~\cite{frantar2023gptq} & 4-bit & PTQ，仅权重 & \parbox[t]{5.5cm}{通过最优脑外科手术逐层量化，最小化 $\|WX - \hat{W}X\|^2$。} \\[4pt]
\textbf{AWQ}~\cite{lin2024awq} & 4-bit & PTQ，仅权重 & \parbox[t]{5.5cm}{保护显著权重（激活值较大的权重）。1\% 的权重承载了 99\% 的重要性。} \\[4pt]
\textbf{GGUF}~\cite{gerganov2023gguf} & 2--8 bit & PTQ，仅权重 & \parbox[t]{5.5cm}{CPU 优化格式 (llama.cpp)。按块量化，支持多种类型。} \\[4pt]
\textbf{FP8} (E4M3) & 8-bit & 训练+推理 & \parbox[t]{5.5cm}{原生 H100 支持。相比于 BF16 吞吐量提升 2 倍。} \\[4pt]
\textbf{SmoothQuant}~\cite{xiao2023smoothquant} & W8A8 & PTQ，权重+激活 & \parbox[t]{5.5cm}{在量化前将激活异常值平滑到权重中。支持 INT8 GEMM。} \\[4pt]
\textbf{QAT}~\cite{liu2023llmqat} & 4-bit & QAT & \parbox[t]{5.5cm}{使用模拟量化进行训练。质量最高但代价昂贵。} \\[4pt]
\textbf{AQLM}~\cite{egiazarian2024aqlm} & 2-bit & PTQ，加法编码 & \parbox[t]{5.5cm}{通过学习式加法量化码本实现极致压缩。} \\
\bottomrule
\end{tabular}
\end{table}

\begin{intuitionbox}[When to Quantize]
\begin{itemize}
  \item \textbf{Inference serving}: Always quantize. W4A16 (4-bit weights, BF16 activations) is the sweet spot --- 2$\times$ memory savings, $<$1\% quality loss for 70B+ models.
  \item \textbf{Training}: FP8 on H100 gives 2$\times$ throughput with minimal quality loss. BF16 is still the default for smaller models.
  \item \textbf{Edge deployment}: GGUF Q4\_K\_M for local inference on consumer hardware.
  \item \textbf{RLHF}: Quantize the frozen models (reference, reward model) to INT8/FP8. Keep the policy in BF16 for training precision.
\end{itemize}
\end{intuitionbox}
\begin{intuitionbox}[何时进行量化]
\begin{itemize}
  \item \textbf{推理服务}：始终进行量化。W4A16（4 比特权重，BF16 激活）是最佳点——节省 2 倍内存，对 70B+ 模型质量损失低于 1%。
  \item \textbf{训练}：在 H100 上使用 FP8 可获得 2 倍吞吐量，质量损失极小。对于较小模型，BF16 仍是默认选择。
  \item \textbf{边缘部署}：在消费级硬件上使用 GGUF Q4\_K\_M 进行本地推理。
  \item \textbf{RLHF}：将冻结模型（参考模型、奖励模型）量化为 INT8/FP8。策略模型保持 BF16 以保证训练精度。
\end{itemize}
\end{intuitionbox}

### Pruning
### 剪枝

\paragraph{Why Prune?}
\paragraph{为何要剪枝？}

Modern LLMs contain billions of parameters, yet empirical studies consistently show that a large fraction of these weights contribute minimally to model outputs. Pruning exploits this over-parameterization: by removing redundant weights, we reduce \textbf{memory footprint} (enabling deployment on smaller GPUs or edge devices), \textbf{inference latency} (fewer multiply-accumulate operations per forward pass), and \textbf{serving cost} (higher throughput per dollar). Unlike quantization, which reduces the precision of all weights uniformly, pruning selectively eliminates weights---enabling multiplicative savings when combined with quantization (e.g., a 50\% sparse, 4-bit model uses $4\times$ less memory than the dense BF16 baseline). The challenge is achieving high sparsity without degrading generation quality, which has driven the development of principled one-shot methods that require no retraining.
现代大语言模型包含数十亿参数，但实证研究一致表明，其中很大一部分权重对模型输出的贡献极小。剪枝利用了这种过参数化：通过移除冗余权重，我们减少了\textbf{内存占用}（使得能够在更小的 GPU 或边缘设备上部署）、\textbf{推理延迟}（每次前向传播的乘加运算更少）以及\textbf{服务成本}（每美元获得更高吞吐量）。与均匀降低所有权重精度的量化不同，剪枝选择性地消除权重——与量化结合时可实现成倍的节省（例如，一个 50% 稀疏度的 4 比特模型比密集的 BF16 基线节省 4 倍内存）。挑战在于实现高稀疏度而不损害生成质量，这推动了无需重新训练的原则性一次性方法的发展。

\begin{keybox}[Pruning Methods]
\begin{itemize}
  \item \textbf{Unstructured pruning}: Zero out individual weights below a threshold. High sparsity (50--90\%) possible. Requires sparse GEMM kernels (2:4 on A100/H100).
  \item \textbf{Structured pruning}: Remove entire attention heads, layers, or FFN neurons. Directly reduces FLOPS without specialized kernels.
  \item \textbf{SparseGPT}~\cite{frantar2023sparsegpt}: One-shot pruning using approximate inverse Hessian. 50\% unstructured sparsity with minimal quality loss on 175B models.
  \item \textbf{Wanda}~\cite{sun2024wanda}: Prune by $|w| \times \|x\|$ (weight magnitude times input activation norm). No calibration data needed. Competitive with SparseGPT.
\end{itemize}
\end{keybox}
\begin{keybox}[剪枝方法]
\begin{itemize}
  \item \textbf{非结构化剪枝}：将低于阈值的单个权重置零。可实现高稀疏度（50--90%）。需要稀疏 GEMM 内核（A100/H100 上的 2:4）。
  \item \textbf{结构化剪枝}：移除整个注意力头、层或 FFN 神经元。直接减少 FLOPS，无需专用内核。
  \item \textbf{SparseGPT}~\cite{frantar2023sparsegpt}：使用近似逆 Hessian 的一步式剪枝。在 175B 模型上实现 50% 非结构化稀疏度，质量损失极小。
  \item \textbf{Wanda}~\cite{sun2024wanda}：通过 $|w| \times \|x\|$（权重幅值乘以输入激活范数）进行剪枝。无需校准数据。与 SparseGPT 竞争力相当。
\end{itemize}
\end{keybox}

\begin{warningbox}[NVIDIA 2:4 Structured Sparsity]
A100/H100 Tensor Cores natively support 2:4 sparsity: out of every 4 elements, at most 2 are non-zero. This gives exactly 2$\times$ speedup on supported operations with hardware acceleration. The constraint: you must achieve \emph{exactly} 50\% sparsity in this specific pattern, which limits flexibility compared to arbitrary sparsity.
\end{warningbox}
\begin{warningbox}[NVIDIA 2:4 结构化稀疏度]
A100/H100 Tensor Cores 原生支持 2:4 稀疏度：每 4 个元素中最多有 2 个非零。这可以在硬件加速下为支持的操作提供恰好 2 倍的加速。约束条件：必须在此特定模式下实现\emph{恰好} 50% 的稀疏度，与任意稀疏度相比限制了灵活性。
\end{warningbox}

### Knowledge Distillation
### 知识蒸馏

Knowledge distillation~\cite{hinton2015distilling} transfers the learned behaviour of a large \emph{teacher} model into a smaller, cheaper \emph{student} model. The core idea is that the teacher’s output distribution over tokens carries far richer signal than ground-truth hard labels alone --- revealing inter-class similarities, calibration, and uncertainty that the student can exploit.
知识蒸馏~\cite{hinton2015distilling}将大型\emph{教师}模型学到的行为迁移到更小、更便宜的\emph{学生}模型中。核心思想是教师模型在 token 上的输出分布比单纯的硬标签蕴含更丰富的信号——揭示了类别间相似性、校准和不确定性，学生可以加以利用。

\paragraph{Temperature-Scaled Softmax.}
\paragraph{温度缩放 Softmax.}

To expose the ``dark knowledge'' in the teacher’s logits we soften the distribution with a temperature $T > 1$: 
\[
p_i^{(T)} = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}
\]
 At high temperature the probability mass spreads across more tokens, making near-miss alternatives visible. During training the same temperature is applied to the student; at inference the student uses $T=1$.
为了揭示教师 logits 中的“暗知识”，我们使用温度 $T > 1$ 来软化分布：
\[
p_i^{(T)} = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}
\]
在高温下，概率质量分散到更多 token 上，使接近正确的备选变得可见。训练时对学生应用相同的温度；推理时学生使用 $T=1$。

\paragraph{General Distillation Loss.}
\paragraph{通用蒸馏损失.}

\[
\mathcal{L}_{\text{distill}} = \alpha \, T^2 \cdot \text{KL}\!\bigl(P_{\text{teacher}}^{(T)} \;\|\; P_{\text{student}}^{(T)}\bigr) \;+\; (1-\alpha) \cdot \mathcal{L}_{\text{CE}}(y, P_{\text{student}}^{(1)})
\]
 The $T^2$ factor compensates for the reduced gradient magnitude of softened distributions. Typical values: $T \in [2, 20]$, $\alpha \in [0.5, 0.9]$ (more weight on KL when teacher quality is high).
\[
\mathcal{L}_{\text{distill}} = \alpha \, T^2 \cdot \text{KL}\!\bigl(P_{\text{teacher}}^{(T)} \;\|\; P_{\text{student}}^{(T)}\bigr) \;+\; (1-\alpha) \cdot \mathcal{L}_{\text{CE}}(y, P_{\text{student}}^{(1)})
\]
$T^2$ 因子用于补偿软化分布梯度幅值的减小。典型值：$T \in [2, 20]$，$\alpha \in [0.5, 0.9]$（当教师质量高时，KL 权重更大）。

\begin{table}[ht!]
\centering
\caption{Knowledge distillation paradigms for LLMs.}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{4cm}@{}}
\toprule
\textbf{Paradigm} & \textbf{Mechanism} & \textbf{Pros} & \textbf{Cons} \\
\midrule
\textbf{Offline / White-box} & Teacher logits pre-computed; student trains on full distributions & Full distribution signal; one-time teacher cost & Stale data; storage heavy \\
\textbf{Online / Co-training} & Teacher generates on-the-fly; student sees fresh logits & Adapts to student weaknesses & $2\times$ compute; complex infra \\
\textbf{Black-box (API)} & Only teacher \emph{text} outputs available (no logits) & Works with proprietary models & Loses dark knowledge; SFT-like \\
\textbf{Self-distillation} & Model distills into a smaller version of itself & No separate teacher needed & Teacher = student family; ceiling \\
\bottomrule
\end{tabular}
\end{table}
\begin{table}[ht!]
\centering
\caption{大语言模型的知识蒸馏范式}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{4cm}@{}}
\toprule
\textbf{范式} & \textbf{机制} & \textbf{优点} & \textbf{缺点} \\
\midrule
\textbf{离线/白盒} & 教师 logits 预计算；学生训练基于完整分布 & 完整分布信号；一次性教师成本 & 数据陈旧；存储量大 \\
\textbf{在线/协同训练} & 教师实时生成；学生看到最新 logits & 适应学生弱点 & 2 倍算力；基础设施复杂 \\
\textbf{黑盒（API）} & 仅教师\emph{文本}输出可用（无 logits） & 适用于专有模型 & 丢失暗知识；类似 SFT \\
\textbf{自蒸馏} & 模型蒸馏到自身的更小版本 & 无需独立教师 & 教师=学生家族；存在上限 \\
\bottomrule
\end{tabular}
\end{table}

\paragraph{Offline (White-Box) Distillation.}
\paragraph{离线（白盒）蒸馏.}

The teacher’s full logit vector (or top-$k$ logits for storage efficiency) is recorded for each training token. The student minimises the KL divergence against these stored distributions. This is the most data-efficient paradigm when teacher access is unrestricted.
每个训练 token 的教师完整 logit 向量（或为了存储效率保留 top-$k$ logits）被记录下来。学生最小化与这些存储分布的 KL 散度。当教师访问不受限时，这是数据效率最高的范式。

\textbf{Motivation:} Decouple teacher inference from student training --- run the teacher once on high-end hardware, then train many students cheaply.
\textbf{动机：} 将教师模型推理解耦与学生训练分离——在高端硬件上运行一次教师模型，然后低成本地训练多个学生模型。

\textbf{Pros:} Deterministic, reproducible; teacher cost is amortised; full distributional signal.\\
\textbf{优点：} 确定性、可复现；教师模型成本被摊销；获得完整的分布信息。

\textbf{Cons:} Requires storing $|V|$-dimensional vectors per token (mitigated by top-$k$ pruning); teacher cannot adapt to student failures.
\textbf{缺点：} 每个词元需要存储 $|V|$ 维向量（可通过 top-$k$ 剪枝缓解）；教师模型无法适应学生模型的失败。

\paragraph{Online (Co-Training) Distillation.}
\paragraph{在线（协同训练）蒸馏（Online (Co-Training) Distillation）。}
\label{online-co-training-distillation.}

Teacher and student are run jointly: the teacher generates logits for the student’s current training batch.
教师模型和学生模型联合运行：教师模型为学生模型当前的训练批次生成 logits。

\textbf{Motivation:} Let the teacher focus on inputs where the student currently struggles (curriculum-like).
\textbf{动机：} 让教师模型聚焦于学生模型当前困难的输入（类似课程学习）。

\textbf{Pros:} Freshness; can use student-generated inputs for on-policy distillation.\\
\textbf{优点：} 数据新鲜；可使用学生模型生成的输入进行在线蒸馏。

\textbf{Cons:} Double the GPU cost; synchronisation complexity; harder to scale.
\textbf{缺点：} GPU成本翻倍；同步复杂；难以扩展。

\paragraph{Black-Box (API) Distillation.}
\paragraph{黑盒（API）蒸馏（Black-Box (API) Distillation）。}
\label{black-box-api-distillation.}

When only text outputs are available (e.g.~distilling from a proprietary API), the student is trained via SFT on the teacher’s generations, optionally augmented with chain-of-thought traces.
当仅能获得文本输出时（例如从专有API进行蒸馏），学生模型通过监督微调（SFT）在教师模型的生成结果上进行训练，可选地辅以思维链（chain-of-thought）轨迹。

\textbf{Motivation:} Practical reality --- most frontier models do not expose logits.
\textbf{动机：} 现实情况——大多数前沿模型不暴露 logits。

\textbf{Pros:} Simple pipeline; works with any model behind an API.\\
\textbf{优点：} 流程简单；可与任何通过API访问的模型配合使用。

\textbf{Cons:} No soft-label signal; prone to hallucination amplification; effectively supervised fine-tuning.
\textbf{缺点：} 无软标签信号；容易放大幻觉；本质上是监督微调。

\paragraph{Self-Distillation.}
\paragraph{自蒸馏（Self-Distillation）。}
\label{self-distillation.}

A model distils from a larger version within the same architecture family (e.g.~Llama-3 70B $\to$ 8B) or from its own checkpoints during training.
一个模型从同一架构家族中的更大版本（例如 Llama-3 70B $\to$ 8B）或训练过程中的自身检查点进行蒸馏。

\textbf{Motivation:} Avoid training a separate teacher; leverage the model’s own capacity at different scales.
\textbf{动机：} 避免训练单独的教师模型；利用模型自身在不同规模下的能力。

\textbf{Pros:} Architecture compatibility; no external dependency.\\
\textbf{优点：} 架构兼容性；无外部依赖。

\textbf{Cons:} Teacher ceiling equals model ceiling; cannot introduce genuinely new knowledge.
\textbf{缺点：} 教师模型上限等于模型自身上限；无法引入真正的新知识。

\begin{intuitionbox}[Dark Knowledge]
Consider a language model predicting the next word after ``The capital of France is''. Hard labels say only ``Paris'' is correct. But the teacher’s soft distribution might assign 5\% to ``Lyon'', 2\% to ``Marseille'', and near-zero to ``banana'' --- telling the student \emph{which errors are reasonable}, which dramatically improves calibration and generalisation.
\end{intuitionbox}
\begin{intuitionbox}[暗知识（Dark Knowledge）]
考虑一个语言模型预测“法国的首都是”后面的下一个词。硬标签只认为“巴黎”是正确的。但教师模型的软分布可能给“里昂”分配5%，给“马赛”分配2%，给“香蕉”分配接近0——这告诉学生模型\emph{哪些错误是合理的}，从而显著提高校准性和泛化能力。
\end{intuitionbox}

\paragraph{Practical Considerations for LLM Distillation.}
\paragraph{LLM蒸馏的实践考虑（Practical Considerations for LLM Distillation）。}
\label{practical-considerations-for-llm-distillation.}

\begin{itemize}
  \item \textbf{Sequence-level vs.~token-level:} Token-level KL is standard; sequence-level distillation (minimising KL over full sequences) better captures long-range coherence but is harder to optimise.
  \item \textbf{序列级 vs. 词元级：} 词元级KL散度是标准做法；序列级蒸馏（最小化完整序列上的KL）能更好地捕捉长程连贯性，但优化难度更大。
  \item \textbf{Layer-wise hints:} Matching intermediate representations (attention maps, hidden states) provides additional learning signal --- especially useful when student architecture differs.
  \item \textbf{逐层提示：} 匹配中间表示（注意力图、隐藏状态）提供额外的学习信号——当学生模型架构不同时尤其有用。
  \item \textbf{Data selection:} Distillation data quality matters; curating diverse, hard examples yields better students than random sampling.
  \item \textbf{数据选择：} 蒸馏数据质量至关重要；精心挑选多样化的困难样本比随机采样能训练出更好的学生模型。
  \item \textbf{Student capacity:} Diminishing returns below $\sim$10\% of teacher parameters; at extreme compression, architecture changes (e.g.~MoE $\to$ dense) may be needed.
  \item \textbf{学生模型容量：} 当学生模型参数低于教师模型的约10%时收益递减；极端压缩时可能需要改变架构（例如从MoE变为密集模型）。
  \item \textbf{Combining with quantization:} Distillation + 4-bit quantization (e.g.~QLoRA-distilled models) achieves near-teacher quality at $20\times$ compression.
  \item \textbf{结合量化：} 蒸馏 + 4-bit量化（例如 QLoRA 蒸馏模型）在 $20\times$ 压缩比下达到接近教师模型的质量。
\end{itemize}

\begin{examplebox}[Compression Method Comparison – 70B Model]
\begin{tabular}{@{}lp{2.5cm}p{2.8cm}p{2.8cm}p{2.8cm}@{}}
\toprule
\textbf{Method} & \textbf{Size} & \textbf{Speed} & \textbf{Quality} & \textbf{Use Case} \\
\textbf{方法} & \textbf{大小} & \textbf{速度} & \textbf{质量} & \textbf{用例} \\
\midrule
BF16 (baseline) & 140 GB & 1$\times$ & 100\% & Training, reference \\
BF16（基线） & 140 GB & 1$\times$ & 100\% & 训练、参考 \\
FP8 (E4M3) & 70 GB & 2$\times$ & 99.5\% & H100 inference \\
FP8（E4M3） & 70 GB & 2$\times$ & 99.5\% & H100 推理 \\
INT8 (SmoothQuant) & 70 GB & 1.8$\times$ & 99\% & A100 inference \\
INT8（SmoothQuant） & 70 GB & 1.8$\times$ & 99\% & A100 推理 \\
4-bit (AWQ) & 35 GB & 2.5$\times$ & 97--98\% & Serving at scale \\
4-bit（AWQ） & 35 GB & 2.5$\times$ & 97--98\% & 大规模服务 \\
2-bit (AQLM) & 17.5 GB & 3$\times$ & 90--93\% & Edge, experimental \\
2-bit（AQLM） & 17.5 GB & 3$\times$ & 90--93\% & 边缘设备、实验性 \\
Pruned 50\% (2:4) & 70 GB & 1.8$\times$ & 97\% & Structured speedup \\
剪枝50\%（2:4） & 70 GB & 1.8$\times$ & 97\% & 结构化加速 \\
Distilled 8B & 16 GB & 10$\times$ & 80--85\% & Mobile, edge \\
蒸馏8B & 16 GB & 10$\times$ & 80--85\% & 移动端、边缘设备 \\
\bottomrule
\end{tabular}
\end{examplebox}
\begin{examplebox}[压缩方法对比——70B模型]
\begin{tabular}{@{}lp{2.5cm}p{2.8cm}p{2.8cm}p{2.8cm}@{}}
\toprule
\textbf{Method} & \textbf{Size} & \textbf{Speed} & \textbf{Quality} & \textbf{Use Case} \\
\textbf{方法} & \textbf{大小} & \textbf{速度} & \textbf{质量} & \textbf{用例} \\
\midrule
BF16 (baseline) & 140 GB & 1$\times$ & 100\% & Training, reference \\
BF16（基线） & 140 GB & 1$\times$ & 100\% & 训练、参考 \\
FP8 (E4M3) & 70 GB & 2$\times$ & 99.5\% & H100 inference \\
FP8（E4M3） & 70 GB & 2$\times$ & 99.5\% & H100 推理 \\
INT8 (SmoothQuant) & 70 GB & 1.8$\times$ & 99\% & A100 inference \\
INT8（SmoothQuant） & 70 GB & 1.8$\times$ & 99\% & A100 推理 \\
4-bit (AWQ) & 35 GB & 2.5$\times$ & 97--98\% & Serving at scale \\
4-bit（AWQ） & 35 GB & 2.5$\times$ & 97--98\% & 大规模服务 \\
2-bit (AQLM) & 17.5 GB & 3$\times$ & 90--93\% & Edge, experimental \\
2-bit（AQLM） & 17.5 GB & 3$\times$ & 90--93\% & 边缘设备、实验性 \\
Pruned 50\% (2:4) & 70 GB & 1.8$\times$ & 97\% & Structured speedup \\
剪枝50\%（2:4） & 70 GB & 1.8$\times$ & 97\% & 结构化加速 \\
Distilled 8B & 16 GB & 10$\times$ & 80--85\% & Mobile, edge \\
蒸馏8B & 16 GB & 10$\times$ & 80--85\% & 移动端、边缘设备 \\
\bottomrule
\end{tabular}
\end{examplebox}

\section{Speculative Decoding Methods}
\section{推测解码方法（Speculative Decoding Methods）}
\label{speculative-decoding-methods}

Speculative decoding~\cite{leviathan2023fast} accelerates autoregressive generation by predicting multiple tokens simultaneously, then verifying them in a single forward pass of the target model. It produces \textbf{identical output distribution} to standard decoding (no quality loss) while achieving 2--3$\times$ speedup.
推测解码~\cite{leviathan2023fast} 通过同时预测多个词元，然后在目标模型的一次前向传播中验证它们，从而加速自回归生成。它产生与标准解码\textbf{完全相同的输出分布}（无质量损失），同时实现2--3$\times$的加速。

\subsection{Core Principle}
\subsection{核心原理（Core Principle）}
\label{core-principle}

\begin{keybox}[Speculative Decoding Framework]
\begin{enumerate}
  \item A fast \textbf{draft mechanism} proposes $k$ candidate tokens: $\hat{x}_1, \ldots, \hat{x}_k$
  \item The large \textbf{target model} runs a single forward pass on all $k$ tokens (batched)
  \item \textbf{Verification}: Accept tokens left-to-right while $P_{\text{target}}(\hat{x}_i) \geq r_i \cdot P_{\text{draft}}(\hat{x}_i)$ (where $r_i \sim U[0,1]$)
  \item On first rejection at position $j$: resample $x_j$ from an adjusted distribution, discard $\hat{x}_{j+1}, \ldots, \hat{x}_k$
\end{enumerate}

\textbf{Key property}: This acceptance/rejection scheme guarantees the final distribution equals $P_{\text{target}}$ exactly.

\textbf{Speedup}: If acceptance rate is $\alpha$, expected tokens per step = $\frac{1 - \alpha^{k+1}}{1 - \alpha}$. At $\alpha=0.8$, $k=5$: expected 3.4 tokens/step vs.~1 for standard decoding.
\end{keybox}
\begin{keybox}[推测解码框架]
\begin{enumerate}
  \item 一个快速的\textbf{草稿机制}提出 $k$ 个候选词元：$\hat{x}_1, \ldots, \hat{x}_k$
  \item 大型\textbf{目标模型}对所有 $k$ 个词元执行一次前向传播（批量处理）
  \item \textbf{验证}：从左到右接受词元，条件为 $P_{\text{target}}(\hat{x}_i) \geq r_i \cdot P_{\text{draft}}(\hat{x}_i)$（其中 $r_i \sim U[0,1]$）
  \item 在位置 $j$ 首次拒绝时：从调整后的分布中重新采样 $x_j$，丢弃 $\hat{x}_{j+1}, \ldots, \hat{x}_k$
\end{enumerate}

\textbf{关键性质}：该接受/拒绝方案保证最终分布精确等于 $P_{\text{target}}$。

\textbf{加速}：如果接受率为 $\alpha$，每步期望词元数 = $\frac{1 - \alpha^{k+1}}{1 - \alpha}$。当 $\alpha=0.8$，$k=5$ 时：每步期望3.4个词元，而标准解码为1个。
\end{keybox}

\subsection{Methods Comparison}
\subsection{方法对比（Methods Comparison）}
\label{methods-comparison}

\begin{table}[ht!]
\centering
\caption{Speculative decoding methods supported by modern inference engines.}
\caption{现代推理引擎支持的推测解码方法。}
\begin{tabular}{@{}lllp{6cm}@{}}
\toprule
\textbf{Method} & \textbf{Draft Source} & \textbf{Speedup} & \textbf{Key Idea} \\
\textbf{方法} & \textbf{草稿来源} & \textbf{加速比} & \textbf{核心思想} \\
\midrule
\textbf{Standard}~\cite{leviathan2023fast} & Small model (1--7B) & 2--3$\times$ & Separate draft model generates candidates. Simple but requires loading 2 models. \\
\textbf{标准方法}~\cite{leviathan2023fast} & 小模型（1--7B） & 2--3$\times$ & 独立的草稿模型生成候选词元。简单但需加载两个模型。 \\
\textbf{Medusa}~\cite{cai2024medusa} & Parallel LM heads & 2--3$\times$ & Add $k$ extra prediction heads to the target model. Each predicts token at position $+1, +2, \ldots, +k$. \\
\textbf{Medusa}~\cite{cai2024medusa} & 并行LM头 & 2--3$\times$ & 向目标模型添加 $k$ 个额外的预测头。每个头预测位置 $+1, +2, \ldots, +k$ 的词元。 \\
\textbf{Eagle}~\cite{li2024eagle} & Feature-level & 2.5--3.5$\times$ & Lightweight decoder generates draft tokens from target model's hidden states. Higher acceptance than Medusa. \\
\textbf{Eagle}~\cite{li2024eagle} & 特征级 & 2.5--3.5$\times$ & 轻量级解码器从目标模型的隐藏状态生成草稿词元。接受率高于Medusa。 \\
\textbf{Eagle-2}~\cite{li2024eagle} & Context-aware & 3--4$\times$ & Dynamic draft tree with confidence-based expansion. State-of-the-art acceptance rates. \\
\textbf{Eagle-2}~\cite{li2024eagle} & 上下文感知 & 3--4$\times$ & 基于置信度扩展的动态草稿树。最先进的接受率。 \\
\textbf{N-gram Lookup} & N-gram cache & 1.5--2$\times$ & Match prompt n-grams against previously generated text. Zero cost; great for repetitive outputs. \\
\textbf{N-gram查找} & N-gram缓存 & 1.5--2$\times$ & 将提示中的n-gram与之前生成的文本匹配。零成本；适用于重复性输出。 \\
\textbf{Lookahead}~\cite{fu2024lookahead} & Jacobi iteration & 2--2.5$\times$ & Parallel Jacobi decoding with n-gram verification. No draft model; uses target model itself. \\
\textbf{Lookahead}~\cite{fu2024lookahead} & Jacobi迭代 & 2--2.5$\times$ & 带n-gram验证的并行Jacobi解码。无草稿模型；使用目标模型自身。 \\
\textbf{Multi-token}~\cite{gloeckle2024multi} & Modified arch. & 2--3$\times$ & Train the model to natively predict multiple tokens per step (Meta's approach in Llama). \\
\textbf{多词元}~\cite{gloeckle2024multi} & 修改架构 & 2--3$\times$ & 训练模型原生预测每步多个词元（Meta在Llama中的方法）。 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Medusa: Multi-Head Speculative Decoding}
\subsection{Medusa：多头推测解码（Medusa: Multi-Head Speculative Decoding）}
\label{medusa-multi-head-speculative-decoding}

\begin{keybox}[How Medusa Works]
Medusa adds $k$ additional ``prediction heads'' to the LLM (sharing the same backbone):

\begin{itemize}
  \item Head 0 (original): predicts token at position $t+1$ (standard next-token)
  \item Head 1: predicts token at position $t+2$ (skipping one)
  \item Head $i$: predicts token at position $t+i+1$
  \item All heads run in parallel during a single forward pass
  \item A \textbf{tree-structured} verification validates multiple candidate sequences simultaneously
\end{itemize}

\textbf{Training}: Fine-tune only the Medusa heads (backbone frozen). Cost: $\sim$1 epoch on representative data.

\textbf{Advantage}: No separate draft model; heads are tiny (one linear layer each). Memory overhead: $<$1\%.
\end{keybox}
\begin{keybox}[Medusa工作原理]
Medusa向LLM添加 $k$ 个额外的“预测头”（共享同一主干）：

\begin{itemize}
  \item 头0（原始）：预测位置 $t+1$ 的词元（标准下一词元预测）
  \item 头1：预测位置 $t+2$ 的词元（跳过一个位置）
  \item 头 $i$：预测位置 $t+i+1$ 的词元
  \item 所有头在单次前向传播中并行运行
  \item 一个\textbf{树结构}验证同时验证多个候选序列
\end{itemize}

\textbf{训练}：仅微调Medusa头（主干冻结）。成本：在代表性数据上约1个epoch。

\textbf{优势}：无需单独的草稿模型；头非常小（每个仅一个线性层）。内存开销：$<$1\%。
\end{keybox}

\subsection{Eagle: Feature-Level Drafting}
\subsection{Eagle：特征级草稿生成（Eagle: Feature-Level Drafting）}
\label{eagle-feature-level-drafting}

## 直觉框：为什么 Eagle 优于 Medusa

## 直觉框：为什么 Eagle 优于 Medusa

Medusa's heads predict independently at each position — they cannot condition on their own previous predictions (token at $t+2$ doesn't know what was predicted at $t+1$). Eagle fixes this with a lightweight autoregressive decoder that operates on the target model's hidden states:
Medusa 的每个位置的头独立预测——它们无法基于自身之前的预测进行条件化（$t+2$ 处的 Token 不知道 $t+1$ 处预测了什么）。Eagle 通过一个轻量级的自回归解码器来修复这一问题，该解码器在目标模型的隐藏状态上运行：

\begin{enumerate}
  \item Extract hidden states from the target model's last layer
  \item 从目标模型的最后一层提取隐藏状态
  \item Feed into a small (1-layer) decoder that autoregressively generates draft tokens conditioned on previous hidden states
  \item 输入到一个小型（1层）解码器，该解码器基于之前的隐藏状态自回归地生成草稿 Token
  \item This captures inter-token dependencies that Medusa misses
  \item 这捕获了 Medusa 遗漏的 Token 间依赖关系
\end{enumerate}

Result: Eagle achieves 85--95\% acceptance rate vs.~Medusa's 60--80\%.
结果：Eagle 实现了 85--95\% 的接受率，而 Medusa 为 60--80\%。

\subsection{N-gram Speculative Decoding}
\subsection{N-gram 推测解码}
\label{n-gram-speculative-decoding}

\begin{keybox}[N-gram Lookup Method]
\begin{关键框}[N-gram 查找方法]
The simplest speculative decoding — requires no additional model or training:
最简单的推测解码 — 无需额外的模型或训练：

\begin{enumerate}
  \item Maintain a cache of n-grams from the prompt and previously generated text
  \item 维护一个来自提示和先前生成文本的 n-gram 缓存
  \item At each step, check if the current context's last $n-1$ tokens match any cached n-gram
  \item 在每一步，检查当前上下文的最后 $n-1$ 个 Token 是否匹配任何缓存的 n-gram
  \item If yes: propose the continuation as draft tokens
  \item 如果匹配：将该延续部分作为草稿 Token 提出
  \item Verify against target model as usual
  \item 像往常一样对目标模型进行验证
\end{enumerate}

\textbf{Best for}: Code generation (repetitive patterns), structured outputs (JSON/XML), and prompts with repeated elements. \textbf{Cost}: Essentially zero.
\textbf{最佳适用场景}：代码生成（重复模式）、结构化输出（JSON/XML）以及包含重复元素的提示。\textbf{成本}：几乎为零。
\end{keybox}
\end{关键框}

\newpage
\subsection{Integration with vLLM}
\subsection{与 vLLM 的集成}
\label{integration-with-vllm}

\begin{lstlisting}[style=pythonstyle]
from vllm import LLM, SamplingParams

# Standard speculative decoding (separate draft model)
# 标准推测解码（单独的草稿模型）
llm = LLM(
    model="meta-llama/Llama-3-70B",
    tensor_parallel_size=4,
    speculative_config={
        "model": "meta-llama/Llama-3-8B",
        "num_speculative_tokens": 5,
    },
)

# N-gram speculation (zero-cost, no draft model needed)
# N-gram 推测（零成本，无需草稿模型）
llm = LLM(
    model="meta-llama/Llama-3-70B",
    speculative_config={
        "method": "ngram",
        "num_speculative_tokens": 5,
        "prompt_lookup_max": 4,  # Match up to 4-grams from prompt
                                 # 从提示中匹配最多 4-gram
    },
)

# EAGLE-style (feature-level draft, high acceptance rate)
# EAGLE 样式（特征级草稿，高接受率）
llm = LLM(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    tensor_parallel_size=4,
    speculative_config={
        "model": "yuhuili/EAGLE-LLaMA3-Instruct-8B",
        "num_speculative_tokens": 2,
        "method": "eagle",
        "draft_tensor_parallel_size": 1,
    },
)

# MLP speculator (IBM-style, lightweight head)
# MLP 推测器（IBM 风格，轻量级头部）
llm = LLM(
    model="meta-llama/Meta-Llama-3.1-70B-Instruct",
    tensor_parallel_size=4,
    speculative_config={
        "model": "ibm-ai-platform/llama3-70b-accelerator",
        "draft_tensor_parallel_size": 1,
    },
)
\end{lstlisting}

\begin{warningbox}[When NOT to Use Speculative Decoding]
\begin{警告框}[何时不应使用推测解码]
\begin{itemize}
  \item \textbf{High batch sizes}: At batch $\geq 64$, generation is already compute-efficient. Speculation adds overhead (draft generation + verification) that doesn't pay off.
  \item \textbf{大批量大小}：当批量大小 $\geq 64$ 时，生成已经计算高效。推测会增加开销（草稿生成 + 验证），得不偿失。
  \item \textbf{Very different distributions}: If draft model is too dissimilar to target, acceptance rate drops below 50\% and speculation is slower than standard decoding.
  \item \textbf{分布差异极大}：如果草稿模型与目标模型差异过大，接受率降至 50\% 以下，推测解码比标准解码更慢。
  \item \textbf{Short outputs}: For $<$20 token outputs, the setup cost of speculation exceeds savings.
  \item \textbf{短输出}：对于少于 20 个 Token 的输出，推测的设置成本超过了节省。
  \item \textbf{Rule of thumb}: Speculation helps most for latency-sensitive, single-stream generation (chatbots, interactive code completion).
  \item \textbf{经验法则}：推测解码对延迟敏感、单流生成（聊天机器人、交互式代码补全）最有效。
\end{itemize}
\end{warningbox}
\end{警告框}

\newpage
\section{Hallucination Detection}
\section{幻觉检测}
\label{sec:hallucination}

LLMs generate fluent text that may be factually incorrect—a phenomenon called \textbf{hallucination}~\cite{ji2023hallucination}. This section covers basic detection methods at the model level (without external retrieval or multi-agent verification).
LLM 会生成流畅但可能事实不准确的文本——这种现象称为 \textbf{幻觉（Hallucination）}~\cite{ji2023hallucination}。本节介绍模型级别的基本检测方法（无需外部检索或多智能体验证）。

\subsection{Types of Hallucination}
\subsection{幻觉的类型}
\label{types-of-hallucination}

\begin{keybox}[Hallucination Taxonomy]
\begin{关键框}[幻觉分类体系]
\begin{itemize}
  \item \textbf{Intrinsic}: Contradicts the provided input/context (e.g., summary says the opposite of the source)
  \item \textbf{内在幻觉（Intrinsic）}：与提供的输入/上下文矛盾（例如，摘要与源文本意思相反）
  \item \textbf{Extrinsic}: Generates claims that cannot be verified from the input and are factually wrong
  \item \textbf{外在幻觉（Extrinsic）}：生成无法从输入中验证且事实错误的断言
  \item \textbf{Faithfulness}: Output diverges from the instruction or specified constraints
  \item \textbf{忠实性（Faithfulness）}：输出偏离了指令或指定的约束条件
\end{itemize}
\end{keybox}
\end{关键框}

\subsection{Detection Methods (Model-Level)}
\subsection{检测方法（模型级别）}
\label{detection-methods-model-level}

\begin{table}[ht!]
\centering
\begin{table}[ht!]
\centering
\caption{Basic hallucination detection methods that operate at the model level.}
\caption{在模型级别运行的基本幻觉检测方法。}
\begin{tabular}{@{}lp{6.5cm}l@{}}
\toprule
\textbf{Method} & \textbf{Mechanism} & \textbf{Signal} \\
\textbf{方法} & \textbf{机制} & \textbf{信号} \\
\midrule
Token-level entropy & High entropy at generation time indicates uncertainty~\cite{kadavath2022language} & $H(P(x_t)) > \tau$ \\
Token 级熵（Token-level entropy） & 生成时的高熵表示不确定性~\cite{kadavath2022language} & $H(P(x_t)) > \tau$ \\
Sequence log-prob & Low average log-probability of the output suggests confabulation & $\frac{1}{T}\sum_t \log P(x_t)$ \\
序列对数概率（Sequence log-prob） & 输出的平均对数概率低表明虚构 & $\frac{1}{T}\sum_t \log P(x_t)$ \\
Consistency sampling & Generate $N$ responses; low agreement $=$ likely hallucination~\cite{manakul2023selfcheckgpt} & Contradiction rate \\
一致性采样（Consistency sampling） & 生成 $N$ 个响应；低一致性 $=$ 可能幻觉~\cite{manakul2023selfcheckgpt} & 矛盾率 \\
Semantic entropy & Cluster meanings (not strings); high semantic entropy $=$ uncertain~\cite{kuhn2023semantic} & Cluster diversity \\
语义熵（Semantic entropy） & 对含义（而非字符串）进行聚类；高语义熵 $=$ 不确定~\cite{kuhn2023semantic} & 聚类多样性 \\
DoLA & Contrast logits between later vs.~earlier layers; amplifies factual knowledge~\cite{chuang2024dola} & Layer divergence \\
DoLA（Decoding by Contrasting Layers） & 对比较晚层与较早层的 logits；放大事实知识~\cite{chuang2024dola} & 层差异 \\
\bottomrule
\end{tabular}
\end{table}

\paragraph{Semantic Entropy.}
\paragraph{语义熵（Semantic Entropy）}
\label{semantic-entropy.}

Kuhn et al.~\cite{kuhn2023semantic} observe that token-level entropy is unreliable (paraphrases have different tokens but same meaning). Instead, they generate multiple responses, cluster them by semantic equivalence (via NLI), and compute entropy over meaning clusters:
Kuhn 等人~\cite{kuhn2023semantic} 观察到 Token 级熵不可靠（释义具有不同的 Token 但含义相同）。因此，他们生成多个响应，通过语义等价（借助 NLI）进行聚类，并计算含义聚类上的熵：
\[
SE = -\sum_{c \in \text{clusters}} P(c) \log P(c)
\]
High SE means the model produces \emph{semantically different} answers—a strong hallucination signal.
高 SE 意味着模型产生了\emph{语义不同的}答案——这是一个强烈的幻觉信号。

\paragraph{SelfCheckGPT.}
\paragraph{SelfCheckGPT}
\label{selfcheckgpt.}

Manakul et al.~\cite{manakul2023selfcheckgpt} detect hallucinations by checking self-consistency: generate multiple responses and verify whether claims in the main response are supported by the alternatives. If the model "disagrees with itself," the claim is likely hallucinated. No external knowledge needed.
Manakul 等人~\cite{manakul2023selfcheckgpt} 通过检查自一致性来检测幻觉：生成多个响应，并验证主要响应中的断言是否得到替代响应的支持。如果模型“与自己不一致”，则该断言很可能是幻觉。不需要外部知识。

\paragraph{DoLA (Decoding by Contrasting Layers).}
\paragraph{DoLA（通过对比层进行解码）}
\label{dola-decoding-by-contrasting-layers.}

Chuang et al.~\cite{chuang2024dola} observe that factual knowledge emerges in later transformer layers while earlier layers retain more generic/uncertain representations. DoLA contrasts the logit distributions between a later ("mature") layer and an earlier ("premature") layer at each decoding step:
Chuang 等人~\cite{chuang2024dola} 观察到，事实知识出现在较晚的 Transformer 层中，而较早的层保留更通用/不确定的表示。DoLA 在每个解码步骤对比较晚（“成熟”）层和较早（“不成熟”）层之间的 logit 分布：
\[
\text{DoLA}(x_t) = \text{softmax}\!\bigl(\log P_{\text{late}}(x_t) - \log P_{\text{early}}(x_t)\bigr)
\]
By amplifying the signal from factual knowledge encoded in deeper layers, DoLA reduces hallucinations at inference time \emph{without any retraining}—requiring only a single additional forward pass through the contrasted layer. It is complementary to sampling-based methods and can be combined with them.
通过放大来自深层编码的事实知识信号，DoLA 在推理时减少幻觉，\emph{无需任何重新训练}——仅需要额外一次通过被对比层的前向传播。它与基于采样的方法互补，并且可以结合使用。

\begin{warningbox}[Limitations of Model-Level Detection]
\begin{警告框}[模型级别检测的局限性]
These methods detect \emph{uncertainty}, not \emph{incorrectness}. A model can be confidently wrong (low entropy, consistent responses—but factually false). For reliable detection, combine with retrieval-based verification (RAG) or external fact-checking tools.
这些方法检测的是\emph{不确定性}，而不是\emph{错误性}。模型可能自信地犯错（低熵、一致的响应——但事实错误）。为了可靠检测，应结合基于检索的验证（RAG）或外部事实核查工具。
\end{warningbox}
\end{警告框}

\section{LLM Safety and Responsible AI}
\section{LLM 安全与负责任的人工智能}
\label{sec:safety}

Safety is not an afterthought—it is an integral part of the LLM training pipeline. This section covers the key dimensions of LLM safety and the mechanisms used to enforce responsible behavior.
安全性不是事后才考虑的问题——它是 LLM 训练流程中不可或缺的一部分。本节涵盖 LLM 安全的关键维度以及用于强制负责任行为的机制。

\subsection{Threat Taxonomy}
\subsection{威胁分类体系}
\label{threat-taxonomy}

\begin{table}[ht!]
\centering
\caption{LLM安全威胁类别。}
\caption{LLM safety threat categories.}
\begin{tabular}{@{}lp{11cm}@{}}
\toprule
\textbf{类别} & \textbf{描述与示例} \\
\textbf{Category} & \textbf{Description and Examples} \\
\midrule
\textbf{有害内容} & 生成有毒、暴力或非法指令（生物武器、CSAM） \\
\textbf{Harmful content} & Generating toxic, violent, or illegal instructions (bioweapons, CSAM) \\
\textbf{偏见与歧视} & 延续刻板印象；跨人群的不公平对待~\cite{gallegos2024bias} \\
\textbf{Bias and discrimination} & Perpetuating stereotypes; unfair treatment across demographics~\cite{gallegos2024bias} \\
\textbf{隐私侵犯} & 从训练数据中泄露个人身份信息；记忆攻击~\cite{carlini2021extracting} \\
\textbf{Privacy violations} & Leaking PII from training data; memorization attacks~\cite{carlini2021extracting} \\
\textbf{越狱} & 绕过安全护栏的对抗性提示~\cite{zou2023universal} \\
\textbf{Jailbreaking} & Adversarial prompts that bypass safety guardrails~\cite{zou2023universal} \\
\textbf{错误信息} & 生成令人信服但虚假的声明（大规模幻觉） \\
\textbf{Misinformation} & Generating convincing but false claims (hallucination at scale) \\
\textbf{双重用途} & 合法的能力（编程、化学）被武器化用于危害 \\
\textbf{Dual-use} & Legitimate capabilities (coding, chemistry) weaponized for harm \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Safety Training Pipeline}
\subsection{安全训练管线}
\label{safety-training-pipeline}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_015_fig15.png}
\caption{安全在每个阶段都被应用：预训练中的数据过滤，SFT中的拒绝示例，RLHF中的安全专用奖励模型，以及迭代红队测试。}
\caption{Safety is applied at every stage: data filtering in pretraining, refusal examples in SFT, safety-specific reward models in RLHF, and iterative red-teaming.}
\end{figure}

\subsection{Key Safety Mechanisms}
\subsection{关键安全机制}
\label{key-safety-mechanisms}

\begin{keybox}[安全技术]
\begin{keybox}[Safety Techniques]
\begin{itemize}
  \item \textbf{数据过滤}：从预训练语料库中移除有毒、有偏见和包含个人身份信息的文本
  \item \textbf{Data filtering}: Remove toxic, biased, and PII-containing text from pretraining corpora
  \item \textbf{安全SFT}：在恰当的拒绝示例上进行训练（“我无法帮助您，因为……”）
  \item \textbf{Safety SFT}: Train on examples of appropriate refusals (``I can’t help with that because\ldots{}'')
  \item \textbf{宪政AI}~\cite{bai2022constitutional}：使用原则进行自我批评；模型根据规则宪法自我修正输出
  \item \textbf{Constitutional AI}~\cite{bai2022constitutional}: Self-critique using principles; model revises its own outputs against a constitution of rules
  \item \textbf{安全奖励模型}：在安全标注的对上训练的独立RM；在RLHF中通过加权求和与有用性RM结合
  \item \textbf{Safety reward model}: Separate RM trained on safety-annotated pairs; combined with helpfulness RM during RLHF via weighted sum
  \item \textbf{护栏}：在服务时阻止有害请求/响应的输入/输出分类器
  \item \textbf{Guardrails}: Input/output classifiers that block harmful requests/responses at serving time
  \item \textbf{红队测试}~\cite{perez2022red}：系统性的对抗性评估，在部署前发现失败模式
  \item \textbf{Red teaming}~\cite{perez2022red}: Systematic adversarial evaluation to find failure modes before deployment
\end{itemize}
\end{keybox}

\subsection{The Helpfulness--Safety Tradeoff}
\subsection{有用性——安全性的权衡}
\label{the-helpfulnesssafety-tradeoff}

\begin{intuitionbox}[平衡有用性与安全性]
\begin{intuitionbox}[Balancing Helpfulness and Safety]
过度优化安全性会产生“过度拒绝”问题：模型拒绝良性请求（例如，拒绝在教育背景下讨论历史暴力）。目标是在安全约束内实现最大有用性的帕累托最优策略：
Over-optimizing for safety creates an \emph{over-refusal} problem: the model declines benign requests (e.g., refusing to discuss historical violence in an educational context). The goal is a Pareto-optimal policy that is maximally helpful \emph{within} safety constraints: 
\[
\max_\theta \; \mathbb{E}[R_\text{helpful}] \quad \text{subject to} \quad \mathbb{E}[R_\text{safety}] \geq \tau
\]
 在实践中，这通过加权奖励实现：$R = \alpha R_\text{helpful} + (1-\alpha) R_\text{safety}$，并仔细调整$\alpha$（通常为0.6–0.8）。Meta的Llama-3报告使用了基于边际加权的独立安全性和有用性奖励模型~\cite{grattafiori2024llama3}。
 In practice, this is implemented as a weighted reward: $R = \alpha R_\text{helpful} + (1-\alpha) R_\text{safety}$ with careful tuning of $\alpha$ (typically 0.6--0.8). Meta’s Llama-3 reports using distinct safety and helpfulness reward models with margin-based weighting~\cite{grattafiori2024llama3}.
\end{intuitionbox}

\subsection{Evaluation}
\subsection{评估}
\label{evaluation}

\begin{itemize}
  \item \textbf{安全基准}：ToxiGen、RealToxicityPrompts、BBQ（偏见）、CrowS-Pairs
  \item \textbf{Safety benchmarks}: ToxiGen, RealToxicityPrompts, BBQ (bias), CrowS-Pairs
  \item \textbf{越狱鲁棒性}：GCG攻击~\cite{zou2023universal}、多轮越狱、编码提示
  \item \textbf{Jailbreak robustness}: GCG attacks~\cite{zou2023universal}, multi-turn jailbreaks, encoded prompts
  \item \textbf{过度拒绝率}：测量良性提示上的假阳性拒绝（目标<5%）
  \item \textbf{Over-refusal rate}: Measure false-positive refusals on benign prompts (target $<$5\%)
  \item \textbf{红队评估}：由领域专家（生物安全、网络安全）进行的人工对抗性测试
  \item \textbf{Red team evaluations}: Human adversarial testing with domain experts (biosecurity, cybersecurity)
\end{itemize}

\begin{warningbox}[安全永无止境]
\begin{warningbox}[Safety Is Never Complete]
没有任何技术组合能提供绝对安全。新的攻击向量持续被发现（多模态越狱、微调攻击可移除安全训练、多轮提示）。安全需要持续监控、对新威胁的快速响应以及纵深防御（多层独立防御）。
No combination of techniques provides absolute safety. New attack vectors are discovered continuously (multi-modal jailbreaks, fine-tuning attacks that remove safety training, many-shot prompting). Safety requires ongoing monitoring, rapid response to new threats, and defense-in-depth (multiple independent layers).
\end{warningbox}