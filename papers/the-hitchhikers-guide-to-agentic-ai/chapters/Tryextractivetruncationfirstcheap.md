    # Try extractive truncation first (cheap)
    truncated = smart_truncate(result, budget)
    if summarizer and tokens > 2 * budget:
