# Configure tracing
provider = TracerProvider()
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://collector:4317"))
)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("agent.tracer")


class InstrumentedAgent:
    def run(self, task: str) -> AgentResult:
        with tracer.start_as_current_span("agent.run") as span:
            span.set_attribute("agent.task", task)
            span.set_attribute("agent.model", self.model)

            result = self._execute(task)

            span.set_attribute("agent.status", result.status)
            span.set_attribute("agent.tool_calls", result.tool_call_count)
            span.set_attribute("agent.tokens_used", result.tokens_used)
            span.set_attribute("agent.cost_usd", result.cost_usd)
            return result

    def _call_llm(self, messages: list) -> str:
        with tracer.start_as_current_span("llm.call") as span:
            span.set_attribute("llm.model", self.model)
            span.set_attribute("llm.prompt_tokens", count_tokens(messages))
            response = self.llm.invoke(messages)
            span.set_attribute("llm.completion_tokens", count_tokens([response]))
            return response

    def _call_tool(self, tool_name: str, args: dict) -> str:
        with tracer.start_as_current_span(f"tool.{tool_name}") as span:
            span.set_attribute("tool.name", tool_name)
            span.set_attribute("tool.args", json.dumps(args))
            try:
                result = self.tools[tool_name](**args)
                span.set_attribute("tool.success", True)
                return result
            except Exception as e:
                span.set_attribute("tool.success", False)
                span.set_attribute("tool.error", str(e))
                span.record_exception(e)
                raise
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={使用OpenTelemetry进行结构化的智能体追踪}]
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


