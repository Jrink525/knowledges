---
title: "Agent Harness 解剖学 — 12 个组件构建生产级 AI Agent"
tags:
  - AI-Agents
  - agent-harness
  - orchestration
  - Anthropic
  - OpenAI
  - LangChain
  - production-agents
date: 2026-04-06
source: "https://x.com/akshay_pachaar/status/2041146899319971922"
authors: "Akshay 🚀 (@akshay_pachaar)"
---

# Agent Harness 解剖学 — 12 个组件构建生产级 AI Agent

> **来源：** [The Anatomy of an Agent Harness](https://x.com/akshay_pachaar/status/2041146899319971922) — Akshay 🚀 (Daily Dose of Data Science 联合创始人)

深入剖析 Anthropic、OpenAI、Perplexity 和 LangChain 在实际构建什么。涵盖编排循环、工具、记忆、上下文管理，以及将无状态 LLM 转变为有能力的 Agent 的一切。

---

## 问题不是模型，而是模型周围的一切

你构建过一个 chatbot。也许还搭过一个带几个工具的 ReAct 循环。Demo 跑得挺好。但当你试图构建生产级的东西时，轮子就掉了：模型忘记三步前做了什么、工具调用静默失败、上下文窗口塞满了垃圾。

> 问题不是模型。是模型周围的一切。

LangChain 证明了这一点——他们只改了 LLM 外围的基础设施（同样的模型、同样的权重），在 TerminalBench 2.0 上就从 30 名之外跳到了第 5 名。另一个研究项目通过让 LLM 优化基础设施本身达到了 76.4% 的通过率，超过了手工设计的系统。

**这套基础设施有个名字：Agent Harness（Agent 脚手架/驭具）。**

---

## 什么是 Agent Harness？

![Agent Harness 概念图](../image/anatomy-of-agent-harness-1.jpg)

这个词在 2026 年初被正式化，但这个概念早就存在。Harness 是包裹在 LLM 周围的完整软件基础设施：**编排循环、工具、记忆、上下文管理、状态持久化、错误处理和护栏**。

Anthropic 的 Claude Code 文档说得很直白：SDK 就是"驱动 Claude Code 的 agent harness"。OpenAI 的 Codex 团队也用同样的框架，明确将"agent"和"harness"视为同义词——指代的是让 LLM 变得有用的非模型基础设施。

> **我喜欢 LangChain 的 Vivek Trivedy 给出的公式：** "如果你不是模型，你就是 harness。"

这里有个容易搞混的区别：
- **Agent** 是涌现出来的行为——用户与之交互的那个目标导向、会用工具、自我修正的实体
- **Harness** 是产生那种行为的机器

当有人说"我构建了一个 Agent"，他们实际上构建了一个 harness 并把它指向了一个模型。

### Von Neumann 架构的再发现

Beren Millidge 在 2023 年的文章《Scaffolded LLMs as Natural Language Computers》中把这个类比精准化了：

| LLM 组件 | 计算机架构类比 |
|----------|-------------|
| 原始 LLM | CPU（无 RAM、无磁盘、无 I/O） |
| 上下文窗口 | RAM（快但有限） |
| 外部数据库 | 磁盘存储（大但慢） |
| 工具集成 | 设备驱动程序 |
| **Agent Harness** | **操作系统** |

如 Millidge 所写："我们重新发明了冯·诺依曼架构"——因为这是任何计算系统的自然抽象。

---

## 三个工程层次

围绕模型有三个同心层次的工程：

1. **提示工程**（Prompt Engineering）— 精炼模型接收的指令
2. **上下文工程**（Context Engineering）— 管理模型看到什么、何时看到
3. **Harness 工程**（Harness Engineering）— 包含以上两者，加上整个应用基础设施

> **Harness 不是提示词的包装器。它是使自主 Agent 行为成为可能的完整系统。**

---

## 生产级 Harness 的 12 个组件

![12 个组件概览](../image/anatomy-of-agent-harness-2.jpg)

综合 Anthropic、OpenAI、LangChain 和更广泛的实践者社区，一个生产级 agent harness 有 **12 个不同的组件**：

---

### 1. 编排循环（Orchestration Loop）

这是心跳。它实现了 **Thought-Action-Observation (TAO) 循环**（也叫 ReAct 循环）：

> 组装 prompt → 调用 LLM → 解析输出 → 执行工具调用 → 反馈结果 → 重复直到完成

机械上，它通常只是一个 `while` 循环。复杂性在于循环管理的**一切**，而不是循环本身。Anthropic 将其运行时描述为"愚笨的循环"，所有智能都在模型中——harness 只管理轮次。

---

### 2. 工具（Tools）

工具是 Agent 的手。它们作为**模式（schemas）**（名称、描述、参数类型）注入到 LLM 的上下文中，让模型知道有什么可用。

工具层处理：注册、模式验证、参数提取、沙盒执行、结果捕获、结果格式化回 LLM 可读的观察。

| 框架 | 工具类型 |
|------|---------|
| Claude Code | 6 大类：文件操作、搜索、执行、Web、代码智能、子 Agent 生成 |
| OpenAI Agents SDK | `@function_tool`、托管工具（WebSearch/CodeInterpreter/FileSearch）、MCP 服务器工具 |

---

### 3. 记忆（Memory）

记忆在多个时间尺度上运作：

- **短期记忆**：单次会话内的对话历史
- **长期记忆**：跨会话持久化

Claude Code 实现了一个**三层记忆层级**：

| 层级 | 描述 | 加载策略 |
|------|------|---------|
| 轻量索引 | ~150 字符/条目 | 始终加载 |
| 详细主题文件 | 按需拉取 | 仅在需要时 |
| 原始转录 | 通过搜索访问 | 仅搜索时 |

关键设计原则：Agent 将自己的记忆视为"提示"，在行动前要**与实际状态核对**。

---

### 4. 上下文管理（Context Management）

这是许多 Agent 静默失败的地方。

**核心问题：上下文腐烂（context rot）**——当关键内容落在中间窗口位置时，模型性能下降 30%+（Chroma 研究，被 Stanford 的 "Lost in the Middle" 证实）。即使是百万 token 窗口，随着上下文增长也会出现指令遵循退化。

**生产策略包括：**

| 策略 | 描述 |
|------|------|
| **压缩**（Compaction） | 接近限制时总结对话历史。Claude Code 保留架构决策和未解决的 bug，丢弃冗余工具输出 |
| **观察屏蔽**（Observation masking） | JetBrains 的 Junie 隐藏旧工具输出，同时保持工具调用可见 |
| **即时检索**（Just-in-time retrieval） | 维护轻量标识符，动态加载数据。Claude Code 用 grep/glob/head/tail 而非加载完整文件 |
| **子 Agent 委派** | 每个子 Agent 广泛探索，但只返回 1,000–2,000 token 的浓缩摘要 |

> Anthropic 的上下文工程指南指出目标：**找到最小的高信号 token 集合，最大化期望结果的可能性。**

---

### 5. 提示构建（Prompt Construction）

组装模型在每个步骤实际看到的内容。它是分层的：

> 系统提示 → 工具定义 → 记忆文件 → 对话历史 → 当前用户消息

OpenAI 的 Codex 使用严格的优先级栈：服务器控制系统消息（最高优先级）→ 工具定义 → 开发者指令 → 用户指令（级联的 AGENTS.md 文件，32 KiB 限制）→ 对话历史。

---

### 6. 输出解析（Output Parsing）

现代 harness 依赖**原生工具调用**（native tool calling），模型返回结构化的 `tool_calls` 对象而非需要解析的自由文本。

Harness 检查：
- 有工具调用？执行它们并继续循环
- 没有工具调用？那就是最终答案

对于结构化输出，OpenAI 和 LangChain 都支持通过 Pydantic 模型的 schema 约束响应。

---

### 7. 状态管理（State Management）

| 框架 | 方法 |
|------|------|
| LangGraph | 类型化字典流经图节点，reducers 合并更新。检查点实现中断后恢复和时间旅行调试 |
| OpenAI | 四种互斥策略：应用内存、SDK sessions、服务端 Conversations API、轻量 `previous_response_id` 链 |
| Claude Code | git commit 作为检查点，progress 文件作为结构化草稿板 |

---

### 8. 错误处理（Error Handling）

> 一个 10 步流程，单步成功率 99%，端到端成功率只有 ~90.4%。错误迅速累积。

LangGraph 区分四种错误类型：

| 错误类型 | 策略 |
|---------|------|
| 瞬态错误（Transient） | 带退避的重试 |
| LLM 可恢复 | 将错误作为 ToolMessage 返回，让模型调整 |
| 用户可修复 | 中断等待人工输入 |
| 意外错误 | 冒泡出来用于调试 |

Anthropic 在工具处理器内捕获失败并以错误结果返回，让循环继续运行。**Stripe 的生产 harness 将重试次数上限设为 2。**

---

### 9. 护栏与安全（Guardrails and Safety）

OpenAI 的 SDK 实现**三级护栏**：
- 输入护栏（在第一个 agent 上运行）
- 输出护栏（在最终输出上运行）
- 工具护栏（在每次 tool 调用上运行）
- "绊线"（Tripwire）机制：触发时立即停止 Agent

Anthropic 在架构上将**权限执行与模型推理分离**：
1. 模型决定尝试什么
2. 工具系统决定允许什么

Claude Code 独立管控约 40 个离散的工具能力，分三个阶段：项目加载时的信任建立 → 每次工具调用前的权限检查 → 高风险操作的显式用户确认。

---

### 10. 验证循环（Verification Loops）

这是玩具 Demo 与生产级 Agent 的分水岭。

Anthropic 推荐三种方法：

| 方法 | 描述 |
|------|------|
| 基于规则的反馈 | 测试、linter、类型检查器 |
| 视觉反馈 | 通过 Playwright 截图进行 UI 任务审查 |
| LLM-as-judge | 一个单独的子 Agent 评估输出 |

> Claude Code 的创建者 Boris Cherny 指出：**给模型验证其工作的方式可以提高 2–3 倍的质量。**

---

### 11. 子 Agent 编排（Subagent Orchestration）

| Agent 系统 | 子 Agent 模式 |
|-----------|-------------|
| Claude Code | Fork（字节级拷贝父上下文）、Teammate（独立终端面板 + 基于文件的邮箱通信）、Worktree（自己的 git worktree，隔离分支） |
| OpenAI SDK | Agents-as-tools（专家处理有限的子任务）、Handoffs（专家接管全部控制） |
| LangGraph | 嵌套状态图作为子 Agent |

---

### 12. 上下文管理与压缩（详见 #4）

已在上文组件 4 中详细讨论，但它在实际中是一个贯穿所有组件的横向能力。

---

## 循环在运行中：逐步演示

![Step-by-step walkthrough 图](../image/anatomy-of-agent-harness-3.jpg)

**Step 1 — 提示组装：** Harness 构建完整输入：系统提示 + 工具模式 + 记忆文件 + 对话历史 + 当前用户消息。重要上下文放在开头和结尾（"Lost in the Middle"）。

**Step 2 — LLM 推理：** 组装的 prompt 发送给模型 API。模型产生输出 token：文本、工具调用请求，或两者都有。

**Step 3 — 输出分类：** 只有文本且无工具调用 → 循环结束。有工具调用 → 执行。有交接请求 → 更新当前 agent 并重启。

**Step 4 — 工具执行：** 对每个工具调用，harness 验证参数、检查权限、在沙盒环境中执行、捕获结果。只读操作可并发；变更操作串行执行。

**Step 5 — 结果打包：** 工具结果格式化为 LLM 可读的消息。错误被捕获并以错误结果返回，让模型自我修正。

**Step 6 — 上下文更新：** 结果追加到对话历史。接近上下文窗口限制时，触发压缩。

**Step 7 — 循环：** 回到 Step 1，重复直到终止。

**终止条件**是分层的：
- 模型产生无工具调用的响应
- 超过最大轮次限制
- token 预算耗尽
- 护栏绊线触发
- 用户中断
- 安全拒绝返回

一个简单问题可能 1–2 轮。一个复杂重构任务可以跨几十轮链式调用上百次工具。

### 跨上下文窗口的 Ralph 循环

![Ralph 循环模式图](../image/anatomy-of-agent-harness-4.jpg)

对于跨多个上下文窗口的长周期任务，Anthropic 开发了**两阶段 Ralph Loop 模式**：

1. **初始化 Agent** — 设置环境（init 脚本、progress 文件、功能列表、初始 git commit）
2. **编码 Agent** — 后续每个 session 读取 git log 和 progress 文件来定位自己，挑选最高优先级的未完成功能，工作，commit，写摘要

文件系统在上下文窗口之间提供了连续性。

---

## 主流框架如何实现 Harness

![框架对比图](../image/anatomy-of-agent-harness-5.jpg)

### Anthropic — Claude Agent SDK
通过单一的 `query()` 函数暴露 harness，创建 agentic 循环并返回异步迭代器流式传输消息。运行时是"愚笨循环"，**所有智能都在模型中**。Claude Code 使用 Gather-Act-Verify 循环：收集上下文（搜索文件、读代码）→ 行动（编辑文件、运行命令）→ 验证结果（运行测试、检查输出）→ 重复。

### OpenAI — Agents SDK / Codex
通过 `Runner` 类实现 harness，有三种模式：async、sync、streamed。SDK 是"代码优先"的——工作流逻辑用原生 Python 表达而非图 DSL。Codex Harness 有三层架构：Codex Core（agent 代码 + 运行时）、App Server（双向 JSON-RPC API）、客户端表面（CLI、VS Code、Web App）。所有表面共享同一个 harness——这就是"Codex 模型用 Codex 表面比通用聊天窗口更好"的原因。

### LangChain — LangGraph
将 harness 建模为显式状态图。两个节点（`llm_call` 和 `tool_node`）通过条件边连接：有工具调用 → 路由到 `tool_node`；没有 → 路由到 END。Deep Agents 显式使用"agent harness"术语：内置工具、规划（`write_todos` 工具）、用于上下文管理的文件系统、子 Agent 生成、持久记忆。

### CrewAI
基于角色的多 Agent 架构：Agent（LLM 周围的 harness，由 role、goal、backstory 和 tools 定义）、Task（工作单元）、Crew（Agent 集合）。Flows 层增加了"确定性骨架，在关键处注入智能"。

### AutoGen → Microsoft Agent Framework
开创了对话驱动的编排。三层架构（Core、AgentChat、Extensions）支持五种编排模式：顺序、并发（fan-out/fan-in）、群聊、交接、magnetic（管理 Agent 维护动态任务账本，协调专家）。

---

## 脚手架隐喻

![脚手架隐喻图](../image/anatomy-of-agent-harness-6.jpg)

脚手架隐喻不是装饰性的。它是精确的。

建筑脚手架是**临时基础设施**，使工人能够构建原本无法够到的结构。它不做建筑本身。但没有它，工人无法到达上层。

> **关键洞察：建筑完成后，脚手架被拆除。随着模型改进，harness 复杂性应该降低。**

Manus 在六个月内重建了五次，每次重写都删除了复杂性：
- 复杂的工具定义 → 通用的 shell 执行
- "管理 Agent" → 简单的结构化交接

### 共同演化原则

> 模型现在是在**特定 harness 参与下**进行后训练的。

Claude Code 的模型学会了使用它被训练时用的特定 harness。**更改工具实现可能会降低性能**——因为这种紧密耦合。

**Harness 的"未来验证"测试：** 如果更强的模型能让性能提升而无需增加 harness 复杂性，那么设计就是合理的。

---

## 定义每个 Harness 的七个决策

![七个决策图](../image/anatomy-of-agent-harness-7.jpg)

每个 harness 架构师面临七个选择：

### 1. 单 Agent vs 多 Agent
Anthropic 和 OpenAI 都说：**先最大化单 Agent**。多 Agent 系统增加开销（路由的额外 LLM 调用、交接过程中的上下文丢失）。只有在工具超载（超过 ~10 个重叠工具）或存在明确分离的任务域时才拆分。

### 2. ReAct vs 规划-执行
- **ReAct**：每一步交织推理和行动（灵活但单步成本高）
- **Plan-and-execute**：将规划与执行分离。LLMCompiler 报告比顺序 ReAct **快 3.6 倍**

### 3. 上下文窗口管理策略
五种生产方法：时间清除、对话摘要、观察屏蔽、结构化笔记、子 Agent 委派。ACON 研究表明：通过优先保留推理轨迹而非原始工具输出，**减少 26–54% token，同时保持 95%+ 准确率**。

### 4. 验证循环设计
- **计算验证**（测试、linter）— 提供确定性基准真相
- **推理验证**（LLM-as-judge）— 捕获语义问题但增加延迟

Martin Fowler 的 Thoughtworks 团队将其框架化为：**Guides**（前馈，在行动前引导）vs **Sensors**（反馈，在行动后观察）。

### 5. 权限与安全架构
- **宽松型**（Permissive）— 快速但有风险，自动批准大多数操作
- **限制型**（Restrictive）— 安全但慢，每次操作需要批准

选择取决于部署环境。

### 6. 工具范围策略
> **更多工具往往意味着更差性能。**

- Vercel 从 v0 中移除了 80% 的工具，结果更好了
- Claude Code 通过惰性加载实现 **95% 的上下文缩减**
- 原则：**暴露当前步骤所需的最小工具集**

### 7. Harness 厚度
有多少逻辑放在 harness 中 vs 留给模型？

- Anthropic 押注**薄 harness + 模型改进**
- 基于图的框架押注**显式控制**

Anthropic 定期从 Claude Code 的 harness 中删除规划步骤——因为新的模型版本已经**内化了**那种能力。

---

## Harness 即产品

![Harness 即产品图](../image/anatomy-of-agent-harness-8.jpg)

使用相同模型的两个产品，仅因 harness 设计不同，性能可能天差地别。TerminalBench 的证据很清楚：**仅仅更改 harness 就让 Agent 提升了 20+ 排名位置。**

Harness 不是一个已解决的问题或商品化层。它是硬工程所在：
- 将上下文作为稀缺资源管理
- 设计在失败累积前捕获它们的验证循环
- 构建提供连续性而不产生幻觉的记忆系统
- 对需要建造多少脚手架 vs 留给模型多少做出架构赌注

这个领域正随着模型改进而走向更薄的 harness。但 harness 本身不会消失。**即使是最有能力的模型，也需要有人来管理它的上下文窗口、执行它的工具调用、持久化它的状态、验证它的工作。**

> **下次你的 Agent 失败时，别怪模型。检查 harness。**

---

*Processed on 2026-06-14 from https://x.com/akshay_pachaar/status/2041146899319971922*
