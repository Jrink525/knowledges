---
title: "用 Fable 5 设计循环——Lance Martin 的实践技巧"
tags:
  - claude
  - fable-5
  - anthropic
  - AI-agents
  - self-correction
  - memory
  - agent-loops
date: 2026-06-10
source: "https://x.com/rlancemartin/status/2064397389189071163"
authors: "Lance Martin (Anthropic)"
---

# 用 Fable 5 设计循环

> **来源：** [Lance Martin 在 X 上发布的文章](https://x.com/rlancemartin/status/2064397389189071163) — Anthropic 成员分享 Mythos 类模型（Fable 5）的两大最佳实践

---

Mythos 类模型（如 Claude Fable 5）已经改变了许多 Anthropic 内部人员的工作方式。本文将分享发挥这类模型最大能力的**两个技巧**。

---

## 技巧一：自我修正循环（Self-Correction Loops）

最近大家对"循环"的讨论很多。`@bcherny` 曾说过"他的工作就是写循环"。让模型在某个评估上 hillclimb（爬山优化）是提升任务表现的通用策略——Claude Code 中的 `/goal` 和 Claude Managed Agent 中的 Outcomes 就是让你将这个通用策略应用到具体任务的基元。

### Fable 5 擅长在循环中自我修正

正如 Anthropic 的 prompt 指南所述，Fable 5 在循环中的自我修正能力很强。一个精心设计的 goal 或 rubric 能为 Claude 运行的环境提供反馈，让 Claude 能够：

1. **执行**任务
2. 通过 goal/rubric **收集反馈**
3. **自我修正**
4. 继续执行，直到 goal/rubric 满足条件

### 实战案例：Parameter Golf

Lance 用了一个 toy 挑战来测试 Fable：**[Parameter Golf](https://github.com/yourbuddyconner/Parameter-Golf)**，一个开源的 ML 工程挑战——在 8 台 H100 上、**10 分钟内**、用 **16MB** 的 artifact 训练最佳模型。

这有点像 `@karpathy` 的 autoresearch 项目：测试 Agent 编辑基础训练代码（一个 `train_gpt.py`）、启动训练、轮询日志、读取分数、决定下一步实验的能力。

### 实验对比：Fable 5 vs Opus 4.7

Lance 使用 **Claude Managed Agents (CMA)** 进行对比测试。CMA 提供 Agent harness + 托管沙箱，非常适合 Fable 5 的长时间运行任务。Parameter Golf 测试中，CMA 配备了 8xH100 GPU 作为自托管沙箱。

**关键设计细节：谁来评判？**

> 评估者（judge）是谁至关重要。模型在自我评判自己输出方面存在问题（Anthropic 的 Prithvi Rajasekaran 在[工程博客](https://anthropic.com/engineering)中有详细分析）。

研究表明，**独立的验证子 Agent（verifier sub-agent）优于自我评判**，因为评分在独立的上下文中进行。CMA 中的 Outcomes 通过自动为你派生出 grader sub-agent 来处理这个问题。

### 测试设置

- 提供一个包含 **9 个可检查标准**的 rubric 文件（如：运行 baseline、运行 20 个实验等）
- 最长运行 8 小时
- Outcomes grader 确认所有实验标准满足后才允许 Claude 停止

### 结果：Fable 5 提升 ~6 倍

| 维度 | Fable 5 | Opus 4.7 |
|------|---------|----------|
| 训练管线优化幅度 | **~6 倍于 Opus** | 基准 |
| 实验类型偏好 | **结构性变更**（如架构变化），敢于冒险 | **标量调整**（改常数），保守策略 |
| 典型行为 | 经历量化回退后仍能推进到最大突破 | 第一次小赢后，后续几乎都复制同一模板：调参数 → 测量 → 保留 |

Fable 5 更倾向于选择结构性的重大变更，表现出更强的韧性——即便遭遇量化回退，最终仍能取得最大突破。Opus 4.7 则在第一次标量调优成功后，几乎完全沿用同一种策略。

---

## 技巧二：记忆（Memory）——跨会话的外循环

记忆是 Fable 另一大优势领域。可以把它理解为一个**跨会话的外循环**：Claude 在会话期间写入记忆，这些记忆可以在未来的会话中被检索。

`@pgasawa` 团队最近发布了 **[Continual Learning Bench 1.0](https://github.com/anthropics/continual-learning-bench)**，Lance 用这个 benchmark 测试了 Fable 5 与早期模型的对比。

### 测试任务

从 SQL 数据库访问任务中选了一道：Agent 需要按顺序回答问题，**每个问题是一个独立的 Agent 会话**，并提供记忆。使用 **CMA with memory**，每个 Agent 可以访问一个跨会话共享的挂载文件系统。

### 记忆的有效使用递进模式

有效的记忆使用遵循一个五步递进：

| 步骤 | 名称 | 说明 |
|------|------|------|
| 1 | **Fail（失败）** | 答错某题，记录下来 |
| 2 | **Investigate（调查）** | 继续前进之前，搞清楚为什么错 |
| 3 | **Verify（验证）** | 将诊断转化为已确认的事实 |
| 4 | **Distill（提炼）** | 将验证转化为通用规则 |
| 5 | **Consult（查阅）** | 下次直接读规则，而不是重新推导 |

### 各模型对比结果

| 模型 | 递进步数 | 行为特征 |
|------|---------|----------|
| **Sonnet 4.6** | ~第 1 步 | 记忆是失败笔记列表 + 开放式猜测（如"maybe prc instead of prc_usd?"），很少查阅之前的笔记。需要任务特定记忆指令才能提升 |
| **Opus 4.7** | ~第 3 步 | 创建带不确定性标记的 schema 引用（如"possibly prc in cents? Verify"），但验证覆盖率低——7%~33%（中位数 ~17%） |
| **Fable 5** | ✅ **完整递进** | 最强运行中**验证覆盖率高达 73%**（22/30），并能将学到的知识提炼为通用规则，帮助未来的任务 |

---

## 核心理念

> **不要直接 prompt 和操控 Fable 5，不如设计好循环，让模型通过环境反馈（如 `/goal` 或 Outcomes）自我修正，并通过记忆管理自己的上下文。**

两个原则：
1. **循环而非指令** — 设计让模型在反馈中自修正的 loop，而不是手动给每步指令
2. **外循环记忆** — 利用跨会话记忆实现持续学习，而不是让每次会话从零开始

---

## 开始使用

Lance 建议直接上手测试 Fable 5。查看 [Anthropic 文档](https://docs.anthropic.com/) 或让最新版 Claude Code 使用内置的 `/claude-api` 技能告诉你关于 Fable 5 的一切（包括 prompt 最佳实践、`/goal`、Claude Managed Agents 等）。

---

## 🖼️ 文章配图

![Fable 5 循环设计概览](../image/fable5-loop-design-1.jpg)
*Fable 5 自我修正循环 + 跨会话记忆的架构示意*

---

*整理于 2026-06-10，来源：https://x.com/rlancemartin/status/2064397389189071163*
