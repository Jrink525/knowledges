    # dataset_text_field="text",  # 或使用 formatting_func
)
trainer.train()
\end{lstlisting}
\end{examplebox}

## Chat Templates and Formatting
## 聊天模板与格式化

\label{sec:chat-templates}

\begin{intuitionbox}[Why Chat Templates Matter]
Language models are trained on raw text, but instruction-following models need to distinguish between system prompts, user messages, and assistant responses. Chat templates encode this structure into the token sequence. Using the wrong template (or no template) at inference time causes significant performance degradation.
\end{intuitionbox}
\begin{intuitionbox}[聊天模板的重要性]
语言模型是在原始文本上训练的，但指令遵循模型需要区分系统提示、用户消息和助手响应。聊天模板将这种结构编码到 token 序列中。在推理时使用错误的模板（或没有模板）会导致显著的性能下降。
\end{intuitionbox}

\subsubsection*{ChatML Format}
\subsubsection*{ChatML 格式}
\label{chatml-format}

ChatML is the most widely used chat template:
ChatML 是使用最广泛的聊天模板：

\begin{lstlisting}[style=pythonstyle]
