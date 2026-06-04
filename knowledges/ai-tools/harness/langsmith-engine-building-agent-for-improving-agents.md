---
title: "LangSmith Engine：我们如何构建一个专门改进 Agent 的 Agent"
tags:
  - LangSmith
  - Agent Observability
  - Agent Debugging
  - LLM
  - AI Engineering
  - LangChain
date: 2026-05-20
source: "https://x.com/palashshah/status/2056786835322687640"
authors: "Palash Shah (@palashshah)"
---

# LangSmith Engine：我们如何构建一个专门改进 Agent 的 Agent

> **来源：** [How We Built LangSmith Engine, Our Agent for Improving Agents](https://x.com/palashshah/status/2056786835322687640) — Palash Shah (@palashshah)

![LangSmith Engine cover](../image/langsmith-engine-1.jpg)

上周 LangSmith 发布了 **Engine**——一个站在 Agent Trace 之上的 Agent，能自动发现重复性问题并建议改进方案。

本文深入技术细节：为什么构建 Engine、它的输入输出是什么、让它能分析大量 Trace 的架构决策。

---

## 为什么需要 Engine

LangSmith 是 Agent 改进循环（Build → Test → Deploy → Monitor）的载体。随着部署的 Agent 增多，产生的 Trace 数量也爆炸式增长。你需要花越来越多的时间翻阅 Trace，找出 Agent 哪里出了问题。

基本工具错误相对容易捕获，整体轨迹也能从 Trace 视图看到。但许多 Agent 问题在逐条细查之前极难发现：

- Agent 在重复调用同一个工具
- 使用了错误的工具参数
- 执行效率低下
- 遗漏了本应使用的工具
- 跨不同运行反复失败于同类型请求

LangChain 内部遇到这个问题后，决定构建 Engine。

**Engine 有三项职责：**
1. 发现 Trace 中的重复性失败
2. 将失败转化为可操作的 Issue
3. 将 Issue 转化为持久改进：Evaluator、数据集样本和修复

Engine 本身就是一个 Agent——一个编排器，使用专用组件端到端运行改进循环。它拉取 Trace（仓库连接时读取代码）、将失败归组为 Issue、提出 Evaluator 和数据集样例，并随时间不断更新对 Agent 的理解。

---

## Engine 产生什么：Issue

Issue 是一个重复性失败模式，附带证据 Trace 和建议的后续操作。Issue 在 **Issue Board**（问题面板）中呈现。

**一个 Issue 包含：**

| 字段 | 说明 |
|------|------|
| **名称** | Issue 标题 |
| **描述** | Issue 的描述段落 |
| **分类** | 预定义的 Agent 失败类别之一 |
| **严重程度** | 低 / 中 / 高 |
| **Trace 证据** | 关联的 Trace，证明此问题发生的位置 |
| **建议操作** | 防止问题再次发生的下一步建议 |
| **标签** | 驱动后续工作流的元数据，如 `needs_fix` |

**建议操作包括：**
- **建议的在线 Evaluator**：下次再发生时能标记此问题的检验器
- **建议的数据集样例**：离线数据集的补充，代表此问题
- **建议的修复**：修复根本问题的代码或提示词变更

> 关键点：Engine 不只指出一条糟糕的 Trace。它把生产故障转化为团队可以采取行动并在未来持续测试的东西。

---

## Engine 消耗什么

Engine 接收（或能够获取）四种主要输入：

### 指令（Agent Overview）

Engine 由一份 **Agent Overview** 指导——类似于 AGENTS.md 文件：对你的 Agent 做什么、期望什么 Trace 结构、注意哪些失败模式、以及团队表达过的偏好的**活文档**。

首次运行从入职回答和项目上下文引导。首次分析中，Engine 利用学到的内容创建 Agent Overview 的第一个版本。后续运行中，Agent Overview 成为 Engine 读取和更新的持久输入。也可以随时手动编辑。

### Trace

Engine 通过 LangSmith CLI 从相关追踪项目中拉取 Trace。完整的 Trace 包含 Agent 运行的消息和轨迹。为了支持规模，Engine 不一定一开始就加载每条 Trace 的完整内容。它通常从紧凑的**轨迹摘要**开始，然后在需要深入调查时选择性地加载完整 Trace。

### 现有 Issue

Engine 获取当前的 Issue 集合（包括开放和已关闭的），从而获得项目的当前状态，避免重复已知问题，为已有 Issue 补充证据，了解已解决或关闭的内容。

### 代码库（可选）

可以选连代码库，让 Engine 更精确地诊断问题，并允许一个独立的修复 Agent 提出变更。已连接的仓库会被安装到沙箱中。

---

## Engine 更新什么

Engine 可以更新以下几类输出：

- **Issue**：创建新 Issue、更新已有 Issue、附加证据 Trace、更改 Issue 元数据。对每个 Issue，Engine 可以提出一个能捕获相同模式的 Evaluator，也可以从证据 Trace 提议回归测试样例，还可以建议修复根本问题的提示词或代码变更。
- **Agent Overview**：Engine 记录发现，更新 Agent Overview 供后续运行使用。这是 Engine 随时间记住项目特定信息的方式：常见失败模式、Trace 模式、工具行为和用户偏好。

---

## 顶层架构

Engine 构建在 Deep Agents 之上，连接到一个沙箱，可以在其中写文件、检查 Trace、执行代码和操作已检出的仓库。

**高层驱动力：**
- **系统提示和指令**：包括 Agent Overview
- **沙箱**：Engine 的工作环境
- **LangSmith CLI**：Engine 获取数据和推送更新的主要接口
- **自定义工具**：特别是测试 Evaluator 和提议回归样例的工具
- **子 Agent**：用于筛选 Trace 和调查可疑 Issue，避免主 Agent 上下文溢出
- **记忆**：通过 Agent Overview 维护，基于用户操作更新

**核心循环：**
1. 准备 Agent 上下文
2. 大规模筛选 Trace
3. 调查可疑 Issue
4. 创建 Issue、Evaluator 和数据集样例
5. 需要时将修复交给独立 Agent
6. 为下一次运行更新记忆

---

## 1. 准备 Agent 上下文

### 沙箱设置

Engine 运行在沙箱中。我们使用 LangSmith Sandboxes。在运行前拉取基础 Engine Docker 镜像（包含所需库和 LangSmith CLI）。如果连接了 GitHub 仓库，也拉取相关代码工件。

沙箱很重要，因为 Engine 经常需要检查 Trace 数据、写中间文件、测试 Evaluator 代码、迭代建议的输出。给它一个可控的工作环境让工作流可靠得多。

### Agent Overview

既是指令文件也是记忆层。设置 Engine 时回答基本入职问题，Engine 利用答案和首次运行中发现的来创建初始版本。

Agent Overview 帮助 Engine 维护连续记录：Agent 做什么、期望的 Trace 结构、常见陷阱、项目特定上下文、用户偏好。

### LangSmith CLI

Engine 主要通过 LangSmith CLI 与 LangSmith 交互，而不是为每项操作创建自定义工具。CLI 是通用接口，用于拉取 Trace、查询 Issue、创建 Issue、附加 Trace、更新 Issue 元数据和提出工件。

这也让 Engine 更容易调试和复现——CLI 同样是可供下载并给本地编码 Agent 使用的同一接口。

---

## 2. 大规模筛选 Trace

**最大的架构挑战是 Trace 数量。**

让 Agent 检查 50 条 Trace 相对容易，但连接生产 Agent 后这一套就不行了——生产项目回看窗口内可能有数千甚至数万条 Trace。把全部完整 Trace 加载到主 Agent 上下文是不可行的。

所以我们把问题分为两个阶段：

- **宽筛阶段** — 快速识别可疑 Trace
- **深度调查阶段** — 只加载真正重要的 Trace 的完整上下文

### 轨迹格式

为了支持筛选，我们需要每个 Trace 的**压缩表示**。答案是**Agent 轨迹**——Trace 的紧凑骨架。每个轨迹条目包含角色、可选工具名、延迟和内容大小，不包括完整内容。

轨迹作为**导航工具**：让筛选器快速识别可疑形状，然后 grep 完整 Trace，只加载需要的信息到上下文。

### 反馈优先

有反馈关联的 Trace（人类标注、LLM-as-a-judge 评分、用户点赞/点踩）作为高优先级信号。Engine 不会自动将其变成 Issue，但会优先筛选和调查。

### 筛选子 Agent

核心筛选问题：**这条 Trace 中是否存在值得进一步调查的 Issue？**

Engine 使用专门的筛选子 Agent（基于 Haiku），主 Agent 将其分发到约 20 条 Trace 一组上。筛选器的任务刻意窄化：不做 Issue 创建，不做根因诊断，只在表面层面判断 Trace 是干净的还是可能有问题。

筛选器返回结构化响应——每条被标记的 Trace 一行，含 Trace ID、分类和简短原因，以及干净 Trace 的数量。

---

## 3. 调查可疑 Issue

筛选后，主 Agent 读取筛选器输出并分发深度调查。

### 调查子 Agent

调查器获取被标记的 Trace，拉取完整 Trace 内容，读取代码库（如有），并对潜在 Issue 进行深度分析。

调查器不是专用子 Agent（不像筛选器有固定系统提示），而是通用子 Agent，由主 Agent 针对具体调查动态提示。不同 Issue 类型可能需要不同的调查策略。

### Issue 分类

预定义了一组常见的 Agent 失败模式：

| 分类 | 含义 |
|------|------|
| `pii_leak` | PII 泄露 |
| `agent_looping` | Agent 重复循环 |
| `incorrect_tool_args` | 错误的工具参数 |
| `missing_tool` | 遗漏了应使用的工具 |

限制到已知分类，帮助控制 Engine 发现的问题类型以及在推向客户前评估这些类型。用户仍可通过 Agent Overview 自定义关注点。

---

## 4. 创建 Issue、Evaluator 和数据集样例

一旦 Engine 识别出真实 Issue，主 Agent 创建或更新 Issue 并附加证据 Trace。

Engine 可为每个 Issue 产生：
- Issue 本身（含证据 Trace）
- 建议的 Evaluator
- 建议的回归测试样例
- `needs_fix` 标签（需要时触发独立修复 Agent）

### Evaluator

两种类型：

| 类型 | 适用场景 | 示例 |
|------|---------|------|
| **代码 Evaluator** | 结构可检测的失败 | JavaScript 函数检查字段值、工具输出、步数 |
| **LLM-as-judge Evaluator** | 需要语义理解的失败 | 幻觉、接地失败、无帮助的拒绝、错误建议 |

### test_evaluator 工具

在把建议的 Evaluator 推给用户之前，Engine 调用 `test_evaluator` 工具在证据 Trace 上测试它。如果 Evaluator 没捕获正确的 Trace，Engine 可以迭代代码或提示词，直到输出最能捕获失败模式的版本。

### 回归样例与断言

每当 Issue 创建或有新 Trace 加入 Issue 时，Engine 调用 `propose_regression_example`。这为该 Trace 创建一个建议的回归样例——包含原始输入和预期输出上的断言。

选择断言而不是完整的 ground-truth 输出，因为断言更简单更灵活。每条断言都有 `key`（短 slug 标识符）和 `comment`（一句话可读声明）。

这将生产故障到离线测试覆盖的循环闭合。

---

## 5. 将修复交给独立 Agent

**关键设计决策：将 Issue 生成与修复生成分离。**

早期版本尝试让主 Agent 既识别 Issue 又提议修复。这让 Agent 的任务过宽——同时扫描 Trace、决定重要性、归组失败、创建 Issue、生成 Evaluator、提议数据集样例、推理正确的修复。主 Agent 很难在一轮中做到全部。

所以拆分工作流：
- 主 Engine Agent 识别和记录 Issue
- 创建数据集和 Evaluator 工件
- 如果需要修复，打上 `needs_fix` 标签
- 独立的修复 Agent 被触发，提出实际的代码或提示词变更

这让主 Agent 更简单，给了修复 Agent 更聚焦的任务。

---

## 6. 为下一次运行更新记忆

Engine 不每次从头开始。Agent Overview 不仅由 Engine 的调查更新，也由**用户操作**更新。当用户解决 Issue、关闭 Issue 或创建 Evaluator 时，这些动作都成为信号。

Engine 专门被提示维护一个 **User Preferences（用户偏好）** 部分，记录从观察用户如何与 Issue 交互中学到的东西。每个团队关心的问题集不同。Agent Overview 是 Engine 随时间适应这些偏好的方式。

---

## 关键架构决策与教训

| 决策 | 原因 | 效果 |
|------|------|------|
| **主 Agent 只聚焦 Issue** | 发现+修复一起做时，Agent 两者都做不好 | 拆分后主 Agent 更简单，修复 Agent 更专注 |
| **用 CLI 作为主要 LangSmith 接口** | 比每个操作建一个自定义工具更灵活 | 更易调试和复现 |
| **读取前先压缩 Trace** | 完整 Trace 太大，无法在生产规模下筛选 | 轨迹格式让大规模推理成为可能 |
| **筛选与调查分离** | 筛选优化规模，调查优化深度 | 处理大量 Trace 而无需全部深度检查 |
| **专用筛选器 + 灵活调查器** | 筛选是窄重复任务，调查多变 | 两全其美 |
| **限定 Issue 分类** | 让模型自行发明分类难以评估和信任 | 可控质量，可测量性能，可故意扩展 |
| **断言优于完整预期输出** | 捕获必须为真的条件，不过度约束措辞 | 更灵活正确的回归测试 |

---

## 结论

Engine 是我们自动化 Agent 改进循环的尝试。Agent 可观测性的难点不在于看一条 Trace 里发生了什么，而在于在大量 Trace 中找到重复性模式、决定哪些重要、并将这些模式转化为 Issue、Evaluator、数据集样例和修复。

这个架构反映了那个循环：Engine 准备上下文、大规模筛选 Trace、调查可疑 Issue、创建 Issue 工件、在需要时将修复交给独立 Agent、并为下一次运行更新记忆。

它已经改变了我们内部改进自己 Agent 的方式。不再手动翻阅 Trace 和分别编写评估——我们可以直接将生产行为转化为 Issue、修复和测试。

---

*整理于 2026-05-20，来源：https://x.com/palashshah/status/2056786835322687640*

### 关联阅读

- [AI Evaluation 完全入门](../ai-tools/ai-evals-explained.md) — Lotte Verheyden（Langfuse Academy），关于手动评估、代码评估和 LLM-as-a-Judge 的基础方法
