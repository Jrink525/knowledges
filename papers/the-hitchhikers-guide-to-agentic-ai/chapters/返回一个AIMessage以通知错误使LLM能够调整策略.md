        # 返回一个 AIMessage 以通知错误，使 LLM 能够调整策略
        error_msg = AIMessage(content=f"工具执行失败: {e}。请尝试不同的方法。")
        return {
            "messages": [error_msg],
            "error_count": state["error_count"] + 1,
        }


def check_completion(state: ResearchState) -> dict:
    """检查报告是否已保存，并更新状态。"""
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
    """根据 LLM 响应决定下一步。"""
    if state["error_count"] >= 5 or state["tool_call_count"] >= 15:
        return "fail"
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    if len(state["messages"]) > 30:
        return "fail"
    return "research"  # LLM 需要继续推理


def fail_node(state: ResearchState) -> dict:
    return {"status": "failed"}
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={Complete production research agent: graph and deployment}]
