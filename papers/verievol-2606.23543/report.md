# VeriEvol: Scaling Multimodal Mathematical Reasoning via Verifiable Evol-Instruct

**Paper**: arXiv:2606.23543 | **Authors**: Haoling Li, Kai Zheng, Jie Wu, Can Xu, Qingfeng Sun, Han Hu, Yujiu Yang  
**Affiliations**: Tsinghua University, Tencent Hunyuan | **Date**: June 2026

---

## 1. One-Sentence Takeaway

VeriEvol decouples prompt-difficulty scaling from answer-reliability verification in multimodal mathematical reasoning data construction, achieving +3.88 mean accuracy over an un-evolved RL baseline on a 5-benchmark visual-math suite by routing seeds through type-aware evolution operators and then requiring every answer to survive offline hypothesis–test falsification before entering the training pool.

---

## 2. Problem Statement

### 2.1 The Core Challenge

Scaling reinforcement learning (RL) for visual mathematical reasoning is not just about generating harder questions — as data volume grows, **reward labels themselves must remain reliable**. Unlike supervised fine-tuning (SFT), where a wrong label is seen once, RL converts unverified labels into reward signals repeatedly across thousands of rollouts, systematically reinforcing incorrect policies.

### 2.2 Why Existing Approaches Fall Short

- **Data-pipeline work** (OpenMMReasoner, MMEvol): Scales supervision but trusts the labeller — answer set remains unverified.
- **Policy-side work** (Vision-R1, VL-Rethinker, OVR): Reshapes supervision distribution or modifies GRPO updates while assuming answers are correct.
- **Common gap**: Both families leave answer reliability to be fixed *inside* the policy/training loop rather than making it a property of the data itself.

### 2.3 The VeriEvol Framing

The paper reframes scaling as a **verifiable data-construction problem** that decouples two axes *before any policy update*:

| Axis | What It Controls | Mechanism |
|------|-----------------|-----------|
| **Prompt difficulty** | How hard the question is | Route-specific evolution operators |
| **Answer reliability** | Whether the answer is trustworthy | Offline hypothesis–test falsification |

---

## 3. Related Work Positioning

### 3.1 Benchmarks & Training Data

Key benchmarks: MathVista, MathVerse, MMMU, MATH-Vision, OlympiadBench, DynaMath, We-Math. Major training data: Qwen2.5-VL, MAmmoTH-VL, VisualWebInstruct, MathCoder-VL — all remain at SFT scale without RL-grade answer verification.

### 3.2 Prompt Evolution

Evol-Instruct → MMEvol → MathBook-7B → OpenMMReasoner. VeriEvol distinguishes itself by jointly performing instruction evolution *and* explicit answer-level falsification.

### 3.3 RL Reward Design

Two families: (a) inside-RL-loop methods (reward design, policy optimization, data-side sampling) and (b) explicit verification (Self-Refine, Reflexion, SelfCheckGPT, CRITIC, PRM800K, Math-Shepherd, ReST-EM). Common assumption: answers are correct or correctable from inside the training loop. VeriEvol is orthogonal — verification happens at data-construction stage targeting visual grounding failures (VG) and text-only shortcuts (TS).

---

## 4. The VeriEvol Framework

### 4.1 Architecture Overview

```
Low-difficulty Image-Question Seeds
         │
         ▼
┌─────────────────────────────────────┐
│  Prompt Difficulty Control           │
│  ├─ Routing (12-topic taxonomy)     │
│  ├─ Route-specific evolution ops    │
│  └─ Question-level gate φ_q         │
└─────────────────────────────────────┘
         │ (harder prompt q')
         ▼
┌─────────────────────────────────────┐
│  HTV-Agent (Answer Reliability)     │
│  ├─ 3 Independent Solvers           │
│  ├─ Counter-evidence Verifiers      │
│  │   ├─ Code-checking (Python AST)  │
│  │   └─ Visual-evidence (OCR/crops) │
│  ├─ Conflict-aware Decider          │
│  └─ Deterministic Acceptance Gate g │
└─────────────────────────────────────┘
         │ (verified answer â, verdict v)
         ▼
┌─────────────────────────────────────┐
│  Closed-loop Refinement             │
│  ├─ VeriEvol-SFT (I,q',r,â,e)      │
│  └─ VeriEvol-RL (I,q',â,v,m)       │
└─────────────────────────────────────┘
```

### 4.2 Problem Formulation

- **Seed sample**: x = (I, q, a) where I=image, q=question, a=optional answer
- **Training sample**: ᵢ̃ = (I, q', â, m) where q'=harder prompt, â=verified answer, m=metadata
- **Two data products**: D_SFT = {(I,q',r,â,e)} and D_RL = {(I,q',â,v,m)}
- **Key design**: Prompt difficulty and answer reliability are varied **independently** — empirically near-additive, confirming orthogonal failure modes

### 4.3 Type-Aware Prompt Evolution (Section 3.2)

**Routing**: Each sample → structured tuple z = (t, y, u, c) where:
- t = coarse problem family
- y = answer type
- u = recommended tool set
- c = visual-evidence sketch

**Operators**: Route-specific sets O_z, each specifying:
1. Reasoning skill to amplify
2. Visual evidence that must remain necessary
3. Desired answer format
4. Generator failure modes to avoid

Candidates scored by image dependence, mathematical lift, answerability, verifiability, and text-only penalty.

**Question gate φ_q**: Five conjunctive checks:
- C_img: grounded in visible image evidence
- C_cons: visually consistent with image
- C_vis: fails text-only probe (image remains necessary)
- C_hard: non-trivial difficulty lift over q
- C_dedup: not near-duplicate of existing prompts

### 4.4 HTV-Agent: Hypothesis–Test Answer Verification (Section 3.3)

Four stages:

1. **Solvers**: Three independent solver branches (T={0.2, 0.6, 0.15}), each returning (a_b, r_b, e_b, κ_b)
2. **Verifiers** (refutation-seeking): Counter-evidence via:
   - Code-checking module (Python assertions under restricted interpreter)
   - Visual-evidence module (OCR, local crops, pixel-level structural probes)
3. **Conflict-aware Decider**: Constrained LLM call that assesses verifier quality, commits to final answer, emits confidence
4. **Deterministic Acceptance Gate g**:
   g(â,m) = 𝟙[G_schema ∧ G_evidence ∧ G_verify ∧ G_program ∧ G_consensus]
   - Conjunctive: any failing channel rejects the sample

### 4.5 From Verified Answers to Training Signal (Section 3.4)

- **VeriEvol-SFT**: (I,q',r,â,e) — retains reasoning trace as imitation signal
- **VeriEvol-RL**: (I,q',â,v,m) — trace removed, deterministic reward checker ν_m
- **Reward**: R(y|I,q') = 𝟙[ν_m(y) = â] − β·𝟙[format_error(y)]
- **Rollout curriculum**: Estimate ρ(x) over N rollouts; intermediate ρ prioritized, ρ=1 dropped (trivially solvable), ρ=0 dropped (intractable)

---

## 5. Experimental Setup (Section 4.1)

| Component | Specification |
|-----------|--------------|
| Backbone | Qwen2.5-VL-7B-Instruct |
| SFT data | 250K VeriEvol-SFT (seeds from Honey-Data-15M) |
| RL data | 130K VeriEvol-RL (seeds from Lin et al. corpus) |
| RL algorithm | GRPO, group size 16, binary correctness reward |
| Data teachers | Seed-2.0-Pro (SFT), Gemini-3-flash (RL) |
| Baselines | OpenMMReasoner, OVR, ReVisual-R1, MMR1, WeThink, VLAA-Thinker, VL-Rethinker, ThinkLite-VL, MM-Eureka, OpenVLThinker, TRON, Vision-R1, PaLMR, NoisyRollout, V-Zero, Qwen2.5-VL-7B, InternVL3-8B |
| Benchmarks | MathVista_MINI, MathVision_MINI, MathVerse Vision-Only, DynaMath-Worst, We-Math-Strict |
| Protocol | Official metric under VLMEvalKit, T=0.6, mean over 3 runs, σ<0.5 |

---

## 6. Main Results (Section 4.2)

### 6.1 SFT-Stage Gains

| Setting | MathVista | MathVision | MathVerse-VO | DynaMath | We-Math | **Avg.** |
|---------|-----------|------------|-------------|----------|---------|----------|
| Seed-only SFT | 74.10 | 36.16 | 65.02 | 26.96 | 56.76 | **51.80** |
| VeriEvol-SFT (Init) | 76.60 | 39.80 | 67.01 | 30.94 | 59.33 | **54.73** |
| **Δ** | **+2.50** | **+3.64** | **+1.99** | **+3.98** | **+2.57** | **+2.93** |

### 6.2 RL-Stage Ablation

| Setting | MathVista | MathVision | MathVerse-VO | DynaMath | We-Math | **Avg.** | **Δ** |
|---------|-----------|------------|-------------|----------|---------|----------|-------|
| RL-Origin | 77.00 | 41.45 | 69.04 | 30.54 | 58.19 | **55.24** | — |
| RL-Evol | 78.10 | 45.39 | 69.67 | 32.14 | 60.00 | **57.06** | +1.82 |
| RL-Evol+Verifier | 79.00 | 47.37 | 70.46 | 35.73 | 63.05 | **59.12** | +3.88 |

**Cumulative decomposition**:
- Evolved prompts: +1.82
- HTV-Agent verifier: +2.06
- Total RL-stage: +3.88

### 6.3 External Comparison

VeriEvol leads on 3/5 benchmarks + mean against external 7B baselines. OpenMMReasoner-7B uses 3.5× larger SFT corpus (874K) yet VeriEvol leads on mean. MathVerse-VO leadership is most diagnostic: +6.66 over next-best OpenMMReasoner.

---

## 7. Scaling Analysis (Section 4.3)

### 7.1 SFT Data Volume

| Samples | Avg. |
|---------|------|
| 10K | 35.42 |
| 50K | 38.90 |
| 100K | 43.41 |
| 150K | 48.20 |
| 200K | 52.24 |
| 250K | **54.73** |

Monotonic +19.31 from 10K→250K. Largest gains on MathVerse-VO (+32.43).

### 7.2 RL Data Volume (Verified)

| Samples | Avg. |
|---------|------|
| 10K | 54.52 |
| 33K | 55.40 |
| 67K | 56.51 |
| 100K | 57.60 |
| 130K | **59.12** |

Monotonic +4.60 from 10K→130K. MathVision_MINI most data-hungry (+8.88). No benchmark worsens with scale.

### 7.3 Verifier Channel Modularity

Inference-time ablation on Gemini-3.5-Flash (300 samples/benchmark):
- Raw baseline: 80.89 mean
- Multi-solver SC: dominant on visually-rich tasks (MathVision: +6.00 pp)
- python_exec: dominant on computation-heavy tasks (OlympiadBench: +4.23 pp on top of SC)
- Full HTV-Agent (SC+python_exec): +4.51 pp mean improvement, never degrades any benchmark

### 7.4 Evolution Depth (Fixed Budget, 10K)

| Regime | 1 Round | 2 Rounds | Δ |
|--------|---------|----------|---|
| SFT Avg. | 35.42 | 36.79 | +1.37 |
| RL Avg. | 54.52 | 55.02 | +0.50 |

Evolution depth and data volume are complementary, not substitutable.

---

## 8. Training Dynamics (Figure 3 Analysis)

Evolved prompts produce two distinct training-time signatures:
1. **Higher reward**: Terminal running mean ~0.43 vs ~0.35
2. **Sustained entropy**: ~0.31 (roughly flat) vs collapse to ~0.22

Low-difficulty seeds → narrow trajectory set → GRPO drives low entropy early. Harder, image-grounded prompts keep multiple reasoning routes viable, preserving exploration as reward rises.

---

## 9. Error Analysis (Section 4.4)

### 9.1 Error-Type Taxonomy

| Code | Type | Description |
|------|------|-------------|
| VG | Visual grounding | Misreads, ignores, or hallucinates image element |
| RC | Reasoning chain | Visual content parsed correctly but argument breaks |
| SA | Symbolic/arithmetic | Step error in symbolic manipulation |
| AF | Answer formatting | Format mismatch |
| TS | Text-only shortcut | Solves from text priors without image |

### 9.2 Error Distribution Shift (60-sample pilot)

| Category | RL-Origin | RL-Evol+Verifier | Δ |
|----------|-----------|-----------------|---|
| VG | 13 | 6 | **-7** |
| TS | 3 | 3 | 0 |
| RC | 6 | 7 | +1 |
| SA | 4 | 6 | +2 |
| AF | 2 | 2 | 0 |
| **Total** | 28 | 24 | -4 |

VG+TS share drops from 57%→38% of residual errors.

### 9.3 Image Use in Successful Traces

On 12 paired flips (RL-Origin fails → VeriEvol succeeds):
- Explicit image reference: 10/12 (83%) vs 5/12 (42%)
- Image-grounded subgoal decomposition: 9/12 vs 3/12
- Answer consistency with image: 11/12 vs 5/12

### 9.4 Residual Failure Modes

1. **Solver–verifier shared blind spots** (~5%): All branches converge on same incorrect reading
2. **Backbone-capacity ceiling** (~20%): Items requiring multi-step symbolic chains beyond 7B capacity

---

## 10. Design Choices Contributing to the Verifier Effectiveness

1. **Multiple independent solvers**: Expose disagreement single-solver pipelines miss
2. **Refutation-seeking framing**: Probes failure modes confirmation-seeking misses (VG, TS, arithmetic slips)
3. **Complementary evidence channels**: Code-checking + visual-evidence catch different error types
4. **Separate decider**: Doesn't assume verifier is more reliable than solver; can retain solver answer or reject
5. **Conjunctive deterministic gate**: Any failing channel rejects — stricter than majority voting
6. **Rollout-based curriculum**: Filters out trivially solved or intractable samples

---

## 11. Key Strengths

1. **Pristine ablation**: RL rows share identical SFT init and GRPO recipe, cleanly isolating evolution and verification contributions
2. **Orthogonal axes confirmed**: Near-additive RL contributions (+1.82 from prompts, +2.06 from verifier)
3. **Monotonic scaling**: Both SFT and RL data volume curves never degrade — verifier filter remains usable at scale
4. **Full traceability**: Every training sample released with verifier trace (solver hypotheses, evidence reports, tool outputs, decider rationale, per-component gate outcomes)
5. **Direct compatibility**: Output plugs into existing GRPO recipes without modification

---

## 12. Limitations

1. **Seed-pool coverage**: Evolution cannot fully compensate for under-represented domains
2. **Imperfect gates**: Evolved prompts may leak textual cues; HTV-Agent accepts wrong answers when all channels share a blind spot
3. **RL-ready subset narrower** than SFT-ready subset
4. **Single seed per RL run** — differences below ~1 point are suggestive not significant
5. **Verifier-on/off not directly matched at RL budget** — indirect through inference-time ablation
6. **12-topic discretization** reduced expressivity vs full cross product of (route × skill × answer-type × verifier-contract)

---

## 13. Broader Impact & Release

- Reduces cost of high-quality visual math training data
- Synthetic pipelines can amplify source bias; per-source license tracking provided
- Full release: prompts, data (250K SFT + 130K RL), models, code, verifier traces
- Substitutes metadata + source pointers for raw images when redistribution rights unclear

---

## 14. Conclusion & Key Metrics Summary

| Metric | Value |
|--------|-------|
| SFT scaling (10K→250K) | +19.31 mean accuracy |
| RL design gain (fixed 130K budget) | +3.88 over un-evolved baseline |
| Evolved prompts contribution | +1.82 |
| HTV-Agent verifier contribution | +2.06 |
| RL data scaling (10K→130K) | +4.60 |
| External leader on MathVerse-VO | +6.66 over OpenMMReasoner-7B |
| Verifier mean improvement (inference) | +4.51 pp |
| Verifier degrades any benchmark | Never (0/6) |
| Sustained policy entropy under evolved prompts | ~0.31 vs collapse to ~0.22 |

---

## 15. Reported Extensions

The composability principle suggests extensions to:
- Chart QA
- Diagram-based science
- Document understanding
- Any domain where image-grounded answers admit deterministic or programmatic checks

Future work: verifier-aware operator-composition (beyond 12-topic discretization), heterogeneous verifier ensembles (different backbones/tool stacks).

---

## 16. Reproducibility

- Homogeneous H20 (80GB) GPU cluster, 8-GPU nodes, TP=8
- SFT: global batch size 512, AdamW LR 5e-5, 10 epochs
- RL: global batch size 256, group size 16, binary reward
- Single configuration YAML manifest released
- Full VeriEvol-RL and VeriEvol-SFT artifacts + verifier traces released
