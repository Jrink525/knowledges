    # Wait for human approval (timeout after 5 minutes)
    try:
        await asyncio.wait_for(approval_event.wait(), timeout=300)
        result = approval_results.get(approval_id, {})

        if result.get("approved"):
            yield sse("tool_call", {
                "tool": "send_email",
                "input": result.get("parameters", {}),
                "tier": 3,
                "approved_by": "human",
            })
            await asyncio.sleep(0.3)
            yield sse("tool_result", {
                "tool": "send_email",
                "output": "Email sent successfully",
                "duration_ms": 128,
            })
        else:
            yield sse("action_rejected", {
                "tool": "send_email",
                "reason": result.get("reason", "User rejected"),
            })
    except asyncio.TimeoutError:
        yield sse("approval_timeout", {
            "approval_id": approval_id,
            "message": "Approval timed out; action skipped",
        })

