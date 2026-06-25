---
title: "从提示者到循环设计师：10 步路线图"
tags:
  - AI-Agents
  - Claude-Code
  - Agent-Design
  - Loop-Architecture
  - Automation
date: 2026-06-24
source: "https://x.com/de1lymoon/status/2069726411724673077"
authors: "Alex (@de1lymoon)"
---

# 从提示者到循环设计师：10 步路线图

> **来源：** [From prompter to loop designer: the 10-step roadmap](https://x.com/de1lymoon/status/2069726411724673077) — Alex (@de1lymoon)，Polymarket & AI 写手

![封面](../image/from-prompter-to-loop-designer-cover.jpg)

---

## 核心论点

大多数人使用 Claude Code 的方式是：输入请求 → 看它工作几分钟 → 读结果 → 输入下一个请求。他们只是**提示者（prompter）**—— 工具在他们手中，但每次都要手动操作。

循环设计师（loop designer）构建的是不同的东西：一个**能自我提示的系统**。它按定时器运行、对照目标自我检查、需要时衍生帮手、把学到的东西记下来让下一轮更聪明。

这两者之间的差距不是天赋，也不是更好的 prompt。**是十步可学的路线图**。

---

## 第一层 · 看清循环（Tier 1 · See the Loop）

### 01. 循环就是加了个定时器的 prompt

![01](../image/from-prompter-to-loop-designer-2.jpg)

去除神秘感，循环的核心只有一个想法：**不是你发送下一个 prompt，而是系统自己发送**。

```
定时器 → Prompt → Agent 执行 → 对比目标 → 完成？
```

### 02. 先搭好 harness（运行环境）

![02](../image/from-prompter-to-loop-designer-3.jpg)

循环的质量取决于它运行的环境。这个环境就是 **harness**：模型、可用工具、工具权限、每轮开始时读取的上下文。

> 在自动化之前，先让一次手动运行可靠。

关键要素：
- `CLAUDE.md`：记录基础设施级事实
- 清晰的验证目标
- 正确的工具连接

**薄弱的 harness + 循环 = 垃圾产出得更快。**

### 03. 自我改进的是系统，不是模型

"自我改进的 Agent"容易让人误解。**模型的权重不会变**——它每次运行都是一样的。真正改进的是它周围的系统：

- 积累的记忆（memory）
- 处理了大量边界案例后变精准的技能（skills）
- 让它诚实的评分者（grader）

你要做的不是等模型变聪明，**是构建一个每次运行都在变聪明的环境**。

---

## 第二层 · 构建循环（Tier 2 · Build the Loop）

### 04. 设定目标和独立的评分者

循环需要一个停止条件，而不是"Agent 觉得自己完成了"。

```bash
> /goal All tests pass and lint is clean.
  Triage failures, draft fixes, repeat until the goal holds.
```

关键：**独立**。决定"完成"的东西，不能是做工作的那个。这一层分离让循环值得信赖。

### 05. 把执行者与检查者分开

![05](../image/from-prompter-to-loop-designer-4.jpg)

模型评判自己的输出时，会偏袒自己的推理——它倾向于和自己已写内容一致的结论。

**独立的 Agent，有自己的上下文窗口**，只看到产物和标准，不涉及执行者的决策。

定义验证器为子 agent：

```markdown
---
name: verifier
description: 独立检查执行者输出是否符合目标。每次迭代使用。
tools: Read, Grep, Bash
---
你没有产生这些工作。对照目标和项目规则检查。
自己跑测试。报告通过/失败并附具体理由和文件引用。
不要仁慈。
```

循环有了执行者（maker）和检查者（checker），**检查者掌控门**。

### 06. 上定时器，然后上云

目标驱动的运行仍然等着你开始它。下一步是加节奏：

```bash
> /loop 30m
  拉取新的失败测试，在 claude/ 分支起草修复方案，
  交给验证器检查。/goal main is green.
```

![06](../image/from-prompter-to-loop-designer-6.jpg)

然后把笔记本电脑去掉。**Cloud routines** 在 Anthropic 管理的基础设施上按计划（定时器/事件）运行保存的配置。定时器让执行变成习惯，云让习惯变成基础设施。

### 07. 用 workflow 编排复杂任务

有些任务对单个循环来说太结构化：大规模并行、多阶段、或需要多个独立视角。Claude Code 可以自己写编排计划并严格执行：

```bash
> Build a workflow: for each failing test, spawn an agent to draft a
  fix, run them in parallel, then have the verifier check every diff
  before anything merges.
```

![07](../image/from-prompter-to-loop-designer-5.jpg)

三种最有用的工作流形状：

1. **Fan out and synthesize** — 拆分工作，并行运行，合并结果
2. **Adversarial verification** — 每个任务都有执行者和独立检查者
3. **Loop until stop condition** — 直到条件满足

![07b](../image/from-prompter-to-loop-designer-7.jpg)

工作流的质量取决于它能调用的子 agent 和技能 —— 所以 harness 要在前面搭好。

---

## 第三层 · 让循环复利（Tier 3 · Make It Compound）

### 08. 给循环记忆

![08](../image/from-prompter-to-loop-designer-8.jpg)

Agent 每次运行之间会忘记一切。**循环不需要**。

状态文件（state file）记录：尝试了什么、什么有效、什么失败了、什么成为了规则。

两条规则让它复利而非增长：
- **走之前写**：每次运行结束时更新文件
- **开始前读**：每次运行开始时加载它

两个规则缺一不可——跳掉任何一个，明天就从零开始。

### 09. 将经验提炼为技能

状态文件是项目记忆，随项目结束而消亡。那些通用的、能帮到下一个项目的经验，要**升级为技能**：

```markdown
---
name: ci-triage
description: 分类 CI 失败，容易的起草修复方案，其余升级处理。
---
## 已知失败模式
- tls-handshake: Windows runner 在 PowerShell 中 TLS 1.2 失败。用 bash。
- db-migration: 超过 1M 行的表 ALTER 超时。按 10k 批次。

## 反模式
- 永远不要为了 CI 变绿而禁用失败的测试。应该提交 issue。
```

循环遇到瓶颈时，教训进入技能。**每个未来的循环、每个未来的项目都继承它。**

这就是"每次重新推导环境"和"站在已有知识上"的区别。

### 10. 闭合循环，安全失效

![10](../image/from-prompter-to-loop-designer-9.jpg)

各部分锁在一起：
- 每轮产生输出
- 验证器评分
- 结论写入记忆
- 通用经验提炼为技能
- 下一轮继承了更锋利的技能和更丰富的记忆

**模型从未改变。系统变锋利了。这就是"自我改进"的诚实含义。**

但无人值守的循环必须安全失效——这就是 guardrails 的作用：

```json
{
  "permissions": {
    "allow": ["Read(*)", "Bash(npm run test *)"],
    "deny": ["Bash(git push origin main)", "Bash(rm *)", "Edit(.env)"]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "./.claude/hooks/block-dangerous.sh" }
        ]
      }
    ]
  }
}
```

同时按成本路由：**编排器用重量级模型**，高吞吐量的 pass 用便宜模型，顶级模型拒绝的任务有 fallback。一个能无人运行、不会做不可逆操作的循环，才是你真正能丢下不管的。

---

## 常见错误（阻止循环复利的陷阱）

1. **薄 harness 上跑循环** — 循环放大其底下的一切。弱 harness 只是更快产出垃圾
2. **让执行者自我评分** — 自我检查是自信的机器，不是正确的机器。检查者需要自己的上下文窗口
3. **没有停止条件** — 没有独立评分者可检查的目标，循环停在"差不多够了"
4. **没有记忆** — 每轮从零开始。这是复利无声流失的地方
5. **经验从未离开状态文件** — 通用的经验留在项目范围内就随项目消亡。要升级为技能
6. **无人值守的循环权限太宽** — 没人看着每一步，hooks 和 deny 不是可选项
7. **每次都跑顶级模型** — 按任务路由，或用便宜模型也能干好的工作就别烧钱

---

## 总结

提示者有一个强大的工具，手动操作它。循环设计师构建一个自我运行的系统，只在需要人的部分召唤他们：设定目标、定义标准、按合并按钮、处理不可逆操作。

从一个到另一个的转变不是一个秘密 prompt——而是一个序列：

> **把 Agent 看作循环 → 构建它运行的 harness → 给目标和诚实的评分者 → 上定时器 → 教它记忆 → 提炼所学**

中间的那个模型从头到尾都没变。**变的是你包裹在它外面的那个循环。**

**挑一个你还没在做的步骤——找一个独立的评分者、一个状态文件、或者一个安全 hook——今天加上。然后下一个。停止优化 prompt。开始设计循环。**

---

*整理于 2026-06-25，来源：https://x.com/de1lymoon/status/2069726411724673077*
