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

