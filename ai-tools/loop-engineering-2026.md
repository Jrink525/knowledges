---
title: "Loop Engineering 完全指南：2026 年每个 AI 工程师都需要知道的"
tags:
  - loop-engineering
  - AI-agents
  - coding-agents
  - prompting
  - deepseek
  - claude-code
  - agent-architecture
date: 2026-06-10
source: "https://x.com/sairahul1/status/2064277888216555684"
authors: "Rahul (@sairahul1)"
---

# Loop Engineering 完全指南

> **来源：** [Loops: What Every AI Engineer Needs to Know in 2026](https://x.com/sairahul1/status/2064277888216555684) — @sairahul1

---

Peter Steinberger（OpenClaw 创始人，现 OpenAI）和 Boris Cherny（Anthropic Claude Code 负责人）不约而同说出了同一个观点：

> **"不要再 prompt 编码 Agent 了。你应该设计循环（loops）来 prompt 你的 Agent。"**

本文是对这个理念的完整拆解。

---

## 先说最现实的障碍：成本

大多数人**不做**循环，是因为账单扛不住。

| 场景 | Token 消耗 |
|------|-----------|
| 单个 Agent 循环（中等编码任务） | 50,000 ~ 200,000 tokens |
| Fleet 循环（编排 + 3 个专家 Agent） | 500,000 ~ 2,000,000 tokens |
| 每日定时循环 | 每周数百万 tokens |

用标准 API 定价，一周认真的循环工程比大多数人**整月 AI 预算还贵**。

所以 Peter Steinberger 的评论区全是：
> "你说得轻松——你有无限的 OpenAI 额度。"

每次重试、每次自我修正、每个子 Agent、每次验证——全都要钱。

**循环不难设计，难的是负担得起。**

## 中国大模型解决了什么？

这正是 DeepSeek、Kimi、MiniMax 改变游戏的地方。自主 Agent 最大的问题不是智能，而是 **token 燃烧**。

DeepSeek V4 是目前最便宜的 SOTA 模型之一：

| 特性 | 值 |
|------|-----|
| 上下文窗口 | **1M tokens** |
| 最大输出 | 384K tokens |
| 并发 | Flash 模型最高 2500 请求 |
| 定价 | 极低 |

1M 上下文窗口为什么重要？循环需要记忆——之前的运行、当前错误、架构文档、测试结果、代码库上下文——全都要同时记住。大部分模型中途就丢了上下文。

---

## 第一部分：旧方式 vs 新方式

**旧方式（Prompting）：**
> 你 → 写 Prompt → Agent 输出 → 你 review → 你修改 → 再 Prompt → 你**就是那个循环**

**新方式（Looping）：**
> 你定目标 → Loop 运行 → Agent 发现 → 计划 → 执行 → 验证 → 迭代 → 完成

> **Prompt 给 Agent 指令，Loop 给 Agent 一份工作。**

---

## 第二部分：什么是 Loop Engineering

**定义：** 设计可重复的反馈循环，引导 AI Agent 从尝试到经过验证的结果——无需持续的人工干预。

每个循环都经历相同的 **5 个阶段**：

```
DISCOVER（发现） → PLAN（计划） → EXECUTE（执行） → VERIFY（验证） → ITERATE（迭代）
通过验证 → 交付；未通过 → 再来一轮
```

---

## 第三部分：单 Agent vs Fleet

### 单 Agent 循环
一个 Agent 独立跑完整循环。适合聚焦任务、简单目标、有限范围。

### Fleet 循环
编排者（Orchestrator）将目标拆解，分给多个专家 Agent，每个专家又分给子 Agent——整棵树都在跑 DISCOVER → PLAN → EXECUTE → VERIFY → ITERATE。

```
Orchestrator（掌握目标）
  ├── 研究员 Agent
  ├── 工程 Agent
  │     ├── 代码编写 Agent
  │     ├── Debug Agent
  └── QA Agent
        ├── 测试编写 Agent
        └── Bug 追踪 Agent
```

---

## 第四部分：开放循环 vs 封闭循环

| | 开放循环 | 封闭循环 |
|--|---------|---------|
| 特点 | 探索性、自由探索 | 有边界、人类设计好路径 |
| Token 消耗 | 极高 | 可控 |
| 成本 | 需要无限预算 | 正常预算即可运行 |
| 乱出结果 | 缺乏标准时变成垃圾制造机 | 质量门保持诚实 |
| 适合谁 | OpenAI 等有无限额度的 | **90% 的普通人** |

> **先用封闭循环。构建一个可靠工作的 Tight 系统。有了质量门之后再打开它。**

---

## 第五部分：优秀循环的 6 个构件

### 1. 自动化（Automations）—— 循环的心跳
定义 prompt、节奏和目标，循环定时运行。`/goal` 在条件满足前持续运行。
> 示例："所有 test/auth 测试通过且 lint 干净。"——然后走开。

### 2. Worktrees —— 并行 Agent 不冲突
多个 Agent 同时运行时文件必然冲突。Git worktree 给每个 Agent 独立的隔离工作目录，同一个 repo 历史，零碰撞。

### 3. Skills —— 项目知识随运行累积
一个文件夹 + `SKILL.md`，记录项目约定、构建步骤、禁忌。一次编写，每次循环都用到。没有 Skills，循环每次都要重新推导整个项目。
- `VISION.md` — 成功标准
- `ARCHITECTURE.md` — 技术栈和目录结构
- `RULES.md` — Agent 绝对不允许做的事

### 4. 插件和连接器 —— 循环连接真实环境
基于 MCP，让 Agent 读 issue tracker、查数据库、调用 staging API、发 Slack 消息。区别在于：一个说"这是修复方案"的 Agent vs 一个自动开 PR、关联 Linear ticket、CI 通过后通知频道的循环。

### 5. 子 Agent —— 制造者和检查者分离
写代码的模型给自己打分太宽容了。一个独立的子 Agent（有时候是不同的模型）来抓住第一个 Agent 骗自己信了的东西。
> 一个探索，一个实现，一个按规格验证。

### 6. 记忆 —— 循环的脊柱
一个 markdown 文件、一个 Linear board——任何存在于单次对话之外的东西。模型会在运行间忘记一切，但 repo 不会。记忆文件记录：尝试了什么、什么通过了、什么还开着。第二天早上循环从昨天停下的地方继续。

---

## 第六部分：真实循环示例

所有循环共享同一个骨架：
> **目标 → 行动 → 检查 → 修复 → 重复直到完成**

**编码循环：** 写 → 测试 → 修复 → 验证，中间没有人类干预
**研究循环：** 搜索 → 提取 → 综合 → 验证来源 → 格式化
**内容循环：** 大纲 → 起草 → 审核 → 修订 → 发布
**销售外联循环：** 研究 → 个性化 → 发送 → 跟踪反馈 → 优化

---

## 第七部分：Prompt 工程师 vs Loop 工程师

| 维度 | Prompt 工程师 | Loop 工程师 |
|------|-------------|------------|
| 核心技能 | 语言技巧 | 软件工程 |
| 追求 | 更好的 prompt → 更好的单次输出 | 更好的循环 → 可靠的可验证结果 |
| 质检方式 | 每次手动 review 输出 | 自动化测试 + 质量门 |
| 收费模式 | 为单次输出付费 | 为经过验证的结果付费 |
| 工作方式 | "写一个函数" | "写 → 测试 → 修复直到变绿" |
| 思维 | 向 AI 要产出 | 设计产出可验证结果的系统 |

> **2026 年薪酬最高的 AI 工程师不是写更好的英语句子的人。他们是设计支配 Agent 如何发现、计划、检查自己工作、以及知道何时完成的逻辑的人。**

---

## 总结：框架速查

**转变：** 两年了我们在逐个 prompt Agent → 现在设计跑完整循环的系统

**6 个要构建的东西：**
1. **自动化** — 心脉，触发发现
2. **Worktrees** — 并行 Agent 不碰撞
3. **Skills** — 项目知识随每次运行累积
4. **插件/连接器** — 循环作用于真实工具
5. **子 Agent** — 制造者和检查者分离
6. **记忆** — 循环在运行间不遗忘

**两个规模：** 单 Agent（自改进）| Fleet（编排 + 专家）

**两种类型：** 开放循环（探索、贵）| 封闭循环（可靠、今天就能用）

**优秀循环的 5 个部分：**
- **目标** — 精确定义何为"完成"
- **上下文** — VISION.md, ARCHITECTURE.md, RULES.md
- **行动** — 只给 Agent 真正需要的
- **反馈** — 测试、类型检查、linter、结构化错误
- **停止条件** — 循环知道何时结束

**成本问题：** DeepSeek 让 $20 的预算走得更远，移除了最后一个真实障碍

---

## 最后的话

Peter Steinberger 说得对：**停止 prompt 你的 Agent。开始设计循环。**

因为一个可靠的循环，胜过一千个完美的 prompt。

但有两件事没人说出口：
- 两个人可以构建完全相同的循环，得到截然不同的结果——一个用它来加深理解，一个用它来逃避理解
- Loop Engineering 不是更简单了，而是**杠杆点转移了**

> **Prompt 工程师向 AI 要产出。Loop 工程师设计产出可验证结果的系统。**

---

## 🖼️ 配图

![Loop Engineering 架构概览](../image/loop-engineering-2026-1.jpg)
*Loop Engineering 核心框架：5 阶段循环 + 6 构件 + 两种规模*

---

*整理于 2026-06-10，来源：https://x.com/sairahul1/status/2064277888216555684*
