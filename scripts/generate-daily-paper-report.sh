#!/bin/bash
# ============================================================
# generate-daily-paper-report.sh
# 从 fetch-daily-papers.sh 的输出 + papers/ 深度解读产物
# 生成每日论文日报 Markdown 报告，并提交到 GitHub。
#
# 用法:
#   ./scripts/generate-daily-paper-report.sh [input_json] [date]
#     默认 input_json=./papers/today-hf-papers.json
#     默认 date=today (YYYY-MM-DD)
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

INPUT_JSON="${1:-${WORKSPACE_DIR}/papers/today-hf-papers.json}"
DATE="${2:-$(date -u '+%Y-%m-%d')}"
REPORT_FILE="${WORKSPACE_DIR}/papers/daily-report-${DATE}.md"

# ---------- 检查输入 ----------
if [ ! -f "$INPUT_JSON" ]; then
  echo "❌ 输入文件不存在: $INPUT_JSON"
  echo "   先运行 scripts/fetch-daily-papers.sh"
  exit 1
fi

# ---------- 生成报告 (使用临时 Python 脚本避免引用问题) ----------
TMP_PY=$(mktemp /tmp/paper-report.XXXXXX.py)
trap 'rm -f "$TMP_PY"' EXIT

cat > "$TMP_PY" << 'PYEOF'
import json, os, re
import sys

input_json = sys.argv[1]
workspace_dir = sys.argv[2]
report_file = sys.argv[3]
date_display = sys.argv[4]

with open(input_json) as f:
    papers = json.load(f)

GITHUB_BASE = 'https://github.com/Jrink525/knowledges/tree/master/papers'

def slugify(title):
    s = title.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = s.strip('-')
    return s

lines = []
lines.append(f'# 📄 每日论文日报 — {date_display}')
lines.append('')
lines.append(f'共筛选出 **{len(papers)}** 篇感兴趣的论文。')
lines.append('')
lines.append('---')
lines.append('')

for i, p in enumerate(papers, 1):
    title = p.get('title', 'Unknown')
    arxiv_id = p.get('arxiv_id', '')
    summary = p.get('summary', '')
    ai_summary = p.get('ai_summary', '')
    cats = p.get('arxiv_categories', [])
    upvotes = p.get('upvotes', 0)
    arxiv_url = p.get('arxiv_url', '')
    pdf_url = p.get('pdf_url', '')
    github_url = p.get('github_url', '') or ''
    hf_url = p.get('hf_discussion', '')

    paper_slug = slugify(title)
    paper_dir_name = f'{paper_slug}-{arxiv_id}'
    deep_read_path = os.path.join(workspace_dir, 'papers', paper_dir_name, 'report.md')
    has_deep_read = os.path.exists(deep_read_path)

    github_deep_read_url = f'{GITHUB_BASE}/{paper_dir_name}/report.md' if has_deep_read else None
    github_dir_url = f'{GITHUB_BASE}/{paper_dir_name}' if has_deep_read else None

    cat_tags = ' '.join(f'`{c}`' for c in cats)

    lines.append(f'## {i}. {title}')
    lines.append('')
    lines.append(f'- **arXiv ID**: [{arxiv_id}]({arxiv_url})')
    if cats:
        lines.append(f'- **分类**: {cat_tags}')
    if upvotes > 0:
        lines.append(f'- **HF 热度**: 👍 {upvotes}')
    if github_url:
        lines.append(f'- **GitHub**: [{github_url}]({github_url})')
    if hf_url:
        lines.append(f'- **HF 讨论**: [{hf_url}]({hf_url})')
    lines.append('')

    if ai_summary:
        lines.append('### 🤖 AI 摘要')
        lines.append('')
        lines.append(ai_summary)
        lines.append('')

    if summary:
        short_summary = summary[:500] + ('...' if len(summary) > 500 else '')
        lines.append('### 📋 原始摘要（节选）')
        lines.append('')
        lines.append(short_summary)
        lines.append('')

    if has_deep_read:
        lines.append('### 🔍 深度解读')
        lines.append('')
        lines.append(f'- 📖 [深度解读报告]({github_deep_read_url}) — 可直接打开')
        lines.append(f'- 📂 [完整解读目录]({github_dir_url})')

        db_path = os.path.join(workspace_dir, 'papers', paper_dir_name, 'direction_board.json')
        if os.path.exists(db_path):
            lines.append(f'- 🧭 [研究方向挖掘]({GITHUB_BASE}/{paper_dir_name}/direction_board.json)')

        rl_path = os.path.join(workspace_dir, 'papers', paper_dir_name, 'research_lens.json')
        if os.path.exists(rl_path):
            lines.append(f'- 🔬 [问题重构分析]({GITHUB_BASE}/{paper_dir_name}/research_lens.json)')
    else:
        lines.append('')
        lines.append('> ⏳ 深度解读尚未完成或尚未加入知识库')

    lines.append('')
    lines.append('---')
    lines.append('')

lines.append('')
lines.append(f'> 报告生成时间: {date_display} | 数据来源: Hugging Face Daily Papers + arXiv')

report = '\n'.join(lines)

with open(report_file, 'w') as f:
    f.write(report)

with_count = sum(1 for p in papers if os.path.exists(
    os.path.join(workspace_dir, 'papers', slugify(p.get('title', '')) + '-' + p.get('arxiv_id', ''), 'report.md')))

print(f'Report saved: {report_file}')
print(f'Total papers: {len(papers)}')
print(f'With deep-read: {with_count}')
PYEOF

python3 "$TMP_PY" "$INPUT_JSON" "$WORKSPACE_DIR" "$REPORT_FILE" "$DATE"

# ---------- 提交到 GitHub ----------
if [ -f "${SCRIPT_DIR}/git-knowledge-commit.sh" ]; then
  # 检查知识库内是否有 papers/ 变更
  cd "$WORKSPACE_DIR"
  if git diff --cached --quiet -- papers/ 2>/dev/null && git diff --quiet -- papers/ 2>/dev/null; then
    echo "📄 报告已生成，但 papers/ 无变更，跳过 GitHub 提交"
  else
    bash "${SCRIPT_DIR}/git-knowledge-commit.sh" -m "📄 每日论文日报 ${DATE}" 2>&1 || echo "⚠️  git commit 失败（可能是暂存区状态问题）"
  fi
else
  echo "⚠️  未找到 git-knowledge-commit.sh，跳过 GitHub 提交"
fi

echo ""
echo "📊 日报已生成: $REPORT_FILE"
echo "📎 可直接用浏览器打开此文件查看完整报告"
