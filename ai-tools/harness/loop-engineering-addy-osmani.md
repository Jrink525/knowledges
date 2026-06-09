---
title: "Loop Engineering — Addy Osmani"
tags:
  - loop-engineering
  - coding-agents
  - automation
  - claude-code
  - codex
  - ai-workflow
date: 2026-06-09
source: "https://addyosmani.com/blog/loop-engineering/"
authors: "Addy Osmani (@addyosmani, Google Chrome)"
---

# Loop Engineering

> **Loop engineering 是用系统代替你来提示 agent。** 你设计一个系统来做这件事，而不是亲自写 prompt。  
> "You shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents." — Peter Steinberger  
> "I don't prompt Claude anymore. I have loops running that prompt Claude and figuring out what to do. My job is to write loops." — Boris Cherny (Claude Code 负责人)

---

## 核心转变

过去两年：你写 prompt → agent 回复 → 你写下一个 prompt。**Agent 是工具，你一直在握着它。**

现在：你构建一个小型系统，它负责发现任务、分配任务、检查结果、记录进度、决定下一步。**你设计这个系统来驱动 agent，而不是亲自驱动。**

- 比 [Agent Harness Engineering](https://addyosmani.com/blog/agent-harness-engineering/) 高一层
- harness 是单个 agent 运行的环境，loop 是让 harness 跑在定时器上、繁殖子 agent、自我喂养的机制

---

## 五个积木块 + 一个记忆

一个 loop 需要五个要素，外加一个地方记录状态：

| 积木块 | Loop 中的角色 | Codex 实现 | Claude Code 实现 |
|--------|-------------|-----------|-----------------|
| **Automations** | 按计划自动发现和分类任务 | Automations 标签页，结果进入 Triage 收件箱；/goal 持续运行直到条件满足 | 定时任务/cron，/loop，/goal，hooks，GitHub Actions |
| **Worktrees** | 并行 agent 互相不踩文件 | 内置每个线程一个 worktree | `git worktree`，`--worktree` 参数，subagent `isolation: worktree` |
| **Skills** | 把项目知识写下来，每次不用重新解释 | Agent Skills (SKILL.md)，`$name` 或隐式调用 | Agent Skills (SKILL.md) |
| **Plugins/Connectors** | 连接你的真实工具链 | Connectors (MCP) + plugins | MCP servers + plugins |
| **Sub-agents** | 把"写的人"和"检查的人"分开 | TOML 格式在 `.codex/agents/` | `.claude/agents/` 目录，agent teams |
| **State / 记忆** | 记录做了什么、下一步做什么 | Markdown 或 Linear (通过 connector) | Markdown (AGENTS.md, progress files) 或 Linear (通过 MCP) |

---

## 各模块详解

### 1. Automations — 让 loop 真正循环起来

- **Codex Automations 标签页**：选项目、写 prompt、设频率、选环境（本地或后台 worktree）。有发现的结果进 Triage 收件箱，没发现的自动归档
- **Claude Code**：`/loop` 按节奏重跑，`/goal` 持续运行直到条件达成（用另一个小模型检查是否完成，而非写代码的 agent 自己判分），cron 定时，hooks 在 agent 生命周期特定点触发 shell 命令，GitHub Actions 在关笔记本后继续跑

### 2. Worktrees — 让并行不变成灾难

- `git worktree` 是核心：共享同一个 repo 历史，但各自独立的工作目录和分支
- Codex 内建支持，Claude Code 通过 `--worktree` flag 和 subagent `isolation: worktree` 实现
- **瓶颈不在工具，在你的 review 带宽**：能跑多少并行 agent 不取决于工具，取决于你审查代码的能力

### 3. Skills — 不用每次重新解释项目

- 文件夹结构 + SKILL.md，内含指令和元数据
- 可选脚本、参考资料、静态资源
- 一个写得好、紧凑的描述比"聪明"的描述管用
- **Intent Debt**：agent 每次冷启动，不知道的内容会用"自信的猜测"填上。Skill 就是把意图写在外部，让 agent 每次运行都读到

### 4. Plugins & Connectors — loop 触摸你的真实工具

- 基于 MCP 协议，Codex 和 Claude Code 互通
- Connectors 读取 issue tracker、查询数据库、访问 staging API、发 Slack 消息
- Plugins 打包 connectors + skills，一键分享给队友
- **Connectors 是 loop 在真实环境中**采取行动而非"告诉你怎么做"的关键

### 5. Sub-agents — 分离"制作者"和"检查者"

- 写代码的 model 给自己评分过于仁慈。**需要第二个模型用不同的指令（甚至不同的 model）来检查**
- 常见三人组：一个探索，一个实现，一个对照需求验证
- 在 loop 里尤其重要：loop 不在你视线中运行时，可信的验证者是你能走开的唯一理由
- `/goal` 本质上就是 maker/checker 分离用于停止条件的判断

### 6. State — agent 会忘，repo 不会

> "The model forgets everything between runs, so the memory has to be on disk and not in the context. The agent forgets, the repo doesn't."

一个 Markdown 文件或 Linear board，存在于单次对话之外，记录已完成和下一步。所有长期运行的 agent 都依赖这个技巧。

---

## 一个完整的 loop 示例

```
每天早上 Automation 跑在 repo 上
  ↓
调用 triage skill：读取昨日 CI 失败、打开的 issues、最近的 commit
  ↓
写入 findings 到 Markdown 或 Linear board
  ↓
对每个值得做的 finding：
  打开独立的 worktree
  → sub-agent 写修复
  → 第二个 sub-agent 对照 project skills 和已有测试审查
  → Connectors 打开 PR + 更新 ticket
  ↓
解决不了的进入 Triage 收件箱 → 等人类处理
  ↓
State file 记录：尝试了什么、通过了什么、还有什么未解决
  → 明天早上从此处继续
```

> 你设计了一次。你没有手动写任何 prompt 步骤。Loop 在 Codex 和 Claude Code 上都一样，因为积木块是一样的。

---

## Loop 做不到的三件事

### 1. 验证最终还是你的责任
无人值守跑的 loop 也是无人值守犯错的 loop。Maker/checker 分离只是让"做完了"更有意义，但"做完了"是声明，不是证明。

### 2. 理解会退化
Loop 越快地产出你没写的代码，存在的东西和你实际理解的差距就越大。这就是 **Comprehension Debt**——顺畅的 loop 只是让它增长更快。

### 3. 舒适的姿态最危险
当 loop 自我运行时，很容易停止拥有判断，接受它给你的任何东西。这就是 **Cognitive Surrender**。设计 loop 本身是解决方案（如果你带着判断设计），也是加速器（如果你用它来逃避思考）。

---

## 核心观点

> "Build the loop. But build it like someone who intends to stay the engineer, not just the person who presses go."

- 两个人构建完全相同的 loop 会得到完全相反的结果：一个人用它加速自己深刻理解的工作，另一个人用它逃避理解工作
- Loop 设计比 prompt engineering **更难**，不是更简单
- Boris Cherny 的观点不是工作变容易了，而是**杠杆点移动了**

*整理于 2026-06-09，来源 Addy Osmani — Loop Engineering*
