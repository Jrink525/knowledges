# Bag of Dims: Training-Free Mechanistic Interpretability via Dimension-Level Sign Patterns

**Authors:** Varun Reddy Nalagatla (Amazon Web Services)  
**arXiv:** 2606.12629v2 [cs.LG]  
**Date:** June 2026  
**Categories:** cs.LG, cs.AI  
**Pages:** 22 pages, 5 figures, 27 tables  
**Code/Data:** N/A (paper only)

---

## 1. Abstract

This paper shows that the **standard basis** of transformer hidden states already provides a training-free, architecture-general feature basis. Individual dimensions encode semantic content via their **signs** (±1) and confidence via their **magnitudes**, acting as independent binary registers. A feature is a subset of dimensions with a consistent sign pattern, readable by counting sign agreements with no learned rotation.

The "Bag of Dims" framework is validated across **seven models**: four language (Qwen 3.5-4B, Gemma 3-4B, Mistral 7B, Qwen3-32B), two vision (DINOv2, ViT-Base), and one audio (AST).

---

## 2. Core Claims

### Claim 1: Sign encodes content, magnitude encodes confidence
- Sign-only next-token prediction preserves 60–93% top-5 accuracy through the LM head
- Pure Hamming scoring (no decoder) reaches 80–90% top-4096
- Low-magnitude dimensions act as noise; the 800 highest-magnitude dims outperform all dims

### Claim 2: Dimensions are independent
- Pairwise mutual information between dimension signs: mean < 0.006 bits
- Context *lowers* pairwise coupling rather than creating it
- An MLP with full cross-dimension capacity adds zero AUC over per-dim logistic regression

### Claim 3: Zero-training feature discovery
- 175 semantic categories detectable at AUC 0.97–0.99 from a single-token cache
- Trained probe adds only +0.018 AUC and converges to axis-aligned weights
- Unsupervised discovery scales to 1500 features per model (100% yield, 99% sparsity)

### Claim 4: Features are causally operative, not merely readable
- Flipping a feature's sign pattern during live forward pass suppresses its concept
- Effect is magnitude-matched (sign, not magnitude) and concept-specific
- Requires coalition-level flipping; individual dimensions are inert

### Claim 5: Features survive attention projections
- All 175 categories exceed null calibration in both K and V dimensions
- Attention projections (Wk, Wv) preserve axis-aligned structure

### Claim 6: FFN neurons write axis-aligned sign patterns
- Up to 20% of features link to individual writer neurons (>0.70 sign agreement)
- Top-200 neuron coalitions reconstruct 99.9% of prototypes via majority vote
- FFN activations are themselves sign-readable at residual parity (survives SwiGLU)

### Claim 7: Cross-modality universality
- Works on DINOv2 (9/12 ImageNet superclasses), ViT-Base (11/12), AST (50/50)
- Self-supervised training already produces the structure; classification sharpens it
- Pure Hamming 1-NN: 93–97% accuracy across all modalities

---

## 3. Method

### 3.1 Bag-of-Dims Framework

Each of the D dimensions (D=2560 for 4B, D=4096 for Mistral 7B, D=5120 for Qwen3-32B) is an independent channel:
- **Sign** (+1 or −1): semantic content
- **Magnitude** (|value|): confidence/commitment

A **feature** = subset of dimensions 𝒟 ⊆ {1,...,D} with consistent sign pattern 𝝅 ∈ {+1,−1}^|𝒟| across tokens of a semantic category.

### 3.2 Single-Token Type Cache

For each vocabulary token (one at a time, no context):
1. Feed as single-token input
2. Extract hidden state at target layers
3. Store D-dimensional state

Result: matrix H ∈ ℝ^(V×D) per layer. One forward pass per vocab token (~20 minutes on single GPU). Storage: 1 bit/dim (93 MB for Qwen3-32B full vocabulary).

### 3.3 Feature Discovery via Per-Dimension AUC

**Step 1:** Anchor tokens: n_a=50 single-token exemplars per category.  
**Step 2:** Per-dimension AUC measures how well each dim's sign separates category from full vocabulary.  
**Step 3:** Register dims above threshold τ=0.75, build sign prototype (𝒟_c, 𝝅_c).  

Scoring new tokens → count fraction of registered dims where sign matches expected polarity (normalized Hamming distance).

### 3.4 K/V Projection Extension

Same procedure applied to sign(K) and sign(V) after normalization, projection, and RoPE.

---

## 4. Key Results

### 4.1 Sign Encodes Content (Table 1)

| Model | Sign-only Top-1 | Sign-only Top-5 | Full Top-5 |
|-------|----------------|----------------|------------|
| Qwen 3.5-4B | 56.5% | 84.0% | 100% |
| Gemma 3-4B | 49.0% | 72.0% | 100% |
| Mistral 7B | 62.5% | 93.0% | 100% |
| Qwen3-32B | 37.5% | 59.5% | 100% |

Random sign permutations → 0% across all models and metrics.

### 4.2 Pure Hamming Prediction (Table 2, no LM head)

| Model | Top-4096 |
|-------|----------|
| Qwen 3.5-4B | 80.5% |
| Gemma 3-4B | 90.0% |
| Mistral 7B | 81.5% |

Zero learned parameters. On Gemma/Mistral, beats the full-dot baseline.

### 4.3 Dimension Independence (Table 3)

| Model | Mean MI (type-level) | Mean MI (contextual) |
|-------|---------------------|---------------------|
| Qwen 3.5-4B | 0.0014 bits | 0.0006 bits |
| Mistral 7B | 0.0051 bits | 0.0006 bits |
| Qwen3-32B | 0.0014 bits | 0.0004 bits |

Maximum possible MI: 1.0 bit. No pair exceeds 0.1 bits.

### 4.4 Zero-Training Feature Discovery (Table 4)

| Model | Discoverable (≥0.75) | Mean Per-dim AUC | Prototype AUC | All exceed null? |
|-------|---------------------|-----------------|--------------|-----------------|
| Qwen 3.5-4B | 161/175 (92%) | 0.801 | 0.980 | 175/175 |
| Gemma 3-4B | 137/175 (78%) | 0.772 | 0.975 | 175/175 |
| Mistral 7B | 175/175 (100%) | 0.844 | 0.993 | 175/175 |
| Qwen3-32B | 154/175 (88%) | 0.792 | 0.978 | 175/175 |

Probe comparison: trained probe achieves 0.9997 vs 0.9814 (difference: +0.018). Probe learns axis-aligned voting—99.9% sign agreement.

### 4.5 Unsupervised Discovery (Table 6)

1500 random seeds → 1500 features (100% yield) for all four models:
- Qwen 3.5-4B: ~897 dims/feature, 99.9% fire on <0.1% vocabulary
- Gemma 3-4B: ~609 dims/feature
- Mistral 7B: ~1488 dims/feature
- Qwen3-32B: ~2826 dims/feature

### 4.6 Causal Sign-Flip (Table 8)

| Model | Away (suppress) | Toward | Disjoint | Random |
|-------|----------------|--------|----------|--------|
| Qwen 3.5-4B | −10 to −14 | ≈0 | ≈0 | ≈0 |
| Gemma 3-4B | −19 to −24 | ≈0 | ≈0 | ≈0 |
| Mistral 7B | −5 to −7 | ≈0 | ≈0 | ≈0 |
| Qwen3-32B | −5 to −9 | ≈0 | ≈0 | ≈0 |

### 4.7 Cross-Modality (Tables 14-17)

- **DINOv2** (self-supervised vision): 9/12 superclasses, 0.831 AUC
- **ViT-Base** (supervised vision): 11/12 superclasses, 0.977 AUC
- **AST** (audio): 50/50 categories, highest per-dim AUC across all models

---

## 5. Strengths

1. **Elegant simplicity**: The central idea—that sign patterns in the standard basis encode features—is beautifully simple and testable.

2. **Comprehensive validation**: Seven models across three modalities, with converging evidence from multiple experimental paradigms (prediction, discovery, causal intervention, circuit tracing).

3. **Strong baselines**: Head-to-head comparison against trained SAEs (Gemma Scope 2) shows sign prototypes win 173/175 categories at the individual feature level.

4. **Causal evidence**: The sign-flip intervention goes beyond correlation, showing these patterns are causally operative during generation.

5. **Practical implications**: If true, feature reading requires one forward pass and no GPU-days—dramatically lowering the cost of mechanistic interpretability.

---

## 6. Weaknesses

1. **Scale**: Tested on 4–32B language models and 86M parameter vision/audio models. Unclear if structure persists at 70B+ (authors note this).

2. **Depth-gated causality**: The sign-flip only works near the output; earlier layer flips are re-derived. This limits practical intervention usefulness.

3. **Directional asymmetry**: Flipping signs away suppresses, but toward does not induce. Only the "suppress" primitive is available.

4. **D/V ratio dependence**: Cross-architecture variation tracks dimension-to-vocabulary ratio, limiting applicability to models with small hidden dimensions relative to vocabulary.

5. **Polysemy ceiling**: Qwen3-32B fails at contextual sense reading (near chance), attributed to low D/V ratio.

6. **Localized to language/vision/audio**: Only tested on transformers; unclear if applies to other architectures (SSMs, RNNs).

---

## 7. Related Work Positioning

The paper positions itself against:
- **Sparse Autoencoders** (SAEs): Require millions of contextual activations and GPU-hours. Sign prototypes match or exceed individual SAE features without training.
- **Probes**: Require labeled datasets per property. Learned probes converge to axis-aligned weights anyway.
- **Superposition hypothesis**: Cross-dim MI in real transformers is 0.001–0.005 bits vs. 0.05–0.10 in Elhage's toy model—real models don't operate in the bottleneck regime where superposition binds.
- **Logit lens**: Explains *why* intermediate states are directly readable (individual dims carry independent features).

---

## 8. Implications

1. **Paradigm shift**: The open problem shifts from "finding the right rotation" (via SAEs/probes) to "cataloging what each dimension encodes at each layer"—a cataloging problem, not an optimization problem.

2. **Combinatorial capacity**: 3^D − 1 possible sign-pattern features (≈10^1220 for D=2560). No inherent scaling limit.

3. **Cross-modal convergence**: The same structure appears in language, vision, and audio transformers → likely a convergent property of gradient descent on transformer architectures, not language-specific.

4. **Safety monitoring**: Real-time per-dim sign pattern monitoring for safety-relevant features.

---

## 9. Open Questions

1. **Why do different objectives converge?** Next-token prediction, self-distillation, and classification all produce the same per-dim structure.

2. **What do the flipping 42% of dimensions encode?** Low-magnitude dims that flip with context likely carry contextual/syntactic role information.

3. **Does the structure persist at 70B+?** Consistent results from 4B to 32B suggest yes, but untested.

4. **Induction primitive**: Flipping signs away suppresses; can we induce concepts (magnitude operation)?

5. **Full layer sweep for vision/audio**: Not yet tested for non-autoregressive architectures.

---

## 10. Verdict

**Score: 8.5/10**

A significant, elegantly argued paper with comprehensive evidence that the standard basis of transformer hidden states already provides a feature basis. The main claims are well-supported across models and modalities. The causal intervention and circuit tracing sections are particularly strong. Primary limitations are scale (tested up to 32B, not 70B+) and the depth-gated nature of the causal effect. If replicated at larger scales, this could substantially reorient the mechanistic interpretability field away from learned rotations and toward direct basis reading.
