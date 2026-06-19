# 📄 每日论文日报 — 2026-06-19

共筛选出 **10** 篇感兴趣的论文。

---

## 1. Bag of Dims: Training-Free Mechanistic Interpretability via Dimension-Level Sign Patterns

> [2606.12629](https://arxiv.org/abs/2606.12629) | `cs.LG` `cs.AI` | [HF讨论](https://huggingface.co/papers/2606.12629)

### 🇨🇳 中文摘要

本文提出了一种无需训练的机制可解释性方法，通过分析Transformer隐藏状态中每个维度的符号（+/-1）和幅度来编码语义内容和置信度，验证了该方法在语言、视觉和音频模型上的有效性。

### 🤖 AI 摘要

The standard basis of transformer hidden states serves as a training-free, architecture-general feature representation where individual dimensions encode semantic content through signs and confidence through magnitudes, functioning as independent binary registers without requiring learned rotations or optimization.

### 💡 推荐理由

> 作为Agent开发者，理解模型内部表示机制有助于调试和优化Agent行为，这篇论文提供了一种轻量级工具来解读模型决策，无需额外训练即可应用。

### 📋 原始摘要（节选）

We show the standard basis of transformer hidden states already provides a training-free, architecture-general feature basis. Individual dimensions encode semantic content via their signs (+/-1) and confidence via their magnitudes, acting as independent binary registers; a feature is a subset of dimensions with a consistent sign pattern, read by counting sign agreements with no learned rotation. W...

### 🔍 深度解读

- 📖 [解读报告](https://github.com/Jrink525/knowledges/tree/master/papers/bag-of-dims-training-free-mechanistic-interpretability-via-dimension-level-sign-patterns-2606.12629/report.md)
- 📂 [完整目录](https://github.com/Jrink525/knowledges/tree/master/papers/bag-of-dims-training-free-mechanistic-interpretability-via-dimension-level-sign-patterns-2606.12629)
- 🧭 [研究方向](https://github.com/Jrink525/knowledges/tree/master/papers/bag-of-dims-training-free-mechanistic-interpretability-via-dimension-level-sign-patterns-2606.12629/direction_board.json)
- 🔬 [问题重构](https://github.com/Jrink525/knowledges/tree/master/papers/bag-of-dims-training-free-mechanistic-interpretability-via-dimension-level-sign-patterns-2606.12629/research_lens.json)

---

## 2. STARE: Surprisal-Guided Token-Level Advantage Reweighting for Policy Entropy Stability

> [2606.19236](https://arxiv.org/abs/2606.19236) | `cs.LG` `cs.AI` `cs.CL` | [GitHub](https://github.com/hp-luo/STARE) | [HF讨论](https://huggingface.co/papers/2606.19236)

### 🇨🇳 中文摘要

针对GRPO算法在训练中策略熵崩溃的问题，提出STARE方法，通过基于惊讶度的令牌级优势重加权和目标熵调节，稳定强化学习训练过程。

### 🤖 AI 摘要

GRPO algorithms face policy entropy collapse during training, which STARE addresses through surprisal-guided token-level advantage reweighting and target-entropy regulation to maintain stable reinforcement learning for large language models.

### 💡 推荐理由

> 如果你在用强化学习训练Agent的推理能力，熵崩溃是常见痛点，STARE提供了一种实用的令牌级优化策略，能直接提升训练稳定性和模型性能。

### 📋 原始摘要（节选）

Reinforcement Learning with Verifiable Rewards algorithms like GRPO have emerged as the dominant post-training paradigm for complex reasoning in LLMs, yet commonly suffer from policy entropy collapse during training. We conduct a first-order gradient analysis of token-level entropy dynamics under GRPO and identify a token-level credit assignment mismatch: the per-token entropy variation decomposes...

> ⚠️ 深度解读产出不完整：缺失 direction_board.json

### 🔍 深度解读

- 📖 [解读报告](https://github.com/Jrink525/knowledges/tree/master/papers/stare-surprisal-guided-token-level-advantage-reweighting-for-policy-entropy-stability-2606.19236/report.md)
- 📂 [完整目录](https://github.com/Jrink525/knowledges/tree/master/papers/stare-surprisal-guided-token-level-advantage-reweighting-for-policy-entropy-stability-2606.19236)
- 🔬 [问题重构](https://github.com/Jrink525/knowledges/tree/master/papers/stare-surprisal-guided-token-level-advantage-reweighting-for-policy-entropy-stability-2606.19236/research_lens.json)

---

## 3. Re-Centering Humans in LLM Personalization

> [2606.06614](https://arxiv.org/abs/2606.06614) | `cs.CL` `cs.AI` `cs.HC` | [GitHub](https://github.com/orange0629/recenter-personalization) | [HF讨论](https://huggingface.co/papers/2606.06614)

### 🇨🇳 中文摘要

通过收集真实人类对话和判断，揭示了LLM在个性化任务中合成数据与真实数据之间的性能差距，模型在提取用户属性和生成个性化回复方面存在显著不足。

### 🤖 AI 摘要

Human-centered evaluation reveals significant gaps between synthetic and real-world LLM personalization performance, with models struggling to extract user attributes and generate truly personalized responses that match human quality judgments.

### 💡 推荐理由

> 构建个性化Agent时，依赖合成数据可能高估系统能力，这篇论文提醒你关注真实用户交互中的瓶颈，对设计更可靠的Agent个性化模块有直接指导意义。

### 📋 原始摘要（节选）

Despite growing interest, most evaluations of large language models' (LLMs') personalization abilities have relied on synthetic data. It remains unclear how well current personalization systems work for real users. In this paper, we study the gap in LLM personalization performance when using synthetic versus human data. We collect human conversations (550 conversations) and judgments across three ...

### 🔍 深度解读

- 📖 [解读报告](https://github.com/Jrink525/knowledges/tree/master/papers/re-centering-humans-in-llm-personalization-2606.06614/report.md)
- 📂 [完整目录](https://github.com/Jrink525/knowledges/tree/master/papers/re-centering-humans-in-llm-personalization-2606.06614)
- 🧭 [研究方向](https://github.com/Jrink525/knowledges/tree/master/papers/re-centering-humans-in-llm-personalization-2606.06614/direction_board.json)
- 🔬 [问题重构](https://github.com/Jrink525/knowledges/tree/master/papers/re-centering-humans-in-llm-personalization-2606.06614/research_lens.json)

---

## 4. REVES: REvision and VErification--Augmented Training for Test-Time Scaling

> [2606.18910](https://arxiv.org/abs/2606.18910) | `cs.LG` `cs.CL` | [GitHub](https://github.com/yxliu02/REVES) | [HF讨论](https://huggingface.co/papers/2606.18910)

### 🇨🇳 中文摘要

提出REVES两阶段迭代框架，通过将中间步骤的“接近正确”答案转化为独立的修正任务，结合数据增强和策略优化，显著提升LLM在编码和约束满足问题上的推理能力。

### 🤖 AI 摘要

A two-stage iterative framework alternates between data augmentation and policy optimization to improve LLM reasoning by leveraging intermediate correction steps, achieving superior performance on coding benchmarks and constraint satisfaction problems.

### 💡 推荐理由

> Agent在复杂任务中常需要多步推理和修正，REVES的中间步骤利用策略能直接应用于提升Agent的自我纠错能力，尤其适合编码和规划类场景。

### 📋 原始摘要（节选）

Test-time scaling via sequential revision has emerged as a powerful paradigm for enhancing Large Language Model (LLM) reasoning. However, standard post-training methods primarily optimize single-shot objectives, creating a fundamental misalignment with multi-step inference dynamics. While recent work treats this as multi-turn reinforcement learning (RL), conventional approaches optimize over the m...


> ⏳ 深度解读尚未完成

---

## 5. No Resource, No Benchmarks, No Problem? Evaluating and Improving LLMs for Code Generation in No-Resource Languages

> [2606.16827](https://arxiv.org/abs/2606.16827) | `cs.SE` | [GitHub](https://github.com/Devy99/no-resource-pl-study) | [HF讨论](https://huggingface.co/papers/2606.16827)

### 🇨🇳 中文摘要

研究无资源编程语言的代码生成问题，通过构建基准并采用预训练与权重差异迁移相结合的方法，以较低计算成本创建专用指令微调模型。

### 🤖 AI 摘要

Research addresses code generation challenges for no-resource programming languages by developing benchmarks and proposing a method that combines further pre-training with weight difference transfer to create specialized instruction-following models at reduced computational cost.

### 💡 推荐理由

> 如果你需要Agent支持内部或领域特定语言，这篇论文提供了从零构建代码生成能力的实用方案，对扩展Agent的编程能力边界很有价值。

### 📋 原始摘要（节选）

Large Language Models (LLMs) have significantly advanced the automation of software engineering tasks. One prominent example is code generation, where an LLM produces code in a specified programming language based on a natural language description. Most research in this area has focused on high-resource languages, such as Python or Java, which benefit from abundant training data. A smaller body of...


> ⏳ 深度解读尚未完成

---

## 6. Selective Synergistic Learning for Video Object-Centric Learning

> [2606.15527](https://arxiv.org/abs/2606.15527) | `cs.CV` `cs.AI` | [GitHub](https://github.com/wjun0830/SSync) | [HF讨论](https://huggingface.co/papers/2606.15527)

### 🇨🇳 中文摘要

提出选择性协同学习方法SSync，通过伪标签和传递合并策略选择性蒸馏可靠线索，改善视频对象中心学习中的对象分解质量和鲁棒性。

### 🤖 AI 摘要

Selective Synergistic Learning (SSync) addresses limitations in video object-centric learning by selectively distilling reliable cues through pseudo-labeling and transitive merging to improve object decomposition quality and robustness.

### 💡 推荐理由

> 虽然聚焦视频领域，但选择性蒸馏思想可迁移到Agent的多模态感知模块，帮助Agent更鲁棒地分解和理解复杂场景中的对象。

### 📋 原始摘要（节选）

Typical video object-centric learning (VOCL) approaches employ slot-based frameworks that rely on reconstruction-driven encoder-decoder architectures, where learning is mediated by two spatial maps: attention maps from the encoder and object maps from the decoder. As these two distinct maps exhibit different properties, a recent dense alignment strategy attempted to reconcile this discrepancy by e...


> ⏳ 深度解读尚未完成

---

## 7. Think Again or Think Longer? Selective Verification for Budget-Aware Reasoning

> [2606.19808](https://arxiv.org/abs/2606.19808) | `cs.AI` `cs.CL` | [GitHub](https://github.com/Sajib-006/SEVRA) | [HF讨论](https://huggingface.co/papers/2606.19808)

### 🇨🇳 中文摘要

提出选择性验证框架SEVRA，通过动态决定何时验证答案，在保持或提升准确率的同时显著减少计算开销，优于始终验证或自一致性方法。

### 🤖 AI 摘要

Selective verification approaches optimize test-time reasoning by dynamically deciding when to verify answers, achieving better accuracy and efficiency compared to always-verifying or self-consistency methods.

### 💡 推荐理由

> Agent在实时场景中需要平衡推理深度和响应速度，SEVRA的预算感知验证策略能帮你优化Agent的计算资源分配，提升效率而不牺牲质量。

### 📋 原始摘要（节选）

Test-time reasoning is increasingly used as a serving-time control knob, but extra reasoning is not uniformly valuable: it can repair failed attempts, waste compute on already-correct answers, or introduce harmful answer changes. We study this as a deployment allocation problem rather than a new-verifier problem. We introduce \sevra, Selective Verification for Reasoning Allocation, a serving-layer...


> ⏳ 深度解读尚未完成

---

## 8. When Does Trajectory-Level Supervision Permit Efficient Offline Reinforcement Learning?

> [2606.18531](https://arxiv.org/abs/2606.18531) | `stat.ML` `cs.LG` | [HF讨论](https://huggingface.co/papers/2606.18531)

### 🇨🇳 中文摘要

针对仅提供轨迹级结果的离线强化学习问题，提出悲观演员-评论家算法OPAC，并给出统计保证和匹配的下界，揭示了过程级监督缺失的代价。

### 🤖 AI 摘要

Offline reinforcement learning with trajectory-level outcome supervision presents statistical challenges that can be addressed through pessimistic actor-critic methods, though fundamental barriers exist for certain generalized outcome-based problems.

### 💡 推荐理由

> 如果你的Agent训练数据只有最终结果而无中间奖励，这篇论文的理论分析和算法能指导你如何有效利用这类数据，对实际部署中的离线学习场景很有帮助。

### 📋 原始摘要（节选）

Offline reinforcement learning is typically analyzed under process-level reward supervision, yet many sequential decision datasets
  record only trajectory-level outcomes. We develop a statistical theory for offline policy optimization from such outcome-level
  supervision. We first study the canonical setting where the target remains the expected cumulative reward, but each offline trajectory
  p...


> ⏳ 深度解读尚未完成

---

## 9. MyPCBench: A Benchmark for Personally Intelligent Computer-Use Agents

> [2606.16748](https://arxiv.org/abs/2606.16748) | `cs.LG` `cs.CL` | [GitHub](https://github.com/ljang0/MyPCBench) | [HF讨论](https://huggingface.co/papers/2606.16748)

### 🇨🇳 中文摘要

提出MyPCBench基准，在模拟Linux桌面环境中评估计算机使用Agent作为个人助理的能力，发现当前最佳模型在多应用和长轨迹任务上仍有显著局限。

### 🤖 AI 摘要

MyPCBench evaluates computer-use agents as personal assistants in a simulated Linux desktop environment with real-world web applications, revealing that Claude Opus 4.6 achieves the highest task completion rate of 55.4% while struggles with multi-application tasks and long trajectories.

### 💡 推荐理由

> 作为Agent开发者，这个基准直接测试了Agent在真实桌面环境中的表现，揭示了多步骤、多应用协同的挑战，对设计更实用的个人助理Agent有重要参考价值。

### 📋 原始摘要（节选）

Current benchmarks for computer-use agents evaluate models in impersonal environments. This leaves a gap between evaluation and deployment where personal assistants are expected to work across a user's whole digital life, including their context, historical data, and logged-in accounts. This gap is widest on web tasks, where live web evaluations cannot exercise sites that require logging in or per...


> ⏳ 深度解读尚未完成

---

## 10. EfficientRollout: System-Aware Self-Speculative Decoding for RL Rollouts

> [2606.18967](https://arxiv.org/abs/2606.18967) | `cs.LG` | [GitHub](https://github.com/furiosa-ai/EfficientRollout) | [HF讨论](https://huggingface.co/papers/2606.18967)

### 🇨🇳 中文摘要

提出EfficientRollout框架，通过系统感知的自推测解码加速强化学习中的rollout生成，自适应调整草稿模型以匹配不断演化的策略。

### 🤖 AI 摘要

EfficientRollout is a system-aware self-speculative decoding framework that accelerates reinforcement learning rollouts by adapting drafters to evolving policies and optimizing speculative decoding regimes.

### 💡 推荐理由

> RL训练Agent时，rollout生成是主要瓶颈，EfficientRollout的加速方案能显著缩短训练周期，尤其适合需要大量交互的Agent场景。

### 📋 原始摘要（节选）

Reinforcement learning (RL) has become a representative post-training paradigm for LLMs, enabling strong reasoning and agentic capabilities. However, rollout generation remains a dominant latency bottleneck because autoregressive sampling decodes responses sequentially and a small number of long-tailed generations often determine completion time. Speculative decoding (SD) offers a natural way to a...


> ⏳ 深度解读尚未完成

---


> 报告生成时间: 2026-06-19 | 数据来源: Hugging Face Daily Papers + arXiv