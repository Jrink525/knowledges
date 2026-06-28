# 当任务在各个状态之间转换时，服务器会向 webhook URL 发送 POST 请求，携带 TaskStatusUpdateEvent 对象。
\end{lstlisting}

## Message Format
## 消息格式

A2A messages consist of a \textbf{role} (\texttt{user} or \texttt{agent}) plus a list of typed \textbf{parts} (text, file, or structured data). The full message schema, multi-modal examples, and context-passing guidelines are covered in Section~\ref{sec:a2a:messages}.
A2A 消息由一个 \textbf{角色（role）}（\texttt{user} 或 \texttt{agent}）加上一个带类型的 \textbf{部件（parts）}列表（文本、文件或结构化数据）组成。完整的消息模式、多模态示例以及上下文传递指南将在第~\ref{sec:a2a:messages} 节中介绍。

## Authentication and Authorization
## 身份认证与授权

A2A supports multiple authentication schemes, declared in the Agent Card and enforced per-request:
A2A 支持多种身份认证方案，这些方案在 Agent Card（智能体卡片）中声明，并在每个请求中强制执行：

\begin{itemize}
  \item \textbf{Bearer tokens (JWT/OAuth 2.0)}: Standard for enterprise deployments; tokens carry scopes that limit what the calling agent is permitted to request.
  \item \textbf{Bearer 令牌（JWT/OAuth 2.0）}：企业部署的标准；令牌携带作用域（scopes），限制调用智能体被允许请求的内容。
  \item \textbf{API keys}: Simpler scheme for internal or trusted environments.
  \item \textbf{API 密钥}：适用于内部或可信环境的更简单的方案。
  \item \textbf{Mutual TLS (mTLS)}: Certificate-based authentication for high-security deployments.
  \item \textbf{双向 TLS（mTLS）}：基于证书的身份认证，适用于高安全性的部署。
  \item \textbf{OpenID Connect}: Federated identity, enabling cross-organization agent communication.
  \item \textbf{OpenID Connect}：联合身份，支持跨组织智能体通信。
\end{itemize}

\begin{warningbox}[Authorization Scope Enforcement]
\begin{warningbox}[授权作用域执行]

An agent receiving a task must verify not only \emph{who} is calling (authentication) but \emph{what they are allowed to request} (authorization). A \texttt{ReportingAgent} might accept read-only data queries from any authenticated agent, but restrict write operations to agents holding a specific OAuth scope. Failing to enforce this creates privilege escalation vulnerabilities in multi-agent systems.
接收任务的智能体不仅需要验证调用者的 \emph{身份}（身份认证），还需要验证调用者 \emph{被允许请求什么}（授权）。一个 \texttt{ReportingAgent} 可能接受来自任何已认证智能体的只读数据查询，但将写操作限制为持有特定 OAuth 作用域的智能体。未能强制执行这一点会造成多智能体系统中的权限提升漏洞。
\end{warningbox}
\end{warningbox}

\section{Communication Patterns}
\section{通信模式}

Multi-agent systems employ a variety of communication patterns depending on the nature of the task, latency requirements, and the number of agents involved.
多智能体系统根据任务的性质、延迟要求和涉及的智能体数量，采用多种通信模式。

## Request-Response
## 请求-响应

The simplest pattern: Agent A sends a task to Agent B and waits for a complete response. Suitable for short, well-defined subtasks where the result is needed before proceeding.
最简单的模式：智能体 A 发送一个任务给智能体 B，并等待完整的响应。适用于简短、定义明确的子任务，这些任务需要在继续之前获取结果。

## Streaming
## 流式传输

Agent A opens an SSE connection; Agent B streams partial results as they are produced. Ideal for long-form generation (reports, code), real-time collaboration, or progressive UI updates.
智能体 A 打开一个 SSE 连接；智能体 B 在生成部分结果时将其流式传输。适用于长文本生成（报告、代码）、实时协作或渐进式 UI 更新。

\begin{examplebox}[Streaming Pattern Use Case]
\begin{examplebox}[流式传输模式使用案例]

An orchestrator asks a \texttt{WritingAgent} to draft a 10-page technical document. Rather than waiting 2 minutes for the complete document, the orchestrator streams each section as it is written, allowing a \texttt{ReviewAgent} to begin reviewing early sections while later sections are still being generated---a pipeline that reduces total latency by 40--60\%.
一个协调器（orchestrator）要求一个 \texttt{WritingAgent} 起草一份 10 页的技术文档。协调器不等待 2 分钟获取完整文档，而是在每个章节被写好后立即流式传输，从而允许一个 \texttt{ReviewAgent} 在后面的章节仍在生成时就开始审阅前面的章节——这种流水线可将总延迟减少 40\% 到 60\%。
\end{examplebox}
\end{examplebox}

## Multi-Turn Interaction
## 多轮交互

Some tasks require iterative refinement. The agent enters \texttt{input-required} state, the orchestrator provides clarification, and the task resumes. This mirrors human collaborative workflows: draft $\to$ feedback $\to$ revision.
某些任务需要迭代改进。智能体进入 \texttt{input-required} 状态，协调器提供澄清，然后任务继续。这反映了人类协作工作流：草稿 $\to$ 反馈 $\to$ 修订。

\begin{lstlisting}[style=pythonstyle]
