# Claude Code + NotebookLM + Obsidian：越用越聪明的研究系统

> **来源**: @monokern 于 X/Twitter  
> **原文链接**: https://x.com/monokern/status/2061044198418031017  
> **设置时间**: 约 30 分钟  
> **标签**: #ClaudeCode #NotebookLM #Obsidian #Research #Workflow #SkillCreator

---

## 核心论点

大多数人做研究的方式仍然是手动的——开十个标签页、看视频、读文章、记笔记、一小时后得到一堆不知道该怎么办的信息。

**有更好的方法。**

核心三件套：**Claude Code（执行引擎）→ NotebookLM（分析引擎）→ Obsidian（记忆层）**，加上 Skill Creator 让整个过程可重用、可演化。

---

## 架构分层

| 层 | 工具 | 职责 |
|----|------|------|
| **执行引擎** | Claude Code | 跑命令、调技能、管理文件、编排整条 pipeline |
| **定制层** | Skill Creator | 用自然语言创建可复用技能，无需编程 |
| **分析引擎** | NotebookLM | Google 的 AI 研究工具，读取来源生成深度分析、信息图、播客脚本等 |
| **记忆层** | Obsidian | 本地 Markdown 知识库，存储所有产出，随时间积累 |

关键优势：当 Claude Code 把分析工作卸载到 NotebookLM 时，用的是 **Google 的基础设施**，不消耗你的 **Claude tokens**。

---

## 四步搭建

### 第 1 步：安装 Skill Creator

打开 Claude Code，**确保你在 Obsidian vault 目录内**：

```
/search skill-creator
```

安装后重启 Claude Code。你就能用自然语言创建任何技能了。

### 第 2 步：创建 YouTube 搜索技能

用自然语言让 Claude Code 创建一个 `/yt-search` 技能，能搜索 YouTube 并提取结构化数据（标题、频道、订阅数、播放量、上传日期、URL、互动率）。

> 前提: 本地需要安装 `yt-dlp`

### 第 3 步：安装 NotebookLM-py

NotebookLM **没有公开 API**，通过开源项目 [notebooklm-py](https://github.com/teng-lin/notebooklm-py) 桥接。

```
pip install notebooklm-py
notebooklm auth
```

会打开浏览器让你登录 Google 账号，建立连接。

### 第 4 步：创建 NotebookLM 技能

用 Skill Creator 创建一个完整的 NotebookLM 技能——覆盖 NotebookLM 的所有操作：最多 50 个来源/笔记本，所有交付类型。

### 第 5 步：组合为一条 Pipeline 技能

**这是精髓——把上面三个技能串成一条 pipeline**：

`/yt-search` → 找到视频 → 传给 NotebookLM → 创建笔记本 → 运行分析 → 生成信息图 → 保存到 Obsidian

一次 `pipeline "研究主题"` 命令搞定全部。

---

## 一个真实例子：AI 智能体框架

主题：2026 年 AI 智能体框架——哪些真正火了、哪些过誉了、有哪些空白。

Claude Code 启动 pipeline → 调用 yt-search 找到 10 个视频 → 把 URL 传给 NotebookLM → 创建笔记本并运行分析 → 请求信息图

**总处理时间：约 6 分钟**（大部分花在 NotebookLM 的 Google 服务器上，不是你的 token）。

产出：
- 完整分析报告（哪些框架在上升 vs 停滞、开发者真正在抱怨什么、内容空白）
- AI 智能体框架全景信息图
- 一个结构化的 Markdown 文件，直接保存在 Obsidian vault 中

---

## Obsidian 的复利效应

单次使用已经很强大，但 Obsidian 让它真正进化：

**每次研究产生的文件都进入你的 vault。** 随着时间的推移，vault 变成你所有研究的结构化语料库——主题、来源、分析、模式、结论。

Claude Code 可以读取所有文件。它看到你的链接结构，理解哪些主题你反复研究、哪些分析你最有共鸣、你偏好什么格式。

**`claude.md`** 文件是关键的显式配置——告诉 Claude Code 你的习惯、输出偏好、结构偏好。每周让它自动分析近期 session 并更新：

> "根据我最近的研究更新 claude.md，反映我的模式和偏好"

**一个月后**，工作流已经足够了解你，输出开始符合你的真实需求。**一年后**，你拥有一个吸收了数百次 session、理解你的思维方式、训练有素的私人研究助手。

---

## 模块化：YouTube 不是重点

pipeline 结构才是核心。**可以替换任何数据源：**

- **PDF** — 学术论文、行业报告、白皮书
- **网页** — 新闻、文档、博客
- **本地文件** — 你的笔记、导出数据、转录稿
- **Google Drive** — 已有的文档和表格

工作流模板不变。换数据源，保留结构。

---

## 你最终得到什么

- ✅ 一条命令执行完整研究 pipeline
- ✅ 将重分析卸载到 Google 基础设施（省 token）
- ✅ 自动生成结构化交付物（信息图、思维导图、音频、卡片）
- ✅ 每份结果存入本地知识库
- ✅ 随时间学习你的偏好，输出越来越好

> **30 分钟搭建，第一次使用就值回票价。**
