---
title: "21 painful mistakes I made building AI agents so you don't have to"
source: "https://x.com/gkisokay/status/2059986597391823286"
author: "Graeme (@gkisokay)"
read_at: 2026-06-02
category: ai-agents
tags: [openclaw, hermes, ai-agents, agent-architecture, research-agent, supervision, cost-control]
---

# 21 painful mistakes I made building AI agents so you don't have to

> 作者 Graeme（@gkisokay）过去 3 个月每天都在构建 Hermes 和 OpenClaw agents，本文是他踩过的 21 个坑 —— 来自一线的血泪教训。

---

## 1. ❌ 别构建一个巨大的全能 Agent

**✅ 构建一队专业 Agent，每个拥有明确的职责。**

一个臃肿的 Agent 会变得难以调试、路由和信任。单一职责的 Agent 才可扩展、易管理。

## 2. ❌ 别先构建面向输出的 Agent

**✅ 先构建研究 Agent（Research Agent）。**

研究 Agent 是输入智能层，为所有其他 Agent 提供养料。它从外部世界收集的一切信息，都会成为你的训练数据，持续优化你的系统。

## 3. ❌ 别把爬虫当研究

**✅ 原始链接、Feed 和摘要远远不够。**

Agent 需要的是**结构化、可验证、有来源支撑**的信息，让它们能真正行动。

## 4. ❌ 别让研究成果死在文档里

**✅ 研究 Agent 应该把发现路由到工作流中** — 编码、内容、营销、竞品情报、咨询信号、产品创意。

## 5. ❌ 别让自主工作流"盲跑"

**✅ 用 Supervisor 或运行时监控**，观察预期流程 vs 实际流程，捕获失败并即时修复。

## 6. ❌ 别一个人扛 OpenClaw 太久

**✅ 尽早让 Hermes 担任 Supervisor。**

作者在调试 OpenClaw 上浪费了数周。Hermes 有更好的 UX、持久记忆，还能自动拉取 ClawHub skills。

> 相关阅读：[《The Setup That Saved Me Hours Every Day: OpenClaw + Hermes》](https://x.com/gkisokay)

## 7. ❌ 别在自动构建之前缺失自动思考

**✅ 一个自构建系统首先需要一个自思考层**，用来发现摩擦、失败运行、缺失工具和重复瓶颈。

> 相关阅读：[《How to Build a Hermes Agent That Finds Important Work and Builds It Autonomously》](https://x.com/gkisokay)

## 8. ❌ 别给 Agent 模糊的目标

**✅ 明确定义"完成"意味着什么。** 添加验收标准、恢复逻辑、去重和清晰的成功检查。

## 9. ❌ 别基于松散的计划构建

**✅ 在 Agent 实施之前**，强制它们明确需求、边界情况、依赖关系、验收标准，以及"好"的标准是什么。

## 10. ❌ 别接受没有证据的 Agent 输出

**✅ 让 Agent 测试、验证、引用或演示结果。** 信任应来自证据，而不是自信。

## 11. ❌ 别在无成本追踪的情况下扩展自主循环

**✅ 记录每次运行的确切成本。** 当系统 24/7 运行时，这是生死攸关的事。

## 12. ❌ 别什么都用前沿模型

| 任务类型 | 推荐模型 |
|---------|---------|
| 扫描、摘要、头脑风暴、低风险审查 | 本地或廉价模型 |
| 规划、调试、硬推理 | 前沿模型（GPT-5.5, Claude, Gemini） |
| 工具调用 | Minimax |
| 全天候后台认知 | 本地 Qwen 等 |

> 模型多样性就是韧性：防止服务中断、限制、价格变化和突然质量下降。

## 13. ❌ 别忽视模型多样性

**✅ 混合使用多种模型。** 作者自己使用的组合：**GPT-5.5** + **Minimax（工具调用）** + **本地 Qwen**。

本地模型是全时段后台认知层，你的 RAM/VRAM 决定你能跑什么工作。

> 相关阅读：Local LLM Cheat Sheet Master Collection（April 2026）

## 14. ❌ 别忘记定期审计

**✅ 在工具、模型、MCP、工作流更新后执行每周审计。**

Agent 不维护就会退化。

## 15. ❌ 别忽视"声音"和"品味"

**✅ Voice 让 Agent 听起来像你。** Taste、Thesis、Proof 和 Forbidden-Pattern 文件让它思考得像你。

这些文件定义 Agent 的人格和行为边界。

## 16. ❌ 别只关注模型本身

**✅ 模型周围的系统才是关键：** 研究（Research）、路由（Routing）、记忆（Memory）、监督（Supervision）、反馈循环（Feedback Loops）和自改进（Self-Improvement）。

> 魔法发生在无聊的基础设施之后：干净的输入、清晰的交接、监控、恢复、评估和成本控制。

## 17. ❌ 别半途而废

**✅ 构建真正重要的东西**，迭代直到它完全按你所需的方式工作，**在完成之前不要转向**。

## 18. ❌ 别忽略成本控制

**✅ 尽一切可能保持 Agent 低成本。** 尤其在研究方面，需要想办法从数据提供商那里省钱。

> 推荐用 **Grok 做研究**（X API 原生的 Grok 搜索，$30/mo 替代数千美元 API 费用）

> 相关阅读：[《How to Make Your Hermes Agent Go SuperGrok》](https://x.com/gkisokay)

## 19. ❌ 别只看表面的"魔法"部分

**✅ 魔法发生在无聊的基础设施之后：** 干净的输入、清晰的交接、监控、恢复、评估和成本控制。

花时间确保这些都到位。大多数人无法忍受无聊的阶段。

## 20. ❌ 别完全照搬别人的方案

**✅ 你的 Agent 是你的。** 确保它为你工作。别人的设置不会构建出你需要的用例。

从他人那里借思想并融入自己的体系，你会学到更多（除了安全威胁外）。

## 21. ❌ 别闭门造车

**✅ 在公开场合构建（Build in Public）。**

没人真正知道什么是最好的方案。你需要自己摸索，并在旅途中与他人连接。

> 独自工作 → 得到孤立的结果。
> 公开构建 → 收获社区的红利。

---

## 总结：核心教训提炼

| 类别 | 教训 |
|------|------|
| **架构** | 专业化 Agent（1）> 研究优先（2）> 结构化数据（3）> 路由结果（4）|
| **运维** | 监控（5）> 监督者（6）> 自思考先行（7）> 审计（14）|
| **目标** | 明确"完成"（8）> 详实计划（9）> 证据验证（10）|
| **成本** | 追踪每笔运行（11）> 分层模型（12,13）> 保持廉价（18）|
| **系统** | 基础设施（19,16）> 保持真我（15,20）> 公开构建（21）> 坚持到完成（17）|

> 原文发布于 2026-05-28，51094 阅读 / 657 书签 / 210 赞
