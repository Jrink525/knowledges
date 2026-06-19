---
title: "7 天入门：搭建你的第一个 Claude Code Agent"
tags:
  - claude-code
  - agent
  - ai-coding
  - workflow
  - best-practices
date: 2026-06-19
source: "https://x.com/zaimiri/status/2067959107890364677"
authors: "zaimiri"
---

# 7 天入门：搭建你的第一个 Claude Code Agent

> **来源：** [7-Day Guide: Build Your First Claude Code Agent](https://x.com/zaimiri/status/2067959107890364677) — by @zaimiri

---

大多数人用 Claude Code 的方式跟用 ChatGPT 一样：开终端 → 问修复 → 贴报错 → 接受 diff → 祈祷没搞坏。

小任务还行，**仓库一大、任务一模糊、需要判断力的时候就开始崩了**。

解法不是"给更多自主权"，而是一套**轻量 Agent 栈**：

- 1 个上下文文件
- 3 个技能
- 3 个子 Agent
- 2 个钩子
- 窄范围 MCP
- 无聊的权限

这套足够让 Claude Code 稳定很多。以下是分 7 天上手的搭建路径。

---

## 第 1 天：创建仓库上下文

从单个文件开始：**`CLAUDE.md`**

这是 Claude Code 学习仓库规则的地方。保持简短，一个能用的初版：

```
# Project Overview
This is a Spring Boot REST API service.

# Conventions
- Java 21, use records for DTOs
- Controller → Service → Repository pattern
- Test classes end with *Test.java
- Use JUnit 5 + Mockito

# Code Style
- No Lombok
- Constructor injection over @Autowired
- Use SLF4j for logging

# Project Structure
src/main/java/com/example/
├── controller/
├── service/
├── repository/
├── model/
└── config/
```

**不要写一本宪法。** Claude 只需要编辑时实际用到的规则。

---

## 第 2 天：添加三个技能

技能是可重复的工作流。当你总让 Claude Code 做类似的事时，就该写成技能。

推荐起步的三个：

| 技能 | 用途 |
|------|------|
| **Research 技能** | 调研新库 / API / 问题根因 |
| **QA 技能** | 写单元测试 + 覆盖率检查 |
| **Release Notes 技能** | 按 commit 历史生成更新日志 |

这些技能的核心价值：**不用每次都重新解释流程**。

---

## 第 3 天：拆分成三个子 Agent

不要从十个 Agent 开始。先分三个：

| Agent | 职责 |
|-------|------|
| **Researcher（研究员）** | 调研、分析、出方案 |
| **Builder（构建者）** | 写代码、改代码 |
| **Reviewer（审查者）** | 审查 diff、检查质量 |

这修补了一个常见问题：让一个 Agent 既要调研、写代码、自我审查、又要解释结果——虽然不是不行，但一定会漏东西。**分阶段给 Agent 更干净的任务**。

---

## 第 4 天：加无聊的钩子

钩子应强制你**始终**想检查的事。

起步推荐：

- **Test Hook**：提交前跑测试，失败则阻断
- **Pre-commit Hook**：检查不要提交生成文件、本地配置、密钥、无关修改

**不要让钩子很聪明，让它们无聊。** 无聊的检查能省掉昂贵的错误。

---

## 第 5 天：只在关键处连 MCP

MCP 在 Claude 需要仓库外的上下文时才有用。

**好的首批连接：**
- GitHub Issues / PRs
- 项目文档
- 错误日志（Sentry）
- 数据库 Schema
- 设计系统文档

**坏的首批连接：**
- 所有工作空间
- 所有收件箱
- 所有数据库
- 每个文档目录
- 每个内部工具

**更多权限 ≠ 更好。** 权限越多，Agent 分心或碰错东西的机会越多。MCP 只在任务真需要的时候连。

---

## 第 6 天：把权限写清楚

好用的编码 Agent 仍然需要硬边界。

**Claude 可以：**
- 读项目文件
- 搜索仓库
- 提出修改
- 按要求做范围内的改动
- 跑安全的本地检查

**Claude 必须先问：**
- 安装包
- 改 env 文件
- 删文件
- 动密钥
- 跑迁移
- 部署
- force-push
- 大规模重构

很多人想让 Agent 先自主再可靠——**但是可靠性先于自主权**。

---

## 第 7 天：跑一个完整工作流

现在用搭建的 Agent 栈处理一个真实任务。

### 工作流

```
想法
  → Researcher 调研
    → Builder 做最小的有用改动
      → QA Skill 检查
        → Reviewer 审查 diff
          → Hook 确认测试通过
            → Release-notes Skill 总结改动
```

### 示例 Prompt

```
📝 任务：给用户模块加一个分页查询接口

1. [Researcher] 调研现有代码中的分页模式
2. [Builder] 添加带 Pageable 参数的 Controller + Service
3. [QA Skill] 为新增接口写单元测试
4. [Reviewer] 审查 diff 确认符合项目规范
5. [Hook] 跑 mvn test 确认全部通过
6. [Release-notes Skill] 总结本次改动
```

这里的关键区别：你不是只说"修一个 bug"，而是给 Claude 一条**路径**：调研 → 编辑 → 测试 → 审查 → 总结。这条路径是输出更可靠的原因。

---

## 新手常见错误

**错误：** 试图一开始就搭建一个巨型编码 Agent。

**应该：** 一个仓库 → 一个 CLAUDE.md → 三个技能 → 三个子 Agent → 两个钩子 → 一个窄 MCP 连接（如果需要）→ 清晰的权限 → 一个真实任务。

然后只在真实工作暴露出缺口时改进这套栈。

一个好的 Claude Code 配置不应该像一堆 Agent 文件。它应该像一个仓库——AI 知道规则、按流程走、检查自己的工作、每周少一点随机出错。

---

## 源码链接

- [Claude Code 官方文档](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Claude Code Sub-Agents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)
- [Claude Code Hooks](https://docs.anthropic.com/en/docs/claude-code/hooks)
- [Claude Code Skills](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Claude Code MCP](https://docs.anthropic.com/en/docs/claude-code/mcp)

---

## 给 Java / Spring AI 开发者的对标

| Claude Code 概念 | 对等你已有的 |
|-----------------|-------------|
| CLAUDE.md | AGENTS.md / TOOLS.md |
| Skills | 可复用的 Tool 函数 |
| Sub-Agents | LangGraph 子节点 / Pydantic AI 多 Agent |
| Hooks | Spring AOP / Advisor 拦截器 |
| MCP 窄权限 | 按需注册 Tool Calling |

这套思路可以直接迁移到 Spring AI + Pydantic AI 的 Agent 体系里。

---

> *Processed on 2026-06-19 from https://x.com/zaimiri/status/2067959107890364677*
