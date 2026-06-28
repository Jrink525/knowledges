# HorizontalPodAutoscaler scales on queue depth metric
hpa_config = {
    "apiVersion": "autoscaling/v2",
    "kind": "HorizontalPodAutoscaler",
    "metadata": {"name": "research-agent-hpa", "namespace": "agents"},
    "spec": {
        "scaleTargetRef": {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "name": "research-agent",
        },
        "minReplicas": 2,
        "maxReplicas": 20,
        "metrics": [{
            "type": "External",
            "external": {
                "metric": {"name": "agent_task_queue_depth"},
                "target": {"type": "AverageValue", "averageValue": "10"},
            }
        }]
    }
}
```

```python
