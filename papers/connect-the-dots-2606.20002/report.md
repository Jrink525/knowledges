# Connect the Dots: Training LLMs for Long-Lifecycle Agents with Cross-Domain Generalization Via Reinforcement Learning

**Paper:** arXiv:2606.20002  
**Authors:** Yanxi Chen, Weijie Shi, Yuexiang Xie, Boyi Hu, Yaliang Li, Bolin Ding, Jingren Zhou (Alibaba Group)  
**Date:** June 2026 (v1)  
**Tags:** `LLM`, `reinforcement-learning`, `agent`, `meta-RL`, `long-lifecycle`, `generalization`

---

## 1. Problem Statement

**What problem does this paper solve?**  
Frontier LLMs today lack the meta-capability to "Connect the Dots" (CoD) — the ability to continuously learn from experience and self-improve during long-lifecycle deployment. When deployed as agents, they get lost in underspecified environments and require human-crafted agent scaffolds. The paper argues that this meta-capability can and should be explicitly trained via end-to-end reinforcement learning.

**Why does it matter?**  
As LLMs evolve from chatbots to real-world AI agents deployed over extended periods, the ability to accumulate knowledge about an environment and transfer it across tasks becomes crucial. Without this, each task is solved from scratch — a fundamental inefficiency that limits the potential of long-lifecycle agentic systems.

**Key gap identified:**  
Standard task-by-task RL trains an LLM to solve each task individually from scratch, which is misaligned with the CoD meta-capability needed for long-lifecycle deployment. Prior work on lifelong agents lacks dedicated LLM post-training for this meta-capability.

---

## 2. The Core Idea: Connect the Dots

The paper defines **CoD meta-capability** formally as:

> During long-lifecycle deployment in an environment, an AI agent continuously solves a sequence of different-but-related tasks, while proactively and deliberately exploring the environment and self-updating its context about it, thereby facilitating more effective task solving within the same environment in the future.

Unlike domain-specific capabilities (math problem solving, competitive coding), CoD is a **meta-capability** that can generalize across diverse environments from different domains.

---

## 3. The CoD Framework: Two Components

The framework has two interconnected components:

### CoD-Deploy (Deployment Abstraction)
An abstraction of long-lifecycle agentic deployment in an environment M:
- Interleaves **solve-task episodes** (solving task x_i^M) and **update-context episodes** (updating context from z_i^M to z_{i+1}^M)
- Can be understood as gradient-free online learning via trial-and-errors
- Each block (task or update) may itself be a long-horizon multi-turn episode

### CoD-Train (Training Process)
The RL post-training process with rollout pattern matching CoD-Deploy:
- Covers diverse environments (A, B, ...) for generalization
- Goes up **one level in the hierarchy** compared to standard task-by-task RL
- Rollout trajectory evolution: tokens → turns → tasks (for long-lifecycle deployment)

**Claim C1.1:** CoD-Train goes up by one level in RL hierarchy compared to standard RL. The definition of one rollout trajectory in LLM-RL has evolved from single-turn tokens (RLHF), to multi-turn sequences for long-horizon tasks, to multi-task sequences for long-lifecycle deployment.

**Claim C1.2:** If there is at least an outcome reward for solving each task, the density of reward signals in CoD-Train is independent of the total number of tasks (reward values grow proportionally with number of tasks).

---

## 4. The RL Algorithm: Credit Assignment Across Episodes

A major challenge is credit assignment across solve-task and update-context episodes in a long state-action sequence. The paper adopts the **dynamic-programming principle**: each episode should maximize not only the immediate reward, but also future rewards.

### GRPO-Style Algorithm with Fine-Grained Credit Assignment

The paper adopts GRPO (Shao et al., 2024) with modifications:

1. **Return Definition (Rewards-to-Go):**
   - Solve-task return: R^x_{i,j} = (1/(S-j)) Σ_{ℓ=j}^{S-1} r^x_{i,ℓ}
   - Update-context return: R^z_{i,j} = (1/(S-j+1))(r^z_{i,j} + Σ_{ℓ=j}^{S-1} r^x_{i,ℓ})
   - Each episode's return = mean of current episode reward PLUS future solve-task rewards

2. **Baseline Calculation:**
   - Episodes at the same position in rollout trajectories form one group
   - Averaged return = baseline for advantage calculation
   - A^x_{i,j} = R^x_{i,j} - R̄^x_j (advantage = return - group mean)

3. **Gradient Calculation:**
   - Starts from REC-OneSide-NoIS (discards importance-sampling weights)
   - Adds adaptive re-weighting (RED-Weight) to address training instability
   - Adaptive temperature T via bisection such that Σ A_i exp(A_i/T) ≈ 0
   - Hard constraint T > 0.8 to avoid numerical instability

**Claim C2.1:** The vanilla GRPO and REC-OneSide-NoIS methods cause training instability on Alchemy-Random domains, correlating with decaying mean advantage.

**Claim C2.2:** The adaptive RED-Weight augmentation (Eq. 3) leads to the most stable training among the three compared methods.

---

## 5. Infrastructure

Built on **Trinity-RFT** (Pan et al., 2025), an LLM-RL framework with modular, decoupled design. The implementation uses an environment-wise meta-workflow following CoD-Deploy, so any task and rollout workflow can be plugged in after minor modifications.

### Context Mechanism
Minimalistic instantiation: cross-episode context = "hint" — a single piece of text appended to the system prompt in solve-task episodes. The paper acknowledges this is sufficient for proof-of-concept but notes future work should generalize to persistent memory banks or Markdown skills files.

---

## 6. Task and Environment Design

The paper argues that generic environments for standard RL are not suitable for CoD, and designs three dedicated environments:

### FrozenLake-Obscure (Sanity-Check Testbed)
- Classic FrozenLake grid navigation, but action space uses abstract symbols (A/B/C/D)
- Action-to-direction mapping randomly permuted per environment, unknown a priori
- Creates **information-theoretic limit**: solving each task from scratch cannot exceed ~45% success rate
- Agent must figure out the mapping across episodes and transfer this hint

**Claim C3.1:** FrozenLake-Obscure imposes an information-theoretic limit on per-task success rate due to unknown action mapping (e.g., 75% failure probability in first step if starting position surrounded by holes).

### Alchemy-Random (Richer Behavior)
- Inspired by the Alchemy benchmark (Wang et al., 2021)
- Each environment has random elements and recipes (fixed after initialization)
- Agent must synthesize target elements without knowing recipes
- Good hints: valid recipes + failed combinations + task-solving strategies
- Compared to FrozenLake-Obscure: more diverse environments, wider difficulty range, richer behaviors

### TerminalSimulator (Cross-Domain Evaluation Only)
- Simulates Linux/MacOS/Windows terminal daily tasks (file manipulation, transferring)
- Agent executes terminal commands and receives feedback
- Useful for evaluating cross-domain generalization of the CoD meta-capability

---

## 7. Experimental Setup

### Settings
- **Setting A:** CoD-Train on FrozenLake-Obscure only, task sequences of length 4
- **Setting B:** CoD-Train on mixture of FrozenLake-Obscure and Alchemy-Random, task sequences of length 4
- Base model: Qwen3-8B-Instruct (thinking disabled)
- Rollout batch size: 32, group size: 8
- Task sequence length: 4 (train), 8 (eval)

### Evaluation Dimensions
1. **In-domain OOD generalization:** Harder environment instances (larger maps, more elements), longer task sequences (length 8)
2. **Cross-domain OOD generalization:** Unseen domains (e.g., TerminalSimulator)
3. **Ralph-loop generalization:** Repeatedly solving the same task to arrive at a better solution

---

## 8. Key Empirical Results

### Setting A (FrozenLake-Obscure Only)

| Metric | Before CoD-Train | After CoD-Train | Improvement |
|--------|-----------------|-----------------|-------------|
| Position 0 (first task, no context) | ~18% | ~45% | +27pp |
| Position 3 (fourth task, conditioned on context) | ~28% | ~76% | +48pp |

**Claim C4.1:** Training reward curves grow with RL steps, and higher rewards are achieved at later positions within a task sequence. The gap between position 0 and position 3 widens during training, showing the learned CoD capability.

**Claim C4.2:** In-domain OOD generalization holds — performance improvements persist on harder environment instances and longer task sequences (length 8).

**Claim C4.3:** Cross-domain generalization to Alchemy-Random and TerminalSimulator (both CoD-Deploy and Ralph-loop settings) shows performance improvements, validating that CoD-Train elicits a generalizable meta-capability.

### Setting B (FrozenLake-Obscure + Alchemy-Random Mixture)

**Claim C5.1:** Training reward curves are less stable than Setting A (minor degradation in Alchemy-Random curves), but overall conclusions are similar — CoD-Train effectively elicits and generalizes the meta-capability.

**Claim C5.2:** Alchemy-Random evaluation reward curves grow rapidly in early steps but fluctuate later, suggesting room for improvement in multi-domain CoD training.

### TerminalSimulator Cross-Domain Results

**Claim C6.1:** In CoD-Deploy setting with different tasks, later tasks show no performance gain — likely because TerminalSimulator tasks in one sequence are not closely related.

**Claim C6.2:** In Ralph-loop setting (repeated attempts at same task), later episodes achieve higher rewards, suggesting the learned meta-capability helps within each solve-task episode.

---

## 9. Related Works: Connections and Distinctions

### Lifelong Agents
- Surge of research on lifelong agents (ICLR 2026 workshop)
- Context management crucial for computational expressivity (Cui et al., 2026)
- Key gap: **no dedicated LLM post-training** for the meta-capability required by lifelong agents
- CoD trains model weights so LLM becomes proficient at both solving tasks AND self-updating context

### Meta Reinforcement Learning (RL²)
- CoD closely related to RL² paradigm (Duan et al., 2016)
- **Key difference 1:** RNN context is fixed-compute, fixed-size; LLM context can be adaptive-size, generated through thinking
- **Key difference 2:** LLMs introduce new opportunities for OOD generalization compared to pre-LLM era
- Contrast with LaMer/Jiang, MAGE/Yang, Orbit/Lin: these works use repeated attempts for the same task, not the classic meta-RL form
- CoD does not require "anchor states" assumption (unlike GiGPO in LaMer/MAGE)
- CoD's fine-grained credit assignment enables effective training where coarse-grained approaches (Orbit) fail

### LLM Inference Scaling (Ralph Loop)
- Ralph loop = special case of CoD-Deploy where task sequence consists of repeated instances of the same task
- RL training for test-time scaling (Hu et al., 2026; Kimi-Team, 2026)
- Key distinction: reflection-and-retry methods train LLM to solve tasks from scratch (context removed during gradient computation), while CoD explicitly trains the LLM to adapt to new environments conditioned on maintained context

---

## 10. Algorithm Details (Appendix A)

### Full Notation
- S tasks: x_0, ..., x_{S-1}
- G end-to-end rollout trajectories per task sequence
- r^x_{i,j} = reward for j-th solve-task episode in i-th trajectory
- r^z_{i,j} = reward for j-th update-context episode in i-th trajectory

### Gradient Methods Compared
1. **Vanilla GRPO (Eq. 1):** Standard importance-sampling weights + clipping
2. **REC-OneSide-NoIS (Eq. 2):** Discards IS weights, keeps clipping — theoretically justified for outcome-reward RLVR
3. **Adaptive RED-Weight (Eq. 3):** Augments REC-OneSide-NoIS with token-level re-weighting when mean advantage is negative; temperature T selected via bisection with constraint T > 0.8

**Conclusion from comparison:** Vanilla GRPO shows unstable reward curves; REC-OneSide-NoIS is even worse; the adaptive re-weighting method produces the most stable training among all three.

---

## 11. Hyperparameters and Configurations (Appendix B)

### Key Hyperparameters
| Parameter | Value |
|-----------|-------|
| Model | Qwen3-8B-Instruct |
| Learning rate | 1.0×10⁻⁶ |
| Gradient clipping | 1.0 |
| KL coefficient | 0 |
| Rollout batch size | 32 |
| Rollout group size | 8 |
| Sampling temperature | 1.0 |
| Max response tokens (cap) | 2,000 |
| Policy loss | REC-OneSide-NoIS, ϵ=0.2 |
| RED-Weight constraint | T > 0.8 |

### Environment Difficulty
| Environment | Easy | Hard |
|-------------|------|------|
| FrozenLake-Obscure map | 4-5 | 6-7 |
| Alchemy-Random base elements | 3-4 | 4-6 |

---

## 12. Prompt Design (Appendix C)

The paper provides detailed prompt templates for:

1. **Update-context episodes:** Generic prompts asking the agent to preserve useful guidance, discard incorrect information, and incorporate new lessons from trajectories. Response format: thinking section + hints section in Markdown.

2. **Solve-task episodes (FrozenLake-Obscure):** Describes the game, hidden clues about action mapping, reward structure, response format with <answer> tags, and optional hints section.

3. **Solve-task episodes (Alchemy-Random):** Describes crafting mechanics, tier system, recipe discovery, and response format.

4. **Solve-task episodes (TerminalSimulator):** Lists available commands, environment details, task descriptions, and response format.

---

## 13. Hint Examples (Appendix D)

Three concrete examples of hints generated during update-context episodes:

1. **FrozenLake-Obscure hint:** Action-to-direction mapping (Direction 1=right, 2=up, 3=down, 4=left), navigation strategy, and general advice

2. **Alchemy-Random hint:** Tier-by-tier recipe breakdown (lqlrr+gwzzz=hjklt, lqlrr+vbpzh=nlji, hjklt+nlji=joouk, joouk+joouk=fhsj) with synthesis strategy

3. **TerminalSimulator hint:** Distilled command sequences (use scp for remote file copy, use unzip for extraction, navigate with cd before extracting)

---

## 14. Limitations and Open Questions

The paper candidly acknowledges several limitations:

1. **RL algorithm caveats:** Heuristic augmentations remain; need for more principled, theoretically grounded algorithm
2. **Return calculation:** Using average of rewards-to-go may become problematic as task sequences scale up; discounting or sliding windows could help
3. **Baseline comparability:** Episodes at the same position from different trajectories start with different context, making baselines not fully comparable
4. **Context mechanism:** Current "hint" is minimalistic; needs generalization to persistent memory banks, Markdown skills files
5. **Environment diversity:** Only 3 environments (FL-Obscure, Alchemy-Random, TerminalSimulator); more needed
6. **Task sequence length:** Limited to 4 (train) / 8 (eval); longer sequences needed
7. **Non-stationary environments:** Not yet evaluated
8. **Broad OOD generalization:** Not yet validated across wider range of environments

---

## 15. Broader Impacts and Future Directions

### Integration with LLM Post-training
CoD is **complementary** (not alternative) to standard task-by-task RL — akin to fluid vs. crystallized intelligence. Two ideas proposed:
1. CoD-Train as an extra sequential stage in post-training
2. Train CoD teacher model → model merging via on-policy distillation

### Key Open Questions
- Will CoD-Train with game/synthetic environments generalize to real-world scenarios (personal assistant, coding agent)?
- Can CoD-Train automatically decide what to learn into model weights vs. context?
- What benefits arise from the natural integration of text-based environment feedback in CoD-Train and CoD-Deploy?

---

## 16. Claim Index

| Claim ID | Section | Summary | Evidence Type |
|----------|---------|---------|---------------|
| C1.1 | §2 | CoD-Train goes up one level in RL hierarchy | Conceptual argument |
| C1.2 | §2 | Reward signal density independent of task count | Formal observation |
| C2.1 | §3.1, App A | Vanilla GRPO + REC-OneSide-NoIS cause instability on Alchemy-Random | Empirical (Fig. 5) |
| C2.2 | §3.1, App A | Adaptive RED-Weight produces most stable training | Empirical (Fig. 5) |
| C3.1 | §3.2 | FL-Obscure creates information-theoretic limit | Formal argument + example |
| C4.1 | §3.3 | Training rewards grow; position 3 >> position 0 | Empirical (Fig. 3) |
| C4.2 | §3.3 | In-domain OOD generalization holds | Empirical (Fig. 3) |
| C4.3 | §3.3 | Cross-domain generalization to Alchemy-Random and TerminalSimulator | Empirical (Fig. 3) |
| C5.1 | §3.3 | Setting B training less stable but similar conclusions | Empirical (Fig. 4) |
| C5.2 | §3.3 | Alchemy-Random evaluation curves fluctuate later | Empirical (Fig. 4) |
| C6.1 | §3.3 | CoD-Deploy TerminalSimulator: later unrelated tasks show no gain | Empirical observation |
| C6.2 | §3.3 | Ralph-loop TerminalSimulator: later episodes achieve higher reward | Empirical observation |

---

## 17. Methodology Assessment

**Strengths:**
- Clear problem-motivation → framework → implementation → evaluation flow
- Well-designed environments with information-theoretic justification
- Thorough ablation of gradient methods (3 methods compared in Appendix A)
- Multi-dimensional OOD evaluation (in-domain, cross-domain, Ralph-loop)
- Open-source release of implementations
- Principled connection to prior work (RL², lifelong agents, inference scaling)
- Honest about limitations and open questions

**Weaknesses:**
- Small-scale proof-of-concept (Qwen3-8B, short sequences, limited environments)
- RL algorithm contains heuristic augmentations (adaptive RED-Weight) lacking theoretical grounding
- TerminalSimulator cross-domain results are ambiguous and require further investigation
- No comparison with baselines (e.g., standard SFT, behavioral cloning from oracle)
- Context mechanism ("hint") is extremely simplified
- Training stability issues in multi-domain setting (Setting B)
- No analysis of scaling behavior with larger models or longer sequences

---

## 18. Core Research Equation

**Problem:** How to train LLMs for long-lifecycle agentic deployment where the agent must accumulate and transfer knowledge across tasks?

**Equation:**
```
CoD meta-capability = 
  (GRPO-style RL with interleaved solve/update episodes)
  + (Environments with information-theoretic gaps)
  + (Fine-grained credit assignment across episodes)
  + (Generalization via diverse training environments)
```

**Evidence:** The gap between position 0 and position 3 success rates growing from (18%→28%) to (45%→76%) during training provides the cleanest signal of learned CoD capability.

---

## 19. Key Takeaways

1. **Novel framework** for training LLMs to connect knowledge across tasks during long-lifecycle deployment
2. **Effective approach** — end-to-end RL with GRPO-style algorithm and fine-grained credit assignment works for eliciting the CoD meta-capability
3. **Generalizable** — the learned meta-capability transfers across domains (FL→Alchemy, FL→TerminalSimulator) and settings (CoD-Deploy→Ralph-loop)
4. **Foundation for future work** — many open questions about scaling, algorithm design, environment design, and integration into LLM post-training pipelines
5. **Practical contribution** — open-source implementations on Trinity-RFT framework
