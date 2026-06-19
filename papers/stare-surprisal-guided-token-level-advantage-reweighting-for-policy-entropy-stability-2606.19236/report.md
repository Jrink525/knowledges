# STARE: Surprisal-Guided Token-Level Advantage Reweighting for Policy Entropy Stability

**arXiv:** 2606.19236 (cs.LG, cs.AI, cs.CL)  
**Published:** 17 Jun 2026  
**Authors:** Haipeng Luo, Qingfeng Sun, Songli Wu, Can Xu, Wenfeng Deng, Han Hu, Yansong Tang  
**Affiliations:** Tsinghua University (Shenzhen International Graduate School) & Tencent Hunyuan  
**Code:** https://github.com/hp-luo/STARE  
**Read by:** subagent (deep-read)

---

## 1. Problem Statement

Reinforcement Learning with Verifiable Rewards (RLVR) — exemplified by GRPO (Group Relative Policy Optimization) — has become the dominant post-training paradigm for eliciting complex reasoning in LLMs (DeepSeek-R1, Qwen3, Kimi K1.5). However, **GRPO-style algorithms suffer from policy entropy collapse during extended training:** entropy decays rapidly, output diversity vanishes, the policy converges prematurely, within-group rollouts homogenize, degrading relative advantage estimation and ultimately capping trainable steps. This is a critical bottleneck for long-horizon post-training.

**Two open questions:** (1) Which tokens drive entropy decay under GRPO? (2) How strong an intervention suffices to reverse it?

---

## 2. Prior Work & Limitations

Existing mitigations fall into three categories:

| Approach | Method | Limitation |
|----------|--------|-----------|
| **Clipping adjustment** | DAPO's clip-higher protects low-probability tokens | Asymmetric, uncontrollable effect; inactive in on-policy regime (ratios ≈ 1) |
| **Trajectory-level weighting** | Upweight rare correct / negative rollouts | Coarse-grained, operate at trajectory granularity |
| **Entropy-aware reshaping** | Couple entropy into advantage | Over-amplifies high-entropy tokens, induces oscillations, hyperparameter-sensitive |

**Gap:** All prior work operates at trajectory or sample granularity, lacking a principled account of the collapse mechanism at the token level. STARE provides the first token-level theoretical analysis.

---

## 3. Core Theoretical Analysis

### 3.1 First-Order Gradient Analysis of Token-Level Entropy

The paper derives a **token-level entropy variation** decomposition. For a sampled token `a` with probability `p = π(a|c)` and surprisal `𝔰_a = -ln p`:

Define:
- **Entropy sensitivity function:** `Φ(p) = p(ln p + H) - S₂` where `S₂ = Σ_v π_v²(ln π_v + H)`
- `Φ` measures the signed excess of the sampled token's probability-weighted surprisal deviation over the distributional baseline `S₂`

**Theorem 3.1 (Token-level entropy variation):** In the unclipped GRPO regime, the per-step per-token change to the position-level entropy is:

`dH/dt ∝ Â · Φ(p)`

This is the **key decomposition:** the trajectory-level advantage `Â` (shared across all tokens in a rollout) multiplies the local entropy sensitivity `Φ(p)`.

### 3.2 Advantage-Surprisal Four-Quadrant Decomposition

**Proposition 3.2:** There exists a **unique critical surprisal threshold** `𝔰*` such that:
- `Φ(p) > 0` when `𝔰 > 𝔰*` (entropy-increasing)
- `Φ(p) < 0` when `𝔰 < 𝔰*` (entropy-decreasing)

This yields a 2×2 matrix:

| | **Low Surprisal** (𝔰 < 𝔰*) | **High Surprisal** (𝔰 > 𝔰*) |
|---|---|---|
| **Positive Advantage** (Â > 0) | **U⁺**: entropy-decreasing | **L⁺**: entropy-increasing |
| **Negative Advantage** (Â < 0) | **U⁻**: entropy-increasing | **L⁻**: entropy-decreasing |

The **critical insight:** Within positive-advantage trajectories, low-surprisal tokens dominate sampling frequency → they drive most entropy-decreasing updates (U⁺ quadrant dominates). The rare high-surprisal tokens (L⁺) that could raise entropy are diluted by sheer count. A mirror-image asymmetry holds for negative-advantage trajectories.

### 3.3 Near-Criticality Property

**Theorem 3.4 (Entropy Neutrality Identity):** `E_a~π[Φ(a)] = 0` — the expectation of Φ over the sampling distribution is zero.

Under token-level reweighting (scaling L⁺ tokens by W ≥ 1):

**Proposition 3.5:** The batch entropy gradient becomes:
`dH̄/dη|_W = -(1/N)[Λ - (W-1)Γ]`

Where Λ is the residual from advantage-surprisal correlation, and Γ aggregates positive contributions from L⁺ tokens.

**Corollary 3.6 (Near-Criticality):** When sequence length T and batch size are large, `W* - 1 = Λ/Γ = O(T⁻¹)`. This means:
- A **mild weight perturbation** (W slightly > 1) suffices to flip entropy from decreasing to increasing
- Beyond the critical threshold, W controls **magnitude, not direction**
- The specific value of W is **robust** — wide operating range before divergence

### 3.4 Cross-Step Dynamics

Without intervention (W=1): Λ > 0 in expectation → entropy decreases → distribution concentrates → high-surprisal tokens further diluted → self-reinforcing entropy collapse loop.

With W > W*: entropy increases → distribution disperses → high-surprisal tokens sampled more → Γ grows → critical weight W* drops → symmetric recovery loop.

---

## 4. STARE Method

### 4.1 Entropy-Critical Token Partitioning

Select tokens via **batch-internal top-P% surprisal quantile** (proxy for theoretical 𝔰* threshold). Validated to achieve ~95% agreement with theoretical threshold by end of training.

Defines four token sets:
- `L_q⁺`: high-surprisal, positive-advantage (entropy-increasing, diluted)
- `L_q⁻`: high-surprisal, negative-advantage (entropy-decreasing, diluted)
- `U_q⁺`: low-surprisal, positive-advantage (entropy-decreasing, dominant)
- `U_q⁻`: low-surprisal, negative-advantage (entropy-increasing, dominant)

### 4.2 Advantage-Conditioned Token-Level Credit Rebalancing

**Single-polarity operations (default: O1 = amplify L_q⁺):**
- **O1:** Amplify effective advantage of L_q⁺ → strengthens entropy-increasing signal
- **O2:** Amplify effective advantage of U_q⁻ → strengthens entropy-increasing signal
- **O3:** Attenuate effective advantage of U_q⁺ → weakens entropy-decreasing signal
- **O4:** Attenuate effective advantage of L_q⁻ → weakens entropy-decreasing signal

**Combined operations (C2 best dual variant):**
- **C1:** Amplify L_q⁺ + Amplify U_q⁻
- **C2:** Amplify L_q⁺ + Attenuate L_q⁻ (dual-sided regulation)

**Default:** STARE-O1 (amplify L_q⁺ by factor W)  
**Variant:** STARE-C2 (amplify L_q⁺ + attenuate L_q⁻)

### 4.3 Target-Entropy Closed-Loop Gate

Control mechanism: activate reweighting when batch-averaged entropy `H̄_k < H_tgt` (entropy too low → need more exploration), revert to standard GRPO once entropy recovers.

This yields **closed-loop, stable, low-intrusion regulation** — the gate engages only when needed, minimizing deviation from standard GRPO.

### 4.4 Weighting Schedules

- **Static:** Fixed W (default: 1.05–1.5)
- **Adaptive:** Dynamically adjust W based on current entropy gap
- Target-entropy gating substantially reduces sensitivity to specific W values

---

## 5. Experimental Setup

| Dimension | Details |
|-----------|---------|
| **Models** | 1.5B (DeepSeek-R1-Distill-Qwen), 7B (Qwen2.5-Math), 8B (Qwen3), 14B (Qwen2.5-Instruct), 32B (Qwen2.5-Base) |
| **Task Families** | Short CoT, Long CoT, Multi-Turn Tool Use |
| **Baselines** | GRPO-ds, DAPO, EAPO (8B), STAPO (8B), STEER (7B), JustRL (1.5B), SimpleTIR (7B) |
| **RL Steps** | 5000 (7B), 1500+ (14B/32B) |
| **Benchmarks** | AIME24, AIME25, MATH-500, Minerva Math, OlympiadBench, GPQA |

---

## 6. Main Results

### 6.1 Performance Gains

**Short CoT (Qwen2.5-Math-7B → STARE-O1):**
- Average accuracy: **54.4%** (vs STEER 49.1%, GRPO-ds 49.1%)
- AIME24: **44.2%** (vs DAPO ~34%) — ~10% improvement
- AIME25: **23.8%** (vs DAPO ~17%) — ~7% improvement

**Short CoT (14B):** STARE-O1 52.0% vs GRPO-ds 46.1% (+5.9%)
**Short CoT (32B):** STARE-O1 60.7% vs GRPO-ds 56.1% (+4.6%)

**Long CoT (1.5B):** STARE-O1 65.9% vs EAPO 57.0% (+8.9%), DAPO 55.1% (+10.8%)
**Long CoT (8B):** STARE-O1 62.0% vs STAPO 58.8%, GRPO-ds 59.0%
**Tool-Use (7B):** STARE-O1 59.4% vs GRPO-ds 53.9% (+5.5%)

**Key pattern: 4–8% improvement on AIME24/25 across all settings, 3–6% across all 6 benchmarks.**

### 6.2 Entropy Stability

- GRPO-ds: entropy collapses toward zero by step 1000, performance plateaus
- STARE: entropy held within target band (H_tgt ≈ 0.3) throughout 5000+ steps, accuracy continues rising
- Pass@32 for STARE consistently exceeds GRPO-ds, indicating preserved output diversity

### 6.3 Ablation Insights

| Finding | Detail |
|---------|--------|
| **Near-criticality validated** | W=1.01 already mitigates decay; W≥1.05 yields steady growth; W≥2.0 triggers divergence |
| **Closed-loop gate essential** | Open-loop forces exceed target entropy (over-exploration); closed-loop keeps in target band |
| **Broad operating range** | P ∈ [5%, 20%] all maintain target band; P=40% still prevents collapse |
| **Token selection valid** | ~95% of top-surprisal tokens fall in theoretical entropy-increasing region by end of training |
| **Dual-side better** | C2 (amplify L⁺ + attenuate L⁻) further improves over O1 alone in some settings |

### 6.4 Cognitive Analysis

Inspecting tokens selected for advantage amplification reveals **reflection and self-correction vocabulary:** "should be", "but", "instead", "verification". STARE activates rare forking tokens with exploratory semantics, driving deeper reasoning and sustained response-length growth.

---

## 7. Strengths

1. **Principled theoretical foundation:** First token-level gradient analysis of entropy dynamics in GRPO; the four-quadrant decomposition and near-criticality property are elegant and actionable.
2. **Minimally invasive:** STARE modifies only the effective advantage weights for a small subset of tokens, with a closed-loop gate that disengages when entropy is healthy — minimal deviation from standard GRPO.
3. **Robust across scale:** Works from 1.5B to 32B without per-scale hyperparameter tuning (robust W and P ranges).
4. **Solves a real bottleneck:** Entropy collapse is a well-known issue limiting long-horizon RL post-training; STARE provides a clean solution enabling 5k+ stable steps.
5. **Comprehensive evaluation:** Three task families, multiple baselines (3-6 per setting), thorough ablations (8 STARE variants), cognitive analysis.

---

## 8. Weaknesses & Limitations

1. **Unclipped regime analysis:** The theoretical analysis assumes the unclipped GRPO regime (ρ ≈ 1). In practice, clipping matters for off-policy updates; the paper validates off-policy in Appendix B.10 but the theory does not cover clipped dynamics.
2. **Designed for GRPO only:** The analysis is specific to GRPO's shared group-normalized advantages. Does not apply to PPO (which has learned value functions) or REINFORCE-style methods without group normalization.
3. **One more hyperparameter:** While robust, STARE still introduces W and P hyperparameters (mitigated by closed-loop gate, but still present).
4. **Computational overhead:** Computing per-token surprisal quantiles across the batch requires additional sorting/comparison; not analyzed for latency impact.
5. **H_tgt selection:** The target entropy threshold is a manual hyperparameter; no principled method for setting it across tasks.
6. **Limited to RLVR domain:** Only evaluated on math/code reasoning benchmarks; general NL tasks (summarization, dialogue) not explored.
7. **Selection proxy relies on quantile:** While validated to match theory, the quantile proxy could fail in edge cases (e.g., bimodal surprisal distributions).
8. **Over-exploration risk poorly bounded:** The paper notes over-exploration with open-loop but doesn't provide formal guarantees for closed-loop stability.

---

## 9. Open Questions & Future Directions

1. Can the target-entropy threshold H_tgt be predicted from pre-trained model statistics?
2. Does STARE generalize to PPO (with learned value function advantages)?
3. How does token-level reweighting interact with KL penalties or other regularizers?
4. Can the surprisal quantile proxy be replaced by a learned gating network?
5. What is the scaling behavior of STARE at 70B+ model scales?
6. Does STARE work for continuous action spaces (non-autoregressive RL)?

---

## 10. Key Figures

- **Figure 1:** Training entropy / AIME24 / AIME25 for STARE vs GRPO-ds on Qwen2.5-7B-Base (tool-use) — STARE maintains entropy, performance keeps rising vs GRPO collapse.
- **Figure 3:** Comprehensive training metrics over 5k steps — entropy, reward, full-solve ratio, response length, AIME24/25 accuracy, Pass@32.
- **Figure 4:** Ablation on W, target-entropy gating, and selection ratio P.
- **Figure 9:** All 8 STARE variant entropy curves vs GRPO-ds.
- **Figure 10:** Word cloud of selected tokens — reflection/self-correction vocabulary.
- **Figures 5-8:** Cross-scale/cross-scenario generalization (14B, 32B, 1.5B-LongCoT, 8B-LongCoT).

---

## 11. Related Work Map

| Direction | Key Papers | How STARE Differs |
|-----------|-----------|-------------------|
| GRPO variants | DAPO, EAPO, STAPO, STEER | Token-level vs trajectory-level intervention |
| Entropy regularization | Cheng et al., Cui et al., Xu et al. | Principled analysis instead of heuristic regularization |
| Exploration in LLM RL | JustRL, SimpleTIR | Token-level credit assignment vs sample-level |
| Surprisal/entropy in NLP | Shannon, Oh et al., Zeng et al. | Applied to RL gradient dynamics for the first time |
| Reflection/self-correction | Wang et al. (forking tokens) | STARE's token selection naturally activates these |

---

## 12. Verdict

**Rating:** 4.5/5 — Strong theoretical contribution, well-executed experiments across scales, practical impact.

STARE is likely to become a standard component in GRPO-based RLVR training pipelines, much like clip-higher from DAPO. The theoretical framework (four-quadrant decomposition, near-criticality) stands as a valuable contribution regardless of the specific method.
