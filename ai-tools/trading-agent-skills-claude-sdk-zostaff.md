---
title: "Developing Skills for a Trading Agent — Plus Claude Agent SDK Step-by-Step Enhancement Guide"
tags:
  - claude-agent-sdk
  - trading-agent
  - custom-tools
  - hooks
  - subagent
  - mcp
  - safety
  - skills
date: 2026-06-05
source: "https://x.com/zostaff/status/2062855497913450793"
authors: "zostaff (@zostaff)"
series: "claude-agent-sdk"
---

# 为交易 Agent 开发技能：教 Agent 新能力

> **来源：** X.com 长文 by zostaff  
> **发布时间：** 2026-06-05  
> **数据：** 20 ❤️ · 1 🔁 · 5 💬

---

## 一、核心认知：Tool 与 Skill 是两回事

> "A custom tool is about action. A skill is about knowledge."

Claude 生态两个不同机制，选择决定了后续一切：

| 机制 | 本质 | 类比 |
|------|------|------|
| **Custom Tool** | 函数——agent 在对话中调用，定义 contract（操作+返回值） | **手** |
| **Skill** | 自包含文件夹 + SKILL.md——存知识和规则，按描述匹配加载 | **规则书** |

- Tool 给 agent **操控能力**：计算、调 API、写数据库
- Skill 给 agent **领域知识**：我们的基金如何计算仓位、风控规则、下单前流程
- 强壮的 agent **两者都要**——先做 tool，因为没手规则书是死的

---

## 二、Skill 1：给 Agent 一双手（Custom Tool via In-Process MCP Server）

```python
@tool(
    name="size_by_volatility",
    description="Calculate position size based on current volatility and stop distance. "
                "Use this when you need to size a position before submitting an order.",
    input_schema={
        "type": "object",
        "properties": {
            "account_equity": {"type": "number", "description": "Current account equity in USD"},
            "risk_per_trade": {"type": "number", "description": "Risk per trade as decimal (e.g. 0.01 for 1%)"},
            "stop_distance_pct": {"type": "number", "description": "Stop distance in percentage"},
        },
        "required": ["account_equity", "risk_per_trade", "stop_distance_pct"]
    },
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def size_by_volatility(args):
    if args["stop_distance_pct"] <= 0:
        return {"content": [{"type": "text", "text": "Error: stop_distance must be positive"}]}
    position_size = (args["account_equity"] * args["risk_per_trade"]) / (args["stop_distance_pct"] / 100)
    return {"content": [{"type": "text", "text": f"Position size: ${position_size:.2f}"}]}
```

**三个注意点：**
1. **Tool description 不是形式**——agent 凭这段文字决定何时调用，必须具体
2. **参数 schema 要带类型**——agent 不猜格式
3. **需要 error branch**——无效输入返回错误文本而非崩溃，agent 读到后可以反应

**Annotations 的作用（常被低估）：**
- `readOnlyHint: True` — 不改变状态，安全
- `destructiveHint: True` — 改变世界状态，如发送订单（需区别对待）

**连接到 Agent：**
```python
options = ClaudeAgentOptions(
    mcp_servers=[server],  # 用 create_sdk_mcp_server 打包 tool
    allowed_tools=[
        "mcp__my_server__size_by_volatility",
        # 格式: mcp__{server}__{tool}
    ]
)
```

`allowed_tools` 是生产环境的**主控制杠杆**——严格控制 agent 被允许做什么。

---

## 三、Skill 2：给 Agent 一本规则书（Skill）

创建 skill 文件夹 + SKILL.md，agent 在任务匹配 description 时加载：

```markdown
---
description: >
  Our fund's risk management rulebook. Use this when sizing positions,
  setting stops, or checking exposure limits.
---

# Risk Rulebook - [Fund Name]

## Position Sizing
- Maximum 2% risk per trade on account equity
- Use volatility-based sizing for directional positions
- Reduce size by 50% during major news events (CPI, FOMC, NFP)

## Stop Loss Rules
- Set initial stop at 1.5x ATR
- Never risk more than 1% on any single position
- Trailing stop activates after 2x initial risk is in profit

## Exposure Limits
- Maximum sector exposure: 25% of portfolio
- Maximum correlated pair exposure: 15%
- Gross exposure limit: 200% of NAV
```

**SDK 中加载 Skill（与 Claude Code CLI 不同）：**
```python
options = ClaudeAgentOptions(
    setting_sources=["/path/to/skills/"],  # 必须显式开启 skill 发现!
    allowed_tools=[...],
)
```

**两个容易掉坑的地方：**
1. 默认 SDK **既不找 settings 文件也不找 skills**——必须通过 `setting_sources` 启用
2. SKILL.md frontmatter 中的 `allowed-tools` 字段**仅 Claude Code CLI 有效**，SDK 中通过 `allowed_tools` 在 query config 中控制

---

## 四、Skill 3：Agent 无法绕过的安全层（Hook）

规则书是指令，模型在巧妙 prompt 或误判下原则上可以**忽略**。涉及钱的时候不够。

**Hook 是在代码层触发、agent 物理上无法绕过的保险丝。**

### 关键 Hook：PreToolUse

```python
async def drawdown_fuse(input_data, tool_use_id, context):
    """PreToolUse: 如果 drawdown 低于阈值，阻止下单"""
    tool_name = input_data.get("tool_name", "")
    if tool_name != "mcp__trading__submit_order":
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}

    portfolio_state = get_portfolio_state()  # 从实际状态读取，不走缓存
    if portfolio_state["drawdown_pct"] < -8.0:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Drawdown {portfolio_state['drawdown_pct']:.1f}% exceeds max -8.0%"
            }
        }
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}
```

**指令 vs 保险丝：**
- **Skill → "drawdown 低于 -8% 别进场"** ← 政策（agent 应自行遵守）
- **Hook → drawdown 低于 -8% 时下单**物理上无法执行** ← 保险丝

**PreToolUse 的三种权限决策：**
```python
# 允许
permissionDecision: "allow"
# 拒绝
permissionDecision: "deny"
# 人机协同: agent 停下来等人类确认
permissionDecision: "ask"
```

**接线：**
```python
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="mcp__trading__submit_order", hooks=[drawdown_fuse]),
        ],
    }
)
```

---

## 五、Skill 4：委托（Subagent）

任务拆成子任务时，一个 agent 管十几个工具会开始混乱。解法：**subagent**。

**三个关键点（否则静默失败）：**
1. **Fresh context** — subagent 从零上下文开始。prompt 是 parent 到 child 的唯一通道，必须把所有需要的东西打包进去（文件路径、前置决策、数字）
2. **并行性** — 多个 subagent 可同时运行，例如同时拉价格/新闻/基本面
3. **无权限继承** — subagent 不自动获得 parent 的权限，通过 PreToolUse hooks 或 permission rules 分别控制

```python
options = ClaudeAgentOptions(
    subagents=[
        AgentDefinition(
            name="research-agent",
            description="Researcher for ticker fundamentals and news",
            prompt="You are a research analyst. Given a ticker, gather price data, "
                   "recent news, and fundamentals. Return a concise summary.",
            tools=["WebSearch", "WebFetch", "Read"],
            model="haiku",  # 子任务用更快的模型
        )
    ],
)
```

**主 agent 保持干净的战略家角色：** 把研究委派给 subagent，接收摘要后做决策，不被原始数据淹没。

---

## 六、为什么不用全塞进 System Prompt？

| | System Prompt | Skill |
|--|--|--|
| 加载方式 | 每个请求都加载 | 仅任务匹配时加载 |
| Token 成本 | 永远燃烧 | 按需燃烧 |
| 修改方式 | 改代码 | 改 markdown 文件即可 |
| 可移植性 | 绑定一个 agent | 任意 agent 可共享 |

> "One rulebook, many agents."

---

## 七、真实资金上才会暴露的 3 个 Bug

### Bug 1：检查和执行间的竞态

Hook 读到 drawdown = -7%，放行。订单飞往 broker 途中市场急跌，drawdown 突破 -8%。检查基于**过时快照**通过。

**修复：** Hook 不读缓存，而是在决策瞬间**加锁读实际状态**；同时在执行侧也放一层最终限制检查，不止在 hook 里。

### Bug 2：重试导致的重复

Agent 发了订单 → 网络抖动 → 响应没回来 → agent 认为 tool 失败 → 重试 → 仓位开了两次。

**修复：幂等键（idempotency key）——基于意图+时间戳生成确定性标识符：**
```python
idempotency_key = f"{intent_hash}_{bar_timestamp}"
# 不能用发送时间——否则延迟一秒重试就生成新 key
```

Broker 拒掉重复 key。

### Bug 3：决策不透明

在真实资金上出错后，第一个问题是**"它为什么这么做"**。如果答案不在日志里就瞎了。

**修复：PostToolUse hook 写结构化追踪：**
```python
async def audit_trail(input_data, tool_use_id, context):
    # 记录: 调了什么工具、参数是什么、返回值、当时 portfolio 状态
    # 不要写纯文本到控制台，写机器可读的记录用于事后重建
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool_name": input_data["tool_name"],
        "tool_input": input_data["tool_input"],
        "portfolio_state": get_portfolio_state(),
    }
    append_to_audit_log(log_entry)
    return {}
```

**共同原则：** 模型负责**意图**，代码负责**意图恰好执行一次、基于最新数据、留下记录**。

---

## 八、马上可以建的 4 层技能集

一个可实战的最小交易 agent skill set = 四种机制各一层：

| 层 | 机制 | 作用 | 类比 |
|----|------|------|------|
| 1 | Custom Tool | 计算仓位 | **手** |
| 2 | Skill | 风险规则书 | **知识** |
| 3 | PreToolUse Hook | 下单 fuse | **保险丝** |
| 4 | Subagent | 研究委派 | **委托** |

**验证顺序（按复杂度递增）：**
1. **测手+规则书：** "帮我计算 AAPL 的合适仓位，波动率 2%，止损 5%"
2. **测 fuse：** "买入 100 股 MSFT"（drawdown 低于阈值 → hook 阻止）
3. **测委托：** "分析 TSLA 全貌并给出仓位建议"（好 agent 会自己委派给 research subagent）

---

# 附：Claude Agent SDK 增强开发指南（Step by Step）

以下为 sopra 的教程内容与官方 SDK 资料整理的综合实操指南。

---

## Step 0：安装与环境

```bash
# Python SDK
pip install claude-agent-sdk
export ANTHROPIC_API_KEY="sk-ant-..."

# Node.js / TypeScript SDK
npm install -g @anthropic-ai/claude-code
npm install @anthropic-ai/claude-agent-sdk
```

**版本要求：** Python 3.10+ / Node.js 18+  
**模型：** 推荐 Claude Opus 4.5（复杂推理）、Sonnet 4（平衡）、Haiku（子任务/快速）

---

## Step 1：理解两个核心接口

### query() — 简单、无状态

```python
from claude_agent_sdk import query
import anyio

async def main():
    async for message in query(
        prompt="Read the file config.yaml and summarize its contents",
        options={"permission_mode": "default", "max_turns": 10}
    ):
        if message.type == "assistant":
            print(message.content)

anyio.run(main)
```

### ClaudeSDKClient — 有状态、多轮会话

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def main():
    options = ClaudeAgentOptions(permission_mode="acceptEdits", max_turns=25)
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Refactor the utils module to use dataclasses")
        async for msg in client.receive_response():
            if msg.type == "assistant":
                print(msg.content)
```

区别：`query()` 是 fire-and-forget，`ClaudeSDKClient` 在会话中维持状态。

---

## Step 2：构建 Custom Tool（完整模式）

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool(
    name="query_database",
    description="Execute a read-only SQL query against the application database",
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "SQL SELECT query to execute"}
        },
        "required": ["query"]
    }
)
async def query_database(args):
    sql = args["query"]
    # 验证只读
    if not sql.strip().upper().startswith("SELECT"):
        return {"content": [{"type": "text", "text": "Error: Only SELECT queries are allowed"}]}
    results = await db.execute(sql)
    return {"content": [{"type": "text", "text": str(results)}]}

# 注册
server = create_sdk_mcp_server(name="app-tools", version="1.0.0", tools=[query_database])
options = ClaudeAgentOptions(
    mcp_servers=[server],
    allowed_tools=["mcp__app-tools__query_database", "Read", "Grep"],
)
```

### Tool 命名约定

SDK 中 tool 的引用名格式：`mcp__{server-name}__{tool-name}`

### Annotations 完整字段

| 字段 | 含义 | 建议 |
|------|------|------|
| `readOnlyHint` | 不修改任何状态 | 查询类设为 True |
| `destructiveHint` | 执行不可逆操作 | 删除/写入类设为 True |
| `idempotentHint` | 相同输入始终产生相同结果 | 纯计算类设为 True |
| `openWorldHint` | 与外部系统通信 | 网络调用类设为 True |

---

## Step 3：安全 Hooks（生产必备）

### 可用 Hook 事件

| 事件 | 触发时机 | 用途 |
|------|---------|------|
| PreToolUse | tool 执行前 | 允许/拒绝/修改 |
| PostToolUse | tool 返回后 | 审计日志、注入上下文 |
| PostToolUseFailure | tool 执行失败 | 告警、fallback |
| UserPromptSubmit | 用户提交 prompt | prompt 审查 |
| SubagentStart / SubagentStop | subagent 启停 | 监控、计费 |
| PermissionRequest | 需要权限决策 | 自定义审批流 |
| Stop | agent 执行完毕 | 清理、报告 |

### 使用 HookMatcher 精确匹配

```python
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            # 只对 Bash tool 生效
            HookMatcher(matcher="Bash", hooks=[validate_bash_command], timeout=120),
        ],
        "PostToolUse": [
            # 无 matcher = 全局生效
            HookMatcher(hooks=[audit_log_tool_use]),
        ],
    }
)
```

### PreToolUse 返回格式

```python
# 允许
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}
# 拒绝
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
  "permissionDecisionReason": "..."}}
# 修改输入（替换掉原参数）
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "modify",
  "modifiedToolInput": {...}}}
```

---

## Step 4：Subagent 实战模式

### 定义 subagent

```python
from claude_agent_sdk import ClaudeAgentOptions, AgentDefinition

options = ClaudeAgentOptions(
    subagents=[
        AgentDefinition(
            name="security-scanner",
            description="Examines code for security vulnerabilities",
            prompt="You are a security expert in Python and web applications...",
            tools=["Read", "Grep", "Glob", "WebSearch"],
            model="sonnet",
        ),
        AgentDefinition(
            name="test-analyzer",
            description="Analyzes test coverage and quality",
            prompt="You are a testing expert...",
            tools=["Read", "Grep", "Glob"],
            model="haiku",  # 子任务用更快的模型省钱
        ),
    ]
)
```

### 消息类型（query 流）

```python
for await message in query({...}):
    if message.type == "system":
        # 初始化信息、可用工具
        ...
    elif message.type == "assistant":
        # Claude 的回复和 tool calls
        ...
    elif message.type == "result":
        # 最终结果，含总消耗
        print(message.subtype)  # "success" 或其他
        print(message.total_cost_usd)
```

### 会话恢复（多轮交互）

```python
# 第一次调用后拿到 session_id
session_id = message.session_id  # 从 system/init 消息拿到

# 后续调用恢复上下文
for await message in query({
    prompt: "Now show me how to fix it",
    options: {resume: session_id, max_turns: 250}
}):
    ...
```

---

## Step 5：permissionMode 全局权限控制

| 模式 | 说明 |
|------|------|
| `default` | 标准模式，每次 tool 调用前询问 |
| `acceptEdits` | 自动批准文件编辑 |
| `bypassPermissions` | 不询问（慎用） |

### 细粒度权限：canUseTool

```python
options = ClaudeAgentOptions(
    canUseTool=async (tool_name, input) => {
        # 读操作全放行
        if ["Read", "Grep", "Glob"].includes(tool_name):
            return { behavior: "allow" }
        # 禁止写 .env 文件
        if tool_name == "Write" && input.file_path?.includes(".env"):
            return { behavior: "deny", message: "Cannot modify .env files" }
        return { behavior: "allow" }
    }
)
```

---

## Step 6：结构化输出（JSON Schema）

```python
options = ClaudeAgentOptions(
    outputFormat={
        "type": "json_schema",
        "schema": {
            "type": "object",
            "properties": {
                "issues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                            "file": {"type": "string"},
                            "line": {"type": "number"},
                            "description": {"type": "string"},
                        },
                        "required": ["severity", "file", "description"]
                    }
                },
                "summary": {"type": "string"},
                "overallScore": {"type": "number"}
            },
            "required": ["issues", "summary", "overallScore"]
        }
    }
)

# 在 result 消息中拿到
message.structured_output  # 直接是解析好的 dict
```

---

## Step 7：常见陷阱

| 陷阱 | 说明 | 解法 |
|------|------|------|
| **AskUserQuestion 静默失败** | 无 TTY 环境（生产）中该 tool 会静默失败 | 用自定义 MCP tool 替代，通过外部通道（Slack/Web）收集输入 |
| **settings.json 权限不继承** | SDK 的 permissionMode 不自动读取 settings.json | 始终在 ClaudeAgentOptions 中显式配置 |
| **Subagent 上下文为空** | subagent 从零上下文开始 | 把所有需要的信息打包进 prompt 字符串 |
| **query() 模式下的 hooks** | query() 不支持 PreToolUse hook 的 modify 输出 | 用 ClaudeSDKClient 获取完整 hook 支持 |

---

## Step 8：框架对比速览

| 框架 | 最佳场景 | 限制 |
|------|---------|------|
| **Claude Agent SDK** | Claude 生态深度绑定、内置工具、Constitutional AI | 锁 Claude 模型 |
| **LangGraph** | 复杂多 agent 工作流、图编排、时间旅行调试 | 学习曲线陡峭 |
| **PydanticAI** | 类型安全、模型无关（支持多 provider） | 功能相对轻量 |

---

## 附录：完整最小 Agent 模板

```python
import anyio
from claude_agent_sdk import (
    ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition,
    tool, create_sdk_mcp_server, HookMatcher
)

# --- 1. Custom Tool ---
@tool(name="my_action", description="Does something useful", input_schema={...})
async def my_action(args):
    return {"content": [{"type": "text", "text": "done"}]}

# --- 2. Safety Hook ---
async def safety_fuse(input_data, tool_use_id, context):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}

# --- 3. Assemble ---
server = create_sdk_mcp_server(name="my-server", version="1.0.0", tools=[my_action])
options = ClaudeAgentOptions(
    mcp_servers=[server],
    allowed_tools=["mcp__my-server__my_action", "Read", "Grep"],
    hooks={"PreToolUse": [HookMatcher(matcher="my_action", hooks=[safety_fuse])]},
    subagents=[AgentDefinition(name="helper", description="...", prompt="...", tools=["Read"])],
    permission_mode="acceptEdits",
    max_turns=50,
)

async def main():
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Your prompt here")
        async for msg in client.receive_response():
            if msg.type == "assistant":
                print(msg.content)

anyio.run(main)
```

---

*整理于 2026-06-05，来自 zostaff X.com 长文 + aiworkflowlab.dev + nader.substack.com 综合补充*
