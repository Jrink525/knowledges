# -- 工具（LLM 调用的操作）-----------------------------------------------
@mcp.tool()
def create_note(title: str, content: str, tags: list[str] | None = None) -> str:
    """使用给定的标题和内容创建一条新的文本笔记。

    当用户想要保存信息以备后用时应使用此工具。
    返回笔记保存的路径。
    """
    tags = tags or []
    safe_title = "".join(
        c if c.isalnum() or c in " -_" else "_" for c in title
    ).strip()
    note_path = NOTES_DIR / f"{safe_title}.md"

    frontmatter = f"---\ntitle: {title}\ntags: {tags}\n---\n\n"
    note_path.write_text(frontmatter + content, encoding="utf-8")
    return f"笔记已保存至 {note_path}"


@mcp.tool()
def search_notes(query: str) -> str:
    """通过关键词搜索笔记。同时搜索标题和内容。

    返回匹配的笔记标题和片段列表。
    在创建新笔记之前使用此工具检查是否已存在。
    """
    query_lower = query.lower()
    results = []

    for note_file in NOTES_DIR.glob("*.md"):
        text = note_file.read_text(encoding="utf-8")
        if query_lower in text.lower():
            idx = text.lower().find(query_lower)
            snippet = text[max(0, idx - 50):idx + 100].replace("\n", " ")
            results.append(f"- **{note_file.stem}**: ...{snippet}...")

    return "\n".join(results) if results else f"未找到匹配 '{query}' 的笔记"


