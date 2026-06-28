# 需要监控的关键指标：train/rewards/chosen, train/rewards/rejected, train/rewards/margins
\end{lstlisting}

## How DPO Works: Full Mechanics  
## DPO 的工作原理：完整机制  

This section provides the complete computational details of DPO --- what happens at the token level during training.  
本节提供 DPO 的完整计算细节 --- 训练时在 token 级别发生了什么。  

### Sequence-Level Log-Probabilities  
### 序列级别的对数概率  

The key quantity in DPO is the log-probability of an \textbf{entire sequence} $y = (y_1, y_2, \ldots, y_T)$ given prompt $x$. This is computed as the \textbf{sum of per-token log-probabilities}:  
DPO 中的关键量是在给定提示 $x$ 下，\textbf{整个序列} $y = (y_1, y_2, \ldots, y_T)$ 的对数概率。它计算为 \textbf{每个 token 对数概率之和}：  

\begin{equation}
\boxed{\log \pi_\theta(y|x) = \sum_{t=1}^{T} \log \pi_\theta(y_t \mid x, y_{<t})}
\end{equation}

Each term $\log \pi_\theta(y_t | x, y_{<t})$ is the log-softmax output at position $t$ for the \emph{actual} token $y_t$ in the sequence. This is identical to the cross-entropy loss used in standard language modeling --- but here we \textbf{sum} rather than average.  
每一项 $\log \pi_\theta(y_t | x, y_{<t})$ 是序列中位置 $t$ 对 \emph{实际} token $y_t$ 的 log-softmax 输出。这与标准语言建模中使用的交叉熵损失相同 —— 但这里我们 \textbf{求和} 而非平均。  

\textbf{Critical detail}: The gradient flows through \textbf{every token position} in both $y_w$ and $y_l$. There is no masking of intermediate tokens --- every token contributes to the sequence-level log-probability.  
\textbf{关键细节}：梯度流经 $y_w$ 和 $y_l$ 中的 \textbf{每一个 token 位置}。中间 token 没有被遮盖 —— 每个 token 都对序列级别的对数概率有贡献。  

### The DPO Loss Decomposed  
### DPO 损失的分解  

Starting from the loss: 
\begin{equation}
\mathcal{L}_{\text{DPO}}(\theta) = -\mathbb{E}_{(x, y_w, y_l) \sim \mathcal{D}}\!\left[\log \sigma\!\left(\beta \cdot h_\theta(x, y_w, y_l)\right)\right]
\end{equation}
 where the ``implicit reward margin'' $h_\theta$ is: 
\begin{equation}
h_\theta(x, y_w, y_l) = \underbrace{\log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)}}_{\text{chosen reward proxy}} - \underbrace{\log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)}}_{\text{rejected reward proxy}}
\end{equation}
从损失函数开始：
\begin{equation}
\mathcal{L}_{\text{DPO}}(\theta) = -\mathbb{E}_{(x, y_w, y_l) \sim \mathcal{D}}\!\left[\log \sigma\!\left(\beta \cdot h_\theta(x, y_w, y_l)\right)\right]
\end{equation}
其中“隐式奖励间隔” $h_\theta$ 为：
\begin{equation}
h_\theta(x, y_w, y_l) = \underbrace{\log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)}}_{\text{被选中奖励代理}} - \underbrace{\log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)}}_{\text{被拒绝奖励代理}}
\end{equation}

Expanding into token-level terms: 
\begin{equation}
\boxed{h_\theta = \sum_{t=1}^{|y_w|}\!\left[\log\pi_\theta(y_w^t | x, y_w^{<t}) - \log\pi_{\text{ref}}(y_w^t | x, y_w^{<t})\right] - \sum_{t=1}^{|y_l|}\!\left[\log\pi_\theta(y_l^t | x, y_l^{<t}) - \log\pi_{\text{ref}}(y_l^t | x, y_l^{<t})\right]}
\end{equation}
展开成 token 级别的项：
\begin{equation}
\boxed{h_\theta = \sum_{t=1}^{|y_w|}\!\left[\log\pi_\theta(y_w^t | x, y_w^{<t}) - \log\pi_{\text{ref}}(y_w^t | x, y_w^{<t})\right] - \sum_{t=1}^{|y_l|}\!\left[\log\pi_\theta(y_l^t | x, y_l^{<t}) - \log\pi_{\text{ref}}(y_l^t | x, y_l^{<t})\right]}
\end{equation}

### Forward Pass: Step by Step  
### 前向传播：逐步说明  

For one training example $(x, y_w, y_l)$:  
对于单个训练样本 $(x, y_w, y_l)$：

\begin{enumerate}
  \item \textbf{Concatenate}: Form two sequences: $[x; y_w]$ and $[x; y_l]$. Pad to equal length within the batch.
  \item \textbf{连接（Concatenate）}：构造两个序列：$[x; y_w]$ 和 $[x; y_l]$。在批次内填充到等长。

  \item \textbf{Forward pass (policy $\pi_\theta$)}: Run both sequences through the model. Collect logits at every response position.
  \item \textbf{前向传播（策略 $\pi_\theta$）}：将两个序列分别送入模型。收集每个响应位置（response position）的 logits。

  \item \textbf{Extract log-probs}: At each position $t$ in the response, take $\log\text{softmax}(\text{logits}_t)[y_t]$ --- the log-probability of the actual token.
  \item \textbf{提取对数概率（log-probs）}：在响应的每个位置 $t$，取 $\log\text{softmax}(\text{logits}_t)[y_t]$ —— 实际 token 的对数概率。

  \item \textbf{Sum over tokens}: 
\begin{align}
\text{logp\_chosen} &= \sum_{t \in \text{response positions}} \log\pi_\theta(y_w^t | x, y_w^{<t}) \\
\text{logp\_rejected} &= \sum_{t \in \text{response positions}} \log\pi_\theta(y_l^t | x, y_l^{<t})
\end{align}
  \item \textbf{对 token 求和}：
\begin{align}
\text{logp\_chosen} &= \sum_{t \in \text{响应位置}} \log\pi_\theta(y_w^t | x, y_w^{<t}) \\
\text{logp\_rejected} &= \sum_{t \in \text{响应位置}} \log\pi_\theta(y_l^t | x, y_l^{<t})
\end{align}

  \item \textbf{Subtract reference} (pre-computed or from second forward pass): 
\begin{align}
\text{ratio\_w} &= \text{logp\_chosen} - \text{ref\_logp\_chosen} \\
\text{ratio\_l} &= \text{logp\_rejected} - \text{ref\_logp\_rejected}
\end{align}
  \item \textbf{减去参考（reference）}（预计算或通过第二次前向传播获得）：
\begin{align}
\text{ratio\_w} &= \text{logp\_chosen} - \text{ref\_logp\_chosen} \\
\text{ratio\_l} &= \text{logp\_rejected} - \text{ref\_logp\_rejected}
\end{align}

  \item \textbf{Compute loss}: $\mathcal{L} = -\log\sigma(\beta \cdot (\text{ratio\_w} - \text{ratio\_l}))$
  \item \textbf{计算损失（loss）}：$\mathcal{L} = -\log\sigma(\beta \cdot (\text{ratio\_w} - \text{ratio\_l}))$

  \item \textbf{Backward pass}: Gradients flow back through steps 5 $\rightarrow$ 4 $\rightarrow$ 3 $\rightarrow$ 2 to update $\theta$.
  \item \textbf{反向传播（Backward pass）}：梯度经由步骤 5 $\rightarrow$ 4 $\rightarrow$ 3 $\rightarrow$ 2 回流，以更新 $\theta$。
\end{enumerate}

\subsection{Token-Level Gradient Analysis}
\label{token-level-gradient-analysis}
\subsection{Token 级梯度分析}

\textbf{Does every token get a gradient?} Yes. The gradient with respect to the logits at position $t$ in the chosen sequence is:
\textbf{每个 token 都会获得梯度吗？} 是的。对选中序列中位置 $t$ 的 logits 的梯度为：

\begin{equation}
\frac{\partial \mathcal{L}}{\partial \text{logits}_t^{(w)}} = -\underbrace{\sigma(-\beta \cdot h_\theta)}_{\text{scaling factor}} \cdot \beta \cdot \frac{\partial \log\pi_\theta(y_w^t | \cdot)}{\partial \text{logits}_t^{(w)}}
\end{equation}

\textbf{Key insight}: The scaling factor $\sigma(-\beta \cdot h_\theta)$ is \textbf{shared across all tokens} in both sequences. It acts as an adaptive learning rate:
\textbf{关键洞察（Key insight）}：缩放因子 $\sigma(-\beta \cdot h_\theta)$ 在两个序列的 \textbf{所有 token 间共享}。它起到自适应学习率的作用：

\begin{itemize}
  \item When $h_\theta$ is small (model can’t distinguish chosen from rejected): scaling $\approx 0.5$ --- strong gradient, learn aggressively.
  \item 当 $h_\theta$ 较小时（模型无法区分选中和拒绝）：缩放因子 $\approx 0.5$ —— 强梯度，积极学习。
  \item When $h_\theta$ is large (model already prefers chosen): scaling $\approx 0$ --- negligible gradient, don’t over-fit.
  \item 当 $h_\theta$ 较大时（模型已偏向选中）：缩放因子 $\approx 0$ —— 梯度可忽略，避免过拟合。
\end{itemize}

\textbf{Effect on chosen tokens}: Probability is \emph{increased} (log-prob pushed up).\\
\textbf{对选中 token 的影响}：概率 \emph{增加}（对数概率被推高）。

\textbf{Effect on rejected tokens}: Probability is \emph{decreased} (log-prob pushed down).\\
\textbf{对拒绝 token 的影响}：概率 \emph{降低}（对数概率被压低）。

\textbf{Relative to reference}: Only the \emph{difference} from $\pi_{\text{ref}}$ matters. If the model already assigns high probability to the chosen response (matching the reference), there’s little gradient.
\textbf{相对于参考（reference）}：只有与 $\pi_{\text{ref}}$ 的 \emph{差值} 起作用。如果模型已为选中响应分配高概率（与参考一致），则梯度很小。

\subsection{Per-Token vs. Sequence-Level: Length Normalization}
\label{per-token-vs.-sequence-level-length-normalization}
\subsection{逐 Token 与序列级：长度归一化（Length Normalization）}

A subtle issue: longer sequences naturally have lower log-probabilities (more terms summed, each $\leq 0$). If $|y_w| \gg |y_l|$, the loss can be biased toward preferring shorter responses.
一个微妙的问题：较长的序列自然具有较低的对数概率（求和项更多，每项 $\leq 0$）。如果 $|y_w| \gg |y_l|$，损失可能会偏向更短的响应。

\textbf{Solutions}:
\textbf{解决方案}：

\begin{itemize}
  \item \textbf{Length-normalized DPO}: Replace $\log\pi_\theta(y|x)$ with $\frac{1}{|y|}\sum_t \log\pi_\theta(y_t|\cdot)$. Used in some implementations (SimPO adopts this).
  \item \textbf{长度归一化 DPO（Length-normalized DPO）}：将 $\log\pi_\theta(y|x)$ 替换为 $\frac{1}{|y|}\sum_t \log\pi_\theta(y_t|\cdot)$。某些实现中采用该方法（SimPO 即如此）。
  \item \textbf{Standard DPO}: Uses raw sum (no normalization). This \emph{implicitly} penalizes verbosity --- the model must assign high probability to every token in the chosen response.
  \item \textbf{标准 DPO（Standard DPO）}：使用原始求和（无归一化）。这 \emph{隐式地} 惩罚冗长 —— 模型必须为选中响应中的每个 token 分配高概率。
  \item \textbf{Practical impact}: On benchmarks, length-normalized DPO reduces length gaming but can hurt instruction-following quality. Standard (unnormalized) is more common in production.
  \item \textbf{实际影响}：在基准测试中，长度归一化 DPO 减少了长度作弊（length gaming），但可能损害指令遵循质量。标准（无归一化）DPO 在生产中更为常见。
\end{itemize}

\subsection{Label Masking: What Gets Gradients}
\label{label-masking-what-gets-gradients}
\subsection{标签掩码（Label Masking）：哪些获得梯度}

\begin{keybox}[Which Tokens Receive Gradient in DPO]
\begin{keybox}[DPO 中哪些 Token 接收梯度]
\begin{itemize}
  \item \textbf{Prompt tokens} ($x$): \textbf{NO gradient}. The loss is computed only over response positions. Prompt tokens provide context but their logits don’t contribute to $\log\pi(y|x)$.
  \item \textbf{提示 token（Prompt tokens）} ($x$)：\textbf{无梯度}。损失仅在响应位置上计算。提示 token 提供上下文，但其 logits 不贡献于 $\log\pi(y|x)$。
  \item \textbf{Chosen response tokens} ($y_w$): \textbf{ALL tokens get gradient}. Each $y_w^t$ contributes to the sum. Gradient pushes their probabilities up.
  \item \textbf{选中响应 token（Chosen response tokens）} ($y_w$)：\textbf{所有 token 均获得梯度}。每个 $y_w^t$ 都贡献到求和中。梯度将其概率推高。
  \item \textbf{Rejected response tokens} ($y_l$): \textbf{ALL tokens get gradient}. Each $y_l^t$ contributes to the sum. Gradient pushes their probabilities down.
  \item \textbf{拒绝响应 token（Rejected response tokens）} ($y_l$)：\textbf{所有 token 均获得梯度}。每个 $y_l^t$ 都贡献到求和中。梯度将其概率推低。
  \item \textbf{Padding tokens}: \textbf{NO gradient}. Masked out with attention mask.
  \item \textbf{填充 token（Padding tokens）}：\textbf{无梯度}。通过注意力掩码（attention mask）屏蔽。
\end{itemize}
\end{keybox}
\end{keybox}

\subsection{Pseudocode: DPO Training Step}
\label{pseudocode-dpo-training-step}
\subsection{伪代码（Pseudocode）：DPO 训练步骤}

\begin{examplebox}[DPO Forward + Backward (PyTorch-style)]
\begin{examplebox}[DPO 前向 + 反向（PyTorch 风格）]
\begin{lstlisting}[style=pythonstyle]
def dpo_loss(model, ref_model, batch, beta=0.1):
    """One DPO training step."""
