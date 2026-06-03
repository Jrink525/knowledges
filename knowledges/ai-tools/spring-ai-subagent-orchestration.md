---
title: Spring AI Subagent Orchestration — Task Tool 与层次化 Agent 架构
source:
  - "https://www.baeldung.com/spring-ai-subagent-orchestration"
  - "https://spring.io/blog/2026/01/27/spring-ai-agentic-patterns-4-task-subagents/"
  - "https://medium.com/codex/sub-agent-orchestration-with-spring-ai-b9262d9563fb"
  - "https://github.com/spring-ai-community/spring-ai-agent-utils"
read_at: 2026-06-01
category: ai-agents
tags: [spring-ai, subagent, orchestration, task-tool, agent-architecture, java, baeldung]
---

# Spring AI Subagent Orchestration — Task Tool 与层次化 Agent 架构

> 本文综合 Spring 官方博客、Medium 实践文章及 GitHub 源码，完整梳理 Spring AI 的子 Agent 编排机制：如何用 Task Tool 构建层次化 Agent 系统，实现上下文隔离、多模型路由与并行执行。

---

## 1. 核心思想

**不再让一个全能 Agent 包办一切**，而是由主 Agent（Orchestrator）根据任务需求，将工作委托给专门的子 Agent（Subagent）。每个子 Agent 在**独立的上下文窗口**中运行，只向主 Agent 返回关键结果。

> 不同于传统的服务编排（硬编码调用链），子 Agent 编排的委托决策由 LLM 自己根据自然语言描述决定 — 系统更灵活、自适应。

为什么有效：
- **上下文隔离** — 子 Agent 不继承主对话的膨胀历史，防止性能退化
- **多模型路由** — 简单任务用廉价模型，复杂分析用高能力模型
- **模块化** — 每个 Agent 单一职责，易于添加、修改或替换
- **并行执行** — 多个子 Agent 可并发运行
- **可测试** — 每个子 Agent 独立验证

---

## 2. 架构组件

### 2.1 三层架构

```
用户
  ↓
┌─────────────────────────────┐
│  主 Agent (Orchestrator)    │  ← 主 LLM + Task Tool
│  - 与用户交互               │
│  - 决定何时委托             │
│  - 合成最终回答             │
└──────────┬──────────────────┘
           │ Task 工具调用
     ┌─────┴─────┐
     ▼           ▼
┌─────────┐ ┌─────────┐
│ Subagent│ │ Subagent│  ← 各司其职，独立上下文
│  A      │ │  B      │     可路由到不同 LLM
└─────────┘ └─────────┘
```

### 2.2 执行流程

1. **启动加载** — TaskTool 加载子 Agent 配置文件，填充 Agent Registry（名称 + 描述目录）
2. **用户提问** — 用户向主 Agent 发问
3. **LLM 评估** — 主 LLM 评估请求，检查 Registry 中可用的子 Agent
4. **决定委托** — LLM 调用 `Task` 工具，指定子 Agent 名称和任务描述
5. **启动子 Agent** — TaskTool 根据配置生成对应的子 Agent 实例
6. **独立执行** — 子 Agent 在专用上下文窗口中自主工作
7. **返回结果** — 只返回关键发现，不返回中间步骤
8. **主 Agent 合成** — 主 Agent 整合结果后返回给用户

### 2.3 关键组件

| 组件 | 说明 |
|------|------|
| **TaskTool** | Spring AI 工具，主 Agent 通过它调用子 Agent |
| **Agent Registry** | 注册表，保存所有可用子 Agent 的名称和描述 |
| **Agent 配置文件** | Markdown 文件（含 YAML frontmatter），定义子 Agent |
| **ChatClient Builder** | 用于为不同子 Agent 配置不同的 LLM |

---

## 3. 内置子 Agent

Spring AI Agent Utils 提供四个内置子 Agent，配置 `TaskTool` 后自动注册：

| 子 Agent | 用途 | 可用工具 |
|----------|------|---------|
| **Explore** | 快速的只读代码库探索 — 查找文件、搜索代码、分析内容 | Read, Grep, Glob |
| **General-Purpose** | 多步研究与执行，具有完全读写权限 | 所有工具 |
| **Plan** | 软件架构师 — 设计实现策略、识别权衡 | 只读 + 搜索 |
| **Bash** | 命令执行专家 — git 操作、构建、终端任务 | Bash 仅 |

多个子 Agent 可并发执行，例如 code review 时同时运行 `style-checker`、`security-scanner` 和 `test-coverage`。

---

## 4. 快速开始

### 4.1 添加依赖（Spring Boot + OpenAI）

```xml
<dependencies>
    <!-- Spring Boot -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
    <!-- Spring AI OpenAI Starter -->
    <dependency>
        <groupId>org.springframework.ai</groupId>
        <artifactId>spring-ai-starter-model-openai</artifactId>
        <version>2.0.0-M5</version>
    </dependency>
    <!-- Agent Utils -->
    <dependency>
        <groupId>org.springaicommunity</groupId>
        <artifactId>spring-ai-agent-utils</artifactId>
        <version>0.4.2</version>
    </dependency>
</dependencies>
```

### 4.2 配置 application.properties

```properties
spring.ai.openai.api-key=${OPENAI_API_KEY}
spring.ai.openai.chat.options.model=gpt-4.1-mini
spring.application.name=spring-ai-subagent
agent.tasks.paths=classpath:/agents/*.md
```

`agent.tasks.paths` 指向子 Agent 定义文件路径（src/main/resources/agents/），Spring AI 启动时自动加载。

### 4.3 配置主 Orchestrator Agent

```java
import org.springaicommunity.agent.tools.task.TaskToolCallbackProvider;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;

@Configuration
public class AgentConfig {

    @Value("${agent.tasks.paths}")
    private List<Resource> agentPaths;

    @Bean
    CommandLineRunner demo(ChatClient.Builder chatClientBuilder) {
        return args -> {
            // 加载子 Agent 定义 + 构建 TaskTool
            var claudeType = ClaudeSubagentType.builder()
                .chatClientBuilder("default", chatClientBuilder.clone())
                .build();

            var taskTool = TaskTool.builder()
                .subagentReferences(ClaudeSubagentReferences.fromResources(agentPaths))
                .subagentTypes(claudeType)
                .build();

            // 构建主 ChatClient，注入 Task 工具
            ChatClient chatClient = chatClientBuilder
                .defaultToolCallbacks(taskTool)
                .build();

            // 使用 — Agent 自动决定何时委托给子 Agent
            String response = chatClient
                .prompt("Review the authentication module code and generate documentation")
                .call()
                .content();
        };
    }
}
```

### 4.4 多模型路由（可选）

```java
var taskTools = TaskToolCallbackProvider.builder()
    .chatClientBuilder("default", sonnetBuilder)   // 默认模型
    .chatClientBuilder("haiku", haikuBuilder)      // 快速、便宜
    .chatClientBuilder("opus", opusBuilder)        // 复杂分析
    .build();
```

子 Agent 在其定义文件中指定 `model` 字段，TaskTool 自动路由到对应模型。

---

## 5. 创建自定义子 Agent

### 5.1 文件结构

子 Agent 定义文件存放在 `src/main/resources/agents/`（或自定义目录，通过 `agent.tasks.paths` 指定）：

```
project-root/
└── src/main/resources/
    └── agents/
        ├── code-reviewer.md
        └── documentation-writer.md
```

### 5.2 文件格式与完整示例

**Code Reviewer：审查代码质量**

```markdown
---
name: code-reviewer
description: >
  Expert code reviewer. Use proactively after writing or modifying code
  to surface quality, security, and readability issues.
tools: Read, Grep, Glob
disallowedTools: Edit, Write
model: sonnet
---

You are a senior code reviewer with expertise in software quality.

**When Invoked:**
1. Run `git diff` to identify recent changes
2. Inspect the modified files and surrounding context
3. Check for issues in the areas listed below

**Review Checklist:**
- Code clarity and readability
- Proper naming conventions
- Error handling and edge cases
- Security vulnerabilities

**Output:** Clear, actionable feedback organized by file, with line references.
```

**Documentation Writer：生成技术文档**

```markdown
---
name: documentation-writer
description: >
  Technical documentation specialist for architecture explanations,
  workflow summaries, and concise developer-facing docs.
model: default
---

You are a senior technical documentation specialist.

Your responsibilities:
- Generate concise technical documentation
- Explain Spring Boot and Java application architecture
- Summarize workflows clearly
- Produce developer-friendly explanations
- Keep documentation simple and technically accurate
```

### 5.3 配置字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 是 | 唯一标识（小写 + 连字符） |
| `description` | 是 | 自然语言描述何时使用该子 Agent（影响 LLM 的委托决策） |
| `tools` | 否 | 允许的工具列表（不填则继承主 Agent 的所有工具） |
| `disallowedTools` | 否 | 明确禁用的工具 |
| `model` | 否 | 模型偏好：`haiku`、`sonnet`、`opus` 或 `default` |

> **重要限制**：子 Agent 不能生成自己的子 Agent。不要在子 Agent 的 `tools` 列表中包含 `Task`。

### 5.4 加载自定义子 Agent

```java
import org.springaicommunity.agent.tools.task.subagent.claude.ClaudeSubagentReferences;

// 从目录加载
var taskTools = TaskToolCallbackProvider.builder()
    .chatClientBuilder("default", chatClientBuilder)
    .subagentReferences(
        ClaudeSubagentReferences.fromRootDirectory("src/main/resources/agents")
    )
    .build();

// 或从 Resource 列表加载（配合 classpath:* 路径）
var references = ClaudeSubagentReferences.fromResources(agentPaths);
```

---

## 6. 实践模式：Architect-Builder

一个强大的子 Agent 模式：**架构师-建造者**。

| 角色 | 模型 | 职责 |
|------|------|------|
| **Architect** | 昂贵推理模型 | 分析数据、提取事实、创建结构化蓝图 |
| **Builder** | 便宜快速模型 | 从蓝图生成最终输出（精炼的散文/代码） |

**为什么有效**：
- Architect 只输出结构化数据，不产生幻觉
- Builder 被锁定在 Architect 的蓝图中，也无法产生幻觉
- 假设需要 2000 推理 token + 1500 输出 token，将生成工作移到便宜模型可节省 **70% 成本**

---

## 7. 后台执行（Background Tasks）

长时间运行的子 Agent 可以**异步执行** — 主 Agent 继续工作，子 Agent 在后台运行。通过 `TaskOutputTool` 在需要时检索结果。

适用于：
- 长文档分析
- 代码审查
- 数据爬取

---

## 8. 权衡与选择

### 编排式 vs 直接调用

| 维度 | 编排式（Task Tool） | 直接调用（编程式） |
|------|-------------------|-------------------|
| **决策者** | LLM 决定调用哪个子 Agent | 开发人员硬编码调用链 |
| **上下文隔离** | ✓ 独立上下文窗口 | ✓ 独立上下文窗口 |
| **token 开销** | 有（TaskTool 描述 + 对话历史） | 少 |
| **灵活性** | 高 — 动态选择 | 低 — 固定流水线 |
| **适用场景** | 用户聊天、多步条件分支 | 固定流水线、极致 token 效率 |

### 何时使用子 Agent 模式

**适合**：
- 需要多个专业技能的任务
- 通过模型路由优化成本
- 需要条件分支的复杂工作流

**不适合**：
- 简单单步任务
- 输出极少的场景
- 延迟敏感场景（子 Agent 调用增加往返次数）

---

## 9. 与 Claude Code Subagents 的关系

Spring AI 的 Task Tool 受 [Claude Code's Subagents](https://platform.claude.com/docs/en/agent-sdk/subagents) 启发，但做了关键扩展：

| 特性 | Claude Code Subagents | Spring AI Task Tool |
|------|----------------------|-------------------|
| 格式 | 兼容 Markdown+YAML | 兼容 Markdown+YAML |
| 模型路由 | 有限 | 多模型支持（haiku/sonnet/opus 等） |
| 协议扩展 | 仅支持 Claude 格式 | 可扩展支持 A2A、MCP 等其他 Agent 协议 |
| 持久化 | 无 | TaskRepository 支持持久化任务存储 |

> Spring AI 的 Subagent Extension Framework（即将发布）将提供协议无关的抽象，实现 A2A、MCP 或自定义协议的远程 Agent 编排。

---

## 10. 集成测试

AI 编排工作流也应当像常规组件一样测试。

### 10.1 子 Agent 加载测试

```java
@Test
void givenSubagentDefinitions_whenLoadingSubagents_thenReferencesAreCreated() {
    var references = ClaudeSubagentReferences.fromResources(agentPaths);
    assertThat(references).isNotNull();
}
```

### 10.2 编排响应测试

```java
@Test
void givenPrompt_whenExecutingOrchestration_thenResponseIsGenerated() {
    List<Resource> agentResources = List.of(
        new ClassPathResource("agents/test-agent.md")
    );

    SubagentType claudeType = ClaudeSubagentType.builder()
        .chatClientBuilder("default", chatClientBuilder.clone())
        .build();

    ToolCallback taskTool = TaskTool.builder()
        .subagentReferences(ClaudeSubagentReferences.fromResources(agentResources))
        .subagentTypes(claudeType)
        .build();

    ChatClient chatClient = chatClientBuilder.clone()
        .defaultToolCallbacks(taskTool)
        .build();

    String result = chatClient
        .prompt("Explain how the authentication module works.")
        .call()
        .content();

    assertThat(result).isNotBlank();
    assertThat(result).contains("authentication");
}
```

> 单元测试中应 mock 模型层，仅验证编排行为。

---

## 11. 参考资料

- [Spring AI Agentic Patterns (Part 4): Subagent Orchestration](https://spring.io/blog/2026/01/27/spring-ai-agentic-patterns-4-task-subagents/) — 官方博客
- [spring-ai-agent-utils GitHub 仓库](https://github.com/spring-ai-community/spring-ai-agent-utils)
- [TaskTools 参考文档](https://github.com/spring-ai-community/spring-ai-agent-utils/blob/main/spring-ai-agent-utils/docs/TaskTools.md)
- [subagent-demo 示例项目](https://github.com/spring-ai-community/spring-ai-agent-utils/tree/main/examples/subagent-demo)
- [Medium: Sub-Agent Orchestration with Spring AI](https://medium.com/codex/sub-agent-orchestration-with-spring-ai-b9262d9563fb) — 实践帖子
- [Baeldung: Guide to Subagent Orchestration in Spring AI](https://www.baeldung.com/spring-ai-subagent-orchestration) — 完整实践教程
- [Spring AI Agentic Patterns 系列](https://spring.io/blog/2026/01/13/spring-ai-generic-agent-skills) — Part 1-5
- [A2A Integration (Part 5)](https://spring.io/blog/2026/01/29/spring-ai-agentic-patterns-a2a-integration)
- [Baeldung 示例代码 (GitHub)](https://github.com/eugenp/tutorials/tree/master/spring-ai-modules/spring-ai-subagent-orchestrator)
