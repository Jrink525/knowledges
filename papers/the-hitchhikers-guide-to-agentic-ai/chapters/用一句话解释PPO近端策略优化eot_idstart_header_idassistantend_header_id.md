# 用一句话解释 PPO（近端策略优化）。<|eot_id|><|start_header_id|>assistant<|end_header_id|>
#
#
\end{lstlisting}

\begin{keybox}[特殊令牌最佳实践]
\begin{itemize}
  \item \textbf{Never split special tokens}: They must be atomic---ensure your tokenizer treats them as single units, not character sequences.
  \item \textbf{绝不分拆特殊令牌}：它们必须是原子性的——确保你的分词器将它们视为单个单元，而非字符序列。
  \item \textbf{Mask loss on special tokens}: During SFT, do not compute loss on structural tokens (role markers, separators). The model should not ``learn'' to predict formatting.
  \item \textbf{在特殊令牌上掩码损失}：在 SFT（监督微调）期间，不对结构令牌（角色标记、分隔符）计算损失。模型不应“学习”预测格式。
  \item \textbf{Use templates for structure}: Encode task semantics via special tokens rather than natural language instructions. E.g., \texttt{<|tool\_call|>} is more reliable than ``Now I will call a tool:''.
  \item \textbf{使用模板进行结构化}：通过特殊令牌而非自然语言指令编码任务语义。例如，\texttt{<|tool\_call|>} 比“现在我将调用一个工具：”更可靠。
  \item \textbf{Tool/function calling}: Define dedicated tokens like \texttt{<|function|>}, \texttt{<|result|>} to create unambiguous boundaries between reasoning and action.
  \item \textbf{工具/函数调用}：定义专用令牌，如 \texttt{<|function|>}、\texttt{<|result|>}，以在推理和动作之间创建无歧义的边界。
  \item \textbf{Consistent handling in RL}: During PPO/GRPO, ensure the reference model and policy model use identical tokenization and special token handling---mismatches corrupt KL computation.
  \item \textbf{在强化学习（RL）中一致处理}：在 PPO/GRPO 期间，确保参考模型和策略模型使用相同的分词和特殊令牌处理——不匹配会破坏 KL 计算。
  \item \textbf{EOS handling}: During generation, ensure EOS is included in the action space. If the model cannot emit EOS, responses grow unbounded (common RL failure mode).
  \item \textbf{EOS 处理}：在生成期间，确保 EOS 包含在动作空间中。如果模型无法输出 EOS，响应将无限增长（常见的 RL 失败模式）。
\end{itemize}
\end{keybox}

