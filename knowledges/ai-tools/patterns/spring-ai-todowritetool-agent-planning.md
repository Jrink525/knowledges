# Spring AI TodoWriteTool：AI 智能体任务规划与进度追踪实战

> **来源：** [Spring Boot 实战案例锦集 · 微信公众号](https://mp.weixin.qq.com/s/LDr4vqbAoAIu0llrnSAe0Q)  
> **整理 & 增强：** 2026-05-23

---

## 一、背景：为什么需要任务规划工具？

大语言模型普遍存在**中途失忆**问题——在长上下文任务中会遗忘关键步骤。当 AI 智能体同时处理文件编辑、测试运行和文档更新等多项工作时，重要步骤常被悄无声息地遗漏。

**TodoWriteTool** 是受 Claude Code 的 TodoWrite 功能启发、为 Spring AI 生态打造的结构化任务规划工具。它让 LLM 能够在执行过程中创建、跟踪、更新任务清单，把隐性的任务规划转化为显性化、可追踪的工作流程。

**核心价值：**
- 智能体绝不跳步——顺序执行，强制专注
- 工作流可实时监控——进度可视化
- 复杂的多步骤任务可拆解为原子步骤

---

## 二、原理解析：TodoWriteTool 的核心机制

### 2.1 工作流程

```
用户下发复杂指令
    ↓
LLM 调用 TodoWriteTool 拆解任务（创建待办列表）
    ↓
同一时间只有一个任务处于 "进行中" 状态
    ↓
每完成一步，LLM 更新任务状态
    ↓
全部完成 → LLM 汇总最终结果
```

### 2.2 任务生命周期

每条待办任务遵循简单的生命周期：

```
pending（待处理） → in_progress（执行中） → completed（已完成）
                                 ↕ (可选回退)
                            blocked（阻塞）
```

**关键约束：** 同一时间只能有一个任务处于 `in_progress` 状态——这一规则强制任务按顺序、专注执行，而非分散精力并行乱做。

### 2.3 进度展示效果

```
Progress: 2/4 tasks completed (50%)
[✓] 找出周星驰评分最高的 6 部电影
[✓] 将电影两两分组
[→] 将片名倒序拼写输出
[ ] 汇总最终结果
```

---

## 三、实战：TodoWriteTool 集成指南

### 3.1 环境准备

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-model-openai</artifactId>
</dependency>
<dependency>
    <groupId>org.springaicommunity</groupId>
    <artifactId>spring-ai-agent-utils</artifactId>
</dependency>
```

配置：

```yaml
spring:
  ai:
    openai:
      api-key: ${API_KEY}
      base-url: ${BASE_URL}
      chat:
        model: deepseek-v4-flash  # 兼容 OpenAI API 的任意模型
```

### 3.2 配置 Agent

```java
@RestController
@RequestMapping("/ai/task")
public class AiTaskController {

    private final ChatClient chatClient;

    public AiTaskController(ChatClient.Builder builder, ApplicationContext context) {
        this.chatClient = builder
            .defaultTools(TodoWriteTool.builder()
                .todoEventHandler(event ->
                    context.publishEvent(new TodoUpdateEvent(this, event.todos())))
                .build())
            .defaultAdvisors(
                ToolCallAdvisor.builder()
                    .conversationHistoryEnabled(false)
                    .build(),
                MessageChatMemoryAdvisor.builder(
                    MessageWindowChatMemory.builder()
                        .maxMessages(500).build())
                    .build())
            .build();
    }

    @GetMapping("/execute")
    public String execute() {
        String response = chatClient.prompt()
            .user("找出周星驰评分最高的 6 部电影，将它们两两分组，"
                + "并把每部电影的片名倒序拼写输出。"
                + "使用 TodoWrite 来梳理、规划你的执行任务。")
            .advisors(a -> a.param(ChatMemory.CONVERSATION_ID, "C-0001"))
            .call()
            .content();
        return response;
    }
}
```

> ⚠️ 重要：`conversationHistoryEnabled(false)` 关闭内置的工具调用历史记录，转而使用 `MessageChatMemoryAdvisor` 来维护会话上下文。

### 3.3 基于事件的进度监测

```java
@Component
public class TodoProgressListener {

    @EventListener
    public void onTodoUpdate(TodoUpdateEvent event) {
        System.err.println(event.getTodos());

        int completed = (int) event.getTodos().stream()
            .filter(t -> t.status() == Todos.Status.completed)
            .count();
        int total = event.getTodos().size();

        System.out.printf("\nProgress: %d/%d tasks completed (%.0f%%)\n",
            completed, total, (completed * 100.0 / total));
    }
}
```

事件对象：

```java
public class TodoUpdateEvent extends ApplicationEvent {
    private final List<TodoItem> todos;

    public TodoUpdateEvent(Object source, List<TodoItem> todos) {
        super(source);
        this.todos = todos;
    }

    public List<TodoItem> getTodos() { return todos; }
}
```

### 3.4 效果验证

当请求被处理后，控制台输出类似如下：

```
创建了3个待办任务，按顺序执行...
[✓] 找出周星驰评分最高的 6 部电影
[✓] 将电影两两分组
[✓] 将片名倒序拼写输出
最终结果已生成
```

---

## 四、补充案例：5 个类似增强模式

> 以下案例均来自 Spring AI 社区和业界最佳实践，可作为 TodoWriteTool 的互补方案。

---

### 案例一：Agent Skills 模块化技能体系

**来源：** [Spring AI Agentic Patterns (Part 1): Agent Skills](https://spring.io/blog/2026/01/13/spring-ai-generic-agent-skills/) — Spring 官方博客

**问题：** 传统 Agent 的领域知识硬编码在提示词中，难以复用和维护。

**方案：** Agent Skills 将能力打包为 Markdown 文件（含 YAML 前置元数据），按需发现和加载：

```
my-skill/
├── SKILL.md          # 必需：指令 + 元数据
├── scripts/          # 可选：可执行脚本
├── references/       # 可选：参考文档
└── assets/           # 可选：模板、资源
```

**核心设计——渐进式上下文加载：**
1. **发现阶段** — 启动时只加载技能名称和描述（轻量注册表）
2. **激活阶段** — 任务匹配时，读取完整 SKILL.md
3. **执行阶段** — 按指令执行，按需加载参考文件

**与 TodoWriteTool 的关系：** Skills 解决"怎么执行"，TodoWriteTool 解决"怎么规划"。两者结合效果最佳。

```java
ChatClient chatClient = chatClientBuilder
    .defaultToolCallbacks(SkillsTool.builder()
        .addSkillsDirectory(".claude/skills")
        .build())
    .defaultTools(FileSystemTools.builder().build())
    .defaultTools(ShellTools.builder().build())
    .build();
```

**亮点：** LLM 无关——定义一次技能，可在 OpenAI、Anthropic、Google Gemini 间自由切换。

---

### 案例二：TaskTool 子智能体编排

**来源：** [Spring AI Agentic Patterns (Part 4): Subagent Orchestration](https://spring.io/blog/2026/01/27/spring-ai-agentic-patterns-4-task-subagents/) — Spring 官方博客

**问题：** 一个 Agent 处理所有事情导致上下文窗口膨胀、专业能力不足。

**方案：** 采用**层级式子 Agent 架构**——主 Agent 通过 Task 工具将任务委托给专业子 Agent，每个子 Agent 拥有独立的上下文窗口。

**内置 4 种子 Agent：**

| 子 Agent | 用途 | 工具 |
|---------|------|------|
| Explore | 快速只读代码探索 | Read, Grep, Glob |
| General-Purpose | 多步研究与执行 | 所有工具 |
| Plan | 软件架构设计 | 只读 + 搜索 |
| Bash | 命令执行（git/构建） | Bash 仅 |

**多模型路由：** 简单任务走廉价模型，复杂分析走强模型：

```java
var taskTools = TaskToolCallbackProvider.builder()
    .chatClientBuilder("default", sonnetBuilder)  // 默认
    .chatClientBuilder("haiku", haikuBuilder)      // 快速便宜
    .chatClientBuilder("opus", opusBuilder)        // 复杂分析
    .build();
```

**与 TodoWriteTool 的关系：** TodoWriteTool 管控"任务步骤"；TaskTool 管控"子 Agent 分工"。主 Agent 用 TodoWriteTool 规划，遇到专业领域任务则用 TaskTool 委派。

---

### 案例三：Tool Argument Augmenter 可解释 Agent

**来源：** [Explainable AI Agents: Capture LLM Tool Call Reasoning with Spring AI](https://spring.io/blog/2025/12/23/spring-ai-tool-argument-augmenter-tzolov/) — Spring 官方博客

**问题：** Agent 调用工具时，开发者只知道"调用了什么工具"，不知道"为什么调用"。

**方案：** 在工具 JSON Schema 中动态注入额外字段（如 `innerThought`、`confidence`、`memoryNotes`），捕获 LLM 的推理过程。

```java
// 定义扩展参数
public record AgentThinking(
    @ToolParam(description = "为什么调用此工具的逐步推理", required = true)
    String innerThought,
    @ToolParam(description = "置信度 (low/medium/high)")
    String confidence,
    @ToolParam(description = "需要记住的关键信息")
    List<String> memoryNotes
) {}

// 包装现有工具
AugmentedToolCallbackProvider<AgentThinking> provider =
    AugmentedToolCallbackProvider.<AgentThinking>builder()
        .toolObject(new WeatherTool())
        .argumentType(AgentThinking.class)
        .argumentConsumer(event -> {
            AgentThinking thinking = event.arguments();
            log.info("工具: {}, 推理: {}", 
                event.toolDefinition().name(), thinking.innerThought());
            // 将推理存入长期记忆
            thinking.memoryNotes().forEach(memorySystem::store);
        })
        .build();
```

**LLM 看到的增强 Schema：**

```json
{
  "type": "object",
  "properties": {
    "location": { "type": "string", "description": "查询位置" },
    "innerThought": { "type": "string", "description": "逐步推理" },
    "confidence": { "type": "string" },
    "memoryNotes": { "type": "array", "items": { "type": "string" } }
  },
  "required": ["location", "innerThought", "memoryNotes"]
}
```

**与 TodoWriteTool 的关系：** TodoWriteTool 让用户看到"做什么"；Tool Argument Augmenter 让开发者看到"为什么这么做"。两者结合实现**全栈可观测**。

---

### 案例四：事务性多 Agent 工作流（Temporal + Saga 模式）

**来源：** [Stop Letting AI Agents Break Your Database: Transactional Multi-Agent Workflows](https://dev.to/machinecodingmaster/stop-letting-ai-agents-break-your-database-transactional-multi-agent-workflows-with-temporal-and-47dc) — Dev.to

**问题：** Agent 调用的多个工具步骤中，第二步失败后第一步已提交，数据库进入不一致状态。普通 `@Transactional` 无法应对异步、非阻塞的 LLM API 调用。

**方案：** 使用 **Temporal Durable Execution + Saga 模式** 编排 Agent 事务：

1. **解耦大脑与状态** — Spring AI 负责非确定性推理和工具路由，Temporal 负责执行状态
2. **立即注册补偿** — 每个成功的工具执行立刻注册补偿动作
3. **隔离 LLM 调用** — 将 Spring AI 调用封装在 Temporal Activity 中

```java
@WorkflowMethod
public void executeAgenticBooking(String userPrompt) {
    Saga saga = new Saga(new Saga.Options.Builder().build());
    try {
        // Spring AI 解析用户意图，决策工具执行路径
        AgentDecision decision = aiActivities.consultLLM(userPrompt);

        bookingActivities.chargeCard(decision.getAmount());
        saga.addCompensation(bookingActivities::refundCard, decision.getAmount());

        bookingActivities.reserveSeat(decision.getSeatId());
        saga.addCompensation(bookingActivities::releaseSeat, decision.getSeatId());
    } catch (ActivityFailure e) {
        saga.compensate(); // 保证性、持久的跨服务回滚
        throw e;
    }
}
```

**核心原则：**
- **永远不要信任 Agent** — 假设 LLM 第 3 步就会幻视错误的工具参数
- **确定性编排** — 工作流引擎必须 100% 确定性，LLM 的不确定性隔离在 Activity 中
- Spring AI 负责**将提示词映射为 Java POJO**，Temporal 负责**执行状态**

---

### 案例五：Orchestrator-Workers 动态任务分解

**来源：** [Spring AI Orchestrator-Workers Workflow Pattern](https://github.com/BootcampToProd/spring-ai-orchestrator-workers-workflow) — GitHub (BootcampToProd)

**问题：** 复杂任务需要并行执行多个子任务，但子任务的划分不固定，无法使用静态工作流。

**方案：** Orchestrator（编排器）动态分析任务 → 分解为子任务 → 分配给 Workers 并行执行 → 汇总结果。

```
用户需求："分析这篇论文核心论点"
    ↓
Orchestrator LLM（分解）
    ├── Worker A: "提取论文摘要与方法"
    ├── Worker B: "分析实验结果"
    └── Worker C: "评估贡献与局限"
    ↓
合并结果 → 最终报告
```

**与 TodoWriteTool 的区别：**
- TodoWriteTool：**顺序执行**，适合有依赖关系的步骤
- Orchestrator-Workers：**并行执行**，适合可并行的独立子任务
- 两者可组合：先 Orchestrator 分解出独立子任务，各子任务内部用 TodoWriteTool 规划步骤

```java
public class OrchestratorWorkersPattern {
    private final ChatClient orchestrator;
    private final List<ChatClient> workers;

    public String execute(String task) {
        // Step 1: Orchestrator 分解任务
        TaskPlan plan = orchestrator.prompt()
            .user("分解以下任务为可并行执行的子任务: " + task)
            .call()
            .entity(TaskPlan.class);

        // Step 2: Workers 并行执行
        List<CompletableFuture<WorkerResult>> futures = plan.subtasks()
            .stream()
            .map(sub -> CompletableFuture.supplyAsync(() -> 
                executeWorker(sub)))
            .toList();

        List<WorkerResult> results = futures.stream()
            .map(CompletableFuture::join)
            .toList();

        // Step 3: 汇总结果
        return synthesizer.synthesize(results);
    }
}
```

---

## 五、模式对比与选型指南

| 模式 | 核心能力 | 适用场景 | 执行模型 | 依赖 |
|------|---------|---------|---------|------|
| **TodoWriteTool** | 任务规划 + 进度追踪 | 多步骤编码、复杂查询 | 顺序执行 | spring-ai-agent-utils |
| **Agent Skills** | 模块化领域知识 | 代码审查、文档生成 | 按需加载 | spring-ai-agent-utils |
| **TaskTool** | 子 Agent 委派 | 专业领域隔离、多模型路由 | 层次委派 | spring-ai-agent-utils |
| **Tool Argument Augmenter** | 推理过程捕获 | 可观测性、记忆系统 | 透明增强 | Spring AI 核心 |
| **Temporal + Saga** | 事务性保证 | 金融交易、订单系统 | 分布式编排 | Temporal SDK |
| **Orchestrator-Workers** | 动态并行分解 | 数据分析、研究综述 | 并行执行 | Spring AI + 线程池 |

### 组合策略

```
简单任务：TodoWriteTool ← 规划 + 执行
   ↓
需要领域知识：TodoWriteTool + Agent Skills
   ↓
需要专业子任务：TodoWriteTool + TaskTool（委派子Agent）
   ↓
需要可观测：TodoWriteTool + Tool Argument Augmenter
   ↓
需要事务保证：TodoWriteTool + Temporal Saga
   ↓
需要并行：Orchestrator-Workers（并行分解）+ TodoWriteTool（各子任务内规划）
```

---

## 六、关联阅读

- [Spring AI Agent Utils 官方文档](https://github.com/spring-ai-community/spring-ai-agent-utils)
- [Spring AI Agentic Patterns 系列](https://spring.io/blog/2026/01/13/spring-ai-generic-agent-skills)
- [Building Effective Agents with Spring AI — Baeldung](https://www.baeldung.com/spring-ai-building-effective-agents)
- [Claude Code 原生 TodoWrite 参考](https://code.claude.com/docs/en/overview)
- [Agent Skills 规范](https://agentskills.io/specification)

---

*基于微信公众号「Spring Boot 实战案例锦集」文章整理，结合 Spring AI 社区官方博客、Dev.to 及 Spring 官方示例增强*
