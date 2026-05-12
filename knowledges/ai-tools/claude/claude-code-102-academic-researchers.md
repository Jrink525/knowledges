---
title: Claude Code 102 for Academic Researchers — Tutorial Notes (CN)
tags: [claude-code, ai, academic-writing, research, interview, 面试]
---

# Claude Code 102 for Academic Researchers 教程笔记

> 原文作者：Mushtaq Bilal, PhD（@MushtaqBilalPhD）  
> 原文链接：https://x.com/mushtaqbilalphd/status/2053829787219595725  
> 译者整理：Jarvis II  
> 本文是 Claude Code 系列教程的第二篇（102），建立在 101（4M+ 阅读量）基础上，面向学术研究人员。

## 概览

Claude Code 是 Anthropic 推出的 AI 编程助手，但作者认为它同样适合学术写作场景——**不需要任何编程基础，只要会用英语写句子，就能用 Claude Code。**

101 教程：打开一个文件夹 → 放入 PDF → 写一个 CLAUDE.md 配置文件  
102 教程：**构建大型学术项目**（长篇论文/专著/博士论文），解决以下问题：

| 问题 | 解决方案 |
|------|----------|
| 一个 CLAUDE.md 无法应对多种任务 | 全局 + 局部 CLAUDE.md 嵌套 |
| 重复性研究任务繁琐 | Custom Slash Commands（自定义斜杠命令） |
| 上下文窗口污染 | Subagents（子代理） |
| 工具碎片化 | MCP Connectors（连接器） |
| 忘记备份、定期扫描 | Hooks + Scheduled Tasks（钩子 + 定时任务） |

---

## Part 1：使用子文件夹组织大型项目

### 核心原则

不要把所有文件放在一个文件夹里，否则 Claude 只能给出同质化的回答。就像你不会让研究助理同时做三件不同的事一样。

### 推荐目录结构

```
My Dissertation/
├── CLAUDE.md                  ← 全局配置文件（项目宪法）
├── Literature/                ← PDF 和文献笔记
│   └── CLAUDE.md              ← 局部指令：格式化输出风格
├── Chapters/                  ← 各章节草稿
│   └── CLAUDE.md              ← 局部指令：MLA 引用、审阅格式
├── Data/                      ← 数据集
│   └── CLAUDE.md              ← 局部指令：不覆盖原始文件
├── Notes/                     ← 会议记录和想法
│   └── CLAUDE.md              ← 局部指令：bullet point 格式
└── Correspondence/            ← 导师邮件、合著者沟通、审稿意见
    └── CLAUDE.md              ← 局部指令：优先处理共同意见
```

### 全局 vs 局部 CLAUDE.md

- **全局（项目根目录）**：描述你是谁、项目全貌——精确但不啰嗦，相当于"宪法"
- **局部（子文件夹内）**：针对该文件夹的特定任务指令，不污染主文件
- **嵌套机制**：Claude Code 在子文件夹工作时会**同时读取两个** CLAUDE.md 文件

### 局部 CLAUDE.md 示例

```markdown
# Chapters/CLAUDE.md
如果让你审阅我的草稿，请按这个结构：论点、证据、文献综述、反驳论点。
引用风格默认 MLA 第 9 版，除非我特别指定。

# Data/CLAUDE.md
所有 CSV 和 Excel 文件视为原始数据，除非我另有说明。
永远不要覆盖原始文件。清洗后的版本文件名加 _clean 后缀。

# Correspondence/CLAUDE.md
始终优先处理审稿意见和合著者建议中共同提到的点。
```

### 输出风格定制

在局部 CLAUDE.md 中指定输出格式：
- **Literature 文件夹**：要求 Claude 以表格格式输出（Argument | Evidence | Relevance）
- **Notes 文件夹**：要求 bullet point 格式
- **Chapters 文件夹**：要求结构化审阅

### 实战练习

```bash
在 Claude Code 中打开项目根目录，输入：
"Read the five papers that I added to the Literature subfolder today
and tell me which ones support or refute my arguments in
'Chapter 3 – Outline.md' in the Chapters subfolder."
```

Claude Code 会自动读取全局 CLAUDE.md + Literature 和 Chapters 的局部 CLAUDE.md 进行跨文件夹分析。

### ❌ 不要做

- 不要在全局和局部 CLAUDE.md 中**重复指令**（浪费 token）
- 不要让局部指令**与全局冲突**（Claude 会选择更具体的，但你会困惑）

---

## Part 2：Plan Mode 与 Custom Slash Commands

学术项目中的任务分为两类：

| 任务类型 | 特点 | 适合工具 |
|----------|------|----------|
| 复杂一次性任务 | 步骤多、跨文件夹、产出长 | Plan Mode |
| 重复性任务 | 每天都在做 | Custom Slash Commands |

### Plan Mode（计划模式）

**解决的问题**：复杂任务一旦 Claude 误解指令，你只有等它执行完才发现问题。

**工作方式**：Claude Code 不是立即执行，而是**先写出分步计划**让你审阅，你同意后再执行。可以修改计划。

**启用方式**：
- 聊天栏下方的 permissions 菜单中点击 Plan Mode
- 快捷键 `Ctrl + Shift + M`
- 或在 prompt 中直接要求 "Show me a plan before executing"

**适用场景**（包含 3+ 个步骤、涉及多个子文件夹的任务）：
- 综合 35 篇论文的笔记
- 系统性综述的文献筛选
- 清洗数据集并生成 codebook

### Custom Slash Commands（自定义斜杠命令）

**解决的问题**：重复性任务每次都要写长 prompt。

**概念**：Slash Command 就是一段用英文写的指令集合，封装成一个快捷命令（`/命令名`）。

**Claude Code 内置命令**：在输入框中打 `/` 即可看到（如 `/schedule`）

**创建方式**：直接在 Claude Code 中输入：

```bash
Create a Slash Command called /firstdraft that converts my raw notes
in my Notes folder into cohesive and coherent paragraphs without any
redundant words or phrases.
```

Claude Code 会在 `.claude/commands/` 目录下生成一个 `.md` 文件。重启 session 后输入 `/` 就能看到它。

### ❌ 不要做

- 不要为半年才用一次的**低频任务**写命令（会占满菜单且过时）
- 不要在一个 Slash Command 文件中放**多步骤长指令**（一行命令管一个任务，超过 15 行就应该拆成两个）
- 复杂长任务**不要跳过 Plan Mode**

---

## Part 3：Subagents 并行研究任务

### 为什么一个助理不够？

1. **Context Clutter（上下文污染）**：读取 20 篇 PDF 后，所有内容都在对话上下文中。再让 Claude 写 Chapter 4 的 outline，响应会变慢且不清晰。
2. **只能串行**：如果你想要三个独立的同行评审意见（理论家、信息学家、毒舌审稿人），你不能依次要求——每个评审都会影响下一个。

### Subagent 是什么？

Subagent（子代理）是 Claude Code 的一个**专门化版本**，有：
- **自己的指令文件**（存储在 `.claude/agents/` 目录下的 `.md` 文件）
- **自己的上下文窗口**（不会污染主 session）

> 主 session 把任务派发给 subagent → subagent 用自己的上下文处理 → 只把最终结果返回给主 session。整个过程都在 subagent 内部完成。

### 与 Slash Command 的区别

| 特性 | Slash Command | Subagent |
|------|---------------|----------|
| 有自己的上下文 | ❌ 无 | ✅ 有独立上下文窗口 |
| 读取 CLAUDE.md | ✅ 读取 | ❌ 不读取（用自己的指令文件）|
| 适用场景 | 重复性简单任务 | 复杂独立任务 |

### 学术场景推荐 Subagent

- **Literature Reviewer**：读取 Literature 文件夹新 PDF，根据你的论点输出结构化摘要
- **Citation Checker**：拿一章草稿，核验每处引用是否在 Literature 文件夹中有对应来源，标出缺失引用
- **Methodology Auditor**：实证项目的 methodology 审查
- **Reviewer 2**：扮演毒舌审稿人审阅你的草稿

### 创建 Subagent

```bash
Create a subagent called Citation Checker. It will take a draft from
the Chapters folder, list every in-text citation, verify each one
against papers in the Literature folder. Then it will create a
markdown file with missing references. The subagent must never edit
or change the draft.
```

文件路径：`.claude/agents/citation-checker.md`

**调用方式**：在主 session 中输入 `"Use Citation Checker on chapter_4.md in the Chapters folder."`

### 并行审阅实战

```bash
In parallel, get Methodology Auditor and Reviewer 2 to read and
critique chapter_4 in the Chapters folder and give me review reports.
Save the two reports as chapter_4_critiques under the subagent's name
in the same folder.
```

两个 subagent 会**各自独立**地审阅 → 输出两个独立的审阅报告文件。主 session 的上下文没有任何污染。

### ❌ 不要做

- 不要为**微小任务**创建 subagent
- 不要让 subagent **职责重叠**
- **永远不要让 subagent 编辑你的草稿**——subagent 应该以**独立文件**形式输出报告

---

## Part 4：MCP Connectors（连接外部 App）

Claude Code 默认只在项目文件夹内工作，但学术项目涉及多个工具：Zotero、Google Drive、Zoom 等。

### MCP（Model Context Protocol）

Anthropic 2024 年推出的协议，让 AI 应用与外部工具交互。你不需要理解 MCP 如何工作，只要知道怎么连接。

### 连接步骤

1. 打开 Claude Code → 左上角 "Customize"
2. 选择 "Connect your apps"
3. 在 Connectors 列表中找到需要的应用（如 Zoom、Google Drive）
4. 授权权限

### 实战：连接 Zoom

```bash
Pull the transcript of the three recent calls I had with my colleague.
Extract all comments related to Chapter 4 in Drafts. Save all extracted
comments in a new file in the Correspondence folder with today's date.
```

### Connector + Subagent 组合

```bash
设置一个 Literature Reviewer subagent，通过 PubMed MCP connector
自动抓取最新的相关论文。
```

### ❌ 不要做

- 不要安装太多 Connectors（只装项目相关的）
- 不要连接包含**未发表机密数据**的应用（如 Slack）

---

## Part 5：Hooks 与 Scheduled Tasks

### Hook（钩子）

Hook 是一段指令，**当特定事件发生时自动触发**。设置后不需要手动调用。

**示例：自动备份钩子**

```bash
Set up a pre-edit safety hook that copies a chapter and saves its
current version before it starts editing it.
```

设置完成后，再执行：
```bash
Edit Chapter_4.md in Drafts in light of the comments in the
transcript of today's Zoom meeting.
```

→ Hook 会自动：备份原文件 → 放在 backup 文件夹 → 再编辑 Drafts 中的副本

### Scheduled Tasks（定时任务）

用于**周期性执行**的任务。

**示例：每周文献扫描**

```bash
Create a Scheduled Task that runs every Monday morning at 9am.
It should use the PubMed MCP to pull new papers on social media
and mental health published in the last week.
It should then hand over the papers to the Literature Review subagent
to screen them.
Save the screening table to a subfolder called Weekly Scans in the
Literature folder.
```

### ❌ 不要做

- 不要设置涉及**删除文件**的 Hook 或 Scheduled Tasks
- 不要创建**太多 Hook**（记不住）
- 不要为**没做过至少 4 次**的任务设置自动化

---

## 总结：学术写作中的 Claude Code 工具选择

```
                任务复杂度？
                    │
         ┌──────────┴──────────┐
         │                     │
       简单                 复杂但周期短        复杂且周期长
         │                     │                    │
    直接提问             Custom Slash          Plan Mode + Subagent
                         Command
```

```
是否涉及外部工具？
    │
    ├── 是 → MCP Connector 连接
    │
    └── 否 → 项目内直接处理

是否需要自动触发？
    │
    ├── 事件触发 → Hook
    │
    └── 定时触发 → Scheduled Task
```

## 对比：Claude Code 101 → 102 → 后续

| 版本 | 核心主题 | 学习目标 |
|------|----------|----------|
| 101 | 单文件夹 + 单个 CLAUDE.md | 入门：打开、读 PDF、写配置 |
| 102 | 多文件夹 + 嵌套指令 | 进阶：结构、自动化、并行、集成 |
| (103+) | TBD | TBD |
