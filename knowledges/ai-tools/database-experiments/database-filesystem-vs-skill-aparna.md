---
title: "数据库文件系统 vs Skill — Aparna Dhinakaran 的 Agent 数据交互实验"
tags:
  - agent-architecture
  - database
  - filesystem
  - skill
  - agent-harness
  - evals
  - arize
  - chromafs
date: 2026-06-04
source: "https://x.com/aparnadhinak/status/2062233330196926720"
authors: Aparna Dhinakaran & Sufjan Fana
---

# 数据库文件系统 vs Skill — Agent 数据交互实验

> **来源：** [Aparna Dhinakaran 的 X 长文](https://x.com/aparnadhinak/status/2062233330196926720)  
> **核心问题：** Agent 需要从数据库取数据时，是应该把数据库包装成文件系统（ChromaFS 模式），还是给 Agent SQL + 真实 Shell？

---

## 背景：ChromaFS 模式的流行

Mintlify 构建了 **ChromaFS** 以改进他们的文档助手：

- **问题：** 纯向量 RAG 只能返回匹配嵌入的 chunk。如果答案跨多页，或需要精确语法但不在 top-K 里 → Agent 卡住
- **方案：** 把 Chroma 向量数据库包装成**文件系统接口**——Agent 跑 `ls`, `cat`, `grep`，底层是数据库读取
- **模式传播：** 其他团队开始复制这个模式，也把 SQL 数据库包装成文件系统

> 前提：Agent 对它训练数据中见过的接口最熟练，所以应该给它一个熟悉的外壳。

---

## 研究假设

> **Skill（本地化）> 文件系统抽象**：让 Agent 通过 skill 从数据库选择性拉取所需数据，然后给予完整的本地 Bash 工具集，应该胜过在数据库内部构建 Bash 式接口。

**核心理由：**
- 许多 shell/pipe 工作流只有在**本地完整形式**下才存在
- 在数据库 abstraction 背后难以完整复现
- 数据库仍擅长：TB 级搜索和过滤
- 本地工具更适合：迭代式、多分支的分析循环

**模式：刻意交接（deliberate handoff）**
```
Agent 用数据库做宽范围检索 → 物化一部数据到本地 → 深入分析 → 如需再拉取下一批
```

---

## 两种架构对比

| 维度 | PostgresFS（文件系统抽象） | Skill（SQL 工作流） |
|------|--------------------------|-------------------|
| **实现方式** | 5 个动词 (ls/cat/grep/find/cd) → Postgres SELECT | 一个小脚本：接一条 SQL，写入本地文件 |
| **读路径** | 每次读都是一次数据库往返 | 一次性 SQL 查询落地到文件 |
| **写能力** | 只读（EROFS，无 /tmp） | 物化后全部本地，可写可复用 |
| **工具集** | 标准 coreutils filters (sort/uniq/awk/sed/cut/comm/join...) | 真实完整 Bash 环境 |
| **过滤方式** | filters 在 pipe 内本地运行；reads 穿过 adapter 变成 SELECT | 全部在本地文件上操作 |
| **维护成本** | 大型定制层（adapter + 粗过滤器 + cache + 正则翻译器） | 一个 prompt + 一个小脚本 |

### Orientation Prompt 的设计差异

**PostgresFS prompt：**
- 给一个决策表：问题形状 → shell 惯用写法
- 告诉 Agent 尽量少做 doc 读取

**Skill prompt：**
- 建立纪律：如果答案能浓缩为小结果（COUNT / GROUP BY / INTERSECT）→ 在 SQL 里算完直接返回
- 否则：把候选行全投影到文件 → 本地组合加工
- 不要将查询脚本当搜索工具用——频繁的缩小查询意味着你一开始投影得太少

---

## 实验设计

### 测试环境
- **Agent loop：** Claude Agent SDK（两侧一致）
- **模型：** claude-sonnet-4-6（执行），claude-opus-4-7（裁判）
- **数据库：** Arize AX 文档的冻结快照
- **每种方法：** 10 个问题 × 10 次运行 → 取中位数
- **计时范围：** Agent 的调查循环（从 prompt 到最后一个 tool call）
- **评分：** 精确答案程序化评分 + LLM judge 按固定 rubric

### 10 个问题（三档难度）

| 层级 | 描述 | 读路径特点 |
|------|------|-----------|
| **Simple**（简单） | 一次或少量读取 | 1-2 次读取 |
| **Mid**（中等） | 跨多页聚合 | 聚合+多读 |
| **Complex**（复杂） | 提取/综合，答案取决于 Agent 必须收集多少次独立读取（**locality pressure**） | 多轮独立读取 |

---

## 结果

### 延迟：几乎平手

- 两侧延迟差距不到 2×
- 延迟差异的真正驱动因素是**读取次数**，而不是层级

| 问题 | 胜方 | 原因 |
|------|------|------|
| q2, q5, q6 | PostgresFS | 进程内调度快 |
| q8, q9, q10 | Skill | 读取次数堆积时本地优势显现 |
| q1, q3, q4, q7 | 平手 | — |

**延迟差异只在正确切片下才可见：** 大部分时间是 skill 加载和答案合成，架构只影响中间「调查循环」那一段。

### 准确率：Skill 胜出

| 架构 | 准确率 |
|------|--------|
| PostgresFS | **93/100** |
| Skill | **99/100** |

差距集中在 **2 个中等问题**——PostgresFS 在这两题上的准确率明显低于 Skill：
- **q7（综合题）：** 6/10
- **q4（计数题）：** 7/10

其他所有题目两侧都是 9/10 或 10/10。

---

## PostgresFS 为什么输了

> 输的不是缺少操作符——所有 filter 都有。输的**在读取路径上**。

### 核心问题 1：Locality Collapse（局部性崩溃）

每次文档读取都是数据库往返（伪装成 shell 动词），即使从缓存返回也每次支付查询解析 + 序列化 + 传输的开销。

一个 `grep -rl` 后面跟着一连串 `cat`——在真实文件系统上几乎是瞬时——变成了一个序列化的往返序列。

**Skill 只支付一次往返：** 一条查询把结果落地到本地文件，之后所有操作都是本地的、可组合的，不再有数据库跳转。

### 核心问题 2：Composability Capped at One Pass（单次通过限制）

- 单次 pipe 两者都行
- 但需要**第二次通过**数据时不行——just-bash 没有 process substitution `<(...)`，且 adapter 是只读的（无 /tmp，EROFS），无法 staging 和复用
- 双输入族（`comm`, `join`, `diff`, `paste`）死了——尽管 `comm` 在 allowlist 里

> **本质：Skill 物化一次，自由复用；PostgresFS 每次看数据都付一次往返。**

### 陷阱：「加东西直到它变好」

自然反应是"那给 abstraction 加功能直到追平为止"。这是一个陷阱。

> 每一步走向更真实的读取路径（更好的 prefetch、更接近的 grep 语义、真正的 cache）都在**走向真实的文件系统**——也就是 Skill 已经到达的位置，只是走了一条更不干净的路。

而且你写的这段往返代码和你每次读都要往返的代码是**同一段代码**——维护成本和性能成本是同一个成本。

---

## 结论

### 三个 takeaways

| # | 结论 | 说明 |
|---|------|------|
| 1 | **性能平手时，看维护成本** | PostgresFS 是大型定制层（adapter + coarse-filter + cache + regex translator），随 schema 变化必须保持正确。Skill 只是一个 prompt + 小脚本 |
| 2 | **按问题形状分层看准确率，否则会带病发布** | 整体 93 vs 99 看起来差距小，但按题分解后才看到 PostgresFS 特定题型只有 60-70% |
| 3 | **奔真实存储去，别奔好看形状去** | "宿主机 shell 实际读什么" > "我想暴露什么形状"。熟悉的 interface 是必要条件，不是充分条件 |

### 通用化

> *"Wrap the store as a filesystem" vs. "give the model the store's real query language plus a real shell"*

这个决策适用于 Chroma、Mongo、BigQuery、ClickHouse——**查询语言是次要的**。

**不变的陷阱：** 每次 fake 一个文件系统，你就签下了维护一个文件系统的债。你越把它往真实文件系统的方向推，你越是在重建真实文件系统——只是更慢。

---

## 方法论亮点：Eval 驱动架构决策

这个实验用 **Arize AX** 做 eval，将架构选择从「猜测」变成「知道」。

关键设计：
- 精确对比 Agent 的**调查循环**（从 prompt 到最后一个 tool call），而非整个运行时间（排除技能加载和答案合成等一次性开销）
- 按题目形状而不是总分来看结果
- 程序化评分 + LLM Judge 双重校验

---

## 关键金句

| 金句 | 主题 |
|------|------|
| "Every step toward a faithful read path is a step toward real files on a real filesystem, which is the skill, reached less cleanly." | 读路径 |
| "We bet on composability and speed; they turned out to be one property: whether the agent works from a local copy." | 合并属性 |
| "A familiar interface is necessary, not sufficient." | 接口设计 |
| "Every time you fake a filesystem, you sign up to maintain one." | 维护成本 |
| "Look at per-question pass rates, or you'll ship the failure without seeing it." | Eval 方法论 |

---

*整理于 2026-06-04，基于 [aparnadhinak 的 X 长文](https://x.com/aparnadhinak/status/2062233330196926720)*
