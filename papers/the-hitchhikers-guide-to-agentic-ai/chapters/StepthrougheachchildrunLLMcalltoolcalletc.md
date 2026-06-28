# Step through each child run (LLM call, tool call, etc.)
for i, run in enumerate(child_runs):
    print(f"Step {i}: [{run.run_type}] {run.name}")
