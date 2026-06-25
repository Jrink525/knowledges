#!/usr/bin/env python3
"""
Fetch GitHub Trending Top 10 via web_fetch-like approach (server-rendered content).
Falls back to direct HTML if JinAI fails.
Outputs formatted WeChat message to stdout.
"""

import re
import subprocess
import sys
from datetime import datetime, timezone


def beijing_now() -> str:
    bj_ts = datetime.now(timezone.utc).timestamp() + 8 * 3600
    return datetime.fromtimestamp(bj_ts, tz=timezone.utc).strftime("%Y-%m-%d")


def fetch() -> str:
    """Fetch as curl-user-agent to get server-rendered HTML."""
    result = subprocess.run(
        ["curl", "-sL", "--max-time", "20",
         "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
         "-H", "Accept: text/html,application/xhtml+xml",
         "https://github.com/trending"],
        capture_output=True, text=True, timeout=25
    )
    return result.stdout


def extract_repos_from_html(html: str):
    """
    Parse GitHub trending HTML. Even though star counts are client-side rendered,
    we extract: name, description, language. Stars info is secondary.
    """
    repos = []
    articles = re.findall(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)

    for article in articles:
        # Repo name from h2 > a
        h2 = re.search(r'<h2[^>]*>(.*?)</h2>', article, re.DOTALL)
        if not h2:
            continue
        link = re.search(r'href="/([^"/]+/[^"/]+)"', h2.group(1))
        if not link:
            continue
        name = link.group(1)

        # Description
        desc = ""
        p = re.search(r'<p[^>]*>(.*?)</p>', article, re.DOTALL)
        if p:
            desc = re.sub(r'<[^>]+>', ' ', p.group(1))
            desc = re.sub(r'\s+', ' ', desc).strip()

        # Language
        lang = ""
        lang_match = re.search(r'itemprop="programmingLanguage"[^>]*>([^<]+)<', article)
        if lang_match:
            lang = lang_match.group(1).strip()

        repos.append({
            "name": name,
            "description": desc[:300],
            "language": lang,
            "url": f"https://github.com/{name}"
        })

        if len(repos) >= 10:
            break

    return repos


def format_message(repos, date_str: str) -> str:
    lines = [f"🔥 GitHub Trending Top 10（{date_str}）", ""]
    for i, r in enumerate(repos, 1):
        lines.append(f"{i}. {r['name']}")
        if r['description']:
            lines.append(f"   {r['description']}")
        if r['language']:
            lines.append(f"   🌐 {r['language']}")
        lines.append(f"   {r['url']}")
        lines.append("")
    lines.append("— GitHub Trending Daily —")
    return "\n".join(lines)


def main():
    try:
        html = fetch()
        repos = extract_repos_from_html(html)
        if not repos:
            print("ERROR: no repos parsed")
            sys.exit(1)
        msg = format_message(repos, beijing_now())
        print(msg)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
