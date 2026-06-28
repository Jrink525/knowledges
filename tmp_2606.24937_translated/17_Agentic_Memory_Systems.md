```markdown
## Chapter: Agentic Memory Systems
## 章节：代理记忆系统

\chapter{Agentic Memory Systems}
\label{sec:agentic-memory}

\section{Motivation: Why Agents Need Memory}
\label{sec:memory-motivation}
\section{动机：为什么代理需要记忆}
\label{sec:memory-motivation}

Large language models are, at their core, stateless function approximators: given a prompt $x$, they produce a distribution over continuations $p_\theta(y \mid x)$. Every inference call begins from scratch. The \emph{context window}---the finite sequence of tokens the model can attend to---is the only information available at generation time. For short, self-contained tasks this is sufficient. For long-horizon agentic tasks it is a fundamental bottleneck.

大型语言模型的核心是无状态函数逼近器：给定提示 $x$，它们生成延续上的分布 $p_\theta(y \mid x)$。每次推理调用都从头开始。\emph{上下文窗口}——模型可以关注的有限 token 序列——是生成时可用的唯一信息。对于短期的自包含任务来说，这已经足够。但对于长期代理型任务来说，这是一个根本性的瓶颈。

\begin{keybox}[The Context-Window Bottleneck]
Let $L$ denote the maximum context length (e.g.~$L = 128{,}000$ tokens for GPT-4o). A single token encodes roughly 4 characters; a typical book contains $\sim\!500{,}000$ words $\approx 670{,}000$ tokens. Even ignoring cost, a multi-day autonomous agent accumulates observations, tool outputs, and reasoning traces that \emph{cannot} fit in any fixed window. Memory systems are the engineering response to this physical constraint.
\end{keybox}
\begin{keybox}[上下文窗口瓶颈]
令 $L$ 表示最大上下文长度（例如 GPT-4o 的 $L = 128{,}000$ 个 token）。单个 token 大约编码 4 个字符；一本典型的书籍包含 $\sim\!500{,}000$ 个单词 $\approx 670{,}000$ 个 token。即使忽略成本，一个运行多天的自主代理也会累积观察结果、工具输出和推理轨迹，这些内容\emph{无法}放入任何固定窗口。记忆系统就是针对这种物理约束的工程应对方案。
\end{keybox}

Three distinct failure modes arise when agents lack persistent memory:

当代理缺乏持久记忆时，会出现三种不同的故障模式：

\begin{enumerate}
  \item \textbf{Catastrophic forgetting of context.} Once an event scrolls out of the context window it is irrecoverably lost. The agent cannot refer back to a decision made 10,000 tokens ago.
  \item \textbf{Inability to learn from experience.} Without episodic storage, every episode is the agent’s first. Successful strategies cannot be reused; mistakes are repeated.
  \item \textbf{Lack of personalization.} User preferences, domain facts, and relationship history must be re-established in every session, degrading user experience and efficiency.
\end{enumerate}
\begin{enumerate}
  \item \textbf{上下文灾难性遗忘。}一旦事件滚动出上下文窗口，就会不可恢复地丢失。代理无法回溯到 10,000 个 token 之前做出的决策。
  \item \textbf{无法从经验中学习。}没有情景存储，每一次情景都是代理的第一次。成功的策略无法重用；错误会重复发生。
  \item \textbf{缺乏个性化。}用户偏好、领域事实和关系历史必须在每个会话中重新建立，从而降低用户体验和效率。
\end{enumerate}

\begin{intuitionbox}[Memory as Cognitive Architecture]
Cognitive science distinguishes several memory systems in biological agents~\cite{tulving1985memory, squire1992declarative}: \emph{working memory} (active manipulation of information), \emph{episodic memory} (autobiographical events), \emph{semantic memory} (world knowledge), and \emph{procedural memory} (skills and habits). Effective agentic AI systems benefit from analogous distinctions---not because we are simulating neuroscience, but because these categories reflect genuinely different \emph{access patterns}, \emph{update frequencies}, and \emph{retrieval mechanisms}.
\end{intuitionbox}
\begin{intuitionbox}[记忆作为认知架构]
认知科学区分了生物代理中的几种记忆系统~\cite{tulving1985memory, squire1992declarative}：\emph{工作记忆}（信息的主动处理）、\emph{情景记忆}（自传式事件）、\emph{语义记忆}（世界知识）和\emph{程序性记忆}（技能和习惯）。有效的代理型AI系统受益于类似的区分——不是因为我们模拟神经科学，而是因为这些类别反映了真正不同的\emph{访问模式}、\emph{更新频率}和\emph{检索机制}。
\end{intuitionbox}

Formally, we model an agent as a tuple $\mathcal{A} = (\pi_\theta, \mathcal{M}, \mathcal{R}, \mathcal{W})$ where $\pi_\theta$ is the policy (the LLM), $\mathcal{M}$ is the memory store, $\mathcal{R}: \mathcal{Q} \times \mathcal{M} \to \mathcal{D}$ is a retrieval function mapping queries to retrieved documents, and $\mathcal{W}: \mathcal{M} \times \mathcal{E} \to \mathcal{M}$ is a write function updating memory with new experiences $\mathcal{E}$. At each step $t$ the agent observes $o_t$, retrieves relevant context $c_t = \mathcal{R}(o_t, \mathcal{M})$, and acts: 
\[
a_t \sim \pi_\theta\!\left(\cdot \;\middle|\; [s_t;\, c_t;\, h_t]\right),
\]
 where $s_t$ is the current system prompt, $c_t$ is retrieved memory, and $h_t$ is the recent in-context history. After acting, the agent may write new information: $\mathcal{M} \leftarrow \mathcal{W}(\mathcal{M},\, (o_t, a_t, r_t))$.

形式上，我们将代理建模为一个元组 $\mathcal{A} = (\pi_\theta, \mathcal{M}, \mathcal{R}, \mathcal{W})$，其中 $\pi_\theta$ 是策略（LLM），$\mathcal{M}$ 是记忆存储，$\mathcal{R}: \mathcal{Q} \times \mathcal{M} \to \mathcal{D}$ 是将查询映射到检索文档的检索函数，$\mathcal{W}: \mathcal{M} \times \mathcal{E} \to \mathcal{M}$ 是用新经验 $\mathcal{E}$ 更新记忆的写入函数。在每个时间步 $t$，代理观察到 $o_t$，检索相关上下文 $c_t = \mathcal{R}(o_t, \mathcal{M})$，然后采取行动：
\[
a_t \sim \pi_\theta\!\left(\cdot \;\middle|\; [s_t;\, c_t;\, h_t]\right),
\]
其中 $s_t$ 是当前系统提示，$c_t$ 是检索到的记忆，$h_t$ 是最近的上下文内历史。行动后，代理可能会写入新信息：$\mathcal{M} \leftarrow \mathcal{W}(\mathcal{M},\, (o_t, a_t, r_t))$。

\section{Taxonomy of Memory Types}
\label{sec:memory-taxonomy}
\section{记忆类型分类}
\label{sec:memory-taxonomy}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_052_memory-taxonomy.png}
\caption{Four-way taxonomy of agentic memory systems, mirroring cognitive science distinctions. Each memory type has distinct access patterns, update frequencies, and retrieval mechanisms.}
\label{fig:memory-taxonomy}
\end{figure}
\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_052_memory-taxonomy.png}
\caption{代理记忆系统的四路分类，反映了认知科学的区分。每种记忆类型都有不同的访问模式、更新频率和检索机制。}
\label{fig:memory-taxonomy}
\end{figure}

\subsection{Working Memory (Short-Term)}
\label{working-memory-short-term}
\subsection{工作记忆（短期）}
\label{working-memory-short-term}

Working memory is the agent’s \emph{active workspace}: the information currently being manipulated. In LLM agents it corresponds to:

工作记忆是代理的\emph{活动工作空间}：当前正在处理的信息。在LLM代理中，它对应于：

\begin{itemize}
  \item \textbf{Scratchpads.} Intermediate reasoning steps written to a dedicated buffer before producing a final answer (e.g.~chain-of-thought~\cite{wei2022chain}, scratchpad~\cite{nye2021show}).
  \item \textbf{Chain-of-thought buffers.} The sequence of reasoning tokens $z_1, z_2, \ldots, z_k$ generated before the answer token $a$, modeled as $p(a \mid x) = \sum_z p(a \mid x, z)\,p(z \mid x)$.
  \item \textbf{Conversation context.} The recent turn history $[(u_1, a_1), \ldots, (u_t, a_t)]$ kept in the context window.
\end{itemize}
\begin{itemize}
  \item \textbf{草稿本。}在生成最终答案之前写入专用缓冲区的中间推理步骤（例如，思维链~\cite{wei2022chain}、草稿本~\cite{nye2021show}）。
  \item \textbf{思维链缓冲区。}在答案 token $a$ 之前生成的推理 token 序列 $z_1, z_2, \ldots, z_k$，建模为 $p(a \mid x) = \sum_z p(a \mid x, z)\,p(z \mid x)$。
  \item \textbf{对话上下文。}保持在上下文窗口中的最近轮次历史 $[(u_1, a_1), \ldots, (u_t, a_t)]$。
\end{itemize}

Working memory is \emph{fast} (zero retrieval latency---it is already in context), \emph{volatile} (lost when the context is cleared), and \emph{capacity-limited} (bounded by $L$).

工作记忆是\emph{快速的}（零检索延迟——它已经在上下文中）、\emph{易失的}（清除上下文时丢失）和\emph{容量受限的}（受 $L$ 限制）。

\subsection{Episodic Memory (Experience-Based)}
\label{episodic-memory-experience-based}
\subsection{情景记忆（基于经验）}
\label{episodic-memory-experience-based}

Episodic memory stores \emph{specific past events} indexed by context and time. For agents:

情景记忆存储由上下文和时间索引的\emph{特定过去事件}。对于代理：

\begin{itemize}
  \item \textbf{Past interactions.} Full or summarized records of prior conversations, task attempts, and their outcomes.
  \item \textbf{Successful trajectories.} High-reward action sequences that can be retrieved as few-shot exemplars for similar future tasks.
  \item \textbf{Failure cases.} Documented mistakes with root-cause annotations, enabling the agent to avoid repeating errors.
  \item \textbf{Retrieval-augmented episodic recall.} Given a new task $q$, retrieve the $k$ most similar past episodes $\{e_i\}_{i=1}^k$ and include them in context.
\end{itemize}
\begin{itemize}
  \item \textbf{过去的交互。}先前对话、任务尝试及其结果的完整或摘要记录。
  \item \textbf{成功的轨迹。}高奖励动作序列，可以作为未来类似任务的少样本示例进行检索。
  \item \textbf{失败案例。}带有根本原因注释的记录错误，使代理能够避免重复错误。
  \item \textbf{检索增强的情景回忆。}给定新任务 $q$，检索最相似的 $k$ 个过去情景 $\{e_i\}_{i=1}^k$ 并将其包含在上下文中。
\end{itemize}

Episodic memory is typically implemented as a vector store (Section~\ref{sec:rag-memory}) with embeddings over episode summaries.

情景记忆通常实现为向量存储（第~\ref{sec:rag-memory}节），其中包含对情景摘要的嵌入。

\subsection{Semantic Memory (World Knowledge)}
\label{semantic-memory-world-knowledge}
\subsection{语义记忆（世界知识）}
\label{semantic-memory-world-knowledge}

Semantic memory encodes \emph{general facts and concepts} decoupled from specific episodes:

语义记忆编码与特定情景解耦的\emph{一般事实和概念}：

\begin{itemize}
  \item \textbf{Factual knowledge.} Entities, attributes, and relationships (e.g.~``Paris is the capital of France'').
  \item \textbf{Domain concepts.} Definitions, taxonomies, and ontologies relevant to the agent’s task domain.
  \item \textbf{Knowledge graphs.} Structured representations $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ where nodes $v \in \mathcal{V}$ are entities and edges $e \in \mathcal{E}$ are typed relations.
\end{itemize}
\begin{itemize}
  \item \textbf{事实知识。}实体、属性和关系（例如，“巴黎是法国的首都”）。
  \item \textbf{领域概念。}与代理任务领域相关的定义、分类法和本体。
  \item \textbf{知识图谱。}结构化表示 $\mathcal{G} = (\mathcal{V}, \mathcal{E})$，其中节点 $v \in \mathcal{V}$ 是实体，边 $e \in \mathcal{E}$ 是类型化关系。
\end{itemize}

Unlike episodic memory, semantic memory is \emph{context-independent}: the fact that water boils at $100^\circ$C is true regardless of when or where it was learned.

与情景记忆不同，语义记忆是\emph{上下文无关的}：水在 $100^\circ$C 沸腾这一事实无论何时何地学到都是正确的。

\subsection{Procedural Memory (Skills)}
\label{procedural-memory-skills}
\subsection{程序性记忆（技能）}
\label{procedural-memory-skills}

Procedural memory encodes \emph{how to do things}---skills and action patterns that have been automatized:

程序性记忆编码\emph{如何做事情}——已自动化的技能和动作模式：

\begin{itemize}
  \item \textbf{Learned tool-use patterns.} Which API to call for which task, how to format inputs, how to handle errors.
  \item \textbf{Action sequences.} Multi-step procedures (e.g.~``to deploy code: run tests $\to$ build image $\to$ push $\to$ update manifest'').
  \item \textbf{Policies as memory.} The model weights $\theta$ themselves encode procedural knowledge; fine-tuning on successful trajectories is a form of procedural memory consolidation.
\end{itemize}
\begin{itemize}
  \item \textbf{学到的工具使用模式。}为哪个任务调用哪个API，如何格式化输入，如何处理错误。
  \item \textbf{动作序列。}多步程序（例如，“部署代码：运行测试 $\to$ 构建镜像 $\to$ 推送 $\to$ 更新清单”）。
  \item \textbf{作为记忆的策略。}模型权重 $\theta$ 本身编码了程序性知识；在成功轨迹上进行微调是程序性记忆巩固的一种形式。
\end{itemize}

\begin{examplebox}[Memory Type Classification]
An agent helping with software development uses:

\begin{examplebox}[记忆类型分类]
一个帮助软件开发的代理使用：

\begin{itemize}
  \item \textbf{Working}: the current file being edited, the error message just received.
  \item \textbf{Episodic}: ``Last week I fixed a similar \texttt{NullPointerException} in module X by adding a null check at line 42.''
  \item \textbf{Semantic}: ``Python’s \texttt{asyncio.gather} runs coroutines concurrently; exceptions propagate unless \texttt{return\_exceptions=True}.''
  \item \textbf{Procedural}: the standard debugging workflow: reproduce $\to$ isolate $\to$ hypothesize $\to$ test $\to$ fix.
\end{itemize}
\end{examplebox}
\begin{itemize}
  \item \textbf{工作记忆}：当前正在编辑的文件，刚刚收到的错误消息。
  \item \textbf{情景记忆}：“上周我通过在模块X的第42行添加空值检查修复了一个类似的 \texttt{NullPointerException}。”
  \item \textbf{语义记忆}：“Python的 \texttt{asyncio.gather} 并发运行协程；除非设置 \texttt{return\_exceptions=True}，否则异常会传播。”
  \item \textbf{程序性记忆}：标准调试工作流程：重现 $\to$ 隔离 $\to$ 假设 $\to$ 测试 $\to$ 修复。
\end{itemize}
\end{examplebox}

\section{Memory Architectures}
\label{sec:memory-architectures}
\section{记忆架构}
\label{sec:memory-architectures}

\subsection{RAG-Based Memory}
\label{sec:rag-memory}
\subsection{基于RAG的记忆}
\label{sec:rag-memory}
```

## Section Title
## 章节标题

## Motivation: Why Agents Need Memory
## 动机：为什么智能体需要记忆

Retrieval-Augmented Generation (RAG)~\cite{lewis2020retrieval} is the dominant paradigm for external memory in LLM agents. The memory store $\mathcal{M}$ is a collection of documents $\{d_i\}_{i=1}^N$; retrieval maps a query $q$ to a ranked subset.
检索增强生成（RAG）~\cite{lewis2020retrieval} 是 LLM 智能体中外存的主流范式。记忆存储 $\mathcal{M}$ 是文档集合 $\{d_i\}_{i=1}^N$；检索将查询 $q$ 映射到排序后的子集。

\paragraph{Embedding Stores and Vector Databases.}
\label{embedding-stores-and-vector-databases.}
\paragraph{嵌入存储与向量数据库。}
\label{embedding-stores-and-vector-databases.}

Each document $d_i$ is encoded by an embedding model $\phi$: $\mathbf{v}_i = \phi(d_i) \in \mathbb{R}^{D}$. Queries are similarly encoded: $\mathbf{q} = \phi(q)$. Retrieval returns the top-$k$ documents by similarity: 
\[
\text{Retrieve}(q, \mathcal{M}, k) = \underset{S \subseteq [N],\, |S|=k}{\arg\max} \sum_{i \in S} \text{sim}(\mathbf{q}, \mathbf{v}_i),
\]
 where $\text{sim}(\cdot,\cdot)$ is typically cosine similarity. Approximate nearest-neighbor (ANN) indices (FAISS~\cite{johnson2019billion}, HNSW~\cite{malkov2018efficient}, ScaNN~\cite{guo2020scann}) make this tractable for $N \sim 10^7$.
每个文档 $d_i$ 由嵌入模型 $\phi$ 编码：$\mathbf{v}_i = \phi(d_i) \in \mathbb{R}^{D}$。查询也被类似编码：$\mathbf{q} = \phi(q)$。检索返回按相似度排序的前 $k$ 个文档：
\[
\text{Retrieve}(q, \mathcal{M}, k) = \underset{S \subseteq [N],\, |S|=k}{\arg\max} \sum_{i \in S} \text{sim}(\mathbf{q}, \mathbf{v}_i),
\]
其中 $\text{sim}(\cdot,\cdot)$ 通常是余弦相似度。近似最近邻（ANN）索引（FAISS~\cite{johnson2019billion}、HNSW~\cite{malkov2018efficient}、ScaNN~\cite{guo2020scann}）使得在 $N \sim 10^7$ 规模下可行。

\paragraph{Retrieval Strategies.}
\label{retrieval-strategies.}
\paragraph{检索策略。}
\label{retrieval-strategies.}

\begin{itemize}
  \item \textbf{Dense retrieval.} Both query and documents are encoded by neural encoders (e.g.~DPR~\cite{karpukhin2020dense}, \texttt{text-embedding-3-large}). Captures semantic similarity but requires GPU inference.
  \item \textbf{Sparse retrieval.} BM25 or TF-IDF over token overlap. Fast, interpretable, strong for exact keyword matches.
  \item \textbf{Hybrid retrieval.} Combine dense and sparse scores via reciprocal rank fusion (RRF): 
\[
\text{RRF}(d, k) = \sum_{r \in \text{rankers}} \frac{1}{k + \text{rank}_r(d)},
\]
 where $k=60$ is a smoothing constant. Hybrid consistently outperforms either alone~\cite{chen2022hybrid}.
\end{itemize}
\begin{itemize}
  \item \textbf{稠密检索（Dense retrieval）。} 查询和文档均由神经编码器编码（例如 DPR~\cite{karpukhin2020dense}、\texttt{text-embedding-3-large}）。捕获语义相似性，但需要 GPU 推理。
  \item \textbf{稀疏检索（Sparse retrieval）。} 基于词重叠的 BM25 或 TF-IDF。快速、可解释，在精确关键词匹配方面表现强劲。
  \item \textbf{混合检索（Hybrid retrieval）。} 通过倒数排名融合（RRF）结合稠密和稀疏得分：
\[
\text{RRF}(d, k) = \sum_{r \in \text{rankers}} \frac{1}{k + \text{rank}_r(d)},
\]
其中 $k=60$ 是平滑常数。混合方法始终优于单独任何一种~\cite{chen2022hybrid}。
\end{itemize}

\paragraph{Re-ranking.}
\label{re-ranking.}
\paragraph{重排序（Re-ranking）。}
\label{re-ranking.}

A cross-encoder re-ranker $f_\psi(q, d) \in [0,1]$ scores each retrieved document jointly with the query, providing higher accuracy at the cost of $O(k)$ forward passes. The pipeline is: retrieve $k' \gg k$ candidates with ANN, re-rank with cross-encoder, return top $k$.
交叉编码器重排序器 $f_\psi(q, d) \in [0,1]$ 联合查询对每个检索到的文档进行评分，以 $O(k)$ 次前向传播的代价提供更高精度。流程为：用 ANN 检索 $k' \gg k$ 个候选，用交叉编码器重排序，返回前 $k$ 个。

\begin{warningbox}[Retrieval Hallucination Risk]
RAG does not eliminate hallucination---it can \emph{introduce} it. If the retrieved document is outdated, incorrect, or only superficially relevant, the model may confidently incorporate false information. Always include provenance metadata (source, timestamp, confidence) and consider faithfulness verification steps.
\end{warningbox}
\begin{warningbox}[检索幻觉风险（Retrieval Hallucination Risk）]
RAG 并不会消除幻觉——它反而可能\emph{引入}幻觉。如果检索到的文档过时、错误或仅表面相关，模型可能会自信地融入虚假信息。始终包含来源元数据（来源、时间戳、置信度），并考虑忠实度验证步骤。
\end{warningbox}

\subsection{Summarization-Based Memory}
\label{summarization-based-memory}
\subsection{基于摘要的记忆（Summarization-Based Memory）}
\label{summarization-based-memory}

When verbatim storage is too expensive or noisy, \emph{summarization} compresses information before storage.
当逐字存储成本过高或噪声过大时，\emph{摘要（summarization）}在存储前对信息进行压缩。

\paragraph{Progressive Summarization.}
\label{progressive-summarization.}
\paragraph{渐进式摘要（Progressive Summarization）。}
\label{progressive-summarization.}

At each step $t$, the agent maintains a running summary $S_t$. When new information $e_t$ arrives: 
\[
S_{t+1} = \text{LLM}\!\left(\texttt{``Summarize: [}S_t\texttt{] + [}e_t\texttt{]''}\right).
\]
 This keeps memory size $O(1)$ but risks losing detail.
在每个时间步 $t$，智能体维护一个运行摘要 $S_t$。当新信息 $e_t$ 到来时：
\[
S_{t+1} = \text{LLM}\!\left(\texttt{``Summarize: [}S_t\texttt{] + [}e_t\texttt{]''}\right).
\]
这使记忆规模保持在 $O(1)$，但有丢失细节的风险。

\paragraph{Hierarchical Compression.}
\label{hierarchical-compression.}
\paragraph{分层压缩（Hierarchical Compression）。}
\label{hierarchical-compression.}

Organize memory in levels $L_0 \supset L_1 \supset \cdots \supset L_K$ where $L_0$ is verbatim and each $L_{i+1}$ is a summary of $L_i$. Retrieval first checks $L_K$ (most compressed, fastest) and drills down as needed. This mirrors the \emph{progressive summarization} technique of Forte~\cite{forte2022building}.
将记忆组织为层级 $L_0 \supset L_1 \supset \cdots \supset L_K$，其中 $L_0$ 是逐字记录，每个 $L_{i+1}$ 是 $L_i$ 的摘要。检索首先检查 $L_K$（最压缩、最快），然后根据需要深入。这反映了 Forte~\cite{forte2022building} 的\emph{渐进式摘要}技术。

\paragraph{When to Summarize vs.~Store Verbatim.}
\label{when-to-summarize-vs.-store-verbatim.}
\paragraph{何时摘要 vs. 逐字存储。}
\label{when-to-summarize-vs.-store-verbatim.}

\begin{itemize}
  \item Store verbatim: precise facts, code snippets, numerical results, user quotes.
  \item Summarize: narrative context, reasoning chains, redundant observations.
  \item Discard: noise, failed tool calls with no informational content.
\end{itemize}
\begin{itemize}
  \item 逐字存储：精确事实、代码片段、数值结果、用户引用。
  \item 摘要存储：叙事上下文、推理链、冗余观察。
  \item 丢弃：噪声、无信息内容的失败工具调用。
\end{itemize}

\subsection{Graph-Based Memory}
\label{graph-based-memory}
\subsection{基于图的记忆（Graph-Based Memory）}
\label{graph-based-memory}

\paragraph{Knowledge Graphs.}
\label{knowledge-graphs.}
\paragraph{知识图谱（Knowledge Graphs）。}
\label{knowledge-graphs.}

A knowledge graph $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{R})$ stores facts as triples $(h, r, t)$ where $h, t \in \mathcal{V}$ are entities and $r \in \mathcal{R}$ is a relation. Agents can query via SPARQL~\cite{harris2013sparql}, Cypher~\cite{francis2018cypher}, or natural-language-to-graph translation.
知识图谱 $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{R})$ 将事实存储为三元组 $(h, r, t)$，其中 $h, t \in \mathcal{V}$ 是实体，$r \in \mathcal{R}$ 是关系。智能体可以通过 SPARQL~\cite{harris2013sparql}、Cypher~\cite{francis2018cypher} 或自然语言到图谱的翻译进行查询。

\paragraph{Entity-Relation Extraction.}
\label{entity-relation-extraction.}
\paragraph{实体关系抽取（Entity-Relation Extraction）。}
\label{entity-relation-extraction.}

New observations are parsed by an extraction model $\text{IE}: \text{text} \to \{(h_i, r_i, t_i)\}$ and merged into $\mathcal{G}$. Coreference resolution and entity linking ensure consistency.
新观察结果由抽取模型 $\text{IE}: \text{text} \to \{(h_i, r_i, t_i)\}$ 解析并合并到 $\mathcal{G}$ 中。共指消解和实体链接确保一致性。

\paragraph{GraphRAG.}
\label{graphrag.}
\paragraph{GraphRAG（GraphRAG）。}
\label{graphrag.}

GraphRAG~\cite{edge2024local} augments RAG with graph traversal: given a query, retrieve seed entities, then expand via $k$-hop neighborhood traversal to surface related facts not directly matched by embedding similarity. This is particularly powerful for multi-hop reasoning: 
\[
\text{GraphRetrieve}(q, \mathcal{G}, k) = \bigcup_{v \in \text{seeds}(q)} \mathcal{N}_k(v, \mathcal{G}),
\]
 where $\mathcal{N}_k(v, \mathcal{G})$ is the $k$-hop neighborhood of $v$.
GraphRAG~\cite{edge2024local} 通过图遍历增强 RAG：给定查询，检索种子实体，然后通过 $k$ 跳邻域遍历扩展，以揭示嵌入相似性未直接匹配的相关事实。这对于多跳推理特别有效：
\[
\text{GraphRetrieve}(q, \mathcal{G}, k) = \bigcup_{v \in \text{seeds}(q)} \mathcal{N}_k(v, \mathcal{G}),
\]
其中 $\mathcal{N}_k(v, \mathcal{G})$ 是 $v$ 的 $k$ 跳邻域。

\paragraph{Temporal Knowledge Graphs.}
\label{temporal-knowledge-graphs.}
\paragraph{时态知识图谱（Temporal Knowledge Graphs）。}
\label{temporal-knowledge-graphs.}

Facts have validity intervals: $(h, r, t, [t_\text{start}, t_\text{end}])$. Temporal KGs~\cite{lacroix2020tensor} enable queries like ``Who was the CEO of OpenAI in 2023?'' without conflating past and present states.
事实具有有效区间：$(h, r, t, [t_\text{start}, t_\text{end}])$。时态知识图谱~\cite{lacroix2020tensor} 支持诸如“2023 年 OpenAI 的 CEO 是谁？”的查询，而不会混淆过去和现在的状态。

\subsection{Key-Value Memory Networks}
\label{key-value-memory-networks}
\subsection{键值记忆网络（Key-Value Memory Networks）}
\label{key-value-memory-networks}

Differentiable memory networks~\cite{weston2014memory, sukhbaatar2015end} represent memory as a set of key-value pairs $\{(\mathbf{k}_i, \mathbf{v}_i)\}_{i=1}^M$ with soft attention-based retrieval: 
\[
\alpha_i = \text{softmax}\!\left(\frac{\mathbf{q}^\top \mathbf{k}_i}{\sqrt{D}}\right), \qquad
  \mathbf{c} = \sum_{i=1}^M \alpha_i \mathbf{v}_i.
\]
 The retrieved context $\mathbf{c}$ is a differentiable function of the query, enabling end-to-end training. Modern transformer attention is a special case of this mechanism. For agentic use, memory slots can be updated via gradient descent or via explicit write operations.
可微分记忆网络~\cite{weston2014memory, sukhbaatar2015end} 将记忆表示为一组键值对 $\{(\mathbf{k}_i, \mathbf{v}_i)\}_{i=1}^M$，并采用基于软注意力的检索：
\[
\alpha_i = \text{softmax}\!\left(\frac{\mathbf{q}^\top \mathbf{k}_i}{\sqrt{D}}\right), \qquad
  \mathbf{c} = \sum_{i=1}^M \alpha_i \mathbf{v}_i.
\]
检索到的上下文 $\mathbf{c}$ 是查询的可微函数，支持端到端训练。现代 Transformer 注意力是这种机制的特例。对于智能体应用，记忆槽可以通过梯度下降或显式写入操作来更新。

\subsection{MemGPT and Virtual Context Management}
\label{sec:memgpt}
\subsection{MemGPT 与虚拟上下文管理（MemGPT and Virtual Context Management）}
\label{sec:memgpt}

MemGPT~\cite{packer2023memgpt} introduces a \emph{virtual context} abstraction analogous to virtual memory in operating systems. Memory is organized in tiers:
MemGPT~\cite{packer2023memgpt} 引入了\emph{虚拟上下文（virtual context）}抽象，类似于操作系统中的虚拟内存。记忆按层级组织：

\paragraph{Page-In / Page-Out Strategies.}
\label{page-in-page-out-strategies.}
\paragraph{换入/换出策略（Page-In / Page-Out Strategies）。}
\label{page-in-page-out-strategies.}

The agent decides \emph{which} memory to promote to hot context (page-in) and \emph{which} to evict (page-out) based on:
智能体根据以下因素决定\emph{将哪些}记忆提升到热上下文（换入）以及\emph{将哪些}驱逐（换出）：

\begin{itemize}
  \item \textbf{Recency:} recently accessed items are more likely to be needed.
  \item \textbf{Relevance:} items with high similarity to the current query.
  \item \textbf{Importance:} items tagged as high-importance during write.
\end{itemize}
\begin{itemize}
  \item \textbf{近期性（Recency）：} 最近访问的项目更可能被需要。
  \item \textbf{相关性（Relevance）：} 与当前查询相似度高的项目。
  \item \textbf{重要性（Importance）：} 写入时标记为高重要性的项目。
\end{itemize}

\paragraph{Self-Directed Memory Management.}
\label{self-directed-memory-management.}
\paragraph{自主记忆管理（Self-Directed Memory Management）。}
\label{self-directed-memory-management.}

In MemGPT, the LLM itself issues memory management function calls (\texttt{memory\_search}, \texttt{memory\_insert}, \texttt{memory\_delete}) as part of its action space. This makes memory management a \emph{learned behavior} rather than a hard-coded policy---a natural target for RL training (Section~\ref{sec:rl-memory}).
在 MemGPT 中，LLM 自身发出记忆管理函数调用（\texttt{memory\_search}、\texttt{memory\_insert}、\texttt{memory\_delete}）作为其动作空间的一部分。这使得记忆管理成为一种\emph{习得行为}而非硬编码策略——这是 RL 训练的自然目标（第~\ref{sec:rl-memory}节）。

\section{Memory Operations}
\label{sec:memory-operations}
\section{记忆操作（Memory Operations）}
\label{sec:memory-operations}

\subsection{Write: Committing to Memory}
\label{write-committing-to-memory}
\subsection{写入：提交到记忆（Write: Committing to Memory）}
\label{write-committing-to-memory}

Not every observation should be stored. The write decision is a filtering problem: 
\[
\text{Write}(e) = \mathbf{1}\!\left[\text{importance}(e) > \tau\right],
\]
 where $\tau$ is a threshold and $\text{importance}(e)$ can be:
并非所有观察结果都应存储。写入决策是一个过滤问题：
\[
\text{Write}(e) = \mathbf{1}\!\left[\text{importance}(e) > \tau\right],
\]
其中 $\tau$ 是阈值，而 $\text{importance}(e)$ 可以是：

\begin{itemize}
  \item \textbf{Surprise:} $-\log p_\theta(e \mid \text{context})$---unexpected events are more informative.
  \item \textbf{Reward signal:} events associated with high $|r_t|$ (positive or negative) are worth remembering.
  \item \textbf{LLM self-assessment:} prompt the model to rate importance on a 1--10 scale.
\end{itemize}
\begin{itemize}
  \item \textbf{意外度（Surprise）：} $-\log p_\theta(e \mid \text{context})$——意外事件信息量更大。
  \item \textbf{奖励信号（Reward signal）：} 与高 $|r_t|$（正或负）相关的事件值得记忆。
  \item \textbf{LLM 自评估（LLM self-assessment）：} 提示模型以 1-10 分制评估重要性。
\end{itemize}

\paragraph{Contradiction Detection.}
\label{contradiction-detection.}
\paragraph{矛盾检测（Contradiction Detection）。}
\label{contradiction-detection.}

## Motivation: Why Agents Need Memory
## 动机：为什么智能体需要记忆

Before writing a new fact $f_\text{new}$, check for conflicts with existing memory: 
\[
\text{Conflict}(f_\text{new}, \mathcal{M}) = \exists\, f \in \mathcal{M} : \text{Contradicts}(f_\text{new}, f).
\]
在写入新事实 $f_\text{new}$ 之前，检查与现有记忆的冲突：
\[
\text{Conflict}(f_\text{new}, \mathcal{M}) = \exists\, f \in \mathcal{M} : \text{Contradicts}(f_\text{new}, f).
\]

Contradiction detection can be implemented via NLI models or by prompting the LLM. On conflict, the agent must decide: overwrite, keep both with timestamps, or flag for human review.
矛盾检测可以通过自然语言推理（NLI）模型或通过提示大语言模型（LLM）来实现。当发生冲突时，智能体必须决定：覆盖、保留两者并附带时间戳，或标记为人工审查。

\paragraph{Memory Format and Granularity.}
\label{memory-format-and-granularity.}
\paragraph{记忆格式与粒度。}
\label{memory-format-and-granularity.}

Beyond \emph{what} to store, the \emph{how} matters greatly. Memory entries range from atomic facts to verbose transcripts, with distinct trade-offs:
除了\emph{存储什么}之外，\emph{如何存储}也至关重要。记忆条目从原子事实到冗长转录稿不等，各有不同的权衡：

\begin{table}[ht!]
\centering
\caption{Memory granularity trade-offs.}
\caption{记忆粒度权衡。}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Format} & \textbf{Pros} & \textbf{Cons} \\
\textbf{格式} & \textbf{优点} & \textbf{缺点} \\
\midrule
\textbf{Atomic facts}\\
\textbf{原子事实}\\
``User prefers Python.'' & Precise retrieval; composable; easy deduplication and contradiction detection & Loses context; extraction errors; brittle for nuanced information\\
``用户偏好Python。'' & 精确检索；可组合；易于去重和矛盾检测 & 丢失上下文；提取错误；对细微信息脆弱\\
\textbf{Structured notes}\\
\textbf{结构化笔记}\\
(A-MEM~\cite{xu2025amem}) & Rich metadata (tags, links); supports graph traversal; balances precision and context & Higher write cost; schema design required\\
(A-MEM~\cite{xu2025amem}) & 丰富的元数据（标签、链接）；支持图遍历；平衡精度与上下文 & 写入成本较高；需要模式设计\\
\textbf{Summarized episodes}\\
\textbf{总结性情节}\\
(MemGPT~\cite{packer2023memgpt}) & Preserves narrative coherence; compact; good for multi-turn reasoning & Summarization lossy; hard to update partially\\
(MemGPT~\cite{packer2023memgpt}) & 保留叙述连贯性；紧凑；适合多轮推理 & 总结有损；难以部分更新\\
\textbf{Verbatim transcripts} & Lossless; no extraction errors; supports exact quotation & Large storage; noisy retrieval; expensive to scan\\
\textbf{逐字转录} & 无损；无提取错误；支持精确引用 & 存储量大；检索噪声高；扫描成本高\\
\bottomrule
\end{tabular}
\end{table}

In practice, production systems often combine granularities~\cite{chhikara2025mem0}: extract atomic facts for precise recall, maintain summarized episodes for narrative context, and archive verbatim transcripts in cold storage for auditability. The Generative Agents architecture~\cite{park2023generative} stores observations as atomic ``memory objects'' with natural-language descriptions, importance scores, and timestamps---enabling both precise retrieval and temporal reasoning.
在实践中，生产系统通常结合多种粒度~\cite{chhikara2025mem0}：提取原子事实用于精确召回，维护总结性情节用于叙事上下文，并将逐字转录归档到冷存储中以供审计。生成式智能体架构~\cite{park2023generative}将观察结果存储为原子“记忆对象”，包含自然语言描述、重要性分数和时间戳——从而支持精确检索和时序推理。

\paragraph{Design Guidelines.}
\label{design-guidelines.}
\paragraph{设计指南。}
\label{design-guidelines.}

\begin{itemize}
  \item \textbf{Match granularity to query type.} If users ask factoid questions (``What’s my API key?''), atomic facts win. If they ask contextual questions (``Why did we decide to use Redis?''), episode summaries are needed.
  \item \textbf{将粒度与查询类型匹配。} 如果用户问事实类问题（“我的API密钥是什么？”），原子事实胜出。如果问上下文类问题（“我们为什么决定使用Redis？”），则需要情节总结。
  \item \textbf{Store at the finest grain you can afford}, then build coarser views on top. It is easy to summarize atomic facts; it is impossible to recover atoms from a lossy summary.
  \item \textbf{以你能承受的最细粒度存储}，然后在其上构建更粗粒度的视图。对原子事实进行总结很容易；但从有损总结中恢复原子是不可能。
  \item \textbf{Include provenance.} Every memory entry should link back to its source (conversation turn, document, tool output) so the agent can verify and the user can audit.
  \item \textbf{包含来源。} 每条记忆条目都应链接回其来源（对话轮次、文档、工具输出），以便智能体能验证，用户能审计。
\end{itemize}

\subsection{Read / Retrieve}
\label{read-retrieve}
\subsection{读取/检索}
\label{read-retrieve}

\paragraph{Query Formulation.}
\label{query-formulation.}
\paragraph{查询构建。}
\label{query-formulation.}

The retrieval query $q$ need not be the raw observation. Better strategies:
检索查询 $q$ 不必是原始观察。更好的策略：

\begin{itemize}
  \item \textbf{HyDE (Hypothetical Document Embeddings)~\cite{gao2022precise}:} generate a hypothetical answer, embed it, and use that embedding as the query.
  \item \textbf{HyDE（假设文档嵌入）~\cite{gao2022precise}：} 生成一个假设答案，对其进行嵌入，然后将该嵌入作为查询。
  \item \textbf{Query expansion:} generate multiple paraphrases of the query and take the union of retrieved results.
  \item \textbf{查询扩展：} 生成查询的多个改写版本，并取检索结果的并集。
  \item \textbf{Step-back prompting:} abstract the specific query to a more general question before retrieval.
  \item \textbf{后退提示：} 在检索前将具体查询抽象为一个更通用的问题。
\end{itemize}

\paragraph{Temporal Decay and Recency Bias.}
\label{temporal-decay-and-recency-bias.}
\paragraph{时间衰减与近因偏差。}
\label{temporal-decay-and-recency-bias.}

Older memories may be less relevant. A time-weighted score: 
\[
\text{score}(d, q, t) = \lambda \cdot \text{sim}(\mathbf{q}, \mathbf{v}_d) + (1-\lambda) \cdot \exp\!\left(-\frac{t - t_d}{\tau_\text{decay}}\right),
\]
 where $t_d$ is the memory’s creation time and $\tau_\text{decay}$ controls the decay rate. The Generative Agents paper~\cite{park2023generative} uses a similar recency-weighted retrieval.
较早的记忆可能相关性较低。一个时间加权得分：
\[
\text{score}(d, q, t) = \lambda \cdot \text{sim}(\mathbf{q}, \mathbf{v}_d) + (1-\lambda) \cdot \exp\!\left(-\frac{t - t_d}{\tau_\text{decay}}\right),
\]
其中 $t_d$ 是记忆的创建时间，$\tau_\text{decay}$ 控制衰减率。生成式智能体论文~\cite{park2023generative}使用了类似的近因加权检索。

\subsection{Update: Conflict Resolution and Consolidation}
\label{update-conflict-resolution-and-consolidation}
\subsection{更新：冲突解决与整合}
\label{update-conflict-resolution-and-consolidation}

Memory consolidation merges related memories to reduce redundancy and surface higher-level patterns: 
\[
\mathcal{M}' = \text{Consolidate}(\mathcal{M}) = \text{Cluster}(\mathcal{M}) \cup \text{Summarize}(\text{Cluster}(\mathcal{M})).
\]
记忆整合将相关记忆合并以减少冗余并呈现高层模式：
\[
\mathcal{M}' = \text{Consolidate}(\mathcal{M}) = \text{Cluster}(\mathcal{M}) \cup \text{Summarize}(\text{Cluster}(\mathcal{M})).
\]

\paragraph{Forgetting Mechanisms.}
\label{forgetting-mechanisms.}
\paragraph{遗忘机制。}
\label{forgetting-mechanisms.}

Biological memory forgets; so should artificial memory. Strategies:
生物记忆会遗忘；人工记忆也应如此。策略：

\begin{itemize}
  \item \textbf{LRU eviction:} remove least-recently-used entries when capacity is exceeded.
  \item \textbf{最近最少使用（LRU）淘汰：} 当容量超限时，移除最近最少使用的条目。
  \item \textbf{Importance-weighted forgetting:} $p(\text{forget}\,|\,d) \propto \exp(-\text{importance}(d))$.
  \item \textbf{重要性加权遗忘：} $p(\text{forget}\,|\,d) \propto \exp(-\text{importance}(d))$.
  \item \textbf{Spaced repetition:} memories accessed repeatedly are retained longer, following the exponential forgetting curve~\cite{ebbinghaus1885memory}.
  \item \textbf{间隔重复：} 重复访问的记忆保留得更久，遵循指数遗忘曲线~\cite{ebbinghaus1885memory}。
\end{itemize}

\subsection{Reflect: Meta-Cognitive Operations}
\label{reflect-meta-cognitive-operations}
\subsection{反思：元认知操作}
\label{reflect-meta-cognitive-operations}

Reflection~\cite{park2023generative, shinn2023reflexion} is a higher-order memory operation: the agent reads its own memory and generates \emph{insights}: 
\[
\text{Reflect}(\mathcal{M}) \to \{i_1, i_2, \ldots\} \subset \mathcal{M}_\text{semantic},
\]
 where each insight $i_j$ is a higher-level abstraction derived from multiple episodic memories.
反思~\cite{park2023generative, shinn2023reflexion}是一种更高阶的记忆操作：智能体读取自己的记忆并生成\emph{洞察}：
\[
\text{Reflect}(\mathcal{M}) \to \{i_1, i_2, \ldots\} \subset \mathcal{M}_\text{semantic},
\]
其中每个洞察 $i_j$ 是从多个情景记忆推导出的高层抽象。

\begin{examplebox}[Reflection in Practice (Reflexion)]
After three failed attempts to solve a coding problem, the agent reflects:
\begin{examplebox}[实践中的反思（Reflexion）]
在解决一个编程问题失败三次后，智能体进行反思：

\begin{enumerate}
  \item Retrieves the three failure episodes from episodic memory.
  \item 从情景记忆中检索三次失败情节。
  \item Generates an insight: ``I keep forgetting to handle the edge case where the input list is empty.''
  \item 生成一个洞察：“我老是忘记处理输入列表为空时的边界情况。”
  \item Stores this insight in semantic memory.
  \item 将此洞察存储在语义记忆中。
  \item On the next attempt, retrieves the insight and explicitly checks for empty inputs.
  \item 在下一次尝试时，检索该洞察并显式检查空输入。
\end{enumerate}

This is the core mechanism of Reflexion~\cite{shinn2023reflexion}: verbal reinforcement learning via self-reflection.
这就是Reflexion~\cite{shinn2023reflexion}的核心机制：通过自我反思进行言语强化学习。
\end{examplebox}

\paragraph{Where Do Reflections Live?}
\label{where-do-reflections-live}
\paragraph{反思存储在哪里？}
\label{where-do-reflections-live}

Reflection \emph{reads} from episodic memory but \emph{writes} to semantic memory. The resulting insights are context-independent generalizations (``always check for empty inputs''), not episode-specific records---hence they belong in semantic memory $\mathcal{M}_\text{semantic}$. However, during the reflection process itself, the intermediate reasoning (retrieved episodes + synthesis prompt + generated insight) occupies \emph{working memory} (the context window). In short:
反思\emph{从}情景记忆\emph{读取}，但\emph{写入}语义记忆。生成的洞察是上下文无关的泛化（“总是检查空输入”），而非特定情节的记录——因此它们属于语义记忆 $\mathcal{M}_\text{semantic}$。然而，在反思过程本身中，中间推理（检索到的情节+合成提示+生成的洞察）占据\emph{工作记忆}（上下文窗口）。简而言之：

\begin{itemize}
  \item \textbf{Input}: episodic memory (specific past events)
  \item \textbf{输入}：情景记忆（特定的过往事件）
  \item \textbf{Computation}: working memory (active reasoning in context)
  \item \textbf{计算}：工作记忆（上下文中的主动推理）
  \item \textbf{Output}: semantic memory (durable, generalized insight)
  \item \textbf{输出}：语义记忆（持久、泛化的洞察）
\end{itemize}

This mirrors biological memory consolidation, where episodic experiences are gradually transformed into semantic knowledge during sleep and reflection.
这反映了生物记忆整合的过程，其中情景经历在睡眠和反思期间逐渐转化为语义知识。

\section{Memory for Multi-Turn Conversations}
\label{sec:memory-multiturn}
\section{多轮对话的记忆}
\label{sec:memory-multiturn}

\subsection{User Modeling and Preference Tracking}
\label{user-modeling-and-preference-tracking}
\subsection{用户建模与偏好追踪}
\label{user-modeling-and-preference-tracking}

A persistent user model $\mathcal{U}$ stores:
一个持久的用户模型 $\mathcal{U}$ 存储：

\begin{itemize}
  \item \textbf{Explicit preferences:} stated likes/dislikes, communication style preferences.
  \item \textbf{显式偏好：} 明确说明的喜好/厌恶、沟通风格偏好。
  \item \textbf{Implicit preferences:} inferred from behavior (e.g.~user always asks for code in Python, prefers concise answers).
  \item \textbf{隐式偏好：} 从行为推断（例如用户总是要求Python代码，偏好简洁答案）。
  \item \textbf{Expertise level:} domain knowledge inferred from vocabulary and question complexity.
  \item \textbf{专业水平：} 从词汇和问题复杂度推断的领域知识。
  \item \textbf{Goals and context:} ongoing projects, current tasks, organizational role.
  \item \textbf{目标与上下文：} 进行中的项目、当前任务、组织角色。
\end{itemize}

The user model is updated after each interaction: 
\[
\mathcal{U}_{t+1} = \text{Update}(\mathcal{U}_t,\, (u_t, a_t, \text{feedback}_t)).
\]
用户模型在每次交互后更新：
\[
\mathcal{U}_{t+1} = \text{Update}(\mathcal{U}_t,\, (u_t, a_t, \text{feedback}_t)).
\]

\subsection{Session Continuity}
\label{session-continuity}
\subsection{会话连续性}
\label{session-continuity}

Without memory, each conversation starts cold. With session memory:
没有记忆，每次对话都会冷启动。有了会话记忆：

\begin{enumerate}
  \item At session start, retrieve the user model $\mathcal{U}$ and recent session summaries.
  \item 在会话开始时，检索用户模型 $\mathcal{U}$ 和最近的会话摘要。
  \item Inject a personalized system prompt: ``You are helping Alice, a senior ML engineer working on a distributed training project. Last session you helped debug a gradient synchronization issue.''
  \item 注入个性化系统提示：``你正在帮助 Alice，一位从事分布式训练项目的高级机器学习工程师。上次会话你帮助调试了一个梯度同步问题。''
  \item At session end, summarize the session and update $\mathcal{U}$.
  \item 在会话结束时，总结本次会话并更新 $\mathcal{U}$。
\end{enumerate}

\subsection{Personalization Through Memory}
\subsection{通过内存实现个性化}
\label{personalization-through-memory}

Personalization improves both \emph{efficiency} (fewer clarifying questions) and \emph{quality} (responses calibrated to user expertise). Key techniques:
个性化既提高了\emph{效率}（减少澄清性问题）也提高了\emph{质量}（根据用户专业知识校准回答）。关键技术包括：

\begin{itemize}
  \item \textbf{Adaptive verbosity:} adjust response length based on user’s historical engagement.
  \item \textbf{自适应详细程度：}根据用户的历史参与度调整回复长度。
  \item \textbf{Domain priming:} prepend relevant domain context from semantic memory.
  \item \textbf{领域启动（Domain priming）：}从语义记忆中预置相关领域上下文。
  \item \textbf{Proactive recall:} surface relevant past interactions without being asked (``You asked about this topic last month; here’s what we found then'').
  \item \textbf{主动回忆（Proactive recall）：}无需用户询问即呈现相关历史互动（“你上个月问过这个话题；这是我们当时发现的内容”）。
\end{itemize}

\begin{warningbox}[Privacy and Memory]
Persistent user memory raises significant privacy concerns. Agents must: (1) obtain explicit consent before storing personal information, (2) provide mechanisms to inspect and delete stored memories, (3) enforce access controls in multi-user deployments, and (4) comply with data retention regulations (GDPR, CCPA). Memory systems should be designed with privacy-by-default.
\end{warningbox}
\begin{warningbox}[隐私与内存]
持久化的用户内存引发了重大的隐私问题。智能体必须：(1) 在存储个人信息前获得明确同意，(2) 提供检查和删除已存储内存的机制，(3) 在多用户部署中实施访问控制，(4) 遵守数据保留法规（GDPR、CCPA）。内存系统应设计为默认隐私保护。
\end{warningbox}

\section{Memory for Multi-Agent Systems}
\section{多智能体系统的内存}
\label{sec:memory-multiagent}

When multiple agents collaborate on a shared task, memory becomes a \emph{coordination mechanism}---not just a personal knowledge store. A planning agent that decomposes a task must communicate sub-goals to executor agents; a critic agent must access the same context as the agent it evaluates; a research team of agents must avoid duplicating work. Without shared memory, agents must communicate everything through direct messages, creating bandwidth bottlenecks and losing information when conversations scroll out of context. Shared memory solves this by providing a persistent, queryable substrate that all agents can read from and write to---turning implicit coordination (``I hope the other agent remembers'') into explicit state (``the answer is on the blackboard'').
当多个智能体协作完成一个共享任务时，内存成为一种\emph{协调机制}——而不仅仅是个人知识存储。一个分解任务的规划智能体必须将子目标传达给执行智能体；一个评审智能体必须访问与其评估的智能体相同的上下文；一个研究团队中的智能体必须避免重复工作。没有共享内存，智能体必须通过直接消息传递所有信息，这会造成带宽瓶颈，并且当对话滚动超出上下文时信息会丢失。共享内存通过提供一个持久化、可查询的基板来解决这个问题，所有智能体都可以读写该基板——将隐式协调（“我希望另一个智能体能记住”）转变为显式状态（“答案在黑板上”）。

\subsection{Shared Memory Pools}
\subsection{共享内存池}
\label{shared-memory-pools}

In multi-agent systems, agents may share a common memory store $\mathcal{M}_\text{shared}$ alongside private stores $\mathcal{M}_i$: 
\[
\text{context}_i(t) = \mathcal{R}(\mathcal{M}_i, q_i) \cup \mathcal{R}(\mathcal{M}_\text{shared}, q_i).
\]
 Shared memory enables \emph{implicit coordination}: agent $A$ writes a finding; agent $B$ retrieves it without explicit communication.
在多智能体系统中，智能体可能共享一个公共内存存储 $\mathcal{M}_\text{shared}$，同时拥有私有存储 $\mathcal{M}_i$：
\[
\text{context}_i(t) = \mathcal{R}(\mathcal{M}_i, q_i) \cup \mathcal{R}(\mathcal{M}_\text{shared}, q_i).
\]
共享内存实现了\emph{隐式协调}：智能体 $A$ 写入一个发现；智能体 $B$ 无需显式通信即可检索到它。

\subsection{Blackboard Architecture}
\subsection{黑板架构}
\label{blackboard-architecture}

The \emph{blackboard} pattern~\cite{hayes1985blackboard} is a classic multi-agent coordination mechanism:
\emph{黑板（Blackboard）}模式~\cite{hayes1985blackboard} 是一种经典的多智能体协调机制：

Each agent reads from and writes to the blackboard. A \emph{controller} monitors the blackboard and activates agents when their preconditions are met. This decouples agents: they communicate through shared state rather than direct messaging.
每个智能体都从黑板上读写。一个\emph{控制器}监视黑板，并在满足智能体的前置条件时激活它们。这使得智能体解耦：它们通过共享状态而非直接消息进行通信。

\subsection{Consensus and Conflict in Shared Knowledge}
\subsection{共享知识中的共识与冲突}
\label{consensus-and-conflict-in-shared-knowledge}

When multiple agents write to shared memory, conflicts arise. Resolution strategies:
当多个智能体写入共享内存时，冲突就会产生。解决策略包括：

\begin{itemize}
  \item \textbf{Last-write-wins:} simple but loses information.
  \item \textbf{最后写入者胜出（Last-write-wins）：}简单但会丢失信息。
  \item \textbf{Versioned memory:} maintain a history of all writes; agents can query any version.
  \item \textbf{版本化内存（Versioned memory）：}维护所有写入的历史记录；智能体可以查询任何版本。
  \item \textbf{Voting / consensus:} require $k$-of-$n$ agents to agree before a fact is committed.
  \item \textbf{投票/共识（Voting/consensus）：}要求 $n$ 个智能体中的 $k$ 个同意后才提交事实。
  \item \textbf{Confidence-weighted merging:} $f_\text{merged} = \sum_i w_i f_i$ where $w_i$ is agent $i$’s confidence.
  \item \textbf{置信度加权合并（Confidence-weighted merging）：} $f_\text{merged} = \sum_i w_i f_i$，其中 $w_i$ 是智能体 $i$ 的置信度。
  \item \textbf{Designated authority:} assign ownership of memory regions to specific agents.
  \item \textbf{指定权威（Designated authority）：}将内存区域的所有权分配给特定智能体。
\end{itemize}

\begin{questionbox}[Open Problem: Distributed Memory Consistency]
How should a multi-agent system maintain memory consistency under concurrent writes, network partitions, and adversarial agents? Classical distributed systems solutions (Paxos, Raft) apply but are expensive. Approximate consistency with bounded staleness may be sufficient for many agentic tasks---but the right trade-off is an open research question.
\end{questionbox}
\begin{questionbox}[开放问题：分布式内存一致性]
在多智能体系统中，如何在并发写入、网络分区和对抗性智能体的条件下保持内存一致性？经典的分布式系统解决方案（Paxos、Raft）适用但代价高昂。对于许多智能体任务，具有有限过时性的近似一致性可能足够——但正确的权衡仍是一个开放的研究问题。
\end{questionbox}

\section{Training Memory Systems with Reinforcement Learning}
\section{使用强化学习训练内存系统}
\label{sec:rl-memory}

\subsection{Reward Signals for Memory Operations}
\subsection{内存操作的奖励信号}
\label{reward-signals-for-memory-operations}

Memory operations (read, write, update, reflect) can be treated as actions in the RL framework. The challenge is designing reward signals that incentivize \emph{useful} memory behavior:
内存操作（读取、写入、更新、反思）可以被视作强化学习框架中的动作。挑战在于设计能够激励\emph{有用}内存行为的奖励信号：

\begin{itemize}
  \item \textbf{Task reward propagation.} If a memory retrieval leads to a correct answer, credit the retrieval action. Sparse but unambiguous.
  \item \textbf{任务奖励传播（Task reward propagation）。}如果一次内存检索导致正确答案，则奖励该检索动作。稀疏但明确。
  \item \textbf{Retrieval precision reward.} $r_\text{retrieve} = \text{Relevance}(d_\text{retrieved}, \text{task})$, estimated by a learned relevance model.
  \item \textbf{检索精度奖励（Retrieval precision reward）。} $r_\text{retrieve} = \text{Relevance}(d_\text{retrieved}, \text{task})$，由学习到的相关性模型估计。
  \item \textbf{Memory efficiency reward.} Penalize unnecessary writes: $r_\text{write} = -\lambda \cdot \mathbf{1}[\text{write}]$, encouraging selective storage.
  \item \textbf{内存效率奖励（Memory efficiency reward）。}惩罚不必要的写入：$r_\text{write} = -\lambda \cdot \mathbf{1}[\text{write}]$，鼓励选择性存储。
  \item \textbf{Consistency reward.} Reward memory states that are internally consistent (no contradictions).
  \item \textbf{一致性奖励（Consistency reward）。}奖励内部一致（无矛盾）的内存状态。
\end{itemize}

The combined reward for a memory operation $m_t$ at step $t$: 
\[
r_t^{\text{mem}} = r_t^{\text{task}} + \alpha \cdot r_t^{\text{retrieve}} + \beta \cdot r_t^{\text{write}} + \gamma \cdot r_t^{\text{consistency}}.
\]
在步骤 $t$ 对内存操作 $m_t$ 的综合奖励为：
\[
r_t^{\text{mem}} = r_t^{\text{task}} + \alpha \cdot r_t^{\text{retrieve}} + \beta \cdot r_t^{\text{write}} + \gamma \cdot r_t^{\text{consistency}}.
\]

\subsection{Learning What to Remember}
\subsection{学习记住什么}
\label{learning-what-to-remember}

The \emph{what-to-remember} problem is a meta-learning challenge: the agent must learn a write policy $\pi_\text{write}(e)$ that maximizes future task performance. This is difficult because:
\emph{记住什么（what-to-remember）}问题是一个元学习挑战：智能体必须学会一个写入策略 $\pi_\text{write}(e)$，以最大化未来任务性能。这很困难，因为：

\begin{enumerate}
  \item The value of a memory is only revealed in the future (delayed reward).
  \item 内存的价值只在未来才会显现（延迟奖励）。
  \item The space of possible future queries is unknown at write time.
  \item 写入时未来可能查询的空间是未知的。
  \item Memories interact: the value of storing $e$ depends on what else is in $\mathcal{M}$.
  \item 内存之间存在交互：存储 $e$ 的价值取决于 $\mathcal{M}$ 中还有哪些内容。
\end{enumerate}

Approaches:
方法包括：

\begin{itemize}
  \item \textbf{Hindsight relabeling}~\cite{andrychowicz2017hindsight}. After a successful episode, retroactively label the memories that were retrieved as ``important'' and train the write policy to store similar items.
  \item \textbf{事后重新标记（Hindsight relabeling）}~\cite{andrychowicz2017hindsight}。在一个成功的回合之后，将检索到的内存回溯标记为“重要”，并训练写入策略以存储类似项目。
  \item \textbf{Meta-RL}~\cite{duan2016rl2}. Train the write policy across a distribution of tasks; the policy learns to store information that generalizes across tasks.
  \item \textbf{元强化学习（Meta-RL）}~\cite{duan2016rl2}。在任务分布上训练写入策略；该策略学会存储能够跨任务泛化的信息。
  \item \textbf{Curiosity-driven storage}~\cite{pathak2017curiosity}. Store observations that are surprising (high prediction error), as these are likely to be informative.
  \item \textbf{好奇心驱动的存储（Curiosity-driven storage）}~\cite{pathak2017curiosity}。存储令人惊讶（高预测误差）的观测，因为这些很可能包含信息。
\end{itemize}

\subsection{Memory-Augmented Policy Optimization}
\subsection{内存增强的策略优化}
\label{memory-augmented-policy-optimization}

The idea of jointly optimizing a policy and its memory system dates to differentiable memory networks~\cite{graves2016hybrid} and was extended to retrieval-augmented LLMs by REALM~\cite{guu2020realm}. The full policy gradient objective for a memory-augmented agent: 
\[
\mathcal{L}(\theta, \phi) = \mathbb{E}_{\tau \sim \pi_\theta}\!\left[\sum_{t=0}^T \gamma^t r_t\right] - \lambda \cdot \mathcal{L}_\text{mem}(\phi),
\]
 where $\theta$ are the LLM parameters, $\phi$ are the memory system parameters (e.g.~retrieval model weights), and $\mathcal{L}_\text{mem}$ is a regularization term on memory complexity.
联合优化策略及其内存系统的思想可以追溯到可微内存网络~\cite{graves2016hybrid}，并由REALM~\cite{guu2020realm}扩展到检索增强的大语言模型。内存增强智能体的完整策略梯度目标为：
\[
\mathcal{L}(\theta, \phi) = \mathbb{E}_{\tau \sim \pi_\theta}\!\left[\sum_{t=0}^T \gamma^t r_t\right] - \lambda \cdot \mathcal{L}_\text{mem}(\phi),
\]
其中 $\theta$ 是大语言模型参数，$\phi$ 是内存系统参数（例如检索模型权重），$\mathcal{L}_\text{mem}$ 是内存复杂度的正则化项。

\begin{keybox}[Key Insight: Memory as a Learned Inductive Bias]
Training memory operations with RL allows the agent to develop task-specific memory strategies. A coding agent learns to store API signatures; a research agent learns to store citation chains; a customer service agent learns to store user complaint patterns. The memory system becomes a \emph{learned inductive bias} tailored to the agent’s domain.
\end{keybox}
\begin{keybox}[关键洞察：内存作为学习到的归纳偏置]
使用强化学习训练内存操作使智能体能够开发特定任务的内存策略。编码智能体学会存储API签名；研究智能体学会存储引用链；客服智能体学会存储用户投诉模式。内存系统成为针对智能体领域定制的\emph{学习到的归纳偏置（learned inductive bias）}。
\end{keybox}

\section{Comparison of Memory Approaches}
\section{内存方法对比}
\label{sec:memory-comparison}

\begin{table}[ht!]
\centering
\caption{Comparison of agentic memory architectures across key dimensions.}
\caption{关键维度上的智能体记忆架构对比。}
\resizebox{\textwidth}{!}{
\begin{tabular}{@{}llllll@{}}
\toprule
\textbf{Architecture} & \textbf{Capacity} & \textbf{Retrieval} & \textbf{Update Cost} & \textbf{Trainable} & \textbf{Best For} \\
\textbf{架构} & \textbf{容量} & \textbf{检索} & \textbf{更新开销} & \textbf{可训练性} & \textbf{最适合} \\
\midrule
In-context (working) & $O(L)$ tokens & 0 ms & Free & Via fine-tuning & Short tasks, active reasoning \\
上下文（工作记忆） & $O(L)$ token & 0 毫秒 & 免费 & 通过微调 & 短任务、主动推理 \\
Dense RAG~\cite{lewis2020retrieval} & $O(10^7)$ docs & 10--50 ms & $O(1)$ embed & Encoder only & Semantic search, QA \\
密集RAG~\cite{lewis2020retrieval} & $O(10^7)$ 文档 & 10--50 毫秒 & $O(1)$ 嵌入 & 仅编码器 & 语义搜索、问答 \\
Sparse (BM25)~\cite{robertson2009probabilistic} & $O(10^8)$ docs & 1--5 ms & $O(|d|)$ index & No & Keyword search, legal/medical \\
稀疏（BM25）~\cite{robertson2009probabilistic} & $O(10^8)$ 文档 & 1--5 毫秒 & $O(|d|)$ 索引 & 否 & 关键词搜索、法律/医学 \\
Hybrid RAG~\cite{chen2022hybrid} & $O(10^7)$ docs & 15--60 ms & $O(1)$ embed & Encoder only & General-purpose retrieval \\
混合RAG~\cite{chen2022hybrid} & $O(10^7)$ 文档 & 15--60 毫秒 & $O(1)$ 嵌入 & 仅编码器 & 通用检索 \\
Summarization & Unlimited & 0 ms (in-ctx) & $O(|e|)$ LLM call & Via fine-tuning & Long conversations, narratives \\
摘要 & 无限 & 0 毫秒（上下文内） & $O(|e|)$ LLM调用 & 通过微调 & 长对话、叙述 \\
Knowledge Graph~\cite{lacroix2020tensor} & $O(10^9)$ triples & 5--100 ms & $O(1)$ insert & Embedding layer & Structured facts, multi-hop \\
知识图谱~\cite{lacroix2020tensor} & $O(10^9)$ 三元组 & 5--100 毫秒 & $O(1)$ 插入 & 嵌入层 & 结构化事实、多跳 \\
KV Memory Net~\cite{sukhbaatar2015end} & $O(M)$ slots & $O(M)$ attn & Gradient step & Fully & End-to-end differentiable tasks \\
KV记忆网络~\cite{sukhbaatar2015end} & $O(M)$ 槽位 & $O(M)$ 注意力 & 梯度步 & 完全可训练 & 端到端可微分任务 \\
MemGPT tiered~\cite{packer2023memgpt} & Unlimited & 0--100 ms & Mixed & Via RL & Long-horizon agents, assistants \\
MemGPT分层~\cite{packer2023memgpt} & 无限 & 0--100 毫秒 & 混合 & 通过强化学习 & 长周期智能体、助手 \\
Graph RAG~\cite{edge2024local} & $O(10^7)$ nodes & 20--200 ms & $O(1)$ insert & Encoder only & Complex reasoning, communities \\
图RAG~\cite{edge2024local} & $O(10^7)$ 节点 & 20--200 毫秒 & $O(1)$ 插入 & 仅编码器 & 复杂推理、社区 \\
\bottomrule
\end{tabular}
}
\end{table}

\section{Evaluating Memory Systems}
\section{评估记忆系统}
\label{sec:memory-evaluation}

Evaluating agentic memory is challenging because the quality of memory operations is only revealed \emph{indirectly}---through downstream task performance over long horizons. A memory system that achieves perfect recall of stored facts can still fail if it retrieves irrelevant context or overwhelms the LLM's context window.

评估智能体记忆具有挑战性，因为记忆操作的质量仅能通过长期的下游任务性能\emph{间接}体现。一个能够完美召回存储事实的记忆系统，如果检索到无关上下文或超出LLM的上下文窗口限制，仍然可能失败。

\subsection{Evaluation Dimensions}
\subsection{评估维度}
\label{evaluation-dimensions}

LongMemEval~\cite{wu2024longmemeval} identifies five core capabilities that a long-term memory system must demonstrate:

LongMemEval~\cite{wu2024longmemeval} 确定了长期记忆系统必须展示的五项核心能力：

\begin{enumerate}
  \item \textbf{Information extraction.} Can the system identify and store salient facts from conversational turns? Measured by fact recall: what fraction of ground-truth facts are recoverable from memory?
  \item \textbf{信息提取。} 系统能否从对话轮次中识别并存储重要事实？通过事实召回率衡量：有多少真实事实可从记忆中恢复？
  \item \textbf{Multi-session reasoning.} Can the system synthesize information scattered across multiple past sessions? E.g., ``Based on our conversations last week and yesterday, what changed in the project scope?''
  \item \textbf{多会话推理。} 系统能否综合分布在多个过去会话中的信息？例如，“根据我们上周和昨天的对话，项目范围发生了什么变化？”
  \item \textbf{Temporal reasoning.} Can the system correctly answer time-dependent queries? E.g., ``What did I say was my priority \emph{before} the reorg?'' requires distinguishing temporal states.
  \item \textbf{时间推理。} 系统能否正确回答依赖时间的查询？例如，“在重组\emph{之前}我说过什么是我的优先事项？”需要区分时间状态。
  \item \textbf{Knowledge updates.} When facts change (user moves cities, preferences shift), does memory reflect the latest state while preserving history?
  \item \textbf{知识更新。} 当事实发生变化（用户搬家、偏好改变）时，记忆是否能在保留历史的同时反映最新状态？
  \item \textbf{Abstention.} When the system has no relevant memory, does it correctly say ``I don't know'' rather than hallucinate a plausible but fabricated recollection?
  \item \textbf{弃权。} 当系统没有相关记忆时，它是否会正确地说“我不知道”，而不是编造看似合理但虚假的回忆？
\end{enumerate}

\subsection{Benchmarks}
\subsection{基准}
\label{benchmarks}

\begin{table}[ht!]
\centering
\caption{Benchmarks for evaluating agentic memory systems.}
\caption{评估智能体记忆系统的基准。}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{Benchmark} & \textbf{Venue} & \textbf{Scale} & \textbf{Focus} \\
\textbf{基准} & \textbf{会议/期刊} & \textbf{规模} & \textbf{重点} \\
\midrule
LongMemEval~\cite{wu2024longmemeval} & ICLR 2025 & 500 questions, scalable histories & Five memory abilities; multi-session chat \\
LongMemEval~\cite{wu2024longmemeval} & ICLR 2025 & 500个问题，可扩展历史 & 五种记忆能力；多会话聊天 \\
LOCOMO~\cite{maharana2024locomo} & EMNLP 2024 & Multi-session dialogues & Single-hop, temporal, multi-hop, open-domain QA over conversations \\
LOCOMO~\cite{maharana2024locomo} & EMNLP 2024 & 多会话对话 & 单跳、时间、多跳、跨对话的开放域问答 \\
InfiniteBench~\cite{zhang2024infinitebench} & ACL 2024 & 100K+ token contexts & Long-context recall, not memory-specific but tests limits \\
InfiniteBench~\cite{zhang2024infinitebench} & ACL 2024 & 10万+ token上下文 & 长上下文召回，非特定记忆但测试极限 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Metrics}
\subsection{度量指标}
\label{metrics}

\paragraph{Memory-Level Metrics.}
\paragraph{记忆层度量指标。}
\label{memory-level-metrics.}

\begin{itemize}
  \item \textbf{Memory Recall}: $\frac{\text{\# ground-truth facts retrievable from memory}}{\text{\# total ground-truth facts}}$. Measures completeness of storage.
  \item \textbf{记忆召回率}：$\frac{\text{\# 可从记忆中检索的真实事实数量}}{\text{\# 真实事实总数}}$。衡量存储的完整性。
  \item \textbf{Memory Precision}: $\frac{\text{\# relevant items in top-}k\text{ retrieval}}{k}$. Measures noise in retrieval.
  \item \textbf{记忆精确率}：$\frac{\text{\# 前}k\text{个检索结果中相关项的数量}}{k}$。衡量检索中的噪声。
  \item \textbf{Latency}: time from query to retrieved context (p50 and p95).
  \item \textbf{延迟}：从查询到检索出上下文的时间（p50和p95）。
  \item \textbf{Token efficiency}: total tokens injected into context per query. Lower is better---unnecessary context degrades LLM accuracy and increases cost.
  \item \textbf{Token效率}：每次查询注入上下文的token总数。越低越好——不必要的上下文会降低LLM准确性并增加成本。
\end{itemize}

\paragraph{Downstream Metrics.}
\paragraph{下游度量指标。}
\label{downstream-metrics.}

\begin{itemize}
  \item \textbf{Answer accuracy}: correctness of the final response conditioned on memory (EM, F1, or LLM-as-judge).
  \item \textbf{答案准确性}：基于记忆的最终响应的正确性（精确匹配、F1或LLM作为评判者）。
  \item \textbf{Faithfulness}: does the response accurately reflect what memory contains, without fabrication?
  \item \textbf{忠实性}：响应是否准确反映记忆中的内容，没有捏造？
  \item \textbf{Personalization quality}: user satisfaction, measured via preference ratings or A/B tests between memory-augmented and memoryless systems.
  \item \textbf{个性化质量}：用户满意度，通过偏好评分或记忆增强系统与无记忆系统之间的A/B测试衡量。
  \item \textbf{Contradiction rate}: how often the system produces responses inconsistent with previously stated facts.
  \item \textbf{矛盾率}：系统产生与先前陈述事实不一致的响应的频率。
\end{itemize}

\paragraph{Operational Metrics.}
\paragraph{操作度量指标。}
\label{operational-metrics.}

\begin{itemize}
  \item \textbf{Write selectivity}: fraction of turns that trigger a memory write. Too high $\to$ noise; too low $\to$ gaps.
  \item \textbf{写入选择性}：触发记忆写入的轮次比例。过高 $\to$ 噪声；过低 $\to$ 空白。
  \item \textbf{Staleness}: how often outdated facts are retrieved despite an update existing.
  \item \textbf{过时性}：尽管存在更新，但过时事实被检索的频率。
  \item \textbf{Storage growth rate}: tokens stored per interaction hour. Unbounded growth is unsustainable.
  \item \textbf{存储增长率}：每交互小时存储的token数。无限制增长是不可持续的。
\end{itemize}

\begin{warningbox}[The Evaluation Gap]
Most memory papers evaluate on short benchmarks (10--50 sessions). Real production agents run for months with thousands of sessions. Long-horizon evaluation---where memory drift, contradiction accumulation, and storage bloat become dominant failure modes---remains an open challenge. Practitioners should complement benchmark scores with longitudinal monitoring of operational metrics.
\end{warningbox}
\begin{warningbox}[评估差距]
大多数记忆论文在短基准（10-50个会话）上进行评估。实际生产中的智能体运行数月，涉及数千个会话。长期评估——其中记忆漂移、矛盾积累和存储膨胀成为主要失败模式——仍然是一个开放挑战。实践者应通过操作指标的纵向监测来补充基准分数。
\end{warningbox}

\section{Implementation Patterns}
\section{实现模式}
\label{sec:memory-implementation}

\subsection{Vector Store Memory with Embeddings}
\subsection{基于嵌入的向量存储记忆}
\label{vector-store-memory-with-embeddings}

The most common memory pattern stores entries as embedding vectors alongside metadata (timestamps, importance scores, tags). Retrieval combines cosine similarity with temporal decay, so recent and important memories surface first. Duplicate detection and LRU eviction keep the store bounded.

最常见的记忆模式是将条目存储为嵌入向量，并附带元数据（时间戳、重要性分数、标签）。检索结合余弦相似度和时间衰减，使近期且重要的记忆优先浮现。重复检测和最近最少使用（LRU）淘汰策略保持存储有界。

\begin{lstlisting}[style=pythonstyle, caption={Vector store memory with embeddings, importance scoring, and hybrid retrieval.}]
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json


@dataclass
class MemoryEntry:
    """A single memory entry with metadata."""
    content: str
    embedding: np.ndarray
    timestamp: datetime = field(default_factory=datetime.now)
    importance: float = 0.5
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: list[str] = field(default_factory=list)
    source: str = "agent"
\end{lstlisting}
\begin{lstlisting}[style=pythonstyle, caption={基于嵌入的向量存储记忆，带有重要性评分和混合检索。}]
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json

@dataclass
class MemoryEntry:
    """单个记忆条目及其元数据。"""
    content: str
    embedding: np.ndarray
    timestamp: datetime = field(default_factory=datetime.now)
    importance: float = 0.5
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: list[str] = field(default_factory=list)
    source: str = "agent"
\end{lstlisting}

class VectorMemoryStore:
    """
    Hybrid dense+sparse memory store with temporal decay.
    Supports importance-weighted retrieval and LRU eviction.
    """
    混合密集+稀疏记忆存储，具有时间衰减。
    支持重要性加权检索和LRU（最近最少使用）淘汰。

    def __init__(
        self,
        embed_fn,           # callable: str -> np.ndarray
        max_entries: int = 10_000,
        decay_rate: float = 0.01,   # per hour
        recency_weight: float = 0.3,
    ):
        self.embed_fn = embed_fn
        self.max_entries = max_entries
        self.decay_rate = decay_rate
        self.recency_weight = recency_weight
        self.entries: list[MemoryEntry] = []

    # -- Write --------------------------------------------------------------
    # -- 写入 --------------------------------------------------------------

    def write(
        self,
        content: str,
        importance: float = 0.5,
        tags: list[str] | None = None,
        check_duplicates: bool = True,
    ) -> MemoryEntry:
        """Commit a new memory, evicting if at capacity."""
        """提交一条新记忆，若容量已满则进行淘汰。"""
        if check_duplicates and self._is_duplicate(content):
            return None  # Skip near-duplicate entries
                       # 跳过近似重复条目

        embedding = self.embed_fn(content)
        entry = MemoryEntry(
            content=content,
            embedding=embedding,
            importance=importance,
            tags=tags or [],
        )

        if len(self.entries) >= self.max_entries:
            self._evict()

        self.entries.append(entry)
        return entry

    def _is_duplicate(self, content: str, threshold: float = 0.95) -> bool:
        """Check if a near-duplicate already exists."""
        """检查是否已存在近似重复条目。"""
        if not self.entries:
            return False
        emb = self.embed_fn(content)
        sims = self._cosine_similarities(emb)
        return float(np.max(sims)) > threshold

    def _evict(self):
        """Remove the least important + least recent entry."""
        """移除最不重要且最不近期的条目。"""
        now = datetime.now()
        scores = []
        for e in self.entries:
            age_hours = (now - e.timestamp).total_seconds() / 3600
            recency = np.exp(-self.decay_rate * age_hours)
            score = e.importance * (1 - self.recency_weight) \
                  + recency * self.recency_weight
            scores.append(score)
        worst_idx = int(np.argmin(scores))
        self.entries.pop(worst_idx)

    # -- Retrieve -----------------------------------------------------------
    # -- 检索 --------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        k: int = 5,
        recency_boost: bool = True,
    ) -> list[MemoryEntry]:
        """
        Hybrid retrieval: dense similarity + temporal recency.
        Returns top-k entries sorted by combined score.
        """
        混合检索：密集相似度 + 时间近因。
        返回按组合分数排序的前k个条目。
        if not self.entries:
            return []

        q_emb = self.embed_fn(query)
        dense_scores = self._cosine_similarities(q_emb)

        now = datetime.now()
        combined = []
        for i, (entry, d_score) in enumerate(
            zip(self.entries, dense_scores)
        ):
            if recency_boost:
                age_h = (now - entry.timestamp).total_seconds() / 3600
                recency = np.exp(-self.decay_rate * age_h)
                score = (1 - self.recency_weight) * d_score \
                      + self.recency_weight * recency
            else:
                score = d_score
            combined.append((score, i))

        combined.sort(reverse=True)
        top_k = [self.entries[i] for _, i in combined[:k]]

        # Update access metadata
        # 更新访问元数据
        for entry in top_k:
            entry.access_count += 1
            entry.last_accessed = now

        return top_k

    def _cosine_similarities(self, query_emb: np.ndarray) -> np.ndarray:
        """Vectorized cosine similarity against all stored embeddings."""
        """针对所有存储嵌入的向量化余弦相似度计算。"""
        matrix = np.stack([e.embedding for e in self.entries])
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        matrix_norm = matrix / (norms + 1e-8)
        q_norm = query_emb / (np.linalg.norm(query_emb) + 1e-8)
        return matrix_norm @ q_norm

    # -- Reflect ------------------------------------------------------------
    # -- 反思 --------------------------------------------------------------

    def reflect(self, llm_fn, k: int = 10) -> list[str]:
        """
        Meta-cognitive reflection: retrieve recent memories,
        synthesize higher-level insights, and store them back.
        """
        元认知反思：检索近期记忆，
        综合更高级别的洞察，并将其存储回记忆库。
        if len(self.entries) < 3:
            return []

        # Retrieve recent high-importance memories
        # 检索近期高重要性记忆
        recent = sorted(
            self.entries, key=lambda e: e.timestamp, reverse=True
        )[:k]
        context = "\n".join(f"- {e.content}" for e in recent)

        # Ask LLM to generate insights
        # 请求LLM生成洞察
        prompt = (
            "Given these recent memories, extract 2-3 high-level "
            "insights or patterns:\n" + context
        )
        raw_insights = llm_fn(prompt)

        # Store each insight as a high-importance memory
        # 将每条洞察作为高重要性记忆存储
        insights = []
        for line in raw_insights.strip().split("\n"):
            line = line.strip().lstrip("-*").strip()
            if len(line) > 20:
                self.write(
                    f"[INSIGHT] {line}",
                    importance=0.9,
                    check_duplicates=True,
                )
                insights.append(line)
        return insights

    def get_stats(self) -> dict:
        """Return memory statistics for monitoring."""
        """返回用于监控的记忆统计信息。"""
        return {
            "total_entries": len(self.entries),
            "avg_importance": float(
                np.mean([e.importance for e in self.entries])
            ) if self.entries else 0.0,
            "oldest_entry": min(
                (e.timestamp for e in self.entries), default=None
            ),
        }
\end{lstlisting}

\subsection{Hierarchical Memory Manager}
\subsection{分层记忆管理器}
\label{hierarchical-memory-manager}


Inspired by MemGPT~\cite{packer2023memgpt}, this pattern organises memory into three tiers: \emph{hot} (in-context, immediate access), \emph{warm} (vector store, fast retrieval), and \emph{cold} (archival, unlimited capacity). Entries are automatically promoted or demoted based on access frequency and importance---analogous to CPU cache hierarchies.
受 MemGPT~\cite{packer2023memgpt} 的启发，该模式将记忆组织为三个层级：\emph{hot（热）}（上下文内，即时访问）、\emph{warm（温）}（向量存储，快速检索）和 \emph{cold（冷）}（存档，无限容量）。条目会根据访问频率和重要性自动升级或降级——类似于 CPU 缓存层次结构。

\begin{lstlisting}[style=pythonstyle, caption={Hierarchical memory manager implementing hot/warm/cold tiers with automatic promotion and demotion.}]
\begin{lstlisting}[style=pythonstyle, caption={实现热/温/冷三层及自动升级降级的分层记忆管理器。}]
from enum import Enum
from collections import OrderedDict


class MemoryTier(Enum):
    HOT  = "hot"    # In-context: immediate access
                    # 上下文内：即时访问
    WARM = "warm"   # Vector store: fast retrieval
                    # 向量存储：快速检索
    COLD = "cold"   # Archival: slow but unlimited
                    # 存档：速度慢但容量无限

```markdown
\subsection{Memory-Augmented Agent Loop}
\subsection{记忆增强型智能体循环}
\label{memory-augmented-agent-loop}

This pattern, introduced by MemGPT~\cite{packer2023memgpt} and formalized in the CoALA framework~\cite{sumers2023coala}, wires the memory system into the agent’s reasoning loop via a \emph{read--act--reflect--write} cycle: before responding, the agent retrieves relevant memories; after responding, it decides what to store. Special tokens in the LLM output trigger memory operations, giving the model self-directed control over its own persistence.
该模式由 MemGPT~\cite{packer2023memgpt} 提出，并在 CoALA 框架~\cite{sumers2023coala} 中正式化，通过 \emph{读取--行动--反思--写入} 循环将记忆系统集成到智能体的推理循环中：在响应之前，智能体检索相关记忆；响应之后，它决定存储什么。LLM 输出中的特殊标记触发记忆操作，使模型能够自主控制其自身的持久性。

\begin{lstlisting}[style=pythonstyle, caption={Complete memory-augmented agent loop with read-act-reflect-write cycle.}]
\begin{lstlisting}[style=pythonstyle, caption={完整的记忆增强型智能体循环，包含读取-行动-反思-写入周期。}]
import re
from typing import Any


class MemoryAugmentedAgent:
    """
    An LLM agent with a full read-act-reflect-write memory cycle.
    Implements the MemGPT-style self-directed memory management.
    """

    SYSTEM_PROMPT = """You are a memory-augmented AI assistant.
You have access to persistent memory across conversations.
At each turn you may issue memory commands:
  [MEMORY_SEARCH: <query>]  - retrieve relevant memories
  [MEMORY_WRITE: <content>] - store important information
  [MEMORY_REFLECT]          - synthesize insights from memory
```

类 MemoryAugmentedAgent:
    """
    一个完整的读取-行动-反思-写入记忆循环的 LLM 智能体。
    实现了 MemGPT 风格的自主记忆管理。
    """

    SYSTEM_PROMPT = """你是一个记忆增强型 AI 助手。
你可以访问跨对话的持久性记忆。
在每次交互中，你可以发出记忆命令：
  [MEMORY_SEARCH: <query>]  - 检索相关记忆
  [MEMORY_WRITE: <content>] - 存储重要信息
  [MEMORY_REFLECT]          - 从记忆中综合洞见
```

## 1.2 A Minimal Memory-Augmented Agent
## 1.2 最小记忆增强代理

We now walk through a concrete implementation of a memory-augmented agent.
我们现在将逐步讲解一个记忆增强代理的具体实现。

The code below defines a minimal `MemoryAugmentedAgent` that uses a three-tier memory hierarchy (hot, warm, cold) together with an LLM backend.
下面的代码定义了一个最小化的 `MemoryAugmentedAgent`，它使用三层记忆层级（热内存、温内存、冷内存）并配合一个LLM后端。

```python
# WeChat Public Account: 方云智能AI
# 微信公众号：方云智能AI

import re
from datetime import datetime
from typing import List, Optional, Tuple

from memory import HierarchicalMemoryManager, MemoryEntry, MemoryTier

class MemoryAugmentedAgent:
    """A minimal agent that uses hierarchical memory to augment an LLM.
       It reads relevant memories before generating responses,
       writes important information automatically,
       and reflects periodically to consolidate knowledge."""

    """一个使用层级记忆增强LLM的最小化代理。
       它在生成响应前读取相关记忆，
       自动写入重要信息，
       并定期反思以巩固知识。"""

    SYSTEM_PROMPT = """You are an AI assistant with hierarchical memory.
    You can remember information across sessions and use past experiences
    to inform your responses. Always think step by step. Use memory to avoid repeating mistakes
    and to personalize your responses."""

    SYSTEM_PROMPT = """你是一个拥有层级记忆的人工智能助手。
    你能够跨会话记住信息，并利用过去的经验
    来指导你的回答。始终逐步思考。利用记忆避免重复错误
    并个性化你的回应。"""

    def __init__(
        self,
        llm_fn,                         # callable: messages -> str
        memory_manager: HierarchicalMemoryManager,
        importance_threshold: float = 0.6,
        max_memory_tokens: int = 1500,
    ):
        self.llm = llm_fn
        self.memory = memory_manager
        self.importance_threshold = importance_threshold
        self.max_memory_tokens = max_memory_tokens
        self.conversation_history: list[dict] = []

    def __init__(
        self,
        llm_fn,                         # 可调用: messages -> str
        memory_manager: HierarchicalMemoryManager,
        importance_threshold: float = 0.6,
        max_memory_tokens: int = 1500,
    ):
        self.llm = llm_fn
        self.memory = memory_manager
        self.importance_threshold = importance_threshold
        self.max_memory_tokens = max_memory_tokens
        self.conversation_history: list[dict] = []

    # -- Main agent step ----------------------------------------------------

    # -- 主代理步骤 ----------------------------------------------------

    def step(self, user_message: str) -> str:
        """
        Full agent step:
        1. Retrieve relevant memories
        2. Construct augmented prompt
        3. Generate response (possibly with memory commands)
        4. Execute memory commands
        5. Reflect and consolidate
        6. Return response to user
        """

    def step(self, user_message: str) -> str:
        """
        完整的代理步骤：
        1. 检索相关记忆
        2. 构建增强后的提示
        3. 生成响应（可能包含记忆命令）
        4. 执行记忆命令
        5. 反思与巩固
        6. 向用户返回响应
        """

        # Step 1: Retrieve relevant memories
        memories = self.memory.retrieve(user_message, k=5)
        memory_context = self._format_memories(memories)

        # 步骤 1：检索相关记忆
        memories = self.memory.retrieve(user_message, k=5)
        memory_context = self._format_memories(memories)

        # Step 2: Construct augmented prompt
        messages = self._build_messages(user_message, memory_context)

        # 步骤 2：构建增强后的提示
        messages = self._build_messages(user_message, memory_context)

        # Step 3: Generate response
        raw_response = self.llm(messages)

        # 步骤 3：生成响应
        raw_response = self.llm(messages)

        # Step 4: Execute any memory commands in the response
        clean_response, memory_ops = self._parse_memory_commands(
            raw_response
        )
        self._execute_memory_ops(memory_ops, user_message, clean_response)

        # 步骤 4：执行响应中的任何记忆命令
        clean_response, memory_ops = self._parse_memory_commands(
            raw_response
        )
        self._execute_memory_ops(memory_ops, user_message, clean_response)

        # Step 5: Auto-write important information
        self._auto_write(user_message, clean_response)

        # 步骤 5：自动写入重要信息
        self._auto_write(user_message, clean_response)

        # Step 6: Update conversation history
        self.conversation_history.append(
            {"role": "user", "content": user_message}
        )
        self.conversation_history.append(
            {"role": "assistant", "content": clean_response}
        )

        # 步骤 6：更新对话历史
        self.conversation_history.append(
            {"role": "user", "content": user_message}
        )
        self.conversation_history.append(
            {"role": "assistant", "content": clean_response}
        )

        return clean_response

    # -- Memory retrieval and formatting -----------------------------------

    # -- 记忆检索与格式化 -----------------------------------

    def _format_memories(self, memories: list[MemoryEntry]) -> str:
        if not memories:
            return ""
        lines = ["Relevant memories:"]
        for i, m in enumerate(memories, 1):
            age = (datetime.now() - m.timestamp).days
            lines.append(
                f"  [{i}] (importance={m.importance:.1f}, "
                f"{age}d ago) {m.content}"
            )
        return "\n".join(lines)

    def _format_memories(self, memories: list[MemoryEntry]) -> str:
        if not memories:
            return ""
        lines = ["相关记忆："]
        for i, m in enumerate(memories, 1):
            age = (datetime.now() - m.timestamp).days
            lines.append(
                f"  [{i}] (重要性={m.importance:.1f}, "
                f"{age}天前) {m.content}"
            )
        return "\n".join(lines)

    def _build_messages(
        self, user_message: str, memory_context: str
    ) -> list[dict]:
        system = self.SYSTEM_PROMPT
        if memory_context:
            system += f"\n\n{memory_context}"
        system += f"\n\n{self.memory.get_hot_context()}"

        messages = [{"role": "system", "content": system}]
        # Include recent conversation history (last 6 turns)
        messages.extend(self.conversation_history[-6:])
        messages.append({"role": "user", "content": user_message})
        return messages

    def _build_messages(
        self, user_message: str, memory_context: str
    ) -> list[dict]:
        system = self.SYSTEM_PROMPT
        if memory_context:
            system += f"\n\n{memory_context}"
        system += f"\n\n{self.memory.get_hot_context()}"

        messages = [{"role": "system", "content": system}]
        # 包含最近的对话历史（最后6轮）
        messages.extend(self.conversation_history[-6:])
        messages.append({"role": "user", "content": user_message})
        return messages

    # -- Memory command parsing ---------------------------------------------

    # -- 记忆命令解析 ---------------------------------------------

    def _parse_memory_commands(
        self, response: str
    ) -> tuple[str, list[dict]]:
        """Extract and remove memory commands from response."""
        ops = []
        patterns = {
            "search":  r"\[MEMORY_SEARCH:\s*(.+?)\]",
            "write":   r"\[MEMORY_WRITE:\s*(.+?)\]",
            "reflect": r"\[MEMORY_REFLECT\]",
        }
        clean = response
        for op_type, pattern in patterns.items():
            for match in re.finditer(pattern, response, re.DOTALL):
                content = match.group(1) if op_type != "reflect" else None
                ops.append({"type": op_type, "content": content})
                clean = clean.replace(match.group(0), "").strip()
        return clean, ops

    def _parse_memory_commands(
        self, response: str
    ) -> tuple[str, list[dict]]:
        """从响应中提取并移除记忆命令。"""
        ops = []
        patterns = {
            "search":  r"\[MEMORY_SEARCH:\s*(.+?)\]",
            "write":   r"\[MEMORY_WRITE:\s*(.+?)\]",
            "reflect": r"\[MEMORY_REFLECT\]",
        }
        clean = response
        for op_type, pattern in patterns.items():
            for match in re.finditer(pattern, response, re.DOTALL):
                content = match.group(1) if op_type != "reflect" else None
                ops.append({"type": op_type, "content": content})
                clean = clean.replace(match.group(0), "").strip()
        return clean, ops

    def _execute_memory_ops(
        self,
        ops: list[dict],
        user_msg: str,
        response: str,
    ):
        """Execute memory commands issued by the LLM."""
        for op in ops:
            if op["type"] == "search":
                results = self.memory.retrieve(op["content"], k=3)
                # Page results into hot tier for immediate use
                self.memory.page_in(op["content"], k=3)

            elif op["type"] == "write":
                self.memory.write(
                    op["content"],
                    importance=0.8,  # explicitly written = important
                    tier=MemoryTier.WARM,
                )

            elif op["type"] == "reflect":
                self._reflect()

    def _execute_memory_ops(
        self,
        ops: list[dict],
        user_msg: str,
        response: str,
    ):
        """执行LLM发出的记忆命令。"""
        for op in ops:
            if op["type"] == "search":
                results = self.memory.retrieve(op["content"], k=3)
                # 将结果分页到热内存层以便立即使用
                self.memory.page_in(op["content"], k=3)

            elif op["type"] == "write":
                self.memory.write(
                    op["content"],
                    importance=0.8,  # 显式写入 = 重要
                    tier=MemoryTier.WARM,
                )

            elif op["type"] == "reflect":
                self._reflect()

    # -- Auto-write heuristic -----------------------------------------------

    # -- 自动写入启发式规则 -----------------------------------------------

    def _auto_write(self, user_msg: str, response: str):
        """
        Automatically store important information without explicit command.
        Uses a simple heuristic: write if response contains facts,
        decisions, or user preferences.
        """
        importance_keywords = [
            "remember", "important", "note that", "you prefer",
            "your name is", "decided to", "the answer is",
            "key insight", "learned that",
        ]
        combined = (user_msg + " " + response).lower()
        if any(kw in combined for kw in importance_keywords):
            summary = f"User: {user_msg[:100]} | Agent: {response[:200]}"
            self.memory.write(
                summary,
                importance=self.importance_threshold,
                tier=MemoryTier.WARM,
            )

    def _auto_write(self, user_msg: str, response: str):
        """
        无需显式命令，自动存储重要信息。
        使用一个简单的启发式规则：如果响应中包含事实、
        决定或用户偏好，则进行写入。
        """
        importance_keywords = [
            "remember", "important", "note that", "you prefer",
            "your name is", "decided to", "the answer is",
            "key insight", "learned that",
        ]
        combined = (user_msg + " " + response).lower()
        if any(kw in combined for kw in importance_keywords):
            summary = f"User: {user_msg[:100]} | Agent: {response[:200]}"
            self.memory.write(
                summary,
                importance=self.importance_threshold,
                tier=MemoryTier.WARM,
            )

    # -- Reflection --------------------------------------------------------

    # -- 反思 --------------------------------------------------------

    def _reflect(self):
        """
        Meta-cognitive reflection: synthesize insights from recent memory.
        Stores high-level insights back into semantic memory.
        """
        recent = self.memory.retrieve("recent important events", k=10)
        if len(recent) < 3:
            return  # Not enough to reflect on

        recent_text = "\n".join(f"- {m.content}" for m in recent)
        insight_prompt = [
            {"role": "system", "content": "You extract high-level insights."},
            {"role": "user", "content":
                f"Based on these memories, what are 2-3 key insights?\n"
                f"{recent_text}\nRespond with bullet points only."},
        ]
        insights = self.llm(insight_prompt)
        # Store each insight as a high-importance semantic memory
        for line in insights.split("\n"):
            line = line.strip().lstrip("*-").strip()
            if len(line) > 20:
                self.memory.write(
                    f"[INSIGHT] {line}",
                    importance=0.9,
                    tier=MemoryTier.WARM,
                )

    def _reflect(self):
        """
        元认知反思：从近期记忆中提炼洞察。
        将高层级的洞察存储回语义记忆。
        """
        recent = self.memory.retrieve("recent important events", k=10)
        if len(recent) < 3:
            return  # 素材不足，无法反思

        recent_text = "\n".join(f"- {m.content}" for m in recent)
        insight_prompt = [
            {"role": "system", "content": "You extract high-level insights."},
            {"role": "user", "content":
                f"Based on these memories, what are 2-3 key insights?\n"
                f"{recent_text}\nRespond with bullet points only."},
        ]
        insights = self.llm(insight_prompt)
        # 将每条洞察存储为高重要性的语义记忆
        for line in insights.split("\n"):
            line = line.strip().lstrip("*-").strip()
            if len(line) > 20:
                self.memory.write(
                    f"[INSIGHT] {line}",
                    importance=0.9,
                    tier=MemoryTier.WARM,
                )
\end{lstlisting}

\begin{intuitionbox}[The Read-Act-Reflect-Write Cycle]
The memory-augmented agent loop implements a four-phase cognitive cycle:

\begin{intuitionbox}[读取-行动-反思-写入循环]
记忆增强代理循环实现了一个四阶段认知周期：

\begin{enumerate}
  \item \textbf{Read:} Before acting, retrieve relevant memories to inform the response.
  \item \textbf{Act:} Generate a response conditioned on retrieved context.
  \item \textbf{Reflect:} Periodically synthesize higher-level insights from accumulated memories.
  \item \textbf{Write:} Selectively commit important new information to persistent storage.
\end{enumerate}

\begin{enumerate}
  \item \textbf{读取：} 行动之前，检索相关记忆来指导响应。
  \item \textbf{行动：} 基于检索到的上下文生成响应。
  \item \textbf{反思：} 定期从累积的记忆中综合出更高层级的洞察。
  \item \textbf{写入：} 有选择地将重要的新信息提交到持久存储。
\end{enumerate}

This cycle mirrors the \emph{observe-orient-decide-act} (OODA) loop from military strategy and the \emph{encode-store-retrieve} model from cognitive psychology. The key insight is that memory is not a passive store but an \emph{active participant} in cognition.
这个循环模仿了军事战略中的\emph{观察-定向-决策-行动}（OODA）循环以及认知心理学中的\emph{编码-存储-检索}模型。关键洞察在于，记忆并非被动的存储库，而是认知中的\emph{主动参与者}。
\end{intuitionbox}

\section{Recent Advances in Agentic Memory}
\label{sec:memory-recent}

\section{代理记忆的最新进展}
\label{sec:memory-recent}

The memory systems described above established the foundational patterns. Several recent works push the boundaries further:
上述记忆系统奠定了基本模式。近期的一些工作进一步拓展了边界：

\subsection{CoALA: Cognitive Architectures for Language Agents}
\label{coala-cognitive-architectures-for-language-agents}

\subsection{CoALA：语言代理的认知架构}
\label{coala-cognitive-architectures-for-language-agents}

## Sumers et al.~\cite{sumers2023coala} propose \emph{Cognitive Architectures for Language Agents} (CoALA), a unifying framework that organizes the growing zoo of LLM agents using principles from cognitive science and symbolic AI. CoALA decomposes a language agent into:
## Sumers 等人~\cite{sumers2023coala} 提出了 \emph{语言智能体认知架构} (CoALA)，这是一个统一框架，利用认知科学和符号人工智能的原理来组织日益庞大的 LLM 智能体生态系统。CoALA 将语言智能体分解为：

\begin{itemize}
  \item \textbf{Modular memory}: working memory (the context window), episodic memory (past experiences), semantic memory (world knowledge), and procedural memory (action schemas)---mirroring our taxonomy in Section~\ref{sec:memory-taxonomy}.
  \item \textbf{模块化记忆}：工作记忆（上下文窗口）、情景记忆（过往经历）、语义记忆（世界知识）和程序记忆（动作模式）——这与我们在第~\ref{sec:memory-taxonomy} 节中的分类法相呼应。
  \item \textbf{Structured action space}: internal actions (reasoning, retrieval, memory writes) and external actions (tool use, environment interaction).
  \item \textbf{结构化动作空间}：内部动作（推理、检索、记忆写入）和外部动作（工具使用、环境交互）。
  \item \textbf{Decision cycle}: a generalized sense--plan--act loop with explicit retrieval and write steps.
  \item \textbf{决策循环}：一个泛化的感知-规划-行动循环，包含显式的检索和写入步骤。
\end{itemize}

CoALA’s contribution is less a new system than a \emph{design language}: it provides a systematic way to analyze existing agents and identify missing capabilities, making it a useful reference architecture for practitioners.
CoALA 的贡献与其说是一个新系统，不如说是一种 \emph{设计语言}：它提供了一种系统化方法，用于分析现有智能体并识别缺失的能力，从而成为实践者有用的参考架构。

\subsection{Mem0: Production-Scale Memory Layer}
\subsection{Mem0：生产级记忆层}
\label{mem0-production-scale-memory-layer}

Mem0~\cite{chhikara2025mem0} addresses the gap between research memory systems and production deployment. Key ideas:
Mem0~\cite{chhikara2025mem0} 弥合了研究型记忆系统与生产部署之间的差距。关键思路如下：

\begin{itemize}
  \item \textbf{Automatic extraction}: Rather than relying on the LLM to explicitly issue memory-write commands, Mem0 automatically extracts salient facts from conversation turns and consolidates them into a persistent store.
  \item \textbf{自动提取}：Mem0 不依赖 LLM 显式发出记忆写入命令，而是自动从对话轮次中提取显著事实，并将其整合到持久化存储器中。
  \item \textbf{Graph-based memory}: Beyond flat vector stores, Mem0 maintains a \emph{relational graph} over extracted entities and facts, enabling multi-hop memory queries (``What did the user say about topic X in the context of project Y?'').
  \item \textbf{基于图的记忆}：Mem0 超越了平面向量存储，维护了一个关于提取实体和事实的 \emph{关系图}，支持多跳记忆查询（“用户在项目 Y 的背景下对主题 X 说了什么？”）。
  \item \textbf{Memory compression}: Redundant or superseded facts are automatically merged, keeping the memory store compact and current.
  \item \textbf{记忆压缩}：冗余或过时的事实会被自动合并，使记忆存储保持紧凑且最新。
\end{itemize}

On the LOCOMO benchmark, Mem0 achieves 26\% relative improvement over OpenAI’s baseline memory, with 91\% lower p95 latency and $>$90\% token cost reduction compared to full-context approaches.
在 LOCOMO 基准测试中，与 OpenAI 的基线记忆系统相比，Mem0 实现了 26\% 的相对改进，p95 延迟降低 91\%，与全上下文方法相比，令牌成本减少 $>$90\%。

\subsection{Sleep-Time Compute: Offline Memory Processing}
\subsection{睡眠时间计算：离线记忆处理}
\label{sleep-time-compute-offline-memory-processing}

Lin et al.~\cite{lin2025sleeptime} introduce \emph{sleep-time compute}, a paradigm where agents process and consolidate memory \emph{between} user interactions rather than only at query time. The analogy is to biological sleep, during which the brain consolidates memories and pre-computes useful associations.
Lin 等人~\cite{lin2025sleeptime} 引入了 \emph{睡眠时间计算}，这是一种范式，智能体在用户交互 \emph{之间} 处理和整合记忆，而不仅仅是在查询时。这类似于生物睡眠，在此期间大脑会巩固记忆并预先计算有用的关联。

\paragraph{How it works.}
\paragraph{工作原理。}
\label{how-it-works.}

During idle periods (``sleep''), the agent:
在空闲时段（“睡眠”）中，智能体：

\begin{enumerate}
  \item Anticipates likely future queries given the current context.
  \item 根据当前上下文预测可能的未来查询。
  \item Pre-computes reasoning chains, summaries, and structured representations.
  \item 预先计算推理链、摘要和结构化表示。
  \item Stores these pre-computed artifacts so that test-time inference can retrieve and reuse them.
  \item 存储这些预先计算的结果，以便测试时的推理可以检索并重用它们。
\end{enumerate}

\paragraph{Results.}
\paragraph{结果。}
\label{results.}

Sleep-time compute reduces the test-time compute needed to achieve equivalent accuracy by $\sim$$5\times$ on reasoning benchmarks. When amortized across multiple related queries about the same context, average cost per query drops by $2.5\times$. The approach is most effective when user queries are \emph{predictable}---i.e., when the context strongly constrains what questions will be asked.
睡眠时间计算在推理基准测试中将达到同等精度所需的测试时计算量减少了约 $\sim$$5\times$。当在关于同一上下文的多个相关查询中摊销时，每次查询的平均成本降低了 $2.5\times$。该方法在用户查询 \emph{可预测} 时最为有效——即当上下文强烈约束了将会被提出的问题时。

\begin{intuitionbox}[Memory Consolidation as Offline RL]
Sleep-time compute can be viewed as \emph{offline policy improvement}: during idle time, the agent improves its memory representations (policy) using the data it has already collected (past interactions), without new environment interactions. This connects to offline RL methods (Chapter~\ref{ch:po-variants}) where the agent learns from a static dataset of trajectories.
\end{intuitionbox}
\begin{intuitionbox}[记忆巩固作为离线强化学习]
睡眠时间计算可以视为 \emph{离线策略改进}：在空闲时间，智能体利用已经收集的数据（过往交互）来改进其记忆表示（策略），而无需进行新的环境交互。这与离线强化学习方法（第~\ref{ch:po-variants} 章）相关联，智能体从静态的轨迹数据集中进行学习。
\end{intuitionbox}

\subsection{A-MEM: Zettelkasten-Inspired Agentic Memory}
\subsection{A-MEM：受卡片盒笔记法启发的智能体记忆}
\label{a-mem-zettelkasten-inspired-agentic-memory}

A-MEM~\cite{xu2025amem} introduces a memory system that borrows from the \emph{Zettelkasten} method---a note-taking system based on densely interconnected atomic notes---to enable dynamic, self-organizing memory for LLM agents.
A-MEM~\cite{xu2025amem} 引入了一种记忆系统，它借鉴了 \emph{卡片盒笔记法}（Zettelkasten）——一种基于密集互连的原子笔记的笔记系统——为 LLM 智能体实现动态、自组织的记忆。

\paragraph{Key Design Principles.}
\paragraph{关键设计原则。}
\label{key-design-principles.}

\begin{itemize}
  \item \textbf{Structured notes.} Each memory entry is not a raw text chunk but a \emph{note} with multiple structured attributes: a contextual description, keywords, tags, and explicit links to related notes. This metadata enables richer retrieval than embedding similarity alone.
  \item \textbf{结构化笔记。}每个记忆条目不是原始文本块，而是一条包含多个结构化属性的 \emph{笔记}：上下文描述、关键词、标签以及指向相关笔记的显式链接。这些元数据使得检索比仅靠嵌入相似度更加丰富。
  \item \textbf{Dynamic linking.} When a new memory is added, the system analyzes existing memories to identify semantically meaningful connections and establishes bidirectional links. The result is a \emph{knowledge network} rather than a flat list.
  \item \textbf{动态链接。}当添加新记忆时，系统会分析现有记忆以识别语义上有意义的连接，并建立双向链接。结果是一个 \emph{知识网络}，而非扁平列表。
  \item \textbf{Memory evolution.} Critically, adding a new note can \emph{trigger updates} to existing notes---refining their contextual representations and attributes as the agent’s understanding deepens. This makes memory a living structure that improves over time, not a static archive.
  \item \textbf{记忆演化。}关键的是，添加新笔记可以 \emph{触发对现有笔记的更新}——随着智能体理解的加深，细化其上下文表示和属性。这使得记忆成为一个随时间改进的活结构，而不是静态存档。
  \item \textbf{Agent-driven organization.} Unlike fixed-schema memory systems, A-MEM lets the LLM itself decide how to organize, link, and update memories---making the organizational structure adaptive to the task domain.
  \item \textbf{智能体驱动的组织。}与固定模式记忆系统不同，A-MEM 让 LLM 自行决定如何组织、链接和更新记忆——使组织结构适应任务领域。
\end{itemize}

\paragraph{Results.}
\paragraph{结果。}
\label{results.-1}

Across six foundation models on multi-session reasoning tasks, A-MEM consistently outperforms flat vector stores, summarization-based memory, and graph-database approaches, demonstrating that \emph{how} memories are organized matters as much as \emph{what} is stored.
在涵盖六个基础模型的多会话推理任务中，A-MEM 始终优于平面向量存储、基于摘要的记忆和图数据库方法，证明了记忆 \emph{如何} 组织与存储 \emph{什么} 同样重要。

\section{Summary}
\section{总结}
\label{sec:memory-summary}

Agentic memory systems are a foundational component of capable AI agents, addressing the fundamental limitation of finite context windows. We have surveyed:
智能体记忆系统是强大 AI 智能体的基础组件，解决了有限上下文窗口的根本限制。我们已综述了：

\begin{itemize}
  \item A \textbf{four-way taxonomy} (working, episodic, semantic, procedural) that mirrors cognitive science and reflects distinct engineering requirements.
  \item 一个 \textbf{四路分类法}（工作记忆、情景记忆、语义记忆、程序记忆），它反映了认知科学，并体现了不同的工程需求。
  \item \textbf{Five architectural families}: RAG-based, summarization-based, graph-based, key-value networks, and tiered virtual context (MemGPT).
  \item \textbf{五种架构家族}：基于 RAG、基于摘要、基于图、键值网络和分层虚拟上下文（MemGPT）。
  \item \textbf{Four core operations}: write (with importance scoring and contradiction detection), read/retrieve (with temporal decay and query expansion), update (with conflict resolution and consolidation), and reflect (meta-cognitive insight generation).
  \item \textbf{四个核心操作}：写入（含重要性评分和矛盾检测）、读取/检索（含时间衰减和查询扩展）、更新（含冲突解决与整合）以及反思（元认知洞察生成）。
  \item \textbf{Multi-turn and multi-agent extensions}: user modeling, session continuity, shared memory pools, and blackboard architectures.
  \item \textbf{多轮与多智能体扩展}：用户建模、会话连续性、共享记忆池和黑板架构。
  \item \textbf{RL training of memory systems}: reward signals for memory operations, learning what to remember, and memory-augmented policy optimization.
  \item \textbf{记忆系统的强化学习训练}：记忆操作的奖励信号、学习记住什么内容，以及记忆增强策略优化。
\end{itemize}

The field is rapidly evolving. Key open challenges include: (1) \emph{memory grounding}---ensuring retrieved memories are faithfully incorporated rather than ignored or hallucinated over; (2) \emph{scalable consistency}---maintaining coherent shared memory in large multi-agent systems; and (3) \emph{privacy-preserving memory}---enabling personalization without compromising user data. As context windows grow, the boundary between in-context and external memory will shift, but the fundamental need for \emph{selective, structured, retrievable} information storage will remain.
该领域正在快速发展。关键开放挑战包括：(1) \emph{记忆落地}——确保检索到的记忆被忠实地整合而非被忽略或产生幻觉；(2) \emph{可扩展一致性}——在大型多智能体系统中维护连贯的共享记忆；(3) \emph{隐私保护记忆}——在不损害用户数据的前提下实现个性化。随着上下文窗口的增长，上下文内记忆与外部记忆之间的界限将会移动，但对 \emph{选择性、结构化、可检索} 信息存储的根本需求将始终存在。