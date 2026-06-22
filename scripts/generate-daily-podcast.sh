#!/bin/bash
# ============================================================
# generate-daily-podcast.sh
# 将每日论文日报 + 深度解读产物导入 NotebookLM，
# 生成中文播客音频，并发送到微信。
#
# 依赖:
#   - notebooklm-py (本脚本内置 /tmp/pip-lib 的路径)
#   - NOTEBOOKLM_HOME 指向认证文件目录
#   - 每日论文日报已生成 (papers/daily-report-{DATE}.md)
#   - 深度解读产物已存在 (papers/{slug}-{arxiv_id}/report.md)
#
# 用法:
#   ./scripts/generate-daily-podcast.sh [date]
#     默认 date=today (YYYY-MM-DD)
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

DATE="${1:-$(date -u '+%Y-%m-%d')}"
REPORT_FILE="${WORKSPACE_DIR}/papers/daily-report-${DATE}.md"
PAPER_JSON="${WORKSPACE_DIR}/papers/today-hf-papers.json"

# notebooklm-py 配置
export NOTEBOOKLM_HOME="${NOTEBOOKLM_HOME:-/tmp/notebooklm}"
PYTHONPATH="/tmp/pip-lib:${PYTHONPATH:-}"

# ---------- 检查依赖 ----------
if [ ! -d "$NOTEBOOKLM_HOME" ]; then
  echo "❌ NOTEBOOKLM_HOME 不存在: $NOTEBOOKLM_HOME"
  echo "   请先设置认证文件"
  exit 1
fi

if [ ! -f "$REPORT_FILE" ]; then
  echo "❌ 日报文件不存在: $REPORT_FILE"
  echo "   请先生成每日论文日报"
  exit 1
fi

if [ ! -f "$PAPER_JSON" ]; then
  echo "❌ 论文 JSON 不存在: $PAPER_JSON"
  echo "   请先运行 fetch-daily-papers.sh"
  exit 1
fi

# notebooklm alias
nb() {
  PYTHONPATH="/tmp/pip-lib:${PYTHONPATH:-}" python3 -m notebooklm "$@"
}

# ---------- 工具函数 ----------
slugify() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g; s/^-//; s/-$//'
}

# ---------- 读取论文列表 ----------
echo ""
echo "📋 读取论文列表..."
PAPERS=$(python3 -c "
import json
with open('$PAPER_JSON') as f:
    papers = json.load(f)
print(json.dumps(papers))
")

PAPER_COUNT=$(python3 -c "
import json
with open('$PAPER_JSON') as f:
    papers = json.load(f)
print(len(papers))
")

echo "   共 $PAPER_COUNT 篇论文"

# ---------- 清理上次生成的测试 notebook ----------
# （脚本一开始会创建新的，不需要清理）

# ---------- 创建 NotebookLM notebook ----------
NOTEBOOK_TITLE="📄 每日论文播客 ${DATE}"
echo ""
echo "📓 创建 NotebookLM notebook: ${NOTEBOOK_TITLE}"

NOTEBOOK_JSON=$(nb create "$NOTEBOOK_TITLE" --use --json 2>&1)
NOTEBOOK_ID=$(echo "$NOTEBOOK_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin)['notebook']['id'])")
echo "   Notebook ID: ${NOTEBOOK_ID}"

# ---------- 为每篇论文添加 source ----------
echo ""
echo "📝 添加论文 source..."

python3 -c "
import json, os, re, sys

workspace = '$WORKSPACE_DIR'
notebook_id = '$NOTEBOOK_ID'

with open('$PAPER_JSON') as f:
    papers = json.load(f)

def slugify(title):
    s = title.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = s.strip('-')
    return s

results = {}
for i, p in enumerate(papers, 1):
    title = p.get('title', 'Unknown')
    arxiv_id = p.get('arxiv_id', '')
    summary = p.get('summary', '')
    ai_summary = p.get('ai_summary', '')
    arxiv_url = p.get('arxiv_url', '')
    cats = ', '.join(p.get('arxiv_categories', []))
    
    paper_slug = slugify(title)
    paper_dir = os.path.join(workspace, 'papers', f'{paper_slug}-{arxiv_id}')
    
    # 构建 source 内容：摘要 + 深度解读（如果有）
    source_parts = [f'# {title}', '']
    source_parts.append(f'## 基本信息')
    source_parts.append(f'- 链接: {arxiv_url}')
    if cats:
        source_parts.append(f'- 分类: {cats}')
    source_parts.append('')
    source_parts.append(f'## 摘要')
    source_parts.append(summary[:2000] if summary else '')
    source_parts.append('')
    
    if ai_summary:
        source_parts.append(f'## AI 摘要')
        source_parts.append(ai_summary[:1000])
        source_parts.append('')
    
    # 检查深度解读报告
    report_path = os.path.join(paper_dir, 'report.md')
    if os.path.exists(report_path):
        with open(report_path) as rf:
            report_content = rf.read()
        # 提取关键章节（最多 4000 字符）
        source_parts.append(f'## 深度解读')
        source_parts.append(report_content[:4000])
        source_parts.append('')
    
    # 检查研究方向
    db_path = os.path.join(paper_dir, 'direction_board.json')
    if os.path.exists(db_path):
        with open(db_path) as df:
            db_data = json.load(df)
        seeds = db_data.get('ranking', db_data.get('results', []))[:3]
        if seeds:
            source_parts.append(f'## 研究方向建议')
            for s in seeds:
                name = s.get('name', s.get('title', ''))
                desc = s.get('description', s.get('rationale', ''))[:200]
                if name:
                    source_parts.append(f'- {name}: {desc}')
            source_parts.append('')
    
    # 检查问题重构
    rl_path = os.path.join(paper_dir, 'research_lens.json')
    if os.path.exists(rl_path):
        with open(rl_path) as rf:
            rl_data = json.load(rf)
        problem = rl_data.get('reconstructed_problem', '')
        if problem:
            source_parts.append(f'## 核心问题')
            source_parts.append(problem[:1000])
            source_parts.append('')
    
    full_text = '\n'.join(source_parts)
    results[str(i)] = {
        'title': p['title'][:80],
        'text': full_text
    }
    
    print(f'   {i}/{len(papers)}: {p[\"title\"][:60]}...')

# 输出为 JSON，供后续批量添加
print('---SOURCE_DATA---')
print(json.dumps(results, ensure_ascii=False))
" 2>&1

# 提取 source 数据（位于 ---SOURCE_DATA--- 之后）
SOURCE_DATA=$(python3 -c "
import json, sys
with open('$PAPER_JSON') as f:
    papers = json.load(f)
print(len(papers))
")

# 用 Python 批量添加 sources
python3 -c "
import subprocess, json, os, sys

workspace = '$WORKSPACE_DIR'
notebook_id = '$NOTEBOOK_ID'

with open('$PAPER_JSON') as f:
    papers = json.load(f)

def slugify(title):
    import re
    s = title.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = s.strip('-')
    return s

env = os.environ.copy()
env['NOTEBOOKLM_HOME'] = '$NOTEBOOKLM_HOME'

for i, p in enumerate(papers, 1):
    title = p.get('title', 'Unknown')
    arxiv_id = p.get('arxiv_id', '')
    summary = p.get('summary', '')
    ai_summary = p.get('ai_summary', '')
    arxiv_url = p.get('arxiv_url', '')
    cats = ', '.join(p.get('arxiv_categories', []))
    
    paper_slug = slugify(title)
    paper_dir = os.path.join(workspace, 'papers', f'{paper_slug}-{arxiv_id}')
    
    # 构建 source 内容
    source_parts = [f'# {title}', '']
    source_parts.append('## 基本信息')
    source_parts.append(f'- 链接: {arxiv_url}')
    if cats:
        source_parts.append(f'- 分类: {cats}')
    source_parts.append('')
    source_parts.append('## 摘要')
    source_parts.append(summary[:2000] if summary else '')
    source_parts.append('')
    
    if ai_summary:
        source_parts.append('## AI 摘要')
        source_parts.append(ai_summary[:1000])
        source_parts.append('')
    
    # 检查深度解读报告
    report_path = os.path.join(paper_dir, 'report.md')
    if os.path.exists(report_path):
        with open(report_path) as rf:
            report_content = rf.read()
        source_parts.append('## 深度解读')
        source_parts.append(report_content[:4000])
        source_parts.append('')
    
    # 研究方向
    db_path = os.path.join(paper_dir, 'direction_board.json')
    if os.path.exists(db_path):
        with open(db_path) as df:
            db_data = json.load(df)
        seeds = db_data.get('ranking', db_data.get('results', []))[:3]
        if seeds:
            source_parts.append('## 研究方向建议')
            for s in seeds:
                name = s.get('name', s.get('title', ''))
                desc = s.get('description', s.get('rationale', ''))[:200]
                if name:
                    source_parts.append(f'- {name}: {desc}')
            source_parts.append('')
    
    # 问题重构
    rl_path = os.path.join(paper_dir, 'research_lens.json')
    if os.path.exists(rl_path):
        with open(rl_path) as rf:
            rl_data = json.load(rf)
        problem = rl_data.get('reconstructed_problem', '')
        if problem:
            source_parts.append('## 核心问题')
            source_parts.append(problem[:1000])
            source_parts.append('')
    
    full_text = '\n'.join(source_parts)
    
    print(f'📝 [{i}/{len(papers)}] 添加: {title[:50]}...')
    
    result = subprocess.run(
        ['python3', '-m', 'notebooklm', 'source', 'add',
         '--type', 'text',
         '--title', title[:80],
         '--json',
         full_text],
        capture_output=True, text=True, env=env,
        cwd='/tmp'
    )
    
    if result.returncode == 0:
        try:
            src = json.loads(result.stdout)
            print(f'   ✅ Source ID: {src[\"source\"][\"id\"]}')
        except:
            print(f'   ⚠️  响应: {result.stdout[:100]}')
    else:
        print(f'   ❌ 失败: {result.stderr[:200]}')
    
print()
print('✅ 所有 source 已添加完毕')
" 2>&1

# ---------- 生成播客音频 ----------
echo ""
echo "🎙️ 生成中文播客音频..."
echo "   语言: 中文简体"
echo "   格式: deep-dive（深度探讨）"
echo "   时长: long（~15分钟）"

# 设置 prompt
PROMPT="这是一个每日论文播客，主题是今天最新的人工智能研究论文。请用中文深入探讨每篇论文：解决了什么问题、用了什么方法、有什么创新点、对 AI 领域的意义。以对话形式呈现，风格轻松自然，适合通勤时听。最后给出整体思考和各论文之间的联系。"

AUDIO_JSON=$(nb generate audio \
  --language zh_Hans \
  --format deep-dive \
  --length long \
  --wait \
  --timeout 900 \
  --json \
  "$PROMPT" 2>&1)

echo ""
echo "$AUDIO_JSON"

# ---------- 下载音频 ----------
echo ""
echo "⬇️ 下载音频文件..."

AUDIO_PATH="${WORKSPACE_DIR}/papers/podcast-${DATE}.mp3"
rm -f "$AUDIO_PATH"

DOWNLOAD_RESULT=$(nb download audio "$AUDIO_PATH" --force 2>&1)
echo "$DOWNLOAD_RESULT"

if [ -f "$AUDIO_PATH" ]; then
  FILE_SIZE=$(stat -c%s "$AUDIO_PATH" 2>/dev/null || stat -f%z "$AUDIO_PATH" 2>/dev/null)
  echo "✅ 音频已下载: $AUDIO_PATH (${FILE_SIZE} bytes)"
else
  echo "⚠️  音频文件未找到，尝试搜索..."
  # 尝试查找下载的文件
  FOUND=$(find "${WORKSPACE_DIR}/papers/" -name "*.mp3" -newer "$REPORT_FILE" 2>/dev/null | head -1)
  if [ -n "$FOUND" ]; then
    mv "$FOUND" "$AUDIO_PATH"
    echo "✅ 已移动音频: $AUDIO_PATH"
  else
    echo "❌ 音频下载失败，可能需要手动下载"
  fi
fi

# ---------- 发送到微信 ----------
echo ""
echo "📱 发送到微信..."

if [ -f "$AUDIO_PATH" ]; then
  # 获取日期显示
  DATE_DISPLAY=$(date -d "${DATE}" '+%m月%d日' 2>/dev/null || echo "${DATE}")
  
  MESSAGE="🎙️ 每日论文播报 ${DATE_DISPLAY}
  
共 ${PAPER_COUNT} 篇论文深度解读，15 分钟中文播客。
通勤路上听一听，了解今日 AI 前沿动态。

#NotebookLM #每日论文"
  
  echo "   发送音频 + 文字说明"
  echo ""
  echo "📤 音频路径: $AUDIO_PATH"
  echo "📤 消息内容: $MESSAGE"
else
  echo "⚠️  音频文件不存在，跳过发送"
fi

# ---------- 清理 ----------
# 保留 notebook 以便将来参考，不清除

echo ""
echo "🎉 播客生成流程完成!"
echo "   Notebook ID: ${NOTEBOOK_ID}"
echo "   日期: ${DATE}"
if [ -f "$AUDIO_PATH" ]; then
  echo "   音频: ${AUDIO_PATH}"
fi
