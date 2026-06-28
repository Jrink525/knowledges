# Tool definition (passed in the API request)
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


