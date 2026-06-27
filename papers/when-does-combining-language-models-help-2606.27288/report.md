# When Does Combining Language Models Help? A Co-Failure Ceiling on Routing, Voting, and Mixture-of-Agents Across 67 Frontier Models

**Authors:** Josef Chen  
**Affiliation:** KAIKAKU  
**arXiv:** 2606.27288  
**Date:** June 26, 2026

---

## 1. Paper Summary

This paper investigates the fundamental limits of multi-model LLM orchestration (routing, voting, cascades, fusion, mixture-of-agents). The central claim is that the pairwise error correlation ρ, which the field uses to decide whether to orchestrate, is blind to the true ceiling: β, the rate at which *every* model fails on the same query. Across 67 frontier models from 21 providers, the paper demonstrates that β caps any selection policy at accuracy ≤ 1 − β, that ρ cannot identify β for m ≥ 3 models, and that the Gaussian-copula model systematically underprices the co-failure tail by ~2.5× on open-ended math tasks.

## 2. Key Contributions

1. **The Orchestration Ceiling (Prop. 1):** No router, vote, or cascade whose output is a member answer can exceed accuracy 1 − β. A Clopper–Pearson bound turns one held-out query set into a $0 pre-deployment certificate on the maximum possible gain.

2. **ρ Cannot See β (Props. 2, 3):** Pairwise error correlation ρ is a sufficient statistic for bivariate error laws but discards the higher-order tail dependence that governs joint failure of large pools. The underpricing ratio β/β<sub>sf</sub> grows with pool size.

3. **Market-Scale Measurement:** On 67 models (GPT-5.5, Claude Opus 4.8, Gemini 3.1 Pro, Grok-4.3, DeepSeek V4, Qwen3.7-Max, Kimi K2.7, etc.), a correctly tetrachoric-calibrated single-factor model still underprices β by ~2.5× on MATH-500. Even the full 67×67 Gaussian copula leaves a 2.25× residual.

4. **Two Regimes Across Domains:** Ceiling-bound (open-ended math: β = 0.052; execution-graded code: β = 0.079) vs. realizability-bound (multiple-choice GPQA: β ≈ 0, oracle gain G = 0.154 is pure resolvable disagreement). The regime is set by answer format, not content.

## 3. Problem Formulation

The paper formalizes orchestration as allocation over a priced, correlated, fast-churning pool:

- **Queries** x carry latent type t = T(x) ∼ D  
- **Pool** M = {1,…,m} of models with quality qᵢ(t) ∈ [0,1] and price cᵢ ≥ 0  
- **Routing policy** π: T → Δ(M) has value V(π) = Eₜ[Σᵢ π(i|t) qᵢ(t)] and cost K(π) = Eₜ[Σᵢ π(i|t) cᵢ]  
- **Objective:** dollars-per-correct [8], or quality subject to a budget

**Economic scaffolding (Appendix A):**
- Budget-constrained routing reduces to a priced assignment with a single shadow price λ_B (Prop. 4)
- Cost-aware fusion has diversification limit k*(ρ, c) that shrinks as ρ rises (Props. 5–7)
- Cascade collapses to random mixing as verifier AUC → ½ (Prop. 8, Cor. 1)

## 4. Experimental Setup

### Pool
- **Pillar experiments:** 15 models across 9 provider families (frontier, mid, cheap)
- **Market-scale:** 67 models across 21 provider families — live OpenRouter catalog
- **Dated snapshots** and prices frozen in the registry (App. C, D)

### Benchmarks
- **Saturated mix:** GSM8K, MMLU, ARC-Challenge, MATH-500  
- **Hard domain:** MMLU-Pro  
- **Market-scale hard:** MATH-500, MATH-Hard Level-5, AIME 2024/2025, GPQA-Diamond  
- **Third domain:** Execution-graded competitive code (Codeforces 1900–3500)  
- **Content control:** GPQA-Diamond in free-response format

### Grading
- Programmatic throughout: exact-match arithmetic, boxed-letter extraction, boxed/integer matching
- No LLM judge used for main experiments (except the content-controlled GPQA open-ended test)
- Answer-anchored grader; corrected from earlier first-letter extractor that mis-scored verbose models

### Cost
- Core pillars: ~$47; market-scale: ~$111; third-domain: ~$110  
- Total reported: ~$270; total account usage including exploration: ~$560  
- Metered via OpenRouter usage endpoint

### Baselines
Single-cheapest, single-best (in-sample selected), random, random-mixing-at-matched-budget, Self-MoA [24], partition-conditioned and per-query oracle, confidence cascade, majority vote, heterogeneous fusion

## 5. Proposition 1: The Orchestration Ceiling and $0 Certificate

**Proposition 1 (Ceiling, gain localization, and a realizability certificate):**

Let β = Pr[all m wrong], a<sub>sb</sub> = max_i q̄_i, and i* = arg max_i q̄_i.

**(i) Ceiling:** Any selection policy — router, vote, or cascade, outputting a member answer — has accuracy ≤ 1 − β, attained by the per-query oracle. Maximum gain over single-best: Δ_ceil = (1 − β) − a<sub>sb</sub>.

**(ii) Gain localization:** G = Vᵒ − a<sub>sb</sub> = Pr[single-best wrong] − β, supported entirely on the resolvable mass (non-unanimous, single-best wrong). The co-failure tail contributes nothing to G.

**(iii) Certificate:** From n i.i.d. queries with K all-wrong, let β_lo(K, n, δ) be the Clopper–Pearson lower limit. With probability ≥ 1 − δ, every selection policy obeys Acc − a<sub>sb</sub> ≤ (1 − β_lo) − a<sub>sb</sub>. This certifies whether orchestration can pay for itself *before* a router is trained.

**Key insight:** A small β does NOT imply orchestration cannot help; it implies a *high* ceiling. The binding quantity is Δ_ceil, small on the frontier only because a<sub>sb</sub> already sits near 1 − β.

## 6. The Co-Failure Tail: Empirical Measurements

### Pillar A Results (15-model pool)

| Quantity | Saturated multi-domain mix | Hard single-domain (MMLU-Pro) |
|---|---|---|
| Single-best | 0.923 (Opus 4.8) | 0.850 (Sonnet 4.6) |
| Oracle (per-query) | 0.967 | 0.970 |
| Oracle gain G (95% CI) | 0.044 [0.027, 0.062] | 0.120 [0.075, 0.155] |
| Mean off-diagonal ρ | 0.464 | 0.382 |
| Within-family ρ | 0.528 | 0.402 |
| Cross-family ρ | 0.459 | 0.380 |

**Confirmed:** G > 0 in both regimes. The realizable routing gain is near zero — a learned TF-IDF+domain router captures ~9% of G (CI spans zero).

### Tail Co-Failure (15-model pool)

| | Saturated mix | Hard (MMLU-Pro) |
|---|---|---|
| All-wrong β (95% CP) | 0.033 [0.019, 0.054] | 0.030 [0.011, 0.064] |
| Mean ρ (Pearson) | 0.464 | 0.382 |
| β predicted by single-factor | 0.0011 | 0.0050 |
| Naive Pearson underpricing | 30× [17, 48] | 6× [2, 13] |
| Implied tail correlation | 0.88 | 0.64 |
| Realizable router gain (fraction of G) | 0.09 (CI spans 0) | < 0 |

## 7. The Large-Pool Co-Failure Phenomenon (Market Scale)

Expanding to **67 models across 21 families** (GPT-5.5, Claude Opus 4.8, Gemini 3.1 Pro, Grok-4.3, GLM-5.2, Qwen3.7-Max, DeepSeek V4, Kimi K2.7, MiniMax M3, down to small open-weights).

### MATH-500 (n=330 fully-covered queries)
- **β = 0.052** (k=17 all-wrong, CP [0.030, 0.081])
- Tetrachoric ρ̄ = 0.78 → β<sub>sf</sub> = 0.021
- **Observed tail is 2.5× fatter** (bootstrap 90% CI 1.7–3.4×)
- Full 67×67 Gaussian copula: β<sub>full-Σ</sub> = 0.023 — empirical 0.052 is **2.25× beyond even the full Gaussian copula**
- Replicated on MATH-Hard: β = 0.044 (k=13, CP [0.023, 0.073]), single-factor underprices 8.3×

### Why the Gaussian Copula Fails
The residual is not single-factor misspecification:
- Full 67×67 tetrachoric matrix Monte Carlo: still 2.25× residual
- Exchangeable Clayton copula (λ<sub>L</sub> = 0.69): β = 0.026 vs empirical 0.052 (1.96× residual)
- **Signature of a common-mode atom** that no pairwise-calibrated copula can represent
- Pool-size effect, not composition: ratio rises monotonically from 1.0 at k=2 to 2.5 at k=67

## 8. Proposition 2: Why Pairwise ρ Underprices Co-Failure

**Proposition 2 (Pairwise ρ underprices co-failure, with bias growing in pool size):**

Model errors by a common-shock mixture: each query is co-hard with probability π (all m models err together) and otherwise each model errs independently with probability α₀.

- Marginal error rate: α = π + (1−π)α₀  
- Pairwise error correlation: ρ̄ > 0  
- True co-failure rate: β(m) = π + (1−π)α₀^m → π > 0  
- Single-factor β<sub>sf</sub>(m) → 0 (Gaussian copula has zero lower tail dependence for ρ̄ < 1)

**(i)** β(m) ↓ π > 0 while β<sub>sf</sub>(m) ↓ 0  
**(ii)** β(m)/β<sub>sf</sub>(m) → ∞, strictly increasing in m, equals 1 at m=2

**Interpretation:** ρ is exact for pairs and increasingly inadequate as the pool grows. The Gaussian copula's zero lower tail dependence is the specific mechanism.

## 9. Proposition 3: Non-Identification of the Co-Failure Floor

**Proposition 3 (Non-identification of the co-failure floor):**

For m ≥ 3, β is not a function of the pairwise error law. There exist joint distributions over {0,1}^m with identical one- and two-dimensional marginals — hence identical marginal error rates and pairwise correlations — yet different β.

**Consequence:** No statistic computed from pairwise correlations, including a single-factor copula, can identify β or the large-pool floor β_∞. A direct estimate of β (with the Prop. 1 certificate), not any function of ρ, is the right instrument.

**Proof sketch for m=3:** Fix p₁ = ½, p₂ = ¼. Both (q₀, q₁, q₂, q₃) = (¼, 0, ¾, 0) and (0, ¾, 0, ¼) reproduce every pairwise marginal yet have β = 0 and β = ¼ respectively.

## 10. The Driver: Common-Mode Atom, Not Tail Dependence

The paper makes a nuanced distinction:
- What pairwise ρ misses is a **common-mode atom**: a positive-probability event of joint failure, β_∞ = lim β(m) > 0
- **Smooth tail dependence** reflected in ρ does not produce the effect
- Simulation: Clayton copula (λ<sub>L</sub> = 0.71) yields 4.0× underpricing at m=53; common-shock mixture with rare shared-failure atom (β_∞ = 0.05) drives ratio past 10⁷×
- The orchestration-relevant object is β_∞, which no single pairwise number can identify

## 11. Execution-Graded Code: Third-Domain Replication

**Setup:** 18 frontier models × 63 Codeforces problems (rating 1900–3500), execution-graded under Python-fair time limit with private + generated stress tests.

**Results:**
- Mean accuracy: 0.45
- **β = 0.079** (k=5, CP [0.026, 0.176])
- Naive Pearson ρ̄ = 0.27 → spurious 17× underpricing
- Tetrachoric ρ̄<sub>tet</sub> = 0.51 → 3.1× underpricing
- Full-Σ Gaussian copula: 1.7× residual
- **Statistical resolution:** bootstrap 90% CI [1.5, 6.2], excluding 1

**Conclusion:** The co-failure signature replicates in a structurally independent open-ended domain. The cross-domain regime is established.

## 12. Format Sets the Regime (Content-Controlled Test)

**GPQA-Diamond content-controlled experiment:**
- Same 79 questions, same models
- Multiple-choice: β ≈ 0 (0/130 co-failure)
- Free-response (options stripped): β = 0.127 (k=10, CP [0.062, 0.220])
- Mean accuracy: 0.66 → 0.51; best model: 0.91 → 0.77
- Graded by 5-judge LLM panel (κ = 0.73–0.92)
- Robust under all judge aggregations (unanimous: β = 0.241; most lenient: β = 0.038)

**Key insight:** Co-failure tracks open-endedness, not subject matter. This is decisive evidence that the open-ended/multiple-choice split is real and not a domain confound.

## 13. Two Regimes Across Domains

| | MATH-500 (math) | Code contests | GPQA-Diamond (science) |
|---|---|---|---|
| Models/queries | 67 / 330 | 18 / 63 | 52 / 130 |
| Single-best | 0.836 | 0.825 | 0.846 |
| Per-query oracle | 0.948 | 0.921 | 1.000 |
| Oracle gain G | 0.112 | 0.096 | 0.154 |
| β | 0.052 (k=17) | 0.079 (k=5) | < 0.03 (0/130) |
| Mean ρ | 0.53 | 0.27 | 0.25 |
| ρ underpricing (tetrachoric) | 2.5× | 3.1× (CI [1.5, 6.2]) | — (β ≈ 0) |
| Regime | **Ceiling-bound** | **Ceiling-bound** | **Realizability-bound** |

**Ceiling-bound (math, code, free-response GPQA):** β > 0 caps every policy; pair-wise ρ underprices the tail. The binding constraint is co-failure.

**Realizability-bound (multiple-choice GPQA, MMLU-Pro):** β ≈ 0, ceiling open. Large oracle gain exists but is pure resolvable disagreement that no deployable router captures.

**Pairwise ρ cannot tell these regimes apart.**

## 14. Pillar B: Naive Diversity Is a Liability; Matched Quality Enables Diversification

### Finding 1: Naive Heterogeneous Fusion Hurts
- All ⁵C₃ = 455 three-model triplets
- Mean vote gain: **negative** (hard: −0.10; saturated: −0.02)
- Robust under model-clustered (leave-one-model-out jackknife) inference
- Positive ρ-slope (+0.13 hard) not significant under clustering

**Conclusion:** Mixing unequal-quality models lets diverse-but-weaker members outvote a strong one. Refutes the "more diverse ⇒ better fusion" intuition — matches Kuncheva & Whitaker [20], Li et al. [24].

### Finding 2: At Matched Quality, Lower ρ Wins
Contrast Self-MoA (ρ = 0.80) vs. heterogeneous fusion (ρ = 0.42), accuracy-matched 6-model band:

- At k=3: low-ρ heterogeneous fusion beats high-ρ Self-MoA
- Across 60 resamplings: average gain +0.027 (positive in all 60)
- The gain shrinks as ρ rises (the direction k*(ρ) predicts)
- Low-correlation MATH-500 regime: +0.020 (not significant)

**Conclusion:** The diversification mechanism is supported in one regime, consistent with the diversification limit's core prediction: lower inter-model error correlation buys larger diversifiable gains at matched quality.

## 15. Pillar C: Cascade Collapse Identity

With L = GPT-5-nano (a<sub>L</sub> = 0.748, 5-sample self-consistency), H = Opus 4.8 (a<sub>H</sub> = 0.921), verifier AUC = 0.899:

- **Collapse identity confirmed:** AUC → ½ ⇒ cascade advantage → 0 (0.121 → 0.012, seed std ≤ 0.005)
- **Volume ceiling:** 1 − a<sub>L</sub>/a<sub>H</sub> = 0.188
- **5-fold held-out:** +0.114 accuracy vs. random-mixing-at-matched-budget (cross-fold sd 0.010)
- At unconstrained optimum, cascade collapses to L corner (matches L on dollars-per-correct)

**Key insight:** Cascade dominance requires both (i) AUC > threshold, and (ii) a positive conditional edge on the deferred tail.

## 16. The Calibration Trap: Pearson vs. Tetrachoric

A critical methodological contribution:

- **Naive Pearson-of-indicators** calibration (treating 0/1 correctness as linear) gives ρ̄ = 0.53 on MATH-500, predicting β<sub>sf</sub> = 0.0016 — a spurious 32× underpricing
- **Tetrachoric** (latent) correlation: ρ̄<sub>tet</sub> = 0.78, predicting β<sub>sf</sub> = 0.021 — a real 2.5× residual
- **Order-of-magnitude difference** is a calibration artifact, not a co-failure effect
- This is "a century-old psychometric point" [30, 32] that the LLM evaluation literature routinely elides

**Bottom line:** Using the wrong correlation transform inflates the reported co-failure gap by an order of magnitude. The correctly calibrated residual is single-digit (≈ 2.5×).

## 17. Economic Scaffolding (Appendix A)

### A.1 Routing as Priced Assignment (Prop. 4)
- Budget-constrained routing: V(B) = min_{λ≥0} {λB + E_t max_i [qᵢ(t) − λcᵢ]}
- Optimal policy: per-type bang-per-buck rule, arg max_i [qᵢ(t) − λ_B cᵢ]
- λ_B: shadow price of the inference dollar

### A.2 Cost-Aware Diversification Limit
- Equal-weight fusion of k equicorrelated models: MSE → ρσ²  
- Cost-aware break-even ensemble size: k*(ρ, c) = ½[−1 + √(1 + 4λσ²(1−ρ)/c)] ~ √(λσ²(1−ρ)/c)
- ∂k*/∂ρ < 0, ∂k*/∂c < 0, ρ → 1 ⇒ k* → 0

### A.3 Cascade Calibration (Prop. 8)
- Cascade advantage = β[w(β) − (1−a<sub>L</sub>)] + β[a<sub>H</sub>(τ) − a<sub>H</sub>]
- Integrated advantage ≥ 0 iff verifier AUC ≥ ½
- β_cas/β_mix → 1 − a<sub>L</sub>/a<sub>H</sub> (price-independent escalation ceiling)

## 18. Optionality Under Churn (Appendix E)

**Secondary finding (observational):** Frontier releases as Poisson process, broad access captures v·max(Γ,0) per arrival.

- Option value of broad access: V_R = v/r · ν/(r+ν) · E_g(μ, η)
- Measured on 2024–2026 timeline: frontier dollars-per-correct dropped ~14–15×
- Capability option value: +0.33 accuracy by 2026 on MMLU-Pro vs. +0.01 on saturated GSM8K

**Corollary 2 (Convergence collapse):** If error correlation rises as models improve, joint orchestration and option value contract.

## 19. Proof Highlights (Appendix B)

### Lemma 1 (Envelope)
V(π) ≤ Vᵒ = E_t maxᵢ qᵢ(t), attained by oracle. G > 0 iff no model is uniformly D-a.e. best.

### Prop. 5 (Variance Floor)
Equal-weight fusion MSE → ρσ². Binary single-factor probit floor: Φ(−Φ⁻¹(1−α)/√ρ).

### Prop. 6 (Diversification Limit)
Marginal variance reduction ∆V(k) = σ²(1−ρ)/[k(k+1)]. Add model iff λ·∆V(k) ≥ c.

### Prop. 8 (Cascade Collapse)
Escalated mass β pays c_H; Q(β) = a_L + β[a_H(τ) − 1 + w(β)]. Against random mixing, advantage = β[w(β) − (1−a_L)], vanishes when AUC = ½.

### Prop. 3 (Non-Identification)
Frêchet class: on {0,1}³ with fixed 1D and 2D marginals, q₃ (triple failure) is free in a 1-parameter family.

## 20. The Market-Scale Model Pool (Appendix D)

The 67-model, 21-family pool spans:
- **Frontier:** GPT-5.5 ($5/$30 per Mtok), Claude Opus 4.8 ($5/$25), Gemini 3.1 Pro ($2/$12)
- **Mid:** Claude Sonnet 4.6, GPT-5.4/5.2/5.1, Qwen3.7-Max ($1.25/$3.75), Kimi K2.7 ($0.74/$3.5), Grok-4.3 ($1.25/$2.5), Mistral-Large ($0.5/$1.5)
- **Cheap:** GPT-5-nano ($0.05/$0.4), Llama-4-Maverick ($0.15/$0.6), DeepSeek V4-Flash ($0.09/$0.18), Gemma-3n ($0.06/$0.12), Granite-4.0 ($0.017/$0.112), Mistral-Small ($0.05/$0.08), Phi-4-mini ($0.08/$0.35)

All chat/instruct only; pure thinking/reasoning variants excluded for clean programmatic grading.

## 21. Reproducibility and Open Science (Appendix C)

- **Full release:** Per-cell outcome matrices, model registry with dated snapshots and live prices
- **Runnable certificate:** `beta_certificate.py` — from K/n and a_sb, returns the Clopper–Pearson-certified $0 bound
- **Full-Σ decomposition:** `residual_decomp.py`, `bootstrap_ratio.py`
- All analysis scripts: `realizability.py`, `cascade.py`, `eqq_robustness.py`, `rho_fusion_test.py`
- Provenance tracked with run identifiers (matrix_stageA2, matrix_hardA, marketE2, etc.)
- References audited with scite Smart Citations

## 22. Limitations

1. **Programmatic grading:** Covers verifiable tasks only; answer-extraction heuristics mildly penalize verbose models
2. **Saturated benchmarks inflate ρ,** mitigated but not removed by the hard regime
3. **Static-price assumptions** in tension with churn; claims restricted to within-release-epoch validity
4. **Equal-quality assumption** load-bearing — naive heterogeneous voting hurts
5. **Unconditional ρ-slope** inference inconclusive under model-clustering
6. **G and block-ρ gap** reported without seed replication
7. **Cascade verifier** scores only cheap model (L); optimal deferral conditions on both models [14]
8. **Code magnitude** rests on k=5 events under a strict-but-not-official judge on 18-model pool
9. **Remaining items for top-venue:** tight-ratio code replication; ≥3 seeds on matched quality; optimal cascade-routing baseline; price-controlled tail-edge experiment

## 23. Discussion: One Allocation Problem on Two Timescales

- **Within epoch (static):** Fixed prices and pool → budget-priced assignment (Prop. 4), capped by realizability ceiling (Prop. 1)
- **Across epochs (dynamic):** Frontier releases → real option on next pool
- **Routing value:** First-moment selection effect scaling with dispersion, not capability
- **Fusion value:** Second-moment effect bounded by systematic error; realized only under accuracy-matched combination
- **Cascade value:** Decision-theoretic effect = integrated AUC lift of verifier
- **All three shrink** as frontier converges and errors correlate (Cor. 2)

**Core empirical signature:** On the 2026 frontier, oracle gains are small and naive fusion is a net liability precisely because today's best models agree — yet once quality is matched, lower error correlation still buys significant gain. The lever is failure-mode heterogeneity, not model count.

## 24. Conclusion: The Takeaway

**For practitioners:**
- Do not use pairwise ρ alone to decide whether to orchestrate — it cannot see the binding constraint
- Measure β directly (all-models-wrong rate) for your workload
- Use the Clopper–Pearson certificate (Prop. 1) as a $0 pre-deployment test: if the certified bound falls below overhead, no router/vote/cascade can pay for itself
- On open-ended tasks, best models increasingly fail alike — the lever is failure-mode dispersion and market churn, not peak capability or model count

**Two regimes:**
- **Open-ended tasks (β > 0):** Ceiling-bound. The gap is small and β constrains everything
- **Multiple-choice/verifiable (β ≈ 0):** Realizability-bound. The gap is resolvable disagreement no router yet captures

**The open question:** Whether this holds on open-ended generative tasks beyond verifiable benchmarks.

## 25. Future Work (Explicit)

1. **Tight-ratio code replication** at 67-model scale with official hidden-test judge
2. **≥3 seeds and held-out model selection** on the matched-quality result
3. **Extension across multiple ρ levels** to fit sensitivity λ and predict k* out-of-sample
4. **Optimal cascade-routing baseline** from Dekoninck et al. [3]
5. **Price-controlled tail-edge experiment**
6. **Human-calibrated judge** on the full 130 GPQA open-ended questions
7. **Open-ended generative tasks** beyond verifiable benchmarks

---

*This report is based on arXiv:2606.27288v1, "When Does Combining Language Models Help? A Co-Failure Ceiling on Routing, Voting, and Mixture-of-Agents Across 67 Frontier Models" by Josef Chen (KAIKAKU), June 2026.*
