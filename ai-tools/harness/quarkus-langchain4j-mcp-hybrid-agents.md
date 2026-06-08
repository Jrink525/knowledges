---
title: "Quarkus + LangChain4j + MCP：构建混合型 Tool Agent"
tags:
  - quarkus
  - langchain4j
  - mcp
  - agent-pattern
  - java-agent
  - mcp-tools
  - hybrid-agents
  - agent-architecture
date: 2026-05-12
source: "https://www.the-main-thread.com/p/quarkus-langchain4j-mcp-tool-agents"
authors: "The Main Thread"
---

# Quarkus + LangChain4j + MCP：构建混合型 Tool Agent

> **来源：** The Main Thread  
> **原文：** Build Hybrid MCP Tool Agents in Quarkus  
> **代码：** [GitHub - myfear/the-main-thread/conduit-hybrid-agents](https://github.com/myfear/the-main-thread/tree/main/conduit-hybrid-agents)

---

## 核心论点

> 我一边觉得 Agent 工作流很酷，一边在发现有人把 `trim().toUpperCase()` 变成一个规划问题时就很头疼。

流水线里的有些步骤需要语言判断力。有些步骤只需要做一件确定的、快的事，然后停止。哈希一个 payload、清理一个记录 ID、执行一个固定的映射——这些事加入模型只会变慢、变难推理，不会变好。

这就是为什么 LangChain4j 的 `langchain4j-agentic-mcp` 模块值得关注。它让 MCP 工具作为节点出现在 Agentic Graph 中——拓扑结构依然精确描述工作流，而那些无聊的阶段保持无聊。

---

## 架构概览：Conduit 示例

一个混合系统，拆成两个 Quarkus 应用：

```
┌──────────────────────────────────────────────────────────────┐
│                    conduit-workflow                          │
│                                                              │
│  POST /runs ──▶ conduitPipeline (5-stage sequence) ──▶ queue │
│                                                              │
│  Normalize ─▶ Classify ─▶ Fingerprint ─▶ Summarize ─▶ Route  │
│  (MCP Tool)    (LLM)       (MCP Tool)    (LLM)      (LLM)   │
│      │                        │                              │
│      └──────── Streamable HTTP MCP ──────────┘              │
│                           │                                  │
│                    conduit-mcp-server                        │
│                    /mcp endpoint                             │
│                    Tool: normalize_record                    │
│                    Tool: fingerprint_payload                 │
│                                                              │
│  AgentMonitor ──▶ GET /topology (HTML 拓扑图)                │
└──────────────────────────────────────────────────────────────┘
```

### 关键设计原则

**确定性步骤交给工具，判断性步骤交给 LLM，在同一个拓扑图中共存。**

### 五个阶段的流水线

| 阶段 | 类型 | 职责 |
|------|------|------|
| `conduit_normalize_record` | MCP Tool (确定的) | 去空格、大写 record ID，纯逻辑 |
| `classifySeverity` | LLM Agent | 从 payload 中推断严重级别 |
| `conduit_fingerprint_payload` | MCP Tool (确定的) | 对 payload 做 SHA-256 哈希 |
| `summarizeHandoff` | LLM Agent | 生成交接摘要 |
| `routeQueue` | LLM Agent | 路由到目标队列 |

---

## 项目结构

```
conduit-hybrid-agents/
├── conduit-mcp-server/          # MCP 工具服务器
│   └── src/main/java/dev/conduit/mcp/
│       └── ConduitMcpTools.java
├── conduit-workflow/            # 工作流编排
│   └── src/main/java/dev/conduit/workflow/
│       ├── config/ConduitMcpConfig.java
│       ├── agent/ClassifySeveritySpecialist.java
│       ├── agent/SummarizeHandoffSpecialist.java
│       ├── agent/RouteQueueSpecialist.java
│       ├── agent/ConduitTopology.java
│       └── resource/
│           ├── RunRequest.java / RunResponse.java
│           └── TopologyResource.java
└── pom.xml (aggregator)
```

---

## 构建步骤

### 1. 创建模块

```bash
mkdir conduit-hybrid-agents && cd conduit-hybrid-agents

quarkus create app dev.conduit:conduit-mcp-server \
  --extension=quarkus-mcp-server-http \
  --java=25 --no-code --package-name=dev.conduit.mcp

quarkus create app dev.conduit:conduit-workflow \
  --extension=quarkus-rest-jackson,quarkus-langchain4j-ollama \
  --java=25 --no-code --package-name=dev.conduit.workflow
```

### 2. 关键依赖（workflow 模块）

```xml
<dependency>
  <groupId>dev.langchain4j</groupId>
  <artifactId>langchain4j-agentic</artifactId>
</dependency>
<dependency>
  <groupId>dev.langchain4j</groupId>
  <artifactId>langchain4j-agentic-mcp</artifactId>
</dependency>
<dependency>
  <groupId>io.rest-assured</groupId>
  <artifactId>rest-assured</artifactId>
  <scope>test</scope>
</dependency>
```

MCP Server 测试依赖：
```xml
<dependency>
  <groupId>io.quarkiverse.mcp</groupId>
  <artifactId>quarkus-mcp-server-test</artifactId>
  <scope>test</scope>
</dependency>
```

### 3. 配置

**conduit-mcp-server** — `application.properties`：
```properties
quarkus.application.name=conduit-mcp-server
quarkus.http.port=8090
```

**conduit-workflow**：
```properties
quarkus.application.name=conduit-workflow
conduit.mcp.server-url=http://127.0.0.1:8090/mcp
quarkus.langchain4j.ollama.base-url=http://localhost:11434
quarkus.langchain4j.ollama.chat-model.model-id=llama3.2
```

### 4. 确定性 MCP 工具（纯逻辑，无模型）

```java
@Tool("Normalize a record ID: strip whitespace, uppercase")
public String conduit_normalize_record(String rawId) {
    if (rawId == null || rawId.isBlank()) return "";
    return rawId.strip().toUpperCase();
}

@Tool("Fingerprint a payload: SHA-256 hex digest")
public String conduit_fingerprint_payload(String payloadSnippet) {
    // ... 纯确定性哈希
}
```

> 📌 这里没有任何模型参与，这正是关键。

### 5. LLM Agent 定义

每个阶段有且只有一个职责：

```java
@CreatedAware
public class ClassifySeveritySpecialist {
    // Prompt 刻意狭小：分类，不是写小说
    String systemPrompt = """
        You are a severity classifier.
        Analyze the payload and respond with exactly one label:
        HIGH, MEDIUM, or LOW.
        """;
}
```

> 每个阶段有**一个工作**。如果 promt 漂移到模糊的"helpful assistant"领域，拓扑图看起来还很干净，但输出已经不可信了。

### 6. 组装拓扑图

```java
// MCP 工具变成 Agent 节点
McpAgent agentNormalize = McpAgent.builder()
    .mcpClient(mcpClient)
    .toolName("conduit_normalize_record")
    .input("rawId")
    .output("canonical_record_id")
    .build();

// LLM Agent
Agent classifySeverity = AgenticServices.agentBuilder(ClassifySeveritySpecialist.class)
    .chatModel(chatModel)
    .build();

// 五阶段顺序执行 + 监控
SequentialSequence sequence = SequentialSequence.from(
    agentNormalize, classifySeverity, agentFingerprint,
    summarizeHandoff, routeQueue
);
```

### 7. API 端点

```java
@POST
@Path("/runs")
public RunResponse run(RunRequest req) {
    if (req.rawId() == null || req.rawId().isBlank()) {
        throw new ValidationException("rawId required");
    }
    // 执行五阶段流水线
    String result = sequence.run(Map.of(
        "rawId", req.rawId(),
        "payloadSnippet", req.payloadSnippet()
    ));
    return new RunResponse(result);
}

@GET
@Path("/topology")
public String topology() {
    return HtmlReportGenerator.generateReport(topology);
}
```

---

## 两个重要设计细节

### 1. `@CreatedAware` 与 Quarkus 集成

```java
AgenticServices.agentBuilder(ClassifySeveritySpecialist.class)
```
这里 `@CreatedAware` 确保了 Quarkus 友好的创建语义。Agent 创建时自动完成依赖注入和生命周期管理。

### 2. AgentMonitor 实时拓扑渲染

```
AgentMonitor 监控器挂在 sequence 根节点
            ↓
LangChain4j 在运行时渲染 HTML 拓扑报告
            ↓
GET /topology 返回完整的 Agent 调用图
```

这在调试复杂工作流时非常有价值——你能看到哪个阶段跑了、哪个没跑、数据流转。

---

## 测试策略：全链路集成测试

**没有桩（No stub）。没有假模型。没有 MCP 客户端模拟。**

测试方式：

1. **McpAssured** 直接对 MCP Server 模块发送 Streamable HTTP 请求，验证工具边界
2. **ConduitWorkflowIT** 在测试执行前：
   - 打包 conduit-mcp-server → 可执行 jar
   - 在空闲 localhost 端口启动 MCP Server jar
   - 覆盖 `conduit.mcp.server-url` 指向该实例
   - 对真实 Ollama 运行完整工作流

```java
// 集成测试验证链
/topology 在运行前→证明 MCP 发现调用成功了
POST /runs→验证返回的 targetQueue 在预期范围
/topology 运行后→验证两个 MCP 工具名出现在报告中
```

这种测试策略最大限度地减少了"单元测试通过但整合就崩"的类问题。

---

## 实战对比：三种模式的适用场景

| 模式 | 适用场景 | 代价 |
|------|---------|------|
| 进程内 `@Tool` | 不需要 MCP 边界的确定性逻辑 | 零额外开销 |
| `McpAgent` | MCP 后的确定性逻辑，但需要在工作流图中可见 | MCP 传输开销 |
| `AgentBuilder.chatModel()` | 需要语言判断、总结、模糊路由 | 推理成本 + 不可确定性 |

> **选不对形态，你付两次代价：** 不必要的延迟 + 你本来就不想要的不可确定性。

---

## 常见错误

| 错误 | 表现 | 修复 |
|------|------|------|
| **MCP URL 指向服务器根路径** | 工作流无法完成 MCP 握手 | 指向 `/mcp` endpoint：`http://127.0.0.1:8090/mcp` |
| **Ollama 可达但模型不存在** | LLM 阶段在到达时直接失败 | 先 `ollama pull llama3.2` |
| **拓扑页暴露到公网** | 安全和混淆信息泄露 | 加认证守卫 |
| **输入/输出 key 拼写错误** | 静默死链（silence dressed as orchestration） | 确认数据契约 key 名一致 |

---

## 生产环境考虑

本 demo 刻意精简，生产化需要：

- **MCP 调用的重试策略**
- **追踪导出**（如 OpenTelemetry）
- **`/runs` 的限流**
- **超时预算**（每个 MCP hop 允许的延迟预算）
- **跨信任边界的密钥管理**
- **MCP 服务器部署模式**（sidecar 或需 mTLS）

---

## 核心收获

架构规律很简单：

> **如果一个步骤是确定且廉价的，就保持它确定。**

Tool Agent 的价值在于让你保持这个边界可见——而不是因为 API 能做就把所有事情都塞进 ChatModel。

---

## 与知识库其他文章的关联

- **[SpringIO 2026: Comparing Agentic AI Frameworks for Java](../frameworks/springio-2026-comparing-agentic-ai-frameworks-for-java.md)** — 本文是 LangChain4j 生态的具体实现示例，展示了 `langchain4j-agentic` 和 `langchain4j-agentic-mcp` 模块的实际用法
- **[Agent Harness Engineering](agent-harness-engineering.md)** — Harness 理论中的"工具生态"和"编排逻辑"在本项目中得到具体实践
- **[SKILLIFY: Skill Engineering Guide](skillify-skill-engineering-guide.md)** — 确定性步骤→`scripts/` 与 `McpAgent` 的模式本质一致

*Processed on 2026-05-12 from the-main-thread.com*
