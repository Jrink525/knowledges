# 解码：令牌 ID -> 文本
decoded = tokenizer.decode(encoded)
print("Decoded:", decoded)  # 还原为原始文本
\end{lstlisting}

```markdown
\begin{lstlisting}[style=pythonstyle, caption={Tokenization example with Llama-3 tokenizer (byte-level BPE).}]
