---
title: "Your LLM Is Burning Through Tokens — Karpathy Found a Way to Save 90%"
source: "https://x.com/bonsaixbt/status/2059266993950277656"
author: "Bonsai 🌳 (@bonsaixbt)"
read_at: 2026-06-01
category: ai-agents
tags: [karpathy, wiki-layer, knowledge-base, token-saving, llm, obsidian, second-brain]
---

# LLM Wiki Layer — Karpathy 式知识库系统，节省 90% Token

> 原文：@bonsaixbt 的 X 长文，介绍基于 Andrej Karpathy 的 Wiki Layer（LLM Wiki）思想，如何构建一个高效的本地知识库系统，实现 70-90% token 节省。

---

## 核心问题

LLM 最大的痛点之一：**反复上传和处理相同的原始文件**。

每次提问，LLM 都要：
- 重新读取整个文档 → 浪费大量 token
- 在文件间失去上下文 → 丢失关键关系
- 忽略重要的文件间关联 → 答案不准确

## Karpathy 的解法：Wiki Layer（LLM Wiki）

思路简单但极其强大：

> **LLM 一次性清洗、结构化、链接所有数据，然后不再接触原始文件，只操作一个干净、组织良好的知识库。**

## 三大优势

- 🎯 **Token 节省 70-90%** — 不再为重复读取付费
- 📈 **答案质量大幅提升** — 信息已清洗、结构化、互联
- 🔗 **自动文件链接** — 建立可见的知识图谱

---

## 系统结构：三个核心文件夹

```
project-root/
├── raw/          ← 不可变的原始源文件
├── wiki/         ← LLM 生成和维护的知识库
└── instructions/ ← 规则和模板
```

### 1. raw/ — 原始文件仓库

- 存放所有原始材料：HTML 页面、PDF、文本笔记、截图、电子表格等
- **永不手动编辑**，保持单一可信源

### 2. wiki/ — 主知识库

- 由 LLM 生成和维护的干净的 Markdown 文件
- 成为 LLM 后续交互的主要工作空间
- 包含内部 Wiki 链接（`[[Page_Name]]`）、元数据、文档间关系

### 3. instructions/ — 规则和模板

- 定义所有规则的文件：
  - 数据如何清洗
  - 使用哪些模板
  - 链接如何创建
  - 需要添加哪些元数据
  - 知识库如何随时间更新

---

## 分步搭建指南

### 第 1 步：建立项目

```bash
mkdir my-wiki && cd my-wiki
mkdir raw wiki instructions
# 把所有原始文件放入 raw/
```

### 第 2 步：启动结构化 Agent

在 Claude（或其他支持文件和代码的强 LLM）中，提供以下系统提示词：

**Agent 会自动执行**：
- 从原始文件中清理技术垃圾、广告、不必要的格式
- 将所有内容转换为干净的 Markdown
- 应用预定义模板
- 创建内部 Wiki 链接（`[[Page_Name]]`）
- 添加元数据并建立文档间的关系

### 第 3 步：在 Obsidian 中打开知识库

直接用 Obsidian 打开项目文件夹，立即获得：
- 可视化的知识图谱，自动显示文件链接关系
- 强大的全文搜索
- 秒级跳转相关笔记

### 第 4 步：使用成品知识库

现在不再需要每次上传几十个文件，只需告诉 LLM：

> **"用我 wiki/ 文件夹里的知识库工作"**

LLM 立刻从一个干净、结构化、互联的知识系统中检索信息。

---

## 为什么 Wiki Layer 优于传统方法

| 维度 | 传统方式 | Wiki Layer |
|------|---------|------------|
| **Token 效率** | 每次重复读取原始文件 | 只需读取结构化的 wiki Markdown |
| **准确性** | 受原始文件杂乱内容干扰 | 信息已清洗、结构化、互联 |
| **可扩展性** | 文件越多越混乱 | 轻松扩展到数百上千文档 |
| **工作流** | 繁杂的文件管理 | Obsidian 提供可视化的"第二大脑" |
| **隐私** | 频繁上传云端 | 全部在本地，无需上传 |

---

## 关键数据

- **Token 节省**：重复查询可达 **70-90%**
- **系统结构**：3 个核心文件夹（raw/ wiki/ instructions/）
- **工具链**：任何强 LLM（Claude 等）+ Obsidian
- **发布者**：@bonsaixbt，5 月 26 日推文
- **传播数据**：119万阅读 / 2519 书签 / 523 赞
