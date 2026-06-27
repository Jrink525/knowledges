---
title: "GBrain 深度解析：Git 仓库里的 AI Agent 大脑"
tags:
  - agent
  - memory
  - knowledge-graph
  - open-source
  - gbrain
  - garrytan
date: 2026-06-27
source: "https://x.com/mem0ai/status/2070541048527609885"
authors: "Mem0 (In Context #14)"
---

# GBrain 深度解析：Git 仓库里的 AI Agent 大脑

> **来源：** [A Brain in a Git Repo: How GBrain Works](https://x.com/mem0ai/status/2070541048527609885) — Mem0 In Context #14

GBrain 是一个开源的 AI Agent 大脑系统，由 Y Combinator CEO Garry Tan 开发并于 2026 年 4 月开源。核心思想：**把 Agent 的知识存在你自己拥有的 Git 仓库的 Markdown 文件里**，而不是存在数据库里。

Garry 在生产环境中运行着 146,646 个页面、24,585 个人物、5,339 个公司节点的 GBrain，由 66 个 cron 作业自主维护，每天夜间自动合并和充实知识。

---

## 核心设计：Markdown 是唯一真相源

知识以 Markdown 文件形式存在一个普通的 Git 仓库（"brain repo"）中。GBrain 将该仓库同步到 Postgres 用于检索，删除操作在 git 中变为数据库中的软删除。

**这种设计带来的独特优势：**
- **可 Diffable** — 可以像 Pull Request 一样审查 Agent 学到的东西
- **版本控制** — 错误写入 = `git revert`
- **人类可读、用户拥有** — 文件在你的磁盘上、你的密钥下，而不是供应商的存储中

**双引擎架构：**

| 引擎 | 场景 | 说明 |
|------|------|------|
| PGLite | 个人使用（~50,000 pages） | Postgres 17 编译到 WebAssembly，进程内、零配置、2秒就绪 |
| Postgres + pgvector | 共享/大规模/多机器部署 | Supabase 或自托管 |

两者实现同一个 `BrainEngine` 接口（约 47 个操作），CLI 和 MCP server 从同一份源码生成。

---

## 知识图谱：零 LLM 调用的自连线图

这是 GBrain 最值得关注的设计。每次写入页面时，`put_page` 操作从 Markdown 中提取实体引用——Obsidian 风格的 wiki 链接 `[[wiki/people/bob]]` 和 typed-link 语法——然后写入图边。**只用正则表达式和字符串匹配，零 LLM 调用。**

边的类型：`attended`、`works_at`、`invested_in`、`founded`、`advises`、`mentions` 等。
数据存入 `links` 表（`from_page_id, to_page_id, link_type, context`），通过递归 SQL 遍历实现多跳查询。

### BrainBench 基准数据

| 模式 | P@5 | R@5 |
|------|-----|-----|
| 完整系统（图 + 向量 + 关键词） | **49.1%** | **97.9%** |
| 去掉图（仅向量 + 关键词） | 17.8% | — |
| 纯向量检索 | 10.8% | — |

> "图层贡献了 31 个百分点 P@5" — BrainBench v0.20.0

**为什么？** Agent 大脑面对的本质上是关系型查询："我投资的公司里谁在做 AI Agent？"这不是语义相似度能回答的，需要遍历边：这个人 `works_at` 那个公司，那个公司 `invested_in_by` 你，这个人 `mentions` agents。向量搜索对这些结构完全无感。

---

## 混合检索 + 合成层

GBrain 暴露两个检索动词：

### `gbrain search` — 返回原始页面，快速排序

底层是混合检索：
1. **查询扩展** — Claude Haiku 将查询扩展为多种改写
2. **向量搜索** — 1,536 维 OpenAI embeddings（text-embedding-3-large），HNSW cosine
3. **全文搜索** — Postgres `tsvector` + `pg_trgm` 模糊标题匹配
4. **融合** — Reciprocal Rank Fusion（1/(60 + rank)）+ 源优先提升 + 重排序
5. **去重** — 四层：按源、余弦相似度 > 0.85、每类型上限 60%、每页上限

### `gbrain think` — 合成回答，附引用 + 诚实声明

不返回块，而是**合成跨结果的答案，附带明确的源页面引用，以及诚实地说明大脑还不知道什么**。最核心的不同点：系统主动暴露自己的空白——过时页面、未引用的声明、矛盾、缺口。

---

## Dream Cycle：睡着时的知识固化

大脑如果只在请求时写入就会逐渐失准。GBrain 的解决方案是后台定时通过的"梦周期"。

- **调度模式**：cron 驱动的充实作业在用户低活跃时段运行
- **20+ 内置作业**：去重人物页面、修复引用、评估显著性、发现矛盾、准备次日任务
- **Garry 生产环境**：66 个 cron 作业
- **矛盾检测**：`gbrain eval suspected-contradictions` 对检索对采样，应用日期预过滤 + LLM 裁判，发现冲突

**成本纪律（v0.14.0+）**：确定性的 cron 工作（API 抓取、token 刷新、爬取写入）作为"shell jobs"运行，完全脱离 LLM gateway，零 token 消耗，约回收 60% gateway 开销。

---

## Brain vs Memory：这是大脑，不是记忆

GBrain 主动画了一条关键分界线：

| 维度 | 大脑（Brain） | 记忆（Memory） |
|------|-------------|---------------|
| 内容 | 世界知识、人/公司/交易/会议/概念 | Agent 如何运作：偏好、决策、工具配置、session 连续性 |
| 载体 | Markdown 文件（Git） | 分布式记忆存储 |
| 持久性 | git 保证 | 部分平台 Agent 重启后丢失 |
| 用途 | 关系型检索 | 操作连续性 |

GBrain 刻意不做记忆层的工作。它不是一个追踪你偏好或跨工具携带操作连续性的系统。它是一个 Agent 的**知识库**，不是 Agent 的**工作记忆**。

---

## 局限性

1. **文件即存储的假设**不是所有人都认同——Cloudflare 在 2026 年 4 月推出自己的 Agent Memory，主张"更紧密的摄取和检索管道优于给 Agent 原始文件系统访问"
2. **免费图的质量依赖链接纪律**——如果 Markdown 里没有 `[[wikilinks]]` 和 typed-link 语法，正则表达式就没东西可提取，写入混乱的页面就建立不好连接
3. **PGLite 是单写入器**——活跃的 MCP server 和 cron 竞争写入锁，这也是为什么扩展路径需要完整 Postgres

---

## 与 Mem0 的关系：互补

GBrain 持有**持久的、关系型的世界知识**（文件格式、用户拥有）。Mem0 持有**Agent 的操作记忆**（偏好、修正、跨 session 的连续性）。

一个让你的**知识保持锐利**，另一个让你的**Agent 保持一致**。有趣的生产系统会同时运行两者。

---

## 参考资料

- [garrytan/gbrain](https://github.com/garrytan/gbrain) — GitHub README
- [GBrain v0 architecture doc](https://github.com/garrytan/gbrain) — 架构文档
- [GBrain skillpack doc](https://github.com/garrytan/gbrain) — Skillpack 文档
- [GBrain brain-vs-memory guide](https://github.com/garrytan/gbrain) — 大脑 vs 记忆指南
- [BrainBench v0.20.0](https://github.com/garrytan/gbrain) — 基准测试
- [Vectorize: GBrain review](https://vectorize.io) — 独立评估
- [Cloudflare: Agent Memory (April 2026)](https://blog.cloudflare.com) — 另一条技术路线的选择
- [Mem0](https://mem0.ai) — 开源记忆层

---

*整理于 2026-06-27，来自 Mem0 In Context #14 文章*
