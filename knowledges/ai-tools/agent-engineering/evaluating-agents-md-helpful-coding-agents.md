---
title: "Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?"
source: "https://x.com/rasbt/status/2063649136323252397"
author: "Sebastian Raschka (@rasbt)"
paper: "https://arxiv.org/abs/2602.11988"
paper_authors: "Thibaud Gloaguen, Niels Mündler, Mark Müller, Veselin Raychev, Martin Vechev"
category: "ai-tools/agent-engineering"
tags: [agents-md, coding-agents, SWE-bench, context-files, CLAUDE.md, agent-benchmark]
---

# AGENTS.md 真的有用吗？— 论文解读

> Sebastian Raschka 解读了一篇有意思的论文：「AGENTS.md」这类仓库级上下文文件到底能不能帮到 coding agent？

---

## 论文基本信息

- **标题：** Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?
- **作者：** Thibaud Gloaguen, Niels Mündler, Mark Müller, Veselin Raychev, Martin Vechev
- **链接：** https://arxiv.org/abs/2602.11988

---

## 研究动机

现在很多项目都放了 AGENTS.md 或 CLAUDE.md，告诉 coding agent 仓库的规则、架构、工作流。但——**这些文件真的有效吗？** 还是只是开发者自我感觉良好？

论文通过两个实验来回答这个问题。

---

## 实验设置

### 实验一：SWE-bench Lite

在 SWE-bench Lite 上测试。因为原始仓库没有开发者写的上下文文件，作者用 LLM 生成 AGENTS.md。

### 实验二：AGENTBENCH（新基准）

作者自己提出了 **AGENTBENCH**——138 个 Python 任务，来自 12 个**已经有开发者手写 AGENTS.md 的仓库**。

Agent 在三种条件下评估：
1. **无上下文文件**（无 AGENTS.md）
2. **LLM 生成的上下文文件**
3. **开发者写的上下文文件**（真实仓库自带）

---

## 核心发现

### 1. LLM 生成的 AGENTS.md 帮助不大

相比不使用任何上下文文件，LLM 生成的 AGENTS.md **平均成功率轻微下降或无显著差异**。

这个结果有点反直觉。Raschta 给出了合理的推测：agent 运行时会根据代码仓库内容动态生成所需上下文信息——AGENTS.md 提供的东西它本来就能自己"看"出来。

### 2. 开发者写的 > LLM 生成的

开发者手写的上下文文件比 LLM 生成的好。这符合预期——领域专家的知识确实是 AI 生成的概括无法替代的。

### 3. 最大的反转：**不用 AGENTS.md 反而更便宜、更高效**

这可能是最令人困惑的结论。直觉上多给些上下文应该更好，但实际结果相反。

**原因推测：**

Raschta 最初以为是 harness 在处理冗余信息——读了 AGENTS.md，但仍然从代码仓库中解析了一遍同样的信息。

但 trace 分析显示：Agent **确实遵循了上下文文件中的指令**——它们跑了更多测试、搜索了更多文件、读取了更多文件、使用了更多仓库特有的工具。

这些额外的步骤没有带来更好的成功率，却消耗了更多 token 和计算时间。**AGENTS.md 让 agent 更「认真」了，但没更「聪明」。**

---

## Raschta 的见解

> 仓库级上下文文件应该**保持简短和具体**，最好做成**层级结构**：
> - 主文件只放最关键的规则
> - 详细说明放在子文件中
> - 例如：「如果你做 X，先检查 context/y.md，否则忽略它」

"做太多"和"做得对"不是一回事——这是本研究最直接的教训。

---

## 对 Agent Engineering 的启示

| 发现 | 含义 |
|------|------|
| AGENTS.md 增加 token 消耗但不提效 | 上下文文件不是越长越好，过长的指令可能反而降低效率 |
| Agent 会跟指令但不改善结果 | 工具引用和探索步骤需要谨慎设计，别让 agent 白费力气 |
| 开发者手写 > LLM 生成 | 自动化生成的短板：缺少真正的领域判断 |
| 层级上下文可能是出路 | 按需加载，而不是把所有规则一次性灌入 |

**和之前几篇文章的关系：**

- **AgentForge**（Mohit）用渐进式披露加载 skill——只在被选中时才加载完整正文
- **这篇论文的结论**本质上验证了同样的方向：**不要一次性把所有上下文塞给模型**
- 这与之前「thin harness, fat skills」「按需加载」的思路完全一致

---

## 局限性

论文本身用的是当时的 LLM 和 harness，现在（2026 年中）已经有些过时。用最新的 GPT/Claude 和最新版的 agent harness 重新跑一遍，结果可能会有变化。

---

## 引用

```
@misc{gloaguen2025evaluatingagentsmdrepositorylevel,
      title={Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?}, 
      author={Thibaud Gloaguen and Niels Mündler and Mark Müller and Veselin Raychev and Martin Vechev},
      year={2025},
      eprint={2602.11988},
      archivePrefix={arXiv},
}
```
