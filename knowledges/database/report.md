# Deep Reading Report: Do Language Models Need Sleep? Offline Recurrence for Improved Online Inference

> Paper: https://arxiv.org/abs/2605.26099 | Source: LaTeX-primary (`main.tex` + `macro.tex` + `neurips_2026.sty` + `reference.bib` + 8 PDF figures)
> Reading mode: LaTeX-primary, with all source files available including bibliography (25324 bytes, 104 entries) and 8 vector-graphic figures
> Confidence: High — all sections, formulas, algorithms, and references present; only appendix checklist omitted (empty)

---

## 1. Paper Identification and Source Package Used

### Anchored Points
- [C1.1][evidence-backed interpretation] The paper was submitted to NeurIPS 2026 (uses `neurips_2026.sty`), authored by Sangyun Lee (CMU), Sean McLeish (UMD), Tom Goldstein (UMD), Giulia Fanti (CMU).
- [C1.2][evidence-backed interpretation] Full LaTeX source was available: 737-line `main.tex`, `macro.tex` (command definitions), `neurips_2026.sty` (NeurIPS 2026 style), `reference.bib` (104 citations), and 8 PDF figures.
- [C1.3][evidence-backed interpretation] No appendix content beyond stub (`\input{checklist.tex}` commented out); no supplementary material was bundled.

**Title:** Do Language Models Need Sleep? Offline Recurrence for Improved Online Inference

**Authors:**
- Sangyun Lee — Carnegie Mellon University (correspondence)
- Sean McLeish — University of Maryland
- Tom Goldstein — University of Maryland
- Giulia Fanti — Carnegie Mellon University

**Venue/Status:** NeurIPS 2026 submission (preprint).

**Source files used:** `main.tex`, `macro.tex`, `neurips_2026.sty`, `reference.bib`, all 8 figures under `figures/`.

**What was searched/verified:** All sections of the LaTeX source, all 104 bibliography entries (titles checked for temporal ordering and relevance), all figure captions.

**What was missing:** The appendix is a stub (`\input{checklist.tex}` commented out), so no NeurIPS checklist or extended ablations are present. No code release URL is provided.

**Effect on confidence:** Moderate. Without the appendix checklist, we cannot verify author-side reproducibility claims. The paper's central claims are well-supported by in-paper evidence even without the appendix.

---

## 2. One-Sentence Thesis and Research Equation

### Anchored Points
- [C2.1][evidence-backed interpretation] The paper's central thesis is: *Hybrid SSM-attention LLMs fail on deep reasoning over evicted context not because of memory capacity limits, but because single-pass fast-weight formation provides insufficient computation for deep sequential transformations — and allowing offline recurrence ("sleep") over the context before eviction remedies this failure.*
- [C2.2][plausible inference] The biological sleep analogy is a narrative device, not a mechanism: there is no pretense of modeling hippocampal replay biologically.

**Research equation:**

```
Hybrid SSM-attention models succeed at long-range recall
  BUT fail when reasoning depth increases (even with fixed memory load)
    → Hard setting: context is hard-evicted, prediction is single-pass
      → Borrowed tool: depth-recurrence / looped networks
        → Unavailable mechanism: multi-pass prediction-time compute (would break latency constraint)
          → Surrogate mechanism: offline recurrence before eviction, which converts computation into persistent fast weights
```

**Compact form:** `A(hybrid SSM-attention) ∩ ¬C(deep reasoning over evicted context) ∩ T(hard eviction + single-pass prediction) ∩ M(offline recurrence) => Z≈Y(reasoning improvement scales with sleep duration)`

Where:
- A = standard hybrid SSM-attention architecture
- ¬C = failure on reasoning-burdened tasks despite sufficient memory capacity
- T = hard eviction constraint + prediction-phase latency constraint
- M = sleep-like offline recursive fast-weight consolidation
- Z≈Y = sleep duration positively correlates with reasoning performance on evicted context

---

## 3. Title Interpretation

### Anchored Points
- [C3.1][evidence-backed interpretation] "Sleep" maps to the phase where the model processes accumulated context in multiple offline forward passes without external input — analogous to biological sleep where hippocampal replay consolidates memories.
- [C3.2][evidence-backed interpretation] "Need" is qualified: the paper shows sleep *helps* on reasoning-heavy tasks, not that models cannot function without it.
- [C3.3][evidence-backed interpretation] "Offline Recurrence" is the precise technical mechanism — multiple forward passes over fixed context with no new input tokens.
- [C3.4][evidence-backed interpretation] "Improved Online Inference" refers to prediction-phase single-pass quality, which improves because fast weights have been refined during sleep.

**Title-to-method mapping:**

| Title term | Maps to | Scope & limitations |
|---|---|---|
| "Sleep" | Multiple offline forward passes (N loops) before KV cache eviction | No biological fidelity claim; just recurrence during a no-input phase |
| "Need" | Downstream accuracy improves with N; tasks with deep reasoning benefit more | Does not claim universal necessity; models without sleep still work on easy tasks |
| "Offline Recurrence" | The algorithmic mechanism: looping over blocks during consolidation | Does not add recurrence at prediction time; compatible with existing looped model training techniques |
| "Improved Online Inference" | Single-pass prediction accuracy improves despite no prediction-time compute increase | Improvement is over "no-sleep" hybrid baseline, not over multi-pass inference methods |

**Caveat:** "Need" in the title is somewhat provocative/marketing; the paper's own evidence shows sleep is beneficial but not strictly necessary for all tasks.

---

## 4. What Problem the Paper Really Solves

### Anchored Points
- [C4.1][evidence-backed interpretation] The direct problem: SSM-attention hybrid models fail when they must reason deeply about context that has been evicted from the KV cache.
- [C4.2][evidence-backed interpretation] The practical pain point: long-context LLM inference cannot afford full attention over all past tokens, but current fast-weight mechanisms (SSM blocks) don't provide enough computation to transform compressed context into useful representations.
- [C4.3][plausible inference] The scientific question: Is the bottleneck in hybrid models memory *capacity* or reasoning *computation*? Prior work claimed capacity; this paper argues it's computation.
- [C4.4][evidence-backed interpretation] The parent-field pressure: As LLMs move toward long-horizon tasks (code generation, multi-turn reasoning, simulation), efficient memory management without sacrificing reasoning quality becomes critical.

**Three-layer problem decomposition:**

| Layer | Problem | Why it matters |
|---|---|---|
| Direct (method) | Single fast-weight pass can't do deep computation | Models fail on multi-hop retrieval and multi-step reasoning over evicted context |
| Practical (systems) | Need long-context processing without quadratic attention cost | Full attention is too expensive; sliding-window + SSM is the practical alternative |
| Scientific (theory) | What limits reasoning with fixed-size memory? | If it's capacity → bigger SSM states. If it's computation → need recurrence |

The paper's main contribution is showing that **computation, not capacity, is the bottleneck**, and that offline recurrence is a computation-adding mechanism that respects latency constraints.

---

## 5. Scientific Problem Ladder

### Anchored Points
- [C5.1][evidence-backed interpretation] The paper works at 4-5 rungs on the ladder, from concrete synthetic tasks to general LLM finetuning.
- [C5.2][plausible inference] A notable bottleneck introduced by the method: training throughput degrades with N (roughly 1/N of the no-recurrence baseline), making it mainly useful when the reasoning gains justify the training cost.

**Ladder:**

| Rung | Level | Paper's contribution | Bottleneck introduced |
|---|---|---|---|
| 1 | Synthetic control (Rule 110 cellular automaton) | Show that single-pass SSM fails on deep rollout; sleep fixes it | — |
| 2 | Graph reasoning (Depo multi-hop retrieval) | Show failure extends to relational reasoning; sleep helps | — |
| 3 | Math reasoning (GSM-Infinite) | Show trend holds with pretrained LLMs at 1.4B–2B scale | — |
| 4 | Training efficiency | Sequentiality across windows + depth costs 1/N throughput | Training cost scales linearly with N |
| 5 | General long-context LLM deployment | Method preserves single-pass inference latency | Requires model to be a hybrid (SSM + attention) or be converted; SSM warm-up needed |

**Upper-level bottlenecks introduced:**
- **Training instability** (noted in limitations): deep BPTT through recurrence is harder to optimize than parallel training.
- **Throughput cost**: ~1/N tokens/sec during training, which may limit adoption for very large N.
- **Architecture constraint**: Only works with SSM-attention hybrids (or models with writable fast-weight blocks); pure-attention models cannot benefit without architectural modification.

---

## 6. How the Authors May Have Found This Direction

### Anchored Points
- [C6.1][evidence-backed interpretation] The authors are from CMU and UMD, with Goldstein being a well-known figure in optimization and adversarial ML. Fanti's group works on networked/secure systems.
- [C6.2][plausible inference] The dissatisfaction likely came from observing that Samba, Hyena, Mamba, and Jet architectures work well on retrieval benchmarks but fail when reasoning depth is explicitly controlled.

| Valuable field | Painful assumption | Borrowed/emerging tool | Blocking constraint | Conceptual replacement |
|---|---|---|---|---|
| Hybrid sequence models | SSM fast weights capture enough info in one pass | Depth-recurrent/looped networks (Ouroboros, Parcae) | Prediction-time latency cannot increase | Move extra compute to consolidation phase, not prediction phase |
| Memory consolidation (neuroscience) | Sleep replay supports LTM formation | Learned local update rules (Hebbian/Delta in SSMs) | Biological implementational details don't transfer | Use forward-pass recurrence instead of gradient-based consolidation |
| Test-time training (TTT) | One gradient step per chunk is enough | Recurrent forward passes as non-gradient memory updates | Gradient-based TTT is expensive and hard to scale | Learned forward pass replaces explicit loss minimization |

**Why the surrogate was worth trying:**
- Depth-recurrent models (Ouroboros) already showed that compute at depth scales with reasoning ability.
- SSM fast weights already support recurrent updates (Eq. 1 with S_t = αS_{t-1} + βvk^T).
- The missing piece was: what if recurrence is applied *to already-seen context* (consolidation) rather than to future prediction?
- This is cheap to test: add a loop in training over the context within each window, BPTT through it, compare with no-loop baseline.

---

## 7. How the Authors Built the Story

### Anchored Points
- [C7.1][evidence-backed interpretation] The story has a tight challenge → failure → principle → module → evidence loop, not a bag of disconnected modules.
- [C7.2][evidence-backed interpretation] The paper sets up the failure cleanly: in Section 3 (motivating example), they show a concrete task (Rule 110, t=32) where the baseline hybrid model fails.
- [C7.3][evidence-backed interpretation] The proposed method directly addresses the identified failure mode (insufficient computation, not insufficient capacity).

**Story structure:**

| Challenge | Failure mode | Design principle | Module | Evidence |
|---|---|---|---|---|
| Deep reasoning over evicted context | Single fast-weight pass insufficient | More compute for consolidation → better fast weights | Offline recurrence (N loops before cache eviction) | Fig 3-right: 3-4 loops > no-loop on automaton t=32 |
| Ensure improvement is not capacity-driven | Prior work blamed memory capacity | Vary reasoning depth t while holding sequence length fixed | Synthetic tasks with controlled variables | Fig 3-left: accuracy drops with rollout step despite fixed length |
| Scale to pretrained LLMs | Synthetic trends may not transfer | Fine-tune existing hybrids with sleep | Jet-Nemotron 2B, Ouro 1.4B finetuning | Fig 5: accuracy improves with N on harder GSM-Infinite problems |
| Realistic eviction (not just hard) | Hard eviction is artificial | Sliding-window eviction retains some context | SWA-SSM hybrid with sleep | Fig 6: sleep helps even with SWA, especially for retrieval |

**Is the story a coherent loop?** Yes. Challenge → failure diagnosis → design response → evidence forms a clean causal chain. The only potential gap is that the paper does not theoretically prove why more recurrence helps (it's empirical throughout).

---

## 8. Related Work, Key Citations, and What Was Still Missing

### Anchored Points
- [C8.1][evidence-backed interpretation] The related work covers 5 clusters with distinct narrative roles.
- [C8.2][evidence-backed interpretation] Key missing piece identified: prior work on hybrid models (Samba, Hymba, Mamba-2) focused on memory capacity as the bottleneck; this paper is the first to systematically separate capacity from computation.

**Citation clusters:**

| Cluster | Key references | Narrative role |
|---|---|---|
| Fast weights & linear RNNs | Katharopoulos 2020, Schlag 2021, Yang 2023/2024, Dao 2024 | Field anchor + method ancestors: these define the SSM-as-fast-weight view |
| Context compression | Ge 2023, Eyuboglu 2025 | Contrast boundary: they compress context → shorten attention; this paper transfers context → weights |
| Context distillation | Snell 2022, Tandon 2025, Zhang 2026 | Neighboring inspiration + limitation: they use gradient-based one-step consolidation; this paper uses learned multi-step forward passes |
| Depth-recurrent models | Dehghani 2018, Graves 2016, McLeish 2025, Geiping scaling, Prairie 2026 | Method ancestors + baseline pressure: looped networks provide the training technique; Ouro/ PArCAE provide scaling insights |
| Sleep & offline processing | Lin 2025, Chalvidal 2022, Hafner 2019, Sutton 1991 | Inspiration + contrast: different uses of "sleep" in ML; this paper's is closest to Lin 2025 but uses a different mechanism |

**What was still missing (at the time of writing):**
- Formal proof relating sleep duration N to reasoning capability (e.g., TC0 vs NC bounds) — the paper is entirely empirical.
- Ablation on where to place sleep loops (they loop all or middle blocks; no systematic study of per-layer effects).
- Comparison against TTT-style baselines under the same compute budget (Table 2 of Tandon 2025 on GPU-hours).
- Scaling laws for N (does optimal N grow with model size?).

---

## 9. Main Idea

### Anchored Points
- [C9.1][evidence-backed interpretation] The core conceptual replacement: instead of treating fast-weight formation as a single-pass, online process (process token → update S → done), treat it as a **two-phase** process where, at eviction boundaries, the model can refine S through **multiple passes over the same context** without seeing new tokens.
- [C9.2][evidence-backed interpretation] This replaces the implicit assumption "one forward pass at token arrival is enough to encode context into weights" with "encoding complex context may need iterative refinement."
- [C9.3][evidence-backed interpretation] The coordination logic: during sleep, the attention layers provide non-local access to the entire current window (the "hippocampal" function), while SSM layers update fast weights (the "cortical" function). Recurrent passes let these two systems interact multiple times.

**Coordination logic (why it works):**
```
Window context → Attention layers (broad access to all tokens in window)
                → SSM layers (update S via learned local rule)
                → (loop N times) S is iteratively refined
                → Evict KV cache (attention forgets window-specific tokens)
                → S carries consolidated information forward
                → Prediction phase: single forward pass uses refined S
```

The key insight is that each pass through the blocks allows attention to re-read the full window context and SSM to update weights based on a potentially improved understanding. After N passes, S contains a more organized representation of what the window contained, even though the raw tokens will soon be evicted.

---

## 10. Symbols, Assumptions, and Notation

### Anchored Points
- [C10.1][evidence-backed interpretation] The paper's notation is consistent with the SSM-as-fast-weight literature.
- [C10.2][evidence-backed interpretation] Hidden assumption: the learned local update rule in SSM blocks (the delta rule / gated Hebbian update) can represent useful consolidation operations; the paper does not analyze what functions the SSM update rule can learn.

**Key symbols:**

| Symbol | Meaning | First introduced | Note |
|---|---|---|---|
| N | Number of sleep passes (recurrence depth) | Section 1 | Core hyperparameter; N=1 ↔ no sleep |
| L | Window size (tokens per chunk) | Section 3 | Hard eviction boundary |
| T | Total sequence length | Section 3 | Held fixed when varying reasoning depth |
| S_t | SSM fast weight matrix at step t | Section 2.1 | Fixed-size, updated by outer product |
| k | Hop count (Depo task) | Section 4.1 | Measures reasoning depth in graph retrieval |
| t | Rollout step (automaton task) | Section 3 | Measures reasoning depth in cellular automaton |
| α_t | Forget gate in SSM update | Eq. 1, Preliminaries | Data-dependent, (0,1) |
| β_t | Input gate in SSM update | Eq. 1, Preliminaries | Data-dependent, (0,1) |

**Hidden assumptions that may become direction seeds:**
1. **S is zero-initialized** — The paper says SSM fast weights are zero-initialized at the start of each sequence. This means prior consolidated memory is reset. Could persistent fast weights across sequences help?
2. **Sleep uses the same context repeatedly** — The N passes all see the same input tokens. Could using progressively refined representations (like iterative refinement in diffusion) help?
3. **SSM update rule is frozen at inference** — The learned local rule is trained end-to-end. Could the rule itself be adapted during inference?
4. **Attention layers don't update weights during sleep** — Only SSM layers get weight updates. Attention provides access but doesn't consolidate. Could attention-to-weight consolidation help?
5. **Training uses full BPTT through N loops** — This is expensive. Implicit differentiation or truncated BPTT could reduce cost (noted as future work).

---

## 11. Key Formulas and Equation-by-Equation Explanation

### Anchored Points
- [C11.1][evidence-backed interpretation] The paper builds on three central formulas: the SSM update, the sleep recurrence, and the training loss.

**Formula 1: SSM fast-weight update (Eq. 1, Preliminaries)**

```math
S_t = α_t S_{t-1} + β_t v_t k_t^T
o_t = S_t q_t
```

- **Role:** The core memory mechanism. Each token at position t writes an outer product v_t k_t^T into the fast weight matrix S, scaled by input gate β_t. The forget gate α_t decays old memory. Reading is a simple matrix-vector product: S_t × q_t.
- **Why this form:** Combines Hebbian-style memory (outer product) with gating for selectivity — analogous to the delta rule in online learning.
- **Connection:** During sleep, the same S is repeatedly updated by processing the same tokens N times. Each pass adds new outer product contributions.
- **Fragile point:** The linear nature of S (matrix-valued) means that the write capacity is d² for dimension d. Complex relational structures must fit in this fixed matrix. The gating mechanism controls what gets overwritten but has no explicit mechanism for organizing entries beyond pairwise associations.

**Formula 2: Sleep architecture (Eq. 2, Section 4)**

```math
Embed → [B_attn_0 → B_ssm_1 → … → B_attn_{D-1}]^{×N} → OutProj
```

- **Role:** Defines the full training-time computation graph. The superscript ×N means N recurrent passes through all D layers.
- **Why this form:** Borrows directly from universal transformers / depth-recurrent networks. The novel part is that this recurrence happens only during consolidation, not during prediction.
- **Connection to Eq. 1:** Each B_ssm pass updates S. Over N passes, S receives N×L outer product updates (L tokens in window, N passes).
- **Fragile point:** The feature vectors h are discarded after sleep (only S is kept). This is stated explicitly but the implications for gradient flow are significant: gradients must go through the SSM update path (S refinement) rather than the feature refinement path.

**Formula 3: Training loss (Algorithm 1)**

```math
L = MaskedCrossEntropy(OutProj(h), c, m_c)
```

Where c is the token chunk and m_c is the loss mask (non-zero only during prediction phase).

- **Role:** The model is trained only on prediction-phase token prediction. The consolidation phase (where sleep happens) has no loss signal.
- **Why this form:** Forces S to learn representations that support future prediction, not current reconstruction.
- **Fragile point:** There is no auxiliary loss during consolidation (no reconstruction loss, no predictive coding loss). The gradient signal must propagate backward through the entire sleep sequence to reach the SSM updates.

**Modification triggers / direction seeds:**
1. What if S is updated with a *difference* rule (S ← S + f(S, context)) rather than overwrite? Could reduce capacity erosion.
2. What if attention layers also get a memory bank during sleep (like a compressed K-V cache that persists)?
3. What if the number of sleep passes N is *adaptive* — predicted by the model based on context complexity?

---

## 12. Theory / Proof / Practice Mapping

### Anchored Points
- [C12.1][evidence-backed interpretation] The paper contains no formal theoretical results (no theorems, no proofs, no complexity bounds).
- [C12.2][evidence-backed interpretation] The argument is entirely empirical: the paper constructs tasks where reasoning depth is the controlled variable and shows that sleep helps.

**What is "proved" vs. shown:**

| Claim | Evidence type | Strength |
|---|---|---|
| Hybrid models fail on deep reasoning | Empirical: accuracy drops with rollout step (Fig 3-left) | Strong: controlled synthetic task, varying only reasoning depth |
| Sleep improves accuracy | Empirical: more loops → higher accuracy (Fig 3-right) | Strong: multiple N values tested, consistent trend |
| Sleep helps more on harder problems | Empirical: gap widens with hop count / operations (Fig 4, 5) | Strong: consistent across three domains |
| Improvement is not due to capacity | By construction: fixed sequence length, varying only reasoning depth | Strong argument, but no theoretical bound |

**What is missing:**
- **Theoretical motivation**: Why should N passes help? Is there a known complexity class where depth N is provably more expressive than depth 1 with fixed memory? References to P-completeness of Rule 110 and TC0 arguments from prior work are suggestive but not formal.
- **Scaling law**: Does optimal N scale with model size? With reasoning depth? No analysis.
- **Convergence guarantee**: Does the training procedure (BPTT through N loops) converge to a useful S? No analysis.

**If assumptions are dropped:**
1. **If sleep doesn't need to be offline** → could interleave sleep and prediction, which would change the latency properties.
2. **If SSM update is not linear** → the fast-weight formulation changes, but the sleep idea may generalize.
3. **If the context window is not fully evicted** → the paper tests this (sliding-window eviction) and sleep still helps.

---

## 13. Algorithm or Module Walkthrough with Concrete Example

### Anchored Points
- [C13.1][evidence-backed interpretation] Algorithm 1 is the core method, presented as pseudocode.
- [C13.2][evidence-backed interpretation] The paper's use of hard eviction boundaries is unusual but is justified by the desire for clean experimental control.

**Concrete example: Rule 110 task with sleep**

Let's walk through one training sequence with hard eviction:

**Input:** 4 binary states of length 24 = 96 tokens + 4 label tokens = 100 tokens total.
**Window size:** L = 24 (fits exactly one state per window)
**Sleep passes:** N = 3
**Rollout step:** t = 32

**Phase 1: Window 0 (state 0: 0101...1101)**
1. Embed "0101...1101" → h (24 token vectors)
2. **Sleep entry:** Since this is a consolidation window (no loss mask), enter sleep:
   - Pass 1 of 3: Forward through B_attn_0 → B_ssm_1 → B_attn_2 → B_ssm_3
   - SSM blocks update S: each token writes v_k^T into S
   - Pass 2 of 3: Same input h, same blocks → S is refined (new outer products from same tokens)
   - Pass 3 of 3: Further refinement of S
3. **Cache eviction:** KV cache cleared
4. Result: S_0 now contains consolidated representation of state 0 (24 bits)

**Phase 2: Window 1 (state 1: 1101...1000)**
- Same process, starting from S_0 (carried over from previous window)
- S updated to S_1 during sleep, representing both state 0 and state 1

**Phase 3-4: Windows 2-3 (states 2 and 3)**
- S_2 and S_3 accumulate representations of all 4 states

**Phase 5: Prediction window (4 tokens: label0, label1, label2, label3)**
1. Process each label token with a single forward pass (no sleep)
2. For label0: predict first bit of state 0 after 32 Rule 110 steps
3. Loss computed against ground truth → backpropagate through entire computation graph

**Key insight:** During sleep, the model must learn to use the outer product updates (v_k^T) in the SSM to store not the raw state but the *first bit after 32 steps*. This requires simulating the cellular automaton during consolidation and storing the result.

---

## 14. Method Deep Reading: The Author-Thinking Behind Each Module

### Anchored Points
- [C14.1][evidence-backed interpretation] Each module fixes a specific failure identified in the motivating example.
- [C14.2][plausible inference] The decision to loop entire blocks (not just SSM layers) suggests the authors thought attention's non-local access was needed during consolidation.

| Module | Failure fixed | Ideal unavailable solution | Available proxy | Hidden assumption | Risk under violation | Future research point |
|---|---|---|---|---|---|---|
| SSM fast-weight block | Single-pass encoding insufficient | Variable-depth inference | N-step recurrence during consolidation | SSM can learn to organize beyond Hebbian associations | If SSM capacity is truly the limit (not compute), N won't help | Structured SSM states (e.g., block-diagonal with different timescales) |
| Sleep-phase attention | Need non-local access within window during consolidation | None (attention works as designed) | Attention over the full window before eviction | Attention doesn't need to persist across windows | If key info spans windows, each window consolidation is incomplete | Cross-window attention during sleep |
| Hard eviction at L boundary | Need controlled test of consolidation | None (it's an experimental control) | Hard boundary | Model can learn which info to consolidate | If boundary bisects important structure, consolidation is harder | Learned eviction (which tokens to keep) |
| Prediction-phase single pass | Must preserve low latency | Multi-pass prediction | Move compute to consolidation phase | Single pass is enough if S is good enough | If task truly requires prediction-time chain-of-thought, sleep won't help | Sleep + short CoT hybrid |

---

## 15. Figure Explanation

### Anchored Points
- [C15.1][evidence-backed interpretation] 8 figures available as PDF vector graphics; all captions informative.
- [C15.2][evidence-backed interpretation] Figures support the central empirical claims without obvious visual cherry-picking.

| Figure | Content | Claim supported | Does evidence match claim? |
|---|---|---|---|
| Fig 1 (method.pdf) | Architecture diagram: SSM-attention hybrid with N-loop sleep | Illustrates the method | Yes; clear visual of recurrence during consolidation |
| Fig 2 (automaton_rollout_steps.pdf) | t=1,4,8,16,32 curves; accuracy drops with rollout | Hybrid fails on deep reasoning | Yes; strong downward trend |
| Fig 3-right (automaton_nl.pdf) | No-loop vs 2/3/4-loop for t=32 | Sleep improves accuracy | Yes; clear separation |
| Fig 4 (depo_h_loss.pdf) | k=1,2,4,8,16 loss curves | Sleep helps multi-hop retrieval | Yes; more loops help hardest hops most |
| Fig 5-left (jet_w2000.pdf) | GSM-Infinite: Jet 2B acc vs ops | Trend holds at 2B scale | Yes, moderate effect (0.351→0.388 for 8-op) |
| Fig 5-right (ouro_w2000.pdf) | GSM-Infinite: Ouro 1.4B acc vs ops | Larger effect for looped-pretrained Ouro | Yes, stronger effect (0.210→0.272 for 8-op) |
| Fig 6 (gsm_ouro_swa_nl.pdf) | Sliding-window eviction, Ouro 1.4B | Sleep helps beyond hard eviction | Yes; large improvement (0.596→0.905 on 2-op) |
| Fig 7-8 (ouro_train_*.pdf) | Training throughput analysis | Overhead is manageable | Partially supportive; shows linear cost |

**Notable:** Fig 6 (sliding-window) shows the largest relative improvement (52% on 2-op problems). The authors note this but don't deeply explain why retrieval (not just reasoning) benefits from sleep. This is an interesting open question.

---

## 16. Experimental Design

### Anchored Points
- [C16.1][evidence-backed interpretation] The experimental design is controlled and systematic, with clear variable separation.
- [C16.2][evidence-backed interpretation] All training details are specified: optimizer (Muon + AdamW), learning rates, batch sizes, GPU days, random seed control.
- [C16.3][plausible inference] Missing control: no comparison against simply training a deeper model (more layers) for the same compute budget. Is N-loop better than D' × 1 (deeper but no recurrence)?

**Tasks:**

| Task | Controlled variable | Fixed variable | Metric | Key result |
|---|---|---|---|---|
| Rule 110 automaton | Rollout step t (1,4,8,16,32) | Sequence length=100, window=24 | Exact accuracy | Accuracy drops with t; sleep (N>1) helps at t=32 |
| Depo | Hop count k (1,2,4,8,16) | Total tokens=360, window=75 | Test loss | Sleep helps most at k≥4; N=4 needed for k=16 |
| GSM-Infinite | Operations (2,4,6,8) | Tokens=2000-3300, window=2000 | Accuracy | Sleep improves 6-op and 8-op; minimal gain at 2-op |

**Baselines:**
- No-loop (N=1) = standard hybrid SSM-attention model
- Training from scratch: 4-layer GDN-attention (automaton, Depo)
- Finetuning: Jet-Nemotron 2B, Ouro 1.4B (GSM-Infinite)

**Missing baselines:**
1. Deeper non-looped model with same parameter count
2. TTT (test-time training) baseline with one gradient step
3. Context distillation baseline
4. A model trained with more tokens (to rule out that the no-loop model just needs more data)

**Statistical rigor:**
- Fixed random seeds (same data ordering across runs) — good
- Early stopping for easy tasks — appropriate
- No confidence intervals shown in figures — concerning; the difference between N=2 and N=3 or N=4 may not be statistically significant without error bars

---

## 17. Experiments as Story Evidence and Claim Alignment Audit

### Anchored Points
- [C17.1][evidence-backed interpretation] The main claims align reasonably with the experimental evidence, but with some important caveats.
- [C17.2][plausible inference] The weakest supported claim is that sleep helps *proportionally to reasoning depth* — the evidence shows it helps, but the granularity is coarse (4 levels of N tested).

| Claim | Key experiment | Alternative explanation ruled out? | Support strength |
|---|---|---|---|
| Hybrid models fail on deep reasoning | Automaton t=1→32, accuracy drops | Yes: sequence length fixed → not capacity | Strong |
| Sleep improves accuracy | Automaton t=32, N=1→2→3→4 | Partially: monotonic but no error bars | Moderate-strong |
| Improvement larger for harder problems | Depo k=1→16, GSM 2→8 ops | Partially: consistent trend but effect size varies | Moderate |
| Benefit transfers to pretrained LLMs | GSM-Infinite with Jet/Ouro | Yes: two architectures, two model families | Strong |
| Sliding-window also benefits | GSM-Infinite with SWA, Ouro | Yes: qualitatively same trend | Moderate-strong |
| Training overhead is manageable | Throughput analysis | Partially: shows linear cost, but no wall-clock comparison for real benefit | Moderate |

**Overall audit:** The evidence is well-constructed for the central claim (computation, not capacity). The weakest point is that the paper doesn't rule out that a deeper non-looped model would match the N-loop model's performance — the comparison is always N-loop vs N=1 with the same architecture.

---

## 18. Results That Surprised Me or Every Reader

### Anchored Points
- [C18.1][evidence-backed interpretation] The 52% improvement on 2-op GSM-Infinite with sliding-window eviction (0.596 → 0.905) is the most striking result.
- [C18.2][evidence-backed interpretation] The failure of the 1-loop model on 4-hop Depo is surprisingly complete — it essentially plateaus at near-chance loss.
- [C18.3][plausible inference] It's surprising that Ouro (1.4B) shows a larger sleep benefit than Jet (2B) on GSM-Infinite, given Jet is larger and already a hybrid.

**Why these are surprising:**
1. **SWA + sleep on retrieval**: The authors expected sleep to help mainly on reasoning, but the biggest effect is on retrieval-heavy problems (2-op GSM). This suggests sleep may help with *compression* as much as *computation*.
2. **Complete 1-loop failure on k=4 Depo**: Even 4-hop graph traversal, which seems modest, cannot be solved with N=1. This strongly validates the computation-over-capacity claim.
3. **Ouro > Jet sleep benefit**: Ouro is pretrained as a depth-recurrent model, so it may already have circuitry that better utilizes recurrence. This suggests that **pretraining with recurrence + finetuning with sleep** may be a winning combination.

---

## 19. Reviewer-Grade Audit: Hard-Hitting Questions

### Anchored Points
- [C19.1][plausible inference] The paper would likely receive positive reviews for its clean experimental design, but would face questions about practical significance.

**Questions a reviewer would (should) ask:**

1. **Q: How does N-loop compare to simply training a deeper model?** The baseline is N=1 with D layers. What about N=1 with 2D layers (twice as deep)? If deeper non-looped models match N-loop, the benefit is just more parameters, not recurrence.
2. **Q: Where are the error bars?** Figures show single runs. With multiple seeds, would the N=2 vs N=3 difference hold?
3. **Q: Is the benefit worth the throughput cost?** N=4 loops → ~1/4 training throughput. For GSM-Infinite 8-op: N=1 gets 0.351, N=6 gets 0.388 (Jet). That's a 10.5% relative gain at 6× training cost.
4. **Q: Does sleep work at larger scales?** Tested only up to 2B. Would sleep help at 7B+? The training instability issue may compound.
5. **Q: Why does Ouro benefit more than Jet?** The paper says "may reflect its depth-recurrent pretraining" but doesn't test this hypothesis (e.g., finetuning Ouro without depth-recurrent pretraining).
6. **Q: How is N chosen?** Is there a principled way to select N, or is it tuned per task? The paper tests {2,3,4} and {2,4,6} without a selection criterion.
7. **Q: Could chain-of-thought (CoT) during prediction achieve the same effect?** The paper explicitly excludes CoT, but a practical system could use short CoT. What's the comparison?
8. **Q: What happens with variable-length windows?** All experiments use fixed L. Real inference uses variable-length context. How robust is sleep to window boundary placement?

**Aggregate assessment:** The paper's core claim (computation bottleneck, not capacity) is solid. Its practical claims (sleep improves accuracy) are supported but the effect size is modest enough that a reviewer may ask whether the training overhead is justified.

---

## 20. Research-Direction Mining

### Anchored Points
- [C20.1][plausible inference] The paper opens at least 5 concrete research directions.

**Priority-ordered directions:**

| Direction | Trigger | Why promising | First-step experiment |
|---|---|---|---|
| **Adaptive sleep duration** | N is currently fixed per run | Different contexts need different compute; can save cost | Train a small "complexity predictor" that predicts optimal N |
| **Persistent fast weights across sessions** | S is zero-initialized each sequence | Long-lived models could benefit from cross-sequence memory | Initialize S from a learned prior instead of zero |
| **Sleep at multiple timescales** | Only window-level sleep is tested | Hierarchical consolidation (tokens → chunks → episodes) | Multi-level architecture: fast sleep within window, slow sleep across windows |
| **Attention consolidation during sleep** | Only SSM weights are updated | Attention's pattern-matching could also inform weight updates | Add compressed attention memory that survives eviction |
| **Combining sleep with test-time adaptation** | Sleep is training-only currently | Fine-tune S during inference using the same mechanism | Continue updating S on new context without BPTT |

**Direction board summary:**
- Low-hanging fruit: adaptive N, persistent S, multi-scale sleep
- High-risk/high-reward: attention consolidation, theoretical depth bounds
- Near-term impact: adaptive sleep + sliding-window eviction (most practical)

---

## Appendix A: Claim-Evidence Traceability Index

| Claim ID | Section | Statement | Evidence type | Source paragraph IDs | Confidence |
|---|---|---|---|---|---|
| C1.1 | 1 | NeurIPS 2026 submission | Evidence-backed | P-main-tex-0003 (neurips_2026.sty) | High |
| C1.2 | 1 | Full LaTeX source available | Evidence-backed | Verification of file listing | High |
| C2.1 | 2 | Central thesis | Evidence-backed | Abstract + Sections 3,4 | High |
| C3.1 | 3 | Sleep maps to offline recurrence | Evidence-backed | Section 4, Fig 1 caption | High |
| C4.1 | 4 | Hybrid models fail on deep reasoning | Evidence-backed | Section 3, Fig 2 | High |
| C5.1 | 5 | Paper works at 4-5 rungs | Evidence-backed | Sections 5.1-5.4 | High |
| C7.1 | 7 | Coherent story loop | Plausible inference | Sections 3→4→5 narrative | High |
| C8.1 | 8 | Five citation clusters | Evidence-backed | Reference.bib analysis | High |
| C9.1 | 9 | Two-phase consolidation | Evidence-backed | Section 4, Algorithm 1 | High |
| C10.2 | 10 | SSM update can represent consolidation | Plausible inference | Section 2.1 + Section 4 | Moderate |
| C12.1 | 12 | No formal theory | Evidence-backed | Full text scan | High |
| C16.3 | 16 | Missing deeper baseline | Plausible inference | Experimental design analysis | Moderate |
| C19.1 | 19 | Reviewer questions about practical significance | Speculation | Section 6 (Limitations) + analysis | Moderate |

---

## Appendix B: Supplementary File Manifest

Files generated in `knowledges/papers/llm-sleep-2605.26099/`:
- `report.md` — This report
- `traceability_manifest.json` — JSON claim-evidence traceability matrix
- `research_lens.json` — Research lens / analytical perspective
- `direction_board.json` — Research direction mining board
