---
title: "How LLMs Actually Work — LLM 内部原理完全图解"
source: "https://www.0xkato.xyz/how-llms-actually-work/"
author: "0xkato"
published: 2026-06-01
category: "ai-tools"
tags: [LLM, transformer, attention, RoPE, GQA, MoE, architecture]
---

# How LLMs Actually Work — LLM 内部原理完全图解

> 原文：[0xkato](https://www.0xkato.xyz/how-llms-actually-work/)  
> 一篇不堆数学公式的 LLM 内部机制详解，覆盖从 tokenization 到推理生成的全流程。

---

## 全文结构

这篇文章把 LLM（大语言模型）从输入到输出拆成 9 个环节，每个环节独立解释。现代 LLM 绝大部分都是 Transformer 架构的变体，理解 Transformer 就理解了 90%。

---

## 1. Tokenization（分词）—— 文本怎么变成数字

**核心：模型不直接读文字，它读整数 ID。**

- 你的 prompt（提示词） → 分词器 → 一串整数
- 每个整数对应一个词表中的条目（token ID）
- 词表大小通常几万到几十万

**Token 是什么？**
- 不是完整单词，而是**子词（subword）**
- "tokenization" 可能拆成 ["token", "ization"]
- "running" 可能拆成 ["run", "ning"]
- 全单词词表太大（不泛化），字符级词表太小（学得慢），子词居中平衡

**不同模型用不同分词器：**
- GPT 家族：BPE（Byte Pair Encoding）
- LLaMA 家族：SentencePiece
- 选择影响计算量（token 越少 → 计算越少）和多语言覆盖

**经典翻车案例：** 问 LLM "strawberry" 有几个 R？它们以前经常答错。不是因为模型不会数数，而是因为它**不按字母操作**，只按 token 操作——"straw" 和 "berry" 是两个 token。

> **一句话：** 文字输入 → 整数输出。

---

## 2. Embeddings（嵌入）—— 数字怎么获得意义

**核心：一个整数（比如 1024）只是行号，给它意义的是嵌入矩阵。**

- 嵌入矩阵：一个超大表格，每个 token 一行，每行一个向量（一串数字）
- 7B 级模型：每 token 4,096 个数字
- 模型查找对应行，用这个向量代替 token 整数

**神奇的现象：语义相近的 token 向量也相近。**
- "king" 的向量接近 "queen"
- "Paris" 接近 "France"
- 没人告诉模型这么做，它是在训练中自己学会的

**甚至可以做向量运算：**
```
king − man + woman ≈ queen
```

> **注意：** 这时每个 token 都有了含义向量，但还不知道它在句子里的位置。"dog" 在第一个位置和第五个位置，向量是一样的——这是个问题。

---

## 3. Positional Encoding（位置编码）—— 模型怎么知道词序

**核心：自注意力本身没有「顺序」概念，需要注入位置信息。**

**原始方案（Vaswani et al. 2017）：正弦波编码**
- 每个位置有独特的数字模式（位置 1、位置 5、位置 100 各有不同）
- 直接加到 token 的 embedding 上
- 问题：embedding 要同时携带含义和位置信息，容量有限；训练时没见过的位置（比如 2K 以上）泛化差

**现代方案：RoPE（Rotary Position Embeddings, 2021）**
- 不往 token 向量上加位置信息
- 而是**旋转** Query 和 Key 向量，旋转角度取决于位置
- 位置 1 的 token 转一小圈，位置 100 的转一大圈
- 注意力计算时，两个 token 的旋转差 = 它们的距离
- 现在 LLaMA、Mistral、Gemma、Qwen 全在用

**"Lost in the Middle" 问题（Liu et al. 2023）：**
- 模型对长 prompt 的开头和结尾利用得好，中间部分容易丢失
- 所以 prompt 技巧「重要信息放开头」和「结尾重复关键信息」真的有效

> **一句话：** RoPE 用旋转角度编码位置，自然地表达相对距离，不增加参数量。

---

## 4. Attention（注意力）—— Token 之间怎么交换信息

**核心：每一步，每个 token 看其他 token，决定谁对下一个词更重要。**

**三个角色的设计：每个 token 同时扮演三种角色**
- **Query（Q）**：问「我在找什么？」
- **Key（K）**：答「我有什么可以匹配？」
- **Value（V）**：给「匹配上了就传走这个信息」

**匹配过程：**
1. 每个 token 的 Query 和其他所有 token 的 Key 做**点积**（dot product）——衡量两个向量有多对齐
2. 点积得分越高 → 匹配越强
3. **Softmax** 把得分变成权重（加起来 = 1 的概率分布）
4. 用权重对 Value 做加权平均 → 得到新的 token 表示

**举例说明：**
句子 "The cat that I saw yesterday was sleeping."
- 模型处理 "was" 时，需要知道谁是动作主体
- "was" 的 Query 和 "cat" 的 Key → 点积高（模型知道动词需要主语）
- "was" 的 Query 和 "yesterday" 的 Key → 点积低
- Softmax 给 "cat" 高权重，"yesterday" 低权重
- "was" 的新表示主要由 "cat" 的 Value 塑造

**因果掩码（Causal Masking）：**
- GPT 类模型从左到右生成，位置 5 只能看 1-5，不能看 6-8
- 实现方式：未来 token 的得分被压到几乎为 0

**Induction Heads（归纳头）—— Anthropic 2022 年的发现：**
- 某些注意力头专门识别 "A B … A" 模式
- 第二次看到 A 时，回头找到之前 A 后面的 B，然后预测 B 会出现
- 这是**上下文学习（In-Context Learning）**背后的最清晰机制之一

**注意力的致命成本：**
- 每个 token 要和所有其他 token 比较 → prompt 长度翻倍 → 计算量翻**四倍**
- 这就是 FlashAttention、稀疏注意力、线性注意力等研究的驱动力

> **一句话：** Q 找 K，找到后传 V——这是 Transformer 得名的机制。

---

## 5. Multi-head Attention（多头注意力）—— 怎么同时跟踪多种关系

**核心：一个注意力处理不够，语言有很多种关系同时存在。**

- 主谓一致
- 代词指代
- 跨句的长距离引用
- 词序和局部短语

**多头解决：并行跑多个注意力，每个在更小的空间里操作。** 每个并行通道叫一个 head。

**很多人讲错的地方：** 每个 head 不是拿 token 向量的一个「切片」。每个 head 有自己的投影矩阵，把完整向量投影到它自己的小空间。如果有 4,096 维、32 个 head，每个 head 在 128 维空间里操作——但这是**学习出来的视角**，不是固定切片。

**自发的专业化：** 没人告诉每个 head 该做什么。训练中它们自然分化：
- 有的 tracking 语法（动词对宾语、冠词对名词）
- 有的 tracking 代词指代
- 有的是 induction heads（模式识别）
- 有的 tracking 位置模式

**KV Cache（KV 缓存）：**
- 每个 head 生成 token 时要存 Key 和 Value 向量——这样生成新 token 时不用重新算整个 prompt
- 这是 LLM 推理时**最大的内存消耗**
- 长上下文场景尤其严重

**现代标准：GQA（Grouped-Query Attention）**
- 不是每个 head 有自己的 K/V vectors，而是**多个 query heads 共享一组 K/V heads**
- LLaMA-2 70B：64 个 query heads，只有 8 个 K/V heads
- Mistral 7B：32 个 query heads，8 个 K/V heads
- 效果几乎不降，但内存和推理成本大幅降低

> **一句话：** 并行跑多个注意力头，各自学会关注不同关系；GQA 让它们共享 K/V，省内存几乎不掉精度。

---

## 6. Feed-Forward Network（前馈网络）—— 模型的知识存在哪里

**核心：注意力是 token 之间交流，前馈网络是每个 token 独自做进一步处理。**

**三步操作：**
1. **扩展**：把 token 向量放大（经典 4 倍，SwiGLU 模型用不同的倍数）
2. **非线性激活函数**：弯曲输入（防止网络塌缩成单个线性变换）
3. **压缩**：回到原始大小

**为什么非线性这么重要？**
- 两层线性层叠加 = 数学上等价于一层线性层（一百层 = 一层）
- 非线性是阻止这种塌缩的关键
- 没有它，FFN 就没有比单次矩阵乘法更丰富的能力

**激活函数的进化：**
- 原始 Transformer：ReLU
- GPT/BERT：GELU
- LLaMA/Mistral/PaLM：SwiGLU

**FFN 是模型的「记忆仓库」：**
- 稠密 Transformer 里**大部分参数在 FFN，不在注意力**
- FFN 的神经元和特定概念/事实强关联：有的对埃菲尔铁塔相关的文本激活强，有的对编程语言，有的对过去式动词
- **ROME（Rank-One Model Editing）**：可以精准地编辑某个 FFN 权重矩阵，把「埃菲尔铁塔在巴黎」改成「埃菲尔铁塔在罗马」——不用重新训练整个模型

**MoE（Mixture of Experts，混合专家模型）：**
- 前沿模型开始把稠密 FFN 换成 MoE：每层有多个并行的 FFN（叫 experts），加一个小路由器选择哪些 expert 处理每个 token
- Mixtral 8x7B：总共 467 亿参数，但每个 token 只激活约 129 亿
- 让总参数量持续增长，但推理成本不按比例增长

> **一句话：** FFN 管「思考」和「记忆」，MoE 把单个 FFN 换成多个专家以扩大容量而不增加推理成本。

---

## 7. Residual Stream & Layer Normalization（残差流 & 层归一化）—— 怎么训练几百层深的模型

**残差流（Residual Stream）：**
- 注意力和 FFN 的输出通常**不替换**原来的向量，而是**加**到原来的向量上
- 新向量 = 旧向量 + 子模块的输出
- 跨 30、50、100 层，每层的贡献不断累积，而不是覆盖前一层

**为什么重要：**
- 残差连接不是 Transformer 发明的，来自 ResNet（He et al. 2015, 图像识别）
- 它的核心贡献：让梯度有「短路」穿过深层网络——训练信号不会在往回传几十层时消失或爆炸
- 现代可解释性研究中，残差流是核心对象——每个组件、每个注意力头、每个 FFN、甚至最后的 unembedding 都在读和写这个残差流

**层归一化（Layer Normalization）：**
- 没有它，残差流里的数字会爆炸或塌缩到零
- 每个 token 的向量被重新调整到稳定范围

**Post-norm vs Pre-norm：**
- 2017 年原始 Transformer：每个子模块**之后**归一化（post-norm）→ 浅层还行，深层不稳定
- 现代（GPT-2 起、LLaMA、Mistral）：每个子模块**之前**归一化（pre-norm）→ 这是深层模型可训练的关键差异之一

**RMSNorm：**
- LLaMA、Mistral、Gemma、Phi 等现代模型用的简化版
- 原始 Layer Norm 做两件事：① 把向量拉回零均值 ② 重新缩放数值大小
- RMSNorm 去掉第①步，只做缩放——更便宜，效果几乎一样

> **一句话：** 残差连接让深层网络可训练，层归一化防止数值爆炸，RMSNorm 是更便宜的归一化变体。

---

## 8. Next-Token Prediction（下一个词预测）—— 模型实际怎么生成文本

**核心：推理时，模型只看最后一个 token 的最终向量。**

**流程：**
1. 经过所有 Transformer 层后，每个 token 位置都有一个向量
2. 取**最后一位 token** 的向量
3. 通过 unembedding 层 → 每个候选 token 一个得分（logits）
4. Softmax 把这些得分转成概率分布
5. 从分布中采样一个 token → 加入输入序列
6. 重复，直到遇到结束标记

**Logits vs 概率：**
- Logits = 原始得分（可以是任意正负数）
- Softmax 把它们转成加起来 = 1 的概率分布

**解码控制参数：**
- **Temperature（温度）**：控制分布的「锐度」。低温 → 更保守（选概率最大的），高温 → 更多样
- **Top-k**：只从前 k 个最可能的 token 里选
- **Top-p**：从概率加起来到 p 的最小 token 集合里选
- 这就是同一个模型能同时输出很确定和很有创造力的原因

**Speculative Decoding（推测解码）：**
- 一个小模型快速猜接下来几个 token
- 大模型并行验证这些猜测
- 接受符合大模型概率的猜测，不接受就回退
- **2-3 倍加速**，输出质量不变

> **一句话：** 取最后一位的向量 → 算所有候选词的概率 → 采样一个 → 继续，如此循环直到结束。

---

## 9. Architecture vs Trained Weights（架构 vs 训练权重）

**核心：GPT、Claude、Gemini、LLaMA 到底有什么不同？**

**它们共享的东西很多：**
- Tokenization → Embeddings → Positional Encoding → 堆叠的 Transformer 层（每层：Multi-head Attention + FFN）→ Residual Stream → Layer Norm → Next-token Prediction

**真正的差异来自三方面：**
1. **训练权重**：在不同数据、不同规模下学到的不同数字
2. **配置选择**：层数、词表大小、head 数、参数量、是否 MoE
3. **后训练**：指令微调、RLHF、安全控制

**2023-2025 年现代 Transformer 的共识选择：**
- Pre-norm（前置层归一化）
- RMSNorm（简化归一化）
- RoPE（旋转位置编码）
- SwiGLU（激活函数）
- GQA（分组查询注意力）
- 部分超大规模模型用 MoE（混合专家）

**未来方向：**
- Mamba 等状态空间模型是可信的替代方案（尤其极长序列场景）
- 混合架构正在探索中
- 但即使架构改变，**本文覆盖的核心机制（token、embedding、位置编码、注意力、FFN、残差流、归一化、下一个词预测）是所有序列模型都必须解决的问题**——这些是最持久的知识。

---

## 总结

这篇文章最大的价值不是讲「Transformer 有 12 层注意力，乘以 64 个 head」这种表面参数，而是解释了**每个组件解决什么问题**：

| 组件 | 解决的问题 |
|------|-----------|
| Tokenization | 把文本变成模型能处理的整数 ID |
| Embedding | 给整数 ID 赋予语义含义 |
| RoPE | 告诉模型词序（谁在前谁在后） |
| Attention + Causal Mask | 让 token 之间交流，且不能看未来 |
| Multi-head + GQA | 同时追踪多种关系，同时省内存 |
| FFN + MoE | 独立处理信息和存储知识，用专家扩大容量 |
| Residual + Layer Norm | 让几百层深的网络能训练而不炸 |
| Next-token prediction | 用最简单的方式生成文本 |

读懂这个架构，就能读懂绝大多数现代 LLM 论文和模型卡。
