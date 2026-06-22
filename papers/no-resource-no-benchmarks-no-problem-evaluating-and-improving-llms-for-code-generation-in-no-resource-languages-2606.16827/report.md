# No Resource, No Benchmarks, No Problem? Evaluating and Improving LLMs for Code Generation in No-Resource Languages

**arXiv: 2606.16827v1 [cs.SE] — Published: 15 Jun 2026**

**Authors:** Alessandro Giagnorio, Alberto Martin-Lopez, Gabriele Bavota  
**Affiliations:** Università della Svizzera italiana (USI) / Universidad de Sevilla  
**GitHub:** [Devy99/no-resource-pl-study](https://github.com/Devy99/no-resource-pl-study)  
**Replication Package:** [10.5281/zenodo.19366887](https://doi.org/10.5281/zenodo.19366887)

---

## 1. The Problem

### 1.1 The Resource Hierarchy of Programming Languages

Large Language Models (LLMs) exhibit a steep performance gradient across programming languages based on their representation in training corpora:

- **High-resource languages** (Python, Java): >10M GitHub repositories each; abundant training data; extensively studied.
- **Low-resource languages** (Lua, R, Racket, Haskell, Julia): 22K–981K repos; underrepresented but some research exists.
- **No-resource languages** (Gleam, MoonBit): <3K repos; virtually **no training data** seen by LLMs; **entirely unstudied** in the literature.

### 1.2 The Gap

While LLMs achieve ~59-89% pass@1 on high-resource languages (McEval-Hard) and ~27-84% on low-resource, **performance on no-resource languages is 0-1%** on the same benchmark. This is not just a matter of degree — it represents a **complete failure mode** for current LLMs on languages that fall outside their training distribution.

### 1.3 Why This Matters

No-resource languages frequently emerge in industry where organizations develop proprietary or domain-specific languages. Commercial tools like GitHub Copilot and ChatGPT do not support these languages. Companies are left with the challenge of developing **custom, in-house code recommenders** — but effective and economically sustainable solutions are far from trivial.

### 1.4 Core Challenges

1. **No benchmarks exist** — no-resource languages are usually proprietary, so no public test suites are available.
2. **No training data** — even the little data that exists (e.g., GitHub repos) is orders of magnitude less than low-resource languages.
3. **Syntactic failure dominates** — ~2/3 of failures in no-resource languages are syntactic (vs. <10% for high-resource), indicating LLMs can't grasp basic grammar.
4. **Instruction-following vs. language knowledge trade-off** — the best technique (further pre-training) can only be applied to base models, which lack instruction-following capabilities.

---

## 2. Study Design

### 2.1 Research Questions

| RQ | Question | Method |
|----|----------|--------|
| RQ1 | How does language popularity affect LLM code generation performance? | Zero-shot evaluation on 9 languages across 3 benchmarks |
| RQ2 | Can in-context learning, pre-training, and fine-tuning boost LLMs on no-resource languages? | 5-shot, RAG, fine-tuning, and further pre-training |
| RQ3 | Does instruction transferring (weight diff) further boost performance? | Base PT → weight diff from instruct model |

### 2.2 Selected Languages

| Language | Classification | GitHub Repos (Jul 2025) | Stable Release |
|----------|---------------|------------------------|----------------|
| MoonBit | **No-resource** | 400 | Dec 2024 (compiler) |
| Gleam | **No-resource** | 2,900 | Mar 2024 (v1.0) |
| Racket | Low-resource | 22,200 | — |
| Julia | Low-resource | 81,000 | — |
| Haskell | Low-resource | 155,000 | — |
| Lua | Low-resource | 517,000 | — |
| R | Low-resource | 981,000 | — |
| Java | High-resource | 18,700,000 | — |
| Python | High-resource | 21,500,000 | — |

**Selection rationale for no-resource languages:**
- Stable releases after LLM cutoff dates (latest: Mar 2024)
- Well-documented with community support for benchmark verification
- Gleam: functional, type-safe, multi-thread; MoonBit: general-purpose, cloud/edge computing

### 2.3 Benchmarks

Three function-level code generation benchmarks were translated (via ChatGPT + manual verification) to Gleam and MoonBit:

| Benchmark | Tasks | Source | Characteristics |
|-----------|-------|--------|---------------- |
| **HumanEval** | 154 | MultiPL-E → translation | Trivial to easy coding tasks |
| **MBPP** | 355 | MultiPL-E → translation | Easy to moderate tasks |
| **McEval-Hard** | 227 | McEval → manually curated "hard" subset | **Most challenging** |

**Translation pipeline** (≈340 man-hours):
1. Exclude Python-specific tasks (6/161 HumanEval, 27/399 MBPP)
2. ChatGPT-generated prompt translation with explicit transformation rules
3. Automated syntax check → manual inspection
4. ChatGPT-generated test translation → automated check → manual inspection + major fixes

**McEval-Hard creation:** Selected only "hard" problems (difficulty ≥3 on 5-point scale) from the original McEval, then manually reviewed and refined for the target languages.

### 2.4 Evaluated LLMs

| Model | Type | Size | Cutoff | Techniques Applied |
|-------|------|------|--------|-------------------|
| **GPT-4o** | Commercial | — | Unknown | Zero-shot, 5-shot, RAG |
| **o3-mini** | Commercial | — | Unknown | Zero-shot, 5-shot, RAG |
| **Qwen 2.5 Coder 32B Instruct** | Open | 32B | Mar 2024 | Zero-shot, 5-shot, RAG, Fine-tuning |
| **Qwen 3 32B Instruct** | Open | 32B | Mar 2024 | Zero-shot, 5-shot, RAG, Fine-tuning |
| **Qwen 2.5 Coder 32B Base** | Open (base) | 32B | Mar 2024 | Zero-shot, Pre-training, Instruction transferring |
| **Qwen 3 8B Base** | Open (base) | 8B | Mar 2024 | Zero-shot, Pre-training, Instruction transferring |

### 2.5 Training Data

| Dataset | Purpose | Gleam | MoonBit |
|---------|---------|-------|---------|
| Pre-training | Teach language syntax/APIs | 28.3M tokens | 13.7M tokens |
| Fine-tuning | Pair (doc, function) training | 3.6M tokens | 0.5M tokens |

Pre-training uses all available code + documentation; fine-tuning requires paired (natural language description, function) pairs — a scarcer resource.

---

## 3. Experimental Results

### 3.1 RQ1: Language Popularity Gradient

**McEval-Hard Results (most challenging benchmark):**

| LLM | Python | Java | Low-resource (range) | Gleam | MoonBit |
|-----|--------|------|---------------------|-------|---------|
| GPT-4o | 75.12 | 58.99 | 27.70–84.89 | 0.97 | 0.88 |
| o3-mini | 88.94 | 86.39 | 52.07–86.39 | 0.18 | 1.10 |
| Qwen 2.5 Coder 32B | 70.57 | 72.60 | 31.63–62.07 | 0.40 | 0.88 |
| Qwen 3 32B | 70.04 | 64.71 | 27.00–54.54 | 0.44 | 0.88 |

**Error analysis:**
- **No-resource:** ~2/3 of failures are **syntactic** (up to 90% for o3-mini on Gleam)
- **High/low-resource:** <10% syntactic failures (exception: Java ~30% due to verbosity)
- The 10-20% pass@1 on simpler benchmarks (HumanEval, MBPP) is explained by **trivial tasks** where the function signature provides enough context and the body is common across languages (e.g., `return l * l * l;`)

### 3.2 RQ2: Boosting Techniques

**Key findings:**

1. **In-context learning (5-shot, RAG):** Modest improvements; few-shot > RAG in most cases (7/12 Gleam, 8/12 MoonBit). Few-shot reduces syntactic errors by 15.36% vs. 8.94% for RAG. Gains are higher on MoonBit (less training data → more room for improvement).

2. **Fine-tuning:** Outperforms in-context learning. Fine-tuned open models competitive with commercial models using few-shot/RAG. E.g., Qwen 3 fine-tuned on Gleam: 23.57% (HumanEval) vs GPT-4o 5-shot: 15.45%.

3. **Pre-training (base models):** **Best-performing technique in RQ2**. Significantly outperforms fine-tuning:
   - Qwen 2.5 Coder 32B Base pre-trained on Gleam: 12.47% McEval-Hard vs. fine-tuned instruct: 3.04%
   - MoonBit: 25.86% vs. 10.93%
   - **Why:** Pre-training uses ALL available data (28.3M/13.7M tokens) vs. fine-tuning only paired (doc, function) data (3.6M/0.5M tokens)

**Trade-off:** Pre-trained base models lack instruction-following capabilities — they can generate code but cannot effectively respond to varied natural language prompts.

### 3.3 RQ3: Instruction Transferring (Weight Diff)

**The innovation:** Start from base model Mb → further pre-train on no-resource language → Mbk. Compute weight diff Δw between instruct model Mi and base Mb. Apply Δw to Mbk → Mbk+i.

**Results:**

| Model | Technique | Gleam (McEval-Hard) | MoonBit (McEval-Hard) |
|-------|-----------|---------------------|----------------------|
| Qwen 2.5 Coder 32B Base | Pre-training only | 12.47% | 25.86% |
| Qwen 2.5 Coder 32B Base | + Instruction Transfer | **26.08%** (+13.61) | **32.60%** (+6.74) |
| Qwen 3 8B Base | Pre-training only | 4.36% | 19.87% |
| Qwen 3 8B Base | + Instruction Transfer | **22.33%** (+17.97) | 19.82% (=) |

**Key findings:**
- **Average improvement:** +12% pass@1 across all benchmarks, models, and languages
- All improvements statistically significant (McNemar, p < 0.05) except Qwen 3 + MoonBit McEval-Hard (no change)
- **Gleam benefits more** (more room for improvement after pre-training)
- **Smaller models can beat larger ones:** Qwen 3 8B + instruction transferring outperforms Qwen 3 32B Instruct in all configurations (up to +28% on Gleam HumanEval)

**Error analysis with instruction transferring:**
- 32B model: both syntactic and semantic errors decrease
- 8B model: syntactic errors increase (+13.3% Gleam, +241.6% MoonBit) but semantic errors decrease more → net positive
- Suggests smaller models **reallocate limited capacity** toward instruction following, sacrificing some syntactic precision

### 3.4 Ablation: Manual Overfitting

The authors tested a "manual" prompt containing all relevant language documentation → approximate upper bound for in-context learning. Result: still far below instruction transferring, especially on McEval-Hard (Gleam: 1.76% vs 26.08%).

---

## 4. Practical Recommendations

### The Best Pipeline

```
Step 1: Choose a base model (Mb) and its instruct version (Mi)
Step 2: Collect all available data for the target no-resource language
        (GitHub repos, documentation, language specs)
Step 3: Further pre-train Mb on the collected data (cheap, CPU-friendly)
Step 4: Compute Δw = Mi - Mb (CPU-only, negligible cost)
Step 5: Apply Δw to pre-trained Mbk → Mbk+i
```

**Cost:** Pre-training uses consumer GPUs (not H100s); instruction transferring uses only CPUs.

### Why This Works

- Pre-training teaches the model the language's **syntax, APIs, and conventions**
- Instruction transferring injects **instruction-following behavior** without the cost of full instruction fine-tuning
- The weight diff captures "the essence of instruction following" separate from domain knowledge

### When to Expect Good Results

| Condition | Impact |
|-----------|--------|
| Language has some code + documentation available | ✓ Pre-training can work |
| Model family has both base and instruct versions | ✓ Instruction transferring possible |
| Language syntax resembles known languages | ✓ Faster learning |
| Language is very different from any known language | — More pre-training needed |

---

## 5. Claim Index

| ID | Claim | Evidence | Confidence |
|----|-------|----------|------------|
| C1 | LLMs achieve 0-1% pass@1 on no-resource languages for hard tasks (McEval-Hard) | Table IV, all 4 LLMs on Gleam/MoonBit | ★★★★★ |
| C2 | Syntactic errors dominate in no-resource failures (~2/3 of cases) | Error classification analysis (replication package) | ★★★★☆ |
| C3 | Low-resource languages no longer as challenging as previously reported; 49/60 cases above 50% pass@1 | Table IV analysis | ★★★★☆ |
| C4 | Further pre-training outperforms fine-tuning for no-resource languages | Table V comparison, ORs 1.43–4.24 | ★★★★★ |
| C5 | Pre-training outperforms fine-tuning because it uses more data (all code vs. only paired doc-function) | Table III data sizes: 28.3M vs 3.6M (Gleam), 13.7M vs 0.5M (MoonBit) | ★★★★☆ |
| C6 | Instruction transferring boosts pass@1 by +12% on average vs. pre-training alone | Table VI, 11/12 cases show improvement | ★★★★★ |
| C7 | Smaller models (8B) + instruction transfer can outperform larger models (32B) | Table VI: Qwen 3 8B+Diff vs Qwen 3 32B fine-tuned | ★★★★☆ |
| C8 | In-context learning helps but is significantly weaker than training-based approaches | Table V: ORs and pass@1 comparisons | ★★★★★ |
| C9 | MoonBit shows higher improvement from techniques than Gleam, possibly due to AI-friendly language design | Table V, discussion in §III | ★★★☆☆ |
| C10 | Pre-training base models does not harm instruction following when combined with weight diff transfer | Table VI vs Table V (comparing to zero-shot instruct models) | ★★★★☆ |

---

## 6. Threats to Validity

### Internal Validity
- **Hyperparameter tuning:** Not performed; default configurations used. Tested at epochs 1, 3, 5: epoch 5 best, epoch 3 within ±3.4%.
- **Benchmark quality:** Manual validation of 346 tasks (95% confidence, ±5% error): 4% prompts with issues, 0.6% test issues. Comparable to flaws in established benchmarks like SWE-bench.
- **Fine-tuning data quality:** Manual validation of 707 instances: median quality score = 5/5 across all dimensions.

### External Validity
- Only 2 no-resource languages studied (Gleam, MoonBit) — may not generalize
- Only function-level code generation — real-world usage may differ
- Benchmarks translated, not native — may not capture idiomatic usage
- 9 languages, 6 LLMs, 3 benchmarks — comprehensive but not exhaustive

### Construct Validity
- **Data contamination:** Cannot fully verify that Gleam/MoonBit code wasn't in training data. However, stable releases post-date known cutoffs (Mar 2024). Not in Qwen's advertised supported languages.
- **pass@1 vs. passed%:** The two metrics can diverge for syntactic errors (which fail all tests vs. partial failures)

---

## 7. Related Work Positioning

| Work | Focus | Relation |
|------|-------|----------|
| MultiPL-E [Cassano et al. 2023] | 24-language benchmark translation | Used as base; extended to no-resource |
| MultiPL-T [Cassano et al. 2024] | Synthetic training data for low-resource | Not applicable: LLMs can't translate to no-resource |
| IRCoder [Paul et al. 2024] | LLVM IR alignment for low-resource | Not applicable: Gleam/MoonBit lack LLVM support |
| ModelMate [Costa et al. 2024] | DSL-specific fine-tuning | Different setting: general-purpose vs. domain-specific |
| Giagnorio et al. [2025] | Low-resource code generation study | Prior work by same authors; no-resource not studied |

---

## 8. Future Work

1. **Expand benchmarks** to cover debugging, refactoring, and change-request-level tasks
2. **Constrained decoding** — enforce grammar rules at inference time (e.g., XGrammar)
3. **More no-resource languages** — test generalizability
4. **Domain-specific tasks** — real-world usage beyond function-level coding
5. **Long-term tracking** — as LLMs evolve, do no-resource gaps persist?

---

## 9. Key Takeaways

1. **No-resource languages are a fundamentally different problem** from low-resource — LLMs completely fail (0-1% on hard tasks), primarily due to syntax ignorance.
2. **Pre-training on available data is the best single technique** — it exploits all available code and documentation, not just paired examples.
3. **Instruction transferring via weight diff is the breakthrough** — it's cheap (CPU-only), preserves both language knowledge and instruction-following, and enables small models to beat large ones.
4. **The pipeline is practical** — any company with a proprietary language can: collect available data → pre-train a base model → transfer instruct weights → deploy.
5. **MoonBit benefits more** due to its AI-friendly design and smaller existing data footprint.
