        # Update task status
        state_store.hset(f"task:{task_id}", mapping={
            "status": "running",
            "started_at": time.time(),
            "worker": self.request.hostname,
        })
