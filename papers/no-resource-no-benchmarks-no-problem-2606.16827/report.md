# No Resource, No Benchmarks, No Problem? Evaluating and Improving LLMs for Code Generation in No-Resource Languages

## 1. Paper Identity

| Field | Value |
|-------|-------|
| **Title** | No Resource, No Benchmarks, No Problem? Evaluating and Improving LLMs for Code Generation in No-Resource Languages |
| **Authors** | Alessandro Giagnorio, Alberto Martin-Lopez, Gabriele Bavota |
| **Affiliations** | SEART @ Software Institute, Università della Svizzera italiana (Giagnorio, Bavota); SCORE Lab, I3US Institute, Universidad de Sevilla (Martin-Lopez) |
| **arXiv ID** | 2606.16827 (cs.SE) |
| **Venue** | Accepted for publication at IEEE Transactions on Software Engineering (TSE) |
| **Submission Date** | 15 June 2026 |
| **License** | CC BY 4.0 |
| **Replication Package** | Zenodo: https://doi.org/10.5281/zenodo.19366887 |

---

## 2. Abstract

Large Language Models (LLMs) have significantly advanced code generation, but most research focuses on high-resource languages (Python, Java). Low-resource languages have received some attention, but **no-resource languages**—those for which LLMs have seen virtually no training data—remain largely unstudied. These languages often emerge in industry as proprietary or domain-specific languages unsupported by commercial tools like GitHub Copilot.

The authors build and release three code generation benchmarks (NoResourceCode) for two no-resource languages: **Gleam** and **MoonBit**. They experiment with prompt-based techniques (few-shot, RAG), pre-training, and fine-tuning. Further pre-training gives the largest gains but harms instruction-following in instruct models. To solve this, they propose **weight diff transfer**: pre-train a base model on the target language, then inject instruction-following capabilities by adding the weight difference from an instruct model. This approach significantly improves performance, allowing cheap deployment of specialized instruct models.

---

## 3. Problem Statement

**What is a no-resource programming language?**

A no-resource language is one that falls **outside the pre-training distribution of LLMs**—the model has seen virtually no training data in that language. The paper focuses on **no-resource general-purpose languages**, which share syntactic and semantic characteristics with mainstream languages but lack training data.

**Key characteristics of no-resource languages:**
- Fewer than ~3,000 GitHub repositories (vs. 22k+ for the least popular low-resource language — Racket)
- Stable release after LLM cutoff dates (training data predates the language)
- Unsupported by commercial tools like GitHub Copilot or ChatGPT
- Often emerge in industry as proprietary or domain-specific languages

**Why this matters:** Organizations developing proprietary languages need custom in-house AI coding assistants, but have no benchmarks to evaluate them and no clear methodology for specialization.

---

## 4. Motivation

The paper addresses a practical industrial problem: companies develop proprietary or domain-specific programming languages that commercial AI tools cannot support. Without benchmarks or established methods, these organizations face significant challenges in deploying LLM-based code generation for their languages.

The work provides:
1. **Benchmarks** to measure code generation quality in no-resource languages
2. **Empirical evidence** of the performance gap across high/low/no-resource languages
3. **Effective techniques** for specializing LLMs at low computational cost

---

## 5. Background & Related Work

### 5.1 Code Generation Benchmarks

Prior benchmarks (HumanEval, MBPP, McEval) target high-resource languages. **MultiPL-E** (Cassano et al., 2023) translated HumanEval and MBPP to 24 languages including low-resource ones. **McEval** (Chai et al., 2025) provides tasks in 40 languages with ~50 instances each. No benchmarks existed for no-resource languages.

### 5.2 Low-Resource Language Studies

**MultiPL-T** (Cassano et al., 2024) generates synthetic training data for low-resource languages. **IRCoder** (Paul et al., 2024) uses LLVM intermediate representation to align high- and low-resource languages. Giagnorio et al. (2025) analyzed in-context learning and fine-tuning strategies for low-resource languages, finding that providing more examples helps but fine-tuning may reduce performance.

### 5.3 Instruction Transferring

In NLP, Jindal et al. (2024) showed that further pre-training an instruct model degrades instruction-following. Lin et al. (2025) proposed fine-tuning reuse—transferring instruction-following weights from an instruct model to a base model via weight diff. The paper adapts this approach for no-resource code generation.

### 5.4 Gap in Literature

No prior work has:
- Built benchmarks for no-resource languages
- Systematically evaluated LLM performance across the high/low/no-resource spectrum
- Applied weight diff transfer for code generation in no-resource settings

---

## 6. Research Questions

**RQ1:** To what extent does the popularity of programming languages affect the code generation performance of LLMs?
- Preliminary RQ establishing performance baselines across high/low/no-resource languages

**RQ2:** To what extent can in-context learning, pre-training, and fine-tuning boost the code generation performance of LLMs on no-resource languages?

**RQ3 (Section IV):** To what extent does instruction transferring (weight diff) boost the code generation performance of LLMs on no-resource languages?

---

## 7. Languages and Benchmarks

### 7.1 Selected Languages

| Language | Classification | #GitHub Repos (as of Jul 2025) | Notes |
|----------|---------------|-------------------------------|-------|
| MoonBit | No-resource | 400 | v1 compiler: Dec 2024 |
| Gleam | No-resource | 2,900 | v1: 4 Mar 2024 |
| Racket | Low-resource | 22,200 | |
| Julia | Low-resource | 81,000 | |
| Haskell | Low-resource | 155,000 | |
| Lua | Low-resource | 517,000 | |
| R | Low-resource | 981,000 | |
| Java | High-resource | 18,700,000 | |
| Python | High-resource | 21,500,000 | |

Gleam and MoonBit have **at least one order of magnitude fewer** repositories than the least popular low-resource language (Racket with 22,200). Before March 2024 (cutoff for 4 of 6 LLMs), only 560 Gleam and 7 MoonBit repos existed.

### 7.2 Benchmarks: NoResourceCode

Three benchmarks translated to all 9 languages:

1. **HumanEval** (154 tasks): Function-level code generation from Python, translated via MultiPL-E and then to Gleam/MoonBit
2. **MBPP** (355 tasks): Same process
3. **McEval-Hard** (227 tasks): Novel benchmark built from McEval's "hard" problems across 40 languages, deduplicated and translated to all 9 languages

**Translation pipeline:**
- Excluded Python-specific tasks
- ChatGPT generated initial translations with explicit transformation rules
- Automated syntax checking + manual inspection
- ChatGPT generated test translations → syntax check → manual inspection
- Gleam benchmarks double-checked by Louis Pilfold (Gleam creator) on 50 random samples

### 7.3 Pre-Training & Fine-Tuning Datasets

| Dataset | Language | #Code Tokens | #Doc Tokens | Total |
|---------|----------|-------------|-------------|-------|
| Pre-training | Gleam | 28.2M | 0.1M | 28.3M |
| Pre-training | MoonBit | 13.1M | 0.6M | 13.7M |
| Fine-tuning | Gleam | 3.6M | — | 3.6M |
| Fine-tuning | MoonBit | 0.5M | — | 0.5M |

- Pre-training: 18,767 Gleam files + 3,609 MoonBit files from GitHub + official documentation
- Fine-tuning: 13,534 Gleam functions + 2,444 MoonBit functions with docstrings (extracted via tree-sitter)
- Data leakage prevention: 8-gram matching + manual verification

---

## 8. LLMs and Experimental Setup

### 8.1 Selected LLMs

| Model | Parameters | Instruction Following | Reasoning | Cutoff Date |
|-------|-----------|----------------------|-----------|-------------|
| Qwen 2.5 Coder 32B Base | 32B | ✗ | ✗ | 2024-03 |
| Qwen 2.5 Coder 32B Instruct | 32B | ✓ | ✗ | 2024-03 |
| Qwen 3 8B Base | 8B | ✗ | ✗ | ? |
| Qwen 3 32B Instruct | 32B | ✓ | ✓ | ? |
| o3-mini | ~200B (est.) | ✓ | ✓ | 2023-10 |
| GPT-4o | ~200B (est.) | ✓ | ✗ | 2023-10 |

### 8.2 Metrics

- **pass@1**: Binary — did the generated code pass ALL tests? (with n=10 repetitions)
- **passed%**: Percentage of tests passed (partial correctness)
- **Statistical testing**: McNemar's test + Benjamini-Hochberg correction + Odds Ratio (OR)

### 8.3 Parameters

- Temperature: 0.2 (except o3-mini which uses default)
- 10 runs per model per benchmark per language
- Total zero-shot generations: 264,960 (66,240 × 4 models)

---

## 9. RQ1 Results: Impact of Language Popularity

### 9.1 Main Results (pass@1 on McEval-Hard)

| | High-Resource | Low-Resource | No-Resource |
|---|---|---|---|
| **Range** | 59–89% | 27–84% | **0–1%** |
| **Average** | ~79% | ~62% | ~9% |

### 9.2 Detailed Results

**Full pass@1 table (all models, all languages):**

**GPT-4o:**
| Dataset | Python | Java | R | Lua | Haskell | Julia | Racket | Gleam | MoonBit |
|---------|--------|------|---|---|---------|-------|--------|-------|---------|
| HumanEval | 91.23 | 83.96 | 64.35 | 81.69 | 64.03 | 72.40 | 60.00 | 7.60 | 12.60 |
| MBPP | 84.90 | 76.11 | 64.85 | 70.85 | 66.62 | 74.00 | 63.66 | 20.31 | 16.54 |
| McEval-Hard | 77.67 | 59.30 | 55.02 | 65.42 | 53.79 | 52.42 | 32.25 | 0.97 | 0.88 |

**o3-mini:**
| Dataset | Python | Java | R | Lua | Haskell | Julia | Racket | Gleam | MoonBit |
|---------|--------|------|---|---|---------|-------|--------|-------|---------|
| HumanEval | 96.75 | 92.92 | 74.48 | 84.03 | 87.21 | 83.70 | 79.68 | 4.55 | 7.34 |
| MBPP | 84.34 | 73.41 | 66.87 | 67.44 | 75.55 | 77.92 | 66.56 | 7.75 | 15.01 |
| McEval-Hard | 88.94 | 86.39 | 80.13 | 69.12 | 83.96 | 73.17 | 52.07 | 0.18 | 1.10 |

**Qwen 2.5 Coder 32B Instruct:**
| Dataset | Python | Java | R | Lua | Haskell | Julia | Racket | Gleam | MoonBit |
|---------|--------|------|---|---|---------|-------|--------|-------|---------|
| HumanEval | 89.61 | 83.31 | 56.49 | 76.04 | 49.48 | 69.74 | 68.12 | 6.49 | 11.04 |
| MBPP | 83.32 | 66.82 | 62.56 | 70.14 | 51.01 | 74.68 | 57.27 | 9.83 | 17.80 |
| McEval-Hard | 70.57 | 72.60 | 47.89 | 62.07 | 31.63 | 48.41 | 33.00 | 0.40 | 0.88 |

**Qwen 3 32B Instruct:**
| Dataset | Python | Java | R | Lua | Haskell | Julia | Racket | Gleam | MoonBit |
|---------|--------|------|---|---|---------|-------|--------|-------|---------|
| HumanEval | 89.03 | 77.66 | 55.26 | 80.52 | 46.82 | 70.84 | 61.88 | 4.55 | 7.27 |
| MBPP | 83.66 | 71.27 | 62.08 | 67.30 | 52.90 | 75.01 | 53.92 | 6.23 | 18.06 |
| McEval-Hard | 70.04 | 64.71 | 40.26 | 54.54 | 27.00 | 44.80 | 28.19 | 0.44 | 0.88 |

### 9.3 Key Findings

1. **High-resource languages**: Excellent performance (avg 79% pass@1)
2. **Low-resource languages**: Reasonable support (avg 62%, 49/60 cases >50%). Performance not solely determined by popularity (Lua outperforms R despite fewer repos)
3. **No-resource languages**: Near-zero performance (avg 9% on easy tasks, 0-1% on McEval-Hard)
4. **Failure analysis**: ~2/3 of failures on no-resource languages are **syntactic errors** vs. <10% for high/low-resource languages. LLMs fundamentally lack basic grammar knowledge.

The ≥10% pass@1 on HumanEval/MBPP for no-resource languages is attributed to **trivial tasks** (e.g., "return l * l * l" for cube volume) where LLMs exploit similarity to high-resource languages like Rust/Java.

---

## 10. RQ2 Results: Boosting Performance

### 10.1 In-Context Learning

**Few-shot (5-shot) and RAG** on instruction-following models:

| Finding | Detail |
|---------|--------|
| Few-shot slightly better than RAG | 7/12 cases Gleam, 8/12 MoonBit |
| Syntax error reduction | Few-shot: -15.36%, RAG: -8.94% |
| Higher gains on MoonBit than Gleam | MoonBit has 7× fewer repos, AI-friendly design |
| Higher gains on simple tasks | McEval-Hard gains substantially lower |
| Statistical significance | Most OR values statistically significant |

**Key numbers (5-shot, best cases):**
- GPT-4o on MoonBit MBPP: from 16.54% → 40.51% (OR=10.35)
- o3-mini on MoonBit HumanEval: from 7.34% → 39.22% (OR=31.69)
- McEval-Hard remains challenging: best from 0.18% → 12.20% (o3-mini MoonBit)

### 10.2 Fine-Tuning

Fine-tuning on open instruct models (Qwen 2.5 Coder 32B Instruct, Qwen 3 32B Instruct):

- **Substantially better than in-context learning**
- Fine-tuned open models compete with commercial models + few-shot/RAG
- Qwen 3 32B Instruct fine-tuned: Gleam HumanEval 23.57%, MBPP 37.32%, McEval-Hard 3.88%
- Qwen 2.5 Coder 32B fine-tuned: MoonBit HumanEval 34.74%, MBPP 37.38%, McEval-Hard 10.93%

### 10.3 Pre-Training

Further pre-training on base (non-instruct) models:

- **Best-performing technique in RQ2**
- Qwen 2.5 Coder 32B Base pre-trained: Gleam HumanEval 32.99%, MBPP 47.35%, McEval-Hard 12.47%
- Qwen 2.5 Coder 32B Base pre-trained: MoonBit HumanEval 41.62%, MBPP 44.76%, McEval-Hard 25.86%
- Pre-training > fine-tuning for same model architecture (more training data available)
- **Downside**: Pre-trained base models lack instruction-following capabilities

### 10.4 Performance Comparison

Pre-trained base >> fine-tuned instruct > in-context learning > zero-shot
- Pre-training outperforms fine-tuning on the same architecture (OR: 1.43–4.24)
- Pre-trained Qwen 3 8B Base comparable to fine-tuned Qwen 3 32B Instruct on MoonBit

---

## 11. Instruction Transferring (Weight Diff)

### 11.1 Method

The authors propose **instruction transferring** to solve the instruction-following gap of pre-trained base models:

1. **M_b**: Base model (e.g., Qwen 2.5 Coder 32B Base) — no instruction following
2. **M_i**: Instruct version of M_b (e.g., Qwen 2.5 Coder 32B Instruct)
3. **M_bk**: M_b further pre-trained on no-resource language k (from RQ2)
4. Compute weight diff: **Δ_w = M_i - M_b**
5. Inject into M_bk: **M_{bk+i} = M_bk + Δ_w**

This captures "the portion of M_i's knowledge allowing it to follow complex instructions" and transfers it at negligible CPU cost.

### 11.2 Results

| Model | Language | Benchmark | Pre-trained (PT) | +Diff | Δ |
|-------|----------|-----------|:-:|:-:|:-:|
| Qwen 2.5 Coder 32B | Gleam | HumanEval | 32.99 | **56.23** | ▲ 23.24 |
| | | MBPP | 47.35 | **53.83** | ▲ 6.48 |
| | | McEval-Hard | 12.47 | **26.08** | ▲ 13.61 |
| Qwen 2.5 Coder 32B | MoonBit | HumanEval | 41.62 | **50.71** | ▲ 9.09 |
| | | MBPP | 44.76 | **53.04** | ▲ 8.28 |
| | | McEval-Hard | 25.86 | **32.60** | ▲ 6.74 |
| Qwen 3 8B | Gleam | HumanEval | 18.57 | **51.88** | ▲ 33.31 |
| | | MBPP | 23.63 | **50.48** | ▲ 26.85 |
| | | McEval-Hard | 4.36 | **22.33** | ▲ 17.97 |
| Qwen 3 8B | MoonBit | HumanEval | 36.82 | **44.42** | ▲ 7.60 |
| | | MBPP | 42.08 | **45.27** | ▲ 3.19 |
| | | McEval-Hard | 19.87 | 19.82 | ▼ 0.05 |

### 11.3 Key Findings

1. **Consistent improvement**: All but one case show significant improvement (avg +12%)
2. **OR range**: 1.21 to 10.95, all statistically significant
3. **Larger gains on Gleam** than MoonBit (more room for improvement after pre-training)
4. **Generalizes across**: model sizes (8B, 32B), types (code-specialized, general-purpose), with/without reasoning
5. **Small model outperforms large**: Qwen 3 8B + Diff outperforms Qwen 3 32B Instruct fine-tuned (avg +12% improvement, up to +28% on Gleam HumanEval)
6. **Only non-significant case**: Qwen 3 8B + Diff on MoonBit McEval-Hard (19.87 vs 19.82)

---

## 12. Upper Bound Analysis (Prompt Engineering)

The authors tested a "manual" (prompt engineered to include all relevant language documentation) as an approximate upper bound for in-context learning:

| Language | Benchmark | Manual | Instruction Transfer | Gap |
|----------|-----------|:------:|:-------------------:|:---:|
| Gleam | HumanEval | 15.58 | 56.23 | 40.65 |
| | MBPP | 25.07 | 53.83 | 28.76 |
| | McEval-Hard | 1.76 | 26.08 | 24.32 |
| MoonBit | HumanEval | 32.47 | 50.71 | 18.24 |
| | MBPP | 39.44 | 53.04 | 13.60 |
| | McEval-Hard | 6.61 | 32.60 | 26.00 |

The manual approach was competitive with fine-tuning on easy tasks but dramatically underperformed weight diff transfer on McEval-Hard.

---

## 13. Data Quality Assessment

### 13.1 Fine-Tuning Dataset Quality

Manual validation (374 Gleam + 333 MoonBit samples, 95% confidence ±5%):
- **Content adequacy**: Median 5/5, avg >4.3
- **Conciseness**: Median 5/5, avg >4.3
- **Fluency & understandability**: Median 5/5, avg >4.3
- Inter-rater agreement: Krippendorff α = 0.69 (substantial), 0.48 (moderate), 0.65 (substantial)

### 13.2 Benchmark Translation Quality

Manual check of 346 translated tasks:
- 14 prompts (4%) with issues (inherited errors, typos, missing type info)
- 2 tests (0.6%) with issues (binary/hex literal conversion)
- Comparable to known issues in SWE-Bench (6.4% inflated rates)

---

## 14. Syntactic vs Semantic Error Analysis

### 14.1 Zero-Shot Setting

- **No-resource languages**: ~2/3 failures are **syntactic** (up to 90% for o3-mini on Gleam)
- **High/low-resource languages**: <10% syntactic failures
- **Java exception**: ~30% syntactic failures (due to verbosity)

### 14.2 Effect of Techniques

| Technique | Impact on Syntax Errors |
|-----------|------------------------|
| Few-shot | -15.36% reduction |
| RAG | -8.94% reduction |
| Fine-tuning | Substantial reduction (<20% syntax failures) |
| Pre-training | Substantial reduction (<20% syntax failures) |
| Instruction Transfer (32B) | -24.1% (Gleam), -73.5% (MoonBit) — further reduction |
| Instruction Transfer (8B) | +13.3% (Gleam), +241.6% (MoonBit) — more syntax but fewer semantic errors |

The 8B model's increase in syntactic errors with instruction transfer is attributed to **limited model capacity** reallocating toward instruction following and semantic reasoning.

---

## 15. Limitations

### 15.1 Methodological

1. **No hyperparameter tuning**: Used default configurations to save compute
2. **In-context learning limitations**: Retrieved context may not capture all necessary language features
3. **Constrained decoding not tested**: Could mitigate syntactic errors at inference time
4. **Computational cost**: The manual upper-bound experiment required ~340 man-hours

### 15.2 Assumptions

1. **Data contamination**: Cannot fully verify that LLMs haven't seen Gleam/MoonBit code (though language timelines suggest limited exposure)
2. **Language cutoffs**: Training data composition not fully known for closed models

### 15.3 Generalizability

1. **9 languages, 6 LLMs, 3 benchmarks**: May not generalize to other settings
2. **Function-level tasks only**: Does not cover debugging, refactoring, or real-world issue resolution
3. **Domain specificity**: Gleam optimized for distributed systems, MoonBit is general-purpose; findings may not transfer to all no-resource languages
4. **Language evolution**: Both languages are rapidly evolving (e.g., MoonBit virtual packages May 2025)

---

## 16. Future Work

1. **Expand benchmarks** to cover more diverse real-world use cases:
   - Debugging tasks
   - Refactoring tasks
   - Code generation for entire change requests
2. **Constrained decoding techniques**: Enforce grammar rules at inference time
3. **Domain-specific tasks**: Test on the specific domains where these languages are used
4. **Hyperparameter optimization**: Explore impact of different training configurations

---

## 17. Practical Implications

**For companies with proprietary languages:**
1. Collect as much code as possible (even without docstrings)
2. Further pre-train a base model (not instruct) on the language
3. Use weight diff transfer from the instruct version to recover instruction following
4. This approach is **computationally cheap** (CPU-only for the diff step)
5. **Smaller models with weight transfer** can outperform 4× larger fine-tuned models

---

## 18. Claim Index

| Claim ID | Section | Summary | Evidence |
|----------|---------|---------|----------|
| C1.1 | Abstract | No-resource languages remain largely unstudied | Prior work survey |
| C1.2 | Abstract | Further pre-training gives largest gains but harms instruction-following | Experimental results, RQ2 |
| C1.3 | Abstract | Weight diff transfer significantly improves performance | RQ3 results |
| C2.1 | II-A1 | Gleam and MoonBit have at least 1 order of magnitude fewer repos than Racket | Table I |
| C2.2 | II-A1 | Before Mar 2024: only 560 Gleam and 7 MoonBit repos existed | Data from GitHub |
| C3.1 | III | LLMs achieve 59-89% pass@1 on high-resource, 27-84% on low-resource, 0-1% on no-resource (McEval-Hard) | Table IV |
| C3.2 | III | Low-resource language performance not solely determined by popularity | Lua vs R comparison |
| C3.3 | III | ~2/3 of failures on no-resource are syntactic errors | Failure analysis |
| C3.4 | III | <10% of failures on high/low-resource are syntactic (except Java ~30%) | Failure analysis |
| C4.1 | III (RQ2) | Few-shot is slightly more effective than RAG | Table V, 7/12 and 8/12 cases |
| C4.2 | III (RQ2) | Fine-tuning > in-context learning | Table V |
| C4.3 | III (RQ2) | Pre-training > fine-tuning for the same architecture | Qwen 2.5 Coder 32B comparison |
| C4.4 | III (RQ2) | Pre-training benefits from more available data (code + docs vs functions only) | Table III |
| C4.5 | IV (RQ3) | Instruction transferring provides consistent significant improvement (avg +12%) | Table VI |
| C4.6 | IV (RQ3) | Qwen 3 8B + Diff outperforms Qwen 3 32B Instruct fine-tuned | Table V vs VI |
| C4.7 | IV (RQ3) | Instruction transfer generalizes across sizes, types, and reasoning capabilities | Qwen 2.5 Coder and Qwen 3 |
| C5.1 | V-C | 4% of translated prompts had issues, 0.6% of tests | Manual validation |
| C5.2 | V-C | Fine-tuning datasets have high quality (median 5/5) | Human evaluation |
| C6.1 | VII | ~340 man-hours for benchmark creation | Author report |

---

## 19. Personal Evaluation

### Strengths

1. **Timely and practical problem**: Industrial relevance is high — many companies face exactly this need
2. **Rigorous empirical methodology**: 264,960+ generations across 9 languages, 6 LLMs, 3 benchmarks
3. **Comprehensive technique comparison**: Covers in-context learning, fine-tuning, pre-training, and weight transfer
4. **Novel application of weight diff transfer**: First application to code generation for no-resource languages
5. **Public benchmarks**: Enables future research (NoResourceCode)
6. **Data quality assurance**: Extensive manual validation of benchmarks and fine-tuning datasets
7. **Small model efficiency**: Demonstrating 8B + transfer outperforming 32B fine-tuned is practically significant

### Weaknesses

1. **Only 2 no-resource languages**: Both relatively new general-purpose languages; results may differ for DSLs or older niche languages
2. **Function-level benchmarks only**: Does not address more realistic scenarios like bug fixing or feature implementation
3. **Single architecture tested for weight transfer**: Only Qwen models used (open-weight requirement)
4. **No constrained decoding experiments**: Acknowledged but not tested
5. **Manual effort not scalable**: ~340 hours for benchmark creation; the method doesn't scale easily
6. **No comparison to RLHF/DPO**: Alternative approaches for instruction tuning after pre-training not explored
7. **Gleam/MoonBit may not be truly "zero-resource"**: The 0-1% McEval-Hard scores suggest near-zero exposure, but ≥10% on easier tasks suggests some generalization from similar languages

### Overall Assessment

A solid, well-executed empirical study that addresses a practical problem with rigorous methodology. The weight diff transfer approach is elegant and practically valuable. The main limitation is the narrow scope (2 languages, function-level tasks) — but this is acknowledged and frames clear future work.

**Rating**: ★★★★☆ (4/5) — Strong empirical contribution with practical impact, limited by scope and single architecture testing.

---

## 20. References (Key)

1. Cassano et al., "MultiPL-E: A Scalable and Polyglot Approach to Benchmarking Neural Code Generation," TSE 2023
2. Cassano et al., "Knowledge Transfer from High-Resource to Low-Resource Programming Languages for Code LLMs," OOPSLA 2024
3. Jindal et al., "Balancing Continuous Pre-Training and Instruction Fine-Tuning," arXiv 2024
4. Lin et al., "Efficient Model Development Through Fine-Tuning Transfer," arXiv 2025
5. Giagnorio et al., "Enhancing Code Generation for Low-Resource Languages: No Silver Bullet," ICPC 2025
6. Chai et al., "McEval: Massively Multilingual Code Evaluation," ICLR 2025
7. Paul et al., "IRCoder: Intermediate Representations Make Language Models Robust Multilingual Code Generators," ACL 2024
