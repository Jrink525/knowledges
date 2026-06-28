    # 掩码：仅对响应 token 求和（labels != -100）
    mask = (labels != -100).float()
    return (token_logps * mask).sum(dim=-1)  # 形状：[batch_size]
\end{lstlisting}
\end{examplebox}
\end{examplebox}

\subsection{Common Pitfalls}
\label{common-pitfalls}
\subsection{常见陷阱（Common Pitfalls）}

\begin{warningbox}[DPO Implementation Pitfalls]
\begin{warningbox}[DPO 实现陷阱]
\begin{itemize}
  \item \textbf{Forgetting to mask the prompt}: If prompt tokens are included in the log-prob sum, the model optimizes for prompt likelihood (useless) and the effective $\beta$ is wrong.
  \item \textbf{忘记掩码提示（mask the prompt）}：如果提示 token 被包含在对数概率求和中，模型会优化提示似然（无用），并且有效 $\beta$ 会出错。
  \item \textbf{Using mean instead of sum}: $\frac{1}{T}\sum_t \log\pi$ vs. $\sum_t \log\pi$ --- these give different implicit length penalties. Must be consistent between $\pi_\theta$ and $\pi_{\text{ref}}$.
  \item \textbf{使用均值代替求和}：$\frac{1}{T}\sum_t \log\pi$ 与 $\sum_t \log\pi$ —— 它们会给出不同的隐式长度惩罚。在 $\pi_\theta$ 和 $\pi_{\text{ref}}$ 之间必须保持一致。
  \item \textbf{Stale reference model}: If $\pi_{\text{ref}}$ is too far from $\pi_\theta$ (e.g., base model vs. fine-tuned), the KL term dominates and gradients vanish. Solution: use the SFT checkpoint (not base) as reference.
  \item \textbf{参考模型过时（Stale reference model）}：如果 $\pi_{\text{ref}}$ 与 $\pi_\theta$ 相差过大（例如，基础模型 vs 微调模型），KL 项会主导且梯度消失。解决方案：使用 SFT 检查点（而非基础模型）作为参考。
  \item \textbf{$\beta$ too large}: Magnifies log-prob differences $\rightarrow$ sigmoid saturates $\rightarrow$ zero gradients. Start with $\beta = 0.1$, tune in $[0.05, 0.5]$.
  \item \textbf{$\beta$ 过大}：放大对数概率差异 $\rightarrow$ sigmoid 饱和 $\rightarrow$ 梯度为零。从 $\beta = 0.1$ 开始，在 $[0.05, 0.5]$ 内调整。
  \item \textbf{$\beta$ too small}: Theoretically allows more freedom from reference (weaker KL constraint), but the gradient $\propto \beta \cdot \sigma(-\beta h)$ becomes vanishingly small $\rightarrow$ loss landscape is flat $\rightarrow$ extremely slow convergence. The model has ``permission'' to move far but receives almost no signal telling it \emph{where} to move.
  \item \textbf{$\beta$ 过小}：理论上允许模型更自由地偏离参考（更弱的 KL 约束），但梯度 $\propto \beta \cdot \sigma(-\beta h)$ 变得极小 $\rightarrow$ 损失景观平坦 $\rightarrow$ 收敛极慢。模型拥有“许可”大幅移动，但几乎收不到任何信号告诉它应该 \emph{朝哪里} 移动。
\end{itemize}
\end{warningbox}
\end{warningbox}

\section{DPO Variants and When Each Fails}
\label{dpo-variants-and-when-each-fails}
\section{DPO 变体及各自的失效场景}

\begin{warningbox}[When DPO Fails]
\begin{warningbox}[DPO 何时失效]
\textbf{1. Distribution shift}: Preference data from old model. Current policy generates different text $\rightarrow$ loss is optimizing on irrelevant examples.
\textbf{1. 分布偏移（Distribution shift）}：偏好数据来自旧模型。当前策略生成不同的文本 $\rightarrow$ 损失正在对不相关的样本进行优化。

\textbf{2. No exploration}: Can’t discover behaviors not in dataset. Stuck in local optimum.
\textbf{2. 缺乏探索（No exploration）}：无法发现数据集中不存在的行为。陷入局部最优。

\textbf{3. Reference collapse}: If reference is too strong, policy can’t move. If too weak, no regularization.
\textbf{3. 参考崩溃（Reference collapse）}：如果参考太强，策略无法移动。如果太弱，则无正则化。
\end{warningbox}
\end{warningbox}

\begin{warningbox}
\textbf{4. Data quality}: Noisy labels poison training. Unlike PPO which averages over many samples, DPO memorizes individual pairs.

\textbf{4. 数据质量}：噪声标签会毒化训练过程。与PPO对大量样本取平均不同，DPO会记忆单个偏好对。

\textbf{5. Preference data diversity}: Ensure chosen/rejected pairs cover the full spectrum of quality differences (not just good-vs-terrible). Pairs that differ in \emph{approach}, not just quality, teach richer policy distinctions.

\textbf{5. 偏好数据多样性}：确保 chosen/rejected 对覆盖质量差异的完整频谱（而不仅仅是好与坏）。在\textit{方法}（而非仅质量）上不同的偏好对，能教会策略更丰富的区分能力。
\end{warningbox}


\section{$\beta$ Selection Guide}
\section{$\beta$ 选择指南}
\label{beta-selection-guide}


\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
$\beta$ & \textbf{Regime} & \textbf{When to Use} \\
$\beta$ & \textbf{模式} & \textbf{使用场景} \\
\midrule
0.01 & Very aggressive & Only if data is extremely clean and you need large distributional shift \\
0.01 & 非常激进 & 仅当数据极其干净且需要较大的分布偏移时使用 \\
0.05 & Aggressive & Good data, want noticeable improvement over SFT \\
0.05 & 激进 & 数据质量好，希望在SFT基础上实现显著改进 \\
0.1 & Standard & Default starting point. Good balance of quality vs stability \\
0.1 & 标准 & 默认起始点。质量与稳定性之间取得良好平衡 \\
0.2 & Conservative & Noisy data, or model already close to desired behavior \\
0.2 & 保守 & 数据有噪声，或模型已接近期望行为 \\
0.5 & Very conservative & Safety fine-tuning where you must not break capabilities \\
0.5 & 非常保守 & 安全微调场景，必须避免破坏已有能力 \\
\bottomrule
\end{tabular}


\section{DPO Batch Size Configuration and Scaling}
\section{DPO 批量大小配置与扩展}
\label{dpo-batch-size-configuration-and-scaling}


Unlike standard SFT which operates on single-sequence token predictions, DPO leverages a \textbf{pairwise loss} comparing a preferred sequence against a dispreferred sequence. This fundamentally alters memory utilization and optimization stability.

与基于单序列token预测的标准SFT不同，DPO采用\textbf{成对损失}，将偏好序列与非偏好序列进行比较。这从根本上改变了内存利用方式和优化稳定性。

\subsection{Global Batch Size Target}
\subsection{全局批量大小目标}
\label{global-batch-size-target}


Empirical evidence across DPO implementations establishes an optimal global batch size range: 
\begin{equation}
\boxed{B_{\text{global}} \in [32, 128]}
\end{equation}

来自各种DPO实现的实证结果确定了最优全局批量大小范围：
\begin{equation}
\boxed{B_{\text{global}} \in [32, 128]}
\end{equation}

\begin{itemize}
  \item $B_{\text{global}} < 32$: Severe gradient noise in implicit reward estimation $\rightarrow$ policy oscillates destructively between alignment goals (helpfulness vs. safety).
  \item $B_{\text{global}} < 32$：隐式奖励估计中存在严重梯度噪声 $\rightarrow$ 策略在有用性与安全性等对齐目标之间破坏性振荡。
  \item $B_{\text{global}} > 128$: Diminishing returns on convergence velocity; high communication overhead across distributed compute.
  \item $B_{\text{global}} > 128$：收敛速度提升的边际收益递减；分布式计算中的通信开销较高。
\end{itemize}


\subsection{Mathematical Decomposition}
\subsection{数学分解}
\label{mathematical-decomposition}


Because DPO loads \textbf{two} model copies simultaneously (active policy $\pi_\theta$ + frozen reference $\pi_{\text{ref}}$), per-sequence memory is doubled. The global batch size is decomposed as: 
\begin{equation}
\boxed{B_{\text{global}} = B_{\text{micro}} \times N_{\text{GPUs}} \times K_{\text{accum}}}
\end{equation}

由于DPO同时加载\textbf{两个}模型副本（活跃策略 $\pi_\theta$ + 冻结参考 $\pi_{\text{ref}}$），每个序列的内存占用翻倍。全局批量大小分解如下：
\begin{equation}
\boxed{B_{\text{global}} = B_{\text{micro}} \times N_{\text{GPUs}} \times K_{\text{accum}}}
\end{equation}

\begin{itemize}
  \item $B_{\text{micro}}$: Per-device micro-batch size (preference pairs per forward pass).
  \item $B_{\text{micro}}$：每设备微批量大小（每次前向传播的偏好对数量）。
  \item $N_{\text{GPUs}}$: Number of parallel data-processing devices.
  \item $N_{\text{GPUs}}$：并行数据处理设备数量。
  \item $K_{\text{accum}}$: Gradient accumulation steps before weight update.
  \item $K_{\text{accum}}$：权重更新前的梯度累积步数。
\end{itemize}


\textbf{The pairing multiplier}: A single DPO data instance contains a prompt ($x$), chosen ($y_w$), and rejected ($y_l$). The actual tensor load per micro-batch: 
\begin{equation}
T_{\text{sequences}} = 2 \times B_{\text{micro}}
\end{equation}

\textbf{配对乘数}：单个DPO数据实例包含一个提示（$x$）、被选答案（$y_w$）和被拒答案（$y_l$）。每个微批量的实际张量负载为：
\begin{equation}
T_{\text{sequences}} = 2 \times B_{\text{micro}}
\end{equation}

For models $>$7B parameters on 80GB GPUs with context lengths 4096--8192 tokens, the physical limit is rigidly constrained to $B_{\text{micro}} \in [1, 2]$.

对于参数量＞7B的模型，在80GB GPU上，上下文长度为4096--8192 token时，物理限制严格限定为 $B_{\text{micro}} \in [1, 2]$。

\subsection{Distributed Scaling Configurations}
\subsection{分布式扩展配置}
\label{distributed-scaling-configurations}


\begin{table}[ht!]
\centering
\caption{Distributed scaling profiles for DPO training ($B_{\text{global}} = 64$ target).}
\caption{DPO训练的分布式扩展配置（目标 $B_{\text{global}} = 64$）}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Configuration} & \textbf{Single GPU} & \textbf{8-GPU Node} \\
\textbf{配置} & \textbf{单GPU} & \textbf{8-GPU节点} \\
\midrule
$B_{\text{global}}$ & 64 & 64 \\
$B_{\text{micro}}$ & 2 (4 sequences) & 2 (4 sequences) \\
$B_{\text{micro}}$ & 2 (4个序列) & 2 (4个序列) \\
$N_{\text{GPUs}}$ & 1 & 8 \\
$K_{\text{accum}}$ & 32 steps & 4 steps \\
$K_{\text{accum}}$ & 32步 & 4步 \\
Throughput & Sequential/slow & High parallel throughput \\
吞吐量 & 串行/慢 & 高并行吞吐量 \\
\bottomrule
\end{tabular}
\end{table}


\subsection{VRAM Optimization: Pre-computing Reference Log-Probabilities}
\subsection{VRAM优化：预计算参考对数概率}
\label{vram-optimization-pre-computing-reference-log-probabilities}


The DPO loss: 
\begin{equation}
\mathcal{L}_{\text{DPO}}(\theta) = -\mathbb{E}_{(x, y_w, y_l)}\!\left[\log \sigma\!\left(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)}\right)\right]
\end{equation}

DPO损失函数：
\begin{equation}
\mathcal{L}_{\text{DPO}}(\theta) = -\mathbb{E}_{(x, y_w, y_l)}\!\left[\log \sigma\!\left(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)}\right)\right]
\end{equation}

Because $\pi_{\text{ref}}$ is \textbf{completely static} throughout training, its outputs can be pre-computed:

由于 $\pi_{\text{ref}}$ 在整个训练过程中\textbf{完全静态}，其输出可以预计算：


\begin{keybox}[Reference Model Eviction Strategy]
\begin{keybox}[参考模型驱逐策略]
\begin{enumerate}
  \item Execute a forward pass over dataset $\mathcal{D}$ using only $\pi_{\text{ref}}$ before training begins.
  \item 在训练开始前，仅使用 $\pi_{\text{ref}}$ 对数据集 $\mathcal{D}$ 执行一次前向传播。
  \item Cache the scalars $\log \pi_{\text{ref}}(y_w|x)$ and $\log \pi_{\text{ref}}(y_l|x)$ to disk.
  \item 将标量 $\log \pi_{\text{ref}}(y_w|x)$ 和 $\log \pi_{\text{ref}}(y_l|x)$ 缓存到磁盘。
  \item \textbf{Evict $\pi_{\text{ref}}$ completely from GPU memory.}
  \item \textbf{将 $\pi_{\text{ref}}$ 完全从GPU内存中驱逐。}
\end{enumerate}


\textbf{Result}: Available GPU memory doubles $\rightarrow$ can increase $B_{\text{micro}}$ from 1--2 to 4--8, maximizing hardware utilization and training throughput.

\textbf{结果}：可用GPU内存翻倍 $\rightarrow$ 可将 $B_{\text{micro}}$ 从1--2提升至4--8，最大化硬件利用率和训练吞吐量。


\emph{Implementation}: In TRL, set \texttt{precompute\_ref\_log\_probs=True} in \texttt{DPOConfig}. For 70B models, this saves $\sim$140GB of GPU memory across the cluster.

\emph{实现}：在TRL中，在 \texttt{DPOConfig} 中设置 \texttt{precompute\_ref\_log\_probs=True}。对于70B模型，这可以在整个集群中节省约140GB的GPU内存。
\end{keybox}


\section{DPO Extensions and Variants}
\section{DPO扩展与变体}
\label{sec:dpo-variants}


Direct Preference Optimization (DPO) reformulates RLHF as a supervised learning problem by deriving a closed-form mapping between the reward function and the optimal policy. The standard DPO loss is:

直接偏好优化（DPO）通过推导奖励函数与最优策略之间的闭式映射，将RLHF重新表述为监督学习问题。标准DPO损失为：

\[
\mathcal{L}_{\text{DPO}}(\theta) = -\mathbb{E}_{(q,y_w,y_l)}\!\left[
    \log \sigma\!\left(
      \beta \log \frac{\pi_\theta(y_w|q)}{\pi_{\text{ref}}(y_w|q)}
      - \beta \log \frac{\pi_\theta(y_l|q)}{\pi_{\text{ref}}(y_l|q)}
    \right)
  \right],
\]

\[
\mathcal{L}_{\text{DPO}}(\theta) = -\mathbb{E}_{(q,y_w,y_l)}\!\left[
    \log \sigma\!\left(
      \beta \log \frac{\pi_\theta(y_w|q)}{\pi_{\text{ref}}(y_w|q)}
      - \beta \log \frac{\pi_\theta(y_l|q)}{\pi_{\text{ref}}(y_l|q)}
    \right)
  \right],
\]

where $y_w$ is the preferred (winning) response, $y_l$ is the dispreferred (losing) response, and $\beta$ controls the strength of the KL penalty. The following subsections cover the most important extensions and variants.

其中 $y_w$ 是偏好（获胜）响应，$y_l$ 是非偏好（失败）响应，$\beta$ 控制KL惩罚的强度。以下小节介绍最重要的扩展和变体。

\subsection{f-DPO -- Generalised f-Divergence DPO}
\subsection{f-DPO -- 广义f-散度DPO}
\label{sec:fdpo}


\begin{intuitionbox}[Beyond Reverse KL]
Standard DPO uses reverse KL divergence as the regulariser between policy and reference. Reverse KL is \emph{mode-seeking}: it prefers to concentrate probability mass on a few high-reward responses. Forward KL is \emph{mode-covering}: it spreads probability mass to cover all plausible responses. f-DPO~\cite{wang2023fdpo} generalises to any f-divergence, allowing practitioners to trade off these behaviours.
\end{intuitionbox}

\begin{intuitionbox}[超越反向KL]
标准DPO使用反向KL散度作为策略与参考之间的正则化项。反向KL是\textit{寻找模态}的：它倾向于将概率质量集中在少数高奖励响应上。正向KL是\textit{覆盖模态}的：它将概率质量分散以覆盖所有合理响应。f-DPO~\cite{wang2023fdpo} 将其推广到任意f-散度，允许实践者在这两种行为之间进行权衡。
\end{intuitionbox}

The f-DPO loss replaces the log-ratio with the derivative of the f-divergence generator:

f-DPO损失将对数比率替换为f-散度生成函数的导数：

\[
\mathcal{L}_{f\text{-DPO}} = -\mathbb{E}\!\left[
    f'\!\left(\frac{\pi_\theta(y_w|q)}{\pi_{\text{ref}}(y_w|q)}\right)
    - f'\!\left(\frac{\pi_\theta(y_l|q)}{\pi_{\text{ref}}(y_l|q)}\right)
  \right],
\]

\[
\mathcal{L}_{f\text{-DPO}} = -\mathbb{E}\!\left[
    f'\!\left(\frac{\pi_\theta(y_w|q)}{\pi_{\text{ref}}(y_w|q)}\right)
    - f'\!\left(\frac{\pi_\theta(y_l|q)}{\pi_{\text{ref}}(y_l|q)}\right)
  \right],
\]

where $f'$ is the derivative of the f-divergence generator function.

其中 $f'$ 是f-散度生成函数的导数。

\begin{keybox}[f-Divergence Options in TRL]
\begin{keybox}[TRL中的f-散度选项]
\begin{itemize}
  \item \textbf{reverse\_kl}: $f'(u) = \log u$. Standard DPO. Mode-seeking.
  \item \textbf{reverse\_kl}: $f'(u) = \log u$。标准DPO。寻找模态。
  \item \textbf{forward\_kl}: $f'(u) = -1/u$. Mode-covering. Better diversity.
  \item \textbf{forward\_kl}: $f'(u) = -1/u$。覆盖模态。多样性更好。
  \item \textbf{js\_divergence}: $f'(u) = \log(2u/(u+1))$. Balanced mode-seeking/covering.
  \item \textbf{js\_divergence}: $f'(u) = \log(2u/(u+1))$。寻找模态与覆盖模态的平衡。
  \item \textbf{alpha\_divergence}: $f'(u) = u^{\alpha-1}$. Interpolates between forward and reverse KL.
  \item \textbf{alpha\_divergence}: $f'(u) = u^{\alpha-1}$。在正向KL和反向KL之间插值。
\end{itemize}
\end{keybox}


\begin{examplebox}[f-DPO in TRL]
\begin{examplebox}[TRL中的f-DPO]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


