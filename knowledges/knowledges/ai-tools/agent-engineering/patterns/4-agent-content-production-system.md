---
title: "四 Agent 内容生产线 —— 从零到运行专业 Agent 团队的完整指南"
tags:
  - multi-agent
  - agent-architecture
  - content-production
  - orchestrator
  - quality-control
  - workflow
  - claude-code
  - agent-team
date: 2026-05-12
source: "https://x.com/cyrilxbt/status/2054037093785928157"
authors: "@cyrilxbt"
stats:
  likes: 464
  retweets: 74
---

# 四 Agent 内容生产线 —— 从零到运行专业 Agent 团队的完整指南

> **来源：** @cyrilxbt 的 X 长文  
> **核心理念：** 专业 Agent 团队永远优于单一通才。4 个角色的 Agent ≠ 4 倍复杂度，而是 4 倍产出。

---

## 核心原则

> 一个专家团队永远优于一个单打独斗的通才。

对 AI Agent 如此，对人类组织亦然。当你让一个 Claude 实例在同一会话中完成研究、写作、审校和发布，每一环节的输出都会平庸——上下文不断切换，质量标准相互冲突，模型同时优化太多目标。

四个专业 Agent，角色分明、交接清晰、有主编排器协调——每个 Agent 只做好一件事。

---

## 为什么是四个 Agent？

四个知识工作阶段：

```
信息摄入 & 研究  →  生产  →  质量控制  →  输出 & 发布
```

| | 单一通才 | 四 Agent 团队 |
|--|---------|-------------|
| **质量** | 不一致——上下文切换导致 | 一致——每个 Agent 一个任务 |
| **速度** | 顺序执行，慢 | 可并行，快 4 倍 |
| **调试** | 问题混在一起难定位 | 故障隔离到单个 Agent |
| **扩展** | 加人=加混乱 | 加 Agent=加吞吐量 |

> 每周 20 篇内容的情景下，仅并行化本身的收益就足以证明四 Agent 架构的价值。

---

## 完整架构

### Agent 角色总览

| 角色 | 职责 | 输入 | 输出 | 永不做什么 |
|------|------|------|------|-----------|
| **Agent 1: Research** | 信息收集与综合 | 主题/问题/简报 | 结构化研究简报 | 写作、编辑、发布 |
| **Agent 2: Production** | 将研究简报转为成品内容 | 研究简报 | 完整初稿 | 研究、编辑、发布 |
| **Agent 3: Quality** | 评估与改进产出 | 初稿 | 批准草稿或修改说明 | 研究、从零写、发布 |
| **Agent 4: Distribution** | 格式化与部署 | 已批准内容 | 平台就绪格式 | 研究、写作、评审 |
| **Orchestrator** | 任务路由、流程管理、故障处理 | 初始任务 | 完成的交付件 | 绕过 Quality、自己批准 |

### 文件夹结构

```
multi-agent-system/
├── inbox/                 # 任务入口
├── research-briefs/       # Research Agent 产出
├── drafts/                # Production Agent 产出
├── approved-content/      # Quality Agent 批准
├── distribution/          # 发布记录
├── logs/                  # 操作日志
│   └── operations.md
└── 05-system/
    └── agents/
        ├── research-agent.md
        ├── production-agent.md
        ├── quality-agent.md
        └── distribution-agent.md
```

---

## 搭建环境

### 安装 Claude Code

```bash
npm install -g @anthropic-ai/claude-code
claude    # 按引导完成认证
claude --version    # 验证
```

### 创建主 CLAUDE.md

```markdown
# Multi-Agent System — CLAUDE.md

## System Overview
4-Agent 内容生产系统。每个 Agent 一个角色，不得越界。

## Agent Roster
- Research Agent: 从主题生成结构化研究简报
- Production Agent: 从研究简报生成初稿
- Quality Agent: 评估并批准或退回草稿
- Distribution Agent: 格式化并部署已批准内容

## Folder Structure
inbox/ — 传入任务文件
research-briefs/ — 研究产出
drafts/ — 生产产出
approved-content/ — 质量批准
distribution/ — 发布记录
logs/ — 操作日志

## Shared Standards
- 产出文件命名: YYYY-MM-DD-[type]-[topic].md
- 每个 Agent 必须记录操作到 logs/operations.md
- 每个 Agent 开始任务前必须读 CLAUDE.md
- 无 Agent 可采取定义角色之外的操作

## Hard Rules
- 永不删除文件。归档到带时间戳的备份目录
- 无 Quality Agent 批准不发布
- 操作前记录，非操作后
- 不确定时：停止并标记人工审查
```

---

## Agent 1：Research Agent（最关键）

下游的一切质量取决于研究简报的质量。Production Agent 无法添加 Research Agent 没找到的洞见。

### 系统提示词

```
## Identity
你是一个专业研究 Agent。唯一工作是产出 Research Brief。永不写作，永不评估。

## Research Process
1. 确定内容需要回答的核心问题
2. 从多个角度找到最相关信息
3. 对事实性声明交叉引用至少 3 个独立来源
4. 找到大部分人在此话题上忽略的洞见
5. 找到"反直觉"角度——创造真正兴趣的来源
6. 定位 3 个具体例子、数据或故事
7. 按潜力排序 3 个可能的内容角度

## Output Format
保存到: research-briefs/YYYY-MM-DD-research-[topic].md

CORE INSIGHT: [一句话——非显而易见的洞见]
TARGET AUDIENCE: [具体描述]
SUPPORTING EVIDENCE: [3 个具体例子与来源]
COUNTERINTUITIVE ANGLE: [大多数人错在哪]
KEY DATA: [2-3 个具体数据或引语]
CONTENT ANGLES: [3 个排序角度，一句话描述]
GAPS: [研究未能回答的问题]

## Quality Standard
如果核心洞见是大多数人已经知道的，失败。洞见必须真的非显而易见。
永不包含无法用特定来源支持的声明。
```

### 运行方式

**手动：**
```bash
claude "读 CLAUDE.md 和 research-agent.md。然后读 inbox/[TASK]。执行研究流程并产出简报。"
```

**通过 N8N / API：**
```json
{
  "model": "claude-opus-4-5",
  "max_tokens": 4096,
  "system": "[CLAUDE.md + research-agent.md 内容]",
  "messages": [{"role": "user", "content": "为该任务运行研究流程: [TASK]"}]
}
```

---

## Agent 2：Production Agent

将研究简报转化为成品内容。

### 最关键环节：提取你的 Voice Profile

在写 Production Agent 提示词之前，收集你最好的 10 篇内容，让 Claude 分析模式：

```markdown
分析以下 10 篇内容并提取：
1. 平均句长
2. 大写模式（你策略性地大写什么？）
3. 结构模式（如何开篇、展开、收尾？）
4. 词汇级别和特定词语选择
5. 你永不做什么（模糊词、填充短语等）
6. 如何处理段落过渡
7. CTA 风格
```

### 系统提示词框架

```
## Identity
专业内容生产 Agent。唯一工作是从研究简报产出初稿。不研究，不评估。

## Pre-Task Checklist
1. 读 CLAUDE.md 了解系统上下文和质量标准
2. 完全读完研究简报后再写任何东西
3. 从 CONTENT ANGLES 中确定最强角度

## Voice Profile
[插入你提取的语音画像]

## Output Header
在每个草稿顶部包含:
SOURCE BRIEF: [使用的研究简报文件名]
CONTENT ANGLE: [所选角度和理由]
WORD COUNT: [实际字数]
PRODUCTION DATE: [日期]

## Self-Check
- 每个句子都符合 Voice Profile 吗？
- 开头足够在滚动时吸引注意力吗？
- 每个主要观点至少有一个具体数据或例子？
- CTA 精确告诉读者下一步做什么？
```

---

## Agent 3：Quality Agent（最常被跳过的关键 Agent）

Quality Agent 是生产到发布之间的门。**没有它，好日子出好内容，坏日子出烂内容——没有地板。**

大多数多 Agent 系统跳过这个 Agent，然后奇怪为什么输出不一致。

### 五维评分规则

| 维度 | 评分 (1-10) | 含义 |
|------|------------|------|
| **VOICE MATCH** | 1-10 | 听起来完全符合配置的声音画像吗？ |
| **HOOK STRENGTH** | 1-10 | 第一行够强，阻止滑动吗？ |
| **INFORMATION DENSITY** | 1-10 | 每个句子都有存在的价值吗？ |
| **CTA CLARITY** | 1-10 | Call to action 具体且有说服力吗？ |
| **FORMAT COMPLIANCE** | 1-10 | 符合所有格式要求吗？ |

**通过门槛：** 五项全部 ≥ 8 分。任何一项低于 8 → 返回 Production Agent 附带精确修改说明。

### 系统提示词

```
## Approval Output
五项全 ≥ 8:
在文件顶部添加:
---
QUALITY APPROVED
Scores: Voice [X] | Hook [X] | Density [X] | CTA [X] | Format [X]
---
移至 approved-content/

## Revision Output
任何一项 < 8:
在 drafts/REVISION-[ORIGINAL-FILENAME].md 创建修改说明:
---
REVISION REQUIRED
Failed Criterion: [标准名] - Score: [分数]
Specific Issue: [精确问题]
Required Change: [确切修改要求]
Example of Correct Approach: [展示而非说教]
---

## Hard Rules
- 绝不在任何标准不满足时批准
- 绝不给出模糊反馈，如"让它更吸引人"
- 必须具体，否则 Production Agent 无法修复
```

---

## Agent 4：Distribution Agent

### 平台特定格式

| 平台 | 格式要求 |
|------|---------|
| **Twitter/X** | 每推 ≤ 280 字。长文用 Thread。短句。每推独立成章。 |
| **LinkedIn** | 专业调整。较长句子可接受。叙事结构有效。首行必须是独立 Hook。 |
| **Newsletter** | 完整格式含标题。HTML 兼容。清晰段落结构。明确主题行。 |

### 系统提示词

```
## Pre-Task Checklist
1. 确认 QUALITY APPROVED header 存在
2. 从文件 header 识别目标平台
3. 为每个目标平台读取格式指南

## Hard Rules
- 无 QUALITY APPROVED header 绝不分发
- 未经平台特定格式化绝不分发
- 每次部署必须在 distribution log 中记录
```

---

## Orchestrator（主编排器）

Orchestrator 不是第五个 Agent，而是连接四个 Agent 的路由逻辑。

### 最简单形式

一个 Claude 会话，知晓完整系统，在 Agent 之间路由任务。

### 工作流

```
Task → Research Agent → Production Agent → Quality Agent → Distribution Agent → ✅
                                    ↑                        |
                                    └── Revision Brief ──────┘
```

### 故障处理

| 场景 | 处理方式 |
|------|---------|
| Quality 拒绝 | 带修改说明返回 Production Agent |
| 研究缺口 | 在进入生产前请求额外研究 |
| 分发失败 | 记录失败，标记人工审查，不自动重试 |

### Hard Rules

- 任何情况下不跳过 Quality Agent
- 不批准自己的输出——每个 Agent 由下一个评估
- 不做创作决策——只做路由和管理

---

## 首次端到端运行

### 1. 创建任务文件

```markdown
# Task: [你的第一个主题]

## Content Type
[推文线程 / 文章 / Newsletter 章节]

## Target Platforms
[X / LinkedIn / Newsletter]

## Specific Requirements
[任何特定要求]

## Deadline
[截止时间]
```

### 2. 触发 Orchestrator

```bash
claude "读 CLAUDE.md。你是 Orchestrator。一则新任务到了 inbox/ 中。开始工作流，先路由到 Research Agent。"
```

### 3. 观察输出文件夹

```
research-briefs/    ← Research Agent 完成
drafts/             ← Production Agent 完成
approved-content/   ← Quality Agent 批准
distribution/       ← Distribution Agent 部署
logs/operations.md  ← 每一步都有记录
```

首次端到端运行约需 **15-30 分钟**，10 次后趋于自然，50 次后不可或缺。

---

## 30 天后的复利效应

4-Agent 系统不仅比单 Agent 产出更好——它每个月都在变得更好，因为每个 Agent 都在积累经验：

- **Research Agent** 学会你的受众对哪些来源反应最好
- **Production Agent** 学会哪个角度带来最高参与
- **Quality Agent** 学会对你特定声音，"好"和"好极了"之间的确切分界线
- **Distribution Agent** 学会你的内容在哪个平台表现最好

这一切的学习不需要你做任何事，除了每周运行系统和一次性地更新共享的 CLAUDE.md。

> 一个人运行 4-Agent 团队 = 四人团队的产出。  
> 更高一致性、更快速度、每个作品都比上一个更好的反馈循环。

---

## 与知识库其他文章的关联

- **[Agent Complexity Ratchet](../agent-engineering/agent-complexity-ratchet.md)** — Garry Tan 的"一周 14 个合并请求"本质上是一个经过无数轮优化的个人多 Agent 系统。本文提供了从零搭建的起步模板。
- **[10 Claude Code Agents Pipeline](../agent-engineering/10-claude-code-agents-pipeline.md)** — @zodchiii 的 10 个 Agent 是本文架构的扩展版（更多角色、并行 Pipeline）。本文的 4-Agent 是"最小可行团队"，10-Agent 是"完整生产线"。
- **[Agent Harness Engineering](../agent-engineering/agent-harness-engineering.md)** — Addy Osmani 的 Agent Harness 理念（资源管理、治理层）与本文的 Orchestrator + Quality Agent 对应——Harness = Orchestrator + Quality + 错误处理。
- **[Claude 五个能力等级框架](claude-five-levels-framework.md)** — Nate Herk 的 L4 中提到的 Sub-agents + Verification Loop 是本文 Quality Agent 的对应概念。
- **[Skillify: Skill Engineering Guide](../agent-engineering/skillify-skill-engineering-guide.md)** — 本文每个 Agent 的 system prompt = 一个 Skill 文件。Skillify 教你如何编写这些 Skill 文件的结构和最佳实践。

### 可直接复制的核心洞见

| 洞见 | 应用 |
|------|------|
| Quality Agent 是被跳过最多的关键组件 | 在所有 Agent 系统中默认加入独立质量门 |
| Voice Profile = 你的 10 篇最佳内容的模式分析 | 内容系统的最强杠杆：分析 → 模板化 → 复用 |
| 文件夹结构 = Agent 之间的通信协议 | 用文件系统事件代替 API 调用，降低耦合 |
| 复利效应来自每个 Agent 持续积累上下文 | 加入"每周绩效观察"到 CLAUDE.md 的更新循环 |

---

*Processed on 2026-05-12 from X article by @cyrilxbt (464 likes, 74 retweets)*
