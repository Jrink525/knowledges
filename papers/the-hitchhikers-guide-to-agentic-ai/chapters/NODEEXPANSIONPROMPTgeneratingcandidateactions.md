# === NODE EXPANSION PROMPT (generating candidate actions) ===
EXPAND_PROMPT = """You are a web navigation agent. Given the current
page state, propose 3 DIFFERENT next actions to try.


Current page: British Airways booking - flight details
  Price: \$489 | Departure: Dec 15 8:30am | Arrival: Dec 15 8:45pm
  [Button: Select] [Button: Back to results] [Link: Fare rules]


Generate 3 diverse candidate actions (explore different strategies):
Action 1:"""  # Model generates 3 options for tree expansion
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[LATS提示词：价值估计与节点扩展]
\begin{lstlisting}[style=pythonstyle]
