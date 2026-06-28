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
