---
title: "A Framework for Agent Memory: Remember, Cite, Forget — Agent 记忆架构框架"
tags:
  - agents
  - agent-memory
  - llm
  - langgraph
  - mem0
  - gbrain
  - rag
  - architecture
date: 2026-05-23
source: "https://x.com/voxyz_ai/status/2057862044783628508"
authors: "Vox (@voxyz_ai)"
enhanced-from:
  - "GBrain - Garry Tan (YC President)"
  - "Lossless Claw (LCM) - Martian Engineering"
  - "LangGraph Memory - LangChain"
  - "Mem0 - Memory System"
  - "Air Canada Chatbot Case 2024"
  - "Demos AI Election Study 2026"
  - "UK DBT GOV.UK Audit"
---

# A Framework for Agent Memory: Remember, Cite, Forget

> **来源：** [Vox (@voxyz_ai)](https://x.com/voxyz_ai/status/2057862044783628508) — Agent 记忆框架  
> **数据：** 3.2 万+ 阅读 · 108 点赞 · 293 收藏  
> **作者：** Voxyz 构建者，"公司里唯一的真人"，实践 AI-native 未来  
> **中文整理：** 核心框架翻译 + 开源工具对照 + 真实案例分析

---

## 为什么读这篇？

给 agent 加"记忆"时，大多数人的第一反应是：**"还能塞什么东西进去？"**

但存储更多 ≠ agent 会用得更好。

**Agent 记忆必须同时做好三件事才能可靠：**
1. **Remember** — 记住该记住的
2. **Cite** — 引用该信任的
3. **Forget** — 忘记该过期的

这三件事一旦分开就构成了一个**适用于任何 agent 的框架**。

---

## Part 1: Remember — Agent 记忆的 6 层架构

实际运行中，agent 使用的记忆层约有 6 层。每层有**不同的生命周期、不同的权威范围、不同的失败方式**。

### 层级一览

| 层级 | 生命周期 | 失效条件 | 常见失败 |
|------|---------|---------|---------|
| **Hot Session** | 当前任务 | 任务结束 | 压缩上下文时丢弃了关键指令 |
| **Day-State** | 今天 | 更新的指令覆盖 | cron agent 还在执行早上的指令 |
| **Project Memory** | 跨 session | 被更新的教训覆盖 | 三个月前的偏好还在影响今天的输出 |
| **Retrieval/Index** | 持久 | 源更新或过期 | 向量搜索返回了六个月的旧计划 |
| **Canonical Policy** | 长期规则 | 手动编辑文件 | — |
| **Direct Instruction** | 当前任务 | 新指令覆盖 | 总结性文字不能替代原始确认 |

### 1. Hot Session（热 session — 当前任务的短期记忆）

持有进行中的上下文：用户刚说了什么、上个工具的输出、本轮的中间结论。

**常见失败：** 用户说"今天不用 emoji"，第三轮上下文被压缩时丢掉了这行，七轮后又加了 emoji。

> **💡 对应方案：** [Lossless Claw (LCM)](https://github.com/Martian-Engineering/lossless-claw)（OpenClaw 插件）用 DAG 结构保留每条原始消息，agent 可以用 `lcm_grep` 从 SQLite 中搜索被压缩的历史上下文，恢复细节。原始消息永远不丢。

### 2. Day-State（今日操作白板）

记录今天 agent 做了什么、当前进度、下一步。

**设计原则：** 白板就是要被覆盖的。**一条带有更新时间戳的指令应该让旧状态退役。**

**常见失败：** 早上说"先做文章 A"，下午切换到文章 B，但 cron agent 还在为 A 拉研究。

### 3. Project Memory（项目级记忆 — 跨 session 的学到教训）

项目之前踩过的坑、哪个模式有效、哪些决策已敲定。

比白板活得久，但仍会被更新的教训覆盖。

**常见失败：** 三个月前的笔记说"用户偏好 markdown"，虽然用户上个月已切换偏好，但现在仍影响格式选择。

> **💡 实际落地：** YC 总裁 Garry Tan 的 [GBrain](https://github.com/garrytan/gbrain) 就是为此而生。它是个跨 session 结构化知识库，为 146K+ 页面、24K+ 人、5K+ 公司的实际 agent 生产环境服务。每天自动摄入会议、邮件、推文、语音通话，夜间整合更新记忆。

### 4. Retrieval / Index（检索层 — 提供候选）

向量数据库、RAG、GBrain 搜索、图搜索都在这一层。

**职责：** 给出可能相关的候选。**最终决策仍取决于来源、时间、权威度和新鲜度。** 索引不决定答案——它只是提出候选人。

**常见失败：** 向量搜索返回了半年前的旧计划，被当作当前最佳答案。

### 5. Canonical Policy（规范策略层 — 长期规则）

项目规则文件（如 AGENTS.md、SOUL.md）、团队策略、产品边界。

**角色：** 相当于 agent 的"宪法"——长寿、稳定、只能通过手动编辑文件来变更。

> 💡 对应我们 workspace 里的 AGENTS.md、SOUL.md、TOOLS.md 文件。

### 6. Direct Instruction（直接指令层 — 当前任务命令）

用户刚说的话。当前任务优先级高，但不一定耐用。

**关键约束：** 必须保留原始来源。总结性转述没有同等权重。

**常见失败：** AGENTS.md 说"外部操作需手动确认"，hot session 总结说"用户已授权批量发送"，agent 默默跟随了总结。**唯一能覆盖规范策略层的是可追溯的原始确认。**

> **Vox 的核心观点：** "用户似乎授权了"这种来自总结的话语不算数。

---

## Part 2: Cite — 不要让 agent 猜测谁有权威

记忆工作至少需要两步：

### Step 1: 确定当前查询应该命中哪个来源

GBrain 的 Source Resolver 是一个很好的参考实现——它按顺序检查：**CLI flag → 环境变量 → dotfile → 最长前缀路径匹配 → 默认配置 → fallback**。

这步防止的错误：**查错来源。** 比如该查产品文档时查了旧的内部笔记。

### Step 2: 冲突时权威裁决顺序

当查询结果出现矛盾，一个**权威顺序**决定谁赢。以下顺序可直接复制：

```
1. 原始直接指令 (Original Direct Instruction)     ← 用户说的优先
2. 规范策略 (Canonical Policy)                     ← 规则文件
3. 最新项目决策 (Most Recent Project Decision)     ← 学到的教训
4. 有来源归因的长期记忆 (LT Memory w/ Source)      ← 追踪到谁说的
5. 检索摘要 (Retrieval Summary)                     ← RAG 结果
6. 压缩摘要 (Compressed Summary)                   ← 上下文压缩
```

**级别越高，优先级越高。**

### 真实案例：Air Canada 聊天机器人民事纠纷 (2024)

**发生了什么：**
- Air Canada 的聊天机器人告诉一名乘客可以申请**追溯性丧亲票价退款**
- 官方政策页面写的恰恰**相反**
- 仲裁庭判 Air Canada 支付 C$650.88 票价差额 + 利息

**法官的话：** "信息来自静态页面还是聊天机器人并不重要。"

**Vox 的分析：** 一旦 AI 代表公司发言，它就不能与规范策略页相矛盾。用户不应该猜测哪个更准确。**公司必须自己定义权威链。**

### 引用本身也会过时

**Demos 研究 (2026 苏格兰大选前)：** 对 75 个选举问题的 AI 工具测试，**34% 的回答包含错误信息**。ChatGPT 的引用**44% 至少过时一年**。

对于 agent 而言，判断一个来源意味着首先要问：**这个链接还当前吗？**

---

## Part 3: Forget — 过期记忆是可靠性工程

**最被低估的 agent 记忆能力：让旧记忆过期。**

大多数团队把"忘记"当作 GDPR 合规任务。但对 agent 来说，**这是可靠性问题**——一条已经过时但仍然看起来可用的记忆，比"没有记忆"更危险。

### 现实案例：UK GOV.UK 内容腐烂

2026 年，英国商业贸易部的审计发现：
- 主页是最新的
- 但 GenAI 机器人在窄查询时从**未维护的旧页面**拉取答案
- 仅第一遍就发现 **150 个页面**同时满足三个条件：
  - **5 年未更新**
  - **5 年内少于 11 次访问**
  - **没有负责人**

旧信息没有消失。只是没人读了。一旦 agent 拉回它，它听起来和今天的答案一样自信。

### 三种过期实现路径

| 方式 | 机制 | 适用场景 | 代表作 |
|------|------|---------|--------|
| **Hard Expiry** | `valid_from` / `valid_until` 字段 | 政策、定价、法规 | GBrain (typed facts / trajectory) |
| **Bitemporal** | 四时间戳：`created_at / valid_at / invalid_at / expired_at` | 随时间变化的事实 | Zep |
| **Soft Decay** | 检索排序降权，降低到 0.3× 地板 | 偏好、习惯、背景知识 | Mem0 |

**核心原则：把过期机制和存储机制一起设计。** 不要先建存储再想怎么删。

---

## Part 4: 三条准入审核问题

在任何记忆进入决策循环之前，问：

### 1️⃣ 这个记忆能影响什么级别的决策？
- 提示级 (Hint only)？
- 可引用的证据 (Citable evidence)？
- 还是可以直接做最终决定？

### 2️⃣ 它来自哪里？
- 哪个规范文件、哪天的笔记、哪条消息？
- 还是只是另一个记忆的衍生物？

### 3️⃣ 它仍然有效吗？
什么样新的信息会让这个记忆退出？

### 示例：Agent 回复邮件时拉了三个月前的偏好

> agent 就要回复一封邮件，从 project memory 拉了一条三个月前的偏好：用户曾说"回复用纯文本，别用 markdown。"

1. **决策级别：** hint only，不能覆盖今天的明确指令
2. **来源：** 必须能指出哪条消息、谁说的
3. **仍然有效：** 三个月未触及，先和用户确认一次再用

**全部可答** → 记忆可进入决策路径  
**任一不可答** → 只能作为背景上下文保留

> 不要让一条没有来源、没有有效期限、没有权威边界的记忆为 agent 做决策。

---

## 速查卡：保存这张卡片

```
Remember by layer.  Cite by source.  Forget by expiry.
记住靠分层      引用找来源      过期就忘记

Hot session        → 载体：当前任务       → 退出：任务结束
Day-state          → 载体：今天             → 退出：更新决策到来
Project memory     → 载体：长期教训         → 退出：教训被覆盖
Retrieval / Index  → 载体：提供候选         → 退出：源更新 / 索引重建 / 事实过期
Canonical Policy   → 载体：长期规则         → 退出：新版本手动提交
Direct Instruction → 载体：当前指令         → 退出：任务结束 / 新指令到达
```

贴在 AGENTS.md 里，每次 review 记忆变更时跑一遍。

---

## 工具生态对照

### GBrain — Garry Tan (YC President)
- **定位：** 跨 session 结构化知识库
- **特性：** 6 层 Source Resolver、双时间事实、自建知识图谱、实体链接自动提取
- **亮点：** 已在生产环境中服务 146K 页面、24K 人、5K 公司
- **规模：** 66 个 cron 任务全自动运行
- **机制：** Hybrid search + backlink 排名，P@5 49.1% vs 无图版本 +31.4pts
- **推荐：** 大项目长期记忆管理层

### Lossless Claw (LCM) — Martian Engineering
- **定位：** OpenClaw 无损上下文插件
- **特性：** DAG 压缩，每条原始消息保存在 SQLite
- **机制：** 叶子摘要 → 凝聚摘要 → 搜索工具 (`lcm_grep`, `lcm_expand`)
- **推荐：** 对应 Vox 文中 Hot Session 层的无损保留

### LangGraph Memory — LangChain
- **定位：** 多 agent 编排框架
- **特性：** 短期 (Semantic / Episodic / Procedural) + 长期分层
- **理念：** Vox 的 6 层架构和 LangGraph 的分层理念一致

### Mem0
- **定位：** 面向 agent 的记忆层
- **特性：** Conversation / Session / User / Org 分层 + Soft Decay
- **失效机制：** 检索降权（soft decay），不删除也不隐藏，最低至 0.3×

### Zep
- **定位：** 事实层 + 时间线
- **特性：** 四时间戳 (created_at / valid_at / invalid_at / expired_at)
- **推荐：** 需要对事实变化有精确追溯的场景

---

## 与本系列前文的关联

**Vox 这篇 + 之前整理的 agent 内容形成了完整的认知链：**

| 文章 | 视角 | 核心价值 |
|------|------|---------|
| **20 AI Concepts** (Rahul) | AI 概念扫盲 | 基础理论：LLM、RAG、Agent |
| **30 Claude Workflows** (Khairallah) | 使用层 | Skills/Workflows 日常实践 |
| **Claude Code Hooks** (Vince) | 开发层 | 代码开发自动化流程 |
| **Agent Memory Framework** (Vox) **← 本篇** | **架构层** | **记忆系统设计、权威链、过期策略** |

Vox 的框架回答了前面三篇都没有深入的问题：**当 agent 变得复杂时，它到底该怎么记住正确的信息、引用正确的来源、忘记过时的干扰？**

---

## 总结

### 三句核心

1. **Remember by layer** — 分层记住，每层有自己的生命周期和退出条件
2. **Cite by source** — 按权威链引用，原始指令 > 规范策略 > 项目记忆 > 检索
3. **Forget by expiry** — 硬过期 + 双时间戳 + 软衰减，让旧记忆安全退役

### 一句话

> **设计 agent 记忆 = 设计公司治理。**
> 记住靠分层，引用靠溯源，忘记靠过期。把这三个打包成一个信任契约写进 agent，它的决策才开始可靠。
>
> 三件事**同时工作**的时刻，才是 agent 真正可信赖的时刻。

---

*整理于 2026-05-23，综合自 Vox @voxyz_ai X 长文 + GBrain/LCM/LangGraph/Mem0/Zep 文档 + Air Canada/Demos/UK GOV.UK 真实案例分析*
