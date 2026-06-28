# -- Tools (LLM-invoked actions) -----------------------------------------------
@mcp.tool()
def create_note(title: str, content: str, tags: list[str] | None = None) -> str:
    """Create a new text note with a given title and content.

    Use this when the user wants to save information for later.
    Returns the path where the note was saved.
    """
    tags = tags or []
    safe_title = "".join(
        c if c.isalnum() or c in " -_" else "_" for c in title
    ).strip()
    note_path = NOTES_DIR / f"{safe_title}.md"

    frontmatter = f"---\ntitle: {title}\ntags: {tags}\n---\n\n"
    note_path.write_text(frontmatter + content, encoding="utf-8")
    return f"Note saved to {note_path}"


@mcp.tool()
def search_notes(query: str) -> str:
    """Search notes by keyword. Searches both titles and content.

    Returns a list of matching note titles and snippets.
    Use this before creating a note to check if one already exists.
    """
    query_lower = query.lower()
    results = []

    for note_file in NOTES_DIR.glob("*.md"):
        text = note_file.read_text(encoding="utf-8")
        if query_lower in text.lower():
            idx = text.lower().find(query_lower)
            snippet = text[max(0, idx - 50):idx + 100].replace("\n", " ")
            results.append(f"- **{note_file.stem}**: ...{snippet}...")

    return "\n".join(results) if results else f"No notes found matching '{query}'"


