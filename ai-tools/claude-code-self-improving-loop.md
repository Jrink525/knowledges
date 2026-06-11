---
title: "在 Claude Code 中构建自我改进循环（完整配置）"
tags:
  - claude-code
  - hooks
  - ai-tools
  - workflow
date: 2026-06-11
source: "https://x.com/0x_rody/status/2064728139314389073"
authors: "rody (@0x_rody)"
---

# 在 Claude Code 中构建自我改进循环（完整配置）

> **来源：** [How to Build a Self-Improving Loop in Claude Code (Exact Setup Inside)](https://x.com/0x_rody/status/2064728139314389073)

---

## 痛点

Claude 写了代码，交给你，然后 3 个测试挂了。

你把报错粘回去，它修了一个 bug、又搞坏另一个，你整个晚上就成了 Claude 和终端之间的传话筒。

大多数开发者接受了这种工作流。

**但正确的解法是一个循环：Claude 自己检查自己的工作，重试直到全部通过，你不再夹在中间。**

---

## 循环如何运作

默认的 Claude Code 流程是一条直线：你提问 → Claude 写代码 → Claude 停止。代码能不能跑是你的事。

循环把直线变成了圆圈：Claude 写代码 → 运行检查 → 看哪里失败 → 修复 → 再跑检查。它只会在两种情况下停止：
- **全部通过**
- **达到重试上限**，然后精确报告哪些还坏了

你从"传话筒"变成了"审查者"。整套配置只需要 **3 个文件**。

---

## 文件 1：CLAUDE.md — 循环协议

告诉 Claude "完成"意味着"已验证"，而不是"已写完"。放入项目根目录：

```markdown
## Loop protocol

Every task runs as a loop, not a line:

1. Write the change.
2. Run the checks: tests, linter, type checker.
3. If anything fails, read the error, fix the cause, go back to step 2.
4. Repeat up to 5 times.

Stop conditions:
- All checks pass: report "done" with the passing output as proof.
- 5 attempts used: stop and report what still fails and what you tried.
- Same error appears twice in a row: stop. You're guessing, not fixing.

Never report "done" without check output from this session.
Never fix a test by weakening it. Fix the code, not the test.
```

> **最重要的一句：** `Never fix a test by weakening it. Fix the code, not the test.`
> 没有这句话，Claude 最终会通过"删除断言"来"通过"测试。
> **循环的目标是改进代码，不是改进记分牌。**

---

## 文件 2：.claude/settings.json — 闭环的 Hook

协议只是"请求"Claude 自我检查。这段配置让协议变成**物理强制**。

放入 `.claude/settings.json`：

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "npm test --silent 2>&1 | tail -20" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "npx tsc --noEmit --pretty false 2>&1 | head -10" }
        ]
      }
    ]
  }
}
```

### 两个 Hook 各自的作用

| Hook | 时机 | 作用 |
|------|------|------|
| **PostToolUse** | 每次编辑完成后 | 把类型错误实时反馈回去，Claude 在任务中途就能自我修正 |
| **Stop** | Claude 试图结束时 | 运行测试套件，失败的输出直接送回当前会话，循环协议强制它再来一轮，而不是假装"做完了" |

### 其他语言适配

| 语言 | PostToolUse（类型检查） | Stop（测试） |
|------|------------------------|-------------|
| **TypeScript** | `npx tsc --noEmit` | `npm test --silent` |
| **Python** | `pyright` | `pytest -q` |
| **Rust** | `cargo check` | `cargo test --quiet` |

---

## 文件 3：.claude/agents/fixer.md — 备用修复 Agent

对于顽固的失败，一个**全新上下文**的独立 Agent 比第 5 次重试效果好得多。

放入 `.claude/agents/fixer.md`：

```yaml
---
name: fixer
description: Invoke when the same test keeps failing after 2 fix attempts. Diagnoses the root cause before touching code.
tools: Read, Edit, Grep, Glob, Bash
model: opus
---

You fix failing checks. You are not allowed to guess.

1. Run the failing check yourself. Read the full error.
2. Read every file in the failure path, end to end.
3. Write one sentence: what is the actual cause.
4. Fix that cause only. No drive-by refactoring.
5. Run the check again. Report before/after output.

Forbidden: deleting tests, loosening assertions, adding try/catch
to silence errors, marking tests as skipped.
```

主会话在循环卡住时调用 `@fixer`。一个没有失败包袱的干净上下文窗口，能解决第 4 次重试解决不了的问题。

---

## 常见错误

### ❌ 没有重试上限
没有"最多 5 次"的限制，Claude 可以在一个错误上烧掉一小时。上限把无限循环变成了可读的报告。

### ❌ 测试跑得太慢
如果测试套件要 90 秒，每次迭代都像爬一样。让 Stop Hook 只跑单元测试，集成测试留给 CI。

### ❌ 让 Claude 在循环中修改测试
**这是最大的作弊路径**。协议禁止它，但建议还是检查 diff，看有没有碰测试文件。

### ❌ 没有"连续两次相同错误"的规则
连续两次一模一样失败 → Claude 在猜。这时该用 `@fixer` 或让你接手，而不是第 3 次重试。

---

## 5 分钟设置

- **1 分钟**：把循环协议复制到 `CLAUDE.md`
- **2 分钟**：把 hooks 添加到 `.claude/settings.json`
- **1 分钟**：创建 `.claude/agents/fixer.md`
- **1 分钟**：给 Claude 一个真实任务，观察循环运行：写 → 失败 → 修复 → 通过

你不再需要做 Claude 和终端之间的传话筒了。

**模型并没有变聪明。它只是不再被允许提前退出了。**

---

## 关键 Insight

这个模式的核心哲学可以概括为：

1. **协议（CLAUDE.md）** 定义了"完成"的标准——不是写了就算完成，而是通过了验证才算
2. **物理强制（Hooks）** 把协议变成了不可绕过的门禁——想停？先过测试
3. **独立 Agent（@fixer）** 解决了"同一上下文越修越乱"的问题

你从"修复代码的人"变成了"审查结果的人"。这是 AI 辅助开发中一个很有意义的分工进化。

---

*Processed on 2026-06-11 from [X article by @0x_rody](https://x.com/0x_rody/status/2064728139314389073)*
