---
title: "Step-By-Step LLM Engineering Projects (2026 Edition)"
tags:
  - llm
  - engineering
  - roadmap
  - projects
  - transformers
date: 2026-05-25
source: "https://x.com/theahmadosman/status/2058745340895870985"
authors: "Ahmad (@TheAhmadOsman)"
---

# LLM 工程实战项目路线图（2026 版）

> **来源：** [@TheAhmadOsman](https://x.com/theahmadosman/status/2058745340895870985)  
> **数据：** 189 👍 · 28 RT · 13K 阅读  
> **核心原则：** Build it → Plot it → Break it → Explain it → Ship the artifact

---

## 核心哲学

阅读 LLM 的理论描述到了一定阶段就不够了。你需要亲手搭建整个技术栈：

> **Tokenizer → Embeddings → Position → Attention → Transformer Blocks → Objectives → Decoding → Cache → Quantization → Serving → Agents**

每个项目遵循同一循环：
1. **Build it** — 在调库之前，自己手写核心实现
2. **Plot it** — 画 loss 曲线、延迟曲线、attention heatmap、routing 直方图、熵曲线
3. **Break it** — 做消融实验：去掉位置编码、关闭 causal mask、过度量化、精简数据、让 router 崩溃
4. **Explain it** — 写一份简短的技术笔记：预期 vs. 实际，什么让你意外，下一步做什么
5. **Ship the artifact** — repo、notebook、博客、demo、benchmark 图表、可复现实验

---

## Part I: 文本变成张量（Text Becomes Tensors）

### 1. 从零构建 Tokenizer

在训练模型之前，你需要决定"世界如何变成符号"。这个决策影响：压缩率、多语言行为、稀有词处理、代码/数学/表情符号、延迟、上下文利用率、模型质量。

- 从 **Byte-Pair Encoding (BPE)** 开始，在小语料上训练一个子词词汇表
- 与 **Unigram / SentencePiece** 风格的 tokenization 做对比
- BPE 之所以成为主流，是因为它优雅地处理了稀有词（退回到字节级）、保持了词汇表大小可控、无需预处理分词

> **实验：** 用不同的 vocabulary size（1K / 8K / 32K）对比同一个语料，看 token 序列长度和压缩率的变化。你会理解为什么 DeepSeek、LLaMA、Qwen 选择了不同的词汇表大小。

### 2. One-hot 向量、学习到的 Embedding、语义几何

Token ID 本身没有意义。当 ID 变成向量时，意义开始出现。

- 构建最简单的 embedding table，在 next-token prediction 任务上学习
- 观察向量空间中语义相似词的距离变化

> **实验：** 训练后在 embedding 空间中找最相似的 5 个邻居，观察语义集群如何形成。

---

## Part II: 位置给 Token 顺序（Position Gives Tokens Order）

### 3. 实现 Sinusoidal、Learned、RoPE、ALiBi 四种位置编码

Attention 本身是排列不变的——去掉位置，"dog bites man" 和 "man bites dog" 会变得太像。

- 原始 Transformer 使用 **sinusoidal** 位置编码
- 更现代的系统通常用 **RoPE**（旋转位置编码）或 **ALiBi**（线性偏置注意力）
- 实现区分并对比它们的外推能力

> **消融实验：** 去掉位置编码做训练，观察模型是否还能学到顺序信息（答案是能学到一些，但远不如有位置编码的版本）。

---

## Part III: Attention 让上下文有用（Attention Makes Context Useful）

### 4. 为一个 Token 手写 Scaled Dot-Product Attention

在实现完整的 Transformer block 之前，先实现单一 query 的 attention：

- 手动计算 Q、K、V
- 做点积 → 缩放 → Softmax → 加权求和

Transformer 用 attention 替代了 RNN 的循环依赖，使得序列级训练可以并行化，同时让每个 token 能注意到其他所有 token。

> **实验：** 可视化 attention 权重矩阵。观察"重要的 token"如何获得更高的注意力权重。

### 5. 扩展到 Multi-Head Attention

不同 attention head 可以学习不同的关系模式。有些 head 擅长局部语法、有些擅长类复制的 inductive copying、有些做分隔符跟踪、有些捕捉长距离依赖。

> **实验：** 冻结训练好的模型，对每个 head 的 attention pattern 做可视化——你通常会发现"语法 head"和"语义 head"的分化。

---

## Part IV: Transformer Block

### 6. 构建一个 Transformer Decoder Block

把所有部件堆起来：

```
Token Embedding → Positional Method → Masked Multi-Head Attention
→ Residual Connection → Normalization → Feed-Forward Network
→ Output Projection
```

现代 decoder block 典型采用 **pre-norm** 结构，使用 **RMSNorm**（LayerNorm 的简化变体），并常用 **gated MLP**（如 SwiGLU）替代最早的 ReLU 式 FFN。

> **笔记：** RMSNorm 简化了 LayerNorm（移除均值中心化），在实践中表现相当甚至更好。SwiGLU 比 ReLU FFN 增加了一个 gating 分支，在小模型上就能看到质量提升。

### 7. 堆叠 Blocks 成为 "Mini-Former"

训练一个很小的 decoder-only 模型在玩具文本上。目的不是构建有用的聊天机器人，而是**理解训练循环**。

> **实验：** 记录训练 loss 曲线，观察随着层数增加，loss 下降的趋势。尝试 1、2、4、6 层的版本。

---

## Part V: 目标函数定义模型学什么（Objectives Define What The Model Learns）

### 8. 对比 Causal LM、Masked LM、Prefix LM、Denoising 四种目标

不同目标函数产生不同的能力：

| 目标 | 代表模型 | 特点 |
|------|----------|------|
| Causal LM（next-token） | GPT 系列 | 自回归，适合生成 |
| Masked LM（填空） | BERT | 双向表示，适合理解 |
| Prefix LM（前缀+生成） | T5 | Encoder-Decoder，统一框架 |
| Denoising（去噪） | BART / SpanBERT | 鲁棒性强 |

> **实验：** 在同一个 tiny 模型上训练三种目标，对比它们在不同任务（分类 vs. 生成）上的表现。

---

## Part VI: 解码将概率变成文本（Decoding Turns Probabilities Into Text）

### 9. 构建 Sampling Dashboard

模型输出 logits → 产品输出文本。解码是中间的桥梁。

- Greedy decoding
- Temperature sampling
- Top-K sampling
- Top-P (Nucleus) sampling
- Beam search

> **实验：** 用不同 temperature（0.1 / 0.5 / 1.0 / 2.0）生成同一 prompt，观察多样性与质量的 trade-off。

### 10. 实现 Speculative Decoding

自回归解码是串行的。Speculative decoding 通过一个小型的 draft model 提前 proposal token，然后由大模型并行验证。

**2026 年的新变体：**
- **Medusa** — 在模型上添加额外的 decoding heads 来 proposal 多个未来 token
- **Lookahead Decoding** — 探索并行的候选 n-gram，无需独立的 draft model

> **实验：** 测量开启/关闭 speculative decoding 的生成吞吐量（tokens/s），对比接受率（acceptance rate）。

---

## Part VII: KV Cache 与内存受限推理（KV Cache And Memory-Bound Inference）

### 11. 构建 KV Cache

在自回归推理中，过去的 K 和 V 不需要每一步都重新计算。KV caching 存储它们。

- **训练 vs. 推理最显著的实践差异之一**
- KV cache 的大小随着序列长度和 batch size 线性增长
- 对长序列推理，KV cache 是主要的内存瓶颈

> **实验：** 监控不同序列长度下 KV cache 的显存占用，画出 growth curve。

### 12. 实现 MQA、GQA，研究 MLA

| 方法 | 策略 | 代表模型 |
|------|------|----------|
| MHA（标准） | 每个 query head 有独立的 K/V heads | 原始 Transformer |
| MQA（Multi-Query） | 所有 query heads 共享 K/V | PaLM |
| GQA（Grouped-Query） | query heads 分组共享 K/V | LLaMA 2/3 |
| MLA（Multi-head Latent Attention） | 低秩 KV 压缩 | DeepSeek-V2/V3 |

**2026 年趋势：** KV-cache 缩减是主要的架构设计 axis。DeepSeek-V2 引入 MLA（低秩 KV 压缩），V3 将 MLA 与稀疏 MoE 结合。

> **实验：** 实现 MQA 并将其与 MHA 对比：测量 KV cache 显存节省和端到端推理速度。

---

## Part VIII: 长上下文是系统问题（Long Context Is A Systems Problem）

### 13. 构建 Sliding-Window Attention 与 Attention-Sink 实验

长上下文不是改个配置文件里的数字就能解决的。模型可能：
- 丢失信息（lost in the middle）
- 过度关注不相关的 token
- 在长序列上性能崩塌
- 变得过于昂贵

- **Mistral 7B** — 流行化了 sliding-window attention + GQA 的组合
- **StreamingLLM** — 发现保留早期"attention sink" token 可以稳定超长序列推理

> **实验：** 用 "needle-in-a-haystack" 测试评估模型在不同上下文长度下的检索准确率。

### 14. 通过 RoPE Scaling、YaRN、Memory 机制扩展上下文

上下文扩展通常组合使用：位置插值 + 微调 + 高效 attention + 评估。

- **YaRN**（Yet another RoPE extensioN method）证明基于 RoPE 的上下文扩展可以是数据和计算高效的
- 对比 Linear、NTK-aware、YaRN 三种 RoPE scaling 方法

---

## Part IX: 高效 Attention 与 Hardware-Aware 建模

### 15. 对比 Naive Attention、PyTorch SDPA、FlashAttention

同样的数学运算，不同的内存访问模式会导致完全不同的运行时性能：

| 方法 | 核心思想 | 加速比（相对 naive） |
|------|----------|---------------------|
| PyTorch SDPA | 融合 kernel | 2-3x |
| FlashAttention | 分块计算，减少 HBM 读写 | 5-10x |
| FlashAttention-2 | 优化 thread block 调度 | 10-15x |

> **实验：** 在相同的输入上运行三种实现，对比延迟和显存占用。

### 16. 学习硬件预算：FLOPs、带宽、内存、精度

2026 年的 LLM 工程深受硬件约束：

- **NVIDIA Blackwell** — 强调 FP4/FP8 推理和大 NVLink 域
- **DGX B200 级别系统** — 巨大的 HBM 容量和带宽
- 理解 **compute-bound vs. memory-bound** 的区别对选择推理引擎至关重要

> **项目：** 为你的 GPU 计算一次理论算力天花板（TFLOPS）和内存带宽天花板，然后对比实际推理和训练能达到的利用率。

---

## Part X: Mixture of Experts

### 17. 构建 Two-Expert Router

Sparse MoE 增加了参数数量而不激活每个 token 的所有参数。

- **Switch Transformer** — 展示了稀疏专家路由可以高效扩展模型容量
- 实现一个两专家路由：
  - Router 决定每个 token 去哪个专家
  - 专家本身是独立的 FFN
  - 需要辅助 loss 来平衡负载（避免所有 token 都去同一个专家）

> **实验：** 故意移除 load balancing loss，观察 router 崩溃（所有 token 流到同一个专家）。

### 18. 复现现代 Sparse-Model 的 Trade-off

2026 年的前沿和开源系统大量使用稀疏激活：

| 模型 | 总参数 | 激活参数 | 特色 |
|------|--------|----------|------|
| DeepSeek-V3 | 671B | 37B/token | +MLA + 无辅助 loss 负载均衡 |
| Kimi K2.6 | 1T | 32B/token | 原生多模态 Agent MoE，256K 上下文 |

> **实验：** 计算稀疏模型的"效率比"：激活参数比总参数越小，效率越高。但也需要量化负载均衡带来的额外开销。

---

## Part XI: 超越 Vanilla Transformers

### 19. 实现 Toy State-Space 或 Linear-Attention 模型

Transformer 占主导地位，但并非唯一的序列架构：

- **Mamba** — 选择性状态空间模型，线性时间序列扩展，高吞吐量
- **Mamba-2** — 改进的 SSM 架构，更强的理论连接
- **Gated Linear Attention** — 结合门控机制和线性 attention

> **实验：** 在相同数据量下训练一个 tiny Transformer 和一个 tiny Mamba，对比 loss 下降曲线和推理速度。

### 20. 构建 Diffusion-Style 语言模型 Toy

自回归生成不是唯一的解码范式：

- **LLaDA** — 从头训练了一个扩散式语言模型，使用 masking + denoising
- 挑战了"高质量语言模型必须是自回归的"这一假设

> **实验：** 实现一个极简版（序列长度 64，词汇表 128）的 diffusion LM，对比生成质量 vs. 自回归基线。

---

## Part XII: 数据才是真正的预训练基础

### 21. 构建预训练数据 Pipeline

数据质量是整个技术栈中影响最大的部分之一：

- **FineWeb** — 从 Common Crawl 构建的 15T token 数据集，展示了精心选择的过滤和去重策略带来的收益
- 实现数据清理流程：去重（MinHash）、质量过滤（classifier-based）、PII 移除

> **实验：** 在过滤前和过滤后的数据上训练同一模型，对比 loss 和 benchmark 分数。

### 22. 合成数据：生成、过滤、证明其价值

合成数据能发挥作用，但必须是有针对性、经过过滤、诚实评估的：

- **phi-1** — 小模型在高质量"教科书风格"合成代码数据上训练就能表现惊人
- 关键原则：合成不是万能药，用对了可以，用错了有害

> **实验：** 用 GPT-4 生成 10K 条数学问答对，人工验证 100 条评估准确率。对比加入/不加合成数据训练的效果。

---

## Part XIII: Scaling Laws 与容量

### 23. 训练 Tiny / Small / Medium 模型，拟合 Scaling Curves

Scaling laws 量化了 loss 如何随模型大小、数据大小、计算量变化：

- **Kaplan scaling laws** — 展示了多个数量级上的平滑幂律关系
- **Chinchilla** — 提出在给定计算预算下，模型和数据量应该按比例缩放（20 tokens / parameter）

> **实验：** 训练 3-5 个不同规模的模型（如 10M / 30M / 100M / 300M 参数），记录 loss 并拟合 scaling curve。检查你的曲线是否符合 Kaplan 和 Chinchilla 的预测。

---

## Part XIV: Post-Training 将 Base Model 变成 Assistant

### 24. Fine-tune、Instruction-tune、Preference-tune

Base model 预测文本，assistant 遵循指令。

- **InstructGPT** — 展示人类反馈微调可以让模型比单纯扩大预训练模型更对齐用户意图
- **DPO** — 简化 RLHF，直接优化偏好对，无需显式 reward model
- **LoRA / QLoRA** — 参数高效的微调方法

> **实验：** 用 LoRA 在 Alpaca 数据集上微调一个 7B 模型，对比微调前后对常见指令的回复质量。

### 25. 构建 Toy RLHF / PPO / GRPO / RLVR 实验室

强化学习在推理模型中变得特别重要：

- **OpenAI o1** — 展示了更多的强化学习 + 更多推理时计算可以持续提升性能
- **DeepSeek-R1** — 展示了纯 RL（无需 SFT）可以催生推理能力
- **GRPO（Group Relative Policy Optimization）** — DeepSeek 引入的分组相对策略优化

> **实验：** 在数学推理任务上对比 GRPO 和 PPO 的收敛速度和最终表现。实现一个 toy reward model。

---

## Part XV: 量化与压缩（Quantization And Compression）

### 26. 量化模型并测量损失

量化不是"把它变小"。它改变了数值行为、延迟、内存带宽，有时还有模型质量。

| 方法 | 位宽 | 特点 |
|------|------|------|
| GPTQ | 4-bit/3-bit | 一次性后训练量化，适合大规模模型 |
| AWQ | 4-bit | 保护少量显著权重以提升低比特精度 |
| GGUF | 多种 | 广泛使用的格式，支持 llama.cpp |

> **实验：** 对同一模型做 FP16 / INT8 / INT4 三种精度，对比 benchmark 得分和推理速度。量化后质量下降了多少？推理速度提升了多少？画出 trade-off 曲线。

---

## Part XVI: Serving 系统

### 27. 通过多个推理引擎 Serve 同一模型

LLM serving 是一个独立的学科：

| 引擎 | 特色 |
|------|------|
| **vLLM** | PagedAttention 减少 KV cache 内存浪费 |
| **TensorRT-LLM** | 飞行中批处理、paged attention、FP8 |
| **llama.cpp** | 单机 CPU/GPU 混合推理 |
| **SGLang** | 结构化生成语言 + RadixAttention |

> **实验：** 在同一个 GPU 上通过不同引擎 serve 同一个模型，对比延迟、吞吐量和显存占用。

---

## Part XVII: 评估终结猜测（Evaluation Stops Guessing）

### 28. 构建 Evaluation Harness

如果你不能测量模型，你就无法改进它。

| 基准 | 测量内容 |
|------|----------|
| **MMLU** | 多任务语言理解 |
| **HELM** | 精确性、校准度、鲁棒性、公平性、毒性、效率 |
| **HumanEval / MBPP** | 代码生成 |
| **GSM8K / MATH** | 数学推理 |

> **实验：** 实现一个 evaluation harness，自动在 MMLU 和 HumanEval 上评估你的模型。确保实现可重复——这是最重要的实验基础设施。

---

## Part XVIII: 检索、工具与 Agent（作为 Capstone）

### 29. 从零构建 RAG

RAG 将模型的参数化记忆与外部的非参数化记忆结合起来：

- 实现完整的 RAG pipeline：文档分块 → embedding → 向量检索 → 重排序 → prompt 注入
- 对比不同的检索策略（稀疏 vs. 密集，BM25 vs. 向量搜索）

> **实验：** 构建一个 RAG 问答系统，测量不同 chunk size / overlap / top-k 下的检索召回率和最终回答准确率。

### 30. 只有在理解 Stack 之后，再构建 Tool Use 和 Agent Loops

Agent 不是假的，但当被当作黑魔法时，它们是脆弱的：

- **ReAct** — 交错推理轨迹和行动，提高任务解决能力和可解释性
- **Toolformer** — 模型自己学习何时调用什么工具

> **关键教训：** 先理解底层基础设施（tokenization → attention → KV cache → serving → evaluation），再构建 agent。wrapper 会隐藏模型真正在做什么。

---

## Part XIX: 多模态 LLM

### 31. 构建 Tiny Vision-Language Adapter

2026 年的 LLM 越来越多地消费文本、图像、音频、视频和结构化工具有输出：

- **CLIP** — 对比图像-文本预训练的威力
- **Flamingo** — 连接冻结的视觉和语言模型与 trained connectors

> **实验：** 在预训练的视觉 encoder（如 CLIP ViT）和语言模型之间训练一个简单的 adapter，构建一个小型多模态问答系统。

---

## Part XX: 可解释性与失败模式

### 32. 研究 Circuits、Probes、Sparse Autoencoders

机械可解释性试图理解模型内部实际计算了什么：

- **Transformer Circuits（Anthropic）** — 将 attention 和 MLP 分解为更可解释的组件
- **Sparse Autoencoders** — 学习模型激活的稀疏分解
- **Logit Lens** — 查看每一层的输出 logits，观察信息如何在层间传递

> **实验：** 对一个小模型应用 Logit Lens，观察不同层对最终预测的贡献。你会发现某些层在特定 token 位置承担了主要信息负载。

### 33. 构建 Red-Team 和安全评估套件

随着模型越来越强大，安全评估成为工程的一部分：

- **Constitutional AI** — 使用一套书面原则 + AI 反馈来减少对人类标注的依赖
- **Red-teaming** — 系统性地寻找模型的对抗性失败模式

> **实验：** 构建自动化的 red-teaming pipeline，给模型发送对抗性 prompt，分类并统计失败模式。

---

## Part XXI: 最终 Capstone——构建完整的小型 LLM 系统

### 34. 训练、微调、量化、服务、评估、记录一个模型

最终项目应该连接整个技术栈：

1. **训练/微调**一个小型模型（如 1B 参数级别）
2. **Model SFT → DPO** 对齐
3. **量化**到 INT4
4. **Serve**（vLLM 或 llama.cpp）
5. **添加 RAG + 工具调用**
6. **评估**（MMLU, HumanEval）
7. **Red-team** 安全测试
8. **发布完整的 write-up**——代码、图表、失败的实验、学到的教训

---

## 12 周学习计划

| 周次 | 聚焦 | 项目 |
|------|------|------|
| 1-2 | 表示与注意力 | Tokenizer、Embeddings、位置编码、Attention、Masking、Multi-Head Attention、单 block Transformer |
| 3-4 | 训练与目标 | 训练 mini-former、对比目标函数、采样工具、归一化与激活函数、首次消融实验 |
| 5-6 | 推理系统 | KV Cache、MQA/GQA、Speculative Decoding、量化、Serving Benchmark |
| 7-8 | 长上下文、MoE、数据 | Sliding-window attention、上下文扩展测试、toy MoE、数据 pipeline |
| 9-10 | Post-Training 与评估 | SFT、LoRA/QLoRA、DPO、toy RL、Benchmark Harness、安全评估 |
| 11-12 | Capstone | 训练/微调小模型 → 量化 → Serve → RAG/Tools → 评估 → Red-team → 发布完整 write-up |

> 精确的时间表不如循环重要：**Build → Plot → Break → Explain**

---

## 每个项目完成后发布的 5 个产物

1. **Implementation** — 带测试的干净代码
2. **Notebook** — 一个可复现的实验
3. **Plots** — 至少 3 张展示行为的图表
4. **Failure Gallery** — 系统崩塌的示例
5. **Write-up** — 你学到了什么，什么改变了你的想法

> 不要只发"我实现了 attention"。发 heatmaps。发 mask bug。发 entropy curves。发 latency charts。发 repetition loops。发 expert-routing collapse。发量化损伤的 token 案例。这就是基础积累的方式。

---

## 心态

- 不要在理论上永远卡住。但也不要混淆 demo 和理解。
- **Agent framework** 可以隐藏模型。**Serving framework** 可以隐藏 cache。**Benchmark** 可以隐藏数据泄露。**产品**可以隐藏失败模式。**Wrapper** 可以隐藏"模型其实在做一件简单的事情"的事实。
- 基础消除了隐藏的空间。
- 学习 tokenization → embeddings → position → attention → residual streams → normalization → objectives → sampling → KV cache → long context → MoE → data scaling → post-training → quantization → serving → evaluation。
- **然后**构建 agents、产品、公司、实验室。
- 但要把它们建立在 bedrock 上。

---

> *"Your future self will thank you."*  
> — Ahmad

---

*整理于 2026-05-25，来源：[@TheAhmadOsman](https://x.com/theahmadosman/status/2058745340895870985)*
