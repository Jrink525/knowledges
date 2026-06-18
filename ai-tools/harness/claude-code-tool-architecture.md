---
title: "Claude Code 的工具架构深度解析"
tags:
  - Claude-Code
  - AI-Agents
  - tool-architecture
  - Anthropic
  - agent-systems
date: 2026-06-17
source: "https://x.com/spandan_madan/status/2067320100911493454"
authors: "Spandan Madan (@spandan_madan)"
---

# Claude Code 的工具架构深度解析

> **来源：** [The Tool Architecture of Claude Code](https://x.com/spandan_madan/status/2067320100911493454) — Spandan Madan

![cover](../image/claude-code-tool-architecture-cover.jpg)

> 深入剖析 Claude Code 如何发现、调度和执行工具

之前我们通过泄露的源码逆向分析了 Anthropic Harness 的记忆系统——结果出乎意料地简单：Markdown 文件、frontmatter 和 prompt 工程。

工具系统则恰恰相反。它是整个代码库中**工程最复杂的子系统**：43+ 个工具、流式执行管道、分层权限系统、钩子框架和并发调度器——全部组装起来，把一个无状态的语言模型变成能读文件、跑 shell 命令、搜索网页、生成子 agent 的系统。

本文追踪一个工具的完整生命周期：从如何定义，到模型的工具调用如何被调度，再到结果如何流回对话。

---

## 四层架构概览

```
Tool Interface（工具接口）
  → Registry（注册器）组装工具池
    → Dispatch Pipeline（分发管道）验证→权限→执行
      → Concurrency Scheduler（并发调度器）决定并行策略
```

---

## 工具接口（Tool Interface）

每个工具都实现同一个接口，定义在 **Tool.ts** 中。类型是泛型的，参数为 **Input**（Zod schema）、**Output**（结果类型）和 **P**（进度数据）。实际工具对象有约 30 个方法。

核心形状：

- **buildTool()** 工厂函数提供安全的默认值
- 默认值刻意保守：没声明并发安全 → 串行执行；没实现权限检查 → 默认弹窗请求权限。系统默认关闭（fail closed）
- **ToolResult** 包含结果数据 + **contextModifier**（允许工具改变后续工具的执行上下文，如 **EnterWorktree** 改变工作目录）
- 关键约束：**contextModifier 只允许非并发安全的工具使用**。并行工具不能修改共享状态

---

## 工具注册器（Tool Registry）

所有工具在 **getAllBaseTools()**（tools.ts）中注册为一个扁平的数组。

### 始终可用（16 个工具）
Shell 执行、文件读写、搜索、编辑、Web 抓取、子 agent 生成、通知、图像理解等。

### 按功能开关启用（约 27 个工具）
环境变量控制：`USER_TYPE=ant` 解锁 Anthropic 内部工具（config、tungsten）
功能开关控制（通过 Statsig）：web_browser、sleep、monitor
平台特定：powershell（Windows）
复合条件：repl 工具同时要求 `USER_TYPE=ant` + REPL 功能开关

### MCP 工具（Model Context Protocol）
支持外部进程通过标准化协议暴露工具。MCP 工具在运行时从已连接的服务器动态注册，封装成相同的 **Tool** 接口。**从分发管道的角度看，MCP 工具和内建工具完全一样。**

每个 MCP 工具携带原服务器的元数据（`mcpInfo: { serverName, toolName }`），用于权限规则、错误处理和认证。认证失败时自动更新服务器状态为 `needs-auth` 并通知用户。

### 工具池组装

三个函数构建最终的工具集：

1. **getAllBaseTools()** — 返回 43+ 个内建工具的原始列表（功能开关已应用）
2. **getTools(permissionContext)** — 根据拒绝规则和 isEnabled() 过滤
3. **assembleToolPool(permissionContext, mcpTools)** — 合并内建和 MCP 工具

合并策略是刻意的：**内建工具排在前面**，同名冲突时内建胜出。每个分区内部按字母排序以保持跨会话稳定——这对 prompt 缓存很关键（工具数组是 API 请求的一部分，重排会导致缓存失效）。

### API 序列化

工具到达 Claude API 之前，**toolToAPISchema()** 将每个工具的 Zod schema 转换为 Anthropic API 的 JSON Schema 格式。

---

## 分发管道（The Dispatch Pipeline）

当 Claude 响应时，消息可能包含 **tool_use** 块——结构化的工具调用请求。分发管道通过 **7 个阶段**处理这些块。

### 阶段 1：提取（Extraction）
在主查询循环（query.ts）中，tool_use 块从助手消息内容中过滤出来。每个块有 **name**、**input** 对象和唯一的 **id**。id 至关重要——工具结果必须引用相同的 id 才能返回给 API，否则对话会断裂。

### 阶段 2：输入验证（Input Validation）
工具的 Zod schema 使用 **safeParse()** 验证原始输入——不抛异常的变体，返回有效数据或结构化错误。验证失败时，模型收到格式化的错误消息和 schema 提示，工具不执行。**无效输入上不运行任何代码。**

Zod 验证后，部分工具还要过第二道 **validateInput()** 检查——用于 schema 无法表达的语义验证（如检查文件路径是否为绝对路径）。

### 阶段 3：钩子前处理（Pre-Tool Hooks）
在权限检查之前，用户配置的钩子（外部 shell 命令或脚本）在工具调用时触发。钩子可以：
- **允许**工具调用（绕过交互式权限弹窗）
- **彻底拒绝**工具调用
- **在执行前修改输入**
- **阻塞执行**并返回错误消息
- **向用户提供额外上下文**

关键不变约束：**钩子的「允许」不绕过 settings.json 的拒绝/询问规则。** 源码中有显式注释：钩子能开门，但不能覆盖锁。

### 阶段 4：权限检查（Permission Check）
权限系统是管道中最复杂的部分。按顺序分层解析：

1. **拒绝规则** — 最先检查。任何匹配都立即停止执行。拒绝规则是最终的，不能被任何其他层覆盖
2. **询问规则** — 如果匹配，向用户发起审批弹窗
3. **工具特定权限** — 工具的 **checkPermissions()** 方法运行（如 BashTool 解析命令检查子命令级规则）
4. **安全检查** — 敏感路径（`.git/`、`.claude/`、shell 配置文件）的硬编码保护——即使在完全绕过模式下也无法绕过，必须交互式审批
5. **权限模式** — 用户配置的模式确定默认行为
6. **允许规则** — 最后检查。匹配且未触发拒绝/询问时，工具执行

权限规则来自多个来源，按优先级解析：**policySettings → localSettings → projectSettings → userSettings → flagSettings → cliArg → command → session**。组织策略覆盖用户偏好，CLI 参数覆盖前两者。

### 阶段 5：执行（Execution）
权限通过后，调用工具的 **call()** 方法：

五个参数：验证后的输入、执行上下文（工作目录、中止控制器、应用状态）、权限回调（工具在运行中如需额外权限）、父级助手消息、进度回调（实时更新）。**全局追踪执行时长。**

一个微妙细节：传入 **call()** 的输入是模型的**原始输入**，不是钩子和权限看到的补全版本。这保证了对话记录的一致性——记录中的工具调用与模型生成的内容完全匹配。

### 阶段 6：钩子后处理（Post-Tool Hooks）
执行后，post-tool 钩子触发。可以修改 MCP 工具输出、提供额外上下文、或阻止对话继续。还有一个独立的 **PostToolUseFailure** 钩子（仅错误时触发），让外部系统记录失败或建议补救。

### 阶段 7：结果映射（Result Mapping）
每个工具实现 **mapToolResultToToolResultBlockParam()**，将输出转换为 Anthropic API 的 **ToolResultBlockParam** 格式——包含 **tool_use_id** 引用和字符串或结构化内容的 **tool_result** 块。

如果结果超过大小阈值（如 10,000 行的文件读入），则持久化到磁盘 **sessionDir/tool-results/{toolUseId}.txt**，只发送摘要给 API。防止大输出膨胀对话上下文。

---

## 并发调度器（The Concurrency Scheduler）

当模型在一次消息中发出多个工具调用时，它们不是同时执行的。调度器根据并发安全性将调用分批。

算法很简单：按顺序遍历工具调用。检查 **isConcurrencySafe(input)**。如果安全且上一个批次也安全，加入当前批次；否则开始新批次。

- **安全批次**：并行运行（最多 10 个，可通过 `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY` 配置）
- **不安全批次**：串行运行，一次一个
- **Context modifier** 只在批次之间应用，不在批次内

实践中，这意味着「读这 5 个文件」产生一个并发批次，而「读这个文件，然后编辑它」产生两个串行批次。模型甚至可以在单轮中触发两种模式——连续的只读调用被批量，第一个写入打断批次。

### 流式执行器（Streaming Executor）
还有第二条执行路径：**StreamingToolExecutor**。启用流式时，**工具在模型还在生成响应时就开始执行**。每个 tool_use 块在流中一完成，就立即排队执行，不必等完整响应。

流式执行器使用相同的并发规则，但增加了一个行为：**Bash 错误级联**。如果 Bash 命令失败而兄弟工具正在并行运行，执行器中止所有兄弟。理由是失败的 Bash 命令很可能使其他工具操作的上下文失效——继续运行浪费时间和可能造成混乱的错误。

---

## 一个完整示例

模型决定读一个文件时的完整流程：

1. **提取**：query.ts 从助手消息内容中过滤出 tool_use 块
2. **工具查找**：**findToolByName(tools, "read")** 找到 FileReadTool
3. **输入验证**：Zod 解析 `{ file_path: "/src/index.ts" }` 通过
4. **钩子前处理**：用户配置的钩子触发（无修改）
5. **权限检查**：FileReadTool 的 checkPermissions() 调用 checkReadPermissionForTool()。读工具在大多数权限模式下默认允许
6. **执行**：FileReadTool.call() 读取文件，应用行号（cat -n 格式），处理 PDF/图片/notebook 等特殊文件
7. **结果映射**：文件内容变成引用 "toolu_01XYZ" 的 tool_result 块
8. **返回**：结果作为用户消息追加到对话，在下次 API 调用中发送

因为 FileReadTool 声明了 `isConcurrencySafe: () => true` 和 `isReadOnly: () => true`，如果模型在同一消息中发出五个读调用，全部并行执行。

---

## 值得关注的要点

### 模型即调度器
并发调度器是被动的——它批量处理模型发出的任何内容。但**模型本身才是真正的调度器**。系统提示告诉模型「所有独立的工具调用要并行发出」、「用单个 Bash 调用 + && 链式依赖命令」。运行时信任这个。调度器在执行模型的计划，而非制定自己的计划。

### 默认关闭（Fail-Closed by Default）
最一致的设计原则：一切默认关闭。未知工具？错误。无效输入？错误。无并发声明？串行执行。无权限声明？问用户。无功能开关？工具不存在。这对一个主要用户是可能幻觉工具名称或错误格式输入的 AI 系统来说很特别。**系统旨在包含模型的错误，而非迁就它们。**

### 钩子作为扩展点
钩子系统（pre-tool、post-tool、post-failure）是主要的扩展点。组织通过它执行策略（pre-hook 中的拒绝规则），日志系统捕获工具使用（post-hook），CI/CD 管道集成（错误钩子）。重要的是：**钩子只能收紧限制，不能放松。** 钩子可以拒绝设置允许的工具，但不能允许设置拒绝的工具。

### 43 个工具，1 个接口
最令人印象深刻的是统一性。一个 **bash** 命令、一个 **web_fetch**、一个子 agent 生成、一个 cron 创建、一个推送通知——都实现相同的 30 方法接口，经历相同的 7 阶段管道，遵循相同的权限系统。**分发器中没有特殊情况。** 复杂度在单个工具实现和权限规则中，不在路由中。

---

## 总结

相比于记忆系统（5 个路径、一个 Markdown 文件目录和 prompt 工程），工具系统是一个**真正的运行时**。区别就像文件柜和操作系统之间的差距。

- **保守的工具工厂**：安全默认值、默认串行、默认询问
- **功能开关注册器**：控制可用性，MCP 扩展
- **7 阶段分发管道**：提取→验证→钩子→权限→执行→钩子→映射
- **并发调度器**：按安全性分批，流式提前执行，Bash 错误级联
- **分层权限**：拒绝 > 询问 > 工具特定 > 安全硬编码 > 模式 > 允许

*Processed on 2026-06-18 from https://x.com/spandan_madan/status/2067320100911493454*
