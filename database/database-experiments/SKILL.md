---
name: paper-deep-reading
description: "Deep-read research papers — three modes: (1) source-aware + traceable + research-direction mining for CS papers, (2) story-mode for non-academic storytelling (7-beat spine), (3) river-mode for paper lineage tracing (倒读法). Use for arxiv links, PDFs, LaTeX, paper names, paper reviews, literature surveys, or '讲论文' / '倒读' / 'paper river' requests."
license: MIT-0
metadata:
  version: 2.0.0
  openclaw:
    emoji: "📚"
    requires:
      bins:
        - python3
    tags:
      - research
      - papers
      - deep-reading
      - ideation
      - literature-review
      - paper-story
      - paper-trace
      - storytelling
---

# Paper Deep Reading: Three Modes

读一篇论文，可以在三个深度上。选择哪个模式由**读者的目标**决定。

---

## Mode 0: 选模式

用户分享论文后，先判断模式：

| 触发信号 | 模式 | 产出 |
|---------|------|------|
| 学术审稿、复现评估、找研究突破口 | **Deep-read** (默认) | `report.md` + JSON 工件 |
| "讲论文" "读论文" "把这篇讲给我听" — 给外行讲故事 | **Story mode** | 中文故事文（markdown，推荐 `knowledges/papers/`） |
| "倒读" "论文溯源" "paper river" "这篇的来龙去脉" | **River mode** | 论文演化线 + 溯源图 |

用户没有明确说 → 默认 Deep-read。

---

# Mode 1: Deep-read (学术深度)

Source-aware + formula-preserving + research-generative deep reading.
Use when the reader is a researcher, practitioner, or reviewer who needs to audit claims, assess novelty, and mine research directions.

## Core deliverables

1. **Human-readable report**
   - `report.md`

2. **Machine-readable trace artifacts**
   - `traceability_manifest.json`
   - `latex_paragraphs.json`
   - `artifact_index.json`

3. **Machine-readable research artifacts**
   - `research_lens.json`
   - `direction_board.json`

The report is the primary user-facing deliverable.
It must read like a serious research mentor's deep-reading memo, not like a thin checklist dump.
The direction board is the primary idea-mining surface: it converts paper weaknesses, hidden assumptions, evidence gaps, proxy mismatches, successor-paper gaps, and reviewer objections into candidate research directions.

## ClawHub and MIT-0 package discipline

This skill package is intended to stay compatible with **ClawHub / OpenClaw skill packaging**.

Keep the package lean:

- keep `SKILL.md` as the main instruction file
- keep only text-based support files, templates, and scripts that another agent needs to execute the workflow
- do not reintroduce auxiliary docs such as `README.md` or `CHANGELOG.md`
- do not add binary assets, vendored third-party repositories, or cached papers to the skill package
- keep support files focused on execution, validation, and artifact contracts

Keep the package license-safe:

- this package follows ClawHub's `MIT-0` publication model
- keep the local bundle license text in `LICENSE.txt`
- do not add restrictive or conflicting license terms elsewhere in the package
- do not vendor third-party projects or assets into the skill unless their license is compatible with `MIT-0` redistribution expectations
- when external tooling is useful, document it or install it outside the skill instead of copying its source tree into the package

Runtime discipline:

- bundled scripts are local text-processing helpers and should not make network calls
- if external search is needed, use the host agent's approved browsing/search capability rather than hidden scripts
- declare runtime dependencies honestly in frontmatter and metadata

## Non-weakening rule and depth bar

Do **not** treat the OpenClaw / ClawHub version as a lightweight summary mode.
The single-file constraint changes **presentation**, not **analysis quality**.

Never remove, weaken, shorten, or bypass any existing deep-reading requirement, including:

- source acquisition and disambiguation
- LaTeX-first reading when source is available
- PDF-assisted figure/table reading
- formula preservation
- proof-to-practice mapping
- OpenReview / reviewer context when relevant
- reviewer-lens audit
- claim IDs and traceability manifest
- final claim-to-evidence appendix
- research-generative overlay
- language policy
- validation scripts

The report depth bar should stay close to a strong top-conference paper memo:

- cover the full 25-section reading scope
- preserve central equations instead of flattening them into prose
- explain why modules exist, not only what they are called
- reconstruct likely author-side reasoning when the evidence supports it
- connect experiments back to claims, ablations, and alternative explanations
- extract reusable research patterns and future ideas
- produce concrete research seeds with minimum viable experiments, negative-result interpretation, killer objections, and killer results

If a tension appears between a shorter explanation and a more idea-generative one, choose the more useful research-direction analysis while keeping claims grounded.
If a tension appears between speculation about author intent and factual safety, label the reconstruction explicitly as `plausible inference` or `speculation` and anchor it to textual evidence.

## Research-generative overlay

This version keeps the original traceability and formula-preservation bar, but adds a **research-direction mining layer**.

The report must help the user answer not only:

- what the paper did
- whether the evidence supports the claims

but also:

- how the authors may have found the direction
- what hidden assumption `C` broke
- what unavailable mechanism `Y` had to be replaced
- what surrogate mechanism `Z` the paper constructed
- how each module maps to a failure mode
- why key citations matter in the story
- what hidden assumption can seed the next paper
- which new research directions are worth testing first

Use [references/research-generative-methodology.md](references/research-generative-methodology.md) and [references/research-direction-mining-best-practices.md](references/research-direction-mining-best-practices.md) whenever the user wants:

- author-perspective reading
- idea mining
- reverse story construction
- module-level design logic
- citation-function analysis
- reviewer-grade critique
- minimum viable experiment design
- boundary-pushing future directions

## Research-direction mining three-pass method

Read each paper in three direction-mining passes.
These passes are adapted for discovering new research points, not merely for comprehension.

### Pass 1: Five-C triage + direction promise

Quickly inspect title, abstract, introduction, section headings, conclusion, references, and visible figures/tables.
Answer the five triage questions:

1. `Category`: What type of paper is this: method, benchmark, theory, measurement, system, dataset, analysis, survey, or position?
2. `Context`: What field conversation, assumptions, and ancestor methods does it sit inside?
3. `Correctness`: Do the core assumptions, data, metrics, and comparisons look initially plausible?
4. `Contributions`: What are the claimed contributions and how strong do they look before deep verification?
5. `Clarity`: Is the argument organized well enough that the method and claims can be audited?

Then add a **direction-promise note**:

- what hidden assumption seems most likely to be attackable
- what omitted setting or stress condition appears promising
- whether the paper is worth a full second and third pass

### Pass 2: Evidence / method / figure chain reconstruction

Read the paper carefully but keep the goal causal:

`problem -> assumption break -> design principle -> module -> formula -> figure/table -> experiment -> claim`

During this pass:

- inspect key figures, diagrams, graphs, and tables as evidence, not decoration
- preserve central equations and explain their role
- build the challenge-to-module table
- map each result to the claim it supports
- mark missing controls, weak baselines, noisy metrics, unclear error bars, and unsupported narrative jumps
- identify the `available proxy` that replaces an `unavailable ideal mechanism`

### Pass 3: Virtual reimplementation + hidden-assumption attack

Recreate the work as if you had to implement, prove, or reproduce it.
Ask:

- What exact assumptions must be made for each module to work?
- Where would the method fail if one assumption were dropped?
- What tiny example, special case, or counterexample exposes the key idea or fragility?
- What proof step, algorithm step, data preprocessing choice, or metric definition carries the argument?
- What implementation details are missing but necessary for reproduction?
- What would a stronger, cleaner, or more decisive experiment look like?

This pass must produce future-work triggers.
A trigger is not a generic suggestion; it is a statement of the form:

`current method works if H -> under not-H it breaks -> new mechanism needed -> minimum experiment to test the opportunity`

## Successor-paper and reverse-citation reading

When the user asks for new research directions, do not stop at the paper's own related work.
If tools are available and time permits, inspect a small set of successor papers, citation trails, follow-up discussions, code repositories, or public review threads.

Use successor reading to answer:

- how later papers describe this paper's real contribution
- what later work treats as the bottleneck or limitation
- what claims were ignored, weakened, or reframed by the community
- which open gap remains after follow-up papers
- which direction is already saturated and which remains underexplored

If successor-paper search was not possible, say so and keep direction confidence lower.
Do not fabricate citation trends.

## Critical + creative reading rule

Every report must combine critical and creative reading.

Critical reading asks:

- Is the paper solving the right problem?
- Are the assumptions reasonable?
- Are the data, metrics, baselines, and controls sufficient?
- Are the conclusions stronger than the evidence?
- Are there simpler alternatives the authors did not rule out?
- What limitations are admitted, hidden, or structurally unavoidable?

Creative reading asks:

- What good idea can be transplanted elsewhere?
- What stronger setting makes the idea newly important?
- What generalization or simplification would be more elegant?
- What proxy can be replaced by a more direct signal?
- What negative result would change community understanding?
- What is the next research question a strong PhD student should test?

The final directions must be creative **and** falsifiable.

## Reviewer-grade audit integrated with direction mining

Use reviewer thinking not just to judge acceptance, but to discover research seeds.

Audit at least these dimensions when evidence allows:

- novelty and relation to prior work
- significance and likely community use
- technical soundness
- methodology rigor
- statistical validity and uncertainty reporting
- baseline and control completeness
- reproducibility and implementation sufficiency
- result-to-claim alignment
- clarity of figures/tables/formulas
- limitation honesty
- ethics, safety, or societal concerns when relevant
- specific constructive critique

Convert reviewer objections into direction candidates:

`reviewer objection -> why it matters -> what evidence would resolve it -> minimum viable experiment -> possible new paper`

## Full-loop research seed discipline

The skill does **not** replace the researcher or claim to have completed experiments.
It turns a paper into candidate directions that a researcher can test.

Every strong candidate direction must include:

- `seed_type`: one of assumption violation, unavailable mechanism, proxy mismatch, evidence gap, tiny example, successor-paper gap, reviewer objection, negative result, or cross-domain transfer
- `paper_anchor`: claim IDs and source evidence that triggered it
- `research_question`: a question that can be answered
- `hypothesis`: what might be true
- `minimum_viable_experiment`: the smallest decisive test
- `negative_result_interpretation`: what it would mean if the hypothesis fails
- `killer_objection`: the strongest reason the idea might be uninteresting or invalid
- `killer_result`: the result that would make the direction worth pursuing
- `first_week_plan`: practical steps for a researcher's first week
- `risk_level` and `expected_value`

Generic future-work lists are not enough.
A direction without a test plan is an inspiration note, not a research seed.

## Verification surface: body first, appendix last

The report itself remains the primary verification surface, but the detailed evidence placement is:

1. **Main body**
   - readable section-by-section analysis
   - `### Anchored Points` blocks near the relevant discussion
   - concise claim bullets in the form `- [C5.2][evidence-backed interpretation] ...`

2. **Final appendix**
   - detailed claim-by-claim evidence records
   - exact source files
   - section paths
   - line spans
   - page hints when available
   - quote snippets and excerpt windows
   - notes that help a human verify the claim quickly

Do **not** clutter the main narrative by inserting long locator bullets immediately after every claim.
Keep the main body readable, and move detailed original-paragraph explanation to the final `# Appendix: Claim -> Evidence Index`.

Use [scripts/render_inline_trace_report.py](scripts/render_inline_trace_report.py) after drafting the report and manifest to materialize or refresh that appendix.

## Formula-first preservation

When the paper contains key formulas, the report must **not** compress them into prose-only summaries.

For each central equation, objective, theorem statement, update rule, estimator, metric, loss, or constraint, explicitly include:

1. the equation itself in readable math form
2. symbol-by-symbol explanation
3. what optimization / estimation / filtering / proof role it plays
4. why the authors likely wrote it in this form instead of a nearby alternative
5. how it connects to the previous and next module
6. what may be brittle, heuristic, under-justified, statistically weak, or computationally expensive about it
7. how changing the equation creates possible new research directions

Do not weaken equation detail for the sake of shorter presentation.

## Source acquisition policy

Always assemble the **best available evidence package** before writing.

Preferred reading order:

1. **arXiv LaTeX/source package**
2. **user-provided LaTeX**
3. **best available PDF**
4. **supplementary material / appendix**
5. **official code or implementation notes when the user asks for reproducibility**
6. **OpenReview thread / rebuttal / meta-review when relevant**
7. **successor papers or citation trails when the user asks for new research directions**

### When LaTeX is available

Treat LaTeX as the primary structural source.

Use PDF only as a visual and pagination aid for:

- figure interpretation
- table reading
- page-local narrative flow
- page anchors
- visual sanity checks that cannot be recovered from source text

### When only PDF is available

Do not stop at PDF summarization immediately.

First check whether the same paper has a matching arXiv LaTeX/source package.
If it exists and matches the same paper, switch to **LaTeX-primary + PDF-assisted** reading.

If not, continue with the PDF and say explicitly that the reading is **PDF-primary**.

### When only title is available

Search for the paper and collect:

1. arXiv source package if available
2. the best PDF
3. supplementary PDF or appendix if available
4. OpenReview forum if venue is ICLR or otherwise OpenReview-hosted
5. official code, successor papers, or citation context when needed for direction mining

Never silently analyze the wrong paper.
Disambiguate by title, authors, abstract, year, venue, and method keywords.

### OpenReview policy

If the paper is an ICLR or OpenReview-hosted paper, look for:

- reviewer comments
- meta-review or area-chair summary
- author rebuttal or response
- revision signals relevant to acceptance

Use them to enrich:

- reviewer-lens audit
- confidence in claimed contributions
- limitations and unresolved doubts
- candidate directions derived from reviewer objections

### Missing source policy

If some sources cannot be found, do not abort.
State clearly what was attempted, what was found, what was missing, and how that affects confidence.
Then continue with the best grounded report possible.

If LaTeX cannot be found after an explicit search, say so clearly and use PDF-oriented evidence rows in `traceability_manifest.json` instead of pretending paragraph anchors exist.

## Language policy (Deep-read mode)

Write the **skill instructions, internal prompts, and template skeletons in English**.
Choose the **report language** from the user's current request language by default.

- if the user's current request is primarily in Chinese, write the report in Chinese
- if the user's current request is primarily not Chinese, write the report in English
- if the user explicitly requests another language, follow that explicit instruction
- if the request is mixed-language, follow the dominant user language in the current request

When writing the report in Chinese:

- keep proper nouns and fixed technical identifiers in English
- this includes paper titles, method names, module names, datasets, baselines, theorem or object names, citation names, equation symbols, claim IDs, filenames, and JSON keys
- translate section headings and explanatory prose into Chinese, but do not translate artifact filenames, schema fields, or claim IDs

## Mandatory artifacts (Deep-read mode)

### `report.md`

The report must cover, whenever the evidence supports it:

1. paper identification and source package used
2. one-sentence thesis and research equation
3. title interpretation
4. what problem the paper really solves
5. scientific problem ladder
6. how the authors may have found the direction
7. how the authors built the story
8. related work, key citations, and what was still missing
9. main idea
10. symbols, assumptions, and notation
11. key formulas and equation-by-equation explanation
12. theory / proof / practice mapping
13. algorithm or module walkthrough with concrete example
14. method deep reading: the author-thinking behind each module
15. figure explanation
16. experimental design
17. experiments as story evidence and claim alignment audit
18. reviewer-lens audit
19. innovation points and claim-by-claim support audit
20. story-making pattern worth learning
21. weaknesses and limitations
22. innovation type and scientific-boundary judgment
23. future directions and stronger idea paths
24. vivid plain-language story summary
25. exact sources used

Use [templates/report_template.md](templates/report_template.md) as the default skeleton.

For each numbered section:

- start with `### Anchored Points`
- add one or more claim bullets in the exact form `- [C<section>.<index>][label] claim text`
- keep the bullets concise
- follow the bullets with a real explanatory section, not just more bullets
- add tables, formulas, examples, reviewer-style critique, or story reconstruction when they help understanding

### `traceability_manifest.json`

This is the claim-to-evidence map.

Rules:

- every claim id in the main report body must appear in the manifest
- one bullet must not hide multiple independent claims under one id
- if a claim depends on multiple paragraphs, equations, tables, appendix passages, figures, or reviews, list them separately
- each claim entry should include `interpretation_type`
- each claim entry should preferably include `research_role`
- each claim entry should include human-friendly locator data when possible

### `latex_paragraphs.json`

This is the stable LaTeX anchor index.

Each entry must keep:

- `paragraph_id`
- `source_path`
- `line_start`
- `line_end`
- `section_path`
- `kind`
- `text`

### `artifact_index.json`

A compact index for the generated text-first bundle.

It should list the locations of:

- `report.md`
- `traceability_manifest.json`
- `latex_paragraphs.json`
- `research_lens.json`
- `direction_board.json`
- main PDF if any
- supplementary PDF if any
- source package path if known

### `research_lens.json`

This is the compact idea-mining artifact.
Use [templates/research_lens.template.json](templates/research_lens.template.json) and [references/artifact_contract.md](references/artifact_contract.md).

It should capture:

- the paper's research equation
- the likely direction-finding path
- challenge-to-module mapping
- per-module hidden assumptions
- citation logic
- reviewer-lens summary
- reusable story pattern
- strongest future idea directions
- links to the most important direction seeds

### `direction_board.json`

This is the structured research-direction board.
Use [templates/direction_board.template.json](templates/direction_board.template.json).

It should capture:

- ranked candidate research directions
- the evidence trigger for each direction
- hidden assumption or missing mechanism
- minimum viable experiment
- negative-result interpretation
- killer objection and killer result
- first-week plan
- score breakdown
- relationship to existing paper claims

## Claim discipline

### Claim ids

Use stable section-local ids such as:

- `C3.1`
- `C5.2`
- `C14.4`

### Claim splitting rule

Do not hide multiple judgments in one claim bullet.

### Evidence completeness rule

List all materially relevant evidence for a claim, not just one convenient paragraph.

### Interpretation labels

Each claim must declare exactly one of:

- `evidence-backed interpretation`
- `plausible inference`
- `speculation`

### Research-generative honesty rule

If the report reconstructs likely author reasoning, it must still point to the exact paragraphs, equations, figures, tables, experiments, reviews, or successor-paper signals that motivate that reconstruction.
Idea generation is required, but fabrication is forbidden.

### Direction trigger labels

Each direction seed should also label the trigger as one of:

- `evidence-backed interpretation`
- `plausible inference`
- `speculation`

Do not rank speculative seeds as high-confidence unless the uncertainty is explicit.

## Writing style for verification and idea generation

Prefer a report that is pleasant to read **and** easy to audit.

For every claim, the user should be able to answer:

1. What section-level conclusion is being made?
2. Is it direct evidence, plausible inference, or speculation?
3. Where should I verify it in the appendix?

For the strongest research-direction sections, the report should also answer:

1. What hidden assumption broke?
2. What missing mechanism was replaced?
3. What future paper becomes possible if that assumption fails harder?
4. What minimum experiment would tell us whether this future paper is real?
5. What result would kill the idea?
6. What result would make the idea exciting?

Use phrasing such as:

- "A plausible author-side thinking path is ..."
- "This module is best understood as a surrogate for ..."
- "The citation is not ornamental; it functions as ..."
- "The deepest reusable lesson is ..."
- "This weakness can be converted into a new research direction ..."
- "The minimum viable experiment is ..."
- "The killer objection is ..."
- "A negative result would still be useful if it shows ..."

The report should sound like a research mentor reconstructing how the work may have been invented and how it could become the next project, not like a generic summarizer.

## Grounded workflow (Deep-read mode)

1. Assemble the best source package.
2. If LaTeX is available, extract paragraph anchors with `scripts/extract_latex_paragraphs.py`.
3. Perform Pass 1 five-C triage and decide whether full deep reading is warranted.
4. Perform Pass 2 evidence / method / figure chain reconstruction.
5. Perform Pass 3 virtual reimplementation and hidden-assumption attack.
6. Draft `report.md` using anchored claim IDs in the main body.
7. Keep claim bullets concise and put longer explanation in prose, tables, formulas, examples, and story reconstructions after them.
8. Fill `traceability_manifest.json` so each claim points to one or more paragraph IDs or fallback anchors.
9. Fill `research_lens.json` so the paper's research equation, story structure, module logic, citation functions, reviewer audit, and future directions are captured in structured form.
10. Fill `direction_board.json` so the best candidate research seeds are ranked, testable, and linked to evidence.
11. Fill `artifact_index.json` so the bundle stays portable.
12. Run `scripts/validate_traceability.py`.
13. Run `scripts/validate_direction_board.py` when `direction_board.json` is present.
14. Run `scripts/render_inline_trace_report.py` to append or refresh the final `Claim -> Evidence Index` appendix in `report.md`.
15. Only then finalize the bundle.

## Small-batch policy (Deep-read mode)

For a small paper batch:

- produce one standalone `report.md`-style bundle per paper when the user expects detailed reading
- do not collapse multiple papers into a shallow combined summary
- optionally add a cross-paper direction board if the goal is choosing a new research direction
- rank cross-paper directions by novelty, evidence gap, testability, expected impact, feasibility, and relationship to the user's research interests

## Failure handling (Deep-read mode)

If some sources cannot be found, do not abort.
State clearly:

- what was attempted
- what was found
- what was missing
- how the missing source changes confidence
- which claims or direction seeds are affected

Then continue with the best grounded report possible.

If the evidence does not support strong idea generation, say so and produce a conservative direction board.
Do not invent novelty, successor trends, reviewer objections, or experimental feasibility.

---

# Mode 2: Story Mode — 把一篇论文当一个故事讲

读一篇论文，最难的不是看懂，是讲明白。讲给一个不懂这个领域的聪明人——讲到他能复述出来——你才算读完。

这是一个讲故事的活。一篇论文背后，有主角、有困境、有撞墙、有转折、有解法、有结局、有内核。把这副脊柱先立起来，再往上挂内容。

## 故事骨架

把论文讲成故事，脊柱是这七拍。不是七个子标题，是节奏要求：

1. *主角* — 谁在这个故事里？这个领域的研究者、一个具体的模型、一个用户、一个系统、甚至论文要回答的那个问题本身。开场两句先把主角领上台。
2. *困境* — 主角面前撞着什么？解不了会怎样？把"利害"摆给读者——读者要看见值得为这件事坐下来听完。
3. *旧路* — 前人怎么试的？为什么没走通？让读者亲眼看一遍那堵墙。开创性问题没有前作，这一拍可以省。
4. *转折* — 作者看到了别人没看到的什么？整篇论文的"啊哈"在这一拍发生。这是故事的腰，整副脊柱靠它撑住。
5. *解法* — 带着新视角，主角怎么动手？机制、设计选择的理由——一步步把方法在那个例子上铺开，让读者跟着推。
6. *结局* — 解完了，世界长什么样？挑两三组最说明问题的数字让读者感受到差距。最反直觉的副发现单独留一拍呈现。
7. *内核* — 这个故事真正留下的那颗东西。不是论文结论的复述，是听众走出门带走的那一句话。

## 章节命名

复用固定 section 名：`问题 / 翻译 / 核心概念 / 洞见 / 博导审稿 / 启发`。故事弧体现在每段的**写法和衔接**上，不在标签上。

### 七拍与执行步骤的映射

| 故事拍 | 在执行哪一步 |
|-------|-----------|
| 主角 + 困境 + 旧路 | 问题 |
| 转折预告 → 转折登场 | 问题收尾 → 翻译开头 |
| 解法 + 结局 | 翻译主体 |
| 故事道具 | 核心概念 |
| 内核 | 洞见 |
| 故事评审 | 博导审稿 |
| 听众的故事 | 启发 |

**写完默读：这读起来像一个人在跟我讲一个故事，还是 N 段独立汇报？后者 → 重写。**

### 七拍落在一篇论文上长什么样

拿 LenVM（让模型一边写一边知道还要写多远）举例：

- *主角*：一个写长答案的语言模型——它在写 GSM8K 的解题过程
- *困境*：模型不知道什么时候该收尾，结果要么没说完就停，要么啰嗦到 token 烧光
- *旧路*：之前的做法是直接训长度限制，硬卡；可一卡，推理质量就掉
- *转折*：作者看到——长度本来就是一种"剩余距离"，可以建一个 value 头实时预测，让模型每写一字都知道还差多远
- *解法*：在 RL 训练里加一个 length value head，用 -1 constant reward 让它学到"少写一字省一字"
- *结局*：在多个 benchmark 上推理长度降 30%，准确率不降反升；token 词云里 "wait/think" 让位给 "finalize/confirm"
- *内核*：监督模型"知道止"，比监督它"会答"更值

写出来不是七个段落，是一条线——把这七拍藏在「问题→翻译→核心概念→洞见」的连续叙述里，读者只感受到一个故事在走。

## 写作原则（Story Mode）

五条核心原则，决定文章是"一个人在讲故事"还是"机器在汇报内容"：

1. *故事流贯到底* — 第一句到最后一句是同一个故事在走：主角立了、困境亮了、旧路撞了、转折来了、解法展开了、结局收了、内核落了。每段末句给下段留个口子——读者读到一半，放不下。
2. *一个锚点撑全文* — 「问题」里立的那个具象例子就是锚点。「翻译」「核心概念」都在这个锚点上展开，每段都回到它。换锚点 = 换地图 = 读者前面建的直觉全丢。
   - **每个 section 里也只能用一个例子**。两个例子 = 切碎读者直觉，即使两例都强，挑最锋利的一个。
3. *推理外显* — 模拟"一个人想明白的过程"，而非呈现"想明白之后的结果"。用"既然 A 是 B，那能不能 C 也是 D？"带读者一起推。让读者觉得结论差一步就是自己想到的。
4. *变形替代定义* — 解释两个概念的关系时，把 A 连续变形成 B，不要说"A 和 B 是 XX 关系"。「把 LSTM 变形→看起来像 ResNet」比「LSTM 和 ResNet 是对偶的」有力十倍。
5. *落点在能用* — 给出"这意味着你可以___"，而非"这让我们重新思考___"。读者听完故事要带走一个能动手的东西。

## 红线（Story Mode，每条必须过）

1. *口语检验* — 你会这样跟朋友讲一篇论文吗？不会→改。学术腔是默认敌人。
2. *零术语* — 先用大白话落地，再顺带提术语名。如果必须用原文术语才能解释，说明还没懂。
3. *短词优先* — 能用两个字说的不用四个字。「本文提出了一种新的框架」→「他们做了个东西」。
4. *一句一事* — 每句只推一步。
5. *具体* — 名词看得见，动词有力气。形容词能砍就砍。
6. *开头给理由* — 问题部分的第一句让人想知道答案。
7. *不填充* — 删学术套话（「近年来随着...的发展」「值得注意的是」）。每句干活。
8. *信任读者* — 说一遍够了。不重复结论。
9. *诚实* — 论文有硬伤就说有硬伤。看不懂的部分说看不懂。
10. *6 个月后的我看得懂吗？* — 每个术语首次出现必须落地（"value function = 给定当前状态预测未来累积奖励"），每个公式必须翻译成自然语言，每个引用都要说明对外行的意义。自检：默想"半年后搜到这篇，30 秒内能回想起核心吗？"
11. *外行优先于凝练* — 该展开就展开，不要为了"短"砍掉读者真正需要的铺垫。凝练的尺度只针对 title；正文该多长就多长。
12. *故事一气* — 整篇读下来，像一个人在跟你讲一件事，不像多份独立汇报拼出来的合订本。章与章之间靠故事弧的牵引力相连。自查：去掉章节标题读全文，故事流还在不在？

## Title 写作规范

title 是这篇故事的*灵魂句*——读者扫一眼就知道这篇论文带走什么。

**写作约束（按优先级）**

1. *中文母语凝练* — 像汪曾祺、王小波、阿城、李娟的标题：短、净、有刃。
   - 写完默问：「一个没读过翻译小说的中国人会这样说吗？」不像 → 重写。
   - 杀句式：被动句（"被锁在…里"）、"是…的"句、长定语后置（"那个由…引起的…"）、"进行+名词"、"让我们…"。

2. *零中英混杂* — title 不出现英文术语（RL / HR / Agent / token 等都不行）。术语放正文展开，title 只放思想。例外：人名、产品名（GPT、Claude）。

3. *6-15 字* — 短到能记住，长到能承得住一个发现。超过 15 字基本就是没炼到位——回去再砍。

4. *动词为骨，名词具体* — 形容词能砍就砍（"重大的""根本的""惊人的"全删）。每个字都得干活。

5. *自带张力，三种姿态任选其一*：
   - *反直觉* — 「学会反成枷锁」
   - *对仗或并置* — 「教人如教己」「记得太牢，想不出新」
   - *转折或反讽* — 「答得越准，看见越少」

6. *不复述题目，不当方法名* —
   - ✗「关于强化学习预训练空间转移的探索性研究」（学术腔）
   - ✗「PreRL：把强化学习搬进预训练空间」（方法名 + 方法描述）

**可识别性测试（必须过）**：把 title 单独贴出来，给一个没读过这篇论文的人看——他应该有方向感。如果完全猜不到，**必须用中文 subtitle 兜底**：

```
title:      字未出，止已现
subtitle:   把"还要写多远"做成一个 value 函数 — Length Value Model
```

## 执行（Story Mode）

### 1. 获取内容

- arxiv URL / 论文名称 / PDF / 本地文件

如果论文有一张承载全文核心思路的总览图（Figure 1），提取并保存。判断标准：让人一看就抓住论文在做什么。不是所有论文都有——没有就跳过。

### 2. 问题：搭台——让读者亲历主角的困境（拍 1-3 + 转折预告）

三件事按顺序在同一段连续叙述里完成：

1. *亲历* (拍 1+2) — 主角谁、面前撞着什么、解不了会怎样。例子最好简单到一两句话能说完。
2. *旧路* (拍 3) — 之前的研究者在这个例子上怎么做？为什么走不通？
3. *转折预告* (拍 4 的引子) — 本论文作者在这个例子上看到了什么别人没看到的入口？只引方向不展开机制。

**三拍是节奏要求，不是格式要求**——不要硬加子标题。问题节用一段连续叙述更有钩力。

### 3. 翻译：推进——转折登场，解法展开（拍 4+5+6）

重心是"转过那个弯之后怎么走"。*沿用同一个例子*。

需要覆盖（都在那个例子上）：
- 转折是什么（拍 4：作者看到的那个新视角，一句话说清）
- 解法怎么动（拍 5：核心机制/方法）
- 结局长什么样（拍 6：挑最说明问题的两三组数字）
- 理解全文需要的钥匙概念（如果有）

**翻译节必有清单**：
1. *承重类比* — 不止是装饰，要能映射方法的关键组件。
2. *三组以上具体数字* — baseline / 改进 / 关键 ablation
3. *一个反直觉的副发现* — 论文里最让人"哇"的一段，单独呈现。有就必须保留，没有就明说没有。
4. *不放原始公式* — 公式对外行无用。用文字翻译。

### 4. 核心概念：故事道具——主角手里那几件东西

挑出论文中最关键的 **3 个**概念，逐个拆解。这些是故事里主角用来转过那个弯的道具——少了任一件，故事就讲不通。

每个道具：
- *一句话*：这东西是什么，干什么用的
- *回到例子*：在那个例子上，这个道具长什么样？少了它在那个例子上会怎样？
- *为什么重要*：少了它论文的逻辑链断在哪里

### 5. 洞见：内核——故事走完留下的那颗东西（拍 7）

用一句话说出来。检验：脱离论文上下文，它还有没有力量？

说不出来就重读翻译节。没有思想火花就直说「这篇论文是工程改进，没有认知层面的新发现」。

### 6. 博导审稿：故事评审——这个故事站不站得住

像带了二十年研究生的博导在办公室跟学生聊：

- *选题眼光*：困境真实吗？真缺口还是人造缺口？
- *方法成熟度*：解法是巧劲还是蛮力？找方法的**根本预设有没有问题**。自问：这论文如果错，最可能错在哪一步？错的根源是不是一个未被讨论的预设？
- *实验诚意*：baseline 公不公道？消融到位没？
- *写作功力*：最该说清楚的地方有没有偷懒？
- *判决*：strong accept / weak accept / borderline / weak reject / strong reject

### 7. 启发：听众的故事——这故事接到我的生活里

落点在"能用"，不在"能想"。三个视角试探，命中展开，没命中跳过：

- *迁移*：论文的某个机制能移植升级我体系的某个零件吗？怎么接？
- *混搭*：和已有的东西组合能产生新东西吗？
- *反转*：论文的做法和我的默认假设相反吗？该停下什么、开始什么？

### 8. 收口：过红线 + 故事流自查

逐条扫红线（12 条）。额外检查：破公式、变节奏、杀金句、查跳跃。故事流自查：盖住章节标题读全文，故事流还在不在？

### 9. 写入

使用 `knowledges/papers/` 作为输出目录（见末尾 Save location 说明）。参考 `references/story-template.org` 作为输出结构模板。

---

# Mode 3: River Mode — 倒读法（论文溯源）

一篇论文不是孤岛。它站在前人的肩上，也踩着前人的伤疤。倒着挖到根，再正着看过来——问题怎么长出来的，每个人看到了什么别人没看到的，解法怎么一步步逼近真相。

## 核心逻辑

读论文最常见的错：只看眼前这一篇，不知道它从哪来。倒读法反过来——先找到这篇论文在批判谁、改进谁，再找那篇论文又在批判谁，递归五层，挖到源头。然后掉头，从源头正向读回来。

## 章节结构

- `问题之河` — 全貌一句话
- `溯源地图` — ASCII 图展示演化链
- `演化叙事` — 从最老到最新，问题为主线
- `前沿延伸` — 目标论文之后的最新进展
- `一张图看懂` — 问题-解法演化总结图
- `洞见` — 读完整条线你看到了什么
- `启发` — 这条线对"怎么做研究"的启示

## 图像规范

所有图表用纯 ASCII 字符。允许：`+ - | / \ > < v ^ * = ~ . : # [ ] ( ) _ , ; ! ' "` 和空格。禁止 Unicode 绘图符号。

## 红线（River Mode）

1. *问题为轴* — 主线是"问题怎么演化"，不是"论文怎么排列"。论文是配角，问题是主角。
2. *口语检验* — 你会这样跟朋友讲一个领域的发展史吗？不会就改。
3. *差异为核* — 每篇论文的讲解重心是"它和前一篇的差异在哪"，不是独立介绍。
4. *零术语* — 先用大白话落地，再顺带提术语名。
5. *逻辑不断链* — 从第一篇到最后一篇，因果链条不能断。读者能感受到"所以他们才会这样做"。
6. *诚实* — 找不到五层就说找到几层。论文之间的关系不确定就说不确定。不编造引用关系。

## 写作原则（River Mode）

1. *差异驱动叙事* — 不要给每篇论文写独立摘要再拼起来。以"这篇看到了前一篇的什么问题"作为每段的开头。
2. *变形替代定义* — 讲两个方案的区别时，把方案 A 连续变形成方案 B。
3. *推理外显* — 每个解法出现前，让读者感受到"不这么做不行了"的压力。
4. *两张图* — 溯源地图（叙事前）+ 问题-解法总览（叙事后）。

## 执行（River Mode）

### 1. 获取目标论文

arxiv URL / PDF / 论文名称 → 获取标题、作者、摘要、引言。

### 2. 提取批判链线索

仔细读引言和相关工作。找出：
- 它明确说"前人方法 X 有问题 Y"的地方
- 它声称自己改进了哪篇论文
- 它对比的 baseline

锁定被批判/被改进的核心论文（通常 1-3 篇，选最直接的那条线）。

### 3. 递归溯源

对找到的核心前序论文重复同样过程。规则：
- 最多递归 **5 层**（或到该领域奠基论文为止）
- 每层只追问题最相关的那条线
- 如果某层找不到明确的被批判对象，停在那里

### 4. 前沿延伸

反方向：目标论文之后有没有新论文在批判/改进它？使用搜索/浏览工具找到最相关的 1-3 篇后续论文。

### 5. 构建演化线

格式：
```
[最老] Paper_0 → Paper_1 → ... → [目标] → [后续]
```
每条箭头标注：后者看到了前者的什么问题。

### 6. 正向费曼叙事

从最老的论文开始，以问题演化为线索串联。每篇论文讲三件事（以差异为重心）：
1. 它看到了前人方案的什么具体问题
2. 它的解法核心思路
3. 这个解法留下了什么新问题（→ 渡到下一篇）

### 7. 画图

两张 ASCII 图：
- *溯源地图*：展示论文间的引用/批判关系
- *问题-解法总览*：把整条线压缩到一屏

### 8. 提炼洞见

回答：这条演化线背后真正在发生什么变化？下一步最可能往哪走？

### 9. 写入

使用 `knowledges/papers/` 作为输出目录（见末尾 Save location 说明）。参考 `references/river-template.org` 作为输出结构模板。

---

# 全局设置

## Save location

Paper digests, deep-reading reports, story-mode papers, and river-trace documents all go to **`knowledges/papers/`**.

This is the dedicated papers directory — do not put paper content under `knowledges/ai-tools/` or any other non-papers subdirectory.

Cover images go to `knowledges/image/` as usual.

## Image path in markdown

When referencing the cover image from a file under `knowledges/papers/`, use the path `../image/{filename}`.

## Markdown 格式约束

Story Mode 和 River Mode 的输出遵循：
- 加粗用 `*bold*`（单星号），禁止 `**bold**`
- 标题层级从 `*` 开始，不跳级
- 图表用纯 ASCII 字符，不用 Unicode 绘图符号

Deep-read mode 不受此约束，按 `report_template.md` 格式。
