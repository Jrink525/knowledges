#!/usr/bin/env bash
# Merge all translated files into one complete bilingual document
set -e

WORKDIR="/home/node/.openclaw/workspace"
SRC="$WORKDIR/tmp_2606.24937_translated"
OUTPUT="$WORKDIR/papers/the-hitchhikers-guide-to-agentic-ai/complete_bilingual_guide.md"

# Header
cat > "$OUTPUT" << 'HEADER'
# The Hitchhiker's Guide to Agentic AI
# 《Agentic AI 漫游指南》

**From Foundations to Systems**
**从基础到系统**

**Author / 作者**: Haggai Roitman
**Year / 年份**: 2026
**Version / 版本**: 1.2.2

---

## 翻译说明 / Translation Notes

This document is a complete bilingual (English + Chinese) translation of *The Hitchhiker's Guide to Agentic AI: From Foundations to Systems* by Haggai Roitman.

本文档是 *The Hitchhiker's Guide to Agentic AI: From Foundations to Systems*（Haggai Roitman 著）的完整中英双语翻译版。

- **Format / 格式**: Original English text followed by Chinese translation in each section.
  每个章节中，英文原文后紧跟中文译文。
- **LaTeX formulas / 公式**: Preserved as-is (`$$` / `$`).
  LaTeX 公式原样保留。
- **Code blocks / 代码块**: Preserved as-is.
  代码块原样保留。
- **Tables / 表格**: Headers translated, data preserved.
  表头已翻译，数据不变。
- **Chapter numbers / 章节编号**: Retained from the original 29-chapter structure.
  保留原书 29 章章节编号。

---

HEADER

# Process files in order: 00_preamble, then 01-29
for f in \
  "00_Preamble.md" \
  "01_LLM_Architecture_and_Optimization_Methods.md" \
  "02_Systems_Foundations_for_LLMs.md" \
  "03_Introduction_to_Reinforcement_Learning.md" \
  "04_RL_Foundations_for_Language_Models.md" \
  "05_PPO_Proximal_Policy_Optimization.md" \
  "06_DPO_Direct_Preference_Optimization.md" \
  "07_GRPO_Group_Relative_Policy_Optimization.md" \
  "08_Preference_Optimization_Variants.md" \
  "09_Reward_Model_Training.md" \
  "10_SFT_Best_Practices_and_Techniques.md" \
  "11_System_Architecture_Infrastructure_at_Scale.md" \
  "12_LLM_Agentic_Training.md" \
  "13_RL_for_Large_Reasoning_Models.md" \
  "14_LLM_Evaluation.md" \
  "15_Introduction_to_Agentic_AI.md" \
  "16_Retrieval_Augmented_Generation_RAG.md" \
  "17_Agentic_Memory_Systems.md" \
  "18_Agent_Harness_Context_Management_and_Orchestration.md" \
  "19_Agent_Design_Patterns.md" \
  "20_Agentic_Environments_and_Benchmarks.md" \
  "21_Model_Context_Protocol_MCP.md" \
  "22_Agent_Skills.md" \
  "23_Agent_to_Agent_Communication_A2A.md" \
  "24_Multi_Agent_Systems.md" \
  "25_Agent_Development_Frameworks.md" \
  "26_Agentic_UI_Frameworks.md" \
  "27_Quiz_Questions_Detailed_Answers.md" \
  "28_Quick_Reference.md" \
  "29_Conclusion_and_Future_Directions.md"; do

  echo "" >> "$OUTPUT"
  echo "---" >> "$OUTPUT"
  echo "" >> "$OUTPUT"

  if [ -f "$SRC/$f" ]; then
    cat "$SRC/$f" >> "$OUTPUT"
  else
    echo "WARNING: $SRC/$f not found" >&2
    echo "*[Missing file: $f]*" >> "$OUTPUT"
  fi
done

echo "" >> "$OUTPUT"
echo "---" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "*End of document / 文档结束*" >> "$OUTPUT"

wc -l -c "$OUTPUT"
echo "Done: $OUTPUT"
