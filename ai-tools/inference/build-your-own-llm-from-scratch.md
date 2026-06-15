---
title: "从零构建自己的 LLM：GPT / Claude / Gemini 背后的 5 阶段流水线"
tags:
  - llm
  - training
  - tokenizer
  - transformer
  - alignment
  - rlhf
date: 2026-06-15
source: "https://x.com/sairahul1/status/2066076937806856661"
authors: "Rahul (@sairahul1)"
---

# 从零构建自己的 LLM：GPT / Claude / Gemini 背后的 5 阶段流水线

> **来源：** Rahul (@sairahul1) X/Twitter 长文 — [How To Build Your Own LLM from Scratch](https://x.com/sairahul1/status/2066076937806856661)

---

## 🔗 关联知识库文章

| 文章 | 关联点 | 建议阅读顺序 |
|------|--------|-------------|
| **[Stanford Lecture: How to Build LLMs](../ai-tools/inference/stanford-building-llm-lecture-notes.md)** | 同一话题的完整学院派版本，104 分钟讲座逐字整理。预训练/后训练的理论推导更深入 | ① 本文入门 → ② Stanford 深化 |
| **[LLM 工程师技能路线图 (2026)](../ai-tools/llm-engineering-roadmap-2026.md)** | 本文讲"从零造"，那篇讲"用起来"——覆盖 prompt、RAG、部署、优化 8 大支柱 | ② 理解原理后读，知道怎么用 |
| **[LLM 究竟如何工作（入门）](../ai-tools/inference/how-llms-actually-work.md)** | Token、attention、predict-next-token 的入门解释，更娓娓道来 | 前置阅读：零基础先读这篇 |
| **[SFT / RL / On-Policy Distillation](../ai-tools/inference/sft-rl-onpolicy-distillation-distributional-lens.md)** | 深入对齐阶段（SFT 和 RLHF），从概率分布视角拆解差异 | ③ 想深挖对齐时读 |
| **[20 AI Core Concepts (2026)](../ai-tools/inference/20-ai-concepts-2026-rahul.md)** | 更广阔的 AI 概念图谱：Transformer / embedding / RAG / agents / diffusion | 全景参考，随时查阅 |
| **[LLM 工程实战项目路线图](../ai-tools/inference/llm-engineering-projects-roadmap-2026.md)** | 34 个 LLM 实操项目，tokenizer→部署的 step-by-step 路径 | ④ 读完原理后用代码实践 |
| **[GPU Memory Math for LLMs](../ai-tools/inference/gpu-memory-math-llms-2026-ahmad.md)** | 训练推理的显存计算：数据集多大、需要多少 GPU、batch size 怎么调 | ⑤ 动手前算预算 |
| **[Inference Engines 决策指南](../ai-tools/inference/inference-engines-decision-guide-2026-ahmad.md)** | 训练完怎么部署？vLLM / llama.cpp / MLX / TensorRT-LLM 选型 | ⑥ 部署阶段参考 |

---

GPT、Claude、Gemini、Llama — 它们都来自同一个 **5 阶段流水线**。一旦理解了这个流水线，你也可以构建一个自己的语言模型。

不是 GPT-4 的克隆，而是一个真正能学习的模型。

---

## 一个大多数人都信的谎言

大多数人认为构建 LLM 的关键是**架构**（Transformer、Attention heads、Layers）。

**错了。**

Transformer 架构是公开发表的，每个主流实验室用的都是差不多的模块。如果架构是秘密，那所有人早都有 GPT-4 了。

真正的秘密是：**数据、训练和对齐（Alignment）**。架构只是一段话，其他地方才是模型真正决出胜负的地方。

---

## 5 阶段总览

```
原始互联网文本 (1M GB) → 阶段1: 数据清洗 → 阶段2: 分词 → 阶段3: 训练 → 阶段4: 对齐 → 阶段5: 评估
```

每个阶段都建立在前一阶段之上，跳过任何一个，整个系统都会崩溃。

---

## 阶段一：数据（模型真正的战场）

原始互联网文本是非常脏的。Common Crawl 包含 2500 亿页面、超过 1PB 数据，但大部分是垃圾。

**训练之前，要经历一组残酷的多步过滤：**

```
HTML → 提取纯文本 → 过滤有害/NSFW/个人数据
→ 去重（URL、文档、行级别）
→ 按词数和 token 密度过滤低质量文档
→ 基于模型的质检评分（一个维基百科编辑会引用这个页面吗？）
→ 平衡数据组合（代码、书籍、科学、网页的配比）
```

结果：最后得到的数据集只有原始大小的一小部分，但质量高出几个数量级。

> **刻进骨子里的规则：数据质量永远胜过数据量。**
>
> 这个领域最被严密守护的秘密不是架构，而是数据是怎么清洗的。

---

## 阶段二：分词（Tokenization）

模型不读原始文本，它读的是 token。

一个 token 不总是一个完整的词，而是词的一部分——模型学习到的一个基本单元：

```
"playing" → ["play", "ing"]
"unbelievable" → ["un", "believ", "able"]
"dog" → ["dog"]
```

标准方法是 **Byte-Pair Encoding (BPE)**：从单个字符开始，反复合并最常用的配对，直到得到固定大小的词表（通常 32,000～100,000 个 token）。

```python
# 极简版 BPE tokenizer
import re
from collections import Counter

def get_stats(ids):
    """统计相邻对的频率"""
    counts = Counter()
    for pair in zip(ids, ids[1:]):
        counts[pair] += 1
    return counts

def merge(ids, pair, idx):
    """合并指定的相邻对"""
    new_ids = []
    i = 0
    while i < len(ids):
        if (i < len(ids) - 1 and 
            ids[i] == pair[0] and 
            ids[i + 1] == pair[1]):
            new_ids.append(idx)
            i += 2
        else:
            new_ids.append(ids[i])
            i += 1
    return new_ids

# 示例
text = "aaabdaaabac"
tokens = list(map(int, text.encode('utf-8')))
# 反复合并最频繁的对...
```

**经验法则：** 1 token ≈ 0.75 词，1000 tokens ≈ 750 词，100k 上下文 ≈ 一本小说。

---

## 阶段三：训练（一个看似简单得荒唐的目标）

整个训练任务听起来简单到不像是真的：**预测下一个 token。**

给定 "The cat sat on the"，预测 "mat"。在数万亿个例子上做这件事，然后神奇的事情发生了——模型学会了语法、事实、推理、写代码、翻译语言、解数学题。

**没有人教它这些，它们是从海量的 next-token prediction 中涌现出来的。**

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class DecoderOnlyTransformer(nn.Module):
    """极简版 decoder-only transformer —— 所有大模型背后的架构"""
    
    def __init__(self, vocab_size, d_model=512, n_heads=8, 
                 n_layers=6, max_seq_len=1024):
        super().__init__()
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embedding = nn.Embedding(max_seq_len, d_model)
        self.layers = nn.ModuleList([
            nn.TransformerDecoderLayer(d_model, n_heads, 
                dim_feedforward=2048, batch_first=True)
            for _ in range(n_layers)
        ])
        self.ln_f = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size)
    
    def forward(self, x):
        B, T = x.shape
        tok_emb = self.token_embedding(x)       # (B,T,d_model)
        pos = torch.arange(0, T, device=x.device)
        pos_emb = self.pos_embedding(pos)       # (T,d_model)
        x = tok_emb + pos_emb
        
        # causal mask: 每个 token 只能看前面的
        mask = nn.Transformer.generate_square_subsequent_mask(T)
        
        for layer in self.layers:
            x = layer(x, x, tgt_mask=mask)
        
        x = self.ln_f(x)
        logits = self.lm_head(x)                # (B,T,vocab_size)
        return logits
```

**训练循环：**

```python
model = DecoderOnlyTransformer(vocab_size=32000)
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)

for batch in dataloader:
    x, y = batch          # x = 输入序列, y = 下一个 token
    logits = model(x)
    loss = F.cross_entropy(
        logits.view(-1, logits.size(-1)),
        y.view(-1)
    )
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

**模型实际在学什么：**
- 每个输入的 token attend 到之前的所有 token
- Causal mask 防止"偷看"未来
- Loss = 模型对真实下一个 token 的"惊讶"程度
- Loss 越低 = 预测越好 = 模型在学习语言

---

## 阶段四：对齐（把文本预测器变成助手）

预训练之后，你得到了一个让人印象深刻但**对聊天完全没用**的东西——问它问题，它可能反问三个问题。因为预测下一个 token 不代表理解你想要什么。

**两步解决：**

### Step 1: 监督微调（SFT）

给模型展示数千个 prompt → 理想回答 的示例。模型学会模仿好答案的格式。

令人惊讶的是：**你需要的数据很少**。几千个例子就够了，因为知识已经存在于预训练模型中，SFT 只是教它用正确的格式表达出来。

### Step 2: RLHF（基于人类反馈的强化学习）

SFT 教格式，RLHF 教偏好。

```
模型生成两个答案 → 人类选择更好的那个
→ 这些偏好训练一个奖励模型（Reward Model）
→ LLM 被优化以最大化该奖励
```

**没有 RLHF：** 流畅、有能力，但不可靠、自信地犯错、不会说"我不知道"

**有 RLHF：** 有用、清晰、安全、学会了"好答案"的真正含义

这就是为什么 ChatGPT 和 Claude 感觉像助手，而不是随机文本生成器。

---

## 阶段五：评估（证明它真的在工作）

没有测量的模型就是瞎猜。

**预训练期间：** 测量 **Perplexity（困惑度）**——模型对真实文本的"惊讶"程度。Perplexity 越低 = 模型学习得越好。2017 到 2023 年，最好的模型从约 70 个候选 token 的困惑度降到了不到 10 个。

**对齐之后：** Perplexity 失效了。微调后的模型在 perplexity 上更差，但实际更有用。

你需要**人工基准**：

| 基准 | 说明 | 特点 |
|------|------|------|
| **MMLU** | 57 个学科，选择题 | 测量知识广度 |
| **Chatbot Arena** | 人类盲测两模型并投票 | 测量真实偏好 |
| **AlpacaEval** | LLM 评审 LLM | 与人工 98% 一致，只要 $10 |

**残酷的真相：** 没有一个单一的评分能捕捉一个模型的全部。同一个模型在同一个基准上，仅因 prompt 格式不同，分数可能在 0.488 到 0.637 之间波动。评估真的很难，而且没人完全解决了这个问题。

---

## 生成文本：Temperature 控制创造力

```python
def generate(model, prompt_tokens, max_new=100, temperature=0.8):
    """从模型中生成文本"""
    model.eval()
    with torch.no_grad():
        for _ in range(max_new):
            logits = model(prompt_tokens)
            logits = logits[:, -1, :] / temperature
            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            prompt_tokens = torch.cat([prompt_tokens, next_token], dim=1)
    return prompt_tokens
```

| temperature | 效果 |
|-------------|------|
| 0.1 | 安全、可预测、重复 |
| 0.8 | 自然、多样、**好的默认值** |
| 1.5 | 有创意、出人意料、有时语无伦次 |

---

## 5 个常见的 LLM 项目致命错误

| # | 错误 | 真相 |
|---|------|------|
| 1️⃣ | 执念于架构 | Transformer 已标准化、公开发表、被复制——**架构是最不重要的部分** |
| 2️⃣ | 把数据当商品 | 脏数据限制你的上限，顶级实验室花在数据清洗上的时间比模型设计多 |
| 3️⃣ | 跳过缩放数学 | 过大的模型配过少的数据 → 欠训练 → 浪费算力。**最优比：约 20 tokens 数据 / 每个参数** |
| 4️⃣ | 止步于 SFT | 微调后的模型只会模仿。没有 RLHF，它永远不会学人类真正偏好什么 |
| 5️⃣ | 对齐后还信 perplexity | 后训练改变了分布。运行 SFT 后 perplexity 就不再有意义了。立刻切换到人工基准 |

---

## 你能构建的 5 个垂直 LLM 产品

流水线完全相同，你只改变一件事：**训练数据。**

### 1. 代码助手 LLM

痛点：盯着不工作的函数，Stack Overflow 12 个答案全是 2014 年的

数据：GitHub Python 文件 + Stack Overflow 被采纳回答

```json
// 训练样本
{"prompt": "Write a Python decorator that retries a function on failure", 
 "completion": "import time, functools\n\ndef retry(max_attempts=3, delay=1):\n    def decorator(func):\n        @functools.wraps(func)\n        def wrapper(*args, **kwargs):\n            for attempt in range(max_attempts):\n                try:\n                    return func(*args, **kwargs)\n                except Exception as e:\n                    if attempt == max_attempts - 1:\n                        raise\n                    time.sleep(delay)\n            return wrapper\n        return decorator"}
```

### 2. SQL 查询生成器

痛点：每个不懂技术的创始人有数据但不会写 SQL

数据：[自然语言描述, SQL 查询] 配对

### 3. 法律文件摘要

痛点：40 页合同、租赁协议、NDA，大多数人签了但不理解

数据：法律文件 + 专业律师摘要（来自公开法律案例库）

### 4. 医疗症状解释器

痛点：谷歌症状 → WebMD 告诉你你只剩 3 天

数据：临床笔记 + 患者教育材料 + **每条回答末尾明确免责声明**

### 5. 电商产品描述生成器

痛点：Shopify 店铺 500 个商品，描述全是没人读的规格表

数据：流量前 1000 的 Shopify 店铺，提取高评分商品的产品标题 + 规格 + 描述

### 所有垂直的共同模式

- ✅ 明确、具体的日常痛点
- ✅ 已经存在且公开可用的数据源
- ✅ 前后对比对这个专业领域的人瞬间可见
- ✅ 替代方案更贵（时间或金钱），因此用户愿意付费

---

## 那个令人不适的真相

一个优秀的 LLM 不是**训练**出来的，而是**工程**出来的。

5 个阶段，不是 1 个。架构只是阶段 3 中的一段话。**真正重要的东西在其他四个阶段里：**

> 数据质量。缩放数学。对齐。诚实的评估。

这就是 GPT-4 和一个业余模型之间的差距。两个实验室用完全相同的架构，会产出完全不同的模型。因为**架构是共享的，而真正重要的东西不是。**

---

## 动手尝试

```bash
# 最小设置：1500 万参数，WikiText 数据集，Google Colab 免费 GPU
# 几个小时内观察 perplexity 从 800 降到 50
# 这个下降 —— 就是模型在实时学习语言
```

> 当 perplexity 在你面前一路下跌时，那就是"一切突然通了"的时刻。

---

## 速查表：5 个阶段

| 阶段 | 输入 → 输出 | 一句话 | 关键指标 |
|------|-----------|--------|---------|
| ① 数据 | 脏乱互联网文本 → 干净数据集 | 质量胜过数量 | 过滤率、质检得分 |
| ② 分词 | 原始文本 → token IDs | BPE 为模型做"母语" | 词表大小、压缩率 |
| ③ 训练 | 随机权重 → 语言理解 | 在数万亿例子上预测下一个 token | Perplexity |
| ④ 对齐 | 文本预测器 → 助手 | SFT 教格式，RLHF 教偏好 | 人工评分 |
| ⑤ 评估 | 黑盒 → 可测量系统 | 没有衡量就是瞎猜 | MMLU、Arena、AlpacaEval |

---

*Processed on 2026-06-15 from https://x.com/sairahul1/status/2066076937806856661*
