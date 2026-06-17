---
title: "如何为你的 Skill 构建自改进循环"
tags:
  - agent
  - loop
  - skills
  - self-improvement
  - ai-engineering
date: 2026-06-17
source: "https://x.com/zachlloydtweets/status/2066908445425496348"
authors: "Zach Lloyd (Warp)"
---

# 如何为你的 Skill 构建自改进循环

> **来源：** [Zach Lloyd (@zachlloydtweets) on X](https://x.com/zachlloydtweets/status/2066908445425496348)

![封面图](../image/self-improvement-loop-1.jpg)

最近关于用"循环（loops）"驱动 Agent 的讨论很多，但也伴随着一些疑问——"循环到底是什么"？

我不能代表所有人，但我想展示一个用 **Skills 和云端 Agent** 实现自改进循环的实操方法。

**核心思想**：Agent 可以根据外部反馈，随时间推移自动提升自身 Skill 的质量。本文的例子包含一个人工反馈步骤；但如果你有清晰的量化目标，同样可以用自动评分器替代。

## 具体场景：Issue 分类

假设 Skill 做的是 Issue 分类——把新 issue 归入几个桶：`ready-to-implement`（已就绪可实施）、`duplicate`（重复）、`needs-info`（需要更多信息）。这个模式也适用于代码审查 Skill、Bug 修复 Skill、事故响应 Skill 等。

你需要搭建**两层循环**：

1. **内层 Agent 循环**：实际执行 Skill 的地方。对于 Issue 分类来说，你可以手动运行，更常见的是与任务跟踪系统集成——每次有新 Issue 提交就自动触发。每次执行都会记录到某个地方：文件、Agent trace、或 Slack/GitHub 的外部交互记录。

2. **外层 Agent 循环**：一个按计划定时运行的 Agent，**观察**内层对 Skill 的使用情况。它的工作是查看内层 Agent 的所有执行记录，根据这些执行的表现来调整 Skill。由于 Skill 本质上就是文件，它应该根据历史用户反馈生成 diff 来改进 Skill。

**实现平台**：Zach 使用 Warp + Oz（Warp 的云端 Agent 平台）来实现，但方法可以推广到其他平台。GitHub Issues 作为 Issue 跟踪系统。

> 示例仓库：[GitHub 上的 Skills 与 GitHub Workflows](https://github.com/warpdotdev/self-improvement-loop)

---

## 第一步：搭建内层 Agent 循环

内层循环使用一个 **GitHub Action**，每次有新 Issue 创建时触发。

流程：
1. GitHub Action 通过 Oz 调用云端 Agent
2. 云端 Agent 同步仓库，从 GitHub 拉取 Issue 内容
3. 尝试分类并打标签

效果：每当新 Issue 进来，云端 Agent 运行分类 Skill，自动打上对应标签（如 `ready-to-implement`）。

---

## 第二步：搭建外层自改进循环

假设人工审阅者不同意 Agent 的分类结果。

具体场景：审阅者将标签从 "ready-to-implement" 改成 "needs-info"，并在 Issue 评论中说明原因——"因为不确定是否应该为新功能添加配置项"。

**外层循环的妙处**：
1. 外层 Agent 每天运行一次
2. 查看所有已分类的 Issue
3. 发现有人工修改标签并给了理由
4. 通过编程 Agent 运行改进 Skill，生成 diff 来更新内层分类 Skill
5. diff 合并后，自动反馈回内层循环

下一次内层 Agent 运行时，Skill 的表现就会更好。

---

## 核心模式

```
┌──────────────────────────────────┐
│  外层循环 (每天运行)              │
│  ┌────────────────────────────┐  │
│  │ 观察内层执行记录            │  │
│  │ 发现人工修正 → 生成 diff    │  │
│  │ diff 合并 → Skill 更新      │  │
│  └────────┬───────────────────┘  │
│           ↓ 反馈回内层            │
│  ┌────────┴───────────────────┐  │
│  │ 内层循环 (Issue 触发)      │  │
│  │ 执行 Skill → 分类 Issue    │  │
│  │ 记录 trace → 等待外层评估  │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

- **Skill 就是文件**——修改 Skill 本质上就是修改配置文件/Prompt/工具定义
- **外层 Agent 就是编程 Agent**——它能读取反馈、理解问题、生成 diff
- **内层 Agent 的执行记录是外层改进的信号源**

---

## 适用场景

这套自改进循环不仅适用于 Issue 分类，还可以用于：
- **代码审查 Skill**：根据审查者的反馈自动调整审查标准
- **Bug 修复 Skill**：根据修复是否被接受来改进修复策略
- **事故响应 Skill**：根据事后复盘改进响应流程
- 任何有明确反馈信号 + 可修改 Skill 定义的任务

> Warp 团队在管理自己的开源仓库时就在用这套自改进循环，他们已经提取出了框架让其他人使用。这是早期版本，欢迎反馈。

---

*整理于 2026-06-17，来源：Zach Lloyd @zachlloydtweets on X*
