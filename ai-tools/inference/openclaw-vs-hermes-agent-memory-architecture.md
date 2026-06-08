---
title: "OpenClaw vs Hermes Agent：智能体记忆架构深度对比"
source: "https://x.com/mem0ai/status/2059662044224475280"
author: "mem0 (mem0ai)"
date: 2026-05-27
tags:
  - agent-memory
  - openclaw
  - hermes-agent
  - memory-architecture
  - mem0
  - prefix-caching
  - compaction
  - dreaming
  - FTS5
  - vector-search
category: "ai-tools/agent-engineering/patterns"
---

# OpenClaw vs Hermes Agent：智能体记忆架构深度对比

> **来源：** [What OpenClaw and Hermes Agent Reveal About Agent Memory](https://x.com/mem0ai/status/2059662044224475280) — mem0 (In Context #10)

---

## 一、核心问题

> "Long-running coding agents all hit the same problem: memory fades over time. A chat session is not one clean prompt. It can stretch across hours, days, files, decisions, preferences, and half-finished work."

**长期运行的编码智能体都面临同一个问题：记忆会随着时间衰减。**

一个聊天会话不是一次干净的提示——它可能跨越数小时、数天、多个文件、无数决策、偏好和未完成的工作。因此，**记忆不再是功能特性，而是智能体架构的一部分**。

---

## 二、两种设计哲学

| 维度 | Hermes Agent | OpenClaw |
|------|-------------|----------|
| **设计理念** | 记忆应保持**小而静态**，优化缓存效率 | 记忆应是**活态、可搜索、文件原生**的 |
| **系统提示方式** | 冻结（Frozen）：启动时固定，会话中不变 | 实时注入（Live）：每轮重新载入 MEMORY.md |
| **记忆容量** | ~3,575 字符（~1,300 tokens） | ~20,000 字符软上限 |
| **核心优化目标** | 缓存稳定长会话 | 即时可见性 |
| **底层权衡** | 为 Prefix Caching 牺牲单会话内记忆新鲜度 | 为记忆即时性承担 token 开销 |

> "Both are coherent designs. Both integrate with Mem0. But the trade-off is very different: Should agent memory be optimized for stable, cached long sessions, or for immediate, live recall?"

---

## 三、记忆存储位置

### 3.1 Hermes Agent

```text
~/.hermes/memories/
├── MEMORY.md    # 对"世界"的笔记，硬上限 2,200 字符
└── USER.md      # 对"用户"的笔记，硬上限 1,375 字符
```

- **总容量：** ~3,575 字符（约 1,300 tokens）
- **条目分隔符：** `§`（节号 U+00A7）
- **行为：** 每次会话启动时，这段内容作为系统提示的一部分发送到 LLM

### 3.2 OpenClaw

```text
~/.openclaw/workspace/
├── MEMORY.md                     # 主长期记忆文件，~20,000 字软目标
├── memory/YYYY-MM-DD.md          # 每日笔记（今日和昨日自动加载）
├── DREAMS.md                     # 可选：记忆整合摘要
└── ~/.openclaw/memory/<agentId>.sqlite  # 每个 Agent 独立的 FTS5 + 向量索引
```

- **标记格式：** 纯 Markdown，无分隔符
- **存储预算：** 约是 Hermes 的 6 倍
- **代价：** 每轮 token 成本更高（部分因启动文件重发）

---

## 四、最深层的架构差异：冻结 vs 实时系统提示

### 4.1 Hermes 的冻结方案

> "Hermes captures memory once, when the session starts, and pins it as a frozen block in the system prompt."

**原理：**
1. 会话启动时，将 MEMORY.md + USER.md 读入系统提示
2. Agent 调用 memory tool 添加或删除条目 → **立即写入磁盘**
3. 但**系统提示不会更新**——新条目只在下次会话启动时生效

**理由：Prefix Caching（前缀缓存）**
> "Every major LLM provider caches the start of every prompt so subsequent turns can reuse those tokens at a fraction of the cost."

只要系统提示不变，缓存就有效。Hermes 明确选择了：
- 整个长会话中 **稳定的、缓存的系统提示输入**
- 代价是**单会话内记忆体验稍差**——Agent 刚写的内容要到下次会话才能读取

### 4.2 OpenClaw 的实时注入方案

> "OpenClaw goes the other way. MEMORY.md is re-injected fresh every turn as part of the system prompt's 'Project Context → Workspace Files' block."

**原理：**
1. MEMORY.md 每轮作为系统提示的 "Workspace Files" 部分**重新注入**
2. 会话中写入的内容 → **下轮立即可见**
3. 新鲜度是内建的

**代价：**
- Token 开销：维护者报告约 **20-30% 的每轮输入是重新发送的启动文件**
- 底层冗余：即使有 `memory_search` 和 `memory_get` 可用，大的 MEMORY.md 文件仍被完整注入

### 4.3 实际例子

**场景：** 用户会话中途提到已从 npm 切换为首选包管理器 pnpm。

| 系统 | 行为 |
|------|------|
| **Hermes** | 立即写入磁盘，Agent 确认收到。**但本会话剩余部分用的系统提示仍是旧状态。** 修正已落地于磁盘，下一会话启动时生效。 |
| **OpenClaw** | Agent 从实时注入的 MEMORY.md 中读取，**下轮立即使用 pnpm**，无需提醒。 |

> "Two coherent answers to the same trade-off. Hermes optimizes for cache-stable long sessions. OpenClaw optimizes for immediate visibility. Neither is wrong. They're different bets about what a developer using the tool actually does for hours at a time."

---

## 五、Agent 如何读写记忆

### 5.1 Hermes Agent

**一个工具，三个动作：**
```tool
memory_tool:
  - action: add     # 追加条目到 world-facts 或 user-facts 文件；拒绝精确重复
  - action: replace # 通过子串匹配找到现有条目并替换
  - action: remove  # 通过子串匹配删除条目
```

**关键设计：** 无条目 ID、无 UUID。Agent 通过引用条目的**唯一子串**来寻址。

### 5.2 OpenClaw

**原生工具（两个）：**
- `memory_search` — 混合检索（向量语义相似度 + 关键字精确匹配，如 ID 和代码符号）
- `memory_get` — 读取指定的记忆文件或行范围

**写入方式：** 直接编辑文件。Agent 编辑 MEMORY.md 的方式与编辑任何源文件相同——**无原生的 `memory_add`**。

**安装 Mem0 插件后扩展为八个工具：**
- `memory_search`, `memory_add`, `memory_list`
- `memory_get`, `memory_update`, `memory_delete`
- `memory_event_list`, `memory_event_status`（平台模式事件监控）

> "Hermes treats memory as a constrained API surface: three verbs, one tool, designed to make the model think carefully about what it's writing. OpenClaw treats memory as a file the agent already knows how to edit, plus a search tool over everything."

---

## 六、跨会话召回

| 维度 | Hermes | OpenClaw |
|------|--------|----------|
| **索引引擎** | FTS5（~/.hermes/state.db） | FTS5 + 向量（可选 QMD/LanceDB/Honcho） |
| **召回工具** | `session_search`（独立工具） | `memory_search`（统一搜索） |
| **表面分离** | 记忆与会话搜索是两套独立工具 | 统一接口无需选择召回来源 |
| **主动模式** | 无；Agent 自主决定何时搜索 | 可选 active memory：阻塞子 Agent 在每轮前检索并注入相关事实 |

### Active Memory 模式（仅 OpenClaw）

> "When enabled, a blocking sub-agent fires before the model generates each reply. It searches stored memory against the current message and injects relevant facts into the context before the main turn begins."

- 仅对交互式持久会话生效（不用于 headless 任务或一次性会话）
- 推荐模式：`recent`（当前消息 + 短会话尾部）

---

## 七、OpenClaw 有而 Hermes 没有的功能

### 7.1 自动压缩（Auto-Compaction）

> "Hermes has no auto-compaction primitive. When MEMORY.md hits 2,200 characters, the next write fails with an error and the agent has to consolidate by hand."

**Hermes 的问题：** 没有自动压缩原语。达到上限时写入失败，Agent 必须手动整理。

**OpenClaw 的 Auto-Compaction：**
- **默认开启**
- 会话接近上下文限制或模型返回上下文溢出错误时触发
- 将较早的轮次**总结为紧凑条目**，保留近期消息，继续运行
- **关键细节：** 分块逻辑会小心保持成对的工具调用与 `toolResult` 条目不分开
- 手动触发：`/compact`
- 完整对话历史仍保留在磁盘上——压缩只改变模型下一轮看到的内容

**配置参数（`agents.defaults.compaction`）：**
```
model:                 # 用于摘要的模型
keepRecentTokens:      # 保留的近期 token 数量
maxActiveTranscriptBytes:  # 触发压缩的字节阈值
truncateAfterCompaction:   # 是否创建后继转录
```

### 7.2 压缩前记忆刷新（Pre-Compaction Memory Flush）

> "Before compaction, OpenClaw automatically reminds the agent to save important notes to memory files. This prevents context loss."

**理念：** 压缩会总结对话上下文，因此**只有已提交到文件的记忆才能在该摘要中幸存。**

### 7.3 梦（Dreaming）——可选整合机制

**三个阶段，后台运行：**

| 阶段 | 行为 |
|------|------|
| **Light Sleep（浅睡）** | 摄入并暂存短期记忆 |
| **REM Sleep（REM 睡眠）** | 反思并提取模式 |
| **Deep Sleep（深睡）** | 将合格记忆提升到 MEMORY.md |

**晋升门槛（全部必须满足）：**
- `minScore` — 最低加权分数
- `minRecallCount` — 至少被召回 N 次
- `minUniqueQueries` — 由至少 N 个不同的搜索查询触发

**加权评分规则构成：**
```
权重 = relevance(相关性) + frequency(频率) + 
       queryDiversity(查询多样性) + recency(新鲜度) + 
       consolidation(整合度) + conceptRichness(概念丰富度)
```

> "Only memories that prove themselves useful across multiple recalls get promoted."

---

## 八、Mem0 的集成角色

### 8.1 核心理念

> "Mem0 sits underneath both as the cross-tool persistence layer: helping agents remember beyond one harness, one session, or one local memory file."

### 8.2 在 Hermes 中

- Mem0 是 8 个外部 Provider 之一
- 集成文档：[docs.mem0.ai/integrations/hermes](https://docs.mem0.ai/integrations/hermes)
- 激活方式：
  ```
  pip install hermes-agent[mem0]
  ```
  选择 mem0 作为 provider 后，`~/.hermes/config.yaml` 中写入 `memory.provider: mem0`，API key 存在 `~/.hermes/.env` 中

**工具集：** 三个工具：`mem0_profile`, `mem0_search`, `mem0_conclude`

**背景线程：** 每轮结束后在后台将 user/assistant 对话发送到 Mem0 进行服务端事实提取——慢或失败的 Mem0 调用不会阻塞对话。**连续 5 次失败后的断路器暂停 2 分钟调用。**

### 8.3 在 OpenClaw 中

- Mem0 是 npm 包 `@mem0/openclaw-mem0`
- 集成文档：[docs.mem0.ai/integrations/openclaw](https://docs.mem0.ai/integrations/openclaw)
- 安装方式：
  ```
  npm install @mem0/openclaw-mem0
  ```
  或通过 `mem0.ai/claw-setup` 的聊天界面安装

**工具集：** 八个工具（`memory_search`, `memory_add`, `memory_list`, `memory_get`, `memory_update`, `memory_delete`, `memory_event_list`, `memory_event_status`）

**两种运行模式：**
| 模式 | 要求 | 行为 |
|------|------|------|
| **Platform** | `MEM0_API_KEY` | 对话发送到 `api.mem0.ai` 进行提取和存储 |
| **Open-Source** | 无需 API Key | 使用 OpenAI `gpt-5-mini` 进行事实提取，`text-embedding-3-small` 进行嵌入（可配置其他后端） |

**Skills Mode（默认）：** 使用插件自带的 triage / recall / dream 协议：
- **Triage** — 从对话中提取事实
- **Recall** — 下一轮回复前拉取相关已有记忆
- **Dream** — 按较长时间节奏整合条目

**标志：** `autoRecall` 和 `autoCapture` 标志在 skills mode 下被忽略（由协议控制）

**用户隔离：** 每个用户的 `userId`（默认使用 OS 用户名）自动作用域化记忆——不同开发者的项目事实自动分离。

### 8.4 对比总结

| | 在 Hermes 中 | 在 OpenClaw 中 |
|--|-------------|---------------|
| **解决的问题** | 打破 3,575 字符硬上限和子串匹配检索 | 修复 20K 字静默截断问题 |
| **价值提升** | Agent 不用记得手动写东西 | Agent 不用记得手动写东西 |
| **运行模式** | 后台线程（不阻塞对话） | Skills 协议（Triage/Recall/Dream）+ 标志模式 |

---

## 九、综合对比总结

| 维度 | Hermes Agent | OpenClaw |
|------|-------------|----------|
| **设计哲学** | 小、冻结、缓存友好 | 活态、可搜索、文件原生 |
| **存储上限** | ~3,575 字符（硬上限） | ~20,000 字符（软目标） |
| **系统提示** | 会话启动时冻结 | 每轮实时注入 |
| **Prefix Caching** | ✅ 高度优化 | ❌ 20-30% 开销 |
| **写入可见性** | 下次会话生效 | 下轮立即生效 |
| **记忆 API** | 1 工具 3 动作（add/replace/remove） | 2 工具（search/get）+ 直接文件编辑 |
| **跨会话召回** | FTS5 + session_search | 统一 memory_search（FTS5+向量） |
| **主动召回** | 无（Agent 自主触发） | Active Memory 模式（阻塞预注入） |
| **自动压缩** | ❌ 无（达到上限报错） | ✅ 自动 + 压缩前刷新 |
| **记忆整合** | ❌ 无 | ✅ Dreaming（3 阶段 + 晋升阈值） |
| **多后端** | ❌ FTS5 仅 | ✅ SQLite / QMD / Honcho / LanceDB |
| **Mem0 集成** | 3 工具（背景线程 + 断路器） | 8 工具（Skills 协议 + 用户隔离） |

---

## 十、附录：知识关联

| 关联文档 | 关联点 |
|---------|--------|
| `spring/ai-agent/spring-ai-agent-resources-top30.md` | Spring AI Agent 记忆管理对比参考 |
| `productivity/obsidian-vault-organization-full-course.md` | 文件组织与记忆检索方法论 | 

---

*本文整理自 mem0 In Context #10 系列文章。*
