---
title: "I Built an Agentic Harness From Scratch — What Agents Actually Are"
source: "https://x.com/ByteMohit/status/2063493300884246598"
author: "Mohit Goyal (@ByteMohit)"
project: "AgentForge"
published: 2026-06-07
category: "ai-tools/agent-engineering"
tags: [agent, harness, MCP, tool-design, safety, context, subagent, persistence]
---

# AgentForge：从零构建 Agent Harness 学到的东西

> Mohit Goyal 花了几个月用 Python 从零构建 AgentForge（一个开源的 agent harness），不依赖任何框架。  
> 核心洞见：**Agent 不是模型。Agent 是控制模型如何看、如何做、如何重试、如何记忆、如何停止的运行时（Runtime）。**

---

## 一句话总结

模型只占工程量的 20%，剩下的 80% 是外围的**行动空间、审批策略、观察格式、上下文预算、恢复路径、持久化层**。这篇文章讲的就是这 80%。

---

## 1. 第一个错误：把 Agent 当函数调用

**天真模式：** `用户消息 → 模型 → 回复`

这对聊天机器人够用，对 coding agent 远远不够。

**一个 coding agent 需要知道：**
- 当前在哪个目录、哪些工具可用、当前什么模型、什么审批模式
- 已经发生了什么、加载了哪些 skill、连接了哪些 MCP 服务
- 还剩多少上下文窗口、当前是 plan 模式还是 build 模式
- 后续是否能恢复、是否在形成死循环

**所以 AgentForge 的第一个核心对象不是模型客户端，而是 Session（会话）。**

Session 在第一次调用模型之前就构造好了模型的世界——哪个工具存在、哪些 MCP 工具被注册、哪些 skill 可见、什么操作模式。**运行时拥有模型，不是反过来。**

> 💡 **关键思想：模型不会自己去发现世界，Harness 决定了模型看到的世界是什么。**

---

## 2. Agent 循环是一个控制系统

**教科书画的循环：** `LLM → tool → observation → LLM`

**真实循环要考虑：**
- 上下文窗口压力（context pressure）
- 模型失败和降级
- 工具算力预算（turn budget）
- Plan/Build 模式切换
- 重复动作检测
- 流式输出
- 崩溃检查点

**AgentForge 的 LoopDetector：** 监控连续相同的工具调用。如果 agent 连续三次调用了 `read_file` 同一路径而没有中间的编辑操作→判定为死循环→强制模型输出最终答案。

**断路器（Circuit Breaker）：** 如果某个模型（provider）持续返回错误，断路器打开→harness 自动切换到下一个备用模型。模型会失败。不处理这个问题的 harness 只是 demo。

> 💡 **Agent 循环不是简单的循环，它是一个关于「进展」的策略引擎。** 决定什么时候继续、什么时候停止、什么时候隐藏工具、什么时候压缩历史、什么时候问用户、什么模式表示 agent 卡住了。

---

## 3. 工具契约（Tool Contract）—— Agent 真正变得有用的地方

**最重要的教训：工具设计 = Agent 设计。**

模型只能通过你给的行动空间来行动。如果工具名重叠→它犹豫；如果 schema 模糊→它猜测；如果结果不透明→它无法恢复；如果错误只说"failed"→它死循环或幻觉下一步。

**AgentForge 每个工具的返回值是结构化的 `ToolResult`：**

```python
ToolResult(
    success=True,
    summary="在 README.md 中找到了 3 处拼写错误",
    artifacts=[...],        # 什么改变了 / 接下来可以检查什么
    next_actions=[...],     # 安全的下一个动作
    recovery_hint=...       # 避免盲目重试的提示
)
```

**关键字段解释：**
- `summary`：用自然语言告诉模型发生了什么
- `artifacts`：变化的内容或可检查的内容
- `next_actions`：安全的下一个操作建议
- `recovery_hint`：失败后如何恢复，而不是盲目重试

连失败的工具调用也要遵循这个契约——裸的异常消息告诉模型「坏了」，结构化的错误结果告诉模型「哪里坏了、怎么修、下一步该做什么」。这个差距就是「死循环 agent」和「能恢复的 agent」的差距。

**工具注册表（Registry）把每个结果变成一致的数据管道：** 每个工具结果（成功或失败）都经过清理、脱敏、prompt-injection 标记、钩子处理后才到模型。**工具执行在外部世界，注册表把结果转回安全的观察。这就是 harness 的边界。**

---

## 4. 文件工具——小细节决定一切

文件读取器不只是返回文本，它还需要：
- 行号
- offset 和 limit（处理大文件）
- 二进制文件检测
- 是否被截断
- 尾部换行符状态（因为 patch 能否干净应用取决于文件末尾有没有换行符）

**编辑工具要求精确的 old_string 匹配。** 如果找不到→不静默失败→展示文件中相似的行→给出恢复提示：重新读文件，因为上下文中的版本可能已经过期了。

> 💡 **小细节会变成模型行为。** 坏的工具让模型去猜隐藏状态。好的工具暴露模型安全行动所需的状态。

---

## 5. 审批不能靠「氛围」

你可以让模型「小心」。但你仍然需要在模型之外强制安全。

**AgentForge 的审批模式：** on-request、auto、auto-edit、never、yolo

审批层检查：是否可变、命令模式、影响的路径、危险标识、配置策略。

**Plan 模式不是靠 prompt 说「不要编辑文件」。** 在 AgentForge 中，plan 模式在注册表层面过滤动作空间——模型在 plan 模式下根本**收不到**写入工具。它即使想调也调不了。这是真正的边界，不是礼貌的指令。

> 💡 **安全属于策略和执行层，不属于文字。**

---

## 6. Prompt Injection——工具输出进入上下文后完全不一样

一开始以为 prompt injection 只是网页浏览的问题。然后你构建了一个 coding agent，意识到**每次文件读取也都是 prompt 输入**。

- 仓库文件可以包含指令
- shell 命令可以打印指令
- 网页可以包含指令
- MCP 服务器可以返回指令

如果这些输出作为普通文本回到模型，模型可能会把它当做指导。

**AgentForge 把工具观察包装为不可信内容（untrusted content）：** 每个观察都明确标记为来自特定源的数据。模型看到包装器和指令的分离。这种边界是结构性的，不是对话性的。

> 💡 **工具输出是证据。工具输出不是权威。**

---

## 7. 上下文不是对话记录

**小规模：** 把一切都追加

**真实规模：** 这样会变成十轮之前的过时工具输出塞满半个上下文窗口的混乱记录

**AgentForge 的策略：**
- 跟踪 token 估计
- 上下文快满时发出警告
- 修剪旧的工具输出
- 压缩旧历史，保留近期轮次

这是有意的设计：**近期轮次是高分辨率工作记忆，旧轮次可以变成一段延续性摘要，已完成的工作必须显式保存防止 agent 重复做。**

压缩本身也消耗模型调用——AgentForge 记录它的 token 消耗，这样 session 的总成本已经包含了压缩成本。

---

## 8. Skills 是上下文预算管理

**你不仅要决定模型能做什么，还要决定模型当前允许思考什么。**

AgentForge 支持本地 `SKILL.md` 文件，核心设计是**渐进式披露（progressive disclosure）**：
- 不把每个 skill 正文都加载进 system prompt
- 索引元数据
- 只在 skill 被显式选中时加载完整正文

`discover()` 和 `load_skill()` 是分离的操作。Discovery 构建索引。Loading 消耗上下文预算。这个区分是显式的，让基础 prompt 保持精简。

---

## 9. MCP——外部工具需要边界，不只是注册

**大多数框架把 MCP 服务器当插件系统：** 连上、拿工具、完事。

**但外部工具引入了本地工具没有的问题：**
- 命名冲突
- 传输失败
- 启动时序
- 信任模糊性
- 外部工具输出是否应该和本地工具输出一样处理

**AgentForge 的方案：**
- MCP 工具进入注册表时带显式命名空间：`filesystem__read_file`、`github__create_issue`
- MCP 工具**不绕过注册表**。完整管道仍然适用：schema 暴露、模式过滤、审批检查、输出卫生、脱敏、injection 标记、钩子

> 💡 **扩展系统只有在保留 harness 契约时才有用。为外部工具创造「二等路径」的插件架构是带洞的安全模型。**

---

## 10. Subagent（子智能体）首先是工具，其次才是群体

**AgentForge 中的子智能体是一个工具。** 父 agent 传入目标。工具生成一个子 agent（带作用域配置、允许的工具、最大轮数、硬超时）。一个输入。一个结果。父 agent 保持控制。

**内置子 agent 刻意设计为只读：** explorer、debugger、codebase investigator、code reviewer、test planner、architect。默认都不能写文件或运行变异 shell 命令。父 agent 决定怎么处理它们的返回。

> 💡 **先把子 agent 当工具。边界迫使你定义契约。契约工作良好后，再考虑扩展。**

---

## 11. 持久化——失败故事让它变得真实

持久化一开始觉得很简单：保存 JSON、加载 JSON、完事。

然后 harness 开始触及真正的机器状态。Session 快照、检查点、事件日志需要存到文件系统。AgentForge 用 `platformdirs` 确定数据目录（Linux: `~/.local/share/agentforge/`），使用原子写入和仅拥有者权限。

**一个真实问题：** 测试不应该依赖开发者的真实家目录状态。之前有些测试因为读取的是之前手动运行的遗留状态时而通过时而失败。解决方案很无聊：在隔离的家目录中跑测试。

> 💡 **Agent Harness 不光是 prompt 实验。它们是读文件、写状态、生成进程、处理权限、必须处理部分失败的软件。**

---

## 12. 可测试的 Harness

大多数人认为 agent 很难测试，因为模型的输出是非确定性的。

**这对于模型的文案是对的。但对于 harness 契约是错的。**

AgentForge 有 278 个测试覆盖：
- 配置加载、Session 状态、plan 模式工具过滤
- 上下文管理和压缩、环路检测
- 工具 schema、文件工具行为、patch 验证、shell 工具策略
- 输出卫生、脱敏、prompt-injection 包装
- 持久化快照、报告、skills、MCP 相邻行为

**这些测试没有一个需要真正的模型调用。**

> 💡 **Agent 可靠性的一大部分来自确定性的 harness 行为，和模型智能无关。如果你的 harness 契约坏了，世界上最聪明的模型也补偿不了。**

---

## 总结：给任何想学 Agent Engineering 的人的建议

**不要一开始就构建巨大的框架。构建一个小型 harness：**

1. 构建一个模型适配器
2. 构建带停止条件的循环
3. 构建三个工具：`read_file`、`edit`、`shell`
4. 让工具类型化
5. 让工具结果结构化为 `summary`、`next_actions`、`recovery_hint`
6. 写入前加审批
7. 文件读取加行号
8. 失败路径加恢复提示
9. 添加上下文裁剪
10. 添加一个检查点
11. 添加一个 skill
12. 添加一个 MCP 服务器并给它的工具加命名空间
13. 添加一个工具调用失败的测试，验证模型能得到有用的观察

**到那时，真正的问题就变得无法回避了：**
- 什么行动应该存在？
- 什么模型永远不能直接做？
- 工具运行后模型该看到什么？
- 在这之前什么应该被脱敏？
- 什么应该算作不可信？
- 循环什么时候停？
- 什么状态必须在崩溃后存活？
- 哪些部分可以在不调用模型的情况下测试？

> **这就是 Agentic Engineering。不仅仅是提示工程。是行动空间设计、观察设计、上下文设计、恢复设计、安全设计、运行时设计。**

---

## 项目信息

- **GitHub**: [MohitGoyal09/AgentForge](https://github.com/MohitGoyal09/AgentForge)
- **PyPI**: `agentforge-harness`
- **安装**: `pip install agentforge-harness`
- **测试**: 278 passed（不依赖真实模型调用）
