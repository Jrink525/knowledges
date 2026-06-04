---
title: "Master Dynamic Workflows in Claude Code: 6 Patterns and 14 Steps"
tags:
  - claude-code
  - dynamic-workflows
  - agent-patterns
  - anthropic
  - agent-orchestration
  - workflow-engineering
date: 2026-06-04
source: "https://x.com/0xcodez/status/2062127385923776831"
authors: "Codez (@0xCodez)"
category: ai-tools
---

# Claude Code Dynamic Workflows 完全指南：6 模式 · 14 步

> **来源：** [Codez (@0xCodez)](https://x.com/0xcodez/status/2062127385923776831)  
> **数据：** 476 ❤️ · 55 转 · 22 回复  
> **背景：** Dynamic Workflows 于 2026 年 5 月 28 日在 Claude Code 中发布

---

## 核心观点

> 9/10 的 Claude Code 用户还没用过 Dynamic Workflows，即使它已经发布了两周。他们还在手写 50 个 prompt，而一个 workflow 就够了。

**Dynamic Workflow = Claude 为任务自写的专属 Harness**——一个 JavaScript 文件，含特殊函数来生成和协调子 Agent，外加标准 JS 处理数据流。

---

## 一、心智模型

### 1. 什么是 Dynamic Workflow

默认 Claude Code Harness 让 Claude 在同一个上下文窗口中规划和执行。对大多数编码工作够了。但对**长运行、大规模并行、高度结构化、对抗性**的任务会崩溃。

Dynamic Workflow 是 Claude 为自己写的自定义 Harness——一个 JavaScript 文件，有两个特质：
- **子 Agent 隔离**：每个子 Agent 有自己的上下文窗口和单一目标，不会交叉污染
- **子 Agent 模型选择**：Opus 做硬推理，Haiku 做廉价探索，Sonnet 做中间层
- **隔离级别**：worktree（隔离 git checkout）或 remote（无 checkout）

启动方式：直接说"make a workflow that…"或通过 `ultracode` 触发词。中断后恢复从断点继续。

### 2. 三种 Workflow 解决的失效模式

在单个上下文窗口中长时间工作，Claude 会退化出三种模式：

| 失效模式 | 表现 | Workflow 解法 |
|---------|------|-------------|
| **Agentic Laziness** | 做到一半就宣告完成（50 个安全检查查到 20 个就说"剩下的处理了"） | 子 Agent 各有明确终止条件 |
| **Self-preferential Bias** | Claude 偏爱自己的结果——让它验证自己的输出，它倾向于说"通过" | 对抗验证（独立子 Agent 各自验证，互不知情） |
| **Goal Drift** | 目标逐渐漂移——每一次 compaction 都有损压缩。"不要做 X" 的约束在第 47 轮悄悄消失 | 子 Agent 有独立的上下文中聚焦的目标 |

你的任务如果有以上任何一种症状，就是使用 Workflow 的信号。

### 3. Static vs Dynamic

| | Static Workflow | Dynamic Workflow |
|--|---------------|-----------------|
| 写法 | Claude Agent SDK 或 `claude -p` 手写 | Claude **自写**，为 **这个** 任务量身定制 |
| 泛化能力 | 一个处理所有 edge case | 一个只处理当前任务 |
| 上下文感知 | 不知道你的代码存在 | 读你的计费代码、查新 provider 文档、按你的交易量定价 |
| 灵活性 | 保守 | 自由 |

**关键区别不在于"能不能搜索"，在于 Workflow 能围绕你的上下文自我塑形。**

---

## 二、核心 API

三个核心函数，理解它们就能读懂 Claude 为你写的任何 Workflow：

| 函数 | 行为 | 类似于 | 选哪个 |
|------|------|-------|-------|
| **parallel()** | **屏障**：扇出 → 等待全部完成 → 返回 | Promise.all | 我需要所有结果才能做下一步？→ parallel |
| **pipeline()** | **流**：每项独立流过每个阶段 | 流式处理 | 不需要等全部？→ pipeline（更便宜更快） |
| **agent()** | 创建一个子 Agent | fork | — |

---

## 三、6 个核心模式（附实战用例）

### 模式 1：Classify-and-Act（分类路由）

分类 Agent 先判断任务类型，Workflow 按结果路由到不同行为。或分类器在最后运行，把原始输出分桶。

**适合场景：**
- 任务异构——不同子类型需要不同处理
- 想把贵模型只花在需要复杂推理的地方（便宜模型分类，只路由到 Opus）
- 任务分解本身复杂，需要模型决定形状

**示例**："解释 auth 模块怎么工作。" 分类子 Agent 先读代码库评估复杂度，然后路由到 Sonnet（10 个文件）或 Opus（100 个文件）。

---

### 模式 2：Fan-Out-and-Synthesize（扇出合成）

拆分任务 → 并行在每个步骤上跑一个 Agent → 合成结果。

**合成步骤是一个屏障**——等待所有扇出的 Agent，然后合并结构化输出。

**为什么这个模式在实践中占主导：** 每个子 Agent 只看到自己的那一块，编排者不会被 50 个无关细节干扰。

**适合场景：**
- 可清晰枚举的工作项清单（50 个文件、200 个端点、100 次审查）
- 每项独立——不需要另一项的输出才能开始
- 想要一个合并后的答案，而不是一堆部分报告

---

### 模式 3：Adversarial Verification（对抗验证）

对每个产物 Agent，运行一个独立的对抗验证子 Agent，用标准检查它。验证者从未见过原产物，所以不会偏爱它。

**配对规则**：验证者只能看到标准 + 产物，不能看到谁产出的。否则 self-preference 会通过 prompt 的暗示溜回来。

**最重要场景：**
- **声明核查**——报告中的每个事实陈述都有独立验证子 Agent 查原文
- **代码审查**——作者 Agent 写修复，审查者 Agent（独立上下文）审查它。同一模型不能既审判又参赛
- **质量门**——任何产物上线前，对抗者试着找出最弱的反例。找不出就发版

---

### 模式 4：Generate-and-Filter（生成过滤）

生成一批想法 → 用标准或验证过滤 → 去重 → 只返回最高质量。

**适用场景：**
- 头脑风暴——30 个产品名 → 验证者杀掉陈词、商标冲突、弱读音 → 你看到 3 个
- 假设生成——5 种方案 → 各自按约束打分 → 赢家名副其实
- 方案设计——同上

**核心哲学**：问"最好的答案"让 Claude 过早承诺。Generate-and-Filter 让 Claude 晚承诺——在每个选项都被挑战之后。

---

### 模式 5：Tournament（锦标赛）

不拆分工作，而是让 Agent 竞争。生成 N 个 Agent 用不同方式执行同一任务，通过两两比较决出胜者。

**为什么比绝对评分好：** 想对 1,000 个项排序的尝试在两个层面失败——质量下降 + 放不进上下文。锦标赛把比赛放在循环代码中（而非上下文中），每次比较只活在独立 Agent 的上下文中。

**适用场景：** 设计选择、候选人筛选、内容优先级排序——所有"品味"相关的工作。

---

### 模式 6：Loop Until Done（循环至完成）

对工作量未知的任务，循环生成 Agent 直到满足停止条件——没有新发现、日志无错误、理论已验证。不运行固定轮次。

**适用场景：**
- 不稳定测试调试——复现 → 形成理论 → 测试 → 直到一个理论成立
- Bug 狩猎——继续找，直到完整一轮返回零
- 模式挖掘——聚类 → 识别规则 → 直到无新聚类

**搭配使用：** `/goal` 设硬性完成条件（"不停止直到一个理论成立"） + `/loop` 让整个 Workflow 定期运行。

---

## 四、模式组合：真实用例

实际 Workflow 很少只用一个模式。以下来自 Anthropic 官方文档的用例与其常用模式对照：

| 用例 | 使用模式组合 | 注释 |
|------|------------|------|
| **迁移和重构** | Fan-Out → Adversarial Verification → Loop | Anthropic 用这个把 Bun 从 Zig 重写为 Rust |
| **深度研究** | Fan-Out（并行搜索）→ Adversarial Verification（独立验证每个声明）→ Synthesize（一份引用报告） | |
| **草稿深度验证** | 一个 Agent 识别所有事实陈述 → Fan-Out（每个声明一个验证者）→ Meta-验证者（检查验证者的来源质量） | |
| **1000+ 项排序** | Tournament（两两比较 / 桶排序 / 锦标赛） | 用比较判断，不用绝对评分 |
| **规则遵守审查** | 每条规则一个验证者（Fan-Out）→ Skeptic 角色审查规则本身（避免假阳性） | |
| **根因排查** | 从不同证据生成理论（不同 Agent 读日志/文件/数据）→ 每个理论一组验证者和反驳者 → Loop 直到一个幸存 | |
| **规模化工单处理** | Classify-and-Act → 去重 → 尝试修复或升级 | 搭配 `/loop` 实现持续处理 |
| **探索与品味** | Generate-and-Filter（5-20 选项）→ Tournament（带标准）→ 排序或挑选 | |
| **轻量 Eval** | 在 worktree 中跑候选 → 对比 Agent 打分（按标准）→ 优化和重新打分 | 类似锦标赛但不排名 |

**实用心法**：识别你的任务正在哪种失效模式下运行，然后选能**结构性阻止**它的模式：

| 失效 | 解 |
|------|----|
| Goal Drift | → Fan-Out（子 Agent 独立上下文） |
| Self-preference | → Adversarial Verification |
| 开放式问题 | → Loop Until Done |
| 难评分 | → Tournament |

---

## 五、三个控制旋钮：`/goal` · `/loop` · Token 预算

Dynamic Workflows 可能很贵。三个控制把它从"酷但贵"变成"无人值守工具"：

| 控制 | 作用 | 最佳搭配 |
|------|------|---------|
| **/goal** | 设硬性完成条件 | Loop 模式——直到理论成立才停 |
| **/loop** | 按计划定期运行 Workflow | 工单处理、周报研究、定期验证 |
| **Token 预算** | 在 prompt 里告诉 Claude "use 10k tokens" | 没有预算限制时，膨胀到预期 5-10 倍 |

> 直接引用 Claude Code 团队：**"最佳实践仍在形成中。Dynamic Workflows 通常使用更多 token，请仔细考虑何时以及如何使用它们。"** 大多数传统编码任务不需要 5 个审查者的评审团。扪心自问：这个任务真的需要更多算力吗？常规 Claude Code 会话 5 分钟能搞定的，不需要 Workflow。

---

## 六、隔离模式（Quarantine）：处理不可信输入

任何读取不可信内容的 Workflow——工单、Bug 报告、用户反馈、爬取数据——必须假设内容可能包含 prompt injection。

**解法：隔离（Quarantine）**
- 读不可信内容的 Agent 被禁止使用高权限操作
- 执行操作的 Agent 不接触原始内容

适用场景：处理用户提交内容、爬取网页、第三方 API 输出。**如果内容不是你或信任的队友写的，隔离它。** 一个 30 行的只读 Agent 成本几乎为零，但去除了一整类 prompt injection 风险。

---

## 七、保存 Workflow：有两条路

按 `s` 保存 Workflow → 保存在 `~/.claude/workflows/`：

1. **留在本地**——在自己的各项目间复用
2. **打包为 Skill**——把 JS 文件放在 Skill 文件夹中，在 SKILL.md 引用，任何安装该 Skill 的人都能跑

**实用细节**：打包为 Skill 时，prompt Claude 把 Workflow 当**模板**而非一成不变的脚本。这样 Claude 能根据具体任务调整 Workflow 形态，同时保持整体结构。对"深度验证"或"工单处理"这类需要弹性的 Workflow 尤其重要。

---

## 八、浪费 token 的 8 个常见错误

1. **不该用的时候用**——常规 Claude Code 会话 5 分钟能搞定的，不需要 5 个审查者
2. **没有 Token 预算**——无上限，膨胀到预期的 5-10 倍
3. **一个 Agent 干两份活**——工作和验证必须分开，self-preference 让验证者偏爱工作者
4. **parallel() 和 pipeline() 混用**——屏障很重要，parallel 等所有，pipeline 流式
5. **Loop 不配 /goal**——Workflow 在第一个软完成点就停止，/goal 强制硬完成
6. **无隔离处理不可信内容**——一旦处理用户提交内容，隔离不是可选项
7. **用绝对评分排序**——比较判断更可靠，用 Tournament
8. **保存工作流但不打包 Skill**——每周反复写相同形状。按 `s` 保存，打包为 Skill

---

## 总结

Dynamic Workflows 不是"更贵的 Claude Code 会话"。它们是**结构性解决单上下文退化问题**的架构模式。

用好它们的关键：
1. 识别失效模式（Laziness / Self-preference / Drift）
2. 选对应的模式（Fan-Out / Adversarial / Loop）
3. 上控制（/goal + Token 预算）
4. 隔离不可信输入
5. 打包为 Skill 复用

> "大多数传统编码任务不需要一个 5 位审查员的评审团。" — Claude Code 团队

---

*整理时间：2026-06-04 | 来源：@0xCodez on X*
