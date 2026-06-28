# GOOD: 名称清晰，包含使用时机，带类型的参数，约束
{"name": "search_web",
 "description": "Search the public web for current information. "
   "Use when the user asks about events after 2024-04. "
   "Do NOT use for internal company data.",
 "parameters": {
   "query": {"type": "string",
             "description": "Natural-language search query"},
   "num_results": {"type": "integer", "default": 5,
                   "description": "Results to return (max 20)"}},
 "returns": "JSON array of {title, url, snippet}",
 "constraints": "Max 10 calls/minute. No PII in queries."}
\end{lstlisting}
\end{examplebox}


Additional best practices for tool descriptions in the prompt:

提示中工具描述的其他最佳实践：

\begin{itemize}
  \item \textbf{Be specific:} ``Search the web for current information'' is better than ``Search''.
  \item \textbf{具体化：} “Search the web for current information（在网络上搜索当前信息）” 优于 “Search（搜索）”。
  \item \textbf{Include when to use:} ``Use this when the user asks about events after your knowledge cutoff.''
  \item \textbf{包含使用时机：} “Use this when the user asks about events after your knowledge cutoff（当用户询问你知识截止日期之后的事件时使用此工具）。”
  \item \textbf{Include when NOT to use:} Reduces false positives.
  \item \textbf{包含何时不使用：} 减少误报。
  \item \textbf{Exclude irrelevant tools:} Dynamically include only tools relevant to the current task to save tokens and reduce confusion.
  \item \textbf{排除不相关的工具：} 仅动态包含与当前任务相关的工具，以节省 token 并减少混淆。
  \item \textbf{Optimize descriptions:} A/B test descriptions; small wording changes can shift tool selection accuracy by 10--20\%.
  \item \textbf{优化描述：} 对描述进行 A/B 测试；措辞的细微变化可使工具选择准确率变动 10--20\%。
\end{itemize}


\section{Tool Integration and Execution}
\label{tool-integration-and-execution}

\section{工具集成与执行}
\label{tool-integration-and-execution}

Tool use is a defining capability of modern LLM agents~\cite{schick2023toolformer}. The harness manages tool definitions, selection, execution, and output processing.

工具使用是现代 LLM 智能体（agent）的一项定义性能力~\cite{schick2023toolformer}。框架（harness）负责管理工具定义、选择、执行和输出处理。

\subsection{Tool Definition Schemas}
\label{tool-definition-schemas}

\subsection{工具定义模式}
\label{tool-definition-schemas}

Different providers use different schemas for tool definitions:

不同的提供商使用不同的模式来定义工具：

\paragraph{OpenAI Function Calling.}
\label{openai-function-calling.}

\paragraph{OpenAI 函数调用（OpenAI Function Calling）。}
\label{openai-function-calling.}

\begin{examplebox}[OpenAI Tool Definition]
\begin{lstlisting}[style=pythonstyle]
{
  "type": "function",
  "function": {
    "name": "search_web",
    "description": "Search the web for current information.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {"type": "string", "description": "Search query"},
        "num_results": {"type": "integer", "default": 5}
      },
      "required": ["query"]
    }
  }
}
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[OpenAI 工具定义]
\begin{lstlisting}[style=pythonstyle]
{
  "type": "function",
  "function": {
    "name": "search_web",
    "description": "Search the web for current information.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {"type": "string", "description": "Search query"},
        "num_results": {"type": "integer", "default": 5}
      },
      "required": ["query"]
    }
  }
}
\end{lstlisting}
\end{examplebox}

\paragraph{Anthropic Tool Use.}
\label{anthropic-tool-use.}

\paragraph{Anthropic 工具使用（Anthropic Tool Use）。}
\label{anthropic-tool-use.}

Anthropic uses a similar JSON schema but with an \texttt{input\_schema} key instead of \texttt{parameters}, and tools are passed in a top-level \texttt{tools} array:

Anthropic 使用类似的 JSON 模式，但使用 \texttt{input\_schema} 键替代 \texttt{parameters}，且工具通过顶级 \texttt{tools} 数组传递：

\begin{examplebox}[Anthropic Tool Definition]
\begin{lstlisting}[style=pythonstyle]
