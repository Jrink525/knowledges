    # Recursive case: split and sub-query
    chunks = split_by_structure(context, max_tokens // 2)
    sub_results = []
    for i, chunk in enumerate(chunks):
        sub_q = f"Summarize this section relevant to: {query}"
        sub_results.append(
            recursive_summarize(chunk, sub_q, model, max_tokens)
        )

