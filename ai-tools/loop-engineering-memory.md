---
title: "Loop Engineering 的底层是记忆工程"
tags:
  - AI-Agents
  - loop-engineering
  - memory
  - context-engineering
  - agent-systems
date: 2026-06-17
source: "https://x.com/mem0ai/status/2067305118891163833"
authors: "mem0"
---

# Loop Engineering 的底层是记忆工程

> **来源：** [Loop Engineering Works On Memory](https://x.com/mem0ai/status/2067305118891163833) — mem0

![cover](../image/loop-engineering-memory-cover.jpg)

Peter Steinberger (@steipete) 最近发推说：「**你不应该再给编程 agent 写 prompt 了。你应该设计循环（loops），让循环提示你的 agent。**」

Boris Cherny（在 Anthropic 负责 Claude Code）说得不同：「我不再给 Claude 写 prompt 了。我的工作是写循环。」（[来源](https://thenewstack.io/loop-engineering/)）

随之而来的讨论给这个思路起了个名字：**Loop Engineering。**

正如 Addy Osmani 所说，「Loop engineering 是在取代你自己作为给 agent 写 prompt 的人。你设计一个替你写 prompt 的系统。」（[来源](https://addyosmani.com/blog/loop-engineering/)）你不再是打字发 prompt 的人，你构建那个代替你做这件事的东西。

这不是理论。**Cursor** 把几百个 agent 指向一个项目让它们跑：某次构建接近一周，在数千个文件中产出了超过一百万行代码。Cherny 说他大多数晚上有「几千个子 agent」在做深层次工作。工作从「打下一条 prompt」变成了**「设计写 prompt、检查工作、决定下一步的系统。」**

但几乎所有关于 loop engineering 的分析都忽略了关键一点：**这些循环失败不是因为模型不够聪明。它们失败是因为模型忘记了。** 一个长期运行的循环的约束条件不是智能、工具或 prompt——是记忆。

---

## Loop 的构成

人们已经形成了一套递进路线：

**Context Engineering → Harness Engineering → Loop Engineering**

- **Context**：放进窗口的内容
- **Harness**：包裹单次 agent 运行的一切（工具、护栏、调用框架）
- **Loop**：更高一层——外部系统，让 agent 持续运行、生成帮手、验证输出、决定下一步

每个循环都走过同样的五个阶段：**发现 → 规划 → 执行 → 验证 → 迭代**

Osmani 列出的五个组件：
- **自动化**（/loop、/goal、cron）触发发现
- **Git worktrees** 防止并行 agent 互相冲突
- **Skills（SKILL.md）**承载项目知识
- **MCP 连接器**让循环在真实工具中行动
- **子 agent** 分离制作与检查

循环有两种形态：**单 agent 与 fleet**；两种气质：**开放式**（自由漫游，燃烧 token）和**封闭式**（有界路径，每步有评估门）。

最简参考实现是 Geoffrey Huntley 的 Ralph Loop：`while :; do cat PROMPT.md | claude-code; done`——每次迭代重置 agent 上下文到固定文件集，停止决策交给外部检查。

**这个重置就是关键信号。设计假设 agent 的上下文内记忆是一次性的。任何需要跨越迭代存活的内容，必须活在别处。**

---

## Loop 在哪里断裂，以及为什么每次断裂都是记忆失败

长期运行 agent 的失败模式现在已经很清楚了，而且它们彼此呼应——每次都是 agent 因为某些东西掉出了上下文而丢失主线。

### 上下文腐败（Context Rot）
性能随着窗口填满而下降。一致的观察是 agent 保持连贯性约 **20–30 轮**，然后开始幻觉边界事实、误用早期假设、固执于不再匹配现实的结论。一个循环跑几千轮。除非状态被主动移出上下文，它永远走在这条曲线的错误一侧。

### 西西弗斯陷阱（The Sisyphus Trap）
长流水线展示三种关联失败：
- **细节丢失**：忘记确切的文件路径和参数
- **目标漂移**：丢失迭代次数和停止条件
- **灾难性遗忘**：经过足够多的修剪循环后，agent 忘记了自己的流水线

循环继续推石头，继续忘记它已经推过了。

### 自我强化（Self-reinforcement）
因为循环会重新消化自己的之前输出，一个早期漏过的错误会被后续每轮当作事实对待。错误变得内部一致，每轮都更难祛除。坏记忆不只是丢失信息——它把错误洗钱成事实。

### 重复工作
粗暴版本：模型忘记了，在不该结束时宣布「任务完成」，然后重新引入它在九步前修复过的 bug。

这些不是边缘报告。@cursor_ai 公开运行着最雄心勃勃的循环，从另一面指出了同一个敌人：「我们仍然需要周期性重新开始来对抗漂移和隧道视野」，并观察到未协调的 agent 陷入「长时间无进展的瞎忙」。他们的共享状态修复本身就是一个记忆纪律——**乐观并发控制**，agent 自由读取状态，但如果状态自上次读取后已变更，则写入失败。

再看一遍列表：**漂移、遗忘、重吃错误、重复已完成的工作。** 没有 prompt 能修复这些。它们是同一个 bug：循环跑赢了它的记忆。

---

## 为什么 Loop 让记忆比之前任何事都难

你不能通过往上下文里塞更多东西来解决这个问题。三个原因：

**第一，窗口有限，自动修复有损。**
压缩会总结历史以腾出空间，但它常规性地丢弃 agent 后来需要的细节。LongMemEval（持续聊天记忆的基准测试）发现，商业助手在长期记忆任务上相对于短上下文表现**下降约 30%**。所以循环面临强迫选择：留着一切看质量腐烂，或修剪掉然后丢失需要的东西。

**第二，循环达到的 token 量级，连好的外部记忆也会退化。**
标准记忆基准测试接近 1.5M tokens 就封顶了；一个多周循环轻易超过它。Mem0 发布了 BEAM 基准测试中这个量级的唯一记忆结果：1M tokens 时 64.1 分，10M tokens 时 48.6 分。循环运行的量级是记忆系统最弱的量级——而几乎没人在这个量级上做基准测试。

**第三，回忆 ≠ 使用。**
MemoryArena 显示，接近饱和召回基准的系统在实际记忆需要指导行动时仍然失败。这正是循环的要求：不是「你能回忆起第 12 次尝试吗」，而是**「给定第 1 到 46 次尝试，第 47 次你该做什么？」**

而且它花钱。实操分析显示一个单 agent 循环 50,000–200,000 token，fleet 级 500,000–2,000,000 token，定时循环每周数百万 token。上下文就是 token，token 在每次调用时计费。Cherny 的规则「保持上下文精简到模型还能思考」和 token 账单是同一个洞察的两面。

---

## 实践中怎么做

修复方案是统一的，而且它们全都是**记忆工程（Memory Engineering）**。

### 锚文件体系
稳定的锚文件组合已经形成：
- **VISION.md**：目标
- **CLAUDE.md / AGENTS.md**：规则
- **PROMPT.md**：每轮指令
- **MEMORY.md**：积累的知识
- **SKILL.md**：可复用流程

第 47 次运行读第 1 到 46 次运行写的东西。

### 前沿做法
前沿将记忆从被动文件变为循环中的主动步骤。

**Cloudflare Agent Memory** 在压缩时介入：不丢弃上下文，而是提取和去重值得保留的事实，让持续数周的 agent 积累记忆而不是丢失它。

研究走得更远：**「记忆即行动」（MemAct）**训练 agent 在任务进行中将编辑自己的工作记忆作为刻意行动，报告平均上下文长度**减少 51%**，一个 14B 模型匹敌约 16 倍大的模型。方向很明确：**记忆整理（Memory Curation）成为循环的一个主动动作。**

---

## 更大的循环：让复利发生的是记忆

把视野从编程 agent 拉远，同一个结构出现在公司的规模。

Satya Nadella 一直在描述**「模型之上的学习循环，人类资本和 token 资本在其中复利增长」**——公司把它的工作流和判断力变成一个每次使用都会改进的系统。「这个循环成为公司的新 IP，」他写道。「我把它看作爬山机器。而且和大多数资产不同，它在复利增长。」

让它复利的是记忆。**一个没有持久记忆的循环无法学习——它只能重复。** 无人类方向，计算就是在原地打转。

记忆把一个循环从圆圈变成螺旋——**攀升而非重复**——因为每轮都写下了下一轮可以构建的持久内容。

---

## 如何落地，以及 Mem0 的位置

如果你在构建一个循环，把记忆当作一等公民对待，而不是事后才贴上的 MEMORY.md。

四个规则：

1. **分离工作记忆与持久记忆。** 每次迭代将 agent 上下文重置为精简锚文件。所有必须跨越迭代存活的内容放在窗口之外。

2. **每次通过后写入，每次通过前召回。** 不读自己历史的循环会重复历史。

3. **让召回是语义的，而不是一个增长的文件。** 一个扁平 MEMORY.md 会腐烂、膨胀上下文、只能匹配关键词。超过几次运行后，你需要一个按意义返回记忆、原地更新事实的存储。

4. **用不同的 agent 做验证，并持久化裁定结果。** 制作者评判自己的作品太仁慈，而检查者的判断是下次通过需要的记忆。

规则三是一个专用层发挥作用的地方。用 Mem0 的 SDK（v3 API），两行调用：`add(memory)` 和 `search(query)`。通过 `user_id`、`agent_id`、`run_id` 做范围限定，防止 fleet 之间交叉污染。

如果 agent 把记忆作为工具调用而非由你的代码驱动，也不限于 SDK——Mem0 还提供了 MCP 服务器、Claude Code 插件、OpenClaw 插件、Hermes 提供者，以及 LangGraph/CrewAI 等框架集成。可托管使用或开源自托管。

**为什么它比扁平文件更适合循环：**
- 多信号检索返回与此轮迭代相关的记忆，而非最近一条
- 事实原地更新而非永远追加
- 在长期循环实际达到的 1M–10M token 量级上经过测量

重点不是供应商。重点是：**一旦你的循环运行超过一个上下文窗口，它的可靠性就是一个记忆问题。而一个扁平文件不是记忆系统。**

---

## 结论

**Loop Engineering 是标题，但 Memory 是机制。** 循环给了 agent 跨越时间的持久性；记忆给了它跨越遗忘的持久性。

做好记忆层——持久、外部、语义、经过整理——循环就能连续数天奔向真实目标，每轮都变更好。做不好，没有 loop 设计能救你：agent 漂移、重复已完成的工作、把早期错误洗成真理、按全价付费重活第一天。

这个术语是新的，还没有完全定论。有人叫 Agent Loop Design，OpenAI 把相邻想法归在 Harness Engineering 下，理性的人说它是自 2022 年 ReAct 以来 agent 循环的简单重新命名。但命名之争之下的主张是成立的。

**当 agent 从单轮询问走向长期运行的循环时，难题不再是 prompt——而是记忆。**

Loop Engineering 底层，是 Memory Engineering。

---

> *本文来自 mem0 的 In Context 系列博客。mem0 是一个面向 LLM 和 AI agent 的开源智能记忆层，提供跨会话的长期、个性化、上下文感知交互。*

### 参考资料

- [Peter Steinberger (@steipete)](https://x.com/steipete)
- [Boris Cherny: "I just write loops" — The New Stack](https://thenewstack.io/loop-engineering/)
- [Addy Osmani: Loop Engineering](https://addyosmani.com/blog/loop-engineering/)
- [Cobus Greyling: Loop Engineering](https://cobusgreyling.substack.com/p/loop-engineering)
- [Cursor: Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents)
- [Geoffrey Huntley: Ralph Loop](https://ghuntley.com/ralph/)
- [Context Rot in AI Coding Agents — MindStudio](https://www.mindstudio.ai/blog/context-rot-ai-coding-agents-how-to-prevent)
- [Cloudflare: Introducing Agent Memory](https://blog.cloudflare.com/introducing-agent-memory/)
- [MemAct: Memory as Action — arXiv:2510.12635](https://arxiv.org/abs/2510.12635)
- [MemoryArena — arXiv:2602.16313](https://arxiv.org/abs/2602.16313)
- [LongMemEval — arXiv:2410.10813](https://arxiv.org/abs/2410.10813)
- [Mem0 BEAM Benchmark](https://mem0.ai/blog/what-is-beam-memory-benchmark-the-paper-that-shows-1m-context-window-isnt-enough)
- [Mem0 Docs & Quickstart](https://docs.mem0.ai/platform/quickstart)
- [Mem0 Open Source](https://github.com/mem0ai/mem0)

*Processed on 2026-06-18 from https://x.com/mem0ai/status/2067305118891163833*
