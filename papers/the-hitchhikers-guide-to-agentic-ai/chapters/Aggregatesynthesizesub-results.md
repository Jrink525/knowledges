    # Aggregate: synthesize sub-results
    combined = "\n---\n".join(sub_results)
    return model.call(
        f"Given these partial summaries, answer: {query}"
        f"\n\nSummaries:\n{combined}"
    )
\end{lstlisting}
\begin{lstlisting}[style=pythonstyle]
def recursive_summarize(context: str, query: str,
                         model: LLM, max_tokens: int = 8000):
    """对超出窗口的上下文进行递归摘要。"""
    if count_tokens(context) <= max_tokens:
