#!/bin/bash
# Spawned sub-agent: batch translate chapters
# Args: <first_chapter_num> <last_chapter_num>

CH_DIR="/home/node/.openclaw/workspace/tmp_2606.24937_chapters"
OUT_DIR="/home/node/.openclaw/workspace/tmp_2606.24937_translated"
SCRIPT="/home/node/.openclaw/workspace/scripts/translate_chapter.py"

mkdir -p "$OUT_DIR"

for num in $(seq -w "$1" "$2"); do
    f=$(ls "$CH_DIR"/${num}_*.tex 2>/dev/null | head -1)
    if [ -z "$f" ]; then
        echo "No file found for chapter $num"
        continue
    fi
    
    bn=$(basename "$f" .tex)
    out_file="$OUT_DIR/${bn}.md"
    
    echo "=== TRANSLATING: $bn ==="
    PYTHONPATH=/home/node/.openclaw/workspace/pylib python3 "$SCRIPT" \
        --input "$f" --output "$out_file" --model "deepseek-v4-flash"
    echo "=== DONE: $bn ==="
done

echo "=== BATCH COMPLETE ==="
