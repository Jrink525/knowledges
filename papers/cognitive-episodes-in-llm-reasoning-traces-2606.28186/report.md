# Cognitive Episodes in LLM Reasoning Traces Enable Interpretable Human Item Difficulty Prediction

**Authors**: Chenguang Wang, Ming Li, Xinyue Zeng, Zhuochun Li, Hong Jiao, Tianyi Zhou, Dawei Zhou  
**Affiliations**: Virginia Tech, University of Maryland, MBZUAI, University of Pittsburgh  
**arXiv**: 2606.28186  
**Code**: https://github.com/c-steve-wang/Epi2Diff

---

## 1. Problem Statement

Predicting human item difficulty is a central challenge in educational assessment. Accurate difficulty estimates are critical for fairness, test construction, and precise measurement along the ability scale. Traditional approaches rely on costly human calibration (pretesting) under Classical Test Theory (CTT) and Item Response Theory (IRT), which are time-consuming and difficult to scale. Automated alternatives exist, but they generally treat difficulty as a property of item text alone, offering limited interpretable evidence about the **cognitive processes** that make an item difficult.

The core thesis of this paper: *Item difficulty should be viewed not only as a property of item text, but also as an observable consequence of the problem-solving burden induced by the item.* Large Reasoning Models (LRMs) offer scalable process evidence through their explicit reasoning traces, but raw traces are long, redundant, and noisy — they must be structured to support interpretable modeling.

---

## 2. Research Gap & Motivation

**Gap 1: Costly human calibration.** CTT/IRT require extensive field testing. Expert judgment has limited agreement with empirical difficulty.

**Gap 2: Text-only representations miss process.** Existing text-based models (feature-based or end-to-end fine-tuned SLMs/LLMs) model difficulty from item text, metadata, or embeddings — not from the solving process itself.

**Gap 3: LLM direct judgments are unreliable.** Prior work shows that strong item-solving ability does not translate to accurate human difficulty estimates (Li et al., 2025a). Direct LLM ratings reflect model-centric rather than human-centric difficulty.

**Gap 4: Raw reasoning traces are noisy.** Directly feeding LRM reasoning traces into predictors introduces irrelevant information and can degrade performance (Fulari & Rusert, 2024; Tack et al., 2024). Richer ≠ better.

**Central question:** *How can explicit LRM reasoning processes be transformed into a structured and informative representation for modeling item difficulty?*

---

## 3. Background & Related Work

### 3.1 Item Difficulty Prediction (Appendix A.1)

Evolution from hand-crafted linguistic features (Perkins et al., 1995; Loukina et al., 2016) → Word2Vec (Hsu et al., 2018) → CNN (He et al., 2021) → BERT/RoBERTa (McCarthy et al., 2021; Benedetto, 2023). These models rely on item text only, leaving process-level solving burden unexplored.

### 3.2 LLM-Based Methods for Difficulty Prediction (Appendix A.2)

Recent approaches use LLMs for: zero-shot difficulty rating, answer variability signals (Rogoz & Ionescu, 2024), simulated examinee responses (Dueñas et al., 2024), uncertainty signals (Zotos et al., 2024), LLM-extracted cognitive features (Razavi & Powers, 2025), and fine-tuned representations (Li et al., 2025c). These methods treat LLM outputs as predictive cues without grounding them in interpretable process evidence.

### 3.3 Reasoning Traces as Process Signals (Appendix A.3)

Chain-of-thought (Wei et al., 2022) and reasoning-oriented models (DeepSeek-R1, QwQ, Qwen3) produce long, human-readable traces. Prior work on reasoning efficiency shows that effective reasoning is not reducible to response length (Chen et al., 2024; Feng et al., 2025b). Li et al. (2025d) applied Schoenfeld's Episode Theory to model traces. However, no prior work uses reasoning traces as structured predictive signals for human item difficulty.

---

## 4. Theoretical Foundation: Schoenfeld's Episode Theory

The paper grounds its approach in **Schoenfeld's Episode Theory** (Schoenfeld, 2014, 2016), which models problem-solving as a temporally ordered sequence of functional episodes:

| Episode | Description |
|---------|-------------|
| **Read** | Initial reading/understanding of the problem |
| **Analyze** | Breaking down the problem, identifying key information |
| **Plan** | Strategic planning and solution design |
| **Implement** | Executing the planned solution steps |
| **Explore** | Exploring alternative approaches or uncertain paths |
| **Verify** | Checking correctness, backtracking, verifying |
| **Monitor** | Meta-cognitive monitoring of progress |
| **Answer** | Final answer commitment (added from ThinkARM; Li et al., 2025b) |

This 8-way taxonomy provides a cognitively grounded vocabulary for characterizing how problem-solving burden is distributed across different stages of long reasoning traces.

---

## 5. Method: Epi2Diff (Episode to Difficulty)

Epi2Diff is a framework with five components:

### 5.1 Overview

```
Item Text → [LRM Reasoning Traces] → [Sentence-Level Episode Profiling]
           → [Episode-Induced Process Features]
           + [Sentence-BERT Semantic Embedding]
           → [Joint Representation] → [XGBoost Predictor] → Difficulty
```

### 5.2 Step 1: LRM Reasoning Trace Generation

For each item, the framework queries two LRMs (QwQ-32B and Qwen3-32B) under **four simulated student profiles**: direct (the model's own reasoning), weak, medium, and strong. This produces 8 reasoning traces per item (2 LRMs × 4 profiles).

### 5.3 Step 2: Sentence-Level Episode Profiling

A **RoBERTa-based sentence classifier** is trained on a cleaned corpus of 231,913 labeled sentence–episode pairs from ThinkARM (Li et al., 2025b), which uses GPT-5 annotations with a human-verified gold set of 7,067 sentences. The classifier achieves:
- Accuracy: 0.799
- Macro-F1: 0.761
- Micro-F1: 0.799

Each reasoning trace sentence is classified into one of the 8 episode types.

### 5.4 Step 3: Episode-Induced Process Representation

Three complementary feature groups (83 dimensions total):

**(a) Length Features (3 dims):**
- Total token length of the trace
- Token length of the 'thinking' part
- Token length of the 'answer' part

**(b) Episode-Distribution Features (16 dims):**
- 8 episode **count** features (absolute token allocation per episode)
- 8 episode **ratio** features (relative allocation normalized by total)

**(c) Transition Features (64 dims):**
- 8×8 adjacency matrix of bigram counts (how often episode e is immediately followed by episode e′)

These features capture **scale** (length), **allocation** (episode distribution), and **flow** (transitions).

### 5.5 Step 4: Multi-Profile Aggregation

Process representations are averaged across all 4 simulated student profiles (direct, weak, medium, strong) and optionally across the 2 LRM sources. The final representation concatenates the averaged process vector with a Sentence-BERT semantic embedding.

### 5.6 Step 5: Supervised Predictor

XGBoost is selected via validation across candidate models (Logistic Regression, Random Forest, XGBoost). Classification uses cross-entropy loss; regression uses MSE.

---

## 6. Experimental Setup

### 6.1 Datasets

| Dataset | Domain | Items | Task | Difficulty Scale |
|---------|--------|-------|------|-----------------|
| **SAT Math** | Mathematical reasoning | 1,075 | 3-class classification | Easy/Medium/Hard |
| **SAT Reading & Writing** | Verbal reasoning | 1,338 | 3-class classification | Easy/Medium/Hard |
| **Cambridge** | English reading comprehension | 793 | Regression | IRT b-parameters (0–100) |
| **USMLE** | Medical assessment | 667 | Regression | Transformed p-values (0–1.3) |

### 6.2 Baselines (5 Paradigms)

1. **SLM Fine-tuning**: BERT, RoBERTa, ModernBERT, ELECTRA
2. **LLM Zero-shot**: GPT-4o, GPT-5, QwQ-32B, Qwen3-32B
3. **LLM In-Context Learning**: 3-shot and 5-shot variants of the above
4. **LLM Supervised Fine-tuning (Full)**: Qwen2.5-3B, Qwen3-4B, Phi-3.5-mini, Phi-4-mini, Llama3.2-3B
5. **LLM Supervised Fine-tuning (LoRA)**: Same models, rank 16

---

## 7. Main Results

| Method | SAT Math ACC↑ | SAT Math F1↑ | SAT Reading ACC↑ | SAT Reading F1↑ | Cambridge RMSE↓ | Cambridge R²↑ | USMLE RMSE↓ | USMLE R²↑ |
|--------|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|
| Best SLM | 0.637 | 0.643 | 0.623 | 0.622 | 8.200 | 0.299 | 0.298 | 0.076 |
| Best LLM SFT (full) | 0.698 | 0.705 | 0.619 | 0.618 | 9.380 | 0.086 | 0.459 | -1.188 |
| Best LLM SFT (LoRA) | 0.647 | 0.648 | 0.608 | 0.602 | 9.117 | 0.076 | 0.371 | -0.431 |
| **Epi2Diff (Ours)** | **0.730** | **0.728** | **0.631** | **0.626** | **7.612** | **0.396** | **0.291** | **0.121** |

**Key observations:**
- Epi2Diff achieves the best performance across **all 4 datasets and all 8 metrics**
- **8.1% average relative gain** over LLM SFT on SAT benchmarks
- Linear models (even best LLM SFT) produce negative R² on regression tasks
- Epi2Diff is the only method with positive R² on both regression datasets

---

## 8. Ablation Studies

### 8.1 Aggregation Strategy (SAT Math)

| Setting | ACC | F1 |
|---------|:---:|:---:|
| QwQ (Single Direct) | 0.684 | 0.681 |
| Qwen (Single Direct) | 0.712 | 0.708 |
| Both (Direct) | 0.707 | 0.708 |
| Both (Role) | **0.730** | **0.728** |

- Role-based aggregation outperforms both single-source and source-level aggregation
- Averaging over sources alone is not always sufficient

### 8.2 Representation Design (SAT Math)

| Feature Config | QwQ (F1) | Both (Role) (F1) |
|----------------|:--------:|:----------------:|
| Sem. Only | 0.607 | 0.607 |
| FFea. Only (no semantic) | 0.670 | 0.631 |
| Sem. + Len. | 0.635 | 0.671 |
| Sem. + Epi. | 0.652 | 0.686 |
| Sem. + Tran. | 0.641 | 0.693 |
| **Sem. + FFea. (full)** | **0.681** | **0.728** |

- Full representation consistently best across all settings
- Removing any feature family hurts performance
- Transition features are especially important in the richest aggregated setting

### 8.3 Matched Rollout-Count Control

| Setting | F1 |
|---------|:---:|
| Single Direct | 0.708 |
| Direct Replication (4x) | 0.714 |
| Profiled Aggregation (4 profiles) | **0.728** |

The benefit of role-based aggregation is **not** from simply using more rollouts; it stems from structured proficiency-conditioned variation.

---

## 9. Interpretability Analyses

### 9.1 Feature Importance

| Feature Group | Permutation Importance | SHAP Importance |
|---------------|:---------------------:|:---------------:|
| Semantic | 0.084 | 4.273 |
| Length | 0.042 | 0.526 |
| Episode | 0.024 | 0.436 |
| Transition | 0.064 | 0.588 |
| Epi.+Tran. combined | **0.136** | **1.024** |

Episode + transition features collectively surpass semantic features in permutation importance, confirming they add genuinely new signal.

### 9.2 Directional Effects (Standardized Average Marginal Effects)

**Length**: Total trace length (+0.237) and think length (+0.151) are the strongest positive drivers. Answer length is small (+0.038).

**Episode counts**: Implement (+0.088), Analyze (+0.042), Plan (+0.007) are positive. Verify is negative (−0.002) — standalone verification decreases as difficulty increases.

**Episode ratios**: Implement ratio positive (+0.009). Ratios of Read (−0.002), Plan (−0.001), Verify (−0.028) are negative. This means harder items **shift effort toward execution** rather than proportionally increasing all reasoning types.

**Transitions**: Top positive transitions: Analyze→Implement (+0.092), Implement→Implement (+0.073), Implement→Analyze (+0.021). This reveals a local **analysis–execution–refinement cycle**.

### Key Finding: Structure of Difficulty

> Harder items induce more effortful, iterative, and **implementation-centered** episode dynamics, rather than merely longer responses.

---

## 10. Representative Case Studies (Appendix C.5)

Three SAT Math items analyzed with Qwen3-32B:

| Item | Difficulty | Total Tokens | % Implement | % Analyze | % Verify | % Read |
|------|:----------:|:------------:|:-----------:|:---------:|:--------:|:------:|
| #217 | Easy | 557 | 25.3% | 15.1% | 17.2% | 12.0% |
| #235 | Medium | 795 | 34.7% | 18.9% | 15.6% | 7.9% |
| #607 | Hard | 995 | 40.3% | 20.3% | 13.0% | 7.4% |

The easy item (#217, "Evaluate f(10) = 4x-3") shows fragmented monitoring/reading/planning with short execution. The medium item (#235, slope from intercepts) shows more sustained analysis. The hard item (#607, exponential function with y-intercept and product constraint) shows heavy early analysis and sustained implementation, with a collapsed trajectory dominated by Monitor→Analyze→Analyze transitions.

---

## 11. Claims & Contributions

### C1: Structured process representation from reasoning traces improves difficulty prediction
**Evidence**: Epi2Diff outperforms all baselines on all 4 datasets. 8.1% avg relative gain on SAT benchmarks.

### C2: Episode dynamics encode interpretable difficulty signatures
**Evidence**: Standardized average marginal effects show coherent patterns (harder = more Implementation, more Analyze→Implement transitions). Feature importance shows episode+transition features provide new signal beyond semantics and length.

### C3: Role-based aggregation is more effective than naive sampling
**Evidence**: Matched rollout-count control (4 direct replications vs. 4 profiled rollouts) shows profiled aggregation yields F1 of 0.728 vs. 0.714 for direct replication.

### C4: Schoenfeld episodes provide a viable cognitive ontology for trace analysis
**Evidence**: RoBERTa classifier achieves 0.799 accuracy on episode labeling. Episode features are consistently predictive across all experimental settings.

### C5: Difficulty has a structured process signature beyond length
**Evidence**: The full representation outperforms Len. Only by 18.9 F1 points. Episode and transition features contribute independently.

---

## 12. Limitations

1. **Finite LRM set**: Only QwQ-32B and Qwen3-32B were used as trace generators. Different models (DeepSeek-R1, GPT-5) may produce different episode distributions.
2. **Domain coverage**: Four benchmarks (SAT, Cambridge, USMLE) do not cover all assessment formats (e.g., open-ended items, fill-in-the-blank).
3. **Computational cost**: Generating multiple traces per item (8 traces = 2 LRMs × 4 profiles) is expensive for large-scale deployment.
4. **Episode labeler quality**: RoBERTa classifier at 0.799 accuracy may not be sufficient for nuanced educational applications.
5. **LRM traces ≠ human cognition**: The paper explicitly acknowledges that reasoning traces are model-generated proxies, not direct observations of human problem solving.

---

## 13. Impact & Significance

**For educational measurement**: Epi2Diff offers a scalable alternative to field testing for difficulty estimation, with interpretable process evidence that can help test developers understand *why* an item is difficult.

**For reasoning model research**: The paper demonstrates that LRM reasoning traces encode structured, usable information beyond verbosity, and that cognitive episode theory provides an effective abstraction for extracting this signal.

**For interpretable AI**: The episode-induced features (length, distribution, transitions) are human-interpretable — test developers can see that a hard item has more Implementation, more Analyze→Implement transitions, and less planning.

---

## 14. References (Key)

1. Schoenfeld, A. H. (2014). *Mathematical Problem Solving.* Elsevier.
2. Li, M. et al. (2025b). Schoenfeld's Anatomy of Mathematical Reasoning by Language Models. *EMNLP 2025.*
3. Li, M. et al. (2025d). Understanding the Thinking Process of Reasoning Models: A Perspective from Schoenfeld's Episode Theory. *EMNLP 2025.*
4. Guo, D. et al. (2025). DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via RL.
5. Razavi, P. & Powers, S. J. (2025). Estimating item difficulty using LLMs and tree-based ML.
6. Feng, W. et al. (2025a). Reasoning and Sampling-Augmented MCQ Difficulty Prediction via LLMs. *AIED 2025.*

---

## 15. Code & Resources

- Code: https://github.com/c-steve-wang/Epi2Diff
- Datasets: SAT (College Board), Cambridge (Mullooly et al., 2023), USMLE (Yaneva et al., 2024)
- ThinkARM annotation corpus used for episode classifier training
