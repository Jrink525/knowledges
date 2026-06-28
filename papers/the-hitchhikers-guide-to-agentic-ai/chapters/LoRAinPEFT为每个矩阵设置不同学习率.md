# LoRA+ in PEFT: 为每个矩阵设置不同学习率
optimizer_grouped_parameters = [
    {"params": [p for n, p in model.named_parameters() if "lora_B" in n],
     "lr": 2e-4 * 16},   # B 矩阵：更高学习率
    {"params": [p for n, p in model.named_parameters() if "lora_A" in n],
     "lr": 2e-4},         # A 矩阵：基础学习率
]
\end{lstlisting}


\paragraph{VeRA -- Vector-based Random Matrix Adaptation.}
\label{vera-vector-based-random-matrix-adaptation.}
\paragraph{VeRA——基于向量的随机矩阵适配}
\label{vera-vector-based-random-matrix-adaptation.}


VeRA~\cite{kopiczko2024vera} takes parameter efficiency to the extreme: instead of learning $A$ and $B$, it \emph{freezes} them as shared random matrices across all layers and only trains two diagonal scaling vectors $d_b \in \mathbb{R}^r$ and $d_a \in \mathbb{R}^d$: 
\[
\Delta W = B \cdot \text{diag}(d_b) \cdot A \cdot \text{diag}(d_a)
\]
 This reduces trainable parameters by $\sim$10$\times$ vs.~LoRA (only $r + d$ params per layer) while achieving 90--95\% of LoRA quality. Best for scenarios where you need hundreds of task-specific adapters with minimal storage.
VeRA~\cite{kopiczko2024vera} 将参数效率推向了极致：它不是学习 $A$ 和 $B$，而是将它们\textit{冻结}为跨所有层共享的随机矩阵，仅训练两个对角缩放向量 $d_b \in \mathbb{R}^r$ 和 $d_a \in \mathbb{R}^d$：
\[
\Delta W = B \cdot \text{diag}(d_b) \cdot A \cdot \text{diag}(d_a)
\]
 这使可训练参数比 LoRA 减少了约 10 倍（每层仅 $r + d$ 个参数），同时达到 LoRA 质量的 90--95\%。最适合需要数百个任务特定适配器且存储最小的场景。


\begin{examplebox}[QLoRA Memory Savings]
\textbf{70B model full fine-tune}: 140 GB (weights) + 280 GB (optimizer) + 140 GB (gradients) = 560 GB (7$\times$ A100-80GB).


\textbf{70B QLoRA (r=16, all linear layers)}:


\begin{itemize}
  \item Base model in NF4: $70\text{B} \times 0.5 = 35$ GB
  \item LoRA adapters in BF16: $\sim$160 MB
  \item Optimizer states (only for adapters): $\sim$320 MB
  \item Activations (gradient checkpointing): $\sim$8 GB
  \item \textbf{Total: $\sim$44 GB} --- fits in a single 48GB GPU!
\end{itemize}
\end{examplebox}

\begin{examplebox}[QLoRA 内存节省]
\textbf{70B 模型全量微调}：140 GB（权重）+ 280 GB（优化器）+ 140 GB（梯度）= 560 GB（7$\times$ A100-80GB）。


\textbf{70B QLoRA (r=16, 所有线性层)}：


\begin{itemize}
  \item NF4 格式的基座模型：$70\text{B} \times 0.5 = 35$ GB
  \item BF16 格式的 LoRA 适配器：约 160 MB
  \item 优化器状态（仅适配器）：约 320 MB
  \item 激活值（梯度检查点）：约 8 GB
  \item \textbf{总计：约 44 GB}——可放入单张 48GB GPU！
\end{itemize}
\end{examplebox}


\begin{lstlisting}[style=pythonstyle]
