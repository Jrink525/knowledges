---
title: "AI Agent 是如何记住东西？从原理到实战详细解释"
date: 2026-05-14
category: "ai-tools"
tags:
  - AI-Agent
  - memory-system
  - LLM
  - RAG
  - context-engineering
  - episodic-memory
  - semantic-memory
  - procedural-memory
source:
  - title: "AI Agent 是如何记住东西？从原理到实战详细解释"
    url: "https://x.com/lxfater/status/2054396603197505745"
    author: "铁锤人 (@lxfater)"
  - title: "Context Engineering, Sessions and Memory"
    author: "Google"
    url: "https://storage.googleapis.com/gweb-research2023-media/pubtools/12041.pdf"
---

# AI Agent 是如何记住东西？从原理到实战详细解释

> **来源：** [铁锤人 (@lxfater)](https://x.com/lxfater) 的 X 长文，411 赞，120 转发
>
> **摘要：** 本文从零开始拆解 AI Agent 记忆系统的底层原理，包含：基础会话记忆机制、认知科学三分类框架（情景/语义/程序性记忆）、OpenClaw 记忆系统深度拆解、企业级方案（EverOS）架构分析，以及 Skill 自进化、生产落地案例等实战内容。

---

## 关于 Agent 记忆系统的一些基础知识

首先，大模型在两次 API 调用之间是没有记忆的。

举个例子：你在第一次调用中说"我喜欢吃橘子"，第二次调用中假如你没有把"我喜欢吃橘子"附加到 prompt，那么大模型对"你喜欢吃橘子"是没有记忆的。

那么 Agent 是如何在对话中保持记忆的呢？

每次你提问时，底层会把之前的聊天历史都发送出去，大模型能看到最近的记忆。但当聊天记录超过大模型上下文窗口最大值时，系统会**压缩聊天记录**——把当前会话的历史总结提炼一下，再塞回 prompt，腾出空间继续聊天。

以上就是模型在**单个冗长对话**中保持记忆的原理。

而在**不同会话之间**保持记忆，则需要长期的记忆系统登场。它做的事就是：在上下文被压缩时，或主动要求记忆时，把重要信息存到某个存储空间；在开启新对话时，在适当时机提取并注入 prompt。通过"腾笼换鸟"，构建出记住很多事情的假象。

---

## 理解框架：记忆系统的两面

Google 在 2025 年 11 月发表了一篇论文《Context Engineering, Sessions and Memory》，其中把 Agent 记忆分为三类（效仿认知科学的方法）：

| 记忆类型 | 定义 | 例子 |
|---------|------|------|
| **情景记忆 (Episodic)** | 昨天发生了什么、上次跟你聊了什么 | 按时间顺序的事件记录 |
| **语义记忆 (Semantic)** | 你叫什么、喜欢什么、是什么身份 | 稳定的事实性知识 |
| **程序性记忆 (Procedural)** | 怎么完成一件事、流程是什么 | 执行步骤、任务模板 |

要搞懂一个记忆系统，只需搞懂两个方面：

### 1. 记忆分类

- 记忆有多少种分类？
- 每种存什么样的信息？

### 2. 抽取、更新、检索

- **抽取：** 如何从对话历史中提取出重要的信息
- **更新：** 如何对记忆进行整理合并（例如用户先在大理后搬到成都，记忆应该只存最新状态）
- **检索：** 通过什么方式找到记忆（关键词、语义向量、混合检索、LLM Agentic 检索）

---

## OpenClaw 记忆系统拆解

### 记忆分类

OpenClaw 的记忆分为三类：

1. **memory.md（记忆）** → 语义记忆
   - 存储身份、偏好、稳定事实
2. **daily logs（每日日志）** → 情景记忆
   - 记录每天发生了啥，按天组织，只追加不删除
3. **session snapshots（会话快照）** → 情景记忆
   - 当用 `/new` 或 `/reset` 开启新会话时，总结最后 15 条"有意义的"消息，保存为 markdown 文件

### 抽取、更新、检索

**抽取发生在三种情况下：**
1. 对话即将被压缩时 → 将有价值的信息写入每日日志
2. 用 `/new` 或 `/reset` 开启新会话 → 保存到会话快照
3. 用户要求记忆时 → 自行判断存储在任意一种记忆中

**检索发生在两种情况：**
1. 开启新对话时 → `memory.md` 自动注入 prompt，还会读取今天和昨天的每日日志
2. OpenClaw 觉得有必要看记忆时 → 调用 `memory search`，通过融合搜索（关键词+向量）找到记忆所在位置，再通过 `memory get` 读取文件

**更新：** 发生在抽取时，即决定记忆什么的时候。

### 不足

OpenClaw 记忆系统存在一些问题：
- 很费 Token
- Markdown 坏了记忆就丢失
- 经常遗忘东西

---

## 企业级 Agent 记忆系统：EverOS 深度拆解

> 企业级方案在稳定性、精细度和自进化能力上做了大量优化。

### 第一问：记忆怎么分类？

EverOS 基于通用的 3 类框架，每一类下又细分：

#### 1. 语义记忆（Semantic Memory）

| 子类 | 说明 | 示例 |
|------|------|------|
| **稳定特质** | 长期不变的用户画像 | 你是夜猫子、是程序员、住北京 |
| **临时状态** | 短期变化的状态 | 你今天熬了夜、这周特别忙 |

#### 2. 情景记忆（Episodic Memory）

| 子类 | 说明 | 示例 |
|------|------|------|
| **Episode（剧情记忆）** | 一段对话或任务的浓缩概要 | 用户问怎么部署模型，卡在环境变量，折腾了 30 分钟 |
| **EventLog（事件日志）** | 关键事实 + 时间戳 | 2026-05-10 用户买了 Mac mini，2026-05-12 用户绑了 GitHub |
| **Foresight（未来记）** | 跟时间有关的"接下来" | 下周五前把方案发出来，到点能提醒 |

#### 3. 程序性记忆（Procedural Memory）

| 子类 | 说明 | 示例 |
|------|------|------|
| **Agent Case（任务档案）** | 单次任务的"想干什么 + 怎么做 + 质量分" | 发邮件：查通讯录、起草、让你确认、发出去 |
| **Agent Skill（蒸馏技能）** | 多次同类任务后蒸馏出的通用打法 + 成熟度分 | 做过 5 次邮件任务后，学会先看收件人级别再决定语气 |

原本 3 类拆成 6 种，能装的信息更精细，与人类记忆更相似——会预测未来、会总结精进技能。

### 第二问：抽取、更新、检索怎么做？

**抽取：** EverOS 自动判断"这一段讲完了没有"，讲完就切下来打包成一个记忆单元。每个单元装 4 样东西：
1. **剧情（概要）**
2. **关键事实**
3. **未来记**（待办 + 推断 + 有效期）
4. **上下文标签**（时间、地点、可信度、情绪）

**更新（语义巩固 Semantic Consolidation）：**

举个例子：用户先说你"最近准备健身"，两周后说"最近忙没去健身房"，今天说"算了不健身了"。

- 普通方案：三条都堆进日志，大模型检出来哪条就认哪条
- EverOS 方案：自动判断哪条是最新的，重复的合并，稳定偏好和临时状态分开存（Profile Evolution）

**检索：** 给 4 种检索方式：

| 方式 | 说明 | 适用场景 |
|------|------|---------|
| 关键词 | 精确匹配 | 查具体名字、ID |
| 向量搜索 | 语义匹配 | 不同说法找同一含义 |
| 混合 + 重排 | 关键词+向量+rerank | 官方推荐默认档 |
| Agentic | LLM 自行判断怎么搜索 | 复杂多部分问题 |

但更重要的是检索逻辑：不是被动匹配，而是**主动重建上下文**——先分析这次想干什么 → 激活相关主题场景 → 过滤过期信息 → 迭代搜索直到信息够用。

EverOS 在长程记忆评测 **LoCoMo** 上拿到 **93.05%** 的总体准确率（GPT-4.1-mini），超过 Zep 的 85.22%。

---

## 实际生产落地

### 免费 API

EverOS 的 Cloud API 免费开放：

```bash
# 1. 浏览器打开 everos.evermind.ai 注册
# 2. 安装 SDK
pip install everos
# 3. 实例化 client 开始使用
```

### Skill 自进化

Agent 反复做同类任务时，EverOS 自动把经验蒸馏成可复用的 skill。

三个核心 API：
```python
# 1. 记录轨迹 → 生成 case（单次任务存档）
# 2. 多次同类任务后自动聚类 → 蒸馏出 skill
# 3. 下次任务直接用 skill，不用从零开始
```

注意：必须用 `/memories/agent` 端点，普通 `/memories` 抽不出 skill。

### 20 个真实 Use Case

特色案例精选：
- **MemoCare** — 阿尔茨海默记忆助手（公益项目）
- **Claude Code Plugin** — 给 Claude Code 装长期记忆，跨 session 不忘
- **Game of Thrones** — 给 AI 灌权游剧情演角色
- **OpenHer** — AI 女友，情感陪伴 + 记忆演化
- **Computer-Use with Memory** — 操控电脑，记住每次操作经验
- **Memory Graph Visualization** — 可视化记忆图谱

### 插件生态

| 插件 | 说明 |
|------|------|
| Claude Code Plugin | 每次回话自动存、每次提问自动召回，带 Memory Hub 面板 |
| OpenClaw Plugin | 作为记忆槽位，Agent 跑前自动检索上下文，跑完存回 |
| OpenClaw Skill | 以 skill 形式接记忆工具，按需调用 |

### 项目概况

- Apache 2.0 开源，4500+ stars
- 创始团队来自盛大旗下的 AI Native 公司 EverMind
- 学术和算法实力强，持续发论文（曾被选中 AAAI/NeurIPS）

---

## 附录：参考文献与推荐论文（10 篇）

> 以下论文从 HuggingFace Daily Papers、arXiv、ACL/EMNLP 等渠道精选，覆盖 Agent 记忆的综述、架构、检索、评估等方向。

### 1. 全面综述

#### [1] Memory in the Age of AI Agents

- **作者：** Yuyang Hu, Shichun Liu, Yanwei Yue 等（28 位作者）
- **来源：** arXiv: 2512.13564, Dec 2025
- **链接：** [https://arxiv.org/abs/2512.13564](https://arxiv.org/abs/2512.13564)
- **简介：** 目前最全面的 Agent 记忆综述，从**形式（Form）**、**功能（Function）**、**动态（Dynamics）** 三个统一维度构建分类体系，清晰区分了 Agent Memory 与 RAG、Context Engineering 的边界。HuggingFace Daily Paper #1。

#### [2] Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging Frontiers

- **作者：** Eric Du 等
- **来源：** arXiv: 2603.07670, Mar 2026
- **链接：** [https://arxiv.org/abs/2603.07670](https://arxiv.org/abs/2603.07670)
- **简介：** 覆盖 2022–2026 年的结构化综述，提出 Write–Manage–Read 三阶段记忆循环和三轴分类（时间跨度 × 表征载体 × 控制策略）。深入分析五大机制家族：上下文压缩、检索增强、反思自我改进、层次虚拟上下文、策略学习管理。

### 2. 基础理论与框架

#### [3] Position: Episodic Memory is the Missing Piece for Long-Term LLM Agents

- **作者：** Mathis Pink 等
- **来源：** arXiv: 2502.06975, Feb 2025
- **链接：** [https://arxiv.org/abs/2502.06975](https://arxiv.org/abs/2502.06975)
- **简介：** 主张情景记忆是长期 LLM Agent 缺失的关键拼图。提出情景记忆的**五大核心属性**（单样本学习、实例特定语境、时间索引、自动编码、重构回忆），并给出融合这些属性的研究路线图。本文的"情景/语义/程序性"三分类正是源自这一脉认知科学方法论。

#### [4] A-MEM: Agentic Memory for LLM Agents

- **作者：** Wujiang Xu 等
- **来源：** arXiv: 2502.12110, NeurIPS 2025
- **链接：** [https://arxiv.org/abs/2502.12110](https://arxiv.org/abs/2502.12110)
- **简介：** 基于 Zettelkasten 卡片盒笔记法的 Agent 记忆系统。新记忆写入时自动生成带结构化属性的笔记（上下文描述、关键词、标签），并与历史记忆建立链接网络。新记忆会触发已有记忆的上下文属性更新，实现记忆网络的**持续自精炼**。

#### [5] EM-LLM: Human-inspired Episodic Memory for Infinite Context LLMs

- **作者：** —
- **来源：** arXiv: 2407.09450, 2024 (OpenReview)
- **链接：** [https://arxiv.org/abs/2407.09450](https://arxiv.org/abs/2407.09450)
- **简介：** 受人类事件认知（Event Cognition）启发的架构。通过**贝叶斯惊奇检测（Bayesian Surprise）** 和图论边界精炼实时分割输入信息为连贯情节，两阶段检索（相似性 + 时间关系）来获取记忆。无需微调即可扩展到 **10M tokens**，在 ∞-Bench 和 LongBench 上超越 InfLLM 等 SOTA。

### 3. 检索与增强

#### [6] MemoRAG: Boosting Long Context Processing with Global Memory-Enhanced Retrieval Augmentation

- **作者：** Hongjin Qian 等
- **来源：** arXiv: 2409.05591, Sep 2024
- **链接：** [https://arxiv.org/abs/2409.05591](https://arxiv.org/abs/2409.05591)
- **简介：** 双系统架构：轻量长程系统创建全局长程上下文的**全局记忆（Global Memory）**，基于草稿答案为检索工具提供线索定位相关信息，再交给强大但昂贵的生成系统输出最终答案。突破传统 RAG 对显式查询和良好结构知识的依赖。

#### [7] Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection

- **作者：** Akari Asai 等
- **来源：** arXiv: 2310.11511, 2023
- **链接：** [https://arxiv.org/abs/2310.11511](https://arxiv.org/abs/2310.11511)
- **简介：** 训练单一 LM 包含检索决策与自我批判能力。通过反射 Token（Reflection Tokens）实现推理时的可控检索行为——按需检索、生成后反思、并基于检索结果调整输出。7B/13B 参数显著优于标准 RAG。

### 4. 系统与工程

#### [8] Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory

- **作者：** 等
- **来源：** arXiv: 2504.19413, Apr 2025
- **链接：** [https://arxiv.org/abs/2504.19413](https://arxiv.org/abs/2504.19413)
- **简介：** 生产级记忆体系架构，支持图结构记忆表示以捕捉会话元素间的复杂关系。在 LoCoMo 基准上与 6 大类基线对比（记忆增强系统、RAG 变体、全上下文、开源方案、专有模型、专用记忆平台）。**Mem0 在 LLM-as-a-Judge 指标上比 OpenAI 提升 26%**，p95 延迟降低 91%，Token 成本节约 90%+。

#### [9] MemoryOS: Memory Operating System for AI Agents

- **作者：** 等
- **来源：** EMNLP 2025 (ACL 2025.emnlp-main.1318)
- **链接：** [https://aclanthology.org/2025.emnlp-main.1318/](https://aclanthology.org/2025.emnlp-main.1318/)
- **简介：** 受操作系统内存管理启发的三层分级存储架构：**短期记忆 → 中期记忆 → 长期个人记忆**。短期到中期采用对话链 FIFO；中期到长期采用分段页面组织策略。LoCoMo 基准上平均提升 F1 48.36%、BLEU-1 46.18%。

### 5. 记忆与知识图谱

#### [10] AriGraph: Learning Knowledge Graph World Models with Episodic Memory for LLM Agents

- **作者：** 等
- **来源：** arXiv: 2407.04363, Jul 2024; IJCAI 2025
- **链接：** [https://arxiv.org/abs/2407.04363](https://arxiv.org/abs/2407.04363)
- **简介：** 构建融合语义记忆和情景记忆的**记忆图（Memory Graph）**，Agent 探索环境时边访问边更新图。增强规划与决策的复杂任务处理能力。在交互式文本游戏环境中显著超越其他记忆方法与强化学习基线（Ariadne Agent）。

---

*整理于 2026-05-14，来源：[@lxfater 的 X 长文](https://x.com/lxfater/status/2054396603197505745)*
