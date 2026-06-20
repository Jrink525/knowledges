# LegalHalluLens: Typed Hallucination Auditing and Calibrated Multi-Agent Debate for Trustworthy Legal AI

**Authors:** Lalit Yadav, Akshaj Gurugubelli  
**Published at:** Second Workshop on Agents in the Wild (AIWILD) at ICML 2026  
**arXiv:** 2606.18021v1 [cs.AI], 16 Jun 2026  
**Code:** https://github.com/lalitdv9/LegalHallulens  

---

## 1. Problem Statement

Legal AI systems are being deployed in high-stakes workflows — contract review, compliance monitoring, regulatory reporting, and due diligence — where errors carry asymmetric costs that aggregate metrics cannot capture. Current practice reports a single hallucination rate (e.g., ~52%), but this average conceals *where* errors concentrate, *in which direction* they run, and whether different systems with identical aggregate rates pose fundamentally different legal risks. A compliance officer comparing models on aggregate hallucination rate has no actionable signal for deployment decisions.

## 2. Motivation

Legal AI errors are asymmetric in who bears the cost. A liability cap invented by a model creates a false risk ceiling that may be relied on for months. A non-compete scope qualifier silently dropped may produce an unenforceable clause that counsel never flags. Trustworthy deployment requires knowing not just *that* a system hallucinates at 52%, but *which clauses*, in *which direction*, and whether a calibrated intervention can shift that profile at reasonable cost. The paper argues that aggregate hallucination rates, the standard reporting practice today, cannot serve this role: averaging across claim types conceals exactly the failure modes that determine legal exposure.

## 3. Research Questions

The paper addresses three research questions:

- **RQ1 (Typed Failure Ordering):** Do LLMs exhibit systematically different hallucination rates across legal claim types, and is this pattern consistent enough across architectures to function as a reliable evaluation signal?
- **RQ2 (Error Direction):** Can the directional character of content errors — whether a model suppresses obligations present in the source or asserts ones that are not — be captured in a single deployment-actionable metric?
- **RQ3 (Typed Mitigation):** Does a debate pipeline calibrated to both failure magnitudes and error directions produce gains concentrated on the highest-failure categories, and can it enable a small open model to match commercial APIs at lower cost?

## 4. Background: Verification Structure of Contract Text

Commercial contracts contain claims of fundamentally different verification character:

- **Numeric claims** (e.g., "cap on liability is $5,000,000") — single numeric value, decidable by direct comparison
- **Temporal claims** (e.g., "agreement terminates on December 31, 2024") — verbatim string comparison
- **Obligation/Entitlement claims** (e.g., "the supplier shall, except as provided in Section 4.2, indemnify…") — multiple semantic elements (modal verb, carve-out, scope, temporal anchor) that must all be preserved
- **Factual claims** (e.g., governing law, counterparty name) — short but structurally simple, relying on the model resisting parametric priors

## 5. LegalHalluLens Framework Overview

The framework has three components:

1. **Typed Hallucination Profiles** — stratified hallucination rates across four legally-motivated claim categories
2. **Risk Direction Index (RDI)** — a signed scalar reducing omission-versus-invention bias to a deployment-comparable metric
3. **Typed Debate Pipeline** — a six-role multi-agent debate calibrated to both magnitudes and directions

## 6. Method: Typed Hallucination Profiles (Section 4.1)

For a model *M* evaluated on corpus *D*, all clause-level outputs are partitioned by claim category *cᵢ ∈ {numeric, temporal, obligation, factual}* and *Hal<sub>TP</sub>(M, cᵢ)* is reported per category. The *within-model typed gap* is defined as:

**Gap(M) = max<sub>cᵢ</sub> Hal<sub>TP</sub>(M, cᵢ) − min<sub>cᵢ</sub> Hal<sub>TP</sub>(M, cᵢ)**

A large gap means Hallucination rates vary substantially across categories — aggregate *Hal<sub>TP</sub>* averages claim types whose deployment consequences differ.

## 7. Method: Risk Direction Index (Section 4.2)

The judge returns a `mismatch_type` label from a fixed inventory. Two labels carry directional meaning:
- `missing_condition` — model omits a qualifier present in ground truth
- `extra_condition` — model asserts a qualifier absent from the source

**RDI(M) = (p<sub>extra</sub>(M) − p<sub>missing</sub>(M)) / 100**

where p<sub>extra</sub> and p<sub>missing</sub> are percentages of contradicted findings carrying each label. Positive values indicate invention-heavy failure (overstates); negative values indicate omission-heavy failure (understates). RDI is a *directional signal* rather than a cardinal measure of risk magnitude — scope errors account for 62–71% of contradictions and compress the directional component.

## 8. Method: Typed Debate Pipeline (Section 4.3)

The pipeline operates on a baseline clause extraction with six agent roles:

| Role | Function |
|------|----------|
| **Skeptic** | Issues typed challenge questions targeting failure modes measured in the diagnosis |
| **Supporter** | Defends the extraction using only verbatim contract quotes |
| **Re-extractor** | Re-runs extraction from source when structural error identified |
| **Arbiter** | Resolves deadlock when agents disagree after all rounds; conservative policy preserving baseline |
| **Verifier** | Searches contract independently and checks definition fit |
| **Judge** | Reads full debate transcript for binding content decisions, subject to asymmetric structural gates |

**Three distinguishing design choices:**

1. **Typed Skeptic challenges** — category-specific questions (numeric → verbatim check; obligation → modal verb & carve-out preservation; temporal → explicit vs. inferred; factual → document vs. external knowledge)
2. **Re-extract node** — when structural extraction error is flagged, re-run rather than debate an unfixable answer
3. **Asymmetric structural gates** — Addition gate (absent→present) requires both Verifier confirmation and debate consensus; Deletion gate (present→absent) blocked when Verifier confirms presence

## 9. Dataset and Oracle (Section 5.1)

**CUAD v1.0** (Hendrycks et al., 2021): 510 commercial contracts with 41 expert-annotated clause types. Provides a complete ground-truth oracle — every model output verifiable against contract text alone, no external knowledge.

The 41 clause types are mapped to four categories:

| Category | *n* | Primary Verification Challenge |
|----------|-----|-------------------------------|
| Numeric | 5 | Threshold fabrication, unit mismatch |
| Temporal | 6 | Implied deadline inference |
| Obligation/Entitlement | 27 | Modal drift, condition loss |
| Factual | 3 | Outside-knowledge injection |

*Note:* Factual and Numeric categories have small *n*; the central typed-gap claim rests on the Obligation (n=27) vs. Temporal (n=6) contrast.

## 10. Models Evaluated (Section 5.2)

**Experiment 1 (Typed profiles benchmark):** Four models at temperature=0:
- gemini-3-flash (commercial API)
- gpt-5.2 (commercial API)
- qwen3-32b (open, 32.8B parameters)
- llama-3.3-70b (open, 70B parameters)

**Experiment 2 (Typed debate mitigation):** 
- Backbone: gemma-4-26B-A4B (Mixture-of-Experts, 4B active parameters)
- Selected as worst baseline composite score on the matched subset

## 11. External Evaluation Judge (Section 5.3)

A single external evaluation judge (gemini-2.5-flash, temperature=0) scores each extracted clause against CUAD ground truth under a strict five-criterion rubric: exact numeric precision, temporal precision, modality match, polarity match, and exception/carve-out preservation. The judge returns a *supported* / *contradicted* verdict and a `mismatch_type` label. The same judge is used for both experiments.

## 12. Experimental Scale (Section 5.4)

**Experiment 1:** Three independent runs per model on all 510 contracts. Nominal: 510 × 41 × 3 = 62,730 per model. Actual totals: 62,580 (gemini-3-flash), 62,689 (gpt-5.2), 61,536 (qwen3-32b), 62,447 (llama-3.3-70b) = **249,252 clause-level instances total**. Missing 0.2–1.9% is contract-correlated (5 contracts fail across all qwen3-32b runs).

**Experiment 2:** 120-contract matched subset (4,920 nominal opportunities) for baseline-vs-debate comparison.

## 13. Results: Aggregate Rates Cannot Support Deployment Decisions

**Table 1:** Aggregate metrics on full 510-contract benchmark.

| Model | FAR | FRR | Acc | Hal<sub>TP</sub> | Hal<sub>Gen</sub> | JEq |
|-------|-----|-----|-----|----------|-----------|-----|
| gemini-3-flash | 19.1 | 4.5 | 85.6 | 50.9 | 65.5 | 46.9 |
| gpt-5.2 | 11.8 | 11.6 | 88.3 | 51.8 | 62.4 | 42.6 |
| qwen3-32b | 13.4 | 10.8 | 87.5 | 52.1 | 63.6 | 42.7 |
| llama-3.3-70b | 7.7 | 18.0 | 89.0 | 56.5 | 63.7 | 35.7 |

Four architecturally distinct models fall within a **6 pp Hal<sub>TP</sub> band (50.9–56.5%)** — too narrow to support deployment decisions.

## 14. Results: The Typed Failure Ordering Is Consistent and Large

**Table 2:** Typed hallucination profiles (Hal<sub>TP</sub> %).

| Model | Numeric | Obligation | Factual | Temporal | Gap |
|-------|---------|------------|---------|----------|-----|
| gemini-3-flash | 67.5 | 67.3 | 36.0 | 29.5 | 38.0 |
| gpt-5.2 | 70.3 | 64.8 | 44.3 | 29.7 | 40.6 |
| qwen3-32b | 66.8 | 69.1 | 39.3 | 29.0 | 40.1 |
| llama-3.3-70b | 74.3 | 73.6 | 46.9 | 35.1 | 39.2 |

**Key finding:** The failure ordering **{numeric, obligation} ≫ factual ≥ temporal** holds for every model without exception. The within-model gap spans **38–41 pp**, completely concealed under aggregate reporting.

Obligation clauses genuinely carry more that can go wrong (modal verbs, trigger conditions, carve-outs, scope qualifiers). Numeric claims fail despite explicit NOTE blocks in extraction prompts specifying exclusions — pretraining priors about common threshold values ("liability caps are usually $5M or $10M") override explicit instructions.

## 15. Results: The Compliance Direction Problem (Section 6.3)

Two systems with matched ~52% aggregate Hal<sub>TP</sub> carry **opposite directional profiles**:

| Model | Hal<sub>TP</sub> | RDI [95% CI] | Direction |
|-------|----------|--------------|-----------|
| gpt-5.2 | 51.8 | **+0.161** [+0.151,+0.170] | Inverts (overstates) |
| qwen3-32b | 52.1 | **−0.202** [−0.212,−0.193] | Omits most (understates) |
| gemini-3-flash | 50.9 | −0.024 [−0.035,−0.015] | Near-balanced |
| llama-3.3-70b | 56.5 | −0.190 [−0.198,−0.180] | Omits (understates) |

Scope errors dominate universally (62–71% of contradictions), compressing the directional component. Despite this, RDI cleanly separates gpt-5.2 (invention-heavy) from qwen3-32b (omission-heavy). In compliance workflows where missed obligations create liability, gpt-5.2's positive RDI is safer (errors are visible additions). In legal-operations settings where false positives consume review capacity, the ordering reverses.

## 16. Results: Calibrated Mitigation (Experiment 2)

**Table 4:** Matched-subset comparison (120 contracts).

| # | Model | FAR | FRR | Acc | Hal<sub>Gen</sub> | JEq | Score |
|---|-------|-----|-----|-----|-----------|-----|-------|
| 1 | **gemma-debate** | 8.4 | 14.4 | 89.7 | 58.6 | 43.3 | **2.4** |
| 2 | gpt-5.2 | 10.7 | 12.0 | 88.9 | 61.0 | 43.7 | 2.6 |
| 3 | qwen3-32b | 14.9 | 10.6 | 86.5 | 64.6 | 43.4 | 3.4 |
| 4 | llama-3.3-70b | 7.6 | 17.9 | 89.2 | 63.4 | 36.3 | 3.6 |
| 5 | gemini-3-flash | 19.1 | 4.5 | 85.4 | 66.2 | 46.8 | 3.8 |
| 6 | gemma-base | 15.4 | 15.8 | 84.5 | 64.8 | 41.8 | 5.2 |

**Key results:**
- Typed debate moves gemma-4-26B-A4B from **last place (Score 5.2) to first (Score 2.4)**
- **Rank 1 under 4 of 5 weighting schemes** (gpt-5.2 leads under recall-heavy weighting)
- **Fabricated detections reduced by 45%** (524 → 287)
- Content contradictions moved only 642 → 641 (−0.2%), confirming the pipeline filters fabrications rather than correcting content

## 17. Per-Type Gains Track the Diagnosis

The per-category ΔFAR ordering, predicted from Experiment 1's typed profiles:
- Obligation: ΔFAR = −8.2 (largest gain)
- Factual: ΔFAR = −5.8
- Numeric: ΔFAR = −3.6
- Temporal: ΔFAR = −2.4 (smallest — lowest baseline)

The ordering was specified *in advance* before running the mitigation, providing evidence that the typed diagnosis is genuinely informative.

## 18. Direction Correction (RDI Shift)

Obligation RDI for gemma-4-26B-A4B shifted from **−0.078 (omission-heavy) to −0.014 (near-balanced)** after debate. Skeptic challenges targeting missing conditions and dropped carve-outs — the omission bias identified in Experiment 1 — produced this intended correction.

## 19. Related Work Comparison

| Prior Work | Contribution | Gap Addressed by LegalHalluLens |
|------------|-------------|-------------------------------|
| Dahl et al. (2024) | Legal hallucination typology (58–88% rates) | Does not address contract extraction or collapse direction into a scalar |
| Hou et al. (2024) | Fine-grained taxonomy of gap categories | Same gap — no deployment-comparable directional scalar |
| Magesh et al. (2025) | RAG doesn't eliminate hallucinations | Starting premise, no typed mitigation proposed |
| Du et al. (2024), Hu et al. (2025) | Multi-agent debate for factuality | Generic Skeptic tuning — not calibrated to per-failure-mode diagnostics |
| FActScore, HaluBench, HalluLens, PHANTOM | Factual precision measurement | No claim-type stratification |

## 20. Key Metrics and Notation

| Metric | Definition | What It Measures |
|--------|-----------|-----------------|
| FAR | FP / (FP + TN) | False acceptance — invents absent clauses |
| FRR | FN / (FN + TP) | False rejection — misses present clauses |
| Acc | (TP + TN) / N | Detection accuracy |
| Hal<sub>TP</sub> | contradicted / TP | Content quality among detections (Experiment 1) |
| Hal<sub>Gen</sub> | (contradicted + FP) / (TP + FP) | Quality of all generated outputs (Experiment 2) |
| JEq | supported / (TP + FN) | End-to-end correctness |
| RDI | (p<sub>extra</sub> − p<sub>missing</sub>) / 100 | Directional bias (positive = invents, negative = omits) |

## 21. Critical Analysis

### Strengths

1. **Large-scale empirical foundation** — 249,252 clause-level instances across 4 architecturally diverse models provide statistical robustness.
2. **Consistent typed gap** — The ~40 pp gap between obligation/numeric and temporal claims holds across all models, strongly supporting the claim that aggregate reporting is insufficient.
3. **Practical, actionable contribution** — RDI is derivable from labels the judge already produces, requiring no additional annotation or model calls.
4. **Calibrated mitigation validation** — The typed debate pipeline demonstrates that diagnostic profiles can directly inform intervention design, with predicted per-type gains confirmed empirically.
5. **Cost efficiency** — 4B active parameter model matching commercial APIs is practically significant for real-world deployment.
6. **Honest limitations** — The paper explicitly acknowledges the judge-dependence limitation, scope constraints to CUAD English US contracts, and single-run Experiment 2.

### Weaknesses

1. **Small *n* for numeric and factual categories** — Only 5 numeric and 3 factual clause types. The central typed-gap claim rests on the Obligation (n=27) vs. Temporal (n=6) contrast, but numeric claims are a key deployment concern.
2. **Single evaluation judge** — All reported Hal<sub>TP</sub>, Hal<sub>Gen</sub>, and RDI values flow through one LLM judge (gemini-2.5-flash). Judge bias cannot be ruled out without human validation.
3. **Single-run Experiment 2** — The mitigation study uses one run with one backbone on a 120-contract subset. Composite ranking is evidence for that comparison only.
4. **Scope errors compressed RDI** — 62–71% of contradictions are scope errors with unclear directional character, meaning RDI captures only the residual signal. The paper frames this explicitly, but it limits RDI's sensitivity.
5. **No content correction** — The pipeline reduced fabrications by 45% but barely touched content contradictions (−0.2%). This is consistent with Huang et al. (2024) but means the fundamental content-quality problem remains.
6. **Generalization uncertainty** — Results apply to CUAD English US commercial contracts; transfer across jurisdictions and document types remains unverified.

## 22. Impact and Deployment Implications

- **Typed gap findings:** Any legal AI evaluation reporting only aggregate Hal<sub>TP</sub> averages a 29–35% failure rate on temporal claims alongside a 65–74% rate on liability-determining claims.
- **Direction-aware procurement:** Two systems with identical aggregate rates can carry opposite compliance risk profiles. RDI makes this trade-off legible.
- **Agent design calibration:** Typed profiles and RDI serve as calibration inputs for multi-agent debate — Skeptic challenges and asymmetric gates targeted at measured failure modes outperform generically-tuned debate.
- **Human oversight remains essential:** The best configuration still contradicted the source in 58.6% of detected clause contents.

## 23. Limitations (from Paper)

1. Numerical results apply to 510 English-US commercial contracts from CUAD
2. All experiments assume full-document context — retrieval-augmented variants introduce additional failure modes
3. Experiment 2 uses one run with one backbone on a 120-contract subset
4. All metrics flow through a single LLM evaluation judge — validating against expert annotation is a direct extension
5. Small *n* for numeric (5 types) and factual (3 types) categories

## 24. Claim Index

| Claim ID | Claim | Evidence Location |
|----------|-------|-------------------|
| C1 | LLMs exhibit ~52% aggregate hallucination rate on legal contract extraction | §1, Abstract |
| C2 | Aggregate metrics conceal typed failure ordering | §6.1, Table 1 |
| C3 | Failure ordering {numeric, obligation} ≫ factual ≥ temporal holds across 4 diverse models | §6.2, Table 2 |
| C4 | Within-model typed gap spans 38–41 pp | §6.2, Table 2 |
| C5 | Two models with matched ~52% Hal<sub>TP</sub> can carry opposite RDI | §6.3, Fig 2, Table 3 |
| C6 | RDI for gpt-5.2 is +0.161 (invention-heavy); for qwen3-32b is −0.202 (omission-heavy) | §6.3, Table 3 |
| C7 | Scope errors dominate 62–71% of contradictions | §6.3, Fig 2 |
| C8 | Typed debate reduces fabricated detections by 45% (524 → 287) | §7.2, Table 4 |
| C9 | Debate pipeline moves gemma-4-26B-A4B from last (5.2) to first (2.4) in composite score | §7.2, Table 4 |
| C10 | Per-type ΔFAR ordering (obligation > factual > numeric > temporal) matches prior diagnosis | §7.2, Fig 4 |
| C11 | Obligation RDI shifts from −0.078 to −0.014 (near-balanced) after debate | §7.2, Fig 5 |
| C12 | 249,252 clause-level instances across 510 contracts × 3 runs × 4 models | §5.4 |
| C13 | Gemma-4-26B-A4B with 4B active parameters matches commercial APIs | §7.2, Table 4 |
| C14 | Content contradictions barely changed (−0.2%) — pipeline filters fabrication, not content errors | §7.2 |
| C15 | llma-3.3-70b numeric JEq is only 12.1% — fewer than 1 in 8 numeric clauses correct | §6.2 |

## 25. Research Directions

1. **Human-judge validation** — Validate LLM judge labels against expert annotation on a stratified sample to tighten RDI's cardinal interpretation.
2. **Generalization across jurisdictions** — Test whether the typed failure ordering transfers to non-US legal systems (civil law, Sharia law, etc.).
3. **Retrieval-augmented variants** — Extend to contracts exceeding model context windows, isolating how retrieval errors compound on content failures.
4. **Content-correction mechanisms** — The pipeline reduces fabrications but not contradictions; develop mechanisms that repair within-clause content errors (e.g., citation grounding, fine-grained value substitution).
5. **Ablation studies** — Minimal-prompt and generic-debate ablations to isolate the contribution of each calibration component (typed Skeptic, asymmetric gates, re-extract node).
6. **Multi-lingual contracts** — Test on non-English contracts to assess whether the typed gap is language-dependent.
7. **Cross-model RDI alignment** — Study whether RDI ordering is consistent across different backbone-judge combinations and whether judge choice affects directional conclusions.
8. **Real-world deployment study** — Measure whether RDI-informed procurement decisions lead to measurably better outcomes in live legal workflows.
