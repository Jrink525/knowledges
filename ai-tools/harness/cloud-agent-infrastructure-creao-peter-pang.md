---
title: "Building Cloud Agent Infrastructure — Lessons from CREAO"
tags:
  - agent-infrastructure
  - cloud-agents
  - sandbox
  - security
  - deployment
  - creao
date: 2026-06-05
source: "https://x.com/intuitiveml/status/2062699747224568212"
authors: "Peter Pang (@intuitiveml / CREAO)"
---

# Cloud Agent Infrastructure: 从桌面到云的工程教训

> **来源：** X.com 长文 by Peter Pang (CREAO 联合创始人)  
> **发布时间：** 2026-06-05  
> **数据：** 90 ❤️ · 11 🔁 · 4 💬

---

## 一、核心问题：桌面 Agent vs 云 Agent

### 桌面 Agent 的隐含假设

- 一个用户、一台机器、一个进程
- Agent 在笔记本开机时运行
- 向本地文件系统写数据
- API key 放在环境变量里
- 终端关闭时进程结束
- 出错了用户自己重试
- 需要包直接 pip install
- **State、密钥、生命周期都在一个可信边界内**

### 云 Agent 的残酷现实

- 运行在每次**新鲜启动**的沙箱里
- 硬件与陌生人共享
- 调用者用户从未见过：定时调度、HTTP 请求、其他 Agent
- **用户通常在睡觉时运行**
- 沙箱内的代码可能是**对抗性的**
- 文件系统需要跨部署持久化
- 凭证不能住在 agent 所在的地方
- **所有桌面免费给的保证（持久化、身份、网络信任、重试）都要作为显式系统重建**

---

## 二、Lesson 1：分离变化快的与变化慢的

### 问题本质

桌面上，用户环境和 agent 运行时是同一回事——同一人、同一节奏更新。

云端则不同：
- **用户环境（依赖、数据、脚本）** → 变化慢，用户主动触发
- **Runner 代码（平台方的运行时）** → 变化快，平台每日多次部署

如果两者混为一个 artifact，每次部署都得二选一：
- 保留旧 runner 代码 → 安全隐患
- 丢弃用户冻结环境 → 违反"环境冻结直到你改"的承诺

### CREAO 的解决方案：Snapshot 冻结 + Hot-swap Runner

**第一阶段（粗暴方案）：**
启动时检查 runner 版本，不匹配则丢弃 snapshot 从干净模板重启。

问题：定时任务的第一次运行会丢失环境。周一 9 点的 cron 不应该因为 8:55 部署了就丢环境。

**第二阶段（最终方案）：** 学 OS 的更新方式（内核升级 ≠ 清空 home 目录）

1. 沙箱从用户冻结的 snapshot 启动，**不动**
2. 在沙箱内热替换 runner：
   - Stage 新 runner 到临时目录
   - `node --check` 验证语法
   - **原子性交换**：
     - 解锁旧 runner 的 immutable flag
     - 复制新 runner 覆盖
     - 重新 `chattr +i` 锁定
     - 隐藏 `chattr` 二进制本身（防沙箱内代码撤销锁定）
   - 清除 V8 compile cache（防旧 bytecode）
3. 任何一步失败 → 杀掉沙箱，用新沙箱重试（**不保留半升级状态**）
4. 成功后重新 snapshot，使下一轮启动跳过 swap

**关键指标：** 整个 swap 约 **300ms**

### 核心诊断问题

> 对于你在云平台中持久化的任何东西，问：谁控制这个 artifact 的变更节奏？
> 如果用户和平台都拥有它，你最终会为耦合买单。
> **沿所有权边界拆分 artifact，让双方按自己的时钟更新。**

---

## 三、Lesson 2：将密钥留在执行边界之外

### 核心安全假设

> "No long-lived credential ever lives inside the sandbox."

**安全模型：默认假设沙箱内的代码已被攻破。** 不是抱着希望，而是假设它已经发生。

### 架构：API Bridge

```
沙箱（不可信）                   主机侧（可信）
┌──────────────┐              ┌──────────────────┐
│ Agent        │──HTTP req──→ │ API Bridge       │
│ (攻击者可控)  │              │ - 附加 OAuth 令牌 │
│              │←──resp────── │ - 执行实际调用    │
└──────────────┘              └──────────────────┘
```

令牌从未进入沙箱的**内存或环境变量**。

### 双重验证

**第一层：IP Allowlist**
- Bridge 只接受来自沙箱宿主内网 IP 范围的连接
- 开发者笔记本、泄漏的 URL、公网 → 在网络层直接丢弃

**第二层：Per-run 短寿命 JWT**
- 沙箱启动时，平台签发一个**仅限本次运行**的 JWT
  - Scope：哪个用户、哪个 App、哪个 Session
  - 过期时间 = 运行窗口，不长于一次运行
- 沙箱每次调用 Bridge 时出示 JWT
- Bridge 验证签名 + 过期时间，再解析用户已存储的凭证，**在服务端附加**
- 如果沙箱被劫持，攻击者拿到的是一个：
  - **短寿命**（随运行结束失效）
  - **窄 scope**（仅限一次会话）
  - **仅从内部网络可用**（IP 限制）
  - 的 token → **没有主凭证可窃取**

### 同一 Bridge 提供向外通道

除此之外，Bridge 还承载：
- 计费扣除
- 日志
- 指标

**双向跨沙箱边界的唯一接口。** 沙箱内的一切默认视为已攻破。

> "如果 prompt injection 诱使 agent 把 process.env dump 到 webhook，攻击者只会拿到一个短寿命 JWT，仅从内部网络可用，随运行结束失效。这个属性让我们敢在共享基础设施上运行不受信任的用户代码而不失眠。"

---

## 四、底层模式总结

```
触发                           执行管道                    领域
┌─────────┐                    ┌─────────────┐
│ UI 点击  │──→                │             │
│ Cron    │──→── executeAgent ──→  沙箱环境     │──→ 业务逻辑
│ API 调用 │──→  (同一函数)      │             │
└─────────┘                    └─────────────┘
                               ↑    ↑    ↑
                            snapshot  hot-swap  API Bridge
                            冻结环境    runner   密钥隔离
```

### 四个不可妥协的属性

1. **State 在沙箱内，冻结到用户主动修改为止**
2. **代码可热替换，与 state 解耦**
3. **凭证在 host 侧，永不进入 agent**
4. **同一执行管道服务所有调用者**（人、调度器、或另一软件）

### 最后一个是点睛之笔

> "A function with a natural language interface."

同一个 `executeAgent` 函数同时服务：
- UI 点击
- 定时调度
- API 调用

计费系统、扣费日志、可观测性信号——完全一致。Agent 本身不知道也不关心谁触发了它。

> "Adding a new trigger surface is a routing change, not an architecture change."

### 与桌面 Agent 的最终对比

| 维度 | 桌面 Agent | 云 Agent |
|------|-----------|---------|
| 生命周期 | 绑定到笔记本 | 是其他系统可调用的函数 |
| 状态持久化 | 本地文件系统 | 冻结 snapshot |
| 代码更新 | 用户手动升级 | 平台热替换，300ms |
| 凭证安全 | 环境变量，可信环境 | API Bridge + per-run JWT |
| 触发器 | 用户手动运行 | UI / Cron / API / Agent 间调用 |
| 安全假设 | 用户是可信的 | 默认沙箱已被攻破 |

> "An agent is a function with a natural language interface. Its implementation belongs to the user. Its trigger surface, its runtime, its security boundary belong to the platform. The discipline is to build the layers so each evolves on its own clock, and to spend the time finding the cracks between systems before someone else does."

---

## 五、与已有知识库的关联

本篇文章的核心主题 **Cloud Agent Infrastructure** 与已有知识高度相关：

- **Agent Sandbox 基础设施对比：**
  - [Agent Sandbox Infrastructure](/ai-tools/agent-sandbox-infrastructure.md) — 沙箱隔离与安全模式
  - [Harness 企业 AI 基础设施](/ai-tools/harness-enterprise-ai-infrastructure-2026.md) — 企业级 agent 运行平台

- **Harness 相关：**
  - [Agent Harness Engineering](/ai-tools/agent-harness-engineering.md) — Harness 架构模式
  - [Thin Harness, Fat Skills](/ai-tools/thin-harness-fat-skills-garry-tan.md) — Garry Tan 的 harness 理念
  - [Harness From Theory to Practice](/ai-tools/harness-from-theory-to-practice.md)

- **安全性方面：**
  - [Agent Hooks 确定性控制](/ai-tools/agent-hooks-deterministic-control.md) — Agent 行为的确定性约束
  - [Claude Code 云部署沙箱隔离](/ai-tools/claude-code-cloud-deployment-sandbox-isolation.md)

**与 Harness 模式的关系：**

这篇文章中的 `executeAgent` 单一入口 + snapshot 冻结 + hot-swap runner + API bridge 的架构，实际上就是 **harness 模式在云端的工程落地**——

- 用户拥有实现（skill / agent code）
- 平台拥有触发面、运行时、安全边界
- 层之间按各自时钟独立演进

这与"thin harness, fat skills"的思想完全一致。

---

*整理于 2026-06-05，来自 Peter Pang (CREAO) X.com 长文*
