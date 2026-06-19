#!/bin/bash
# git-knowledge-commit — 提交知识文件目录（不含 workspace 基础设施）
#
# 用法: ./scripts/git-knowledge-commit.sh [-m "message"]
#
# 遗留问题（手动处理）:
#   - git mv / git rm 需要手动执行
#
# 自动行为:
#   - commit 后自动 push origin master
#
# 历史教训:
#   2026-05-15: 用了 git add -A 把整个 workspace 都提交了
#   2026-05-15: git rm --cached 后接 git add -A 又把删掉的文件加回来了
#   永远不要用 git add -A / git add . ，只显式指定具体目录

set -euo pipefail

msg=""
while getopts "m:" opt; do
  case $opt in
    m) msg="$OPTARG" ;;
    *) echo "用法: $0 -m \"提交信息\""; exit 1 ;;
  esac
done

if [ -z "$msg" ]; then
  echo "❌ 必须指定 -m 提交信息"
  exit 1
fi

cd "$(git rev-parse --show-toplevel)"

# 知识文件目录（只包含磁盘上实际存在的，不含 workspace 基础设施）
ALL_KNOWN_DIRS=(
  ai-tools
  business
  database
  image
  infrastructure
  java
  life
  papers
  programming
  prompt-engineering
  sre
  startup
  spring
  vulnerability-research
)

# 只取实际存在的目录
KNOWLEDGE_DIRS=()
for d in "${ALL_KNOWN_DIRS[@]}"; do
  [ -d "$d" ] && KNOWLEDGE_DIRS+=("$d")
done

# 拼 exclude 模式
EXCLUDE_PATTERNS=()
for d in "${ALL_KNOWN_DIRS[@]}"; do
  EXCLUDE_PATTERNS+=(":!$d/")
done

# 检查 workspace 基础设施文件是否有变更
outside_files=$(git diff --name-only HEAD -- "${EXCLUDE_PATTERNS[@]}" 2>/dev/null)
if [ -n "$outside_files" ]; then
  echo "⚠️ 以下知识目录外的文件有未提交变更:"
  echo "$outside_files"
  echo
fi

# 只暂存知识文件目录内实际存在的目录的变更
git add "${KNOWLEDGE_DIRS[@]}" 2>/dev/null || true

# 检查有没有东西要提交
if git diff --cached --quiet; then
  echo "⚠️  知识文件目录内没有变更，跳过提交"
  exit 0
fi

echo "📦 暂存的变更："
for dir in "${KNOWLEDGE_DIRS[@]}"; do
  count=$(git diff --cached --name-only -- "$dir" 2>/dev/null | wc -l 2>/dev/null)
  if [ "${count:-0}" -gt 0 ] 2>/dev/null; then
    git diff --cached --stat -- "$dir" 2>/dev/null || true
  fi
done

echo
git commit -m "$msg"

echo "🚀 正在 push origin master..."
git push origin master 2>&1 || echo "⚠️  push 失败"

echo "✅ 全部完成"
