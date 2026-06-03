---
title: "使用 Autoresearch 优化 Agent Harness Skills——evo 系统详解与 SealQA 实践"
source: "https://x.com/alokbishoyi97/status/2059610305408462898"
author: "Alok Bishoyi (@alokbishoyi97)"
date: 2026-05-28
tags:
  - autoresearch
  - evo
  - self-improving-agents
  - agent-harness
  - skills
  - optimization
  - agent-loop
  - sealqa
  - claude-code
  - codex
  - openclaw
  - parallel-experimentation
category: "ai-tools/agent-engineering/autoresearch"
---

# 使用 Autoresearch 优化 Agent Harness Skills——evo 系统详解与 SealQA 实践

> **来源：** [@alokbishoyi97](https://x.com/alokbishoyi97/status/2059610305408462898)  
> **核心洞察：** Agent 的参数空间不再是模型权重，而是 markdown。当 Skill 文件可以被读写评估时，自我进化就变得可行。
> **关键数据：** SealQA 基准 5/20 → 11/20（纯通过优化 Skill，模型完全未变）

---

## 一、核心命题：自我进化的 Agent 已来

AI 领域当下最有趣的变化是：**Agent 正在变得能够自我改进**。你把一个 Agent 指向某个问题，离开它，回来时发现它已经：

- 对自己的行为做了实验
- 保留了有效的做法，丢弃了无效的
- 产出了一个新版本的自己，在你关心的任务上得分明显更高

**关键事实：底层模型从未改变。改变的是包裹模型的层（wrapper）。**

> "The underlying model never changed. The wrapper around it did."

---

## 二、被优化的究竟是什么

### 2.1 参数空间：从 GPU 到 Markdown

被优化的不是模型权重——那需要训练运行、GPU 集群和标注数据集。**被优化的是 Agent Harness 暴露的配置层**。

大多数 Agent Harness 现在都将部分能力暴露为 **Skill**：

- **Claude Code** 有 Skills（`.claude/skills/` 目录下的 markdown 文件）
- **Codex** 有 Skills
- **Cursor** 暴露了类似的表面
- **OpenClaw** 也有 Skills
- **Hermes、Pi** 等也有

实现细节有差异，但核心思想一致：Agent 对某类任务的执行流程就是一个**纯 markdown 文件**。

### 2.2 为什么这让自我进化可行

```
模型权重优化                 Skill 参数优化
──────────────              ──────────────
需要 GPU 集群               需要 LLM 读写 markdown
需要标注数据集               需要另一个 LLM 评分
需要数小时训练               需要数秒生成假设
改动代价极大                 改动代价极低
```

任何人都可以——包括另一个 Agent——读取、编辑并发布新版本。**LLM 可以写 markdown，另一个 LLM 可以给它打分。这就是自我进化可行性的根基。**

> "The parameter space isn't model weights. The parameter space is markdown in this case."

> 本文的实验使用 Claude Code 和 Claude Skills，但方法适用于 Codex、Cursor、OpenClaw 等任何暴露 Skill 表面的 Harness。

---

## 三、evo：完整 Autoresearch 循环

### 3.1 什么是 evo

**evo 是一个优化循环**。你给它：

1. **一个代码库**（你的 Agent 配置、Skill 目录、提示词等）
2. **"更好"的定义**（什么指标衡量成功）
3. **一个预算**（多少轮实验、多少并发）

它自动完成以下流程：

```text
输入: 代码库 + "更好"的定义 + 预算
          │
          ▼
    ┌─ 建立基准测试 ──────────────────┐
    │ （自动检测或用已有 benchmark）   │
    └──────────┬─────────────────────┘
               ▼
    ┌─ 生成假设 ─────────────────────┐
    │ （关于"应该改什么"的多个想法）  │
    └──────────┬─────────────────────┘
               ▼
    ┌─ 并行执行 ─────────────────────┐
    │ 每个假设在独立沙箱中运行        │
    │ 各 Agent 同时出发               │
    └──────────┬─────────────────────┘
               ▼
    ┌─ 评分 → 树搜索 ───────────────┐
    │ 高分分支扩展、低分剪枝        │
    │ 不同切片上的"专家"独立保留    │
    └──────────┬─────────────────────┘
               ▼
    ┌─ 审计门禁 ─────────────────────┐
    │ 检查是否有作弊/参数泄漏       │
    └──────────┬─────────────────────┘
               ▼
    输出: 最优参数文件 + 完整实验记录
```

### 3.2 与简单贪心爬升的区别（三个关键差异）

| 维度 | 贪心爬升 | evo 树搜索 |
|------|---------|-----------|
| **探索方式** | 串行，每一步找最优 | **并行多路探索**，多个假设同时运行 |
| **保留策略** | 只保留最高分 | **保留分支树**——在不同切片上获胜的专业化方案与通用方案并存 |
| **安全机制** | 无 | **门禁（Gates）**——任何 pass/fail 检查（回归测试、保留集验证、防作弊审计）都是门禁。一个实验即使分数最高，如果触发门禁也会被丢弃 |

> "Without gates, optimization loops find ways to game the metric."  
> 没有门禁，优化循环会找到方法去"刷分"。

**evo 是开源项目**，也是 evo 平台底层引擎。本次 SealQA 实验完全基于 evo 运行。

---

## 四、使用方式

### 4.1 安装与配置

仅需两条命令：

```bash
# 安装 evo（只需这一步）
npm install -g @anthropic-ai/evo    # 或对应 pkg
```

支持 Claude Code、Codex、Cursor、OpenClaw、Hermes、Pi 等主流 Harness。

### 4.2 运行循环

```bash
# 第一步：发现（一次性设置）
/evo:discover

# 指向代码库，告诉它你想优化什么
# 它会：
# - 探索仓库结构
# - 找出/建立基准测试
# - 提出优化目标
# - 注册所有实验必须通过的门禁

# 第二步：优化循环（核心）
/evo:optimize

# 编排并行 Agent 运行
# 参数：并发数 + 每次 Agent 的预算 + 停止条件
# （通常：连续 N 轮无改进后停止）
```

**用户体验：** 用户只需：
1. 安装 → 2. 运行 discover → 3. 运行 optimize

仪表盘实时流式显示分数和追踪轨迹。你可以让它跑一小时，或跑一周。

### 4.3 输出

循环结束后返回：
- **参数文件**（Skill、prompt、config 等目标）——评分最高的版本
- **完整实验记录**——所有尝试过的假设、每条分支的完整追踪

支持本地运行（默认），也可切换到云端沙箱提供商实现大规模并行实验。

---

## 五、实战：SealQA 基准测试

### 5.1 基准说明

**SealQA** 是一组 20 道事实性问答，特点是：
- 明显的搜索结果相互矛盾
- 正确答案需要一定的推理才能提取
- 普通 Agent 会自信地给出错误答案

**典型题目：**

> "哪个国家是最近加入欧盟的，同时与俄罗斯接壤？"  
> — 联合条件会让大多数单次搜索翻车

> "目前有多少活火山在喷发？"  
> — "喷发"定义在今天/本月/今年不同，且头部来源答案不一致

### 5.2 实验过程

| 阶段 | 配置 | 成绩 |
|------|------|------|
| **基线** | Claude Code + Web Search，无自定义 Skill | **5/20** |
| **目标** | `.claude/skills/` 目录中的 Skill 文件 | 运行 evo 优化 |
| **实验量** | 50 次实验 | 并行执行 |
| **结果** | 一个 **145 行** Skill 文件 | **11/20** |

### 5.3 最终产出

evo 产出的 Skill 文件包含 **5 个触发门控子协议**——每个对应 Agent 系统性出错的题目类型。每个子协议针对一个特定的 query shape 有专门的处理策略：

```markdown
## Skill: sealqa-optimizer (145 lines, 5 sub-protocols)

### Sub-protocol 1: Joint-condition questions
- 检测：问题包含两个以上条件的 AND 连接
- 策略：分解为子查询 → 交叉验证结果

### Sub-protocol 2: Temporal ambiguity questions
- 检测：涉及"当前""最近""最新"等时间敏感词
- 策略：显式请求时间戳 + 指定日期范围搜索

### Sub-protocol 3: Conflicting-source questions
- 检测：初步搜索结果存在矛盾
- 策略：权威来源排序 + 交叉引用 + 推理链

### Sub-protocol 4: ...
### Sub-protocol 5: ...
```

**核心事实：底层模型完全没有变。evo 只修改了包裹模型的 wrapper（Skill 文件）。**

> "Score: 11/20. More than doubled. The underlying model did not change. The loop produced the wrapper."

---

## 六、为什么这很重要

### 6.1 Agent 系统的杠杆模型

```
Agent 系统效能 = 模型能力 × 好的 Harness × 紧致的验证循环
                  ↑           ↑                ↑
             常态更新      新！也可编程优化   新！持续运行
```

过去，只有第一个因子（模型能力）以规律节奏移动。新模型 → 新行为。  
现在，**另外两个因子也在移动——而且以你控制的节奏移动**。

- 对你的指标进行优化
- 在你的数据集上运行
- 在任何人可更新的参数空间中迭代

> "This is what I mean when I say AI's 4-minute mile is here. The breakthrough isn't a bigger model. It's a tighter loop around the one we already have."  
> 这就是"AI 的四分钟英里"时刻。突破不是更大的模型，而是围绕现有模型构建的更紧致的循环。

### 6.2 evo 平台的愿景

evo 平台的目标不仅是提供一次性运行，更是实现**持续调优**：

```text
一次性运行                   持续调优
──────────                   ────────
跑一次 → 拿结果                24/7 持续运行
输出固定版本                  持续监控基准
不关心后续漂移                问题漂移时自动重新优化
```

用户并不真的只需要一次 autolesearch 运行——他们希望系统保持调优状态，随着问题漂移、模型更新、新失败模式出现而持续适应。

**适用范围：** 任何有"更好"定义的事物——代码、Agent 配置、Skills、模型——都可以成为优化目标。

### 6.3 与 Harness Engineering 的关系

本文直接对应并推进了 [Harness Engineering](/ai-tools/agent-engineering/harness/agent-harness-engineering.md) 的理念：

- Harness 定义了 Agent 的约束层和工具集
- Skills 是 Harness 中**可优化**的参数——比模型权重更易迭代
- Autoresearch 在 Harness 之上增加了**自动发现瓶颈 + 并行实验 + 树搜索 + 门禁校验**的能力

简言之：**Harness Engineering 告诉你构建什么结构；Autoresearch 告诉你如何自动优化这个结构。**

---

## 七、总结

| 问题 | 答案 |
|------|------|
| 被优化的是什么？ | Agent Harness 的 Skill 文件（纯 markdown），不是模型权重 |
| 优化引擎是什么？ | **evo**——开源 autolesearch 循环 |
| 如何工作？ | 并行假设生成 → 独立沙箱执行 → 树搜索评分 → 门禁审计 |
| 需要多少努力？ | 安装一条命令，运行两条命令 |
| 实际效果？ | SealQA 基准 5/20 → 11/20，45 行 → 145 行 Skill，5 个门控子协议 |
| 适用哪些 Harness？ | Claude Code、Codex、Cursor、OpenClaw、Hermes、Pi 等 |
| 下一步是什么？ | 24/7 持续调优——问题漂移时自动重新优化 |

---

## 八、知识关联

| 关联文档 | 关联点 |
|---------|--------|
| `agent-engineering/harness/agent-harness-engineering.md` | Harness Engineering 概念基础——evo 自动优化正是对 Harness 的 Skills 进行优化 |
| `agent-engineering/harness/skillify-skill-engineering-guide.md` | Skills/Hooks 体系——evo 优化的目标文件格式 |
| `agent-engineering/tooling/claude-code-cloud-deployment-sandbox-isolation.md` | Claude Code 云端部署——evo 的并行沙箱环境依赖 |
| `agent-engineering/patterns/openclaw-vs-hermes-agent-memory-architecture.md` | 不同 Harness 的记忆/技能系统对比 |
| `spring-ai/from-assistants-to-agents-self-improving-agentic-systems.md` | Agent 从助手到自我进化系统的演进路径 |

---

*本文整理自 @alokbishoyi97 的 X 长文，描述了 evo 系统如何通过 Autoresearch 循环自动优化 Agent Harness 的 Skill 参数层，实现不改变模型的自我进化。*
