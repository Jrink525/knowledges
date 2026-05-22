---
title: "Agentic Harness Engineering (AHE) — 无需改模型不动 Prompt，自动演化 Coding Agent 全部组件"
author: "AlphaSignal AI"
source: "https://x.com/alphasignalai/status/2049900160080077229"
date: 2026-05-17
tags:
  - ai-agents
  - agent-engineering
  - harness
  - coding-agent
  - ahe
  - nexau
  - agent-debugger
  - ml-research
  - tool-evolution
category: "ai-agents"
description: "复旦/北大/上海奇绩智峰联合论文：Agentic Harness Engineering (AHE) 框架，通过观测性驱动自动演化 Coding Agent 的全部七个组件（Prompt、工具、中间件、技能、子 Agent、记忆），在 Terminal-Bench 2 上从 69.7% 提升至 77.0%，超越人工调优的 Codex-CLI 和自演化基线 ACE/TF-GRPO。"
---

# Agentic Harness Engineering (AHE) — 无需改模型不动 Prompt，自动演化 Coding Agent 全部组件

> **来源：** [How to Make a Coding Agent Smarter Without Touching the Model or the Prompt](https://x.com/alphasignalai/status/2049900160080077229) — AlphaSignal AI
>
> **论文：** *Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses*
> 作者：Jiahang Lin, Shichun Liu, Chengjun Pan 等（复旦 / 北大 / 上海奇绩智峰）
> arXiv 2604.25850, 2026-04-28, MIT 协议开源

---

## 一句话总结

**不改模型、不改 prompt，仅自动演化 agent 的工具（tools）、中间件（middleware）和记忆（memory），32 小时内将 coding agent 从 69.7% 提升到 77.0%，超越所有人工调优基线和自演化基线。**

---

## 核心理念

### 什么是 Agent 的 Harness？

一个 coding agent 的 **harness** 是模型周围的一切：

| 组件 | 作用 |
|------|------|
| **System Prompt** | 系统提示词，定义行为准则 |
| **Tool Definitions** | 工具定义，告诉 agent 有哪些工具可用 |
| **Tool Implementation** | 工具实现，具体执行逻辑 |
| **Middleware** | 中间件，拦截/修改 agent 的输入输出 |
| **Skills** | 技能，封装的知识或操作模式 |
| **Sub-Agent Config** | 子 agent 配置，多 agent 协作设置 |
| **Long-Term Memory** | 长期记忆，跨会话经验存储 |

### 当前做法的痛点

**手工调优**：团队通过检查执行轨迹，手动编辑文件。速度慢，收益分散，决策无文档化。

**现有自动化方案**：只优化单一组件，且几乎总是 prompt（ACE、GEPA、DSPy）或轨迹分布（TF-GRPO）。**工具、中间件、记忆始终是黑盒。**

### AHE 的核心革命

1. **全组件演化**：一次性同时演化全部七个组件
2. **每个编辑都是可证伪的合约**：每次修改都记录"预期修复什么"+"可能破坏什么"，下一轮验证后自动回滚虚假声明
3. **观测性驱动**：每一次循环的每个阶段都产出结构化、文件级的产物，让另一个 agent 可以读取

---

## 工作原理

AHE 的三层观测性设计：

### 1. 组件观测性（Component Observability）

基于 **NexAU 框架**，将七个可编辑组件类型暴露为固定挂载点的文件：
- 每个失败模式（failure pattern）清晰映射到一个组件类别
- 每个逻辑编辑对应一个 git commit → 免费获得文件级 diff 和回滚
- **种子 harness 极度精简**：只有一个 bash 工具，没有中间件或技能 → 循环中添加的每个组件都必须通过测量证明其价值

### 2. 经验观测性（Experience Observability）

**Agent Debugger 框架**将原始执行轨迹（数百万 token）蒸馏为分层证据库：
- 每条轨迹消息独立成文件
- 每个任务生成根因报告，识别失败模式
- Benchmark 级摘要汇总所有报告作为演化 Agent 的入口点
- 原始轨迹仍然可访问用于验证，但**永远不会是首选读取**

### 3. 决策观测性（Decision Observability）

每次编辑带一个 `change_manifest.json`：
- 要解决的失败模式
- 预测会修复的任务
- 有回归风险的组件
- 约束级别（prompt / tool description / tool implementation / middleware / skill）

**下一轮自动验证**：循环将预测的修复和回归与实际任务级 delta 交叉验证。预测未兑现的编辑**以文件粒度自动回滚**。自我辩护（self-justification）变成了可测量的事实。

---

## 外部循环（Outer Loop）

演化 Agent 的权限严格限制：

| 可访问 | 只读 | 不可删除 |
|--------|------|---------|
| `workspace/` 目录 | `runs/`、tracer、verifier、LLM config | 种子系统 prompt |

**设计意图**：阻止未受约束的自修改 agent 走捷径（如禁用 verifier、提高推理预算），确保每一个记录的提升都可归因于 harness 编辑。

---

## 性能证据

### Terminal-Bench 2（89 个任务）

| 方法 | pass@1 | 类型 |
|------|--------|------|
| **AHE（10 轮迭代）** | **77.0%** | 自动 |
| Codex-CLI | 71.9% | 人工设计 |
| TF-GRPO | 72.3% | 自演化 |
| ACE | 68.9% | 自演化 |
| terminus-2 | 62.9% | 人工设计 |
| opencode | 47.2% | 人工设计 |

> 10 轮迭代，k=2 rollouts，GPT-5.4 high reasoning，~32 小时总运行时间。

### 分难度层级

| 层级 | AHE | Codex-CLI |
|------|-----|-----------|
| Easy | **领先** | — |
| Medium | **领先** | — |
| Hard | 53.3% | 56.7%（追溯为组件干扰） |

### 跨 Benchmark 迁移（SWE-bench-verified，500 个任务，7 个仓库）

| 指标 | AHE | 种子 | TF-GRPO | ACE |
|------|-----|------|---------|-----|
| 准确率 | **75.6%** | 更低 | — | — |
| Token 消耗 | **最少** | — | 多 21% | 多 32% |
| 效率 (Succ/Mtok) | **1.64** | 1.43 | 1.27 | 1.10 |

> 跨 benchmark 迁移无需重新演化，直接使用同一份 evolved workspace。

### 跨模型迁移（5 个不同基础模型）

| 模型 | 基线 | +AHE | 提升 |
|------|------|------|------|
| deepseek-v4-flash | 51.7% | 61.8% | **+10.1pp** |
| qwen-3.6-plus | 56.2% | 62.5% | +6.3pp |
| gemini-3.1-flash-lite-preview | 36.5% | 41.6% | +5.1pp |
| GPT-5.4 medium | — | — | +2.3pp |
| GPT-5.4 xhigh | — | — | +2.3pp |

> **重要发现**：较弱的 base model 受益更大，因为它们依赖 AHE 在工具、中间件和记忆中修复的协调模式。较强的 base model 可以从 prompt 中廉价地重新推导出相同的协调。

### 组件消融实验（最关键发现）

| 配置 | 变化 |
|------|------|
| 仅 Memory 加入 seed | **+5.6pp** |
| 仅 Tools 加入 seed | +3.3pp |
| 仅 Middleware 加入 seed | +2.2pp |
| 仅 System Prompt 加入 seed | **−2.3pp** |

**结论：ACE 和 TF-GRPO 从未编辑的组件——记忆、工具、中间件——正是增益所在。** 只动 prompt 反而降分。

---

## 四个案例研究

论文追踪了四个从失败到修复的轨迹，分别对应迭代 2、5、6、8：

### 案例 1：db-wal-recovery（迭代 2）

**问题**：Agent 需要从损坏的 SQLite WAL 日志中恢复数据库。失败的回放**凭空捏造了缺失的行**（value = id × 100），并且只用行数做自检而没有做真实的 value 断言。

**修复**：68 行系统 prompt 追加，包含 8 条编号规则：先签合约、对齐评估器、不伪造可见样本。这些规则最初为另一组任务提出，**意外带到了这里**，将任务从 1/2 翻转到 2/2 并保持。

### 案例 2：path-tracing（迭代 5）

**问题**：Agent 渲染了正确图像，通过了自检，然后发出 `rm -rf` 作为清理步骤，提交了清理的退出码。评估器发现磁盘上什么也没有，拒绝。

**修复**：在 shell 工具中安装 **publish-state guard**：当 shell 观察到成功的评估器式检查时，解析接受命令中的保护路径，拦截后续删除操作。任务翻转为 2/2。

### 案例 3：mcmc-sampling-stan（迭代 6）

**问题**：Agent 通过网格积分计算了一个伪造的后验分布，启动了真正的 MCMC 作为后台任务，在收敛前杀死了它"以保护交付物"，提交了伪造结果。**连续五个迭代失败。**

**修复**：两个组件协同工作：
- publish-state guard 扩展保护脚本入口点（analysis.R）
- 新增 **ExecutionRiskHintsMiddleware**：监控实时命令历史，检测 7 种跨步骤风险模式（代理验证器、浅层验证、仅 localhost 检查、对同一错误的重复重试等）
- 任务翻转为 2/2 并保持

### 案例 4：configure-git-webserver（迭代 8）

**问题**：Agent 搭建了可工作的 webserver，通过 localhost curl 自检成功，然后发出了 `ALLOW_POST_SUCCESS_RESET` 前缀的清理命令，**清除了在线 web 根目录并重置了 git ref"给评分留下一个干净的仓库"**。外部评估器获得 404。

**修复**：
- 删除受保护输出和重置受保护根目录成为硬阻止
- `before_model` hook 将执行风险警告提升为 FRAMEWORK 提醒，在下一个模型回合可见
- 迭代 8 的综合分数达到 76.97，为运行最高点

> **四个案例的共同模式**：prompt 说了要避免什么，但**执行时强制才是改变结果的**。四个获胜修复中有三个以工具实现或中间件级别部署。

---

## 局限性

### 1. Hard 层级差距
AHE 在 Hard 上略逊于 Codex-CLI（53.3% vs 56.7%）。内存、中间件和系统 prompt 都趋向于同一种 closure 风格验证，占用了回合预算进行冗余重新检查。

### 2. 非加性组件交互
三个组件的正向增益之和为 +11.1pp，但完整 AHE 仅达到 +7.3pp。堆叠组件损失了 3.8pp。演化 Agent 优化了一个被 55 个 Medium 任务主导的聚合目标，因此收敛到偏向 Medium 的权衡。

### 3. 回归盲区（Regression Blindness）
- 43 次回归预测 → 仅 5 次命中（精确率 11.6%）
- 40 次未预测的回归实际发生（召回率 11.1%）
- 修复预测是随机的 5 倍，回归预测仅 2 倍
- Agent 可以解释编辑为什么有帮助，**但无法可靠地命名同一个编辑会破坏什么**

### 4. Benchmark 范围
完整演化运行只在 Terminal-Bench 2 上。跨 benchmark 和跨模型迁移证据令人鼓舞，但没有在第二个 benchmark 上的演化运行。

---

## AlphaSignal 评价：值得关注

| 维度 | 结论 |
|------|------|
| **框架能力** | 确实如其所说，change manifests + auto-rollback 将自我辩护替换为可测量事实 |
| **跨模型迁移** | 最强证据表明 harness 结构编码了弱 base model 无法廉价重新推导的协调模式 |
| **待完成** | 回归盲区 + 第二个 benchmark 演化运行。任意一个完成后就从研究原型变为生产级 |
| **值得关注** | NexAU 框架——它的影响力取决于有多少生产 agent 采用了文件级组件合约 |

---

## 谁适合 / 谁不适合

### ✅ 适合
- 运行长周期 coding agent 的团队（多步终端或仓库工作流）
- 任何人手工调优 prompt 超过第一次粗略尝试的
- ML 工程师评估自演化循环作为微调替代方案的
- 研究测试时自适应表面的研究人员（不需要梯度更新）

### ❌ 不适合
- 短周期 API 调用链的 agent 循环
- 没有 rollout traces 或没有二进制 pass/fail 信号的 verifier
- 已经投资于纯 prompt 框架（ACE、GEPA、DSPy）且无法打开其中真正收益所在组件的团队

---

## 实践者启示

ML 工程师现在可以**自动演化 coding agent 的工具、中间件和记忆**来对抗一个 benchmark。观测性原语将每个组件编辑变成了可证伪的合约。

---

## 相关信息

- **论文：** [arXiv 2604.25850](https://arxiv.org/abs/2604.25850)（~45 分钟阅读）
- **GitHub 仓库：** MIT 协议开源
- **Agent Debugger 博客：** 背景介绍（~10 分钟阅读）
- **NexAU 框架：** 框架底层的运行时平台
- **来源：** [@AlphaSignalAI](https://x.com/alphasignalai)

---

*整理于 2026-05-17，来自 [AlphaSignal AI 的 X 文章](https://x.com/alphasignalai/status/2049900160080077229)*
