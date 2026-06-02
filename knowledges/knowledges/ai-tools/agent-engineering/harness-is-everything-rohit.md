---
title: "Harness 才是一切：Cursor、Claude Code、Perplexity 真正构建的东西"
tags:
  - harness-engineering
  - agent-architecture
  - SWE-agent
  - ACI
  - agent-interface
  - agentic-engineering
date: 2026-06-02
source: "https://x.com/rohit4verse/status/2033945654377283643"
authors: "Rohit (@rohit4verse)"
---

# Harness 才是一切：Cursor、Claude Code、Perplexity 真正构建的东西

> **来源：** [@rohit4verse](https://x.com/rohit4verse)  
> **阅读：** 152 万+ 浏览 | 2,584 赞 | 9,418 书签  
> **关系：** 本文是业务分析师的 Software Factory 指南和 Garry Tan 的停止建造富士康工厂的核心理论基础

---

## 核心论点

> 你用 AI 用得不好，不是因为没找到对的模型。
> 是因为你没搭建对的环境。

有些团队三个人就能交付百万行代码，而另一些团队连一个稳定的 refactor 都跑不出来。这个差距不是 GPT-5 或 Claude 5 带来的。

**差距在于 harness。**

---

## 第一部：没人讨论的真正问题

### 为什么原始能力不够

2024 年中，研究人员注意到一个奇怪的现象：同一个前沿模型在**不同工具环境下**，对相同的编程任务产生截然不同的结果。

这其实不应该让人惊讶。几十年来我们早已知道，好的工具能让工程师大幅提升效率。一个拥有现代 IDE、调试器、版本控制、自动补全和实时 linting 的开发者，和一个用裸文本编辑器的人不在一个量级。

**语言模型也一样。** 它们不是从某种无限内部知识库中进行推理的通用推理机。它们是在上下文窗口内操作 token 的、精密的模式匹配引擎**。接口对它们来说不是便利层——接口就是思维本身。**

这是 2024 年普林斯顿 NLP 组的 **SWE-agent 论文**的核心主张。论文引入了 **Agent-Computer Interface（ACI）** 的概念，并实证证明了同一模型（GPT-4）在同一任务（SWE-bench）上——

| 设置 | 解决率 | 提高 |
|------|--------|------|
| 标准 bash shell 接口 + GPT-4 | 3.97% | baseline |
| 定制 ACI + 同一 GPT-4 | **12.47%** | **+64% 相对提升** |

这个提升完全来自环境设计，而非模型能力的任何改进。

### 不要把上下文窗口当 RAM

天真的 mental model 认为上下文窗口就是 RAM——你把数据 load 进去，模型处理，你得到输出。但上下文窗口实际上更接近 agent 的**全部工作意识**。窗口中的每个 token 都消耗计算，每条无关信息都在争夺模型注意力。

当你在 agent 循环中 grep 一个大型代码库并返回一万行匹配结果时，你不是给了 agent 更多信息。你是在稀释它的注意力。

**SWE-agent 研究人员精确定位了这些失败模式：** 标准 bash 接口导致 agent 漫无目的地搜索。一条 grep 返回数千行结果，agent 迷失在其中。它试图查看一个文件，发现太长放弃了，转而搜索另一个模式。上下文被大量不完整、未过滤的信息填满。

ACI 的解决方案：构建一个**搜索结果上限**的搜索工具。如果搜索返回超过 50 个匹配，工具会抑制输出并告诉 agent 优化搜索条件。看起来是限制——实际上是**释放认知空间**。

---

## 第二部：SWE-Agent 论文与 ACI 的诞生

### ACI 四组件

**1. 搜索与导航**
- 用 `find_file`、`search_file`、`search_dir` 替代标准 grep/find
- 关键区别不是语法——是**输出管理**。结果上限 + 自动优化引导

**2. 文件查看器**
- 每次显示 100 行是最佳值（Golidlocks zone）
- **有状态的**：跨交互维护文件位置
- **关键细节**：每行前加行号。看似表面功夫，但模型在定位精确行号上远胜于"第 75 行左右"

**3. 文件编辑器（带 linting 集成）**
- 每次编辑后自动 linting 检查
- **闭环反馈**：没有 linting 时，agent 可能引入语法错误，跑测试发现不相关错误，开始链条式犯错
- 对比 raw bash 的 `sed`：静默执行，错误累积

**4. 上下文管理**
- 旧观察结果压缩为单行摘要
- 近 5 回合的详细内容保持，更早的折叠

### 消融研究的关键发现

linting 集成始终是**最高杠杆组件**。移除 linting 导致的性能下降最大。这背后的原因：语言模型对语法错误生成的错误消息没有直觉。通过静默 linting 在编辑时捕获问题，整个下游的级联失败被阻止在源头。

> 任何长周期 agent 任务都面临相同的核心挑战：在大型信息空间中导航、在多步骤中维持连贯状态、管理不断增长的上下文。ACI 设计原则是普适的。

---

## 第三部：Anthropic 的 Harness 工程（长期运行的 Agent 问题）

### 上下文窗口边界的难题

SWE-agent 解决的是单次 session 内的接口设计。Anthropic 面临的是另一个问题：**人类不会只用一个 session 完成生产软件**。一个真正有用的 agent 需要能够跨多个 session 工作，跨越上下文窗口的边界，**记住该记住的事**。

**两种失败模式：**
1. **一次做太多**：agent 试图一步完成整个应用，所有功能纠缠在一起，一个失败导致全面失败
2. **幻觉"已经完成"**：新 session 的 agent 看到代码库已有进展，就认为工作完成了（因为代码"看起来很不错"）

根因：**agent 没有能跨越上下文窗口边界的、持久的结构化项目状态理解。**

### 双 Agent 架构

**初始化器 Agent（Initializer）→ 产生三样东西：**
1. `init.sh` —— 每次 session 可靠启动开发环境的脚本
2. **功能清单（feature list）** —— 200+ 端到端功能描述，每项带 `passes: true/false`
3. `claude-progress.txt` + 初始 git commit

**编码 Agent（Coding Agent）—— 每次 session 不同 prompt：**
- 一次处理一个功能
- 结束前保持环境干净
- 更新 progress 文件和 feature list 的 passes 字段

### 功能清单的设计精髓

存储为 **JSON 而非 Markdown**。原因是行为层面的：经验上，模型不太可能不当修改 JSON 文件。每个项目：
```json
{
  "category": "functional",
  "description": "New chat button creates a fresh conversation",
  "steps": [
    "Navigate to main interface",
    "Click the 'New Chat' button",
    "Verify a new conversation is created with an empty chat area"
  ],
  "passes": false
}
```

指令明确：**不可接受删除或修改测试，因为这可能导致功能缺失或 buggy。**

### 清理状态与 Git 提交

每次 session 结束必须：
- git commit（带描述性消息）
- 更新 progress 文件
- 更新 feature list 的 passes

git commit 不仅是检查点——它是**恢复机制**。agent 搞砸了可以 `git revert` 回到上一个已知良好状态。

### 不被提起的失败模式：假装验证完成

Agent 常常标记功能为"已完成"但从未真正端到端验证。单元测试通过了但应用根本没跑起来。

Anthropic 的解决方案：给 agent 访问 **Puppeteer MCP 服务器（浏览器自动化）**——真实地打开浏览器、点击按钮、填表、验证功能是否工作。

> **核心原则：agent 的工作质量受限于其反馈循环的质量。**

### 启动序列

每个 session 开始前标准化流程：
```
1. pwd → 确认工作目录
2. 读取 claude-progress.txt 和 git log → 了解最近工作
3. 读取 feature_list.json → 选择最高优先级未完成功能
4. 运行 init.sh → 确认环境正常
5. 运行现有测试 → 确认一切正常
6. → 开始工作
```

如果启动测试发现应用已损坏，agent 先修复现有问题再开始新工作。

---

## 第四部：OpenAI 的 Harness 工程（零行手动代码）

### 实验

2025 年 8 月底，OpenAI Codex 团队启动了一个 git 仓库，**约束条件只有一个：没有人类编写的代码。**

五个月后，仓库包含约**一百万行代码**——应用逻辑、测试、CI 配置、部署脚本、文档——全部由 agent 生成。约 1,500 个 PR 被打开并合并。**三位工程师的小团队管理着这个"产品"。**

这不是 demo。这是内部真实产品，完全通过 agent 生成代码构建和交付。

### 工程工作的重新定义

当你的主要工作不再是写代码时，你在做什么？

> 你在**设计环境**。你在**指定意图**。你在**构建反馈循环**。你问的不是"这个 bug 怎么修"，而是**"环境缺少什么能力导致 agent 在这里失败了？"**

工程团队的主要工作变成了**使 agent 能做有用的工作**，而不是自己去做。

### 仓库作为唯一真相源

一个关键架构决策：**使仓库本身成为 agent 需要知道的一切的真相源。**

早期尝试了一个巨大的 `AGENTS.md`——包含项目架构、约定、规则的一切。但有两个问题：
1. 上下文是稀缺资源——大文件挤掉了实际任务和代码
2. 不容易保持准确

最终方案：**结构化的 `docs/` 目录作为真相源**，加上一个短小的 `AGENTS.md`（约 100 行）作为进入点地图。

这实现了**渐进式披露（Progressive Disclosure）**：agent 从一个小型、稳定的入口点开始，被引导到需要时再深入。

### 应用可读性

随着代码吞吐量的提升，瓶颈从生成转移到验证。解决方案是**让更多的系统行为对 agent 可见：**
- 每个 agent 任务运行在完全隔离的应用实例上（通过 git worktree）
- 完整的本地可观测性栈：LogQL、PromQL、TraceQL
- Agent 可以查询日志、指标和追踪，就像人类开发者看 Grafana 一样

### 用机械检查代替代码审查

经典问题：**如何在没有人工 code review 的情况下维持架构一致性？**

答案：**用 linter 强制执行边界，不靠人审。** 每个业务域分为固定的层层次结构。Linter 检查代码流向是否遵守层结构。它不是规定层内的实现方式——而是确保跨层的边界不被打破。

关键细节：**linter 错误消息是为 agent 优化的。** 当 linting 捕获违规时，错误消息包含 remediation instructions，格式化为可直接注入 agent 上下文。

他们还把"**黄金原则**"直接编码到仓库中：偏向共享工具而非重复实现、偏向核心抽象而非直接系统调用、保持最低的可变状态。

### 吞吐量改变了合并哲学

当 agent 吞吐量远超人类注意力时，传统工程规范变得适得其反：
- 等待审查的 PR 阻塞 agent 工作
- 测试不稳定被用后续补跑解决，而非阻塞进度
- PR 保持短寿命
- 操作的合并门禁最少

---

## 第五部：Awesome Agent Harness 分类法（7 层）

社区维护的 [Awesome Agent Harness](https://github.com/AutoJunjie/awesome-agent-harness) 仓库将完整的 harness 生态系统分为七层：

| 层 | 名称 | 功能 |
|----|------|------|
| **L1** | Human Oversight | 人批准提案、审查 PR、设定优先级 |
| **L2** | Planning & Spec Tools | 将人类意图转化为结构化规范和任务 DAG |
| **L3** | Full Lifecycle Platforms | 端到端管理从需求到交付 |
| **L4** | Task Runners | 连接问题跟踪器和 coding agent |
| **L5** | Agent Orchestrators | 多 agent 并行执行，隔离 git worktree |
| **L6** | Harness Frameworks & Runtimes | 可组合的原语构建定制环境 |
| **L7** | Coding Agents | 执行层：写、测、调试代码（Claude Code/Codex） |

仓库的核心论点很直白：**L7 是商品化的。** Agent 的真正竞争力不在选择哪个 coding agent。在于 L1-L6——spec tooling、orchestration、feedback loops、observability infrastructure。

---

## 第六部：重复出现的五种设计模式

### 模式 1：渐进式披露（Progressive Disclosure）

不给 agent 所有可能需要的东西。给它**最小化的定向信息**，以及指向更深信息的指针。

出现在：SWE-agent 的上限搜索结果、Anthropic 的 progress file + feature list、OpenAI 的 `AGENTS.md → docs/` 结构。

### 模式 2：Git Worktree 隔离

**一个 agent，一个 worktree。** 每个 agent 有自己的工作目录、分支和环境。变更加隔离、测试加隔离、合并加隔离。

### 模式 3：先写 Spec，仓库作为真相源

Agent 对非正式知识是盲目的——Slack 消息、Google Doc、某人的大脑都不可见。唯一 agent 可操作的就是上下文中的内容。

要在 agent 驱动的开发中取得成功，**所有相关知识必须存在于仓库中，以 agent 可以消费的格式。**

### 模式 4：机械架构执行

人工 code review 无法扩展到 agent 驱动的开发。Agent 一天可以开 3.5 个 PR/人——审查不能是质量的主要机制。

**自定义 linter、结构测试、CI 管道**接管了 code review 的大部分工作。关键原则：**强制执行不变性，而非实现方式。**

### 模式 5：集成反馈循环

每个高效的 harness 架构都尽可能紧密地闭合反馈循环：
- 编辑时的 linting 捕获语法错误
- 运行时错误通过 agent 可查询的可观测性工具暴露
- 端到端测试通过浏览器自动化在应用中验证

更早捕获错误 = 更便宜地修复。对于 agent 来说，这个差距被放大了一个数量级——因为一次未捕获的错误可以污染整个 session 的上下文。

---

## 第八部：构建你自己的 Harness

### 最小有效 Harness

你不需要 OpenAI 级别的可观测性栈。一个真实的项目，最小有效的 harness 应该包含：

1. **一个持久的 progress 文件** —— agent 每次 session 开始读、结束时写
2. **一个结构化的任务列表** —— 具体的、枚举的、可验证的完成标准
3. **版本控制 + 描述性 commit 消息** —— 每次 session 以 commit 结束
4. **如果是 web 应用，加浏览器自动化** —— 能让 agent 真正使用应用的反馈

### 环境审计（诊断流程）

如果你的 agent 系统表现不佳，不要换模型或改 prompt。做环境审计：

1. **什么信息是 agent 需要的但目前无法访问的？** → 添加新工具或文档
2. **任务流中哪些点 agent 经常卡住或犯错？** → 缺少什么反馈？
3. **反馈循环的延迟是多少？** → 编辑时 linting > 运行时观测 > 后续 session 的问题报告

每一个失败都是一个信号——告诉你的环境缺少什么。

---

## 最后的想法

新技术被误解有一个模式。抓人眼球的是原始能力——令人印象深刻的 demo、基准分数、惊艳的发布会——但**真正使技术可用的从来不是原始能力。**

- Web 不是因为 HTML 存在而具有变革性的——是因为**搜索引擎和浏览器**让 Web 可导航
- 移动不是因为智能手机存在——是因为**应用商店和通知系统**让移动可用
- AI 代理正在遵循同样的模式

> **Harness 才是一切。模型是推理引擎。Harness 是上下文、约束、反馈循环、记忆、工具和脚手架——决定了推理引擎的能力能实现什么。**

SWE-agent 论文 + Anthropic 的工程 + OpenAI 的产品 + 社区的开源工具——每一个都证明了同一个事实。**如果你把精力花在更好的模型上，你在做别人也在做的事情。如果你把精力花在更好的 harness 上，你在做几乎没人做的事情。** 这是真正的竞争优势所在。

---

## 与已读内容的连接

这篇文章是三篇中**最底层、最技术**的，它回答了"为什么"：

| 关联文章 | 这篇文章给它们的理论基础 |
|---------|---------------------|
| **businessbarista 的 Software Factory** | 为什么 L3/L4 需要 ACI + harness 基础设施——因为模型能力在正确的 harnees 环境下被释放 |
| **Garry Tan 的 Foxconn 批判** | 为什么"过度控制 = 坏 Harness"——好的 harness 是 SWE-agent 式的认知释放，不是富士康式的囚禁 |
| **Harness Evolution 论文**（2605.30621） | 为什么 harness-updating 平坦+harness-benefit 倒 U 形——Harness 设计比模型选择更关键 |

---

*整理于 2026-06-02 | 原文：@rohit4verse / Rohit | 来源：X/Twitter*
