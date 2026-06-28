\chapter{Retrieval-Augmented Generation (RAG)}
\label{retrieval-augmented-generation-rag}

# \chapter{检索增强生成（RAG）}
# \label{检索增强生成（RAG）}

Retrieval-Augmented Generation (RAG)~\cite{lewis2020retrieval} has emerged as one of the most practically impactful techniques for deploying large language models in production. Rather than relying solely on knowledge encoded in model weights during training, RAG equips LLMs with a dynamic, updatable external memory---enabling accurate, grounded, and verifiable responses across a wide range of knowledge-intensive tasks.

检索增强生成（RAG）~\cite{lewis2020retrieval}已成为在生产环境中部署大语言模型的最具实际影响力的技术之一。RAG 不依赖训练期间编码在模型权重中的知识，而是为大语言模型（LLM）配备一个动态、可更新的外部存储器——使其能够在广泛的知识密集型任务中生成准确、有依据且可验证的响应。

\section{Motivation and Problem Statement}
\label{motivation-and-problem-statement}

## Motivation and Problem Statement
## 动机与问题陈述

\begin{keybox}[Why LLMs Need External Knowledge]
Large language models store knowledge \emph{parametrically}---compressed into billions of weights during training. This creates three fundamental limitations:

\begin{enumerate}
  \item \textbf{Hallucination}: Models confidently generate plausible-sounding but factually incorrect statements when queried beyond their reliable knowledge boundary.
  \item \textbf{Knowledge Staleness}: Training data has a cutoff date; models cannot know about events, papers, or product updates that occurred after training.
  \item \textbf{Domain Specificity}: General-purpose models lack deep knowledge of proprietary codebases, internal documents, specialized regulations, or enterprise data.
\end{enumerate}
\end{keybox}

\begin{keybox}[Why LLMs Need External Knowledge]
大语言模型以 \emph{参数化} 方式存储知识——在训练期间压缩到数十亿个权重中。这带来了三个根本性限制：

\begin{enumerate}
  \item \textbf{幻觉（Hallucination）}：当模型被询问超出其可靠知识边界的问题时，会自信地生成听起来合理但事实错误的语句。
  \item \textbf{知识过时（Knowledge Staleness）}：训练数据有截止日期；模型无法知道训练之后发生的事件、论文或产品更新。
  \item \textbf{领域特异性（Domain Specificity）}：通用模型缺乏对专有代码库、内部文档、特殊法规或企业数据的深入了解。
\end{enumerate}
\end{keybox}

\subsection{Parametric vs.~Non-Parametric Knowledge}
\label{parametric-vs.-non-parametric-knowledge}

### Parametric vs.~Non-Parametric Knowledge
### 参数化知识与非参数化知识

We can formalize the distinction between the two knowledge sources. Let $\mathcal{M}_\theta$ denote a language model with parameters $\theta$, and let $\mathcal{D} = \{d_1, d_2, \ldots, d_N\}$ be an external document corpus. The probability of generating answer $a$ given query $q$ under each paradigm is:

我们可以形式化这两种知识源的区别。令 $\mathcal{M}_\theta$ 表示参数为 $\theta$ 的语言模型，$\mathcal{D} = \{d_1, d_2, \ldots, d_N\}$ 表示外部文档语料库。在每种范式下，给定查询 $q$ 生成答案 $a$ 的概率为：

\begin{align}
  P_{\text{parametric}}(a \mid q) &= P_{\mathcal{M}_\theta}(a \mid q) \\[6pt]
  P_{\text{RAG}}(a \mid q, \mathcal{D}) &= \sum_{d \in \mathcal{D}} P_{\mathcal{M}_\theta}(a \mid q, d)\,
    P_{\text{ret}}(d \mid q, \mathcal{D})
\end{align}

where $P_{\text{ret}}(d \mid q, \mathcal{D})$ is the retrieval distribution over documents. RAG marginalizes over retrieved evidence, grounding generation in non-parametric knowledge.

其中 $P_{\text{ret}}(d \mid q, \mathcal{D})$ 是文档上的检索分布。RAG 对检索到的证据进行边缘化，将生成过程建立在非参数化知识的基础上。

\begin{intuitionbox}[The Library Analogy]
Think of a parametric LLM as a scholar who has memorized an enormous library but graduated years ago. RAG gives that scholar a library card---they can look things up in real time, cite sources, and acknowledge when they need to check a reference rather than guessing from memory.
\end{intuitionbox}

\begin{intuitionbox}[图书馆类比]
将参数化大语言模型想象成一位背下了整个图书馆但已毕业多年的学者。RAG 给这位学者发了一张借书证——他们可以实时查阅资料、引用来源，并在需要核对参考文献时坦白承认，而不是凭记忆猜测。
\end{intuitionbox}

\subsection{When to Use RAG vs.~Fine-Tuning vs.~Long Context}
\label{when-to-use-rag-vs.-fine-tuning-vs.-long-context}

### When to Use RAG vs.~Fine-Tuning vs.~Long Context
### 何时使用 RAG 对比微调对比长上下文

\begin{table}[ht!]
\centering
\caption{Decision guide: RAG vs.~Fine-Tuning vs.~Long Context}
\begin{tabular}{@{}lp{3cm}p{3.2cm}p{3.2cm}p{3.5cm}@{}}
\toprule
\textbf{Criterion} & \textbf{RAG} & \textbf{Fine-Tuning} & \textbf{Long Context} & \textbf{RAG + FT} \\
\midrule
Knowledge updates frequently & \checkmark{} & $\times$ & $\times$ & \checkmark{} \\
Need citations / grounding & \checkmark{} & $\times$ & \checkmark{} & \checkmark{} \\
Proprietary large corpus & \checkmark{} & $\times$ & $\times$ & \checkmark{} \\
Adapt style / format & $\times$ & \checkmark{} & $\times$ & \checkmark{} \\
Teach new reasoning skills & $\times$ & \checkmark{} & $\times$ & \checkmark{} \\
Corpus fits in context window & $\times$ & $\times$ & \checkmark{} & $\times$ \\
Low latency required & $\times$ & \checkmark{} & $\times$ & $\times$ \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[ht!]
\centering
\caption{决策指南：RAG 对比微调对比长上下文}
\begin{tabular}{@{}lp{3cm}p{3.2cm}p{3.2cm}p{3.5cm}@{}}
\toprule
\textbf{标准} & \textbf{RAG} & \textbf{微调} & \textbf{长上下文} & \textbf{RAG + 微调} \\
\midrule
知识频繁更新 & \checkmark{} & $\times$ & $\times$ & \checkmark{} \\
需要引用/有据可依 & \checkmark{} & $\times$ & \checkmark{} & \checkmark{} \\
专有大规模语料库 & \checkmark{} & $\times$ & $\times$ & \checkmark{} \\
调整风格/格式 & $\times$ & \checkmark{} & $\times$ & \checkmark{} \\
教授新推理技能 & $\times$ & \checkmark{} & $\times$ & \checkmark{} \\
语料适合上下文窗口 & $\times$ & $\times$ & \checkmark{} & $\times$ \\
要求低延迟 & $\times$ & \checkmark{} & $\times$ & $\times$ \\
\bottomrule
\end{tabular}
\end{table}

\begin{warningbox}[Common Misconception]
RAG is \emph{not} a replacement for fine-tuning. Fine-tuning teaches the model \emph{how} to reason and respond; RAG provides \emph{what} to reason about. They are complementary. A model fine-tuned to follow instructions well will use retrieved context more effectively than a base model.
\end{warningbox}

\begin{warningbox}[常见误解]
RAG 并\emph{不是}微调的替代品。微调教会模型\emph{如何}推理和回复；RAG 提供\emph{推理的内容}。它们相辅相成。一个经过微调、能很好地遵循指令的模型，会比基础模型更有效地利用检索到的上下文。
\end{warningbox}

\section{Core RAG Architecture}
\label{core-rag-architecture}

## Core RAG Architecture
## 核心 RAG 架构

A standard RAG system consists of two phases: an \textbf{offline indexing pipeline} that processes and stores documents, and an \textbf{online retrieval-generation pipeline} that serves queries.

一个标准的 RAG 系统包含两个阶段：一个处理并存储文档的 \textbf{离线索引管道}（offline indexing pipeline），以及一个服务于查询的 \textbf{在线检索-生成管道}（online retrieval-generation pipeline）。

\subsection{Full Pipeline Diagram}
\label{full-pipeline-diagram}

### Full Pipeline Diagram
### 完整管道图

\begin{figure}[ht!]
\centering
\includegraphics[width=\textwidth]{figures/fig_050_rag_arch.png}
\caption{End-to-end RAG architecture. The offline pipeline (blue) indexes documents once; the online pipeline (green/orange) serves each query at inference time.}
\label{fig:rag_arch}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=\textwidth]{figures/fig_050_rag_arch.png}
\caption{端到端 RAG 架构。离线管道（蓝色）一次性索引文档；在线管道（绿色/橙色）在推理时为每个查询提供服务。}
\label{fig:rag_arch}
\end{figure}

\subsection{Indexing Pipeline}
\label{indexing-pipeline}

### Indexing Pipeline
### 索引管道

\paragraph{Document Loading.}
\label{document-loading.}

#### Document Loading.
#### 文档加载

Documents arrive in heterogeneous formats (PDF, HTML, Markdown, DOCX, code). Loaders extract clean text and preserve metadata (source URL, page number, section title, timestamp) that will be stored alongside embeddings for filtering and citation.

文档以异构格式（PDF、HTML、Markdown、DOCX、代码）到达。加载器提取纯净文本并保留元数据（来源 URL、页码、章节标题、时间戳），这些元数据将与嵌入向量一起存储，用于过滤和引用。

\paragraph{Chunking.}
\label{chunking.}

#### Chunking.
#### 分块

Long documents must be split into chunks that fit within the embedding model’s context window (typically 512 tokens) and are semantically coherent. Chunking strategy is one of the highest-impact decisions in RAG system design (see Section~\ref{sec:chunking}).

长文档必须拆分为符合嵌入模型上下文窗口（通常为 512 个 token）且语义连贯的块。分块策略是 RAG 系统设计中影响最大的决策之一（见第~\ref{sec:chunking}节）。

\paragraph{Embedding.}
\label{embedding.}

#### Embedding.
#### 嵌入

Each chunk $c_i$ is encoded into a dense vector $\mathbf{e}_i = f_\phi(c_i) \in \mathbb{R}^d$ using an embedding model $f_\phi$. These vectors are stored in a vector database alongside the original text and metadata.

每个块 $c_i$ 使用嵌入模型 $f_\phi$ 编码为一个稠密向量 $\mathbf{e}_i = f_\phi(c_i) \in \mathbb{R}^d$。这些向量与原始文本和元数据一起存储在向量数据库中。

\subsection{Retrieval}
\label{retrieval}

### Retrieval
### 检索

Given a query $q$, the retrieval step encodes it as $\mathbf{q} = f_\phi(q)$ and finds the $k$ most similar chunks by cosine similarity:

给定查询 $q$，检索步骤将其编码为 $\mathbf{q} = f_\phi(q)$，并通过余弦相似度找到最相似的 $k$ 个块：

\begin{equation}
  \text{sim}(\mathbf{q}, \mathbf{e}_i) = \frac{\mathbf{q} \cdot \mathbf{e}_i}{\|\mathbf{q}\|\,\|\mathbf{e}_i\|}
\end{equation}

The top-$k$ chunks $\mathcal{C}_k = \{c_{(1)}, \ldots, c_{(k)}\}$ are returned as context.

排名前 $k$ 的块 $\mathcal{C}_k = \{c_{(1)}, \ldots, c_{(k)}\}$ 作为上下文返回。

\subsection{Generation}
\label{generation}

### Generation
### 生成

Retrieved chunks are injected into a prompt template:

检索到的块被注入到一个提示模板中：

\begin{lstlisting}[style=pythonstyle, caption={Standard RAG prompt template}]
SYSTEM_PROMPT = """You are a helpful assistant. Answer the question using ONLY
the provided context. If the context does not contain enough information,
say so explicitly. Cite your sources using [Doc N] notation."""


def build_rag_prompt(query: str, chunks: list[dict]) -> str:
    context_str = "\n\n".join(
        f"[Doc {i+1}] (Source: {c['source']}, Page: {c.get('page','N/A')})\n{c['text']}"
        for i, c in enumerate(chunks)
    )
    return f"""{SYSTEM_PROMPT}


Context:
{context_str}


Question: {query}


Answer:"""
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={标准 RAG 提示模板}]
SYSTEM_PROMPT = """你是一个有益的助手。请仅使用提供的上下文来回答问题。
如果上下文没有包含足够的信息，请明确说明。使用 [Doc N] 标记引用来源。"""


def build_rag_prompt(query: str, chunks: list[dict]) -> str:
    context_str = "\n\n".join(
        f"[Doc {i+1}] (来源: {c['source']}, 页码: {c.get('page','N/A')})\n{c['text']}"
        for i, c in enumerate(chunks)
    )
    return f"""{SYSTEM_PROMPT}


上下文:
{context_str}


问题: {query}


答案:"""
\end{lstlisting}

\section{Retrieval Methods}
\label{retrieval-methods}

## Retrieval Methods
## 检索方法

\subsection{Sparse Retrieval: BM25 and TF-IDF}
\label{sparse-retrieval-bm25-and-tf-idf}

### Sparse Retrieval: BM25 and TF-IDF
### 稀疏检索：BM25 和 TF-IDF

Sparse retrieval methods represent documents and queries as high-dimensional sparse vectors over the vocabulary. The classic BM25 scoring function~\cite{robertson2009probabilistic} for document $d$ given query $q$ with terms $t_1, \ldots, t_n$ is:

稀疏检索方法将文档和查询表示为词汇表上的高维稀疏向量。经典的 BM25 评分函数~\cite{robertson2009probabilistic} 对于包含词项 $t_1, \ldots, t_n$ 的查询 $q$ 下的文档 $d$ 为：

\begin{equation}
  \text{BM25}(d, q) = \sum_{i=1}^{n} \text{IDF}(t_i) \cdot
    \frac{f(t_i, d) \cdot (k_1 + 1)}{f(t_i, d) + k_1 \cdot \left(1 - b + b \cdot \frac{|d|}{\text{avgdl}}\right)}
\end{equation}

where $f(t_i, d)$ is term frequency, $|d|$ is document length, $\text{avgdl}$ is average document length, and $k_1 \in [1.2, 2.0]$, $b = 0.75$ are tuning parameters.

其中 $f(t_i, d)$ 是词频，$|d|$ 是文档长度，$\text{avgdl}$ 是平均文档长度，$k_1 \in [1.2, 2.0]$、$b = 0.75$ 是调优参数。

\begin{keybox}[When Sparse Retrieval Still Wins]
\begin{itemize}
  \item \textbf{Exact keyword matching}: product codes, error codes, proper nouns, rare terms
  \item \textbf{Low-resource domains}: insufficient training data for dense models
  \item \textbf{Interpretability}: easy to debug why a document was retrieved
  \item \textbf{Speed}: no GPU required; scales to billions of documents with inverted indices
  \item \textbf{Out-of-vocabulary terms}: new terminology not seen during embedding training
\end{itemize}
\end{keybox}

\begin{keybox}[稀疏检索仍然胜出的场景]
\begin{itemize}
  \item \textbf{精确关键词匹配}：产品代码、错误代码、专有名词、罕见术语
  \item \textbf{低资源领域}：稠密模型缺乏足够训练数据
  \item \textbf{可解释性}：易于调试为何检索到某篇文档
  \item \textbf{速度}：无需 GPU；使用倒排索引可扩展到数十亿文档
  \item \textbf{词汇表外词项}：嵌入训练中未出现的新术语
\end{itemize}
\end{keybox}

\subsection{Dense Retrieval: DPR}
\label{dense-retrieval-dpr}

### Dense Retrieval: DPR
### 稠密检索：DPR

## Dense Passage Retrieval (DPR) and Hybrid Retrieval
## 稠密段落检索（DPR）与混合检索

Dense Passage Retrieval (DPR)~\cite{karpukhin2020dense} uses two separate BERT-based encoders---a \emph{query encoder} $E_Q$ and a \emph{passage encoder} $E_P$---trained with contrastive loss to place relevant query-passage pairs close together in embedding space.
稠密段落检索（Dense Passage Retrieval, DPR）~\cite{karpukhin2020dense} 使用两个独立的基于 BERT 的编码器——一个 \emph{查询编码器（query encoder）} $E_Q$ 和一个 \emph{段落编码器（passage encoder）} $E_P$——通过对比损失（contrastive loss）进行训练，将相关的查询-段落对在嵌入空间中拉近。

\paragraph{Bi-Encoder Architecture.}
\paragraph{双编码器架构（Bi-Encoder Architecture）}
\label{bi-encoder-architecture.}

\begin{equation}
  \text{sim}(q, p) = E_Q(q)^\top E_P(p)
\end{equation}

\paragraph{Training with In-Batch Negatives.}
\paragraph{使用批内负样本（In-Batch Negatives）训练}
\label{training-with-in-batch-negatives.}

Given a batch of $B$ query-passage pairs $\{(q_i, p_i^+)\}_{i=1}^B$, the contrastive loss treats all other passages in the batch as negatives:
给定一个包含 $B$ 个查询-段落对的批次 $\{(q_i, p_i^+)\}_{i=1}^B$，对比损失将批次中的所有其他段落视为负样本：

\begin{equation}
  \mathcal{L}_{\text{DPR}} = -\frac{1}{B} \sum_{i=1}^{B}
    \log \frac{\exp\!\left(E_Q(q_i)^\top E_P(p_i^+) / \tau\right)}
              {\sum_{j=1}^{B} \exp\!\left(E_Q(q_i)^\top E_P(p_j) / \tau\right)}
\end{equation}

where $\tau$ is a temperature hyperparameter. Hard negatives (passages that are lexically similar but semantically irrelevant) are crucial for training strong retrievers.
其中 $\tau$ 是温度超参数。硬负样本（hard negatives，即词汇相似但语义无关的段落）对于训练强大的检索器至关重要。

\paragraph{Approximate Nearest Neighbor Search.}
\paragraph{近似最近邻搜索（Approximate Nearest Neighbor Search）}
\label{approximate-nearest-neighbor-search.}

At scale, exhaustive search over millions of embeddings is infeasible. FAISS~\cite{johnson2019billion} (Facebook AI Similarity Search) provides efficient approximate nearest neighbor (ANN) search using:
在大规模场景下，对数百万个嵌入进行穷举搜索是不可行的。FAISS~\cite{johnson2019billion}（Facebook AI 相似度搜索库）提供了高效的近似最近邻（Approximate Nearest Neighbor, ANN）搜索，使用以下方法：

\begin{itemize}
  \item \textbf{IVF (Inverted File Index)}: cluster vectors into Voronoi cells; search only nearby cells
  \item \textbf{HNSW (Hierarchical Navigable Small World)}~\cite{malkov2018efficient}: graph-based index with $O(\log N)$ search
  \item \textbf{PQ (Product Quantization)}: compress vectors to reduce memory footprint
\end{itemize}

\begin{itemize}
  \item \textbf{IVF（倒排文件索引）}：将向量聚类到 Voronoi 单元中；仅搜索邻近单元
  \item \textbf{HNSW（分层可导航小世界图）}~\cite{malkov2018efficient}：基于图的索引，搜索复杂度为 $O(\log N)$
  \item \textbf{PQ（乘积量化）}：压缩向量以减小内存占用
\end{itemize}

\subsection{Hybrid Retrieval with Reciprocal Rank Fusion}
\subsection{基于倒数排序融合（Reciprocal Rank Fusion）的混合检索}
\label{hybrid-retrieval-with-reciprocal-rank-fusion}

Hybrid retrieval combines sparse and dense scores. A simple linear combination is: 
混合检索结合了稀疏得分与稠密得分。一种简单的线性组合形式为：
\begin{equation}
  s_{\text{hybrid}}(d, q) = \alpha \cdot s_{\text{dense}}(d, q) + (1-\alpha) \cdot s_{\text{sparse}}(d, q)
\end{equation}

However, scores from different systems are not directly comparable. \textbf{Reciprocal Rank Fusion (RRF)}~\cite{cormack2009reciprocal} avoids this by operating on ranks rather than scores:
然而，来自不同系统的分数无法直接比较。\textbf{倒数排序融合（Reciprocal Rank Fusion, RRF）}~\cite{cormack2009reciprocal} 通过基于排名而非分数来避免这一问题：

\begin{equation}
  \text{RRF}(d) = \sum_{r \in \mathcal{R}} \frac{1}{k + \text{rank}_r(d)}
\label{eq:rrf}
\end{equation}

where $\mathcal{R}$ is the set of ranked lists (e.g., BM25 ranking and dense ranking), $\text{rank}_r(d)$ is the rank of document $d$ in list $r$, and $k = 60$ is a smoothing constant that reduces the impact of very high-ranked documents.
其中 $\mathcal{R}$ 是排名列表的集合（例如 BM25 排名和稠密排名），$\text{rank}_r(d)$ 是文档 $d$ 在列表 $r$ 中的排名，$k = 60$ 是一个平滑常数，用于降低高排名文档的影响。

\begin{examplebox}[RRF Calculation]
\begin{examplebox}[RRF 计算示例]
Suppose BM25 ranks document $d$ at position 3, and dense retrieval ranks it at position 7. With $k = 60$: 
假设 BM25 将文档 $d$ 排在第 3 位，稠密检索将其排在第 7 位。取 $k = 60$：
\[
\text{RRF}(d) = \frac{1}{60 + 3} + \frac{1}{60 + 7} = \frac{1}{63} + \frac{1}{67} \approx 0.0159 + 0.0149 = 0.0308
\]
 A document ranked 1st in both lists would score $\frac{1}{61} + \frac{1}{61} \approx 0.0328$.
一个在两个列表中均排名第一的文档得分为 $\frac{1}{61} + \frac{1}{61} \approx 0.0328$。
\end{examplebox}

\subsection{Learned Sparse Retrieval: SPLADE and SPLADEv2}
\subsection{学习型稀疏检索：SPLADE 与 SPLADEv2}
\label{learned-sparse-retrieval-splade-and-spladev2}

\begin{intuitionbox}[Why SPLADE?]
\begin{intuitionbox}[为什么选择 SPLADE？]
Traditional sparse retrieval (BM25) relies on exact lexical matching --- it fails when the query says ``car'' but the document says ``automobile.'' Dense retrieval (DPR) captures semantics but loses interpretability, requires GPU at query time, and produces large indexes. \textbf{SPLADE} gets the best of both worlds: sparse vectors (fast inverted-index lookup like BM25) with learned semantic expansion (handles synonyms and related concepts like dense models).
传统稀疏检索（BM25）依赖于精确的词法匹配——当查询为“car”而文档为“automobile”时就会失败。稠密检索（DPR）能够捕获语义，但失去了可解释性，查询时需使用 GPU，且生成的索引较大。\textbf{SPLADE} 综合了两者的优点：稀疏向量（像 BM25 那样快速倒排索引查找）加上学习的语义扩展（像稠密模型那样处理同义词和相关概念）。
\end{intuitionbox}

\paragraph{SPLADE (v1) --- Core Idea.}
\paragraph{SPLADE（v1）——核心思想}
\label{splade-v1-core-idea.}

SPLADE (Sparse Lexical and Expansion Model)~\cite{formal2021splade} uses a pre-trained masked language model (e.g., BERT/DistilBERT) to produce a sparse vector over the \emph{entire vocabulary} for each document or query. The key insight: the MLM head already knows which words are semantically related to each position in a text --- SPLADE repurposes this knowledge as term importance weights.
SPLADE（稀疏词汇与扩展模型，Sparse Lexical and Expansion Model）~\cite{formal2021splade} 使用预训练的掩码语言模型（如 BERT/DistilBERT），为每个文档或查询产生一个覆盖\emph{整个词汇表}的稀疏向量。其关键洞察是：MLM 头已经知道文本中每个位置在语义上与哪些词相关——SPLADE 将这一知识重新用作词项重要性权重。

\paragraph{Architecture.}
\paragraph{架构}
\label{architecture.}

Given input text $x = [x_1, \ldots, x_n]$:
给定输入文本 $x = [x_1, \ldots, x_n]$：

\begin{enumerate}
  \item Pass through a transformer encoder to get contextual representations $\mathbf{H} \in \mathbb{R}^{n \times |\mathcal{V}|}$ via the MLM head
  \item Aggregate across positions and apply a saturating activation:
\end{enumerate}

\begin{enumerate}
  \item 通过 Transformer 编码器，经 MLM 头得到上下文表示 $\mathbf{H} \in \mathbb{R}^{n \times |\mathcal{V}|}$
  \item 跨位置聚合，并应用饱和激活函数：
\end{enumerate}

\begin{equation}
  w_t(x) = \log\!\left(1 + \text{ReLU}\!\left(\max_{i \in [1,n]} \mathbf{H}_i[t]\right)\right)
\end{equation}

where $\mathbf{H}_i[t]$ is the MLM logit for vocabulary token $t$ at input position $i$.
其中 $\mathbf{H}_i[t]$ 是输入位置 $i$ 处词汇 token $t$ 的 MLM logit。

\begin{itemize}
  \item The $\log(1 + \cdot)$ saturation prevents any single term from dominating (similar to TF saturation in BM25)
  \item The ReLU ensures sparsity --- most vocabulary terms get weight zero
  \item The $\max$ pooling across positions captures the strongest signal for each term from any position in the text
  \item \textbf{Expansion}: Even tokens \emph{not present} in the original text can get non-zero weight (e.g., a document about ``neural networks'' may get weight for ``deep learning,'' ``AI,'' ``backpropagation'')
\end{itemize}

\begin{itemize}
  \item $\log(1 + \cdot)$ 饱和函数防止任何单个词项主导（类似于 BM25 中的词频饱和）
  \item ReLU 确保稀疏性——大多数词汇词项权重为零
  \item 跨位置的 $\max$ 池化从文本中的任何位置捕获每个词项的最强信号
  \item \textbf{扩展}：即使是原始文本中\emph{不存在的} token 也能获得非零权重（例如，一篇关于“neural networks”的文档可能为“deep learning”、“AI”、“backpropagation”分配权重）
\end{itemize}

\paragraph{Scoring.}
\paragraph{评分}
\label{scoring.}

Query and document are each mapped to sparse vectors $\mathbf{w}^q, \mathbf{w}^d \in \mathbb{R}^{|\mathcal{V}|}$. The relevance score is a simple dot product: 
查询和文档分别被映射为稀疏向量 $\mathbf{w}^q, \mathbf{w}^d \in \mathbb{R}^{|\mathcal{V}|}$。相关性得分是一个简单的点积：
\begin{equation}
  s(q, d) = \sum_{t \in \mathcal{V}} w_t^q \cdot w_t^d
\end{equation}

Because both vectors are sparse (typically 20--200 non-zero entries out of 30K vocabulary), this can be computed efficiently using standard inverted indexes (Lucene, Anserini) --- no GPU needed at query time.
由于两个向量都是稀疏的（通常在 30K 词汇中仅有 20-200 个非零项），这可以通过标准倒排索引（Lucene, Anserini）高效计算——查询时无需 GPU。

\paragraph{Training.}
\paragraph{训练}
\label{training.}

SPLADE is trained with contrastive learning (in-batch negatives + hard negatives) plus two regularization terms:
SPLADE 使用对比学习（批内负样本 + 硬负样本）加上两个正则化项进行训练：

\begin{equation}
  \mathcal{L} = \mathcal{L}_{\text{contrastive}} + \lambda_q \|\mathbf{w}^q\|_1 + \lambda_d \|\mathbf{w}^d\|_1
\end{equation}

The $L_1$ penalties on query and document representations encourage sparsity --- without them, the model would learn dense representations that defeat the purpose.
对查询和文档表示的 $L_1$ 惩罚项鼓励稀疏性——如果没有它们，模型会学到稠密表示，从而违背初衷。

\paragraph{SPLADEv2 --- Key Improvements.}
\paragraph{SPLADEv2 —— 关键改进}
\label{spladev2-key-improvements.}

SPLADEv2~\cite{formal2021spladev2} introduces several refinements that significantly improve efficiency and effectiveness:
SPLADEv2~\cite{formal2021spladev2} 引入了若干改进，显著提升了效率与效果：

\begin{enumerate}
  \item \textbf{Distillation from cross-encoder}: Instead of training only on binary relevance labels, SPLADEv2 uses a cross-encoder teacher (e.g., MonoT5~\cite{nogueira2020document}) to provide soft relevance scores. This gives richer training signal: 
\begin{equation}
    \mathcal{L}_{\text{distill}} = \text{KL}\!\left(\sigma(s_{\text{student}}) \,\|\, \sigma(s_{\text{teacher}})\right)
\end{equation}
  \item \textbf{Separate query/document encoders}: SPLADEv2 uses different sparsity targets for queries vs.~documents. Queries are encouraged to be \emph{more sparse} (faster lookup) while documents can be slightly denser (pre-computed offline): 
\begin{equation}
    \lambda_q > \lambda_d \quad \text{(e.g., } \lambda_q = 3 \times 10^{-4},\; \lambda_d = 1 \times 10^{-4}\text{)}
\end{equation}
  \item \textbf{FLOPS regularization}: Instead of simple $L_1$, SPLADEv2 introduces a FLOPS-aware regularizer that directly penalizes the expected retrieval cost: 
\begin{equation}
    \mathcal{L}_{\text{FLOPS}} = \sum_{t \in \mathcal{V}} \left(\overline{a}_t^q\right)^2 + \sum_{t \in \mathcal{V}} \left(\overline{a}_t^d\right)^2
\end{equation}
 where $\overline{a}_t$ is the mean activation for term $t$ across the batch. This penalizes terms that are non-zero for many documents (high posting list length = slow retrieval).
  \item \textbf{Efficient backbone}: Uses DistilBERT (66M params) instead of BERT-base (110M), halving encoding time with minimal quality loss.
\end{enumerate}

\begin{enumerate}
  \item \textbf{从交叉编码器蒸馏}：SPLADEv2 不再仅基于二元相关性标签进行训练，而是使用交叉编码器教师模型（如 MonoT5~\cite{nogueira2020document}）提供软相关性分数。这提供了更丰富的训练信号：
\begin{equation}
    \mathcal{L}_{\text{distill}} = \text{KL}\!\left(\sigma(s_{\text{学生}}) \,\|\, \sigma(s_{\text{教师}})\right)
\end{equation}
  \item \textbf{独立的查询/文档编码器}：SPLADEv2 对查询和文档使用不同的稀疏性目标。查询被鼓励\emph{更稀疏}（查找更快），而文档可以稍微稠密一些（可离线预计算）：
\begin{equation}
    \lambda_q > \lambda_d \quad \text{（例如， } \lambda_q = 3 \times 10^{-4},\; \lambda_d = 1 \times 10^{-4}\text{）}
\end{equation}
  \item \textbf{FLOPS 正则化}：SPLADEv2 不再使用简单的 $L_1$，而是引入了一种感知 FLOPS 的正则化器，直接惩罚预期的检索成本：
\begin{equation}
    \mathcal{L}_{\text{FLOPS}} = \sum_{t \in \mathcal{V}} \left(\overline{a}_t^q\right)^2 + \sum_{t \in \mathcal{V}} \left(\overline{a}_t^d\right)^2
\end{equation}
 其中 $\overline{a}_t$ 是词项 $t$ 在批次上的平均激活值。这惩罚了那些在众多文档中非零的词项（高倒排列表长度 = 慢速检索）。
  \item \textbf{高效骨架}：使用 DistilBERT（6600 万参数）替代 BERT-base（1.1 亿参数），编码时间减半且质量损失极小。
\end{enumerate}

\begin{keybox}[SPLADE vs. SPLADEv2 Comparison]
\resizebox{\textwidth}{!}{%
\begin{tabular}{@{}lll@{}}
\toprule
\textbf{Aspect} & \textbf{SPLADE (v1)} & \textbf{SPLADEv2} \\
\midrule
Training signal & Binary relevance + hard negatives & Cross-encoder distillation \\
Sparsity control & $L_1$ regularization & FLOPS-aware regularization \\
Query/doc symmetry & Same encoder, same $\lambda$ & Asymmetric (sparser queries) \\
Backbone & BERT-base (110M) & DistilBERT (66M) \\
MRR@10 (MS MARCO~\cite{bajaj2016msmarco}) & 34.0 & 36.8 \\
Avg non-zero terms/doc & $\sim$200 & $\sim$120 (40\% sparser) \\
\bottomrule
\end{tabular}}
\end{keybox}

\begin{keybox}[SPLADE vs. SPLADEv2 对比]
\resizebox{\textwidth}{!}{%
\begin{tabular}{@{}lll@{}}
\toprule
\textbf{方面} & \textbf{SPLADE (v1)} & \textbf{SPLADEv2} \\
\midrule
训练信号 & 二值相关性 + 困难负样本 & 交叉编码器蒸馏 \\
稀疏性控制 & $L_1$ 正则化 & FLOPS 感知正则化 \\
查询/文档对称性 & 相同编码器，相同 $\lambda$ & 非对称（更稀疏的查询） \\
骨干网络 & BERT-base (1.1亿) & DistilBERT (6600万) \\
MRR@10 (MS MARCO~\cite{bajaj2016msmarco}) & 34.0 & 36.8 \\
每个文档平均非零项 & $\sim$200 & $\sim$120 (稀疏40\%) \\
\bottomrule
\end{tabular}}
\end{keybox}

\begin{intuitionbox}[When to Use SPLADE]
\begin{itemize}
  \item \textbf{Use SPLADE/v2 when}: You need semantic retrieval without GPU at query time, your infrastructure already has inverted indexes (Elasticsearch, Lucene), or you need interpretable relevance scores (you can inspect which expanded terms matched).
  \item \textbf{Prefer dense retrieval when}: You have GPU budget for query encoding, need multilingual support (dense models transfer better), or your queries are very short (1--2 words where expansion helps less).
  \item \textbf{Best practice}: Use SPLADEv2 as the first-stage retriever + cross-encoder reranker for top-$k$. This matches or beats dense retrieval pipelines at lower latency.
\end{itemize}
\end{intuitionbox}

\begin{intuitionbox}[何时使用 SPLADE]
\begin{itemize}
  \item \textbf{使用 SPLADE/v2 的场景}：在查询时无需 GPU 即可进行语义检索，你的基础设施已经拥有倒排索引（Elasticsearch、Lucene），或者你需要可解释的相关性分数（你可以检查哪些扩展词匹配上了）。
  \item \textbf{倾向稠密检索的场景}：你有 GPU 预算进行查询编码，需要多语言支持（稠密模型迁移性更好），或者你的查询非常短（1--2个词，扩展帮助较小）。
  \item \textbf{最佳实践}：使用 SPLADEv2 作为第一阶段检索器 + 交叉编码器重排序 top-$k$。这可以匹配或超越稠密检索流程，且延迟更低。
\end{itemize}
\end{intuitionbox}

\subsection{ColBERT: Late Interaction}
\label{colbert-late-interaction}

\subsection{ColBERT：晚期交互}
\label{colbert-late-interaction}

ColBERT~\cite{khattab2020colbert} encodes queries and documents into \emph{sets} of token-level embeddings and uses a \emph{MaxSim} operator for scoring:

ColBERT~\cite{khattab2020colbert} 将查询和文档编码为 token 级嵌入的 \emph{集合}，并使用 \emph{MaxSim} 运算符进行评分：

\begin{equation}
  s(q, d) = \sum_{i \in |\mathbf{q}|} \max_{j \in |\mathbf{d}|} \mathbf{q}_i^\top \mathbf{d}_j
\label{eq:colbert}
\end{equation}

This late interaction mechanism is more expressive than single-vector bi-encoders while being far faster than cross-encoders, since document embeddings are pre-computed offline.

这种晚期交互机制比单向量双编码器更具表现力，同时比交叉编码器快得多，因为文档嵌入可以离线预计算。

\paragraph{Architecture.}
\label{architecture.-1}

\paragraph{架构.}
\label{architecture.-1}

Both the query encoder $E_Q$ and document encoder $E_D$ are BERT-based models that produce \emph{per-token} embeddings (not a single [CLS] vector). Each token embedding is projected to a lower dimension (typically 128) via a linear layer: 

查询编码器 $E_Q$ 和文档编码器 $E_D$ 都是基于 BERT 的模型，生成 \emph{每个 token} 的嵌入（而不是单一的 [CLS] 向量）。每个 token 嵌入通过线性层投影到更低维度（通常为 128）：

\begin{align}
  \mathbf{q}_i &= \text{Linear}(E_Q(q)_i) \in \mathbb{R}^{128}, \quad i = 1, \ldots, |q| \\
  \mathbf{d}_j &= \text{Linear}(E_D(d)_j) \in \mathbb{R}^{128}, \quad j = 1, \ldots, |d|
\end{align}

\paragraph{Training.}
\label{training.-1}

\paragraph{训练.}
\label{training.-1}

ColBERT is trained with a pairwise softmax cross-entropy loss over positive and negative passages. Given a query $q$, a positive passage $d^+$, and a set of negative passages $\{d^-_1, \ldots, d^-_N\}$:

ColBERT 使用成对的 softmax 交叉熵损失在正负段落上进行训练。给定一个查询 $q$，一个正段落 $d^+$，以及一组负段落 $\{d^-_1, \ldots, d^-_N\}$：

\begin{equation}
  \mathcal{L}_{\text{ColBERT}} = -\log \frac{\exp(s(q, d^+))}{\exp(s(q, d^+)) + \sum_{k=1}^{N} \exp(s(q, d^-_k))}
\end{equation}

where $s(q, d)$ is the MaxSim score from Equation~\ref{eq:colbert}. Negatives are sourced from:

其中 $s(q, d)$ 是来自公式~\ref{eq:colbert} 的 MaxSim 分数。负样本来自：

\begin{itemize}
  \item \textbf{In-batch negatives}: Other passages in the same training batch (free, abundant)
  \item \textbf{Hard negatives}: Passages retrieved by BM25 that are lexically similar but semantically irrelevant (most impactful for quality)
  \item \textbf{Distillation negatives} (ColBERTv2~\cite{santhanam2022colbertv2}): Use a cross-encoder teacher to mine the hardest negatives and distill its scores into ColBERT
\end{itemize}

\begin{itemize}
  \item \textbf{批内负样本}：同一训练批次中的其他段落（免费且丰富）
  \item \textbf{困难负样本}：由 BM25 检索到的词汇相似但语义无关的段落（对质量影响最大）
  \item \textbf{蒸馏负样本}（ColBERTv2~\cite{santhanam2022colbertv2}）：使用交叉编码器教师挖掘最困难的负样本，并将其分数蒸馏到 ColBERT 中
\end{itemize}

\paragraph{Indexing and Serving.}
\label{indexing-and-serving.}

\paragraph{索引与服务.}
\label{indexing-and-serving.}

At index time, all document token embeddings are pre-computed and stored (with optional compression via residual quantization in ColBERTv2). At query time, only the query tokens are encoded live, and MaxSim is computed against the stored document embeddings. This separation enables:

在索引时，所有文档 token 嵌入被预计算并存储（在 ColBERTv2 中可通过残差量化进行可选压缩）。在查询时，只有查询 token 被实时编码，并与存储的文档嵌入计算 MaxSim。这种分离带来了：

\begin{itemize}
  \item \textbf{Offline document encoding}: Encode once, serve many queries
  \item \textbf{PLAID indexing} \cite{santhanam2022colbertv2}: Cluster document embeddings, use centroids for initial candidate retrieval, then compute exact MaxSim only on candidates---reducing latency by 5--10$\times$
  \item \textbf{Index size}: $|d| \times 128$ floats per document (larger than single-vector methods but compressible to $\sim$2 bytes/dimension with quantization)
\end{itemize}

\begin{itemize}
  \item \textbf{离线文档编码}：一次编码，服务多次查询
  \item \textbf{PLAID 索引} \cite{santhanam2022colbertv2}：对文档嵌入进行聚类，使用质心进行初始候选检索，然后仅对候选者计算精确 MaxSim——将延迟降低 5--10$\times$
  \item \textbf{索引大小}：每个文档 $|d| \times 128$ 个浮点数（比单向量方法大，但通过量化可压缩到每个维度约 2 字节）
\end{itemize}

\subsection{Retrieval Method Comparison}
\label{retrieval-method-comparison}

\subsection{检索方法比较}
\label{retrieval-method-comparison}

\begin{table}[ht!]
\centering
\caption{Comparison of retrieval methods across key dimensions}
\label{tab:retrieval_methods}
{\footnotesize
\begin{tabular}{@{}llllll@{}}
\toprule
\textbf{Method} & \textbf{Latency} & \textbf{Accuracy} & \textbf{Index Size} & \textbf{GPU} & \textbf{Best For} \\
\midrule
TF-IDF \cite{sparckjones1972idf} & Very Low & Low & Small & No & Baseline, exact match \\
BM25 \cite{robertson2009probabilistic} & Very Low & Medium & Small & No & Keyword search, rare terms \\
DPR / bi-encoder \cite{karpukhin2020dense} & Low & High & Large & Yes & Semantic similarity \\
SPLADE \cite{formal2021splade} & Low & High & Medium & Yes & Hybrid accuracy + speed \\
ColBERT \cite{khattab2020colbert} & Medium & Very High & Very Large & Yes & High-accuracy retrieval \\
Cross-encoder \cite{nogueira2019passage} & High & Highest & N/A & Yes & Re-ranking top-$k$ \\
Hybrid (RRF) \cite{cormack2009reciprocal} & Low & Very High & Large & Yes & Production systems \\
\bottomrule
\end{tabular}
}
\end{table}

\begin{table}[ht!]
\centering
\caption{各检索方法的关键维度比较}
\label{tab:retrieval_methods}
{\footnotesize
\begin{tabular}{@{}llllll@{}}
\toprule
\textbf{方法} & \textbf{延迟} & \textbf{准确率} & \textbf{索引大小} & \textbf{GPU} & \textbf{最佳用途} \\
\midrule
TF-IDF \cite{sparckjones1972idf} & 非常低 & 低 & 小 & 否 & 基线、精确匹配 \\
BM25 \cite{robertson2009probabilistic} & 非常低 & 中等 & 小 & 否 & 关键词搜索、稀有词 \\
DPR / 双编码器 \cite{karpukhin2020dense} & 低 & 高 & 大 & 是 & 语义相似度 \\
SPLADE \cite{formal2021splade} & 低 & 高 & 中等 & 是 & 混合准确率 + 速度 \\
ColBERT \cite{khattab2020colbert} & 中等 & 非常高 & 非常大 & 是 & 高准确率检索 \\
交叉编码器 \cite{nogueira2019passage} & 高 & 最高 & 不适用 & 是 & 重排序 top-$k$ \\
混合 (RRF) \cite{cormack2009reciprocal} & 低 & 非常高 & 大 & 是 & 生产系统 \\
\bottomrule
\end{tabular}
}
\end{table}

\section{Chunking Strategies}
\label{sec:chunking}

\section{分块策略}
\label{sec:chunking}

Chunking is the process of splitting documents into segments that are (1) small enough to fit in an embedding model’s context window, (2) semantically coherent, and (3) contain enough context to be useful when retrieved in isolation.

分块是将文档分割成片段的过程，这些片段需要：(1) 足够小以能放入嵌入模型的上下文窗口，(2) 语义连贯，以及 (3) 包含足够的上下文，以便在单独检索时有用。

\subsection{Fixed-Size Chunking with Overlap}
\label{fixed-size-chunking-with-overlap}

\subsection{固定大小分块（带重叠）}
\label{fixed-size-chunking-with-overlap}

The simplest strategy: split every $W$ tokens with an overlap of $O$ tokens between consecutive chunks.

最简单的策略：每 $W$ 个 token 进行分割，连续块之间有 $O$ 个 token 的重叠。

\begin{lstlisting}[style=pythonstyle, caption={Fixed-size chunking with overlap}]
from langchain.text_splitter import RecursiveCharacterTextSplitter


splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,       # tokens per chunk
    chunk_overlap=64,     # overlap to preserve context across boundaries
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = splitter.split_documents(documents)
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={固定大小分块（带重叠）}]
from langchain.text_splitter import RecursiveCharacterTextSplitter


splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,       # 每个块包含的 token 数
    chunk_overlap=64,     # 重叠 token 数，用于跨边界保留上下文
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = splitter.split_documents(documents)
\end{lstlisting}

\textbf{Overlap formula}: For a document of length $L$ tokens, the number of chunks is: 

\textbf{重叠公式}：对于长度为 $L$ 个 token 的文档，块的数量为：

\begin{equation}
  N_{\text{chunks}} = \left\lceil \frac{L - O}{W - O} \right\rceil
\end{equation}

\subsection{Semantic Chunking}
\label{semantic-chunking}

\subsection{语义分块}
\label{semantic-chunking}

Rather than splitting at fixed intervals, semantic chunking splits at \emph{topic boundaries} detected by measuring embedding similarity between consecutive sentences:

语义分块不是以固定间隔分割，而是在通过测量连续句子之间的嵌入相似度检测到的 \emph{主题边界} 处进行分割：

\begin{lstlisting}[style=pythonstyle, caption={Semantic chunking via embedding similarity}]
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings


chunker = SemanticChunker(
    embeddings=OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",  # or "standard_deviation"
    breakpoint_threshold_amount=95,          # split at top 5% dissimilarity
)
chunks = chunker.split_documents(documents)
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={通过嵌入相似度进行语义分块}]
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings


chunker = SemanticChunker(
    embeddings=OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",  # 或 "standard_deviation"
    breakpoint_threshold_amount=95,          # 在相似度最低的5%处分割
)
chunks = chunker.split_documents(documents)
\end{lstlisting}

\subsection{Document-Structure-Aware Chunking}
\label{document-structure-aware-chunking}

\subsection{文档结构感知分块}
\label{document-structure-aware-chunking}

For structured documents (Markdown, HTML, code), split at natural boundaries:

对于结构化文档（Markdown、HTML、代码），在自然边界处分割：

\begin{itemize}
  \item \textbf{Markdown}: split at \texttt{\#\#} headers, preserving section context
  \item \textbf{HTML}: split at \texttt{<section>}, \texttt{<article>}, \texttt{<p>} tags
  \item \textbf{Code}: split at function/class definitions, preserving imports in each chunk
  \item \textbf{Tables}: keep entire tables as single chunks; never split mid-row
\end{itemize}

\begin{itemize}
  \item \textbf{Markdown}：在 \texttt{\#\#} 标题处分割，保留章节上下文
  \item \textbf{HTML}：在 \texttt{<section>}、\texttt{<article>}、\texttt{<p>} 标签处分割
  \item \textbf{代码}：在函数/类定义处分割，每个块中保留导入语句
  \item \textbf{表格}：将整个表格保留为单个块；切勿在行中间分割
\end{itemize}

\subsection{Parent-Child Chunking}
\label{parent-child-chunking}

\subsection{父子分块}
\label{parent-child-chunking}

A powerful pattern that decouples retrieval granularity from generation context:

一种强大的模式，将检索粒度与生成上下文解耦：

\begin{enumerate}
  \item \textbf{Index small child chunks} (e.g., 128 tokens) for precise retrieval
  \item \textbf{Return large parent chunks} (e.g., 512 tokens) to the LLM for richer context
\end{enumerate}

\begin{enumerate}
  \item \textbf{索引较小的子块}（例如 128 个 token），以便精确检索
  \item \textbf{返回较大的父块}（例如 512 个 token）给 LLM，以提供更丰富的上下文
\end{enumerate}

\begin{lstlisting}[style=pythonstyle, caption={Parent-child chunking with LangChain}]
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter


parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
child_splitter  = RecursiveCharacterTextSplitter(chunk_size=400)


retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=InMemoryStore(),
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)
retriever.add_documents(documents)
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={使用 LangChain 进行父子分块}]
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter


parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
child_splitter  = RecursiveCharacterTextSplitter(chunk_size=400)


retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=InMemoryStore(),
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)
retriever.add_documents(documents)
\end{lstlisting}

\subsection{Empirical Guidelines for Chunk Size}
\label{empirical-guidelines-for-chunk-size}

\subsection{分块大小的经验指南}
\label{empirical-guidelines-for-chunk-size}

\begin{table}[ht!]
\centering
\caption{Chunk size recommendations by use case}
\begin{tabular}{@{}lll@{}}
\toprule
\textbf{Use Case} & \textbf{Recommended Chunk Size} & \textbf{Overlap} \\
\midrule
Factoid QA (precise facts) & 128--256 tokens & 20--32 tokens \\
Summarization / synthesis & 512--1024 tokens & 64--128 tokens \\
Code retrieval & Full function & None \\
Legal / regulatory documents & Paragraph-level & 1 sentence \\
Conversational / chat & 256--512 tokens & 32--64 tokens \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[ht!]
\centering
\caption{不同场景下的分块大小推荐}
\begin{tabular}{@{}lll@{}}
\toprule
\textbf{使用场景} & \textbf{推荐分块大小} & \textbf{重叠} \\
\midrule
事实型问答（精确事实） & 128--256 个 token & 20--32 个 token \\
摘要 / 综合 & 512--1024 个 token & 64--128 个 token \\
代码检索 & 整个函数 & 无 \\
法律 / 监管文档 & 段落级别 & 1 个句子 \\
对话 / 聊天 & 256--512 个 token & 32--64 个 token \\
\bottomrule
\end{tabular}
\end{table}

\section{Advanced RAG Patterns}
\label{advanced-rag-patterns}

\section{高级 RAG 模式}
\label{advanced-rag-patterns}

\subsection{Query Transformation}
\label{query-transformation}

\subsection{查询转换}
\label{query-transformation}

Raw user queries are often ambiguous, too short, or poorly matched to document language. Query transformation techniques improve retrieval before the search step.

原始用户查询通常模糊、过短，或与文档语言不匹配。查询转换技术在搜索步骤之前改进检索。

\paragraph{HyDE (Hypothetical Document Embeddings)~\cite{gao2022precise}.}
\label{hyde-hypothetical-document-embeddings-.}

\paragraph{HyDE（假设文档嵌入）~\cite{gao2022precise}。}
\label{hyde-hypothetical-document-embeddings-.}

Instead of embedding the query directly, generate a \emph{hypothetical answer} and embed that:

不直接对查询进行嵌入，而是先生成一个 \emph{假设答案}，再对其进行嵌入：

\begin{equation}
  \hat{d} = \text{LLM}(q), \quad \mathbf{e}_{\text{query}} = f_\phi(\hat{d})
\end{equation}

The intuition: a hypothetical answer is in the same linguistic register as real documents, reducing the query-document distribution gap.

其直觉在于：假设答案与真实文档使用相同的语言风格，从而缩小查询与文档之间的分布差距。

\paragraph{Step-Back Prompting.}
\label{step-back-prompting.}

\paragraph{后退提示。}
\label{step-back-prompting.}

For specific questions, first generate a more general ``step-back'' question, retrieve for both, and combine the contexts. Example: ``What is the boiling point of ethanol at 2 atm?'' $\to$ step-back: ``What factors affect the boiling point of liquids?''

对于具体问题，先产生一个更笼统的“后退”问题，分别检索两者，然后将上下文合并。例如：“乙醇在 2 个大气压下的沸点是多少？” $\to$ 后退问题：“哪些因素影响液体的沸点？”

\paragraph{Multi-Query Generation.}
\label{multi-query-generation.}

\paragraph{多查询生成。}
\label{multi-query-generation.}

Generate $M$ diverse reformulations of the query, retrieve for each, and union the results:

生成查询的 $M$ 个不同改写版本，对每个版本进行检索，并对结果取并集：

\begin{lstlisting}[style=pythonstyle, caption={Multi-query retrieval}]
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI


retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    llm=ChatOpenAI(temperature=0.7),
    include_original=True,   # also retrieve for original query
)
# Internally generates 3 query variants, retrieves for each, deduplicates
docs = retriever.get_relevant_documents(query)
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={多查询检索}]
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI


retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    llm=ChatOpenAI(temperature=0.7),
    include_original=True,   # 同时为原始查询进行检索
)
# 内部生成 3 个查询变体，对每个进行检索，去重
docs = retriever.get_relevant_documents(query)
\end{lstlisting}

\subsection{Re-Ranking}
\label{re-ranking}

\subsection{重排序}
\label{re-ranking}

After initial retrieval of top-$k$ candidates, a \emph{cross-encoder} re-ranker scores each query-document pair jointly (attending to both simultaneously), producing much more accurate relevance scores at the cost of higher latency:

在初步检索出 top-$k$ 候选结果后，使用一个 \emph{交叉编码器} 重排序器对每个查询-文档对进行联合评分（同时关注两者），以更高的延迟为代价换取更精确的相关性分数：

\begin{equation}
  s_{\text{cross}}(q, d) = \text{CrossEncoder}([q; d])
\end{equation}

Cross-encoders cannot be used for first-stage retrieval (no pre-computed document embeddings), but are ideal for re-ranking a small candidate set (typically $k = 20$--$100$).

交叉编码器不能用于第一阶段检索（无法预先计算文档嵌入），但非常适合对较小的候选集（通常 $k = 20$--$100$）进行重排序。

\begin{lstlisting}[style=pythonstyle, caption={Cross-encoder re-ranking with BGE}]
from sentence_transformers import CrossEncoder


reranker = CrossEncoder("BAAI/bge-reranker-large")


def rerank(query: str, docs: list[str], top_n: int = 5) -> list[str]:
    pairs = [(query, doc) for doc in docs]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, docs), reverse=True)
    return [doc for _, doc in ranked[:top_n]]
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={使用 BGE 进行交叉编码器重排序}]
from sentence_transformers import CrossEncoder


reranker = CrossEncoder("BAAI/bge-reranker-large")


def rerank(query: str, docs: list[str], top_n: int = 5) -> list[str]:
    pairs = [(query, doc) for doc in docs]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, docs), reverse=True)
    return [doc for _, doc in ranked[:top_n]]
\end{lstlisting}

\subsection{Contextual Compression}
\label{contextual-compression}

\subsection{上下文压缩}
\label{contextual-compression}

Retrieved chunks often contain irrelevant sentences surrounding the relevant passage. Contextual compression uses an LLM to extract only the relevant portions:

检索到的块中通常包含与相关段落无关的周围句子。上下文压缩利用 LLM 仅提取相关部分：

\begin{lstlisting}[style=pythonstyle, caption={LLM-based contextual compression}]
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor


compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorstore.as_retriever()
)
compressed_docs = compression_retriever.get_relevant_documents(query)
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={基于 LLM 的上下文压缩}]
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor


compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorstore.as_retriever()
)
compressed_docs = compression_retriever.get_relevant_documents(query)
\end{lstlisting}

\subsection{Self-RAG}
\label{self-rag}

\subsection{Self-RAG}
\label{self-rag}

Self-RAG~\cite{asai2023selfrag} trains a single model to (1) decide \emph{whether} to retrieve, (2) generate with or without retrieval, and (3) \emph{critique} its own output using special reflection tokens:

Self-RAG~\cite{asai2023selfrag} 训练单个模型以（1）决定\emph{是否}需要检索，（2）在有或没有检索的情况下生成，以及（3）使用特殊的反思标记对自己的输出进行\emph{批判}：

\begin{itemize}
  \item \texttt{[Retrieve]}: should the model retrieve additional passages?
  \item \texttt{[IsRel]}: is the retrieved passage relevant to the query?
  \item \texttt{[IsSup]}: does the generated statement follow from the retrieved passage?
  \item \texttt{[IsUse]}: is the overall response useful?
\end{itemize}

\begin{itemize}
  \item \texttt{[Retrieve]}: 模型是否应该检索额外的段落？
  \item \texttt{[IsRel]}: 检索到的段落是否与查询相关？
  \item \texttt{[IsSup]}: 生成的陈述是否源自检索到的段落？
  \item \texttt{[IsUse]}: 整体回答是否有用？
\end{itemize}

The model is trained end-to-end to predict these tokens alongside the response, enabling fine-grained control over retrieval and self-grading.

该模型经过端到端训练，在生成回答的同时预测这些标记，从而实现对检索和自我评分的细粒度控制。

\subsection{CRAG: Corrective RAG}
\label{crag-corrective-rag}

\subsection{CRAG：修正性 RAG}
\label{crag-corrective-rag}

CRAG~\cite{yan2024crag} adds a \emph{retrieval evaluator} that grades retrieved documents and triggers corrective actions:

CRAG~\cite{yan2024crag} 增加了一个\emph{检索评估器}，用于对检索到的文档进行评分并触发修正动作：

\begin{enumerate}
  \item Retrieve top-$k$ documents
  \item Grade each document: \textbf{Correct} / \textbf{Ambiguous} / \textbf{Incorrect}
  \item If all documents are incorrect or ambiguous $\to$ fall back to web search
  \item If some documents are correct $\to$ use knowledge refinement (strip irrelevant sentences)
  \item Generate answer from refined context
\end{enumerate}

\begin{enumerate}
  \item 检索 top-$k$ 个文档
  \item 对每个文档进行评分：\textbf{正确} / \textbf{模糊} / \textbf{错误}
  \item 如果所有文档都错误或模糊 $\to$ 回退到网络搜索
  \item 如果部分文档正确 $\to$ 使用知识精化（剔除无关句子）
  \item 根据精化后的上下文生成答案
\end{enumerate}

\subsection{Adaptive RAG}
\label{adaptive-rag}

\subsection{自适应 RAG}
\label{adaptive-rag}

Adaptive RAG~\cite{jeong2024adaptive} routes queries to different retrieval strategies based on predicted complexity:

自适应 RAG~\cite{jeong2024adaptive} 根据预测的复杂度将查询路由到不同的检索策略：

\begin{itemize}
  \item \textbf{No retrieval}: simple factual queries the model can answer from parameters
  \item \textbf{Single-step RAG}: standard retrieve-then-generate for moderate queries
  \item \textbf{Multi-step RAG}: iterative retrieval for complex multi-hop questions
\end{itemize}

\begin{itemize}
  \item \textbf{无需检索}：模型可以直接从参数中回答的简单事实查询
  \item \textbf{单步 RAG}：针对中等复杂度查询的标准“检索-然后生成”
  \item \textbf{多步 RAG}：针对复杂多跳问题的迭代检索
\end{itemize}

A lightweight classifier trained on query complexity labels routes each incoming query.

一个在查询复杂度标签上训练的轻量级分类器将每个传入的查询路由到相应策略。

\subsection{Graph RAG}
\label{graph-rag}

\subsection{图 RAG}
\label{graph-rag}

Microsoft’s Graph RAG~\cite{edge2024local} constructs a \emph{knowledge graph} from the document corpus and uses community detection to generate hierarchical summaries:

微软的 Graph RAG~\cite{edge2024local} 从文档语料库中构建一个\emph{知识图谱}，并使用社区检测来生成层次化摘要：

\begin{enumerate}
  \item \textbf{Entity extraction}: LLM extracts entities and relationships from each chunk
  \item \textbf{Graph construction}: build a graph $G = (V, E)$ where nodes are entities and edges are relationships
  \item \textbf{Community detection}: apply Leiden algorithm to find communities at multiple resolutions
  \item \textbf{Community summaries}: LLM generates a summary for each community
  \item \textbf{Query}: for global queries, map-reduce over community summaries; for local queries, use standard vector search
\end{enumerate}

\begin{enumerate}
  \item \textbf{实体提取}：LLM 从每个分块中提取实体和关系
  \item \textbf{图构建}：构建图 $G = (V, E)$，其中节点为实体，边为关系
  \item \textbf{社区检测}：应用 Leiden 算法以多分辨率寻找社区
  \item \textbf{社区摘要}：LLM 为每个社区生成摘要
  \item \textbf{查询}：对于全局查询，对社区摘要进行 map-reduce；对于局部查询，使用标准向量搜索
\end{enumerate}

\begin{keybox}[When to Use Graph RAG]
Graph RAG excels at \emph{global} queries that require synthesizing information across many documents (``What are the main themes in this corpus?'') but is expensive to build and maintain. Standard RAG is better for \emph{local} queries (``What did document X say about topic Y?'').
\end{keybox}

\begin{keybox}[何时使用图 RAG]
图 RAG 擅长需要综合多个文档信息的\emph{全局}查询（如“这个语料库的主要主题是什么？”），但构建和维护成本高。标准 RAG 更适合\emph{局部}查询（如“文档 X 对主题 Y 说了什么？”）。
\end{keybox}

\subsection{RAG-Fusion}
\label{rag-fusion}

\subsection{RAG-Fusion}
\label{rag-fusion}

RAG-Fusion~\cite{rackauckas2023ragfusion} generates multiple search queries from the original, retrieves for each, and fuses the ranked lists using RRF (Equation~\ref{eq:rrf}):
RAG-Fusion~\cite{rackauckas2023ragfusion} 从原始查询生成多个搜索变体，对每个变体执行检索，并使用 RRF（公式~\ref{eq:rrf}）融合排序列表：

\begin{lstlisting}[style=pythonstyle, caption={RAG-Fusion with RRF}]
def reciprocal_rank_fusion(ranked_lists: list[list[str]], k: int = 60) -> list[str]:
    """Fuse multiple ranked document lists using RRF."""
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, doc_id in enumerate(ranked, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)


def rag_fusion(query: str, retriever, llm, n_queries: int = 4) -> str:
    # Step 1: Generate query variants
    variants = generate_query_variants(query, llm, n=n_queries)
    # Step 2: Retrieve for each variant
    all_ranked = [retriever.retrieve(q) for q in [query] + variants]
    # Step 3: Fuse with RRF
    fused_docs = reciprocal_rank_fusion(all_ranked)
    # Step 4: Generate answer
    return generate_answer(query, fused_docs[:5], llm)
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={使用 RRF 的 RAG-Fusion}]
def reciprocal_rank_fusion(ranked_lists: list[list[str]], k: int = 60) -> list[str]:
    """使用 RRF 融合多个排序文档列表。"""
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, doc_id in enumerate(ranked, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)


def rag_fusion(query: str, retriever, llm, n_queries: int = 4) -> str:
    # 步骤1：生成查询变体
    variants = generate_query_variants(query, llm, n=n_queries)
    # 步骤2：对每个变体进行检索
    all_ranked = [retriever.retrieve(q) for q in [query] + variants]
    # 步骤3：使用 RRF 融合
    fused_docs = reciprocal_rank_fusion(all_ranked)
    # 步骤4：生成答案
    return generate_answer(query, fused_docs[:5], llm)
\end{lstlisting}


\section{Efficient RAG Decoding: REFRAG}
\label{efficient-rag-decoding-refrag}
\section{高效 RAG 解码：REFRAG}
\label{efficient-rag-decoding-refrag}


A practical bottleneck of RAG is \emph{decoding latency}: the retrieved passages concatenated into the LLM context are often long yet sparsely relevant, inflating time-to-first-token (TTFT) and KV-cache memory. REFRAG \cite{lin2025refrag} observes that because retrieved passages are independently sourced (via diversity or deduplication during re-ranking), their attention patterns are \emph{block-diagonal}---most cross-passage attention is near zero. This sparsity means that the majority of computations over the RAG context during decoding are unnecessary.
RAG 的一个实际瓶颈是 \emph{解码延迟}：拼接进 LLM 上下文的检索段落通常较长但相关性稀疏，这增加了首 token 生成时间（TTFT）和 KV 缓存内存。REFRAG \cite{lin2025refrag} 观察到，由于检索到的段落是独立来源的（通过重排序时的多样性或去重），它们的注意力模式是 \emph{块对角} 的——大多数跨段落的注意力接近零。这种稀疏性意味着解码过程中对 RAG 上下文的大部分计算都是不必要的。

\paragraph{Compress--Sense--Expand Framework.}
\label{compresssenseexpand-framework.}
\paragraph{压缩-感知-扩展框架。}
\label{compresssenseexpand-framework.}


REFRAG exploits this structure via a three-phase decoding strategy:
REFRAG 通过一个三阶段解码策略利用这一结构：

\begin{enumerate}
  \item \textbf{Compress}: Replace full KV representations of retrieved passages with compact summaries (e.g., mean-pooled keys/values per passage block), drastically reducing memory.
  \item \textbf{Sense}: At each decoding step, use lightweight attention over the compressed representations to identify which passage blocks are relevant to the current token.
  \item \textbf{Expand}: Reconstruct full KV entries only for the selected blocks, performing exact attention over the sparse active set.
\end{enumerate}

\begin{enumerate}
  \item \textbf{压缩}：用紧凑的摘要（例如每个段落块的均值池化键/值）替换检索段落的完整 KV 表示，大幅减少内存。
  \item \textbf{感知}：在每个解码步骤，使用轻量级注意力机制对压缩表示进行操作，识别哪些段落块与当前 token 相关。
  \item \textbf{扩展}：仅为选中的块重建完整的 KV 条目，对稀疏的活动集执行精确注意力。
\end{enumerate}

\paragraph{Results.}
\label{results.}
\paragraph{结果。}
\label{results.}


On LLaMA-based models, REFRAG achieves up to $30.85\times$ TTFT speedup (a $3.75\times$ improvement over prior sparse-attention baselines) with no loss in perplexity. It also extends effective context length by $16\times$ under fixed memory budgets. These gains hold across RAG, multi-turn conversation, and long-document summarization tasks.
在基于 LLaMA 的模型上，REFRAG 实现了高达 $30.85\times$ 的 TTFT 加速（相比之前的稀疏注意力基线有 $3.75\times$ 的提升），且困惑度无损失。在固定内存预算下，它还将有效上下文长度扩展了 $16\times$。这些收益在 RAG、多轮对话和长文档摘要任务中均成立。

\begin{intuitionbox}[Why REFRAG Matters for Agentic RAG]
Agentic RAG (Section~\ref{sec:agentic_rag}) requires \emph{multiple} retrieval rounds per query, compounding latency. Efficient decoding methods like REFRAG are essential infrastructure: they make iterative retrieve-reason-generate loops practical at scale by ensuring each round’s decoding cost is sublinear in context length.
\end{intuitionbox}
\begin{intuitionbox}[为什么 REFRAG 对 Agentic RAG 很重要]
Agentic RAG（第~\ref{sec:agentic_rag} 节）需要对每个查询进行\emph{多轮}检索，这会加剧延迟。像 REFRAG 这样的高效解码方法是关键基础设施：它们通过确保每轮解码成本在上下文长度上是次线性的，使得迭代检索-推理-生成循环在大规模下变得实用。
\end{intuitionbox}


\section{Agentic RAG}
\label{sec:agentic_rag}
\section{Agentic RAG}
\label{sec:agentic_rag}


\subsection{Motivation: Limits of Static RAG}
\label{motivation-limits-of-static-rag}
\subsection{动机：静态 RAG 的局限性}
\label{motivation-limits-of-static-rag}


Standard RAG follows a fixed retrieve-then-generate pattern. This fails on:
标准的 RAG 遵循固定的先检索后生成模式。它在以下方面失败：

\begin{itemize}
  \item \textbf{Multi-hop questions}: ``Who founded the company that acquired OpenAI’s main competitor in 2023?'' requires chaining multiple retrievals
  \item \textbf{Ambiguous queries}: the right retrieval strategy depends on what is found
  \item \textbf{Heterogeneous sources}: different sub-questions require different knowledge bases
  \item \textbf{Iterative refinement}: initial retrieval may reveal that a different query is needed
\end{itemize}

\begin{itemize}
  \item \textbf{多跳问题}：“谁创立了收购 OpenAI 主要竞争对手的公司？”需要串联多次检索
  \item \textbf{模糊查询}：正确的检索策略取决于找到的内容
  \item \textbf{异构来源}：不同的子问题需要不同的知识库
  \item \textbf{迭代优化}：初始检索可能表明需要不同的查询
\end{itemize}

\begin{intuitionbox}[RAG as a Markov Decision Process]
Agentic RAG frames retrieval as a sequential decision problem. The \emph{state} is the current context (query + retrieved documents so far); the \emph{actions} include retrieve, reason, generate, and stop; the \emph{reward} is answer correctness. The agent learns a policy for when and what to retrieve.
\end{intuitionbox}
\begin{intuitionbox}[RAG 作为马尔可夫决策过程]
Agentic RAG 将检索建模为序列决策问题。\emph{状态}是当前上下文（查询 + 到目前为止检索到的文档）；\emph{动作}包括检索、推理、生成和停止；\emph{奖励}是答案的正确性。智能体学习何时检索以及检索什么的策略。
\end{intuitionbox}

\subsection{Agentic RAG Architecture}
\label{agentic-rag-architecture}
\subsection{Agentic RAG 架构}
\label{agentic-rag-architecture}


\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_051_agentic_rag.png}
\caption{Agentic RAG control flow. The agent iteratively plans, retrieves, evaluates sufficiency, and self-checks grounding before returning an answer.}
\label{fig:agentic_rag}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_051_agentic_rag.png}
\caption{Agentic RAG 控制流。智能体在返回答案之前迭代地规划、检索、评估充分性并自我检查基础。}
\label{fig:agentic_rag}
\end{figure}

\subsection{Multi-Source Routing}
\label{multi-source-routing}
\subsection{多源路由}
\label{multi-source-routing}


An agentic RAG system can route sub-queries to specialized knowledge sources. The core insight is that different question types demand different retrieval backends---no single index excels at everything.
Agentic RAG 系统可以将子查询路由到专门的知识源。核心洞察是不同类型的问题需要不同的检索后端——没有单一的索引能擅长所有事情。

\paragraph{Why Route?}
\label{why-route}
\paragraph{为什么需要路由？}
\label{why-route}


Consider a financial analyst’s assistant handling four queries:
考虑一个处理四个查询的金融分析师助手：

\begin{itemize}
  \item ``What is our company’s PTO policy?'' $\rightarrow$ \textbf{Vector DB} (internal documents)
  \item ``What did the Fed announce yesterday?'' $\rightarrow$ \textbf{Web search} (real-time)
  \item ``Show Q3 revenue by region'' $\rightarrow$ \textbf{SQL database} (structured data)
  \item ``How does our auth middleware validate tokens?'' $\rightarrow$ \textbf{Code index} (codebase)
\end{itemize}

\begin{itemize}
  \item ``我们公司的带薪休假政策是什么？'' $\rightarrow$ \textbf{向量数据库}（内部文档）
  \item ``美联储昨天宣布了什么？'' $\rightarrow$ \textbf{网络搜索}（实时）
  \item ``按区域显示第三季度收入'' $\rightarrow$ \textbf{SQL 数据库}（结构化数据）
  \item ``我们的认证中间件如何验证 token？'' $\rightarrow$ \textbf{代码索引}（代码库）
\end{itemize}

A flat retrieve-from-one-index approach either misses the answer or returns irrelevant passages. Routing selects the \emph{right tool for the right sub-question} before retrieval begins.
单一的从单一索引检索的方法要么遗漏答案，要么返回不相关的段落。路由在检索开始之前选择\emph{正确的工具处理正确的子问题}。

\paragraph{Routing Strategies.}
\label{routing-strategies.}
\paragraph{路由策略。}
\label{routing-strategies.}


Three main approaches, in increasing sophistication:
三种主要方法，按复杂程度递增：

\begin{enumerate}
  \item \textbf{Rule-based routing.} Keyword triggers (e.g., SQL keywords $\rightarrow$ database, URL patterns $\rightarrow$ web). Fast and interpretable but brittle for ambiguous queries.
  \item \textbf{Classifier-based routing.} A lightweight model (e.g., a fine-tuned BERT classifier or logistic regression over query embeddings) predicts the best source. Low latency ($<$10 ms) and trainable on routing logs, but requires labeled data.
  \item \textbf{LLM-based routing.} The LLM itself decides the source in a structured-output call (see Listing below). Most flexible---handles novel query types and can explain its reasoning---but adds one LLM call of latency.
\end{enumerate}

\begin{enumerate}
  \item \textbf{基于规则的路由。}关键词触发（例如 SQL 关键词 $\rightarrow$ 数据库，URL 模式 $\rightarrow$ 网络）。快速且可解释，但对模糊查询脆弱。
  \item \textbf{基于分类器的路由。}一个轻量级模型（例如微调的 BERT 分类器或基于查询嵌入的逻辑回归）预测最佳来源。低延迟（<$10 ms）且可在路由日志上进行训练，但需要标注数据。
  \item \textbf{基于 LLM 的路由。}LLM 自身通过结构化输出调用决定来源（参见下面的清单）。最灵活——能处理新型查询类型并解释其推理——但增加了一次 LLM 调用的延迟。
\end{enumerate}

\begin{intuitionbox}[Router as a Learned Policy]
Multi-source routing is a \emph{classification} problem at its simplest and a \emph{planning} problem at its richest. When treated as an RL policy---where the state is the query plus conversation history, the action is the choice of source (and optional query rewrite), and the reward is downstream answer quality---the router can be optimized end-to-end via policy gradient techniques (Chapter~\ref{ch:po-variants}).
\end{intuitionbox}
\begin{intuitionbox}[作为学习策略的路由器]
多源路由在最简单时是一个\emph{分类}问题，在最丰富时是一个\emph{规划}问题。当被视为 RL 策略时——其中状态是查询加上对话历史，动作是来源选择（以及可选的查询重写），奖励是下游答案质量——路由器可以通过策略梯度技术（第~\ref{ch:po-variants} 章）进行端到端优化。
\end{intuitionbox}

\paragraph{Practical Considerations.}
\label{practical-considerations.}
\paragraph{实际考虑。}
\label{practical-considerations.}


\begin{itemize}
  \item \textbf{Fallback chains}: If the primary source returns low-confidence results, try the next-best source.
  \item \textbf{Parallel fan-out}: For ambiguous queries, retrieve from multiple sources simultaneously and fuse results via Reciprocal Rank Fusion (Table~\ref{tab:retrieval_methods}).
  \item \textbf{Cost awareness}: Web search and API calls may have monetary cost or rate limits; the router should factor these in.
  \item \textbf{Observability}: Log every routing decision with its reasoning---essential for debugging and retraining.
\end{itemize}

\begin{itemize}
  \item \textbf{回退链}：如果主要来源返回低置信度结果，则尝试次优来源。
  \item \textbf{并行扇出}：对于模糊查询，同时从多个来源检索，并通过倒数排名融合（表~\ref{tab:retrieval_methods}）融合结果。
  \item \textbf{成本感知}：网络搜索和 API 调用可能有货币成本或速率限制；路由器应将这些因素纳入考虑。
  \item \textbf{可观测性}：记录每个路由决策及其推理——对于调试和重新训练至关重要。
\end{itemize}

\begin{lstlisting}[style=pythonstyle, caption={Multi-source agentic RAG router}]
from enum import Enum
from pydantic import BaseModel

\begin{lstlisting}[style=pythonstyle, caption={多源 Agentic RAG 路由器}]
from enum import Enum
from pydantic import BaseModel

```markdown
class KnowledgeSource(str, Enum):
    VECTOR_DB   = "vector_db"    # internal documents
    WEB_SEARCH  = "web_search"   # real-time web
    SQL_DB      = "sql_db"       # structured data
    CODE_INDEX  = "code_index"   # codebase
    API         = "api"          # external APIs

class KnowledgeSource(str, Enum):
    VECTOR_DB   = "vector_db"    # 内部文档
    WEB_SEARCH  = "web_search"   # 实时网络
    SQL_DB      = "sql_db"       # 结构化数据
    CODE_INDEX  = "code_index"   # 代码库
    API         = "api"          # 外部API

class RouteDecision(BaseModel):
    source: KnowledgeSource
    refined_query: str
    reasoning: str

class RouteDecision(BaseModel):
    source: KnowledgeSource
    refined_query: str
    reasoning: str

def route_query(query: str, llm) -> RouteDecision:
    """Use LLM to decide which knowledge source to query."""
    prompt = f"""Given the query: "{query}"
    
Decide which knowledge source to use:
- vector_db: for internal documents, policies, past reports
- web_search: for current events, recent information
- sql_db: for numerical data, statistics, structured records
- code_index: for code examples, API documentation
- api: for real-time data (weather, stock prices, etc.)


Return a JSON with: source, refined_query, reasoning."""
    
    return llm.with_structured_output(RouteDecision).invoke(prompt)
\end{lstlisting}

def route_query(query: str, llm) -> RouteDecision:
    """使用LLM决定查询哪个知识源。"""
    prompt = f"""给定查询："{query}"
    
决定使用哪个知识源：
- vector_db: 用于内部文档、政策、历史报告
- web_search: 用于当前事件、最新信息
- sql_db: 用于数值数据、统计数据、结构化记录
- code_index: 用于代码示例、API文档
- api: 用于实时数据（天气、股票价格等）

返回一个JSON，包含：source, refined_query, reasoning。"""
    
    return llm.with_structured_output(RouteDecision).invoke(prompt)
\end{lstlisting}

\subsection{Full Agentic RAG Implementation}
\label{full-agentic-rag-implementation}

## Full Agentic RAG Implementation
## 完整的智能体RAG实现

The previous sections introduced individual components---routing, retrieval, evaluation. A full agentic RAG system orchestrates these as a \emph{graph of stateful nodes}, where control flow depends on intermediate results. The implementation below uses LangGraph to wire four nodes into a loop:

前面的章节介绍了各个独立组件——路由（Routing）、检索（Retrieval）、评估（Evaluation）。一个完整的智能体RAG系统将这些组件编排成一个\textbf{有状态节点的图}，控制流依赖于中间结果。下面的实现使用LangGraph将四个节点连接成一个循环：

\begin{enumerate}
  \item \textbf{Plan}: Decompose the user query into sub-queries (one per information need).
  \item \textbf{Retrieve}: Route each sub-query to the appropriate source and fetch documents.
  \item \textbf{Evaluate}: Judge whether the accumulated context is sufficient to answer the original query.
  \item \textbf{Generate}: Synthesize a final answer with citations from the retrieved documents.
\end{enumerate}

\begin{enumerate}
  \item \textbf{计划（Plan）}：将用户查询分解为子查询（每个信息需求一个）。
  \item \textbf{检索（Retrieve）}：将每个子查询路由到合适的源并获取文档。
  \item \textbf{评估（Evaluate）}：判断累积的上下文是否足以回答原始查询。
  \item \textbf{生成（Generate）}：综合最终答案，并引用检索到的文档。
\end{enumerate}

The key design pattern is the \emph{conditional loop}: after evaluation, the agent either proceeds to generation (if context is sufficient or the iteration budget is exhausted) or loops back to retrieval with refined sub-queries. This mirrors the sense--act--evaluate cycle of an RL agent operating over information-gathering actions.

关键设计模式是\textbf{条件循环}：评估之后，智能体要么进入生成阶段（如果上下文足够或迭代预算耗尽），要么带着优化的子查询回到检索阶段。这模仿了强化学习（RL）智能体在信息收集动作上的感知-行动-评估循环。

\begin{lstlisting}[style=pythonstyle, caption={LangGraph-based agentic RAG}]
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator


class AgentState(TypedDict):
    query: str
    sub_queries: list[str]
    retrieved_docs: Annotated[list[dict], operator.add]
    context_sufficient: bool
    answer: str
    iterations: int
    max_iterations: int


def plan_node(state: AgentState) -> AgentState:
    """Decompose query into sub-queries."""
    sub_queries = decompose_query(state["query"])
    return {**state, "sub_queries": sub_queries, "iterations": 0}


def retrieve_node(state: AgentState) -> AgentState:
    """Retrieve documents for current sub-queries."""
    new_docs = []
    for sq in state["sub_queries"]:
        source = route_query(sq)
        docs = retrieve_from_source(sq, source)
        new_docs.extend(docs)
    return {**state, "retrieved_docs": new_docs,
            "iterations": state["iterations"] + 1}


def evaluate_node(state: AgentState) -> AgentState:
    """Evaluate whether retrieved context is sufficient."""
    sufficient = evaluate_context_sufficiency(
        query=state["query"],
        docs=state["retrieved_docs"]
    )
    return {**state, "context_sufficient": sufficient}


def generate_node(state: AgentState) -> AgentState:
    """Generate answer from retrieved context."""
    answer = generate_with_citations(
        query=state["query"],
        docs=state["retrieved_docs"]
    )
    return {**state, "answer": answer}


def should_retrieve(state: AgentState) -> str:
    if state["context_sufficient"]:
        return "generate"
    if state["iterations"] >= state["max_iterations"]:
        return "generate"  # give up and generate with what we have
    return "retrieve"


# Build the graph
workflow = StateGraph(AgentState)
workflow.add_node("plan",     plan_node)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("evaluate", evaluate_node)
workflow.add_node("generate", generate_node)


workflow.set_entry_point("plan")
workflow.add_edge("plan",     "retrieve")
workflow.add_edge("retrieve", "evaluate")
workflow.add_conditional_edges("evaluate", should_retrieve,
    {"retrieve": "retrieve", "generate": "generate"})
workflow.add_edge("generate", END)


agent = workflow.compile()


# Run
result = agent.invoke({
    "query": "What were the main causes of the 2023 banking crisis?",
    "max_iterations": 3,
    "retrieved_docs": [],
    "iterations": 0,
})
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={基于LangGraph的智能体RAG}]
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator


class AgentState(TypedDict):
    query: str
    sub_queries: list[str]
    retrieved_docs: Annotated[list[dict], operator.add]
    context_sufficient: bool
    answer: str
    iterations: int
    max_iterations: int


def plan_node(state: AgentState) -> AgentState:
    """将查询分解为子查询。"""
    sub_queries = decompose_query(state["query"])
    return {**state, "sub_queries": sub_queries, "iterations": 0}


def retrieve_node(state: AgentState) -> AgentState:
    """为当前子查询检索文档。"""
    new_docs = []
    for sq in state["sub_queries"]:
        source = route_query(sq)
        docs = retrieve_from_source(sq, source)
        new_docs.extend(docs)
    return {**state, "retrieved_docs": new_docs,
            "iterations": state["iterations"] + 1}


def evaluate_node(state: AgentState) -> AgentState:
    """评估检索到的上下文是否足够。"""
    sufficient = evaluate_context_sufficiency(
        query=state["query"],
        docs=state["retrieved_docs"]
    )
    return {**state, "context_sufficient": sufficient}


def generate_node(state: AgentState) -> AgentState:
    """从检索到的上下文生成答案。"""
    answer = generate_with_citations(
        query=state["query"],
        docs=state["retrieved_docs"]
    )
    return {**state, "answer": answer}


def should_retrieve(state: AgentState) -> str:
    if state["context_sufficient"]:
        return "generate"
    if state["iterations"] >= state["max_iterations"]:
        return "generate"  # 放弃，用已有内容生成
    return "retrieve"


# 构建图
workflow = StateGraph(AgentState)
workflow.add_node("plan",     plan_node)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("evaluate", evaluate_node)
workflow.add_node("generate", generate_node)


workflow.set_entry_point("plan")
workflow.add_edge("plan",     "retrieve")
workflow.add_edge("retrieve", "evaluate")
workflow.add_conditional_edges("evaluate", should_retrieve,
    {"retrieve": "retrieve", "generate": "generate"})
workflow.add_edge("generate", END)


agent = workflow.compile()


# 运行
result = agent.invoke({
    "query": "2023年银行业危机的主要原因是什么？",
    "max_iterations": 3,
    "retrieved_docs": [],
    "iterations": 0,
})
\end{lstlisting}

\subsection{Tool-Augmented RAG}
\label{tool-augmented-rag}

## Tool-Augmented RAG
## 工具增强型RAG

Agentic RAG can combine retrieval with computation tools:

智能体RAG可以将检索与计算工具结合起来：

\begin{lstlisting}[style=pythonstyle, caption={Tool-augmented RAG with SQL and retrieval}]
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import tool


@tool
def search_documents(query: str) -> str:
    """Search internal document knowledge base."""
    docs = vectorstore.similarity_search(query, k=5)
    return "\n\n".join(d.page_content for d in docs)


@tool
def query_database(sql: str) -> str:
    """Execute SQL query on the analytics database."""
    return db.run(sql)


@tool
def web_search(query: str) -> str:
    """Search the web for current information."""
    return tavily_client.search(query)


@tool
def execute_python(code: str) -> str:
    """Execute Python code for calculations."""
    return python_repl.run(code)


tools = [search_documents, query_database, web_search, execute_python]
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={带有SQL和检索的工具增强型RAG}]
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import tool


@tool
def search_documents(query: str) -> str:
    """搜索内部文档知识库。"""
    docs = vectorstore.similarity_search(query, k=5)
    return "\n\n".join(d.page_content for d in docs)


@tool
def query_database(sql: str) -> str:
    """在分析数据库上执行SQL查询。"""
    return db.run(sql)


@tool
def web_search(query: str) -> str:
    """在网络上搜索当前信息。"""
    return tavily_client.search(query)


@tool
def execute_python(code: str) -> str:
    """执行Python代码进行计算。"""
    return python_repl.run(code)


tools = [search_documents, query_database, web_search, execute_python]
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
\end{lstlisting}

\subsection{Search-R1: RL-Trained Agentic RAG}
\label{search-r1-rl-trained-agentic-rag}

## Search-R1: RL-Trained Agentic RAG
## Search-R1：基于强化学习训练的智能体RAG

The agentic RAG approaches above rely on \emph{prompt-engineered} orchestration --- the agent’s search behavior is controlled by instructions, not learned through training. \textbf{Search-R1}~\cite{jin2025searchr1} takes a fundamentally different approach: it trains the LLM via reinforcement learning to \emph{learn when, what, and how many times to search} as part of its reasoning process.

上述智能体RAG方法依赖于\textbf{提示工程}编排——智能体的搜索行为由指令控制，而非通过训练学习。\textbf{Search-R1}~\cite{jin2025searchr1} 采用了一种根本不同的方法：它通过强化学习（Reinforcement Learning, RL）训练LLM，使其\textbf{学习何时、搜索什么以及搜索多少次}，作为其推理过程的一部分。

\paragraph{Core Idea.}
\label{core-idea.}

**Core Idea.**
**核心思想.**

Search-R1 extends the DeepSeek-R1~\cite{deepseek2025r1} reasoning framework by treating search engine queries as \textbf{actions} within the RL training loop. During chain-of-thought generation, the model can emit special tokens \texttt{<search>query</search>} that trigger real-time retrieval from a search engine. The retrieved results are injected back into the reasoning context, and the model continues generating.

Search-R1扩展了DeepSeek-R1~\cite{deepseek2025r1}推理框架，将搜索引擎查询视为RL训练循环中的\textbf{动作}。在思维链（Chain-of-Thought）生成过程中，模型可以发出特殊标记 \texttt{<search>query</search>}，触发从搜索引擎的实时检索。检索结果被重新注入推理上下文，模型继续生成。

\paragraph{Formal Setup.}
\label{formal-setup.}

**Formal Setup.**
**形式化设定.**

The model generates a reasoning trace interleaved with search actions: 
\[
\underbrace{\text{think}_1}_{\text{reasoning}} \to \underbrace{\texttt{<search>}q_1\texttt{</search>}}_{\text{action}} \to \underbrace{[\text{results}_1]}_{\text{observation}} \to \text{think}_2 \to \texttt{<search>}q_2\texttt{</search>} \to \cdots \to \text{answer}
\]
 The entire trajectory (reasoning + searches + final answer) is scored by a terminal reward: correctness of the final answer against a ground-truth label.

模型生成一个与搜索动作交错进行的推理轨迹：
\[
\underbrace{\text{think}_1}_{\text{推理}} \to \underbrace{\texttt{<search>}q_1\texttt{</search>}}_{\text{动作}} \to \underbrace{[\text{结果}_1]}_{\text{观察}} \to \text{think}_2 \to \texttt{<search>}q_2\texttt{</search>} \to \cdots \to \text{答案}
\]
整个轨迹（推理+搜索+最终答案）通过一个终端奖励（Terminal Reward）进行评分：最终答案相对于真实标签的正确性。

\paragraph{Training Algorithm.}
\label{training-algorithm.}

**Training Algorithm.**
**训练算法.**

Search-R1 uses GRPO (Group Relative Policy Optimization):

Search-R1使用GRPO（组相对策略优化，Group Relative Policy Optimization）：

\begin{enumerate}
  \item \textbf{Sample $N$ trajectories} per question, each potentially containing 0--5 search calls
  \item \textbf{Execute searches in real-time} --- the environment returns actual search engine results
  \item \textbf{Score terminal answer correctness} (exact match or F1 against ground truth)
  \item \textbf{Compute group-relative advantage}: $\hat{A}_i = (R_i - \mu_G) / \sigma_G$
  \item \textbf{Update policy} with GRPO clipped objective --- reinforcing trajectories that searched effectively
\end{enumerate}

\begin{enumerate}
  \item \textbf{对每个问题采样 $N$ 条轨迹}，每条轨迹可能包含0-5次搜索调用
  \item \textbf{实时执行搜索}——环境返回实际的搜索引擎结果
  \item \textbf{对终端答案正确性评分}（精确匹配或与真实标签的F1分数）
  \item \textbf{计算组相对优势}：$\hat{A}_i = (R_i - \mu_G) / \sigma_G$
  \item \textbf{使用GRPO裁剪目标更新策略}——强化那些有效搜索的轨迹
\end{enumerate}
```

## Motivation and Problem Statement
## 动机与问题陈述

The model learns to:
该模型学会：

\begin{itemize}
  \item \textbf{Search when uncertain} --- avoid unnecessary searches for knowledge it already has
  \item \textbf{不确定时搜索} —— 避免对已有知识进行不必要的搜索
  \item \textbf{Formulate effective queries} --- learn query phrasing that returns relevant results
  \item \textbf{制定有效查询} —— 学习能返回相关结果的查询措辞
  \item \textbf{Search multiple times} --- iteratively refine queries based on initial results
  \item \textbf{多次搜索} —— 基于初始结果迭代优化查询
  \item \textbf{Integrate retrieved context} --- use search results to support or correct its reasoning
  \item \textbf{整合检索到的上下文} —— 利用搜索结果支持或修正其推理
\end{itemize}

\paragraph{How Search-R1 Differs from Prompt-Based Agentic RAG.}
\label{how-search-r1-differs-from-prompt-based-agentic-rag.}
\paragraph{Search-R1 与基于提示的 Agentic RAG 的区别。}
\label{how-search-r1-differs-from-prompt-based-agentic-rag.}

\begin{table}[ht!]
\centering
\caption{Search-R1 (RL-trained) vs.~prompt-based Agentic RAG.}
\caption{Search-R1（RL训练）与基于提示的 Agentic RAG 的对比。}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Dimension} & \textbf{Prompt-Based Agentic RAG} & \textbf{Search-R1} \\
\textbf{维度} & \textbf{基于提示的 Agentic RAG} & \textbf{Search-R1} \\
\midrule
Search decision & Prompt/heuristic & Learned via RL \\
搜索决策 & 提示/启发式 & 通过RL学习 \\
Query formulation & Prompted (``rewrite query'') & Trained end-to-end \\
查询制定 & 提示（“重写查询”） & 端到端训练 \\
\# searches & Fixed or LLM-decided at inference & Learned optimal count \\
搜索次数 & 固定或在推理时由LLM决定 & 学习最优次数 \\
Training signal & None (frozen model) & Correctness reward \\
训练信号 & 无（冻结模型） & 正确性奖励 \\
Search integration & Append to context & Interleaved in CoT \\
搜索整合 & 追加到上下文 & 穿插在CoT中 \\
Failure recovery & Retry heuristics & Learned backoff/reformulation \\
失败恢复 & 重试启发式 & 学习退避/重新表述 \\
Overhead at inference & Framework overhead (LangGraph) & Native model behavior \\
推理开销 & 框架开销（LangGraph） & 原生模型行为 \\
\bottomrule
\end{tabular}
\end{table}

\paragraph{Results.}
\label{results.-1}
\paragraph{结果。}
\label{results.-1}

On open-domain QA benchmarks (NQ~\cite{kwiatkowski2019natural}, TriviaQA~\cite{joshi2017triviaqa}, HotpotQA~\cite{yang2018hotpotqa}), Search-R1 with a 7B model outperforms:
在开放域问答基准（NQ~\cite{kwiatkowski2019natural}、TriviaQA~\cite{joshi2017triviaqa}、HotpotQA~\cite{yang2018hotpotqa}）上，配备7B模型的Search-R1优于：

\begin{itemize}
  \item Standard RAG (single retrieval) by 15--20\% accuracy
  \item 标准RAG（单次检索）15–20%的准确率
  \item Prompted agentic RAG (ReAct-style) by 8--12\% accuracy
  \item 基于提示的Agentic RAG（ReAct样式）8–12%的准确率
  \item Approaches the performance of much larger models (70B) with standard RAG
  \item 接近使用标准RAG的更大模型（70B）的性能
\end{itemize}

The key insight: \textbf{learning when and how to search is more valuable than having a larger model that knows more}. A small model that searches well beats a large model that doesn’t search.
关键洞察：**学习何时以及如何搜索比拥有一个知识更多的大模型更有价值**。一个搜索能力强的小模型胜过不搜索的大模型。

\begin{intuitionbox}[Search-R1: The Paradigm Shift]
\begin{intuitionbox}[Search-R1：范式转变]
Traditional RAG asks: ``Given this query, what should I retrieve?'' (a pipeline decision made before generation).
传统RAG问：“给定这个查询，我应该检索什么？”（一个在生成之前做出的流水线决策）。

Search-R1 asks: ``Given what I’ve reasoned so far, do I need more information? If so, what specific question would fill this gap?'' (a learned decision made \emph{during} generation).
Search-R1问：“考虑到我目前为止的推理，我需要更多信息吗？如果需要，哪个具体问题能填补这个空白？”（一个在\emph{生成}过程中做出的学习决策）。

This is the difference between a student who looks up the textbook before starting an exam, versus one who consults references mid-problem when they realize they’re stuck. The latter is more efficient and more targeted.
这就好比一个学生在考试前查阅教科书，与另一个在解题中途意识到卡壳时查阅参考资料的区别。后者更高效，更有针对性。
\end{intuitionbox}

\section{Evaluation}
\label{evaluation}
\section{评估}
\label{evaluation}

Evaluating a RAG system is harder than evaluating retrieval or generation in isolation, because errors can originate at \emph{any stage} of the pipeline---and they compound. A perfect generator cannot compensate for irrelevant retrievals, and a perfect retriever is wasted if the generator hallucinates or ignores the context.
评估RAG系统比单独评估检索或生成更困难，因为错误可能源自流水线的\emph{任何阶段}——并且会累积。完美的生成器无法弥补不相关的检索，而如果生成器产生幻觉或忽略上下文，完美的检索器也会被浪费。

Effective RAG evaluation therefore operates at \textbf{three levels}:
因此，有效的RAG评估在\textbf{三个层面}上操作：

\begin{enumerate}
  \item \textbf{Retrieval quality}: Did the retriever surface the right passages? (Recall, Precision, MRR, NDCG)
  \item \textbf{检索质量}：检索器是否返回了正确的段落？（召回率、精确率、MRR、NDCG）
  \item \textbf{Generation quality}: Is the answer correct, faithful to the retrieved context, and complete? (Correctness, Faithfulness, Answer Relevance)
  \item \textbf{生成质量}：答案正确、忠实于检索到的上下文且完整吗？（正确性、忠实性、答案相关性）
  \item \textbf{End-to-end quality}: Does the full system satisfy the user? (Human preference, task success rate, latency-adjusted utility)
  \item \textbf{端到端质量}：整个系统是否满足用户？（人类偏好、任务成功率、延迟调整后的效用）
\end{enumerate}

A common failure mode is optimizing only one level---for example, maximizing Recall@$K$ with large $K$ fills the context with marginally relevant passages that actually \emph{degrade} generation quality. The metrics below cover both retrieval and generation, enabling practitioners to diagnose which stage is the bottleneck.
一个常见的失败模式是只优化一个层面——例如，用大$K$最大化召回率@$K$会用边缘相关的段落填充上下文，这实际上会\emph{降低}生成质量。下面的指标涵盖检索和生成，使从业者能够诊断哪个阶段是瓶颈。

\subsection{Retrieval Metrics}
\label{retrieval-metrics}
\subsection{检索指标}
\label{retrieval-metrics}

Let $\mathcal{R}_k$ be the set of retrieved documents at rank $k$, and $\mathcal{R}^*$ be the set of relevant documents.
设$\mathcal{R}_k$为排名$k$处检索到的文档集合，$\mathcal{R}^*$为相关文档集合。

\paragraph{Recall@K.}
\label{recallk.}
\paragraph{召回率@K.}
\label{recallk.}

\begin{equation}
  \text{Recall@}K = \frac{|\mathcal{R}_K \cap \mathcal{R}^*|}{|\mathcal{R}^*|}
\end{equation}

\paragraph{Precision@K.}
\label{precisionk.}
\paragraph{精确率@K.}
\label{precisionk.}

\begin{equation}
  \text{Precision@}K = \frac{|\mathcal{R}_K \cap \mathcal{R}^*|}{K}
\end{equation}

\paragraph{Mean Reciprocal Rank (MRR).}
\label{mean-reciprocal-rank-mrr.}
\paragraph{平均倒数排名 (MRR).}
\label{mean-reciprocal-rank-mrr.}

\begin{equation}
  \text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}
\end{equation}
 where $\text{rank}_i$ is the rank of the first relevant document for query $i$.
 其中$\text{rank}_i$是查询$i$的第一个相关文档的排名。

\paragraph{Normalized Discounted Cumulative Gain (NDCG@K).}
\label{normalized-discounted-cumulative-gain-ndcgk.}
\paragraph{归一化折损累计增益 (NDCG@K).}
\label{normalized-discounted-cumulative-gain-ndcgk.}

\begin{equation}
  \text{NDCG@}K = \frac{\text{DCG@}K}{\text{IDCG@}K}, \quad
  \text{DCG@}K = \sum_{i=1}^{K} \frac{\text{rel}_i}{\log_2(i+1)}
\end{equation}
 where $\text{rel}_i \in \{0, 1, 2, \ldots\}$ is the graded relevance of the $i$-th result and IDCG is the ideal (perfect) DCG.
 其中$\text{rel}_i \in \{0, 1, 2, \ldots\}$是第$i$个结果的分级相关性，IDCG是理想（完美）DCG。

\subsection{Generation Metrics}
\label{generation-metrics}
\subsection{生成指标}
\label{generation-metrics}

\paragraph{Faithfulness.}
\label{faithfulness.}
\paragraph{忠实性。}
\label{faithfulness.}

Measures whether the generated answer is \emph{grounded} in the retrieved context---i.e., every claim in the answer can be attributed to a retrieved document. Evaluated by an LLM judge:
衡量生成的答案是否\emph{基于}检索到的上下文——即答案中的每一个主张都可以归因于某个检索到的文档。由LLM评判器评估：

\begin{equation}
  \text{Faithfulness} = \frac{\text{\# claims supported by context}}{\text{\# total claims in answer}}
\end{equation}

\paragraph{Answer Relevance.}
\label{answer-relevance.}
\paragraph{答案相关性。}
\label{answer-relevance.}

Measures whether the answer addresses the question. Computed by generating questions from the answer and measuring similarity to the original query:
衡量答案是否回答了问题。通过从答案生成问题并测量与原始查询的相似度来计算：

\begin{equation}
  \text{AnswerRelevance} = \frac{1}{N} \sum_{i=1}^{N} \cos\!\left(E(q), E(\hat{q}_i)\right)
\end{equation}

where $\hat{q}_i$ are questions generated from the answer.
其中$\hat{q}_i$是从答案生成的问题。

\paragraph{Context Precision and Recall.}
\label{context-precision-and-recall.}
\paragraph{上下文精确率和召回率。}
\label{context-precision-and-recall.}

\begin{align}
  \text{ContextPrecision@}K &= \frac{1}{K} \sum_{k=1}^{K} \text{Precision@}k \cdot \mathbf{1}[\text{doc}_k \text{ is relevant}] \\
  \text{ContextRecall} &= \frac{\text{\# ground-truth claims attributable to context}}{\text{\# total ground-truth claims}}
\end{align}

\subsection{RAGAs Framework}
\label{ragas-framework}
\subsection{RAGAs框架}
\label{ragas-framework}

RAGAs (Retrieval Augmented Generation Assessment)~\cite{es2023ragas} provides a reference-free evaluation framework using LLM judges:
RAGAs（检索增强生成评估）~\cite{es2023ragas} 提供了一个使用LLM评判器的无参考评估框架：

\begin{lstlisting}[style=pythonstyle, caption={RAGAs evaluation (v0.1 API; v0.2+ uses \texttt{user\_input}, \texttt{response}, \texttt{retrieved\_contexts}, \texttt{reference})}]
\begin{lstlisting}[style=pythonstyle, caption={RAGAs评估（v0.1 API；v0.2+使用\texttt{user\_input}、\texttt{response}、\texttt{retrieved\_contexts}、\texttt{reference}）}]
from ragas import evaluate
from ragas.metrics import (
    faithfulness,  # 忠实性
    answer_relevancy,  # 答案相关性
    context_precision,  # 上下文精确率
    context_recall,  # 上下文召回率
    answer_correctness,  # 答案正确性
)
from datasets import Dataset


eval_dataset = Dataset.from_dict({  # 评估数据集
    "question":  questions,  # 问题
    "answer":    generated_answers,  # 生成的答案
    "contexts":  retrieved_contexts,   # list of lists  # 检索到的上下文（列表的列表）
    "ground_truth": reference_answers,  # 参考答案
})


results = evaluate(  # 评估结果
    dataset=eval_dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
        answer_correctness,
    ],
)
print(results.to_pandas())  # 打印为pandas DataFrame
\end{lstlisting}

\subsection{Common Failure Modes}
\label{common-failure-modes}
\subsection{常见失败模式}
\label{common-failure-modes}

```markdown
\begin{warningbox}[RAG Failure Modes to Monitor]
\begin{enumerate}
  \item \textbf{Retrieval Miss}: The relevant document exists in the corpus but is not retrieved. Causes: poor chunking, embedding model mismatch, query-document vocabulary gap.
  \item \textbf{检索缺失（Retrieval Miss）}：相关文档存在于语料库中但未被检索到。原因：分块不当、嵌入模型不匹配、查询与文档词汇差异。
  \item \textbf{Context Poisoning}: Retrieved documents contain misleading or contradictory information that causes the model to generate incorrect answers.
  \item \textbf{上下文污染（Context Poisoning）}：检索到的文档包含误导性或矛盾信息，导致模型生成错误答案。
  \item \textbf{Lost-in-the-Middle}: LLMs attend more strongly to the beginning and end of long contexts; relevant information in the middle may be ignored~\cite{liu2023lost}.
  \item \textbf{中间丢失（Lost-in-the-Middle）}：大语言模型更关注长上下文的开头和结尾；中间的相关信息可能被忽略~\cite{liu2023lost}。
  \item \textbf{Over-Retrieval}: Too many retrieved chunks dilute the relevant signal and increase latency and cost.
  \item \textbf{过度检索（Over-Retrieval）}：检索到的块过多会稀释相关信号，增加延迟和成本。
  \item \textbf{Hallucination Despite Retrieval}: Model ignores retrieved context and generates from parametric memory, especially when context contradicts training data.
  \item \textbf{检索后仍出现幻觉（Hallucination Despite Retrieval）}：模型忽略检索到的上下文，仅从参数化记忆中生成，尤其当上下文与训练数据矛盾时。
  \item \textbf{Citation Fabrication}: Model attributes claims to documents that do not support them.
  \item \textbf{引用捏造（Citation Fabrication）}：模型将主张归因于不支持的文档。
\end{enumerate}
\end{warningbox}

\section{Production Considerations}
\section{生产考量}
\label{production-considerations}

\subsection{Embedding Model Selection}
\subsection{嵌入模型选择}
\label{embedding-model-selection}

The embedding model is the single most impactful component choice in a RAG system---it determines the quality ceiling for retrieval. The field has advanced rapidly; Table~\ref{tab:embedding_models} summarizes current options across the cost--quality spectrum.
嵌入模型是RAG系统中影响最大的组件选择——它决定了检索的质量上限。该领域发展迅速；表~\ref{tab:embedding_models} 总结了当前在成本-质量谱系中的选项。

\begin{table}[ht!]
\centering
\caption{Embedding models for production RAG (as of 2026). MTEB scores are overall averages across retrieval, classification, clustering, and STS tasks.}
\caption{用于生产环境RAG的嵌入模型（截至2026年）。MTEB分数为检索、分类、聚类和STS任务的整体平均值。}
\label{tab:embedding_models}
{\footnotesize
\begin{tabular}{@{}llllll@{}}
\toprule
\textbf{Model} & \textbf{Dims} & \textbf{Max Tokens} & \textbf{MTEB Avg} & \textbf{Access} & \textbf{Notes} \\
\textbf{模型} & \textbf{维度} & \textbf{最大令牌数} & \textbf{MTEB平均} & \textbf{访问方式} & \textbf{说明} \\
\midrule
\emph{API-based (managed)} &  &  &  &  &  \\
\emph{基于API（托管型）} &  &  &  &  &  \\
Voyage \texttt{voyage-4-large} & 1024* & 32K & --- & API & Best retrieval quality \\
Voyage \texttt{voyage-4-large} & 1024* & 32K & --- & API & 最佳检索质量 \\
OpenAI \texttt{text-embedding-3-large} & 3072 & 8191 & 64.6 & API & Matryoshka dims \\
OpenAI \texttt{text-embedding-3-large} & 3072 & 8191 & 64.6 & API & 嵌套维度（Matryoshka dims） \\
Cohere \texttt{embed-english-v3.0} & 1024 & 512 & 64.5 & API & int8/binary support \\
Cohere \texttt{embed-english-v3.0} & 1024 & 512 & 64.5 & API & 支持 int8/二值量化 \\
Google \texttt{text-embedding-005} & 768 & 2048 & --- & API & Vertex AI integration \\
Google \texttt{text-embedding-005} & 768 & 2048 & --- & API & 集成 Vertex AI \\
\emph{Open-weight (self-hosted)} &  &  &  &  &  \\
\emph{开放权重（自托管）} &  &  &  &  &  \\
\texttt{nvidia/NV-Embed-v2}~\cite{lee2024nvembed} & 4096 & 32K & 72.3 & Free & \#1 MTEB (Sep 2024) \\
\texttt{nvidia/NV-Embed-v2}~\cite{lee2024nvembed} & 4096 & 32K & 72.3 & 免费 & MTEB排名第一（2024年9月） \\
\texttt{Alibaba-NLP/gte-Qwen2-7B}~\cite{li2023gte} & 3584 & 32K & 70.2 & Free & Apache-2.0, multilingual \\
\texttt{Alibaba-NLP/gte-Qwen2-7B}~\cite{li2023gte} & 3584 & 32K & 70.2 & 免费 & Apache-2.0许可证，多语言 \\
\texttt{BAAI/bge-m3}~\cite{chen2024bgem3} & 1024 & 8192 & 65.0 & Free & Dense + sparse + multi-vec \\
\texttt{BAAI/bge-m3}~\cite{chen2024bgem3} & 1024 & 8192 & 65.0 & 免费 & 稠密+稀疏+多向量 \\
\texttt{jinaai/jina-embeddings-v3} & 1024 & 8192 & 66.0 & Free & Multilingual, LoRA adapters \\
\texttt{jinaai/jina-embeddings-v3} & 1024 & 8192 & 66.0 & 免费 & 多语言，LoRA适配器 \\
\texttt{BAAI/bge-large-en-v1.5}~\cite{xiao2023cpack} & 1024 & 512 & 64.2 & Free & Mature, well-supported \\
\texttt{BAAI/bge-large-en-v1.5}~\cite{xiao2023cpack} & 1024 & 512 & 64.2 & 免费 & 成熟，支持良好 \\
\bottomrule
\end{tabular}
}
\end{table}

\paragraph{Selection Criteria.}
\paragraph{选择标准}
\label{selection-criteria.}

\begin{itemize}
  \item \textbf{Domain match}: Specialized models (e.g., \texttt{voyage-code-3} for code, \texttt{voyage-finance-2} for finance) can outperform general models by 5--15\% on domain tasks.
  \item \textbf{领域匹配}：专用模型（例如用于代码的 \texttt{voyage-code-3}、用于金融的 \texttt{voyage-finance-2}）在领域任务上可比通用模型提升5--15\%。
  \item \textbf{Context length}: Models with 32K token context (Voyage-4, NV-Embed-v2) can embed entire documents without chunking, simplifying the pipeline.
  \item \textbf{上下文长度}：具有32K令牌上下文的模型（Voyage-4, NV-Embed-v2）可以嵌入整个文档而无需分块，从而简化流水线。
  \item \textbf{Matryoshka embeddings}: Models supporting flexible output dimensions (256--4096) let you trade quality for storage/latency at serving time without re-encoding.
  \item \textbf{嵌套嵌入（Matryoshka embeddings）}：支持灵活输出维度（256--4096）的模型允许你在服务时在不重新编码的情况下权衡质量与存储/延迟。
  \item \textbf{Quantization support}: int8 or binary quantization at the model level (Cohere, Voyage) reduces index size by 4--32$\times$ with minimal recall loss.
  \item \textbf{量化支持}：模型级别的 int8 或二值量化（Cohere, Voyage）可将索引大小减少4--32倍，且召回损失极小。
  \item \textbf{Multilingual}: For non-English or cross-lingual RAG, prefer models explicitly trained multilingual (BGE-M3, Jina-v3, Voyage-4).
  \item \textbf{多语言}：对于非英语或跨语言RAG，优先选用明确进行多语言训练的模型（BGE-M3, Jina-v3, Voyage-4）。
\end{itemize}

\subsection{Vector Database Comparison}
\subsection{向量数据库比较}
\label{vector-database-comparison}

\begin{table}[ht!]
\centering
\caption{Vector database comparison for production RAG systems}
\caption{生产环境RAG系统的向量数据库比较}
{\footnotesize
\begin{tabular}{@{}llllll@{}}
\toprule
\textbf{Database} & \textbf{Hosting} & \textbf{Scale} & \textbf{Filtering} & \textbf{Hybrid} & \textbf{Best For} \\
\textbf{数据库} & \textbf{托管方式} & \textbf{规模} & \textbf{过滤} & \textbf{混合搜索} & \textbf{最佳适用场景} \\
\midrule
FAISS1 & Self-hosted & Billions & Limited & No & Research, offline \\
FAISS1 & 自托管 & 十亿级 & 有限 & 否 & 研究、离线 \\
Pinecone2 & Managed & Billions & Yes & Yes & Serverless, easy setup \\
Pinecone2 & 托管 & 十亿级 & 是 & 是 & 无服务器、易部署 \\
Weaviate3 & Both & Billions & Yes & Yes & GraphQL, multi-modal \\
Weaviate3 & 两者皆可 & 十亿级 & 是 & 是 & GraphQL、多模态 \\
Chroma4 & Self-hosted & Millions & Yes & No & Local dev, prototyping \\
Chroma4 & 自托管 & 百万级 & 是 & 否 & 本地开发、原型设计 \\
Qdrant5 & Both & Billions & Yes & Yes & High performance \\
Qdrant5 & 两者皆可 & 十亿级 & 是 & 是 & 高性能 \\
Milvus6 & Both & Billions & Yes & Yes & Enterprise, GPU accel. \\
Milvus6 & 两者皆可 & 十亿级 & 是 & 是 & 企业级、GPU加速 \\
pgvector7 & Self-hosted & Millions & Yes & Yes & Existing Postgres users \\
pgvector7 & 自托管 & 百万级 & 是 & 是 & 现有Postgres用户 \\
\bottomrule
\end{tabular}
}
\end{table}

5\href{https://qdrant.tech}{https://qdrant.tech} 6\href{https://milvus.io}{https://milvus.io} 7\href{https://github.com/pgvector/pgvector}{https://github.com/pgvector/pgvector}
5\href{https://qdrant.tech}{https://qdrant.tech} 6\href{https://milvus.io}{https://milvus.io} 7\href{https://github.com/pgvector/pgvector}{https://github.com/pgvector/pgvector}

\subsection{Latency Optimization}
\subsection{延迟优化}
\label{latency-optimization}

\begin{enumerate}
  \item \textbf{Pre-filtering}: Use metadata filters (date range, category, source) to reduce the search space before ANN search
  \item \textbf{预过滤}：在近似最近邻搜索之前使用元数据过滤器（日期范围、类别、来源）缩小搜索空间
  \item \textbf{Approximate NN}: Use HNSW or IVF indices instead of exact search; accept $\sim$1\% recall loss for $10\times$ speedup
  \item \textbf{近似最近邻}：使用HNSW或IVF索引代替精确搜索；牺牲约1\%的召回率换取10倍加速
  \item \textbf{Embedding caching}: Cache embeddings for frequently repeated queries
  \item \textbf{嵌入缓存}：为频繁重复的查询缓存嵌入向量
  \item \textbf{Async retrieval}: Retrieve from multiple sources in parallel
  \item \textbf{异步检索}：从多个来源并行检索
  \item \textbf{Streaming generation}: Stream LLM output while retrieval completes
  \item \textbf{流式生成}：在检索完成的同时流式输出大语言模型结果
  \item \textbf{Quantization}: Use int8 or binary quantization for embeddings to reduce memory and increase throughput
  \item \textbf{量化}：对嵌入向量使用int8或二值量化以减少内存并增加吞吐量
\end{enumerate}

\paragraph{Async Parallel Retrieval.}
\paragraph{异步并行检索}
\label{async-parallel-retrieval.}

Techniques (3) and (4) above compose naturally: cache the query embedding, then fan out retrieval requests to multiple backends concurrently. In a multi-source RAG system (Section~\ref{sec:agentic_rag}), the user query may need results from a vector database, a keyword index, and a web API. Sequential retrieval adds latencies; parallel retrieval pays only the cost of the \emph{slowest} source. Listing~\ref{lst:async_retrieve} demonstrates this pattern using Python’s \texttt{asyncio}---the \texttt{lru\_cache} decorator ensures repeated queries skip the embedding model entirely, while \texttt{asyncio.gather} dispatches all source queries simultaneously.
上述技术（3）和（4）自然组合：缓存查询嵌入，然后并发地将检索请求分发到多个后端。在多源RAG系统（第~\ref{sec:agentic_rag}节）中，用户查询可能需要来自向量数据库、关键词索引和Web API的结果。顺序检索会增加延迟；并行检索仅支付\textit{最慢}来源的成本。清单~\ref{lst:async_retrieve}使用Python的\texttt{asyncio}展示了这一模式——\texttt{lru\_cache}装饰器确保重复查询完全跳过嵌入模型，而\texttt{asyncio.gather}同时分发所有来源的查询。

\begin{lstlisting}[style=pythonstyle, caption={Async parallel retrieval for low latency}, label=lst:async_retrieve]
import asyncio
from functools import lru_cache


@lru_cache(maxsize=1024)
def get_cached_embedding(text: str) -> list[float]:
    return embedding_model.embed_query(text)


async def parallel_retrieve(
    query: str,
    sources: list[str],
    k: int = 5
) -> list[dict]:
    """Retrieve from multiple sources in parallel."""
    """从多个来源并行检索。"""
    tasks = [
        asyncio.create_task(retrieve_from_source_async(query, src, k))
        for src in sources
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # Flatten and deduplicate
    # 展平并去重
    all_docs = []
    for r in results:
        if not isinstance(r, Exception):
            all_docs.extend(r)
    return deduplicate_by_content(all_docs)
\end{lstlisting}

\subsection{Incremental Indexing and Versioning}
\subsection{增量索引与版本管理}
\label{incremental-indexing-and-versioning}

In production, the document corpus is never static---policies get revised, new reports land daily, deprecated content must be removed. A full re-index (re-chunk, re-embed, re-upload) is expensive and causes downtime. Incremental indexing solves this by applying changes at the document level.
在生产环境中，文档语料库从不是静态的——政策会被修订，新报告每日涌现，过时内容必须移除。全量重新索引（重新分块、重新嵌入、重新上传）成本高昂且会导致停机。增量索引通过在文档级别应用更改解决了这一问题。

\paragraph{Core Operations.}
\paragraph{核心操作}
\label{core-operations.}
```

```markdown
\begin{itemize}
  \item \textbf{Upsert}: When a document is created or updated, delete all existing chunks for that \texttt{doc\_id}, re-chunk the new content, embed, and insert. This guarantees no stale fragments linger.
  \item \textbf{Delete/Expire}: Remove chunks by document ID (explicit deletion) or by TTL (automatic garbage collection for time-sensitive sources like news or market data).
  \item \textbf{Version tracking}: Store a \texttt{version} and \texttt{indexed\_at} timestamp in chunk metadata. This enables rollback (restore previous version from source) and auditability (``which version did the model see?'').
\end{itemize}

\begin{itemize}
  \item \textbf{Upsert（更新插入）}：当文档被创建或更新时，删除该 \texttt{doc\_id} 的所有现有块，对新内容重新分块、嵌入并插入。这确保不会有陈旧的片段残留。
  \item \textbf{Delete/Expire（删除/过期）}：通过文档ID（显式删除）或TTL（针对新闻或市场数据等时间敏感源的自动垃圾回收）移除块。
  \item \textbf{Version tracking（版本追踪）}：在块元数据中存储 \texttt{version} 和 \texttt{indexed\_at} 时间戳。这支持回滚（从源恢复先前版本）和可审计性（“模型看到的是哪个版本？”）。
\end{itemize}

\paragraph{Consistency Challenges.}
\label{consistency-challenges.}

\paragraph{一致性挑战。}
\label{consistency-challenges.}

\begin{itemize}
  \item \textbf{Embedding model drift}: If you upgrade the embedding model, old and new vectors are incompatible. Solutions: (a) maintain separate indices per model version and migrate in the background, or (b) use Matryoshka-compatible models where dimension truncation preserves compatibility.
  \item \textbf{Chunk boundary shifts}: Changing the chunking strategy invalidates all existing chunks. Version metadata lets you identify and selectively re-index affected documents.
  \item \textbf{Eventual consistency}: In distributed vector databases, newly upserted vectors may not be immediately searchable. Design your pipeline to tolerate a brief indexing lag (typically seconds to minutes).
\end{itemize}

\begin{itemize}
  \item \textbf{嵌入模型漂移}：如果升级嵌入模型，新旧向量不兼容。解决方案：(a) 为每个模型版本维护独立的索引并在后台迁移，或(b) 使用Matryoshka兼容模型，其中维度截断保留了兼容性。
  \item \textbf{分块边界变化}：更改分块策略会使所有现有块失效。版本元数据允许您识别并有选择地重新索引受影响的文档。
  \item \textbf{最终一致性}：在分布式向量数据库中，新更新插入的向量可能无法立即搜索。设计你的流水线以容忍短暂的索引延迟（通常为秒到分钟）。
\end{itemize}

\paragraph{Implementation.}
\label{implementation.}

\paragraph{实现。}
\label{implementation.}

Listing~\ref{lst:incremental_index} shows a minimal \texttt{RAGIndexManager} class that encapsulates upsert and expiration logic, suitable for wrapping any vector store with metadata filtering support.

列表~\ref{lst:incremental_index} 展示了一个极简的 \texttt{RAGIndexManager} 类，它封装了更新插入和过期逻辑，适用于包装任何支持元数据过滤的向量存储。

\begin{lstlisting}[style=pythonstyle, caption={Incremental index updates with versioning}, label={lst:incremental_index}]
class RAGIndexManager:
    def __init__(self, vectorstore, metadata_store, chunker, embedder):
        self.vs = vectorstore
        self.meta = metadata_store
        self.chunker = chunker
        self.embedder = embedder

    def upsert_document(self, doc_id: str, content: str,
                        metadata: dict) -> None:
        """Add or update a document, replacing old chunks."""
        # Delete existing chunks for this document
        self.vs.delete(filter={"doc_id": doc_id})
        # Chunk new version (vectorstore embeds internally)
        chunks = self.chunker.split_text(content)
        self.vs.add_texts(
            texts=chunks,
            metadatas=[{**metadata, "doc_id": doc_id,
                        "version": metadata.get("version", 1),
                        "indexed_at": datetime.utcnow().isoformat()}
                       for _ in chunks],
        )

    def expire_old_documents(self, ttl_days: int = 365) -> int:
        """Remove documents older than TTL."""
        cutoff = (datetime.utcnow() - timedelta(days=ttl_days)).isoformat()
        return self.vs.delete(filter={"indexed_at": {"$lt": cutoff}})
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={带版本控制的增量索引更新}, label={lst:incremental_index}]
class RAGIndexManager:
    def __init__(self, vectorstore, metadata_store, chunker, embedder):
        self.vs = vectorstore
        self.meta = metadata_store
        self.chunker = chunker
        self.embedder = embedder

    def upsert_document(self, doc_id: str, content: str,
                        metadata: dict) -> None:
        """添加或更新文档，替换旧块。"""
        # 删除该文档的现有块
        self.vs.delete(filter={"doc_id": doc_id})
        # 对新版本分块（向量存储内部嵌入）
        chunks = self.chunker.split_text(content)
        self.vs.add_texts(
            texts=chunks,
            metadatas=[{**metadata, "doc_id": doc_id,
                        "version": metadata.get("version", 1),
                        "indexed_at": datetime.utcnow().isoformat()}
                       for _ in chunks],
        )

    def expire_old_documents(self, ttl_days: int = 365) -> int:
        """移除超过TTL的文档。"""
        cutoff = (datetime.utcnow() - timedelta(days=ttl_days)).isoformat()
        return self.vs.delete(filter={"indexed_at": {"$lt": cutoff}})
\end{lstlisting}

\section{RAG + Fine-Tuning Synergy}
\label{rag-fine-tuning-synergy}

\section{RAG + 微调协同}
\label{rag-fine-tuning-synergy}

\subsection{When to Combine RAG with Fine-Tuning}
\label{when-to-combine-rag-with-fine-tuning}

\subsection{何时将RAG与微调结合}
\label{when-to-combine-rag-with-fine-tuning}

Fine-tuning and RAG address complementary weaknesses:

微调和RAG解决互补的弱点：

\begin{itemize}
  \item \textbf{Fine-tuning alone}: model learns style and format but may hallucinate facts
  \item \textbf{RAG alone}: model has access to facts but may not know how to use them optimally
  \item \textbf{Combined}: fine-tune the model to \emph{use retrieved context well}---cite sources, acknowledge uncertainty, and ignore irrelevant context
\end{itemize}

\begin{itemize}
  \item \textbf{仅微调}：模型学习风格和格式，但可能产生事实幻觉
  \item \textbf{仅RAG}：模型能访问事实，但可能不知道如何最优地使用它们
  \item \textbf{结合}：微调模型以\emph{善用检索到的上下文}——引用来源、承认不确定性、忽略无关上下文
\end{itemize}

\subsection{RAFT: Retrieval-Augmented Fine-Tuning}
\label{raft-retrieval-augmented-fine-tuning}

\subsection{RAFT：检索增强微调}
\label{raft-retrieval-augmented-fine-tuning}

RAFT~\cite{zhang2024raft} trains models to answer questions given a mix of relevant and \emph{distractor} documents, teaching the model to identify and use only the relevant context:

RAFT~\cite{zhang2024raft} 训练模型在给定相关文档和\emph{干扰}文档混合的情况下回答问题，教会模型识别并仅使用相关上下文：

\begin{enumerate}
  \item For each training example $(q, a, d^*)$, sample $k-1$ distractor documents $\{d_i^-\}$
  \item Fine-tune on: \texttt{[q, }$d^*$\texttt{, }$d_1^-$\texttt{, \ldots{}, }$d_{k-1}^-$\texttt{]} $\to$ \texttt{[chain-of-thought + a]}
  \item The chain-of-thought explicitly quotes from $d^*$, teaching the model to ground answers
\end{enumerate}

\begin{enumerate}
  \item 对于每个训练样本 $(q, a, d^*)$，采样 $k-1$ 个干扰文档 $\{d_i^-\}$
  \item 微调目标：\texttt{[q, }$d^*$\texttt{, }$d_1^-$\texttt{, \ldots{}, }$d_{k-1}^-$\texttt{]} $\to$ \texttt{[chain-of-thought + a]}
  \item 思维链显式引用 $d^*$，教会模型将答案基于证据
\end{enumerate}

\begin{equation}
  \mathcal{L}_{\text{RAFT}} = -\mathbb{E}_{(q,a,d^*,\{d_i^-\})} \left[
    \log P_\theta\!\left(\text{CoT}(d^*) \oplus a \;\middle|\; q, d^*, \{d_i^-\}\right)
  \right]
\end{equation}

\begin{equation}
  \mathcal{L}_{\text{RAFT}} = -\mathbb{E}_{(q,a,d^*,\{d_i^-\})} \left[
    \log P_\theta\!\left(\text{CoT}(d^*) \oplus a \;\middle|\; q, d^*, \{d_i^-\}\right)
  \right]
\end{equation}

\subsection{Joint Retriever-Generator Training}
\label{joint-retriever-generator-training}

\subsection{联合检索器-生成器训练}
\label{joint-retriever-generator-training}

For maximum performance, the retriever and generator can be trained jointly. The REALM~\cite{guu2020realm} and RAG~\cite{lewis2020retrieval} papers propose end-to-end training where gradients flow through the retrieval step:

为获得最佳性能，检索器和生成器可以联合训练。REALM~\cite{guu2020realm} 和 RAG~\cite{lewis2020retrieval} 论文提出了端到端训练，梯度通过检索步骤流动：

\begin{equation}
  \nabla_\theta \mathcal{L} = \nabla_\theta \left[
    -\log \sum_{d \in \mathcal{D}} P_\theta(a \mid q, d) \cdot P_\phi(d \mid q)
  \right]
\end{equation}

\begin{equation}
  \nabla_\theta \mathcal{L} = \nabla_\theta \left[
    -\log \sum_{d \in \mathcal{D}} P_\theta(a \mid q, d) \cdot P_\phi(d \mid q)
  \right]
\end{equation}

The retriever parameters $\phi$ are updated using the REINFORCE estimator or by treating $P_\phi(d \mid q)$ as a differentiable attention over documents.

检索器参数 $\phi$ 通过REINFORCE估计器或通过将 $P_\phi(d \mid q)$ 视为文档上的可微分注意力来更新。

\begin{warningbox}[Joint Training Challenges]
Joint retriever-generator training is powerful but complex: (1) the document index must be periodically refreshed as $\phi$ changes (asynchronous index refresh), (2) the training signal is sparse (only top-$k$ documents contribute), and (3) training is unstable without careful initialization from a pre-trained retriever.
\end{warningbox}

\begin{warningbox}[联合训练挑战]
联合检索器-生成器训练功能强大但复杂：(1) 文档索引必须随 $\phi$ 的变化定期刷新（异步索引刷新），(2) 训练信号稀疏（仅 top-$k$ 文档有贡献），(3) 如果没有从预训练检索器进行仔细初始化，训练不稳定。
\end{warningbox}

\section{Comprehensive RAG Approach Comparison}
\label{comprehensive-rag-approach-comparison}

\section{综合RAG方法比较}
\label{comprehensive-rag-approach-comparison}

\begin{table}[ht!]
\centering
\caption{RAG approaches across key dimensions}
{\footnotesize
\begin{tabular}{@{}llllll@{}}
\toprule
\textbf{Approach} & \textbf{Accuracy} & \textbf{Latency} & \textbf{Complexity} & \textbf{Cost} & \textbf{Best For} \\
\midrule
Naive RAG \cite{lewis2020retrieval} & Medium & Low & Low & Low & Prototyping, simple QA \\
RAG + Re-ranking \cite{nogueira2019passage} & High & Medium & Medium & Medium & Production QA systems \\
HyDE \cite{gao2022precise} & High & Medium & Low & Medium & Semantic mismatch domains \\
Multi-Query RAG & High & Medium & Medium & Medium & Ambiguous queries \\
RAG-Fusion \cite{rackauckas2023ragfusion} & High & Medium & Medium & Medium & Diverse query types \\
Self-RAG \cite{asai2023selfrag} & High & Medium & High & Medium & Selective retrieval \\
CRAG \cite{yan2024crag} & High & Medium & High & High & Unreliable corpora \\
Adaptive RAG \cite{jeong2024adaptive} & High & Low--High & High & Medium & Mixed query complexity \\
Graph RAG \cite{edge2024local} & V. High & High & V. High & High & Global synthesis queries \\
Agentic RAG & V. High & High & V. High & High & Multi-hop reasoning \\
RAFT \cite{zhang2024raft} & V. High & Low & V. High & V. High & Domain-specific deployment \\
\bottomrule
\end{tabular}
}
\end{table}

\begin{table}[ht!]
\centering
\caption{各关键维度下的RAG方法}
{\footnotesize
\begin{tabular}{@{}llllll@{}}
\toprule
\textbf{方法} & \textbf{准确性} & \textbf{延迟} & \textbf{复杂度} & \textbf{成本} & \textbf{最佳适用场景} \\
\midrule
Naive RAG \cite{lewis2020retrieval} & 中 & 低 & 低 & 低 & 原型开发、简单问答 \\
RAG + 重排序 \cite{nogueira2019passage} & 高 & 中 & 中 & 中 & 生产级问答系统 \\
HyDE \cite{gao2022precise} & 高 & 中 & 低 & 中 & 语义不匹配领域 \\
多查询 RAG & 高 & 中 & 中 & 中 & 模糊查询 \\
RAG-Fusion \cite{rackauckas2023ragfusion} & 高 & 中 & 中 & 中 & 多样查询类型 \\
Self-RAG \cite{asai2023selfrag} & 高 & 中 & 高 & 中 & 选择性检索 \\
CRAG \cite{yan2024crag} & 高 & 中 & 高 & 高 & 不可靠语料库 \\
Adaptive RAG \cite{jeong2024adaptive} & 高 & 低--高 & 高 & 中 & 混合查询复杂度 \\
Graph RAG \cite{edge2024local} & 很高 & 高 & 很高 & 高 & 全局综合查询 \\
Agentic RAG & 很高 & 高 & 很高 & 高 & 多跳推理 \\
RAFT \cite{zhang2024raft} & 很高 & 低 & 很高 & 很高 & 特定领域部署 \\
\bottomrule
\end{tabular}
}
\end{table}

\begin{questionbox}[Key Design Questions for RAG Systems]
When designing a RAG system for production, consider:

\begin{questionbox}[RAG系统的关键设计问题]
在设计用于生产的RAG系统时，请考虑：

\begin{enumerate}
  \item \textbf{What is the query distribution?} Factoid vs.~analytical vs.~multi-hop queries require different retrieval strategies.
  \item \textbf{How large and dynamic is the corpus?} Millions of documents with frequent updates favor managed vector databases with incremental indexing.
  \item \textbf{What are the latency requirements?} Sub-100ms responses preclude re-ranking and agentic loops; batch or async use cases can afford them.
  \item \textbf{How critical is grounding?} High-stakes domains (medical, legal, financial) require faithfulness evaluation and citation verification.
  \item \textbf{Is the vocabulary specialized?} Domain-specific terminology may require hybrid retrieval or domain-adapted embedding models.
\end{enumerate}
\end{questionbox}

\begin{enumerate}
  \item \textbf{查询分布是什么？} 事实型查询、分析型查询与多跳查询需要不同的检索策略。
  \item \textbf{语料库有多大且动态性如何？} 数百万文档且频繁更新，更适合采用支持增量索引的托管向量数据库。
  \item \textbf{延迟要求是什么？} 亚100毫秒响应时间排除了重排序和智能体循环；批处理或异步用例则可以接受这些开销。
  \item \textbf{基于证据有多重要？} 高风险领域（医疗、法律、金融）需要忠实性评估和引用验证。
  \item \textbf{词汇是否专业？} 特定领域的术语可能需要混合检索或领域适配的嵌入模型。
\end{enumerate}
\end{questionbox}
```

\begin{keybox}[RAG Best Practices Summary]
\begin{keybox}[RAG最佳实践总结]
\begin{itemize}
  \item \textbf{Start simple}: naive RAG with good chunking often outperforms complex systems with poor chunking
  \item \textbf{从简单开始}：naive RAG（朴素RAG）搭配良好的chunking（分块）通常优于分块不佳的复杂系统
  \item \textbf{Evaluate retrieval separately}: fix retrieval before optimizing generation
  \item \textbf{单独评估retrieval（检索）}：在优化generation（生成）之前先修复检索
  \item \textbf{Use hybrid retrieval}: BM25 + dense with RRF is a strong default
  \item \textbf{使用hybrid retrieval（混合检索）}：BM25 + dense（稠密检索）配合RRF（倒数排名融合，Reciprocal Rank Fusion）是一个强大的默认方案
  \item \textbf{Add re-ranking}: a cross-encoder re-ranker on top-20 candidates is high ROI
  \item \textbf{添加re-ranking（重排序）}：对前20个候选结果使用cross-encoder（交叉编码器）re-ranker（重排序器）具有高ROI（投资回报率）
  \item \textbf{Monitor faithfulness}: track hallucination rate in production with LLM judges
  \item \textbf{监控faithfulness（忠实性）}：在生产环境中使用LLM judges（大语言模型评估器）跟踪hallucination rate（幻觉率）
  \item \textbf{Cache aggressively}: embed documents once; cache frequent query embeddings
  \item \textbf{积极cache（缓存）}：将文档embed（嵌入）一次；缓存频繁查询的embeddings（嵌入向量）
  \item \textbf{Chunk with overlap}: 10--15\% overlap prevents information loss at boundaries
  \item \textbf{带overlap（重叠）的chunk（分块）}：10--15\%的重叠可防止边界处的信息丢失
  \item \textbf{Store rich metadata}: source, date, section, and document type enable powerful pre-filtering that dramatically improves precision
  \item \textbf{存储丰富的metadata（元数据）}：来源、日期、章节和文档类型能够实现强大的pre-filtering（预过滤），从而显著提高精确度
\end{itemize}
\end{keybox}