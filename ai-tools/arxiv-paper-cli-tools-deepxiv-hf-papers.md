---
title: "arXiv 论文阅读 CLI 工具指南：DeepXiv + HuggingFace hf papers"
tags:
  - arxiv
  - paper-reading
  - deepxiv
  - huggingface
  - cli-tools
  - ai-agents
  - research-tools
date: 2026-06-03
source: "https://toolin.ai/blog/deepxiv-arxiv-cli-tutorial & https://zhuanlan.zhihu.com/p/2023174807903052843"
authors: "toolin小编, Zhihu contributor"
---

# arXiv 论文阅读 CLI 工具指南：DeepXiv + HuggingFace `hf papers`

> **来源：** [DeepXiv：让AI Agent直接消费2亿篇论文的CLI工具](https://toolin.ai/blog/deepxiv-arxiv-cli-tutorial) + [HuggingFace 为 LLM Agent 做的读论文工具：`hf papers`](https://zhuanlan.zhihu.com/p/2023174807903052843)

如果你在做 AI 相关的研发，大概率每天都在和论文打交道。传统的论文阅读方式——打开网页、下载 PDF、手动翻页——对越来越依赖 AI Agent 辅助工作的开发者来说效率太低。

好消息是，现在有两个强大的 CLI 工具可以把论文从「给人看」升级为「给 Agent 用」：**DeepXiv**（智源研究院出品）和 **HuggingFace `hf papers`**。本文整合这两者的能力，帮你搭建完整的论文阅读工作流。

---

## 一、工具概览

| 维度 | DeepXiv | HuggingFace `hf papers` |
|------|---------|------------------------|
| **开发者** | 智源研究院 + 社区 | HuggingFace |
| **覆盖范围** | 2 亿+ 开放论文（全量 arXiv，每日增量） | arXiv + HuggingFace Hub 论文 |
| **安装方式** | `pip install deepxiv-sdk` | `pip install huggingface_hub` / `brew install hf` |
| **核心能力** | 搜索、渐进式阅读、热点追踪、深度调研 Agent | 搜索、列表、信息查询、全文阅读 |
| **Agent 友好** | CLI + Python SDK + MCP 协议 | CLI + `--format agent\|json` 输出 |
| **扩展中** | PMC、ACM、bioRxiv 等 | HuggingFace 生态（模型、数据集、Spaces） |
| **开源** | ✅ MIT | ✅ Apache 2.0 |

### 选择建议

- **需要深度调研 + Agent 自动化** → DeepXiv（内置 Agent 模式、MCP 协议、渐进式阅读）
- **需要融入 HuggingFace 生态** → `hf papers`（与模型、数据集、Spaces 一站式查询）
- **两者互补**：分别安装，根据场景选用对应工具

---

## 二、DeepXiv — 面向 Agent 的论文 CLI

### 2.1 安装

```bash
# 基础版
pip install deepxiv-sdk

# 完整版（含深度调研 Agent）
pip install "deepxiv-sdk[all]"
```

**资源链接：**
- GitHub: https://github.com/DeepXiv/deepxiv_sdk
- PyPI: https://pypi.org/project/deepxiv-sdk/
- API 文档: https://data.rag.ac.cn/api/docs
- 技术报告: https://arxiv.org/abs/2603.00084

### 2.2 核心命令

#### 搜索论文

```bash
# 基础搜索
deepxiv search "agent memory"

# 按时间过滤，限制数量，JSON 输出
deepxiv search "agentic memory" --date-from 2026-03-02 --limit 50 --format json

# 多近义词并行搜索，扩大召回范围
deepxiv search "memory agents long-horizon" --date-from 2026-03-02 --limit 50 --format json
```

搜索结果返回论文 ID、标题、摘要等结构化信息，方便后续处理。

#### 渐进式阅读（核心设计）

DeepXiv 的核心理念是**渐进披露**——先用最低成本判断论文价值，再按需深入阅读：

```bash
# 第一步：快速预览（最低 Token 消耗）
deepxiv paper 2602.16493 --brief
# 返回：标题、发表日期、引用数、PDF 链接、GitHub、关键词、TL;DR

# 第二步：查看整体结构
deepxiv paper 2602.16493 --head
# 返回：章节分布、各章节摘要 + Token 数

# 第三步：定点精读某个章节
deepxiv paper 2602.16493 --section "Experiments"
# 返回：解析后的 Markdown / JSON，Agent 可直接消费
```

这个三步走路径对应一个非常自然的文献阅读流程：**搜索候选 → 预览筛选 → 结构定位 → 定点精读**。每阶段 Token 消耗递增，可在任意阶段停下来。

#### 热点追踪

```bash
# 近 7 天热点论文
deepxiv trending --days 7 --limit 30 --json

# 查看单篇论文的社交媒体传播热度
deepxiv paper 2603.28767 --popularity
```

#### 深度调研 Agent 模式

```bash
# 一键执行完整调研链路：搜索 → 筛选 → 阅读 → 提取 → 归纳
deepxiv agent query "What are the latest papers about agent memory?" --verbose
```

#### 其他文献源支持

```bash
# PMC（PubMed Central）论文
deepxiv pmc PMC544940 --head
deepxiv pmc PMC544940
```

### 2.3 接入方式

| 方式 | 使用场景 |
|------|---------|
| **CLI** | 命令行直接使用，适合手动调研 |
| **Python SDK** | 集成到自定义 Agent / 代码中 |
| **MCP 协议** | 嵌入 Claude Code、OpenClaw 等支持 MCP 的 Agent 框架 |

### 2.4 MCP 接入示例

DeepXiv 提供 MCP Server，可作为工具注册到支持 MCP 协议的 Agent 框架中，让 Agent 直接搜索和阅读论文。适合将论文检索能力无缝集成到已有的 Agent 工作流。

### 2.5 核心优势

- **渐进披露设计**：Token 消耗精确控制，避免全量阅读浪费
- **批量筛选高效**：`--brief` + JSON 输出可一次过筛数十篇论文
- **Agent 原生友好**：输出已经是结构化格式（Markdown/JSON），无 PDF 解析烦恼
- **PMC 扩展**：不只 arXiv，正扩展到医学等更多文献源

---

## 三、HuggingFace `hf papers` — HuggingFace 生态中的论文工具

### 3.1 安装

```bash
# 方式一：独立安装器（推荐）
curl -LsSf https://hf.co/cli/install.sh | bash

# 方式二：pip
pip install -U huggingface_hub

# 方式三：Homebrew
brew install hf

# 方式四：uv（隔离环境，无需安装）
uvx hf
```

### 3.2 进化历程

`hf papers` 从最初只能列每日论文的简单命令，到 v1.8.0+ 版本已经进化成了完整的论文检索工具：

- **早期**：仅能列举每日 arXiv 论文
- **中期**：增加搜索、论文元信息查询
- **v1.8.0+**：支持全文阅读（`hf papers read`）、结构化 JSON 导出、Agent 专属输出格式

### 3.3 核心命令

#### 列出论文

```bash
# 默认列出最新论文
hf papers ls

# 按热度排序
hf papers ls --sort trending

# 按日期筛选
hf papers ls --date 2025-01-23
hf papers ls --week 2025-W09

# 按提交者筛选
hf papers ls --submitter akhaliq

# JSON 输出（方便后续处理）
hf papers ls --format json
```

#### 搜索论文

```bash
# 关键词搜索
hf papers search "vision language"
hf papers search "attention mechanism" --limit 10
hf papers search "diffusion" --format json
```

#### 论文信息查询

```bash
hf papers info 2601.15621
# 返回论文元数据：标题、作者、摘要、分类等
```

#### 全文阅读

```bash
hf papers read 2601.15621
# 直接返回论文全文，无需 PDF
```

### 3.4 Agent 友好输出格式

`hf` CLI 全系列支持 Agent 专属输出模式，`hf papers` 也不例外：

```bash
# Agent 模式（TSV 格式，无截断）
hf papers ls --format agent

# JSON 模式（结构化数据，方便 pipe 到 jq）
hf papers ls --sort trending --format json | jq '.[].id'

# Quiet 模式（仅输出 ID，一行一个）
hf papers search "agent" --limit 5 --quiet
```

这种输出设计使得 `hf papers` 可以无缝集成到 Agent 的工作流中——Agent 通过 `--quiet` 获取论文 ID，再逐个 `read` 获取全文，或者通过 `--format json` 获取完整元数据做进一步分析。

### 3.5 融入 HuggingFace 生态

`hf papers` 的一大优势是它融入了更广泛的 HuggingFace CLI 生态：

```bash
# 一套工具链完成：搜论文 → 查模型 → 跑推理
hf papers search "vision transformer" --limit 5 --format json
hf models ls --search "vit" --limit 10 --format json
hf spaces ls --search "vit-inference" --limit 5
```

### 3.6 核心优势

- **零额外安装**：有 `huggingface_hub` 或 `hf` CLI 即可使用，无需单独安装
- **HuggingFace 生态集成**：论文 ↔ 模型 ↔ 数据集 ↔ Spaces 一站式跳转
- **Agent 原生输出**：`--format agent|json|quiet` 满足各种自动化需求
- **社区驱动**：HuggingFace 社区活跃，论文更新及时

---

## 四、实战工作流：结合两条工具链

以下是一个完整的论文调研工作流示例，结合了 DeepXiv 和 `hf papers` 各自的优势：

### 场景：调研 AI Agent Memory 方向的前沿论文

```bash
# 阶段一：广度覆盖（DeepXiv 搜索 + 趋势）
deepxiv search "agent memory" --date-from 2026-01-01 --limit 30 --format json > candidates.json
deepxiv trending --days 14 --limit 20 --json >> candidates.json

# 阶段二：快速筛选（DeepXiv 渐进式预览）
cat candidates.json | jq -r '.[].id' | while read id; do
  deepxiv paper "$id" --brief --format json >> briefs.json
done

# 阶段三：交叉验证（hf papers 获取 HuggingFace 生态信息）
hf papers search "agent memory" --limit 10 --format json
hf papers info 2601.15621

# 阶段四：精读重点论文（DeepXiv 逐章阅读）
deepxiv paper 2601.15621 --head
deepxiv paper 2601.15621 --section "Method"

# 阶段五：深度调研（DeepXiv Agent 模式自动生成调研报告）
deepxiv agent query "Compare memory mechanisms in recent agent papers, create a baseline comparison table" --verbose
```

### 使用原则

| 环节 | 推荐工具 | 原因 |
|------|---------|------|
| **初始搜索 + 广撒网** | DeepXiv | 支持多近义词并行搜索，搜索范围大 |
| **快速筛选 + 渐进式阅读** | DeepXiv | 渐进披露设计，Token 消耗可控 |
| **热点追踪** | 两者均可 | DeepXiv: 社交热度 / `hf papers`: 社区热度 |
| **生态信息查询** | `hf papers` | 与 HuggingFace 模型、数据集、Spaces 联动 |
| **深度调研** | DeepXiv Agent | 全自动链路搜索 → 阅读 → 归纳 → 生成报告 |
| **代码层面集成到 Agent** | DeepXiv MCP | MCP 协议可直接注册为 Agent 工具 |
| **日常快速查阅** | `hf papers` | 零额外安装，`--format agent` 一键输出 |

---

## 五、进阶技巧

### 5.1 代理自动筛选

写一个简单的脚本让 Agent 自动筛选论文：

```python
# auto-screen-papers.py
import subprocess
import json

def search_deepxiv(query, limit=30):
    """搜索论文"""
    result = subprocess.run(
        ["deepxiv", "search", query, f"--limit={limit}", "--format=json"],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)

def screen_papers(papers, criteria_callback):
    """自动筛选手稿"""
    for paper in papers:
        # 用 brief 获取详细摘要
        result = subprocess.run(
            ["deepxiv", "paper", paper["id"], "--brief", "--format=json"],
            capture_output=True, text=True
        )
        meta = json.loads(result.stdout)
        if criteria_callback(meta):
            yield meta

# 使用
papers = search_deepxiv("agentic memory")
shortlisted = screen_papers(papers, 
    lambda m: "2026" in m.get("date", "") and "reinforcement" in m.get("abstract", "").lower())
```

### 5.2 与 Agent 框架集成（MCP）

在 Claude Code 或 OpenClaw 中注册 DeepXiv 为工具：

```bash
# DeepXiv 自动注册 MCP 工具
deepxiv mcp start
```

Agent 就可以直接调用 `deepxiv_search`、`deepxiv_read_paper` 等工具完成论文检索。

### 5.3 批量元数据导出

```bash
# DeepXiv - 批量导出 JSON
deepxiv search "agent" --limit 100 --format json > agent_papers_2026.json

# hf papers - 批量获取论文 ID
hf papers search "agent" --limit 50 --quiet | xargs -I{} hf papers info {} --format json
```

### 5.4 每日论文简报自动化

结合 cron 或 Agent 定时任务，每日自动拉取热点论文并生成简报：

```bash
#!/bin/bash
# daily-paper-brief.sh
DATE=$(date +%Y-%m-%d)
deepxiv trending --days 1 --limit 10 --format json > "/tmp/papers-$DATE.json"
echo "## 今日论文热点 ($DATE)" > "daily-brief-$DATE.md"
cat "/tmp/papers-$DATE.json" | jq -r '.[] | "- [\(.title)](\(.url)) — \(.tldr)"' >> "daily-brief-$DATE.md"
```

---

## 六、常见问题

### 数据覆盖范围
- **DeepXiv**：全量 arXiv，每日增量更新，正在扩展至 PMC、ACM、bioRxiv 等
- **`hf papers`**：arXiv + HuggingFace Hub 论文，遵循 HuggingFace 更新节奏

### 是否免费？
- 两者均开源免费使用

### 返回格式
- **DeepXiv**：Markdown + JSON
- **`hf papers`**：human / agent / json / quiet 四种格式

### Agent 集成哪种好？
- 已经用 Claude Code / OpenClaw → **DeepXiv MCP**（最直接）
- 已经用 HuggingFace 生态 → **`hf papers`**（零额外依赖）
- 两者互不冲突，建议同时安装

### 是否需要登录？
- **DeepXiv**：无需登录注册
- **`hf papers`**：查询论文无需登录，但部分高级功能需要 HuggingFace 账号

---

## 七、总结

DeepXiv 和 HuggingFace `hf papers` 从不同角度解决了论文阅读的 Agent 化问题：

- **DeepXiv** 更适合**需要深度调研场景**——它的渐进式阅读设计精确控制 Token 消耗，内置 Agent 模式可以串起全链路，MCP 协议让任何 Agent 框架都能直接调用
- **`hf papers`** 更适合**日常快速查阅 + HuggingFace 生态集成**——零额外安装、多种 Agent 输出格式、与模型/数据集/Spaces 无缝联动

两者是互补关系，并非竞争。理想的论文阅读工作流是：**用 DeepXiv 做深度调研，用 `hf papers` 做日常查阅和生态联动**。

---

*整理于 2026-06-03，来源：[toolin.ai](https://toolin.ai/blog/deepxiv-arxiv-cli-tutorial) + [知乎专栏](https://zhuanlan.zhihu.com/p/2023174807903052843)*
