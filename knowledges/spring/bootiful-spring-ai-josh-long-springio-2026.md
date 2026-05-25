# Bootiful Spring AI — 从零构建生产级 AI Agent

> 演讲人：**James Ward**（AWS） & **Josh Long**（Spring 团队）
> 会议：Spring I/O 2026（或类似技术大会）
> 代码地址：[GitHub — James Ward / Pooch Palace](https://github.com/JamesWard/pooch-palace)
> 书籍：[beautifulspringai.com](https://beautifulspringai.com)（Spring AI 入门书，未出版）
> 播客：[Coffee and Software](https://youtube.com)（YouTube 频道）

---

## 目录

1. [开场 & 故事背景](#1-开场--故事背景)
2. [Dial Tone：让模型响起来](#2-dial-tone让模型响起来)
3. [System Prompt：给 AI 安上使命](#3-system-prompt给-ai-安上使命)
4. [Agent Skills / Skill Jars：渐进式知识注入](#4-agent-skills--skill-jars渐进式知识注入)
5. [Memory：让 AI 记住对话](#5-memory让-ai-记住对话)
6. [RAG：连接外部数据库](#6-rag连接外部数据库)
7. [Tool Calling：给 AI 行动能力](#7-tool-calling给-ai-行动能力)
8. [MCP Server：分布式工具调用](#8-mcp-server分布式工具调用)
9. [Security（OAuth）：给 MCP 上锁](#9-securityoauth给-mcp-上锁)
10. [Observability：看得见的 AI](#10-observability看得见的-ai)
11. [总结：Java/Spring 开发者的黄金时代](#11-总结javaspring-开发者的黄金时代)

---

## 1. 开场 & 故事背景

### 演讲人

- **James Ward** — AWS 工程师，负责 Spring AI 的 AWS Bedrock 集成
- **Josh Long** — Spring 团队成员（Spring 布道师）
- 两人共同主持播客 *Coffee and Software*，合著 Spring AI 入门书

### 他们做的第一件事：给书建一个 MCP Server

演讲开始前，James 和 Josh 展示了他们已经完成的一个项目——为他们的 Spring AI 书写了一个 **MCP Server**：

> 用户可以在 Claude（或任何 MCP 客户端）中连接这个 MCP Server，直接问"这本书讲了什么？"，MCP Server 实时返回书中的内容。

这个例子引出了整场演讲的核心问题：**AI 的真正价值在于与现有业务系统的深度集成。**

### 虚构案例：Pooch Palace 狗狗领养中心

他们用一家虚构的全球连锁宠物领养机构 **Pooch Palace**（分支机构覆盖 Antwerp、Seoul、Tokyo、Singapore、Paris、Mumbai、New Delhi、Barcelona、Adonis Animals / San Francisco、London）作为贯穿全场的例子。

**明星狗狗：Prancer**

Prancer 是一只"神经质、恨男人、恨动物、恨小孩、长得像小魔怪"的狗。原主人花了几个月都没能把它送出去。James 和 Josh 要用 AI 帮 Prancer 找到新家。

---

## 2. Dial Tone：让模型响起来

### 2.1 项目骨架

从 Spring Initializr 开始，需要添加以下依赖：

| 依赖 | 用途 |
|------|------|
| `spring-boot-starter-web` | REST 端点 |
| `spring-boot-starter-data-jdbc` | 数据库访问 |
| `pgvector` | 向量存储（Postgres 双用途） |
| `spring-ai-bedrock-spring-ai` | Bedrock Embeddings |
| `spring-ai-bedrock-converse` | Bedrock Chat Model |
| `spring-ai-pgvector-store` | PGVector 向量存储 |
| `spring-boot-starter-security` | 安全（稍后配置） |
| `spring-boot-starter-actuator` | 健康检查/监控 |

**为什么 Postgres 能做两件事？** PGVector 让同一个 Postgres 实例同时做关系型数据库和向量存储，两套数据结构的底层是同一个进程。

> 你也可以选 Chroma、Weaviate、Neo4j、MongoDB、Elastic 等作为向量存储——Spring AI 有约 20 种向量存储实现。

### 2.2 配置

```yaml
# 数据库
spring.datasource.url=jdbc:postgresql://localhost:5432/doghouse
spring.datasource.username=postgres
spring.datasource.password=postgres
spring.datasource.driver-class-name=org.postgresql.Driver

# Bedrock Chat Model
spring.ai.bedrock.converse.chat.model=amazon.nova-pro-v1:0
spring.ai.bedrock.converse.chat.options.temperature=0.7

# Bedrock Embedding Model
spring.ai.bedrock.converse.embedding.model=cohere.embed-english-v3
spring.ai.bedrock.converse.embedding.options.inputType=search_document

# PG Vector
spring.ai.vectorstore.pgvector.index-type=hnsw
spring.ai.vectorstore.pgvector.distance-type=cosine-distance
spring.ai.vectorstore.pgvector.dimensions=1024
```

### 2.3 Dial Tone Controller

```java
@RestController
public class AssistantController {

    private final ChatClient chatClient;

    public AssistantController(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }

    @GetMapping("/ask")
    String ask(@RequestParam String question) {
        return chatClient.prompt()
                .user(question)
                .call()
                .content();
    }
}
```

这是最基础的"通话音测试"：发一个问题给 LLM，拿到回复。只需要一个 `ChatClient`——这是 Spring AI 中跨所有模型的标准交互接口。

### 2.4 第一次启动

Spring Boot 启动极快，但第一次启动时**必须要注释掉安全依赖**，否则 Security Auto-Configuration 会强制要求认证。

> 现场翻车名场面：Josh 忘记注释安全依赖，启动后被 Security 拦截，全场爆笑。

---

## 3. System Prompt：给 AI 安上使命

没有 System Prompt 时，问"你有神经质的狗吗？"模型会以为你在问怎么处理你的狗。我们需要让模型知道自己的身份和使命。

```java
@Bean
ChatClient chatClient(ChatClient.Builder builder) {
    return builder
            .defaultSystem("""
                You are an AI-powered system to help people adopt a dog from
                the adoption agency named Pooch Palace with locations in Antwerp,
                Seoul, Tokyo, Singapore, Paris, Mumbai, New Delhi, Barcelona,
                Adonis Animals in San Francisco, and London.

                Information about the dogs available will be presented below.
                If there is no information, return a blank response suggesting
                we don't have any dogs available.

                If somebody asks you about animals and there is no information
                in the context, feel free to source the answer from other places.

                If somebody asks for a time to pick up a dog, don't ask other
                questions. Simply provide a time by consulting the tools you
                have available.
                """)
            .build();
}
```

**System Prompt 的作用**：像给 LLM 调用加上"重力"，让它在特定方向上发挥——给它一个个性、一个使命和一个工作框架。

---

## 4. Agent Skills / Skill Jars：渐进式知识注入

### 4.1 什么是 Skills？

Skills 就像是 **AI 的 wiki**，允许你**渐进式加载知识**到 AI 中。Skill 本质上是一个包含 `SKILL.md` 文件的目录结构，该文件的文本权重比 LLM 预训练知识更高——当知识冲突时，Skill 内容优先。

### 4.2 Skill Jars：可版本化的知识包

**[skillsjars.com](https://skillsjars.com)** — 由 James 创建的技能打包工具，允许你：

1. 把 Skill 内容打包成 **Maven Jar**
2. 发布到 **Maven Central**（或内部 Artifactory/Nexus）
3. 以标准依赖的方式引入项目
4. 实现**版本管理、审计、供应链安全**

```xml
<dependency>
    <groupId>com.poochpalace</groupId>
    <artifactId>pooch-palace-skills</artifactId>
    <version>1.0.0</version>
</dependency>
```

### 4.3 Pooch Palace 中的示例 Skill

Pooch Palace 的狗狗和猫猫有一些独特属性：

```markdown
# Pooch Palace - Cat Knowledge

## Cat Whiskers
Most people don't know that cat whiskers are actually high-gain antennas.
They are natural WiFi extenders. This is a fact.

## ...
```

### 4.4 代码集成

```java
@Bean
public ChatClient chatClient(ChatClient.Builder builder, ToolCallbackProvider tools) {
    return builder
            .defaultSystem("...")
            .defaultTools(tools)  // 从 skill jar 自动发现的工具
            .build();
}
```

当用户问"我应该领养狗还是猫？"时：

1. LLM 收到用户 prompt + system prompt + 可用工具列表
2. LLM 决定调用 Skill Tool 获取完整的 Skill markdown 文件
3. Spring AI 在 agent 侧执行工具调用，返回文件内容
4. LLM 根据获取到的知识（猫胡须是 WiFi 天线！）回答用户

> ⚠️ 注意：必须在 ChatClient 上启用 **Tool Call Advisor** 才能工作。

---

## 5. Memory：让 AI 记住对话

LLM 默认是无状态的——每次调用都像第一次见面。Spring AI 通过 **Advisor**（类似拦截器）为 ChatClient 添加记忆功能。

### 5.1 JDBC Chat Memory

```java
@Bean
ChatClient chatClient(ChatClient.Builder builder,
                      ToolCallbackProvider tools,
                      DataSource dataSource) {
    return builder
            .defaultSystem("...")
            .defaultTools(tools)
            .defaultAdvisors(
                new PromptChatMemoryAdvisor(
                    JDBCChatMemoryRepository.builder()
                        .dataSource(dataSource)
                        .build()
                )
            )
            .build();
}
```

- 使用**滑动窗口**存储最近的对话（默认最大 20 条）
- 存储到关系数据库（可持久化）
- 通过 `conversationId` 区分不同用户/会话

### 5.2 更高级的选项

Spring AI 社区还提供了 **Auto Memory**（`agent-utils` 库的一部分），能自动管理记忆压缩和高级记忆技术。

### 5.3 Spring AI 记忆架构

```
User Request
    │
    ▼
┌──────────────────────────────┐
│     Advisor Chain            │
│  ┌────────────────────────┐  │
│  │ ChatMemoryAdvisor      │  │  ← 拦截请求，加载历史
│  └────────────────────────┘  │
│  ┌────────────────────────┐  │
│  │ VectorStoreAdvisor     │  │  ← RAG 检索
│  └────────────────────────┘  │
│  ┌────────────────────────┐  │
│  │ ToolCallAdvisor        │  │  ← 工具调用
│  └────────────────────────┘  │
│              ...             │
└──────────────────────────────┘
    │
    ▼
   LLM
```

---

## 6. RAG：连接外部数据库

### 6.1 RAG 流程

```
1. 启动时：从数据库读取所有狗狗记录
2. 用 Embedding Model 将每条记录转为向量
3. 存储向量到 PGVector
4. 用户提问时：用 user prompt 做相似度搜索
5. 匹配到关联记录 → 注入 prompt → 发给 LLM
6. LLM 基于增强后的上下文回答
```

### 6.2 启动时创建 Embeddings

```java
@Component
public class DataInitializer implements CommandLineRunner {

    private final DogRepository dogRepository;
    private final VectorStore vectorStore;

    @Override
    public void run(String... args) {
        List<Document> documents = dogRepository.findAll()
            .stream()
            .map(dog -> new Document(dog.getDescription()))
            .toList();
        vectorStore.add(documents);
    }
}
```

> 在生产中，你应该在创建/更新狗狗记录时同步更新 Embedding，而不是全部在启动时加载。

### 6.3 配置 RAG Advisor

```java
@Bean
ChatClient chatClient(ChatClient.Builder builder,
                      ToolCallbackProvider tools,
                      DataSource dataSource,
                      VectorStore vectorStore) {
    return builder
            .defaultSystem("...")
            .defaultTools(tools)
            .defaultAdvisors(
                new PromptChatMemoryAdvisor(...),
                new VectorStoreChatMemoryAdvisor(vectorStore)
            )
            .build();
}
```

**Bedrock Embeddings 的速度优势**：James 提到用 Bedrock Cohere 做 Embedding 只需要约 5 秒完成所有狗狗记录，而某些竞品需要 2-3 倍时间。

### 6.4 强类型返回值

```java
public record DogAdoptionSuggestion(int id, String name) {}

@GetMapping("/ask")
DogAdoptionSuggestion ask(@RequestParam String question) {
    return chatClient.prompt()
            .user(question)
            .call()
            .entity(DogAdoptionSuggestion.class);
}
```

**Java 的优势**：在无类型语言中你必须手动声明 schema，但在 Java 中，类型信息 + Jackson = schema 自动传递给 LLM，返回的 JSON 自动反序列化成强类型对象。

> 部分模型支持 **Native Structured Outputs**，Spring AI 会自动把你的 Java 类型 schema 传给 LLM，确保返回的 JSON 完全匹配。

---

## 7. Tool Calling：给 AI 行动能力

### 7.1 `@Tool` 注解

这是最简单的方式：在本地代码中定义一个 `@Tool` 方法，Spring AI 自动将其注册为 LLM 可用工具。

```java
@Component
public class DogAdoptionTools {

    @Tool("Schedule a dog adoption appointment at a Pooch Palace location")
    public AdoptionConfirmation scheduleAdoption(
            @ToolParam("The ID of the dog to adopt") int dogId,
            @ToolParam("The Pooch Palace location") String location,
            @ToolParam("The preferred date") LocalDate date
    ) {
        // 实际预约逻辑
        return new AdoptionConfirmation(dogId, date);
    }
}
```

**关键**：`@Tool` 的 `description` 字段至关重要——这就是告诉 LLM"什么时候应该调用这个工具"的 schema。

### 7.2 工作原理

1. ChatClient 将所有可用工具的描述（名称、描述、输入参数 schema）发送给 LLM
2. LLM 根据用户的请求决定是否调用某个工具
3. 如果需要，LLM 返回一个"工具调用请求"
4. Spring AI agent 端执行实际方法调用
5. 将结果返回给 LLM
6. LLM 基于结果生成最终回复

> 现场"翻车"名场面：James 忘了在工具方法中打印日志，不确定工具是否真的被调用了，还是 LLM 自己"幻觉"了一个结果。增加日志后确认调用成功。

---

## 8. MCP Server：分布式工具调用

### 8.1 为什么需要 MCP？

本地 `@Tool` 很好，但如果：
- 别的团队也想复用你的预约逻辑？
- 你需要调用第三方服务？
- 你的工具需要独立部署和扩展？

**MCP（Model Context Protocol）** 就是"microservices for AI agents"——标准化的工具服务协议。

### 8.2 从 `@Tool` 迁移到 `@MCPTool`

```java
@Component
public class DogAdoptionMcpTools {

    @MCPTool("Schedule a dog adoption appointment at a Pooch Palace location")
    public AdoptionConfirmation scheduleAdoption(
            @ToolParam("The ID of the dog to adopt") int dogId,
            @ToolParam("The Pooch Palace location") String location,
            @ToolParam("The preferred date") LocalDate date
    ) {
        // 同一个逻辑，变成了 MCP 服务
        return new AdoptionConfirmation(dogId, date);
    }
}
```

### 8.3 配置 MCP 客户端

```yaml
spring:
  ai:
    mcp:
      client:
        server-discovery: enabled
        servers:
          - url: http://localhost:8081/mcp
            name: pooch-palace-scheduler
```

```java
@Bean
ChatClient chatClient(ChatClient.Builder builder,
                      ToolCallbackProvider tools,
                      DataSource dataSource,
                      VectorStore vectorStore,
                      List<McpTool> mcpTools) {
    return builder
            .defaultSystem("...")
            .defaultTools(tools)
            .defaultAdvisors(...)
            .build();
}
```

**自动发现机制**：Spring AI 应用启动时，自动连接到所有配置的 MCP Server，获取可用工具列表，注册到 ChatClient 上下文中。

### 8.4 Tool Search Tool：解决工具数量爆炸

当你有很多工具（几十甚至上百个）时：

| 问题 | 后果 |
|------|------|
| 工具描述太多 | LLM 难以选择正确的工具 |
| 元数据过大 | 每次调用都传输大量 schema 信息 |
| 上下文浪费 | 不相关的工具占用了宝贵的 token 窗口 |

解决方案：**Tool Search Tool**

```java
// 启用工具语义搜索
builder.defaultAdvisors(
    new ToolSearchTool(vectorStore)
);
```

流程：
1. 首次调用时只发送"搜索工具"这一个工具给 LLM
2. LLM 搜索后确定需要哪些工具
3. 后续调用只发送匹配的少量工具

---

## 9. Security（OAuth）：给 MCP 上锁

分布式系统意味着更多的攻击面。需要立刻锁定！

### 9.1 架构

```
┌─────────────────┐     OAuth Token      ┌──────────────────┐
│   AI Agent      │ ──────────────────→   │  MCP Server      │
│   (Spring Boot) │                       │  (Spring Boot)   │
│                 │  ←────── 响应 ──────  │                  │
└─────────────────┘                       └──────────────────┘
        │                                        │
        │                                   OAuth Token
        │                                   Propagation
        ▼                                        │
┌─────────────────┐                               ▼
│   OAuth Server   │─────────────────────┐
│ (Spring Auth    │                     │
│  Server + MCP   │                     │
│  Security ext)  │                     │
└─────────────────┘                     │
         │                              │
         │ Validates Token              │
         ▼                              ▼
   ┌──────────────┐           ┌──────────────────┐
   │ User DB      │           │  MCP 端点受保护  │
   │ (Postgres)   │           │  需要 Bearer Token│
   └──────────────┘           └──────────────────┘
```

### 9.2 OAuth Server 配置

```java
@Configuration
@EnableAuthorizationServer
public class McpAuthServerConfig {

    @Bean
    public SecurityFilterChain authServerFilterChain(HttpSecurity http) {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/oauth2/**").permitAll()
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(OAuth2ResourceServerConfigurer::jwt)
            .with(new McpAuthorizationServerConfigurer(), config -> {})
            .formLogin(Customizer.withDefaults());
        return http.build();
    }

    @Bean
    public UserDetailsService userService(DataSource dataSource) {
        return new JdbcUserDetailsManager(dataSource);
    }
}
```

**关键依赖**：Spring AI 社区的 `mcp-security` 库，它为 OAuth Server 添加了 MCP 协议支持。

### 9.3 Agent 端 OAuth 客户端配置

```yaml
spring:
  security:
    oauth2:
      client:
        registration:
          mcpservice:
            client-id: pooch-palace-agent
            client-secret: secret
            authorization-grant-type: client_credentials
            provider: mcp-auth-server
        provider:
          mcp-auth-server:
            issuer-uri: http://localhost:9000
```

```java
@Bean
SecurityFilterChain clientFilterChain(HttpSecurity http) {
    http
        .oauth2Client(Customizer.withDefaults())
        .addFilterBefore(new McpOAuth2Interceptor(), BasicAuthenticationFilter.class);
    return http.build();
}
```

`McpOAuth2Interceptor` 的作用：
1. 拦截对 MCP Server 的调用
2. 检查当前是否有有效 token
3. 没有 → 重定向到 OAuth Server 获取 token
4. 有 → 将 Bearer Token 注入 MCP 请求头

### 9.4 延迟初始化

```yaml
spring:
  ai:
    mcp:
      client:
        defer-initialization: true  # 有 token 才连接 MCP Server
```

> 另一种策略：允许未认证用户获取工具列表，只在工具调用时要求认证。

### 9.5 用户身份传播

```java
@MCPTool("Schedule adoption")
public AdoptionConfirmation scheduleAdoption(...) {
    // 获取当前认证用户
    String username = SecurityContextHolder.getContext()
            .getAuthentication().getName();
    return service.schedule(dogId, location, date, username);
}
```

> 现场高光时刻：安全配置**一次通过**，没有任何翻车！James 和 Josh 兴奋击掌。

---

## 10. Observability：看得见的 AI

### 10.1 Grafana 集成

整个演示过程中，所有调用数据都被发送到了 Grafana，包括：

| 指标 | 说明 |
|------|------|
| **Token 用量** | 每次调用的输入/输出 token 数 |
| **调用耗时** | LLM 调用 + 工具调用的延迟分解 |
| **错误率** | 调用失败的统计 |
| **模型选择** | 使用的具体模型和版本 |

### 10.2 为什么 Observability 对 AI 应用至关重要

> "This is the difference between AI and production-worthy AI."
> — James Ward

- **成本控制**：Token 即金钱，你需要知道你的 AI 是否在烧钱
- **性能定位**：是 LLM 慢还是工具慢？
- **质量监控**：模型升级后输出是否有退化？
- **审计合规**：谁调用了什么工具？花了多少 token？

---

## 11. 总结：Java/Spring 开发者的黄金时代

### MIT 的统计

> MIT 去年做了一项研究：**95% 的 AI 解决方案失败**，原因就是它们没有与组织内现有的业务系统深度集成。

### 我们的身份

**你和我——在座的每一位——是守护企业业务逻辑的人。** 这些逻辑跑在 Java 和 Spring 上。

我们拥有的能力：

```
✅ System Prompts     → 控制 AI 人格和使命
✅ Skills & Jars      → 可审计的知识注入
✅ Memory             → 持久化对话上下文
✅ RAG                → 连接企业数据库
✅ Tool Calling       → 本地业务逻辑调用
✅ MCP Servers        → 分布式标准化工具
✅ Security (OAuth)   → 多方认证和身份传播
✅ Observability      → 成本与质量可视化
```

### 结论

> **"There's never been a better time to be a Java and Spring developer."**
> — Josh Long

### 延伸学习

| 资源 | 链接 |
|------|------|
| Spring AI 社区 | [spring.io/projects/spring-ai](https://spring.io/projects/spring-ai) |
| MCP 深度探索（Josh 的另一个 Talk） | 当天 11:30 同会场 |
| Skills Jars | [skillsjars.com](https://skillsjars.com) |
| Beautiful Spring AI 书 | [beautifulspringai.com](https://beautifulspringai.com) |
| Coffee & Software 播客 | YouTube |

---

## 附录：完整架构演化图

```
Step 1 — Dial Tone
┌──────────┐    HTTP ask(l)    ┌──────────┐    Prompt    ┌─────┐
│  Client   │ ──────────────→  │ ChatClient│ ──────────→│ LLM  │
└──────────┘                   └──────────┘    Response  └─────┘

Step 2 — + System Prompt
         System Prompt ──────→ ChatClient → LLM

Step 3 — + Skills (Knowledge Injection)
         Skill Jars ──→ ToolCallback ──→ ChatClient → LLM
                                           ↑  (LLM decides to fetch skill)
                                           └── Skills Tool ←─┘

Step 4 — + Memory
         Memory Advisor ──→ ChatClient
                              ↑  Load history from DB
                              ↓  Save new exchange

Step 5 — + RAG
         VectorStore Advisor ──→ ChatClient
                                   ↑ Similarity search on user input
                                   ↓ Retrieved docs injected into prompt

Step 6 — + Local Tool Calling
         @Tool beans ──→ ToolCallback ──→ ChatClient → LLM
                                              ↑ LLM requests tool call
                                              └── Agent invokes tool ──→

Step 7 — + MCP (Distributed Tools)
         MCP Server ─── Tool Discovery ───→ ChatClient → LLM
                        ↑ Auto-discover tools on startup
                        ↓ Expose as ToolCallbacks

Step 8 — + OAuth Security
         OAuth Server ◄── Agent ◄── MCP Server
         ▲  Token      │ Token      │ Token
         │  Issuance   │ Propagation│ Validation
         └─────────────┴────────────┘

Step 9 — + Observability
         ChatClient ──→ Micrometer ──→ Grafana
                        Token counts, latency, errors
```

---

> 文档整理自：Spring I/O 2026 演讲视频 [nHnKReitDXc](https://youtu.be/nHnKReitDXc)
> 转录 & 整理：Jarvis II
