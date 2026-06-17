---
title: "循环工程的艺术：LangChain 四层 Agent 循环体系"
tags:
  - agent
  - langchain
  - loopcraft
  - ai-engineering
date: 2026-06-17
source: "https://x.com/sydneyrunkle/status/2066928783534289358"
authors: "Sydney Runkle (LangChain)"
---

# 循环工程的艺术：LangChain 四层 Agent 循环体系

> **来源：** [Sydney Runkle (@sydneyrunkle) on X](https://x.com/sydneyrunkle/status/2066928783534289358)

![封面图](../image/the-art-of-loop-engineering-1.png)

Agent 之所以有用，是因为它们能通过在现实世界中执行操作来自动化工作。但要让 Agent 可靠地完成有价值的任务，仅仅有一个好模型是不够的——还需要一个**精心设计的承载框架（harness）**，与具体任务相匹配。

核心的 Agent 算法很简单：给 LLM 上下文，让它在循环中调用工具，直到任务完成。这是最基础的循环。但这远非驱动 Agent 的唯一循环。@swyx 最近写了一篇关于"循环工艺（loopcraft）"的好文章，核心思想是：**你可以堆叠和扩展循环来构建更高效能的 Agent**。

以下是我们对这个堆叠体系的理解，以及如何用 LangChain 原语来实现每一层。

---

## 第一层：Agent 循环

最底层就是 Agent 本身——模型在循环中调用工具直到任务完成。

这就是 LangChain 的 `create_agent` 提供的能力。选一个模型，接入工具，你就有了一个可运行的 Agent 循环。工具赋予了 Agent 在现实世界中采取行动的能力。

以他们内部的**文档 Agent** 为例（全篇的贯穿案例）。在第一层循环中，它收到文档改进的请求，模型规划并起草修改，使用工具来克隆仓库、读取文件、写文档、提交 PR 等。

---

## 第二层：验证循环（Verification Loop）

Agent 循环能干活，但不能保证第一次输出就是正确的。当一致性很重要时，可以在外层包装一个**验证循环**：检查输出质量，不符合标准就回传反馈。

验证循环引入了一个**评分器（grader）**：根据预设准则检查 Agent 输出，不合格就退回重做。评分器可以是确定性的（规则检查），也可以是 Agent 式的（LLM as a Judge 是经典做法）。

**LangChain 实现**：
- `RubricMiddleware` 直接支持这个模式
- 也可以通过 `create_agent` 的 `after_agent` 钩子来手动接入

回到文档 Agent 的例子：评分器在每次尝试后运行测试，检查所有链接是否可解析、CI 检查是否通过、diff 范围是否仅限于请求内容。这些错误类别无需人工审核就能自动捕获。

**取舍**：增加验证会提高延迟和每次运行的成本。当**质量比速度更重要**时值得——这涵盖了大多数生产场景。

---

## 第三层：事件驱动循环（Event-Driven Loop）

Agent 开发中最重要的一环是**集成层**：把你的 Agent 连接到生态系统中，让它能在后台持续运行。

事件驱动循环将 Agent 连接到你的整个技术栈。事件触发——新文档落地、定时器到点、Webhook 到达——Agent 就自动运行。Agent 不是你手动调用的东西，而是一个**在更大系统中持续运行的组件**。

**LangChain 支持**：
- **LangSmith Deployment** 提供触发器基础设施，支持 cron 定时任务和 webhooks
- 文中特别提到 OpenClaw 的"heartbeats"就是 cron 驱动 Agent 的经典案例——让你的 Agent 变成全天候的主动助手
- **Fleet**（LangChain 的无代码 Agent 构建器）的 channels 和 schedules 负责事件驱动和 cron 风格触发器。文档 Agent 就是用 Fleet 构建的——每当 `#docs-plz` Slack 频道有消息，channel 就会触发文档 Agent 开始工作

---

## 第四层：爬山循环（Hill Climbing Loop）

前三个循环**自动化了工作**。第四层——也是最关键的一层——**自动化了改进本身**。

每次 Agent 运行都会产生一个**追踪（trace）**：记录了模型做了什么、调用了什么工具、评分器的反馈等。这些 trace 含有关于**什么在起作用、什么不起作用**的高价值信号。

爬山循环的运行逻辑：
1. 一个**分析 Agent** 遍历这些 trace
2. 根据发现的问题重写承载框架（harness）的配置
3. 这可能包括：prompt 调整、工具调整、评分器调整

**LangChain 实现**：在 LangSmith 中，可以使用 **Engine**（trace 分析 Agent）来实现这第四层循环。

回到文档 Agent：他们在文档 Agent 的 trace 上运行 Engine 来检测问题。当多个 trace 指向同一个潜在问题时，会自动提交一个 issue，要求修改出问题的 prompt 或工具。

**关键洞察**：这个循环的返回箭头不只是回到起点——它**向内深入，直接更新 Agent 循环本身**。外层循环的每一轮迭代都让内层循环变得更高效。

> **展望未来**：Prompt 和工具配置是最容易改进的维度，但这不是唯一选择。对于运行开源权重模型的团队，爬山循环可以接入 **RL 微调**——用 trace 或 eval 结果作为训练信号来改进模型本身。辅助上下文（如记忆和检索到的技能）也可以用同样方式改进。**循环是模式，优化什么由你决定。**

---

## 人工监督与专业知识

自动化不等于把人移出循环。在每一层都有自然的**人工介入点**：

1. **Agent 循环**：在敏感操作/工具调用前要求人工确认
2. **验证循环**：对于敏感工作流，人类可以作为评分器
3. **应用循环**：输出返回给最终用户前，人工审批
4. **爬山循环**：改进方案可以经过人工审核后再部署

自动评分器能检查链接是否可解析，但只有人类才能注意到"这个表述对目标受众不合适"。那种源自上下文、经验和品味的判断力，正是人类审核的价值所在。

LangChain 的所有开源框架都将"人在回路中（human in the loop）"作为一等公民原语。

---

## 总结

| 层级 | 循环 | 核心目的 | LangChain 原语 |
|------|------|---------|------------|
| 1 | Agent 循环 | 执行任务 | `create_agent` |
| 2 | 验证循环 | 保证质量 | `RubricMiddleware` / `after_agent` hook |
| 3 | 事件驱动循环 | 融入生态 | LangSmith Deployment (cron/webhook) / Fleet channels & schedules |
| 4 | 爬山循环 | 自动改进 | LangSmith Engine (trace 分析 Agent) |

**核心结论**：这就是"循环工程"（或称 loopcraft）在实践中的真正面貌。AI 领域的领军人物（Steipete、Boris、Andrej）都得出了一致的结论——**Agent 的潜力在于你围绕它们构建的循环体系**。

我们已经思考第一、二层循环很久了。但重点应该转向第三、四层——**将 Agent 嵌入生态系统并持续自我改进**的价值是复利的。

**组织的战略启示**：那些尽早构建学习循环的公司——人类判断和 token 资本在其中一起复利增长——将建立起难以复制的竞争优势。

---

### 致谢

感谢 @Vtrivedy10、@masondrxy、@hwchase17 和 @huntlovell 的审阅。

### 参考链接

- [DeepAgents 快速开始](https://langchain-ai.github.io/deepagents/)
- [create_agent 文档](https://langchain-ai.github.io/langgraph/how-tos/create-react-agent/)
- [Rubric Middleware](https://langchain-ai.github.io/deepagents/#evaluation--refine)
- [LangSmith Deployment 定时任务 & Webhooks](https://docs.smith.langchain.com/deployment)
- [LangSmith Engine](https://docs.smith.langchain.com/evaluation/engine)
- [Fleet Channels](https://langchain.com/fleet)

---

*整理于 2026-06-17，来源：Sydney Runkle @sydneyrunkle on X*
