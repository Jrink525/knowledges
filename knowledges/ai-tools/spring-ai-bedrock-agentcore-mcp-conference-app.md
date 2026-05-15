# Spring AI + Amazon Bedrock AgentCore：构建 AI Agent 的完整实战

> 原文系列：Building AI Agents with Spring AI and Amazon Bedrock AgentCore — Part 1~6
> 作者：Vadym Kazulkin (DevOps/Java 专家, AWS 社区贡献者)
> 仓库：<https://github.com/Vadym79/amazon-bedrock-agentcore-spring-ai>

---

## 一、系列概述

本系列以"**会议检索应用 (Conference Search)**"为实战案例，完整展示如何用 **Spring AI** + **Amazon Bedrock AgentCore** 构建企业级 AI Agent。

### 应用场景

一个技术会议搜索 Agent，支持：
- 按主题（如 Java、AI、DevOps）搜索会议
- 按日期范围筛选
- 按 CFP (Call for Papers) 开放时间搜索
- 用户用自然语言提问，Agent 自动调用对应工具

### 全系列架构总览

```
┌─────────────────────────────────────────────────────────────────────┐
│                          应用的演进维度                              │
│                                                                     │
│  Part 1             Part 2                  Part 3                  │
│  ┌──────────┐      ┌──────────────┐       ┌─────────────┐          │
│  │ MCP      │ ──►  │ 部署到        │ ──►  │ 本地 MCP    │          │
│  │ Server   │      │ AgentCore    │       │ Client      │          │
│  │ (Spring) │      │ Runtime +    │       │ (Spring     │          │
│  └──────────┘      │ CDK + Cognito│       │  ChatClient)│          │
│                    └──────────────┘       └─────────────┘          │
│                                                                     │
│  Part 4                      Part 5                  Part 6         │
│  ┌────────────────────┐     ┌────────────────────┐  ┌────────────┐ │
│  │ Streamable HTTP    │     │ Spring AI Custom   │  │ ADOT       │ │
│  │ 传输协议深度        │     │ Agent 部署到       │  │ 可观测性    │ │
│  │ (MCP Inspector /   │     │ AgentCore Runtime  │  │ (Collector │ │
│  │  Amazon Q)         │     │ (Java Agent)       │  │ -less)    │ │
│  └────────────────────┘     └────────────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 系列导航

| 章节 | 内容 | 来源 |
|---|---|---|
| 核心概念 | Spring AI / AgentCore / MCP / Streamable HTTP | Part 1 |
| Part 1 | 会议检索 MCP Server 设计，4 个 Tool 的领域模型 | Part 1 |
| Part 2 | 部署到 AgentCore Runtime：CDK / Docker→ECR / Cognito JWT / IAM | Part 2 |
| Part 3 | 本地 MCP Client：ChatClient / JWT 获取 / Streamable HTTP 客户端 | Part 3 |
| Part 4 | Streamable HTTP 传输协议：MCP Inspector / Amazon Q / 安全配置 | Part 4 ② |
| Part 5 | Spring AI 作为 Custom Agent 部署到 AgentCore Runtime | Part 5 ② |
| Part 6 | ADOT 可观测性：Collector-less OpenTelemetry → CloudWatch | Part 6 ② |
| 最佳实践 | Stateless vs Stateful / Runtime vs Gateway / 部署速查 / 已知问题 | Parts 1~3 |
| 未来扩展 | Memory / Embabel / ADOT / Spring Boot 4 适配 / Gateway | Parts 1~3 |

> ② = Spring AI with Amazon Bedrock 系列 (dev.to/vkazulkin/series/32829)
> Parts 1~3 = Building AI Agents with Spring AI and Amazon Bedrock AgentCore 系列

### 完整技术栈

| 组件 | 技术 |
|---|---|
| 框架 | Spring AI 1.1.x，Spring Boot 3.x / 4.x（未来） |
| LLM | Amazon Bedrock（Bedrock Converse API） |
| Agent 运行时 | Amazon Bedrock AgentCore Runtime + Gateway |
| 模型上下文协议 | Model Context Protocol (MCP) — Streamable HTTP |
| MCP 客户端工具 | MCP Inspector（Docker）、Amazon Q Developer |
| 身份认证 | Amazon Cognito（JWT OAuth2） |
| 基础设施 | AWS CDK (Java L2 Construct) + CloudFormation |
| 容器 | Docker → ECR |
| 可观测性 | AWS Distro for OpenTelemetry (ADOT) + CloudWatch GenAI |
| 替代方案 | Embabel Agent Framework（构建于 Spring AI 之上） |

---

## 二、核心概念速览

### 2.1 Spring AI

Spring AI 是 Spring 生态的 AI 集成框架，提供：
- **ChatClient** — 统一的 LLM 对话接口
- **MCP 客户端/服务端** — 原生支持 Model Context Protocol（STDIO/SSE/Streamable HTTP）
- **Tool (工具) 机制** — 将任意 Spring Bean 暴露为 AI Agent 可调用的工具
- **模型适配器** — 统一接口对接 Bedrock、OpenAI、Anthropic 等

### 2.2 Amazon Bedrock AgentCore

AgentCore 是 AWS 的 AI Agent 托管服务，包含两个核心组件：

| 组件 | 用途 |
|---|---|
| **AgentCore Runtime** | 运行 AI Agent / MCP Server 的托管环境（类似 Lambda） |
| **AgentCore Gateway** | 托管 MCP Server 网关，跨 Runtime 暴露工具（类似 API Gateway） |

### 2.3 MCP (Model Context Protocol)

MCP 是 LLM 与外部工具/数据源交互的标准协议。支持三种传输方式：

| 传输方式 | 连接模型 | 适用场景 | 状态管理 |
|---|---|---|---|
| **STDIO** | 子进程 stdin/stdout | 本地 Agent，进程内通信 | N/A |
| **SSE** (Server-Sent Events) | HTTP 长连接 | 传统远程 MCP（已弃用） | Stateful |
| **Streamable HTTP** | HTTP 请求-响应（可选 SSE） | **推荐**：云端、AgentCore | Stateless / Stateful 均可 |

**Streamable HTTP 的关键特性：**
- **非流式响应**：所有内容在一个 HTTP 响应中返回（适合工具列表等）
- **流式响应**：通过 `text/event-stream` 逐步推送内容（适合 LLM 流式输出）
- **Stateless 模式**：一次请求一个响应，无会话状态
- **Stateful 模式**：通过 `Mcp-Session-Id` 头维持跨请求会话

> ⚠️ SSE 传输在 Spring AI 1.1 中已标记为弃用。新项目应直接使用 Streamable HTTP。

### 2.4 Spring AI AgentCore 社区项目

<https://github.com/spring-ai-community/spring-ai-agentcore>

提供 Spring AI 与 AgentCore 各服务的简便集成：
- AgentCore Runtime 集成
- AgentCore Memory（短期/长期/情景记忆）
- 降低集成复杂度

---

## 三、Part 1：会议检索应用 (MCP Server)

### 3.1 应用架构

![Spring AI 架构总览](../image/part1-spring-ai-architecture.png)

*图：Spring AI 应用中 ChatClient → LLM → Tools 的整体调用链路*

核心架构中的数据流：
```
用户 ═> [Spring AI ChatClient] ═> LLM (Bedrock)
                                    │
                                    ├── ConferenceSearchTool (get_all │ by_topic │ ...)
                                    │
                                    └── MCP Client ──> MCP Server (AgentCore Runtime)
                                                           │
                                                           └── conferences.json
```

![ChatClient + Tools 配置](../image/part1-chatclient-tools.png)

*图：ChatClient 构建与 Tool 注入配置*

![Bedrock Converse 配置](../image/part1-bedrock-converse-config.png)

*图：Amazon Bedrock Converse API 的 Spring AI 配置*

### 3.2 领域模型

Conference 类包含字段：
```java
public class Conference {
    private String conferenceId;       // 新增
    private String name;
    private String topic;
    private String location;
    private LocalDate startDate;
    private LocalDate endDate;
    private LocalDate callForPapersStartDate;  // 新增
    private LocalDate callForPapersEndDate;    // 新增
    // ...
}
```

### 3.3 暴露的工具 (Tools)

所有工具通过 `ConferenceSearchTool` 实现，共 4 个：

| 工具 | 功能 |
|---|---|
| `Conference_Search_Tool_All` | 获取全量会议列表 |
| `Conference_Search_Tool_By_Topic` | 按主题搜索 |
| `Conference_Search_Tool_By_Topic_And_Date` | 按主题+日期范围搜索 |
| `Conference_Search_Tool_By_Topic_Date_CFP_Open` | 按主题+日期+CFP 开放状态搜索 |

### 3.4 Spring AI 配置

**主要依赖**（pom.xml）：
- `spring-ai-bom` — BOM 管理
- `spring-ai-starter-model-bedrock-converse` — Bedrock LLM 适配
- `spring-ai-starter-mcp-server-webflux` — MCP Server (Streamable HTTP)
- `spring-ai-starter-mcp-client-webflux (可选)` — MCP Client (异步)

**MCP Server 配置**（application.properties）：
```properties
# Stateless Streamable-HTTP MCP Server
spring.ai.mcp.server.type=STATELESS
spring.ai.mcp.server.transport=STREAMABLE_HTTP
# MCP server endpoint
spring.ai.mcp.server.identity=conference-search-server
```

---

## 四、Part 2：部署到 AgentCore Runtime

### 4.1 总体部署架构

![AgentCore Runtime 部署架构](../image/part2-agentcore-runtime-deploy.png)

*图：AgentCore Runtime 部署全貌 — CDK → Cognito → ECR → Runtime*

核心组件交互：
```
CDK Stack ──► Cognito (JWT) ──► Runtime ──► ECR (Docker Image)
                 │                  │
                 └── MCP Client ────┘
                 (MCP Inspector / Amazon Q Dev)
```

### 4.2 AgentCore Runtime 创建（CDK）

```java
// RuntimeWithMCPStack.java — 核心栈
CfnRuntime runtime = CfnRuntime.Builder.create(this, "ConferenceSearchRuntime")
    .name("conference-search-runtime")
    .description("Conference Search Agent Runtime with MCP")
    .protocol("MCP")                           // MCP 协议
    .runtimeConfiguration(...)                  // ECR 镜像配置
    .authorizationConfiguration(               // JWT 认证配置
        AuthorizationConfiguration.builder()
            .inboundAuthenticationType("JWT")
            .jwtConfiguration(
                JwtConfiguration.builder()
                    .jwtDiscoveryUrl(cognitoDiscoveryUrl)
                    .allowedClientIds(List.of(userClientPoolId))
                    .build()
            )
    )
    .executionRole(iamRole.roleArn)
    .build();
```

输出变量：`RuntimeIdOutput` — 后续 MCP Client 需要用到。

### 4.3 容器化与 ECR

**方式一：Dockerfile**
```bash
aws ecr get-login-password --region {region} | \
  docker login --username AWS --password-stdin {account_id}.dkr.ecr.{region}.amazonaws.com

# 构建并推送
docker build -t conference-search-mcp-server ../../
docker tag conference-search-mcp-server:latest \
  {account_id}.dkr.ecr.{region}.amazonaws.com/conference-search-mcp-server:v1
docker push {account_id}.dkr.ecr.{region}.amazonaws.com/conference-search-mcp-server:v1
```

**方式二：Buildpack（无需 Dockerfile）**
```bash
mvn spring-boot:build-image
# 再用 docker tag/push 到 ECR
```

**cdk.json 配置映像 URI：**
```json
{
  "ecrImageURIForConferenceSearchAndApplicationAppAsMCPServer": "{AWS_ACCOUNT_ID}.dkr.ecr.{region}.amazonaws.com/conference-search-mcp-server:v1"
}
```

工具类 `ConventionalDefaults.getContextVariableValueWithReplacedAccountId()` 自动替换占位符。

### 4.4 Cognito JWT 认证

创建认证流水分三步：

| 序号 | 步骤 | CDK 栈 |
|---|---|---|
| 1 | 创建 Cognito User Pool | `UserPoolStack` |
| 2 | 创建 Resource Server + Scope | `UserPoolStack`（同上） |
| 3 | 创建 User Client Pool + Domain | `UserClientPoolStack` |

**踩坑记录**：CDK 创建 Cognito Domain 时存在 bug（[aws-cdk#37514](https://github.com/aws/aws-cdk/issues/37514)），domain prefix 必须与 user pool ID 完全一致（仅转小写+去下划线），但 CDK 目前自动生成的 prefix 不符合要求。

**临时解决方案**：
1. 先注释掉 domain 创建
2. 单独部署 `UserClientPoolStack` 获取 `CognitoUserPoolIdOutput`
3. 将 `cognitoUserPoolId` 写入 `cdk.json`
4. 取消 domain 创建注释（此时使用精确的 pool ID）
5. 重新部署

**部署命令：**
```bash
# 单独部署 Cognito 栈
cdk deploy spring-ai-conference-search-user-client-pool-stack \
  --parameters AWSAccountId={account_id}

# 部署 Runtime + MCP Server 栈
cdk deploy spring-ai-conference-search-agentcore-runtime-with-mcp-server-stack \
  --parameters AWSAccountId={account_id}
```

### 4.5 IAM 执行角色

从 `cdk.json` 读取 `roleArnForTheAgentCoreRuntime`，配置到 Runtime 的 `executionRole` 属性。

部署完成后需要记录两样产出：
1. **Runtime ID** — 用于 MCP Client 构造 endpoint
2. **Cognito 配置** — user pool name、client pool name、resource server ID

---

## 五、Part 3：本地 MCP Client

### 5.1 Client 架构

![本地 MCP Client 架构](../image/part3-local-mcp-client-arch.png)

*图：本地 MCP Client 的组件交互 — JWT 认证 → MCP Client → Bedrock ChatClient*

```
┌─────────────────────────────────────────────┐
│      Local MCP Client (Spring Boot)          │
│  SpringAIAgentController (@RestController)    │
│  ├──[1] JWT Token ← Cognito                 │
│  ├──[2] AsyncMcpToolCallbackProvider         │
│  │        └── WebClientStreamableHttpTransport│
│  │                 └── AgentCore Runtime     │
│  ├──[3] DateTimeTools (本地 Tool)            │
│  └──[4] ChatClient (Bedrock Converse) ── LLM │
└─────────────────────────────────────────────┘
```

### 5.2 依赖配置

**pom.xml 关键依赖：**
```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-model-bedrock-converse</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-mcp-client-webflux</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

**application.properties：**
```properties
# Spring AI - Bedrock
spring.ai.bedrock.converse.region=us-east-1
spring.ai.bedrock.converse.timeout=120s
spring.ai.bedrock.converse.model=anthropic.claude-sonnet-4-20250507
spring.ai.bedrock.converse.max-tokens=4096
spring.ai.mcp.client.type=ASYNC

# MCP Server (AgentCore Runtime)
agentcore.runtime.id=runtime-xxxxxxxx
agentcore.runtime.endpoint=https://runtime.{region}.bedrock-agent.aws.dev

# Cognito
cognito.user.pool.name=ConferenceSearchUserPool
cognito.user.pool.client.name=ConferenceSearchUserPoolClient
cognito.auth.token.resource.server.id=conference-search-resource-server
```

### 5.3 ChatClient 构建

```java
@Bean
public ChatClient chatClient(
        BedrockChatModel chatModel,
        @Value("${spring.ai.bedrock.converse.model}") String modelName,
        @Value("${spring.ai.bedrock.converse.max-tokens}") int maxTokens) {
    
    var toolCallOptions = ToolCallingChatOptions.builder()
        .model(modelName)
        .maxTokens(maxTokens)
        .build();
    
    return ChatClient.builder(chatModel)
        .defaultOptions(toolCallOptions)
        .build();
}
```

### 5.4 JWT Token 获取

调用 Cognito 获取 OAuth2 令牌的完整流程：

```java
private String getAuthToken() {
    // 1. 通过 STS 获取 caller identity
    // 2. 根据 user pool name / client name 获取 Cognito 配置
    // 3. 构造 OAuth2 token endpoint URL
    String tokenUrl = "https://" + userPoolDomain + ".auth." + region + ".amazoncognito.com/oauth2/token";
    
    // 4. 用 client_credentials grant 获取令牌
    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);
    // ... 设置 scope 为 resource server id
    
    // 5. 从响应中提取 access_token
    // ... 返回 bearer token
}
```

### 5.5 MCP Client 配置

```java
private McpAsyncClient getMcpClient(String authToken) {
    // 1. 构造 MCP Server endpoint
    String serverEndpoint = String.format(
        "https://%s.runtime.%s.bedrock-agent.aws.dev",
        runtimeId, region);
    
    // 2. 创建 WebClient（含 JWT 头）
    WebClient.Builder webClientBuilder = WebClient.builder()
        .defaultHeader(HttpHeaders.AUTHORIZATION, "Bearer " + authToken);
    
    // 3. 创建 Streamable HTTP Transport（⚠️ 必须用 Streamable）
    var transport = new WebClientStreamableHttpTransport(
        serverEndpoint, webClientBuilder);
    
    // 4. 初始化 MCP Client
    var mcpClient = McpClient.async(transport).build();
    mcpClient.initialize().block();
    
    return mcpClient;
}
```

### 5.6 工具集成与 Chat 循环

```java
// 1. 初始化 MCP Client
McpAsyncClient mcpClient = getMcpClient(token);

// 2. 列出 MCP Server 的工具
ListToolsResult toolsResult = mcpClient.listTools().block();

// 3. 创建 Tool Callback Provider
var toolCallbacks = new AsyncMcpToolCallbackProvider(mcpClient);

// 4. 本地 Tool：获取当前日期（LLM 不知道实时日期）
public class DateTimeTools {
    @Tool(name = "Get_The_Current_Date", description = "获取当前日期")
    public String getCurrentDate() {
        return LocalDate.now().toString();
    }
}

// 5. 组装 ChatClient
String response = chatClient.prompt()
    .user(prompt)
    .tools(dateTimeTools)       // 本地工具
    .toolCallbacks(toolCallbacks) // MCP Server 工具
    .stream()
    .content();
```

### 5.7 测试验证

![Conference Search 演示](../image/part1-conference-search-demo.png)

*图：自然语言搜索会议的效果演示*

![MCP Inspector 测试](../image/part1-mcp-inspector-test.png)

*图：使用 MCP Inspector 调试工具调用*

![Client 测试结果](../image/part3-client-test-results.png)

*图：两个查询的 LLM 响应和工具调用日志*

```bash
# 启动 MCP Client
mvn spring-boot:run

# 测试查询 1：搜索会议
http GET http://localhost:8080/conference?prompt="Please provide me with the list of conferences, including their IDs, with Java topics happening in 2027" \
  Content-Type:text/plain

# 测试查询 2：搜索 + CFP 开放中
http GET http://localhost:8080/conference?prompt="Please provide me with the list of conferences, including their IDs, with Java topics happening in 2026 and 2027, with the call for papers open today" \
  Content-Type:text/plain
```

**预期结果：**
- 查询1 → LLM 调用 `Conference_Search_Tool_By_Topic_And_Date`
- 查询2 → LLM 调用 `Conference_Search_Tool_By_Topic_Date_CFP_Open` + 本地 `Get_The_Current_Date`

---

## 六、Part 4：Streamable HTTP 传输协议深度解析

### 6.1 Streamable HTTP 传输总览

![Streamable HTTP 传输概览](../image/part4-streamable-http-overview.png)

*图：MCP Streamable HTTP 传输的 stateless 和 stateful 两种模式*

### 6.2 从 SSE 到 Streamable HTTP

Spring AI 1.0.x 中 MCP 仅支持 STDIO 和 SSE 传输。从 **Spring AI 1.1.0-SNAPSHOT** 开始，引入 **Streamable HTTP** 作为 MCP 传输协议，SSE 被标记为弃用。

**传输协议对比演进：**

| 特性 | SSE | Streamable HTTP |
|---|---|---|
| 连接模型 | 长期 HTTP 连接（eventsource） | 短期 HTTP 请求-响应 |
| 流式响应 | ✅ 原生 | ✅ 可选 (text/event-stream) |
| 非流式响应 | ❌ 不适合 | ✅ 直接 HTTP 响应 |
| 服务端开销 | 高（维持长连接） | 低（无状态请求） |
| 客户端要求 | 支持 EventSource | 标准 HTTP 客户端 |
| 状态管理 | 隐式（连接级） | 显式 (Mcp-Session-Id) |
| AgentCore 支持 | ❌ | ✅ |

### 6.2 配置 Streamable HTTP MCP Server

**pom.xml — 依赖配置：**

**重要：** MCP Client 使用 **ASYNC** 模式时，必须使用 `spring-ai-starter-mcp-client-webflux` 而非 `spring-boot-starter-web`。WebFlux 提供了响应式 Streamable HTTP 支持的底层。

```xml
<!-- MCP Server：始终使用 WebFlux 变体 -->
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-mcp-server-webflux</artifactId>
</dependency>

<!-- MCP Client：ASYNC 模式必须使用 WebFlux 变体 -->
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-mcp-client-webflux</artifactId>
</dependency>
```

![Spring Initializr 依赖配置](../image/part1-spring-init-scan.png)

*图：Spring Initializr 生成项目时的依赖配置*

**🎯 Spring AI 版本与 Snapshot Repository：**

Spring AI 1.1.0-SNAPSHOT 是当前包含 Streamable HTTP 支持的开发版本。需要声明两个 snapshot 仓库：

```xml
<repositories>
    <repository>
        <id>spring-snapshots</id>
        <name>Spring Snapshots</name>
        <url>https://repo.spring.io/snapshot</url>
        <releases><enabled>false</enabled></releases>
    </repository>
    <repository>
        <id>central-portal-snapshots</id>
        <name>Central Portal Snapshots</name>
        <url>https://central.sonatype.com/repository/maven-snapshots/</url>
        <releases><enabled>false</enabled></releases>
        <snapshots><enabled>true</enabled></snapshots>
    </repository>
</repositories>
```

```xml
<properties>
    <java.version>21</java.version>
    <spring-ai.version>1.1.0-SNAPSHOT</spring-ai.version>
</properties>
```

> ✅ **Spring AI 1.1 GA 后：** 只需删除两个 snapshot 仓库声明（repositories 块），版本改为 `1.1.0` 即可。无需改其他代码。

**application.properties：**

```properties
# MCP Server 配置
spring.ai.mcp.server.type=STATELESS
spring.ai.mcp.server.transport=STREAMABLE_HTTP
spring.ai.mcp.server.identity=conference-search-server

# MCP 服务端端口与路径
spring.ai.mcp.server.bindings.port=8081
spring.ai.mcp.server.bindings.path=/mcp
```

> 默认 MCP Server 监听端口 **8081**，路径 `/mcp`。完整的 endpoint 为 `http://localhost:8081/mcp`。

### 6.3 同步 vs 异步 MCP Client

Spring AI 1.1 同时支持 SYNC 和 ASYNC 两种 MCP Client 模式：

| 模式 | 依赖要求 | 传输方式 | 适用场景 |
|---|---|---|---|
| **SYNC** | `spring-ai-starter-mcp-client` + `spring-boot-starter-web` | Streamable HTTP | 简单请求-响应 |
| **ASYNC** | `spring-ai-starter-mcp-client-webflux` + WebFlux | Streamable HTTP | 流式响应、反应式 |

```properties
spring.ai.mcp.client.type=ASYNC    # 推荐：支持流式响应
# spring.ai.mcp.client.type=SYNC   # 如果不需要流式
```

### 6.4 MCP Inspector 客户端

![MCP Inspector 配置页](../image/part4-mcp-inspector-config.png)

*图：MCP Inspector Web UI 的环境变量配置界面*

MCP Inspector 是官方 MCP 客户端调试工具，以 Docker 容器运行。

**启动命令：**

```bash
docker run --rm \
  -e MCP_INSPECTOR_ENV_VARS='{
    "amazon.bedrock.agentcore.runtime.id": "demoamazonapigatewayorderapi-5hkl78n",
    "amazon.bedrock.agentcore.cognito.user.pool.name": "sample-agentcore-gateway-pool",
    "amazon.bedrock.agentcore.cognito.user.pool.client.name": "sample-agentcore-gateway-client",
    "amazon.bedrock.agentcore.cognito.auth.token.resource.server.id": "sample-agentcore-gateway-id",
    "amazon.bedrock.agentcore.region": "us-east-1",
    "AWS_ACCESS_KEY_ID": "...",
    "AWS_SECRET_ACCESS_KEY": "...",
    "AWS_SESSION_TOKEN": "..."
  }' \
  -p 3001:3000 \
  amazon/amazon-bedrock-agentcore-mcp-inspector:latest
```

**关键环境变量说明：**

| 变量 | 说明 |
|---|---|
| `amazon.bedrock.agentcore.runtime.id` | AgentCore Runtime ID |
| `amazon.bedrock.agentcore.*.cognito.*` | Cognito User Pool / Client / Resource Server 配置 |
| `amazon.bedrock.agentcore.region` | AWS 区域 |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_SESSION_TOKEN` | AWS 凭证（用于获取 Cognito JWT） |

启动后访问 http://localhost:3001 进入 MCP Inspector Web UI。

### 6.5 Amazon Q Developer 客户端

![Amazon Q Developer MCP 配置](../image/part4-amazon-q-config.png)

*图：Amazon Q Developer 的 MCP Streamable HTTP 端点配置*

部署到 AgentCore Runtime 的 MCP Server 可以直接被 **Amazon Q Developer**（Amazon 的企业级 AI 助手）调用，连接方式是在 Amazon Q 中配置 MCP Streamable HTTP 端点。

```json
{
  "mcpServers": {
    "conference-search": {
      "type": "streamable-http",
      "url": "https://{runtime-id}.runtime.{region}.bedrock-agent.aws.dev/mcp",
      "cognitoAuth": {
        "userPoolName": "ConferenceSearchUserPool",
        "userPoolClientName": "ConferenceSearchUserPoolClient",
        "resourceServerId": "conference-search-resource-server"
      }
    }
  }
}
```

**支持的 MCP Client 工具总结：**

| 工具 | 部署方式 | 适用场景 |
|---|---|---|
| Spring AI ChatClient (MCP Client) | 自部署 Spring Boot 应用 | 自定义 Agent 编排 |
| MCP Inspector | Docker 本地运行 | 调试与测试 |
| Amazon Q Developer | AWS 托管 | 企业级 AI 助手集成 |
| 其他标准 MCP Client | 任意 | 通用 MCP 工具消费 |

### 6.6 安全性：OAuth2 + Spring Security

生产环境中的 MCP Server 应添加安全保护。AgentCore Runtime 已有 JWT 认证（Cognito），但直接部署的 MCP Server 也可以配置自己的安全层。

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
</dependency>
```

```properties
spring.security.oauth2.resourceserver.jwt.issuer-uri=https://cognito-idp.{region}.amazonaws.com/{userPoolId}
spring.security.oauth2.resourceserver.jwt.jwk-set-uri=https://cognito-idp.{region}.amazonaws.com/{userPoolId}/.well-known/jwks.json
```

AgentCore 内置对 JWT 认证的支持（`AuthorizationConfiguration.jwtConfiguration`），可直接在 Runtime 级别配置而无需在应用代码层面处理。

### 6.7 验证 Streamable HTTP MCP Server

```bash
# 1. 启动 MCP Server
mvn spring-boot:run -f conference-search-mcp-server/pom.xml

# 2. 用 curl 测试工具列表（MCP ListTools 请求）
curl -X POST http://localhost:8081/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'

# 预期返回 tools 列表，包含 Conference_Search_Tool_All 等 4 个工具
```

---

## 七、Part 5：Spring AI 作为 Custom Agent 部署到 AgentCore Runtime

### 7.1 为什么要用 Java/Spring AI 而非 Python

大部分 Agent 示例使用 Python（Strands Agents、LangChain、LangGraph），但 Spring AI 证明了 Java 也是 Agent 开发的一等公民。本部分展示如何用 **Spring AI** 实现 Custom Agent 并托管到 **AgentCore Runtime**。

### 7.2 Custom Agent 架构

![Spring AI Custom Agent 架构](../image/part5-spring-ai-agentcore-arch.png)

*图：Spring AI Custom Agent 内部结构 — /ping + /invocations 端点，MCP Client → Gateway*

```
AgentCore Runtime
  ┌────────────────────────────────┐
  │ Spring AI Agent (Spring Boot)  │
  │  GET /ping → {"status"...}     │
  │  POST /invocations → Agent     │
  │  ├── ChatClient (Bedrock)      │
  │  └── MCP Client (Streamable)   │
  │        └── AgentCore Gateway   │
  │              └── getOrderById  │
  │              └── getOrders...  │
  └────────────────────────────────┘
```

### 7.3 AgentCore Runtime 对 Custom Agent 的要求

AgentCore Runtime 要求非常简单——只需遵循三个约定：

| 约束 | 说明 |
|---|---|
| **`/invocations`** | POST 端点，接收用户 prompt，返回 Agent 响应 |
| **`/ping`** | GET 端点，健康检查，返回 `{"status": "healthy"}` |
| **Docker 容器** | ARM64 架构，推送到 ECR |

### 7.4 前提条件

在部署 Spring AI Custom Agent 之前，需要准备：

1. **数据层应用已部署** — 如 Aurora DSQL + 订单 API
2. **AgentCore Gateway 已设置并暴露 MCP 工具** — 参考 Gateway 系列文章（Gateway Part 2: API Gateway → MCP，或 Gateway Part 3: Lambda → MCP），包括：
   - Cognito User Pool
   - Cognito Resource Server
   - Cognito User Pool Client
   - AgentCore Gateway URL
3. **理解 Spring AI 基础** — Tool 机制、ChatClient、MCP 客户端

### 7.5 pom.xml 配置

```xml
<repositories>
    <repository>
        <id>spring-snapshots</id>
        <name>Spring Snapshots</name>
        <url>https://repo.spring.io/snapshot</url>
        <releases><enabled>false</enabled></releases>
    </repository>
    <repository>
        <id>central-portal-snapshots</id>
        <name>Central Portal Snapshots</name>
        <url>https://central.sonatype.com/repository/maven-snapshots/</url>
        <releases><enabled>false</enabled></releases>
        <snapshots><enabled>true</enabled></snapshots>
    </repository>
</repositories>

<properties>
    <java.version>21</java.version>
    <spring-ai.version>1.1.0-SNAPSHOT</spring-ai.version>
</properties>

<dependencies>
    <dependency>
        <groupId>org.springframework.ai</groupId>
        <artifactId>spring-ai-starter-model-bedrock-converse</artifactId>
    </dependency>
    <!-- ASYNC MCP Client → 必须用 WebFlux 变体 -->
    <dependency>
        <groupId>org.springframework.ai</groupId>
        <artifactId>spring-ai-starter-mcp-client-webflux</artifactId>
    </dependency>
</dependencies>
```

### 7.6 application.properties

```properties
# Cognito 配置（与 Gateway 创建时保持一致）
cognito.user.pool.name=sample-agentcore-gateway-pool
cognito.user.pool.client.name=sample-agentcore-gateway-client
cognito.auth.token.resource.server.id=sample-agentcore-gateway-id

# AgentCore Gateway URL
amazon.bedrock.agentcore.gateway.url=https://demoamazonapigatewayorderapi-5hkl78n.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp
```

### 7.7 RestController 实现（SpringAIAgentController）

**ChatClient 构建：**

```java
@RestController
public class SpringAIAgentController {

    private final ChatClient chatClient;

    public SpringAIAgentController(ChatClient.Builder builder, ChatMemory chatMemory) {
        var options = ToolCallingChatOptions.builder()
            .model("amazon.nova-lite-v1:0")
            // .model("amazon.nova-pro-v1:0")
            // .model("anthropic.claude-3-5-sonnet-20240620-v1:0")
            .maxTokens(2000)
            .build();

        this.chatClient = builder
            .defaultAdvisors(MessageChatMemoryAdvisor.builder(chatMemory).build())
            .defaultOptions(options)
            // .defaultSystem(SYSTEM_PROMPT)
            .build();
    }
}
```

**Ping 端点：**

```java
// 方式一：手动实现
@GetMapping("/ping")
public String ping() {
    return "{\"status\": \"healthy\"}";
}

// 方式二：Spring Actuator
// application.properties:
//   management.endpoints.web.exposure.include=health
//   management.endpoints.web.base-path=/
//   management.endpoints.web.path-mapping.health=ping
```

**Invocations 端点（核心逻辑）：**

```java
@PostMapping(value = "/invocations", consumes = { "*/*" })
public Flux<String> invocations(@RequestBody String prompt) {
    // 1. 获取 Cognito JWT Token
    String token = getAuthToken();

    // 2. 创建 MCP Client（Streamable HTTP → AgentCore Gateway）
    var client = McpClient.async(getMcpClientTransport(token)).build();
    client.initialize();

    // 3. 获取 MCP Server 暴露的工具列表
    var toolsResult = client.listTools();

    // 4. 创建 Tool Callback Provider
    var asyncMcpToolCallbackProvider = new AsyncMcpToolCallbackProvider(client);

    // 5. 调用 ChatClient，绑定 MCP 工具
    var content = this.chatClient.prompt()
        .user(prompt)
        .toolCallbacks(asyncMcpToolCallbackProvider.getToolCallbacks())
        .stream()
        .content();

    // 6. 关闭 MCP Client
    client.close();

    return content;
}
```

**JWT Token 获取：**

```java
private String getAuthToken() {
    // 1. 通过 AmazonCognitoIdentityProviderClient 获取 User Pool / Client 信息
    // 2. 构造 token endpoint URL：
    //    https://<domain>.auth.<region>.amazoncognito.com/oauth2/token
    // 3. POST client_credentials grant，scope = resource server id
    // 4. 解析响应，提取 access_token
    // ...
}
```

### 7.8 Dockerfile

```dockerfile
FROM --platform=linux/arm64 eclipse-temurin:21-jre

RUN groupadd -r agent && useradd -r -g agent agent

WORKDIR /app

COPY target/spring-ai-agent-demo-*.jar app.jar

RUN chown -R agent:agent /app

USER agent

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

> ⚠️ AgentCore Runtime 运行在 **ARM64** 架构上，Dockerfile 必须用 `--platform=linux/arm64`。

**构建与推送命令：**

```bash
# 构建 Docker 镜像
sudo docker build --no-cache -t agentcore-runtime-spring-ai-demo:v1 .

# 登录 ECR
aws ecr get-login-password --region {region} | \
  sudo docker login --username AWS --password-stdin {account_id}.dkr.ecr.{region}.amazonaws.com

# 创建 ECR 仓库
aws ecr create-repository \
  --repository-name agentcore-runtime-spring-ai-demo \
  --image-scanning-configuration scanOnPush=true \
  --region {region}

# 打标签并推送
sudo docker tag agentcore-runtime-spring-ai-demo:v1 \
  {account_id}.dkr.ecr.{region}.amazonaws.com/agentcore-runtime-spring-ai-demo:v1

sudo docker push \
  {account_id}.dkr.ecr.{region}.amazonaws.com/agentcore-runtime-spring-ai-demo:v1
```

**Buildpack 替代方案（无需 Dockerfile）：**

```bash
mvn spring-boot:build-image \
  -Dspring-boot.build-image.imageName=agentcore-runtime-spring-ai-demo:v1
# 然后 docker tag + push 到 ECR
```

### 7.9 DeployRuntimeAgent：通过 AWS SDK 部署

```java
public class DeployRuntimeAgent {

    private static final String IAM_ROLE_ARN = "{IAM_ARN_ROLE}";
    private static final String CONTAINER_URI = "{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/{ECR_REPO}";

    private static final String CREATE_AGENT_RUNTIME_CONTAINER_URI = CONTAINER_URI + ":v1";
    private static final String UPDATE_AGENT_RUNTIME_CONTAINER_URI = CONTAINER_URI + ":v14";

    private static final String AGENT_RUNTIME_NAME = "{AGENT_RUNTIME_NAME}";
    private static final String AGENT_RUNTIME_ID = "{AGENT_RUNTIME_ID}";

    private static final BedrockAgentCoreControlClient bedrockAgentCoreControlClient =
        BedrockAgentCoreControlClient.builder()
            .region(Region.US_EAST_1)
            .build();

    private static void createAgentRuntime() {
        var request = CreateAgentRuntimeRequest.builder()
            .agentRuntimeName(AGENT_RUNTIME_NAME)
            .roleArn(IAM_ROLE_ARN)
            .networkConfiguration(NetworkConfiguration.builder()
                .networkMode(NetworkMode.PUBLIC)
                .build())
            .agentRuntimeArtifact(AgentArtifact.fromContainerConfiguration(
                ContainerConfiguration.builder()
                    .containerUri(CREATE_AGENT_RUNTIME_CONTAINER_URI)
                    .build()))
            .build();

        var response = bedrockAgentCoreControlClient.createAgentRuntime(request);
        System.out.println("Create Agent Runtime response: " + response);
    }

    private static void updateAgentRuntime() {
        var request = UpdateAgentRuntimeRequest.builder()
            .agentRuntimeId(AGENT_RUNTIME_ID)
            .roleArn(IAM_ROLE_ARN)
            .networkConfiguration(NetworkConfiguration.builder()
                .networkMode(NetworkMode.PUBLIC)
                .build())
            .agentRuntimeArtifact(AgentArtifact.fromContainerConfiguration(
                ContainerConfiguration.builder()
                    .containerUri(UPDATE_AGENT_RUNTIME_CONTAINER_URI)
                    .build()))
            .build();

        var response = bedrockAgentCoreControlClient.updateAgentRuntime(request);
        System.out.println("Update Agent Runtime response: " + response);
    }

    public static void main(String[] args) throws Exception {
        // createAgentRuntime();    // 首次创建
        updateAgentRuntime();      // 更新已有 Runtime
    }
}
```

> 注意 `CREATE_AGENT_RUNTIME_CONTAINER_URI` 和 `UPDATE_AGENT_RUNTIME_CONTAINER_URI` 使用不同的版本标签，每次更新镜像时递增版本号。

### 7.10 调用验证

部署完成后，AgentCore Runtime 会自动将请求路由到 Spring AI Agent。调用方式与任何 Custom Agent 相同：

```bash
curl -X POST https://{runtime-id}.runtime.{region}.bedrock-agent.aws.dev/invocations \
  -H "Authorization: Bearer {cognito-jwt}" \
  -H "Content-Type: text/plain" \
  -d "Show me orders with IDs greater than 10"

# 预期：Agent 通过 MCP Client 调用 AgentCore Gateway 暴露的
# getOrderById / getOrdersByCreatedDates 工具，返回结果
```

---

## 八、Part 6：AgentCore 可观测性

### 8.1 挑战：AgentCore Runtime 不支持 Sidecar

AgentCore Runtime 不运行 Docker Compose，无法部署 **ADOT Collector** 作为 Sidecar。所以标准的 ADOT 方案（Java Agent → OTLP → ADOT Collector → CloudWatch）不适用。

**解决方案：Collector-less 模式**

![Collector-less 可观测性架构](../image/part6-observability-arch.png)

*图：ADOT Java Agent 直接上报 OTLP 到 CloudWatch，无需 Collector Sidecar*

```
AgentCore Runtime (Docker)
  ┌─────────────────────────────┐
  │ Spring AI Agent              │
  │  ┌───────────────────────┐  │
  │  │ ADOT Java Agent       │──│──OTLP (http/protobuf)──► CloudWatch
  │  └───────────────────────┘  │  GenAI Observability
  └─────────────────────────────┘  ├─ Agent Sessions
                                   ├─ Traces
                                   ├─ Trajectory
                                   └─ Timeline
```

![ADOT Dockerfile 配置](../image/part6-adot-config.png)

*图：Dockerfile 中 ADOT Agent JAR 下载与环境变量配置*

### 8.2 Dockerfile 配置

下载 ADOT Java Agent JAR 并配置环境变量：

```dockerfile
FROM --platform=linux/arm64 eclipse-temurin:21-jre AS builder

# 下载 AWS OpenTelemetry Java Agent
ADD https://github.com/aws-observability/aws-otel-java-instrumentation/releases/latest/download/aws-opentelemetry-agent.jar \
    /otel/aws-opentelemetry-agent.jar

FROM --platform=linux/arm64 eclipse-temurin:21-jre

RUN groupadd -r agent && useradd -r -g agent agent

WORKDIR /app

COPY --from=builder /otel/aws-opentelemetry-agent.jar /otel/aws-opentelemetry-agent.jar
COPY target/spring-ai-agent-demo-*.jar app.jar

RUN chown -R agent:agent /app /otel

USER agent

EXPOSE 8080

ENV AGENT_OBSERVABILITY_ENABLED=true
ENV JAVA_TOOL_OPTIONS="-javaagent:/otel/aws-opentelemetry-agent.jar"
ENV OTEL_RESOURCE_ATTRIBUTES="service.name=spring-ai-agent-demo,aws.log.group.names=/bedrock/agentcore/spring-ai-agent-demo"
ENV OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
ENV OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://otlp.cloudwatch.region.amazonaws.com/v1/traces
ENV OTEL_EXPORTER_OTLP_LOGS_ENDPOINT=https://otlp.cloudwatch.region.amazonaws.com/v1/logs
ENV OTEL_EXPORTER_OTLP_LOGS_HEADERS=x-aws-log-group=/bedrock/agentcore/spring-ai-agent-demo,x-aws-log-stream=spring-ai-agent-stream,x-aws-metric-namespace=bedrock-agentcore
ENV OTEL_TRACES_EXPORTER=otlp
ENV OTEL_LOGS_EXPORTER=otlp
ENV OTEL_METRICS_EXPORTER=none
ENV OTEL_BSP_MAX_EXPORT_BATCH_SIZE=512
ENV OTEL_BSP_SCHEDULE_DELAY=100

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

### 8.3 环境变量详解

| 变量 | 值 | 说明 |
|---|---|---|
| `AGENT_OBSERVABILITY_ENABLED` | `true` | 启用 AgentCore Observable 集成 |
| `JAVA_TOOL_OPTIONS` | `-javaagent:...` | 注入 ADOT Java Agent |
| `OTEL_RESOURCE_ATTRIBUTES` | `service.name=...,aws.log.group.names=...` | 资源标识，CloudWatch Log Group |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `http/protobuf` | OTLP 传输协议（必须） |
| `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` | CloudWatch OTLP URL | Trace 上报端点 |
| `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT` | CloudWatch OTLP URL | Log 上报端点 |
| `OTEL_EXPORTER_OTLP_LOGS_HEADERS` | `x-aws-log-group=...,x-aws-log-stream=...,x-aws-metric-namespace=bedrock-agentcore` | 日志路由 + 指标命名空间 |
| `OTEL_TRACES_EXPORTER` | `otlp` | Trace 导出器 |
| `OTEL_LOGS_EXPORTER` | `otlp` | Log 导出器 |
| `OTEL_METRICS_EXPORTER` | `none` | 暂不启用 Metrics |
| `OTEL_BSP_EXPORT_BATCH_SIZE` | `512` | Batch Span Processor 批次大小 |
| `OTEL_BSP_SCHEDULE_DELAY` | `100` | Batch Span Processor 调度延迟（ms） |

### 8.4 CloudWatch GenAI Observability 视图

启用后，在 CloudWatch 控制台可以查看以下 GenAI Observability 面板：

| 视图 | 内容 |
|---|---|
| **Agent Sessions** | Agent 会话级别追踪：prompt、模型调用、工具调用 |
| **Traces** | 分布式链路追踪：Invocation → MCP Client → Gateway → 后端服务 |
| **Trajectory** | Agent 推理轨迹：选择了哪些工具、各步骤时间 |
| **Timeline** | 时间线视图：整条请求链路的时间分布 |

### 8.5 已知限制

| 限制 | 说明 | 未来状态 |
|---|---|---|
| **Memory 指标** | Spring AI AgentCore Memory 未集成，暂无 Memory 相关 metrics | Spring AI AgentCore 社区项目未来可能加入 |

![Memory 指标缺失](../image/part6-no-memory-metrics.png)

*图：CloudWatch GenAI 面板中暂无 Memory 相关指标*

| **Metrics 导出器** | 当前设为 `none`，未启用自定义业务指标 | 可按需启用 |
| **OTLP 端点** | 需要 CloudWatch OTLP 支持的区域 | 检查 AWS 区域可用性 |

### 8.6 CloudWatch GenAI 控制台视图

![Agent Sessions 视图](../image/part6-cloudwatch-sessions.png)

*图：CloudWatch GenAI — Agent Sessions 面板，展示每个 Invocation 的完整链路*

![Traces 视图](../image/part6-traces-view.png)

*图：CloudWatch GenAI — Traces 面板，展示 ChatClient → MCP Client → Gateway 的调用链*

![Trajectory 视图](../image/part6-trajectory-view.png)

*图：CloudWatch GenAI — Trajectory 面板，展示 Agent 的工具选择和执行轨迹*

![Timeline 视图](../image/part6-timeline-view.png)

*图：CloudWatch GenAI — Timeline 面板，展示请求链路的时间分布*

### 8.7 验证 Agent 日志

```bash
# 1. 确认容器内 ADOT Agent 已加载
docker logs {container_id} | grep "OpenTelemetry"

# 输出类似：
# [OpenTelemetry Agent] OpenTelemetry Java Agent v2.x.x initialized

# 2. 在 AWS Console → CloudWatch → GenAI Observability 查看
#    - Agent Sessions: 每个 HTTP POST /invocations 请求为一个 Session
#    - Traces: 展示 ChatClient → MCP Client → Gateway 调用链
#    - Trajectory: Agent 每一步的工具选择和执行结果
```

---

## 九、关键设计决策与最佳实践

### 9.1 Stateless vs Stateful MCP Server

| 模式 | 适用场景 | AgentCore 支持 |
|---|---|---|
| Stateless HTTP | 纯工具调用，不需要会话上下文 | ✅ 推荐（默认） |
| Stateful HTTP | 需要跨请求维护会话状态 | ✅ 支持（加 Mcp-Session-Id） |

配置方式（application.properties）：
```properties
spring.ai.mcp.server.type=STATELESS   # 或 STATEFUL
```

### 9.2 Runtime vs Gateway 的选择

| 对比项 | AgentCore Runtime | AgentCore Gateway |
|---|---|---|
| 定位 | 运行 MCP Server / Custom Agent | 托管 MCP Server（网关层） |
| 适用场景 | 需要将 MCP Server / Agent 托管在云端 | 已有部署的应用，需要暴露为 MCP 工具 |
| 管理成本 | 需自行构建/推送 Docker 镜像 | 托管管理，接入现有 API |
| 认证 | Cognito JWT | 类似 |

**推荐策略**：
- 新开发的 MCP Server / Custom Agent → **Runtime**
- 已有后端服务需暴露为 MCP 工具 → **Gateway**

### 9.3 传输协议选择指南

| 场景 | 推荐协议 | 说明 |
|---|---|---|
| 本地开发测试 | STDIO | 零网络开销，进程内通信 |
| 云端部署（新项目） | Streamable HTTP | ☑️ 全场景推荐，AgentCore 原生支持 |
| 旧项目迁移 | Streamable HTTP | SSE 已弃用，应尽快迁移 |
| 流式 LLM 响应 | Streamable HTTP + ASYNC | WebFlux + Flux<String> |
| 简单工具查询 | Streamable HTTP + SYNC | 无需流式，一次请求返回 |

### 9.4 SYNC vs ASYNC MCP Client 选择

| 场景 | 推荐 Client 类型 | 原因 |
|---|---|---|
| 流式输出（逐 token） | **ASYNC** | 支持 `Flux<String>`，WebFlux |
| 聚合后返回 | **SYNC** | 简单，无 WebFlux 依赖 |
| 需流式但用 WebMVC | ❌ 不可行 | ASYNC 必须用 WebFlux |

### 9.5 部署命令速查

```bash
# 1. 构建 Docker 镜像（MCP Server / Custom Agent）
mvn spring-boot:build-image -f pom.xml

# 2. 推送到 ECR
docker tag ... && docker push ...

# 3. 部署 Cognito 栈
cdk deploy spring-ai-conference-search-user-client-pool-stack \
  --parameters AWSAccountId=123456789012

# 4. 部署 Runtime 栈
cdk deploy spring-ai-conference-search-agentcore-runtime-with-mcp-server-stack \
  --parameters AWSAccountId=123456789012

# 5. 配置 MCP Client（填入 Runtime ID + Cognito 信息）
# 6. 启动 Client
mvn spring-boot:run -f spring-ai-1.1-conference-app-agent-local/pom.xml
```

### 9.6 已知问题

| 问题 | 影响 | 解决状态 |
|---|---|---|
| CDK Cognito Domain prefix bug | 需要在 cdk.json 中手动设置 userPoolId | Workaround 有，等待 AWS 修复 |
| CDK AgentCore L2 Construct 仍为 Alpha | API 可能变化 | 使用 L1 CfnRuntime 更稳定 |
| Spring AI 2.x（Spring Boot 4）未 GA | 无法使用最新版本 | 当前使用 1.1.x 分支 |
| AgentCore Runtime 无 Docker Compose | 无法运行 Sidecar（如 ADOT Collector） | 使用 collector-less 方案 |
| ADOT CloudWatch OTLP 区域限制 | 部分区域不支持 | 确认区域可用性 |

---

## 十、未来扩展预告

- **MCP Server 部署到 AgentCore Gateway** — 对比 Runtime vs Gateway
- **Spring AI AgentCore Memory** — 短期/长期/情景记忆集成（含 Observability 指标）
- **Embabel Agent Framework** — 基于 Spring AI 的声明式 Agent 编排
- **MCP Client 托管到 AgentCore Runtime** — 客户端也部署到云端
- **Java 25 + Spring Boot 4 + Spring AI 2.x** — 最新版本适配

---

## 十一、源码与参考

- 主示例仓库：<https://github.com/Vadym79/amazon-bedrock-agentcore-spring-ai>
- Spring AI Agent Demo（Part 5）：<https://github.com/Vadym79/SpringAIWithAmazonBedrock/tree/main/spring-ai-agent-demo>
- Spring AI AgentCore 社区项目：<https://github.com/spring-ai-community/spring-ai-agentcore>
- AgentCore MCP 文档：<https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html>
- AgentCore Runtime 文档：<https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html>
- AgentCore Gateway 文档：<https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html>
- Spring AI MCP Server 文档：<https://docs.spring.io/spring-ai/reference/api/mcp/mcp-stateless-server-boot-starter-docs.html>
- Spring AI MCP Client 文档：<https://docs.spring.io/spring-ai/reference/api/mcp/mcp-client-boot-starter-docs.html>
- CDK AgentCore L2 Construct (Alpha)：<https://docs.aws.amazon.com/cdk/api/v2/java/software/amazon/awscdk/services/bedrock/agentcore/alpha/package-summary.html>
- ADOT Java Instrumentation：<https://github.com/aws-observability/aws-otel-java-instrumentation>
- CloudWatch GenAI Observability：<https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-GenAI-observability.html>
- Embabel Agent Framework：<https://github.com/embabel/embabel-agent>
- 原文作者 Spring AI 系列 (Parts 1-6)：<https://dev.to/vkazulkin/series/32829>
- 原文作者 AgentCore 系列 (Parts 1-6)：<https://dev.to/vkazulkin/series/34771>

---

> **总结**：本系列完整展示了从本地 MCP Server → AgentCore Runtime 部署 → 本地 MCP Client → Streamable HTTP 传输协议 → Java Spring AI Custom Agent → ADOT 可观测性的全链路。核心价值在于：
> 1. 将 Spring AI 的 ChatClient + Tool 机制与 AWS AgentCore 的托管运行时结合
> 2. 通过 MCP Streamable HTTP 协议实现分布式 Agent 架构
> 3. 使用 Cognito JWT 保障生产级安全
> 4. 借助 CDK IaC 实现可重复的自动化部署
> 5. 用 Java 实现 Custom Agent，证明 Java 是 Agent 开发的一等公民
> 6. 通过 Collector-less ADOT 实现 Serverless 环境的可观测性
