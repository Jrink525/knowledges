# v 非常小 -> Adam 尚未预热，延长预热步数
\end{lstlisting}
\end{examplebox}


\begin{intuitionbox}[The Learning Rate is the Most Important Hyperparameter]
In practice, getting the learning rate right matters more than any other hyperparameter. A rule of thumb for LLM fine-tuning:

\begin{itemize}
  \item Start with the values in the table above
  \item If loss diverges (increases after initial decrease): LR is too high
  \item If loss decreases very slowly and plateaus early: LR is too low
  \item If loss is unstable (oscillates): LR is too high or warmup is too short
\end{itemize}

The second most important hyperparameter is batch size (affects gradient noise and effective LR via the linear scaling rule). Everything else is secondary.
\end{intuitionbox}

\begin{intuitionbox}[学习率是最重要的超参数]
在实践中，正确设置学习率比其他任何超参数都更重要。LLM微调的经验法则：

\begin{itemize}
  \item 从上面表格中的值开始
  \item 如果损失发散（在初始下降后增加）：学习率过高
  \item 如果损失下降非常缓慢且早期停滞：学习率过低
  \item 如果损失不稳定（震荡）：学习率过高或预热步数不足
\end{itemize}

第二重要的超参数是批次大小（通过线性缩放规则影响梯度噪声和有效学习率）。其他一切都是次要的。
\end{intuitionbox}

\section{Flash Attention -- Algorithm and Hardware Awareness}
\label{flash-attention-algorithm-and-hardware-awareness}

\section{Flash Attention —— 算法与硬件感知}
\label{flash-attention-algorithm-and-hardware-awareness}

Flash Attention~\cite{dao2022flashattention, dao2023flashattention2} is one of the most impactful algorithmic innovations in deep learning since the transformer itself. It does not change the mathematical result of attention -- it computes \emph{exactly} the same output -- but it restructures the memory access pattern so that the GPU's limited fast SRAM does all the heavy lifting, cutting HBM footprint from $O(n^2)$ to $O(n)$ and delivering 2--4$\times$ end-to-end wall-clock gains on typical workloads.

Flash Attention~\cite{dao2022flashattention, dao2023flashattention2} 是自Transformer以来深度学习中最具影响力的算法创新之一。它不改变注意力的数学结果 —— 它计算出的输出 **完全相同** —— 而是重构了内存访问模式，使得GPU有限的快速SRAM承担所有繁重工作，将HBM占用从 $O(n^2)$ 削减到 $O(n)$，在典型工作负载上实现2–4倍的端到端加速。

\subsection{The Standard Attention Memory Problem}
\label{the-standard-attention-memory-problem}

\subsection{标准注意力的内存问题}
\label{the-standard-attention-memory-problem}

Standard scaled dot-product attention is: 
\[
\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}}\right) V
\]

标准缩放点积注意力为：
\[
\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}}\right) V
\]

\begin{keybox}[Standard Attention Memory Complexity]
For sequence length $n$ and head dimension $d$:

\begin{itemize}
  \item $Q, K, V \in \mathbb{R}^{n \times d}$: $O(nd)$ memory
  \item $S = QK^T \in \mathbb{R}^{n \times n}$: \textbf{$O(n^2)$ memory} -- the bottleneck
  \item $P = \text{softmax}(S) \in \mathbb{R}^{n \times n}$: another $O(n^2)$
  \item $O = PV \in \mathbb{R}^{n \times d}$: $O(nd)$
\end{itemize}

At $n=8192$, $d=128$, BF16: the attention matrix alone is $8192^2 \times 2 \approx 134$ MB \emph{per head}. With 32 heads, that is 4.3 GB just for one layer's attention scores.
\end{keybox}

\begin{keybox}[标准注意力的内存复杂度]
对于序列长度 $n$ 和头维度 $d$：

\begin{itemize}
  \item $Q, K, V \in \mathbb{R}^{n \times d}$：$O(nd)$ 内存
  \item $S = QK^T \in \mathbb{R}^{n \times n}$：\textbf{$O(n^2)$ 内存} —— 瓶颈
  \item $P = \text{softmax}(S) \in \mathbb{R}^{n \times n}$：又一个 $O(n^2)$
  \item $O = PV \in \mathbb{R}^{n \times d}$：$O(nd)$
\end{itemize}

当 $n=8192$, $d=128$, BF16 时：仅注意力矩阵就是 $8192^2 \times 2 \approx 134$ MB \emph{每头}。有 32 个注意力头，那么仅一层注意力分数就需要 4.3 GB。
\end{keybox}

\begin{intuitionbox}[Why $O(n^2)$ is Catastrophic]
The attention matrix must be written to HBM (it does not fit in SRAM for long sequences), then read back for the softmax, then read again for the $PV$ product. Each of these HBM round-trips is slow. For $n=32768$ (32K context), the attention matrix is $32768^2 \times 2 \approx 2$ GB \emph{per head} -- completely infeasible to store.
\end{intuitionbox}

\begin{intuitionbox}[为什么 $O(n^2)$ 是灾难性的]
注意力矩阵必须写入 HBM（对于长序列它无法放入 SRAM），然后为了 softmax 读取回来，再为了 $PV$ 乘积读取一次。每一次 HBM 往返都很慢。对于 $n=32768$（32K 上下文），注意力矩阵是 $32768^2 \times 2 \approx 2$ GB \emph{每头} —— 完全无法存储。
\end{intuitionbox}

\subsection{The Flash Attention Key Insight -- Tiling and Online Softmax}
\label{the-flash-attention-key-insight-tiling-and-online-softmax}

\subsection{Flash Attention 的关键洞察 —— 分块与在线 Softmax}
\label{the-flash-attention-key-insight-tiling-and-online-softmax}

The core insight is: \textbf{we never need the full $n \times n$ matrix in memory at once}. We can compute the output $O$ block-by-block if we use the \emph{online softmax} trick.

核心洞察是：**我们永远不需要一次性将完整的 $n \times n$ 矩阵放入内存**。如果使用 *在线 softmax* 技巧，我们可以逐块计算输出 $O$。

\paragraph{Online Softmax.}
\label{online-softmax.}

\paragraph{在线 Softmax。}
\label{online-softmax.}

Recall that softmax requires a global maximum for numerical stability: 
\[
\text{softmax}(x_i) = \frac{e^{x_i - m}}{\sum_j e^{x_j - m}}, \quad m = \max_j x_j
\]

回忆一下，softmax 需要全局最大值以保证数值稳定性：
\[
\text{softmax}(x_i) = \frac{e^{x_i - m}}{\sum_j e^{x_j - m}}, \quad m = \max_j x_j
\]

The trick: we can \emph{update} the running maximum and normalization factor as we process new blocks, without ever materializing the full row.

技巧：在处理新块时，我们可以**更新**运行中的最大值和归一化因子，而不必实现完整的行。

\begin{keybox}[Online Softmax Update Rule]
Given a running state $(m_{\text{old}}, \ell_{\text{old}}, O_{\text{old}})$ and a new block of scores $s_{\text{new}}$:

\begin{enumerate}
  \item $m_{\text{new}} = \max(m_{\text{old}},\; \max(s_{\text{new}}))$
  \item $\ell_{\text{new}} = e^{m_{\text{old}} - m_{\text{new}}} \cdot \ell_{\text{old}}
        + \sum\_j e^{s\_{\text{new},j} - m\_{\text{new}}}$
  \item $O_{\text{new}} = \frac{1}{\ell_{\text{new}}} \left(
        e^{m\_{\text{old}} - m_{\text{new}}} \cdot \ell\_{\text{old}} \cdot O\_{\text{old}}
        + e^{s\_{\text{new}} - m\_{\text{new}}} \cdot V\_{\text{new}} \right)$
\end{enumerate}

This is mathematically equivalent to computing softmax over all blocks at once.
\end{keybox}

\begin{keybox}[在线 Softmax 更新规则]
给定一个运行状态 $(m_{\text{old}}, \ell_{\text{old}}, O_{\text{old}})$ 和一个新的分数块 $s_{\text{new}}$：

\begin{enumerate}
  \item $m_{\text{new}} = \max(m_{\text{old}},\; \max(s_{\text{new}}))$
  \item $\ell_{\text{new}} = e^{m_{\text{old}} - m_{\text{new}}} \cdot \ell_{\text{old}}
        + \sum\_j e^{s\_{\text{new},j} - m\_{\text{new}}}$
  \item $O_{\text{new}} = \frac{1}{\ell_{\text{new}}} \left(
        e^{m\_{\text{old}} - m_{\text{new}}} \cdot \ell\_{\text{old}} \cdot O\_{\text{old}}
        + e^{s\_{\text{new}} - m\_{\text{new}}} \cdot V\_{\text{new}} \right)$
\end{enumerate}

这在数学上等价于一次性对所有块计算 softmax。
\end{keybox}

\subsection{The Flash Attention Algorithm}
\label{the-flash-attention-algorithm}

\subsection{Flash Attention 算法}
\label{the-flash-attention-algorithm}

\begin{examplebox}[Flash Attention Forward Pass – Block Tiling]
\textbf{Setup:} SRAM size $M$. Block sizes $B_r = \lceil M / (4d) \rceil$, $B_c = \min(\lceil M / (4d) \rceil, d)$.

\begin{enumerate}
  \item Divide $Q$ into $T_r = \lceil n / B_r \rceil$ blocks $Q_1, \ldots, Q_{T_r}$
  \item Divide $K, V$ into $T_c = \lceil n / B_c \rceil$ blocks $K_1, \ldots, K_{T_c}$
  \item Initialize output $O \in \mathbb{R}^{n \times d}$, running max $m \in \mathbb{R}^n$, running sum $\ell \in \mathbb{R}^n$ (all in HBM)
  \item \textbf{Outer loop} over $j = 1, \ldots, T_c$:
  \begin{enumerate}
    \item Load $K_j, V_j$ from HBM to SRAM
    \item \textbf{Inner loop} over $i = 1, \ldots, T_r$:
    \begin{enumerate}
      \item Load $Q_i, O_i, m_i, \ell_i$ from HBM to SRAM
      \item Compute $S_{ij} = Q_i K_j^T / \sqrt{d}$ (stays in SRAM)
      \item Apply online softmax update to get new $m_i, \ell_i, O_i$
      \item Write $O_i, m_i, \ell_i$ back to HBM
    \end{enumerate}
  \end{enumerate}
  \item Return $O$
\end{enumerate}

\textbf{Key:} $S_{ij}$ (the attention tile) is computed and discarded in SRAM. It is \emph{never written to HBM}.
\end{examplebox}

\begin{examplebox}[Flash Attention 前向传播 —— 块分块]
\textbf{设置：} SRAM 大小 $M$。块大小 $B_r = \lceil M / (4d) \rceil$，$B_c = \min(\lceil M / (4d) \rceil, d)$。

\begin{enumerate}
  \item 将 $Q$ 划分为 $T_r = \lceil n / B_r \rceil$ 个块 $Q_1, \ldots, Q_{T_r}$
  \item 将 $K, V$ 划分为 $T_c = \lceil n / B_c \rceil$ 个块 $K_1, \ldots, K_{T_c}$
  \item 初始化输出 $O \in \mathbb{R}^{n \times d}$，运行中的最大值 $m \in \mathbb{R}^n$，运行中的和 $\ell \in \mathbb{R}^n$（全部在 HBM 中）
  \item \textbf{外层循环} 遍历 $j = 1, \ldots, T_c$：
  \begin{enumerate}
    \item 将 $K_j, V_j$ 从 HBM 加载到 SRAM
    \item \textbf{内层循环} 遍历 $i = 1, \ldots, T_r$：
    \begin{enumerate}
      \item 将 $Q_i, O_i, m_i, \ell_i$ 从 HBM 加载到 SRAM
      \item 计算 $S_{ij} = Q_i K_j^T / \sqrt{d}$（保留在 SRAM 中）
      \item 应用在线 softmax 更新以获得新的 $m_i, \ell_i, O_i$
      \item 将 $O_i, m_i, \ell_i$ 写回 HBM
    \end{enumerate}
  \end{enumerate}
  \item 返回 $O$
\end{enumerate}

\textbf{关键：} $S_{ij}$（注意力块）在 SRAM 中计算并丢弃。它 **从未被写入 HBM**。
\end{examplebox}

\begin{keybox}[Flash Attention Complexity]
\begin{tabular}{@{}lp{5cm}p{6.5cm}@{}}
\toprule
 & \textbf{Standard Attention} & \textbf{Flash Attention} \\
\midrule
Memory (HBM) & $O(n^2)$ & $O(n)$ \\
HBM reads/writes & $O(n^2 d)$ & $O(n^2 d / M)$ \\
FLOPs & $O(n^2 d)$ & $O(n^2 d)$ (same) \\
Speedup & 1$\times$ & 2--4$\times$ \\
\bottomrule
\end{tabular}

In the forward pass, the total FLOPs remain $O(n^2 d)$ -- identical to standard attention. Flash Attention gains speed entirely by slashing slow HBM traffic, not by reducing arithmetic. (The backward pass actually performs \emph{more} FLOPs due to recomputation, but the wall-clock time is still lower because the saved memory bandwidth dominates.)
\end{keybox}

\begin{keybox}[Flash Attention 复杂度]
\begin{tabular}{@{}lp{5cm}p{6.5cm}@{}}
\toprule
 & \textbf{标准注意力} & \textbf{Flash Attention} \\
\midrule
内存（HBM） & $O(n^2)$ & $O(n)$ \\
HBM 读写次数 & $O(n^2 d)$ & $O(n^2 d / M)$ \\
FLOPs & $O(n^2 d)$ & $O(n^2 d)$（相同） \\
加速比 & 1$\times$ & 2--4$\times$ \\
\bottomrule
\end{tabular}

在前向传播中，总 FLOPs 仍然是 $O(n^2 d)$ —— 与标准注意力相同。Flash Attention 完全通过削减慢速 HBM 流量来获得速度，而不是减少算术运算。（由于重计算，反向传播实际上执行了 *更多* 的 FLOPs，但挂钟时间仍然更低，因为节省的内存带宽占主导。）
\end{keybox}

\subsection{Flash Attention 2 -- Better Parallelism}
\label{flash-attention-2-better-parallelism}

\subsection{Flash Attention 2 —— 更好的并行性}
\label{flash-attention-2-better-parallelism}

Flash Attention 2~\cite{dao2023flashattention2} made three key improvements:

\begin{enumerate}
  \item \textbf{Reduced non-matmul FLOPs:} The original FA had unnecessary rescaling operations in the inner loop. FA2 restructures the loop to minimize these. On A100, Tensor Core matrix multiplications outpace scalar operations by roughly 16$\times$, so even a small fraction of non-matmul work in the inner loop becomes the latency bottleneck.
  \item \textbf{Better parallelism across sequence dimension:} FA1 parallelized over batch and heads only. FA2 also parallelizes over the query sequence dimension, enabling better GPU utilization for long sequences with small batch sizes.
  \item \textbf{Causal masking optimization:} For autoregressive (causal) attention, roughly half the blocks are fully masked. FA2 skips these blocks entirely, giving $\sim$2$\times$ speedup for causal attention vs.~bidirectional.
\end{enumerate}

Flash Attention 2~\cite{dao2023flashattention2} 做出了三项关键改进：

\begin{enumerate}
  \item \textbf{减少非矩阵乘法 FLOPs：} 原始 FA 在内循环中有不必要的重缩放操作。FA2 重构循环以最小化这些操作。在 A100 上，Tensor Core 矩阵乘法的速度约为标量运算的 16 倍，因此内循环中即使很小的非矩阵乘法工作量也会成为延迟瓶颈。
  \item \textbf{沿序列维度的更好并行性：} FA1 仅对批处理和注意力头进行并行化。FA2 还对查询序列维度进行并行化，从而在小批次大小的长序列上实现更好的 GPU 利用率。
  \item \textbf{因果掩码优化：} 对于自回归（因果）注意力，大约一半的块是完全掩码的。FA2 完全跳过这些块，使得因果注意力相比双向注意力获得 $\sim$2 倍的加速。
\end{enumerate}
```

\subsection{Flash Attention 3 -- Hopper Architecture}
\subsection{Flash Attention 3 -- Hopper 架构}
\label{flash-attention-3-hopper-architecture}

Flash Attention 3~\cite{shah2024flashattention3} is designed specifically for H100 and exploits three Hopper-specific features:
Flash Attention 3~\cite{shah2024flashattention3} 专门为 H100 设计，利用了 Hopper 的三个特有功能：

\begin{itemize}
  \item \textbf{TMA (Tensor Memory Accelerator):} H100 has a dedicated hardware unit for asynchronous bulk data movement between HBM and SRAM. FA3 uses TMA to overlap data loading with computation, hiding memory latency.
  \item \textbf{TMA（张量内存加速器）：} H100 拥有专用硬件单元，用于在 HBM 和 SRAM 之间进行异步批量数据移动。FA3 使用 TMA 将数据加载与计算重叠，从而隐藏内存延迟。
  \item \textbf{Warp-specialization:} FA3 assigns different warps to different roles (producer warps load data via TMA; consumer warps compute MMA). This is a software pipelining technique that keeps both the memory system and Tensor Cores busy simultaneously.
  \item \textbf{Warp 专业化：} FA3 将不同的 warp 分配给不同的角色（生产者 warp 通过 TMA 加载数据；消费者 warp 计算 MMA）。这是一种软件流水线技术，可同时保持内存系统和 Tensor Core 忙碌。
  \item \textbf{FP8 support:} H100 supports FP8 (E4M3/E5M2) Tensor Core operations at 2$\times$ the throughput of BF16. FA3 supports FP8 attention with per-block quantization to maintain accuracy.
  \item \textbf{FP8 支持：} H100 支持 FP8（E4M3/E5M2）Tensor Core 运算，吞吐量是 BF16 的 2$\times$。FA3 支持 FP8 注意力，并通过逐块量化来保持精度。
\end{itemize}

FA3 achieves up to \textbf{75\% of H100 theoretical peak} for FP16 attention, compared to $\sim$35\% for FA2.
对于 FP16 注意力，FA3 达到了 H100 理论峰值的 \textbf{75\%}，而 FA2 约为 35\%。

\subsection{Flash Attention 4 -- Blackwell Architecture}
\subsection{Flash Attention 4 -- Blackwell 架构}
\label{flash-attention-4-blackwell-architecture}

Flash Attention 4~\cite{zadouri2026flashattention4} targets NVIDIA’s Blackwell GPUs (B200/GB200), which double Tensor Core throughput to 2.25 PFLOP/s (BF16) while non-matmul units (exponential, shared memory bandwidth) scale at a slower rate. This \emph{asymmetric hardware scaling} means that the bottleneck shifts: on Blackwell, attention is limited not by matmul but by the softmax exponentials and shared memory traffic surrounding them.
Flash Attention 4~\cite{zadouri2026flashattention4} 针对 NVIDIA 的 Blackwell GPU（B200/GB200），其 Tensor Core 吞吐量翻倍至 2.25 PFLOP/s（BF16），而非矩阵乘法单元（指数运算、共享内存带宽）的扩展速度较慢。这种 \emph{非对称硬件扩展} 意味着瓶颈发生了转移：在 Blackwell 上，注意力不受矩阵乘法限制，而是受软最大指数运算及其周围的共享内存流量限制。

FA4 addresses this with four key techniques:
FA4 通过四项关键技术来解决这一问题：

\begin{itemize}
  \item \textbf{Fully asynchronous MMA pipelines:} Blackwell’s MMA instructions are fully asynchronous (unlike Hopper’s wgmma which still blocked on completion). FA4 redesigns the pipeline to overlap MMA, TMA loads, and softmax rescaling across larger tile sizes, keeping all hardware units saturated.
  \item \textbf{完全异步的 MMA 流水线：} Blackwell 的 MMA 指令是完全异步的（与 Hopper 的 wgmma 仍在完成时阻塞不同）。FA4 重新设计了流水线，以在更大的 tile 尺寸上重叠 MMA、TMA 加载和软最大重新缩放，使所有硬件单元保持饱和。
  \item \textbf{Software-emulated exponential:} Instead of calling the hardware \texttt{ex2} unit (which is the throughput bottleneck), FA4 emulates $e^x$ using polynomial approximations executed on the much faster Tensor Cores themselves. This trades extra matmul instructions for exponential-unit stalls.
  \item \textbf{软件模拟的指数运算：} FA4 不调用硬件 \texttt{ex2} 单元（这是吞吐量瓶颈），而是在速度更快的 Tensor Core 上使用多项式近似来模拟 $e^x$。这相当于用额外的矩阵乘法指令换取指数单元的停顿。
  \item \textbf{Conditional softmax rescaling:} Standard FlashAttention rescales the running $\max$ every tile. FA4 skips the rescaling when the new tile’s max does not exceed the running max (common in practice), saving both register shuffles and synchronization barriers.
  \item \textbf{条件软最大重新缩放：} 标准的 FlashAttention 在每个 tile 上重新缩放运行中的 $\max$。当新 tile 的最大值不超过运行中的最大值时（实践中常见），FA4 跳过重新缩放，从而节省寄存器重排和同步屏障。
  \item \textbf{Tensor Memory + 2-CTA MMA mode (backward pass):} The backward pass uses Blackwell’s \emph{Tensor Memory} (a per-SM scratchpad larger than shared memory) and a 2-CTA cooperative mode that fuses $dQ$ accumulation across two thread-block clusters, halving shared memory round-trips.
  \item \textbf{Tensor Memory + 2-CTA MMA 模式（反向传播）：} 反向传播使用 Blackwell 的 \emph{Tensor Memory}（一种比共享内存更大的每 SM 暂存器）和一种 2-CTA 协作模式，该模式将两个线程块簇的 $dQ$ 累加融合，将共享内存往返次数减半。
\end{itemize}

\begin{keybox}[FA4 Implementation: CuTe-DSL]
FA4 is the first FlashAttention version written in \textbf{CuTe-DSL}, a Python-embedded domain-specific language for GPU kernels (part of CUTLASS 4.x). CuTe-DSL compiles 20--30$\times$ faster than C++ CUTLASS templates while retaining full control over register allocation and pipeline scheduling. This dramatically lowers the iteration time for kernel development.
\end{keybox}

\begin{keybox}[FA4 实现：CuTe-DSL]
FA4 是第一个用 \textbf{CuTe-DSL} 编写的 FlashAttention 版本，CuTe-DSL 是一种嵌入 Python 的 GPU 内核领域特定语言（属于 CUTLASS 4.x 的一部分）。CuTe-DSL 的编译速度比 C++ CUTLASS 模板快 20--30$\times$，同时保持对寄存器分配和流水线调度的完全控制。这大大降低了内核开发的迭代时间。
\end{keybox}

\paragraph{Results.}
\paragraph{结果}
\label{results.}

On B200 with BF16 head-dim 128 (causal, seq-len 8K):
在 B200 上，使用 BF16，头维度 128（因果，序列长度 8K）：

\begin{itemize}
  \item \textbf{1613 TFLOP/s} -- 71\% of Blackwell peak utilization
  \item \textbf{1613 TFLOP/s} —— Blackwell 峰值利用率的 71\%
  \item \textbf{1.3$\times$} faster than cuDNN~9.13 (NVIDIA’s proprietary fused kernel)
  \item \textbf{1.3$\times$} 比 cuDNN~9.13（NVIDIA 专有的融合内核）更快
  \item \textbf{2.7$\times$} faster than Triton on the same hardware
  \item \textbf{2.7$\times$} 比相同硬件上的 Triton 更快
\end{itemize}

\begin{intuitionbox}[Hardware--Software Co-evolution]
The FlashAttention series illustrates a key principle: each GPU generation shifts the bottleneck, demanding new algorithmic ideas rather than just re-compilation. A80 $\to$ memory bandwidth limited (FA1/FA2: tiling + recomputation). H100 $\to$ data movement limited (FA3: TMA + warp-specialization). B200 $\to$ non-matmul compute limited (FA4: software-emulated exp + conditional rescaling). Understanding \emph{where the hardware bottleneck lies} is the prerequisite for writing efficient kernels.
\end{intuitionbox}

\begin{intuitionbox}[硬件-软件协同演进]
FlashAttention 系列说明了一个关键原则：每一代 GPU 都会改变瓶颈，需要新的算法思想而不仅仅是重新编译。A80 $\to$ 受内存带宽限制（FA1/FA2：分块 + 重计算）。H100 $\to$ 受数据移动限制（FA3：TMA + warp 专业化）。B200 $\to$ 受非矩阵乘法计算限制（FA4：软件模拟指数 + 条件重新缩放）。理解 \emph{硬件瓶颈所在} 是编写高效内核的前提。
\end{intuitionbox}

\section{Pretraining: Best Practices}
\section{预训练：最佳实践}
\label{sec:pretraining}

Pretraining is the most expensive phase of LLM development---consuming millions of GPU-hours and requiring careful orchestration of data, compute, and hyperparameters. This section distills key lessons from Llama-3~\cite{grattafiori2024llama3}, Chinchilla~\cite{hoffmann2022chinchilla}, and GPT-4~\cite{openai2023gpt4}.
预训练是 LLM 开发中最昂贵的阶段——消耗数百万 GPU 小时，需要精心协调数据、计算和超参数。本节提炼了来自 Llama-3~\cite{grattafiori2024llama3}、Chinchilla~\cite{hoffmann2022chinchilla} 和 GPT-4~\cite{openai2023gpt4} 的关键经验。

\subsection{Training Objective}
\subsection{训练目标}
\label{training-objective}

All modern decoder-only LLMs use \textbf{causal language modeling} (CLM): 
所有现代仅解码器的 LLM 都使用 \textbf{因果语言建模}（CLM）：
\[
\mathcal{L}_\text{CLM} = -\frac{1}{T}\sum_{t=1}^T \log P_\theta(x_t \mid x_{<t})
\]
 This simple objective---with enough data and scale---produces emergent capabilities (in-context learning, reasoning, instruction following) without explicit supervision~\cite{brown2020language}.
这个简单的目标——在足够的数据和规模下——无需显式监督即可产生涌现能力（上下文学习、推理、指令遵循）~\cite{brown2020language}。

\subsection{Data Pipeline}
\subsection{数据流水线}
\label{data-pipeline}

\begin{keybox}[Pretraining Data Recipe]
\begin{itemize}
  \item \textbf{Scale}: 1--15 trillion tokens for frontier models (Llama-3: 15T tokens)
  \item \textbf{规模}：前沿模型需要 1--15 万亿个 token（Llama-3：15T tokens）
  \item \textbf{Sources}: Web crawl (80\%), code (10\%), books/papers (5\%), curated (5\%)
  \item \textbf{来源}：网页爬取（80\%）、代码（10\%）、书籍/论文（5\%）、精选数据（5\%）
  \item \textbf{Deduplication}: MinHash + exact substring dedup reduces memorization~\cite{lee2022deduplicating}
  \item \textbf{去重}：MinHash + 精确子串去重减少记忆化~\cite{lee2022deduplicating}
  \item \textbf{Quality filtering}: Perplexity-based classifier, heuristic filters (length, language ID, toxicity)
  \item \textbf{质量过滤}：基于困惑度的分类器、启发式过滤器（长度、语言 ID、有害性）
  \item \textbf{Data mixing}: Temperature-weighted sampling across domains; upweight code and math for reasoning
  \item \textbf{数据混合}：跨领域的温度加权采样；提高代码和数学的权重以增强推理能力
\end{itemize}
\end{keybox}

\subsection{Scaling Laws}
\subsection{缩放定律}
\label{scaling-laws}

Hoffmann et al.~\cite{hoffmann2022chinchilla} showed that compute-optimal training requires balancing model size $N$ and data size $D$: $N_\text{opt} \propto C^{0.50}$, $D_\text{opt} \propto C^{0.50}$. A 70B model is compute-optimal at $\sim$1.4T tokens. In practice, models are \emph{over-trained} (more tokens than Chinchilla-optimal) because inference cost scales with model size, not training tokens---smaller over-trained models are cheaper to deploy.
Hoffmann 等人~\cite{hoffmann2022chinchilla} 表明，计算最优训练需要平衡模型大小 $N$ 和数据大小 $D$：$N_\text{opt} \propto C^{0.50}$，$D_\text{opt} \propto C^{0.50}$。一个 70B 模型在约 1.4T tokens 时达到计算最优。在实践中，模型会被 \emph{过度训练}（token 数超过 Chinchilla 最优值），因为推理成本随模型大小而非训练 token 数增长——较小的过度训练模型部署成本更低。

\subsection{Key Hyperparameters}
\subsection{关键超参数}
\label{key-hyperparameters}

\begin{table}[ht!]
\centering
\caption{Pretraining hyperparameters from published models.}
\caption{已发布模型的预训练超参数。}
\begin{tabular}{@{}lp{2.5cm}p{2.8cm}p{2.8cm}p{2.8cm}@{}}
\toprule
\textbf{Setting} & \textbf{Llama-3 405B} & \textbf{Llama-3 8B} & \textbf{Qwen-2.5 72B} & \textbf{Mistral 7B} \\
\textbf{设置} & \textbf{Llama-3 405B} & \textbf{Llama-3 8B} & \textbf{Qwen-2.5 72B} & \textbf{Mistral 7B} \\
\midrule
Tokens & 15T & 15T & 18T & 8T \\
Token 数 & 15T & 15T & 18T & 8T \\
Batch size (tokens) & 16M & 4M & 4M & 4M \\
批量大小（token） & 16M & 4M & 4M & 4M \\
Peak LR & $8\text{e-}5$ & $3\text{e-}4$ & $3\text{e-}4$ & $3\text{e-}4$ \\
峰值学习率 & $8\text{e-}5$ & $3\text{e-}4$ & $3\text{e-}4$ & $3\text{e-}4$ \\
Schedule & WSD & WSD & Cosine & Cosine \\
调度策略 & WSD & WSD & 余弦 & 余弦 \\
Weight decay & 0.1 & 0.1 & 0.1 & 0.1 \\
权重衰减 & 0.1 & 0.1 & 0.1 & 0.1 \\
Context length & 8192 & 8192 & 4096$\to$32K & 8192 \\
上下文长度 & 8192 & 8192 & 4096$\to$32K & 8192 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Common Failure Modes}
\subsection{常见失败模式}
\label{common-failure-modes}

\begin{warningbox}[Pretraining Pitfalls]
\begin{itemize}
  \item \textbf{Loss spikes}: Sudden loss increases from bad data batches or numerical instability. Llama-3 reports rolling back to checkpoints and skipping offending batches.
  \item \textbf{损失尖峰}：由不良数据批次或数值不稳定性导致的损失突然增加。Llama-3 报告回滚到检查点并跳过有问题的批次。
  \item \textbf{Memorization}: Model regurgitates training data verbatim. Fix: deduplicate aggressively; monitor extraction attacks.
  \item \textbf{记忆化}：模型逐字复述训练数据。修复方法：积极去重；监控提取攻击。
  \item \textbf{Context length}: Training on short sequences then deploying at long context fails. Use continued pretraining on long documents + RoPE scaling.
  \item \textbf{上下文长度}：在短序列上训练然后在长上下文中部署会失败。使用在长文档上的持续预训练 + RoPE 缩放。
\end{itemize}
\end{warningbox}

\section{Supervised Fine-Tuning (SFT)}
\section{监督微调（SFT）}
\label{sec:sft}

SFT transforms a pretrained language model into an instruction-following assistant by training on curated prompt--response pairs. This is the bridge between raw language modeling and RLHF.
SFT 通过在精选的提示-响应对上进行训练，将预训练语言模型转变为指令遵循助手。这是原始语言建模与 RLHF 之间的桥梁。

\subsection{SFT Objective}
\subsection{SFT 目标}
\label{sft-objective}

The loss is identical to CLM, but computed only on \textbf{response tokens}: 
\[
\mathcal{L}_\text{SFT} = -\frac{1}{|y|}\sum_{t=1}^{|y|} \log P_\theta(y_t \mid x_\text{prompt}, y_{<t})
\]
 Prompt tokens provide context but receive no gradient (labels set to $-100$).

该损失与因果语言模型（CLM）相同，但仅在\textbf{响应token}上计算：
\[
\mathcal{L}_\text{SFT} = -\frac{1}{|y|}\sum_{t=1}^{|y|} \log P_\theta(y_t \mid x_\text{prompt}, y_{<t})
\]
提示 token 提供上下文但不接收梯度（标签设为 $-100$）。

\subsection{Data Quality: The LIMA Principle}
\subsection{数据质量：LIMA原则}
\label{data-quality-the-lima-principle}

Zhou et al.~\cite{zhou2023lima} demonstrated that 1,000 carefully curated examples can match models trained on 50K+ noisy examples. Key requirements:

周等人~\cite{zhou2023lima} 证明，1,000个精心策划的示例可以匹配在50K以上噪声示例上训练的模型。关键要求：

\begin{itemize}
  \item \textbf{Diversity}: Cover QA, summarization, code, math, creative writing, multi-turn dialogue
  \item \textbf{多样性}：涵盖问答、摘要、代码、数学、创意写作、多轮对话
  \item \textbf{Correctness}: Every response must be factually accurate and well-formatted
  \item \textbf{正确性}：每个响应必须事实准确且格式良好
  \item \textbf{Length balance}: Mix short (1-sentence) and long (multi-paragraph) responses
  \item \textbf{长度平衡}：混合短（单句）和长（多段落）响应
  \item \textbf{Decontamination}: Remove overlap with evaluation benchmarks
  \item \textbf{去污染}：移除与评估基准的重叠
\end{itemize}

\subsection{Training Configuration}
\subsection{训练配置}
\label{training-configuration}

\begin{lstlisting}[style=pythonstyle]
from trl import SFTTrainer, SFTConfig

sft_config = SFTConfig(
    output_dir="./sft_output",
    max_seq_length=4096,
    packing=True,              # Pack short examples into full sequences
    learning_rate=2e-5,
    lr_scheduler_type="cosine",
    warmup_ratio=0.1,
    weight_decay=0.01,
    max_grad_norm=1.0,
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    bf16=True,
    gradient_checkpointing=True,
)
trainer = SFTTrainer(model=model, args=sft_config,
                     train_dataset=dataset, processing_class=tokenizer)
trainer.train()
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle]
from trl import SFTTrainer, SFTConfig

sft_config = SFTConfig(
    output_dir="./sft_output",
    max_seq_length=4096,
    packing=True,              # 将短示例打包成完整序列
    learning_rate=2e-5,
    lr_scheduler_type="cosine",
    warmup_ratio=0.1,
    weight_decay=0.01,
    max_grad_norm=1.0,
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    bf16=True,
    gradient_checkpointing=True,
)
trainer = SFTTrainer(model=model, args=sft_config,
                     train_dataset=dataset, processing_class=tokenizer)
trainer.train()
\end{lstlisting}

\subsection{Efficient Training Solutions}
\subsection{高效训练方案}
\label{efficient-training-solutions}

Standard HuggingFace training leaves significant performance on the table. Several libraries provide drop-in efficiency gains for SFT workloads:

标准 HuggingFace 训练会留下显著的性能提升空间。多个库为 SFT 工作负载提供了即插即用的效率提升：

\paragraph{Liger Kernel~\cite{hsu2024liger}.}
\paragraph{Liger Kernel~\cite{hsu2024liger}}
\label{liger-kernel-.}

An open-source set of \textbf{Triton-fused kernels} from LinkedIn that replace standard PyTorch operators during training. Key fusions include:

来自 LinkedIn 的一套开源\textbf{Triton 融合内核}，在训练期间替换标准 PyTorch 算子。关键融合包括：

\begin{itemize}
  \item \textbf{Fused Cross-Entropy}: Merges the final linear projection, softmax, and loss computation into a single kernel---avoids materializing the full $(\text{batch} \times \text{seq} \times \text{vocab})$ logit tensor.
  \item \textbf{融合交叉熵}：将最后的线性投影、softmax 和损失计算合并为单个内核——避免实例化完整的 $(\text{batch} \times \text{seq} \times \text{vocab})$ logit 张量。
  \item \textbf{Fused RMSNorm / SwiGLU / RoPE}: Eliminates intermediate memory allocations for common LLM building blocks.
  \item \textbf{融合 RMSNorm / SwiGLU / RoPE}：消除常见 LLM 构建块的中间内存分配。
  \item \textbf{Chunked operations}: Processes large tensors in tiles to keep peak memory bounded.
  \item \textbf{分块操作}：将大张量分块处理以维持峰值内存有界。
\end{itemize}

\textbf{Result}: 20\% higher throughput and up to 60\% memory reduction with a one-line integration (\texttt{apply\_liger\_kernel\_to\_llama()}). Compatible with FSDP, DeepSpeed, and LoRA.

\textbf{结果}：通过一行集成（\texttt{apply\_liger\_kernel\_to\_llama()}）即可实现20%的吞吐量提升和高达60%的内存减少。兼容 FSDP、DeepSpeed 和 LoRA。

\paragraph{Unsloth~\cite{unsloth2024}.}
\paragraph{Unsloth~\cite{unsloth2024}}
\label{unsloth-.}

A specialized fine-tuning library that combines \textbf{custom CUDA/Triton kernels} with aggressive memory optimization:

一个专门的微调库，结合了\textbf{自定义 CUDA/Triton 内核}和激进的内存优化：

\begin{itemize}
  \item Manual backpropagation through LoRA layers (avoids autograd overhead).
  \item 手动反向传播通过 LoRA 层（避免自动求导开销）。
  \item 4-bit QLoRA with fused dequantization---trains 70B models on a single 48~GB GPU.
  \item 带融合反量化的 4 位 QLoRA——在单张 48 GB GPU 上训练 70B 模型。
  \item Intelligent RoPE and attention kernel fusion specific to each architecture (Llama, Mistral, Qwen, Gemma).
  \item 针对每种架构（Llama、Mistral、Qwen、Gemma）的智能 RoPE 和注意力内核融合。
\end{itemize}

\textbf{Result}: 2--5$\times$ faster than vanilla HuggingFace + PEFT, with 60--70\% less VRAM. Particularly impactful for single-GPU and consumer-hardware workflows.

\textbf{结果}：比原始 HuggingFace + PEFT 快 2--5 倍，显存减少 60--70%。对单 GPU 和消费级硬件工作流尤其有效。

\paragraph{torchtune~\cite{torchtune2024}.}
\paragraph{torchtune~\cite{torchtune2024}}
\label{torchtune-.}

Meta’s native PyTorch fine-tuning library (development wound down in 2025), designed around \textbf{composability} rather than monolithic abstractions:

Meta 的原生 PyTorch 微调库（开发于2025年收尾），围绕\textbf{可组合性}而非整体抽象设计：

\begin{itemize}
  \item Pure PyTorch---no trainer class; recipes are readable single-file scripts.
  \item 纯 PyTorch——无训练器类；配方是可读的单文件脚本。
  \item Native integration with \texttt{torch.compile}, FSDP2, and activation checkpointing.
  \item 原生集成 \texttt{torch.compile}、FSDP2 和激活检查点。
  \item First-class support for QLoRA, full fine-tuning, and knowledge distillation.
  \item 一流的 QLoRA、全微调和知识蒸馏支持。
  \item Built-in quantization-aware training (QAT) for post-training compression.
  \item 内置训练后压缩的量化感知训练（QAT）。
\end{itemize}

\textbf{Result}: Comparable speed to custom solutions but with full debuggability and no framework lock-in.

\textbf{结果}：速度与自定义方案相当，但具有完全可调试性且无框架锁定。

\begin{keybox}[Choosing an Efficiency Stack]
\begin{itemize}
  \item \textbf{Quick LoRA/QLoRA on $\leq$1 GPU}: Unsloth (fastest time-to-train, minimal setup)
  \item \textbf{Multi-GPU full fine-tune}: TRL/DeepSpeed + Liger Kernel (best throughput at scale)
  \item \textbf{Research / custom training loops}: torchtune (transparent, hackable, native PyTorch)
\end{itemize}

These are \emph{complementary}: Liger kernels can be used inside both TRL and torchtune workflows.
\end{keybox}

\begin{keybox}[选择效率堆栈]
\begin{itemize}
  \item \textbf{在$\leq$1 GPU上快速LoRA/QLoRA}：Unsloth（训练时间最短，设置最少）
  \item \textbf{多GPU全微调}：TRL/DeepSpeed + Liger Kernel（规模下吞吐量最佳）
  \item \textbf{研究/自定义训练循环}：torchtune（透明、可入侵、原生PyTorch）
\end{itemize}

这些是\emph{互补的}：Liger内核可以在TRL和torchtune工作流中使用。
\end{keybox}

\subsection{Best Practices}
\subsection{最佳实践}
\label{best-practices}

\begin{table}[ht!]
\centering
\caption{SFT training guidelines.}
\begin{tabular}{@{}lp{11cm}@{}}
\toprule
\textbf{Practice} & \textbf{Details} \\
\midrule
Packing & Concatenate multiple short examples into one sequence (separated by EOS). Avoids padding waste. \\
NEFTune~\cite{jain2024neftune} & Add uniform noise to embeddings ($\alpha=5$). Improves MT-Bench by 5--15\% at zero cost. \\
Chat template & Always use the model’s native template. Mismatched templates degrade quality. \\
Epochs & 2--3 for large datasets; up to 5 for small ($<$10K) curated sets. Over-training causes format memorization. \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[ht!]
\centering
\caption{SFT训练指南}
\begin{tabular}{@{}lp{11cm}@{}}
\toprule
\textbf{实践} & \textbf{详情} \\
\midrule
打包 & 将多个短示例连接成一个序列（由EOS分隔）。避免填充浪费。 \\
NEFTune~\cite{jain2024neftune} & 向嵌入添加均匀噪声（$\alpha=5$）。以零成本将MT-Bench提升5--15\%。 \\
聊天模板 & 始终使用模型的原生模板。不匹配的模板会降低质量。 \\
轮数 & 大数据集2-3轮；小数据集（$<$10K）精选集最多5轮。过度训练会导致格式记忆。 \\
\bottomrule
\end{tabular}
\end{table}

\begin{intuitionbox}[SFT Is Not Enough]
SFT teaches format and basic instruction following, but cannot reliably teach: \emph{preference} (which response is better---needs RLHF/DPO), \emph{refusal} (when not to answer---needs safety training), \emph{calibration} (saying ``I don’t know''---needs RL with truthfulness rewards), or \emph{complex reasoning} (multi-step chains---needs RL with verifiable rewards). The full pipeline is: Pretrain $\to$ SFT $\to$ RLHF/DPO.
\end{intuitionbox}

\begin{intuitionbox}[SFT不够]
SFT教会格式和基本的指令遵循，但不能可靠地教会：\emph{偏好}（哪个响应更好——需要RLHF/DPO）、\emph{拒绝}（何时不应回答——需要安全训练）、\emph{校准}（说“我不知道”——需要带诚实奖励的RL）、或\emph{复杂推理}（多步链——需要带可验证奖励的RL）。完整流程是：预训练 $\to$ SFT $\to$ RLHF/DPO。
\end{intuitionbox}

\section{LoRA and Parameter-Efficient Fine-Tuning}
\section{LoRA与参数高效微调}
\label{lora-and-parameter-efficient-fine-tuning}

Full fine-tuning of a 70B model requires storing 70B trainable parameters plus their optimizer states (560+ GB of memory). LoRA~\cite{hu2021lora} (Low-Rank Adaptation) provides a way to fine-tune with $<$1\% of the parameters while achieving comparable quality.

对70B模型进行全微调需要存储700亿可训练参数及其优化器状态（560+ GB内存）。LoRA~\cite{hu2021lora}（低秩适应）提供了一种用$<$1\%的参数进行微调并达到可比质量的方法。

\subsection{The LoRA Insight}
\subsection{LoRA洞察}
\label{the-lora-insight}

\begin{keybox}[LoRA Core Idea]
Instead of updating a full weight matrix $W \in \mathbb{R}^{d \times d}$, learn a low-rank perturbation: 
\[
W' = W + \frac{\alpha}{r} \cdot BA, \quad B \in \mathbb{R}^{d \times r}, \; A \in \mathbb{R}^{r \times d}
\]

\begin{itemize}
  \item $W$ is \textbf{frozen} (no gradients, no optimizer states)
  \item Only $B$ and $A$ are trained: $2 \times d \times r$ parameters instead of $d^2$
  \item At rank $r=16$, $d=4096$: LoRA adds $2 \times 4096 \times 16 = 131K$ params per layer vs.~$16.8M$ for full matrix
  \item $\alpha/r$ scaling controls the magnitude of the update
\end{itemize}
\end{keybox}

\begin{keybox}[LoRA核心思想]
不更新完整的权重矩阵 $W \in \mathbb{R}^{d \times d}$，而是学习一个低秩扰动：
\[
W' = W + \frac{\alpha}{r} \cdot BA, \quad B \in \mathbb{R}^{d \times r}, \; A \in \mathbb{R}^{r \times d}
\]

\begin{itemize}
  \item $W$ 被\textbf{冻结}（无梯度，无优化器状态）
  \item 仅训练 $B$ 和 $A$：$2 \times d \times r$ 个参数而非 $d^2$
  \item 当秩 $r=16$，$d=4096$：LoRA 每层添加 $2 \times 4096 \times 16 = 131K$ 参数，而全矩阵为 $16.8M$
  \item $\alpha/r$ 缩放控制更新的幅度
\end{itemize}
\end{keybox}

\begin{intuitionbox}[Why Low-Rank Works]
Aghajanyan et al.~\cite{aghajanyan2020intrinsic} showed that fine-tuning operates in a very low-dimensional subspace --- the ``intrinsic dimensionality'' of the fine-tuning task is much smaller than the model’s parameter count. A 175B model’s fine-tuning task may have intrinsic dimensionality $<$10,000. LoRA exploits this directly: rank $r$ constrains the update to an $r$-dimensional subspace per weight matrix.
\end{intuitionbox}

\begin{intuitionbox}[为何低秩有效]
Aghajanyan等人~\cite{aghajanyan2020intrinsic}表明，微调在一个非常低维的子空间中进行——微调任务的“固有维度”远小于模型的参数量。175B模型的微调任务可能具有$<$10,000的固有维度。LoRA直接利用这一点：秩 $r$ 将每个权重矩阵的更新约束到一个 $r$ 维子空间。
\end{intuitionbox}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_011_lora-decomposition.png}
\caption{LoRA decomposes the weight update $\Delta W$ into two small matrices $B \times A$. The original weight $W$ remains frozen; only $B$ and $A$ receive gradients. At inference, the product $BA$ can be merged into $W$ with zero overhead.}
\label{fig:lora-decomposition}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_011_lora-decomposition.png}
\caption{LoRA将权重更新$\Delta W$分解为两个小矩阵$B \times A$。原始权重$W$保持冻结；仅$B$和$A$接收梯度。推理时，乘积$BA$可以零开销合并到$W$中。}
\label{fig:lora-decomposition}
\end{figure}

\begin{intuitionbox}[Why the $\alpha/r$ Scaling Matters]
Without scaling, doubling the rank $r$ would roughly double the magnitude of $\Delta W = BA$ (more columns in $B$ contribute to the sum). This means changing rank would also change how much the model is perturbed---you’d need to re-tune the learning rate every time you adjust $r$.

The $\alpha/r$ factor \textbf{normalizes the update magnitude} so that it stays approximately constant regardless of rank: 
\[
W' = W + \frac{\alpha}{r} \cdot BA
\]


\begin{itemize}
  \item \textbf{Fix $\alpha$, sweep $r$}: The effective update magnitude stays $\sim\alpha$ regardless of rank. You can try $r \in \{8, 16, 32, 64\}$ without re-tuning LR.
  \item \textbf{Common practice}: Set $\alpha = r$ (so $\alpha/r = 1$) or $\alpha = 2r$ (so $\alpha/r = 2$). This is a convenient default where the scaling factor is a small integer.
  \item \textbf{Why not just tune LR?} You could, but $\alpha/r$ provides a \emph{rank-independent} knob. Teams can share LR recipes across experiments with different ranks.
  \item \textbf{rsLoRA insight}~\cite{kalajdzievski2023rslora}: At high ranks ($r \geq 64$), empirical evidence shows $\alpha/\sqrt{r}$ is more stable than $\alpha/r$, because the variance of $BA$ scales with $\sqrt{r}$, not $r$.
\end{itemize}
\end{intuitionbox}

\begin{intuitionbox}[为什么 $\alpha/r$ 缩放很重要]
如果没有缩放，将秩 $r$ 加倍会使 $\Delta W = BA$ 的幅值大致加倍（$B$ 中更多的列对求和有贡献）。这意味着改变秩也会改变模型被扰动的程度——每次调整 $r$ 时都需要重新调整学习率。

$\alpha/r$ 因子\textbf{归一化了更新幅值}，使其在不同秩下大致保持恒定：
\[
W' = W + \frac{\alpha}{r} \cdot BA
\]


\begin{itemize}
  \item \textbf{固定 $\alpha$，扫描 $r$}：有效更新幅值在不同秩下保持约为 $\alpha$。你可以尝试 $r \in \{8, 16, 32, 64\}$ 而无需重新调整学习率。
  \item \textbf{常见做法}：设置 $\alpha = r$（即 $\alpha/r = 1$）或 $\alpha = 2r$（即 $\alpha/r = 2$）。这是一种方便的默认设置，缩放因子为一个小整数。
  \item \textbf{为什么不仅仅调整学习率？}你可以这样做，但 $\alpha/r$ 提供了一个\textit{与秩无关}的调节旋钮。团队可以在不同秩的实验之间共享学习率配方。
  \item \textbf{rsLoRA 的洞见}~\cite{kalajdzievski2023rslora}：在高秩 ($r \geq 64$) 下，经验证据表明 $\alpha/\sqrt{r}$ 比 $\alpha/r$ 更稳定，因为 $BA$ 的方差随 $\sqrt{r}$ 而非 $r$ 缩放。
\end{itemize}
\end{intuitionbox}


\subsection{LoRA Hyperparameters}
\label{lora-hyperparameters}
\subsection{LoRA 超参数}
\label{lora-hyperparameters}


Choosing LoRA hyperparameters correctly is critical --- the wrong rank or alpha can either under-fit (too constrained) or waste memory (too expressive).
正确选择 LoRA 超参数至关重要——错误的秩或 alpha 要么导致欠拟合（过于受限），要么浪费内存（过于表达力强）。


\begin{table}[ht!]
\centering
\caption{LoRA hyperparameter guide.}
\caption{LoRA 超参数指南。}
\begin{tabular}{@{}lp{5cm}p{6.5cm}@{}}
\toprule
\textbf{Hyperparameter} & \textbf{Typical Values} & \textbf{Guidance} \\
\textbf{超参数} & \textbf{典型值} & \textbf{指导建议} \\
\midrule
\texttt{r} (rank) & 8, 16, 32, 64 & Higher = more capacity but more memory. Start with 16. \\
\texttt{r} (秩) & 8, 16, 32, 64 & 越高=能力越强但内存越多。从 16 开始。 \\
\texttt{lora\_alpha} & 16, 32 (often $= r$ or $2r$) & Controls update magnitude via $\alpha/r$ scaling. \\
\texttt{lora\_alpha} & 16, 32 (通常 $= r$ 或 $2r$) & 通过 $\alpha/r$ 缩放控制更新幅值。 \\
\texttt{target\_modules} & \texttt{q\_proj, k\_proj, v\_proj, o\_proj} & All attention projections. Add \texttt{gate\_proj, up\_proj, down\_proj} for full coverage. \\
\texttt{target\_modules} & \texttt{q\_proj, k\_proj, v\_proj, o\_proj} & 所有注意力投影。添加 \texttt{gate\_proj, up\_proj, down\_proj} 以获得完整覆盖。 \\
\texttt{lora\_dropout} & 0.0--0.1 & Regularization. Usually 0.05 for small datasets. \\
\texttt{lora\_dropout} & 0.0--0.1 & 正则化。小数据集通常用 0.05。 \\
\texttt{bias} & \texttt{"none"} & Training biases adds minimal params but rarely helps. \\
\texttt{bias} & \texttt{"none"} & 训练偏置项增加极少量参数但很少有帮助。 \\
Learning rate & $1\text{e-}4$ to $3\text{e-}4$ & Higher than full fine-tuning (only adapters update). \\
学习率 & $1\text{e-}4$ 到 $3\text{e-}4$ & 高于全量微调（只有适配器更新）。 \\
\bottomrule
\end{tabular}
\end{table}


\begin{warningbox}[Rank Selection Rules of Thumb]
\begin{itemize}
  \item \textbf{r=8}: Simple tasks (single-domain chat, classification). Very memory-efficient.
  \item \textbf{r=16}: General-purpose fine-tuning. Good default.
  \item \textbf{r=32--64}: Complex tasks (math, code, multi-turn reasoning). Approaches full fine-tune quality.
  \item \textbf{r=128+}: Diminishing returns; consider full fine-tuning or QLoRA with higher rank.
  \item \textbf{Key indicator}: If training loss plateaus well above full fine-tune loss, increase rank.
\end{itemize}
\end{warningbox}

\begin{warningbox}[秩选择经验法则]
\begin{itemize}
  \item \textbf{r=8}：简单任务（单领域对话、分类）。非常节省内存。
  \item \textbf{r=16}：通用微调。良好的默认值。
  \item \textbf{r=32--64}：复杂任务（数学、代码、多轮推理）。接近全量微调质量。
  \item \textbf{r=128+}：收益递减；考虑全量微调或使用更高秩的 QLoRA。
  \item \textbf{关键指标}：如果训练损失明显高于全量微调损失并出现平台期，则增加秩。
\end{itemize}
\end{warningbox}


\subsection{LoRA Variants}
\label{lora-variants}
\subsection{LoRA 变体}
\label{lora-variants}


\begin{table}[ht!]
\centering
\caption{LoRA variants and their innovations.}
\caption{LoRA 变体及其创新点。}
\begin{tabular}{@{}lp{5cm}p{6.5cm}@{}}
\toprule
\textbf{Method} & \textbf{Key Innovation} & \textbf{When to Use} \\
\textbf{方法} & \textbf{关键创新} & \textbf{何时使用} \\
\midrule
\textbf{QLoRA}~\cite{dettmers2023qlora} & 4-bit quantized base + LoRA in BF16. NF4 data type + double quantization. & Fine-tune 70B on single 48GB GPU. \\
\textbf{QLoRA}~\cite{dettmers2023qlora} & 4 位量化基座 + BF16 下的 LoRA。NF4 数据类型 + 双重量化。 & 在单张 48GB GPU 上微调 70B 模型。 \\
\textbf{DoRA}~\cite{liu2024dora} & Decomposes $W$ into magnitude and direction; LoRA updates direction only. & Better generalization for reasoning. \\
\textbf{DoRA}~\cite{liu2024dora} & 将 $W$ 分解为幅值和方向；LoRA 仅更新方向。 & 在推理任务上获得更好的泛化能力。 \\
\textbf{LoRA+}~\cite{hayou2024loraplus} & Different LRs for $A$/$B$ ($\eta_B = \lambda \eta_A$, $\lambda \approx 16$). & Free 2\% gain; no extra cost. \\
\textbf{LoRA+}~\cite{hayou2024loraplus} & 对 $A$/$B$ 使用不同的学习率 ($\eta_B = \lambda \eta_A$, $\lambda \approx 16$)。 & 免费获得 2\% 提升；无额外成本。 \\
\textbf{AdaLoRA}~\cite{zhang2023adalora} & Dynamic rank budget across layers (SVD-based importance). & Very tight compute budget. \\
\textbf{AdaLoRA}~\cite{zhang2023adalora} & 各层动态分配秩预算（基于 SVD 的重要性评估）。 & 计算预算非常紧张时使用。 \\
\textbf{rsLoRA}~\cite{kalajdzievski2023rslora} & Scales by $\alpha/\sqrt{r}$ instead of $\alpha/r$. Stable at high ranks. & When using $r \geq 64$. \\
\textbf{rsLoRA}~\cite{kalajdzievski2023rslora} & 使用 $\alpha/\sqrt{r}$ 而非 $\alpha/r$ 进行缩放。在高秩下稳定。 & 当使用 $r \geq 64$ 时。 \\
\textbf{VeRA}~\cite{kopiczko2024vera} & Shared frozen random $A, B$; trains diagonal scaling only. & Extreme param efficiency. \\
\textbf{VeRA}~\cite{kopiczko2024vera} & 共享冻结的随机 $A, B$；仅训练对角缩放。 & 极端参数效率场景。 \\
\textbf{LoRA-FA} & Freezes $A$ after init; only trains $B$. Halves LoRA memory. & Memory-constrained scenarios. \\
\textbf{LoRA-FA} & 初始化后冻结 $A$；仅训练 $B$。将 LoRA 内存减半。 & 内存受限的场景。 \\
\bottomrule
\end{tabular}
\end{table}


\subsubsection{Key Extensions Explained}
\label{key-extensions-explained}
\subsubsection{关键扩展详解}
\label{key-extensions-explained}


\paragraph{DoRA -- Weight-Decomposed Low-Rank Adaptation.}
\label{dora-weight-decomposed-low-rank-adaptation.}
\paragraph{DoRA——权重解耦低秩适配}
\label{dora-weight-decomposed-low-rank-adaptation.}


DoRA~\cite{liu2024dora} observes that full fine-tuning tends to change the \emph{direction} of weight vectors more than their magnitude. Standard LoRA conflates both. DoRA decomposes each weight column into magnitude $m = \|W\|_\text{col}$ and direction $\hat{V} = W / \|W\|_\text{col}$, then applies LoRA only to the direction: 
\[
W' = m \odot \hat{V}', \quad \hat{V}' = \frac{W + BA}{\|W + BA\|_\text{col}}
\]
 Magnitude $m$ is a separate learnable vector (one scalar per column). This consistently outperforms LoRA by 1--3\% on reasoning and instruction-following benchmarks with no additional inference cost (merged at deployment).
DoRA~\cite{liu2024dora} 观察到全量微调倾向于更多地改变权重向量的\textit{方向}而非幅值。标准 LoRA 将两者混为一谈。DoRA 将每个权重列分解为幅值 $m = \|W\|_\text{col}$ 和方向 $\hat{V} = W / \|W\|_\text{col}$，然后仅对方向应用 LoRA：
\[
W' = m \odot \hat{V}', \quad \hat{V}' = \frac{W + BA}{\|W + BA\|_\text{col}}
\]
 幅值 $m$ 是一个单独的可学习向量（每列一个标量）。在推理和指令遵循的基准测试上，它始终比 LoRA 高出 1--3\%，且不增加推理成本（部署时合并）。


\newpage
\paragraph{LoRA+ -- Asymmetric Learning Rates.}
\label{lora-asymmetric-learning-rates.}
\newpage
\paragraph{LoRA+——非对称学习率}
\label{lora-asymmetric-learning-rates.}


Hayou et al.~\cite{hayou2024loraplus} show that matrices $A$ and $B$ in LoRA have different optimal learning rates. Since $B$ is initialized to zero, it starts in a very different regime than $A$ (initialized from $\mathcal{N}(0, \sigma^2)$). Setting $\eta_B \approx 16 \times \eta_A$ improves convergence speed and final quality by $\sim$2\% --- a free gain requiring only a one-line config change:
Hayou 等人~\cite{hayou2024loraplus} 表明 LoRA 中的矩阵 $A$ 和 $B$ 具有不同的最优学习率。由于 $B$ 初始化为零，它开始的运行状态与 $A$（从 $\mathcal{N}(0, \sigma^2)$ 初始化）非常不同。设置 $\eta_B \approx 16 \times \eta_A$ 可将收敛速度和最终质量提高约 2\%——这是一个只需一行配置更改的免费收益：


\begin{lstlisting}[style=pythonstyle]
