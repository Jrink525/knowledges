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
