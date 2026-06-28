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

