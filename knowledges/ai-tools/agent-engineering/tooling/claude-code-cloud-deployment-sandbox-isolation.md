---
title: "Claude Code 云端部署与沙箱多用户隔离实践"
source: "https://mp.weixin.qq.com/s/gaBKZFIZetj9H9eqyhT13g"
author: "阿里开发者"
date: 2026-05-28
tags:
  - claude-code
  - cloud-deployment
  - sandbox
  - fastapi
  - sse
  - multi-user-isolation
  - file-versioning
  - harness-engineering
  - docker
  - agent-loop
  - session-store
  - checkpointing
  - bubblewrap
  - deployment-patterns
  - security-best-practices
  - subagents
category: "ai-tools/agent-engineering/tooling"
---

# Claude Code 云端部署与沙箱多用户隔离实践

> **来源：** 阿里开发者（阿里妹导读）  
> **内容：** 将本地 Claude Code CLI 改造为云端 HTTP 流式服务，并通过「一用户一沙箱 + 文件版本化」实现多用户隔离
> **核心耗时：** 1.5 人日 + 1909 Credits

---

## 一、背景：从 DIY Agent 到 Harness Engineering

在 OpenClaw、Claude Code 等产品出现之前，自主开发 Agent 的基本思路是：

1. **DIY ReactAgent** — 基于 LLM 实现 Loop 调用 + MCP/自定义工具
2. **框架接入** — 利用 Spring AI、LangGraph 配置工具和提示词

但这些方案都有明显局限。随着 **Harness Engineering** 概念的提出（参见 [Agent Harness Engineering](/ai-tools/agent-engineering/harness/agent-harness-engineering.md)），一个稳定好用的 Agent 还需要：
- 约束层工具
- 任务完成的 Evaluation 机制
- 上下文切换到干净的子 Agent

自行开发实现这些门槛很高，框架（Spring AI / LangGraph）也很难及时适配最新的 Agent 设计理念。

**当下最快的路径：** 部署现有的成熟产品 → 提供调用能力 → 在应用层和端上做封装及扩展。

### 核心挑战

将 Claude Code（本地 CLI 闭源产品）部署到云端，面临三个关键问题：

| 问题 | 描述 |
|------|------|
| **离线部署** | 服务器/沙箱无外网，不支持 `brew install` 等在线安装 |
| **服务化输出** | CLI 非流式、输出的是终端 UI 而非结构化结果，不适合程序消费 |
| **多用户隔离** | Claude Code 是单实例本地系统，记忆和配置以文件形式存储，多用户会串扰 |

---

## 二、整体方案

```
┌───────────────────────────────────────────────────────────────────┐
│                         Application Layer                        │
│                   (Web UI / Bot / API Gateway)                    │
└──────────────────────────┬────────────────────────────────────────┘
                           │  HTTP + SSE
                           ▼
┌───────────────────────────────────────────────────────────────────┐
│                       Sandbox Control Plane                       │
│          (路由分发 / 沙箱生命周期管理 / 用户实例映射)               │
└──────┬───────────────┬───────────────┬────────────────────────────┘
       │               │               │
       ▼               ▼               ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│Sandbox A │   │Sandbox B │   │Sandbox C │   ← 每用户独占
│┌──────┐  │   │┌──────┐  │   │┌──────┐  │
││Claude│  │   ││Claude│  │   ││Claude│  │
││ Code │  │   ││ Code │  │   ││ Code │  │
│└──┬───┘  │   │└──┬───┘  │   │└──┬───┘  │
│┌──▼───┐  │   │┌──▼───┐  │   │┌──▼───┐  │
││HTTP  │  │   ││HTTP  │  │   ││HTTP  │  │
││:8765 │  │   ││:8765 │  │   ││:8765 │  │
│└──────┘  │   │└──────┘  │   │└──────┘  │
│~/.claude/│   │~/.claude/│   │~/.claude/│  ← 独立记忆&配置
└──────────┘   └──────────┘   └──────────┘
```

**四层架构：**

1. **云端离线部署** — `npm pack` 打包 → Docker 镜像
2. **HTTP 流式服务化** — Claude Agent SDK + FastAPI + SSE
3. **基础镜像构建** — 一次性打包 Node.js + Python + Claude CLI
4. **沙箱多实例隔离** — 每用户独立沙箱 + 文件版本化持久化

---

## 三、Claude Code 云端离线部署

### 3.1 环境要求

```bash
node -v       # 需要 Node.js 18+
npm -v
uname -m      # 确认 CPU 架构: x86_64 or aarch64
```

### 3.2 获取离线包

**推荐方式：npm pack**

```bash
# 在有外网的机器上执行
npm pack @anthropic-ai/claude-code
# → 生成 anthropic-ai-claude-code-2.1.119.tgz
```

**备选（整目录打包，避免依赖缺失）：**

```bash
npm install -g @anthropic-ai/claude-code
cd $(npm root -g)
tar -czvf claude-code-full.tar.gz @anthropic-ai/claude-code
```

### 3.3 离线安装

```bash
tar -xf node-v20.x.x-linux-x64.tar.xz
export PATH=$PWD/node-v20.x.x-linux-x64/bin:$PATH

sudo npm install -g ./anthropic-ai-claude-code-2.1.119.tgz
claude --version
```

### 3.4 Agent Loop 架构：SDK 内部工作流

理解 Claude Agent SDK 背后的 agent loop 机制，对构建稳健的云端服务至关重要。官方文档将 Agent Loop 抽象为五个阶段：

```
┌───────────────────────────────────────────┐
│            Agent Loop (5 阶段)             │
│                                           │
│  Prompt ──→ Evaluate ──→ Execute ──→ Repeat │
│                  │                          │
│                  └──── Result ←──────────────┘
└───────────────────────────────────────────┘
```

| 阶段 | 描述 |
|------|------|
| **Prompt** | 收集系统提示、用户输入、工具定义，构建完整的 Messages 数组。包含 `system`、`user` 和已有的 `assistant`+`tool_result` 消息 |
| **Evaluate** | Claude API 根据上下文决定下一步——生成一段文本，或发起一个工具调用（tool use）|
| **Execute** | SDK 执行工具调用（文件读写、Shell 命令等），结果以 `tool_result` 形式返回 |
| **Repeat** | 新的 `tool_result` 作为上下文继续循环：Prompt → Evaluate → Execute |
| **Result** | Claude 判断任务完成（或达到 `max_turns`），返回最终 `assistant` 文本消息 |

**SDK 的超时保护：** 为防止无限制循环，始终设置 `max_turns` 参数。默认值通常为 20，但对自动化云端服务建议设更大（如 50-100），结合心跳机制防止卡死。

**和 Stream 的关系：** 每次 `query()` 调用内部自动完成整个 agent loop（可能多次调用 API）。事件流中每个 `tool_use` block 代表一次 Execute 阶段，每次 `text` block 代表 Evaluate 或 Result 阶段的输出。

---

### 3.5 注意事项

| 注意点 | 说明 |
|--------|------|
| **CPU 架构匹配** | Node.js 二进制必须与服务器架构一致（x64 / arm64） |
| **依赖缺失** | `npm pack` 只打包主包不含依赖，缺依赖时改用整目录打包 |
| **API 网络** | Claude Code 需访问 Anthropic API。完全无外网时需配置内网代理（`ANTHROPIC_BASE_URL`） |

---

## 四、HTTP 流式服务层（核心）

基于 `claude-agent-sdk` + FastAPI + SSE（Server-Sent Events），将 CLI 模式转换为 RESTful HTTP 流式接口。

### 4.1 技术栈

| 组件 | 版本 | 职责 |
|------|------|------|
| FastAPI | >=0.110.0 | 异步 Web 框架 |
| uvicorn | >=0.29.0 | ASGI 服务器 |
| sse-starlette | >=2.0.0 | SSE 协议实现 |
| claude-agent-sdk | >=0.1.60（注意！非 0.2.x） | Claude Code Python SDK |
| Pydantic | >=2.6.0 | 请求/响应模型校验 |

### 4.2 项目结构

```
claude-code-scripts/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI 入口，环境变量配置
│   ├── models/
│   │   └── schemas.py     # Pydantic 请求/响应模型
│   ├── routers/
│   │   ├── health.py      # 健康检查
│   │   ├── query.py       # 单次查询（同步 + SSE 流式）
│   │   └── sessions.py    # 多轮会话管理
│   └── services/
│       ├── agent_service.py     # 核心：SDK 封装、SSE 序列化
│       └── session_service.py   # 持久化会话查询
├── run.py                 # Uvicorn 启动入口
└── requirements.txt
```

### 4.3 核心设计：SDK 消息 → SSE 事件流

`query()` 是异步迭代器，每次 yield 出 `SystemMessage`、`AssistantMessage`、`ResultMessage`。核心工作是将这些序列化为 SSE 事件。

**消息序列化（`agent_service.py`）：**

```python
def _serialize_message(message: Any) -> dict[str, Any]:
    """将 SDK 消息对象转换为 JSON 可序列化的 SSE 事件字典"""
    if isinstance(message, SystemMessage):
        return {
            "event": "system",
            "data": {
                "subtype": getattr(message, "subtype", None),
                "session_id": getattr(message, "session_id", None)
                              or (message.data.get("session_id")
                                  if hasattr(message, "data") else None),
                "details": message.data if hasattr(message, "data") else {},
            },
        }
    elif isinstance(message, AssistantMessage):
        blocks = []
        for block in message.content:
            if isinstance(block, TextBlock):
                blocks.append({"type": "text", "text": block.text})
            elif hasattr(block, "type") and block.type == "tool_use":
                blocks.append({
                    "type": "tool_use",
                    "name": block.name,
                    "id": getattr(block, "id", None),
                    "input": getattr(block, "input", {}),
                })
            else:
                blocks.append({"type": getattr(block, "type", "unknown"),
                               "raw": str(block)})
        return {
            "event": "assistant",
            "data": {"content": blocks,
                     "parent_tool_use_id": getattr(message, "parent_tool_use_id", None)},
        }
    elif isinstance(message, ResultMessage):
        return {
            "event": "result",
            # ... result data with total_cost_usd etc.
        }
```

**SSE 流式端点（`query.py`）：**

```python
@router.post("/query/stream")
async def query_stream(req: QueryRequest):
    async def event_generator():
        async for event in run_query_stream(req):
            yield {
                "event": event.get("event", "message"),
                "data": json.dumps(event.get("data", {}), ensure_ascii=False),
            }
    return EventSourceResponse(event_generator())
```

**客户端收到的 SSE 事件流：**

```
event: system
data: {"subtype": "init", "session_id": "abc-123", ...}

event: assistant
data: {"content": [{"type": "text", "text": "我来分析一下..."}]}

event: assistant
data: {"content": [{"type": "tool_use", "name": "Glob",
                    "input": {"pattern": "**/*.py"}}]}

event: result
data: {"subtype": "success", "result": "...", "total_cost_usd": 0.012}
```

### 4.4 两种调用模式

#### 模式一：单次查询（Single-shot）

```bash
# SSE 流式（推荐）
curl -N -X POST http://localhost:8765/v1/query/stream \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "分析当前目录下的代码结构"}'

# 同步（等待完整结果）
curl -X POST http://localhost:8765/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "列出当前目录的文件"}'
```

#### 模式二：多轮会话（Streaming Session）

```bash
# 1. 创建会话
SESSION=$(curl -s -X POST http://localhost:8765/v1/sessions/create \
  -H 'Content-Type: application/json' \
  -d '{"allowedTools": ["Read", "Edit", "Glob"]}' | jq -r '.session_id')

# 2. 监听事件流（另一个终端）
curl -N http://localhost:8765/v1/sessions/$SESSION/events

# 3. 发送消息
curl -X POST http://localhost:8765/v1/sessions/$SESSION/send \
  -H 'Content-Type: application/json' \
  -d '{"message": "分析 auth 模块"}'

# 4. 继续对话
curl -X POST http://localhost:8765/v1/sessions/$SESSION/send \
  -H 'Content-Type: application/json' \
  -d '{"message": "用 JWT 重构它"}'
```

### 4.5 StreamingSession 核心实现

多轮会话基于 `StreamingSession` 类，内部维护消息队列和响应队列：

```python
class StreamingSession:
    def __init__(self, session_id: str, options: ClaudeAgentOptions):
        self.session_id = session_id
        self._client: Optional[ClaudeSDKClient] = None
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._response_queue: asyncio.Queue = asyncio.Queue()
        self._running = False

    async def start(self):
        """初始化 SDK Client 并启动后台处理循环"""
        self._client = ClaudeSDKClient(options=self.options)
        await self._client.__aenter__()
        self._running = True
        self._task = asyncio.create_task(self._process_loop())

    async def _process_loop(self):
        """后台循环：取用户输入 → 调用 SDK → 推送响应"""
        while self._running:
            msg = await self._message_queue.get()
            if msg is None:  # 关闭信号
                break
            await self._client.query(msg["message"])
            async for response in self._client.receive_response():
                await self._response_queue.put(_serialize_message(response))
            await self._response_queue.put({
                "event": "turn_complete",
                "data": {"session_id": self.session_id}
            })

    async def receive_events(self) -> AsyncGenerator[dict, None]:
        """SSE 事件流输出，超时时发送心跳保活"""
        while self._running or not self._response_queue.empty():
            try:
                event = await asyncio.wait_for(
                    self._response_queue.get(), timeout=120)
                yield event
            except asyncio.TimeoutError:
                yield {"event": "heartbeat",
                       "data": {"session_id": self.session_id}}
```

### 4.6 高级功能支持

#### 权限控制（Permission Mode）——官方六种模式

基于 Claude Code 官方文档，共有六种 Permission Mode，每种在自动化程度和安全性之间做出不同权衡：

| 模式 | 无需询问即可执行的操作 | 适用场景 |
|------|----------------------|----------|
| `default` | 仅读取操作 | 开始使用、敏感操作 |
| `acceptEdits` | 读取、文件编辑、常见文件系统命令（mkdir/touch/mv/cp等） | 代码迭代审查 |
| `plan` | 仅读取操作 | 修改前先探索代码库 |
| `auto` | 全部操作（带后台安全检查） | 长任务、减少确认疲劳 |
| `dontAsk` | 仅预先批准的工具 | 锁定 CI/CD 脚本 |
| `bypassPermissions` | 全部操作（跳过权限层） | 仅限隔离容器/VM（**云端服务首选**） |

**关键限制：** 任何模式下，写入[保护路径](https://docs.anthropic.com/en/docs/claude-code/permission-modes#protected-paths)（如仓库状态文件、Claude 自身配置）都不会被自动批准。`bypassPermissions` 是唯一跳过完整权限层的模式，**仅应在隔离容器中使用**——恰好符合本方案的沙箱架构。

**默认配置：** 云端服务设为 `bypassPermissions` 避免无人值守卡死。如需更细粒度控制，可在下方叠加 Permission Rules。

**模式切换方式（CLI）：**
- 运行中按 `Shift+Tab` 循环切换 `default` → `acceptEdits` → `plan`
- 启动时指定 `claude --permission-mode bypassPermissions`
- 在 `settings.json` 中设置 `permissions.defaultMode: "bypassPermissions"`

`auto` 模式需要满足账号条件才会出现循环；`dontAsk` 不会出现在循环中，需用 `--permission-mode dontAsk` 指定。`bypassPermissions` 可通过 `--dangerously-skip-permissions` 启用。

---

#### 子代理（Subagents）——三种定义方式与完整配置

官方 SDK 支持三种子代理创建方式：

1. **编程式**（推荐）：通过 `query()` 的 `agents` 参数在代码中定义
2. **文件式**：在 `.claude/agents/` 目录放置 Markdown 文件定义
3. **内置通用代理**：Claude 可随时通过 Agent 工具调用内置的 `general-purpose` 子代理

**完整 AgentDefinition 配置参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `description` | `string` | 是 | 自然语言描述何时使用该代理（Claude 据此自动委派）|
| `prompt` | `string` | 是 | 定义角色和行为的系统提示词 |
| `tools` | `string[]` | 否 | 允许的工具列表。省略则继承全部工具 |
| `disallowedTools` | `string[]` | 否 | 从工具集中移除的工具 |
| `model` | `string` | 否 | 模型覆盖（`'sonnet'`、`'opus'`、`'haiku'`、`'inherit'` 或完整模型 ID）|
| `skills` | `string[]` | 否 | 预加载的 Skill 列表 |
| `memory` | `'user' / 'project' / 'local'` | 否 | 该代理使用的记忆来源 |
| `mcpServers` | `(string / object)[]` | 否 | 可用的 MCP 服务器 |
| `maxTurns` | `number` | 否 | 代理最大自主轮数 |
| `background` | `boolean` | 否 | 是否以后台非阻塞任务运行 |
| `effort` | `'low' / 'medium' / 'high' / 'xhigh' / 'max' / number` | 否 | 推理努力级别 |
| `permissionMode` | `PermissionMode` | 否 | 代理内部的权限模式 |

**子代理的核心价值：**
- **上下文隔离**：每个子代理拥有独立的会话上下文，中间工具调用结果不会污染主代理的提示窗口。只有最终消息返回给父代理
- **并行执行**：多个子代理可并发运行，加速复杂工作流（如同时运行风格检查、安全扫描、测试覆盖）
- **工具限制**：子代理可限制特定工具集，减少意外操作的风险。例如一个文档审查子代理只有 Read 和 Grep 工具

**实践案例：**
```json
{
  "prompt": "审查并优化代码库",
  "agents": {
    "code-reviewer": {
      "description": "代码审查专家，检查安全性和最佳实践",
      "prompt": "你是一名高级代码审查员。关注安全漏洞、性能问题和代码异味。",
      "tools": ["Read", "Glob", "Grep"],
      "model": "sonnet"
    },
    "test-analyzer": {
      "description": "测试覆盖率分析，发现缺失的测试用例",
      "prompt": "分析测试覆盖情况，建议补充的测试用例。",
      "tools": ["Read", "Glob", "Grep", "Run"],
      "background": true
    }
  }
}
```

---

#### MCP 服务器集成

```json
{
  "prompt": "列出最近的 GitHub issues",
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_TOKEN": "ghp_xxx"}
    }
  }
}
```

**云端部署注意事项：** 容器内需确保 MCP 服务器命令可用（`npx` 需要在 PATH 中），必要时参考 Dockerfile 将常用 MCP 包预装为本地模块避免下载。

---

#### 钩子（Hooks）——拦截与控制

SDK 的 Hooks 系统允许在 Agent 循环的关键节点插入自定义逻辑。两个主要钩子点：

| 钩子 | 触发时机 | 典型用途 |
|------|----------|----------|
| `PreToolUse` | 工具执行前 | 权限拦截、参数校验、审计日志 |
| `PostToolUse` | 工具执行后 | 结果过滤、Webhook 通知、成本统计 |

**示例：**
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write|Edit",
      "action": "deny",
      "reason": "禁止写入 .env 文件"
    }],
    "PostToolUse": [{
      "matcher": "*",
      "action": "webhook",
      "webhook_url": "https://audit.example.com/log"
    }]
  }
}
```

**云端服务的 Hooks 策略：**
- `PreToolUse` 用于安全防护——在 CLI 的 `dangerouslyDisableSandbox` 参数之上添加第二层保护
- `PostToolUse` 用于审计和用量统计——记录每个用户的 API 消耗，支持按用户配额限制

### 4.7 踩坑记录

| 问题 | 现象 | 解决 |
|------|------|------|
| **SDK 版本** | `claude-agent-sdk>=0.2.111` 在 PyPI 不存在 | 改为 `>=0.1.60` |
| **权限拦截** | 读取 `~/.claude/CLAUDE.md` 时触发安全确认卡死 | 默认设为 `bypassPermissions` |
| **闭包变量绑定** | 动态生成钩子函数时循环变量延迟绑定 | 用默认参数捕获 `_event_name=event_name` |
| **异步阻塞** | SDK session 管理函数是同步阻塞调用 | 用 `asyncio.to_thread()` 包装 |

---

## 五、Docker 基础镜像

目标：将运行环境、Claude Code CLI、HTTP 服务一次性打包，沙箱实例开箱即用。

### Dockerfile 核心模块

```dockerfile
# ===== 第二阶段：系统依赖 + Node.js + Python 3.11 =====
FROM hub.docker.alibaba-inc.com/ali/ubuntu:22.04

ENV PYPI_MIRROR http://mirrors.aliyun.com/pypi/simple

# 系统依赖（编译工具链 + 浏览器运行时库）
RUN apt-get update && apt-get install -y \
    make gcc build-essential curl git wget ...

# Node.js 22.x（Claude Code 运行时依赖）
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs

# Python 3.11（从源码编译，确保版本一致性）
RUN cd /opt/temp && \
    wget https://registry.npmmirror.com/-/binary/python/3.11.13/Python-3.11.13.tgz && \
    tar xvf Python-3.11.13.tgz && cd Python-3.11.13/ && \
    ./configure && make -j && make install

# ===== 第三阶段：安装 Claude Code CLI =====
RUN npm pack @anthropic-ai/claude-code --registry=https://registry.npmmirror.com && \
    npm install -g ./anthropic-ai-claude-code-*.tgz && \
    rm -f ./anthropic-ai-claude-code-*.tgz

# ===== 第四阶段：部署 HTTP 服务 =====
COPY claude-code-scripts /home/admin/claude-code-scripts
```

### 容器启动脚本

```bash
#!/bin/bash
echo "[INFO] Starting claude-agent-http service on port 8765 ..."
cd /home/admin/claude-code-scripts
python3 run.py &
echo "[INFO] Service started. Container will stay alive."
sleep 365d
```

---

## 六、沙箱多用户隔离（核心创新）

这是整套方案最关键的设计——**如何在云上实现多用户隔离**。

### 6.1 问题本质

Claude Code 是**单用户、本地化**系统。它的所有状态以文件形式存储在本地磁盘：

```
~/.claude/                # 全局记忆与配置
├── CLAUDE.md             # 用户级记忆（跨项目）
├── settings.json         # 全局设置
├── credentials.json      # 认证信息
├── sessions/             # 会话历史索引
│   └── <session_id>.json
└── projects/             # 项目级记忆
    └── <project_hash>/
        └── CLAUDE.md

~/workspace/              # 用户工作目录
├── .claude/CLAUDE.md     # 项目级配置
├── src/                  # 代码文件
└── ...
```

多用户共享同一实例会引发：
- **记忆串扰** — 用户 A 的对话历史被用户 B 看到
- **配置冲突** — system prompt、permission mode 互相覆盖
- **文件污染** — 工作目录文件对所有用户可见
- **会话冲突** — SDK 内存中的 `_sessions` 字典是进程级，多用户碰撞

### 6.2 核心思路：一用户一沙箱 + 文件版本化

**两层隔离设计：**

1. **容器级隔离** — 每个用户独占一个沙箱实例，天然实现运行时全方位隔离
2. **用户状态持久化** — 一切皆文件！沙箱实例变成**无状态计算节点**，用户状态外置到 OSS 持久化存储

**核心洞察：** Claude Code 的用户态数据**全部都是文件**。既然一切皆文件，就可以做**文件版本化存储**：
- 新启实例 → 从 OSS 加载该用户最新版本的文件快照
- 销毁实例 → 计算文件差异，生成新版本存储到 OSS
- 沙箱可随时创建销毁，用户记忆永不丢失

### 6.3 完整架构

```
┌──────────────────────────────────────────────────────────┐
│                     Application Layer                     │
│               HTTP + SSE (带 user_id)                     │
└───────────────────────────┬──────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────┐
│                   Sandbox Control Plane                   │
│                                                          │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │路由&调度  │  │生命周期管理器 │  │ 文件版本管理器    │   │
│  │user_id→ip│  │ 创建/销毁    │  │ 快照存储(OSS)    │   │
│  │          │  │ 健康检查     │  │ 版本记录(DB)     │   │
│  │          │  │ 闲置回收     │  │ 增量同步         │   │
│  └──────────┘  └──────────────┘  └──────────────────┘   │
└────────┬────────────────┬────────────────┬───────────────┘
         │                │                │
         ▼                ▼                ▼
  ┌──────────┐   ┌──────────┐   ┌──────────┐
  │Sandbox A │   │Sandbox B │   │Sandbox C │
  │(user_001)│   │(user_002)│   │(无状态)  │
  │Claude CLI│   │Claude CLI│   │等待分配   │
  │HTTP:8765 │   │HTTP:8765 │   │          │
  │~/.claude/│   │~/.claude/│   │          │
  │(快照恢复)│   │(快照恢复)│   │          │
  └────┬─────┘   └────┬─────┘   └──────────┘
       │              │
       ▼              ▼
  ┌─────────────────────────────────────┐
  │      Persistent Storage (OSS)       │
  │                                     │
  │  user_001/                          │
  │  ├── v3 (latest)  ─ 2026-03-15     │
  │  ├── v2          ─ 2026-03-14     │
  │  └── v1          ─ 2026-03-12     │
  │  user_002/                          │
  │  ├── v5 (latest)  ─ 2026-03-15     │
  │  └── ...                            │
  └─────────────────────────────────────┘
```

### 6.4 文件版本化存储流程

**完整生命周期：**

```
用户请求 (带 user_id)
    │
    ▼
Control Plane 查找
    │
    ├─ [有活跃沙箱] → 直接转发到 sandbox_ip:8765
    │
    └─ [无] → 从空闲池分配沙箱
               │
               ├─ ① 从 OSS 拉取该用户最新文件快照
               ├─ ② 解压到 ~/.claude/ 和 ~/workspace/
               ├─ ③ 启动 HTTP 服务，等待 health check
               ├─ ④ 记录 user_id → sandbox_ip 映射
               └─ ⑤ 转发请求

用户使用中...
Claude 读写文件，记忆持续积累...
闲置超时 / 主动销毁
    │
    ▼
    ├─ ⑥ 计算文件差异（增量 diff / rsync --dry-run）
    ├─ ⑦ 上传变更文件至 OSS
    ├─ ⑧ 记录新版本号（数据库）
    └─ ⑨ 释放沙箱，回归空闲池
```

### 6.5 版本管理数据模型

```sql
CREATE TABLE user_snapshots (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id     VARCHAR(64) NOT NULL,
    version     INT NOT NULL,
    storage_key VARCHAR(256) NOT NULL,   -- OSS路径 snapshots/user_001/v3.tar.gz
    file_count  INT,                      -- 文件数量
    total_size  BIGINT,                   -- 快照总大小
    created_at  TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_version (user_id, version DESC)
);
```

### 6.6 沙箱生命周期管理

| 阶段 | 行为 |
|------|------|
| **按需分配** | 首次请求时从空闲池取实例，拉取文件快照后提供服务。池空时触发新实例创建 |
| **闲置回收** | 无请求超过阈值（如 30 分钟）→ 回写快照 → 清理用户数据 → 回归池 |
| **主动释放** | 用户 API 关闭沙箱 → 同样触发快照保存 |
| **定期清理** | 超过 30 天未使用的快照归档或清理 |

### 6.7 请求路由示例

```python
import httpx

async def query_claude(user_id: str, prompt: str) -> AsyncIterator[dict]:
    """通过 Control Plane 路由到用户专属沙箱"""
    sandbox_url = await control_plane.get_or_create_sandbox(user_id)
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST", f"{sandbox_url}/v1/query/stream",
            json={"prompt": prompt},
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    yield json.loads(line[6:])
```

### 6.8 方案优势

| 优势 | 说明 |
|------|------|
| **彻底的隔离性** | 独立文件系统 + 进程空间 + 网络栈，不存在串扰的可能。相比逐一识别 Claude Code 散布的状态文件，容器级隔离一刀切解决问题 |
| **状态永不丢失** | 一切工作成果——记忆、代码、配置、会话历史——以快照形式持久化在 OSS |
| **资源弹性伸缩** | 沙箱实例无状态，活跃用户少时少量实例，高峰期扩大池。闲置用户不占计算资源 |
| **天然版本回溯** | 每次回收生成新版本，Claude 写坏代码或误删文件时可回滚到任意历史版本——为自动化操作提供"安全网" |

---

### 6.9 官方 SDK 补充方案：SessionStore 适配器

本文方案以文件版本化（tar 快照 + OSS 存储）实现用户状态持久化。但 Anthropic 官方提供了另一种更适合**会话级**持久化的方案——`SessionStore` 适配器。

#### SessionStore 接口

默认 SDK 将会话记录写到 `~/.claude/projects/` 下的 JSONL 文件。`SessionStore` 允许你将会话镜像到 S3、Redis 或数据库，实现跨主机恢复：

| 方法 | 必填 | 调用时机 |
|------|------|----------|
| `append(entry)` | 是 | 每次本地写入一批会话记录后调用 |
| `load(sessionKey)` | 是 | 通过 `resume` 参数恢复会话时调用。返回 `null` 表示未知会话 |
| `listSessions()` | 否 | 被 `listSessions()` 和 `query()`/`startup()` 的 `continue: true` 调用 |
| `delete(sessionKey)` | 否 | 被 `deleteSession()` 调用。删除主 key 必须级联删除所有子 key |
| `listSubkeys(sessionKey)` | 否 | 恢复时发现子代理会话记录。省略则只恢复主会话 |

#### 官方参考实现

Anthropic 在 TypeScript SDK 仓库中提供了三个参考适配器：

| 适配器 | 后端 | 存储模型 |
|--------|------|----------|
| S3SessionStore | `@aws-sdk/client-s3` | 每次 `append()` 产生一个 JSONL part 文件；`load()` 列出、排序、合并 |
| RedisSessionStore | `ioredis` | 每条会话使用 `RPUSH`/`LRANGE` 列表 + sorted-set 会话索引 |
| PostgresSessionStore | `pg` | 每条记录一行，`BIGSERIAL` 排序，`jsonb` 列存储 |

#### 与本方案的关系

```
┌──────────────────────────────────────────────┐
│           用户状态持久化全景                    │
│                                              │
│  文件级持久化（本方案）   会话级持久化（官方）   │
│  ────────────────        ────────────────    │
│  • ~/.claude/ 全部快照    • 仅会话 JSONL      │
│  • 按用户 tar 打包        • S3/Redis/DB       │
│  • 支持版本回滚            • 跨主机恢复会话     │
│  • 容器创建/销毁时触发     • 每次 query 自增   │
│                                              │
│  最佳实践：两者结合                             │
│  文件快照 ≈ 每周全量备份                        │
│  SessionStore ≈ 实时增量同步                   │
└──────────────────────────────────────────────┘
```

**推荐策略：** 文件快照 + SessionStore 双轨制。文件快照处理全量用户状态恢复；SessionStore 保存会话历史，支持用户从上次中断处继续对话。

---

### 6.10 官方文件回滚：Checkpointing

除外部 OSS 版本管理外，Claude Code SDK 内置了文件检查点（checkpointing）功能，用于快速回滚文件变更：

| 方法 | 说明 |
|------|------|
| `checkpoint()` | 创建当前工作目录和 `~/.claude/` 的快照（基于 git）|
| `restoreCheckpoint()` | 恢复到最近的检查点状态 |

**典型用法：**

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// 在危险操作前创建检查点
await checkpoint();

// 执行可能出错的变更
const result = await query("重构 auth 模块");

// 如果结果不理想，回滚
if (result.status === "error") {
  await restoreCheckpoint();
}
```

**常见模式：**
- **危险操作前检查点**：在 `PreToolUse` Hooks 中，对 `Write|Edit|Delete` 等操作触发 `checkpoint()`
- **多重恢复点**：保留多个检查点，支持逐层回退

**和 OSS 快照的关系：** Checkpointing 用于**运行中的快速回滚**（秒级）；OSS 快照用于**容器生命周期级的持久化**（分钟级）。两者互补，建议同时启用。

---

### 6.11 官方沙箱模式：Claude Code 内置 sandboxing

除云端方案的 Docker 沙箱外，Claude Code 本身提供了内置 sandboxing 功能。了解这一机制有助于理解云端方案的边界和替代方案。

#### 技术实现

| 平台 | 技术 |
|------|------|
| macOS | Seatbelt 框架（内置，无需安装）|
| Linux / WSL2 | bubblewrap（文件系统隔离）+ socat（网络代理）|
| Windows | 不直接支持，需在 WSL2 中运行 |

#### 两种模式

| 模式 | 行为 |
|------|------|
| **Auto-allow 模式** | 沙箱内的 Bash 命令自动允许，不触发权限确认。无法沙箱化的命令（需访问未允许的主机）回退到常规权限流程 |
| **Regular 权限模式** | 所有 Bash 命令走常规权限流程，即使已在沙箱内运行 |

两种模式下，文件系统和网络限制完全相同，区别仅在于沙箱内命令是否需要手动批准。

#### 安全逃逸（Escape hatch）

当命令因沙箱限制失败时，Claude 会分析失败原因，并可能使用 `dangerouslyDisableSandbox` 参数重试（会触发用户确认）。可通过 `"allowUnsandboxedCommands": false` 彻底禁用此逃逸机制，实现严格沙箱模式。

#### 文件系统限制

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "allowWrite": ["~/.kube", "/tmp/build"]
    }
  }
}
```

默认沙箱内命令只允许写入当前工作目录。上例允许写入 `~/.kube` 和 `/tmp/build`。路径前缀解析规则：
- `/` → 绝对路径
- `~/` → 相对于 `$HOME`
- `./` 或无前缀 → 对于项目设置相对于项目根，对于用户设置相对于 `~/.claude`

#### 与云端 Docker 沙箱的对比

| 维度 | Claude Code 内置沙箱 | 云端 Docker 沙箱（本方案） |
|------|---------------------|--------------------------|
| 隔离级别 | 进程级（bubblewrap） | 容器级（Docker）|
| 网络隔离 | 基于 socat 代理 | 独立网络命名空间 |
| 文件系统 | 基于 mount namespace | 独立文件系统 |
| 适用场景 | 单机安全执行 | 多用户云端隔离 |
| 部署复杂度 | 低（apt install） | 中（Docker/Orchestration）|
| 是否跨用户 | 否（单用户） | 是 |

**结论：** 两种沙箱并非互斥。在云端每个用户的 Docker 容器内，仍可启用 Claude Code 内置沙箱作为第二层防护（纵深防御）。

---

## 七、总结：三个问题的答案

| 问题 | 方案 | 关键点 |
|------|------|--------|
| **离线部署** | `npm pack` + Docker 基础镜像 | 一次打包处处部署，无需外网 |
| **服务化输出** | Claude Agent SDK + FastAPI + SSE | 支持流式单次查询和多轮会话，保留全部高级特性（Subagents / MCP / Hooks）|
| **多用户隔离** | 一用户一沙箱 + 文件版本化存储 | 容器级隔离彻底解决问题，文件版本化让沙箱变为无状态节点 |

**设计原则：** 尽量不改造 Claude Code 本身，只在外围做封装和调度。Claude Code 升级时只需更新基础镜像中的 tgz 包，HTTP 服务和调度层基本不需改动。

### 感悟

> "AI 的合理利用对研发提效很大。这个项目从 Claude Code 部署调研→方案设计→重构 SDK→基础镜像构建→沙箱部署→本文撰写，仅耗时 1.5 人日及 1909 Credits。"
>
> "但：个人的工程设计能力始终是借助 AI 高效产出的基础，合理的设计思路才能快速引导 AI 构建高质量系统。"

---

## 八、官方推荐部署架构与安全实践

本节基于 Anthropic 官方文档，补充生产级部署的架构模式和安全最佳实践。

### 8.1 官方四种部署模式

Anthropic 在 Hosting 文档中将 Agent SDK 的生产部署归纳为四种模式，每种对应不同的场景需求：

#### 模式一：Ephemeral Sessions（短生命周期）

每次任务创建新容器，完成后销毁。

**特点：**
- 每个用户任务独立容器，零状态残留
- 任务完成后立即释放资源
- 用户可在任务执行过程中继续交互

**适合场景：**
- Bug 调查与修复：提供上下文后自动调试
- 发票/文档处理：提取结构化数据
- 翻译任务：批量文档翻译
- 图片/视频处理：编解码、元数据提取

**最小资源配置：** 1GiB RAM、5GiB 磁盘、1 CPU（基础要求）

#### 模式二：Long-Running Sessions（长生命周期）

维护持久性容器实例，单容器内可运行多个 Claude Agent 进程。

**特点：**
- 容器常驻，Agent 进程按需创建
- 适合需要自主运行的 Agent
- 适合高频消息处理

**适合场景：**
- 邮件 Agent：监控收件箱，自主分类/回复
- 网站构建器：托管自定义网站，实时编辑
- 高频聊天机器人：处理 Slack/Telegram 等持续消息流

#### 模式三：Hybrid Sessions（混合模式）

Ephemeral 容器 + 状态补水：启动时从数据库或 SessionStore 加载历史，任务完成后销毁。

**特点：**
- 短生命周期容器的成本优势 + 长会话的连续体验
- 通过 SDK 的 `resume` 功能加载会话历史
- 用户间歇性参与，容器在空闲时释放

**适合场景：**
- 项目管理助手：间歇性沟通，维护任务和决策上下文
- 深度研究：执行数小时研究任务，保存中间结果
- 客服 Agent：处理跨多轮交互的工单

> **这是本方案「一用户一沙箱 + 文件版本化」对应的官方模式。** 用户状态以文件快照 + SessionStore 形式持久化，容器按需创建销毁。

#### 模式四：Single Containers（单容器多 Agent）

一个全局容器运行多个 Claude Agent SDK 进程。

**特点：**
- 多个 Agent 紧密协作
- 需特别注意文件竞争

**适合场景：**
- 多 Agent 模拟（如游戏场景）

---

### 8.2 官方建议的沙箱提供商

如不希望自建容器编排，官方文档推荐以下托管沙箱提供商：

| 沙箱提供商 | 特点 | 适用场景 |
|-----------|------|----------|
| [Modal Sandbox](https://modal.com/docs/guide/sandbox) | 无服务器沙箱，按秒计费 | Serverless 任务执行 |
| [Cloudflare Sandboxes](https://github.com/cloudflare/sandbox-sdk) | 全球边缘网络 | 低延迟场景 |
| [Daytona](https://www.daytona.io/) | 开发环境即服务 | 容器化开发环境 |
| [E2B](https://e2b.dev/) | 专为 AI Agent 设计的沙箱 | AI 代码执行沙箱 |
| [Fly Machines](https://fly.io/docs/machines/) | 按需启动的轻量级虚拟机 | 地理分布部署 |
| [Vercel Sandbox](https://vercel.com/docs/functions/sandbox) | 与 Vercel 生态集成 | Edge Functions 执行 |

**自托管选项：** Docker（最灵活）、gVisor（更强隔离）、Firecracker（微 VM，AWS Lambda 底层技术）

---

### 8.3 安全部署原则

对于需要额外加固的生产部署，官方建议遵循三大安全原则：

#### 安全边界（Security Boundaries）

不同信任级别的组件之间应用安全边界分隔。敏感资源（如 API Key）应放在 Agent 环境之外：

```
┌─────────────────────┐
│     Agent 容器       │  ← 低信任区域
│  Claude Agent        │
│  接受用户输入        │
└──────┬──────────────┘
       │ 只能发出请求，无法读取凭证
       ▼
┌─────────────────────┐
│    代理服务           │  ← 高信任区域
│  注入 API Key        │
│  请求过滤/审计       │
│  速率限制            │
└─────────────────────┘
       │
       ▼
  ┌───────────┐
  │外部API服务 │
  └───────────┘
```

例如：在 Agent 容器外运行一个代理 Proxy，Proxy 为请求注入认证信息。Agent 可以进行 API 调用，但永远看不到原始凭证。

#### 最小权限（Least Privilege）

| 资源 | 限制方式 |
|------|----------|
| 文件系统 | 仅挂载必要目录，优先只读 |
| 网络 | 通过代理限制到特定端点 |
| 凭据 | 通过 Proxy 注入，而非直接暴露 |
| 系统能力 | 容器内 Drop Linux capabilities |

#### 纵深防御（Defense in Depth）

避免依赖单层防护。多层安全叠加，即使某一层被绕过仍然安全：

```
第一层：Permission Rules（Claude Code 内置）
  └─ 允许 / 拒绝 / 询问具体的工具和命令

第二层：Sandbox（Claude Code 内置）
  └─ bubblewrap 进程级文件系统/网络隔离

第三层：Docker 容器
  └─ 独立文件系统 + 网络命名空间

第四层：网络代理（外部）
  └─ 限制出站到白名单 API 端点

第五层：Hooks + 审计
  └─ PreToolUse 验证 → PostToolUse 审计
```

---

### 8.4 容器运维 Q&A（官方 FAQ）

| 问题 | 回答 |
|------|------|
| **如何与沙箱通信？** | 暴露容器端口，应用层通过 HTTP/WebSocket 与内部 SDK 实例通信 |
| **托管容器成本？** | Token 是主要开销。容器本身约 $0.05/hr |
| **闲置容器何时关闭？** | 取决于沙箱提供商配置。建议根据用户响应频率调整超时 |
| **Claude Code CLI 更新频率？** | 遵循 semver，破坏性更新会标记大版本。建议 CI/CD 中定期更新基础镜像 |
| **如何监控容器健康？** | 标准后端监控工具即可（Prometheus + Grafana / Datadog 等）|
| **Agent 会话超时？** | Agent 会话不会超时。但应设置 `max_turns` 防止无限循环 |

---

## 九、知识关联

| 关联文档 | 关联点 |
|---------|--------|
| `agent-engineering/harness/agent-harness-engineering.md` | Harness Engineering 概念基础 |
| `agent-engineering/harness/build-your-own-mcp-server.md` | MCP 服务器集成 |
| `agent-engineering/harness/agent-sandbox-infrastructure.md` | 沙箱基础设施 |
| `agent-engineering/harness/harness-from-theory-to-practice.md` | Harness 从理论到实践 |
| `agent-engineering/harness/skillify-skill-engineering-guide.md` | Skills/Hooks 体系 |
| `agent-engineering/patterns/openclaw-vs-hermes-agent-memory-architecture.md` | Agent 记忆架构——SessionStore 持久化与记忆模型的对比参考 |
| `spring-ai/from-assistants-to-agents-self-improving-agentic-systems.md` | Agent Loop 架构的不同实现对比（Spring AI vs Claude SDK）|

### 参考资料

本文补充内容的官方来源：

- [Agent Loop 工作原理](https://docs.anthropic.com/en/docs/agent-sdk/agent-loop)
- [Agent SDK Hosting 部署指南](https://docs.anthropic.com/en/docs/claude-code/agent-sdk/hosting)
- [Secure Deployment 安全部署](https://docs.anthropic.com/en/docs/claude-code/agent-sdk/secure-deployment)
- [SessionStore 外部存储](https://docs.anthropic.com/en/docs/claude-code/agent-sdk/session-storage)
- [File Checkpointing 快照回滚](https://docs.anthropic.com/en/docs/claude-code/agent-sdk/file-checkpointing)
- [Sandboxing 沙箱配置](https://docs.anthropic.com/en/docs/claude-code/sandboxing)
- [Permission Modes 权限模式](https://docs.anthropic.com/en/docs/claude-code/permission-modes)
- [Subagents 子代理](https://docs.anthropic.com/en/docs/claude-code/agent-sdk/subagents)
- [Hooks 钩子系统](https://docs.anthropic.com/en/docs/claude-code/agent-sdk/hooks)

---

*本文整理自阿里开发者公众号付费文章，描述了将 Claude Code 改造为云端 HTTP 流式服务并实现多用户隔离的完整工程方案。*
