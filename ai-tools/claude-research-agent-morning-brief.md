---
title: "How to Build a Claude Research Agent That Reads the Internet Every Morning and Briefs You in 5 Mins"
tags:
  - claude
  - research-agent
  - automation
  - n8n
  - mcp
  - obsidian
date: 2026-05-25
source: "https://x.com/cyrilxbt/status/2058749052712276332"
authors: "Cyril (@cyrilxbt)"
---

# Claude 晨间研究 Agent：每天自动阅读互联网，5 分钟完成简报

> **来源：** [@cyrilxbt](https://x.com/cyrilxbt/status/2058749052712276332)  
> **核心理念：** 每天早晨在你打开任何东西之前，Claude agent 已经读完了所有对你重要的信源，过滤了无关内容，提炼了有价值的发展，整理成结构化简报存入你的 Obsidian 笔记库。  
> **结果：** 醒来 → 读简报 → 5 分钟掌握今天需要知道的一切 → 开始工作。

---

## 痛点：大多数人的早晨

大多数人每天早晨的流程：
1. 打开 Twitter 刷 20 分钟噪音
2. 打开邮件，进入被动响应模式
3. 45 分钟后，焦虑、落后，有效信息为零

**这个 Claude 研究 Agent 永久解决了这个问题。**

---

## Agent 的四大功能

每天早晨自动执行四个任务：

| 功能 | 说明 |
|------|------|
| **Source Monitoring** | 读取所有配置的信源：行业新闻、竞品网站、学术论文、特定 newsletter、YouTube 频道 |
| **Signal Filtering** | 不是总结所有内容——根据你定义的判断标准，识别真正重要的信息 |
| **Synthesis** | 不是列点——而是整合成结构化叙述：发生了什么、为什么重要、和你已知信息的关联 |
| **Delivery** | 每天定时存入你的 Obsidian 库指定位置，无需手动触发 |

这四个功能用 **5 分钟阅读** 替代了每天 **45 分钟的信息搜集**。

---

## 技术架构：五个组件

```
┌─────────────────────────────────────────────────────┐
│                   N8N (调度层)                        │
│  Schedule Trigger → Read Files → API → Save Files   │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│              Claude API (智能层)                      │
│  读取原始信息 → 应用过滤标准 → 合成结构化简报          │
└──────────────────┬──────────────────────────────────┘
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
┌─────────┐ ┌──────────┐ ┌──────────┐
│ Filesys │ │  Brave   │ │Obsidian  │
│ MCP     │ │ Search   │ │ Vault    │
│ (本地)  │ │ MCP (网) │ │ (存储)   │
└─────────┘ └──────────┘ └──────────┘
```

### 每个组件的角色

| 组件 | 角色 |
|------|------|
| **Claude** | 智能层。读取原始信源，应用过滤标准，合成结构化简报 |
| **Filesystem MCP** | 连接 Claude 到你的 Obsidian 库，直接读写 vault 文件 |
| **Brave Search MCP** | 实时网络搜索，突破 Claude 训练数据截止日期限制 |
| **N8N** | 调度整个工作流：定时触发、传递上下文、保存输出 |
| **CLAUDE.md** | 上下文层，让简报对"你的具体情境"有针对性 |

**缺少任何一个组件，系统质量都会下降。**

---

## 前提条件搭建

### 1. Claude Desktop MCP 连接

安装 Claude Desktop（[claude.ai/download](https://claude.ai/download)），配置 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/your/obsidian/vault"
      ]
    },
    "brave-search": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic-ai/server-brave-search"
      ],
      "env": {
        "BRAVE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

- Brave Search API Key 在 [brave.com/search/api](https://brave.com/search/api) 获取
- 免费版每月 2000 次查询，日更 agent 绰绰有余
- 配置完成后重启 Claude Desktop，验证连接是否生效

### 2. Obsidian Vault 结构

```tree
vault/
├── BRIEFINGS/
│   └── [YYYY-MM-DD]-morning-brief.md  ← 每天自动生成
├── CLAUDE.md
└── (其他笔记)
```

### 3. N8N 自托管

- 最低配置：**$5/月 DigitalOcean droplet**
- 完整搭建约 **30 分钟**（创建 droplet → SSH → npm install → 配置为系统服务）
- 自托管的好处：无限工作流运行，无按次计费

---

## 核心：CLAUDE.md 研究上下文

通用 research agent 产出通用简报。配置了你个人上下文的 research agent，产出的每条信息都直接与你的工作和决策相关。

### CLAUDE.md 研究上下文模板

```markdown
# Research Agent Context

## Who I Am
[你的名字、角色、你在做什么]

## My Primary Focus Areas
[列出你需要保持更新的具体主题、行业或领域]

## What Constitutes Significant Information for Me
- [事件类型 1] → [为什么重要]
- [事件类型 2] → [为什么重要]

## What I Specifically Do NOT Want
[最重要的部分，大多数人会跳过]
```

**"What I Specifically Do NOT Want" 是最重要的部分。** 没有它，Claude 会包括所有与你主题相关的内容。有了它，Claude 会激进过滤，简报只包含你真正会采取行动的信息。

---

## Research Agent Prompt

这是每天早晨执行的核心 prompt，放到 N8N 工作流中作为发给 Claude API 的消息：

```
You are my personal research agent. Your job is to produce 
my morning intelligence brief.

Read my research context from CLAUDE.md in my vault.

Then execute the following research sequence:

STEP 1: SEARCH
Use Brave Search to search for developments since 
last briefing in each of my primary focus areas.

STEP 2: DEEP READ
For each search result that passes my significance 
criteria, read the full content and extract the 
specific development, its implications, and why 
it matters to my work.

STEP 3: SYNTHESIZE
Produce a structured brief with:
- Top developments (max 3-5 items)
- For each: what happened, why it matters, 
  what I should do about it
- One-sentence bottom line for each item

STEP 4: DEPOSIT
Write the brief to BRIEFINGS/[today]-morning-brief.md

Format the brief so it is readable in 5 minutes.
```

---

## N8N 工作流：5 个节点

```
[Trigger] → [Read CLAUDE.md] → [Prepare API] → [Claude API] → [Save to Vault]
```

### Node 1: Schedule Trigger

建议时间：**早晨 6:00**（在你打开电脑之前准备好）

```cron
0 6 * * 1-5    ← 周一至周五 6AM
0 6 * * *      ← 每天 6AM（含周末）
```

### Node 2: Read CLAUDE.md

读取保存研究上下文的 CLAUDE.md → 输出完整文本。

### Node 3: Prepare API Request

将 prompt 模板 + CLAUDE.md 内容合并为 Anthropic API 调用：

```javascript
const claudeMd = $node["Read CLAUDE.md"].json.content;
const today = new Date().toISOString().split('T')[0];
const time = new Date().toLocaleTimeString();

const systemPrompt = `You are a personal research agent...`;
const userPrompt = `Today is ${today}. Current time is ${time}.\n\nMy research context:\n${claudeMd}\n\nProduce my morning brief.`;

return {
  model: "claude-sonnet-4-20250514",
  max_tokens: 4096,
  system: systemPrompt,
  messages: [{ role: "user", content: userPrompt }]
};
```

### Node 4: Claude API Call

```http
POST https://api.anthropic.com/v1/messages
Headers:
  x-api-key: [YOUR ANTHROPIC API KEY]
  anthropic-version: 2023-06-01
  content-type: application/json
Body: [Node 3 的输出]
```

### Node 5: Save to Vault

提取 Claude 返回的文本内容，写入 BRIEFINGS 文件夹：

```javascript
const response = $node["Claude API Call"].json;
const content = response.content[0].text;
const date = new Date().toISOString().split('T')[0];

return {
  filename: `${date}-morning-brief.md`,
  content: content
};
```

### Optional: Telegram 通知

添加 Telegram bot 通知节点，简报就绪时推送手机通知：

```
Message: "Morning brief ready: BRIEFINGS/[DATE]-morning-brief.md"
```

这样你在起床前就能在手机上看到简报。

---

## 配置信源列表

Brave Search MCP 处理开放式网络搜索。但一些最高价值的信源需要显式配置：

```markdown
## Specific Sources to Monitor

### Daily Checks
- news.ycombinator.com — check front page for AI and developer tools
- reddit.com/r/MachineLearning — significant paper releases only
- reddit.com/r/ClaudeAI — product updates and workflow patterns
- [your industry news site]

### Weekly Checks
- [academic journals / arXiv]
- [competitor blogs]
- [specific newsletters]
```

---

## 反馈循环：简报会越来越精准

每天早上花 **2 分钟** 在简报底部标注你的反馈：

```markdown
## My Notes on This Brief
[什么有用、什么是噪音、缺少了什么]
```

**每周日** 运行这个 prompt：

```
Read all morning briefs from the past week in my 
BRIEFINGS folder and read all annotations in 
the "My Notes on This Brief" sections.

Based on my annotations, update my research 
CLAUDE.md with:
- New sources to add
- Sources that produced noise → reduce priority
- New filtering criteria
- Topics to deprioritize
```

**结果：**
- **第 1 周**：通用简报
- **第 1 个月**：精准校准到你的注解
- **第 2 个月**：周度合开始揭示日度快照中不可见的模式
- **第 3 个月**：AI 对你领域的了解程度相当于专职分析师

---

## 高级配置扩展

### Topic Deep Dives

当日简报出现重大发展时，加入深度研究队列：

```markdown
DEEP-DIVE: [topic from today's brief]
```

队列处理器执行更全面的研究 session，生成详细的分析笔记。

### Competitive Intelligence Alerts

配置独立的工作流，**每 4 小时**检查竞品新闻。发现重要信息时立即推送 Telegram 通知，而不是等到第二天早晨。

### Weekly Synthesis

每周日早晨，Claude 读取过去 7 天的日简报，生成周度合成：

> - 本周最大的主题及其对你的领域长期意味着什么
> - 最重要的单一事件及其应对
> - 你预期会发生但没有发生的事情及其含义

周度合成经常揭示任何单日简报中不可见的模式。

### Research on Demand

将任意主题放入 QUEUE 文件夹，前缀 `RESEARCH:`：

```
RESEARCH: quantum-computing-applications-in-finance.md
```

队列处理器立即执行深度研究，而非等待次日早晨周期。

---

## 30 天后的变化

| 时间 | 效果 |
|------|------|
| **第 1 天** | 非一般的价值 —— 第一个早晨简报 |
| **第 30 天** | 简报校准到你的特定注解。持续产生噪音的主题被移除。持续产生信号的信源被优先 |
| **第 60 天** | 周度合成开始揭示跨 8 周数据的趋势 |
| **第 90 天** | 你的研究系统对领域的了解程度 = 专职分析师 |

> 你的竞争对手还在每天花 45 分钟刷噪音。  
> 你花 5 分钟读信号。  
> 这个差距不仅是时间节省——而是**基于更好信息的决策质量**。

---

> 关注 [@cyrilxbt](https://x.com/cyrilxbt) 获取 N8N 工作流模板、CLAUDE.md 研究上下文结构和 Brave Search 查询模式。

---

*整理于 2026-05-25，来源：[@cyrilxbt](https://x.com/cyrilxbt/status/2058749052712276332)*
