        # Phase 1: Announce task to all candidates
        announcement = {
            "type": "task-announcement",
            "task": dataclasses.asdict(task),
            "deadline": (datetime.now(timezone.utc) + timedelta(seconds=10)).isoformat(),
            "evaluationCriteria": ["confidence", "estimatedTime", "cost"]
        }

