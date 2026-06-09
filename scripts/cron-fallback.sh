#!/bin/bash
# scripts/cron-fallback.sh
# 兜底定时任务：每 5 分钟检查一次，到 22:00 UTC (06:00 北京时间) 运行 _organize.py
# 配合 OpenClaw cron scheduler 使用，防止调度器因 restart 丢失定时

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="${WORKSPACE}/scripts/organize-cron.log"
JOBS_FILE="/home/node/.openclaw/cron/jobs.json"

# 只记录真正跑的时候的日志，不浪费磁盘
last_run_date=""

while true; do
    current_hour=$(date -u +%H)
    current_min=$(date -u +%M)
    current_date=$(date -u +%Y-%m-%d)

    # 22:00 UTC = 06:00 CST (北京时间)
    if [ "$current_hour" = "22" ] && [ "$current_min" = "00" ] && [ "$last_run_date" != "$current_date" ]; then
        echo "[$(date -u '+%Y-%m-%d %H:%M UTC')] ⏰ 触发 _organize.py..." >> "$LOG_FILE"
        
        cd "$WORKSPACE"
        python3 scripts/_organize.py >> "$LOG_FILE" 2>&1
        
        exit_code=$?
        if [ $exit_code -eq 0 ]; then
            echo "[$(date -u '+%Y-%m-%d %H:%M UTC')] ✅ _organize.py 完成" >> "$LOG_FILE"
        else
            echo "[$(date -u '+%Y-%m-%d %H:%M UTC')] ❌ _organize.py 失败 (exit=$exit_code)" >> "$LOG_FILE"
        fi
        
        last_run_date="$current_date"
    fi

    sleep 60  # 每分钟检查一次，精确到分钟
done
