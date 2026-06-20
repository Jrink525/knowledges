---
title: "从 Prompt Agent 到 Loop Engineering"
tags:
  - claude-code
  - agent
  - loop-engineering
  - ai-coding
  - autonomous-agent
  - crabfleet
date: 2026-06-20
source: "https://x.com/omarsar0/status/2068008743153832264"
authors: "omarsar0 (Elvis Saravia)"
---

# 从 Prompt Agent 到 Loop Engineering

> **来源：** [From Prompting Agents to Loop Engineering](https://x.com/omarsar0/status/2068008743153832264) — by Elvis Saravia (@omarsar0)

---

AI 编程圈有个说法在流传：**别再给 coding agent 写 prompt 了，开始设计循环来帮你写 prompt。**

这篇文讲的不是 prompt engineering 死了，而是**工作上升了一个层级**——从写代码变成了写一个帮你写代码的系统。

---

## 这个说法从哪来

> "你不应该再给 coding agent 写 prompt 了。你应该设计循环，让循环来写 prompt。"
> — Peter Steinberger (@steipete)，2026.6.7，220 万次观看

Claude Code 的创造者 Boris Cherny 从另一侧表达了同样观点：

> "我不再手动 prompt Claude 了。我有在跑的循环，它们在 prompt Claude 并决定下一步做什么。我的工作是写循环。"
> — Boris Cherny (@bcherny)

走到最前面的开发者说，他们连续几个月没打开 IDE 就交付了数百个 PR——每一行代码都是 Agent 写的。

![img-1](../image/from-prompting-agents-to-loop-engineering-1.jpg)

---

## Loop 到底是什么

Loop 是你写的一个小程序，做四件事：

1. **替你给 coding agent 写 prompt**
2. **读取 Agent 的输出**
3. **判断是否完成**
4. **如果没完成，带着错误或下一步再写一次 prompt**

你不再坐在循环里手动输入 prompt；你写一个循环，LLM 成为它调用的一个子程序。

形状始终一样：**设目标 → 行动 → 检查 → 反馈错误 → 重复，直到检查通过或循环自行停止。**

---

## "Loop" 至少指五件事

很多争论是因为人们用同一个词指代五种不同的东西：

| 阶段 | 时间 | 特点 |
|------|------|------|
| **ReAct** | 2022 | 原始研究模式：思考 → 行动 → 观察 → 重复 |
| **AutoGPT** | 2023 | 自 prompt 目标循环，以"不知何时停止"闻名 |
| **ralph loop** | 近期 | 每次迭代之间主动重置上下文，防止 Agent 被自己的历史淹死 |
| **/loop 和 /goal** | 现在 | Cadence 和完成条件内置于 Agent，跨轮次携带状态 |
| **Orchestration** | 前沿 | 一个作者派出多个 Agent，读取你的 GitHub/Slack 决定该做什么 |

![img-2](../image/from-prompting-agents-to-loop-engineering-2.jpg)

---

## Loop 的六个组装部件

无论哪种 Loop，都由相同的六部分组成——如今大部分已经内置到编码工具里了：

1. **触发器** — 不用你按"开始"就能启动的东西：定时任务、webhook、文件变更、PR 标标签
2. **隔离** — 每个 Agent 有一个独立的 git worktree，两个 Agent 同时跑不会互相覆盖
3. **写下来的上下文** — 项目惯例、构建步骤、仓库规则放在 Agent 每次运行都能读到的地方
4. **接入工具** — 连到 Issue 跟踪器、CI、数据库、聊天工具，让 Loop 能直接开 PR、关联 ticket、发结果
5. **第二个 Agent 做审查** — 一个独立的 Agent 评分输出——因为让模型审查自己的作品，它几乎什么都过
6. **磁盘上的状态** — Markdown 文件、看板或队列——跑在对话之外的东西，记录什么完成了、什么该下一步。模型每次运行会忘记，文件不会

---

## 一个具体的 Loop：PR Babysitter

一个你今天就能搭的具体例子：

```
触发器：每 15 分钟
范围：打了 agent-watch 标签的开放 PR
动作：如果 CI 因为确定性原因变红，尝试一次修复。如果 main 前进了，rebase 一次
预算：每个 PR 一次修复，5 分钟，最多改 10 个文件
停止条件：CI 变绿 或 预算耗尽 → 通知人类
```

你回来看到的是**已合并的 PR**，而不是一堆积压的坏构建。

同样的模式管用的大多数运维工作：

- **CI 健康** — 每 30 分钟拉取失败的运行，按根因归类
- **部署验证** — push 后检查端点确认 200 + 预期内容
- **反馈聚类** — 每 30 分钟拉取各渠道评论，按主题分组映射到对应文档

![img-3](../image/from-prompting-agents-to-loop-engineering-3.jpg)

---

## Claude Code 的具体 Loop：/goal

在 Claude Code 里，最小的完整 Loop 是 `/goal`：你给它一个**可验证的终态**，它不断执行直到达成。

一个好的 `/goal` 读起来不像 prompt，更像**合约**。好合约指定四样东西：

- **你想要的目标状态**（end state）
- **证明你达到了的证据**（evidence）
- **Agent 不能打破的约束**（constraints）
- **它允许花多少工作量**（budget）

任一项模糊了，模型就用最省事的理解补全：提前停止、走捷径、或者重新定义"成功"。

| /goal 例子 | 说明 |
|-----------|------|
| ✅ `npm test exits 0` | 可测量 |
| ❌ "make it better" | 不可测量 |

> **隐藏技巧**：评估者不必和编码者用同一个模型。规划器、执行器、评估者、视觉审查者各司其职，你可以为每个角色选不同的模型。有些模型策划更好，有些执行更便宜，有些看截图更准确。

---

## 无人值守跑多个 Loop

Cherny 的做法分五步：

1. **自动审批权限** — Agent 不需要每次调工具都停下来问你
2. **动态工作流** — 用一个 Agent 派出多个子 Agent，不串行
3. **/goal 或 /loop** — 带状态跨轮次，不提前退出
4. **云端运行** — 在桌面或手机 App 上跑，关了笔记本也不停
5. **端到端自验证** — Web 用 Chrome，Mobile 用模拟器 MCP，后端用 live server——这一步让前四步变得安全

![img-4](../image/from-prompting-agents-to-loop-engineering-4.jpg)
![img-5](../image/from-prompting-agents-to-loop-engineering-5.jpg)

---

## crabfleet：产品化的 Orchestration

Peter Steinberger 的 [crabfleet](https://github.com/steipete/crabfleet)（OpenClaw 生态）把 Loop 做成了产品：

- **工作即看板卡片** — 任务从 prompt / GitHub Issue / PR 变成卡片，流经 todo → running → human review → done
- **持久化运行** — 有心跳追踪，关笔记本也不停
- **Agent 生子 Agent** — 一个运行可以开子会话、发消息、读转录、更新自己的摘要

关键是 Loop 已经硬化成了基础设施：队列、持久化执行、发散、人工审查关卡——这些都是配置项，不是每次手写。

![img-6](../image/from-prompting-agents-to-loop-engineering-6.jpg)

---

## 成本去哪了

过去两年 AI 编程的成本问题是：哪个模型，用了多少 token？

**在 Loop 里，本能会指向错误的层面。** 花费不是单次调用，而是**循环了多少轮**。一个要重试 6 次的 Loop，成本是 1 次就搞定的 6 倍——同一个模型。

这对优化方向的改变：

- **迭代次数是预算线，不是 token 数** — 更便宜的模型如果多循环一倍次数，并不便宜。追踪每完成一个任务的成本，不是每次调用的成本
- **弱的验证器是最贵的 bug** — 如果"完成"的判断很宽松，Loop 要么在破损工作上提前停止，要么在已完成的工件上浪费轮次
- **快速失败就是成本控制** — 没有连续失败上限的 Loop 不会最终成功，只会最终把账号榨干

你曾经调 prompt，现在你调的是 Loop——因为这才是成本累积的地方。

---

## 什么时候不该用 Loop

Loop 在以下情况才有价值：**任务可重复 + 机器能判断完成**。否则它只自动化了空转。

| 跳过 | 原因 |
|------|------|
| 一次性修改 | 一次能完成的事，Loop 是纯粹的额外开销 |
| 无范围探索 | "找找用户为啥流失"没有 pass condition，Loop 永远不会收敛 |
| 没有廉价自动检查 | 如果唯一的验证器是你的眼睛，你仍然在循环里。先搭好检查，或者手动做 |

---

## 会出什么问题

你睡觉时还在跑的 Loop，也在你睡觉时犯错：

- **验证负担仍然是人的** — Loop 写得比你审查快，如果你不读 diff，就不是取消了工作，只是推迟了
- **理解差距扩大** — 提交不是自己写的代码，快到自己吸收不了，侵蚀自己对系统的理解，下次事故时爆发
- **宽松检查下的静默漂移** — 弱的验证器让错误但通过检查的工作每轮都通过，Loop 看起来高产却在挖坑

这些都不是反对使用 Loop——恰恰说明**设计 Loop 的工程师更重要了，不是更不重要。**

---

## 如何自己搭建 Loop

1. **选一个可重复的任务** — 看 PR、修 CI、验证部署：从例行工作开始
2. **把范围收紧** — "修 billing webhook 校验，只动 app/api/billing 和 lib/billing" 好过 "修 bug"
3. **给预算和停止条件** — 最大尝试次数、最大运行时间、最大文件数量、最大连续失败次数
4. **加独立验证器** — 一个独立的子 Agent 评分输出，因为写代码的 Agent 是判断"是否完成"的最差人选
5. **按节奏跑** — `/loop` 做间隔循环，cron 做定时任务，钩子在生命周期点触发，GitHub Actions 让它不受笔记本开关影响
6. **状态放磁盘** — 模型在运行之间会忘记，状态存在 Markdown 或看板上，不在上下文窗口里

**核心观点收束：Loop（而不是模型）现在是昂贵和容易出故障的部分。像一个真正对产出负责的工程师那样构建它——而不只是按下启动键的人。**

![img-7](../image/from-prompting-agents-to-loop-engineering-7.jpg)

---

## 参考链接

- Addy Osmani — [AI-assisted coding loops](https://x.com/addyosmani)
- Matt Van Horn — ["WTF Is a Loop?"](https://x.com/mvanhorn)
- Peter Steinberger — [designing loops](https://x.com/steipete)
- Boris Cherny — [running agents autonomously](https://x.com/bcherny)

---

## 跟你的 Agent 栈的关联

| Loop Engineering 概念 | 可以用什么实现 |
|----------------------|---------------|
| 6 个组装部件 | Claude Code / Spring AI + Pydantic AI |
| /goal 条件合同 | Pydantic AI result_type Schema |
| 独立验证器 | 第二个 Agent 做 Reviewer 角色 |
| 磁盘状态 | 文件或看板，不是上下文窗口 |
| 多 Agent 角色分工 | 不同模型负责不同角色 |
| crabfleet | OpenClaw 的原生子 Agent + 看板 |

---

> *Processed on 2026-06-20 from https://x.com/omarsar0/status/2068008743153832264*
