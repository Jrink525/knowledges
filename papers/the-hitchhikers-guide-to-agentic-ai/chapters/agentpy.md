# === agent.py ===
import json
from typing import TypedDict, Annotated, List, Literal
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from tools import TOOLS


SYSTEM_PROMPT = """你是一名专业研究分析师。你的任务是：
1. 搜索给定主题的相关信息
2. 阅读并分析关键来源（目标 3-5 个来源）
3. 将发现综合成结构化报告，并使用 save_report 保存

指南：
- 始终跨多个来源验证信息
- 在报告中引用你的来源
- 如果工具失败，尝试替代方法
- 最多在 15 次工具调用内完成任务
- 在获得足够信息后，仅调用一次 save_report"""


class ResearchState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    topic: str
    sources_found: List[str]
    sources_read: List[str]
    report_id: str | None
    error_count: int
    tool_call_count: int
    status: Literal["researching", "done", "failed"]


tool_executor = ToolNode(TOOLS)


def research_node(state: ResearchState) -> dict:
    """主 LLM 推理节点。"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(TOOLS)
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


def tool_node_with_error_handling(state: ResearchState) -> dict:
    """执行工具调用，包含错误处理和状态更新。"""
    try:
        result = tool_executor.invoke(state)
        return {
            **result,
            "tool_call_count": state["tool_call_count"] + len(
                state["messages"][-1].tool_calls
            ),
        }
    except Exception as e:
