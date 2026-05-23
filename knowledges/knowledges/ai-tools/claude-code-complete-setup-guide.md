---
title: "Claude Code 完全配置指南：.claude 目录解剖到 Token 优化"
tags:
  - Claude Code
  - AI 编程助手
  - CLAUDE.md
  - 开发工作流
  - Token 优化
  - 钩子系统
  - Subagents
date: 2026-05-14
source: "https://x.com/akshay_pachaar/status/2035341800739877091 + https://github.com/drona23/claude-token-efficient + https://levelup.gitconnected.com/i-spent-6-months-tuning-claude-code-heres-the-exact-setup-that-finally-worked-b41c67628478"
authors: "Akshay 🚀 (@akshay_pachaar), Anubhav (@anubhavgoyal101), Drona Gangarapu (@drona23)"
---

# Claude Code 完全配置指南：.claude 目录解剖到 Token 优化

> 本文整合了三份高质量 Claude Code 配置资源：
> - **Akshay 🚀** — 《.claude/ 目录解剖》- .claude 目录的完整指南
> - **Anubhav** — 《6 个月调教 Claude Code 的最终配置》- 实战级配置栈
> - **Drona Gangarapu** — 《claude-token-efficient》- Token 优化 CLAUDE.md

---

## 一、概览：两个 .claude 目录

Claude Code 实际上有**两个** `.claude` 目录：

| 位置 | 用途 | Git 提交? |
|------|------|-----------|
| `./.claude/`（项目级） | 团队配置、共享规则、钩子 | ✅ 提交 |
| `~/.claude/`（全局） | 个人偏好、会话历史、自动记忆 | ❌ 不提交 |

项目级目录存放团队共享配置。全局目录存放个人偏好和机器本地状态。

> 一个被充分配置的 `.claude/` 目录大致如下：
>
> ```
> .claude/
> ├── CLAUDE.md              # 核心指令（最关键）
> ├── CLAUDE.local.md        # 个人覆盖（自动 .gitignore）
> ├── settings.json          # 权限、钩子、配置
> ├── settings.local.json    # 个人权限覆盖
> ├── rules/                 # 模块化规则文件
> │   ├── code-style.md
> │   ├── testing.md
> │   └── api-conventions.md
> ├── agents/                # 专业子代理
> │   ├── code-reviewer.md
> │   └── security-auditor.md
> ├── skills/                # 可复用的工作流
> │   └── security-review/
> │       ├── SKILL.md
> │       └── DETAILED_GUIDE.md
> ├── hooks/                 # 钩子脚本
> │   ├── bash-firewall.sh
> │   └── auto-format.sh
> └── .mcp.json              # MCP 服务器配置
> ```

---

## 二、CLAUDE.md — Claude 的指令手册

### 2.1 核心原则

**这是整个系统最重要的文件。** Claude Code 启动时，第一件事就是读取 CLAUDE.md 并加载到系统提示词中。

> **简单说：你在 CLAUDE.md 里写什么，Claude 就遵循什么。**

### 2.2 该写什么

| ✅ 写 | ❌ 别写 |
|------|---------|
| 构建/测试/检查命令 (`npm run test`, `make build`) | 属于 linter/formatter 配置的内容 |
| 关键架构决策（"我们使用 Turborepo 管理 monorepo"） | 已可链接的完整文档 |
| 不明显的坑（"TypeScript strict mode 开启，未使用变量视为错误"） | 长篇大论的解释理论 |
| 导入约定、命名模式、错误处理风格 | |
| 主要模块的文件和目录结构 | |

> **保持 CLAUDE.md 在 200 行以内。** 超过这个长度会消耗过多上下文，且 Claude 的指令遵循度反而下降。

### 2.3 最小但有效的示例

```markdown
# Project: Acme API

## Commands
npm run dev          # Start dev server
npm run test         # Run tests (Jest)
npm run lint         # ESLint + Prettier check
npm run build        # Production build

## Architecture
- Express REST API, Node 20
- PostgreSQL via Prisma ORM
- All handlers live in src/handlers/
- Shared types in src/types/

## Conventions
- Use zod for request validation in every handler
- Return shape is always { data, error }
- Never expose stack traces to the client
```

### 2.4 CLAUDE.local.md — 个人覆盖

创建 `CLAUDE.local.md` 放在项目根目录。Claude 会同时读取主 CLAUDE.md 和这个文件，且它会被自动 `.gitignore`。

适用场景：你个人偏好的测试运行器、特定的文件打开模式等。

### 2.5 多级联读（全局 + 项目 + 子目录）

Claude 会按层级合并读取多个 CLAUDE.md：

```
~/.claude/CLAUDE.md           # 全局：所有项目通用（个人偏好、风格）
├── project/CLAUDE.md         # 项目级：团队配置
│   └── src/api/CLAUDE.md     # 子目录级：目录特定规则
```

---

## 三、rules/ 文件夹 — 模块化规则

当团队增长后，200 行的 CLAUDE.md 会变得难以维护。`rules/` 文件夹解决了这个问题。

**`.claude/rules/` 下的每个 markdown 文件都会自动加载到会话中。** 按关注点拆分：

```
.claude/rules/
├── code-style.md
├── testing.md
├── api-conventions.md
└── security.md
```

### 3.1 路径限定规则（高级功能）

通过 YAML frontmatter 指定规则只在特定路径下生效：

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "src/handlers/**/*.ts"
---
# API Design Rules

- All handlers return { data, error } shape
- Use zod for request body validation
- Never expose internal error details to clients
```

Claude 在编辑 React 组件时不加载此文件，只有在处理 `src/api/` 或 `src/handlers/` 下的文件时才激活。

---

## 四、钩子系统 — 确定性行为控制

CLAUDE.md 指令是**建议性的**——Claude 大多数时候遵循，但不是每次都遵循。**钩子（Hooks）让行为变成确定性的。**

钩子是在 Claude 工作流程中特定点自动触发的事件处理器。Shell 脚本每次都会运行，没有例外。

### 4.1 支持的钩子事件

| 事件 | 触发时机 | 典型用途 |
|------|---------|---------|
| `PreToolUse` | 任何工具运行前 | 安全门、阻止危险命令 |
| `PostToolUse` | 工具成功后 | 格式化代码、运行检查 |
| `Stop` | Claude 完成时 | 质量门（测试必须通过） |
| `UserPromptSubmit` | 用户按下回车时 | 提示词验证 |
| `Notification` | — | 桌面通知 |
| `SessionStart/SessionEnd` | 会话开始/结束时 | 上下文注入/清理 |

### 4.2 配置示例

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write 2>/dev/null"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/bash-firewall.sh" }
        ]
      }
    ]
  }
}
```

### 4.3 关键细节

- **退出码 2** 是唯一阻止执行的状态码。退出 0 = 成功，退出 1 = 非阻塞错误。最常见的错误就是用退出码 1 来做安全钩子（它只会记录错误，什么也不做）。
- `matcher` 字段使用正则匹配工具名：
  - `"Write|Edit|MultiEdit"` → 文件变更
  - `"Bash"` → Shell 命令
  - 省略 → 匹配所有工具
- **钩子不会热重载**，需要在会话启动前生效。
- **PostToolUse 不能撤销**操作（工具已经运行），用 PreToolUse 来阻止动作。
- 钩子对所有子代理操作也递归触发。
- **始终引用 shell 变量、验证 JSON 输入、使用绝对路径。**

---

## 五、Skills/ 文件夹 — 按需可复用工作流

技能（Skills）是 Claude 可以根据上下文自动调用的工作流。

每个技能在自己的子目录中有 `SKILL.md`：

```
.claude/skills/
├── security-review/
│   ├── SKILL.md
│   └── DETAILED_GUIDE.md
└── deploy/
    ├── SKILL.md
    └── templates/
        └── release-notes.md
```

### SKILL.md 示例

```markdown
---
name: security-review
description: Comprehensive security audit. Use when reviewing code for
  vulnerabilities, before deployments, or when the user mentions security.
allowed-tools: Read, Grep, Glob
---
Analyze the codebase for security vulnerabilities:

1. SQL injection and XSS risks
2. Exposed credentials or secrets
3. Insecure configurations
4. Authentication and authorization gaps

Report findings with severity ratings and specific remediation steps.
Reference @DETAILED_GUIDE.md
```

> **技能 vs 命令的关键区别：** 技能可以打包附带文件，`@DETAILED_GUIDE.md` 引用了一个紧邻 SKILL.md 的文档。命令是单文件，技能是包。

个人技能放在 `~/.claude/skills/`，跨项目可用。

---

## 六、Agents/ 文件夹 — 专业子代理

当任务复杂到需要专业分工时，在 `.claude/agents/` 中定义子代理。

每个代理是一个 markdown 文件，有自己的系统提示词、工具权限和模型偏好：

```
.claude/agents/
├── code-reviewer.md
└── security-auditor.md
```

### 示例：code-reviewer.md

```markdown
---
name: code-reviewer
description: Expert code reviewer. Use PROACTIVELY when reviewing PRs,
  checking for bugs, or validating implementations before merging.
model: sonnet
tools: Read, Grep, Glob
---
You are a senior code reviewer with a focus on correctness and maintainability.

When reviewing code:
- Flag bugs, not just style issues
- Suggest specific fixes, not vague improvements
- Check for edge cases and error handling gaps
- Note performance concerns only when they matter
```

> **关键设计原则：** `tools` 字段限制代理能做什么。安全审计员只需要 `Read, Grep, Glob`——它没理由写文件。`model` 字段允许对专注型任务使用更便宜、更快的模型（如 Haiku），保留 Sonnet/Opus 给真正需要它们的任务。

个人代理放在 `~/.claude/agents/`，跨项目可用。

---

## 七、settings.json — 权限和项目配置

`settings.json` 控制 Claude 允许做什么、被禁止做什么，以及钩子配置的位置。

### 完整示例

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Read",
      "Write",
      "Edit"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(curl *)",
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

### 权限三档

| 列表 | 行为 |
|------|------|
| `allow` | 直接执行，无需确认 |
| `deny` | 完全阻止，无论什么情况 |
| 不在任一列表 | Claude 执行前先询问 |

> 第三档（询问）是有意为之的安全网——不必预判所有危险命令，但也不会完全敞开。

### settings.local.json

与 `CLAUDE.local.md` 相同的概念。创建 `.claude/settings.local.json` 存放你不想提交的个人权限变更。自动 `.gitignore`。

---

## 八、全局 ~/.claude/ 目录

| 文件/目录 | 用途 |
|-----------|------|
| `~/.claude/CLAUDE.md` | 全局指令，加载到每个会话 |
| `~/.claude/projects/` | 会话记录和每项目自动记忆 |
| `~/.claude/commands/` | 个人命令 |
| `~/.claude/skills/` | 个人技能 |
| `~/.claude/agents/` | 个人代理 |

> 自动记忆（Auto-memory）：Claude Code 会自己记笔记——发现的命令、观察到的模式、架构洞察。这些跨会话持久化。可以用 `/memory` 浏览和编辑。知道这个存在很有用——比如当 Claude "记得"你从没告诉过它的事，或者你想清空某个项目的自动记忆重新开始时。

---

## 九、Token 效率优化（来自 claude-token-efficient）

### 9.1 问题：默认输出太啰嗦

Claude 默认行为：
- 每条回复开头"Sure!"、"Great question!"、"Absolutely!"
- 结尾"I hope this helps! Let me know if you need anything!"
- 使用破折号、智能引号等 Unicode 字符（破坏解析器）
- 在回答前复述你的问题
- 添加未经请求的建议
- 过度工程化代码
- 同意错误陈述（"You're absolutely right!"）

**所有这些都在浪费 Token，没有增加价值。**

### 9.2 实测效果

| 测试 | 基线 | 优化后 | 减少 |
|------|------|--------|------|
| 解释 async/await | 180 词 | 65 词 | 64% |
| 代码审查 | 120 词 | 30 词 | 75% |
| 什么是 REST API | 110 词 | 55 词 | 50% |
| 幻觉纠正 | 55 词 | 20 词 | 64% |
| **总计** | **465 词** | **170 词** | **63%** |

### 9.3 优化 CLAUDE.md

```markdown
# Problem
1. Starts coding without context → Think first; read files before writing
2. Verbose responses → Keep output concise
3. Rewrites large files unnecessarily → Prefer targeted edits
4. Re-reading the same files → Read each file once unless it changed
5. Declaring done without validation → Run tests before finishing
6. Sycophantic chatter → No flattering preamble/closing fluff
7. Over-engineered solutions → Favor simple direct fixes
8. Prompt conflict confusion → User instructions always override
```

### 9.4 典型对比

**Without CLAUDE.md — Code Review:**
> *"Great question! I can see you're working with a loop. Let me take a look at that. That's a thoughtful piece of code! However, I notice there's actually a subtle bug here that's worth pointing out. The condition i <= arr.length should be i < arr.length. Using <= means the loop will run one extra iteration... You might also want to consider using modern array methods like forEach, map, or for...of which are cleaner... Great catch on reviewing this - it's always good practice to double-check loop boundaries! I hope this review was helpful. Feel free to share more code anytime!"*
→ **120 词**

**With CLAUDE.md — Same prompt:**
> *Bug: <= causes an off-by-one error. On the final iteration arr[arr.length] is undefined.*
> *Fix: for (let i = 0; i < arr.length; i++)
> → **30 词，75% 更少 Token，同一条修复**

### 9.5 成本节约估算

| 使用量 | 节省 Token/天 | 月省（Sonnet） |
|--------|-------------|---------------|
| 100 提示/天 | ~9,600 tokens | ~$0.86 |
| 1,000 提示/天 | ~96,000 tokens | ~$8.64 |
| 3 个项目合计 | ~288,000 tokens | ~$25.92 |

> **⚠️ 诚实说明：** CLAUDE.md 文件本身在每条消息中消耗输入 Token。节省来自减少的输出 Token。只有在输出量足够高、抵消了持续的输入成本时，净收益才为正。低使用量场景下反而可能增加成本。

### 9.6 实战验证

在 3 个编码挑战（CSV 报告器、SQLite 窗口函数、Hono WebSocket 计数器）上的独立基准测试：

| 挑战 | v8 优化后 | 聊天粘贴规则 | 节省 |
|------|-----------|------------|------|
| CSV 报告器 | $0.244 | $0.274 | - |
| SQLite 窗口函数 | $0.406 | $0.459 | - |
| WebSocket 计数器 | $0.285 | $0.585 | 最强！|
| **总计** | **$0.935** | **$1.131** | **-17.4%** |

两种方式都通过所有测试。**文件方式在重复任务中成本更低。**

### 9.7 场景适配

| 场景 | 推荐方案 |
|------|---------|
| 日常开发、代码审查 | CLAUDE.md 文件 |
| 一次性快速任务 | 聊天粘贴规则 |
| 自动化管道/代理循环 | CLAUDE.md 文件（节约最显著） |
| 单次简短查询 | 不值得（输入成本 > 节省） |
| 探索/架构讨论 | 用覆盖规则按需要详细输出 |

### 9.8 配置方案选择

| 方案 | 策略 | 工具预算 | 适用场景 |
|------|------|---------|---------|
| v5 | 多文件结构化 | 50 次调用 | 复杂项目，需要详细工作流规则 |
| v6 | 一次性执行 | 50 次调用 | 应单次完成的任务 |
| v8 | 超精简最小轮次 | 20 次调用 | 成本敏感的管道 |

### 9.9 快速开始

**方式 A — 项目级（推荐）：**
```bash
curl -o CLAUDE.md https://raw.githubusercontent.com/drona23/claude-token-efficient/main/CLAUDE.md
```

**方式 B — 克隆并按需选择配置：**
```bash
git clone https://github.com/drona23/claude-token-efficient
cp claude-token-efficient/profiles/CLAUDE.coding.md your-project/CLAUDE.md
```

**方式 C — 聊天中粘贴（一次性会话）：**
```
Rules: Read files first. Write complete solution. Test once. No over-engineering.
```

---

## 十、完整目录结构总览

```
your-project/
├── CLAUDE.md                  # 团队指令（提交）
├── CLAUDE.local.md            # 个人覆盖（忽略）
│
└── .claude/
    ├── settings.json          # 权限、钩子、配置（提交）
    ├── settings.local.json    # 个人权限覆盖（忽略）
    │
    ├── hooks/                 # 钩子脚本
    │   ├── bash-firewall.sh   # PreToolUse: 阻止危险命令
    │   ├── auto-format.sh     # PostToolUse: 格式化编辑的文件
    │   └── enforce-tests.sh   # Stop: 确保测试通过再结束
    │
    ├── rules/                 # 路径限定的规则文件
    │   ├── code-style.md
    │   ├── testing.md
    │   └── api-conventions.md
    │
    ├── agents/                # 子代理定义
    │   ├── code-reviewer.md
    │   └── security-auditor.md
    │
    ├── skills/                # 技能工作流
    │   └── security-review/
    │       ├── SKILL.md
    │       └── DETAILED_GUIDE.md
    │
    └── .mcp.json              # MCP 服务器配置
```

---

## 十一、渐进式入门路径

**Step 1:** 在 Claude Code 中运行 `/init`。它会读取你的项目生成初始 CLAUDE.md。精简到必要内容。

**Step 2:** 添加 `.claude/settings.json`，配置 allow/deny 规则。至少允许运行命令，禁止读取 `.env`。

**Step 3:** 为最常用的工作流创建 1-2 个命令。代码审查和问题修复是很好的起点。

**Step 4:** 随着项目增长，CLAUDE.md 变得臃肿时，开始拆分为 `.claude/rules/` 文件。合理使用路径限定。

**Step 5:** 添加 `~/.claude/CLAUDE.md` 存放个人偏好。

**Step 6（可选）:** 添加 token 优化 CLAUDE.md 减少输出开销。

> **核心洞见：** .claude/ 目录实际上是一个"协议"——告诉 Claude 你是谁、你的项目做什么、该遵循什么规则。你定义得越清晰，纠正 Claude 的时间就越少，做有用工作的时间就越多。
>
> **CLAUDE.md 是你最高杠杆的文件。先把这个搞定，其他都是优化。**

---



## 十二、Anubhav 的八层配置栈（完整版）

> 以下内容来自 Anubhav 在 *I Spent 6 Months Tuning Claude Code. Here's the Exact Setup That Finally Worked* 中的完整实战框架。以一个 citation-RAG 服务项目为例，逐步拆解从零到 headless CI 的配置栈。

Anubhav 的核心观点：大多数开发者使用 Claude Code 时只接触了 20% 的功能——一个单薄的 CLAUDE.md 文件。**剩下 80% 的产能在地板上。**

一个充分配置的 power user 目录结构：

```
.claude/
├── CLAUDE.md
├── rules/
│   ├── langgraph.md
│   ├── retrieval.md
│   ├── tests.md
│   └── python-types.md
├── agents/
│   ├── retrieval-reviewer.md
│   ├── prompt-auditor.md
│   └── eval-runner.md
├── skills/
│   ├── new-rag-eval/
│   │   └── SKILL.md
│   └── claude-pr-checklist/
│       └── SKILL.md
├── settings.json
└── .mcp.json
```

每份文件都不长。主记忆文件刻意保持在 500 token 以下。每个 rules 文件是简短的路径限定行为。每个子代理大约三十行。settings 中的钩子配置只包含一个 pre-tool 门控和一个 post-tool 格式化器。服务器配置只有五个而不是十五个。

两位工程师接手同一个任务：给现有检索服务添加引用来源的答案生成，编写评估，并以 PR 形式提交到主分支。

一位工程师有空的文件夹，另一位有上述完整目录结构和 headless 模式。前者花了一个下午做出一项功能并在傍晚发布。**后者在 30 分钟内交付了一个 PR。** 差异不在他们输入的提示词，而在一套没人花时间搭建的配置栈。

先从记忆文件开始，因为这一层做对了，其他所有层的代价都更低。

### 12.1 层 1：记忆层级（Memory Hierarchy）

Claude Code 有五级记忆：

1. **家目录偏好**（`~/.claude/CLAUDE.md`）
2. **项目根目录文件**（`CLAUDE.md`）
3. **路径限定规则**（`.claude/rules/`）
4. **本地未提交覆盖**（`CLAUDE.local.md`）
5. **自动记忆工具写入**（auto-memory）

项目根文件在每次会话启动时加载，它永久消耗 token。许多团队把整套工程 wiki 塞进这个文件，像向量数据库而不是热缓存。

**关键发现：** 在 Anubhav 的实际工作负载中，超过 ~500 token 后，缓存命中率明显下降。Opus 4.7 的 tokenizer 将相同内容映射到约 1.0–1.35× 更多 token——如果你不严格控制上下文，相同工作现在更贵了。

**规则：**
- 保持在 **200 行以内**
- 保持**命令式**风格
- 不要写 "write clean code" 这样描述性的建议
- 写字面规则，如 "all functions must have TypeScript type annotations"
- **每一行必须实际改变行为**

#### 最小有效的 CLAUDE.md（RAG 服务示例）

```markdown
# citation-rag
Retrieval + answer-generation service. LangGraph-based pipeline,
PostgreSQL+pgvector retrieval, Gemini answer generation, eval harness
in `evals/`.

## Layout
- `services/retrieval/` — chunking, embedding, reranker, citation packer
- `services/answer/` — prompt templates, generator node, guardrails
- `shared/` — schemas, tracing, settings
- `evals/` — golden sets, runners, scoring

## Build & test
- Install: `uv sync`
- Unit tests: `uv run pytest -q`
- Eval harness: `uv run python -m evals.run --suite citations`
- Lint + types: `uv run ruff format . && uv run mypy .`

## Canonical conventions
- The canonical answer prompt lives at `services/answer/prompts/v4.md`.
  Do not edit `v3.md` because it is frozen for regression evals.
- All LLM outputs are validated with the pydantic models in
  `shared/schemas/answers.py`. No raw dict returns from generator nodes.
- Retrieval always returns `Chunk` objects with a `citation_id`.
  The answer node must emit citations using those exact ids.

## Guardrails (Claude: follow these literally)
- Never bump the model version string without updating
  `evals/snapshots/<version>.json` in the same commit.
- Never introduce network calls inside `tests/unit/`. Use fixtures in
  `tests/fixtures/` and the fakes in `tests/fakes/`.
- Prefer editing existing modules over adding new top-level packages.
- If a change touches `services/retrieval/`, read `.claude/rules/retrieval.md`
  before planning.
- Keep functions under ~40 lines. Split by responsibility, not by length.

## Before opening a PR
- Run the eval harness and attach the diff output to the PR body.
- Update `CHANGELOG.md` under `## Unreleased`.
- Use the `claude-pr-checklist` skill.
```

这份文件告诉代理目录做什么，定义检索节点和答案节点之间的严格引用契约，建立防止模型幻觉 mock 的硬性护栏。

### 12.2 层 2：路径限定规则（Path-Scoped Rules）

在整理了根记忆文件后，你仍然有文件特定的指令。通过路径限定规则实现。

**模式：** 使用 YAML frontmatter。定义一个 glob 路径数组。工具仅在接触匹配文件时加载规则文件。**其余时间成本为零。**

> ⚠️ **已知问题：** 虽然 `paths:` 是文档中的 schema 键，但当前版本有时会因 bug 丢弃它。如果发现规则被静默忽略，使用 `globs:` 或 CSV 格式更可靠。

检索服务的规则文件：

```yaml
---
name: retrieval-rules
description: Conventions for services/retrieval/**. Loaded only when
 Claude is editing or planning changes inside the retrieval service.
globs:
  - "services/retrieval/**"
  - "tests/retrieval/**"
---
# Retrieval service rules

## Chunking
- Use `shared/chunking.semantic_chunker` for all document ingest.
  Do not introduce a second chunker without updating the eval snapshot.
- Chunk size target: 512 tokens, 64 overlap. Changes require an ADR.

## Reranker
- The reranker interface is `services/retrieval/reranker.Reranker`.
  New backends must implement it, not parallel it.
- Never rerank more than the top 50 hits from vector search. Rerank latency
  is the #1 service SLO risk.

## Citations
- Every `Chunk` returned from retrieval must carry a stable `citation_id`.
- Citation ids are produced by `shared/citations.make_citation_id`. Do not
  hand-roll ids anywhere else.
- The answer node assumes `citation_id` is URL-safe. Do not change that
  without updating `services/answer/citation_packer.py` in the same diff.

## Tests
- Unit tests for retrieval must never hit the embedding API. Use the fake
  embedder in `tests/fakes/embeddings.py`.
- Integration tests live under `tests/retrieval/integration/` and are
  opt-in via `pytest -m integration`.
```

三四个简短的规则文件胜过一个大根文件。token 节省在对话的每一轮叠加。

### 12.3 层 3：Plan Mode（计划模式）

大多数人从未在生产中使用 Plan Mode。他们输入提示词，然后看着文件立即变更。

**Plan Mode 将思考与执行分离。** 它保持探索在主执行上下文之外，生成一份你可以审查并修改的可执行计划文档，在破坏性操作发生之前。

三个计划层级：

| 层级 | 适用场景 |
|------|---------|
| **Simple Plan** | 简短任务，单个文件 |
| **Visual Plan** | 多文件变更，结构重要 |
| **Deep Plan** | 多服务变更，风险重构 |

**Deep Plan 使用子代理做风险评估和架构审查。** 计划子代理设计为只读——明确拒绝写和编辑权限。它不会在映射依赖关系时意外改变你的代码库。

使用流程：
1. explore 子代理将相关文件拉入简短的上下文
2. planner 输出显式的编辑列表、评估添加项，并草拟 PR 描述
3. 你审查并锁定计划
4. 退出 Plan Mode 后才执行实际变更

### 12.4 层 4：自定义子代理（Custom Subagents）

**子代理是整个工具中最未被充分利用的功能。**

已经内置：explore（只读搜索）、general-purpose（多步工作）、code-reviewer、code-architect。

**何时编写自定义子代理：**
- 任务频繁重复
- 需要特定工具限制的角色
- 特定系统提示词与主配置冲突

#### 检索审查器（Retrieval Reviewer）示例

```yaml
---
name: retrieval-reviewer
description: Reviews changes under services/retrieval/ for chunking,
 reranker, and citation-contract regressions. Read-only. Invoke
 proactively before opening a PR that touches retrieval code.
tools: Read, Grep, Glob, Bash(git diff:*), Bash(uv run pytest:*)
model: sonnet
---
You are a retrieval-service reviewer for the citation-rag repo.

Scope:
- Only review files under `services/retrieval/**` and their tests.
- Do not comment on unrelated files even if they appear in the diff.

Review checklist, in order:
1. Chunking: does the change respect the 512/64 target, and does it keep
   `shared.chunking.semantic_chunker` as the single entry point?
2. Reranker: if the reranker interface changed, is every implementation
   updated, and is the top-k cap still ≤ 50?
3. Citations: every returned `Chunk` must have a `citation_id` produced
   by `shared.citations.make_citation_id`. Flag any hand-rolled ids.
4. Tests: no new network calls in unit tests. Integration tests gated
   by `pytest -m integration`.
5. Eval impact: if behavior changed, confirm `evals/snapshots/*.json`
   has been regenerated in the same commit.

Output format:
- A short "Verdict" (pass / needs-changes / blocker).
- Bullet list of findings, each with the file path and a one-line fix.
- Do not suggest unrelated refactors.
```

**设计洞察：** `tools` 行是一个狭窄的 allowlist，仅授予读访问和限定范围的 bash 执行。`model: sonnet` 将子代理降级到更便宜的模型。主循环保留在昂贵模型上做硬推理，子代理在后台廉价运行。

#### Eval-Runner 技能（Skill）示例

```yaml
---
name: new-rag-eval
description: Support a new RAG eval case from a golden example, wire it
 into the eval harness, run it against the current pipeline, and write
 a result summary. Use when the user asks to "add an eval for ..."
 or "cover this regression with an eval."
allowed-tools: Read, Write, Edit, Bash(uv run:*), Bash(git add:*)
---
# new-rag-eval

## When to use
Trigger when the user wants to add a new eval case to
`evals/suites/citations/` or reproduce a regression in the eval harness.

## Inputs to gather first
1. A natural-language description of the query.
2. The expected citation ids (or the expected answer text).
3. Optional: the failing trace id from production.

## Steps
1. Read `evals/templates/case.json` — this is the case template.
2. Ask the user for the query, expected citations, and any notes.
3. Write a new case file at `evals/suites/citations/<slug>.json` using
   the template. Slug is kebab-case from the query.
4. Run the harness for just this case:
   `uv run python -m evals.run --suite citations --case <slug>`
5. Parse the JSON output at `evals/out/<slug>.json`. Summarize:
   - pass / fail
   - grounded-citation rate
   - unsupported-claim rate
   - any new latency outliers
6. If failing, add a short "why this is expected to fail today" note
   to the case file under `notes:`.
7. Stage the new case with `git add evals/suites/citations/<slug>.json`.

## Do not
- Do not edit `evals/templates/case.json`.
- Do not touch other eval suites.
- Do not open a PR from this skill. The PR flow lives in the
  `claude-pr-checklist` skill.
```

`allowed-tools` 确定性地限制技能可以做什么——它只能运行评估脚本和暂存文件。不能编辑模板，也不能打开 PR。

### 12.5 层 5：技能（Skills）

技能将工作流打包，使其可以通过名称触发。

一个技能是一个包含带 YAML frontmatter 的 markdown 文件的文件夹。它可以打包 Python 脚本、bash 命令和测试夹具。

**架构：逐步暴露（Progressive Disclosure）**
1. 元数据在会话启动时加载
2. 实际指令仅在你触发技能时加载
3. 捆绑的资源仅在代理引用时加载
4. 即使安装了 50 个技能，环境 token 成本仍然很低

### 12.6 层 6：Hooks 与确定性

#### 配置（settings.json）

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/gate_git_push.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "uv run ruff format $CLAUDE_TOOL_FILE_PATH >/dev/null 2>&1 || true"
          }
        ]
      }
    ],
    "PermissionDenied": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "jq -c . >> .claude/logs/denied.jsonl"
          }
        ]
      }
    ]
  }
}
```

#### PreToolUse：推迟 Git Push 到主分支

```bash
#!/usr/bin/env bash
# Defer any `git push` that targets main. The session pauses. A human
# approves out-of-band and the agent resumes via `claude --resume`.
set -euo pipefail
payload="$(cat)"
cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // empty')"
case "$cmd" in
  *"git push"*"origin main"*|*"git push"*" main"*)
    jq -nc '{
      "permissionDecision": "defer",
      "reason": "Push to main requires human approval."
    }'
    ;;
  *)
    jq -nc '{"permissionDecision": "allow"}'
    ;;
esac
```

#### PostToolUse：自动格式化

后工具钩子有意简单——**一行式格式化钩子是你能获得的最高回报投资**。每次写入后自动运行 `ruff format`，确保代码一致。

### 12.7 层 7：MCP 服务器栈（精选五个）

**基本原则：** 工具 schema 消耗上下文 token。Anthropic 的 Tool Search 文档指出，如果没有延迟加载，50 个工具每轮可能消耗 10,000–20,000 token。**少即是多。**

你真正需要的五个服务器：

| 服务器 | 用途 |
|--------|------|
| **vexp**（@vexp/mcp-server） | 代码图谱 + 持久会话记忆。驱动 65–70% 的 token 减少 |
| **GitHub**（@modelcontextprotocol/server-github） | 分支和提交管理 |
| **Filesystem**（@modelcontextprotocol/server-filesystem） | 跨目录文件访问 |
| **Brave Search**（@modelcontextprotocol/server-brave-search） | 实时文档搜索 |
| **Context7**（@upstash/context7-mcp） | 版本特定的库文档拉取 |

```json
{
  "mcpServers": {
    "vexp": {
      "command": "npx",
      "args": ["-y", "@vexp/mcp-server@latest"],
      "env": {
        "VEXP_PROJECT": "citation-rag",
        "VEXP_MEMORY_DIR": ".vexp"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "${HOME}/code/citation-rag",
        "${HOME}/code/shared-prompts"
      ]
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": { "BRAVE_API_KEY": "${BRAVE_API_KEY}" }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

> 如果你是直接查询生产数据的 AI 工程师，可以加第六个数据库服务器。保持列表精简。vexp 服务器在长期运行的代理设置上驱动 65–70% 的 token 减少（根据 vexp 自己的基准测试）。

> **2026 年 4 月新特性：** 服务器现在可以在工具的 `_meta` 字段中设置 `anthropic/maxResultSizeChars` 注解。这使大型库文档拉取保持内联，无需从磁盘读取，完全绕过旧的文件写入变通方案。

### 12.8 层 8：并行 Worktrees 和 Headless 自动化

**Worktrees 是你不再等待代理打字完成的方式。**

一条命令创建分支、工作目录和隔离会话。每个 worktree 保持自己的编辑器状态和运行中进程。在并列窗格中管理它们。

**实际场景：将 citation 任务并行化**

| 窗格 | 任务 |
|------|------|
| 窗格 1 | 核心生成变更实现 |
| 窗格 2 | 评估框架重写 |
| 窗格 3 | 新检索路径添加追踪 |
| 窗格 4 | 草拟 PR |

每个窗格运行自己的会话、自己的上下文。重叠任务产生重叠编辑，但如果你将任务限定到不同领域——评估在一个窗格，核心逻辑在另一个——实践中很少遇到合并冲突。

#### Headless 模式——夜间评估 CI

最后一块是 headless 模式：在 CI 流水线中**以非交互方式运行代理**。列入白名单特定工具，剥离本地配置以获得可复现行为。

```yaml
name: claude-nightly-evals
on:
  schedule: [{cron: "0 7 * * *"}]
  workflow_dispatch:

jobs:
  run-evals-and-open-pr:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    env:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync

      - name: Install Claude Code
        run: npm i -g @anthropic-ai/claude-code@latest

      - name: Run nightly eval + draft PR (headless)
        id: claude
        run: |
          set -o pipefail
          claude -p \
            --bare \
            --output-format stream-json \
            --allowedTools "Bash(uv run:*),Read,Grep,Glob,Write,Edit,mcp__github__*" \
            --append-system-prompt "You are the nightly eval runner. \
              Run the citations eval suite. If regressions appear, \
              open a draft PR with a fix attempt and the eval diff." \
            "Run: uv run python -m evals.run --suite citations. \
              If any case regresses, implement the minimal fix and open \
              a draft PR against main via the GitHub MCP." \
            | tee claude.ndjson
          if grep -q '"permissionDecision":"defer"' claude.ndjson; then
            echo "deferred=true" >> "$GITHUB_OUTPUT"
          fi

      - name: Resume if the run deferred on push-to-main
        if: steps.claude.outputs.deferred == 'true'
        run: |
          SESSION_ID="$(jq -r 'select(.type=="deferred") | .session_id' \
            claude.ndjson | head -n1)"
          claude --resume "$SESSION_ID" \
            --append-system-prompt "Approved. Continue." \
            --output-format stream-json
```

流程：
1. headless 作业运行评估
2. 草拟修复并尝试推送到主分支
3. hook 捕获推送并推迟权限（defer）
4. 流水线解析 JSON 日志，设置输出变量并暂停
5. 人类审查结构化日志并批准
6. resume 命令精确拾取会话 ID 并完成作业

### 12.9 实战回放：90 分钟的变更如何在 30 分钟内交付

场景：给现有检索服务添加引用来源的答案生成。

**第 1 步：** 工程师打开项目，创建 feature worktree。CLAUDE.md 和 rules 自动加载。五个 MCP 服务器连接。

**第 2 步：** 进入 Deep Plan Mode。explore 子代理映射当前检索路径，planner 输出具体文档：

```
## Implementation Plan: Citation-Backed Generation
1. Modify `services/retrieval/search.py`: Ensure `Chunk` objects attach
   `citation_id` via `shared.citations.make_citation_id`.
2. Update `services/answer/generator.py`: Inject `[Source: {citation_id}]`
   into the Gemini system prompt context block.
3. Create Eval: Add `evals/suites/citations/defective-charger.json` to
   verify strict citation formatting.
```

**第 3 步：** 工程师审查并锁定计划。在主 worktree 中执行实现。

**第 4 步：** 代理完成检索逻辑修改后，调用 `retrieval-reviewer` 子代理。子代理根据路径限定规则返回硬阻断：

```
**Verdict: blocker**
- services/retrieval/search.py: You hand-rolled a UUID for the citation ID
  on line 42. Rule .claude/rules/retrieval.md requires
  shared.citations.make_citation_id.
- tests/retrieval/test_search.py: Missing @pytest.mark.integration on the
  new database test.
```

**第 5 步：** 代理修复手写 ID 和缺失的装饰器。post-tool hook 在每次写入后保持格式整洁。

**第 6 步：** 并行 worktree 使用 `new-rag-eval` 技能重写评估。headless 运行执行最终评估框架并生成 diff。

```json
{
  "suite": "citations",
  "cases_run": 45,
  "grounded_citation_rate": {"previous": 0.82, "current": 0.98, "delta": "+0.16"},
  "unsupported_claims": {"previous": 12, "current": 0, "delta": "-12"},
  "status": "PASS"
}
```

**第 7 步：** 推迟的权限暂停推送。工程师批准。PR 通过 GitHub MCP 附带完整变更集和评估 diff 自动打开。

> 前提是任务范围清晰、配置栈已就绪。第一次搭建这个栈需要一下午。**此后每个任务都在叠加收益。**

### 12.10 底线与最小起点（Floor and Ceiling）

#### 你能搞砸的方式
- ❌ 写一个过大的记忆文件
- ❌ 安装十五个 MCP 服务器（工具 schema 不是免费的）
- ❌ 在主子会话中使用需要子代理的任务（探索和审查应属于隔离上下文）

#### 最小可行配置（不做全部，就做这些）

1. 在项目根目录写一个**简短的命令式记忆文件**
2. 为你最常接触的目录写**两个路径限定规则文件**
3. 添加**一个格式化钩子**
4. 安装**三个服务器**：仓库、文件系统和库文档
5. **强制使用 Plan Mode** 处理任何有出错风险的任务

#### 渐进式扩展

| 什么时候 | 做什么 |
|---------|--------|
| 任务开始重复出现 | 添加子代理 |
| 工作流稳定到可以打包 | 添加技能 |
| 每小时换分支超过两次 | 添加 worktrees |
| 想在睡觉时让代理写代码 | 添加 headless 模式 |

> **栈就是工作流。工作流就是乘数。提示词只是最后 5%。**

---

## 十三、参考资料

- [Akshay Pachaar — Anatomy of the .claude/ folder](https://x.com/akshay_pachaar/status/2035341800739877091)
- [Anubhav — I Spent 6 Months Tuning Claude Code](https://levelup.gitconnected.com/i-spent-6-months-tuning-claude-code-heres-the-exact-setup-that-finally-worked-b41c67628478)
- [Drona Gangarapu — claude-token-efficient](https://github.com/drona23/claude-token-efficient)
- [GitHub #3382 - Sycophantic behavior](https://github.com/anthropics/claude-code/issues/3382)
- [GitHub #14759 - Undermines usefulness](https://github.com/anthropics/claude-code/issues/14759)
- [DEV Community — 7 Ways to Cut Claude Code Token Usage](https://dev.to/boucle2026/7-ways-to-cut-your-claude-code-token-usage-elb)
- [Token Checkup — Free diagnostic](https://yurukusa.github.io/cc-safe-setup/token-checkup.html)
- [Cache Health Checker](https://yurukusa.github.io/cc-safe-setup/cache-health.html)

---

*整理于 2026-05-14，整合来自 @akshay_pachaar、@anubhavgoyal101 和 @drona23 的三份资源*
