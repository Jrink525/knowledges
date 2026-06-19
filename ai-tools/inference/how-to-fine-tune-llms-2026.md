---
title: "2026 年如何微调 LLM：GRPO + ART + RULER 实战"
tags:
  - llm
  - fine-tuning
  - grpo
  - agent
  - reinforcement-learning
date: 2026-06-19
source: "https://x.com/akshay_pachaar/status/2029212227438518406"
authors: "akshay_pachaar"
---

# 2026 年如何微调 LLM：GRPO + ART + RULER 实战

> **来源：** [How to Fine-Tune LLMs in 2026](https://x.com/akshay_pachaar/status/2029212227438518406) — by akshay_pachaar

---

每个做 LLM Agent 的团队终会撞上同一堵墙。

你写了详细的 system prompt，加了 few-shot 示例，调了 temperature——Agent 还是有 30-40% 的概率搞错。

最要命的是：**它从不从错误中学习。**

## 微调才是破墙的钥匙

用 GPT 或 Claude，你和所有人用的一样——同样的模型、同样的能力、同样的成本，没有竞争壁垒。

但拿一个小的开源模型微调到你专属任务上？它能吊打比它大 100 倍的模型，成本低、延迟小。

多数开发一想到微调就头大：要收集数据集、标注输出、手写 reward function。

**2026 年，已经不一样了。**

GRPO 和 RULER 彻底改变了游戏规则。现在你可以训练 Agent 从经验中真正进步——不需要写一行 reward function，不需要标一条数据。

这篇文章一步步拆解怎么做。

![img-1](../image/how-to-fine-tune-llms-2026-1.jpg)
![img-2](../image/how-to-fine-tune-llms-2026-2.jpg)

---

## SFT vs. 强化微调（RFT）

SFT（监督微调）大家都知道。收集输入-输出对，模型学习模仿它们。

问题在哪？**SFT 教模型说什么，没教怎么成功。**

对 Agent 这种要搜索、调 API、多步推理的东西，模仿不够用。你想要的是**通过试错进步**。

类比一下：

> **SFT = 背书**（记住已知问题的标准答案）
>
> **RL = 在岗培训**（从试错和反馈中学会做事）

这就是**强化微调（RFT）**。你给模型一个奖励信号，让它自己发现最佳策略。

![img-3](../image/how-to-fine-tune-llms-2026-3.jpg)

---

## GRPO 的工作原理

GRPO（Group Relative Policy Optimization，群体相对策略优化）是目前最流行的 RFT 算法。DeepSeek-R1 的推理能力就是它训出来的。

核心思路很简单：**不训练单独的评分模型，而是对同一个 prompt 生成多个回答，让它们互相比较。**

对每个 prompt 的流程：

1. **采样一个群体**：从当前模型生成 N 个回答
2. **评分**：reward function 评估每个回答
3. **组内归一化**：计算每个回答相对于群体平均的「优势」
4. **更新模型**：强化高于平均的行为，抑制低于平均的

GRPO 只需要**相对排名**，不需要绝对分数。回答得分是 0.3、0.5、0.7，还是 30、50、70——完全不重要。**只有排序驱动学习。**

![img-4](../image/how-to-fine-tune-llms-2026-4.jpg)

---

## ART：Agent 强化训练框架

GRPO 很强大，但怎么用到真实的 Agent 上？

**ART（Agent Reinforcement Trainer）** 是一个 100% 开源框架，把 GRPO 带到任何 Python 应用里。

大多数 RL 框架只适合简单的聊天：一个输入、一个输出，完事。**真实的 Agent 完全不一样**——它要搜文档、调 API、多步推理才能出答案。

ART 为此而生，核心能力：

- 原生支持 Tool-Call 和多轮对话
- 与 LangGraph、CrewAI、ADK 集成
- 训练时高效利用 GPU

### 架构

ART 分成两部分：**Client** 和 **Backend**。

**Client** = 你的 Agent 代码所在的地方。它把推理请求发给 Backend，并记录每一步动作到 **Trajectory**（一次 Agent 运行的完整历史）。

**Backend** = 干重活的地方。它用 **vLLM** 做快速推理，用 **Unsloth 驱动的 GRPO** 做训练。每次训练完成后，新的 LoRA checkpoint 自动加载到推理服务器。

### 完整训练循环

```
Client 发送推理请求
  → Backend 生成模型输出
    → Agent 在环境中执行动作（调工具、搜索等）
      → 环境返回奖励
        → Trainer 用 GRPO 更新模型
          → 新 LoRA checkpoint 加载到推理服务器
            → 重复，每一轮模型都比上一轮更好
```

![img-5](../image/how-to-fine-tune-llms-2026-5.jpg)
![img-6](../image/how-to-fine-tune-llms-2026-6.jpg)

---

## RULER：再也不用手写 Reward Function

这是最让人头疼的部分。

定义一个好的 reward function 一直是 RL 里最难的事。训练邮件 Agent 需要标注正确答案，训练代码 Agent 需要测试套件——每个都是独立的工程项目。

**RULER（Relative Universal LLM-Elicited Rewards，相对通用 LLM 诱发的奖励）** 彻底消除了这个瓶颈。它用 **LLM-as-Judge** 来比较多条 Agent 轨迹并排序——**不需要任何标注数据**。

它的有效性来自两个洞察：

- 让 LLM "打 0-10 分" → 结果不一致
- 问 LLM "这 4 次尝试哪个最接近目标？" → 结果可靠得多

刚好 GRPO 只需要相对评分，绝对值无所谓。

### RULER 三步走

1. 对同一个场景生成 N 条轨迹
2. 把它们丢给 LLM Judge，每条打 0-1 分
3. 分数直接作为 GRPO 的奖励

不需要写 reward function。不需要收集标注数据。

![img-7](../image/how-to-fine-tune-llms-2026-7.jpg)

---

## 实战：训练一个会用 MCP 的 3B 模型

作者提供了一个完整的 Jupyter Notebook（点击原文链接获取），目标是：

**输入一个 MCP 服务 URL → 训练一个 3B 模型学会使用它**

Notebook 会自动：
1. 查询 MCP 服务的工具列表
2. 基于这些工具生成输入任务
3. 用 RULER 自动评估 + GRPO 训练

![img-8](../image/how-to-fine-tune-llms-2026-8.png)

---

## 总结：2026 年微调 Agent 的关键技术栈

| 技术 | 做什么 | 为什么重要 |
|------|--------|-----------|
| **GRPO** | 组内相对策略优化 | 不需要单独的评分模型，只需要相对比较 |
| **ART** | Agent 强化训练框架 | 原生支持 Tool-Call、多轮对话 |
| **RULER** | LLM 自动评判奖励 | 不需要手写 reward function，零标注 |
| **Unsloth** | 高效 LoRA 训练 | 训练完自动加载到 vLLM 推理服务器 |
| **vLLM** | 快速推理引擎 | 支持连续 LoRA 热加载 |

**给 Java 工程师的提示：**
- ART 的 Client 部分可以替换成 Spring AI 的 agent，通过 REST API 调用 Backend 的推理服务
- MCP 服务是语言无关的，你可以用 Java 写 MCP Server，然后在 Notebook 里训练 Agent 使用它
- 这套流程跟 Spring AI 的 ChatClient + Tool Calling + RAG 是互补的：Spring AI 做上层编排，GRPO/RULER 做底层模型优化

---

> *Processed on 2026-06-19 from https://x.com/akshay_pachaar/status/2029212227438518406*
