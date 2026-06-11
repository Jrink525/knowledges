# Claude Agent SDK 深度入门 + Replit 实战部署（@mattyp 视频文字稿）

> **来源**: X/Twitter @mattyp 视频教程 (30 min)
> **链接**: <https://x.com/mattyp/status/2021962510702645629>
> **转录工具**: 本地 Whisper small.en (ONNX)
> **日期**: 2026-06-11

---

## 一、Claude Agent SDK 是什么

Claude Agent SDK 允许我们**程序化地创建 Agent**——和 Claude Code 使用的是同一套 Agent 系统。你提供 prompt，SDK 负责处理整个 loop，直到某个终止条件满足，然后用户提供下一次输入。

SDK 的核心能力远不止简单的 loop：

- 构建**多 Agent / Agent 层级**，不同 Agent 执行不同任务
- 使用**开放标准**：Skills、MCP Servers、Permissions、其他工具
- 支持**委派**：将任务派给更 specialized 的子 Agent

### Agent 编排示例：写作工作流

一个典型的 orchestrator（编排器）模式：

1. 用户通过 prompt 提交任务 → Orchestrator Agent 接收
2. Orchestrator 将写作主题派发给 **Author Agent**
3. Author 完成写作后，交给 **Reviewer Agent** 审查
4. 结果返回给用户

### 核心原语（Core Primitives）

**1. Query Loop（查询循环）**

Agent 的本质很简单：接受 prompt → 使用工具 → 执行工具 → 观察结果 → 重复 → 返回输出。

**2. Tools（工具）**

Agent 使用的工具，就像人用锤子敲钉子一样。常见工具：
- 命令行工具（如 Bash）
- Git 操作（commit 到 GitHub）
- 可自定义的定制工具

通过构建自定义工具，可以让 Agent 完成特定任务（如管理 Todoist 收件箱）。

**3. MCP Servers（Model Context Protocol）**

MCP 是**定制化的工具集合**，遵循开放标准。安全、可复用。可以理解为"给 Agent 的一整盒工​​具"。

**4. Skills**

Skills 是**指令集**——一组 Markdown 文件，教 Agent 如何做事。Skills 比 MCP 更新，更像"说明书"而非"工具箱"。

> 💡 **一句话区分**：Skills 定义 Agent **怎么做**，MCP 定义 Agent **有什么工具可用**。

---

## 二、Skills vs MCP Servers

这是最容易混淆的概念，Matt 专门花了篇幅讲解。

### Skills（技能）

- **本质**：Markdown 文件
- **类比**：维修自行车的说明书 —— 你不必记住所有内容，需要用的时候拿出来读就行
- **上下文高效**：Agent 不需要把所有指令装在工作记忆里，只有 description 被加载，调用时才读完整内容
- **用途**：
  - 工作流和约定（"做代码审查时一定要检查这些项"）
  - 参考资料
  - 可复用的 prompt（用 skill name 触发）

### MCP Servers

- **本质**：运行中的进程，对外暴露工具
- **特点**：定制化的工具集合、开放标准、安全

| 维度 | Skills | MCP Servers |
|------|--------|-------------|
| 格式 | Markdown 文件 | 运行中的服务进程 |
| 作用 | 教 Agent 怎么做 | 给 Agent 能用什么 |
| 加载方式 | 按需加载（描述先加载） | 连接到工具端点 |
| 上下文压力 | 小（懒加载） | 取决于工具数量 |

---

## 三、何时用 Claude Agent SDK vs Anthropic API

| SDK | API |
|-----|-----|
| 自动化 Claude Code 任务 | 简单 App 或单轮任务 |
| 多 Agent 工作流 | 非 Agent 场景 |
| 需要 Agent 循环 | 直接调 LLM |

> 当然，你也可以只用 API 从头构建 Agent（Matt 也做过），是个有趣的学习项目。但他提供了**模板**可以一键 Remix。

---

## 四、Replit 模板结构详解

Matt 提供了个人模板，结构如下：

### `.agents/` 目录

包含 `skills/` 文件夹，里面是 Replit Agent 在构建时使用的 Skills：

1. **Claude Agent SDK Skill** — 教 Replit Agent 如何构建 Claude Agent SDK 应用
2. **工具查找能力** — 让 Agent 知道去哪里找构建所需的资源

### `src/` 源文件目录

Matt 推荐的框架结构（不是必须的，但能带来结构化项目）：
- `agents/` — Agent 定义（近乎英文的自然语言）
- `mcp-servers/` — MCP 服务器定义
- `skills/` — Markdown 文档（同 Replit Agent 可用的 Skills）
- `permissions/` — 权限配置
- `utilities/` — 工具函数

示例 Agent 定义几乎像在写英语，不像代码。

### Skills 与 Agent 共享

> Replit Agent 能用 Skills，你自己构建的 Claude Agent SDK Agent 也能用 Skills。同一个 Skills 文件夹同时服务两者。

---

## 五、实战：构建 Todoist Agent

### 第一步：Remix 模板

1. 打开 Matt 的 Claude Agent SDK 模板（链接在视频描述）
2. 点击 Remix → 创建副本（命名为 "matt's todoist"）
3. 确保显示隐藏文件（Show Hidden Files）

### 第二步：编写 Prompt（Plan Mode）

最佳实践 → 先切到 **Plan Mode**：

```
Use the Claude Agent SDK skill to build an agent that looks at my Todoist inbox
and organizes my tasks by applying relevant labels and supporting information.
Create tools that allow our agent to interact with Todoist using the SDK.
The result should be an agent that when triggered, loads all tasks and available projects,
polishes them, then organizes them appropriately.
Be sure to use the Replit integrations for easier authentication.
```

### 第三步：配置 Integrations

在 `replit.com/integrations` 授权 Todoist 账号。这样 Agent 就能访问 Todoist API 构建工具。

> ⚠️ Todoist 有一个官方 MCP Server，但用的是 OAuth2 认证，复杂。Matt 使用 **Replit Integrations + Todoist API** 更简单。

### 第四步：Debug 与迭代

**遇到的问题和解决方式：**

1. **Agent 使用了错误的 MCP Server**（OAuth2 的 Todoist MCP）
   - 修正：明确告诉 Agent "用我们的 Agent 结构和文件系统，但用**自定义工具**对接 Todoist API，通过 Integrations 认证"

2. **Inbox 检测用了错误的属性名**
   - Orchestrator Agent 自己发现了 bug：`prong` 属性名不对 → 自动修复

3. **Agent 没有把任务移出 Inbox**
   - 原因：prompt 不够精确
   - 修正：补充 "fetch a list of projects and assign a relevant project to each item"

### 第五步：验证结果

Agent 运行成功：
- 修改了任务标题
- 添加了标签（如 "computer"、"next"）
- 任务移出了 Inbox

### 第六步：部署（Schedule）

```
Agent 会引导你完成发布流程。
发布为定时任务 → 每天自动运行 → 自动整理 Todoist。
```

---

## 六、关键教训

1. **Prompt 要精确**：提供更多上下文、更多细节。Matt 说 "thus" 这种他平时不会用的词都出来了——说明用 AI 构建时真的要很精确
2. **了解框架再构建**：先理解 Claude Agent SDK 的原语（Agent、MCP、Skill、Tool），再让 AI 在此基础上构建
3. **为 AI 建立结构**：先搭好脚手架（项目结构），AI 就能产出更干净的项目
4. **调试是常态**："bumped into some rough edges, and we figured stuff out. That's part of vibe coding."
5. **Replit 的优势**：所有原语开箱即用（文件存储、数据库、Auth、Secret 管理）

---

## 七、视频中使用的技术栈

| 组件 | 用途 |
|------|------|
| Claude Agent SDK | Agent 运行时和编排 |
| Replit | 开发、部署、托管 |
| Replit Integrations | 服务认证（Todoist API） |
| Todoist API | 任务管理 |
| Anthropic API Key | 存在 Replit Secrets Vault 中 |
| Skills（Markdown） | 教 Replit Agent 和 SDK Agent |

---

## 八、可扩展方向

视频中没有演示但有潜力的方向：
- **使用数据库**：让 Agent 有持久状态
- **多 Agent 层级**：更复杂的编排（如视频中的部署 Agent）
- **更多服务集成**：用同样的 Integrations 模式对接各种 API

---

> 完整原始转录：`claude-agent-sdk-transcript-combined.txt`（22KB，Whisper 直接输出）
