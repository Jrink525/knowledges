---
title: "QQ音乐 Harness Engineering 实践：从 Vibe Coding 到工程化 AI 协作"
tags:
  - harness-engineering
  - agent-engineering
  - enterprise
  - monorepo
  - context-engineering
  - ai-governance
  - qqmusic
  - tencent
  - best-practices
date: 2026-05-21
source: "https://mp.weixin.qq.com/s/yw3DvqKBIV5fIZkSG12zdA"
authors: "黄欣欣（腾讯云开发者）"
---

# QQ音乐 Harness Engineering 实践：从 Vibe Coding 到工程化 AI 协作

> **来源：** [腾讯云开发者公众号]
> **作者：** 黄欣欣
> **场景：** QQ音乐音乐商业化团队，50+ 微服务，单仓多服务 + 多仓协同

![QQ音乐 Harness Engineering 封面](../image/qqmusic-harness-engineering-1.jpg)
*(封面图：腾讯云开发者公众号)*

![Harness Engineering 架构图](../image/qqmusic-harness-engineering-3.jpeg)
*(架构图：Harness 四大组件与 L5 治理层)*

---

## 核心矛盾：生成快、验证慢、错误累积

AI 能显著提升编码效率，但有一个容易被忽略的配套事实：**生成速度在提升，验证能力却没有同步提升。** 代码出得越快，错误积累得也越快；AI 自主性越强，偏离正确轨道时的修正成本就越高。

这就是 AI 时代软件工程的核心矛盾。

解决的思路不是更长更复杂的 prompt，而是 **工程化**。Harness Engineering 的核心理念是：AI 参与分析、设计、编码、审查和验证，但最终判断权始终留在工程师手中。**Engineering 的本质是约束下的优化**——在质量、安全、可维护性等约束下寻找最优可行解。

---

## 核心公式：代码产出 = AI 能力 × 上下文质量

这个乘号至关重要。当上下文质量趋近于零时，模型再强，产出也是零。

在真实业务仓里，AI 拿不到的上下文缺口主要有五类：

| 缺口类型 | 典型问题 | AI 的"盲区" | Harness 的解 |
|---------|---------|------------|-------------|
| **隐性规范** | 锁机制、埋点规则、错误码空间 | 不知道这些规范存在 | `context/team/` |
| **历史决策** | 为什么选了 A 方案没选 B | 训练语料里没有 | `context/project/{module}/experience/` |
| **服务契约** | IDL 字段冻结状态、下游依赖 | 不理解哪些字段动不得 | `.service-matrix/dependencies.yaml` |
| **跨服务依赖** | 同一个需求要改哪几个服务 | 缺乏全局视角 | 服务矩阵自动解析 |
| **演进轨迹** | 模块上次大改的坑、灰度策略 | 没有跨会话记忆 | Self-Refinement 闭环 |

提升上下文质量，是比提升模型能力更高效的杠杆。**模型能力的提升依赖外部厂商，上下文质量的提升完全掌握在团队自己手中。**

---

## 什么是 Harness Engineering

> "Harness"本义是马具/挽具——把一匹原始力量巨大但方向不定的马，通过缰绳、鞍具、辔头接入可控系统。这个隐喻恰好概括了 LLM 应用的本质矛盾。

### 四大标准组件

| 组件 | 能力 |
|------|------|
| **① 运行时控制系统** | 工具编排、状态持久化、错误恢复、反馈循环 |
| **② 上下文工程** | Context Window 优化、动态检索/摘要、防 Context Rot、信息优先级 |
| **③ 工具集成与防护** | API 调用标准化、预执行校验、阻止幻觉执行、安全护栏 |
| **④ 生命周期管理** | 多步长任务、Checkpoint/Crash Recovery、Human-in-the-Loop、跨会话状态 |

### QQ音乐的独特挑战：缺少 Multi-Agent × Multi-Service 治理层

业界共识止步于四大组件，但 QQ 音乐面对的是：**50+ 微服务 + 单仓多服务 + 多仓协同**。一个需求从开始到上线要经历多个 Agent、多个工具、多个服务、多个仓库的协同，这一层业界留白了。

因此他们补齐了 **L5 工程治理层**：

```
L5  Harness Engineering：团队拥有的工程治理层
    - 五阶段流程 + 四道门禁
    - 三层知识体系
    - 服务矩阵
    - Self-Refinement
    - 多运行时适配
L3/L4 执行层：Claude Code / Gemini CLI / Codex CLI / Continue / CodeBuddy
L1/L2 体验层：IDE、补全、对话、diff 可视化
```

**核心原则：不替代执行工具，只定义执行工具必须遵守的工程上下文和协作协议。**

---

## 业务约束的四类工程化

| 约束类型 | 具体问题 | 技术落点 |
|---------|---------|---------|
| **流程约束** | 需求→设计→开发→交付容易跳步 | 五阶段主流程 + 四道门禁 + `main-process-numbering.md` |
| **拓扑约束** | AI 不知道服务之间真实依赖 | `.service-matrix/dependencies.yaml` + 影响面分析 |
| **契约约束** | IDL 字段兼容性和分支一致性 | 三仓联动 + `idl_required` + 服务仓库检查门禁 |
| **知识约束** | 团队规范和历史经验不在上下文里 | `context/team/`、`context/harness-framework/`、`context/project/` 三层知识 |
| **演进约束** | AI 错误修完就丢，下次继续犯 | Self-Refinement + `experience/*.md` 版本化沉淀 |

---

## 五阶段 + 四道门禁：让错误死在最便宜的地方

```
阶段 1 初始化 → 阶段 2 需求定义⭐ → 阶段 3 设计⭐ → 阶段 4 开发⭐⭐ → 阶段 5 交付
                    ↑需求评审       ↑设计评审       ↑Dev进入 + 服务仓库检查
```

⭐ = 强制门禁，共 4 道，不可跳过。

| 门禁 | 位置 | 阻塞条件 | 改动代价 |
|------|------|---------|---------|
| 需求评审 | 阶段 2.2 | 需求文档不合格 | 改几行文档 |
| 设计评审 | 阶段 3.3 | 方案漏了关键约束 | 改设计文档 |
| Dev 进入 | 阶段 4.2 | `tasks/features.json` 缺失 | 改任务拆分 |
| 服务仓库检查 | 阶段 4.3 | 三仓分支不一致 | 重切分支 |

**核心理念：错误越早被拦住，代价越低。** 门禁尽量少、尽量靠前。过了编码循环再回退，代价就从"改几行文档"升到"回滚代码 + IDL + 数据迁移"。

门禁是机读的，不是口头的。每个门禁都有对应的 Agent / Skill 和 markdown 检查规范，结论写入文件固定格式，确保可审计。

---

## 三层知识体系

```
团队级 (最稳定)          context/team/          Git规范、错误码空间、日志规范
框架工程级 (中频更新)    context/harness-framework/  五阶段流程、门禁规则、模板
服务级 (高频演进)        context/project/{项目}/{模块}/{服务}/  架构图、API、踩坑经验
```

每层都有 `INDEX.md` 作为入口，AI 按"团队→项目→模块→服务"逐层缩小范围，O(1) 命中。

### `.service-matrix/dependencies.yaml` — 服务拓扑单一真相源

```yaml
workspace: ".."
business_repo: "music_commercial_go_proj"
idl_repo: "qqmusicjce"
default_team: "music-commercial"

services:
  vipapi:
    module: vip
    repo_path: "{business-repo}/vipapi"
    idl_required: true
  assetcardmallcgi:
    module: assetcard
    repo_path: "{business-repo}/assetcard/mall/assetcardmallcgi"
```

**设计要点：**
- 路径从不硬编码，用 `{business-repo}` / `{idl-repo}` 占位符，跨机器无缝迁移
- 多团队共用同一 Harness 仓
- `$HARNESS_TEAM` > `.harness/local.yaml` > `default_team` 三级解析
- 当前仓实际管理 **57 个服务**

### 三仓联动

每个需求，在三个仓里用**完全相同的分支名**：

```
Harness 仓 (脑)   业务代码仓 (手脚)    IDL 契约仓 (神经)
   ├─ 规范/知识       ├─ 代码/测试        ├─ .jce 契约
   └─ feature/...     └─ feature/...      └─ feature/...
   /T12345 ✓          /T12345 ✓           /T12345 ✓
```

一条 TAPD 单 ID → 三仓分支名一对一，追溯链整洁。阶段 4.3 门禁自动校验三仓分支一致性，不一致直接阻塞。

---

## Skill / Agent / Command 三件套

所有能力都是版本化 markdown 文件，任何一次修改都能 code review、diff、rollback——**Knowledge as Code** 的物理实现。

### Skill（34 个）：可复用的工作流

| 类别 | 代表 Skill |
|------|-----------|
| 需求生命周期 | `managing-requirement-lifecycle`、`feature-lifecycle-manager` |
| 文档撰写 | `requirement-doc-writer`、`outline-design-doc-writer` |
| 代码审查 | `code-review-report`、`traceability-gate-checker` |
| 服务治理 | `service-dependency-analyzer`、`load-service` |
| 知识沉淀 | `managing-knowledge`、`self-refinement` |

### Agent（24 个）：自主子任务执行者

按阶段组织：Init → RequirementManagement → Startup(1) → Definition(2) → TechResearch(3.1) → OutlineDesign(3.2) → DetailDesign(3.2) → Implementation(4.4) → Acceptance(5) → KnowledgeMaintenance

**亮点：阶段 4.4 的代码审查被拆成 8 个维度的独立 Agent 并行执行：**

```
code-review-preparer → 并行分发
 ├─ design-checker (设计一致性)
 ├─ complexity-checker (复杂度)
 ├─ concurrency-checker (并发安全)
 ├─ error-checker (错误处理)
 ├─ security-checker (安全漏洞)
 ├─ api-contract-consistency-validator (契约一致)
 ├─ traceability-consistency-checker (追溯链)
 └─ auxiliary-checker (辅助检查)
→ code-review-report Skill 聚合为 reviews/*.md
```

### Slash Command（35 个）：标准化入口

```
/requirement:new /:continue /:next /:gate-check   需求生命周期
/agentic:code-review /:load-service /:note          AI 操作
/service:deps /:onboard /:load-domain               服务治理
/knowledge:extract-experience /:generate-sop         知识沉淀
```

同一命令对应同一流程，无论用 Claude Code、Gemini CLI、Codex CLI 还是 Continue，体验一致。

---

## Self-Refinement：让 AI 从错误中沉淀经验

LLM 没有跨会话记忆。但团队的每一个"纠正"，都是一次宝贵的信号。

**闭环流程：**

```
① 用户纠正 AI → ② AI 识别是"模式性教训"还是"一次性 diff"
  → ③ 模式性教训 → 提出沉淀层级（团队级/框架级/服务级）
  → ④ 用户确认 → 生成 experience 文档 / 更新 Skill
  → ⑤ 下次同类场景，新会话/新模型/新人自动受益
```

**具体产物示例：**
- `context/project/{module}/experience/*.md` — 踩坑经验（分页必须有上限、goroutine 泄漏、🔒字段约束）
- `context/project/{module}/sop/*.md` — 从经验提炼的标准操作规程
- **框架自身的演进也是 Self-Refinement 的活样本**：占位符词典从模糊到精确，路径错误被后续 MR 修正——每一次修正都在沉淀经验。

---

## 与 Claude Code / Cursor / Cline 的关系

**Harness Engineering 不是这些工具的替代品，而是它们上层的治理层协议。**

```
执行层：Claude Code / Cursor / Cline / Gemini CLI / Codex CLI / Continue
  ↑            提供 AI 能力、代码理解、文件编辑、命令执行、测试修复
  │
治理层：Harness Engineering
  ↑            定义流程、门禁、知识体系、服务矩阵、三仓联动、经验沉淀
```

**三句话概括：**
- **执行交给工具**：读代码、改代码、跑测试，交给更强的 AI IDE / CLI
- **规则留在仓库**：流程、门禁、服务拓扑、团队知识为可 review 的工程资产
- **协议连接两者**：Skill / Agent / Command 把团队规范翻译成执行层可消费的上下文

**多运行时适配：** Harness 仓的 `.codebuddy/skills/` / `agents/` / `commands/` 是真相源，`scripts/install.sh` 把它们渲染到各 CLI 的本地目录：

```
.claude/    ← Claude Code
.gemini/    ← Gemini CLI
.codex/     ← Codex CLI
.continue/  ← Continue
```

修改规范只改 `.codebuddy/`，不同 CLI 自动受益。今天用 Claude Code，明天换新工具，流程和知识都不丢。

---

## 关键洞察

### Why Self-Research（为什么必须自研）

通用产品无法替团队定义：
1. **服务矩阵语义** — 谁依赖谁、路径如何解析
2. **需求生命周期语义** — 阶段、门禁、产物、追溯关系
3. **IDL 契约语义** — 哪些字段冻结、哪些变更需同步业务仓
4. **团队经验语义** — 某个服务过去因分页无上限打爆下游
5. **工具解耦语义** — 不被任何运行时锁定

### 工程制品的构成

| 制品 | 作用 |
|------|------|
| `AGENTS.md` | 全局协作规范和硬规则入口 |
| `.codebuddy/skills/` | 可复用能力单元 |
| `.codebuddy/agents/` | 专家角色定义 |
| `.codebuddy/commands/` | 标准化入口命令 |
| `context/team/` | 团队级规范 |
| `context/harness-framework/` | 框架工程规范 |
| `context/project/` | 服务级知识 |
| `.service-matrix/dependencies.yaml` | 服务拓扑与仓库路径 |
| `requirements/` | 需求生命周期产物 |

全部在仓库里 → 可 code review、可 diff、可回滚、可持续演进。对 AI 是上下文，对团队是资产，对工程管理是审计线索。

### 一句话总结

> **Context Engineering + Spec-First + Knowledge as Code，构成了可验证、可演进的 AI 协作工程基线。把你的团队当作镜子照一照：流程是否完整、门禁是否可机读、知识是否已沉淀、跨服务协调是否已显式化。**

---

## 关联文章

- [Agent Harness Engineering — AI Agent 的脚手架才是真正的工程](../agent-harness-engineering.md) — Addy Osmani（Harness 通用理论）
- [Agentic Harness Engineering (AHE)](../agentic-harness-engineering-ahe.md) — AlphaSignal（自动演化 Coding Agent 组件）
- [瘦 Harness，胖技能](../agent-engineering/thin-harness-fat-skills-garry-tan.md) — Garry Tan（Harness 架构哲学）

---

*整理于 2026-05-21，来源：腾讯云开发者公众号*
