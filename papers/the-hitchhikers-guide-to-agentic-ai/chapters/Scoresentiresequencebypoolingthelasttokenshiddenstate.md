# Scores entire sequence by pooling the last token's hidden state
inputs = tokenizer("Good response here", return_tensors="pt")
reward_score = reward_model(**inputs).logits  # shape: (batch, 1)
\end{lstlisting}

\begin{intuitionbox}[Weight Tying: LM Head = Embedding Matrix Transposed]
Most modern LLMs \emph{tie} the LM head weights with the input embedding matrix: \texttt{lm\_head.weight = model.embed\_tokens.weight}. This means the LM head is \emph{not} a separately learned layer---it reuses the embedding table. Benefits: fewer parameters ($|\mathcal{V}| \times d$ saved), better generalization, and the geometric structure of the embedding space directly determines token probabilities. You can verify this in HuggingFace: \texttt{model.lm\_head.weight is model.model.embed\_tokens.weight} returns \texttt{True} for most models.
\end{intuitionbox}

\begin{intuitionbox}[权重绑定：LM头 = 嵌入矩阵转置]
大多数现代LLM将LM头的权重与输入嵌入矩阵\emph{绑定}：\texttt{lm\_head.weight = model.embed\_tokens.weight}。这意味着LM头\emph{不是}一个单独学习的层——它复用了嵌入表。好处：参数更少（节省了$|\mathcal{V}| \times d$）、泛化更好，并且嵌入空间的几何结构直接决定了token概率。你可以在HuggingFace中验证：对于大多数模型，\texttt{model.lm\_head.weight is model.model.embed\_tokens.weight}返回\texttt{True}。
\end{intuitionbox}

\newpage
\section{Optimization Theory for LLM Training}
\section{LLM训练的优化理论}
\label{optimization-theory-for-llm-training}

Training a large language model means finding the set of parameters $\theta$ (billions of weights) that minimizes the loss function $\mathcal{L}(\theta)$ --- typically the negative log-likelihood of the next token. This is an optimization problem in extraordinarily high-dimensional space, and the algorithm used to navigate this space determines whether training succeeds, diverges, or stalls.

训练大型语言模型意味着找到一组参数$\theta$（数十亿个权重），使损失函数$\mathcal{L}(\theta)$最小化——通常是下一个token的负对数似然。这是一个在极高维空间中的优化问题，而用于导航该空间的算法决定了训练是成功、发散还是停滞。

\subsection{Gradient Descent: The Foundation}
\subsection{梯度下降：基础}
\label{gradient-descent-the-foundation}

\paragraph{What is a Gradient?}
\paragraph{什么是梯度？}
\label{what-is-a-gradient}

The gradient $\nabla_\theta \mathcal{L}$ is a vector that points in the direction of \emph{steepest increase} of the loss. Each component $\frac{\partial \mathcal{L}}{\partial \theta_i}$ tells us how much the loss would change if we slightly increased parameter $\theta_i$. To \emph{decrease} the loss, we move in the opposite direction:

梯度$\nabla_\theta \mathcal{L}$是一个指向损失\emph{最陡增加}方向的向量。每个分量$\frac{\partial \mathcal{L}}{\partial \theta_i}$告诉我们如果稍微增加参数$\theta_i$，损失会变化多少。为了\emph{减小}损失，我们向相反方向移动：

\begin{equation}
\theta_{t+1} = \theta_t - \eta \nabla_\theta \mathcal{L}(\theta_t)
\end{equation}

where $\eta > 0$ is the \textbf{learning rate} --- the step size. This is \textbf{gradient descent}~\cite{rumelhart1986learning}.

其中$\eta > 0$是\textbf{学习率}——步长。这就是\textbf{梯度下降}~\cite{rumelhart1986learning}。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.7\textwidth]{figures/fig_009_fig9.png}
\caption{Gradient descent: starting from a random initialization $\theta_0$, each step moves the parameters in the direction that reduces the loss, with step size controlled by the learning rate $\eta$. The process converges toward a (local) minimum.}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.7\textwidth]{figures/fig_009_fig9.png}
\caption{梯度下降：从随机初始化$\theta_0$开始，每一步将参数向减少损失的方向移动，步长由学习率$\eta$控制。该过程收敛到（局部）最小值。}
\end{figure}

\paragraph{Why Full Gradient Descent is Impractical.}
\paragraph{为什么全批量梯度下降不可行。}
\label{why-full-gradient-descent-is-impractical.}

Computing the exact gradient requires evaluating the loss over the \emph{entire} training dataset (trillions of tokens for LLMs). This is computationally prohibitive --- a single gradient step would require a full pass over all data.

计算精确梯度需要对\emph{整个}训练数据集（对于LLM来说是数万亿个token）评估损失。这在计算上是不可行的——单个梯度步骤需要对所有数据进行一次完整遍历。

\paragraph{Stochastic Gradient Descent (SGD).}
\paragraph{随机梯度下降（SGD）。}
\label{stochastic-gradient-descent-sgd.}

The solution: estimate the gradient from a small random subset (\textbf{mini-batch}) of the data~\cite{robbins1951stochastic}: 
\[
\nabla_\theta \mathcal{L}(\theta) \approx \frac{1}{B}\sum_{i=1}^{B} \nabla_\theta \ell(\theta; x_i)
\]
 where $B$ is the batch size (typically 1K--4M tokens for LLMs). The mini-batch gradient is a \emph{noisy but unbiased} estimate of the true gradient.

解决方案：从数据的一个小的随机子集（\textbf{小批量}）估计梯度~\cite{robbins1951stochastic}：
\[
\nabla_\theta \mathcal{L}(\theta) \approx \frac{1}{B}\sum_{i=1}^{B} \nabla_\theta \ell(\theta; x_i)
\]
其中$B$是批量大小（对于LLM通常是1K--4M个token）。小批量梯度是真实梯度的\emph{有噪声但无偏}的估计。

\begin{keybox}[Why Mini-Batch SGD Works]
\begin{itemize}
  \item \textbf{Computational efficiency}: Each step costs $O(B)$ instead of $O(N_{\text{total}})$. With $B = 4096$ tokens and 15T total tokens, each step is $\sim$4 billion$\times$ cheaper.
  \item \textbf{Noise as regularization}: The stochastic noise helps escape sharp local minima, finding flatter regions that generalize better.
  \item \textbf{GPU utilization}: Mini-batches are large enough to saturate GPU parallelism (matrix multiplications become compute-bound rather than memory-bound).
  \item \textbf{Convergence}: Theoretically converges to a local minimum at rate $O(1/\sqrt{T})$ (slower than exact GD’s $O(1/T)$, but each step is millions of times cheaper).
\end{itemize}
\end{keybox}

\begin{keybox}[为什么小批量SGD有效]
\begin{itemize}
  \item \textbf{计算效率}：每一步的代价是$O(B)$而不是$O(N_{\text{total}})$。当$B = 4096$个token且总token数为15T时，每一步便宜约40亿倍。
  \item \textbf{噪声作为正则化}：随机噪声有助于逃离尖锐的局部最小值，找到泛化更好的平坦区域。
  \item \textbf{GPU利用率}：小批量足够大，可以饱和GPU并行度（矩阵乘法变成计算密集型而非内存密集型）。
  \item \textbf{收敛性}：理论上以$O(1/\sqrt{T})$的速率收敛到局部最小值（比精确GD的$O(1/T)$慢，但每一步便宜数百万倍）。
\end{itemize}
\end{keybox}

\paragraph{From SGD to Adaptive Methods.}
\paragraph{从SGD到自适应方法。}
\label{from-sgd-to-adaptive-methods.}

While SGD with momentum works well for vision models (CNNs), LLM training requires \textbf{adaptive optimizers} --- algorithms that maintain a per-parameter learning rate.

虽然带动量的SGD在视觉模型（CNN）上效果很好，但LLM训练需要\textbf{自适应优化器}——为每个参数维护一个学习率的算法。

\subsection{Why Vanilla SGD Fails for LLMs}
\subsection{为什么普通SGD对LLM失败}
\label{why-vanilla-sgd-fails-for-llms}

Stochastic Gradient Descent updates weights as: 
\[
\theta_{t+1} = \theta_t - \eta \nabla_\theta \mathcal{L}(\theta_t)
\]

随机梯度下降按如下方式更新权重：
\[
\theta_{t+1} = \theta_t - \eta \nabla_\theta \mathcal{L}(\theta_t)
\]

\begin{warningbox}[SGD Problems for LLMs]
\begin{itemize}
  \item \textbf{Different gradient scales per layer:} Early layers in a transformer have much smaller gradients than later layers (vanishing gradients). A single learning rate $\eta$ is too large for some parameters and too small for others.
  \item \textbf{Sparse gradients:} Embedding layers receive gradients only for tokens in the current batch. Most embedding rows have zero gradient. SGD with momentum wastes momentum on zero-gradient rows.
  \item \textbf{Saddle points:} High-dimensional loss landscapes have many saddle points. SGD can stall; adaptive methods escape faster.
  \item \textbf{Sensitivity to learning rate:} SGD requires careful tuning; a 2$\times$ change in $\eta$ can cause divergence.
\end{itemize}
\end{warningbox}

\begin{warningbox}[SGD对LLM的问题]
\begin{itemize}
  \item \textbf{每层梯度规模不同：}Transformer中的早期层梯度比后期层小得多（梯度消失）。单一学习率$\eta$对某些参数太大，对另一些参数太小。
  \item \textbf{稀疏梯度：}嵌入层只接收当前批量中token的梯度。大多数嵌入行梯度为零。带动量的SGD在零梯度行上浪费动量。
  \item \textbf{鞍点：}高维损失景观中有许多鞍点。SGD可能会停滞；自适应方法能更快逃离。
  \item \textbf{对学习率敏感：}SGD需要仔细调参；$\eta$变化2倍可能导致发散。
\end{itemize}
\end{warningbox}

\subsection{Adam -- Adaptive Moment Estimation}
\subsection{Adam——自适应矩估计}
\label{adam-adaptive-moment-estimation}

Adam~\cite{kingma2015adam} maintains per-parameter estimates of the first moment (mean of gradients) and second moment (uncentered variance of gradients).

Adam~\cite{kingma2015adam}维护每个参数的一阶矩（梯度的均值）和二阶矩（梯度的非中心方差）的估计。

\begin{keybox}[Adam Update Equations]
Given gradient $g_t = \nabla_\theta \mathcal{L}(\theta_t)$, hyperparameters $\beta_1, \beta_2, \epsilon, \eta$:

\begin{keybox}[Adam更新方程]
给定梯度$g_t = \nabla_\theta \mathcal{L}(\theta_t)$，超参数$\beta_1, \beta_2, \epsilon, \eta$：

\textbf{Step 1 -- Update biased first moment estimate:} 
\[
m_t = \beta_1 m_{t-1} + (1 - \beta_1) g_t
\]

\textbf{步骤1——更新有偏一阶矩估计：}
\[
m_t = \beta_1 m_{t-1} + (1 - \beta_1) g_t
\]

\textbf{Step 2 -- Update biased second moment estimate:} 
\[
v_t = \beta_2 v_{t-1} + (1 - \beta_2) g_t^2
\]

\textbf{步骤2——更新有偏二阶矩估计：}
\[
v_t = \beta_2 v_{t-1} + (1 - \beta_2) g_t^2
\]

\textbf{Step 3 -- Bias correction:} 
\[
\hat{m}_t = \frac{m_t}{1 - \beta_1^t}, \qquad \hat{v}_t = \frac{v_t}{1 - \beta_2^t}
\]

\textbf{步骤3——偏差校正：}
\[
\hat{m}_t = \frac{m_t}{1 - \beta_1^t}, \qquad \hat{v}_t = \frac{v_t}{1 - \beta_2^t}
\]

\textbf{Step 4 -- Parameter update:} 
\[
\theta_{t+1} = \theta_t - \eta \cdot \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}
\]

\textbf{步骤4——参数更新：}
\[
\theta_{t+1} = \theta_t - \eta \cdot \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}
\]

\textbf{Typical values:} $\beta_1 = 0.9$, $\beta_2 = 0.95$ or $0.999$, $\epsilon = 10^{-8}$, $\eta = 10^{-4}$ to $10^{-5}$.
\end{keybox}

\textbf{典型值：} $\beta_1 = 0.9$, $\beta_2 = 0.95$ 或 $0.999$, $\epsilon = 10^{-8}$, $\eta = 10^{-4}$ 到 $10^{-5}$。
\end{keybox}

\newpage
\begin{intuitionbox}[What Each Term Does]
\begin{itemize}
  \item $m_t$ (\textbf{momentum}): Exponential moving average of gradients. Smooths out noisy gradient estimates. $\beta_1 = 0.9$ means the current gradient contributes 10\% and the history contributes 90\%.
  \item $v_t$ (\textbf{adaptive LR}): EMA of squared gradients. Parameters with consistently large gradients get a smaller effective learning rate ($\eta / \sqrt{v_t}$). Parameters with small gradients get a larger effective LR. This is the key to handling different gradient scales per layer.
  \item $\hat{m}_t, \hat{v}_t$ (\textbf{bias correction}): At $t=1$, $m_1 = (1-\beta_1)g_1$ is much smaller than the true mean. Dividing by $(1-\beta_1^t)$ corrects this initialization bias. Without it, early steps are too small.
  \item $\epsilon$ (\textbf{numerical stability}): Prevents division by zero. Also acts as a floor on the effective learning rate.
\end{itemize}
\end{intuitionbox}

\begin{intuitionbox}[每个项的作用]
\begin{itemize}
  \item $m_t$（\textbf{动量}）：梯度的指数移动平均。平滑有噪声的梯度估计。$\beta_1 = 0.9$意味着当前梯度贡献10%，历史贡献90%。
  \item $v_t$（\textbf{自适应学习率}）：平方梯度的指数移动平均。梯度持续大的参数获得较小的有效学习率（$\eta / \sqrt{v_t}$）。梯度小的参数获得较大的有效学习率。这是处理每层不同梯度规模的关键。
  \item $\hat{m}_t, \hat{v}_t$（\textbf{偏差校正}）：在$t=1$时，$m_1 = (1-\beta_1)g_1$远小于真实均值。除以$(1-\beta_1^t)$校正了这种初始化偏差。没有它，早期步长会太小。
  \item $\epsilon$（\textbf{数值稳定性}）：防止除零。同时也作为有效学习率的下限。
\end{itemize}
\end{intuitionbox}

\subsection{AdamW -- Decoupled Weight Decay}
\subsection{AdamW——解耦权重衰减}
\label{adamw-decoupled-weight-decay}

AdamW~\cite{loshchilov2019adamw} fixes a subtle but important issue with how weight decay interacts with adaptive optimizers.

AdamW~\cite{loshchilov2019adamw}修复了一个微妙但重要的问题，即权重衰减与自适应优化器的交互方式。

\begin{keybox}[Why L2 Regularization $\neq$ Weight Decay in Adam]
With L2 regularization, the loss becomes $\mathcal{L} + \frac{\lambda}{2}\|\theta\|^2$, so the gradient is $g_t + \lambda \theta_t$. In Adam, this regularization gradient is \emph{scaled by the adaptive factor} $1/\sqrt{\hat{v}_t}$: 
\[
\theta_{t+1} = \theta_t - \eta \cdot \frac{\hat{m}_t + \lambda \theta_t}{\sqrt{\hat{v}_t} + \epsilon}
\]
 Parameters with large $v_t$ (large gradient variance) get \emph{less} regularization. This is not what we want -- weight decay should be uniform.
\end{keybox}

\begin{keybox}[为什么L2正则化 $\neq$ Adam中的权重衰减]
使用L2正则化时，损失变为$\mathcal{L} + \frac{\lambda}{2}\|\theta\|^2$，因此梯度为$g_t + \lambda \theta_t$。在Adam中，这个正则化梯度被自适应因子$1/\sqrt{\hat{v}_t}$\emph{缩放}：
\[
\theta_{t+1} = \theta_t - \eta \cdot \frac{\hat{m}_t + \lambda \theta_t}{\sqrt{\hat{v}_t} + \epsilon}
\]
具有大$v_t$（大梯度方差）的参数获得的\emph{更少}的正则化。这不是我们想要的——权重衰减应该是均匀的。
\end{keybox}

\begin{keybox}[AdamW – Decoupled Weight Decay]
\begin{keybox}[AdamW – 解耦权重衰减]

AdamW (Loshchilov \& Hutter, 2017) applies weight decay \emph{directly} to the parameters, outside the adaptive scaling: 
AdamW（Loshchilov \& Hutter, 2017）将权重衰减 \emph{直接} 应用于参数，独立于自适应缩放：

\[
\theta_{t+1} = \theta_t - \eta \cdot \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}
  - \eta \lambda \theta_t
\]

The weight decay term $\eta \lambda \theta_t$ is not divided by $\sqrt{\hat{v}_t}$. This gives uniform regularization across all parameters regardless of their gradient history.
权重衰减项 $\eta \lambda \theta_t$ 不会被 $\sqrt{\hat{v}_t}$ 除。这使得所有参数获得统一的正则化，与它们的梯度历史无关。

\textbf{Typical value:} $\lambda = 0.1$ for LLM training.
\textbf{典型值：} LLM 训练中 $\lambda = 0.1$。
\end{keybox}


\begin{warningbox}[Always Use AdamW – Never Plain Adam – for LLMs]
\begin{warningbox}[LLM 训练始终使用 AdamW – 切勿使用普通 Adam]

The difference between Adam and AdamW is subtle but matters. With Adam + L2, the effective weight decay is stronger for parameters with small gradient variance (e.g., biases, LayerNorm parameters) and weaker for parameters with large gradient variance (e.g., attention weights). AdamW gives the intended uniform regularization. Most frameworks default to AdamW; double-check your optimizer class.
Adam 与 AdamW 的差异虽细微但至关重要。使用 Adam + L2 时，梯度方差较小的参数（如偏置、LayerNorm 参数）的有效权重衰减更强，而梯度方差较大的参数（如注意力权重）则更弱。AdamW 实现了预期的统一正则化。大多数框架默认使用 AdamW；请务必检查你的优化器类。
\end{warningbox}


\newpage
\subsection{Learning Rate -- The Most Important Hyperparameter}
\subsection{学习率——最重要的超参数}
\label{learning-rate-the-most-important-hyperparameter}


\begin{keybox}[Typical Learning Rates by Training Phase]
\begin{keybox}[各训练阶段的典型学习率]
\begin{tabular}{@{}lp{4cm}p{5.5cm}@{}}
\toprule
\textbf{Phase} & \textbf{Typical LR} & \textbf{Notes} \\
\textbf{阶段} & \textbf{典型学习率} & \textbf{说明} \\
\midrule
Pretraining (from scratch) & $1\text{e-}4$ to $3\text{e-}4$ & Large model, large batch \\
预训练（从头开始） & $1\text{e-}4$ 至 $3\text{e-}4$ & 大模型，大批量 \\
Continued pretraining & $1\text{e-}5$ to $1\text{e-}4$ & Smaller LR to preserve knowledge \\
继续预训练 & $1\text{e-}5$ 至 $1\text{e-}4$ & 较小学习率以保留知识 \\
SFT (supervised fine-tune) & $1\text{e-}5$ to $2\text{e-}5$ & Standard range \\
SFT（监督微调） & $1\text{e-}5$ 至 $2\text{e-}5$ & 标准范围 \\
LoRA fine-tuning & $1\text{e-}4$ to $3\text{e-}4$ & Higher LR for adapter weights \\
LoRA 微调 & $1\text{e-}4$ 至 $3\text{e-}4$ & 适配器权重使用较高学习率 \\
\bottomrule
\end{tabular}


\smallskip
\noindent\emph{For RL learning rates (PPO, DPO, GRPO) see §\ref{sec:rl-optimizer-config}.}
\noindent\emph{关于强化学习率（PPO、DPO、GRPO），参见第 §\ref{sec:rl-optimizer-config} 节。}
\end{keybox}


\subsection{Learning Rate Warmup}
\subsection{学习率预热}
\label{learning-rate-warmup}


\begin{keybox}[Why Warmup is Necessary]
\begin{keybox}[为什么需要预热]
At the start of training, $v_t$ (the second moment estimate) is initialized to zero. After bias correction: $\hat{v}_t = v_t / (1 - \beta_2^t)$. At $t=1$ with $\beta_2 = 0.999$: $\hat{v}_1 = v_1 / (1 - 0.999) = 1000 v_1$. This means the effective learning rate is $\eta / \sqrt{1000 v_1}$ -- much smaller than intended.
训练开始时，$v_t$（二阶矩估计）初始化为零。经过偏差校正后：$\hat{v}_t = v_t / (1 - \beta_2^t)$。当 $t=1$ 且 $\beta_2 = 0.999$ 时：$\hat{v}_1 = v_1 / (1 - 0.999) = 1000 v_1$。这意味着有效学习率为 $\eta / \sqrt{1000 v_1}$ —— 远小于预期值。

However, if the first gradient is unusually large (common at initialization), the second moment estimate can be dominated by this outlier, causing erratic early steps. Warmup mitigates this by starting with a very small LR and gradually increasing it, giving $v_t$ time to accumulate a reliable estimate.
然而，如果第一个梯度异常大（这在初始化时很常见），二阶矩估计可能会被这个异常值主导，导致早期步骤不稳定。预热通过从一个非常小的学习率开始并逐渐增加来缓解这一问题，使 $v_t$ 有时间累积一个可靠的估计。
\end{keybox}


\begin{itemize}
  \item \textbf{Linear warmup:} $\eta_t = \eta_{\max} \times t / T_{\text{warmup}}$
  \item \textbf{线性预热：} $\eta_t = \eta_{\max} \times t / T_{\text{warmup}}$
  \item \textbf{Typical warmup duration:} 1--5\% of total steps for pretraining; 3--10\% for fine-tuning (shorter runs need proportionally more warmup)
  \item \textbf{典型预热时长：} 预训练为总步数的 1--5%；微调为 3--10%（较短运行需要按比例增加预热）
  \item \textbf{For SFT:} 50--200 warmup steps is typical
  \item \textbf{对于 SFT：} 典型为 50--200 预热步
\end{itemize}


\subsection{Learning Rate Schedules}
\subsection{学习率调度}
\label{learning-rate-schedules}


\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_010_fig10.png}
\caption{Common learning rate schedules. All include a linear warmup phase. WSD (Warmup-Stable-Decay) is the emerging standard for pretraining.}
\caption{常见学习率调度。所有调度都包含线性预热阶段。WSD（预热-稳定-衰减）正在成为预训练的行业标准。}
\end{figure}


\paragraph{(a) Constant.}
\paragraph{(a) 常数。}
\label{a-constant.}


Simplest schedule. Good for short fine-tuning runs where you want to avoid over-decaying the LR. Risk: no annealing means the model may not converge to the sharpest minimum.
最简单的调度。适用于希望避免学习率过度衰减的短时微调。风险：没有退火意味着模型可能不会收敛到最尖锐的最小值。


\paragraph{(b) Cosine Decay.}
\paragraph{(b) 余弦衰减。}
\label{b-cosine-decay.}


\[
\eta_t = \eta_{\min} + \frac{1}{2}(\eta_{\max} - \eta_{\min})
  \left(1 + \cos\!\left(\frac{t - T_{\text{warmup}}}{T - T_{\text{warmup}}} \pi\right)\right)
\]
 Standard for pretraining and SFT. Smooth decay avoids abrupt LR changes. $\eta_{\min}$ is typically $\eta_{\max} / 10$.
预训练和 SFT 的标准选择。平滑衰减避免了学习率的突变。$\eta_{\min}$ 通常为 $\eta_{\max} / 10$。


\paragraph{(c) Linear Decay.}
\paragraph{(c) 线性衰减。}
\label{c-linear-decay.}


Simpler than cosine, similar empirical results. Preferred when you want predictable LR at any step.
比余弦更简单，经验结果相似。当你希望在任何步骤都有可预测的学习率时，优先选择。


\paragraph{(d) WSD -- Warmup-Stable-Decay.}
\paragraph{(d) WSD——预热-稳定-衰减。}
\label{d-wsd-warmup-stable-decay.}


The new standard for large-scale pretraining~\cite{hu2024minicpm, grattafiori2024llama3}. Three phases:
大规模预训练的新标准~\cite{hu2024minicpm, grattafiori2024llama3}。包含三个阶段：

\begin{enumerate}
  \item \textbf{Warmup:} Linear ramp to $\eta_{\max}$ (1--5\% of steps)
  \item \textbf{预热：} 线性增加到 $\eta_{\max}$（占步数的 1--5%）
  \item \textbf{Stable:} Constant $\eta_{\max}$ for the majority of training
  \item \textbf{稳定阶段：} 大部分训练过程保持恒定 $\eta_{\max}$
  \item \textbf{Decay:} Fast cosine or linear decay to $\eta_{\min}$ (last 10--20\% of steps)
  \item \textbf{衰减阶段：} 快速余弦或线性衰减至 $\eta_{\min}$（最后 10--20% 的步数）
\end{enumerate}


Key advantage: the stable phase allows checkpointing at any point and continuing training. The decay phase can be applied at the end of any run.
关键优势：稳定阶段允许在任何点进行检查点保存并继续训练。衰减阶段可以在任何训练运行的末尾应用。


\paragraph{(e) Cosine with Restarts (SGDR).}
\paragraph{(e) 带重启的余弦（SGDR）。}
\label{e-cosine-with-restarts-sgdr.}


Periodic restarts reset the LR to $\eta_{\max}$. Can help escape local minima. Less common for LLMs; more useful for smaller models.
周期性重启将学习率重置为 $\eta_{\max}$。有助于逃离局部最小值。在 LLM 中不太常见；对较小模型更有用。


\subsection{Gradient Clipping}
\subsection{梯度裁剪}
\label{gradient-clipping}


\begin{keybox}[Gradient Clipping]
\begin{keybox}[梯度裁剪]
Gradient clipping rescales the gradient if its global norm exceeds a threshold: 
梯度裁剪会在梯度的全局范数超过阈值时重新缩放梯度：
\[
g_t \leftarrow g_t \cdot \min\!\left(1,\; \frac{\tau}{\|g_t\|_2}\right)
\]
 where $\tau$ is \texttt{max\_grad\_norm} (typically 1.0).
其中 $\tau$ 为 \texttt{max\_grad\_norm}（通常为 1.0）。
\end{keybox}


\begin{intuitionbox}[Gradient Clipping vs. LR Reduction]
\begin{intuitionbox}[梯度裁剪 vs. 降低学习率]
Gradient clipping and reducing the learning rate both limit the size of parameter updates. The difference: clipping preserves the \emph{direction} of the gradient (just scales the magnitude), while a smaller LR scales all updates uniformly. Clipping is better for handling occasional large gradients without slowing down normal training steps.
梯度裁剪和降低学习率都限制了参数更新的幅度。区别在于：裁剪保留了梯度的 \emph{方向}（仅缩放大小），而较小的学习率均匀缩放所有更新。裁剪更适合处理偶尔出现的大梯度，同时不拖慢正常训练步。
\end{intuitionbox}


\subsubsection{Putting It Together: HuggingFace Optimizer Configuration}
\subsubsection{综合应用：HuggingFace 优化器配置}
\label{putting-it-together-huggingface-optimizer-configuration}


The following snippet shows how the concepts from this section---AdamW with decoupled weight decay (§1.6.6), cosine learning-rate scheduling with linear warmup (§1.6.7), and gradient clipping (§1.6.8)---come together in practice using the HuggingFace \texttt{transformers} library.
以下代码片段展示了本节的概念——解耦权重衰减的 AdamW（第 1.6.6 节）、带线性预热的余弦学习率调度（第 1.6.7 节）和梯度裁剪（第 1.6.8 节）——如何通过 HuggingFace \texttt{transformers} 库在实践中组合使用。

\begin{lstlisting}[style=pythonstyle, caption={Complete optimizer configuration combining AdamW -- cosine schedule -- and gradient clipping.}]
\begin{lstlisting}[style=pythonstyle, caption={完整的优化器配置：结合 AdamW、余弦调度和梯度裁剪。}]
from transformers import TrainingArguments, Trainer
from transformers import get_cosine_schedule_with_warmup
import torch


