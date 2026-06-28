    # 使用回调处理器时，Chainlit 自动将每个步骤渲染为可折叠的 UI 元素
    async with cl.Step(name="Agent", type="run") as step:
        step.input = message.content
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": message.content}]},
            config={"callbacks": [cl.LangchainCallbackHandler()]}
        )
        output = result["messages"][-1].content
        step.output = output

    await cl.Message(content=output).send()
\end{lstlisting}

\subsection{Gradio}
\label{gradio}
\subsection{Gradio}
\label{gradio}

Gradio~\cite{abid2019gradio} is a Python library for rapidly building ML demos and agent interfaces. Its \texttt{gr.ChatInterface} and \texttt{gr.Blocks} API enable quick prototyping of conversational agents with minimal code.

Gradio~\cite{abid2019gradio} 是一个 Python 库，用于快速构建机器学习演示和智能体界面。其 \texttt{gr.ChatInterface} 和 \texttt{gr.Blocks} API 可以用最少的代码快速原型化对话式智能体。

\textbf{Strengths for agentic UIs:}

\textbf{在智能体 UI 方面的优势：}

\begin{itemize}
  \item \textbf{Zero-configuration deployment}: One-line sharing via Hugging Face Spaces.
  \item \textbf{Custom components}: The Gradio Custom Components system allows building React components that integrate seamlessly with Python backends.
  \item \textbf{Multi-modal inputs}: File upload, image, audio, video, and webcam inputs with minimal configuration.
  \item \textbf{Streaming}: Native support for generator-based streaming responses.
\end{itemize}

\begin{itemize}
  \item \textbf{零配置部署}：通过 Hugging Face Spaces 一键共享。
  \item \textbf{自定义组件}：Gradio 自定义组件系统允许构建与 Python 后端无缝集成的 React 组件。
  \item \textbf{多模态输入}：文件上传、图像、音频、视频和摄像头输入，配置极少。
  \item \textbf{流式传输}：原生支持基于生成器的流式响应。
\end{itemize}

\textbf{Limitations:} Gradio’s layout system is less flexible than full React frameworks, and its state management is session-scoped, making complex multi-agent coordination challenging.

\textbf{局限性：} Gradio 的布局系统不如完整的 React 框架灵活，且其状态管理局限于会话范围，使得复杂的多智能体协调变得具有挑战性。

\subsection{Streamlit}
\label{streamlit}
\subsection{Streamlit}
\label{streamlit}

Streamlit~\cite{streamlit2024} is a Python framework for data applications that has been widely adopted for agent dashboards and monitoring UIs. Its reactive execution model---the entire script reruns on each interaction---is simple but can be limiting for complex agentic workflows.

Streamlit~\cite{streamlit2024} 是一个用于数据应用的 Python 框架，已广泛用于智能体仪表盘和监控 UI。它的响应式执行模型（每次交互整个脚本重新运行）虽然简单，但对于复杂的智能体工作流可能有限制。

\textbf{Agentic use cases:}

\textbf{智能体用例：}
```

\begin{itemize}
  \item \textbf{Agent dashboards}: Real-time metrics, task queues, and status displays using \texttt{st.metric}, \texttt{st.dataframe}, and \texttt{st.status}.
  \item \textbf{代理仪表盘 (Agent dashboards)}：使用 \texttt{st.metric}、\texttt{st.dataframe} 和 \texttt{st.status} 实现实时指标、任务队列和状态显示。
  \item \textbf{Session state}: \texttt{st.session\_state} persists agent state across reruns, enabling multi-turn conversations.
  \item \textbf{会话状态 (Session state)}：\texttt{st.session\_state} 在多次重运行之间持久化代理状态，支持多轮对话。
  \item \textbf{Streaming}: \texttt{st.write\_stream} renders generator outputs progressively.
  \item \textbf{流式输出 (Streaming)}：\texttt{st.write\_stream} 逐步渲染生成器的输出。
  \item \textbf{Fragments}: \texttt{@st.fragment} decorator enables partial reruns, improving performance for live-updating dashboards.
  \item \textbf{片段 (Fragments)}：\texttt{@st.fragment} 装饰器支持部分重运行，提升实时更新仪表盘的性能。
\end{itemize}

\subsection{OpenAI Assistants Playground}
\label{openai-assistants-playground}
\subsection{OpenAI Assistants Playground}
\label{openai-assistants-playground}

The OpenAI Assistants Playground serves as a reference implementation for agentic UI design. It demonstrates:
OpenAI Assistants Playground 作为代理 UI 设计的参考实现，展示了以下功能：

\begin{itemize}
  \item Thread-based conversation management with persistent history.
  \item 基于线程的对话管理，支持持久化历史记录。
  \item File attachment and retrieval visualization.
  \item 文件附件与检索的可视化。
  \item Code interpreter execution with output display (stdout, images, files).
  \item 代码解释器执行与输出显示（标准输出、图像、文件）。
  \item Function call display with input/output inspection.
  \item 函数调用显示，支持输入/输出检查。
  \item Run step visualization showing the sequence of model calls and tool invocations.
  \item 运行步骤可视化，展示模型调用和工具调用的序列。
\end{itemize}

While not a framework for building custom UIs, the Playground’s design patterns are widely emulated.
虽然它并非用于构建自定义 UI 的框架，但 Playground 的设计模式被广泛借鉴。

\subsection{LangGraph Studio}
\label{langgraph-studio}
\subsection{LangGraph Studio}
\label{langgraph-studio}

LangGraph Studio~\cite{langgraph2024studio} is a desktop application providing a visual IDE for LangGraph agents. It is the most sophisticated tool-use and workflow visualization environment currently available.
LangGraph Studio~\cite{langgraph2024studio} 是一款桌面应用程序，为 LangGraph 代理提供可视化 IDE。它是目前最完善的工具使用和工作流可视化环境。

\textbf{Features:}
\textbf{特性：}

\begin{itemize}
  \item \textbf{Graph visualization}: Interactive rendering of the agent’s state machine, with nodes representing agent steps and edges representing transitions.
  \item \textbf{图可视化 (Graph visualization)}：交互式渲染代理状态机，节点表示代理步骤，边表示转换。
  \item \textbf{State inspection}: At any point in execution, the full agent state (all variables, memory, tool results) can be inspected as structured JSON.
  \item \textbf{状态检查 (State inspection)}：在执行过程中的任意时刻，可查看完整的代理状态（所有变量、记忆、工具结果）作为结构化 JSON。
  \item \textbf{Time-travel debugging}: Replay any prior execution step, modify the state, and re-run from that point.
  \item \textbf{时间旅行调试 (Time-travel debugging)}：重放任意先前的执行步骤，修改状态，然后从该点重新运行。
  \item \textbf{Human-in-the-loop integration}: Breakpoints can be set on any node; execution pauses and waits for human input before proceeding.
  \item \textbf{人在回路集成 (Human-in-the-loop integration)}：可在任意节点设置断点；执行暂停并等待人工输入后再继续。
  \item \textbf{Multi-agent support}: Visualizes supervisor-subagent hierarchies and inter-agent message passing.
  \item \textbf{多代理支持 (Multi-agent support)}：可视化主管-子代理层级以及代理间消息传递。
\end{itemize}

\subsection{Framework Comparison}
\label{framework-comparison}
\subsection{框架比较}
\label{framework-comparison}

Table~\ref{tab:ui-framework-comparison} summarizes the key characteristics of the frameworks discussed above.
表~\ref{tab:ui-framework-comparison} 总结了上述框架的关键特征。

\begin{table}[ht!]
\centering
\caption{Agentic UI framework comparison.}
\caption{代理 UI 框架比较。}
\label{tab:ui-framework-comparison}
{\footnotesize
\begin{tabular}{@{}llccccc@{}}
\toprule
\textbf{Framework} & \textbf{Language} & \textbf{Stream} & \textbf{Tool Viz} & \textbf{Multi-Ag.} & \textbf{Gen UI} & \textbf{Prod} \\
\textbf{框架} & \textbf{语言} & \textbf{流式} & \textbf{工具可视化} & \textbf{多代理} & \textbf{生成式 UI} & \textbf{生产可用} \\
\midrule
Vercel AI SDK & TypeScript & \checkmark{} & Partial & Partial & \checkmark{} & \checkmark{} \\
Vercel AI SDK & TypeScript & \checkmark{} & 部分 & 部分 & \checkmark{} & \checkmark{} \\
Chainlit & Python & \checkmark{} & \checkmark{} & Partial & Partial & \checkmark{} \\
Chainlit & Python & \checkmark{} & \checkmark{} & 部分 & 部分 & \checkmark{} \\
Gradio & Python & \checkmark{} & $\circ$ & $\times$ & $\circ$ & \checkmark{} \\
Gradio & Python & \checkmark{} & $\circ$ & $\times$ & $\circ$ & \checkmark{} \\
Streamlit & Python & \checkmark{} & $\circ$ & $\times$ & $\times$ & \checkmark{} \\
Streamlit & Python & \checkmark{} & $\circ$ & $\times$ & $\times$ & \checkmark{} \\
OAI Playground & N/A (hosted) & \checkmark{} & \checkmark{} & $\times$ & $\times$ & $\times$ \\
OAI Playground & N/A (托管) & \checkmark{} & \checkmark{} & $\times$ & $\times$ & $\times$ \\
LangGraph Studio & Python/TS & \checkmark{} & \checkmark{} & \checkmark{} & $\times$ & Partial \\
LangGraph Studio & Python/TS & \checkmark{} & \checkmark{} & \checkmark{} & $\times$ & 部分 \\
\bottomrule
\end{tabular}
}
\end{table}

\section{Generative UI}
\label{subsec:generative-ui}
\section{生成式 UI (Generative UI)}
\label{subsec:generative-ui}

\begin{intuitionbox}[The Generative UI Concept]
Traditional LLM interfaces render model outputs as text or markdown. \emph{Generative UI} inverts this: the model’s tool calls \emph{generate} UI components. The model decides not just \emph{what} to say, but \emph{how} to present it---as a chart, a form, a map, a calendar widget---based on the content type and user intent.
\end{intuitionbox}
\begin{intuitionbox}[生成式 UI 概念]
传统 LLM 接口将模型输出渲染为文本或 Markdown。\emph{生成式 UI (Generative UI)} 则颠覆了这一模式：模型的工具调用\emph{生成} UI 组件。模型不仅决定\emph{说什么}，还根据内容类型和用户意图决定\emph{如何呈现}——以图表、表单、地图、日历控件等形式。
\end{intuitionbox}

Generative UI represents a fundamental shift in the relationship between LLMs and interfaces. Rather than the developer pre-specifying all possible UI states, the model dynamically selects and parameterizes UI components appropriate to the current context.
生成式 UI 代表了 LLM 与界面关系的根本转变。开发者不再需要预先指定所有可能的 UI 状态，而是由模型根据当前上下文动态选择并参数化合适的 UI 组件。

\subsection{React Server Components for Dynamic Interfaces}
\label{react-server-components-for-dynamic-interfaces}
\subsection{用于动态界面的 React 服务端组件}
\label{react-server-components-for-dynamic-interfaces}

The Vercel AI SDK’s RSC (React Server Components\footnote{React Server Components}) integration is the most mature implementation of generative UI. The architecture works as follows:
Vercel AI SDK 的 RSC（React 服务端组件 (React Server Components)）集成是生成式 UI 最成熟的实现。其架构工作流程如下：

\begin{enumerate}
  \item The user sends a message to a Next.js\footnote{Next.js} server action.
  \item 用户向 Next.js 服务端操作 (Server Action) 发送消息。
  \item The server calls the LLM with a set of tools, each associated with a React component.
  \item 服务端调用 LLM，并传入一组工具，每个工具都与一个 React 组件相关联。
  \item When the LLM calls a tool (e.g., \texttt{show\_weather}), the server renders the corresponding React component with the tool’s output as props.
  \item 当 LLM 调用某个工具（例如 \texttt{show\_weather}）时，服务端渲染对应的 React 组件，并将工具的输出作为 props 传入。
  \item The rendered component is streamed to the client as a React Server Component, appearing inline in the chat.
  \item 渲染后的组件作为 React 服务端组件流式传输到客户端，在聊天中内联显示。
\end{enumerate}

\begin{lstlisting}[style=pythonstyle, caption={Generative UI with Vercel AI SDK RSC (TypeScript)}]
\begin{lstlisting}[style=pythonstyle, caption={使用 Vercel AI SDK RSC 的生成式 UI (TypeScript)}]
// app/actions.tsx (Server Action)
import { streamUI } from 'ai/rsc';
import { openai } from '@ai-sdk/openai';
import { WeatherCard } from '@/components/WeatherCard';
import { StockChart } from '@/components/StockChart';

export async function chat(userMessage: string) {
  const result = await streamUI({
    model: openai('gpt-4o'),
    messages: [{ role: 'user', content: userMessage }],
    tools: {
      show_weather: {
        description: 'Display current weather for a location',
        parameters: z.object({
          location: z.string(),
          unit: z.enum(['celsius', 'fahrenheit']),
        }),
        // Tool result rendered as a React component
        generate: async ({ location, unit }) => {
          const data = await fetchWeather(location, unit);
          return <WeatherCard data={data} />;
        },
      },
      show_stock: {
        description: 'Display stock price chart',
        parameters: z.object({ ticker: z.string() }),
        generate: async ({ ticker }) => {
          const data = await fetchStockData(ticker);
          return <StockChart ticker={ticker} data={data} />;
        },
      },
    },
  });
  return result.value;
}
\end{lstlisting}
\end{lstlisting}

\subsection{Adaptive Interfaces Based on Content Type}
\label{adaptive-interfaces-based-on-content-type}
\subsection{基于内容类型的自适应界面}
\label{adaptive-interfaces-based-on-content-type}

Generative UI enables interfaces that adapt to the nature of the content being presented:
生成式 UI 使界面能够根据所呈现内容的性质进行自适应调整：

\begin{itemize}
  \item \textbf{Tabular data} $\rightarrow$ sortable, filterable data table with export options.
  \item \textbf{表格数据 (Tabular data)} $\rightarrow$ 可排序、可筛选的数据表，并支持导出选项。
  \item \textbf{Geographic data} $\rightarrow$ interactive map with markers and layers.
  \item \textbf{地理数据 (Geographic data)} $\rightarrow$ 带有标记和图层的交互式地图。
  \item \textbf{Time series} $\rightarrow$ zoomable line chart with annotations.
  \item \textbf{时间序列 (Time series)} $\rightarrow$ 可缩放且带注释的折线图。
  \item \textbf{Code} $\rightarrow$ syntax-highlighted editor with run button.
  \item \textbf{代码 (Code)} $\rightarrow$ 语法高亮编辑器，附带运行按钮。
  \item \textbf{Documents} $\rightarrow$ formatted document viewer with annotation tools.
  \item \textbf{文档 (Documents)} $\rightarrow$ 格式化文档查看器，带有注释工具。
  \item \textbf{Forms/structured input} $\rightarrow$ dynamically generated form fields.
  \item \textbf{表单/结构化输入 (Forms/structured input)} $\rightarrow$ 动态生成的表单字段。
\end{itemize}

The model acts as a \emph{UI orchestrator}, selecting the most appropriate presentation for each piece of information. This reduces the need for developers to anticipate every possible output type and pre-build corresponding components.
模型充当\emph{UI 编排器 (UI orchestrator)}，为每条信息选择最合适的展示方式。这减少了开发者需要预判所有可能的输出类型并预先构建对应组件的需求。

\begin{questionbox}[Limits of Generative UI]
How much UI generation should be delegated to the model? Fully model-driven UI risks inconsistency, accessibility failures, and security vulnerabilities (e.g., a model generating a form that submits data to an unexpected endpoint). In practice, generative UI works best when the model selects from a \emph{curated library} of pre-built, accessible, and secure components rather than generating arbitrary HTML or JSX.
\end{questionbox}
\begin{questionbox}[生成式 UI 的局限性]
应该将多少 UI 生成工作委托给模型？完全由模型驱动的 UI 存在不一致性、无障碍性失败以及安全漏洞的风险（例如，模型生成的表单将数据提交到意外的端点）。在实践中，当模型从预构建、无障碍且安全的\emph{精选组件库 (curated library)} 中进行选择，而非生成任意 HTML 或 JSX 时，生成式 UI 的效果最佳。
\end{questionbox}

\section{Streaming and Real-Time Patterns}
\label{subsec:streaming-patterns}
\section{流式与实时模式}
\label{subsec:streaming-patterns}

Streaming is foundational to agentic UIs: it transforms the experience from ``wait for a result'' to ``watch the agent work.'' This section covers the key streaming patterns and their implementation considerations.
流式传输是代理 UI 的基础：它将体验从“等待结果”转变为“观察代理工作”。本节涵盖关键的流式模式及其实现考虑因素。

\subsection{Token Streaming}
\label{token-streaming}
\subsection{令牌流式传输 (Token Streaming)}
\label{token-streaming}

## Motivation: Beyond the Chat Box
## 动机：超越聊天框

Token streaming delivers LLM output incrementally as tokens are generated, rather than waiting for the complete response. Two transport mechanisms are commonly used:
Token streaming（令牌流）在生成令牌时逐步传递 LLM 输出，而不是等待完整响应。常用两种传输机制：

\begin{itemize}
  \item \textbf{Server-Sent Events (SSE)}12: A unidirectional HTTP stream from server to client. Each event carries a chunk of tokens. SSE is simple, works over standard HTTP/1.1, and is automatically reconnected by browsers. It is the dominant mechanism for LLM streaming APIs (OpenAI, Anthropic, Google all use SSE).
  \item \textbf{Server-Sent Events（SSE）}：从服务器到客户端的单向 HTTP 流。每个事件携带一个令牌块。SSE 简单，基于标准 HTTP/1.1，浏览器自动重连，是 LLM 流式 API 的主流机制（OpenAI、Anthropic、Google 均使用 SSE）。
  \item \textbf{WebSockets}: Bidirectional persistent connections. More complex to implement but necessary for interactive streaming scenarios where the client needs to send data mid-stream (e.g., interrupting the agent, providing mid-generation feedback).
  \item \textbf{WebSockets}：双向持久连接。实现更复杂，但对于客户端需要在流中发送数据的交互式流场景（例如中断智能体、提供生成中反馈）是必要的。
\end{itemize}

\begin{lstlisting}[style=pythonstyle, caption={SSE token streaming with FastAPI}]
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
import json


app = FastAPI()
client = AsyncOpenAI()


async def token_stream(prompt: str):
    """Generator that yields SSE-formatted token chunks."""
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
