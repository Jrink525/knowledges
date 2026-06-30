#!/usr/bin/env python3
"""github_trending_full.py — v2 自包含脚本：抓取 GitHub Trending + 多级 fallback，无需 agent 干预"""

import json
import os
import re
import socket
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ─── 常量 ────────────────────────────────────────────────
TRENDING_URL = "https://github.com/trending"
SEARCH_API = "https://api.github.com/search/repositories"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
GLOBAL_TIMEOUT = 12  # 每个请求硬限 12 秒
MAX_REPOS = 10


def fetch_url(url, timeout=GLOBAL_TIMEOUT):
    """带超时的 URL 获取"""
    socket.setdefaulttimeout(timeout)
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/json,*/*",
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_repos_from_html(html):
    """从 GitHub Trending HTML 提取仓库列表"""
    articles = re.findall(
        r'<article class="Box-row[^"]*"[^>]*>(.*?)</article>', html, re.DOTALL
    )
    repos = []
    for a in articles:
        h2_start = a.find("<h2")
        if h2_start == -1:
            continue
        h2_region = a[h2_start : h2_start + 1500]
        name_match = re.search(r'href="/([^/"]+)/([^/"]+)"', h2_region)
        if not name_match:
            continue
        full_name = f"{name_match.group(1)}/{name_match.group(2)}"
        desc_match = re.search(
            r'<p[^>]*class="col-9[^"]*color-fg-muted[^"]*"[^>]*>\s*(.*?)\s*</p>',
            a, re.DOTALL,
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
        repos.append({
            "name": full_name,
            "description": description,
            "language": language,
            "stars": stars_total,
            "forks": forks,
            "stars_today": stars_today,
            "contributors": contributors,
        })
    return repos


def parse_repos_from_search(items):
    """从 GitHub Search API 结果提取仓库列表（fallback 用）"""
    repos = []
    for r in items[:MAX_REPOS]:
        repos.append({
            "name": r["full_name"],
            "description": r.get("description", "") or "",
            "language": r.get("language") or "N/A",
            "stars": str(r.get("stargazers_count", "?")),
            "forks": str(r.get("forks_count", "?")),
            "stars_today": "N/A",  # Search API 不提供今日增量
            "contributors": [],
        })
    return repos


def format_message(repos, date_str, source="GitHub Trending"):
    """格式化输出消息"""
    lines = [f"🔥 GitHub Trending Top {min(len(repos), MAX_REPOS)}（{date_str}）\n"]
    for i, r in enumerate(repos[:MAX_REPOS], 1):
        lines.append(f"{i}. {r['name']}  ★ +{r['stars_today']} today")
        if r["description"]:
            desc = r["description"][:120]
            lines.append(f"   {desc}")
        if r["contributors"]:
            names = " · ".join(r["contributors"][:5])
            lines.append(f"   Built by {names}")
        lines.append(f"   语言：{r['language']} · 总星 {r['stars']}")
        lines.append(f"   https://github.com/{r['name']}")
    return "\n".join(lines)


def main():
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    repos = []

    # ─── 方法 1：从 GitHub Trending 页面抓取 ───
    try:
        html = fetch_url(TRENDING_URL)
        repos = parse_repos_from_html(html)
        if repos:
            print(format_message(repos, date_str, "GitHub Trending"))
            return
    except Exception as e:
        sys.stderr.write(f"[WARN] Scrape trending.github.com failed: {e}\n")

    # ─── 方法 2：fallback 到 GitHub Search API ───
    try:
        # 按 stars 排序 + 最近 push 的活跃项目
        search_url = (
            f"{SEARCH_API}?q=stars:%3E100+pushed:%3E{date_str}"
            f"&sort=stars&order=desc&per_page={MAX_REPOS}"
        )
        req = urllib.request.Request(
            search_url,
            headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"},
        )
        with urllib.request.urlopen(req, timeout=GLOBAL_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        repos = parse_repos_from_search(data.get("items", []))
        if repos:
            print(format_message(repos, date_str, "GitHub Search API"))
            return
    except Exception as e:
        sys.stderr.write(f"[WARN] GitHub Search API fallback failed: {e}\n")

    # ─── 全部失败 ───
    print("ERROR: 所有获取 GitHub Trending 的方法都失败了")
    sys.exit(1)


if __name__ == "__main__":
    main()
