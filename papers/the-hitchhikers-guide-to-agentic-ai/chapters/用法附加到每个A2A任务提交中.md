# 用法：附加到每个 A2A 任务提交中
ctx = WorkflowContext()
task = await client.send_task(
    message=message,
    metadata=ctx.to_metadata()
)
