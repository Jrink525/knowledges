        # BF16 path: no scaling needed
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

    scheduler.step()
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={使用HuggingFace和手动PyTorch AMP进行混合精度训练。}]
