---
title: "Rethinking Search as Code Generation"
authors: ["Perplexity Research"]
tags: ["search-as-code", "SaC", "agent-harness", "perplexity", "search-architecture", "agentic-search", "code-generation", "benchmarks"]
source: "https://research.perplexity.ai/articles/rethinking-search-as-code-generation"
date: 2026-06-01
---

# Rethinking Search as Code Generation

> Evolving search from monolithic services to programmable primitives for the era of agent harnesses.

## 核心命题

搜索是 AI 系统的核心基元（core primitive）。前沿模型能力增长迅速，但仍然需要访问新鲜、准确、精选的外部知识。传统搜索管线在 agent 时代日益过时——传统搜索回答查询，但今天的 agent 完成任务需要 task-specific 的检索策略，agent harness 需要直接在内部定义这些策略。

在 Perplexity Computer 的实践中，单个任务可以在几分钟内调用数百甚至数千次检索操作——这对人类不可能，但对 agent 完全自然。

**核心结论：搜索本身必须 agentic，其构建块应直接作为 SDK 暴露在 agent harness 中。** Perplexity 推出 **Search as Code (SaC)** 作为新的参考搜索架构。

## 传统搜索的僵化（三个失败模式）

传统搜索引擎围绕一个控制点设计：查询参数（query parameters）。模型只能控制输入，下游管线由搜索引擎预定义逻辑决定。

1. **Coarse Context（粗糙上下文）**：AI 模型对上下文质量和紧凑度敏感。单一管线无法在所有查询上表现最优。需要精准信息时却获得高召回全量结果；需要多种策略时被迫串行调用同一次优管线→成本膨胀+上下文污染。

2. **Failure to Leverage Domain Knowledge（无法利用领域知识）**：模型可能有领域知识（训练、Agent Skill、记忆等）应指导搜索策略。但僵化接口阻止模型利用这些知识——除非恰好能通过查询参数实现。

3. **Inefficient Control Flow & Context Pollution（低效控制流+上下文污染）**：许多搜索工作流并非天然串行，需要 fan-out、并行抓取、去重等操作。通过模型轮次强制串行增加延迟，中间状态污染模型上下文→性能下降+频繁 compaction。

在 function calling / MCP 时代，每次搜索操作均需 LLM 推理回合，开发者自然倾向在单次回合中获取尽可能多的结果。但今天的前沿模型建立在 code-first harnesses 上，可以在一分钟内执行数千个动作，搜索系统尚未完全释放这一潜力。

## SaC 架构：三层耦合

核心原则：搜索应对 AI agent 来说 **native programmable**。agent 不应被限定在预定义搜索管线集合中，而应能用可组合的构建块构建 task-specific 管线。

SaC 中，**没有一个检索操作是通过 function calling 或 MCP 接口分发的**。所有操作均通过模型生成的 Python 代码编排。

### 第一层：Models — 控制平面

模型推理用户（或父 agent）的指令，分解为任务，决定每个任务需要的检索和处理管线，并生成代码实现这些管线。

### 第二层：Compute Sandboxes — 确定性计算

安全代码执行运行时，提供控制流、批处理、重试、过滤、join、聚合等确定性操作画布。

**关键设计：跨轮次的中间状态管理**

- **Persistent filesystem + explicit serde**：模型在生成代码中包含序列化/反序列化步骤，跨轮次显式传递状态
- **REPL 模式**：持久化运行时本身，变量直接在内存中跨轮次引用

结论：两种方案在日常使用中表现相似，但 **filesystem-based serde 在长轨迹上更可靠**。要求模型声明式（而非隐式）传递状态，有助于模型更有效地管理状态。

### 第三层：Agentic Search SDK — 可组合基元

将 Perplexity 搜索栈重新架构为模块化、可组合的基元。**不是将现有搜索 API 打包为库**，而是重建更低层次的构建块。

**运行时选择**：Python（vs Rust/TypeScript/Bash），经过内部测试确认最自然选择。

**持续优化**：通过自动化研究循环（autoresearch loop）持续优化 SDK 对前沿 LLM 的可消费性，优化指标包括延迟、代码生成质量、整体任务性能。

### 代码作为编排器与能力填充

代码不仅能编排已有能力，还可以填补搜索栈中不存在的能力缺口。SDK 提供最基础基元，模型可即兴写代码构建额外组件。

举例：复杂正则匹配无法通过搜索系统自身查询语法高效实现。SaC 中，模型可生成程序：并行 SDK 调用收集结果超集 → SDK 去重 → 写代码精确正则筛选。

## 案例研究：CVE 厂商公告

现实世界任务：识别并描述 2023–2025 年超过 200 个高严重度 CVE。每条记录必须引用受影响厂商自己的公告，写明产品、修复版本，并证明修复版本锁定到具体 CVE。

**结果**：SaC 准确率 100%，总 token 使用量下降 **85.1%**（从 288.7K token 降至 42.9K token）。测试的非 Perplexity 系统得分均低于 25%。

三段风格化代码示例展示 SaC 的可编程性：

1. **纯编排**：将源-类别规则直接编码到查询计划中，只接受厂商拥有的公告格式
2. **LLM 作为中间规划子程序**：总结哪些厂商-年份对产生足够候选页面，要求针对性优化，执行前验证每个查询
3. **结果验证器**：代理通过代码生成完全定义验证逻辑——通过 CVE 去重、拒绝聚合器 URL、丢弃弱版本证据、持续回填直到满足记录数下限

## 评估结果

### 基准测试集

5 个基准，覆盖知识密集型 AI 工作流：

| 基准 | 观察指标 |
|------|---------|
| DeepSearchQA (DSQA) | 准确率 |
| BrowseComp | 准确率 |
| Humanity's Last Exam (HLE) | 准确率 |
| WideSearch | F1 score |
| WANDR（新） | 综合分数 |

WANDR 专注于困难的"广域研究"任务，需要搜索、计算、模型推理的精心编排。受 Perplexity Computer 实践的启发。

### 对比系统

- Perplexity (SaC) — GPT 5.5 (high reasoning)
- OpenAI — GPT 5.5 (high reasoning)
- Anthropic — Opus 4.7 (high reasoning)
- Exa Agent — effort=high
- Parallel Tasks — ultra4x

### 完整分数表

| 基准 | Perplexity (SaC) | OpenAI | Anthropic | Exa | Parallel |
|------|:---:|:---:|:---:|:---:|:---:|
| DSQA | **0.871** | 0.733 | 0.815 | 0.530 | 0.810 |
| BrowseComp | **0.805** | 0.720 | 0.598 | 0.380 | 0.560 |
| HLE | **0.612** | 0.614 | 0.566 | 0.387 | 0.515 |
| WideSearch | **0.651** | 0.522 | 0.590 | 0.471 | 0.584 |
| WANDR | **0.386** | 0.130 | 0.152 | 0.057 | 0.126 |

SaC 在 4/5 基准上领先（HLE 上基本并列第一）。

### 关键发现

- **WANDR 优势最大**：SaC 是次优系统的 **2.5×**，但仍远未饱和，说明复杂的水平搜索工作流需要更多研究突破
- **SaC vs 非 SaC 架构**（相同基础设施）：DSQA 绝对增益 +19.77 pp（29%），WANDR 相对增益最大 +12.00 pp（45%）
- **性价比前沿**：在 DSQA 和 WideSearch 上，SaC 的低推理设置比所有非 SaC 系统更便宜且性能更优；中推理设置在 <$1/任务下超越所有非 SaC 系统

## 哲学：更广泛的计算架构变革

SaC 反映了一个更广泛的软件设计变革：

> **两种计算形态**：确定性指令（传统 CPU 运行时）与 token 空间推理（前沿模型）。最强大的计算系统将结合两者，而非二选一。

搜索是这种混合架构的天然试验场：
- **模型**决定需要什么证据、如何消解不确定性
- **确定性运行时**负责批处理、并行、过滤、排序、聚合
- **搜索基础设施**作为通用 I/O 层，提供每秒数千次的信息操作手柄

三个层次缺一不可。SaC 之所以有效，是因为推理、确定性计算和 I/O 共同设计，相互增强。

## 与已读内容的连接

1. **与 Rohit "The Harness Is Everything"（理论基础层）**：SaC 是这篇论文的完美工程化实例。Rohit 主张 harness 应提供完整可编程环境（+BREADS 原则）；SaC 具体展示了如何将搜索栈原子化为 SDK 基元，让代码生成代替串行函数调用，这正是 harness 作为"执行环境"哲学在搜索领域的实践。

2. **与 Garry Tan "Stop Building Foxconn Factories"（哲学层）**：Garry Tan 警告"为 agent 筑笼子"的陷阱。SaC 的反向验证是教科书的——它故意打破"预定义管线"的笼子，让 agent 在搜索中拥有完整可控性，正是"自由 vs 囚笼"哲学的搜索域具体化。

3. **与 Businessbarista "Software Factory"（操作层）**：SaC 的 Agent Skills（<2000 token 的 SKILL.md）、autoresearch 循环、SDK 持续优化，与 Software Factory 的质量工程理念高度一致。Perplexity 就是在运行一个搜索领域的事实性"软件工厂"。

4. **与论文 2605.30621 "Harness Evolution"**：SaC 代表了从"搜索即服务"到"搜索即代码生成"的范式跃迁，完全符合 harness evolution 论文描述的第三阶段——系统不再暴露固定 API，而是暴露可编程基元让 agent 自主组合。

## 关键术语

| 术语 | 含义 |
|------|------|
| SaC | Search as Code，搜索即代码生成 |
| Agentic Search SDK | 将搜索栈拆解为可组合 Python 基元的 SDK |
| Sandbox | 安全代码执行环境，提供确定性计算 |
| Autoresearch Loop | 持续自动化优化循环，改进 SDK 和 Skills |
| WANDR | 新基准，专注广域研究型任务 |

## 意义与启示

- 搜索架构从"服务"到"程序"的范式迁移已从论文走向生产
- Function calling / MCP 只是过渡方案，code generation 是最终形态
- 性价比前沿比绝对性能更重要——SaC 在更低成本下实现更好结果
- Agent Skills + Autoresearch 的组合是让 LLM 掌握自定义 SDK 的关键工程模式
