#!/bin/bash
# scripts/cron-test.sh
# 手动测试 _organize.py 是否正常工作

cd /home/node/.openclaw/workspace
python3 scripts/_organize.py 2>&1
exit $?
