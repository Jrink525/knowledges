# 工具定义（在 API 请求中传递）
{"tools": [{
    "name": "search_web",
    "description": "Search the web for current information.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string",
                      "description": "Search query"},
            "num_results": {"type": "integer",
                            "description": "Max results"}
        },
        "required": ["query"]
    }
}]}


