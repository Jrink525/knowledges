---
title: "从助手到智能体：基于 Spring AI 的自改进 Agentic 系统（完整实录）"
source: "https://youtu.be/_ZZuzakjgxQ"
author: "Christian Tzolov (Spring AI 核心贡献者, VMware)"
event: "Spring I/O 2025"
date: 2025-05-27
tags:
  - Spring AI
  - Agent
  - AdvisorPattern
  - ToolCalling
  - MCP
  - RAG
  - StructuredOutput
  - SpringAI2.0
  - JudgeLLM
  - ProgressiveDisclosure
  - AgentSkills
  - SubAgents
  - TodoRight
category: "ai-tools/spring-ai"
---

# 从助手到智能体：基于 Spring AI 的自改进 Agentic 系统（完整实录）

> 演讲人：**Christian Tzolov**（Spring AI 核心贡献者）
> 活动：Spring I/O 2025
> 时长：51:50
> [观看视频](https://youtu.be/_ZZuzakjgxQ)
>
> 本文为视频字幕完整整理版，包含所有代码示例、Demo 过程及演讲者原话。

---

## 一、开场与核心认知

### 1.1 演讲者引子

Christian 开场引用了一篇近期博客（Raphael 的文章），指出一个很多人已经意识到但仍在消化的现实：

> "当我们谈论生成式 AI 时，它其实不是关于训练模型，而是关于如何使用这个模型——像一个黑盒，或者像你可以使用它的智能。"

### 1.2 LLM 作为黑盒的五大特征

| 特性 | 原文 | 工程含义 |
|------|------|---------|
| **无状态（Stateless）** | "Statelessness is one of the most important bits." | 每次调用独立，不记忆历史 |
| **预训练截止** | "Those models have been pre-trained up to some point in the past." | 知识过时，无法感知实时信息 |
| **非结构化输出** | "Text in, text out, non-structured response." | 默认只返回自由文本 |
| **非确定性（Non-deterministic）** | "They're creative, but also they can be hallucinating." | 同样输入不同输出，可能幻觉 |
| **有限上下文** | "Limited amount of data that we can get in and get out in a single pass, single turn. It's measured in tokens." | Token 窗口限制 |

### 1.3 基本循环（The Relentless Loop）

> "You're going to pass and use LLM, send the context, get some feedback, try to improve it, and loop over until you get the response that you expect to be useful for you. And it's kind of a relentless loop to get there."

**这就是所有 AI 系统的本质原型：**
```
发送请求 → 检查输出 → 修正 → 再试 → ... → 直到可接受
```

---

## 二、Chat Memory Advisors（聊天记忆拦截器）— Demo 1

### 2.1 理论：有状态从拦截开始

由于 LLM 无状态，要构建有状态对话，需要：

1. **拦截（Intercept）** 发送给 LLM 的请求
2. 将问题写入某种**存储**
3. 发送给 LLM 的**不是问题本身**，而是问题 + 从先前对话中检索到的历史
4. **拦截输出**，将响应追加到对话历史

### 2.2 Advisor 概念（整场演讲的基石）

> "This is the typical concept of interceptor or advisor or hooks you can think of. It's nothing new — or filters if you're coming from the web background."

```java
// 概念层面：Advisor 就是一个可以插在 LLM 交互路径上的代码块
// 拦截并增强 LLM 的输入和输出
// 核心思想：intercept the input and output of your black box
```

**类比：**
- **Web 背景** → Servlet Filter
- **Spring 背景** → HandlerInterceptor
- **AOP 背景** → Around Advice
- **函数式背景** → Middleware

### 2.3 代码 Demo：Chat Memory

**不插 Advisor（无记忆）：**
```java
// 用户：自我介绍，然后问"我叫什么？"
ChatClient chatClient = ChatClient.create(chatModel);

// 第一轮
chatClient.call("Hi, my name is Christian.");
// → 正常回复

// 第二轮
chatClient.call("What's my name?");
// → "I don't know." 
// 因为无状态！
```

**插入 Memory Advisor（有记忆）：**
```java
ChatClient chatClient = ChatClient.builder(chatModel)
    .advisors(new MessageChatMemoryAdvisor(chatMemory))  // <-- 关键一行
    .build();

// 第一轮
chatClient.call("Hi, my name is Christian.");
// → 正常回复

// 第二轮
chatClient.call("What's my name?");
// → "Your name is Christian." ✅
```

**一句话总结：** "All you have to do is to put this advisor — memory advisor — in your path."

> **演讲者注：** Spring AI 2.0 正在孵化新的 session ID 实现，但底层原理相同。

---

## 三、RAG（检索增强生成）— Demo 2

### 3.1 问题：LLM 不知道你的领域知识

> "LLM has been pre-trained up to some point in the past. You're supposed to pass some additional context that would inform the LLM how to answer your question in this particular domain of knowledge."

### 3.2 方案：Context Stuffing / RAG

有两种方式注入知识：

| 方式 | 适用场景 | 限制 |
|------|---------|------|
| **直接注入静态文件** | 信息量小、可放入上下文 | Token 窗口限制 |
| **外部存储检索** | 信息量大 | 需要向量存储/语义搜索 |

**外部存储类型（演讲中列举）：**
- 常规数据库（Regular Databases）
- 图数据库（Graph Databases）
- 全文搜索（Full Text Search）
- 向量存储 + Embedding（最常用）

### 3.3 RAG 的底层模式：还是 Advisor

> "The way to handle this under the service — again the same pattern."

```java
// 最朴素的 RAG 实现
ChatClient chatClient = ChatClient.builder(chatModel)
    .advisors(new QuestionAnswerAdvisor(vectorStore))  // RAG Advisor
    .build();
```

**流程：**
1. 拦截用户输入
2. 用用户问题作为查询，从向量库检索最相似的文档块
3. 将检索到的文档注入上下文
4. 发送给 LLM
5. LLM 基于注入的上下文回答问题

### 3.4 重要观点：RAG 是非 Agentic 的

> "We are doing this injection or stuffing up front before consulting the LLM. We're trying to be smart — we're trying to figure out what is the most important piece of information related to this context judging only by the user question... We are doing this **without consulting the LLM**. It's not agentic in that sense."

---

## 四、Guardrails：敏感词过滤 — Demo 3

在进入结构化输出之前，演讲快速展示了一个简单的**输入保护**示例。

### 4.1 场景

> "You would like to prevent sending sensitive words to your LLM — passwords or some additional information that should not get out of the realm of your enterprise."

### 4.2 实现：敏感词检测 Advisor

```java
// 拦截输入 → 检查是否包含敏感词
// 如果包含：直接拦截，中止通信
// 如果不包含：放行到 LLM
```

**演讲者说这是个"very simplistic example"——用来展示在真正进入 LLM 之前可以做什么。**

---

## 五、Structured Output Advisor（结构化输出）— Demo 4

### 5.1 问题：LLM 输出非结构化文本

> "Text in, text out, unstructured. But with Spring AI, you can support structured and enforce structured response on different levels."

### 5.2 最简单的实现方式

```java
// 定义期望的数据类型（Java Record）
record ActorFilms(String actor, List<String> movies) {}

// 直接通过泛型要求结构化输出
ChatClient.create(chatModel)
    .call()
    .entity(ActorFilms.class, "Generate filmography of 5 movies for Tom Hanks");
```

**底层机制：**
1. Spring AI 自动将 `ActorFilms.class` 转换为 JSON Schema
2. 注入到 LLM 上下文中，要求按格式输出
3. 解析响应为 `ActorFilms` 对象
4. 如果不符合 Schema → 抛出转换错误

**1% 的失败率问题：**
> "In this 1% where actually the LLM does not provide the right format, the user is going to see an error message itself. The JSON doesn't comply with the schema."

### 5.3 解决方案：Structured Output Advisor（自动重试）

```java
ChatClient chatClient = ChatClient.builder(chatModel)
    .advisors(new DocumentStructuredOutputAdvisor())  // <-- 自动处理和重试
    .build();

ActorFilms films = chatClient.call()
    .entity(ActorFilms.class, "Generate filmography of 5 movies for Tom Hanks");
```

**工作原理（核心亮点）：**
1. 拦截输出，检查是否符合 JSON Schema
2. 如果不符合 → 将错误信息作为**反馈**放回上下文
3. **重新发送给 LLM 要求修正**
4. "Most of the time, the second attempt is successful."
5. 可配置最大重试次数

> 最关键的是：**这一切发生在用户无感知的情况下** —— "happening without the involvement of the user explicitly."

### 5.4 Spring AI 2.0 新增：Provider 原生结构化输出

> "This is a new addition to Spring 2.0. You can opt for the structured output native format. Many AI models nowadays started to provide this capability of structured output built into their APIs."

```java
// 如果 Provider 支持原生结构化输出
ChatClient.create(chatModel)
    .call()
    // Advisors 会自动优先使用 Provider 原生 API
    // 如果不支持则回退到 Schema 注入方式
```

**Spring AI 的策略：**
1. 检查 Provider 是否支持原生结构化输出 API
2. 如果支持 → 使用 Provider API
3. 如果不支持 → 回退到 JSON Schema 注入方式
4. 两种情况下，如果响应不满足 Schema → 使用 Advisor 重试

---

## 六、Self-Refine Advisor（自改进 / Judge LLM）— Demo 5

### 6.1 理念升级：从确定性判断到 LLM 判断

前一个 Advisor（Guardrails）是用**确定性逻辑**（deterministic logic）检查输出。现在是：

> "This one uses LLM. It does guardrails on the output — but actually you can use another LLM to check the correctness of the response for the first one and make some action."

### 6.2 架构

```
LLM 响应 → [Judge LLM 检查是否回答用户问题]
  ├── 是 → 返回给用户
  └── 否 → [注入原问题 + Judge 反馈] → LLM 重新生成 → 循环
```

**关键术语：**
- **Judge LLM**：用于评估主 LLM 输出质量
- **Feedback Loop**：错误信息作为上下文反馈重新输入
- **Structured Response for Judge**：Judge LLM 的输出也要结构化（yes/no + 改进建议）

### 6.3 Judge LLM 的选择

> "Most of the time, you're going to use a dedicated smaller fine-tuned judge LLMs, which are trying to not be that biased and can support ranges."

**推荐来源：**
- Hugging Face 提供 [Judge 模型排行榜](https://huggingface.co/spaces/guardrails/evaluation-leaderboard)

### 6.4 代码实现

```java
// 自改进 Advisor — 同样是可插拔的 Advisor
ChatClient chatClient = ChatClient.builder(chatModel)
    .advisors(new SelfRefineAdvisor(3))  // 最多尝试 3 次
    .tools(new WeatherTool())            // 注册天气工具
    .build();
```

### 6.5 Demo 演示：故意制造错误数据

Christian 设计了一个精巧的 Demo：

```java
// 天气工具故意在 2/3 的情况下返回错误数据
@Tool(description = "获取实时天气信息")
public String getWeather(String location) {
    if (Math.random() < 0.67) {  // 2/3 概率
        return "Temperature: -15°C";  // 不合理数据
    }
    return fetchActualWeather(location);  // 真实数据
}
```

**Demo 过程（演讲原话还原）：**

1. **第一次尝试**："We were lucky — we have a negative temperature. The judge LLM is going to detect this response and before returning to the user, it's going to try again."
2. **第二次尝试**："Even the second attempt was unsuccessful."
3. **第三次尝试**："Hopefully the third one would be successful. No."
4. **结果**：最多 3 次尝试失败，最终返回错误信息

> "But you get the idea. It's trying and it's doing all this on behind. What you are paying as a user is additional latency and more loops that go back and forth."

---

## 七、The Evolution：Prompt → Context → Harnessing

### 7.1  Spring AI 三年的演进史

**Three years ago — Prompt Engineering：**
> "We were discussing about prompt engineering. That was the big thing."

**Then — Context Engineering：**
> "Over time, it was realized it's not about the text. It's about the whole metadata that gets to the model. So, we started to talk about context engineering."

**Now — Harnessing / Agent 时代：**
> "Everything that's not the LLM is harnessing. Officially, Spring AI is a harnessing framework as well."

### 7.2 Advisor 是 Harnessing 的优雅实现

> "The advisor is a very elegant way that you can provide harnessing logic into your existing pipelines."

---

## 八、Tool Calling Advisor（工具调用）— Demo 6

### 8.1 理论：为什么工具调用是第二个最重要的概念

> "This may be the second important concept that you should take away from here."

大多数现代 LLM 被预训练为：如果你在上下文中放入工具元数据（函数名称 + 描述 + 参数 Schema），LLM 可以在需要时**发送特殊的工具调用消息**（而不是直接返回文本）。

**工具元数据的三要素：**
1. **工具名称**：如 `getRealTimeWeather`
2. **工具描述**：决定 LLM 何时使用该工具的关键
3. **参数 Schema**：JSON Schema 格式，LLM 自动填充参数值

### 8.2 历史教训：最初实现在错误的位置

> "Historically, it was in Spring AI implemented in very low layer into the chat model, which made it almost impossible to perceive and observe what's going on."

**问题：** 如果实现在 Chat Model 内部，你无法：
- 观察什么工具被调用了
- 拦截工具调用过程
- 自定义工具行为

**重构结果：** Tool Calling 被重做为 Advisor — 可观察、可插拔、可组合。

### 8.3 Tool Calling 的完整流程

```
1. 注册工具定义到上下文
2. LLM 决定需要工具 → 发送 Tool Call 消息
3. Tool Call Advisor 拦截输出
4. 检查输出是否包含 Tool Call 消息
5. 如果是 → 通过 Tool Call Manager 分发
6. 调用实际工具 → 获取结果
7. 将结果放回上下文 → LLM 重新生成响应
```

### 8.4 代码实现

**方式一：注解方式（最常用）**
```java
@Tool(description = "获取实时天气信息")
public String getRealTimeWeather(String location) {
    return weatherService.fetch(location);
}
```

**方式二：Java 函数方式**
```java
// 直接作为 Tool Function
ToolCallback weatherTool = ToolCallbacks.from("getRealTimeWeather", 
    "获取实时天气预报",
    weatherService::fetch);
```

**方式三：MCP 工具**
```java
// 如果是 MCP 服务器暴露的工具
// 原则相同：都是工具
```

### 8.5 Demo：两个地点的天气查询

**问题：** "What should I wear today in Amsterdam and Barcelona?"

**期望行为：** LLM 应发出**两次** Tool Call，分别查询两个地点的天气。

```java
@Tool(description = "获取实时天气信息")
public String getRealTimeWeather(String location) {
    return weatherService.fetch(location);
}

ChatClient chatClient = ChatClient.builder(chatModel)
    .tools(new WeatherTool())
    .build();

// 单个工具，但 LLM 自动根据参数决定调用两次
chatClient.call("What should I wear today in Amsterdam and Barcelona?");
```

**Demo 结果：**
1. LLM 发出两次 Tool Call：`getRealTimeWeather("Amsterdam")` 和 `getRealTimeWeather("Barcelona")`
2. Spring AI 自动分发、解析、获取结果
3. 返回给 LLM 后生成最终建议

> The focus is not about how tool calling works. It's about that we're using **the same principle** (Advisors) to implement these capabilities.

### 8.6 多个 Advisor 组合时的注意事项：顺序问题

> "When you start mixing and matching and combining multiple advisors like memory and tool calling, you have to be mindful about this detail."

```java
// 正确顺序
ChatClient.builder(chatModel)
    .advisors(new ToolCallAdvisor(), new MessageChatMemoryAdvisor())
    .build();
// ToolCallAdvisor 在外层 → Memory 记住的是请求前 + 工具调用后的完整上下文

// 错误顺序
ChatClient.builder(chatModel)
    .advisors(new MessageChatMemoryAdvisor(), new ToolCallAdvisor())
    .build();
// Memory 只记住原始请求和最终响应 → 丢失中间工具调用信息
```

---

## 九、Progressive Tool Disclosure（渐进式工具暴露 / Tool Search Tool）— Demo 7

### 9.1 问题：工具定义膨胀

> "If you have used MCP servers, it's very easy to overload your system with only tool definition. If you just use only the GitHub MCP server, you'll end up with a few hundred tools."

**两个核心问题：**
1. **LLM 难以抉择**："It's very difficult for the LLM to dispatch which tool to use among hundreds."
2. **Token 浪费**："You're wasting a lot of context because you're passing back and forth a lot of metadata that you might never need."

### 9.2 背景：传统 RAG 预过滤方案的缺陷

> "Historically, people have been trying to use RAG-like techniques using the user question to pre-filter what tools might be necessary. But it turns out that this is **a very weak approach** because the user question itself might not indicate the real intent. Semantic search is not enough as a mechanism to understand the intent."

### 9.3 解决方案：Tool Search Tool（工具搜索工具）

**核心理念：** "Delegating this responsibility to the LLM."

> "The LLM, from the user question, **much better** can figure out what are the tools and what is the real intent."

### 9.4 架构

```
启动时：只注册一个工具 → "toolSearchTool"
                        
用户提问 → LLM分析需要什么 → 调用 toolSearchTool
                                ↓
                    [Client-Side Tool Searcher]
                    (向量存储 / Lucene / 正则表达式)
                                ↓
                    返回匹配的工具定义
                                ↓
                    LLM 调用具体工具完成工作
```

**Tool Search Tool 的定义：**
```java
@Tool(description = """
    If you need some additional information to fulfill the task,
    you can use this tool to search for available tools.
    Provide your intent and I'll find the right tools for you.
    """)
public List<ToolDefinition> searchTools(String userIntent) {
    // 在本地索引中搜索匹配的工具
    return toolSearcher.search(userIntent);
}
```

**客户端工具索引：**
```java
// 启动时索引所有可用工具
ToolSearcher toolSearcher = new VectorStoreToolSearcher(vectorStore);
// 或
ToolSearcher toolSearcher = new LuceneToolSearcher();
// 或纯正则
ToolSearcher toolSearcher = new RegexToolSearcher();
```

### 9.5 Demo 对比：正常 vs Progressive Disclosure

**配置：**
```java
// 有 ~50 个工具，其中 3-4 个相关
// 一次注入所有工具  vs  使用 Tool Search Tool
```

**正常模式（无 Progressive Disclosure）：**
```
输入 Tokens: 40,000+
输出 Tokens: 14,000
所有工具描述一次性注入上下文中
LLM 需要自己在 50 个工具中寻找相关工具
```

**Progressive Disclosure 模式：**
```java
// 只需要换一个 Advisor
ChatClient.builder(chatModel)
    .advisors(new ToolSearchToolAdvisor(toolSearcher))  // <-- 不同 Advisor
    .build();
```

**Demo 对话过程（演讲原话还原）：**

步骤 1：初始请求
```
用户："Help me plan what to wear today in Landsmeer."
LLM 最早看到的只有一个工具 → toolSearchTool
```

步骤 2：LLM 第一次回询
```
LLM → [调用 toolSearchTool]："我需要当前时间来开始规划"
toolSearcher → 返回：getCurrentTime
LLM → 调用 getCurrentTime → 获得当前时间
```

步骤 3：LLM 再次回询
```
LLM → [再次调用 toolSearchTool]："我现在需要天气信息"
toolSearcher → 返回：getWeatherForecast(location, time)
LLM → 调用 getWeatherForecast → 获得天气数据
```

步骤 4：LLM 第三次回询
```
LLM → [再次调用 toolSearchTool]："还需要附近服装店信息"
toolSearcher → 返回：findClothingShops(location, time)
LLM → 调用 findClothingShops → 获得商店列表
```

步骤 5：生成最终响应（建议穿什么 + 推荐商店）

**Tokn 对比（原文）：**
> "Half in this case — **half of the tokens** that we've been used. It's a very powerful way, especially if you use a lot of tools and tokens."

### 9.6 状态

> "We're going to make it part of the release 2.0 coming next month of Spring AI. Right now it's part of the community — you already can use it."

---

## 十、Tool Augmentation & Inner Thoughts（工具参数增强）— Demo 8

### 10.1 背景：灵感来自 MemGPT

> "This pattern was borrowed from a product called MemGPT. How many of you have heard about MemGPT?"

**MemGPT 的思路：** 在工具调用中增加参数来获取 LLM 的**推理过程**。

**原始方案（MemGPT 方式）：**
```java
@Tool(description = "获取实时天气")
public String getRealTimeWeather(
    String location,
    
    @ToolParam(description = "请提供你为什么要调用此工具的内省")
    String innerThoughts  // <-- 额外参数，为了获取 LLM 推理
) {
    System.out.println("LLM reasoning: " + innerThoughts);
    return weatherService.fetch(location);
}
```

**问题：** "It was kind of **abusing the idea of tool itself**." —— 这个参数与工具功能无关，只是为了"劫持"工具调用来获取额外信息。

### 10.2 Spring AI 的方案：Tool Augmentor（工具增强器）

```java
// 原始工具定义
public record GetTemperature(String location) {}

// 使用 Augmentor 包装 — 可以注册任意数量的附加参数
ToolCallback augmentedTool = ToolAugmentor.builder()
    .tool(new GetTemperature())
    .additionalParameter("innerThoughts", 
        "你的逐步推理：为什么要调用此工具",
        String.class)
    .additionalParameter("confidence",
        "你对此工具调用的置信度",
        String.class)
    .build();

// 配置到 ChatClient
ChatClient.builder(chatModel)
    .tools(augmentedTool)
    .build();
```

**底层原理：**
1. Augmentor 是一个 **Tool Call Provider**（Spring AI 的标准抽象）
2. 对 LLM 来说，这些参数看起来是工具定义的一部分
3. LLM 必须提供这些参数的值才能调用工具
4. 返回时，可以丢弃这些参数，或注册 Consumer 来处理

### 10.3 处理增强参数的 Consumer

```java
// 注册 Consumer 来处理 LLM 返回的附加参数
ToolAugmentor.builder()
    .tool(new GetTemperature())
    .additionalParameter("innerThoughts", ...)
    .additionalParameter("confidence", ...)
    .consumer((toolExecutionResult) -> {
        // 可以在这里处理 innerThoughts 和 confidence
        // 用于可观测性、日志、分析等
        System.out.println("Reasoning: " + result.get("innerThoughts"));
        System.out.println("Confidence: " + result.get("confidence"));
    })
    .build();
```

### 10.4 Demo 结果

```
用户："What's the current weather in Paris?"

LLM 返回的推理：
"innerThoughts: The user is asking for current weather in Paris.
 This is a straightforward weather query, no complex reasoning needed.
confidence: high"
```

> "Most of the time it would be for some additional observability."

**兼容性：** "This works perfectly fine with any tools, both local and MCP tools."

---

## 十一、Progressive Disclosure 的通用原理

### 11.1 回顾：RAG 的问题

> "If you remember I mentioned about the RAG and the context stuffing early on where you try to upfront preload your context with everything relevant to your question hoping that this would be enough to yield the right response. You're doing the best manipulation in order to restrict or extract the context that makes sense for this question — but you **did not involve the LLM** in order to make this decision. This very often leads to overloading the context."

### 11.2 替代方案：让 LLM 决定

> "Keep the context upfront as **small as possible** and **let the LLM decide** what to get next to put next in the context."

**已经展示的模式都遵循此原则：**
1. **Tool Search Tool** — 不预加载所有工具定义
2. **Agent Skills** — 不预加载所有知识
3. **Sub-Agents** — 子任务隔离上下文

---

## 十二、Agent Skills（技能系统）— Demo 9

### 12.1 什么是 Agent Skills

Skill 是一个标准化的**可加载能力模块**，用 Markdown 文件定义。

**格式：**
```yaml
---
name: youtube-transcriber
description: 转录 YouTube 视频并用简单语言总结
author: Community
tags: [youtube, transcription, education]
---
# YouTube Transcriber Skill

你可以使用 Python 脚本转录 YouTube 视频内容...

## 附加文件

- [transcriber.py](transcriber.py) — 转录脚本
- [template.md](template.md) — 输出模板
```

### 12.2 Skill 的三个组成部分

| 部分 | 说明 |
|------|------|
| **元数据（Frontmatter）** | 名称、描述、标签（类似工具描述，用于 LLM 决策） |
| **Markdown 内容** | LLM 实际读取的上下文信息 |
| **引用文件（可选）** | 附加 Markdown / 脚本（LLM 可按需阅读） |

### 12.3 Spring AI 对 Agent Skills 的支持

**兼容性：**
> "It's entirely compatible with any skills you can get out there right now."

**配置方式：**
```java
// 从目录加载 Skills
SkillTool skillTool = new SkillTool("/path/to/skills");

// 或从 JAR 加载（Agent JARs，由 James 实现）
SkillTool skillTool = new SkillTool("classpath:skills/**");

// 或通过 OCI (提案中，由 Thomas 提出) — 标准化的打包机制
```

**跨模型支持：**
> "You can actually use it across various models. In this case, I'm using Anthropic — but OpenAI, Google Gen AI, Bedrock would work almost equally the same."

### 12.4 Agent Skills 的本质

> "It's nothing more than **yet another set of tools**."

```java
// 底层实现——SkillTool 就是一组特殊的工具
SkillTool skillTool = new SkillTool(skillsDirectory);

ChatClient.builder(chatModel)
    .tools(skillTool)          // Skill 工具—用于列出和加载 Skill
    .tools(new ShellTool())    // 允许执行脚本
    .tools(new FileSystemTool()) // 允许读取文件
    .tools(new BraveSearchTool()) // 允许搜索网页
    .build();
```

**Skill 工具的工作流程：**
1. **注册一个"Skill 列表工具"** → 告知 LLM 有哪些 Skill 可用
2. LLM 查看 Skill 名称和描述，决定需要哪个
3. **调用 Skill 加载工具** → 将 Skill 的 Markdown 内容注入上下文
4. 如果 Skill 引用其他文件 → LLM 按需读取
5. 如果 Skill 包含脚本 → 通过 Shell Tool 执行

### 12.5 Demo：Agent 自己动手做任何事

> "When you're building your application, you're just defining yet another tools. This is the skill tools — it takes the list of directory where you have your skills defined."

**提问：** "Explain reinforcement learning in simple terms and refer to some YouTube videos."

**实际执行过程：**
1. LLM 检测到需要 `youtube-transcriber` Skill
2. 加载 Skill 内容
3. 通过 **Shell Tool** 执行 `transcriber.py`（Python 转录脚本）
4. 脚本下载并转录 YouTube 视频
5. 读取转录文本 → 生成简单解释
6. 返回最终响应

> "It immediately realizes that it needs this skill. We already starting executing bash scripts. It actually runs scripts, generates JavaScript, compiles it, runs it. It's quite impressive and **scary** at the same time."

**安全警告：**
> "If you do this, you definitely have to run your application in some sandbox or container environment."

---

## 十三、To-Do Right（任务清单模式）— Demo 10

### 13.1 问题：LLM 在多步任务中容易迷失

> "When you have a complex task that requires multiple steps to resolve, some of the agent models can get confused on the way to the answer. They perform too many intermediate steps and they can lose track of what actually was supposed to be done."

### 13.2 解决方案：强制 LLM 创建结构化待办清单

```java
@Tool(description = """
    管理任务清单。此工具用于跟踪多步任务的进度。
    每个任务有生命周期：PENDING → IN_PROGRESS → COMPLETED
    
    关键规则：
    1. 一次只执行一个步骤
    2. 前一步未完成不得进入下一步
    3. 每一步完成时更新清单状态
    """)
public String manageTodo(String action, String taskName, String status) {
    return todoService.update(action, taskName, status);
}
```

### 13.3 代码组合

```java
ChatClient.builder(chatModel)
    .advisors(new TodoAdvisor(), new MessageChatMemoryAdvisor())
    .tools(new ManageTodoTool())  // 清单管理工具
    .build();
```

### 13.4 Demo 展示

**提问：** 一个复杂的多步任务

**执行过程（可视化）：**
```
创建一个包含 N 个步骤的 To-Do 清单

Step 1: [PENDING]
Step 2: [PENDING]  
Step 3: [PENDING]
...

→ Step 1: [IN_PROGRESS] → 执行 → [COMPLETED]
→ Step 2: [IN_PROGRESS] → 执行 → [COMPLETED]
→ Step 3: [IN_PROGRESS] → 执行 → [COMPLETED]
...
```

> "It's a technique to ensure that the LM actually always does the task in the right order and it's not going to skip something on the way."

### 13.5 灵感来源

> "This pattern I actually borrowed from Claude Code's implementation. Interestingly, the last version of Claude Code actually moves away from this pattern because they re-implemented some of this logic in their new task management mechanism — but the idea is the same."

---

## 十四、Clarification Questions（澄清问题工具）— Demo 11

### 14.1 问题：LLM 过于武断

> "Very often the LLMs are opinionated. If you ask a complex question, they would tend to make assumptions and go forward. Once they moved forward, it's very hard to force them to come back and correct what they've assumed."

### 14.2 解决方案：一个"问我"工具

```java
@Tool(description = """
    By the way, if you're not sure about how to proceed or have multiple choices,
    DON'T make opinionated decisions — ask us for details.
    """)
public String askUserQuestion(
    @ToolParam(description = "给用户的提问内容")
    String question,
    
    @ToolParam(description = "可选的多选选项")
    List<String> options,
    
    @ToolParam(description = "是否允许自由文本回答")
    boolean allowFreeText
) {
    // Spring AI 提供 CLI 默认 Handler
    // 自定义 UI 框架需要自己实现 Handler
    return userInputHandler.ask(question, options, allowFreeText);
}
```

### 14.3 集成

```java
ChatClient.builder(chatModel)
    .advisors(new ToolCallAdvisor(), new MessageChatMemoryAdvisor())
    .tools(new AskUserTool())  // <-- 又一个"只是一个工具"
    .build();
```

### 14.4 Demo：旅行规划

**没有 Clarification Tool 时：**
```
用户："我应该去哪里旅行？"
LLM → "我推荐巴黎！"  (武断猜测，完全不问用户偏好)
```

**有 Clarification Tool 时：**
```
用户："我应该去哪里旅行？"
LLM → [调用 askUserQuestion，询问偏好]
     "您喜欢什么类型的假期？"
     
用户："户外自然"
LLM → [再问]
     "喜欢温暖气候还是凉爽气候？"

用户："温暖地中海风格"
LLM → [再问]
     "预算范围？奢华还是经济？"

用户："奢华"
LLM → "基于您的喜好，我推荐：西班牙(Marbella)、马耳他(Sliema)、意大利(Amalfi)"
```

> "Without adding this tool, most likely the LM is going to make some assumption and give me suggestions based on no context at all."

---

## 十五、Sub-Agents（子智能体）— Demo 12

### 15.1 问题：主 Agent 上下文污染

> "In order to solve a complex task, the LM would have to solve a lot of small sub tasks. In order to solve these sub tasks, very often it's going to use tools, additional skills — and it's going to **pollute your main agent context**, which would decrease the chance and the ability of this agent to solve and provide the right response."

### 15.2 解决方案：隔离上下文

> "Let's run these sub tasks in their own **isolated context**."

### 15.3 子任务定义

```yaml
---
name: code-review
model: gpt-4o-mini  # 可以使用不同模型（通常更小更快）
description: Review generated code for bugs and security issues
---
Analyze the following code and check for:
1. Logic errors
2. Security vulnerabilities
3. Performance issues
4. Code style violations
```

### 15.4 Sub-Agent 底层

```java
// Sub-Agent 底层也是一个 Tool
@Tool(description = "在隔离上下文中执行一个子任务")
public String executeSubTask(String taskDefinition, String parameters) {
    ChatClient subClient = ChatClient.builder(this.subChatModel)  // 独立模型
        .defaultSystem(taskDefinition)
        .build();
    return subClient.call(parameters);
}
```

**关键特性：**
- **隔离上下文**：子 Agent 的执行不污染主 Agent
- **独立模型**：可以用更小更快的模型
- **结果汇总**：只有最终结果回到主 Agent
- **可扩展**：Spring AI 还支持通过 Agent 描述定义远程 Agent
- **任务即 Tool**：底层是另一个 Task Tool

---

## 十六、总结：一切皆 Advisor + Tool

### 16.1 核心公式

> "We built everything with advisors, with one small exception (Todo Advisor, which also relies on the ability to execute tools). Two things practically: **advisors and tool support is everything you need to implement all of these patterns.**"

```
所有 Agent 模式 = Advisor（拦截增强） + Tool Support（工具执行）
```

**演讲中展示的所有模式：**

| # | 模式 | 本质 |
|---|------|------|
| 1 | Chat Memory | Advisor |
| 2 | RAG | Advisor |
| 3 | Sensitive Word Guardrails | Advisor |
| 4 | Structured Output | Advisor |
| 5 | Self-Refine / Judge LLM | Advisor |
| 6 | Tool Calling | Advisor |
| 7 | Progressive Tool Disclosure | Advisor + Tool |
| 8 | Tool Argument Augmentation | Advisor（Proxy） |
| 9 | Agent Skills | Tool |
| 10 | To-Do Right | Tool |
| 11 | Clarification Questions | Tool |
| 12 | Sub-Agents | Tool（+隔离 ChatClient） |

### 16.2 Advisor 顺序的最终验证（最后分享的代码）

> "Here is the last thing I'm going to share. This was the Todo Advisor and the memory."

```java
// ✅ 正确顺序：Memory 记住完整上下文
ChatClient.builder(chatModel)
    .advisors(new TodoAdvisor(), new MessageChatMemoryAdvisor())
    // Memory Advisor 在 Todo Advisor 内部
    // → 记忆包括：初始请求 + 所有中间工具调用 + 最终响应
    .build();

// ❌ 旧行为：Memory 只记住最外层
ChatClient.builder(chatModel)
    .advisors(new MessageChatMemoryAdvisor(), new TodoAdvisor())
    // Memory 只记忆原始请求和最终响应
    // → 丢失中间步骤
    .build();
```

> "In order for this to happen, your memory advisor should be **inside** your Todo Advisor. If you change the order, it's still going to work, but it will be the **old behavior** — the memory is going only to memorize your original request and final response."

### 16.3 三个核心概念串起来

Spring AI 的整个 Agent 构建哲学可以通过三个概念串联：

```
Advisor（拦截器）
    │
    ├── 拦截输入 → 增强上下文
    ├── 拦截输出 → 检查/重试/分发
    └── 本质上就是"中间件"
    
    + 
    
Tool（工具）
    │
    ├── 让 LLM 能"动手做事"
    ├── 标准化描述（名称+描述+参数Schema）
    └── 各种模式本质都是"只是一个工具"
    
    =
    
Agentic Systems（智能体系统）
```

---

## 十七、附录：知识关联

### 本演讲在 Spring AI 生态中的位置

| 关联文档 | 关联点 |
|---------|--------|
| `spring/ai-agent/dan-vega-spring-ai-full-course-notes.md` | Dan Vega 5h+ 全栈课程，含 RAG、MCP、可观测性、评估—**偏实操入门** |
| `spring/ai-agent/josh-long-spring-ai-workshop-notes.md` | Josh Long & James Ward Agent Workshop—**Bedrock + MCP 集成** |
| `spring/bootiful-spring-ai-josh-long-springio-2026.md` | Josh Long 演讲—**从零构建生产级 AI Agent** |
| `ai-tools/frameworks/springio-2026-comparing-agentic-ai-frameworks-for-java.md` | Java 框架对比（Spring AI vs LangChain4j vs Embabel） |
| `ai-tools/frameworks/spring-ai-bedrock-agentcore-mcp-conference-app.md` | Spring AI + Bedrock 实战 |
| `spring/ai-agent/spring-ai-agent-resources-top30.md` | Spring AI Agent 资源 Top 30 汇总 |

### 推荐阅读路径

1. **先读 Dan Vega** — 掌握 Spring AI 基础操作和实战
2. **再读本文** — 理解 Advisor 模式和 Agent 演进的完整理论框架
3. **再读 Josh Long** — 看生产环境部署和 Bedrock 集成
