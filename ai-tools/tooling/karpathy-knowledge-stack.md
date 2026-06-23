---
title: "Karpathy 式知识栈：为什么我把 Hermes、MiniMax M3 和 Obsidian 放在核心"
tags:
  - ai-tools
  - knowledge-management
  - obsidian
  - hermes-agent
  - minimax
date: 2026-06-16
source: "https://x.com/polydao/status/2066904909849440434"
authors: "Mr. Buzzoni (@polydao)"
---

# Karpathy 式知识栈：Hermes + MiniMax M3 + Obsidian 三合一

> **来源：** [Karpathy-Style Knowledge Stack: Why I Put Hermes, MiniMax M3 and Obsidian at the Core](https://x.com/polydao/status/2066904909849440434)

> *大多数人把笔记、模型和 agent 看作三个独立的世界。*
> *这个栈把它们合并成一个反馈循环：*
> **Obsidian 作为记忆，Hermes 作为 agent，MiniMax M3 作为推理核心。**

![cover](../image/karpathy-knowledge-stack-1.jpg)

---

## 为什么"知识栈"胜过"笔记应用"

传统个人知识管理（PKM）在三个方面必然崩坏：

- 笔记写一次就再也没人更新
- AI 对话很聪明但健忘——每次会话从零开始
- 重要工作的上下文不断掉出"内存"——无论是你的还是模型的

**我们真正想要的是：**

- 一个本地的、可链接的知识图谱
- 一个活在这个图谱**里面**（而非上面）的 agent
- 一个能在大规模真实上下文中推理的前沿模型，不只是 2-3 段话

**Hermes + MiniMax M3 + Obsidian 正好给你这个：**

- **Obsidian** — 本地 markdown 图谱，带反向链接、图谱视图，以及为个人知识库设计的插件生态
- **Hermes Agent** — 自我进化的开源 agent，内置学习循环、工具和长期任务运行能力，跑在你自己的基础设施上
- **MiniMax M3** — 我每天在 Hermes 里实际运行的模型。长上下文、多模态、agentic。我选它是因为我需要一个模型能一次性读我的整个 vault、所有日志和一堆新的原始文章——不需要拼凑 RAG 管道就能用一个上下文窗口搞定

> 结果感觉不像是"在用 LLM"，更像是慢慢训练一个第二大脑。

---

## 为什么我选 M3（以及实际使用观察）

> *我不是因为 benchmark 选的 M3。*

**我在 2025 年试过的每个模型都有同一个失败模式：**

> 它单独总结一篇笔记没问题，但一旦我让它读十篇笔记、和我的 MOC（内容地图）交叉引用、再写一篇新的回来，它就开始丢线索。

**症状总是相似的：**

- 总结局部正确，全局错误
- 引用了文件里根本不存在的项目
- 用了不同分类体系里的标签
- 发明了一个不存在的 wikilink

模型很聪明。但工作流比模型大。

**M3 是我试过的第一个让整个图谱能放进上下文、并在整个任务过程中保持在那里的模型。**

### 实际使用中三个突出感受

1. **它真的会用我的分类体系**
   我有一套 ~41 个固定标签（#coin/*、#project/*、#concept/* 等）。让 M3 编译一篇新笔记，它第一次就选对主标签的概率约 90%。
   用 200K 上下文模型时大概只有 60%。区别在于 M3 能看到完整的标签全景图，然后在这个全景上推理，而不是只靠几个例子去猜。

2. **它在长 agentic 循环中不会丢线索**
   完整的 vault 检查是 30+ 次工具调用：读 MOC、跟 wikilink、数标签、查重、写报告。
   大多数模型到第 8-9 次调用就开始漂移了。M3 能一直保持连贯到最后。这是我停止每 20 分钟换一次会话的根本原因。

3. **它把前向引用当作特性**
   当我要它编译一篇笔记、但某个概念还不存在时，M3 会写一个 "Forward Reference"。Obsidian 将其渲染为灰色链接。我每周在 lint 时整理一次。
   这比模型要么编造一篇不存在的笔记、要么直接跳过链接好太多了。

### 几个月使用后的三个实在约束

- **首次调用延迟高。** Hermes 预加载上下文。别用前 3 秒评价 M3——给它 10 秒。
- **它会自信地写一个不存在的 [[wikilink]]。** 这就是上面的"前向引用"行为。只有在你不做每周 lint 时才会变成问题。
- **多模态确实存在，但图表密集的 PDF 我还是会用专门的视觉工具。** M3 读取图片中的文字和短截图很好，但整页带图的内容不是它的强项。

> **这就是整个卖点。这个模型正好擅长 vault 工作流需要的事：一次性读完整图谱，然后写回去，不丢结构。**

---

## 第一层：Obsidian 作为真相源

Obsidian 是这个堆栈里无聊但关键的基础层。

- 你的知识以纯 markdown 文件存在磁盘上，不锁在任何人的云端
- 反向链接、图谱视图和日记帮你把想法聚集成集群，而不是消失在聊天记录里
- 插件把 Obsidian 变成一个可编程的文档、任务和数据集图谱，agent 可以系统性地遍历它

**原则很简单：**

> 值得保留的东西，先放进 Obsidian。
> Agent 做了有用的事，结果应该变成一篇笔记。

**实用的 vault 结构：**

```
/obsidian-vault
  /inbox
  /people
  /projects
  /research
    ai-agents.md
    minimax-m3-benchmarks.md
  /ai
    hermes-playbook.md
    agents-ideas.md
```

![vault structure](../image/karpathy-knowledge-stack-4.jpg)

Hermes 会读、重构、创建这些笔记——但 vault 永远是真相源。

---

## 第二层：Hermes 作为自我进化的操作者

这是让这个栈从"一个带 LLM 的笔记系统"变成基础设施的关键。

Hermes Agent 是 NousResearch 构建的自我进化 AI agent。

- 它持续维护你和你的工作模型
- 从经验中创建技能
- 在使用中改进这些技能
- 搜索自己的历史对话来找回相关上下文——而不是每次重置会话

**运行 Hermes 有两种主要方式：**

- CLI 工具（Linux、macOS、WSL2）
- **Hermes Desktop** — macOS、Windows、Linux 的原生应用

### 安装方式

**macOS / Linux / WSL2 (CLI)：**

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

安装后：
```bash
source ~/.bashrc 2>/dev/null || true
source ~/.zshrc 2>/dev/null || true
hermes
```

**Windows PowerShell (CLI)：**
```powershell
irm https://hermes-agent.nousresearch.com/install.ps1 | iex
```

Windows 安装器会处理 Python 3.11、Node.js 22、ripgrep、ffmpeg 和便携版 Git Bash，然后把 hermes 加入 PATH。

**Hermes Desktop (GUI)：**
从[官方桌面页](https://hermes-agent.nousresearch.com/)下载原生安装器。

- **Desktop**：想要原生 GUI、更简单的入门体验
- **CLI**：需要可复现性、脚本化、远程服务器/VPS 部署、精细控制
- **大多数人两者都用**：Desktop 日常交互，CLI 用于设置、自动化和远程工作

![hermes desktop](../image/karpathy-knowledge-stack-3.jpg)

---

## 架构：这个栈如何实际组合在一起

清晰的思维模型：

```
Obsidian Vault
   ↓
Hermes Agent
   ↓
MiniMax M3
   ↓
Updated notes, summaries, skills, scheduled jobs
```

每一层有明确分工：

- **Obsidian** 以 markdown 文件存储笔记——易于索引、搜索、差异对比和版本管理
- **Hermes** 是编排层——读文件、运行工具、记住之前的工作、调度任务、决定何时持久化有用内容。它还能连接到消息平台和网关
- **MiniMax M3** 是推理引擎——读大量笔记集合、重写凌乱的笔记、跨 vault 比较文档、处理长期 agentic 任务而不会忘记 20 次工具调用前在做什么

> Hermes 不是在取代 Obsidian。它坐在你的 vault 和模型之间，把 vault 变成可行动的东西。

**一个真实的循环：**
1. 你在 Obsidian 里捕捉原始想法
2. Hermes 读 vault 或特定文件夹
3. Hermes 把相关笔记集发送给 MiniMax M3
4. M3 重构、打标签、建立链接、总结或扩展材料
5. Hermes 把结果作为干净的 markdown 写回 vault

> 这个循环——不是一次性的聊天——才是真正的产品。

---

## 实际操作：连接 Hermes 到你的 Vault

把 Obsidian vault 放在正常文件系统路径，暴露给 Hermes：

**macOS / Linux：**
```bash
export OBSIDIAN_VAULT="$HOME/Documents/Obsidian/MainVault"
ls "$OBSIDIAN_VAULT"
```

**Windows PowerShell：**
```powershell
$env:OBSIDIAN_VAULT="$HOME\Documents\Obsidian\MainVault"
Get-ChildItem $env:OBSIDIAN_VAULT
```

然后运行 Hermes 设置向导：
```
hermes setup
```

或通过 Nous Portal 的最短路径：
```
hermes setup --portal
```

验证安装：
```
hermes doctor
```

> `hermes doctor` 检查依赖、PATH、provider 配置，标出常见问题。

### 模型层：把 Hermes 连上 MiniMax M3

Hermes 把"用什么模型"当作一等配置。

选模型的主命令：
```
hermes model
```

这会打开模型选择流程，列出支持的 provider 和模型。

**实际操作路径：**
1. 安装 Hermes（CLI 或 Desktop）
2. 运行 `hermes setup` 或 `hermes setup --portal`
3. 运行 `hermes model`
4. 选择能访问 MiniMax M3 的 provider 路径
5. 保存为默认长上下文模型

已知环境变量和 provider 格式也可用：
```
hermes config set
```

**我日常的划分：**
- **M3 用于**：读大量笔记文件夹、合并重复笔记、用我的语气写结构化总结、长研究链（不断增长的上下文）、代码密集的多步 agent 任务
- **小快模型用于**：文件名重命名、搜字符串、格式化 YAML 等小工具操作

> **经验法则：** 用快速便宜的模型做小工具操作。用 MiniMax M3 做任何依赖大上下文、结构或长推理的事。这才是这个栈真正超越标准聊天的地方。

---

## 可扩展的工作模式

vault 结构决定了这个方案对普通人的实用性。

**实用布局：**

```
MainVault/
  Inbox/
  Projects/
  People/
  Reading/
  Daily/
  Reviews/
  AI/
    Hermes/
    MiniMax/
```

**为什么这样有效：**
- *Inbox/* — 原始捕捉和粗略转储
- *Daily/* — 低摩擦的日常日志
- *Reading/* — 源笔记、高亮和引用
- *Projects/* — 持久化产出和进行中的工作
- *Reviews/* — 周度和月度总结

Hermes 在每个文件夹有明确职责时表现最佳。如果你的 vault 混乱，Hermes 仍然能帮上忙，但会花更多时间"理解混乱"而不是"改进混乱"。

**简单的操作规则：**
- 人类自由写入 Inbox/、Daily/ 和 Reading/
- Hermes 被允许总结到 Projects/、Reviews/ 和 AI/ 等主题文件夹
- 长期笔记存在于稳定可预测的文件夹

这给了 agent 权限边界——即使你从未在 YAML 中正式定义它们。

---

## 真正值得自动化的工作

> Hermes 最强的用例不是"回答一个问题"——而是重复的转换。

**具体例子：**
- 把昨天的日记变成结构化总结
- 将 10 篇粗略的阅读笔记合并为一篇长青笔记
- 从项目文件夹中提取未解决的问题
- 从散落的笔记构建周度回顾
- 对比当前笔记和旧笔记，标出观点变化

**这就是 MiniMax M3 真正发光的地方。**
短上下文模型能很好地总结单篇笔记。M3 能总结一个 50 篇笔记的文件夹、与 vault 中 10 个 MOC 交叉引用、然后用你自己的语气和标签提出一篇 1000 字的概述——因为它看到了整个图谱。

**我最常跑的任务：** 把一篇新文章丢进 raw/，让 M3 编译成 5 节笔记（# 简介 → # 在我研究中的上下文 → # 与 vault 的链接 → # 标签 → # 相关），然后观察它：
- 从 41 标签分类体系中正确选一个标签
- 写 8-12 个指向现有笔记的 wikilink
- 告诉我哪个 MOC 需要更新

> 用 200K 模型，我大概 4 个里能对 3 个。
> 用 M3，在一个 ~500 文件的 vault 上，一个 pass 全对。

**复合效应：** 我以这种方式编译的每篇笔记都成为 M3 下一次提问的上下文的一部分。6 个月的每周编译后，模型"知道"我的语气、我的标签系统、以及我为什么样的工作更新哪些 MOC——不需要我再重新训练任何东西。

终端里的典型流程：
```
hermes
```

在 Hermes 内部，类似这样的任务：
- "读 Reading/AI Agents/ 里的所有内容，创建一篇叫 agent-architecture-overview.md 的合并笔记"
- "扫描最近 7 天的 Daily/，写一篇周度回顾到 Reviews/2026-W24.md"
- "找出 Inbox/ 和 Projects/ 中的重复想法，提出合并方案"

---

## 定时任务：无人在场的知识维护

Hermes 不仅为聊天构建，也为网关、调度器和后台执行构建。因为最好的 PKM 工作流通常是异步的，而不是随机的。

**有用的定时任务：**
- 每天早上 08:00 — 把昨天的笔记总结到 Reviews/ 中的日报
- 每周五 — 从 Daily/ 和 Projects/ 生成周度回顾
- 每天一次 — 扫描孤立笔记和结构性问题
- 每晚 — 把新的阅读高亮变成原子笔记并建立链接

**架构上的重大转变：**
- 聊天答案会消失
- 定时笔记维护会复合增长
- 随着时间的推移，这个复合效应才是把"只是笔记"变成真正第二大脑的关键

---

## 完整的实操路径

### 1. 安装 Hermes
macOS / Linux / WSL2：
```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```
Windows：
```powershell
irm https://hermes-agent.nousresearch.com/install.ps1 | iex
```
Desktop：从[官方页面](https://hermes-agent.nousresearch.com/)下载安装器

### 2. 配置 agent
```
hermes setup
# 或
hermes setup --portal
```

### 3. 验证健康状态
```
hermes doctor
```

### 4. 选择模型
```
hermes model
```
选择能访问 MiniMax M3 的 provider 路径，保存为默认长上下文模型。

### 5. 开始使用
上手后最有用的第一步不是"写代码"，而是：
- 把 Hermes 指向你的 vault
- 给它恰好一个文件夹
- 让它产出一篇干净的 markdown
- 在 Obsidian 中打开并检查结果
- 重复直到这个工作流变得无聊且可靠

> 当一个循环感觉稳固了，再加一个 → 然后再加一个。
> 这就是你把 Hermes + MiniMax M3 + Obsidian 从"酷想法"变成真正基础设施的方式。

---

## 结尾

> **不要只是读。去构建它。从今天开始改变你的工作流。**

如果你觉得有用：
- 收藏这篇文章。链接会变，新 repo 每周冒出来——你会需要这个参考资料
- 点赞和转发上面的线程，帮助其他构建者跳出聊天机器人陷阱
- 关注 @polydao，每周深度解析 AI 架构、量化交易和 agent 经济
- 加入 TG 频道：Buzzoni Notes——分享原始提示词、自定义技能和太早不适合 X 的 alpha

---

*整理于 2026-06-23，来自 @polydao 的 X 长文*
