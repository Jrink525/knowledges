        # Return an AIMessage signaling the error so the LLM can adapt
        error_msg = AIMessage(content=f"Tool execution failed: {e}. Try a different approach.")
        return {
            "messages": [error_msg],
            "error_count": state["error_count"] + 1,
        }


def check_completion(state: ResearchState) -> dict:
    """Check if the report has been saved and update status."""
    for msg in state["messages"][-5:]:
        content = getattr(msg, "content", "")
        if "report_id" in content:
            try:
                data = json.loads(content)
                return {"status": "done", "report_id": data["report_id"]}
            except (json.JSONDecodeError, KeyError):
                pass
    return {}


def route_after_llm(state: ResearchState) -> str:
    """Determine next step after LLM response."""
    if state["error_count"] >= 5 or state["tool_call_count"] >= 15:
        return "fail"
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    if len(state["messages"]) > 30:
        return "fail"
    return "research"  # LLM needs to continue reasoning


def fail_node(state: ResearchState) -> dict:
    return {"status": "failed"}
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={完整生产级研究代理：状态与节点}]
