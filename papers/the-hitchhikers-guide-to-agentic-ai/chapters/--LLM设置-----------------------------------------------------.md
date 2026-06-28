# -- LLM设置-----------------------------------------------------------------


llm = ChatOpenAI(model="gpt-4o", streaming=True)
tools = [web_search, send_email, read_file]
llm_with_tools = llm.bind_tools(tools)


def should_request_approval(tool_name: str) -> bool:
    return tool_name in APPROVAL_REQUIRED_TOOLS


