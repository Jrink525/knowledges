#!/usr/bin/env python3
"""GitHub Trending 推送脚本 — 直接解析官方页面，保证数据质量。

数据源：直接 curl GitHub Trending 页面 HTML，Python 正则解析。
比第三方 JSON API 更完整（含 Built by 贡献者信息），比 web_fetch 方式更稳定快速。
"""

import json
import re
import sys
import urllib.request
from datetime import datetime, timezone

TRENDING_URL = "https://github.com/trending"


def fetch_html():
    """获取 GitHub Trending 页面 HTML"""
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
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_repos(html):
    """从 HTML 中提取 trending repo 数据"""
    articles = re.findall(
        r'<article class="Box-row[^"]*"[^>]*>(.*?)</article>',
        html,
        re.DOTALL,
    )

    repos = []
    for a in articles:
        h2_region = a[a.find("<h2") : a.find("<h2") + 1500]

        # --- repo name（从 href 提取 owner/name）---
        name_match = re.search(
            r'href="/([^/"]+)/([^/"]+)"', h2_region
        )
        if not name_match:
            continue
        full_name = f"{name_match.group(1)}/{name_match.group(2)}"

        # --- description ---
        desc_match = re.search(
            r'<p[^>]*class="col-9[^"]*color-fg-muted[^"]*"[^>]*>\s*(.*?)\s*</p>',
            a,
            re.DOTALL,
        )
        description = ""
        if desc_match:
            description = re.sub(r"<[^>]+>", "", desc_match.group(1)).strip()

        # --- language ---
        lang_match = re.search(
            r'itemprop="programmingLanguage"[^>]*>(.*?)</span>', a, re.DOTALL
        )
        language = lang_match.group(1).strip() if lang_match else "N/A"

        # --- total stars ---
        stars_match = re.search(
            r'/stargazers[^"]*"[^>]*>.*?</svg>\s*([\d,]+)', a, re.DOTALL
        )
        stars_total = stars_match.group(1).strip() if stars_match else "?"

        # --- forks ---
        forks_match = re.search(
            r'/forks[^"]*"[^>]*>.*?</svg>\s*([\d,]+)', a, re.DOTALL
        )
        forks = forks_match.group(1).strip() if forks_match else "?"

        # --- stars today ---
        today_match = re.search(r"([\d,]+)\s+stars?\s+today", a)
        stars_today = today_match.group(1).strip() if today_match else "0"

        # --- built by contributors ---
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


def format_message(repos, date_str):
    """格式化为微信可读的文本"""
    lines = [f"🔥 GitHub Trending Top 10（{date_str}）\n"]
    for i, r in enumerate(repos[:10], 1):
        name = r["name"]
        desc = r["description"]
        lang = r["language"]
        stars = r["stars"]
        today = r["stars_today"]
        contribs = r["contributors"]
        url = f"https://github.com/{name}"

        lines.append(f"{i}. {name}  ★ +{today} today")
        if desc:
            lines.append(f"   {desc}")
        if contribs:
            by_str = " · ".join(contribs[:5])
            lines.append(f"   Built by {by_str}")
        lines.append(f"   语言：{lang} · 总星 {stars}")
        lines.append(f"   {url}")
        if i < 10:
            lines.append("")

    return "\n".join(lines)


def main():
    try:
        html = fetch_html()
        repos = parse_repos(html)
        if not repos:
            print("ERROR: 未提取到任何仓库")
            sys.exit(1)

        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        msg = format_message(repos, date_str)
        print(msg)

    except urllib.request.URLError as e:
        print(f"ERROR: 网络请求失败 — {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
