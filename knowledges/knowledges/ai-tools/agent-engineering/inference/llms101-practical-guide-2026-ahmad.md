---
title: "LLMs 101: A Practical Guide (2026 Edition) — 本地大模型完全实践指南"
tags:
  - llm
  - inference
  - local-ai
  - transformer
  - kv-cache
  - quantization
  - vram
  - gpu
  - rag
  - fine-tuning
  - edge-ai
  - hardware
  - tokenizer
  - attention
date: 2026-05-22
source: "X/Twitter @TheAhmadOsman"
authors: "Ahmad (@TheAhmadOsman) — ai, chips, systems engineering"
---

# LLMs 101: A Practical Guide (2026 Edition) — 本地大模型完全实践指南

> **原文**：[Ahmad Osman 在 X 上的长文](https://x.com/theahmadosman/status/2057590224729911346)  
> **数据**：187 ❤️ · 21 🔁 · 529 🔖 · 58K 阅读  
> **字数**：原文约 54,000 字符，本文为精要中文版

---

## 一、核心循环：Token In, Token Out

先理解核心循环。文本变成 token → token 经过 Transformer → Attention 决定哪些早先的 token 重要 → 运行时维护 KV Cache 免得每次重新算 → 模型选下一个 token → 重复。

**数学模型很简单：**
> f(theta, sequence) —> probability distribution over next_token

其中：
- **theta** = 模型权重
- **sequence** = prompt + 已生成的 token
- **Logits** = softmax 之前的原始分数
- **解码（Decoding）** = 把概率分布变成一个选中的 token

速度用 **tokens/s** 衡量。响应感知取决于两阶段：长 prefill ≈ 第一个字之前的停顿；慢 decode ≈ 输出流变慢。

---

## 二、Tokens：工作的基本单位

LLM 看到的不是词，而是 token——文本碎片的整数 ID。

| token 类型 | 示例 |
|-----------|------|
| 完整单词 | "hello" |
| 词根 | "inter", "national" |
| 标点 | "," |
| 带空格的字符串 | " hello" |
| 字节级后备 | 生僻字/特殊符号 |
| 控制标记 | `<\|user\|>`, `<\|assistant\|>` |

不同 tokenizer（BPE vs SentencePiece）压缩率不同。4000 英文词在一个 tokenizer 里可能 5000 token，在另一个里可能 7500。

**2026 年本地模型的上下文窗口：** 8K ~ 32K 常见，128K、256K 甚至 1M 也有。但支持 ≠ 不慢 ≠ 同等准确——128K 模型可能在 64K 就开始变慢、100K 开始丢 coherence。**始终测试你实际要用的长度。**

---

## 三、Transformer：骨架

现代 LLM 基本都是 **decoder-only Transformer**，只向后看过去 token。

简化的 Transformer 层：
1. **Token Embeddings** — token ID 变成向量
2. **位置编码（RoPE）** — 旋转表示，编码位置
3. **Self-Attention** — 看回头哪些 token 重要
4. **MLP / Feed-Forward** — 扩展再压缩表示（大部分参数在这里）
5. **LayerNorm + Residual** — 稳定深层网络
6. **Output Projection** — 最后的 hidden state 变成 logits

---

## 四、Attention 架构：选模型的关键

| 类型 | 说明 | 内存代价 |
|------|------|---------|
| **MHA** (Multi-Head) | 每头独立 K/V，表现力最强 | KV Cache 最大 |
| **GQA** (Grouped Query) | 组间共享 K/V 头，当前主流 | 中等 |
| **MQA** (Multi-Query) | 所有查询头共享 1 个 K/V 头 | 最省 |

> 两个 7B 模型在长上下文下表现天差地别。7B MHA × 128K 可能爆 24GB GPU；7B GQA × 128K 可能绰绰有余。**选模型时要看 Attention 类型，不能只看参数量。**

FlashAttention / SDPA 等内核优化可大幅降低 attention 内存流量。同一模型、同一硬件，runtime 的内核不同可能差出数倍速度。

---

## 五、KV Cache：隐藏的内存账单

KV Cache 是生成阶段的"工作记忆"——存储已处理 token 的 key/value attention 状态，避免每次从头算。

**KV Cache 大小公式：**
> tokens × layers × kv_heads × head_dim × precision × 2

经验值（Llama 7B MHA, FP16）：**每 token ~0.5 MiB**
- 4K tokens → ~2 GiB
- 32K tokens → ~16 GiB

> 这就是为什么空 prompt 时模型能加载，贴一篇长文档就崩了。**权重能装下，工作记忆装不下。**

GQA/MQA + FP8/INT8 KV Cache 可大幅缩减。低于 8-bit 的 KV cache（KIVI、KVQuant 等 2-4 bit）只在研究系统里有用，**不要在生产里随意启用**。

⚠️ KV Cache 量化和推测解码（Speculative Decoding / DTree）是两回事。推测解码加速 decode 不改 cache 大小。

---

## 六、Prefill vs Decode：两个性能区间

| 阶段 | 做什么 | 特征 | 瓶颈 |
|------|--------|------|------|
| **Prefill** | 处理输入 prompt | 可并行，GPU 高效 | 长 prompt 很贵 |
| **Decode** | 逐个生成新 token | 顺序执行 | 决定"快不快"的感知 |

- 长 prompt 惩罚 prefill（首字等待时间长）
- 长回答惩罚 decode（流式输出慢）
- 长对话惩罚两者（KV Cache 持续膨胀）

---

## 七、解码策略（Decoding）

模型产出 logits 后还没写任何东西。**解码是把分数变成实际 token 的策略。**

三个核心旋钮：
| 旋钮 | 作用 |
|------|------|
| **Randomness**（Temperature） | 允许多少变化 |
| **Tail Reach**（Top-p/Top-k） | 能触及多低概率的 token |
| **Boundaries**（Stop tokens / max tokens） | 防循环、防跑题、防 Schema 破坏 |

> Greedy decoding 不一定更准，经常很脆弱。评估用确定性设置，创意工作让模型喘口气。

---

## 八、模型包包含什么

一个可运行的本地 LLM 远不止一个权重文件：

1. **架构/配置**：层数、hidden size、attention 类型、RoPE 设置、词表大小、特殊 token
2. **权重**：safetensors / GGUF / GPTQ / AWQ / EXL2 等格式
3. **Tokenizer**：文本 ↔ token ID 的规则
4. **Chat Template**：system/user/assistant/tool 消息的精确标记
5. **生成配置**：temperature、top-p、stop tokens 等默认值
6. **许可证 + 模型卡**

权重最大但不代表全部。**Tokenizer、config 或 chat template 错了，权重本身也会感觉坏了。**

---

## 九、Chat Templates：最常见的故障点

每个聊天模型都有特定的对话格式。用错格式会导致胡言乱语、角色混淆、system prompt 被忽略、工具调用出错。

最佳实践：
- 用 `apply_chat_template`（Transformers）或 runtime 自带的模型模板
- 区分 base / instruct / chat / reasoning / tool-tuned 模型类型
- 确保 BOS/EOS token 正确
- 支持多模型的应用要做**模板切换**

> **把模板当作 API 契约。用错了，你测试的根本不是你以为的模型。**

---

## 十、本地模型的内存公式

**三大内存消费者：**
1. 模型权重
2. KV Cache
3. Runtime 开销

**权重内存近似：**
| 精度 | 每参数字节 |
|------|-----------|
| FP16/BF16 | ~2 bytes |
| INT8/Q8 | ~1 byte |
| Q4 | ~0.5 byte（+ 格式开销）|

**完整估算：**
> total_memory = quantized_weights + KV_cache_for_context + runtime_overhead + batch/concurrency_overhead + safety_margin

⚠️ **陷阱：** 13B Q4 在 8K 上下文下轻松装下，32K 时 KV Cache 翻 4 倍就炸了。权重没变，上下文变了。

**留 10-20% 余量。** 跑到 99% VRAM 是在乞求 OOM。

---

## 十一、2026 年硬件分层

| VRAM | 级别 | 推荐模型大小 |
|------|------|-------------|
| 8-12 GB | 入门 | 4B-9B, Q4/Q5 |
| 16 GB | 最低舒适 | 7B-14B, Q4/Q5 |
| **24 GB** | **最佳性价比** | 7B-32B |
| 48 GB+ | 强者世界 | 大 Dense / MoE |

> **最痛苦的设置**是模型几乎能装下但只能 spill 到 CPU。技术上能跑，但 token 速度从可用变绝望。

性能取决于：**内存带宽 > VRAM 容量 > GPU FLOPs**。两张卡 VRAM 相同但带宽差 2 倍，token 速度差 2 倍。

---

## 十二、模型选择五步检查

> 不是"什么模型最好"，而是**"在你的硬件上、做你的任务，最小的好模型是什么"**

1. **Task fit** — 聊天 / 编程 / 文档 / Agent / 多模态 / edge
2. **Memory fit** — 权重 + KV Cache + runtime 开销 + 安全余量 ≤ 80-90% 可用内存
3. **Interface fit** — Tokenizer、chat template、stop tokens、tool schema
4. **Runtime fit** — runtime 是否支持此架构、量化、上下文长度、服务模式
5. **License fit** — 你真能在目标场景里用吗？

> 排行榜有用，但不代替你的评估。你的工作负载才是重要的 benchmark。

**场景推荐：**
| 场景 | 推荐方案 |
|------|---------|
| 简单本地助手 | 7B-14B instruct, Q4/Q5, 8K-32K, Harbor/LM Studio |
| 本地编程助手 | 14B-32B, 代码模型, 低温度, 仓库检索, test loop |
| 隐私文档助手 | 强 instruct + 本地 embedding + reranker + RAG + 引用 |
| 推理任务 | reasoning-tuned 模型, 预留额外 token |
| 低资源 | 1B-4B, Q4/Q5, 短 prompt, 固定 schema |

---

## 十三、2026 年本地模型生态

> 不再是 Llama vs 其他。你在选择**生态系统**：权重、许可证、tokenizer、模板、量化、runtime 支持、社区工具、故障模式。

| 家族 | 特色 |
|------|------|
| **Qwen 3.5/3.6** | 强默认家族。覆盖小模型 → MoE → 编程/多语言/工具/Agent/长上下文 |
| **Gemma 4** | Google DeepMind, Apache 2.0, 适合商业使用和端侧部署 |
| **DeepSeek** | MoE + Multi-head Latent Attention + FP8 serving |
| **Mistral** | 通用/编程/推理/多模态全系列 |
| **Nemotron 3** | NVIDIA 生产级 Agent 模型, Mamba-Transformer MoE |

Qwen 27B Dense 是目前本地用户最实用的公开权重模型之一。2×RTX 3090 上配置好 runtime 即可流畅运行。

**前沿推理研究：**
- PagedAttention — 服务端 KV Cache 内存管理
- FP8 KV Cache — vLLM 等已支持
- DFlash / DDTree — 推测解码新方向
- NVFP4 — NVIDIA 硬件专属

---

## 十四、常见故障模式

| 故障 | 最可能原因 | 修复 |
|------|-----------|------|
| **OOM** | KV Cache 或 batch 太大 | 减上下文/换小模型/降量化 |
| **胡言乱语** | Chat template 错误 | 检查模型卡和 runtime 模板 |
| **首字慢** | Prefill 太贵 | 加 prefix caching / 缩短 prompt |
| **流式慢** | Decode 瓶颈 | 检查带宽/量化/spill/attention 后端 |
| **文档回答差** | 检索失败 | 检查 chunking/reranker/引用 |
| **JSON 坏了** | 温度太高 | 用低温度/constrained decoding |
| **重复循环** | 温度或 top-p 太高 | 加 repetition penalty / 检查 stop tokens |

> **先检查无聊的东西。** 它们比换模型修得更多问题。

---

## 十五、成长路线

| 阶段 | 工具 | 目标 |
|------|------|------|
| **初学者** | Harbor / LM Studio + 4B-9B Q4 | 学会 prompt、比较模型、理解速度和内存 |
| **进阶开发者** | llama.cpp / Transformers + GGUF | 构建本地服务、测试 RAG、自定义应用 |
| **高级私有部署** | vLLM / SGLang + 多 GPU | 服务真实用户、优化吞吐、监控运维 |
| **专家优化** | TensorRT-LLM + 自定义 kernel | 极致推理效率、量化实验、蒸馏 |

---

## 十六、安全底线

**本地 ≠ 自动安全。** 威胁包括：
- 恶意模型文件（pickle 可执行任意代码）
- 检索文档中的 prompt injection
- 工具调用滥用
- 日志泄露隐私
- 桌面应用的 telemetry

四个习惯：
1. **加载慎重**：选 safetensors / GGUF，避开 `.bin`，不用 `trust_remote_code`
2. **运行限制**：非特权用户、容器 sandbox、离线时关网络
3. **保护秘密**：凭证不出现在 prompt 和 RAG 索引中
4. **版本追踪**：模型、prompt、runtime、量化版本都要记

---

## 十七、RAG > 巨无霸 Prompt

**RAG = 检索增强生成。** 从知识库检索相关 chunk 给模型，而不是把一切塞进 prompt。

好的 RAG 系统需要：
文档解析 → chunking → embedding → 向量索引 → 检索 → reranking → prompt 构建 → 回答生成 → 引用检查 → 评估

**Chunking 策略是无声杀手。** 固定大小无重叠会切断句子和丢失上下文。语义 chunking 或父子文档检索通常更好。

> 大多数烂 RAG 不是 LLM 的错，而是 chunking、检索、reranking、评估的问题。

---

## 十八、微调：最后的手段

| 优先级 | 方法 |
|--------|------|
| 1 ✅ | 正确的 chat template |
| 2 ✅ | 更好的 prompt |
| 3 ✅ | 更好的模型 |
| 4 ✅ | 更好的解码设置 |
| 5 ✅ | RAG + reranking |
| 6 ✅ | Few-shot examples |
| 7 ⏳ | **Fine-tuning（LoRA / QLoRA）** |

> 大多数"模型不懂我的领域"的问题，实际上是 prompt 太模糊、template 错了、或 retrieval 坏了。

---

## 十九、Open-Weight ≠ Open Source

2026 年常见术语：
- **Open-weight** — 能下载权重，不表示能商用/自由修改
- **Source-available** — 代码可见，不一定是开源
- **Open Source AI Model** — OSI 的严格定义需包含架构、权重、推理代码、足够的数据信息

有些许可证看起来宽松但有**限制条款**：禁止竞争用途、禁止输出训练、禁止超规模部署、地域限制、专利条款。

> **规则：** 商用前必须读模型卡和许可证。

---

## 二十、实用 Runbook

在信任本地模型做真正工作之前的最后检查：

1. **选型**：家族匹配任务 → 读许可证 → 确认硬件 → 选量化 → 估算完整内存（含 KV Cache）
2. **加载**：安全来源 → 验证 tokenizer 和 template → 设定上下文长度 → 按任务选解码参数
3. **评估**：代表 prompt 测试 → 测 TTFT 和 decode 速度 → 跟踪峰值内存 → RAG 之前先测 retrieval
4. **版本**：模型、量化、runtime、prompt、template、adapter、embedding、reranker、eval 集、硬件配置都要记

---

## 总结：核心公式

> **本地 LLM 成功 = 模型适配 + 正确的格式 + 好 runtime + 真实的评估**

剩下都是细节——但细节决定成败。

| 要点 | 一句话 |
|------|--------|
| **模型一次只产生一个 token** | 不是一次性写好答案 |
| **代码是更大物体的表面（约等于这个逻辑）** | 权重之外还有 template、tokenizer、config |
| **KV Cache 是隐藏账单** | 长上下文最大的成本 |
| **量化是权衡** | 代码/数学/结构化输出先退化 |
| **长上下文不是免费的** | 先 RAG 找到证据，再用长上下文分析 |
| **隐私需要纪律** | 本地 ≠ 自动安全 |
| **排行榜不是你的 eval** | 用你自己的任务测试 |
| **工具使用需要外部防护** | JSON Schema 不阻止 prompt injection |

---

## 关联阅读

- [The Software Factory Trap](../agent-engineering/software-factory-trap-dhasandev.md) — 理解本地模型 Agent 化之后的"更大的物体"
- [Agent Harness 从理论到实践](../agent-engineering/harness-from-theory-to-practice.md) — 本地模型集成到工程体系
- [Codex 用到极致指南](../agent-engineering/codex-max-usage-guide-dotey.md) — 对比：Codex 云端 vs 本地部署
