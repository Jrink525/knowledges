# A Verifiable Search Is Not a Learnable Chain-of-Thought

**Authors:** Harsh Patel (Independent Researcher)  
**Published:** June 2026, arXiv:2606.21884  
**Tags:** `chain-of-thought`, `distillation`, `search`, `cryptarithm`, `verdict-as-token`, `SFT`, `RLVR`, `Nemotron`, `LoRA`

---

## 0. Paper at a Glance

| Aspect | Summary |
|--------|---------|
| **Core Question** | Does a verifiable solver's procedure transfer into a small model's chain-of-thought via SFT? |
| **Method** | Reverse-engineer 9 deterministic generators → Python solvers → synthetic CoT → rank-32 LoRA on Nemotron-30B (3.5B active) |
| **Key Finding** | Search does NOT distill into CoT. Forward-computable tasks transfer; backtracking search over information-free structure does not. |
| **Binding Bottleneck** | Forward-derivability: no faithful left-to-right CoT exists for search, so SFT learns only the *shape* of a verdict ("verdict-as-token"), not its logic. |
| **Escape** | Memorize the search's finite structure (catalog) + bounded verification in-trace. The 1st-place solution reached Private LB 0.92 this way. |
| **Negative Result Robustness** | 11 CoT designs, RLVR/GRPO, STaR all ≤0.07 cryptarithm-deduce; holds across 4 backbones (3B–671B), SFT and in-context. |

---

## 1. Problem Setup

The paper investigates whether any procedure expressible as a short program can be taught to a language model as its chain-of-thought (CoT) via supervised fine-tuning. The intuition: write the program's steps in natural language, fine-tune on them, and the model reproduces them. This intuition underlies rationale distillation, bootstrapped self-training (STaR), and RL from verifiable rewards (RLVR/GRPO).

**Three Research Questions:**
- **(RQ1)** Does a verifiable solver's coverage predict whether its procedure is learnable as a small model's CoT?
- **(RQ2)** When a procedure resists every training method, what is the binding bottleneck?
- **(RQ3)** Is there a cheap pre-training test that predicts resistance?

**Thesis:** A verifiable search does not distill into a chain-of-thought. The dividing line is whether the task admits a *faithful forward chain-of-thought* — a left-to-right derivation that reaches the answer. Forward-computable tasks install readily; tasks whose only solution is backtracking search over information-free structure have no faithful forward trace.

---

## 2. The Benchmark: Deterministic-Generator Design

The benchmark ships 9,500 public training problems and is scored on ≈500 hidden test problems from a public Kaggle competition (NVIDIA Nemotron Model Reasoning Challenge).

**Critical property — train ≡ test:** Every category is produced by a deterministic generator, and the hidden test uses the same generators. Train and test are i.i.d. draws from one distribution. A stratified held-out slice of `train.csv` (100 rows/category) is a faithful oracle for the leaderboard. This enables the author to measure "did the procedure transfer?" without accessing test labels.

**Grading:** Single LoRA adapter (rank ≤32) loaded onto frozen base model, served with vLLM in greedy mode (temperature 0, top-p 1.0, max_tokens=7680, max_model_len=8192) with thinking enabled. Final answer must be in `\boxed{}`.

---

## 3. The Nine Generators (Tasks)

| Category | Description | Solver Accuracy | Model Accuracy |
|----------|-------------|-----------------|----------------|
| numeral | Roman numeral encoding | ≥98% | ≥0.99 |
| unit_conversion | Linear map y=ax+b | ≥98% | ≥0.99 |
| gravity | Free-fall d=½gt² | ≥98% | ≥0.99 |
| cipher | Monoalphabetic substitution (closed 7-word vocab) | ≥98% | ≥0.99 |
| bit_manipulation | 8-bit boolean function over ≤3 taps | ≥98% | 0.68 |
| equation_numeric (deduce) | Visible-digit equation induction | ≥98% | ~0.59 |
| equation_numeric (guess) | Unseen operator | ~0.26 | ~0.26 |
| **cryptarithm (deduce)** | **5-char LHS, hidden digit→symbol cipher, hidden op, hidden endianness** | **71% (search solver)** | **0.01–0.07** |
| cryptarithm (guess) | Unseen operator | ~0.10 | ~0.02 |

**The gap is near-zero for four tasks and exceeds 0.65 for cryptarithm.**

---

## 4. Cryptarithm: The Hard Case

Each example is a five-character left-hand side `s0 s1 OP s2 s3 = RHS`. Three things are hidden per row:
1. **Injective digit→symbol cipher** (10 distinct glyphs from a 23-symbol pool)
2. **Operation** (add, sub, mul, abs-diff, mod, gcd, lcm, floor-div, ±1/±2 variants, two concat operations)
3. **Endianness** (standard or little-endian)

"**Deduce**" = query's operator was seen in examples. "**Guess**" = it was not.

Because the cipher is **information-free** (MI(digit;glyph) ≈ 0.021 nats), no single column reveals a digit. The map is pinned only by requiring *all* example equations to hold simultaneously — a cross-equation constraint search with backtracking. This is the structural reason cryptarithm sits on the far side of the learnability frontier.

---

## 5. Method: Solver-Grounded Synthetic CoT

**Pipeline (deliberately simple):**
1. Reverse-engineer each generator into a Python solver; validate against training rows
2. Render synthetic CoT for fresh instances by instrumenting the solver to narrate its steps
3. SFT the LoRA on this synthetic corpus
4. Evaluate the adapter on held-out real training rows

**One non-negotiable discipline:** The trace must *show the search* (try, reject, match) and must *never teleport* to an answer it has not derived on the page. Every verdict must restate the evidence that forces it — a "witnessed verdict."

**Escalation ladder:** When SFT plateaus → RLVR/GRPO against binary verify() → STaR (harvest model's own correct rollouts).

**Statistical reporting:** Wilson confidence intervals throughout.

---

## 6. Main Results: Where Procedure Transfers

### Easy Four (numeral, unit_conversion, gravity, cipher)
Uninteresting in the best way: once CoT is correct and ASCII-clean, model reproduces the solver to ≥0.99. Confirms pipeline and budget are not bottlenecks.

### Bit-Manipulation (the informative middle)
- Task's own prompt names its operations (XOR, AND, OR, NOT, shifts, majority, choice)
- A six-function basis (xor, maj, xor_or, or_xnor, choice, AND) accounts for 83.4% of training rows
- **Hand-authored CoT** that teleports the rule search → collapses to ≈0.05
- **STaR on the model's own successful searches** → lifts 0.526 → 0.678, truncation drops from 18.6% → 0.2%
- Accuracy is monotone in tap count: one-tap solved, two-tap mostly, three-tap sits at chance-corrected 0.31
- What transfers is search the model can *actually run*, not search narrated for it

---

## 7. The Negative Result: Cryptarithm

**Eleven successive CoT designs, all land at 0.01–0.07.** Designs included:
- Decode-first verification, truthful conditionals, policy-driven backtracking renderers
- Two-regime structure modeling, construction-of-symbol-table scaffolds
- Monotone try-counters with bail-out endings, self-routing forced chains
- Witness-bearing elimination lines, generate-and-verify reframe
- Explicit terminate-on-exhaustion traces

Truncation rate swings wildly (50% down to 14%) while accuracy does not move.

### Five Convergent Walls (Table 3)

| Wall | What It Measures | Number |
|------|-----------------|--------|
| **Solver ceiling** | Unbounded full-enumeration vote | 71% correct; 17% ambiguous |
| **Information floor** | Map mutual information | 0.021 nats ≈ 0 |
| **Base behavior** | Native greedy | 0% correct; 79% truncate |
| **Forward derivation** | Provable-step closure | 1/659 instances covered |
| **Verdict fidelity** | Per-line audit | Arithmetic 97-100%, verdicts 16-57% |

These bound *different quantities* and converge to the same conclusion.

---

## 8. Verdict-as-Token — The Mechanism

The paper's key mechanistic finding. In a per-line fidelity audit of 659 held-out cryptarithm transcripts:

- **Arithmetic is essentially perfect** (97-100% of lines)
- **Verdicts follow from their own numbers only 16-57% of the time**

Example from an actual model transcript:
```
EQ ones: ... -> no matches -> drop       ← teleported verdict
```
The same line shows `*ends` *matches* the target ones digit, yet concludes "no matches -> drop," wrongly eliminating the correct operation.

**What happens:** SFT installs the *surface form* of a verifiable elimination step as a fixed template, decoupled from the logic the step is supposed to encode. Under teacher forcing this template is always emitted in a correct context. At free-running inference it fires unconditionally — a textbook exposure-bias failure localized to the single most load-bearing token in the procedure.

**Training loss is not a signal:** All 14 cryptarithm SFT rounds drove train NLL to floor (~0.013 by step 200) while held-out accuracy stayed ≤0.07. Train loss does not predict this kind of learnability.

---

## 9. Derivation-Blocked, Not Ranking-Blocked

**The cleanest single diagnostic:** A generate-and-verify reframe. Instead of deriving the map, the model proposes hypotheses and a learned prior ranks them.

- **hit@8 = 0.71** (gold answer is in model's top 8, 71% of instances)
- Worst-case token cost of checking 8 hypotheses is well under budget

So ranking is NOT the constraint. But when the model must *derive* each hypothesis by forward arithmetic closure, coverage collapses to 1/659. The model can **recognize** a correct map but cannot **construct** one left-to-right, because constructing requires tracking which assignments remain consistent — explicit search state — across the whole problem.

---

## 10. Architecture Control: Not an SSM Problem

The author initially suspected the hybrid Mamba-2/MoE backbone (where most attention layers are replaced by state-space layers). Controlled architecture sweep:

| Model | Architecture | crypt-deduce |
|-------|------------|--------------|
| Nemotron-3-Nano-30B (3.5B act) | Hybrid Mamba/MoE | ≤0.04 |
| Llama 3.2 3B | Dense Transformer | ≤0.04 |
| Qwen 2.5 3B | Dense Transformer | ≤0.04 |
| GPT-OSS 5B | MoE Transformer | ≤0.04 |

All ≤0.04. The search-distillation ceiling is **architecture-general**, not backbone- or scale-specific. This refutes the author's own initial SSM-specific hypothesis. The same holds without fine-tuning: DeepSeek-V3 (671B) scores 0.03, Nemotron-Super-49B truncates 79%.

---

## 11. Causal Intervention: Forward-Derivability

**The paper's strongest evidence for the causal mechanism.** The author took the *same* cryptarithm instances and revealed a fraction of the digit→symbol key in the prompt, turning that fraction of the derivation from search into forward lookup:

| Key Revealed | Forward-Derivable | crypt-deduce |
|-------------|-------------------|-------------|
| None (original task) | 1/659 | 0.03 |
| Half | partial | 0.05 (CI [0.02, 0.13]) |
| Full | 659/659 | **0.571** (CI [0.45, 0.68]) |

**Two implications:**
1. Forward-derivability is **causal** — it is the lever, holding the surface task fixed
2. The effect is **sharply nonlinear** — half-forward does not give half-accuracy, because any residual search re-introduces the verdict-as-token failure. A faithful forward CoT must cover the *whole* derivation.

---

## 12. Native-Voice Attractor (Extreme Exposure Bias)

A distinct and broadly important mode: when the author authored grammars in a *non-native* voice (opening with "Bit..." or "Group..." rather than the base's habitual "I..."):
- Teacher-forced fidelity was 1.0 — the model demonstrably *learned* them
- At greedy decoding, it entered them 0% of the time
- At the very first generated token it emitted its native opener instead, a hard divergence

**Operational lesson:** Author chain-of-thought in the base's native voice, or it will never be decoded at inference no matter how well it fits.

---

## 13. RLVR: Present Gradient, No Transfer

Reinforcement learning against the verifier behaved exactly as the walls predict:
- On an **eased curriculum** (concat-only tier — pure transcription, no arithmetic): mean reward ~0.9, pass@1 ~0.98
- On **real value-operator instances**: reward ~0.0, pass@≤1 on real deduce rows stays near zero across checkpoints
- There are essentially **no positive rollouts** to learn from, so held-out accuracy never moves

The gradient mechanism is intact but has nothing to grip.

---

## 14. Solvability–Learnability Gap

The correlation between solver accuracy and model accuracy:
- **High** among lookup/fit tasks
- **Breaks** exactly where the procedure stops being a forward computation and becomes a search
- **Information-limited "guess" tasks are the control**: solver itself is low, model tracks it closely

**Solver coverage predicts model accuracy only when the solver is a forward map.** For search procedures it predicts almost nothing.

---

## 15. Error Anatomy Across All Tasks

| Root Cause | Variants | Measured Signature |
|-----------|----------|-------------------|
| **Verdict decoupled from evidence** ("verdict-as-token") | Teleport, unwitnessed claim, verdict-as-constant, fabrication-on-exhaustion | Verdict fidelity 16-57% vs arithmetic 97-100% |
| **No carried search state** | Infinite loop, no tried-set | Re-enters identical attempts; loops to tok cap on 34% |
| **Distribution mismatch** (exposure bias) | Never-enters, mid-trace drift | Teacher-forced fidelity 1.0 yet greedy adoption 0% |
| **Output corruption** | Symbol-table hallucination | Correct derivation, glyphs emitted out of order |

For the shipped adapter: **failure is wrong-answer, not budget** (cryptarithm-deduce finishes within budget and is wrong on 83%; bit-manipulation truncates only 11%).

---

## 16. Competition Dynamics and External Corroboration

The benchmark is drawn from a public competition with 4,355 teams:
- Median score: 0.85 (the ceiling of the search-distillation approach)
- Only ~15 teams cleared 0.87
- Only 2 teams reached 0.91; leader at 0.92
- Score of 0.85 is consistent with solving easy four + learnable bit-manipulation share

**Open Progress Prize** (awarded separately from leaderboard): went to a fully open-source solution that, independently, took the same approach (reverse-engineer generators → rank-32 LoRA → SFT on solver-grounded CoT). It also scored 0.85. Two independent teams converging on the same method and same ceiling is strong evidence that 0.85 *is* the ceiling of the search-distillation approach.

---

## 17. The Escape: Memorization, Not Search

The 1st-place solution (Team NullSira, Private LB 0.92) takes the approach the paper predicts: **remove the search from the trace**.

**For cryptarithm:**
- Precompute a *per-signature candidate catalog* (4,205 entries). A "signature" is the pattern of repeated symbols normalized by first occurrence (e.g., ABCCCDD)
- Enumerate all two-digit × two-digit operands under non-join rules into this catalog, mapping each signature to a shortlist of candidate (rule, digit-assignment) rows with counts
- The model **memorizes this catalog** through heavy SFT
- At inference: recall the candidate list for each equation → pick the equation with fewest candidates as anchor → bounded DFS that checks recalled candidates against remaining equations

**For bit-manipulation:**
- Precompute all valid rule sequences (5,238 entries) — every coherent 8-bit transformation normalized per-output-bit
- Project the greedy per-bit search onto the nearest catalog sequence under Hamming distance
- Verify candidates against examples

**Key insight:** The combinatorially hard step is *memorized*, not derived. Only short, bounded verification remains as CoT. What transfers is memorization and verification, not search.

---

## 18. A Predictive Rule of Thumb (Three-Part Screening)

The paper suggests a cheap pre-test for whether a solvable task will be CoT-learnable, applied *before* any training:
1. **(Forward closure)** Does a purely forward closure (no backtracking, no global constraint propagation) cover a meaningful fraction of instances?
2. **(Information structure)** Does the task's hidden structure carry non-trivial MI with observable tokens?
3. **(Base behavior)** Does the base model, prompted natively, attempt the right *kind* of move rather than truncating?

Cryptarithm fails all three. Bit-manipulation passes (2) and (3). The easy four pass trivially. This heuristic remains a hypothesis offered for testing.

---

## 19. Threats to Validity

Three worth recording:
1. **Binary-string trap:** Binary answers compared as exact strings — correct value at wrong width scored wrong
2. **Public/private overfitting:** Competitors discussed choosing a default operation that raised public score while lowering private score
3. **Memorization under train≡test:** Multi-epoch training can drive training metric to ceiling by memorizing rather than learning — author avoids this by training on synthetic instances with *different* values

**Adapter-noise laundering:** A shared high-scoring adapter can be perturbed with Gaussian noise (σ = 0.005 × tensor std) and repackaged as nominally distinct — a reproducible integrity concern.

---

## 20. Limitations

- Deep on one benchmark rather than broad across many
- Single training seeds per cell (binomial CIs bound sampling noise, not seed variance)
- Greedy decoding evaluation (sampling-based test-time search would change numbers but not the learnability question)
- One cell not schedulable: exact 30B/3.5B Transformer match fine-tuned at length
- Author did not win the competition (best public 0.85, best private 0.86, vs leader at 0.92)

---

## 21. Conclusion

A verifiable search is not a learnable chain-of-thought. What a small autoregressive model can imitate is a forward computation; what a search procedure requires is carried state — a record of what has been tried and a decision about when to stop. When a task's only honest solution is search, SFT can learn only the *shape* of the solver's verdicts, which then misfire at inference.

Two ways across this gap, and both avoid distilling the search itself:
1. Teach the model a search it can *actually run* (bit-manipulation via STaR on its own successful traces)
2. Remove the search from the trace entirely — precompute its finite structure into a catalog the model memorizes and verifies against (1st-place solution)

Solver coverage tells you the answer exists, not that your model can reason its way to it, and least of all that the solver's *search* will become its chain-of-thought.

---

## 22. Key Contributions

1. **Controlled solvability–learnability gap** — quantified per task on a train≡test benchmark
2. **Negative result with convergent evidence** — 11 CoT rounds + 3 RL/STaR escalations, 5 independent measurements all agree
3. **Three named, measured mechanisms** — verdict-as-token, derivation-blocked (not ranking-blocked), information-free sub-structure
4. **Architecture control** — search-distillation ceiling is architecture-general, not SSM-specific
5. **Causal intervention** — revealing the cipher key lifts 0.03→0.571, proving forward-derivability is the lever
6. **Externally validated escape** — 1st-place solution confirms memorization+verification, not search
7. **Public/private LB trap documented** — best private score (0.86) would have been discarded by public-LB selection

---

## 23. Related Work Connections

| Area | How This Paper Relates |
|------|----------------------|
| **CoT distillation** | Strong sense: teacher is perfect symbolic solver, not another LLM |
| **RLVR/GRPO** | Gradient present but non-transferring on cryptarithm (positive rollouts too rare) |
| **CoT faithfulness** | Verdict-as-token: sharp mechanistic instance of unfaithfulness arising in the *training* regime |
| **Compositional limits of transformers** | Adds a mechanism specific to imitation learning of search, connecting to exposure-bias gap |
| **SSM limitations** | Initially suspected, then refuted by architecture control — Mamba limit is at most a contributing factor |

---

## 24. Claim Index

| Claim ID | Statement | Evidence |
|----------|-----------|----------|
| C1.1 | Solver coverage does NOT predict whether search distills | Fig 1, Table 1 |
| C2.1 | Search over information-free structure admits no faithful forward CoT | Table 3 (walls 2,4) |
| C3.1 | Cryptarithm CoT never exceeds 0.07 across 11 designs, RLVR, STaR | Fig 4 |
| C4.1 | Arithmetic is correct on 97-100% of lines but verdicts only 16-57% | Fig 5, fidelity audit |
| C5.1 | Search-distillation ceiling holds across 4 backbones (3B-21B) | Table 6 |
| C6.1 | Revealing cipher key lifts 0.03→0.571; half-key barely helps | Table 7 |
| C7.1 | Ranking is not the constraint (hit@8=0.71); forward derivation is (1/659) | Section 5.2 |
| C8.1 | Train loss is not a signal for this learnability (NLL converges, accuracy stays at floor) | Section C |
| C9.1 | The escape: memorize catalog + bounded verification (1st-place, Private LB 0.92) | Section 9 |
| C10.1 | Non-native CoT voice → 0% greedy adoption despite 1.0 teacher-forced fidelity | Section 5.4 |

---

## 25. References (Selected Key Works)

- [2] Bengio et al. Scheduled Sampling, NIPS 2015 (exposure bias)
- [5] DeepSeek-AI. DeepSeek-R1, Nature 2025 (RLVR)
- [8] GoodMeatDay et al. 1st-place solution (memorization–computation split)
- [10] Hsieh et al. Distilling step-by-step, ACL 2023
- [12] Hu et al. LoRA, ICLR 2022
- [20] Merrill et al. Illusion of state in state-space models, ICML 2024
- [22] NVIDIA. Nemotron Nano (hybrid Mamba/MoE)
- [25] Shao et al. DeepSeekMath, 2024 (GRPO)
- [28] Turpin et al. Unfaithful explanations in CoT, NeurIPS 2023
- [31] Zelikman et al. STaR, NeurIPS 2022
- [32] Zhou et al. What algorithms can transformers learn? ICLR 2024
