# DragMesh-2: Physically Plausible Dexterous Hand-Object Interaction with Articulated Objects

**Authors:** Tianshan Zhang\*, Yijia Duan\*, Yanjun Li\*, Zeyu Zhang\*†, Hao Tang‡  
**Affiliation:** School of Computer Science, Peking University  
**Paper:** arXiv:2606.15133 ([PDF](https://arxiv.org/pdf/2606.15133))  
**Code:** [https://github.com/AIGeeksGroup/DragMesh-2](https://github.com/AIGeeksGroup/DragMesh-2)  
**Website:** [https://aigeeksgroup.github.io/DragMesh-2](https://aigeeksgroup.github.io/DragMesh-2)

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Key Challenge](#2-key-challenge)
3. [Related Work and Gap Analysis](#3-related-work-and-gap-analysis)
4. [Method Overview](#4-method-overview)
5. [Contact-Driven Task Formulation](#5-contact-driven-task-formulation)
6. [PICA: Physically Informed Contact-Aware Training](#6-pica-physically-informed-contact-aware-training)
7. [PICA Reward Design](#7-pica-reward-design)
8. [PICA Auxiliary Supervision](#8-pica-auxiliary-supervision)
9. [Heuristic Reference Trajectory Dataset](#9-heuristic-reference-trajectory-dataset)
10. [Experimental Setup](#10-experimental-setup)
11. [Baselines and Ablations](#11-baselines-and-ablations)
12. [Main Results](#12-main-results)
13. [Ablation Study](#13-ablation-study)
14. [Diagnostic Analysis: Nominal Success Masks Saturation Collapse](#14-diagnostic-analysis-nominal-success-masks-saturation-collapse)
15. [Additional Studies](#15-additional-studies)
16. [Limitations](#16-limitations)
17. [Claim Index](#17-claim-index)
18. [Critical Analysis](#18-critical-analysis)
19. [Research Directions](#19-research-directions)

---

## 1. Problem Statement

Dexterous interaction with articulated objects is a fundamental capability for household robotics, assistive systems, and humanoid manipulation. Unlike static-object manipulation where the robot directly controls the target, articulated-object manipulation presents a fundamentally different control structure: **the target part cannot be directly actuated**. Instead, its motion must emerge through sustained physical contact between the dexterous hand and the object's handle.

The critical gap this paper addresses is the **transition from object-centric articulated generation to hand-driven dexterous hand–object interaction**. Prior work, including the authors' own DragMesh 1 ([Zhang et al., 2025]), showed that explicit articulation priors can convert user interaction into articulated motion following kinematic constraints — but this operates in an object-centric paradigm. The challenge is to move from geometric trajectory replay or open-loop execution to closed-loop contact-driven interaction, where articulated motion arises through real physical hand–handle engagement.

**The core insight:** Success under nominal dynamics does not imply stable contact behavior. Policies trained only for task completion under fixed dynamics overfit nominal contact loads and degrade rapidly when contact loads change.

---

## 2. Key Challenge

The transition from object-centric generation to hand-driven interaction is non-trivial for several reasons:

1. **No direct actuation channel:** The policy controls only the hand (51-DoF SMPL-X). The object joint has no action channel. Articulated motion can only arise through hand–handle contact.
2. **Contact dynamics are unobserved:** Without tactile or force feedback, the policy must infer contact state indirectly from kinematic error and positional state.
3. **Overfitting to nominal dynamics:** RL policies trained under fixed dynamics exploit dynamics shortcuts (e.g., pushing hard under low damping) rather than learning stable contact behaviors.
4. **Action saturation:** Under increased damping, policies tend toward saturated joint commands (clip099 → 1.0), breaking contact and destabilizing motion.
5. **Policies degrade under OOD contact loads:** A policy achieving 1.00 success at nominal damping can collapse to 0.10 at ×4 damping.

---

## 3. Related Work and Gap Analysis

### Articulated Object Understanding and Manipulation
Prior work addresses articulated object understanding through part-level perception, pose estimation, joint parameter prediction, and simulation platforms. Manipulation methods either infer articulation models for planning or learn actionable representations from observations. **Gap:** These target object/scene-level manipulation with mobile manipulators or grippers, not multi-finger contact-rich interaction with articulated parts.

### Dexterous Hand-Object Manipulation
Classical methods use contact mechanics and force closure but require accurate models. RL methods achieve strong performance on rigid-object in-hand manipulation. Recent work extends to articulated objects with benchmarks and datasets. **Gap:** Evaluation focuses on task progress/success, ignoring whether contacts are physically stable, interpenetration is limited, and motion is coordinated.

### Physics-Grounded Manipulation Learning
Domain randomization handles dynamics variation through data diversity. Sim-to-real methods condition policies on latent dynamics parameters inferred from history. **Gap:** These factors are typically low-dimensional and global — unsuited for capturing local, state-dependent responses that vary with handle geometry, finger configuration, and part motion.

**PICA's motivation:** Use short-horizon interaction history as a task-level signal for contact-rich articulated manipulation, with separate action-bound and contact-preserving regularization inspired by constrained RL.

---

## 4. Method Overview

DragMesh-2 is a **contact-driven framework** that extends DragMesh-style articulated interaction from object-centric motion generation to dexterous hand–object interaction. The key architectural insight is that the **policy controls only the hand** — the target joint has **no action channel**, and articulated motion must emerge through sustained physical contact.

**PICA** (Physically Informed Contact-Aware training) injects physically informed signals into policy learning without tactile or force feedback, operating at two levels:
- **Environment level:** Reward augmentation with contact maintenance, action regularization, detachment handling
- **Policy level:** Temporal contact-response prediction via auxiliary supervision

---

## 5. Contact-Driven Task Formulation

**Hand configuration:** 51-DoF SMPL-X hand (6 virtual wrist DoFs + 45 finger joints).

**Task constraint:** Policy controls only the hand; object joint has no action channel. Target part moves only through hand–handle contact.

**Success threshold (Equation 1):**
```
q_done = q_min^{traj} + ρ · (q_max^{traj} - q_min^{traj})
```
Where ρ = 0.75 by default, and the range is object-specific from the reference trajectory.

**Task progress normalization (Equation 2):**
```
p_t = max(0, (q_t^o - q_start) / (q_goal - q_start))
```
This normalizes drawers, sliders, and doors onto comparable scales.

**Observation:** Hand joint positions + velocities, handle pose, relative palm–handle geometry, target-joint state, task-scale features (progress, distance to success). No RGB, depth, point clouds, force, or tactile signals.

**Action:** 51-dimensional increment to hand PD target, clipped to joint limits.

**Reference trajectory role:** Initializes expert grasp, defines target motion scale, provides non-learned tracking baseline. Not replayed as object-control command; does not provide expert action labels.

---

## 6. PICA: Physically Informed Contact-Aware Training

PICA augments PPO with observable physical proxies across two levels:

### History Token (Equation 3)
```
h_t = [e_t, a_{t-1}],  e_t = q_t^{PD} - q_t^h
```
Combines current PD tracking error and previous action.

### Temporal Encoding
A **GLA encoder** (Gated Linear Attention, [Yang et al. 2024]) maps the recent token block to a contact-history feature. This captures temporal structure in the interaction dynamics.

### Causal-Window Auxiliary Head (Equation 4)
Predicts 4 observable contact-response targets from the temporal feature:

```
y_t = [q_t^o - q_{t-K}^o,                       # Recent object response
       max_{τ∈[t-K,t]} d_τ,                      # Max palm–handle distance
       1(max_{τ∈[t-K,t]} d_τ > d_detach),        # Detachment risk (binary)
       max_{τ∈[t-K,t]} ||e_τ||_2]                # Tracking stress
```

Where K is the causal window size, d_τ is palm–handle distance, and d_detach is the detachment threshold.

---

## 7. PICA Reward Design

The complete reward function (Equation 5) augments task progress with contact-aware terms:

```
r_t = r_task + r_dist + r_act + r_time + r_detach + r_success + r_bound + r_contact
```

| Component | Purpose |
|-----------|---------|
| r_task | Task progress toward success threshold |
| r_dist | Contact maintenance (palm–handle proximity) |
| r_act | Action regularization (penalize large actions) |
| r_time | Time penalty (encourage efficiency) |
| r_detach | Detachment handling (triggered after hand enters and leaves effective contact range) |
| r_success | Bonus on successful task completion |
| r_bound | Action-bound regularization |
| r_contact | Contact encouragement |

The reward signal drives not just task progress but also **whether the task is completed under contact-maintaining and action-regularized conditions**.

---

## 8. PICA Auxiliary Supervision

The PICA loss function (Equation 6):

```
ℒ = ℒ_PPO + c_v · ℒ_V + c_b · ℒ_bounds + w_aux · ℒ_aux
```

The auxiliary loss ℒ_aux updates the temporal encoder to predict the 4 contact-response targets, biasing learning away from nominal-success shortcuts toward contact-conditioned interaction.

**Physical diagnostics** reported alongside task success:
- **clip099:** Fraction of rollout steps where max action magnitude exceeds 0.99
- **detach_proxy:** Detachment-failure rate

**Robustness metrics (Equation 7):**
For damping set B = {×1, ×2, ×4} and mode m ∈ {det, stoch}:
```
S̄_m = (1/|B|) Σ_{b∈B} S_{b,m}         # Mean across dampings
S^{worst}_m = min_{b∈B} S_{b,m}         # Worst-case damping
```

---

## 9. Heuristic Reference Trajectory Dataset

The dataset is generated **heuristicially, without learning**, directly from GAPartNet geometry. A geometry-guided procedure reads part, handle, and joint-mobility annotations with an SMPL-X hand model and emits a phased interaction trajectory: **approach → grasp → drag → release**.

| Category | # Trajectories |
|----------|---------------|
| StorageFurniture | 256 |
| TrashCan | 7 |
| Dishwasher | 5 |
| Refrigerator | 4 |
| Oven | 3 |
| Microwave | 1 |
| TableObject | 1 |
| **Total** | **277** |

**Three roles in DragMesh-2:**
1. Initializes expert grasp state and target motion scale for RL
2. Defines non-learned trajectory-tracking baseline
3. Released as pure-geometry interaction resource for future HOI research

---

## 10. Experimental Setup

**Benchmark:** 7 GAPartNet objects across 3 categories (Dishwasher, StorageFurniture, Microwave) and 2 joint types (5 revolute doors, 2 prismatic drawers).

**Episodes:** 20 per (method, object, damping, mode) cell.

**Execution modes:**
- **Deterministic:** Uses Gaussian mean
- **Stochastic:** Samples from learned policy distribution

**Damping conditions:**
- **×1:** Nominal performance
- **×2:** Mild contact-load shift
- **×4:** Strong OOD contact-load shift

**Starting state:** All episodes start from the expert grasp state (initialized from heuristic dataset).

**Simulation:** Isaac Gym-based physics simulation.

---

## 11. Baselines and Ablations

### Non-learned baselines
1. **Trajectory tracking replay:** Open-loop playback of reference trajectory
2. **GT-part-pose parallel-jaw primitive:** Ground-truth part pose + parallel-jaw gripper

### Learned baselines
3. **State-only PPO:** No temporal history in observation
4. **Flat-history PPO:** Fixed-length concatenated history
5. **GRU-PPO:** GRU temporal encoder
6. **Transformer-PPO:** Transformer temporal encoder

### Ablations
7. **w/o PICA (GLA only):** Retains GLA temporal encoder, drops PICA physical signals
8. **w/o GLA (PICA only):** Retains physical signals with flat-history encoder (no GLA)

---

## 12. Main Results

### Summary (Figure 2 + Table 2)

PICA achieves the **highest mean success in all six mode × damping settings** and retains the highest absolute success under strong damping.

| Method | ×1 Det | ×2 Det | ×4 Det | ×1 Stoch | ×2 Stoch | ×4 Stoch |
|--------|--------|--------|--------|----------|----------|----------|
| Traj. tracking | 1.00 | 0.71 | 0.71 | — | — | — |
| Parallel-Jaw | 0.14 | 0.14 | 0.14 | — | — | — |
| State-only PPO | 0.58 | 0.44 | 0.27 | 0.44 | 0.35 | 0.26 |
| Flat-history PPO | 0.43 | 0.36 | 0.32 | 0.34 | 0.19 | 0.21 |
| GRU-PPO | 0.51 | 0.33 | 0.30 | 0.44 | 0.27 | 0.28 |
| Transformer-PPO | 0.35 | 0.23 | 0.09 | 0.25 | 0.11 | 0.04 |
| **PICA (Ours)** | **0.89** | **0.80** | **0.56** | **0.82** | **0.72** | **0.43** |

### Four Key Findings

1. **Trajectory tracking** reaches 1.00 at ×1 on all objects but drops to 0.71 at ×2/×4 — open-loop replay alone is not OOD-robust.

2. **Parallel-jaw primitive** succeeds on only 1/7 objects (0.14 mean) and is damping-invariant — a geometric primitive cannot substitute for closed-loop dexterous contact control even with GT part pose.

3. **PICA attains best mean in every damping/mode column:**
   - ×1 det: 0.89 vs 0.58 (state-only PPO)
   - ×4 det: 0.56 vs 0.27 (state-only PPO), vs 0.09 (Transformer-PPO)

4. **Richer temporal encoders alone don't close the gap:** GRU (0.30), Transformer (0.09), and GLA-only ablation (0.36) all lag PICA by ≥0.13 at ×4. The win is the **combination** of physical signals with temporal contact-response modeling.

### Per-Object Heterogeneity
No single method dominates every object instance. PICA shows broad coverage but fails on some objects (e.g., 48513 StorageFurniture door at ×4: 0.10 deterministic).

---

## 13. Ablation Study

Table 3 isolates the two physical-structure components of PICA:

| Method | ×1 Det | ×2 Det | ×4 Det | ×1 Stoch | ×2 Stoch | ×4 Stoch |
|--------|--------|--------|--------|----------|----------|----------|
| w/o PICA (GLA only) | 0.65 | 0.56 | 0.36 | 0.68 | 0.64 | 0.35 |
| w/o GLA (PICA only) | 0.75 | 0.71 | 0.43 | 0.77 | 0.57 | 0.36 |
| **PICA (full)** | **0.89** | **0.80** | **0.56** | **0.82** | **0.72** | **0.43** |

- Physical signals contribute more under nominal damping
- Temporal encoder helps more under stochastic mid-damping
- Components are **complementary**, not redundant
- Full model exceeds either component by ≥0.13 at ×4

---

## 14. Diagnostic Analysis: Nominal Success Masks Saturation Collapse

This is a key methodological contribution of the paper. Table 4 shows the effect of varying training length on a single object:

| Training Epochs | Succ. ×1 | Succ. ×4 | clip099 ×4 |
|----------------|----------|----------|------------|
| 150 | 0.90 | 0.55 | 0.90 |
| 200 | 0.90 | 0.50 | 0.97 |
| 300 | 1.00 | 0.10 | 0.99 |
| 500 | 1.00 | 0.10 | 0.99 |

**Key insight:** As training extends from 150 to 500 epochs, nominal (×1) success rises from 0.90 to 1.00, but ×4 success **collapses** from 0.55 to 0.10, while clip099 climbs toward 1.0. Longer training buys nominal success by driving the policy into a **saturated, low-robustness regime**.

This directly motivates:
1. Reporting OOD damping and saturation alongside success
2. Checkpoint selection by OOD robustness, not training reward

---

## 15. Additional Studies

The appendix reports:
- **Extended fine-tuning** does not yield stable additional OOD gains
- **Damping-range expansion** also does not improve OOD robustness
- **Rollout-level diagnostics** confirm the contact-aware saturation and detachment metrics
- The convergence point: robustness under strong contact load requires **richer contact interfaces**, not longer optimization or wider damping distribution

---

## 16. Limitations

1. **Action saturation:** Even with PICA, the policy relies on a position-increment action interface and tends toward saturation under strong contact load. Success drops from 0.89 (×1) to 0.56 (×4).

2. **Per-object heterogeneity:** No single policy dominates every instance. Some objects (e.g., 48513 StorageFurniture door at ×4) show PICA success as low as 0.10.

3. **No force/tactile feedback:** Contact state inferred only from kinematic error — insufficient for stable light pulling at high damping.

4. **Isolated task:** Contact-driven pulling from an expert grasp state with a floating hand — not yet coupled with whole-body control or locomotion.

---

## 17. Claim Index

| ID | Claim | Evidence |
|----|-------|----------|
| C1.1 | Articulated objects cannot be directly controlled; motion must emerge through sustained hand–object contact | This is the core task formulation — Section 3.1: policy controls only hand, object joint has no action channel |
| C1.2 | Geometric replay or open-loop execution fails to capture contact dynamics | Experimental: trajectory tracking drops from 1.00 at ×1 to 0.71 at ×2/×4 |
| C1.3 | Policies overfit nominal dynamics without tactile/force feedback | Training-length study (Table 4): nominal success rises but ×4 success collapses |
| C1.4 | PICA injects physical signals without tactile/force feedback | Method Section 3.2: reward and auxiliary loss design |
| C2.1 | PICA attains the highest mean success in all six mode × damping settings | Table 2: PICA best in every column |
| C2.2 | PICA retains highest absolute success under strong damping | ×4 deterministic: 0.56 (PICA) vs 0.27 (state-only PPO) vs 0.09 (Transformer-PPO) |
| C2.3 | Richer temporal encoders alone do not close the gap to PICA | GRU (0.30), Transformer (0.09), GLA-only (0.36) all lag PICA (0.56) at ×4 by ≥0.13 |
| C2.4 | The win is the combination of physical signals with temporal modeling, not the encoder alone | Ablation Table 3: full PICA exceeds either component by ≥0.13 at ×4 |
| C2.5 | Loss of contact at OOD damping is due to saturated action, not policy failure to track | Table 4: clip099 rises to 0.99 as ×4 success collapses |
| C3.1 | Physical signals contribute more under nominal damping, temporal encoder under stochastic | Ablation Table 3: w/o GLA at ×1 (0.75) vs w/o PICA at ×1 (0.65) |
| C3.2 | Components are complementary rather than redundant | Full model > either component at all damping levels |
| C3.3 | No single policy dominates every object instance | Table 2 per-object: objectives vary substantially |
| C3.4 | Parallel-jaw primitive cannot substitute for dexterous contact control | Only 0.14 mean success across all objects and dampings |
| C3.5 | Extended fine-tuning and damping-range expansion do not yield stable OOD gains | Appendix C.4, C.5 |
| C4.1 | Longer training buys nominal success by driving policy into saturated, low-robustness regime | Table 4: from 150→500 epochs, ×1 goes 0.90→1.00 but ×4 drops 0.55→0.10 |
| C4.2 | Nominal success does not guarantee stable contact behavior | Key insight throughout the paper |
| C4.3 | Dataset contains 277 trajectories over 7 GAPartNet categories | Table 1 |
| C4.4 | Dataset generated heuristicially, without learning, from GAPartNet geometry | Section 3.3 |

---

## 18. Critical Analysis

### Strengths
1. **Well-motivated problem formulation:** The transition from object-centric to hand-driven contact interaction is genuinely non-trivial, and the paper articulates this clearly.
2. **PICA is practical:** Requires no tactile/force sensors — just observable kinematic signals. This is important for real-world applicability.
3. **Diagnostic contribution finding:** The demonstration that nominal success masks saturation collapse (Table 4) is valuable for the community — many RL papers report only nominal performance.
4. **Robustness evaluation protocol:** Systematic evaluation across ×1, ×2, ×4 damping + deterministic/stochastic execution is more thorough than typical manipulation papers.
5. **Complementarity analysis:** The ablation cleanly shows that physical signals and temporal encoding contribute along different axes.

### Weaknesses
1. **Simulation-only quantitative evaluation:** The hardware example (Figure 3) is purely qualitative. No real robot experiments with sim-to-real transfer are reported.
2. **Limited object diversity:** 7 objects from GAPartNet, heavily dominated by StorageFurniture (256/277 trajectories).
3. **Per-object variance is high:** PICA fails on some objects even at nominal damping (e.g., 45661 StorageFurniture door: 0.85 at ×1, which is not ceiling-level).
4. **Damping as the only contact-load variation:** Real-world contact loads vary in more dimensions than damping (friction, surface compliance, jamming, etc.).
5. **No comparison with force/tactile-based methods:** Since PICA claims to work without them, a comparison with the same architecture + force feedback would be instructive.
6. **Floating hand assumption:** No arm or body — limits applicability to real humanoid systems.

### Reproducibility
Code is available on GitHub. The heuristic dataset generator, simulation environment (Isaac Gym), and policy training pipeline are released. However, the specific damping coefficients, randomization ranges, and reward weights are in the appendix, making reproduction feasible but requiring careful parameter matching.

---

## 19. Research Directions

1. **Enrich contact interface with force/tactile feedback** — The paper identifies this as the primary next step. Adding wrist force-torque sensing or tactile fingertips could allow the policy to regulate grip force directly.

2. **Whole-body humanoid loco-manipulation** — Couple the upper-body contact interaction with whole-body control using the dataset as a motion-scale prior.

3. **Sim-to-real transfer** — Validate PICA on physical hardware with damping variation (e.g., different handle surfaces, lubrication conditions).

4. **Beyond damping: multi-dimensional contact-load variation** — Test under friction changes, surface compliance, handle geometry variations, and joint jamming.

5. **Multi-object generalization** — Train on more diverse articulated objects and test zero-shot generalization.

6. **Replace position-increment action with torque/force control** — Address action saturation directly at the control interface level.

7. **Integration with visual perception** — Add RGB-D perception for object-agnostic handle detection and grasping without expert grasp initialization.
