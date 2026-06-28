    # when using the callback handler
    async with cl.Step(name="Agent", type="run") as step:
        step.input = message.content
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": message.content}]},
            config={"callbacks": [cl.LangchainCallbackHandler()]}
        )
        output = result["messages"][-1].content
        step.output = output

    await cl.Message(content=output).send()
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={最小化 Chainlit 智能体，包含步骤可视化}]
import chainlit as cl
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

@tool
def search(query: str) -> str:
    """搜索信息。"""
    return f"Results for: {query}"

agent = create_react_agent(
    ChatOpenAI(model="gpt-4o"), tools=[search]
)

@cl.on_message
async def on_message(message: cl.Message):
