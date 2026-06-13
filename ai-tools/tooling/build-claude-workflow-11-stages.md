---
title: "从空白对话到自运行助手：构建 Claude 工作流的 11 个阶段"
tags:
  - Claude
  - AI-Agents
  - Workflow
  - Anthropic
  - MCP
  - Agent-SDK
  - automation
date: 2026-06-12
source: "https://x.com/rileywestreel/status/2065472381737459802"
authors: "Riley West (@rileywestreel)"
---

# 从空白对话到自运行助手：构建 Claude 工作流的 11 个阶段

> **来源：** [How to Build a Claude Workflow: 11 Stages From Blank Chat to a Self-Running Assistant](https://x.com/rileywestreel/status/2065472381737459802) — Riley West, 2026-06-12

![封面](../image/build-claude-workflow-11-stages-cover.jpg)

几乎所有人都止步在对话界面。打开空白对话，粘贴问题，复制答案，关掉标签页。工具、记忆、无需你干预就能自动循环的流程——大多数每天都用 Claude 的人，从未触碰过这些东西。

**本文将填补这个空白。一个有价值的助手不是更好的提示词——它是一个管道：一系列微小、枯燥的升级，把一个聊天窗口变成一个能睡大觉时自动运转的流程。**

以下是通往那里的 11 个阶段——从空白对话，经过工具、Agent 和 MCP，最终抵达一个按 cron 定时触发并汇报工作的任务。每个阶段都是一次移动。你不需要第一天就搞定全部 11 个阶段；你只需要第 N+1 阶段。

> 这条主线的骨架来自 Anthropic 自身的 Agent 构建建议：**从简单起步，组合小模式，只在能收回成本时才增加机器**（@AnthropicAI, *Building Effective Agents*, 2024年12月）。我们将沿着这个阶梯一路爬上去。

**你将构建什么**：一个收件箱/运维助手——能分类输入、调用真实工具、在循环中运行、跨会话记住事实、按计划自动触发。栈：Python（Anthropic SDK → Claude Agent SDK）+ MCP。参考模型：`claude-haiku-4-5-20251001`、`claude-sonnet-4-6`、`claude-opus-4-8`。

---

## 第一部分 · 思维模型

在接触工具和 Agent 之前，先把无聊但基础的工程正确建立起来：**稳定的指令层**和**机器可读的输出**。跳过这些，后面每一个阶段都会继承一团乱麻。

### 01. 从空白对话开始，设定基线

在普通聊天界面（claude.ai 或桌面客户端）中手动完成任务一次。这不是浪费时间——**这是你的基线**。你是在摸索精确的措辞，然后再将其冻结为代码。反复迭代提示词，直到连续三次都输出正确的结果。

![Stage 01 - Baseline](../image/build-claude-workflow-11-stages-1.jpg)

> **原则：** 如果你不能在聊天中用手动方式获得干净的结果，再多自动化也救不了你。自动化会放大你起步时的一切，包括 bug。

**何时使用：** 启动任何新任务时；或者下游阶段失败、需要隔离是提示词的问题还是管道的问题时。

### 02. 将提示词提升为系统提示词（迁移到 API）

一旦提示词能正常工作，它就不再是一条消息，而变成了**配置**。把它从对话中移出来，放到 API 的 `system` 字段中。

```python
# pip install anthropic
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM = (
    "You are an inbox triage assistant. "
    "Classify each email as exactly one of: urgent, normal, ignore. "
    "Reply with one word only."          # 规则在这里，不在每次用户轮次中
)

resp = client.messages.create(
    model="claude-sonnet-4-6",           # 均衡模型层级；换成 Haiku 可降低成本
    max_tokens=16,                       # 只输出一个词→很小的预算
    system=SYSTEM,                       # 配置，应用于每次调用
    messages=[{"role": "user", "content": "Subject: server on fire\nBody: prod is down"}],
)

print(resp.content[0].text)              # -> "urgent"
```

系统提示词是适用于每一轮的规则；用户消息只是数据。将它们分离是第一个真正的工程步骤。

这也解锁了模型选择。有意识地选择层级：Haiku 用于便宜/快速的分类，Sonnet 用于均衡工作，Opus 用于困难推理。分类任务很简单，所以不需要用最贵的模型。

**何时使用：** 相同指令在多个请求中重复时；或者需要用代码而不是手动输入来调用任务时。

### 03. 强制结构化输出：让输出可被机器读取

对人工来说，一个词的答案就够了。但一旦代码需要处理输出，自由文本就成了负债——你写的正则表达式会在下一个响应时崩掉。

相反，**通过工具 schema 强制 Claude 输出**。设置 `tool_choice` 指向特定工具后，模型必须返回匹配你 JSON 形状的参数。无需解析，无需猜测。

```python
import json
from anthropic import Anthropic

client = Anthropic()

# 将你想要的输出描述为工具的 input_schema
save_ticket = {
    "name": "save_ticket",
    "description": "Save a structured support ticket.",
    "input_schema": {
        "type": "object",
        "properties": {
            "priority": {"type": "string", "enum": ["low", "medium", "high"]},
            "topic":    {"type": "string"},
            "summary":  {"type": "string"},
        },
        "required": ["priority", "topic", "summary"],
    },
}

resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    tools=[save_ticket],
    tool_choice={"type": "tool", "name": "save_ticket"},  # 强制使用此工具 -> 保证 JSON
    messages=[{"role": "user", "content": "My API keys leaked and billing is wrong."}],
)

# 结构化数据以 dict 形式到达 tool_use 块中——已经解析好了
ticket = next(b.input for b in resp.content if b.type == "tool_use")
print(json.dumps(ticket, indent=2))
# -> {"priority": "high", "topic": "security", "summary": "Leaked API keys; billing error"}
```

> 这是整篇指南的枢纽：结构化输出使得下一阶段（真正的工具）得以存在。你在教 Claude 填写表单，而不是写文章。

**何时使用：** 另一个系统要消费输出时——数据库、API、代码中的分支。

![Stage 03 - Structured Output](../image/build-claude-workflow-11-stages-2.jpg)

---

## 第二部分 · 给 Claude 装上双手

结构化输出是准备阶段。现在 Claude 不再描述动作，而是开始执行动作——先一个工具，然后多个，最后是一个能自主判断何时完成的循环。

### 04. 给 Claude 一个工具，闭合工具使用循环

工具就是你向 Claude 描述的一个函数。当 Claude 想要用时，API 会以 `stop_reason == "tool_use"` 停下来，把参数交给你，然后等待。你运行函数，把结果喂回去，再次调用 API。这个来回——模型请求，你回答，重复直到完成——就是 **Agentic 循环**。你听说过的每一个"Agent"本质上都是这个 while 循环加上漂亮的包装。

从一个工具开始。**一个你能调试的工具，胜过十个你调试不了的。**

```python
from anthropic import Anthropic

client = Anthropic()

def get_weather(city: str) -> str:
    return f"{city}: 18C, clear"          # 假装这真的调了 API

weather_tool = {
    "name": "get_weather",
    "description": "Get current weather for a city.",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
}

messages = [{"role": "user", "content": "What should I wear in Berlin today?"}]

while True:
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=[weather_tool],
        messages=messages,
    )
    messages.append({"role": "assistant", "content": resp.content})

    if resp.stop_reason != "tool_use":                 # Claude 不再需要工具 -> 结束
        print("".join(b.text for b in resp.content if b.type == "text"))
        break

    tool_results = []
    for block in resp.content:
        if block.type == "tool_use":
            result = get_weather(**block.input)        # 分发到你的真实函数
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,                # 将结果关联到请求
                "content": result,
            })
    messages.append({"role": "user", "content": tool_results})  # 反馈 -> 继续循环
```

**何时使用：** 任务需要实时数据或副作用时——天气、数据库行、发邮件——任何模型无法从记忆中完成的事。

![Stage 04 - Tool Use Loop](../image/build-claude-workflow-11-stages-3.jpg)

### 05. 将工具组合成工作流：路由，然后链式处理

一个工具是一个特性。跃迁到工作流意味着用预定义的路径编排多个工具。两种模式覆盖了大部分需求，直接来自 Anthropic 的剧本：

- **路由（Routing）** — 一个便宜的模型读取输入并选择跑道（退款 vs Bug vs 销售）。分类很容易，所以用 Haiku 路由，把 Sonnet/Opus 留给困难步骤。
- **链式处理（Prompt Chaining）** — 将任务分解为步骤，每一步的输出喂给下一步（草稿 → 润色），这样每次调用只做好一件简单的事。

```python
from anthropic import Anthropic
client = Anthropic()

def ask(prompt, model="claude-haiku-4-5-20251001", system="", max_tokens=512):
    msg = client.messages.create(
        model=model, max_tokens=max_tokens, system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()

def route(text):                                        # 路由：最便宜的模型选择跑道
    lane = ask(f"Classify intent, one word [refund|bug|sales]:\n{text}",
               model="claude-haiku-4-5-20251001")
    return lane.lower()

def handle(text):                                       # 链式：上一步的输出喂给下一步
    lane = route(text)
    if lane == "bug":
        repro = ask(f"Write numbered repro steps for this bug:\n{text}",
                    model="claude-sonnet-4-6")          # 更难的步骤 -> 更强的模型
        return ask(f"Turn these repro steps into a calm customer reply:\n{repro}")
    return ask(f"Answer this {lane} request:\n{text}")

print(handle("The app crashes when I upload a 2GB file."))
```

> Anthropic 的区分很重要：**工作流**运行你代码中定义的路径；**Agent**让模型自主决策。工作流更可预测——当步骤已知时优先使用它。

**何时使用：** 任务有清晰阶段或明显不同类型的请求，且你需要可预测性胜过自主性。

![Stage 05 - Route and Chain](../image/build-claude-workflow-11-stages-4.jpg)

### 06. 闭合循环成为 Agent（Claude Agent SDK）

手写 while 循环教会你原理。但在实际工作中，不要自己维护它。**Claude Agent SDK**（2025年9月从 Claude Code SDK 更名而来）把整个循环——规划、工具调用、重试、文件 I/O——打包到一次 `query()` 调用后面。你交给它一个目标和一套工具；它运行「思考 → 行动 → 观察」直到目标达成或 `max_turns` 触发。

这就是驱动 Claude Code 的同一套引擎，以库的形式暴露出来。

```python
# pip install claude-agent-sdk   (Python 3.10+, 自带 Claude CLI)
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock

options = ClaudeAgentOptions(
    system_prompt="You are a research assistant. Cite every source.",
    allowed_tools=["WebSearch", "Read", "Write"],   # 自动批准这些，其余提示用户
    permission_mode="acceptEdits",                  # 文件编辑不暂停
    max_turns=8,                                     # 循环的硬上限
)

async def main():
    # query() 为你运行完整的 think -> act -> observe 循环
    async for message in query(prompt="Summarize today's AI news into news.md", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

anyio.run(main)
```

**何时使用：** 任务需要超过 2–3 次工具调用时，或者你在手写循环/重试/权限管理时。

![Stage 06 - Agent SDK](../image/build-claude-workflow-11-stages-5.jpg)

---

## 第三部分 · 扩展 Agent

单 Agent 处理短任务已经解决了。现在的问题是可靠性（它不能做危险的事）和规模（一个上下文窗口不够）。三步：护栏、委派、连接真实世界。

### 07. 添加自定义工具和护栏（Hook + 权限）

内置工具能带你走很远，但你的助手需要你特有的操作——发起退款、更新数据库行、发 Slack 消息。在 Agent SDK 中，自定义工具就是一个用 `@tool` 包装的普通 async 函数，作为进程内 MCP 服务器提供服务（无需子进程，无需 IPC）。

当工具可以花钱或删除数据时，你需要一个 **hook**：SDK 在生命周期节点（如 `PreToolUse`）运行的决定性代码，可以在调用发生前拒绝它。

```python
from claude_agent_sdk import (
    tool, create_sdk_mcp_server, ClaudeAgentOptions, ClaudeSDKClient, HookMatcher,
)

# 自定义工具 = 暴露给 Claude 的 async 函数
@tool("refund", "Issue a refund in cents", {"order_id": str, "cents": int})
async def refund(args):
    # ... 在此调用你的支付 API ...
    return {"content": [{"type": "text", "text": f"Refunded {args['cents']}c on {args['order_id']}"}]}

server = create_sdk_mcp_server(name="ops", version="1.0.0", tools=[refund])

# Hook = 由 APP（而非模型）执行的决定性护栏
async def cap_refund(input_data, tool_use_id, context):
    if input_data["tool_name"] == "mcp__ops__refund":
        if input_data["tool_input"].get("cents", 0) > 5000:        # > $50 -> 阻止
            return {"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",                      # 在运行前拦截
                "permissionDecisionReason": "Refunds over $50 need a human.",
            }}
    return {}

options = ClaudeAgentOptions(
    mcp_servers={"ops": server},
    allowed_tools=["mcp__ops__refund"],
    hooks={"PreToolUse": [HookMatcher(matcher=None, hooks=[cap_refund])]},  # 门控工具调用
)
```

> **模型提议；Hook 裁决。** 护栏应该放在你控制的代码中，而不是放在你希望模型遵守的提示词里。

**何时使用：** Agent 可以执行真实、不可逆的操作时——支付、删除、外部发帖。

![Stage 07 - Guardrails](../image/build-claude-workflow-11-stages-6.jpg)

### 08. 通过子 Agent 委派任务（编排器-工作器模式）

当任务铺开时——研究五个竞品，逐一总结——不要把所有东西都塞进一个上下文窗口。启动**子 Agent（subagents）**：在自己独立的上下文中运行的专业 Agent，只向主"编排器"返回简练的摘要。这就是 Anthropic 的**编排器-工作器（orchestrator-workers）**模式，也是你在保住上下文限制的同时并行完成更多工作的方法。

子 Agent 就是一个带有 frontmatter 的 Markdown 文件，放在 `.claude/agents/` 目录下。

```markdown
<!-- .claude/agents/researcher.md -->
---
name: researcher
description: Deep-dive ONE topic and return a tight summary. Use proactively for research.
tools: WebSearch, Read
model: sonnet            # 工作器可以比编排器运行更便宜的模型
---
You are a focused research worker. Investigate ONLY the topic you are handed.
Return exactly: 5 bullet findings + 3 source URLs. No preamble, no filler.
```

编排器用自然语言委派——"用研究员子 Agent 分别研究这五家公司，并行进行"——每个工作器的详细搜索停留在自己的工作区。只有摘要回来。

**何时使用：** 任务可以拆分为独立的子任务，或者一个 Agent 的上下文被嘈杂的中间输出撑爆时。

![Stage 08 - Subagents](../image/build-claude-workflow-11-stages-7.jpg)

### 09. 通过 MCP 连接真实世界

你的助手的价值取决于它能触及的范围。**模型上下文协议（Model Context Protocol, MCP）**——Anthropic 的开放标准，2024年11月25日发布——是工具的 USB-C：一个基于 JSON-RPC 的协议，任何符合规范的服务器（GitHub、Slack、Postgres、你的内部 API）即插即用。它消灭了 N×M 问题——每个应用都需要为每个数据源做自定义集成的困境。

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

options = ClaudeAgentOptions(
    mcp_servers={
        # 外部 MCP 服务器：一个标准，任意厂商。替换这个块，获得上百个新动作。
        "github": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_TOKEN": "ghp_..."},
        },
    },
    allowed_tools=["mcp__github__create_issue", "mcp__github__search_issues"],
)

async def main():
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Open an issue titled 'Flaky CI' in my main repo.")
        async for msg in client.receive_response():
            print(msg)
```

**何时使用：** 你需要 Agent 接触一个已经支持 MCP 的系统，而不是手写 API 包装器。

![Stage 09 - MCP](../image/build-claude-workflow-11-stages-8.jpg)

---

## 第四部分 · 让它跑起来

Agent 已经工作，有双手，能触及你的系统。还有最后两步，把它从"你调用的东西"变成"自己运行的东西"：**持久记忆**和**不需要你的触发器**。

### 10. 赋予记忆并管理上下文

默认情况下，每次运行都是从失忆开始的。要表现得像一个真正的助手，它必须跨会话记住事实，而不把整个历史拖进每次调用——那条路通往爆掉的上下文窗口。模式很简单：保留一个小而持久的存储，读入相关切片，写出新事实。

以下是手动实现版本，这样你能看到机制：

```python
# 轻量级、可验证的记忆：开头读取、结尾追加的文件。
# 这正是平台原生"memory tool"在客户端自动化的思想。
from pathlib import Path
from anthropic import Anthropic

client = Anthropic()
MEM = Path("memory.md")
MEM.touch(exist_ok=True)

def run(user_msg):
    memory = MEM.read_text()[-4000:]                 # 只取最近的部分 -> 有限上下文
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=f"Durable notes about this user:\n{memory}",   # 将记忆作为上下文注入
        messages=[{"role": "user", "content": user_msg}],
    )
    answer = resp.content[0].text
    MEM.write_text(memory + f"\n- {user_msg[:80]}")  # 持久化一个事实（实际使用中让 Claude 挑选）
    return answer

print(run("I'm allergic to peanuts — remember that for any food suggestions."))
```

**在生产中使用平台的记忆工具（memory tool）**——Claude 跨会话读写的客户端文件存储——配合上下文编辑（context editing，在接近限制时自动清除过时的工具调用）。Anthropic 在内部 Agentic 搜索评估中测得两者配合带来 39% 的提升；在 100 回合的网络搜索测试中，上下文编辑将 token 使用量削减了 84%，同时让原本会因上下文耗尽而失败的回合得以完成。（两者在 Claude Developer Platform 上均为 Beta——上线前确认文档中的当前 Beta 标志。）

**何时使用：** 助手需要跨天记住偏好/决策时，或者长运行总是撞到上下文天花板时。

![Stage 10 - Memory](../image/build-claude-workflow-11-stages-4.jpg)

### 11. 让它自己跑起来（无头模式 + Cron）

最后一步把你从触发器中去掉。Claude Code / Agent SDK 无头运行：一个 prompt 进去，一个结果出来，然后退出——一个普通的命令行程序。把它包装到 shell 脚本里，让 cron 指向它，你的助手现在按计划醒来，做工作，记录结果。

> **这就是「我用的工具」和「运行的助手」之间的分界线。**

```bash
#!/usr/bin/env bash
# self-runner.sh — 一次无人值守的 Agent 批量运行
set -euo pipefail
export ANTHROPIC_API_KEY="sk-ant-..."          # cron 环境空：显式设置机密

cd "$HOME/agents/inbox"
# -p = headless/print: 运行一次，写结果，退出。--bare = 为 cron/CI 确定性的启动。
claude -p "Triage new emails in ./inbox and draft replies into ./drafts" \
  --allowedTools "Read,Write,Bash" \           # 无人值守运行限缩爆炸半径
  --bare > "logs/$(date +%F).log" 2>&1

# 调度 (crontab -e): 每个工作日 08:00，助手自动运行
# 0 8 * * 1-5  /home/me/agents/inbox/self-runner.sh
```

两条生产注意事项已烘焙到上述脚本中：
- cron 启动时环境很空，所以要**显式 export ANTHROPIC_API_KEY**
- `--allowedTools` 要**严格限定**，这样无人值守的运行不会四处乱逛

**何时使用：** 任务应该按时钟或事件触发——而不是在你想起来打开标签页的时候。

---

## 常见错误

以下错误模式会悄悄浪费 token 并破坏信任。每条是：错误 → 为什么不好 → 修复方法。

| # | 错误 | 为什么不好 | 修复 |
|---|------|-----------|------|
| 1 | **一个大 Prompt 包揽一切** | 上下文腐化——随着指令和历史填充窗口，准确率下降，成本上升 | 先路由，再链式小步骤 |
| 2 | **用正则解析自由文本** | 格式每次响应都变，解析器碎一地 | 强制工具 schema |
| 3 | **把所有工具一次给 Agent** | 更多工具 = 更多错误方向 + 更大的爆炸半径 | 严格的 allowlist |
| 4 | **没有停止阀门的循环** | 困惑的 Agent 无限循环，烧光预算 | 限制 turns、门控动作 |
| 5 | **一个大 Agent 处理铺开的大任务** | 单一上下文窗口被中间噪音撑爆 | 编排器 + 子 Agent，各自独立上下文，只返回摘要 |
| 6 | **"为保险"把所有东西留在上下文中** | 撞到限制，Agent 中途丢失线索 | 记忆工具 + 上下文编辑——事实持久化到存储，清除过时工具调用（Anthropic 测试节省 84% token） |

---

## 结论

一个自运行的助手从来不是靠一个聪明的提示词。它是**11 个微小而枯燥的升级按顺序堆叠**的结果：

1. 稳定的指令层
2. 结构化输出
3. 一个工具
4. 一个循环
5. 拥有这个循环的 SDK
6. 护栏
7. 委派
8. MCP 扩展连接
9. 记忆
10. Cron 触发器

每个阶段独立有用，每个阶段都为下一阶段铺路。

> **贯穿始终的主线，也是 Anthropic 对 Agent 的建议：从简单开始，组合小模式，只在能收回成本时才增加机器。** 不要在第一天就构建第 11 阶段。找到你的助手还在手动做事的那个最低阶段——然后向上爬刚好一级。

### 现在就做（5 步检查清单）

1. 将最好的 prompt 冻结为 `system` 字段，为任务固定模型层级 (Haiku/Sonnet/Opus)
2. 用 `tool_choice` 强制一个输出为 JSON——消灭你的第一个正则
3. 连接一个真实工具，闭合工具使用循环（`stop_reason == "tool_use"`）
4. 将循环迁移到 Agent SDK 的 `query()`，加上 `max_turns` 和一个 `PreToolUse` hook
5. 用 cron 调度一个无头任务：`claude -p ... --allowedTools ...` 放在 cron 行后面

**今天就交付第 1 阶段。在你睡觉时自动运行的助手，只是你已经开始的某件事的第 11 阶段。**

---

*整理于 2026-06-13，来源：Riley West 的 X/Twitter 长文*
