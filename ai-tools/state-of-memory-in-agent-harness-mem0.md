---
title: "State of Memory in Agent Harness — 9 大 Harness 记忆系统全景分析"
authors: ["mem0 (@mem0ai)"]
tags: ["agent-memory", "agent-harness", "memory-benchmark", "claude-code", "codex", "copilot", "hermes-agent", "openclaw", "managed-agents", "mem0", "in-context-series"]
source: "https://x.com/mem0ai/status/2061822612398014782"
date: 2026-06-02
series: "In Context #11"
---

# State of Memory in Agent Harness

> Agent Harness 是 AI 软件真正运行的地方。Cursor、Devin、Claude Code、Codex——这些环境处理上下文、编排工具、协调 agent，以及越来越多地，管理记忆。Harness（而非模型）日益成为真正"发货"的产品。
>
> 记忆是 harness 设计变难的地方。

---

## 记忆的三层分类

文中明确区分三种不同的"记忆"，因为失效模式各有不同：

| 类型 | 生命周期 | 2026 生产部署 | 关键问题 |
|------|---------|:---:|---------|
| **Working Memory**（工作记忆） | 一次会话的 context window 内 | ✅ 全部 | Compaction：窗口满了留下什么？ |
| **External Memory**（外部记忆） | 持久化在权重之外（向量库、KG、文件） | ✅ 全部 | 检索质量、存储上限、跨会话 |
| **Parametric Memory**（参数记忆） | 编码进权重的知识（梯度下降训练） | ❌ 零生产部署 | 仍在学术阶段 |

> 认知科学中的语义/情节/程序记忆描述的是"存了什么"，这三层描述的是"存在哪里"。

核心引用的论文 **[arXiv:2604.27707](https://arxiv.org/abs/2604.27707)**（Contextual Agentic Memory is a Memo, Not True Memory）形式化了天花板：检索需要 Ω(k²) 个存储示例才能匹配参数记忆 O(d) 权重更新的效果。

---

## 9 大 Harness 记忆实现横向对比

### 1. Claude Code（Anthropic）

**两条路径：**
- **CLAUDE.md**：人类编写的配置（约定、指令），会话开始时读取
- **Auto-memory**：Claude 通过后台提取 agent 写入的笔记，存储在 `~/.claude/projects/<repo>/memory/`，核心是 **MEMORY.md**，上限 **200 行 / 25KB**，分四类（user/feedback/project/reference）

**检索机制**：每轮调用一个较小的模型，传入文件名和描述的清单，模型选择加载哪些文件。**无嵌入向量**，每轮最多 5 个文件，超过上限静默截断（被丢弃的文件得不到任何警告）。

**不足：**
- 检索按文件名而非语义，因此名字匹配但内容不相关的文件胜出
- 团队共享需要 TEAMMEM 标志，底层仍是本地、repo 范围的 markdown，无语义索引

### 2. Managed Agents（Anthropic 托管）

**架构特性**：会话是只追加的事件日志（append-only），从不修改——回滚和审计是架构级特性而非后期添加。记忆存储以文件系统形式挂载到 `/mnt/memory/`（每个工作区最多 8 个，每个 ~100KB）；每次写入是不可变版本；多个 agent 可并发共享一个存储，有可审计历史而非冲突。

**不足**：面向多 agent 协调和工作区规模，不擅长长期个人记忆。100KB 上限和工作区范围意味着跨会话个人上下文需要额外模式搭建。

### 3. Codex（OpenAI）

**数据模型**：一个 markdown 目录 `~/.codex/memories/`（**无 SQLite、无嵌入向量**）——`memory_summary.md`（优先读）、`MEMORY.md`（grep 按需）、`raw_memories.md`、`skills/`、`rollout_summaries/`。默认关闭（`features.memories` 标志）。

**写入两阶段**：
- Phase 1（per-rollout）：会话空闲 6 小时后，Codex 按严格 schema 提取，脱敏敏感信息，写入本地状态 DB（非记忆目录）
- Phase 2（global）：加锁，合并子 agent 合并/修补/丢弃差异并写入

**约束**：256 轮次上限，30 天时效剪裁，受速率限制感知

**读取**：非语义——摘要截断为固定 5,000 token 预算，其余通过 `grep MEMORY.md` 查找

**不足**：5,000 token 摘要静默截断；grep 仅子串匹配，同义改写的事实不可见；6 小时空闲门控意味着背靠背会话可能从不合并；状态仅本地；启动时 EEA、UK、瑞士不可用。

### 4. GitHub Copilot ✅（唯一有生产数据的）

**关键创新**：**Just-in-time citation verification**（实时引用验证）。记忆项是结构化对象（主题、事实内容、文件+行引用、推理依据），使用前 agent 验证引用是否与当前分支一致，如果代码已矛盾则重写记忆。记忆 28 天后自动过期。

**这是唯一有已发布生产数据的记忆系统**：
- A/B 测试（p<0.00001）
- PR 合并率从 **83% 升至 90%**（+7 个百分点）
- 代码审查 precision +3%，recall +4%

**不足**：引用的 schema 不能干净地容纳不可引用的事实（如"偏好最少抽象"），且严格 repo 范围。

### 5. OpenClaw

**原生记忆**：markdown（`MEMORY.md` + 带日期的每日日志）配合**按 agent 的 SQLite 索引 + 嵌入向量 + 混合检索**（70% 向量 + 30% BM25）。**原生支持语义检索**。

**问题**：窗口满时，OpenClaw 触发"静默内部轮次"让模型将重要内容写入磁盘——写入什么完全由模型在那一轮中决定，因此长期记忆是**选择性且不一致的**。Mem0 插件（`@mem0/openclaw-mem0`）解决了这个依赖：Auto-Recall 在每轮前注入相关记忆，Auto-Capture 在每轮后持久化每次交互。

### 6. Hermes Agent（NousResearch，135K ⭐）

**三层内置 + 八个可插拔 provider：**

| 层级 | 存储 | 特点 |
|------|------|------|
| Layer 1: 工作记忆 | MEMORY.md（2,200 chars）+ USER.md（1,375 chars），~1,300 token | § 分隔，利用率仪表盘，80% 容量时自动合并 |
| Layer 2: 技能 | 过程性文档 | 5+ 次工具调用任务后写入，定期整理 |
| Layer 3: 会话搜索 | SQLite FTS5 全量会话 | 按需总结 |

**不足**：持久记忆上限极小（~800 token），FTS5 仅关键词（"429 errors"不匹配"rate limiting"），本地限定。因此 Hermes 预置了 provider 插槽——使用 Mem0 后上限消失、检索变为语义、写入按用户 ID 隔离。

### 7. AWS Bedrock AgentCore

**三层异步提取策略**：语义事实、偏好、叙事摘要。提取 ~20-40s，检索 ~200ms。变更的事实标记为 INVALID 而非删除，保留谱系。

**发布分数**：LoCoMo 70.58，PrefEval 79，PolyBench-QA 83.02

**不足**：AWS 生态锁定，LoCoMo 分数远低于领先的记忆系统。

### 8. Windsurf

**Cascade 管理**：`~/.codeium/windsurf/memories/` 记录代码库模式和约定。无开发者工作流。

**不足**：捕获什么由 Cascade 决定而非开发者；工作区范围（跨项目不可见）；本地（无跨设备/团队共享）。

### 9. Devin（Cognition）

**两条路径**：
- **Knowledge**：人工筛选的触发-内容事实（无自动捕获）
- **DeepWiki**：参考文档（30 页，100 notes，每页 10,000 chars）

会话后 Devin 建议添加 Knowledge，但**必须人类批准**后才存储。

**不足**：审批关卡保持高质量但造成摩擦：不审查的团队什么也积累不了。上限有限，Knowledge 为 Devin 定制，不能迁移到其他工具。

---

## 记忆基准测试的缺陷

### LoCoMo — 最差的常见基准
- 仅 10 个对话，比较不可靠
- 许多问题不需要记忆（简单 grep 基线即可达 ~74%）
- 对抗性问题与目标有表面相似性，模型靠模式匹配获胜

### LongMemEval — 仍然可以
500 个精选问题，跨越五种能力（信息提取、多会话推理、时间推理、知识更新、弃权），扩展方向 1.5M token；仍以召回为中心但是真正的测试。

### 深层问题：它们都没测什么
- **[MemoryArena](https://arxiv.org/abs/2602.16313)**（Stanford/UCSD/Princeton）：测试必须**指导行动**的记忆。在 LoCoMo 和 LongMemEval 上接近饱和的系统在这里失败
- **[Anatomy of Agentic Memory](https://arxiv.org/abs/2602.19320)**：形式化批评——接近饱和，测量相似性而非任务效用
- **[BEAM](https://mem0.ai/blog/what-is-beam-memory-benchmark-the-paper-that-shows-1m-context-window-isnt-enough)**（ICLR 2026）：**唯一为生产规模设计的基准**（10M+ token），大多数系统不报告

**诚实结论**：领域需要新的记忆基准，排行榜分数应被批判性看待。

---

## 研究揭示的未解决问题

### 稳定性-可塑性困境重新定位
转向外部记忆并未终结灾难性遗忘。**[arXiv:2604.27003](https://arxiv.org/abs/2604.27003)**（When Continual Learning Moves to Memory）表明新旧记忆争夺检索槽恰好如它们曾经争夺权重：来自简单任务的原始轨迹损害了更难任务（前向迁移 −9.5%）。

### 选择性遗忘未解决
**[MemoryAgentBench](https://arxiv.org/abs/2507.05257)**（ICLR 2026）列出四种能力；系统能处理检索但不能处理选择性遗忘（遗忘过时事实的同时保留其周围结构）。

### 记忆是攻击面
- **[arXiv:2604.01350](https://arxiv.org/abs/2604.01350)**（No Attacker Needed）：**57–71%** 跨用户污染（正常使用下）
- **[arXiv:2601.05504](https://arxiv.org/abs/2601.05504)**：投毒攻击成功率 6–38%

---

## 共同缺陷模式

| 缺陷 | 具体表现 |
|------|---------|
| **存储有上限且本地** | Claude Code 25KB，Hermes 2,200 chars，Codex 5,000 token load |
| **检索以关键词为主** | Claude Code 按文件名，Codex 靠 grep，Hermes 靠 FTS5 |
| **语义检索的两个** | OpenClaw（本地+合并限制）、AgentCore（云锁定） |
| **Harness 范围** | Claude Code 的记忆对 Codex 毫无意义 |
| **陈旧处理** | 几乎不存在（Copilot 除外） |
| **隔离** | 事后考虑 → 57–71% 污染率 |

---

## Mem0 的定位

Mem0 是为**harness 边界不是问题终点**的场景构建的：

**架构**：混合系统——向量存储（语义检索）+ 知识图谱（关系推理）+ key-value（快速元数据）

**v3 算法**（2026 年 4 月）：
- 单次 ADD-only 提取
- 多信号检索（semantic + BM25 + entity linking 一次完成）
- 实体链接在向量存储内部完成，放弃 v2 的外部图数据库

**性能**：~6,900 tokens 和 1.44s 每次查询，对比全上下文检索的 ~26,000 tokens 和 17.12s

**覆盖缺口**：
- 无上限的外部存储
- 多信号检索（措辞不同也能找到上个月的讨论）
- 按身份隔离的命名空间（瞄准 57–71% 污染率）
- 跨 21 框架 + 20 向量存储

---

## 与已读内容的连接

1. **与 Rohit "The Harness Is Everything"**：本文是最直接的工程化落地续篇。Rohit 从理论层面论证 harness 的边界（BREADS 原则），Mem0 从实践层面展示 harness 边界正是记忆问题的根源——记忆被限定在 harness 范围内，因此跨 harness 不可移植。

2. **与 Perplexity SaC 文章**：SaC 讨论的是检索操作本身的编程化（将搜索栈暴露为 SDK），本文讨论的是检索结果的持久化与跨会话记忆——两者正好构成 agent 信息流的上下游：SaC 控制如何获取信息，Memory 控制如何记住已获取的信息。

3. **与 SkillOpt 文章**：SkillOpt 改进的是 agent skill（行为指令），本文讨论的是 agent memory（过去的知识和上下文）。两者是 agent 长期改进的两条独立路径：skill 决定 agent"怎么做"，memory 决定 agent"知道什么"。

4. **与 Garry Tan "Stop Building Foxconn Factories"**：记忆系统的现状（bounded local + keyword search + harness-scoped）正是"foxconn factory"在记忆维度的体现。Mem0 的跨 harness 方案就是在拆这个笼子。

5. **与论文 2605.30621 "Harness Evolution"**：本文的 9 个 harnesses 记忆实现对比，实际上映射了该论文描述的三阶段——从无记忆（早期）→ 本地 bounded 实现（今天）→ 跨 harness 持久化记忆基础设施（Mem0 代表的方向）。

## 关键参考文献

- arXiv:2604.27707 — Contextual Agentic Memory is a Memo, Not True Memory
- arXiv:2602.16313 — MemoryArena (Stanford/UCSD/Princeton)
- arXiv:2602.19320 — Anatomy of Agentic Memory
- arXiv:2604.27003 — When Continual Learning Moves to Memory
- arXiv:2507.05257 — MemoryAgentBench (ICLR 2026)
- arXiv:2604.01350 — No Attacker Needed: Cross-User Contamination
- arXiv:2601.05504 — Memory Poisoning Attack and Defense
- BEAM Benchmark (ICLR 2026) — 唯一生产规模记忆基准
