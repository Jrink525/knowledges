---
title: "用 Claude Code 学习任何领域：把学习变成一个可运行的项目"
tags:
  - claude-code
  - learning
  - workflow
  - ai-tools
date: 2026-06-11
source: "https://x.com/voxyz_ai/status/2064703822774010257"
authors: "Vox (@Voxyz_ai)"
---

# 用 Claude Code 学习任何领域：把学习变成一个可运行的项目

> **来源：** [How to Use Claude Code to Learn Any Field: Turn Learning Into a Project That Runs](https://x.com/voxyz_ai/status/2064703822774010257)

---

一个本地仓库，一个 CLAUDE.md，一个 progress.md。每天你打开项目，Claude Code 读取进度、分配任务、检查输出、更新复习日志。

## 问题

大多数人在用 AI 学习时是同样的方式：

> "给我解释一下 AI Agent。"

AI 给你一段解释。你感觉懂了。第二天，换个问题，又回到原点。笔记散落在聊天记录里，概念从来不牢固，错误从来不被复习，项目从未向前推进。最后你得到一堆听起来合理的答案，但没有学习系统。

## 解法

**用 Claude Code 学习的正确方式是：把学习变成一个本地项目。**

规则放进 CLAUDE.md，进度放进 progress.md，资料放进 02_sources/，概念放进 03_notes/，练习放进 04_exercises/，然后用交付一个小项目来证明你学会了。

Claude Code 读写项目目录的文件、运行命令、每次启动通过 CLAUDE.md 加载同一套规则、把可复用工作流打包成 Skill、跨子 Agent 拆分任务。它是一个在你本地项目上操作的 Agentic 编码工具。

你不用每天跟 AI 重新开始。你打开仓库说一句话：

```
Based on progress.md, plan today's learning session.
```

Claude Code 就在昨天停下的地方继续。

---

## 方法的一句话总结

> **用 Claude Code 为一个领域创建一个本地学习仓库。**

仓库至少包含 6 样东西：知识地图、源材料、概念笔记、练习、项目交付物、复习日志。

---

## 第 1 步：搭建仓库，编写规则

以学习 AI Agent 为例：

```bash
mkdir learn-ai-agent && cd learn-ai-agent && claude
```

然后让 Claude Code 创建学习仓库：

```
I want to learn AI Agents.

Create a minimal learning repo in the current directory:

./├── CLAUDE.md          # learning rules
├── README.md          # repo description
├── 00_goal.md         # learning goals, time commitment, final deliverable
├── 01_map.md          # domain knowledge map
├── 02_sources/        # source materials
├── 03_notes/          # core concept notes
├── 04_exercises/      # exercises and quizzes
├── 05_project/        # final project
├── 06_reviews/        # milestone tests and reviews
└── progress.md        # progress, mistakes, weak spots, next steps

Only generate Day 1 tasks. Do not generate the entire course at once.
Day 1 tasks should include: reading, concept explanation, exercises, output, acceptance criteria.
```

**关键约束：** 只让它生成 Day 1 的任务，不要一次性生成 30 天。学习系统不是一次建成的，是每天使用、每天修正建成的。

> 在空目录开始，别在公司代码库、客户文件或密钥附近搞这个。学习仓库只应有公开材料、匿名数据和你自己的练习输出。

仓库建好后，把长期规则写入 **CLAUDE.md**：

```markdown
# CLAUDE.md

You are my domain learning engineer.

Goal: help me build beginner-level understanding of AI Agents in 30 days
       and complete a presentable small project.

## Working principles

1. At the start of every session, read 00_goal.md, 01_map.md, and progress.md.
2. Every learning session must include: concepts, examples, exercises,
   an output task, and acceptance criteria.
3. Max 3 core concepts per day. More than that becomes information hoarding.
4. At the end of every session, update progress.md: what I learned,
   what I got wrong, the error type, and what to cover next.
5. When I get something wrong, classify the error: concept gap / can't apply /
   can't articulate / knowledge confusion / missing background.
6. Don't assume I understood. Verify through exercises, rephrasing,
   and project output.
7. Solidify important concepts into 03_notes/.
8. Run a milestone test once a week, save results to 06_reviews/.
9. The ultimate goal is to complete a presentable project in 05_project/.
```

> ⚠️ **常见错误：** Claude Code 读的是 `CLAUDE.md`，不是 `AGENTS.md`。如果项目已有 AGENTS.md，可以在 CLAUDE.md 里用 `AGENTS.md` 引入。

CLAUDE.md 在每次会话启动时作为上下文加载。Claude Code 读到规则后，把项目当学习项目对待，不是闲聊。

---

## 第 2 步：先画地图

学习新领域最常见的错误是直接问"什么是 AI Agent？"

你得到百科式的答案。你感觉明白了，但对领域边界毫无概念。

更好的第一步：让 Claude Code 生成领域知识地图并保存到 **01_map.md**。地图应该回答：

- 这个领域解决了什么问题
- 最重要的 20 个概念
- 它们之间的关系
- 初学者最容易混淆的 10 对概念
- 从入门到项目就绪的阶段

初学者需要知道**跳过什么**。地图给你这个。Claude Code 把材料压缩成结构：

> **必须先学的 20%，现在跳过的 60%，项目做完再回来补的 20%。**

---

## 第 3 步：每日输入-输出循环

不要问"今天教我一些 AI Agent 的内容"——太模糊了，Claude Code 会给你一篇论文。

而是说：

```
It's Day 3. Read progress.md first, then plan today's session.

Requirements:
1. Review yesterday's weak spots.
2. Max 3 new concepts, each with examples and exercises.
3. One task I can finish in 60 minutes.
4. Give me acceptance criteria.
5. Update progress.md when we're done.
```

Claude Code 每次先检查你的进度，再决定教什么。你昨天把 Tool Use 和 Function Calling 搞混了？今天先补那个。你能解释概念但不会实现？砍掉讲座、加任务。同类型问题连续错两次？降低难度。

几天后，**progress.md** 看起来像这样：

```markdown
# Learning Progress

## Day 3

### What I learned
- The full Tool Use flow: define → call → execute → return
- The difference between Function Calling and Tool Use
- Basic structure of an Agent loop

### What I got wrong
- Confused the trigger mechanism of Tool Use vs Function Calling
  - Error type: concept gap
  - Fix: reread 03_notes/tool-use-vs-function-calling.md

### Weak spots
- Can't clearly explain "stop conditions" in an Agent loop
- Can't implement even the simplest tool call in code

### Next steps
- Day 4: Agent stop conditions + build a single-tool agent
- Redo: explain Tool Use vs Function Calling in my own words
```

progress.md 是下次规划的输入。每次会话后更新，Claude Code 下次读它来知道你在哪卡住了。

---

## 第 4 步：建一个小项目

你直到能**动手建东西**才算真正了解一个领域。学习仓库必须有 **05_project/**。

项目越小越好，但必须完整：能跑、能给别人看。

| 领域 | 小项目 |
|------|--------|
| AI Agent | 一个研究助手 |
| 数据分析 | 一个销售仪表盘 |
| 写作 | topic → outline → draft → edit 工作流 |
| Prompt 工程 | 一个 Prompt 模板库 |

让 Claude Code 基于 progress.md 设计项目，保存到 `05_project/project_plan.md`。计划包括：名称、核心功能、每日任务、验收标准、如何展示。

---

## 第 5 步：让 Claude Code 当考官

大多数人卡住是因为从不受测。完成一个阶段后，不要继续加新内容。让 Claude Code 考你：

```
Stop teaching new material. You are now the examiner.

Based on the learning repo, create a milestone test: multiple choice,
concept explanations, scenario applications.
Give me the questions first. I'll answer, then you grade.
Classify each error type and write weak spots to progress.md.
Save the test record to 06_reviews/.
```

你需要找出那些你以为懂了、其实没懂的东西，以及你能跟着理解但不能独立做的东西。测试中发现的首点盲区永远比你预期的多。

---

## 第 6 步：复用和升级

在多个领域使用这个方法后，可以打包成 **Claude Code Skill**。Skill 是 Claude Code 的扩展：创建 SKILL.md，Claude Code 在相关上下文中使用它。也可以直接用 `/skill-name` 调用。内容只在需要时加载，比都塞进 CLAUDE.md 省上下文。

打包后，开始一个新领域只需一句话：

```
/domain-learning-master

Field: data analysis
Background: know Excel, no Python
Daily time: 45 minutes
Goal: do basic analysis independently
Final project: sales data dashboard
```

> ⚠️ 注意：命令名来自目录名 `domain-learning-master`，不是 SKILL.md 里的 name 字段。全局 Skill 放 `~/.claude/skills/`，项目级放 `.claude/skills/`。

### 可直接复制的 SKILL.md

```markdown
---
name: domain-learning-master
description: When the user says "I want to learn a field," create a sustainable
  learning repo in the current directory and generate Day 1 tasks.
---

# domain-learning-master

You are a domain learning engineer. Based on the user's field, background,
time, and goals, create a learning repo in the current directory and
kick off Day 1.

## Input

User provides:
- Field
- Current background
- Daily time available
- Learning goal
- Final project

## Workflow

1. Create repo structure: CLAUDE.md / progress.md / goal / map / sources /
   notes / exercises / project / reviews.
2. Write learning rules into CLAUDE.md.
3. Set up progress.md with templates for progress, mistakes, weak spots,
   and next steps.
4. Generate a domain knowledge map in 01_map.md.
5. Only generate Day 1 tasks. Do not generate the entire course at once.
6. Every day must have a deliverable.
7. Schedule a milestone test every 7 days.
8. Guide the user toward completing a presentable small project.

## Ongoing use

User opens the repo each day and says: "Based on progress.md, plan today's
learning session."
```

### 进阶配置

更高级的可以加 **Subagent**（source-scout 找材料、concept-checker 验证理解、examiner 出题评分）和 **Hooks** 做硬约束。Stop Hook 可以检查 progress.md 是否更新了才允许完成。SessionEnd Hook 可以在关闭会话时保存日志。

> **先把基础跑通。** 一个 CLAUDE.md + 一个 progress.md 就够跑学习循环。复用多个领域再加 Skill。材料足够多了再加 Subagent。

---

## 30 天节奏

不要承诺"30 天精通任何领域"。30 天能做的事：

| 阶段 | 内容 | 产出 |
|------|------|------|
| **第 1 周：建地图** | 了解领域全貌、哪些概念最重要、哪些可以跳过 | 01_map.md、20 个核心概念、第一轮错误 |
| **第 2 周：拆解概念 + 示例** | 每天 2-3 个概念 + 示例 + 练习 | 03_notes/、04_exercises/、第一次里程碑测试 |
| **第 3 周：建最小项目** | 停止堆理论，压缩前两周所学到一个小项目 | 05_project/ 第一个可运行版本 |
| **第 4 周：测试 + 修补 + 展示** | Claude Code 当考官、找盲点、加练习、打磨出可展示成品 | 项目 README、演示笔记、评审报告 |

每天完成一个循环：学一点 → 练一点 → 交一个交付物 → 被测试 → 更新进度。

> 每天的目标：留下一件可以被检查的东西。

---

## 万能 Prompt

学习任何领域，直接用这个：

```markdown
I want to use Claude Code to learn a new field.

Field: {填写}
Background: {填写}
Daily time: {填写}
Goal: {考试 / 工作 / 建项目 / 写作}
Final project: {想做什么，或让 AI 推荐}

Create a learning project in the current directory:

1. Create minimal repo structure (CLAUDE.md / progress.md / goal / map /
   sources / notes / exercises / project / reviews)
2. Write learning rules into CLAUDE.md
3. Set up progress template in progress.md
4. Generate domain knowledge map in 01_map.md
5. Only generate Day 1 tasks, not the entire course
6. Every day must have a deliverable
7. Weekly milestone tests
8. Ultimate goal is completing a presentable small project
```

---

## 最后

打开终端，现在就开始：

```bash
mkdir learn-whatever-you-want && cd learn-whatever-you-want && claude
```

粘贴上面的万能 Prompt，跑 Day 1。仓库建好后，你每天只需要一句话：

> **"Based on progress.md, plan today's learning session."**

你的笔记在累积，盲点在缩小。30 天后你有一个可以持续迭代的仓库和一个可以展示的项目。

> 更多 Agent 构建笔记见：[voxyz.ai/insights](https://voxyz.ai/insights)
>
> — Vox ❤️

---

*Processed on 2026-06-11 from [X article by @Voxyz_ai](https://x.com/voxyz_ai/status/2064703822774010257)*
