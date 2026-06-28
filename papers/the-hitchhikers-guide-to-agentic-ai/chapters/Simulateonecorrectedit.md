    # Simulate one correct edit
    fix = "edit\n```python\ndef add(a, b):\n    return a + b\n```"
    result = env.step(fix)
    print(f"\nReward: {result.reward}  |  Terminated: {result.terminated}")
    env.close()
\end{lstlisting}


\begin{keybox}[Design Decisions in the Example Environment]
\begin{itemize}
  \item \textbf{Text-only interface}: observations and actions are plain strings, compatible with any LLM.
  \item \textbf{Execution-based reward}: the reward is derived from running the actual test suite, not from an LLM judge. This makes it tamper-proof and perfectly aligned.
  \item \textbf{Isolated subprocess}: tests run in a separate process with a timeout, preventing infinite loops from crashing the training loop.
  \item \textbf{Gymnasium-compatible}: \texttt{reset}/\texttt{step}/ \texttt{render}/\texttt{close} follow the standard API, enabling drop-in use with RL training frameworks.
\end{itemize}
\end{keybox}


\section{Comparison of Major Agentic Environments}
\label{sec:env-comparison}


Table~\ref{tab:env-comparison} summarizes the key properties of the major agentic environments discussed in this section.

@dataclass
class StepResult:
    observation: str          # 提供给LLM的文本
    reward: float             # 0.0 或 1.0
    terminated: bool          # 回合结束（任务解决或达到最大步数）
    truncated: bool           # 回合被截断（预算超限）
    info: dict[str, Any] = field(default_factory=dict)

