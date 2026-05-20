---
title: "mattpocock/skills — AI 编码技能集工作手册"
author: "Matt Pocock"
source: "GitHub"
date: 2026-05-17
url: "https://github.com/mattpocock/skills"
tags:
  - ai-agents
  - coding-skills
  - prompt-engineering
  - tdd
  - architecture
  - debugging
  - workflow
category: "ai-agents"
description: "Matt Pocock Skills 项目的详尽分析和工作手册。涵盖 14 个核心技能的分组讲解与实战流程，从项目初始化到日常编码的最佳实践。目标：让 AI 编码 Agent 更像真正的工程师，而不是 vibe coder。"
---

# Matt Pocock Skills — 让 AI Agent 做真正的工程

## 项目概述

[mattpocock/skills](https://github.com/mattpocock/skills) 是 TypeScript 大师 Matt Pocock（[Total TypeScript](https://www.totaltypescript.com/) 作者）开源的 **AI Agent 技能集合**。这些技能是他每天使用的、用于 Clance Code / Codex / Cursor 等编码 Agent 的指令集。

### 核心理念

> **"Real engineering, not vibe coding."**

Matt 认为当前的 AI 编码工具存在几个**常见失败模式**（Common Failure Modes）：

1. **对不齐**（Misalignment）— 你说 A，Agent 理解成 B，结果大相径庭
2. **语言模糊**（Fuzzy Language）— Agent 不知道领域术语，用 20 个词说 1 个词的事
3. **反馈缺失**（No Feedback Loops）— Agent 写完代码但不验证，在真空中飞行
4. **架构崩溃**（Accelerated Entropy）— Agent 加速编码的同时也加速了软件熵，代码越来越烂

这套技能的解决方案：**小而可组合的技能**，而不是 GSD / BMAD / Spec-Kit 那种大而全的框架。它们与模型无关，基于几十年的软件工程经验（《The Pragmatic Programmer》、《Domain-Driven Design》、《Extreme Programming》、《A Philosophy of Software Design》）。

---

## 高价值点分析

### 价值 1：Grill Session（对标校准）
**核心技能：** `/grill-me` / `/grill-with-docs`

> "没有人确切知道自己想要什么。" — 《The Pragmatic Programmer》

在写任何代码之前，Agent 应该**追问**你，而不是直接开干。这个技能把"需求磋商"变成了系统化的追问流程：

- 逐条设计决策树
- 每个问题给出**推荐答案**
- 能把模糊术语精确定义
- 同时更新领域词典（CONTEXT.md）和架构决策记录（ADRs）

**效果：** 消除沟通差距，让 Agent 真正理解你要什么。

### 价值 2：共享语言（Shared Language）
**核心技能：** `/grill-with-docs` → 产出 `CONTEXT.md`

> "通用的语言让开发者之间的对话和代码表达都源自同一个领域模型。" — Eric Evans, DDD

大多数项目让 Agent 边干活边摸索行话，结果就是代码里 20 个词表达 1 个概念。CONTEXT.md 是项目的**领域词典**，Agent 每次都能用它解码术语：

```
BEFORE: "当课程中某节课在文件系统中有了实际位置时..."
AFTER:  "当物化级联（materialization cascade）触发时..."
```

简洁带来的是**每次会话都节省大量 tokens**，而且变量、函数、文件命名都保持一致。

### 价值 3：垂直切片 TDD（红-绿-重构）
**核心技能：** `/tdd`

> "反馈的速度就是你的速度限制。" — 《The Pragmatic Programmer》

关键洞察：不要一次性写所有测试（水平切片），那是灾难。应该**一个测试 → 一段代码 → 重复**（垂直切片）：

```
错误方式（水平）：
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

正确方式（垂直）：
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  ...
```

测试只测**公开接口的行为**，不测实现细节。这样重构不会炸测试。

### 价值 4：诊断即技术手段
**核心技能：** `/diagnose`

六阶段系统性诊断流程：

1. **建立反馈环** — 这是技能本身。快速、确定性的 pass/fail 信号 > 一切
2. **复现** — 确认复现的是用户描述的问题
3. **提出 3-5 个可证伪假设** — 列出并排序，先给用户看
4. **仪器化** — 每次只改一个变量
5. **修复 + 回归测试** — 先给正确的 seam 写失败测试
6. **清理 + 事后总结** — 问"什么能防止这个 bug？"

没有反馈环，一切假设都是玄学（vibe）。这个技能把调试从艺术变成了工程。

### 价值 5：架构即日常维护
**核心技能：** `/improve-codebase-architecture`

> "投资于系统设计，每天都要做。" — Kent Beck, XP

AI 加速了软件熵，代码越来越烂。这个技能用一套精确的架构语言（Module / Interface / Depth / Seam / Adapter / Leverage / Locality）来分析代码库的"变深机会"（deepening opportunities）。

**删除测试（Deletion Test）：** 想象删除这个模块。如果复杂度消失了——它是透传；如果复杂度分散到 N 个调用者那里——它在发挥作用。

**推荐频次：** 每隔几天跑一次。

### 价值 6：完整工程闭环
从需求到代码到诊断，技能之间**可组合**，形成完整闭环：

```
需求讨论 → Grill Session → 共享语言
    ↓
PRD 生成 → 分解为 Issue
    ↓
TDD 实现 → 代码改进
    ↓
发布上线
    ↓
Bug 出现 → Diagnose 诊断 → 修复
    ↑                      ↓
    回归测试 ← 架构改进 ← 事后总结
```

---

## 技能全景一览

| 技能 | 分类 | 一句话概括 |
|------|------|-----------|
| `/grill-me` | 生产力 | 追问设计决策树直到完全对齐 |
| `/grill-with-docs` | 工程 | 追问 + 建立共享语言 + 记录 ADR |
| `/tdd` | 工程 | 垂直切片红-绿-重构循环 |
| `/diagnose` | 工程 | 六阶段系统化 bug 诊断 |
| `/improve-codebase-architecture` | 工程 | 发现并实施架构"变深"机会 |
| `/to-prd` | 工程 | 将对话内容合成 PRD 并提交 |
| `/to-issues` | 工程 | 将 PRD/计划分解为可独立执行的 Issue |
| `/triage` | 工程 | 状态机驱动的 Issue 分类 |
| `/setup-matt-pocock-skills` | 工程 | 一次性脚手架 —— 配上 Issue tracker / 标签 / 领域文档 |
| `/prototype` | 工程 | 抛光的可抛弃原型（逻辑 or UI） |
| `/zoom-out` | 工程 | 让 Agent 从更高层视角解释代码 |
| `/caveman` | 生产力 | 原始人模式 —— 去掉填充词节省 75% tokens |
| `/handoff` | 生产力 | 将当前会话紧凑打包以便另一 Agent 接手 |
| `/write-a-skill` | 生产力 | 创建新技能的标准流程 |

---

## 循序渐进工作手册

### 第一阶段：初始设置（一次性）

#### 步骤 1：安装技能
```bash
npx skills@latest add mattpocock/skills
```
选择你需要的技能，确保选中 `/setup-matt-pocock-skills`。

#### 步骤 2：运行初始化
在 Agent 中执行：
```
/setup-matt-pocock-skills
```
它会逐个问：

**问题 A — Issue Tracker**
- GitHub（默认）→ 用 `gh` CLI
- GitLab → 用 `glab` CLI
- 本地 Markdown → `.scratch/<feature>/` 下
- 其他（Jira/Linear）→ 描述工作流

**问题 B — 分类标签**
五个状态角色：
- `needs-triage` — 需要评估
- `needs-info` — 等待提问者补充
- `ready-for-agent` — 规格完整，Agent 可直接接活
- `ready-for-human` — 需要人类实现
- `wontfix` — 不处理

你可以映射到自己仓库现有的标签。

**问题 C — 领域文档布局**
- 单上下文（single-context）→ 根目录 `CONTEXT.md` + `docs/adr/`
- 多上下文（multi-context）→ `CONTEXT-MAP.md` 指向各处

#### 步骤 3：初始产出物
```
repo-root/
├── CONTEXT.md              # 领域词典（后续持续更新）
├── docs/
│   ├── adr/                # 架构决策记录
│   └── agents/
│       ├── issue-tracker.md
│       ├── triage-labels.md
│       └── domain.md
├── CLAUDE.md / AGENTS.md   # 追加了 ## Agent skills 块
```

---

### 第二阶段：需求与设计（每次功能开发）

这个阶段的目标是**对齐**——确保你和 Agent 理解同一个东西。

#### 步骤 4：Grill Session —— 对齐需求
当你要开发一个新功能时，先用：
```
/grill-with-docs
```
Agent 会：
- 逐个问题追问，每个问题给出推荐答案
- 探索代码库验证假设
- 检测术语冲突（"你的词典里 'cancellation' 定义为 X，但你现在似乎说的是 Y"）
- 用具体场景压力测试概念边界
- **即时更新** CONTEXT.md —— 不攒批

**此阶段结束时的产出：**
- CONTEXT.md 更新（如果新增了术语）
- 如果有刚性决策，创建 ADR

#### 步骤 5：Deep Module 规划
在 Grill Session 中，Agent 会主动寻找"变深机会"：
- 哪些模块可以把复杂逻辑封装到简单接口后面？
- 哪些接口设计得不够好？

**原则：** 先设计接口，再写实现。好的接口让测试变简单，让 Agent 变高效。

#### 步骤 6：PRD 生成
完成 Grill Session 后：
```
/to-prd
```
Agent 会直接合成对话内容为 PRD（不会再追问）。PRD 模板包含：
- Problem Statement
- Solution
- User Stories（逐条编号）
- Implementation Decisions（模块接口、架构决策，不含代码路径）
- Testing Decisions
- Out of Scope

PRD 会自动发布到 Issue Tracker，打上 `ready-for-agent` 标签。

#### 步骤 7：拆分为 Issue
```
/to-issues
```
Agent 会将 PRD 拆解为**垂直切片**（vertical slices）：

每条 Issue ：
- 切穿所有集成层（schema → API → UI → tests）
- 完成即可 demo / 验证
- 标注类型：HITL（需人类参与） vs AFK（Agent 独立完成）
- 标注依赖关系

> **HITL vs AFK：** 尽量多做 AFK 切片。HITL 只留给架构决策、设计评审等必须人类的步骤。

**此阶段结束时的产出：**
- 一系列按依赖顺序排列的 Issue
- 每条 Issue 都 ready-for-agent

---

### 第三阶段：实现（日常编码）

#### 步骤 8：TDD 实现
```
/tdd
```
最关键的流程：

**① 规划**
- [ ] 确认接口变更
- [ ] 确认测试优先级
- [ ] 识别深模块机会
- [ ] 列出要测试的行为
- [ ] 获得用户批准

**② 追踪子弹（Tracer Bullet）**
```
RED:   写第一个测试 → 失败
GREEN: 写最少代码 → 通过
```

**③ 递增循环**
```
RED:   写下一个测试 → 失败
GREEN: 写最少代码 → 通过
```
规则：
- 一次只测一个行为
- 只有能通过当前测试的最少代码
- 不预判未来测试
- 只测可观察行为，不测实现细节

**④ 重构**
- [ ] 消除重复
- [ ] 加深模块（把复杂度推给实现、简化接口）
- [ ] 自然应用 SOLID
- [ ] 每次重构后跑测试

> ⚠️ **绝不在 RED 时重构。** 先到 GREEN。

**每个循环的检查清单：**
```
[ ] 测试描述行为而非实现
[ ] 测试只使用公开接口
[ ] 测试能在内部重构后存活
[ ] 代码对此测试最小
[ ] 没有添加预测性功能
```

#### 步骤 9：原型验证（可选）
如果你对某个设计不确定，不要直接写生产代码：
```
/prototype
```
Agent 会判断你需要的是：
- **逻辑原型（LOGIC.md）：** 交互式终端应用，反复演练状态机 / 业务逻辑
- **UI 原型（UI.md）：** 多个截然不同的 UI 变体，通过 URL 参数切换

原型规则：
- 从第一天就视为可抛弃
- 一键运行
- 无持久化（state in memory）
- 无测试、无错误处理、无抽象
- 结束后删除或吸收到真实代码

---

### 第四阶段：Triage（日常维护）

#### 步骤 10：Issue 分类
当有新的 bug report 或 feature request：
```
/triage
```

Agent 会：
1. 获取全量 Issue 清单，按未分类 → needs-triage → needs-info 展示
2. 对你选中的 Issue，读全文、探索代码库、查之前拒绝记录（`.out-of-scope/`）
3. **Bug 优先：** 尝试复现，读代码跑测试
4. **推荐：** 给出 category（bug/enhancement）+ state 推荐
5. **Grill（如需）：** 对不明确的 Issue 自动跑 `/grill-with-docs`
6. **执行：**
   - `ready-for-agent` → 写 Agent Brief，打标签
   - `needs-info` → 写具体可回答的问题
   - `wontfix` → 礼貌解释并关闭（enhancement 写进 `.out-of-scope/`）

每条 AI 输出的评论必须以以下声明开头：
```
> *This was generated by AI during triage.*
```

**Agent Brief（ready-for-agent 时）** 要包含足够的信息，让另一个 Agent 直接接活，不需要问任何人。

---

### 第五阶段：调试（Bug 出现时）

#### 步骤 11：Diagnose —— 六阶段诊断
```
/diagnose
```

**Phase 1 — 建立反馈环 ⭐（最重要！）**
尝试顺序：
1. 失败测试 → 2. Curl/HTTP 脚本 → 3. CLI 调用比对输出 → 4. 无头浏览器脚本 → 5. 回放流量 → 6. 一次性 harness → 7. Fuzz 循环 → 8. Git Bisect harness → 9. 差异对比 → 10. HITL bash 脚本

> **"Build the right feedback loop, and the bug is 90% fixed."**
> 
> 没有反馈环，不要进入 Phase 2。列出你尝试了什么、为什么做不到、问用户要权限/数据。

**Phase 2 — 复现**
确认复现的是用户描述的故障模式（而非附近恰好出现的另一个问题）。

**Phase 3 — 提出假设**
产出 3-5 个假说，排序，**每个都必须可证伪**。
> 格式："如果 <X> 是原因，那么 <改 Y> 会让 bug 消失 / <改 Z> 会让它更严重。"

**先给用户看排序！**

**Phase 4 — 仪器化**
每次只改一个变量。每个调试日志加唯一前缀 `[DEBUG-a4f2]`。

**Phase 5 — 修复 + 回归测试**
如果存在正确的 test seam → 先写失败测试 → 确认它失败 → 修复 → 确认它通过 → 跑原始反馈环确认。

**Phase 6 — 清理 + 事后总结**
- [ ] 原始故障不再出现
- [ ] 回归测试通过
- [ ] 所有 `[DEBUG-*]` 日志已移除
- [ ] 一次性原型已删除
- [ ] 正确的假说写入了 commit / PR message

然后问：**"什么能防止这个 Bug 发生？"** 如果答案涉及架构问题（没有好的 test seam、耦合等），交给 `/improve-codebase-architecture`。

---

### 第六阶段：架构优化（定期重构）

#### 步骤 12：改进代码架构
```
/improve-codebase-architecture
```
建议频率：**每隔几天跑一次**。

**① 探索**
遍历代码库，关注摩擦点：
- 理解一个概念需要跳多少个小模块？
- 哪些模块是**浅的**（接口复杂度 ≈ 实现复杂度）？
- 哪些纯函数被提取仅为了测试，但真实 bug 隐藏在它们的调用方式中？
- 哪些紧密耦合的模块在跨越 seam 泄露？
- 哪些部分没测试，或难以通过当前接口测试？

**② 列出候选**
每个候选包含：
- 涉及的文件
- 问题描述
- 解决方案简述
- 收益（以 Locality + Leverage 角度描述，以及测试会怎么改进）

**使用 CONTEXT.md 术语描述领域，LANGUAGE.md 术语描述架构。**

**③ Grill 循环**
选中一个候选后，进入设计对话。决策结晶时**同步更新**：
- 新增概念？→ 更新 CONTEXT.md
- 模糊术语？→ 更新 CONTEXT.md
- 用户因有分量的理由拒绝了？→ 创建 ADR（"需要记录以便后来人不重复提议"）
- 需要探索备选接口？→ 查看 INTERFACE-DESIGN.md

---

### 第七阶段：工具与效率

#### 步骤 13：手递手（Handoff）
```
/handoff 下一个会话要做什么
```
Agent 会将会话压缩成 handoff 文档，另一个 Agent 接手。文档：
- 不重复已有产出物（PRD / ADR / Issues）
- 引用已有产出物的路径
- 建议下一个会话使用的技能

#### 步骤 14：原始人模式（Caveman Mode）
```
/caveman
```
极端压缩模式 —— 去掉冠词、填充词、客套话、模糊表达，节省约 75% tokens：

```
正常: "Sure! I'd be happy to help you with that. The issue you're experiencing is likely caused by..."
Caveman: "Bug in auth middleware. Token expiry check use `<` not `<=`."
```

一旦触发，每次响应都保持。用户说 `stop caveman` 或 `normal mode` 才恢复。

**自动清晰例外：** 安全警告、不可逆操作确认、多步骤流程容易读错时，临时退出 caveman。

#### 步骤 15：Zoom Out
```
/zoom-out
```
当你不熟悉某块代码时：
```
"我不太清楚这个区域。向上抽象一层，给我一个相关模块和调用者的地图，用项目领域词典的术语。"
```

#### 步骤 16：写自己的技能
```
/write-a-skill
```
当你想把某个工作流固化下来，让 Agent 帮你创建新的 SKILL.md：
1. 问需求 → 2. 起草 → 3. 审查
技能结构：
```
skill-name/
├── SKILL.md           # 主要指令
├── REFERENCE.md       # 详细文档
├── EXAMPLES.md        # 使用示例
└── scripts/
    └── helper.js
```

---

## 完整工作流总览图

```
                        初始化
                          │
                      /setup
                          │
              ┌───────────┼───────────┐
              │           │           │
              ▼           ▼           ▼
         新功能开发     Issue 分类    Bug 修复
              │           │           │
         /grill-with    /triage     /diagnose
         -docs             │           │
              │           ▼           ▼
              ├──→ CONTEXT.md    修复 + 改进
              ├──→ ADRs
              │                 事后总结
              ▼                    │
           /to-prd             ┌────┘
              │                │
           /to-issues    /improve-arch
              │
              ▼
           /tdd (循环)
              │
           /prototype (可选)
              │
              ▼
          上线
              │
         ┌────┘
         ▼
     /handoff (若需交接)
```

---

## 关键原则总结

| 原则 | 出处 | 含义 |
|------|------|------|
| 反馈的速度就是你的速度极限 | 《Pragmatic Programmer》 | 快速反馈环 > 一切 |
| 专注于系统设计，每天都做 | Kent Beck, XP | 架构不是事后才做的事 |
| 深模块（Deep Module） | John Ousterhout | 小接口 + 大实现 = 好的设计 |
| 通用语言（Ubiquitous Language） | Eric Evans, DDD | 人和 Agent 用同一个词典 |
| 删除测试（Deletion Test） | Matt Pocock | 删掉它，看复杂度去哪了 |
| 可证伪假设 | 科学方法 | "如果 X 是原因，那么 Y" |
| 垂直切片（Vertical Slice） | TDD 实战 | 一次一个端到端路径 |
| 追踪子弹（Tracer Bullet） | 《Pragmatic Programmer》 | 第一条路径验证了整个系统 |
| 可组合 > 大而全 | Matt Pocock | 小技能拼出大能力 |

---

## 安装命令

```bash
# 安装所有技能
npx skills@latest add mattpocock/skills

# 配置
# 在 Agent 中运行 /setup-matt-pocock-skills
```

## 相关资源

- [GitHub 仓库](https://github.com/mattpocock/skills)
- [Matt Pocock 的 AI Hero 新闻通讯](https://www.aihero.dev/s/skills-newsletter)（~60K 订阅者）
- [Matt Pocock 的 Total TypeScript 课程](https://www.totaltypescript.com/)
- [skills.sh — 技能分享平台](https://skills.sh/mattpocock/skills)
