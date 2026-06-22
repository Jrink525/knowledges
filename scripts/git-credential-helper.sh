#!/bin/sh
# ============================================================
# Git 凭据助手 + 快捷推送工具
# ============================================================
#
# 作为 credential.helper（git push 时自动调用）:
#   git config credential.helper "/path/to/scripts/git-credential-helper.sh"
#
# 直接推送（快捷用法）:
#   bash scripts/git-credential-helper.sh push "提交信息"
#   bash scripts/git-credential-helper.sh push   # 用默认信息
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

case "$1" in
    get)
        # Git credential helper mode (called by git internally)
        TOKEN=$(grep -A3 Jrink525 /home/node/.openclaw/gh-config/hosts.yml | grep oauth_token | head -1 | awk '{print $2}')
        echo "username=Jrink525"
        echo "password=${TOKEN}"
        ;;
    push)
        # Direct push mode: add knowledge dirs + commit + push
        MSG="${2:-知识库更新 $(date '+%Y-%m-%d %H:%M')}"
        cd "$WORKSPACE_DIR"

        # Check if git-knowledge-commit.sh exists (preferred)
        if [ -f "${SCRIPT_DIR}/git-knowledge-commit.sh" ]; then
            exec bash "${SCRIPT_DIR}/git-knowledge-commit.sh" -m "$MSG"
        fi

        # Fallback: minimal add+commit+push
        echo "📦 暂存变更..."
        git add ai-tools/ business/ database/ infrastructure/ java/ life/ papers/ programming/ prompt-engineering/ scripts/ sre/ startup/ spring/ vulnerability-research/ image/ 2>/dev/null || true

        if git diff --cached --quiet; then
            echo "⚠️  没有变更需要提交"
            exit 0
        fi

        git commit -m "$MSG"
        echo "🚀 推送到 origin master..."
        git push origin master
        echo "✅ 完成"
        ;;
    *)
        echo "用法:"
        echo "  作为 Git 凭据助手（由 git 自动调用）:"
        echo "    git config credential.helper \"$0\""
        echo ""
        echo "  直接推送:"
        echo "    bash $0 push [\"提交信息\"]"
        exit 1
        ;;
esac
