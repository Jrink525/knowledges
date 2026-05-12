---
title: "Java Agentic AI 框架对比：Spring AI vs LangChain4j vs Embabel"
tags:
  - spring-ai
  - langchain4j
  - embabel
  - agentic-ai
  - java
  - spring
  - ai-agent
  - mcp
  - conference-summary
date: 2026-04
source: "Spring I/O 2026, Barcelona"
authors: "Timo Salm (Broadcom), Sandra Ahlgrimm (Microsoft)"
---

# Java Agentic AI 框架对比：Spring AI vs LangChain4j vs Embabel

> **来源：** Spring I/O 2026 大会分享  
> **演讲者：** Timo Salm (Broadcom / VMware) & Sandra Ahlgrimm (Microsoft)  
> **视频：** [YouTube](https://www.youtube.com/watch?v=To724qB8yEk)  
> **幻灯片：** [PDF](https://2026.springio.net/slides/comparing-agentic-ai-frameworks-for-java-springio26.pdf)  
> **演示代码：** [github.com/SandraAhlgrimm/ai-nutrition-planner](https://github.com/SandraAhlgrimm/ai-nutrition-planner)  
> **日期：** 2026年4月，巴塞罗那

---

## 一、背景：从 LLM 调用到 Agentic AI

### 1.1 范式转变

Agentic AI 标志着一个根本性转变——从被动的、基于 prompt 的交互，进化到具备自主推理、规划和执行能力的智能系统。在 JVM 生态中，多个框架正在崛起以支持这一新范式，但它们的实现路径截然不同。

```
传统 LLM 集成：  Prompt → LLM → 响应
Agentic AI：     目标 → 推理 → 规划 → 工具调用 → 执行 → 观察 → 循环
```

### 1.2 核心 Agent 能力

本场分享围绕以下五个核心维度展开对比：

1. **推理循环（Reasoning Loops）**—— Agent 如何思考、规划和迭代
2. **工具调用（Tool Invocation）**—— Agent 如何与外部系统交互
3. **记忆管理（Memory）**—— Agent 如何在对话和工作流中保持上下文
4. **编排（Orchestration）**—— 如何组合多个 Agent 或步骤
5. **MCP 协议支持**—— 如何标准化工具和数据的访问

---

## 二、三大框架概览

| 维度 | Spring AI | LangChain4j | Embabel |
|------|-----------|-------------|---------|
| **核心作者/组织** | Spring 生态（VMware/Broadcom） | 社区驱动 | Rod Johnson（Spring 框架创始人） |
| **语言** | Java | Java | Kotlin / Java |
| **版本（2026）** | 1.1.4+ | 1.12.2-beta22+ | 0.7+ |
| **设计哲学** | Spring 原生体验，自动配置 | 广度与灵活性，庞大 Provider 生态 | 确定性规划，GOAP 引擎 |
| **关键模式** | ChatClient + Advisors | @Agent 接口 + 组合 Builder | 声明式 Goal/Action DSL |
| **MCP 支持** | ✅ 原生支持 | ✅ 原生支持 | ✅ 通过 Action 支持 |
| **推理循环** | Advisor 链 + 自定义重试 | sequenceBuilder / loopBuilder | GOAP 状态机自动编排 |
| **记忆/状态管理** | ChatMemory API | 多种 Memory Store | 通过 @State 记录 |
| **可观测性** | Micrometer + OTLP | AgentMonitor + Micrometer | 通过 Spring Boot Actuator |

---

## 三、Demo 用例：AI 营养规划助手（AI Nutrition Planner）

这是贯穿整场分享的实战案例。同一个需求用三个框架分别实现，直观对比编程模型差异。

### 3.1 业务需求

创建一个个性化的一周饮食计划：

1. **并行获取**：拉取用户画像 + 查询时令食材
2. **生成食谱**：根据请求的日期和餐次，用时令食材生成食谱
3. **验证合规**：检查食谱是否符合用户画像（过敏原、热量限制、饮食禁忌）
4. **迭代修正**：根据验证反馈修正食谱 → 重新验证 → 循环直到通过或达到最大迭代次数

### 3.2 技术栈

- **Java 25** — 使用现代语言特性：Records、Sealed Interfaces、Pattern Matching、Scoped Values、Virtual Threads
- **Spring Boot 3.5.13** / Spring Framework 6.2
- **LLM 提供商**：Azure OpenAI / OpenAI / Ollama（本地，`qwen2.5` 模型）
- **可观测性**：Grafana + Loki + Tempo + Mimir（OTLP 协议）
- **部署**：Azure Container Apps（通过 Azure Developer CLI 一键部署）

---

## 四、Spring AI 实现详解

### 4.1 核心依赖

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-model-azure-openai</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-mcp-server-webmvc</artifactId>
</dependency>
```

### 4.2 核心架构

Spring AI 的 Agent 实现基于两个核心抽象：

- **`ChatClient`** — 流畅的 LLM 交互 API
- **`Advisors`** — 可插拔的调用链拦截器，用于实现重试、验证、工具搜索等横切关注点

### 4.3 Agent 实现（简化流程）

```java
@Service
class NutritionPlannerAgent {

    @McpTool(description = "Provides a nutrition plan for the week")
    WeeklyPlan createNutritionPlan(WeeklyPlanRequest request) {
        // Phase 1: 并行获取用户画像和时令食材
        var result = Workflow.parallel(
            () -> fetchUserProfile(request),
            () -> fetchSeasonalIngredients(request)
        );

        // Phase 2: 生成 + 验证循环（通过 Advisors 实现）
        var weeklyPlan = createWeeklyPlan(request, seasonalIngredients, userProfile);
        return weeklyPlan;
    }

    private WeeklyPlan createWeeklyPlan(...) {
        // 使用 ValidationRetryAdvisor 实现重试循环
        var advisor = new ValidationRetryAdvisor<>(WeeklyPlan.class,
            plan -> validateWeeklyPlan(plan, userProfile));

        return chatClient.prompt()
            .system(Personas.RECIPE_CURATOR)
            .user(u -> u.text("..."))
            .advisors(advisor)     // 注入验证重试 Advisor
            .tools(askUserTool)
            .call()
            .entity(WeeklyPlan.class);
    }
}
```

### 4.4 关键设计模式

**ValidationRetryAdvisor** 实现了 `CallAdvisor` 接口，拦截 ChatClient 的调用结果，执行验证逻辑，失败时自动重试：

```java
class ValidationRetryAdvisor<T> implements CallAdvisor {
    private final Function<T, ValidationResult> validator;
    private final int maxRetries = 3;

    @Override
    public ChatClientResponse adviseCall(ChatClientRequest request, CallAdvisorChain chain) {
        var response = chain.nextCall(request);
        for (int attempt = 0; attempt < maxRetries; attempt++) {
            var entity = toEntity(response);
            var result = validator.apply(entity);
            if (result.allPassed()) return response;  // 验证通过，返回

            // 验证失败：将反馈注入 prompt，重新调用
            request = withValidationFeedback(request, entity, result);
            response = chain.copy(this).nextCall(request);
        }
        return response; // 达到最大重试次数，返回最后一次结果
    }
}
```

**Spring AI 特点总结：**
- ✅ 与 Spring 生态无缝集成（自动配置、Security、Actuator）
- ✅ 20+ LLM 提供商支持
- ✅ 原生 MCP 支持
- ✅ Advisors 模式灵活可组合
- ⚠️ 复杂 Agent 工作流需要手写更多编排代码
- ⚠️ 没有内置的 Agent 组合 DSL（相比 LangChain4j）

---

## 五、LangChain4j 实现详解

### 5.1 核心依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-spring-boot-starter</artifactId>
</dependency>
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-agentic</artifactId>
</dependency>
```

### 5.2 核心架构

LangChain4j 的 Agent 实现围绕两个核心概念：

- **`@Agent` 接口** — 用注解声明 Agent 的行为和输出
- **`AgenticServices`** — 组合 Agent 的 Builder API（`sequenceBuilder` / `loopBuilder`）

### 5.3 Agent 实现（声明式接口）

```java
interface Agents {

    // 顶层编排：用 @SequenceAgent 声明顺序执行
    @SequenceAgent(description = "Creates a validated weekly nutrition plan",
        subAgents = {SeasonalIngredientAgent.class, WeeklyValidatedPlanCreator.class})
    WeeklyPlan createNutritionPlan(
        @K(UserProfile.class) UserProfile userProfile,
        @K(WeeklyPlanRequest.class) WeeklyPlanRequest request,
        @V("month") String month,
        @V("country") String country,
        @V("additionalInstructions") String additionalInstructions);

    // 子 Agent 1：获取时令食材——声明式 @Agent
    interface SeasonalIngredientAgent {
        @UserMessage("""
            You are a nutrition expert with deep knowledge of seasonal produce.
            Return a list of ingredients for {{month}} in {{country}}.
            """)
        @Agent(description = "Fetches seasonal ingredients",
                typedOutputKey = SeasonalIngredients.class)
        SeasonalIngredients fetchSeasonalIngredients(
            @V("month") String month, @V("country") String country);
    }

    // 子 Agent 2 + 3：生成 + 验证循环——声明式 Loop
    @LoopAgent(subAgents = {WeeklyPlanCreator.class, NutritionGuard.class},
               typedOutputKey = WeeklyPlan.class, maxIterations = 3)
    WeeklyPlan createValidatedWeeklyPlan();

    @ExitCondition(testExitAtLoopEnd = true)
    static boolean exit(
        @K(NutritionAuditValidationResult.class) NutritionAuditValidationResult result) {
        return result.allPassed();
    }
}
```

### 5.4 关键设计模式

**声明式 Agent 组合** 是 LangChain4j 最大的亮点：
- `@SequenceAgent` → 顺序执行子 Agent
- `@LoopAgent` → 循环执行子 Agent 直到满足退出条件
- `@ExitCondition` → 声明式定义循环终止条件
- `@K` / `@V` → 类型安全的上下文传递（`@K` = 共享键值上下文，`@V` = 变量参数）

```java
// 实际调用入口
var weeklyPlan = AgenticServices.createAgenticSystem(Agents.NutritionPlanner.class)
    .createNutritionPlan(userProfile, request, month, country, additionalInstructions);
```

**LangChain4j 特点总结：**
- ✅ 声明式 Agent 组合——用注解定义工作流，代码量最少
- ✅ 类型安全的上下文传递机制（`@K` + `@V`）
- ✅ 庞大的 Provider 生态（20+ LLM，RAG，Tool Calling，MCP）
- ✅ 内置可观测性（AgentMonitor + Micrometer 指标）
- ⚠️ 需要理解注解驱动的组合模式
- ⚠️ 复杂逻辑仍需辅助代码

---

## 六、Embabel 实现详解

### 6.1 背景

Embabel 是 Spring 框架创始人 **Rod Johnson** 打造的 Agent 框架，采用 Kotlin 编写但完全支持 Java。其核心创新是 **GOAP（Goal-Oriented Action Planning）**—— 一种不依赖 LLM 的确定性规划引擎。

### 6.2 核心架构

- **`@Agent`** — 标记一个类为 Agent
- **`@Goal`** — 定义 Agent 的目标
- **`@Action`** — 定义可执行的动作
- **`@State`** — 定义 Agent 的状态，驱动状态机流转

### 6.3 Agent 实现（状态机 + 动作）

```java
@Agent(description = "Supports conscious meal planning and sustainable eating habits.")
class NutritionPlannerAgent {

    @State interface Stage {}  // 状态标记接口

    // Action 1：获取用户画像
    @Action
    UserProfile fetchUserProfileForUser(String user) { ... }

    // Action 2：获取时令食材（注入 Ai 实例）
    @Action
    SeasonalIngredients fetchSeasonalIngredients(WeeklyPlanRequest request, Ai ai) {
        return ai.withLlm(LlmOptions.withAutoLlm())
                 .withReference(skills)
                 .createObject("...", SeasonalIngredients.class);
    }

    // 状态：营养审核（Action 触发状态转换）
    @State
    record NutritionAudit(WeeklyPlan plan, UserProfile profile, ...) implements Stage {

        @Action(canRerun = true)
        Stage validate(Ai ai) {
            var result = ai.createObject("...", ValidationResult.class);
            if (result.allPassed()) return new Done(weeklyPlan);
            return new ReviseWeeklyPlan(weeklyPlan, ...); // 转换到修正状态
        }
    }

    // 状态：修正食谱
    @State
    record ReviseWeeklyPlan(WeeklyPlan plan, ValidationResult feedback, ...) implements Stage {

        @Action(canRerun = true)
        Stage revise(Ai ai) {
            var revised = ai.createObject("Revise based on: ...", WeeklyPlan.class);
            return new NutritionAudit(revised, ...); // 回到审核状态 → 形成循环
        }
    }

    // 状态：完成（标记为 Goal Achievement）
    @State
    record Done(WeeklyPlan weeklyPlan) implements Stage {

        @AchievesGoal(description = "Provides a nutrition plan for the week",
            export = @Export(remote = true, name = "createNutritionPlan"))
        WeeklyPlan createNutritionPlan() { return weeklyPlan; }
    }
}
```

### 6.4 关键设计模式：GOAP 与状态机

Embabel 与其他两个框架最大的区别在于**规划方式**：

```
传统 Agent： LLM 决定 "怎么做"（规划 + 执行都由 LLM 驱动）
Embabel：    LLM 决定 "做什么"（目标），GOAP 引擎决定 "怎么做"（动作序列）
```

- `@State` + `@Action(canRerun = true)` → 定义状态转换图
- `@AchievesGoal` → 标记最终目标达成状态
- LLM 只负责单个 Action 的生成任务，不负责全局规划
- 规划由 GOAP 引擎**确定性执行**，结果可解释、可预测

**Embabel 特点总结：**
- ✅ 确定性规划——动作序列可预测、可审计
- ✅ 状态机模型——天然适合复杂工作流
- ✅ 声明式 Goal/Action DSL——代码结构清晰
- ✅ LLM 调用开销最小化（只在 Action 内部使用）
- ⚠️ 需要理解 GOAP 思维模式
- ⚠️ 社区相对较小（但增长迅速）

---

## 七、横向对比：三个框架的关键差异

### 7.1 推理循环（Reasoning Loop）

| 框架 | 实现方式 | 循环控制 |
|------|---------|---------|
| **Spring AI** | 自定义 `CallAdvisor` | 手动编写重试逻辑，灵活但代码量大 |
| **LangChain4j** | `@LoopAgent` + `@ExitCondition` | 声明式，一行注解控制循环和退出 |
| **Embabel** | `@State` 转换 + `@Action(canRerun=true)` | 状态机自动流转，`canRerun` 控制重试 |

### 7.2 工具调用（Tool Invocation）

| 框架 | 注册方式 | MCP |
|------|---------|-----|
| **Spring AI** | `.tools(bean)` + ToolCallback | ✅ spring-ai-starter-mcp-server |
| **LangChain4j** | `@ToolsSupplier` + Tool 对象 | ✅ 原生支持 |
| **Embabel** | `ai.withToolObject(obj)` | ✅ 通过 Action 暴露 |

### 7.3 记忆与状态管理

| 框架 | 短期记忆 | 长期记忆 | 跨 Agent 状态传递 |
|------|---------|---------|------------------|
| **Spring AI** | ChatMemory API | 需自定义 | 通过方法参数 |
| **LangChain4j** | @K 注解上下文 | 多种 Memory Store | @K 注解自动传递 |
| **Embabel** | @State 记录 | 需自定义 | 状态机 Record 传递 |

### 7.4 人机交互（Human-in-the-Loop）

Spring AI 实现了完整的 SSE（Server-Sent Events）交互机制：

```java
// Spring AI 实现：AskUserQuestionTool + SseInteractionController
@GetMapping(path = "/interactions/{id}/events", produces = "text/event-stream")
public SseEmitter interactionEvents(@PathVariable String interactionId) { ... }
```

用户可以在 Agent 执行过程中：
- 回答 Agent 提出的问题（偏好、口味等）
- 实时查看 Agent 的思考过程（流式事件推送）
- 干预决策（修改食谱方向）

---

## 八、Model Context Protocol（MCP）

MCP 是三个框架都重点支持的标准化协议，用于统一 Agent 访问外部数据和工具的方式。

### MCP 的核心价值

```
传统方式：   每个框架的自定义 Tool API → 绑定到特定生态
MCP 方式：  标准化 Server/Client 协议 → 工具可跨框架复用
```

**MCP Server 下载量增长趋势：** 10万 → 800万+（6个月内）

### 各框架的 MCP 集成

- **Spring AI**：`spring-ai-starter-mcp-server-webmvc`，自动配置 MCP Server
- **LangChain4j**：原生 MCP 客户端 + 服务端支持
- **Embabel**：通过 `@Action` 和 `@Export(remote=true)` 暴露 MCP 端点

---

## 九、可观测性（Observability）

三个框架都集成了 OpenTelemetry 协议，支持导出到 Grafana 栈。

### 技术栈

```
Docker Compose：
├── Grafana     → http://localhost:3000 (admin/admin)
├── Loki        → 日志聚合
├── Tempo       → 分布式追踪
└── Mimir       → 指标存储

OTLP Collector → localhost:4318 (HTTP) / 4317 (gRPC)
```

### 监控指标

- **Agent 调用率**（每秒调用次数）
- **执行时长**（p95 延迟）
- **活跃 Agent 数**（实时并发量）
- **HTTP 端点延迟**
- **JVM 指标**（内存、GC、线程）

### 启用方式

```bash
# 三步启用可观测性
docker compose --profile observability up -d
export SPRING_PROFILES_ACTIVE=ollama,observability
./mvnw spring-boot:run
```

### LangChain4j 的内置 Agent Monitor

```java
// 通过 AgentListener 自动收集指标
@AgentListenerSupplier
static AgentListener composedAgentListener() {
    return new ComposedAgentListener(
        new LoggingListener(),
        new MicrometerAgentListener(meterRegistry),
        agentMonitor
    );
}

// 自动收集的指标
// - agent_invocations_total（按 Agent 名标记）
// - agent_duration（执行时长直方图）
// - agent_active（当前活跃数 Gauge）
```

---

## 十、生产环境部署

### Azure Container Apps 一键部署

```bash
azd auth login
azd up
```

自动部署：
- Container Apps Environment
- Azure Container Registry
- Azure OpenAI（gpt-4o）
- **每个框架一个独立 Container App**

### 技术栈

- **Java 25** + **Spring Boot 3.5.13**
- **Virtual Threads**（默认启用）
- **Maven**（多模块构建）

### 本地运行

```bash
cd langchain4j   # 或 embabel, spring-ai
export SPRING_PROFILES_ACTIVE=ollama  # 或 openai, azure
./mvnw spring-boot:run
```

应用启动在 `http://localhost:8080`，使用 Basic Auth（`alice` / `123456`）。

### API 调用示例

```bash
curl -s -X POST http://localhost:8080/api/nutrition-plan \
  -u alice:123456 \
  -H "Content-Type: application/json" \
  -d '{
    "days": [
      { "day": "MONDAY",    "meals": ["BREAKFAST", "LUNCH", "DINNER"] },
      { "day": "TUESDAY",   "meals": ["BREAKFAST", "LUNCH", "DINNER"] },
      { "day": "WEDNESDAY", "meals": ["LUNCH", "DINNER"] }
    ],
    "countryCode": "DE",
    "additionalInstructions": "Prefer quick recipes with less than 30 minutes prep time."
  }'
```

---

## 十一、指导建议：如何选择框架

### 选型决策树

```
你的团队更看重什么？
│
├── Spring 生态深度集成？
│   └── ✅ Spring AI —— 如果项目已经在用 Spring Boot，这是最自然的选择
│
├── 声明式 Agent 组合 + 最少样板代码？
│   └── ✅ LangChain4j —— @Agent 接口 + AgenticServices 组合器
│
├── 确定性规划 + 可审计的工作流？
│   └── ✅ Embabel —— GOAP 引擎，动作序列可预测
│
├── 多 Agent 编排 + 图状工作流？
│   └── 考虑 LangGraph4j（LangChain4j 的扩展）
│
└── 更看重生产环境耐久性（崩溃恢复、审计追踪）？
    └── 考虑 JamJet 作为运行时层（可叠加在任何框架之上）
```

### 框架权衡速览

| 场景 | 推荐框架 | 理由 |
|------|---------|------|
| 快速原型、POC | Spring AI | 自动配置最省心 |
| 复杂多 Agent 工作流 | LangChain4j | 声明式组合能力最强 |
| 合规敏感场景 | Embabel | 确定性规划，可审计 |
| 已有 Spring Boot 项目 | Spring AI | 集成成本最低 |
| 需要最大 LLM 提供商支持 | LangChain4j | 生态最丰富 |
| 需要类型安全的 DSL | Embabel / Koog | Kotlin 原生类型安全 |
| 需要 MCP 标准化 | 三者都行 | 都支持 MCP 协议 |
| 云原生部署 | Quarkus + LangChain4j | GraalVM 原生镜像 |

---

## 十二、关键 Takeaways

1. **没有银弹。** 三个框架各有取舍，选择取决于团队的上下文和具体需求。

2. **Spring AI 最"Spring"。** 如果你的项目已经是 Spring Boot 生态，Spring AI 提供了最自然的开发体验——自动配置、Advisors 模式、与 Security/Actuator 无缝集成。

3. **LangChain4j 最灵活。** 声明式 @Agent 接口 + AgenticServices 组合器（sequence/loop）让复杂工作流的定义变得极其简洁。庞大的 Provider 生态也是巨大优势。

4. **Embabel 最独特。** GOAP 规划引擎让 Agent 行为变得可预测和可解释——这在合规场景中至关重要。状态机模型天然适合复杂工作流。

5. **MCP 是未来方向。** 标准化工具和数据的访问方式，让 Agent 的能力可以跨框架复用。

6. **"Agent" 不仅仅是调用 LLM。** 生产级的 Agent 系统需要：可观测性、人机交互、错误恢复、审计追踪——这些框架都在快速演进中。

7. **2026 年的 Java AI 生态已经成熟。** 从 2023 年的裸 HTTP 调用到现在的三个成熟框架 + MCP 协议栈，JVM 上的 AI Agent 开发已经具备了企业级的生产力。

---

*本文档基于 Spring I/O 2026 分享 "Comparing Agentic AI Frameworks for Java" 整理，结合了演讲内容、源代码分析和相关生态调研。*
