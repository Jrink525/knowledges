# Sub-tasks use child contexts for tracing
sub_ctx = ctx.child_context()
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle]
import uuid


class WorkflowContext:
    """在多智能体工作流中携带关联元数据。"""

    def __init__(self, workflow_id: str | None = None):
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.span_id = str(uuid.uuid4())
        self.parent_span_id: str | None = None

    def child_context(self) -> "WorkflowContext":
        """为子任务创建子上下文。"""
        child = WorkflowContext(workflow_id=self.workflow_id)
        child.parent_span_id = self.span_id
        return child

    def to_metadata(self) -> dict:
        return {
            "x-workflow-id": self.workflow_id,
            "x-span-id": self.span_id,
            "x-parent-span-id": self.parent_span_id
        }


