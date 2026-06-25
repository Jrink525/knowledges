# MemSlides: A Hierarchical Memory Driven Agent Framework for Personalized Slide Generation with Multi-turn Local Revision

**ArXiv:** 2606.17162 | **Authors:** Ye Jin (BUPT), Yangyang Xu (Tsinghua), Jun Zhu (Tsinghua), Yibo Yang (SJTU) | **License:** CC BY 4.0 | **Date:** June 2026

---

## 1. Problem Statement

Automatic presentation generation aims to convert user requests into structured slide decks. While recent agentic systems can produce complete and visually polished decks through multi-modal or tool-based workflows, they **lack persistent personalization** — the ability to remember a user's stylistic, structural, and content preferences across tasks and sessions. In practice, users vary widely in domain, purpose, style, and presentation habits (e.g., academic vs. business decks), yet existing systems require users to repeatedly specify their preferences in every interaction.

This paper targets a specific formulation: **multi-turn personalized slide generation** where the agent must:

- Generate a first draft aligned with a user's **long-term, intent-conditioned** preferences
- Accept **local revision requests** across multiple turns without degrading already-aligned content
- **Carry over preferences** discovered during revision (e.g., "use blue accent colors" or "move methodology to the appendix") to later turns and even future sessions

### 1.1 The Central Gap

The authors identify a core gap: slide generation agents still lack a **user-facing multi-turn dialogue process** that converts revision requests into **reusable preference memory** and preserves local revision constraints across later turns.

The gap has two roots:

1. **Revision granularity problem:** Personalization is often revealed through revision rather than specified upfront. Yet existing systems handle edits by re-contextualizing or re-generating large parts of the deck, making multi-turn modifications fragile.
2. **Memory as an afterthought:** Current systems treat personalization as an implicit byproduct of prompting rather than an explicit service enabled by memory architecture.

---

## 2. Contributions

The paper makes three contributions:

1. **MemSlides framework**: A personalized presentation agent supporting multi-turn localized revision. By maintaining session state and applying targeted slide-level updates instead of repeated full-deck regeneration, it provides the interaction substrate needed for learning user preferences from revision feedback.

2. **Hierarchical memory framework**: Two-level memory architecture — long-term memory (user profile + tool memory) for cross-job persistence, and working memory for session-specific constraints.

3. **Evaluation benchmark**: A multi-persona, multi-intent user profile bank for personalized presentation generation evaluation. Experiments show profile memory improves round-0 persona alignment, tool memory enhances localized modify reliability, and working memory supports session-level preference carryover.

---

## 3. Related Work

### 3.1 Slide Generation

Presentation generation has evolved from document compression and structured summarization to LLM-based systems emphasizing audience adaptation, editability, task-time preference inference, and visual refinement. Key systems:

| System | Contribution | Limitation |
|--------|-------------|------------|
| PPTAgent [58] | Couples generation with presentation-specific evaluation | No explicit user personalization |
| DeepPresenter [59] | Environment-grounded reflection for agentic generation | Does not model user-specific preferences |
| SlideTailor [55] | Conditions on reference slides and task-time templates | Personalization tied to provided examples, not accumulated profiles |

**Key insight:** These systems improve general generation and agentic refinement, but none explicitly models user-specific personalization as persistent memory.

### 3.2 Memory and Tool-Using Agents

Retrieval-augmented and external-memory language models demonstrate that stored context supports generation [16, 7, 14, 3, 10, 43]. Persistent memory work [61, 31, 32, 50, 4, 45, 12, 47, 54] focuses on memory management, reflection, and structured updates. Tool-using agents [53, 39, 38, 33, 36, 18, 13, 46, 42, 24, 28, 1, 44, 52, 8] establish patterns for interleaving reasoning with actions.

**Gap:** No prior work targets personalized presentation authoring where memory must distinguish user preference from execution experience and preserve local edit scope during multi-turn revision.

### 3.3 Personalized Generation and Evaluation

Personalized generation has evolved from explicit persona conditioning to profile- and history-aware generation [17, 48, 37, 27, 11]. Recent surveys characterize personalization as an agentic, retrieval-centric process.

**Gap:** Benchmarking personalization in slide generation lacks multi-persona, multi-intent evaluation frameworks.

---

## 4. MemSlides Architecture

### 4.1 Overview

MemSlides is built on two interacting subsystems:

- **Hierarchical memory system** (Section 4.2): Long-term memory (user profile + tool) and working memory
- **Localized revision executor** (Section 4.3): Plan-Act-Guard loop for scoped slide-local modification

The framework takes a current session state and user feedback, and produces updated state and revised deck. Figure 1 in the paper shows the complete pipeline.

### 4.2 Hierarchical Memory Framework

#### 4.2.1 Memory Decomposition

MemSlides separates memory by **lifetime** and **functional role**:

```
Memory
├── Long-term Memory (persists across jobs)
│   ├── User Profile Memory: Intent-conditioned presentation preferences
│   │   Dimensions: theme, content, visual, layout, template, general
│   └── Tool Memory: Reusable execution experience
│       ├── Round-scope task experience: job-level lessons
│       └── Operation-scope tool chains: reasoning + tool-call + observation fragments
└── Working Memory (active within current job)
    ├── Routed profile items (from user profile memory)
    ├── Temporary feedback preferences (from current session)
    ├── Edit state records (resolved targets, coverage, snapshot hashes)
    ├── Carryover instructions (active for current deck)
    └── Repair focus (pending verification items)
```

#### 4.2.2 User Profile Memory

The profile memory governs personalization through:

$$\mathcal{M}^{\mathrm{pref}}_t = (P_u, A_t)$$

where $P_u$ is user $u$'s long-term profile and $A_t$ is active temporary memory at revision round $t$.

**Profile lifecycle (Figure 3):**
1. **Select**: $\tilde{P}_u = \mathcal{S}(P_u, i_0)$ — retrieve intent-matched profile bucket
2. **Extract**: $C_0 = \mathcal{E}(q_0)$ — extract constraints from request
3. **Reconcile**: $A_0 = \mathcal{R}(\tilde{P}_u, C_0)$ — reconcile profile with request constraints
   - Compatible preferences coexist
   - Explicit conflicts supersede profile items for current deck
4. **Evolve**: $A_t = \mathcal{U}(A_{t-1}, r_t)$ — active memory evolves with revision feedback
5. **Consolidate**: After job end, stable interaction signals are written back to $P_u$

**Key design choice:** Profile memory is NOT injected as a static prompt block. It is selected, reconciled with the current request, used during generation and revision, then updated post-job.

#### 4.2.3 Working Memory

Working memory is the **session-scoped state layer** that makes Plan-Act-Guard multi-turn. Key roles:

- Stores active temporary preferences from earlier feedback turns
- Maintains carryover instructions valid for the current deck
- Tracks edit-state records (resolved targets, coverage status, snapshot rebinding hints)
- Buffers round-level tool-memory signals before consolidation

#### 4.2.4 Tool Memory

Tool memory captures **reusable execution experience** for localized editing:

- **Round-scope task experience**: Buffered through working memory, updated after modify rounds
- **Operation-scope tool chains**: Retrieved before similar operations to guide tool calls

---

### 4.3 Localized Revision: Plan-Act-Guard

Instead of re-reading or re-writing the whole deck for each feedback turn, MemSlides projects the request onto the **smallest affected slide region** and operates on a bounded "repair surface."

#### 4.3.1 Plan Phase

Build an **execution contract**:
1. Infer scope (target slides)
2. Identify active rules (style rules, layout constraints)
3. Generate selector hints (CSS/structural selectors)
4. Determine if coverage verification is required

#### 4.3.2 Act Phase

Edit the bounded surface:
- **Preferred**: Batch CSS, semantic styling, or local patches
- **Reserved for**: Full rewrite for new slides or controlled recovery
- Reading: only a structured snapshot of the local surface (layout structure, selectors, style rules)
- Writing: only patches scoped to explicit selectors or style rules

#### 4.3.3 Guard Phase

Verify before finalize:
- Inspection tools to check edit correctness
- Coverage checks to ensure all required slides modified
- Snapshot hashes to detect unintended changes
- Repair focus: blocks premature finalize until all targets satisfied

This design ensures both reading and writing stay **local by construction**, reducing context pressure and unintended drift.

---

## 5. Implementation

### 5.1 System Architecture

The codebase is organized into pipelined modules:

```
pipelines/     → Generation and revision coordination
memory/        → Profile and tool memory stores
runtime/       → Session state tracking
tools/         → Guarded slide operations (write, inspect, patch, template, etc.)
```

### 5.2 Tool Suite

The tool set implements guarded slide operations:
- **Write**: Apply patches to selected slide regions
- **Inspect**: Read structured snapshots of local surfaces
- **Patch**: Batch CSS/semantic styling updates
- **Template**: Template-aware constrained generation
- **Document**: Access source document context
- **Asset**: Manage slide assets
- **Memory**: Read/write memory states
- **Verifier**: Check coverage and edit correctness

---

## 6. Experimental Setup

### 6.1 Evaluation Framework

The evaluation covers three dimensions:

| Dimension | Metric | Method |
|-----------|--------|--------|
| Round-0 personalization | Persona-alignment judgments | Multi-persona, multi-intent profile bank |
| Deck quality | DeepPresenter-style quality metrics (GPT-5 evaluation) | Three-profile shared suite |
| Localized modify reliability | Diagnostic matched-pair modify behavior | With/without tool-memory injection |

### 6.2 Multi-Persona, Multi-Intent Profile Bank

The authors construct a benchmark profile bank with multiple personas (e.g., product strategy, research seminar, visual teaching) and intents, enabling controlled evaluation of personalization alignment.

### 6.3 Baselines

Comparisons include:
- **SlideTailor**: Previous state-of-the-art in personalized slide generation with reference-slide conditioning
- Variants without profile memory
- Variants without tool-memory injection

---

## 7. Experimental Results

### 7.1 Profile Memory Effectiveness (Persona Alignment)

**All-column wins over both baseline systems on GLM-5 and Gemini 3.1 Pro evaluations.**

| Dimension | Avg. Gain over SlideTailor | Notes |
|-----------|---------------------------|-------|
| Content | +2.73 | Strongest improvement |
| Structure | +2.95 | Narrative/organization alignment |
| Visual | +2.79 | Layout, style, design consistency |
| Specificity | +3.08 | Detail-level personalization |

**Interpretation**: User profile memory significantly improves first-pass personalization across all measured dimensions, with specificity showing the largest gain.

### 7.2 Deck Quality

**GPT-5 evaluation: Avg. 4.17 for MemSlides** — best among compared systems in the shared three-profile suite.

This confirms that personalization does NOT come at the cost of absolute quality; MemSlides remains competitive with state-of-the-art non-personalized systems.

### 7.3 Tool Memory for Localized Edit Reliability

**Diagnostic modify pairs — matched-pair closed-loop edit task:**

| Metric | Without Tool Memory | With Tool Memory |
|--------|-------------------|-----------------|
| Closed-loop completion | Lower | **0.963** |
| Strict verify rate | Lower | **0.534** |
| Time to first correct edit (overall) | 609.5s | **242.5s** |
| Time to first correct edit (non-error) | — | ~92s |

**Interpretation**: Tool memory more than **halves the time** to first correct edit (242.5s vs 609.5s). The 0.963 closed-loop completion rate demonstrates highly reliable automated editing, while the 0.534 strict verify rate suggests room for improvement in edge-case handling.

### 7.4 Qualitative Analysis

#### 7.4.1 Memory Behavior Cases

**Profile lifecycle demonstration**: Intent-conditioned profile memory is selected, reconciled with request, used as active memory, and consolidated post-job. Examples show:
- Consistent theme application across jobs per user intent
- Preference adjustment when request explicitly contradicts profile items

**Cross-job consolidation**: Repeated local feedback cues (e.g., "make methodology tables always a single-column layout") become reusable patterns for later sessions.

#### 7.4.2 Localized Revision Behavior

**Localized modification**: Targeted patches preserve already-aligned content while satisfying requested changes. Example: updating only the color scheme of section headers without touching content, layout, or other design elements.

**Template-aware generation**: Task-time templates act as deck-local design constraints rather than generic profile preferences, showing separation of job-specific and persistent memory.

---

## 8. Analysis & Discussion

### 8.1 Why Hierarchical Memory Works

The separation of memory by lifetime (long-term vs. working) and function (profile vs. tool vs. edit-state) is well-motivated:

1. **Profile vs. tool separation**: User preferences (what to generate) and execution experience (how to edit) have fundamentally different update frequencies and retrieval triggers. Mixing them would cause profile items to be diluted by operational noise.

2. **Long-term vs. working separation**: Personalization signals decay at different rates. Persistent user preferences should survive across jobs; temporary feedback from the current revision session should not pollute the permanent profile unless explicitly consolidated.

3. **Reconciliation mechanism**: The $\mathcal{R}$ function handles the critical conflict case where a user's explicit request contradicts a stored preference. This prevents the profile from being treated as immutable dogma.

### 8.2 Why Localized Revision Matters

The Plan-Act-Guard loop addresses a practical failure mode in multi-turn editing: **scope creep**. Without explicit scoping:
- Small changes compete with deck state and feedback history for limited context
- Intended edits accumulate drift in already-aligned content
- The system may prematurely declare completion

By constraining both read and write operations to the smallest affected region, MemSlides makes multi-turn revision **compositional** — each turn's edit is independent of and non-destructive to prior turns' work.

### 8.3 Comparison with Decomposed Memory in Other Domains

The hierarchical memory design draws on broader agent-memory literature [61, 31, 47] but adapts it to the specific needs of presentation authoring:
- Unlike general-purpose memory (e.g., MemGPT), MemSlides' working memory is **task-structured** (edit-state, carryover, repair focus) rather than free-form
- Unlike chatbot personalization, tool memory captures **execution-level** patterns (tool-call chains, error recovery) rather than conversational style

---

## 9. Limitations

1. **Profile cold start**: The system assumes pre-existing profile memory. Cold-start personalization (learning user preferences from zero prior knowledge) is not evaluated.

2. **Conflict resolution granularity**: The reconcile function $\mathcal{R}$ handles explicit conflicts, but implicit conflicts (where user actions subtly contradict profile items) are not addressed.

3. **Strict verification ceiling**: The 0.534 strict verify rate with tool memory indicates that while edits complete reliably, perfect verification remains challenging — automated checks may miss nuanced correctness criteria.

4. **Scalability of profile bank**: The multi-persona evaluation covers limited personas. Scaling to hundreds or thousands of diverse user profiles may introduce new challenges in profile management and retrieval.

5. **Multi-modal inputs**: The current pipeline processes text and structural slide content but does not handle rich multi-modal inputs (charts, diagrams, embedded media).

---

## 10. Conclusion

MemSlides addresses a fundamental gap in personalized presentation generation: current systems lack persistent, structured memory for user preferences and execution experience across multi-turn revision sessions.

**The central thesis** is that effective personalization in presentation authoring depends on **separating persistent user profiles, session-level working memory, and reusable execution experience** across generation and localized revision.

Key results:
- Profile memory: +2.73 to +3.08 gains in persona alignment over SlideTailor
- Quality: GPT-5 Avg. 4.17, best among compared systems
- Tool memory: Halves edit time (242.5s vs 609.5s) with 0.963 closed-loop completion

The paper demonstrates that **memory architecture matters for personalization** — not as a monolithic retrieval buffer, but as a structured hierarchy with differentiated lifetimes and functional roles.

---

## 11. Future Directions (Implicit)

Based on the analysis, promising research directions include:

1. **Cold-start personalization**: Learning user profiles from few interactions or zero prior data
2. **Implicit conflict detection**: Recognizing subtle mismatches between user behavior and stored profiles
3. **Verified localized editing**: Improving strict verification rate beyond 0.534
4. **Scalable profile management**: Efficient retrieval and maintenance for large user bases
5. **Multi-modal slide memory**: Extending memory to cover charts, images, and dynamic embedded content
6. **Cross-platform transfer**: Applying learned preferences across different presentation tools (PowerPoint, LaTeX/Beamer, web slides)
7. **Collaborative memory**: Sharing profile patterns (with privacy) across similar user cohorts

---

## 12. Core Claims Index

| Claim ID | Claim | Evidence Source | Verdict |
|----------|-------|----------------|---------|
| C1 | Multi-turn localized revision preserves already-aligned content | Qualitative case studies, Plan-Act-Guard design | Supported |
| C2 | Profile memory improves round-0 persona alignment | +2.73 Content, +2.95 Structure, +2.79 Visual, +3.08 Specificity | Strongly supported |
| C3 | MemSlides maintains competitive deck quality | GPT-5 Avg. 4.17, best among compared systems | Supported |
| C4 | Tool memory improves localized edit reliability | 0.963 closed-loop completion (vs lower without) | Supported |
| C5 | Tool memory reduces time to correct edit | 242.5s vs 609.5s (2.5× faster) | Supported |
| C6 | Working memory carries session-level preferences across turns | Qualitative cases | Preliminary |
| C7 | Separating profile from tool memory is beneficial | Diagnostic matched-pair comparisons, ablation via comparison | Indirect support |

---

## 13. Appendices Summary

The paper's appendix is not accessible in the truncated HTML version, but based on the main text structure, it likely contains:
- Detailed prompt templates used for memory routing, reconciliation, and consolidation
- Additional qualitative examples and failure case analysis
- Full GPT-5 evaluation rubric and scoring methodology
- Extended related work discussion
- Implementation details for the tool suite

---

## References

Key references cited in the paper (from the truncated reference list):
- [61] Wang et al. — MemoryBank (persistent memory for LLMs)
- [31] Park et al. — Generative Agents (long-term memory for agents)
- [47] Wang et al. — MemGPT (OS-level memory management for LLMs)
- [55] SlideTailor (previous SOTA in personalized slide generation)
- [58] PPTAgent (evaluation-coupled presentation generation)
- [59] DeepPresenter (reflection-grounded presentation generation)
- [13, 46, 42, 24, 28, 1, 44, 52, 8] — Various tool-using agent papers
- [16, 7, 14, 3, 10, 43] — RAG and external-memory papers
- [17, 48, 37, 27, 11] — Personalized generation papers
