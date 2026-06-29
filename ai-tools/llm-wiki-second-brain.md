---
title: "如何构建一个自动维护的「第二大脑」—— Karpathy 的 LLM Wiki 模式"
tags:
  - AI-Tools
  - 知识管理
  - 第二大脑
  - Karpathy
  - Obsidian
  - Claude
  - RAG
date: 2026-06-29
source: "https://x.com/wandermist/status/2070454234189893747"
authors: "wandermist (@wandermist)"
---

# 如何构建一个自动维护的「第二大脑」—— Karpathy 的 LLM Wiki 模式

> **来源：** [wandermist 的 X 长文](https://x.com/wandermist/status/2070454234189893747)
> **数据：** 95 万阅读 · 529 赞 · 1870 收藏 · 93 次转发
> **作者：** wandermist（894 粉丝，瑞士内容创作者）

---

## 一句话梗概

Andrej Karpathy 提出了一种叫 **LLM Wiki** 的知识管理范式：**让 AI 帮你维护一个持续累积、自我更新的 Markdown Wiki**，而不是每次从零开始搜索碎片化文档。AI 负责"苦力活"（更新页面、维护交叉引用、标记矛盾），你负责"脑力活"（筛选来源、提好问题、深度思考）。配合 Obsidian + Claude Code，15 分钟就能搭起来。

![LLM Wiki 封面](../image/llm-wiki-second-brain-1.jpg)

---

## 你现在的使用方式是"一次性的"

大多数人用 AI 的模式：

> 上传文档 → 提问 → 拿到答案 → 关掉标签页

第二天，你又上传同一份文档，问了稍微不同的问题。AI **从零开始**。没有昨天的记忆，没有积累，没有跨所有问题的综合分析。

- NotebookLM 是这样
- ChatGPT 文件上传是这样
- 大多数 RAG 系统是这样

**对于需要随时间积累知识的人，这种模式从根本上就是错的。**

---

## Karpathy 提出的方案

Karpathy 上周在 X 上发了两条爆火帖子，提出了一个叫 **LLM Wiki** 的模式。想法简单但强大：

> **与其每次都让 AI 重读原始文档，不如让 AI 增量式地构建和维护一个持久的 Wiki**——一个结构化的、相互链接的 Markdown 文件集合，随时间不断累积。

当你添加一个新来源时，AI **不只是在索引以备后用**。它阅读内容、提取关键信息，然后**整合到现有的 Wiki 中**：
- 更新实体页面
- 修订主题摘要
- 标记新旧信息的矛盾
- 加强整体综合

### RAG vs LLM Wiki

| 对比维度 | 现在的 RAG | Karpathy 的 LLM Wiki |
|---------|-----------|-------------------|
| **添加来源时** | 被切块 + 向量化，等待检索 | AI 阅读、总结、更新 Wiki 中所有相关页面 |
| **提问时** | AI 搜索相关碎片，**从零拼凑答案** | AI **直接读取已有的 Wiki 页面**，答案附带引用 |
| **随时间推移** | 什么也不积累，每次查询从零开始 | Wiki 越来越丰富，交叉引用累积，矛盾被标记 |
| **维护** | 不需要（但质量也不提升） | **AI 全程维护**，这就是核心亮点 |

Karpathy 的原文一针见血：

> "人类放弃 Wiki 是因为维护成本增长快于价值。LLM 不会无聊、不会忘记更新交叉引用、一次能处理 15 个文件。"

---

## 三层架构

要让这个模式工作，需要理解三个层次：

### 1️⃣ Raw Sources（原始来源）
你精心收集的源文档集合：文章、PDF、笔记、剪切的网页。这些是**不可变的**——AI 从中读取但**绝不修改**。这是你的"真相源"。

### 2️⃣ The Wiki（Wiki 层）
AI 生成的 Markdown 文件目录。包含总结、实体页面、概念页面、比较页面、索引等。**AI 完全拥有这一层**：创建页面、新来源到达时更新、维护交叉引用、保持一致性。
> 你读它；AI 写它。

### 3️⃣ The Schema（配置文件）
一个配置文件（在 Claude Code 中是 `CLAUDE.md`），告诉 AI Wiki 的结构是什么、遵循什么约定、在摄入来源/回答问题/维护 Wiki 时执行什么工作流。

**这就是让 AI 成为一个有纪律的 Wiki 维护者（而不是通用聊天机器人）的关键。**

Karpathy 的比喻太妙了：

> Obsidian 是 IDE，LLM 是程序员，Wiki 是代码库。

---

## 实操：15 分钟搭建教程

### 你需要什么

- **Claude Code** —— 已安装并配置好
- **Obsidian** —— 从 [obsidian.md](https://obsidian.md) 免费下载
- **Obsidian Web Clipper** —— Chrome 扩展商店安装

### 第 1 步：创建 Obsidian Vault

打开 Obsidian → 点击 `Create new vault` → 取个名字。本质上就是在电脑上创建一个文件夹，存放所有 Markdown 文件。

### 第 2 步：喂给 Claude Code Karpathy 的 Gist

在终端里，将 Claude Code 指向你的 Vault 文件夹，然后粘贴 Karpathy 的 gist 内容：

```
Here is Andrej Karpathy's LLM Wiki pattern. Please implement this as my personal knowledge base in this Obsidian vault. Create the full directory structure, the CLAUDE.md schema file, the index, the log, and all templates. Use his gist as the first source to ingest.
```

然后把 Karpathy gist 的全文粘贴进去。

**就这么简单。Claude Code 会自动：**
1. 创建文件夹结构（`raw/`、`wiki/sources/`、`wiki/entities/`、`wiki/concepts/` 等）
2. 编写完整的 `CLAUDE.md` schema 文件（包含规则、页面类型、工作流）
3. 创建索引和活动日志
4. 把 gist 本身作为第一个来源摄入
5. 从 gist 内容构建实体页和概念页

完成后切到 Obsidian → 文件浏览器中可以看到完整的 Wiki 结构，图谱视图中能看到第一组互链页面。

### 第 3 步：配置 Obsidian Web Clipper

这是你快速把来源灌入 Wiki 的方式：
- 打开 Obsidian Web Clipper 扩展设置
- 默认 vault 设为刚创建的那个
- 默认文件夹设为 `raw/`——剪切的文章会落在这里

以后读到想保存的文章 → 点击 Clipper 图标 → 干净 Markdown 版自动存入 `raw/`。

### 第 4 步：摄入第一个真实来源

找一篇文章剪贴（或用 Web Clipper，或把 URL 贴给 Claude Code），然后告诉 Claude Code：

```
Ingest the new file in raw/
```

Claude Code 会：
1. 读取源文件
2. 展示摘要和关键主张供你审阅
3. 写入所有内容：
   - 来源摘要页
   - 提及的人物/产品实体页
   - 概念页
   - 全部交叉引用 + 更新索引

**一个来源 = 5~15 个 Wiki 页面被更新。这就是 Karpathy 说的复利效应。**

### 第 5 步：查询你的 Wiki

现在你可以提问了：

```
What do we know about [topic] across all sources?
```

Claude Code 会读取索引、拉取相关页面、用 `[[wikilink]]` 引用回具体来源来综合答案。如果答案很有价值，还可以把它存为一个新的 Wiki 页面——**你的探索也在复利积累**。

### 第 6 步：定期健康检查

偶尔让 Claude Code 跑一次：

```
Lint the wiki
```

它会扫描并报告：
- 页面间的矛盾
- 孤儿页面（没有链接）
- 已被新来源覆盖的陈旧主张
- 缺失的交叉引用

按严重程度分类报告，并提供修复选项。

---

## 为什么这比你现在的做法好

核心洞察属于那种"一说就懂"级别的：

> **维护有用知识库的瓶颈从来不是阅读或思考，而是"记账"。**

更新交叉引用、保持总结时效、标记新数据与旧数据的矛盾、保持数十个页面的一致性——这些是人类会放弃的工作。而**这恰恰是 LLM 最擅长的**。

Wiki 之所以能保持维护，是因为维护成本几乎为零。

而且因为**它只是一堆 Markdown 文件**，你享有：
- **Git 版本历史**
- **Obsidian 图谱可视化**
- **完全的便携性** —— 没有厂商锁定，没有专有数据库，没有订阅需求（除了 Claude）

---

## 5 个让你觉得值得一做的用例

### 1️⃣ X/Newsletter 写作大脑 ← 作者的亲身实践

每篇文章都被摄入，不只是存储——而是分解为结构化页面：论文、关键主张、引用数据、覆盖的产品、反复出现的主题。

开始写新文章时，不再从零想：
> "关于这个话题我写过什么？有什么数据？有什么新角度？根据我之前的写作，怎么组织？"

Wiki 会给你一份上下文的简报，附带引用。它防止你重复自己，给你找出你已忘记的关联，追踪你论证的演变。

> 摄入 20+ 篇文章后，Wiki 比我自己的记忆更了解我的写作领域。

### 2️⃣ 持续数周/月的深度研究

研究 AI 安全、气候科技、行业竞争分析？每找到一篇论文/文章/报告就摄入一篇。

15 个来源后，Wiki 中就会有：
- 每个研究者/公司的实体页
- 追踪思想连接和来源分歧的概念页
- 一个反映你读过的一切的活概况

问一个需要综合五份文档的问题——Wiki 已经准备好了，因为综合是增量完成的，不是临时的。

### 3️⃣ 团队知识库（Slack + 通话 + 文档）

这才是真正强大的企业用例：
- 喂入 Slack 产品频道线程
- 喂入 Granola/Fireflies 会议转录
- 喂入客户通话录音
- 喂入项目文档和内部策略文档

Wiki 会自动构建每个客户、每个项目、每个竞争对手的实体页。

> **销售团队**：摄入所有发现通话转录。一个季度后，Wiki 揭示："本季度客户提出的 TOP 3 异议是 X, Y, Z"，附带具体通话引用。
> **产品团队**：喂入用户研究访谈 → Wiki 追踪功能请求、痛点、情感变化趋势。

团队中**没有一个人需要做维护工作**。AI 做了没人想做的事。

### 4️⃣ 商业与竞争情报

喂入客户通话转录、竞争对手博客、行业报告、内部策略文档。Wiki 构建每个竞争对手的实体页，追踪他们的公告，跨数十个来源发现模式。

> "本季度客户提出的 TOP 3 异议是什么？" 变成一个可查询的问题——有引用答案——而不是你上次团队会议的模糊记忆。

### 5️⃣ 课程笔记与自我教育

在上在线课程、考证、或深入钻研某项技能？摄入每堂讲座、每次阅读、每个练习。Wiki 追踪概念如何相互构建，标记后期材料何时与早期材料矛盾或更新，给你一个**按你学习方式组织的**个人参考——而不是按老师组织的方式。

---

## 更大的图景

如果你在关注 AI 领域，主流的文档处理方式是 RAG：全部上传，查询时让 AI 搜索、生成答案。它能工作。

但 Karpathy 在指向**不同的东西**——一种把知识当作**复利资产**、而不是检索问题的方法。

这个想法可以追溯到 **1945 年 Vannevar Bush 的 Memex**……一个个人、精心策划的知识存储，其中**文档之间的连接和文档本身一样有价值**。Bush 的愿景比后来的网络更接近这个模式。他无法解决的是"谁来做维护"的问题。

**现在我们有了答案。**

> **人的工作**：筛选来源、引导分析、问好问题、思考所有这一切的意义。
> **LLM 的工作**：**其他所有事**。

---

## 参考资料

- [Karpathy 的原始推文](https://x.com/karpathy/status/2051526429178511772)
- [Karpathy 的 follow-up + gist 链接](https://x.com/karpathy/status/2051645530743939277)
- [LLM Wiki 完整 Gist](https://gist.github.com/karpathy/56a44bcd3a8a24b4fc4582916bb71e77)
- [Obsidian](https://obsidian.md)（免费）
- [Obsidian Web Clipper](https://chromewebstore.google.com/detail/obsidian-web-clipper)

---

*整理于 2026-06-29，原文来自 [wandermist 的 X 长文](https://x.com/wandermist/status/2070454234189893747)*
