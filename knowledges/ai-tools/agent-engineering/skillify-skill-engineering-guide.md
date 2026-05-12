---
title: "SKILLIFY —— Skill 工程：Agent Skills 的设计、优化与维护"
tags:
  - skillify
  - skill-engineering
  - agent-skills
  - agent-prompting
  - coding-agent
  - prompt-engineering
  - context-optimization
  - agent-architecture
date: 2026-05-12
source: "https://x.com/av1dlive/status/2053880492680958439"
authors: "@av1dlive"
---

# SKILLIFY —— Skill 工程：Agent Skills 的设计、优化与维护

> **来源：** @av1dlive 的 X 长文  
> **参考：** Garry Tan "The Skills Are the Prompts" | Anthropic (Barry Zhang, Mahesh Murag) "Don't Build Agents. Build Skills Instead." | Perplexity "Designing, Refining, and Maintaining Agent Skills at Perplexity"

---

## 核心论点

**Prompt Engineering 已死。100x 工程师现在在做 SKILLIFY。**

所谓 SKILLIFY，就是把一次性的 prompt 固化为可复用的 Skill 文件——一个有结构的文件夹，包含描述、约束、引用、脚本和 Eval。

大多数人之所写不好 Skill，不是因为他们不够努力，而是因为他们用写代码的直觉去写 Skill。而**写 Skill 和写代码是完全相反的思维方式。**

Skill 不是文件，它是文件夹。

---

## 行业共识：Skill 代替 Prompt 是必然方向

三个团队从不同方向抵达了同一个结论：

- **Garry Tan（4 月发帖）：** "当别人问我怎么给 AI '写 Prompt'，答案是：我不写。Skills 就是 Prompts。"
- **Anthropic Barry Zhang & Mahesh Murag（AIE 演讲）：** "别构建 Agent，构建 Skills。"
- **Perplexity（内部 Skill 设计指南）：** "如果你像写代码一样写 Skill，你一定会失败。"

三个最受尊敬的 AI 团队，不同的路径，同一个答案。

**原因：Prompts 不累积。** 每次对话都从零开始。你个人对 Prompting 越来越擅长，但系统永远不会变聪明。

**Skills 累积。** 你今天写的 Skill 下个月还在。Agent 失败了你追加一条错误。失败变成了指南。Skill 最终反映了你遇到过的**每一个边缘情况**，而不仅仅是你第一天想象中的理想流程。

---

## Skill 的文件夹结构（决定 80% 的成本）

Perplexity 的内部指南第一条就指出这个：**大多数人第一个搞错的就是结构。**

### 错误做法（新手）

一个巨大的 `SKILL.md`，把所有指令、示例、边缘情况、API 文档全部塞进一个文件。每次触发都加载全部内容，8,000 tokens，永远花这么多。

### 正确做法（三层上下文模型）

```
my-skill/
├── SKILL.md              ← 加载层：2,000–8,000 tokens（触发后加载）
│                           核心约束，不是文档
├── references/           ← 运行时层：按需读取（免费直到使用）
│   ├── api.md
│   ├── errors.md
│   ├── style.md
│   └── templates/
├── scripts/              ← 确定性代码：零成本（不经过模型推理）
│   └── fix-git-history.sh
├── evals/                ← 测试集：先于 Skill 编写
│   ├── should-trigger.txt
│   └── should-not-trigger.txt
└── assets/               ← 模板/输出格式
```

**关键优化：**
- `SKILL.md` 是 Agent **触发后**才会读取的文件——只有它需要保持精简
- `references/` **不消耗任何 token**，直到 Agent 显式请求读取
- `scripts/` 里的确定性脚本每次运行结果完全一致，且[拉取/load]时零成本
- 你的 Skill Body 应该是**约束**，不是文档

> 我有个 Skill 原本 6,000 tokens。把参考材料移到 references/，模板移到 assets/ 后，Skill Body 变成了 800 tokens。行为完全一致。过去我每次触发都在白花 5,200 个 tokens。

---

## 描述（Description）—— 你写的最贵的 100 个 tokens

每一百个 tokens。每次对话。每个用户。**即使 Skill 没有被触发，这些 token 也要付。**

### 描述不是"功能介绍"，是"路由触发器"

Agent 在会话启动时读取你 Skill 库里的每一个描述，来决定加载什么。写错了，错误的 Skill 会触发。写窄了，正确的 Skill 永远不触发。

**从第一天开始，每一段描述都用 "Load when" 开头。**

- ❌ "Helps with API debugging"
- ❌ "Use for X"
- ✅ **"Load when the user is getting a 4xx or 5xx from a service they own and are trying to diagnose it"**

"Load when" 强制你用**触发器**思维来思考，而不是**能力**。能力是什么——触发器是何时 Agent 应该决定加载它。这两个问题完全不同，只有触发器才对描述有意义。

### 用工程师的真实语言写

不是"there is a compilation error in my project"，而是"my build is broken"。
不是"the query is underperforming"，而是"this is slow as hell"。
不是"there is a recurring failure pattern"，而是"why does this keep happening"。

Agent 根据语义相似度做路由。如果用户说"my build is broken"而你的描述是"compilation error resolution"，Skill 可能不会加载。**用你用户在冒烟时的真实话术写描述。**

---

## Skill Body —— 不是文档，是约束

### 黄金测试：没有这句话 Agent 会搞错吗？

**每一行都必须通过这个测试：没有这行，Agent 会不会在这个场景下犯错？**

- 如果不会 → 删掉。模型已经知道。
- Agent 知道怎么写 PR 描述 → 不需要写"write a clear title and describe the changes"
- Agent 知道 Python → 不需要写"use descriptive variable names"
- Agent 知道 git → 不需要写 commit 格式（除非有特例）

**模型不知道的是你的 taste。**

- "we don't force-push to main, ever, even during a hotfix" — 你的 team 的 taste
- "type stubs go in the same file as the implementation, not in a separate .pyi" — 你的 taste
- "API errors always get logged before they're raised, never after" — 你的 taste

**这个测试会砍掉大部分人写的东西的 60%。** 几乎所有 Skill 的初稿有三分之二是模型已经知道的内容。删掉它们。剩下的才是 Skill。

### 写意图，不写步骤

我的第一个 PR Review Skill 有 12 个步骤：检查标题格式、运行 linter、搜索 TODO、读 diff、检查测试覆盖率……

重写后是 4 句话：
> "我对照着 references/style.md 中的团队代码风格审查 PR。我只标记那些会在生产环境中出问题的问题，而不仅仅是次优的代码。我在读完测试文件之前绝不开绿灯。这里有三个我认为审查得不错的 PR，以及原因。"

重写后的版本输出更好，而且会随着模型升级变得更好。**过程式 Skill 会老化。基于意图的 Skill 会累积。**

---

## References 与零成本层

三层上下文成本模型：

| 层级 | 成本 | 说明 |
|------|------|------|
| **Index 层** | ~100 tokens | 描述，总是加载。你无法逃避这个成本，所以每个字都得值 |
| **Load 层** | 2,000–8,000 tokens | SKILL.md，触发后加载。这是你要优化的重点。大多数 Skill 应在 1,500 tokens 以下 |
| **Runtime 层** | 无上限 | references/，只在 Agent 请求时加载。免费直到需要 |

**把能推到 Runtime 层的都推过去。**

Index 层引用 Runtime 层，但不加载它：在 Skill body 里写"Consult references/style.md for house style before writing any prose"。这句话 8 个 tokens，告诉 Agent 需要时加载什么。替代方案是把整个风格指南塞进 Skill body，每次触发都为它付钱。

---

## Evals 在 Skill 之前，不在之后

**在写 Skill 之前，先写 10–20 条查询。** 每条标记为"应该触发"或"不应该触发"。

10 条 should-trigger + 10 条 should-not-trigger。

- Should-triggers 告诉你这个 Skill 究竟是干什么的
- Should-not-triggers 强迫你定义边界

**如果你写不出这些 Evals，你就不需要这个 Skill。**

Evals 也是避免模糊 Skill 的强制机制。如果你的 Skill 叫 "writing-helper" 而你写不出 10 条具体的 should-trigger 查询——这个 Skill 太宽了。拆开："api-changelog-writer" 和 "error-message-copywriter"。现在 Evals 自然就出来了。

实际操作：
- 上线前跑一次 Evals
- 每次重大变更后跑一次
- 如果一个变更破坏超过 2 条 Eval，回滚
- Evals 是契约。Skill 是实现。

---

## Skill 是 Append-Only（追加机制）

**Agent 失败时，不要重写描述。不要重写 body。追加一条 gotcha。**

Gotcha 部分是 Skill 在发布之后唯一应该增长的部分。其他一切应保持稳定。

原因：如果你每次失败都重写描述，描述会漂移。积累条件和特例后，路由不再准确。

**Gotcha 部分不影响路由。** 它在 Agent 已经决定加载 Skill 之后才生效。你可以无限追加，永远不会触碰路由相关的内容。

**Gotcha 也是 Skill 的组织记忆。** 每一条都是 Agent 在真实任务中的真实失败。随着时间的推移，它比原始 Skill body 更有价值——原始 body 源于想象，gotchas 源于经验。

> 我最老的 Skill 有 600 tokens 的 body 和 400 tokens 的 gotcha section。大多数有用指令都在 gotchas 里。这就是三个月真实使用的结果。

---

## 不要让 LLM 帮你写 Skill

**自生成的 Skill 平均没有额外价值。** Perplexity 直接指出了这一点。Barry 和 Mahesh 在舞台上暗示了这一点。

模型可以起草结构。可以填充显而易见的约束。但它无法**识别自己训练分布的缺口。**

Skill 的价值在于它编码了模型**没有它就会搞错的东西**。模型看不到自己会搞错什么。它接触不到自己失败的案例。它无法从内部观察自己的盲点。

能写好 Skill 的人，是**亲眼看过 Agent 失败**的人。在真实任务上。不止一次。同一种失败模式在不同的上下文中重复出现。

那个人是你。不是模型。

> 模型能写一个看起来正确的 Skill。正确的结构，正确的格式，覆盖明显的 case。上线顺利。然后三周后，它遗漏了在你环境里真正重要的 case——因为这些 case 是你特有的栈、约定、用户、失败历史。这些全不在模型的训练数据里。

**Skill authoring 是少有的瓶颈在真正人类判断力的软件任务。**

---

## 六周的演进

| 时间 | 发生了什么 |
|------|-----------|
| **W1** | 三天发 9 个 Skill。感觉很好。Agent 正确完成了一次 PR review，以为自己发现了什么。 |
| **W2** | Agent 开始触发错误的 Skill。debug-api 在提到 API 的任何请求上都加载——哪怕是文档请求。Context 被无关指令填满。 |
| **W3–4** | 重写每个描述。能力语言 → 触发器语言。Skill 路由开始正确。噪音下降。 |
| **W4** | 把所有重内容移到 references/。Skill body 从平均 3,200 tokens → 900 tokens。会话性能提升。不再碰到复杂任务的 context budget 问题。 |
| **W5** | 事后写了所有 Evals。发现 3 个 Skill 在同一个触发器上重叠。合并 2 个。删掉 1 个——因为写不出 10 条真实的 should-trigger。原来这个 Skill 是为一件我只做过一次的事写的。 |
| **W6** | 打开一个 3 周没碰的 Skill，在 gotcha 部分发现一行自己完全不记得写过的内容。Agent 在一个 monorepo 任务上失败了，记录了失败，然后在一次反思循环中更新了 Skill。那条 gotcha 是对的。它抓住了我写原 Skill 时没有预料到的东西。 |

变化不是系统变魔术了。**变化是错误不再重复。成功拦截了一次错误的 Skill，会在后续持续拦截同样的错误——不需要你重新教。**

---

## 常见陷阱

| 陷阱 | 表现 | 修正 |
|------|------|------|
| **描述漂移** | 每次失败后重写描述，6 次后路由失灵 | 上线后永不重写描述。追加 gotchas。 |
| **Token 盲区** | Skill body 5,000 tokens，一半是模型已知道的 | 每行跑"没有这行会犯错吗"测试。移动参考材料到 references/。目标 < 1,500 tokens。 |
| **触发器碰撞** | 两个 Skill 在同一查询上触发，context 被冲突指令填满 | 上线前写 Evals，包含 should-not-trigger。重叠超过 3 条 should-trigger 则合并或重定义边界。 |
| **LLM 起草 Skill 缺边缘情况** | 看起来正确，上线顺利，漏了所有你环境里实际情况 | 只有亲眼看过 Agent 失败的人审阅并加了真实 gotchas 后才能上线。 |
| **References 过期** | references/api.md 6 个月了，Agent 自信地调用不存在的端点 | 每文件标注最后更新日期。超 60 天标记需审查。 |
| **Eval 腐化** | Evals 通过是因为 Skill 现在在 Eva 查询上特别优化了路由 | 每月从真实会话中添加真实查询到 Eval 集。Eval 应包括真实世界查询。 |

---

## 7 天入门计划

大多数人搞错的地方：试图先构建系统再用它。正确做法：**通过使用来构建系统。**

| 天 | 做 |
|----|----|
| **D1** | 一口气读完三个来源：Garry Tan 的帖子、Anthropic 的 AIE 演讲、Perplexity Skill 设计指南 |
| **D2** | Clone 一个参考 stack（如 gstack/agentic-stack），看结构 |
| **D3** | 挑一个**你每周都做**的工作流。不是新流程。是你已经知道失败模式的那个 |
| **D4** | 用 Agent 做一次。不优化。观察 Agent 在哪里搞错——这些错误的地方就是 Skill body 的内容 |
| **D5** | 执行 `/skillify`。Skill 进入库，Agent 下次会自动找到它 |
| **D6** | 在真实实例上运行。追加 gotchas。第一次真实运行会暴露你没想到的东西→去 gotcha section，不是 body |
| **D7** | 再上两个工作流 |

到 D7 你就有 3 个 Skill、3 个脚本、3 个触发器。你不再写 prompt。上周编码的工作流下个月还在库里。它们运行完全一致。每次 Agent 失败你追加一条 gotcha，它们就优化一次。不需要你做任何额外的事。这就是**累积效应。**

---

## 如果重来，我会怎么做

1. **先写 Evals，再写描述。** 我前两周都是先写描述再写 Evals，接下来的两周为此付出了代价。
2. **从 5 个 Skill 开始，不要 20 个。** 每加一个会增加路由问题的复杂性。先让 5 个路由正确，再加。
3. **从初稿就在每个描述里写 "Load when"。** 事后再去加是发现你的描述从一开始就不是触发器的尴尬时刻。
4. **在你需要之前就建好 references/ 目录。** 第一版 Skill 的冲动是把所有内容塞进 body——因为更快。克制它。
5. **单独维护一个失败日志，和 gotcha section 分开。** 一个文件，一行一个失败，日期+Skill 名。如果 gotcha section 长到 30 秒扫不完，说明有该记却漏掉的 gotcha。
6. **不给 /skillify 一个失败故事就别用。** 没有这个上下文的输出只覆盖了 happy path——那是你不需要帮助的部分。

---

## 总结

> Prompts 活在你的大脑和聊天记录里。每次对话重置。不累积。抓不住上周二的失败然后应用到周四的任务上。

> Skills 活在 git 仓库的纯文本文件里。Gotcha section 增长。References 被更新。Evals 抓住回归。系统下个月比今天知道更多——不需要你重新教任何事。

最让人惊讶的是：**瓶颈不是技术。** 文件夹结构很简单。格式很友好。真正难的部分是——看够 Agent 失败，知道它缺什么它自己还不知道。

那个知识是你的。它不能被生成。只能被累积。

**拥有你的 Skills。拥有塑造它们的失败。把它们放在纯文本文件和 git 里，这样没有人能从你这里夺走它们，而且每次 Agent 失败它们都会变得更好。**

---

## 核心参考材料

- Garry Tan — "The Skills Are the Prompts" — [x.com/garrytan](https://x.com/garrytan)
- Barry Zhang, Mahesh Murag — "Don't Build Agents. Build Skills Instead." (AIE 演讲)
- Perplexity — "Designing, Refining, and Maintaining Agent Skills at Perplexity" (内部指南)

*本文由原作者研究与撰写，经 Claude Sonnet 4.6 编辑。*  
*Processed on 2026-05-12 from @av1dlive's X article.*

---

## 与知识库其他文章的关联

- **[Agent Harness Engineering](agent-engineering/agent-harness-engineering.md)** 讨论了 Agent 脚手架的总体架构，本文是其"Skill 子系统"的深度展开
- **Two papers: the principle of the "棘轮原则"** —— 每一次失败成为一条永久规则 —— 在两个文章中完全一致，只是本文聚焦在 Skill 层面
- 本文对描述作为路由触发器的观点与 Harness Engineering 中"system prompt 每一行都应能追溯到一次具体失败"完全同源
