---
title: "写出好 AGENTS.md 的 10 堂课：让 Codex 和 Claude Code 真正理解你的项目"
tags:
  - agent-engineering
  - claude-code
  - openai-codex
  - agents-md
  - ai-coding
date: 2026-05-31
source: "https://x.com/voxyz_ai/status/2060753730643837205"
authors: "Vox (@Voxyz_ai)"
---

# 写出好 AGENTS.md 的 10 堂课：让 Codex 和 Claude Code 真正理解你的项目

> 一个 markdown 文件 + 一个名人名字 = 162K 星标（andrej-karpathy-skills）。名字确实拉了很多流量，但它能火是因为击中了一个真实痛点：每个人都把自己的代码交给 AI，而绊倒所有人的是同一件事——模型会写代码，但它不知道你的项目规则。
>
> 这篇文章不是 AGENTS.md 格式化教程。它是**实战中总结的 10 堂课**：哪些反直觉的做法真正有效，哪些坑你只需要踩一次。我同时使用 Codex 和 Claude Code，以下内容对两者都适用。

![Cover](../image/agents-md-10-lessons-1.jpg)

---

## 第 1 课：短就是好。200 行是上限。

你可能会想：信息越多，工具理解越准。**事实恰恰相反**——写越多，工具越容易错过那几行真正重要的内容。

入口文件在每次会话开始时**完整加载**。每行废话都在挤占工具的上下文空间。

- **Codex**：`project_doc_max_bytes` 默认 32 KiB，但它不是简单地截断一个文件——它会从全局 → 项目根 → 当前目录**串联拼接**，一旦总量达到上限就停止添加。前面写太多，靠近任务的关键规则反而被挤掉。
- **Claude Code**：官方建议控制在 **200 行以内**，且 `CLAUDE.md` 会完整加载，越长→遵守率越差。

**最佳实践：** 根文件保持在 **100-200 行**。超过的部分拆到 `docs/` 或子目录中。

> **快速检验标准：** 一个从未看过你项目的工程师，应该在 30 秒内回答出：这是什么项目、怎么运行、代码放哪里、如何验证改动。

---

## 第 2 课：不引入什么，和引入什么同样重要

你列出了技术栈，以为工具就不会乱来。但它不知道你的项目包袱——它会"好心"地用自己知道的"最佳"方案，而这个方案**可能和你项目的迁移计划/惯例相冲突**。

Codex 和 Claude Code 都会自主执行命令、编辑文件、请求权限。在 Codex 默认的 Auto preset 下，工作区内读写和常规命令自动执行，写入工作区外或访问网络才需确认。仅列技术栈的文件**拦不住任何东西**。

所以"不要做"清单应该有两层：
- **Do NOT introduce**（永远不要引入什么）
- **Stop and ask**（什么决定不能自己做）

> 一个"不要做"清单不是情绪宣泄，它是**决策的压缩记录**。附带 Reason（原因）和 Revisit（何时可以放宽），工具才知道为什么有这个规则、什么时候可以放松。
>
> Stop-and-ask 列更重要——它不是禁令，而是说：**这个决定不是你一个人能做的。**

---

## 第 3 课：写工具**能检查**的规则

"写干净的代码"听起来像好规则，但对工具来说等于什么都没说。

工具看不懂"干净"、"简单"、"高性能"。它看得懂的是：
- "使用命名导出 (named exports)"
- "组件不超过 200 行"
- "用 async/await 而不是 .then() 链"

Codex 和 Claude Code 都会运行命令来检查自己的工作，所以"完成意味着什么"也要写清楚：

| 动作 | 检查方法 |
|------|---------|
| 添加 API 端点 | 运行测试 |
| 数据库迁移 | 验证 schema |
| 前端改动 | 构建无报错 |

> **快速检验：** 读完一条规则后，你能在 5 秒内判断一段代码是否遵守了它吗？能→好规则。不能→重写。

---

## 第 4 课：写下**行为规范**，而不仅仅是项目知识

你觉得该写的是项目知识。但工具真正脱轨的地方是**行为**，不是知识。

- 它不确定时不会问，而是选一种理解直接往前冲
- 它不该停时不停，顺手把你隔壁的代码也"优化"了
- 它过度自信时，会冲进它不该碰的目录

那棵 162K 星标的仓库火起来，正是因为这一层。它没有描述任何具体项目，只是把 Karpathy 观察到的几个失败模式转化为了行为规则。

> 把下面这些**复制进你的文件**：
> - 不确定时停下来问
> - 做最小改动，不做附带重构
> - 完成后跑验证
> - 解释你的推理

---

## 第 5 课：AGENTS.md 是路由器，不是图书馆

诱惑是把所有架构文档塞进这一个文件。但它的职责不是存储——而是**指路**。

- **普通用户的入口文件**：知识倾倒场
- **高手用户的入口文件**：路由器

```markdown
# 架构 → 见 docs/architecture.md
# 数据库 → 见 docs/db/schema.md
# 复杂计划 → 见 .agent/PLANS.md
```

### PLANS.md 最有价值

在 `.agent/PLANS.md` 写规划，分成多个阶段，等你确认后再执行。

**我（作者）的设置：**
1. 在隔离的 **worktree**（独立分支 checkout）中运行
2. 睡前放一个清晰的目标
3. 早上检查一串提交记录和验证笔记
4. 最长一次跑了 **36 小时**——从头到尾解决一个完整架构问题，成果不错
5. 见过有人跑 **6 天**的

> 它能跑这么长，只因目标写得紧、阶段切得细。前提条件：测试通过、沙箱限制操作范围、每阶段可回滚、机器上**没有生产凭据和写入权限**。没有这些，就不是自动化，而是把实习生锁在生产服务器上过夜。

**分阶段模板：**

```
GOAL: [一句话描述要完成的任务]
PHASE 1: [理解或调查]
PHASE 2: [实现]
PHASE 3: [验证]
CONSTRAINTS: [不做什么]
WAIT FOR APPROVAL: [between phases]
```

### Codex vs Claude Code 寻址差异

- **Codex**：按需加载，用到时才取文档
- **Claude Code**：import 会**完整拉入**启动上下文，所以别用它挂大文档，改用 skills 或路径作用域的 `.claude/rules/`

> 如果根文件看不到大段文档文本，只有"需要 X 时，去读 Y"，你就做对了。

---

## 第 6 课：敏感目录放独立的本地文件

有些模块的风险是其他模块的 **10 倍**。给它们单独的本地文件。

两个工具都会从项目根目录往下扫描到当前目录：
- **Codex**：更接近**覆盖**——同级目录下 `AGENTS.override.md` > `AGENTS.md`，近的覆盖远的
- **Claude Code**：更像**拼接**——多个 `CLAUDE.md` 按顺序缝合进上下文，越靠后权重越高，但如果规则矛盾，模型可能摇摆

### 示例：认证模块（高敏感度）

```markdown
# .agent/rules/auth/

在修改认证代码之前，先运行安全审计。
不要引入新的认证库。
所有密码变更必须有审批。
```

> 子目录文件应该只承载该目录的特定风险，**不要复制根目录的内容**。

---

## 第 7 课：文件表达意图，hooks/rules/sandbox 强制执行

你在文件里画了红线，以为工具会遵守。**它不会一直记得。** 不要把红线只留在文件里。

Anthropic 说得很直白：要真正阻止某个操作，**不管模型怎么决定**，就用 PreToolUse hook；写在 CLAUDE.md 里不算数。

### 分层强制执行体系

| 层 | 强度 | 说明 |
|----|------|------|
| AGENTS.md / CLAUDE.md | ⚪ 最低 | "请记住" |
| PreToolUse Hook | 🟡 中等 | 真实拦截，但非所有命令都被捕获 |
| Rules（Codex） | 🟡 中等 | 控制命令级策略 |
| Sandbox | 🟢 强 | 隔离环境 |
| 权限 / Deny 规则 | 🟢 强 | 硬性禁止 |
| 隔离 Worktree | 🟢 强 | CI + 无生产凭据 |
| 无生产凭据 | 🔴 绝对 | 最底层保障 |

**Codex Hooks：** 从 `~/.codex/hooks.json` 或 `<repo>/.codex/hooks.json` 加载，支持 PreToolUse、PostToolUse、Stop 等生命周期事件。

**Claude Code：** PreToolUse hook + `permissions.deny` + `sandbox.enabled` 是更硬的强制执行层。

> 文件里放的是"请记住"。用 hooks 拦截能拦截的，用 rules 治理能治理的，用 sandbox 隔离能隔离的，**不要再信任模型会自己遵守。** 动作越危险、越不可逆，就让它落在越靠下的层面。

---

## 第 8 课：长期记忆必须可审计。不要全交给工具。

每次新会话，工具都像失忆一样重新认识你的项目。你不需要向量数据库，也不应该把记忆全交给工具的内置系统。

- **Codex Memories**：默认关闭，部分地区不可用
- **Claude Code 自动记忆**：默认开启（v2.1.59+），Claude 把学到的写到 `MEMORY.md`，前 200 行 / 25KB 每次会话都加载

> 两家厂商都强调：**必须的团队规则放在文件里、在 Git 中**，自动记忆只是备份。

### 记忆评判标准

```
SAVE IF:
- 这是一个困难的修复，别人可能重蹈覆辙
- 这是一个架构决策，将来需要复习
- 这是一个会重复出现的配置/依赖问题

SKIP IF:
- 一次性调试发现
- 某个人的临时偏好
- 下一轮重构可能就变了
```

> 如果记忆是可审计的、可删除的、出现在 git diff 中的，它就是健康的。否则长期记忆慢慢变成长期污染。

---

## 第 9 课：三类文件分开存放

把个人偏好、团队约定和机器权限混到一个文件里——那你实际上在造一个**没人敢清理的抽屉**。

### 正确分层

| 文件 | 位置 | 内容 |
|------|------|------|
| 个人偏好 | 全局（`~/.codex/`） | 编辑器、个人简写、常用命令 |
| 项目约定 | 项目根 `.agent/` | 代码规范、架构规则 |
| 机器权限 | `hooks.json` / `rules` | 安全策略、禁止命令 |

**个人偏好示例（`~/.codex/rules.md`）：**

```markdown
我使用 Vim 键绑定
我用 pnpm 而不是 npm/yarn
测试命令：pnpm test
```

**项目根 `AGENTS.md`** 只包含项目的约定，不包含个人偏好。

---

## 第 10 课：一个真相来源，同时供给两个工具

如果你同时用 Codex 和 Claude Code，自然想法是各写一个文件。但**两个文件会漂移**，两个月后没人说得清哪个是对的。

Anthropic 明确：**Claude Code 读 `CLAUDE.md`，不是 `AGENTS.md`。**

### 修复方案：import

让 `AGENTS.md` 是唯一的真相来源，`CLAUDE.md` 只放一行 import：

```markdown
<!-- CLAUDE.md -->
Import: AGENTS.md

# Claude-specific extras (optional)
```

Claude Code 会把 import 的文件在启动时完整拉入，然后追加自己的内容。如果不需要 Claude 特有的内容，symlink 也可以：

```bash
ln -s AGENTS.md CLAUDE.md
```

> **不要维护两套完整的规则。** `AGENTS.md` 是来源，`CLAUDE.md` 只保留 import 和罕见的 Claude-only 补充。分开写，两个月后它们就不会匹配了。

---

## 可直接复制的骨架模板

```markdown
# Project
[一句话描述]

# Stack
[技术栈清单]

# How to Run
[运行命令]
[测试命令]

# Code Rules
- 使用命名导出
- 组件不超过 200 行
- async/await 而不是 .then()

# Do NOT Introduce
- 不移除旧的构建系统
- 不引入新的状态管理库

# Stop and Ask
- 涉及数据库迁移时停下来问
- 改变认证逻辑时停下来问

# Architecture
- 核心领域 → /domain
- API 层 → /api
- 基础设施 → /infra

# Verification
每个 PR 必须：通过测试 + 类型检查 + lint 无误
```

---

## 从哪里开始

1. **运行 `/init` 生成初稿**：Codex 生成 `AGENTS.md`，Claude Code 生成 `CLAUDE.md`（也会读取已有的 `AGENTS.md`）
2. **把根文件砍到 200 行 / 32 KiB 以下**，大文档移到 `docs/` 和 `PLANS.md`
3. **添加 Do NOT introduce 和 Stop and ask**，把危险操作交给 rules / hooks / sandbox 执行，不要只写在文件里
4. **`AGENTS.md` 作为真相来源**，通过 import 或 symlink 给 `CLAUDE.md` 使用。不要维护两套

---

## 全文总结

入口文件不是写一次就忘记的。它应该像测试套件一样**不断生长**——每次工具犯同样的错误，就把这个错误转化为更具体的规则；每次你需要手动解释某个流程，就转化为文档指针、hook、rule 或测试命令。

入口文件不是 agent 的知识库。它是 agent 的**工作契约**。

它回答四个问题：
1. 我在哪里，代码怎么跑？
2. 不确定时我该如何表现？
3. 我怎么证明工作完成了？
4. 哪些决定不是我能做的？

前三问由 AGENTS.md / CLAUDE.md 回答。第四问交给 config、rules、hooks、sandbox 和 CI。

一个月后 Codex 和 Claude Code 不会变得更聪明。**你只是把项目中隐性的知识，变成了它们在每次任务前都会读取、运行和验证的东西。**

---

## 参考来源

- [andrej-karpathy-skills（那棵 162K 星标的仓库）](https://github.com/multica-ai/andrej-karpathy-skills)
- [Codex AGENTS.md 官方指南](https://developers.openai.com/codex/guides/agents-md)
- [Codex 最佳实践](https://developers.openai.com/codex/learn/best-practices)
- [Codex Hooks](https://developers.openai.com/codex/hooks)
- [Codex Rules](https://developers.openai.com/codex/rules)
- [Codex Agent 审批与安全](https://developers.openai.com/codex/agent-approvals-security)
- [Codex Memories](https://developers.openai.com/codex/memories)
- [OpenAI Cookbook: PLANS.md](https://developers.openai.com/cookbook/articles/codex_exec_plans)
- [Claude Code 文档（Memory / AGENTS.md import）](https://code.claude.com/docs/en/memory)

---

*整理于 2026-05-31，原文来自 [Vox (@Voxyz_ai)](https://x.com/voxyz_ai/status/2060753730643837205)*
