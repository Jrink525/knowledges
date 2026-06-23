#!/usr/bin/env python3
"""
add_sources_to_notebooklm.py — 将今日论文 source 批量添加到 NotebookLM notebook

用法:
  python3 add_sources_to_notebooklm.py <workspace_dir> <notebook_id> [date]

依赖:
  - NOTEBOOKLM_HOME 环境变量（或其默认值 /tmp/notebooklm）
  - PYTHONPATH 包含 notebooklm-py 的依赖路径
  - papers/today-hf-papers.json 必须存在
"""

import json, os, re, sys, subprocess, tempfile, time

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.openclaw/workspace")
NOTEBOOK_ID = sys.argv[2] if len(sys.argv) > 2 else None
PAPER_JSON = os.path.join(WORKSPACE, "papers/today-hf-papers.json")

if not os.path.exists(PAPER_JSON):
    print(f"❌ 论文列表不存在: {PAPER_JSON}")
    sys.exit(1)

with open(PAPER_JSON) as f:
    papers = json.load(f)

print(f"📋 共 {len(papers)} 篇论文")

def slugify(title):
    s = title.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = s.strip('-')
    return s

def safe_str(v, maxlen=0):
    """安全获取字符串值，兼容非字符串类型"""
    if v is None:
        return ""
    if isinstance(v, str):
        return v[:maxlen] if maxlen else v
    return str(v)

def run_nb(args):
    """运行 notebooklm 命令"""
    env = os.environ.copy()
    env.setdefault("NOTEBOOKLM_HOME", "/tmp/notebooklm")
    env.setdefault("PYTHONPATH", "/tmp/pip-lib")
    cmd = ["python3", "-m", "notebooklm"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=120)
    return result.stdout, result.stderr, result.returncode

# 如果没有 notebook_id，创建一个新的
if not NOTEBOOK_ID:
    date = sys.argv[3] if len(sys.argv) > 3 else time.strftime("%Y-%m-%d")
    title = f"📄 每日论文播客 {date}"
    print(f"📓 创建 Notebook: {title}")
    stdout, stderr, rc = run_nb(["create", title, "--use", "--json"])
    if rc != 0:
        print(f"❌ 创建失败: {stderr}")
        sys.exit(1)
    try:
        NOTEBOOK_ID = json.loads(stdout)["notebook"]["id"]
        print(f"   ID: {NOTEBOOK_ID}")
    except (json.JSONDecodeError, KeyError):
        print(f"❌ 解析失败: {stdout[:200]}")
        sys.exit(1)

print(f"📓 Notebook: {NOTEBOOK_ID}")
print(f"📝 添加 source...")

FAILED = 0
for i, p in enumerate(papers, 1):
    title = safe_str(p.get("title", "Unknown"))
    arxiv_id = safe_str(p.get("arxiv_id", ""))
    summary = safe_str(p.get("summary", ""))
    ai_summary = safe_str(p.get("ai_summary", ""))
    arxiv_url = safe_str(p.get("arxiv_url", ""))
    cats = ", ".join(p.get("arxiv_categories", []))

    paper_slug = slugify(title)
    paper_dir = os.path.join(WORKSPACE, "papers", f"{paper_slug}-{arxiv_id}")

    source_parts = [f"# {title}", ""]
    source_parts.append("## 基本信息")
    source_parts.append(f"- 链接: {arxiv_url}")
    if cats:
        source_parts.append(f"- 分类: {cats}")
    source_parts.append("")
    source_parts.append("## 摘要")
    source_parts.append(summary[:2000])
    source_parts.append("")

    if ai_summary:
        source_parts.append("## AI 摘要")
        source_parts.append(ai_summary[:1000])
        source_parts.append("")

    # 深度解读报告
    report_path = os.path.join(paper_dir, "report.md")
    if os.path.exists(report_path):
        with open(report_path) as rf:
            report_content = rf.read()
        source_parts.append("## 深度解读")
        source_parts.append(report_content[:4000])
        source_parts.append("")

    # 研究方向
    db_path = os.path.join(paper_dir, "direction_board.json")
    if os.path.exists(db_path):
        with open(db_path) as df:
            db_data = json.load(df)
        seeds = db_data.get("ranking", db_data.get("results", []))[:3]
        if seeds:
            source_parts.append("## 研究方向建议")
            for s in seeds:
                name = s.get("name", s.get("title", ""))
                desc = safe_str(s.get("description", s.get("rationale", "")), 200)
                if name:
                    source_parts.append(f"- {name}: {desc}")
            source_parts.append("")

    # 问题重构
    rl_path = os.path.join(paper_dir, "research_lens.json")
    if os.path.exists(rl_path):
        with open(rl_path) as rf:
            rl_data = json.load(rf)
        problem = safe_str(rl_data.get("reconstructed_problem", ""), 1000)
        if problem:
            source_parts.append("## 核心问题")
            source_parts.append(problem)
            source_parts.append("")

    full_text = "\n".join(source_parts)

    # 写入临时文件（避免命令行参数过长）
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, dir="/tmp")
    tmp.write(full_text)
    tmp_path = tmp.name
    tmp.close()

    safe_title = title[:80]
    print(f"  [{i}/{len(papers)}] {safe_title[:50]}...", end=" ", flush=True)
    stdout, stderr, rc = run_nb([
        "source", "add",
        "--type", "text",
        "--notebook", NOTEBOOK_ID,
        "--title", safe_title,
        tmp_path
    ])
    os.unlink(tmp_path)
    if rc == 0:
        print("✅")
    else:
        print(f"❌ {stderr.strip()[:100]}")
        FAILED += 1

print()
if FAILED:
    print(f"⚠️  {FAILED}/{len(papers)} 篇添加失败")
else:
    print(f"✅ 全部 {len(papers)} 篇添加完成")
print(f"📓 Notebook: {NOTEBOOK_ID}")
