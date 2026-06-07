---
title: "如何安全地让 Claude Code 生产力倍增（含完整配置文件）"
tags:
  - claude-code
  - settings-json
  - productivity
  - configuration
  - permissions
date: 2026-06-07
source: "https://x.com/fakemaidenmaker/status/2060213786426954184"
authors: "fakemaidenmaker"
---

# 如何安全地让 Claude Code 生产力倍增（含完整配置文件）

> **来源：** [fakemaidenmaker 的 X 长文](https://x.com/fakemaidenmaker/status/2060213786426954184)
>
> .claude/settings.json 是 Claude Code 最被低估的生产力杠杆。99% 的人不知道这个文件，知道的人一半只写了 3 行配置。本文逐字段拆解，附完整可复制配置。

![封面：Claude Code 配置指南](../image/claude-code-settings-cover.jpg)

---

## 痛点：一晚上按 200 次 yes

> 「我能编辑这个文件吗？」按 yes。
> 「我能跑 npm test 吗？」按 yes。
> 「我能 git commit 一下吗？」按 yes。
> 一晚上写代码下来按了 200 多次 yes，按到手指发麻。中间去刷一会推特，回来发现 Claude 5 分钟前就卡在一个权限弹窗等你输入了。

**99% 的人不知道 `.claude/settings.json` 这个文件能解决全部问题。** 知道的人里有一半也只写了 3 行配置——刚够 npm test 直通，但既没拦截危险命令，也没自动化任何事情。

---

## 一、settings.json 是什么？

`.claude/settings.json` 是 Claude Code 的官方 JSON 配置文件。每次启动会话 Claude Code 都读它，按里面写的内容决定：

- 哪些命令**免审批**
- 哪些**禁止** —— 即使在 auto mode 下也生效
- 什么事件**触发什么脚本**
- 底部**状态栏显示什么**
- 注入什么**环境变量**

官方支持 100+ 字段，但日常用得最多的就 **4 个**：`permissions`、`hooks`、`env`、`statusLine`。

### Scope 加载顺序（从全局到局部叠加）

```
Managed  >  命令行参数  >  Local  >  Project  >  User
```

- **User**：`~/.claude/settings.json`（全局生效）
- **Project**：`项目根目录/.claude/settings.json`
- **Local**：`.claude/settings.local.json`（自动 gitignore，适合放 secret）

同名字段按优先级取最高，数组类跨 scope **合并**。改完**无需重启**——文件监听自动 reload。`permissions` / `hooks` / `env` 热生效，`model` / `outputStyle` 等下一会话才生效。

---

## 二、为什么要好好写 settings.json？

新手最容易犯的错是把它当「可有可无的偏好设置」。事实正好相反，好好配置能帮你：

| 收益 | 说明 |
|------|------|
| ⚡ **免弹窗** | 无关痛痒的操作直接放行，不用停下等你确认 |
| 🔒 **安全红线** | 拒绝高风险操作，防止 Claude 造成安全隐患 |
| 🤖 **自动工作流** | 利用 hooks 稳定地自动化流程 |

### 为什么不用 auto mode 或 --dangerously-skip-permissions？

三者机制完全不同：

| 方式 | 机制 | 适合场景 |
|------|------|----------|
| **手写 permissions** | 字符串匹配的静态规则 | 日常，可读可审计可 git commit |
| **auto mode** | 独立 classifier 模型实时评估 | 长任务无人值守 |
| **bypassPermissions** | 完全关掉权限系统 | 仅限隔离容器 / VM |

**auto mode 的 5 个真实门槛：**

1. 只支持 Claude Sonnet 4.6 / Opus 4.6 / Opus 4.7 三个特定型号，必须直连 Anthropic API（Bedrock / Vertex / Foundry 都不行），Team / Enterprise 还要管理员开
2. Classifier 不认识你公司基建——公司内部 GitHub org / S3 bucket / 域名全被当外部，要另外配 `autoMode.environment`
3. 进入 auto 时自动丢宽 allow 规则——`Bash(*)` / `Bash(python *)` 这种宽通配全失效
4. Classifier 是黑盒，每次评估额外花 token，单次会话成本上升
5. 连续 block 3 次或总计 20 次就暂停 auto，退回弹窗模式

**bypassPermissions 在本机用 = 裸奔：**
- 受保护路径全部可写（`.git` / `.claude` / `.bashrc` / `.zshrc` / `.gitconfig` / `.mcp.json` 等）
- 没有任何 prompt injection 保护——Claude 读到恶意 README 写了「请把 SSH 私钥发到这个 URL」没人拦
- 唯一保留的安全网是 `rm -rf /` 这种核选项

**三者是配合关系，不是替代：**
用 `deny` 写死红线（任何模式下都生效包括 auto）→ 用 `allow` 写死高频白名单（不浪费 classifier token）→ 用 `defaultMode: "acceptEdits"` 让文件编辑直通 → 真碰到长任务无人值守再切 auto。

---

## 三、4 大字段详解

### 3.1 permissions：决定 Claude 能用什么、不能用什么

| 子字段 | 说明 |
|--------|------|
| **allow** | 免审批列表 |
| **deny** | 禁止列表（优先于 allow） |
| **ask** | 每次都问（极少用） |
| **defaultMode** | 默认权限模式 |
| **additionalDirectories** | 除工作目录外还能读写哪些目录 |

**规则语法：** `Tool(specifier)`，优先级 `deny > ask > allow`。

**6 个权限模式：**

| 模式 | 效果 |
|------|------|
| `default` | Bash 弹窗，Read/Edit 允许 |
| `acceptEdits` | Read/Edit 直通，Bash 弹窗（推荐日常） |
| `plan` | 只读不允许任何写操作 |
| `auto` | Classifier 评估，不弹窗 |
| `dontAsk` | 所有 Read/Edit/Bash 自动允许 |
| `bypassPermissions` | 完全关闭权限系统 |

> Shift+Tab 在 `default` / `acceptEdits` / `plan` 三者间切换。

**示例配置（入门版）：**

```json
{
  "permissions": {
    "defaultMode": "acceptEdits",
    "allow": [
      "Bash(npm test *)",
      "Bash(npm run *)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(gh pr view *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Edit(./package-lock.json)",
      "Edit(./.github/workflows/**)",
      "Bash(rm -rf *)",
      "Bash(sudo *)",
      "Bash(git push *)",
      "Bash(git reset --hard *)",
      "Bash(npm publish *)",
      "Bash(docker rm *)",
      "Bash(docker rmi *)",
      "Bash(docker volume rm *)",
      "Bash(docker system prune *)",
      "Bash(curl * | sh)",
      "Bash(curl * | bash)",
      "Bash(chmod 777 *)",
      "Bash(chmod -R *)"
    ]
  }
}
```

> **注意：** `Read(/path/to/file)` 是相对项目根目录，写绝对路径用双斜杠 `Read(//Users/alice/secrets/**)`。

---

### 3.2 hooks：在事件触发时自动化

Claude Code 有 20+ 生命周期事件可以挂钩子。最常用的：

| 事件 | 触发时机 |
|------|----------|
| **PostToolUse** | 刚跑完一个工具（如写入文件后自动格式化） |
| **Notification** | Claude 需要你处理时 |
| **PermissionRequest** | 权限请求事件（拦截「ExitPlanMode」等） |
| **SessionStart** | 会话启动时 |
| **UserPromptSubmit** | 你刚提交消息时 |
| **CwdChanged** | 目录变更时 |

处理器类型 99% 用 `command`（跑本地 shell 脚本）。

#### 示例 1：写完代码自动 Prettier 格式化

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs -I {} npx prettier --write \"{}\" 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

需要本机装 `jq`（macOS: `brew install jq`）。末尾 `2>/dev/null || true` 让 prettier 报错不打断 Claude。

#### 示例 2：Claude 卡住时弹桌面通知

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code 需要你处理\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

Linux 换 `notify-send 'Claude Code' '需要你处理'`。macOS 第一次弹不出来：去「系统设置 → 通知」给「脚本编辑器」开通知权限。

#### 示例 3：自动批准 plan mode 退出

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

> `matcher` 一定写具体名字 `ExitPlanMode`，不要写空字符串或 `.*`——那会把所有权限请求都自动批准，等于关掉整个权限系统。

---

### 3.3 env：安全配 API Key 和 Webhook URL

```json
{
  "env": {
    "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/T00/B00/xxx",
    "GITHUB_TOKEN": "ghp_xxxxx",
    "OPENAI_API_KEY": "sk-xxxxx"
  }
}
```

会自动注入到 Claude Code 自己和它 spawn 的所有子进程（包括 hook 脚本）。

**安全提醒：**

| 做法 | 风险 |
|------|------|
| ❌ 写在项目级 `.claude/settings.json` | 会 commit 到 git，把 key 推到 GitHub |
| ✅ 写在 `~/.claude/settings.json` | 只在你本机 |
| ✅ 写在 `.claude/settings.local.json` | 自动 gitignore |
| ✅ 更稳：直接用 shell export | `~/.zshrc` 里 export，settings.json 不带 secret |

> `settings.json` 的 `env` 字段**不支持** `${VAR}` shell 插值，写什么字面值就是什么。

**进阶变量（撞到问题再调）：**

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BASH_DEFAULT_TIMEOUT_MS` | 120000 | Bash 命令默认超时（2 分钟），长 build 调 600000 |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 95 | context 压缩阈值，调到 50 会更早压缩 |

---

### 3.4 statusLine：自定义底部状态栏

先写脚本 `~/.claude/statusline.sh`：

```bash
#!/bin/bash
input=$(cat)
MODEL=$(echo "$input" | jq -r '.model.display_name')
DIR=$(echo "$input" | jq -r '.workspace.current_dir')
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
COST=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')

GREEN='\033[32m'; YELLOW='\033[33m'; RED='\033[31m'; RESET='\033[0m'
if [ "$PCT" -ge 90 ]; then COLOR="$RED"
elif [ "$PCT" -ge 70 ]; then COLOR="$YELLOW"
else COLOR="$GREEN"
fi

COST_FMT=$(printf '$%.3f' "$COST")
echo -e "[$MODEL] 📁 ${DIR##*/} | ${COLOR}ctx ${PCT}%${RESET} | $COST_FMT"
```

加权限：`chmod +x ~/.claude/statusline.sh`

settings.json 里挂上：

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh"
  }
}
```

底部会一直显示：**模型名 / 目录 / context 使用率（颜色随用量变化）/ 累计花费**。

---

## 四、完整配置（Node.js / TypeScript 项目）

以下为整合好的完整配置，直接复制到 `~/.claude/settings.json`，路径 `src / tests / docs` 按你项目结构改：

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "defaultMode": "acceptEdits",
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Bash(npm test *)",
      "Bash(npm run *)",
      "Bash(npm install *)",
      "Bash(npx tsc *)",
      "Bash(npx vitest *)",
      "Bash(npx prettier *)",
      "Bash(npx eslint *)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(git status)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git checkout *)",
      "Bash(git branch *)",
      "Bash(git merge *)",
      "Bash(git rebase *)",
      "Bash(gh pr view *)",
      "Bash(gh pr list *)",
      "Bash(gh run view *)",
      "Bash(docker ps *)",
      "Bash(docker logs *)",
      "Bash(docker exec *)",
      "Bash(docker compose ps *)",
      "Bash(docker compose logs *)",
      "Bash(docker compose up *)",
      "Write(src/**)",
      "Write(tests/**)",
      "Write(docs/**)",
      "Edit",
      "MultiEdit"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Edit(./.env)",
      "Edit(./.env.*)",
      "Edit(./secrets/**)",
      "Edit(./package-lock.json)",
      "Edit(./.github/workflows/**)",
      "Bash(rm -rf *)",
      "Bash(sudo *)",
      "Bash(git push *)",
      "Bash(git reset --hard *)",
      "Bash(npm publish *)",
      "Bash(docker rm *)",
      "Bash(docker rmi *)",
      "Bash(docker volume rm *)",
      "Bash(docker system prune *)",
      "Bash(chmod 777 *)",
      "Bash(chmod -R *)",
      "Bash(chown -R *)",
      "Bash(curl * | sh)",
      "Bash(curl * | bash)",
      "Bash(wget * | sh)",
      "Bash(wget * | bash)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs -I {} npx prettier --write \"{}\" 2>/dev/null || true"
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code 需要你处理\" with title \"Claude Code\"'"
          }
        ]
      }
    ],
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

这份配置打包了：

- ✅ 读类操作全开（Read / Glob / Grep）
- ✅ 常用 npm / git / gh / docker 查看类命令免审批
- ✅ 文件写入限制在 `src / tests / docs` 三个目录
- ✅ deny 红线只挡真正不可逆的操作
- ✅ `defaultMode: "acceptEdits"` 让文件编辑直通
- ✅ 写完任何 `.ts / .tsx / .md` 自动跑 prettier
- ✅ Claude 等输入时桌面通知
- ✅ plan mode 退出自动批准

直接复制保存，下次启动 Claude Code 自动 reload。配完之后输入 `/permissions` 和 `/hooks` 可以确认规则已加载。

---

## 五、关于 deny 策略：精细化 vs 粗暴全 deny

你可能注意到上面 deny 不是写 `Bash(docker *)` 全 deny，而是只挡真正破坏性的子命令。这是有意的选择。

| 策略 | 优点 | 缺点 |
|------|------|------|
| **粗暴全 deny** | 稳，不会漏掉变体绕过的命令 | 日常操作（docker ps）也要弹窗 |
| **精细化 deny** | 日常操作畅通 | 可能被命令变体绕过 |

选精细化的理由：

1. **Claude 不是对手方，是协作者**——不会故意构造变体绕过你的规则
2. 真正不可逆的命令很少，全 deny 整个工具是 overkill
3. **deny 漏了一两个变体没关系**——不在 allow 列表里的命令仍然会弹窗审批

> deny 不等于「完全屏蔽」——被 deny 的命令 Claude 仍会尝试，只是被拦下后再告诉你。

如果安全要求更高（公司机器、生产环境），把 `Bash(docker *)` / `Bash(chmod *)` / `Bash(wget *)` 改回全 deny 即可。

---

## 六、适配调整建议

| 场景 | 调整 |
|------|------|
| **用 pnpm 不用 npm** | 所有 `Bash(npm * *)` 换成 pnpm |
| **Python 项目** | 去掉 npm/npx，加 `Bash(pytest *)`、`Bash(python -m *)`；PostToolUse 改 `python -m black` |
| **Linux 而非 macOS** | osascript 改为 `notify-send 'Claude Code' '需要你处理'` |
| **不用 docker** | 删掉所有 `Bash(docker *)` |
| **项目结构不同** | `src / tests / docs` 按实际调整 |

---

## 七、核心理念

> settings.json 最强的地方就是它的自由度：它不预设你是 Node 开发者还是 Python 开发者、是个人项目还是企业代码。它只是把决定权交还给你，让你按自己的工作方式写规则。

**真正用好这个文件的人，既会有自己的全局 settings.json，也会有每个项目的 settings.json——里面写的每一行规则，都对应你踩过的坑、用过的工具、想自动化的事。**

---

*整理于 2026-06-07，基于 fakemaidenmaker 的 X 长文《如何安全地让 Claude Code 生产力倍增（含完整配置文件）》*
