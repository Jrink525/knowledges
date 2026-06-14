---
title: "你的 Agent Harness 应该能自我修复 — Opik：面向 Agent 时代的 AI 可观测性"
tags:
  - AI-Agents
  - Observability
  - Opik
  - Comet-ML
  - LLM
  - Agent-Harness
  - Testing
  - Sandbox
date: 2026-06-12
source: "https://x.com/akshay_pachaar/status/2064051835636498924"
authors: "Akshay 🚀 (@akshay_pachaar) | Sponsored by Comet ML"
---

# 你的 Agent Harness 应该能自我修复

> **来源：** [Your Agent Harness Should Repair Itself](https://x.com/akshay_pachaar/status/2064051835636498924) — Akshay 🚀，2026-06-12（Comet ML 赞助内容）

![封面](../image/agent-harness-self-repair-cover.jpg)

## 问题：生产中的 Agent 挂了，然后呢？

当 AI Agent 在生产环境出问题时，你的可观测性工具会精确展示它做了什么——但对怎么修几乎毫无帮助。

你会得到一条干净的执行追踪（trace）：每一次模型调用、每个触发过的工具、每步耗时、消耗了多少 token。但你没有的是：**为什么坏了、什么改动能修好、或者下周同样的问题不会再来。**

于是你手动一条条过 trace，猜测哪里出了问题，手写补丁，祈祷别搞坏其他正在工作的地方。然后新模型上线带着一批新的失败模式，你又得从头跑一遍这整个手工循环。

> **真正的瓶颈不是可观测性。是 trace 落到你屏幕上之后，那一切需要人工完成的事。**

Cursor 曾分享过他们围绕 Agent 构建的 harness（提示词、工具、校验组成的包裹层）投入了多少工程精力。同一个模型配上更好的 harness，结果天差地别——而且这项工作永远没有终点。

这就是目前可观测性平台的共同盲区：告诉你发生了什么，然后把"为什么会发生、要改什么、怎么防止再犯"全部扔回给你。

---

## 为何传统可观测性在规模化后失效

大多数 Agent 可观测性平台给你一条 trace 就结束了。你拿到 span 树、延迟数据、token 成本、一个仪表板。但你没有的是：

| 环节 | 当前状态 |
|------|---------|
| 发生了什么 | ✅ 平台处理 |
| 为什么会发生 | ❌ 手工分析 |
| 怎么修 | ❌ 手工打补丁 |
| 保证不再坏 | ❌ 无 |

这在 2023 年是个合理的产品，但对今天在生产环境跑 Agent 的团队来说，这个抽象层已经过时了。

问题会自我叠加。每次模型升级引入新的失败模式，每个新工具带来新的边界情况。Harness 变得越来越复杂，任何团队靠手动追踪修复都跟不上速度。

---

## Opik：面向 Agent 时代的 AI 可观测性与评估

Opik 是一个开源的 AI Agent 和 LLM 应用日志记录、调试和优化平台。它的核心理念：**这个修复循环应该被自动化，而不是靠人力填补。**

当前 GitHub 19.3K+ Stars。

---

## 四层架构

Opik 的架构是一个完整的工作流：

> Trace → Ollie 诊断 → Ollie 提议修复 → 修复被应用并验证 → 测试套件将此次失败锁定为回归测试 → 回到 Trace

### 第一层：Tracing（追踪）

每个 LLM 调用、工具调用和检索步骤都通过一个装饰器自动埋点：

```python
@opik.track
def my_agent_function(...):
    ...
```

原生支持 LangGraph、CrewAI 及 50+ 框架。每条 trace 记录了当时活跃的 Agent 配置，保证后续复现时能精确重现。

### 第二层：Ollie（诊断+修复 Agent）

**这是关键突破。** 其他可观测性平台到 trace 就停住了。Opik 从 trace 走到修复代码，靠的是内置的编码 Agent **Ollie**。

**无代码访问模式：** Ollie 读取 span 树，识别失败模式，跨所有 LLM 调用解释因果链。你可以问"为什么最终答案忽略了检索到的上下文？"，它会遍历整个 span 树找到根因。

**完整代码修复模式：** 在你的项目根目录运行 `opik connect`，Ollie 获得代码访问权限：
- 读取你的源文件
- 定位有问题的具体代码行
- 生成 diff 供你审批
- 你批准后，Ollie 用原始失败输入重新运行 Agent
- 输出新的 trace，并排对比
- 将原始失败锁定为回归测试用例

> Bad trace → 根因 → diff → 审批 → 重跑 → 回归锁定

### 第三层：Test Suites（测试套件）

大多数评估工作流的做法：构建标注数据集 → 定义数值指标 → 比较浮点数。这种模式对研究者有用，但不符合工程师对质量的理解方式。

Opik 用**自然语言的断言**替代：

```python
assert (
    "The response must include a citation for every factual claim"
)
```

底层通过 LLM-as-a-Judge 机制执行，每个测试用例输出干净的通过/失败。

**关键设计：** 每次调试的失败 trace 自动变成新的测试用例。测试套件来自真实生产故障，而不是预先编写的人造场景——每个循环中，harness 变得越来越难被打破。

### 第四层：Agent Sandbox（沙箱）

大多数 playground 只是提示词 playground——改个 system prompt，重跑一次 LLM 调用。这回答的是错误的问题。

生产环境的真正问题是：**当我改了某个东西，整个 Agent 图会发生什么？**

Opik 的 Agent Sandbox 能在 UI 内端到端运行完整埋点的 Agent。改提示词、换模型、加工具——观察整个系统在完整 span 树上的响应。每次沙箱运行产生一条完整的 Opik trace。非开发干系人（PM、领域专家、QA）可以不碰 git 就能安全测试配置。

---

## 实际运转飞轮

这些层不是独立的功能，而是一个循环：

```
1. 用 @opik.track 埋点
2. 声明 opik.Config
3. 产品环境出问题
4. Ollie 读 trace + 读源码 → 生成修复 diff
5. 你审批
6. Ollie 在 Sandbox 中重跑 Agent（用原始失败输入）
7. 修复通过 → 保存为新 Blueprint
8. 环境指针推向 Staging
9. 原始失败锁定为回归测试
10. 下一个失败的 trace 进入同一个循环
```

**每个循环，harness 变得越来越难被打破。**

---

## 总结

> 到 trace 就结束的可观测性，在 Agent 简单时没问题。一旦进入生产，真正的工作全在 trace 之后的那部分——而 Opik 自动运行了这一部分，而不是把它丢给你。

全部开源。Tracing、Ollie、Test Suites、Agent Sandbox、6 算法 Agent Optimizer、50+ 框架集成。自托管只需三条命令：

```bash
pip install opik
opik init
opik start
```

Cursor 描述的那种手动循环，正是 Opik 自动闭合的——从一个失败的 trace 一路走到一个锁定的回归测试。

---

*整理于 2026-06-14，来源：Akshay 🚀 的 X/Twitter 长文（Comet ML 赞助内容）*
