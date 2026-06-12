---
title: "Building Recursive Agent Systems"
tags:
  - cursor
  - ai-agents
  - ml-training
  - agent-orchestration
date: 2026-06-12
source: "https://x.com/leerob/status/2065469795529588940"
authors: "Lee Robinson (Cursor CEO)"
---

# 构建递归 Agent 系统：Cursor 如何用数千个 Agent 训练下一代 Composer

> **来源：** [@leerob on X](https://x.com/leerob/status/2065469795529588940)
> *Lee Robinson, Cursor CEO, 2026-06-12*

---

## 核心思路

Cursor 内部运行着**数千个 Agent**来帮助训练下一代 Composer。他们的方法是构建一个 **Agent 的组织架构图（org chart）**——一个人类→Agent 的层级管理系统。

---

## 系统架构

### 主 Agent（Fleet Manager）
- 运行在一台大规模远程机器上，拥有本地开发的所有工具
- 维护一个磁盘上的文件作为"收件箱"（inbox），用于收集整个 fleet 的状态
- 通过 SSH 连接到运行着数百个子 Agent 的机器

### 运作流程

1. **主 Agent 循环检查**：每次循环检查 fleet 健康状态
2. **保持健康任务运行**：背景中保持正常运行的任务
3. **异常上报**：将任何出现问题的工作通过 Slack 推送给团队
4. **Fleet 控制**：可以终止或重启 fleet 中的任意进程

### 关键技术决策

- 主 Agent 被赋予**多种技能**，编码了运行 ML 实验、监控结果等的**隐性知识（tacit knowledge）**
- 构建在 Cursor 之前发布的**长期运行 Agent** 研究之上
- 遇到临时问题或需要"戳一下"，主 Agent 可以直接控制整个 fleet

---

## 为什么这样做？

### 训练好模型的关键

训练一个好模型意味着需要尝试**大量想法**来创建有用的 RL 数据。

- 单台笔记本电脑远远不够——你需要**云中的一台计算机军队**来并行运行实验
- Cursor 不做计算资源限制（not compute-constrained），全团队都可以使用这套基础设施

### 研究人员的超能力

> **研究人员的时间是最稀缺的资源。**
> 这套系统将研究人员的杠杆效应**放大了几个数量级**。

想象一下，如果你有一个管理着 **10,000 个直接下属的人类经理**——显然行不通。但人类→Agent 的"组织架构"方式竟然有效！

---

## 什么时候值得考虑这个方案？

Lee 给出的判断标准：

> **如果你的问题是可验证的（verifiable），并且投入更多 token 能更快或更好地解决问题——就值得考虑构建这样的系统。**

### 适用场景
- 大规模并行 ML 实验
- 需要处理海量数据的 RL 训练
- 可通过程序自动验证的任务

### 当前成果
这套系统使得**成群结队的 Agent 能够爬梳 Composer 的数据**，递归地自我改进，为未来版本铺路。

---

## 总结

| 维度 | 内容 |
|------|------|
| **主体** | 一个 Fleet Manager Agent + 数百个子 Agent |
| **通信** | SSH + 磁盘文件收件箱 |
| **监控** | 主 Agent 检查 fleet 健康，Slack/PagerDuty 通知 |
| **人力杠杆** | 研究人员的效率被放大几个数量级 |
| **关键前提** | 问题必须是可验证的，更多 token = 更好结果 |
| **核心理念** | 人类→Agent 的"组织架构"替代传统管理 |

---

*整理于 2026-06-12，原文来自 @leerob 的 X/Twitter 长文*
