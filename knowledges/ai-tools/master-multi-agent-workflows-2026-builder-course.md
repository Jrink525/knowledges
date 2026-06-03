---
title: "2026 多 Agent 工作流完全教程：从单 Agent 到工程化协作"
tags:
  - codex
  - multi-agent
  - agents-md
  - sub-agents
  - agent-engineering
  - agentic-workflow
date: 2026-05-28
source: "基于 @Av1dlive 的 X 长文 'How to Master Multi Agent Workflows in 2026 (Builder\'s Course)'"
---

# 2026 多 Agent 工作流完全教程

> **一句话总结**：我用了 12 个月的单 Agent 模式，然后切换到多 Agent 工作流 30 天。这篇文章就是那 30 天的全部经验。

---

## 目录

- [一、从"自动补全"到"AI 工程师团队"的思维转变](#一从自动补全到-ai-工程师团队的思维转变)
- [二、Codex 的五种使用表面](#二codex-的五种使用表面)
- [三、AGENTS.md — 你仓库里最重要的文件](#三agentsmd--你仓库里最重要的文件)
- [四、Skill 系统：封装可复用的 Agent 能力](#四skill-系统封装可复用的-agent-能力)
- [五、Sub-agents：真正的多 Agent 协作](#五sub-agents真正的多-agent-协作)
- [六、多 Agent 架构设计模式](#六多-agent-架构设计模式)
- [七、Codex Cloud：并行任务与水平扩展](#七codex-cloud并行任务与水平扩展)
- [八、验证机制：如何信任 Agent 的输出](#八验证机制如何信任-agent-的输出)
- [九、自动化运维：无人值守的定时任务](#九自动化运维无人值守的定时任务)
- [十、MCP 集成：扩展 Agent 的边界](#十mcp-集成扩展-agent-的边界)
- [十一、Chrome 扩展与 Mobile App](#十一chrome-扩展与-mobile-app)
- [十二、Codex SDK：将 Agent 嵌入你的管道](#十二codex-sdk将-agent-嵌入你的管道)
- [十三、十大常见错误与解决方案](#十三十大常见错误与解决方案)
- [十四、实战 Recipe 大全](#十四实战-recipe-大全)
- [十五、快速参考 Cheat Sheet](#十五快速参考-cheat-sheet)

---

## 一、从"自动补全"到 AI 工程师团队的思维转变

### Codex 到底是什么

大多数人以为 Codex 是一个更聪明的自动补全。**它不是。**

Codex 是一个完整的 **Agentic 软件开发平台**。它能：
- 读取你的整个代码库
- 编写和测试代码
- 审查 Pull Request
- 控制你的 Mac 桌面
- 浏览网页
- 生成图片
- 调度定时任务
- 跨会话记住你的偏好

**思维转变：** 你不再是写代码的人，而是**审查代码的人**——你的背后是一个永不睡觉的初级工程师团队。

### 工作单元的变化

| 旧思维（Autocomplete） | 新思维（Agent） |
|----------------------|----------------|
| 单元是"轮次"（turn） | 单元是**任务**（task） |
| 输出是"聊天回复" | 输出是 **PR** |
| 提示："写一个函数做 X" | 提示："实现功能 Y，约束条件如下，完成后跑测试" |

### 2026 年 5 月的模型选择

| 模型 | 用途 | 备注 |
|------|------|------|
| **GPT-5.5** | 默认模型，处理大多数任务 | 延迟不变但 token 用量显著减少 |
| **GPT-5.3-Codex** | 长时间自主运行、大重构、并行 Cloud fan-out | 比前代 Codex 专精模型快 25% |
| **GPT-5.5 Pro** | 最高推理能力 | 仅 Pro / Business / Enterprise 计划 |
| **Codex Mini** | 学习用途 | ChatGPT Free 永久免费 |

**实践建议：** 默认用 GPT-5.5，大 Agent 任务切到 GPT-5.3-Codex。

### 真实案例：WorkOS

WorkOS 的开发者现在每天早上冲咖啡前排队 4-5 个 Codex 任务。到他们坐下来时，2-3 个完成的 PR 已经在等审查了。这些任务处理了过去消耗他们 30-40% 时间的维护工作。

---

## 二、Codex 的五种使用表面

选择使用表面取决于你**想多紧密地跟随 Agent 的工作**。

| 表面 | 适用场景 | 工作位置 | 启动时间 |
|------|---------|---------|---------|
| **CLI** | 脚本化工作流、单任务、无头自动化 | 本地机器 | — |
| **IDE 扩展** | 交互式编辑、精确文件上下文操作 | VS Code / Cursor / JetBrains | — |
| **Desktop App** | 多线程工作流、浏览器、Computer Use、Goal 模式、Appshots、自动化 | macOS (2026.02) / Windows (2026.03) | 独立桌面应用 |
| **Cloud** | 异步后台任务、并行 PR、让你睡觉时工作 | 沙箱容器 + GitHub repo | Desktop App 中启动 |
| **In-app 浏览器 + Computer Use** | UI 验证、前端迭代、端到端测试 | 本地 dev server + 浏览器 | Desktop App 内置 |

### 实际组合策略

```
CLI          → 脚本化操作
IDE          → 交互式功能开发
Cloud        → 不需要盯着看的并行任务
App + Goal   → 长时间运行的定向任务
```

---

## 三、AGENTS.md — 你仓库里最重要的文件

> AGENTS.md 是区分"能用"和"好用"的唯一分界线。

### 什么是 AGENTS.md

- 一个位于仓库根目录的纯 Markdown 文件
- 每次 Codex 会话启动时**自动读取**
- **开放标准**——Codex、Cursor、Gemini CLI、Windsurf、GitHub Copilot 都支持

### 读取优先级

```
~/.codex/AGENTS.md          ← 个人级别，应用于所有项目
<project>/AGENTS.md         ← 项目级别
AGENTS.override.md          ← 覆盖文件（同级优先级最高）
```

合并上限：**32 KiB**。

### 写入的内容

✅ **应该放入：**
- Stack、框架、语言版本、包管理器
- **精确可复制的**构建/测试/运行命令（不是"跑一下常规测试"）
- 文件结构约定和命名规则
- 风格和模式规则
- **禁区**：哪些不能碰
- 发布要求：CI、PR 规范、部署机制

❌ **不应该放入：**
- 密钥或凭证（文件在版本控制中）
- 模糊指导（"写干净的代码"对 Agent 没有意义）
- 重复 README 的文档

> **黄金标准：** 控制在 **500 词**以内。过长会把有用上下文挤出模型工作记忆。

### 工作模板

```markdown
# Project: [项目名]

## Stack
- Language: [语言] [版本]
- Framework: [框架] [版本]
- Package manager: [工具]

## Commands
- Build: [精确命令]
- Test: [精确命令]
- Dev server: [精确命令]

## Conventions
- [具体约定1]
- [具体约定2]

## Forbidden
- [不要碰的文件/目录]
```

### 验证 Codex 是否读到了

```bash
# 直接问：
"总结你当前加载的指令"
```

### 大项目最佳实践

对于 monorepo，在子目录中放置额外的 AGENTS.md：

```
packages/api/AGENTS.md    ← 比根级 AGENTS.md 优先级更高
```

### /init 命令——快速启动

```bash
# 在新项目中的第一件事
codex /init
```

Codex 扫描目录和 Git 历史，识别语言、框架、构建命令、测试命令，自动生成 AGENTS.md。**审查、调整、提交。** 然后才开始真实工作。

---

## 四、Skill 系统：封装可复用的 Agent 能力

### 什么是 Skill

Skill 是给 Agent 使用的**可复用指令模板**。写一次，到处用。

### Skill 放置位置

```
$HOME/.agents/skills/       ← 个人技能（所有项目可用）
<project>/.agents/skills/   ← 团队技能（仅限项目内）
```

### Skill 的组成部分

一个完整的 Skill 包含三个文件：

```
skills/<name>/
├── SKILL.md        ← 主要指令（给 Agent 读）
├── scripts/        ← 辅助脚本
└── config/         ← 配置文件
```

### 编写一个"新功能"Skill 的模板

```markdown
# skill: new-feature

## Context
You are implementing a new feature for [项目类型].

## Process
1. Read the PRD and AGENTS.md
2. Plan first → wait for approval
3. Write tests for happy path + one error case
4. Implement
5. Anything ambiguous → ask before generating code

## Constraints
- Do NOT modify existing tests unless explicitly told
- Follow existing code style (see AGENTS.md)
- One PR per feature
```

### Skill 在对话中使用

```bash
# 在 CLI 或 IDE 中引用
@use new-feature
"Implement user profile page with avatar upload"
```

---

## 五、Sub-agents：真正的多 Agent 协作

### 什么是 Sub-agents

Sub-agents = Agent 的 Agent。主 Agent 可以创建多个子 Agent，各自独立工作，相互隔离。

### 子 Agent 配置

```
.codex/agents/<name>.md
```

每个子 Agent 有自己的：
- 独立的系统提示词
- 独立的工作区
- 独立的状态

### 常见子 Agent 模式

| 子 Agent | 职责 |
|---------|------|
| `reviewer` | 审查主 Agent 的输出（独立上下文，无原输出偏见） |
| `investigator` | 诊断 Bug，只分析不修复 |
| `tester` | 并行编写测试 |
| `web-researcher` | 浏览网页收集信息 |
| `ui-verifier` | Computer Use 验证 UI 正确性 |

### 实践案例

```yaml
# .codex/agents/reviewer.md
name: PR Reviewer
role: "你是严格的代码审查者。对主 Agent 的输出持怀疑态度。"
instructions: |
  - 不要假设上述代码是正确的
  - 检查：
    1. 安全性：SQL 注入、XSS、敏感数据泄露
    2. 边界条件：空值、大输入、并发
    3. 测试覆盖：是否有足够的测试
    4. 与 AGENTS.md 的一致性
```

---

## 六、多 Agent 架构设计模式

### 模式 1：Manager / Worker（管理者 / 工作者）

```
主 Agent (Manager)
├── 制定计划、拆解任务
├── 子 Agent 1: 实现前端的用户页面
├── 子 Agent 2: 编写后端 API
├── 子 Agent 3: 编写测试
└── 主 Agent 整合并审查结果
```

### 模式 2：Bureaucrat（官僚链）

适合"先做 X，再做 Y，结果必须通过 Z 验证"的流水线。

```
feature-Agent → reviewer-Agent → deployment-Agent
     ↓              ↓                  ↓
   写代码         审查代码           部署到 staging
```

### 模式 3：Specialist Team（专家团队）

```
Feature Squad
├── Database Specialist: 只处理数据模型和迁移
├── API Specialist: 只处理 REST/gRPC 端点
├── Frontend Specialist: 只处理 UI 组件
└── QA Specialist: 只处理测试和端到端验证
```

### 模式 4：Competition（竞争/交叉验证）— 黄金标准

```bash
# Codex 写代码，Claude Code 审查
# 跨提供商的验证捕获单一模型族系的盲点
```

### Cloud Fan-Out

```
主 Agent 创建任务列表
├── Cloud Task 1: 实现功能 A
├── Cloud Task 2: 实现功能 B
├── Cloud Task 3: 实现功能 C
└── Cloud Task 4: 实现功能 D
        ↓
20 分钟后，4 个 PR 等着你审查
```

---

## 七、Codex Cloud：并行任务与水平扩展

### 核心概念

Codex Cloud 把 Codex 从一个快速的编码助手变成了**水平可扩展的初级工程师团队**。

提交任务 → Codex 启动预加载你 repo 的沙箱 → 工作 → 运行测试 → 打开 PR。你的本地机器不受影响。

### 基本用法

```bash
# 提交单个 Cloud 任务
codex cloud "Implement user profile API endpoint"

# 并行提交多个任务
codex cloud "Task 1: Add user search endpoint"
codex cloud "Task 2: Add user cache layer"
codex cloud "Task 3: Write integration tests"
codex cloud "Task 4: Update API docs"

# 查看所有任务状态
codex cloud list

# 将 Cloud 任务变更拉到本地
codex cloud apply <task-id>
```

### CSV Fan-Out

创建一个包含多行的 CSV 文件，每行是一个独立任务，Codex 自动并行分发。

```
codex cloud < tasks.csv
```

---

## 八、验证机制：如何信任 Agent 的输出

> **写作已经解决。验证是瓶颈。** 5 个并行 Cloud PR = 5 个出 Bug 的机会。

核心问题：**奉承偏差（Sycophancy）**——写代码的模型倾向于认为自己的代码是正确的。让它自审，90% 它会说"没问题"。

### 两种结构性修复方案

#### 方案 1：auto_review（内置审查子 Agent）

```yaml
# 内置：Codex 的自动审查子 Agent
# 新上下文，对原输出无投入
# 更有可能标记真正的问题
```

#### 方案 2：跨提供商验证（Gold Standard）

```
Codex 写代码     →      Claude Code 审查
    ↑                         ↑
 模型家族 A                模型家族 B
```

跨提供商审查能捕获单一模型族系的系统性盲点。这是生产环境代码的**最低可行验证习惯**。

### Computer Use 行为验证

"测试通过" ≠ "功能实际工作"。让 Codex：
1. 打开本地 dev server
2. 点击相关流程
3. 截图结果
4. 与 PRD 对比

```bash
# 示例提示
"Open the dev server at localhost:3000, navigate to the user profile page,
upload an avatar, screenshot the result, and verify the UI matches the
design spec in /docs/profile-design.md"
```

### 最低可行验证流程

```
每个 PR 的黄金流程：
1. 用 auto_review 运行自动化审查（不同模型）
2. 先读审查摘要
3. 审查通过后 → 打开 diff
4. diff 中只读"品味"，不读"正确性"
5. UI 变更 → 看截图
```

---

## 九、自动化运维：无人值守的定时任务

### 什么是 Automations

Automations = 在专用工作树中按计划运行的 Codex 任务。从 Automations 面板设置：名称、项目、提示词、调度、执行环境。

### 线程复用（2026 年 4 月新特性）

Automations 可以在运行之间复用线程，**积累上下文**，随时间变得更聪明。

### 三个必设的 Starter Automation

#### 1. 每周依赖审查（周一早上 6 点）

```yaml
prompt: |
  运行 pnpm outdated 和 pnpm audit。
  报告 critical、major、minor 发现。
  安全的小版本和补丁升级 → 自动 PR。
  不碰 critical 和 major 更新（需要人工决策）。
```

#### 2. 每日 Sentry 分类（工作日早上 8 点）

```yaml
prompt: |
  获取过去 24 小时的错误，按指纹分组。
  对于出现 ≥3 次的每组：
    - 定位文件和行号
    - 读取相关代码
    - 识别根因
  发布 triage 报告。只诊断，不修复。
```

#### 3. 每周过期 PR 清理（周五下午 5 点）

```yaml
prompt: |
  列出所有超过 7 天的开放 PR。
  对每个 PR 判断：
    - 在等你响应
    - 在等待审查
    - 已经过期
  发布提醒评论。不关闭或合并任何内容。
```

### 自动化原则

> 杀掉任何**输出不再被阅读**的自动化。

好的自动化应该：
- ✅ 节省了你**肯定会做**的重复性任务
- ✅ 产生**一条可扫描的输出**
- ✅ **不采取破坏性行动**（无人值守时）

---

## 十、MCP 集成：扩展 Agent 的边界

Automations 处理仓库内部的事务。**MCP（Model Context Protocol）** 让 Codex 与仓库外部的一切交互。

### MCP 部署方式

| 方式 | 适用场景 |
|------|---------|
| **STDIO** | Codex 启动本地进程，通过 stdin/stdout 通信。覆盖 95% 的单人使用场景 |
| **Streamable HTTP** | Codex 连接网络端点。用于托管团队 MCP |

### 配置 MCP 服务器

直接在 `~/.codex/config.toml` 中：

```toml
[mcp.servers]
[mcp.servers.my-custom-tool]
command = "node"
args = ["path/to/mcp-server.js"]
```

### 权限控制

```toml
# 按工具配置
# 读操作自动批准，写操作先问
[mcp.servers.my-tool]
auto-approve = ["read_*", "list_*"]
```

### Docker MCP Toolkit

一条命令连接 220+ 个预构建的 MCP 服务器：

```bash
docker mcp-client configure codex
```

### ⚠️ MCP 陷阱

每个 MCP 服务器为 Codex 的上下文添加工具定义，**消耗 token 和稀释注意力**。只启用你**实际使用**的。

---

## 十一、Chrome 扩展与 Mobile App

### Chrome 扩展

核心优势：**可以访问已验证的网站**（LinkedIn、Salesforce、Gmail、Workday 以及任何需要登录的内部工具）。

- 通过 Desktop App 的 Plugins 面板安装
- 可以从任何 Codex 线程中调用
- **可以控制多个 Chrome 标签页**（不同线程的子 Agent 各自隔离）
- 能访问 **Web Developer Tools** → 检查 DOM、读取 Console 错误、诊断运行时问题

### Mobile App（2026 年 5 月 14 日发布）

Codex 进入 ChatGPT mobile app（iOS + Android）。

Mobile Codex 是一个**远程监控和控制面**，不是代码编辑器。

**你能在手机上做的事：**
- 观察跨笔记本、devbox 或远程环境的实时运行
- 浏览线程，在并行任务间跳转
- 审查 diff，在合并分支前查看
- 批准或拒绝 Codex 要在你硬件上执行的命令
- 中途更换模型
- 从 GitHub Issue 直接启动任务
- 对 Codex 打开的 PR 发表评论

**典型闭环：** 早上出门前启动一个 Goal 模式 → 通勤路上检查进度 → 从手机批准暂停的决策 → 走进办公室时前两个 PR 已经打开了。

---

## 十二、Codex SDK：将 Agent 嵌入你的管道

### JavaScript SDK

```javascript
import { Codex } from 'codex-app-server';

const codex = new Codex();

// 启动新线程
const thread = await codex.threadStart({
  prompt: 'Refactor the authentication module',
  model: 'gpt-5.3-codex',
});

// 在同一线程上继续对话
const result = await codex.run(thread.id, 'Add error handling');
```

### 关键 API

```javascript
// 恢复已保存的线程
await codex.resumeThread(threadId);

// Python SDK
from codex_app_server import Codex
thread = codex.thread_start(model="gpt-5.5")
```

> ⚠️ KSDK 目前是实验性的，需要本地 Codex CLI 安装。通过 JSON-RPC 与本地 app-server 通信，控制的是你在 Desktop App 中与之交互的同一个 Agent。

---

## 十三、十大常见错误与解决方案

| # | 错误 | 解决方案 |
|:-:|------|---------|
| 1 | **模糊的任务描述** | 指定具体输出、文件、约束。如果你说不清楚，任务还没准备好 |
| 2 | **没有 AGENTS.md** | 写一个。烂的总比没有强 |
| 3 | **跳过计划** | 在非琐碎任务前加"先输出计划" |
| 4 | **多任务写在同一个提示中** | 一个提示一个任务。并行任务用 Sub-agents 或 Cloud |
| 5 | **一上来就放开全部权限** | `workspace-write` + `on-request` 是合适的默认项 |
| 6 | **挂载太多 MCP 和插件** | 保持精简。不用的禁用 |
| 7 | **自审** | 用 `auto_review` 或另一个工具。写代码的模型对自己的代码有偏见 |
| 8 | **编译通过 = 正确** | 加上行为验证。UI 变更用 Computer Use |
| 9 | **过度并行** | 只有**独立的**工作可以并行。共享文件的必须串行 |
| 10 | **无边界 Goal 模式** | 设置最大 PR 数、最大代码行数、最长时间、明确的停止条件 |

---

## 十四、实战 Recipe 大全

### Recipe 1：实现新功能

```yaml
Skill: new-feature
Process:
  1. 读取 PRD 和 AGENTS.md
  2. 先做计划 → 等待批准
  3. 测试覆盖 happy path + 一个错误场景
  4. 如果任何内容不明确 → 先问再写代码
```

### Recipe 2：修复 Bug

```yaml
Skill: investigate
Process:
  1. 只诊断
  2. 输出：
     - 复现步骤
     - 根因假设
     - 验证计划
  3. 确认后才开始修复
```

### Recipe 3：重构

```yaml
Process:
  1. 用 grep 列出所有受影响位置
  2. 输出迁移计划 → 等待批准
  3. 所有现有测试必须不修改通过
  4. 如果测试需要更新 → 测试错了，停止并报告
  5. 一个 PR
```

### Recipe 4：第三方集成

```yaml
Process:
  1. 封装到 /lib/integrations/[name].ts
  2. 添加环境变量到 .env.example
  3. 这个 PR 不包含 UI
  4. 以 Draft 模式打开，供手动测试
```

### Recipe 5：测试补全

```yaml
Process:
  1. 输出测试计划（happy path + edge cases + error cases）
  2. 等待批准
  3. 所有测试必须通过现有生产代码
  4. 不改生产代码
```

### Recipe 6：依赖升级

```yaml
Process:
  1. 阅读版本间的 release notes
  2. 列出 breaking changes
  3. 等待批准
  4. 更新并应用代码变更
  5. 跑测试直到全绿
```

### Recipe 7：Goal Mode 项目

```yaml
Bounds:
  - 最大 PR 数
  - 每个 PR 最大代码行数
  - CI 作为 PR 间门禁
  - 明确的停止条件
  - 遇到 AGENTS.md 中没有的架构决策 → 暂停
  - 遇到 Breaking API 变更 → 暂停
```

---

## 十五、快速参考 Cheat Sheet

### CLI 命令速查

| 命令 | 功能 |
|------|------|
| `codex /init` | 初始化 AGENTS.md |
| `codex trust .` | 启用项目级配置 |
| `codex cloud "task"` | 提交 Cloud 任务 |
| `codex cloud list` | 查看所有 Cloud 任务 |
| `codex cloud apply <id>` | 将 Cloud 任务变更拉到本地 |

### 关键文件位置

| 文件 | 用途 |
|------|------|
| `~/.codex/config.toml` | 全局配置（审批模式、沙箱模式、MCP、模型默认值） |
| `~/.codex/AGENTS.md` | 个人级别 AGENTS.md（适用于所有项目） |
| `<project>/AGENTS.md` | 项目级别 AGENTS.md |
| `AGENTS.override.md` | 覆盖（同级最高优先级） |
| `~/.codex/memories/` | 跨会话记忆 |
| `$HOME/.agents/skills/` | 个人 Skill |
| `<project>/.agents/skills/` | 团队 Skill |
| `.codex/agents/<name>.md` | 子 Agent 配置 |

### 四段式提示结构

```
1. Tell    : 目标，不是方法
2. Show    : 示例输入和期望输出
3. Describe: 要使用的 API、库和模式
4. Remind  : AGENTS.md 中的约定
```

---

> **原文作者**：Avid (@Av1dlive)
> **发布时间**：2026 年 5 月
> **原文平台**：X (Twitter) 长文
> **本文基于作者的笔记、研究和个人经验编写，经 AI 模型（Sonnet 4.6）编辑。**
