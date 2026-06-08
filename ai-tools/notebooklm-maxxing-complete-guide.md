---
title: "你应该 NotebookLM Maxxing —— 完整上手指南"
tags:
  - NotebookLM
  - Google AI
  - AI工具
  - 知识管理
  - 工作流
  - 提示工程
date: 2026-05-14
source: "https://x.com/hooeem/status/2054652562867896520"
authors: "hoeem (@hooeem)"
---

# 你应该 NotebookLM Maxxing —— 完整上手指南

> **来源：** [you should be NotebookLM maxxing.](https://x.com/hooeem/status/2054652562867896520) 作者：hoeem (@hooeem)

![封面图片](../image/notebooklm-maxxing-cover.jpg)

只有 **2.1%** 的人在积极使用 NotebookLM，而其他人都在用 Claude 和 ChatGPT——但这 2.1% 的人正在全方位碾压你。

他们在用"有根有据的知识"（grounded knowledge）做这件事，而这篇完整的课程会让你也做到。

这是一份关于 NotebookLM 的完整课程。这篇**极其极其极其**详尽的文章涵盖了：

- ✅ 深度分析
- ✅ 27 个实用的使用场景（本篇覆盖 19 个）
- ✅ 我的提示词库
- ✅ 我的主工作流
- ✅ 可选的精通引导课程（文末）

> **是的，内容非常多。**
> **是的，你会反复回看这篇文章。**
> **是的，这是金子，我们开始吧！！**

---

## 一、什么是 NotebookLM？

NotebookLM 最好的理解方式是：一个**以信源为锚点的工作空间**（source-grounded workspace）。

你上传可信的材料，NotebookLM 帮你**提取、组织、比较、综合和转换**这些材料，输出结构化的成果。

### 它能做什么？

- 从上传的信源中提取知识
- 构建研究矩阵和数据表
- 把信源集转化为课程、指南和 SOP
- 从密集材料中创建学习系统
- 生成 Studio 资产：音频概览、视频概览、报告、数据表、闪卡、测验、幻灯片、信息图、思维导图
- 为外部 AI 助手创建可复用的知识文件
- 将客户、业务或研究材料转化为精良交付物
- 将杂乱信息转化为可复用、可教学、可分享、可导出的结构化输出

NotebookLM 的强大之处在于：**它是信源锚定的，且可引用核查**。这种锚定大大降低了幻觉风险，提高了输出质量。

### NotebookLM 的七层体系

NotebookLM 把可信信源材料转化为结构化知识资产。把它当做一个**分层系统**来使用：

- **输入层（Input layer）：** 上传可信信源
- **推理层（Reasoning layer）：** 用 Chat 提取、比较和综合
- **捕获层（Capture layer）：** 将有用的输出保存为笔记（Notes）
- **复合层（Compounding layer）：** 把优质的笔记转化成信源
- **资产层（Asset layer）：** 生成报告、表格、闪卡、测验、幻灯片、音频、视频、信息图和思维导图
- **部署层（Deployment layer）：** 导出到 Docs、Sheets、PDF、PPTX、Markdown、Notion、Obsidian 或其他系统
- **扩展层（Scaling layer）：** 当项目超出 NotebookLM 原生边界时，使用 Gemini、Claude、Custom GPTs、Zotero、Obsidian 或 Notion

### 本文适合谁？

- **初学者：** 想理解 NotebookLM 但不想把它当普通聊天机器人用
- **中级用户：** 想要可重复的工作流——学习、研究、写作、内容创作、运营
- **专家用户：** 想构建知识管线、课程材料、客户交付物、AI 助手文件和长期研究资产

### 学完后你能做什么？

将上传的信源转化为：知识库 / 课程 / 深度分析 / 指南 / 研究矩阵 / 学习系统 / SOP / 咨询报告 / 幻灯片 / 音频简报 / 公开笔记本 / 内容引擎 / AI 助手知识文件 / 书籍大纲 / 个人知识系统

---

## 二、NotebookLM 如何工作？

NotebookLM 有六个工作层级。

### 第 1 层：信源（Sources）

信源是输入层。上传的 PDF、文档、网页、视频、音频、电子表格、图片或粘贴的文本，定义了笔记本的知识边界。

- **坏信源 = 坏输出**
- **好信源 = 好输出**
- **精选信源永远胜过随机倾倒**

### 第 2 层：对话（Chat）

对话是推理和综合层。在这里提问、提取信息、比较信源、测试想法、生成结构化答案。

**用途：** 信源盘点 / 提取 / 综合 / 矛盾映射 / 声明审计 / 大纲 / 提示词 / 检查清单 / 草稿报告 / 验证

> **不要一开始就说"概括所有内容"。** 从盘点、提取和结构化开始。

### 第 3 层：笔记（Notes）

笔记是捕获层。保存有价值的输出，不让它们消失在长对话中。

**用途：** 保存的大纲 / 提取的框架 / 信源摘要 / 模块计划 / 经过验证的声明 / 最终草稿 / 项目决策

一个好的笔记不仅仅是保存的回答——它是**可复用的项目记忆**。

### 第 4 层：笔记转化为信源（Notes → Sources）

这是**复合层**，也是 NotebookLM 最强大的工作流之一。

你可以把回答保存为笔记，再把笔记转化为信源。这样就能分阶段构建知识资产。

**示例：**

1. 提取所有框架
2. 保存提取结果为笔记
3. 将笔记转化为信源
4. 让 NotebookLM 用这个新的框架信源作为结构来构建课程

**NotebookLM 不再是单次问答工具，而是一个分阶段的知识构建系统。**

### 第 5 层：工作室（Studio）

工作室是资产生成层。把信源锚定的材料转化为：

报告 / 数据表 / 学习指南 / 闪卡 / 测验 / 思维导图 / 音频概览 / 视频概览 / 幻灯片 / 信息图

工作室让 NotebookLM 从阅读助手变成生产工具。

> **但不要让工作室驱动策略。** 先提取 → 再综合 → 最后生成资产。

### 第 6 层：导出和部署（Export & Deployment）

资产构建完成后，移到合适的目的地：

- **Google Docs** → 报告和指南
- **Google Sheets** → 表格和矩阵
- **PPTX/PDF** → 幻灯片
- **Markdown** → Obsidian、Notion、Claude Projects、Custom GPTs
- **MP3** → 音频概览
- **公开笔记本链接** → 客户或受众分享
- **HTML**

NotebookLM 擅长综合，但**不一定是存储这些信息的地方**——个人 Wiki 更好！

---

## 三、功能速查

| 想要做什么 | 用什么功能 |
|-----------|-----------|
| 从信源中提取知识 | Chat |
| 比较多个信源 | Chat |
| 生成报告 | Studio → Report |
| 生成表格 | Studio → Data Table |
| 生成学习指南 | Studio → Study Guide |
| 生成闪卡 | Studio → Flashcards |
| 生成测验 | Studio → Quizzes |
| 生成思维导图 | Studio → Mind Map |
| 生成音频讨论 | Studio → Audio Overview |
| 生成视频概览 | Studio → Video Overview |
| 生成幻灯片 | Studio → Slide Deck |
| 生成信息图 | Studio → Infographic |
| 保存输出 | Notes |
| 复用笔记为新信源 | Notes → Convert to Source |
| 跨笔记本协作 | Bridge Summary + Gemini |

---

## 四、信源策略

NotebookLM 的输出质量高度依赖于信源质量。

**使用正确的信源类型做正确的工作。**

如果你的信源很弱……你猜输出怎么样？**对，也很弱！**

### 信源类型速查

| 信源类型 | 最佳用途 |
|---------|---------|
| PDF | 报告、论文、电子书 |
| Google Docs | 笔记、草稿、大纲 |
| 网页 URL | 文章、博客、文档 |
| YouTube 视频 | 演讲、教程、访谈 |
| 音频文件 | 播客、会议录音、语音笔记 |
| 电子表格 | 数据、CSV |
| 图片 | 信息图、截图、图表 |
| 粘贴文本 | 快速输入 |

### 信源原则

1. **精选而非堆积** — 10 个好的 PDF 胜过 50 个随机文档
2. **命名清晰** — 文件名为后续工作提供上下文
3. **分块处理** — 很长的文档按主题拆分
4. **创建术语表** — 专业主题先上传术语表作为信源 #1
5. **阶段性加载** — 分阶段处理信源，不要一次求全

---

## 五、使用场景库（19 个实战场景）

这是本文的实用引擎。每个场景都包含：

> 用途 → 最佳信源 → 设置 → 工作流 → 可粘贴的提示词 → 预期输出 → 质量检查 → 常见错误 → 进阶版 → 最终产出

准备好了吗？开始。

---

### 场景 1：从上传信源构建完整知识库

**用途：** 将多个信源转化为可复用的知识库，可进一步生成指南、课程、教程、操作手册、文章系列、幻灯片或 AI 助手文件

**最佳信源：** PDF、Google Docs、网页、YouTube 转录、音频转录、ePub、Markdown、Google Slides、Google Sheets、CSV、粘贴笔记

**设置：**
- 移除弱、过时或不相关的信源
- 清晰命名文件
- 按主题拆分超长文档
- 如涉及专业术语，创建术语表并作为信源 #1
- 配置角色为"Expert Knowledge Architect"

**工作流：**
1. 运行信源盘点
2. 逐个信源提取知识
3. 创建主题映射
4. 创建概念映射
5. 创建框架映射
6. 创建流程映射
7. 识别矛盾和缺失
8. 构建模块化知识库
9. 每个模块保存为笔记
10. 将优质笔记转为信源
11. 基于笔记信源构建最终指南/课程/剧本

**可粘贴提示词：**

```markdown
Act as an Expert Knowledge Architect.

Create a complete knowledge base from the selected sources.

Work in this order:

1. Create a source inventory.
2. Extract key ideas, definitions, frameworks, processes, examples, warnings, tools and gaps.
3. Create a master theme map.
4. Create a concept map.
5. Create a framework map.
6. Create a process map.
7. Identify contradictions and missing information.
8. Build a modular knowledge base.
9. Add checklists, templates, prompts and practical exercises.
10. Save each module as a Note.
```

**预期输出：** 结构化的知识库，包含模块、定义、框架、流程、示例、检查清单、模板、提示词和最终审计

**质量检查：**
- 每个信源是否都出现在盘点了？
- 输出是否过于依赖某一个信源？
- 完全重复的内容是否已合并？
- 非完全一致的关联想法是否被保留？
- 无信源支持的推断是否已标注？
- 缺口是否被明确说明？

**常见错误：**
- 直接要求"概括一切"
- 跳过盘点阶段
- 没有保存有用的输出作为笔记
- 让 NotebookLM 过度压缩
- 把第一个答案当作最终答案

**进阶版：** 使用分阶段笔记转信源工作流

**最终产出：** 可复用的知识库

---

### 场景 2：将信源转化为课程

**用途：** 将上传材料转化为结构化课程，包含模块、课程、练习、评估和结业项目

**提示词：**

```markdown
Act as an Expert Curriculum Designer.

Turn the selected sources into a complete course.

Include:

1. Course title
2. Course promise
3. Target learner
4. Beginner, intermediate and advanced tracks
5. Module structure
6. Lesson titles
7. Learning outcomes
8. Exercises
9. Assessments
10. Final project
11. Common mistakes
12. Required templates or worksheets
13. Suggested study schedule

Use only the selected sources.
Mark gaps where the sources do not provide enough material.
```

**最终产出：** 完整课程蓝图

---

### 场景 3：创建深度分析或长篇指南

**用途：** 将分散的研究转化为严肃的长篇指南、文章、电子书章节或技术解释

**提示词（第一阶段 — 架构）：**

```markdown
Act as a Senior Technical Writer.

Create a long-form guide from the selected sources.

First produce:

1. Working title
2. Thesis
3. Target reader
4. Section-by-section outline
5. Main argument of each section
6. Supporting sources for each section
7. Contradictions or tensions to address
8. Gaps that need a second pass

Do not write the full guide yet.
First create the architecture.
```

**提示词（第二阶段 — 逐节撰写）：**

```markdown
Write Section 1 only.

Use the agreed outline.
Use only the selected sources.

Include:
- clear explanation
- source-backed claims
- examples
- warnings
- practical steps
- gaps
- section summary
```

**最终产出：** 长篇指南或深度分析

---

### 场景 4：构建研究矩阵或数据表

**用途：** 将杂乱的信源转化为结构化的研究数据库

适用场景：声明/证据矩阵、文献综述矩阵、竞品比较表、术语表数据库、工具库、矛盾映射、信源质量审计、示例库、引用库、框架库、行动项目表

**提示词：**

```markdown
Create a Data Table from all selected sources.

Use these columns:

1. Item
2. Category
3. Definition or description
4. Source-backed evidence
5. Practical implication
6. Example
7. Limitation or warning
8. Related concept
9. Confidence level
10. Gap or missing information

Rules:
- Only include information supported by the selected sources.
- Merge exact duplicates.
- Preserve different framings where they add nuance.
- Mark inferred points clearly.
- Leave a cell blank if the source does not provide the information.
- Use Data Table or columnar format where possible.
```

**最终产出：** 研究矩阵或结构化知识数据库

---

### 场景 5：文献综述与学术研究工作流

**用途：** 处理学术论文，提取主题，比较方法论，识别研究空白，构建文献综述

**提示词：**

```markdown
Act as a post-doctoral researcher.

Conduct a literature review of the selected papers.

Include:

1. Major thematic clusters
2. Consensus view in each cluster
3. Dissenting papers or opposing findings
4. Methodologies used
5. Methodological weaknesses
6. Key evidence
7. Research gaps
8. Suggested research questions
9. Literature review outline

Use source-backed claims only.
Mark inferred synthesis clearly.
```

**最终产出：** 文献综述大纲和研究矩阵

---

### 场景 6：考试复习与主动学习系统

**用途：** 将被动学习材料转化为主动回忆、测验、闪卡、苏格拉底式辅导和复习计划

**提示词（苏格拉底式辅导）：**

```markdown
Act as a strict Socratic tutor.

Test me on the selected sources one question at a time.

Rules:
- Ask one question.
- Wait for my answer.
- Grade my answer against the sources.
- Explain what I got right.
- Explain what I missed.
- Give a hint before giving the full answer.
- Track my weak areas.
- At the end, create a revision plan based on my mistakes.
```

**提示词（生成测验）：**

```markdown
Create three levels of questions from the selected sources:

1. Beginner recall questions
2. Intermediate application questions
3. Expert-level exam questions that expose shallow understanding

Include answers, explanation and source support.
```

**最终产出：** 主动学习系统

---

### 场景 7：YouTube、播客和转录内容再利用

**用途：** 将长视频、播客和转录文本转化为结构化内容资产

**提示词：**

```markdown
Analyse this transcript.

Extract:

1. Core thesis
2. Key ideas
3. Frameworks
4. Examples
5. Stories
6. Warnings
7. Strong quotes
8. Content hooks
9. Contrarian angles
10. Practical takeaways

Then turn the strongest ideas into:
- one newsletter outline
- one X thread
- one LinkedIn post
- one short-form video script
- one infographic prompt
```

**最终产出：** 内容再利用包

---

### 场景 8：商业 SOP 与运营手册创建

**用途：** 将杂乱的运营知识转化为 SOP、操作手册、检查清单和培训材料

**提示词：**

```markdown
Turn the selected source material into a formal Standard Operating Procedure.

Use this structure:

1. SOP title
2. Purpose
3. When to use this SOP
4. Owner
5. Required tools
6. Required inputs
7. Step-by-step process
8. Quality standard
9. Common failure points
10. Troubleshooting
11. Escalation rules
12. Final checklist

Do not invent missing steps.
If a step is unclear, mark it as a gap.
```

**最终产出：** SOP 或操作手册

---

### 场景 9：会议记录、通话和语音笔记工作流

**用途：** 从对话中提取决策、行动项、项目简报、风险和跟进事项

**提示词：**

```markdown
Analyse this meeting transcript.

Provide:

1. 3-sentence executive summary
2. Key decisions made
3. Action item table with owner and deadline
4. Risks raised
5. Open questions
6. Dependencies
7. Follow-up email draft
8. Project brief update

If the transcript does not clearly assign an owner or deadline, mark it as unclear.
```

**最终产出：** 会议简报和项目行动日志

---

### 场景 10：客户交付物与咨询工作流

**用途：** 将客户材料转化为审计报告、战略备忘录、提案、演示文稿和实施计划

**提示词：**

```markdown
Act as a Strategy Consultant.

Review the selected client materials.

Create an audit report with:

1. Client context
2. Stated goals
3. Current strategy
4. Main problems
5. Blind spots
6. Contradictions in the client's own material
7. Opportunities
8. Recommended implementation roadmap
9. Risks
10. Next steps

Use specific source-backed evidence.
Do not invent client facts.
```

**最终产出：** 客户审计报告或提案演示文稿

---

### 场景 11：内容创作者研究引擎

**用途：** 构建研究库，将信源材料转化为文章、新闻简报、脚本、帖子、钩子和视觉创意

**提示词：**

```markdown
Act as a Content Strategist.

Review the selected sources and create a content engine.

Extract:

1. Strongest ideas
2. Best hooks
3. Contrarian angles
4. Examples and stories
5. Useful frameworks
6. Common mistakes
7. Audience pain points
8. Content angles
9. Newsletter ideas
10. X/Twitter thread ideas
11. LinkedIn post ideas
12. Visual infographic concepts

Preserve source accuracy.
Avoid generic content.
```

**最终产出：** 内容引擎

---

### 场景 12：幻灯片和演示文稿工作流

**用途：** 将信源转化为演示大纲、故事板和幻灯片

> ⚠️ **关键规则：** 不要假设幻灯片的修订版还能引用信源。先用 Chat 构建和验证信源锚定的大纲，再生成幻灯片。修订后要手动再次验证事实。

**提示词（先在 Chat 中构建大纲）：**

```markdown
Create a source-backed slide deck outline.

For each slide include:

1. Slide title
2. Core message
3. Source-backed bullet points
4. Supporting source name
5. Any numbers or claims requiring manual verification
6. Suggested visual
7. Speaker note

Do not create the slide deck yet.
First produce the verified outline.
```

**修订提示词：**

```markdown
Revise the slide deck for clarity and presentation quality.

Only revise:
- wording
- layout
- visual hierarchy
- slide flow
- audience clarity

Do not introduce new factual claims.
Do not add new statistics.
Do not change numerical claims unless I provide the corrected numbers manually.
```

**最终产出：** 演示文稿

---

### 场景 13：音频概览和播客工作流

**用途：** 将信源材料转化为定制化的音频简报、辩论、讲解或学习会话

**提示词（自定义音频概览为辩论形式）：**

```markdown
Format this Audio Overview as a Debate.

Focus only on the failure modes of the methodology in the selected sources.

Host A should defend the methodology.
Host B should act as a sceptic and ask practical questions.

Do not summarise the whole notebook.
Focus on:
- risks
- limitations
- trade-offs
- implementation mistakes
- how to avoid failure
```

**最终产出：** 音频简报或播客

---

### 场景 14：可视化思维工作流

**用途：** 将密集材料转化为可视化结构（思维导图、信息图、流程图表）

**提示词：**

```markdown
Review the selected sources.

Create a visual thinking map with:

1. Central concept
2. Main branches
3. Sub-branches
4. Dependencies
5. Sequence of ideas
6. Contradictions or tensions
7. Suggested diagram formats
8. Suggested infographic structure

Output as Markdown.
```

**最终产出：** 可视化地图或信息图方案

---

### 场景 15：信源审计与验证工作流

**用途：** 检查信源是否可信、最新、有用、矛盾或薄弱

**提示词：**

```markdown
Conduct a rigorous Source Audit.

Create a table with:

1. Source name
2. Source type
3. Publication date if available
4. Author or organisation if available
5. Core thesis
6. Usefulness rating
7. Potential bias or weakness
8. What this source is best used for
9. Whether it should be kept, removed or used cautiously

Then identify any contradictions between sources.
```

**最终产出：** 信源质量报告

---

### 场景 16：大型项目与多笔记本工作流

**用途：** 管理超出单个笔记本承载范围的项目

> **核心理念：** 一个笔记本不应该容纳一切。按主题、项目、受众或输出拆分信源。使用外部存储作为永久记忆。

**提示词（生成桥梁摘要）：**

```markdown
Create a Bridge Summary for this notebook.

The summary must represent the most important knowledge from all selected sources.

Include:

1. Core topic
2. Main themes
3. Key frameworks
4. Important evidence
5. Contradictions
6. Gaps
7. Useful examples
8. Recommended next-step questions
9. Source list

This Bridge Summary will be exported into an external knowledge base.
Make it dense and portable.
```

**最终产出：** 跨笔记本知识系统

架构建议：
- NotebookLM → 信源锚定的综合
- Zotero → 论文管理
- Obsidian/Notion → 永久知识库
- Gemini → 跨笔记本编排

---

### 场景 17：NotebookLM 与 Gemini 协作工作流

**用途：** 结合 NotebookLM 的信源锚定能力和 Gemini 的长上下文推理与执行能力

**提示词（Gemini 端）：**

```markdown
You are working from a NotebookLM extraction.

Your job is to turn the extracted source-grounded material into a final knowledge asset.

Rules:
- Do not restart extraction.
- Do not invent unsupported claims.
- Separate source-backed material, synthesis and inference.
- Preserve all high-signal frameworks, examples, tactics and warnings.
- Write in British English.
- Structure the output as a practical playbook.

Build:
1. Executive overview
2. Core mental model
3. Feature-to-outcome map
4. Workflow step-by-step
5. Prompt library
6. Recommended tools and integrations
7. Common breakdowns and recoveries
8. Metrics and evaluation
```

**最佳分工：**

| NotebookLM | Gemini |
|-----------|--------|
| 信源提取 | 编程 |
| 验证 | 长提示编辑 |
| Studio 输出 | 电子书重组 |
| 引用核查 | 文章生成 |
| | 模式/网站创建 |
| | 宽泛的创意扩展 |

**最终产出：** Gemini 扩展的知识资产

---

### 场景 18：创建自定义 AI 助手 / GPT 知识文件

**用途：** 将 NotebookLM 输出转化为结构化知识文件，供 Custom GPTs、Claude Projects 或其他 AI 助手使用

**提示词：**

```markdown
Create an AI Assistant Knowledge File from the selected sources.

Include:

1. Assistant role
2. Domain overview
3. Target user
4. Key terminology
5. Core principles
6. Frameworks
7. Workflows
8. Decision rules
9. Examples
10. Mistakes to avoid
11. Answer style guidance
12. Boundaries
13. Uncertainty rules
14. Required output formats

Write in clean Markdown.
Make it suitable for uploading into a Custom GPT or Claude Project.
```

**最终产出：** AI 助手知识文件

---

### 场景 19：书籍、电子书或长文内容工作流

**用途：** 将 NotebookLM 作为研究和结构引擎，用于书籍和长文写作

**提示词：**

```markdown
Act as a Senior Editor.

Use the selected sources to create a book architecture.

Include:

1. Book title options
2. Core thesis
3. Target reader
4. Chapter-by-chapter outline
5. Main argument of each chapter
6. Supporting source material
7. Examples to include
8. Gaps in the source material
9. Exercises or workbook ideas
10. Promotional content angles
```

**最终产出：** 书籍大纲和研究库

---

> ⚠️ **X 平台限制了文章长度，无法继续保存。还有更多使用场景待续……**
>
> **第二部分已发布，请在作者主页查看。**

---

## 六、掌握工作流（主流程速查）

无论你用哪个场景，核心流程是：

```
信源 → 盘点 → 提取 → 综合 → 保存(笔记) 
      → 笔记转信源(可选) → 生成资产 → 导出/部署
```

### 关键原则

1. **先盘点，后提问** — 永远先了解你有什么信源
2. **提取优于概括** — 不要要求"总结"，而是要求"提取 X"
3. **保存一切有价值的内容** — 好的输出不保存就等于没做过
4. **笔记→信源循环** — 这是威力放大的核心机制
5. **工作室是终点，不是起点** — 先做提取和综合
6. **验证再验证** — 始终手动核查数字和声明
7. **外部存储最终态** — NotebookLM 擅长综合，但不是终极存储

---

## 七、嵌入的提示词库速查

本文完整包含了以下可直接使用的提示词（均在对应场景中有完整展示）：

| # | 提示词用途 | 使用场景 |
|---|-----------|---------|
| 1 | Expert Knowledge Architect | 场景 1：构建知识库 |
| 2 | Expert Curriculum Designer | 场景 2：构建课程 |
| 3 | Senior Technical Writer（架构） | 场景 3：指南架构 |
| 4 | Senior Technical Writer（写作） | 场景 3：逐节撰写 |
| 5 | 数据表生成 | 场景 4：研究矩阵 |
| 6 | Post-Doctoral Researcher | 场景 5：文献综述 |
| 7 | Socratic Tutor | 场景 6：学习辅导 |
| 8 | 三级测验生成 | 场景 6：测验 |
| 9 | 转录分析+内容再利用 | 场景 7：内容复用 |
| 10 | SOP 生成 | 场景 8：SOP |
| 11 | 会议转录分析 | 场景 9：会议记录 |
| 12 | Strategy Consultant | 场景 10：客户审计 |
| 13 | Content Strategist | 场景 11：内容引擎 |
| 14 | 幻灯片大纲生成 | 场景 12：演示文稿 |
| 15 | 幻灯片修订 | 场景 12：修订 |
| 16 | 辩论格式音频概览 | 场景 13：音频 |
| 17 | 可视化思维地图 | 场景 14：思维导图 |
| 18 | 信源审计 | 场景 15：审计 |
| 19 | Bridge Summary | 场景 16：跨笔记本 |
| 20 | Gemini 知识资产扩展 | 场景 17：Gemini 协作 |
| 21 | AI 助手知识文件 | 场景 18：GPT 文件 |
| 22 | Senior Editor 书籍架构 | 场景 19：书籍 |

---

*整理于 2026-05-14，来自 [@hooeem 的 X 文章](https://x.com/hooeem/status/2054652562867896520)*

*本文是系列的第一部分（覆盖 19/27 个使用场景），第二部分已由作者发布。*
