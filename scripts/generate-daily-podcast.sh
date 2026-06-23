#!/bin/bash
# ============================================================
# generate-daily-podcast.sh
# 将每日论文日报 + 深度解读产物导入 NotebookLM，
# 生成中文播客音频，并下载到 papers/ 目录。
#
# 用法:
#   ./scripts/generate-daily-podcast.sh [date]
#     默认 date=today (YYYY-MM-DD)
#
# 依赖:
#   - notebooklm-py (通过 PYTHONPATH=/tmp/pip-lib)
#   - NOTEBOOKLM_HOME 指向认证文件目录
#   - papers/today-hf-papers.json 存在
#   - scripts/add_sources_to_notebooklm.py 存在（Python 辅助脚本）
# ============================================================
set -uo pipefail
# ^ 故意去掉 -e：让脚本能在某步失败后继续

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
DATE="${1:-$(date -u '+%Y-%m-%d')}"
REPORT_FILE="${WORKSPACE_DIR}/papers/daily-report-${DATE}.md"
PAPER_JSON="${WORKSPACE_DIR}/papers/today-hf-papers.json"
ADD_SRC_SCRIPT="${SCRIPT_DIR}/add_sources_to_notebooklm.py"

# notebooklm-py 配置
export NOTEBOOKLM_HOME="${NOTEBOOKLM_HOME:-/tmp/notebooklm}"
PYTHONPATH="/tmp/pip-lib:${PYTHONPATH:-}"

# ---------- 前置检查 ----------
if [ ! -d "$NOTEBOOKLM_HOME" ]; then
  echo "❌ NOTEBOOKLM_HOME 不存在: $NOTEBOOKLM_HOME"
  exit 1
fi

if [ ! -f "$PAPER_JSON" ]; then
  echo "❌ 论文 JSON 不存在: $PAPER_JSON"
  exit 1
fi

# ---------- 强制设置中文语言 ----------
echo ""
echo "🌐 设置 NotebookLM 语言为中文..."
python3 -m notebooklm language set zh_Hans 2>&1 | tail -1

PAPER_COUNT=$(python3 -c "import json; print(len(json.load(open('$PAPER_JSON'))))" 2>/dev/null || echo "0")
echo ""
echo "📋 共 $PAPER_COUNT 篇论文"

# ---------- 创建 NotebookLM notebook ----------
NOTEBOOK_TITLE="📄 每日论文播客 ${DATE}"
echo ""
echo "📓 创建 NotebookLM notebook: ${NOTEBOOK_TITLE}"

NOTEBOOK_JSON=$(python3 -m notebooklm create "$NOTEBOOK_TITLE" --use --json 2>&1)
NOTEBOOK_ID=$(echo "$NOTEBOOK_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['notebook']['id'])" 2>/dev/null || echo "")

if [ -z "$NOTEBOOK_ID" ]; then
  echo "   ⚠️ 创建失败，可能已存在同名 notebook"
  echo "   $NOTEBOOK_JSON" | head -3
  # 尝试列出已有的同名 notebook
  NOTEBOOK_ID=$(python3 -m notebooklm list 2>/dev/null | grep "$NOTEBOOK_TITLE" | head -1 | awk '{print $2}')
  if [ -z "$NOTEBOOK_ID" ]; then
    echo "❌ 无法创建或找到 notebook"
    exit 1
  fi
  echo "   使用已有: $NOTEBOOK_ID"
else
  echo "   ID: $NOTEBOOK_ID"
fi

# ---------- 添加论文 source ----------
echo ""
echo "📝 添加论文 source..."

if [ -f "$ADD_SRC_SCRIPT" ]; then
  python3 "$ADD_SRC_SCRIPT" "$WORKSPACE_DIR" "$NOTEBOOK_ID" 2>&1
  SRC_EXIT=$?
  if [ $SRC_EXIT -ne 0 ]; then
    echo ""
    echo "⚠️  source 添加部分失败 (exit=$SRC_EXIT)"
    echo "   继续尝试生成播客..."
  fi
else
  # 回退：内联添加（兼容旧版）
  echo "⚠️  $ADD_SRC_SCRIPT 不存在，使用内联方式"
  for i in $(seq 1 $PAPER_COUNT); do
    TITLE=$(python3 -c "import json; print(json.load(open('$PAPER_JSON'))[$((i-1))].get('title','Unknown')[:50])" 2>/dev/null)
    echo "   [$i/$PAPER_COUNT] $TITLE..."
    python3 -m notebooklm source add --type text --notebook "$NOTEBOOK_ID" --title "$TITLE" -- "$PAPER_JSON" 2>/dev/null && echo "   ✅" || echo "   ⚠️"
  done
fi

# ---------- 生成播客音频 ----------
echo ""
echo "🎙️ 生成中文播客音频..."
echo "   格式: deep-dive | 语言: zh_Hans | ~15分钟"

AUDIO_OUTPUT=$(python3 -m notebooklm generate audio \
  --language zh_Hans \
  --format deep-dive \
  --length long \
  --wait \
  --timeout 900 \
  "这是一个每日论文播客，主题是今日最新人工智能研究论文。请用中文深入探讨每篇论文：解决了什么问题、用了什么方法、有什么创新点、对领域的意义。以对话形式呈现，风格轻松自然。最后给出整体思考和各论文间的联系。" 2>&1)

AUDIO_EXIT=$?
echo ""
echo "$AUDIO_OUTPUT" | tail -5

# 提取 artifact ID
ARTIFACT_ID=$(echo "$AUDIO_OUTPUT" | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1)

if [ $AUDIO_EXIT -ne 0 ] || [ -z "$ARTIFACT_ID" ]; then
  echo ""
  echo "⚠️  generate 输出没有 artifact ID，尝试从 artifact list 获取最新..."
  ARTIFACT_ID=$(python3 -m notebooklm artifact list --json -n "$NOTEBOOK_ID" 2>/dev/null | python3 -c "
import json,sys
try:
    data=json.load(sys.stdin)
    if data:
        print(data[0]['id'])
except: pass
" 2>/dev/null)
fi

# ---------- 下载音频 ----------
echo ""
echo "⬇️ 下载音频文件..."
AUDIO_PATH="${WORKSPACE_DIR}/papers/podcast-${DATE}.mp3"

if [ -n "$ARTIFACT_ID" ]; then
  echo "   下载 artifact: $ARTIFACT_ID"
  python3 -m notebooklm download audio \
    -n "$NOTEBOOK_ID" \
    -a "$ARTIFACT_ID" \
    "$AUDIO_PATH" 2>&1
  
  if [ -f "$AUDIO_PATH" ] && [ -s "$AUDIO_PATH" ]; then
    FILE_SIZE=$(stat -c%s "$AUDIO_PATH" 2>/dev/null || stat -f%z "$AUDIO_PATH" 2>/dev/null)
    echo "✅ 音频已下载: ${FILE_SIZE} bytes"
  else
    echo "⚠️  音频下载失败，尝试 --latest 重新下载..."
    python3 -m notebooklm download audio -n "$NOTEBOOK_ID" "$AUDIO_PATH" 2>&1
    if [ -f "$AUDIO_PATH" ] && [ -s "$AUDIO_PATH" ]; then
      FILE_SIZE=$(stat -c%s "$AUDIO_PATH" 2>/dev/null || stat -f%z "$AUDIO_PATH" 2>/dev/null)
      echo "✅ 音频已下载: ${FILE_SIZE} bytes"
    else
      echo "❌ 音频下载失败，需手动操作"
    fi
  fi
else
  echo "⚠️  未找到 artifact ID，尝试最新下载..."
  python3 -m notebooklm download audio -n "$NOTEBOOK_ID" "$AUDIO_PATH" 2>&1
  if [ -f "$AUDIO_PATH" ] && [ -s "$AUDIO_PATH" ]; then
    FILE_SIZE=$(stat -c%s "$AUDIO_PATH" 2>/dev/null || stat -f%z "$AUDIO_PATH" 2>/dev/null)
    echo "✅ 音频已下载: ${FILE_SIZE} bytes"
  else
    echo "❌ 音频下载失败，需手动操作"
  fi
fi

# ---------- 完成 ----------
echo ""
echo "🎉 播客生成流程完成!"
echo "   Notebook: ${NOTEBOOK_ID}"
if [ -f "$AUDIO_PATH" ] && [ -s "$AUDIO_PATH" ]; then
  echo "   音频: ${AUDIO_PATH}"
fi
