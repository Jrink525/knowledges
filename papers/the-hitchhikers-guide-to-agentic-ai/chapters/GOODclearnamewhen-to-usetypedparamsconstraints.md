# GOOD: clear name, when-to-use, typed params, constraints
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

\begin{examplebox}[好工具签名 vs. 坏工具签名]
\begin{lstlisting}[style=pythonstyle]
