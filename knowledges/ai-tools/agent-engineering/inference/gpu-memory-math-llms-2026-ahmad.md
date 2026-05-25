---
title: "GPU Memory Math for LLMs (2026 Edition) — 大模型显存计算完全指南"
tags:
  - llm
  - gpu
  - vram
  - memory
  - quantization
  - gguf
  - moe
  - hardware
  - inference
  - local-ai
date: 2026-05-22
source: "X/Twitter @TheAhmadOsman"
authors: "Ahmad (@TheAhmadOsman) — Part 1 of Self-hosted LLMs / Local AI series"
---

# GPU Memory Math for LLMs (2026 Edition) — 大模型显存计算完全指南

> **原文**：[Ahmad Osman 在 X 上的长文](https://x.com/theahmadosman/status/2040103488714068245)  
> **系列**：Self-hosted LLMs / Local AI Part 1（Part 2 = Memory Bandwidth, Part 3 = Inference Engines）  
> **数据**：1.7K ❤️ · 235 🔁 · 2.6K 🔖 · 259K 阅读  
> **保存日期**：2026-05-22（原文发布于 2026-04-03）

---

## 核心公式

> **VRAM（GB）≈ 参数量（B）×（每权重的有效比特位 ÷ 8）**

这一条公式解释了所有量化格式：

| 格式 | 每参数比特位 | 每 1B 参数所需 GB |
|------|------------|------------------|
| **FP16 / BF16** | 16 bits | ~2 GB |
| **FP8 / INT8** | 8 bits | ~1 GB |
| **4-bit 量化**（GPTQ/AWQ/NF4）| ~4 bits | ~0.5 GB |

### GGUF 精度对照

| 格式 | 每 1B 参数所需 | 说明 |
|------|---------------|------|
| Q6_K | ~0.82 GB | 高保真 |
| Q5_K | ~0.69 GB | 主流推荐 |
| Q4_K | ~0.56 GB | **2026 年消费级甜蜜点** |
| Q3_K | ~0.43 GB | 有损 |
| Q2_K | ~0.33 GB | 激进 |

> 如果只记三组数字：**FP16 = 2x 模型大小，FP8 = 1x 模型大小，4-bit = 0.5x 模型大小。**

---

## 没人提的显存税

权重只是 VRAM 账单的一部分。真正的杀手是：

| 隐藏项 | 说明 |
|--------|------|
| **KV Cache** | 随上下文长度增长，32K/128K 时悄然蚕食大量显存 |
| **Activations** | 运行时中间激活，因优化水平而异 |
| **Batching / 并发** | 尤其是 agent 风格的工作负载，乘数增长很快 |
| **框架开销** | Transformers vs vLLM vs TensorRT-LLM vs llama.cpp 各不相同 |
| **CUDA Graphs** | 用预留额外显存换取更好的延迟和吞吐稳定性 |

> **如果只算权重预算，你已经 Out of Memory 了。**

**经验：加 10-30% 的额外显存作为安全余量。** 长上下文（32K/128K+）、高并发、agent 工作流需要更多。

---

## 实际模型 × 显存对照表

### 按参数量

| 模型大小 | FP16 | FP8 | 4-bit |
|---------|------|-----|-------|
| **7B** | ~14 GB | ~7 GB | ~3.5-4 GB |
| **13B** | ~26 GB | ~13 GB | ~6-7 GB |
| **70B** | ~140 GB | ~70 GB | ~35-40 GB |
| **405B** | ~810 GB | ~405 GB | ~200+ GB |

### 按显存容量（权重大致能装什么）

| 显存 | FP16 | FP8 | 4-bit |
|------|------|-----|-------|
| **8 GB** | ~3B | ~6-7B | ~12-13B |
| **12 GB** | ~5B | ~10B | ~18-20B |
| **16 GB** | ~7B | ~13B | ~25B |
| **24 GB ⭐** | ~10-12B | ~20B | ~35-40B |
| **48 GB** | ~20-24B | ~40B | ~70-80B |
| **80 GB** | ~35-40B | ~70B | ~140B-class |

> 24 GB（RTX 3090/4090/5090）是目前本地部署的最佳性价比甜蜜点。

---

## 为什么算好了还爆显存

**因为权重只是故事的一部分。** 上面的表格只是权重，不是实际运行时所需总显存。需要额外计入 KV Cache、激活值、batch 和框架开销。

---

## MoE 陷阱

Mixture-of-Experts 容易迷惑人。

- "8×7B"听起来是 56B 模型
- 但每次只有一部分 expert 参与计算

**所以：计算代价 ≠ 内存代价。**
- **总参数量** → 影响内存占用
- **激活参数量** → 影响速度

取决于加载方式：可能需要加载所有 expert 的权重（全内存开销），也可以在 GPU 间分片。

> 把 MoE 当 dense 模型算，会严重高估或低估。

---

## GGUF 不是魔法

GGUF 被当作"作弊代码"，但它不是。它是一种针对 llama.cpp 风格推理优化的容器+量化策略，专为 CPU+GPU 混合部署和极致内存效率设计。

**陷阱：** 这些内存数字只在 llama.cpp 运行时中成立。一旦切换框架，权重可能被反量化，内存用量可能大幅飙升。

> "它只要 6 GB"不是普适真理，而是**运行时相关的真理。**

---

## 唯一需要记住的心智模型

> **VRAM ≈ B × (bits ÷ 8)**，然后加上运行时开销、KV Cache 和并发余量。

一旦内化了这个公式，你不再问"能不能跑"，而是问**"我想怎么跑"**。

---

## 关联阅读

- [Inference Engines 决策指南（2026）](../agent-engineering/inference-engines-decision-guide-2026-ahmad.md) — Part 3，理解公式之后的引擎选择
- [LLMs 101 实践指南（2026）](../agent-engineering/llms101-practical-guide-2026-ahmad.md) — Part 2 的等效内容，KV Cache、Transformer 完整背景
- [RAG 管道设计 10M 文档](../agent-engineering/rag-pipeline-10m-docs-google-l5.md) — 理解了显存限制后，如何设计企业级 RAG 系统

---

**🔗 关联项目路线图：** [Step-By-Step LLM Engineering Projects (2026 Edition)](../../../../ai-engineering/llm-engineering-projects-roadmap-2026.md) — 本文是该系列的后续实践路线图，包含 34 个动手项目。
