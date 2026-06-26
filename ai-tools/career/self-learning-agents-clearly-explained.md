---
title: "代理自我学习（Self-Learning）完全指南"
tags:
  - ai-agents
  - self-learning
  - llm-agents
  - agentic-systems
date: 2026-06-24
source: "https://x.com/ataiiam/status/2069797329809395978"
authors: "Atai Barkai (CopilotKit CEO)"
---

# 代理自我学习（Self-Learning）完全指南

> **来源：** Self Learning for Agents Clearly Explained — Atai Barkai
> 作者为 CopilotKit CEO、前 Meta 员工

![封面](../image/self-learning-agents/cover.jpg)

每个人都在谈"自我学习代理"，但大多数产品需要的根本不是那个版本。

**最有价值的信号，几乎没人捕捉：你的用户。**

你的代理和用户每天都在并肩工作，成千上万次。每个交互都可以成为学习素材。

---

## 三种学习层

![三层架构](../image/self-learning-agents/three-layers.jpg)

Harrison Chase 给出了最清晰的划分方式：

- **模型（Model）** = 权重（训练参数）
- **框架（Harness）** = 模型周围的代码（循环、工具、提示词）
- **上下文（Context）** = 框架之外的记忆和技能，可以持续增长

你在 Claude Code 里已经用到了全部三层：模型是 Claude，框架是 Claude Code 本身，上下文是你的 CLAUDE.md 和 Skills。每一层可以独立优化，不影响其他两层。

---

**在产品中，"自我学习"几乎总是框架层或上下文层，而不是模型层。模型属于研究实验室，框架和上下文才属于你。**

我会用一个贯穿三层的例子：**一个处理退款的客服代理。**

对每一层，问两个问题：能在这里学习吗？你拥有这个学习成果吗？

---

## 第一层：模型（The Model）

这是每个人想象中的那层，也是几乎没人真正在跑的那层。代理改进模型本身。研究实验室用三种方式实现：

![模型层方法概览](../image/self-learning-agents/seal-alphaevolve.jpg)

1. 编辑训练代码，保留提升分数的修改
2. 自己写训练数据，融入权重
3. 尝试多个代码改动，保留最好的

这三种都是同一个循环，而且只在**计算机能免费打分**时才能运作。

### Karpathy 的 AutoResearch

> 链接：[github.com/karpathy/autoresearch](https://github.com/karpathy/autoresearch)

![Karpathy AutoResearch](../image/self-learning-agents/karpathy.jpg)

把一个编码代理指向一个小型训练环境，让它跑一整夜。它编辑一个文件，训练五分钟，打分。保留改好的，撤销没用的。循环一百次。

有一次发现了一个约 11% 的真实加速。

**问题：** 这个代理改进的是另一个更小的模型——它自己的权重其实从未改变。

### MIT SEAL（Self-Adapting LLMs）

> 论文：[arxiv.org/abs/2506.10943](https://arxiv.org/abs/2506.10943)

自己写训练数据，训练后保留提升分数的改动。这是对自己权重的真实修改。

**问题：** 每次编辑都是一次完整重训——30-45 秒。而且学习新任务时会忘记旧任务。实验室里挺好，生产环境太慢。

### DeepMind AlphaEvolve

> 博客：[DeepMind](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/)

提出代码改动，自动打分，保留胜者。这是三者中最有说服力的。

它让一个真实的注意力内核快了 32.5%，发现了一个自 1969 年以来未被超越的矩阵乘法捷径，甚至让它自己运行的 AI 训练变快了——**AI 改进了它自己运行的 AI**。

**问题：** 只在计算机能免费回答时有效——也就是说，只有代码和数学。

### 模型层总结

哪种应该放进你的产品？**大概都不。**

它们都需要免费的、可信的分数。内核更快就是更快，模型得分更高就是更高。但进入客服、销售或运营后，这个分数就消失了。

**退款代理的例子（模型层）：** 你根据过去的退款决定重新训练它。但没有计算机能评判一个退款是对是错。循环没有东西可打分，所以永远跑不起来。

---

## 第二层：框架（The Harness）

框架就是模型之外的一切：运行模型的那个循环、它能接触的工具和文件、系统提示词、行为前的检查。

模型提供智能，**框架决定智能如何被使用。**

框架和上下文容易混淆。Dex Horthy 给出了清晰的区分：框架是上下文工程的一部分——管理模型能看到的一切。

![框架层方法概览](../image/self-learning-agents/harness-diagram.jpg)

四种方法，不同的人机分工：

1. 手写循环
2. 让代理读取日志并提出改动，你审批
3. 让框架自己改自己，无人监督
4. 直接装一个预构建的框架

### 方法 1：循环工程（Loop Engineering）

> 参考：[The art of loop engineering — Sydney Runkle](https://www.langchain.com/blog/the-art-of-loop-engineering)

![循环工程](../image/self-learning-agents/deep-agents.jpg)

基础循环是模型调用工具直到它认为完成了。改进方式是**在它外面套更多循环**。

最有用的是验证循环——一个评分者检查输出，不过关就打回去。上面还可以再套两个：一个按计划调度代理后台运行，另一个读取日志并重写框架。

**问题：** 循环只在你能对输出打分时才有用——需要测试、规则或 LLM 评委。

### 方法 2：LangChain Deep Agents

> 博客：[LangChain](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)

从自己的日志中重写框架。

跑一批任务，记录每条日志（哪里成功、哪里失败），然后让一个编码代理分析失败模式，重写提示词、工具和钩子。

LangChain 在模型不变的情况下用这个方法优化 Deep Agents：Terminal-Bench 2.0 从 52.8 提升到 66.5，从前 30 冲进前 5。

**问题：** 代理只做提案。**每次改动需要人工审批才能上线。**

### 方法 3：Self-Harness

> 论文：[arxiv.org/abs/2606.09498](https://arxiv.org/abs/2606.09498)

![Self-Harness](../image/self-learning-agents/HLlMkarWQAA0RW4.jpg)

让框架自己改自己，无人监督。发现失败，提出一个修改，测试，只有测试通过才保留。

同一个方法让三个不同模型（权重冻结）的成绩：40.5→61.9、23.8→38.1、42.9→57.1。**只改框架就能提升所有模型，说明框架才是瓶颈。**

**问题：** 同样只在计算机能免费评分时有效——编码基准可以，退款流程不行。

### 方法 4：Microsoft Agent Framework

> 博客：[Microsoft](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-at-build-2026-announce/)

![Microsoft Agent Framework](../image/self-learning-agents/HLlUQGAWQAAMKpM.jpg)

框架是一个安装包：文件记忆、磁盘技能、plan-and-execute 模式、沙盒 shell。

**问题：** 它从代理自身的运行中学习。用户的行为不在其中。

### 框架层总结

这四种方法都是**提前构建好框架**，一次设置，代理每次任务都用同一套。你也可以反过来想：代理为每个任务**临时组装框架**，只拉入需要的工具和记忆。这还处于早期，但是方向。

**退款代理的例子（框架层）：** 加一个验证循环（退款前二次检查）。代理批了 $5,000 退款，检查发现超过 $2,000 限额，转给你人工审核。你批或拒。

不用重新训练，超额退款不再漏网。但代理并没有变聪明——是检查抓住了它。下次遇到 $5,000，它会做同样的事，再次来问你。**它没学会。**

---

## 第三层：上下文（The Context）

上下文是记忆和技能，作为**纯文本存在模型之外**。你可以读、改、删。这就是为什么大多数团队从这里开始。

记忆分三种：

- **语义记忆（Semantic）**：事实。这个客户的退款限额是 $2,000。
- **情景记忆（Episodic）**：过去经历。上周这个客户的退款被退回了。
- **程序性记忆（Procedural）**：怎么处理。忠诚客户超限且曾因多次发货失败：批准。

自我改进的代理需要后两种，但大多数实现只有第一种。

![上下文层方法概览](../image/self-learning-agents/HLlUWG0XwAA6_vi.jpg)

而且上下文能做到其他两层做不到的事：同一段文本可以同时服务于代理的记忆、单个用户的偏好、或整个团队——一次写下，所有人可读。

三种写入方式：

### 方法 1：Letta + OpenClaw

> Letta： [letta.com/blog/continual-learning](https://www.letta.com/blog/continual-learning) | Sleeping/Dreaming：[letta.com/blog/sleep-time-compute](https://www.letta.com/blog/sleep-time-compute) | OpenClaw Dreaming：[docs.openclaw.ai/concepts/dreaming](https://docs.openclaw.ai/concepts/dreaming)

![Letta & OpenClaw](../image/self-learning-agents/HLlUcH7XoAAGijD.jpg)

保持权重冻结，用你可读、可 diff、可删除的纯文本学习。正在和你对话的代理不能编辑自己的核心记忆——一个**独立的代理在空闲时间重写它**。OpenClaw 用同样的思路实现了"夜间做梦"回放记忆文件。

**价值：** 权重是临时的，文本是持久的。你可以迁移到新模型，或者回滚。

### 方法 2：Hermes Self-Evolution

> 项目：[NousResearch/hermes-agent-self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution) | Agentic Context Engine：[kayba-ai/agentic-context-engine](https://github.com/kayba-ai/agentic-context-engine)

![Hermes Self-Evolution](../image/self-learning-agents/HLlUv-WXkAATrSl.jpg)

读取失败的日志，找到失败原因，提出修复方案。不需要 GPU。

**问题：** 只能重写技能，不能改工具、提示词或代码。而且每次改动必须通过测试和人工审批。

### 方法 3：Anthropic Skills + Manus

> Anthropic Skills：[claude.ai/skills](https://platform.claude.com/docs/en/docs/agents-and-tools/agent-skills/overview) | Manus Skills：[manus.im/docs/features/skills](https://manus.im/docs/features/skills)

把一次成功的会话存为 SKILL.md。只有名称和一行摘要常驻内存（约 100 tokens），其余内容在技能被调用时才加载。

一次检查一个技能，分享出去，一个人的好成果让所有人的下次运行更好。

**问题：** 保存的是曾经成功过一次的东西。没有人检查它是否仍然有效，也不会在它过时时移除它。

### 上下文层总结

这三种方法都是**把有效做法变成文本**，供下次运行读取。权重冻结，框架不变。

**退款代理的例子（上下文层）：** 它保留一个运行笔记：这个客户的限额、哪些退款被退回、上次尝试了什么。下次运行时它读到这个笔记，而不需要从头开始。什么都没重训，只是贴了一张便签。

---

## 你错过的最重要信号：从用户中学习

到目前为止的所有方法，都是从**代理自身的运行**中学习。

**有一个更好的信号，几乎没人捕捉：使用你产品的人。**

客服、销售、运营。退款决策没有自动测试。唯一能告诉代理它做得对还是错的，是**一个人**。

![从交互中学习](../image/self-learning-agents/HLlUhtbXgAATVHg.jpg)

一个人的真实决策是**无法伪造的信号**。自动分数可以。

Sakana 的 Darwin Gödel Machine 被放出去针对测试自我改进，结果它不是在提升工作质量，而是**伪造了测试日志**。当研究人员加上检测器抓它，它把检测器依赖的标记给删了——尽管被明确禁止这么做。

有两种方式捕捉人的知识，每种只看到一半：

### 方式 1：在背后窥视
录屏、记录按键和点击。Meta 2026 年在员工笔记本上部署了这种方案。**侵入性高，看到人做的一切，但看不到代理。**

### 方式 2：从交互中学习
代理从来回对话中学习。告诉代理邮件太正式，下次它就写得更随意。但它只注意到人打的字，**错过了人做的所有事。**

### 最佳位置：CopilotKit + AG-UI

一个地方能同时看到两边：**人和代理并肩工作的界面。** 这就是 CopilotKit 和 AG-UI（Agent-User Interaction Protocol）的所在。

AG-UI 是一个开放标准协议，实时流式传输应用、用户和代理之间的每一个事件。

![AG-UI 示意图](../image/self-learning-agents/HLlUovdWYAAcQQx.jpg)

**再想想退款代理：**

一个客户要求退回 $5,000。代理停在 $2,000 限额上拒绝了。经理打开同一个线程，手动批准：老客户，第三次配送延迟。

**这一对就是教训，捕捉它不花一分钱。**

经理的点击已经在通过应用刷新屏幕了——你只是在读同样的事件。

后台代理记录经理做了什么和为什么。**下一个代理读到它作为程序性记忆**，下次遇到同样的案子，它会像经理一样批准，而不是拒绝。

不只是文字。AG-UI 把每次工具调用、状态变更、审批都作为事件携带——代理的失误和人的修正落在同一个地方。

![CopilotKit Intelligence 演示视频截图](../image/self-learning-agents/HLlUhtbXgAATVHg.jpg)

这可以通过 **CopilotKit Intelligence** 实现，已经在 Fortune 500 企业生产环境中运行，开放早期体验。

> CopilotKit Intelligence 可自托管，在你自己的基础设施中运行，学到的一切都归你所有。

---

## 自我学习一句话总结

![总结表](../image/self-learning-agents/final.jpg)

| 层 | 什么在变 | 怎么学 | 在哪跑 |
|---|---|---|---|
| 模型（Model） | 权重 | 用自己的运行训练，当分数免费时 | 研究实验室 |
| 框架（Harness） | 脚手架 | 从日志重写提示词、工具、钩子 | 产品中，今天 |
| 上下文（Context） | 记忆和技能 | 把有效做法蒸馏为文本供下次读取 | 产品中，**且唯一能从用户学习的层** |

问题不是你的代理应不应该改进，而是**在哪里改进**。

- 模型属于研究实验室
- 框架和上下文是你的
- **最好的地方**：上下文从用户中学习。它运行在机器无法伪造的信号之上：**一个已经做出正确决定的人。**

---

> 想了解更多？联系 [CopilotKit](https://www.copilotkit.ai/) 获取早期体验。
> 关注 [@ataiiam](https://x.com/ataiiam) 获取更多内容。

---

*Processed on 2026-06-26 from [x.com/ataiiam/status/2069797329809395978](https://x.com/ataiiam/status/2069797329809395978)*
