# ImageWAM: Do World Action Models Really Need Video Generation, or Just Image Editing?

**arXiv:** 2606.19531 | **Date:** June 17, 2026 | **Authors:** Zhang et al. (Shanghai Jiao Tong University, Eastern Institute of Technology, Tencent Robotics X, Tsinghua University, Zhongguancun Academy)

**Project Page:** https://zhangwenyao1.github.io/ImageWAM/ | **Code:** https://github.com/yuyangalin/ImageWAM

---

## 1. Problem Statement

### 1.1 The Premise of Video-Based World Action Models

World Action Models (WAMs) are an emerging paradigm in robot policy learning that use video generation as a bridge between visual world modeling and robot control. The premise is appealing:

- **Visual dynamics from pretraining:** Video generation models, trained on large-scale heterogeneous video data, learn rich visual dynamics — object motion, temporal continuity, physical interaction, and scene evolution.
- **Reason-before-act:** A policy first imagines how the scene will change (predicts a future video), then uses that imagined future to guide action prediction.
- **Scalability:** Generative pretraining on large video datasets makes this approach scalable.

### 1.2 Three Coupled Limitations of Video-Based WAMs

The paper identifies three intertwined problems with video generation as a backbone for robot action prediction:

1. **Inference Cost:** Video generation requires predicting dense spatio-temporal tokens across multiple future frames. This makes inference expensive and limits real-time applicability. For real-time robot control, sub-100ms latency is often needed.

2. **Action-Irrelevant Capacity Allocation:** Video models must synthesize complete future videos, including appearance details, background changes, camera motion, temporal smoothness, and other factors only weakly related to the robot's next action. Model capacity is wasted on irrelevant visual details.

3. **Error Propagation from Inaccurate Future Video:** Generating a physically consistent video is a hard proxy task, especially for fine-grained manipulation where small contact events, slight object displacements, or subtle configuration changes determine success. If the imagined video is wrong (containing artifacts, missing subtle changes), the downstream action predictor is misled.

These issues motivate the paper's central question: **Does the world action model really require video generation?**

---

## 2. Key Insight: Image Editing as a Better Prior

### 2.1 Why Image Editing Matches Robot Policy Requirements

The authors argue that image editing models offer a more direct generative prior for language-conditioned manipulation:

| Aspect | Video Generation | Image Editing |
|--------|-----------------|---------------|
| **Objective** | Predict complete scene evolution over time | Transform a source image per language instruction |
| **Relevant signal** | All visual changes (relevant + irrelevant) | Instruction-guided visual change only |
| **Information density** | Dense multi-frame tokens | Single target transformation |
| **Temporal scope** | Full trajectory prediction | Current → desired state mapping |

### 2.2 Three Advantages

1. **Instruction-to-Change Alignment:** The editing pretraining objective directly couples language with visual modifications. The model learns what should change, where it should change, and how the change is specified by the instruction.

2. **Easier and More Action-Relevant Proxy:** Rather than modeling complete temporal trajectories, editing focuses on the visual difference between the current state and an instruction-consistent target state. This avoids spending capacity on irrelevant temporal details and reduces the risk of using inaccurate future videos for action generation.

3. **Compact Inference Path:** A policy can use internal editing-aware representations (KV caches) that encode the intended visual transformation, without decoding dense multi-frame videos at inference time.

---

## 3. ImageWAM Framework: Method

### 3.1 Problem Formulation

The standard robot policy objective: predict an action chunk **a**_{t:t+H} = (a_t, a_{t+1}, ..., a_{t+H}) given current observation o_t and language instruction l:

π_θ(a_{t:t+H} | o_t, l)

**Video-based WAM** approach: (o_t, l) → ô_{t+1:t+H+1} → a_{t:t+H}
**ImageWAM** approach: (o_t, l) → ô_edit ≡ ô_{t+H+1} → a_{t:t+H}

ImageWAM predicts only the endpoint frame rather than the full video trajectory.

### 3.2 ImageWAM Architecture

The architecture consists of three key components:

#### 3.2.1 Image Editing Backbone
- A pretrained text-guided image editing model (e.g., OmniGen2, FLUX.2, Ovis-U1)
- Takes current observation o_t and language instruction l as input
- Predicts the future endpoint frame ô_{t+H+1}
- **Key innovation:** The backbone is frozen or fine-tuned, and its intermediate representations are extracted as editing caches

#### 3.2.2 Editing Caches as World-Action Context
The editing cache is defined as the set of layer-wise KV pairs from the editing denoising process:

**C**_{edit}^τ = {(K_ℓ^τ, V_ℓ^τ)}^L_{ℓ=1} = f_{edit}^τ(o_t, l)

where τ is the editing denoising timestep. These caches encode instruction-conditioned visual transformation information — what changes, where it changes, and how the instruction specifies the change.

#### 3.2.3 Multi-Modal Token Integration (MoT)
The architecture uses joint self-attention over four token types:
- **Language context tokens** (from LLM)
- **Visual condition tokens** (current observation)
- **Visual prediction tokens** (future frame noising trajectory)
- **Action tokens** (robot actions)

The attention mask is configured such that action tokens attend to other tokens unidirectionally, while noisy tokens attend only to context tokens to keep context information clean.

### 3.3 Training Objectives

#### Image Editing Objective (Flow Matching)
The editing branch predicts the task-relevant future endpoint frame. Let o*_{t+H+1} be the target future observation and z* = E_vae(o*_{t+H+1}) its latent. With image noise ϵ_z ~ N(0,I) and flow time r ∈ (0,1):

z_r = (1-r)z* + rϵ_z

The velocity predictor u_φ is trained:

L_img = E[∥u_φ(z_r, r | o_t, l) - (ϵ_z - z*)∥²₂]

#### Action Flow Matching
The action expert generates action chunks using flow matching. With action flow time s ∈ (0,1):

a_s = (1-s)a*_{t:t+H} + sϵ_a

Conditioned on current observation, task instruction, and editing cache C_{edit}^τ:

L_act = E[∥v_θ(a_s, s | o_t, l, C_{edit}^τ) - (ϵ_a - a*_{t:t+H})∥²₂]

**Joint training:** L = L_act + L_img

### 3.4 Efficient Inference

At inference time, ImageWAM avoids full future-video generation:

1. **Select a fixed editing denoising timestep τ\***
2. **Perform only one editing-branch forward step** to get C_{edit}^{τ\*}
3. **Action expert generates action chunk** by denoising conditioned on this cache

This means ImageWAM preserves the reason-before-act principle while being much more efficient than video-based WAMs — no dense multi-frame decoding needed.

### 3.5 Architecture Variants

Three base image editing models are adapted:

| Variant | Editing Backbone | LLM | Action DiT Size |
|---------|-----------------|-----|-----------------|
| ImageWAM-OmniGen2 | OmniGen2 DiT | Qwen2.5-VL-3B | ~760M params |
| ImageWAM-FLUX.2 4B | FLUX.2 | Qwen3-4B | ~642M params |
| ImageWAM-FLUX.2 9B | FLUX.2 | Qwen3-8B | ~952M params |
| ImageWAM-Ovis-U1 | Ovis-U1 visual decoder | Qwen3-1.7B | ~1.1B params |

All use action-head weight-copy initialization: Action DiT weights initialized by copying from the image editing model's DiT blocks.

---

## 4. Experiments and Results

### 4.1 Experimental Setup

**Benchmarks:**
- **LIBERO** (4 suites: Spatial, Object, Goal, Long) — 500 demos per suite, 10 tasks each
- **LIBERO-Plus** — distribution-shifted version with camera/robot/language/light/background/noise/layout perturbations
- **RoboTwin 2.0** — large-scale bimanual benchmark, 50+ tasks, 27,500 trajectories
- **Real-world** — 4 dual-arm tasks (Stack Bowls, Fold Towel, Open Drawer & Store Marker, Hang Cup on Rack), 100 demos per task

**Training details:**
- 8× NVIDIA H20 GPUs, DeepSpeed ZeRO-1/2, bf16 precision
- AdamW optimizer, lr=1e-4, warmup cosine scheduler
- Image resolution varies by benchmark (LIBERO: 224×448, RoboTwin: 288×256)
- Future horizon: 16 frames, action chunk length: 16

### 4.2 Main Results

#### RoboTwin 2.0

| Method | Policy Pretraining | Clean | Randomized | Average |
|--------|-------------------|-------|------------|---------|
| π₀ | ✓ | 65.92 | 58.40 | 62.16 |
| π₀.₅ | ✓ | 82.74 | 76.76 | 79.75 |
| ABot-M0 | ✗ | 81.20 | 80.40 | 80.80 |
| Motus | ✓ | 88.66 | 87.02 | 87.80 |
| LingBot-VA | ✓ | 92.90 | 91.50 | 92.20 |
| FastWAM | ✗ | 91.88 | 91.78 | 91.83 |
| **ImageWAM (Ours)** | **✗** | **93.20** | **93.56** | **93.38** |

ImageWAM achieves the highest average success rate (93.38%) among all methods, including those with extensive policy pretraining. Notably, it outperforms all VLA baselines by a large margin and matches/beats competitive video-based WAMs without additional embodied data.

#### LIBERO

| Method | Policy Pretraining | Spatial | Object | Goal | Long | Average |
|--------|-------------------|---------|--------|------|------|---------|
| OpenVLA | ✓ | 84.7 | 88.4 | 79.2 | 53.7 | 76.5 |
| GR00T N1 | ✓ | 84.7 | 88.4 | 79.2 | 53.7 | 76.5 |
| π₀ | ✓ | 96.8 | 98.8 | 95.8 | 85.2 | 94.1 |
| π₀.₅ | ✓ | 98.8 | 98.2 | 98.0 | 92.4 | 96.9 |
| LingBot-VA | ✓ | 98.5 | 99.6 | 97.2 | 98.5 | 98.5 |
| Motus | ✓ | 96.8 | 99.8 | 96.6 | 97.6 | 97.7 |
| FastWAM | ✗ | 98.2 | 100.0 | 97.0 | 95.2 | 97.6 |
| **ImageWAM** | **✗** | **97.2** | **99.2** | **98.8** | **98.4** | **98.4** |

ImageWAM achieves 98.4% average — competitive with video-based WAMs and VLAs with extensive policy pretraining, without any policy pretraining of its own.

#### LIBERO-Plus (Distribution Shift)

| Method | P.T. | Camera | Robot | Language | Light | Background | Noise | Layout | Avg |
|--------|------|--------|-------|----------|-------|------------|-------|--------|-----|
| FastWAM | ✗ | 16.4 | 44.5 | 68.9 | 78.2 | 53.7 | 37.7 | 60.7 | 51.5 |
| ImageWAM (FLUX.2 4B) | ✗ | **80.8** | 50.3 | **91.4** | **98.1** | 85.5 | **93.8** | 80.5 | **83.1** |

ImageWAM dramatically outperforms FastWAM (83.1% vs 51.5%), particularly on Camera perturbation (80.8% vs 16.4%), suggesting that editing-based world-action reasoning is more robust to visual domain shifts.

#### Real-World Robot Tasks

| Method | Stack Bowls (T1) | Fold Towel (T2) | Drawer & Marker (T3) | Hang Cup (T4) | Avg |
|--------|---------|---------|----------|--------|-----|
| π₀ | 57 | 58 | 54 | 54 | 55.8 |
| π₀.₅ | 83 | 77 | 74 | 55 | 72.3 |
| FastWAM | 88 | 75 | 77 | 76 | 79.0 |
| **ImageWAM** | **94** | **84** | **78** | **82** | **84.5** |

ImageWAM achieves the best performance on all four real-world tasks. Largest gain is on Fold Towel (84% vs 75% FastWAM, +9 points), suggesting editing context is particularly useful for deformable-object manipulation.

### 4.3 Efficiency Comparison

| Method | Latency | TFLOPs | Intermediate |
|--------|---------|--------|-------------|
| FastWAM-IDM (video WAM) | 1081 ms | 63.65 | Full video |
| FastWAM (1 step) | 302 ms | 13.21 | Video cache |
| **ImageWAM** | **263 ms** | **9.72** | **Editing cache** |

**1/6 FLOPs and ~1/4 latency** of full video-based WAMs.

With compilation optimization:
- ImageWAM (prefix-only): 198 ms (1.53×)
- + Action Loop Compile: 85 ms (3.55×)
- + Image Prefill Compile: 77 ms (3.92×)
- + Action Static Graph: **69 ms (4.38×)**

### 4.4 Qualitative Analysis: Future-Video Artifacts

The paper demonstrates that video-WAM baselines can generate distorted future observations around task-relevant objects. These artifacts lead to unreliable action conditioning. ImageWAM avoids this issue by using editing caches rather than decoded future frames.

### 4.5 Attention Analysis

Attention analysis shows that editing caches **focus on task-relevant change regions**. The instruction-conditioned attention maps concentrate on areas where visual change is expected (e.g., the bowl to be stacked, the towel to be folded), rather than spreading attention uniformly across the scene. This supports image editing as an effective alternative to video-based world-action modeling.

### 4.6 Ablation Studies

#### Comparison with Unified Understanding-and-Generation Models
ImageWAM (98.4% on LIBERO, 84.4% Clean RoboTwin) outperforms BagelVLA with keyframe prediction (75.3%) and without (56.7%), showing that the editing-specific pretraining matters — it's not just about having any generative model.

#### Scaling the Backbone
Scaling from FLUX.2 4B to 9B on LIBERO-Plus:
- 4B: 83.1% average
- 9B: 85.2% average (+2.1 points)
Gains are largest on Robot, Language, and Layout perturbations.

---

## 5. Related Work

### 5.1 Image Editing
Text-guided image editing modifies a source image according to language instruction while preserving irrelevant content. Recent progress from diffusion-based and MLLM-enhanced models has advanced from simple object-level edits to complex spatial, semantic, and knowledge-driven modifications. This work is the first to study image editing from a robotics perspective, using its source-conditioned representations as world-action backbones.

### 5.2 World Action Models
WAMs use video generation for visual planning. Early work predicts complete future videos which are then translated to actions via an inverse dynamics model or action decoder. Recent works broaden this by using video generative models as representation extractors for action generation. ImageWAM is the first to propose **image editing as a WAM backbone**, identifying it as offering the right inductive bias for instruction-conditioned manipulation.

### 5.3 Vision-Language-Action (VLA) Models
VLAs fine-tune pretrained vision-language models for action prediction. While effective, they lack explicit world-action modeling. ImageWAM combines the benefits of both — the strong visual understanding from VLMs and the explicit change reasoning from image editing.

---

## 6. Claim Index

| # | Claim | Evidence |
|---|-------|----------|
| C1 | Video-based WAMs face three coupled limitations: cost, irrelevant details, error propagation | Section 1 — qualitative argument supported by efficiency numbers (Table 5/16) and qualitative analysis (Fig. 5) |
| C2 | Image editing provides a better-matched prior for world-action modeling | Sections 2, 3 — three properties identified: instruction-to-change alignment, easier proxy, compact inference |
| C3 | ImageWAM repurposes editing KV caches as world-action context without decoding edited images | Section 3.2-3.4 — method describes cache extraction and single-step inference |
| C4 | ImageWAM outperforms VLA baselines without additional policy pretraining | Table 1 (RoboTwin: 93.38% vs 62.16% π₀), Table 2 (LIBERO: 98.4% vs 76.5% OpenVLA) |
| C5 | ImageWAM matches competitive WAMs without video denoising at inference | Table 1 (93.38% vs 91.83% FastWAM), Table 2 (98.4% vs 97.6% FastWAM) |
| C6 | ImageWAM reduces FLOPs to 1/6 and latency to 1/4 of video-based WAMs | Table 5/16 (9.72 TFLOPs vs 63.65, 263ms vs 1081ms) |
| C7 | ImageWAM generalizes to real-world tasks, outperforming π₀ (+28.7 pts), π₀.₅ (+12.2 pts), FastWAM (+5.5 pts) | Table 4 (84.5% vs 55.8%, 72.3%, 79.0%) |
| C8 | Editing caches focus on task-relevant change regions | Section 4.3, Figure 4 — attention visualization |
| C9 | Gains are not merely from stronger visual recognition or language alignment | Table 6 — comparison with unified understanding-and-generation models shows editing-specific pretraining matters |
| C10 | Instruction conditioning and editing-oriented feature extraction are important | Ablation study (Table 6: BagelVLA w/ K.F. 75.3% vs ImageWAM 84.4% on RoboTwin) |
| C11 | ImageWAM is robust to visual domain shifts (LIBERO-Plus) | Table 3: 83.1% vs 51.5% FastWAM, especially Camera: 80.8% vs 16.4% |
| C12 | Scaling the editing backbone improves performance | Table 7: FLUX.2 4B → 9B improves LIBERO-Plus from 83.1% to 85.2% |

---

## 7. Critical Analysis

### Strengths

1. **Novel and well-motivated problem framing.** The paper identifies a real limitation of video-based WAMs and asks a genuinely productive question. The insight that image editing provides a better inductive bias for instruction-conditioned manipulation is both elegant and practical.

2. **Clean and principled architecture.** The idea of using editing KV caches (not decoded images) as world-action context is clever — it preserves the benefits of generative visual reasoning while avoiding the overhead of explicit video/image decoding.

3. **Strong empirical validation.** Results span multiple simulators (LIBERO, LIBERO-Plus, RoboTwin 2.0) and real-world tasks with four diverse manipulation challenges. The consistent outperformance of VLA baselines without policy pretraining is compelling.

4. **Efficiency numbers are concrete and impressive.** Going from 63.65 TFLOPs → 9.72 TFLOPs and from 1081ms → 69ms (with compilation) is a real practical advantage for real-time robot control.

5. **Open and reproducible.** Project page and code are provided.

### Weaknesses / Limitations

1. **Hidden complexity of "editing cache."** The paper describes extracting KV caches from a specific editing denoising timestep. However, the exact mechanism of how these caches encode "transformation-aware" information is not rigorously analyzed. The attention analysis is qualitative (Figure 4) and could benefit from quantitative attribution metrics.

2. **Comparison to video-based WAMs is somewhat narrow.** The paper primarily compares against FastWAM, which is only one (though recent) video-based WAM. Comparisons with more diverse WAM approaches (e.g., UniPi, SuSIE, or video diffusion planners) would strengthen the claim.

3. **Single endpoint frame may lose temporal information.** Predicting only the endpoint frame (t+H+1) means intermediate state information is discarded. For tasks requiring precise temporal coordination (e.g., catching, rhythm-dependent manipulation), this could be insufficient.

4. **Gap in unified understanding-and-generation comparison.** The comparison with BagelVLA shows ImageWAM is better, but BagelVLA uses a different base architecture. A more controlled ablation — e.g., using the same LLM with and without editing pretraining — would more cleanly isolate the benefit of editing-specific features.

5. **Real-world evaluation size.** 100 demos per task and 50 trials per model per task is modest. While sufficient for initial validation, larger-scale deployment studies would be needed to assess robustness.

6. **Dependence on image editing model quality.** ImageWAM's performance is inherently bounded by the quality of the underlying image editing model. Limitations of the editing backbone (e.g., failure on complex scenes, ambiguous instructions) will propagate to action prediction.

7. **The "world model" claim is subtle.** ImageWAM does not actually model the world's dynamics — it predicts a single future frame and uses editing features. Whether this qualifies as "world-action modeling" vs. "strongly conditioned action prediction" is a definitional question the paper acknowledges but doesn't fully resolve.

---

## 8. Future Research Directions

1. **Multi-step editing rollouts.** Extending ImageWAM to iteratively predict the next endpoint frame as the observation changes, enabling closed-loop re-planning.

2. **Temporal hierarchy.** Combining ImageWAM's efficient single-frame editing with lightweight temporal models for tasks requiring intermediate state information.

3. **Goal-conditioned exploration.** Using the editing model's ability to predict task-relevant visual changes as a reward signal for exploration in reinforcement learning.

4. **Video editing as an intermediate.** Exploring video editing (edit a video clip rather than a single image) as a middle ground between full video generation and image editing.

5. **Formal analysis of editing caches.** Developing quantitative metrics (e.g., mutual information between cache and action, intervention-based causal analysis) to better understand what information editing caches encode.

6. **Scaling across more diverse robot embodiments.** Applying ImageWAM to different robot platforms (single-arm, mobile manipulators, humanoids) to assess generality.

7. **Integration with 3D representations.** Combining image editing with 3D scene representations for tasks requiring explicit geometric reasoning.

---

## 9. Conclusion

The paper presents ImageWAM, a framework that replaces video generation with image editing as the backbone for world-action modeling. By repurposing pretrained image editing models and using their intermediate KV caches as compact world-action context, ImageWAM achieves:

- **State-of-the-art performance** on RoboTwin 2.0 (93.38%), competitive results on LIBERO (98.4%) and LIBERO-Plus (83.1%)
- **Strong real-world generalization** (84.5% average, +5.5 pts over FastWAM)
- **1/6 FLOPs and 1/4 latency** of video-based WAMs
- **Robustness to distribution shift** (dramatically outperforming FastWAM on LIBERO-Plus)

The core message is compelling: for instruction-conditioned robot manipulation, image editing provides a better-matched inductive bias than video generation. The language-vision interaction priors learned during editing pretraining encode the what, where, and how of task-relevant visual changes — precisely the information a robot policy needs to act.
