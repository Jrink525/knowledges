# Beyond Static Leaderboards: Predictive Validity for the Evaluation of LLM Agents

**论文标题:** Beyond Static Leaderboards: Predictive Validity for the Evaluation of LLM Agents  
**作者:** Dhaval C. Patel et al. (55+ authors, IBM Research and Columbia University)  
**来源:** arXiv:2606.19704 [cs.AI], 2026  
**DOI:** 10.48550/arXiv.2606.19704  
**Slug:** beyond-static-leaderboards

---

## 1. 问题：静态 Leaderboard 的破产

### 1.1 问题的引入

The evaluation of LLM agents has outgrown its leaderboards. Agents today plan, call tools, reuse artifacts across turns, and coordinate with other agents, yet they are ranked by a small number of aggregate scores inherited from single-shot benchmarks.

这篇论文的核心洞察非常简洁但犀利：当 agent 的能力维度从单轮问答扩展到规划、工具调用、多轮工件复用、多 agent 协调时，继承自单轮 benchmark 的 aggregate-score leaderboard 已经完全无法反映部署行为。

### 1.2 CODS-2025 的冲击波

最有力度的实证来自 CODS-2025 的 149 支队伍 agent 竞赛（Patel et al., 2026）：

| Track | n | Public–Hidden Spearman ρ | 解读 |
|---|---|---|---|
| Execution | 13 | −0.13 (p=0.71) | **统计上不可区分于零**——公开榜排名与隐藏榜排名完全无关 |
| Planning | 20 | 0.69 (CI≈[0.35,0.87]) | 上界落在论文提出的证伪阈值（ρ=0.85） |

一个公开榜排名与隐藏排名 Spearman 为负数的竞赛——这意味着如果 operator 按照公开榜推荐的前三名去部署，**几乎可以肯定选错**。这就是 ``rank instability`` 最直接、最残酷的证据。

## 2. 三个结构性批判

论文的立场建立在三个对 aggregate-score leaderboard 的结构性批判之上。

### 2.1 C1: Aggregate Scores Collapse Orthogonal Dimensions (维度坍缩)

> A Pass1 score of 0.75 can be achieved by many qualitatively different configurations. Aggregate scores treat these as equivalent; deployment treats them as not.

三个具体案例：

- **Per-rubric reasoning sensitivity** (C3.1): Reasoning-on vs. off 在总 rubic 均分上相似，但在 clarity 维度相差 31 个百分点，而 data-retrieval 和 agent-sequence 维度不受影响(Li et al., 2026c)。
- **Multi-turn artifact reuse** (C3.2): Plan-Execute 和 Supervisor-Specialist 在单轮 Pass1 上相似，但 2-5 轮延迟相差 4.2×——一个在单轮 benchmark 中完全不可见的维度(Li et al., 2026b)。
- **Retrieval-strategy trade-off** (C3.3): 单轮 RAG 50-68% 准确率 vs. 多跳 agentic retrieval ~90% 准确率，但伴随 4.5-10× 的 token 膨胀(Li et al., 2026a)。

**关键推论**: 没有一种配置在所有这些维度上同时胜出。aggregate score 让 operator 以为选项等价，但部署选择恰恰需要在这些 trade-off 中决策。

### 2.2 C2: LLM-as-Judge Measurement is Reflexive (裁判反身性)

> Most leaderboards depend on LLM-as-judge scoring, which is itself a measurement instrument with model-specific biases. The leaderboard risks measuring its own judge as much as the systems it evaluates.

三项证据：

- **Condition Insight (C4.1)**: CAR (Condition Agreement Rate) 从 0.68 上升到 0.91——是 prompt 设计而非 backbone 模型的改善(O'Donncha et al., 2026)。
- **ARE/Gaia2 verifier (C4.2)**: DAG oracle 达到 0.99 precision、0.95 recall（无需 LLM 评判）(Froger et al., 2025)。
- **PHMForge (C4.3)**: LLM-as-judge 的 inter-rater reliability 仅有 Krippendorff α=0.61，远低于人类-human 范围 0.74-0.82(Feng et al., 2026)。

**核心论点**: 没有 judge-independent component 的 leaderboard 没有锚点来检测 judge drift。

### 2.3 C3: Out-of-Distribution Behavior is the Deployment Question (OOD 才是部署问题)

> Deployed systems do not encounter the training set or the leaderboard set.

引用经典链：Ethayarajh & Jurafsky (2020) 指出 leaderboard ranks 只"偶然"反映用户效用函数；Dehghani et al. (2021) 的 ``benchmark lottery``；Recht et al. (2019) 的 ImageNet 结果。Exgentic 的跨 benchmark rank 相关性在 0.32-0.85 之间(Bandel et al., 2026)——"current architectures do not achieve robust generalization but instead optimize for specific task distributions."

## 3. 综合：十二层测量体系

### 3.1 七层核心测量 (T1-T7)

由七个现有 benchmark 综合而来的核心层：

| Tier | 名称 | 代表指标 | 来源 |
|---|---|---|---|
| T1 | Success | Pass1, Passk, DAG-Pass | AssetOpsBench, ARE/Gaia2 |
| T2 | Tool-Call Hygiene | tool-name validity, schema compliance, execution success | MCP-Bench |
| T3 | Planning Quality | ROUGE decomposition, Node/Edge F1, chain-order NED | TaskBench, MCP-Bench |
| T4 | Capability Axes | 7 axes: execution, search, adaptability, time, ambiguity, agent-to-agent, noise | ARE/Gaia2 |
| T5 | Cost & Efficiency | $/scenario, step count, latency, budget-scaling curves | MCP-Universe, Gaia2 |
| T6 | Failure Modes | 14 MAST failure modes, distractor robustness, recovery rate | AssetOpsBench |
| T7 | Integrity & Reproducibility | multi-run variance, prompt-shuffle averaging, judge–human agreement | MCP-Bench |

### 3.2 五层部署扩展测量 (T8-T12)

来自 14 组实现研究的部署扩展层：

| Tier | 名称 | 关键维度 | 来源研究 |
|---|---|---|---|
| T8 | Deployment Infrastructure | latency decomposition, MCP-stdio overhead, cross-domain transfer | G7 Battery |
| T9 | Multi-Turn Dialog | cross-turn artifact reuse, per-turn cost dynamics | G5 Multi-Turn |
| T10 | Reasoning Mode | per-phase reasoning cost, adaptive routing precision/recall | G21 Profiling |
| T11 | Knowledge Augmentation | retrieval recall, multi-hop depth, embedding-index quality | G3 Skills+KP |
| T12 | Evidence Grounding & Verification | judge-independent governance, CAR, DAG oracle violations | Condition Insight, ARE/Gaia2 |

**关键洞察**: 没有任何一个现有 benchmark 覆盖超过 4-5 层；T8-T12 在几乎所有已有 benchmark 中完全缺失。

## 4. 预测效度作为排序标准

### 4.1 核心公式

> The right ranking criterion is predictive validity: the correlation between in-sample rank and out-of-sample rank, not in-sample mean.

$$PV(c) = α·Ȳ_c - β·σ_{Y_c,OOD} - γ·IQR(Y_c)$$

其中：
- Ȳ_c = in-sample mean（传统 leaderboard 用这个就够了，但不够）
- σ_{Y_c,OOD} = 跨 OOD 准则的 rank 标准差（惩罚不稳定配置）
- IQR(Y_c) = per-scenario score 的 IQR（惩罚方差大的配置）
- α, β, γ 通过 Criterion-A holdout 拟合

### 4.2 三种 OOD 位移操作化

| 准则 | 难度 | 方法 | 通过的意义 | 失败的意义 |
|---|---|---|---|---|
| A: Held-Out | 轻度 | 分层随机 split，保持 subset×category 联合分布 | passes are uninformative | failures are damning |
| B: Cross-Subset | 中度 | 在 k-1 子集上排名，测试第 k 子集；6 subsets → 6×6 稳定性矩阵 | 最接近实际部署——"你在 chiller 上排的名，能推广到 pump 吗？" | 不可转移 |
| C: Adversarial | 最强 | 四类语义等价扰动：paraphrase, identifier renaming, time-window shifting, distractor injection | 配置真的"解决了任务"而非"记住了模式" | 脆弱 |

### 4.3 证伪条件 (Falsification Thresholds)

论文立场之所以有力量，在于它**明确给出了可以被证伪的条件**：

1. **ρ < 0.85**: In-sample 与 OOD 排名之间的 Spearman 相关性在至少两个 OOD 准则上低于 0.85（否则一般化程度太高，我们的担忧不成立）
2. **Top-3 离开 top-5**: 在 ≥10% 的 holdout split 中，in-sample top-3 配置离开 OOD top-5
3. **Mean-vs-OOD-variance ρ_pearson > 0.2**: 高性能配置不成比例地不稳定
4. **PV top-10 与 mean top-10 的 Jaccard < 0.85**: 否则提出的方法不提供不同的部署指导

**第一条件已部分得到支持**: CODS-2025 执行轨道的公开-隐藏 Spearman ρ=-0.13，远低于 0.85 阈值。

## 5. 汇聚性架构敏感性

### 5.1 十四组实现研究的全景

论文汇聚了在同一 MCP-based benchmark (AssetOpsBench) 上独立开展的 14 组扩展研究，沿六条扩展轴。每组只修改一个架构变量做端到端比较。

**扩展轴与关键发现:**

| 扩展轴 | 组数 | 代表性的关键发现 |
|---|---|---|
| Asset Class | G7, G8 | Battery 6× speedup; Transformer 74.28× end-to-end 优化 |
| Orchestration | G5, G12, G16 | SS 架构 4.2× turn 2-5 加速; MCP vs direct transport 比较 |
| Knowledge/Retrieval | G3, G9, G14, G20 | RAG 50-68% vs Knowledge Plugin ~90%; QLoRA 消除 82.6% 输入 token |
| Infrastructure | G5, G7, G27 | MCP-stdio subprocess overhead 是主导延迟地板 |
| Reasoning Mode | G14, G21 | Reasoning-on 提升 clarity 31pp; 置信门控路由 13%→30.4% 正确率 |
| Evaluation Methodology | G12, G30 | LLM judge IR α=0.61 vs human 0.74-0.82; substrate 消融从 80.8% 降到 25% |

### 5.2 五个汇聚模式 (Convergence Patterns)

**Pattern A: FMSR/TSFM bottleneck** — G5, G14, G16, G27 各自从不同角度定位到同一个瓶颈（TSFM 工具调用时间是主导 wall-clock 占比）。

**Pattern B: Prompt-versus-weight tool knowledge** — G3, G14, G20, G21 从四个不同方向（retrieval, gating, fine-tuning, reasoning）"覆盖"同一个 trade-off 前沿。

**Pattern C: MCP transport overhead** — G7, G9, G12, G27 各自独立测量 MCP-stdio 子进程开销是主导每调用延迟。

**Pattern D: Caching trustworthiness** — G3, G9, G16, G27 都加了 cache，但只有 G9 发现了参数碰撞导致的 F1 上限 0.64——"caching helps" 和 "caching is safe" 是不同的论断。

**Pattern E: Scenario authoring as binding constraint** — G7, G8, G12, G30 都遇到原本 141 场景的语料大小限制。

> Convergence is the strongest evidence we offer for the synthesis; not new experiments, but convergent architectural sensitivity across many.

## 6. PHMForge：一个深入案例

PHMForge 是 14 组研究中最深入的一个(Feng et al., 2026)。它有几点特别值得注意：

- **99 个 SME 撰写的预测场景**，跨越 8 个工业资产类，通过 39 个算法接地 MCP 工具服务
- 唯一使用 ReAct 和 Claude Code（而非 plan-execute）的研究组
- 最强配置 80.8% pass@1，但三个消融实验比标题数字更有信息量：
  - MCP 工具 → text-RAG：RUL pass-all-3 从 100% 降到 20%（5/5 → 1/5）
  - Cross-equipment transfer：从 bearings 84.1% → motors 42.7%（41 点差距）
  - Withholding domain tools：从 80.8% → 25%
- **Orchestration errors dominate failures**，作者原话："stronger at calling tools than at planning when to call them"

## 7. 对 Leaderboard 设计的启示

### Proposal 1: 声明配置而非仅声明模型

Submissions should declare: Architecture, Reasoning Mode, Retrieval Strategy, Prompt-Constraint Level, Verifier Type. 每个都是非空轴，conflating across them produces misleading rankings.

SmartGridBench 的实证支持：2400 trajectory 实验中，transport（direct vs. MCP）和 orchestration（PE vs. Verified PE vs. Self-Ask）独立变化，MCP 标准化增加延迟但不增加质量，而 orchestration 单变量提高 12.3pp pass rate。

### Proposal 2: 分层展示

Layer 1: PV rank headline table → Layer 2: Cost-Pareto plot → Layer 3: Per-tier drill-down panels → Layer 4: Significance and confidence intervals

### Proposal 3: 必需提交要素

Multi-run variance, hardware disclosure, declared tier coverage, raw trajectories. 社区需要两个公共构件：一个共享的 rule pipeline 做 judge-independent verification，以及一个 adversarial-perturbation suite 用于 Criterion C。

## 8. 四个现场级建议

1. **Declare configurations, not just models** — 提交架构、推理模式、检索策略、prompt-constraint 级别、验证器类型
2. **Rank by transfer, not by mean** — 报告至少一个 OOD 准则的 PV 分数；in-sample mean 只是众多列中的一列
3. **Require a judge-independent anchor** — 每个 leaderboard 至少应有一个轨迹级确定性验证器（rule pipeline, DAG oracle 等）
4. **Adopt persistent, non-stdio infrastructure** — 14 组中有 3 组独立识别 MCP-stdio 开销为主导延迟地板

> These four moves do not require a new benchmark; they require a different relationship between leaderboards and the deployments they advise.

## 9. 局限性与自知之明

论文对自身的局限异常坦诚：

| 局限 | 具体内容 |
|---|---|
| **Predictive validity 未经验证** | 指定了实验框架但没有运行它。论文是综合与立场，不是实证发现 |
| **领域特异性** | 所有证据来自工业资产运维，特别是 AssetOpsBench。十二层体系对其他 MCP 域的泛化性未知 |
| **层级正交性未经验证** | "roughly orthogonal" 只是工作假设 |
| **工业部署效度缺口** | 所有 PV 准则仍在 AssetOpsBench 内部，没有与实际部署结果的数据关联 |
| **14 个研究的认识论地位** | 这些是未发表的实现报告，不是同行评审论文 |

## 10. 立场与未来议程

### 10.1 PV Score 的预注册实验设计

论文提出了一个具体的预注册实验：

- **low-power finding (ρ>0.95)**: 修正 down：AssetOpsBench 在 i.i.d. holdout 下高度稳定
- **middle finding (0.65 < ρ < 0.95)**: 按计划进行完整研究
- **strong finding (ρ < 0.65)**: 立场如此强有力以至于可以用减少范围的实验来达成

### 10.2 四个未来方向集群

Appendix F 汇聚了 14 个研究的 forward-looking suggestions，形成四个集群：

- **Cluster I: Adaptive meta-router** — 5 组共同呼吁学习型路由器替代静态管道
- **Cluster II: Persistent non-stdio MCP servers** — 3 组各自指出 stdio 延迟地板
- **Cluster III: Cross-model and cross-asset generalization** — 4 组呼吁拓展模型与资产类
- **Cluster IV: Scenario-corpus expansion** — 4 组呼吁突破 141 场景限制

> The aggregate of these four clusters is exactly the position-paper thesis.

---

## 声明索引 (Claim Index)

| 编号 | 声明 | 证据 | 章节 |
|---|---|---|---|
| C1.1 | Aggregate-score leaderboards underspecify deployed-agent evaluation | CODS-2025 ρ=-0.13 (execution) and ρ=0.69 (planning) | §1 |
| C2.1 | Aggregate scores collapse orthogonal dimensions | Three concrete cases: reasoning sensitivity 31pp, multi-turn 4.2× latency, RAG vs KP trade-off | §2.1 |
| C2.2 | LLM-as-judge measurement is reflexive | CAR 0.68→0.91 from prompt alone; Krippendorff α=0.61 vs human 0.74-0.82 | §2.2 |
| C2.3 | OOD behavior is the deployment question, not in-sample mean | Exgentic cross-benchmark ρ=0.32-0.85; CODS-2025 gap | §2.3 |
| C3.1 | No single benchmark covers >5 of 12 tiers | Figure 2: Coverage analysis across 9 source benchmarks | §3 |
| C4.1 | Three OOD criteria operationalize the predictive validity concept | Criteria A (held-out), B (cross-subset), C (adversarial) | §4.1 |
| C4.2 | Four falsification thresholds specify when position is refuted | ρ<0.85, top-3 departure, mean-OOD variance correlation, Jaccard <0.85 | §4.3 |
| C5.1 | 14 implementation studies converge on same measurement gaps | Five convergence patterns (A-E) across 14 groups | §5, Appendix E |
| C5.2 | MCP-stdio transport overhead is a dominant latency floor | G7, G9, G12, G27 independently measure this | §5, Appendix E |
| C5.3 | Judge-independent verification is feasible | ARE/Gaia2 0.99 precision; Condition Insight CAR; PHMForge α=0.61 | §5.3 |
| C6.1 | Predictive validity score PV(c) combines mean with OOD reliability | PV(c) = αȲ_c - βσ_Y_c,OOD - γIQR(Y_c) | §4.2, Appendix G |
| C6.2 | Substrate underspecification dominates failure modes | PHMForge: withholding domain tools drops 80.8%→25% | §5.4 |
| C7.1 | Four field-level recommendations for next-gen agent benchmarks | Declare configs, rank by transfer, require judge anchor, adopt persistent infra | §6, §7 |

---

## 词汇表

| 术语 | 定义 |
|---|---|
| Predictive Validity | In-sample rank 与 out-of-sample rank 的相关性，而非 in-sample mean |
| Rank Instability | 不同分布设置下 leaderboard 排名不一致 |
| MCP | Model Context Protocol — 模型工具调用协议 |
| PV Score | Predictive Validity Score: α·mean - β·OOD_std - γ·IQR |
| OOD Criterion | Out-of-Distribution 位移操作化：holdout, cross-subset, adversarial |
| Falsification Threshold | 立场被认为不成立的具体条件集 |
| CAR | Condition Agreement Rate — LLM 分类与 rule-based pipeline 比对 |
| ARE/Gaia2 | Agent 轨迹级验证，使用 human-annotated oracle DAGs |
| PHMForge | Prognostics Health Management Benchmark，99 个 SME 场景，8 个资产类 |
| T1-T12 | 十二层测量体系的每层 |

---

*Deep-read generated: 2026-06-19 | Paper: arXiv:2606.19704 | Slug: beyond-static-leaderboards*
