---
title: "Karpathy 的 Agentic Engineering 终于有了趁手的工具 —— Google Agents CLI 保姆级教程"
tags:
  - AI-Tools
  - Agentic Engineering
  - Google
  - Karpathy
  - ADK
  - RAG
  - 智能体
date: 2026-06-29
source: "https://x.com/akshay_pachaar/status/2070860837448040832"
authors: "Akshay 🚀 (@akshay_pachaar)"
---

# Karpathy 的 Agentic Engineering 终于有了趁手的工具

> **来源：** [Akshay 🚀 的 X 长文](https://x.com/akshay_pachaar/status/2070860837448040832)
> **数据：** 12.4 万阅读 · 1088 赞 · 2447 收藏 · 169 次转发
> **作者：** Akshay（27.9 万粉丝，Daily Dose of Data Science 联合创始人，前 LightningAI AI 工程师）

---

## 一句话梗概

Karpathy 在 Sequoia Ascent 2026 定义了 **Agentic Engineering**——spec 设计、eval 循环、安全审查——但一直缺工具支撑。Google 刚推出的 **Agents CLI** 填补了这个空白：一次安装，给任何编码助手注入 7 项 ADK 技能，从脚手架生成 → 本地测试 → 评估 → Cloud Run 部署 → 注册到 Gemini Enterprise，全程用自然语言驱动，不用离开编辑器。

![Agents CLI 封面](../image/karpathy-agentic-engineering-google-1.jpg)

---

## 背景：Agentic Engineering 缺什么？

Karpathy 在 Sequoia Ascent 2026 的演讲中定义了 **Agentic Engineering**，将其与"vibe coding"划清界限：

> Agentic Engineering = 能交付生产级 Agent 的工程纪律

核心技能三件套：
1. **Spec 设计** —— 精确的 Agent 行为规范
2. **Eval 循环** —— 系统化的评估反馈
3. **安全审查** —— 权限/数据安全边界

**问题：** 到今天为止，实践 Agentic Engineering 需要在多个工具间来回切换：
- 编辑器（写代码）
- 终端（脚手架）
- 浏览器（测试）
- 云控制台（部署）
- 另一个框架（eval）

没有一个统一的工具链。

---

## Google Agents CLI：一站式解决

Agents CLI 把完整的 Agent 生命周期统一在一个终端会话中：
- **脚手架生成**（Scaffolding）
- **评测**（Evaluating）
- **部署**（Deploying）

### 核心机制：7 项注入技能

安装 Agents CLI 后，它会向你的编码助手注入 **7 项 ADK 技能**：

| 技能 | 作用 |
|------|------|
| ADK 代码模式 | 知道 ADK 的最佳实践和代码结构 |
| 项目脚手架 | 知道如何从模板生成项目骨架 |
| Eval 设置 | 知道如何用 LLM-as-Judge 打分 |
| 部署配置 | 知道 Agent Runtime 和 Cloud Run 配置 |
| Cloud Trace 可观测性 | 知道如何集成链路追踪 |
| 检索增强模式 | 知道 RAG agent 的正确模式 |
| 安全/权限配置 | 知道 IAM 和安全边界 |

**一次安装，所有编码助手同步获得这些技能：** Antigravity、Claude Code、Cursor、Codex 等——全平台统一。

---

## 实战：6 步从零到生产部署

作者用 **RAG 知识助手**作为示例，全程只用了 6 条自然语言 prompt。

### Step 1：安装 Agents CLI

```bash
# 一条命令安装，注入所有技能
agents setup
```

安装后，你的编码助手就知道了 ADK 的所有模式。

### Step 2：构建 RAG Agent

打开编码助手，用自然语言描述：

> "Build a RAG agent that answers questions about Python fundamentals."

编码助手自动激活 ADK 技能：
1. 从 `agentic_rag` 模板生成项目
2. 使用 **Vector Search** 作为数据存储
3. 发现模板缺少**引用支持**，主动改写了 Agent 指令要求内联引用（grounded answers with inline citations）
4. 修改了检索器（retriever），让每个返回文档携带 source ID
5. 创建了数据存储（datastore）
6. 摄入了一个合成 Q&A 语料库（12 条 Python 基础问答）
7. 运行冒烟测试

> **关键点：** 不是死板套模板——AI 发现问题（缺引用）就主动修复了。

### Step 3：本地测试

```bash
# 启动 ADK Web UI
agents ui
```

在浏览器中打开交互界面验证两件事：

**✅ 正确检索+引用：**
> Q: "how to merge two dictionaries?"
> A: 介绍了 `merge` 操作符和 `update()` 两种方法。
> 内附引用 **[source: 1003]** ✅

**✅ 缺失上下文时拒绝回答：**
> Q: "who won the FIFA World Cup in 2022?"（语料库中没有）
> A: "I cannot answer based on the available documents." ✅

### Step 4：Eval 评估（最重要的一步）

```bash
# 一句话生成完整 eval 套件
agents eval
```

编码助手自动生成了 **20 个测试场景**，分 4 类：

| 类别 | 数量 | 目的 |
|------|:----:|------|
| 正确检索 | 6 | 语料库能回答的问题 |
| 上下文不足 | 5 | Agent 应拒绝回答 |
| 多跳推理 | 5 | 需要跨多个文档推理 |
| 引用准确度 | 4 | 验证来源未编造 |

> Karpathy 特别指出过这个缺口：89% 的团队有可观测性，但**只有 52% 有 eval**。

**Eval 结果：**
- 引用准确度：**1.00（满分）** —— 所有 20 个测试无一编造来源
- 但发现了**幻觉边缘案例**：遇到语料库外的问题时，Agent 有时会追加通用知识而不是直接说不知道

**根因追踪：** Eval 追踪到 Agent 指令中的一行——`"if you already know the answer to a simple question, you may respond directly without using the tools"`。删掉这行就解决了。

> **这就是 eval 的价值：不是泛泛地"测一下而已"，它能精确定位到是哪一行代码的问题。**

### Step 5：部署到 Agent Runtime

```bash
# 一句话部署
agents deploy
```

编码助手自动：
1. 添加了部署入口点和基础设施配置
2. 部署到 Google Cloud
3. 全程约 **2-3 分钟**
4. **Cloud Trace 默认启用**，第一个请求开始就有可观测性

### Step 6：注册到 Gemini Enterprise（最关键的一步）

```bash
# 一句话注册到企业平台
agents register gemini-enterprise
```

**为什么这一步如此重要？**

> 大多数 Agent 在部署后就"默默死掉了"。它们能工作，但只有开发者本人知道怎么用。
> 其他团队成员需要：端点 URL → 正确的 API 凭证 → 知道这东西存在。

注册到 Gemini Enterprise 后：
- 整个组织都能在 Gemini Enterprise 应用中发现这个 Agent
- **IAM 控制访问权限**
- **企业仪表盘**提供完整可观测性
- 其他团队可以直接使用知识助手，**无需搭建自己的 RAG 管道**

---

## 作者总结

> **一次终端会话、6 条自然语言 prompt，Agent 从空文件夹变成了全组织可用的生产级助手。**

这就是有趁手工具的 Agentic Engineering，正如 Karpathy 所描述的那样。

---

## 相关资源

- [Agents CLI (GitHub)](https://github.com/google-cloud/agents-cli)
- [ADK 文档](https://google-cloud.github.io/adk-docs)
- [Agent Platform](https://cloud.google.com/agent-platform)

---

*整理于 2026-06-29，原文来自 [Akshay 🚀 的 X 长文](https://x.com/akshay_pachaar/status/2070860837448040832)*
