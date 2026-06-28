# 输出: trainable params: 83,886,080 || all params: 70,553,706,496 || 0.12%
\end{lstlisting}


\subsection{Other PEFT Approaches}
\subsection{其他 PEFT 方法}
\label{other-peft-approaches}


LoRA dominates modern practice, but it is not the only parameter-efficient method. For completeness, the main alternatives:
LoRA 主导了现代实践，但它并非唯一的参数高效方法。为完整起见，以下是主要替代方案：


\begin{table}[ht!]
\centering
\caption{PEFT method families. LoRA is the de facto standard for LLM fine-tuning; the others are included for historical context and niche use cases.}
\caption{PEFT 方法族。LoRA 是 LLM 微调的事实标准；其他方法则因历史背景和特定用例而收录。}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{4cm}@{}}
\toprule
\textbf{Method} & \textbf{Mechanism} & \textbf{Pros / Cons} & \textbf{Status} \\
\textbf{方法} & \textbf{机制} & \textbf{优点/缺点} & \textbf{状态} \\
\midrule
\textbf{LoRA}~\cite{hu2021lora} (and variants) & Low-rank matrices added to existing weights & Mergeable at inference (zero overhead); well-supported; works for all architectures & \textbf{Standard} \\
\textbf{LoRA}~\cite{hu2021lora}（及变体） & 向现有权重添加低秩矩阵 & 推理时可合并（零开销）；支持良好；适用于所有架构 & \textbf{标准} \\
\textbf{Adapters}~\cite{houlsby2019adapters} & Small bottleneck MLPs inserted between layers & Modular; stackable; adds inference latency (extra sequential layers) & Rarely used \\
\textbf{适配器 (Adapters)}~\cite{houlsby2019adapters} & 在层间插入小型瓶颈 MLP & 模块化；可堆叠；增加推理延迟（额外的顺序层） & 很少使用 \\
\textbf{Prefix Tuning}~\cite{li2021prefix} & Learnable ``virtual tokens'' prepended to keys/values at each layer & No weight modification; effective for generation tasks; consumes context length & Niche \\
\textbf{前缀微调 (Prefix Tuning)}~\cite{li2021prefix} & 在每个层的键/值前添加可学习的“虚拟令牌” & 不修改权重；对生成任务有效；消耗上下文长度 & 小众 \\
\textbf{Prompt Tuning}~\cite{lester2021prompt} & Learnable soft prompt embeddings prepended to input & Extremely few params ($<$0.01\%); weaker than LoRA for complex tasks & Niche \\
\textbf{提示微调 (Prompt Tuning)}~\cite{lester2021prompt} & 在输入前添加可学习的软提示嵌入 & 参数极少（$<$0.01\%）；在复杂任务上弱于 LoRA & 小众 \\
\textbf{IA3}~\cite{liu2022ia3} & Learned vectors that rescale keys, values, and FFN activations & Even fewer params than LoRA; mergeable; limited capacity & Deprecated \\
\textbf{IA3}~\cite{liu2022ia3} & 学习缩放键、值和 FFN 激活的向量 & 参数比 LoRA 更少；可合并；容量有限 & 已弃用 \\
\textbf{BitFit}~\cite{zaken2022bitfit} & Train only bias terms & Near-zero params; surprisingly effective for simple tasks; limited expressiveness & Historical \\
\textbf{BitFit}~\cite{zaken2022bitfit} & 仅训练偏置项 & 参数接近零；对简单任务出奇有效；表达能力有限 & 历史 \\
\bottomrule
\end{tabular}
\end{table}


\begin{intuitionbox}[Why LoRA Won]
\begin{intuitionbox}[LoRA 为何胜出]
LoRA became the standard because it uniquely combines: (1)~\textbf{zero inference overhead} --- adapters merge into base weights, unlike Adapters or Prefix Tuning which add latency or consume context; (2)~\textbf{composability} --- multiple LoRA adapters can be swapped at serving time for multi-tenant deployments; (3)~\textbf{ecosystem support} --- HuggingFace PEFT, TRL, vLLM, and all major frameworks have first-class LoRA support; (4)~\textbf{proven at scale} --- used in production by Meta, Google, and most open-source fine-tunes on HuggingFace. Unless you have a specific constraint that LoRA cannot satisfy, it should be your default choice.
LoRA 成为标准是因为它独特地结合了：(1)~\textbf{零推理开销} —— 适配器可合并到基权重中，不像适配器 (Adapters) 或前缀微调 (Prefix Tuning) 那样增加延迟或消耗上下文；(2)~\textbf{可组合性} —— 服务时可切换多个 LoRA 适配器以实现多租户部署；(3)~\textbf{生态系统支持} —— HuggingFace PEFT、TRL、vLLM 以及所有主流框架都对 LoRA 提供了一流支持；(4)~\textbf{大规模验证} —— 已被 Meta、Google 以及 HuggingFace 上的大多数开源微调模型在生产中使用。除非你有 LoRA 无法满足的特定约束，否则它应该是你的默认选择。
\end{intuitionbox}


\clearpage
\section{Mixture of Experts (MoE)}
\section{混合专家 (Mixture of Experts, MoE)}
\label{mixture-of-experts-moe}


Mixture of Experts models~\cite{shazeer2017outrageously, jiang2024mixtral} scale model capacity without proportionally scaling compute cost by activating only a subset of parameters for each token.
混合专家 (Mixture of Experts, MoE) 模型~\cite{shazeer2017outrageously, jiang2024mixtral} 通过仅为每个令牌激活一部分参数，在不按比例增加计算成本的情况下扩展模型容量。


\subsection{Architecture}
\subsection{架构}
\label{architecture}


\begin{keybox}[MoE Layer]
\begin{keybox}[MoE 层]
In a MoE transformer, the FFN layer in each block is replaced by $N$ parallel ``expert'' FFNs plus a \textbf{router} that selects which experts to use: 
在 MoE 变换器中，每个块中的 FFN 层被替换为 $N$ 个并行的“专家”FFN 加上一个 \textbf{路由器}，该路由器选择使用哪些专家：
\[
\text{MoE}(x) = \sum_{i=1}^{N} g_i(x) \cdot E_i(x), \quad g(x) = \text{TopK}(\text{softmax}(W_r x))
\]


\begin{itemize}
  \item $E_i$ are expert networks (standard FFN layers)
  \item $g_i(x)$ are gating weights from the router (only top-$K$ are non-zero)
  \item Typically $K=2$ out of $N=8$--64 experts are active per token
  \item Total params scale with $N$; \textbf{active params} scale with $K/N$ of FFN size
\end{itemize}
\begin{itemize}
  \item $E_i$ 是专家网络（标准 FFN 层）
  \item $g_i(x)$ 是路由器的门控权重（仅 top-$K$ 非零）
  \item 通常每个令牌激活 $N=8$--64 个专家中的 $K=2$ 个
  \item 总参数随 $N$ 扩展；\textbf{活跃参数} 随 FFN 大小的 $K/N$ 扩展
\end{itemize}
\end{keybox}


\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_012_fig12.png}
\caption{MoE layer with 8 experts and Top-2 routing. Only the two highest-gated experts are computed per token; the rest are skipped entirely.}
\caption{具有 8 个专家和 Top-2 路由的 MoE 层。每个令牌仅计算门控得分最高的两个专家；其余专家被完全跳过。}
\end{figure}


\subsection{Load Balancing}
\subsection{负载均衡}
\label{load-balancing}


\begin{warningbox}[The Load Balancing Problem]
\begin{warningbox}[负载均衡问题]
Without constraints, the router may send most tokens to the same 1--2 experts (``expert collapse''). This wastes capacity and creates compute imbalance across GPUs (each expert typically lives on a different GPU).
在没有约束的情况下，路由器可能将大多数令牌发送给相同的 1--2 个专家（“专家崩溃”）。这会浪费容量并在 GPU 之间造成计算不平衡（每个专家通常位于不同的 GPU 上）。


\textbf{Solution}: Add an auxiliary load-balancing loss: 
\textbf{解决方案}：添加一个辅助负载均衡损失：
\[
\mathcal{L}_{\text{bal}} = \alpha \cdot N \sum_{i=1}^{N} f_i \cdot p_i
\]
 where $f_i$ = fraction of tokens routed to expert $i$, $p_i$ = mean router probability for expert $i$. This encourages uniform expert utilization.
其中 $f_i$ = 路由到专家 $i$ 的令牌比例，$p_i$ = 专家 $i$ 的平均路由器概率。这鼓励专家利用率均匀分布。
\end{warningbox}


\subsection{Noisy Top-K Gating: Making Discrete Routing Trainable}
\subsection{带噪声的 Top-K 门控：使离散路由可训练}
\label{noisy-top-k-gating-making-discrete-routing-trainable}


The core challenge in MoE is that \textbf{top-$k$ selection is not differentiable} --- you can’t backpropagate through a hard ``pick the top 2'' operation. The field has developed two key tricks to solve this:
MoE 的核心挑战是 \textbf{top-$k$ 选择不可微} —— 你无法通过硬性的“选择前 top 2”操作进行反向传播。该领域已开发出两种关键技巧来解决这个问题：


\begin{intuitionbox}[The Routing Differentiability Problem]
\begin{intuitionbox}[路由可微性问题]
The router computes logits $h(x) = W_r \cdot x$ for each expert, then selects the top-$k$. But:
路由器为每个专家计算 logits $h(x) = W_r \cdot x$，然后选择 top-$k$。但是：


\begin{itemize}
  \item The \emph{selected} experts get gradients through their gate weights (softmax over selected)
  \item The \emph{selection decision itself} (which $k$ to pick) has zero gradient
  \item Without a trick, the router can get stuck: an expert never selected $\rightarrow$ never gets a gradient signal $\rightarrow$ never gets selected
\end{itemize}
\begin{itemize}
  \item \emph{被选中的}专家通过其门控权重（对选定者做 softmax）获得梯度
  \item \emph{选择决策本身}（选择哪个 $k$）的梯度为零
  \item 没有技巧的话，路由器可能陷入困境：一个专家从未被选中 $\rightarrow$ 从未获得梯度信号 $\rightarrow$ 永远不被选中
\end{itemize}
\end{intuitionbox}


\paragraph{Approach 1: Noisy Top-K Gating~\cite{shazeer2017outrageously}.}
\paragraph{方法 1：带噪声的 Top-K 门控 (Noisy Top-K Gating)~\cite{shazeer2017outrageously}。}
\label{approach-1-noisy-top-k-gating-.}


Add learnable Gaussian noise to the router logits \emph{before} the top-$k$ selection:
在 top-$k$ 选择\emph{之前}向路由器 logits 添加可学习的高斯噪声：


\begin{align}
  h(x) &= W_g \cdot x \tag{clean logits} \\
  H(x) &= h(x) + \epsilon \cdot \text{Softplus}(W_{\text{noise}} \cdot x), \quad \epsilon \sim \mathcal{N}(0, 1) \tag{noisy logits} \\
  \text{TopK}(v, k)_i &= \begin{cases} v_i & \text{if } v_i \text{ is in the top } k \\ -\infty & \text{otherwise} \end{cases} \\
  g(x) &= \text{softmax}\big(\text{TopK}(H(x),\, k)\big) \tag{sparse gates}
\end{align}
\begin{align}
  h(x) &= W_g \cdot x \tag{干净的 logits} \\
  H(x) &= h(x) + \epsilon \cdot \text{Softplus}(W_{\text{noise}} \cdot x), \quad \epsilon \sim \mathcal{N}(0, 1) \tag{带噪声的 logits} \\
  \text{TopK}(v, k)_i &= \begin{cases} v_i & \text{if } v_i \text{ is in the top } k \\ -\infty & \text{otherwise} \end{cases} \\
  g(x) &= \text{softmax}\big(\text{TopK}(H(x),\, k)\big) \tag{稀疏门控}
\end{align}


\begin{itemize}
  \item $W_{\text{noise}}$ is a \emph{learned} noise magnitude --- the model learns how much exploration each expert needs
  \item During training, noise occasionally promotes ``underdog'' experts into the top-$k$, giving them gradient signal
  \item At inference, noise is removed: use clean logits $h(x)$ for deterministic routing
  \item The Softplus ensures noise scale is always positive
\end{itemize}
\begin{itemize}
  \item $W_{\text{noise}}$ 是一个\emph{可学习的}噪声幅度——模型学习每个专家需要多少探索
  \item 在训练期间，噪声偶尔会将“弱势”专家提升到 top-$k$ 中，从而为它们提供梯度信号
  \item 在推理时，移除噪声：使用干净的 logits $h(x)$ 进行确定性路由
  \item Softplus 确保噪声尺度始终为正
\end{itemize}


\paragraph{Approach 2: Gumbel-Softmax Trick (for differentiable discrete sampling).}
\paragraph{方法 2：Gumbel-Softmax 技巧（用于可微的离散采样）。}
\label{approach-2-gumbel-softmax-trick-for-differentiable-discrete-sampling.}


An alternative from the variational inference literature~\cite{jang2017categorical}. The \textbf{Gumbel-Max trick} provides exact sampling from a categorical distribution:
另一种方法来自变分推断文献~\cite{jang2017categorical}。\textbf{Gumbel-Max 技巧}提供了从分类分布中精确采样的方法：


\begin{equation}
  z = \arg\max_i \left[ \log \pi_i + G_i \right], \quad G_i \sim \text{Gumbel}(0,1)
\end{equation}


where Gumbel noise is generated as $G_i = -\log(-\log(U_i)),\; U_i \sim \text{Uniform}(0,1)$.
其中 Gumbel 噪声生成方式为 $G_i = -\log(-\log(U_i)),\; U_i \sim \text{Uniform}(0,1)$。


For \textbf{top-$k$ routing}: taking the top-$k$ of $(\log \pi_i + G_i)$ gives $k$ samples \emph{without replacement} from the categorical distribution defined by $\pi$.
对于 \textbf{top-$k$ 路由}：取 $(\log \pi_i + G_i)$ 的前 top-$k$ 个，得到从 $\pi$ 定义的分类分布中\emph{无放回}的 $k$ 个样本。


Since $\arg\max$ is non-differentiable, the \textbf{Gumbel-Softmax} relaxation replaces it with a temperature-controlled softmax:
由于 $\arg\max$ 不可微，\textbf{Gumbel-Softmax} 松弛将其替换为受温度控制的 softmax：


\begin{equation}
  \hat{g}_i = \frac{\exp\left((\log \pi_i + G_i) / \tau\right)}{\sum_j \exp\left((\log \pi_j + G_j) / \tau\right)}
\end{equation}
```

\begin{itemize}
  \item $\tau \to 0$: approaches a hard one-hot (exact but non-differentiable)
  \item $\tau \to 0$：趋近于硬独热（精确但不可微）
  \item $\tau \to \infty$: approaches uniform (differentiable but uninformative)
  \item $\tau \to \infty$：趋近于均匀分布（可微但信息量低）
  \item In practice, anneal $\tau$ from 1.0 down to 0.1--0.5 during training
  \item 在实际训练中，将 $\tau$ 从 1.0 退火至 0.1--0.5
  \item \textbf{Straight-through estimator（直通估计器）}: use hard top-$k$ in the forward pass, but Gumbel-Softmax gradients in the backward pass --- best of both worlds
  \item \textbf{Straight-through estimator（直通估计器）}：在前向传播中使用硬 top-$k$，但在反向传播中使用 Gumbel-Softmax 梯度——两全其美
\end{itemize}

\begin{keybox}[实践中使用哪种方法？]
\begin{itemize}
  \item \textbf{Sparsely-Gated MoE~\cite{shazeer2017outrageously}, Mixtral~\cite{jiang2024mixtral}, DeepSeek-V2~\cite{deepseekv2}}: Use Noisy Top-K with Gaussian noise. Simple, effective, well-proven at scale.
  \item \textbf{Sparsely-Gated MoE~\cite{shazeer2017outrageously}、Mixtral~\cite{jiang2024mixtral}、DeepSeek-V2~\cite{deepseekv2}}：使用带高斯噪声的Noisy Top-K。简单、有效，在大规模上得到了充分验证。
  \item \textbf{Switch Transformer~\cite{fedus2022switch}}: Simplified to Top-1 with no noise (relies on load-balancing loss alone).
  \item \textbf{Switch Transformer~\cite{fedus2022switch}}：简化为无噪声的Top-1（仅依赖于负载均衡损失）。
  \item \textbf{Research / smaller-scale MoE}: Some use Gumbel-Softmax for fully differentiable routing, especially when learning the routing itself is the research objective.
  \item \textbf{研究/小规模MoE}：有些使用Gumbel-Softmax实现完全可微路由，尤其是当学习路由本身是研究目标时。
  \item \textbf{Key insight}: Both approaches solve the same problem (making discrete selection trainable) via noise injection. Gaussian noise is simpler; Gumbel noise has stronger theoretical guarantees for categorical sampling.
  \item \textbf{关键洞察}：这两种方法都通过注入噪声解决了同一个问题（使离散选择可训练）。高斯噪声更简单；Gumbel噪声在类别采样方面具有更强的理论保证。
\end{itemize}
\end{keybox}

\subsection{Notable MoE Models}
\subsection{值得关注的MoE模型}
\label{notable-moe-models}

\begin{tabular}{@{}lp{2.5cm}p{2.8cm}p{2.8cm}p{2.8cm}@{}}
\toprule
\textbf{Model} & \textbf{Total Params} & \textbf{Active Params} & \textbf{Experts} & \textbf{Innovation} \\
\textbf{模型} & \textbf{总参数量} & \textbf{激活参数量} & \textbf{专家数} & \textbf{创新点} \\
\midrule
Switch Transformer~\cite{fedus2022switch} & 1.6T & 100B & 128, Top-1 & First large-scale MoE; simplified routing \\
Switch Transformer~\cite{fedus2022switch} & 1.6T & 100B & 128, Top-1 & 首个大规模MoE；简化路由 \\
Mixtral 8x7B~\cite{jiang2024mixtral} & 47B & 13B & 8, Top-2 & Open-weight; matches Llama-2 70B quality \\
Mixtral 8x7B~\cite{jiang2024mixtral} & 47B & 13B & 8, Top-2 & 开源权重；匹配Llama-2 70B质量 \\
DeepSeek-V2~\cite{deepseekv2} & 236B & 21B & 160, Top-6 & DeepSeekMoE with shared + routed experts \\
DeepSeek-V2~\cite{deepseekv2} & 236B & 21B & 160, Top-6 & DeepSeekMoE结合共享专家和路由专家 \\
Qwen-MoE~\cite{qwen2024qwen25} & 14.3B & 2.7B & 60, Top-4 & Fine-grained experts for efficiency \\
Qwen-MoE~\cite{qwen2024qwen25} & 14.3B & 2.7B & 60, Top-4 & 细粒度专家以提高效率 \\
DBRX~\cite{databricks2024dbrx} & 132B & 36B & 16, Top-4 & Fine-grained with 4 experts per block \\
DBRX~\cite{databricks2024dbrx} & 132B & 36B & 16, Top-4 & 每个块4个专家的细粒度结构 \\
\bottomrule
\end{tabular}

\section{Diversity in LLM Training}
\section{LLM训练中的多样性}
\label{diversity-in-llm-training}

Diversity --- in training data, model outputs, and optimization trajectories --- is critical for preventing mode collapse and ensuring robust, general-purpose LLMs. This section covers the key diversity mechanisms applicable to all LLM training phases.
多样性——在训练数据、模型输出和优化轨迹中——对于防止模式崩溃和确保稳健、通用的LLM至关重要。本节涵盖了适用于所有LLM训练阶段的关键多样性机制。

\subsection{Sampling Diversity}
\subsection{采样多样性}
\label{sampling-diversity}

\begin{keybox}[多样生成的采样策略]
\begin{itemize}
  \item \textbf{Temperature $\tau$}: $P(x_i) \propto \exp(\text{logit}_i / \tau)$. Higher $\tau$ = more uniform distribution = more diverse. Typical: $\tau=0.7$--$1.0$ for RLHF generation.
  \item \textbf{温度 $\tau$}：$P(x_i) \propto \exp(\text{logit}_i / \tau)$。更高的 $\tau$ = 更均匀的分布 = 更多样化。典型值：RLHF生成中 $\tau=0.7$--$1.0$。
  \item \textbf{Top-$k$}: Only sample from the $k$ highest-probability tokens. Prevents degenerate low-probability tokens.
  \item \textbf{Top-$k$}：仅从概率最高的 $k$ 个token中采样。防止出现退化的低概率token。
  \item \textbf{Top-$p$ (nucleus)}: Sample from the smallest set of tokens whose cumulative probability $\geq p$. Adaptive: more diverse when the model is uncertain.
  \item \textbf{Top-$p$（核心采样）}：从累积概率 $\geq p$ 的最小token集合中采样。自适应：当模型不确定时更多样化。
  \item \textbf{Min-$p$}: Only keep tokens with $P \geq p_{\min} \times P_{\max}$. More principled than top-$k$.
  \item \textbf{Min-$p$}：仅保留 $P \geq p_{\min} \times P_{\max}$ 的token。比 top-$k$ 更合理。
  \item \textbf{Frequency/presence penalty}: Penalize tokens that appeared in the response. Encourages lexical diversity.
  \item \textbf{频率/出现惩罚}：惩罚在响应中出现过的token。鼓励词汇多样性。
\end{itemize}
\end{keybox}

\subsection{Training Data Diversity}
\subsection{训练数据多样性}
\label{training-data-diversity}

\begin{itemize}
  \item \textbf{Prompt diversity（提示多样性）}: Cover different domains, difficulty levels, and formats. The Goldilocks principle: prompts should have 20--80\% success rate.
  \item \textbf{Prompt diversity（提示多样性）}：覆盖不同领域、难度级别和格式。金发姑娘原则：提示应具有20--80%的成功率。
  \item \textbf{Deduplication}: Remove near-duplicate training examples (MinHash, n-gram overlap). Duplicates cause overfitting to specific patterns.
  \item \textbf{去重}：移除近似重复的训练样本（MinHash、n-gram重叠）。重复会导致对特定模式的过拟合。
  \item \textbf{Data mixing}: Balance across tasks/domains using temperature-weighted sampling or curriculum strategies.
  \item \textbf{数据混合}：使用温度加权采样或课程策略来平衡不同任务/领域。
\end{itemize}

\subsection{Diversity-Promoting Methods}
\subsection{促进多样性的方法}
\label{diversity-promoting-methods}

\begin{tabular}{@{}lp{11cm}@{}}
\toprule
\textbf{Method} & \textbf{How It Promotes Diversity} \\
\textbf{方法} & \textbf{如何促进多样性} \\
\midrule
Temperature scaling & Higher $\tau$ flattens the distribution; more tokens become plausible. \\
温度缩放 & 更高的 $\tau$ 使分布更平坦；更多token变得可行。 \\
Top-$p$ / Min-$p$ & Adaptive thresholds allow wider sampling when the model is uncertain. \\
Top-$p$ / Min-$p$ & 自适应阈值允许在模型不确定时进行更广泛的采样。 \\
Frequency penalty & Penalizes repeated tokens, forcing lexical variety within a response. \\
频率惩罚 & 惩罚重复的token，强制在响应中产生词汇多样性。 \\
Data deduplication & Removing near-duplicates from training data prevents overfitting to specific patterns. \\
数据去重 & 从训练数据中移除近似重复项可防止对特定模式的过拟合。 \\
Multi-domain mixing & Temperature-weighted sampling across domains ensures broad coverage. \\
多领域混合 & 跨领域的温度加权采样确保广泛覆盖。 \\
Verbalized sampling & Prompt the model to explicitly verbalize a probability distribution over responses~\cite{zhang2025verbalized}. See §\ref{grpo-variants-and-extensions}. \\
口头化采样 & 提示模型明确口头表达对响应的概率分布~\cite{zhang2025verbalized}。参见§\ref{grpo-variants-and-extensions}。 \\
\bottomrule
\end{tabular}

\section{Text Generation: Decoding Methods}
\section{文本生成：解码方法}
\label{text-generation-decoding-methods}

A trained language model outputs a probability distribution over the vocabulary at each step: $P(x_t | x_{<t})$. The \textbf{decoding strategy} determines how we select the next token from this distribution. This choice profoundly affects output quality, diversity, and coherence.
训练好的语言模型在每个步骤输出词汇表上的概率分布：$P(x_t | x_{<t})$。\textbf{解码策略}决定了我们如何从该分布中选择下一个token。这一选择深刻影响输出质量、多样性和连贯性。

\subsection{Greedy Decoding}
\subsection{贪心解码}
\label{greedy-decoding}

The simplest strategy: always pick the highest-probability token. 
\[
x_t = \arg\max_{v \in \mathcal{V}} P(v | x_{<t})
\]
最简单的策略：总是选择概率最高的token。 
\[
x_t = \arg\max_{v \in \mathcal{V}} P(v | x_{<t})
\]

\textbf{Int

\textbf{Intuition:} After ``The cat sat on the...'', only consider the top $k$ plausible continuations (``mat'', ``floor'', ``couch'', ...) and ignore extremely unlikely ones (``quantum'', ``archipelago'').

\textbf{直觉：} 在“The cat sat on the...”之后，只考虑最可能的 $k$ 个续词（“mat”、“floor”、“couch”……），忽略极不可能的续词（“quantum”、“archipelago”）。

\textbf{Pros:} Removes tail noise; simple to implement.\\

\textbf{优点：} 去除尾部噪声；实现简单。\\

\textbf{Cons:} Fixed $k$ is too restrictive for peaked distributions (wastes probability mass) and too permissive for flat distributions (lets in garbage tokens).

\textbf{缺点：} 固定的 $k$ 对于尖峰分布（概率质量浪费）过于严格，对于平坦分布（允许垃圾词进入）过于宽松。

\subsection{Top-$p$ (Nucleus) Sampling}
\subsection{Top-$p$（核）采样}
\label{top-p-nucleus-sampling}

Sample from the smallest set of tokens whose cumulative probability exceeds $p$: 
\[
\text{Top-}p = \min \left\{ S \subseteq \mathcal{V} : \sum_{v \in S} P(v | x_{<t}) \geq p \right\}
\]
 where tokens are sorted by descending probability and added until the threshold $p$ is reached.

从累积概率超过 $p$ 的最小词元集合中采样：
\[
\text{Top-}p = \min \left\{ S \subseteq \mathcal{V} : \sum_{v \in S} P(v | x_{<t}) \geq p \right\}
\]
其中词元按概率降序排列并逐个添加，直到达到阈值 $p$。

\textbf{Intuition:} Adaptively resize the candidate pool. If the model is confident (``Paris'' at 95\%), the nucleus is tiny. If uncertain (``The movie was...''), the nucleus expands to include many plausible adjectives.

\textbf{直觉：} 自适应调整候选池大小。如果模型很确信（“Paris”概率为95%），则核很小。如果不确定（“The movie was...”），则核会扩大以包含许多可能的形容词。

\textbf{Pros:} Adapts to distribution shape; widely used default ($p=0.9$--$0.95$).\\

\textbf{优点：} 适应分布形状；广泛使用的默认值（$p=0.9$--$0.95$）。\\

\textbf{Cons:} Still includes some low-quality tokens at the tail of the nucleus; the threshold is a single global hyperparameter.

\textbf{缺点：} 仍包含核尾部的一些低质量词元；阈值是单一的全局超参数。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_014_fig14.png}
\caption{Top-$p$ (nucleus) sampling: tokens are sorted by probability and included until cumulative mass reaches $p=0.9$. The nucleus (dark blue) adapts its size to the distribution shape --- here 5 tokens suffice.}
\caption{Top-$p$（核）采样：词元按概率排序并加入，直到累积质量达到 $p=0.9$。核（深蓝色）根据分布形状自适应调整大小——此处5个词元即够。}
\end{figure}

\begin{intuitionbox}[Top-kk vs. Top-pp]
Consider predicting the next word:

\begin{intuitionbox}[Top-kk vs. Top-pp]
考虑预测下一个词：

\begin{itemize}
  \item After ``2 + 2 ='': distribution is peaked --- top-1 token (``4'') has 99\% mass. Top-$k$=50 wastefully considers 49 wrong answers. Top-$p$=0.9 correctly picks just ``4''.
  \item After ``I enjoy eating'': distribution is flat --- many foods are plausible. Top-$k$=5 is too restrictive. Top-$p$=0.9 might include 50+ tokens, matching the actual uncertainty.
\end{itemize}

\begin{itemize}
  \item 在“2 + 2 =”之后：分布是尖峰型——top-1词元（“4”）占99%质量。Top-$k$=50浪费地考虑了49个错误答案。Top-$p$=0.9正确只选择“4”。
  \item 在“I enjoy eating”之后：分布平坦——很多食物都可能。Top-$k$=5过于严格。Top-$p$=0.9可能包含50+个词元，符合实际不确定性。
\end{itemize}

Top-$p$ adapts; top-$k$ doesn’t. In practice, both are often combined: sample from top-$p$ intersected with top-$k$.
\end{intuitionbox}

Top-$p$ 自适应；top-$k$ 不会。实践中常将两者结合：从 top-$p$ 与 top-$k$ 的交集中采样。
\end{intuitionbox}

\subsection{Min-$p$ Sampling}
\subsection{Min-$p$ 采样}
\label{min-p-sampling}

A recent alternative that sets a \textbf{relative} probability floor~\cite{nguyen2024minp}: 
\[
\text{Min-}p = \left\{ v \in \mathcal{V} : P(v | x_{<t}) \geq p_{\min} \cdot \max_{v'} P(v' | x_{<t}) \right\}
\]
 Only tokens with probability at least $p_{\min}$ times the top token’s probability are kept.

一种近期的替代方案，设定一个**相对**概率下限~\cite{nguyen2024minp}：
\[
\text{Min-}p = \left\{ v \in \mathcal{V} : P(v | x_{<t}) \geq p_{\min} \cdot \max_{v'} P(v' | x_{<t}) \right\}
\]
只保留概率至少为 top 词元概率 $p_{\min}$ 倍的词元。

\textbf{Intuition:} ``Only consider tokens that are at least 10\% as likely as the best token.'' If the top token has probability 0.8, only tokens above 0.08 survive. If the top token has probability 0.05 (very uncertain), tokens above 0.005 survive --- naturally expanding the pool.

\textbf{直觉：} “只考虑概率至少为最佳词元10%的词元。”如果 top 词元概率为0.8，则只有大于0.08的词元保留。如果 top 词元概率为0.05（非常不确定），则大于0.005的词元保留——自然地扩大词元池。

\textbf{Pros:} Scales naturally with model confidence; fewer degenerate samples than top-$p$ on peaked distributions; single intuitive parameter.\\

\textbf{优点：} 随模型置信度自然缩放；在尖峰分布上比 top-$p$ 产生更少的退化样本；单个直观参数。\\

\textbf{Cons:} Newer, less battle-tested; not yet standard in all inference frameworks.

\textbf{缺点：} 较新，测试不够充分；尚未成为所有推理框架的标准。

\subsection{Temperature Scaling}
\subsection{温度缩放}
\label{temperature-scaling}

Before applying any sampling strategy, logits are divided by temperature $T$: 
\[
P_T(v | x_{<t}) = \frac{\exp(z_v / T)}{\sum_{v'} \exp(z_{v'} / T)}
\]

在应用任何采样策略之前，logits 被温度 $T$ 除：
\[
P_T(v | x_{<t}) = \frac{\exp(z_v / T)}{\sum_{v'} \exp(z_{v'} / T)}
\]

\begin{itemize}
  \item $T < 1$: Sharpens distribution $\to$ more deterministic, focused outputs.
  \item $T = 1$: Unmodified model distribution.
  \item $T > 1$: Flattens distribution $\to$ more random, creative outputs.
  \item $T \to 0$: Becomes greedy decoding. $T \to \infty$: Becomes uniform sampling.
\end{itemize}

\begin{itemize}
  \item $T < 1$：锐化分布 $\to$ 更确定、更聚焦的输出。
  \item $T = 1$：未修改的模型分布。
  \item $T > 1$：展平分布 $\to$ 更随机、更具创造性的输出。
  \item $T \to 0$：变为贪心解码。$T \to \infty$：变为均匀采样。
\end{itemize}

\textbf{Common settings:} $T=0.7$ for factual tasks, $T=1.0$--$1.2$ for creative writing, $T=0.0$ (greedy) for code/math.

\textbf{常用设置：} 事实性任务 $T=0.7$，创意写作 $T=1.0$--$1.2$，代码/数学 $T=0.0$（贪心）。

\subsection{Contrastive Decoding}
\subsection{对比解码}
\label{contrastive-decoding}

Contrastive decoding~\cite{li2023contrastive} exploits the difference between a strong model (expert) and a weak model (amateur) to amplify the expert’s unique knowledge: 
\[
x_t = \arg\max_{v \in \mathcal{V}(x_{<t})} \left[ \log P_{\text{expert}}(v | x_{<t}) - \log P_{\text{amateur}}(v | x_{<t}) \right]
\]
 where $\mathcal{V}(x_{<t}) = \{v : P_{\text{expert}}(v | x_{<t}) \geq \alpha \cdot \max_{v'} P_{\text{expert}}(v' | x_{<t})\}$ is an adaptive plausibility constraint.

对比解码~\cite{li2023contrastive} 利用强模型（专家）与弱模型（业余者）之间的差异来放大专家的独特知识：
\[
x_t = \arg\max_{v \in \mathcal{V}(x_{<t})} \left[ \log P_{\text{expert}}(v | x_{<t}) - \log P_{\text{amateur}}(v | x_{<t}) \right]
\]
其中 $\mathcal{V}(x_{<t}) = \{v : P_{\text{expert}}(v | x_{<t}) \geq \alpha \cdot \max_{v'} P_{\text{expert}}(v' | x_{<t})\}$ 是一个自适应合理性约束。

\textbf{Intuition:} The amateur model captures generic, obvious patterns (common words, repetition). Subtracting its log-probabilities removes this ``generic signal,'' leaving the expert’s distinctive knowledge and reasoning. Like removing background noise from a recording to hear the signal.

\textbf{直觉：} 业余者模型捕捉通用、明显的模式（常见词、重复）。减去其对数概率可去除这种“通用信号”，留下专家的独特知识和推理。就像从录音中去除背景噪声以听到信号。

\textbf{Pros:} Reduces repetition and generic phrasing; improves factuality and coherence without additional training; works with any model pair.\\

\textbf{优点：} 减少重复和通用措辞；无需额外训练即可提高事实性和连贯性；适用于任何模型对。\\

\textbf{Cons:} Requires running two models (2$\times$ compute); sensitive to amateur model choice; the plausibility threshold $\alpha$ needs tuning.

\textbf{缺点：} 需要运行两个模型（2倍计算）；对业余者模型选择敏感；合理性阈值 $\alpha$ 需要调优。

\subsection{Repetition Penalties}
\subsection{重复惩罚}
\label{repetition-penalties}

Orthogonal to the sampling strategy, repetition penalties discourage the model from repeating tokens. Given the raw logit $z_v$ for token $v$ (i.e., the unnormalized score output by the LM head \emph{before} softmax), the penalized logit is: 
\[
z_v' = \begin{cases}
    z_v / \theta & \text{if } v \in \text{generated tokens and } z_v > 0 \\
    z_v \cdot \theta & \text{if } v \in \text{generated tokens and } z_v < 0
  \end{cases}
\]
 where $\theta > 1$ is the penalty factor (typically 1.1--1.3). In both cases, the effect is to push the logit toward zero---reducing the probability of previously generated tokens. Frequency and presence penalties are simpler additive variants used by OpenAI APIs: 
\[
z_v' = z_v - \alpha \cdot \text{count}(v) - \beta \cdot \mathbf{1}[v \in \text{generated}]
\]
 where $\alpha$ is the frequency penalty (proportional to how many times $v$ appeared) and $\beta$ is the presence penalty (flat penalty for any prior occurrence).

与采样策略正交，重复惩罚阻止模型重复词元。给定词元 $v$ 的原始 logit $z_v$（即语言模型头部在 softmax \emph{之前}输出的未归一化分数），惩罚后的 logit 为：
\[
z_v' = \begin{cases}
    z_v / \theta & \text{if } v \in \text{generated tokens and } z_v > 0 \\
    z_v \cdot \theta & \text{if } v \in \text{generated tokens and } z_v < 0
  \end{cases}
\]
其中 $\theta > 1$ 是惩罚系数（通常为 1.1--1.3）。两种情况下，效果都是将 logit 推向零——降低先前生成词元的概率。频率惩罚和存在惩罚是 OpenAI API 使用的更简单的加法变体：
\[
z_v' = z_v - \alpha \cdot \text{count}(v) - \beta \cdot \mathbf{1}[v \in \text{generated}]
\]
其中 $\alpha$ 是频率惩罚（与 $v$ 出现的次数成正比），$\beta$ 是存在惩罚（对任何先前出现施加固定惩罚）。

\subsection{Practical Comparison}
\subsection{实际比较}
\label{practical-comparison}

\begin{table}[ht!]
\centering
\caption{Decoding method comparison for LLM text generation.}
\caption{LLM文本生成的解码方法比较。}
\begin{tabular}{@{}lp{2.5cm}p{2.8cm}p{2.8cm}p{2.8cm}@{}}
\toprule
\textbf{Method} & \textbf{Deterministic} & \textbf{Diversity} & \textbf{Quality} & \textbf{Best For} \\
\midrule
Greedy & Yes & None & Medium & Code, factual QA \\
Beam Search ($B$=4--8) & Yes & Low & High (narrow) & Translation, summarization \\
Diverse Beam Search & Yes & Medium & High & Candidate generation for reranking \\
Top-$k$ ($k$=50) & No & Medium & Medium & General-purpose generation \\
Top-$p$ ($p$=0.9) & No & Adaptive & High & Default for open-ended tasks \\
Min-$p$ ($p_{\min}$=0.1) & No & Adaptive & High & Robust alternative to top-$p$ \\
Contrastive & Yes & Low & Very High & Factual, coherent long-form \\
\bottomrule
\end{tabular}
\begin{tabular}{@{}lp{2.5cm}p{2.8cm}p{2.8cm}p{2.8cm}@{}}
\toprule
\textbf{方法} & \textbf{确定性} & \textbf{多样性} & \textbf{质量} & \textbf{最佳用途} \\
\midrule
贪心 & 是 & 无 & 中等 & 代码、事实性问答 \\
束搜索（$B$=4--8） & 是 & 低 & 高（狭窄） & 翻译、摘要 \\
多样化束搜索 & 是 & 中等 & 高 & 用于重排的候选生成 \\
Top-$k$（$k$=50） & 否 & 中等 & 中等 & 通用生成 \\
Top-$p$（$p$=0.9） & 否 & 自适应 & 高 & 开放式任务的默认选择 \\
Min-$p$（$p_{\min}$=0.1） & 否 & 自适应 & 高 & top-$p$ 的稳健替代 \\
对比解码 & 是 & 低 & 非常高 & 事实性、连贯的长文本 \\
\bottomrule
\end{tabular}
\end{table}

\begin{examplebox}[Decoding in Practice: ``Once upon a time'']
Given the prompt ``Once upon a time,'':

\begin{examplebox}[解码实践：“Once upon a time”]
给定提示“Once upon a time,”：

\begin{itemize}
  \item \textbf{Greedy}: ``there was a young girl who lived in a small village...'' (generic fairy tale)
  \item \textbf{Top-$p$=0.9, $T$=1.0}: ``the rivers ran backwards and the fish learned to fly...'' (creative, surprising)
  \item \textbf{Top-$p$=0.9, $T$=0.3}: ``there was a kingdom ruled by a wise and just king...'' (coherent, conventional)
  \item \textbf{Contrastive}: ``in the amber-lit corridors of a collapsing star, two minds argued about the nature of time...'' (distinctive, avoids clichés)
\end{itemize}

\begin{itemize}
  \item \textbf{贪心}：“there was a young girl who lived in a small village...” （通用童话）
  \item \textbf{Top-$p$=0.9, $T$=1.0}：“the rivers ran backwards and the fish learned to fly...” （创意、出人意料）
  \item \textbf{Top-$p$=0.9, $T$=0.3}：“there was a kingdom ruled by a wise and just king...” （连贯、传统）
  \item \textbf{对比解码}：“in the amber-lit corridors of a collapsing star, two minds argued about the nature of time...” （独特、避免陈词滥调）
\end{itemize}

Same model, same prompt --- decoding strategy determines the character of the output.
\end{examplebox}

相同模型、相同提示——解码策略决定了输出的特征。
\end{examplebox}

\subsection{Constrained Decoding (Structured Generation)}
\subsection{约束解码（结构化生成）}
\label{sec:constrained-decoding}

All methods above sample from the \emph{full} vocabulary at each step. \textbf{Constrained decoding} restricts the set of allowed tokens so that the output is \emph{guaranteed} to conform to a formal grammar---typically a JSON schema, regex, or context-free grammar (CFG).

上述所有方法都在每一步从*完整*词表中采样。**约束解码**限制允许的词元集合，使得输出*保证*符合某种形式文法——通常是 JSON 模式、正则表达式或上下文无关文法（CFG）。

\paragraph{Core mechanism.}
\paragraph{核心机制}
\label{core-mechanism.}

\label{core-mechanism.}

## Section Title
## 章节标题

At each decoding step $t$, a \textbf{token mask} $M_t \subseteq \mathcal{V}$ is computed from the current parser state. Only tokens in $M_t$ receive their original logits; all others are set to $-\infty$ before softmax: 
\[
P'(v | x_{<t}) = \begin{cases}
    P(v | x_{<t}) / Z & \text{if } v \in M_t \\
    0 & \text{otherwise}
  \end{cases}
\]
 where $Z = \sum_{v \in M_t} P(v | x_{<t})$ renormalizes. Because the mask changes every step (it depends on what has been generated so far), the constraint is enforced \emph{incrementally}---the model cannot produce an invalid prefix at any point.

在每个解码步骤 $t$ 中，从当前解析器状态计算出一个 \textbf{令牌掩码 (token mask)} $M_t \subseteq \mathcal{V}$。只有 $M_t$ 中的令牌保留其原始 logits；其他所有令牌在 softmax 之前被设置为 $-\infty$：
\[
P'(v | x_{<t}) = \begin{cases}
    P(v | x_{<t}) / Z & \text{如果 } v \in M_t \\
    0 & \text{否则}
  \end{cases}
\]
其中 $Z = \sum_{v \in M_t} P(v | x_{<t})$ 进行重新归一化。由于掩码每步都在变化（取决于目前已生成的内容），约束是以 \emph{增量} 方式实现的——模型在任何时刻都不能产生无效前缀。

\paragraph{From schema to mask.}
\label{from-schema-to-mask.}

\paragraph{从模式到掩码。}
\label{from-schema-to-mask.}

The compilation pipeline is: 
\[
\text{JSON Schema} \;\xrightarrow{\text{compile}}\; \text{Regex}
  \;\xrightarrow{\text{compile}}\; \text{FSM (DFA)}
  \;\xrightarrow{\text{index}}\; \text{Token Mask per State}
\]
 The FSM states correspond to positions in the regex. For each state, all vocabulary tokens that would keep the string in the language are precomputed into an index (a one-time cost per schema). At runtime, looking up the mask is an $O(1)$ table access---adding negligible latency to each decoding step.

编译流水线如下：
\[
\text{JSON Schema} \;\xrightarrow{\text{编译}}\; \text{Regex}
  \;\xrightarrow{\text{编译}}\; \text{FSM (DFA)}
  \;\xrightarrow{\text{索引}}\; \text{每个状态的 Token Mask}
\]
FSM 的状态对应正则表达式中的位置。对于每个状态，所有能够使字符串保持在语言中的词汇令牌被预先计算并存入一个索引（每个模式的一次性成本）。在运行时，查找掩码是一个 $O(1)$ 的表访问——为每个解码步骤增加可忽略的延迟。

\paragraph{Key libraries.}
\label{key-libraries.}

\paragraph{关键库。}
\label{key-libraries.}

\begin{itemize}
  \item \textbf{Outlines}~\cite{willard2023outlines}: Compiles JSON schemas and regexes into interleaved FSM-guided generation. Supports any model with a logits interface.
  \item \textbf{Outlines}~\cite{willard2023outlines}：将 JSON 模式和正则表达式编译成交错的 FSM 引导生成。支持任何具有 logits 接口的模型。
  \item \textbf{lm-format-enforcer}\footnote{\url{https://github.com/noamgat/lm-format-enforcer}}: Similar FSM approach with a focus on integration with serving frameworks (vLLM, TGI).
  \item \textbf{lm-format-enforcer}\footnote{\url{https://github.com/noamgat/lm-format-enforcer}}：类似的 FSM 方法，专注于与推理框架（vLLM、TGI）的集成。
  \item \textbf{Guidance}\footnote{\url{https://github.com/guidance-ai/guidance}} (Microsoft): Interleaves constrained generation with control flow (loops, conditions), enabling complex structured outputs beyond flat schemas.
  \item \textbf{Guidance}\footnote{\url{https://github.com/guidance-ai/guidance}}（微软）：将约束生成与控制流（循环、条件）交错结合，支持超越平面模式的复杂结构化输出。
  \item \textbf{XGrammar}~\cite{dong2024xgrammar}: Pushdown-automaton-based engine supporting full context-free grammars (not just regular languages), used in MLC-LLM and vLLM for grammar-mode decoding.
  \item \textbf{XGrammar}~\cite{dong2024xgrammar}：基于下推自动机的引擎，支持完整的上下文无关文法（不仅仅是正则语言），用于 MLC-LLM 和 vLLM 中的文法模式解码。
\end{itemize}

\paragraph{Trade-offs.}
\label{trade-offs.}

\paragraph{权衡。}
\label{trade-offs.}

Constrained decoding \emph{guarantees} syntactic validity---no post-hoc parsing failures, no retries. However:

约束解码 \emph{保证}句法有效性——没有事后解析失败，无需重试。然而：

\begin{itemize}
  \item \textbf{Semantic quality}: Forcing structure can degrade content quality if the model’s probability mass for the ``correct'' answer lies outside the grammar. In practice this is rare for well-trained models on well-designed schemas.
  \item \textbf{语义质量}：如果模型对“正确”答案的概率质量位于文法之外，强制结构可能会降低内容质量。在实践中，对于训练良好的模型和设计良好的模式，这种情况很少见。
  \item \textbf{Compilation cost}: The FSM index must be built per schema. For complex schemas this can take 1--5 s, but it is amortized over all requests using that schema.
  \item \textbf{编译成本}：必须为每个模式构建 FSM 索引。对于复杂模式，这可能需要 1-5 秒，但该成本会分摊到使用该模式的所有请求中。
  \item \textbf{Grammar coverage}: Regex/FSM handles JSON, YAML, SQL fragments, and most structured formats. Full CFGs (via XGrammar or LALR parsers) cover languages like Python or XML.
  \item \textbf{文法覆盖范围}：正则表达式/FSM 处理 JSON、YAML、SQL 片段以及大多数结构化格式。完整的 CFG（通过 XGrammar 或 LALR 解析器）覆盖 Python 或 XML 等语言。
\end{itemize}

\begin{keybox}[When to Use Constrained Decoding]
Use constrained decoding whenever the consumer of the model’s output is a program rather than a human. Tool-calling agents, API backends, and data-extraction pipelines all benefit from \emph{guaranteed} valid structure. For free-form prose or creative text, unconstrained sampling remains appropriate.
\end{keybox}

\begin{keybox}[何时使用约束解码]
每当模型输出的使用者是程序而非人类时，请使用约束解码。工具调用智能体、API 后端和数据提取流水线都能从 \emph{保证}有效的结构中受益。对于自由形式的散文或创意文本，无约束采样仍然适用。
\end{keybox}

\section{Prompt Engineering}
\label{sec:prompt-engineering}

\section{提示工程 (Prompt Engineering)}
\label{sec:prompt-engineering}

Prompt engineering is the discipline of designing inputs to LLMs that reliably elicit desired behaviour---without changing model weights. While fine-tuning modifies the model, prompt engineering exploits the model’s \emph{existing} capabilities through careful framing, examples, and structure. It is the fastest, cheapest, and most accessible lever for improving LLM outputs, and remains essential even when using fine-tuned models.

提示工程是一门设计 LLM 输入以可靠地引发所需行为（无需改变模型权重）的学科。微调修改模型，而提示工程则通过精心设计的框架、示例和结构来利用模型的 \emph{现有}能力。它是改进 LLM 输出最快、最便宜且最易获取的杠杆，即使在使用微调模型时也仍然必不可少。

\subsection{In-Context Learning (ICL)}
\label{in-context-learning-icl}

\subsection{上下文学习 (In-Context Learning, ICL)}
\label{in-context-learning-icl}

In-context learning~\cite{brown2020language} is the remarkable ability of large language models to learn tasks at inference time purely from examples provided in the prompt---with no gradient updates. The model implicitly infers the task from the pattern of input--output pairs and generalizes to new inputs.

上下文学习~\cite{brown2020language} 是大型语言模型在推理时仅通过提示中提供的示例来学习任务的卓越能力——无需梯度更新。模型从输入-输出对的模式中隐式推断任务，并泛化到新输入。

\begin{keybox}[Why In-Context Learning Works]
\begin{itemize}
  \item \textbf{Implicit Bayesian inference}: The model has seen millions of tasks during pretraining. The prompt examples \emph{locate} the relevant task in the model’s learned distribution~\cite{xie2022explanation}.
  \item \textbf{Induction heads}: Specific attention heads learn to copy patterns (``A is to B as C is to ''), enabling in-context generalization~\cite{olsson2022context}.
  \item \textbf{Task vectors}: ICL creates implicit task representations in the residual stream that steer generation toward the demonstrated format and content~\cite{todd2024function}.
\end{itemize}
\end{keybox}

\begin{keybox}[上下文学习为何有效]
\begin{itemize}
  \item \textbf{隐式贝叶斯推理}：模型在预训练期间见过数百万个任务。提示中的示例 \emph{定位}了模型学习到的分布中的相关任务~\cite{xie2022explanation}。
  \item \textbf{归纳头 (Induction heads)}：特定的注意力头学习复制模式（“A 之于 B 如同 C 之于 ”），从而实现上下文泛化~\cite{olsson2022context}。
  \item \textbf{任务向量 (Task vectors)}：ICL 在残差流中创建隐式任务表示，引导生成朝向演示的格式和内容~\cite{todd2024function}。
\end{itemize}
\end{keybox}

\paragraph{Scaling behaviour.}
\label{scaling-behaviour.}

\paragraph{缩放行为。}
\label{scaling-behaviour.}

ICL emerges primarily in models above $\sim$1B parameters and improves log-linearly with model scale~\cite{brown2020language}. Smaller models can memorize examples but struggle to generalize to novel inputs within the same context window.

ICL 主要出现在参数超过 $\sim$10 亿的模型中，并随着模型规模的增大呈对数线性改善~\cite{brown2020language}。较小的模型可以记住示例，但难以在相同上下文窗口内泛化到新输入。

\subsection{Zero-Shot Prompting}
\label{zero-shot-prompting}

\subsection{零样本提示 (Zero-Shot Prompting)}
\label{zero-shot-prompting}

Zero-shot prompting provides \emph{no} examples---only a task description or instruction. The model must rely entirely on its pretrained knowledge and instruction-tuning to produce the correct format and content.

零样本提示不提供 \emph{任何}示例——仅提供任务描述或指令。模型必须完全依赖其预训练知识和指令微调来生成正确的格式和内容。

\begin{examplebox}[Zero-Shot Classification]
\begin{lstlisting}
Classify the following movie review as POSITIVE or NEGATIVE.


Review: "The cinematography was breathtaking but the plot 
felt rushed and predictable."


Sentiment:
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[零样本分类]
\begin{lstlisting}
将以下电影评论分类为 POSITIVE 或 NEGATIVE。


评论："The cinematography was breathtaking but the plot 
felt rushed and predictable."


情感：
\end{lstlisting}
\end{examplebox}

\paragraph{When zero-shot works well:}
\label{when-zero-shot-works-well}

\paragraph{零样本何时表现良好：}
\label{when-zero-shot-works-well}

\begin{itemize}
  \item Tasks the model has seen extensively during pretraining/SFT (translation, summarization, sentiment)
  \item Well-specified instructions with unambiguous output format
  \item Instruction-tuned models (e.g., ChatGPT, Claude, Llama-3-Instruct) significantly outperform base models at zero-shot tasks~\cite{ouyang2022training}
\end{itemize}

\begin{itemize}
  \item 模型在预训练/SFT 期间广泛见过的任务（翻译、摘要、情感分析）
  \item 指定明确、输出格式无歧义的指令
  \item 指令微调模型（例如 ChatGPT、Claude、Llama-3-Instruct）在零样本任务上显著优于基础模型~\cite{ouyang2022training}
\end{itemize}

\paragraph{When zero-shot fails:}
\label{when-zero-shot-fails}

\paragraph{零样本何时失败：}
\label{when-zero-shot-fails}

Novel formats, domain-specific labeling schemes, or ambiguous tasks where the model cannot infer your exact requirements from the instruction alone.

新奇的格式、特定领域的标注方案，或任务模糊时，模型无法仅从指令中推断出你的确切要求。

\subsection{Few-Shot Prompting}
\label{few-shot-prompting}

\subsection{少样本提示 (Few-Shot Prompting)}
\label{few-shot-prompting}

Few-shot prompting~\cite{brown2020language} provides $k$ input--output examples (``shots'') before the actual query. This is the most common form of in-context learning and remains one of the most effective prompting strategies.

少样本提示~\cite{brown2020language} 在实际查询之前提供 $k$ 个输入-输出示例（“样本”）。这是上下文学习最常见的形式，并且仍然是最有效的提示策略之一。

\begin{examplebox}[Few-Shot Named Entity Recognition]
\begin{lstlisting}
Extract named entities from the text. Format: [ENTITY](TYPE)


Text: "Apple released the iPhone 15 in Cupertino."
Entities: [Apple](ORG), [iPhone 15](PRODUCT), [Cupertino](LOC)


Text: "Elon Musk announced Tesla's new factory in Berlin."
Entities: [Elon Musk](PER), [Tesla](ORG), [Berlin](LOC)


Text: "OpenAI partnered with Microsoft to deploy GPT-4."
Entities:
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[少样本命名实体识别]
\begin{lstlisting}
从文本中提取命名实体。格式：[实体](类型)


文本："Apple released the iPhone 15 in Cupertino."
实体：[Apple](ORG), [iPhone 15](PRODUCT), [Cupertino](LOC)


文本："Elon Musk announced Tesla's new factory in Berlin."
实体：[Elon Musk](PER), [Tesla](ORG), [Berlin](LOC)


文本："OpenAI partnered with Microsoft to deploy GPT-4."
实体：
\end{lstlisting}
\end{examplebox}

\paragraph{Key design principles for few-shot examples:}
\label{key-design-principles-for-few-shot-examples}

\paragraph{少样本示例的关键设计原则：}
\label{key-design-principles-for-few-shot-examples}

\begin{enumerate}
  \item \textbf{Diversity}: Cover the range of expected inputs (different lengths, edge cases, categories).
  \item \textbf{Ordering}: Place harder or more representative examples last (recency bias)~\cite{lu2022fantastically}.
  \item \textbf{Label balance}: If classifying, include examples from all classes to avoid majority-class bias.
  \item \textbf{Format consistency}: Every example must follow the \emph{exact} same structure. The model mimics the pattern.
  \item \textbf{Relevance}: Use examples semantically similar to the target query for best results~\cite{liu2022makes}.
\end{enumerate}

\begin{enumerate}
  \item \textbf{多样性}：覆盖预期输入的范围（不同长度、边缘情况、类别）。
  \item \textbf{排序}：将较难或更具代表性的示例放在最后（近因偏差）~\cite{lu2022fantastically}。
  \item \textbf{标签平衡}：如果进行分类，请包含所有类别的示例，以避免多数类偏见。
  \item \textbf{格式一致性}：每个示例必须遵循 \emph{完全}相同的结构。模型会模仿该模式。
  \item \textbf{相关性}：使用与目标查询语义相似的示例以获得最佳结果~\cite{liu2022makes}。
\end{enumerate}

\paragraph{How many shots?}
\label{how-many-shots}

\paragraph{使用多少个样本？}
\label{how-many-shots}

## How LLMs Work: An Intuitive Overview
## 大型语言模型的工作原理：直观概述

Performance typically improves from 0 to 4--8 examples, then plateaus. Beyond $\sim$20 examples, gains are marginal and you risk filling the context window. Min et al.~\cite{min2022rethinking} showed that the \emph{format} and \emph{label space} of examples matter more than label correctness---even random labels help (though correct labels help more).
性能通常从0个示例增加到4--8个示例时提升，之后趋于平稳。超过$\sim$20个示例后，收益微乎其微，且可能填满上下文窗口。Min等人~\cite{min2022rethinking} 表明，示例的\emph{格式}和\emph{标签空间}比标签正确性更重要——即使是随机标签也有帮助（尽管正确标签效果更好）。

\subsection{Instruction-Following Prompts}
\subsection{指令遵循提示（Instruction-Following Prompts）}
\label{instruction-following-prompts}
\label{instruction-following-prompts}

Instruction-tuned models respond best to clear, structured instructions. The key insight: treat the prompt as a \emph{specification}, not a suggestion.
经过指令微调的模型对清晰、结构化的指令响应最佳。关键要点：将提示视为\emph{规范}（specification），而非建议。

\begin{keybox}[Anatomy of an Effective Instruction Prompt]
\begin{keybox}[有效指令提示的构成要素]
\begin{enumerate}
  \item \textbf{Role/Persona}: Define who the model is (``You are a senior data scientist...'')
  \item \textbf{Task}: What to do, stated clearly and unambiguously
  \item \textbf{Context}: Background information the model needs
  \item \textbf{Constraints}: Length limits, tone, what to avoid, output format
  \item \textbf{Examples} (optional): Show the desired output format
  \item \textbf{Input}: The actual data to process
\end{enumerate}
\begin{enumerate}
  \item \textbf{角色/身份（Role/Persona）}：定义模型的身份（“你是一名资深数据科学家……”）
  \item \textbf{任务（Task）}：清晰明确地说明要做什么
  \item \textbf{上下文（Context）}：模型所需的背景信息
  \item \textbf{约束条件（Constraints）}：长度限制、语气、应避免的内容、输出格式
  \item \textbf{示例（Examples）}（可选）：展示期望的输出格式
  \item \textbf{输入（Input）}：待处理的实际数据
\end{enumerate}
\end{keybox}

\begin{examplebox}[Instruction Prompt with Constraints]
\begin{examplebox}[带约束条件的指令提示]
\begin{lstlisting}
Role: You are a medical literature reviewer.
角色：你是一名医学文献审阅者。

Task: Summarize the following research abstract for a 
general audience.
任务：为普通读者总结以下研究摘要。

Constraints:
- Maximum 3 sentences
- No jargon (explain any technical terms)
- Include the key finding and its clinical implication
- Do NOT speculate beyond what the abstract states
约束条件：
- 最多3句话
- 不使用专业术语（如有技术术语需解释）
- 包含关键发现及其临床意义
- 不要超出摘要内容进行推测

Abstract: [...]
摘要：[...]
\end{lstlisting}
\end{examplebox}

\paragraph{System prompts vs.~user prompts.}
\paragraph{系统提示（System prompts） vs. 用户提示（user prompts）}
\label{system-prompts-vs.-user-prompts.}
\label{system-prompts-vs.-user-prompts.}

Modern chat APIs separate the \emph{system} prompt (persistent instructions, role definition) from the \emph{user} message (per-turn input). System prompts are processed with higher attention priority in most models and provide a natural place for role definitions, constraints, and output format specifications~\cite{openai2023gpt4}.
现代聊天API将\emph{系统}提示（system prompt，持久的指令、角色定义）与\emph{用户}消息（user message，每轮输入）分开。在大多数模型中，系统提示以更高的注意力优先级处理，为角色定义、约束条件和输出格式规范提供了自然的位置~\cite{openai2023gpt4}。

\subsection{Structured Output Prompts (JSON/XML)}
\subsection{结构化输出提示（Structured Output Prompts，JSON/XML）}
\label{structured-output-prompts-jsonxml}
\label{structured-output-prompts-jsonxml}

For programmatic use, the most critical prompting technique is enforcing structured output---particularly JSON.
对于程序化使用，最关键提示技术是强制结构化输出——尤其是JSON。

\begin{examplebox}[JSON Output Prompt]
\begin{examplebox}[JSON输出提示]
\begin{lstlisting}
Extract the following information from the customer email.
Respond ONLY with valid JSON, no other text.
从客户邮件中提取以下信息。仅以有效JSON格式回复，不附带其他文本。

Schema:
{
  "intent": "refund|complaint|question|praise",
  "urgency": "low|medium|high",
  "product_mentioned": "string or null",
  "summary": "one sentence summary"
}
模式：
{
  "intent": "refund|complaint|question|praise",
  "urgency": "low|medium|high",
  "product_mentioned": "string or null",
  "summary": "one sentence summary"
}

Email: [...]
邮件：[...]
\end{lstlisting}
\end{examplebox}

\paragraph{Techniques for reliable structured output:}
\paragraph{实现可靠结构化输出的技术：}
\label{techniques-for-reliable-structured-output}
\label{techniques-for-reliable-structured-output}

\begin{itemize}
  \item \textbf{Schema-first}: Show the exact JSON schema \emph{before} the input. The model treats it as a template.
  \item \textbf{Constrained decoding}: Use grammar-based sampling (e.g., Outlines~\cite{willard2023outlines}, Guidance) to guarantee syntactically valid JSON at the token level.
  \item \textbf{XML tags}: For nested or multi-part outputs, XML tags (e.g., \texttt{<thinking>...</thinking>}) provide unambiguous delimiters that models follow reliably.
  \item \textbf{Pydantic/TypeScript types}: Providing type definitions helps models understand field constraints (OpenAI’s function calling uses JSON Schema internally).
\end{itemize}
\begin{itemize}
  \item \textbf{模式优先（Schema-first）}：在输入\emph{之前}展示精确的JSON模式。模型将其视为模板。
  \item \textbf{约束解码（Constrained decoding）}：使用基于语法的采样（例如Outlines~\cite{willard2023outlines}、Guidance）来保证在token级别生成语法有效的JSON。
  \item \textbf{XML标签（XML tags）}：对于嵌套或多部分输出，XML标签（例如\texttt{<thinking>...</thinking>}）提供了模型能可靠遵循的无歧义分隔符。
  \item \textbf{Pydantic/TypeScript类型（Pydantic/TypeScript types）}：提供类型定义有助于模型理解字段约束（OpenAI的函数调用内部使用JSON Schema）。
\end{itemize}

\begin{warningbox}[JSON in Prompts — Common Pitfalls]
\begin{warningbox}[提示中的JSON——常见陷阱]
\begin{itemize}
  \item Models may add markdown fences (\texttt{```json ... ```}) --- instruct explicitly to output raw JSON.
  \item Nested objects and arrays increase hallucination risk --- flatten schemas where possible.
  \item Enum fields (fixed choices) are much more reliable than free-text fields.
  \item Always validate outputs programmatically; no prompt guarantees 100\% compliance without constrained decoding.
\end{itemize}
\begin{itemize}
  \item 模型可能会添加markdown代码块标记（\texttt{```json ... ```}）——明确指示输出原始JSON。
  \item 嵌套对象和数组会增加幻觉风险——尽可能扁平化模式。
  \item 枚举字段（固定选项）比自由文本字段可靠得多。
  \item 始终以编程方式验证输出；没有约束解码时，任何提示都无法保证100%符合要求。
\end{itemize}
\end{warningbox}

\paragraph{JSON Prompting: Structuring the Input.}
\paragraph{JSON提示（JSON Prompting）：结构化输入}
\label{json-prompting-structuring-the-input.}
\label{json-prompting-structuring-the-input.}

A distinct but complementary technique is \emph{JSON prompting}---formatting the prompt \emph{itself} as JSON rather than natural language. This exploits the model’s extensive pre-training on structured data (APIs, configs, code) to improve instruction adherence, reduce ambiguity, and enable deterministic parsing of multi-field requests.
一种不同但互补的技术是\emph{JSON提示（JSON prompting）}——将提示\emph{本身}格式化为JSON而非自然语言。这利用了模型在结构化数据（API、配置文件、代码）上广泛预训练的经验，以提高指令遵循度、减少歧义，并实现对多字段请求的确定性解析。

\begin{examplebox}[JSON Prompting with System Prompt]
\begin{examplebox}[带系统提示的JSON提示]
\begin{lstlisting}
=== SYSTEM ===
You are a senior code reviewer. Analyze code for bugs, 
security issues, and style violations. Always respond 
in the JSON schema provided.
=== 系统 ===
你是一名资深代码审查员。分析代码中的错误、
安全问题和风格违规。始终以提供的JSON模式回复。

=== USER (JSON prompt) ===
{
  "task": "code_review",
  "language": "python",
  "severity_filter": "high",
  "code": "def login(user, pw):\n    query = ...",
  "output_schema": {
    "issues": [{
      "line": "int",
      "severity": "critical|high|medium|low",
      "category": "security|bug|style|performance",
      "description": "string",
      "fix": "string"
    }],
    "overall_risk": "critical|high|medium|low"
  }
}
=== 用户（JSON提示） ===
{
  "task": "code_review",
  "language": "python",
  "severity_filter": "high",
  "code": "def login(user, pw):\n    query = ...",
  "output_schema": {
    "issues": [{
      "line": "int",
      "severity": "critical|high|medium|low",
      "category": "security|bug|style|performance",
      "description": "string",
      "fix": "string"
    }],
    "overall_risk": "critical|high|medium|low"
  }
}
\end{lstlisting}

\textbf{Why JSON prompting works:}
\textbf{为什么JSON提示有效：}

\begin{itemize}
  \item \textbf{Unambiguous field boundaries}: No confusion about where one instruction ends and another begins.
  \item \textbf{Typed constraints}: Fields like \texttt{"severity\_filter": "high"} are clearer than ``only show high severity issues.''
  \item \textbf{Schema-as-contract}: Including \texttt{output\_schema} in the input mirrors API design patterns the model has seen extensively during pre-training.
  \item \textbf{System prompt still essential}: The system message provides \emph{role}, \emph{tone}, and \emph{behavioral constraints} that don’t fit naturally in a JSON payload.
\end{itemize}
\begin{itemize}
  \item \textbf{无歧义的字段边界}：不会混淆一条指令在哪里结束、另一条指令在哪里开始。
  \item \textbf{类型约束}：像\texttt{"severity\_filter": "high"}这样的字段比“仅显示高严重性问题”更清晰。
  \item \textbf{模式即契约（Schema-as-contract）}：在输入中包含\texttt{output\_schema}反映了模型在预训练期间广泛见过的API设计模式。
  \item \textbf{系统提示仍然必不可少}：系统消息提供了\emph{角色}、\emph{语气}和\emph{行为约束}，这些自然不适合放在JSON负载中。
\end{itemize}
\end{examplebox}

\subsection{Chain-of-Thought (CoT) Prompting}
\subsection{思维链提示（Chain-of-Thought, CoT Prompting）}
\label{chain-of-thought-cot-prompting}
\label{chain-of-thought-cot-prompting}

Chain-of-thought prompting~\cite{wei2022chain} asks the model to produce intermediate reasoning steps before giving a final answer. This simple technique dramatically improves performance on tasks requiring multi-step reasoning: arithmetic, logic, commonsense inference, and code generation.
思维链提示（Chain-of-thought prompting）~\cite{wei2022chain} 要求模型在给出最终答案之前产生中间推理步骤。这一简单技术显著提高了需要多步推理的任务（算术、逻辑、常识推理和代码生成）上的性能。

\paragraph{Why CoT works:}
\paragraph{为什么CoT有效：}
\label{why-cot-works}
\label{why-cot-works}

\begin{itemize}
  \item \textbf{Serializes computation}: Transformers have fixed depth but variable-length generation. CoT converts parallel (hard) problems into sequential (easy) steps, effectively increasing the model’s computational budget.
  \item \textbf{Reduces compounding errors}: Each step is a simpler sub-problem with lower per-step error rate.
  \item \textbf{Exposes intermediate state}: Makes reasoning auditable and debuggable.
\end{itemize}
\begin{itemize}
  \item \textbf{序列化计算（Serializes computation）}：Transformer具有固定深度但可变长度的生成能力。CoT将并行（困难）问题转化为顺序（简单）步骤，有效增加了模型的计算预算。
  \item \textbf{减少复合错误（Reduces compounding errors）}：每一步都是更简单的子问题，每步错误率更低。
  \item \textbf{暴露中间状态（Exposes intermediate state）}：使推理过程可审计、可调试。
\end{itemize}

\begin{keybox}[Chain-of-Thought Variants]
\begin{keybox}[思维链变体]
\small
\begin{tabular}{@{}ll@{}}
\toprule
\textbf{Method} & \textbf{Description} \\
\textbf{方法} & \textbf{描述} \\
\midrule
Zero-shot CoT~\cite{kojima2022large} & Append ``Let's think step by step'' to any prompt \\
零样本CoT~\cite{kojima2022large} & 在任何提示后附加“让我们一步步思考” \\
Few-shot CoT~\cite{wei2022chain} & Provide examples with explicit reasoning chains \\
少样本CoT~\cite{wei2022chain} & 提供带有显式推理链的示例 \\
Self-Consistency~\cite{wang2023selfconsistency} & Sample $N$ CoT paths; majority-vote the final answer \\
自一致性~\cite{wang2023selfconsistency} & 采样$N$条CoT路径；对最终答案进行多数投票 \\
Tree of Thoughts~\cite{yao2023tree} & Explore multiple reasoning branches with backtracking \\
思维树~\cite{yao2023tree} & 探索多个推理分支并支持回溯 \\
Plan-and-Solve~\cite{wang2023planandsolve} & First plan the steps; then execute each step \\
计划-求解~\cite{wang2023planandsolve} & 先规划步骤，然后执行每一步 \\
ReAct~\cite{yao2023react} & Interleave Reasoning and Acting (tool use) \\
ReAct~\cite{yao2023react} & 交错推理与行动（工具使用） \\
\bottomrule
\end{tabular}
\end{keybox}

\begin{examplebox}[Zero-Shot Chain-of-Thought]
\begin{examplebox}[零样本思维链示例]
\begin{lstlisting}
Q: A store has 45 apples. They sell 3/5 of them in the 
morning and 1/3 of the remaining in the afternoon. 
How many apples are left?
问：一家商店有45个苹果。上午售出3/5，下午售出剩余部分的1/3。还剩多少个苹果？

Let's think step by step.
让我们一步步思考。

A: Morning sales: 45 * 3/5 = 27 apples sold.
Remaining after morning: 45 - 27 = 18.
Afternoon sales: 18 * 1/3 = 6 apples sold.
Remaining: 18 - 6 = 12 apples.
答：上午售出：45 * 3/5 = 27个苹果。
上午剩余：45 - 27 = 18个。
下午售出：18 * 1/3 = 6个苹果。
剩余：18 - 6 = 12个苹果。
\end{lstlisting}
\end{examplebox}

\paragraph{Self-Consistency.}
\paragraph{自一致性（Self-Consistency）}
\label{self-consistency.}
\label{self-consistency.}

Wang et al.~\cite{wang2023selfconsistency} showed that sampling multiple chain-of-thought reasoning paths and taking a majority vote over final answers significantly outperforms single-path CoT. The intuition: correct reasoning paths tend to converge on the same answer, while errors are typically idiosyncratic. This trades compute (generating $N$ samples) for accuracy---practical when latency is less important than correctness.

Wang等人~\cite{wang2023selfconsistency} 表明，对多个思维链推理路径进行采样并对最终答案进行多数投票，其效果显著优于单路径CoT。直觉上：正确的推理路径往往收敛于同一个答案，而错误通常是独特的。这是用计算资源（生成 $N$ 个样本）来换取准确性——在延迟不如正确性重要时很实用。

\paragraph{When CoT hurts.}
\label{when-cot-hurts.}

\paragraph{CoT何时有害。}
\label{when-cot-hurts.}

CoT is not universally beneficial. For simple tasks (single-step classification, retrieval, formatting), CoT adds unnecessary tokens, increases latency, and can even introduce errors through overthinking. Use CoT selectively for tasks where you expect multi-step reasoning to be required.

CoT并非普遍有益。对于简单任务（单步分类、检索、格式化），CoT会增加不必要的令牌，增加延迟，甚至可能因过度思考而引入错误。请仅在预期需要多步骤推理的任务中有选择地使用CoT。

\subsection{Advanced Prompting Techniques}
\label{advanced-prompting-techniques}

\subsection{高级提示技巧}
\label{advanced-prompting-techniques}

\paragraph{Retrieval-Augmented Generation (RAG).}
\label{retrieval-augmented-generation-rag.}

\paragraph{检索增强生成（RAG）。}
\label{retrieval-augmented-generation-rag.}

Rather than relying solely on the model’s parametric memory, RAG~\cite{lewis2020retrieval} retrieves relevant documents and includes them in the prompt:

与其仅依赖模型的参数化记忆，RAG~\cite{lewis2020retrieval} 会检索相关文档并将其包含在提示中：

\begin{lstlisting}
Context (retrieved): [document chunks]
Question: [user query]
Answer based ONLY on the provided context.
\end{lstlisting}

\begin{lstlisting}
上下文（检索到的）：[文档片段]
问题：[用户查询]
仅基于提供的上下文进行回答。
\end{lstlisting}

This grounds the model’s responses in verifiable sources and dramatically reduces hallucinations for knowledge-intensive tasks.

这使模型的响应基于可验证的源，并显著减少知识密集型任务中的幻觉。

\paragraph{Prompt Chaining and Decomposition.}
\label{prompt-chaining-and-decomposition.}

\paragraph{提示链与分解。}
\label{prompt-chaining-and-decomposition.}

Complex tasks benefit from being broken into a pipeline of simpler prompts, where the output of one becomes the input to the next:

复杂任务可通过分解为一系列更简单的提示来获益，其中前一个提示的输出成为下一个提示的输入：

\begin{enumerate}
  \item \emph{Extract} key facts from document
  \item \emph{Reason} over extracted facts
  \item \emph{Format} final answer
\end{enumerate}

\begin{enumerate}
  \item 从文档中\emph{提取}关键事实
  \item 对提取的事实进行\emph{推理}
  \item \emph{格式化}最终答案
\end{enumerate}

Each step can use a different prompt template, model, or temperature setting. This is more controllable than a single monolithic prompt and enables targeted debugging.

每一步可以使用不同的提示模板、模型或温度设置。这比单个庞大的提示更具可控性，并支持有针对性的调试。

\paragraph{Constitutional AI / Self-Critique.}
\label{constitutional-ai-self-critique.}

\paragraph{宪法AI / 自我批评。}
\label{constitutional-ai-self-critique.}

Bai et al.~\cite{bai2022constitutional} introduce prompts that ask the model to critique and revise its own output against a set of principles:

Bai等人~\cite{bai2022constitutional} 引入了提示，要求模型根据一组原则对自己的输出进行批评和修改：

\begin{lstlisting}
[Generate initial response]
Critique: Does this response violate any of the following 
principles? [list principles]
Revision: Rewrite the response addressing the critique.
\end{lstlisting}

\begin{lstlisting}
[生成初始响应]
批评：此响应是否违反了以下任何原则？[列出原则]
修订：根据批评重写响应。
\end{lstlisting}

\paragraph{Meta-Prompting and Prompt Optimization.}
\label{meta-prompting-and-prompt-optimization.}

\paragraph{元提示与提示优化。}
\label{meta-prompting-and-prompt-optimization.}

Rather than hand-crafting prompts, recent work automates prompt design:

最近的工作不再手工制作提示，而是自动化提示设计：

\begin{itemize}
  \item \textbf{APE}~\cite{zhou2023large}: Uses an LLM to generate and score candidate prompts automatically.
  \item \textbf{DSPy}~\cite{khattab2023dspy}: Compiles declarative task descriptions into optimized prompt pipelines with learned few-shot examples.
  \item \textbf{OPRO}~\cite{yang2024large}: Treats prompt optimization as an optimization problem, using an LLM as the optimizer.
\end{itemize}

\begin{itemize}
  \item \textbf{APE}~\cite{zhou2023large}: 使用LLM自动生成和评分候选提示。
  \item \textbf{DSPy}~\cite{khattab2023dspy}: 将声明式任务描述编译为优化的提示流水线，并带有学到的少样本示例。
  \item \textbf{OPRO}~\cite{yang2024large}: 将提示优化视为一个优化问题，使用LLM作为优化器。
\end{itemize}

\paragraph{Attentive Reasoning Queries (ARQ).}
\label{attentive-reasoning-queries-arq.}

\paragraph{注意力推理查询（ARQ）。}
\label{attentive-reasoning-queries-arq.}

ARQ~\cite{yang2025arq} addresses a fundamental weakness of standard prompting: as context length grows, models increasingly ``lose'' critical information in the middle of the prompt (the \emph{lost-in-the-middle} effect). ARQ mitigates this by decomposing a complex query into multiple focused sub-queries, each designed to direct the model’s attention to a specific part of the context:

ARQ~\cite{yang2025arq} 解决了标准提示的一个根本弱点：随着上下文长度增长，模型会越来越“丢失”提示中间的关键信息（即\emph{中间丢失}效应）。ARQ通过将复杂查询分解为多个聚焦的子查询来缓解这一问题，每个子查询旨在将模型的注意力引导到上下文的特定部分：

\begin{enumerate}
  \item \textbf{Query decomposition}: Break the user question into atomic sub-questions that each target a narrow aspect.
  \item \textbf{Attentive retrieval}: For each sub-query, retrieve or highlight only the relevant context slice---forcing the model to attend to it.
  \item \textbf{Aggregation}: Combine sub-answers into a coherent final response.
\end{enumerate}

\begin{enumerate}
  \item \textbf{查询分解}：将用户问题分解为原子子问题，每个子问题针对一个狭窄方面。
  \item \textbf{注意力检索}：对于每个子查询，仅检索或高亮相关的上下文片段——迫使模型关注它。
  \item \textbf{聚合}：将子答案组合成连贯的最终响应。
\end{enumerate}

This is particularly effective for long-document QA, multi-hop reasoning over large retrieval sets, and agentic tasks where the context window contains many tool outputs. ARQ can be seen as a structured form of chain-of-thought that explicitly manages \emph{where} the model looks, not just \emph{how} it reasons.

这对于长文档问答、大型检索集上的多跳推理以及上下文窗口包含许多工具输出的智能体任务尤为有效。ARQ可以看作是一种结构化的思维链形式，它显式地管理模型\emph{看向何处}，而不仅仅是\emph{如何推理}。

\subsection{Best Practices: Crafting Effective Prompts}
\label{best-practices-crafting-effective-prompts}

\subsection{最佳实践：构建有效提示}
\label{best-practices-crafting-effective-prompts}

Based on empirical findings across the literature and practitioner experience, the following principles reliably improve prompt quality:

基于文献中的实证发现和实践者经验，以下原则能可靠地提高提示质量：

\begin{keybox}[The Prompt Engineering Checklist]
\begin{enumerate}
  \item \textbf{Be specific and unambiguous}: Replace ``summarize this'' with ``summarize in 2--3 bullet points, each under 20 words, focusing on actionable findings.''
  \item \textbf{Show, don’t tell}: One good example is worth 100 words of instruction. When in doubt, add a few-shot example.
  \item \textbf{Define the output format explicitly}: Specify JSON schema, bullet points, table format, or exact delimiters. Never leave format to interpretation.
  \item \textbf{Use delimiters for input data}: Wrap user inputs in clear delimiters (\texttt{"""}, \texttt{<input>...</input>}, \texttt{---}) to separate instructions from data.
  \item \textbf{Assign a role}: ``You are a [domain expert] who [specific behaviour]'' primes relevant knowledge and tone.
  \item \textbf{Specify what NOT to do}: Negative constraints (``do not explain your reasoning'', ``never output more than 5 items'') are often more effective than positive ones.
  \item \textbf{Add chain-of-thought for reasoning tasks}: Append ``Think step by step'' or provide worked examples for math, logic, or multi-hop questions.
  \item \textbf{Control temperature appropriately}: Use $T \approx 0$ for factual/deterministic tasks; $T \approx 0.7$--$1.0$ for creative/diverse outputs.
  \item \textbf{Iterate empirically}: Treat prompts as code---version them, A/B test them, and measure performance on representative eval sets.
  \item \textbf{Leverage recency bias}: Place the most critical instructions and examples at the \emph{end} of the prompt (closest to the generation point).
\end{enumerate}
\end{keybox}

\begin{keybox}[提示工程检查清单]
\begin{enumerate}
  \item \textbf{具体且无歧义}：将“总结这个”替换为“用2-3个要点总结，每点不超过20词，侧重于可操作的结果。”
  \item \textbf{展示，而非告知}：一个好的示例胜过100词的指令。如有疑问，添加少样本示例。
  \item \textbf{明确定义输出格式}：指定JSON模式、要点、表格格式或确切分隔符。切勿让模型自行解读格式。
  \item \textbf{为输入数据使用分隔符}：使用清晰的分隔符（\texttt{"""}, \texttt{<input>...</input>}, \texttt{---}）包裹用户输入，以区分指令和数据。
  \item \textbf{分配角色}：“你是一位[领域专家]，其[具体行为]”能够激发相关知识和语调。
  \item \textbf{指定不要做什么}：否定约束（“不要解释你的推理”，“最多输出5项”）通常比肯定约束更有效。
  \item \textbf{为推理任务添加思维链}：对于数学、逻辑或多跳问题，附加“逐步思考”或提供已完成的示例。
  \item \textbf{适当控制温度}：对于事实性/确定性任务使用 $T \approx 0$；对于创造性/多样性输出使用 $T \approx 0.7$--$1.0$。
  \item \textbf{经验性迭代}：将提示视为代码——进行版本控制、A/B测试，并在代表性评估集上衡量性能。
  \item \textbf{利用近因偏差}：将最关键指令和示例放在提示的\emph{末尾}（最接近生成点）。
\end{enumerate}
\end{keybox}

\begin{table}[ht!]
\centering
\caption{Common prompting failure modes and solutions.}
\begin{tabular}{@{}lp{5cm}p{6.5cm}@{}}
\toprule
\textbf{Failure Mode} & \textbf{Symptom} & \textbf{Solution} \\
\midrule
Instruction amnesia & Model ignores constraints in long prompts & Move constraints to end; repeat key rules; use system prompt \\
Format drift & Output starts correct but degrades over long generations & Use constrained decoding; break into shorter chained prompts \\
Sycophancy & Model agrees with incorrect premises in the prompt & Add ``challenge assumptions if incorrect''; use system-level instruction \\
Hallucinated details & Model invents facts not in provided context & Add ``if unknown, say I don’t know''; use RAG with source attribution \\
Refusal over-triggering & Model refuses benign requests due to safety training & Rephrase to clarify legitimate intent; provide explicit context for why the request is appropriate \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[ht!]
\centering
\caption{常见提示失败模式及解决方案。}
\begin{tabular}{@{}lp{5cm}p{6.5cm}@{}}
\toprule
\textbf{失败模式} & \textbf{症状} & \textbf{解决方案} \\
\midrule
指令遗忘 & 模型忽略长提示中的约束 & 将约束移至末尾；重复关键规则；使用系统提示 \\
格式漂移 & 输出开始时正确，但在长生成过程中退化 & 使用约束解码；拆分为更短的链式提示 \\
谄媚 & 模型同意提示中的错误前提 & 添加“如果错误则质疑假设”；使用系统级指令 \\
虚构细节 & 模型编造不在提供的上下文中的事实 & 添加“如果不知道，请说我不知道”；使用带来源归属的RAG \\
过度触发拒绝 & 模型因安全训练而拒绝良性请求 & 重新措辞以澄清合法意图；提供明确上下文说明请求为何适当 \\
\bottomrule
\end{tabular}
\end{table}

\begin{intuitionbox}[The Prompt Engineering Mindset]
Think of prompt engineering as \emph{programming in natural language}. The model is a powerful but literal interpreter---it will do exactly what you ask, interpreted in the most likely way given its training distribution. Common principles from software engineering apply:

\begin{itemize}
  \item \textbf{DRY (Don’t Repeat Yourself)}: Unless fighting attention decay in long contexts
  \item \textbf{Separation of concerns}: Different prompt sections for role, constraints, examples, and input
  \item \textbf{Test-driven development}: Define expected outputs before writing the prompt
  \item \textbf{Version control}: Track prompt iterations and their eval scores
  \item \textbf{Modularity}: Build reusable prompt templates; parameterize variable parts
\end{itemize}
\end{intuitionbox}

\begin{intuitionbox}[提示工程思维模式]
将提示工程视为\emph{用自然语言编程}。模型是一个强大但字面解释的执行者——它会严格按照你的要求去做，并根据其训练分布以最可能的方式解释你的指令。软件工程中的常见原则同样适用：

\begin{itemize}
  \item \textbf{DRY（不要重复自己）}：除非是为了对抗长上下文中的注意力衰减
  \item \textbf{关注点分离}：为角色、约束、示例和输入设置不同的提示部分
  \item \textbf{测试驱动开发}：在编写提示之前定义预期输出
  \item \textbf{版本控制}：追踪提示迭代及其评估分数
  \item \textbf{模块化}：构建可重用的提示模板；对可变部分进行参数化
\end{itemize}
\end{intuitionbox}

## Model Compression Methods
## 模型压缩方法

Model compression reduces model size and inference cost while preserving quality. Three main approaches: quantization (reduce precision), pruning (remove parameters), and distillation (train a smaller model to mimic a larger one).
模型压缩在保持质量的同时减小模型大小和推理成本。主要方法有三种：量化（降低精度）、剪枝（移除参数）和蒸馏（训练一个较小的模型来模仿较大的模型）。

### Quantization
### 量化

Quantization reduces model size and inference cost by representing weights (and optionally activations) in lower-precision formats. The core trade-off is compression ratio versus quality degradation.
量化通过以较低精度格式表示权重（以及可选的激活值）来减小模型大小和推理成本。核心权衡是压缩比与质量损失之间的关系。

\begin{keybox}[Quantization Overview]
Quantization reduces the numerical precision of model weights (and optionally activations) from FP32/BF16 to lower-bit formats: 
\[
x_q = \text{round}\!\left(\frac{x - z}{s}\right), \quad x_{\text{dequant}} = s \cdot x_q + z
\]
 where $s$ is the scale factor and $z$ is the zero-point.
\end{keybox}
\begin{keybox}[量化概览]
量化将模型权重（以及可选的激活值）的数值精度从 FP32/BF16 降低到更低比特格式：
\[
x_q = \text{round}\!\left(\frac{x - z}{s}\right), \quad x_{\text{dequant}} = s \cdot x_q + z
\]
其中 $s$ 是缩放因子，$z$ 是零点偏移。
\end{keybox}

\begin{table}[ht!]
\centering
\caption{Quantization methods for LLMs.}
\begin{tabular}{@{}llll@{}}
\toprule
\textbf{Method} & \textbf{Bits} & \textbf{Type} & \textbf{Key Idea} \\
\midrule
\textbf{GPTQ}~\cite{frantar2023gptq} & 4-bit & PTQ, weight-only & \parbox[t]{5.5cm}{Layer-wise quantization minimizing $\|WX - \hat{W}X\|^2$ via optimal brain surgeon.} \\[4pt]
\textbf{AWQ}~\cite{lin2024awq} & 4-bit & PTQ, weight-only & \parbox[t]{5.5cm}{Protects salient weights (those with large activations). 1\% of weights carry 99\% importance.} \\[4pt]
\textbf{GGUF}~\cite{gerganov2023gguf} & 2--8 bit & PTQ, weight-only & \parbox[t]{5.5cm}{CPU-optimized format (llama.cpp). Per-block quantization with multiple types.} \\[4pt]
\textbf{FP8} (E4M3) & 8-bit & Training + inference & \parbox[t]{5.5cm}{Native H100 support. 2$\times$ throughput vs BF16.} \\[4pt]
\textbf{SmoothQuant}~\cite{xiao2023smoothquant} & W8A8 & PTQ, weight+act. & \parbox[t]{5.5cm}{Smooths activation outliers into weights before quantization. Enables INT8 GEMM.} \\[4pt]
\textbf{QAT}~\cite{liu2023llmqat} & 4-bit & QAT & \parbox[t]{5.5cm}{Trains with simulated quantization. Highest quality but expensive.} \\[4pt]
\textbf{AQLM}~\cite{egiazarian2024aqlm} & 2-bit & PTQ, additive codes & \parbox[t]{5.5cm}{Extreme compression via learned additive quantization codebooks.} \\
\bottomrule
\end{tabular}
\end{table}
\begin{table}[ht!]
\centering
\caption{大语言模型的量化方法}
\begin{tabular}{@{}llll@{}}
\toprule
\textbf{方法} & \textbf{比特数} & \textbf{类型} & \textbf{核心思想} \\
\midrule
\textbf{GPTQ}~\cite{frantar2023gptq} & 4-bit & PTQ，仅权重 & \parbox[t]{5.5cm}{通过最优脑外科手术逐层量化，最小化 $\|WX - \hat{W}X\|^2$。} \\[4pt]
\textbf{AWQ}~\cite{lin2024awq} & 4-bit & PTQ，仅权重 & \parbox[t]{5.5cm}{保护显著权重（激活值较大的权重）。1\% 的权重承载了 99\% 的重要性。} \\[4pt]
\textbf{GGUF}~\cite{gerganov2023gguf} & 2--8 bit & PTQ，仅权重 & \parbox[t]{5.5cm}{CPU 优化格式 (llama.cpp)。按块量化，支持多种类型。} \\[4pt]
\textbf{FP8} (E4M3) & 8-bit & 训练+推理 & \parbox[t]{5.5cm}{原生 H100 支持。相比于 BF16 吞吐量提升 2 倍。} \\[4pt]
\textbf{SmoothQuant}~\cite{xiao2023smoothquant} & W8A8 & PTQ，权重+激活 & \parbox[t]{5.5cm}{在量化前将激活异常值平滑到权重中。支持 INT8 GEMM。} \\[4pt]
\textbf{QAT}~\cite{liu2023llmqat} & 4-bit & QAT & \parbox[t]{5.5cm}{使用模拟量化进行训练。质量最高但代价昂贵。} \\[4pt]
\textbf{AQLM}~\cite{egiazarian2024aqlm} & 2-bit & PTQ，加法编码 & \parbox[t]{5.5cm}{通过学习式加法量化码本实现极致压缩。} \\
\bottomrule
\end{tabular}
\end{table}

\begin{intuitionbox}[When to Quantize]
\begin{itemize}
  \item \textbf{Inference serving}: Always quantize. W4A16 (4-bit weights, BF16 activations) is the sweet spot --- 2$\times$ memory savings, $<$1\% quality loss for 70B+ models.
  \item \textbf{Training}: FP8 on H100 gives 2$\times$ throughput with minimal quality loss. BF16 is still the default for smaller models.
  \item \textbf{Edge deployment}: GGUF Q4\_K\_M for local inference on consumer hardware.
  \item \textbf{RLHF}: Quantize the frozen models (reference, reward model) to INT8/FP8. Keep the policy in BF16 for training precision.
\end{itemize}
\end{intuitionbox}
\begin{intuitionbox}[何时进行量化]
\begin{itemize}
  \item \textbf{推理服务}：始终进行量化。W4A16（4 比特权重，BF16 激活）是最佳点——节省 2 倍内存，对 70B+ 模型质量损失低于 1%。
  \item \textbf{训练}：在 H100 上使用 FP8 可获得 2 倍吞吐量，质量损失极小。对于较小模型，BF16 仍是默认选择。
  \item \textbf{边缘部署}：在消费级硬件上使用 GGUF Q4\_K\_M 进行本地推理。
  \item \textbf{RLHF}：将冻结模型（参考模型、奖励模型）量化为 INT8/FP8。策略模型保持 BF16 以保证训练精度。
\end{itemize}
\end{intuitionbox}

### Pruning
### 剪枝

\paragraph{Why Prune?}
\paragraph{为何要剪枝？}

Modern LLMs contain billions of parameters, yet empirical studies consistently show that a large fraction of these weights contribute minimally to model outputs. Pruning exploits this over-parameterization: by removing redundant weights, we reduce \textbf{memory footprint} (enabling deployment on smaller GPUs or edge devices), \textbf{inference latency} (fewer multiply-accumulate operations per forward pass), and \textbf{serving cost} (higher throughput per dollar). Unlike quantization, which reduces the precision of all weights uniformly, pruning selectively eliminates weights---enabling multiplicative savings when combined with quantization (e.g., a 50\% sparse, 4-bit model uses $4\times$ less memory than the dense BF16 baseline). The challenge is achieving high sparsity without degrading generation quality, which has driven the development of principled one-shot methods that require no retraining.
现代大语言模型包含数十亿参数，但实证研究一致表明，其中很大一部分权重对模型输出的贡献极小。剪枝利用了这种过参数化：通过移除冗余权重，我们减少了\textbf{内存占用}（使得能够在更小的 GPU 或边缘设备上部署）、\textbf{推理延迟}（每次前向传播的乘加运算更少）以及\textbf{服务成本}（每美元获得更高吞吐量）。与均匀降低所有权重精度的量化不同，剪枝选择性地消除权重——与量化结合时可实现成倍的节省（例如，一个 50% 稀疏度的 4 比特模型比密集的 BF16 基线节省 4 倍内存）。挑战在于实现高稀疏度而不损害生成质量，这推动了无需重新训练的原则性一次性方法的发展。

\begin{keybox}[Pruning Methods]
\begin{itemize}
  \item \textbf{Unstructured pruning}: Zero out individual weights below a threshold. High sparsity (50--90\%) possible. Requires sparse GEMM kernels (2:4 on A100/H100).
  \item \textbf{Structured pruning}: Remove entire attention heads, layers, or FFN neurons. Directly reduces FLOPS without specialized kernels.
  \item \textbf{SparseGPT}~\cite{frantar2023sparsegpt}: One-shot pruning using approximate inverse Hessian. 50\% unstructured sparsity with minimal quality loss on 175B models.
  \item \textbf{Wanda}~\cite{sun2024wanda}: Prune by $|w| \times \|x\|$ (weight magnitude times input activation norm). No calibration data needed. Competitive with SparseGPT.
\end{itemize}
\end{keybox}
\begin{keybox}[剪枝方法]
\begin{itemize}
  \item \textbf{非结构化剪枝}：将低于阈值的单个权重置零。可实现高稀疏度（50--90%）。需要稀疏 GEMM 内核（A100/H100 上的 2:4）。
  \item \textbf{结构化剪枝}：移除整个注意力头、层或 FFN 神经元。直接减少 FLOPS，无需专用内核。
  \item \textbf{SparseGPT}~\cite{frantar2023sparsegpt}：使用近似逆 Hessian 的一步式剪枝。在 175B 模型上实现 50% 非结构化稀疏度，质量损失极小。
  \item \textbf{Wanda}~\cite{sun2024wanda}：通过 $|w| \times \|x\|$（权重幅值乘以输入激活范数）进行剪枝。无需校准数据。与 SparseGPT 竞争力相当。
\end{itemize}
\end{keybox}

\begin{warningbox}[NVIDIA 2:4 Structured Sparsity]
A100/H100 Tensor Cores natively support 2:4 sparsity: out of every 4 elements, at most 2 are non-zero. This gives exactly 2$\times$ speedup on supported operations with hardware acceleration. The constraint: you must achieve \emph{exactly} 50\% sparsity in this specific pattern, which limits flexibility compared to arbitrary sparsity.
\end{warningbox}
\begin{warningbox}[NVIDIA 2:4 结构化稀疏度]
A100/H100 Tensor Cores 原生支持 2:4 稀疏度：每 4 个元素中最多有 2 个非零。这可以在硬件加速下为支持的操作提供恰好 2 倍的加速。约束条件：必须在此特定模式下实现\emph{恰好} 50% 的稀疏度，与任意稀疏度相比限制了灵活性。
\end{warningbox}

### Knowledge Distillation
### 知识蒸馏

Knowledge distillation~\cite{hinton2015distilling} transfers the learned behaviour of a large \emph{teacher} model into a smaller, cheaper \emph{student} model. The core idea is that the teacher’s output distribution over tokens carries far richer signal than ground-truth hard labels alone --- revealing inter-class similarities, calibration, and uncertainty that the student can exploit.
知识蒸馏~\cite{hinton2015distilling}将大型\emph{教师}模型学到的行为迁移到更小、更便宜的\emph{学生}模型中。核心思想是教师模型在 token 上的输出分布比单纯的硬标签蕴含更丰富的信号——揭示了类别间相似性、校准和不确定性，学生可以加以利用。

\paragraph{Temperature-Scaled Softmax.}
\paragraph{温度缩放 Softmax.}

To expose the ``dark knowledge'' in the teacher’s logits we soften the distribution with a temperature $T > 1$: 
\[
p_i^{(T)} = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}
\]
 At high temperature the probability mass spreads across more tokens, making near-miss alternatives visible. During training the same temperature is applied to the student; at inference the student uses $T=1$.
为了揭示教师 logits 中的“暗知识”，我们使用温度 $T > 1$ 来软化分布：
\[
p_i^{(T)} = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}
\]
在高温下，概率质量分散到更多 token 上，使接近正确的备选变得可见。训练时对学生应用相同的温度；推理时学生使用 $T=1$。

\paragraph{General Distillation Loss.}
\paragraph{通用蒸馏损失.}

\[
\mathcal{L}_{\text{distill}} = \alpha \, T^2 \cdot \text{KL}\!\bigl(P_{\text{teacher}}^{(T)} \;\|\; P_{\text{student}}^{(T)}\bigr) \;+\; (1-\alpha) \cdot \mathcal{L}_{\text{CE}}(y, P_{\text{student}}^{(1)})
\]
 The $T^2$ factor compensates for the reduced gradient magnitude of softened distributions. Typical values: $T \in [2, 20]$, $\alpha \in [0.5, 0.9]$ (more weight on KL when teacher quality is high).
\[
\mathcal{L}_{\text{distill}} = \alpha \, T^2 \cdot \text{KL}\!\bigl(P_{\text{teacher}}^{(T)} \;\|\; P_{\text{student}}^{(T)}\bigr) \;+\; (1-\alpha) \cdot \mathcal{L}_{\text{CE}}(y, P_{\text{student}}^{(1)})
\]
$T^2$ 因子用于补偿软化分布梯度幅值的减小。典型值：$T \in [2, 20]$，$\alpha \in [0.5, 0.9]$（当教师质量高时，KL 权重更大）。

\begin{table}[ht!]
\centering
\caption{Knowledge distillation paradigms for LLMs.}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{4cm}@{}}
\toprule
\textbf{Paradigm} & \textbf{Mechanism} & \textbf{Pros} & \textbf{Cons} \\
\midrule
\textbf{Offline / White-box} & Teacher logits pre-computed; student trains on full distributions & Full distribution signal; one-time teacher cost & Stale data; storage heavy \\
\textbf{Online / Co-training} & Teacher generates on-the-fly; student sees fresh logits & Adapts to student weaknesses & $2\times$ compute; complex infra \\
\textbf{Black-box (API)} & Only teacher \emph{text} outputs available (no logits) & Works with proprietary models & Loses dark knowledge; SFT-like \\
\textbf{Self-distillation} & Model distills into a smaller version of itself & No separate teacher needed & Teacher = student family; ceiling \\
\bottomrule
\end{tabular}
\end{table}
\begin{table}[ht!]
\centering
\caption{大语言模型的知识蒸馏范式}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{4cm}@{}}
\toprule
\textbf{范式} & \textbf{机制} & \textbf{优点} & \textbf{缺点} \\
\midrule
\textbf{离线/白盒} & 教师 logits 预计算；学生训练基于完整分布 & 完整分布信号；一次性教师成本 & 数据陈旧；存储量大 \\
\textbf{在线/协同训练} & 教师实时生成；学生看到最新 logits & 适应学生弱点 & 2 倍算力；基础设施复杂 \\
\textbf{黑盒（API）} & 仅教师\emph{文本}输出可用（无 logits） & 适用于专有模型 & 丢失暗知识；类似 SFT \\
\textbf{自蒸馏} & 模型蒸馏到自身的更小版本 & 无需独立教师 & 教师=学生家族；存在上限 \\
\bottomrule
\end{tabular}
\end{table}

\paragraph{Offline (White-Box) Distillation.}
\paragraph{离线（白盒）蒸馏.}

The teacher’s full logit vector (or top-$k$ logits for storage efficiency) is recorded for each training token. The student minimises the KL divergence against these stored distributions. This is the most data-efficient paradigm when teacher access is unrestricted.
每个训练 token 的教师完整 logit 向量（或为了存储效率保留 top-$k$ logits）被记录下来。学生最小化与这些存储分布的 KL 散度。当教师访问不受限时，这是数据效率最高的范式。

\textbf{Motivation:} Decouple teacher inference from student training --- run the teacher once on high-end hardware, then train many students cheaply.
\textbf{动机：} 将教师模型推理解耦与学生训练分离——在高端硬件上运行一次教师模型，然后低成本地训练多个学生模型。

\textbf{Pros:} Deterministic, reproducible; teacher cost is amortised; full distributional signal.\\
\textbf{优点：} 确定性、可复现；教师模型成本被摊销；获得完整的分布信息。

\textbf{Cons:} Requires storing $|V|$-dimensional vectors per token (mitigated by top-$k$ pruning); teacher cannot adapt to student failures.
\textbf{缺点：} 每个词元需要存储 $|V|$ 维向量（可通过 top-$k$ 剪枝缓解）；教师模型无法适应学生模型的失败。

\paragraph{Online (Co-Training) Distillation.}
\paragraph{在线（协同训练）蒸馏（Online (Co-Training) Distillation）。}
\label{online-co-training-distillation.}

Teacher and student are run jointly: the teacher generates logits for the student’s current training batch.
教师模型和学生模型联合运行：教师模型为学生模型当前的训练批次生成 logits。

\textbf{Motivation:} Let the teacher focus on inputs where the student currently struggles (curriculum-like).
\textbf{动机：} 让教师模型聚焦于学生模型当前困难的输入（类似课程学习）。

\textbf{Pros:} Freshness; can use student-generated inputs for on-policy distillation.\\
\textbf{优点：} 数据新鲜；可使用学生模型生成的输入进行在线蒸馏。

\textbf{Cons:} Double the GPU cost; synchronisation complexity; harder to scale.
\textbf{缺点：} GPU成本翻倍；同步复杂；难以扩展。

\paragraph{Black-Box (API) Distillation.}
\paragraph{黑盒（API）蒸馏（Black-Box (API) Distillation）。}
\label{black-box-api-distillation.}

When only text outputs are available (e.g.~distilling from a proprietary API), the student is trained via SFT on the teacher’s generations, optionally augmented with chain-of-thought traces.
当仅能获得文本输出时（例如从专有API进行蒸馏），学生模型通过监督微调（SFT）在教师模型的生成结果上进行训练，可选地辅以思维链（chain-of-thought）轨迹。

\textbf{Motivation:} Practical reality --- most frontier models do not expose logits.
\textbf{动机：} 现实情况——大多数前沿模型不暴露 logits。

\textbf{Pros:} Simple pipeline; works with any model behind an API.\\
\textbf{优点：} 流程简单；可与任何通过API访问的模型配合使用。

\textbf{Cons:} No soft-label signal; prone to hallucination amplification; effectively supervised fine-tuning.
\textbf{缺点：} 无软标签信号；容易放大幻觉；本质上是监督微调。

\paragraph{Self-Distillation.}
\paragraph{自蒸馏（Self-Distillation）。}
\label{self-distillation.}

A model distils from a larger version within the same architecture family (e.g.~Llama-3 70B $\to$ 8B) or from its own checkpoints during training.
一个模型从同一架构家族中的更大版本（例如 Llama-3 70B $\to$ 8B）或训练过程中的自身检查点进行蒸馏。

\textbf{Motivation:} Avoid training a separate teacher; leverage the model’s own capacity at different scales.
\textbf{动机：} 避免训练单独的教师模型；利用模型自身在不同规模下的能力。

\textbf{Pros:} Architecture compatibility; no external dependency.\\
\textbf{优点：} 架构兼容性；无外部依赖。

\textbf{Cons:} Teacher ceiling equals model ceiling; cannot introduce genuinely new knowledge.
\textbf{缺点：} 教师模型上限等于模型自身上限；无法引入真正的新知识。

\begin{intuitionbox}[Dark Knowledge]
Consider a language model predicting the next word after ``The capital of France is''. Hard labels say only ``Paris'' is correct. But the teacher’s soft distribution might assign 5\% to ``Lyon'', 2\% to ``Marseille'', and near-zero to ``banana'' --- telling the student \emph{which errors are reasonable}, which dramatically improves calibration and generalisation.
\end{intuitionbox}
\begin{intuitionbox}[暗知识（Dark Knowledge）]
考虑一个语言模型预测“法国的首都是”后面的下一个词。硬标签只认为“巴黎”是正确的。但教师模型的软分布可能给“里昂”分配5%，给“马赛”分配2%，给“香蕉”分配接近0——这告诉学生模型\emph{哪些错误是合理的}，从而显著提高校准性和泛化能力。
\end{intuitionbox}

\paragraph{Practical Considerations for LLM Distillation.}
\paragraph{LLM蒸馏的实践考虑（Practical Considerations for LLM Distillation）。}
\label{practical-considerations-for-llm-distillation.}

\begin{itemize}
  \item \textbf{Sequence-level vs.~token-level:} Token-level KL is standard; sequence-level distillation (minimising KL over full sequences) better captures long-range coherence but is harder to optimise.
  \item \textbf{序列级 vs. 词元级：} 词元级KL散度是标准做法；序列级蒸馏（最小化完整序列上的KL）能更好地捕捉长程连贯性，但优化难度更大。
  \item \textbf{Layer-wise hints:} Matching intermediate representations (attention maps, hidden states) provides additional learning signal --- especially useful when student architecture differs.
  \item \textbf{逐层提示：} 匹配中间表示（注意力图、隐藏状态）提供额外的学习信号——当学生模型架构不同时尤其有用。
  \item \textbf{Data selection:} Distillation data quality matters; curating diverse, hard examples yields better students than random sampling.
  \item \textbf{数据选择：} 蒸馏数据质量至关重要；精心挑选多样化的困难样本比随机采样能训练出更好的学生模型。
  \item \textbf{Student capacity:} Diminishing returns below $\sim$10\% of teacher parameters; at extreme compression, architecture changes (e.g.~MoE $\to$ dense) may be needed.
  \item \textbf{学生模型容量：} 当学生模型参数低于教师模型的约10%时收益递减；极端压缩时可能需要改变架构（例如从MoE变为密集模型）。
  \item \textbf{Combining with quantization:} Distillation + 4-bit quantization (e.g.~QLoRA-distilled models) achieves near-teacher quality at $20\times$ compression.
  \item \textbf{结合量化：} 蒸馏 + 4-bit量化（例如 QLoRA 蒸馏模型）在 $20\times$ 压缩比下达到接近教师模型的质量。
\end{itemize}

\begin{examplebox}[Compression Method Comparison – 70B Model]
\begin{tabular}{@{}lp{2.5cm}p{2.8cm}p{2.8cm}p{2.8cm}@{}}
\toprule
\textbf{Method} & \textbf{Size} & \textbf{Speed} & \textbf{Quality} & \textbf{Use Case} \\
\textbf{方法} & \textbf{大小} & \textbf{速度} & \textbf{质量} & \textbf{用例} \\
\midrule
BF16 (baseline) & 140 GB & 1$\times$ & 100\% & Training, reference \\
BF16（基线） & 140 GB & 1$\times$ & 100\% & 训练、参考 \\
FP8 (E4M3) & 70 GB & 2$\times$ & 99.5\% & H100 inference \\
FP8（E4M3） & 70 GB & 2$\times$ & 99.5\% & H100 推理 \\
INT8 (SmoothQuant) & 70 GB & 1.8$\times$ & 99\% & A100 inference \\
INT8（SmoothQuant） & 70 GB & 1.8$\times$ & 99\% & A100 推理 \\
4-bit (AWQ) & 35 GB & 2.5$\times$ & 97--98\% & Serving at scale \\
4-bit（AWQ） & 35 GB & 2.5$\times$ & 97--98\% & 大规模服务 \\
2-bit (AQLM) & 17.5 GB & 3$\times$ & 90--93\% & Edge, experimental \\
2-bit（AQLM） & 17.5 GB & 3$\times$ & 90--93\% & 边缘设备、实验性 \\
Pruned 50\% (2:4) & 70 GB & 1.8$\times$ & 97\% & Structured speedup \\
剪枝50\%（2:4） & 70 GB & 1.8$\times$ & 97\% & 结构化加速 \\
Distilled 8B & 16 GB & 10$\times$ & 80--85\% & Mobile, edge \\
蒸馏8B & 16 GB & 10$\times$ & 80--85\% & 移动端、边缘设备 \\
\bottomrule
\end{tabular}
\end{examplebox}
\begin{examplebox}[压缩方法对比——70B模型]
\begin{tabular}{@{}lp{2.5cm}p{2.8cm}p{2.8cm}p{2.8cm}@{}}
\toprule
\textbf{Method} & \textbf{Size} & \textbf{Speed} & \textbf{Quality} & \textbf{Use Case} \\
\textbf{方法} & \textbf{大小} & \textbf{速度} & \textbf{质量} & \textbf{用例} \\
\midrule
BF16 (baseline) & 140 GB & 1$\times$ & 100\% & Training, reference \\
BF16（基线） & 140 GB & 1$\times$ & 100\% & 训练、参考 \\
FP8 (E4M3) & 70 GB & 2$\times$ & 99.5\% & H100 inference \\
FP8（E4M3） & 70 GB & 2$\times$ & 99.5\% & H100 推理 \\
INT8 (SmoothQuant) & 70 GB & 1.8$\times$ & 99\% & A100 inference \\
INT8（SmoothQuant） & 70 GB & 1.8$\times$ & 99\% & A100 推理 \\
4-bit (AWQ) & 35 GB & 2.5$\times$ & 97--98\% & Serving at scale \\
4-bit（AWQ） & 35 GB & 2.5$\times$ & 97--98\% & 大规模服务 \\
2-bit (AQLM) & 17.5 GB & 3$\times$ & 90--93\% & Edge, experimental \\
2-bit（AQLM） & 17.5 GB & 3$\times$ & 90--93\% & 边缘设备、实验性 \\
Pruned 50\% (2:4) & 70 GB & 1.8$\times$ & 97\% & Structured speedup \\
剪枝50\%（2:4） & 70 GB & 1.8$\times$ & 97\% & 结构化加速 \\
Distilled 8B & 16 GB & 10$\times$ & 80--85\% & Mobile, edge \\
蒸馏8B & 16 GB & 10$\times$ & 80--85\% & 移动端、边缘设备 \\
\bottomrule
\end{tabular}
\end{examplebox}

\section{Speculative Decoding Methods}
\section{推测解码方法（Speculative Decoding Methods）}
\label{speculative-decoding-methods}

Speculative decoding~\cite{leviathan2023fast} accelerates autoregressive generation by predicting multiple tokens simultaneously, then verifying them in a single forward pass of the target model. It produces \textbf{identical output distribution} to standard decoding (no quality loss) while achieving 2--3$\times$ speedup.
推测解码~\cite{leviathan2023fast} 通过同时预测多个词元，然后在目标模型的一次前向传播中验证它们，从而加速自回归生成。它产生与标准解码\textbf{完全相同的输出分布}（无质量损失），同时实现2--3$\times$的加速。

\subsection{Core Principle}
\subsection{核心原理（Core Principle）}
\label{core-principle}

\begin{keybox}[Speculative Decoding Framework]
\begin{enumerate}
  \item A fast \textbf{draft mechanism} proposes $k$ candidate tokens: $\hat{x}_1, \ldots, \hat{x}_k$
  \item The large \textbf{target model} runs a single forward pass on all $k$ tokens (batched)
  \item \textbf{Verification}: Accept tokens left-to-right while $P_{\text{target}}(\hat{x}_i) \geq r_i \cdot P_{\text{draft}}(\hat{x}_i)$ (where $r_i \sim U[0,1]$)
  \item On first rejection at position $j$: resample $x_j$ from an adjusted distribution, discard $\hat{x}_{j+1}, \ldots, \hat{x}_k$
\end{enumerate}

\textbf{Key property}: This acceptance/rejection scheme guarantees the final distribution equals $P_{\text{target}}$ exactly.

\textbf{Speedup}: If acceptance rate is $\alpha$, expected tokens per step = $\frac{1 - \alpha^{k+1}}{1 - \alpha}$. At $\alpha=0.8$, $k=5$: expected 3.4 tokens/step vs.~1 for standard decoding.
\end{keybox}
\begin{keybox}[推测解码框架]
\begin{enumerate}
  \item 一个快速的\textbf{草稿机制}提出 $k$ 个候选词元：$\hat{x}_1, \ldots, \hat{x}_k$
  \item 大型\textbf{目标模型}对所有 $k$ 个词元执行一次前向传播（批量处理）
  \item \textbf{验证}：从左到右接受词元，条件为 $P_{\text{target}}(\hat{x}_i) \geq r_i \cdot P_{\text{draft}}(\hat{x}_i)$（其中 $r_i \sim U[0,1]$）
  \item 在位置 $j$ 首次拒绝时：从调整后的分布中重新采样 $x_j$，丢弃 $\hat{x}_{j+1}, \ldots, \hat{x}_k$
\end{enumerate}

\textbf{关键性质}：该接受/拒绝方案保证最终分布精确等于 $P_{\text{target}}$。

\textbf{加速}：如果接受率为 $\alpha$，每步期望词元数 = $\frac{1 - \alpha^{k+1}}{1 - \alpha}$。当 $\alpha=0.8$，$k=5$ 时：每步期望3.4个词元，而标准解码为1个。
\end{keybox}

\subsection{Methods Comparison}
\subsection{方法对比（Methods Comparison）}
\label{methods-comparison}

\begin{table}[ht!]
\centering
\caption{Speculative decoding methods supported by modern inference engines.}
\caption{现代推理引擎支持的推测解码方法。}
\begin{tabular}{@{}lllp{6cm}@{}}
\toprule
\textbf{Method} & \textbf{Draft Source} & \textbf{Speedup} & \textbf{Key Idea} \\
\textbf{方法} & \textbf{草稿来源} & \textbf{加速比} & \textbf{核心思想} \\
\midrule
\textbf{Standard}~\cite{leviathan2023fast} & Small model (1--7B) & 2--3$\times$ & Separate draft model generates candidates. Simple but requires loading 2 models. \\
\textbf{标准方法}~\cite{leviathan2023fast} & 小模型（1--7B） & 2--3$\times$ & 独立的草稿模型生成候选词元。简单但需加载两个模型。 \\
\textbf{Medusa}~\cite{cai2024medusa} & Parallel LM heads & 2--3$\times$ & Add $k$ extra prediction heads to the target model. Each predicts token at position $+1, +2, \ldots, +k$. \\
\textbf{Medusa}~\cite{cai2024medusa} & 并行LM头 & 2--3$\times$ & 向目标模型添加 $k$ 个额外的预测头。每个头预测位置 $+1, +2, \ldots, +k$ 的词元。 \\
\textbf{Eagle}~\cite{li2024eagle} & Feature-level & 2.5--3.5$\times$ & Lightweight decoder generates draft tokens from target model's hidden states. Higher acceptance than Medusa. \\
\textbf{Eagle}~\cite{li2024eagle} & 特征级 & 2.5--3.5$\times$ & 轻量级解码器从目标模型的隐藏状态生成草稿词元。接受率高于Medusa。 \\
\textbf{Eagle-2}~\cite{li2024eagle} & Context-aware & 3--4$\times$ & Dynamic draft tree with confidence-based expansion. State-of-the-art acceptance rates. \\
\textbf{Eagle-2}~\cite{li2024eagle} & 上下文感知 & 3--4$\times$ & 基于置信度扩展的动态草稿树。最先进的接受率。 \\
\textbf{N-gram Lookup} & N-gram cache & 1.5--2$\times$ & Match prompt n-grams against previously generated text. Zero cost; great for repetitive outputs. \\
\textbf{N-gram查找} & N-gram缓存 & 1.5--2$\times$ & 将提示中的n-gram与之前生成的文本匹配。零成本；适用于重复性输出。 \\
\textbf{Lookahead}~\cite{fu2024lookahead} & Jacobi iteration & 2--2.5$\times$ & Parallel Jacobi decoding with n-gram verification. No draft model; uses target model itself. \\
\textbf{Lookahead}~\cite{fu2024lookahead} & Jacobi迭代 & 2--2.5$\times$ & 带n-gram验证的并行Jacobi解码。无草稿模型；使用目标模型自身。 \\
\textbf{Multi-token}~\cite{gloeckle2024multi} & Modified arch. & 2--3$\times$ & Train the model to natively predict multiple tokens per step (Meta's approach in Llama). \\
\textbf{多词元}~\cite{gloeckle2024multi} & 修改架构 & 2--3$\times$ & 训练模型原生预测每步多个词元（Meta在Llama中的方法）。 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Medusa: Multi-Head Speculative Decoding}
\subsection{Medusa：多头推测解码（Medusa: Multi-Head Speculative Decoding）}
\label{medusa-multi-head-speculative-decoding}

\begin{keybox}[How Medusa Works]
Medusa adds $k$ additional ``prediction heads'' to the LLM (sharing the same backbone):

\begin{itemize}
  \item Head 0 (original): predicts token at position $t+1$ (standard next-token)
  \item Head 1: predicts token at position $t+2$ (skipping one)
  \item Head $i$: predicts token at position $t+i+1$
  \item All heads run in parallel during a single forward pass
  \item A \textbf{tree-structured} verification validates multiple candidate sequences simultaneously
\end{itemize}

\textbf{Training}: Fine-tune only the Medusa heads (backbone frozen). Cost: $\sim$1 epoch on representative data.

\textbf{Advantage}: No separate draft model; heads are tiny (one linear layer each). Memory overhead: $<$1\%.
\end{keybox}
\begin{keybox}[Medusa工作原理]
Medusa向LLM添加 $k$ 个额外的“预测头”（共享同一主干）：

\begin{itemize}
  \item 头0（原始）：预测位置 $t+1$ 的词元（标准下一词元预测）
  \item 头1：预测位置 $t+2$ 的词元（跳过一个位置）
  \item 头 $i$：预测位置 $t+i+1$ 的词元
  \item 所有头在单次前向传播中并行运行
  \item 一个\textbf{树结构}验证同时验证多个候选序列
\end{itemize}

\textbf{训练}：仅微调Medusa头（主干冻结）。成本：在代表性数据上约1个epoch。

\textbf{优势}：无需单独的草稿模型；头非常小（每个仅一个线性层）。内存开销：$<$1\%。
\end{keybox}

\subsection{Eagle: Feature-Level Drafting}
\subsection{Eagle：特征级草稿生成（Eagle: Feature-Level Drafting）}
\label{eagle-feature-level-drafting}

## 直觉框：为什么 Eagle 优于 Medusa

## 直觉框：为什么 Eagle 优于 Medusa

Medusa's heads predict independently at each position — they cannot condition on their own previous predictions (token at $t+2$ doesn't know what was predicted at $t+1$). Eagle fixes this with a lightweight autoregressive decoder that operates on the target model's hidden states:
Medusa 的每个位置的头独立预测——它们无法基于自身之前的预测进行条件化（$t+2$ 处的 Token 不知道 $t+1$ 处预测了什么）。Eagle 通过一个轻量级的自回归解码器来修复这一问题，该解码器在目标模型的隐藏状态上运行：

\begin{enumerate}
  \item Extract hidden states from the target model's last layer
  \item 从目标模型的最后一层提取隐藏状态
  \item Feed into a small (1-layer) decoder that autoregressively generates draft tokens conditioned on previous hidden states
  \item 输入到一个小型（1层）解码器，该解码器基于之前的隐藏状态自回归地生成草稿 Token
  \item This captures inter-token dependencies that Medusa misses
  \item 这捕获了 Medusa 遗漏的 Token 间依赖关系
\end{enumerate}

Result: Eagle achieves 85--95\% acceptance rate vs.~Medusa's 60--80\%.
结果：Eagle 实现了 85--95\% 的接受率，而 Medusa 为 60--80\%。

\subsection{N-gram Speculative Decoding}
\subsection{N-gram 推测解码}
\label{n-gram-speculative-decoding}

\begin{keybox}[N-gram Lookup Method]
\begin{关键框}[N-gram 查找方法]
The simplest speculative decoding — requires no additional model or training:
最简单的推测解码 — 无需额外的模型或训练：

\begin{enumerate}
  \item Maintain a cache of n-grams from the prompt and previously generated text
  \item 维护一个来自提示和先前生成文本的 n-gram 缓存
  \item At each step, check if the current context's last $n-1$ tokens match any cached n-gram
  \item 在每一步，检查当前上下文的最后 $n-1$ 个 Token 是否匹配任何缓存的 n-gram
  \item If yes: propose the continuation as draft tokens
  \item 如果匹配：将该延续部分作为草稿 Token 提出
  \item Verify against target model as usual
  \item 像往常一样对目标模型进行验证
\end{enumerate}

\textbf{Best for}: Code generation (repetitive patterns), structured outputs (JSON/XML), and prompts with repeated elements. \textbf{Cost}: Essentially zero.
\textbf{最佳适用场景}：代码生成（重复模式）、结构化输出（JSON/XML）以及包含重复元素的提示。\textbf{成本}：几乎为零。
\end{keybox}
\end{关键框}

\newpage
\subsection{Integration with vLLM}
\subsection{与 vLLM 的集成}
\label{integration-with-vllm}

\begin{lstlisting}[style=pythonstyle]
from vllm import LLM, SamplingParams

