# Dan Vega — AI for Java Developers: Full Course / Workshop 精要

> **视频**: [AI for Java Developers: Full Course / Workshop on Getting Started with Spring AI](https://youtu.be/FzLABAppJfM)  
> **主讲**: Dan Vega | **时长**: 5h 37min  
> **内容**: Spring AI 从零到一，含 RAG、MCP、Observability、Evaluation 全栈覆盖  
> **中文整理**: 根据字幕归纳核心内容

---

## 一、课程概览

> "Today we're going to see what it takes to build AI-powered applications using Spring AI. Whether you have a project at work or you're just wanting to learn, this course covers everything you need."

**Agenda:**
1. What is AI? (概念扫盲)
2. Getting Started (Spring AI 基本使用)
3. Structured Output (结构化输出)
4. LLM Limitations & RAG (大模型局限性与 RAG)
5. Tools & Function Calling (工具调用)
6. MCP (Model Context Protocol)
7. Observability (可观测性)
8. Evaluations / Testing (模型评估与测试)

---

## 二、Spring AI 入门

### 2.1 创建项目

```java
// Write your first application that talks to an LLM
@SpringBootApplication
public class AiApplication {
    public static void main(String[] args) {
        SpringApplication.run(AiApplication.class, args);
    }
}
```

### 2.2 ChatClient 基本使用

**Dan:** "The ChatClient is a Fluent API similar to WebClient, designed for interacting with AI models."

```java
ChatClient chatClient = ChatClient.builder(chatModel).build();

String response = chatClient.prompt()
    .user("Tell me about Spring AI")
    .call()
    .content();

System.out.println(response);
```

**中文解读：** `ChatClient` 是 Spring AI 的核心门面，提供流式 API（类似 `WebClient`）。默认由自动配置注入 `ChatModel` bean，支持多模型提供商（OpenAI, Bedrock, Ollama 等）。

### 2.3 System Message & User Message

```java
String response = chatClient.prompt()
    .system("You are a helpful Java expert. Answer in simple terms.")
    .user("What is dependency injection?")
    .call()
    .content();
```

**中文解读：** Prompt 由 system message（角色设定）+ user message（用户提问）组成。System message 在整个对话周期内生效。

### 2.4 Prompt Templates

```java
String response = chatClient.prompt()
    .user(u -> u.text("""
        Tell me about {topic} in the context of {framework}
        """)
        .param("topic", "dependency injection")
        .param("framework", "Spring Boot"))
    .call()
    .content();
```

**中文解读：** Prompt templates 类似 `MessageFormat`，支持占位符替换。避免了字符串拼接的安全和可维护性问题。

---

## 三、Structured Output（结构化输出）

> "If you want a much more structured output, you can use structured output that will return JSON format guaranteed."

### 3.1 BeanOutputConverter

```java
// 定义 POJO
public record ActorFilms(String actor, List<String> films) {}

// 使用结构化输出
BeanOutputConverter<ActorFilms> converter = 
    new BeanOutputConverter<>(ActorFilms.class);

String response = chatClient.prompt()
    .user("List Tom Hanks' top 5 movies")
    .call()
    .content();

ActorFilms result = converter.convert(response);
// result.actor() → "Tom Hanks"
// result.films() → ["Forrest Gump", "Cast Away", ...]
```

### 3.2 ChatClient.entity() 快捷方式

```java
ActorFilms result = chatClient.prompt()
    .user("List Tom Hanks' top 5 movies")
    .call()
    .entity(ActorFilms.class);
```

**中文解读：** `entity()` 方法内部做了三件事：
1. 自动生成格式指令追加到 prompt（"请返回 JSON，模式为..."）
2. 调用 LLM 获取响应
3. 反序列化为指定 Java 类型

**Dan:** "Structured output — big big fan of it. This is a game changer for integrating AI responses into your application."

---

## 四、RAG（检索增强生成）

> "RAG is like giving AI a search engine. You can take your data, chunk it, embed it, store it, and retrieve relevant context."

### 4.1 基本流程

```
用户查询 → 嵌入 → 向量搜索(相似度) → 取 Top-K 片段 → 注入 prompt → LLM 生成回答
```

### 4.2 配置 RAG

```java
@Configuration
public class RagConfiguration {
    
    @Bean
    public VectorStore vectorStore(EmbeddingModel embeddingModel) {
        return new PgVectorStore(embeddingModel);
    }
    
    @Bean
    public Advisor questionAnswerAdvisor(VectorStore vectorStore) {
        return new QuestionAnswerAdvisor(
            vectorStore, 
            SearchRequest.defaults()
                .withTopK(5)
        );
    }
}
```

### 4.3 文档分块（Chunking）

**Dan:** "Instead of having one long paragraph, you could split it by paragraph, you could split it by sentence, add overlap to maintain context."

```java
// 文档分块策略
Document document = new Document("long text...");
TokenTextSplitter splitter = new TokenTextSplitter();
List<Document> chunks = splitter.apply(List.of(document));
```

**中文解读：** 分块是 RAG 的关键——块太大精度下降，块太小上下文丢失。常见策略：
- 按段落/句子分割
- Token 数固定（如 512 tokens）
- 加重叠（overlap）保持上下文连贯

### 4.4 RAG 注意事项

1. **向量维度一致性**：嵌入模型输出维度需与向量库配置一致
2. **Top-K 选择**：太少可能漏相关信息，太多可能超上下文窗口
3. **嵌入模型选择**：权衡质量 vs 成本（Ada-002 性价比高）
4. **元数据过滤**：对搜索结果按元数据（日期、类别等）做二次过滤

---

## 五、Tool Calling & Function Calling

> "Tool calling, also known as function calling, is a common pattern in AI applications. The LLM decides when to call a tool."

### 5.1 定义工具

```java
@Component
public class DateTimeTools {
    
    @Tool(description = "Get the current date and time")
    public String getCurrentDateTime() {
        return LocalDateTime.now().toString();
    }
    
    @Tool(description = "Calculate days between two dates")
    public long daysBetween(
            @ToolParam(description = "Start date (yyyy-MM-dd)") String start,
            @ToolParam(description = "End date (yyyy-MM-dd)") String end) {
        return ChronoUnit.DAYS.between(
            LocalDate.parse(start), LocalDate.parse(end));
    }
}
```

### 5.2 注册工具

```java
ChatClient chatClient = ChatClient.builder(chatModel)
    .defaultTools(new DateTimeTools())
    .build();
```

**中文解读：** 声明式工具注册：
- `@Tool` — 标注方法为 AI 可调用工具
- `@ToolParam` — 描述参数（LLM 根据描述决定传值）
- LLM 自主决定何时调用工具（非强制）

---

## 六、MCP（Model Context Protocol）🔥

> "I'm sure you've probably heard of MCP at this point. MCP helps you build agents in complex systems."

### 6.1 MCP 概念

**Dan:** "MCP follows a client-server architecture. An MCP host can connect to multiple MCP servers. MCP servers expose tools, the MCP client connects to servers through the MCP protocol."

```
MCP Host (应用)
  ├─ MCP Client
  │    ├─ MCP Server A (Python)
  │    ├─ MCP Server B (Java)
  │    └─ MCP Server C (Node.js)
  └─ AI Model
```

**中文解读：** MCP 是 AI 版的"API 网关"——不同语言的服务通过 MCP 协议统一暴露工具给 AI Agent 调用。

### 6.2 构建 MCP Server

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-mcp-server-webmvc</artifactId>
</dependency>
```

```java
@SpringBootApplication
public class McpServerApplication {
    
    @Bean
    public ToolCallbackProvider sessionTools(SessionTool sessionTool) {
        return MethodToolCallbackProvider.builder()
            .toolObjects(sessionTool)
            .build();
    }
}

@Component
public class SessionTool {
    
    @Tool(description = "Schedule a session")
    public String schedule(String topic, @ToolParam String date) {
        return "Scheduled: " + topic + " on " + date;
    }
}
```

### 6.3 MCP Inspector

```bash
# 启动 MCP Inspector 调试工具
npx @modelcontextprotocol/inspector java -jar my-mcp-server.jar
```

**Dan:** "The MCP inspector allows you to test your MCP server, see all the tools that you're registering, and test their output."

### 6.4 MCP 安全

**Dan:** "There's a newer spec on securing MCP servers using OAuth 2.0 authorization. Each MCP request will include a token, and the MCP server validates that token."

**中文解读：** MCP 安全演进：
1. **基础**：Stdio 传输（本地通信，不安全）
2. **SSE (Server-Sent Events)**：HTTP 传输，支持认证
3. **OAuth 2.0**：MCP 新规范，标准授权流程

### 6.5 MCP vs. 本地 @Tool

| 维度 | 本地 @Tool | MCP |
|------|-----------|-----|
| 部署 | 同进程 | 独立服务 |
| 语言 | 仅 Java | 任意语言 |
| 复用 | 仅当前应用 | 跨应用/团队共享 |
| 发现 | 编译时注册 | 运行时协议发现 |
| 安全 | 应用内控制 | OAuth/Token 控制 |

---

## 七、Observability（可观测性）

> "Observability was rewritten from the ground up in Spring Boot 3."

### 7.1 三大支柱

**Dan:** "Metrics, logs, and traces — end-to-end view of our RAG pipeline."

```properties
# 开启 AI 可观测性
management.tracing.enabled=true
management.endpoints.web.exposure.include=*
```

**关键指标：**
- **平均响应时间** (Average Response Time)
- **成功率** (Success Rate)
- **Token 消耗** (Input/Output Tokens)
- **模型调用延迟**

### 7.2 Token 监控

```java
// Micrometer 自动收集 AI 指标
// 可通过 /actuator/metrics 查看
// spring.ai.chat.client.requests
// spring.ai.chat.tokens.total
```

**中文解读：** Spring AI 内置了 Micrometer 指标收集，无需额外代码即可监控 token 消耗、调用延迟、成功率等关键指标。

---

## 八、Evaluations & Testing（模型评估）

> "Traditional software testing works great when you know the expected output. With LLMs, the output is non-deterministic — it can return different things every time."

### 8.1 评估挑战

**Dan:** "LLM responses are non-deterministic — the same input can produce different outputs each time. This makes evaluation challenging."

### 8.2 Spring AI Evaluators

```java
// RAG 评估 - 检查答案是否基于提供的上下文
EvaluationRequest request = new EvaluationRequest(
    userPrompt,        // 用户提问
    context,           // RAG 提供的上下文
    response           // LLM 生成的回答
);

// 相关性评估
RelevanceEvaluationEvaluator relevanceEval = 
    new RelevanceEvaluationEvaluator(chatModel);

EvaluationResponse evalResult = relevanceEval.evaluate(request);
// evalResult.isPass() → true/false
```

### 8.3 评估类型

| 评估方法 | 用途 |
|---------|------|
| **RelevanceEvaluator** | 检查回答是否基于上下文（RAG 专用） |
| **StructuredOutputEvaluator** | 验证输出是否符合 JSON Schema |
| **Custom Evaluator** | 自定义评估逻辑 |

### 8.4 测试结构化输出

```java
@Test
void testStructuredOutput() {
    ChatClient chatClient = ChatClient.builder(chatModel).build();
    
    ActorFilms result = chatClient.prompt()
        .user("List Tom Cruise's top 3 movies")
        .call()
        .entity(ActorFilms.class);
    
    assertThat(result.actor()).isEqualTo("Tom Cruise");
    assertThat(result.films()).hasSize(3);
}
```

---

## 九、总结与学习路径

**Dan:** "We covered so much — RAG, tool calling, MCP, observability, and evaluations."

### 推荐实践路径

1. **入门**：ChatClient → Prompt Template → Structured Output
2. **进阶**：RAG → Tool Calling → MCP
3. **运维**：Observability → Evaluation
4. **生产**：MCP Security → Custom Evaluators

### 关键金句

> *"If you can use Java and Spring, you can build AI-powered applications today — no PhD in machine learning needed."*  
> *"The first step is getting started. Create a project, write a ChatClient, and you're already building with AI."*

---

> **关联阅读**：Christian Tzolov 在 Spring I/O 的演讲「[从助手到智能体](/ai-tools/spring-ai/from-assistants-to-agents-self-improving-agentic-systems.md)」深入讲解了 Advisor 模式和 Agent 演进框架，与本文实操内容互补——建议先实操再读理论框架。
>
> **整理说明**：本文基于 5.5h Workshop 字幕提炼，原课程包含大量实时编码演示，此处仅保留结构化技术内容。完整课程可在 [Dan Vega 的 YouTube](https://youtu.be/FzLABAppJfM) 观看。
