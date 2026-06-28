# 在 https://agent.example.com/.well-known/agent.json 提供的智能体卡片
agent_card = {
    "name": "DataAnalysisAgent",
    "description": "Analyzes structured datasets, produces statistical summaries, "
                   "generates visualizations, and answers data questions.",
    "description": "分析结构化数据集，生成统计摘要，创建可视化，并回答数据相关问题。",
    "url": "https://agent.example.com/a2a",
    "version": "1.2.0",
    "capabilities": {
        "streaming": True,
        "pushNotifications": True,
        "stateTransitionHistory": True
    },
    "authentication": {
        "schemes": ["Bearer", "ApiKey"]
    },
    "skills": [
        {
            "id": "statistical-analysis",
            "name": "Statistical Analysis",
            "name": "统计分析",
            "description": "Compute descriptive statistics, run hypothesis tests, "
                           "fit regression models on tabular data.",
            "description": "计算描述性统计，运行假设检验，在表格数据上拟合回归模型。",
            "tags": ["statistics", "data", "analysis", "regression"],
            "examples": [
                "What is the correlation between columns A and B?",
                "Run a t-test comparing these two groups.",
                "Fit a linear regression predicting sales from ad spend."
            ],
            "inputModes": ["text", "data"],
            "outputModes": ["text", "data", "file"]
        },
        {
            "id": "visualization",
            "name": "Data Visualization",
            "name": "数据可视化",
            "description": "Generate charts, plots, and dashboards from data.",
            "description": "根据数据生成图表、图形和仪表盘。",
            "tags": ["charts", "plots", "visualization", "dashboard"],
            "examples": [
                "Create a bar chart of monthly revenue.",
                "Plot the distribution of customer ages."
            ],
            "inputModes": ["text", "data"],
            "outputModes": ["file", "text"]
        }
    ],
    "defaultInputModes": ["text"],
    "defaultOutputModes": ["text"]
}
\end{lstlisting}
\end{examplebox}


Agent Cards enable \emph{capability-based routing}: an orchestrator agent can fetch cards from a registry, semantically match a subtask to the most appropriate agent, and dispatch accordingly---all without hardcoded routing logic.
智能体卡片实现了\emph{基于能力的路由}：编排智能体可以从注册中心获取卡片，将子任务语义匹配到最合适的智能体，并相应地分派——全部无需硬编码的路由逻辑。
```

## Task Lifecycle
## 任务生命周期

A2A models all work as \textbf{Tasks}. A task progresses through a well-defined state machine:
A2A 将所有工作建模为 \textbf{任务（Tasks）}。一个任务会经过一个定义良好的状态机进行推进：

\texttt{submitted}
\texttt{submitted}

The client has sent the task; the server has acknowledged receipt.
客户端已发送任务；服务器已确认收到。

\texttt{working}
\texttt{working}

The agent is actively processing. The client may poll or await SSE events.
智能体正在积极处理中。客户端可以轮询或等待 SSE 事件。

\texttt{input-required}
\texttt{input-required}

The agent needs additional information from the user or calling agent before it can proceed (e.g., a clarifying question, a missing credential).
智能体需要从用户或调用智能体处获取额外信息后才能继续（例如，一个澄清问题、一个缺失的凭证）。

\texttt{completed}
\texttt{completed}

The task finished successfully; results are available in the response.
任务成功完成；结果可在响应中获取。

\texttt{failed}
\texttt{failed}

An unrecoverable error occurred; an error message explains the cause.
发生了不可恢复的错误；错误消息解释了原因。

\texttt{rejected}
\texttt{rejected}

The agent declined the task (e.g., outside its capabilities or unauthorized). Added in A2A v1.0.
智能体拒绝了任务（例如，超出其能力范围或未经授权）。在 A2A v1.0 中新增。

\texttt{canceled}
\texttt{canceled}

The task was aborted, either by the client or by the server.
任务被中止，由客户端或服务器发起。

## Streaming via Server-Sent Events
## 通过服务器发送事件（Server-Sent Events）进行流式传输

For tasks that produce incremental output (e.g., a long report being written, a code file being generated), A2A uses \textbf{Server-Sent Events (SSE)}. The client opens a persistent HTTP connection and receives a stream of JSON events:
对于产生增量输出的任务（例如，正在撰写的长报告、正在生成的代码文件），A2A 使用 \textbf{服务器发送事件（Server-Sent Events, SSE）}。客户端打开一个持久的 HTTP 连接，并接收一串 JSON 事件流：

\begin{examplebox}[SSE Event Stream Example]
\begin{examplebox}[SSE 事件流示例]

\begin{lstlisting}[style=pythonstyle]
