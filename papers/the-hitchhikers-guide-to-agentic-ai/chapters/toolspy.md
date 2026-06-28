# === tools.py ===
import httpx
import json
import os
import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse
from langchain_core.tools import tool
from tenacity import retry, stop_after_attempt, wait_exponential
from utils import extract_text  # HTML -> 纯文本辅助函数（例如 BeautifulSoup）
from database import db          # 应用数据库连接


@tool
@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def search_web(query: str, num_results: int = 5) -> str:
    """搜索网络信息。返回 JSON 格式的结果列表。"""
    if not query.strip():
        raise ValueError("搜索查询不能为空")
    response = httpx.get(
        "https://api.search.example.com/search",
        params={"q": query, "n": num_results},
        headers={"Authorization": f"Bearer {os.environ['SEARCH_API_KEY']}"},
        timeout=10.0,
    )
    response.raise_for_status()
    results = response.json()["results"]
    return json.dumps([{"title": r["title"], "url": r["url"],
                        "snippet": r["snippet"]} for r in results])


@tool
@retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=5))
def fetch_document(url: str, max_chars: int = 5000) -> str:
    """从 URL 获取并提取文本内容。"""
    allowed_domains = os.environ.get("ALLOWED_DOMAINS", "").split(",")
    domain = urlparse(url).netloc
    if allowed_domains[0] and domain not in allowed_domains:
        raise PermissionError(f"域名 {domain} 不在允许列表中")
    response = httpx.get(url, timeout=15.0, follow_redirects=True)
    response.raise_for_status()
    return extract_text(response.text)[:max_chars]


@tool
def save_report(title: str, summary: str, sections: list[dict]) -> str:
    """将结构化研究报告保存到数据库。"""
    report_id = str(uuid.uuid4())
    db.reports.insert_one({
        "id": report_id, "title": title,
        "summary": summary, "sections": sections,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return json.dumps({"report_id": report_id, "status": "saved"})


TOOLS = [search_web, fetch_document, save_report]
\end{lstlisting}

\begin{lstlisting}[style=pythonstyle, caption={Complete production research agent: state and nodes}]
