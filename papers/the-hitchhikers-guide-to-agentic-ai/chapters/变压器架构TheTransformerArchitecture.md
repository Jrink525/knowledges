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


