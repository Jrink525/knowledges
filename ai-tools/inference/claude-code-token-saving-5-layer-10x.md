---
title: "Claude Code Token 消耗砍掉 90%+：5 层工具链 + 自定义 Hooks + 从 0 到 1 开发插件"
tags:
  - claude-code
  - token-optimization
  - hooks
  - plugins
  - claude
  - context-management
date: 2026-05-30
source: "https://x.com/vincemask/status/2060298054599934424"
authors: "Vince 聊开发 (@vincemask)"
related:
  - "ai-tools/claude/claude-code-stop-installing-plugins-ultimate-guide.md"
  - "ai-tools/claude/claude-code-hooks-automation-workflow.md"
  - "ai-tools/agent-engineering/harness/agent-hooks-deterministic-control.md"
  - "ai-tools/agent-engineering/harness/thin-harness-fat-skills-garry-tan.md"
  - "ai-tools/agent-engineering/harness/npx-skills-add-flow.md"
  - "ai-tools/agent-engineering/harness/skillify-skill-engineering-guide.md"
---

# Claude Code Token 消耗砍掉 90%+：5 层工具链 + 自定义 Hooks

> **来源：** [如何用 5 个工具 + 自定义 Hooks 把 Claude Code Token 消耗砍掉 90%+](https://x.com/vincemask/status/2060298054599934424) — @vincemask
> **整理日期：** 2026-05-30

---

## 问题：Token 都去哪了

随手发一句 `test`，背后可能已经滚掉几百 token；一次代码检索直接冲到 400K token，会话二十分钟就烧完。你以为在写代码，实际上 token 都消耗在看不见的地方了。

省 token 不能只靠"少说两句"或"换个便宜模型"。真正要做的是把整条链路拆开，**让省 token 变成默认执行**。

---

## 五道闸门体系

```
  用户输入
     │
  ┌──▼─────────────────────────────────────────────┐
  │ 第一层: CBM                     代码探索 token │
  │   (Codebase Memory MCP)          省 99.2%     │
  └──┬────────────────────────────────────────────┘
     │
  ┌──▼─────────────────────────────────────────────┐
  │ 第二层: context-mode             大输出 token  │
  │   (沙箱执行 + BM25 摘要)         省 85%+      │
  └──┬────────────────────────────────────────────┘
     │
  ┌──▼─────────────────────────────────────────────┐
  │ 第三层: RTK                       中小输出     │
  │   (Rust Token Killer)           <10ms 压 CLI  │
  └──┬────────────────────────────────────────────┘
     │
  ┌──▼─────────────────────────────────────────────┐
  │ 第四层: Headroom                  API 层再压   │
  │   (shell wrapper + 本地代理)                   │
  └──┬────────────────────────────────────────────┘
     │
  ┌──▼─────────────────────────────────────────────┐
  │ 第五层: Caveman                   输出废话     │
  │   (寄存器模式)                    省 30-50%   │
  └──┬────────────────────────────────────────────┘
     │
     ▼
   Anthropic API
```

每一层只处理自己那一段的消耗，不指望一个工具包解决所有问题。工具只占一半，**另一半是 Hooks 门禁**——不让 Claude 绕过压缩策略走捷径。

---

### 第一层：CBM + cbm-code-discovery-gate

**工具：** [Codebase Memory MCP](https://github.com/DeusData/codebase-memory-mcp)

CBM 用 tree-sitter AST 把代码库解析成持久化知识图谱，支持 66 种语言。查函数定义、调用链、模块关系时，Claude 可以直接问图，而不是把几十个文件塞进上下文。

- **数据：** 5 次结构查询 CBM 约 3,400 token；逐文件 grep 约 412,000 token → **省 99.2%**

**门禁：** 三个 Hooks 搭的小状态机

| Hook | 文件名 | 作用 |
|------|--------|------|
| PreToolUse | `cbm-code-discovery-gate` | Mark Read/Grep/Bash 调用次数，超过阈值就注入提示，建议改用 CBM |
| PostToolUse | `cbm-mcp-marker` | 只要调过 CBM，touch `/tmp/cbm-mcp-used-$PPID` |
| SessionStart | `cbm-session-reminder` | 在 startup/resume/clear/compact 时重新注入 CBM 使用规则 |

> **重点：** 只写"建议使用 CBM"没用。Claude 总会滑回 Read 和 Grep。要省 token，就得把捷径堵上。

---

### 第二层：context-mode + PreToolUse 导流

**工具：** [context-mode](https://github.com/mksglu/context-mode)

context-mode 处理**大输出**。它让命令在沙箱子进程里跑，完整输出留在本地并建 BM25 索引，进对话窗口的只有摘要。之后需要细节，再用搜索把相关片段捞出来。

- **效果：** 同样 200K 上下文窗口，会话从约 30 分钟延到 3 小时以上

**门禁：** PreToolUse Hook 导流

安装分两步——插件（让 Claude Code 认识它）+ npm 包（给 Hook 调 CLI）。Hook 挂在 PreToolUse、PostToolUse、PreCompact、SessionStart 上，统一调用：

```bash
context-mode hook claude-code <event>
```

**重点：** 测试命令值得单独管。`npm test`、`pytest`、`go test ./...` 等跑起来就是几千行输出。可以加一个非阻塞 PreToolUse hook 提醒 Claude 改用 `ctx_batch_execute`，不要把测试日志直接灌进上下文。

---

### 第三层：RTK + bash-ban-raw-tools

**工具：** [RTK (Rust Token Killer)](https://github.com/rtk-ai/rtk)

RTK 是一个 Rust 二进制文件，专门压缩 CLI 输出——删样板、合并重复内容、截断长输出、去重。开销小于 10ms，不联网。

**与 context-mode 的分工：**
- context-mode → 大输出（20 行以上的测试/构建日志）
- RTK → 中小型 shell 输出（git status、npm install、短测试结果）

RTK 随 Headroom 捆绑安装，一般不用单独配。

**门禁：** `bash-ban-raw-tools`

Claude 可以不用 Read/Grep，直接跑 `cat file.js` 来绕过前面的压缩策略。这个 Hook 专堵这条路：

**拦截：**
```
cat file.py | head -100
curl http://localhost:8080/health
```

**逃生门：** 真需要原始输出时，设标记临时解锁（两个标记 10 分钟后过期）：

```
#allow-raw-output-on
#allow-raw-output-off
```

---

### 第四层：Headroom + shell wrapper

**工具：** [Headroom](https://github.com/chopratejas/headroom)

前三层控制"什么进入上下文"。Headroom 管另一件事：**请求离开本机、发给 Anthropic API 之前，把整个 prompt 再压一遍**。

它压的不仅是工具输出，还包括对话历史、系统提示、CLAUDE.md、规则文件等——很多 token 藏在这些地方，普通工具碰不到。

**四块组件：**
1. **Prompt compression** — 全量压缩
2. **API proxy** — 本地代理劫持请求
3. **Cost tracking** — 实时 token 统计
4. **RTK integration** — 内嵌 RTK

**门禁：** shell wrapper

Headroom 的 `install.sh` 在 shell 配置里注入一个 `claude` 函数：

```bash
# bash / zsh
claude() {
  headroom -- "$@"
}

# fish
function claude
  headroom -- $argv
end
```

这个 wrapper 启动本地代理、设置 `ANTHROPIC_BASE_URL`，再拉起 Claude。`--` 不能省——后面的 `--resume`、`-p "query"` 等参数要靠它正确穿透。

---

### 第五层：Caveman + 插件自激活

**工具：** [Caveman](https://github.com/JuliusBrussee/caveman)

还有一种浪费经常被忽略——**Claude 自己太啰嗦**。

Caveman 把 Claude 的回复压成"寄存器模式"：客套话、铺垫、重复解释都砍掉，技术信息保留。

- **压缩前：** "好的，我来为你分析这段代码的逻辑，首先我们可以看到……"
- **压缩后：** "代码分析: <技术内容>"
- **强度三档：** `lite` / `full` / `ultra`（默认 full）

**门禁：** 插件自激活

Caveman 不需要手写 Hook。装成 Claude Code 插件后，它在 SessionStart 和 UserPromptSubmit 上自动注册——装好就生效，它自己就是门禁。

---

## 完整配置一览

### `.claude/settings.json`

```json
{
  "model": "claude-sonnet-4-8",
  "advisorModel": {"model": "claude-sonnet-4-8"},
  "effortLevel": "xhigh",
  "plugins": [
    "@claude-code/plugin-context-mode",
    "@claude-code/plugin-caveman",
    "cbm-code-discovery-gate",
    "cbm-mcp-marker",
    "cbm-session-reminder",
    "bash-ban-raw-tools"
  ]
}
```

### Hook 路由表

| 事件 | Hook | 作用 |
|------|------|------|
| **PreToolUse** | cbm-code-discovery-gate | 限制 Read/Grep/Bash 过度调用 |
| | bash-ban-raw-tools | 拦截绕过压缩的 raw cat/curl |
| | context-mode PreToolUse | 大输出导流到 ctx_batch_execute |
| **PostToolUse** | cbm-mcp-marker | 记录 CBM 调用标记 |
| | context-mode PostToolUse | 处理 context-mode 结果 |
| **PreCompact** | context-mode PreCompact | 会话压缩前释放空间 |
| **SessionStart** | cbm-session-reminder | 注入 CBM 使用提醒 |
| | Caveman (自动) | 注册输出压缩 |
| | context-mode SessionStart | 初始化 context-mode 环境 |

### CLAUDE.md 建议

只写 Claude 在会话里能看到、能执行的规则。Headroom 和 RTK 在会话外运行，Claude 不知道它们存在，写进去也没意义。

```
## Token 节约规则
- 代码探索优先用 CBM 知识图谱，避免逐文件 Read
- 大输出（测试日志、构建输出）先用 ctx_batch_execute
- 查询结构信息（函数定义、调用链）不要 grep，用 CBM 查询
- 不要用 cat/curl 绕过压缩
```

### 按语言拆分规则

`~/.claude/rules/` 按技术栈拆文件，通过 `@import` 加载：

```
~/.claude/rules/
├── flutter.md          # Flutter/Dart 项目规则
├── react-next.md       # React/Next.js 规则
└── python.md           # Python 规则
```

**Flutter 示例（flutter.md）：**
```
- 访问 Flutter MCP 获取 widget 和 API 文档
- @import /skills/flutter/flutter-widget-guide.md
- pub.dev 的包信息优先用 `dart pub deps --json`
```

**React/Next 示例（react-next.md）：**
```
- 客户端组件用 'use client'
- 服务器组件直接 async，不需要 useEffect
- 图片用 next/image
```

---

## 其他好用 Hook

| Hook | 功能 |
|------|------|
| **codeburn** | `.claude/hooks/PreToolUse/`，审查且阻止危险命令（rm -rf、危险 curl、网络诊断） |
| **agent-browser** | 无头浏览器截图，视觉检查页面变更 |
| **cache-browser** | 多仓库 CBM 缓存共享 |
| **context-hog** | 监控每类工具消耗的 token 比例，超限时告警 |

---

## 最终效果

| 场景 | 优化前 | 优化后 | 降幅 |
|------|--------|--------|------|
| 代码探索（5 次查询） | ~412K tokens | ~3.4K tokens | **99.2%** |
| 单次完整会话窗口 | ~30 分钟用完 | 3 小时+ | **83%+** |
| CLI 输出占 context | 全文 | 压缩摘要 | **60-80%** |
| Claude 回复废话 | 含铺垫客套 | 寄存器模式 | **30-50%** |

> 数字因统计口径不同仅供参考，核心是**分层堵漏的思路**。

---

## 从 0 到 1：开发你自己的 Claude Code 插件

上面这套方案大量依赖自定义 Hooks 和插件。如果你需要在团队内部署或自己做扩展，以下是完整的插件开发指南。

### 背景：Claude Code 插件体系

Claude Code 插件 = `.claude/` 目录下的约定式文件结构，背后有三个层次的扩展机制：

| 方式 | 复杂度 | 场景 |
|------|--------|------|
| **CLAUDE.md** | ★☆☆ | 静态指令、编码规范、项目约定 |
| **Hooks** | ★★☆ | 在特定生命周期事件上注入逻辑 |
| **Plugins**（npm 包） | ★★★ | 完整功能插件，可分发、可升级 |

### 方式一：Hook（轻量级）

想最快写出自定义逻辑，**写一个 Hook**。Hooks 是放在 `.claude/hooks/<event>/` 目录下的可执行文件。

#### 生命周期事件一览

| 事件 | 触发时机 | 用途 |
|------|---------|------|
| `SessionStart` | session 开始、resume、clear、compact | 注入指南/规则/技能 |
| `UserPromptSubmit` | 用户提交 prompt 后 | 改写 prompt |
| `PreToolUse` | AI 调用任何工具前 | 校验/拦截/导流/计数 |
| `PostToolUse` | 工具返回结果后 | 标记/记录/分析结果 |
| `PreCompact` | context 即将压缩前 | 做清理或释放 |
| `PostCompact` | 压缩完成后 | 重新注册状态 |
| `CompletionStart` | AI 开始生成回复前 | 注入系统规则 |
| `PostCompletion` | AI 回复完成后 | 后处理/记录 |

#### Step-by-step：10 行 Hook 示例

```bash
#!/bin/bash
# .claude/hooks/PreToolUse/check-read-count.sh

# 读取已使用 Read 的次数
count=$(cat /tmp/read-count-$PPID 2>/dev/null || echo 0)
count=$((count + 1))
echo $count > /tmp/read-count-$PPID

# 超过阈值时注入提示
if [ $count -gt 5 ]; then
  echo "⚠️ 你已经读取了 $count 个文件。考虑改用 CBM 知识图谱查询。"
fi
```

**文件命名规则：** 任何可执行文件（.sh, .js, .py, 二进制）丢到 `.claude/hooks/<event>/` 下即可。文件名即 Hook 名。

#### 输出约定

Hook 的标准输出（stdout）内容会自动添加到当前步骤的消息队列中：

- **PreToolUse Hook** → 输出追加到工具调用前的消息
- **PostToolUse Hook** → 输出追加到工具返回后的消息
- **其他 Hook** → 输出追加到 AI prompt

示例（Node.js）：

```javascript
#!/usr/bin/env node
// .claude/hooks/PreToolUse/token-guard.js

const toolName = process.env.CLAUDE_TOOL_NAME || '';
const toolInput = process.env.CLAUDE_TOOL_INPUT || '';

// 拦截超过 10MB 的文件读取
if (toolName === 'Read' && toolInput.includes('.')) {
  const size = require('fs').statSync(toolInput).size;
  if (size > 10 * 1024 * 1024) {
    console.log(`⚠️ 文件 ${toolInput} 超过 10MB，建议用 grep 或 head 选择性读取`);
  }
}
```

### 方式二：Skills（中等重量）

Skills 是给 Claude 的预包装指令集。比 Hook 更结构化，但不比 Hook 复杂多少。

#### 手工创建

```markdown
# ~/.claude/skills/deploy-check.md
---
name: deploy-check
description: 部署前检查清单
activation: manual
---

## 部署前必须检查
1. 运行 `npm run type-check` 确保类型正确
2. 运行 `npm run test -- --changedSince=main` 确保变更部分测试通过
3. 检查 `CHANGELOG.md` 是否已更新
4. 确认环境变量配置无误

## 回滚步骤
如果部署失败：
1. `git revert HEAD --no-commit`
2. `npm run build`
3. 验证后 `git commit -m "revert: ..."`
```

创建后通过 `.claude/settings.json` 引入：

```json
{
  "skills": ["deploy-check"]
}
```

#### 用 npx 安装社区技能

```bash
npx @anthropic-ai/claude-code-skills add deploy-health-check
```

#### 用 skillify 包装现有知识

[skillify](https://github.com/anthropics/claude-code/tree/main/skillify) 可以把现有文档/代码目录一键包装成 skill。

### 方式三：完整插件（重量级）

完整插件是发布到 npm 的包，供 `npx claude-code plugins:install` 安装。对团队分发最友好。

#### 插件目录结构

```
my-claude-plugin/
├── package.json
├── .claude/
│   ├── settings.json        # 插件默认配置
│   ├── hooks/               # 插件附带的 hooks
│   │   ├── PreToolUse/
│   │   │   └── my-pre-check.sh
│   │   └── SessionStart/
│   │       └── my-reminder.sh
│   └── skills/              # 插件附带的 skills
│       └── my-skill.md
├── bin/
│   └── my-cli.js            # 插件自带的 CLI 工具
└── README.md
```

#### package.json 规范

```json
{
  "name": "@my-team/claude-code-plugin-token-saver",
  "version": "1.0.0",
  "description": "Claude Code 插件：自动 Token 优化",
  "keywords": ["claude-code-plugin", "token-saver"],
  "claudeCode": {
    "hooks": [".claude/hooks"],
    "skills": [".claude/skills"],
    "configSchema": {
      "maxReadThreshold": {
        "type": "number",
        "default": 5,
        "description": "Read 调用次数阈值"
      },
      "verbose": {
        "type": "boolean",
        "default": false
      }
    }
  },
  "bin": {
    "my-token-saver": "./bin/my-cli.js"
  }
}
```

安装方式：

```bash
npx claude-code plugins:install @my-team/claude-code-plugin-token-saver
```

#### 最佳实践：如何设计一个好插件

| 维度 | 建议 |
|------|------|
| **职责** | 一个插件只做一件事，做好它 |
| **Hook 粒度** | 尽量用 Hooks 而非笨重重写 |
| **Skill 分离** | 静态指令放 skills，动态逻辑放 hooks |
| **配置** | 提供 `configSchema`，让用户按需修改 |
| **调试** | 保留 debug 模式：`export CLAUDE_PLUGIN_DEBUG=1` |
| **测试** | 模拟 Hook 事件来测试：`bash .claude/hooks/PreToolUse/my-hook.sh` |
| **日志** | 输出到 stderr 的不会被 Claude 捕获，适合调试日志 |
| **性能** | Hook 执行时间不要超过 100ms，用 Rust/Go 写 CLI 工具 |
| **兜底** | 始终提供逃生门（escape hatch），不要完全没有绕过途径 |

### 插件 vs Hooks vs Skills 决策树

```
需要自定义逻辑？
  ├─ 只需注入静态指令 → CLAUDE.md 或 Skill
  ├─ 需要在特定事件上执行 → Hook
  │    ├─ 逻辑简单（10 行 bash） → 直接写 .sh Hook
  │    └─ 逻辑复杂（数据处理/API 调用） → 写 .js/.py Hook
  └─ 需要分发给整个团队 → 完整 npm 插件
       ├─ 含多个 hooks + skills → 插件包
       ├─ 仅包含 hooks/skills → 简单插件（无 bin）
       └─ 带 CLI 工具 → 带 bin 的插件
```

### 开发工作流：0 到 1 快速起步

```bash
# 1. 创建本地 Hook
mkdir -p .claude/hooks/PreToolUse
touch .claude/hooks/PreToolUse/my-first-hook.sh
chmod +x .claude/hooks/PreToolUse/my-first-hook.sh

# 2. 测试（直接跑一下看看输出）
bash .claude/hooks/PreToolUse/my-first-hook.sh

# 3. 用 Claude 跑个会话上下文
claude -p "列出当前目录下的文件"

# 4. 检查 Hook 有没有生效
less /tmp/claude-hook-log.txt

# 5. 把好用的 Hook 封装成 plugin npm 包
# 参考上面的 package.json 模板

# 6. 本地安装测试
npx claude-code plugins:install /path/to/your-plugin

# 7. 发布
npm publish --access public
```

### 参考资料

- [[claude-code-hooks-automation-workflow|从 0 开始：用 Hooks 打造自动化 Claude Code 工作流]]
- [[agent-hooks-deterministic-control|Agent Hooks：代理工作流的确定性控制]]
- [[claude-code-stop-installing-plugins-ultimate-guide|停止安装插件——内置功能才是正道]]
- [[thin-harness-fat-skills-garry-tan|Thin Harness, Fat Skills]]
- [[npx-skills-add-flow|npx 安装社区技能]]
- [[skillify-skill-engineering-guide|Skillify 技能工程指南]]
- [Claude Code Documentation: Plugins](https://code.claude.com/docs/en/claude-code/plugins)
- [Claude Code Documentation: Hooks](https://code.claude.com/docs/en/claude-code/hooks)

---

*整理于 2026-05-30，来源：@vincemask 的 X/Twitter 文章 + 知识库资料综合整理*
