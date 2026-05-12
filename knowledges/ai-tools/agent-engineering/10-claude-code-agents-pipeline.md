---
title: "10 个 Claude Code Agent 并行流水线 —— 实战清单"
tags:
  - claude-code
  - agent-pipeline
  - pr-reviewer
  - test-generator
  - bug-hunter
  - doc-writer
  - inbox-triage
  - daily-standup
  - cold-outreach
  - content-repurposing
  - agent-pattern
  - practical-guide
  - slash-commands
  - hooks
date: 2026-05-12
source: "https://x.com/zodchiii/status/2054137878968439247"
authors: "@zodchiii"
stats:
  likes: 141
---

# 10 个 Claude Code Agent 并行流水线 —— 实战清单

> **来源：** @zodchiii 的 X 长文  
> **核心论调：** 你的 Claude Code 只发挥了 10% 的潜力。剩下的 90% 是 10 个 Agent 并行运行。

---

## Agent 的三种运行形态

在配置任何 Agent 之前，理解三种形态很重要：

| 形态 | 存放位置 | 触发方式 | 特点 |
|------|---------|---------|------|
| **Slash Command** | `.claude/commands/<name>.md` | 终端输入 `/name` 手动触发 | 按需运行，简单直接 |
| **Hook** | `.claude/hooks/<event>.sh` | Git 事件 / ToolUse 事件自动触发 | 自动化，零人工干预 |
| **Hosted Script** | Claude Agent SDK (24/7 服务器) | 定时/Webhook 触发 | 全天候运行，适合后台任务 |

---

## 10 个 Agent 完整清单

### 1️⃣ PR Reviewer

| 属性 | 值 |
|------|-----|
| 类型 | Slash Command + GitHub Action |
| 文件 | `.claude/commands/review.md` |
| 用法 | 运行 `/review` 或自动触发 |
| 响应时间 | ~90 秒 |

**Prompt：**
```
You are a senior code reviewer. Read the staged diff. Flag: 
hardcoded secrets, missing tests, type errors, obvious bugs. 
Be terse, max 5 comments.
```

**自动化方式：** 安装 `claude-code-action` GitHub Action，指向 `review.md`。

---

### 2️⃣ Test Generator

| 属性 | 值 |
|------|-----|
| 类型 | Slash Command + pre-commit hook |
| 文件 | `.claude/commands/tests.md` |
| 用法 | 写完函数后运行 `/tests <filename>` |
| 产出 | 每个函数 3-5 个测试：happy path + 边缘情况 + 失败路径 |

**Prompt：**
```
Read the function I just wrote. Generate tests in [your framework, 
e.g. Vitest, Pytest]. Cover happy path, 2 edge cases, one error case. 
Match the style of existing tests in this repo.
```

**自动化方式：** 在 pre-commit hook 中扫描 staged 的 `.ts`/`.py` 文件，如无对应测试则自动触发。

---

### 3️⃣ Bug Hunter

| 属性 | 值 |
|------|-----|
| 类型 | Hosted Script (Claude Agent SDK) |
| 运行方式 | 每 5 分钟轮询 Sentry API |
| 输入 | Sentry stacktrace + 相关源码 |
| 产出 | root cause 分析 + git patch 修复 + 回归测试 |
| 设置时间 | ~90 分钟 |

**Prompt：**
```
Read this Sentry stacktrace and the relevant source files. Identify 
the root cause in one sentence. Propose a minimal fix as a git patch. 
Add a regression test if possible.
```

---

### 4️⃣ Doc Writer

| 属性 | 值 |
|------|-----|
| 类型 | Post-merge hook |
| 文件 | `.claude/hooks/post-merge.sh` |
| 行为 | 每次 merge 到 main 后，检查变更是否影响 README/docstrings/docs |
| 产出 | 如有过时文档，生成 git patch 更新 |

**Prompt：**
```
Check README.md, docstrings in changed files, and /docs. 
If any are now wrong or missing info, generate updated versions. 
Output as a git patch.
```

**建议：** 配合一个 `docs.md` skill 文件，描述项目文档风格和结构。

---

### 5️⃣ Refactor Tracker

| 属性 | 值 |
|------|-----|
| 类型 | Slash Command（每周运行） |
| 文件 | `.claude/commands/rot.md` |
| 用法 | 每五运行 `/rot`，周一早上处理 |
| 扫描内容 | TODO（30+ 天）、FIXME、>500 行文件、>80 行函数、重复字面量 |

**Prompt：**
```
Scan the repo. Find: TODOs older than 30 days, FIXMEs, files over 
500 lines, functions over 80 lines, duplicated string literals 
appearing 3+ times. Output as a Markdown table sorted by priority. 
Add an effort estimate (S/M/L) for each.
```

---

### 6️⃣ Daily Standup Agent

| 属性 | 值 |
|------|-----|
| 类型 | Hosted Script（每早 8 点） |
| 数据源 | GitHub commits + Linear tickets + 日历 |
| 产出 | 4 行日报 |

**Prompt：**
```
Summarize in 4 lines max. Yesterday I did X. Today I'm working on Y. 
Blocked on Z. Next priority: W. Skip anything trivial.
```

---

### 7️⃣ Customer Feedback Synthesizer

| 属性 | 值 |
|------|-----|
| 类型 | Hosted Script（每周日 6pm） |
| 数据源 | Intercom + X 提及 + 产品评论 |
| 产出 | 5-10 个主题聚类，含频率排名 + 原文引用 |

**Prompt：**
```
Cluster these into 5-10 themes. For each theme, give a one-line 
summary, count, and one verbatim quote from source. Rank by frequency.
```

---

### 8️⃣ Cold Outreach Personalizer

| 属性 | 值 |
|------|-----|
| 类型 | Hosted Script（Webhook 触发） |
| 数据源 | CRM 新线索 → 公司主页 + LinkedIn + 最近 3 条 X |
| 产出 | 个性化 4 行冷邮件草稿 |

**Prompt：**
```
Write a 4-line cold email. Reference one specific real thing about 
this person (their company, recent post, or shipped product). 
No generic openers. No "I noticed you...". Sign off as [your name].
```

---

### 9️⃣ Content Repurposer

| 属性 | 值 |
|------|-----|
| 类型 | Slash Command |
| 文件 | `.claude/commands/repurpose.md` |
| 用法 | 运行 `/repurpose blog-post.md` |
| 产出 | 3 条 X + 1 条 LinkedIn + 1 Telegram + 1 简讯 + 5 备选标题 |

**Prompt：**
```
Read the input file. Output 5 sections: (1) 3 X tweets, each under 
280 chars, (2) 1 LinkedIn post 100-150 words, (3) 1 Telegram note 
in casual voice, (4) 1 newsletter intro paragraph, (5) 5 alt 
headlines. Match my voice from [link to 3 examples].
```

**关键：** "voice" 部分是秘诀——提供 3 篇你真实写作的例子，锁定风格。

---

### 🔟 Inbox Triage Agent

| 属性 | 值 |
|------|-----|
| 类型 | Hosted Script（每 30 分钟） |
| 数据源 | Gmail 未读邮件 |
| 分类 | today / this-week / fyi / archive |
| 产出 | today 和 this-week 的 3 行草稿回复 |

**Prompt：**
```
Classify this email as [today / this-week / fyi / archive]. 
If today or this-week, write a 3-line draft reply in my voice. 
Match the formality of the sender. Don't sound like AI.
```

---

## 部署策略对比

### 本地运行（Slash Command + Hook）

| Agent | 类型 |
|-------|------|
| PR Reviewer | Slash Command |
| Test Generator | Slash Command + pre-commit |
| Doc Writer | Post-merge hook |
| Refactor Tracker | Slash Command |
| Content Repurposer | Slash Command |

这 5 个触发时运行，用完退出，零基础设施。

### 24/7 托管运行

| Agent | 运行频率 | 数据源 |
|-------|---------|--------|
| Bug Hunter | 每 5 分钟 | Sentry/Linear |
| Daily Standup | 每早 8 点 | GitHub + Linear + Calendar |
| Cold Outreach | Webhook | CRM → LinkedIn + X |
| Feedback Synthesizer | 每周日 6pm | Intercom + X + Reviews |
| Inbox Triage | 每 30 分钟 | Gmail |

这 5 个需要你睡着时也在跑。常见失败模式：
- Cron 在 macOS 更新的凌晨 4 点停止
- VPS 在周六宕机
- Sentry 告警在你吃饭时堆积

---

## 实用建议

### 不要一个周末全部装完

> 选这周最痛的 2 个。PR Reviewer 和 Inbox Triage 对大多数人是最高杠杆。
> 然后每周加一个。到第 3 个月，一个人就在运行 10 Agent 流水线了。

### 两种思路对比

| 思维模式 | 影响 |
|---------|------|
| Claude Code Agent = 聊天窗口 | 10% 的使用率 |
| Claude Code Agent = 工作描述 + 触发器 + 输出 | 3x 的产出效率 |

### 与知识库其他文章的关联

- **[Agent Complexity Ratchet](agent-complexity-ratchet.md)** — Garry Tan 的"14 个 PR / 72 小时"背后就是这个级别的自动化。本文提供了具体的 Agent 配置方法。
- **[Skillify Skill Engineering Guide](skillify-skill-engineering-guide.md)** — 本文的 refactor-tracker、doc-writer、test-generator 正是 Skillify 中"Skillify 每个工作流"的实例。你写了 SKILL.md/slash command，Agent 下次自动找到它。
- **[Agent Engineers Survival Guide](agent-engineers-survival-guide.md)** — @rohit4verse 说的"5 个命名良好的工具 > 20 个普通工具"与本文的"周末先搞 2 个"完全一致：从小处入手，从最痛的失败模式入手。

---

> ⚠️ 注意：本文末尾提及 Teamly 平台作为托管方案，是其团队的商业产品。核心价值在于 10 个 Agent 的设计思路和 Prompt 模板，托管方案可根据实际需求选择。
