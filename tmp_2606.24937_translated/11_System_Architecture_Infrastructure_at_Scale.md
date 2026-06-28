## Chapter: System Architecture & Infrastructure at Scale
## 章节：系统架构与规模化基础设施

Training LLMs with reinforcement learning from human feedback is as much a systems engineering challenge as it is an algorithmic one. Unlike standard supervised fine-tuning---which involves a single model, a single forward-backward pass, and well-understood scaling---RLHF requires \emph{multiple models} (policy, reference, reward model, value head) to be loaded simultaneously, coordinated through a complex rollout-scoring-training loop, and distributed across dozens to hundreds of GPUs. This chapter covers the systems-level details that make large-scale RLHF training possible: memory budgeting, parallelism strategies (Data, Tensor, Pipeline, Sequence, and their combinations), the generation bottleneck, decoupled architectures, weight synchronization, fault tolerance, and production monitoring.
使用人类反馈的强化学习训练大语言模型既是工程挑战，也是算法挑战。与标准的有监督微调（涉及单个模型、单次前向-后向传播，且扩展性已被充分理解）不同，RLHF 需要同时加载\emph{多个模型}（策略模型、参考模型、奖励模型、价值头），通过复杂的 rollout-评分-训练循环进行协调，并分布在数十到数百个 GPU 上。本章介绍使大规模 RLHF 训练成为可能的系统级细节：内存预算、并行策略（数据并行、张量并行、流水线并行、序列并行及其组合）、生成瓶颈、解耦架构、权重同步、容错和产线监控。

\section{The 4-Model Memory Challenge}
\section{4 模型内存挑战}
\label{the-4-model-memory-challenge}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_031_fig31.png}
\caption{70B PPO memory budget: the four models required for RLHF and their memory footprints. Total: 1470--1560GB. Minimum 19--20 A100-80GB (naive). With ZeRO-3: fits in 8 nodes.}
\caption{70B PPO 内存预算：RLHF 所需的四个模型及其内存占用。总计：1470--1560GB。最少需要 19--20 块 A100-80GB（朴素方案）。使用 ZeRO-3：可放入 8 个节点。}
\end{figure}

\begin{warningbox}[Memory Budget Reality Check -- 70B BF16]
\begin{warningbox}[内存预算现实核查——70B BF16]
\begin{tabular}{@{}ll@{}}
\toprule
Policy weights (BF16) & 140 GB \\
策略权重（BF16） & 140 GB \\
\midrule
FP32 master weights & 280 GB \\
FP32 主权重 & 280 GB \\
Adam optimizer (m + v, FP32) & 560 GB \\
Adam 优化器（m + v，FP32） & 560 GB \\
Gradients (BF16) & 140 GB \\
梯度（BF16） & 140 GB \\
Reference model & 140 GB (or 70 GB in INT8) \\
参考模型 & 140 GB（或 INT8 下 70 GB） \\
Reward model & 140 GB (or 70 GB in INT8) \\
奖励模型 & 140 GB（或 INT8 下 70 GB） \\
Activations (batch 128, seq 2048) & 50--100 GB \\
激活值（batch 128，seq 2048） & 50--100 GB \\
KV cache for generation & 20--60 GB \\
用于生成的 KV 缓存 & 20--60 GB \\
\textbf{Total} & \textbf{1470--1560 GB} \\
\textbf{总计} & \textbf{1470--1560 GB} \\
\bottomrule
\end{tabular}

\smallskip
$\div$ 80 GB/GPU = \textbf{19--20 A100s minimum} (without any parallelism overhead).
$\div$ 80 GB/GPU = \textbf{最少 19--20 块 A100}（未计入任何并行开销）。
\end{warningbox}

\section{Parallelism Strategies in Detail}
\section{并行策略详解}
\label{sec:parallelism}

Training large language models requires distributing computation across many GPUs. There are fundamentally different \emph{axes} along which to parallelize, each with distinct trade-offs. This section provides detailed coverage of each strategy with mathematical formulations, diagrams, and practical guidance.
训练大语言模型需要将计算分布到多个 GPU 上。存在根本不同的并行化\emph{轴}，每个轴都有不同的权衡。本节详细介绍每种策略，包括数学公式、示意图和实践指导。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_032_fig32.png}
\caption{Overview of the four parallelism strategies. Production systems typically combine 2--3 of these simultaneously.}
\caption{四种并行策略概览。生产系统通常同时组合其中 2--3 种。}
\end{figure}

\subsection{Data Parallelism (DP) and Distributed Data Parallelism (DDP)}
\subsection{数据并行 (Data Parallelism, DP) 与分布式数据并行 (Distributed Data Parallelism, DDP)}
\label{subsec:dp-ddp}

Data Parallelism is the simplest and most common form of distributed training~\cite{li2020pytorch}. Each GPU holds a \emph{complete copy} of the model, processes a different mini-batch, and synchronizes gradients.
数据并行是最简单、最常见的分布式训练形式~\cite{li2020pytorch}。每个 GPU 持有模型的\emph{完整副本}，处理不同的 mini-batch，并同步梯度。

\paragraph{Vanilla DP (PyTorch \texttt{DataParallel}).}
\paragraph{朴素 DP（PyTorch \texttt{DataParallel}）。}
\label{vanilla-dp-pytorch-dataparallel.}

A single-process approach where one ``master'' GPU scatters input, gathers outputs, and broadcasts gradients. Limited by GIL and PCIe bandwidth to the master GPU.
一种单进程方法，其中一个“主”GPU 分发输入、收集输出并广播梯度。受限于 GIL 和到主 GPU 的 PCIe 带宽。

\paragraph{Distributed Data Parallelism (DDP, \texttt{DistributedDataParallel}).}
\paragraph{分布式数据并行（DDP，\texttt{DistributedDataParallel}）。}
\label{distributed-data-parallelism-ddp-distributeddataparallel.}

Multi-process: each GPU runs its own process. Gradients are synchronized via ring-AllReduce~\cite{sergeev2018horovod} in the background while backward computation continues.
多进程：每个 GPU 运行自己的进程。梯度通过 ring-AllReduce~\cite{sergeev2018horovod} 在后台同步，同时后向计算继续进行。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_033_ddp.png}
\caption{DDP: each GPU holds a full model replica and processes a different batch. Gradients are averaged via ring AllReduce, overlapped with backward computation.}
\caption{DDP：每个 GPU 持有一个完整模型副本并处理不同的批次。梯度通过 ring AllReduce 求平均，与后向计算重叠。}
\label{fig:ddp}
\end{figure}

\textbf{Key properties of DDP}:
\textbf{DDP 的关键特性}：

\begin{itemize}
  \item \textbf{Memory}: Each GPU stores full model + optimizer + gradients. For 70B BF16: $\sim$560~GB/GPU---impossible without memory optimizations.
  \item \textbf{内存}：每个 GPU 存储完整模型 + 优化器 + 梯度。对于 70B BF16：$\sim$560~GB/GPU——没有内存优化则无法实现。
  \item \textbf{Communication}: One AllReduce of gradient tensor per step. Size = model parameters $\times$ 2 bytes (BF16). Ring AllReduce cost: $2 \cdot \frac{N-1}{N} \cdot M$ bytes transferred per GPU.
  \item \textbf{通信}：每步一次梯度张量的 AllReduce。大小 = 模型参数 $\times$ 2 字节（BF16）。Ring AllReduce 开销：每 GPU 传输 $2 \cdot \frac{N-1}{N} \cdot M$ 字节。
  \item \textbf{Scaling}: Near-linear up to $\sim$64 GPUs. Beyond that, communication starts to dominate.
  \item \textbf{扩展性}：在 $\sim$64 个 GPU 内接近线性。超出后，通信开始占主导。
  \item \textbf{Gradient bucketing}: DDP groups parameters into buckets (default 25~MB) and starts AllReduce as soon as a bucket’s gradients are ready---overlapping communication with backward computation.
  \item \textbf{梯度分桶}：DDP 将参数分组为桶（默认 25~MB），并在桶的梯度准备好后立即启动 AllReduce——使通信与后向计算重叠。
\end{itemize}

\begin{lstlisting}[style=pythonstyle]
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

dist.init_process_group(backend="nccl")  # NCCL for GPU communication
model = model.to(local_rank)
model = DDP(model, device_ids=[local_rank],
            gradient_as_bucket_view=True,    # Memory optimization
            static_graph=True)               # Enable comm optimizations
\end{lstlisting}

\begin{warningbox}[DP vs DDP — Always Use DDP]
\begin{warningbox}[DP vs DDP——始终使用 DDP]
PyTorch’s legacy \texttt{DataParallel} (DP) should \textbf{never} be used for LLM training:
PyTorch 的旧版 \texttt{DataParallel} (DP) \textbf{绝不}应被用于 LLM 训练：

\begin{itemize}
  \item Single-process, limited by Python GIL
  \item 单进程，受限于 Python GIL
  \item All gradients funnel through GPU 0 (bottleneck)
  \item 所有梯度都汇聚到 GPU 0（瓶颈）
  \item 2--3$\times$ slower than DDP even on a single node
  \item 即使在单节点上也比 DDP 慢 2--3$\times$
  \item Cannot scale beyond one machine
  \item 无法扩展到一台机器以上
\end{itemize}

DDP is the \emph{minimum} parallelism strategy. For LLMs $>$7B, FSDP/ZeRO is preferred.
DDP 是\emph{最低限度}的并行策略。对于 $>$7B 的 LLM，推荐使用 FSDP/ZeRO。
\end{warningbox}

\subsection{Tensor Parallelism (TP)}
\subsection{张量并行 (Tensor Parallelism, TP)}
\label{subsec:tensor-parallel}

Tensor Parallelism (Megatron-LM style~\cite{shoeybi2019megatron}) splits \emph{individual weight matrices} across GPUs. Each GPU computes a partial result, and an AllReduce combines them.
张量并行（Megatron-LM 风格~\cite{shoeybi2019megatron}）将\emph{单个权重矩阵}分割到多个 GPU 上。每个 GPU 计算部分结果，然后通过 AllReduce 合并。

\paragraph{Column-Parallel Linear Layer.}
\paragraph{列并行线性层。}
\label{column-parallel-linear-layer.}

The weight matrix $W \in \mathbb{R}^{d \times h}$ is split column-wise across $T$ GPUs: 
\begin{equation}
W = [W_0 \;|\; W_1 \;|\; \cdots \;|\; W_{T-1}], \quad W_i \in \mathbb{R}^{d \times h/T}
\end{equation}
 Each GPU $i$ computes $Y_i = XW_i$ independently (no communication). The output is split along the hidden dimension.
权重矩阵 $W \in \mathbb{R}^{d \times h}$ 按列分割到 $T$ 个 GPU 上：
\begin{equation}
W = [W_0 \;|\; W_1 \;|\; \cdots \;|\; W_{T-1}], \quad W_i \in \mathbb{R}^{d \times h/T}
\end{equation}
每个 GPU $i$ 独立计算 $Y_i = XW_i$（无需通信）。输出沿隐藏维度分割。

\paragraph{Row-Parallel Linear Layer.}
\paragraph{行并行线性层。}
\label{row-parallel-linear-layer.}

The weight matrix is split row-wise: $W = [W_0; W_1; \ldots; W_{T-1}]$ where $W_i \in \mathbb{R}^{d/T \times h}$. Input $X$ must also be split. Each GPU computes a partial sum, then an \textbf{AllReduce} produces the final output.
权重矩阵按行分割：$W = [W_0; W_1; \ldots; W_{T-1}]$，其中 $W_i \in \mathbb{R}^{d/T \times h}$。输入 $X$ 也必须被分割。每个 GPU 计算部分和，然后通过 \textbf{AllReduce} 生成最终输出。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_034_tp-column.png}
\caption{Column-parallel linear layer (TP=2). The weight is split column-wise; each GPU computes $XW_i$ independently. The MLP pairs this with a row-parallel layer to avoid redundant AllReduce.}
\caption{列并行线性层（TP=2）。权重按列分割；每个 GPU 独立计算 $XW_i$。MLP 将其与行并行层配对使用，以避免冗余的 AllReduce。}
\end{figure}

\paragraph{Transformer Block with TP.}
\paragraph{带有 TP 的 Transformer 块。}
\label{transformer-block-with-tp.}

In a Transformer layer, Megatron-LM applies TP as follows:
在 Transformer 层中，Megatron-LM 按以下方式应用 TP：

\begin{enumerate}
  \item \textbf{MLP}: Column-parallel for the first linear ($h \to 4h$), row-parallel for the second ($4h \to h$). One AllReduce after the row-parallel layer.
  \item \textbf{MLP}：第一个线性层（$h \to 4h$）使用列并行，第二个线性层（$4h \to h$）使用行并行。行并行层之后一次 AllReduce。
  \item \textbf{Attention}: $Q$, $K$, $V$ projections are column-parallel (split heads across GPUs). Output projection is row-parallel. One AllReduce after output projection.
  \item \textbf{注意力}：$Q$、$K$、$V$ 投影使用列并行（将注意力头分割到 GPU 上）。输出投影使用行并行。输出投影之后一次 AllReduce。
  \item \textbf{Total}: 2 AllReduce per transformer layer (one for attention, one for MLP).
  \item \textbf{总计}：每个 transformer 层 2 次 AllReduce（注意力一次，MLP 一次）。
\end{enumerate}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_035_tp-transformer.png}
\caption{Tensor Parallel communication pattern in one Transformer block. Two AllReduce operations (marked in red) are required per layer---one after attention, one after MLP.}
\caption{一个 Transformer 块中的张量并行通信模式。每层需要两次 AllReduce 操作（红色标记）——一次在注意力之后，一次在 MLP 之后。}
\label{fig:tp-transformer}
\end{figure}

\begin{intuitionbox}[Why TP is Restricted to Intra-Node]
Each transformer layer requires 2 AllReduce operations (marked as $f$ and $g$ above). For a 70B model with 80 layers, that’s 160 AllReduce operations per forward pass (320 including backward). At NVLink speeds (600~GB/s), each AllReduce takes $<$0.5~ms. But over InfiniBand (50~GB/s), the same operation takes $\sim$4~ms, making the total overhead 160 $\times$ 4 = 640~ms---\emph{longer than the computation itself}.

\textbf{Rule}: TP degree $\leq$ GPUs per node (typically TP $\leq$ 8). Use DP/FSDP for inter-node scaling.
\end{intuitionbox}

\begin{intuitionbox}[为什么 TP 限于节点内]
每个 Transformer 层需要 2 次 AllReduce 操作（上面标记为 $f$ 和 $g$）。对于一个 70B 模型，80 层，前向传播需要 160 次 AllReduce（包括反向传播则为 320 次）。在 NVLink 速度（600~GB/s）下，每次 AllReduce 耗时 $<$0.5~ms。但在 InfiniBand（50~GB/s）上，同样的操作耗时约 $\sim$4~ms，使得总开销为 160 $\times$ 4 = 640~ms——\emph{比计算本身还长}。

\textbf{规则}：TP 度数 $\leq$ 每节点 GPU 数（通常 TP $\leq$ 8）。跨节点扩展使用 DP/FSDP。
\end{intuitionbox}

\begin{keybox}[TP Degree Selection]
\begin{itemize}
  \item \textbf{TP=1}: No tensor parallelism. Model fits on one GPU (typically $\leq$ 13B with BF16).
  \item \textbf{TP=2}: Minimal split. Good for 13--34B inference on 2 GPUs. Low overhead ($<$5\%).
  \item \textbf{TP=4}: Standard for 34--70B inference. Overhead 8--12\%.
  \item \textbf{TP=8}: Full node. Required for 70B+ training. Overhead 12--18\%.
  \item \textbf{TP$>$8}: Cross-node TP. Rarely used---only for 200B+ models where PP alone is insufficient. Overhead 30--50\%.
\end{itemize}


\textbf{Important}: Number of attention heads must be divisible by TP degree. For LLaMA-70B (64 heads), valid TP = 1, 2, 4, 8, 16, 32, 64.
\end{keybox}

\begin{keybox}[TP 度数选择]
\begin{itemize}
  \item \textbf{TP=1}：无张量并行。模型可放入单个 GPU（通常 $\leq$ 13B，BF16 下）。
  \item \textbf{TP=2}：最小拆分。适用于 13--34B 模型在 2 个 GPU 上推理。开销低（$<$5\%）。
  \item \textbf{TP=4}：34--70B 推理的标准选择。开销 8--12\%。
  \item \textbf{TP=8}：完整节点。70B+ 训练所需。开销 12--18\%。
  \item \textbf{TP$>$8}：跨节点 TP。很少使用——仅用于 200B+ 模型且单独 PP 不够的情况。开销 30--50\%。
\end{itemize}

\textbf{重要}：注意力头数必须能被 TP 度数整除。对于 LLaMA-70B（64 个头），有效 TP = 1, 2, 4, 8, 16, 32, 64。
\end{keybox}

\subsection{Sequence Parallelism (SP)}
\label{subsec:sequence-parallel}

\subsection{序列并行 (SP)}
\label{subsec:sequence-parallel}

Sequence Parallelism~\cite{korthikanti2023reducing} addresses a memory bottleneck that Tensor Parallelism alone cannot solve: the \textbf{activation memory} in LayerNorm and Dropout layers.

序列并行~\cite{korthikanti2023reducing} 解决了仅靠张量并行无法解决的内存瓶颈：LayerNorm 和 Dropout 层中的\textbf{激活内存}。

\paragraph{The Problem.}
\label{the-problem.}

\paragraph{问题。}
\label{the-problem.}

With TP, weight memory is split across GPUs. But LayerNorm and Dropout operate on the \emph{full} hidden dimension and are replicated on every GPU. Their activations (needed for backward pass) consume memory proportional to $b \times s \times d$---the same on every GPU, unreduced by TP.

使用 TP 时，权重内存分布在多个 GPU 上。但 LayerNorm 和 Dropout 在\emph{完整}隐藏维度上操作，并且在每个 GPU 上被复制。它们的激活（反向传播所需）消耗的内存与 $b \times s \times d$ 成正比——在每个 GPU 上相同，TP 无法减少。

\paragraph{The Solution.}
\label{the-solution.}

\paragraph{解决方案。}
\label{the-solution.}

Split the \emph{sequence dimension} for operations that don’t require cross-GPU communication (LayerNorm, Dropout, residual connections). Each GPU processes a $s/T$ slice of the sequence for these operations, then gathers the full sequence only where needed (attention, linear layers).

对于不需要跨 GPU 通信的操作（LayerNorm、Dropout、残差连接），沿\emph{序列维度}进行拆分。每个 GPU 处理序列的 $s/T$ 切片用于这些操作，然后仅在需要的地方（注意力、线性层）收集完整序列。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_036_seq-parallel.png}
\caption{Sequence Parallelism reduces activation memory for LayerNorm/Dropout by splitting along the sequence dimension. Communication (AllGather/ReduceScatter) replaces the AllReduce used in standard TP---same total bytes transferred, but memory is saved.}
\label{fig:seq-parallel}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_036_seq-parallel.png}
\caption{序列并行通过沿序列维度拆分，减少了 LayerNorm/Dropout 的激活内存。通信（AllGather/ReduceScatter）取代了标准 TP 中使用的 AllReduce——传输的总字节数相同，但节省了内存。}
\label{fig:seq-parallel}
\end{figure}

\begin{intuitionbox}[SP Communication is ``Free'']
Standard TP uses AllReduce after each sub-layer, which is equivalent to ReduceScatter + AllGather. SP simply \emph{reorders} these primitives:


\begin{itemize}
  \item TP without SP: AllReduce (= ReduceScatter + AllGather) $\rightarrow$ same data on all GPUs $\rightarrow$ LayerNorm on full tensor (wasteful).
  \item TP with SP: ReduceScatter $\rightarrow$ each GPU has $1/T$ of sequence $\rightarrow$ LayerNorm on partial tensor $\rightarrow$ AllGather before next TP layer.
\end{itemize}


The total communication volume is identical! SP is purely a memory optimization with \textbf{zero additional communication cost}. It should always be enabled when using TP.
\end{intuitionbox}

\begin{intuitionbox}[SP 通信是“免费”的]
标准 TP 在每个子层后使用 AllReduce，这等价于 ReduceScatter + AllGather。SP 只是\emph{重新排列}了这些原语：

\begin{itemize}
  \item 无 SP 的 TP：AllReduce（= ReduceScatter + AllGather）$\rightarrow$ 所有 GPU 上相同的数据 $\rightarrow$ 对完整张量进行 LayerNorm（浪费）。
  \item 有 SP 的 TP：ReduceScatter $\rightarrow$ 每个 GPU 拥有序列的 $1/T$ $\rightarrow$ 对部分张量进行 LayerNorm $\rightarrow$ 在下一个 TP 层之前进行 AllGather。
\end{itemize}

总通信量完全相同！SP 纯粹是一种内存优化，\textbf{额外通信成本为零}。使用 TP 时应始终启用它。
\end{intuitionbox}

\textbf{Memory savings from SP (70B model, TP=8, batch=4, seq=2048)}: 
\begin{equation}
\text{Activation savings} = (T-1) \times b \times s \times d \times n_\text{layers} \times 2\text{ bytes} = 7 \times 4 \times 2048 \times 8192 \times 80 \times 2 \approx \textbf{59 GB/GPU}
\end{equation}

\textbf{SP 节省的内存（70B 模型，TP=8，batch=4，seq=2048）}：
\begin{equation}
\text{激活节省} = (T-1) \times b \times s \times d \times n_\text{layers} \times 2\text{ 字节} = 7 \times 4 \times 2048 \times 8192 \times 80 \times 2 \approx \textbf{59 GB/GPU}
\end{equation}

\subsection{Pipeline Parallelism (PP)}
\label{subsec:pipeline-parallel}

\subsection{流水线并行 (PP)}
\label{subsec:pipeline-parallel}

Pipeline Parallelism splits the model \emph{vertically} by layers, assigning consecutive groups of layers to different devices (stages). Activations flow forward through stages; gradients flow backward.

流水线并行按层\emph{垂直}拆分模型，将连续的层组分配给不同的设备（阶段）。激活向前流经各阶段；梯度向后传播。

\paragraph{The Bubble Problem.}
\label{the-bubble-problem.}

\paragraph{气泡问题。}
\label{the-bubble-problem.}

Naive pipeline execution creates ``bubbles''---idle time while a stage waits for input from the previous stage or gradients from the next:

朴素流水线执行会产生“气泡”阶段——即当一个阶段等待上一阶段的输入或下一阶段的梯度时的空闲时间：

\begin{figure}[ht!]
\centering
\includegraphics[width=0.95\textwidth]{figures/fig_037_pipeline-bubble.png}
\caption{Pipeline bubble comparison. Left: naive pipeline with one micro-batch has 75\% idle time. Right: GPipe with $M=4$ micro-batches reduces bubbles significantly. With $M \gg P$, bubble fraction approaches zero.}
\label{fig:pipeline-bubble}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.95\textwidth]{figures/fig_037_pipeline-bubble.png}
\caption{流水线气泡比较。左图：一个微批次的朴素流水线有 75\% 的空闲时间。右图：使用 $M=4$ 个微批次的 GPipe 显著减少了气泡。当 $M \gg P$ 时，气泡比例趋近于零。}
\label{fig:pipeline-bubble}
\end{figure}

\paragraph{Bubble Fraction Formula.}
\label{bubble-fraction-formula.}

\paragraph{气泡比例公式。}
\label{bubble-fraction-formula.}

For $P$ pipeline stages and $M$ micro-batches per step: 
\begin{equation}
\text{Bubble fraction} = \frac{P - 1}{P + M - 1} \approx \frac{P-1}{M} \quad \text{(when } M \gg P\text{)}
\end{equation}

对于 $P$ 个流水线阶段和每步 $M$ 个微批次：
\begin{equation}
\text{气泡比例} = \frac{P - 1}{P + M - 1} \approx \frac{P-1}{M} \quad \text{（当 } M \gg P \text{ 时）}
\end{equation}

To keep bubble overhead $<$10\%, you need $M \geq 10 \cdot (P-1)$. For PP=4: at least 30 micro-batches.

为了保持气泡开销 $<$10\%，需要 $M \geq 10 \cdot (P-1)$。对于 PP=4：至少 30 个微批次。

\paragraph{Pipeline Schedules.}
\label{pipeline-schedules.}

\paragraph{流水线调度策略。}
\label{pipeline-schedules.}

\begin{table}[ht!]
\centering
\caption{Pipeline scheduling strategies}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{Schedule} & \textbf{Bubble} & \textbf{Memory} & \textbf{Characteristics} \\
\midrule
GPipe & $\frac{P-1}{M+P-1}$ & $M \times$ activations & Simple; all-forward then all-backward~\cite{huang2019gpipe} \\
1F1B & $\frac{P-1}{M+P-1}$ & $P \times$ activations & Interleaved; steady-state memory bounded~\cite{narayanan2019pipedream} \\
Interleaved 1F1B & $\frac{P-1}{M \cdot V + P - 1}$ & $P \times$ activations & Virtual stages ($V$); further reduces bubble~\cite{narayanan2021efficient} \\
Zero-Bubble (ZB-H1) & $\approx 0$ & $P \times$ activations & Splits backward into B and W phases~\cite{qi2023zerobubble} \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[ht!]
\centering
\caption{流水线调度策略}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{调度策略} & \textbf{气泡} & \textbf{内存} & \textbf{特性} \\
\midrule
GPipe & $\frac{P-1}{M+P-1}$ & $M \times$ 激活 & 简单；全部前向然后全部反向~\cite{huang2019gpipe} \\
1F1B & $\frac{P-1}{M+P-1}$ & $P \times$ 激活 & 交错；稳态内存有界~\cite{narayanan2019pipedream} \\
Interleaved 1F1B & $\frac{P-1}{M \cdot V + P - 1}$ & $P \times$ 激活 & 虚拟阶段 ($V$)；进一步减少气泡~\cite{narayanan2021efficient} \\
Zero-Bubble (ZB-H1) & $\approx 0$ & $P \times$ 激活 & 将反向拆分为 B 和 W 阶段~\cite{qi2023zerobubble} \\
\bottomrule
\end{tabular}
\end{table}

\begin{intuitionbox}[1F1B: The Production Standard]
The \textbf{1F1B} (one-forward-one-backward) schedule~\cite{narayanan2019pipedream} is used in most production systems (Megatron-LM~\cite{narayanan2021efficient}, DeepSpeed~\cite{rajbhandari2020zero}):


\textbf{Warmup}: Forward passes fill the pipeline (P-1 micro-batches).


\textbf{Steady state}: Alternate one forward and one backward per time slot. This bounds peak activation memory to $P$ micro-batches (vs $M$ for GPipe).


\textbf{Cooldown}: Remaining backward passes drain the pipeline.


\textbf{Memory advantage}: GPipe must store activations for \emph{all} $M$ micro-batches simultaneously. 1F1B only stores $P$ sets of activations at steady state---critical when $M = 32$ but $P = 4$.
\end{intuitionbox}

\begin{intuitionbox}[1F1B：生产标准]
\textbf{1F1B}（一个前向一个反向）调度~\cite{narayanan2019pipedream} 用于大多数生产系统（Megatron-LM~\cite{narayanan2021efficient}、DeepSpeed~\cite{rajbhandari2020zero}）：

\textbf{预热}：前向传播填充流水线（P-1 个微批次）。

\textbf{稳态}：每个时隙交替执行一个前向和一个反向。这使峰值激活内存限制在 $P$ 个微批次（对比 GPipe 的 $M$ 个）。

\textbf{冷却}：剩余反向传播排空流水线。

\textbf{内存优势}：GPipe 必须同时存储\emph{所有} $M$ 个微批次的激活。1F1B 在稳态下仅存储 $P$ 组激活——当 $M = 32$ 但 $P = 4$ 时至关重要。
\end{intuitionbox}

\paragraph{Communication in PP.}
\label{communication-in-pp.}

\paragraph{PP 中的通信。}
\label{communication-in-pp.}

Unlike TP (AllReduce), PP only requires \textbf{point-to-point} communication of activations between adjacent stages: 
\begin{equation}
\text{Data per transfer} = b_\text{micro} \times s \times d \times 2\text{ bytes (BF16)}
\end{equation}
 For micro-batch=4, seq=2048, $d$=8192: $4 \times 2048 \times 8192 \times 2 = 128$~MB per transfer. At InfiniBand 50~GB/s: 2.6~ms per transfer---small relative to compute per stage.

与 TP（AllReduce）不同，PP 只需要相邻阶段之间激活的\textbf{点对点}通信：
\begin{equation}
\text{每次传输的数据量} = b_\text{micro} \times s \times d \times 2\text{ 字节 (BF16)}
\end{equation}
对于微批次=4，seq=2048，$d$=8192：每次传输 $4 \times 2048 \times 8192 \times 2 = 128$~MB。在 InfiniBand 50~GB/s 下：每次传输 2.6~ms——相对于每个阶段的计算量很小。

\paragraph{Load Balancing.}
\label{load-balancing.}

\paragraph{负载均衡。}
\label{load-balancing.}

Not all layers have equal compute:


\begin{itemize}
  \item \textbf{Embedding layer}: Very cheap (lookup table).
  \item \textbf{Transformer blocks}: Uniform compute.
  \item \textbf{Final LM head}: Moderate (large matrix multiply for vocabulary projection).
\end{itemize}


Assign more transformer layers to middle stages and fewer to the first/last stages to balance compute.

并非所有层具有相同的计算量：

\begin{itemize}
  \item \textbf{嵌入层}：非常轻量（查找表）。
  \item \textbf{Transformer 块}：统一的计算量。
  \item \textbf{最终 LM 头}：中等（用于词汇投影的大矩阵乘法）。
\end{itemize}

将更多 Transformer 层分配给中间阶段，更少分配给第一个/最后一个阶段，以平衡计算。

\subsection{Fully Sharded Data Parallelism (FSDP / ZeRO-3)}
\label{fully-sharded-data-parallelism-fsdp-zero-3}

\subsection{全分片数据并行 (FSDP / ZeRO-3)}
\label{fully-sharded-data-parallelism-fsdp-zero-3}

FSDP~\cite{zhao2023pytorch} (PyTorch) and ZeRO-3~\cite{rajbhandari2020zero} (DeepSpeed) address the memory duplication inherent in DDP: instead of every GPU holding a full copy of parameters, gradients, and optimizer states, each GPU owns only a $1/N$ slice and reconstructs the full tensor on-the-fly when needed.

FSDP~\cite{zhao2023pytorch}（PyTorch）和 ZeRO-3~\cite{rajbhandari2020zero}（DeepSpeed）解决了 DDP 中固有的内存重复问题：每个 GPU 不再持有参数、梯度和优化器状态的完整副本，而是每个 GPU 仅拥有 $1/N$ 的分片，并在需要时动态重建完整张量。

```markdown
\begin{figure}[ht!]
\centering
\includegraphics[width=0.95\textwidth]{figures/fig_038_fsdp.png}
\caption{FSDP shards all model state across GPUs. Each GPU owns $1/N$ of parameters, optimizer states, and gradients. Full parameters are reconstructed on-demand via AllGather before each layer’s computation.}
\label{fig:fsdp}
\end{figure}
\begin{figure}[ht!]
\centering
\includegraphics[width=0.95\textwidth]{figures/fig_038_fsdp.png}
\caption{FSDP将全部模型状态分片到各GPU上。每个GPU拥有参数的$1/N$、优化器状态和梯度。完整参数在每层计算前通过AllGather按需重建。}
\label{fig:fsdp}
\end{figure}

\textbf{FSDP execution flow per layer:}
**FSDP每层执行流程：**

\begin{enumerate}
  \item \textbf{Forward}: AllGather parameters $\rightarrow$ compute $\rightarrow$ discard non-owned shards.
  \item \textbf{前向}: AllGather参数 $\rightarrow$ 计算 $\rightarrow$ 丢弃非本地的分片。
  \item \textbf{Backward}: AllGather parameters (again) $\rightarrow$ compute gradients $\rightarrow$ ReduceScatter gradients (each GPU gets its gradient shard) $\rightarrow$ discard non-owned parameter shards.
  \item \textbf{后向}: AllGather参数（再次） $\rightarrow$ 计算梯度 $\rightarrow$ ReduceScatter梯度（每个GPU得到其梯度分片） $\rightarrow$ 丢弃非本地的参数分片。
  \item \textbf{Optimizer step}: Each GPU updates only its owned shard using its gradient shard and optimizer states.
  \item \textbf{优化器步}: 每个GPU仅使用其梯度分片和优化器状态更新其拥有的分片。
\end{enumerate}

\begin{table}[ht!]
\centering
\caption{Memory comparison: DDP vs FSDP/ZeRO stages (70B model, 8 GPUs). Baseline: BF16 params (140 GB) + BF16 grads (140 GB) + FP32 master+m+v (840 GB) = 1120 GB per GPU.}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{Strategy} & \textbf{Sharded} & \textbf{Memory/GPU} & \textbf{Communication} \\
\midrule
DDP (no sharding) & Nothing & 1120 GB $\times$ & AllReduce (gradients only) \\
ZeRO-1 & Optimizer states & 385 GB $\times$ & AllReduce (gradients) \\
ZeRO-2 & Optimizer + gradients & 368 GB $\times$ & AllReduce (gradients) \\
ZeRO-3 / FSDP & Everything & \textbf{140 GB} \checkmark{} & AllGather + ReduceScatter (per layer) \\
\bottomrule
\end{tabular}
\end{table}
\begin{table}[ht!]
\centering
\caption{内存对比：DDP 与 FSDP/ZeRO 阶段（70B模型，8 GPU）。基线：BF16参数（140 GB）+ BF16梯度（140 GB）+ FP32主副本+m+v（840 GB）= 每GPU 1120 GB。}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{策略} & \textbf{分片内容} & \textbf{每GPU内存} & \textbf{通信} \\
\midrule
DDP（不分片） & 无 & 1120 GB $\times$ & AllReduce（仅梯度） \\
ZeRO-1 & 优化器状态 & 385 GB $\times$ & AllReduce（梯度） \\
ZeRO-2 & 优化器 + 梯度 & 368 GB $\times$ & AllReduce（梯度） \\
ZeRO-3 / FSDP & 全部 & \textbf{140 GB} \checkmark{} & AllGather + ReduceScatter（每层） \\
\bottomrule
\end{tabular}
\end{table}

\begin{lstlisting}[style=pythonstyle]
from functools import partial
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp import ShardingStrategy, MixedPrecision, BackwardPrefetch
from torch.distributed.fsdp.wrap import transformer_auto_wrap_policy
from transformers.models.llama.modeling_llama import LlamaDecoderLayer


# Wrap model with FSDP
auto_wrap = partial(transformer_auto_wrap_policy,
                    transformer_layer_cls={LlamaDecoderLayer})
mp_policy = MixedPrecision(
    param_dtype=torch.bfloat16,
    reduce_dtype=torch.bfloat16,
    buffer_dtype=torch.bfloat16,
)


model = FSDP(
    model,
    sharding_strategy=ShardingStrategy.FULL_SHARD,  # ZeRO-3
    mixed_precision=mp_policy,
    auto_wrap_policy=auto_wrap,  # Wrap each transformer layer
    use_orig_params=True,        # Required for torch.compile compatibility
    limit_all_gathers=True,      # Bound peak memory (1 AllGather in flight at a time)
    forward_prefetch=True,       # Prefetch next layer's params during current layer
    backward_prefetch=BackwardPrefetch.BACKWARD_PRE,  # Prefetch during backward
)
\end{lstlisting}
\begin{lstlisting}[style=pythonstyle]
from functools import partial
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp import ShardingStrategy, MixedPrecision, BackwardPrefetch
from torch.distributed.fsdp.wrap import transformer_auto_wrap_policy
from transformers.models.llama.modeling_llama import LlamaDecoderLayer


# 使用FSDP包裹模型
auto_wrap = partial(transformer_auto_wrap_policy,
                    transformer_layer_cls={LlamaDecoderLayer})
mp_policy = MixedPrecision(
    param_dtype=torch.bfloat16,
    reduce_dtype=torch.bfloat16,
    buffer_dtype=torch.bfloat16,
)


model = FSDP(
    model,
    sharding_strategy=ShardingStrategy.FULL_SHARD,  # ZeRO-3
    mixed_precision=mp_policy,
    auto_wrap_policy=auto_wrap,  # 包裹每个Transformer层
    use_orig_params=True,        # 需要与torch.compile兼容
    limit_all_gathers=True,      # 限制峰值内存（同一时间只有一个AllGather在执行）
    forward_prefetch=True,       # 在当前层预取下一层的参数
    backward_prefetch=BackwardPrefetch.BACKWARD_PRE,  # 在后向过程中预取
)
\end{lstlisting}

\begin{warningbox}[FSDP Communication Volume]
FSDP communicates \textbf{3$\times$ more data} than DDP per step:


\begin{itemize}
  \item DDP: 1 AllReduce of gradients = $2M$ bytes total across ring (where $M$ = model size in bytes).
  \item FSDP: 2 AllGather (forward + backward) + 1 ReduceScatter = $3M$ bytes.
\end{itemize}


This is the memory--communication trade-off. FSDP is worthwhile when: (a) model doesn’t fit in GPU memory with DDP, or (b) communication is well-overlapped with compute (modern frameworks achieve 70--90\% overlap).
\end{warningbox}
\begin{warningbox}[FSDP通信量]
FSDP每步通信量比DDP多\textbf{3倍}：


\begin{itemize}
  \item DDP: 1次梯度AllReduce = ring中总计 $2M$ 字节（其中 $M$ = 模型大小，以字节计）。
  \item FSDP: 2次AllGather（前向+后向）+ 1次ReduceScatter = $3M$ 字节。
\end{itemize}


这是内存与通信的权衡。FSDP在以下情况有价值：(a) 模型无法在DDP下放入GPU内存，或 (b) 通信能与计算良好重叠（现代框架可实现70–90%的重叠）。
\end{warningbox}

\subsection{3D Parallelism: Combining Strategies}
\subsection{3D并行：组合策略}
\label{subsec:3d-parallel}


Production systems at scale (70B+) combine TP, PP, and DP/FSDP simultaneously:


\begin{figure}[ht!]
\centering
\includegraphics[width=0.95\textwidth]{figures/fig_039_3d-parallel.png}
\caption{3D parallelism layout for 16 GPUs: TP=4 (within each box, using NVLink), PP=2 (orange arrows, stages), DP=2 (red arrows, gradient sync). Each dimension exploits a different level of the communication hierarchy.}
\label{fig:3d-parallel}
\end{figure}
\begin{figure}[ht!]
\centering
\includegraphics[width=0.95\textwidth]{figures/fig_039_3d-parallel.png}
\caption{16 GPU的3D并行布局：TP=4（每个框内，使用NVLink），PP=2（橙色箭头，阶段），DP=2（红色箭头，梯度同步）。每个维度利用通信层次结构的不同层级。}
\label{fig:3d-parallel}
\end{figure}

\begin{keybox}[Production Recipe: 70B on 64 A100-80GB (8 nodes)]
\textbf{Intra-node} (NVLink 600GB/s): TP=8 for generation, FSDP within node for training.\\


\textbf{Inter-node} (InfiniBand 400Gb/s): FSDP across nodes (8-way data parallel).\\


\textbf{Result}: Each GPU holds $\sim$70GB. Policy weights gathered per-layer during forward/backward.\\


\textbf{Pipeline Parallel}: Only if model exceeds 100B+ and won’t fit with TP+ZeRO. Adds complexity (bubble overhead 10--20\%) and scheduling headaches.


\textbf{Decision flowchart}:


\begin{enumerate}
  \item Does the model fit on 1 GPU? $\rightarrow$ Use DDP.
  \item Does it fit on 1 node with FSDP? $\rightarrow$ Use FSDP (ZeRO-3).
  \item Does it fit on 1 node with TP+FSDP? $\rightarrow$ Use TP (intra-node) + FSDP (inter-node).
  \item Still doesn’t fit? $\rightarrow$ Add PP across nodes. This is the last resort.
\end{enumerate}
\end{keybox}
\begin{keybox}[生产配方：70B模型在64个A100-80GB上（8节点）]
\textbf{节点内}（NVLink 600GB/s）：生成时TP=8，训练时节点内FSDP。\\


\textbf{节点间}（InfiniBand 400Gb/s）：跨节点FSDP（8路数据并行）。\\


\textbf{结果}：每个GPU持有$\sim$70GB。前向/后向时每层收集策略权重。\\


\textbf{流水线并行}：仅当模型超过100B+且TP+ZeRO放不下时使用。增加复杂性（气泡开销10–20%）和调度难题。


\textbf{决策流程图}：


\begin{enumerate}
  \item 模型能否放进1个GPU？ $\rightarrow$ 使用DDP。
  \item 能否放进1个节点（带FSDP）？ $\rightarrow$ 使用FSDP（ZeRO-3）。
  \item 能否放进1个节点（带TP+FSDP）？ $\rightarrow$ 使用TP（节点内）+ FSDP（节点间）。
  \item 仍然放不下？ $\rightarrow$ 跨节点添加PP。这是最后的手段。
\end{enumerate}
\end{keybox}

\begin{table}[ht!]
\centering
\caption{Parallelism strategy comparison summary}
{\footnotesize
\begin{tabular}{@{}llllll@{}}
\toprule
\textbf{Strategy} & \textbf{Splits} & \textbf{Communication} & \textbf{Scaling Limit} & \textbf{Overhead} & \textbf{When to Use} \\
\midrule
DP/DDP & Batch & AllReduce (grads) & $\sim$64 GPUs & 5--10\% & Model fits on 1 GPU \\
FSDP & Params+Opt+Grad & AllGather+RS & 100s of GPUs & 10--20\% & Default for $>$13B \\
TP & Weight matrices & AllReduce (2/layer) & 8 GPUs (1 node) & 12--18\% & Large model inference+train \\
SP & Activations (seq) & Reuses TP comms & Same as TP & $\approx$0\% extra & Always with TP \\
PP & Layers (stages) & Point-to-point & $\sim$16 stages & 15--30\% & 100B+ models only \\
\bottomrule
\end{tabular}
}
\end{table}
\begin{table}[ht!]
\centering
\caption{并行策略对比总结}
{\footnotesize
\begin{tabular}{@{}llllll@{}}
\toprule
\textbf{策略} & \textbf{切分内容} & \textbf{通信方式} & \textbf{扩展限制} & \textbf{开销} & \textbf{何时使用} \\
\midrule
DP/DDP & 批次 & AllReduce（梯度） & $\sim$64 GPU & 5--10\% & 模型可放进1个GPU \\
FSDP & 参数+优化器+梯度 & AllGather+RS & 数百GPU & 10--20\% & $>$13B模型的默认选择 \\
TP & 权重矩阵 & AllReduce（每层2次） & 8 GPU（1节点） & 12--18\% & 大型模型推理+训练 \\
SP & 激活（序列维） & 复用TP通信 & 同TP & $\approx$0\%额外 & 总是与TP一起使用 \\
PP & 层（阶段） & 点对点 & $\sim$16阶段 & 15--30\% & 仅限100B+模型 \\
\bottomrule
\end{tabular}
}
\end{table}

\section{The Generation Bottleneck: Quantitative Analysis}
\section{生成瓶颈：定量分析}
\label{the-generation-bottleneck-quantitative-analysis}


\begin{intuitionbox}[Roofline Analysis: Why Generation is Memory-Bound]
\textbf{A100 specs}: 312 TFLOPS (BF16 tensor cores), 2 TB/s HBM bandwidth.


\textbf{Roofline crossover}: $312\text{T} / 2\text{T} = 156$ FLOP/byte. Operations below 156 FLOP/byte are \emph{memory-bound}.


\textbf{Autoregressive generation}: For each token, read all weights (140GB for 70B) and do $2 \times 70\text{B} = 140\text{G}$ FLOPs per token (at batch=1).


\textbf{Arithmetic intensity}: $140\text{G FLOP} / 140\text{GB} = 1$ FLOP/byte. That’s $156\times$ below the roofline!


\textbf{Utilization}: $1/156 = 0.6\%$ of peak FLOPS utilized. The GPU is 99.4\% idle, waiting for memory reads.


\textbf{Token rate}: $2\text{TB/s} / 140\text{GB} = 14.3$ tokens/second (single stream, batch=1).


\textbf{For 512 tokens}: $512 / 14.3 = 35.8$ seconds per response (batch=1, TP=1).


\textbf{Batching helps}: Batch=64 with TP=4 $\rightarrow$ reads weights once, generates 64 tokens in parallel. Arithmetic intensity: $64 \times 1 = 64$ FLOP/byte. Better, but still below roofline!
\end{intuitionbox}
\begin{intuitionbox}[屋顶线分析：为什么生成是内存受限的]
\textbf{A100规格}：312 TFLOPS（BF16张量核心），2 TB/s HBM带宽。


\textbf{屋顶线交叉点}：$312\text{T} / 2\text{T} = 156$ FLOP/字节。低于156 FLOP/字节的操作是\emph{内存受限}的。


\textbf{自回归生成}：每个token需要读取所有权重（70B模型需要140GB），每token执行$2 \times 70\text{B} = 140\text{G}$ FLOPs（batch=1时）。


\textbf{算术强度}：$140\text{G FLOP} / 140\text{GB} = 1$ FLOP/字节。比屋顶线低156倍！


\textbf{利用率}：仅使用峰值FLOPS的$1/156 = 0.6\%$。GPU有99.4\%空闲，等待内存读取。


\textbf{Token速率}：$2\text{TB/s} / 140\text{GB} = 14.3$ tokens/秒（单流，batch=1）。


\textbf{生成512个token}：$512 / 14.3 = 35.8$ 秒每次响应（batch=1，TP=1）。


\textbf{批处理有帮助}：Batch=64且TP=4 $\rightarrow$ 读取一次权重，并行生成64个token。算术强度：$64 \times 1 = 64$ FLOP/字节。有所改善，但仍低于屋顶线！
\end{intuitionbox}

\begin{table}[ht!]
\centering
\caption{Generation throughput for 70B model (512 tokens, various configurations)}
{\footnotesize
\begin{tabular}{@{}lllll@{}}
\toprule
\textbf{Config} & \textbf{Batch} & \textbf{Time/batch} & \textbf{Tok/s/GPU} & \textbf{Notes} \\
\midrule
TP=1, batch=1 & 1 & 36s & 14 & Baseline, worst case \\
TP=4, batch=1 & 1 & 9s & 57 & Linear TP scaling for gen \\
TP=4, batch=32 & 32 & 15s & 1092 & Near-optimal batching \\
TP=4, batch=128, vLLM & 128 & 45s & 1456 & Continuous batching \\
TP=4, batch=128, INT8 & 128 & 25s & 2621 & 2$\times$ bandwidth savings \\
\bottomrule
\end{tabular}
}
\end{table}
\begin{table}[ht!]
\centering
\caption{70B模型生成吞吐量（512 token，不同配置）}
{\footnotesize
\begin{tabular}{@{}lllll@{}}
\toprule
\textbf{配置} & \textbf{Batch} & \textbf{每批时间} & \textbf{Tok/s/GPU} & \textbf{备注} \\
\midrule
TP=1, batch=1 & 1 & 36s & 14 & 基线，最差情况 \\
TP=4, batch=1 & 1 & 9s & 57 & 生成时TP线性扩展 \\
TP=4, batch=32 & 32 & 15s & 1092 & 近乎最优的批处理 \\
TP=4, batch=128, vLLM & 128 & 45s & 1456 & 连续批处理 \\
TP=4, batch=128, INT8 & 128 & 25s & 2621 & 带宽节省2倍 \\
\bottomrule
\end{tabular}
}
\end{table}

\textbf{Optimization stack} (cumulative speedup):
**优化栈**（累积加速比）：
```

## vLLM + PagedAttention~~\cite{kwon2023efficient} (2--4$\times$)：消除 KV 缓存碎片，支持更大的批次
## vLLM + PagedAttention~~\cite{kwon2023efficient} (2--4$\times$)：消除 KV 缓存碎片，支持更大的批次

\item \textbf{Continuous batching}~\cite{yu2022orca} (1.5--2$\times$): Don’t wait for longest sequence; start new ones as others finish
\item \textbf{连续批处理}~\cite{yu2022orca} (1.5--2$\times$)：不等最长的序列；当其他序列完成时启动新序列

\item \textbf{Speculative decoding}~\cite{leviathan2023fast} (2--3$\times$): Small draft model proposes 5 tokens, large model verifies in one forward pass. Accept 3--4 on average.
\item \textbf{推测解码}~\cite{leviathan2023fast} (2--3$\times$)：小型草稿模型提出 5 个 token，大型模型一次前向传播验证。平均接受 3--4 个。

\item \textbf{INT8/FP8 weights for gen} (2$\times$): Halve bandwidth needs. Quality loss is minimal since we’re sampling (not computing exact logits for training)
\item \textbf{生成时使用 INT8/FP8 权重} (2$\times$)：带宽需求减半。质量损失极小，因为我们进行采样（而非为训练计算精确 logits）

\item \textbf{CUDA graphs} (1.1--1.3$\times$): Eliminate kernel launch overhead for fixed-shape operations
\item \textbf{CUDA 图} (1.1--1.3$\times$)：消除固定形状操作的内核启动开销

\item \textbf{Prefix caching} (1.5$\times$ for shared-prefix prompts): Don’t recompute system prompt KV cache
\item \textbf{前缀缓存}（共享前缀提示词可达 1.5$\times$）：不重新计算系统提示词的 KV 缓存
\end{enumerate}

```python
# Production vLLM generation setup
# 生产环境 vLLM 生成设置
from vllm import LLM, SamplingParams


engine = LLM(
    model="./policy_checkpoint",
    tensor_parallel_size=4,           # TP=4 per instance
                                       # 每个实例 TP=4
    gpu_memory_utilization=0.92,      # Leave headroom for KV cache
                                       # 为 KV 缓存预留空间
    max_num_batched_tokens=16384,     # Max tokens in flight
                                       # 飞行中的最大 token 数
    max_num_seqs=256,                 # Max concurrent sequences
                                       # 最大并发序列数
    dtype="bfloat16",
    enable_prefix_caching=True,       # Cache system prompt KV
                                       # 缓存系统提示词的 KV
    speculative_model="./draft_1B",   # Speculative decoding
                                       # 推测解码
    num_speculative_tokens=5,
    block_size=16,                    # PagedAttention block size
                                       # PagedAttention 块大小
    swap_space=4,                     # GB swap space for preemption
                                       # 用于抢占的交换空间（GB）
)


# Generate responses for RLHF batch
# 为 RLHF 批次生成响应
sampling_params = SamplingParams(
    temperature=0.7, top_p=0.9, max_tokens=512,
    logprobs=1,  # Need log-probs for PPO ratio calculation
                  # 需要对数概率用于 PPO 比率计算
)
outputs = engine.generate(prompts, sampling_params)
# Extract: responses, log_probs for each token (needed for PPO/GRPO)
# 提取：每个 token 的响应、对数概率（PPO/GRPO 需要）
```

## Decoupled Architecture: Production Design
## 解耦架构：生产环境设计
\label{decoupled-architecture-production-design}

Production RLHF systems such as DeepSpeed-Chat~\cite{yao2023deepspeedchat} and OpenRLHF~\cite{hu2024openrlhf} use a \textbf{decoupled architecture} that separates generation, scoring, and training into independently scalable clusters.
生产环境中的 RLHF 系统，如 DeepSpeed-Chat~\cite{yao2023deepspeedchat} 和 OpenRLHF~\cite{hu2024openrlhf}，采用\textbf{解耦架构}，将生成、评分和训练分离为可独立扩展的集群。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_040_fig40.png}
\caption{Decoupled RLHF architecture. Each cluster optimized for its workload. Scored rollouts accumulate in the experience buffer before being consumed by training.}
\caption{解耦的 RLHF 架构。每个集群针对其工作负载进行优化。评分后的 rollouts 在经验缓冲区中累积，然后由训练使用。}
\end{figure}

\begin{keybox}[Why Decouple?]
\textbf{Generation} is memory-bandwidth bound (need fast HBM, waste compute).\\
\textbf{生成}受内存带宽限制（需要快速 HBM，浪费计算能力）。

\textbf{Training} is compute-bound (need tensor cores, waste bandwidth during backprop).\\
\textbf{训练}受计算能力限制（需要张量核心，在反向传播期间浪费带宽）。

\textbf{Same hardware can’t optimize both}: If you put everything together, you either waste compute during generation or waste bandwidth during training. Decoupling lets each cluster use optimal hardware/config.
\textbf{同一硬件无法同时优化两者}：如果将一切放在一起，要么在生成时浪费计算能力，要么在训练时浪费带宽。解耦允许每个集群使用最优的硬件/配置。

\textbf{Practical benefits}:\\
\textbf{实际收益}：

\begin{itemize}
  \item Scale generation and training independently
  \item 独立扩展生成和训练
  \item Generation cluster is stateless $\rightarrow$ trivial fault tolerance
  \item 生成集群无状态 $\rightarrow$ 容错简单
  \item Can overlap gen(step $N+1$) with training(step $N$) $\rightarrow$ 30--40\% speedup
  \item 可以重叠生成（步骤 $N+1$）和训练（步骤 $N$）$\rightarrow$ 30--40\% 加速
  \item Different quantization: INT8 for generation (bandwidth), BF16 for training (precision)
  \item 不同的量化：生成用 INT8（带宽），训练用 BF16（精度）
\end{itemize}
\end{keybox}

## Weight Synchronization Strategies
## 权重同步策略
\label{weight-synchronization-strategies}

{\small
\begin{tabular}{@{}llll@{}}
\toprule
\textbf{Strategy} & \textbf{Staleness} & \textbf{Bandwidth} & \textbf{Quality Impact} \\
\textbf{策略} & \textbf{陈旧度} & \textbf{带宽} & \textbf{质量影响} \\
\midrule
Synchronous (every step) & 0 steps & 140 GB/step & Perfect but too slow \\
同步（每步） & 0 步 & 140 GB/步 & 完美但太慢 \\
Periodic (every 50 steps) & 25 avg & 2.8 GB/step amortized & $<$2\% quality loss \\
周期性（每 50 步） & 平均 25 & 分摊后 2.8 GB/步 & $<$2\% 质量损失 \\
Delta compression (INT8) & 25 avg & 0.4 GB/step & $<$3\% quality loss \\
增量压缩（INT8） & 平均 25 & 0.4 GB/步 & $<$3\% 质量损失 \\
Async streaming & 5--10 steps & 14 GB/step (background) & $<$1\% quality loss \\
异步流式 & 5--10 步 & 14 GB/步（后台） & $<$1\% 质量损失 \\
\bottomrule
\end{tabular}
}

\begin{intuitionbox}[Why Staleness is OK for PPO/GRPO]
PPO’s clipped objective was \emph{designed} for off-policy data! The clip $[1-\epsilon, 1+\epsilon]$ bounds the impact of stale data. With 10--50 steps of staleness:
PPO 的裁剪目标本就是\textit{为}离策略数据\textit{设计的}！裁剪区间 $[1-\epsilon, 1+\epsilon]$ 限制了陈旧数据的影响。在 10--50 步的陈旧度下：

\begin{itemize}
  \item Policy changes $\sim$0.1--1\% per step (with proper LR)
  \item 策略每步变化 $\sim$0.1--1\%（使用合适的 LR）
  \item Over 50 steps: $\sim$5\% policy drift
  \item 超过 50 步：$\sim$5\% 的策略漂移
  \item PPO clip handles up to 20\% drift by design
  \item PPO 裁剪设计上可处理高达 20\% 的漂移
  \item Empirically: quality loss $<$2\% for 50-step staleness
  \item 经验上：50 步陈旧度下质量损失 $<$2\%
\end{itemize}

\textbf{Bandwidth math}: 70B BF16 = 140GB. InfiniBand 400Gb/s = 50GB/s $\rightarrow$ full sync in 2.8s. With delta compression: $<$0.5s. Async = free (runs in background).
\textbf{带宽计算}：70B BF16 = 140GB。InfiniBand 400Gb/s = 50GB/s $\rightarrow$ 完全同步需 2.8 秒。使用增量压缩：$<$0.5 秒。异步 = 免费（后台运行）。
\end{intuitionbox}

## Memory Optimization Techniques
## 内存优化技术
\label{memory-optimization-techniques}

\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{ZeRO Stage} & \textbf{What Gets Sharded} & \textbf{Memory/GPU (70B, 8 GPUs)} \\
\textbf{ZeRO 阶段} & \textbf{分片内容} & \textbf{每 GPU 内存（70B，8 GPU）} \\
\midrule
None (Data Parallel) & Nothing (full replica) & 560GB per GPU (impossible) \\
无（数据并行） & 无（完整副本） & 每 GPU 560GB（不可能） \\
ZeRO-1 & Optimizer states only & 175GB \\
ZeRO-1 & 仅优化器状态 & 175GB \\
ZeRO-2 & Optimizer states + Gradients & 105GB \\
ZeRO-2 & 优化器状态 + 梯度 & 105GB \\
ZeRO-3 (FSDP) & Optimizer + Gradients + Parameters & \textbf{70GB (fits in A100-80GB!)} \\
ZeRO-3 (FSDP) & 优化器 + 梯度 + 参数 & \textbf{70GB（可放入 A100-80GB！）} \\
\bottomrule
\end{tabular}

\textbf{Additional techniques}:\\
\textbf{其他技术}：

\begin{itemize}
  \item \textbf{Gradient checkpointing}~\cite{chen2016training}: Don’t store all activations; recompute during backward pass. Saves $\sim$60\% activation memory, costs $\sim$33\% extra compute. Selective: only checkpoint attention layers (memory-heavy), keep FFN activations (compute-heavy to recompute).
  \item \textbf{梯度检查点}~\cite{chen2016training}：不存储所有激活值；在反向传播期间重新计算。节省 $\sim$60\% 的激活内存，额外增加 $\sim$33\% 的计算量。选择性策略：仅对注意力层（内存密集）设置检查点，保留 FFN 激活值（计算密集，重新计算成本高）。
  \item \textbf{Mixed precision}~\cite{micikevicius2018mixed}: Forward in BF16 (2 bytes/param), optimizer states in FP32 (4 bytes each for m,v). Master weights in FP32 for accumulation.
  \item \textbf{混合精度}~\cite{micikevicius2018mixed}：前向传播使用 BF16（每参数 2 字节），优化器状态使用 FP32（m、v 各 4 字节）。主权重使用 FP32 进行累加。
  \item \textbf{CPU offloading} (ZeRO-Infinity~\cite{rajbhandari2021zeroinfinity}): Move optimizer states to CPU RAM. 50\% memory savings but 2--3$\times$ slower (PCIe 64GB/s bottleneck).
  \item \textbf{CPU 卸载}（ZeRO-Infinity~\cite{rajbhandari2021zeroinfinity}）：将优化器状态移至 CPU RAM。节省 50\% 内存，但慢 2--3$\times$（PCIe 64GB/s 瓶颈）。
  \item \textbf{Activation offloading}: Move activations to CPU during forward, bring back for backward. Only when memory is truly critical.
  \item \textbf{激活卸载}：在前向传播期间将激活值移至 CPU，反向传播时取回。仅在内存真正紧张时使用。
  \item \textbf{Flash Attention}~\cite{dao2022flashattention, dao2023flashattention2}: O($n$) memory instead of O($n^2$) for attention. 2--4$\times$ faster + massive memory savings for long sequences.
  \item \textbf{Flash Attention}~\cite{dao2022flashattention, dao2023flashattention2}：注意力机制的内存从 O($n^2$) 降至 O($n$)。对于长序列，速度提升 2--4$\times$，同时大幅节省内存。
\end{itemize}

\subsection{Flash Attention’s Impact on RLHF}
\subsection{Flash Attention 对 RLHF 的影响}
\label{flash-attentions-impact-on-rlhf}

\begin{intuitionbox}[Why Flash Attention Matters for RLHF]
RLHF involves generating long sequences (rollouts) and then training on them. Without Flash Attention:
RLHF 涉及生成长序列（rollouts）然后在其上进行训练。如果没有 Flash Attention：

\begin{itemize}
  \item A 4K-token sequence with 32 heads requires $\sim$4 GB just for attention matrices
  \item 一个 4K token、32 头的序列仅注意力矩阵就需要 $\sim$4 GB
  \item This severely limits batch size during PPO/GRPO training
  \item 这严重限制了 PPO/GRPO 训练期间的批次大小
  \item Gradient checkpointing of attention activations is expensive
  \item 对注意力激活值进行梯度检查点成本高昂
\end{itemize}

With Flash Attention:\\
使用 Flash Attention：

\begin{itemize}
  \item Attention memory is $O(n)$ -- dominated by $Q, K, V, O$ tensors
  \item 注意力内存为 $O(n)$ —— 主要由 $Q, K, V, O$ 张量占据
  \item Longer rollouts (8K--32K tokens) become feasible with the same GPU memory
  \item 更长的 rollouts（8K--32K token）在相同 GPU 内存下变得可行
  \item Backward pass recomputes attention tiles from $Q, K, V$ (no stored $n^2$ matrix)
  \item 反向传播从 $Q, K, V$ 重新计算注意力分块（不存储 $n^2$ 矩阵）
  \item This is the key enabler for long-context RLHF (e.g., reasoning models)
  \item 这是长上下文 RLHF（例如推理模型）的关键使能技术
\end{itemize}
\end{intuitionbox}

\begin{warningbox}[Flash Attention and Gradient Checkpointing]
Flash Attention’s backward pass recomputes the attention tiles on-the-fly from $Q, K, V$ (which are stored). This means Flash Attention \emph{already implements} a form of activation recomputation for the $O(n^2)$ attention matrix. You do not need to additionally checkpoint the attention layer -- doing so would recompute $Q, K, V$ unnecessarily.
Flash Attention 的反向传播会从存储的 $Q, K, V$ 中即时重新计算注意力分块。这意味着 Flash Attention \textit{已经实现了}对 $O(n^2)$ 注意力矩阵的某种激活重新计算。你不需要额外对注意力层设置检查点——这样做会不必要地重新计算 $Q, K, V$。
\end{warningbox}

```markdown
\begin{lstlisting}[style=pythonstyle]
# DeepSpeed ZeRO-3 configuration for 70B RLHF training
ds_config = {
    "bf16": {"enabled": True},
    "zero_optimization": {
        "stage": 3,
        "overlap_comm": True,                    # Overlap communication with compute
        "contiguous_gradients": True,            # Better memory layout
        "reduce_scatter": True,                  # More efficient than allreduce
        "reduce_bucket_size": 5e7,               # 50M params per bucket
        "prefetch_bucket_size": 5e7,             # Prefetch next bucket
        "param_persistence_threshold": 1e5,      # Keep small params on all GPUs
        "offload_optimizer": {"device": "cpu", "pin_memory": True},  # CPU offload
        "sub_group_size": 1e9,                   # Reduce fragmentation
    },
    "gradient_accumulation_steps": 4,
    "gradient_clipping": 1.0,
    "train_micro_batch_size_per_gpu": 2,
    "wall_clock_breakdown": True,
}
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle]
# DeepSpeed ZeRO-3 配置，用于 70B RLHF 训练
ds_config = {
    "bf16": {"enabled": True},
    "zero_optimization": {
        "stage": 3,
        "overlap_comm": True,                    # 将通信与计算重叠
        "contiguous_gradients": True,            # 更好的内存布局
        "reduce_scatter": True,                  # 比 allreduce 更高效
        "reduce_bucket_size": 5e7,               # 每个桶 5000 万个参数
        "prefetch_bucket_size": 5e7,             # 预取下一个桶
        "param_persistence_threshold": 1e5,      # 在所有 GPU 上保留小参数
        "offload_optimizer": {"device": "cpu", "pin_memory": True},  # CPU 卸载
        "sub_group_size": 1e9,                   # 减少碎片化
    },
    "gradient_accumulation_steps": 4,
    "gradient_clipping": 1.0,
    "train_micro_batch_size_per_gpu": 2,
    "wall_clock_breakdown": True,
}
\end{lstlisting}

## Fault Tolerance at Scale
## 大规模容错

\label{fault-tolerance-at-scale}

\begin{warningbox}[Hardware Failure Reality]
\textbf{Individual GPU MTBF}: $\sim$10,000 hours.\\
\textbf{512-GPU cluster MTBF}: $10000/512 \approx 20$ hours. But with software/network: \textbf{4--8 hours realistically}.\\
\textbf{Multi-day training run}: Will see 5--15 failures. Without fault tolerance, one failure kills everything.
\end{warningbox}

\begin{warningbox}[硬件故障的现实]
\textbf{单 GPU 平均无故障时间（MTBF）}：约 10,000 小时。\\
\textbf{512-GPU 集群 MTBF}：$10000/512 \approx 20$ 小时。但加上软件/网络因素：实际为 \textbf{4--8 小时}。\\
\textbf{多日训练运行}：会出现 5--15 次故障。若无容错机制，一次故障就会导致一切失败。
\end{warningbox}

\textbf{Production fault tolerance stack}:

\textbf{生产级容错栈}：

\begin{enumerate}
  \item \textbf{Detection}: NCCL timeout (60s), GPU heartbeat (10s), NVML health monitoring, ECC error counting.
  \item \textbf{Checkpointing}: Async every 50--100 steps. Non-blocking (background thread). Save: model weights, optimizer states (Adam m/v), scheduler state, RNG states, KL coefficient, replay buffer. Keep last 3 checkpoints. Time: $\sim$30s for 70B (parallel write to NVMe).
  \item \textbf{Recovery}: (a) Generation cluster = stateless, just restart and load latest weights. (b) Training cluster: load checkpoint, rebuild NCCL process group excluding failed node, redistribute FSDP shards, resume from last checkpoint.
  \item \textbf{Elastic training}: Torch Elastic / Kubernetes auto-scaling. Replace failed node within minutes. Training continues with $N-1$ GPUs temporarily.
  \item \textbf{Prevention}: GPU health pre-screening (run GEMM stress test before starting). Hot spares on standby. Redundant network paths (dual-rail InfiniBand).
\end{enumerate}

\begin{enumerate}
  \item \textbf{检测}：NCCL 超时（60秒）、GPU 心跳（10秒）、NVML 健康监控、ECC 错误计数。
  \item \textbf{检查点保存}：每 50--100 步异步执行。非阻塞（后台线程）。保存内容：模型权重、优化器状态（Adam m/v）、调度器状态、随机数生成器状态、KL 系数、经验回放缓冲区。保留最近 3 个检查点。耗时：70B 模型约 30 秒（并行写入 NVMe）。
  \item \textbf{恢复}：（a）生成集群 = 无状态，只需重启并加载最新权重。（b）训练集群：加载检查点，重建排除故障节点的 NCCL 进程组，重新分配 FSDP 分片，从上一个检查点恢复。
  \item \textbf{弹性训练}：Torch Elastic / Kubernetes 自动缩放。在几分钟内替换故障节点。训练暂时以 $N-1$ 个 GPU 继续。
  \item \textbf{预防}：GPU 健康预筛查（启动前运行 GEMM 压力测试）。热备机待命。冗余网络路径（双轨 InfiniBand）。
\end{enumerate}

\section{End-to-End Latency Breakdown}
\section{端到端延迟分解}

\label{end-to-end-latency-breakdown}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_041_fig41.png}
\caption{Without overlap (monolithic). With decoupled: gen overlaps with training, effective 1.4$\times$ speedup.}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_041_fig41.png}
\caption{无重叠（整体式）。解耦后：生成与训练重叠，有效加速 1.4 倍。}
\end{figure}

\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{Phase} & \textbf{Time (70B)} & \textbf{Bound By} & \textbf{Optimization} \\
\midrule
Generation (128$\times$512 tok) & 30--45s & Memory bandwidth & vLLM, spec decoding, INT8 \\
Reward scoring & 5--8s & Compute (batch forward) & INT8 RM, batch=128 \\
Reference log-probs & 4--6s & Compute (batch forward) & INT8 ref, or LoRA (free) \\
PPO update (4 epochs) & 8--12s & Compute (backprop) & FSDP, Flash Attention \\
Weight sync & 0--3s & Network (async) & Delta compression, async \\
\textbf{Total (monolithic)} & \textbf{50--75s} &  &  \\
\textbf{Total (decoupled, overlapped)} & \textbf{35--50s} &  & Gen overlaps with prev training \\
\bottomrule
\end{tabular}

\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{阶段} & \textbf{时间（70B）} & \textbf{受限于} & \textbf{优化} \\
\midrule
生成（128$\times$512 tok） & 30--45秒 & 内存带宽 & vLLM、推测解码、INT8 \\
奖励评分 & 5--8秒 & 计算（批量前向） & INT8 RM, batch=128 \\
参考对数概率 & 4--6秒 & 计算（批量前向） & INT8 参考模型，或 LoRA（免费） \\
PPO 更新（4轮） & 8--12秒 & 计算（反向传播） & FSDP、Flash Attention \\
权重同步 & 0--3秒 & 网络（异步） & 增量压缩、异步 \\
\textbf{总计（整体式）} & \textbf{50--75秒} &  &  \\
\textbf{总计（解耦、重叠）} & \textbf{35--50秒} &  & 生成与上一次训练重叠 \\
\bottomrule
\end{tabular}

\section{Monitoring and Observability}
\section{监控与可观测性}

\label{monitoring-and-observability}

\begin{keybox}[Key Metrics to Track During RLHF Training]
\textbf{Quality metrics} (log every 10 steps):

\begin{itemize}
  \item Mean reward (should increase then plateau)
  \item KL divergence from reference (should stay 3--10)
  \item Response length distribution (watch for length hacking)
  \item Entropy (should decrease slowly, not collapse)
\end{itemize}

\textbf{System metrics} (log every step):

\begin{itemize}
  \item GPU utilization (target: $>$80\% during training, $>$60\% during gen)
  \item Memory watermark per GPU (catch OOM before it happens)
  \item Generation throughput (tokens/sec, should be stable)
  \item Gradient norm (spikes = instability incoming)
  \item NCCL communication time (detect network degradation)
\end{itemize}
\end{keybox}

\begin{keybox}[RLHF 训练中需要追踪的关键指标]
\textbf{质量指标}（每 10 步记录一次）：

\begin{itemize}
  \item 平均奖励（应上升后趋于平稳）
  \item 与参考模型的 KL 散度（应保持在 3--10）
  \item 响应长度分布（警惕长度作弊）
  \item 熵（应缓慢下降，而非骤降）
\end{itemize}

\textbf{系统指标}（每步记录一次）：

\begin{itemize}
  \item GPU 利用率（目标：训练时 $>$80%，生成时 $>$60%）
  \item 每 GPU 内存水位（在 OOM 发生前捕捉）
  \item 生成吞吐量（token/秒，应保持稳定）
  \item 梯度范数（尖峰 = 不稳定即将到来）
  \item NCCL 通信时间（检测网络退化）
\end{itemize}
\end{keybox}

\section{Network Topology and Communication Patterns}
\section{网络拓扑与通信模式}

\label{sec:network-topology}

Efficient distributed training requires understanding the hierarchical communication fabric that connects GPUs. Modern clusters use a two-tier architecture: ultra-fast intra-node links and slower but scalable inter-node networks.

高效的分布式训练需要理解连接 GPU 的分层通信结构。现代集群采用两层架构：超快的节点内链路和较慢但可扩展的节点间网络。

\subsection{Intra-Node: NVLink and NVSwitch}
\subsection{节点内：NVLink 与 NVSwitch}

\label{intra-node-nvlink-and-nvswitch}

\begin{table}[ht!]
\centering
\caption{NVLink generations and their impact on LLM training}
\begin{tabular}{@{}lp{3cm}p{3.2cm}p{3.2cm}p{3.5cm}@{}}
\toprule
\textbf{Generation} & \textbf{BW per link} & \textbf{Links/GPU} & \textbf{Total BW} & \textbf{Platform} \\
\midrule
NVLink 3.0 & 50 GB/s & 12 & 600 GB/s & A100 (DGX A100) \\
NVLink 4.0 & 50 GB/s & 18 & 900 GB/s & H100 (DGX H100) \\
NVLink 5.0 & 100 GB/s & 18 & 1800 GB/s & B200 (DGX B200) \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[ht!]
\centering
\caption{NVLink 代际及其对 LLM 训练的影响}
\begin{tabular}{@{}lp{3cm}p{3.2cm}p{3.2cm}p{3.5cm}@{}}
\toprule
\textbf{代际} & \textbf{每链路带宽} & \textbf{每 GPU 链路数} & \textbf{总带宽} & \textbf{平台} \\
\midrule
NVLink 3.0 & 50 GB/s & 12 & 600 GB/s & A100 (DGX A100) \\
NVLink 4.0 & 50 GB/s & 18 & 900 GB/s & H100 (DGX H100) \\
NVLink 5.0 & 100 GB/s & 18 & 1800 GB/s & B200 (DGX B200) \\
\bottomrule
\end{tabular}
\end{table}

Within a single node (typically 8 GPUs), \textbf{NVSwitch} provides full-bisection bandwidth between all GPU pairs. This means any GPU can communicate with any other at full NVLink speed simultaneously---critical for Tensor Parallelism where every layer requires an AllReduce across all 8 GPUs.

在单个节点（通常 8 个 GPU）内部，\textbf{NVSwitch} 提供所有 GPU 对之间的全二分带宽。这意味着任意 GPU 可以同时以满 NVLink 速度与任何其他 GPU 通信——这对张量并行（Tensor Parallelism, TP）至关重要，因为每一层都需要跨全部 8 个 GPU 执行 AllReduce 操作。

\begin{keybox}[NVSwitch vs PCIe Topology]
\textbf{With NVSwitch} (DGX/HGX): All 8 GPUs connected all-to-all at 600--1800~GB/s. AllReduce for TP takes $\sim$0.2ms per layer.

\textbf{Without NVSwitch} (PCIe-only servers): GPUs communicate through CPU PCIe root complex at 32--64~GB/s. TP across 8 GPUs becomes 10--30$\times$ slower. \textbf{Never use TP$>$2 on PCIe-only systems.}
\end{keybox}

\begin{keybox}[NVSwitch 与 PCIe 拓扑对比]
\textbf{使用 NVSwitch}（DGX/HGX）：全部 8 个 GPU 以 600--1800 GB/s 全连接。TP 的 AllReduce 每层约需 0.2 毫秒。

\textbf{无 NVSwitch}（仅 PCIe 服务器）：GPU 通过 CPU PCIe 根复合体以 32--64 GB/s 通信。跨 8 个 GPU 的 TP 速度降低 10--30 倍。\textbf{切勿在仅 PCIe 系统上使用 TP>2。}
\end{keybox}

\subsection{Inter-Node: InfiniBand and RoCE}
\subsection{节点间：InfiniBand 与 RoCE}

\label{inter-node-infiniband-and-roce}

For FSDP/ZeRO-3 AllGather and ReduceScatter operations across nodes, the inter-node network dominates.

对于跨节点的 FSDP/ZeRO-3 AllGather 和 ReduceScatter 操作，节点间网络占主导地位。

\begin{table}[ht!]
\centering
\caption{Inter-node networking options for LLM training clusters}
{\small
\begin{tabular}{@{}llll@{}}
\toprule
\textbf{Technology} & \textbf{Bandwidth} & \textbf{Latency} & \textbf{Notes} \\
\midrule
InfiniBand NDR & 400 Gb/s (50 GB/s) & 1--2 $\mu$s & Gold standard, RDMA, lossless \\
InfiniBand NDR (dual-rail) & 800 Gb/s (100 GB/s) & 1--2 $\mu$s & Used in H100 clusters \\
RoCE v2 & 100--400 Gb/s & 2--5 $\mu$s & Cheaper, needs PFC/ECN tuning \\
Ethernet (TCP) & 100--400 Gb/s & 10--50 $\mu$s & Not suitable for $>$16 GPU training \\
\bottomrule
\end{tabular}
}
\end{table}

\begin{table}[ht!]
\centering
\caption{LLM 训练集群的节点间网络选择}
{\small
\begin{tabular}{@{}llll@{}}
\toprule
\textbf{技术} & \textbf{带宽} & \textbf{延迟} & \textbf{备注} \\
\midrule
InfiniBand NDR & 400 Gb/s (50 GB/s) & 1--2 $\mu$s & 黄金标准，RDMA，无损 \\
InfiniBand NDR (双轨) & 800 Gb/s (100 GB/s) & 1--2 $\mu$s & 用于 H100 集群 \\
RoCE v2 & 100--400 Gb/s & 2--5 $\mu$s & 更便宜，需要 PFC/ECN 调优 \\
以太网 (TCP) & 100--400 Gb/s & 10--50 $\mu$s & 不适用于 >16 GPU 训练 \\
\bottomrule
\end{tabular}
}
\end{table}

\subsection{Communication Primitives and Their Costs}
\subsection{通信原语及其开销}

\label{communication-primitives-and-their-costs}

Understanding when each collective is used helps diagnose bottlenecks:

了解每个集合操作的使用时机有助于诊断瓶颈：

\begin{table}[ht!]
\centering
\caption{NCCL collective operations in distributed LLM training}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{Collective} & \textbf{Data Moved} & \textbf{Used By} & \textbf{When} \\
\midrule
AllReduce & $2 \cdot \frac{N-1}{N} \cdot M$ & TP, DP & Sum gradients or activations across GPUs \\
AllGather & $\frac{N-1}{N} \cdot M$ & FSDP forward & Reconstruct full parameter tensor before matmul \\
ReduceScatter & $\frac{N-1}{N} \cdot M$ & FSDP backward & Distribute gradient shards after backprop \\
Broadcast & $M$ & PP & Send activations to next pipeline stage \\
Send/Recv & $M$ & PP & Point-to-point between adjacent stages \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[ht!]
\centering
\caption{分布式 LLM 训练中的 NCCL 集合操作}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{集合操作} & \textbf{数据传输量} & \textbf{使用方} & \textbf{使用时机} \\
\midrule
AllReduce & $2 \cdot \frac{N-1}{N} \cdot M$ & TP, DP & 跨 GPU 求和梯度或激活 \\
AllGather & $\frac{N-1}{N} \cdot M$ & FSDP 前向 & 矩阵乘法前重建完整参数张量 \\
ReduceScatter & $\frac{N-1}{N} \cdot M$ & FSDP 反向 & 反向传播后分发梯度分片 \\
Broadcast & $M$ & PP & 将激活发送到下一流水线阶段 \\
Send/Recv & $M$ & PP & 相邻阶段之间的点对点通信 \\
\bottomrule
\end{tabular}
\end{table}

where $M$ is the message size (bytes) and $N$ is the number of participants.

其中 $M$ 是消息大小（字节），$N$ 是参与方数量。

\newpage
\begin{intuitionbox}[Communication-Computation Overlap]
Modern frameworks (FSDP, DeepSpeed) aggressively overlap communication with computation:

\newpage
\begin{intuitionbox}[通信-计算重叠]
现代框架（FSDP、DeepSpeed）积极地实现通信与计算重叠：
```

## Network Topology Design  
## 网络拓扑设计  

Production clusters use **fat-tree** or **rail-optimized** topologies:  
生产集群使用**胖树（fat-tree）**或**轨道优化（rail-optimized）**拓扑：  

\begin{itemize}  
  \item \textbf{Fat-tree}: Full bisection bandwidth at every level. Any node can communicate with any other at full speed. Expensive (many switches) but maximally flexible.  
  \item \textbf{胖树}：每一层都有全对分带宽。任何节点之间都可以全速通信。成本高（需要大量交换机），但灵活性最大。  
  \item \textbf{Rail-optimized}: GPU $i$ on every node connects to the same leaf switch (``rail $i$''). AllReduce within a rail is cheap; cross-rail traffic is expensive. Used by Meta's RSC and Google's TPU pods.  
  \item \textbf{轨道优化}：每个节点上的 GPU $i$ 连接到同一个叶交换机（“轨道 $i$”）。轨道内的 AllReduce 廉价；跨轨道流量昂贵。被 Meta 的 RSC 和 Google 的 TPU pods 使用。  
  \item \textbf{3D torus / Dragonfly}: Used in HPC clusters (Frontier, Aurora). Topology-aware job placement is critical.  
  \item \textbf{3D 环面 / Dragonfly}：用于 HPC 集群（Frontier、Aurora）。拓扑感知的任务放置至关重要。  
\end{itemize}  

\begin{warningbox}[Job Placement Matters]  
\begin{warningbox}[任务放置至关重要]  

On a 512-GPU cluster, random node assignment can cause 2--3$\times$ slowdown due to network congestion. \textbf{Always request contiguous node blocks.} Production schedulers (Slurm, Kubernetes) should enforce locality: all nodes in a training job should be on the same leaf switch or within one hop of each other.  
在一个 512 GPU 集群上，随机节点分配可能因网络拥塞导致 2--3$\times$ 减速。\textbf{始终请求连续的节点块。} 生产调度器（Slurm、Kubernetes）应强制局部性：训练作业中的所有节点应位于同一叶交换机上或彼此一跳以内。  

\end{warningbox}  

\section{Training Throughput and Model FLOPs Utilization}  
\section{训练吞吐量与模型 FLOPs 利用率}  

\subsection{Measuring Training Efficiency: MFU}  
\subsection{衡量训练效率：MFU}  

\textbf{Model FLOPs Utilization (MFU)}~\cite{chowdhery2022palm} is the standard metric for training efficiency:  
**模型 FLOPs 利用率（Model FLOPs Utilization, MFU）**~\cite{chowdhery2022palm} 是训练效率的标准指标：  

\begin{equation}  
\text{MFU} = \frac{\text{Observed throughput (tokens/sec)} \times \text{FLOPs per token}}{\text{Peak hardware FLOPS}}  
\end{equation}  

对于具有 $P$ 参数、$s$ 序列长度和 $b$ 批量大小的 Transformer：  
\begin{equation}  
\text{FLOPs per token} \approx 6P + 12 \cdot n_\text{layers} \cdot d_\text{model} \cdot s  
\end{equation}  

The factor of 6 comes from: 2 (multiply-add) $\times$ 3 (forward + backward, where backward $\approx 2\times$ forward). The second term accounts for attention's $O(s^2)$ cost.  
因子 6 来自：2（乘加）× 3（前向 + 反向，其中反向 ≈ 2× 前向）。第二项考虑了注意力机制的 $O(s^2)$ 成本。  

\begin{table}[ht!]  
\centering  
\caption{MFU benchmarks across scales and hardware}  
\caption{不同规模与硬件下的 MFU 基准}  

\begin{tabular}{@{}lp{3cm}p{3.2cm}p{3.2cm}p{3.5cm}@{}}  
\toprule  
\textbf{Model} & \textbf{Hardware} & \textbf{MFU} & \textbf{Tokens/sec/GPU} & \textbf{Configuration} \\  
\textbf{模型} & \textbf{硬件} & \textbf{MFU} & \textbf{每秒每 GPU 令牌数} & \textbf{配置} \\  
\midrule  
LLaMA-7B & 8$\times$A100 & 57\% & 3,200 & FSDP, FlashAttn, BF16 \\  
LLaMA-13B & 16$\times$A100 & 52\% & 1,750 & FSDP, FlashAttn, BF16 \\  
LLaMA-70B & 64$\times$A100 & 45\% & 380 & FSDP+TP=8, FlashAttn \\  
GPT-4 (est.) & 10,000+ H100 & 40--50\% & --- & 3D parallelism \\  
PaLM-540B & 6144 TPUv4 & 46\% & --- & DP+TP+PP \\  
\bottomrule  
\end{tabular}  
\end{table}  

\begin{intuitionbox}[Why MFU Decreases with Scale]  
\begin{intuitionbox}[为什么 MFU 随规模增加而下降]  

Larger models require more parallelism, which introduces:  
更大的模型需要更多并行化，这会引入：  

\begin{enumerate}  
  \item \textbf{Communication overhead}: AllGather/ReduceScatter for FSDP ($\sim$10--15\% at 64 GPUs)  
  \item \textbf{通信开销}：FSDP 的 AllGather/ReduceScatter（64 GPU 时约 10–15%）  
  \item \textbf{Pipeline bubbles}: PP introduces idle time at start/end of micro-batches ($\sim$15--25\% with PP=4)  
  \item \textbf{流水线气泡}：PP 在微批次的开始和结束时引入空闲时间（PP=4 时约 15–25%）  
  \item \textbf{Memory for auxiliary models}: Reference/RM take GPU memory that could hold larger batches  
  \item \textbf{辅助模型的显存}：参考模型/奖励模型占用本可容纳更大批次的 GPU 显存  
  \item \textbf{Load imbalance}: Not all layers have equal compute (embeddings vs transformer blocks)  
  \item \textbf{负载不均衡}：并非所有层的计算量相同（嵌入层 vs Transformer 块）  
\end{enumerate}  

\textbf{Rule of thumb}: Target MFU $>$ 40\% for training. If below 30\%, diagnose with profiling.  
**经验法则**：训练目标 MFU > 40%。若低于 30%，请通过性能分析诊断。  

\end{intuitionbox}  

\subsection{Compute-Optimal Batch Sizing}  
\subsection{计算最优批量大小}  

The effective batch size interacts with hardware utilization in non-obvious ways:  
有效批量大小与硬件利用率之间存在非直观的交互：  

\begin{equation}  
\text{Effective batch size} = \text{micro\_batch} \times \text{grad\_accum} \times \text{DP degree}  
\end{equation}  

\begin{itemize}  
  \item \textbf{Too small}: GPU underutilized (low arithmetic intensity), communication dominates.  
  \item \textbf{过小}：GPU 利用率不足（低算术强度），通信占主导。  
  \item \textbf{Too large}: Diminishing learning per token (critical batch size exceeded), wastes compute.  
  \item \textbf{过大}：每个令牌的学习收益递减（超过关键批量大小），浪费计算。  
  \item \textbf{Sweet spot}: The \emph{critical batch size} $B_\text{crit}$ where gradient noise equals gradient signal. For LLMs, $B_\text{crit} \sim 1$--$4$M tokens~\cite{mccandlish2018empirical}.  
  \item \textbf{最佳点}：\emph{关键批量大小} $B_\text{crit}$，即梯度噪声等于梯度信号的点。对于 LLM，$B_\text{crit} \sim 1$–$4$M 令牌~\cite{mccandlish2018empirical}。  
\end{itemize}  

For RLHF specifically, the batch contains \emph{rollouts} (not just tokens):  
对于 RLHF 而言，批量包含\emph{展开（rollouts）}（不仅包含令牌）：  

\begin{equation}  
\text{RLHF batch} = N_\text{prompts} \times K_\text{generations} \times L_\text{avg response length}  
\end{equation}  

Typical production values: $N=128$ prompts, $K=1$--$4$ generations, $L=256$--$512$ tokens $\rightarrow$ 32K--256K tokens per step.  
典型生产值：$N=128$ 个提示，$K=1$–$4$ 个生成，$L=256$–$512$ 令牌 → 每步 32K–256K 个令牌。  

\subsection{Profiling and Bottleneck Diagnosis}  
\subsection{性能分析与瓶颈诊断}  

Key profiling tools and what they reveal:  
关键性能分析工具及其揭示的内容：  

\begin{tabular}{@{}lp{5cm}p{8cm}@{}}  
\toprule  
\textbf{Tool} & \textbf{Captures} & \textbf{Best For} \\  
\textbf{工具} & \textbf{捕获内容} & \textbf{最适用于} \\  
\midrule  
\texttt{torch.profiler} & Kernel timing, memory & Finding slow ops, memory leaks \\  
\texttt{torch.profiler} & 内核时间、显存 & 发现慢操作、显存泄漏 \\  
NVIDIA Nsight Systems & Full GPU timeline & Visualizing overlap, gaps between kernels \\  
NVIDIA Nsight Systems & 完整 GPU 时间线 & 可视化内核间的重叠与间隙 \\  
\texttt{nccl\_debug=INFO} & Collective sizes/times & Diagnosing communication bottlenecks \\  
\texttt{nccl\_debug=INFO} & 集合大小/时间 & 诊断通信瓶颈 \\  
\texttt{torch.cuda.memory\_stats} & Allocation patterns & Finding fragmentation, peak usage \\  
\texttt{torch.cuda.memory\_stats} & 分配模式 & 发现碎片化、峰值使用 \\  
DeepSpeed Flops Profiler & Per-layer FLOPs & Identifying load imbalance \\  
DeepSpeed Flops Profiler & 每层 FLOPs & 识别负载不均衡 \\  
\texttt{py-spy} / \texttt{scalene} & CPU profiling & Data loading, tokenization bottlenecks \\  
\texttt{py-spy} / \texttt{scalene} & CPU 分析 & 数据加载、分词瓶颈 \\  
\bottomrule  
\end{tabular}  

\begin{examplebox}[Diagnosing Low MFU: A Checklist]  
\begin{examplebox}[诊断低 MFU：检查清单]  

\begin{enumerate}  
  \item \textbf{GPU utilization $<$ 80\%?} $\rightarrow$ Data loading bottleneck (check CPU, I/O).  
  \item \textbf{GPU 利用率 < 80\%？} $\rightarrow$ 数据加载瓶颈（检查 CPU、I/O）。  
  \item \textbf{Large gaps between kernels?} $\rightarrow$ Python overhead, synchronization points. Use CUDA graphs.  
  \item \textbf{内核间间隙大？} $\rightarrow$ Python 开销、同步点。使用 CUDA graphs。  
  \item \textbf{Communication $>$ 20\% of step time?} $\rightarrow$ Reduce TP degree, increase batch size, check network health.  
  \item \textbf{通信占步时间的 20% 以上？} $\rightarrow$ 降低 TP 度数、增大批量大小、检查网络健康。  
  \item \textbf{Memory at 99\%?} $\rightarrow$ Cannot increase batch. Try gradient checkpointing, offloading.  
  \item \textbf{显存 99%？} $\rightarrow$ 无法增大批量。尝试梯度检查点、卸载。  
  \item \textbf{OOM during generation?} $\rightarrow$ KV cache too large. Reduce max\_seq\_len or batch size for gen.  
  \item \textbf{生成时 OOM？} $\rightarrow$ KV 缓存过大。减小 max\_seq\_len 或生成时的批量大小。  
\end{enumerate}  

\end{examplebox}  

\section{Cost Analysis and Cloud Deployment}  
\section{成本分析与云端部署}  

Understanding the economics of RLHF training is essential for planning.  
理解 RLHF 训练的经济性对于规划至关重要。  

\subsection{Hardware Cost Comparison}  
\subsection{硬件成本对比}  

\begin{table}[ht!]  
\centering  
\caption{Approximate cloud GPU costs for RLHF training (2024--2025 pricing)}  
\caption{RLHF 训练的近似云 GPU 成本（2024–2025 年定价）}  

\begin{tabular}{@{}lp{3cm}p{3.2cm}p{3.2cm}p{3.5cm}@{}}  
\toprule  
\textbf{GPU} & \textbf{On-Demand/hr} & \textbf{Spot/hr} & \textbf{Memory} & \textbf{Use Case} \\  
\textbf{GPU} & \textbf{按需/小时} & \textbf{竞价/小时} & \textbf{显存} & \textbf{使用场景} \\  
\midrule  
A100 80GB & \$2.50--3.50 & \$1.00--1.50 & 80 GB HBM2e & Budget training, gen cluster \\  
A100 80GB & \$2.50–3.50 & \$1.00–1.50 & 80 GB HBM2e & 预算训练、生成集群 \\  
H100 80GB & \$4.00--6.00 & \$2.00--3.00 & 80 GB HBM3 & Production training \\  
H100 80GB & \$4.00–6.00 & \$2.00–3.00 & 80 GB HBM3 & 生产训练 \\  
H200 141GB & \$6.00--8.00 & --- & 141 GB HBM3e & Large context, fewer-GPU configs \\  
H200 141GB & \$6.00–8.00 & --- & 141 GB HBM3e & 大上下文、少 GPU 配置 \\  
MI300X 192GB & \$3.50--5.00 & \$1.50--2.50 & 192 GB HBM3 & Cost-effective alternative \\  
MI300X 192GB & \$3.50–5.00 & \$1.50–2.50 & 192 GB HBM3 & 性价比替代方案 \\  
\bottomrule  
\end{tabular}  
\end{table}  

\subsection{RLHF Training Cost Estimation}  
\subsection{RLHF 训练成本估算}  

\begin{equation}  
\text{Cost} = \frac{N_\text{steps} \times T_\text{step}}{3600} \times N_\text{GPUs} \times C_\text{GPU/hr}  
\end{equation}  

\begin{examplebox}[Cost Example: 70B Model RLHF (10K steps)]  
\begin{examplebox}[成本示例：70B 模型 RLHF（10K 步）]  

\begin{tabular}{@{}lp{11cm}@{}}  
\toprule  
Steps & 10,000 \\  
步骤 & 10,000 \\  
\midrule  
Time per step (decoupled) & 45 seconds \\  
每步时间（解耦） & 45 秒 \\  
Total training time & $10000 \times 45 / 3600 = 125$ hours \\  
总训练时间 & $10000 \times 45 / 3600 = 125$ 小时 \\  
GPUs (generation + training) & 64 A100-80GB \\  
GPU（生成 + 训练） & 64 个 A100-80GB \\  
Cost per GPU-hour (spot) & \$1.20 \\  
每 GPU 小时成本（竞价） & \$1.20 \\  
\textbf{Total cost} & $125 \times 64 \times \$1.20 =$ \textbf{\$9,600} \\  
\textbf{总成本} & $125 \times 64 \times \$1.20 =$ \textbf{\$9,600} \\  
\bottomrule  
\end{tabular}  

\textbf{Breakdown by phase}:  
\textbf{按阶段分解}：

\begin{itemize}
  \item Generation cluster (32 GPUs): \$4,800 (60\% of time)
  \item 生成集群（32 GPU）：\$4,800（60%的时间）
  \item Training cluster (32 GPUs): \$4,800 (could overlap $\rightarrow$ \$3,400 effective)
  \item 训练集群（32 GPU）：\$4,800（可重叠 $\rightarrow$ 有效成本 \$3,400）
  \item Scoring (shared with gen GPUs): included above
  \item 评分（与生成GPU共享）：已包含在上述成本中
\end{itemize}

\textbf{With overlap}: Effective cost $\approx$ \textbf{\$7,500} for full RLHF alignment of a 70B model.
\textbf{重叠情况下}：对70B模型进行完整RLHF对齐的有效成本约为 \textbf{\$7,500}。
\end{examplebox}


\subsection{Cost Optimization Strategies}
\subsection{成本优化策略}
\label{cost-optimization-strategies}


\begin{itemize}
  \item \textbf{Spot/preemptible instances}: 50--70\% savings. Requires robust checkpointing (save every 5 minutes).
  \item \textbf{竞价/可抢占实例}：节省50--70%成本。需要健壮的检查点机制（每5分钟保存一次）。
  \item \textbf{Right-sizing}: Don’t use H100 for generation (memory-bound); A100 achieves similar tokens/\$ for inference.
  \item \textbf{合理选型}：不要在生成阶段使用H100（受内存限制）；A100在推理时可实现相似的 tokens/\$ 表现。
  \item \textbf{Quantized inference}: INT8/FP8 for generation and scoring halves GPU count for those clusters.
  \item \textbf{量化推理}：在生成和评分阶段使用INT8/FP8可将这些集群的GPU数量减半。
  \item \textbf{Progressive training}: Start with 8B proxy model for reward engineering/debugging ($\sim$\$200), then scale to 70B.
  \item \textbf{渐进式训练}：先用8B代理模型进行奖励工程设计/调试（约\$200），再扩展至70B。
  \item \textbf{LoRA for reference-free}: Eliminates reference model entirely (50\% memory reduction).
  \item \textbf{使用LoRA实现无参考模型}：完全消除参考模型（内存减少50%）。
  \item \textbf{Shorter sequences first}: Curriculum from 256$\rightarrow$512$\rightarrow$1024 token generations saves 40\% compute.
  \item \textbf{先短序列后长序列}：按课程从256$\rightarrow$512$\rightarrow$1024 token生成，节省40%计算量。
\end{itemize}


\section{Distributed Checkpointing}
\section{分布式检查点}
\label{sec:checkpointing}


At scale, naive checkpointing becomes a bottleneck. A 70B model with optimizer state requires saving $\sim$840~GB per checkpoint (FP32 master weights + Adam m + v).
大规模下，朴素检查点成为瓶颈。一个带有优化器状态的70B模型每次检查点需保存约840 GB（FP32主权重 + Adam m + v）。


\subsection{Checkpointing Strategies}
\subsection{检查点策略}
\label{checkpointing-strategies}


\begin{table}[ht!]
\centering
\caption{Checkpointing approaches for large-scale RLHF}
\caption{大规模RLHF的检查点方法}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{Strategy} & \textbf{Save Time (70B)} & \textbf{Storage/ckpt} & \textbf{Characteristics} \\
\textbf{策略} & \textbf{保存时间（70B）} & \textbf{存储/检查点} & \textbf{特点} \\
\midrule
Synchronous (all ranks) & 30--60s (blocking) & 420 GB & Simple, stalls training \\
同步（所有进程） & 30--60秒（阻塞） & 420 GB & 简单，会阻塞训练 \\
Async (background copy) & $<$1s (non-blocking) & 420 GB & Overlaps with next step \\
异步（后台拷贝） & $<$1秒（非阻塞） & 420 GB & 与下一步骤重叠 \\
Incremental (delta) & $<$1s & 5--20 GB & Only save changed params \\
增量（差分） & $<$1秒 & 5--20 GB & 仅保存变化的参数 \\
Sharded (FSDP native) & 5--10s & 420 GB sharded & Each rank saves its shard \\
分片（FSDP原生） & 5--10秒 & 420 GB（分片） & 每个进程保存自己的分片 \\
\bottomrule
\end{tabular}
\end{table}


\subsection{Production Checkpointing with torch.distributed.checkpoint}
\subsection{使用 torch.distributed.checkpoint 的生产级检查点}
\label{production-checkpointing-with-torch.distributed.checkpoint}


\begin{lstlisting}[style=pythonstyle]
import torch.distributed.checkpoint as dcp
from torch.distributed.checkpoint.state_dict import get_state_dict, StateDictOptions


# Save: each rank writes its shard in parallel
# 保存：每个进程并行写入自己的分片
state_dict = {"model": get_state_dict(model, options=StateDictOptions(full_state_dict=False))}
dcp.save(
    state_dict=state_dict,
    storage_writer=dcp.FileSystemWriter("/mnt/checkpoints/step_5000"),
    planner=dcp.DefaultSavePlanner(),  # Handles FSDP sharding automatically
    # 自动处理FSDP分片
)


# Async save: non-blocking, runs in background thread
# 异步保存：非阻塞，在后台线程中运行
future = dcp.async_save(
    state_dict=state_dict,
    storage_writer=dcp.FileSystemWriter("/mnt/checkpoints/step_5000"),
)
# Training continues immediately; future.result() blocks only if needed
# 训练立即继续；仅在需要时调用 future.result() 阻塞
\end{lstlisting}


\begin{keybox}[Checkpoint Hygiene for RLHF]
\begin{keybox}[RLHF的检查点卫生]
RLHF checkpoints must capture \emph{more} than standard pre-training:
RLHF检查点必须捕获比标准预训练 \emph{更多} 的内容：


\begin{itemize}
  \item Policy model weights + optimizer states (standard)
  \item 策略模型权重 + 优化器状态（标准）
  \item KL coefficient ($\beta$) and its schedule state
  \item KL系数 ($\beta$) 及其调度状态
  \item Replay buffer contents (for off-policy corrections)
  \item 回放缓冲区内容（用于离策略校正）
  \item RNG states for all GPUs (reproducibility)
  \item 所有GPU的随机数生成器状态（可复现性）
  \item Prompt iterator position (avoid re-processing prompts)
  \item 提示迭代器位置（避免重复处理提示）
  \item Reward model version tag (for auditability)
  \item 奖励模型版本标签（用于可审计性）
  \item Wandb/metrics run ID (for continuous logging)
  \item Wandb/指标运行ID（用于持续日志记录）
\end{itemize}
\end{keybox}


\section{Hardware Selection Guide}
\section{硬件选择指南}
\label{sec:hardware-guide}


Choosing the right hardware depends on model size, budget, and training phase.
选择合适的硬件取决于模型规模、预算和训练阶段。


\begin{table}[ht!]
\centering
\caption{Hardware recommendations by model scale and training phase}
\caption{按模型规模和训练阶段的硬件推荐}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{Model Size} & \textbf{Training Phase} & \textbf{Recommended} & \textbf{Configuration} \\
\textbf{模型规模} & \textbf{训练阶段} & \textbf{推荐硬件} & \textbf{配置} \\
\midrule
$\leq$7B & SFT + RLHF & 1--2$\times$ A100 & Single node, no parallelism needed \\
$\leq$7B & SFT + RLHF & 1--2$\times$ A100 & 单节点，无需并行 \\
7--13B & SFT + RLHF & 4--8$\times$ A100 & FSDP, optional TP=2 for gen \\
7--13B & SFT + RLHF & 4--8$\times$ A100 & FSDP，可选TP=2用于生成 \\
13--34B & SFT + RLHF & 8--16$\times$ A100/H100 & FSDP + TP=4 for gen \\
13--34B & SFT + RLHF & 8--16$\times$ A100/H100 & FSDP + TP=4用于生成 \\
70B & RLHF (full) & 32--64$\times$ A100/H100 & Decoupled, FSDP + TP=8 \\
70B & RLHF（完整） & 32--64$\times$ A100/H100 & 解耦，FSDP + TP=8 \\
70B & RLHF (LoRA) & 8--16$\times$ A100/H100 & No ref model, LoRA adapters \\
70B & RLHF（LoRA） & 8--16$\times$ A100/H100 & 无参考模型，LoRA适配器 \\
$>$100B & RLHF & 128+$\times$ H100 & 3D parallelism (TP+PP+DP) \\
$>$100B & RLHF & 128+$\times$ H100 & 3D并行（TP+PP+DP） \\
\bottomrule
\end{tabular}
\end{table}


\begin{intuitionbox}[H100 vs A100: When is the Upgrade Worth It?]
\begin{intuitionbox}[H100 vs A100：什么时候升级值得？]
H100 provides:
H100提供：


\begin{itemize}
  \item $\sim$1.6$\times$ peak FLOPS (989 vs 624 TFLOPS for BF16 with sparsity; 495 vs 312 without sparsity)
  \item $\sim$1.6$\times$峰值FLOPS（有稀疏性时BF16为989 vs 624 TFLOPS；无稀疏性时495 vs 312）
  \item $\sim$2$\times$ memory bandwidth (3.35 vs 2.0 TB/s)
  \item $\sim$2$\times$内存带宽（3.35 vs 2.0 TB/s）
  \item FP8 support (additional 2$\times$ for inference)
  \item FP8支持（推理时额外2倍）
  \item NVLink 4.0 (900 vs 600 GB/s)
  \item NVLink 4.0（900 vs 600 GB/s）
\end{itemize}


\textbf{For training}: $\sim$1.8--2.2$\times$ faster end-to-end (FP8 support and higher bandwidth amplify the raw FLOPS advantage).
\textbf{训练方面}：端到端速度提升约1.8--2.2倍（FP8支持和更高带宽放大了原始FLOPS优势）。


\textbf{For generation}: $\sim$1.7$\times$ faster (bandwidth-bound, so 2$\times$ BW $\approx$ 1.7$\times$ throughput with overhead).
\textbf{生成方面}：速度提升约1.7倍（受带宽限制，因此2倍带宽带来约1.7倍吞吐量，考虑开销后）。


\textbf{Cost-performance}: At 1.5$\times$ the price, H100 is almost always better value for training. For inference-only (generation clusters), A100 at spot pricing can be more cost-effective.
\textbf{性价比}：在价格1.5倍的情况下，H100在训练时几乎总是更划算。对于纯推理（生成集群），使用竞价价格的A100可能更具成本效益。
\end{intuitionbox}


\section{Optimizer Configuration for RL Training}
\section{RL训练的优化器配置}
\label{sec:rl-optimizer-config}


RL training (PPO, GRPO, DPO) imposes unique demands on the optimizer compared to pretraining or SFT. The loss landscape is non-stationary (the policy changes what data is generated), gradients are noisier (reward signal variance), and training is more prone to catastrophic forgetting or reward hacking. This section consolidates RL-specific optimizer guidance, using AdamW~\cite{loshchilov2019adamw} as the default optimizer.
与预训练或SFT相比，RL训练（PPO、GRPO、DPO）对优化器提出了独特的要求。损失景观是非平稳的（策略改变了生成的数据），梯度噪声更大（奖励信号方差），训练更容易出现灾难性遗忘或奖励破解。本节总结了RL特定的优化器指南，使用AdamW~\cite{loshchilov2019adamw}作为默认优化器。


\subsection{Why RL Requires Different Optimizer Settings}
\subsection{为什么RL需要不同的优化器设置}
\label{why-rl-requires-different-optimizer-settings}


\begin{keybox}[RL vs. SFT Optimization – Key Differences]
\begin{keybox}[RL与SFT优化——关键差异]
\begin{itemize}
  \item \textbf{Non-stationary data distribution}: unlike SFT where the dataset is fixed, RL generates new rollouts each iteration---the data distribution shifts with the policy.
  \item \textbf{非平稳数据分布}：与数据集固定的SFT不同，RL每次迭代生成新的轨迹——数据分布随策略变化。
  \item \textbf{High gradient variance}: reward signals are sparse and noisy; gradients have much higher variance than cross-entropy on curated data.
  \item \textbf{高梯度方差}：奖励信号稀疏且有噪声；梯度方差远高于在精心整理的数据上计算交叉熵时的方差。
  \item \textbf{Smaller updates required}: the policy must stay close to the reference model (KL constraint), so learning rates are 10--100$\times$ smaller than SFT.
  \item \textbf{需要更小的更新量}：策略必须保持接近参考模型（KL约束），因此学习率比SFT小10--100倍。
  \item \textbf{No weight decay}: regularization comes from the KL penalty, not weight decay. Adding WD on top can fight the KL constraint.
  \item \textbf{无权重衰减}：正则化来自KL惩罚，而非权重衰减。额外添加权重衰减可能与KL约束冲突。
  \item \textbf{Shorter warmup}: RL starts from a converged SFT checkpoint---the optimizer state needs minimal warmup.
  \item \textbf{更短的预热}：RL从已收敛的SFT检查点开始——优化器状态只需极少的预热。
\end{itemize}
\end{keybox}


\subsection{Recommended Hyperparameters by RL Method}
\subsection{按RL方法推荐超参数}
\label{recommended-hyperparameters-by-rl-method}


\begin{table}[ht!]
\centering
\caption{Optimizer settings for RL training phases. All use $\beta_1=0.9$, $\beta_2=0.95$, $\epsilon=10^{-8}$, \texttt{max\_grad\_norm}=1.0, BF16.}
\caption{RL训练阶段的优化器设置。所有设置均使用 $\beta_1=0.9$，$\beta_2=0.95$，$\epsilon=10^{-8}$，\texttt{max\_grad\_norm}=1.0，BF16。}
{\footnotesize
\begin{tabular}{@{}llllll@{}}
\toprule
\textbf{Method} & \textbf{Optimizer} & \textbf{LR} & \textbf{WD} & \textbf{Warmup} & \textbf{Schedule} \\
\textbf{方法} & \textbf{优化器} & \textbf{学习率} & \textbf{权重衰减} & \textbf{预热步数} & \textbf{调度策略} \\
\midrule
DPO & AdamW & $5\text{e-}7$ & 0.0 & 50 steps & Constant or Linear \\
DPO & AdamW & $5\text{e-}7$ & 0.0 & 50步 & 常数或线性 \\
PPO (policy) & AdamW & $1\text{e-}6$ & 0.0 & 20 steps & Constant \\
PPO（策略） & AdamW & $1\text{e-}6$ & 0.0 & 20步 & 常数 \\
PPO (critic) & AdamW & $1\text{e-}6$ & 0.0 & 20 steps & Constant \\
PPO（评论家） & AdamW & $1\text{e-}6$ & 0.0 & 20步 & 常数 \\
GRPO & AdamW & $1\text{e-}6$ & 0.0 & 20 steps & Constant \\
GRPO & AdamW & $1\text{e-}6$ & 0.0 & 20步 & 常数 \\
\bottomrule
\end{tabular}
}
\end{table}


\begin{intuitionbox}[Why Constant Schedule for RL?]
\begin{intuitionbox}[为什么RL使用常数调度？]
Cosine and linear-decay schedules assume a fixed training horizon and monotonically decreasing loss. RL training has neither: reward may plateau, spike, or oscillate unpredictably. A constant LR (after brief warmup) keeps the optimizer responsive throughout training. If you must decay, use a very gentle linear schedule with a high minimum LR ratio ($\geq 0.5$).
余弦和线性衰减调度假设固定的训练步数和单调递减的损失。RL训练两者都不具备：奖励可能停滞、突增或不可预测地振荡。常数学习率（经过短暂预热后）使优化器在整个训练过程中保持响应。如果必须衰减，请使用非常平缓的线性调度，并设置较高的最小学习率比例（$\geq 0.5$）。
\end{intuitionbox}

## Beta-2 = 0.95 for RL: Faster Adaptation
## 强化学习中 Beta-2 = 0.95：更快的自适应

The default Adam $\beta_2 = 0.999$ gives a very long memory for the second moment ($\sim$1000-step effective window). In RL training, the loss landscape changes rapidly as the policy evolves---the gradient variance from 1000 steps ago is irrelevant. Using $\beta_2 = 0.95$ shortens the window to $\sim$20 steps, making the adaptive learning rate respond quickly to changing gradient statistics.
默认的 Adam $\beta_2 = 0.999$ 为二阶矩提供了非常长的记忆（有效窗口约为 1000 步）。在强化学习训练中，损失函数地形随着策略的演化而快速变化——1000 步之前的梯度方差已无关紧要。使用 $\beta_2 = 0.95$ 可将窗口缩短至约 20 步，使自适应学习率能够快速响应变化的梯度统计量。

\begin{warningbox}[When beta2 = 0.95 Hurts]
\begin{warningbox}[何时 beta2 = 0.95 会造成损害]
For very small batch sizes (e.g., batch=1 in online RL), $\beta_2 = 0.95$ can make the second moment estimates too noisy. In this regime, use $\beta_2 = 0.99$ as a compromise, or increase the effective batch size via gradient accumulation.
对于非常小的批次大小（例如在线 RL 中 batch=1），$\beta_2 = 0.95$ 会使二阶矩估计过于嘈杂。在这种情况下，作为一种折中方案使用 $\beta_2 = 0.99$，或者通过梯度累积增加有效批次大小。
\end{warningbox}

## Mixed Precision for RL: FP32 Master Weights Are Critical
## 强化学习中的混合精度：FP32 主权重至关重要

RL training is particularly sensitive to numerical precision:
强化学习训练对数值精度特别敏感：

\begin{itemize}
  \item Gradients are noisier---small updates must accumulate accurately over many steps
  \item 梯度更嘈杂——小的更新必须在多步中精确累积
  \item Learning rates are very small ($10^{-6}$--$10^{-7}$), making $\Delta\theta \ll \theta$
  \item 学习率非常小（$10^{-6}$--$10^{-7}$），使得 $\Delta\theta \ll \theta$
  \item BF16 mantissa (7 bits $\approx$ 0.8\% relative precision) cannot represent updates of magnitude $10^{-6}$ relative to weights of magnitude $10^{0}$
  \item BF16 的尾数（7 位，相对精度约 0.8%）无法表示相对于量级为 $10^{0}$ 的权重量级为 $10^{-6}$ 的更新
\end{itemize}

\textbf{Always use FP32 master weights for RL training.} BF16-only training (no FP32 copy) reliably causes reward collapse in PPO/GRPO after 100--500 steps.
\textbf{始终在强化学习训练中使用 FP32 主权重。} 纯 BF16 训练（无 FP32 副本）在 PPO/GRPO 中 100-500 步后必然导致奖励崩溃。

## Gradient Clipping is Critical for RL
## 梯度裁剪对强化学习至关重要

In PPO and GRPO, the reward signal can be highly variable, especially early in training. A single bad batch can produce gradients with norm $>100$, which would completely destroy the model weights. \texttt{max\_grad\_norm=1.0} is the standard setting. For SFT, clipping is less critical but still recommended.
在 PPO 和 GRPO 中，奖励信号可能高度可变，尤其是在训练早期。单个坏批次可能产生范数 $>100$ 的梯度，这会完全破坏模型权重。\texttt{max\_grad\_norm=1.0} 是标准设置。对于 SFT，裁剪不那么关键但仍推荐使用。

\begin{warningbox}[Never Disable Gradient Clipping for RL]
\begin{warningbox}[切勿在强化学习中禁用梯度裁剪]
Unlike SFT where gradient norms are typically stable (0.1--1.0 range), RL gradients are spiky because: (1)~reward variance propagates through the policy gradient, (2)~rare high-reward trajectories create outsized updates, and (3)~the KL penalty term can produce large gradients when the policy drifts. A single unclipped step with $\|\nabla\| > 50$ can undo hundreds of training steps.
与 SFT 中梯度范数通常稳定（0.1-1.0 范围）不同，RL 梯度呈尖峰状，因为：(1) 奖励方差通过策略梯度传播；(2) 罕见的高奖励轨迹会产生过大的更新；(3) 当策略漂移时，KL 惩罚项可能产生大的梯度。一个未裁剪的 $\|\nabla\| > 50$ 的单步可以抵消数百步的训练。
\end{warningbox}

## Diagnosing RL Training Instability
## 诊断强化学习训练不稳定性

\begin{examplebox}[Red Flags and Fixes for RL Optimization]
\begin{examplebox}[强化学习优化的危险信号与修复措施]
{\small
\begin{tabular}{@{}lp{9.5cm}@{}}
\toprule
\textbf{Symptom} & \textbf{Likely Cause and Fix} \\
\textbf{症状} & \textbf{可能原因与修复} \\
\midrule
Reward improves then collapses & LR too high or KL coefficient too low. Reduce LR by 2--5$\times$ or increase $\beta_\text{KL}$. \\
奖励提升后崩溃 & 学习率过高或 KL 系数过低。将学习率降低 2-5 倍或增加 $\beta_\text{KL}$。 \\
Gradient norm constantly at clip threshold & Updates too aggressive. Reduce LR (clipping means you’re losing gradient direction info every step). \\
梯度范数持续处于裁剪阈值 & 更新过于激进。降低学习率（裁剪意味着每一步都在丢失梯度方向信息）。 \\
KL divergence explodes ($>$15 nats) & LR too high. Reduce by 10$\times$ or add adaptive KL penalty. \\
KL 散度爆炸（$>$15 nats） & 学习率过高。降低 10 倍或添加自适应 KL 惩罚。 \\
Reward stuck at baseline & LR too low, or reward model has low signal. Try 2--5$\times$ higher LR. Check reward model calibration. \\
奖励停滞在基线 & 学习率过低，或奖励模型信号弱。尝试将学习率提高 2-5 倍。检查奖励模型校准。 \\
Loss NaN after 100+ steps & FP32 master weights missing, or grad norm overflow. Enable FP32 master weights; verify BF16 mode. \\
100 步后损失 NaN & FP32 主权重缺失，或梯度范数溢出。启用 FP32 主权重；检查 BF16 模式。 \\
\bottomrule
\end{tabular}
}
\end{examplebox}

## HuggingFace TRL Configuration for RL
## 用于强化学习的 HuggingFace TRL 配置

The TRL library~\cite{vonwerra2022trl} provides production-ready implementations of PPO, DPO, and other RL methods for LLMs.
TRL 库~\cite{vonwerra2022trl} 为 LLM 提供了 PPO、DPO 以及其他 RL 方法的生产级实现。

\begin{lstlisting}[style=pythonstyle, caption={Complete PPO and DPO optimizer configuration using TRL.}]
\begin{lstlisting}[style=pythonstyle, caption={使用 TRL 的完整 PPO 和 DPO 优化器配置。}]
from trl import PPOConfig, PPOTrainer, DPOConfig, DPOTrainer


# --- PPO Configuration ---
# --- PPO 配置 ---
ppo_config = PPOConfig(
    # Optimizer (AdamW with RL-specific settings)
    # 优化器（带有 RL 特定设置的 AdamW）
    learning_rate=1e-6,           # 10-100x smaller than SFT
                                  # 比 SFT 小 10-100 倍
    
    # PPO-specific
    # PPO 特定
    ppo_epochs=4,                 # mini-batch updates per rollout
                                  # 每次收集的迷你批次更新次数
    mini_batch_size=16,
    batch_size=64,                # rollout batch size
                                  # 收集批次大小
    
    # Gradient control
    # 梯度控制
    max_grad_norm=1.0,
    
    # KL penalty (replaces weight decay as regularizer)
    # KL 惩罚（替代权重衰减作为正则化器）
    init_kl_coef=0.2,            # initial KL penalty coefficient
                                  # 初始 KL 惩罚系数
    adap_kl_ctrl=True,           # adaptive KL targeting
                                  # 自适应 KL 目标
    target_kl=6.0,               # target KL divergence
                                  # 目标 KL 散度
    
    # Mixed precision
    # 混合精度
    bf16=True,                   # BF16 compute, FP32 master weights
                                  # BF16 计算，FP32 主权重
)


ppo_trainer = PPOTrainer(
    model=model,
    ref_model=ref_model,
    config=ppo_config,
    tokenizer=tokenizer,
    dataset=dataset,
)


# --- DPO Configuration ---
# --- DPO 配置 ---
dpo_config = DPOConfig(
    output_dir="./dpo_output",
    
    # Optimizer
    # 优化器
    learning_rate=5e-7,           # even smaller than PPO
                                  # 比 PPO 更小
    optim="adamw_torch",
    adam_beta1=0.9,
    adam_beta2=0.95,              # shorter memory for RL
                                  # 对 RL 使用更短的记忆
    weight_decay=0.0,            # no WD -- KL provides regularization
                                  # 无权重衰减——KL 提供正则化
    
    # Schedule
    # 学习率调度
    lr_scheduler_type="constant_with_warmup",
    warmup_steps=50,
    
    # Gradient control
    # 梯度控制
    max_grad_norm=1.0,
    
    # DPO-specific
    # DPO 特定
    beta=0.1,                    # KL constraint strength
                                  # KL 约束强度
    loss_type="sigmoid",         # standard DPO loss
                                  # 标准 DPO 损失
    
    # Mixed precision
    # 混合精度
    bf16=True,
    
    # Training
    # 训练
    num_train_epochs=1,          # DPO typically 1 epoch
                                  # DPO 通常为 1 个 epoch
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
)


dpo_trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=dpo_config,
    train_dataset=dataset,
    tokenizer=tokenizer,
)
dpo_trainer.train()
\end{lstlisting}

## MoE Considerations for RL Training
## 强化学习训练中的 MoE 注意事项

\begin{intuitionbox}[MoE for RLHF]
\begin{intuitionbox}[用于 RLHF 的 MoE]
Mixture-of-Experts (MoE) models~\cite{fedus2022switch} are increasingly used in RLHF:
混合专家（MoE）模型~\cite{fedus2022switch} 在 RLHF 中使用日益增多：

\begin{itemize}
  \item \textbf{Advantage}: 3--4$\times$ more capacity at same compute cost. Better for reward models (more capacity to judge).
  \item \textbf{优势}：在相同计算成本下容量提升 3-4 倍。更适合奖励模型（有更多容量进行判断）。
  \item \textbf{Challenge}: Expert parallelism requires all-to-all communication (tokens routed across GPUs). This conflicts with pipeline parallelism.
  \item \textbf{挑战}：专家并行需要全对全通信（令牌跨 GPU 路由）。这与流水线并行冲突。
  \item \textbf{GRPO with MoE}: Works well since generation cost is dominated by active params (not total params).
  \item \textbf{结合 MoE 的 GRPO}：效果良好，因为生成成本由活跃参数（而非总参数）主导。
  \item \textbf{LoRA for MoE}: Can apply LoRA to router + shared layers only, or to all experts (expensive).
  \item \textbf{面向 MoE 的 LoRA}：可以仅对路由器+共享层应用 LoRA，或对所有专家应用（代价昂贵）。
\end{itemize}
\end{intuitionbox}

\begin{intuitionbox}[The RL Optimizer Mantra]
\begin{intuitionbox}[RL 优化器口诀]
For RL fine-tuning: \textbf{small LR, no weight decay, constant schedule, FP32 master weights, aggressive clipping}. Let the KL penalty handle regularization---the optimizer’s job is just to follow the policy gradient without overshooting.
对于强化学习微调：\textbf{小学习率，无权重衰减，恒定调度，FP32 主权重，激进裁剪}。让 KL 惩罚处理正则化——优化器的工作仅仅是跟随策略梯度而不越界。
\end{intuitionbox}