# === kubernetes/deployment.yaml (as Python dict for illustration) ===
k8s_deployment = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {"name": "research-agent", "namespace": "agents"},
    "spec": {
        "replicas": 3,
        "selector": {"matchLabels": {"app": "research-agent"}},
        "template": {
            "metadata": {"labels": {"app": "research-agent"}},
            "spec": {
                "containers": [{
                    "name": "agent",
                    "image": "myregistry/research-agent:latest",
                    "ports": [{"containerPort": 8000}],
                    "resources": {
                        "requests": {"memory": "512Mi", "cpu": "250m"},
                        "limits":   {"memory": "2Gi",  "cpu": "1000m"},
                    },
                    "env": [
                        {"name": "DATABASE_URL",   "valueFrom": {
                            "secretKeyRef": {"name": "agent-secrets", "key": "db-url"}}},
                        {"name": "OPENAI_API_KEY", "valueFrom": {
                            "secretKeyRef": {"name": "agent-secrets", "key": "openai-key"}}},
                    ],
                    "livenessProbe":  {"httpGet": {"path": "/health", "port": 8000},
                                       "initialDelaySeconds": 30, "periodSeconds": 10},
                    "readinessProbe": {"httpGet": {"path": "/ready",  "port": 8000},
                                       "initialDelaySeconds": 10, "periodSeconds": 5},
                }]
            }
        }
    }
}


