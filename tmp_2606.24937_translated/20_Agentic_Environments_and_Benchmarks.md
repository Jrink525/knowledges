\chapter{Agentic Environments and Benchmarks}
\label{sec:agentic-environments}
\chapter{代理环境与基准测试}
\label{sec:agentic-environments}

\section{Motivation: Why Agents Need Environments}
\label{sec:env-motivation}
\section{动机：为什么智能体需要环境}
\label{sec:env-motivation}

The evaluation of a conversational language model is, in principle, straightforward: present a prompt, collect a response, and score it against a reference or via human judgment. Agent evaluation is fundamentally different. An agent must \emph{act} in a world, observe consequences, and adapt its behavior over a sequence of steps. No single response captures this; only a structured \emph{environment} can.
原则上，对话式语言模型的评估是直接的：提供一个提示，收集回复，并根据参考或人工判断进行评分。而智能体（agent）的评估则根本不同。智能体必须在一个世界中\emph{行动}，观察后果，并在连续步骤中调整其行为。单一的回复无法捕捉这一点；只有结构化的\emph{环境}才能做到。

\textbf{Scope.} We use \emph{environment} in the reinforcement-learning sense: a world the agent interacts with for training or evaluation---not the production infrastructure (harness, orchestrator) that hosts the agent at serving time. Execution sandboxes appear here because they \emph{enable} such environments, but the agent harness itself is covered in Chapter~18.
\textbf{范围。} 我们在强化学习（reinforcement-learning，RL）意义上使用\emph{环境}：智能体为训练或评估而与之交互的世界——而不是服务时托管智能体的生产基础设施（框架、协调器）。执行沙盒在此出现是因为它们\emph{使能}了这类环境，但智能体框架本身在第18章中讨论。

\begin{keybox}[The Chatbot–Agent Evaluation Gap]
\textbf{Chatbot evaluation} measures the quality of a single generation: fluency, factuality, helpfulness. \textbf{Agent evaluation} measures the quality of a \emph{policy}: does the agent reliably achieve goals across diverse, long-horizon tasks? The gap is not merely quantitative---it requires a different infrastructure.
\end{keybox}
\begin{keybox}[聊天机器人与智能体评估差距]
\textbf{聊天机器人评估}衡量单次生成的质量：流畅性、事实性、有用性。\textbf{智能体评估}衡量一个\emph{策略}的质量：智能体是否能在多样且长期的任务中可靠地实现目标？这种差距不仅仅是量上的——它需要不同的基础设施。
\end{keybox}

Three forces drive the need for dedicated agentic environments:
三个因素推动了对专用代理环境的需求：

\paragraph{Safe Exploration.}
\label{safe-exploration.}
\paragraph{安全探索。}
\label{safe-exploration.}

Real-world systems---production databases, live websites, financial APIs---cannot absorb the exploratory behavior of an agent under training. A sandboxed environment provides a faithful replica in which the agent can fail, recover, and learn without causing irreversible harm. Security isolation (e.g., Docker containers, network-restricted VMs) is not optional; it is a first-class design requirement.
现实世界的系统——生产数据库、在线网站、金融API——无法承受训练中智能体的探索行为。沙盒环境提供了一个忠实的副本，智能体可以在其中失败、恢复和学习，而不会造成不可逆转的损害。安全隔离（例如，Docker容器、网络受限的虚拟机）不是可选的；它是一等设计需求。

\paragraph{Reproducible Evaluation.}
\label{reproducible-evaluation.}
\paragraph{可复现评估。}
\label{reproducible-evaluation.}

Benchmarking requires that every agent faces the same task under the same conditions. Environments must be deterministic on demand, version-controlled, and distributable so that results reported in one lab can be reproduced in another. The absence of this property has historically made agent benchmarks difficult to compare.
基准测试要求每个智能体在相同条件下面对相同任务。环境必须是按需确定性的、版本控制的且可分发的，以便在一个实验室报告的结果可以在另一个实验室复现。缺乏这一特性在历史上使得智能体基准测试难以比较。

\paragraph{Curriculum Learning.}
\label{curriculum-learning.}
\paragraph{课程学习（Curriculum Learning）。}
\label{curriculum-learning.}

Training an agent from scratch on hard tasks is sample-inefficient. Environments that expose a \emph{difficulty curriculum}---gradually increasing task complexity as the agent improves---dramatically reduce the number of environment interactions required to reach a target performance level. This mirrors how humans learn: mastery of sub-skills precedes mastery of the whole.
从头开始在困难任务上训练智能体是样本效率低下的。暴露\emph{难度课程}的环境——随着智能体进步逐渐增加任务复杂度——可以大幅减少达到目标性能水平所需的环境交互次数。这反映了人类学习的方式：掌握子技能先于掌握整体。

\begin{intuitionbox}[Environments as the RL ``Gym'' for LLMs]
Just as OpenAI Gym~\cite{brockman2016openai} standardized the interface between RL algorithms and simulated control tasks, agentic environments standardize the interface between LLM-based agents and the diverse tasks they must solve. The analogy is tight: \texttt{reset()} initializes a new episode, \texttt{step(action)} advances the world and returns an observation and reward, and \texttt{render()} produces a human-readable view of the current state.
\end{intuitionbox}
\begin{intuitionbox}[环境作为LLM的RL“Gym”]
正如OpenAI Gym~\cite{brockman2016openai}标准化了RL算法与模拟控制任务之间的接口，代理环境标准化了基于LLM的智能体与它们必须解决的各种任务之间的接口。这种类比很紧密：\texttt{reset()}初始化一个新回合，\texttt{step(action)}推进世界并返回观察和奖励，\texttt{render()}生成当前状态的人类可读视图。
\end{intuitionbox}

\section{Environment Design Principles}
\label{sec:env-design}
\section{环境设计原则}
\label{sec:env-design}

A well-designed agentic environment exposes four orthogonal design axes: the \emph{observation space}, the \emph{action space}, the \emph{reward signal}, and the \emph{episode structure}. Getting each right is necessary; getting all four right simultaneously is the craft of environment engineering.
一个设计良好的代理环境暴露四个正交的设计轴：\emph{观察空间}、\emph{动作空间}、\emph{奖励信号}和\emph{回合结构}。把每个都做好是必要的；同时把四个都做好是环境工程的艺术。

\subsection{Observation Space Design}
\label{observation-space-design}
\subsection{观察空间设计}
\label{observation-space-design}

The observation is what the agent \emph{sees} at each step. For LLM-based agents the observation is almost always rendered as text, but the source material varies widely:
观察是智能体在每个步骤中\emph{看到}的内容。对于基于LLM的智能体，观察几乎总是以文本形式呈现，但源材料差异很大：

\begin{itemize}
  \item \textbf{Pure text}: terminal output, file contents, API responses, error messages. Maximally compatible with any LLM but loses spatial and visual structure.
  \item \textbf{Structured (JSON/XML)}: machine-readable state representations. Enables precise grounding but requires the agent to parse structure rather than read prose.
  \item \textbf{Multimodal}: screenshots, accessibility trees, rendered HTML. Necessary for GUI and web tasks; requires a vision-capable model or a separate perception module.
  \item \textbf{Hybrid}: a screenshot paired with an accessibility tree (used in OSWorld and VisualWebArena) gives both visual context and structured element identifiers, combining the strengths of both modalities.
\end{itemize}
\begin{itemize}
  \item \textbf{纯文本（Pure text）}：终端输出、文件内容、API响应、错误消息。与任何LLM最大兼容，但丢失了空间和视觉结构。
  \item \textbf{结构化数据（JSON/XML）}：机器可读的状态表示。实现精确的接地（grounding），但要求智能体解析结构而非阅读散文。
  \item \textbf{多模态（Multimodal）}：屏幕截图、无障碍树、渲染后的HTML。对于GUI和Web任务必不可少；需要具备视觉能力的模型或单独的感知模块。
  \item \textbf{混合（Hybrid）}：屏幕截图配合无障碍树（用于OSWorld和VisualWebArena），既提供视觉上下文，又提供结构化元素标识符，结合了两种模态的优势。
\end{itemize}

\begin{warningbox}[Observation Leakage]
A common design mistake is including information in the observation that the agent should not have access to---for example, the ground truth answer, the reward value, or future task steps. Observation leakage inflates benchmark scores and produces agents that fail catastrophically when deployed in real environments where such information is absent.
\end{warningbox}
\begin{warningbox}[观察泄漏（Observation Leakage）]
一个常见的设计错误是在观察中包含智能体不应该访问的信息——例如，真实答案、奖励值或未来的任务步骤。观察泄漏会抬高基准分数，并产生在真实环境中部署时因缺乏此类信息而灾难性失败的智能体。
\end{warningbox}

\subsection{Action Space Design}
\label{action-space-design}
\subsection{动作空间设计}
\label{action-space-design}

The action space defines what the agent can \emph{do}. For LLM agents the action is typically a text string that is parsed and executed by the environment. Common action types include:
动作空间定义了智能体可以\emph{做什么}。对于LLM智能体，动作通常是一个由环境解析并执行的文本字符串。常见的动作类型包括：

\begin{itemize}
  \item \textbf{Tool calls}: structured invocations of external functions (search, calculator, calendar). Often formatted as JSON or XML function-call syntax.
  \item \textbf{Code execution}: the agent writes code that is run in a sandbox; the stdout/stderr is returned as the next observation. This is the most expressive action type.
  \item \textbf{API interactions}: HTTP requests to web services, database queries, shell commands.
  \item \textbf{GUI actions}: \texttt{click(x,y)}, \texttt{type("text")}, \texttt{scroll(direction)}, \texttt{key("Enter")}. Used in computer-use environments.
  \item \textbf{Natural language}: free-form text directed at another agent, a human, or a sub-task planner.
\end{itemize}
\begin{itemize}
  \item \textbf{工具调用（Tool calls）}：外部函数的结构化调用（搜索、计算器、日历）。通常格式化为JSON或XML函数调用语法。
  \item \textbf{代码执行（Code execution）}：智能体编写代码在沙盒中运行；stdout/stderr作为下一个观察返回。这是最具表达力的动作类型。
  \item \textbf{API交互（API interactions）}：向Web服务的HTTP请求、数据库查询、Shell命令。
  \item \textbf{GUI动作（GUI actions）}：\texttt{click(x,y)}、\texttt{type("text")}、\texttt{scroll(direction)}、\texttt{key("Enter")}。用于计算机使用环境。
  \item \textbf{自然语言（Natural language）}：面向另一个智能体、人类或子任务规划器的自由形式文本。
\end{itemize}

\subsection{Reward Signal Design}
\label{reward-signal-design}
\subsection{奖励信号设计}
\label{reward-signal-design}

Reward design is the hardest part of environment engineering. The reward must be:
奖励设计是环境工程中最难的部分。奖励必须满足：

\begin{enumerate}
  \item \textbf{Aligned}: high reward should correspond to genuine task completion, not to superficial proxies.
  \item \textbf{Learnable}: the signal must be dense enough that the agent can make progress; pure sparse rewards on long-horizon tasks are often unlearnable without additional shaping.
  \item \textbf{Tamper-proof}: the agent must not be able to achieve high reward without actually completing the task (reward hacking).
\end{enumerate}
\begin{enumerate}
  \item \textbf{对齐（Aligned）}：高奖励应对应于真正的任务完成，而非表面代理。
  \item \textbf{可学习（Learnable）}：信号必须足够密集，使智能体能取得进展；长期任务上的纯稀疏奖励（sparse rewards）在缺乏额外塑造（shaping）时通常无法学习。
  \item \textbf{防篡改（Tamper-proof）}：智能体不能在没有实际完成任务的情况下获得高奖励（奖励黑客）。
\end{enumerate}

\begin{table}[ht!]
\centering
\caption{Reward signal types for agentic environments with trade-offs.}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Reward Type} & \textbf{Pros} & \textbf{Cons} \\
\midrule
Sparse (0/1 at end) & Aligned, hard to hack & Hard to learn \\
Dense (step-level) & Easy to learn & Prone to shaping artifacts \\
Intrinsic (curiosity) & Drives exploration & May diverge from task \\
LLM-as-judge & Flexible, nuanced & Expensive, inconsistent \\
Execution-based & Ground truth & Only for verifiable tasks \\
\bottomrule
\end{tabular}
\end{table}
\begin{table}[ht!]
\centering
\caption{代理环境中具有权衡的奖励信号类型。}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{奖励类型} & \textbf{优点} & \textbf{缺点} \\
\midrule
稀疏（结束时0/1） & 对齐，难以黑客 & 难以学习 \\
密集（步骤级） & 易于学习 & 易产生塑造伪影 \\
内在（好奇心） & 驱动探索 & 可能偏离任务 \\
LLM作为评判 & 灵活、细致 & 昂贵、不一致 \\
基于执行 & 真实解 & 仅适用于可验证任务 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Episode Structure}
\label{episode-structure}
\subsection{回合结构}
\label{episode-structure}

Episodes can be structured in several ways:
回合可以通过多种方式结构化：

\begin{itemize}
  \item \textbf{Fixed-length}: the agent takes exactly $T$ steps. Simple to implement; wastes compute on already-solved tasks.
  \item \textbf{Early termination}: the episode ends when the agent signals completion or a terminal state is reached. More efficient but requires a reliable termination detector.
  \item \textbf{Open-ended}: no fixed horizon; the agent operates until a resource budget (tokens, API calls, wall time) is exhausted. Closest to real deployment but hardest to evaluate.
\end{itemize}
\begin{itemize}
  \item \textbf{固定长度（Fixed-length）}：智能体恰好执行 $T$ 步。实现简单；在已解决的任务上浪费计算资源。
  \item \textbf{提前终止（Early termination）}：智能体发出完成信号或达到终止状态时结束回合。更高效，但需要可靠的终止检测器。
  \item \textbf{开放式（Open-ended）}：无固定水平线；智能体持续运行直到资源预算（令牌、API调用、挂钟时间）耗尽。最接近实际部署，但最难评估。
\end{itemize}

\paragraph{Adaptive episode length and early termination.}
\label{adaptive-episode-length-and-early-termination.}
\paragraph{自适应回合长度与提前终止。}
\label{adaptive-episode-length-and-early-termination.}

## Recent work challenges the assumption that episode length must be fixed before training begins:
## 近期研究挑战了“回合长度必须在训练开始前固定”这一假设：

\begin{itemize}
  \item \textbf{Curriculum over horizon.} AELA~\cite{yoo2025aela} starts with short episodes and gradually extends the horizon as agent competence grows, measured by policy-entropy convergence. Short early episodes expose more diverse initial states per training sample.
  \item \textbf{基于时域的长度课程 (Curriculum over horizon)。} AELA~\cite{yoo2025aela} 从短回合开始，随着智能体能力提升（以策略熵收敛为衡量标准）逐步延长时域。较短的早期回合使得每个训练样本能暴露更多样化的初始状态。
  \item \textbf{Truncation as RL penalty.} DLER~\cite{liu2025dler} shows that the simplest length control---hard truncation---works well for reasoning models when paired with batch-wise reward normalization and dynamic sampling to avoid losing the reward signal from cut-off rollouts.
  \item \textbf{截断作为强化学习惩罚 (Truncation as RL penalty)。} DLER~\cite{liu2025dler} 表明，最简单的长度控制——硬截断——在配合批量奖励归一化和动态采样以避免丢失截断展开中的奖励信号时，对推理模型效果很好。
  \item \textbf{Learned stopping.} Rather than a fixed budget, the model itself can learn when to stop reasoning. \cite{liu2025answerstop} propose three strategies: stop when successive reasoning steps converge to the same answer, boost the end-of-thinking token probability, or train a lightweight classifier on hidden-state activations to predict the optimal stopping point.
  \item \textbf{学习式停止 (Learned stopping)。} 模型本身可以学习何时停止推理，而非依赖固定预算。\cite{liu2025answerstop} 提出了三种策略：当连续推理步骤收敛到相同答案时停止；提高思考结束标记的概率；或训练一个轻量级分类器，基于隐藏状态激活来预测最佳停止点。
  \item \textbf{Partial-rollout recycling.} APRIL~\cite{april2025} over-provisions rollout requests and terminates once the target batch count is reached; incomplete responses are recycled as warm-start prefixes in future steps, eliminating the long-tail stall where a few slow samples block the entire batch (20--35\% throughput gain). TLT~\cite{hu2025tlt} addresses the same bottleneck by training an adaptive draft model on-the-fly for speculative decoding of stragglers (1.7$\times$ end-to-end speedup, lossless).
  \item \textbf{部分展开回收 (Partial-rollout recycling)。} APRIL~\cite{april2025} 超额提供展开请求，并在达到目标批次数时终止；未完成的响应被回收作为后续步骤的热启动前缀，从而消除了少数慢样本阻塞整个批次的“长尾停滞”问题（吞吐量提升20-35%）。TLT~\cite{hu2025tlt} 通过在线训练自适应草稿模型对落后样本进行投机解码（端到端加速1.7倍，无损）解决了同样的瓶颈。
\end{itemize}


\subsection{Difficulty Curriculum and Adaptive Environments}
\label{difficulty-curriculum-and-adaptive-environments}

## Difficulty Curriculum and Adaptive Environments
## 难度课程与自适应环境

Static benchmarks measure a fixed snapshot of agent capability. Adaptive environments go further: they monitor agent performance online and adjust task difficulty to keep the agent in the ``zone of proximal development''---hard enough to learn from, easy enough to succeed occasionally. Techniques include:
静态基准测试衡量智能体能力的固定快照。自适应环境则更进一步：它们在线监控智能体性能，并调整任务难度，使其保持在“最近发展区”——足够难以便从中学习，又足够简单以使偶尔成功。技术包括：

\begin{itemize}
  \item \textbf{Procedural generation}: tasks are sampled from a parameterized distribution; difficulty parameters are tuned based on recent success rate. Prioritized Level Replay~\cite{jiang2021plr} scores each generated level by its estimated learning potential (e.g.~GAE magnitude) and replays high-value levels more often.
  \item \textbf{程序化生成 (Procedural generation)}：任务从参数化分布中采样；难度参数根据近期成功率进行调整。Prioritized Level Replay (PLR)~\cite{jiang2021plr} 根据每个生成关卡的估计学习潜力（例如GAE幅度）进行评分，并更频繁地重放高价值关卡。
  \item \textbf{Self-play / adversarial environment design}: PAIRED~\cite{dennis2020paired} trains an adversary to propose environments that maximize the \emph{regret} between a protagonist and antagonist agent, producing a natural curriculum of increasing complexity without hand-designed difficulty schedules.
  \item \textbf{自博弈/对抗环境设计 (Self-play / adversarial environment design)}：PAIRED~\cite{dennis2020paired} 训练一个对手来提出能够最大化主角智能体和对手智能体之间 \emph{遗憾 (regret)} 的环境，从而在没有手动设计难度调度的情况下自然产生递增复杂度的课程。
  \item \textbf{Hindsight relabeling}: failed trajectories are relabeled with the goal the agent \emph{did} achieve, providing a learning signal even from failures (Hindsight Experience Replay, HER)~\cite{andrychowicz2017hindsight}.
  \item \textbf{事后重新标注 (Hindsight relabeling)}：失败轨迹被重新标注为智能体 \emph{实际} 完成的目标，从而即使从失败中也能提供学习信号（事后经验回放，HER）~\cite{andrychowicz2017hindsight}。
  \item \textbf{Difficulty-targeted data selection for LLMs}: in RLVR training, not all problems provide equal signal. Recent work prioritizes moderate-difficulty questions---those the model solves roughly 30--70\% of the time---which yield the highest gradient information~\cite{wang2025dataefficiency}. ADCL~\cite{liu2025adcl} periodically re-estimates difficulty as the model improves, avoiding stale curricula.
  \item \textbf{针对难度的LLM数据选择 (Difficulty-targeted data selection for LLMs)}：在RLVR训练中，并非所有问题都能提供相同信号。近期工作优先考虑中等难度的问题——即模型约30-70%时间能解决的那些——这些能产生最高的梯度信息~\cite{wang2025dataefficiency}。ADCL~\cite{liu2025adcl} 随着模型提升定期重新估计难度，避免过时的课程。
\end{itemize}


\section{Types of Agentic Environments}
\label{sec:env-types}

## Types of Agentic Environments
## 智能体环境的类型

\subsection{Code Execution Sandboxes}
\label{code-execution-sandboxes}

## Code Execution Sandboxes
## 代码执行沙盒

The most fundamental agentic environment for LLMs is a code execution sandbox: the agent writes code, the sandbox runs it, and the output is returned. This simple loop underlies a surprising fraction of real-world agent deployments.
对于LLM而言，最基础的智能体环境是代码执行沙盒：智能体编写代码，沙盒运行它，然后返回输出。这个简单的循环支撑着现实中相当大一部分智能体部署。

\textbf{Docker-based isolation} is the most common approach. Each episode spawns a fresh container from a known image, executes the agent’s code inside it, and destroys the container at episode end. Network access, filesystem writes, and process spawning can all be controlled at the container level.1
\textbf{基于Docker的隔离 (Docker-based isolation)} 是最常见的方法。每个回合从一个已知镜像生成新容器，在容器内执行智能体的代码，并在回合结束时销毁容器。网络访问、文件系统写入和进程生成都可以在容器层面进行控制。1

\textbf{E2B} (Environments to Benchmarks)2 provides a managed cloud sandbox API: the agent sends code over HTTP, E2B executes it in an isolated Firecracker microVM that boots in under 200 ms, and returns stdout/stderr. E2B handles the infrastructure complexity of container lifecycle management, making it easy to integrate into agent training loops.
\textbf{E2B (Environments to Benchmarks)}2 提供了一个托管的云沙盒API：智能体通过HTTP发送代码，E2B在隔离的Firecracker微虚拟机中执行（启动时间不超过200毫秒），并返回stdout/stderr。E2B处理了容器生命周期管理的基础设施复杂性，使其易于集成到智能体训练循环中。

\textbf{Modal}3 offers a similar managed execution model with stronger GPU support, making it suitable for agents that need to run ML workloads as part of their task.
\textbf{Modal}3 提供了类似的托管执行模型，并具有更强的GPU支持，使其适用于需要在任务中运行机器学习工作负载的智能体。

\begin{warningbox}[Sandbox Escape and Security]
Sandbox Escape and Security
沙盒逃逸与安全

Code execution sandboxes are a primary attack surface. A sufficiently capable agent (or a prompt-injected payload) may attempt to escape the sandbox via kernel exploits, network exfiltration, or resource exhaustion. Defense-in-depth is essential: combine container isolation with seccomp profiles, read-only root filesystems, network egress filtering, and CPU/memory cgroups. Never run agent-generated code with host-level privileges.
代码执行沙盒是一个主要攻击面。一个能力足够强的智能体（或通过提示注入的负载）可能尝试通过内核漏洞利用、网络数据外泄或资源耗尽来逃逸沙盒。纵深防御至关重要：将容器隔离与seccomp配置文件、只读根文件系统、网络出口过滤以及CPU/内存cgroup相结合。绝对不要以主机级权限运行智能体生成的代码。
\end{warningbox}

\subsection{Web Environments}
\label{web-environments}

## Web Environments
## 网页环境

Web environments present the agent with a browser and ask it to complete tasks on real or simulated websites.
网页环境为智能体提供一个浏览器，并要求其在真实或模拟网站上完成任务。

\textbf{WebArena}~\cite{zhou2024webarena} provides a self-hosted testbed of four functional web applications---an e-commerce store, a social forum, a GitLab instance, and a CMS---plus a map service, totalling 812 long-horizon tasks. The agent interacts via a browser automation API; tasks require multi-step navigation, form filling, and information retrieval. Human performance is approximately 78\%; state-of-the-art LLM agents achieve around 35--45\%.
\textbf{WebArena}~\cite{zhou2024webarena} 提供了一个自托管的测试平台，包含四个功能性网络应用程序——一个电商商店、一个社交论坛、一个GitLab实例和一个CMS——外加一个地图服务，总共812个长时域任务。智能体通过浏览器自动化API进行交互；任务需要多步导航、表单填写和信息检索。人类表现约为78%；最先进的LLM智能体达到约35-45%。

\textbf{VisualWebArena}~\cite{koh2024visualwebarena} extends WebArena with visually grounded tasks that require interpreting images on web pages. The observation is a screenshot paired with an accessibility tree; the agent must ground its actions in both modalities.
\textbf{VisualWebArena}~\cite{koh2024visualwebarena} 通过需要解释网页上图像的视觉基础任务扩展了WebArena。观察结果是一个截图与一个无障碍树配对；智能体必须将其动作锚定在这两种模态中。

\textbf{Mind2Web}~\cite{deng2024mind2web} is a large-scale dataset of 2,000 tasks across 137 real websites, collected via human demonstrations. Unlike WebArena, Mind2Web focuses on generalization to unseen websites, making it a harder out-of-distribution test.
\textbf{Mind2Web}~\cite{deng2024mind2web} 是一个大规模数据集，包含137个真实网站上的2000个任务，通过人类演示收集。与WebArena不同，Mind2Web侧重于对未见网站的泛化能力，使其成为更难的分布外测试。

\begin{examplebox}[WebArena Task Example]
WebArena Task Example
WebArena任务示例

\textbf{Task}: ``Find the cheapest red dress under \$50 on the e-commerce site and add it to the cart.''
\textbf{任务}：“在电商网站上找到价格低于50美元的最便宜红色连衣裙，并将其加入购物车。”

\textbf{Agent trajectory}:
\textbf{智能体轨迹}：

\begin{enumerate}
  \item Navigate to the clothing category.
  \item 导航到服装类别。
  \item Apply color filter: red.
  \item 应用颜色筛选：红色。
  \item Sort by price ascending.
  \item 按价格升序排序。
  \item Identify the first item under \$50.
  \item 识别价格低于50美元的第一件商品。
  \item Click ``Add to Cart''.
  \item 点击“加入购物车”。
  \item Verify cart contents.
  \item 验证购物车内容。
\end{enumerate}

The environment checks the final cart state against the ground truth item; reward is 1 if correct, 0 otherwise.
环境检查最终购物车状态是否与真实商品匹配；正确则奖励为1，否则为0。
\end{examplebox}

\subsection{Computer Use Environments}
\label{computer-use-environments}

## Computer Use Environments
## 计算机使用环境

Computer use environments give the agent control of a full desktop operating system, observed through screenshots and/or accessibility APIs.
计算机使用环境赋予智能体对整个桌面操作系统的控制权，并通过截图和/或无障碍API进行观察。

\textbf{OSWorld}~\cite{xie2024osworld} tests desktop automation across three operating systems (Ubuntu, Windows, macOS) with 369 tasks spanning productivity apps (LibreOffice, VS Code, Chrome, GIMP, etc.). The agent observes screenshots and acts via \texttt{pyautogui}-style mouse and keyboard commands. The human--agent gap is stark: annotators succeed on roughly 72\% of tasks while the strongest LLM agent manages only $\sim$18\%, underscoring the difficulty of pixel-level GUI control.
\textbf{OSWorld}~\cite{xie2024osworld} 在三个操作系统（Ubuntu、Windows、macOS）上测试桌面自动化，包含369个跨生产力应用（LibreOffice、VS Code、Chrome、GIMP等）的任务。智能体观察截图并通过 \texttt{pyautogui} 风格的鼠标和键盘命令执行操作。人类与智能体之间的差距十分显著：标注者在大约72%的任务上成功，而最强的LLM智能体仅能完成约18%，凸显了像素级GUI控制的难度。

\textbf{WindowsAgentArena}~\cite{bonatti2024windows} focuses specifically on Windows 11, with 154 tasks across 19 applications. It emphasizes enterprise workflows: Excel formulas, PowerPoint editing, Outlook email management.
\textbf{WindowsAgentArena}~\cite{bonatti2024windows} 专门针对Windows 11，包含横跨19个应用的154个任务。它侧重于企业工作流：Excel公式、PowerPoint编辑、Outlook电子邮件管理。

## Motivation: Why Agents Need Environments
## 动机：为何智能体需要环境

\begin{keybox}[The Screenshot Bottleneck]
\begin{keybox}[截图瓶颈]

Computer use agents face a fundamental challenge: screenshots are high-dimensional (typically $1920 \times 1080 \times 3$ pixels) but most of the information is irrelevant to the current action. Efficient agents learn to attend to small regions of the screen, use accessibility trees to identify interactive elements by name rather than pixel coordinate, and maintain a compact working memory of previously visited UI states.
计算机使用智能体面临一个根本性挑战：截图是高维的（通常为 $1920 \times 1080 \times 3$ 像素），但大部分信息与当前动作无关。高效的智能体学会关注屏幕的小区域，使用无障碍树（accessibility tree）通过名称而非像素坐标来识别可交互元素，并维护之前访问过的UI状态的紧凑工作记忆。
\end{keybox}
\end{keybox}

\subsection{Software Engineering Environments}
\subsection{软件工程环境}
\label{software-engineering-environments}
\label{software-engineering-environments}

Software engineering (SWE) environments ask the agent to solve real-world programming tasks: fixing bugs, implementing features, writing tests.
软件工程（SWE）环境要求智能体解决真实的编程任务：修复错误、实现功能、编写测试。

\textbf{SWE-bench}~\cite{jimenez2024swebench} draws on 2,294 real pull requests from 12 widely-used Python projects (Django, Flask, scikit-learn, among others). Each instance pairs an issue description with a held-out test suite that passes only after the correct patch is applied. The agent must understand the repository structure, locate the relevant code, implement a fix, and verify it with the test suite. The \textbf{SWE-bench Verified} subset (500 issues) has been human-validated for correctness and is the standard evaluation target.
\textbf{SWE-bench}~\cite{jimenez2024swebench} 从12个广泛使用的Python项目（Django、Flask、scikit-learn等）中抽取了2,294个真实的拉取请求（pull request）。每个实例将一个问题描述与一个保留的测试套件配对，该套件仅在应用了正确的补丁后才会通过。智能体必须理解代码库结构、定位相关代码、实现修复，并通过测试套件进行验证。**SWE-bench Verified**子集（500个问题）经过人工验证以确保正确性，是标准的评估目标。

\textbf{SWE-agent}~\cite{yang2024sweagent} is both a benchmark environment and an agent framework. It introduces the \emph{Agent-Computer Interface} (ACI): a set of shell commands optimized for LLM agents (e.g., \texttt{search\_file}, \texttt{open}, \texttt{edit}) that reduce the action space complexity compared to raw bash.
\textbf{SWE-agent}~\cite{yang2024sweagent} 既是一个基准测试环境，也是一个智能体框架。它引入了\emph{智能体-计算机接口（Agent-Computer Interface，ACI）}：一组为LLM智能体优化的shell命令（例如 \texttt{search\_file}、\texttt{open}、\texttt{edit}），相比于原始bash降低了动作空间的复杂度。

\begin{examplebox}[SWE-bench Workflow]
\begin{examplebox}[SWE-bench工作流程]
\textbf{Input}: A GitHub issue description and the full repository at the commit where the issue was filed.
\textbf{输入}：GitHub问题描述以及问题提交时所在的完整代码库提交版本。

\textbf{Agent actions}: \texttt{find\_file}, \texttt{view}, \texttt{edit}, \texttt{python -m pytest tests/}.
\textbf{智能体动作}：\texttt{find\_file}、\texttt{view}、\texttt{edit}、\texttt{python -m pytest tests/}。

\textbf{Reward}: 1 if all target tests pass after the agent’s patch; 0 otherwise. No partial credit.
\textbf{奖励}：如果在智能体的补丁之后所有目标测试通过，则得1分；否则得0分。无部分分数。
\end{examplebox}
\end{examplebox}

\subsection{Scientific Research Environments}
\subsection{科学研究环境}
\label{scientific-research-environments}
\label{scientific-research-environments}

Scientific research environments push agents toward autonomous knowledge generation: reading papers, forming hypotheses, designing experiments, and interpreting results.
科学研究环境推动智能体走向自主知识生成：阅读论文、形成假设、设计实验以及解读结果。

\textbf{PaperQA2}~\cite{lala2023paperqa} is a retrieval-augmented agent that answers scientific questions by searching a corpus of PDFs, extracting relevant passages, and synthesizing an answer with citations. It serves as both a tool and a benchmark for literature-grounded reasoning.
\textbf{PaperQA2}~\cite{lala2023paperqa} 是一个检索增强型智能体，通过搜索PDF语料库、提取相关段落并综合带有引用的答案来回答科学问题。它既可用作工具，也可作为基于文献推理的基准。

\textbf{AI Scientist}~\cite{lu2024aiscientist} is an end-to-end research automation system: given a research direction, the agent generates hypotheses, writes and runs experiments, interprets results, and produces a draft paper. The environment includes a Python execution sandbox, a literature search API, and a LaTeX compiler.
\textbf{AI Scientist}~\cite{lu2024aiscientist} 是一个端到端的研究自动化系统：给定一个研究方向，智能体生成假设、编写并运行实验、解读结果，并生成论文草稿。环境包括Python执行沙箱、文献搜索API以及LaTeX编译器。

\textbf{MLAgentBench}~\cite{huang2024mlagentbench} evaluates agents on machine learning engineering tasks: improving model accuracy on a given dataset within a compute budget. The agent can read data, write training scripts, run experiments, and iterate.
\textbf{MLAgentBench}~\cite{huang2024mlagentbench} 在机器学习工程任务上评估智能体：在给定的计算预算内提高模型在给定数据集上的准确率。智能体可以读取数据、编写训练脚本、运行实验并进行迭代。

\subsection{Game and Simulation Environments}
\subsection{游戏与模拟环境}
\label{game-and-simulation-environments}
\label{game-and-simulation-environments}

Games provide rich, long-horizon environments with well-defined reward signals and no real-world consequences.
游戏提供了丰富、长周期的环境，具有明确定义的奖励信号，且无真实世界后果。

\textbf{NetHack}~\cite{kuttler2020nethack} is a procedurally generated roguelike with an enormous state space, requiring long-term planning, inventory management, and adaptation to unexpected events. The NetHack Learning Environment (NLE) provides a Gym-compatible interface.
\textbf{NetHack}~\cite{kuttler2020nethack} 是一个程序生成的roguelike游戏，具有巨大的状态空间，需要长期规划、背包管理以及对意外事件的适应能力。NetHack学习环境（NLE）提供了与Gym兼容的接口。

\textbf{Voyager / Minecraft}~\cite{wang2023voyager} uses the Minecraft game engine as an open-ended environment. Voyager introduces a curriculum of progressively harder tasks (collect wood $\to$ craft tools $\to$ build shelter $\to$ explore the Nether) and a skill library that accumulates reusable code snippets across episodes.
\textbf{Voyager / Minecraft}~\cite{wang2023voyager} 使用Minecraft游戏引擎作为开放式环境。Voyager引入了逐渐变难的任务课程（收集木材 $\to$ 制作工具 $\to$ 建造庇护所 $\to$ 探索下界）以及一个技能库，该库跨回合积累可复用的代码片段。

\textbf{GAIA}~\cite{mialon2023gaia} poses 466 questions that demand chained tool use---web search, code execution, file parsing---graded into three difficulty levels by the number of reasoning steps involved. The benchmark starkly exposes the gap between human capability ($\sim$92\% accuracy) and current LLM agents (GPT-4 with plugins scored $\sim$15\% at launch; later systems reach $\sim$30\%).
\textbf{GAIA}~\cite{mialon2023gaia} 提出了466个需要链式工具使用的问题——网页搜索、代码执行、文件解析——根据所涉及的推理步骤数量分为三个难度等级。该基准鲜明地揭示了人类能力（准确率约92%）与当前LLM智能体之间的差距（带有插件的GPT-4在发布时得分约15%；后续系统达到约30%）。

\subsection{Multi-Agent Environments}
\subsection{多智能体环境}
\label{multi-agent-environments}
\label{multi-agent-environments}

Multi-agent environments involve two or more LLM agents interacting with each other and/or a shared world.
多智能体环境涉及两个或更多LLM智能体相互交互，和/或与一个共享世界交互。

\begin{itemize}
  \item \textbf{Negotiation}: agents with private utility functions must reach a deal through dialogue. Classic environments include DealOrNoDeal~\cite{lewis2017dealornodeal} and CaSiNo~\cite{chawla2021casino}.
  \item \textbf{谈判}：具有私有效用函数的智能体必须通过对话达成协议。经典环境包括DealOrNoDeal~\cite{lewis2017dealornodeal}和CaSiNo~\cite{chawla2021casino}。
  \item \textbf{Debate}: two agents argue opposing positions; a judge agent (or human) evaluates the quality of arguments. Used to elicit truthful reasoning via adversarial pressure.
  \item \textbf{辩论}：两个智能体争论对立立场；一个裁判智能体（或人类）评估论点的质量。用于通过对抗压力引出真实推理。
  \item \textbf{Collaborative task completion}: agents with complementary capabilities (planner, executor, critic) must coordinate to complete a task neither could solve alone. Frameworks include AutoGen~\cite{wu2023autogen}, CrewAI~\cite{moura2023crewai}, and MetaGPT~\cite{hong2023metagpt}.
  \item \textbf{协作任务完成}：具有互补能力的智能体（规划者、执行者、评审者）必须协调完成单个智能体无法独立解决的任务。相关框架包括AutoGen~\cite{wu2023autogen}、CrewAI~\cite{moura2023crewai}和MetaGPT~\cite{hong2023metagpt}。
  \item \textbf{Competitive games}: agents play zero-sum games (chess, Go, poker) where the opponent is itself an LLM agent. Self-play in these environments has produced superhuman performance in narrow domains.
  \item \textbf{竞争性游戏}：智能体玩零和游戏（国际象棋、围棋、扑克），对手本身就是一个LLM智能体。在这些环境中的自我对弈已在狭窄领域产生了超人类表现。
\end{itemize}

\section{OpenEnv: Standardized Agentic Environment Interfaces}
\section{OpenEnv：标准化的智能体环境接口}
\label{sec:openenv}
\label{sec:openenv}

The proliferation of agentic environments has created a fragmentation problem: each environment exposes a different API, uses different observation formats, and requires different scaffolding. \textbf{OpenEnv}~\cite{huggingface2025openenv} is a recent open-source framework by Hugging Face that addresses this directly: it provides a Gymnasium-style~\cite{towers2024gymnasium} interface (\texttt{step()}, \texttt{reset()}, \texttt{state()}) for agentic execution environments, with isolated Docker-based deployments communicating over WebSocket. OpenEnv complements broader standardization efforts such as AgentGym~\cite{xi2024agentgym}, which offers a uni-format platform for LLM agents across diverse environments, and BrowserGym~\cite{drouin2024browsergym}, which standardizes observation and action spaces for web-agent benchmarks. The design principles below capture the converging best practices from these projects.
智能体环境的激增导致了一个碎片化问题：每个环境暴露不同的API，使用不同的观察格式，并且需要不同的脚手架（scaffolding）。\textbf{OpenEnv}~\cite{huggingface2025openenv} 是Hugging Face最近推出的一个开源框架，直接解决了这一问题：它为智能体执行环境提供了Gymnasium风格~\cite{towers2024gymnasium}的接口（\texttt{step()}、\texttt{reset()}、\texttt{state()}），并通过WebSocket通信实现基于Docker的隔离部署。OpenEnv 补充了更广泛的标准化工作，例如AgentGym~\cite{xi2024agentgym}（为跨多样环境的LLM智能体提供统一格式平台）和BrowserGym~\cite{drouin2024browsergym}（标准化Web智能体基准的观察和动作空间）。下面的设计原则捕捉了这些项目中趋于一致的最佳实践。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_064_openenv-arch.png}
\caption{OpenEnv architecture with an LLM agent. The agent reasons via a harness loop, which calls the typed \texttt{EnvClient}. The client communicates over WebSocket to an \texttt{HTTPEnvServer} running inside a Docker container. An RL trainer (dashed) optionally wraps the loop to collect rollouts and reward signals for policy optimization.}
\label{fig:openenv-arch}
\caption{OpenEnv与LLM智能体的架构。智能体通过一个工具循环（harness loop）进行推理，该循环调用类型化的\texttt{EnvClient}。客户端通过WebSocket与运行在Docker容器内的\texttt{HTTPEnvServer}通信。RL训练器（虚线）可选地包装该循环以收集轨迹和奖励信号，用于策略优化。}
\label{fig:openenv-arch}
\end{figure}

\subsection{Standardized Agent--Environment Interface}
\subsection{标准化的智能体-环境接口}
\label{standardized-agentenvironment-interface}
\label{standardized-agentenvironment-interface}

OpenEnv defines a typed interface for agentic execution environments. The design mirrors Gymnasium’s simplicity but targets LLM agents interacting with tools over HTTP/WebSocket:
OpenEnv为智能体执行环境定义了一个类型化接口。其设计模仿了Gymnasium的简洁性，但针对的是通过HTTP/WebSocket与工具交互的LLM智能体：

\begin{itemize}
  \item \texttt{env.reset()} $\to$ \texttt{StepResult}: start a new episode; returns the initial observation.
  \item \texttt{env.reset()} $\to$ \texttt{StepResult}：开始一个新的回合；返回初始观察。
  \item \texttt{env.step(action)} $\to$ \texttt{StepResult(observation, reward, done)}: execute one action and return the resulting observation, scalar reward, and termination flag.
  \item \texttt{env.step(action)} $\to$ \texttt{StepResult(observation, reward, done)}：执行一个动作并返回结果观察、标量奖励和终止标志。
  \item \texttt{env.state()} $\to$ current environment state (episode ID, step count, environment-specific fields).
  \item \texttt{env.state()} $\to$ 当前环境状态（回合ID、步数、环境特定字段）。
  \item \texttt{env.close()}: release resources (stop containers, close connections).
  \item \texttt{env.close()}：释放资源（停止容器、关闭连接）。
\end{itemize}

## Motivation: Why Agents Need Environments
## 动机：为什么智能体需要环境

Actions and observations are strongly typed Python dataclasses, specific to each environment. For example, a coding environment defines \texttt{CodeAction(code=...)} and returns an observation with \texttt{stdout}, \texttt{stderr}, and \texttt{exit\_code}; a game environment defines its own action/observation types. This per-environment typing gives agents structured, predictable interfaces while keeping the three core methods (\texttt{reset}, \texttt{step}, \texttt{state}) universal.
动作和观测是强类型的 Python 数据类（dataclasses），每个环境都有其特定的类型。例如，一个编码环境定义了 \texttt{CodeAction(code=...)} 并返回包含 \texttt{stdout}、\texttt{stderr} 和 \texttt{exit\_code} 的观测；游戏环境则定义自己的动作/观测类型。这种按环境划分的类型系统为智能体提供了结构化、可预测的接口，同时保持了三个核心方法（\texttt{reset}、\texttt{step}、\texttt{state}）的通用性。

\paragraph{Architecture.}
\label{architecture.}
\paragraph{架构。}
\label{architecture.}

Each environment is a Python class inheriting from \texttt{Environment} (implementing \texttt{reset()} and \texttt{step()}). It is served inside a Docker container via \texttt{HTTPEnvServer}, which exposes a FastAPI/WebSocket endpoint. Clients use environment-specific subclasses of \texttt{EnvClient} that handle serialization and connection lifecycle. Containers can be launched locally via \texttt{from\_docker\_image()} or connected to remotely via a base URL:
每个环境都是一个继承自 \texttt{Environment}（实现了 \texttt{reset()} 和 \texttt{step()}）的 Python 类。它通过 \texttt{HTTPEnvServer} 在 Docker 容器中提供服务，该服务器暴露一个 FastAPI/WebSocket 端点。客户端使用 \texttt{EnvClient} 的环境特定子类来处理序列化和连接生命周期。容器可以通过 \texttt{from\_docker\_image()} 在本地启动，或通过基础 URL 远程连接：

\begin{lstlisting}[style=pythonstyle]
from coding_env import CodeAction, CodingEnv

# Option 1: Launch a local Docker container
# 选项 1：启动本地 Docker 容器
client = CodingEnv.from_docker_image("coding-env:latest")

# Option 2: Connect to a remote deployment
# 选项 2：连接到远程部署
# client = CodingEnv(base_url="http://localhost:8000")

# Interact with the environment
# 与环境交互
result = client.reset()
print(result.observation.stdout)
print(result.observation.stderr)
print(result.observation.exit_code)

result = client.step(CodeAction(code="print(2 + 2)"))
print(result.observation.stdout)       # "4\n"
print(result.observation.exit_code)    # 0
print(result.reward, result.done)

# Check state
# 检查状态
state = client.state()
print(state.episode_id, state.step_count)

client.close()
\end{lstlisting}

\paragraph{Environment as a server.}
\label{environment-as-a-server.}
\paragraph{作为服务器的环境。}
\label{environment-as-a-server.}

Creating a new environment requires only implementing the \texttt{Environment} base class:
创建新环境只需要实现 \texttt{Environment} 基类：

\begin{lstlisting}[style=pythonstyle]
from openenv.core.env_server import Environment, create_app
from dataclasses import dataclass

@dataclass
class MyAction:
    text: str

@dataclass
class MyObservation:
    response: str
    reward: float = 0.0
    done: bool = False

class MyEnvironment(Environment):
    def reset(self) -> MyObservation:
        return MyObservation(response="Ready")

    def step(self, action: MyAction) -> MyObservation:
        return MyObservation(response=f"Echo: {action.text}",
                             reward=1.0, done=False)

app = create_app(MyEnvironment(), MyAction, MyObservation)
# Run: uvicorn module:app --host 0.0.0.0 --port 8000
# 运行：uvicorn module:app --host 0.0.0.0 --port 8000
\end{lstlisting}

\paragraph{Harness integration (experimental).}
\label{harness-integration-experimental.}
\paragraph{框架集成（实验性）。}
\label{harness-integration-experimental.}

RFC~0054 introduces a harness-facing layer where RL training frameworks interact with environments through MCP-style tool calls. A \texttt{build\_harness\_rollout\_func()} helper produces a TRL-compatible rollout function, bridging OpenEnv directly into existing training pipelines like TorchForge~\cite{meta2025torchforge}.
RFC~0054 引入了一个面向框架的层，其中强化学习（RL）训练框架通过 MCP 风格的工具调用与环境交互。一个 \texttt{build\_harness\_rollout\_func()} 辅助函数生成一个 TRL 兼容的 rollout 函数，将 OpenEnv 直接桥接到现有的训练流水线中，例如 TorchForge~\cite{meta2025torchforge}。

\paragraph{Governance.}
\label{governance.}
\paragraph{治理。}
\label{governance.}

OpenEnv is openly governed by a technical committee including Meta-PyTorch, NVIDIA, Unsloth, Modal, Prime Intellect, Reflection, and Hugging Face---ensuring that the standard evolves with broad industry input rather than a single vendor’s agenda.
OpenEnv 由一个技术委员会公开治理，成员包括 Meta-PyTorch、NVIDIA、Unsloth、Modal、Prime Intellect、Reflection 和 Hugging Face——确保该标准在广泛的行业输入下发展，而非受单一供应商的议程驱动。

\subsection{Environment Registries and Discovery}
\label{environment-registries-and-discovery}
\subsection{环境注册表与发现}
\label{environment-registries-and-discovery}

OpenEnv environments can be deployed as Hugging Face Spaces or local Docker images, enabling discovery and use without manual installation. The same client interface works regardless of deployment target:
OpenEnv 环境可以部署为 Hugging Face Spaces 或本地 Docker 镜像，无需手动安装即可发现和使用。无论部署目标如何，相同的客户端接口都能工作：

\begin{lstlisting}[style=pythonstyle]
from echo_env import EchoAction, EchoEnv

# Connect to a remote HF Space deployment
# 连接到远程 HF Space 部署
client = EchoEnv(base_url="https://openenv-echo-env.hf.space")
result = client.reset()
print(result.observation.echoed_message)  # "Echo environment ready!"

result = client.step(EchoAction(message="Hello!"))
print(result.observation.echoed_message)  # "Hello!"
print(result.reward)
client.close()
\end{lstlisting}

The OpenEnv ecosystem already spans 70+ environments (OpenSpiel games, Atari, BrowserGym, coding sandboxes, financial RL, traffic simulation, and more). RFC~0025 proposes a formal \emph{tool discovery} protocol so agents can query which actions an unfamiliar environment accepts at runtime.
OpenEnv 生态系统已涵盖 70 多个环境（OpenSpiel 游戏、Atari、BrowserGym、编码沙箱、金融强化学习、交通模拟等）。RFC~0025 提出了一种正式的 \emph{工具发现} 协议，以便智能体可以在运行时查询陌生环境接受哪些动作。

\subsection{Compositional Environments}
\label{compositional-environments}
\subsection{组合式环境}
\label{compositional-environments}

Real agent deployments rarely use a single tool. OpenEnv supports rich environments that expose multiple capabilities through typed actions. For example, a coding environment supports code execution, file I/O, and shell commands within a single sandboxed session:
实际智能体部署很少只使用单一工具。OpenEnv 支持丰富的环境，通过类型化动作暴露多种能力。例如，编码环境在单个沙箱会话中支持代码执行、文件 I/O 和 shell 命令：

\begin{lstlisting}[style=pythonstyle]
from coding_env import CodeAction, CodingEnv

client = CodingEnv.from_docker_image("coding-env:latest")
result = client.reset()

# Execute code
# 执行代码
result = client.step(CodeAction(code="x = 42\nprint(x)"))
print(result.observation.stdout)   # "42"
print(result.observation.exit_code)  # 0

# State persists across steps within an episode
# 在一个 episode 内，状态在步骤间持续存在
result = client.step(CodeAction(code="print(x + 1)"))
print(result.observation.stdout)   # "43"

state = client.state()
print(state.step_count)  # 2

client.close()
\end{lstlisting}

For agents requiring diverse tool access (code + web + files), OpenEnv’s RFC~0036 proposes MCP integration, allowing any MCP-compatible tool server to be wrapped as an OpenEnv environment. Additionally, the \texttt{openenv} CLI can scaffold, build, and deploy new environments to Hugging Face Spaces with a single command.
对于需要多种工具访问（代码 + 网页 + 文件）的智能体，OpenEnv 的 RFC~0036 提出了 MCP 集成，允许任何兼容 MCP 的工具服务器被包装为 OpenEnv 环境。此外，\texttt{openenv} CLI 可以通过单个命令搭建、构建新环境并将其部署到 Hugging Face Spaces。

\subsection{Environment Versioning and Reproducibility}
\label{environment-versioning-and-reproducibility}
\subsection{环境版本控制与可复现性}
\label{environment-versioning-and-reproducibility}

Benchmark integrity requires that environment behavior is frozen at evaluation time. Best practices include:
基准测试的完整性要求环境行为在评估时固定不变。最佳实践包括：

\begin{itemize}
  \item \textbf{Semantic versioning}: \texttt{WebArena-v1.2.0} guarantees backward compatibility within a minor version.
  \item \textbf{语义版本控制}：\texttt{WebArena-v1.2.0} 保证次要版本内的向后兼容性。
  \item \textbf{Docker image pinning}: the environment runtime is packaged as a Docker image with a content-addressed hash.
  \item \textbf{Docker 镜像锁定}：环境运行时被打包为一个带有内容可寻址哈希的 Docker 镜像。
  \item \textbf{Seed-based determinism}: all stochastic elements (procedural generation, network responses) are seeded and logged so that any trajectory can be exactly replayed.
  \item \textbf{基于种子的确定性}：所有随机元素（程序化生成、网络响应）都通过种子设定并记录，以便任何轨迹都可以精确重放。
  \item \textbf{Leaderboard snapshots}: public leaderboards record the environment version alongside the score, preventing silent benchmark drift.
  \item \textbf{排行榜快照}：公开排行榜记录环境版本及其得分，防止基准测试悄然漂移。
\end{itemize}

\section{Building Custom Environments}
\label{sec:custom-env}
\section{构建自定义环境}
\label{sec:custom-env}

\subsection{Gymnasium-Style API for LLM Agents}
\label{gymnasium-style-api-for-llm-agents}
\subsection{面向 LLM 智能体的 Gymnasium 风格 API}
\label{gymnasium-style-api-for-llm-agents}

The Gymnasium API~\cite{towers2024gymnasium}7 (successor to OpenAI Gym) is the de facto standard for RL environments. Adapting it for LLM agents requires two modifications: (1) observations and actions are strings (or dicts containing strings) rather than numeric arrays, and (2) the \texttt{step} method must handle asynchronous tool execution.
Gymnasium API~\cite{towers2024gymnasium}（OpenAI Gym 的继任者）是强化学习环境的事实标准。将其适配到 LLM 智能体需要两项修改：（1）观测和动作是字符串（或包含字符串的字典）而非数值数组；（2）\texttt{step} 方法必须处理异步工具执行。

\subsection{Reward Function Engineering}
\label{reward-function-engineering}
\subsection{奖励函数工程}
\label{reward-function-engineering}

Reward functions for LLM agent environments are typically \emph{execution-based}: the environment runs a verifier after each episode and returns 1 if the task is solved, 0 otherwise. For tasks without a clear verifier, options include:
面向 LLM 智能体环境的奖励函数通常是 \emph{基于执行的}：环境在每个 episode 后运行一个验证器，如果任务解决则返回 1，否则返回 0。对于没有明确验证器的任务，选项包括：

\begin{itemize}
  \item \textbf{LLM-as-judge}: a separate LLM scores the agent’s final state against the task description.
  \item \textbf{LLM 作为裁判}：另一个独立的 LLM 根据任务描述对智能体的最终状态进行评分。
  \item \textbf{Rubric-based scoring}: a structured rubric decomposes the task into sub-criteria, each scored independently.
  \item \textbf{基于评分标准的评分}：一个结构化的评分标准将任务分解为子标准，每个子标准独立评分。
  \item \textbf{Human annotation}: a human evaluator scores a random sample of trajectories; the scores are used to calibrate an automated proxy.
  \item \textbf{人工标注}：人工评估者对 trajectories 的随机样本进行评分；这些评分用于校准自动化代理。
\end{itemize}

\subsection{State Management and Checkpointing}
\label{state-management-and-checkpointing}
\subsection{状态管理与检查点}
\label{state-management-and-checkpointing}

Long-horizon tasks may require hours of wall time. Environments should support:
长周期任务可能需要数小时的挂钟时间。环境应支持：

```markdown
\begin{itemize}
  \item \textbf{State serialization}: the full environment state (filesystem, browser cookies, database contents) can be serialized to disk and restored.
  \item \textbf{状态序列化}：完整的环境状态（文件系统、浏览器 cookie、数据库内容）可以序列化到磁盘并恢复。
  \item \textbf{Mid-episode checkpointing}: the agent can save a checkpoint at any step and resume from it, enabling tree-search-style exploration.
  \item \textbf{回合中间检查点}：智能体可以在任何步骤保存检查点并从中恢复，从而实现树搜索式探索。
  \item \textbf{Trajectory logging}: every observation, action, and reward is logged to a structured file for offline analysis and reward model training.
  \item \textbf{轨迹日志记录}：每次观测、动作和奖励都被记录到结构化文件中，用于离线分析和奖励模型训练。
\end{itemize}

\subsection{Parallelization for Training Data Collection}
\label{parallelization-for-training-data-collection}
\subsection{训练数据收集的并行化}
\label{parallelization-for-training-data-collection}

Training LLM agents via RL requires millions of environment interactions. Parallelization strategies include:
通过强化学习训练 LLM 智能体需要数百万次环境交互。并行化策略包括：

\begin{itemize}
  \item \textbf{Process-level parallelism}: spawn $N$ independent environment processes; collect trajectories in parallel.
  \item \textbf{进程级并行}：启动 $N$ 个独立的环境进程；并行收集轨迹。
  \item \textbf{Async rollout workers}: use an async event loop (e.g., \texttt{asyncio}) to overlap LLM inference latency with environment execution.
  \item \textbf{异步回滚工作器}：使用异步事件循环（例如 \texttt{asyncio}）将 LLM 推理延迟与环境执行重叠。
  \item \textbf{Vectorized environments}: batch multiple environments into a single \texttt{step} call, amortizing Python overhead.
  \item \textbf{向量化环境}：将多个环境批量处理到单个 \texttt{step} 调用中，分摊 Python 开销。
  \item \textbf{Cloud-native scaling}: use a job scheduler (Ray, SLURM) to distribute environment workers across a cluster, with a central replay buffer aggregating trajectories.
  \item \textbf{云原生扩展}：使用作业调度器（Ray、SLURM）将环境工作器分布到集群中，并通过中央回放缓冲区聚合轨迹。
\end{itemize}

\section{Environment--Agent Interface Patterns}
\label{sec:interface-patterns}
\section{环境-智能体接口模式}
\label{sec:interface-patterns}

Figure~\ref{fig:env-agent-interface} illustrates the four main interface patterns used in practice.
图~\ref{fig:env-agent-interface} 展示了实际中使用的四种主要接口模式。

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_065_env-agent-interface.png}
\caption{Four agent--environment interface patterns. (a) Text-based is the most common for LLMs. (b) Structured JSON enables precise parsing. (c) Multimodal combines screenshots with accessibility trees for GUI tasks. (d) Streaming supports real-time interaction without discrete turn boundaries.}
\label{fig:env-agent-interface}
\end{figure}
\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_065_env-agent-interface.png}
\caption{四种智能体-环境接口模式。(a) 基于文本的接口在 LLM 中最常见。(b) 结构化 JSON 支持精确解析。(c) 多模态接口将截图与无障碍树结合用于 GUI 任务。(d) 流式接口支持实时交互，无需离散的回合边界。}
\label{fig:env-agent-interface}
\end{figure}

\paragraph{Text-Based Observation/Action.}
\label{text-based-observationaction.}
\paragraph{基于文本的观测/动作。}
\label{text-based-observationaction.}

The agent receives a string observation and produces a string action. The environment parses the action (e.g., extracts a tool call from a \texttt{<tool>...</tool>} block) and returns the result as a string. This is the most compatible pattern: any LLM can participate without special architecture.
智能体接收字符串形式的观测，并产生字符串形式的动作。环境解析动作（例如从 \texttt{<tool>...</tool>} 块中提取工具调用），并以字符串形式返回结果。这是最兼容的模式：任何 LLM 都可以参与，无需特殊架构。

\paragraph{Structured JSON Observation/Action.}
\label{structured-json-observationaction.}
\paragraph{结构化 JSON 观测/动作。}
\label{structured-json-observationaction.}

Observations and actions are JSON objects with a defined schema. This enables strict validation (reject malformed actions before execution), structured logging, and easier programmatic analysis of trajectories. The tradeoff is that the agent must reliably produce valid JSON, which requires either fine-tuning or constrained decoding.
观测和动作是带有定义模式（schema）的 JSON 对象。这支持严格验证（在执行前拒绝格式错误的动作）、结构化日志记录，以及更轻松的程序化轨迹分析。代价是智能体必须可靠地生成有效的 JSON，这需要微调或约束解码（constrained decoding）。

\paragraph{Multimodal (Screenshot + Accessibility Tree).}
\label{multimodal-screenshot-accessibility-tree.}
\paragraph{多模态（截图 + 无障碍树）。}
\label{multimodal-screenshot-accessibility-tree.}

Used in computer-use and web environments. The observation is a tuple \texttt{(screenshot: PIL.Image, a11y\_tree: dict)}. The screenshot provides visual context; the accessibility tree provides element identifiers that can be used in actions without pixel-level coordinate specification. This hybrid approach is more robust than pure screenshot-based control.
用于计算机操作和网页环境。观测是一个元组 \texttt{(screenshot: PIL.Image, a11y\_tree: dict)}。截图提供视觉上下文；无障碍树提供元素标识符，可用于动作而无需像素级坐标指定。这种混合方法比纯基于截图的控制更鲁棒。

\paragraph{Streaming vs.~Turn-Based Interaction.}
\label{streaming-vs.-turn-based-interaction.}
\paragraph{流式交互 vs. 回合制交互。}
\label{streaming-vs.-turn-based-interaction.}

Most current environments use a turn-based model: the agent produces a complete action, the environment executes it, and the next observation is returned. Streaming environments allow the agent to receive partial observations as they arrive (e.g., the output of a long-running command) and to interrupt or redirect execution mid-stream. This is closer to how humans interact with computers but requires more complex agent architectures.
目前大多数环境使用回合制模型：智能体产生一个完整的动作，环境执行它，然后返回下一个观测。流式环境允许智能体在部分观测到达时立即接收（例如长时间运行命令的输出），并在流中中断或重定向执行。这更接近人类与计算机的交互方式，但需要更复杂的智能体架构。

\section{Evaluation Harness Design}
\label{sec:eval-harness}
\section{评估框架设计}
\label{sec:eval-harness}

An evaluation harness is the infrastructure that runs an agent across a benchmark suite, collects results, and produces summary statistics. Good harness design is as important as good environment design.
评估框架（Evaluation Harness）是运行智能体遍历基准套件、收集结果并生成汇总统计的基础设施。好的框架设计与好的环境设计同等重要。

\subsection{Deterministic vs.~Stochastic Environments}
\label{deterministic-vs.-stochastic-environments}
\subsection{确定性环境 vs. 随机性环境}
\label{deterministic-vs.-stochastic-environments}

\begin{itemize}
  \item \textbf{Deterministic environments} produce the same observation sequence for the same action sequence. They are easy to debug and reproduce but may not reflect real-world variability.
  \item \textbf{确定性环境}：对相同的动作序列产生相同的观测序列。它们易于调试和复现，但可能无法反映现实世界的可变性。
  \item \textbf{Stochastic environments} introduce randomness (procedural generation, network latency, user simulation). They require multiple runs per task to estimate mean performance and confidence intervals.
  \item \textbf{随机性环境}：引入随机性（程序化生成、网络延迟、用户模拟）。它们需要对每个任务多次运行，以估计平均性能和置信区间。
\end{itemize}

\begin{questionbox}[How Many Runs Are Enough?]
For a benchmark with $N$ tasks and binary rewards, the standard error of the mean success rate is $\sqrt{p(1-p)/N}$. With $N=500$ tasks and $p=0.4$, the 95\% confidence interval is approximately $\pm 4.3\%$. For stochastic environments, multiply by $\sqrt{k}$ where $k$ is the number of independent runs per task. A common practice is 3--5 runs per task for stochastic benchmarks.
\end{questionbox}
\begin{questionbox}[多少次运行足够？]
对于一个包含 $N$ 个任务和二值奖励的基准，平均成功率的标准误差为 $\sqrt{p(1-p)/N}$。当 $N=500$ 个任务且 $p=0.4$ 时，95\% 置信区间约为 $\pm 4.3\%$。对于随机性环境，乘以 $\sqrt{k}$，其中 $k$ 是每个任务的独立运行次数。对于随机性基准，常见做法是每个任务运行 3--5 次。
\end{questionbox}

\subsection{Held-Out Test Environments}
\label{held-out-test-environments}
\subsection{留出测试环境}
\label{held-out-test-environments}

Benchmark integrity requires a strict train/test split at the \emph{environment} level, not just the task level. An agent that has been trained on WebArena tasks should be evaluated on a held-out set of tasks that were not used during training. Ideally, the held-out set covers different websites, task types, and difficulty levels than the training set.
基准的完整性要求在\emph{环境}层面（而不仅仅是任务层面）进行严格的训练/测试划分。在 WebArena 任务上训练过的智能体，应该在一个未在训练中使用过的留出任务集上评估。理想情况下，留出集包含与训练集不同的网站、任务类型和难度级别。

\subsection{Cross-Environment Generalization}
\label{cross-environment-generalization}
\subsection{跨环境泛化}
\label{cross-environment-generalization}

The ultimate test of an agent is whether skills learned in one environment transfer to another. Cross-environment evaluation protocols measure:
智能体的终极测试是：在一个环境中学到的技能是否能迁移到另一个环境。跨环境评估协议衡量：

\begin{itemize}
  \item \textbf{Zero-shot transfer}: train on environment A, test on environment B with no fine-tuning.
  \item \textbf{零样本迁移}：在环境 A 上训练，在环境 B 上测试，不进行微调。
  \item \textbf{Few-shot adaptation}: provide $k$ demonstrations from environment B before evaluation.
  \item \textbf{少样本适应}：在评估前提供来自环境 B 的 $k$ 个示范。
  \item \textbf{Continual learning}: train sequentially on environments A, B, C; measure performance on all three after training on C.
  \item \textbf{持续学习}：依次在环境 A、B、C 上训练；在 C 上训练后测量所有三个环境上的性能。
\end{itemize}

\subsection{Human Baseline Collection}
\label{human-baseline-collection}
\subsection{人类基线收集}
\label{human-baseline-collection}

Every benchmark should include human performance as a reference point. Human baselines serve three purposes:
每个基准都应包含人类表现作为参考点。人类基线有三个目的：

\begin{enumerate}
  \item They establish an upper bound on task difficulty.
  \item 它们建立任务难度的上限。
  \item They reveal whether a task is solvable at all (some benchmark tasks turn out to be ambiguous or impossible).
  \item 它们揭示任务是否根本可解（有些基准任务可能实际上是模糊或不可能的）。
  \item They provide a calibration point for interpreting agent scores (``the agent achieves 40\% of human performance'').
  \item 它们为解释智能体得分提供校准点（“智能体达到了人类表现的 40%”）。
\end{enumerate}

Human baselines should be collected from workers with domain expertise (e.g., software engineers for SWE-bench, not crowdworkers) and should include time-on-task measurements to enable efficiency comparisons.
人类基线应从具有领域专业知识的工人（例如 SWE-bench 的软件工程师，而非众包工人）处收集，并应包含任务时间测量，以便进行效率比较。

\section{Code Example: Minimal Custom LLM Agent Environment}
\label{sec:code-example}
\section{代码示例：最小自定义 LLM 智能体环境}
\label{sec:code-example}

\begin{examplebox}[Minimal Custom Environment for LLM Agent Training]
The following Python class implements a file-editing environment where the agent must modify a Python file to make a failing test pass. It follows the Gymnasium API adapted for LLM agents.
\end{examplebox}
\begin{examplebox}[用于 LLM 智能体训练的最小自定义环境]
以下 Python 类实现了一个文件编辑环境，智能体必须修改一个 Python 文件以使失败的测试通过。它遵循为 LLM 智能体调整的 Gymnasium API。
\end{examplebox}

\begin{lstlisting}[style=pythonstyle, caption={Minimal LLM agent environment following the Gymnasium API.}]
"""
minimal_env.py  --  A minimal file-editing environment for LLM agents.
minimal_env.py  --  一个用于 LLM 智能体的最小文件编辑环境。

The agent receives a Python file with a bug and a failing test.
智能体接收一个包含 bug 的 Python 文件和一个失败的测试。
It must edit the file until the test passes.
它必须编辑文件直到测试通过。
Reward: 1.0 if all tests pass, 0.0 otherwise.
奖励：所有测试通过得 1.0，否则得 0.0。
"""

from __future__ import annotations
import subprocess, shutil, tempfile, textwrap
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Data structures
# 数据结构
# ---------------------------------------------------------------------------
```

```markdown
@dataclass
class StepResult:
    observation: str          # Text fed to the LLM
    reward: float             # 0.0 or 1.0
    terminated: bool          # Episode over (task solved or max steps)
    truncated: bool           # Episode cut short (budget exceeded)
    info: dict[str, Any] = field(default_factory=dict)

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------


class FileEditEnv:
    """
    A Gymnasium-style environment for LLM-based code repair.

    Observation space : str  (file contents + test output)
    Action space      : str  (one of: view, edit, run_tests, submit)
    Reward            : 1.0 on passing all tests, 0.0 otherwise
    """

    MAX_STEPS = 20          # Hard episode limit
    TIMEOUT   = 30          # Seconds per test run

    def __init__(self, buggy_code: str, test_code: str,
                 task_description: str):
        self.buggy_code       = buggy_code
        self.test_code        = test_code
        self.task_description = task_description
        self._workdir: Path | None = None
        self._step_count = 0

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def reset(self, seed: int | None = None) -> tuple[str, dict]:
        """Initialise a fresh episode; return (observation, info)."""
        if self._workdir and self._workdir.exists():
            shutil.rmtree(self._workdir)

        self._workdir    = Path(tempfile.mkdtemp(prefix="fileenv_"))
        self._step_count = 0

        # Write initial files
        (self._workdir / "solution.py").write_text(self.buggy_code)
        (self._workdir / "test_solution.py").write_text(self.test_code)

        obs = self._build_observation(
            action_taken="[Episode start]",
            test_output=self._run_tests()
        )
        return obs, {"step": 0}

    def step(self, action: str) -> StepResult:
        """Execute one agent action; return StepResult."""
        self._step_count += 1
        action = action.strip()

        # --- Parse and dispatch action ---
        if action.startswith("view"):
            result_text = self._action_view()
        elif action.startswith("edit"):
            result_text = self._action_edit(action)
        elif action.startswith("run_tests"):
            result_text = self._run_tests()
        elif action.startswith("submit"):
            result_text = self._run_tests()
        else:
            result_text = (
                f"Unknown action: {action!r}\n"
                "Valid actions: view | edit <new_content> | "
                "run_tests | submit"
            )

        test_output = self._run_tests()
        passed      = "passed" in test_output and "failed" not in test_output
        reward      = 1.0 if passed else 0.0
        terminated  = passed or action.startswith("submit")
        truncated   = self._step_count >= self.MAX_STEPS

        obs = self._build_observation(action, test_output)
        return StepResult(obs, reward, terminated, truncated,
                          {"step": self._step_count,
                           "passed": passed})

    def render(self) -> str:
        """Return a human-readable summary of the current state."""
        if self._workdir is None:
            return "[Environment not initialised]"
        code = (self._workdir / "solution.py").read_text()
        return f"=== solution.py ===\n{code}\n"

    def close(self) -> None:
        """Release resources."""
        if self._workdir and self._workdir.exists():
            shutil.rmtree(self._workdir)
            self._workdir = None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _action_view(self) -> str:
        code = (self._workdir / "solution.py").read_text()
        return f"Current solution.py:\n```python\n{code}\n```"

    def _action_edit(self, action: str) -> str:
        # Expect: edit\n```python\n<code>\n```
        try:
            new_code = action.split("```python")[1].split("```")[0]
            (self._workdir / "solution.py").write_text(new_code)
            return "File updated successfully."
        except IndexError:
            return "Edit failed: wrap new code in ```python ... ```"

    def _run_tests(self) -> str:
        result = subprocess.run(
            ["python", "-m", "pytest", "test_solution.py",
             "-v", "--tb=short", "--no-header"],
            cwd=self._workdir,
            capture_output=True, text=True,
            timeout=self.TIMEOUT
        )
        return result.stdout + result.stderr

    def _build_observation(self, action_taken: str,
                           test_output: str) -> str:
        code = (self._workdir / "solution.py").read_text()
        return textwrap.dedent(f"""
            TASK: {self.task_description}
            STEP: {self._step_count}/{self.MAX_STEPS}

            --- Last action ---
            {action_taken}

            --- Current solution.py ---
            {code}

            --- Test output ---
            {test_output}

            --- Available actions ---
            view                          # show current file
            edit\n```python\n<code>\n```  # replace file contents
            run_tests                     # run pytest
            submit                        # finalise and end episode
        """).strip()


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    BUGGY = "def add(a, b):\n    return a - b\n"   # bug: minus not plus
    TESTS = (
        "from solution import add\n"
        "def test_add(): assert add(2, 3) == 5\n"
    )

    env = FileEditEnv(BUGGY, TESTS, "Fix the add() function.")
    obs, _ = env.reset(seed=0)
    print(obs)

    # Simulate one correct edit
    fix = "edit\n```python\ndef add(a, b):\n    return a + b\n```"
    result = env.step(fix)
    print(f"\nReward: {result.reward}  |  Terminated: {result.terminated}")
    env.close()
\end{lstlisting}


\begin{keybox}[Design Decisions in the Example Environment]
\begin{itemize}
  \item \textbf{Text-only interface}: observations and actions are plain strings, compatible with any LLM.
  \item \textbf{Execution-based reward}: the reward is derived from running the actual test suite, not from an LLM judge. This makes it tamper-proof and perfectly aligned.
  \item \textbf{Isolated subprocess}: tests run in a separate process with a timeout, preventing infinite loops from crashing the training loop.
  \item \textbf{Gymnasium-compatible}: \texttt{reset}/\texttt{step}/ \texttt{render}/\texttt{close} follow the standard API, enabling drop-in use with RL training frameworks.
\end{itemize}
\end{keybox}


\section{Comparison of Major Agentic Environments}
\label{sec:env-comparison}


Table~\ref{tab:env-comparison} summarizes the key properties of the major agentic environments discussed in this section.

@dataclass
class StepResult:
    observation: str          # 提供给LLM的文本
    reward: float             # 0.0 或 1.0
    terminated: bool          # 回合结束（任务解决或达到最大步数）
    truncated: bool           # 回合被截断（预算超限）
    info: dict[str, Any] = field(default_factory=dict)

# ---------------------------------------------------------------------------
# 环境
# ---------------------------------------------------------------------------

class FileEditEnv:
    """
    一个基于LLM的代码修复的Gymnasium风格环境。

    观测空间 : str  （文件内容 + 测试输出）
    动作空间 : str  （view, edit, run_tests, submit 之一）
    奖励    : 所有测试通过时1.0，否则0.0
    """

    MAX_STEPS = 20          # 硬性回合限制
    TIMEOUT   = 30          # 每次测试运行的秒数

    def __init__(self, buggy_code: str, test_code: str,
                 task_description: str):
        self.buggy_code       = buggy_code
        self.test_code        = test_code
        self.task_description = task_description
        self._workdir: Path | None = None
        self._step_count = 0

    # ------------------------------------------------------------------
    # 核心API
    # ------------------------------------------------------------------

    def reset(self, seed: int | None = None) -> tuple[str, dict]:
        """初始化一个新回合；返回 (observaton, info)。"""
        if self._workdir and self._workdir.exists():
            shutil.rmtree(self._workdir)

        self._workdir    = Path(tempfile.mkdtemp(prefix="fileenv_"))
        self._step_count = 0

        # 写入初始文件
        (self._workdir / "solution.py").write_text(self.buggy_code)
        (self._workdir / "test_solution.py").write_text(self.test_code)

        obs = self._build_observation(
            action_taken="[Episode start]",
            test_output=self._run_tests()
        )
        return obs, {"step": 0}

    def step(self, action: str) -> StepResult:
        """执行一个智能体动作；返回 StepResult。"""
        self._step_count += 1
        action = action.strip()

        # --- 解析并分发动作 ---
        if action.startswith("view"):
            result_text = self._action_view()
        elif action.startswith("edit"):
            result_text = self._action_edit(action)
        elif action.startswith("run_tests"):
            result_text = self._run_tests()
        elif action.startswith("submit"):
            result_text = self._run_tests()
        else:
            result_text = (
                f"未知动作: {action!r}\n"
                "有效动作: view | edit <new_content> | "
                "run_tests | submit"
            )

        test_output = self._run_tests()
        passed      = "passed" in test_output and "failed" not in test_output
        reward      = 1.0 if passed else 0.0
        terminated  = passed or action.startswith("submit")
        truncated   = self._step_count >= self.MAX_STEPS

        obs = self._build_observation(action, test_output)
        return StepResult(obs, reward, terminated, truncated,
                          {"step": self._step_count,
                           "passed": passed})

    def render(self) -> str:
        """返回当前状态的人类可读摘要。"""
        if self._workdir is None:
            return "[环境未初始化]"
        code = (self._workdir / "solution.py").read_text()
        return f"=== solution.py ===\n{code}\n"

    def close(self) -> None:
        """释放资源。"""
        if self._workdir and self._workdir.exists():
            shutil.rmtree(self._workdir)
            self._workdir = None

    # ------------------------------------------------------------------
    # 私有辅助函数
    # ------------------------------------------------------------------

    def _action_view(self) -> str:
        code = (self._workdir / "solution.py").read_text()
        return f"当前 solution.py:\n```python\n{code}\n```"

    def _action_edit(self, action: str) -> str:
        # 期望格式: edit\n```python\n<代码>\n```
        try:
            new_code = action.split("```python")[1].split("```")[0]
            (self._workdir / "solution.py").write_text(new_code)
            return "文件已成功更新。"
        except IndexError:
            return "编辑失败：请将新代码包裹在 ```python ... ``` 中"

    def _run_tests(self) -> str:
        result = subprocess.run(
            ["python", "-m", "pytest", "test_solution.py",
             "-v", "--tb=short", "--no-header"],
            cwd=self._workdir,
            capture_output=True, text=True,
            timeout=self.TIMEOUT
        )
        return result.stdout + result.stderr

    def _build_observation(self, action_taken: str,
                           test_output: str) -> str:
        code = (self._workdir / "solution.py").read_text()
        return textwrap.dedent(f"""
            任务: {self.task_description}
            步数: {self._step_count}/{self.MAX_STEPS}

            --- 上一步动作 ---
            {action_taken}

            --- 当前 solution.py ---
            {code}

            --- 测试输出 ---
            {test_output}

            --- 可用动作 ---
            view                          # 显示当前文件
            edit\n```python\n<代码>\n```  # 替换文件内容
            run_tests                     # 运行 pytest
            submit                        # 完成并结束回合
        """).strip()


# ---------------------------------------------------------------------------
# 示例用法
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    BUGGY = "def add(a, b):\n    return a - b\n"   # 错误：减号而不是加号
    TESTS = (
        "from solution import add\n"
        "def test_add(): assert add(2, 3) == 5\n"
    )

    env = FileEditEnv(BUGGY, TESTS, "修复 add() 函数。")
    obs, _ = env.reset(seed=0)
    print(obs)

    # 模拟一次正确的编辑
    fix = "edit\n```python\ndef add(a, b):\n    return a + b\n```"
    result = env.step(fix)
    print(f"\n奖励: {result.reward}  |  已终止: {result.terminated}")
    env.close()
\end{lstlisting}

\begin{keybox}[示例环境中的设计决策]
\begin{itemize}
  \item \textbf{纯文本接口 (Text-only interface)}：观测和动作都是纯字符串，与任何 LLM 兼容。
  \item \textbf{基于执行的奖励 (Execution-based reward)}：奖励来自运行实际测试套件，而非 LLM 评判。这使其不可篡改且完美对齐。
  \item \textbf{隔离子进程 (Isolated subprocess)}：测试在独立的进程中运行并设置超时，防止无限循环使训练循环崩溃。
  \item \textbf{兼容 Gymnasium (Gymnasium-compatible)}：\texttt{reset}/\texttt{step}/\texttt{render}/\texttt{close} 遵循标准 API，可即插即用于 RL 训练框架。
\end{itemize}
\end{keybox}

\section{主要智能体环境对比}
\label{sec:env-comparison}

表~\ref{tab:env-comparison} 总结了本节讨论的主要智能体环境的关键属性。
```

\begin{table}[ht!]
\centering
\caption{Comparison of major agentic environments for LLM agents. ``SoTA'' refers to the best published LLM agent result at the time of writing. Human performance is shown where available.}
\caption{主要大语言模型智能体环境的比较。``SoTA''指撰写时已发表的最佳大语言模型智能体结果。人类表现（Human performance）在可用时给出。}
\label{tab:env-comparison}
\begin{tabular}{@{}lp{2.1cm}p{2.1cm}p{2.1cm}p{2.1cm}p{2.1cm}p{2.1cm}@{}}
\toprule
\textbf{Environment} & \textbf{Obs.~Type} & \textbf{Action Space} & \textbf{Domain} & \textbf{\# Tasks} & \textbf{Human} & \textbf{SoTA LLM} \\
\textbf{环境} & \textbf{观测类型} & \textbf{动作空间} & \textbf{领域} & \textbf{任务数} & \textbf{人类} & \textbf{最佳大语言模型} \\
\midrule
WebArena & Text + DOM & Browser API & Web navigation & 812 & 78\% & $\sim$45\% \\
WebArena & 文本 + DOM & 浏览器API & 网页导航 & 812 & 78\% & $\sim$45\% \\
VisualWebArena & Screenshot + DOM & Browser API & Visual web & 910 & 88\% & $\sim$35\% \\
VisualWebArena & 截图 + DOM & 浏览器API & 视觉网页 & 910 & 88\% & $\sim$35\% \\
Mind2Web & Screenshot + DOM & Browser API & Real websites & 2,000 & --- & $\sim$30\% \\
Mind2Web & 截图 + DOM & 浏览器API & 真实网站 & 2,000 & --- & $\sim$30\% \\
OSWorld & Screenshot & Mouse + keyboard & Desktop OS & 369 & 72\% & $\sim$18\% \\
OSWorld & 截图 & 鼠标 + 键盘 & 桌面操作系统 & 369 & 72\% & $\sim$18\% \\
WindowsAgentArena & Screenshot & Mouse + keyboard & Windows apps & 154 & 75\% & $\sim$20\% \\
WindowsAgentArena & 截图 & 鼠标 + 键盘 & Windows应用 & 154 & 75\% & $\sim$20\% \\
SWE-bench Verified & Text (repo) & Shell + editor & Code repair & 500 & 100\% & $\sim$50\% \\
SWE-bench Verified & 文本（仓库） & Shell + 编辑器 & 代码修复 & 500 & 100\% & $\sim$50\% \\
GAIA (Level 1) & Text + files & Tool calls & General QA & 165 & 92\% & $\sim$55\% \\
GAIA（等级1） & 文本 + 文件 & 工具调用 & 通用问答 & 165 & 92\% & $\sim$55\% \\
GAIA (Level 3) & Text + files & Tool calls & Hard QA & 42 & 92\% & $\sim$10\% \\
GAIA（等级3） & 文本 + 文件 & 工具调用 & 困难问答 & 42 & 92\% & $\sim$10\% \\
NetHack (NLE) & Text + glyphs & Discrete actions & Roguelike game & --- & $>$10k score & $\sim$5k score \\
NetHack（NLE） & 文本 + 字形 & 离散动作 & Roguelike游戏 & --- & $>$10k得分 & $\sim$5k得分 \\
Voyager (Minecraft) & Text + code & Code execution & Open-world game & Curriculum & --- & 15+ tech tree \\
Voyager（Minecraft） & 文本 + 代码 & 代码执行 & 开放世界游戏 & 课程式 & --- & 15+科技树 \\
MLAgentBench & Text + code & Shell + editor & ML engineering & 13 & --- & $\sim$40\% \\
MLAgentBench & 文本 + 代码 & Shell + 编辑器 & 机器学习工程 & 13 & --- & $\sim$40\% \\
\bottomrule
\end{tabular}
\end{table}

\begin{intuitionbox}[Reading the Comparison Table]
\begin{intuitionbox}[解读比较表格]
The gap between human performance and SoTA LLM performance is largest for \emph{computer use} tasks (OSWorld: 72\% vs.~18\%) and smallest for \emph{code repair} (SWE-bench: 100\% vs.~50\%). This pattern reflects the maturity of the action space: LLMs have been trained on vast amounts of code but relatively little screenshot-based interaction data. As computer-use training data accumulates, the gap is expected to narrow.
人类表现与最佳大语言模型表现之间的差距在\emph{计算机使用}任务（OSWorld：72\% vs.~18\%）中最大，在\emph{代码修复}（SWE-bench：100\% vs.~50\%）中最小。这种模式反映了动作空间的成熟度：大语言模型在大量代码上进行了训练，但相对缺乏基于截图的交互数据。随着计算机使用训练数据的积累，这一差距预计将会缩小。
\end{intuitionbox}

\section{Summary}
\section{总结}
\label{sec:env-summary}

Agentic environments are the substrate on which LLM agents are trained and evaluated. The key takeaways from this section are:
智能体环境（Agentic environments）是大语言模型智能体进行训练和评估的基座。本节的关键要点如下：

\begin{enumerate}
  \item \textbf{Environments are not optional.} Safe exploration, reproducible evaluation, and curriculum learning all require a structured environment. The gap between chatbot and agent evaluation cannot be bridged without one.
  \item \textbf{环境并非可选。} 安全探索、可复现评估以及课程学习（curriculum learning）都需要结构化的环境。没有环境，聊天机器人与智能体评估之间的鸿沟就无法弥合。
  \item \textbf{Design all four axes carefully.} Observation space, action space, reward signal, and episode structure each have failure modes that can invalidate an entire benchmark.
  \item \textbf{仔细设计四个轴线。} 观测空间（observation space）、动作空间（action space）、奖励信号（reward signal）和回合结构（episode structure）各自存在失效模式，可能导致整个基准测试失效。
  \item \textbf{The landscape is rich but fragmented.} Code sandboxes, web environments, computer-use environments, SWE environments, scientific environments, games, and multi-agent arenas each test different capabilities. No single environment is sufficient.
  \item \textbf{领域丰富但碎片化。} 代码沙箱、网页环境、计算机使用环境、软件工程环境、科学环境、游戏以及多智能体竞技场各自测试不同的能力。没有任何单一环境能够满足所有需求。
  \item \textbf{Standardization matters.} OpenEnv~\cite{huggingface2025openenv} provides a Gymnasium-style API with Docker isolation and Hugging Face Spaces as a registry---reducing the cost of building new environments and comparing agents across them.
  \item \textbf{标准化很重要。} OpenEnv~\cite{huggingface2025openenv} 提供了Gymnasium风格的API，具备Docker隔离和Hugging Face Spaces作为注册中心——降低了构建新环境以及跨环境比较智能体的成本。
  \item \textbf{The human gap is real and closing.} Current LLM agents achieve 20--50\% of human performance on most benchmarks. The fastest progress is in domains with abundant training data (code) and the slowest in domains requiring fine-grained perception (GUI control).
  \item \textbf{与人类的差距真实存在且正在缩小。} 当前的大语言模型智能体在大多数基准测试上达到了人类表现的20%–50%。进步最快的领域是训练数据丰富的领域（代码），最慢的则是需要细粒度感知的领域（GUI控制）。
\end{enumerate}

\begin{questionbox}[Open Research Questions in Agentic Environments]
\begin{questionbox}[智能体环境中的开放研究问题]
\begin{itemize}
  \item How do we design reward functions for tasks where correctness is subjective or context-dependent?
  \item 如何为正确性主观或依赖上下文的任务设计奖励函数？
  \item Can a single agent architecture generalize across text-based and multimodal environments without task-specific fine-tuning?
  \item 单一智能体架构能否在无需特定任务微调的情况下，跨文本环境与多模态环境进行泛化？
  \item What is the right level of environment fidelity for training? Does training on simplified simulators transfer to real deployments?
  \item 训练所需的环境保真度（environment fidelity）应达到什么水平？在简化模拟器上的训练能否迁移到真实部署中？
  \item How do we prevent benchmark contamination as LLMs are trained on ever-larger web corpora that may include benchmark solutions?
  \item 随着大语言模型在可能包含基准测试解决方案的日益庞大的网络语料库上训练，如何防止基准测试污染？
\end{itemize}
\end{questionbox}