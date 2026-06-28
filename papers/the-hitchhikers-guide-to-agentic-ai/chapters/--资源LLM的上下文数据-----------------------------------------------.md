# -- 资源（LLM 的上下文数据）-----------------------------------------------
@mcp.resource("notes://{title}")
def get_note(title: str) -> str:
    """通过标题读取笔记。"""
    note_path = NOTES_DIR / f"{title}.md"
    if not note_path.exists():
        raise ValueError(f"未找到笔记：{title}")
    return note_path.read_text(encoding="utf-8")


