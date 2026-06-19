#!/bin/bash
# ============================================================
# generate-daily-paper-report.sh
# 从 fetch-daily-papers.sh 的输出 + papers/ 深度解读产物
# 生成每日论文日报 Markdown 报告，并提交到 GitHub。
#
# 现在支持: 中文摘要 (通过 AI 翻译) + 个性化推荐理由
# 用户画像: Java 工程师 | 正在做 Agent 开发
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

# ---------- 生成报告 ----------
TMP_PY=$(mktemp /tmp/paper-report.XXXXXX.py)
trap 'rm -f "$TMP_PY"' EXIT

cat > "$TMP_PY" << 'PYEOF'
import json, os, re, sys, urllib.request, urllib.error, time

input_json = sys.argv[1]
workspace_dir = sys.argv[2]
report_file = sys.argv[3]
date_display = sys.argv[4]
api_key = os.environ.get('OPENAI_API_KEY', '')
api_base = os.environ.get('OPENAI_BASE_URL', 'https://api.deepseek.com/v1')
api_model = 'deepseek-chat'

with open(input_json) as f:
    papers = json.load(f)

GITHUB_BASE = 'https://github.com/Jrink525/knowledges/tree/master/papers'

USER_PROFILE = """
用户是 Java 工程师，目前正在做 Agent（AI智能体）相关的开发工作。
请针对这个身份给出推荐理由。
"""

def slugify(title):
    s = title.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = s.strip('-')
    return s

# ---------- Call OpenAI to generate Chinese summary + recommendation ----------
def generate_enrichments(papers_list, api_key, api_base, api_model):
    """Batch-generate Chinese summaries and recommendations via LLM API."""
    if not api_key or len(api_key) < 10:
        return {}

    # Build prompt
    paper_descriptions = []
    for i, p in enumerate(papers_list, 1):
        title = p.get('title', 'Unknown')
        summary = p.get('summary', '')[:800]
        ai_summary = p.get('ai_summary', '')[:300]
        cats = p.get('arxiv_categories', [])
        github = p.get('github_url', '')
        paper_descriptions.append(f"""Paper {i}:
Title: {title}
Categories: {', '.join(cats)}
Summary: {summary}
AI Summary: {ai_summary}
GitHub: {github}""")

    prompt = f"""你是一个 AI 研究助手。以下有 {len(papers_list)} 篇论文。

请为每篇论文生成：
1. **中文摘要** (chinese_summary): 2-3 句中文，翻译并概括论文的核心贡献和发现
2. **推荐理由** (recommendation): 2-3 句中文，说明这篇论文对这个用户有什么价值

{USER_PROFILE}

论文列表：
{chr(10).join(paper_descriptions)}

请以 JSON 格式返回（key 为论文序号 "1", "2", ...），格式示例：
{{
  "1": {{
    "chinese_summary": "中文摘要...",
    "recommendation": "推荐理由..."
  }},
  "2": {{
    "chinese_summary": "中文摘要...",
    "recommendation": "推荐理由..."
  }}
}}

只返回 JSON，不要其它文字。"""

    payload = json.dumps({
        "model": api_model,
        "messages": [
            {"role": "system", "content": "你是一个 AI 研究助手，擅长论文分析和个性化推荐。请用中文回答，语言自然流畅，不要过于学术化。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 3000
    }).encode('utf-8')

    req = urllib.request.Request(
        f"{api_base.rstrip('/')}/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
                content = result['choices'][0]['message']['content']
                # Try to parse JSON from response
                # Handle case where response has markdown code block
                content = content.strip()
                if content.startswith('```'):
                    content = re.sub(r'```json\s*|```\s*', '', content)
                enrich = json.loads(content)
                return enrich
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            sys.stderr.write(f"OpenAI API error (attempt {attempt+1}): {e}\n")
            if attempt < 2:
                time.sleep(3)
        except (json.JSONDecodeError, KeyError) as e:
            sys.stderr.write(f"Parse error (attempt {attempt+1}): {e}\n")
            break
    return {}

# Generate enrichments
sys.stderr.write("Generating Chinese summaries and recommendations...\n")
enrichments = generate_enrichments(papers, api_key, api_base, api_model)
sys.stderr.write(f"Got enrichments for {len(enrichments)} papers\n")

# ---------- Build report ----------
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
    github_url = p.get('github_url', '') or ''
    hf_url = p.get('hf_discussion', '')

    # Get enrichments for this paper
    enrich = enrichments.get(str(i), {})
    chinese_summary = enrich.get('chinese_summary', '')
    recommendation = enrich.get('recommendation', '')

    paper_slug = slugify(title)
    paper_dir_name = f'{paper_slug}-{arxiv_id}'
    deep_read_path = os.path.join(workspace_dir, 'papers', paper_dir_name, 'report.md')
    has_deep_read = os.path.exists(deep_read_path)

    github_deep_read_url = f'{GITHUB_BASE}/{paper_dir_name}/report.md' if has_deep_read else None
    github_dir_url = f'{GITHUB_BASE}/{paper_dir_name}' if has_deep_read else None

    cat_tags = ' '.join(f'`{c}`' for c in cats)

    lines.append(f'## {i}. {title}')
    lines.append('')

    # Meta info row
    meta_parts = [f'[{arxiv_id}]({arxiv_url})']
    if cats:
        meta_parts.append(cat_tags)
    if upvotes > 0:
        meta_parts.append(f'👍 {upvotes}')
    if github_url:
        meta_parts.append(f'[GitHub]({github_url})')
    if hf_url:
        meta_parts.append(f'[HF讨论]({hf_url})')
    lines.append(f'> {" | ".join(meta_parts)}')
    lines.append('')

    # Chinese summary (new!)
    if chinese_summary:
        lines.append('### 🇨🇳 中文摘要')
        lines.append('')
        lines.append(chinese_summary)
        lines.append('')

    # AI summary (English)
    if ai_summary:
        lines.append('### 🤖 AI 摘要')
        lines.append('')
        lines.append(ai_summary)
        lines.append('')

    # Recommendation (new!)
    if recommendation:
        lines.append('### 💡 推荐理由')
        lines.append('')
        lines.append(f'> {recommendation}')
        lines.append('')

    # Original summary
    if summary:
        short_summary = summary[:400] + ('...' if len(summary) > 400 else '')
        lines.append('### 📋 原始摘要（节选）')
        lines.append('')
        lines.append(short_summary)
        lines.append('')

    # Check artifact completeness
    if has_deep_read:
        missing = []
        for art in ['traceability_manifest.json', 'research_lens.json', 'direction_board.json']:
            if not os.path.exists(os.path.join(workspace_dir, 'papers', paper_dir_name, art)):
                missing.append(art)
        if missing:
            lines.append(f'> ⚠️ 深度解读产出不完整：缺失 {", ".join(missing)}')
            lines.append('')

    # Deep read link
    if has_deep_read:
        lines.append('### 🔍 深度解读')
        lines.append('')
        lines.append(f'- 📖 [解读报告]({github_deep_read_url})')
        lines.append(f'- 📂 [完整目录]({github_dir_url})')

        db_path = os.path.join(workspace_dir, 'papers', paper_dir_name, 'direction_board.json')
        if os.path.exists(db_path):
            lines.append(f'- 🧭 [研究方向]({GITHUB_BASE}/{paper_dir_name}/direction_board.json)')

        rl_path = os.path.join(workspace_dir, 'papers', paper_dir_name, 'research_lens.json')
        if os.path.exists(rl_path):
            lines.append(f'- 🔬 [问题重构]({GITHUB_BASE}/{paper_dir_name}/research_lens.json)')
    else:
        lines.append('')
        lines.append('> ⏳ 深度解读尚未完成')

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

# Pass OPENAI_API_KEY as the 5th argument
python3 "$TMP_PY" "$INPUT_JSON" "$WORKSPACE_DIR" "$REPORT_FILE" "$DATE"

# ---------- 提交到 GitHub ----------
if [ -f "${SCRIPT_DIR}/git-knowledge-commit.sh" ]; then
  cd "$WORKSPACE_DIR"
  if git diff --cached --quiet -- papers/ 2>/dev/null && git diff --quiet -- papers/ 2>/dev/null; then
    echo "📄 报告已生成，但 papers/ 无变更，跳过 GitHub 提交"
  else
    bash "${SCRIPT_DIR}/git-knowledge-commit.sh" -m "📄 每日论文日报 ${DATE}" 2>&1 || echo "⚠️  git commit 失败"
  fi
fi

echo ""
echo "📊 日报已生成: $REPORT_FILE"
