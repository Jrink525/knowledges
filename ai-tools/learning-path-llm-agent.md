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
| [Pydantic AI](https://ai.pydantic.dev/) | 类型安全，Schema 定义 Agent 行为。适合有类型系统思维的人 | **推荐优先学**。自动编码、结构化输出 |
| [Spring AI](https://docs.spring.io/spring-ai/reference/) | Java 生态，DI/Template 模式。支持 OpenAI、Ollama 等 | 已有 Spring 基础，1 小时上手 |
| [Claude Agent SDK](https://docs.anthropic.com/en/docs/agents-and-tools/claude-agent-sdk) | MCP + Tool-Use 原生支持 | 搭高级 Agent（投研、多步推理）|
| [LangGraph](https://langchain-ai.github.io/langgraph/) | 图状态机编排 Agent 多步流程 | 复杂工作流（投研流水线、自动 PR review）|

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

**最短路**：Karpathy GPT 视频 (1 天) → Unsloth 微调 (1 天) → Pydantic AI/Spring AI 搭 Agent (3 天) → 第 1 周跑起来 MVP。

---

> 整理于 2026-06-19，基于 Stanford CS336 2026 Spring + 社区课程资源
