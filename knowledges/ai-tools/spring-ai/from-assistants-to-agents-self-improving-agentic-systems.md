---
title: "从助手到智能体：基于 Spring AI 的自改进 Agentic 系统"
source: "https://youtu.be/_ZZuzakjgxQ"
author: "Christian Tzolov"
event: "Spring I/O"
date: 2025-05-27
tags:
  - Spring AI
  - Agent
  - LLM
  - AdvisorPattern
  - ToolCalling
  - MCP
  - RAG
  - StructuredOutput
  - Java
category: "ai-tools/spring-ai"
---

# 从助手到智能体：基于 Spring AI 的自改进 Agentic 系统

> **演讲者：** Christian Tzolov（Spring AI 核心贡献者）
> **活动：** Spring I/O 2025
> **时长：** 51:50

## 概述

本演讲从 LLM 的"黑盒"本质出发，系统性地展示了如何通过 Spring AI 的 **Advisor（拦截器）模式**，从简单的 LLM 调用一步步演进到复杂的自改进 Agentic 系统。核心论点是：**几乎所有 Agent 模式都可以用「Advisor + 工具支持」这两个基础构件组合出来。**

演讲覆盖了从 Chat Memory → RAG → Structured Output → Tool Calling → MCP → Judge LLM 自改进循环 → 渐进式工具暴露 → Agent Skills → To-Do Right → Clarification Questions → Sub-Agents 的完整演进路径。

---

## 1. LLM 的本质：有状态幻觉的永久循环

| 特性 | 含义 |
|------|------|
| **无状态** | 每次调用独立，不记忆历史 |
| **预训练截止** | 知识有截止日期，无法感知实时信息 |
| **非结构化输出** | 默认只返回文本，缺乏格式保证 |
| **确定性不足** | 相同输入可能产生不同输出 |

因此，任何有价值的 AI 系统本质上都是一个 **relentless loop**：发送请求 → 检查输出 → 修正 → 再试 → ... 直到得到可接受的响应。

---

## 2. 核心概念：Advisor（拦截器）模式

这是整个演讲的基石——**你必须记住的最重要的概念**。

```java
// Advisor：一个可以插在 LLM 交互路径上的代码块
// 拦截并增强 LLM 的输入和输出
public interface Advisor {
    void around(LLMRequest request, LLMResponse response);
}
```

类比：
- Web 背景的开发者 → 像 **Filter** 或 **Interceptor**
- AOP 背景 → 像 **Around Advice**
- 函数式背景 → 像 **Middleware**

**为什么是 Advisor？** 所有 LLM 交互模式（记忆、RAG、结构化输出、工具调用、自我改进……）本质都是：**拦截输入，增强它；拦截输出，检查并决定下一步。** Advisor 就是做这个的统一抽象。

---

## 3. 演进路径：从助手到智能体

### 3.1 Chat Memory（聊天记忆）

最简单的 Advisor 应用。拦截每次 LLM 调用的输入/输出，将历史对话存储/检索，实现多轮对话。

```
用户提问 → [Memory Advisor 注入历史] → LLM → [Memory Advisor 存储响应] → 返回用户
```

Spring AI 2.0 引入了新的 session ID 实现，但底层原理相同。

---

### 3.2 RAG（检索增强生成）

同样是 Advisor 模式：在发送给 LLM 前，从外部存储（向量数据库、图数据库、全文搜索等）检索相关上下文并注入。

```
用户提问 → [RAG Advisor 检索文档 + 注入上下文] → LLM → 返回
```

> Spring AI 的 RAG 支持由 Thomas Vitali 贡献，非常完善。

---

### 3.3 Structured Output（结构化输出）

LLM 默认输出非结构化文本。Spring AI 通过 Advisor 实现结构化输出：

1. 自动将 Java 类型转换为 JSON Schema
2. 注入到 LLM 上下文中，要求按格式输出
3. 解析响应，若不符合 Schema → **自动重试**

**两层保障：**
- **Provider 原生支持**（如 OpenAI Structured Output API）— 优先使用
- **Fallback 机制** — 若不支持，退回到注入 JSON Schema + 重试

```java
// 声明结构化输出类型
record ActorFilms(String actor, List<String> movies) {}

// 使用结构化输出 Advisor
ChatClient.create(chatModel)
    .advisors(new StructuredOutputAdvisor())
    .call(ActorFilms.class, "Generate filmography for Tom Hanks");
```

> 重要：结构化输出 Advisor 会在输出不符合 Schema 时，将错误信息作为反馈发回 LLM 重新生成——**99% 的情况第二次就成功了**，而且用户完全无感知。

---

### 3.4 Tool Calling（工具调用）

这是第二个最重要的概念。LLM 预训练时被教会：如果上下文中包含工具的元数据（名称、描述、参数），它可以在需要时 **发送特殊的工具调用消息** 而不是最终响应。

**Spring AI 的工具定义：**

```java
@Tool(description = "获取实时天气")
public String getWeather(String location) {
    return weatherService.fetch(location);
}
```

**流程：**
1. 注册工具描述到上下文
2. LLM 决定需要工具 → 发送 Tool Call 消息
3. Tool Call Advisor 拦截 → 调用实际工具
4. 工具结果放回上下文 → LLM 生成最终响应

> 历史教训：Spring AI 早期将工具调用实现在 Chat Model 的底层，导致无法观察和拦截。现在重构为 Advisor，**可观察、可插拔、可组合**。

---

### 3.5 MCP（Model Context Protocol）工具

MCP 是标准化的工具调用协议。Spring AI 同时支持：
- **Java @Tool 注解**（简单场景）
- **MCP 服务器**（标准化、生态互通）

> MCP 服务器非常容易让工具集膨胀——一个 GitHub MCP 服务器可能暴露几百个工具，上下文会被大量工具定义占满。这就引出下一个模式。

---

### 3.6 Progressive Tool Disclosure（渐进式工具暴露）

**问题：** 几百个工具的定义全部塞入上下文 → 浪费 token + LLM 难以抉择。

**解决方案：工具搜索工具（Tool Search Tool）**

```java
@Tool(description = "如果你需要额外信息来完成任务，请使用此工具搜索可用工具")
public List<Tool> searchTools(String userIntent) { ... }
```

**流程：**
1. 启动时只注册一个"工具搜索工具"
2. LLM 需要信息时 → 调用此工具
3. 根据用户意图从本地搜索引擎（向量、Lucene、甚至正则）检索相关工具
4. 动态注册找到的工具到 LLM 上下文
5. LLM 再调用具体工具完成任务

**效果：** 相比一次性注入所有工具，**token 消耗降低 50%**。

> 该模式将在 Spring AI 2.0 中正式发布（演讲时处于 community 版本）。

---

### 3.7 Self-Improving Loop（自改进循环 / Judge LLM）

用另一个 LLM（通常是专用的小型 Judge 模型）来评估主 LLM 的输出质量。

```
LLM 响应 → [Judge LLM 检查是否回答用户问题] 
  ├── 是 → 返回给用户
  └── 否 → [注入原问题 + Judge 反馈] → LLM 重新生成 → 循环
```

```java
// 代码层面：又是一个 Advisor
chatClient.advisors(new SelfRefineAdvisor(maxAttempts=3));
```

**关键点：**
- Judge LLM 通常使用 **更小、更专注的微调模型**
- Hugging Face 提供 [Judge 模型排行榜](https://huggingface.co/spaces/guardrails/evaluation-leaderboard)
- 缺陷的代价是**额外延迟**（每次循环多一次 LLM 调用）

**Demo：** 故意让天气工具 2/3 的概率返回错误数据，Judge LLM 检测到后自动重试——即使多次尝试仍失败，也展示了模式的可行性。

---

### 3.8 Agent Skills（技能系统）

将 Agent 能力模块化为可加载的 **Skills（技能）**，每个 skill 是一个 markdown 文件：

```yaml
name: youtube-transcriber
description: 转录 YouTube 视频并总结
scripts:
  - transcriber.py
files:
  - template.md
```

Skill 可以包含：
- **Markdown 文件**（LLM 会阅读）
- **脚本**（LLM 通过 bash 工具执行）
- **元数据**（名称、描述、标签）

Spring AI 的 Agent Skills 完全兼容 [OpenAI 的 Skill 格式](https://platform.openai.com/docs/assistants/tools)，可以跨模型使用（Anthropic、OpenAI、Google、Bedrock 等）。

> 演讲 Demo：让 Agent 使用 youtube-transcriber skill → 调用 bash 运行 Python 转录脚本 → 编译 JavaScript → 回答"用简单术语解释强化学习"——**在同一个机器上执行真正的代码，非常令人印象深刻但也让人害怕。**

---

### 3.9 To-Do Right（任务清单模式）

**问题：** 复杂多步任务中，LLM 容易迷失方向、跳过步骤或执行顺序混乱。

**解决方案：** 强制 LLM 在开始时创建结构化待办清单，每个任务有生命周期：

```
PENDING → IN_PROGRESS → COMPLETED
```

核心规则：
- 一次只执行一个步骤
- 前一步未完成不得进入下一步
- 每个步骤更新清单状态

```java
// 又是一个工具！配合 Memory Advisor
chatClient
    .advisors(new TodoAdvisor(), new MemoryAdvisor())
    .tools(new ManageTodoTool())
    .call("Plan my trip to Europe");
```

> 灵感来源：Claude Code（Anthropic 的编码助手）的实现。有趣的是，Claude Code 最新版已弃用此模式，改为更高级的任务管理机制——但思路相同。

---

### 3.10 Clarification Questions（澄清问题）

**问题：** LLM 倾向于做出假设性判断（opinionated），一旦错了很难纠正。

**解决方案：** 注册一个"提问工具"，指示 LLM 不确定时先向用户澄清：

```java
@Tool(description = "如果不确定如何继续，或有多个选择，不要自行假设——先向用户询问细节。支持多选和自由文本")
public String askUser(String question, List<String> options) { ... }
```

> Spring AI 提供命令行默认 Handler；自定义 UI 框架需自己实现 Handler。

---

### 3.11 Sub-Agents（子智能体）

**问题：** 复杂任务产生大量中间步骤，**污染主 Agent 的上下文**，降低推理质量。

**解决方案：** 将子任务放在**隔离的上下文**中执行，只返回结果。

```yaml
# 子任务定义（同样是 markdown）
---
name: code-review
model: gpt-4o-mini  # 可以用更小、更快的模型
description: Review generated code for bugs
---
Analyze the following code for...
```

```java
// Sub-agent 底层也是一个 Tool
chatClient.tools(new SubAgentTool());
```

**特性：**
- 子任务运行在**独立上下文**
- 可以使用**不同的模型**（如小模型做简单任务）
- 主 Agent 只拿到最终结果
- 支持本地和远程 Agent 定义

---

## 4. 总结：一切皆 Advisor

演讲最后的架构总结：

```
所有 Agent 模式 = Advisor（拦截增强） + Tool Support（工具执行）
                                   ↑
                           唯一的例外是 Todo Advisor
                           （也需要工具执行能力）
```

**Advisor 顺序至关重要：**

```
[CORRECT]  ToolCallAdvisor → MemoryAdvisor → LLM
                            ↑
                   Memory 记住的是请求前 + 工具调用后的完整上下文

[WRONG]     MemoryAdvisor → ToolCallAdvisor → LLM
                   Memory 只记住原始请求和最终响应，丢失中间工具调用
```

---

## 5. 知识关联

### 本演讲在 Spring AI 生态中的位置

本演讲聚焦于 Spring AI 的 **Advisor 模式和 Agent 模式的系统演进**，与其他资源互补：

| 关联文档 | 关联点 |
|---------|--------|
| `spring/ai-agent/dan-vega-spring-ai-full-course-notes.md` | Dan Vega 5h+ 全栈课程，含 RAG、MCP、可观测性、评估，**偏实操入门** |
| `spring/ai-agent/josh-long-spring-ai-workshop-notes.md` | Josh Long & James Ward Agent Workshop，**Bedrock + MCP 集成** |
| `spring/bootiful-spring-ai-josh-long-springio-2026.md` | Josh Long Spring I/O 2026 演讲，**从零构建生产级 AI Agent** |
| `ai-tools/frameworks/springio-2026-comparing-agentic-ai-frameworks-for-java.md` | Java Agentic AI 框架对比（Spring AI vs LangChain4j vs Embabel） |
| `ai-tools/frameworks/spring-ai-bedrock-agentcore-mcp-conference-app.md` | Spring AI + Bedrock + AgentCore + MCP 会议应用实战 |
| `spring/ai-agent/spring-ai-agent-resources-top30.md` | Spring AI Agent 资源 Top 30 汇总 |
| `ai-tools/ml-research/binary-quantization-rag-32x.md` | RAG 检索基础设施（向量存储 + 二值量化），与本文 RAG Advisor 互补 |

### 归类建议

本文的核心在于 **Advisor 模式的理论框架**，属于架构层。建议与 `dan-vega-spring-ai-full-course-notes`（实操入门）和 `josh-long-spring-ai-workshop-notes`（Bedrock 生产环境）配合阅读：
1. 先读 Dan Vega — 掌握 Spring AI 基础操作
2. 读本文 — 理解 Advisor 模式和 Agent 演进逻辑
3. 读 Josh Long — 看生产级部署和 Bedrock 集成
