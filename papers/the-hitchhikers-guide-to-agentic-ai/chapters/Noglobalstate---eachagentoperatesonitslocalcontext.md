# No global state --- each agent operates on its local context
response = client.run(
    agent=triage_agent,
    messages=[{"role": "user", "content": "My invoice is wrong"}]
)
\end{lstlisting}
\end{examplebox}
\begin{examplebox}[OpenAI Swarm：例程与移交]
\begin{lstlisting}[style=pythonstyle]
from swarm import Swarm, Agent


client = Swarm()


def transfer_to_billing():
    """移交：将控制权转移给账单专员。"""
    return billing_agent


def transfer_to_technical():
    """移交：将控制权转移给技术支持代理。"""
    return technical_agent


triage_agent = Agent(
    name="分诊代理",
    instructions="""你是一个客户服务分诊代理。
    确定客户问题的性质：
    - 账单问题，转至账单代理。
    - 技术问题，转至技术支持代理。
    - 一般问题，直接回答。""",
    functions=[transfer_to_billing, transfer_to_technical],
)


billing_agent = Agent(
    name="账单专员",
    instructions="你处理账单查询。"
                 "访问账户数据并解决支付问题。",
    functions=[lookup_account, process_refund],
)


technical_agent = Agent(
    name="技术支持",
    instructions="你解决技术问题。"
                 "诊断问题并提供逐步解决方案。",
    functions=[run_diagnostics, escalate_to_engineering],
)


