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

