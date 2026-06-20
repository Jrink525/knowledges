# 驾驭 Claude Code：CLAUDE.md、Skills、Hooks、Rules、Subagents 全面指南

> 原文：[Steering Claude Code: CLAUDE.md files, skills, hooks, rules, subagents and more](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more)
> 辅以 Anthropic 官方文档扩展而成

---

## 概述

Claude Code 是 Anthropic 推出的智能编程环境。与传统聊天机器人不同，Claude Code 可以读取文件、运行命令、自主修改代码，并在你观察、指导或完全放手的情况下独立完成任务。

控制 Claude Code 行为有 **七种方法**，每种方法在上下文开销、加载时机、持久性和控制力度上各有不同：

| 方法 | 加载时机 | 压缩/持久化行为 | 上下文开销 | 最佳用途 |
|------|---------|----------------|-----------|---------|
| **CLAUDE.md** | 会话启动时加载，整个会话保留 | 压缩时重新读取 | 高——每行都在消耗 token | 构建命令、目录布局、单仓库结构、编码约定、团队规范 |
| **Rules（规则）** | 会话启动时（无范围规则）或仅当匹配文件被触及（路径范围规则） | 无范围规则同 CLAUDE.md；路径范围规则在文件不相关时不加载 | 路径范围规则低，无范围规则高 | 特定约束或约定（如所有 API 处理器必须用 Zod 验证输入） |
| **Skills（技能）** | 会话启动时仅加载名称和描述；主体在被调用时加载 | 被调用的技能在压缩时重新注入，共享总预算，最旧的先丢弃 | 低——全量主体仅在被调用时加载，受共享 token 预算约束 | 程序化工作流（部署流程、发布清单、代码审查） |
| **Subagents（子代理）** | 会话启动时加载名称、描述和工具列表；主体通过 Agent 工具调用时加载 | 不进入主对话；仅在隔离窗口中运行，返回最终消息+元数据 | 低——直到调用前在上下文中零开销 | 需要在隔离环境中并行运行或执行后只返回摘要的侧任务 |
| **Hooks（钩子）** | 钩子配置存在于主上下文窗口之外 | 某些类型的输出可能会写回上下文（如阻断型 hook 的错误输出） | 低——配置存在于主上下文之外 | 确定性自动化：运行 linter、完成后发 Slack、阻断命令、压缩前备份聊天历史 |
| **Output Styles（输出风格）** | 会话启动时注入系统提示；永不压缩 | 缓存 | 高——占用上下文窗口，但覆盖默认系统提示 | 显著的角色变更（代码助手 → 通用助手） |
| **追加系统提示** | 调用时传入，仅对该次调用的请求适用 | 不持久化为文件 | 高——增加输入 token；缓存可降低第一请求后的开销 | 特定编码标准、输出格式或领域知识的临时添加 |

---

## 一、CLAUDE.md 文件

CLAUDE.md 是项目根目录下的 Markdown 文件。它在会话启动时加载，并**在整个会话期间保留在上下文**中。

### 适合放入 CLAUDE.md 的内容

- 构建命令（`pnpm build`、`make` 等）
- 目录布局和单仓库结构说明
- 编码约定和团队规范
- 指向更详细文档的索引

### CLAUDE.md 加载行为

- **始终加载型**：项目根目录 CLAUDE.md + 用户级 CLAUDE.md（`~/.claude/CLAUDE.md`）。加载后不会在长时间会话中丢失或退化。Claude Code 压缩对话时会重新读取这些文件。
- **按需加载型**：子目录中的 CLAUDE.md（如 `app/api/CLAUDE.md`）。当 Claude 读取该目录下的文件时才加载，不在会话启动时加载。
- **用户级 CLAUDE.md**（`~/.claude/CLAUDE.md`）：对命令行中所有项目生效。
- **本地 CLAUDE.local.md** ：个人项目特定笔记；加入 `.gitignore` 防止被提交。

### 潜规则与最佳实践

- **CLAUDE.md 会膨胀**：在共享仓库中，每个团队追加自己的指令但没人删除。随着文件增长，每条内容都在消耗 token，并稀释 Claude 对真正重要指令的遵循度。
- **建议**：保持 CLAUDE.md **少于 200 行**，指定文件负责人，像审查代码一样审查对其的修改。
- **将团队特定规范移入路径范围规则，将程序化流程移入技能**，它们只在相关时加载。
- **在单仓库中**，为每个团队的目录创建独立的子目录 CLAUDE.md，团队只加载自己的约定。使用 `claudeMdExcludes` 设置跳过从不触碰的团队的文件。
- **企业级 CLAUDE.md**：安全策略、合规要求等可通过 MDM 或配置管理部署到开发者机器，且不能被个人设置排除。

---

## 二、Rules（规则）

Rules 是放在 `.claude/rules/` 目录下的 Markdown 文件，用于给 Claude 提供特定的**约束或约定**。

### 无范围规则 vs 路径范围规则

- **无范围规则**：行为与 CLAUDE.md 相同——总是加载、总是消耗 token、压缩时重新注入。对不相关的任务浪费 token。
- **路径范围规则**：通过添加 `paths` 字段控制何时加载。例如只作用在 `src/api/**` 的规则，在纯文档任务中不会出现在上下文里，只有当 Claude 读取 `src/api/` 下的文件时才加载。

### 示例

```yaml
---
paths: src/api/**
---
所有 API 处理器在返回前都必须用 Zod 验证输入。
```

路径范围规则最适合**跨多个（但非全部）领域**的约束。如果需要的是单文件的特定约束（如"迁移文件只追加不修改"），也是规则的理想场景。

---

## 三、Skills（技能）

Skills 是 `.claude/skills/` 目录中的指令、脚本和资源文件夹，Claude 可以**动态加载**。

### 核心原理

- 每个技能有一个 `SKILL.md` 文件，包含 YAML 前置元数据（名称、描述）+ Markdown 正文
- **会话启动时仅加载名称和描述**；完整主体在 Claude 调用技能时才加载
- 调用方式：通过斜杠命令（`/code-review`）或 Claude 的任务自动匹配
- 压缩时：Claude Code 重新注入被调用的技能，所有被调用技能共享总预算，最旧的先丢弃

### 适合做成技能的内容

程序化工作流：部署流程、发布清单、审查流程、安全检查清单等。

判断标准：如果你发现自己**反复粘贴同样的指令清单**到对话中，或者 CLAUDE.md 里的某段内容已经长成了流程而非事实——那就是该做成技能了。

### 技能存放位置

| 位置 | 路径 | 适用范围 |
|------|------|---------|
| 企业级 | 见托管设置 | 组织中所有用户 |
| 个人级 | `~/.claude/skills/<skill-name>/SKILL.md` | 个人所有项目 |
| 项目级 | `.claude/skills/<skill-name>/SKILL.md` | 当前项目 |
| 插件级 | `<plugin>/skills/<skill-name>/SKILL.md` | 插件启用处同名覆盖 |

优先级：企业级 > 个人级 > 项目级 > 内置技能。同名的技能会覆盖内置技能。如果 `.claude/commands/` 和技能同名，技能优先。

### Skills 遵循 AgentSkills 开放标准

Claude Code 技能遵循 [AgentSkills](https://agentskills.io) 开放标准，该标准跨多个 AI 工具。Claude Code 在此基础上扩展了调用控制、子代理执行和动态上下文注入等高级功能。

### 前置元数据字段参考

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 否 | 显示名称，默认为目录名 |
| `description` | 推荐 | 技能功能描述，Claude 据此决定何时自动应用 |
| `when_to_use` | 否 | 何时调用的额外上下文（触发短语或示例请求） |
| `argument-hint` | 否 | 自动补全时显示的参数提示 |
| `arguments` | 否 | 命名的位置参数，用于 `$name` 替换 |
| `disable-model-invocation` | 否 | true 时阻止 Claude 自动加载此技能 |
| `user-invocable` | 否 | false 时从 `/` 菜单隐藏 |
| `allowed-tools` | 否 | 技能激活时 Claude 可直接使用的工具 |
| `disallowed-tools` | 否 | 技能激活时禁止的工具 |
| `model` | 否 | 技能激活时使用的模型覆盖 |

### 内置技能

Claude Code 自带一组内置技能，除非用 `disableBundledSkills` 禁用：

- **`/code-review`**：审查当前 diff 并报告发现，不编辑文件
- **`/debug`**：调试助手
- **`/batch`**：批量操作
- **`/loop`**：循环执行
- **`/claude-api`**：Claude API 工具

另外三个内置技能协同工作来启动和验证应用：
- **`/run`**：启动并驱动应用
- **`/verify`**：构建并运行应用以确认更改
- **`/run-skill-generator`**：教 `/run` 和 `/verify` 如何构建和启动项目（运行一次录制配方，生成项目级技能）

### 动态上下文注入

技能可以在 SKILL.md 中使用反引号加感叹号语法（`!` ``command``）来动态注入命令输出。例如：

```markdown
!`git diff HEAD`
```

Claude 在技能加载前执行该命令，并将输出内联到指令中。

---

## 四、Subagents（子代理）

Subagents 是 `.claude/agents/` 目录下的 Markdown 文件，定义用于特定侧任务的**隔离助手**。

### 核心原理

- 每个文件使用 YAML 前置元数据（名称、描述 + 可选的模型和工具访问权限），后接作为子代理系统提示的正文
- 与技能类似：名称、描述和工具列表在会话启动时加载；但主体**不会自动调用**，只有通过 Agent 工具传递提示词时才触发
- **主体从不进入主对话**——子代理在自己的全新上下文窗口中运行，只有最终消息（通常是多个子任务的结果汇总）+ 元数据返回主会话

### 与 Skills 的关键区别

- **使用 Subagent 的场景**：当侧任务（深度搜索、日志分析、依赖审计）会产生大量中间结果、而这些结果你不会再引用时
- **使用 Skill 的场景**：当希望流程在主线程中执行，以便观察和引导每一步

### 扩展性

子代理可以嵌套最多**五层**，动态工作流可以编排数十到数百个后台代理，而无需指定每个子代理架构的细节。编排计划和中间结果存放在脚本变量中而非 Claude 的上下文窗口中，从而实现规模化而不用牺牲指令遵循度。

### 内置子代理

| 代理 | 模型 | 特点 |
|------|------|------|
| **Explore** | Haiku | 只读代理，优化用于搜索和分析代码库 |
| **Plan** | 继承主对话 | 规划模式下的调研代理，只读 |
| **General-purpose** | 继承主对话 | 复杂多步任务的通用代理 |
| **statusline-setup** | Sonnet | 运行 `/statusline` 时配置状态栏 |
| **claude-code-guide** | Haiku | 回答关于 Claude Code 功能的问题 |

### 配置字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 是 | 唯一标识符（小写字母+连字符） |
| `description` | 是 | Claude 何时应委派任务给此子代理 |
| `tools` | 否 | 子代理可使用的工具（省略时继承全部） |
| `disallowedTools` | 否 | 禁止的工具 |
| `model` | 否 | 模型指定（haiku/sonnet/opus 等） |
| `permissionMode` | 否 | 权限模式（bypass/accept/plan/auto） |
| `hooks` | 否 | 钩子配置 |
| `mcpServers` | 否 | MCP 服务器 |
| `maxTurns` | 否 | 最大轮次限制 |
| `skills` | 否 | 预加载进上下文的技能 |
| `effort` | 否 | 效果级别 |
| `background` | 否 | 是否后台运行 |
| `isolation` | 否 | 隔离级别 |
| `memory` | 否 | 持久化记忆（User scope/Project scope/None） |

### 创建子代理

- 交互式：运行 `/agents` 命令，通过界面创建
- 手动：在 `.claude/agents/` 或 `~/.claude/agents/` 中创建 Markdown 文件
- CLI：`claude --agents '{"name": {...}}'`，仅当前会话有效
- 命令行中的 `--add-dir` 添加的目录也会被扫描

### 子代理权限

子代理默认继承父对话的权限。子代理可以配置自己的权限覆盖：
- 继承模式：使用主对话的权限设置
- 旁路模式：绕过所有权限请求，子代理可以自由行动
- 自动模式：使用分类器自动决定权限
- 接受模式：子代理的权限请求回传主对话处理

### 子代理的 Fork 功能

子代理的 `fork` 模式从当前对话中创建一个分叉，父对话继续等待，子代理处理侧任务。子代理完成后，结果合并回主窗口。这可以处理中断——去处理一个侧任务，然后无缝回到原来的工作。

---

## 五、Hooks（钩子）

Hooks 是用户定义的命令、HTTP 端点或 LLM 提示，在 Claude 生命周期的特定事件上触发，提供**更确定性的控制**。

### 核心原理

- 通过 `settings.json`、托管策略设置或技能/代理前置元数据注册
- 钩子的配置存在于主上下文窗口之外，**上下文开销低**
- 某些钩子类型可能将输出保存回主上下文窗口（如阻断型 hook 的 stderr）

### 五种类型

| 类型 | 行为 | 说明 |
|------|------|------|
| **command** | 确定性 | 运行 shell 脚本 |
| **HTTP** | 确定性 | 发送 HTTP 请求 |
| **mcp_tool** | 确定性 | 调用 MCP 工具 |
| **prompt** | 模型判断 | Claude 在单独窗口中处理 |
| **agent** | 模型判断 | 子代理在单独窗口中处理 |

### 事件生命周期

事件分为三种节奏：
- **每会话一次**：`SessionStart`、`SessionEnd`
- **每轮次一次**：`UserPromptSubmit`、`Stop`、`StopFailure`
- **每次工具调用**（在代理循环内）：`PreToolUse`、`PostToolUse`

### 事件列表

| 事件 | 触发时机 |
|------|---------|
| `SessionStart` | 会话开始或恢复时 |
| `Setup` | `--init-only` 或 `--init`/`--maintenance` 的 `-p` 模式 |
| `UserPromptSubmit` | 提交提示时，Claude 处理之前 |
| `UserPromptExpansion` | 用户输入的命令扩展为提示时 |
| `PreToolUse` | 工具调用执行前（可阻断） |
| `PermissionRequest` | 权限对话框出现时 |
| `PermissionDenied` | 工具被自动模式分类器拒绝时 |
| `PostToolUse` | 工具调用成功后 |
| `PostToolUseFailure` | 工具调用失败后 |
| `PostToolBatch` | 一批并行工具调用解析完成后 |
| `Notification` | Claude Code 发送通知时 |
| `MessageDisplay` | 助手消息文本显示时 |
| `SubagentStart` | 子代理产生时 |
| `SubagentStop` | 子代理完成时 |
| `TaskCreated` | 任务创建时 |
| `TaskCompleted` | 任务标记为完成时 |
| `Stop` | Claude 完成响应时 |
| `StopFailure` | 轮次因 API 错误结束时 |
| `TeammateIdle` | 代理团队成员即将空闲时 |
| `InstructionsLoaded` | CLAUDE.md 或规则文件加载到上下文时 |
| `ConfigChange` | 配置文件在会话中变更时 |
| `CwdChanged` | 工作目录变更时 |
| `FileChanged` | 监控的文件在磁盘上变更时 |
| `WorktreeCreate` | worktree 创建时 |
| `WorktreeRemove` | worktree 移除时 |
| `PreCompact` | 上下文压缩前 |
| `PostCompact` | 上下文压缩完成后 |
| `Elicitation` | MCP 服务器请求用户输入时 |
| `ElicitationResult` | 用户响应 MCP elicitation 后 |
| `SessionEnd` | 会话终止时 |

### 配置示例

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
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh",
            "args": []
          }
        ]
      }
    ]
  }
}
```

### Hook 解析过程

1. 事件触发 → hook 框架检查匹配器（matcher）
2. 匹配器确定哪个 handler 应该运行 → handler 接收到 JSON 格式的事件上下文
3. 对于 `command` 类型，标准输入传入 JSON；对于 `HTTP` 类型，POST body 传入
4. handler 检查输入、采取行动，可选地返回决策（如 `permissionDecision: "deny"`）
5. 退出码 0 = 不决策（正常流程继续）；特定退出码 = 阻断（决策被采纳）

### Hook 适用场景建议

- **应该用 Hook 的场景**：需要确定性执行的行为——每次编辑后运行 linter、完成后推送到 Slack、阻断特定命令、在 `PreCompact` 前备份聊天历史
- **不适合的场景**：需要模型判断的柔性约束——这类应该用 Rules 或 Skills

### Hook 与其他方法的本质区别

Hook 是**框架运行的代码**，而非加载到上下文中的 Claude 指令。因此它们的主上下文开销极低。特别是阻断型 Hook（`PreToolUse` 退出码 2），是唯一能在 Claude 违背指令时真正阻止操作的手段。

---

## 六、Output Styles（输出风格）

Output Styles 是 `.claude/output-styles/` 目录中的文件，将指令注入系统提示。

### 核心特点

- 它们**永远不会被压缩**，在每个会话开始时加载
- 在会话中第一个请求后缓存，上下文开销中等
- 因为位于系统提示中，它拥有**最高级别的指令遵循权重**
- 修改输出风格会**替换默认输出风格**（除非设置 `keep-coding-instructions: true`）

### 默认输出风格包含的关键指令

- 通知 Claude 它在帮助用户完成软件工程任务
- 何时添加或省略代码注释
- 安全问题如何处理
- 验证习惯——在声明完成前运行测试

如果自定义输出风格覆盖了默认值，Claude Code 会变得更像通用助手而非软件工程师助手。

### 内置输出风格

在创建自定义输出风格之前，先检查内置风格：
- **Proactive**：主动模式
- **Explanatory**：教学模式
- **Learning**：协作编程模式

它们覆盖最常见的需求，无需自己维护风格文件。

---

## 七、追加系统提示

`append-system-prompt` 标志是修改输出风格的替代方案。

### 核心特点

- 仅向原始系统提示**追加**内容，不修改
- 不会改变 Claude 的角色——只是在其默认角色上添加指令
- 在调用时传入，仅对该次调用适用，不在会话间持久化
- 可以比输出风格有更高的上下文开销，但 prompt caching 可以降低第一个请求后的开销

### 适用场景

最适合添加特定编码标准、输出格式或领域知识。注意追加系统提示的**遵循度递减**——使用此方法提供的指令越多，Claude 遵循得越不严格，尤其当指令之间存在矛盾时。

---

## 八、选择指南：你的指令应该放在哪里？

如果你发现自己有以下行为，可能需要换个位置：

| 场景 | 建议 | 原因 |
|------|------|------|
| 在 CLAUDE.md 中写 "每次 X 必须 Y" | 使用 Hook | 格式自动运行 vs 模型选择运行完全不同 |
| 在 CLAUDE.md 中写 "永远不要做 X" | 使用 Hook + 权限 | 指令不是防护栏——模型可能在大模型压力下违背 |
| 30 行的流程写在 CLAUDE.md 中 | 使用 Skill | CLAUDE.md 放事实（构建命令、目录布局）；流程放技能 |
| API 特定规则没有加 paths | 加路径范围 | 无范围规则 = 永远在消耗 token |
| 把个人偏好写进项目级 CLAUDE.md | 使用用户级文件 | 个人偏好（如"始终用语义化 commit 信息"）应放在本地 |

### 核心安全原则

当某件事**绝对不能发生**时，指令不是正确的工具。Claude 大多数时候会遵循指令，但：
- 在长时间会话中
- 在模糊情况下
- 因为提示注入

模型可能失败。真正的防护需要确定性机制。用 `PreToolUse` Hook 检查调用并以退出码 2 阻断。**托管设置更进一步**：由管理员部署，不能被用户本地配置覆盖，是实施组织级防护的唯一方式。

---

## 九、最佳实践速查

### 验证工作

**给 Claude 一个可以运行的检查**——测试、构建、可比较的截图——这是被动的会话和你能够完全放手的会话之间的区别。

四种验证层次（越来越自动）：

1. **单条提示中**：要求 Claude 执行检查并在同一消息中迭代
2. **跨会话**：设置检查为 `/goal` 条件，独立评估器在每轮后重新检查
3. **确定性门控**：Stop Hook 运行脚本检查，阻止轮次结束直到通过
4. **第二意见**：验证子代理用新的模型试图反驳结果

### 先探索、再规划、后编码

四阶段工作流：
1. **探索**（Plan 模式）：Claude 阅读文件但不修改
2. **规划**（Plan 模式）：Claude 制定详细实现计划
3. **实现**（默认模式）：根据规划编码
4. **提交**：描述性的 commit 信息 + 创建 PR

规划模式对多文件修改或不熟悉的代码库最有价值。对明确的小改动（修拼写、加日志行、重命名变量），直接做。

### 提供具体上下文

- 限定任务范围：指定文件、场景和测试偏好
- 指向信息来源：引导 Claude 从 git 历史、文档等获取信息
- 引用现有模式：指向代码库中的模式示例

### 环境配置

- 设置 **CLAUDE.md**：构建命令、编码规范、工作流参考
- 配置**权限**：自动模式（分类器审批）/ 权限白名单 / 沙箱隔离
- 使用 **CLI 工具**（`gh`、`aws`、`gcloud` 等）替代 API 调用
- 连接 **MCP 服务器**：`claude mcp add` 连接 Notion、Figma、数据库等
- 设置 **Hooks**：确定性动作（每次编辑后运行 linter、阻断写入特定目录）
- 创建 **Skills**：领域知识和可复用工作流
- 使用 **Subagents**：隔离侧任务，保护主上下文

---

## 十、插件系统

一旦你有了几个技能、子代理、钩子和输出风格，可以将它们打包为一个**插件**，在队友或项目间共享统一的设置。

插件通过在技能文件夹中添加 `.claude-plugin/plugin.json` 来加载，可以同时捆绑代理、钩子、MCP 服务器等组件。

---

## 总结

驾驭 Claude Code 的核心在于理解每种指令机制的**上下文开销**和**控制力度**：

| 控制力度从低到高 |
|----------------|
| CLAUDE.md / 无范围 Rules（柔性指导，高开销） |
| 路径范围 Rules（按需加载，中等开销） |
| Skills（按需调用，低开销） |
| Subagents（隔离执行，零主上下文开销） |
| Output Styles / 追加系统提示（高控制力，高开销） |
| Hooks（确定性执行，最低开销）→ 唯一的真正防护手段 |
| 托管设置 + 权限（最高的强制力）|

把轻量级事实放在 CLAUDE.md，约束用路径范围规则，流程做成技能，侧任务交给子代理，确定性执行配钩子，角色变更用输出风格，临时调整靠追加系统提示。

---

> **参考来源**
> - [Anthropic 官方博客：Steering Claude Code](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more)
> - [Skills 官方文档](https://code.claude.com/docs/en/skills)
> - [Hooks 参考文档](https://code.claude.com/docs/en/hooks)
> - [Subagents 官方文档](https://code.claude.com/docs/en/sub-agents)
> - [Claude Code 最佳实践](https://code.claude.com/docs/en/best-practices)
