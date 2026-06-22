# Beyond Static Leaderboards: Predictive Validity for the Evaluation of LLM Agents

## Paper Information

| Field | Value |
|-------|-------|
| **Title** | Beyond Static Leaderboards: Predictive Validity for the Evaluation of LLM Agents |
| **Authors** | Dhaval C. Patel, Kaoutar El Maghraoui, and 55+ co-authors |
| **Venue** | arXiv preprint, submitted 18 Jun 2026 |
| **arXiv ID** | 2606.19704 |
| **Domain** | cs.AI (Artificial Intelligence) |
| **Pages** | 17 pages, 2 tables, 5 figures |
| **License** | CC BY 4.0 |
| **Slug** | beyond-static-leaderboards-predictive-validity-for-the-evaluation-of-llm-agents |

---

## 1. Abstract

Agent benchmarks are growing fast, but no single benchmark touches more than four or five of the dimensions that deployment exposes. This paper aggregates the largest coordinated deep-dive of one MCP-based industrial-agent benchmark to date: fourteen parallel implementation studies covering new asset classes (including a multi-modal visual extension), alternative orchestrations, retrieval strategies, reasoning modes, infrastructure optimizations, and evaluation-methodology probes. Consolidating those studies with seven prior agent benchmarks, the authors argue that aggregate-score leaderboards systematically underspecify deployed-agent evaluation. Rankings derived from aggregate scores do not transfer to out-of-distribution settings; recent public-to-hidden competition retrospectives provide direct empirical evidence of this rank instability. The paper proposes ranking configurations by **predictive validity** — the correlation between in-sample and out-of-sample rank, rather than in-sample mean — and reports a **twelve-tier measurement apparatus** that exposes the deployment-relevant dimensions HELM and its agent-era successors collapse. The position is operationalized through three falsifiable out-of-distribution criteria with explicit thresholds. The paper closes with a pre-registered pilot design and a field-level vision for what the next generation of agentic benchmarks should report.

---

## 2. Problem Definition and Motivation

### 2.1 The Core Problem

The evaluation of LLM agents has outgrown its leaderboards. Agents today plan, call tools, reuse artifacts across turns, and coordinate with other agents, yet they are ranked by a small number of aggregate scores inherited from single-shot benchmarks. The result is **rank instability**: rankings derived from aggregate scores do not predict what an operator would observe in deployment.

### 2.2 The CODS-2025 Competition Data Point

In the 149-team CODS-2025 AssetOpsBench competition (Patel et al., 2026), the Spearman correlation between public-leaderboard rankings and hidden-evaluation rankings was:
- **Execution track**: ρ = −0.13 (n=13, p=0.71, statistically indistinguishable from zero)
- **Planning track**: ρ = 0.69 (n=20, robustly positive, but the upper 95% confidence bound falls at the falsification threshold)

With n=13, the 95% bootstrap CI on the execution correlation spans roughly [−0.64, +0.45]. The planning track's mean private scores still fall 11.3 points below public, and public scores saturate (8 unique values across 20 teams).

### 2.3 Two Streams of Prior Work

**Stream 1 — Wave of agent benchmarks**: SWE-Bench (Jimenez et al., 2024), τ-Bench (Yao et al., 2024), ARE/Gaia2 (Froger et al., 2025), MCP-Universe (Luo et al., 2025), MCP-Bench (Wang et al., 2026), AssetOpsBench (Patel et al., 2025), Exgentic (Bandel et al., 2026). Each surfaces a different facet of trajectory-level evaluation but still ranks configurations by aggregate score.

**Stream 2 — NLP critique of single-score ranking**: Ethayarajh and Jurafsky (2020), Bowman and Dahl (2021), Raji et al. (2021) questioning single-score ranking; HELM (Liang et al., 2022) and Dynabench (Kiela et al., 2021) as multi-dimensional frameworks; Ribeiro et al. (2020) for behavioral testing. HELM broadens dimensions for single-shot models, but agents introduce orthogonal axes (orchestration, multi-turn artifact reuse, tool-call hygiene, judge-independent verification) that HELM does not score.

---

## 3. Position Statement

> **Position:** Aggregate-score leaderboards systematically underspecify the dimensions on which deployed LLM agents are evaluated. The field would benefit from a multi-tier measurement apparatus ranked by predictive validity rather than in-sample mean.

### Three Supporting Claims

| Claim | Summary |
|-------|---------|
| **C1** | Existing benchmarks measure overlapping subsets of a larger measurement space; their findings, taken together, suggest the larger space is non-redundant. |
| **C2** | Within a single industrial domain, parallel implementations by independent teams converge on evaluation dimensions that no single benchmark surfaces. |
| **C3** | Predictive validity (how in-sample rankings forecast out-of-sample rankings) is a more useful ranking criterion than in-sample mean for deployment decisions. |

---

## 4. Three Structural Critiques of Aggregate-Score Leaderboards

### 4.1 Aggregate Scores Collapse Orthogonal Dimensions (Section 2.1)

A Pass1 score of 0.75 can be achieved by qualitatively different configurations:
- Reasoning-heavy and cost-expensive
- Retrieval-rich and latency-bound
- Tool-hygiene-fragile but artifact-reuse-efficient

**Three concrete cases:**

| Case | Finding | Source |
|------|---------|--------|
| Per-rubric reasoning sensitivity | Reasoning-on vs. reasoning-off score similarly on overall rubric mean but differ by **31 pp on clarity-specific scoring**; data-retrieval and agent-sequence dimensions unchanged | Li et al., 2026c |
| Multi-turn artifact reuse | Plan-Execute and Supervisor-Specialist score similarly on single-turn Pass1 but differ by **4.2× on turn-2-to-5 latency** due to cross-turn artifact reuse | Li et al., 2026b |
| Retrieval-strategy trade-off | Single-pass RAG: 50–68% accuracy vs. agentic multi-hop: ~90% accuracy with **4.5×–10× token inflation** | Li et al., 2026a |

### 4.2 LLM-as-Judge Measurement is Reflexive (Section 2.2)

Most leaderboards depend on LLM-as-judge scoring (Zheng et al., 2023), which has model-specific biases. As judge models evolve, ranking shifts; as judge prompts are adjusted, scores move.

**Three evidence points:**
1. **Condition Insight**: CAR moves from 0.68 to 0.91 under constrained-prompting design — a 20pp improvement attributable to prompting, not backbone-model choice (O'Donncha et al., 2026)
2. **ARE/Gaia2 DAG oracle**: 0.99 precision and 0.95 recall against 450 hand-labeled trajectories — judge-independent verification is feasible (Froger et al., 2025)
3. **PHMForge**: LLM-as-judge inter-rater reliability reaches only Krippendorff α=0.61, well below human-human range α∈[0.74, 0.82] on the same sample (Feng et al., 2026)

### 4.3 Out-of-Distribution Behavior is the Deployment Question (Section 2.3)

Deployed systems encounter three types of scenarios:
- Distributionally similar to held-out cases
- Distributionally distinct (cross-domain transfer)
- Adversarially perturbed by user phrasing

In-sample mean predicts none of these directly. Exgentic observed cross-benchmark rank correlations of 0.32–0.85 across six heterogeneous benchmarks (Bandel et al., 2026), concluding that "current architectures do not achieve robust generalization but instead optimize for specific task distributions."

---

## 5. The Synthesis: Twelve-Tier Measurement Apparatus (Section 3)

The twelve tiers are consolidated from seven source benchmarks plus fourteen parallel implementation studies. No single prior benchmark reports more than four or five tiers.

### Core Capability Tiers (T1–T7)

| Tier | Dimension | Source | Representative Metric |
|------|-----------|--------|----------------------|
| T1 | Success | AssetOpsBench, ARE/Gaia2 | Pass1, Passk, DAG-Pass |
| T2 | Tool-Call Hygiene | MCP-Bench | Tool-name validity, schema compliance, execution success, dependency-order correctness |
| T3 | Planning Quality | MCP-Bench, TaskBench | ROUGE on decomposition, Node/Edge F1, chain-order NED |
| T4 | Capability Axes | ARE/Gaia2, TaskBench | 7 axes: execution, search, adaptability, time, ambiguity, agent-to-agent, noise |
| T5 | Cost & Efficiency | MCP-Universe, Gaia2 | $/scenario, step count, latency, budget-scaling curves |
| T6 | Failure Modes | AssetOpsBench | 14 MAST failure modes + emergent clusters, distractor robustness, recovery rate |
| T7 | Integrity & Reproducibility | MCP-Bench | Multi-run variance, prompt-shuffle averaging, validation/test split, judge–human IAA |

### Deployment Extension Tiers (T8–T12)

| Tier | Dimension | Source | Representative Metric |
|------|-----------|--------|----------------------|
| T8 | Deployment Infrastructure | G7 Battery extension | Latency decomposition, MCP-stdio overhead, subprocess-spawn count, cross-domain transfer |
| T9 | Multi-Turn Dialog | G5 Multi-Turn study | Cross-turn artifact reuse, per-turn cost dynamics, context-bloat trade-offs, dialog-level Pass1 |
| T10 | Reasoning Mode | G21 Profiling | Per-phase reasoning cost, per-rubric reasoning sensitivity, adaptive routing P/R |
| T11 | Knowledge Augmentation | G3 Skills+KP | Retrieval recall, multi-hop depth, embedding-index quality, skill-marketplace coverage |
| T12 | Evidence Grounding & Verification | Condition Insight, ARE/Gaia2 | Condition Agreement Rate (CAR), hard/causality/timing violations, Unsupported Claim Rate |

---

## 6. Predictive Validity as Ranking Criterion (Section 4)

### 6.1 The Predictive Validity Score

A composite ranking score combining mean performance with out-of-sample reliability:

```
PV(c) = α·Ȳ_c − β·σ_{Y_c,OOD} − γ·IQR(Y_c)
```

Where:
- Ȳ_c = in-sample mean
- σ_{Y_c,OOD} = cross-OOD-criterion standard deviation of rank position
- IQR(Y_c) = interquartile range of per-scenario scores
- α, β, γ = weights fit on Criterion-A holdouts to maximize Spearman correlation between PV rank and Criterion-B/C ranks

### 6.2 Three Operationalizations of OOD Shift

| Criterion | Shift Type | Description | Interpretation |
|-----------|-----------|-------------|----------------|
| **A: Held-Out Scenarios** | Mild | Stratified random split of benchmark preserving joint distribution | Weakest test; passes uninformative, failures damning |
| **B: Cross-Subset Transfer** | Moderate | Rank on k−1 subsets, test on held-out; 6×6 rank-stability matrix for AssetOpsBench's 6 subsets | Most realistic: "you ranked agents on chillers; will ranking transfer to hydraulic pumps?" |
| **C: Adversarial Perturbation** | Strongest | Four perturbation classes: paraphrase, identifier renaming, time-window shifting, distractor injection | "A configuration that genuinely solved the task should perform equivalently across base and perturbed versions" |

### 6.3 Falsification Conditions (Section 4.3)

For the position to be considered well-supported:

| Condition | Threshold | Current Status |
|-----------|-----------|----------------|
| F1: In-sample vs OOD Spearman ρ | < 0.85 across ≥2 OOD criteria | Partially supported: execution-track ρ=−0.13 (Patel et al., 2026) |
| F2: Top-3 in-sample leave top-5 OOD | ≥10% of holdout splits | Not yet tested |
| F3: Mean-vs-OOD-variance ρ_Pearson | > 0.2 | Not yet tested |
| F4: PV-top-10 vs mean-top-10 Jaccard | < 0.85 | Not yet tested |

The paper commits to publishing the position as refuted if these conditions fail under controlled experiment.

---

## 7. Convergent Architectural Sensitivity (Section 5)

### 7.1 Study Overview

Fourteen parallel implementation studies extending one MCP-based benchmark (AssetOpsBench) along six axes. The headline improvements are summarized in Figure 3 and range from ~1.26× (reasoning-on) to ~3500× (disk cache for predict-only).

### 7.2 Key Findings (Body Cases)

**Case 1 — Reasoning mode (G21, Li et al., 2026c):**
- Reasoning-on raised total latency by 21.5% (15.08s → 18.32s), planning latency by 41.9%
- Clarity improved 31pp (61% → 92%), hallucination dropped 7pp (12% → 5%)
- Data retrieval and agent-sequence correctness: unchanged

**Case 2 — Knowledge augmentation (G3, Li et al., 2026a):**
- RAG: 50–68% rubric accuracy at 8.9–20s end-to-end
- Knowledge Plugin: ~90% at 114–146s with 4.5×–10× token inflation
- Cross-model split: Granite-3-8B reached 60% at 91s on the same pipeline

**Case 3 — Judge-independent governance:**
- Condition Insight: CAR 0.68 → 0.91 under constrained prompting (prompt-level, not backbone-model gain)
- ARE/Gaia2 DAG oracle: 0.99 precision, 0.95 recall against 450 hand-labeled trajectories
- PHMForge: LLM-as-judge Krippendorff α=0.61 vs human-human α∈[0.74, 0.82]

**Case 4 — Substrate underspecification (G30, Feng et al., 2026):**
- Replacing MCP with text-RAG collapsed RUL pass-all-3 from 100% to 20%
- Cross-equipment transfer: 84.1% (bearings) → 42.7% (motors), a 41-point gap
- Operator-style fuzzy queries: 80.6% → 48.6% (McNemar p=0.002)
- Withholding domain tools: 80.8% → 25%

### 7.3 Appendix A: Additional Cases

| Case | Key Finding |
|------|------------|
| Multi-turn artifact reuse (G5) | SS architecture: tool-time 47.3% → 26.3%, planning 0.559 → 0.791, schema-failure rate −68.7%, turns 2–5 ran 4.2× faster than turn 1 |
| QLoRA tool internalization (G20) | AT-F1 0.65 vs 0.47; tokens reduced 82.6%; catastrophic forgetting: Gemma retained 79.8% MCQ, Qwen3 retained 61.3% |
| Confidence-gated routing (G14) | Overall correct 13.0% → 30.4%, hallucination 93.5% → 35.6%, agent-sequence 6.5% → 88.9% at θ=0.8 |
| Asset class — Battery (G7) | 6× end-to-end speedup; 8/11 scenarios at 7.4s vs 44.6s baseline |
| Asset class — Transformer (G8) | 8× speedup; quality preserved (74.2±1.9 vs 73.8±3.0) |
| Temporal semantic cache (G9) | 3.48× overall speedup; F1 ceiling 0.64 due to parameter-collision false positives |
| Visual inspection extension (G23) | AWQ W4A16 + domain calibration: pass 0.48 → 0.82 with 1.99× latency reduction; FP8-KV caused 0/44 response collapse on Qwen |

### 7.4 Five Convergence Patterns (Appendix E)

| Pattern | Description | Teams |
|---------|-------------|-------|
| A: Plan-execute bottleneck localization | Independent teams localize same bottleneck to FMSR or TSFM | G5, G14, G16, G27 |
| B: Prompt-versus-weight tool knowledge | Four groups improve by adding "more thinking" along distinct axes | G3, G14, G20, G21 |
| C: MCP transport overhead | MCP-stdio subprocess overhead as dominant per-call latency floor | G7, G9, G12, G27 |
| D: Caching trustworthiness | Only G9 surfaces parameter-collision F1 ceiling as structural failure mode | G3, G9, G16, G27 |
| E: Scenario authoring as binding constraint | 141-scenario corpus is too small for serious extension work | G7, G8, G12, G30 |

---

## 8. Implications for Leaderboard Design (Section 6)

### Three Proposals

**Proposal 1: Declared configuration columns.** Beyond Model and Pass1, submissions should declare: Architecture, Reasoning Mode, Retrieval Strategy, Prompt-Constraint Level, and Verifier Type. The SmartGridBench study provides direct empirical motivation: in a 2,420-trajectory experiment, MCP standardization adds latency without quality gain, while orchestration changes alone raise pass rate from 43.2% to 55.5%.

**Proposal 2: Layered presentation.** Four layers: (L1) headline PV rank table, (L2) cost-Pareto plot, (L3) drill-down panels per tier, (L4) significance and confidence intervals.

**Proposal 3: Required submission elements.** Multi-run variance, hardware disclosure, declared tier coverage, raw trajectories. Two community artifacts needed: shared rule pipeline for judge-independent verification, adversarial perturbation suite for Criterion C.

### 6.2 Alternative Views

1. **"Aggregate scores are sufficient for model comparison."** The paper's claim is narrower — rankings derived from aggregate scores do not transfer.
2. **"Predictive validity reproduces the problem."** No — predictive validity is reported across three OOD criteria with explicit thresholds and bootstrap CIs.
3. **"HELM and Dynabench already address multi-dimensionality."** They address it for single-shot models; agents introduce trajectory- and orchestration-level axes.

---

## 9. Summary and Outlook (Section 7)

### Field-Level Recommendations

1. **Declare configurations, not just models** — Submission fields for architecture, reasoning mode, retrieval strategy, prompt-constraint level, verifier type
2. **Rank by transfer, not by mean** — Report predictive-validity scores across at least one OOD criterion
3. **Require a judge-independent anchor** — At least one trajectory-level deterministic verifier
4. **Adopt persistent, non-stdio infrastructure** — MCP-stdio overhead conflated with reasoning ability

### Four Forward-Looking Suggestion Clusters (Appendix F)

| Cluster | Recommendation | Supporting Groups |
|---------|---------------|-------------------|
| I | Adaptive and learned routing (meta-router as first-class abstraction) | G3, G9, G14, G16, G21 |
| II | Persistent, non-stdio MCP servers | G7, G9, G27 |
| III | Cross-model and cross-asset generalization | G8, G14, G16, G19 |
| IV | Scenario-corpus expansion beyond 141 scenarios | G8, G12, G20, G30 |

---

## 10. Limitations

1. **Empirical validation is future work** — The position is supported by convergent architectural-sensitivity evidence, not a controlled randomized trial
2. **Domain specificity** — All evidence from industrial asset operations and maintenance (AssetOpsBench); generalization to other MCP-based domains is open
3. **Tier independence asserted, not tested** — Twelve-tier orthogonality is a working hypothesis
4. **Industrial deployment validity gap** — No data linking framework rankings to real deployed-system outcomes (operator override rate, incident reduction, false-alarm rate)
5. **Implementation-study epistemic status** — The fourteen studies are unpublished implementation reports, not peer-reviewed publications

---

## 11. Claim Index

| ID | Claim | Section | Evidence Source |
|----|-------|---------|-----------------|
| C1.1 | Aggregate-score leaderboards collapse orthogonal deployment-relevant dimensions | §2.1 | Pass1=0.75 achievable by qualitatively different configurations |
| C1.2 | Reasoning-on vs reasoning-off differ by 31pp on clarity scoring while overall mean hides it | §2.1 | Li et al., 2026c |
| C1.3 | Plan-Execute vs Supervisor-Specialist differ by 4.2× on turn-2-to-5 latency | §2.1 | Li et al., 2026b |
| C1.4 | Single-pass RAG vs multi-hop retrieval show 50-68% vs ~90% accuracy with 4.5-10× token inflation | §2.1 | Li et al., 2026a |
| C2.1 | LLM-as-judge measurement is reflexive and model-specific | §2.2 | Zheng et al., 2023 |
| C2.2 | CAR moves from 0.68 to 0.91 under constrained prompting — prompt-level gain, not backbone gain | §2.2 | O'Donncha et al., 2026 |
| C2.3 | ARE/Gaia2 DAG oracle achieves 0.99 precision and 0.95 recall | §2.2 | Froger et al., 2025 |
| C2.4 | PHMForge: LLM-as-judge inter-rater reliability α=0.61 vs human α∈[0.74,0.82] | §2.2 | Feng et al., 2026 |
| C3.1 | CODS-2025 execution-track public-hidden Spearman ρ=−0.13 (n=13, p=0.71) | §2.3 | Patel et al., 2026 |
| C3.2 | CODS-2025 planning-track public-hidden Spearman ρ=0.69 (n=20) | §2.3 | Patel et al., 2026 |
| C3.3 | Exgentic cross-benchmark rank correlations span 0.32–0.85 | §2.3 | Bandel et al., 2026 |
| C4.1 | No single prior benchmark reports more than 4-5 of the 12 tiers | §3 | Benchmark×tier coverage matrix (Figure 2) |
| C4.2 | The 12 tiers are non-redundant measurement dimensions | §3 | Consolidated from 7 benchmarks + 14 studies |
| C5.1 | Reasoning-on raises latency 21.5%, clarity +31pp, hallucination −7pp | §5.1 | Li et al., 2026c |
| C5.2 | Knowledge Plugin achieves ~90% accuracy at 114-146s vs RAG 50-68% at 8.9-20s | §5.2 | Li et al., 2026a |
| C5.3 | MCP tool execution → text-RAG collapses RUL pass-all-3 from 100% to 20% | §5.4 | Feng et al., 2026 |
| C5.4 | Cross-equipment transfer drops pass rate from 84.1% to 42.7% | §5.4 | Feng et al., 2026 |
| C5.5 | Frontier LLMs are "stronger at calling tools than at planning when to call them" | §5.4 | Feng et al., 2026 |
| C6.1 | MCP-stdio subprocess overhead is a dominant per-call latency floor identified by 4 independent teams | Appendix E | G7, G9, G12, G27 |
| C6.2 | Scenario-corpus size (141 scenarios) is the binding constraint on extension work | Appendix E | G7, G8, G12, G30 |
| C6.3 | The base architecture is under-designed, not near-optimal (5 convergence patterns) | Appendix E | All 14 studies |

---

## 12. Ethical Considerations

This paper makes no use of human-subjects data, PII, or sensitive deployed-system traces. The implementation studies use publicly released AssetOpsBench data (Apache-2.0) and synthetic or public industrial data (NASA PCOE Li-ion cycling data). The paper flags a potential downside: predictive-validity measurements are more expensive than aggregate scoring and could concentrate evaluation capacity in well-resourced institutions. The recommendation is to maintain reference adversarial-perturbation suites and reference rule pipelines as community artifacts.

---

## 13. Pre-Registered Pilot Design

The proposed pilot study:
- **Sample size**: 80 configurations, 120 scenarios, ~1,200 perturbed observations
- **Statistical power**: 80 paired ranks can distinguish ρ=0.85 vs ρ=0.95 at α=0.01 with power >0.9
- **Decision rule**: If pilot holdout Spearman > 0.95 → revise central claim downward (rankings are stable); if 0.65-0.95 → proceed with full study; if < 0.65 → claim so strongly supported that reduced scope suffices

---

## 14. The Big Picture

This paper is a **position paper grounded in synthesis**, not new controlled experiments. Its central contribution is introducing **predictive validity** as a ranking criterion for LLM agent evaluation, operationalized through three falsifiable OOD criteria and a twelve-tier measurement apparatus. The evidence base is the largest coordinated extension of one agent benchmark to date: fourteen studies, ~6,000 judged trajectories, six extension axes. The paper's value lies in providing a concrete, falsifiable alternative to the aggregate-score paradigm that dominates current leaderboard practice.
