## Introduction to Reinforcement Learning
## 强化学习简介

Reinforcement Learning (RL) is a paradigm where an \textbf{agent} learns to make sequential decisions by interacting with an \textbf{environment}, receiving \textbf{rewards} as feedback, and optimizing its \textbf{policy} to maximize cumulative reward over time~\cite{sutton2018reinforcement}. Unlike supervised learning (which requires labeled input-output pairs), RL discovers optimal behavior through \emph{trial and error}.
Reinforcement Learning (RL，强化学习) 是一种范式，其中 \textbf{智能体 (agent)} 通过与 \textbf{环境 (environment)} 交互、接收 \textbf{奖励 (rewards)} 作为反馈，并优化其 \textbf{策略 (policy)} 以最大化随时间累积的奖励~\cite{sutton2018reinforcement}。与监督学习（需要标记的输入-输出对）不同，强化学习通过 \emph{试错 (trial and error)} 发现最优行为。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_020_fig20.png}
\caption{Reinforcement Learning overview: an agent interacts with an environment, receiving rewards as feedback and updating its policy through trial and error. Unlike supervised learning which learns from labeled pairs, RL learns what to do by maximizing reward through experience.}
\caption{强化学习概览：智能体与环境交互，接收奖励作为反馈，并通过试错更新其策略。与从标记对中学习的监督学习不同，强化学习通过经验最大化奖励来学习该做什么。}
\end{figure}

\section{The Markov Decision Process (MDP)}
\label{the-markov-decision-process-mdp}
\section{马尔可夫决策过程 (MDP)}
\label{the-markov-decision-process-mdp}

An MDP is a 5-tuple $(S, A, P, R, \gamma)$:
一个 MDP 是一个五元组 $(S, A, P, R, \gamma)$：

\begin{itemize}
  \item $S$: State space --- all possible configurations of the environment
  \item $S$: 状态空间 (state space) --- 环境的所有可能配置
  \item $A$: Action space --- all actions available to the agent
  \item $A$: 动作空间 (action space) --- 智能体可用的所有动作
  \item $P(s'|s, a)$: Transition function --- probability of reaching state $s'$ from state $s$ after taking action $a$
  \item $P(s'|s, a)$: 转移函数 (transition function) --- 在状态 $s$ 采取动作 $a$ 后到达状态 $s'$ 的概率
  \item $R(s, a, s')$: Reward function --- immediate scalar feedback for a transition
  \item $R(s, a, s')$: 奖励函数 (reward function) --- 对一次转移的即时标量反馈
  \item $\gamma \in [0, 1]$: Discount factor --- how much future rewards are valued relative to immediate ones
  \item $\gamma \in [0, 1]$: 折扣因子 (discount factor) --- 相对于即时奖励，未来奖励的重视程度
\end{itemize}

\textbf{The Markov Property}: The future depends only on the current state, not the history:
\textbf{马尔可夫性质 (Markov Property)}：未来仅取决于当前状态，而非历史：
\[
P(s_{t+1} | s_t, a_t, s_{t-1}, a_{t-1}, \ldots) = P(s_{t+1} | s_t, a_t)
\]
This makes the problem tractable.
这使得问题易于处理。

\begin{intuitionbox}[Agent-Environment Interaction Loop]
\begin{intuitionbox}[智能体-环境交互循环]
At each time step $t$:
在每个时间步 $t$：

\begin{enumerate}
  \item Agent observes state $s_t$
  \item 智能体观测状态 $s_t$
  \item Agent selects action $a_t$ according to policy $\pi(a|s)$
  \item 智能体根据策略 $\pi(a|s)$ 选择动作 $a_t$
  \item Environment transitions to $s_{t+1} \sim P(\cdot|s_t, a_t)$
  \item 环境转移到 $s_{t+1} \sim P(\cdot|s_t, a_t)$
  \item Agent receives reward $r_t = R(s_t, a_t, s_{t+1})$
  \item 智能体接收奖励 $r_t = R(s_t, a_t, s_{t+1})$
  \item Repeat until terminal state or horizon $T$
  \item 重复直到终止状态或时间范围 $T$
\end{enumerate}
\end{intuitionbox}

\section{Core Concepts and Definitions}
\label{core-concepts-and-definitions}
\section{核心概念与定义}
\label{core-concepts-and-definitions}

\textbf{Policy} $\pi(a|s)$: A mapping from states to action probabilities. Deterministic: $a = \pi(s)$. Stochastic: $a \sim \pi(\cdot|s)$.
\textbf{策略 (Policy)} $\pi(a|s)$：从状态到动作概率的映射。确定性策略：$a = \pi(s)$。随机性策略：$a \sim \pi(\cdot|s)$。

\textbf{Return} (cumulative discounted reward): 
\textbf{回报 (Return)}（累积折扣奖励）：
\begin{equation}
G_t = \sum_{k=0}^{\infty} \gamma^k r_{t+k} = r_t + \gamma r_{t+1} + \gamma^2 r_{t+2} + \cdots
\end{equation}

\textbf{Value Function} (expected return from state $s$ under policy $\pi$): 
\textbf{值函数 (Value Function)}（在策略 $\pi$ 下从状态 $s$ 开始的期望回报）：
\begin{equation}
V^\pi(s) = \mathbb{E}_\pi\left[G_t \mid s_t = s\right] = \mathbb{E}_\pi\left[\sum_{k=0}^{\infty} \gamma^k r_{t+k} \mid s_t = s\right]
\end{equation}

\textbf{Action-Value Function} (expected return from state $s$, taking action $a$, then following $\pi$): 
\textbf{动作值函数 (Action-Value Function)}（在状态 $s$ 采取动作 $a$ 后遵循策略 $\pi$ 的期望回报）：
\begin{equation}
Q^\pi(s, a) = \mathbb{E}_\pi\left[G_t \mid s_t = s, a_t = a\right]
\end{equation}

\textbf{Advantage Function} (how much better action $a$ is compared to average): 
\textbf{优势函数 (Advantage Function)}（动作 $a$ 相比平均表现好多少）：
\begin{equation}
A^\pi(s, a) = Q^\pi(s, a) - V^\pi(s)
\end{equation}

\textbf{Bellman Equations} (recursive relationship): 
\textbf{贝尔曼方程 (Bellman Equations)}（递归关系）：
\begin{align}
V^\pi(s) &= \sum_a \pi(a|s) \sum_{s'} P(s'|s,a)\left[R(s,a,s') + \gamma V^\pi(s')\right] \\
Q^\pi(s,a) &= \sum_{s'} P(s'|s,a)\left[R(s,a,s') + \gamma \sum_{a'} \pi(a'|s') Q^\pi(s', a')\right]
\end{align}

\begin{keybox}[Optimal Policy and Bellman Optimality]
\begin{keybox}[最优策略与贝尔曼最优性]
The optimal policy $\pi^*$ satisfies: 
最优策略 $\pi^*$ 满足：
\begin{equation}
V^*(s) = \max_a \sum_{s'} P(s'|s,a)\left[R(s,a,s') + \gamma V^*(s')\right]
\end{equation}
 
\begin{equation}
Q^*(s,a) = \sum_{s'} P(s'|s,a)\left[R(s,a,s') + \gamma \max_{a'} Q^*(s', a')\right]
\end{equation}
 Once $Q^*$ is known, the optimal policy is simply: $\pi^*(s) = \arg\max_a Q^*(s,a)$.
一旦 $Q^*$ 已知，最优策略即为：$\pi^*(s) = \arg\max_a Q^*(s,a)$。
\end{keybox}

\newpage
\section{Taxonomy of RL Methods}
\label{taxonomy-of-rl-methods}
\section{强化学习方法的分类}
\label{taxonomy-of-rl-methods}

Reinforcement learning algorithms can be classified along several axes. Understanding this taxonomy helps select the right approach for a given problem.
强化学习算法可以沿多个维度进行分类。理解这一分类有助于为特定问题选择正确的方法。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_021_fig21.png}
\end{figure}

\begin{keybox}[Key Taxonomy Distinctions]
\begin{keybox}[关键分类区别]
\textbf{Model-Free vs Model-Based}:
\textbf{无模型 (Model-Free) 与基于模型 (Model-Based)}：

\begin{itemize}
  \item \textbf{Model-Free}: Learn policy or value function directly from experience. No knowledge of environment dynamics. Most practical for LLMs (language dynamics are intractable to model).
  \item \textbf{无模型 (Model-Free)}：直接从经验中学习策略或值函数。对环境动态没有先验知识。对于大语言模型 (LLMs) 最为实用（语言动态难以建模）。
  \item \textbf{Model-Based}: Learn or use a model of environment transitions $P(s'|s,a)$. Can plan ahead. More sample-efficient but requires accurate model.
  \item \textbf{基于模型 (Model-Based)}：学习或使用环境转移模型 $P(s'|s,a)$。可以进行前瞻规划。样本效率更高，但需要精确的模型。
\end{itemize}

\textbf{Value-Based vs Policy-Based}:
\textbf{基于值 (Value-Based) 与基于策略 (Policy-Based)}：

\begin{itemize}
  \item \textbf{Value-Based}: Learn $Q(s,a)$ or $V(s)$, derive policy as $\arg\max_a Q(s,a)$. Works well for discrete, small action spaces (e.g., Atari). Struggles with continuous/large action spaces.
  \item \textbf{基于值 (Value-Based)}：学习 $Q(s,a)$ 或 $V(s)$，通过 $\arg\max_a Q(s,a)$ 导出策略。适用于离散、小动作空间（例如 Atari）。在连续/大动作空间上表现不佳。
  \item \textbf{Policy-Based}: Directly parameterize and optimize $\pi_\theta(a|s)$. Natural for continuous/high-dimensional action spaces. Essential for LLMs (vocabulary = 32K--128K actions).
  \item \textbf{基于策略 (Policy-Based)}：直接参数化并优化 $\pi_\theta(a|s)$。适用于连续/高维动作空间。对大语言模型至关重要（词汇表 = 32K--128K 个动作）。
  \item \textbf{Actor-Critic}: Combine both --- policy (actor) proposes actions, value function (critic) evaluates them. PPO for LLMs is actor-critic.
  \item \textbf{演员-评论家 (Actor-Critic)}：结合两者——策略（演员）提出动作，值函数（评论家）评估它们。用于大语言模型的 PPO 是演员-评论家方法。
\end{itemize}

\textbf{On-Policy vs Off-Policy}:
\textbf{同策略 (On-Policy) 与异策略 (Off-Policy)}：

\begin{itemize}
  \item \textbf{On-Policy}: Learn from data generated by the \emph{current} policy. Must regenerate data after each update. Examples: REINFORCE, PPO, A2C. More stable but less sample-efficient.
  \item \textbf{同策略 (On-Policy)}：从 \emph{当前} 策略生成的数据中学习。每次更新后必须重新生成数据。示例：REINFORCE、PPO、A2C。更稳定但样本效率较低。
  \item \textbf{Off-Policy}: Learn from data generated by \emph{any} policy (including old versions or other agents). Can reuse past experience. Examples: Q-Learning, DQN, SAC. More sample-efficient but harder to stabilize.
  \item \textbf{异策略 (Off-Policy)}：从 \emph{任意} 策略（包括旧版本或其他智能体）生成的数据中学习。可以重用过去的经验。示例：Q-Learning、DQN、SAC。样本效率更高但更难稳定。
\end{itemize}
\end{keybox}

\section{Temporal Difference (TD) Learning}
\label{temporal-difference-td-learning}
\section{时序差分 (TD) 学习}
\label{temporal-difference-td-learning}

TD learning~\cite{sutton1988learning} bootstraps --- it updates value estimates using other value estimates, without waiting for the full episode to end.
TD 学习~\cite{sutton1988learning} 采用自举 (bootstrapping) 方法——它使用其他值估计来更新当前值估计，无需等待整个回合结束。

\subsection{Understanding TD Error: ``Surprise'' as a Learning Signal}
\label{understanding-td-error-surprise-as-a-learning-signal}
\subsection{理解 TD 误差：将 “惊喜” 作为学习信号}
\label{understanding-td-error-surprise-as-a-learning-signal}

\textbf{TD error} measures the discrepancy between an agent’s \textbf{current estimate} of future reward and a \textbf{newly updated estimate} after taking one step. Put simply, it is the difference between what the agent \emph{thought} would happen and what \emph{actually} happened plus what it expects next. It represents the agent’s ``surprise.''
\textbf{TD 误差 (TD error)} 衡量智能体对未来奖励的 \textbf{当前估计} 与采取一步动作后的 \textbf{新更新估计} 之间的差异。简单来说，它是智能体 \emph{认为} 将发生的事与 \emph{实际} 发生的事加上它下一步预期之间的差距。它代表了智能体的 “惊喜”。

\begin{examplebox}[Intuition: The Driving Analogy]
\begin{examplebox}[直觉：驾驶类比]
Imagine you are driving home and expect the drive to take 30 minutes.
想象你正在开车回家，预计行程需要 30 分钟。

\begin{itemize}
  \item \textbf{The prediction}: 30 minutes total.
  \item \textbf{预测}：总共 30 分钟。
  \item \textbf{The reality shift}: After 10 minutes, you hit unexpected road construction. Your GPS updates, saying you now have 35 minutes left.
  \item \textbf{现实变化}：10 分钟后，你遇到了意外的道路施工。你的 GPS 更新，提示你现在还剩 35 分钟。
  \item \textbf{The TD Error}: Total expected time is now 45 minutes (10 elapsed + 35 remaining). The difference between new estimate (45 min) and old estimate (30 min) is a \textbf{+15 minute TD error}. You use this ``surprise'' to change your route next time.
  \item \textbf{TD 误差}：现在预期总时间为 45 分钟（已过 10 分钟 + 剩余 35 分钟）。新估计（45 分钟）与旧估计（30 分钟）之差为 \textbf{+15 分钟的 TD 误差}。你利用这个 “惊喜” 下次改变路线。
\end{itemize}

A \textbf{positive TD error} means the outcome was better than expected $\rightarrow$ boost this state’s value.\\
\textbf{正的 TD 误差} 意味着结果比预期更好 $\rightarrow$ 提高该状态的价值。\\

A \textbf{negative TD error} means it was worse than expected $\rightarrow$ lower this state’s value.
\textbf{负的 TD 误差} 意味着结果比预期更差 $\rightarrow$ 降低该状态的价值。
\end{examplebox}

\subsection{The TD Error Formula}
\label{the-td-error-formula}
\subsection{TD 误差公式}
\label{the-td-error-formula}

\begin{equation}
\boxed{\delta_t = R_{t+1} + \gamma V(S_{t+1}) - V(S_t)}
\end{equation}

\begin{itemize}
  \item $R_{t+1}$: The \textbf{immediate reward} received after taking an action.
  \item $R_{t+1}$: 采取动作后获得的 \textbf{即时奖励 (immediate reward)}。
  \item $\gamma V(S_{t+1})$: The estimated \textbf{discounted value} of the next state (what the agent expects to get from the next state onward, scaled by discount factor $\gamma$).
  \item $\gamma V(S_{t+1})$: 下一状态的估计 \textbf{折扣值 (discounted value)}（智能体预期从下一状态开始能获得的值，按折扣因子 $\gamma$ 缩放）。
  \item $V(S_t)$: The \textbf{original estimate} of the current state’s value.
  \item $V(S_t)$: 当前状态价值的 \textbf{原始估计 (original estimate)}。
\end{itemize}

The combined term $(R_{t+1} + \gamma V(S_{t+1}))$ is called the \textbf{TD Target}. Therefore: 
\begin{equation}
\text{TD Error} = \text{TD Target} - \text{Old Estimate}
\end{equation}
组合项 $(R_{t+1} + \gamma V(S_{t+1}))$ 被称为 \textbf{TD 目标 (TD Target)}。因此：
\begin{equation}
\text{TD 误差} = \text{TD 目标} - \text{旧估计}
\end{equation}

\subsection{How the Agent Uses TD Error}
\label{how-the-agent-uses-td-error}
\subsection{智能体如何使用 TD 误差}
\label{how-the-agent-uses-td-error}

The agent adjusts its value function to drive TD error toward zero: 
\begin{equation}
\boxed{V(S_t) \leftarrow V(S_t) + \alpha \cdot \delta_t}
\end{equation}
智能体调整其价值函数，使 TD 误差趋于零：
\begin{equation}
\boxed{V(S_t) \leftarrow V(S_t) + \alpha \cdot \delta_t}
\end{equation}

\begin{itemize}
  \item If $\delta_t > 0$: outcome was better than predicted $\rightarrow$ increase $V(S_t)$ so the agent seeks this state.
  \item If $\delta_t < 0$: outcome was worse than predicted $\rightarrow$ decrease $V(S_t)$ so the agent avoids this state.
  \item If $\delta_t = 0$: prediction was perfect $\rightarrow$ no update needed (convergence).
\end{itemize}
\begin{itemize}
  \item 如果 $\delta_t > 0$：结果好于预测 $\rightarrow$ 增加 $V(S_t)$，使智能体倾向于该状态。
  \item 如果 $\delta_t < 0$：结果差于预测 $\rightarrow$ 降低 $V(S_t)$，使智能体回避该状态。
  \item 如果 $\delta_t = 0$：预测完美 $\rightarrow$ 无需更新（收敛）。
\end{itemize}

\begin{intuitionbox}[TD vs Monte Carlo]
\textbf{Monte Carlo}: Wait until episode ends, use actual return $G_t$. Unbiased but high variance (one full trajectory may be unrepresentative).


\textbf{TD}: Update after every step using estimated future value $\gamma V(s_{t+1})$. Biased (depends on $V$ accuracy) but much lower variance (one-step updates, doesn’t compound noise).


\textbf{TD($\lambda$)}: Interpolate between TD(0) and Monte Carlo. $\lambda=0$: pure TD. $\lambda=1$: pure MC. This is exactly what GAE does for PPO (with $\lambda=0.95$).
\end{intuitionbox}
\begin{intuitionbox}[TD 与蒙特卡洛对比]
\textbf{蒙特卡洛 (Monte Carlo)}：等待回合结束，使用实际回报 $G_t$。无偏但方差高（单条完整轨迹可能不具有代表性）。


\textbf{TD}：每步更新，使用估计的未来值 $\gamma V(s_{t+1})$。有偏（依赖于 $V$ 的准确度），但方差低得多（单步更新，不会累积噪声）。


\textbf{TD($\lambda$)}：在 TD(0) 和蒙特卡洛之间插值。$\lambda=0$：纯 TD。$\lambda=1$：纯 MC。这正是 PPO 中 GAE 所做的（$\lambda=0.95$）。
\end{intuitionbox}

\textbf{TD Target}: $y_t = r_t + \gamma V(s_{t+1})$ --- the ``better estimate'' we move toward.
\textbf{TD 目标 (TD Target)}：$y_t = r_t + \gamma V(s_{t+1})$ --- 我们趋向的“更优估计”。

\textbf{Multi-step TD} (n-step returns): 
\begin{equation}
G_t^{(n)} = r_t + \gamma r_{t+1} + \cdots + \gamma^{n-1} r_{t+n-1} + \gamma^n V(s_{t+n})
\end{equation}
\textbf{多步 TD (Multi-step TD)}（n 步回报）：
\begin{equation}
G_t^{(n)} = r_t + \gamma r_{t+1} + \cdots + \gamma^{n-1} r_{t+n-1} + \gamma^n V(s_{t+n})
\end{equation}

\section{Q-Learning}
\label{q-learning}
\section{Q 学习 (Q-Learning)}
\label{q-learning}

Q-Learning~\cite{watkins1989learning} is the foundational \textbf{off-policy, value-based} algorithm. It learns the optimal $Q^*$ directly, regardless of the policy being followed.
Q 学习 (Q-Learning)~\cite{watkins1989learning} 是基础的 \textbf{离策略 (off-policy)、基于价值 (value-based)} 算法。它直接学习最优 $Q^*$，与当前遵循的策略无关。

\textbf{Update rule}: 
\begin{equation}
\boxed{Q(s_t, a_t) \leftarrow Q(s_t, a_t) + \alpha\left[r_t + \gamma \max_{a'} Q(s_{t+1}, a') - Q(s_t, a_t)\right]}
\end{equation}
\textbf{更新规则}：
\begin{equation}
\boxed{Q(s_t, a_t) \leftarrow Q(s_t, a_t) + \alpha\left[r_t + \gamma \max_{a'} Q(s_{t+1}, a') - Q(s_t, a_t)\right]}
\end{equation}

\begin{intuitionbox}[Why Q-Learning is Off-Policy]
The update uses $\max_{a'} Q(s_{t+1}, a')$ --- the value of the \emph{best} action at the next state, regardless of which action the agent actually took. This means the target is always computed under the optimal policy, even if the behavior policy explores randomly ($\epsilon$-greedy).


This is why Q-Learning can learn from replay buffers, demonstrations, or any source of experience. The data doesn’t need to come from the current policy.
\end{intuitionbox}
\begin{intuitionbox}[为什么 Q 学习是离策略的]
更新中使用 $\max_{a'} Q(s_{t+1}, a')$ --- 下一状态下 \emph{最优}动作的价值，无论智能体实际执行了哪个动作。这意味着目标总是在最优策略下计算的，即使行为策略是随机探索（$\epsilon$-贪婪）。


这就是为什么 Q 学习可以从回放缓冲区、演示或任何经验来源中学习。数据不必来自当前策略。
\end{intuitionbox}

\textbf{SARSA}~\cite{rummery1994online} (on-policy alternative): Uses the action \emph{actually taken} instead of the max: 
\begin{equation}
Q(s_t, a_t) \leftarrow Q(s_t, a_t) + \alpha\left[r_t + \gamma Q(s_{t+1}, a_{t+1}) - Q(s_t, a_t)\right]
\end{equation}
\textbf{SARSA}~\cite{rummery1994online}（同策略 (on-policy) 替代方案）：使用 \emph{实际执行}的动作而非最大值：
\begin{equation}
Q(s_t, a_t) \leftarrow Q(s_t, a_t) + \alpha\left[r_t + \gamma Q(s_{t+1}, a_{t+1}) - Q(s_t, a_t)\right]
\end{equation}

\textbf{Deep Q-Networks (DQN)}~\cite{mnih2015human}: Replace tabular $Q(s,a)$ with a neural network $Q_\theta(s,a)$. Key innovations: experience replay buffer (off-policy data reuse), target network (stability), $\epsilon$-greedy exploration.
\textbf{深度 Q 网络 (Deep Q-Networks, DQN)}~\cite{mnih2015human}：将表格型 $Q(s,a)$ 替换为神经网络 $Q_\theta(s,a)$。关键创新：经验回放缓冲区 (experience replay buffer)（离策略数据复用）、目标网络 (target network)（稳定性）、$\epsilon$-贪婪探索。

\textbf{DQN Loss Function}: The network is trained to minimize the mean squared TD error over mini-batches sampled from the replay buffer: 
\begin{equation}
\boxed{\mathcal{L}(\theta) = \mathbb{E}_{(s,a,r,s') \sim \mathcal{B}}\!\left[\left(r + \gamma \max_{a'} Q_{\bar{\theta}}(s', a') - Q_\theta(s, a)\right)^2\right]}
\end{equation}
\textbf{DQN 损失函数}：网络被训练以最小化从回放缓冲区采样的 mini-batch 上的均方 TD 误差：
\begin{equation}
\boxed{\mathcal{L}(\theta) = \mathbb{E}_{(s,a,r,s') \sim \mathcal{B}}\!\left[\left(r + \gamma \max_{a'} Q_{\bar{\theta}}(s', a') - Q_\theta(s, a)\right)^2\right]}
\end{equation}

where $Q_{\bar{\theta}}$ is the \textbf{target network} --- a frozen copy of $Q_\theta$ updated only every $C$ steps (e.g., $C = 10{,}000$). This prevents the moving target problem: without it, both the prediction and the target shift simultaneously, causing divergence.
其中 $Q_{\bar{\theta}}$ 是 \textbf{目标网络 (target network)} --- $Q_\theta$ 的冻结副本，仅每 $C$ 步更新一次（例如 $C = 10{,}000$）。这防止了移动目标问题：没有它，预测和目标会同时移动，导致发散。

\textbf{Gradient update}: Taking the gradient of the loss w.r.t. $\theta$ (note: the target $y$ is treated as a constant --- no gradient flows through $\bar{\theta}$): 
\begin{equation}
\nabla_\theta \mathcal{L} = -\mathbb{E}\!\left[\underbrace{\left(r + \gamma \max_{a'} Q_{\bar{\theta}}(s', a') - Q_\theta(s, a)\right)}_{\text{TD error } \delta}\; \nabla_\theta Q_\theta(s, a)\right]
\end{equation}
 
\begin{equation}
\theta \leftarrow \theta - \alpha \cdot \delta \cdot \nabla_\theta Q_\theta(s, a)
\end{equation}
\textbf{梯度更新}：对损失关于 $\theta$ 求梯度（注意：目标 $y$ 被视为常数 --- 梯度不通过 $\bar{\theta}$ 传播）：
\begin{equation}
\nabla_\theta \mathcal{L} = -\mathbb{E}\!\left[\underbrace{\left(r + \gamma \max_{a'} Q_{\bar{\theta}}(s', a') - Q_\theta(s, a)\right)}_{\text{TD 误差 } \delta}\; \nabla_\theta Q_\theta(s, a)\right]
\end{equation}
 
\begin{equation}
\theta \leftarrow \theta - \alpha \cdot \delta \cdot \nabla_\theta Q_\theta(s, a)
\end{equation}

\textbf{Learning scheme} (per training step):
\textbf{学习方案}（每训练步）：

\begin{enumerate}
  \item \textbf{Act}: Select action via $\epsilon$-greedy: with probability $\epsilon$ take random action, otherwise $a = \arg\max_a Q_\theta(s, a)$. Anneal $\epsilon$ from 1.0 $\rightarrow$ 0.01 over first 1M steps.
  \item \textbf{Store}: Save transition $(s, a, r, s', d)$ in replay buffer $\mathcal{B}$ (capacity $\sim$1M).
  \item \textbf{Sample}: Draw mini-batch of 32 transitions uniformly from $\mathcal{B}$.
  \item \textbf{Compute target}: $y = r + \gamma(1 - d)\max_{a'} Q_{\bar{\theta}}(s', a')$ (zero future value if terminal).
  \item \textbf{Update}: Gradient descent on $(y - Q_\theta(s,a))^2$. Clip gradients to $[-1, 1]$ (Huber loss variant).
  \item \textbf{Sync target}: Every $C$ steps, copy $\bar{\theta} \leftarrow \theta$.
\end{enumerate}
\begin{enumerate}
  \item \textbf{动作 (Act)}：通过 $\epsilon$-贪婪选择动作：以概率 $\epsilon$ 采取随机动作，否则 $a = \arg\max_a Q_\theta(s, a)$。在前 1M 步中将 $\epsilon$ 从 1.0 退火到 0.01。
  \item \textbf{存储 (Store)}：将转移 $(s, a, r, s', d)$ 保存到回放缓冲区 $\mathcal{B}$（容量 $\sim$1M）。
  \item \textbf{采样 (Sample)}：从 $\mathcal{B}$ 中均匀抽取 32 个转移的 mini-batch。
  \item \textbf{计算目标 (Compute target)}：$y = r + \gamma(1 - d)\max_{a'} Q_{\bar{\theta}}(s', a')$（如果是终止状态，未来价值为零）。
  \item \textbf{更新 (Update)}：对 $(y - Q_\theta(s,a))^2$ 进行梯度下降。将梯度裁剪到 $[-1, 1]$（Huber 损失变体）。
  \item \textbf{同步目标 (Sync target)}：每 $C$ 步，复制 $\bar{\theta} \leftarrow \theta$。
\end{enumerate}

\subsection{Understanding Replay Buffers}
\label{understanding-replay-buffers}
\subsection{理解回放缓冲区}
\label{understanding-replay-buffers}

A \textbf{replay buffer}~\cite{lin1992self} (experience replay) is a data storage mechanism that saves past experiences so an agent can relearn from them later. Instead of discarding data immediately after an action, the agent stores transitions in a memory bank and samples random mini-batches for training.
\textbf{回放缓冲区 (replay buffer)}~\cite{lin1992self}（经验回放）是一种数据存储机制，用于保存过去的经验，以便智能体随后可以从中重新学习。智能体不会在动作后立即丢弃数据，而是将转移存储在记忆库中，并采样随机 mini-batch 进行训练。

\textbf{What’s stored}: Each transition is a tuple: 
\begin{equation}
e_t = (s_t, a_t, r_t, s_{t+1}, d_t)
\end{equation}
 where $d_t$ is a boolean flag indicating if the episode ended.
\textbf{存储内容}：每个转移是一个元组：
\begin{equation}
e_t = (s_t, a_t, r_t, s_{t+1}, d_t)
\end{equation}
其中 $d_t$ 是一个布尔标志，指示回合是否结束。

\begin{keybox}[Why Replay Buffers Are Essential]
\begin{itemize}
  \item \textbf{Breaks data correlation}: Consecutive steps are highly correlated. Neural networks generalize poorly on sequential data. Random sampling from a buffer makes training samples approximately i.i.d.
  \item \textbf{Prevents catastrophic forgetting}: Without a buffer, an agent that passes a difficult level might forget how to clear it while spending the next 10K steps failing on a later level. The buffer ensures it continues to practice old scenarios.
  \item \textbf{Improves sample efficiency}: Running environments can be slow. A replay buffer allows multiple weight updates from the same transition, extracting more value from every step.
\end{itemize}
\end{keybox}
\begin{keybox}[为什么回放缓冲区至关重要]
\begin{itemize}
  \item \textbf{打破数据相关性}：连续步骤高度相关。神经网络在序列数据上泛化较差。从缓冲区随机采样使训练样本近似独立同分布。
  \item \textbf{防止灾难性遗忘}：如果没有缓冲区，通过某个困难关卡的智能体可能会在接下来 1 万步中失败于后续关卡时忘记如何通过前一关卡。缓冲区确保它继续练习旧场景。
  \item \textbf{提高样本效率}：运行环境可能很慢。回放缓冲区允许从同一转移进行多次权重更新，从每一步提取更多价值。
\end{itemize}
\end{keybox}

\begin{lstlisting}[style=pythonstyle]
import random
from collections import deque


class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)  # Bounded queue
    
    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
        
    def sample(self, batch_size):
        # Break correlation by selecting random experiences
        return random.sample(self.buffer, batch_size)
        
    def __len__(self):
        return len(self.buffer)
\end{lstlisting}
\begin{lstlisting}[style=pythonstyle]
import random
from collections import deque


class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)  # 有界队列
    
    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
        
    def sample(self, batch_size):
        # 通过选择随机经验来打破相关性
        return random.sample(self.buffer, batch_size)
        
    def __len__(self):
        return len(self.buffer)
\end{lstlisting}

\begin{intuitionbox}[Prioritized Experience Replay (PER)]
In a standard buffer, all experiences have equal sampling probability. But some are much more educational. \textbf{PER}~\cite{schaul2016prioritized} scales sampling probability by \textbf{TD error magnitude} --- if a transition caused massive ``surprise'' (high $|\delta_t|$), the agent samples it more frequently to correct its model faster. This accelerates learning by 2--3$\times$ on Atari benchmarks.
\end{intuitionbox}
\begin{intuitionbox}[优先经验回放 (Prioritized Experience Replay, PER)]
在标准缓冲区中，所有经验具有相同的采样概率。但有些经验更具有教育意义。\textbf{PER}~\cite{schaul2016prioritized} 根据 \textbf{TD 误差幅度} 缩放采样概率 --- 如果某次转移造成了巨大的“意外”（高 $|\delta_t|$），智能体更频繁地采样它以更快地修正其模型。在 Atari 基准测试上，这可将学习速度提升 2--3 倍。
\end{intuitionbox}

\begin{warningbox}[Why Q-Learning Fails for LLMs]
The action space in language generation is the full vocabulary ($|A| = 32\text{K}$--$128\text{K}$), and the state space is all possible token sequences (infinite). Computing $\max_a Q(s,a)$ over 128K actions at every token position is intractable. This is why LLM RL uses \textbf{policy-based} methods (PPO, GRPO) instead.
\end{warningbox}
\begin{warningbox}[为什么 Q 学习不适用于大语言模型]
语言生成中的动作空间是整个词汇表（$|A| = 32\text{K}$--$128\text{K}$），状态空间是所有可能的 token 序列（无限）。在每个 token 位置计算 128K 个动作上的 $\max_a Q(s,a)$ 是不可行的。这就是为什么大语言模型强化学习使用 \textbf{基于策略 (policy-based)} 的方法（PPO、GRPO）的原因。
\end{warningbox}

\newpage
\section{Policy Gradient Methods --- REINFORCE}
\label{policy-gradient-methods-reinforce}
\newpage
\section{策略梯度方法 --- REINFORCE}
\label{policy-gradient-methods-reinforce}

Instead of learning a value function and deriving a policy, directly optimize the policy parameters $\theta$ to maximize expected return~\cite{williams1992simple}.
不学习价值函数并推导策略，而是直接优化策略参数 $\theta$ 以最大化期望回报~\cite{williams1992simple}。

\textbf{Objective}: $J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}[R(\tau)] = \mathbb{E}_{\pi_\theta}\left[\sum_{t=0}^T r_t\right]$
\textbf{目标}：$J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}[R(\tau)] = \mathbb{E}_{\pi_\theta}\left[\sum_{t=0}^T r_t\right]$

\textbf{Policy Gradient Theorem}: 
\textbf{策略梯度定理}：
\begin{equation}
\boxed{\nabla_\theta J(\theta) = \mathbb{E}_{\pi_\theta}\left[\sum_{t=0}^T \nabla_\theta \log \pi_\theta(a_t|s_t) \cdot G_t\right]}
\end{equation}

\begin{keybox}[Policy Gradient Theorem — Formal Derivation (5 Steps)]
\begin{keybox}[策略梯度定理——正式推导（5步）]

\textbf{Step 1}: Define the objective. We want to maximize expected return: 
\textbf{第1步}：定义目标。我们希望最大化期望回报：
\[
J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}\!\left[\sum_{t=0}^T r_t\right] = \sum_\tau P(\tau|\theta) R(\tau)
\]
 where $P(\tau|\theta) = p(s_0)\prod_{t=0}^T \pi_\theta(a_t|s_t)\, p(s_{t+1}|s_t, a_t)$ is the trajectory probability.
其中 $P(\tau|\theta) = p(s_0)\prod_{t=0}^T \pi_\theta(a_t|s_t)\, p(s_{t+1}|s_t, a_t)$ 是轨迹概率。

\textbf{Step 2}: Take the gradient. Only $\pi_\theta$ terms depend on $\theta$ (dynamics $p$ doesn’t): 
\textbf{第2步}：求梯度。只有 $\pi_\theta$ 项依赖于 $\theta$（动力学 $p$ 不依赖）：
\[
\nabla_\theta J = \sum_\tau \nabla_\theta P(\tau|\theta)\, R(\tau)
\]

\textbf{Step 3}: Apply the \textbf{log-derivative trick}: $\nabla_\theta P(\tau|\theta) = P(\tau|\theta)\, \nabla_\theta \log P(\tau|\theta)$: 
\textbf{第3步}：应用 \textbf{对数导数技巧}：$\nabla_\theta P(\tau|\theta) = P(\tau|\theta)\, \nabla_\theta \log P(\tau|\theta)$：
\[
\nabla_\theta J = \mathbb{E}_{\tau \sim \pi_\theta}\!\left[\nabla_\theta \log P(\tau|\theta)\, R(\tau)\right]
\]

\textbf{Step 4}: Expand $\log P(\tau|\theta)$. The $\log p(s_0)$ and $\log p(s_{t+1}|s_t,a_t)$ terms vanish under $\nabla_\theta$: 
\textbf{第4步}：展开 $\log P(\tau|\theta)$。$\log p(s_0)$ 和 $\log p(s_{t+1}|s_t,a_t)$ 项在 $\nabla_\theta$ 下消失：
\[
\nabla_\theta \log P(\tau|\theta) = \sum_{t=0}^T \nabla_\theta \log \pi_\theta(a_t|s_t)
\]

\textbf{Step 5}: Combine. Future rewards don’t depend on past actions (causality), so each $\nabla\log\pi$ pairs only with future return $G_t = \sum_{t'=t}^T r_{t'}$: 
\textbf{第5步}：合并。未来奖励不依赖于过去动作（因果性），因此每个 $\nabla\log\pi$ 仅与未来回报 $G_t = \sum_{t'=t}^T r_{t'}$ 配对：
\[
\boxed{\nabla_\theta J = \mathbb{E}_{\pi_\theta}\!\left[\sum_{t=0}^T \nabla_\theta \log \pi_\theta(a_t|s_t) \cdot G_t\right]}
\]
\end{keybox}

\begin{intuitionbox}[Why This Is Beautiful]
\begin{intuitionbox}[为什么这很优美]

The gradient does \textbf{not require differentiating through the environment dynamics} $p(s'|s,a)$. The log-derivative trick converts it into an expectation we can estimate by simply \emph{running the policy and observing rewards}. Replacing $G_t$ with advantage $\hat{A}_t = G_t - V(s_t)$ reduces variance without bias (since $\mathbb{E}[\nabla\log\pi \cdot b(s)] = 0$ for any state-dependent baseline).
该梯度\textbf{不需要对环境的动力学} $p(s'|s,a)$ \textbf{求导}。对数导数技巧将其转化为一个我们可以通过简单\emph{运行策略并观察奖励}来估计的期望。将 $G_t$ 替换为优势函数 $\hat{A}_t = G_t - V(s_t)$ 可以在不引入偏差的情况下降低方差（因为对于任何依赖于状态的基线 $b(s)$，有 $\mathbb{E}[\nabla\log\pi \cdot b(s)] = 0$）。
\end{intuitionbox}

\textbf{REINFORCE Algorithm}~\cite{williams1992simple} (Williams, 1992):
\textbf{REINFORCE算法}~\cite{williams1992simple}（Williams, 1992）：

\begin{enumerate}
  \item Sample complete trajectory $\tau = (s_0, a_0, r_0, s_1, a_1, r_1, \ldots)$ under $\pi_\theta$
  \item 在 $\pi_\theta$ 下采样完整轨迹 $\tau = (s_0, a_0, r_0, s_1, a_1, r_1, \ldots)$
  \item Compute return $G_t = \sum_{k=0}^{T-t} \gamma^k r_{t+k}$ for each time step
  \item 对每个时间步计算回报 $G_t = \sum_{k=0}^{T-t} \gamma^k r_{t+k}$
  \item Update: $\theta \leftarrow \theta + \alpha \sum_t \nabla_\theta \log \pi_\theta(a_t|s_t) \cdot G_t$
  \item 更新：$\theta \leftarrow \theta + \alpha \sum_t \nabla_\theta \log \pi_\theta(a_t|s_t) \cdot G_t$
\end{enumerate}

\begin{intuitionbox}[REINFORCE Intuition — ``Reward-Weighted Maximum Likelihood'']
\begin{intuitionbox}[REINFORCE 直觉——“奖励加权最大似然”]

$\nabla_\theta \log \pi_\theta(a_t|s_t)$ is the direction that increases the probability of action $a_t$. Multiplying by $G_t$ means:
$\nabla_\theta \log \pi_\theta(a_t|s_t)$ 是增加动作 $a_t$ 概率的方向。乘以 $G_t$ 意味着：

\begin{itemize}
  \item High-reward trajectories: increase probability of all actions taken (positive $G_t$)
  \item 高奖励轨迹：增加所有已执行动作的概率（正 $G_t$）
  \item Low-reward trajectories: decrease probability of actions taken (negative $G_t$ after baseline)
  \item 低奖励轨迹：减少已执行动作的概率（基线处理后为负 $G_t$）
\end{itemize}

It’s supervised learning where the ``labels'' are the actions you took, weighted by how good they turned out to be.
这就像监督学习，其中“标签”是你实际采取的动作，权重由它们最终表现的好坏决定。
\end{intuitionbox}

\textbf{Variance Reduction with Baseline}: 
\textbf{使用基线降低方差}：
\begin{equation}
\nabla_\theta J(\theta) = \mathbb{E}_{\pi_\theta}\left[\sum_{t=0}^T \nabla_\theta \log \pi_\theta(a_t|s_t) \cdot (G_t - b(s_t))\right]
\end{equation}
 Any baseline $b(s_t)$ that doesn’t depend on $a_t$ keeps the gradient unbiased but reduces variance. Best choice: $b(s_t) = V^\pi(s_t)$. Then $G_t - V(s_t) \approx A^\pi(s_t, a_t)$ = advantage.
任何不依赖于 $a_t$ 的基线 $b(s_t)$ 都能保持梯度无偏但降低方差。最佳选择：$b(s_t) = V^\pi(s_t)$。此时 $G_t - V(s_t) \approx A^\pi(s_t, a_t)$ = 优势。

\begin{warningbox}[REINFORCE Limitations]
\begin{warningbox}[REINFORCE 局限性]

\begin{itemize}
  \item \textbf{High variance}: Each gradient uses one trajectory. Thousands of samples needed for stable updates.
  \item \textbf{方差高}：每个梯度使用一个轨迹。需要数千个样本才能实现稳定更新。
  \item \textbf{No bootstrapping}: Must wait for full episode (no partial credit).
  \item \textbf{无自助法（Bootstrapping）}：必须等待完整回合（无法提前部分评估）。
  \item \textbf{Sample inefficient}: Data is used once then discarded (on-policy).
  \item \textbf{样本效率低}：数据只使用一次即丢弃（在线策略）。
  \item \textbf{No step-size control}: Can take catastrophically large policy steps.
  \item \textbf{无步长控制}：可能导致策略步长过大，造成灾难性后果。
\end{itemize}

These limitations motivate the progression: REINFORCE $\to$ Actor-Critic $\to$ TRPO $\to$ \textbf{PPO}.
这些局限性推动了以下演进：REINFORCE $\to$ Actor-Critic $\to$ TRPO $\to$ \textbf{PPO}。
\end{warningbox}

\section{Actor-Critic Methods}
\section{Actor-Critic 方法}
\label{actor-critic-methods}

Combine policy gradient (actor) with learned value function (critic) to reduce variance while maintaining the flexibility of policy optimization.
将策略梯度（Actor）与学习到的价值函数（Critic）相结合，以降低方差，同时保持策略优化的灵活性。

\textbf{Architecture}:
\textbf{架构}：

\begin{itemize}
  \item \textbf{Actor} $\pi_\theta(a|s)$: The policy. Proposes actions.
  \item \textbf{Actor} $\pi_\theta(a|s)$：策略。提出动作。
  \item \textbf{Critic} $V_\phi(s)$ or $Q_\phi(s,a)$: Evaluates how good a state/action is. Provides low-variance baseline.
  \item \textbf{Critic} $V_\phi(s)$ 或 $Q_\phi(s,a)$：评估状态/动作的好坏。提供低方差基线。
\end{itemize}

\textbf{Actor update} (using advantage from critic): 
\textbf{Actor 更新}（使用来自 Critic 的优势）：
\begin{equation}
\nabla_\theta J = \mathbb{E}\left[\nabla_\theta \log \pi_\theta(a_t|s_t) \cdot \hat{A}_t\right], \quad \hat{A}_t = r_t + \gamma V_\phi(s_{t+1}) - V_\phi(s_t)
\end{equation}

\textbf{Critic update} (minimize TD error): 
\textbf{Critic 更新}（最小化 TD 误差）：
\begin{equation}
\mathcal{L}_\text{critic} = \mathbb{E}\left[(r_t + \gamma V_\phi(s_{t+1}) - V_\phi(s_t))^2\right]
\end{equation}

\begin{keybox}[Evolution to PPO for LLMs]
\begin{keybox}[面向大语言模型（LLM）的 PPO 演进]

\begin{enumerate}
  \item \textbf{REINFORCE}~\cite{williams1992simple}: High variance, no bootstrapping $\rightarrow$ impractical for LLMs
  \item \textbf{REINFORCE}~\cite{williams1992simple}：方差高，无自助法 $\rightarrow$ 不适用于 LLM
  \item \textbf{A2C/A3C}~\cite{mnih2016asynchronous} (Advantage Actor-Critic): Uses TD-based advantage. Lower variance. But unbounded step sizes.
  \item \textbf{A2C/A3C}~\cite{mnih2016asynchronous}（优势 Actor-Critic）：使用基于 TD 的优势。方差较低。但步长无界。
  \item \textbf{TRPO}~\cite{schulman2015trust}: Constrains KL divergence between policy updates. Stable but expensive (second-order).
  \item \textbf{TRPO}~\cite{schulman2015trust}：约束策略更新之间的 KL 散度。稳定但计算成本高（二阶）。
  \item \textbf{PPO}~\cite{schulman2017proximal}: Clips the policy ratio to achieve similar stability as TRPO with first-order optimization only. The standard for LLM RL training.
  \item \textbf{PPO}~\cite{schulman2017proximal}：裁剪策略比率，仅用一阶优化即可达到与 TRPO 相似的稳定性。LLM 强化学习训练的标准方法。
  \item \textbf{GRPO}: Removes the critic entirely. Uses group statistics as baseline. Simpler and effective for verifiable rewards.
  \item \textbf{GRPO}：完全移除 Critic。使用组统计量作为基线。更简单，对可验证奖励有效。
\end{enumerate}
\end{keybox}

\section{Generalized Advantage Estimation (GAE)}
\section{广义优势估计（GAE）}
\label{generalized-advantage-estimation-gae}

\textbf{Motivation}: The Actor-Critic framework needs a good estimate of the advantage $A(s,a) = Q(s,a) - V(s)$ --- how much better was this action than average? But there’s a fundamental tension:
\textbf{动机}：Actor-Critic 框架需要一个好的优势估计 $A(s,a) = Q(s,a) - V(s)$ —— 这个动作比平均水平好多少？但存在一个根本性的矛盾：

\begin{itemize}
  \item \textbf{1-step TD advantage} ($r_t + \gamma V(s_{t+1}) - V(s_t)$): Low variance (only one random step), but \textbf{biased} --- if the value function $V$ is wrong, the advantage estimate is systematically off.
  \item \textbf{1步TD优势}（$r_t + \gamma V(s_{t+1}) - V(s_t)$）：方差低（仅一个随机步），但\textbf{有偏}——如果价值函数 $V$ 有误，优势估计会系统性地偏离。
  \item \textbf{Monte Carlo advantage} ($G_t - V(s_t)$): Unbiased (uses actual returns), but \textbf{high variance} --- the sum of many random rewards fluctuates wildly between episodes.
  \item \textbf{蒙特卡洛优势}（$G_t - V(s_t)$）：无偏（使用实际回报），但\textbf{方差高}——许多随机奖励的和在不同回合间波动剧烈。
\end{itemize}

GAE~\cite{schulman2016high} (Schulman et al., 2016) provides a \textbf{smooth interpolation} between these extremes via a single parameter $\lambda \in [0, 1]$. It takes an exponentially-weighted average of $n$-step advantage estimates for all $n$, giving a principled way to trade bias for variance.
GAE~\cite{schulman2016high}（Schulman 等人，2016）通过一个参数 $\lambda \in [0, 1]$ 提供了这些极端情况之间的\textbf{平滑插值}。它对所有 $n$ 步优势估计取指数加权平均，提供了一个在有偏性与方差之间进行权衡的 principled 方法。

\textbf{Core idea}: Compute the 1-step TD error $\delta_t$ at each timestep, then blend them with exponentially decaying weights $(\gamma\lambda)^l$ --- recent TD errors get full weight, distant ones are down-weighted:
\textbf{核心思想}：在每个时间步计算1步TD误差 $\delta_t$，然后用指数衰减权重 $(\gamma\lambda)^l$ 将它们混合——最近的 TD 误差获得全权重，较远的被降权：

\begin{equation}
\boxed{\hat{A}_t^{\text{GAE}} = \sum_{l=0}^{T-t} (\gamma\lambda)^l \delta_{t+l}, \quad \delta_t = r_t + \gamma V(s_{t+1}) - V(s_t)}
\end{equation}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_022_fig22.png}
\caption{GAE data flow: each TD residual $\delta_{t+l}^V$ is weighted by $(\gamma\lambda)^l$ before summation. Higher $\lambda$ includes more future residuals (lower bias, higher variance).}
\caption{GAE 数据流：每个 TD 残差 $\delta_{t+l}^V$ 在求和前乘以 $(\gamma\lambda)^l$ 权重。$\lambda$ 越大，包含的未来残差越多（偏差越低，方差越高）。}
\end{figure}

\begin{intuitionbox}[What $\lambda$ Controls --- Bias-Variance Tradeoff]
\begin{itemize}
  \item $\lambda = 0$: $\hat{A}_t = \delta_t = r_t + \gamma V(s_{t+1}) - V(s_t)$. Trust value function completely. Low variance, but biased if $V$ is inaccurate.
  \item $\lambda = 1$: $\hat{A}_t = \sum_l \gamma^l r_{t+l} - V(s_t)$. Full Monte Carlo return minus baseline. Unbiased but very high variance.
  \item $\lambda = 0.95$ (standard): Sweet spot. Mostly trusts $V$ but corrects with actual returns for distant effects. Works because value head becomes accurate after initial training.
\end{itemize}

For LLMs specifically: $\gamma = 1.0$ (no time discounting --- all tokens matter equally in single-turn), $\lambda = 0.95$.
\end{intuitionbox}

\begin{intuitionbox}[$\lambda$ 控制什么——偏差-方差权衡]
\begin{itemize}
  \item $\lambda = 0$: $\hat{A}_t = \delta_t = r_t + \gamma V(s_{t+1}) - V(s_t)$。完全信任价值函数。方差低，但如果 $V$ 不准确则有偏。
  \item $\lambda = 1$: $\hat{A}_t = \sum_l \gamma^l r_{t+l} - V(s_t)$。完整蒙特卡洛回报减去基线。无偏但方差非常高。
  \item $\lambda = 0.95$（标准）：最佳点。主要信任 $V$，但用实际回报修正远期效应。因为价值头在初始训练后变得准确，所以有效。
\end{itemize}

对于LLM而言具体设置：$\gamma = 1.0$（无时间折扣——在单轮对话中所有token同等重要），$\lambda = 0.95$。
\end{intuitionbox}

\subsection{Intuitive Mapping of Bias and Variance in GAE}
\label{intuitive-mapping-of-bias-and-variance-in-gae}

\subsection{GAE中偏差与方差的直观映射}
\label{intuitive-mapping-of-bias-and-variance-in-gae}

In supervised learning, bias and variance stem from structural model assumptions. In reinforcement learning via GAE, they stem from \textbf{how much you trust a flawed model versus how much you trust a chaotic environment}:

在监督学习中，偏差和方差源于结构性的模型假设。在通过GAE进行强化学习时，它们源于\textbf{你多大程度上信任一个有缺陷的模型，以及多大程度上信任一个混乱的环境}：

\begin{itemize}
  \item \textbf{Bias (Systemic Misalignment):} Arises when the estimator relies on the structural assumptions and imperfect predictions of the value network $V_\theta$. If $\theta$ is under-trained or lacks capacity, the baseline guesses are systematically wrong.
  \item \textbf{Variance (Sample Jitteriness):} Arises when the estimator relies on long, unconstrained environmental trajectories. Stochastic transitions, random seeds, and policy execution noise accumulate over long horizons, causing empirical sample rewards to swing wildly between rollouts.
\end{itemize}

\begin{itemize}
  \item \textbf{偏差（系统性错位）}：当估计器依赖于价值网络 $V_\theta$ 的结构性假设和不完美预测时产生。如果 $\theta$ 训练不足或容量不足，基线猜测会系统性地错误。
  \item \textbf{方差（样本抖动性）}：当估计器依赖于长程、无约束的环境轨迹时产生。随机转移、随机种子和策略执行噪声在长时序上积累，导致经验样本奖励在不同回合之间剧烈波动。
\end{itemize}

\subsection{The Architectural Spectrum: Boundary Analysis}
\label{the-architectural-spectrum-boundary-analysis}

\subsection{架构谱系：边界分析}
\label{the-architectural-spectrum-boundary-analysis}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_023_fig23.png}
\caption{Bias vs. Variance in GAE: $\lambda$ controls the trade-off. Small $\lambda$ (left) yields high bias / low variance via bootstrapping; large $\lambda$ (right) yields low bias / high variance using full Monte Carlo returns. The optimal choice ($\lambda \in [0.9, 0.95]$) balances stable training with accurate long-horizon credit assignment.}
\end{figure}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_023_fig23.png}
\caption{GAE中的偏差与方差：$\lambda$ 控制权衡。小 $\lambda$（左）通过自举产生高偏差/低方差；大 $\lambda$（右）使用完整蒙特卡洛回报产生低偏差/高方差。最优选择（$\lambda \in [0.9, 0.95]$）平衡了稳定训练与准确的长期信用分配。}
\end{figure}

The hyperparameter $\lambda$ serves as a slide-rule between two fundamental estimation paradigms.

超参数 $\lambda$ 充当两种基本估计范式之间的计算尺。

\begin{keybox}[High Bias / Low Variance Limit ($\lambda = 0$)]
\begin{equation}
\hat{A}_t^{\text{GAE}(\gamma, 0)} = \delta_t^V = r_t + \gamma V_\theta(s_{t+1}) - V_\theta(s_t)
\end{equation}

\begin{keybox}[高偏差/低方差极限（$\lambda = 0$）]
\begin{equation}
\hat{A}_t^{\text{GAE}(\gamma, 0)} = \delta_t^V = r_t + \gamma V_\theta(s_{t+1}) - V_\theta(s_t)
\end{equation}

\begin{itemize}
  \item \textbf{Behavior}: The advantage is heavily dictated by the current state of parameters $\theta$.
  \item \textbf{Intuition}: Highly \textbf{biased} because the network is grading its own performance over a 1-step window; if $V_\theta$ is inaccurate, the gradient step is corrupted. Low \textbf{variance} because it ignores future stochastic events beyond step $t+1$, leading to smooth, stable parameter updates.
  \item \textbf{Risk}: Policy traps in sub-optimal local minima --- never discovers complex delayed reward sequences.
\end{itemize}
\end{keybox}

\begin{itemize}
  \item \textbf{行为}：优势高度依赖于参数 $\theta$ 的当前状态。
  \item \textbf{直觉}：高度\textbf{有偏}，因为网络在一步窗口内评估自身表现；如果 $V_\theta$ 不准确，梯度步长就会被破坏。低\textbf{方差}，因为它忽略了 $t+1$ 步之后的未来随机事件，导致参数更新平滑稳定。
  \item \textbf{风险}：策略陷入次优局部最小值——永远无法发现复杂的延迟奖励序列。
\end{itemize}
\end{keybox}

\begin{keybox}[Low Bias / High Variance Limit ($\lambda = 1$)]
When $\lambda = 1$, intermediate value terms telescopically cancel, reducing GAE to Monte Carlo return minus baseline: 
\begin{equation}
\hat{A}_t^{\text{GAE}(\gamma, 1)} = \sum_{l=0}^{\infty} \gamma^l r_{t+l} - V_\theta(s_t)
\end{equation}

\begin{keybox}[低偏差/高方差极限（$\lambda = 1$）]
当 $\lambda = 1$ 时，中间价值项通过伸缩抵消，将GAE简化为蒙特卡洛回报减去基线：
\begin{equation}
\hat{A}_t^{\text{GAE}(\gamma, 1)} = \sum_{l=0}^{\infty} \gamma^l r_{t+l} - V_\theta(s_t)
\end{equation}

\begin{itemize}
  \item \textbf{Behavior}: Discards bootstrap look-aheads and sums up the literal reality of the entire episode.
  \item \textbf{Intuition}: Completely \textbf{unbiased} with respect to true environment dynamics --- measures actual rewards instead of neural approximations. However, exhibits extreme \textbf{variance}: minor perturbations early in an episode can result in completely divergent total returns, causing policy updates to become erratic.
  \item \textbf{Risk}: Destructive gradient updates; training explosions.
\end{itemize}
\end{keybox}

\begin{itemize}
  \item \textbf{行为}：丢弃自举前向展开，直接求和整个回合的直观现实。
  \item \textbf{直觉}：相对于真实环境动态完全\textbf{无偏}——测量实际奖励而非神经网络近似。然而，表现出极端\textbf{方差}：一个回合早期的微小扰动可能导致完全发散的总回报，使策略更新变得不稳定。
  \item \textbf{风险}：破坏性梯度更新；训练崩溃。
\end{itemize}
\end{keybox}

\subsection{The Trade-off Matrix}
\label{the-trade-off-matrix}

\subsection{权衡矩阵}
\label{the-trade-off-matrix}

By selecting $\lambda \in [0.95, 0.99]$, GAE minimizes the total mean squared error of the advantage estimate:

通过选择 $\lambda \in [0.95, 0.99]$，GAE最小化优势估计的总均方误差：

\begin{table}[ht!]
\centering
\caption{Operational comparison of GAE parameter choices.}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{Configuration} & \textbf{Statistical Properties} & \textbf{Core Reliance} & \textbf{Practical Risk} \\
\midrule
$\lambda = 0$ & High Bias, Low Variance & Model parameters ($\theta$) & Policy traps in sub-optimal local minima \\
$\lambda \in [0.95, 0.99]$ & Balanced (Optimal MSE) & Hybrid blending & Requires tuning based on environment stochasticity \\
$\lambda = 1$ & Low Bias, High Variance & Empirical environment rollout & Destructive gradient updates; training explosion \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[ht!]
\centering
\caption{GAE参数选择的操作性对比。}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{配置} & \textbf{统计特性} & \textbf{核心依赖} & \textbf{实际风险} \\
\midrule
$\lambda = 0$ & 高偏差，低方差 & 模型参数 ($\theta$) & 策略陷入次优局部最小值 \\
$\lambda \in [0.95, 0.99]$ & 平衡（最优MSE） & 混合融合 & 需要根据环境随机性进行调参 \\
$\lambda = 1$ & 低偏差，高方差 & 经验环境 rollout & 破坏性梯度更新；训练崩溃 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Diagnostics for Tuning $\lambda$}
\label{diagnostics-for-tuning-lambda}

\subsection{调参 $\lambda$ 的诊断方法}
\label{diagnostics-for-tuning-lambda}

Monitoring training curves yields direct insight into whether bias or variance dominates:

监控训练曲线可以直接洞察是偏差还是方差占主导：

\begin{enumerate}
  \item \textbf{High Variance Indicators}: Policy entropy drops precipitously while explained variance of the value function becomes highly negative or erratic $\rightarrow$ policy updates are noisy. \textbf{Remedy}: Lower $\lambda$ to smooth target updates.
  \item \textbf{High Bias Indicators}: Agent achieves early stable training but completely fails to discover complex delayed reward sequences $\rightarrow$ under-estimating long-horizon dependencies due to bootstrapping. \textbf{Remedy}: Raise $\lambda$ closer to $1.0$ to expose policy to real downstream trajectory signals.
\end{enumerate}

\begin{enumerate}
  \item \textbf{高方差指标}：策略熵急剧下降，同时价值函数的解释方差变得高度负值或不稳定 $\rightarrow$ 策略更新噪声大。\textbf{补救措施}：降低 $\lambda$ 以平滑目标更新。
  \item \textbf{高偏差指标}：智能体实现早期稳定训练，但完全无法发现复杂的延迟奖励序列 $\rightarrow$ 由于自举而低估了长期依赖关系。\textbf{补救措施}：将 $\lambda$ 提高到接近 $1.0$，使策略暴露于真实的下游轨迹信号。
\end{enumerate}

\section{On-Policy vs Off-Policy --- Detailed Comparison}
\label{on-policy-vs-off-policy-detailed-comparison}

\section{在线策略 vs 离线策略 —— 详细对比}
\label{on-policy-vs-off-policy-detailed-comparison}

\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
 & \textbf{On-Policy} & \textbf{Off-Policy} \\
\midrule
\textbf{Data source} & Current policy $\pi_\theta$ only & Any policy (replay buffer) \\
\textbf{After update} & Old data is invalid, must regenerate & Old data still usable \\
\textbf{Sample efficiency} & Low (data used once) & High (data reused many times) \\
\textbf{Stability} & More stable (consistent distribution) & Can diverge (distribution mismatch) \\
\textbf{Examples} & REINFORCE, PPO, A2C, GRPO & Q-Learning, DQN, SAC, DPO \\
\textbf{For LLMs} & PPO, GRPO (generate fresh each step) & DPO (static preference dataset) \\
\bottomrule
\end{tabular}

\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
 & \textbf{在线策略（On-Policy）} & \textbf{离线策略（Off-Policy）} \\
\midrule
\textbf{数据来源} & 仅当前策略 $\pi_\theta$ & 任意策略（经验回放池） \\
\textbf{更新之后} & 旧数据作废，必须重新生成 & 旧数据仍可使用 \\
\textbf{样本效率} & 低（数据仅用一次） & 高（数据可重复使用多次） \\
\textbf{稳定性} & 更稳定（分布一致） & 可能发散（分布不匹配） \\
\textbf{示例} & REINFORCE, PPO, A2C, GRPO & Q-Learning, DQN, SAC, DPO \\
\textbf{用于LLM} & PPO, GRPO（每步重新生成） & DPO（静态偏好数据集） \\
\bottomrule
\end{tabular}

\begin{intuitionbox}[On/Off-Policy for RLHF Methods]
\textbf{PPO/GRPO are on-policy}: Generate responses with current policy, compute advantages, update, discard data, generate again. This is why generation is 60\% of compute --- you regenerate every step.

\textbf{DPO is off-policy}: Train on a fixed preference dataset. No generation during training. Much cheaper but suffers from distribution shift (data becomes stale as policy changes).

\textbf{Online DPO is a hybrid}: Generates fresh data (on-policy generation) but uses DPO’s supervised loss (off-policy-style optimization). Gets benefits of both.

\textbf{PPO’s cleverness}: Uses the clip ratio $r = \pi_\text{new}/\pi_\text{old}$ to squeeze multiple gradient steps from one batch of on-policy data (4 epochs), making it ``slightly off-policy'' in a controlled way.
\end{intuitionbox}

\begin{intuitionbox}[用于RLHF方法的在线/离线策略]
\textbf{PPO/GRPO是在线策略}：用当前策略生成回复，计算优势，更新，丢弃数据，再次生成。这就是为什么生成占计算量的60%——每一步都要重新生成。

\textbf{DPO是离线策略}：在固定的偏好数据集上训练。训练期间不生成。便宜得多，但面临分布偏移（数据随着策略变化而过时）。

\textbf{在线DPO是混合体}：生成新鲜数据（在线策略生成），但使用DPO的监督损失（离线策略式优化）。兼具两者优点。

\textbf{PPO的巧妙之处}：使用裁剪比率 $r = \pi_\text{new}/\pi_\text{old}$ 从一批在线策略数据中挤出多个梯度步（4个epoch），使其以受控方式“略带离线”特性。
\end{intuitionbox}

\section{Model-Based vs Model-Free}
\label{model-based-vs-model-free}

\section{基于模型 vs 无模型}
\label{model-based-vs-model-free}

\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
 & \textbf{Model-Free} & \textbf{Model-Based} \\
\midrule
\textbf{What’s learned} & Policy $\pi$ and/or value $V$/$Q$ directly & Environment model $\hat{P}(s'|s,a)$ \\
\textbf{Planning} & No planning, reactive decisions & Can simulate future trajectories \\
\textbf{Sample efficiency} & Low (must experience everything) & High (can plan in imagination) \\
\textbf{Accuracy} & No model bias & Model errors compound \\
\textbf{When to use} & Complex/unknown dynamics & Simple dynamics, need efficiency \\
\textbf{Examples} & PPO, DQN, SAC~\cite{haarnoja2018soft} & MuZero~\cite{schrittwieser2020mastering}, Dreamer~\cite{hafner2020dream}, AlphaGo~\cite{silver2016mastering} \\
\bottomrule
\end{tabular}

\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
 & \textbf{无模型（Model-Free）} & \textbf{基于模型（Model-Based）} \\
\midrule
\textbf{学习内容} & 直接学习策略 $\pi$ 和/或价值函数 $V$/$Q$ & 学习环境模型 $\hat{P}(s'|s,a)$ \\
\textbf{规划} & 无规划，反应式决策 & 可以模拟未来轨迹 \\
\textbf{样本效率} & 低（必须经历所有状态） & 高（可以在想象中规划） \\
\textbf{精确性} & 无模型偏差 & 模型误差会累积 \\
\textbf{使用时机} & 复杂/未知的动态 & 简单的动态，需要效率 \\
\textbf{示例} & PPO, DQN, SAC~\cite{haarnoja2018soft} & MuZero~\cite{schrittwieser2020mastering}, Dreamer~\cite{hafner2020dream}, AlphaGo~\cite{silver2016mastering} \\
\bottomrule
\end{tabular}

\begin{intuitionbox}[Why LLM RL is Model-Free]
Language generation dynamics are trivial (append token to sequence --- deterministic transitions). The ``model'' of the environment is not the bottleneck. What’s hard is the \textbf{reward} --- predicting what humans will prefer. This makes model-based methods unnecessary for LLM RL.

语言生成的动态是简单的（将标记附加到序列——确定性转移）。环境的“模型”并不是瓶颈。真正的难点在于\textbf{奖励}——预测人类会偏好什么。这使得基于模型的方法在LLM RL中变得不必要。

The reward model in RLHF could be seen as a ``model'' in some sense (it predicts human preference), but it’s used as a reward signal, not for planning/simulation. LLM RL is fundamentally model-free policy optimization.

RLHF中的奖励模型在某种意义上可以被视为一个“模型”（它预测人类偏好），但它被用作奖励信号，而不是用于规划/模拟。LLM RL本质上是无模型的策略优化。
\end{intuitionbox}

\section{Reward Shaping}
\label{reward-shaping}
\section{奖励塑形}
\label{reward-shaping}

\textbf{Reward shaping}~\cite{ng1999policy} is a technique where a developer modifies or supplements the environment’s original reward function. Its primary objective is to transform a \textbf{sparse reward} scenario --- where the agent receives feedback only upon final task completion --- into a \textbf{dense reward} scenario with intermediate feedback signals to accelerate convergence.

\textbf{奖励塑形（Reward Shaping）}~\cite{ng1999policy} 是一种技术，开发者通过修改或补充环境的原始奖励函数来加速收敛。其主要目标是将\textbf{稀疏奖励（sparse reward）}场景——智能体仅在最终任务完成时获得反馈——转变为具有中间反馈信号的\textbf{密集奖励（dense reward）}场景。

\subsection{The Mathematical Framework}
\label{the-mathematical-framework}
\subsection{数学框架}
\label{the-mathematical-framework}

Let the original reward at time step $t$ be $R_t(s, a, s')$. The reshaped reward adds an auxiliary shaping function $F$: 
\begin{equation}
\boxed{R'_t(s, a, s') = R_t(s, a, s') + F(s, a, s')}
\end{equation}

令时间步 $t$ 的原始奖励为 $R_t(s, a, s')$。塑形后的奖励添加了一个辅助塑形函数 $F$：
\begin{equation}
\boxed{R'_t(s, a, s') = R_t(s, a, s') + F(s, a, s')}
\end{equation}

\begin{warningbox}[The Risk of Naive Reshaping: Reward Hacking]
If $F(s, a, s')$ is arbitrarily designed, the agent will find structural loopholes to maximize auxiliary signals while ignoring the global objective.

如果 $F(s, a, s')$ 被随意设计，智能体就会寻找结构漏洞来最大化辅助信号，而忽略全局目标。

\textbf{Example}: A navigation agent rewarded for reaching intermediate landmarks might learn to loop indefinitely around a single checkpoint to accumulate infinite rewards --- without ever reaching the destination.

\textbf{示例}：一个因到达中间地标而获得奖励的导航智能体，可能会学会在单个检查点无限循环以累积无限奖励——却从不抵达目的地。

In LLMs: a model rewarded for ``sounding confident'' might learn to always start with ``Absolutely!'' regardless of accuracy.

在LLM中：一个因“听起来自信”而获得奖励的模型，可能会学会总是以“Absolutely!”开头，而不顾其准确性。
\end{warningbox}

\subsection{Potential-Based Reward Shaping (PBRS)}
\label{potential-based-reward-shaping-pbrs}
\subsection{基于势能的奖励塑形（PBRS）}
\label{potential-based-reward-shaping-pbrs}

To mathematically guarantee that reshaping does \textbf{not} alter the optimal policy, use \textbf{Potential-Based Reward Shaping}. The shaping function $F$ is constrained to the difference in a scalar potential function $\Phi$ across states: 
\begin{equation}
\boxed{F(s, a, s') = \gamma\, \Phi(s') - \Phi(s)}
\end{equation}

为了在数学上保证塑形\textbf{不}改变最优策略，请使用\textbf{基于势能的奖励塑形（Potential-Based Reward Shaping）}。塑形函数 $F$ 被约束为标量势函数 $\Phi$ 在不同状态之间的差值：
\begin{equation}
\boxed{F(s, a, s') = \gamma\, \Phi(s') - \Phi(s)}
\end{equation}

where $\Phi: \mathcal{S} \to \mathbb{R}$ is a real-valued potential function evaluating the desirable proximity of a state to the goal, and $\gamma$ is the discount factor.

其中 $\Phi: \mathcal{S} \to \mathbb{R}$ 是一个实值势函数，用于评估状态与目标的理想接近程度，$\gamma$ 是折扣因子。

The complete PBRS reward: 
\begin{equation}
R'(s, a, s') = R(s, a, s') + \gamma\, \Phi(s') - \Phi(s)
\end{equation}

完整的PBRS奖励：
\begin{equation}
R'(s, a, s') = R(s, a, s') + \gamma\, \Phi(s') - \Phi(s)
\end{equation}

\subsection{Theoretical Guarantees}
\label{theoretical-guarantees}
\subsection{理论保证}
\label{theoretical-guarantees}

\begin{keybox}[PBRS Policy Invariance Theorem]
\begin{itemize}
  \item \textbf{Policy Invariance}: The optimal policy $\pi^*$ under the reshaped reward $R'$ is \textbf{identical} to the optimal policy under the original reward $R$. The shaping cannot introduce sub-optimal behaviors.
  \item \textbf{策略不变性}：在塑形奖励 $R'$ 下的最优策略 $\pi^*$ 与原始奖励 $R$ 下的最优策略\textbf{完全相同}。塑形不会引入次优行为。
  \item \textbf{Loop Immunity}: Any cyclic trajectory starting and ending at the same state results in net potential change of exactly zero ($\Phi(s) - \Phi(s) = 0$). The agent cannot exploit loops to hack the reward.
  \item \textbf{循环免疫}：任何起始和终止于同一状态的循环轨迹都会导致净势变化恰好为零（$\Phi(s) - \Phi(s) = 0$）。智能体无法利用循环来钻奖励的空子。
  \item \textbf{Convergence Acceleration}: While the optimal policy is unchanged, the shaped reward provides denser gradient signals, enabling the agent to converge 5--50$\times$ faster in sparse reward environments.
  \item \textbf{收敛加速}：在最优策略不变的情况下，塑形奖励提供了更密集的梯度信号，使智能体在稀疏奖励环境中收敛速度提升5--50倍。
\end{itemize}
\end{keybox}

\part{RL Methods for LLMs}
\part{用于LLM的强化学习方法}