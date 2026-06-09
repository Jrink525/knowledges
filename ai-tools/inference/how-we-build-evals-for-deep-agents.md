# How We Build Evals for Deep Agents

> **作者**: Viv Trivedy — Applied Research @LangChain  
> **来源**: [X/Twitter](https://x.com/vtrivedy10/status/2037203679997018362) | [LangChain Blog](https://blog.langchain.dev)  
> **日期**: 2026-03-26  
> **标签**: `#agent-evals` `#deep-agents` `#langsmith` `#agent-testing`

---

## TL;DR

最好的 agent evals 直接测量你在意的 agent 行为。本文涵盖如何采集数据、创建指标、以及运行范围明确的目标实验来让 agent 更准确可靠。

---

## 核心理念：Evals 塑造 Agent 行为

每个 eval 都是改变 agent 系统行为的一个**向量**。

例如：如果「高效文件读取」的 eval 失败了，你会调整 system prompt 或 `read_file` tool 的描述，直到它通过。每个你保留的 eval 都会持续对整个系统施加压力。

**关键警告：** 盲目添加数百/数千个测试，会导致你"感觉" agent 在改进，但实际上可能在做一个不准确反映生产环境的评估套件上得分很高。

> **更多 evals ≠ 更好的 agent。** 构建反映生产所需行为的**目标化** evals。

---

## Eval 处理流程

### 1. 决定要测量的行为
列出生产中重要的行为，例如：
- 跨文件检索内容
- 准确组合 5+ 次工具调用

### 2. 为目标行为编写目标化 evals
为每个 eval 添加 docstring，说明它如何测量 agent 能力（自文档化）。打上标签（如 `tool_use`）以便分组运行。

### 3. 分析失败模式并更新覆盖
通过 trace 理解失败模式，提出修复方案，重新运行 agent，跟踪进展和回归。

---

## 三种数据来源

### 1. Dogfooding（吃自己的狗粮）
团队每天使用自己的 agent。每次出错 → 变成一次 eval → 更新 agent 定义和上下文工程实践。

**案例：** Open SWE（开源后台编码 agent）驱动了大量修复 PR。每个交互都被 trace，错误很容易变成 evals。

### 2. 外部 Benchmark（调整后引入）
从现有 benchmark 中精选并调整 evals：
- **BFCL** → Function Calling 能力
- **Terminal Bench 2.0** → 编码任务（通过 Harbor 在沙箱环境运行）

### 3. 手写定制 Evals
编写完全自定义的 evals，用于测试隔离行为（如测试 `read_file` tool）。

---

## Eval 分类法（按测试内容分组）

按**测量什么**分组，而不是按**来源**分组：

| 分类 | 测试内容 |
|------|---------|
| **memory** | 记忆 — 从之前对话/交互中保留和读取 |
| **tool_use** | 工具使用 — 选择正确工具、正确参数 |
| **file_operations** | 文件操作 — 读取/写入/编辑文件 |
| **multi_step_reasoning** | 多步推理 — 跨越多个步骤的逻辑链 |
| **planning** | 规划 — 面对复杂问题制定并执行方案 |

> 💡 **提示：** 按测试内容分类，而非来源。例如 FRAMES 和 BFCL 都打上"外部 benchmark"标签反而看不出它们分别测量 retrieval 和 tool use。

---

## 如何定义指标

### 第一阶段：正确性（Correctness）
如果模型无法可靠完成任务，其他指标没有意义。

| 测试类型 | 评估方式 |
|---------|---------|
| 内部 Evals | 自定义断言（如"agent 是否并行调用了工具？"） |
| 外部 Benchmark (BFCL) | 与 ground truth 精确匹配 |
| 语义正确性（如记忆持久化） | LLM-as-a-judge |

### 第二阶段：效率（Efficiency）
两个能解决相同任务的模型，行为可能差异巨大（多余步骤、不必要的工具调用、不同模型大小导致速度差异）。

**关键指标：**

| 指标 | 说明 |
|------|------|
| **Latency Ratio** | 实际耗时 / 期望耗时 |
| **Cost** | 按 token 和 API 调用计费 |
| **Solve Rate** | 完成任务速度（标准化为期望步数）—— 对简单任务更易操作 |

### 理想轨迹（Ideal Trajectory）

定义"最优执行"的参考基准：

```
简单任务: "我现在在哪，天气怎么样？"
理想轨迹: 4步, 4次工具调用, ~8秒
  - resolve_user → resolve_location → fetch_time + fetch_weather(并行)

低效但正确: 6步, 5次工具调用, ~14秒
  - 包含不必要的工具调用，未并行化
```

这种对比框架让你同时评估**正确性**和**效率**。

---

## 如何运行 Evals

- **工具**: pytest + GitHub Actions（CI，干净/可复现环境）
- **每次运行**: 创建 Deep Agent 实例 → 给定 model → 输入任务 → 计算指标
- **标签子集**: 使用 tags 选择特定子集运行（节省成本），例如只运行 `file_operations` 和 `tool_use` 相关的 evals

> ⚠️ **注意：** 区分 SDK 单元/集成测试（system prompt passthrough、interrupt config、subagent routing）与模型能力评估。任何模型都能通过那些测试，加入评估分数没有信号价值。

---

## Eval 架构（开源）

所有 Deep Agents 的 eval 架构和实现已开源，代码库见 [Deep Agents Repository](https://github.com/langchain-ai/deep-agents)。

---

## 下一步计划

1. **Open Models vs 闭源 Frontier Models** — 跨 eval 分类的性能对比
2. **Eval 驱动自动改进** — 利用 evals 实时自动优化 agent 执行
3. **开放的 Eval 维护策略** — 展示如何随时间维护、缩减和扩展 evals

---

## 核心洞察总结

> **好的 evals 不是越多越好，而是每个都精准测量一个你真正在意的行为。**

整套方法论的核心：
1. **来源** → dogfooding + 精选 benchmark + 手写定制
2. **分类** → 按测试能力分组（memory, tool_use, file_operations 等）
3. **指标** → 正确性优先，效率其次（latency ratio, solve rate, cost）
4. **运行** → pytest + CI + 标签子集
5. **迭代** → trace 分析 → 修复 → 重新评估

---

*感谢团队审核和共同撰写：@masondrxy @veryboldbagel @hwchase17*
*全文同步发布在 LangChain 官方博客。*
