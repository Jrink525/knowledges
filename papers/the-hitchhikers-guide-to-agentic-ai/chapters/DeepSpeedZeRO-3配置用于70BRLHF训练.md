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


