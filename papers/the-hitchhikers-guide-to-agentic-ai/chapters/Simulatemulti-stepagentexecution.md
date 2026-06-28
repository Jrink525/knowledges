    # Simulate multi-step agent execution
    steps = [
        ("thinking", {"content": "Analyzing the request..."}),
        ("tool_call", {
            "tool": "web_search",
            "input": {"query": user_message},
            "tier": 1,  # Auto-approve
        }),
        ("tool_result", {
            "tool": "web_search",
            "output": f"Results for: {user_message}",
            "duration_ms": 342,
        }),
    ]

    for event_type, data in steps:
        await asyncio.sleep(0.5)  # Simulate processing time
        yield sse(event_type, data)

