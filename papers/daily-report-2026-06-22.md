# 📄 每日论文日报 — 2026-06-22

共筛选出 **20** 篇感兴趣的论文。

---

## 1. Verified Detection and Prevention of Concurrency Anomalies in Multi-Agent Large Language Model Systems

> [2606.17182](https://arxiv.org/abs/2606.17182) | `cs.LG` `cs.DC` `cs.LO` `cs.MA` `cs.PL` | [GitHub](https://github.com/sajjadanwar0/mac-consistency) | [HF讨论](https://huggingface.co/papers/2606.17182)

### 🇨🇳 中文摘要

本文通过形式化方法分析了多智能体大语言模型系统中的并发异常，定义了四种与经典隔离异常结构相似的并发问题，并建立了经过机械验证的一致性层次结构。这是首个针对此类运行时系统进行机器验证的一致性研究。

### 🤖 AI 摘要

Multi-agent LLM systems with shared state are analyzed through formal methods identifying concurrency anomalies and establishing a verified consistency hierarchy with mechanized proofs of soundness and completeness.

### 💡 推荐理由

> 作为Agent开发者，你可能会遇到多Agent共享状态时的并发问题。本文提供了形式化的异常分类和验证方法，能帮助你设计更健壮的Agent协作机制，避免数据不一致和工具调用冲突。

### 📋 原始摘要（节选）

Multi-agent LLM systems share state through memory stores, vector indices, and tool registries. We model such sharing as long-running read-generate-write operations under deterministic-generation semantics -- the regime durable-execution engines enforce by deterministic replay -- and formalize four concurrency anomalies in TLA+: stale-generation, phantom-tool, causal-cascade, and tool-effect reord...


> ⏳ 深度解读尚未完成

---

## 2. Bag of Dims: Training-Free Mechanistic Interpretability via Dimension-Level Sign Patterns

> [2606.12629](https://arxiv.org/abs/2606.12629) | `cs.LG` `cs.AI` | [HF讨论](https://huggingface.co/papers/2606.12629)

### 🇨🇳 中文摘要

本文提出Bag of Dims框架，发现Transformer隐藏状态的标准基向量可作为无需训练的特征表示，每个维度通过符号编码语义、通过幅度编码置信度，无需学习旋转即可解读模型内部状态。

### 🤖 AI 摘要

The standard basis of transformer hidden states serves as a training-free, architecture-general feature representation where individual dimensions encode semantic content through signs and confidence through magnitudes, functioning as independent binary registers without requiring learned rotations or optimization.

### 💡 推荐理由

> 如果你想理解Agent内部推理过程或进行可解释性分析，本文提供了一种轻量级、无需额外训练的方法来解读模型特征，有助于调试Agent行为或优化提示词设计。

### 📋 原始摘要（节选）

We show the standard basis of transformer hidden states already provides a training-free, architecture-general feature basis. Individual dimensions encode semantic content via their signs (+/-1) and confidence via their magnitudes, acting as independent binary registers; a feature is a subset of dimensions with a consistent sign pattern, read by counting sign agreements with no learned rotation. W...

### 🔍 深度解读

- 📖 [解读报告](https://github.com/Jrink525/knowledges/tree/master/papers/bag-of-dims-training-free-mechanistic-interpretability-via-dimension-level-sign-patterns-2606.12629/report.md)
- 📂 [完整目录](https://github.com/Jrink525/knowledges/tree/master/papers/bag-of-dims-training-free-mechanistic-interpretability-via-dimension-level-sign-patterns-2606.12629)
- 🧭 [研究方向](https://github.com/Jrink525/knowledges/tree/master/papers/bag-of-dims-training-free-mechanistic-interpretability-via-dimension-level-sign-patterns-2606.12629/direction_board.json)
- 🔬 [问题重构](https://github.com/Jrink525/knowledges/tree/master/papers/bag-of-dims-training-free-mechanistic-interpretability-via-dimension-level-sign-patterns-2606.12629/research_lens.json)

---

## 3. STARE: Surprisal-Guided Token-Level Advantage Reweighting for Policy Entropy Stability

> [2606.19236](https://arxiv.org/abs/2606.19236) | `cs.LG` `cs.AI` `cs.CL` | [GitHub](https://github.com/hp-luo/STARE) | [HF讨论](https://huggingface.co/papers/2606.19236)

### 🇨🇳 中文摘要

本文分析了GRPO算法中策略熵崩溃的原因，提出STARE方法，通过基于惊奇度的令牌级优势重加权和目标熵调节来稳定强化学习训练过程。

### 🤖 AI 摘要

GRPO algorithms face policy entropy collapse during training, which STARE addresses through surprisal-guided token-level advantage reweighting and target-entropy regulation to maintain stable reinforcement learning for large language models.

### 💡 推荐理由

> 如果你在用强化学习训练Agent的推理能力，熵崩溃是常见问题。STARE提供了一种实用的令牌级调节方法，能帮助你的Agent保持探索多样性，避免过早收敛到次优策略。

### 📋 原始摘要（节选）

Reinforcement Learning with Verifiable Rewards algorithms like GRPO have emerged as the dominant post-training paradigm for complex reasoning in LLMs, yet commonly suffer from policy entropy collapse during training. We conduct a first-order gradient analysis of token-level entropy dynamics under GRPO and identify a token-level credit assignment mismatch: the per-token entropy variation decomposes...

### 🔍 深度解读

- 📖 [解读报告](https://github.com/Jrink525/knowledges/tree/master/papers/stare-surprisal-guided-token-level-advantage-reweighting-for-policy-entropy-stability-2606.19236/report.md)
- 📂 [完整目录](https://github.com/Jrink525/knowledges/tree/master/papers/stare-surprisal-guided-token-level-advantage-reweighting-for-policy-entropy-stability-2606.19236)
- 🧭 [研究方向](https://github.com/Jrink525/knowledges/tree/master/papers/stare-surprisal-guided-token-level-advantage-reweighting-for-policy-entropy-stability-2606.19236/direction_board.json)
- 🔬 [问题重构](https://github.com/Jrink525/knowledges/tree/master/papers/stare-surprisal-guided-token-level-advantage-reweighting-for-policy-entropy-stability-2606.19236/research_lens.json)

---

## 4. Externalizing Research Synthesis and Validation in AI Scientists through a Research Harness

> [2606.18874](https://arxiv.org/abs/2606.18874) | `cs.AI` | [GitHub](https://github.com/OpenDFM/Xcientist) | [HF讨论](https://huggingface.co/papers/2606.18874)

### 🇨🇳 中文摘要

本文提出Xcientist研究框架，将AI科学研究的推理过程外部化为可检查的持久化工件，包括文献证据、想法状态、实验记录等，确保生成机制可追溯、可验证。

### 🤖 AI 摘要

Xcientist enables transparent and accountable AI-driven scientific research by creating persistent artifacts that track the complete research process from problem formulation to mechanism validation and revision.

### 💡 推荐理由

> 如果你在构建自动化研究Agent，本文的“声明漂移”概念和持久化工件设计很有价值。它教你如何让Agent的推理过程透明可审计，避免生成结果与原始目标脱节。

### 📋 原始摘要（节选）

AI systems can increasingly automate scientific workflows, but the reasoning that links prior evidence, generated ideas, experiments and final claims often remains implicit inside model inference. Here we introduce Xcientist, a research harness that externalizes research synthesis and experimental validation into inspectable, contract-governed processes. Xcientist organizes literature evidence, id...


> ⏳ 深度解读尚未完成

---

## 5. LegalHalluLens: Typed Hallucination Auditing and Calibrated Multi-Agent Debate for Trustworthy Legal AI

> [2606.18021](https://arxiv.org/abs/2606.18021) | `cs.AI` `cs.CL` `cs.LG` `cs.MA` | [GitHub](https://github.com/lalitdv9/LegalHallulens) | [HF讨论](https://huggingface.co/papers/2606.18021)

### 🇨🇳 中文摘要

本文提出LegalHalluLens审计框架，对法律AI中的幻觉进行类型化分析（数字、时间、义务、事实四类），并引入风险方向指数和校准的多Agent辩论机制来提升可靠性。

### 🤖 AI 摘要

LegalHalluLens audits AI systems in legal workflows by identifying specific error patterns and directional biases in hallucinations across different claim types, enabling more reliable deployment through targeted diagnostic and mitigation approaches.

### 💡 推荐理由

> 如果你在开发法律或合规领域的Agent，本文的幻觉分类和校准辩论方法能帮你识别和缓解特定类型的错误输出，提升Agent在敏感场景中的可信度。

### 📋 原始摘要（节选）

AI systems deployed in legal workflows hallucinate at rates that aggregate metrics report at ~52%, but this average conceals where errors concentrate and in which direction they run, leaving compliance officers without an actionable signal for trustworthy deployment. We present LegalHalluLens, an auditing framework with three components: typed hallucination profiles across four legally-motivated c...


> ⏳ 深度解读尚未完成

---

## 6. MemSlides: A Hierarchical Memory Driven Agent Framework for Personalized Slide Generation with Multi-turn Local Revision

> [2606.17162](https://arxiv.org/abs/2606.17162) | `cs.CL` `cs.HC` `cs.MA` | [GitHub](https://github.com/huohua325/Memslides) | [HF讨论](https://huggingface.co/papers/2606.17162)

### 🇨🇳 中文摘要

本文提出MemSlides层次化记忆框架，将长期用户画像、工作记忆和工具记忆分离，使个性化演示生成Agent能在多轮修订中稳定保持用户偏好并执行可靠局部编辑。

### 🤖 AI 摘要

MemSlides presents a hierarchical memory framework for personalized presentation agents that separates long-term user profiles, working memory for session constraints, and tool memory for reusable execution experiences to enable stable personalization and reliable local edits across multi-turn revisions.

### 💡 推荐理由

> 如果你在构建需要记忆用户偏好的Agent（如个性化助手），本文的层次化记忆设计很实用。它解决了多轮交互中偏好漂移和局部编辑失败的问题，可直接借鉴到你的Agent架构中。

### 📋 原始摘要（节选）

Personalized presentation generation requires more than conditioning on a current prompt or template: agents must preserve stable user preferences across tasks, retain newly introduced preferences and constraints during multi-turn revision, and carry out local edits reliably. We propose MemSlides, a hierarchical memory framework for personalized presentation agents that separates long-term memory ...


> ⏳ 深度解读尚未完成

---

## 7. Re-Centering Humans in LLM Personalization

> [2606.06614](https://arxiv.org/abs/2606.06614) | `cs.CL` `cs.AI` `cs.HC` | [GitHub](https://github.com/orange0629/recenter-personalization) | [HF讨论](https://huggingface.co/papers/2606.06614)

### 🇨🇳 中文摘要

本文通过收集真实人类对话和判断，揭示了LLM个性化在合成数据与真实数据之间的性能差距，发现模型在提取用户属性、匹配相关属性和生成个性化回复方面存在显著不足。

### 🤖 AI 摘要

Human-centered evaluation reveals significant gaps between synthetic and real-world LLM personalization performance, with models struggling to extract user attributes and generate truly personalized responses that match human quality judgments.

### 💡 推荐理由

> 如果你在开发个性化Agent，本文提醒你注意合成数据评估的局限性。它提供了真实人类评估的方法论，能帮你更准确地衡量Agent的个性化效果，避免过度乐观。

### 📋 原始摘要（节选）

Despite growing interest, most evaluations of large language models' (LLMs') personalization abilities have relied on synthetic data. It remains unclear how well current personalization systems work for real users. In this paper, we study the gap in LLM personalization performance when using synthetic versus human data. We collect human conversations (550 conversations) and judgments across three ...

### 🔍 深度解读

- 📖 [解读报告](https://github.com/Jrink525/knowledges/tree/master/papers/re-centering-humans-in-llm-personalization-2606.06614/report.md)
- 📂 [完整目录](https://github.com/Jrink525/knowledges/tree/master/papers/re-centering-humans-in-llm-personalization-2606.06614)
- 🧭 [研究方向](https://github.com/Jrink525/knowledges/tree/master/papers/re-centering-humans-in-llm-personalization-2606.06614/direction_board.json)
- 🔬 [问题重构](https://github.com/Jrink525/knowledges/tree/master/papers/re-centering-humans-in-llm-personalization-2606.06614/research_lens.json)

---

## 8. CEO-Bench: Can Agents Play the Long Game?

> [2606.18543](https://arxiv.org/abs/2606.18543) | `cs.AI` `cs.CL` `cs.SE` | [GitHub](https://github.com/zlab-princeton/ceobench-src) | [HF讨论](https://huggingface.co/papers/2606.18543)

### 🇨🇳 中文摘要

本文提出CEO-Bench基准，通过模拟经营初创公司500天的任务，评估Agent在长期规划、噪声环境信息获取、适应变化和多任务协调方面的综合能力。

### 🤖 AI 摘要

CEO-Bench evaluates language model agents' ability to manage a simulated startup over 500 days, testing their proficiency in long-term planning, noise handling, adaptability, and multi-task coordination through a Python interface.

### 💡 推荐理由

> 如果你想测试Agent在复杂长期任务中的表现，CEO-Bench提供了一个逼真的模拟环境。它特别适合评估你的Agent在不确定性和多目标下的决策能力，而不仅仅是单步任务。

### 📋 原始摘要（节选）

Language model agents are becoming proficient executors at isolated, short-horizon tasks such as software engineering and customer service. Yet real-world challenges require a combination of sophisticated skills that remain largely untested in agents: (1) navigating long horizons amid uncertainty; (2) acquiring information in noisy environments; (3) adapting to a changing world; (4) orchestrating ...


> ⏳ 深度解读尚未完成

---

## 9. REVES: REvision and VErification--Augmented Training for Test-Time Scaling

> [2606.18910](https://arxiv.org/abs/2606.18910) | `cs.LG` `cs.CL` | [GitHub](https://github.com/yxliu02/REVES) | [HF讨论](https://huggingface.co/papers/2606.18910)

### 🇨🇳 中文摘要

本文提出REVES两阶段迭代框架，通过将中间步骤的“接近正确”答案转化为解耦的修订数据，交替进行数据增强和策略优化，显著提升LLM在编码和约束满足问题上的推理能力。

### 🤖 AI 摘要

A two-stage iterative framework alternates between data augmentation and policy optimization to improve LLM reasoning by leveraging intermediate correction steps, achieving superior performance on coding benchmarks and constraint satisfaction problems.

### 💡 推荐理由

> 如果你在优化Agent的推理能力，本文的“接近正确”答案利用策略很有启发性。它教你如何从失败轨迹中提取学习信号，通过迭代训练提升Agent的自我修正能力。

### 📋 原始摘要（节选）

Test-time scaling via sequential revision has emerged as a powerful paradigm for enhancing Large Language Model (LLM) reasoning. However, standard post-training methods primarily optimize single-shot objectives, creating a fundamental misalignment with multi-step inference dynamics. While recent work treats this as multi-turn reinforcement learning (RL), conventional approaches optimize over the m...


> ⏳ 深度解读尚未完成

---

## 10. Rethinking the Role of Efficient Attention in Hybrid Architectures

> [2606.15378](https://arxiv.org/abs/2606.15378) | `cs.CL` `cs.LG` | [GitHub](https://github.com/thunlp/rethinking-hybrid-attention) | [HF讨论](https://huggingface.co/papers/2606.15378)

### 🇨🇳 中文摘要

本文系统分析了混合架构中高效注意力模块（如滑动窗口注意力）的作用，发现它们主要影响长上下文能力的涌现速度而非最终性能，且长距离检索主要由全注意力承担。

### 🤖 AI 摘要

Hybrid architectures combining full attention with efficient attention modules like sliding-window attention exhibit distinct scaling behaviors and optimization trajectories, with efficient attention primarily affecting the emergence speed of long-context capabilities rather than final performance.

### 💡 推荐理由

> 如果你在Agent中处理长上下文（如多轮对话、长文档），本文能帮你理解不同注意力机制的权衡。它指导你如何设计混合架构，在效率和长程依赖之间取得平衡。

### 📋 原始摘要（节选）

Modern language models increasingly adopt hybrid architectures that combine full attention with efficient attention modules, such as sliding-window attention (SWA) and recurrent sequence mixers. However, how these efficient modules shape model capabilities remains poorly understood. To address this gap, we conduct a systematic analysis across hybrid architectures from three perspectives: scaling b...


> ⏳ 深度解读尚未完成

---

## 11. SAE Interventions are Unreliable: Post-Intervention Recovery of Suppressed Behavior

> [2606.18322](https://arxiv.org/abs/2606.18322) | `cs.LG` `cs.AI` | [GitHub](https://github.com/Mingyuee88/sae-post-intervention-recovery) | [HF讨论](https://huggingface.co/papers/2606.18322)

### 🇨🇳 中文摘要

本文揭示稀疏自编码器（SAE）的特征级干预存在可恢复性漏洞：即使成功抑制了某个有害特征，模型仍可通过残差空间优化恢复原始行为，表明SAE干预并非完全可靠。

### 🤖 AI 摘要

Sparse Autoencoders' feature-level interventions may appear successful but can be circumvented through residual-space optimization that recovers original behaviors, revealing limitations in using SAE features for complete behavioral control.

### 💡 推荐理由

> 如果你在用SAE做Agent安全控制或行为干预，本文是一个重要警示。它提醒你单一特征抑制可能不够，需要更全面的安全机制来防止行为恢复。

### 📋 原始摘要（节选）

Sparse Autoencoders (SAEs) decompose residual-stream activations into interpretable features. Recent latent-space defenses increasingly rely on these decompositions, assuming that identified "unsafe" SAE features serve as actionable handles for monitoring and intervention. In this paradigm, clamping a specific harmful feature is expected to reliably prevent model misbehavior. However, we show that...


> ⏳ 深度解读尚未完成

---

## 12. LedgerAgent: Structured State for Policy-Adherent Tool-Calling Agents

> [2606.20529](https://arxiv.org/abs/2606.20529) | `cs.AI` `cs.CL` | [HF讨论](https://huggingface.co/papers/2606.20529)

### 🇨🇳 中文摘要

本文提出LEDGERAGENT方法，将客服Agent的任务状态显式维护在独立账本中，避免隐式状态管理导致的过时信息或策略违规问题，提升工具调用的策略合规性。

### 🤖 AI 摘要

LEDGERAGENT is a method for customer service agents that maintains task states in a separate ledger to improve policy adherence and state management during tool calling.

### 💡 推荐理由

> 如果你在开发需要严格策略合规的Agent（如客服、金融），本文的显式状态管理方案很实用。它解决了Agent因隐式状态导致的信息错误和策略违规问题，可直接应用于你的系统。

### 📋 原始摘要（节选）

Policy-adherent tool-calling agents in customer-service domains must maintain task states across turns while calling tools and obeying domain policies. Task states consist of relevant facts, identifiers, constraints, and conditions observed through user interaction and tool calls. In standard agents, task states are not represented separately. Observations, tool returns, and policy instructions ar...


> ⏳ 深度解读尚未完成

---

## 13. No Resource, No Benchmarks, No Problem? Evaluating and Improving LLMs for Code Generation in No-Resource Languages

> [2606.16827](https://arxiv.org/abs/2606.16827) | `cs.SE` | [GitHub](https://github.com/Devy99/no-resource-pl-study) | [HF讨论](https://huggingface.co/papers/2606.16827)

### 🇨🇳 中文摘要

本文研究了无资源编程语言的代码生成问题，通过构建基准并提出结合预训练和权重差异迁移的方法，以较低计算成本创建了专门的指令跟随模型。

### 🤖 AI 摘要

Research addresses code generation challenges for no-resource programming languages by developing benchmarks and proposing a method that combines further pre-training with weight difference transfer to create specialized instruction-following models at reduced computational cost.

### 💡 推荐理由

> 如果你需要Agent支持自定义或领域特定语言，本文的方法很有价值。它展示了如何在缺乏训练数据的情况下，通过迁移学习让Agent掌握新语言，扩展了Agent的编程能力边界。

### 📋 原始摘要（节选）

Large Language Models (LLMs) have significantly advanced the automation of software engineering tasks. One prominent example is code generation, where an LLM produces code in a specified programming language based on a natural language description. Most research in this area has focused on high-resource languages, such as Python or Java, which benefit from abundant training data. A smaller body of...

### 🔍 深度解读

- 📖 [解读报告](https://github.com/Jrink525/knowledges/tree/master/papers/no-resource-no-benchmarks-no-problem-evaluating-and-improving-llms-for-code-generation-in-no-resource-languages-2606.16827/report.md)
- 📂 [完整目录](https://github.com/Jrink525/knowledges/tree/master/papers/no-resource-no-benchmarks-no-problem-evaluating-and-improving-llms-for-code-generation-in-no-resource-languages-2606.16827)
- 🧭 [研究方向](https://github.com/Jrink525/knowledges/tree/master/papers/no-resource-no-benchmarks-no-problem-evaluating-and-improving-llms-for-code-generation-in-no-resource-languages-2606.16827/direction_board.json)
- 🔬 [问题重构](https://github.com/Jrink525/knowledges/tree/master/papers/no-resource-no-benchmarks-no-problem-evaluating-and-improving-llms-for-code-generation-in-no-resource-languages-2606.16827/research_lens.json)

---

## 14. Selective Synergistic Learning for Video Object-Centric Learning

> [2606.15527](https://arxiv.org/abs/2606.15527) | `cs.CV` `cs.AI` | [GitHub](https://github.com/wjun0830/SSync) | [HF讨论](https://huggingface.co/papers/2606.15527)

### 🇨🇳 中文摘要

本文提出选择性协同学习（SSync），通过伪标签和传递合并策略选择性蒸馏可靠线索，解决了视频对象中心学习中密集对齐策略的计算开销和噪声传播问题。

### 🤖 AI 摘要

Selective Synergistic Learning (SSync) addresses limitations in video object-centric learning by selectively distilling reliable cues through pseudo-labeling and transitive merging to improve object decomposition quality and robustness.

### 💡 推荐理由

> 虽然本文聚焦视频领域，但其选择性蒸馏思想可迁移到Agent的多模态感知中。如果你在处理视觉Agent的对象识别或场景理解，本文的方法能提升鲁棒性并降低计算成本。

### 📋 原始摘要（节选）

Typical video object-centric learning (VOCL) approaches employ slot-based frameworks that rely on reconstruction-driven encoder-decoder architectures, where learning is mediated by two spatial maps: attention maps from the encoder and object maps from the decoder. As these two distinct maps exhibit different properties, a recent dense alignment strategy attempted to reconcile this discrepancy by e...


> ⏳ 深度解读尚未完成

---

## 15. Think Again or Think Longer? Selective Verification for Budget-Aware Reasoning

> [2606.19808](https://arxiv.org/abs/2606.19808) | `cs.AI` `cs.CL` | [GitHub](https://github.com/Sajib-006/SEVRA) | [HF讨论](https://huggingface.co/papers/2606.19808)

### 🇨🇳 中文摘要

本文提出选择性验证框架SEVRA，通过动态决定何时需要验证答案，在保持高准确率的同时减少后生成令牌数，比始终验证或自一致性方法更高效。

### 🤖 AI 摘要

Selective verification approaches optimize test-time reasoning by dynamically deciding when to verify answers, achieving better accuracy and efficiency compared to always-verifying or self-consistency methods.

### 💡 推荐理由

> 如果你在优化Agent的推理效率，本文的预算感知验证策略很实用。它教你如何根据推理状态动态分配计算资源，避免在已正确的答案上浪费算力，提升响应速度。

### 📋 原始摘要（节选）

Test-time reasoning is increasingly used as a serving-time control knob, but extra reasoning is not uniformly valuable: it can repair failed attempts, waste compute on already-correct answers, or introduce harmful answer changes. We study this as a deployment allocation problem rather than a new-verifier problem. We introduce \sevra, Selective Verification for Reasoning Allocation, a serving-layer...


> ⏳ 深度解读尚未完成

---

## 16. When Does Trajectory-Level Supervision Permit Efficient Offline Reinforcement Learning?

> [2606.18531](https://arxiv.org/abs/2606.18531) | `stat.ML` `cs.LG` | [HF讨论](https://huggingface.co/papers/2606.18531)

### 🇨🇳 中文摘要

本文发展了离线强化学习在轨迹级结果监督下的统计理论，提出悲观演员-评论家算法OPAC，并刻画了从过程级到轨迹级监督的统计代价。

### 🤖 AI 摘要

Offline reinforcement learning with trajectory-level outcome supervision presents statistical challenges that can be addressed through pessimistic actor-critic methods, though fundamental barriers exist for certain generalized outcome-based problems.

### 💡 推荐理由

> 如果你在Agent训练中只有轨迹级反馈（如任务成功/失败），本文的理论和算法能帮你设计更高效的离线学习策略。它解释了为什么轨迹级监督更难，并提供了解决方案。

### 📋 原始摘要（节选）

Offline reinforcement learning is typically analyzed under process-level reward supervision, yet many sequential decision datasets
  record only trajectory-level outcomes. We develop a statistical theory for offline policy optimization from such outcome-level
  supervision. We first study the canonical setting where the target remains the expected cumulative reward, but each offline trajectory
  p...


> ⏳ 深度解读尚未完成

---

## 17. MyPCBench: A Benchmark for Personally Intelligent Computer-Use Agents

> [2606.16748](https://arxiv.org/abs/2606.16748) | `cs.LG` `cs.CL` | [GitHub](https://github.com/ljang0/MyPCBench) | [HF讨论](https://huggingface.co/papers/2606.16748)

### 🇨🇳 中文摘要

本文提出MyPCBench基准，在模拟Linux桌面环境中测试Agent作为个人助手的能力，包含17个真实Web应用和184个任务，发现当前最佳模型完成率仅55.4%。

### 🤖 AI 摘要

MyPCBench evaluates computer-use agents as personal assistants in a simulated Linux desktop environment with real-world web applications, revealing that Claude Opus 4.6 achieves the highest task completion rate of 55.4% while struggles with multi-application tasks and long trajectories.

### 💡 推荐理由

> 如果你想评估Agent在真实个人助手场景中的表现，MyPCBench提供了贴近实际的测试环境。它特别适合测试Agent的多应用协作和长轨迹任务能力，帮你发现系统瓶颈。

### 📋 原始摘要（节选）

Current benchmarks for computer-use agents evaluate models in impersonal environments. This leaves a gap between evaluation and deployment where personal assistants are expected to work across a user's whole digital life, including their context, historical data, and logged-in accounts. This gap is widest on web tasks, where live web evaluations cannot exercise sites that require logging in or per...


> ⏳ 深度解读尚未完成

---

## 18. EfficientRollout: System-Aware Self-Speculative Decoding for RL Rollouts

> [2606.18967](https://arxiv.org/abs/2606.18967) | `cs.LG` | [GitHub](https://github.com/furiosa-ai/EfficientRollout) | [HF讨论](https://huggingface.co/papers/2606.18967)

### 🇨🇳 中文摘要

本文提出EfficientRollout框架，通过系统感知的自推测解码加速强化学习中的轨迹生成，解决了策略演化导致的草稿模型不匹配和长尾生成延迟问题。

### 🤖 AI 摘要

EfficientRollout is a system-aware self-speculative decoding framework that accelerates reinforcement learning rollouts by adapting drafters to evolving policies and optimizing speculative decoding regimes.

### 💡 推荐理由

> 如果你在训练Agent时遇到推理速度瓶颈，本文的加速方法很实用。它针对RL训练中策略不断变化的特点，提供了自适应推测解码方案，能显著减少训练时间。

### 📋 原始摘要（节选）

Reinforcement learning (RL) has become a representative post-training paradigm for LLMs, enabling strong reasoning and agentic capabilities. However, rollout generation remains a dominant latency bottleneck because autoregressive sampling decodes responses sequentially and a small number of long-tailed generations often determine completion time. Speculative decoding (SD) offers a natural way to a...


> ⏳ 深度解读尚未完成

---

## 19. Kairos: A Native World Model Stack for Physical AI

> [2606.16533](https://arxiv.org/abs/2606.16533) | `cs.AI` `cs.CV` | [GitHub](https://github.com/kairos-agi/kairos-sensenova) | [HF讨论](https://huggingface.co/papers/2606.16533)

### 🇨🇳 中文摘要

本文提出Kairos世界模型栈，通过跨实体数据课程、混合线性时间注意力和硬件感知部署设计，使世界模型能原生学习、维护和高效执行物理AI任务。

### 🤖 AI 摘要

Kairos is a world model framework that learns from diverse experiences, maintains persistent states through hybrid temporal attention mechanisms, and operates efficiently across different hardware platforms for physical AI applications.

### 💡 推荐理由

> 如果你在开发物理世界交互的Agent（如机器人、自动驾驶），Kairos提供了完整的世界模型框架。它的跨实体学习和高效部署设计能帮你构建更强大的环境感知Agent。

### 📋 原始摘要（节选）

World models are transitioning from passive visual generators to foundational, operational infrastructure for Physical AI: they must natively acquire world knowledge from heterogeneous experience, maintain persistent states over long horizons, and execute efficiently within real deployment constraints. We introduce Kairos, a native world model stack designed around these requirements. (1) Kairos l...


> ⏳ 深度解读尚未完成

---

## 20. RepSelect: Robust LLM Unlearning via Representation Selectivity

> [2606.17168](https://arxiv.org/abs/2606.17168) | `cs.CL` | [GitHub](https://github.com/filyp/RepSelect) | [HF讨论](https://huggingface.co/papers/2606.17168)

### 🇨🇳 中文摘要

本文提出RepSelect方法，通过折叠权重梯度的主成分来隔离遗忘集特定表示，实现比现有方法更深层、更鲁棒的LLM遗忘，且不易被微调或少样本提示恢复。

### 🤖 AI 摘要

RepSelect isolates forget-set-specific representations in LLMs by collapsing top principal components of weight gradients, achieving deeper and more robust unlearning compared to existing methods.

### 💡 推荐理由

> 如果你需要Agent遗忘特定知识（如隐私数据、有害内容），本文的方法更可靠。它解决了现有遗忘方法容易被逆向恢复的问题，能帮你构建更安全的Agent系统。

### 📋 原始摘要（节选）

Making large language models (LLMs) deeply forget specific knowledge and values without sacrificing general capabilities remains a central challenge in unlearning. However, current methods are easily reversed by fine-tuning or few-shot prompting, suggesting their forgetting is only shallow. We identify the root cause. Existing methods target representations shared with both the retain set and the ...


> ⏳ 深度解读尚未完成

---


> 报告生成时间: 2026-06-22 | 数据来源: Hugging Face Daily Papers + arXiv