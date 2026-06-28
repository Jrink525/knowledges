# 通过运行 ID 加载失败的执行轨迹
child_runs = list(ls.list_runs(
    project_name="research-agent",
    filter=f'eq(parent_run_id, "{root_run.id}")',
    order="asc",
))

print(f"Trace: {root_run.id} | Status: {root_run.status}")
print(f"Trace: {root_run.id} | 状态: {root_run.status}")
print(f"Error: {root_run.error}" if root_run.error else "")
print(f"Total tokens: {root_run.total_tokens}\n")
print(f"总 Token 数: {root_run.total_tokens}\n")

