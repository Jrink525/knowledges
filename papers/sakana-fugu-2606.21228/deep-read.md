---
title: "Sakana Fugu Technical Report — 深度解读"
tags:
  - sakana-fugu
  - multi-agent
  - LLM-orchestration
  - collective-intelligence
  - deep-read
date: 2026-06-28
source: "https://arxiv.org/abs/2606.21228 | https://sakana.ai/fugu-release/"
---

# 🐡 Sakana Fugu Technical Report — 深度解读

> **Sakana Fugu: A Family of Orchestrator Models** | arxiv:2606.21228 | 2026-06-19
>
> **作者：** Fugu Team, Sakana AI（15 位共同作者）
>
> **相关论文：** Trinity (ICLR 2026) + Conductor (ICLR 2026)
>
> **官网产品：** https://sakana.ai/fugu/

---

## 📋 概述

Sakana Fugu 是一个**多智能体编排系统**，但以**单一模型 API** 的形式呈现。它是一族经过训练的 orchestrator 模型（本质上是语言模型本身），能够理解用户查询并**动态设计 agentic scaffold** 来解决该查询。

**核心论点：** 前沿 LLM 的下一个前沿可能不是由单一模型实现的，而是由能够识别、组合和放大多个模型互补优势的系统实现的。

---

## 🏗️ 论文结构

### 1. 引言：为什么需要编排

**背景观察：**
- 不同供应商的 LLM 正在出现**日益精细的领域专长分化**
  - Gemini-3-Deep-Think → IMO 金牌
  - GPT-5.5 → 反证 Erdős 80年未解猜想（组合几何）
  - Claude-Mythos → 发现 OpenBSD/FreeBSD 零日漏洞
  - 在同一领域内部也存在细粒度差异：Gemini 擅长直接实现已知算法，GPT 擅长规划结合多种算法思路
- Agentic scaffold 本身对性能有巨大影响（Claude Code、Codex 等证明能力不仅仅是模型的属性，也是 scaffold 的属性）

**Sakana Fugu 的定位：** 将**模型编排**视为**新的互补性 scaling axis** —— 超越更大的模型，转向更聪明地组合已有模型。

### 2. 相关工作

论文梳理了三个方向的已有工作：

| 方向 | 代表工作 | 与 Fugu 的差异 |
|------|---------|---------------|
| **LLM 集体智能** | Du et al., Mixture-of-Agents, Smoothie, MASRouter, GPTSwarm | 传统方法依赖手工设计的协作模式或固定通信拓扑。Fugu 是**训练出的 orchestrator**，自适应决策。 |
| **Agentic Scaffolds** | Chain-of-Thought, ReAct, Self-Reflection, Toolformer, Codex, Claude Code | 现有 scaffold 通常是**任务特定的外部系统**；Fugu 的 scaffold 是由训练好的 orchestrator **在推理时生成**的。 |
| **模型融合（Model Merging）** | Weight Averaging, Model Soups, TIES-Merging, Evolutionary Merge | 参数级融合需要参数访问和架构兼容性，无法用于闭源模型。Fugu 是**宏观层面的行为级融合**。 |

### 3. Fugu 系统设计

#### 3.1 Fugu（平衡版）

基于 Trinity (ICLR 2026) 的基础，扩展到生产环境。

**参数化（Parametrization）：**
- 使用预训练语言模型作为 backbone
- 在 backbone 的最后一层 hidden state 上附加一个**轻量级预测头**
- 对于有 L 个 worker 模型的池子，预测头输出 L 个 logits，选取得分最高的 worker
- **设计选择：** 不像 Trinity 那样给选中的模型分配角色，Fugu 总是将查询作为 worker 分发给选中的模型——大大简化了编排空间
- 使用**奇异值微调（Singular-Value Fine-tuning）** 适应 backbone 参数，仅训练少量奇异值尺度

**关键架构图：** 轻量级选择头与主干模型的 LM head 并行运行，输入 hidden state → 输出 L 个 logits。

#### 3.2 Fugu-Ultra（高质量版）

基于 Conductor (ICLR 2026)，扩展到生产环境。

**架构：**
- 主干模型 + 文本生成头（不同于 Fugu 的轻量级选择头）
- backbone 输出**自然语言指令**来编排 worker 模型
- 在 multi-turn 交互中，Fugu-Ultra 可以：
  - 编写 worker 指令并调用它们
  - 读取 worker 返回的中间结果
  - 决定是否需要更多 worker
  - 综合最终答案

**编排模式不仅限于模型选择：** 可以设计 agent-to-agent 通信拓扑，将复杂任务分解为多个子步骤。

#### 3.3 训练范式

三阶段训练流程：

| 阶段 | 方法 | 数据 |
|------|------|------|
| **1. 监督微调（SFT）** | 在高质量路由/编排轨迹上微调 backbone | 合成的查询-编排数据集 |
| **2. 进化算法（Evolutionary）** | 进化搜索编排策略空间 | 基于 benchmark 反馈的奖励信号 |
| **3. 强化学习（RL）** | 进一步优化编排策略 | 多轮交互和端到端任务完成 |

### 4. 实验结果

Fugu 和 Fugu-Ultra 在严格的基准测试中取得的结果：

#### 编码和工程基准

| Benchmark | Fugu | Fugu-Ultra | 最佳基线 | 备注 |
|-----------|------|-----------|----------|------|
| **SWE-Bench Pro** | — | **SOTA** | 超过所有可公开访问模型 | 软件工程多步骤任务 |
| **Terminal Bench** | — | **SOTA** | 超过所有可公开访问模型 | 终端操作任务 |
| **LiveCodeBench** | — | **SOTA** | 超过所有可公开访问模型 | 竞赛编程 |

#### 科学和推理基准

| Benchmark | Fugu | Fugu-Ultra | 最佳基线 |
|-----------|------|-----------|----------|
| **GPQA-Diamond** | — | **SOTA** | 超过所有可公开访问模型 |
| **Humanity's Last Exam** | — | **SOTA** | 超过所有可公开访问模型 |
| **CharXiv Reasoning** | — | **SOTA** | 超过所有可公开访问模型 |

**关键比较：** Fugu-Ultra 与 Anthropic Fable 5 和 Mythos Preview **肩并肩**，而这两个模型**不在 Fugu 的 agent pool 中**（不可公开访问）。

#### 应用于实际场景

自动化数据科学研究、代码审查、网络安全评估、论文复现等都展示了一致的优势：

- 代码审查：Fugu Ultra 比 GPT-5.5 显著更好，发现 20+ 个问题（其他工具只标记约 3 个）
- 网络安全评估：端到端安全评估——侦察、XSS/SQLi 检查、认证审查、带证据的清理报告
- 在多步骤开放式任务中，价值不仅仅是更好的单次答案，而是跨多步的持续进展

---

## 🎯 核心洞见

### 1. 编排作为新的 scaling 轴

论文最重要的论点：**能力不仅来自更大的模型，也来自如何组合已有模型。** 如果可以通过组合现有模型来放大能力，那么 AI 进步不必只依赖于最大的训练运行。

### 2. 宏观模型融合（Macro-level Model Merging）

Fugu 将模型在**行为层面**融合：把前沿模型视为黑盒智能体，学习如何路由、协调、验证和综合它们的输出。这避开了参数级融合需要架构兼容性的根本限制。

### 3. 两种模式适应两种场景

- **Fugu**：轻量级选择头，单 worker 模式，延迟接近直接调用一个前沿模型。适合日常交互。
- **Fugu-Ultra**：自然语言编排，多 worker 组合，牺牲延迟换取质量。适合最复杂的多步骤任务。

### 4. 地缘政治意义

论文明确指出单一供应商依赖的风险（引用 Anthropic 的 Fable/Mythos 出口管制案例）。Fugu 的 agent pool 是完全可替换的，天然提供了对集中化风险的制衡——"AI 主权" (AI sovereignty)。

### 5. 三阶段训练范式的独特之处

进化搜索 + 强化学习的组合，使得 Fugu 能发现人工难以设计的编排策略。这与 Sakana AI 一贯的"进化"理念一致（公司名 Sakana = 鱼，本身就是进化隐喻）。

---

## 🔍 技术细节

### Fugu 的轻量级选择头

```
hidden state h ∈ ℝᵈ → 轻量级预测头 → L 个 logits
                            ↓
                      argmax → 选中的 worker 模型
```

- 不使用角色分配，简化编排空间
- 奇异值微调：仅训练选中的权重矩阵的奇异值尺度
- 极小的可训练参数集

### Fugu-Ultra 的自然语言编排

- backbone 输出自然语言→决定使用哪些 worker
- 可以设计 agent 间通信拓扑
- 可以规划多步骤工作流
- 读取 worker 中间结果并综合

---

## ⚠️ 局限与未来方向

1. **延迟问题：** Fugu-Ultra 编排多个 worker，延迟显著增加。论文承认这是 trade-off，而非单纯的提升。
2. **token 成本：** 多 agent 编排消耗更多 token，目前主要面向有预算的团队。
3. **worker pool 依赖：** Fugu 的整体能力取决于可用 worker 模型的质量和多样性。
4. **可解释性：** 编排决策（为什么选 A 不选 B）目前不够透明。
5. **未公开的评估细节：** 部分比较使用了供应商报告的分数，可能存在基准泄漏。

---

## 💡 启示

1. **API 层开始超越模型层创新：** Fugu 证明了在 API 层面组合已有模型可能是比训练更大模型更高效的路径。
2. **集体智能产品化：** 这是从学术研究（Trinity/Conductor at ICLR）到产品（Fugu API）的最快转化之一。
3. **Agentic scaffold 从手工走向学习：** 未来 agentic scaffold 的设计将从手工编码转向训练式生成。
4. **对开发者的影响：** 如果你能用单一 API 调用获取多智能体编排能力，就能大幅降低构建复杂 AI 系统的门槛。

---

*深度解读基于 arxiv:2606.21228、sakana.ai/fugu-release/、GitHub SakanaAI/fugu。生成于 2026-06-28。*
