#!/bin/bash
# run_trending.sh — GitHub Trending 抓取 + 发送，不依赖 cron agent 的 exec
# 被 cron agent 调用：只需要读本脚本输出文件，然后发送

OUTPUT_FILE="/tmp/github-trending-output.txt"
touch "$OUTPUT_FILE"  # ensure it exists even if script fails

cd /home/node/.openclaw/workspace && timeout 30 python3 scripts/github_trending.py > "$OUTPUT_FILE" 2>&1
EXIT_CODE=$?

# If error, write error message
if [ $EXIT_CODE -ne 0 ]; then
    echo "⚠️ GitHub Trending 获取失败（exit code: $EXIT_CODE）" > "$OUTPUT_FILE"
fi

# Always output the content to stdout for the cron agent to capture
cat "$OUTPUT_FILE"
