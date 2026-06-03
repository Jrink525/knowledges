---
title: "Agentic Memory（智能体记忆）详解"
author: "Ram @techwith_ram"
source: "X/Twitter 长文"
date: 2026-03-27
url: "https://x.com/techwith_ram/status/2037499938574110770"
tags:
  - agentic-memory
  - llm-agents
  - vector-database
  - episodic-memory
  - chromadb
  - memory-management
category: "ai-agents"
description: "深入解析智能体记忆系统的核心概念——四种记忆类型、记忆在 Agent Loop 中的流转、向量数据库的作用、以及遗忘策略等实践建议。来源：techwith_ram 的 X 长文。"
---

# Agentic Memory（智能体记忆）详解

## 为什么记忆对 Agent 至关重要？

想象一下，你雇佣了一位才华横溢的自由职业者。第一天她令人惊叹——捕捉每一个 bug、写出干净的文档、甚至提出你没想到的改进建议。

第二天你走进来说："嘿，还记得昨天讨论的那个问题吗？"

她停住了。看着你。微微一笑。

"抱歉……什么问题？"

没有记忆。没有上下文。全部归零。

这正是大多数 LLM 的行为方式。每次新对话都是从头开始。模型不知道你是谁、你们一起构建了什么、甚至几分钟前在另一个聊天窗里讨论过什么。

对于简单的聊天机器人来说，这没问题。但对于 **Agent**——一个执行任务、做决策、随时间改进的系统——这种健忘症是致命的。

因为真正的智能不只是"能回答好"，更是**记住、学习、并在已有基础上构建**。记忆是把无状态系统变成真正能进化的东西的关键。

---

## 什么是 Agentic Memory？

Agentic Memory 不是一个单一组件，而是一个**幕后运行的系统**——包括不同类型的存储、信息检索方式、以及管理策略，让 Agent 能够跨时间承载上下文。

核心理解：记忆不是在做一个任务，而是在同时做三个截然不同的工作：

### 三大支柱

| 维度 | 作用 | 类比 |
|------|------|------|
| **Continuity（连续性）** | 关乎身份认同。Agent 知道你是谁、你的偏好、你们已经一起构建了什么。没有它，每次交互都像从零开始。 | 长期关系 |
| **Context（上下文）** | 关乎当前任务。刚刚发生了什么、用了什么工具、返回了什么结果、下一步该做什么。它是多步骤工作流不崩盘的保障。 | 短期工作台 |
| **Learning（学习）** | 关乎持续改进。理解什么有效、什么无效，逐步优化决策，而不是重复犯同一个错。 | 经验积累 |

三者结合，让 Agent 感觉**一致、可靠、每一次交互都比之前更聪明一点**。

---

## 四种记忆类型

业界已收敛到四种不同的记忆类型——就像大脑的四个不同部分，各自为特定任务演化而来。

### 1. In-context Memory（上下文记忆）

**类比：** Agent 的工作台（working desk）。

上下文窗口上的内容即刻可访问，模型可以在一次前向传播中直接推理，**无需检索步骤**。

**但工作台有大小限制：** 每个 token 都花钱花时间，会话结束时工作台被清空。

**上下文中包含什么？**
- **System prompt**：Agent 人格、规则、能力、当前日期/用户信息
- **对话历史**：当前会话的来回交互
- **工具调用结果**：Agent 刚调用的工具的输出
- **检索到的记忆**：从外部存储拉入的片段
- **草稿区（scratchpad）**：中间推理过程（think-step-by-step 输出）

#### 滑动窗口问题

在长对话中，历史积累最终会溢出上下文限制。粗暴地截断最旧的消息会丢失重要的早期上下文。更好的策略：

- **Summarization（总结）**：定期将旧轮次压缩为简短摘要，用摘要替换原文
- **Selective retention（选择性保留）**：保留包含关键事实、决策或工具结果的轮次，丢弃闲聊
- **Offload to external memory（卸载到外部记忆）**：将重要事实提取到向量存储中，需要时再检索

---

### 2. External Memory（外部记忆）

**类比：** 持久化的外部存储。超越会话边界，Agent 可以记住六个月前的事。

**两种风格：**

| 类型 | 技术 | 特点 |
|------|------|------|
| **Structured Store（结构化存储）** | PostgreSQL、Redis、SQLite | 按 key/ID/SQL 精确查询，快速可预测，适合用户画像、偏好、结构化数据 |
| **Vector Stores（向量存储）** | Pinecone、Chroma、pgvector | 按语义查询"找和这个概念相似的记忆"，对非结构化笔记和情景回忆至关重要 |

> ⚠️ **检索步骤是瓶颈。** 如果没有检索到正确的记忆，Agent 表现得就像它们不存在一样。好的记忆架构 = **20% 存储 + 80% 检索设计**。

---

### 3. Episodic Memory（情景记忆）

**最被低估的记忆类型。** 外部记忆存储"事实"（facts），而情景记忆存储"事件"（events）——**过去行动的结果**。

最简单的形式是一个结构化日志：每次 Agent 完成一个任务，它就记录发生了什么。随时间推移，这个日志成为丰富的自我知识来源，Agent 可以在做决策前查阅。

**一个"情景"长什么样：**

```
Episode {
  task: "分析第三季度销售数据"
  actions_taken: ["查询数据库", "生成图表", "编写摘要"]
  outcome: "成功 → 发现 15% 的增长异常"
  timestamp: "2026-03-27T14:30:00Z"
  metadata: { priority: "high", duration: "45s" }
}
```

当一个新任务进来时，Agent 检索语义上最相似的过去情景，用它们来**选择策略**。这本质上是从个人历史中进行 few-shot 学习，而非从手工构建的数据集中学习。

**反思循环：** `行动 → 记录结果 → 检索相似情景 → 调整策略 → 再次行动`

---

### 4. Semantic/Parametric Memory（语义/参数化记忆）

这是模型**天生携带的记忆**——训练时编码在权重中的一切：
- 关于世界的事实
- 语言模式
- 推理策略
- 编程惯例
- 文化知识

它始终存在，Agent 从不需要检索它。

**但有其硬限制：**

| 限制 | 说明 |
|------|------|
| ❄️ 训练时冻结 | 模型不知道 cutoff 日期后发生了什么 |
| 🔒 运行时不可更新 | 不重新训练/fine-tune 就无法注入新永久知识 |
| 👁️ 不透明 | 无法精确检查模型"知道"或不知道什么 |
| 💭 易产生幻觉 | 模型会用看似合理但错误的补全来填补空白 |

**正确的心智模型：** 参数化记忆是 Agent 的**通识教育**（general education）；外部记忆、情景记忆和上下文记忆是 Agent 的**在职经验**（on-the-job experience）。最好的 Agent 两者都用。

---

## 记忆在 Agent Loop 中的流转

每次 Agent 处理一个请求时，以下是完整的记忆流转：

```
输入请求
    ↓
① **检索**（Retrieval）
   - 从向量存储中拉取语义相关的过往记忆
   - 从情景日志中拉取相似历史任务
   - 写入 in-context 工作台
    ↓
② **推理**（LLM Call）
   - 利用 in-context 中的所有信息进行推理
   - 输出思考（scratchpad）、行动（tool calls）等
    ↓
③ **执行**（Action）
   - 调用工具、查询数据、生成内容
    ↓
④ **写入**（Storage）
   - 将本次行动记录为新的情景日志
   - 提取关键事实存入向量存储
   - 更新记忆评分用于后续遗忘策略
    ↓
返回响应
```

> 注意：记忆操作**夹住 LLM 调用的两端**——检索在调用之前，写在调用之后。模型本身是无状态的，**记忆系统赋予了它有状态、有感知的错觉**。

---

## 构建记忆层（实践）

### MemoryStore 类

处理写入记忆（含 embedding）和语义检索的核心类：

```python
import chromadb
from openai import OpenAI
import numpy as np

class MemoryStore:
    def __init__(self, collection_name="agent_memory"):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(collection_name)
        self.embed_client = OpenAI()  # 使用 embedding model
    
    def add_memory(self, text, metadata=None, memory_id=None):
        """写入记忆，自动生成 embedding"""
        embedding = self._embed(text)
        self.collection.add(
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata or {}],
            ids=[memory_id or str(hash(text))]
        )
    
    def retrieve(self, query, top_k=5):
        """按语义检索最相关的记忆"""
        query_embedding = self._embed(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return results['documents'][0]
    
    def _embed(self, text):
        resp = self.embed_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return resp.data[0].embedding
```

### EpisodicLogger 类

在 MemoryStore 之上添加情景日志层：

```python
from datetime import datetime
import json

class EpisodicLogger:
    def __init__(self, memory_store: MemoryStore):
        self.store = memory_store
    
    def log_episode(self, task, actions, outcome, metadata=None):
        episode = {
            "task": task,
            "actions": actions,
            "outcome": outcome,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        episode_text = json.dumps(episode)
        self.store.add_memory(
            text=episode_text,
            metadata={"type": "episode", "timestamp": episode["timestamp"]},
            memory_id=f"ep_{hash(task + str(datetime.utcnow()))}"
        )
    
    def retrieve_similar_episodes(self, task_query, top_k=3):
        return self.store.retrieve(task_query, top_k=top_k)
```

### 组合使用：带记忆的 Agent

```python
class MemoryEnhancedAgent:
    def __init__(self):
        self.memory = MemoryStore()
        self.episodes = EpisodicLogger(self.memory)
    
    def process(self, user_input):
        # 1. 检索相关记忆
        past_episodes = self.episodes.retrieve_similar_episodes(user_input)
        facts = self.memory.retrieve(user_input)
        
        # 2. 构建含记忆上下文的 prompt
        prompt = self._build_prompt(user_input, past_episodes, facts)
        
        # 3. LLM 推理
        response = llm_call(prompt)
        
        # 4. 记录本次交互
        self.episodes.log_episode(
            task=user_input,
            actions=["推理", "生成响应"],
            outcome="success" if response else "failed"
        )
        
        return response
```

---

## 向量数据库（核心基础设施）

它是任何正经记忆系统的心脏。不像 SQL 那样按精确匹配查询，它在高维空间中寻找向量的**最近邻**——这就是语义搜索的能力：找到概念上相关但可能**没有共享任何词汇**的记忆。

### 相似度搜索工作原理

1. 每条记忆被转为向量（OpenAI embedding 模型输出 **1,536 维**浮点数组）
2. 概念相似的文本产生**相似的向量**
3. 查询时，将查询转为 embedding，用**余弦相似度**找到最近的向量

### 向量数据库选型建议

| 阶段 | 推荐 |
|------|------|
| **本地开发** | ChromaDB |
| **已在用 PostgreSQL** | pgvector（零额外基础设施） |
| **大规模生产** | Pinecone 或 Qdrant |

---

## 记忆管理：遗忘策略

真实的记忆系统不只是**积累**，还要**策展**。不断增长、没有焦点记忆存储会随时间退化——检索变嘈杂、延迟上升、矛盾记忆混淆 Agent。

**需要遗忘策略。三种主要方法：**

### 1. 基于时间的衰减
旧记忆相关度低。通过组合**时效性 + 语义相关度**来评分记忆：

```
score = relevance × (1 - decay_rate)^age
```

### 2. 写入时重要性评分
存储记忆时，让模型对自己的输出进行**重要性评分**（如 1-10 分）。只存储高分项——在源头过滤噪音。

```python
def add_with_scoring(self, text, metadata=None):
    score = self._ask_model_to_score(text)  # LLM 自评重要性
    if score >= IMPORTANCE_THRESHOLD:
        self.add_memory(text, metadata)
```

### 3. 定期合并
运行一个定时任务（如每晚），将重复或高度相似的记忆合并为**一条规范摘要**。这类似于人类睡眠中记忆巩固的机制。

---

## 最后的话

最终，**记忆是让 AI 感觉不那么像工具、更像伙伴的关键**。

- 没有记忆：每次交互从零开始
- 有了记忆：Agent 能够理解、适应，并随时间持续改进

真正的能力不在于模型本身，而在于**你如何设计模型记住什么、忘记什么、以及如何使用这些信息**。

> 把记忆层建对，其他一切都会变得更聪明。

---

## 相关资源

- [MemGPT / Letta](https://github.com/letta-ai/letta) — 虚拟上下文管理
- [LangGraph](https://langchain-ai.github.io/langgraph/) — Agent 编排框架，内置持久化
- [CrewAI Memory](https://docs.crewai.com/core-concepts/Memory/) — CrewAI 的记忆系统
- [Anthropic Agentic Memory 相关文档](https://docs.anthropic.com/)
