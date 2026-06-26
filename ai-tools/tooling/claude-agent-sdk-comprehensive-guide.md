# Claude Agent SDK 全面上手指南

> **版本**：v1.0 | **更新日期**：2026-06-26 | **适用版本**：Claude Agent SDK v0.1.48+ (Python) / v0.2.71+ (TypeScript)
>
> 本文综合整理自官方文档、社区教程和最佳实践，目标是为开发者提供一份 **循序渐进、全面MECE、有深度、包含最佳实践** 的 Claude Agent SDK 入门到进阶指南。

---

## 目录

1. [概述：什么是 Claude Agent SDK](#1-概述什么是-claude-agent-sdk)
2. [快速开始：5 分钟 Hello World](#2-快速开始5-分钟-hello-world)
3. [核心概念深度解析](#3-核心概念深度解析)
4. [工具系统（Tool System）](#4-工具系统tool-system)
5. [子代理与多 Agent 编排](#5-子代理与多-agent-编排)
6. [Hooks 生命周期钩子](#6-hooks-生命周期钩子)
7. [会话管理与上下文控制](#7-会话管理与上下文控制)
8. [MCP 集成详解](#8-mcp-集成详解)
9. [生产部署与运营](#9-生产部署与运营)
10. [实战项目](#10-实战项目)
11. [常见问题与故障排查](#11-常见问题与故障排查)
12. [最佳实践与设计模式](#12-最佳实践与设计模式)
13. [生态与进阶资源](#13-生态与进阶资源)

---

## 1. 概述：什么是 Claude Agent SDK

### 1.1 一句话定义

**Claude Agent SDK 是 Anthropic 官方提供的编程接口**，让你能够在自己的 Python 或 TypeScript 程序中使用 Claude Code 的全部核心能力——包括 Agent Loop（代理循环）、内置工具集、上下文管理和多 Agent 协作——而不是在终端里人工交互。

### 1.2 为什么需要 Agent SDK？

使用 Anthropic 原生 API（`anthropic` Python 包 / `@anthropic-ai/sdk`）构建 Agent 时，你需要**手动管理工具调用循环**：

```python
# 原生 API 模式：你需要自己管理循环
response = client.messages.create(model="claude-sonnet-4-6", tools=[...], messages=[...])
while response.stop_reason == "tool_use":
    # 手动解析 tool_use block
    # 手动执行工具
    # 手动把结果塞回消息列表
    # 再次调用 API
    response = client.messages.create(model="claude-sonnet-4-6", tools=[...], messages=messages)
```

**Agent SDK 替你完成了这个循环**：

```python
# Agent SDK 模式：SDK 自动管理工具循环
async for message in query(prompt="修复 auth.py 中的 bug", options=options):
    # Claude 自动读取文件、发现 bug、编辑代码
    # 你只需要处理流式消息
```

这听起来只是少写了几行代码，但在生产环境中差别巨大——SDK 内置了权限控制、审计日志、会话恢复、子代理并行等企业级功能。

### 1.3 SDK vs CLI：何时用哪个？

```
                    Claude 代理核心能力
                          │
          ┌───────────────┴───────────────┐
          │                               │
    Claude Code CLI                 Claude Agent SDK
    （命令行工具）                    （编程接口）
          │                               │
    ┌─────┴─────┐                 ┌───────┴───────┐
    │           │                 │               │
  人工交互   Shell 脚本          Python 程序    TypeScript 程序
```

| 维度 | Claude Code CLI | Claude Agent SDK |
|------|----------------|------------------|
| **使用方式** | 终端交互式命令 | 代码中调用 `query()` |
| **适合场景** | 日常开发、快速原型 | 自动化流水线、批量处理、系统集成 |
| **交互方式** | 人工对话 | 程序化控制 |
| **并发能力** | 单会话 | 多 Agent 并行 |
| **定制程度** | 配置文件（.claude/） | 完全可编程 |
| **学习曲线** | 低 | 中（需编程基础） |
| **审计能力** | 基本日志 | Hook 机制 + 结构化审计 |

**何时用 SDK**：自动化 CI/CD 流水线、批量代码审查、多 Agent 协作系统、长时间运行的后台任务、需要审计日志的生产环境。

**何时用 CLI**：日常交互式开发、临时任务、学习探索。

### 1.4 支持的语言与安装

| 语言 | 包名 | 安装命令 | 最低版本 |
|------|------|---------|---------|
| **Python** | `claude-agent-sdk` | `pip install claude-agent-sdk` | Python 3.10+ |
| **TypeScript/JavaScript** | `@anthropic-ai/claude-agent-sdk` | `npm install @anthropic-ai/claude-agent-sdk` | Node.js 18+ |

> ⚠️ **版本演进**：SDK 早期叫「Claude Code SDK」，包的导入路径是 `claude_code_sdk` / `@anthropic-ai/claude-code`。2025 年底统一更名为 `claude-agent-sdk`。如果你看到旧文档中的 `ClaudeCodeOptions`，那就是现在的 `ClaudeAgentOptions`。

### 1.5 支持的 Backend Provider

除了 Anthropic 原生 API，SDK 还支持以下云平台作为后端：

| 平台 | 环境变量 |
|------|---------|
| **Amazon Bedrock** | `CLAUDE_CODE_USE_BEDROCK=1` + AWS 凭证 |
| **Google Vertex AI** | `CLAUDE_CODE_USE_VERTEX=1` + GCP 凭证 |
| **Microsoft Azure AI Foundry** | `CLAUDE_CODE_USE_FOUNDRY=1` + Azure 凭证 |

---

## 2. 快速开始：5 分钟 Hello World

### 2.1 环境准备

```bash
# 检查环境
node --version   # 需要 v18.0.0+
python --version # 需要 3.10+
```

### 2.2 安装 SDK

```bash
# Python
python -m venv venv && source venv/bin/activate
pip install claude-agent-sdk

# TypeScript
npm init -y
npm install @anthropic-ai/claude-agent-sdk
```

### 2.3 配置 API 密钥

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

或在项目中创建 `.env` 文件：

```env
ANTHROPIC_API_KEY=sk-ant-...
```

### 2.4 Hello World Agent

**Python 版**（`hello_agent.py`）：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="你好！请用一句话介绍你能做什么？",
        options=ClaudeAgentOptions(
            model="claude-sonnet-4-6"
        )
    ):
        if message.type == "assistant":
            for block in message.content:
                if block.type == "text":
                    print(block.text, end="", flush=True)

    print()

asyncio.run(main())
```

**TypeScript 版**（`hello_agent.ts`）：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

async function main() {
  for await (const message of query({
    prompt: "你好！请用一句话介绍你能做什么？",
    options: {
      model: "claude-sonnet-4-6"
    }
  })) {
    if (message.type === "assistant") {
      for (const block of message.message.content) {
        if ("text" in block) {
          process.stdout.write(block.text);
        }
      }
    }
  }
  console.log();
}

main().catch(console.error);
```

### 2.5 验证安装

运行后如果看到 Claude 的回复，说明安装成功。

### 2.6 ⚠️ 版本锁定建议

SDK 的版本迭代非常快（Python 包从 2025 年底至今已迭代数十个版本）。生产环境中**务必锁定版本**：

```bash
# Python requirements.txt
claude-agent-sdk==0.1.48

# TypeScript package.json
"@anthropic-ai/claude-agent-sdk": "0.2.71"
```

同时建议定期关注 [GitHub Releases](https://github.com/anthropics/claude-agent-sdk-typescript/releases) 以获取新特性及破坏性变更通知。

---

## 3. 核心概念深度解析

### 3.1 `query()` 函数：SDK 的心脏

`query()` 是 Agent SDK 的核心入口函数，返回一个**异步可迭代对象**，持续产生流式消息直到 Agent 完成任务。

**Python 签名**：

```python
async def query(
    prompt: str | AsyncIterable[SDKUserMessage],
    options: Optional[ClaudeAgentOptions] = None
) -> AsyncIterator[SDKMessage]:
```

**TypeScript 签名**：

```typescript
function query(params: {
  prompt: string | AsyncIterable<SDKUserMessage>;
  options?: Options;
}): Query;
```

### 3.2 消息类型（Message Types）

理解消息类型是正确处理 Agent 响应的关键。SDK 在 Agent 执行过程中会产生以下消息：

| 消息类型 | Python 类型 | TypeScript `type` 字段 | 含义 |
|---------|-----------|----------------------|------|
| **系统消息** | `SystemMessage` | `"system"` | 会话初始化信息，含 session_id |
| **助手消息** | `AssistantMessage` | `"assistant"` | Claude 的文本回复或工具调用请求 |
| **结果消息** | `ResultMessage` | `"result"` | 最终执行结果，含 cost 统计 |
| **用户消息** | `UserMessage` | - | 用户输入（较少直接处理） |

**标准消息处理模式**：

```typescript
for await (const message of query({ prompt: "...", options })) {
  switch (message.type) {
    case "system":
      if (message.subtype === "init") {
        console.log("Session ID:", message.session_id);
        console.log("Available tools:", message.tools);
      }
      break;

    case "assistant":
      for (const block of message.message.content) {
        if ("text" in block) {
          // Claude 的文字回复
          console.log("Claude:", block.text);
        } else if ("name" in block) {
          // 工具调用
          console.log("Tool call:", block.name);
        }
      }
      break;

    case "result":
      if (message.subtype === "success") {
        console.log("Cost: $", message.total_cost_usd);
        console.log("Token usage:", message.usage);
      }
      break;
  }
}
```

### 3.3 ClaudeAgentOptions 完整配置

`ClaudeAgentOptions` 是配置 Agent 行为的核心对象，涵盖以下能力域：

#### 模型与服务

| 参数 | 类型 | 说明 |
|------|------|------|
| `model` | str | 模型选择：`sonnet`/`opus`/`haiku` 或完整 ID |
| `max_turns` / `maxTurns` | int | 最大迭代轮次，防止失控循环（默认 50-250） |
| `system_prompt` / `systemPrompt` | str | 系统提示词，定义 Agent 角色和行为 |

> **关于采样参数**：Agent SDK 当前**不直接暴露** temperature、top_p、top_k 等底层采样参数。这些由 SDK 内部管理以保持 Agent 行为的一致性和稳定性。如果你需要在不同场景下控制输出的确定性与创造性，应通过 `system_prompt` 中的指令间接影响（如

#### 工具控制

| 参数 | 说明 |
|------|------|
| `allowed_tools` / `allowedTools` | 工具白名单（字符串数组）；`None` 表示允许所有内置工具 |
| `permission_mode` / `permissionMode` | 权限模式：`default` / `acceptEdits` / `bypassPermissions` / `plan` |

#### 子代理与 MCP

| 参数 | 说明 |
|------|------|
| `agents` | 子代理定义字典（`Dict[str, AgentDefinition]`） |
| `mcp_servers` / `mcpServers` | MCP 服务器配置 |

#### 生命周期 🎣

| 参数 | 说明 |
|------|------|
| `hooks` | Hook 回调函数配置（详见第6章） |
| `resume` | 会话恢复 ID，实现跨 `query()` 调用的上下文延续 |

#### 其他设置

| 参数 | 说明 |
|------|------|
| `cwd` | 工作目录路径 |
| `setting_sources` / `settingSources` | 从项目配置文件读取设置：`["project"]` 启用 `CLAUDE.md`、`.claude/commands/`、`.claude/skills/` |
| `output_format` / `outputFormat` | 结构化输出格式，如 `{"type": "json_schema", "schema": {...}}` |
| `api_key` / `apiKey` | API 密钥（通常通过环境变量注入） |

### 3.4 Agent Loop：代理工作循环

Agent 不是简单的"单次问答"，而是遵循一个完整的**思考-行动-验证循环**：

```
┌─────────────────────────────────────────────────────────┐
│                  Agent Loop（代理循环）                     │
│                                                          │
│   ┌──────────┐    ┌──────────┐    ┌──────────────┐     │
│   │ 接收任务  │ →  │  理解分析  │ →  │  决定下一步   │     │
│   └──────────┘    └──────────┘    └──────┬───────┘     │
│                                          │             │
│                              ┌───────────┴───────────┐ │
│                              │   需要使用工具吗？       │ │
│                              └───────────┬───────────┘ │
│                                          │             │
│                              是 ┌────────┴────────┐ 否 │
│                                ▼                  ▼    │
│   ┌──────────┐    ┌──────────┐         ┌──────────┐   │
│   │ 验证结果  │ ←  │ 执行工具  │         │ 直接回复  │   │
│   └────┬─────┘    └──────────┘         └──────────┘   │
│        │                                               │
│        ▼                                               │
│   ┌──────────┐                                         │
│   │ 任务完成？│                                         │
│   └────┬─────┘                                         │
│        │                                               │
│     否 │    ┌──────────────────┐                       │
│        └───→│  继续下一轮循环   │────→ 回到"理解分析"    │
│             └──────────────────┘                       │
│        是 ▼                                            │
│   ┌──────────┐                                         │
│   │ 返回结果  │                                         │
│   └──────────┘                                         │
└─────────────────────────────────────────────────────────┘
```

**实际示例**：让 Agent "创建一个 Python 计算器并测试"。

| 轮次 | Agent 行为 | 工具调用 | 分析 |
|------|-----------|---------|------|
| 1 | 理解需求，决定创建文件 | `Write("calculator.py")` | 创建代码文件 |
| 2 | 创建后决定验证 | `Bash("python calculator.py")` | 运行测试 |
| 3 | 发现错误，决定修复 | `Read → Edit` | 修正 bug |
| 4 | 再次验证 | `Bash("python calculator.py")` | 确认运行正常 |
| 5 | 任务完成 | 直接回复 | 返回最终结果 |

`max_turns` 参数控制最大轮次，防止 Agent 陷入无限循环：

```python
# 简单任务：设小一点节省 token
options = ClaudeAgentOptions(max_turns=10)

# 复杂任务：给 Agent 足够的空间
options = ClaudeAgentOptions(max_turns=50)
```

### 3.5 流式 vs 结式：两种结果获取模式

`query()` 默认返回异步**流式（streaming）** 迭代器，但你可以在两种模式之间切换：

| 模式 | 获取方式 | 特点 |
|------|---------|------|
| **流式（Streaming）** | `async for message in query(...)` | 实时看到 Agent 的思考过程、工具调用和中间结果 |
| **结式（Result）** | 监听 `type == "result"` 的消息 | 只关心最终结果和成本统计，适合程序化自动处理 |

```python
# 场景 A：流式处理——实时打印 Agent 输出
async for message in query(prompt="...", options=options):
    if message.type == "assistant":
        for block in message.content:
            if block.type == "text":
                print(block.text, end="", flush=True)  # 实时打印

# 场景 B：只取最终结果——程序化消费
final_result = ""
last_cost = 0
async for message in query(prompt="...", options=options):
    if message.type == "result" and message.subtype == "success":
        final_result = message.result_text  # 完整文本结果
        last_cost = message.total_cost_usd  # 成本统计
```

> **设计建议**：开发调试阶段用流式模式观察 Agent 行为；生产自动化流水线中用结式模式处理最终结果。

### 3.6 `ClaudeSDKClient`：另一套编程接口

除了直接调用 `query()`，SDK 还提供了 `ClaudeSDKClient` 类，适用于**多轮交互式**场景：

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async with ClaudeSDKClient(options=ClaudeAgentOptions(model="sonnet")) as client:
    await client.query("第一轮：分析代码库")
    async for message in client.receive_response():
        # 处理回复...

    await client.query("第二轮：基于前面结果继续")
    async for message in client.receive_response():
        # 第二轮消息...
```

**`ClaudeSDKClient` vs `query()`**：

| 接口 | 适用场景 | 状态管理 |
|------|---------|---------|
| `query()` | 一次性任务、自动化流水线 | 每次调用独立；通过 `resume` 参数恢复 |
| `ClaudeSDKClient` | 多轮交互、对话式应用 | 内部维护会话上下文 |

> 项目中 10.4 节的交互式 Agent 使用了 `ClaudeSDKClient`。

---

## 4. 工具系统（Tool System）

工具是 Agent 能够"做事情"的关键。没有工具，Agent 只能"说话"不能"干活"。

### 4.1 内置工具清单

SDK 内置了一套完整的开发工具，Agent 可以直接使用：

| 工具名 | Python 名 | TypeScript 名 | 功能 | 适用场景 |
|--------|----------|--------------|------|---------|
| **Read** | `Read` | `Read` | 读取文件内容 | 分析代码、读取配置 |
| **Write** | `Write` | `Write` | 写入新文件 | 创建代码/文档 |
| **Edit** | `Edit` | `Edit` | 精确编辑文件 | 修改已有代码 |
| **Bash** | `Bash` | `Bash` | 执行终端命令 | 运行脚本、安装依赖、git 操作 |
| **Glob** | `Glob` | `Glob` | 文件名模式匹配 | 查找特定类型文件 |
| **Grep** | `Grep` | `Grep` | 文件内容搜索 | 在代码库中搜索关键词 |
| **Agent** | `Agent` | `Agent` | 子代理工具 | 启动子代理并行处理 |
| **WebSearch** | `WebSearch` | `WebSearch` | 网络搜索 | 查找最新信息 |
| **WebFetch** | `WebFetch` | `WebFetch` | 抓取网页 | 获取网页内容 |
| **AskUserQuestion** | `AskUserQuestion` | - | 询问用户 | 需要人工干预时 |

### 4.2 工具权限控制

#### 白名单模式

```python
# 只读模式：只能读取和搜索，禁止修改
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob", "Grep"]
)

# 全部开放（默认）
options = ClaudeAgentOptions(
    allowed_tools=None  # 所有内置工具
)
```

#### Permission Mode（权限模式）

| 模式 | Python | TypeScript | 行为 |
|------|--------|-----------|------|
| 默认 | `default` | `default` | 每个工具执行前都请求确认 |
| 接受编辑 | `acceptEdits` | `acceptEdits` | 自动接受文件编辑操作 |
| 绕过权限 | `bypassPermissions` | `bypassPermissions` | **不请求任何确认**（仅隔离环境使用） |
| 计划模式 | `plan` | `plan` | 只读分析模式 |

#### 细粒度权限控制（TypeScript）

```typescript
options = {
  canUseTool: async (toolName, input) => {
    // 允许所有读取操作
    if (["Read", "Glob", "Grep"].includes(toolName)) {
      return { behavior: "allow", updatedInput: input };
    }

    // 阻止修改敏感文件
    if (toolName === "Write" && input.file_path?.includes(".env")) {
      return { behavior: "deny", message: "不能修改 .env 文件" };
    }

    // 默认允许
    return { behavior: "allow", updatedInput: input };
  }
}
```

### 4.3 自定义工具（SDK MCP Server）

Agent SDK 的一大优势是**可以用 Python/TypeScript 函数直接定义自定义工具**，无需单独启动 MCP 服务器进程。

**Python 版**：

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("get_weather", "获取指定城市的实时天气", {"city": str})
async def get_weather(args):
    city = args["city"]
    # 调用天气 API...
    return {
        "content": [{"type": "text", "text": f"{city} 当前温度 22°C，晴"}]
    }

@tool("calculate", "执行数学表达式计算", {"expression": str})
async def calculate(args):
    try:
        result = eval(args["expression"])  # 注意：生产环境需做安全检查
        return {"content": [{"type": "text", "text": f"结果：{result}"}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"错误：{str(e)}"}]}

# 创建 MCP 服务器
my_tools = create_sdk_mcp_server(
    name="my-utils",
    version="1.0.0",
    tools=[get_weather, calculate]
)

# 在 Agent 中使用
options = ClaudeAgentOptions(
    mcp_servers={"utils": my_tools},
    allowed_tools=[
        "mcp__utils__get_weather",
        "mcp__utils__calculate"
    ]
)
```

**TypeScript 版**：

```typescript
import { tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

const customServer = createSdkMcpServer({
  name: "code-metrics",
  version: "1.0.0",
  tools: [
    tool(
      "analyze_complexity",
      "计算文件的圈复杂度",
      {
        filePath: z.string().describe("要分析的文件路径")
      },
      async (args) => {
        // 实际实现中计算真实的圈复杂度
        return {
          content: [{
            type: "text",
            text: `圈复杂度分析结果: ${args.filePath}`
          }]
        };
      }
    )
  ]
});
```

### 4.4 工具命名规范

- **内置工具**：直接使用名称，如 `"Read"`, `"Bash"`
- **MCP 工具**：格式为 `mcp__<server-name>__<tool-name>`，如 `mcp__utils__get_weather`
- **子代理工具**：需要在 `allowed_tools` 中包含 `"Agent"` 才能启用

---

## 5. 子代理与多 Agent 编排

当任务规模超出单个 Agent 的能力时，**子代理（Subagent）** 是性能的倍增器。

### 5.1 为什么需要子代理？

```
传统方式（串行处理）：
  Agent 顺序处理 A、B、C 三个模块
  总耗时 = A + B + C（单个上下文窗口限制）

子代理方式（并行处理）：
  主 Agent 分配任务
    ├─ 子 Agent A: 模块 A （独立上下文）
    ├─ 子 Agent B: 模块 B （独立上下文）
    └─ 子 Agent C: 模块 C （独立上下文）
  总耗时 ≈ max(A, B, C)（并行加速）
```

**核心优势**：

| 优势 | 说明 |
|------|------|
| **独立上下文** | 每个子代理拥有独立的 200K 上下文窗口 |
| **并行执行** | 最多 10 个子代理同时运行 |
| **失败隔离** | 单个子代理失败不影响其他子代理 |
| **专业分工** | 每个子代理有独立的系统提示词和可用工具 |
| **成本优化** | 简单任务可以用 Haiku，复杂任务用 Sonnet/Opus |

### 5.2 AgentDefinition 配置

```python
from claude_agent_sdk import AgentDefinition

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "Glob", "Edit", "Write", "Agent"],
    agents={
        "security-reviewer": AgentDefinition(
            description="安全专家，擅长检测漏洞",
            prompt="""你是安全审查专家。重点关注：
- SQL 注入、XSS、CSRF 漏洞
- 暴露的凭证和密钥
- 不安全的数制处理
- 认证/授权问题""",
            tools=["Read", "Grep", "Glob"],
            model="sonnet",
        ),
        "test-analyzer": AgentDefinition(
            description="测试覆盖率和质量分析",
            prompt="你是测试专家。分析测试覆盖盲区、边界情况和质量。",
            tools=["Read", "Grep", "Glob"],
            model="haiku",  # 简单任务用更经济的模型
        ),
    },
    max_turns=50,
)
```

**AgentDefinition 核心字段**：

| 字段 | 说明 | 默认值 |
|------|------|-------|
| `description` | 告诉主 Agent 何时使用这个子代理 | 必填 |
| `prompt` | 子代理的系统提示词 | 选填 |
| `tools` | 可用工具；省略时继承父级 | 继承 |
| `model` | `sonnet` / `opus` / `haiku` / `inherit` | `inherit` |
| `background` | 是否作为后台非阻塞任务运行 | `false` |
| `maxTurns` | 子代理最大迭代轮次 | 继承父级 |
| `skills` | 注入的技能列表 | 选填 |

### 5.3 协作模式（Orchestration Patterns）

参考 Yeasy GitBook 中的四种协作模式：

#### 模式 1：流水线（Pipeline）

适用于有明确先后顺序的任务链。

```python
# 主 Agent prompt 中体现顺序依赖
prompt = """
第一步：让 parser 解析文档内容
第二步：把解析结果交给 analyzer 分析
第三步：根据分析结果生成报告
"""
```

#### 模式 2：扇出/扇入（Fan-out/Fan-in）

适用于多个独立子任务并行执行。

```python
prompt = """
请同时启动以下三个子代理并行工作：
1. api-reviewer → 审查 src/api/ 目录
2. model-reviewer → 审查 src/models/ 目录
3. ui-reviewer → 审查 src/views/ 目录
全部完成后汇总结果。
"""
```

#### 模式 3：条件分支（Conditional Routing）

根据内容性质路由到不同专家。

```python
prompt = """
分析变更文件的类型：
- 如果是安全相关文件，交给 security-reviewer
- 如果是测试文件，交给 test-analyzer
- 其他文件你自己处理
"""
```

#### 模式 4：迭代精炼（Iterative Refinement）

子代理生成草稿 → 另一个子代理评审 → 返回改进。

```python
prompt = """
1. 先 review 整个代码库，找到所有问题
2. 将结果交给 security-reviewer 做第二轮安全审计
3. 合并两轮结果生成最终报告
"""
```

### 5.4 子代理上下文注入

子代理获取上下文的三种方式：

1. **Skills 注入**：在 `AgentDefinition.skills` 中指定 Skill 名称，相关技能内容会被直接注入子代理的上下文
2. **Memory 持久化**：子代理可拥有持久记忆目录，跨会话积累知识
3. **工具访问控制**：通过 `tools` 精细控制子代理能力

> ⚠️ **约束**：子代理不能再创建子代理（只有一级嵌套）。最多同时运行 10 个并行子代理。

### 5.5 Skills 技能系统：模块化知识注入

Skills 是 Claude Code CLI 中定义在 `.claude/skills/` 目录下的模块化技能文件，Agent SDK 可以通过 `AgentDefinition.skills` 或 `setting_sources: ["project"]` 继承使用。

**Skill 文件结构**：

```
.claude/skills/
├── react-components.md    # React 组件开发规范
├── sql-optimization.md    # SQL 优化指南
├── security-checklist.md  # 安全审查清单
└── api-design.md          # API 设计规范
```

每个 Skill 文件是一个纯 Markdown 文件，内容在 Agent 启动时自动注入上下文：

```markdown
# SQL 优化技能

## 索引使用
- 为 JOIN 和 WHERE 中常用的列创建索引
- 避免在索引列上使用函数或类型转换

## 查询优化
- 使用 EXPLAIN 分析执行计划
- 避免 SELECT *，只选择需要的列
```

**在 SDK 中使用 Skills**：

```python
# 方式一：定义 AgentDefinition 时指定 skills
options = ClaudeAgentOptions(
    agents={
        "sql-expert": AgentDefinition(
            description="SQL 优化专家",
            skills=["sql-optimization"],  # 注入 SQL 优化技能
            model="sonnet",
        )
    },
    allowed_tools=["Read", "Write", "Bash", "Agent"],
)

# 方式二：从项目配置加载（读取 .claude/skills/）
options = ClaudeAgentOptions(
    setting_sources=["project"],  # 自动加载 .claude/skills/*.md
)
```

> **Skills 最佳实践**：将组织的最佳实践、安全规范、编码风格写成 Skill 文件，所有 Agent 自动继承。Skill 文件应短小精悍（1-2 页），聚焦单一领域知识。

---

## 6. Hooks 生命周期钩子

Hooks 让你在 Agent 执行的关键节点插入自定义逻辑——这是**生产级部署的关键能力**。

### 6.1 可用的 Hook 类型

| Hook | 触发时机 | 典型用途 |
|------|---------|---------|
| **PreToolUse** | 每个工具执行前 | 验证输入、阻止危险命令、记录日志 |
| **PostToolUse** | 每个工具执行后 | 记录输出、触发后续流程、累积指标 |
| **Stop** | Agent 停止时 | 清理资源、生成汇总报告 |
| **SessionStart** | 新会话开始时 | 加载状态、初始化连接 |
| **SessionEnd** | 会话结束时 | 持久化状态、断开连接 |
| **UserPromptSubmit** | 用户提交 prompt 时 | 拦截和增强用户输入 |
| **PreCompact** | 上下文压缩前 | 保存关键信息到外部存储，防止压缩过程丢失重要上下文 |

### 6.2 Hook 完整示例（Python）

```python
import json
from datetime import datetime
from claude_agent_sdk import (
    query, ClaudeAgentOptions, HookMatcher
)

AUDIT_LOG = "./audit.log"
BLOCKED_PATTERNS = ["rm -rf", "sudo", "chmod 777", "git push --force"]

async def pre_tool_hook(input_data, tool_use_id, context):
    """工具执行前的验证和审计"""
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Bash 命令安全检查
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        for pattern in BLOCKED_PATTERNS:
            if pattern in command:
                _log("BLOCKED", tool_name, f"命令包含禁止模式: {pattern}")
                return {
                    "decision": "block",
                    "reason": f"危险命令已被阻止: {pattern}"
                }

    _log("APPROVED", tool_name, str(tool_input)[:200])
    return {}  # 返回空字典表示允许执行

async def post_tool_hook(input_data, tool_use_id, context):
    """工具执行后记录结果"""
    _log("COMPLETED", input_data.get("tool_name", ""), "执行完成")
    return {}

def _log(action, tool_name, detail):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "tool": tool_name,
        "detail": detail,
    }
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

# 使用 Hook
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Edit", "Bash", "Glob"],
    permission_mode="acceptEdits",
    hooks={
        "PreToolUse": [
            # 无 matcher = 对所有工具生效
            HookMatcher(matcher=".*", hooks=[pre_tool_hook])
        ],
        "PostToolUse": [
            # 只对 Edit 和 Write 生效
            HookMatcher(matcher="Edit|Write", hooks=[post_tool_hook])
        ],
    }
)
```

### 6.3 Hook 示例（TypeScript）

```typescript
import { query, HookCallback, PreToolUseHookInput } from "@anthropic-ai/claude-agent-sdk";

const auditLogger: HookCallback = async (input, toolUseId, context) => {
  if (input.hook_event_name === "PreToolUse") {
    const preInput = input as PreToolUseHookInput;
    console.log(`[AUDIT] ${new Date().toISOString()} - ${preInput.tool_name}`);
  }
  return {};
};

const blockDangerousCommands: HookCallback = async (input, toolUseId, context) => {
  if (input.hook_event_name === "PreToolUse") {
    const preInput = input as PreToolUseHookInput;
    if (preInput.tool_name === "Bash") {
      const command = (preInput.tool_input as any).command || "";
      if (command.includes("rm -rf") || command.includes("sudo")) {
        return {
          hookSpecificOutput: {
            hookEventName: "PreToolUse",
            permissionDecision: "deny",
            permissionDecisionReason: "危险命令已阻止"
          }
        };
      }
    }
  }
  return {};
};

// 使用 Hook
const options = {
  hooks: {
    PreToolUse: [
      { hooks: [auditLogger] },
      { matcher: "Bash", hooks: [blockDangerousCommands] }
    ]
  }
};
```

---

## 7. 会话管理与上下文控制

### 7.1 Session Resume：跨轮对话

对于多轮交互场景，SDK 支持**会话恢复**——让 Agent 在后续调用中保持之前的上下文。

**获取 Session ID**：

```python
session_id = None
async for message in query(prompt="分析代码库结构...", options=options):
    if hasattr(message, "subtype") and message.subtype == "init":
        session_id = message.data.get("session_id")
        print(f"Session: {session_id}")
```

**恢复会话**：

```python
# 第一轮：分析
async for message in query(
    prompt="分析 src/auth.py 的完整代码",
    options=ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep"])
):
    pass  # 处理消息...

# 第二轮：基于前一轮上下文继续
async for message in query(
    prompt="找出所有调用这个模块的地方",
    options=ClaudeAgentOptions(
        resume=session_id,  # 恢复上下文
        allowed_tools=["Read", "Glob", "Grep"]
    )
):
    # Claude 已经知道 auth.py 的内容，无需重新读取
    pass
```

### 7.2 上下文管理策略

Agent 的上下文窗口是有限的（200K tokens），长时间运行的 Agent 需要有效的上下文管理。

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| **Compaction（压缩）** | SDK 自动压缩历史对话，保留关键信息 | 长时间运行任务 |
| **子代理隔离** | 每个子代理独立上下文，只返回结果给父级 | 大型代码库分析 |
| **文件系统索引** | Agent 用 grep/tail 等智能加载文件部分，而非全量加载 | 日志分析、大数据处理 |
| **外部存储** | 通过自定义工具持久化中间结果到数据库 | 跨会话长期任务 |

---

## 8. MCP 集成详解

### 8.1 什么是 MCP？

**Model Context Protocol（MCP）** 是 Anthropic 推出的标准化工具协议，让 Claude Agent 能够连接外部工具和服务——相当于 AI 世界的 USB 标准。

### 8.2 SDK 内置 MCP vs 外部 MCP

| 特性 | SDK 内置 MCP Server | 外部 MCP Server |
|------|--------------------|----------------|
| **运行方式** | 在同一进程内运行 | 独立子进程 |
| **性能** | 更快（无 IPC 开销） | 略慢 |
| **部署** | 简单（单进程） | 需管理多进程 |
| **调试** | 更容易 | 需分别调试 |
| **适用场景** | 简单自定义工具 | 复杂工具、已有 MCP 生态 |

### 8.3 配置外部 MCP 服务器

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@anthropic/mcp-server-filesystem", "/allowed/path"]
        },
        "database": {
            "command": "npx",
            "args": ["-y", "@anthropic/mcp-server-sqlite", "./app.db"]
        },
        "github": {
            "command": "python",
            "args": ["-m", "github_mcp_server"],
            "env": {"GITHUB_TOKEN": "ghp_xxx"}
        }
    },
    allowed_tools=[
        "mcp__filesystem__read",
        "mcp__database__query",
        "mcp__github__create_pr"
    ]
)
```

### 8.4 MCP 工具命名

SDK 中的 MCP 工具遵循命名规范：`mcp__<server-name>__<tool-name>`。

例如，配置了 `"database"` 服务器，该服务器提供了 `query` 工具，则在 `allowed_tools` 中写作：
`"mcp__database__query"`。

### 8.5 MCP 传输层：stdio vs HTTP/SSE

MCP 服务器可以通过两种传输协议与 SDK 通信：

| 传输方式 | 启动方式 | 适用场景 | 示例 |
|---------|---------|---------|------|
| **stdio** | 子进程标准输入输出 | 本地工具、CLI 集成 | `{"command": "npx", "args": ["-y", "mcp-server"]}` |
| **HTTP/SSE** | HTTP 服务端点 | 远程服务、已有 API、多客户端共享 | 通过 HTTP URL 连接 |

**stdio（默认）**：SDK 自动启动 MCP 服务器子进程，通过 stdin/stdout 通信。部署简单，无需额外网络配置，适合本地工具和 CLI 集成。

**HTTP/SSE（Server-Sent Events）**：MCP 服务器作为独立 HTTP 服务运行，通过 SSE 推送事件。适合以下场景：

- 远程团队共享同一个 MCP 工具服务
- 已有 REST API 需要包装为 MCP 工具
- 容器化/云部署时解耦 SDK 与 MCP 进程

```python
# stdio 模式（默认）
options = ClaudeAgentOptions(
    mcp_servers={
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@anthropic/mcp-server-filesystem", "/allowed/path"]
        }
    }
)

# HTTP/SSE 模式（连接到远程 MCP 服务器）
options = ClaudeAgentOptions(
    mcp_servers={
        "remote-db": {
            "url": "https://mcp.mycompany.com/database",
            "headers": {"Authorization": "Bearer token123"}
        }
    }
)
```

### 8.6 MCP 调试与验证

开发 MCP 服务器时，可以使用以下工具调试和验证：

| 工具 | 用途 | 安装 |
|------|------|------|
| **MCP Inspector** | 官方调试 GUI，查看工具列表、输入输出、事件流 | `npx @anthropic/mcp-inspector` |
| **MCP CLI** | 命令行测试 MCP 服务器连接和工具调用 | `npx @anthropic/mcp-cli` |
| **日志输出** | SDK 的 Hook 机制可拦截 MCP 工具调用 | 编写 `PreToolUse` Hook |

**MCP Inspector 使用示例**：

```bash
# 启动 Inspector 连接到本地 MCP 服务器
npx @anthropic/mcp-inspector --command "python -m my_mcp_server"

# 打开浏览器访问 http://localhost:5173
# 在 GUI 中查看工具列表、测试调用、监控事件流
```

---

## 9. 生产部署与运营

### 9.1 错误处理

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def safe_query(prompt: str, options: ClaudeAgentOptions, retries: int = 3):
    """带重试和错误处理的查询"""
    last_error = None
    for attempt in range(retries):
        try:
            result_text = ""
            async for message in query(prompt=prompt, options=options):
                if message.type == "assistant":
                    for block in message.content:
                        if block.type == "text":
                            result_text += block.text
                elif message.type == "result":
                    if message.subtype == "success":
                        return {
                            "status": "success",
                            "text": result_text,
                            "cost": message.total_cost_usd
                        }
                    else:
                        return {
                            "status": "error",
                            "error": message.subtype,
                            "text": result_text
                        }
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                wait = 2 ** attempt
                print(f"Attempt {attempt + 1} failed, retrying in {wait}s...")
                await asyncio.sleep(wait)
            continue

    return {"status": "failed", "error": str(last_error)}
```

### 9.2 日志与监控

```python
import logging
from datetime import datetime

class AgentObserver:
    """Agent 执行观察者——记录每个关键事件"""

    def __init__(self):
        self.logger = logging.getLogger("agent_observer")
        self.events = []

    def on_tool_call(self, agent_id: str, tool_name: str, args: dict):
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "tool_call",
            "agent_id": agent_id,
            "tool": tool_name,
        }
        self.events.append(event)
        self.logger.info(f"Agent {agent_id} calling tool: {tool_name}")

    def on_agent_complete(self, agent_id: str, duration_ms: int, cost: float):
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "agent_complete",
            "agent_id": agent_id,
            "duration_ms": duration_ms,
            "cost_usd": cost,
        }
        self.events.append(event)

    def get_metrics(self) -> dict:
        """汇总性能指标"""
        tool_calls = sum(1 for e in self.events if e["type"] == "tool_call")
        completions = [e for e in self.events if e["type"] == "agent_complete"]
        avg_duration = (
            sum(e["duration_ms"] for e in completions) / len(completions)
            if completions else 0
        )
        total_cost = sum(e.get("cost_usd", 0) for e in completions)

        return {
            "total_tool_calls": tool_calls,
            "avg_duration_ms": avg_duration,
            "total_cost_usd": total_cost,
            "total_events": len(self.events),
        }
```

### 9.3 成本追踪

SDK 的 `result` 消息内置了成本统计：

```python
async for message in query(prompt="...", options=options):
    if message.type == "result" and message.subtype == "success":
        print(f"总成本: ${message.total_cost_usd:.4f}")
        print(f"Token 使用: {message.usage}")

        # 按模型细分（多子代理时）
        for model, usage in message.modelUsage.items():
            print(f"  {model}: ${usage.costUSD:.4f}")
```

### 9.4 安全最佳实践

> ⚠️ **这一节非常重要**——在生产环境部署 Agent 时，以下安全检查不可跳过。

1. **最小权限原则**：只给 Agent 完成工作所需的最少工具和权限
2. **命令白名单**：通过 Hook 阻止危险命令（`rm -rf`, `sudo`, `chmod 777` 等）
3. **路径隔离**：限制 Agent 只能访问特定目录
4. **文件大小限制**：防止 Agent 加载超大文件导致上下文溢出
5. **超时控制**：通过 `max_turns` 和工具执行超时防止失控
6. **审计日志**：所有工具调用都记录到不可篡改的日志
7. **结构化输出**：用 JSON Schema 约束 Agent 的输出格式

```python
# 生产级安全配置模板
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob", "Grep", "Edit", "Write", "Bash"],
    permission_mode="acceptEdits",
    max_turns=30,
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[security_hook]),
            HookMatcher(matcher=".*", hooks=[audit_hook]),
        ]
    }
)
```

---

## 10. 实战项目

### 10.1 项目一：代码审查 Agent（入门）

**目标**：自动分析指定文件的代码质量，发现 bug、安全问题和改进建议。

**Python 实现**：

```python
import asyncio
import sys
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions

async def analyze_code(file_path: str):
    path = Path(file_path)
    if not path.exists():
        print(f"文件不存在: {file_path}")
        return

    print(f"分析文件: {path.absolute()}")

    options = ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        allowed_tools=["Read", "Glob", "Grep"],
        max_turns=10,
        system_prompt="""你是一位资深代码审查专家。请分析代码并提供：
1. 代码概述（功能和结构）
2. 潜在问题（bug 风险、安全隐患）
3. 改进建议（可读性、性能、最佳实践）
请用中文回复，格式清晰。"""
    )

    async for message in query(
        prompt=f"请分析 {path.absolute()} 的代码质量",
        options=options
    ):
        if message.type == "assistant":
            for block in message.content:
                if block.type == "text":
                    print(block.text, end="", flush=True)

    print("\n分析完成！")

if __name__ == "__main__":
    asyncio.run(analyze_code(sys.argv[1]))
```

### 10.2 项目二：带结构化输出的审查 Agent（进阶）

使用 JSON Schema 约束输出格式，便于程序化处理：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const reviewSchema = {
  type: "object",
  properties: {
    issues: {
      type: "array",
      items: {
        type: "object",
        properties: {
          severity: { type: "string", enum: ["low", "medium", "high", "critical"] },
          category: { type: "string", enum: ["bug", "security", "performance", "style"] },
          file: { type: "string" },
          line: { type: "number" },
          description: { type: "string" },
          suggestion: { type: "string" }
        },
        required: ["severity", "category", "file", "description"]
      }
    },
    summary: { type: "string" },
    overallScore: { type: "number" }
  },
  required: ["issues", "summary", "overallScore"]
};

async function reviewCodeStructured(directory: string) {
  for await (const message of query({
    prompt: `审查 ${directory} 的代码，识别所有问题`,
    options: {
      model: "opus",
      allowedTools: ["Read", "Glob", "Grep"],
      permissionMode: "bypassPermissions",
      maxTurns: 250,
      outputFormat: {
        type: "json_schema",
        schema: reviewSchema
      }
    }
  })) {
    if (message.type === "result" && message.subtype === "success") {
      const review = message.structured_output;
      console.log(`分数: ${review.overallScore}/100`);
      console.log(`摘要: ${review.summary}`);
      for (const issue of review.issues) {
        console.log(`[${issue.severity}] ${issue.file}:${issue.line} - ${issue.description}`);
      }
    }
  }
}
```

### 10.3 项目三：CI/CD 集成 Agent（生产级）

完整的 PR 审查流水线：

```python
"""
CI/CD 代码审查 Agent — 可在 GitHub Actions / Jenkins 中调用
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from claude_agent_sdk import (
    query, ClaudeAgentOptions, HookMatcher
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("code_review")

REVIEW_PROMPT = """你是代码审查专家。

请审查以下变更文件，查找：
1. Bug 和逻辑错误
2. 安全漏洞
3. 性能问题
4. 代码风格和可维护性问题

对每个问题，提供：
- 严重级别（critical/high/medium/low）
- 问题描述
- 修复建议

最后生成 JSON 格式的审查报告。

CHANGED_FILES:
{changed_files}
"""

async def run_code_review(
    changed_files: List[str],
    max_turns: int = 30,
) -> Dict[str, Any]:
    audit_entries: List[Dict] = []
    start_time = datetime.now()

    async def audit_hook(input_data, tool_use_id, context):
        audit_entries.append({
            "ts": datetime.now().isoformat(),
            "tool": input_data.get("tool_name", "unknown"),
            "id": tool_use_id,
        })
        return {}

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep"],
        permission_mode="acceptEdits",
        model="claude-sonnet-4-6",
        max_turns=max_turns,
        hooks={
            "PreToolUse": [
                HookMatcher(matcher=".*", hooks=[audit_hook])
            ],
        },
    )

    prompt = REVIEW_PROMPT.format(changed_files="\n".join(changed_files))
    final_result = ""

    async for message in query(prompt=prompt, options=options):
        if message.type == "assistant":
            for block in message.content:
                if block.type == "text":
                    print(block.text, end="", flush=True)
                    final_result += block.text

    elapsed = (datetime.now() - start_time).total_seconds()
    return {
        "result": final_result,
        "elapsed_seconds": elapsed,
        "tool_calls": len(audit_entries),
    }

def get_changed_files() -> List[str]:
    """从 git diff 获取变更文件列表"""
    import subprocess
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        capture_output=True, text=True
    )
    files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    extensions = {".py", ".ts", ".js", ".go", ".rs", ".java"}
    return [f for f in files if Path(f).suffix in extensions]

def main():
    parser = argparse.ArgumentParser(description="CI/CD 代码审查 Agent")
    parser.add_argument("--files", nargs="+", help="指定审查的文件")
    parser.add_argument("--output", default="review-report.json")
    args = parser.parse_args()

    files = args.files or get_changed_files()
    if not files:
        print("没有变更文件需要审查")
        return

    import asyncio
    result = asyncio.run(run_code_review(files))

    with open(args.output, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n审查完成！报告已保存至: {args.output}")

if __name__ == "__main__":
    main()
```

**GitHub Actions 集成示例**：

```yaml
# .github/workflows/code-review.yml
name: AI Code Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install claude-agent-sdk
      - run: python code_review_agent.py --output review.json
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      - uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('review.json', 'utf8'));
            github.rest.issues.createComment({
              ...context.repo,
              issue_number: context.issue.number,
              body: `## 🤖 AI Code Review\n${report.result}`
            });
```

### 10.4 项目四：交互式 Agent（综合应用）

```python
"""
交互式 Agent — 支持多轮对话和自定义工具
"""
import asyncio
from datetime import datetime
from claude_agent_sdk import (
    query, ClaudeAgentOptions, tool, create_sdk_mcp_server,
    ClaudeSDKClient
)

# 自定义工具
@tool("get_time", "获取当前时间", {})
async def get_time(args):
    return {
        "content": [{"type": "text", "text": f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}]
    }

@tool("todo_add", "添加待办事项", {"item": str})
async def todo_add(args):
    with open("todos.txt", "a") as f:
        f.write(f"- {args['item']}\n")
    return {"content": [{"type": "text", "text": f"已添加: {args['item']}"}]}

@tool("todo_list", "列出所有待办事项", {})
async def todo_list(args):
    try:
        with open("todos.txt") as f:
            items = f.read()
        return {"content": [{"type": "text", "text": items or "暂无待办"}]}
    except FileNotFoundError:
        return {"content": [{"type": "text", "text": "暂无待办"}]}

# 创建工具服务器
tools_server = create_sdk_mcp_server(
    name="personal-tools",
    version="1.0.0",
    tools=[get_time, todo_add, todo_list]
)

def get_options():
    return ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        allowed_tools=[
            "Read", "Write", "Bash",
            "mcp__personal-tools__get_time",
            "mcp__personal-tools__todo_add",
            "mcp__personal-tools__todo_list",
        ],
        mcp_servers={"personal-tools": tools_server},
        system_prompt="""你是全能助手。你可以：
1. 获取当前时间
2. 添加和查看待办事项
3. 读写文件和执行命令
请根据需求选择合适的工具。用中文回复。"""
    )

async def interactive_chat():
    print("=" * 60)
    print("欢迎使用交互式 Agent！")
    print("你可以：")
    print("  - 问现在几点")
    print("  - 添加待办：添加待办 写周报")
    print("  - 查看待办")
    print("  - 读写文件或执行命令")
    print("输入 退出 结束对话")
    print("=" * 60)

    async with ClaudeSDKClient(options=get_options()) as client:
        while True:
            user_input = input("\n你: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["退出", "再见", "exit", "quit"]:
                print("\nAgent: 再见！")
                break

            await client.query(user_input)
            print("\nAgent: ", end="", flush=True)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(block.text, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(interactive_chat())
```

---

## 11. 常见问题与故障排查

### 11.1 Agent 不调用工具

**症状**：Agent 直接返回文本，不调用你定义的工具。

**原因排查**：
1. 工具描述不够清晰
2. 输入模式过于复杂
3. 任务描述与工具能力不匹配

**解决方案**：

```python
# ❌ 模糊的描述
@tool("file_tool", "文件操作", ...)

# ✅ 清晰描述触发条件
@tool("read_file", "读取文本文件内容，支持 .md/.txt/.json，返回文件内容和元数据", {"path": str})
```

### 11.2 长时间任务中途失败

**症状**：处理大量文件时，某一步出错导致整个任务失败。

**解决方案**：实现检查点（Checkpoint）机制。

```python
import json
from pathlib import Path

async def process_with_checkpoint(files: list, processor):
    checkpoint_file = Path("./checkpoint.json")
    checkpoint = {}
    if checkpoint_file.exists():
        checkpoint = json.loads(checkpoint_file.read_text())

    start = checkpoint.get("step", 0)
    for i in range(start, len(files)):
        try:
            result = await processor(files[i])
            checkpoint["step"] = i + 1
            checkpoint["last_success"] = str(files[i])
            if i % 5 == 0:  # 每 5 个文件保存一次
                checkpoint_file.write_text(json.dumps(checkpoint))
        except Exception as e:
            checkpoint_file.write_text(json.dumps(checkpoint))
            raise e

    checkpoint_file.unlink(missing_ok=True)
```

### 11.3 输出质量不稳定

**症状**：相同任务每次结果差异很大。

**解决方案**：增加验证步骤。

```python
async def run_with_verification(task: str, max_attempts=3):
    for attempt in range(max_attempts):
        result = await run_agent(task)
        # 验证输出质量
        if len(result) < 100 or "TODO" in result:
            task = f"{task}\n注意：请提供更详细的分析。"
            continue
        return result
    return result  # 返回最后一次结果
```

### 11.4 API 成本过高

**优化建议**：

1. **控制上下文长度**：限制消息历史窗口
2. **压缩工具输出**：对大结果做截断摘要
3. **分层模型策略**：简单任务用 Haiku，复杂用 Sonnet/Opus

```python
# 工具输出压缩
def compress_output(text: str, max_len: int = 2000) -> str:
    if len(text) > max_len:
        return text[:max_len] + f"\n...[省略 {len(text) - max_len} 字符]"
    return text
```

### 11.5 SDK vs 其他框架

| 维度 | Claude Agent SDK | LangChain | AutoGPT |
|------|-----------------|-----------|---------|
| **目标** | 可控、可审计的企业级执行 | 通用 LLM 应用框架 | 完全自主的 AGI 探索 |
| **控制粒度** | 细粒度工具策略 | 中等 | 粗粒度 |
| **场景** | 代码重构、数据处理、运维 | 聊天机器人、RAG | 开放式任务探索 |
| **学习曲线** | 中（但有扎实文档） | 陡峭 | 简单 |

---

## 12. 最佳实践与设计模式

### 12.1 Agent 反馈循环模式（核心模式）

Anthropic 工程团队推荐的 **Gather → Take Action → Verify** 循环：

```
┌─────────────────────────────────────────────┐
│         Gather Context（收集上下文）          │
│  · 文件系统索引（grep/tail 智能加载）         │
│  · 子代理并行搜索                           │
│  · 自动上下文压缩（Compaction）               │
└─────────────────┬───────────────────────────┘
                  ▼
┌─────────────────────────────────────────────┐
│         Take Action（执行任务）               │
│  · 内置工具（Read/Write/Bash/...）           │
│  · MCP 外部服务调用                         │
│  · 代码生成（精确、可组合、可复用）            │
└─────────────────┬───────────────────────────┘
                  ▼
┌─────────────────────────────────────────────┐
│         Verify Work（验证工作）               │
│  · 规则反馈（lint、类型检查）                 │
│  · 视觉反馈（截图、渲染）                    │
│  · LLM 作为评判者（子代理评审）               │
└─────────────────┬───────────────────────────┘
                  ▼
          继续或结束 ─── 未完成 → 回到收集上下文
```

### 12.2 工具设计原则

1. **描述要有上下文**：告诉 Agent 何时使用、什么输入、什么输出
2. **输入模式要简洁**：过复杂的 schema 会让 Agent 困惑
3. **错误处理要优雅**：工具内部捕获异常，返回友好信息
4. **命名要自描述**：`get_user_info` 优于 `user_tool`

### 12.3 Prompt 工程策略

1. **明确角色设定**：在 `system_prompt` 中定义 Agent 的专家角色
2. **给出约束边界**：告诉 Agent 什么不能做（安全边界）
3. **结构化输出要求**：指定输出格式（JSON、列表等）
4. **提供错误恢复路径**：告诉 Agent 出错时该怎么办

### 12.4 成本优化策略

| 策略 | 说明 | 预期节省 |
|------|------|---------|
| **分层模型** | 简单子代理用 Haiku，复杂用 Opus | 40-60% |
| **限制 max_turns** | 防止 Agent 过度迭代 | 20-30% |
| **压缩工具输出** | 截断大结果 | 15-25% |
| **会话恢复** | 避免重复读取大文件 | 30-50% |
| **Batch API** | 批量调用 Anthropic API 享折扣 | 50% |

### 12.5 安全清单

- [ ] `allowed_tools` 遵循最小权限原则
- [ ] 通过 Hook 阻止危险 Bash 命令
- [ ] 敏感文件路径在 `canUseTool` 中过滤
- [ ] 生产环境使用 `acceptEdits` 而非 `bypassPermissions`
- [ ] 所有工具调用记录审计日志
- [ ] 设置合理的 `max_turns` 上限
- [ ] API Key 通过环境变量注入，不硬编码
- [ ] 子代理权限范围不超过主 Agent

---

## 13. 生态与进阶资源

### 13.1 SDK 版本演进时间线

| 阶段 | 包名 | 说明 |
|------|------|------|
| 早期 (2025) | `claude-code-sdk` / `@anthropic-ai/claude-code` | 初始版本，紧耦合 Claude Code |
| 当前 (2026) | `claude-agent-sdk` / `@anthropic-ai/claude-agent-sdk` | 通用 Agent 运行时，独立于 CLI |

### 13.2 推荐学习路径

1. **入门（1-2 天）**：阅读本文 → 完成 Hello World → 尝试代码审查项目
2. **进阶（3-5 天）**：自定义工具 → MCP 集成 → 子代理编排 → 生产部署
3. **专家（1-2 周）**：多 Agent 协作系统 → CI/CD 集成 → 性能优化 → 安全审计

### 13.3 官方资源

- [Agent SDK 官方概览](https://platform.claude.com/docs/en/agent-sdk/overview)
- [GitHub: Python SDK](https://github.com/anthropics/claude-agent-sdk-python)
- [GitHub: TypeScript SDK](https://github.com/anthropics/claude-agent-sdk-typescript)
- [Claude Code 官方文档](https://code.claude.com/docs/en/agent-sdk/quickstart)
- [Blog: Building agents with Claude Agent SDK](https://claude.com/blog/building-agents-with-the-claude-agent-sdk)

### 13.4 社区资源

- Nader Dabit: [The Complete Guide to Building Agents with Claude Agent SDK](https://nader.substack.com/p/the-complete-guide-to-building-agents)
- Moksa: [Claude Code Agent SDK 完整指南](https://moksaweb.com/claude-code-agent-sdk/)
- 老金: [Claude Agent SDK 完整指南 (GitHub)](https://github.com/KimYx0207/AI-Coding-Guide-Zh/blob/main/docs/claude-code/09-Agent-SDK%E5%AE%8C%E6%95%B4%E6%8C%87%E5%8D%97.md)
- Yeasy: [Claude Agent SDK 深度指南](https://yeasy.gitbook.io/claude_guide/di-san-bu-fen-jin-jie-pian/08_agent/8.6_agent_sdk_deep_dive)
- DataCamp: [Claude Agent SDK Tutorial](https://www.datacamp.com/tutorial/how-to-use-claude-agent-sdk)
- SerpAPI: [Build an AI Agent with Claude Agent SDK](https://serpapi.com/blog/build-an-ai-agent-with-claude-agent-sdk/)

---

> **许可证**：本文档为社区整理的学习资源，基于 Anthropic 官方文档和社区教程综合编写。如有更新请以 [官方文档](https://platform.claude.com/docs/en/agent-sdk/overview) 为准。
