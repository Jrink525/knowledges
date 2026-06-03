---
title: "停止安装 Claude Code 插件——终极指南"
tags:
  - claude-code
  - plugins
  - context-management
  - productivity
  - built-in-features
date: 2026-05-23
source: "https://x.com/regent0x_/status/2057419591618302029"
authors: "regent0x_"
---

# 停止安装 Claude Code 插件——终极指南

> **来源：** [Stop Installing Plugins on Claude Code - The Ultimate Guide](https://x.com/regent0x_/status/2057419591618302029) @regent0x_
> **中文整理：** 根据原文翻译、扩充、结构化

---

## 引子：一个典型的故事

作者曾是"插件狂人"：23 个插件、8 个 skills、5 个 MCP 服务器、3 个自定义 agent 框架…… 结果呢？

- 会话越来越慢
- Context window 被飞快填满
- 连第一个 prompt 都没写，**62,000 tokens 已被消耗**——占了整个 context（200k）的 **31%**

跑了一次 `/context` 才看到真相，然后花了一个周末全部删光。

**结果：** 会话时长从 30 分钟延长到 3 小时以上，输出质量显著提升，Token 消耗减少一半。

核心教训：「Claude Code 内置了完成这么多事情的一切能力。我只是从来不知道它们已经存在了。」

---

## 一、上下文管理（取代 5 个插件）

Context 是 Claude Code 中最宝贵的资源。200k token 窗口里，对话历史、system prompt、工具、文件读取、命令输出都在竞争空间。满了就会遗忘、幻觉、输出垃圾。

### `/context` —— 看清你的 token 去向

在每次重要会话开始时执行。你会看到：

- System prompt 占多少
- Tools/plugins/skills 占多少
- 对话历史占多少
- 还剩多少空间

> **实践经验：** 如果还没做任何事情 baseline 就超过 30k，说明有结构性问题。先修复再工作。

### `/compact` —— 压缩对话而不丢失上下文

这是整个 Claude Code 中最被低估的命令。经验丰富的用户每 20-30 分钟跑一次，大多数人从没用过。

对话越长，每条新消息的成本指数级增长 —— 到第 30 条消息时，单次交互消耗的 token 是第一条的 **31 倍**（因为 Claude 要重读整段历史）。`/compact` 将所有历史压缩为密集摘要，释放空间同时保持关键上下文。

```bash
# 可以指定压缩优先级
/compact focus on the auth module and current test failures
```

> 运行 `/compact` 和不运行的区别：30 分钟 v.s. 3 小时以上的会话持久性。

### `/clear` —— 需要时的核弹级重置

`/clear` 删除所有对话历史，重新开始。文件编辑保留在磁盘上，但 context 完全清空。

**选择原则：**
- `/compact` → 继续工作但需要更多空间
- `/clear` → 切换到完全不相关的任务

> 作者之前装了 2 个插件来做上面三件事的劣质版本，每个还吃掉数千 token 的开销。

---

## 二、会话控制（取代 session 管理插件）

### `/resume` —— 精确恢复上次会话

终端崩溃、笔记本没电、误关窗口 —— 都没关系。

- `/resume` 列出所有近期会话，选择即可精确恢复
- `/name <session-name>` 可以命名会话方便搜索
- 恢复后所有代码状态和对话历史都在

### `/rewind` —— 随时随地撤销任何操作

Claude 把你的 auth 模块改坏了？`/rewind` 回滚到任意之前检查点——代码和对话一起恢复。

### `Esc Esc` —— 隐藏的超能力

- 单次 `Esc`：停止生成（谁都知道）
- 双次 `Esc`：打开一个可滚动的**全部检查点列表**

这个列表包含会话中的每一个状态——每个文件版本、每段对话状态。四个选项：

1. 恢复代码 + 对话
2. 仅恢复对话
3. 仅恢复代码
4. 从检查点向前总结

> 这让实验成本降为零。让 Claude 尝试任何大胆的方案——如果失败了，回滚没有任何代价。

---

## 三、成本与模型控制（取代计费/模型切换插件）

### `/cost` —— 实时查看 API 消耗

使用 API 计费模式时，`/cost` 显示当前会话的实时花费。

对于 Pro/Max 订阅用户，`/stats` 显示 5 小时会话限制和每周使用上限。

### `/model` —— 会话中切换模型

最有价值的省钱技巧，没有之一：

- **Opus** 强大但贵，大约消耗 Sonnet 2 倍的 token
- **Sonnet** 适合 80% 的编码工作——快、能打、性价比高
- **Opus** 只在复杂架构决策和深度调试时才有必要

以前全程开 Opus（格式化文件、写测试、重命名变量），现在：

```
/model switch to sonnet    # 简单任务用 Sonnet
/model switch to opus      # 复杂任务换 Opus
```

### `/effort` —— 控制 Claude 的思考强度

重命名变量和设计数据库 schema 不需要同样的认知投入。`/effort low` 做简单任务 = 更少 token = 更长会话。

### `Option+T` —— 按消息切换扩展思考

Extended thinking 强大但昂贵。`Option+T` 在每个消息级别开关：

- 快速格式化问题 → 关
- 复杂架构决策 → 开
- 简单重命名 → 再关

开关耗时 0.2 秒，菜单路径耗时 4 秒。

---

## 四、项目设置（10 分钟节省数小时）

### `/init` —— 让 Claude Code 自我配置

在项目根目录运行 `/init`，Claude Code 扫描代码库后自动生成 `CLAUDE.md` 启动文件。它会：

- 检测你的技术栈
- 检测文件结构
- 检测编码约定
- 写入每个未来会话都会自动读取的配置文件

之后**自定义它**——添加你的约定、架构决策、规则。

### `/doctor` —— 诊断连接状态

检查 MCP 服务器是否连接、skills 是否加载、权限是否正确。每次配置变更后运行一次。

### `.claudeignore` —— 让垃圾远离 Context

就像 `.gitignore` 防止文件进 Git，`.claudeignore` 防止无关文件消耗 token：

```
# .claudeignore 示例
node_modules/
dist/
*.log
.git/
```

> 每个 Claude 读取的文件都在消耗 token。每个扫描的目录都在占用 context。`.claudeignore` 是保持会话精简的最简单方式——5 行配置取代一个插件。

---

## 五、代码质量（比大多数审查插件更好）

### `/review` —— 内置代码审查

分析近期变更，检查 bug、样式问题、潜在风险，给出改进建议。比直接用 "review my changes" 这种自由 prompt 更精准且更省 token。

### `/diff` —— 显示所有工作区变更

### `/security-review` —— 安全漏洞扫描

> 之前装了一个独立的安全扫描插件——发现 `/security-review` 后立即删除。零额外开销做同样的事。

### `/plan` —— 写代码先思考

Claude 开始写代码、读文件、跑命令之前，`/plan` 让它先生成一个**结构化的执行计划**——但什么都不执行。

这节省了大量的 token，因为你在早期阶段就能发现误解：如果 Claude 计划读取 6 个文件，但实际上只需要 2 个，你在它烧掉 context 去读不需要的文件之前就纠正了。

> 任何复杂任务前切换到 plan 模式。审查计划。调整。再执行。这是精确工作和昂贵试错的差距。

---

## 六、键盘快捷键（最快的方式）

### `Shift+Tab` —— 循环权限模式

Claude Code 对每个文件编辑和命令都请求权限。安全但慢。`Shift+Tab` 在三个模式间循环：

| 模式 | 行为 | 适用场景 |
|------|------|---------|
| Normal | 每步都问 | 安全（慢） |
| Auto-accept | 自动执行 | 快速迭代熟悉代码（快） |
| Plan | 显示计划但不执行 | 高风险操作前预览 |

> 一个键击改变整个交互速度。

### `Ctrl+R` —— 搜索 prompt 历史

跨会话模糊搜索所有历史 prompt。三天前跑过一个完美生效的复杂 prompt？`Ctrl+R`，输入两个关键字，它就回来了。使用一个月后，你的 prompt 历史就是个人最佳实践库。

### `Ctrl+G` —— 在编辑器中写 prompt

终端的单行输入写多段 prompt 很痛苦。`Ctrl+G` 打开默认编辑器（vim、VS Code 等等），写完保存即发送。写详细 prompt 必备。

### `/btw` —— 不中断主任务问旁路问题

Claude 正在深度重构中，你突然需要知道"auth 中间件在哪个文件？"

- 没有 `/btw`：取消整个任务 → 问问题 → 重新 prompt 原任务 → 所有中断工作的上下文丢失
- 有 `/btw`：侧路提问，Claude 继续工作，答案不影响主任务对话历史

---

## 七、自定义命令（30 秒构建你自己的"插件"）

大多数人没意识到：**大多数插件本质上就是带指令的 markdown 文件。** 你可以自己在 `.claude/commands/` 目录下构建完全相同的东西。

```markdown
# .claude/commands/fix-issue.md

You are helping fix issue #{arg}. Follow these steps:
1. Read the issue description
2. Reproduce the bug
3. Write a failing test
4. Fix the code
5. Verify all tests pass
```

现在 `/fix-issue 456` 就变成了一个自定义命令——**零开销、零依赖、零额外 token 消耗。**

```markdown
# .claude/commands/review-pr.md

Review this PR for:
1. Architecture consistency
2. Security vulnerabilities
3. Test coverage
4. Performance implications
...
```

**团队协作：** 把这些文件提交到 repo 的 `.claude/commands/` 目录。全员共享同一套工作流。像对待代码一样对待它们——PR 中 review、迭代、版本化管理。

> 这本质上就是大多数插件商店卖给你的东西。只不过它是免费的，在 context 中零重量，并且你控制每一个字。

---

## 配置悖论

作者揭示了 Claude Code 生态中没人谈论的事实：

> **每个插件、每个 skill、每个 MCP 服务器都在你的 context window 中增加基线开销。** 它们在每次会话开始时被加载，无论你是否使用它们。

Anthropic 官方对规则文件的限制：
- 单个规则文件 ≤ 6,000 字符
- 全部规则合计 ≤ 12,000 字符

官方文档原话："对于每一行，问自己：删除这行会导致 Claude 犯错吗？如果不会——删掉。"

### 作者的转变

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| Baseline token 开销 | **62,000** (31%) | **6,000** (3%) |
| 可用 token 上限 | 138,000 | 194,000 |
| 单次会话时长 | 30 分钟 | 3+ 小时 |

**结论非常简单：** 更少插件 = 更多 context = 更长会话 = 更好输出。

---

## 真正值得安装的三个例外

不是完全禁止安装任何东西。重点是有意识地安装。以下三个幸存者：

### 1. Superpowers（唯一值得的 skills 框架）

结构化的开发方法论，真正改变 Claude 的工作方式。GitHub 17 万+ star。

```
https://github.com/obra/superpowers
```

### 2. Karpathy's 4 Lines（四条行为规则）

四条规则防止 Claude 做假设、过度复杂化、修改未要求的代码、未经验证就提交。GitHub 6 万+ star。

```
https://github.com/forrestchang/andrej-karpathy-skills
```

### 3. Context-Mode MCP（MCP 输出的沙箱）

如果你确实使用 MCP 服务器，这个工具把它们的输出沙箱化，防止原始 JSON 倾倒 10,000 token 到对话中。将工具输出路由到独立的知识库，保持 context 干净。

```
https://github.com/d-e-s-o/claude-context-mode
```

**三个扩展，总开销：约 4,000 token。**

---

## 快速参考卡

| 分类 | 命令/快捷键 | 作用 |
|------|------------|------|
| 📊 上下文 | `/context` | 查看 token 分配 |
| 📊 上下文 | `/compact` | 压缩历史释放空间 |
| 📊 上下文 | `/clear` | 完全重置 |
| 🔄 会话 | `/resume` | 恢复上次会话 |
| 🔄 会话 | `/rewind` | 回滚到检查点 |
| 🔄 会话 | `Esc Esc` | 浏览全部检查点列表 |
| 💰 成本 | `/cost` | 实时 API 花费 |
| 💰 成本 | `/stats` | Pro/Max 限额使用情况 |
| 🤖 模型 | `/model` | 切换模型 |
| 🤖 模型 | `/effort` | 控制思考强度 |
| 🤖 模型 | `Option+T` | 开关扩展思考 |
| 🏗️ 项目 | `/init` | 自动生成 CLAUDE.md |
| 🏗️ 项目 | `/doctor` | 诊断工具连接 |
| 🏗️ 项目 | `.claudeignore` | 排除无关文件 |
| ✅ 质量 | `/review` | 代码审查 |
| ✅ 质量 | `/diff` | 显示变更 |
| ✅ 质量 | `/security-review` | 安全扫描 |
| ✅ 质量 | `/plan` | 生成执行计划 |
| ⌨️ 快捷键 | `Shift+Tab` | 循环权限模式 |
| ⌨️ 快捷键 | `Ctrl+R` | 搜索 prompt 历史 |
| ⌨️ 快捷键 | `Ctrl+G` | 编辑器中写 prompt |
| ⌨️ 快捷键 | `/btw` | 旁路提问不中断任务 |
| 🛠️ 自定义 | `.claude/commands/` | 自定义 slash 命令 |

---

## 总结

- **Claude Code 内置了绝大多数人安装插件来完成的能力**——/context, /compact, /resume, /rewind, /plan, /review, /model……全部免费，零 overhead
- 每个插件、skill、MCP 服务器都增加 context 基线开销
- 检查自己的 context baseline：`/context`，如果 > 30k 就需要清理
- 自定义命令 `~/.claude/commands/` 可以取代大部分插件
- 真正安装前问自己：**"Claude Code 是否已经内置了这个功能？"**

---

*Processed on 2026-05-23 from https://x.com/regent0x_/status/2057419591618302029*
