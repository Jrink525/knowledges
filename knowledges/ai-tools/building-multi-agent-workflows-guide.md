---
title: "如何构建多 Agent 工作流 — 完整指南"
tags:
  - multi-agent
  - claude-code
  - orchestration
  - agent-patterns
  - workflow
date: 2026-06-01
source: "https://x.com/av1dlive/status/2061386872321130782"
authors: "Avid (@Av1dlive)"
---

# 如何构建多 Agent 工作流 — 完整指南

> **来源：** [How to Build Multi Agent Workflows (Full Guide)](https://x.com/av1dlive/status/2061386872321130782) — Avid (@Av1dlive)
>
> **免责声明：** 本文由作者根据笔记、研究和个人经验编写，经 AI 模型 (Sonnet 4.6) 编辑。封面图来自 Pinterest，经 AI 修改。

![Multi-Agent Workflows Guide Cover](../image/building-multi-agent-workflows-guide-1.jpg)

---

## 概述

> "Multi-agent systems in 2026 have a single defining question: how do you coordinate agents that cannot share context without poisoning each other?"

2026 年的多 Agent 系统有一个核心问题：**如何协调那些共享上下文就会互相污染的 Agent？** 答案决定了你的系统是能扩展还是会崩溃。

本文从基本原理出发，逐步构建你的思维模型，并将每个概念直接映射到 **Claude Code Dynamic Workflows** 的实际能力。学完本文你会知道：何时用哪种编排拓扑、如何设计不会被污染的 Agent 间通信、哪些失效模式会杀死生产系统、以及如何用 Claude 原生编排栈将它们串联起来。

---

## 一、什么是多 Agent 系统

### Agent 与 Runtime 的区分

- **Agent（单元）：** 一个 LLM 实例 + 自己的系统提示 + 工具集 + 记忆窗口（+ 可能不同的模型）
- **多 Agent 系统（Runtime）：** 协调两个以上 Agent 的机制 — 任务路由、交接、治理层

> **关键洞见：** 多 Agent 系统的大部分故障是 **Runtime 故障**，而非 Agent 故障。单个 Agent 通常推理正确，是系统的协调、上下文传播和权限边界出了问题。

### 为什么单 Agent 会失效

单 Agent 处理大型任务会遇到三个硬限制：

| 限制 | 说明 |
|------|------|
| **Context 饱和** | 每个中间结果都消耗上下文窗口，到后期 Agent 在一大堆自己的历史记录上推理，而不是解决实际问题 |
| **顺序瓶颈** | Agent 一次执行一步。200 个文件的迁移，本可并行，却串行跑数小时 |
| **脆弱恢复** | Agent 中途崩溃或漂移，整个任务重新开始，没有检查点 |

**多 Agent 的解法：** 将工作分布到隔离的 Agent 间、把中间状态存在任何 Agent 的上下文之外、增加阶段级恢复点。

---

## 二、Claude 的三种编排原语

在选拓扑之前，先理解 Claude Code 给你的三种协调原语。选错是最常见的架构错误。

| 原语 | 是什么 | 状态存在哪 | 可重复？ | 最大规模 |
|------|--------|-----------|---------|---------|
| **Subagents** | 主 session 派生的隔离 Claude 实例，只向编排器汇报 | 主 session 的上下文 | ❌ | 每轮几个 |
| **Agent Teams** | 多个 Claude Code session 由 team lead 协调，可通过 mailbox 直接互相发消息 | 各自 session 的上下文 | ❌ | 并行 session |
| **Dynamic Workflows** | Claude 写的 JavaScript 编排脚本，独立 runtime 执行，支持最多 1000 个 Agent | 脚本变量（在上下文之外） | ✅（存为 slash command） | 1000 Agent / 16 并发 |

### 决策规则

- **用 Subagents：** 需要一两个隔离的调查任务，报告回主 session
- **用 Agent Teams：** 团队成员需要互相直接通信（不必经过中央编排器）
- **用 Dynamic Workflows：** 编排本身需要可重复、计划必须能跨上下文窗口存活、或任务需要持续数小时到数天

---

## 三、六种编排拓扑

### 1. Sequential Pipeline（顺序流水线）

```
[Agent A: Parse] → [Agent B: Analyze] → [Agent C: Format]
```

- **何时用：** 工作严格依赖顺序，每一步必须等上一步完成
- **Claude 实现：** 单个 dynamic workflow 脚本里的 prompt chain，每阶段一个 subagent，串行传递结果
- **失效模式：** 延迟累积。Agent B 慢了，整个 pipeline 都等。不要用于有独立并行路径的任务

### 2. Coordinator-Worker / Hub and Spoke（协调器-工作者）

```
          [Coordinator]
        /      |       \
[Security]  [Perf]  [Coverage]
        \      |       /
      [Coordinator: Synthesize]
```

- **何时用：** 工作可分解为不同的专业领域，路由逻辑在计划阶段是稳定的
- **Claude 实现：** Dynamic workflow 的默认形态。编排脚本=协调器，subagents=工作者。Claude 把分解逻辑写在脚本里，不是对话中
- **失效模式：** 协调器单点故障。协调器的上下文填满或漂移，整个系统退化。**修复方法：** 让协调器的职责保持窄 — 只做分解和路由，不做领域推理

### 3. Parallel Fan-Out with Merge（并行扇出+合并）

```
  [Orchestrator]
   |  |  |  |
 [A][B][C][D]   ← 同时执行
   |  |  |  |
[Merge + Reconcile]
```

- **何时用：** 子任务间无依赖。经典场景：审计 200 个文件、查询多个数据源、同时调查 5 个 bug
- **Claude 实现：** Dynamic workflow 默认支持最多 16 个并发 Agent。结果存在脚本变量中，不在编排器的上下文里
- **性能收益：** 无步骤依赖的任务，并行执行削减 60-80% 的处理时间
- **失效模式：** 合并逻辑最难。Agent 返回不一致的 schema 或冲突发现，简单合并会产生垃圾数据。**在写扇出之前先设计好输出契约**

### 4. Generator-Verifier（生成-验证）

```
[Generator] → [Verifier] → passes? → done
     ↑           |
     |-- feedback --| fails? → iterate
```

- **何时用：** 输出质量至关重要，且评价标准可以明确写出来。测试编写、安全发现、迁移计划
- **Claude 实现：** 两阶段 dynamic workflow。Phase 1 并行跑 generator agents，Phase 2 并行跑独立的 verifier agents 检查每个输出。只有通过验证的输出才被合并。这是 Claude dynamic workflow 默认内置的对抗验证机制
- **失效模式：** 验证标准模糊 = 橡皮图章。把验证标准写成显式、可检查的规则

### 5. Shared-State（共享状态）

- **机制：** Agent 通过一个持久存储来协调，大家直接读写，没有中央编排器
- **Claude 实现：** 实际上就是 git worktree 里的文件系统或结构化 docs 文件夹。作者的生产环境做法：**每个决策、计划、完成项都落到结构化 docs 文件夹的 Markdown 文件中，下游 Agent 自动拾取**
- **失效模式：** **Context Poisoning** — 一个 Agent 写了错误发现，所有下游 Agent 都当成真理读入，错误扩散到整个系统

### 6. Debate / Adversarial Multi-Agent（辩论/对抗多 Agent）

```
[Agent: Find Issues] →  claim
[Agent: Refute Issues] →  counter-claim
  [Judge: Reconcile] →  verified finding
```

- **何时用：** 你希望发现先经过对抗压力测试再到你手上。安全审计、迁移风险评估、假阳/假阴有实际成本的工作
- **Claude 实现：** Dynamic workflow 原生支持此模式 — "Agent 从独立角度解决问题，其他 Agent 尝试反驳，循环直到答案收敛"

---

## 四、通信架构

### 直接通信 vs 基底通信

| 方法 | 工作机制 | 风险 |
|------|---------|------|
| **直接 Agent 到 Agent** | Agent A 将输出直接发送到 Agent B 的上下文 | Agent B 继承 Agent A 的错误、偏见和幻觉 |
| **基底中介通信** | Agent 写入共享存储（脚本变量、文件系统、DB），其他 Agent 读取 | Context 可控；错误写操作可隔离 |

**来自生产系统的实际规则：**

> "Agent should not talk to each other directly. They should write to a shared memory layer and read from it."

Claude 的 dynamic workflow 默认使用基底中介通信。中间结果存在**脚本变量**中，不在任何 Agent 的上下文窗口里。这就是为什么编排脚本用 JavaScript 在架构上有意义 — **脚本变量就是基底**。

### 输出契约

生产系统中每个 Agent 都需要显式的输出契约 — 定义它必须返回什么的 schema：

```javascript
// 安全审计 Agent 的输出契约示例
{
  "finding_id": "string",
  "file_path": "string",
  "line_number": "number",
  "severity": "critical | high | medium | low",
  "description": "string",
  "confirmed": "boolean",
  "suggested_fix": "string"
}
```

在 workflow prompt 中强制要求：

```
Return results in this exact JSON schema. If a field cannot be populated,
return null for that field. Do not add fields not in the schema.
```

### Context 窗口预算管理

- **保持编排器窄：** 只做分解和路由，领域推理交给专业 Agent。窄编排器不会用不用的领域知识填满 context
- **限制 Agent 接收的内容：** 只给 Agent 完成特定任务所需要的东西。不要把完整文件树传给只需要三个文件的 Agent
- **热路径限制：** Agent 循环中只保留最近 3-5 次交互在活跃 context。旧的 context 丢弃到共享存储

---

## 五、失效模式

**定义五种会杀死生产多 Agent 系统的失效模式，每种都可预测、可预防。**

### 1. Context Poisoning（上下文中毒）
- **现象：** Agent 将错误输出（幻觉发现、错误 schema、损坏状态）写入共享存储，下游 Agent 当成真理读取并在此基础上构建，错误在整个 pipeline 中叠加
- **迹象：** 看起来合理但无法追溯到实际文件内容的发现；Agent 在同个文件上互相矛盾
- **预防：**
  - 每个写入点做 schema 验证。Agent 不能写原始文本到共享存储
  - Verifier Agent 在**写入共享存储之前**检查输出（不是之后）
  - 结果从一个阶段进入下一阶段之前增加人工审核门

### 2. Cascading Failure（级联故障）
- **现象：** 一个 Agent 失败，编排器没有隔离失败，将坏结果传递到下游。不恰当编排的多 Agent 系统失败率报告为 **41-86.7%**
- **预防：**
  - **断路器：** Agent 返回错误或 null 输出，立即暂停该分支，不转发
  - Pipeline 检查点设置置信度评分：低于阈值的不通过
  - 来自多个 Agent 的独立发现 — 一个失败不能污染整个运行

### 3. Scope Creep（范围蔓延）
- **现象：** 编排器分解太宽泛，Agent 解释自己的任务太随意。被要求"审计代码库"的 Agent 开始修改不该碰的文件
- **预防：**
  - 每个 Agent 在任务 prompt 中有显式、有界的范围：路径、文件类型、允许的操作
  - 编辑策略：默认只读，只有显式授予写权限的路径才能写入
  - Anthropic 设计指导：最小足迹，只请求必要权限，优先用可逆操作

### 4. Silent Substitution（静默替换）
- **现象：** Agent 无法完成某步骤（API 调用失败、文件不可读），偷偷在 try/catch 后面插入占位数据，报告成功。Pipeline 把占位符当成真实结果
- **预防：** 在 CLAUDE.md 或 workflow 的 agent system prompt 中明确要求：「静默失败不允许。每个错误必须在停止之前报告。」

### 5. Coordination Deadlock（协调死锁）
- **现象：** 两个 Agent 互相等待。A 等 B 完成，B 等 A 写共享存储，工作流卡死
- **预防：**
  - 在 workflow 脚本中用显式依赖图（Claude 编排脚本用代码而不是隐式对话顺序编码依赖关系）
  - 每个 Agent 调用设超时 — 超时未返回标记为失败并绕行
  - 扇出之前确保阶段真正独立

---

## 六、治理层

> "The governance layer is what separates a demo from a production system."

### 三层的结构

| 层 | 角色 | 缺少会怎样 |
|-------|------|------------|
| **编排器** | 分解任务、路由给专业 Agent、合成 | 无协调，Agent 重复或冲突工作 |
| **专业 Agent** | 用领域聚焦的 prompt 和工具执行限定操作 | 单 context 瓶颈，无并行 |
| **治理层** | 控制每个 Agent 能访问什么、何时能行动、必须记录什么 | 无检查的工具访问、无审计日志、未验证的输出到达下游系统 |

### 治理层的具体职责

1. **权限范围：** 每个 Agent 有声明的权限集。安全审计 Agent 只读。迁移 Agent 只能写入特定路径。没有 Agent 拥有超出其任务所需的权限
2. **人在回路（HITL）门控：** 定义哪些操作需要人工批准才能执行 — 不可逆操作（文件删除、生产 API 调用、schema 迁移）必须经过 HITL
3. **审计追踪：** 每个 Agent 决策、每个操作、每个工具调用都记录 Agent ID 和导致该决策的推理
4. **爆炸半径限制：** 定义任意单个 Agent 行为失常时能造成的最大损害范围。文件写入限于 worktree，不是 repo root。API 调用限于 staging 环境

### 在 Claude Dynamic Workflows 中实现治理

CLAUDE.md 规则（应用于 session 中所有 Agent）：

```markdown
## Agent Permissions
- Read access: entire repository
- Write access: only paths listed in the task prompt
- Shell commands: only commands on the approved list
- Network: no external calls unless the task prompt specifies an endpoint

## Error Handling
- Silent failures are not permitted
- Every error must be reported before halting

## Irreversible Action Policy
- Database writes require explicit approval in the task prompt
- File deletions require explicit approval in the task prompt
- No production API calls without "production: true" in the task prompt
```

---

## 七、五种 Claude 原生生产模式

Anthropic 从生产环境的实际经验中总结了五种可靠模式，每种都直接映射到 dynamic workflow 结构。

### Pattern 1: Prompt Chaining（提示链）

- **是什么：** 将复杂任务分解成一系列更简单的 prompt，前面输出是后面的输入
- **何时用：** 任务有明显的顺序阶段：文档处理（提取→分析→总结）、数据转换 pipeline、代码生成→测试→评审
- **Claude workflow 形态：** 每阶段一个独立的 Agent 调用，Phase N 的输出通过脚本变量进入 Phase N+1

### Pattern 2: Routing（路由）

```
[Classifier Agent: reads task, returns agent_type]
    |
    → dynamic dispatch to [Security | Code | Performance | Documentation]
```

- **是什么：** 分类器 Agent 读取输入并路由到合适的专业 Agent。分类器不处理任务，只路由
- **何时用：** 任务以异构流到达。编码任务→编码 Agent；安全问题→安全 Agent；文档问题→文档 Agent
- **Claude workflow 形态：** 在 workflow 脚本的路由逻辑中实现分发

### Pattern 3: Parallelization（并行化）

- **是什么：** 扇出独立子任务给多个 Agent 同时执行，最后合并结果
- **Claude workflow 形态：** Dynamic workflow 支持最多 16 个并发 Agent。Token 使用量比顺序链式降低 60-90%，因为中间结果留在脚本变量中

### Pattern 4: Orchestrator-Subagents（编排器-子 Agent）

```
[Orchestrator: decompose goal into subtasks]
    |
    [Security Agent] [Perf Agent] [Coverage Agent]
    |                |             |
    [Orchestrator: synthesize findings]
```

- **是什么：** 编排器接收高层目标→分解子任务→分派给专业 subagents→合成输出
- **何时用：** 工作需要多个专业领域。代码库审计需要安全专家、性能专家、覆盖率专家同时工作
- **关键原则：** 编排器的唯一工作是分解和合成。领域推理属于专业 Agent

### Pattern 5: Evaluator-Optimizer（评估器-优化器）

```
Phase 1: Generator agent produces initial output
Phase 2: Evaluator agent scores against criteria schema
  - Score >= threshold: forward to output
  - Score < threshold: feedback → Phase 1 with iteration count + 1
Phase 3: Max iterations reached: flag for human review
```

- **是什么：** 生成器产出→评估器按显式标准打分→分数+反馈回到生成器→循环直到通过或达到最大迭代数
- **何时用：** 输出质量至关重要且评估标准可写成显式规则。安全发现、迁移计划、测试用例
- **设置硬上限（3-5 次）：** 没有上限，评估标准模糊时循环可能无限继续

---

## 八、从零开始系统设计

在设计多 Agent 系统时，先用这五个步骤，再写任何 workflow prompt。

### Step 1: 任务分解
- 用一个句子写下顶层任务
- 列出完成它所需的每个独立操作，对每个操作回答两个问题：
  1. 这个操作依赖其他操作的输出吗？（顺序依赖）
  2. 这个操作能和其他操作同时运行吗？（并行候选）
- **输出：** 带显式依赖箭头的阶段图

### Step 2: 专业 Agent 识别
- 为每个操作定义需要的专业 Agent，明确：
  - Role（一句话，无歧义）
  - Tool access（只读？写哪些路径？哪些 shell 命令？）
  - Output contract（精确 JSON schema）
  - Failure behavior（无法完成时怎么做）
- **避免通用 Agent：** "什么都能干的编码 Agent" 就是一个 context 臃肿的单 Agent，不是专业 Agent

### Step 3: 通信设计
- 决定：基底中介还是直接通信？（大多数选基底中介）
- 画出数据流：哪个 Agent 在什么时间写什么内容到哪个位置
- 如果某个位置有超过一个 Agent 写入，这就是 context poisoning 的风险点 → 在该位置加验证步骤

### Step 4: 治理契约
- **在写任何 workflow prompt 之前**先写 CLAUDE.md Agent 规则。这迫使你把权限、错误处理、HITL 门控写成显式决策，而非事后想法

### Step 5: 预飞检查清单
在真实仓库上运行任何多 Agent workflow 之前：

- [ ] 在 git worktree 或 feature branch 上工作，不是 main
- [ ] 每个 Agent 的权限范围在 task prompt 中显式限定
- [ ] 向共享存储写入的每个 Agent 都定义了输出契约
- [ ] 关键路径上的每个 generator Agent 都有对应的 verifier/evaluator
- [ ] 所有不可逆操作都有 HITL 门控
- [ ] 所有 evaluator-optimizer 循环设定了最大迭代次数
- [ ] 每个 Agent 都定义了失败行为（大声失败，禁止静默替代）
- [ ] 运行前检查 `/usage`，了解 token 预算

---

## 九、用 Claude 编排栈构建

### 实用架构：Dynamic Workflows + Agent Teams

对大多数生产工程任务，组合两种 Claude 原语：

**外层：Dynamic Workflow**
- Claude 写编排脚本，处理分解、扇出、结果收集、阶段排序
- 中间状态存在脚本变量中
- Workflow 可重跑：保存为 slash command，整个编排变成团队命令

**内层：专业 Subagent**
- 每个阶段分派专业 subagents
- 每个 subagent 有 scope 化的 system prompt（通过 workflow 中 task 定义）、特定文件路径、定义好的输出 schema、失败策略

**需要 Agent 间通信时：Agent Teams**
- 当专业 Agent 需要直接互相发送消息（不只是向编排器报告），用 Claude Code 的 Agent Teams
- 每个 teammate 是一个完整的 Claude Code session，有自己的 context，通过 mailbox 通信
- Team lead 协调但不微操

### Claude Code 内置可观测性

`/workflows` 命令提供每个运行中 dynamic workflow 的实时可观测性：

- 阶段级状态（running/complete/failed）
- Agent 级 drill-down：task prompt、当前状态、当前输出
- 支持暂停、重启单个 Agent、停止整个 workflow
- 在 session 内从检查点恢复
- Agent Teams 中每个 teammate session 可独立检查，可以直接和 teammate 交互而不用通过 lead

---

## 十、扩展与成本控制

多 Agent 系统的成本曲线不是线性的。成本随 Agent 数量叠加。

### Token 成本构成

| 来源 | 说明 |
|------|------|
| **编排规划** | 写 workflow 脚本或分解任务 — 固定成本，每作业一次 |
| **Agent 执行** | 每个 Agent 读任务、读输入、调工具、产输出 — 成本随 Agent 数量线性增长 |
| **合成** | 编排器读所有 Agent 输出并合成 — 成本随输出总量增长 |

Dynamic workflow 通过将中间结果保留在脚本变量中（而不是全部灌进编排器的 context）来削减合成成本。

### 3-7 Agent 规则

- 保持团队小型：每个 workflow phase **3-7 个 Agent**
- 超过这个数，创建层级结构：每组的 team lead → team leads 向全局编排器报告
- 一个协调层里 20+ Agent 的扁平架构有 **二次通信开销** 和协调死锁风险

---

## 十一、决策指南：何时构建多 Agent

### ✅ 构建多 Agent 的场景

- 任务有真正独立的并行路径（且你能枚举它们）
- 工作超出单个 Agent 的 context 窗口且无法在不丢失内容的情况下总结
- 需要对抗验证（经得起反驳的发现比单次通过的发现更有价值）
- 任务持续数小时到数天，需要检查点恢复
- 过程是可重复的（审计、迁移、测试生成），编排本身应该是可复用的工件
- 不同阶段需要真正不同的专业能力或工具集

### ❌ 保持单 Agent 的场景

- 任务是顺序的，没有并行可能
- 工作能舒适地放在一个 context 窗口中
- 协调开销会超过执行时间
- 你还在快速修改系统（多 Agent 架构重构成本高）

### 最大的架构错误

> **"Routing all agent results back through the orchestrator's context."**
>
> 一旦你这样做，你就用额外的网络跳数重建了单 Agent 的 context 瓶颈。中间状态属于基底（脚本变量、文件系统、结构化文档），**不是**编排器的对话历史。
>
> "The orchestrator's context should hold the plan and the final synthesis. Nothing else."

---

## 总结

本文从基本原理到生产实践，完整覆盖了多 Agent 工作流的构建：

1. **先理解问题** — 单 Agent 的三个硬限制（Context 饱和、顺序瓶颈、脆弱恢复）
2. **选对原语** — Subagents vs Agent Teams vs Dynamic Workflows
3. **匹配拓扑** — 六种拓扑对应不同类型的任务
4. **管好通信** — 基底中介通信优于直接通信
5. **预防失效** — 五种可预测的失效模式及预防措施
6. **构建治理** — 权限、HITL、审计、爆炸半径限制
7. **按步骤设计** — 五步法从任务分解到预飞检查
8. **控制规模** — 3-7 Agent 规则、token 预算管理
9. **知道何时不做** — 单 Agent 够用时别用多 Agent

---

*整理于 2026-06-02，原文来自 [@Av1dlive 的 Twitter 长文](https://x.com/av1dlive/status/2061386872321130782)*
