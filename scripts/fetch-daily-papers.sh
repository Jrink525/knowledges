#!/bin/bash
# ============================================================
# fetch-daily-papers.sh
# 从 Hugging Face Daily Papers API 拉取当日热门论文，
# 用 arXiv API 获取分类标签，按兴趣分类过滤，输出 JSON。
#
# 用法:
#   ./scripts/fetch-daily-papers.sh [date] [max_papers]
#     默认 date=today, max_papers=10
#     示例: ./scripts/fetch-daily-papers.sh 2026-06-17 15
#
# 输出: 过滤后的论文 JSON 数组到 stdout
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${WORKSPACE_DIR}/papers"

# 配置
MAX_PAPERS="${2:-10}"
DATE="${1:-$(date -u '+%Y-%m-%d')}"
DEFAULT_OUTPUT="${WORKSPACE_DIR}/papers/today-hf-papers.json"
OUTPUT_FILE="${3:-$DEFAULT_OUTPUT}"
HF_API="https://huggingface.co/api/daily_papers"
ARXIV_API="https://export.arxiv.org/api/query"
ARXIV_PAGE="https://arxiv.org/abs"

# 目标 arXiv 分类 (含一级和二级)
INTEREST_CATS=(
  "cs.AI"
  "cs.CL"
  "cs.LG"
  "cs.SE"
  "cs.MA"
  "cs.IR"
  "cs.HC"
)

# 补充关键词 —— 当 arXiv 分类不可用时 fallback 使用
INTEREST_KEYWORDS=(
  "agent"
  "agentic"
  "multi-agent"
  "software engineering"
  "llm agent"
  "code agent"
  "autonomous"
  "reinforcement learning"
  "reasoning"
  "large language model"
  "foundation model"
)

# 临时文件
TMP_RAW=$(mktemp)
TMP_ARXIV=$(mktemp)
trap 'rm -f "$TMP_RAW" "$TMP_ARXIV"' EXIT

log() { echo "[$(date '+%H:%M:%S')] $*" >&2; }

# ---------- 1. Fetch from HF ----------
log "Fetching daily papers from HF API (date=$DATE)..."

if ! curl -sf --max-time 30 "$HF_API?date=$DATE" > "$TMP_RAW" 2>/dev/null; then
  log "WARNING: HF API failed, trying without date param..."
  curl -sf --max-time 30 "$HF_API" > "$TMP_RAW" 2>/dev/null || {
    log "ERROR: HF API unreachable"
    echo '[]'
    exit 1
  }
fi

# 解析为 arXiv ID 列表
PAPER_IDS=$(python3 -c "
import json,sys
data = json.load(sys.stdin)
ids = []
for item in data:
    pid = item.get('paper', {}).get('id', '')
    if pid:
        ids.append(pid)
print(' '.join(ids))
" < "$TMP_RAW")

ID_COUNT=$(echo "$PAPER_IDS" | wc -w)
log "Found $ID_COUNT papers in HF daily feed"

if [ "$ID_COUNT" -eq 0 ]; then
  log "ERROR: No papers found"
  echo '[]'
  exit 0
fi

# ---------- 2. Fetch arXiv categories ----------
log "Fetching arXiv categories for $ID_COUNT papers..."
ID_LIST=$(echo "$PAPER_IDS" | tr ' ' ',')

# arXiv API batch query (max ~50 IDs at a time)
curl -sf --max-time 60 "${ARXIV_API}?id_list=${ID_LIST}&max_results=${ID_COUNT}" > "$TMP_ARXIV" 2>/dev/null || {
  log "WARNING: arXiv API failed, falling back to keyword-only filtering"
  echo "" > "$TMP_ARXIV"
}

# ---------- 3. Build parsed JSON ----------
# 将 arXiv xml 解析为 id -> categories 映射
python3 -c "
import json, sys, xml.etree.ElementTree as ET

# Read HF data
with open('$TMP_RAW') as f:
    hf_data = json.load(f)

# Parse arXiv XML
arxiv_cats = {}
arxiv_xml = open('$TMP_ARXIV').read() if open('$TMP_ARXIV').read().strip() else None
if arxiv_xml and arxiv_xml.startswith('<?xml'):
    try:
        ns = {'a': 'http://www.w3.org/2005/Atom', 'ar': 'http://arxiv.org/schemas/atom'}
        root = ET.fromstring(arxiv_xml)
        for entry in root.findall('a:entry', ns):
            link = entry.find('a:id', ns)
            if link is not None:
                # id format: http://arxiv.org/abs/XXXX.XXXXXv1
                arxiv_id = link.text.split('/')[-1].split('v')[0]
            else:
                continue
            cats = []
            for cat in entry.findall('a:category', ns):
                term = cat.get('term', '')
                if term:
                    cats.append(term)
            primary = entry.find('ar:primary_category', ns)
            if primary is not None:
                pterm = primary.get('term', '')
                if pterm and pterm not in cats:
                    cats.insert(0, pterm)
            arxiv_cats[arxiv_id] = cats
    except Exception as e:
        sys.stderr.write(f'arXiv XML parse error: {e}\n')

# Interest categories set
interest_cats = {'cs.ai', 'cs.cl', 'cs.lg', 'cs.se', 'cs.ma', 'cs.ir', 'cs.hc'}
interest_keywords = ['agent', 'agentic', 'multi-agent', 'software engineering',
                     'llm agent', 'code agent', 'autonomous', 'reinforcement learning',
                     'reasoning', 'large language model', 'foundation model',
                     'tool use', 'llm', 'code generation', 'ai engineer']

def matches_interest(title, summary, cats, keywords):
    '''Return a score: higher = better match'''
    score = 0
    title_lower = (title or '').lower()
    summary_lower = (summary or '').lower()
    
    # arXiv category match (strong signal)
    if cats:
        for c in cats:
            if c.lower() in interest_cats:
                score += 3
    
    # Keyword match in title
    for kw in keywords:
        if kw in title_lower:
            score += 2
    
    # Keyword match in summary
    for kw in keywords:
        if kw in summary_lower:
            score += 1
    
    return score

results = []
for item in hf_data:
    paper = item.get('paper', {})
    pid = paper.get('id', '')
    title = paper.get('title', '')
    summary = paper.get('summary', '')
    ai_summary = paper.get('ai_summary', '')
    ai_keywords = paper.get('ai_keywords', [])
    upvotes = item.get('upvotes', 0) or 0
    github = paper.get('githubRepo', '') or ''
    
    if not pid:
        continue
    
    cats = arxiv_cats.get(pid, [])
    # Also use HF ai_keywords for matching
    kw_list = ai_keywords if isinstance(ai_keywords, list) else []
    
    score = matches_interest(title, summary + ' ' + ai_summary, cats, kw_list)
    
    # Minimum score to include
    if score >= 2 or (cats and any(c.lower() in interest_cats for c in cats)):
        results.append({
            'id': pid,
            'arxiv_id': pid,
            'title': title,
            'summary': summary,
            'ai_summary': ai_summary,
            'arxiv_categories': cats,
            'score': score,
            'upvotes': upvotes,
            'arxiv_url': f'https://arxiv.org/abs/{pid}',
            'pdf_url': f'https://arxiv.org/pdf/{pid}',
            'github_url': github,
            'hf_discussion': f'https://huggingface.co/papers/{pid}'
        })

# Sort by score (desc), then upvotes (desc)
results.sort(key=lambda r: (-r['score'], -r['upvotes']))

# Take top N
limited = results[:${MAX_PAPERS}]

# Write output file path
output = open('$OUTPUT_FILE', 'w')
json.dump(limited, output, indent=2, ensure_ascii=False)
output.close()

print(json.dumps(limited, indent=2, ensure_ascii=False))
" 2>&1

log "Saved filtered papers to $OUTPUT_FILE ($(python3 -c "import json; d=json.load(open('$OUTPUT_FILE')); print(len(d))" 2>/dev/null) papers)"
