# Bootiful Spring AI — Josh Long & James Ward @ Spring I/O 2026

> **视频信息**
>
> - **演讲者：** Josh Long（Broadcom / VMware Tanzu）& James Ward（AWS）
> - **会议：** Spring I/O 2026，西班牙巴塞罗那，2026 年 4 月 14-15 日
> - **时长：** 42 分 03 秒
> - **播放量：** 918 次
> - **链接：** <https://youtu.be/nHnKReitDXc>

---

## 一、演讲概述

> "The age of artificial intelligence (because the search for regular intelligence hasn't gone well..) is nearly at hand, and it's everywhere! But is it in your application?"
>
> — Josh Long & James Ward

这场演讲的核心命题：**AI 就是集成（AI is about integration）**。Java 和 Spring 社区在集成方面有深厚积累，Spring AI 项目正是将这些经验延伸到 AI 工程领域。

两位演讲者分别代表了**企业 Java 生态**（Josh Long，Spring 布道师）和**云原生基础设施**（James Ward，AWS），从不同视角探讨了 Spring AI 如何让 Java 开发者无缝接入 AI 能力。

---

## 二、Spring AI 项目简介

Spring AI 是一个面向 AI 工程的应用程序框架，由 Spring 团队在 2023 年底启动。它的核心理念是**将 Spring 生态系统的设计原则（可移植性、模块化设计、POJO 编程模型）应用到 AI 领域**。

> Spring AI 受 LangChain 和 LlamaIndex 等 Python 项目启发，但**不是直接移植**——它认为下一波生成式 AI 应用不会只属于 Python 开发者，而是会跨编程语言普及。

### 核心定位

连接**企业数据 & API** 与 **AI 模型**。

---

## 三、Spring AI 特性全景

### 3.1 AI 模型支持

Spring AI 为所有主流 AI 模型提供**统一的可移植 API**：

| 模型类型 | 说明 | 主要提供商 |
|---------|------|-----------|
| **Chat 对话** | 同步 / 流式 API | OpenAI、Anthropic、Azure、AWS Bedrock、Google Vertex AI、Ollama |
| **Embedding 嵌入** | 向量化文本 | 同上 |
| **Text-to-Image 文生图** | DALL-E、Stable Diffusion | OpenAI、Stability AI |
| **Audio Transcription 语音转文字** | Whisper 等 | OpenAI |
| **Text-to-Speech 语音合成** | 文字转语音 | OpenAI、Amazon Polly |
| **Moderation 内容审核** | 安全过滤 | OpenAI Moderation |

支持同时访问**模型通用能力**和**模型特有功能**（如特定参数）。

### 3.2 Vector Store 向量数据库

支持所有主流向量数据库，并提供统一的可移植 API：

Cassandra、Azure Cosmos DB、Azure Vector Search、Chroma、Elasticsearch、Milvus、MongoDB Atlas、Neo4j、OpenSearch、Oracle、PostgreSQL/PGVector、Pinecone、Qdrant、Redis、SAP Hana、Typesense、Weaviate、GemFire、MariaDB

> **亮点：** 创新的 SQL 风格元数据过滤 API（metadata filter API）

### 3.3 ChatClient API

Spring AI 的标志性 API，风格上类似于 `WebClient` 和 `RestClient`：

```java
ChatClient chatClient = ChatClient.builder(chatModel).build();
String response = chatClient.prompt("Tell me a joke")
    .call()
    .content();
```

支持：
- **Chat Memory** — 对话记忆
- **工具调用 / Function Calling** — 让模型调用客户端工具
- **Retrieval Augmented Generation (RAG)** — 检索增强生成
- **Advisors API** — 封装生成式 AI 的通用模式

### 3.4 Advisors API（关键设计）

Advisors API 是 Spring AI 的一个独特设计，用于：

- **封装通用模式** — 如提示词注入缓、RAG 路由、日志记录
- **数据转换** — 在 LLM 数据流中插入预处理/后处理
- **跨模型可移植** — 同样的 Advisor 可在不同模型间复用

### 3.5 结构化输出

将 AI 模型输出映射到 POJO，解决非结构化文本到类型安全数据的问题：

```java
@Bean
CommandLineRunner runner(ChatClient.Builder builder) {
    return args -> {
        ChatClient chatClient = builder.build();
        ActorFilms response = chatClient.prompt()
            .user("Generate a filmography for a random actor")
            .call()
            .entity(ActorFilms.class);
        System.out.println(response);
    };
}
```

### 3.6 ETL 框架（文档摄取）

内置的文档注入 ETL 流程：

```
Document Reader → Document Transformer → Vector Store Writer
```

典型的 RAG 场景管线。

### 3.7 AI 模型评估

- 评估生成内容的质量
- 检测幻觉（hallucination）
- 提供测试工具集

### 3.8 可观测性

OpenTelemetry 集成，提供 AI 操作的监控、追踪和度量。

### 3.9 Spring Boot Auto-Configuration

所有 AI 模型和 Vector Store 都通过 Spring Boot Starter 自动配置：
- 使用 [start.spring.io](https://start.spring.io/) 选择所需模型和存储
- 一行配置即可切换提供商

---

## 四、快速入门示例

```properties
# application.properties
spring.ai.openai.api-key=YOUR_API_KEY
```

```java
@SpringBootApplication
public class SpringAiDemoApplication {

    @Bean
    CommandLineRunner runner(ChatClient.Builder builder) {
        return args -> {
            ChatClient chatClient = builder.build();
            String response = chatClient.prompt("Tell me a joke")
                .call()
                .content();
            System.out.println(response);
        };
    }

    public static void main(String[] args) {
        SpringApplication.run(SpringAiDemoApplication.class, args);
    }
}
```

---

## 五、演讲者介绍

### Josh Long — Broadcom / VMware Tanzu

- **Spring 布道师**，开发者体验工程师
- 畅销书作者（《Spring Boot in Practice》等）
- 熟悉 Spring 生态的方方面面，是社区最活跃的技术布道者之一
- 以 "bootiful" 系列演讲闻名

### James Ward — AWS

- AWS 高级开发者布道师（Java / AI 方向）
- 前 Adobe、Heroku 技术布道师
- 云原生架构和 AI/ML 基础设施专家
- 将 Spring AI 与 AWS 服务（Bedrock、SageMaker）的集成经验

---

## 六、生态与延伸资源

### 官方资源
- **Spring AI 首页：** <https://spring.io/projects/spring-ai>
- **Spring AI 参考文档：** <https://docs.spring.io/spring-ai/reference/>
- **Spring I/O 2026 议程：** <https://2026.springio.net/sessions/bootiful-spring-ai/>
- **start.spring.io：** 快速创建 Spring AI 项目

### 相关视频
- [Bootiful Spring AI — An Evening with Josh Long and James Ward](https://www.youtube.com/watch?v=hzLo1EefMqA)（同主题深入版）

### 适用场景
- **Q&A over your documentation** — 语义搜索 + RAG
- **Chat with your documentation** — 对话式文档查询
- **智能客服系统** — Function Calling + 记忆
- **内容生成与审核** — Chat + Moderation
- **图像生成应用** — Text-to-Image API

---

## 七、文章总结

| 维度 | 要点 |
|------|------|
| **核心理念** | AI 就是集成，Spring AI 将 Spring Boot 的集成能力扩展到 AI |
| **设计哲学** | 可移植 API + POJO 编程 + 模块化 |
| **关键 API** | ChatClient（流式） + Advisors（模式封装） + ETL（文档管线） |
| **独特价值** | 统一多个 AI 提供商，一行配置切换；SQL 风格向量过滤 |
| **适用人群** | Java / Spring 开发者，希望在应用中集成 AI 能力 |
| **下一步** | 上手 start.spring.io 创建项目，尝试 ChatClient |

---

*本文基于 Spring I/O 2026 演讲元数据和 Spring AI 官方文档整理。完整的演讲内容包含现场 demo 和技术细节，建议观看原视频。*
