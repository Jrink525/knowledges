---
title: "到底什么是 Loop？ Peter Steinberger vs. Boris Cherny 之争"
tags:
  - ai-loop
  - agent
  - claude-code
  - loop-engineering
  - automation
date: 2026-06-21
source: "https://x.com/mvanhorn/status/2063865685558903149"
authors: "Matt Van Horn"
---

# 到底什么是 Loop？Peter Steinberger vs. Boris Cherny 之争

> **来源：** [WTF Is a Loop? Peter Steinberger vs. Boris Cherny](https://x.com/mvanhorn/status/2063865685558903149) by Matt Van Horn (@mvanhorn)
>
> 这是循环工程（Loop Engineering）系列的第一篇，Part 2 见 [mvanhorn-15-loops-part2.md](../ai-tools/patterns/mvanhorn-15-loops-part2.md)

---

## 引子

本周 AI 编程圈出现了一条六字短句，几乎每个人都在引用，但几乎没人能说清楚它到底是什么意思。我 90 秒的研究从 Reddit 找回了 15 个帖子、21 条 X 推文，以及一个令人不安的模式：**AI 编程中最响亮的口号，大多数重复它的人却无法解释。**

> **"这是给你的每月提醒：不要再给 AI 编程代理写提示词了。你应该设计 loop 来提示你的代理。"**
> — Peter Steinberger (@steipete)，2026 年 6 月 7 日

有人问了唯一重要的问题：这在实际中是什么样子？答案是：

> **"没人知道——除了他和 Boris。"**
> — Matthew Berman

这就是真实的故事。不是 loop 是未来，而是一个六字短句获得 220 万浏览量，而力挺它的人却在评论区争它到底是什么意思。

---

## Loop 到底是什么

Boris Cherny（Claude Code 创建者）在 2024 年 9 月以个人项目创建了 Claude Code。现在它背后据称占了 GitHub 所有公共 commit 的近 4%。在 2026 年 6 月 2 日的 Acquired Unplugged 活动上，他给出了 loop 最清晰的定义：

> **"现在，我认为它实际上已经升级到了下一波抽象——我不再给 Claude 写提示词了。我有 loop 在运行。是它们在提示 Claude 并决定下一步做什么。我的工作是写 loop。"**
> — Boris Cherny，WorkOS Acquired Unplugged，2026 年 6 月 2 日

**简单版本：** Loop 是你写的一个小程序，它替你提示代码代理、读取产出、判断是否完成、如果没完成就再次提示。你不再是循环中敲提示词的那个环节。你成为了循环的作者。模型成为了一个子程序。

Boris 的进化三阶段：
1. **手工写代码 + 自动补全** — 一年前
2. **并行运行 5-10 个 Claude 会话，逐个提示** — 之后
3. **现在：完全不再写提示词，写 loop 来提示 Claude，数百个代理读取他的 GitHub、Slack 和 Twitter，决定下一步构建什么**

他的成绩单：
> **"过去 30 天，我对 Claude Code 的 100% 贡献都是由 Claude Code 写的。我合入了 259 个 PR。"**
> — Boris Cherny，2025 年 12 月 27 日

他去年 11 月删掉了 IDE，之后再也没打开过。**但注意**：他并不是说工程师过时了。仍然需要有人决定构建什么、和客户沟通、协调团队。工作没有消失——它升了一个高度，从写代码变成了写那个写代码的东西。

---

## 光谱：从 ReAct 到编排

回复一片混乱，因为"loop"这个词至少藏在五个不同的东西下面。从旧到新：

### Stage 1：学术 while 循环（2022）
ReAct 论文形式化了它：模型推理 → 调用工具 → 读取结果 → 重复直到完成。一个模型，一个循环，人类在旁观看。

### Stage 2：AutoGPT（2023）
给了模型一个目标，让它自己提示自己。以无限旋转什么都不做而闻名。那次失败为"代理是玩具"的观点埋下了种子。

### Stage 3：ralph 循环（2025 年 7 月）
由 Geoffrey Huntley 发布。简单到荒谬——一个 bash 一行命令，不断将同一个提示文件输入代理。真正的创新是**纪律**：每次迭代将上下文重置为一组固定的锚点文件，而不是让对话不断膨胀。Huntley 用大约 297 美元用它构建了一整套编程语言。

### Stage 4：产品化（2026 年春）
Codex 和 Claude Code 都发布了 `/goal` 命令，运行 ralph 循环模式，直到一个小型验证模型确认任务完成。

### Stage 5：真正的编排循环（现在）
这是 Boris 和 Steinberger 实际所指的——真正的全新内容。四件事变了：
1. **Loop 成为工作单元**，而非任务
2. **Loop 开始监督其他 loop**，并发且按计划运行
3. **调度取代了人工启动**——loop 运行在基础设施时间上，而非你的注意力
4. **持久化变得显式**——基于 git 的状态和崩溃恢复（ralph 假设终端一直开着，2026 年版本不这么假设）

> 单代理 ralph 循环已经是老黄历了；多代理编排循环才是新东西。

---

## 它不就是带了个帽子的 cron 吗？

> **"Job 们现在有有趣的改名了。"** — X 回复

这是对整个话题最刻薄的质疑，而且它**对了一半**。是的，调度层就是 cron。Boris 确实是在 cron 上运行的。但如果你的"loop"定义就是定时运行的东西，那 1975 年我们就发明它了，你可以回家了。

**cron 从未有过的**是中间的那部分。Cron 跑一个固定脚本。Loop 跑一个模型，它查看当前状态、决定下一步做什么、做它、检查是否有效、决定是否继续。**决策是 agent 的**，不是你的，也不是硬编码分支。

把它们叠加起来，让一个 loop 调度和监督其他 loop，给它们持久化的共享状态——你就有了 cron 无法表达的东西。诚实的框架是：**loop 不是新魔法，也不只是 cron。Loop 是 cron 加上主体中的决策者**，而有趣的工程是围绕这个决策所做的一切，确保它不会跑进悬崖。

---

## 实际构建一个 Loop 的样子

> **入门是一行命令。** Claude Code 发布了 `/loop`，Boris 自己的示例：

```
/loop babysit all my PRs. Auto-fix build issues, and when comments come in, use a worktree agent to fix them.
```

Boris 的五个自主运行 Opus（数小时到数天）的技巧：
1. 使用 **auto mode** 让 Claude 无需请求批准
2. 使用 **动态工作流** 让 Claude 编排数百或数千代理完成一个任务
3. 使用 **/goal 或 /loop** 推动 Claude 继续直到完成
4. 在云中使用 **Claude Code** 以便能合上笔记本
5. **确保 Claude 能端到端自我验证其工作**

**第五点是 hype 跳过而实践者痴迷的：一个 loop 的可靠性取决于它检查自己工作的能力。**

> 你写的不是步骤。你写的是**意图**和**停止行为**，loop 在每个 tick 提示代理。

深度端是 **Steve Yegge 的 Gas Town**（2026 年 1 月发布）：20-30 个 Claude Code 实例，由一个 Mayor 代理协调，包含跑持续循环的 patrol 代理，状态存储在 git 中，崩溃后工作不丢失。这就是 Trash Panda 在追寻的"监督其他线程的持续编排循环"——已发布且开源。

但研究中最实用的结论是：**一个 loop 的好坏取决于它检查自己的能力。** 增长速度最快的子主题不是编排，而是**验证**。

> "你的代码代理可以快速行动，但坏 commit 也会快速累积。"
> — @DanKornas

一个写代码但没有反馈的开放 loop 是生成自信错误的机器。一个写→运行→读取结果→修正的 loop 才是真正有用的东西。**Loop 不是魔法。它里面的反馈才是。**

---

## 剧情转折：Loop 现在是最贵的部分

> "我今年发布的每个 AI 代理都是一个 for 循环、一次 LLM 调用和一个 JSON 解析的 try/catch。它唯一'代理化'的地方是月末 Anthropic 的账单。"
> — @rohit_jsfreaky

**那个账单不是玩笑。** 本月最引人注目的账单：**Uber 将工程师的 Claude Code 和 Cursor 使用限制在每人每月 1,500 美元**——在四个月内烧完了年度 AI 预算。

> "AI 编程中最贵的东西不再是写代码，而是管理代理循环。"
> — @runes_leo

每个认真的 2026 年 loop 文章都收敛到三个硬性停止条件：
1. **最大迭代次数**
2. **无进展检测**
3. **Token 或美元预算上限**

浪漫版本：你写 loop，一千个代理在一夜之间建起你的公司。
生产版本：你写 loop，而你的大部分工作是确保它们停止。

---

## 不是 Loop，是技能

> Loop 是管道。资产是它调用的技能。

Steinberger 另一个重复出现的观点是：**如果你做某事超过一次，把它变成自动化技能；如果你做困难的事，做完后把它变成技能，这样下次就免费了。**

一个没有可复用技能在其内部的 loop = 对着陌生人做 while(true)。
一个调用精准、经过测试的命名技能库的 loop = 一个能复利的系统。

> "很多人在 Twitter 上翻白眼，但我的耳朵竖起来了。"
> — r/ChatGPTCoding

**所以回答"到底什么是 Loop"：** 别再当循环里的那个环节。写一次 loop，给它值得调用的技能和能自我检查的反馈，设置上限让它能停止，让它在 cron 上运行——而你去决定下一步构建什么。

---

## 关键模式总结

| 洞察 | 说明 |
|------|------|
| Loop = cron + 决策者 | 模型在每个 tick 选择下一步动作，不是硬编码分支 |
| 血统真实 | ReAct(2022) → AutoGPT(2023) → ralph(2025) → /goal(2026春) → 编排循环(现在) |
| 反馈决定一切 | 持续审查和验证门控使 loop 可信 |
| 昂贵资源转移 | 从 token 成本转移到 loop 管理成本 |
| 复用单位是技能 | 调用命名技能的 loop 复利；每次都重新推导的 loop 只烧钱 |

---

## 研究数据

- **Reddit**: 17 个账号 (r/ClaudeAI, r/AI_Agents, r/ExperiencedDevs)，47 个帖子，34k upvotes
- **X**: 21 个账号 (steipete, bcherny, runes_leo)，56 条帖子，175 次转发
- **YouTube**: 4 个频道 (WorkOS, Lenny's Podcast, Y Combinator)，演讲文稿
- **TikTok**: 6 个创作者 (ai.native.founder, nikpolale)，34 个视频
- **Instagram**: 4 个账号 (sequenzy_com, ai.builders)，14 个 reel
- **Hacker News**: 12 个账号，54 个故事，1k 评论
- **GitHub**: 6 个仓库 (gastownhall/gastown, NousResearch/hermes)，steipete 259+ PRs

*数据来自 2026-06-07 的 /last30days 运行*

---

*处理时间：2026-06-21 | 来源：X/Twitter @mvanhorn*
