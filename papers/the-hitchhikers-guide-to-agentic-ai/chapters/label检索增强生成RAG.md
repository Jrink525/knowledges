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
