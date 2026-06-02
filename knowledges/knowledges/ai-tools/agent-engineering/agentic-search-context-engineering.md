---
title: "Agentic Search for Context Engineering——Agent 上下文工程的核心是搜索"
tags:
  - agent
  - context-engineering
  - RAG
  - agentic-search
  - tool-engineering
  - elasticsearch
date: 2026-05-29
source: "https://leoniemonigatti.com/blog/agentic-search-for-context-engineering.html"
authors: "Leonie Monigatti (Elastic)"
---

# Agentic Search for Context Engineering —— Agent 上下文工程的核心是搜索

> **来源：** [Agentic Search for Context Engineering](https://leoniemonigatti.com/blog/agentic-search-for-context-engineering.html)
> **作者：** Leonie Monigatti（Elastic）
> **整理日期：** 2026-05-29

本文是作者在 AI Engineer Europe 2026 上同名 Workshop 的长文版，探讨了 context engineering（上下文工程）与搜索工具的关系。[Workshop 仓库](https://github.com/iamleonie/workshop-agentic-search)和[视频](https://www.youtube.com/watch?v=x2bH0RKPgdc)均有提供。

---

## 核心论点

> **上下文工程 ≈ 80% 的 agentic search**

Context engineering 就是从所有可能的上下文中，决定哪些信息真正放进 Agent 的 context window 以让 LLM 生成最佳回答。这个过程的核心是一套搜索工具（search tools），Agent 可以按需选择和调用来获取上下文。

---

## 从 RAG 到 Context Engineering 的演进

### 第一阶段：Retrieval-Augmented Generation (RAG)

2024 年我们刚开始用 LLM 构建系统时，采用固定检索流水线：

- 用户消息几乎原封不动地用作搜索查询（通常是向量搜索）
- 从数据库拉取一次 chunks
- 检索结果 + 用户消息拼入 prompt，喂给 LLM

**问题：**

- 模型不需要外部上下文时也检索，无关 chunks 反而混淆它
- 只检索一次，无法修正查询——如果结果不够好，能不能再来一次？
- 不支持多跳检索——第一波 chunks 可能只告诉你下一步搜什么，但流水线不会再跑一轮

### 第二阶段：Agentic RAG / Agentic Search

把固定流水线替换成一个搜索工具。Agent 自己决定：是否要调用搜索工具、结果是否相关、是否需要更多检索、是否需要重写搜索查询。

这个阶段通常只有一种上下文源和一个检索工具。

### 第三阶段：Context Engineering

现在我们有多种上下文源：

| 上下文源 | 原生搜索工具 |
|---------|-------------|
| 本地文件（repo、scratch pad、skills） | file search |
| 数据库（大规模企业数据） | 语义搜索 / 查询执行 |
| 网页 | web search |
| 长期记忆 | memory tools |
| Agent Skills | skill loading |

此外还有一个万能工具——**shell 工具**（也叫 bash tool / exec tool），可以通过 CLI 与大部分上下文源交互（local files 的 `ls`/`grep`、数据库的 CLI、网络的 `curl` 等）。

虽然 shell 工具很万能，但作者的另一篇文章《[The shell tool is not a silver bullet for context engineering](https://www.elastic.co/search-labs/blog/search-tools-context-engineering)》已经指出：**核心问题不是"shell vs 其他"，而是"你的 stack 里应该有哪些搜索工具"**。

> **一句话总结：做好的搜索是困难的。正因如此，我们才有这么多不同的搜索技术，才需要根据延迟和质量要求来策划你的搜索工具栈。**

---

## 构建搜索工具的基础知识

### Agentic Search 的三大失败模式

1. **Agent 根本不调用任何工具**——直接凭参数化知识回答
2. **Agent 调了错的工具**——例如用 web search 搜公司内部索引
3. **Agent 调对了工具但参数错了**

### Tool Description 是王道

Tool description 是任何工具最重要的部分。大多数 system prompt 里只有一行最简单的描述就期望 Agent 能正确使用它。

**推荐的 Tool Description 模板：**

| 组件 | 说明 |
|------|------|
| Core purpose | 工具的核心用途 |
| Trigger conditions | 什么情况下使用 |
| Actions | 工具做什么 |
| Relationships | 与其他工具的关系、调用顺序 |
| Limitations | 工具的局限性 |
| Examples | 参数示例 |

先从清晰的 core purpose + trigger conditions 开始，当发现 Agent 使用时出问题，逐步加入更多组件。如果还不够，在 system prompt 里重复同样的规则。

### 参数复杂度

参数复杂度从简单到困难递增：

```
简单 ID  < 语义搜索字符串 < 带过滤器的搜索 < 完整查询语言（SQL/ES|QL）
```

大多数模型在生成 SQL 方面表现不错，但风险仍然明显增加。

---

## 代码实战：三种搜索工具方案

作者用 AI Engineer Europe 2026 日程数据集，通过 LangChain 搭建了三种搜索方案。

### 方案一：Vanilla Agentic Search（纯语义搜索）

**结构：** 一个语义搜索工具，单一索引 `conference_schedule`

**关键代码：**

```python
@tool()
def semantic_search_conference_sessions(query: str) -> str:
    """Runs a semantic search query to find conference sessions by concept or topic."""
    docs = vector_store.similarity_search(query, k=3)
    return "\n\n".join(...)
```

**优点：** 简单直接，语义匹配自然语言描述效果好

**缺点：** 遇到精确关键词的查询时崩溃。例如搜索 "GEPA"（一个精确缩写），语义搜索返回了无关的 "Gemma" 相关内容，完全没找到 Samuel Colvin 介绍 GEPA 的 Workshop。

### 方案二：Agentic Search with DB Query Tool（通用数据库查询 + Agent Skills）

**结构：** 用一个通用 ES|QL 查询工具替换窄范围语义搜索

**关键代码：**

```python
@tool()
def execute_esql_query(esql_query: str) -> str:
    """Execute an ES|QL query against the conference_schedule index."""
    try:
        response = es_client.esql.query(query=esql_query, format="csv")
        return response.body
    except Exception as e:
        return f"Error executing ES|QL query: {e}"
```

**核心发现：**
- Agent 第一次生成的 ES|QL 用了 `%GEPA%`（SQL 习惯），但 ES|QL 用 `*` 做通配符 → 需要技能加持
- 引入 **Agent Skills**：创建一个 `elasticsearch-esql` 技能文档，Agent 通过 `load_skill` 工具在调用查询前先加载该技能
- 技能加载后，Agent 能写出正确的 ES|QL 查询（`LIKE "*GEPA*"`），成功找到结果
- 通用查询工具还能处理分析性问题（如"4月8日有多少场会议？"），通过 `STATS count = COUNT()` 精确定量

**优点：** 更强大，能处理模糊或复杂查询，包括聚合分析

**缺点：** 需要更强模型（gpt-5.4-mini 而非 nano），引入 skill loading 增加成本和延迟

### 方案三：Agentic Search with Shell Tool

**结构：** 数据从 Elasticsearch 移到本地文件，Agent 通过 shell 工具 + grep 搜索

**关键代码：**

```python
from langchain_community.tools import ShellTool
shell_tool = ShellTool()  # 默认没有安全保护，生产环境需要沙箱
```

**实验结果：**
- 搜索 "GEPA"：Agent 先 `ls -R` 探索文件系统，然后 `grep -Ril "GEPA"` 一次命中
- 搜索 "regulatory constraints"：Agent 尝试 `grep` 多个近义词（regulat、compliance、constraints、GDPR、governance），也找到了结果——但需要进行多次工具调用

**这种方式的局限性：** 对于需要语义理解的查询，Agent 不得不多次 grep 枚举近义词。如果用户问"找关于动物超级英雄的电影"，Agent 得把所有动物都列出来搜一遍。

**解决方案：语义搜索替代 grep**——引入 `jina-grep-cli`（基于语义相似度的 CLI 搜索工具）

```bash
jina-grep -r --top-k 5 "memory leak" /data/session_data
```

**决定用 grep 还是 jina-grep 的规则：**
- 精确子串、已知文件名、简单列表 → 用 `grep` / `find` / `cat`
- 自然语言或模糊匹配 → 用 `jina-grep`

在 system prompt 中清晰描述两者的适用场景后，Agent 能正确选择工具，一次 `jina-grep` 调用就找到了 "regulatory constraints" 相关会话。

---

## 实用建议

### "Low floor, high ceiling" 的搜索工具组合

| 类型 | 特点 |
|------|------|
| **专用工具（low floor）** | 参数简单、失败率低、token 消耗少（如语义搜索、按 ID 查找） |
| **通用工具（high ceiling）** | 能处理边界情况，但可能需要更多轮迭代和更强的模型（shell、ES|QL） |

**理想状态是两者都要：** 专用工具覆盖常见查询，通用工具作为不速之客（long tail）的逃生出口。

### 如何演进你的工具栈

1. **已知查询模式** → 直接设计专用工具
2. **未知查询模式** → 从通用工具开始
3. **记录工具调用和错误日志**
4. **看到重复模式后添加专用工具**
5. 如果一个简单问题要调用 4-5 次工具，说明当前工具对模型来说太难了

> Ship, read traces, narrow with purpose-built tools instead of guessing APIs on day one.

---

## 总结

| 维度 | 方案一：语义搜索 | 方案二：DB 查询+Skills | 方案三：Shell+grep |
|------|---------------|---------------------|------------------|
| 复杂度 | 低 | 中 | 中高 |
| 精确关键词 | ❌ 不行 | ✅ 有技能后行 | ✅ grep 精准 |
| 语义模糊 | ✅ 好 | ✅ 好 | ⚠️ 需枚举近义词 |
| 聚合分析 | ❌ 不行 | ✅ ES|QL 统计 | ❌ 需后处理 |
| 模型要求 | 低 | 中 | 中 |
| 延迟 | 低 | 中（+skill loading） | 取决于命令数 |

没有银弹。上下文工程的核心不是选一个"最好"的搜索工具，而是**为你的 Agent 精心挑选一小撮匹配实际行为的工具**——并且随着你对查询模式的理解加深，持续迭代这个工具集。

---

**相关资源：**
- [Workshop 仓库](https://github.com/iamleonie/workshop-agentic-search)
- [Workshop 视频](https://www.youtube.com/watch?v=x2bH0RKPgdc)
- [The shell tool is not a silver bullet for context engineering](https://www.elastic.co/search-labs/blog/search-tools-context-engineering)
- [Building effective database retrieval tools for context engineering](https://www.elastic.co/search-labs/blog/database-retrieval-tools-context-engineering)
- AI Engineer Europe 2026 [日程数据集](https://www.ai.engineer/europe/schedule)

---

*整理于 2026-05-29，来源：Leonie Monigatti 博客*
