# === graph.py ===
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
```

## async def build_graph(db_url: str) -> CompiledStateGraph:
## async def build_graph(db_url: str) -> CompiledStateGraph:

```python
async def build_graph(db_url: str) -> CompiledStateGraph:
    """Build and compile the research agent graph."""
    checkpointer = AsyncPostgresSaver.from_conn_string(db_url)
    await checkpointer.setup()  # Create tables if needed
