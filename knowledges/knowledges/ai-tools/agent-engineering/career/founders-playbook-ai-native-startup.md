---
title: "创始人实战手册：构建 AI-Native 初创公司"
author: "Anthropic"
source: "https://cdn.prod.website-files.com/6889473510b50328dbb70ae6/69fe2a55b93bb0732b1fe33c_The-Founders-Playbook-05062026_v3%20(1).pdf"
date: 2026-05-17
tags:
  - startup
  - founder
  - ai-native
  - mvp
  - product-market-fit
  - go-to-market
  - scaling
  - claude
  - anthropic
  - agentic-coding
category: "startup"
description: "Anthropic 出品的 AI-Native 创业实战手册。覆盖 Idea → MVP → Launch → Scale 四阶段全生命周期，详解创始人如何在 AI 时代用更小团队、更快速度构建可持续公司。含每阶段的目标、退出标准、常见陷阱及 Claude 工具链（Chat/Cowork/Code）实战策略。"
---

# 创始人实战手册：构建 AI-Native 初创公司

> **来源：** Anthropic *The Founder's Playbook: Building an AI-Native Startup*（2026 年 5 月版，36 页）
>
> **核心理念：** AI 已经消除了「会写代码的人」和「有好想法的人」之间的壁垒。2026 年的创始人不再是独立贡献者，而是 **AI Agents 的指挥者**。

---

## 一条主线：四个阶段的范式迁移

```
验证周期：  months → afternoons
原型构建：  需招工程师 → 几轮 prompt
发布就绪：  上线前手忙脚乱 → 持续工作流
运营规模：  被迫早期扩招 → AI 代管，人管判断
```

传统路径：`validate → raise → hire → build → raise → grow → hire more → repeat`

2026 路径：**好想法走得更远。Agentic Coding 把一整个工程团队压缩进一个创始人自己就能交付的工作量。**

---

## 第一章：2026 年的创业新现实

### 三个关键变化

| 变化 | 传统模式 | AI-Native 模式 |
|------|---------|--------------|
| **创始人画像** | 技术型 vs 非技术型壁垒分明 | 壁垒消失；领域专家无需代码也能做产品 |
| **团队规模** | 头部门槛 = 工程师团队 | 单人/极简团队，AI 替代 3 倍人手 |
| **增长节奏** | 每个阶段需要新融资、新招聘 | 同一团队持续压缩，直到规模才需扩人 |

### AI-Native 公司的三大能力支柱

| 支柱 | 类比 | 说明 |
|------|------|------|
| **Conversational Intelligence / Research** | 按需专家 | 市场研究、竞品分析、财务建模、投资人备忘录 |
| **Agentic Coding** | 永不阻塞的工程师 | 用自然语言描述需求，AI 生成、测试、调试、重构 |
| **Workflow Automation** | 按需运营团队 | CRM 自动更新、周报自动生成、文档自动同步 |

---

## 第二章：创始人的角色变迁

### 从 IC 到 Orchestrator

**传统创始人：** 码代码 → 管人 → 处理日常运营

**AI-Native 创始人：** 生成想法 → 指挥 AI Agents → 做只有创始人能做的判断

> 最革命性的变化：**释放非技术背景的领域专家。** 当创始人的池子扩大到工程背景之外，你得到的是有完全不一样人生经验的人，解决传统科技创始人 pipeline 从未重视过的问题。

### 什么时候用什么工具

| 任务类型 | 用 | 原因 |
|---------|-----|------|
| 快速问答、改写、脑暴 | **Claude Chat** | 快速对话，无需设置 |
| 研究分析、生成文档/报告 | **Claude Cowork** | 访问文件夹、连接器、技能、定时任务 |
| 写代码、测试、发布软件 | **Claude Code** | 代码库访问、diff、git、开发环境 |

> 三个工具共用同一个 Claude 底层，区别在于围绕它的工作空间。

---

## 第三章：Idea Stage（创意阶段）

### 核心问题

```
Is this problem real, specific, and frequent enough?
→ Who exactly has it, and is that a market?
→ Is anyone else solving it, and if so, how and how well?
→ What would a solution actually need to do?
→ IS THIS WORTH BUILDING?
```

> "People struggle with expense reporting" 是一个观察。
> "Finance managers at mid-market companies spend 4+ hours/week reconciling submissions because their current tools don't integrate with their accounting software" 是一个可验证的假设。

### 退出标准：找到 Problem-Solution Fit

必须全部满足：

1. **问题是真实且具体的吗？** 能说出谁有这个问题、频率多高、影响多严重、他们现在怎么解决
2. **你的方案真的能解决那个问题？** 不是你以为的问题，而是验证过程揭示的问题
3. **有足够信号 justify 开建吗？** 永远不会有 certainty，但需要足够定性证据

### 三大陷阱

| 陷阱 | 描述 | 解药 |
|------|------|------|
| **把 Build 当 Validate** | 42% 的创业失败是因为造了没人要的东西。AI 让这更容易了——有原型 ≠ 有验证 | 原型只是对话道具，真正的证据来自用户对话 |
| **过早 Scale** | AI 让执行跑得远超过商业需求。AI 对你差劲的想法和好的一样热情 | 保持「sense-making > building」，尤其是在构建如此轻松的时候 |
| **丧失客观性** | 确认偏误有了搜索引擎。问 AI 支持你，它就找支持你的证据 | 让 AI 当反方，压力测试自己的想法 |

### Claude 在 Idea Stage 的实战策略

#### 1. 定义并压力测试问题假设

与 Claude 一起打磨你的问题陈述，直到它可测试。

> **示例：** "合同审查太慢" 不是可测试的。
> "中型公司法务团队每份合同平均花 3 天以上，因为修订意见分散在邮件线程而非版本管理系统" —— 非常可测试。

**练习：** 让 Claude 做结构化魔鬼代言人。

#### 2. 市场研究与竞品地图

| 任务 | 方法 |
|------|------|
| **竞品映射** | 按层级分：直接竞品、间接竞品、潜在收购方、能进入你领域的相邻玩家 |
| **客户反馈合成** | Claude Code 可抓取公开客户反馈，识别现有方案未解决的问题 |
| **市场建模** | TAM/SAM/SOM 建模，压力测试假设 |
| **趋势分析** | 识别监管、技术、人口趋势，判断是推力还是阻力 |

#### 3. 客户发现全流程

| 步骤 | Claude 如何帮助 |
|------|----------------|
| **谁该聊** | 精确目标画像（职位、公司类型、团队结构、层级） |
| **问什么** | 设计问题框架，避免引导性问题、未来指向性问题、过于宽泛的问题 |
| **访谈后分析** | 输入笔记，识别：什么确认了假设、什么挑战了假设、什么让你意外 |
| **批量合成** | 每 5 次访谈后，生成「支持假设」和「挑战假设」两个清单 |
| **自动化运营** | Claude Cowork 建联系人清单、写个性化邮件、排日程、维护追踪表 |

#### 4. 设计最终方案

向 Claude 展示方案后，让 Claude 识别三个最重要的依赖假设。每个假设为真需要什么条件？如果任何一个不成立，后果如何？

#### 5. 用 Claude Code 构建轻量原型

> **关键：** 只构建一个核心交互——你的方案依赖的那个最关键操作。放到 5 个目标用户面前。他们的反应决定你继续 build 还是回到画板。

---

## 第四章：MVP Stage（最小可行产品阶段）

### 理念转变

> **Idea Stage 的问题：**"这值得造吗？"
> **MVP Stage 的问题：**"我们到底该先造什么？"
> **AI 的角色转换：** 从研究伙伴 → 施工队

### MVP 阶段的三个目标

1. **把验证过的问题翻译成能工作的产品**，让真实用户用
2. **快速移动但不积累会复利的** 技术债
3. **从第一天起建立持久上下文**——Claude Code 每 session 都需要的项目记忆

### 退出标准：产品-市场契合（Product-Market Fit）

证明一个特定的、可识别的用户群足够重视你的产品：
- **留存（Retention）** → 他们会回来
- **营收（Revenue）** → 他们愿意付钱
- **推荐（Referral）** → 他们会告诉别人

### 四大陷阱

| 陷阱 | 描述 | 解药 |
|------|------|------|
| **Agentic 技术债** | AI 每 session 重推基础决策，决策漂移导致无脑模型 | 写 CLAUDE.md + 架构文档 |
| **虚假 PMF** | 早期 momentum ≠ PMF。Launch energy 来自朋友/投资者/HN 排行榜 | 设定留存基准和激活条件 |
| **零摩擦 Scope Creep** | 加一个功能只花一个下午，而每个都看起来必要 | 写 scope 文档 + 功能准入标准 |
| **不安全的代码** | Agentic coding 生成能跑的代码，但不是安全的代码 | 安全审查在用户触碰之前 |

### Claude 在 MVP Stage 的实战策略

#### 1. 先定义架构再 Build

打开 Claude 而非 Claude Code，先定义：
- 架构原则（architectural principles）
- 要避免的依赖
- 当前阶段主动接受的 tradeoffs

> **输出：** `CLAUDE.md` — 项目级指令文件，Claude Code 自动读取。

**每次 session 模板：**
```
1. 回顾 scope 文档
2. 提供 CLAUDE.md 架构上下文
3. 指定本 session 的具体任务和约束
4. 结束时更新 CLAUDE.md：建了什么、做了什么决定、引入了什么假设
（每个 session 5 分钟文档  = 防止架构漂移 的廉价保险）
```

#### 2. 定义并守护 MVP Scope

Scope 文档必须包含：
- 产品做什么
- 产品故意不做什么
- 功能准入标准：什么证据 justify 加新功能

当新功能想法出现时，用 Claude 压力测试：这是用户真实信号，还是创始人的热情伪装成产品思考？

#### 3. 安全审查

在部署到任何真实用户之前，必须做：
- 认证与会话管理
- API 响应中的数据暴露
- 输入验证和注入风险
- 已知漏洞的依赖

> Claude Code Security 可扫描代码库并建议补丁（发布时处于 limited beta）。

#### 4. 在上线前建立度量框架

设定**上线前**的基准：
- 留存基准
- 激活条件
- Day 7 / Day 30 目标
- 定义什么是"假阳性"：没有激活的注册、没有留存的营收、没有重复使用的热情

#### 5. 用户反馈循环

| 工具 | 职能 |
|------|------|
| Claude Cowork | 建联系人列表、发邮件、排反馈会议、写周度综合报告 |
| 人类创始人 | 解释反馈：这是核心需求还是 nice-to-have？代表一个 segment 还是特定客户？ |

#### 6. PMF 的基本检测

| 测试 | 说明 |
|------|------|
| **Sean Ellis Test** | "如果不能再用这个产品，你会多失望？" >40% 选"非常失望" = 强 PMF 信号 |
| **Effort Test** | Pre-PMF 需要持续人工推动；Post-PMF 产品自己拉回用户 |

#### 7. 当需要 Pivot 时

已完成 ≥3 轮迭代但 PMF 指标未见改善？用 Claude 诊断：

1. 数据中是否存在某个 segment 表现不同？
2. 设计价值和体验价值之间的差距是定位问题还是产品问题？
3. 当前产品找到真正 PMF 需要什么条件，现实吗？

---

## 第五章：Launch Stage（发布阶段）

### 理念转变

> **MVP Stage：** 证明你的产品值得存在
> **Launch Stage：** 证明你的公司值得增长

### 三个目标

1. **把早期 traction 变成可复制的增长引擎**
2. **硬化工底层基础设施**
3. **建立运营系统来释放创始人的注意力**

### 退出标准

| 条件 | 说明 |
|------|------|
| **增长可复制、渠道驱动** | CAC、LTV、payback period 都能说出数字 |
| **产品能承受生产负载** | 基础设施已硬化，安全合规就绪 |
| **运营不依赖创始人** | 支持、排期、报告都有流程，不再需要创始人亲自处理 |

### 三大陷阱

| 陷阱 | 描述 | 解药 |
|------|------|------|
| **技术债到期** | MVP 代码跑够了，生产流量暴露了所有 shortcuts | 系统架构审计 + 定向重构 + 测试覆盖扩展 |
| **创始人成瓶颈** | 创始人什么都要亲自过目 | 审计创始人注意力去向 → 自动化/委派/保留 |
| **安全和合规不再可推迟** | 真实数据 + 企业合同下的暴露风险 | 系统性安全审查在产品规模到来前做 |
| **过早扩张** | 新市场看起来是机会，但和你的早期受众本质不同 | 专注原用户群，不分散精力 |

### Claude 在 Launch Stage 的实战策略

#### 1. 修复技术债

1. Claude Code 跑全架构审计：脆弱点、测试覆盖缺口、重构候选
2. 喂给 Claude 做优先级排期：什么必须在下个版本前修、什么可以等
3. 把 MVP 阶段的架构决策写进 CLAUDE.md

#### 2. 系统化替代创始人注意力

用 Claude Cowork 做运营负载审计：
- 每项重复性任务
- 每个落在你桌面的决策
- 每个只有你记得做的流程

分类：可完全自动化 → 需要人但不需要你 → 必须由创始人决定

#### 3. 安全和合规作为产品工作流

- Claude Code：面向 SOC 2/GDPR/HIPAA 扫描代码级问题
- Claude：排优先级 + 设计控制措施
- 把合规构建到开发周期中，而非一次性项目

> AI 扫描是辅助，不能替代专业合规审查。

#### 4. 建立产品管理流程

用 Claude 设计：
- Sprint cadence
- 最小 spec 模板
- Bug 分类决策树
- 每周指标简报

然后用 Claude Cowork **执行**运营层：排期、路由、编译、分发。

---

## 第六章：Scale Stage（规模阶段）

### 理念转变

> **Launch Stage：** 你仍然在 builder mode
> **Scale Stage：** 创始人的角色变成面向公众的高管——产品仍是核心，但你的日常越来越关乎公司本身

### 三个目标

1. **建立系统化增长**，靠成熟的组织运营维系
2. **通过积累的深度构建防御性 moat**：领域知识、集成深度、专有数据
3. **产品和组织都能经得起外部 scrutiny**：投资人、分析师、监管、企业采购

### 退出标准

公司可持续发展，即使创始人不再直接管理日常运营：

| 形式 | 条件 |
|------|------|
| **可持续盈利** | 规模不再依赖外部资本 |
| **IPO-ready** | 组织成熟，治理合规 |
| **被收购** | 产品和 moat 经得起核查 |

通用前提：增长可系统化、产品 moat 经得起质疑、组织运营成熟

### 四大挑战

| 挑战 | 描述 |
|------|------|
| **委派运营层** | 从做工作 → 设计系统。创始人的心理挑战 |
| **扩展技术运营** | 客户不只看产品，还要看 org 是否能当可靠的基础设施伙伴 |
| **扩展组织功能** | 财务、合规、合同管理、客户支持 |
| **建立 GTM 职能** | 有机增长有天花板。创始人力推的 pipeline 到顶了 |

### Claude 在 Scale Stage 的实战策略

#### 1. 将日常任务移交给 Claude Cowork

用 Claude 生产「**瓶颈地图**」：每一条当前需你经手的流程/决策/审批。
然后问：**当你一周不可用，每条流程会怎样？** 僵住的就是需要交接的。

#### 2. 扩展到企业级基础设施

| 领域 | Claude 工具 |
|------|-------------|
| 产品文档、支持手册、SLA 草稿 | Claude |
| 代码级可靠性+安全审计 | Claude Code |
| 日志/监控/事故响应/可观测性 | Claude Code |
| 工单路由、escalation、更新追踪 | Claude Cowork |

**练习：** 选 3 个理想客户，让 Claude 产出 gap analysis：一个企业采购团队在签多年合同前期望看到什么文档/SLA/支持设施？你现在差什么？

#### 3. 建立 GTM 职能

三个工具的协同：

| 阶段 | 工具 | 产出 |
|------|------|------|
| GTM 战略 | Claude | 市场细分、信息架构、分析师关系策略、销售手册 |
| GTM 执行 | Claude Cowork | 内容管线、外呼序列、CRM 卫生、Pipeline 报告 |
| GTM 基础设施 | Claude Code | 互动 demo 环境、集成文档、API 参考、技术 one-pager |

#### 4. 将领域知识转化为 AI 上下文

**核心策略：** 把你的行业知识外化到 Claude，形成任何通用 AI 无法复制的专有知识基底。

| 步骤 | 方法 |
|------|------|
| **Capture** | 通过对话、Projects、Memory，把你懂的所有行业知识输入 Claude |
| **Codify** | Skills 将重复性工作流编码为可复用流程 |
| **Embed** | Claude Code 把领域 edge case 变成验证逻辑、prompt 优化、MCP 集成 |

> **练习：** 识别一个通用竞品肯定会搞错的垂直领域 edge case。用 Claude Code 构建一个专用测试用例。每次遇到类似的 edge case 就加进去。你的测试套件就成了你的 moat 地图。

#### 5. 将用户数据积累为竞争壁垒

**数据飞轮：** 每次改进让产品更有用 → 驱动更多使用 → 产生更多反馈 → 驱动更多改进

这个数据是时间锁定、上下文特定、竞品无法复制的。

**练习：** 让 Claude 分析用户交互数据，识别 3 个最高信号的用户行为模式，设计把每个模式转化为系统性模型改进的反馈回路。然后起草一页 moat narrative：你的数据飞轮如何运作、跑了多久、为什么一个有资源的竞品现在开始也追不上。

#### 6. 创建 Workflow Lock-in

用户在你的产品上构建的 workflows → integration depth → switching cost

| 层次 | 描述 |
|------|------|
| 使用 | 用户用你的产品 |
| 集成 | 用户连接了它的数据和工具 |
| 构建 | 用户在之上建了 automations、API、SDK |
| 深度集成 | 团队流程被不可逆地嵌入 |

**练习：** 对 top 10 客户做 workflow integration audit。每个客户的 automation、依赖、团队流程、切换成本。找出什么类型的集成对你的特定产品创造了最深的 lock-in。

---

## 第七章：Same Job, New Rules

> **创始人的工作没变：** 找到一个真问题，造一个能解决它的东西，把它扩展成一个有价值的公司。
>
> **变了的是到达那里的路径。** AI 把四个阶段的时间从季度压缩成周。

**验证周期：** 原来几个月 → 现在一个下午
**原型构建：** 原来要技术联合创始人 → 现在几轮 prompt
**发布就绪：** 从上线前的手忙脚乱 → 持续工作流
**规模运营：** 从被迫早招人 → AI 代管

> **瓶颈不再是你能建造什么，而是你选择建造什么。**

---

## 资源汇总

### 官方文档与教程

| 资源 | 链接 |
|------|------|
| Building AI Agents for Startups | claude.ai |
| Claude Code 文档 | claude.ai |
| CLAUDE.md 使用指南 | claude.ai |
| Claude Cowork 入门 | claude.ai |
| 教程汇总 | claude.com/resources/tutorials |

### 真实的 AI-Native Startup 案例

| 公司 | 领域 | 关键数字 |
|------|------|---------|
| **HumanLayer / Ambral / Vulcan Tech** | YC cohort S25 | Claude Code 快速原型 → 市场 |
| **GC AI** | 法律科技 | Claude-powered 法律平台，公司专属手册 |
| **Carta Healthcare** | 医疗 | 22,000 手术案例/年，数据抽象时间减 **66%** |
| **Anything** | 无代码产品 | 150 万用户，AI 代理处理全栈构建 |
| **Cogent** | 企业安全 | Claude 作为安全 Agents 的推理层 |
| **Airtree** | 运营 | Claude Cowork 整合 12+ 分散工具 |
| **Duvo** | 采购/供应链 | 完全基于 Claude + Agent SDK |
| **Zingage** | 家庭护理 | 24/7 自动运营，Claude 结构化 tool calling |
| **Kindora** | 慈善匹配 | 非营利高管用 Claude Sonnet 自建匹配平台 |
| **Wordsmith** | 法律科技 | 律师出身的 CTO，Claude 做合同审查引擎 |

### 创业支持

| 项目 | 内容 |
|------|------|
| **Anthropic Startups Program** | 免费 API 额度、最高 rate limits、专属活动 |
| **Claude Community** | 论坛 + 社区活动 |
| **Live Learning** | 会议、网络研讨会、直播回放 |

---

## 核心框架总结

| 阶段 | 核心问题 | Claude 主力工具 | 退出标准 |
|------|---------|---------------|---------|
| **Idea** | 这值不值得造？ | Chat + Cowork | Problem-Solution Fit |
| **MVP** | 该先造什么？ | Code + Cowork | Product-Market Fit |
| **Launch** | 公司配不配增长？ | Code + Cowork + Chat | 增长可复制，运营不依赖创始人 |
| **Scale** | 这值不值得持续做？ | Cowork + Code + Chat | 可持续盈利 / IPO-ready / 可收购 |

---

*来源：* [The Founder's Playbook: Building an AI-Native Startup](https://cdn.prod.website-files.com/6889473510b50328dbb70ae6/69fe2a55b93bb0732b1fe33c_The-Founders-Playbook-05062026_v3%20(1).pdf) — Anthropic（2026）
*整理于 2026-05-17*
