#!/bin/bash
# ============================================================
# fetch-daily-papers.sh
# 从 Hugging Face Daily Papers API 拉取论文（过去 ~24h），
# 用 arXiv API 获取分类标签，按兴趣分类过滤，去重，输出 JSON。
#
# 用法:
#   ./scripts/fetch-daily-papers.sh [date] [max_papers]
#     默认 date=today, max_papers=10
#
# 去重: 每次运行记录已处理的 paper IDs 到 papers/.seen-papers.json，
#       下次跳过这些 ID（滚动 24h 窗口）。
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

# 配置
MAX_PAPERS="${2:-10}"
DATE="${1:-$(date -u -d '-1 day' '+%Y-%m-%d')}"
OUTPUT_FILE="${WORKSPACE_DIR}/papers/today-hf-papers.json"
STATE_FILE="${WORKSPACE_DIR}/papers/.seen-papers.json"
HF_API="https://huggingface.co/api/daily_papers"
ARXIV_API="https://export.arxiv.org/api/query"

# 临时文件
TMP_RAW=$(mktemp)
TMP_ARXIV=$(mktemp)
TMP_PY=$(mktemp /tmp/fetch-papers.XXXXXX.py)
trap 'rm -f "$TMP_RAW" "$TMP_ARXIV" "$TMP_PY"' EXIT

log() { echo "[$(date '+%H:%M:%S')] $*" >&2; }

# ---------- 1. Fetch from HF ----------
log "Fetching daily papers from HF API (date=$DATE)..."
if ! curl -sf --max-time 30 "$HF_API?date=$DATE" > "$TMP_RAW" 2>/dev/null; then
  log "WARNING: HF API failed with date, trying without..."
  curl -sf --max-time 30 "$HF_API" > "$TMP_RAW" 2>/dev/null || {
    log "ERROR: HF API unreachable"
    echo '[]'
    exit 1
  }
fi

# Parse arXiv IDs
PAPER_IDS=$(python3 -c "
import json,sys
data = json.load(sys.stdin)
ids = [item.get('paper',{}).get('id','') for item in data if item.get('paper',{}).get('id','')]
print(' '.join(ids))
" < "$TMP_RAW")

ID_COUNT=$(echo "$PAPER_IDS" | wc -w)
log "Found $ID_COUNT papers in HF daily feed"
[ "$ID_COUNT" -eq 0 ] && { echo '[]'; exit 0; }

# ---------- 2. Fetch arXiv categories ----------
log "Fetching arXiv categories for $ID_COUNT papers..."
ID_LIST=$(echo "$PAPER_IDS" | tr ' ' ',')
curl -sf --max-time 60 "${ARXIV_API}?id_list=${ID_LIST}&max_results=${ID_COUNT}" > "$TMP_ARXIV" 2>/dev/null || {
  log "WARNING: arXiv API failed, falling back to keyword-only filtering"
  echo "" > "$TMP_ARXIV"
}

# ---------- 3. Build Python filter + dedup script ----------
cat > "$TMP_PY" << 'PYEOF'
import json, os, sys, xml.etree.ElementTree as ET

# Args from shell
hf_json_path = sys.argv[1]
arxiv_xml_path = sys.argv[2]
state_file_path = sys.argv[3]
output_path = sys.argv[4]
max_papers = int(sys.argv[5])
run_date = sys.argv[6]

# Load seen IDs
seen_ids = set()
if os.path.exists(state_file_path):
    try:
        with open(state_file_path) as f:
            seen_ids = set(json.load(f).get('ids', []))
    except Exception:
        seen_ids = set()

# Read HF data
with open(hf_json_path) as f:
    hf_data = json.load(f)

# Parse arXiv XML
arxiv_cats = {}
arxiv_raw = open(arxiv_xml_path).read() if os.path.getsize(arxiv_xml_path) > 0 else None
if arxiv_raw and arxiv_raw.strip().startswith('<?xml'):
    try:
        ns = {'a': 'http://www.w3.org/2005/Atom', 'ar': 'http://arxiv.org/schemas/atom'}
        root = ET.fromstring(arxiv_raw)
        for entry in root.findall('a:entry', ns):
            link = entry.find('a:id', ns)
            if link is None:
                continue
            arxiv_id = link.text.split('/')[-1].split('v')[0]
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

# Interest categories & keywords
interest_cats = {'cs.ai', 'cs.cl', 'cs.lg', 'cs.se', 'cs.ma', 'cs.ir', 'cs.hc'}
interest_keywords = [
    'agent', 'agentic', 'multi-agent', 'software engineering',
    'llm agent', 'code agent', 'autonomous', 'reinforcement learning',
    'reasoning', 'large language model', 'foundation model',
    'tool use', 'llm', 'code generation', 'ai engineer',
]

def matches_interest(title, summary, cats, keywords):
    score = 0
    title_lower = (title or '').lower()
    summary_lower = (summary or '').lower()
    for c in cats:
        if c.lower() in interest_cats:
            score += 3
    for kw in keywords:
        if kw in title_lower:
            score += 2
    for kw in keywords:
        if kw in summary_lower:
            score += 1
    return score

results = []
new_ids = []

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
    # Skip papers we already reported on
    if pid in seen_ids:
        continue
    
    cats = arxiv_cats.get(pid, [])
    kw_list = ai_keywords if isinstance(ai_keywords, list) else []
    score = matches_interest(title, summary + ' ' + ai_summary, cats, kw_list)
    
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
        new_ids.append(pid)

# Sort & limit
results.sort(key=lambda r: (-r['score'], -r['upvotes']))
limited = results[:max_papers]

# Extract only the actually-outputted paper IDs (top N)
outputted_ids = [p['id'] for p in limited]

# Save state (rolling 24h window: only block these IDs next run)
with open(state_file_path, 'w') as f:
    json.dump({'ids': outputted_ids, 'updated': run_date}, f)

# Write output
with open(output_path, 'w') as f:
    json.dump(limited, f, indent=2, ensure_ascii=False)

print(json.dumps(limited, indent=2, ensure_ascii=False))
PYEOF

python3 "$TMP_PY" "$TMP_RAW" "$TMP_ARXIV" "$STATE_FILE" "$OUTPUT_FILE" "$MAX_PAPERS" "$DATE"

COUNT=$(python3 -c "import json; print(len(json.load(open(\"$OUTPUT_FILE\"))) or 0)" 2>/dev/null || echo 0)
log "Done: $COUNT papers saved to $OUTPUT_FILE"
