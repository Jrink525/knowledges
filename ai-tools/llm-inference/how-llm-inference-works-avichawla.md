---
title: "LLM 推理工作原理（清晰解释）"
tags:
  - llm-inference
  - transformer
  - kv-cache
  - optimization
date: 2026-06-28
source: "https://x.com/_avichawla/status/2071201619530956863"
authors: "Avi Chawla"
---

# LLM 推理工作原理，清晰解释

> **来源：** [How LLM Inference Works, Clearly Explained.](https://x.com/_avichawla/status/2071201619530956863) — Avi Chawla (@_avichawla)

---

每次对 LLM 调用 `generate()`，都会在同一个 GPU 上运行两个截然不同的计算阶段：

- **Prefill（预填充）**—— 处理 prompt，**计算密集型**（compute-bound）
- **Decode（解码）**—— 逐一生成 token，**内存带宽密集型**（memory-bound）

大多数推理优化专项针对其中一个阶段。诊断哪个阶段是瓶颈，是加速部署的第一步。

---

## 1. Tokenization 和 Embedding

Byte Pair Encoding（BPE）等分词器将原始文本转换为整数 ID，词表大小约 50,000 token：

```python
prompt = "How does inference work?"
ids = tokenizer.encode(prompt)
# ids -> [2437, 1374, 32278, 670, 30]
```

每个 ID 映射到 Embedding Table 中的一行，形状为 `[vocab_size, hidden_dim]`。如果模型的隐藏维度为 4,096，则每个 token 变成一个 4,096 维向量。

```python
# embedding_table 形状: [vocab_size, hidden_dim]
vectors = embedding_table[ids]   # 形状: [num_tokens, 4096]
```

位置信息在此阶段注入。大多数现代架构使用 **Rotary Position Embeddings（RoPE）**，通过旋转嵌入向量而不是添加独立的位置向量来编码位置。

![RoPE 位置编码示意图](../image/llm-inference-explained-avichawla-1.png)

---

## 2. Transformer Layers

嵌入序列通过堆叠的 Transformer 层（通常 32-80+ 层，视模型大小而定）。每层依次执行两个操作：

### Self-Attention

为每个 token 计算三种投影（Query、Key、Value）：

```python
# scores: 每个 token 对其它 token 的注意力强度
Q, K, V  = x @ Wq, x @ Wk, x @ Wv

scores = (Q @ K.T) / sqrt(d_k)

weights = softmax(scaled)  # 每个 token 一行，和为 1

attn_output = weights @ V
```

![Self-Attention 计算示意图](../image/llm-inference-explained-avichawla-2.png)

### Feed-Forward Network (FFN)

独立处理每个 token 的向量，经过两层 MLP。Attention 负责在不同位置间传递信息，FFN 负责对信息进行变换。

最终层之后，模型将最后一个 token 的隐藏状态投影回词表大小 `[hidden_dim, vocab_size]`，应用 softmax，从结果分布中采样产生第一个输出 token。

---

## 3. Prefill：计算密集阶段

处理输入 prompt 是第一个阶段。所有 token 被并行处理：Q、K、V 同时计算，attention 以大规模的矩阵-矩阵乘法运行。这是**计算密集型**（compute-bound）工作，GPU 的算力吞吐是瓶颈，利用率很高。

衡量此阶段的指标是 **TTFT（Time to First Token）**——第一个输出 token 出现之前的延迟。

Prefill 阶段还负责填充 **KV Cache**：每层的 K 和 V 张量被存储在 GPU 内存中以供后续重用。

![Prefill 与 Decode 对比](../image/llm-inference-explained-avichawla-3.png)

代码示意：

```python
# Prefill: 一次性处理整个 prompt
hidden = embed(prompt_tokens) + positions
for layer in model.layers:
    Q, K, V = project(hidden)             # 一次性计算所有 token
    hidden  = attention(Q, K, V) + hidden
    hidden  = feedforward(hidden) + hidden
    cache_kv(layer, K, V)                 # 保存供后续使用
first_token = sample(project_to_vocab(hidden[-1]))
```

---

## 4. Decode：内存带宽密集阶段

第一个 token 生成后，模型切换为逐 token 生成模式。对于每个新 token，只计算该 token 的 Q、K、V。前面所有 token 的 K 和 V 已在缓存中。

每一步的算力需求极小（一个 query 向量与已缓存的 key 矩阵相乘，而非全矩阵乘法）。但 GPU 仍需从内存中加载所有权重矩阵和整个缓存的 K/V。瓶颈从算力切换为**内存带宽**。

衡量此阶段的指标是 **ITL（Inter-Token Latency）**——连续输出 token 之间的时间。低 ITL 让模型感觉响应迅速。

```python
# Decode: 每次迭代一个 token
token = first_token
for step in range(MAX_STEPS):
    x = embed(token) + position(step)
    for layer in model.layers:
        q, k, v = project(x)
        K_all, V_all = caches[layer].append(k, v)  # 缓存历史 + 新值
        x = layer.forward(q, K_all, V_all, x)      # attention + FFN + 残差连接
    token = sample(project_to_vocab(x))
    yield token
```

![Decode 阶段的内存瓶颈示意图](../image/llm-inference-explained-avichawla-4.png)

---

## 5. KV Cache（键值缓存）

如果没有缓存，生成 1,000 个 token 的响应需要在每一步重新计算对整个不断增长的序列的注意力，产生 O(n²) 的复杂度。

KV Cache 存储每层的 K 和 V 张量，增量追加新条目。下面的视频展示有/无 KV Cache 的推理速度对比：

![KV Cache 效果演示视频](https://video.twimg.com/amplify_video/2071198581126815744/vid/avc1/1256x732/e8_B27wjDc2X6qqN.mp4)

加速比在长生成中大约 **5 倍以上**。

代价是缓存随序列长度线性增长，且逐层存在。对于 13B 参数模型，每个 token 大约消耗 **1 MB** 的缓存。4K token 的上下文仅在缓存上就消耗 **4 GB 显存**。这就是长上下文代价高昂的原因——缓存与批大小直接竞争 GPU 内存。

标准缓解措施包括：
- **量化缓存**到 INT8 或 INT4
- **滑动窗口注意力**（丢弃固定窗口外的 token）
- **分组查询注意力（GQA）**——在注意力头间共享 K/V
- **PagedAttention**——vLLM 背后的内存管理技巧，像操作系统管理虚拟内存一样分页管理缓存，消除碎片

![KV 缓存管理技术对比](../image/llm-inference-explained-avichawla-5.png)

Avi 还在另一条推文中深入讨论了 KV 缓存管理：

> 相关推文: https://x.com/_avichawla/status/2070828078247604480

---

## 6. 围绕缓存重新设计注意力机制

量化和分页将 KV Cache 视为固定成本。DeepSeek 的 V4 系列（2025 年 4 月发布）采取了不同路线：重新设计注意力，使缓存从结构上就更小。

V4 使用两种压缩注意力机制的混合：

**Compressed Sparse Attention (CSA)** — 通过 softmax-gated pooling 将 KV 条目压缩 4 倍，然后在压缩 token 上应用稀疏注意力。

**Heavily Compressed Attention (HCA)** — 更激进，将 128 个 token 的 KV 条目合并为单个压缩条目，对这些表示应用密集注意力。

![DeepSeek V4 注意力机制对比](../image/llm-inference-explained-avichawla-6.png)

在 100 万 token 上下文下，V4-Pro 相比 DeepSeek-V3.2 仅需 **27%** 的单 token 推理 FLOP 和 **10%** 的 KV 缓存。

绝对值上，1M 上下文下 bf16 精度每序列的 KV 缓存为 **9.62 GiB**，而 V3.2 架构估计为 83.9 GiB。再加上 fp4/fp8 量化，缓存再缩小 2 倍。

KV Cache 已成为整个领域围绕其优化模型架构的核心约束。

---

## 7. 量化（Quantization）

训练使用 FP32 或 BF16 以保证梯度稳定性。推理不需要这种精度。降低位宽带来的内存节省是线性的：

| 精度 | 7B 参数模型大小 |
|------|----------------|
| FP32 | 28 GB |
| FP16/BF16 | 14 GB |
| INT8 | 7 GB |
| INT4 | 3.5 GB |

INT4 是 7B 模型能在 4-6 GB 显存的笔记本 GPU 上运行的原因。GPTQ 和 AWQ 等方法使用逐通道缩放因子来最小化有损压缩造成的质量退化。做得好的 INT4 在标准基准测试上距离全精度模型仅在 1-2 个百分点以内。

![量化对性能的影响](../image/llm-inference-explained-avichawla-7.png)

从 FP16 降到 INT8 通常能将推理延迟减半，而质量损失可忽略不计——使量化成为大多数部署中**杠杆率最高的单点优化**。

---

## 8. 推理服务基础设施

现代推理服务器在 prefill-decode 循环上包装了几项优化：

### 连续批处理（Continuous Batching）
在同一个 GPU 步骤中交错来自多个请求的 token，即使在内存密集的解码阶段也能保持高利用率。

### 推测解码（Speculative Decoding）
使用小型的 draft 模型提出多个 token，然后大型模型在一次前向传播中验证它们。当 draft 模型的接受率较高时，这实际上将多个顺序解码步骤转化为一次并行验证。

Avi 在此详细介绍了推测解码：

> 相关推文: https://x.com/_avichawla/status/2054860740541207032

![推测解码示意图](../image/llm-inference-explained-avichawla-8.png)

### PagedAttention (vLLM)
以固定大小的块管理 KV 缓存内存，消除碎片，使每个 GPU 能处理更多并发请求。

vLLM、TensorRT-LLM 和 Text Generation Inference (TGI) 等框架组合了这些技术。单个 GPU 可以服务数十个并发用户——因为 decode 阶段使大部分算力处于空闲，连续批处理用其他请求填充了空闲容量。

---

## 9. 完整推理路径

![LLM 推理完整流程](../image/llm-inference-explained-avichawla-3.png)

| 步骤 | 操作 | 说明 |
|------|------|------|
| **1. Tokenize** | 文本 → 整数 ID | 通过 BPE 分词 |
| **2. Embed** | ID → 向量 | RoPE 编码位置 |
| **3. Prefill** | 并行处理所有输入 token | 计算密集型，KV Cache 填充，首 token 输出 |
| **4. Decode Loop** | 每次一个 token | 投影 Q → 对缓存的 K/V 做 Attention → FFN → 采样 → 追加 K/V 到缓存。内存带宽密集型 |
| **5. Detokenize** | Token ID → 文本 | 映射回文本并流式输出 |

---

## 10. 实践启示

- **长 prompt → TTFT 昂贵**（prefill 瓶颈）
- **长输出 → ITL 昂贵**（decode 瓶颈）
- 两者对硬件资源的要求截然不同
- 上下文长度不是免费的——它膨胀 KV Cache 并直接降低批处理容量
- 即使服务器满载，decode 阶段的 GPU 利用率也可能降到 30%——瓶颈是内存带宽，不是算力
- 解决方案不是增加算力，而是**更快的内存、更小的缓存、或更好的批处理**

> 当有人告诉你他们的模型很慢时，第一步诊断是：**启动慢**（prefill 瓶颈，优化 TTFT）还是 **流式输出慢**（decode 瓶颈，优化 ITL）？

---

## 总结

LLM 推理优化的核心矛盾是 **prefill vs. decode** 这两个阶段的物理特性完全不同：

- **Prefill** 是计算密集型 → 需要更大算力（更多 GPU、Tensor Core 利用率）
- **Decode** 是内存带宽密集型 → 需要更好内存（HBM 带宽）、更小缓存（GQA、量化、PagedAttention）、以及 batch 层面复用（连续批处理、推测解码）

DeepSeek V4 代表了从"管理缓存成本"到"设计上消除缓存成本"的范式转变。未来，模型架构本身将成为推理优化的第一道防线。

---

*Published on 2026-06-28 by Avi Chawla (@_avichawla) | Processed and translated from [X/Twitter long-form article](https://x.com/_avichawla/status/2071201619530956863)*
