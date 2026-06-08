---
title: "Agent Harness 的解剖学 — Agents = Model + Harness"
tags:
  - agent
  - agent-harness
  - langchain
  - architecture
  - deepagents
date: 2026-06-07
source: "https://x.com/vtrivedy10/status/2031408954517971368"
authors: "Viv (Vtrivedy10) — applied research @LangChain"
---

# Agent Harness 的解剖学

> **来源：** [The Anatomy of an Agent Harness](https://x.com/vtrivedy10/status/2031408954517971368) — Viv (@Vtrivedy10), applied research @LangChain

---

## 核心论点

**Agent = Model + Harness**

> *"If you're not the model, you're the harness."*

**Harness** 是模型中"非模型"之处的全部代码、配置和执行逻辑的总和。原始模型不是 agent，但给它加上 state、工具执行、反馈循环和可执行约束后，它就变成了 agent。

**TLDR**：Harness engineering = 围绕模型构建系统，把智力转化为工作引擎。

---

## 一、Harness 的定义

### Harness 具体包含什么？

- **System Prompts** — 系统提示词
- **Tools, Skills, MCPs + 描述** — 工具、技能、MCP 服务及描述
- **捆绑的基础设施** — 文件系统、沙箱、浏览器
- **编排逻辑** — 子 agent 生成、交接、模型路由
- **Hooks / Middleware** — 确定性执行（compaction、continuation、lint 检查）

### 为什么需要 Harness

模型本身只能做一件事：输入（文本/图像/音频/视频）→ 输出文本。开箱即用，模型 **不能**：

- 维持跨交互的持久状态
- 执行代码
- 访问实时知识
- 搭建环境、安装依赖完成工作

**这些都是 harness 层的特性。**

---

## 二、核心 Harness 组件逐一推导

### 2.1 文件系统 — 持久存储 & 上下文管理

> 行为目标：Agent 需要持久存储来读写真实数据、卸载超出上下文的负载、跨会话持久化工作。

- 模型只能操作上下文窗口内的知识。以前用户得手动 copy/paste → 体验差且不适合自动化 agent。
- 世界本来就用文件系统工作，模型天然训练了数十亿 token 的 fs 使用方式。
- **Harness 方案**：内置文件系统抽象 + fs 操作工具。

**文件系统的核心价值**：
- Agent 获得 workspace 读取数据、代码、文档
- 增量工作可卸载到 fs，不挤占 context window，跨会话持久化
- **文件系统是天然的协作面** — 多个 agent 和人类通过共享文件协调，Agent Teams 架构依赖此特性
- Git 增加版本管理：追踪工作、回滚错误、分支实验

### 2.2 Bash + 代码执行 — 通用工具

> 行为目标：Agent 能自主解决问题，无需人类预设计每个工具。

- 主流执行模式：ReAct 循环（推理 → 工具调用 → 观察结果 → 重复）
- 但 harness 只能执行它有逻辑的工具。用户不可能预建所有工具。
- **Harness 方案**：给 agent 通用工具 — Bash。

Bash + 代码执行 ≈ 给模型一台计算机让它自己搞定。模型能通过代码动态设计工具，不受固定工具集限制。
代码执行已成为自主解决问题的默认通用策略，但 harness 仍然会附带其他工具。

### 2.3 沙箱 — 安全执行 & 验证环境

> 行为目标：Agent 需要安全的运行环境来执行、观察结果、推进工作。

- 本地运行 agent 生成的代码有风险，单一本地环境无法扩展到大规模负载。
- **Harness 方案**：沙箱提供安全操作环境。Harness 连接沙箱执行代码、检查文件、安装依赖。
  - 允许列表命令、强制网络隔离
  - 环境可按需创建、扇出任务、完成后销毁

**工具链加持**：
- 预装语言运行时、包、CLI（git, 测试）、浏览器
- 浏览器、日志、截图、测试运行器 → agent 可观察分析自己的成果
- 形成**自验证循环**：写代码 → 跑测试 → 查日志 → 修 bug

> *模型不会自己配置执行环境。在哪儿运行、用什么工具、访问什么、如何验证 — 都是 harness 层面的设计决策。*

### 2.4 记忆 & 搜索 — 持续学习

> 行为目标：Agent 应记住见过的东西，访问训练时不存在的信息。

- 模型除了权重和当前上下文，没有额外知识。不加权重就只能靠上下文注入"添加知识"。
- **记忆方案**：文件系统再次成为核心 — AGENTS.md 这类记忆文件标准 → agent 启动时注入上下文
  - Agent 编辑该文件 → harness 加载更新版 → 跨会话持久化知识 → 持续学习

- **知识截止**：模型无法直接访问新数据（如更新的库版本）。**Harness 方案**：Web Search + MCP 工具（如 Context7）
  - 访问训练截止后的信息（新库版本、实时数据）

### 2.5 对抗 Context Rot（上下文腐败）

> 行为目标：Agent 性能不应随时间衰减。

**Context Rot** = 模型在上下文窗口填满后推理和完成任务的能力下降。上下文是宝贵的稀缺资源。

**Harness 策略**：

1. **Compaction（压缩）** — 上下文即将填满时，智能卸载和总结现有上下文，让 agent 继续工作
2. **工具调用卸载** — 大型工具输出噪声多 → 保留头尾 token，完整输出写入文件系统供按需访问
3. **Skills 渐进式披露** — 启动时加载太多工具/MCP 会降低性能。Skills 通过渐进式披露保护模型不受 context rot 影响

> Harness 基本上是好的上下文工程的交付机制。

### 2.6 长周期自主执行

> 行为目标：Agent 能自主、正确、长时间地完成复杂任务。

自主软件创建是 coding agent 的圣杯。但模型面临：过早停止、复杂问题分解困难、跨多上下文窗口的不连贯。

**Harness 方案 — 前序 primitives 的叠加效应**：

- **文件系统 + Git** — 跨会话追踪工作。Agent 在长任务中产生数百万 token，fs 持久化记录进度，Git 让新 agent 快速掌握项目历史和当前进展。多 agent 协作时，fs 充当共享工作账本。
- **Ralph Loops** — 拦截模型退出尝试 → 在干净的上下文窗口中重新注入原始提示 → 强迫 agent 继续工作至完成。文件系统让每次迭代从全新上下文启动但仍能读取前序状态。
- **规划 & 自验证** — 模型将目标分解为步骤。Harness 通过好的提示 + 规划文件来支持。完成每步后通过自验证（预定义测试套件或模型自我评估）确保正确性，失败时形成反馈信号循环。

---

## 三、Harness 的未来

### 模型训练与 Harness 设计的耦合

当代 agent 产品（Claude Code、Codex）是模型 + harness 在循环中联合训练的结果。模型被训练来擅长 harness 设计者认为其应当擅长的行为（文件操作、bash 执行、规划、子 agent 并行）。

这形成了**反馈循环**：
1. 发现有用的 primitive → 加入 harness
2. 下一代模型训练时使用该 harness
3. 模型在新 harness 内能力更强

但副作用：**过拟合**。改变工具逻辑会导致模型性能下降。如 Codex-5.3 中 `apply_patch` 工具的逻辑变更就影响了效果。

> 这并不意味着"模型训练时用的 harness 就是最好的"。Terminal Bench 2.0 排行榜显示：Opus 4.6 在 Claude Code 中得分远低于在其他 harness 中的表现。该作者团队通过仅更改 harness 就将 coding agent 从 Top 30 提升到了 Top 5。

**Harness 优化能榨出大量性能空间。**

### 未来趋势

随着模型变得更强，部分当前 harness 的功能会被模型吸收（规划、自验证、长周期连贯性 — 原生支持减少上下文注入）。

但就像 prompt engineering 今天仍有用一样，**harness engineering 在可预见的未来仍是构建好 agent 的关键**。合理的环境配置、正确的工具、持久状态和验证循环，能让任何模型更高效。

### LangChain DeepAgents 的开放课题

1. 在共享代码库上编排数百个并行工作的 agent
2. Agent 分析自身 trace 来识别和修复 harness 级别的失效模式
3. 动态即时组装工具和上下文的 harness（而非预先配置）

---

## 总结

| 行为目标 | Harness 解决方案 |
|---|---|
| 持久存储、读写数据 | 文件系统 + Git |
| 自主解决问题 | Bash / 代码执行 |
| 安全执行环境 | 沙箱 + 预装工具链 + 自验证 |
| 记忆 & 实时知识 | AGENTS.md 记忆文件 + Web Search/MCP |
| 上下文窗口管理 | Compaction + 工具卸载 + 渐进式披露 |
| 长周期自主工作 | Ralph Loops + 规划 + 自验证 |

> *The model contains the intelligence and the harness is the system that makes that intelligence useful.*

---

*整理于 2026-06-07，来源：Viv (@Vtrivedy10) / LangChain*
