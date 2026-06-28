# -- Context Manager ------------------------------------------
\end{lstlisting}

```python
class ContextManager:
    """
    Manages the context window with budget enforcement,
    compression, and token counting.
    """
    ```
管理上下文窗口，包括预算执行、压缩和令牌计数。

```python
    BUDGET_FRACTIONS = {
        "system":   0.10,
        "memory":   0.20,
        "tools":    0.10,
        "history":  0.50,
        "reserved": 0.10,
    }

    def __init__(self, model: str, max_tokens: int):
        self.model      = model
        self.max_tokens = max_tokens
        self.enc        = tiktoken.encoding_for_model(model)
        self.history:   list[Message] = []
        self.system_msg: Optional[Message] = None

    def count_tokens(self, text: str) -> int:
        return len(self.enc.encode(text))

    def count_message_tokens(self, msg: Message) -> int:
