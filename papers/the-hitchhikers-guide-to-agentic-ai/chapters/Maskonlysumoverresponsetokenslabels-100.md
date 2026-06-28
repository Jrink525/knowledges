    # Mask: only sum over response tokens (labels != -100)
    mask = (labels != -100).float()
    return (token_logps * mask).sum(dim=-1)  # Shape: [batch_size]
\end{lstlisting}
\begin{lstlisting}[style=pythonstyle]
def dpo_loss(model, ref_model, batch, beta=0.1):
    """一次 DPO 训练步骤。"""
