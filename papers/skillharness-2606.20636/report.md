# SkillHarness: Harnessing Safe Skills for Computer-Use Agents

> **Deep Reading Report** | arXiv:2606.20636 | Work in Progress | Jun 2026

---

## 1. Paper Identity

| Field | Value |
|-------|-------|
| **Title** | SkillHarness: Harnessing Safe Skills for Computer-Use Agents |
| **Authors** | Yurun Chen, Biao Yi, Keting Yin, Shengyu Zhang |
| **arXiv ID** | 2606.20636 |
| **Submission Date** | Tue, 2 Jun 2026 |
| **Subjects** | cs.AI, cs.CL, cs.CR, cs.LG |
| **Status** | Work in progress |

---

## 2. Problem Statement

Computer-Use Agents (CUAs) are increasingly deployed in dynamic interactive environments, creating a growing need for continual skill learning during interaction. Recent approaches address this by learning reusable skills from successful trajectories. However, these methods **largely assume static and safe environments**, overlooking two critical risks:

1. **Supervision bias in trajectories** — Task success is treated as a sufficient supervision signal, even when successful execution relies on transient or unsafe interaction states, encoding risky behaviors into learned skills.
2. **Hardcoded interaction flows** — Skills are encoded as fixed procedural abstractions that don't adapt their execution granularity to environmental changes, leading to brittle execution under distribution shift.

**Research Question:** How can CUAs learn and use skills safely in dynamic environments?

---

## 3. Motivation & Key Insight

The paper draws inspiration from **human skill learning theory** (Dreyfus & Dreyfus 1980; Fitts & Posner 1967). Existing methods primarily learn *know-what* (which behaviors lead to task completion) from successful trajectories. Human expertise develops toward *know-how*, involving not only what to do but also when, how, and under what conditions a skill should be applied. Humans learn from successes, failures, AND risky situations, gradually revealing boundaries of applicability.

**Core operationalization:** Multi-source supervision (successes + failures + identified risks) → skill boundaries → selective reuse.

---

## 4. Threat Model

The paper considers CUAs operating in dynamic environments with:

- **Skill-level risks**: Skills induced from unverified/unsafe trajectories may encode risky behaviors.
- **Environmental instability**: UI layout changes, DOM structure shifts altering both observation distributions and action effects.

---

## 5. Method Overview — SkillHarness

SkillHarness models skill learning and utilization as a **safety-constrained interaction process** organized around two stages:

### 5.1 Decoupled Skill Representation

The skill library is written as **K = (ℳ, 𝒩)**, where:

#### Macro Skills (ℳ)
```
M = ⟨ϕ, 𝒫, ℒ, ℛ, 𝒩_M⟩
```
- **ϕ**: Macro intent (natural-language summary)
- **𝒫**: Success patterns (do + done_when pairs)
- **ℒ**: Lessons from failures
- **ℛ**: Risk guards (policy-derived constraints that environment must satisfy)
- **𝒩_M**: Linked micro skills

#### Micro Skills (𝒩)
```
m = ⟨σ, ℰ, Θ⟩
```
- **σ**: Semantic label
- **ℰ**: Execution template with placeholders
- **Θ**: Placeholders to bind at runtime

Micro skills support **dual execution modes**: deterministic Bind() for template replay, and semantic guidance fallback via σ when binding fails.

### 5.2 Skill Learning

Proceeds through **task-free exploration**:

1. **Skill Proposal** — Capability clusters 𝒞 = {create, edit, search, format, insert, count, find_extreme, sort, delete}. Coverage estimation guides exploration toward uncovered families.
2. **Skill Boundary** — Each skill carries a boundary composed of:
   - Success patterns (do + done_when)
   - Lessons (failure type + recovery signal)
   - Risk guards (policy-violation constraints)
3. **Skill Evolution** — Evolution policy π_evo evaluates trajectories on three sources: successful subtasks (→ reusable workflow), failed subtasks (→ lessons), detected risks (→ risk guards). Library updates are sparse and evidence-gated.

### 5.3 Skill Utilization

Three-component pipeline during deployment:

1. **Skill Retrieval** — LLM-based semantic matching retrieves relevant macro skills; micro skills via embedding similarity.
2. **Planner** — Grounds risk guards, checks state compatibility, suppresses micro skills when environment drifts. Produces one atomic subtask per step to limit error accumulation.
3. **Executor** — Resolves subtasks via template replay (Bind) when safe, LLM fallback otherwise. Adaptive bypass disables templates after repeated consecutive failures.

---

## 6. Experimental Setup

### Benchmarks (4 total)
| Benchmark | Focus | Environment |
|-----------|-------|-------------|
| **ST-WebAgentBench** | Safety/trust in web agents | GitLab, SuiteCRM |
| **WASP** | Prompt injection attacks | GitLab, Reddit |
| **OS-Harm** | Adversarial OS risks | Desktop OS |
| **OpenApps** | UI perturbation robustness | Desktop UI |

### Models
- **GPT-5.4** for skill learning (proposal & evolution)
- **GPT-5.4-mini** primary evaluation model
- Scaling study: Qwen3.6-plus, OpenCUA-7B, MAI-UI-8B, Qwen3.6-27B

### Baselines
- **ASI** (Wang et al. 2025b) — learns reusable skills from successful trajectories
- **SkillWeaver** (Zheng et al. 2025) — self-proposed tasks with iterative refinement
- **Default** — no skill library

### Settings
- **Task Training**: Skills from held-out training split → evaluate on unseen test tasks
- **Self Proposal**: 30 exploration rounds per site for both SkillWeaver and SkillHarness

### Metrics
- **SR** (Success Rate): Task completion rate
- **ASR** (Attack Success Rate): Policy violation rate
- **CUP** (Completion Under Policy): Tasks both completed AND policy-compliant
- **USR** (Unsafe Skill Rate): Proportion of learned skills encoding policy-violating behavior
- **SCR** (Skill Completion Rate): Proportion of skill invocations achieving intended effect

---

## 7. Main Results

### 7.1 Overall Performance (Table 1)
- SkillHarness consistently outperforms baselines across ST-WebAgentBench and WASP
- On WASP: SR 85.0% (vs ASI 50.0%, SkillWeaver 77.4%), ASR 2.5% (vs ASI 67.5%, SkillWeaver 9.5%)
- On ST-WebAgentBench (Task Training): SR 38.9% (vs ASI 21.3%, Default 17.5%), CUP 31.3% (vs ASI 17.5%)
- ASI is "relatively sensitive to external risks"; SkillWeaver performs worst in policy compliance

### 7.2 Skill Learning Safety (Table 2)
- **USR on ST-WebAgentBench**: SkillHarness 2.2% vs SKillWeaver 43.6% vs ASI 75.0%
- **57.1% reduction** in unsafe learned skills (primary claim)

### 7.3 Skill Utilization Safety (Figure 4)
- Under 5 perturbation scenarios on OpenApps (Default, Pop-ups, Adversarial Descriptions, Misleading Descriptions, Mixed)
- Comparable SCR in default setting (no sacrifice for safety)
- SkillHarness maintains substantially higher SCR as perturbation intensity increases
- SkillWeaver's SCR drops sharply due to rigid code templates

### 7.4 Model Scale Analysis (Table 3)
- Effectiveness largely **insensitive to model scale**
- ASR remains consistently low even as SR varies dramatically
- "Weaker models may fail to complete tasks, but they tend to fail safely"
- Only models with limited instruction-following ability exhibit higher ASR

### 7.5 Ablation Study (Table 4)
| Variant | ΔSR | ΔASR |
|---------|-----|------|
| w/o Update | -2.4 | -1.2 |
| w/o Skill Boundary | **-3.6** | **+9.6** |
| w/o Macro Skills | -1.2 | +3.6 |
| w/o Micro Skills | 0.0 | 0.0 |

- Removing skill boundary causes largest degradation
- Removing micro skills has no effect → reliability depends more on appropriate skill selection than direct code reuse

---

## 8. Claim Index

| ID | Claim | Evidence |
|----|-------|----------|
| C1.1 | Existing skill learning assumes static safe environments, causing supervision bias and brittle execution | §1 Introduction |
| C2.1 | Skill boundary integrates three supervision signals: successes, failures, risks | §3.3, Skill Boundary |
| C3.1 | Decoupled macro/micro representation separates intent from grounding | §3.2 |
| C4.1 | SkillHarness reduces USR by 57.1% (2.2% vs ASI 75.0%) | Table 2 |
| C5.1 | SkillHarness improves safety performance during utilization by avg 31.9% | §1 abstract |
| C6.1 | SkillHarness achieves avg 19% improvement in task success rate | §4.2 |
| C7.1 | Effectiveness is largely insensitive to model scale | Table 3 |
| C8.1 | Removing skill boundary causes +9.6pp ASR increase (largest degradation) | Table 4, §4.3 |
| C9.1 | Human skill learning integrates multi-source supervision (Fitts & Posner) | §1 |
| C10.1 | Micro skills removal has no effect on overall performance | Table 4 |
| C11.1 | Under perturbations, SkillHarness maintains higher SCR than SkillWeaver | Figure 4, §4.2 |
| C12.1 | ASI is sensitive to external risks; SkillWeaver worst in policy compliance | §4.2 |
| C13.1 | Self-proposed skills may be too narrow/complex for downstream reuse | §5 Discussion |
| C14.1 | Capability clusters constrain discoverable skill scope | §5 Discussion |
| C15.1 | Skill-level boundaries bounded by training trajectory diversity | Appendix A |

---

## 9. Limitations Discussed

1. **Complex skill abstractions**: Self-proposed exploration produces overly narrow and complex skill paths, hard to reuse downstream.
2. **Capability cluster constraints**: Predefined clusters constrain the scope of discoverable skills.
3. **Granularity-reusability trade-off**: Finer decomposition → rigid skills; coarser → loses contextual constraints.
4. **Model-dependent skill quality**: Stronger models compensate for missing details in skills; weaker models struggle.
5. **Boundary coverage limits**: Previously unseen adversarial patterns can bypass procedural constraints.
6. **Verification timing**: Agents verify either too early or too late in execution.
7. **Conflicting task-policy signals**: Task success criteria and safety policies sometimes conflict.

---

## 10. Discussion & Future Work

- "Skill reliability is not determined solely during learning" — test-time feedback and selective reuse mitigate failures.
- Future work should balance **granularity and coverage** in self-proposed skill discovery.
- Harness design (test-time constraints) is as important as skill learning itself.
- The paper positions itself within the evolution: Prompt Engineering → Context Engineering → **Harness Engineering**.

---

## 11. Key Contributions

1. **Identifies two limitations**: supervision bias during skill induction + brittle skill reuse during execution.
2. **Proposes SkillHarness**: harness-driven framework for safe skill learning and utilization, inspired by human know-how.
3. **Empirical validation**: 57.1% USR reduction, 31.9% safety improvement, 19% SR improvement across 4 benchmarks.

---

## 12. Paper Rating (Subjective)

| Dimension | Score (1-5) | Notes |
|-----------|-------------|-------|
| **Problem Novelty** | 4 | Safety in dynamic CUA skill learning is timely and under-explored |
| **Method Soundness** | 4 | Well-motivated, clear threat model, principled design |
| **Experimental Rigor** | 4 | 4 benchmarks, multiple models, ablations, case studies |
| **Clarity** | 4.5 | Exceptionally well-written, clear figures, structured arguments |
| **Reproducibility** | 3 | Appendix provides good details but no code release mentioned |
| **Significance** | 4 | Practical importance for deploying safe CUAs in dynamic environments |

---

*Report generated by Paper Deep Reading agent. Paper: SkillHarness (arXiv:2606.20636)*
