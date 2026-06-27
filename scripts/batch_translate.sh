#!/bin/bash
# Batch translate chapters using Python script
# Usage: batch_translate.sh <first_ch> <last_ch>

CH_DIR="$HOME/.openclaw/workspace/tmp_2606.24937_chapters"
OUT_DIR="$HOME/.openclaw/workspace/tmp_2606.24937_translated"
PYTHONPATH="$HOME/.openclaw/workspace/pylib"

mkdir -p "$OUT_DIR"

for f in "$CH_DIR"/*.tex; do
    basename=$(basename "$f" .tex)
    out_file="$OUT_DIR/${basename}.md"
    
    # Skip already translated files
    if [ -f "$out_file" ] && [ -s "$out_file" ]; then
        echo "SKIP: $basename (already exists)"
        continue
    fi
    
    echo "TRANSLATING: $basename..."
    PYTHONPATH=$PYTHONPATH python3 "$HOME/.openclaw/workspace/scripts/translate_chapter.py" \
        --input "$f" \
        --output "$out_file" \
        --model "deepseek-v4-flash" 2>&1
    echo "DONE: $basename"
done

echo "ALL DONE for batch"
