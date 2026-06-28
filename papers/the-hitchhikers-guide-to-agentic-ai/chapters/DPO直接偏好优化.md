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

