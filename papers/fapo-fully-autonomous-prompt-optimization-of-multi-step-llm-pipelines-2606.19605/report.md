# FAPO: Fully Autonomous Prompt Optimization of Multi-Step LLM Pipelines

> **论文**: arXiv:2606.19605 (cs.SE), June 2026  
> **作者**: Paul Kassianik, Baturay Saglam, Huaibo Zhao, Blaine Nelson, Supriti Vijay, Aman Priyanshu, Amin Karbasi  
> **机构**: Foundation AI – Cisco Systems Inc.; Yale University  
> **代码**: [github.com/cisco-foundation-ai/fully-automated-prompt-optimization](https://github.com/cisco-foundation-ai/fully-automated-prompt-optimization)  
> **深度解读**: v1.2.0

---

## 一、问题：为什么纯 prompt 优化不够

### 1.1 多步骤 LLM Pipeline 的级联失败

现代的 LLM 应用很少是单次推理调用。它们通常是**多步骤 pipeline**：先检索（retrieval），再推理（reasoning），最后格式化输出（formatting）。每个步骤都可能出错，而且错误会**向下游级联**。

FAPO 的作者们点出一个关键观察：**prompt-only 优化（prompt-only optimization）无法诊断或修复 pipeline 结构层面的瓶颈。** 如果一个问题的根源是检索覆盖不足（retrieval insufficient）或控制流不当（incorrect chain topology），无论怎么优化单一步骤的 prompt，都无法从根本上解决问题。

> **Claim C1.1**: *Multi-step LLM pipelines fail through interactions among retrieval, reasoning, and formatting steps, so prompt-only optimization can miss bottlenecks in the chain.*

### 1.2 现有工具的盲区

论文梳理了现有工具的局限：

| 范式 | 代表工具 | 局限 |
|------|----------|------|
| **评测套件** | HELM, BIG-bench, AgentBench | 评测模型能力，不优化 pipeline |
| **Prompt 编程** | DSPy, GEPA | 优化 prompt 但限于固定 pipeline 结构 |
| **Prompt 进化搜索** | APE, OPRO, EvoPrompt | 只改 prompt 文本，不改结构 |

没有工具能做到：**检查每一步的失败原因，然后决定是改 prompt 还是改 pipeline 结构，且都在一个标准的代码工作区中完成。** 这个空白，就是 FAPO 要填补的。

---

## 二、FAPO 的技术方案

### 2.1 核心架构：三代理 + 共享运行时

FAPO 的架构围绕一个核心洞察：**优化器（orchestrator）必须与被优化的任务模型（task model）分离**。FAPO 使用 Claude Code 作为 orchestrator，通过三个专业 agent 驱动优化循环：

```
┌─────────────────────────────────────────────────────┐
│                    FAPO Orchestrator                 │
│  ┌─────────────────┐  ┌────────────┐  ┌──────────┐  │
│  │ Optimization    │  │Step-Attri- │  │Variant-  │  │
│  │ Agent           │  │bution Agent│  │Reviewer  │  │
│  │ (驱动优化循环)   │  │(分析失败)   │  │(检查合规) │  │
│  └────────┬────────┘  └────────────┘  └──────────┘  │
│           │                                                  │
│  ┌────────┴─────────────────────────────────────┐   │
│  │         Shared Runtime (src/hephaestus/)      │   │
│  │  dataset loading · prompt rendering · scoring │   │
│  │  provider adapters · LangGraph runner · logs  │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

> **Claim C2.3**: *The optimization loop uses three core agents: optimization agent, step-attribution subagent, and variant-reviewer subagent.*

### 2.2 五步优化循环

FAPO 的优化循环（Section 3.2）由六个阶段组成：

1. **Evaluate** → 在训练集上运行当前 pipeline，记录每一步的输入、输出、日志
2. **Attribute** → step-attribution agent 分析失败原因，归类为 prompt-addressable 或 structural
3. **Propose** → 针对主要的失败类别，提出一个 scoped change
4. **Review** → variant-reviewer agent 独立检查变更合规模板完整性、数据泄露、scorer 兼容性
5. **Validate** → 在验证集上对比新 variant 与之前的最佳 variant
6. **Iterate or Escalate** → 保留改进的 variant，当 prompt-level 搜索饱和时，根据 scope contract 升级到结构变更

### 2.3 Prompt-First 升级策略

这是 FAPO 最巧妙的设计之一：**优先尝试最小的有用变更**。

```
Level 1: Prompt text    ← 首选，最简单
Level 2: Chain params   ← 仅当 prompt 优化不足时
Level 3: Chain structure ← 仅当 attribution 确认结构瓶颈时
```

> **Claim C2.2**: *FAPO first attempts prompt-level optimization and escalates to structural changes only when attribution indicates prompt edits are not enough to resolve the dominant bottleneck.*

这个策略借鉴了 jailbreaking 文献中的 `evaluate–analyze–propose–iterate` 闭环搜索模式（PAIR, TAP, GCG），但**把目标从"找到一个成功的注入"变成了"提高 pipeline 在所有评估样本上的平均得分"**。

> **Claim C4.1**: *FAPO integrates the adversarial evaluate-analyze-propose-iterate search pattern from jailbreaking literature but changes the objective to mean score improvement across evaluation cases.*

### 2.4 Tenant 隔离模型

FAPO 引入了一个非常实用的企业级设计：**tenant 工作区**。每个任务一个 tenant，包含：

- `chains/` — baseline 和 structural variants
- `prompts/` — prompt variants（不可变，每个版本一个新文件）
- `configs/` — eval configs
- `docs/` — 操作文档、scope contract、iteration memory
- Shared runtime (`src/hephaestus/`) — 不包含任何 tenant 特定代码

这个设计确保了**可复现性、隔离性和可扩展性**——企业环境中不同业务单元、安全域、操作需求可以共存。

> **Claim C2.6**: *FAPO organizes optimization around a tenant model with isolated workspaces, ensuring reproducibility, isolation, and extensibility.*

### 2.5 防止过拟合的四个护栏

| Guardrail | 机制 |
|-----------|------|
| **Split access controls** | 优化器只能看到训练用例；验证集和测试集只暴露聚合分数 |
| **Scope constraints** | Tenant playbook 定义允许/禁止的变更类型 |
| **Iteration memory** | 结构化日志记录所有 variant、分数、废弃原因 |
| **Variant immutability** | 每次尝试（包括被拒的）都写为新文件 |

> **Claim C2.5**: *FAPO uses four guardrails against overfitting: split access controls, scope constraints, iteration memory, and variant immutability.*

---

## 三、实验结果与分析

### 3.1 整体表现：15/18 胜率

| Benchmark | 模型 | Baseline | GEPA | FAPO | Δ (pp) |
|-----------|------|----------|------|------|--------|
| **HotpotQA** | GPT-4.1-mini | 37.11 | 67.56 | **72.67** | +5.11 |
| | GPT-5.4-mini | 55.56 | 56.22 | **69.56** | +13.34 |
| | Gemma 3-12B | 56.56 | 61.66 | **62.78** | +1.12 |
| **HoVer‡** | GPT-4.1-mini | 43.89 | 59.67 | **84.45** | +24.78 |
| | GPT-5.4-mini | 26.33 | 31.78 | **80.34** | +48.56 |
| | Gemma 3-12B | 24.89 | 54.00 | **86.67** | +32.67 |
| **IFBench‡** | GPT-4.1-mini | 25.74 | 54.76 | **93.71** | +38.95 |
| | GPT-5.4-mini | 24.49 | 48.36 | **86.06** | +37.70 |
| | Gemma 3-12B | 34.69 | 42.46 | **62.30** | +19.84 |
| **LiveBench-Math** | GPT-4.1-mini | 50.25 | 61.78 | **73.56** | +11.78 |
| | GPT-5.4-mini | 31.76 | 57.26 | **66.99** | +9.73 |
| | Gemma 3-12B | 30.80 | 38.66 | **45.30** | +6.64 |
| **AIME** | GPT-4.1-mini | 51.11 | **48.89** | 45.11 | -3.78 |
| | GPT-5.4-mini | 30.00 | 33.78 | **38.45** | +4.67 |
| | Gemma 3-12B | 16.67 | 18.22 | **19.66** | +0.44 |
| **Papillon** | GPT-4.1-mini | 68.39 | 90.72 | **94.29** | +3.57 |
| | GPT-5.4-mini | 87.79 | 88.82 | **95.08** | +6.26 |
| | Gemma 3-12B | 67.15 | 92.65 | **95.46** | +2.81 |

> **Claim C1.2**: *FAPO beats the baseline GEPA in 15 of 18 model-benchmark comparisons.*  
> **Claim C1.3**: *The mean FAPO-GEPA gain is +14.1 percentage points across all comparisons.*

‡ = FAPO used permitted pipeline optimization (prompt→structural escalation)

### 3.2 结构变更带来的巨大提升

在 HoVer 和 IFBench 上，FAPO 识别出 prompt 优化无法解决的瓶颈：

- **HoVer**（多跳事实验证）：attribution 发现检索覆盖不足 → FAPO 将 baseline 的 3-hop 检索扩展到 4-5 hop，引入 multi-query BM25 搜索和 entity-aware rescue。**结果：+24.78 到 +48.56 pp**

- **IFBench**（指令遵循）：attribution 发现格式失败 → FAPO 添加了确定性后处理节点（deterministic post-processing nodes）强制约束条件。**结果：+19.84 到 +38.95 pp**

> **Claim C1.4**: *In the six HoVer and IFBench comparisons where prompt-first search escalated to structural changes, FAPO wins all six with a mean gain of +33.8 pp.*

### 3.3 安全领域：CTIBench-RCM

FAPO 的一个亮点是对**安全分类任务**的优化。CTIBench-RCM 是 263 类 CVE→CWE 安全漏洞分类任务，遵循 Foundation-Sec 评估协议（仅允许 prompt 优化）。

| Model | Dev base → best | Test base → best | Gain |
|-------|----------------|-----------------|------|
| GPT-5 | 78.6% → 85.6% | 72.1% → 76.1% | +4.0 pp |
| Foundation-Sec-8B-Instruct | 76.3% → 80.4% | 63.9% → 71.0% | +7.1 pp |
| Foundation-Sec-8B-Reasoning | 80.4% → 83.2% | 71.0% → 73.0% | +2.0 pp |

有意思的是，最好的 prompt 策略因模型而异：
- **GPT-5**: 需要一个详细（23行）的 NVD 映射规则列表
- **Foundation-Sec-8B-Instruct**: 最有效的 prompt 反而是**更短**（2行），删除了规则细节
- **Foundation-Sec-8B-Reasoning**: 接近 Instruct 的 prompt，加上 "standard NVD abstraction level" 短语带来 +2.9 pp

> **Claim C1.5**: *FAPO improves CTIBench-RCM test accuracy: +4.0 pp on GPT-5, +7.1 pp on Foundation-Sec-8B-Instruct, +2.0 pp on Foundation-Sec-8B-Reasoning.*

### 3.4 AIME 的异常与讨论

AIME（竞赛数学）是 FAPO 唯一的失败基准。论文认为结果**缺乏统计显著性**（落在噪音范围内），推测可能是由于训练样本太少导致的过拟合。

> **Claim C3.4**: *AIME is the only benchmark where GEPA leads FAPO across all three model comparisons; results are inconclusive.*

### 3.5 Token 预算不对称

论文在 4.5 节揭示了一个值得注意的细节：**GPT-4.1-mini 在 4/6 的 baseline 上优于 GPT-5.4-mini**。原因不是模型能力，而是 token 预算机制：

- GPT-4.1-mini：16K token 只对**可见输出**有限制
- GPT-5.4-mini（reasoning model）：16K 是 `max_completion_tokens`，覆盖**隐藏推理 + 可见输出**

实际观测到 GPT-5.4-mini 的可见输出从未超过 4,922 tokens，在 LiveBench-Math 上中位数仅 78 tokens。这导致其最终答案经常被截断或格式错误，解释了为什么更新的模型反而在 benchmark 上表现更差。

> **Claim C3.6**: *GPT-4.1-mini outperforms GPT-5.4-mini on four of six baselines due to asymmetric token budgeting.*

---

## 四、深入分析：FAPO 设计中的权衡

### 4.1 Prompt-First vs 直接结构优化

FAPO 的 prompt-first 策略是双刃剑：

**优点**：
- 保持搜索空间可控
- 最小化不必要的架构变更
- 与保护性 guardrails 自然兼容

**问题**：
- 可能导致优化路径的强路径依赖（path dependence）
- 论文承认 FAPO 的方差（trial standard deviation）在允许结构变更时更高，反映了这种路径依赖
- AIME 上 prompt-only 策略失败，但 FAPO 是否尝试了足够多的结构变更加以挽回？不确定

### 4.2 GEPA 对比的公平性

论文坦白承认 FAPO 与 GEPA 的对比不是 apples-to-apples：

> *"GEPA remains a fixed-program prompt optimizer, whereas FAPO is an agentic workspace optimizer with a different search space."*

GEPA 被限制在固定的 DSPy chain-of-thought 程序中搜索 instruction string，而 FAPO 可以修改 chain 参数和结构。而且 GEPA 的 reflector 被替换为 Claude Opus 4.6，**可能反而加强了 GEPA**。

论文的处理方式是诚实地标记了哪些行启用了结构变更（HoVer, IFBench），并分别报告 prompt-only 和 structural 的结果。

### 4.3 与 Jailbreaking 文献的深层联系

论文在 Related Work（Section 5）中非常坦率地建立了与 adversarial prompt 优化的联系。这不是简单的"引用相关 work"，而是**一个深层论证**：

> FAPO takes the same evaluate–analyze–propose–iterate loop from jailbreaking, but changes the objective from finding one rare success (adversarial) to improving mean performance across all examples (constructive).

这种"同一技术，不同目标"的框架统一了 prompt 优化的两个看似对立的领域——**红队（red-teaming）和蓝队（blue-teaming）**。

---

## 五、工程启示

### 5.1 对企业 AI 部署的启示

FAPO 的 tenant 模型特别值得关注。很多 AI 平台面临的问题是：不同业务单元需要不同的 pipeline，但共享基础设施。FAPO 提供了一个可落地的工程方案：

- **共享运行时**（`src/hephaestus/`）+ **隔离工作区**（`tenants/{id}/`）
- **Scope contract** 作为优化策略的安全阀
- **Variant immutability** 确保每次尝试可追溯

### 5.2 对 AI Agent 开发者的启示

FAPO 展示了**Claude Code 作为 agent 操作系统的潜力**——不仅用来写代码，还可以：

- 驱动实验循环
- 管理结构化日志
- 协调子 agents
- 执行策略约束

这说明 LLM-powered coding agents 的能力边界远不止"写代码"，而是**工程设计工作流**。

### 5.3 局限性

- 仅评估了 Claude Code 一种 orchestrator，泛化性未验证
- 未报告优化成本（API 调用数、token 消耗、运行时间）
- 缺乏 ablation study（排除 prompt-only vs structural 各自的贡献）
- AIME 负结果的解释不充分

---

## 六、未来方向

FAPO 打开的研究方向（详见 `direction_board.json`）：

1. **学习升级策略**（D1）— 用学习替代启发式的 attribution 和 escalation
2. **跨轮次失败追踪**（D2）— 跟踪失败分布随优化轮次的变化
3. **多 orchestrator 泛化**（D3）— FAPO 架构是否依赖 Claude Code？
4. **多目标帕累托优化**（D4）— 精度 vs 成本 vs 延迟
5. **异构多 Agent Pipeline**（D5）— 不同步骤用不同模型
6. **AIME 失败的深层原因**（D6）— 数学推理优化是否需要不同策略？
7. **分布漂移下的持续适应**（D7）— 生产环境中的轻量级再优化

---

## 七、结论

FAPO 是一篇**系统而诚实**的系统论文。它的贡献不是某个突破性算法，而是一个**经过深思熟虑、有充分实验支撑的工程框架**。核心信息很明确：

> **Pipeline-aware, evidence-grounded optimization with prompt-first escalation beats prompt-only search — and when structural changes are needed, the gains can be dramatic.**

15/18 基准胜率、+14.1 pp 平均增益、+33.8 pp 结构变更增益、安全领域的额外验证——这些数字很有说服力。但更重要的是 FAPO 代表的**工程范式转变**：从"人工调 prompt"到"agent-driven 自动实验"，从"单点优化"到"全链路归因+多级优化"。

对于任何构建多步骤 LLM 系统（security pipeline, enterprise analytics, knowledge work）的团队，FAPO 的工程思路都值得借鉴。

---

## Claim Index

| ID | Claim | Evidence Section |
|----|-------|-----------------|
| C1.1 | Multi-step pipelines fail through step interactions; prompt-only misses bottlenecks | Abstract |
| C1.2 | FAPO beats GEPA in 15/18 comparisons | Abstract, §1 |
| C1.3 | Mean FAPO-GEPA gain = +14.1 pp | Abstract |
| C1.4 | 6 structural-change comparisons: FAPO wins all, mean +33.8 pp | Abstract |
| C1.5 | CTIBench-RCM gains: GPT-5 +4.0, FS-8B-I +7.1, FS-8B-R +2.0 pp | Abstract, §4.4 |
| C2.1 | Claude Code is orchestrator, separate from task model | §3 |
| C2.2 | Prompt-first escalation to structure only when attribution supports | Abstract, §1 |
| C2.3 | Three core agents: optimization, step-attribution, variant-reviewer | §3.1 |
| C2.4 | Three levels: prompt, chain params, chain structure | §3.2 |
| C2.5 | Four guardrails: split access, scope, iteration memory, immutability | §3.3 |
| C2.6 | Tenant model ensures reproducibility, isolation, extensibility | §2.2 |
| C3.1 | HoVer: 3-hop→4-5 hop retrieval, multi-query BM25, entity rescue | §4.3 |
| C3.2 | IFBench: deterministic post-processing nodes, +19.84 to +38.95 pp | §4.3 |
| C3.3 | 9/12 prompt-only wins, 6 with non-overlapping CI | §1, §4.3 |
| C3.4 | AIME: only benchmark where GEPA leads; inconclusive | §4.3 |
| C3.5 | Higher variance with structural changes due to path dependence | §4.5 |
| C3.6 | GPT-4.1-mini outruns GPT-5.4-mini on 4/6 baselines due to token budget | §4.5 |
| C4.1 | Borrows evaluate-analyze-propose-iterate from jailbreaking | §1, §5 |
| C4.2 | GEPA reproduction uses Claude Opus 4.6 reflector | §4.5 |
| C4.3 | FAPO budget: 50 variants or 10 rounds per trial | §4.2 |

---

*Generated by paper-deep-reading v1.2.0 · Subagent deep-read session · 2026-06-19*
