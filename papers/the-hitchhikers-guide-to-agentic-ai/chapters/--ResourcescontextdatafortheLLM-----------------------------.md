# -- Resources (context data for the LLM) -------------------------------------
@mcp.resource("notes://{title}")
def get_note(title: str) -> str:
    """Read a note by title."""
    note_path = NOTES_DIR / f"{title}.md"
    if not note_path.exists():
        raise ValueError(f"Note not found: {title}")
    return note_path.read_text(encoding="utf-8")


