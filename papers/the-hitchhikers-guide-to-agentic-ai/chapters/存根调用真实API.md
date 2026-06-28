                                           # 存根；调用真实 API


@tool
def read_document(url: str) -> str:
    """Fetch and read the content of a document at a URL."""
    """获取并读取某个 URL 上的文档内容。"""
    return f"Document content from: {url}"


tools = [search_web, read_document]


