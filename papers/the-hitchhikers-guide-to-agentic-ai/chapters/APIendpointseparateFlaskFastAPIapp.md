# API endpoint (separate Flask/FastAPI app)
from flask import Flask, request, jsonify
import uuid

web_app = Flask(__name__)

@web_app.route("/tasks", methods=["POST"])
def submit_task():
    task_id = str(uuid.uuid4())
    task = run_agent_task.delay(
        task_id=task_id,
        task_input=request.json["input"],
        config=request.json.get("config", {}),
    )
    return jsonify({"task_id": task_id, "celery_id": task.id}), 202
\end{lstlisting}

\subsection{Multi-Tenant Isolation}
\label{multi-tenant-isolation}
\subsection{多租户隔离}
\label{multi-tenant-isolation}

Production agent systems serving multiple customers require strict isolation:
为多个客户服务的生产级智能体系统需要严格的隔离：

\begin{itemize}
  \item \textbf{Namespace isolation}: Each tenant’s state, memory, and tool configurations are stored in separate namespaces
  \item \textbf{命名空间隔离}：每个租户的状态、记忆和工具配置存储在独立的命名空间中
  \item \textbf{Rate limiting}: Per-tenant rate limits on LLM calls, tool invocations, and compute time
  \item \textbf{速率限制}：每个租户对 LLM 调用、工具调用和计算时间的速率限制
  \item \textbf{Resource quotas}: Maximum concurrent agents, token budgets, and storage limits per tenant
  \item \textbf{资源配额}：每个租户的最大并发智能体数、Token 预算和存储限制
  \item \textbf{Audit logging}: All agent actions are logged with tenant ID for compliance and billing
  \item \textbf{审计日志}：所有智能体操作均记录租户 ID，用于合规性和计费
\end{itemize}

\subsection{Cost Optimization Strategies}
\label{cost-optimization-strategies}
\subsection{成本优化策略}
\label{cost-optimization-strategies}

\begin{itemize}
  \item \textbf{Model routing}: Use smaller, cheaper models for simple subtasks (classification, extraction) and reserve large models for complex reasoning
  \item \textbf{模型路由}：为简单子任务（分类、提取）使用更小、更便宜的模型，保留大模型用于复杂推理
  \item \textbf{Prompt caching}: OpenAI and Anthropic offer prompt caching for repeated system prompts, reducing costs by up to 90\% for high-traffic agents
  \item \textbf{提示缓存}：OpenAI 和 Anthropic 为重复的系统提示提供提示缓存，可降低高流量智能体高达 90% 的成本
  \item \textbf{Result caching}: Cache tool results for identical inputs within a time window
  \item \textbf{结果缓存}：在时间窗口内缓存相同输入的工具结果
  \item \textbf{Batching}: Batch multiple independent LLM calls when latency permits
  \item \textbf{批处理}：在延迟允许的情况下批量处理多个独立的 LLM 调用
  \item \textbf{Early termination}: Detect when the agent has sufficient information to answer and terminate the loop early
  \item \textbf{早期终止}：检测智能体何时拥有足够信息回答，并提前终止循环
\end{itemize}

\begin{lstlisting}[style=pythonstyle, caption={Model routing for cost optimization}]
\begin{lstlisting}[style=pythonstyle, caption={用于成本优化的模型路由}]
class CostOptimizedRouter:
    TASK_MODEL_MAP = {
        "classification": "gpt-4o-mini",
        "extraction": "gpt-4o-mini",
        "summarization": "gpt-4o-mini",
        "reasoning": "gpt-4o",
        "code_generation": "gpt-4o",
        "complex_analysis": "o1",
    }

    def route(self, task_type: str, complexity: float) -> str:
        base_model = self.TASK_MODEL_MAP.get(task_type, "gpt-4o-mini")
