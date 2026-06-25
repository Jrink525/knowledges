# Multi4D: High-Fidelity Dynamic Gaussian Splatting via Multi-Level Competitive Allocation

> **Accepted at ECCV 2026**
>
> Rui Wang, Quentin Lohmeyer, Siyu Tang, Mirko Meboldt — ETH Zürich
>
> arXiv: 2606.22197 | Project page: https://batfacewayne.github.io/Multi4D.io/

---

## 1. Paper Metadata

| Field | Value |
|---|---|
| **Full Title** | Multi4D: High-Fidelity Dynamic Gaussian Splatting via Multi-Level Competitive Allocation |
| **Authors** | Rui Wang, Quentin Lohmeyer, Siyu Tang, Mirko Meboldt |
| **Affiliation** | ETH Zürich |
| **Venue** | ECCV 2026 (European Conference on Computer Vision) |
| **Submission Date** | 20 Jun 2026 (v1) |
| **Keywords** | Dynamic Gaussian Splatting, 4D Scene Representation, Novel View Synthesis, Competitive Allocation, 4D Segmentation |
| **Code** | Not released at time of reading |
| **Project Page** | https://batfacewayne.github.io/Multi4D.io/ |

---

## 2. Problem Statement

Dynamic 3D Gaussian Splatting faces a **fundamental tension between motion consistency (physical plausibility / temporal correspondence) and visual fidelity (rendering quality)**. Existing methods fall into two opposing families, each with complementary failure modes:

- **Deformation-based approaches** (e.g., Deformable-3DGS, 4DGaussian): maintain a fixed set of canonical Gaussians warped over time. They preserve temporal identity and support downstream tasks (tracking, segmentation), but suffer from **motion over-factorization** — the deformation field groups nearby motion and over-smooths high-frequency dynamics. Complex appearance changes (specularities, lighting shifts) are mis-modeled as physical motion, causing spurious geometric warping.
  
- **4D-primitive approaches** (e.g., 4DGS, STG): use spatiotemporal Gaussian hyper-cylinders sliced at each timestamp. They capture fine visual details but incur **temporal over-parameterization** — the optimization exploits temporal scaling to minimize photometric error, hallucinating millions of short-lived primitives with broken geometry in fast motion regions. These methods lack long-term identity and generalize poorly to sparse camera inputs.

**The gap**: No existing method reconciles both properties — neither approach can simultaneously achieve long-term motion consistency AND high-frequency appearance fidelity with compact storage.

---

## 3. Core Insight & High-Level Approach

The authors challenge the **monolithic assumption** that a single representation must explain both physical kinematics and transient appearance. Instead, they formulate dynamic reconstruction as a **competitive multi-level optimization problem**:

> *Models with distinct inductive biases dynamically compete to explain photometric residuals.*

Three functionally specialized Gaussian subsets are jointly optimized under a **shared differentiable rasterizer**:

1. **Static Gaussians (ℊₛ)** — Time-invariant structural backbone
2. **Persistent Dynamic Gaussians (ℊ𝒹)** — Deformable primitives with long-term identity
3. **Transient Gaussians (ℊₜ)** — Short-lived 4D primitives for high-frequency appearance residuals

**Key mechanism**: Shared transmittance in the unified renderer couples gradients across subsets. Once one subset explains a region, residual-driven densification in the others is suppressed — enabling **emergent, self-organized specialization** without pre-assigned decomposition.

---

## 4. Related Work Analysis

### 4.1 Deformation-Based Dynamic Gaussian Methods
- **Core idea**: Warp canonical Gaussians via time-conditioned deformation modules (MLPs, HexPlane grids, explicit trajectories)
- **Examples**: Deformable-3DGS [48], 4DGaussian [41], SC-GS [9], SplineGS [50], Spec4D [8]
- **Strengths**: Temporal correspondence, downstream capability (tracking, semantics)
- **Weaknesses**: Motion over-factorization; deformation query overhead scales with Gaussian count; appearance changes absorbed as spurious motion
- **Decoupled variants**: DeGauss [39], Swift4D [42] — separate static/dynamic, but still lack high-fidelity transient modeling

### 4.2 4D-Primitive-Based Methods
- **Core idea**: 4D spatiotemporal ellipsoids sliced to 3D per timestamp
- **Examples**: 4DGS [47], 4D-Rotor [6], STG [22], FreeTimeGS [40]
- **Strengths**: High-fidelity appearance, temporal pre-filtering for efficiency
- **Weaknesses**: Temporal over-parameterization (millions of short-lived primitives); broken geometry in fast motion; poor generalization to sparse/monocular input
- **Compression variants**: MEGA [53], OM-4DGS [18], 1000+FPS-GS [51] — prune static redundancy but cannot simplify dynamic regions

### 4.3 Semantic Embedding with Gaussians
- Combine Gaussian representations with foundation models (SAM, DINO)
- **Dynamic examples**: TRASE [21], SA4D [10], DGD [16], 4D-LangSplat [20]
- **Key limitation**: Inherit deformation network overhead — evaluating high-dim features for every primitive at each frame is expensive

### 4.4 Positioning of Multi4D
Multi4D is the **first to explicitly decompose the dynamic scene into three hierarchically specialized subsets** and let them compete under a unified objective, simultaneously solving motion over-factorization AND temporal over-parameterization while achieving compact storage and downstream capability.

---

## 5. Method — Full Architecture

### 5.1 Overall Framework

Given a set of multi-view video frames 𝒮 = {Iₜ}ₜ₌₁ᵀ, Multi4D models the scene as:

**𝒢 = ℊₛ ∪ ℊ𝒹 ∪ ℊₜ**

Three subsets are jointly rendered in a **single differentiable rasterization pass** at each timestamp.

### 5.2 Preliminaries: 3D & 4D Gaussian Splatting

**3D Gaussian Splatting** (Kerbl et al., 2023):
Each primitive g has mean μ, covariance Σ = R S Sᵀ Rᵀ, opacity σ, and SH coefficients c(d). Rendering at pixel u:

**C(u) = Σᵢ cᵢ(d) σᵢ 𝒫ᵢ(gᵢ, u) Πⱼ₌₁ⁱ⁻¹ (1 − σⱼ 𝒫ⱼ(gⱼ, u))**

**4D Gaussian Splatting** (Yang et al., 2023):
4D ellipsoid with μ₄D = (μ_xyz, μₜ) ∈ ℝ⁴ and 4D covariance Σ₄D. At timestamp t, the 3D slice is:

**μ_xyz|t = μ₁:₃ + Σ₁:₃,₄ · Σ₄,₄⁻¹ · (t − μₜ)**
**Σ_xyz|t = Σ₁:₃,₁:₃ − Σ₁:₃,₄ · Σ₄,₄⁻¹ · Σ₄,₁:₃**

With 4D spherical harmonics c₄D(d, t−μₜ) for time-varying appearance.

### 5.3 Initialization: Inverse Expressiveness

| Subset | Initialization | Rationale |
|--------|---------------|-----------|
| ℊₛ (Static) | Dense COLMAP points | Strong structural anchor; prevents static content from being assigned to dynamic subsets |
| ℊ𝒹 (Persistent Dynamic) | Sparse random points (~10k) | Gradual geometric refinement under self-supervision |
| ℊₜ (Transient) | Empty | Instantiated only via periodic lifting from ℊ𝒹 later in training; prevents overfitting to noise |

Also applies **Adaptive Spatial-Temporal Rescaling** to normalize spatial/temporal domains, preventing ill-conditioned 4D covariance matrices.

### 5.4 Unified Multi4D Rendering

Each primitive i ∈ 𝒢 at timestamp t is projected to an instantaneous 3D state Θₜ,ᵢ:

- **ℊₛ**: (μ, Σ, σ, c₃D) — time-invariant
- **ℊ𝒹**: (μₜ, Σₜ, σ, c₃D) — via deformation field Φ𝓰(μ, t) predicting rigid motion: (μₜ, rₜ) = (μ, r) + Φ𝓰(μ, t)
- **ℊₜ**: (μ_xyz|t, Σ_xyz|t, σₜ, c₄D) — via 4D slicing, with σₜ = σ · exp(−(t−μₜ)² / 2Σ₄,₄)

**Three outputs extracted from one pass:**
1. **Full Render C_full** — blends all subsets for photometric supervision
2. **Persistent Render Cₚ** — ℊₛ ∪ ℊ𝒹 only (masking out ℊₜ transmittance)
3. **Transient Contribution Cₜ** — ℊₜ contributions using global transmittance

A **diversity loss ℒ_diversity** (SSIM-based) between Cₜ and Cₚ discourages redundant modeling across subsets.

### 5.5 Self-Supervised Dynamic-Static Decomposition (Section 3.4)

Based on DeGauss [39] but augmented:

1. **Mask Rendering**: Each ℊ𝒹 Gaussian gets a base mask logit mᵢ + time-dependent offset via MLP 𝒟ₘ: m'ᵢ(t) = mᵢ + 𝒟ₘ(ℋ(μᵢ, t))

2. **Composite Rendering**: Substitute SH colors with activated mask, render dynamic mask M𝒹 ∈ [0,1]ᴴˣᵂ, compose:
   **C_comp = M𝒹 ⊙ C𝒹 + (1 − M𝒹) ⊙ Cₛ**

3. **Separation Loss ℒ_sep** combines compositing error and regional supervision (Eq. 11-12), plus **opacity penalty ℒ_α** that suppresses ℊ𝒹 opacity in static regions (M𝒹 ≈ 0).

Structural asymmetry (dense COLMAP ℊₛ vs sparse random ℊ𝒹) biases static content toward ℊₛ, and M𝒹 naturally contracts to moving regions.

### 5.6 Velocity-Aware Periodic Lifting (Section 3.5)

**When**: After dynamic-static separation stabilizes (~6k iterations)
**How**: Periodically (every 50 iters until 10k), sample K=2000 active ℊ𝒹 candidates with dynamic score m'ᵢ(t) > τ=0.05 and lift to ℊₜ via:

- **Velocity estimation**: vᵢ = (Φ𝓰(μᵢ, t+Δt) − Φ𝓰(μᵢ, t)) / Δt
- **Momentum inheritance**:
  **μ₄D⁽ⁿᵉʷ⁾ = [μᵢ(t) + ϵ, t]ᵀ**
  **r₄D⁽ⁿᵉʷ⁾ ← Align(vᵢ)**
  
  (ϵ = small offset toward camera to prevent immediate occlusion; Align orients the 4D principal axis along [vᵢᵀ, 1]ᵀ)

This provides a **strong motion prior** for ℊₜ, mitigating instability under sparse/monocular supervision. After promotion, ℊₜ densifies autonomously to model residuals.

### 5.7 Mask-Aware Utility-Based Pruning (Section 3.6)

Overcomes limitations of opacity-based pruning. For each Gaussian gᵢ and view I, define **peak visible contribution**:

**wᵢ,𝐼 = max_𝐮∈𝐼 ( σᵢ 𝒫ᵢ(gᵢ, u) Πⱼ₌₁ⁱ⁻¹(1−σⱼ 𝒫ⱼ(gⱼ, u)) ) · M(u)**

where gating mask M(u) applies:
- M𝒹 for ℊ𝒹
- (1−M𝒹) for ℊₛ
- 1 for ℊₜ

Aggregate over window ℐₛ: **sᵢ = β · max(wᵢ,𝐼) + (1−β) · mean(wᵢ,𝐼)**

Primitives with sᵢ < τ_prune are removed. Also applies **Stochastic Primitive Dropout** to discourage view-dependent overfitting.

### 5.8 Training Strategy and Objectives

**Two-stage training:**
- **Phase I (0–10k iters, Subset Formation)**: Dynamic-static separation, velocity-aware lifting, diversity loss, mask-aware pruning all active. Deformation frozen for first 2k iters.
- **Phase II (10k–20k iters, Rendering Refinement)**: Separation/lifting disabled; focus on refining geometry and appearance with unified renderer; pruning remains active.

**Total Loss** (Eq. 8, detailed in Appendix 0.C.4):

**ℒ_total = ℒ_color + λ_sep · ℒ_sep + λ_reg · ℒ_reg + λ_div · ℒ_diversity**

- **ℒ_color**: L₁ + (1−SSIM) applied to full hybrid render (and separately to foreground/background during Phase I)
- **ℒ_sep**: Self-supervised dynamic-static decomposition loss
- **ℒ_diversity**: SSIM-based penalty between Cₜ and Cₚ (λ_div=0.1)
- **ℒ_reg** aggregates:
  - Mask-aware opacity regularization (ℒ_α)
  - Depth ordering (transient should be on/in front of persistent geometry)
  - Scale regularization (max scale < 10% scene extent)
  - Aspect ratio regularization (prevent degenerate elongated primitives)
  - Edge-aware depth TV smoothness
  - Temporal smoothness on HexPlane grids

**Implementation**: PyTorch, single RTX 4090, 20k iterations, ~1.2 hours (vs 5.5h for 4DGS).

### 5.9 Independent Per-Subset Optimization (Appendix 0.C.1)

Each subset has its own Adam optimizer, learning rate schedule, and densification/pruning policy:
- **ℊₛ**: Larger budget, relaxed pruning, densified by 2D gradients
- **ℊ𝒹**: Updates Gaussians + HexPlane deformation network Φ𝓰; clone/split on canonical Gaussians
- **ℊₜ**: Controlled by both spatial+temporal gradients; progressive opacity pruning

---

## 6. Downstream Application: Efficient 4D Segmentation

After reconstruction, **freeze all geometric parameters** and attach learnable 32-dim semantic features to the persistent subset ℊₚ = ℊₛ ∪ ℊ𝒹 (ℊₜ discarded — it has no stable identity).

Training follows TRASE [21] contrastive framework:
- Splat semantic features via frozen renderer
- Supervise with SAM masks via soft contrastive loss (ℒ_pos + ℒ_neg + feature collapse prevention)
- KNN feature smoothing in canonical 3D space

**Key advantage**: Only ~13k dynamic Gaussians needed vs 624k in TRASE, enabling 204 FPS semantic rendering (10× speedup over 21 FPS baseline). Achieves 0.9142 mIoU on Neu3D-Mask (SOTA).

Supports **open-vocabulary 4D segmentation**: text prompt → Grounding DINO + SAM → 3D unprojection → cluster assignment → temporal tracking.

---

## 7. Datasets

| Task | Dataset | Description |
|------|---------|-------------|
| Multi-view NVS | Technicolor [33] | 5 scenes, 2048×1088, light-field video |
| Multi-view NVS | Neu3D [19] | 6 scenes, 300-frame sequences, 1352×1014 |
| Monocular NVS | NeRF-DS [46] | Dynamic specular objects, challenging monocular setting |
| 4D Segmentation | Neu3D-Mask [21] | Neu3D scenes with mask annotations |

---

## 8. Quantitative Results

### 8.1 Technicolor Dataset (Table 1)

| Method | Mean PSNR↑ | Mean DSSIM↓ | FPS↑ |
|--------|-----------|-------------|------|
| DyNeRF | 31.80 | - | 0.02 |
| HyperReel | 32.70 | 0.047 | 4.0 |
| 4DGaussians | 30.86 | 0.071 | 35 |
| Def-3DGS | 30.95 | 0.070 | 76 |
| E-D3DGS | 32.89 | 0.049 | 79 |
| 4DGS | 32.07 | 0.054 | 55 |
| STG | 33.35 | 0.040 | 86 |
| **Multi4D (Ours)** | **34.30** | **0.037** | **161** |

Multi4D surpasses the best baseline (STG) by **+0.95 dB PSNR** while achieving **161 FPS**.

### 8.2 Neu3D Dataset (Table 2)

| Method | Mean PSNR↑ | Mean DSSIM↓ | FPS↑ |
|--------|-----------|-------------|------|
| Def-3DGS | 30.98 | 0.033 | 29 |
| 4DGaussian | 31.12 | 0.032 | 53 |
| DeGauss | 31.52 | 0.029 | 157 |
| E-D3DGS | 31.20 | 0.026 | 70 |
| 4DGS | 31.57 | 0.029 | 114 |
| STG | 32.04 | 0.026 | 140 |
| **Multi4D (Ours)** | **32.30** | **0.026** | **217** |

Best PSNR of all methods, matching best DSSIM, and **fastest rendering** (217 FPS).

### 8.3 NeRF-DS (Monocular, Table 3)

| Method | Mean PSNR↑ | Mean DSSIM↓ |
|--------|-----------|-------------|
| NeRF-DS | 23.24 | 0.081 |
| HyperNeRF | 19.01 | 0.092 |
| Def-3DGS | 23.43 | 0.086 |
| 4DGaussian | 22.79 | 0.088 |
| 4DGS | 21.51 | 0.108 |
| STG | 22.54 | 0.089 |
| **Multi4D (Ours)** | **23.69** | **0.077** |

Multi4D achieves best PSNR and best DSSIM, highlighting robustness under sparse supervision.

### 8.4 4D Segmentation on Neu3D-Mask (Table 4)

| Method | mIoU↑ | mAcc↑ | Note |
|--------|-------|-------|------|
| OpenGaussian | 0.8178 | 0.9899 | |
| SA4D | 0.8832 | 0.9931 | |
| TRASE | 0.8932 | 0.9938 | |
| **Multi4D (Ours)** | **0.9142** | **0.9952** | **204 FPS** (vs 21 FPS TRASE) |

Multi4D improves mIoU by +2.1% over TRASE with **10× speedup**.

---

## 9. Ablation Studies (Table 5)

Ablation on 4 Neu3D scenes:

| Configuration | PSNR↑ | DSSIM↓ | Dyn. GS # | Storage |
|--------------|-------|--------|-----------|---------|
| Baseline 4DGS | 33.14 | 0.0219 | 4215k | 2.6 GB |
| w/o ℊ𝒹 (Persistent) | 32.78 | 0.0237 | 1139k | 727.5 MB |
| w/o ℊₜ (Transient) | 32.86 | 0.0217 | 25k | 105.4 MB |
| w/o Periodic Lifting | 33.22 | 0.0216 | 13k+132k | 184.8 MB |
| w/o ℒ_diversity | 33.66 | 0.0203 | 19k+257k | 263.8 MB |
| w/o Mask-Aware Pruning | 33.68 | 0.0199 | 70k+659k | 527.9 MB |
| **Multi4D (Full)** | **33.92** | **0.0197** | **13k+152k** | **214.7 MB** |

**Key findings:**
- Removing ℊ𝒹 lowers PSNR by 1.14 dB — no structured motion modeling
- Removing ℊₜ limits high-frequency modeling (-1.06 dB), though very compact (25k)
- Without lifting: -0.70 dB — transient primitives lack motion priors
- Without ℒ_diversity: +67% dynamic primitives (276k vs 165k) — redundant cross-set modeling
- Without mask-aware pruning: 729k primitives, 145% storage increase — temporal over-parameterization returns
- **Full system: 25× fewer dynamic Gaussians than 4DGS, 12× less storage**

---

## 10. Efficiency Analysis

| Metric | 4DGS [47] | Multi4D | Improvement |
|--------|-----------|---------|-------------|
| Dynamic Gaussians | 4.2M | 165k | **25× reduction** |
| Model Size | 2.6 GB | 214.7 MB | **12× reduction** |
| Training Time (RTX 4090) | 5.5 hours | 1.2 hours | **4.6× faster** |
| Rendering Speed (Neu3D) | 114 FPS | 217 FPS | **1.9× faster** |
| 4D Seg. Inference Speed | 21 FPS (TRASE) | 204 FPS | **~10× faster** |

---

## 11. Qualitative Results

- **Technicolor (Fig. 3)**: Multi4D better preserves high-frequency dynamic details vs baselines. Deformation-based methods exhibit temporal blurring; 4D-primitive approaches produce fragmented geometry.
- **Neu3D (Fig. 4)**: Deformation methods [41, 2] over-smooth complex appearance changes; 4D-primitive [47, 22] show broken geometry in fast motion. Multi4D mitigates both.
- **NeRF-DS (Fig. 5)**: 4D-primitive methods degrade heavily under monocular supervision; Multi4D preserves coherent geometry and fine specular details via decoupled motion/appearance.
- **4D Segmentation (Fig. 6)**: Multi4D produces sharper masks and more stable tracks than TRASE.
- **Subset Specialization (Fig. 8, Appendix)**: Visual breakdown shows ℊₛ captures background, ℊ𝒹 maintains coherent motion, ℊₜ activates for fire, smoke, specular highlights.

---

## 12. Sensitivity Analysis (Appendix 0.E.2, Table 6)

Systematic sweep over regularizers (ℒ_α, ℒ_TV), lifting count K (500–10000), and mask threshold τ (0–0.50). All settings remain within -0.28 dB of reference, demonstrating **robustness to exact hyperparameters**.

---

## 13. Core Contributions (Index)

| # | Claim | Evidence Location | Supporting Data |
|---|-------|-------------------|-----------------|
| C1 | Multi-level Gaussian decomposition resolves tension between motion consistency and visual fidelity | Section 1, 3 | Tab 5 ablation: both ℊ𝒹 and ℊₜ needed |
| C2 | Competitive allocation via shared rasterization induces emergent specialization | Section 3.3, Appendix 0.B | Fig. 8 subset renderings |
| C3 | SOTA novel view synthesis (multi-view) | Section 4.2, Tab 1, 2 | Technicolor 34.30 PSNR, Neu3D 32.30 PSNR |
| C4 | Best monocular dynamic reconstruction | Section 4.2, Tab 3 | NeRF-DS 23.69 PSNR |
| C5 | Significantly fewer dynamic primitives (25× vs 4DGS) | Section 5, Tab 5 | 165k vs 4.2M dynamic Gaussians |
| C6 | Real-time rendering (161-217 FPS) | Tab 1, 2 | 161 FPS (Technicolor), 217 FPS (Neu3D) |
| C7 | SOTA 4D segmentation accuracy | Section 3.8, Tab 4 | 0.9142 mIoU on Neu3D-Mask |
| C8 | 10× faster 4D segmentation inference | Section 3.8, 4.2 | 204 FPS vs 21 FPS TRASE |
| C9 | Robust to sparse/monocular supervision | Tab 3, Fig. 5 | Best on NeRF-DS |
| C10 | 4.6× faster training than 4DGS | Section 5 | 1.2h vs 5.5h |
| C11 | Self-supervised dynamic-static decomposition | Section 3.4 | Eq. 9-12, Fig. 9 |
| C12 | Velocity-aware lifting provides strong motion priors | Section 3.5, Tab 5 | -0.70 dB without lifting |

---

## 14. Limitations (from the paper)

1. **No explicit attribute compression**: The paper notes that post-training deformation distillation, Gaussian quantization, or lightweight deformation parameterizations could further improve storage efficiency.

2. **Persistent subset limitation for segmentation**: While effective, discarding ℊₜ for segmentation means information loss for highly transient objects.

3. **Dependence on COLMAP**: Like many 3DGS methods, initialization depends on SfM points, which may fail for texture-poor or highly dynamic scenes.

---

## 15. Future Directions

1. **Post-training compression**: Explore deformation distillation, Gaussian quantization, or lightweight deformation parameterizations
2. **Feed-forward dynamic reconstruction**: Extend to one-shot/few-shot settings
3. **All-point tracking**: Leverage persistent Gaussians for long-term point correspondence
4. **Large-scale / outdoor scenes**: Apply to egocentric (e.g., EgoGaussian [52]) or surgical (e.g., POV-Surgery [38]) domains
5. **Temporal editing**: Leverage decomposed representation (static vs. dynamic vs. transient) for controllable scene editing

---

## 16. Connections to Prior Work

| Prior Work | Relationship | Key Difference |
|-----------|-------------|----------------|
| **4DGS** [47] | Foundation for ℊₜ 4D primitives | + ℊₛ and ℊ𝒹 competition prevents over-parameterization |
| **STG** [22] | Gaussian feature splatting | Multi4D adds subset competition and explicit decomposition |
| **4DGaussian** [41] | Deformation-based dynamic | Multi4D decouples appearance from deformation |
| **DeGauss** [39] | Dynamic-static decomposition | Multi4D adds 3rd transient level + competitive allocation |
| **Hybrid 3D-4D** [29] | Binary static-dynamic fusion | Multi4D extends to 3 levels + competitive allocation |
| **TRASE** [21] | 4D segmentation framework | Multi4D applies on persistent subset only → 10× speedup |

---

## 17. Recommended Reading Order

1. **Abstract + Fig. 1** (overview)
2. **Section 1** (problem + contributions)
3. **Section 3 + Fig. 2** (method overview)
4. **Tabs 1-4** (main results)
5. **Tab 5** (ablation — most informative for understanding each component's role)
6. **Appendix 0.B + Fig. 8** (subset specialization visualization)
7. **Appendix 0.C.4** (exact loss formulations)

---

## 18. Summary

Multi4D introduces a **conceptually simple yet highly effective** idea: instead of forcing a single representation to model all aspects of dynamic scenes, let three specialized Gaussian subsets **compete** under a shared photometric objective. The result is emergent specialization: static structure, coherent motion, and transient appearance each handled by the subset best suited for it.

This achieves **SOTA on all three evaluated benchmarks** (Technicolor, Neu3D, NeRF-DS), **25× fewer dynamic Gaussians** than 4DGS, **4.6× faster training**, and **SOTA 4D segmentation with 10× speedup**. The paper is well-structured, the ablations are thorough, and the supplementary material provides complete implementation details.
