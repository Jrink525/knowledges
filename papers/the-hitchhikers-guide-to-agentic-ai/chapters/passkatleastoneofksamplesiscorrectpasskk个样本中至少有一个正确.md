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
---

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


