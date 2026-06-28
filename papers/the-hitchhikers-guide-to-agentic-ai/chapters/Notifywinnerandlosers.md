        # Notify winner and losers
        await self._award_contract(winner_agent, task)
        await asyncio.gather(*[
            self._reject_bid(agent, task.id)
            for agent, _ in valid_bids if agent != winner_agent
        ])

        return winner_agent

    async def _request_bid(self, agent: AgentCard,
                           announcement: dict) -> dict | None:
        """Ask an agent to bid on a task."""
        try:
            result = await self.client.send_task(
                agent_url=agent.url,
                message={"role": "user",
                         "parts": [{"type": "data", "data": announcement}]}
            )
            return result.artifacts[0].parts[0]["data"]
        except Exception:
            return None
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[合同网协议实现]
\begin{lstlisting}[style=pythonstyle]
import dataclasses


class ContractNetManager:
    """实现用于任务分配的合同网协议。"""

    async def allocate_task(self, task: Task,
                            candidate_agents: list[AgentCard]) -> AgentCard:
