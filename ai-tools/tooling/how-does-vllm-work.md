---
title: "vLLM 工作原理：PagedAttention + 连续批处理"
tags:
  - vLLM
  - LLM-Serving
  - PagedAttention
  - Continuous-Batching
  - GPU-Memory
  - AI-Infrastructure
date: 2026-06-23
source: "https://x.com/amitiitbhu/status/2069384034074107905"
authors: "Amit Shekhar (@amitiitbhu)"
---

# vLLM 工作原理：PagedAttention + 连续批处理

> **来源：** [How does vLLM work?](https://x.com/amitiitbhu/status/2069384034074107905) — Amit Shekhar，Outcome School 创始人

![封面](../../image/how-does-vllm-work-cover.jpg)

---

本文深入浅出地讲解 **vLLM** 的工作原理：为什么需要它，它如何巧妙管理 GPU 内存，以及在真实世界中如何用 vLLM 高效服务大量用户。

---

## 什么是 LLM 服务（Serving）

在讲 vLLM 之前，先理解"服务一个 LLM"是什么意思。

**服务 LLM** 就是把模型跑在一台计算机上，让许多用户能同时发送问题并收到回答。

```
User 1  --question-->  +-------------------+      +-------------------+
User 2  --question-->  |  serving engine   |----->|  model on GPU     |
User 3  --question-->  |  (接请求、发回复)  |<-----| (做数学运算、回复) |
   ...                 +-------------------+      +-------------------+
                               |
                               +--reply--> 回到各用户
```

LLM 运行在 GPU 上——一种擅长做模型所需繁重数学运算的专用芯片。GPU 昂贵且内存有限，**浪费 GPU 内存 = 能服务的用户更少 = 成本更高**。

所以服务的核心目标就是：**在一张 GPU 上，同时服务尽可能多的用户，速度尽可能快**。

---

## 快速回顾：Prefill、Decode 与 KV Cache

了解 vLLM 需要先知道 LLM 是如何生成答案的。

当输入 prompt 时，模型先把它拆成 **tokens**（词或子词），然后分两个阶段处理：

### Prefill（预填充）阶段
模型读入整个 prompt，处理每个 token。这是模型的"阅读理解"阶段。

### Decode（解码）阶段
模型逐 token 写出回答。每写一个 token，就看一次前面的所有内容，再写下一个。

### KV Cache

在两个阶段中，模型为每个 token 计算一些内部值并储存——这些值就是 **KV Cache**。

简单说：模型每读或写一个 token，就为这个 token 创建一份"笔记"（notes），记录它在当前上下文中的含义。KV Cache 就是所有这些笔记的集合。

> **KV Cache 随回答长度增长。** 每生成一个新 token，就多一份笔记。所有笔记都放在 GPU 内存中。

```
PREFILL then DECODE: KV Cache 每多一个 token 就多一套笔记

prompt tokens:  [ Tell ][ me ][ a ][ joke ]
                   |      |     |     |
PREFILL 写入:    [n]    [n]   [n]   [n]      (每个 prompt token 一份笔记)

KV cache =   [n][n][n][n]                    (prefill 后 4 份笔记)

DECODE step 1:  写 "Why"       KV cache: [n][n][n][n][n]
DECODE step 2:  写 "did"       KV cache: [n][n][n][n][n][n]
DECODE step 3:  写 "the"       KV cache: [n][n][n][n][n][n][n]
                   ...                         (每步增长一个)
```

---

## 问题：KV Cache 吃掉 GPU 内存

模型本身已经占了一大块 GPU 内存。剩下的内存要装所有正在处理的请求的 KV Cache。

**每个请求的 KV Cache 都在增长。如果服务很多用户，所有 KV Cache 都挤在有限的 GPU 内存中竞争。**

服务的真正瓶颈不是数学计算速度，而是 **KV Cache 内存**。

---

## 朴素方案为什么浪费内存

朴素引擎的做法：每个请求来时，引擎不知道回答会有多长。为保险起见，它**预分配一整块连续内存**，大到足够装最长的可能回答。

比如模型最长支持 2000 个 token，那每个请求一来就预分配 2000 个 token 的 KV Cache 空间——哪怕是还没开始写一个字。

**问题在于：大多数回答都很短。** 如果某个用户的回答只有 50 个 token，剩下 1950 个 token 的空间就白白占据了，谁也用不了。

这导致两种浪费：

1. **过度预留（Over-reservation）**：预留的空间远大于实际使用，闲置空间无法给他人
2. **碎片化（Fragmentation）**：空闲内存被打散成无法利用的小碎片

```
NAIVE SERVING: 每个请求预分配一大块连续内存

Request A: [#### used (50) ............... wasted, reserved for 2000 ..............]
Request B: [###### used (120) ............ wasted, reserved for 2000 ..............]
Request C: [## used (20) ................. wasted, reserved for 2000 ..............]

剩余空闲内存：散落的微小空隙  ->  无法容纳新的请求
```

---

## vLLM 是什么

**vLLM 是一个高吞吐量的 LLM 服务引擎**，通过高效管理 KV Cache 内存，在一张 GPU 上尽可能多地服务请求。

vLLM 用两个核心思想解决内存问题：

1. **PagedAttention** — 把 KV Cache 拆成固定大小的小块，按需分配
2. **Continuous Batching** — 每步换出已完成请求，换入等待中的请求，保持 GPU 持续繁忙

---

## PagedAttention：核心思想

> **PagedAttention 将 KV Cache 拆成固定大小的小块（blocks），按需分配内存，而非一次性预留一大块。**

这个思路来自操作系统管理内存的方式。操作系统用固定大小的"页（pages）"管理内存。程序需要更多内存时，OS 就给一页，页面不必在内存中相邻排列。

vLLM 对 KV Cache 做了同样的事：
- 把 KV Cache 内存分成固定大小的 blocks，每个 block 保存固定数量 token 的笔记（例：16 tokens）
- 请求需要存更多 token 时，vLLM 给它一个额外的 block
- blocks 不必相邻排列
- vLLM 维护一个 **block table**，记录哪些 block 属于哪个请求及顺序

```
PAGED ATTENTION: KV Cache 拆成固定大小的小块

GPU memory:  [B1][B2][B3][B4][B5][B6][B7][B8][B9] ... (等大小 block 池)

Request A 的 block table  ->  B1, B4, B7      (3 blocks, 按需分配)
Request B 的 block table  ->  B2, B3          (2 blocks, 按需分配)
Request C 的 block table  ->  B5              (1 block, 刚开始)

空闲 blocks: B6, B8, B9
```

**Step 1**: 请求进入并开始生成。vLLM 给一个 block（够 16 tokens），请求开始填充。
**Step 2**: 超过 16 token，第一个 block 满了。vLLM 再给一个，哪里有空就给哪里，不必相邻。
**之后**: 回答继续增长，vLLM 一个 block 接一个 block 地按需分配。回答结束，vLLM 一次释放所有 blocks，立即回到空闲池。

这样**没有过度预留**，因为只有真正需要时才分配。**几乎没有碎片化**，因为所有 block 大小相同，任何空闲 block 都能被任意请求使用。

### PagedAttention 如何共享内存

由于 KV Cache 现在是独立的小 block，**两个请求可以指向同一个 block**，而不是各自保留一份副本。

**场景一：相同前缀。** 许多请求以相同的系统提示开头（如"你是一名友好的客服..."）。vLLM 可以只存一次共享开头部分的 KV Cache，所有请求都指向同一批 blocks，无需重复存储。

**场景二：Beam Search。** 同时探索多个候选回答，它们共享相同开头、只在后部分不同。所有 beam 共享开头部分的 blocks，只有分叉后才用独有 blocks。

```
SHARING WITH BLOCKS

共享开头:   [B1][B2]   <- 内存中只存一份，所有人共用
                |
     +-----------+-----------+
     |           |           |
Request A   Request B    Beam C
adds [B5]   adds [B6]    adds [B7]
```

---

## Continuous Batching（连续批处理）

**Batching** 是把多个请求打包在一起处理。GPU 同时处理多个请求时效率更高。

但朴素的方式——**静态批处理（static batching）**——有问题：等一批请求全部收齐，统一处理，**必须等整个批次都完成才能开始下一批**。

不同请求的回答长度差异巨大。有的 20 tokens，有的 800 tokens。短的早早完成后就空等，GPU 插槽闲置。

> **连续批处理在每个 decode 步骤结束后，立即把已完成请求换出，从等待队列拉入新请求，而不是等整个批次都完成。**

```
STATIC BATCHING (朴素): 整个批次等最慢的那个

step:   1    2    3    4    5    6    7    8
Req A:  X    X    X    done -    -    -    -     <- 空闲，浪费插槽
Req B:  X    X    X    X    X    X    X    done


CONTINUOUS BATCHING (vLLM): 完成的插槽立即被填满

step:   1    2    3    4    5    6    7    8
slot1:  A    A    A    C    C    C    D    D     <- A 完成，C 跳入，然后 D
slot2:  B    B    B    B    B    B    B    done
```

**PagedAttention + Continuous Batching 完美配合**：PagedAttention 即时释放刚完成请求的 blocks，连续批处理立即用释放的内存和插槽拉入新请求。GPU 内存和算力都得到充分利用。

---

## OpenAI 兼容 API

vLLM 以 **OpenAI 兼容 API 服务器**的形式运行。大量工具和应用已经写成与 OpenAI API 通信的接口。只需改一下地址，现有工具就能指向自己的 vLLM 服务器，跑自己的模型，而不需重写代码。

---

## vLLM 的优势

- ✅ **高得多吞吐量** — PagedAttention 停止浪费内存，连续批处理停止浪费 GPU 时间
- ✅ **更好的 GPU 利用率** — GPU 内存和算力都接近满负荷使用
- ✅ **更低的每请求成本** — 一张 GPU 服务更多用户
- ✅ **易于采用** — OpenAI 兼容 API，接入现有应用几乎无改动

---

## vLLM 的真实场景

1. **高流量聊天应用** — 大量用户同时聊天，连续批处理保持 GPU 插槽饱满，PagedAttention 把多用户的 KV Cache 打包进同一片内存
2. **Agent 系统** — Agent 每步都发送相同的大量指令，PagedAttention 的共享前缀节省大量内存；连续批处理让多步短任务不间断流转

---

## 总结

vLLM 的核心在于借鉴操作系统内存管理思想，把 KV Cache 拆成固定大小的小块按需分配、跨请求共享（PagedAttention），配合每步换入换出的连续批处理，背后提供了 OpenAI 兼容 API，使得在同等硬件上获得远超朴素方案的吞吐量和 GPU 利用率。

相关推荐阅读：
- [PagedAttention](https://outcomeschool.com/blog/paged-attention-in-llms)
- [Continuous Batching](https://outcomeschool.com/blog/continuous-batching-in-llms)
- [KV Cache](https://outcomeschool.com/blog/kv-cache-in-llms)
- [LLM Inference Optimization](https://outcomeschool.com/blog/llm-inference-optimization)

---

*整理于 2026-06-25，来源：https://x.com/amitiitbhu/status/2069384034074107905*
