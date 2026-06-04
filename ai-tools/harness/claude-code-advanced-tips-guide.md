---
title: Claude Code 使用技巧手册 —— 进阶指令与实战心法
tags:
  - claude-code
  - claude-code-tips
  - slash-commands
  - context-management
  - effort
  - memory
  - troubleshooting
  - prompt-engineering
  - skill
  - automation
date: 2026-05-12
source: "https://x.com/buhuaguo1/status/2054179889650307118"
authors: "@buhuaguo1"
stats:
  likes: 14
---

# Claude Code 使用技巧手册 —— 进阶指令与实战心法

> **来源：** @buhuaguo1 的 X 长文  
> **目标读者：** 已经在用 Claude Code、但还没用精的人。不讲安装，不讲"它是什么"——直接进技巧。

---

## 一、指令质量决定输出质量

Claude Code 用不好，**90% 的问题出在这里：你给的信息不够精确。**

模型不读心。你脑子里想的、没说出口的部分，它会自己填——填的不一定是你要的。

### 指令质量公式

每次给指令前套一遍：

> **背景 + 目标 + 约束 + 重点关注 + 不要做什么**

### 对比

| 坏例子 | 好例子 |
|--------|--------|
| 帮我优化这段代码 | 这段代码有内存泄漏，请找出泄漏点，重点关注数据库连接和文件句柄，给出修复方案，不要重命名变量也不要拆分函数 |

同一个 Claude，同一段代码，信息量不同，结果天差地别。

---

## 二、上下文管理命令（最常用）

上下文是 Claude Code 的"工作桌"——桌子满了，它就开始遗忘或效率下降。

| 命令 | 作用 | 使用场景 |
|------|------|---------|
| `/context` | 查看当前上下文使用情况 + 是否建议压缩 | 回答质量下滑时先跑这个 |
| `/compact [说明]` | 压缩上下文，继续做同一件事 | 会话很长但不想开新对话；可加说明重点保留什么 |
| `/clear` | 清空重来 | 与 compact 的区别：clear 是彻底开新桌，旧会话通过 `/resume` 可找回 |
| `/resume [会话]` | 恢复历史会话 | 忘记任务进展或需要接着上次的工作 |
| `/btw <问题>` | 旁路提问，不污染主会话 | 长任务中间问不相关的小问题，不影响 Claude 对当前任务的理解 |
| `/rewind` | 回到之前的检查点 | Claude 改了一堆不满意的东西想撤回 |

---

## 三、调整思考深度

有一个常被忽视的旋钮：`/effort`（思考深度）。

不是所有任务都需要深度推理：

| Effort 级别 | 适用场景 | 代价 |
|-------------|---------|------|
| `low` | 改变量名、调格式、简单替换 | 最快 |
| `medium` | 默认 | 均衡 |
| `high` | 架构设计、复杂 bug 排查、方案对比 | 较慢 |
| `xhigh` / `max` | 关键迁移、安全审查、影响面广的改动 | 显著消耗更多 token |

**`/fast [on\|off]`** — 快速模式。需要快速迭代、质量要求不高时开启。

> max 不是免费增强。用得其所。

---

## 四、模型与状态命令

| 命令 | 作用 |
|------|------|
| `/model [模型名]` | 切换模型。不同阶段用不同模型：探索期便宜快，关键决策用更强 |
| `/status` | 查看当前版本、模型、账号和连接状态。遇到奇怪行为先跑这个 |
| `/usage` / `/cost` | 查看 token 消耗和计划用量 |
| `/doctor` | 诊断安装和配置。连不上、登录异常、行为奇怪，第一步跑这个 |

---

## 五、代码工作流命令

| 命令 | 作用 |
|------|------|
| `/diff` | 交互式 diff 查看器。看 Claude 这轮改了哪些 |
| `/review [PR]` | 在本地会话里 review PR，不用切浏览器 |
| `/security-review` | 分析当前分支 pending changes 的安全风险。提交前跑一遍 |
| `/simplify [范围]` | 官方内置 Skill。审查近期改动，修复可复用性、质量和效率问题 |
| `/batch <指令>` | 官方内置 Skill。大规模并行修改（如：整个 src/ 从 Solid 迁移到 React） |

---

## 六、配置与记忆管理

### `/memory`

查看和编辑 Claude 的记忆文件（CLAUDE.md / auto memory 等）。搞不清 Claude 现在"知道"什么，用这个。

**重要区别：**

| 文件 | 谁写的 | 作用 |
|------|--------|------|
| **CLAUDE.md** | 你（开发者） | 项目规则、代码规范、架构约定——每次会话自动读取 |
| **Auto Memory** | Claude 自己 | 工作中积累的项目经验，本地自动维护 |

### CLAUDE.md 该写什么？

> 只写 **Claude 自己看代码查不到的东西。**

❌ 不要塞：目录结构、依赖列表、git 历史（它能自己查）
✅ 该写：团队约定、隐性规则、技术选型理由、架构约定

### 其他命令

| 命令 | 作用 |
|------|------|
| `/config` / `/settings` | 设置界面：主题、模型、输出风格 |
| `/permissions` / `/allowed-tools` | 管理工具权限（allow / ask / deny） |

---

## 七、关于 Skill 的一个关键事实

> **用 Skill 发现问题时，对话里讨论的修改不会自动写回 Skill 文件。**

会话结束，讨论的一切就消失了，Skill 文件本身一个字没变。

让修改真正生效，只有两种办法：
1. 在对话里直接让 Claude **写文件**
2. 手动打开 `~/.claude/skills/<name>/SKILL.md` 编辑

---

## 八、自动化命令

| 命令 | 作用 |
|------|------|
| `/loop [间隔] [任务]` | 按间隔重复执行。如 `/loop 每30分钟检查一次构建状态` |
| `/schedule [描述]` | 创建真正的定时任务（routine） |
| `/tasks` | 查看和管理后台任务 |

---

## 九、排障的正确姿势

遇到问题，先分清楚是哪一层出问题，再找对应命令：

```
指令不够精确  → 重新组织指令（本章第一节）
上下文溢出   → /context → /compact
模型不够强   → /model 切换
配置/连接问题 → /doctor → /status
```

> 命令只是入口。执行后还会经过权限、Hooks、上下文这些系统。问题不一定出在命令本身。

---

## 十、指令写法进阶：三个杠杆

### 杠杆 1：把抽象动词换成可验证动词

| ❌ 抽象 | ✅ 可验证 |
|---------|----------|
| 优化 | 减少 50% 响应时间、消除 N+1 查询 |
| 改进 | 按 x 规范格式化 |
| 看看 | 检查 xxx 条件并报告 |

### 杠杆 2：给显式范围

```text
❌ 看一下 webhook
✅ 看 controllers/webhook.ts 的 handleStripeEvent 函数
```

### 杠杆 3：把隐含约束说出来

每个项目都有"人人知道但没写下来"的约定。模型靠不了常识猜：

- 所有 API 必须返回 `{ data, error }` 结构 → **写进 CLAUDE.md**
- 测试不要 mock 数据库 → **写进 CLAUDE.md**
- 这段代码两周后要重构，临时方案别太完美 → **当次对话说清楚**

> 每次纠正 Claude，都是在补这类隐含约束。补一次写进 CLAUDE.md，比补十次省心。

---

## 附：命令快速参考

命令记不住？随时输入 `/`，当前环境可用的命令全在那里。静态列表不如实时菜单可靠。

---

## 与知识库其他文章的关联

- **[claudemd-21-config-rules.md](claudemd-21-config-rules.md)** — 本文第六节的 CLAUDE.md 最佳实践与 claudemd 2.1 的配置规则形成互补。claudemd 告诉你所有可配置项；本文告诉你什么该写、什么不该写。
- **[claude-code-101-academic-researchers.md](claude-code-101-academic-researchers.md)** — 101 是面向初学者的入门流程；本文是面向已入门者的进阶心法。
- **[10-claude-code-agents-pipeline.md](../agent-engineering/10-claude-code-agents-pipeline.md)** — 本文的 Skill 关键事实（修改不会自动写回）解释了为什么 Agent Pipeline 文章强调手动配置 Skill 文件而非对话修改。
- **[npx-skills-add-flow.md](../agent-engineering/npx-skills-add-flow.md)** — 七、八节（Skill 编辑 + 自动化）与 npx skills add 的安装流程对应：Skill 需要手动编辑文件，自动化可以通过 `/schedule` 实现。

---

*Processed on 2026-05-12 from X article by @buhuaguo1*
