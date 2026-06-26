---
title: "Hermes Agent Masterclass"
tags:
  - hermes-agent
  - ai-agent
  - nous-research
  - self-learning
  - multi-agent
date: 2026-06-26
source: "https://x.com/akshay_pachaar/status/2054564519280804028"
authors: "Akshay 🚀 (@akshay_pachaar)"
---

# Hermes Agent 大师课：自进化 Agent 架构完整指南

> **来源：** [Hermes Agent Masterclass](https://x.com/akshay_pachaar/status/2054564519280804028) — Akshay 🚀 (@akshay_pachaar)
>
> 5.4M 阅读 · 6.2K 点赞 · 22.7K 收藏 · 778 转发

## 一、概述

Hermes Agent（Nous Research）在两个月内突破 90,000 GitHub Stars。和普通 Agent 不同，Hermes 解决了所有 Agent 的致命缺陷——会话结束后一切归零。

**一句话定位**：一个**越用越好用的 Agent**——跨会话记忆、自编写技能、后台垃圾回收和离线验证引擎（GEPA）。

### 与 OpenClaw 的架构对比

| 维度 | Hermes Agent | OpenClaw |
|------|-------------|----------|
| 核心哲学 | 围绕自学习 Agent 封装 Gateway | 围绕消息 Gateway 封装 Agent |
| 学习能力 | 内置自进化循环 | 依赖外部 Skill/Tool |
| 记忆系统 | 三层内置（MEMORY.md + SQLite + 外部插件） | 需自行配置 |
| 身份层 | SOUL.md（系统 Prompt #1） | 类似但非原生 |
| 技能进化 | 自主编写 + Curator 回收 + GEPA 验证 | 手动安装 |

---

## 二、架构设计

一切基于 `AIAgent` 类的 `run_agent.py`。CLI、消息网关、批处理、IDE 集成——都是同一个核心 Agent 的不同入口。

### 核心循环（ReAct 风格，同步）

```
构建 System Prompt → 检查是否需要压缩 → API 调用（可中断）→ 执行工具 → 循环
```

### 关键设计细节

**执行环境**：可在 6 种环境中运行——Local Terminal、Docker、SSH、Modal、Daytona、Singularity。改配置即可切换。

**模型兼容**：通过翻译层将任意 Provider 映射到三种 API 格式之一。Claude ↔ GPT ↔ Gemini ↔ Ollama 可一键切换。

**回合上限**：每个任务硬限制 **90 次工具调用**，子 Agent 共享同一预算。

---

## 三、身份层：SOUL.md

> 记忆 = Agent 知道什么。技能 = Agent 会做什么。身份 = Agent 是谁。

`~/.hermes/SOUL.md` 是系统 Prompt 中的**一号位**（slot #1），插入在所有其他内容之前。

- 手动编写，静态不变
- 定义人格、语气、沟通风格、硬约束
- 跨项目、跨会话保持一致
- 缺少时回退到内置默认身份

身份是所有学习的基础框架——记忆和技能都通过这个身份透镜来运作。

---

## 四、三层记忆系统（Three-Tier Memory）

### Tier 1：两个微型 Markdown 文件

| 文件 | 容量上限 | 用途 |
|------|---------|------|
| `MEMORY.md` | 2,200 字符 | 环境笔记、项目约定、工具技巧、经验教训 |
| `USER.md` | 1,375 字符 | 用户画像（名字、偏好、技能水平、应避免事项） |

- 会话开始时作为冻结快照注入 system prompt
- 中间写入立即持久化到磁盘，但下次会话才生效
- 容量达到 ~80% 时触发**合并**（Consolidation）——将相关条目浓缩为更密集的信息

### Tier 2：全文会话搜索

- 所有对话存于 SQLite，FTS5 全文索引
- Agent 可通过搜索找回数周前的对话
- 权衡：Tier 1 = 总是可见但小容量，Tier 2 = 无限容量但需主动搜索

### Tier 3：外部记忆提供者（8 个插件）

- 可插拔，不替代内置记忆
- 同一时间只能激活一个
- 激活后自动：每次 turn 前预取相关记忆、每个响应后同步、会话结束时提取

---

## 五、自进化技能（Self-Evolving Skills）

技能是带 YAML 前言的 Markdown 文件，作为 Agent 的**程序性记忆**——不是它知道什么，而是它怎么做。

### 技能结构

```yaml
---
name: "skill_name"
description: "一行描述"
---
## Skill Content

具体步骤、提示词、参考信息...
```

### 渐进式披露（Progressive Disclosure）

| 层级 | Agent 看到的内容 | Token 成本 |
|------|----------------|-----------|
| Level 0 | 仅名称 + 描述 | ~3K tokens（完整目录）|
| Level 1 | 完整的单技能内容 | 按需加载 |
| Level 2 | 技能内的参考文件 | 按需深入 |

### 自进化循环

Agent 自主使用 `skill_manage` 工具创建技能。触发条件：

- 完成复杂任务（5+ 工具调用）
- 遇到错误/死胡同后找到正确路径
- 用户纠正其方式
- 发现非平凡的工作流

支持 6 种操作：`create`、`patch`（首选，低 token 成本）、`edit`、`delete`、`write_file`、`remove_file`。

### Curator：技能垃圾回收

后台维护系统，非 cron 守护进程——在**空闲时**触发（7 天未运行 + Agent 空闲 2 小时以上）。

**两阶段操作**：

1. **自动转换**（确定性，无 LLM）：
   - 30 天未用 → 标记为**过时**
   - 90 天未用 → **归档**

2. **LLM 审查**（最多 8 轮迭代）：
   - 分叉一个 Agent，审阅所有自主创建的技能
   - 决定：保留/修补/合并/归档

**约束**：
- 绝不会触碰打包或 Hub 安装的技能
- 绝不会自动删除——最差情况是归档到 `.archive/`，一条命令可恢复
- 每次 Curator 运行前自动创建 `tar.gz` 快照，回滚一条命令即可
- 支持 `pin` 保护关键技能不被归档

---

## 六、GEPA：离线技能进化

> GEPA（Genetic-Pareto Prompt Evolution）— ICLR 2026 Oral，MIT 许可

**核心问题**：Agent 的自评估倾向于自我表扬，即使表现不佳也会认为自己做得很好。这一缺陷已获社区反馈证实。同一套自动生成系统可能用更差的版本覆盖手动优化。

### GEPA 工作流

```
1. 读取 Hermes 仓库中的当前技能
2. 生成评估数据集（综合测试用例 / 真实会话历史 / 手动精选黄金集）
3. 运行 GEPA 优化器：
   a. 读取执行轨迹 → 理解失败原因
   b. 生成候选变体
4. 用 LLM-as-Judge + 评分标准（非二值 pass/fail）评估
5. 应用约束门：
   - 完整测试套件 100% 通过
   - 技能 ≤ 15KB
   - 缓存兼容性不变
   - 语义目标不漂移
6. 最佳变体作为 PR 提交到 Hermes 仓库（非直接提交）
```

**成本**：每次优化约 $2-10（无需 GPU，纯 API 调用）。

**定位**：`RL/GRPO 微调之前的好方案`——当遇到瓶颈又不想投入微调成本时使用。

---

## 七、安装与运行

```bash
# 一行安装
curl -fsSL https://hermes-agent.ai/install.sh | sh

# 启动设置向导（配置 Provider、API Key、模型、工具）
hermes setup

# 终端聊天
hermes

# 连接 Telegram
hermes gateway --enable telegram
```

### 目录结构

```
~/.hermes/
├── config.yaml          # 核心配置（模型、终端后端、工具、MCP 服务器）
├── .env                 # 密钥（API Key、Bot Token）
├── SOUL.md              # 身份层
├── skills/              # 自学习循环所在地
├── state.db             # SQLite 对话存储（WAL 模式、FTS5 索引）
└── cron/                # 定时任务
    ├── jobs.json
    └── output/
```

### Skills Hub

Hermes 拥有官方 Skills Hub，共 **687 个技能**，18 个分类：

| 来源 | 数量 |
|------|------|
| 内置技能（随 Agent 发行） | 87 |
| 可选技能（按需启用） | 79 |
| Anthropic 贡献 | 16（frontend-design, pdf, pptx, docx, mcp-builder 等）|
| LobeHub 社区 | 505 |

还可添加任意 GitHub 仓库作为自定义 tap：

```bash
hermes install skill https://github.com/your-org/your-skills-repo
```

---

## 八、多 Agent 架构（Profiles）

Profile 是**完全隔离的 Hermes 实例**——各自拥有独立的配置、记忆、技能、会话和 SOUL.md，默认不共享任何东西。

### 创建团队

```bash
# 创建团队目录
hermes config set team_name "my-agents"

# 创建三个 Profile
hermes profile create designer --clone default
hermes profile create programmer --clone default
hermes profile create researcher --clone default
```

### 配置 Telegram Bot

每个 Profile 需要自己的 Bot Token（BotFather 上 `/newbot` 跑三次）：

```bash
hermes gateway --enable telegram --profile designer
hermes gateway --enable telegram --profile programmer
hermes gateway --enable telegram --profile researcher
```

### 个性定制

编辑每个 Profile 的 `SOUL.md` 赋予不同人格。

**Designer**（设计师 Agent）：

```
You are Pixel, a skilled graphic designer.
You create functional, elegant designs.

— You think in design systems, not just individual pages.
— Your default output format is SVG.
— You ask clarifying questions before generating.
— You never use placeholder text.
```

**Programmer**（程序员 Agent）：

```
You are a senior software engineer.
You write clean, testable, well-documented code.

— Plan before you act.
— Prefer simple solutions.
— Always test your code.
— Use Claude Code for all executions.
```

**Researcher**（研究员 Agent）：

```
You are a deep research assistant.
You track emerging trends in AI.

— Read papers before summarizing.
— Cite your sources.
— Distill technical concepts to actionable insights.
— Prepare a daily digest for the user.
```

---

## 九、高级定制

### 程序员 + Claude Code 集成

通过 Claude Code CLI 执行代码，Hermes 负责编排：

```
启动提示词：
"I already have a Claude Max subscription. You are my staff engineer who
helps me with my day-to-day coding tasks, and under the hood you use
Claude Code for all the executions. Set yourself up accordingly."
```

成功后，所有编码任务（读文件、写代码、跑测试、commit、push）都通过 Claude Code 执行。

### 设计师 + 个人风格定制

让设计师学习你的视觉风格：

1. 拖拽参考图片到 CLI / 在 Telegram 中附加
2. 发送提示词让设计师研究并编码你的风格
3. 设计师自动创建 SKILL.md + Python 脚本

之后每次要求新插图，都会以你的风格指纹为基础生成。

---

## 十、定时任务（Cron）

Hermes 内置调度器，Gateway 每 60 秒检查一次，执行到期任务。

### 自然语言创建

```
"每天早上 8 点将 AI 新闻摘要发送到我的 Telegram"
```

Hermes 自动将自然语言转换为 cron 表达式。

### 其他模式

- **一次性延迟**：`/cron add 30m "提醒我检查构建"`
- **重复间隔**：`/cron add "every 2h" "检查服务器状态"`
- **标准 cron**：`/cron add "0 9 * * 1-5" "工作日早9点"`
- **技能绑定**：`/cron add "every 1h" "总结新文章" --skill blogwatcher`
- **任务链**：一个 cron 的输出通过 `context_from` 标志成为下一个 cron 的输入

---

## 十一、关键设计原则总结

| 原则 | 说明 |
|------|------|
| **身份优先** | SOUL.md 是所有学习的固定框架 |
| **渐进式披露** | 技能目录 3K tokens，内容按需加载 |
| **零遗忘设计** | 三层记忆覆盖最短（当前会话）到最长（数周历史）|
| **写后验证** | GEPA 通过执行轨迹而非自我评估来优化技能 |
| **安全回退** | Curator 从不自动删除，归档可恢复 |
| **平台无关** | CLI ↔ Telegram ↔ IDE 同一套核心 |
| **模型无关** | Claude ↔ GPT ↔ Gemini ↔ Ollama 一键切换 |
| **物理隔离** | Profiles 之间零共享，适合多角色 |

---

> **参考资源**：
> - [Nous Research Hermes Agent (GitHub)](https://github.com/NousResearch/hermes-agent)
> - [Hermes Self-Evolution (GEPA)](https://github.com/NousResearch/hermes-agent-self-evolution)
> - [Hermes Skills Hub](https://hermes-agent.ai/skills)
> - 原始推文：[@akshay_pachaar](https://x.com/akshay_pachaar/status/2054564519280804028)

---

*整理于 2026-06-26，基于 X 长文提取补充。*
