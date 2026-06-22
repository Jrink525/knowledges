# LLM 理解 + 训练 + Agent 实践学习路径

> 目标：
> 1. 理解大模型原理与边界
> 2. 能在 Google Colab 上微调一个 2-4B 模型
> 3. 能用 Spring AI、Claude Agent SDK、LangGraph 等框架搭 Agent（自动编码、投研等）

---

## 课程资源（由浅入深）

### 第一层：打好基础（2-3 周）

| 资源 | 主要学什么 |
|------|-----------|
| [Fast.ai Practical Deep Learning](https://course.fast.ai/) | 先上手再理论，Top-down 教学，适合有工程背景的人 |
| [Andrej Karpathy: Let's build GPT from scratch](https://www.youtube.com/watch?v=kCc8FmEb1nY) | 2 小时视频，~200 行 Python 写一个 GPT。看完对 Transformer 理解比读十篇论文都深 |
| [Stanford CS224N](https://web.stanford.edu/class/cs224n/) (NLP with Deep Learning) | 看第 1-7 课（Word Vectors → Transformers），每课有 PyTorch 作业 |

**产出**：说清楚 Attention 是什么、Transformer 各组件作用、Tokenization 原理。

---

### 第二层：深入研究 LLM（3-4 周）

| 资源 | 说明 |
|------|------|
| [Stanford CS336](https://cs336.stanford.edu/) — Language Modeling from Scratch | 从 Common Crawl 洗数据 → 手写 FlashAttention → 训 RL。完成即超越 90% AI 工程师 |
| [Hugging Face NLP Course](https://huggingface.co/learn/nlp-course) | 实操：用 Transformers 库加载/微调模型，理解 tokenizer 和 pipeline |
| [nanoGPT](https://github.com/karpathy/nanoGPT) (Karpathy) | 300 行 PyTorch GPT 训练。Colab 就能跑 |

**产出**：自己写 mini-GPT，理解训练 loop、loss 曲线、模型在"记忆"和"泛化"之间的边界。

---

### 第三层：Colab 上微调 2-4B 模型

2-4B 参数在 Colab 单卡上训练 full params 不够，需要用 **PEFT (Parameter-Efficient Fine-Tuning)**：

| 资源 | 说明 |
|------|------|
| [Unsloth](https://github.com/unslothai/unsloth) | Colab 优化微调框架，2x 加速，显存减半。推荐入口 |
| [QLoRA 论文](https://arxiv.org/abs/2305.14314) | 4bit 量化 + LoRA，单卡 24GB 能微调 7-13B |
| [Axolotl](https://github.com/OpenAccess-AI-Collective/axolotl) | 更全的微调框架，多数据集支持 |
| [TRL](https://github.com/huggingface/trl) | RLHF / DPO / GRPO 对齐训练，对应 CS336 第 5 个作业 |

**推荐 2-4B 模型（适合 Colab）：**

| 模型 | 特点 |
|------|------|
| [Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B) | 最新，4K/32K context，代码好 |
| [Llama-3.2-3B](https://huggingface.co/meta-llama/Llama-3.2-3B) | Meta，生态最全 |
| [Gemma-3-4B](https://huggingface.co/google/gemma-3-4b-it) | Google，中文 OK |

**Colab 实操路线**：

```
1. Unsloth 加载 2B 模型 + 4bit 量化 → ~6GB 显存 ✅
2. 找开源数据集（OpenHermes/代码数据集）→ QLoRA 微调 → 1-2h ✅
3. TRL 做 DPO 对齐 → 让模型偏好的代码风格 ✅
4. 导出 → Ollama/vLLM 部署成 API ✅
```

**理解大模型的边界**：

- 推理局限：Chain-of-Thought 并非万能，幻觉无法彻底消除
- 知识边界：训练数据截止，无法自知"不知道"
- 上下文限制：长上下文性能显著退化（lost in the middle）
- Scaling Law 放缓：单纯增大规模收益边际递减

---

### 第四层：Agent 框架实战（Java + Agent 开发背景）

按上手难度排列：

| 框架 | 特点 | 适用场景 |
|------|------|---------|
| [Pi](https://pi.dev) | TypeScript 编码 Agent 框架。最小化 harness，15+ 模型供应商，树形会话历史，上下文工程（AGENTS.md/SYSTEM.md），4 种模式（交互/JSON/RPC/SDK） | TypeScript 生态。自动化编码、自定义 Agent |
| [Spring AI](https://docs.spring.io/spring-ai/reference/) | Java 生态，DI/Template 模式。支持 OpenAI、Ollama 等 | 已有 Spring 基础，1 小时上手 |
| [Claude Agent SDK](https://docs.anthropic.com/en/docs/agents-and-tools/claude-agent-sdk) | MCP + Tool-Use 原生支持 | 搭高级 Agent（投研、多步推理）|
| [LangGraph](https://langchain-ai.github.io/langgraph/) | 图状态机编排 Agent 多步流程 | 复杂工作流（投研流水线、自动 PR review）|

#### Spring AI 实战要点

| 模块 | 说明 |
|------|------|
| ChatClient | 统一聊天接口，切换模型只要改配置，支持流式/非流式 |
| Tool Calling | @Tool 注解注册 Java 方法为 AI 工具，自动生成 JSON Schema |
| Advisors | 拦截器链（QuestionAnswerAdvisor for RAG） |
| VectorStore | PGVector/Redis/Milvus/Chroma 做 RAG |
| MCP | 基于 Model Context Protocol 接入外部工具/数据源 |
| Function Calling | 直接调 Spring Bean 方法为 AI 工具 |
| Structured Output | BeanOutputConverter 将 LLM 输出转 Java 对象 |

**Demo 1：带 Tool 的 Agent（代码审查）**

```java
@SpringBootApplication
public class CodeReviewAgent {

    public static void main(String[] args) {
        SpringApplication.run(CodeReviewAgent.class, args);
    }

    @Bean
    ApplicationRunner demo(ChatClient.Builder builder) {
        return args -> {
            var client = builder.build();
            var response = client.prompt()
                .system("你是资深 Java 代码审查员，关注：代码规范、性能、安全")
                .user("Review this: """
                    public void process() {
                        List list = new ArrayList();
                        for (int i = 0; i < 100000; i++) {
                            list.add(data.get(i));
                        }
                    }
                    """)
                .call()
                .content();
            System.out.println(response);
        };
    }
}
```

**Demo 2：Spring AI + MCP（对接投研数据源）**

```java
// MCP 服务端定义
@Component
public class StockDataMcpServer {

    @Tool(description = "查询股票实时数据")
    public StockInfo getStockPrice(String symbol) {
        // 调外部 API 获取数据
        return stockApi.fetch(symbol);
    }

    @Tool(description = "获取公司财报摘要")
    public FinancialReport getFinancialReport(String companyCode, String quarter) {
        return database.query(companyCode, quarter);
    }
}

// 客户端调用
var response = client.prompt()
    .system("根据提供的工具，收集 {company} 最新财务数据并生成报告")
    .user("帮我查一下 NVDA 的最新股价和 Q2 财报")
    .call()
    .content();
```

**Demo 3：多步骤 Agent 工作流**

```java
@Service
public class ResearchAgent {
    private final ChatClient chatClient;

    public ResearchAgent(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }

    public String research(String company) {
        // Step 1: 收集信息
        String raw = chatClient.prompt()
            .user("收集 " + company + " 最近一周的新闻和动态")
            .call().content();

        // Step 2: 深度分析
        String analysis = chatClient.prompt()
            .user("基于以下信息，分析 " + company + " 的竞争优势和风险：\n" + raw)
            .call().content();

        // Step 3: 生成报告
        return chatClient.prompt()
            .user("根据分析，生成一份 " + company + " 的投资研究报告")
            .call().content();
    }
}
```

**Spring AI 主要资源：**

- [官方文档](https://docs.spring.io/spring-ai/reference/) — 最权威，场景全
- [GitHub: spring-ai](https://github.com/spring-projects/spring-ai) — 示例代码
- [Spring AI 最佳实践](https://www.baeldung.com/spring-ai) — Baeldung 教程系列
- [Spring AI + Ollama 本地部署](https://www.baeldung.com/spring-boot-ollama-local-ai) — 本地测试

---

#### Pi (pi.dev) 实战要点

> 官网：<https://pi.dev>  |  GitHub: <https://github.com/earendil-works/pi>  |  TypeScript 编码 Agent 框架

Pi 是一个最小化的 Agent harness，核心特色：

| 特性 | 说明 |
|------|------|
| 模型供应商 | Anthropic、OpenAI、Google、Azure、Bedrock、Mistral、Kimi、MiniMax、Ollama 等 **15+** |
| 上下文工程 | AGENTS.md / SYSTEM.md 加载，支持 compaction、skills、prompt templates |
| 会话历史 | **树形结构**，`/tree` 可在任意节点回退继续 |
| 四种模式 | 交互式 / Print/JSON / RPC / SDK，跨平台集成 |
| 扩展系统 | Extensions 可自定 compaction、RAG、长时记忆、消息过滤 |
| 共享能力 | 主题、扩展、skill 可打包为 npm 包分发 |

**Pi 的典型用法（SDK 模式嵌入应用）：**

```typescript
// SDK 模式：在 Node 应用中嵌入 Pi
import { createAgent } from 'pi-coding-agent';

const agent = createAgent({
  provider: 'anthropic',
  model: 'claude-sonnet-4-20250514',
  system: '你是一个代码审查助手，擅长 Java/TypeScript'
});

const result = await agent.run('审查以下代码的质量和安全性');
console.log(result.text);
```

**Pi 与 Spring AI 的差异：**

| 维度 | Pi | Spring AI |
|------|-----|-----------|
| 语言 | TypeScript | Java |
| 运行环境 | Node.js | JVM (Spring Boot) |
| 定位 | 编码 Agent 工具 + SDK | 企业级 AI 集成框架 |
| 核心优势 | 上下文工程、树形历史、扩展灵活 | Spring 生态、事务、安全、监控 |
| 适用场景 | 自动化编码、CLI Agent 工具 | 后端应用集成 AI 能力 |

---

#### Claude Agent SDK 实战要点

> 官网：<https://docs.anthropic.com/en/docs/agents-and-tools/claude-agent-sdk>  |  Python **/ TypeScript** | 原生 MCP 支持

**核心能力：**

1. **原生 MCP（Model Context Protocol）**：Claude 团队设计的工具协议，Agent 能动态发现和调用外部服务
2. **多 Agent 编排**：master Agent 指派子 Agent 处理独立子任务，可嵌套
3. **计算机使用（Computer Use）**：Agent 能操作 UI、截图、点击——对自动化测试和 GUI 操作用处大
4. **人机交互**：Agent 执行到决策点可暂停等待人工输入

**Demo 1：MCP Server 驱动的投研 Agent**

```typescript
import { Agent } from 'claude-agent-sdk';

// MCP Server 连接多个数据源
const agent = new Agent({
  apiKey: process.env.ANTHROPIC_API_KEY,
  mcpServers: [
    './stock-price-server.js',     // 股票行情
    './financial-report-server.js', // 财报数据
    './news-search-server.js'       // 新闻检索
  ]
});

const report = await agent.run(`
  分析 TSLA 的投资价值：
  1. 获取最近 3 个月股价走势
  2. 获取最新财报数据
  3. 搜索近期相关新闻和公告
  4. 综合判断并给出投资建议
`);
```

**Demo 2：多步骤 Agent + 人工审批**

```typescript
const result = await agent.run(
  '分析并生成 PR #42 的代码审查报告，标记安全风险',
  { onStep: async (step) => {
    if (step.type === 'decision' && step.confidence < 0.7) {
      return await askHuman(step.question); // 停住等人
    }
  }}
);
```

**资源：**
- [Anthropic 官方文档 - Agent SDK](https://docs.anthropic.com/en/docs/agents-and-tools/claude-agent-sdk)
- [MCP Specification](https://modelcontextprotocol.io/) — MCP 协议详解
- [MCP Server 市场](https://github.com/modelcontextprotocol/servers) — 开源 MCP Server 集合
- [Claude Computer Use Demo](https://docs.anthropic.com/en/docs/agents-and-tools/computer-use) — 操作浏览器/桌面

**与 Spring AI 搭配：** Claude Agent SDK 做推理层（复杂多步、MCP 工具链），Spring AI 做服务层（REST API、数据库、事务管理）。

---

#### LangGraph 实战要点

> 官网：<https://langchain-ai.github.io/langgraph/>  |  Python / TypeScript / Java | 基于图的 Agent 编排

LangGraph 和普通 Agent 框架的区别：**它不是线性链，而是有状态图**。每个节点是一个处理步骤，边定义了流程控制逻辑。

**核心概念：**

| 概念 | 说明 |
|------|------|
| StateGraph | 共享状态的有向图，节点读写状态 |
| Node | 处理函数（Agent 调用、工具执行、条件判断） |
| Edge | 条件边：根据当前状态决定下一步走到哪个节点 |
| Checkpoint | 自动保存状态快照，支持断点续跑 |
| Human-in-the-loop | 执行到决策节点暂停等人类输入 |

**Demo：带人工反馈的 PR 审查工作流**

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

# 共享状态
class PRReviewState(TypedDict):
    pr_diff: str
    issues: List[str]
    auto_approved: bool
    human_feedback: str
    final_decision: str

# 节点 1：自动检查
def auto_check(state: PRReviewState):
    # Claude 代码审查
    issues = llm.invoke(f"Review this PR diff: {state['pr_diff']}")
    # 如果都是格式问题，自动通过
    auto_ok = len(issues.split('\n')) < 3
    return {"issues": issues, "auto_approved": auto_ok}

# 节点 2：等人工审查
def human_review(state: PRReviewState):
    return {}  # 暂停，等用户输入 human_feedback

# 条件边
def after_auto_check(state):
    if state["auto_approved"]:
        return "approve"
    else:
        return "human_review"

# 节点 3：综合判断
def final_decision(state):
    feedback = state.get("human_feedback", "")
    issues = state["issues"]
    decision = llm.invoke(f"Issues: {issues}\nHuman feedback: {feedback}\nApprove?")
    return {"final_decision": decision}

# 构建图
builder = StateGraph(PRReviewState)
builder.add_node("auto_check", auto_check)
builder.add_node("human_review", human_review)
builder.add_node("final", final_decision)
builder.set_entry_point("auto_check")
builder.add_conditional_edges(
    "auto_check",
    after_auto_check,
    {"approve": END, "human_review": "human_review"}
)
builder.add_edge("human_review", "final")
builder.add_edge("final", END)

graph = builder.compile()

# 执行
result = graph.invoke({
    "pr_diff": open("pr.diff").read()
})
```

**在 Java 生态中使用 LangGraph：**

- [LangGraph4j](https://github.com/bsorrentino/langgraph4j) — LangGraph 的 Java 移植版
- 配合 Spring AI 做节点内的 Agent 调用
- 适用场景：需要**人工审批环节**的工作流（PR review、投研报告、合规审查）

**资源：**
- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/) — 教程 + API 参考
- [LangGraph 官方示例](https://github.com/langchain-ai/langgraph/tree/main/examples) — 多 Agent 编排、RAG、客服
- [LangGraph4j (Java)](https://github.com/bsorrentino/langgraph4j) — Java/Scala 版
- [LangGraph Studio](https://github.com/langchain-ai/langgraph-studio) — 可视化调试台

---

## 框架选型建议

| 场景 | 推荐框架 | 原因 |
|------|---------|------|
| Spring Boot 后端接入 AI | **Spring AI** | 原生 Spring 整合，DI/事务/监控全齐 |
| 命令行编码 Agent | **Pi** | TypeScript、树形会话、扩展灵活 |
| 复杂多步推理 + 工具链 | **Claude Agent SDK** | MCP 协议、多 Agent 编排、Computer Use |
| 有状态工作流 + 人工审核 | **LangGraph** | 图编排、Checkpoint、Human-in-the-loop |

**实践路线：** Spring AI 做基础层（API + 工具注册），Claude Agent SDK / LangGraph 做推理层（复杂多步），Pi 做 CLI 工具和原型验证。

---

## 推荐 8 周学习计划

```
第1-2周  Fast.ai + Karpathy GPT 视频 → 动手改 nanoGPT
          Hugging Face NLP Course → 用 Transformers/TRL

第3-4周  Unsloth QLoRA + Colab 微调 2B 模型
          CS336 作业 1+2（手写 Transformer + FlashAttention）

第5-6周  Spring AI + Claude Agent SDK 上手 → 搭基础 Agent
          MCP Server 开发 → 集成投研/代码审查数据源

第7-8周  LangGraph 状态图编排 → 搭带人工审核的完整工作流
          集成：自己微调的模型 + Spring AI + MCP → 完整应用
```

**最短路**：Karpathy GPT 视频 (1 天) → Unsloth 微调 (1 天) → **Spring AI + Claude Agent SDK 搭 Agent** (2 天) → MCP 数据源集成 (1 天) → 第 1 周跑起来 MVP。

> 你有 Spring 基础，**Spring AI** 是最短路径的入口框架，MCP 协议可以无缝对接外部数据源。复杂流程再上 LangGraph 编排。

---

> 整理于 2026-06-19，基于 Stanford CS336 2026 Spring + 社区课程资源
