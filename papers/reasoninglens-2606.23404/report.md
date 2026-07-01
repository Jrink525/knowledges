# ReasoningLens: Hierarchical Visualization and Diagnostic Auditing for Large Reasoning Models

**arXiv**: 2606.23404 | **Date**: June 22, 2026 | **Authors**: Jun Zhang, Jiasheng Zheng, Boxi Cao, Yaojie Lu, Hongyu Lin, Jia Zheng, Xianpei Han, Le Sun (Chinese Information Processing Laboratory, Institute of Software, CAS)

---

## 1. Paper Metadata

- **Venue**: arXiv preprint (cs.CL)
- **Slug**: reasoninglens
- **Code**: https://github.com/icip-cas/ReasoningLens
- **Dataset**: https://hf.co/datasets/LasRuinasCirculares/LensBench
- **Demo**: https://youtu.be/sVZ8yYrpCYk
- **Length**: 10 pages, 4 figures, 1 table

---

## 2. The Problem: Transparency Burden of Long CoT

Large Reasoning Models (LRMs) such as Deepseek-R1, GPT-5, and Qwen3 generate exceptionally long Chain-of-Thought (CoT) traces — often tens of thousands of tokens. This introduces a **structural trade-off between expressiveness and interpretability**:

- Critical logical dependencies are buried under massive procedural text ("walls of text")
- Manual inspection becomes prohibitively difficult
- Error diagnosis and safety assurance are significantly challenged
- Prior visualization tools remain heuristic, superficial, and lack a diagnostic framework

The paper frames this as a **transparency burden** — the scaling of reasoning length does not merely increase volume, but actively obscures the meaningful structure that researchers need to audit.

---

## 3. The Gap: Prior Work and Its Limitations

Section 2 maps the related landscape into two streams:

**Error Analysis:** Prior work identifies failure modes (overthinking, safety leakage, logical inconsistencies) and process reward model evaluations, but taxonomies are **limited to reasoning failures in math/coding** and lack a holistic taxonomy across pathological behaviors.

**Visualization Systems:** Tools like Reasongraph, Interactive Reasoning, Retrace, and ReasoningFlow render CoT as graphical interfaces to reduce cognitive load, but they:
- Rely on **superficial text rendering** without capturing underlying reasoning structures
- Provide **no diagnostic capability** — they show, but don't analyze
- Remain **heuristic and descriptive** rather than principled

The key gap: no existing work provides a **unified framework combining structured modeling with automated diagnosis**.

---

## 4. Core Contribution

ReasoningLens reframes long CoT analysis from **passive observation** to **active, structured interpretation** through three pillars:

1. **Hierarchical Visualization** — Multi-granularity reasoning graphs separating high-level strategy from low-level execution
2. **Agentic Diagnosis** — Multi-agent system for automated error detection with tool-augmented verification
3. **Systemic Profiling** — Cross-trajectory behavioral modeling to reveal model-specific blind spots

Plus the release of **LENSBENCH**, a benchmark of 130 instances with gold annotations for both trace structure and reasoning errors.

---

## 5. The Research Equation

> **Given**: Unstructured long CoT traces from LRMs
> **Approach**: Taxonomy-guided hierarchical parsing → multi-agent diagnosis → cross-trajectory profiling
> **Validate**: LENSBENCH benchmark with 5 backbone models spanning families and scales
> **Measure**: NTA + GES (structuring); P/R/F1 (error diagnosis)
> **Goal**: Turn opaque reasoning walls of text into auditable, actionable insights

---

## 6. The Reasoning Behavior Taxonomy (Core Design)

The taxonomy is the foundation of the entire framework. It organizes reasoning behaviors into **two levels**:

### Exploration-Level (High-level strategic moves)
1. **Decomposition** — Divide-and-conquer; partitions complex problems into atomic sub-goals; expands a linear path into a tree
2. **Backtracking** — Failure-triggered; prunes failed branches and resumes from prior decision points
3. **Validation** — Self-correction mechanism; introduces verification loops before committing to a path

### Exploitation-Level (Low-level procedural execution)
1. **Knowledge Retrieval** — Extracts task-relevant priors from parametric memory or context
2. **Procedural Execution** — Rule-governed transformations over instantiated inputs
3. **State Assertion** — Commits local assumptions or intermediate findings into working state

This taxonomy directly mirrors cognitive science concepts of exploration (search over solution space) and exploitation (local optima refinement), giving the framework theoretical grounding beyond ad-hoc engineering.

---

## 7. The Error Taxonomy (Five Categories)

1. **Overthinking** — Redundant reasoning cycles (repeated verification, circular loops, over-elaboration)
2. **Safety** — Harmful content generation risk, toxicity, bias, sensitive information leakage
3. **Knowledge Error** — Incorrect recall or misuse of established knowledge, factual hallucinations
4. **Logical Error** — Flawed reasoning strategies, non-sequiturs, internal contradictions
5. **Formal Error** — Non-compliance with symbolic rules (syntax, LaTeX, arithmetic) in programming/math contexts

---

## 8. System Architecture Overview

ReasoningLens is composed of three tightly integrated components:

```
Raw Long CoT Trace
    │
    ▼
┌─────────────────────────────────────────────┐
│ 1. Hierarchical Visualization               │
│    ├─ Planning Unit Extraction (lexical cues)│
│    ├─ Exploration-Level Graph (macro-nodes) │
│    └─ Exploitation-Level Subgraph (micro)   │
└──────────┬──────────────────────────────────┘
           ▼
┌─────────────────────────────────────────────┐
│ 2. Agentic Diagnosis                        │
│    ├─ Memory Module (incremental inspection)│
│    ├─ Verification Module (tool invocation) │
│    └─ Suggestion Module (fix strategies)    │
└──────────┬──────────────────────────────────┘
           ▼
┌─────────────────────────────────────────────┐
│ 3. Systemic Profiling                       │
│    ├─ Shared representation (tree artifacts)│
│    ├─ Semantic deduplication                │
│    └─ Model-level profile (3 axes)          │
└─────────────────────────────────────────────┘
```

---

## 9. Hierarchical Visualization — Detailed Design

### Planning Unit Extraction
CoT traces are segmented into **atomic planning units** — minimal semantically coherent segments. The segmentation leverages **decision-oriented lexical cues** (e.g., "but", "wait", "alternatively", "try another approach") to identify strategy transitions.

### Exploration-Level Graph (Macro)
The unit sequence S = (u₁, …, u_N) is abstracted into a macro-level graph G_macro = (V_macro, E_macro). An LLM partitions S into M disjoint contiguous spans, each collapsed into a macro-node v_j with a functional role from T^macro_V (e.g., problem decomposition, validation, intermediate answer). Structural edges T^macro_E (forward reasoning, backtracking, detached verification) connect them into a tree-structured hierarchy.

### Exploitation-Level Subgraph (Micro)
Each macro-node v_j spanning (u_i, …, u_{i+k}) is further refined into a local execution subgraph of micro-nodes. Each micro-node is labeled with an execution behavior from T^micro_V, connected by micro-edges T^micro_E encoding procedural dependencies.

This two-level design is the key innovation: it provides **tunable granularity** — researchers can zoom between strategic overview and line-by-line execution.

---

## 10. Agentic Diagnosis — Detailed Design

### The Multi-Agent Framework
Three core modules:

**Memory Module:** Incrementally inspects the CoT through memory compression. Enables granular localization of local errors while preserving trace-level consistency. Prevents the "lost in the middle" problem common in long-context processing.

**Verification Module:** Strategically leverages **external tool invocations** to resolve internal ambiguity. This is a crucial design choice — rather than relying purely on the model's internal knowledge for verification, the system can call code executors, calculators, or knowledge bases for precise verification.

**Suggestion Module:** Closes the analytical loop by generating **actionable mitigation strategies** mapped to specific error types. Maintains a curated repository of two paradigms:
- **Training-free approaches** (prompt engineering, early stopping, temperature control)
- **Post-training techniques** (RL-based alignment, supervised fine-tuning)

### Contribution
The agentic framework shifts the paradigm from **passive observation** (just visualizing) to **active diagnostic intervention**.

---

## 11. Systemic Profiling — Detailed Design

This module lifts analysis from **instance-level to model-level**.

**Pipeline:**
1. Tree-structured artifacts and failure signals from multiple trajectories are mapped into a shared representation
2. Global invariants are extracted: search topology (backtracking distributions), node-level annotations (error types)
3. LLM-driven **semantic deduplication** compresses similar reasoning paths while preserving distinct heuristic features
4. Final structured model-level profile synthesized along **three axes**:
   - **Exploration habits** — depth–breadth trade-offs in strategy search
   - **Verification reliability** — self-correction consistency across problems
   - **Stability bottlenecks** — high-variance logical structures prone to failure

This enables **interpretable model comparison** (e.g., DeepSeek-V4-Pro vs Qwen3-32B on exploration-exploitation balance) and **principled iterative optimization**.

---

## 12. LENSBENCH Benchmark — Construction

**Source:** Mixture-of-Thoughts (Fein-Ashley et al., 2025), a public long-CoT benchmark

**Filtering criteria:**
- ≥10 planning units (sufficient reasoning complexity)
- No mixed-language traces
- Clean traces (no pre-existing reasoning errors, filtered by GPT-5.4)

**Trace Structuring Annotation:** GPT-5.4 annotates exploration-level structure per the reasoning behavior taxonomy

**Error Injection:** Since naturally occurring errors are heavily imbalanced, controlled taxonomy-guided errors are injected:
- GPT-5.4 identifies plausible insertion points
- Selects compatible failure types
- Rewrites targeted spans for globally coherent injection

**Human Verification:** All 130 instances manually reviewed with strict criteria:
- Coherent rewrites (no surface cues exposing injection)
- Unambiguous single-category error identification
- Informative and non-redundant error composition
- Valid structure: non-overlapping nodes, plausible progression, textually-supported edges

Final dataset: **130 verified examples** with gold annotations for both evaluation dimensions.

---

## 13. Experimental Setup

**Backbone Evaluators** (5 models, diverse families and scales):
| Model | Family | Scale |
|-------|--------|-------|
| DeepSeek-V4-Pro | DeepSeek | Largest |
| MiniMax-M2.7 | MiniMax | Large |
| Qwen3.5-27B | Qwen | 27B |
| Gemma-4-26B-A4B | Google | 26B (4B active) |
| Qwen3-32B | Qwen | 32B |

**Metrics:**
- **Trace Structuring:** Node Type Accuracy (NTA) + Graph Edit Similarity (GES)
- **Error Diagnosis:** Per-type and micro-averaged Precision, Recall, F1

**NTA Definition:** Predicted nodes matched to gold by section IoU (≥0.5 threshold), greedy matching, checking type correctness.

**GES Definition:** Graph edit distance with unit costs, normalized by total nodes+edges.

---

## 14. Main Results — Agentic Diagnosis

**Overall Performance (micro-averaged F1):** 66.3 (Qwen3-32B) to 82.3 (DeepSeek-V4-Pro)

**Key findings by error category:**

| Error Type | Best Model (F1) | Worst Model (F1) | Observation |
|-----------|-----------------|------------------|-------------|
| **Safety** | DeepSeek-V4-Pro (98.5) | Qwen3-32B (89.9) | Consistently high across all models |
| **Overthinking** | MiniMax-M2.7 (87.2) | Qwen3.5-27B (80.6) | All models reasonably detect |
| **Formal Error** | DeepSeek-V4-Pro (86.0) | Qwen3-32B (46.2) | Wide variance |
| **Knowledge Error** | DeepSeek-V4-Pro (65.1) | Qwen3-32B (39.0) | Strong model-dependent |
| **Logical Error** | DeepSeek-V4-Pro (60.3) | Qwen3-32B (34.6) | Most challenging, strongly model-dependent |

**Key insight:** Safety detection is robust across all models (safety alignment has effectively reinforced boundaries). In contrast, Knowledge and Logical error detection **depends heavily on the backbone model's reasoning capacity** — confirming that diagnosing deeper reasoning failures is a metacognitive task that scales with model capability.

---

## 15. Main Results — Hierarchical Visualization

**NTA (Node Type Accuracy):** 70.9–79.5 across models (mean ~75.0)
**GES (Graph Edit Similarity):** 68.0–72.3 across models (mean ~69.7)

**Key insight:** The visualization module is **consistently robust across model scales**. Despite substantial variation in diagnostic F1 (66.3→82.3), trace structuring remains stable. The paper attributes this to the design choice of segmenting raw reasoning into locally-scoped planning units, which converts long-context understanding into a simpler labeling task — reducing backbone model burden.

**This validates the hierarchical visualization design as a robust component independent of backbone choice.**

---

## 16. Case Analysis — What Gets Revealed

A detailed case study on Qwen3-32B shows ReasoningLens:

1. **Decomposes** the reasoning trajectory into semantically coherent functional blocks (e.g., Strategy Shift, Verification)
2. **Aligns well** with human-annotated ground truth structural nodes
3. **Surfaces** critical vulnerabilities otherwise obscured by verbosity:
   - Unsafe manipulation tactics
   - Redundant overthinking
4. **Associates** each error with targeted remediation strategies (e.g., Early Stopping) in the "How to fix" panel

This closes the loop between **latent reasoning analysis and model alignment**.

---

## 17. Claims and Their Evidence

| # | Claim | Evidence Source | Strength |
|---|-------|----------------|----------|
| C1 | Long CoT creates transparency burden | Prior citations + framing (Turpin et al., Chen et al., Arcuschin et al.) | Well-supported by literature |
| C2 | Prior visualization tools are heuristic/descriptive | Literature review (Reasongraph, Interactive Reasoning, Retrace) | Valid gap analysis |
| C3 | Hierarchical taxonomy captures reasoning behavior comprehensively | Design description + experimental validation | Supported by stable NTA/GES |
| C4 | Two-level (exploration + exploitation) separation is effective | Consistent NTA/GES across models | Strong evidence |
| C5 | Agentic diagnosis achieves reliable error detection | LENSBENCH results, F1 66.3–82.3 | Supported but backbone-dependent |
| C6 | Safety detection is near-universally robust | All models ≥89.9 Safety F1 | Very strong evidence |
| C7 | Knowledge and Logical error detection is model-dependent | 39.0 vs 65.1 Knowledge F1, 34.6 vs 60.3 Logical F1 | Strong evidence |
| C8 | Visualization module is robust independent of backbone | NTA 70.9–79.5, GES 68.0–72.3 | Strong evidence |
| C9 | Systemic profiling enables model comparison | Framework design described | No experimental validation in current paper |
| C10 | LENSBENCH provides high-quality annotations | Human verification protocol described | Reasonable, but N=130 is small |

---

## 18. Strengths

1. **Principled framework design** — The two-level taxonomy (exploration/exploitation) is theoretically grounded and practically useful, mapping well to cognitive science concepts
2. **End-to-end pipeline** — From raw CoT to actionable insights, with three well-defined stages (visualize → diagnose → profile)
3. **Human-verified benchmark** — LENSBENCH uses rigorous manual review with explicit criteria (Appendix B)
4. **Replicable** — Open-source code, benchmark, and demo video all publicly released
5. **Multiple backbone evaluation** — 5 models across families and scales strengthens generalizability claims
6. **Agentic architecture with tool-use** — The verification module's external tool invocation is a pragmatic design choice that grounds diagnosis
7. **Practical contribution** — Actionable fix suggestions bridge analysis to remediation

---

## 19. Weaknesses and Limitations

1. **Small benchmark (N=130)** — For 5 error types × 2 evaluation dimensions, 130 instances is relatively small, potentially limiting statistical power
2. **Static traces only** — The paper explicitly acknowledges this: the framework currently handles static CoT traces, not dynamic multi-step agentic interactions
3. **Artificially injected errors** — LENSBENCH uses GPT-5.4 to inject errors into clean traces. While necessary for balanced evaluation, injected errors may not perfectly reflect naturally occurring failures
4. **Single backbone for annotation** — GPT-5.4 is used for both trace structuring annotation and error injection, potentially encoding systematic biases
5. **Systemic Profiling unvalidated** — The profiling module is described but has no dedicated experimental evaluation in the current paper
6. **Monolithic deployment** — The system currently runs as a monolithic pipeline without modular plugin architecture
7. **Error taxonomy completeness** — While five categories are identified, some reasoning failures may span multiple categories or fall outside the taxonomy entirely

---

## 20. Comparison to Related Work

| System | Visualization | Diagnosis | Profiling | Open-Source |
|--------|--------------|-----------|-----------|-------------|
| Reasongraph (Li et al.) | ✅ Graphical | ❌ | ❌ | ✅ |
| Interactive Reasoning (Pang et al.) | ✅ Interactive | ❌ | ❌ | ❌ |
| Retrace (Felder et al.) | ✅ Interactive | ❌ | ❌ | ✅ |
| ReasoningFlow (Lee et al.) | ✅ Structural | ❌ | ❌ | ❌ |
| **ReasoningLens (this work)** | ✅ **Hierarchical** | ✅ **Agentic** | ✅ **Systemic** | ✅ |

ReasoningLens is unique in combining all three capabilities: structural visualization, automated diagnosis, and cross-trajectory profiling.

---

## 21. Broader Significance

The paper addresses a **fundamental tension** in scaling reasoning AI: as models think more, they become harder to audit. ReasoningLens's answer is not to reduce thinking, but to **structure it** — making extended chains of reasoning inspectable, debuggable, and improvable within the same framework.

This has implications beyond research:
- **Safety evaluation:** The Safety error detection (≥89.9 F1 across all models) demonstrates structured analysis can aid red-teaming
- **Model alignment:** Closing the loop between error diagnosis and fix suggestions enables continuous improvement
- **Process supervision:** The authors explicitly mention future deployment for process-based training supervision
- **Transparency regulation:** As AI governance frameworks demand explainability, tools like ReasoningLens operationalize transparency

---

## 22. Future Directions (Explicit + Inferred)

**Explicit (from Section 6):**
1. **Agentic trajectory analysis** — Extend beyond static CoT to Plan-Act-Observe cycles
2. **Modular plugin ecosystem** — Lightweight integration for process-based training supervision

**Inferred:**
3. **Scalable N** — Larger benchmark beyond 130 instances
4. **Cross-model comparison** — Use systemic profiling for principled model ranking
5. **Real-time monitoring** — Apply diagnosis during inference for runtime guardrailing
6. **Multi-language support** — Extend taxonomy and parsing beyond English

---

## 23. Technical Depth Assessment

The paper provides substantial technical depth for the visualization and diagnosis modules:
- Explicit definitions of NTA and GES with mathematical formulations
- Detailed human verification protocol (Appendix B)
- Complete annotated example (Appendix C, including JSON schema)
- Well-described taxonomy of reasoning behaviors and errors

Areas where depth could improve:
- The Systemic Profiling module lacks experimental validation
- Ablation studies (e.g., with/without tool-augmented verification) are absent
- Sensitivity analysis on lexical cue thresholds for planning unit extraction

---

## 24. Readability and Accessibility

The paper is well-structured with clear sectioning, but:
- **Dense abstractions** — The introduction is heavy on high-level framing, and some prose could be more concrete
- **Visual reasoning** — The paper relies heavily on figures (Figures 1-4) which are described but not fully accessible in text
- **Technical rigor** — The appendices (A-C) provide needed detail that helps ground the claims
- **Code release** — The open-source repository is a significant accessibility contribution

---

## 25. Final Verdict

| Dimension | Rating (1-10) | Notes |
|-----------|--------------|-------|
| **Problem Significance** | 9 | Transparency burden is a critical problem as LRMs scale |
| **Novelty** | 8 | First unified framework combining visualization + diagnosis + profiling |
| **Technical Soundness** | 7 | Solid for visualization/diagnosis; profiling lacks experimental validation |
| **Empirical Validation** | 6 | N=130, single annotation backbone, no systemic profiling experiments |
| **Reproducibility** | 9 | Open-source code, dataset, and demo released |
| **Practical Impact** | 8 | Directly applicable to model debugging, safety evaluation, alignment |
| **Presentation** | 7 | Well-structured but dense; relies heavily on figures |
| **Overall** | **7.7** | Significant contribution to LRM interpretability, with clear paths for extension |

---

*Report generated by ReasoningLens deep-read agent. arXiv:2606.23404.*
