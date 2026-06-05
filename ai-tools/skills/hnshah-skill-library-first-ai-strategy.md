---
title: "Every Company's First AI Strategy Should Be a Skill Library"
tags:
  - skills
  - ai-strategy
  - agent
  - enterprise-ai
date: 2026-06-05
source: "https://x.com/hnshah/status/2062647149582750101"
authors: "Hiten Shah"
---

# 每个公司的第一个 AI 策略应该是 Skill Library

> **来源：** [Every Company's First AI Strategy Should Be a Skill Library](https://x.com/hnshah/status/2062647149582750101)  
> **作者：** Hiten Shah (@hnshah)  
> **发布时间：** 2026-06-04  
> **数据：** 586 ❤️ · 49 🔁 · 25 💬

---

## 一、核心论点

观察顶尖员工做事——销售、支持、财务、产品——你会发现他们都有**模式（patterns）**。这些模式通常被归为"经验"、"判断力"、"品味"或"机构知识"，但在 AI 时代，这些东西有了新名字：**Skills（技能）**。

**一句话论点：**
> 每个公司的第一个 AI 策略，应该是一个 Skill Library。

---

## 二、关键概念

### 2.1 Access ≠ Good Work

很多人开始用 AI 时，第一反应是**接入数据**——接 CRM、接 Slack、接 Google Drive、接 GitHub。
但这远远不够：

> "An agent can read every sales note and still miss the shape of a deal."
> "An agent can search every support ticket and still fail to recognize the customer who needs immediate attention."

接入给了 agent **context**，但没法给它**判断力**和**工作方式**。后者才是 skills 要做的事。

### 2.2 What a Skill Is

Skill > Prompt。

| | Prompt | Skill |
|---|---|---|
| 作用 | 告诉 agent 具体怎么做一件事 | 捕获一种**可复用的工作方式** |
| 内容 | 单次指令 | 指令 + 示例 + 模板 + 检查清单 + 参考 + 经验法则 |
| 复用 | 每次重新写 | 需要该类任务时自动应用 |
| 形式 | 文本字符串 | 结构化文件（如 SKILL.md + 附属文件） |

> "A skill is the method made reusable."

### 2.3 演化路线图

```
Data → Connectors → Skills → Plugins
```

- **Data & Connectors**：接入信息源（CRM, Slack, Google Drive...）
- **Skills**：捕获判断、流程、可重复的工作方式
- **Plugins** = Data + Connectors + Skills + Actions 的组合体

下一阶段：**智能系统 = 信息接入 + 理解工作方式 + 可执行动作**

---

## 三、计算史上的重复模式

这个趋势不是 AI 发明的，是计算机行业一直以来的方向：

| 时代 | 对象 | 复用什么 |
|------|------|---------|
| Unix | 命令 | 有用的操作 |
| Shell | 脚本 | 操作序列 |
| 软件工程 | 库（Libraries） | 代码 |
| 服务架构 | API | 服务 |
| 业务流程 | Workflows | 流程 |
| AI 时代 | **Skills** | **判断力** |

> "Skills make judgment reusable."

**变化的核心：** 过去，人类需要读剧本再执行。现在，agent 可以直接加载剧本、使用工具、检查文件、运行脚本并持续执行。**剧本变成能动的了（the playbook can become active）。**

---

## 四、Skill Library 作为公司资产

假设两家公司用同一个前沿模型：
- **公司 A**：只接入了系统
- **公司 B**：接了系统 + 给了它一个基于公司最佳实践构建的 skill library

公司 B 有一个不同的资产。它的 agent 知道公司如何做销售 call 准备、审合同、写发布文案、调查 bug、处理升级、总结研究、解释财务表现。

> "A good skill prevents the same mistake from being corrected twice."
> "A better one raises the floor for everyone who uses it."
> "A great one captures judgment that used to take years to build."

### 最有价值的 Skills 是私有的

公开的 skill marketplace 会有，但真正有价值的一定在公司内部：

> "Your customer escalation process, sales qualification lens, and product review standards. The format you use for board updates, the legal fallback positions you rely on, and the voice that defines your brand. Even the way you decide what matters. That's the knowledge competitors cannot download."

---

## 五、实践指导

### 从哪里开始

> "Before picking platforms, map the repeated work."

找到这些场景：
1. **经验丰富的人明显比其他人做得好的工作流程**
2. **涉及判断力（judgment）而不只是体力（effort）的任务**
3. **那些不是"工作本身"但围绕工作的东西**——销售 call、客户调研、支持升级、PRD、事故复盘、合同、预测、发布、竞品分析、release notes

### 如何挖掘 Skill 素材

观察你团队里最优秀的人，问这些问题：

> What catches their attention first?
> What tends to get overlooked?
> Which examples shape their approach?
> What questions come up repeatedly?
> Which errors are they trying to avoid?
> How do they define success?

那就是 raw material。把它变成 skill，投入使用，持续改进，保持 owner close to the work。

### 公司的真实 AI 策略

> "Companies will get the most out of agents when they stop treating AI as a layer of generic intelligence sprinkled across the business and instead embed it deeply into the workflows where it can drive real outcomes."

**最终建议：**
1. 教 agent 业务实际怎么运作
2. 把反复出现的判断力转化为可复用系统
3. 让 top performer 的方法更容易被应用、改进、且不易流失

> "A company's AI advantage will come from the work it teaches the model to do well, rather than from the model it chooses."

---

## 六、总结

| 概念 | 要点 |
|------|------|
| Skill vs Prompt | Skill 是可复用的工作方式，不仅仅是一次性指令 |
| Access vs Understanding | 接入数据 ≠ 理解工作方式 |
| 演化路径 | Data → Connectors → Skills → Plugins |
| 复用对象 | 判断力（judgment）而非代码 |
| Skill Library | 公司最被低估的 AI 资产 |
| 私有价值 | 内部 skills 比通用的有价值得多 |
| 从哪里开始 | 映射重复性工作，提取 top performer 的隐性知识 |

---

*Processed on 2026-06-05 from X.com article by Hiten Shah*
