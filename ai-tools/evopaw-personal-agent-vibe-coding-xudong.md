---
title: "个人 Agent 搭建 + Vibe Coding 实战 — EvoPaw 作者 30 天完整经验指南"
tags:
  - evopaw
  - vibe-coding
  - personal-agent
  - nanobot
  - claude-code
  - codex
  - superpowers
  - agent-development
  - vibe-coding-workflow
date: 2026-06-03
source: "https://x.com/xudong07452910/status/2062087939547332948"
authors: xudong07452910 (EvoPaw 作者)
---

# 个人 Agent 搭建 + Vibe Coding 实战指南

> **来源：** [xudong07452910 的 X 长文合集](https://x.com/xudong07452910/status/2062087939547332948)  
> **项目：** [EvoPaw — GitHub](https://github.com/hxdflying/EvoPaw)  
> **中文整理：** 作者用一个多月时间手搓个人 Agent EvoPaw 并持续迭代成日常工作系统的完整心法

> **核心观点：** 工具可以换，但真正懂你工作流、偏好和方法的系统，只有你自己能慢慢养出来。

---

## 第一章：为什么自己搭 Agent（主权问题）

面对 OpenClaw、Hermes Agent、Nanobot 等成熟框架，选择自己搭的理由：

### 1. 模块边界清晰
想换哪一层就换哪一层——provider、编排、记忆、技能——上层代码基本不动。现成框架很难做到。

### 2. 可以「偷」设计
- 读 **Hermes 的 Curator** 学技能自动演化
- 读 **Nanobot** 学依赖预检
- 读 **Pi-mono** 学多 provider 抽象
- 在自己的系统里跑一遍后，看别人项目不再是「一个整体框架」，而是一堆可以拆下来拼回去的零件

### 3. 数据和理解的主权
Agent 用久了会慢慢长出对你的「理解」——喜欢的格式、拆任务的方式、焦虑的事情。这些是长期互动里出现的**「二阶资产」**。平台 Agent 很难迁移，一年喂养出来的默契，换平台可能一夜归零。

### 4. 门槛已极低
2026 年有了 Claude Code、Codex 等 Vibe Coding 工具，**不需要是程序员**。改一行 prompt、让 AI 写一个 Skill、加一个记忆文件，就能让系统变成只属于你的样子。

> **建议路径：** 先用现成工具跑两周感受 → 然后带着挑剔去用 → 把所有别扭的地方记下来 → 从这些痛点开始自己动手。

---

## 第二章：15 天从 0 到日常使用 — 五步流程

### 基座推荐：Nanobot
代码干净、轻量、飞书等通道内置好、多 provider 支持。

### 五步流程

| 步骤 | 操作 | 说明 |
|------|------|------|
| **① 选基座** | 代码行数 < 8000，agent loop 一眼能看懂，能接飞书/Telegram | 能改得动才能长得久 |
| **② 安装跑通** | 用 Claude Code 装好，接飞书 | 飞书强烈走**长连接模式**（无需公网 IP、无需 webhook） |
| **③ 建脚手架** | `CLAUDE.md` + `docs/spec.md`、`docs/prompt_plan.md`、`docs/todo.md` | 跨会话持久化记忆，比任何 prompt 技巧都强 |
| **④ 模糊需求→清晰 spec** | 见第三章 | 整套流程最关键的一步 |
| **⑤ 每加功能配测试** | 见第四章 | 保持系统可重构 |

### 进阶玩法
- 从 Hermes、OpenClaw 等项目「偷」好设计
- 装 Codex MCP 实现双模型互审（第七章详解）

---

## 第三章：Vibe Coding 的命门 — 把模糊需求逼成清晰 Spec

> Vibe Coding 速度优势的前提是 spec 必须清楚。spec 越糊，AI 跑得越快，你死得越惨。

### 五步 Spec 流程（以「飞书群待办总结」为例）

**① 填需求表** — 逼自己说人话
写出：痛点、期望、不知道的地方。这一步能拦住 80% 的「想到哪写到哪」。

**② Plan mode 追问** — 让 Claude Code 反复追问
- 边界条件
- 错误处理
- 性能要求
- 与现有功能冲突

Claude Code 中开 Plan mode（Shift+Tab），全部问清楚。

**③ 输出 `docs/spec.md`** — 像合同一样写
- 用列表、表格
- 不要散文
- 能让别人按着实现出来的 spec 才算合格

**④（可选但强烈推荐）** 让 **Codex review** 这份 spec — 它能挑出你和 Claude 都意识不到的盲区

**⑤ 拆成 `prompt_plan.md` + `todo.md`**
每一步控制在 **2~5 分钟**，可以独立验收。

### 懒人神器
安装 **[obra/superpowers](https://github.com/obra/superpowers)** → 说"加个功能"会自动触发 brainstorming skill，硬约束你先把 spec 出清楚再动手。**新手装上能少踩 70% 的坑。**

---

## 第四章：测试 — 你敢重构的胆量

> Vibe Coding 时代，测试不是「防 bug」，而是真相通道。没有测试，你根本不知道 AI 改的这版有没有破坏旧功能。

### 反直觉：别让 AI 给自己写测试
AI 给自己写测试天然会作弊——测试和实现互为镜像，永远绿，看着安心，毫无防御能力。

### TDD 简化版五步走

1. AI 根据 spec 写测试（此时测试是红的）
2. 你 review 这些测试 —— **只测行为，不测实现细节**
3. AI 写实现，让测试变绿
4. 加 boundary case 和 adversarial case（故意喂坏数据）
5. 让 Codex review 一遍测试

### Superpowers TDD Skill 的 Iron Law
> 写了实现但没先写测试，就删掉重写。

听起来狠，但坚持两周后，真正的杠杆不是测试本身，而是**「敢重构」的勇气。**

---

## 第五章：Claude Code 和 Codex 关键配置

### 一、Claude Code 8 个关键配置（`~/.claude/settings.json` / `~/.zshrc`）

| # | 配置 | 作用 |
|---|------|------|
| 1 | 强制高思考强度 (`ANTHROPIC_THINKING_BUDGET`) | 提高推理质量 |
| 2 | 关掉自适应思考 | 防幻觉 |
| 3 | 子代理切到便宜的 **Haiku** 模型 | 账单砍到 1/5 |
| 4 | 主模型默认 **Sonnet**，硬骨头切 **Opus** | 性价比平衡 |
| 5 | 拉长单次输出上限 | 减少中断 |
| 6 | 开虚拟视口 + diff 渲染 | 不闪屏 |
| 7 | 关所有遥测 | 隐私 + 减少干扰 |
| 8 | bash 超时放宽到 **30 分钟以上** | 长任务不中断 |

### 二、Codex 10 个 TOML 配置（`~/.codex/config.toml`）

| # | 配置 | 效果 |
|---|------|------|
| 1 | 默认强模型 | 推理质量 |
| 2 | reasoning effort → high | 深度思考 |
| 3 | 审批策略 → `on-request` | 该问时问，不该问时不问 |
| 4 | 沙盒 → `workspace-write` | 默认断网安全 |
| 5 | 搜索 → cached | 节省费用 |
| 6 | 关 alternate screen | 减少视觉干扰 |
| 7 | 关 reasoning event 实时显示 | 减少干扰 |
| 8 | 关长期历史落盘 | 隐私 |
| 9 | 关 analytics | 隐私 |
| 10 | ...各项叠加质变 | 体验全面提升 |

> 每一项单独看都不起眼，但叠在一起，使用体验是质变。

---

## 第六章：新手必装 — Superpowers 纪律系统

> 新手做 Vibe Coding 最大的敌人，不是 AI 不够聪明，而是缺少强制纪律。

### 5 个必用 Skill（全部自动触发）

| Skill | 作用 |
|-------|------|
| **brainstorming** | 硬约束你出 spec 再动手 |
| **writing-plans** | 把 spec 拆成 bite-sized task |
| **test-driven-development** | 强制红绿循环 + Iron Law |
| **systematic-debugging** | 没复现就不许 fix |
| **verification-before-completion** | 没跑过验证命令不许 claim 完成 |

**第一周**严格跟着跑，养肌肉记忆。  
**一个月后**再碰剩下的 9 个 skill（worktree、parallel agents 等），避免心力分散。

---

## 第七章：双模型互审 — 破解自我盲区

> Claude 和 Codex 的训练分布不一样，盲区不重合。让它们互相 review，是目前性价比最高的 QA 方式。

### 配置方法
用 **MCP** 把 Codex 注册成 Claude Code 的工具（反过来也行），整个流程在一个 session 里跑。

### 4 个最值钱的互审场景

| 场景 | 互审内容 |
|------|---------|
| **Spec 互审** | 专门挑边界、歧义、隐含假设 |
| **测试互审** | 只看测试本身，揪出「装样子的测试」 |
| **Debug 二审** | 让另一方在**不看 fix 的前提下**独立诊断根因 |
| **重要 diff 互审** | 盯破坏接口、吞错、和 spec 不一致 |

### 两条铁律
1. **测试一定要让没写实现的那一方来写**
2. **Debug 一定要让对方在不看 fix 的前提下独立诊断**

只要这两条守住，互审就不会退化成两个模型互相点头。

---

## 结语：行动起来

> 用现成框架，你永远是用户。自己搭，你才有可能成为主人。

### 四件具体的事
1. **Fork Nanobot** 或类似的轻量项目
2. **装好 Claude Code / Codex**，改完第五章的配置
3. **装上 Superpowers**
4. **挑一个真实的痛点**，按 spec 流程跑一遍

> 一天改一行 prompt、一周加一个 Skill、一个月重构一次底层——它就会一点一点地，变成只懂你的那个系统。

---

### 相关链接
- **EvoPaw：** https://github.com/hxdflying/EvoPaw
- **Nanobot：** AI Agent 轻量框架（推荐基座）
- **obra/superpowers：** https://github.com/obra/superpowers
- **Hermes Agent：** 技能自动演化的参考来源
- **Pi-mono：** 多 provider 抽象参考来源

---

*整理于 2026-06-03，基于 [xudong07452910 的 X 长文合集](https://x.com/xudong07452910/status/2062087939547332948)*
