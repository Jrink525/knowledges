---
title: Claude Code 101 for Academic Researchers — Tutorial Notes (CN)
tags: [claude-code, ai, academic-writing, research, interview, 面试]
---

# Claude Code 101 for Academic Researchers 教程笔记

> 原文作者：Mushtaq Bilal, PhD（@MushtaqBilalPhD）
> 原文链接：https://x.com/mushtaqbilalphd/status/2052338632426467550
> 译者整理：Jarvis II
>
> 本文是 Claude Code 系列教程的第一篇（101），面向**零编程基础**的学术研究人员。
> 系列后续：参见 ai-tools/claude-code-102-academic-researchers.md

---

## 概述

**一句话**：Claude Code 是安装在电脑上的 AI 工具，不是浏览器里的聊天机器人——它直接在你的文件夹里工作，能读、能写、能改文件。

| 对比项 | ChatGPT / Gemini（浏览器） | Claude Code（桌面端） |
|--------|---------------------------|----------------------|
| 工作方式 | 你把文件上传给它 | 它直接进入你的文件夹 |
| 持久性 | 每次会话需重复解释背景 | 通过 CLAUDE.md + Auto-Memory 记住你 |
| 文件处理 | 一次几个文件 | 一次处理整个文件夹（45+ PDF） |
| 能力边界 | 只能"说" | 能"做"（创建/编辑文件、重命名、整理） |

---

## Part 1：Claude Code 是什么

### 为什么研究者该关注它？

你电脑上有个文件夹，里面可能有：
- 几十篇 PDF 论文
- 论文草稿
- 电子表格 & 数据集
- 访谈转录文本

传统 AI 用法：打开浏览器 → 上传文件 → 提问 → 关闭浏览器 → 下次再来一遍。

**Claude Code 完全相反**：不是你把文件拿到 AI 面前，而是你把 AI 带进那**个已经有所有文件的文件夹**。

### 学术场景的核心价值

1. **记住你**：你的研究领域、写作风格、不断变化的需求——不用每次重复
2. **批量处理**：一次读 45 篇 PDF 并提取信息，甚至可以创建新文件
3. **处理所有格式**：Word、Excel、PDF 通吃

### 实践场景

- **定性研究**：加载访谈转录 → 提取每个受访者关于某主题的表述 → 跨访谈寻找主题
- **定量研究**：加载 CSV → 清洗数据 → 跑描述性统计 → 解释审稿人的关键评论

### ⚠️ Claude Code 不能做什么

**它不是你的专业判断的替代品**。它可以是你的研究助理，但什么算论据、什么算证据——**那是你的责任**。那些把全部思考和判断外包给 AI 的学者不会成功。

---

## Part 2：安装与首次会话

### 前置条件

- 需要 **Claude Pro 或 Max** 订阅
- 无编程基础要求
- 预留 **15-20 分钟**

### 安装步骤

1. 访问 `claude.com/download`
2. 下载对应版本（Win/Mac），像 Zoom 或 Zotero 一样安装
3. 首次打开 → 浏览器弹出登录 → 授权
4. 界面：左侧对话历史 / 中间聊天面板

### 打开第一个文件夹

点击聊天栏附近的 "Open Folder" → 导航到你的项目文件夹（论文/草稿文件夹）

**新手建议**：创建一个专门的 "Claude Research Assistant"文件夹

⚠️ Claude Code **默认会请求权限**再执行操作（如创建/删除文件）。初期不要关闭权限提示，防止误删重要文件。

### 第一次会话

> Read all the papers in the folder and give me their main arguments as a separate file.

Claude Code 会读取所有文件 → 创建新文件 → 直接出现在文件夹中。

---

## Part 3：CLAUDE.md —— 你的研究助理大脑

Claude Code 启动后第一件事：找 `CLAUDE.md` 文件（注意大写）。这是**你的指令文件**。

### 手动创建

用 Notepad/TextEdit 写好指令，保存为 `CLAUDE.md`：

```markdown
# Role
请以研究助理身份工作。我的研究方向是 XXX，当前项目是 XXX。

# Standards
使用适当学术标准。引用风格使用 APA 第 7 版。

# Writing Style
论文中回复使用正式学术风格，对话中可以使用轻松风格。

# Critique Style
审阅时重点检查：论点是否清晰、证据是否充分、方法论是否可靠。
```

### 自动创建

直接在 Claude Code 中描述你的角色、标准、写作风格、审阅方式，然后说：

> Create a CLAUDE.md file using this information.

Claude Code 自动生成并保存到文件夹。

### Auto-Memory（自动记忆）

- Claude Code 会**自动记笔记**——记录你项目中的偏好和变化
- 每次启动时读取：CLAUDE.md + 自动笔记 → 提供上下文相关回答
- **查看记忆**：`"Tell me what you have stored in your memory."`
- **更新记忆**：直接告诉它更新过时信息

### ❌ CLAUDE.md 避坑

- ❌ 不要放**机密信息**
- ❌ 不要让它变成**过时的配置文件**（每几周更新一次）

---

## Part 4：与研究文档协同工作

### 文件夹不需要完美整理

Claude Code 可以自己整理。但别用 "论文（最终版）（最终版2）（用这个）.docx" 这种文件名。

### 文献综述实战

> Read every PDF in this folder and tell me which articles disagree with the following argument: [粘贴你的论点]

Claude Code 会读所有 PDF → 以表格形式输出结果。

### 系统性文献筛选

把 50 篇文献放进 "Systematic Review with Claude" 文件夹 → 给出纳排标准：

> Screen all the papers according to my inclusion/exclusion criteria.

### 访谈转录分析

定性研究者：把转录文本放入文件夹

> Extract how each respondent answered the question about [主题].

### 繁琐任务外包

> Go through all fifty PDFs and rename them using their titles.

几分钟搞定。

### 让 Claude Code 创建文件

完成重要任务（如筛选论文、提取信息）时，要求它把结果保存为文件：
- 默认格式：Markdown（省空间、方便检索）
- 也支持 Word、Excel

---

## Part 5：Skills（技能）

Skill 是一组指令，让 Claude Code **专精于一项特定任务**。和 CLAUDE.md 一样是纯英文 Markdown 文件。

### 创建 Skill（推荐自动方式）

示例：你有 Zoom 通话转录，想每次提取可执行项。

> Create a Skill for extracting actionable items from Zoom transcripts.

Claude Code 会反问澄清 → 自动创建 Skill 文件 → 重启后即可使用。

### CLAUDE.md vs Skills 对比

| 维度 | CLAUDE.md | Skill |
|------|-----------|-------|
| 范围 | 全局项目配置 | 单个任务专用 |
| 内容 | 你是谁、项目全貌 | 特定任务的精细指令 |
| 调用 | 自动读取 | 自动识别或 `/command` 手动调用 |

**三者协同工作**：CLAUDE.md（全局）→ Skill（专项）→ Auto-Memory（动态），共同产出最优结果。

### ⚠️ 不要委托给 Claude Code 的事

Claude Code 擅长：**劳动密集、耗时、重复性**任务。外包这些给它。

但它**不会**产出真正的学术研究——原创论点仍然是你作为研究者的工作。它可以综合信息供你使用，但提出原创论点是你自己的责任。

---

## 系列总览

| 篇目 | 核心主题 | 链接 |
|------|----------|------|
| 101 | 零基础入门：安装、CLAUDE.md、基本用法 | 本文 |
| 102 | 进阶：目录结构、Subagents、Plan Mode、Hooks | [ai-tools/claude-code-102-academic-researchers.md](./claude-code-102-academic-researchers.md) |

数据：101 文章获 **4.25M 阅读**、**5.8K 赞**、**1.1K 转发**（截至 2026-05-07）
