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

