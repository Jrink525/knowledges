---
title: "从 0 开始：用 Hooks 打造自动化 Claude Code 工作流"
tags:
  - claude-code
  - hooks
  - automation
  - workflow
  - claude
date: 2026-05-23
source: "https://x.com/vincemask/status/2054457804057100405"
authors: "Vince 聊开发 (@vincemask)"
enhanced-from:
  - "GitButler - Scott Chacon: Automate Your AI Workflows with Claude Code Hooks"
  - "Medium - Claude Code Hooks: The Complete PM Guide (2026)"
  - "ralphable.com - Claude Code Hooks: Automate Your Entire Development Workflow"
  - "vincemask - .claude 文件夹组织蓝图"
---

# 从 0 开始：用 Hooks 打造自动化 Claude Code 工作流

> **来源：** [Vince 聊开发 — 从 0 开始：用 Hooks 打造自动化 Claude Code 工作流](https://x.com/vincemask/status/2054457804057100405)  
> **增强补充：** GitButler 官方指南、Medium Hook 实战、Claude Code 官方文档  
> **中文整理：** 核心内容归纳 + 多源交叉增强 + 实战配置合集

---

## 一、为什么需要 Hook？

你让 Claude Code 写功能、补测试、格式化文件，最后顺手提交。

它功能写了，测试也补了大半，格式化跑了两个文件，但偏偏漏了一个。然后它很自然地告诉你：「搞完了。」

你一看：没提交，格式也没完全对齐。

**这些问题不该靠你事后检查。** 在 Claude Code 里，它们都可以配置成自动流程。

Hook 把行为从 Claude 的判断里抽出来，放到你的项目规则里。代码质量、通知、安全检查——这些最要紧的事应该放在 Hook 里，不是 prompt 里。

> **核心认知：** CLAUDE.md 是建议性的，Hook 是强制性的。  
> Claude Code 可能误解或忽略一条 CLAUDE.md 指令，但它无法绕过 Hook。
> — medium.com/@koriigami

---

## 二、Hook 是什么

Claude Code hooks 是在 Claude 生命周期固定节点自动执行的 shell 命令。不需要你给 Claude 下任何指令，Hook 就已经跑完了。

| 场景 | 以前 | 有了 Hook |
|------|------|-----------|
| 代码格式化 | Claude 可能不跑 | PostToolUse 上挂 Prettier，每次编辑后自动格式化 |
| 通知 | 你得盯着终端 | Notification 事件自动弹窗，该干嘛干嘛 |
| 安全防护 | Claude 可能改 .env | PreToolUse 拦截敏感文件操作 |

> **GitButler 的指南：** 从三个开始：PostToolUse 自动格式化、PreToolUse 拦截危险命令、Stop 桌面通知，覆盖最广，上手最容易。
> [来源](https://blog.gitbutler.com/automate-your-ai-workflows-with-claude-code-hooks)

---

## 三、5 个最常用的生命周期事件

Claude Code 有 20+ 个生命周期事件（SessionStart 到 SessionEnd），但实际工作中这 5 个就够了：

### 1. PostToolUse — Claude 用完工具后触发

自动格式化、跑 linter、记变更日志。

```
matcher: "Edit|Write" → 文件编辑后执行
```

最常见的使用场景：文件编辑后自动跑 Prettier。

### 2. PreToolUse — Claude 调工具之前触发，**可以拦截**

保护敏感文件（.env、package-lock.json）、阻止危险命令、在 Claude 写任何东西之前卡一刀。

```
退出码 2 → 阻止当前动作，stderr 消息传给 Claude
```

### 3. Notification — Claude 需要你关注时触发

弹桌面通知。不用盯着终端。

```
任何需要你介入的时刻（权限确认、空闲等待等）
```

### 4. Stop — Claude 回复结束时触发

跑测试、跑 CI、自动提交——Claude 说「搞完了」之后自动执行。

### 5. SessionStart — 会话启动或恢复时触发

压缩（compaction）之后重新灌上下文，或者加载环境相关的提醒。

```
matcher: "compact" → 只在压缩后触发
```

> 剩余事件（SubagentStart、WorktreeCreate、InstructionsLoaded 等）留给更复杂的流程。先从上面 5 个上手。

---

## 四、三种 Hook Type

除了标准的 shell 命令 Hook（`"type": "command"`），还有三种高级类型：

### Prompt Hook（`"type": "prompt"`）

把 Hook 的输入丢给 Claude 模型（默认用 Haiku）做判断，返回是/否。适合需要模型理解的场景——比如在 Claude 停止前检查是否所有任务都完成了：

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if all tasks are complete. If not, respond with {\"ok\": false, \"reason\": \"what remains to be done\"}."
          }
        ]
      }
    ]
  }
}
```

比写正则强。

### Agent Hook（`"type": "agent"`）

起一个子代理，能读文件、搜代码、跑工具，最多 50 轮。适合需要对照实际代码状态做判断的情况——比如 Claude 停之前确认测试确实过了。

### HTTP Hook（`"type": "http"`）

把事件数据 POST 到 URL，不跑 shell。适合团队审计日志、共享通知服务、webhook 集成。

> 多数场景 `"type": "command"` 够用。

---

## 五、Hook 配置位置

Hook 配置可放在三个位置：

| 位置 | 作用域 | 是否提交 |
|------|--------|---------|
| `~/.claude/settings.json` | 所有项目（全局） | ❌ 不提交 |
| `.claude/settings.json` | 当前项目 | ✅ 提交到仓库，团队共享 |
| `.claude/settings.local.json` | 当前项目 | ❌ 不提交 |

结构都一样：

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolName|OtherTool",
        "hooks": [
          {
            "type": "command",
            "command": "your shell command here"
          }
        ]
      }
    ]
  }
}
```

`matcher` 是正则，过滤触发条件：
- `"Edit|Write"` — 文件编辑后触发
- `"Bash"` — shell 命令后触发
- `"mcp__github_.*"` — 任意 GitHub MCP 工具调用后触发

> **💡 最简单的方式：** 在 Claude Code 里敲 `/hooks`，交互菜单选择事件、设 matcher、填命令，不用手写 JSON。

---

## 六、立即能配好的 5 个 Hook

### 1. Claude 需要你时弹通知（macOS）

别盯终端了。每次 Claude 等你输入——权限确认、空闲等待、任何需要你介入的时刻——自动弹：

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude needs your attention\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

放 `~/.claude/settings.json`，全局生效。

> ⚠️ **首次使用注意事项：**
> 在 macOS 上第一次使用 osascript 通知之前，需要打开「脚本编辑器」(Script Editor)，手动运行一次该命令，然后在系统设置的通知中允许。之后就可以正常工作了。
> — GitButler 官方指南

### 2. Claude 碰过的文件自动格式化

每次 Edit 或 Write 之后跑 Prettier。Claude 逐文件改代码导致的格式不一致，一劳永逸：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
          }
        ]
      }
    ]
  }
}
```

需要 `jq` 做 JSON 解析，macOS 上安装 `brew install jq`。

放项目的 `.claude/settings.json` 并提交——这是团队规范。

### 3. 不让 Claude 碰受保护文件

拦住 .env、package-lock.json、.git/。被拦后 Claude 会收到反馈说明原因：

Shell 脚本 `.claude/hooks/protect-files.sh`：

```bash
#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
PROTECTED_PATTERNS=(".env" "package-lock.json" ".git/")

for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if [[ "$FILE_PATH" == *"$pattern"* ]]; then
    echo "Blocked: $FILE_PATH matches protected pattern '$pattern'" >&2
    exit 2
  fi
done

exit 0
```

`chmod +x .claude/hooks/protect-files.sh`，然后注册：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-files.sh"
          }
        ]
      }
    ]
  }
}
```

> **安全延伸：** 还可以扩展为扫描 git diff 中的密钥模式（如 `API_KEY=`、`SECRET=`），在提交前拦截意外暴露的凭证。

### 4. 压缩后把上下文填回去

上下文窗口满了，Claude 会压缩对话总结。有时候重要细节被丢掉了。这个 Hook 在每次压缩后触发，提醒 Claude 最核心的事：

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Reminder: use Bun, not npm. Run bun test before committing. Current sprint: auth refactor.'"
          }
        ]
      }
    ]
  }
}
```

echo 换成动态命令也行：`git log --oneline -5` 看最近提交，或 `cat .claude/sprint-context.md` 加载独立上下文文件。

### 5. Git 提交强制规范

Claude 有时候按自己喜好写 commit message——type 前缀不对、用了句子大小写、末尾拖个句号。这个 Hook 在提交落地前拦一道：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Look at tool_input.command. If it does NOT start with 'git commit', return {\"ok\": true}. If it is a git commit command, extract the commit message and check only the FIRST LINE (subject line) — ignore any body lines after the first newline. Check: (1) format is 'type: Capitalized description' where type is one of feat/fix/refactor/docs/chore/perf/revert, (2) description starts with a capital letter, (3) no trailing period, (4) no 'Co-Authored-By' trailer anywhere in the command. Return {\"ok\": false, \"reason\": \"[specific issue. Corrected subject line: type: Description]\"} if any check fails. Return {\"ok\": true} if all pass."
          }
        ]
      }
    ]
  }
}
```

这是 **Prompt Hook**——不写 shell 脚本，不写正则，让 Haiku 模型读命令、对照你的规范判断，直接返回结果。

放 `~/.claude/settings.json`，所有项目生效。

> **🔄 配合 Git 工作流：** 有开发者会将指令注入终端 via Bash hook 实现更多高级控制，详见进阶部分。

---

## 七、退出码怎么用

Hook 脚本通过三个通道和 Claude Code 通信：

```
Stdout:  会被加入 Claude 的上下文中
         适用于 SessionStart、UserPromptSubmit 等 hooks

Stderr:  当你以退出码 2 退出时，会显示给 Claude

Exit code: 决定接下来发生什么：
  0    → 继续执行
  2    → 阻止当前动作，stderr 中的消息会作为反馈传给 Claude
  其他 → 继续执行，stderr 会被记录下来，可通过 Ctrl+O 查看
```

PreToolUse Hook 真正的威力就靠这个退出码体系：你的脚本读到 Claude 即将执行的操作，对照规则判断，要么放行，要么返回具体原因。

---

## 八、三步上手

1. **全局加通知 Hook**  
   打开 `~/.claude/settings.json`，贴上 macOS 通知的配置。最实用、零风险。让 Claude 做一件会触发权限确认的事，看看弹没弹。

2. **当前项目加 Prettier 格式化**  
   在项目根目录打开 `.claude/settings.json`（没有就新建），加 PostToolUse 格式化 Hook。没装 jq 先装。让 Claude 改个文件，确认自动格式化了。

3. **打开 /hooks 翻一翻**  
   交互菜单列出全部事件和说明。想想你的工作流里还有哪些可以自动化。Stop 事件（Claude 完成后跑测试）和 PreToolUse（拦截特定模式）是下一个选择。

---

## 九、进阶：GitButler 的多分支自动提交

Scott Chacon（GitHub 联合创始人、GitButler 创始人）展示了一个高难度案例——用 Hook 实现并行会话的分支隔离。

**核心思路：** 三个 Hook 配合 Git 底层命令，将不同 Claude Code 会话的变更自动推送到独立分支：

| Hook | 作用 |
|------|------|
| **PreToolUse** (Edit/Write) | 为每个 session_id 创建独立的 Git index |
| **PostToolUse** (Edit/Write) | 用 `GIT_INDEX_FILE` 将变更添加到 session 专属 index |
| **Stop** | 用 `git write-tree` + `git commit-tree` + `git update-ref` 提交到 `refs/heads/claude/<session_id>` |

效果示例：
```
❯ git branch
  claude/35560697-eb5b-4bc3-92bf-77536b1dda8f   # 第一个会话：添加 list_dir.py
  claude/9a326bde-78a1-4e6b-abac-dede8721d11f   # 第二个会话：添加 disk_usage.sh
* main
```

**适用场景：** 同时启动多个 Claude Code 实例处理不同任务，每个实例的变更自动隔离到独立分支，互不干扰。

> 完整脚本在 [schacon/cc-hooks-auto-commit](https://github.com/schacon/cc-hooks-auto-commit)

---

## 十、生产级 Hook 配置（TypeScript 项目参考）

以下是一个结合多种模式的生产环境配置：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write", "timeout_ms": 15000 },
          { "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npx eslint --fix", "timeout_ms": 30000 }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "jq -r '.tool_input.command' | grep -q 'git push' && (git branch --show-current | grep -qE '^(main|master)$' && echo 'Direct push to main blocked' >&2 && exit 2) || exit 0", "timeout_ms": 5000 }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "npm run test -- --related", "timeout_ms": 120000 }
        ]
      }
    ]
  }
}
```

> 来源：ralphable.com 完整指南

---

## 十一、常见陷阱与避坑

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **无限循环** | 格式化 Hook 修改文件后又触发 PostToolUse | 使用幂等格式化器；或加前置检查「文件已格式化则跳过」 |
| **Matcher 过宽** | `Bash` 无过滤 → 每次 `ls` 都触发 | 精确匹配：`Bash:git commit`，`Edit|Write` |
| **依赖缺失** | ESLint/Prettier 未安装导致 Hook 失败阻塞所有操作 | 加存在检查：```[ -x node_modules/.bin/eslint ] || exit 0``` |
| **超时不足** | 测试套件 >30s 被 kill | 设置明确 `timeout_ms`，建议实际耗时×1.5 |
| **性能开销** | 批量重构 50 个文件时每个都跑 lint | 批量场景禁用文件级 Hook，依赖 Stop 或 pre-commit 级别 |

---

## 十二、.claude/ 文件夹组织蓝图

一个组织良好的 `.claude/` 文件夹让 Claude 更容易被引导、被信任，也更容易在真实项目中扩展。以下是 Vince 推荐的结构：

```
.claude/
├── CLAUDE.md                # 全局指导：栈、架构、关键命令、全局约定
├── settings.json            # 控制操作方式：权限、hooks、项目级行为
├── CLAUDE.local.md          # 个人覆盖（不进 git）
├── settings.local.json      # 个人覆盖（不进 git）
├── rules/                   # 专项指导（某个领域或工作流）
│   ├── security.md
│   ├── api-design.md
│   └── testing.md
├── hooks/                   # 自动运行的脚本
│   ├── protect-files.sh
│   ├── format-edits.sh
│   └── run-tests-before-stop.sh
├── commands/                # 可复用的提示词工作流
│   ├── review-pr.md
│   ├── write-tests.md
│   └── summarize-changes.md
├── skills/                  # 打包的能力（多步骤 + 配套文档）
└── agents/                  # 专用子代理角色
```

### 渐进式成长路径

```
起步       → CLAUDE.md + .claude/settings.json
指令膨胀   → + rules/
需要自动化 → + hooks/
提示词重复 → + commands/
工作流变深 → + skills/
需要专精   → + agents/
```

> 最高效的 `.claude/` 文件夹不是功能最丰富的，而是每个部分都有清晰用途的。好的结构应该能立即回答：项目级指令在哪里？模块化规则放哪里？自动化脚本放哪里？哪些是共享的、哪些是私人的？
>
> — [vincemask - .claude 文件夹组织蓝图](https://x.com/vincemask/status/2056757482152960110)

---

## 十三、总结

**没有 Hook 时，** 你可能需要结束后追问和检查：格式化做了吗？测试跑了吗？代码提交了吗？

**配置 Hook 之后，** 这些问题消失了。格式化一定会执行，测试一定会运行，通知一定会弹出。它们不再依赖 Claude 是否记得、是否理解、是否照做，而是变成项目环境本身的默认行为。

> **不要把关键流程寄托在 prompt 约束上。应通过环境机制强制执行关键动作，确保它们在每次运行中稳定执行。**

### 推荐的学习路径

1. 读完本文 → 配置「通知 + 格式化」两个 Hook（10 分钟）
2. 第二天 → 加上「敏感文件保护」（复用上面的 protect-files.sh）
3. 一周内 → 探索 `/hooks` 菜单，配置 Stop 自动测试
4. 进阶 → 尝试 Prompt Hook 治理 commit message
5. 高阶 → 研究 GitButler 的多分支自动提交方案

### 一句话总结

**CLAUDE.md 告诉 Claude 应该做什么。Hook 强制它必须做什么。CLAUDE.md 是建议。Hook 是机制。** 把关键流程放在 Hook 里，而不是 prompt 里。

---

*整理于 2026-05-23，综合自 Vince 聊开发、GitButler (Scott Chacon)、Medium 多篇 Hook 实践指南、ralphable.com 及 Claude Code 官方文档*
