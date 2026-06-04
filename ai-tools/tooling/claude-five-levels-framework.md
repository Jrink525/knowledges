---
title: "Claude 五个能力等级框架 —— 从聊天到基础设施的进阶之路"
tags:
  - claude
  - claude-code
  - claude-cowork
  - claude-levels
  - proficiency-framework
  - agent-architecture
  - mcp
  - plan-mode
  - sub-agents
  - worktrees
  - cloud-routines
  - hooks
  - trust
date: 2026-05-12
source: "https://x.com/nateherk/status/2054206361240490434"
authors: "@nateherk"
stats:
  likes: 66
---

# Claude 五个能力等级框架 —— 从聊天到基础设施的进阶之路

> **来源：** @nateherk 的 X 长文（400+ 小时 Claude 使用经验总结）  
> **核心理念：** 大多数人的 Claude 使用水平停留在 L1-L3，实际上有清晰的五个等级。每一级解锁不同的工作类别、不同的小时节省、不同的收费天花板。

---

## TL;DR

| 等级 | 名称 | 核心能力 | 节省时间 | 收费天花板 |
|------|------|---------|---------|-----------|
| L1 | Enthusiast | Chat 当搜索框用 | ~30 分钟/天 | — |
| L2 | Beginner | Projects + Memory + Connectors + 文件创建 + Office 插件 | 5+ 小时/周 | — |
| L3 | Intermediate | Cowork + 文件系统访问 + Skills + 定时任务 + 手机控制 | 10+ 小时/周 | 可接自动化服务 |
| L4 | Advanced | Claude Code + Plan Mode + Sub-agents + Worktrees + MCP | 数十小时/周 | $5K-$15K 项目 |
| L5 | Architect | Cloud Routines + Hooks + Channels + Headless + Agent 团队 | 24/7 自动化 | 基础设施级 |

---

## Level 1：Enthusiast（爱好者）

打开 Claude → 问一个问题 → 得到回答 → 关掉标签页。这就是地板。

### 特征

大多数人停留在此，因为他们不知道 Claude 可以跨会话保持上下文、组织项目、接入日常使用的工具。他们把 Claude 当"返回段落的搜索引擎"。

### 快速升级

- **粘截图**。Claude 可以读取图像。一半的 L1 用户还在手动输入一张截图两秒就展示清楚的内容。

### 升 L2 的作弊码

> **创建你的第一个项目。** 选一个你反复回来的主题：你的业务、副业、重复性工作。放几份参考文档，写一段关于你是谁、你希望 Claude 如何回应的 system prompt。

从此项目内的每次聊天都预加载了上下文。这一步是通往 L2 的门。

---

## Level 2：Beginner（初学者）

Project 是这一级的脊梁。你打开一个项目中的新聊天，问"我们上周关于 Q2 发布做了什么决定"，Claude 能拉出之前聊天的内容、自动引用来源、无缝续接。

Claude 不再是"无状态工具"——它有了连续性。

### 6 个关键特性

| # | 特性 | 说明 | 付费 |
|---|------|------|------|
| 1 | **Memory + 历史聊天搜索** | 记住你的角色、偏好、数周前的决策。Memory 在免费用。历史搜索需付费。 | 部分免费 |
| 2 | **Connectors（连接器）** | Slack、Google Drive、Gmail、GitHub、Notion、Calendar 等 50+ 工具。OAuth 登录即用。 | Pro+ |
| 3 | **文件创建** | 从 Chat 直接生成真实的 Excel（含公式）、PPT、Word、PDF，可直接下载发送给客户。**免费用户也能用。** | 全部免费 |
| 4 | **持久化 Artifacts** | 跨会话保存数据，可调用 Claude API，可发布公开链接。非开发者也能在 Chat 中构建一个可用的客户反馈追踪器。 | Pro+ |
| 5 | **Inline Visuals（内联图表）** | 在聊天中构建图表，可交互切换类型、添加变量。 | 全部免费 |
| 6 | **Office 原生插件** | Excel/PPT/Word 中的原生插件。Claude 读取整个表格、解释公式、保持品牌色和布局。三个插件共享上下文，可在 Excel 分析后切换到 PPT 直接生成。 | Pro+ |

### 类比

> L1 是绝顶聪明但无记忆的实习生。L2 是同一个实习生，但现在他记住了每一次对话、有一叠项目文档、可以随时从你的工具拉数据、在一天结束时交给你一份完成好的 PPT。

Claude 在这里开始"回本"（5+ 小时/周节省）。

### 天花板

Claude 仍然不能在你的机器上执行操作。你在手动复制输出、手动运行变更。

### 升 L3 的作弊码

> **不要再试图让 Chat 做一切。** 打开 Claude Desktop，点击 Cowork 标签。

---

## Level 3：Intermediate（中级）

如果你曾想"要是 Claude 能直接在我的电脑上搞定这个，而不是告诉我怎么做就好了"——你准备好了。

> Cowork 就像 n8n 住在你电脑上，有完整的文件系统权限。你描述结果，Claude 自己找出实现路径。

### 5 个关键特性

| # | 特性 | 说明 |
|---|------|------|
| 1 | **文件系统访问** | 在隔离的虚拟机中运行，对你授权的文件夹有真实的读写权限。下载文件夹三个月没整理？一句话搞定。 |
| 2 | **Skills（技能）** | 可复用的工作流，定义为一个 Markdown 文件。建一次"周报生成"，之后只需说"生成这周的报告"。100+ 社区 Skill，16+ Anthropic 官方出品。 | 
| 3 | **Scheduled Tasks（定时任务）** | `/schedule` 设定定时任务：每天 8 点晨会、每周一竞争对手简报。**需要电脑开着。** |
| 4 | **移动端控制（Dispatch）** | 手机配对桌面，从通勤路上、健身房发任务。Claude 在桌面端执行，完成后通知你。 |
| 5 | **Claude Design** | Anthropic Labs 的独立产品，随 Pro 套餐包含。用自然语言描述原型 → Claude 设计。可读取 GitHub repo、品牌指南，构建完整设计系统。非开发者可在 Claude Design 设计前端 → 通过 Claude Code 发布，全程零代码。 |

### 天花板

Cowork 是安全和友好的，但不够精确。当你需要真正的版本控制、工程级的严谨、或客户愿意付 $5K+ 的系统时，你会超出 Cowork 的能力范围。

这是第一个节省 10+ 小时/周的级别，第一个非开发者也能将自动化作为服务出售的级别。

### 升 L4 的作弊码

> **建一个 Claude 可以信赖的文件夹结构。** 一个 about-me 文件、一个 templates 文件夹、一个 projects 文件夹、一个 outputs 文件夹。告诉 Cowork："先读 about-me。永远不要编辑我的模板。所有产出都放到 outputs 文件夹。"

---

## Level 4：Advanced（高级）

> Boris Cherny（Anthropic 内部 Claude Code 的构建者）每天并行运行 **5 个 Claude 会话**。编号的终端标签页，每个在自己的隔离工作区里。它们不能冲突，不能看到彼此的文件。他启动它们，走开，回来时多个 PR 已准备好审查。

这不是并行生产力。这是**不同类别的工作**。

### 5 个关键能力

#### 1️⃣ claude.md 文件

项目根目录的 Markdown 文件，Claude 在每次会话开始时读取。**技术栈、命名规范、你是谁、项目目标、"永远不要做 X"。**

**关键技巧：** 每次 Claude 犯错，说"更新你的 claude.md 确保不再犯同样错误"。几周后，它自己学会了你的工作方式。

**注意：** claude.md 会在每次对话中被读取。超过 200 行会增加 token 消耗。重要的细节放进独立文件，用 `@filename` 引用。

#### 2️⃣ Plan Mode（计划模式）

按 Shift+Tab 两次切换。Claude 阅读代码、展示计划、提问、等你批准。

**隐藏技巧：** **Opus Plan** — Opus 做规划，Sonnet 做执行。强模型负责关键推理，便宜模型负责执行。成本降低一半，质量不降。

#### 3️⃣ Sub-agents（子 Agent）

专门的 Claude 做专门的工作：一个写测试，一个做安全审查，一个写文档。每个在自己的上下文窗口中运行，主会话的噪音不会污染子 Agent，反之亦然。多个子 Agent 可并行运行。

> 你实际上在组建一个迷你工程团队。通过主会话沟通。

#### 4️⃣ Worktrees（工作树）

`claude-worktree feature-name` 启动一个隔离的 git 工作区，在独立分支上。再开一个终端再来一次。2-4 个 Claude 同时工作，文件永不覆盖。

一个实现功能，一个修 Bug，一个写测试——全部并行。

#### 5️⃣ MCP（Model Context Protocol）

让几乎任何外部工具接入 Claude。

**关键警告（Anthropic 官方文档）：** 当 CLI 工具存在时，**用 CLI 而非 MCP**（如 GitHub、AWS、Google Workspace）。CLI 比等价 MCP server 少用 **60-70% 的 token**，因为啥都没加载到上下文里，直到你真正运行它。

**MCP 使用优先序：** CLI 第一 → API 端点第二 → Skills 第三 → MCP 只在其他都不行时用。

### L4 的强力技巧

| 技巧 | 说明 |
|------|------|
| **掌握上下文窗口** | Opus 4.7 的 100 万 token 窗口超过 50% 容量后质量下降。`/compact` 主动压缩，不要等警告 |
| **Auto Mode + Focus** | Shift+Tab 切换到 auto，安全命令自动放行。`/focus` 隐藏中间步骤只看最终结果 |
| **Verification Loop** | Boris 说这是最重要的习惯：给 Claude 一个检查自己工作的方式。浏览器测试 UI、截图验证、不自测完不交 PR。**质量提升 2-3 倍** |
| **自定义 Slash Commands** | 同一个提示出现两次就做成命令。Boris 的 `/commit-push-pr` 一天用几十次——一键完成整套提交流程 |

### 其他值得知道的命令

| 命令 | 作用 |
|------|------|
| `/rewind` (Esc×2) | 丢弃失败的尝试，不污染会话 |
| `/btw` | 中间问个问题，不打断主流程 |
| `/branch` (原 `/fork`) | 分叉会话——试一条路，跳回来试另一条。**对话的 git** |
| `/insights` | 读取过去一个月的使用模式：重复做的事、浪费 token 的地方、该做成 Skill 的提示 |
| `/output-style new` | 切换 Claude Code 的"人格"：default / explanatory / learning / 你自定义 |

### 类比

> Claude Chat = 你的实习生。Claude Cowork = 你的助手。Claude Code = 你的工程团队。每个专业，并行工作，都向你汇报。

### 天花板

并行工作手动管理 → 你成了自己的瓶颈。"Fire off Claudes, watch them, switch contexts" 不是在扩展，是在**当保姆**。

这里自由职业/外包项目的收费达到 **$5K-$15K**。

### 升 L5 的作弊码

> 找到你那周用 Claude Code 做得最重复的事情（审查、依赖检查、手动执行同一条命令）。那就是你的第一个云端自动化。

---

## Level 5：Architect（架构师）

> 如果你曾合上笔记本但希望工作还在进行——你准备好了。

想象这个场景：笔记本合上了。你在吃晚饭。有人打开了一个 PR。Claude 在云端处理它：审查代码、贴出详细反馈。你打开手机——一切已经完成。你啥都没碰。

### 3 个关键技术

#### 1️⃣ Cloud Routines（云上定时任务）

保存在 Anthropic 云端的 Claude Code 配置。**你的电脑可以关机。**

三种触发方式：
- **定时**：每天早上 8 点做 backlog triage
- **API 调用**：外部系统触发
- **GitHub 事件**：PR 一打开就自动审查

这里是 Claude 成为基础设施而非工具的关键点。

#### 2️⃣ Hooks（安全闸）

在生命周期事件触发的自定义逻辑：

| Hook 类型 | 作用 |
|-----------|------|
| **Pre-tool-use** | 危险命令执行前拦截 |
| **Post-edit** | Claude 修改文件后自动格式化 |
| **Stop** | 长时间运行任务完成时发 Slack 通知 |

这是"酷炫 demo"和"你敢信任它做实际工作的生产系统"之间的分水岭。

#### 3️⃣ Channels（通道）

从终端之外控制会话：Discord、Telegram、iMessage、自定义 Webhook。

- **单向**：外部事件触发 Claude（日历事件→研究 Agent→准备客户简报）
- **双向**：你直接发短信给 Claude，它对你的真实代码库工作

### 更多组件

| 组件 | 说明 |
|------|------|
| **Headless Mode + Agent SDK** | `claude -p "xxx"` 无人类会话。Python/TypeScript SDK 让你在自己的产品上构建 Claude Code 引擎 |
| **Remote Control** | `/remote-control` → 扫 QR 码 → 手机走路编程。会话在电脑上跑，手机是遥控器 |
| **Memory Consolidation (Autodream)** | 背景子 Agent 在会话间修剪记忆文件：删除矛盾事实、合并重复、将"昨天"转为实际日期。**需手动开启** |
| **Task Budgets** | Opus 4.7 Beta：给 Agent 整个执行的 token 预算。模型自己调控，预算耗尽前优雅收尾。目前仅 API，尚未进入 Claude Code/Cowork |
| **Agent Teams** | 实验性：多个专门 Claude 由主 Agent 协调。**与 Sub-agents 不同——它们可以互相通信**。可共享任务列表、互相挑战、辩论。MCP（工具访问）和 A2A（Agent 间通信） |

### L5 的关键习惯

> 最高杠杆的技能不是从零构建。而是发现和利用已有的东西。社区有 **5,000+ Skills、800+ MCP 服务器、3,000+ 市场插件**。去 X，去 Reddit。找到适用的开源项目，按你的需求定制。

---

## 真正的瓶颈：L4 到 L5 之间的信任鸿沟

> **L5 的瓶颈不是技术，是信任。**

几乎任何人都能设置云端定时任务。他们不会。因为把方向盘交给一个你睡觉时还在运行的系统，感觉太鲁莽了。

**解决方法和学开车一样：**

1. 不要在高速公路上开始。**在空停车场开始。**
2. 选一个低风险的 routine：每天发给自己的晨会摘要（不是发出去的外部消息）、每周依赖审计。
3. **每天看它运行。看它跑几周。不要碰它。**
4. 一旦你信任了第一个，你就能信任后面的十个。

> **谨慎部署。** "只管发布"不意味着你能设置了就不管了，特别是高度自主的 Agent。
>
> 单向数据搬运的自动化通常安全（确定性）。Skills 和 Claude Code Agent 非确定性但更强大。**从安全的开始。**

信任是在 L4 和 L5 之间的主要隔阂。这是需要重复练习和时间的技能，不是一个可以"安装"的功能。

---

## 总结：Claude 五级全景

| 等级 | Claude 是什么 | 节省 | 核心限制 |
|------|-------------|------|---------|
| L1 | 聪明的实习生，无记忆 | ~30 分/天 | 不知道它可以更好 |
| L2 | 有记忆的实习生，有项目文件夹 | 5+ 小时/周 | 无法在机器上执行 |
| L3 | 住在你电脑里的自动化引擎 | 10+ 小时/周 | 不够精确，无版本控制 |
| L4 | 你的工程团队，并行工作 | 数十小时/周 | 手动管理成为瓶颈 |
| L5 | 基础设施，你合上电脑它还在工作 | 24/7 | 信任——不是技术 |

---

## 与知识库其他文章的关联

- **[Claude Code 使用技巧手册](claude-code-advanced-tips-guide.md)** — @buhuaguo1 的技巧手册是 L4 的详细操作指南（命令速查、Skill 编辑、effort 调节）。本文是 L1-L5 的全景框架，二者互补：框架帮你定位自己在哪里，技巧手册帮你做那一级的动作。
- **[Agent Complexity Ratchet](../agent-engineering/agent-complexity-ratchet.md)** — Garry Tan 的"Agent 复杂度棘轮"中的 14 PR/72h 自动化，本质上是本文 L5 的实际案例（Cloud Routines + GitHub hooks + 并行 Worktrees）。
- **[10 Claude Code Agents Pipeline](../agent-engineering/10-claude-code-agents-pipeline.md)** — @zodchiii 的 10 个 Agent 是 L4 的典型拼图：PR Reviewer、Test Generator、Bug Hunter 都是 Sub-agents + Slash Commands 的实例。
- **[Agent Engineers Survival Guide](../agent-engineering/agent-engineers-survival-guide.md)** — @rohit4verse 的生存指南中关于"从小处入手、从最痛的失败模式入手"，与本文 "从空停车场开始" 的信任构建策略完全一致。
- **[claudemd-21-config-rules.md](claudemd-21-config-rules.md)** — L4 中 claude.md 文件的具体配置规则（200 行限制、Opus Plan 切换等），详见 claudemd 2.1。
- **[npx-skills-add-flow.md](../agent-engineering/npx-skills-add-flow.md)** — L3 Skills + L4 Custom Slash Commands 的底层安装机制。

---

*Processed on 2026-05-12 from X article by @nateherk*
