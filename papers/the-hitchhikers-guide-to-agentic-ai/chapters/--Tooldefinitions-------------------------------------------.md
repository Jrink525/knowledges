# -- Tool definitions ----------------------------------------------------------


@tool
def web_search(query: str) -> str:
    """Search the web for information."""
    return f"Search results for '{query}': [simulated results]"


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email. REQUIRES HUMAN APPROVAL."""
    return f"Email sent to {to} with subject '{subject}'"
\end{lstlisting}

```python
@tool
def read_file(path: str) -> str:
    """Read a file from the filesystem."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {path}"

