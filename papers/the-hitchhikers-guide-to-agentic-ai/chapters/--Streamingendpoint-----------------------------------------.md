# -- Streaming endpoint --------------------------------------------------------


async def agent_stream(
    session_id: str,
    user_message: str,
) -> AsyncGenerator[str, None]:
    """Stream agent events as SSE."""

    def sse(event_type: str, data: dict) -> str:
        return f"data: {json.dumps({'type': event_type, **data})}\n\n"

    yield sse("status", {"message": "Agent starting..."})

