    # Sample from the verbalized distribution
    import random
    chosen = random.choices(responses, weights=probs, k=1)[0]
    return chosen
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle]
