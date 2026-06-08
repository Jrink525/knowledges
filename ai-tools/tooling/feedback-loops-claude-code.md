---
title: "反馈循环：让 Claude Code 用更少的「保姆式监控」完成复杂任务"
tags:
  - claude-code
  - ai-coding
  - feedback-loops
  - verification
  - code-review
date: 2026-06-06
source: "https://x.com/delba_oliveira/status/2062203743387459836"
authors: "Delba Oliveira (Claude Code @ Anthropic)"
---

# 反馈循环：让 Claude Code 用更少的「保姆式监控」完成复杂任务

> **来源：** [Delba Oliveira 的 X 长文](https://x.com/delba_oliveira/status/2062203743387459836)
>
> Delba 是 Anthropic 的 Claude Code 团队成员，曾在 Vercel 任职。她从实战经验出发，阐述了如何通过建立反馈循环让 Claude Code 自主验证工作成果，从而减少人工干预。

![封面图：Feedback loops 文章配图](../image/feedback-loops-1.jpg)

---

## 核心观点

当我们把越来越复杂的任务交给 Claude 时，Claude 能够**自我验证**（self-verify）其工作成果的能力变得至关重要。

Claude 越是能够自我验证：

- ✅ **越能独立地处理长时间运行的任务**
- ✅ **最终结果的质量越高**
- ✅ **需要的来回沟通越少**

---

## 一、自我验证的现状与边界

> "When checks depend on you, coding sessions become a turn-based game, and you lose what makes agents useful: autonomy."
>
> （当检查依赖于你时，编码会话就变成了回合制游戏，而你会失去智能体最宝贵的特性：自主性。）

好消息是，Claude **已经在**对确定性信号进行自我验证，包括：

- 类型错误（Type errors）
- Lint 错误
- 测试失败
- 运行时错误

随着模型能力的提升，这一能力只会越来越强。

**但 Claude 无法推断的是**你在它响应后手动执行的检查，以及在合并代码前做的那些验证。你能将越多的检查编码化，Claude 的第一次响应就越接近你想要的最终结果。**你花在「保姆式监控」上的时间就越少，Claude 可以持续工作而不需要你守在一旁。**

![自我验证示意图：你离得越远，Claude 自主性越强](../image/feedback-loops-2.jpg)

---

## 二、把你的流程写下来

**出发点很简单：**把你自己或团队已经在做的最佳实践版本写下来。

以前端为例，通常的流程是：

1. 启动开发服务器
2. 打开浏览器
3. 检查控制台错误
4. 像用户一样点击各处，留意布局偏移、导航卡顿等问题

每个领域都有自己的版本。对每个步骤，通常都有 Claude 可以用来验证的工具。

---

## 三、把你的流程编码为技能（Skill）

流程明确后，尽可能将其编码为一个 **Skill**。安装 `skill-creator` 插件，然后让 Claude 采访你：

```bash
/skill-creator Create a skill for verifying frontend changes end-to-end. Interview me about my workflow.
```

如果你不知道如何表述你的流程，可以先让 Claude 展示该领域的最佳实践，看看一个端到端的验证流程应该长什么样。

> **品味和判断难以编码**，但很多检查都有可量化的标准：性能预算、无障碍清单、设计系统规则、好 vs 坏的示例。

### 前端验证 Skill 示例

以下是一个可供 Claude Code 使用的前端验证技能定义：

```markdown
---
name: frontend-verify
description: Verify frontend changes in a browser. Run whenever
a UI (page, component, typography, CSS style) change is made.
---

# Frontend verify

- Run a two-step verification pass in a real browser.
- Fix issues and re-verify before responding to the user.

## Step 1 — Verify the change behaves as expected

1. Open the URL in a browser:
   - In the Claude Code desktop app, use the embedded preview.
   - In the CLI, use the Chrome DevTools MCP.
2. Interact with the new element and confirm it renders and
   behaves as expected.

## Step 2 — Verify the change passes a mobile audit

1. Open the URL in a new page via the Chrome DevTools MCP
2. Run a performance trace and audit Core Web Vitals
```

对于更偏**定性**而非 pass/fail 的检查（比如将数据与历史基线对比），可以和 Claude 一起制定一个评价标准（rubric），用于评估输出质量。

---

## 四、合并前用第二个 Agent 进行代码审查

前面所有步骤都发生在 **Agent 内部的循环中**。在合并前的关键时刻，还存在**第二层验证**——让另一个 Agent 来审查。

**为什么需要第二个 Agent？**

> 新的 Agent 没有写代码的那个 Agent 的偏见。它有自己的上下文，不受前面对话的影响。这种隔离使得审查更客观，能发现第一个 Agent 可能遗漏的问题。

从手动到自动化，有几种选择：

| 方式 | 描述 | 适用场景 |
|------|------|----------|
| **`/review`**（内置 Skill） | 快速单次读取 PR 内容 | 快速检查 |
| **`/code-review`**（插件） | 并行启动多个子 Agent，各自从不同角度读取 diff，对发现进行置信度评分，最终在 PR 上发布结果 | 深度审查 |
| **Claude Code Review**（托管服务） | 通过 GitHub 对每个 PR 自动运行（Team 和 Enterprise 计划提供） | 团队级自动化 |

无论选择哪种，**合并前有一道最后的防线总是有益的**。

---

## 五、整合在一起

至此，你有了**两层验证**：

```
第一层：Claude 在构建时运行的验证                  ← 实时、循环内
第二层：未写代码的 Agent 在合并前执行的审查        ← 独立、合并前
```

两者都属于同一个开发生命周期。回想一下你当前的手动步骤：修改代码 → 收尾清理 → 确认工作正常 → 提交 → 开 PR → 审查 → 观察 CI。

你可以通过**编写一个调用其他 Skill 的 Skill** 将所有步骤整合为一个工作流。

### Claude Code 团队的实战案例

Claude Code 团队在开发功能时运行的一个聚合 Skill，它捆绑了：

1. **`/simplify`** — 清理 diff，使代码更简洁
2. **自定义 `/verify`** — 确认改动端到端工作正常
3. **设计检查** — 如果改动涉及 UI
4. **开 PR 并订阅** — 自动提交并关注 PR 状态
5. **观察 CI 并修复失败** — 持续监控 CI，出现问题立即修复

> 虽然你的工作流可能不同，但核心思想是：**创建反馈循环 + 捆绑 Skill**，让 Claude 能够端到端地验证和执行更多工作。

---

## 总结

| 要点 | 说明 |
|------|------|
| 🎯 **编码化人工检查** | 把你在响应后和合并前手动做的那步检查编码为 Skill |
| 🔄 **循环内验证** | Claude 构建时就能自我验证，减少等待 |
| 👁️ **第二层审查** | 合并前由独立 Agent 审查，消除偏见 |
| 🧩 **Skill 组合** | 用高阶 Skill 调用低级 Skill，形成完整工作流 |
| ⏰ **释放时间** | Claude 自主性越强，你花在「保姆式监控」上的时间越少 |

> **一句话总结：** 把你的验证流程从「人盯着做」变成「Claude 自动跑」，然后让另一个 Claude 在合并前再扫一遍。

---

*整理于 2026-06-06，基于 Delba Oliveira 的 X 长文 [Feedback loops: Help Claude Code complete ambitious tasks with less babysitting](https://x.com/delba_oliveira/status/2062203743387459836)*
