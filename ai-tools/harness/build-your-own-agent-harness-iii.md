---
title: "构建你自己的 Agent Harness：iii 架构深度解析"
tags:
  - agent-harness
  - iii
  - agent-architecture
  - multi-agent
  - agent-engineering
  - open-source
  - agents
date: 2026-05-29
source: "基于 @mfpiccolo 的 X 长文 'How to build your own agent harness?'"
---

# 构建你自己的 Agent Harness：iii 架构深度解析

> **一句话总结**：大多数 Agent 团队没有构建 harness，而是采用一个框架。但框架把十多个独立关注点捆绑成一个单体，这是每个长运行 Agent 团队最终不得不从头重写 harness 的根源。iii 的解法是将 harness 拆解为一组可独立替换的 worker，通过一个共享引擎连接。

---

## 目录

- [一、框架模式的问题](#一框架模式的问题)
- [二、Agent Harness 的 15 个职责](#二agent-harness-的-15-个职责)
- [三、iii 的核心设计哲学](#三iii-的核心设计哲学)
- [四、完整 Worker 栈](#四完整-worker-栈)
- [五、单轮对话的执行流程](#五单轮对话的执行流程)
- [六、构建你自己的 Harness：5 个替换示例](#六构建你自己的-harness5-个替换示例)
- [七、Harness 是一个滑块，不是一个岔路口](#七harness-是一个滑块不是一个岔路口)
- [八、实践建议与资源](#八实践建议与资源)

---

## 一、框架模式的问题

大多数 Agent 团队不构建 harness，他们**采用**一个。LangChain、LangGraph、OpenAI Agents SDK、Anthropic SDK、CrewAI、AutoGen——循环、工具、记忆、编排都作为一个决定从货架上拿来。

如果内部有东西不合适，你就只能 fork、对抗或绕道而行。

作者认为这种**形状是错的**——这就是每个长运行 Agent 团队最终不得不从头重写 harness 的根本原因。Harness 不是一件事，而是**十个或十二个不同的事**捆绑在一起，因为周边生态系统没有给你组合它们的方式。

> **核心论点：** iii 引擎将所有 worker 一视同仁，彻底消除了集成逻辑。提供者路由、凭据库、策略引擎、审批网关、模型目录、会话存储、预算追踪、调用后 hook 扇出、持久化轮次循环——这些是**独立的关注点**。一个把它们打包成一个块的框架，是在向你出售一个你本不必做的权衡。

---

## 二、Agent Harness 的 15 个职责

剥离生产级 Agent Harness 到其核心职责，清单大致如下：

| # | 职责 | 说明 |
|:-:|------|------|
| 1 | **接收轮次请求** | 从客户端接受 turn 请求并持久化 |
| 2 | **解析凭据** | 为调用的模型提供者解析凭证 |
| 3 | **模型能力查询** | 查看选中的模型能做什么（视觉、工具、流式、上下文窗口） |
| 4 | **驱动状态机** | 每个轮次的状态机：准备、流式、运行工具、控制、销毁 |
| 5 | **加载 Skill** | 加载描述函数请求格式、错误码和使用说明的 skill 体 |
| 6 | **组装系统提示** | 系统提示 + 模式段落 + 身份前缀 + 工作目录 + 默认 skill 附录 |
| 7 | **流式返回 tokens** | 模型生成时流式推送回客户端 |
| 8 | **策略检查** | 每个工具调用在执行前都要经过策略检查 |
| 9 | **审批暂停** | 需要人工决策的工具调用暂停并路由回对应轮次 |
| 10 | **预算追踪** | 追踪 LLM 花费，按工作空间或 Agent 预算限制 |
| 11 | **Hook 执行** | 在工具调用前后运行钩子（日志、脱敏、自定义副作用） |
| 12 | **会话持久化** | 将会话保存为分支树，支持 fork 和 resume |
| 13 | **上下文压缩** | 上下文窗口满时压缩会话历史 |
| 14 | **事件流推送** | 发射 UI 订阅的事件流 |
| 15 | **OpenTelemetry 追踪** | **每个公司都在缺失这一步**——每一步都有 OTel trace 以便调试 |

> **关键洞察：** 每个严肃的 Agent harness 大部分都会做。昂贵的全部做。便宜的切角，上生产后重做。框架把它们打包成单体，你一年后发现想要的策略引擎不是框架自带的，而替换它意味着替换整个 harness。

---

## 三、iii 的核心设计哲学

### 3.1 基础原语

iii 的赌注是：**一个原语就够了。**

- 一个通过 WebSocket 连接到引擎的 **Worker**
- 在总线上注册**函数**（functions）和**触发器**（triggers）
- 足够小，能分别吸收上述 15 个职责中的每一个

### 3.2 关键设计决策

| 维度 | 框架模式 | iii Worker 模式 |
|------|---------|----------------|
| 架构 | 单体捆绑 | 拆分为独立 worker |
| 替换 | 替换意味着重写 harness | 替换一个 worker |
| 集成 | 每个新组件需要集成 | 引擎一视同仁，零集成逻辑 |
| 版本 | 同步升级 | 独立版本，可独立升级 |
| 语言 | 框架语言限制 | 任何有 SDK 的语言 |
| 部署 | 单体部署 | 独立进程，各自运行 |

---

## 四、完整 Worker 栈

iii 的 11 个 worker，每个一个职责：

| Worker | 职责 |
|--------|------|
| **harness meta-worker** | 入口网关，分发 turn 请求 |
| **turn-orchestrator** | 核心状态机，驱动每一轮的完整生命周期 |
| **provider-\<name\>** | 模型提供者适配器（Anthropic、OpenAI 等） |
| **models-catalog** | 静态模型能力目录 |
| **auth-credentials** | 文件/密钥管理器的凭据解析 |
| **policy** | 策略引擎（检查工具调用的权限） |
| **approval-gate** | 审批网关（需人工决策的中转） |
| **llm-budget** | LLM 消费预算追踪 |
| **hook-fanout** | 调用后 hook 扇出 |
| **session** | 会话存储与持久化 |
| **context-compaction** | 上下文压缩 |

> **所有 worker 共用同一个引擎总线。每个注册的接口都是一致的，替换任何一个不影响其他组件。**

---

## 五、单轮对话的执行流程

下面是一个完整的 turn 生命周期，按 worker 触发顺序：

### 5.1 入口: harness::trigger

浏览器/CLI/chat 通过 `harness::trigger` POST turn 请求，包含 `{session_id, message_id, payload}`。harness meta-worker 转发 payload 到 `run::start`。

这个跳转的目的是让 **OpenTelemetry span wrapper** 种子 session 和 message ID 作为 baggage，传播到堆栈中每个 worker 的每个 `iii.trigger` 调用。最终的 trace 树是一个连通图。

### 5.2 turn-orchestrator

`run::start` 到达 turn-orchestrator。它：
- 持久化 run 请求
- 在 iii state 中播种初始 `TurnStateRecord`（`session/<sid>/turn_state`）
- 立即返回

实际工作在持久性状态机中发生，由 turn-step FIFO 唤醒。

两个终止状态：
- **stopped**：通过 `finishSession()` 干净退出
- **failed**：意外的 handler throw 路由到这里，ACK 队列停止重试，向 UI 显示错误信息

### 5.3 provisioning（准备阶段）

做三件事：
1. **启动沙箱**：如果需要隔离执行，启动 iii-sandbox microVM
2. **下载 Skill**：调用 `directory::skills::download` 预缓存 skill 体
3. **组装系统提示**：三层结构
   - **Mode 段落**：从 `run_request.mode` 选取（plan / ask / agent）
   - **iii 身份前缀**：教导模型 `agent_trigger` 约定和 `directory::skills::get` 按需发现模式
   - **默认 Skill 索引**：Agent 启动时加载的默认 skill

> **调用方覆盖：** 可在 `run::start` 传入 `system_prompt` 覆盖整个提示。

### 5.4 assistant_streaming（流式响应）

调用 `provider::<name>::stream`（匹配 run 的 provider 字段）。provider worker：
- 通过 `auth::get_token` 拉取凭证
- 将模型的 SSE 响应流式送入 **iii channel**
- orchestrator 从 channel 读取，发射 `message_update` 事件到 `agent::events` 供 UI 消费

### 5.5 function_execute（工具调用执行）

当 assistant 返回工具调用时，FSM 进入 `function_execute`。

#### 策略检查

每个工具调用通过 `dispatchWithHook` —— orchestrator 中的**单一瓶颈点**。`consultBefore` 调用 `policy::check_permissions`（5 秒超时）。

策略 worker 读取 `iii-permissions.yaml`，匹配 `function_id` 并返回三种结果之一：

| 结果 | 动作 |
|------|------|
| **allow** | 放行，orchestrator 触发目标函数并写结果 |
| **deny** | 短路返回 `DenialEnvelope` |
| **needs_approval** | 调用进入等待审批列表，其他调用继续执行 |

**安全设计：**
- 策略 worker 不可达或超时 → 返回 `gate_unavailable` 信封（**fail-closed**）
- 引擎 publish 自身出错 → 视为 deny

#### 审批机制

- 当有调用等待审批时，turn 转入 `function_awaiting_approval` 状态
- orchestrator 注册单个 `turn::on_approval` 状态触发器
- 当控制台调用 `approval::resolve`，approval-gate worker 写 `approvals/<sid>/<cid> = {decision, reason}`
- 该写操作触发 `turn::on_approval`，推进对应 session
- **无需每个调用注册恢复函数，无需启动时重新扫描恢复审批**

### 5.6 steering_check（转向决策）

本轮工具调用批次完成后，决定下一步：
- **continue** → 回到 `assistant_streaming`
- **stop** → 运行 `finishSession()`：发射 `agent_end`，释放沙箱，转入 `stopped`
- **max_turns** → 同 stop

### 5.7 延迟优化

| 优化 | 效果 |
|------|------|
| **hook publish 短路** | 无 durable subscriber 时跳过，省 ~500ms/调用 |
| **teardown 内联** | `finishSession()` 内联，省一次队列跳转 |
| **上下文压缩按 turn 触发** | 订阅 `agent::turn_end` 流，不是每个事件 |
| **session-create 状态触发器** | 进程内匹配，去掉之前的 RPC 调用 |

### 5.8 可观测性

每个参与的 worker 发射带 `iii.session.id`、`iii.message.id`、`iii.function.id` 标签的 OTel span。引擎的 `engine::traces::group_by` 读取这些标签来支持按 Session/Message/Function 分组。

> **Instrumentation 是自动的**：`src/runtime/worker.ts` 将每个 `registerFunction` 包装在 Proxy 中，不需要每个 worker 记住添加 span。

---

## 六、构建你自己的 Harness：5 个替换示例

iii 中"构建你自己的 harness"分解为"写任何 worker"相同的操作：选择要替换的层，写一个在总线上注册相同函数的 worker，用 `iii worker add` 添加，堆栈其他部分自动使用你的 worker。

### 示例 1：用实时 API 替换模型目录

```typescript
// 写一个 worker 注册 models::list, models::get, models::supports
// 从提供者的 catalog endpoint 获取，N 分钟缓存
// iii worker add your-org/dynamic-models-catalog
// 停止静态 models-catalog worker
// turn-orchestrator 调用 iii.trigger('models::list') → 路由到你的 worker
```

### 示例 2：添加新的模型提供者

`provider-kimi` 和 `provider-lmstudio` 已经是现成的模式。每个 worker：
1. 注册 `provider::<name>::stream` 和 `provider::<name>::complete`
2. 将上游 API 的 SSE 流排入 channel
3. 通过 `budget::record` 记录使用量

**添加第五个提供者 = 写一个文件夹（iii.worker.yaml + register.ts）**。

### 示例 3：从私有存储提供 Skill

```typescript
// 注册 directory::skills::get 和 directory::skills::list
// 后端指向内部文档系统或私有 S3 bucket
// 断开默认的 iii-directory worker
// orchestrator 的 bootstrap 调用你的 worker 回答
```

### 示例 4：完全覆盖系统提示

`run::start` 接受可选的 `system_prompt` 字段。传入后 orchestrator 直接使用你的字符串，跳过三层组装。Skill 下载仍然运行，Agent 保留按需发现能力。

### 示例 5：替换审批网关的 UI 表面

```typescript
// 默认 approval-gate 注册 approval::resolve
// 写一个 Slack worker 监听 /approve <id> 和 /deny <id> slash 命令
// 调用 approval::resolve 传递 payload
// orchestrator 和 approval-gate worker 毫无感知
// 你添加了一个新 worker，没有替换现有 worker
```

---

## 七、Harness 是一个滑块，不是一个岔路口

经典的 harness 争论框架化为"薄 vs 厚"。Anthropic 的薄循环 vs LangGraph 的显式 DAG。框架假设你选一边，然后忍受。

当 harness 由同一总线上的 worker 组成时，**薄 vs 厚只是你安装了多少个 worker 的计数**：

### 薄 Harness

```
turn-orchestrator + provider-anthropic + auth-credentials + 最小 meta-worker
```

- 没有审批、预算、策略引擎、hook 扇出
- 信任模型
- 适合：自主研究 Agent、实验循环、内部工具

### 厚 Harness

```
全部 11 个 worker + context-compaction + 自定义策略 worker
+ 自定义审批网关 + Slack 集成审批 + 预算 worker
```

- 每个工具调用可审计
- 每个模型消费归入财务仪表盘
- 适合：处理客户工作流的 Agent

**薄和厚之间的架构距离不是重写，而是配置变更。** 相同的线协议、相同的 trace 形状、相同的可观测性故事。滑块通过从 `config.yaml` 添加和移除 worker 来移动。

### 内部重构的独立性

turn-orchestrator 刚完成一次重构：将 FSM 从 11 个状态缩减到 7 个，删除了每个调用的 `turn::approval_resume` 机制，改用单个响应式 `turn::on_approval` 状态触发器，将 `tearing_down` 内联到 `finishSession()`。

堆栈中的**每个其他 worker 保持不变**。`approval::resolve` 的线格式没有移动。契约保持不变。

> **这就是组合给你的属性：** 一个 worker 的重大内部重构是自包含变更，因为每个邻居都通过总线级别的函数 ID 通信。

---

## 八、实践建议与资源

### 快速体验

```bash
git clone github.com/iii-hq/workers
pnpm install
pnpm build
# 运行复合入口点，你将获得完整的 14-worker harness
```

### 核心资源

| 资源 | 地址 |
|------|------|
| 文档 | iii.dev/docs |
| 引擎 | github.com/iii-hq/iii |
| Worker 注册中心 | workers.iii.dev |
| Harness 包 | github.com/iii-hq/workers/harness |
| 社区 | discord.gg/iiidev |

### 一句话总结

> **Harness 不是你安装的东西。Harness 是你的系统为了让 Agent 持久、安全、可观察地运行而必须完成的一组工作。框架时代把这些工作捆绑在一起，因为底层没有给你组合它们的方式。iii 的赌注是，一个原语——通过 WebSocket 连接引擎、注册函数和触发器的 worker——足够小，能分别吸收每一个职责，最终得到的栈比任何框架都更有用，因为每一层都是可独立替换的。**
>
> 你不"采用"iii harness。你安装你需要的 worker，写你需要的 worker，得到一个形状与你的系统完全匹配的 harness。

---

> **原文作者**：Mike Piccolo (@mfpiccolo)，iii 创始人 & CEO
> **发布时间**：2026 年 5 月
> **原文平台**：X (Twitter) 长文 — "How to build your own agent harness???"
> **引用统计**：1k+ 书签 / 393 赞 / 36 转发
