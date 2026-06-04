# Harness Updating Is Not Harness Benefit: Disentangling Evolution Capabilities in Self-Evolving LLM Agents

> **论文**: Lin et al., 2026. arXiv:2605.30621.
> **来源**: arXiv LaTeX source package (pdflatex, ACL style). 8 .tex files + 9 PDF figures + bib.
> **状态**: Deep-read complete. Evidence packages verified.

---

## 一句话论点

> **Harness-updating（产生有用 harness 更新的能力）与模型的基础能力无关，而 harness-benefit（从更新后的 harness 中获益的能力）与基础能力呈非单调关系——中等能力的模型受益最大，弱模型和强模型反而受益更少。**

---

## 研究方程

```
给定: LLM agent = (frozen LLM f, editable external harness H)
观测: 自进化过程在 f 固定时迭代更新 H
问题: 更新 H 的能力（harness-updating）和使用 H 的能力（harness-benefit）
      是否与 f 的基础任务求解能力相关？
发现: 
  harness-updating ∦ base capability（平坦）
  harness-benefit ⨆ base capability（非单调，倒 U 形）
```

---

## 标题解读

"Harness Updating Is Not Harness Benefit" — 标题本身就是论文的核心论点。Evolver（更新者）和 solver（使用更新者）是同一个模型的两个不同角色，它们所需的能力不同。一个能写好 harness 的模型不一定能从 harness 中获益，反之亦然。标题的对称结构（"X Is Not Y" + 冒号说明）精确地传达了论文的分解式思考方式。

---

## 问题：论文到底在解决什么问题？

### Problem Ladder

| 层 | 问题 | 论文的回答 |
|----|------|-----------|
| **L1 (现象)** | 自进化 agent 系统的端到端收益来自哪里？ | 端到端分数混淆了两个独立来源 |
| **L2 (分解)** | Harness-updating 和 harness-benefit 如何分别测量？ | 定义两种能力 + 交叉配对实验设计 |
| **L3 (实证)** | 这两种能力与模型的基础能力相关吗？ | Updating 平坦，Benefit 非单调 |
| **L4 (归因)** | 弱模型为什么获益少？ | 两种失效模式：activation failure + adherence failure |
| **L5 (指导)** | 系统设计者应该把预算投在哪？ | 投给 task-solving agent，不是 evolver |

### 现状的盲点

现有自进化方法（Reflexion, Self-Refine, GEPA, EvolveR, SkillRL 等）的评估都是**端到端**的：一个进化方法 + 一个 agent 模型 + 一个 benchmark → 看最终分数。这种评估把三种能力混在一起：

> "The gain may come from the evolver producing higher-quality harness updates, or from the task-solving agent using the updated harnesses more effectively. End-to-end scores cannot disentangle these contributions."

这篇论文的核心贡献不是提出新方法，而是**提出了一种测量框架**来拆解这些混杂的因素。

---

## 作者如何找到这个方向？

*推测性重建：*

现有自进化文献中有一个被广泛注意到但从未系统分析的现象：同样的进化算法不同的 backbone 效果差异很大。但现有论文的常规处理是将这种差异归因于"模型能力"。作者面前的问题是：如果把 evolver 和 solver 拆成两个不同的模型来配对，这个差异到底来自谁？

一旦把问题表述为"两种角色、两种能力"，自然实验设计就是**交叉配对矩阵**：固定 evolver 变 solver、固定 solver 变 evolver。这个设计在机器学习中很常见（消融研究的变体），但据我所知之前没有人用在自进化能力分解上。

- [C1.1][evidence-backed interpretation] The paper's central innovation is an evaluation framework, not a new algorithm. The cross-pairing matrix (7 models × 3 anchor agents × 3 benchmarks + 6 models × 3 anchor evolvers × 3 benchmarks) is the core methodological contribution.

---

## 故事构建

论文的叙事结构非常清晰：

1. **Introduction**: 提出问题（端到端评估隐藏了来源）→ 定义两种能力 → 预告两个关键发现
2. **Related Work**: 展示现有自进化方法 → 指出评估盲点
3. **Method**: 形式化定义 harness 状态、evolver、协议、三种指标
4. **Experiments (evolver side)**: 发现 1 — harness-updating 平坦
5. **Experiments (agent side)**: 发现 2 — harness-benefit 非单调 → 归因为两种失效模式
6. **Conclusion**: 设计指导

这种"先宏观发现 → 再微观归因"的叙事节奏值得学习。特别是 agent-side 分析部分，它先展示倒 U 形曲线这个宏观现象，然后逐层深入：activation failure → adherence failure → phase-level drift，越来越细。

---

## Related Work 与关键引用

论文明确区分两条线：

- **Harness engineering**（表示层）：prompts / tools / memory / skills / code 这五种 artifact 类型。关键引用：ReAct, SWE-agent, Terminal-Bench, ToolACE, ReasoningBank, MetaHarness 等。
- **Self-evolution**（更新层）：task-level feedback → persistent harness updates。关键引用：Reflexion, Self-Refine, GEPA, EvolveR, SkillRL, ACE 等。

**引用的功能定位**：这些引用不是装饰性的。每个引用在论文中承担一个具体角色：要么作为"现有方法覆盖了这个组件但我没做"的边界声明，要么作为"我们的交叉配对评估填补了这些端到端评估的盲点"的靶子。

论文没有引用任何"模型能力评估/分解"方向的工作（如 BIG-bench、MMLU 的分解式分析），这是一个遗漏——如果引用 behavioral scaling laws 或 capability decomposition 的相关文献，位置会更清晰。

- [C2.1][evidence-backed interpretation] The paper correctly identifies the evaluation gap in existing self-evolution work but misses a relevant citation line on capability decomposition methodology.

---

## 方法详解

### Harness 形式化

$$
A_t = (f, H_t)
$$

- $f$: 模型 backbone（固定）
- $H_t$: 第 $t$ 步的 harness 状态（可编辑组件：prompts, skills, memories；不可编辑：tool interfaces, execution policies）

### Evolver 形式化

$$
\Delta H_t = e(H_{t-1}, \mathcal{D}_t), \quad H_t = \mathrm{Apply}(H_{t-1}, \Delta H_t)
$$

- $e$: evolver（LLM 实例化）
- $\mathcal{D}_t$: 执行证据（轨迹 + 输出 + 反馈）

### 进化协议

迭代循环：solve（一批任务）→ collect evidence → evolve（更新 harness）→ next batch. 每步的任务在 $H_{t-1}$ 下评分，然后其 evidence 才用于生成 $H_t$（in-situ 评估，避免数据泄露）。

### 三种指标

| 指标 | 符号 | 含义 | 测量方式 |
|------|------|------|---------|
| **Base Capability** | $M_{\text{base}}(f)$ | 无进化时模型的基线性能 | $J_{\mathcal{X}}(f, H_0)$ |
| **Harness-Updating** | $\Delta_{\text{update}}(e)$ | evolver 产出的 harness 更新所能带来的平均增益 | $\frac{1}{|\mathcal{F}^{\star}|} \sum_{f \in \mathcal{F}^{\star}} \Delta(f, e)$ |
| **Harness-Benefit** | $\Delta_{\text{benefit}}(f)$ | agent 从进化后的 harness 中获得的最大增益 | $\max_{e \in \mathcal{E}^{\star}} \Delta(f, e)$ |

关键设计选择：$\Delta_{\text{benefit}}$ 使用 max 而非 mean。作者的解释是"测量 model 的最佳可获得增益"。这意味着论文承认同一个模型用不同 evolver 效果不同，关注的是上限而非平均。这是一个有意识的选择：如果你想测量"这个模型硬上限能收益多少"，max 是合理的；但如果你关心"这个模型在随机 evolver 下的预期收益"，mean 会更合适。

- [C3.1][evidence-backed interpretation] Using max rather than mean for $\Delta_{\text{benefit}}$ reflects an "upper-bound capability" lens, not an "expected benefit" lens.

---

## 实验设计

### 基准（Benchmarks）

| Benchmark | 任务数 | 领域 | 评估方式 |
|-----------|--------|------|---------|
| SWE-bench Verified | 500 | 软件工程（12 repos） | 二进制 pass rate（hidden tests） |
| MCP-Atlas | 500 | 工具编排（36 MCP server, 220 tools） | claims-based rubric → 二进制 pass rate |
| SkillsBench | 86 | 通用技能执行（11 domains） | 二进制 pass rate（5 trials avg） |

### 模型

- **Closed-source**: Claude Opus 4.6, Sonnet 4.6, Haiku 4.5
- **Open-source**: Qwen3-235B-A22B, Qwen3-32B, Qwen3.5-9B, GPT-OSS-120B

### 实验规模

- Evolver-side: 7 evolvers × 3 anchor agents × 3 benchmarks = 63 runs
- Agent-side: 6 agents × 3 anchor evolvers × 3 benchmarks = 54 runs
- 总量: ~117 个独立 cell（每个 cell 对应一个 agent-evolver 配对在某个 benchmark 上的完整进化循环）

---

## 发现 1: Harness-Updating 是平坦的

**核心结果**: 不同能力层的 evolver 产生的 harness 更新所带来的增益差异非常小。

| Benchmark | 最佳 evolver | 最差 evolver | 差距 |
|-----------|-------------|-------------|------|
| SWE | Qwen3-235B (8.2pp) | GPT-OSS-120B (5.9pp) | 2.3pp |
| MCP | Opus 4.6 (3.6pp) | Qwen3-235B (0.6pp) | 3.0pp |
| SB | Qwen3.5-9B (3.8pp) | Qwen3-32B (0.7pp) | 3.1pp |

**关键数据点**:
- 最小的 evolver Qwen3.5-9B 在 SB 上取得最高增益（3.8pp），超过 Opus 4.6（2.3pp）
- 没有 evolver 在所有 benchmark 上占优
- Qwen3-235B 在 SWE 上领先（8.2pp）但在 MCP 上垫底（0.6pp）

**机制分析**（case study）：一个 SkillsBench task `flink-query` 上，Qwen3.5-9B 和 Opus 4.6 编写的 skill 在过程上是**同构的**（相同的五个步骤序列），只在实现细节（API 函数选择）和详细程度上不同。两者注入到同一个 Opus 4.6 agent 后产生相同的提升。

**更深的结论**：Post-evolution 的最终分数由 agent 的 base capability 主导，不是由 evolver 的身份主导。即使把最强的 agent 配最差的 evolver、最弱的 agent 配最好的 evolver，强 agent 仍然领先 18.6-35.2pp。

- [C5.1][evidence-backed interpretation] Harness-updating gain across 7 evolvers spans at most 3.1pp on any benchmark, confirming flatness.
- [C5.2][evidence-backed interpretation] Post-evolution performance is dominated by the task-solving agent's base capability, not evolver identity. Extreme pairings show strong agents still lead by 18.6-35.2pp.

---

## 发现 2: Harness-Benefit 是非单调的（倒 U 形）

**核心结果**: 中等能力模型从进化 harness 中获益最多，弱模型和强模型获益都少。

**SWE-bench 数据**:

| Model | Base (%) | $\Delta_{\text{benefit}}$ (pp) |
|-------|---------|------------------------------|
| Qwen3-32B | 3.6 | 4.4 |
| Qwen3-235B | 20.7 | **19.3** |
| GPT-OSS-120B | 26.2 | 15.8 |
| Haiku 4.5 | 66.0 | 2.4 |
| Sonnet 4.6 | 73.2 | 2.8 |
| Opus 4.6 | 74.2 | 2.6 |

在 MCP 上，峰值移到了 GPT-OSS-120B（7.0pp）而不是 Qwen3-235B（4.3pp）。在 SB 上，Haiku 4.5 取得最高增益（15.1pp），但由于多个模型的 base 接近零，SB 的排序噪音大。

**两端解释**：
- **强模型端**：天花板效应。已经能解决大多数任务，剩余提升空间小。
- **弱模型端**：天花板解释不成立——弱模型有最大的提升空间（base 最低），但实际提升最小。说明存在不同的瓶颈。

- [C6.1][evidence-backed interpretation] $\Delta_{\text{benefit}}$ follows an inverted-U shape: mid-tier models benefit most, with the pattern confirmed on SWE and MCP (cleanest) and SB (noisier but not contradicting).

---

## 发现 3: 弱模型获益少的两种失效模式

### 失效模式 1: Harness Activation Failure

**问题**: 弱模型无法将相关 harness artifacts（如 skill）加载到工作上下文中。

**数据**（SkillsBench 上的 Skill-Load Rate, SLR）:

| Model | SLR |
|-------|-----|
| Qwen3-32B | 0.251 |
| GPT-OSS-120B | 0.446 |
| Haiku 4.5 | 0.794 |
| Qwen3-235B | 0.961 |
| Sonnet 4.6 | 0.959 |
| Opus 4.6 | 0.957 |

**机理**: 观察到一个典型的失败案例——Qwen3-32B 正确识别了相关的 skill，但在发出 `load_skill` 动作时，把它和其他推理内容打包成一个**多键 JSON 动作**。SkillsBench 的格式 gate 只接受单键动作，拒绝了这个复合请求。skill body 从未进入 context。

**关键洞察**: 这不是任务理解失败，而是**协议层失败**。模型知道要加载什么，但无法将意图转化为 runner 期望的格式。

### 失效模式 2: Harness Adherence Failure

**问题**: 即使 skill 被成功加载，弱模型也无法忠实地遵循其指导。

**数据**（Harness-Following Rate, HFR）:

| Model | HFR |
|-------|-----|
| Qwen3-32B | 0.142 |
| GPT-OSS-120B | 0.442 |
| Haiku 4.5 | 0.600 |
| Qwen3-235B | 0.350 |
| Sonnet 4.6 | 0.730 |
| Opus 4.6 | 0.757 |

**分离 activation 和 adherence 的关键数据点**: Qwen3-235B 的 SLR 是 0.961（接近 Opus 4.6 的 0.957），但 HFR 只有 0.350（远低于 Opus 4.6 的 0.757）。这意味着**加载能力不等于遵循能力**。

**机理**: 观察到一个案例——Qwen3-32B 成功加载了一个 procedural skill（TTS-fallback chain），但把它当作**字面脚本**而非**应急程序**执行。第一步失败后，没有调用 skill 中预设的 fallback 步骤，最终在不满足条件时宣称 task complete。

### 长期指令遵循的衰减

**相位级分析**: 对 Qwen3-32B（weak）、GPT-OSS-120B（mid）、Opus 4.6（strong）的 adherence score 随时间步的变化：

| Phase | Qwen3-32B | GPT-OSS-120B | Opus 4.6 |
|-------|-----------|-------------|---------|
| Harness loaded | 0.52 | 0.67 | 0.89 |
| Mid turn | 0.22 | 0.48 | 0.79 |
| Final turn | 0.13 | 0.43 | 0.80 |
| **drift (load → final)** | **-0.39** | **-0.24** | **-0.09** |

弱模型的 adherence 在轨迹尾部衰减了 0.39（-75%），而强模型只衰减 0.09（-10%）。这指出了一个更深的瓶颈：**long-horizon instruction following**。弱模型不是加载时就读错了——它们开始时读对了在执行过程中慢慢偏离。

- [C7.1][evidence-backed interpretation] Two failure modes explain weak-tier low $\Delta_{\text{benefit}}$: harness activation failure (SLR as low as 0.251 for Qwen3-32B) and harness adherence failure (HFR as low as 0.142).
- [C7.2][evidence-backed interpretation] Activation and adherence are separable: Qwen3-235B has near-perfect SLR (0.961) but low HFR (0.350), proving loading ≠ following.
- [C7.3][evidence-backed interpretation] Adherence decays over trajectory for weak models: Qwen3-32B drifts -0.39 from load to final turn, whereas Opus 4.6 drifts only -0.09.

---

## Reviewer-Lens Audit

### Novelty

**Strong sides**:
- 首次将自进化的端到端效果分解为两种独立能力
- 交叉配对实验设计在方法论上很干净
- 两种失效模式的归因分析深入且有说服力

**Weak spots**:
- 方法论贡献（分解框架）而非算法贡献，适合 ACL 的 analysis track。如果在 ICLR/NeurIPS 环境下，可能被质疑"无新方法"
- 分解为两种能力的基本框架并非完全原创——类似的概念在 multi-task learning 的 capability decomposition 中被使用过

### Technical Soundness

**Strong**:
- 实验规模大（117+ cells）
- 控制充分：prompt 模板、轨迹窗口、进化预算、per-task turn limit 全部固定
- SLR/HFR/phase-drift 的测量设计合理
- HFR judge pipeline 有 blinded + Sonnet 4.6 judge 控制

**Concerns**:
- HFR judge 使用 Sonnet 4.6 → 可能存在 judge bias（对其他模型不够公平？）作者做了 blinding，但 judge 模型本身的能力偏差无法完全消除。一个跨 judge 一致性的分析（比如用另一个 LLM 做 judge 是否得到相同结论）被遗漏了。
- $\Delta_{\text{benefit}}$ 使用 max 而非 mean 的 rationale 是合理的但不完整——max 可能高估了实用性
- MCP 和 SB 上的趋势不如 SWE 上明显，论文对此诚实讨论了
- 三个 benchmark 的可编辑 harness 组件不同（SWE/SB: skills only; MCP: skills + prompts + memory），这是一个不必要的可变因素

### Baseline Completeness

实验中"no evolution baseline"（$H_0$，初始 harness）是合理的 baseline。但缺少两种额外控制：
1. **Random harness**: 如果 harness 更新只是随机写的，效果如何？
2. **Human-written harness**: 人工编写的 skill 与 evolver 生成的 skill 对比如何？

这两个控制能帮助判断 "flat" 是因为所有 evolver 都好，还是所有 evolver 都差。

- [C8.1][speculation] Missing baselines (random harness, human-written harness) weaken the claim that harness-updating is truly "flat" rather than "uniformly weak."
- [C8.2][plausible inference] HFR judge pipeline may contain judge-model bias despite blinding. A cross-judge agreement analysis is absent.

---

## 创新类型与科学边界判断

| 维度 | 判断 |
|------|------|
| **Innovation type** | Analysis / Measurement — 不是新算法，是新测量框架 |
| **Method novelty** | 中 — 交叉配对设计在 ML 中常见但未用在自进化领域 |
| **Finding novelty** | 高 — Harness-updating 平坦、harness-benefit 倒 U 形、两种失效模式都是新发现 |
| **Practical impact** | 高 — "投给 agent 不投 evolver" 的指导直接可操作 |
| **Scientific boundary** | 在"测量"和"归因"层面贡献明确；在"解决问题"层面没有新方案 |

---

## 可复用的故事模式

这篇论文的叙事结构在 analysis-based 论文中很优秀：

1. **Define the blind spot**: "端到端分数隐藏了能力来源" → 读者立刻认同这是个重要问题
2. **Propose a decomposition**: 两角色 × 两能力 → 干净的形式化
3. **Show the macro pattern**（evolver-side）: "所有 evolver 差不多" → 反直觉，吸引读者
4. **Show the micro pattern**（agent-side）: "倒 U 形" → 更反直觉
5. **Drill into the cause**: 两个失效模式，每个有具体 case study → 让读者"看到"失败
6. **Extract the deeper bottleneck**: long-horizon instruction following → 揭示根本原因
7. **Derive actionable guidance**: 三条设计建议 → 读者带走能用

每一步都在回答"所以呢？"（So what?），这是 analysis 论文最难做到的。

---

## 局限与弱点

1. **模型覆盖不完整**：7 个模型不足以完全覆盖能力谱系。特别是 open-source 阵营在高端缺失（没有 Llama 4、Gemma 3 等）。
2. **Benchmark 代表性**：SWE-bench 是 binary pass/fail，MCP 和 SB 也是离散或近似二进制评估。如果使用连续分数指标（如 pass@k），可能会揭示更多微妙差异。
3. **可编辑组件不一致**：三个 benchmark 的 harness scope 不同，增加了跨 benchmark 对比的噪音。
4. **HFR judge pipeline 的可靠性**：只使用了一个 judge 模型（Sonnet 4.6），没有 judge agreement 分析。
5. **进化协议的通用性**：实验只使用了 A-EVOLVE-V3 的一种 evolution 算法（`adaptive_skill`）。不同算法可能对不同模型的效果差异不同。
6. **缺失对 evolver 的深入分析**：论文说明 harness-updating 是平坦的，但没有分析**为什么**——是由于 harness 任务（skill writing）比较简单，还是由于 evolver 的搜索空间受限？这个空白对理解能力的本质很重要。
7. **Cost 维度缺失**：Qwen3.5-9B 和 Opus 4.6 作为 evolver 效果相似，但成本差了几个数量级。这个差异在实验中未被讨论。

- [C9.1][evidence-backed interpretation] The paper honestly acknowledges scope: "We do not evaluate parametric fine-tuning, reinforcement learning of model weights, or hybrid adaptation methods."

---

## 未来方向

### 方向 1: 验证 harness-updating 平坦性在不同进化算法下是否成立

- **种子类型**: assumption violation
- **假设**: Harness-updating 的平坦性可能只对 `adaptive_skill` 这种简单算法成立；更复杂的算法（如 SkillRL 的 RL-based evolution）可能放大 evolver 间的差异
- **最小实验**: 对 3 个能力层级的 evolver（small/medium/large），在同一个 benchmark 上用 3 种演化算法（adaptive_skill, SkillRL-style, GEPA-style）重复更新测量
- **消极结果解释**: 如果所有算法都平坦 → 说明 harness-updating 能力的本质就是平坦的；如果不平坦 → 找到了调节因素
- **致命反对**: 更复杂算法的差异可能来源于 algorithm-model interaction 而非模型能力差异
- **关键结果**: 即使一个算法下所有 evolver 效果相似，换算法后排序发生变化

### 方向 2: 构建 adversarial harness 以解耦 activation 和 adherence

- **种子类型**: proxy mismatch
- **假设**: Activation 和 adherence 是两种分离的技能，可以通过针对性 adversarial 测试来验证
- **实验**: 构造需要特定格式激活的 harness（如不同协议格式），测试模型从重新格式化到激活的能力；再构造需要复杂分支处理的 harness，测试 adherence
- **注意**: 论文中的 activation 和 adherence 是相关而非因果的，构造 adversarial 测试可以证实或证伪它们是否真正独立

### 方向 3: Long-horizon instruction following 的显式训练

- **种子类型**: evidence gap
- **假设**: 弱模型的 adherence 衰减是长期指令遵循能力不足的表现，可以通过在训练中加入"监督性衰减对抗"来缓解
- **实验**: 在弱模型的训练数据中加入 long-range feedback，要求模型在长轨迹中持续引用初始指令
- **关键结果**: 如果 adherence 在训练后不再衰减 → 问题可训练解决；如果仍衰减 → 存在更深的架构瓶颈

### 方向 4: 使用随机 harness 作为更严格的 baseline

- **种子类型**: reviewer objection
- **假设**: "所有 evolver 差不多"可能是因为 harness 更新的内容不是关键信息，而只是任何结构化信息都会带来提升
- **实验**: 将真正的 harness 更新替换为随机生成的 procedural text（保留相似的格式和长度但内容无意义），对比效果
- **消极结果解释**: 如果随机 harness 也能带来相同提升 → 论文的"平坦性"实际上是因为 harness evolution 本身效果有限
- **致命结果**: 随机 harness 的无提升 → 验证 evolver 的更新确实有内容价值

---

## 附录: Claim -> Evidence Index

| Claim | Type | Source | Location |
|-------|------|--------|----------|
| C1.1 | evidence-backed | "Evaluation of these methods still asks an end-to-end question... The gain may come from the evolver producing higher-quality harness updates..." | `1_introduction_v2.tex` lines ~80-100 |
| C2.1 | evidence-backed | Related Work section | `2_related_work.tex` entire file |
| C3.1 | evidence-backed | §4.3 definition of $\Delta_{\text{benefit}}$ as max | `4_method_v4.tex` lines ~130-140 |
| C5.1 | evidence-backed | Fig. 3, Tab. 5 | `5_experiments_v5.tex` Fig. 3 caption |
| C5.2 | evidence-backed | Fig. 4 caption, Tab. 6 | `5_experiments_v5.tex` Fig. 4, Appendix Tab. 6 |
| C6.1 | evidence-backed | Tab. 1, Fig. 5 | `5_experiments_v5.tex` Tab. 1, Fig. 5 |
| C7.1 | evidence-backed | Tab. 2, Fig. 6 | `5_experiments_v5.tex` Tab. 2 |
| C7.2 | evidence-backed | Qwen3-235B SLR=0.961 vs HFR=0.350 | `5_experiments_v5.tex` Tab. 2 |
| C7.3 | evidence-backed | Tab. 3 | `5_experiments_v5.tex` Tab. 3 |
| C8.1 | speculation | Missing baselines | `5_experiments_v5.tex` §5.2 |
| C8.2 | plausible inference | Single judge model (Sonnet 4.6) | `8_appendix_v2.tex` §HFR pipeline |
| C9.1 | evidence-backed | § Limitations | `7_conclusion.tex` |

---

*Deep-read report by Jarvis II | arXiv:2605.30621 | June 2026*
