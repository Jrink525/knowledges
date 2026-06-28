# ChatML format
template = """<|im_start|>system
{system_message}<|im_end|>
<|im_start|>user
{user_message}<|im_end|>
<|im_start|>assistant
{assistant_message}<|im_end|>"""
\end{lstlisting}

\subsubsection*{Llama Format}
\subsubsection*{Llama 格式}
\label{llama-format}

Llama 3 uses a different template with special tokens:
Llama 3 使用了一种不同的模板，带有特殊 token：

\begin{lstlisting}[style=pythonstyle]
