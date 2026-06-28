# 只有人类管理员持有：admin:config

class A2AServer:
    def verify_authorization(self, token: str, required_scope: str) -> bool:
        """Verify that the calling agent holds the required scope."""
        """验证调用 agent 是否持有所需的 scope。"""
        claims = jwt.decode(token, self.public_key, algorithms=["RS256"])
        granted_scopes = claims.get("scope", "").split()
        if required_scope not in granted_scopes:
            raise PermissionError(
                f"Caller lacks required scope '{required_scope}'. "
                f"Granted: {granted_scopes}"
            )
        return True
\end{lstlisting}


\subsection{Audit Trails and Accountability}
\subsection{审计追踪与问责}
\label{audit-trails-and-accountability}


\begin{warningbox}[The Accountability Gap]
In a chain of agent delegations, it can become unclear \emph{who} is responsible for an action. If Agent A asks Agent B to delete a file, and Agent B does so, who is accountable? Every A2A interaction must be logged with: the calling agent’s identity, the task description, the authorization token used, the timestamp, and the outcome. This audit trail is essential for incident response, compliance, and debugging.
\end{warningbox}

\begin{warningbox}[问责缺口]
在一连串的 agent 委托链中，\emph{谁}对某个行为负责可能变得不清晰。如果 Agent A 要求 Agent B 删除一个文件，而 Agent B 照做了，那么谁应承担责任？每次 A2A 交互都必须记录：调用 agent 的身份、任务描述、所使用的授权令牌、时间戳以及结果。该审计追踪对于事件响应、合规性和调试至关重要。
\end{warningbox}


Every A2A server should emit structured audit logs:
每个 A2A 服务器都应发出结构化的审计日志：


\begin{lstlisting}[style=pythonstyle]
@dataclass
class A2AAuditEvent:
    timestamp: str          # ISO 8601
