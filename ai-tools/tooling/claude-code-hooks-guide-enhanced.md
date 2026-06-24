# Claude Code Hooks 完整指南：从概念到最佳实践

> 本文基于 @sairahul1 的 X 长文、Anthropic 官方文档、以及多篇 Medium 实践文章综合整理增强。
> 原文：《Claude Code Hooks: The Most Powerful Feature Nobody Uses》— @sairahul1
> 增补来源：docs.anthropic.com (hooks reference + hooks guide)、Medium PM 实战指南、hooks 安全实践

---

## 一、原文核心：CLAUDE.md 指导，Hooks 保证

> **CLAUDE.md 告诉 Claude 应该怎么做，但 Hooks 让 Claude 必须遵守。**

这之间的区别，大多数人没注意到。

你可以在 CLAUDE.md 里写 "不要修改 prod.env"，但 Claude 是否执行完全取决于它在那个时刻的判断。

**Hooks 绕过了这个判断。**

它们是可编程的检查点，在 Claude Code 的执行流中运行——在动作发生之前，而不是之后。

---

## 二、Hook 的本质

**Hook 不是一个提示词。不是另一种注入上下文的方式。**

它是一个可编程的控制机制，嵌入在 Claude Code 的执行流中。

当 Claude Code 将要调用一个工具、写入文件或执行命令时——Hook 在动作之前介入并决定：
- ✅ **允许** → 放行
- ❌ **拒绝** → 拦截
- ❓ **请示人类** → 弹出确认框

**这个决定由你提前写好的代码做出，不是由模型。**

### 三层结构

一个 Hook 配置有三层嵌套，大多数人不理解每层的意思：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "./.claude/hooks/protect-prod.sh"
          }
        ]
      }
    ]
  }
}
```

- **第 1 层（hooks）** — 事件注册入口。最外层 `hooks` 对象，每个 key 是一个事件名
- **第 2 层（matcher）** — 匹配规则。数组内的匹配器对象，`"Write"` 表示只在 Claude 调用 Write 工具时触发
- **第 3 层（hook）** — 实际逻辑。`type: command` 运行脚本，`type: http` 调用 URL，`type: mcp_tool` 调用 MCP 工具

> hooks                    ← 入口
>   └── PreToolUse        ← 事件：在工具调用前触发
>         └── matcher     ← 过滤器：只匹配 "Write" 工具
>               └── hook  ← 动作：运行这个命令

---

## 三、完整事件系统（28 个事件）

> 官方文档确认 Claude Code 有 28 个 Hook 事件，覆盖执行流的每个关键点。

### 主流程事件（可阻塞）

| 事件 | 触发时机 | 能否阻塞 |
|------|----------|----------|
| `SessionStart` | 会话启动或恢复时 | ✅ |
| `Setup` | `--init-only` / `--init` / `--maintenance` 模式启动 | ✅ |
| `UserPromptSubmit` | 用户提交提示词后，Claude 处理前 | ✅ |
| `UserPromptExpansion` | 用户命令展开为提示词时，抵达 Claude 前 | ✅ |
| `PreToolUse` | 工具调用前 | ✅ |
| `PermissionRequest` | 权限对话框弹出时 | ✅（可自动审批） |
| `PermissionDenied` | 自动模式拒绝了工具调用 | 🔄（可返回 retry） |
| `PostToolUse` | 工具调用成功后 | ❌（信息型） |
| `PostToolUseFailure` | 工具调用失败后 | ❌ |
| `PostToolBatch` | 一批并行工具调用全部解析完毕 | ❌ |
| `Stop` | Claude 完成响应时 | ❌ |
| `StopFailure` | 因 API 错误结束时 | ❌ |
| `SubagentStart` | 子 Agent 被派生时 | ❌ |
| `SubagentStop` | 子 Agent 完成时 | ❌ |
| `TaskCreated` | 任务通过 TaskCreate 创建时 | ❌ |
| `TaskCompleted` | 任务标记为完成时 | ❌ |
| `TeammateIdle` | Agent 团队成员即将空闲 | ❌ |

### 旁路事件（观测/通知）

| 事件 | 触发时机 | 用途 |
|------|----------|------|
| `Notification` | Claude Code 发送通知时 | 桌面通知、状态更新 |
| `MessageDisplay` | 助手消息文本流式显示时 | 实时日志 |
| `InstructionsLoaded` | CLAUDE.md 或规则文件加载时 | 注入上下文 |
| `ConfigChange` | 配置文件发生变化时 | 审计变更 |
| `CwdChanged` | 工作目录切换时 | 环境管理（配合 direnv） |
| `FileChanged` | 被监听文件变更时 | 实时响应 |
| `WorktreeCreate` | worktree 被创建时 | 干预 git 行为 |
| `WorktreeRemove` | worktree 被移除时 | 清理 |
| `PreCompact` | 上下文压缩前 | 保存状态 |
| `PostCompact` | 上下文压缩完成后 | 重新注入上下文 |
| `Elicitation` | MCP 服务器请求用户输入时 | MCP 交互控制 |
| `ElicitationResult` | 用户响应 MCP 请求后 | 拦截响应 |
| `SessionEnd` | 会话终止时 | 清理收尾 |

### 关键理解：事件是平级的

**PreToolUse 和 PermissionRequest 经常接连触发**，看起来像一个导致另一个。**但它们不是父子关系。** 两者是完全独立的介入点，各自有独立的匹配规则，执行时不互相干扰。

---

## 四、阻塞机制：exit code 的陷阱

> 这是官方文档中容易被忽略的关键细节。

### 两种阻塞方式，含义完全不同

**`exit 2` → 系统错误**
Claude 以为出了问题。工具不可用、资源丢失、环境坏了。它可能会尝试理解错误，甚至另寻方案。

**`exit 0` + JSON stdout → 策略决策**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "明确拒绝的原因"
  }
}
```

Claude 理解这是明确的业务规则说该操作不允许。它不会尝试绕过。接受决策并调整行为。

**JSON 方式还能做更多：**
- 附带可读的拒绝原因
- 通过 `updatedInput` 修改工具输入参数
- 通过 `"decision": {"behavior": "ask"}` 弹出人类确认

### ⚠️ 最常见错误

**`exit 1` 什么都不做。** 在 Unix 惯例中它表示失败，但在 Claude Code Hook 系统中，`exit 1` 是非阻塞的。Claude 忽略它继续执行。

只有 `exit 2` 或 `exit 0` + JSON 才真正影响执行流。

---

## 五、四种 Hook 类型

官方确认了四种 handler 类型，各有优劣：

### 1. `type: "command"` — Shell 脚本

最快、最灵活。脚本通过 stdin 接收 JSON，通过 exit code 和 stdout 通信。

**适合：** 类型检查、lint、拦截危险命令、验证文件路径

### 2. `type: "http"` — HTTP 端点

将事件 POST 到你的 API 或验证服务。JSON 输入作为 POST body 发送。

**适合：** 团队级策略执行、与外部系统集成、集中式审计

### 3. `type: "prompt"` — AI 提示评估

将 Hook 输入发送给一个快速 AI 模型（默认 Haiku）进行智能化、细微的判断。返回 `{"ok": true/false}`。

**适合：** 需要判断力而非确定性规则的情况

### 4. `type: "agent"` — 验证子 Agent

一个完整的 AI 子 Agent，可以使用工具（Read、Grep、Glob）检查文件、验证条件，然后返回决策。

**适合：** 需要多步检查的复杂验证场景

---

## 六、Hook 的注册位置

Hook 可以注册在 4 个不同位置，各有不同作用域和生命周期。

### 1. 设置级 Hooks（常驻）

写在 `settings.json` 中，从 Claude Code 启动到结束一直活跃，不会在任务间被清理。

```
~/.claude/settings.json          ← 用户级，你的机器
.claude/settings.json            ← 项目级，与团队共享
.claude/settings.local.json      ← 本地覆盖，不提交
```

### 2. 插件 Hooks（随插件加载）

插件捆绑自己的 CLAUDE.md、Skills 和 Hooks。当 Claude Code 加载插件时，其 Hooks 与主 Hooks 合并，同等运行。**没有优先级差异。**

**硬限制：插件子 Agent 不能定义 Hooks。** 这是安全设计——子 Agent 是受限执行单元，给它注册 Hooks 的能力会破坏安全模型。

### 3. Skill Hooks（作用域到 Skill）

Skill 被调用时注册，完成时自动清理。不污染全局环境。

### 4. 子 Agent Hooks（作用域到子 Agent）

临时性，自动清理。额外行为：如果在子 Agent 的 frontmatter 中注册了 Stop Hook，它会在运行时自动转换为 `SubagentStop`。

### 多 Hook 合并规则

当多个 Hook 同时匹配时（比如用户设置 + 项目配置 + 当前 Skill 都注册了 PreToolUse）：

**规则 1：并行执行。**
所有匹配的 Hook **同时运行**，非串行，非优先级排序。Claude 等待所有 Hook 返回后才决定。

**规则 2：自动去重。**
如果两层注册了完全相同的 Hook（相同事件、相同匹配器、相同命令串），只保留一份，只运行一次。

**规则 3：最严格结果胜出。**
```
deny > ask > allow
```

一个 deny 就足够了。不管它来自哪一层。

> 为什么这样设计：在安全系统中，允许需要所有人同意。拒绝只需要一个否决。这是所有严肃安全模型的工作方式。

---

## 七、常用模式与最佳实践（官方+社区增强）

### 模式 1：阻止危险命令

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh"
          }
        ]
      }
    ]
  }
}
```

脚本内容：
```bash
#!/bin/bash
COMMAND=$(jq -r '.tool_input.command')
if echo "$COMMAND" | grep -q 'rm -rf'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "危险命令已被 Hook 拦截"
    }
  }'
else
  exit 0
fi
```

### 模式 2：保护敏感文件

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-files.sh"
          }
        ]
      }
    ]
  }
}
```

脚本检查 .env、production 配置等敏感路径，匹配则 `exit 2` 阻塞。

### 模式 3：写入后自动格式化

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

### 模式 4：上下文压缩后重新注入信息

```json
{
  "hooks": {
    "PostCompact": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "cat .claude/inject-on-compact.md"
          }
        ]
      }
    ]
  }
}
```

### 模式 5：桌面通知

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude 需要你的注意\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

各平台命令：
- **macOS**: `osascript -e 'display notification ...`
- **Linux**: `notify-send 'Claude Code' '...'`
- **Windows**: `powershell.exe -Command "[...] MessageBox.Show(...)"`

### 模式 6：自动审批特定操作

```json
{
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"hookSpecificOutput\": {\"hookEventName\": \"PermissionRequest\", \"decision\": {\"behavior\": \"allow\"}}}'"
          }
        ]
      }
    ]
  }
}
```

### 模式 7：注入上下文（Superpowers Plugin 模式）

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "cat .claude/session-bootstrap.md"
          }
        ]
      }
    ]
  }
}
```

### 模式 8：事件桥接（Warp Plugin 模式）

用 6 个 Hook 将 Claude Code 的执行状态同步到外部系统：
- `SessionStart` → 发送初始化信息
- `UserPromptSubmit` → 通知开始工作
- `PostToolUse` → 通知阻塞状态清除
- `Notification` → 空闲时触发通知
- `PermissionRequest` → 发送工具信息
- `Stop` → 读取会话、提取摘要、发送完成通知

---

## 八、自纠正反馈循环（原文未覆盖的关键洞察）

将 PreToolUse 和 PostToolUse 结合使用，你就得到了一个**自纠正反馈循环**：

```
Claude 尝试操作
    │
PreToolUse: 是否允许？
    ├→ No → 拒绝 + 返回原因 → Claude 调整
    │
    ↓ Yes
操作执行完成
    │
PostToolUse: 结果是否有效？
    ├→ No → 返回错误信息 → Claude 自动修正
    │
    ↓ Yes
进入下一步
```

**关键：PostToolUse 的输出来到 Claude 的上下文中。** 如果类型检查失败，Claude 看到错误并自动修正代码——无需复制粘贴错误信息。

---

## 九、心智模型：三个层次协同工作

```
CLAUDE.md  ── 告诉 Claude 如何理解项目
Skills     ── 将 Claude 组织成可靠的工作流
Hooks      ── 在执行关键点守卫边界
```

没有任何一个能替代另外两个：
- **CLAUDE.md 没有 Hooks**: 好的指导，不一致的执行
- **Hooks 没有 CLAUDE.md**: 对模型不理解的东西严格执行
- **三者一起**: 每个层面都可靠

### 调试 Hooks

```
claude --debug
```

这会显示哪些 Hook 匹配了、它们的 exit code 和完整输出。在会话内你也可以用 `Ctrl+O` 切换 verbose 模式。

---

## 十、安全最佳实践

> ⚠️ Command Hook 以你的完整系统用户权限运行。每一条 Hook 命令都需要像生产代码一样审查和测试。

1. **验证和清理输入** — 永远不要盲目信任 Hook 输入数据
2. **始终引用 Shell 变量** — 用 `"$VAR"` 而不是 `$VAR`
3. **阻止路径穿越** — 检查文件路径中是否有 `..`
4. **使用绝对路径** — 用 `$CLAUDE_PROJECT_DIR` 指定完整脚本路径
5. **排除敏感文件** — 不要暴露 .env、.git/ 或密钥文件
6. **测试每个 Hook** — 处理边界情况、错误路径，显式记录失败
7. **匹配器尽可能窄** — `.*` 或空匹配器会匹配所有操作，风险极高

---

## 十一、快速入门：最小 Day-One 配置

不需要一次性自动化所有事。从一个能挽救你最多痛苦的安全网开始：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-env.sh" },
          { "type": "command", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write" }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "echo '✅ Hooks 已就绪：保护 .env、拦截 rm -rf、自动格式化'" }
        ]
      }
    ]
  }
}
```

---

## 十二、速查清单

1. **❌ `exit 1` 什么都不做** — 用 `exit 2` 或 `exit 0` + JSON
2. **🔀 事件是平级的** — PreToolUse 和 PermissionRequest 独立触发
3. **🛡️ 最严格结果胜出** — 一个 deny 否决所有 allow
4. **🧹 自动去重** — 相同 Hook 只跑一次
5. **📦 临时 Hook 自动清理** — Skill 和子 Agent Hook 用完即删
6. **🔗 子 Agent 不能定义 Hook** — 安全模型限制
7. **🪞 $CLAUDE_PROJECT_DIR** — 用这个环境变量指向项目根目录
8. **🔍 `claude --debug`** — 调试 Hook 的首选工具

---

> **结语：Hook 最有用的一点不是防止犯错，而是让你有底气让 Claude 跑得更快。**
> 当你有了一层能拦截错误写入、失败类型检查和作用域违规的防线，你就可以给 AI 更多自由度。这才是真正的解锁。

*本文综合整理自：[@sairahul1 的 X 长文](https://x.com/sairahul1/status/2069710540654645550)、[Anthropic Hooks Reference](https://code.claude.com/docs/en/hooks)、[Anthropic Hooks Guide](https://code.claude.com/docs/en/hooks-guide)、[Medium PM Guide](https://medium.com/all-about-claude/claude-code-hooks-the-complete-pm-guide-nobody-wrote-until-now-2026-f287cb1b2c32)、[Medium Dev Guide](https://medium.com/data-science-collective/claude-code-hooks-explained-the-missing-layer-between-prompts-and-production-d0e3d1509278)、[Medium Safety Net Guide](https://medium.com/@negi.gaurav2/hooks-in-claude-code-718cb145214a)*
