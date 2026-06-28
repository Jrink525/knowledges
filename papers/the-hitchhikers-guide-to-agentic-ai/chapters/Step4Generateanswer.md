    # Step 4: Generate answer
    return generate_answer(query, fused_docs[:5], llm)
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={使用 RRF 的 RAG-Fusion}]
def reciprocal_rank_fusion(ranked_lists: list[list[str]], k: int = 60) -> list[str]:
    """使用 RRF 融合多个排序文档列表。"""
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, doc_id in enumerate(ranked, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)


def rag_fusion(query: str, retriever, llm, n_queries: int = 4) -> str:
