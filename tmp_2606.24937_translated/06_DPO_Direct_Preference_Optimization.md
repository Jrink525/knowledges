# DPO — Direct Preference Optimization  
# DPO —— 直接偏好优化  

## Motivation  
## 动机  

PPO requires 4 models in memory (policy, reference, reward model, value head), complex RL infrastructure, and is notoriously unstable. DPO~\cite{rafailov2023direct} asks: \emph{can we skip the RL and learn directly from preferences?}  
PPO（近端策略优化）需要在内存中维护4个模型（策略模型、参考模型、奖励模型、价值网络），依赖复杂的强化学习基础设施，并且以不稳定著称。DPO（直接偏好优化）~\cite{rafailov2023direct} 提出了一个问题：\emph{我们能否跳过强化学习，直接从偏好中学习？}  

\textbf{Key insight}: The optimal policy under the RLHF objective (reward maximization + KL penalty) has a \textbf{closed-form solution}. We can derive a supervised loss that implicitly optimizes the same objective.  
\textbf{核心洞察}：在 RLHF（基于人类反馈的强化学习）目标（奖励最大化 + KL（库尔贝克-莱布勒）惩罚）下的最优策略具有 \textbf{闭式解}。我们可以推导出一个监督损失函数，隐式地优化同一目标。  

## Mathematical Derivation  
## 数学推导  

\textbf{Step 1}: RLHF objective: $\max_\pi \mathbb{E}_{x,y\sim\pi}[r(x,y)] - \beta D_\text{KL}[\pi\|\pi_\text{ref}]$  
\textbf{步骤1}：RLHF 目标：$\max_\pi \mathbb{E}_{x,y\sim\pi}[r(x,y)] - \beta D_\text{KL}[\pi\|\pi_\text{ref}]$  

\textbf{Step 2}: The optimal solution is: $\pi^*(y|x) = \frac{1}{Z(x)} \pi_\text{ref}(y|x) \exp\left(\frac{r(x,y)}{\beta}\right)$  
\textbf{步骤2}：最优解为：$\pi^*(y|x) = \frac{1}{Z(x)} \pi_\text{ref}(y|x) \exp\left(\frac{r(x,y)}{\beta}\right)$  

\textbf{Step 3}: Rearrange to express reward in terms of policy: $r(x,y) = \beta \log \frac{\pi^*(y|x)}{\pi_\text{ref}(y|x)} + \beta \log Z(x)$  
\textbf{步骤3}：重新排列以用策略表示奖励：$r(x,y) = \beta \log \frac{\pi^*(y|x)}{\pi_\text{ref}(y|x)} + \beta \log Z(x)$  

\textbf{Step 4}: Substitute into Bradley-Terry preference model $P(y_w \succ y_l) = \sigma(r(y_w) - r(y_l))$. The $Z(x)$ cancels!  
\textbf{步骤4}：代入 Bradley-Terry 偏好模型 $P(y_w \succ y_l) = \sigma(r(y_w) - r(y_l))$。$Z(x)$ 被消去！  

\begin{equation}
\boxed{\mathcal{L}_\text{DPO}(\theta) = -\mathbb{E}_{(x, y_w, y_l)}\left[\log\sigma\left(\beta\log\frac{\pi_\theta(y_w|x)}{\pi_\text{ref}(y_w|x)} - \beta\log\frac{\pi_\theta(y_l|x)}{\pi_\text{ref}(y_l|x)}\right)\right]}
\end{equation}

\begin{intuitionbox}[What DPO Actually Does]
Define the \textbf{implicit reward} as $\hat{r}(x,y) = \beta\log\frac{\pi_\theta(y|x)}{\pi_\text{ref}(y|x)}$.

DPO minimizes the cross-entropy loss where the ``label'' is: chosen should have higher implicit reward than rejected. The margin is controlled by $\beta$:

\begin{itemize}
  \item Large $\beta$: need large margin $\rightarrow$ policy moves aggressively $\rightarrow$ risk forgetting
  \item Large $\beta$：需要大间隔 $\rightarrow$ 策略激进变化 $\rightarrow$ 有遗忘风险
  \item Small $\beta$: small margin suffices $\rightarrow$ policy stays close to reference $\rightarrow$ conservative
  \item Small $\beta$：小间隔即可 $\rightarrow$ 策略接近参考模型 $\rightarrow$ 保守
\end{itemize}

The reference model acts as a regularizer: the policy must ``justify'' any deviation from it by showing preference alignment.
参考模型充当正则化器：策略必须通过展示偏好对齐来“证明”任何偏离的合理性。
\end{intuitionbox}

\begin{intuitionbox}[DPO 实际做了什么]
将 \textbf{隐式奖励} 定义为 $\hat{r}(x,y) = \beta\log\frac{\pi_\theta(y|x)}{\pi_\text{ref}(y|x)}$。

DPO 最小化交叉熵损失，其中“标签”是：被选中的回答应具有比被拒绝的回答更高的隐式奖励。间隔由 $\beta$ 控制：

\begin{itemize}
  \item 大的 $\beta$：需要大间隔 $\rightarrow$ 策略激进变化 $\rightarrow$ 有遗忘风险
  \item 大的 $\beta$：需要大间隔 $\rightarrow$ 策略激进变化 $\rightarrow$ 有遗忘风险
  \item 小的 $\beta$：小间隔即可 $\rightarrow$ 策略接近参考模型 $\rightarrow$ 保守
  \item 小的 $\beta$：小间隔即可 $\rightarrow$ 策略接近参考模型 $\rightarrow$ 保守
\end{itemize}

参考模型充当正则化器：策略必须通过展示偏好对齐来“证明”任何偏离的合理性。
\end{intuitionbox}

## Gradient Analysis  
## 梯度分析  

The DPO gradient decomposes as: 
\begin{equation}
\nabla_\theta \mathcal{L} = -\beta \cdot \underbrace{\sigma(-\hat{r}_w + \hat{r}_l)}_{\text{weight: higher when model is wrong}} \cdot \left[\nabla_\theta \log\pi_\theta(y_w|x) - \nabla_\theta \log\pi_\theta(y_l|x)\right]
\end{equation}
 
\textbf{Interpretation}: The gradient increases probability of chosen and decreases rejected. The weight is largest when the model currently prefers the wrong answer --- it focuses learning on ``confusing'' pairs.  
\textbf{解释}：梯度增加被选中回答的概率，降低被拒绝回答的概率。当模型当前偏向错误答案时，权重最大 —— 它使学习集中在“令人困惑”的样本对上。  

\begin{examplebox}[Concrete DPO Example]
\textbf{Prompt}: ``Explain quantum entanglement to a 10-year-old.''

\textbf{Chosen} ($y_w$): ``Imagine you have two magic coins. When you flip one and it’s heads, the other one instantly becomes tails, no matter how far apart they are!''\\

$\log\pi_\theta(y_w|x) = -15.3$, $\log\pi_\text{ref}(y_w|x) = -16.1$

\textbf{Rejected} ($y_l$): ``Quantum entanglement is a phenomenon where two particles become correlated such that the quantum state of one particle cannot be described independently.''\\

$\log\pi_\theta(y_l|x) = -12.8$, $\log\pi_\text{ref}(y_l|x) = -12.5$

\textbf{Implicit rewards}: $\hat{r}_w = 0.1 \times ((-15.3) - (-16.1)) = 0.08$, $\hat{r}_l = 0.1 \times ((-12.8) - (-12.5)) = -0.03$

\textbf{Loss input}: $\sigma(0.08 - (-0.03)) = \sigma(0.11) = 0.527$

\textbf{Loss}: $-\log(0.527) = 0.64$ --- The model barely prefers the chosen. Gradient will push hard.

After training: chosen probability increases, rejected decreases, until margin stabilizes around $1/(2\beta)$.
\end{examplebox}

\begin{examplebox}[具体 DPO 示例]
\textbf{提示}：“用量子纠缠对一个十岁孩子解释。”

\textbf{被选中} ($y_w$)：“想象你有两枚魔法硬币。当你抛起一枚并得到正面时，另一枚会立即变为反面，无论它们相隔多远！”\\

$\log\pi_\theta(y_w|x) = -15.3$, $\log\pi_\text{ref}(y_w|x) = -16.1$

\textbf{被拒绝} ($y_l$)：“量子纠缠是一种两个粒子相互关联的现象，使得其中一个粒子的量子态无法独立描述。”\\

$\log\pi_\theta(y_l|x) = -12.8$, $\log\pi_\text{ref}(y_l|x) = -12.5$

\textbf{隐式奖励}：$\hat{r}_w = 0.1 \times ((-15.3) - (-16.1)) = 0.08$, $\hat{r}_l = 0.1 \times ((-12.8) - (-12.5)) = -0.03$

\textbf{损失输入}：$\sigma(0.08 - (-0.03)) = \sigma(0.11) = 0.527$

\textbf{损失}：$-\log(0.527) = 0.64$ —— 模型几乎不偏好被选中的回答。梯度将强力推动。

训练后：被选中回答的概率增加，被拒绝回答的概率降低，直到间隔稳定在 $1/(2\beta)$ 附近。
\end{examplebox}

## TRL Implementation  
## TRL 实现  

The following shows a minimal working example using HuggingFace TRL.  
以下展示了一个使用 HuggingFace TRL 的最小可运行示例。

\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig
from datasets import load_dataset

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B-Instruct",
    torch_dtype=torch.bfloat16, attn_implementation="flash_attention_2")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")

# 数据集格式: {"prompt": str, "chosen": str, "rejected": str}
dataset = load_dataset("argilla/ultrafeedback-binarized-preferences")

lora_config = LoraConfig(r=64, lora_alpha=16, lora_dropout=0.05,
    target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"])

dpo_config = DPOConfig(
    output_dir="./dpo_output",
    beta=0.1,                    # KL 正则化强度
    learning_rate=5e-7,          # 极低学习率以保证稳定性
    loss_type="sigmoid",         # 标准 DPO 损失
    max_length=2048,             # 最大序列长度
    max_prompt_length=1024,      # 提示截断
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,  # 有效批次大小 = 16
    gradient_checkpointing=True,
    bf16=True,
    num_train_epochs=1,          # DPO 容易过拟合——只跑 1 轮！
    warmup_ratio=0.1,
    logging_steps=10,
    eval_strategy="steps",
    eval_steps=200,
    save_strategy="steps",
    save_steps=500,
)

trainer = DPOTrainer(
    model=model,
    ref_model=None,             # 使用 LoRA 时，ref = 基模型（无需拷贝！）
    args=dpo_config,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    tokenizer=tokenizer,
    peft_config=lora_config,
)
trainer.train()
# 需要监控的关键指标：train/rewards/chosen, train/rewards/rejected, train/rewards/margins
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig
from datasets import load_dataset

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B-Instruct",
    torch_dtype=torch.bfloat16, attn_implementation="flash_attention_2")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")

# 数据集格式: {"prompt": str, "chosen": str, "rejected": str}
dataset = load_dataset("argilla/ultrafeedback-binarized-preferences")

lora_config = LoraConfig(r=64, lora_alpha=16, lora_dropout=0.05,
    target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"])

dpo_config = DPOConfig(
    output_dir="./dpo_output",
    beta=0.1,                    # KL 正则化强度
    learning_rate=5e-7,          # 极低学习率以保证稳定性
    loss_type="sigmoid",         # 标准 DPO 损失
    max_length=2048,             # 最大序列长度
    max_prompt_length=1024,      # 提示截断
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,  # 有效批次大小 = 16
    gradient_checkpointing=True,
    bf16=True,
    num_train_epochs=1,          # DPO 容易过拟合——只跑 1 轮！
    warmup_ratio=0.1,
    logging_steps=10,
    eval_strategy="steps",
    eval_steps=200,
    save_strategy="steps",
    save_steps=500,
)

trainer = DPOTrainer(
    model=model,
    ref_model=None,             # 使用 LoRA 时，ref = 基模型（无需拷贝！）
    args=dpo_config,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    tokenizer=tokenizer,
    peft_config=lora_config,
)
trainer.train()
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
    # batch contains: input_ids_chosen, input_ids_rejected,
    #                 labels_chosen, labels_rejected (prompt masked to -100)
    
    # 1. Forward pass: get per-token log-probs
    logps_chosen = get_sequence_logprob(model, batch["chosen"])
    logps_rejected = get_sequence_logprob(model, batch["rejected"])
    
    # 2. Reference log-probs (pre-computed or computed here)
    with torch.no_grad():
        ref_logps_chosen = get_sequence_logprob(ref_model, batch["chosen"])
        ref_logps_rejected = get_sequence_logprob(ref_model, batch["rejected"])
    
    # 3. Compute implicit reward margins
    chosen_rewards = beta * (logps_chosen - ref_logps_chosen)
    rejected_rewards = beta * (logps_rejected - ref_logps_rejected)
    
    # 4. DPO loss = -log(sigmoid(chosen_reward - rejected_reward))
    loss = -F.logsigmoid(chosen_rewards - rejected_rewards).mean()
    return loss


def get_sequence_logprob(model, sequences):
    """Sum of log-probs over response tokens only."""
    outputs = model(sequences["input_ids"], attention_mask=sequences["mask"])
    logits = outputs.logits[:, :-1, :]  # Shift for next-token prediction
    
    # Gather log-prob of actual tokens
    labels = sequences["labels"][:, 1:]  # Shifted labels
    log_probs = F.log_softmax(logits, dim=-1)
    token_logps = log_probs.gather(-1, labels.unsqueeze(-1)).squeeze(-1)
    
    # Mask: only sum over response tokens (labels != -100)
    mask = (labels != -100).float()
    return (token_logps * mask).sum(dim=-1)  # Shape: [batch_size]
\end{lstlisting}
\begin{lstlisting}[style=pythonstyle]
def dpo_loss(model, ref_model, batch, beta=0.1):
    """一次 DPO 训练步骤。"""
    # batch 包含：input_ids_chosen, input_ids_rejected,
    #                 labels_chosen, labels_rejected (提示被掩码为 -100)
    
    # 1. 前向传播：获取每个 token 的对数概率
    logps_chosen = get_sequence_logprob(model, batch["chosen"])
    logps_rejected = get_sequence_logprob(model, batch["rejected"])
    
    # 2. 参考对数概率（预计算或在此处计算）
    with torch.no_grad():
        ref_logps_chosen = get_sequence_logprob(ref_model, batch["chosen"])
        ref_logps_rejected = get_sequence_logprob(ref_model, batch["rejected"])
    
    # 3. 计算隐式奖励边际
    chosen_rewards = beta * (logps_chosen - ref_logps_chosen)
    rejected_rewards = beta * (logps_rejected - ref_logps_rejected)
    
    # 4. DPO 损失 = -log(sigmoid(chosen_reward - rejected_reward))
    loss = -F.logsigmoid(chosen_rewards - rejected_rewards).mean()
    return loss


def get_sequence_logprob(model, sequences):
    """仅对响应 token 的对数概率求和。"""
    outputs = model(sequences["input_ids"], attention_mask=sequences["mask"])
    logits = outputs.logits[:, :-1, :]  # 为下一个 token 预测进行移位
    
    # 收集实际 token 的对数概率
    labels = sequences["labels"][:, 1:]  # 移位后的标签
    log_probs = F.log_softmax(logits, dim=-1)
    token_logps = log_probs.gather(-1, labels.unsqueeze(-1)).squeeze(-1)
    
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


# Jensen-Shannon divergence (balanced)
config = DPOConfig(
    f_divergence_type="js_divergence",
    beta=0.1,
)


# Alpha divergence (alpha=0: forward KL, alpha=1: reverse KL)
config_alpha = DPOConfig(
    f_divergence_type="alpha_divergence",
    f_alpha_divergence_coef=0.5,   # alpha parameter
    beta=0.1,
)


trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}


\begin{keybox}[When to Use f-DPO]
\begin{keybox}[何时使用f-DPO]
\begin{itemize}
  \item Use \textbf{JS divergence} when you want a balance between diversity and quality.
  \item 当你需要在多样性和质量之间取得平衡时，使用\textbf{JS散度}。
  \item Use \textbf{forward KL} for creative tasks where diversity is paramount.
  \item 对于多样性至关重要的创意任务，使用\textbf{正向KL}。
  \item Use \textbf{reverse KL} (standard DPO) for tasks with a single correct answer.
  \item 对于只有一个正确答案的任务，使用\textbf{反向KL}（标准DPO）。
  \item Use \textbf{alpha divergence} to continuously interpolate and tune the trade-off.
  \item 使用\textbf{alpha散度}来连续插值和调节权衡。
\end{itemize}
\end{keybox}

## Robust DPO
## 鲁棒 DPO

\label{sec:robust-dpo}

\begin{intuitionbox}[Noisy Labels in Preference Data]
Human preference annotations are noisy. Annotators disagree, make mistakes, and sometimes flip the preferred/dispreferred labels. Standard DPO treats all labels as ground truth, which can cause the model to overfit to noise. Robust DPO~\cite{chowdhury2024robustdpo} analytically debiases the loss under a known noise model.
\begin{intuitionbox}[偏好数据中的噪声标签]
人类偏好标注存在噪声。标注者意见不一、会出错，有时甚至颠倒偏好/非偏好标签。标准 DPO 将所有标签视为真实标签，这可能导致模型过拟合噪声。Robust DPO（鲁棒DPO）~\cite{chowdhury2024robustdpo} 在已知噪声模型下对损失函数进行解析去偏。
\end{intuitionbox}

Assume each label is flipped with probability $\epsilon$ (the noise rate). The debiased loss is:
假设每个标签以概率 $\epsilon$（噪声率）被翻转。去偏后的损失函数为：

\[
\boxed{
    \mathcal{L}_{\text{robust}} =
    \frac{(1-\epsilon)\,\mathcal{L}_{\text{DPO}}(y_w, y_l)
          - \epsilon\,\mathcal{L}_{\text{DPO}}(y_l, y_w)}{1 - 2\epsilon},
  }
\]

where $\mathcal{L}_{\text{DPO}}(y_w, y_l)$ is the standard DPO loss treating $y_w$ as preferred, and $\mathcal{L}_{\text{DPO}}(y_l, y_w)$ is the loss with labels flipped. This correction removes the bias introduced by label noise.
其中 $\mathcal{L}_{\text{DPO}}(y_w, y_l)$ 是将 $y_w$ 视为优选的标准 DPO 损失，而 $\mathcal{L}_{\text{DPO}}(y_l, y_w)$ 是标签翻转后的损失。这一修正消除了标签噪声引入的偏差。

\begin{keybox}[Intuition for Robust DPO]
The formula is a linear combination that ``subtracts out'' the contribution of flipped labels. When $\epsilon=0$, it reduces to standard DPO. When $\epsilon=0.5$, the denominator goes to zero -- the labels are pure noise and no learning is possible. In practice, $\epsilon \in [0.05, 0.2]$ covers most real annotation noise levels.
\begin{keybox}[鲁棒DPO的直观理解]
该公式是一个线性组合，它“减去”了翻转标签的贡献。当 $\epsilon=0$ 时，它退化为标准 DPO。当 $\epsilon=0.5$ 时，分母为零——标签为纯噪声，无法进行学习。实践中，$\epsilon \in [0.05, 0.2]$ 覆盖了大多数真实的标注噪声水平。
\end{keybox}

\begin{examplebox}[Robust DPO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


config = DPOConfig(
    loss_type="robust",
    label_smoothing=0.1,   # corresponds to epsilon = 0.1
                           # 对应 epsilon = 0.1
    beta=0.1,
)


trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\subsection{TR-DPO -- Trust Region DPO}
\subsection{TR-DPO——信任区域 DPO}
\label{sec:tr-dpo}

\begin{intuitionbox}[Stale Reference Model Problem]
Standard DPO uses a fixed reference model $\pi_{\text{ref}}$ throughout training. As the policy $\pi_\theta$ improves, the KL penalty $\beta \log(\pi_\theta/\pi_{\text{ref}})$ grows, eventually dominating the loss and preventing further improvement. TR-DPO~\cite{gorbatenko2024trdpo} periodically updates the reference model to track the current policy.
\begin{intuitionbox}[过时参考模型问题]
标准 DPO 在整个训练过程中使用固定的参考模型 $\pi_{\text{ref}}$。随着策略 $\pi_\theta$ 的提升，KL 惩罚项 $\beta \log(\pi_\theta/\pi_{\text{ref}})$ 不断增大，最终主导损失函数，阻碍进一步改进。TR-DPO（信任区域DPO）~\cite{gorbatenko2024trdpo} 定期更新参考模型以跟踪当前策略。
\end{intuitionbox}

TR-DPO updates the reference model using an exponential moving average (EMA):
TR-DPO 使用指数移动平均（EMA）更新参考模型：

\[
\pi_{\text{ref}}^{(t+1)} \leftarrow
    \alpha \cdot \pi_\theta^{(t)} + (1-\alpha) \cdot \pi_{\text{ref}}^{(t)},
\]

where $\alpha \in (0,1)$ is the mixup coefficient. This is applied every $T_{\text{sync}}$ gradient steps.
其中 $\alpha \in (0,1)$ 是混合系数。该更新每 $T_{\text{sync}}$ 个梯度步执行一次。

\begin{examplebox}[TR-DPO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


config = DPOConfig(
    loss_type="sigmoid",        # standard DPO loss
                                # 标准 DPO 损失
    sync_ref_model=True,        # enable TR-DPO
                                # 启用 TR-DPO
    ref_model_mixup_alpha=0.6,  # alpha: how much of current policy to mix in
                                # alpha: 混合当前策略的比例
    ref_model_sync_steps=512,   # T_sync: sync every 512 steps
                                # T_sync: 每 512 步同步一次
    beta=0.1,
)


trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\begin{keybox}[When to Use TR-DPO]
\begin{itemize}
  \item Long training runs where the policy drifts far from the initial reference.
  \item When you observe the DPO loss plateauing early due to KL penalty domination.
  \item Iterative DPO pipelines where new preference data is collected from the current policy.
  \item Set $\alpha$ close to 1 for fast reference updates; close to 0 for slow updates.
\end{itemize}
\begin{keybox}[何时使用 TR-DPO]
\begin{itemize}
  \item 长时间训练，策略与初始参考模型偏差较大时。
  \item 当观察到 DPO 损失因 KL 惩罚主导而过早趋于平稳时。
  \item 迭代式 DPO 流程中，需要从当前策略收集新的偏好数据时。
  \item 将 $\alpha$ 设为接近 1 以快速更新参考模型；接近 0 以缓慢更新。
\end{itemize}
\end{keybox}

\subsection{EXO -- Exact Optimisation}
\subsection{EXO——精确优化}
\label{sec:exo}

\begin{intuitionbox}[DPO’s KL Direction Problem]
DPO is derived by solving for the optimal policy under a reverse KL constraint. However, the resulting loss actually optimises a \emph{forward} KL objective in the reward space, which is the wrong direction. EXO~\cite{ji2024exo} corrects this by using reverse KL probability matching, which is the theoretically correct objective for alignment.
\begin{intuitionbox}[DPO 的 KL 方向问题]
DPO 通过在逆向 KL 约束下求解最优策略推导得出。然而，最终的损失函数实际上在奖励空间中优化的是 \emph{正向} KL 目标，这是错误的方向。EXO（精确优化）~\cite{ji2024exo} 通过使用逆向 KL 概率匹配来修正这一问题，这是对齐任务中理论上正确的目标。
\end{intuitionbox}

EXO minimises the reverse KL between the model distribution and the target (reward-optimal) distribution:
EXO 最小化模型分布与目标（奖励最优）分布之间的逆向 KL：

\[
\mathcal{L}_{\text{EXO}} = \mathbb{E}_{y \sim \pi_\theta}\!\left[
    \log \frac{\pi_\theta(y|q)}{p^*(y|q)}
  \right],
\]

where $p^*(y|q) \propto \pi_{\text{ref}}(y|q) \exp(r(y,q)/\beta)$ is the optimal policy. In practice, EXO approximates this using the available preference pairs:
其中 $p^*(y|q) \propto \pi_{\text{ref}}(y|q) \exp(r(y,q)/\beta)$ 是最优策略。实践中，EXO 利用可用的偏好对进行近似：

\[
\mathcal{L}_{\text{EXO}} \approx -\mathbb{E}\!\left[
    \log \sigma\!\left(
      \beta \log \frac{\pi_{\text{ref}}(y_w|q)}{\pi_\theta(y_w|q)}
      - \beta \log \frac{\pi_{\text{ref}}(y_l|q)}{\pi_\theta(y_l|q)}
    \right)
  \right].
\]

Note the \emph{swapped} roles of $\pi_\theta$ and $\pi_{\text{ref}}$ compared to DPO.
注意与 DPO 相比，$\pi_\theta$ 和 $\pi_{\text{ref}}$ 的角色发生了 \emph{互换}。

\begin{examplebox}[EXO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


config = DPOConfig(
    loss_type="exo_pair",
    beta=0.1,
)


trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\subsection{NCA -- Noise Contrastive Alignment}
\subsection{NCA——噪声对比对齐}
\label{sec:nca}

\begin{intuitionbox}[Likelihood Collapse in DPO]
A known failure mode of DPO is \emph{likelihood collapse}: the model learns to decrease the probability of the losing response but also decreases the probability of the winning response (since the loss only cares about the \emph{difference}). NCA~\cite{chen2024nca} adds an absolute likelihood term to prevent this.
\begin{intuitionbox}[DPO 中的似然坍塌]
DPO 的一个已知失败模式是 \emph{似然坍塌}：模型学会降低失败回复的概率，但同时也会降低获胜回复的概率（因为损失函数只关心 \emph{差值}）。NCA（噪声对比对齐）~\cite{chen2024nca} 通过添加一个绝对似然项来防止这一问题。
\end{intuitionbox}

NCA reframes alignment as noise-contrastive estimation. The loss has three terms:
NCA 将对齐重新定义为噪声对比估计。损失函数包含三项：

\[
\boxed{
    \mathcal{L}_{\text{NCA}} =
      -\log \sigma(r_w)
      - \tfrac{1}{2}\log \sigma(-r_w)
      - \tfrac{1}{2}\log \sigma(-r_l),
  }
\]

where $r_y = \beta \log(\pi_\theta(y|q)/\pi_{\text{ref}}(y|q))$ is the implicit reward. The first term encourages high reward for $y_w$; the second and third terms penalise high reward for both $y_w$ and $y_l$ (preventing collapse).
其中 $r_y = \beta \log(\pi_\theta(y|q)/\pi_{\text{ref}}(y|q))$ 是隐式奖励。第一项鼓励 $y_w$ 获得高奖励；第二项和第三项惩罚 $y_w$ 和 $y_l$ 两者的高奖励（防止坍塌）。

\begin{examplebox}[NCA in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


config = DPOConfig(
    loss_type="nca_pair",
    beta=0.01,   # small beta: absolute likelihood term dominates
                 # 较小的 beta：绝对似然项占主导
)


trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\begin{keybox}[When to Use NCA]
\begin{itemize}
  \item When you observe the winning response probability decreasing during DPO training.
  \item For tasks where absolute response quality matters, not just relative ranking.
  \item Use small $\beta$ (e.g., 0.01) to give the absolute likelihood term more weight.
\end{itemize}
\begin{keybox}[何时使用 NCA]
\begin{itemize}
  \item 当观察到 DPO 训练中获胜回复概率下降时。
  \item 对于绝对回复质量（而非仅相对排序）至关重要的任务。
  \item 使用较小的 $\beta$（例如 0.01）以赋予绝对似然项更多权重。
\end{itemize}
\end{keybox}

\subsection{SLiC-HF -- Sequence Likelihood Calibration}
\subsection{SLiC-HF——序列似然校准}
\label{sec:slic}

\begin{intuitionbox}[Hinge Loss as a Simpler Alternative]
The log-sigmoid loss in DPO is smooth but can be slow to converge when the margin is large. SLiC-HF~\cite{zhao2023slichf} uses a hinge loss, which is zero when the margin exceeds a threshold and linear otherwise. This is simpler, faster, and surprisingly competitive.
\begin{intuitionbox}[作为更简单替代方案的合页损失]
DPO 中的对数 sigmoid 损失是平滑的，但当间隔较大时可能收敛缓慢。SLiC-HF（序列似然校准-合页）~\cite{zhao2023slichf} 使用合页损失，当间隔超过阈值时损失为零，否则为线性。这更简单、更快，且出人意料地具有竞争力。
\end{intuitionbox}

The SLiC-HF loss is:
SLiC-HF 损失为：

\[
\mathcal{L}_{\text{SLiC}} = \max\!\left(0,\;
    \delta - \beta\log\frac{\pi_\theta(y_w|q)}{\pi_{\text{ref}}(y_w|q)}
    + \beta\log\frac{\pi_\theta(y_l|q)}{\pi_{\text{ref}}(y_l|q)}
  \right),
\]

where $\delta$ is the margin threshold. When the model already assigns a margin of $\delta$ between winning and losing responses, the loss is zero.
其中 $\delta$ 是间隔阈值。当模型已在获胜和失败回复之间分配了 $\delta$ 的间隔时，损失为零。

\begin{examplebox}[SLiC-HF in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


config = DPOConfig(
    loss_type="hinge",
    beta=0.1,
)


trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\subsection{Iterative RPO -- Reasoning Preference Optimisation}
\subsection{Iterative RPO——推理偏好优化}
\label{sec:rpo}

\begin{intuitionbox}[DPO Forgets How to Generate]
Standard DPO trains the model to \emph{discriminate} between winning and losing responses. But for reasoning tasks, the model also needs to \emph{generate} correct reasoning traces. A model that can discriminate but not generate is useless at inference time. RPO adds an NLL (negative log-likelihood) term on the winning response to ensure the model learns to generate it.
\end{intuitionbox}

\begin{intuitionbox}[DPO 遗忘如何生成]
标准的 DPO 训练模型在获胜回答和失败回答之间进行 \emph{判别}。但对于推理任务，模型还需要 \emph{生成} 正确的推理轨迹。一个能判别但不能生成的模型在推理时毫无用处。RPO 在获胜回答上添加了一个 NLL（负对数似然）项，以确保模型学会生成它。
\end{intuitionbox}

The RPO loss combines DPO and SFT:

RPO 损失结合了 DPO 和 SFT：

\[
\mathcal{L}_{\text{RPO}} =
    \lambda_1 \mathcal{L}_{\text{DPO}}(y_w, y_l)
    + \lambda_2 \mathcal{L}_{\text{NLL}}(y_w),
\]

where $\mathcal{L}_{\text{NLL}}(y_w) = -\log \pi_\theta(y_w|q)$ is the standard language modelling loss on the winning response.

其中 $\mathcal{L}_{\text{NLL}}(y_w) = -\log \pi_\theta(y_w|q)$ 是在获胜回答上的标准语言建模损失。

\begin{examplebox}[Iterative RPO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


config = DPOConfig(
    loss_type="sigmoid",            # Standard DPO loss
    rpo_alpha=1.0,                  # NLL regularisation weight (RPO)
    beta=0.1,
)


trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[TRL 中的迭代 RPO]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


config = DPOConfig(
    loss_type="sigmoid",            # 标准 DPO 损失
    rpo_alpha=1.0,                  # NLL 正则化权重 (RPO)
    beta=0.1,
)


trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\begin{keybox}[When to Use RPO]
\begin{itemize}
  \item Reasoning tasks (math, code, logic) where the model must generate step-by-step solutions.
  \item When DPO training causes the model to lose fluency or generation quality.
  \item Iterative pipelines: generate rollouts, label them, train with RPO, repeat.
  \item The NLL term acts as a regulariser, preventing the policy from collapsing.
\end{itemize}
\end{keybox}

\begin{keybox}[何时使用 RPO]
\begin{itemize}
  \item 推理任务（数学、代码、逻辑），其中模型必须生成逐步的解决方案。
  \item 当 DPO 训练导致模型失去流畅性或生成质量时。
  \item 迭代流程：生成轨迹，标记它们，用 RPO 训练，重复。
  \item NLL 项起到正则化作用，防止策略崩溃。
\end{itemize}
\end{keybox}

\subsection{SimPO -- Simple Preference Optimisation}
\label{sec:simpo}

## SimPO -- Simple Preference Optimisation
## SimPO——简单偏好优化

\begin{intuitionbox}[Reference-Free Preference Learning]
DPO requires a reference model to compute the implicit reward. This doubles memory usage and adds complexity. SimPO~\cite{meng2024simpo} eliminates the reference model by using the \emph{average log-probability} of the response as an implicit reward, with a length normalisation term to prevent the model from preferring short responses.
\end{intuitionbox}

\begin{intuitionbox}[无参考模型偏好学习]
DPO 需要参考模型来计算隐式奖励。这会使内存使用翻倍并增加复杂性。SimPO~\cite{meng2024simpo} 通过使用回答的 \emph{平均对数概率} 作为隐式奖励，并加入长度归一化项来防止模型偏好短回答，从而消除了参考模型。
\end{intuitionbox}

SimPO defines the implicit reward as:

SimPO 将隐式奖励定义为：

\[
r_{\text{SimPO}}(y|q) = \frac{\beta}{|y|} \log \pi_\theta(y|q),
\]

and the loss as:

损失函数定义为：

\[
\boxed{
    \mathcal{L}_{\text{SimPO}} = -\mathbb{E}\!\left[
      \log \sigma\!\left(
        \frac{\beta}{|y_w|}\log\pi_\theta(y_w|q)
        - \frac{\beta}{|y_l|}\log\pi_\theta(y_l|q)
        - \gamma
      \right)
    \right],
  }
\]

where $\gamma > 0$ is a target reward margin that ensures the winning response has strictly higher reward than the losing response by at least $\gamma$.

其中 $\gamma > 0$ 是目标奖励边际，确保获胜回答的奖励至少比失败回答高 $\gamma$。

\begin{keybox}[SimPO vs DPO vs ORPO]
\begin{itemize}
  \item \textbf{DPO}: uses reference model; ratio-based implicit reward.
  \item \textbf{ORPO}: reference-free; adds odds-ratio term to SFT loss.
  \item \textbf{SimPO}: reference-free; length-normalised log-prob reward + margin.
  \item SimPO is simpler than DPO (no reference model) and more principled than ORPO.
  \item The length normalisation in SimPO is critical: without it, the model prefers long responses.
\end{itemize}
\end{keybox}

\begin{keybox}[SimPO vs DPO vs ORPO]
\begin{itemize}
  \item \textbf{DPO}：使用参考模型；基于比值的隐式奖励。
  \item \textbf{ORPO}：无参考模型；在 SFT 损失中添加优势比项。
  \item \textbf{SimPO}：无参考模型；长度归一化的对数概率奖励 + 边际。
  \item SimPO 比 DPO 更简单（无参考模型），且比 ORPO 更具原则性。
  \item SimPO 中的长度归一化至关重要：没有它，模型会偏好长回答。
\end{itemize}
\end{keybox}

\begin{examplebox}[SimPO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


config = DPOConfig(
    loss_type="simpo",
    simpo_gamma=0.5,   # target reward margin gamma
    beta=2.5,          # length normalisation coefficient
    # No ref_model needed!
)


trainer = DPOTrainer(
    model=model,
    ref_model=None,    # SimPO is reference-free
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[TRL 中的 SimPO]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


config = DPOConfig(
    loss_type="simpo",
    simpo_gamma=0.5,   # 目标奖励边际 gamma
    beta=2.5,          # 长度归一化系数
    # 不需要 ref_model！
)


trainer = DPOTrainer(
    model=model,
    ref_model=None,    # SimPO 是无参考模型的
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}