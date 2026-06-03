# Embabel AI Agent Framework 最佳实践

> **一站式指南：从入门到生产级 GOAP 智能体开发**
>
> 作者：Rod Johnson（Spring 创始人）| 框架定位：JVM 上的下一代 Agent 框架
> 关键词：GOAP、OODA 循环、强类型 Agent、Spring 集成、LLM 混用、多 Action 编排、Persona

---

## 目录

1. [背景与定位](#1-背景与定位)
2. [核心概念](#2-核心概念)
3. [快速开始：5 分钟跑通第一个 Agent](#3-快速开始)
4. [深入理解：GOAP 规划引擎](#4-深入理解-goap-规划引擎)
5. [三种执行模式详解](#5-三种执行模式详解)
6. [开发姿势：Java 注解 vs Kotlin DSL](#6-开发姿势)
7. [编程最佳实践](#7-编程最佳实践)
8. [生产级配置：LLM 混用与平台适配](#8-生产级配置)
9. [测试策略](#9-测试策略)
10. [常见陷阱与解决方案](#10-常见陷阱与解决方案)
11. [完整示例](#11-完整示例)
12. [生态与资源](#12-生态与资源)

---

## 1. 背景与定位

### 1.1 什么是 Embabel？

Embabel（发音 /ɛmˈbeɪbəl/）是由 **Spring 框架创始人 Rod Johnson** 打造的新一代 JVM Agent 框架。它不是一个简单的 LLM 封装库，而是一个 **目标导向的智能体（Goal-Oriented Agent）编排平台**。

> **一句话定位：** Embabel 之于 Spring AI，就像 Spring MVC 之于 Servlet API。

Rod Johnson 形容 Embabel 是他自 Spring 以来最重要的项目。框架用 Kotlin 编写，但对 Java 开发者非常友好。

### 1.2 与同类框架的对比

| 特性 | Embabel | Spring AI | LangChain4j |
|------|---------|-----------|-------------|
| 抽象层级 | **高**（Agent 编排） | **中**（LLM 集成） | **中**（LLM 集成） |
| 规划能力 | **GOAP 算法** 动态规划 | FSM / 手动编排 | 链式 / 手动编排 |
| 强类型 | ✅ 全程强类型 | ⚠️ 部分 | ⚠️ 部分 |
| 测试支持 | 一等公民 | 一般 | 一般 |
| 执行模式 | Focused / Closed / Open | 手动 | 手动 |
| 核心语言 | Kotlin（Java 互操作一流） | Java | Java |

> **Rod Johnson 的原话：** "Embabel 提供的是比 LangChain4j 和 Spring AI 高得多的抽象层。它建立在 Spring AI 之上，但引入了全新的原创思想。"

### 1.3 Embabel vs Spring AI（一文讲清）

这是一个常见疑问。关键在于：**Embabel 和 Spring AI 是不同抽象层**：

| 维度 | Spring AI | Embabel |
|------|-----------|---------|
| 定位 | AI 集成框架 | Agent 编排框架 |
| 职责 | 模型抽象（Chat/Embedding/Image）、向量存储、工具调用 | 目标驱动的 Action 编排、GOAP 规划、条件评估 |
| 关系 | Spring AI 是 LLM 调用层 | Embabel 可以**运行在 Spring AI 之上**，用其模型抽象 |
| 编排 | 开发者硬编码 chain / flow | 系统用 GOAP 算法**动态规划** Action 序列 |
| 典型使用 | 聊天、RAG、简单工具链 | 多步推理、条件分支、自适应重规划 |

**实践中**：
- Spring AI 帮你"和模型说话、连接 AI 组件"
- Embabel 帮你"构建 Agent —— Agent 自主决定执行哪些 Action 来达成 Goal，并动态重规划"

### 1.4 为什么需要 Agent 框架？

直接调用 LLM API 也能写代码，但 Agent 框架提供了：

- **拆分 LLM 交互**：让每次调用更简单、更聚焦 → 降低成本和错误
- **最大化复用**：Action、Goal、Condition 组件化
- **可测试性**：单元测试和端到端测试同等重要
- **可组合性**：子流程和独立 Action 可随意组合
- **安全护栏**：在多个环节施加保护
- **规划能力**：系统自动发现路径，而非程序员硬编码

### 1.5 JVM 还是 Python？

> "Agent 框架最初确实以 Python 为主，但现在还很早期，还有大量创新空间。关键的不在于与 LLM 的邻接关系（LLM 只是一个 HTTP 调用），而在于**现有的代码和基础设施资产——这些在 JVM 上远比 Python 有价值**。"

**Embabel 的核心信念：** Java 团队不需要切到 Python 来开发 AI 应用。现有的业务逻辑、基础设施、工具链可以直接复用。通过强类型和在确定性代码中使用 LLM，你得到的 Agent "既智能，又不失控"。

---

## 2. 核心概念

Embabel 用五个核心抽象来描述 Agentic Flow：

### 2.1 Action（动作）

Agent 执行的最小工作单元。可以是一个 LLM 调用、一段业务代码、一个外部 API 请求。每个 Action 有类型化的输入和输出。

```java
@Action(description = "Retrieve daily horoscope for a person")
public Horoscope retrieveHoroscope(StarPerson starPerson) {
    return new Horoscope(horoscopeService.dailyHoroscope(starPerson.sign()));
}
```

### 2.2 Goal（目标）

Agent 试图达成的状态。Goal 由 `@AchievesGoal` 注解标记在某个 Action 方法上——意味着一旦这个 Action 成功执行，Goal 就算达成。

```java
@AchievesGoal(
    description = "Write an amusing writeup for the target person based on their horoscope and current news stories",
    export = @Export(remote = true, name = "starNewsWriteupJava",
        startingInputTypes = {StarPerson.class, UserInput.class})
)
@Action
public Writeup writeup(/* ... */) { /* ... */ }
```

Goal 可以使用 `examples` 属性提供自然语言示例，帮助系统理解该 Goal 的适用范围：

```java
@AchievesGoal(
    description = "Investigate an incident signal and produce a complete incident case",
    examples = {
        "Investigate telemetry anomalies near (lon,lat) in a time window and propose containment",
        "Assess implant incident risk and recommend actions"
    })
```

### 2.3 Condition（条件）

执行 Action 前的前置条件（Precondition），或判断 Goal 是否达成的后置条件。每次 Action 执行后都会重新评估（形成 OODA 循环）。

大部分 Conditions 由**数据流自动推断**：当一个 Action 的输入类型是另一个 Action 的输出类型时，框架自动推导出依赖关系。GOAP 规划器利用这些依赖关系决定 Action 的执行顺序和并行性。

### 2.4 Domain Model（领域模型）

支撑 Flow 的对象模型，可以包含行为。**这是强类型的核心优势**——所有 Action、Goal、Condition 都由领域模型驱动。

```java
// ✅ 好的设计：明确的类型
public record IncidentSignal(
    @NotNull double longitude,
    @NotNull double latitude,
    @Positive double radiusMeters,
    @NotNull @Past LocalDateTime from,
    @NotNull @Past LocalDateTime to,
    @NotNull @NotEmpty String metric,
    @Positive double threshold
) { }
```

### 2.5 Plan（计划）

达成 Goal 的 Action 序列。关键在于：**计划由系统动态生成，而不是程序员硬编码**。每次 Action 完成后系统会重新规划（Replanning），形成 OODA 循环：

```
Observe → Orient → Decide → Act → (loop)
```

### 2.6 核心差异化优势

| 优势 | 说明 |
|------|------|
| **真正规划** | 不用 FSM，用非 LLM 的 AI 算法（GOAP）做路径发现 |
| **超级可扩展** | 新增 Domain、Action、Goal 即可增强系统能力，无需修改现有代码 |
| **强类型安全** | `Map<String, Object>` 的噩梦结束了——编译期检查、重构支持 |
| **平台无关** | 编程模型与运行平台分离：本地开发 → 生产高 QoS，代码不变 |
| **LLM 混用** | 轻松混合不同模型，关键任务用强模型，简单任务用便宜/本地模型 |
| **确定性 + 非确定性混合** | LLM 用于"模糊"部分（解析、假设生成），Java 用于"硬"部分（查询、评分、规则） |

---

## 3. 快速开始

### 3.1 创建项目

从模板创建（最简单）：

1. 使用 [Java Agent Template](https://github.com/embabel/java-agent-template) 或 [Kotlin Agent Template](https://github.com/embabel/kotlin-agent-template)
2. 点击 GitHub 的 "Use this template" 按钮
3. 配置 `OPENAI_API_KEY` 环境变量
4. 确保已安装 Maven

**5 分钟不到就能跑起来一个 Agent！**

或者从 Spring Initializr 手动创建：选择 Spring Boot **3.5.x**（Embabel 暂不支持 Boot 4.x），语言 Java 17+。

### 3.2 Maven 依赖

```xml
<!-- 版本属性 -->
<properties>
    <java.version>25</java.version>
    <embabel.version>0.4.0-SNAPSHOT</embabel.version>
    <spring-ai.version>1.1.4</spring-ai.version>
</properties>

<!-- Spring AI BOM -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.ai</groupId>
            <artifactId>spring-ai-bom</artifactId>
            <version>${spring-ai.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<!-- Embabel Starter + LLM Provider -->
<dependencies>
    <dependency>
        <groupId>com.embabel.agent</groupId>
        <artifactId>embabel-agent-starter-shell</artifactId>
        <version>${embabel.version}</version>
    </dependency>
    <dependency>
        <groupId>org.springframework.ai</groupId>
        <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
    </dependency>
</dependencies>
```

**LLM Provider 选项**：

| Starter | 用途 |
|---------|------|
| `embabel-agent-starter-shell` | Spring Shell 交互式应用（开发/学习最佳） |
| `embabel-agent-starter` | 核心 Starter（无 Shell，用于 Web App） |
| `spring-ai-openai-spring-boot-starter` | OpenAI 模型 |
| `embabel-agent-starter-ollama` | Ollama 本地模型 |

**注意**：需要添加 Embabel Snapshot 仓库到 `pom.xml` 才能解析依赖。

### 3.3 配置

**application.properties 或 application.yaml**：

```yaml
# 禁用 Web 应用，启用 Spring Shell 交互模式
spring:
  main:
    web-application-type: none
  shell:
    interactive:
      enabled: true

embabel:
  models:
    default-llm: gpt-4.1-mini    # 默认模型（便宜快速）
    llm:
      reviewer: gpt-4.1           # 按角色指定不同模型

spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
```

**Ollama 配置**：

```properties
embabel.models.default-llm=llama3.1:8b
```

### 3.4 第一个 Agent（Hello World）

```java
@Agent(description = "A simple greeting agent")
public class HelloAgent {

    @Action
    public Greeting greet(UserInput input, Ai ai) {
        return ai
            .withDefaultLlm()
            .createObject(
                "Generate a friendly greeting for: " + input.getContent(),
                Greeting.class
            );
    }
}
```

Spring Boot 启动后自动扫描 `@Agent` 类，像 Spring Bean 一样管理。

### 3.5 运行 Agent

启动应用后，Embabel 控制台显示 ASCII Art 和命令提示符。内置命令：

| 命令 | 功能 |
|------|------|
| `agents` | 列出所有注册的 Agent、Goal、Action |
| `models` | 列出可用 LLM 和角色映射 |
| `x <message>` / `execute <message>` | 执行 Agent |

```bash
x How to get started with Spring Boot
```

加 `-p` 参数可查看详细调试输出（包含发送给 LLM 的完整消息和 JSON Schema）：

```bash
x -p How to get started with Spring Boot
```

---

## 4. 深入理解：GOAP 规划引擎

### 4.1 什么是 GOAP？

**Goal-Oriented Action Planning（目标导向行动规划）** 最初来自游戏 AI（如《F.E.A.R.》），是一种 **非 LLM 的 AI 规划算法**。Embabel 使用 A* 搜索算法实现 GOAP。

### 4.2 GOAP 的工作原理

1. **系统状态**：当前的世界状态（由 Domain Model 描述）
2. **Goal**：期望的目标状态（由 `@AchievesGoal` 定义）
3. **Action 的 Preconditions / Effects**：
   - 某个 Action 执行前需要什么条件（输入类型）
   - 执行后会产出什么（输出类型，改变世界状态）
4. **规划器**：从当前状态出发，通过 A* 搜索一条 Action 序列，使目标状态达成

### 4.3 与 LLM 规划的区别

| 维度 | GOAP | LLM 规划 |
|------|------|----------|
| 确定性 | **高**（算法保证） | 低（概率输出） |
| 可解释性 | **强**（可追踪规划树） | 弱（黑盒） |
| 效率 | **优**（最小化 LLM 调用） | 差（每次都要 LLM 决策） |
| 组合性 | **强**（新 Action 自动可用） | 一般 |
| 并行决策 | **原生支持**（无依赖 Action 可并行） | 需手动编排 |

> GOAP 作为默认规划器，但也支持 **Utility AI**（基于效用分数的行动选择），适用于探索性、开放性任务。

### 4.4 OODA 循环

每次 Action 执行后，系统会自动触发 Replanning：

```
当前状态 → GOAP 规划 → 执行首个 Action → 观察新状态 → 重新规划 → ...
```

这意味着：
- Agent 能适应执行过程中的新信息
- 如果第一步执行效果不如预期，后续计划会自动调整
- 无需程序员编写异常处理的 FSM

### 4.5 Utility AI（备用规划器）

当任务目标是"探索最优解"而非"达成特定状态"时，Utility AI 更适合：

```kotlin
// Kotlin DSL with Utility AI
agent {
    planningStrategy = PlanningStrategy.UTILITY
    
    action("explore") {
        utility = { state -> state.energyLevel * 0.3 + state.curiosity * 0.7 }
        execute { /* 探索行为 */ }
    }
    
    action("rest") {
        utility = { state -> (100 - state.energyLevel) * 0.5 }
        execute { /* 休息行为 */ }
    }
}
```

---

## 5. 三种执行模式详解

### 5.1 Focused Mode（聚焦模式）

**最适合的场景**：代码驱动的流程，如响应事件的回调、REST API 触发

**特点**：
- 用户代码直接调用特定 Agent，传入输入
- 只运行该 Agent 内的 Action
- 确定性强，不做 Agent 选择

```java
// 在 Spring Bean 中调用
@Autowired
private AgentPlatform agentPlatform;

public void handleIncomingEvent(Event event) {
    var result = agentPlatform.run(
        MyAgent.class,    // 指定 Agent
        new UserInput(event.getPayload())
    );
}
```

### 5.2 Closed Mode（封闭模式）

**最适合的场景**：有明确意图分类的入口，如客服工单路由

**特点**：
- 系统根据用户意图（或事件）选择合适的 Agent
- Agent 选择是动态的，但只运行被选中 Agent 内的 Action
- 通过 `AgentPlatform` 自动分类

```java
// 自动选择 Agent
var result = agentPlatform.runClosed(new UserInput("Book a flight to London"));
// 系统会自动匹配 TravelAgent vs WeatherAgent
```

### 5.3 Open Mode（开放模式）

**最强但确定性最低的模式**

**特点**：
- 系统评估用户意图后，从**所有已知 Goal** 中找到最匹配的
- 动态构建一个"临时 Agent"，包含必要的 Action 和 Conditions
- 可能跨多个 Provider 组合功能
- 如果系统不确定 Goal 的适用性，会拒绝执行
- 可通过 `GoalChoiceApprover` 接口限制 Goal 选择

```java
var result = agentPlatform.runOpen(new UserInput("Plan a weekend trip to Paris with flight under $500"));
```

### 5.4 未来模式：Evolving Mode

系统可以在同一进程中处理多个 Goal，并在运行时动态添加新 Goal 和 Agent——
例如一个 Action 执行过程中发现需要额外实现另一个 Goal。

---

## 6. 开发姿势

### 6.1 Java 注解风格（推荐给 Spring 团队）

```java
@Agent(description = "旅游规划助手")
public class TravelAgent {

    private final FlightService flightService;
    private final HotelService hotelService;

    public TravelAgent(FlightService flightService, HotelService hotelService) {
        this.flightService = flightService;
        this.hotelService = hotelService;
    }

    @Action(description = "Parse user input into structured trip data")
    public TripInput parseInput(UserInput input, Ai ai) {
        return ai.createObject(
            "Extract destination, dates, and budget from: " + input.getContent(),
            TripInput.class
        );
    }

    @Action(description = "Search for available flights")
    public FlightOptions searchFlights(TripInput trip, Ai ai) {
        return ai.withLlm(OpenAiModels.GPT_41_MINI)
                 .createObject("Find flights: " + trip, FlightOptions.class);
    }

    @AchievesGoal(description = "Complete travel plan")
    @Action(description = "Assemble a complete travel itinerary")
    public Itinerary buildPlan(TripInput trip, FlightOptions flights, Ai ai) {
        return ai.withLlm(OpenAiModels.GPT_41)
                 .createObject("Create travel plan: " + trip, Itinerary.class);
    }
}
```

**关键注解**：

| 注解 | 用途 |
|------|------|
| `@Agent` | 标记一个类为 Agent（类似 `@Controller`，也是 `@Component`） |
| `@Action` | 标记一个方法为 Action，`description` 用于规划器理解 |
| `@AchievesGoal` | 声明完成该 Action 即达成某个 Goal，`examples` 提供自然语言匹配 |
| `@Condition` | 标记条件评估方法 |

### 6.2 Kotlin DSL 风格

```kotlin
agent {
    description = "旅游规划助手"
    
    action("parseInput") {
        input { UserInput::class to TripInput::class }
        execute { input ->
            ai.createObject("Extract info from: ${input.content}", TripInput::class)
        }
    }
    
    action("searchFlights") {
        execute { trip ->
            ai.withLlm(OpenAiModels.GPT_41_MINI)
              .createObject("Find flights: $trip", FlightOptions::class)
        }
    }
    
    achievesGoal(action = "buildPlan", description = "Complete travel plan")
    action("buildPlan") {
        execute { (trip, flights) ->
            ai.withLlm(OpenAiModels.GPT_41)
              .createObject("Create plan", Itinerary::class)
        }
    }
}
```

### 6.3 Java vs Kotlin：选择指南

**Rod Johnson 选择 Kotlin 实现的原因**：
- Null 安全性
- 更简洁的集合操作
- Reified 泛型消除类型擦除问题

**但 Java 使用完全没有障碍**：
- 「你看不到 Kotlin 风格的 Kt 导入」
- 「我们在需要的地方加了 Java 代码确保 Java 体验」
- **Embabel 是 JVM 框架，不是 Kotlin 框架**

> 💡 **建议**：现有 Spring 项目用 Java 注解风格，新项目可考虑 Kotlin DSL。

---

## 7. 编程最佳实践

### 7.1 Action 粒度原则

**✅ 推荐**：
- 每个 Action 只做一件事（单一职责）
- Action 越细，GOAP 规划能力越强（更多组合可能性）
- 每个 Action 的 LLM Prompt 尽量聚焦

**❌ 避免**：
- 一个 Action 做 N 个 LLM 调用
- Action 太粗导致无法复用

```
✅ parseInput → queryDatabase → scoreResults → assembleReport
❌ doEverything → generateFullReport  (一个 Action 包揽所有)
```

### 7.2 Domain Model 设计

Domain Model 是 Embabel 的心脏。**强类型**的好处：

```java
// ✅ 好的设计：明确的类型
public record IncidentSignal(
    @NotNull double longitude,
    @NotNull double latitude,
    @Positive double radiusMeters,
    @NotNull @Past LocalDateTime from,
    @NotNull @Past LocalDateTime to,
    @NotNull @NotEmpty String metric,
    @Positive double threshold
) { }

public enum RiskLevel { LOW, MEDIUM, HIGH, CRITICAL }

public record IncidentAssessment(
    IncidentSignal signal,
    int numberOfLogs,
    RiskLevel riskLevel
) { }

// ❌ 糟糕的设计：Map 地狱
public class TripInput {
    private Map<String, Object> rawData;  // 失去了所有类型信息
}
```

**基本原则**：
- 每个 Action 的输入输出都用具体类型
- 避免 `Map<String, Object>` 传递数据
- 利用 Java 的重构支持（重命名、提取等）

### 7.3 LLM 使用策略：只在需要的地方用 LLM

Embabel 的核心模式：**LLM 用于模糊部分，Java 处理硬逻辑**。

```java
@Action
public IncidentAssessment triageIncidentSignal(UserInput input, OperationContext context) {
    // ⚡ LLM 部分：将用户自然语言解析为结构化对象
    IncidentSignal signal = context.ai().withDefaultLlm().createObject(
        """
        Extract an IncidentSignal from the user's message.
        - lon is a number in [-180, 180]
        - lat is a number in [-90, 90]
        ...
        """, IncidentSignal.class);

    // 🔧 确定性部分：业务规则，不需要 LLM
    Map<String, List<ImplantMonitoringLog>> logs = logService.findLogsByAreaAndTime(...);
    RiskLevel risk = classifyRisk(logs, signal);

    // ✅ 返回强类型结果
    return new IncidentAssessment(signal, logs.size(), risk);
}
```

**策略建议**：

| 任务类型 | 推荐模型 | 原因 |
|---------|---------|------|
| 意图理解、结构化提取 | 强模型（GPT-4.1, Claude） | 精度要求高 |
| 分类、格式转换 | 小模型（GPT-4.1-Mini） | 成本低 |
| 敏感数据 / 离线场景 | 本地模型（Ollama） | 隐私和成本 |
| 总结、摘要 | 便宜模型 | 质量够用 |

### 7.4 Persona（角色）可复用设计

Embabel 支持提取角色描述为可复用的 Persona 对象，减少 Prompt 重复：

```java
public abstract class Personas {
    public static final RoleGoalBackstory WRITER = new RoleGoalBackstory(
        "Software developer and educator",
        "Write practical, beginner-friendly blog posts",
        "Experienced developer who loves teaching through clear, simple writing"
    );

    public static final RoleGoalBackstory REVIEWER = new RoleGoalBackstory(
        "Technical editor",
        "Review and improve blog posts for clarity and accuracy",
        "Meticulous editor with deep technical knowledge"
    );
}

// 在 Action 中使用
@Action(description = "Write a first draft of the blog post")
public BlogDraft writeDraft(UserInput userInput, Ai ai) {
    return ai.withDefaultLlm()
        .withId("blog-post-draft-writer")
        .withPromptContributor(Personas.WRITER)     // 👈 注入角色
        .creating(BlogDraft.class)
        .fromPrompt("""Write a blog post about %s. ...""".formatted(userInput.getContent()));
}
```

好处：角色定义与任务指令分离，多个 Action 可共享同一角色，角色可组合。

### 7.5 按角色分配 LLM

通过 `withLlmByRole("roleName")`，可以将不同 Action 路由到不同模型，在配置文件中定义：

```yaml
embabel:
  models:
    default-llm: gpt-4.1-mini    # 写作用便宜模型
    llm:
      reviewer: gpt-4.1           # 审阅用强模型
```

```java
@Action(description = "Review and improve the draft")
@AchievesGoal(description = "A reviewed and polished blog post")
public ReviewedPost reviewDraft(BlogDraft draft, Ai ai) {
    return ai.withLlmByRole("reviewer")    // 👈 使用 reviewer 角色对应的模型
        .creating(ReviewedPost.class)
        .fromPrompt("Review and improve this blog post...");
}
```

### 7.6 AI API 使用模式

| API | 用途 | 示例 |
|-----|------|------|
| `ai.withDefaultLlm()` | 使用配置的默认模型 | `ai.withDefaultLlm().createObject(prompt, TargetType.class)` |
| `ai.withLlm("model-name")` | 使用指定模型 | `ai.withLlm(OpenAiModels.GPT_41).createObject(...)` |
| `ai.withLlmByRole("roleName")` | 使用配置中按角色映射的模型 | `ai.withLlmByRole("reviewer").createObject(...)` |
| `withId("unique-id")` | 为本次 LLM 调用设置 ID（便于调试/追踪） | `.withId("blog-post-draft-writer")` |
| `withPromptContributor(persona)` | 注入 Persona 角色描述 | `.withPromptContributor(Personas.WRITER)` |
| `creating(Class)` | 指定结构化输出类型 | `.creating(BlogDraft.class)` |
| `createObject(prompt, Class)` | 创建结构化对象 | `ai.createObject(prompt, MyType.class)` |
| `createObject(formattedPrompt, Class)` | 同上，使用格式化字符串 | `context.ai().withDefaultLlm().createObject(msg, IncidentSignal.class)` |

### 7.7 数据流驱动 Conditions

大多数情况下不需要显式定义 Conditions —— 框架会根据 Action 间的数据依赖自动推断前置和后置条件：

```java
// Action1 输出 FlightOptions → Action2 自动等待 FlightOptions 可用
// 无需手动配置顺序！
@Action
public FlightOptions searchFlights(TripInput trip) { ... }

@Action
public Itinerary buildPlan(FlightOptions flights, HotelOptions hotels) { ... }
// ↑ 这自动要求 searchFlights 和 searchHotels 先执行
```

在 GOAP 中，Action 依赖有向无环图（DAG）自然支持并行化：**没有依赖关系的 Action 可以并行执行**。

### 7.8 安全性：Guardrails

```java
@Action
public SafeOutput processSensitiveData(UserInput input, Ai ai) {
    // 在 LLM 调用前后添加安全检查
    var sanitized = sanitize(input);
    var result = ai.createObject(prompt, SensitiveOutput.class);
    return validateOutput(result);
}
```

**多层安全策略**：
1. **输入层**：过滤注入/越权输入
2. **Prompt 层**：限制 LLM 行为边界
3. **输出层**：验证输出合法性和类型
4. **Action 层**：前置条件检查
5. **Goal 层**：`GoalChoiceApprover` 限制 Goal 选择

### 7.9 @Export 与远程 API

```java
@AchievesGoal(
    description = "Provide weather info for a city",
    export = @Export(remote = true, name = "weatherJava",
        startingInputTypes = {CityQuery.class})
)
@Action
public WeatherReport getWeather(CityQuery query, Ai ai) {
    // 这个 Action 可以作为远程 API 暴露
}
```

---

## 8. 生产级配置

### 8.1 平台抽象

```properties
# 开发环境
embabel.platform=local

# 生产环境（自动切换更高 QoS，代码不变）
embabel.platform=production
```

### 8.2 多 LLM Provider 配置

```yaml
embabel:
  models:
    default-llm: gpt-4.1
    llm:
      reviewer: gpt-4.1
      writer: gpt-4.1-mini

spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
    ollama:
      base-url: http://localhost:11434
```

### 8.3 重试与持久化

```java
@Action(retry = 3, persistState = true)
public CriticalOperation doSomethingImportant(Input input) {
    // 失败自动重试 + 状态持久化
}
```

结合 Spring 的声明式事务和持久化能力：
- Agent 执行过程中的状态可以被持久化
- 失败后可恢复
- 支持分布式事务

### 8.4 监控与运维

- **Spring AOP**：可以装饰 Action（日志、指标、鉴权）
- **SonarQube**：项目已集成代码质量扫描
- **YourKit / JProfiler**：项目支持性能分析
- **GitHub Actions**：CI/CD 流水线

---

## 9. 测试策略

### 9.1 单元测试

Agent 像 Spring Bean 一样可以单元测试：

```java
@SpringBootTest
class StarNewsFinderTest {

    @Autowired
    private StarNewsFinder agent;

    @MockBean
    private HoroscopeService horoscopeService;

    @Test
    void testExtractStarPerson() {
        when(horoscopeService.dailyHoroscope(any()))
            .thenReturn("Today is a good day for creativity.");

        var input = new UserInput("I'm Alice, a Leo");
        var person = agent.extractStarPerson(input, mockAi());

        assertEquals("Alice", person.getName());
        assertEquals("Leo", person.getSign());
    }
}
```

### 9.2 集成测试

Embabel 提供了专用的测试库，可以对整个 Agentic Flow 做端到端测试：

```java
@AgentTest
class TravelAgentIntegrationTest {

    @Test
    void testFullTripPlanning() {
        var agentPlatform = AgentTestPlatform.create()
            .withAgent(TravelAgent.class)
            .build();

        var result = agentPlatform.runFocused(
            TravelAgent.class,
            new UserInput("Book a flight to Tokyo next week")
        );

        assertNotNull(result);
        assertInstanceOf(Itinerary.class, result);
    }
}
```

### 9.3 Prompt 测试

Agent Prompt 是可以测试的——有专门的测试库支持：

```java
// 验证 Prompt 的结构和安全性
@Test
void testPromptStructure() {
    var prompt = PromptTestUtil.extractPrompt(StarNewsFinder.class, "findNewsStories");
    assertTrue(prompt.contains("astro"));
    assertFalse(prompt.contains("ignore previous instructions"));
}
```

---

## 10. 常见陷阱与解决方案

### ❌ 陷阱 1：Domain Model 使用 Map 传递数据

```java
// 错误
@Action
public Map<String, Object> doSomething(Map<String, Object> input) { ... }

// 正确：用具体类型
@Action
public SpecificOutput doSomething(SpecificInput input) { ... }
```

### ❌ 陷阱 2：Action 粒度太粗

```java
// 错误：一个 Action 做所有事
@Action
public FullPlan doEverything(UserInput input, Ai ai) { ... }

// 正确：拆分为多个可组合的 Action
@Action
public ParsedInput parse(UserInput input, Ai ai) { ... }
@Action
public SearchResults search(ParsedInput input, Ai ai) { ... }
@Action @AchievesGoal(...)
public FullPlan build(ParsedInput input, SearchResults results, Ai ai) { ... }
```

### ❌ 陷阱 3：在 Open 模式下期望完全确定性

Open 模式是最强大的，但也最不可预测。**先确定用哪种模式**：
- 需要确定性 → Focused Mode
- 需要意图路由 → Closed Mode
- 需要创造性组合 → Open Mode

### ❌ 陷阱 4：忽略 LLM 成本

```java
// 错误：所有 Action 都用最强模型
@Action
public CheapTask doCheap(Input input, Ai ai) {
    return ai.withLlm(OpenAiModels.GPT_41).createObject(...);
}

// 正确：按任务复杂度分配模型
@Action
public CheapTask doCheap(Input input, Ai ai) {
    return ai.withLlm(OpenAiModels.GPT_41_MINI).createObject(...);
}
```

### ❌ 陷阱 5：不写测试

Agent 系统引入 LLM 后，不确定性增加，测试比传统应用更重要：
- 单元测试验证 Action 逻辑
- 集成测试验证 Flow 编排
- Prompt 测试验证提示安全性

### ❌ 陷阱 6：让 LLM 做所有事（包括业务逻辑）

```java
// 错误：让 LLM 做风险评分（应该用确定性代码）
@Action
public RiskLevel assessRisk(IncidentSignal signal, Ai ai) {
    return ai.createObject("What is the risk level?", RiskLevel.class);
}

// 正确：LLM 只做解析，评分用代码规则
@Action
public IncidentAssessment assessIncident(UserInput input, Ai ai) {
    IncidentSignal signal = /* LLM 解析输入 */;
    RiskLevel risk = classifyRisk(logs, signal);  // 确定性规则
    return new IncidentAssessment(signal, risk);
}
```

---

## 11. 完整示例

### 11.1 StarNewsFinder Agent（星座新闻搜索）

来自 Embabel 官方示例库：

```java
@Agent(description = "基于用户星座查找相关新闻")
public class StarNewsFinder {

    private final HoroscopeService horoscopeService;
    private final int storyCount;

    public StarNewsFinder(
            HoroscopeService horoscopeService,
            @Value("${star-news-finder.story.count:5}") int storyCount) {
        this.horoscopeService = horoscopeService;
        this.storyCount = storyCount;
    }

    // Action 1: 提取用户信息
    @Action
    public StarPerson extractStarPerson(UserInput userInput, Ai ai) {
        return ai
            .withLlm(OpenAiModels.GPT_41)
            .createObjectIfPossible(
                "Create a person from this user input, extracting their name and star sign: %s"
                    .formatted(userInput.getContent()),
                StarPerson.class
            );
    }

    // Action 2: 获取星座运势（纯业务代码，无 LLM）
    @Action
    public Horoscope retrieveHoroscope(StarPerson starPerson) {
        return new Horoscope(
            horoscopeService.dailyHoroscope(starPerson.sign())
        );
    }

    // Action 3: 搜索相关新闻（使用 Web 工具）
    @Action(toolGroups = {CoreToolGroups.WEB})
    public RelevantNewsStories findNewsStories(
            StarPerson person, Horoscope horoscope, Ai ai) {
        var prompt = """
            %s is an astrology believer with the sign %s.
            Their horoscope for today is:
            <horoscope>%s</horoscope>
            Use web tools to find %d relevant news stories.
            """.formatted(person.getName(), person.getSign(),
                          horoscope.summary(), storyCount);
        return ai.withDefaultLlm()
                 .createObject(prompt, RelevantNewsStories.class);
    }

    // Action 4（最终 Goal）：生成趣味文章
    @AchievesGoal(
        description = "Write an amusing writeup for the target person",
        export = @Export(remote = true, name = "starNewsWriteupJava",
            startingInputTypes = {StarPerson.class, UserInput.class})
    )
    @Action
    public Writeup writeup(
            StarPerson person,
            RelevantNewsStories relevantNewsStories,
            Horoscope horoscope,
            Ai ai) {
        return ai.withLlm(
            LlmOptions.withModel(OpenAiModels.GPT_41_MINI)
                      .withTemperature(0.9) // 更高温度增加创意
        ).createObject(prompt, Writeup.class);
    }
}
```

> 📁 完整代码见：https://github.com/embabel/embabel-agent/tree/main/embabel-agent-examples

### 11.2 Incident Triage Agent（赛博朋克事件响应）

来自 BellSoft 博客的完整示例，展示多 Action 工作流：

**领域模型**：

```java
public record IncidentSignal(
    @NotNull double longitude, @NotNull double latitude,
    @Positive double radiusMeters,
    @NotNull @Past LocalDateTime from, @NotNull @Past LocalDateTime to,
    @NotNull @NotEmpty String metric, @Positive double threshold
) { }

public enum RiskLevel { LOW, MEDIUM, HIGH, CRITICAL }

public record IncidentAssessment(IncidentSignal signal, int numberOfLogs, RiskLevel riskLevel) { }

public record AffectedImplant(String lotNumber, String model, /* ... */) { }

public record RootCauseHypothesis(String summary, String mechanism, double confidence) { }

public record EstimatedBlastRadius(
    int affectedEstimate, List<String> affectedLots,
    List<String> affectedModels, String geoSummary, String timeSummary
) { }

public record ContainmentPlan(String summary, List<ContainmentStep> steps) { }

public record ContainmentStep(String text) { }

public record IncidentCase(
    String id, Instant timestamp, IncidentSignal signal,
    IncidentAssessment assessment, List<AffectedImplant> affected,
    RootCauseHypothesis hypothesis, ContainmentPlan plan
) { }
```

**Agent 实现（6 个 Action，GOAP 自动规划）**：

```java
@Agent(description = "Investigates and assesses implant telemetry anomalies")
public class IncidentTriageAgent {

    private final ImplantMonitoringLogService logService;

    public IncidentTriageAgent(ImplantMonitoringLogService logService) {
        this.logService = logService;
    }

    // Action 1: LLM 解析 → 结构化
    @Action(description = "Parse user's message into an IncidentSignal")
    public IncidentSignal parseIncidentSignal(UserInput input, OperationContext context) {
        return context.ai().withDefaultLlm().createObject(/* parsing prompt */, IncidentSignal.class);
    }

    // Action 2: 确定性数据库查询
    @Action(description = "Query monitoring logs from MongoDB")
    public AllAffectedImplants queryImplants(IncidentSignal signal, OperationContext context) {
        var logs = logService.findLogsByAreaAndTime(/* ... */);
        /* 确定性地提取受影响的植入物清单 */
        return new AllAffectedImplants(affected);
    }

    // Action 3: 确定性风险评估
    @Action(description = "Create risk assessment based on collected logs")
    public IncidentAssessment assessRisk(
            IncidentSignal signal, AllAffectedImplants affected, OperationContext context) {
        var risk = classifyRisk(affected, signal);  // 纯代码逻辑
        return new IncidentAssessment(signal, affected.implants().size(), risk);
    }

    // Action 4: LLM 假设生成（受约束的结构化输出）
    @Action(description = "Form a hypothesis about root cause")
    public RootCauseHypothesis hypothesize(
            AllAffectedImplants affected, IncidentAssessment assessment, OperationContext context) {
        return context.ai().withDefaultLlm().createObject(
            """
            Based on the implant assessment, suggest a root cause.
            - summary: one sentence cause
            - mechanism: detailed explanation
            - confidence: 0.0 to 1.0
            """, RootCauseHypothesis.class);
    }

    // Action 5: LLM + 确定性混合（爆炸半径估算用代码，应急计划用 LLM）
    @Action(description = "Estimate blast radius and build containment plan")
    public ContainmentPlan planContainment(
            IncidentSignal signal, AllAffectedImplants affected,
            RootCauseHypothesis hypothesis, OperationContext context) {
        var blastRadius = estimateRadius(signal, affected.implants());  // 确定性
        return context.ai().withDefaultLlm().createObject(
            "Generate a containment plan with 4-8 steps", ContainmentPlan.class);
    }

    // Action 6（最终 Goal）：组装最终用例
    @AchievesGoal(
        description = "Investigate an incident signal and produce a complete incident case",
        examples = {
            "Investigate telemetry anomalies near (lon,lat) in a time window and propose containment",
            "Assess implant incident risk and recommend actions"
        })
    @Action(description = "Assemble a complete IncidentCase")
    public IncidentCase buildIncidentCase(
            IncidentSignal signal, IncidentAssessment assessment,
            AllAffectedImplants affected, RootCauseHypothesis hypothesis,
            ContainmentPlan plan) {
        return new IncidentCase(UUID.randomUUID().toString(), Instant.now(),
            signal, assessment, affected.implants(), hypothesis, plan);
    }

    private static RiskLevel classifyRisk(...) { /* 纯代码逻辑 */ }
    private static EstimatedBlastRadius estimateRadius(...) { /* 纯代码逻辑 */ }
}
```

**运行结果**：输入一句自然语言 → 6 步多 Action 编排 → 输出完整的有结构的事故报告（JSON）。

### 11.3 Blog Writer Agent（博客写作 + 审阅）

来自 Dan Vega 教程，展示 **Persona + 角色化 LLM** 模式：

```java
@Agent(description = "Write and review a blog post about a given topic")
public class BlogWriterAgent {

    private final BlogAgentProperties properties;

    public BlogWriterAgent(BlogAgentProperties properties) {
        this.properties = properties;
    }

    @Action(description = "Write a first draft of the blog post")
    public BlogDraft writeDraft(UserInput userInput, Ai ai) {
        return ai.withDefaultLlm()
            .withId("blog-post-draft-writer")
            .withPromptContributor(Personas.WRITER)
            .creating(BlogDraft.class)
            .fromPrompt("""Write a blog post about %s.
                Keep it practical and beginner-friendly.
                Use short sentences and plain language.
                """.formatted(userInput.getContent()));
    }

    @Action(description = "Review and improve the draft")
    @AchievesGoal(description = "A reviewed and polished blog post")
    public ReviewedPost reviewDraft(BlogDraft draft, Ai ai) {
        return ai.withLlmByRole("reviewer")    // 使用更强模型
            .withId("blog-post-reviewer")
            .creating(ReviewedPost.class)
            .fromPrompt("""
                Review and improve this blog post:
                Title: %s
                Content: %s
                Fix any technical errors. Tighten the writing.
                Provide a revised title, content, and feedback summary.
                """.formatted(draft.title(), draft.content()));
    }
}
```

---

## 12. 生态与资源

### 官方资源

| 资源 | 链接 |
|------|------|
| GitHub 主仓库 | https://github.com/embabel/embabel-agent |
| 在线文档 | https://docs.embabel.com/embabel-agent/guide/0.1.2-SNAPSHOT/ |
| Java 模板 | https://github.com/embabel/java-agent-template |
| Kotlin 模板 | https://github.com/embabel/kotlin-agent-template |
| 示例代码 | https://github.com/embabel/embabel-agent-examples |
| Travel Planner 示例 | https://github.com/embabel/tripper |
| Coding Agent 示例 | https://github.com/embabel/embabel-coding-agent |
| DeepWiki 源码解析 | https://deepwiki.com/embabel/embabel-agent |
| Discord 社区 | https://discord.gg/t6bjkyj93q |

### 教程与文章

| 资源 | 链接 | 作者 |
|------|------|------|
| Build AI Agents in Java with Embabel | https://bell-sw.com/blog/build-ai-agents-in-java-with-embabel-step-by-step-guide/ | BellSoft |
| Creating an AI Agent in Java Using Embabel | https://www.baeldung.com/java-embabel-agent-framework | Baeldung |
| Embabel First Look | https://www.danvega.dev/blog/2026/04/02/embabel-first-look | Dan Vega |
| Introducing Embabel (InfoQ) | https://www.infoq.com/news/2025/06/introducing-embabel-ai-agent/ | InfoQ |

### Maven 依赖坐标

```
Group: com.embabel.agent
Artifacts:
  - embabel-agent-bom (BOM)
  - embabel-agent-starter
  - embabel-agent-starter-shell
  - embabel-agent-starter-ollama
  - embabel-agent-openai-autoconfigure
  - embabel-agent-deepseek-autoconfigure
  - embabel-agent-api
```

### 版本

| 组件 | 当前版本 | 说明 |
|------|---------|------|
| Embabel Agent | 0.3.4 - 0.4.0-SNAPSHOT | 积极迭代中，API 可能变化 |
| Spring AI | 1.1.4 | Embabel 依赖版本 |
| Spring Boot | 3.5.x | Embabel 暂不支持 Boot 4.x |
| License | Apache 2.0 | |

---

## 总结：什么时候用 Embabel？

| 场景 | 推荐使用 | 原因 |
|------|---------|------|
| 简单 LLM 调用 | ❌ 直接用 Spring AI / OpenAI SDK | 不需要编排 |
| 复杂多步骤流程 | ✅ Embabel | GOAP 自动规划 |
| 现有 Spring 项目要加 AI 能力 | ✅ Embabel | 无缝集成 |
| 需要强类型 + 可测试性 | ✅ Embabel | 核心优势 |
| 企业级 Agent + 事务 + 持久化 | ✅ Embabel | Spring 生态加成 |
| Python AI 团队 | ⚠️ 考虑 LangChain Python | 生态不同 |

---

> **文章信息**  
> - 原文：[Build AI Agents in Java with Embabel: Step-by-Step Guide](https://bell-sw.com/blog/build-ai-agents-in-java-with-embabel-step-by-step-guide/) — BellSoft, 2026  
> - 补充：[Embabel First Look: Building Agentic Flows on the JVM](https://www.danvega.dev/blog/2026/04/02/embabel-first-look) — Dan Vega, Apr 2026  
> - 补充：[Introducing Embabel: Advanced AI Agent Development for Java Applications](https://www.infoq.com/news/2025/06/introducing-embabel-ai-agent/) — InfoQ, Jun 2025  
> - 主仓库：[embabel/embabel-agent](https://github.com/embabel/embabel-agent)  
> - 作者：Rod Johnson（Spring 创始人）  
> - 分类：`knowledges/ai-tools/agents/`
