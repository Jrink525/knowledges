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

### 3.4 注意事项

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

**权限控制（Permission Mode）：**
支持 `default`、`dontAsk`、`acceptEdits`、`bypassPermissions`、`plan` 五种模式。默认设为 `bypassPermissions` 避免无人值守卡死。

**子代理（Subagents）：**
```json
{
  "prompt": "审查并优化代码",
  "agents": {
    "code-reviewer": {
      "description": "代码审查专家",
      "prompt": "关注安全性和最佳实践",
      "tools": ["Read", "Glob", "Grep"]
    }
  }
}
```

**MCP 服务器集成：**
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

**钩子（Hooks）：**
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write|Edit",
      "action": "deny",
      "reason": "禁止写入 .env 文件"
    }],
    "PostToolUse": [{
      "action": "webhook",
      "webhook_url": "https://audit.example.com/log"
    }]
  }
}
```

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

## 八、知识关联

| 关联文档 | 关联点 |
|---------|--------|
| `agent-engineering/harness/agent-harness-engineering.md` | Harness Engineering 概念基础 |
| `agent-engineering/harness/build-your-own-mcp-server.md` | MCP 服务器集成 |
| `agent-engineering/harness/agent-sandbox-infrastructure.md` | 沙箱基础设施 |
| `agent-engineering/harness/harness-from-theory-to-practice.md` | Harness 从理论到实践 |
| `agent-engineering/harness/skillify-skill-engineering-guide.md` | Skills/Hooks 体系 |
| `agent-engineering/patterns/openclaw-vs-hermes-agent-memory-architecture.md` | Agent 记忆架构—记忆持久化的对比参考 |

---

*本文整理自阿里开发者公众号付费文章，描述了将 Claude Code 改造为云端 HTTP 流式服务并实现多用户隔离的完整工程方案。*
