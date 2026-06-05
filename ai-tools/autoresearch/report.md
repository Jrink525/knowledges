# The Log is the Agent: Event-Sourced Reactive Graphs for Auditable, Forkable Agentic Systems

> **论文**: arXiv:2605.21997 | **作者**: Yohei Nakajima (Untapped Capital / BabyAGI)  
> **代码**: https://github.com/yoheinakajima/activegraph · **安装**: `pip install activegraph`  
> **许可**: Apache-2.0

---

## 一句话核心

**把 Agent 的 append-only event log 作为一等公民——Log 不是副产品，Log 就是 Agent 本身。** 工作图（graph）是 log 的确定性投影（projection），行为（behavior）是 graph 变化时的反应函数。

---

## 三遍法阅读

### 第一遍：五 C 概览

| C 维度 | 内容 |
|--------|------|
| **Category** | Agent 系统架构论文（非经验性评估，是系统/架构贡献） |
| **Context** | 现有 Agent 框架围绕模型构建（chat loop → tools → rules → logging → memory），log 是副产品。记忆系统（MemGPT, Zep, Mem0, Hindsight）试图在模型外挂记忆层，但 provenance 始终不完整，且无法确定性重放（replay） |
| **Correctness** | 推理严密——从设计动机（log 是什么、问题在哪）到架构（event, graph, behavior）到 replay 机制到 fork 机制，层层递进。每个设计的 rationale 都明确 |
| **Contributions** | 4 个：① event-sourced agent model；② determinism contract + replay mechanism；③ forking + structural-diff；④ 完整可复现的工作示例（diligence pack） |
| **Clarity** | 清晰务实，不浮夸。明确声明"不 claim 提升准确率"、"没有评估 self-improving 能力"——这在 ML 论文中极其罕见，值得注意 |

### 第二遍：论证链重建

**问题**：现有 Agent 框架中，log 是副产品。所有状态分散在不同的地方（prompt、代码、框架内部状态、数据库、记忆系统），provenance 不完整，无法重放，无法分叉。

**假设前提**：如果 log 不是副产品而是 Agent 本身，那 replay、fork、lineage 会自然成立。

**模块**：
1. **Event** — append-only 有序序列，每个 event 有 id、type、payload、actor、`caused_by` 指针
2. **Graph** — 从 log 通过 replay 确定性折叠（fold）得到，typed objects + relations
3. **Behavior** — 订阅 graph shape 模式的反应函数（4 种形式：函数、类、LLM-backed routines、relation-behavior）
4. **Replay 机制** — 内容寻址缓存在 log 中，replay 时 model/tool response 直接从 cache 读取，不需要重新调用
5. **Fork** — 在任意 event 处 fork，前面共享前缀使用 cache 不重算

**公式**：
```
log [event1, event2, ...] → replay → graph (objects + relations)
graph change → match subscriptions → behavior fires → emit new events → append to log
```

**关键实验/证明手段**：
- Diligence pack：671 events, 93 objects, 76 relations, 103 model calls, 48 tool calls，完全可复现（`activegraph quickstart`）
- Deterministic replay：两次运行产生 byte-identical logs
- Fork 示例：在 event 150 处 fork，前 149 步从 cache 读取，不产生新 model calls

### 第三遍：虚拟重实现

**关键假设**：
1. Behavior 主体必须是其输入的确定性函数（不能读 `random`、wall-clock、UUID）
2. LLM 调用通过 cache 在 replay 时变得确定——前提是 prompt hash 匹配
3. 图谱投影必须完全确定——即同一 log 重复 replay 得到完全相同的图
4. 外部工具 side effect 仅通过记录来 replay-safe（首次执行仍然变 externality）

**边界情况**：
1. 百万 event 级别的 log——目前没有 checkpoint/compaction 机制，replay 全量扫描
2. Schema 迁移——event/object type 改变后旧格式 event 的处理需要 migration tooling
3. 分布式多 writer——ordering 未解决（当前只有单 writer append-only）
4. Behavior 违反 determinism contract——只在 replay 时被捕获而非静态检查
5. LLM prompt 变化——fork 时如果改 prompt，新 hash 不匹配，需要重新调用 model

---

## 设计精要

### 核心架构（图 1）

```
Events (append-only log)
  ↓ replay (deterministic fold)
Graph (objects + relations)
  ↓ match subscriptions
Behaviors (fire on graph change)
  ↓ emit events
Events (append-only log) ← 闭环
```

**三个关键设计决策**：

1. **为什么用图而非纯 log？** Event sourcing 只给 log + 值投影；graph 让 behavior 可以订阅图拓扑结构（"一个 claim 地址指向未回答的 question"），让 relation-behavior 成为一等对象，让 structural diff 有明确定义
2. **为什么没 workflow？** 控制流是 emergent 的——planner 响应 goal → 创建 company → question-generator 响应 company → 生成 questions → researcher 响应每个 question。同步演化（implicit coordination），不是编排（explicit orchestration）
3. **为什么 determinism 只在 replay 时保障？** Behavior 第一次可以非确定地调用 LLM，response 记录在 event 中。Replay 时从 cache 读取。这区分了"运行时的非确定性"和"重放时的确定性"

### 对比表（原文 Table 1）

| 属性 | 传统 Agent Loop | Memory-Layer 系统 | ActiveGraph |
|------|----------------|-------------------|-------------|
| 跨会话持久状态 | partial | yes | yes |
| Provenance（为什么这个出现？） | no | partial | **total** |
| 确定性状态重建 | no | no | **yes** |
| 全运行历史 replay | no | no | **exact** |
| 任意点 fork | no | no | **yes** |
| Fork 共享前缀成本 | 重执行 | 重执行 | **cached** |
| 两次运行 structural diff | no | no | **yes** |

### Determinism Contract

- 不能直接读 `random`、`time.time()`、new UUIDs（从 event 获取这些）
- 不能直接做 I/O（通过 framework 的 tool/model 原语）
- 不能依赖跨 fired 次的可变全局状态
- **不静态执行**，violations 在 replay 时检出不匹配 event 来捕获

### Replay 的两种模式

| 模式 | 行为 | 用途 |
|------|------|------|
| **Permissive** | 命中 cache 的从 cache 读；未命中的重新调用写新 event | 从 log 加载 run 的默认方式 |
| **Strict** | 逐 event 比对，第一个不匹配抛出 divergence error | 证明可复现性、policing determinism contract |

### Fork 的 3 个特性

1. **便宜**（cheap）：共享前缀从 cache 读取，不重算 model calls
2. **诚实**（honest）：fork 的 events 1..k 就是 parent 的 events 1..k，event ids 完全相同
3. **可验证**（verifiable）：读两个 log 就能验证共享 lineage

### Fork vs Frame

| | Fork | Frame |
|--|------|-------|
| 持久性 | 独立持久化 | 共享同一 log |
| 合用场景 | 长期分支可独立检查 | 短期并行子上下文最终收敛 |
| 典型 flow | 探索 → 好分支 fork 保留 | Frame 探索后合并回主 log |

---

## 工作示例：Diligence Pack

三个公司（Northwind Robotics, Stellar Logistics, Pinecone Bio）的尽职调查：

| 统计量 | 值 |
|--------|-----|
| Events | 671 |
| Objects | 93（3 companies + 24 questions + 9 docs + 25 claims + 25 evidence + 1 contradiction + 3 risks + 3 memos）|
| Relations | 76 |
| Model calls | 103 |
| Tool calls | 48 |
| 编排代码 | **0 行** |
| 能否离线运行 | ✅ `pip install` + `activegraph quickstart`，30 秒内完成 |

**Lineage 是产品**：每个 claim 携带 provenance——创建它的 behavior、causing event 的 id、产生它的具体 model request event。通过 typed relations 链接到它 address 的 question、derived_from 的 document、supports 的 evidence。从 goal 到 memo 的因果链完全可从 log 重建。

---

## Self-improving Agent 的切入点

论文第 7 节（\S7）是唯一"推测而非评估"的部分。作者明确指出架构为 self-improvement 移除了两个障碍：

1. **可审计性和回滚**：规则/behavior 是 logged state，self-modification 本身是 event。可以 replay 修改前的状态，用 strict replay 暴露修改后的行为偏差
2. **Fork-and-diff 作为 eval primitive**：自然改进循环 = 提出修改 → fork → 在 fork 中应用 → 跑 → structural diff vs parent。共享前缀从 cache 读取，每个候选改进的评估"不重算历史"

---

## 与记忆系统的关系

| 系统 | 立场 | 限制 |
|------|------|------|
| MemGPT/Letta | VM 式 paging | 仍是记忆层；非 primary |
| Zep/Graphiti | 时间知识图谱内部记忆 | 仍是记忆层 partial provenance |
| Mem0 | 生产记忆提取 | projection approach |
| Hindsight | 记忆是一等公民 + 观察/推理分离 + 审计 | 仍是"layer"而非 whole agent substrate |
| **ActiveGraph** | **Log 是 primary，其他都是 projection** | Total provenance, exact replay |

**关键区别**：记忆系统把记忆作为 derived state（summaries + embeddings）附着在 Agent 上；ActiveGraph 把所有状态（包括规则和 tool calls）放在 log 中，记忆只是 log 的片段

---

## Blackboard 架构的复兴

论文明确承认 ActiveGraph 是 blackboard systems（1970-80s）的继承者。两个历史约束被 LLM 溶解了：
1. **知识源**：原先是 brittle 的 rule-based 组件 → 现在是通用的 LLM-backed behavior
2. **控制逻辑**：需手写哪个知识源 → 自然语言 / generated

**论文的论点**：Blackboard 的 shared-state + react-and-write-back 模型可能天然适合 LLM，比 chat loop 更适合。

---

## 限制与成本

1. **Cascade divergence / loop**：behavior emit event → trigger behavior → 可能发散/死循环。当前防御：per-run budget（event 数、behavior 调用数、patches、递归深度、时间、成本）——"钝器而非静态保证"
2. **Replay 成本随 log 线性增长**：百万 event 全量 replay。无 checkpoint/compaction
3. **Schema 演进**：event/object type 变化后旧格式仍存在
4. **外部工具 side effect**：首次执行仍会影响外部世界，仅记录可 replay-safe
5. **分布式 multi-writer**：ordering 未解决
6. **Determinism contract 动态执行**：violation 在 replay 时才被发现
7. **Cache 空间**：model/tool response 占用空间随 run 大小增长
8. **修改 prompt 的 fork**：需要重跑 affected model calls
9. **无任务准确率实验**：纯系统论文，无 benchmark

---

## 方向种子

| 方向 | 类型 | 最小可行实验 |
|------|------|------------|
| D1: Fork-based self-improvement loop | proxy_mismatch | 用一个 behavior prompt 改进场景：fork → 改 prompt → 跑 → diff → 决策是否 merge |
| D2: 分布式/多 writer ordering | evidence_gap | GRACE 类协议扩展到 ActiveGraph events |
| D3: Checkpoint/compaction 策略 | missing_subsystem | 阈值压缩：log 达到 N event 后创建 snapshot（graph + cache 快照），replay 从最后 checkpoint 开始 |
| D4: Static determinism validation | reviewer_objection | 在 Python AST 层面静态检查 behavior body 不调用 `random/time.uuid` |
| D5: Hybrid deterministic-probabilistic replay | assumption_violation | 允许行为声明"这个 LLM 调用在 replay 时可以不严格匹配 cache"→ 概率近似 replay |
| D6: Cascade budget 优化 | evidence_gap | 学习型预算分配——不是全局 cap，是为每个 behavior 基于历史模式分配预算 |

---

## 读后感

这篇论文的意义在于**刷新了 Agent 架构的根本假设**。大多数人看到系统里 log 很多，想到的是"log 太多了，要压缩、总结、embedding"。Nakajima 看到的是"log 不是垃圾，log 就是你需要的全部——而且你之前扔掉的才是关键"。

**架构层面的贡献：**
- 把 event sourcing 这个数据库领域的成熟模式（40 年了）应用到 Agent 系统——这个跨域重组（recombination）才是不容易想到的点子
- Replay cache + fork 的组合非常巧妙：既然 LLM 调用在运行时不可能是确定性的，那就不要求它在运行时确定——只要求在 replay 时确定。这是一个聪明的"scoping"——把问题框定在可解决的范围内

**怀疑点：**
- 百万 event replay 的实际耗时没有定量数据。如果一次 deep research 产生 2000 events，replay 1 秒内能完成吗？
- 实际 Agent 系统的 behavior 往往依赖于 non-deterministic 信号（如 slack webhook 触发时间）。把外部 causation 缩小到 event causation，理论上可行但实际迁移成本很大
- Behavior 之间的 implicit coordination 在复杂场景下 debug 更困难——传统 workflow 虽然笨但可见，emergent 控制流在出现异常时序时很难排查

**为什么重要：** 这不是一个"项目用框架 X 替代 Y"的问题。这是一个应该出现在每一个 Agent 架构师桌上的模式——**Log 优先架构**。不管你的具体实现是不是 ActiveGraph，理解并采纳这个倒置（inversion）可以让你在设计 Agent 系统时得到 replay + fork + lineage 这些原本很难同时获得的特性。

---

*整理时间：2026-06-04 | LaTeX 源阅读 | Report for arXiv:2605.21997*
