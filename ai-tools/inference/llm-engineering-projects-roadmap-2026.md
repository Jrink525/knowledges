---
title: "LLM 工程化项目路线图 2026 版——从 Tokenizer 到全栈大模型"
tags:
  - LLM
  - engineering
  - roadmap
  - projects
  - tokenizer
  - transformer
  - attention
  - MoE
  - quantization
  - post-training
  - evaluation
date: 2026-06-22
source: "https://x.com/theahmadosman/status/2058745340895870985"
authors: "Ahmad Osman (@theahmadosman)"
---

# LLM 工程化项目路线图 2026 版——从 Tokenizer 到全栈大模型

> 原题：Step-By-Step LLM Engineering Projects (2026 Edition)
> 
> **核心信条：读论文到一定程度就不够了。你得自己把栈搭起来。**

---

## 学习方法论

每做一个项目，遵循同一个循环：

1. **Build（构建）** — 用库之前先自己手写核心实现
2. **Plot（可视化）** — loss 曲线、延迟曲线、内存曲线、attention 热图、路由直方图、熵值图
3. **Break（搞坏它）** — 去掉位置编码、禁用 causal mask、过度量化、饿死数据、让 router 崩溃、塞爆 KV cache
4. **Explain（解释）** — 预期的行为 vs 实际发生了什么、什么让你意外、下一步做什么
5. **Ship（交付）** — 仓库、notebook、博客、Demo、基准图表

> 不要只发"I implemented attention"——发 attention 热图、发 mask bug、发熵值曲线、发延迟图表、发那些 repition loop、发专家路由坍缩、发量化退化、发出乎意料的安全失败。

---

## 前置基础（四篇文章系列）

在开始本路线图之前，作者推荐先掌握这套硬件基础：

1. **GPU Memory Math for LLMs (2026 Edition)** — GPU 显存数学
2. **Memory Bandwidth for Local AI Hardware (2026 Edition)** — 本地 AI 硬件的内存带宽
3. **Inference Engines for LLMs & Local AI Hardware (2026 Edition)** — 推理引擎
4. **LLMs 101 (2026 Edition): How Models Think One Token At A Time** — 模型工作机制

---

## Part I：文本 → 张量

### 项目 1：从零实现 Tokenizer

在训练模型之前，先决定世界如何变成符号。这个决定影响压缩率、多语言行为、罕见词、代码、数学、表情符号、延迟和上下文利用率。

实现 BPE（Byte-Pair Encoding）。训练一个小词表。然后和 Unigram/SentencePiece 对比。

> **关键理解：** BPE 通过子词单元组合处理罕见词；SentencePiece 让 tokenizer 变成可从原始文本直接训练的算法。

### 项目 2：One-Hot 向量、Embedding 和语义几何

用最简单的方式构建 embedding 表，在 next-token 目标上训练它。

---

## Part II：位置编码

### 项目 3：实现 Sinusoidal、Learned、RoPE、ALiBi

Attention 本身是置换不变的——没有位置，"狗咬人"和"人咬狗"看起来太相似。

- **RoPE**：通过旋转编码相对位置
- **ALiBi**：基于距离对 attention 分数加偏置，设计来改善长度外推

---

## Part III：Attention 构建

### 项目 4：单 Query 手写 Scaled Dot-Product Attention

为单个 query 算 Q、K、V → 点积 → Scale → Softmax → 加权求和。

> **关键理解：** Transformer 用 Attention 替代了 RNN 的循环，使训练可以序列并行。

### 项目 5：扩展到 Multi-Head Attention

多头 Attention 让不同子空间学习不同的关系模式——有的头专攻局部语法、有的头做 induction-like copying、有的头追踪长程依赖。

---

## Part IV：Transformer Block

### 项目 6：构建单个 Decoder Block

Token Embedding + 位置编码 + Masked Multi-Head Attention + Residual + Normalization + FFN + 输出投影。

> **2026 年的常见配置：** Pre-norm + RMSNorm + SwiGLU 门控 MLP

### 项目 7：堆叠多个 Block 成 Mini-Former

在玩具文本上训练一个小型 decoder-only 模型。目的不是做一个有用的 chatbot，而是**理解训练循环**。

---

## Part V：训练目标

### 项目 8：对比 Causal LM、Masked LM、Prefix LM、Denoising

- **BERT**：Masked LM，构建双向表征
- **GPT**：Causal next-token prediction
- **T5**：Text-to-Text + Denoising
- **UL2**：混合多种 Denoising 模式

---

## Part VI：解码策略

### 项目 9：构建 Sampling Dashboard

模型输出 Logits，产品输出文字。解码是桥梁。

### 项目 10：实现 Speculative Decoding

用小模型（draft model）提议 tokens，大模型验证加速。

**2026 年变种：**
- **Medusa**：加解码头提议多个未来 token
- **Lookahead Decoding**：无辅助模型，探索候选 n-grams

---

## Part VII：KV Cache 和内存受限推理

### 项目 11：构建 KV Cache

推理时不需要每步都重算过去的 K 和 V。KV Cache 存储它们——这是训练和推理最重要的实践差异之一。

### 项目 12：实现 MQA、GQA、研究 MLA

| 方法 | 特点 |
|------|------|
| MHA | 每个 query head 各自有 K/V head |
| MQA | 跨 query head 共享 K/V，省带宽 |
| GQA | MHA 和 MQA 的折中 |
| MLA | DeepSeek-V2/V3 的低秩 KV 压缩，结合 MoE |

> 到 2026 年，KV-cache 缩减已是主要的架构设计轴之一。

---

## Part VIII：长上下文是系统工程问题

### 项目 13：Sliding Window Attention + Attention Sink 实验

- **Mistral 7B** 推广了 Sliding Window + GQA 组合
- **StreamingLLM** 展示保留早期 attention sink 可稳定长序列生成

### 项目 14：RoPE Scaling、YaRN 插值、记忆机制

- **YaRN**：RoPE 上下文扩展更数据/计算高效
- **Infini-Attention**：压缩记忆机制，无边界的输入长度但有界的内存

---

## Part IX：高效 Attention 和硬件感知建模

### 项目 15：对比 Naive Attention、PyTorch SDPA、FlashAttention

同样的数学运算，命中模式不同，运行时间天差地别。

- **FlashAttention**：减少 HBM 读写
- **FlashAttention-3**：为 H100 优化（硬件调度、异步、FP8）

### 项目 16：理解硬件预算（FLOPs / 带宽 / 内存 / 精度）

**2026 年硬件格局：**
- **NVIDIA Blackwell**：FP4/FP8 推理 + 大 NVLink 域
- **Google Ironwood TPU**：重点在推理
- **AMD MI300X**：192GB HBM3 per accelerator

---

## Part X：Mixture of Experts

### 项目 17：构建双 Expert Router

稀疏 MoE 增加参数量但不激活所有参数。

### 项目 18：复现现代稀疏模型权衡

**2026 年关键 MoE 模型：**

| 模型 | 总参数 | 激活参数 | 特点 |
|------|--------|---------|------|
| DeepSeek-V3 | 671B | 37B | MLA + MoE + 多 token 预测 |
| Llama 4 | MoE | — | Meta 首个 MoE，原生多模态 |
| Qwen3-235B-A22B | 235B | 22B | 开源 MoE |
| Kimi K2.6 | 1T | 32B | 原生多模态 Agentic MoE，256K 上下文 |

---

## Part XI：超越普通 Transformer

### 项目 19：实现 State-Space 或 Linear-Attention 模型

- **Mamba**：选择性 SSM，线性时间序列扩展
- **Mamba-2**：连接 SSM 和 Attention
- **RetNet**：保留机制，训练并行推理递归

### 项目 20：构建 Diffusion-Style 语言模型

- **LLaDA**：从头训练 Diffusion LM，非自回归
- **Dream**：开放 Diffusion LM
- **Mercury** (Inception)：Diffusion LLM，极致生成速度

---

## Part XII：数据才是真正的预训练要素

### 项目 21：构建预训练数据管线

- **FineWeb**：15T tokens，基于 Common Crawl
- **Dolma**：OLMo 的开放语料
- **DataComp-LM**：标准化数据配比实验

### 项目 22：合成数据——生成、过滤、证明它有用

合成数据有用，但也会放大错误、坍缩多样性、污染评估。

---

## Part XIII：Scaling Laws

### 项目 23：训练小/中/大模型，拟合 Scaling Curves

- **Kaplan Style**：平滑幂律关系
- **Chinchilla**：很多大模型训练不足，参数和 tokens 应同比例增加

---

## Part XIV：Post-Training

### 项目 24：Fine-Tune / Instruction-Tune / Preference-Tune

基础模型预测下一个 token，Assistant 跟随指令。

### 项目 25：构建 RLHF / PPO / GRPO / RLVR 实验室

2026 年 RL 对推理模型至关重要：
- **o1**：更多 RL + 更多推理时间 = 更好
- **DeepSeek-R1**：纯 RL 的 R1-Zero + 多阶段管线
- **GRPO (DeepSeekMath)**：替代 PPO，去掉 critic 模型，省显存

---

## Part XV：量化与压缩

### 项目 26：量化模型并评测损伤

| 方法 | 特点 |
|------|------|
| GPTQ | 一次性 post-training 量化 |
| AWQ | 保护小部分重要权重来提高低比特量化 |
| GGUF | llama.cpp 生态的格式标准 |

---

## Part XVI：推理服务系统

### 项目 27：同一个模型跑多个推理栈

| 引擎 | 特点 |
|------|------|
| vLLM | PagedAttention 减少 KV cache 浪费 |
| TensorRT-LLM | 批量推理、量化、多 GPU |
| SGLang | RadixAttention、prefix caching、speculative decoding、解耦服务 |

---

## Part XVII：评估

### 项目 28：构建 Evaluation Harness

- **HELM**：全维评估
- **MMLU**：通用知识和推理基准
- **EleutherAI LM Eval Harness**：开源通用工具

---

## Part XVIII：RAG、工具和 Agent

### 项目 29：从零构建 RAG

RAG = 模型中的参数记忆 + 外部语料的非参数记忆。

### 项目 30：先理解栈，再做 Tool Use 和 Agent

> **关键观点：** Agent 不是假的，但把它当魔法就很脆弱。
>
> - **ReAct**：推理轨迹 + 动作
> - **Toolformer**：从自监督信号学习用 API
> - **DSPy**：LM 管线变成可优化的程序

---

## Part XIX：多模态

### 项目 31：构建 Vision-Language Adapter

- **CLIP**：对比学习图像-文本
- **Flamingo**：冻结视觉+语言模型
- **LLaVA**：视觉指令微调

到 2026 年，Llama 4、Kimi K2.6 等强调原生多模态。

---

## Part XX：可解释性和失败模式

### 项目 32：研究 Circuits、Probes、Sparse Autoencoders

- **Transformer Circuits**：拆解 Attention 和 MLP
- **Anthropic Sparse Autoencoders**：比神经元更可解释的特征

### 项目 33：构建 Red-Team 和安全评估套件

- **Constitutional AI**：原则 + AI 反馈替代直接人工标注
- **Red-teaming**：手动 + 自动化对抗攻击

---

## Part XXI：终极 Capstone

### 项目 34：训练 → 微调 → 量化 → 服务 → 评估 → 文档

连接整个栈。

---

## 12 周落地计划

| 阶段 | 周次 | 内容 |
|------|------|------|
| 表征与 Attention | 1-2 | Tokenizer → Embeddings → 位置编码 → Attention → 单 Block |
| 训练与目标 | 3-4 | 训练 Mini-Former → 对比目标 → Sampling → 归一化 → Ablation |
| 推理系统 | 5-6 | KV Cache → MQA/GQA → Speculative Decoding → 量化 → Serving 基准 |
| 长上下文 / MoE / 数据 | 7-8 | Sliding Window → 上下文扩展 → 玩具 MoE → 真实数据管线 |
| Post-Training + 评估 | 9-10 | SFT → LoRA/QLoRA → DPO → 玩具 RL → Benchmark → Safety |
| Capstone | 11-12 | 训练/微调小模型 → 量化 → 服务 → RAG/Tools → 评估 → Red-team → 发布 |

## 每项目产出标准

1. **实现**：干净的代码 + 测试
2. **Notebook**：一个可复现的实验
3. **图表**：至少 3 张（loss 变化、延迟曲线、Attention 热图等）
4. **失败画廊**：系统在什么情况下挂掉
5. **短文**：学到了什么、什么改变了看法

---

> Likes: 964 | Retweets: 135 | Views: 256K
>
> *整理于 2026-06-22，原文：[@theahmadosman](https://x.com/theahmadosman/status/2058745340895870985)*
