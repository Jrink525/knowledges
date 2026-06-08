# Josh Long & James Ward Spring AI Agent Workshop 精要

> **视频**: [Building Agents with Spring AI, MCP, Java, and Amazon Bedrock | Workshop](https://youtu.be/G9PD6ANza70)  
> **主讲**: Josh Long (Spring Developer Advocate) & James Ward (AWS)  
> **时长**: 2h 6min | **类型**: 现场 Workshop  
> **中文整理**: 根据自动生成字幕归纳翻译，重点提炼工程落地要点

---

## 一、Spring Boot 基石

> *"I just want you to understand the shoulders on which we stand when we build today."*  
> — Josh Long

### 1.1 自动配置 (Auto-Configuration)

Spring Boot 的核心能力：通过 `@EnableAutoConfiguration` 自动检测 classpath 中的依赖并注册对应 Bean。

```java
@Configuration
public class MyConfig {
    @Bean
    public CustomerService customerService() {
        return new CustomerService();
    }
}
```

**Josh:** "Instead of writing all the boilerplate code - transaction handling, exception handling, rollback - Spring Boot auto-configuration figures out what you need based on what's in your classpath."

**中文解读：** Spring Boot 的自动配置不是黑魔法，本质是条件化 Bean 注册。框架会根据：
- classpath 中是否存在特定类（如 `DataSource`）
- 是否已有用户自定义的 Bean
- 配置属性文件中是否有相关设置

来决定要不要创建一个默认 Bean。

### 1.2 起步依赖 (Starters)

> "A starter is just a dependency that brings in the right code to start up a particular bit of support that you want. I've added that to the classpath, done nothing else, and now I've got an embedded web server running."

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

**中文解读：** Starters 是 Maven BOM 理念的实践，一个依赖引入一组经过兼容性验证的传递依赖。避免了你手动组合依赖版本时踩坑。

### 1.3 Actuator 健康检查

```json
// GET /actuator/health
{
  "status": "UP",
  "components": {
    "db": { "status": "UP" },
    "diskSpace": { "status": "UP" }
  }
}
```

**中文解读：** Actuator 返回 `200 UP` 或 `500 DOWN`，可集成到 K8s liveness/readiness probe。

### 1.4 虚拟线程 (Virtual Threads)

**Josh:** "This is equivalent to httpbin.org. It's a function of what thread the framework is dispatching to this controller handler method. We set that globally pretty simple: `spring.threads.virtual.enabled=true`"

```properties
spring.threads.virtual.enabled=true
```

**中文解读：** 一行配置即可让 Spring MVC 使用 Project Loom 虚拟线程处理请求，从线程池模型切换到轻量级虚拟线程，大幅提升并发承载能力。

### 1.5 GraalVM Native Image & SBOM

Josh 展示了：
- **CDS (Class Data Sharing)**：`spring.context.exit=refresh` 优化启动速度
- **CycloneDX SBOM**：生成软件物料清单，追溯依赖来源
- **GraalVM Native**：AOT 编译为原生二进制，但构建时间较长

---

## 二、Spring AI 入门 - Chat Client

> 主题过渡："We wanted to show you very quickly some of the AI stuff."

### 2.1 基础配置 (Amazon Bedrock)

```properties
spring.ai.bedrock.aws.region=us-east-1
spring.ai.bedrock.nova.claude.model-id=anthropic.claude-v2
```

**中文解读：** Spring AI 通过 `spring.ai.bedrock.*` 属性自动配置 Bedrock 客户端。支持多种模型提供商（Amazon, Anthropic, OpenAI 等），切换只需改配置。

### 2.2 构建 ChatClient

```java
@RestController
public class ChatController {
    private final ChatClient chatClient;
    
    public ChatController(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }
    
    @GetMapping("/chat")
    public String chat(@RequestParam String message) {
        return chatClient.prompt()
            .user(message)
            .call()
            .content();
    }
}
```

**中文解读：** `ChatClient` 是 Spring AI 的核心抽象，类似于 `RestTemplate` 之于 HTTP。通过 `Builder` 模式创建，默认使用自动配置的模型。

**Josh:** "It's cheap and easy to create as many of these chat clients as you want, but they will point to the same model which is auto-configured based on the properties."

### 2.3 System Prompt & 角色设定

```java
ChatClient chatClient = ChatClient.builder(chatModel)
    .defaultSystem("""
        You are a helpful pet adoption assistant.
        Your name is Prancer Finder.
        You help users find dogs available for adoption.
        If there's no information, return a polite response.
        """)
    .build();
```

**中文解读：** System prompt 定义 AI 助手的"人格"和行为边界。这是 RAG 之前的第一层控制，告诉模型"你是谁、要做什么"。

### 2.4 对话记忆 (Chat Memory)

```java
@Bean
public ChatMemory chatMemory() {
    return new InMemoryChatMemory();
}

@Bean
public Advisor chatMemoryAdvisor(ChatMemory chatMemory) {
    return new MessageChatMemoryAdvisor(chatMemory);
}
```

**Josh:** "This is just the most simplest form of memory. There's other forms - maybe you want automatic summarization, keeping track of the conversation. And then we inject this advisor into the system."

**中文解读：** Spring AI 通过 Advisor 链实现对话记忆，类似拦截器模式：
- **MessageChatMemoryAdvisor**：将历史消息添加到每次请求中
- 支持 **Prompt Caching** (Spring AI 1.1+)：减少重复 token 消耗

---

## 三、RAG (检索增强生成)

> "RAG is Retrieval Augmented Generation. This is the way to get data into our prompt to be sent to the LLM."

### 3.1 向量存储配置

```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/pgvector
spring.ai.vectorstore.pgvector.index-type=HNSW
spring.ai.vectorstore.pgvector.distance-type=COSINE
spring.ai.vectorstore.pgvector.dimension=1536
```

**中文解读：** 使用 PostgreSQL + pgvector 作为向量数据库。向量维度需与嵌入模型输出维度一致（如 Ada-002 为 1536 维）。

### 3.2 文档嵌入流程

```java
// 1. 加载文档
Document doc = new Document("Prancer is a demonic, neurotic dog...");
// 2. 嵌入并存入向量库
vectorStore.add(List.of(doc));
// 3. 配置 QA Advisor (RAG)
@Bean
public Advisor qaAdvisor(VectorStore vectorStore) {
    return new QuestionAnswerAdvisor(vectorStore, SearchRequest.defaults());
}
```

**中文解读：** RAG 的核心流程：
1. 用户查询 → 嵌入为向量
2. 向量库相似度搜索（cosine similarity）
3. 返回 Top-K 相关文档片段
4. 注入到 prompt 中一并发给 LLM
5. LLM 基于这些上下文生成回答

### 3.3 结构化输出 (Structured Output)

```java
// 告诉 LLM 返回 JSON，自动反序列化为 Java 对象
ChatClient chatClient = ChatClient.builder(chatModel)
    .build();

Dog dog = chatClient.prompt()
    .user("Tell me about Prancer the dog")
    .call()
    .entity(Dog.class);  // 自动解析为 Dog 对象
```

**中文解读：** `entity()` 方法是 Spring AI 的亮点。它：
1. 在 prompt 中附加格式指令（"返回 JSON，字段为 name, age, description"）
2. LLM 返回 JSON
3. 自动反序列化为 Java POJO

这样就不用自己写 JSON 解析代码，类型安全。

### 3.4 RAG 的挑战

**Josh:** "The challenging piece with AI is deciding like what do you put into the prompt. Do you re-embed data every time even when unnecessary? It gets tricky."

**中文解读：** RAG 的实际工程难点：
- 什么时候需要重新嵌入（re-embed）数据？
- 上下文窗口满了怎么办？
- 多数据源如何分块和检索？
- 如何避免"幻觉"——给的不相关信息误导 LLM

---

## 四、MCP (Model Context Protocol) 工具调用

> "Let's take advantage of remote tool calling via MCP."  
> "This is all brand new as of last week."

### 4.1 MCP 是什么

MCP 是 Anthropic 提出的开放协议，让 LLM 调用远程工具/服务。相当于"LLM 的 API 网关"。

### 4.2 MCP 服务端实现

```java
@SpringBootApplication
public class McpServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(McpServerApplication.class, args);
    }
    
    @Bean
    public ToolCallbackProvider scheduleTool() {
        return MethodToolCallbackProvider.builder()
            .toolObjects(new ScheduleTool())
            .build();
    }
}

// 工具实现
@Component
public class ScheduleTool {
    
    @Tool(description = "Schedule a dog pickup at a specific time")
    public String schedulePickup(
        @ToolParam(description = "The dog's name") String dogName,
        @ToolParam(description = "Date and time") String dateTime
    ) {
        return "Pickup scheduled for " + dogName + " on " + dateTime;
    }
}
```

**中文解读：** MCP 工具 = LLM 能调用的后端 API。
- `@Tool` 注解标识这是一个 AI 可用的工具
- `@ToolParam` 描述参数（LLM 根据描述决定传什么值）
- `MethodToolCallbackProvider` 自动注册工具

### 4.3 MCP 客户端集成

```properties
# Spring AI MCP 客户端配置
spring.ai.mcp.client.enabled=true
spring.ai.mcp.server.url=http://localhost:8081
```

**中文解读：** Spring AI 1.1+ 支持自动发现和调用 MCP 服务端。AI Agent 在推理过程中，如果需要排期等能力，会自动调用 MCP 工具。

### 4.4 MCP Inspector

Josh 展示了 MCP Inspector 工具（官方测试 UI），可以：
- 查看所有注册的工具
- 手动触发工具调用
- 模拟 LLM 调用工具的流程

**中文解读：** MCP Inspector 是调试 AI Agent 工具调用的利器。在没有 LLM 的情况下也能验证工具行为。

### 4.5 从本地工具到 MCP

**Josh:** "The benefit of this approach is that you can take the code we had for the local tool calling and just copy and paste it and it's there."

```java
// 本地工具
@Bean
public ToolCallbackProvider localTool() {
    return MethodToolCallbackProvider.builder()
        .toolObjects(new LocalTool())
        .build();
}

// 远程 MCP 工具 - 逻辑几乎相同，只是通过 HTTP 暴露
// 客户端通过 MCP 协议自动发现和调用
```

**中文解读：** MCP 的优雅之处：本地工具 → 远程 MCP 工具的迁移成本极低。接口定义一致，只是部署模式不同。

---

## 五、Spring AI Agent 构建要点

### 5.1 Agent 的本质

Agent = LLM + 工具 + 记忆 + 规划

Spring AI 中通过 ChatClient + Advisor + Tool 的组合实现：
- `ChatClient` — LLM 交互
- `Advisor` — 记忆、RAG、安全过滤
- `Tool` / MCP — 外部能力

### 5.2 完整工作流

```
用户请求 → System Prompt(角色) → ChatMemory(历史) 
  → RAG(向量检索上下文) → LLM 推理 → 工具调用(MCP)
  → 工具结果返回 → LLM 综合回答 → 结构化输出
```

### 5.3 Spring AI 1.1 新特性 (整理)

| 特性 | 说明 |
|------|------|
| **Prompt Caching** | 缓存重复 prompt 片段，减少 token 消耗 |
| **MCP 客户端自动配置** | 一行配置即可接入 MCP 服务 |
| **方法级工具回调** | 通过 `@Tool` 注解简化工具定义 |
| **ChatClient 流式调用** | stream() 方法支持 SSE 流式响应 |

---

## 六、工程最佳实践 & 洞察

### 6.1 值得注意的细节

1. **环境差异**：Josh 提到 workshop 基于 Spring AI 1.0 编写但使用 1.1 演示 — 技术演讲中版本兼容性是个常见坑
2. **target 目录缓存**：遇到诡异的构建问题，先删 `target/` 再试 (Maven 缓存问题)
3. **Prompt Engineering 直播**："We're live prompt engineering" — 现场调试 prompt 是常态

### 6.2 推荐的学习路径

1. **先掌握 Spring Boot 基础**：自动配置、Starters、Actuator
2. **Spring AI ChatClient**：理解 prompt → call → content 的基本模式
3. **RAG 实现**：向量存储 + QA Advisor
4. **工具调用**：从本地 @Tool 到远程 MCP
5. **Agent 编排**：组合记忆 + RAG + 工具

### 6.3 后续资源

- Spring AI 官方文档: https://docs.spring.io/spring-ai/reference/
- Spring AI GitHub: https://github.com/spring-projects/spring-ai
- MCP Java SDK: https://github.com/modelcontextprotocol/java-sdk
- Spring AI by the Bay (该 Workshop 相关活动)

---

> **整理说明**：本文基于 Workshop 字幕内容提炼，重点覆盖 Spring Boot 自动配置、Spring AI ChatClient、RAG、MCP、Agent 等核心主题。原 workshop 为 2 小时现场互动形式，包含大量演示调试和设备切换过程，此文档仅保留结构化技术内容。
