#!/usr/bin/env python3
"""GitHub Trending 推送脚本 — 获取今日 Trending Top 10 并格式化为微信消息。"""

import json
import urllib.request
import sys
from datetime import datetime, timezone

API_URL = "https://githubtrending.lessx.xyz/trending?since=daily"


def fetch_trending():
    req = urllib.request.Request(
        API_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; OpenClaw)"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def format_message(data, date_str):
    lines = [f"🔥 GitHub Trending Top 10（{date_str}）\n"]
    for i, repo in enumerate(data[:10], 1):
        name = repo["name"]
        stars_today = repo["increased"].replace(" stars today", "").replace(" star today", "").strip()
        stars_total = repo.get("stars", "?")
        lang = repo.get("language") or "N/A"
        desc = (repo.get("description") or "无描述").strip()
        url = f"https://github.com/{name}"

        lines.append(f"{i}. {name}  ★ +{stars_today} today")
        if desc:
            lines.append(f"   {desc}")
        lines.append(f"   语言：{lang} · 总星 {stars_total}")
        lines.append(f"   {url}")
        if i < 10:
            lines.append("")  # blank line between items

    return "\n".join(lines)


def main():
    try:
        data = fetch_trending()
        if not data:
            print("ERROR: API returned empty list")
            sys.exit(1)
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        msg = format_message(data, date_str)
        print(msg)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
