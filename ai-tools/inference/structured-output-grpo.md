---
title: "训练 LLM 生成可靠的结构化输出（Structured Output）—— GRPO 实战"
tags:
  - structured-output
  - GRPO
  - fine-tuning
  - Qwen
  - LLM-training
  - AI-engineering
  - fireworks
date: 2026-06-11
source: "https://x.com/akshay_pachaar/status/2064700531600458093"
authors: "Akshay 🚀 (@akshay_pachaar)"
---

# 训练 LLM 生成可靠的结构化输出

> **来源：** [Training an LLM to Generate Reliable Structured Output](https://x.com/akshay_pachaar/status/2064700531600458093) — @akshay_pachaar

---

你让语言模型输出 JSON，大部分时候没问题。

然后某一次返回就坏了——数字变成了字符串，或者模型在 JSON 外面包了一段解释，解析器直接报错。

这个**小概率失败率**就是全部的问题所在。输出要喂给函数调用或数据库写入，"看起来像 JSON" 和 "就是 JSON" 不是一回事。

下游代码只在它崩了的时候才发现。

**这就是结构化输出（Structured Output）的意义：** 模型返回数据是固定的形状、符合 schema，而不是碰巧读起来对的自由文本。

Agent、工具调用和数据管线现在全靠这个运行。模型写的是给代码执行的东西，不是给人读的东西。

---

## 为什么 SFT（监督微调）会撞天花板

SFT 通过复制样本来学习。给它看正确的完成结果，它就能变得擅长产生看起来像它们的东西。

但**看起来像有效 JSON** 和**就是有效 JSON** 是不同目标。SFT 永远只追第一个。

损失是逐 token 计算的。一个字段类型写错的完成结果，和完美的几乎得分一样。

所以你加更多例子。数字往上走，然后**持平**——因为限制是目标，而不是数据。

---

## 对正确性（Correctness）训练，而非对示例训练

> DeepSeek-R1 展示了另一条路：取代标注管线、偏好对和标注团队——只需要一个 Python 函数来检查答案是否正确。如果你能用代码定义正确性，就不需要那些了。

这就是 **GRPO** 背后的思想。不是从例子中学习，而是从你编写的**奖励函数（reward function）**中学习。

对每个 prompt，模型生成几个候选答案，奖励函数给它们打分，模型被推向分数更高的答案。

---

## 实战：用 GRPO 微调 Qwen3-8B 做 JSON 提取

作者使用 **GRPO** 对 **Qwen3-8B** 进行微调，任务是从发票文本中提取结构化 JSON 字段（vendor、date、amount、currency）。

### 奖励函数设计

奖励函数只做一件事：检查输出是否能解析并匹配 schema。

| 输出状态 | 分数 |
|---------|------|
| 无法解析为 JSON | **0.0** |
| 能解析但不符合 schema | **0.5** |
| 解析 + schema 都通过 | **1.0** |

中间的 0.5 分比看起来更重要。没有它，能解析但字段类型错的输出会和完全垃圾一样得 0 分。**0.5 是训练往上爬的台阶。**

### 数据准备

- 200 条训练 prompt（只提供 prompt，不需要标注过的输出）
- 50 条 eval prompt（模型从未训练过）
- 覆盖不同的 vendor 名、日期格式、金额样式、货币代码

GRPO 不需要标注输出——模型在训练中自己生成完成结果，`score()` 实时打分。

### 基础设施

GRPO 比 SFT 重得多。8B 模型需要 **H200 GPU**，跑数小时。

每一步：为每个 prompt 生成多个完成结果 → 全部打分 → 更新权重 → 重复整个数据集。

Fireworks Training API 处理了推理和训练之间的**同步问题**（这是大多数自定义 RL 都会崩掉的地方）。

关键配置：
- `completions_per_prompt=4` — 组大小，生产环境常用 8~16
- `weight_sync_interval=1` — 每步同步权重，保持 rollout 用确切当前模型

### Qwen3 的坑

Qwen3 默认开启 **thinking 模式**，会在回答前加 `<think>...</think>` 标签。必须：
- 推理时用 `content.split("</think>")[-1].strip()` 去掉
- 训练时在 system prompt 加 `/no-think` 禁止

否则奖励函数读到的是推理文本而不是 JSON，全给 0 分。

---

## 结果

| 模型 | Schema 有效输出率 |
|------|-----------------|
| 基础 Qwen3-8B | **62%** |
| GRPO 微调后 | **82%** |
| GPT-4.1（对照） | **58%** 🔻 |

**微调后的模型超过了 GPT-4.1**，且运行在 Fireworks serverless 端点，token 成本远低于 GPT-4.1。

真正的差距体现在**杂乱的输入**上——通用 prompt 模型开始下滑，而训练过的模型保持稳定，因为它学的是约束本身而不是例子。

---

## 这个方法适用于什么

只要能**用代码检查正确性**的任务：

- SQL 必须能解析
- API 响应必须匹配格式
- 工具调用
- 代码必须通过 lint

> 如果能为输出打分，就能训练模型追求那个分数。
> DeepSeek-R1 在十亿级尺度上证明的，对你的小任务一样成立。

完整代码在 GitHub 仓库中，包含：
- 奖励函数
- 训练配置
- 数据集构建器
- 评估脚本

---

## 🖼️ 配图

![GRPO 训练结构化输出流程图](../image/structured-output-grpo-1.jpg)
*GRPO 训练流程：奖励函数驱动、Qwen3-8B 微调、Fireworks H200 训推同步*

---

*整理于 2026-06-11，来源：https://x.com/akshay_pachaar/status/2064700531600458093*
