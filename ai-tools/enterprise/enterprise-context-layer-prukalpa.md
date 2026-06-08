---
title: "企业 Context Layer 完全指南 — Prukalpa 的 AI 架构蓝图"
tags:
  - context-layer
  - enterprise-ai
  - enterprise-architecture
  - knowledge-graph
  - ontology
  - skills
  - context-engineering
  - ai-governance
date: 2026-06-03
source: "https://x.com/prukalpa/status/2061512556590809342"
authors: Prukalpa (Context & Chaos)
---

# 企业 Context Layer 完全指南

> **来源：** [Context & Chaos — Prukalpa 的 X 长文](https://x.com/prukalpa/status/2061512556590809342)  
> **核心命题：** 企业 AI 的胜负不在于模型，而在于组织级 context 能否积累和复用。

---

## 核心命题

> *"赢得下一个十年的公司不是拥有最好模型的公司——大家都能访问同样的模型。而是那些 context 能复利的公司：第十个 agent 比第一个聪明太多，因为它底下的层每用一次都在学习。"*

---

## 一、Context 的三种类型

一个在企业内部运作的 AI agent 需要三种 context：

| 类型 | 含义 | 通俗理解 |
|------|------|---------|
| **Knowledge**（知识） | 业务的"地图"：实体、定义、指标、关系、术语 | 让人类和 AI 对"客户"、"收入"说同一件事 |
| **Expertise**（专长） | 工作实际的**执行方式**：流程、剧本、know-how | 怎么结账、怎么升级工单——藏在 SOP、Slack 和少数人脑子里 |
| **Norms**（规范） | 可接受行为的**规则**：政策、权限、审批路径、合规约束 | 什么允许做、什么需要审批、什么数据不能出地区 |

> **后续映射：** Knowledge → 数据和语义；Expertise + Norms → Skills

---

## 二、企业 Context Layer 是什么

> **定义：** 把知识、专长、规范转化为 AI 可用的机器 context 的系统。跨异构的数据、业务系统和 AI 工具，让 agent 在共享语义下运作。

本质是一个**共享的企业大脑（shared enterprise brain）**——每个 agent 都能从中获取、学习、贡献。这使得**第十个 agent 远好于第一个**。

架构分两大部分：

---

## 三、Part 1：核心 Context Substrate

三个紧密集成的组件，回答 agent 行动前需要知道的三个问题：

```
有什么可信的数据？ → AI-ready data + Knowledge graph
是什么意思？怎么关联？ → Semantics + Ontology
这里的工作怎么做？什么允许？ → Skills
```

### 1. AI-ready Data + Knowledge Graph

企业数据和知识资产的**可信、AI 就绪**表示：

- 结构化数据 → 机器可读（加描述、join path、人们通常怎么查）
- 非结构化知识 → 有治理地可访问

**被低估的一环：Canonical Knowledge（规范知识）**
- 战略文档、品牌声音指南、产品定位、组织架构
- 资深员工脑子里、新员工前 90 天在吸收的东西
- **忽略它的 context layer 会产生能回答问题但不知道公司要干什么的 agent**

### 2. Semantics + Ontology

| 概念 | 回答的问题 | 示例 |
|------|----------|------|
| **Semantics（语义）** | 这是什么意思？ | 术语表、指标定义、"活跃客户"是什么 |
| **Ontology（本体论）** | 概念之间怎么关联？ | 客户→账户→交易，产品→SKU→库存 |

> 没有语义，检索是脆弱的——agent 拿到了字符串但无法解释。  
> 新的突破：**AI 现在能以业务节奏半自动构建和策展这些知识**，读取 query log、调和矛盾文档——一个"活的知识模型"终于在大企业级可行。

### 3. Skills — 可复用的过程知识和规范

> **Skill 是新的原语，就像函数对逻辑的贡献。**

**函数类比：**
- 在软件有函数之前，逻辑散布在各处，每次重新推导、半记得、各处不同
- 函数让逻辑变成可命名、可版本化、可测试、可从任何地方调用
- **从那一刻起，软件开始复利而不是被重写**

**企业中过程知识的现状就卡在函数出现之前的那一步。** 结账流程、线索筛选、退款异常处理——活在 Notion 的 prompt 里、部落记忆里、每个人即兴发挥的步骤里。

**Skill = 那一步之后的版本：** 可复用、可版本化、可测试的"how-to"单元，带着自己的触发条件、边界案例和负责人。

> 当组织把 skill 作为一等资产而不是散落的 prompt——过程知识停止被每个 agent 和每个员工重新推导，开始复利。

**两个难点（后面第五项能力解决）：**
- **建库难** → 采矿问题
- **维护难** → 生命周期问题

---

## 四、Part 2：五大能力

Substrate 定义 context layer 是**什么**，五大能力定义它**做什么**。

### 1. Context Mining — 大多数业务 context 从未被写下来

**真相：** 如果你想了解公司认为它怎么运行 → 读文档。想了解它**实际**怎么运行 → 观察系统。

**采矿语义：** AI 读 SQL query 历史，发现 Sales 和 Finance 对"年度经常收入"定义不同 → 自动标记冲突供人类做全公司统一决策。

**采矿 skill：** 更难的层级——大多数过程知识从未被写下来。四种方法：
- 从 agent session 中提取（工作完成后自动化）
- 从事件日志构建过程地图
- 在 agent 失败时捕获 context
- 运行结构化 AI 访谈来挖掘观察不到的判断

> AI 做重活（挖掘），人类做决定（哪个候选变得 canonical）

### 2. 开发生命周期 — Context 也需要自己的 SDLC

> 软件工程有 SDLC 来管理代码如何构建、review、版本化和部署。想 AI-native 的公司需要**CDLC（Context Development Lifecycle）**来管理 context。

流程：创建 → 测试 → 审批 → 部署 → 退役

**关键：变更传播（Change Propagation）**
想象一个场景：CMO 更新了公司核心 ICP（理想客户画像）定位。这会级联影响到所有下游——社交媒体 skill、SDR pitch skill、分析师 call skill。

| 变更传播策略 | 说明 |
|------------|------|
| 自动传播 | 所有依赖自动更新 |
| 队列待审 | 每个下游 owner 审查后确认 |
| 旧版继续运行 | 直到有人认证新版 |

> **这不是理论问题**——它们决定 layer 是复利还是自相矛盾。**下一波创新的核心看起来更像组织设计，而不是 prompt 工程。**

### 3. 复利学习循环 — 第十个 agent 比第一个聪明

**记忆分类体系（关键架构性区分）：**

| 记忆类型 | 归属 | 说明 |
|---------|------|------|
| **Working Memory**（工作记忆） | Agent harness 层 | 即时执行面 |
| **Episodic Memory**（情景记忆） | Agent harness 层 | 结构化的执行记录 |
| **Semantic Memory**（语义记忆） | Context layer | 系统保留的持久知识 |
| **Procedural Memory**（过程记忆） | Context layer | 工作如何完成的规则书 |

**学习循环机制：** 临时经历 → Eval / 修正 / 人工审查 / 认证 → 变为持久 context

例：客服 agent 收到客户提到儿子有乳糖不耐。那一刻 → 在工作记忆中（working memory），留下情景痕迹（episodic trace）。系统验证并升级后 → 成为客户档案中的语义记忆（semantic memory），未来 agent 无需重新发现。

> 每一次交互让 layer 更聪明，layer 越聪明，未来每个 agent 表现都更好。

### 4. 激活与检索 — 一个 layer，多种方言

Context 若要创造价值，必须能到达正确的人类或 agent——

| 消费方式 | 接口 |
|---------|------|
| Copilot | MCP / API |
| 搜索 | 向量检索 |
| 分析 | SQL / LookML |
| 代码编辑器 | MCP |
| Agent 框架 | MCP / API / 图查询 |

> 短期需要翻译——即使在 Google 生态内，Looker 要 LookML 模型，Gemini Enterprise 要 skill 文件。**胜出的架构不会强迫每个生态说一种语言，而是把 canonical context 翻译成多种本地方言。**

### 5. Context 治理和可观测性

其他四项能力让 layer **可用**。治理让它**可信**。

**五个必须全生命周期贯通的治理关切：**

| 关切 | 追问 |
|------|------|
| **质量（Quality）** | 定义或 skill 是否经过 owner 验证和测试？ |
| **漂移（Drift）** | 它底下的世界变了没有？ |
| **血缘（Lineage）** | 它从哪来，什么依赖它？ |
| **版本（Versioning）** | 能回滚吗？两个 agent 意见不同是因为在不同版本上吗？ |
| **审批（Approval）** | 谁可以合并影响多个团队的变更？谁认证新 playbook 安全可复用？ |

> 没有清晰的问责循环 → layer 变成另一个数据湖——没人信任的 artifact 坟场。  
> 有了问责循环 → 成为整个 stack 信任的共享大脑。

---

## 五、Context Layer 不是什么

| 容易混淆的概念 | 区别 |
|--------------|------|
| **Semantic Layer** | 只是 context layer 的一部分，仅限指标和维度的分析范围。而 context layer 覆盖 data + semantics + skills + 五大能力 |
| **Data Catalog** | 为人类建的——帮分析师找表。Context layer 的 producer 和 consumer 是 AI，因此必须包含 skills，激活层必须说 MCP / vectors / graphs / APIs |
| **Long-term Memory** | 只是五大能力之一的一小部分。Context layer 是更大的系统——决定什么从记忆晋升为共享、有治理的企业知识 |

---

## 六、市场格局预览

当前 context layer 公司地图：很多 logo 挤在一个类别。

| 类别 | 说明 |
|------|------|
| **Agent builders** | layer 局限于自己垂直领域 |
| **平台公司** | layer 局限于产品内的数据 |
| **专业厂商** | 只做 substrate 的一个组件（memory / process mining / vector retrieval / semantics） |

> 每个都在一件事情上做得很好。但大多数会被集成进一个 context layer，而不是自己变成一个。

**预测：** Context layer 会比大多数领域更快/更猛整合——因为它的核心价值就是**共享**。一家有四个 context 孤岛的财富 500 强（CS 一个、分析一个、memory 一个、process mining 一个）——没有 context layer，只有四个 context 孤岛，复利循环在 context 不能跨 agent 流动时就断裂了。

> **胜出的公司将集成全部三个 substrate 元素，并以一个连贯循环运行全部五项能力。**

---

## 七、关键金句

| 金句 | 主题 |
|------|------|
| "The context layer is not a feature you ship. It is the foundation everything else stands on." | 定义 |
| "A skill is the new primitive that does for procedural knowledge what code did for logic in software." | Skills |
| "Before software had functions, logic lived as instructions you re-derived every time." | 函数类比 |
| "The next era of innovation will look much more like organizational design than prompt engineering." | 未来发展 |
| "A data catalog was built for humans. The primary consumer of a context layer is AI." | 区分 |
| "The companies that win will be the ones whose context compounds." | 核心命题 |
| "Canonical knowledge is the narrative that defines how the company thinks, sells, builds, and speaks." | 被低估的一环 |
| "AI does the heavy lifting; humans decide." | 采矿原则 |

---

*整理于 2026-06-03，基于 [Prukalpa 的 X 长文](https://x.com/prukalpa/status/2061512556590809342) — Context & Chaos Newsletter*
