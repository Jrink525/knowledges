    # Final response
    yield sse("token", {"content": "I've completed the research. "})
    yield sse("token", {"content": "Here's a summary of what I found..."})
    yield sse("done", {"total_tokens": 847, "duration_ms": 2341})


@app.get("/chat/stream")
async def chat_stream(session_id: str, message: str):
    return StreamingResponse(
        agent_stream(session_id, message),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


class ApprovalRequest(BaseModel):
    approval_id: str
    approved: bool
    parameters: dict | None = None
    reason: str | None = None


@app.post("/chat/approve")
async def handle_approval(req: ApprovalRequest):
    if req.approval_id not in approval_store:
        raise HTTPException(status_code=404, detail="Approval not found")
    approval_results[req.approval_id] = {
        "approved": req.approved,
        "parameters": req.parameters,
        "reason": req.reason,
    }
    approval_store[req.approval_id].set()
    return {"status": "ok"}
```

```python
@tool
def read_file(path: str) -> str:
    """从文件系统读取文件。"""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {path}"

