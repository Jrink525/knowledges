---
title: "Agent Harness 深度解析 — Akshay Pachaar 解读 Anthropic/OpenAI/LangChain 的 12 组件架构"
tags:
  - agent-harness
  - agent-architecture
  - anthropic
  - openai
  - langchain
  - orchestration
  - context-management
  - akshay-pachaar
date: 2026-06-03
source: "https://x.com/akshay_pachaar/status/2041146899319971922"
authors: Akshay Pachaar
---

# Agent Harness 深度解析 — 12 组件架构

> **来源：** [Akshay Pachaar 的 X 长文](https://x.com/akshay_pachaar/status/2041146899319971922)  
> **中文整理：** 涵盖 Agent Harness 定义、12 个组件、框架实现对比、7 个架构决策

## 核心命题：Harness 才是产品

**LangChain 只改写了 LLM 外围的 infrastructure（同一模型、同一权重），在 TerminalBench 2.0 上从 30 名外冲到了第 5 名。** 另一个研究项目用 LLM 自行优化基础设施，达到了 76.4% pass rate，超越手工设计的系统。

这个基础设施有一个名字：**Agent Harness**。

> **核心公式** (LangChain's Vivek Trivedy)  
> *"If you're not the model, you're the harness."*

---

## 一、概念基础

### 什么是 Agent Harness？

Agent Harness 在 2026 年初被正式命名，但其概念早已存在。它是包裹 LLM 的**完整软件基础设施**：

- 编排循环 (Orchestration Loop)
- 工具 (Tools)
- 记忆 (Memory)
- 上下文管理 (Context Management)
- 状态持久化 (State Persistence)
- 错误处理 (Error Handling)
- 护栏 (Guardrails)

> **Agent ≠ Harness** — Agent 是**涌现行为**（有目标、会用工具、能自我纠正的实体），而 Harness 是**产生这种行为的基础设施**。你说"我构建了一个 agent"，实际上是你构建了一个 harness 然后指向了一个模型。

### Von Neumann 类比（Beren Millidge, 2023）

| 计算机组件 | Agent 系统中对应 |
|-----------|----------------|
| CPU | 原始 LLM |
| RAM | 上下文窗口（快但有限） |
| 磁盘 | 外部数据库（大但慢） |
| 设备驱动 | 工具集成 |
| 操作系统 | **Harness** |

> *"We have reinvented the Von Neumann architecture."*

### 三个工程层级

1. **Prompt Engineering** — 模型收到的指令
2. **Context Engineering** — 模型看到什么、何时看到
3. **Harness Engineering** — 包括以上两者 + 完整应用基础设施

> Harness 不是 prompt 的包装器，它是一个完整的系统，使得自主 Agent 行为成为可能。

---

## 二、12 个生产级 Harness 组件

### 1. 编排循环 (Orchestration Loop)

心跳。实现 Thought-Action-Observation (TAO) 循环，也叫 ReAct 循环。

流程：组装 prompt → 调 LLM → 解析输出 → 执行工具调用 → 反馈结果 → 重复直到完成。

核心洞察：**循环本身只是一个 while 循环**，复杂度在循环管理的内容上。Anthropic 称他们的 runtime 是 "dumb loop"，所有智能都在模型里。Harness 只是管理轮次。

**Gather-Act-Verify 周期（Claude Code）：**
```
Gather context → Take action → Verify results → Repeat
```
搜索文件、读代码 → 编辑文件、跑命令 → 跑测试、检查输出 → 重复

### 2. 工具 (Tools)

工具的完整生命周期：注册 → 模式验证 → 参数提取 → 沙箱执行 → 结果捕获 → 格式化回 LLM 可读的 observation。

| 来源 | 工具类型 |
|------|---------|
| OpenAI Agents SDK | `@function_tool` + hosted tools (WebSearch, CodeInterpreter, FileSearch) + MCP |
| Claude Code | 六类：文件操作、搜索、执行、Web访问、代码智能、子Agent分发 |

### 3. 记忆 (Memory)

记忆在多个时间尺度上运作：

| 类型 | 说明 | 示例 |
|------|------|------|
| 短期记忆 | 单个 session 内的对话历史 | 当前上下文窗口 |
| 长期记忆 | 跨 session 持久化 | CLAUDE.md, MEMORY.md, JSON Stores, SQLite / Redis |

**Claude Code 三级记忆体系：**
1. **轻量索引**（~150 字符/条，始终加载）
2. **详细主题文件**（按需拉取）
3. **源生对话**（仅通过搜索访问）

> **关键设计原则：** Agent 把自己的记忆当作"提示"，在执行动作前必须与实际状态**核对验证**，不能直接信记忆。

### 4. 上下文管理 (Context Management)

**为什么重要：** 当关键内容落在中间位置时，模型性能下降 30%+（Chroma 研究，Stanford "Lost in the Middle" 验证）。即使是百万 token 窗口，随着上下文增长指令遵循能力也会下降。

**生产级策略：**

| 策略 | 说明 | 代表 |
|------|------|------|
| **压缩** (Compaction) | 接近上下文限制时，总结对话历史，保留架构决策和未解决 bug，丢弃冗余工具输出 | Claude Code |
| **Observation 遮蔽** | 隐藏旧的工具输出，但保留工具调用可见 | JetBrains Junie |
| **即时检索** | 只维持轻量标识符，按需加载数据 | Claude Code（grep/glob/head/tail 而非加载全文件） |
| **子 Agent 委派** | 每个子 Agent 深入探索但只返回 1000~2000 token 的摘要 | 通用 |

> **Anthropic Context Engineering 目标：** 找到最小的、信号密度最高的 token 集合，最大化预期结果的概率。

### 5. Prompt 构建

层次化组装模型实际看到的内容：

```
系统 prompt → 工具定义 → 记忆文件 → 对话历史 → 当前用户消息
```

**OpenAI Codex 优先级栈（严格顺序）：**
1. 服务器控制的消息（最高优先级）
2. 工具定义
3. 开发者指令
4. 用户指令（级联 AGENTS.md 文件，32 KiB 限制）
5. 对话历史

### 6. 输出解析

现代 harness 依赖**原生 tool calling**——模型返回结构化的 `tool_calls` 对象，而非需要解析的文本。

循环逻辑：
- 如果有 tool calls → 执行后继续循环
- 如果没有 tool calls → 最终答案，结束

结构化输出：通过 Pydantic 模型的 schema 约束响应（OpenAI + LangChain）。

### 7. 状态管理

| 框架 | 方案 |
|------|------|
| **LangGraph** | 类型化字典 + reducers 合并更新，checkpoint 在 super-step 边界，支持中断恢复和时间旅行调试 |
| **OpenAI** | 四种互斥策略：应用内存 / SDK sessions / 服务端 Conversations API / `previous_response_id` 链 |
| **Claude Code** | git commit 作为 checkpoint + progress 文件作为结构化草稿板 |

### 8. 错误处理

> **数学：** 10 步流程，每步 99% 成功率 → 端到端只有 ~90.4%。错误快速累积。

**LangGraph 四种错误类型：**
- **瞬态** — 重试 + backoff
- **LLM 可恢复** — 以 ToolMessage 返回错误，让模型自我调整
- **用户可修复** — 中断等待人工输入
- **意外** — 向上冒泡供调试

**Anthropic：** 在 tool handler 内捕获失败，以错误结果返回，保持循环运行。  
**Stripe 生产 harness：** 重试次数上限设为 2 次。

### 9. 护栏和安全

| 框架 | 实现 |
|------|------|
| **OpenAI SDK** | 三级：输入护栏（首个 agent 运行）→ 输出护栏（最终输出）→ 工具护栏（每次调用）。Tripwire 机制立即终止 |
| **Anthropic** | 权限判断与模型推理**架构性分离**。模型决定做什么，工具系统决定允许做什么。Claude Code 独立管控 ~40 个工具权限：项目加载时建立信任 → 每次调用前检查权限 → 高风险操作显式确认 |

### 10. 验证循环

> *What separates toy demos from production agents.*

| 验证方式 | 说明 |
|---------|------|
| **规则验证** | 测试、linter、类型检查器 |
| **视觉验证** | Playwright 截图 (UI 任务) |
| **LLM 裁判** | 独立 subagent 评估输出 |

> **Boris Cherny (Claude Code 创造者)：** 给模型验证自己工作的能力，**质量提升 2~3 倍。**

### 11. 子 Agent 编排

| 框架 | 模式 |
|------|------|
| **Claude Code** | Fork（父 context 完全复制） / Teammate（独立终端窗格 + 文件 mailbox） / Worktree（独立 git worktree + 隔离分支）|
| **OpenAI SDK** | agents-as-tools（专家处理有界子任务） / handoffs（专家完全接手控制权）|
| **LangGraph** | 嵌套状态图 |

---

## 三、循环执行：逐步骤跟踪

```
Step 1 (Prompt Assembly): 组装完整输入 (系统 + 工具 + 记忆 + 历史 + 消息)
Step 2 (LLM Inference): 模型生成输出 (文本 / tool calls / 两者)
Step 3 (Output Classification):
  - 纯文本无 tool calls → 结束
  - 请求 tool calls → 执行
  - 请求 handoff → 更新 agent 后重启
Step 4 (Tool Execution): 验证参数 → 检查权限 → 沙箱执行 → 捕获结果
  - 只读操作可并发，可变操作串行
Step 5 (Result Packaging): 结果格式化 → 错误返回为错误消息供模型自我修正
Step 6 (Context Update): 追加结果到对话历史 → 接近限制时触发压缩
Step 7 (Loop): 回到 Step 1，直到终止
```

**终止条件（分层）：** 无 tool call 响应 / 达最大轮次 / 预算耗尽 / 护栏触发 / 用户打断 / 安全拒绝。

**长任务（跨多个上下文窗口）：Anthropic 的 Ralph Loop 模式**
- Initializer Agent：设置环境（init 脚本、progress 文件、功能列表、初始 git commit）
- Coding Agent：后续每个 session 里读 git log + progress 文件 → 选最高优先级未完成功能 → 工作 → commit → 写摘要
- 文件系统提供跨上下文窗口的连续性

---

## 四、各框架如何实现 Harness

| 框架 | Harness 实现方式 |
|------|----------------|
| **Anthropic Claude Agent SDK** | 通过 `query()` 函数暴露 harness，返回 async iterator 流式消息。runtime 是 "dumb loop" |
| **OpenAI Agents SDK** | `Runner` 类（async / sync / streamed 三种模式）。Code-first——workflow 逻辑用 Python 而非图 DSL 表达。Codex 三层架构：Core + App Server (JSON-RPC) + 客户端 (CLI/VS Code/Web) |
| **LangGraph** | 显式状态图。两个节点 (llm_call + tool_node) + 条件边。从 AgentExecutor (v0.2 弃用) 进化而来 |
| **CrewAI** | 角色化架构：Agent(harness, 含角色/目标/背景/工具) → Task → Crew。Flows 层提供"确定性骨架 + 智能节点" |
| **AutoGen → Microsoft Agent Framework** | 对话驱动编排。三架构层 (Core / AgentChat / Extensions)，五种编排模式：顺序、并发(fan-out/fan-in)、群聊、handoff、magentic |

---

## 五、脚手架隐喻

> 脚手架是临时基础设施，让工人能到达他们原本够不到的上层。它不参与建造——但没有它，工人无法到达任何上层。

**核心洞察：** 建筑完成后脚手架会拆除。**随着模型提升，harness 复杂度应降低。**

真实案例：Manus 在 6 个月内重建了 5 次，**每次都在消除复杂度**。复杂的工具定义变成通用的 shell 执行。"管理 Agent"变成了简单的结构化 handoff。

**共进化原则：** 模型现在是在特定 harness 环境下进行后训练的。Claude Code 的模型学到的是如何使用与自己训练时一致的 harness。**改变工具实现可能降低性能**，因为耦合紧密。

> **未来验证测试：** 如果更强的模型来了，不需要增加 harness 复杂度就能性能放大 → 设计就是好的。

---

## 六、7 个架构决策

### 1. 单 Agent vs 多 Agent
- **Anthropic + OpenAI 共识：** 先最大化单 agent。
- 多 agent 有额外开销（路由的额外 LLM 调用、handoff 时上下文丢失）
- 只在工具超载（~10 个重叠工具以上）或明显分离的任务域时才拆分

### 2. ReAct vs Plan-and-Execute
- **ReAct：** 每步交错推理和行动（灵活但单步成本高）
- **Plan-and-Execute：** 计划和执行分离。LLMCompiler 报告相对于顺序 ReAct 有 **3.6x 加速**

### 3. 上下文窗口管理策略
五种生产策略：
- 时间清理
- 对话摘要
- Observation 遮蔽
- 结构化笔记
- 子 Agent 委派

**ACON 研究：** 通过优先保留推理链、丢弃原始工具输出，实现 **26~54% token 缩减**，同时保持 95%+ 准确率。

### 4. 验证循环设计
- **计算验证（tests, linters）：** 确定性的 ground truth
- **推断验证（LLM-as-judge）：** 捕获语义问题但有延迟

**Martin Fowler's Thoughtworks 团队：** Guide（前馈，在行动前引导）vs Sensor（反馈，观察行动后）

### 5. 权限和安全架构
- **宽松（permissive）：** 快速但有风险，自动批准多数操作
- **严格（restrictive）：** 安全但慢，每次操作需确认

选择取决于部署环境。

### 6. 工具范围策略
- 更多工具 ≠ 更好性能。**Vercel 从 v0 移除了 80% 的工具，获得了更好的结果。**
- **Claude Code 通过懒加载实现了 95% 的上下文缩减。**
- 原则：只暴露当前步骤需要的最小工具集。

### 7. Harness 厚度
- **Anthropic：** 押注 thin harness + 模型持续提升
- **基于图的框架：** 押注显式控制
- Anthropic 在新模型版本吸收了规划能力后，**定期从 Claude Code 的 harness 中删除规划步骤**。

---

## 七、Harness 即产品

> 两个使用相同模型的产品，仅因 harness 设计不同，就能有悬殊的性能差异。TerminalBench 证据：**只改变 harness 就让 agent 排名移动 20+ 位。**

Harness 不是一个已解决的问题，也不是一个可商品化的层。**它是最困难工程所在的地方**：把上下文作为稀缺资源来管理，设计能捕捉错误的验证循环以防错误累积，构建提供连续性的记忆系统而不产生幻觉，以及做架构性赌注——多少脚手架需要搭、多少该留给模型。

> *"The next time your agent fails, don't blame the model. Look at the harness."*

---

## 八、关键金句总结

| 金句 | 出处 |
|------|------|
| "If you're not the model, you're the harness." | Vivek Trivedy, LangChain |
| "We have reinvented the Von Neumann architecture." | Beren Millidge, 2023 |
| "A separate research project hit 76.4% pass rate by having an LLM optimize the infrastructure itself." | 研究基准 |
| "Scaffolding is removed when the building is complete." | 脚手架隐喻 |
| "Manus was rebuilt five times in six months, each rewrite removing complexity." | Manus 开发实践 |
| "Vercel removed 80% of tools from v0 and got better results." | Vercel |
| "The model decides, the tool system decides what's allowed." | Anthropic 安全架构 |
| "Giving the model a way to verify its work improves quality by 2 to 3x." | Boris Cherny |
| "The next time your agent fails, don't blame the model. Look at the harness." | Akshay Pachaar |

---

*整理于 2026-06-03，基于 [akshay_pachaar 的 X 长文](https://x.com/akshay_pachaar/status/2041146899319971922)*
