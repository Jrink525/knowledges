---
title: "零转 AI 工程师 14 周路线图 — 完全免费，从搭环境到部署生产级系统"
author: "self.dll (@seelffff)"
source: "https://x.com/seelffff/status/2054991798519656789"
date: 2026-05-17
tags:
  - ai-engineering
  - learning-path
  - ml
  - deep-learning
  - llm
  - agents
  - career
  - free-resources
category: "ai-engineering"
description: "@seelffff 整理的 14 周 AI 工程师完全免费学习路线图。覆盖 Python 环境搭建 → ML 基础 → 深度学习/Karpathy → LLM/Prompt → AI Agent → 部署上线。所有资源免费（Anthropic Academy/Google AI/Microsoft GitHub repos），含每周检查点和项目。"
---

# 零转 AI 工程师 14 周路线图 — 完全免费

> **来源：** [Zero to AI Engineer - The Roadmap](https://x.com/seelffff/status/2054991798519656789) — @seelffff
>
> **核心理念：** 别再花 $300/月买课程了。Google、Anthropic、OpenAI 自己就在免费教。14 周，$0，从零到部署真实 AI 系统。

---

## 三条铁律

| 规则 | 说明 |
|------|------|
| **不要跳步** | 第 3 步假设你已完成第 2 步。跳过基础直接学 LLM = 复制你不懂的代码 |
| **记笔记** | 用 Obsidian（免费）。每次学习后写三件事：学到了什么、什么让你惊讶、什么还不懂 |
| **每步必须构建** | 每步结束有一个 checkpoint。做不出来就退回去重学 |

---

## 学习路径概览

```
第 1 天: 搭环境
第 1-2 周: AI 基础概念
第 3-5 周: ML 数学基础 + 实战
第 6-8 周: 深度学习 + 从零搭神经网络
第 9-10 周: LLM + Prompt Engineering + RAG
第 11-12 周: AI Agent（MCP + LangGraph）
第 13-14 周: 部署 + 评估 + 安全 + 求职
```

---

## 第 1 步：搭环境（Day 1）

一个晚上搞定工具，不要纠结。

### 安装工具

| 工具 | 用途 | 链接 |
|------|------|------|
| **Python 3.11+** | 主语言 | python.org/downloads（勾选 Add to PATH） |
| **VS Code** | IDE | code.visualstudio.com（装 Python 插件） |
| **Git + GitHub** | 版本控制 | github.com |
| **Obsidian** | 笔记 | obsidian.md |
| **Ollama** | 本地跑模型 | ollama.com（先装上，第 4 步开始用） |

### 创建免费账号

| 平台 | 内容 | 价值 |
|------|------|------|
| **Anthropic Academy** | 16 门免费课程 + 证书。2026 年被严重低估的最佳 AI 学习平台 | ⭐⭐⭐⭐⭐ |
| **OpenAI Academy** | 免费工作坊、教程、AI Foundations 课程 | ⭐⭐⭐⭐ |
| **Google AI** | Google AI Professional Certificate，7 模块 | ⭐⭐⭐⭐ |
| **Coursera（审计模式）** | IBM ML 证书等全部免费看视频 | ⭐⭐⭐ |

> **⚠️ Coursera 审计模式小技巧：** 当它让你付费时，找页面底部的 "Audit this course" 链接。视频和材料全量免费，只是没有 Coursera 自己的证书——但你可以拿 Anthropic/OpenAI/Google 的证书。

### ✅ Checkpoint
- [ ] Python + VS Code + Ollama 已安装
- [ ] GitHub 账号已创建
- [ ] Obsidian vault 就绪
- [ ] Anthropic Academy / OpenAI Academy / Google AI / Coursera 账号就绪

---

## 第 2 步：AI 基础（第 1-2 周）

> **为什么重要：** AI 素养已成为招聘过滤器。2025 WEF 分析显示具备 AI 素养的人薪资高 **15–22%**。

### 第 1 周：宏观认知

**学习顺序：**

```
先 → Google AI Professional Certificate（模块 1-3）
     grow.google/ai-professional
     最温和的入门。无代码。了解 AI 是什么、如何与 AI 脑暴、如何用 AI 做研究。建立词汇表。

然后 → Anthropic Academy: AI Fluency: Framework & Foundations
     anthropic.skilljar.com
     4D AI Fluency Framework（与大学教授联合开发）。2-3 小时。
     → 这是 2026 年最好的入门课程之一，LinkedIn 上认 Anthropic 的证书。
```

### 第 2 周：第一次写代码

```
→ microsoft/generative-ai-for-beginners（第 1-6 课）
  github.com/microsoft/generative-ai-for-beginners
  95,000+ stars，21 课。Fork 这个仓库，完成第 1-6 课。
  内容：什么是 GenAI、LLM 如何工作、用 prompt、第一个聊天应用。
```

### ✅ Checkpoint
- [ ] 能用自己的话解释 LLM、tokens、transformer
- [ ] Jupyter notebook 能跑起来了
- [ ] Obsidian 有 4-6 条笔记

---

## 第 3 步：ML 基础（第 3-5 周）

> **为什么重要：** ML 基础是「复制教程的人」和「能调试模型的人」之间的分水岭。公司愿意付 **$150K+** 给知道"为什么模型表现不佳"的工程师。

### 核心学习材料

| 资源 | 内容 | 方式 |
|------|------|------|
| **microsoft/ML-For-Beginners**（主） | 12 周课程：回归、分类、聚类、NLP 基础。Quiz + Notebooks + 挑战 | 压缩到 3 周，每天 2 课 |
| **IBM ML on Coursera**（并行） | 审计模式免费。传统视频格式。双角度学习加深记忆 | 配合 Microsoft repo 一起看 |
| **mlabonne/llm-course**（数学参考） | 线代、微积分、概率。只看和 ML 相关的部分，遇到不懂的来查 | 参考书 |

### 第 5 周项目
从 Microsoft repo 选一个数据集，**自己从头构建一个分类模型**，推送到 GitHub。

### ✅ Checkpoint
- [ ] 理解回归、分类、聚类、梯度下降、损失函数、过拟合
- [ ] 在真实数据上训练过模型
- [ ] GitHub 上有一个项目

---

## 第 4 步：深度学习 + 从零搭神经网络（第 6-8 周）

### 核心：Karpathy 的 nn-zero-to-hero

> **Andrej Karpathy** — 前特斯拉 AI 总监、OpenAI 联合创始人。他**不用任何框架，只用 Python + 数学**，从零搭建神经网络。

| 周次 | 内容 | 产出 |
|------|------|------|
| **第 6 周** | 讲座 1-3：micrograd + makemore | 逐行跟敲、运行、打破它 |
| **第 7 周** | 讲座 4-5：激活函数、BatchNorm、反向传播 | 每天一课，做详细笔记 |
| **第 8 周** | 讲座 6-7：GPT 从零搭建 + Tokenization | 自己动手搭了一个 transformer |

> **边学边做的实验：** 同时打开另一个终端跑 `ollama run llama3.2:3b`，把你训练的"玩具模型"和真正的 3B 参数模型对比。3B 参数 vs 你的 10M 参数带来的输出质量差异会让你大开眼界。

### 补充

| 资源 | 内容 |
|------|------|
| **microsoft/AI-For-Beginners** | 第 7-12 周：CNN、RNN，拓展 CV 方向 |
| **Anthropic Academy: Building with the Claude API** | 理解模型内部后，学如何通过 API 使用模型。涵盖认证、system prompt、tool use、streaming。从理论到产品的桥梁。 |

### ✅ Checkpoint
- [ ] 从零搭了一个神经网络
- [ ] 理解反向传播、注意力机制、transformer
- [ ] 能解释 GPT 的原理
- [ ] 能用 Ollama 本地跑模型
- [ ] 知道 Claude API

---

## 第 5 步：LLM + Prompt Engineering（第 9-10 周）

### 核心：mlabonne/llm-course（LLM Scientist Track）

> [github.com/mlabonne/llm-course](https://github.com/mlabonne/llm-course) — 最全面的免费 LLM 课程，每章都有 Colab notebook。

| 模块 | 说明 |
|------|------|
| **LLM 架构** | 和你用 Karpathy 搭建的内容连接起来 |
| **微调（LoRA、QLoRA）** | 为特定任务定制模型 |
| **量化** | 本地跑模型（连接你的 Ollama） |
| **评估** | 衡量模型是否真的好 |

### Prompt Engineering

| 资源 | 说明 |
|------|------|
| **OpenAI Academy** | "Intro to Prompt Engineering" + "ChatGPT for any role" |
| **Anthropic Prompt Engineering Guide** | docs.anthropic.com — 互联网上最好的 prompt 工程指南之一。不是课程，是深度参考文档。 |

### 完成 Generative AI for Beginners
回去完成 **第 7-21 课**。有了深度知识后，这些高级课程会豁然开朗：RAG、function calling、设计模式、微调。

### 第 10 周项目：用你的 Obsidian 笔记构建 RAG

```
使用 ChromaDB 或 LanceDB（免费、本地）索引你的 AI-Learning vault。
构建一个能回答你所学内容一切问题的工具
→ 你是在为你的"第二大脑"再建一个第二大脑
→ 推送到 GitHub
```

### ✅ Checkpoint
- [ ] 完成第 5 步全部学习
- [ ] 搭建了一个 RAG 系统
- [ ] 理解微调、量化的基本概念
- [ ] GitHub 上有 RAG 项目

---

## 第 6 步：AI Agent（第 11-12 周）

### 核心学习

| 资源 | 说明 |
|------|------|
| **microsoft/ai-agents-for-beginners** | 12 课：工具使用、记忆、多 Agent 系统、编排 |
| **Anthropic Academy: MCP 课程** | "Introduction to Model Context Protocol" + "MCP: Advanced Topics"。MCP 是 2026 年 Agent 工具连接的标准 |
| **LangGraph** | 用免费 Colab Notebook 花 2-3 次学习，最流行的有状态多步 Agent 工作流框架 |
| **Anthropic Cookbook** | docs.anthropic.com — 最好的 tool-use 和 MCP 实战案例 |

### 最终 Agent 项目

> 构建一个使用 **MCP + Claude** 操作本地文件的 Agent。
>
> **示例：** 一个 Agent 读取你的 Obsidian vault，检查网页上你正在学习主题的更新，每天生成一份摘要发到你的 Telegram。
>
> 参考原作者文章："I Built an AI Agent That Manages My Life" 获取架构灵感。

### ✅ Checkpoint
- [ ] 构建了一个可工作的 AI Agent，使用 MCP
- [ ] 理解 Agent 架构、工具使用、多步工作流
- [ ] 你的作品集又丰富了

---

## 第 7 步：部署 + 作品集 + 负责任 AI（第 13-14 周）

### 部署（全部免费）

| 平台 | 用途 |
|------|------|
| **Gradio + Hugging Face Spaces** | 最快的 ML demo 分享方式，免费托管 |
| **Streamlit Community Cloud** | 数据类应用，免费 |
| **Vercel** | Web 端 AI 工具，免费 |

### 评估模型

> 部署一个不评估的模型 = 不负责任。

| 工具 | 用途 |
|------|------|
| **DeepEval** | LLM 评估的 opensource 框架 |
| **RAGAS** | 专门评估 RAG 流水线（你的 Obsidian RAG） |
| **LLM-as-Judge** | 用一个 LLM 评估另一个的输出。Claude 在这方面很出色 |

### 负责任 AI 与安全

> 90% 的免费指南教你怎么搭，但不教你怎么**负责任地**搭。

| 主题 | 说明 |
|------|------|
| **Constitutional AI** | Anthropic 的核心方法：理解对齐原理 |
| **Prompt Injection 防御** | 保护你的应用免受对抗性输入攻击 |
| **Red-teaming** | 在用户发现之前，自己压力测试你的系统 |

**资源：** Anthropic 官方安全指南 + Anthropic Academy 中的 Responsible AI 课程

### 作品集与求职

> **你的 GitHub 在 AI 行业就是你的简历。**

1. **GitHub README** — 专业个人 README + 项目 README（含架构图和在线 demo 链接）
2. **LinkedIn 案例** — 每个项目写 2-3 个简短案例研究：什么问题、怎么解决的、学到了什么
3. **职业路径：**
   - Junior AI Engineer: **$80–120K**
   - Prompt/Agent Engineer: **$120–180K**
   - AI Product Engineer: **$150–250K**

### 结业项目

> 构建一个解决你生活中真实问题的**生产级 AI Agent**。已部署。带评估系统。带安全检查。
>
> 这就是你给雇主看的东西。这就是你发推的东西。这就是证据。

### ✅ Checkpoint
- [ ] 一个已部署、已评估、经过安全检查的 AI 系统
- [ ] 专业的 GitHub 个人主页
- [ ] LinkedIn 案例研究
- [ ] 你已经具备求职能力了

---

## 维护模式：如何保持不掉队

> AI 变化太快。以下是每周例行公事，保持前 10%：

| 时间 | 事项 | 耗时 |
|------|------|------|
| **周一** | 查看 Anthropic、OpenAI、Google 的 release notes | 10 分钟 |
| **周三** | 浏览 arxiv-sanity-lite，看一篇有趣的论文摘要 | 15 分钟 |
| **周五** | 看一个 Yannic Kilcher 或 1littlecoder 视频 | 20 分钟 |
| **每月** | 用一个新工具或新技术做一个小项目，推 GitHub | 若干小时 |

> **每周总计：~1 小时。** 这就能让你保持在 AI 从业者的前 10%。

---

## 完整资源汇总

### 免费课程（带证书）

| 平台 | 链接 | 内容 |
|------|------|------|
| **Anthropic Academy** | anthropic.skilljar.com | 16 门课，免费证书 |
| **OpenAI Academy** | academy.openai.com | 工作坊、教程、AI Foundations |
| **Google AI Professional Certificate** | grow.google/ai | 7 模块 |
| **IBM ML on Coursera** | 审计模式免费 | 完整 ML 证书 |
| **NVIDIA DLI** | developer.nvidia.com/training | GPU & 深度学习 |
| **DeepLearning.AI** | 短课程（Andrew Ng） | Agentic AI、LangChain for LLM Apps |

### GitHub 仓库（按学习顺序）

| 仓库 | Stars | 内容 |
|------|-------|------|
| **microsoft/generative-ai-for-beginners** | 95K★ | 21 课 GenAI |
| **microsoft/ML-For-Beginners** | 45K★ | 12 周经典 ML |
| **microsoft/AI-For-Beginners** | 35K★ | 24 课深度学习 & CV |
| **karpathy/nn-zero-to-hero** | — | Andrej Karpathy 从零搭神经网络 |
| **mlabonne/llm-course** | 40K★ | 完整 LLM 路线图 + Colab |
| **microsoft/ai-agents-for-beginners** | — | 12 课 AI Agent |

### 免费工具

| 工具 | 说明 |
|------|------|
| **Ollama + Open WebUI** | 本地跑模型，自托管 ChatGPT 替代品 |
| **Anthropic Cookbook** | 最佳 tool-use 和 MCP 实战 |
| **Hugging Face Course (2026)** | Agent 和 Evaluation 部分 |
| **ChromaDB / LanceDB** | 免费本地向量数据库，用于 RAG |

### YouTube 推荐

| 频道 | 内容 |
|------|------|
| **Andrej Karpathy** — Neural Networks: Zero to Hero |
| **3Blue1Brown** | 神经网络 & 线性代数可视化 |
| **Yannic Kilcher** | AI 论文解读 |
| **1littlecoder** | 最新 AI 工具和实现（2026） |
| **Matt Wolfe** | AI 新闻和工具评测 |

---

## 今晚就开始

接下来 **60 分钟**要做的事：

1. **安装 Obsidian**，创建 AI-Learning vault → 5 分钟
2. **注册 Anthropic Academy**，开始 AI Fluency，看完第一个模块，写下第一条笔记 → 30 分钟
3. **Fork** microsoft/generative-ai-for-beginners 到 GitHub，打开第 1 课阅读 → 20 分钟

> 2026 年真正能学会 AI 的人，不是那些收藏 50 篇文章的人，而是那些**打开终端开始敲的人**。

---

*源文章作者：* [@seelffff](https://x.com/seelffff)
*整理于 2026-05-17*
