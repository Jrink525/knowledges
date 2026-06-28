---
title: "Hermes Agent 完全指南：自学进化、三层记忆、GEPA 优化"
tags:
  - hermes-agent
  - ai-agent
  - nous-research
  - memory
  - self-evolution
date: 2026-06-28
source: "https://x.com/akshay_pachaar/status/2054564519280804028"
authors: "Akshay 🚀"
---

# Hermes Agent Masterclass 中文翻译

> **来源：** [Hermes Agent Masterclass](https://x.com/akshay_pachaar/status/2054564519280804028) — Akshay 🚀 (@akshay_pachaar)

---

Hermes Agent（Nous Research 出品）在两个月内收获了 **90,000+ GitHub stars**。开发者们正在悄悄构建能学习自己工作流、记住上下文、24/7 运行的个人 AI 智能体。

本文涵盖：自学进化技能、三层记忆系统、GEPA 离线优化，以及从 1 个到 10 个智能体的规模化部署。

本文的插图均由文中搭建的 Pixel 设计师智能体制作。

---

## 一、Hermes Agent 是什么？

一句话定位：**一个越用越好的智能体**。

三个通常独立的能力整合在了一个框架中：
1. **运行时技能学习**（Runtime Skill Learning）
2. **持久多层记忆**（Persistent Multi-layer Memory）
3. **可选的权重训练流水线**（Offline Weight Training）

在开源生态中，最接近的对比是 **OpenClaw**。两者都是持久化、消息友好的，但架构选择截然相反：

> 「Hermes 把一个学习智能体包在网关里。OpenClaw 把一个智能体包在消息网关里。」—— Kilo 博客

---

## 二、架构概览

![Hermes 智能体架构](../image/hermes-agent-masterclass-akshay-1.jpg)

一切通过一个单一的 `AIAgent` 类（`run_agent.py`）运行。CLI、消息网关、批处理、IDE 集成——都是同一个核心智能体的入口点。

核心循环是 **ReAct** 风格、同步执行的：
1. 构建系统提示词
2. 检查是否需要压缩
3. 发起可中断的 API 调用
4. 执行工具调用
5. 循环

几个关键设计细节：

- **6 种执行后端**：本地终端、Docker、SSH、Modal、Daytona、Singularity。切换只需改一行配置。
- **几乎所有模型兼容**：翻译层将任意提供商路由到三种 API 格式之一。从 Claude 切到 GPT 再到本地 Ollama，命令不变。
- **每任务 90 步硬上限**：防止智能体在循环中白白消耗额度。子智能体共享同一预算。

---

## 三、身份层（Before Memory）：SOUL.md

在记忆和技能之前，还有一个上层：**身份**。

> 记忆是智能体知道的。技能是它如何做的。但两者都不告诉它「来者何人」。

Hermes 通过一个文件解决：**`~/.hermes/SOUL.md`**。

- 位于系统提示词 slots[0]（排在所有内容之前）
- 定义人格、语气、沟通风格和硬边界
- **手动编写、静态不变**。写一次，跨项目跨会话保持一致
- 如果文件缺失，回退到内置默认身份

```markdown
# SOUL.md 示例
你是一个务实的高级工程师，品味出色。
你为真相、清晰和有用性而优化，
而不是礼貌性的表演。
```

SOUL.md 是固定框架，记忆和技能是其中的运动部件。

---

## 四、三层记忆系统

Hermes 没有单一的"记忆"，而是三个层次，各自有不同的用途：

### 第一层：两个小型 Markdown 文件

- **MEMORY.md**（最多 2,200 字符）：存放关于环境、项目约定、工具细节的经验总结
- **USER.md**（最多 1,375 字符）：存放用户画像——名字、沟通偏好、技能水平、需避免事项

两者在会话启动时作为「冻结快照」注入系统提示词。若智能体在会话中写入新记忆条目，会立即持久化到磁盘，但直到下次会话才会出现在系统提示词中。

当记忆占用达到约 80%（在系统提示词头部以百分比显示），智能体必须**合并**——将相关条目压缩为更密集、信息更丰富的形式。

### 第二层：全文会话搜索

每个对话（CLI 和消息）存储在 SQLite 中，带全文索引（FTS5）。智能体可以搜索数周前的对话记录。

权衡很清晰：第一层始终在上下文中但容量小；第二层容量无限但需要主动搜索加 LLM 摘要。

> 关键事实活在记忆里。其他信息按需搜索。

![三层记忆架构](../image/hermes-agent-masterclass-akshay-2.jpg)

### 第三层：外部记忆提供商（8 个插件）

Hermes 内置了 8 个可插拔的记忆提供商，与内置记忆并行运行（永不替换）。同一时间只能激活一个。

当任一外部提供商激活时，Hermes 会自动：
- 每轮对话前预取相关记忆
- 每次回复后同步对话轮次
- 会话结束时提取记忆

外部提供商对比：

![外部记忆提供商对比](../image/hermes-agent-masterclass-akshay-3.jpg)

---

## 五、自学进化技能（Self-Evolving Skills）

记忆处理事实（facts）。技能处理流程（procedures）。

**技能是以 YAML frontmatter 开头的 Markdown 文件**，作为智能体的「流程记忆」——不是它知道什么，而是它怎么做。

技能结构示例：

```yaml
---
name: k8s-pod-debug
description: >
  在 pod 崩溃、CrashLoopBackOff、容器故障时激活
version: 1.2.0
author: agent
platforms: [linux, macos]
---
## 流程
1. 获取 pod 状态 → 检查事件 → 拉取日志
2. 检查 OOMKilled、ImagePullBackOff、配置错误

## 常见陷阱
- 忘记在重启容器上使用 --previous 标志
```

为了控制 token 成本，技能使用**渐进式披露**：

- **Level 0**：智能体只看名称和描述（完整目录约 3k tokens）
- **Level 1**：需要时才加载完整技能内容
- **Level 2**：可深入到技能内的具体参考文件

![渐进式披露示意图](../image/hermes-agent-masterclass-akshay-4.jpg)

### 自学循环

这是核心差异化能力。智能体通过 `skill_manage` 工具**自主创建技能**。技能创建在以下情况下触发：

- 智能体完成复杂任务（5+ 次工具调用）
- 遇到错误并找到正确路径
- 用户纠正了它的方法
- 发现非平凡的工作流

循环：**遇到问题 → 试错解决 → 将成功方法保存为 SKILL.md → 下次遇到类似问题时直接加载。**

工具支持六个动作：`create`、`patch`（针对性修复，首选项）、`edit`（完全重写）、`delete`、`write_file`、`remove_file`。

### Curator（技能垃圾回收）

没有维护，智能体创建的技能会堆积——几十个狭窄、重叠的 playbook，浪费 token 并污染目录。

**Curator** 是一个后台维护系统，基于不活跃检测运行（非 cron 守护进程）：如果距上次运行已过 7 天且智能体空闲 2 小时以上，后台分支会启动，带自己的提示缓存，从不触及活跃对话。

运行分为两个阶段：
1. **自动转换（确定性，无 LLM）**：30 天未用 → stale；90 天未用 → archived
2. **LLM 评审**（最多 8 轮）：分支智能体调查所有技能，逐条决定 keep/patch/consolidate/archive

重要约束：
- 从不触及捆绑或从 Hub 安装的技能，只处理智能体自写的
- 从不自动删除。最坏情况是归档到 `.archive/`，一条命令即可恢复
- 每次 Curator 运行前对整个技能目录做 `tar.gz` 快照，回滚一条命令即可

---

## 六、GEPA：离线技能进化引擎

> GEPA（Genetic-Pareto Prompt Evolution）没有内置在 Hermes 运行时中。它位于独立的配套仓库（NousResearch/hermes-agent-self-evolution），作为离线优化流水线运行。已作为 ICLR 2026 Oral 论文发表，MIT 许可。

### 为什么需要 GEPA？

智能体的自学循环有一个已知弱点：**自我表扬倾向**——它几乎总觉得自己干得不错，即使其实不是。社区反馈已证实这点。同一个系统可以覆盖手动定制的内容。

### 核心思路

GEPA 不直接问智能体「你干得怎么样？」，而是读取**执行追踪（execution traces）**来理解为什么出问题，然后通过**进化搜索**提出针对性改进。

![GEPA 对比 GRPO](../image/hermes-agent-masterclass-akshay-5.jpg)

### 流水线步骤

1. 从 Hermes 仓库读取当前技能
2. 生成评估数据集（通过 Claude Opus 合成测试用例、真实会话历史、或人工策展的 golden set）
3. 运行 GEPA 优化器：读取执行追踪 → 理解失败点 → 生成候选变体
4. 使用 LLM-as-judge 评分（非二元的 pass/fail，而是带评分 rubrics 的连续评分）
5. 应用约束门：完整测试套件 100% 通过、技能不超 15KB、缓存兼容性不变、语义不漂移
6. 最佳变体以 **PR 形式**提交到 Hermes 仓库——从不直接 commit

> 不需要 GPU。全部通过 API 调用完成。每次优化运行成本约 **$2-10**。

GEPA 是在投入全量微调或 RL 微调之前的极佳替代方案。

---

## 七、上手实践

### 安装（一行命令）

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
source ~/.bashrc   # 或 ~/.zshrc
```

要求：Linux、macOS 或 WSL2。Python 3.11+。基于 API 的场景 8GB RAM 绰绰有余。

### 运行配置向导

```bash
hermes setup
```
会逐步引导配置提供商、API key、模型和工具。

### 连接 Telegram

从 @BotFather 获取 bot token，从 @userinfobot 获取 Telegram user ID，然后配置 gateway：

```bash
hermes gateway setup
```

### `~/.hermes/` 目录结构

```
~/.hermes/
├── config.yaml           # 主配置（模型、终端后端、工具、MCP 服务器）
├── .env                  # API key 和密码
├── auth.json             # OAuth 凭证
├── SOUL.md               # 智能体身份（系统提示词 slot[0]）
├── memories/
│   ├── MEMORY.md         # 持久化智能体事实
│   └── USER.md           # 用户画像
├── skills/               # 所有技能（内置、Hub、智能体自写）
│   ├── mlops/            # 按分类组织
│   └── .hub/             # Skills Hub 状态
├── sessions/             # 跨平台会话元数据
├── state.db              # SQLite 会话存储，FTS5 索引
├── cron/
│   ├── jobs.json         # 计划任务
│   └── output/           # 任务输出
├── plugins/              # 自定义插件
├── hooks/                # 生命周期钩子
├── skins/                # CLI 主题
└── logs/                 # agent.log, gateway.log, errors.log
```

### 安装新技能

Hermes 官方 Skills Hub 有 **687 个技能，18 个分类**：
- 87 个内置技能（随智能体自带）
- 79 个可选技能（按需启用）
- 16 个来自 Anthropic（前端设计、PDF、PPTX、DOCX、MCP 构建等）
- 505 个来自 LobeHub（更广泛的社区贡献）

也可以添加任意 GitHub 仓库作为自定义 tap：

```bash
hermes skills tap add yourname/your-skills-repo
hermes skills install yourname/your-skills-repo/<skill-name>
```

---

## 八、从 1 到 10 个智能体

Hermes 有名为 **profiles** 的一等公民功能。每个 profile 是完全隔离的 Hermes 实例，拥有独立的配置、记忆、技能、会话和 SOUL.md。

### 创建一个团队（程序员 + 设计师 + 研究员）

```bash
hermes profile create designer --clone
hermes profile create programmer --clone
hermes profile create researcher --clone
hermes profile list
```

`--clone` 会复制默认 profile 的配置和 .env 作为起点。

### 为每个 Profile 分配独立的 Telegram Bot

每个 profile 需要自己的 bot（从 BotFather 创建）。Telegram 只允许每个 token 一个连接。

```bash
hermes -p designer gateway setup
hermes -p programmer gateway setup
hermes -p researcher gateway setup
```

### 定制设计师：喂给它视觉风格

设计师通过示例学习你的风格，然后自主创建设计技能。发送参考图 + 以下提示词：

```markdown
仔细研究这些参考插图。注意配色、线条粗细、细节程度、构图和整体美学。

请创建一个名为 "my-design-style" 的新技能，记录这种风格的特征，
包含一个 Python 脚本，通过 OpenRouter 调用 Nano Banana 模型，
按照这个风格生成新图片。
```

智能体会研究参考图、写 SKILL.md、生成 Python 脚本并验证运行。

### 定制程序员：通过 Claude Code 执行

程序员更高效的做法是它将代码执行委托给 Claude Code CLI。Hermes 编排，Claude Code 执行。

激活提示词：

```
I already have a Claude Max subscription. You are my staff engineer who
helps me with my day-to-day coding tasks, and under the hood you use
Claude Code for all the executions. Set yourself up accordingly.
```

智能体会自动安装 `autonomous-ai-agents/claude-code` 技能，验证 `claude` 在 PATH 上，然后开始使用 Claude Code 进行代码操作。

### 定时任务（Cron）：用自然语言描述

研究员的 SOUL.md 说它负责每日 Telegram 摘要——这就是定时任务的用武之地。

Hermes 有内置调度器。Gateway 守护进程每 60 秒 tick 一次，在独立智能体会话中执行到期任务，并将输出发送到指定消息平台。任务在重启后保留。

给研究员的激活提示词：

```markdown
Every weekday at 8am India time, prepare a deep digest of what's new
in the AI and machine learning space over the last 24 hours. Cover
four streams: GitHub trending, big tech announcements, fresh papers,
and social pulse. Cite every claim with a URL. Keep under 800 words.
Deliver to Telegram.
```

验证：

```bash
hermes -p researcher cron list
```

其他常用 cron 模式：
- **一次性延迟**：`/cron add 30m "Remind me to check the build"`
- **重复间隔**：`/cron add "every 2h" "Check server status"`
- **标准 cron 表达式**：`/cron add "0 9 * * 1-5" "..."` 每周一至周五早上 9 点
- **技能绑定**：`/cron add "every 1h" "..." --skill blogwatcher`

---

## 九、总结

整个体系层层递进：

| 层次 | 功能 | 更新方式 |
|------|------|---------|
| **SOUL.md** | 身份层（人格、语气、硬边界） | 手动编写，静态不变 |
| **MEMORY.md / USER.md** | 持久化事实（环境、用户、约定） | 智能体自主维护，约 80% 容量时合并 |
| **SQLite 全文搜索** | 无限容量会话检索 | 按需搜索 + LLM 摘要 |
| **外部记忆提供商** | 深层持久记忆（8 种插件） | 自动预取、同步、提取 |
| **自写技能** | 流程记忆（工具调用、工作流） | ReAct 循环自动创建 + Curator 维护 |
| **GEPA** | 离线技能优化 | 读取执行追踪 → 进化搜索 → PR |

SOUL.md 设定身份。运行时循环捕获经验。Curator 保持技能库整洁。GEPA 确保库里的东西真的能用。

---

*Published on 2026-05-13 by Akshay 🚀 (@akshay_pachaar) | Processed and translated from [X/Twitter long-form article](https://x.com/akshay_pachaar/status/2054564519280804028)*
