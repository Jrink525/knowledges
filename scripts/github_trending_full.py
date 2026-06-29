#!/usr/bin/env python3
"""github_trending_full.py — 自包含脚本：抓取 + 发送微信，无需 agent 干预"""

import json
import os
import re
import socket
import sys
import urllib.request
from datetime import datetime, timezone

TRENDING_URL = "https://github.com/trending"
socket.setdefaulttimeout(15)


def fetch_html():
    req = urllib.request.Request(
        TRENDING_URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_repos(html):
    articles = re.findall(
        r'<article class="Box-row[^"]*"[^>]*>(.*?)</article>', html, re.DOTALL
    )
    repos = []
    for a in articles:
        h2_start = a.find("<h2")
        h2_region = a[h2_start : h2_start + 1500]
        name_match = re.search(r'href="/([^/"]+)/([^/"]+)"', h2_region)
        if not name_match:
            continue
        full_name = f"{name_match.group(1)}/{name_match.group(2)}"
        desc_match = re.search(
            r'<p[^>]*class="col-9[^"]*color-fg-muted[^"]*"[^>]*>\s*(.*?)\s*</p>',
            a,
            re.DOTALL,
        )
        description = ""
        if desc_match:
            description = re.sub(r"<[^>]+>", "", desc_match.group(1)).strip()
        lang_match = re.search(
            r'itemprop="programmingLanguage"[^>]*>(.*?)</span>', a, re.DOTALL
        )
        language = lang_match.group(1).strip() if lang_match else "N/A"
        stars_match = re.search(
            r'/stargazers[^"]*"[^>]*>.*?</svg>\s*([\d,]+)', a, re.DOTALL
        )
        stars_total = stars_match.group(1).strip() if stars_match else "?"
        forks_match = re.search(
            r'/forks[^"]*"[^>]*>.*?</svg>\s*([\d,]+)', a, re.DOTALL
        )
        forks = forks_match.group(1).strip() if forks_match else "?"
        today_match = re.search(r"([\d,]+)\s+stars?\s+today", a)
        stars_today = today_match.group(1).strip() if today_match else "0"
        contributors = re.findall(r'alt="@([^"]+)"', a)
        repos.append(
            {
                "name": full_name,
                "description": description,
                "language": language,
                "stars": stars_total,
                "forks": forks,
                "stars_today": stars_today,
                "contributors": contributors,
            }
        )
    return repos


def main():
    html = fetch_html()
    repos = parse_repos(html)
    if not repos:
        print("ERROR: 未提取到任何仓库")
        sys.exit(1)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [f"🔥 GitHub Trending Top 10（{date_str}）\n"]
    for i, r in enumerate(repos[:10], 1):
        lines.append(f"{i}. {r['name']}  ★ +{r['stars_today']} today")
        if r["description"]:
            lines.append(f"   {r['description']}")
        if r["contributors"]:
            lines.append(f"   Built by {' · '.join(r['contributors'][:5])}")
        lines.append(f"   语言：{r['language']} · 总星 {r['stars']}")
        lines.append(f"   https://github.com/{r['name']}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
