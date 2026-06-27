# KV Caching in LLMs：从原理到工程的全方位解析

> **原文作者**: Avi Chawla (@_avichawla) — Co-founder @ Daily Dose of Data Science  
> **原文链接**: [KV Caching in LLMs, Clearly Explained](https://x.com/_avichawla/status/2034902650534187503)  
> **发布日期**: 2026-03-20  
> **核心概念**: KV Cache / 自回归推理 / Attention 机制 / TTFT / GQA / MQA

---

## 1. 现象：为什么 Token 生成"先慢后快"？

使用 ChatGPT 或 Claude 时，你有没有注意到：

> **第一个 Token 出现明显更慢，后续 Token 几乎瞬间输出。**

这不是偶然。背后是一个刻意的工程优化——**KV Caching**（键值缓存）。它的目标只有一个：**让 LLM 推理更快**。

本文从第一性原理出发，拆解 KV Cache 是如何工作的。

---

## 2. 第一部分：LLM 如何生成 Token

Transformer 推理的**自回归**特性：

```
输入 token 序列 → Transformer 处理 → 每个 token 产生一个 hidden state
  ↓
hidden state 投影到词汇空间 → 产生 logits（每个词一个分数）
  ↓
只取最后一个 token 的 logits → 采样得到下一个 token
  ↓
新 token 追加到输入 → 重复以上步骤
```

**关键洞察**：要生成下一个 token，你**只需要最后一个 token 的 hidden state**。其他所有 hidden state 都是中间产物。

---

## 3. 第二部分：Attention 实际上计算了什么

在每一层 Transformer 中，每个 token 产生三个向量：

- **Q（Query）** — 查询向量
- **K（Key）** — 键向量
- **V（Value）** — 值向量

Attention 的计算：

```
Attention(Q, K, V) = softmax(QK^T / √d) · V
```

对于**最后一个 token**：

```
QK^T 的最后一行使用：
  → 最后一个 token 的 Q
  → 序列中所有 token 的 K

最终 attention 输出使用：
  → 同一个 Q
  → 所有 K 和 V
```

> **结论**：计算唯一需要的 hidden state，每一层都需要最新 token 的 Q，以及**所有 token 的 K 和 V**。

---

## 4. 第三部分：冗余计算

假设模型正在生成 token：

```
生成 token 50：需要 token 1~50 的 K 和 V
生成 token 51：需要 token 1~51 的 K 和 V
```

**但 token 1~49 的 K 和 V 之前已经算过了**。同样的输入 → 同样的输出。然而，如果不做缓存，模型每一步都在**从头重新计算**所有 K 和 V。

冗余量：
- 每步：O(n) 次冗余计算（n = 当前序列长度）
- 整段生成：**O(n²) 的浪费**

---

## 5. 第四部分：KV Cache 的解决方案

**核心思路：算一次，存起来。**

### 有 KV Cache 的推理流程

```
每一步，对最新 token：
  1. 计算它的 Q、K、V
  2. 把新的 K 和 V 追加到缓存中
  3. 从缓存中取出之前所有 token 的 K 和 V
  4. 用新 Q + 完整 KV 缓存做 Attention
```

每一步只产生：
- **1 个新的 K**（每层）
- **1 个新的 V**（每层）

其他所有 K 和 V 都从内存中读取。

### 效果

- `Attention(Q, ...)` 的计算量仍然随序列长度增长（你需要对全部 K 和 V 做 attention）
- 但产生 K 和 V 的** costly projection 计算，每个 token 只做一次**，而不是每步一次
- **实际加速约 5 倍**

---

## 6. 第五部分：首 Token 延迟（TTFT）

现在你明白了为什么第一个 Token 慢：

### Prefill 阶段

发送 prompt 时，模型在一轮前向传播中处理**整个输入**：
```
计算并缓存所有输入 token 的 K 和 V
            ↓
这是最计算密集的阶段
            ↓
缓存准备好后（warm cache），后续每步只处理一个 token
```

这个初始延迟称为 **Time-to-First-Token**（TTFT）：

| 因素 | 影响 |
|------|------|
| 更长的 prompt | 更长的 prefill → 更长的 TTFT |
| chunked prefill | 分块处理降低峰值显存 |
| speculative decoding | 投机解码减少串行步数 |
| prompt caching | 复用已缓存 prompt 的 KV |

> **规律：构建缓存很贵，读取缓存很便宜。**

---

## 7. 第六部分：权衡 — 计算换内存

KV Cache 的本质：**用计算换内存**。

### 显存消耗有多大？

以 **Qwen 2.5 72B** 为例：

| 参数 | 值 |
|------|:----:|
| 层数 | 80 |
| 上下文长度 | 32K |
| 隐藏维度 | 8192 |
| 每请求 KV Cache | **数个 GB** |
| 数百并发请求 | 常超过**模型权重本身**的显存 |

### 为什么难以扩展上下文？

> 上下文长度翻倍 → KV Cache 翻倍 → 每 GPU 可服务的并发用户数减半

### 工程对策

**1. Grouped-Query Attention（GQA）**
- 多个 Query 头共享 Key/Value 头
- 以极小的质量损失大幅降低 KV Cache

**2. Multi-Query Attention（MQA）**
- 所有 Query 头共享一组 K、V
- 比 GQA 更激进

**3. PagedAttention**
- 解决 KV Cache 的显存碎片问题
- 由 vLLM 引入，成为主流推理框架的标准

---

## 8. 工程全景

### 主流推理框架的支持

| 框架 | KV Cache 优化 |
|------|--------------|
| **vLLM** | PagedAttention、连续批处理 |
| **TGI（Text Generation Inference）** | 连续批处理、Kernel 融合 |
| **TensorRT-LLM** | 精心优化的 KV Cache 管理 |
| **llama.cpp** | 多层缓存、共享 KV |

### TTFT 优化技术总结

| 技术 | 原理 | 收益 |
|------|------|:----:|
| **Chunked Prefill** | 将长 prompt 分块处理 | 降低峰值显存 |
| **Prompt Caching** | 复用已缓存的 prompt KV | 完全消除相同前缀的 prefill |
| **Speculative Decoding** | 小模型草稿 + 大模型验证 | 减少串行步数 |
| **Prefix Caching** | 自动检测并复用共用前缀 | 批处理场景显著 |

---

## 9. 速查总结

```
无 KV Cache：
  每步：重新计算所有 K 和 V（O(n²) 冗余）
  优点：无额外显存开销

有 KV Cache：
  每步：只计算新 token 的 K 和 V（O(1) 新增）
  优点：推理快 ~5 倍
  代价：每请求数 GB 显存

瓶颈迁移：
  无 KV Cache → 计算是瓶颈
  有 KV Cache → 显存是瓶颈

行业解法：
  显存瓶颈 → GQA / MQA / PagedAttention
```

---

## 10. 对 LLM 应用开发者的启示

1. **不要忽略 TTFT** — 用户能感知到首 token 延迟，长 prompt 场景尤其明显
2. **Prompt Caching 是利器** — 如果用户消息有固定前缀（系统提示词 + 历史），复用 KV Cache 能几乎完全消除 prefill 成本
3. **上下文长度不是免费的** — 2x 上下文 = 2x KV Cache = 一半的并发。请按需设置合适的 `max_tokens`
4. **推理框架选型很重要** — vLLM 的 PagedAttention 在处理长序列和高并发时相比 naive 实现优势巨大
5. **GQA 是当前最佳权衡** — 几乎所有新模型（Llama 3、Qwen 2.5、Mistral）都采用了 GQA 而非 MHA

---

> **本文基于 Avi Chawla (@_avichawla) 2026年3月20日发布的 Twitter 长文整理，并补充了工程实践背景。**
> 原文链接：[https://x.com/_avichawla/status/2034902650534187503](https://x.com/_avichawla/status/2034902650534187503)
