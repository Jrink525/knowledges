# Critique of Agent Model — Deep Reading Report

**Paper:** Critique of Agent Model  
**arXiv:** [2606.23991](https://arxiv.org/abs/2606.23991)  
**Authors:** Eric Xing, Mingkai Deng, Jinyu Hou (MBZUAI Institute of Foundation Models & CMU)  
**Date:** June 15, 2026 (submitted Jun 22, 2026)  
**Category:** cs.AI, cs.LG, cs.MA, cs.RO

---

## 1. Problem Statement

What is an agent? What constitutes genuine agency? The paper argues that the field has conflated *automation* with *agency*. With the explosion of systems marketed as "coding agents", "AI co-scientists", and "agentic" tools — alongside existential fears about AI escaping human control — the authors assert that a clear, principled boundary must be drawn between mere task-automation and true autonomous agency.

**Core tension:** Current AI systems achieve impressive results through carefully engineered external scaffolding (tools, workflows, prompts, control loops), but their competence resides in the *engineering around* the model, not in the model itself. The field lacks a formal understanding of what structural properties a system must internalize to warrant the designation "agent."

---

## 2. Key Contributions

1. **Agentic vs. Agentive distinction** — A principled taxonomy: *agentic* systems execute tasks through externally orchestrated workflows; *agentive* systems derive capabilities endogenously from internalized structures.

2. **Five-dimensional framework for agency** — Goals, Identity, Decision-Making, Self-Regulation, and Learning — each analyzed along a spectrum from externally prescribed to internally maintained.

3. **Formal Agent Model (AM) definition** — $p_\pi(a \mid s, g, i)$: a reasoning model generating actions conditioned on goals and identity.

4. **GIC (Goal-Identity-Configurator) Architecture** — A complete architectural proposal combining hierarchical goal decomposition, identity evolution, simulative reasoning (separate world model), learned self-regulation, and self-directed learning.

5. **Two formal theorems** — Theorem 1 (fast-slow identity learning dominates slow-only) and Theorem 2 (world-model-based planning improves any policy).

6. **Safety analysis** — Argues that GIC's modular architecture provides *layered transparency* and auditability, reducing safety concerns to component-level debugging.

---

## 3. Formal Framework

### Agent-Environment Model

The paper begins with a minimal formalization:

**Environment** $\mu$: stochastic dynamical system with transition $p_\mu(s_{t+1} \mid s_t, a_t)$
**Agent policy** $\pi$: action distribution $p_\pi(a_t \mid s_t)$
**Trajectory:** $p^\pi_\mu(a_t, s_{t+1}, \dots, s_T \mid s_t) = \prod_{k=t}^{T-1} \underbrace{p_\pi(a_k \mid s_k)}_{\text{agent}} \cdot \underbrace{p_\mu(s_{k+1} \mid s_k, a_k)}_{\text{universe}}$

**Key principle:** The agent factor and universe factor must remain functionally distinct — the agent model decides *what to do*, the world model predicts *what will happen*. Collapsing them (as recent proposals do) conflates reward-driven action selection with fidelity-driven next-state prediction.

### Agent Model Definition

An agent model (AM) is defined as: $p_\pi(a \mid s, g, i)$ where $g$ is the goal and $i$ is the identity. This formalization enables the agent to inspect, decompose, and revise its objectives and self-model rather than leaving them implicitly distributed across weights.

---

## 4. The Five Dimensions of Agency

### 4.1 Goals

| Spectrum | Agentic End | Agentive End |
|-----------|-------------|--------------|
| **Source** | Externally supplied step-by-step | Internally persistent, decomposable |
| **Persistence** | Vanishes after interaction | Continues over long horizons |
| **Decomposition** | Human specifies every subgoal | Learned module $\delta$ breaks down $g$ into $(g_1, g_2, \dots)$ |

**Formalization:** $g_t \sim p_\delta(\cdot \mid s_t, g)$ with value function $V^{g_t}_{\pi,\mu}(s_t) = \mathbb{E}_{\pi,\mu}[\sum_{k=t}^\infty \gamma_k r(s_k, g_t) \mid s_t]$.

### 4.2 Identity

| Spectrum | Agentic End | Agentive End |
|-----------|-------------|--------------|
| **Nature** | Static, externally defined | Evolving with experience |
| **Update** | Manual re-engineering | Fast-slow: $i_t \sim p_\iota(\cdot \mid s_t, i_{t-1})$ |
| **Examples** | System prompts, config files | Self-model updated from performance feedback |

**Theorem 1 (Fast-slow learning):** An agent maintaining both slow (parameter) updates and fast (identity) updates accumulates strictly less regret than a slow-only agent: $\text{Regret}^{\text{fast-slow}}_K \leq \text{Regret}^{\text{std}}_K - \Omega(\sum_{k=1}^K N_k)$.

### 4.3 Decision-Making

| Spectrum | Agentic End | Agentive End |
|-----------|-------------|--------------|
| **Mode** | Black-box end-to-end policy | Simulative planning + reactive execution |
| **Grounding** | Narrative plausibility (token prob.) | Predicted state transitions via world model |
| **System** | Single unregulated chain-of-thought | System I (actor), System II (planner), System III (configurator) |

**Theorem 2 (World-model-based planning):** Given a world model $f$ with bounded TV error $\epsilon$, any policy $\pi$ can be augmented into $\pi_{\text{mix}}$ such that $V^{g}_{\pi_{\text{mix}}} \geq V^{g}_\pi$.

### 4.4 Self-Regulation

| Spectrum | Agentic End | Agentive End |
|-----------|-------------|--------------|
| **Control** | Fixed human-designed workflow | Learned configurator $\kappa$ |
| **Mode selection** | None (always same process) | Adaptive: $u_t \sim p_\kappa(\cdot \mid s_t, g_t, i_t, c_{t-1})$ |
| **Scope** | Inference only | Inference + learning scheduling |

The configurator outputs a regulation variable $u_t$ governing whether to act directly, continue an existing plan, invoke planning, or revise goals.

### 4.5 Learning

| Spectrum | Agentic End | Agentive End |
|-----------|-------------|--------------|
| **Schedule** | Externally scheduled | Configurator-governed |
| **Scope** | Pre-deployment only | Continuous and endogenous |
| **Sources** | Human-curated data | Real interaction + simulated experience |

**Key distinction:** Self-directed learning governed by the configurator $\kappa$ vs. "AI trains AI" systems where training decisions remain human-made.

---

## 5. Critique of Current Practice (§4)

The paper systematically critiques five common design choices:

### 5.1 Goal Problem: Step-by-Step Instruction

**Observation:** Current systems require human-supplied goals at every step.
**Critique:** Cannot scale to long-horizon tasks (e.g., "make wine over a year").
**Alternative:** Hierarchical decomposition module $\delta$ with world-model-based evaluation of subgoal consequences.

### 5.2 Identity Problem: Harness Engineering

**Observation:** Identity is hand-written system prompts + MCP/Agent Skills infrastructure.
**Critique:** Exogenous identity cannot adapt to new environments; locks out genuine autonomy.
**Alternative:** Fast-slow update principle — slow parameter updates + fast identity revisions.

### 5.3 Decision-Making Problem: Black-Box Policies

**Observation:** Scaling end-to-end policies with chain-of-thought; belief that planning will emerge.
**Critique:** Conflates *internal compute* with *planning*. Chain-of-thought describes futures but is not grounded in state-transition prediction. No counterfactual engine.
**Alternative:** Explicit world model $f$ for simulative reasoning.

### 5.4 Self-Regulation Problem: Unconstrained RL or Fixed Workflows

**Observation:** Either hope deliberation emerges from RL, or build fixed plan-then-act pipelines.
**Critique:** First approach leads to overthinking/underthinking; second is rigid and brittle.
**Alternative:** Learned configurator $\kappa$ as meta-controller.

### 5.5 Learning Problem: Human-Scheduled Pipelines

**Observation:** Training terminates before deployment; behavior change requires external intervention.
**Critique:** Even "AI trains AI" systems keep the training loop external.
**Alternative:** Self-directed learning where configurator governs when/how to learn.

### 5.6 Common Root Cause

Underlying all limitations: the structural absence of an explicit *world model* — a model of reality capable of predicting action consequences across mental, physical, social, and natural layers.

---

## 6. Landscape of Current Agent Systems (§3)

The paper classifies existing systems along a continuum:

| Category | Examples | Agency Level |
|----------|----------|-------------|
| **Program-Based** | Thermostat, ELIZA, Selenium | Fully prescribed |
| **LLM Wrapper** | DeerFlow, AutoGen, Cursor, OpenClaw | Externally orchestrated |
| **LLM-Centered** | Claude Code, DeepSeek-V4, SIMA-2 | More internalized but goals/identity external |
| **Model-less Physical** | Boston Dynamics Spot, ABB robots | High physical competence, no internal agency |
| **Embodied-Model** | Figure Helix, $\pi_{0.6}$, DreamZero | Closest to internal organization, still limited |

**Relation to existing surveys:** The paper cites surveys by Wang et al. (2024), Wei et al. (2026), Jiang et al. (2025), Gao et al. (2025), Fang et al. (2025), and Chu et al. (2026), noting they tend to take "agency" for granted.

---

## 7. The GIC Architecture (§5)

### 7.1 Core Components

| Component | Symbol | Function | Analogy |
|-----------|--------|----------|---------|
| Belief Encoder | $h$ | $s_t \sim p_h(\cdot \mid o_t)$ | Perceptual system |
| Goal Decomposer | $\delta$ | $g_t \sim p_\delta(\cdot \mid s_t, g)$ | Strategic planning |
| Identity Evolver | $\iota$ | $i_t \sim p_\iota(\cdot \mid s_t, i_{t-1})$ | Self-model update |
| Configurator | $\kappa$ | $u_t \sim p_\kappa(\cdot \mid s_t, g_t, i_t, c_{t-1})$ | Metacognition (System III) |
| Simulative Planner | $\pi_f$ | $c_t \sim p_{\pi_f}(\cdot \mid s_t, g_t, i_t, u_t)$ | Deliberative reasoning (System II) |
| Actor | $\alpha$ | $a_t \sim p_\alpha(\cdot \mid s_t, c_t)$ | Reactive execution (System I) |
| World Model | $f$ | $p_f(s_{t+1} \mid s_t, a)$ | Reality simulator (separately trained) |

### 7.2 The Three-System Cognitive Architecture

- **System I (Actor $\alpha$):** Reactive, fast execution for routine/high-urgency decisions.
- **System II (Planner $\pi_f$):** Simulative reasoning via world model for novel/high-stakes situations.
- **System III (Configurator $\kappa$):** Metacognitive control governing mode selection, deliberation depth, and learning scheduling.

**Joint action distribution:**
$p_{\text{GIC}}(a_t \mid o_t, g, i_{t-1}) = \sum_{g_t,i_t,u_t,c_t} p_\alpha(a_t \mid s_t, c_t) \cdot p_{\pi_f}(c_t \mid s_t, g_t, i_t, u_t) \cdot p_\kappa(u_t \mid s_t, g_t, i_t) \cdot p_\iota(i_t \mid s_t, i_{t-1}) \cdot p_\delta(g_t \mid s_t, g) \cdot p_h(s_t \mid o_t)$

### 7.3 Training Phases

**Phase 1: Component Pretraining (Ground School)**
- Agent model initialized from pretrained LLM ("book knowledge")
- World model trained via GLP architecture on multimodal next-state prediction
- Critic pretrained on reward-labeled data
- Policy seeded from demonstration data

**Phase 2: Simulative RL (Simulator Hours)**
- Agent trains on hypothetical trajectories within world model
- Builds System I, II, and III competence
- Safe sandbox for dangerous scenarios

**Phase 3: Real-World Deployment (First Flights)**
- Refines world model (sim-to-real gap)
- Sharpens configurator decisions
- Evolves identity via performance feedback

### 7.4 Evaluation Framework: PEG

| Dimension | What It Measures | Key Metrics |
|-----------|-----------------|-------------|
| **P**erformance | Task success + generalizable reasoning | Goal decomposition, identity adaptation, simulative reasoning, reactive execution |
| **E**fficiency | Compute allocation quality | Decision latency, thinking tokens vs. accuracy, planning frequency |
| **G**rowth | Learning over time | Learning efficiency, self-directed exploration, learning transfer |

---

## 8. Safety and Auditability (§5.7)

**Key argument:** GIC's modularity turns safety from an opaque emergent-property problem into a component-debugging problem.

**Harmful behavior decomposes into:**
1. **Goal misspecification** — wrong human-supplied $g$
2. **Component imperfection** — a module made a mistake

**Layered transparency:**
- $\delta$ (goal decomposition): Audit for undesirable subgoals before execution
- $\iota$ (identity evolution): Monitor for appropriate self-model development
- $f$ (world model): Inspect predictions for consistency with reality
- $\kappa$ (configurator): Verify deliberation is proportional to task complexity
- Learning decisions: Review and steer competence gaps

**Addresses specific concerns:**
- *Instrumental subgoals*: If self-preservation isn't useful for $g$, well-trained $\delta$ shouldn't pursue it
- *Reward hacking*: Traces to misspecified reward — identifiable and correctable
- *Shutdown problem*: No intrinsic reason to resist correction when only terminal goal is human-supplied

**Philosophical stance:** The relevant question is not whether risk exists, but whether the architecture makes risk manageable and decreasing. Building transparent agents is itself a safety intervention.

---

## 9. Related Work

The paper connects to:
- **Philosophy of agency:** Aristotle (purposeful action), Descartes (Cogito, ergo sum), Kant (outer/inner sense)
- **SF portrayals:** Blade Runner replicants as examples of agentive (imperfect but autonomous) beings
- **Safety literature:** Bostrom (superintelligence), Amodei et al. (concrete AI safety problems), Russell (shutdown problem)
- **RL theory:** Sutton & Barto, Simulation Lemma (Kearns & Singh), Performance Difference Lemma (Kakade & Langford)
- **Cognitive science:** Kahneman's System I/II thinking
- **World models:** GLP (Xing et al.), JEPA (LeCun / Assran et al.), DreamZero, Cosmos
- **Agent surveys:** Wang et al. 2024, Wei et al. 2026, Jiang et al. 2025

---

## 10. Data Considerations (§5.6)

| Data Type | Purpose | Used For |
|-----------|---------|----------|
| Observation-only | Full sensory experience | World model training |
| Reward-labeled | Outcome-annotated trajectories | Critic/evaluator training |
| Action-labeled demonstrations | Expert trajectories | Policy seeding |
| **Goal-oriented data** (new) | Extended purposeful activity with goal annotations | Multi-scale planning training |

**Key insight:** Different sources train different levels without needing monolithic coverage. Goal-oriented data (e.g., "fly to Paris" video) is identified as the highest-leverage investment for training general-purpose agent models.

---

## 11. Limitations and Open Questions

1. **Computational feasibility:** GIC requires multiple interacting components (separate world model, planner, configurator, identity evolver). Training and inference efficiency at scale is unproven.

2. **World model accuracy:** Theorem 2's guarantee depends on bounded TV error $\epsilon$. Building accurate world models for open-ended environments remains a grand challenge.

3. **Identity evolution quality:** Theorem 1 assumes identity revisions are "better than random" — the evolver $\iota$ must be well-trained, which itself is a non-trivial learning problem.

4. **Growth evaluation:** The authors note Growth evaluation "remains an important direction for future work" — no experimental results are provided.

5. **Goal-oriented data scarcity:** Curating and scaling goal-annotated trajectories at the necessary variety and volume is a significant data engineering challenge.

6. **Multi-agent scaling:** Scaling GIC to multi-agent settings requires nested world models (simplified models of other agents with their own goals/identities), potentially compounding complexity.

7. **Safety in practice:** While the architectural argument for safety is principled, no deployed system validates the claims.

---

## 12. Companion Work

The paper references companion works for preliminary experimental validation:
- **Deng et al. (2026a):** "General Agentic Planning through Simulative Reasoning with World Models" (arXiv:2507.23773)
- **Deng et al. (2026b):** "Efficient Agentic Reasoning through Self-Regulated Simulative Planning" (arXiv:2605.22138)

These provide "initial evidence along the Performance and Efficiency dimensions."

---

## 13. Conclusions

The paper's central thesis: agency requires internalization of goal management, identity, planning grounded in world models, self-regulated computation, and self-directed learning. The GIC architecture offers a principled path toward this vision. The key message is not technical novelty in each component, but the *systematic integration* of all five dimensions, paired with the fundamental principle of keeping the agent model functionally distinct from the world model.

The paper is unusual in its scope — part philosophical treatise, part formal framework, part architectural blueprint, part safety manifesto. It explicitly positions itself as a provocation: "Our intent is not to offer definitive answers, but to inspire deeper reflection on questions the field may have too often taken for granted."
