# Re-Centering Humans in LLM Personalization

**Authors:** Lechen Zhang (UIUC), Jiarui Liu (CMU), Tal August (UIUC)  
**arXiv:** 2606.06614 (cs.CL, cs.AI, cs.HC)  
**Code & Data:** [github.com/orange0629/recenter-personalization](https://github.com/orange0629/recenter-personalization)  
**Reading Date:** 2026-06-19

---

## 1. Problem Hook

LLM personalization is a fast-growing area — but evaluations overwhelmingly use **synthetic data** (simulated personas, generated conversations, LLM-as-judge). Nobody knows if these synthetic evaluations reflect how personalization actually works for **real humans**. The paper asks: *How big is the gap? And can we bridge it?*

---

## 2. The Core Thesis

> Progress on LLM personalization requires **re-centering humans** in the evaluation pipeline: (1) grounding data to real human interactions, and (2) judging personalization quality with humans.

The paper systematically reveals that synthetic evaluations **systematically overestimate** model capabilities at **every stage** of personalization, and that lightweight human-annotated interventions can partially close the gap — but the hardest stage (generation quality judgment) remains fundamentally difficult.

---

## 3. Three-Stage Framework

The paper decomposes personalization into a diagnostic pipeline:

| Stage | Task | Human Data Collected |
|-------|------|---------------------|
| **Stage 1** | Extract stable user attributes from conversation history | 5,949 attribute quality judgments |
| **Stage 2** | Select which attributes are relevant to a specific prompt | 11,919 relevance judgments |
| **Stage 3** | Generate a response incorporating relevant attributes that improves over generic | 1,101 response preference judgments |

This decomposition follows prior work (Wang et al., 2023; Zhuang et al., 2024; Shi et al., 2025) showing that **factorized** approaches beat **monolithic** end-to-end ones.

---

## 4. Dataset Construction

**Real data source:** WildChat (Zhao et al., 2024) → 98,334 users → filtered to 16,573 active English users (≥3 conversations, ≥15 turns).

**Synthetic baselines:** CUPID, PrefEval, PersonaLens — three recent personalization benchmarks.

**Attribute extraction:** Llama-3.3-70B extracts attributes per user with confidence scores; clustering merges duplicates; threshold at 0.4 confidence.

**Human annotation:** 3 Prolific annotators per task, selected via pilot studies, Cohen's κ ~0.31–0.43 across tasks.

---

## 5. Models Evaluated

| Model | Type | Size |
|-------|------|------|
| Llama-3.3-70B | Open-weight | 70B |
| Qwen3.5-27B | Open-weight | 27B |
| Gemma-4-31B | Open-weight | 31B |
| Claude-Sonnet-4.6 | Proprietary | — |
| GPT-5.4 | Proprietary | — |

---

## 6. Stage 1 — Key Finding: Attribute Extraction

**Claim C1.1:** Real conversations produce **22% more problematic attributes** (uncertain + rejected) than synthetic ones. (Evidence: Figure 2, 1,983 human-annotated attributes)

**Claim C1.2:** Uniformly sampled real data isn't inherently more diverse than synthetic data — but **filtering + diversity sampling** yields substantially higher diversity (0.737 vs 0.706 best synthetic). (Evidence: Table 4.1)

**Failure modes** in extraction (1,225 uncertain/rejected attributes analyzed via GPT-5.4):

| Failure Mode | % | Example |
|-------------|---|---------|
| Overgeneralization | 53.9% | "User is learning French" from one translation request |
| Missing evidence | 20.3% | Attribute unsupported by visible excerpt |
| Task-context confusion | 16.1% | "User has 5 years marketing experience" from fictional cover-letter prompt |
| Attribute not standalone | 6.0% | Attribute describes immediate task, not user trait |

---

## 7. Stage 1 — Intervention: Attribute Verification

**Intervention:** A lightweight post-extraction verifier that detects problematic attributes.

**RoBERTa verifier** (trained on human annotations): F1 = **0.726** — best among all verifiers, significantly outperforms zero-shot LLMs (best LLM: Claude with optimized prompt at 0.630).

**Key insight:** Optimized prompting improves LLM recall dramatically (e.g., Gemma-4-31B recall: 0.562 → 0.877), but **RoBERTa still wins on F1** by achieving better precision-recall balance.

**Verify-and-refine:** Sending flagged attributes back to the extraction model increases human acceptance from 58% → **>90%** in a small-scale study.

---

## 8. Stage 2 — Key Finding: Relevance Matching

**Claim C2.1:** LLMs and humans **systematically disagree** on which attributes are relevant to a given prompt. (Evidence: Figure 3, 3,969 attribute-prompt pairs, 5 LLMs × 3 humans)

- Human–human agreement: κ = **0.426**
- LLM–LLM agreement: κ = **0.597**
- LLM–human agreement: κ = **0.300**

**Claim C2.2:** LLMs **over-select** 20–40% more attributes as relevant. Humans mark ~20% relevant; LLMs mark 40–60%.

**Claim C2.3:** Relevance selection **cannot be reduced to semantic similarity**. BM25: F1=0.243; embedding similarity: F1=0.384 — both far below LLM judges.

---

## 9. Stage 2 — Intervention: Aligned Relevance Selection

Two training-based approaches:

| Method | Accuracy | Precision | Recall | F1 |
|--------|----------|-----------|--------|----|
| Best zero-shot LLM (Claude) | 0.719 | 0.372 | 0.838 | 0.515 |
| **RoBERTa classifier** | **0.859** | 0.608 | 0.605 | **0.606** |
| Qwen3-4B + **GRPO** | **0.870** | 0.611 | 0.674 | **0.641** |

**Insight:** GRPO-trained model learns to *self-correct*. Example: untrained model marks "user is creative" as relevant to "What's a mode vs scale?" because "creative examples." GRPO model catches itself: *"Wait, this is a factual question — the attribute should not change the answer."*

---

## 10. Stage 3 — Key Finding: Personalization Quality

**Claim C3.1:** **54.6%** of personalized responses are judged **no better than generic** responses by humans. (Evidence: 1,101 preference judgments)

**Claim C3.2:** Open-source models (Qwen3.5, Gemma-4) even **degrade** response quality after personalization. (Evidence: Figure 5)

**Claim C3.3:** LLM judges **systematically inflate** personalization quality scores. (Evidence: Table 6, all LLMs assign higher avg ratings than humans)

| Judge | Avg Rating | Spearman ρ with Human |
|-------|-----------|----------------------|
| Human | 3.176 | — |
| Claude-S4.6 | 3.428 | 0.362 |
| GPT-5.4 | 3.523 | 0.312 |
| Llama-3.3-70B | 4.019 | 0.376 |
| Qwen3.5-27B | 3.487 | 0.182 |
| Gemma-4-31B | 3.409 | 0.111 |

**None reach even ρ=0.4** with human judgments.

---

## 11. Why LLM Judges Fail at Personalization

**Mechanical attribute invocation:** Models explicitly mention user attributes ("Given your interest in X...") without meaningfully adapting content. This impresses LLM judges but feels robotic to humans.

**Generator–judge feedback loop:** Models that explicitly mention attributes more often as generators also **reward** such mentions more as judges (Spearman r = 0.90, p = 0.04). This suggests surface-level personalization tricks transfer from generation to evaluation.

**Claude-S4.6 exception:** Has the lowest explicit mention rate (5%) and is the only judge that significantly *penalizes* explicit mentions — but its penalty is too harsh relative to humans (Δ = -0.39 vs human Δ = 0.03).

---

## 12. Stage 3 — Intervention: Learned Reward Models

Trained reward models (ModernBERT, Qwen2.5-1.5B, Llama-3.2-1B) achieve only **~0.3 Spearman correlation** with human ratings — comparable to the best LLM judges.

**Implication:** Personalization quality judgment is **inherently difficult to model** as a single aggregate objective. The paper suggests future work may need **user-specific or preference-adaptive reward models**.

---

## 13. Limitations

1. **Aggregated annotations** collapse individual variation — personalization is inherently subjective.
2. **English-only** with likely Western cultural norms; personalization norms likely differ across languages/cultures.
3. **Stable attributes only** — doesn't cover memory updates, conflicting attributes, or user control.
4. **Interventions tested within-study only** — generalization to broader populations is unestablished.

---

## 14. Ethical Considerations

- Real user conversations contain sensitive information; systems should not treat inferred attributes as reliable without verification and user control.
- Overgeneralization from limited evidence risks intrusive or presumptuous personalization.
- Annotators exposed to personal content; direct user control over memory and usage is recommended.

---

## 15. Key Contributions

1. **Dataset** of 550 human conversations + 19K+ human judgments across three personalization stages.
2. **Empirical demonstration** that synthetic evaluations overestimate LLM personalization at every stage.
3. **Characterization of failure modes**: overgeneralization (53.9%), over-selection (20–40%), surface-level personalization (54.6% no-better-than-generic).
4. **Lightweight interventions**: RoBERTa verifier (F1=0.726), GRPO relevance alignment (F1=0.641).
5. **Negative result**: Personalization quality reward modeling achieves only modest correlation (ρ≈0.3).

---

## 16. Connections to Related Work

| Work | Connection |
|------|-----------|
| Naous et al. (2026) — synthetic vs real dialogue | Foundation: synthetic responses deviate from human ones |
| Salemi et al., LaMP (2024) — personalization benchmark | Basis for the three-stage decomposition |
| Kim et al., CUPID (2025) | Synthetic persona dataset used as baseline |
| Ouyang et al., RLHF (2022) | Reward modeling approach for Stage 3 |
| Shao et al., GRPO (2024) | Training method used for relevance alignment |

---

## 17. Claim Index

| ID | Claim | Evidence |
|----|-------|----------|
| C1.1 | Real conversations produce 22% more problematic attributes | Figure 2, §4.2 |
| C1.2 | Filtered real data yields higher diversity than synthetic | Table 4.1 |
| C1.3 | Overgeneralization is the dominant failure mode (53.9%) | §4.2, Appendix D |
| C1.4 | RoBERTa verifier achieves best F1 (0.726) for attribute verification | Table 2 |
| C1.5 | Verify-and-refine boosts acceptance from 58% to >90% | §4.3 |
| C2.1 | LLM–human relevance agreement is low (κ=0.300) | Figure 3, §5.2 |
| C2.2 | LLMs over-select 20–40% more attributes as relevant | §5.2 |
| C2.3 | Semantic similarity is insufficient for relevance (BM25 F1=0.243) | Figure 4 |
| C2.4 | GRPO achieves best relevance F1 (0.641) | Table 3 |
| C3.1 | 54.6% of personalized responses no better than generic | §6.2 |
| C3.2 | LLM judges inflate personalization scores | Table 6 |
| C3.3 | Generator–judge explicit mention bias is strongly correlated (r=0.90) | Figure 7 |
| C3.4 | Learned reward models achieve only ρ≈0.3 | §6.3 |
| C3.5 | Claude-S4.6 uniquely penalizes explicit mentions, but over-penalizes | Figure 6 |

---

## 18. Methodological Notes

- **Attribute extraction** uses Llama-3.3-70B with confidence filtering (≥0.4) and agglomerative clustering (threshold 0.7).
- **Relevance matching** uses majority vote of 3 human annotators as ground truth (κ>0.7 with individual annotators).
- **Personalization quality** uses a 5-point Likert preference scale comparing personalized vs generic responses.
- **RoBERTa training:** roberta-base, 10 epochs, batch 16, lr 2e-5, β=2.0 recall-weighting.
- **GRPO training:** Qwen3-4B, 15 epochs, batch 128, lr 1e-6, KL=0.001, n=5 rollouts, 4× A100 80GB.

---

## 19. Key Tables

**Table 1 — Dataset Diversity:** Filtered WildChat (0.737) > PersonaLens (0.706) > PrefEval (0.689) > raw WildChat (0.656) > CUPID (0.649)

**Table 2 — Verifier Performance:** RoBERTa (trained) F1=0.726 beats best LLM Claude+optimized F1=0.630

**Table 3 — Relevance Alignment:** GRPO F1=0.641 > RoBERTa F1=0.606 > Claude (zero-shot) F1=0.515

**Table 6 — Judge Agreement:** Llama highest Spearman (0.376), Gemma worst (0.111), none >0.4

---

## 20. Key Figures

- **Figure 1:** Three-stage personalization pipeline overview.
- **Figure 2:** Attribute annotation distributions — real data has higher uncertainty/rejection.
- **Figure 3:** Pairwise Cohen's κ matrix — human-human > model-human.
- **Figure 4:** Relevance selection F1 — retrieval methods far below LLMs, LLMs still unreliable.
- **Figure 5:** Human ratings by generator — proprietary models barely above neutral, open-source degrades.
- **Figure 6:** Explicit mention sensitivity — LLMs reward explicit mentions, humans don't.
- **Figure 7:** Generator–judge correlation (r=0.90) — surface-level preference transfer.

---

## 21. Data Released

- **50 real users** with multi-session histories (from WildChat)
- **550 conversations** in total
- **5,949** attribute quality judgments (Stage 1)
- **11,919** relevance judgments (Stage 2)
- **1,101** response preference judgments (Stage 3)
- All available at [github.com/orange0629/recenter-personalization](https://github.com/orange0629/recenter-personalization)

---

## 22. Aftertaste

**Strength:** Clean, well-scoped study that systematically demonstrates the gap between synthetic and human evaluation across the entire personalization pipeline. The decomposition into three operational stages makes the diagnosis precise. The GRPO relevance alignment result is especially elegant — the self-correction behavior ("Wait, this is a factual question...") is a compelling demonstration.

**Weakness:** The interventions in Stages 1 and 2 are evaluated on the same data distribution — generalization is unproven. Stage 3's negative result (reward models ρ≈0.3) is stated but not deeply analyzed; the paper doesn't explore *why* it's so hard (e.g., annotation subjectivity vs model limitation).

**Missing piece:** The paper establishes that LLM judges are unreliable, but doesn't propose a practical alternative for automated evaluation at scale beyond small-scale human annotation. The practical path forward for deployment at scale remains unclear.

---

## 23. Follow-up Questions

1. How does the GRPO-trained relevance model generalize to unseen prompts and user types?
2. Can user-specific reward models (rather than a single judge) better capture personalization quality?
3. What happens when the pipeline is tested end-to-end (vs stage-by-stage)?
4. Do the failure patterns hold for non-English languages and non-Western cultures?
5. How do dynamic/updating attributes interact with this static-attribute framework?
