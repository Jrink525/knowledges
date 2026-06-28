        # Store result
        state_store.hset(f"task:{task_id}", mapping={
            "status": "completed",
            "result": result.to_json(),
            "completed_at": time.time(),
            "cost_usd": result.cost_usd,
        })
