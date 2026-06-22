# LLM 理解 + 训练 + Agent 实践学习路径

> 目标：
> 1. 理解大模型原理与边界
> 2. 能在 Google Colab 上微调一个 2-4B 模型
> 3. 能用 Spring AI、Pydantic AI、Claude Agent SDK 等框架搭 Agent（自动编码、投研等）

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
| [Pydantic AI](https://ai.pydantic.dev/) | Python 框架，类型安全，Pydantic Schema 定义 Agent 行为。跟 Java 类型系统思维完全合拍 | **推荐优先学**。自动编码、结构化输出 |
| [Pi](https://pi.dev) | TypeScript 编码 Agent 框架。最小化 harness，15+ 模型供应商，树形会话历史，上下文工程（AGENTS.md/SYSTEM.md），4 种模式（交互/JSON/RPC/SDK） | TypeScript 生态。自动化编码、自定义 Agent |
| [Spring AI](https://docs.spring.io/spring-ai/reference/) | Java 生态，DI/Template 模式。支持 OpenAI、Ollama 等 | 已有 Spring 基础，1 小时上手 |
| [Claude Agent SDK](https://docs.anthropic.com/en/docs/agents-and-tools/claude-agent-sdk) | MCP + Tool-Use 原生支持 | 搭高级 Agent（投研、多步推理）|
| [LangGraph](https://langchain-ai.github.io/langgraph/) | 图状态机编排 Agent 多步流程 | 复杂工作流（投研流水线、自动 PR review）|

---

#### Pydantic AI 详解

> 官网：<https://ai.pydantic.dev/>  |  Python 框架 | 与 Pydantic（数据验证库）同一团队 | 最强类型安全

**为什么推荐你从 Pydantic AI 入手？**
- 你有 Java 工程背景，Pydantic 的 Schema 定义类比 Java 的 POJO + JSR-303 校验，思维契合
- 所有 Agent 输入/输出都用 Pydantic Model 定义，IDE 自动补全 + 类型检查
- 天然支持 Ollama、OpenAI、Claude、Google 等多种 LLM 后端
- 内置 Tool-Use、多 Agent 编排、结构化结果提取

**三个递进 Demo：**

⭐ **Demo 1：Hello Agent（5分钟上手）**

```python
from pydantic_ai import Agent

# 一行定义一个 Agent，类型是它的签名
agent = Agent('openai:gpt-4o', system_prompt='你是一个代码助手，擅长 Java 代码审查')

result = agent.run_sync('Review: public void doStuff() { /* complex logic */ }')
print(result.data)
```

⭐ **Demo 2：带工具的 Agent（自动编码 Agent）**

```python
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
import subprocess

class CodeReview(BaseModel):
    issues: list[str]
    score: int  # 1-10
    suggestion: str

agent = Agent(
    'openai:gpt-4o',
    result_type=CodeReview,  # 结构化输出，自动解析
    system_prompt='你是高级 Java 代码审查员'
)

@agent.tool
def run_checkstyle(ctx: RunContext, file_path: str) -> str:
    """运行 checkstyle 检查代码规范"""
    result = subprocess.run(['checkstyle', file_path], capture_output=True, text=True)
    return result.stdout

@agent.tool
def git_diff(ctx: RunContext, branch: str) -> str:
    """获取指定分支的 Git 差异"""
    result = subprocess.run(['git', 'diff', f'main..{branch}'], capture_output=True, text=True)
    return result.stdout[:5000]

# 用法
result = agent.run_sync('审查 feature/agent-auto-coding 分支的代码质量')
print(f"评分: {result.data.score}")
print(f"问题: {result.data.issues}")
```

⭐ **Demo 3：多 Agent 编排（投研 Agent）**

```python
from pydantic_ai import Agent
from pydantic import BaseModel

class ResearchReport(BaseModel):
    company: str
    market_position: str
    financial_health: str
    technical_analysis: str
    risk_factors: list[str]
    recommendation: str

# 三个专业 Agent
collector = Agent('openai:gpt-4o', system_prompt='搜索收集企业基础信息')
analyzer = Agent('openai:gpt-4o', system_prompt='财务和技术面分析师')
writer = Agent('openai:gpt-4o', result_type=ResearchReport,
               system_prompt='整合分析结果生成投资研究报告')

# 多步编排
async def research_pipeline(company: str):
    # 1. 信息收集
    raw = await collector.run(f'收集 {company} 最近财报和新闻')

    # 2. 分析
    analysis = await analyzer.run(f'基于以下信息进行分析：{raw.data[:3000]}')

    # 3. 写报告
    report = await writer.run(f'基于分析：{analysis.data}，生成投资建议')
    return report.data
```

**Pydantic AI 学习路径：**
1. 官网 Quickstart（10分钟）
2. 定义带 result_type 的结构化 Agent（理解类型驱动）
3. 添加 tool（理解 Tool-Use 模式）
4. 多 Agent 编排（理解 Agent Chain）
5. 对接自己微调后部署在 Ollama 上的模型（`ollama:qwen3-4b`）

---

#### Spring AI 实战要点

| 模块 | 说明 |
|------|------|
| ChatClient | 统一聊天接口，切换模型只要改配置 |
| Tool Calling | @Tool 注解注册 Java 方法为 AI 工具 |
| Advisors | 拦截器链（QuestionAnswerAdvisor 等） |
| VectorStore | PGVector/Redis 做 RAG |
| Function Calling | 直接调 Spring Bean 方法 |

**最小 Demo：**

```java
var client = ChatClient.builder(chatModel).build();

String response = client.prompt()
    .system("你是一个代码审查助手")
    .user("审查这段代码: ...")
    .call()
    .content();
```

---

#### Claude Agent SDK 实战要点

- 原生 MCP（Model Context Protocol）支持
- ```python
from claude_agent_sdk import Agent
agent = Agent(
    api_key="sk-ant-...",
    mcp_servers=["./investment-mcp-server.js"]  # 投研数据源
)
```
- 适合复杂多步推理的工具链
- 与 Spring AI 可同时使用：Claude Agent SDK 搭推理层，Spring AI 搭服务层

---

## 推荐 8 周学习计划

```
第1-2周  Fast.ai + Karpathy GPT 视频 → 动手改 nanoGPT
          Hugging Face NLP Course → 用 Transformers/TRL

第3-4周  Unsloth QLoRA + Colab 微调 2B 模型
          CS336 作业 1+2（手写 Transformer + FlashAttention）

第5-6周  Pydantic AI + Spring AI 上手 → 搭第一个 Agent
          Claude Agent SDK + MCP → 搭代码审查/投研 Agent

第7-8周  CS336 作业 5 + TRL（对齐训练）→ 优化 Agent 底座
          集成：自己微调的模型 + Agent 框架 + Spring AI → 完整应用
```

**最短路**：Karpathy GPT 视频 (1 天) → Unsloth 微调 (1 天) → **Pydantic AI 搭 Agent** (2 天) → Spring AI 集成 (1 天) → 第 1 周跑起来 MVP。

> Pydantic AI 的 Type-Safe 思维跟你的 Java 背景天然合拍，建议作为 Agent 入口框架优先练手。

---

> 整理于 2026-06-19，基于 Stanford CS336 2026 Spring + 社区课程资源
