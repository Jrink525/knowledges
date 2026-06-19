# 📄 每日论文日报 — 2026-06-19

共筛选出 **10** 篇感兴趣的论文。

---

## 1. Bag of Dims: Training-Free Mechanistic Interpretability via Dimension-Level Sign Patterns

> [2606.12629](https://arxiv.org/abs/2606.12629) | `cs.LG` `cs.AI` | [HF讨论](https://huggingface.co/papers/2606.12629)

### 🇨🇳 中文摘要

本文发现Transformer隐藏状态的标准基可以直接作为无需训练的特征表示，每个维度通过符号编码语义、通过幅度编码置信度，形成独立的二进制寄存器。该框架在语言、视觉和音频等多个模型上验证了有效性，仅靠符号模式就能保留60-93%的预测准确率。

### 🤖 AI 摘要

The standard basis of transformer hidden states serves as a training-free, architecture-general feature representation where individual dimensions encode semantic content through signs and confidence through magnitudes, functioning as independent binary registers without requiring learned rotations or optimization.

### 💡 推荐理由

> 作为Agent开发者，理解Transformer内部表示机制有助于调试和优化Agent的推理过程。本文提出的无需训练的解释方法可以直接应用于你开发的Agent模型，帮助分析模型在决策时依赖哪些特征维度，提升Agent行为的可解释性。

### 📋 原始摘要（节选）

We show the standard basis of transformer hidden states already provides a training-free, architecture-general feature basis. Individual dimensions encode semantic content via their signs (+/-1) and confidence via their magnitudes, acting as independent binary registers; a feature is a subset of dimensions with a consistent sign pattern, read by counting sign agreements with no learned rotation. W...


> ⏳ 深度解读尚未完成

---

## 2. STARE: Surprisal-Guided Token-Level Advantage Reweighting for Policy Entropy Stability

> [2606.19236](https://arxiv.org/abs/2606.19236) | `cs.LG` `cs.AI` `cs.CL` | [GitHub](https://github.com/hp-luo/STARE) | [HF讨论](https://huggingface.co/papers/2606.19236)

### 🇨🇳 中文摘要

针对GRPO算法在训练中策略熵崩溃的问题，本文提出STARE方法，通过基于惊异度的token级优势重加权和目标熵调节来稳定强化学习训练。该方法识别熵关键token子集，有效维持策略多样性。

### 🤖 AI 摘要

GRPO algorithms face policy entropy collapse during training, which STARE addresses through surprisal-guided token-level advantage reweighting and target-entropy regulation to maintain stable reinforcement learning for large language models.

### 💡 推荐理由

> 如果你正在用强化学习训练Agent的推理能力，STARE能直接解决训练中策略熵崩溃的痛点。它通过精细的token级调节保持探索多样性，避免Agent过早收敛到次优策略，提升复杂任务上的最终性能。

### 📋 原始摘要（节选）

Reinforcement Learning with Verifiable Rewards algorithms like GRPO have emerged as the dominant post-training paradigm for complex reasoning in LLMs, yet commonly suffer from policy entropy collapse during training. We conduct a first-order gradient analysis of token-level entropy dynamics under GRPO and identify a token-level credit assignment mismatch: the per-token entropy variation decomposes...


> ⏳ 深度解读尚未完成

---

## 3. Re-Centering Humans in LLM Personalization

> [2606.06614](https://arxiv.org/abs/2606.06614) | `cs.CL` `cs.AI` `cs.HC` | [GitHub](https://github.com/orange0629/recenter-personalization) | [HF讨论](https://huggingface.co/papers/2606.06614)

### 🇨🇳 中文摘要

本文通过收集真实人类对话和判断数据，揭示了LLM个性化系统在合成数据与真实数据之间的显著差距。模型在从人类对话中提取用户属性、判断相关属性以及生成个性化回复方面都存在明显不足。

### 🤖 AI 摘要

Human-centered evaluation reveals significant gaps between synthetic and real-world LLM personalization performance, with models struggling to extract user attributes and generate truly personalized responses that match human quality judgments.

### 💡 推荐理由

> Agent开发中个性化是核心能力，本文提醒你依赖合成数据评估个性化效果可能过于乐观。通过了解真实场景下的瓶颈（如属性提取困难），你可以针对性地优化Agent的用户建模模块，提升实际部署中的个性化表现。

### 📋 原始摘要（节选）

Despite growing interest, most evaluations of large language models' (LLMs') personalization abilities have relied on synthetic data. It remains unclear how well current personalization systems work for real users. In this paper, we study the gap in LLM personalization performance when using synthetic versus human data. We collect human conversations (550 conversations) and judgments across three ...


> ⏳ 深度解读尚未完成

---

## 4. REVES: REvision and VErification--Augmented Training for Test-Time Scaling

> [2606.18910](https://arxiv.org/abs/2606.18910) | `cs.LG` `cs.CL` | [GitHub](https://github.com/yxliu02/REVES) | [HF讨论](https://huggingface.co/papers/2606.18910)

### 🇨🇳 中文摘要

本文提出REVES两阶段迭代框架，通过将中间步骤的“接近正确”答案转化为独立的修正任务来增强LLM推理能力。该方法在编程基准测试和约束满足问题上取得了优于传统多步强化学习的效果。

### 🤖 AI 摘要

A two-stage iterative framework alternates between data augmentation and policy optimization to improve LLM reasoning by leveraging intermediate correction steps, achieving superior performance on coding benchmarks and constraint satisfaction problems.

### 💡 推荐理由

> Agent在复杂任务中常需要多步推理和修正，REVES提供了一种高效利用中间错误来提升推理能力的方法。你可以将其集成到Agent的训练流程中，让Agent学会从自己的错误中学习，提升在编程和逻辑推理任务上的表现。

### 📋 原始摘要（节选）

Test-time scaling via sequential revision has emerged as a powerful paradigm for enhancing Large Language Model (LLM) reasoning. However, standard post-training methods primarily optimize single-shot objectives, creating a fundamental misalignment with multi-step inference dynamics. While recent work treats this as multi-turn reinforcement learning (RL), conventional approaches optimize over the m...


> ⏳ 深度解读尚未完成

---

## 5. No Resource, No Benchmarks, No Problem? Evaluating and Improving LLMs for Code Generation in No-Resource Languages

> [2606.16827](https://arxiv.org/abs/2606.16827) | `cs.SE` | [GitHub](https://github.com/Devy99/no-resource-pl-study) | [HF讨论](https://huggingface.co/papers/2606.16827)

### 🇨🇳 中文摘要

本文研究了LLM在无资源编程语言（训练数据几乎为零的语言）上的代码生成问题，开发了基准测试并提出结合进一步预训练和权重差异迁移的方法，以较低计算成本创建专用指令微调模型。

### 🤖 AI 摘要

Research addresses code generation challenges for no-resource programming languages by developing benchmarks and proposing a method that combines further pre-training with weight difference transfer to create specialized instruction-following models at reduced computational cost.

### 💡 推荐理由

> 作为Java工程师，你可能需要为内部DSL或专有语言生成代码。本文的方法可以帮你快速为这些无资源语言构建代码生成能力，无需大量训练数据，直接提升Agent在特定领域代码生成任务上的实用性。

### 📋 原始摘要（节选）

Large Language Models (LLMs) have significantly advanced the automation of software engineering tasks. One prominent example is code generation, where an LLM produces code in a specified programming language based on a natural language description. Most research in this area has focused on high-resource languages, such as Python or Java, which benefit from abundant training data. A smaller body of...


> ⏳ 深度解读尚未完成

---

## 6. Selective Synergistic Learning for Video Object-Centric Learning

> [2606.15527](https://arxiv.org/abs/2606.15527) | `cs.CV` `cs.AI` | [GitHub](https://github.com/wjun0830/SSync) | [HF讨论](https://huggingface.co/papers/2606.15527)

### 🇨🇳 中文摘要

本文提出选择性协同学习（SSync）方法，通过伪标签和传递合并策略选择性蒸馏可靠线索，解决了视频对象中心学习中注意力图与对象图不一致的问题，提升了对象分解质量和鲁棒性。

### 🤖 AI 摘要

Selective Synergistic Learning (SSync) addresses limitations in video object-centric learning by selectively distilling reliable cues through pseudo-labeling and transitive merging to improve object decomposition quality and robustness.

### 💡 推荐理由

> 如果你的Agent需要处理视频或图像数据（如视觉Agent），SSync提供了一种更鲁棒的对象分解方法。它通过选择性学习避免噪声传播，有助于Agent更准确地理解视觉场景中的物体，提升多模态任务的性能。

### 📋 原始摘要（节选）

Typical video object-centric learning (VOCL) approaches employ slot-based frameworks that rely on reconstruction-driven encoder-decoder architectures, where learning is mediated by two spatial maps: attention maps from the encoder and object maps from the decoder. As these two distinct maps exhibit different properties, a recent dense alignment strategy attempted to reconcile this discrepancy by e...


> ⏳ 深度解读尚未完成

---

## 7. Think Again or Think Longer? Selective Verification for Budget-Aware Reasoning

> [2606.19808](https://arxiv.org/abs/2606.19808) | `cs.AI` `cs.CL` | [GitHub](https://github.com/Sajib-006/SEVRA) | [HF讨论](https://huggingface.co/papers/2606.19808)

### 🇨🇳 中文摘要

本文提出选择性验证方法SEVRA，作为服务层控制器动态决定是否对初始答案进行验证，在保持或提升准确率的同时减少计算开销。在数学推理任务上，该方法比始终验证节省26.8%的token。

### 🤖 AI 摘要

Selective verification approaches optimize test-time reasoning by dynamically deciding when to verify answers, achieving better accuracy and efficiency compared to always-verifying or self-consistency methods.

### 💡 推荐理由

> Agent在推理时经常面临计算资源与准确率的权衡。SEVRA提供了一种智能的预算感知策略，让你可以根据任务难度动态分配推理资源，在保证Agent回答质量的同时降低延迟和成本，特别适合生产环境部署。

### 📋 原始摘要（节选）

Test-time reasoning is increasingly used as a serving-time control knob, but extra reasoning is not uniformly valuable: it can repair failed attempts, waste compute on already-correct answers, or introduce harmful answer changes. We study this as a deployment allocation problem rather than a new-verifier problem. We introduce \sevra, Selective Verification for Reasoning Allocation, a serving-layer...


> ⏳ 深度解读尚未完成

---

## 8. When Does Trajectory-Level Supervision Permit Efficient Offline Reinforcement Learning?

> [2606.18531](https://arxiv.org/abs/2606.18531) | `stat.ML` `cs.LG` | [HF讨论](https://huggingface.co/papers/2606.18531)

### 🇨🇳 中文摘要

本文研究了仅提供轨迹级结果标签的离线强化学习场景，提出OPAC悲观演员-评论家算法来学习潜在奖励模型并优化策略。理论分析给出了统计代价的精确刻画，并证明了在某些广义问题上的根本性障碍。

### 🤖 AI 摘要

Offline reinforcement learning with trajectory-level outcome supervision presents statistical challenges that can be addressed through pessimistic actor-critic methods, though fundamental barriers exist for certain generalized outcome-based problems.

### 💡 推荐理由

> Agent训练中常遇到只有最终结果反馈（如任务成功/失败）而缺乏过程奖励的情况。本文的理论和方法可以帮助你从这类稀疏反馈中有效学习，设计更高效的离线训练策略，减少对密集奖励信号的依赖。

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

本文提出MyPCBench基准，在模拟Linux桌面环境中测试计算机使用Agent作为个人助手的能力，包含17个真实Web应用和184个任务。结果显示Claude Opus 4.6完成率最高仅55.4%，多应用和长轨迹任务仍是挑战。

### 🤖 AI 摘要

MyPCBench evaluates computer-use agents as personal assistants in a simulated Linux desktop environment with real-world web applications, revealing that Claude Opus 4.6 achieves the highest task completion rate of 55.4% while struggles with multi-application tasks and long trajectories.

### 💡 推荐理由

> 如果你正在开发能操作计算机的Agent，MyPCBench提供了贴近真实场景的评估环境。它揭示了当前Agent在跨应用协作和长任务执行上的瓶颈，你可以据此定位自己Agent的薄弱环节，并参考其任务设计来改进。

### 📋 原始摘要（节选）

Current benchmarks for computer-use agents evaluate models in impersonal environments. This leaves a gap between evaluation and deployment where personal assistants are expected to work across a user's whole digital life, including their context, historical data, and logged-in accounts. This gap is widest on web tasks, where live web evaluations cannot exercise sites that require logging in or per...


> ⏳ 深度解读尚未完成

---

## 10. EfficientRollout: System-Aware Self-Speculative Decoding for RL Rollouts

> [2606.18967](https://arxiv.org/abs/2606.18967) | `cs.LG` | [GitHub](https://github.com/furiosa-ai/EfficientRollout) | [HF讨论](https://huggingface.co/papers/2606.18967)

### 🇨🇳 中文摘要

本文提出EfficientRollout，一种系统感知的自推测解码框架，通过自适应调整草稿模型以匹配不断演化的策略，并优化推测解码策略，显著加速强化学习中的rollout生成。

### 🤖 AI 摘要

EfficientRollout is a system-aware self-speculative decoding framework that accelerates reinforcement learning rollouts by adapting drafters to evolving policies and optimizing speculative decoding regimes.

### 💡 推荐理由

> Agent的强化学习训练中，rollout生成往往是延迟瓶颈。EfficientRollout能直接加速这一过程，让你在训练Agent时更快地收集经验数据，缩短迭代周期。对于需要大量在线交互的Agent训练场景，这是非常实用的优化工具。

### 📋 原始摘要（节选）

Reinforcement learning (RL) has become a representative post-training paradigm for LLMs, enabling strong reasoning and agentic capabilities. However, rollout generation remains a dominant latency bottleneck because autoregressive sampling decodes responses sequentially and a small number of long-tailed generations often determine completion time. Speculative decoding (SD) offers a natural way to a...


> ⏳ 深度解读尚未完成

---


> 报告生成时间: 2026-06-19 | 数据来源: Hugging Face Daily Papers + arXiv