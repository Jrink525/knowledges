---
title: "How to Build an AI Second Brain for OpenClaw/Hermes That Learns While You Sleep"
tags:
  - agent-memory
  - second-brain
  - hermes
  - openclaw
  - gbrain
  - knowledge-layer
date: 2026-06-05
source: "https://x.com/voxyz_ai/status/2062604405682090403"
authors: "Vox (@voxyz_ai / voxyz.ai)"
series: "agent-memory"
---

# AI Second Brain：在 OpenClaw / Hermes 之上搭建共享知识层

> **来源：** X.com 长文 by Vox  
> **发布时间：** 2026-06-04  
> **数据：** 112 ❤️ · 18 🔁 · 5 💬

---

## 一、核心问题：两个 Runtime 两本日记

> "If each one only stores things inside its own runtime, what you end up with is two agents keeping separate diaries."

Hermes 和 OpenClaw 各自有自己的内存系统，但如果只把知识锁在各自的 runtime 里，第二天另一个 agent 醒来时不知道昨天学了什么。

一个生动的例子——某天某个知名开发者对一条 AI 回复反应很差，agent 记录下：
> "That developer is sensitive about tone. Approach with more caution."

但如果这条记录留在其中一个 runtime 的 cron 输出或 daily memory 里，下次另一个 runtime 接手时知识就丢失了。

---

## 二、三层分离架构

作者将系统拆为三层（三者不可混用）：

```
┌──────────────────────────────────────────────────────┐
│ Layer 3: BRAIN (gbrain)                              │
│ runtime-agnostic 知识层                              │
│ structure: Compiled Truth + Timeline                 │
├──────────────────────────────────────────────────────┤
│ Layer 2: MEMORY  (per-runtime)                       │
│ Hermes → MEMORY.md / USER.md / session_search        │
│ OpenClaw → daily notes / MEMORY.md / memory_search   │
│          → Dreaming / Active Memory                  │
├──────────────────────────────────────────────────────┤
│ Layer 1: RUNTIME                                     │
│ Hermes: personal agent loops, cron, CLI delivery     │
│ OpenClaw: workspace routing, multi-agent, dreaming   │
└──────────────────────────────────────────────────────┘
```

### Layer 1 — Runtime（谁干活）

**Hermes：**
- 适合固定调度的 agent 循环：晨间总结、夜间审计、定期检查
- 每次 cron run 是**全新会话**，不继承当前 chat context
- 默认 `skip_memory=True`（cron 时跳过 memory provider）
- 需通过 `context_from` / workdir / context files / 直接读 gbrain 自行携带上下文

**OpenClaw：**
- 适合 workspace / channel 路由 / 多 agent / Dreaming
- MEMORY.md = curated 层，daily notes = working 层
- Dreaming：三段式（Light / REM / Deep），仅 Deep 写入 durable candidates 到 MEMORY.md
- Active Memory：在交互式会话中，回复前阻塞式运行 recall sub-agent 拉取相关记忆

### Layer 2 — Memory（各 runtime 自己的记忆）

每个 runtime 已有足够的记忆系统（无需 gbrain）。

### Layer 3 — Brain / gbrain（共享知识层）

> "gbrain solves the step after that: when you run Hermes and OpenClaw at the same time, or you'll switch runtimes later."

**gbrain 的关键属性：**
- 不绑定任何 runtime
- 任何 agent 都可以读（Hermes / OpenClaw / 夜间任务 / 审计任务）
- 多个 runtime 共享一个 brain
- 这才是"第二大脑"的感觉

---

## 三、gbrain 页面结构：Compiled Truth + Timeline

这是 gbrain 最核心的设计：

```
┌─────────────────────────────────────┐
│   Compiled Truth (当前结论)          │  ← 始终是最新状态，被新信息重写
│   ─────────────────────────────      │
│   "Customer A is annoyed about X.    │
│    We promised fix by Friday."       │
├─────────────────────────────────────┤
│   Timeline (证据链)                  │  ← 只追加，不修改
│   ─────────────────────────────      │
│   [2026-06-02] Customer complained   │
│   [2026-06-03] Support escalated     │
│   [2026-06-04] Engineering assigned  │
└─────────────────────────────────────┘
```

**为什么这样设计：**
- 只问"当前状态"→ 读 Compiled Truth → 快
- 只问"发生了什么"→ 读 Timeline → 全
- 最大的问题：结论本身不带置信度，原始日志需要从头推理
- 两个半层完美解决：上层是给下一个 agent 快速接手的当前判断，下层是审计/冲突/重写的证据链

> "I don't let the agent write long-term knowledge as prose. I make it write a page."

---

## 四、信息的五种归宿

处理一条信息时，不问"要不要存"，而问**"该进哪一层"**：

| 归宿 | 说明 | 示例 |
|------|------|------|
| 🗑️ **Discard** | 噪音，直接丢弃 | 某条新闻的点击量数字 |
| 📝 **Log / Timeline** | 事实性记录，追加到证据链 | "Customer asked about pricing. No immediate follow-up." |
| 🧠 **Brain Page** | 影响当前判断或行为模式的知识 | 一个人的性格、项目的状态、一个关系的当前状况 |
| 📖 **Runtime Memory** | 行为规则、操作方式 | "Reply shorter next time" |
| ⏰ **Scheduler** | 需要未来某时刻做的事 | "Check billing update next Wednesday" |

**关键区分：**
- "Reply shorter next time" → Runtime Memory（怎么行动）
- "Why a certain developer is sensitive to AI replies" → Brain Page（当前状态）
- "Check billing update next Wednesday" → Scheduler（提醒）
- 很多人把所有东西塞进 MEMORY.md，结果变成一锅粥

---

## 五、Memory Candidate Card

夜间审查时发现值得保留的信息时，先填这张卡，**不直接写长时记忆**：

```
title: <对象名>
type: person | company | project | concept | writing-asset
claim: 一句话当前判断
evidence: 相关的原始日志/引用
confidence: high | medium | low
action_boundary: agent 可以做什么/不可以做什么
```

这张卡强制 agent 回答一个问题：
> **"这段信息实际上会如何改变未来的行为或判断？"**

答不上来就别 promote。

---

## 六、gbrain 写规则（每次写前过一遍）

1. **只写断言，不写描述**
   - ✅ "Customer A is annoyed about X. We promised fix by Friday."
   - ❌ "Customer A is in a hurry."

2. **标明置信度**
   - high / medium / low

3. **注明来源**
   - 哪次对话、哪条记录

4. **设定行动边界（action boundary）**
   - 这个知识授权 agent 做什么、不做什么

> 注意：write rule 只是把边界写下来让 agent 读。执行的硬阻断仍在 runtime 的 approval settings / sandboxing / tool policy / scheduled-task config 层面。

---

## 七、Nightly Learning 的三种产出

不做"总结今天发生了什么"，而是：

| 产出 | 说明 |
|------|------|
| **Compiled Truth 更新** | 哪些 brain page 的上半部分需要重写 |
| **新 Brain Page 创建** | 哪些对象值得独立跟踪 |
| **Timeline 追加** | 哪些事件是新的证据需要记录 |

---

## 八、判断"第二大脑是否建成了"的五个问题

1. 上次客户上下文在下一次运行中是否可用？
2. 行为调整是否跨会话持续？
3. 换运行时时知识层是否留存？
4. 一个 agent 发现的模式是否被另一个 agent 使用？
5. 长期记忆是否因新证据更新，而非无限膨胀？

> "If those questions come back uncertain, what you're missing is probably a runtime-neutral knowledge layer. More cron or another memory plugin won't close the gap."

---

## 九、一句话总结

> "If you only run one runtime, its own memory is enough. The moment you run Hermes and OpenClaw together, a real question shows up: who maintains the current state that belongs to no single runtime?"

---

## 十、与已有知识库的关联

本篇文章与知识库中多个主题高度呼应：

**Agent Memory 系列：**
- [Agent Memory System: From Basics to Production](/ai-tools/agent-memory-system-from-basics-to-production.md)
- [Agent Memory Framework: Remember, Cite, Forget](/ai-tools/agent-memory-framework-remember-cite-forget.md)
- [OpenClaw vs Hermes Agent Memory Architecture](/ai-tools/openclaw-vs-hermes-agent-memory-architecture.md)
- [State of Memory in Agent Harness: Mem0](/ai-tools/state-of-memory-in-agent-harness-mem0.md)

**Skill 相关：**
- [Skillify: Skill Engineering Guide](/ai-tools/skillify-skill-engineering-guide.md)
- [Hiten Shah: Skill Library First AI Strategy](/ai-tools/skills/hnshah-skill-library-first-ai-strategy.md)

**CF / DBFS 讨论：**
- [Database vs Filesystem vs Skill: Aparna](/ai-tools/database-filesystem-vs-skill-aparna.md)

---

## 附录：快速上手

今晚可以做的三件事：

1. **挑一个对象**（一个人、一个项目、一个公司），用手写一个 brain page（Compiled Truth + Timeline）
2. **写一条 gbrain Write Rule** 贴在你改知识的位置（CLAUDE.md / agent-startup rules）
3. **设定一条试验：** 下次做夜间审查时，输出不是"总结一下"而是"这张 Card 是否值得创建/更新"

不要一次性迁移所有历史。先跑通一个循环：
```
runtime 产生信息 → 审查 → 填充 Memory Candidate Card → 写进 gbrain page → 下一个 session 读 brain page
```

---

*整理于 2026-06-05，来自 Vox (voxyz.ai) X.com 长文*
