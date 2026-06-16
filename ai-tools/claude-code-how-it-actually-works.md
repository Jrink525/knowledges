---
title: "Claude Code 究竟如何工作——Agent Loop / Tools / Memory / Hooks / Skills / SubAgents / MCP 完全解读"
tags:
  - claude-code
  - agent-loop
  - tools
  - mcp
  - subagents
  - hooks
  - skills
  - memory
date: 2026-06-16
source: "https://x.com/santtiagom_/status/2035736659010969856"
authors: "Santi (@santtiagom_)"
---

# Claude Code 究竟如何工作？

> **来源：** Santi (@santtiagom_) X/Twitter 长文（西班牙语）— [¿Cómo funciona realmente Claude Code?](https://x.com/santtiagom_/status/2035736659010969856)
>
> Santi 是 Claude Code 重度用户，拥有 100+ Skills，用 Agent 做 code review 和学习研究

---

## 开篇：从"当聊天用"到理解架构

大部分人刚开始用 Claude Code 时，都是当聊天框用——问什么答什么，好使。但时间长了会发现，重复的 prompt、重复的手工操作，根本没发挥出全部潜力。

Claude Code **不是魔法**，它是建立在一组具体构件之上的系统，每个构件有清晰的职责。理解这些构件，就能知道什么时候用什么、为什么用。

> 如果老重复同样的指令 → 做成 Skill
> 如果长任务丢失上下文 → 交给 SubAgent
> 如果反复做手工步骤 → 用 Hook 自动化

---

## 一、Agent Loop——Claude Code 的心脏

### 聊天 vs Agent

| | 聊天 | Agent |
|--|------|-------|
| 你说 | "教我怎么加鉴权" | "给我的应用加鉴权" |
| 它做 | 解释步骤，**你动手** | **它做事**——读代码、选库、写代码、测试 |
| 结果 | 你还有一堆工作 | 它做完通知你 |

### Loop 的 3 个阶段

```
┌─ 收集上下文（Reunir contexto）
│   读文件、分析代码、探索项目结构
│   ↓
│  采取行动（Tomar acción）
│   编辑文件、运行命令、安装依赖
│   ↓
│  验证结果（Verificar resultados）
│   跑测试、检查错误、有错就修
└──→ 回到起点，直到目标达成
```

Loop 自动适应任务类型：
- **咨询问题** → 只需要收集上下文
- **修 bug** → 可能需要反复经历三个阶段

你也是 loop 的一部分——随时可以打断、重定向、添加新上下文。

---

## 二、Tools——Agent 与真实世界的接口

LLM 本身只处理文本，不能访问文件系统，不能跑命令。**Claude Code 通过 Tools 来做事。**

每调用一次 tool，Claude Code 发送请求给系统 → 系统执行 → 返回结果 → Claude Code 决定下一步。

### 内置 Tools

| Tool | 用途 | 类比 |
|------|------|------|
| **Read / Edit / Write** | 读、改、创建文件——最常用 | 你的 IDE 编辑器 |
| **Bash** | 完整终端权限——装依赖、跑测试、git commit | 你手敲命令行 |
| **Grep / Glob** | 项目内搜索——Glob 按名/模式找文件，Grep 搜内容 | VS Code 搜索 |
| **WebFetch / WebSearch** | 查文档、读 API、调研 | 你的浏览器 |

**Login bug 示例——Tools 如何协同：**
```
Glob → 找到按钮组件在哪
Read → 读代码，理解逻辑哪里出问题
Edit → 修复错误
Bash → 跑测试确认修复通过
→ 全程无需你干预
```

这些 Tools 覆盖日常需求，但它们只和你的本地环境交互。要连接外部服务（GitHub、DB、Slack），需要 **MCP**。

---

## 三、Context & Memory——Claude Code 的"记忆"

每执行一个动作，结果都累积到**上下文（Context）**中。不仅初始 prompt，还包括所有打开的文件、发现的错误、执行的操作和结果。

**两个限制：**

| 限制 | 后果 | 解决方式 |
|------|------|---------|
| 容量有限 | 长 session 会遗忘前面的内容 | SubAgent |
| 每次新对话清空 | Agent 不记得项目上下文 | Memory 系统 |

### Memory 系统（解决了第二个问题）

一套 markdown 文件系统，让 Claude Code 在每次对话开始时就知道项目背景。

**无 Memory**：你说"加一个创建用户的 API"——Claude Code 问"用什么框架？有数据库配置吗？路由怎么组织的？"

**有 Memory**：同样一句话——它知道是 Express + Prisma，routes 在 `/src/routes/`，错误处理用 centralized middleware。**直接开始。**

---

### Memory 的两种形式

#### 1. 手工编写的 Memory

**`~/.claude/CLAUDE.md`**（全局）
- 个人偏好：缩进、命名规范、不喜欢什么写法
- 指令要**具体**："用 2 空格缩进" > "把代码格式好"

**`/项目根目录/CLAUDE.md`**（项目级）
- 架构、团队规范、重要命令
- 新项目跑 `/init`、自动生成
- 保持 **<200 行**，太长会被忽略
- 提交到 repo 则全团队共享

**`.claude/rules/`**（模块级规则）
- 按文件类型自动触发
- 例如：只影响 `src/api/` 文件的规则

#### 2. 自动 Memory（Auto Memory）

Claude Code 在工作时**自己记笔记**：
- 检测到的模式
- 被你纠正过的写法
- 一起做过的决策

保存在 `~/.claude/projects/<项目>/memory/`，每次 session 自动加载。

> ⚠️ **纯本地**，不共享给团队。**定期检查**：Claude Code 可能会记下不好的实践而不自知。
>
> 用 `/memory` 命令查看和编辑 Claude Code 记住的一切。

---

## 四、Hooks & Skills——掌控 Agent

### Hooks——确定性控制

Agent 自主决策是好事，但有时它做的事不是你想要的。**Hook 是不依赖 Agent "记得"的确定性控制。**

| Hook | 触发时机 | 例子 |
|------|---------|------|
| **PreToolUse** | Tool 调用前 | **唯一能阻止动作的 hook**——禁改 .env 文件 |
| **PostToolUse** | Tool 调用后 | 每次改文件后自动跑 Prettier |
| **Notification** | 需要你注意时 | 长任务完成后 Mac 通知 |
| **Stop** | 响应结束时 | 自动 push 到 staging |

**配置在 `.claude/settings.json`：**

```json
{
  "hooks": {
    "PostToolUse": {
      "command": "npx prettier --write {{filePath}}",
      "trigger": ["Edit", "Write"]
    }
  }
}
```

> 无 Hook：Agent 改完代码，没格式化，下个 commit 才发现。
> 有 Hook：改完即格式化，代码永远干净。
>
> Hook = 加到 Agent 生命周期里的**强制规则**。不是建议，不是指令（模型可能忽略），是**永远执行**。

---

### Skills——标准化任务执行

**Skill** 是一个 markdown 文件，定义了某个任务的精确流程：检查什么、什么顺序、什么格式、忽略什么。

**无 Skill**：每次让 Agent 写 API 文档——格式每次不同，有时有示例有时没有，有时有摘要表有时没有。

**有 Skill**：每次按你定义的精确流程执行——相同步骤、相同格式、相同标准。

#### Skill 的目录结构

```
project/
  .claude/
    skills/
      api-docs/
        SKILL.md          ← 必须（指令）
        scripts/           ← 可选（脚本）
        references/        ← 可选（参考）
        assets/            ← 可选（静态资源）
```

#### SKILL.md 的两部分

```markdown
---
name: api-docs
description: 为 REST API 生成标准化文档
---

## 流程
1. 用 Glob 查找所有路由文件
2. 对每个端点提取：方法、路径、参数、响应模式
3. 生成 markdown，格式为：方法 | 路径 | 参数 | 响应
4. 保存到 docs/api/
```

**调用方式：**
- `/api-docs` 直接输入命令
- 用自然语言提要求，Claude Code 根据 description 自动匹配

**可 Skill 化的场景：** API 文档、Changelog、会议纪要、代码迁移——任何你重复做、且有清晰流程的事。

---

## 五、SubAgents——让问题变大的时候交给别人

### 为什么需要 SubAgent？

**上下文的容量有限。** 对话越长，Claude Code 越容易忘记前面的内容。

假设你让它审查整个项目的安全问题——读几十个文件，产生详细报告。这些全部塞进主上下文，且主对话被阻塞。

**SubAgent = 独立的 Claude Code 实例**，有自己的上下文。主 Agent 委托任务给它，它独立执行，执行完只返回摘要。

**支持并行**：三个独立任务可以同时跑，耗时从几分钟压缩到秒级。

### 内置 SubAgents

| Agent | 用途 |
|-------|------|
| **Explore** | 快、只读、专精搜索分析——结果不进主上下文 |
| **Plan** | Plan mode 启动，代理研究项目 |
| **General-purpose** | 需要探索+修改的复杂任务 |

### 自定义 SubAgent

```yaml
# .claude/agents/security-reviewer.md
---
name: security-reviewer
description: 专业代码安全审计
tools:
  - Read
  - Grep
  - Glob
  # 没有 Edit、没有 Bash——只读，不能修改任何东西
---
```

> 注意上例中 tools 限制为 Read/Grep/Glob——这个 Agent 能分析但**绝不修改**任何代码。

创建后用 `/agents` 命令。Claude Code 会自动根据 description 匹配合适任务，也可以显式调用："用 security-reviewer 审查这个 PR"。

### 什么时候用 SubAgent

✅ **适合：**
- 长任务会产生大量输出
- 可拆分成独立并行部分
- 需要特定 tool 权限限制的专用 Agent

❌ **不用：**
- 任务短、不撑爆上下文——协调 SubAgent 的复杂性>收益

---

## 六、MCP——连接外部世界

Tools 限制在本地。MCP（Model Context Protocol）让 Agent 连接外部服务。

**架构：** Claude Code 是 MCP Client → 每个服务有 MCP Server → 暴露一组可调用的 Tools

**无 MCP：** 你说"改完了，开个 PR"——Claude Code 做不到。你得到 GitHub 填表单、assign reviewer、merge。

**有 MCP：** 你说"改完了，开个 PR"——Claude Code 开 PR、写描述、assign reviewer、通知你。全程不离开终端。

**可用 MCP 服务：**
- GitHub — PR、review、issues
- Postgres / Supabase — 查改数据库
- Slack — 消息和频道
- Jira — 工单和项目

> **原生 Tools = 本地环境；MCP = 外部世界。** 两者在 Agent 看来是统一接口。

---

## 七、合奏：所有构件一起工作

### 场景 1：审阅并合并 PR

> "审查 PR #42，没问题的话合入。"

```
1. MCP GitHub → 读修改文件，理解变更
2. SubAgent security-reviewer → 安全审计（不进主上下文）
3. Hook PostToolUse → 本地跑测试验证
4. MCP GitHub → 通过后自动 merge
```

你写了一行，Claude Code 协调了四个系统。

### 场景 2：写 API 文档并通知团队

> "给新端点写文档，通知团队。"

```
1. Skill api-docs → 激活标准文档流程
2. Tools（Read/Grep）→ 读代码抽端点
3. Hook PostToolUse → Prettier 自动格式化
4. MCP Slack → 发摘要到团队频道
```

每次结果完全一致，不用重新解释任何事。

---

## 八、完整架构全景

```
                          ┌─────────────────────────────┐
                          │      Agent Loop              │
                          │  收集 → 行动 → 验证 → 重复   │
                          └──────┬──────────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
       ┌──────────┐     ┌──────────────┐    ┌──────────┐
       │  Tools    │     │  Memory      │    │  SubAgents│
       │(本地操作)  │     │(CLAUDE.md +  │    │(独立实例)  │
       │          │     │ Auto Memory) │    │          │
       └──────────┘     └──────────────┘    └──────────┘
              │                                      │
              ▼                                      ▼
       ┌──────────┐                          ┌──────────┐
       │   MCP    │                          │  Hooks   │
       │(外部服务) │                          │(确定性控制)│
       └──────────┘                          └──────────┘
              │
              ▼
       ┌──────────┐
       │  Skills  │
       │(标准化流程)│
       └──────────┘
```

> 所有构件都围绕 Agent Loop。Memory 让每次 session 信息充分。Tools 让它能行动。Hooks 给它确定性控制。Skills 标准化重复工作。SubAgents 让它规模化。MCP 连接外部世界。

### 今天能开始的 5 件事

1. 检查 Auto Memory，改进 Claude Code 记住的内容
2. 为项目创建 `CLAUDE.md`（如果还没有的话）
3. 连接 GitHub MCP
4. 为撑爆上下文的场景创建专用 SubAgent
5. 配置 Hook 让每次改动后自动跑测试

---

## 关联知识库文章

| 文章 | 关联点 |
|------|--------|
| **[Loop Engineering：14 步路线图](../ai-tools/loop-engineering-roadmap.md)** | Agent Loop 的工程化设计——Automations、Subagents、Hooks 的完整框架 |
| **[Top 10 Agent Skills by GitHub Stars](../ai-tools/top-10-agent-skills-bibryam.md)** | Skills 生态排名——本文是"如何写 Skill"，那篇是"什么 Skill 最火" |
| **[Skill Engineering：Matt Pocock 技能工作簿](../ai-tools/harness/mattpocock-skills-workbook.md)** | 100+ 条 Skill Engineering 实战提示 |
| **[Agentic Code Review（Addy Osmani）](../ai-tools/agentic-code-review-addy-osmani.md)** | SubAgent 做 code review 的工程实践 |
| **[Thin Harness Fat Skills（Garry Tan）](../ai-tools/harness/thin-harness-fat-skills-garry-tan.md)** | "薄框架厚技能"的哲学基础 |

---

*Processed on 2026-06-16 from https://x.com/santtiagom_/status/2035736659010969856*
