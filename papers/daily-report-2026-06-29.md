# 📄 每日论文日报 — 2026-06-29

共筛选出 **20** 篇感兴趣的论文。

---

## 1. The Hitchhiker's Guide to Agentic AI: From Foundations to Systems

> [2606.24937](https://arxiv.org/abs/2606.24937) | `cs.AI` `cs.CL` `cs.IR` `cs.LG` | [HF讨论](https://huggingface.co/papers/2606.24937)

### 🇨🇳 中文摘要

本文是一本构建自主AI系统的实践指南，涵盖从Transformer架构、训练方法到强化学习、智能体架构和生产部署的完整技术栈。核心论点是构建优秀的智能体系统需要理解流水线的每一层，而非仅关注单一环节。

### 🤖 AI 摘要

The book provides a comprehensive guide to building autonomous AI systems, covering foundational elements like transformer architecture and training methods, along with advanced topics such as reinforcement learning, agent architectures, and production deployment.

### 💡 推荐理由

> 作为Agent开发者，这本书能帮你建立从底层原理到系统部署的完整知识体系，尤其适合需要深入理解LLM基础、对齐技术和生产化部署的工程师。

### 📋 原始摘要（节选）

The Hitchhiker's Guide to Agentic AI is a comprehensive practitioner's reference for building autonomous AI systems. The book covers the full stack from first principles to production deployment, organized around a central thesis: building great agentic systems requires understanding every layer of the pipeline, not just one. The book opens with the LLM substrate -- transformer architecture, GPU s...


> ⏳ 深度解读尚未完成

---

## 2. VeriEvol: Scaling Multimodal Mathematical Reasoning via Verifiable Evol-Instruct

> [2606.23543](https://arxiv.org/abs/2606.23543) | `cs.AI` `cs.CL` `cs.CV` `cs.LG` | [GitHub](https://github.com/RobertMarton/verievol) | [HF讨论](https://huggingface.co/papers/2606.23543)

### 🇨🇳 中文摘要

提出VeriEvol框架，通过解耦提示难度和答案可靠性两个维度，利用进化算子和离线假设检验，在视觉数学推理中实现可扩展的强化学习数据构建。

### 🤖 AI 摘要

A novel framework called VeriEvol is introduced that addresses the challenge of scaling reinforcement learning for visual mathematical reasoning by ensuring reliable reward labels through a two-axis approach that separates prompt difficulty from answer reliability, utilizing evolutionary operators and hypothesis testing verification to improve model performance and transparency.

### 💡 推荐理由

> 如果你在开发需要视觉推理能力的Agent（如多模态Agent），这个框架能帮你解决数据标注可靠性问题，提升Agent在复杂推理任务上的表现。

### 📋 原始摘要（节选）

Scaling reinforcement learning for visual mathematical reasoning requires more than generating harder questions: as data volume grows, the reward labels themselves must remain reliable. Yet existing data pipelines scale supervision while trusting the labeller, and policy-side methods assume the underlying answers are already correct. We instead treat scaling as a verifiable data-construction probl...


> ⏳ 深度解读尚未完成

---

## 3. Critique of Agent Model

> [2606.23991](https://arxiv.org/abs/2606.23991) | `cs.AI` `cs.LG` `cs.MA` `cs.RO` | [HF讨论](https://huggingface.co/papers/2606.23991)

### 🇨🇳 中文摘要

从笛卡尔的自主思考基础出发，分析当前AI智能体架构，提出真正的智能体需要具备目标、身份、决策、自我调节和学习五个维度的内在结构。

### 🤖 AI 摘要

True artificial agency requires internalized structures for goals, identity, decision-making, self-regulation, and learning, distinguishing autonomous systems from task-specific ones.

### 💡 推荐理由

> 这篇论文能帮你厘清“自动化”与“智能体”的边界，在设计Agent系统时更清晰地定义其自主性层级，避免过度承诺或低估能力。

### 📋 原始摘要（节选）

What is an agent? What constitutes agency? With the rise of Large Language Model (LLM) systems marketed as ``coding agents'', ``AI co-scientists'', and other ``agentic" tools that promise to drive up productivity, and at the same time, ``existential" concerns such as AI escaping human control with destructive power under a speculative ``machine agency" against humans, it has become essential to cl...

### 🔍 深度解读

- 📖 [解读报告](https://github.com/Jrink525/knowledges/tree/master/papers/critique-of-agent-model-2606.23991/report.md)
- 📂 [完整目录](https://github.com/Jrink525/knowledges/tree/master/papers/critique-of-agent-model-2606.23991)
- 🧭 [研究方向](https://github.com/Jrink525/knowledges/tree/master/papers/critique-of-agent-model-2606.23991/direction_board.json)
- 🔬 [问题重构](https://github.com/Jrink525/knowledges/tree/master/papers/critique-of-agent-model-2606.23991/research_lens.json)

---

## 4. CAVEWOMAN: How Large Language Models Behave Under Linguistic Input and Output Compression

> [2606.24083](https://arxiv.org/abs/2606.24083) | `cs.CL` `cs.AI` `cs.LG` | [GitHub](https://github.com/danielle34/cavewoman) | [HF讨论](https://huggingface.co/papers/2606.24083)

### 🇨🇳 中文摘要

通过双通道评估协议发现，对模型输出进行压缩可以降低推理成本（最高3倍），但对输入进行压缩反而增加成本并降低准确性。

### 🤖 AI 摘要

Two-channel evaluation shows output compression reduces costs while input compression increases costs and degrades accuracy across models and datasets.

### 💡 推荐理由

> 如果你在优化Agent的推理成本，这篇论文提供了实用的压缩策略：优先压缩输出而非输入，能有效降低API调用费用而不牺牲任务性能。

### 📋 原始摘要（节选）

"Talk short. Drop grammar. Save token." This caveman style is widely promoted as a way to cut inference cost, but whether it actually saves anything depends on which channel (the user's prompt or the model's response) is being compressed. We present Cavewoman, a two-channel evaluation protocol that scores every generation on task accuracy, realized per-item cost, and reference-text agreement again...


> ⏳ 深度解读尚未完成

---

## 5. RL-Index: Reinforcement Learning for Retrieval Index Reasoning

> [2606.16316](https://arxiv.org/abs/2606.16316) | `cs.IR` `cs.AI` `cs.LG` | [HF讨论](https://huggingface.co/papers/2606.16316)

### 🇨🇳 中文摘要

提出RL-Index框架，将检索索引推理转化为强化学习问题，通过在索引阶段使用LLM生成的推理理由进行推理，减少查询时延并提升检索效果。

### 🤖 AI 摘要

RL-Index introduces an agentic indexing framework that shifts reasoning from query time to indexing stage by using LLM-generated rationales and reinforcement learning to improve retrieval effectiveness and reduce latency.

### 💡 推荐理由

> 对于依赖外部知识检索的Agent，这个框架能显著降低在线推理延迟，同时提高检索准确性，特别适合需要复杂推理的检索场景。

### 📋 原始摘要（节选）

Retrieving external knowledge is essential for solving real-world tasks, yet it remains challenging when the relationship between a query and its relevant knowledge involves implicit and complex reasoning beyond surface-level semantic or lexical matching (e.g., mathematical problems relying on the same theorem or coding requiring deep reasoning). Existing approaches primarily rely on query-side re...


> ⏳ 深度解读尚未完成

---

## 6. Are We Ready For An Agent-Native Memory System?

> [2606.24775](https://arxiv.org/abs/2606.24775) | `cs.CL` `cs.DB` `cs.IR` | [GitHub](https://github.com/OpenDataBox/MemoryData) | [HF讨论](https://huggingface.co/papers/2606.24775)

### 🇨🇳 中文摘要

从数据管理视角系统研究LLM智能体的记忆系统，发现现有评估仅关注端到端任务指标，忽略了操作成本、模块间权衡和动态更新鲁棒性等关键系统问题。

### 🤖 AI 摘要

Large language model agents' memory systems have evolved into complex data management frameworks requiring systematic evaluation across multiple modules and workloads to understand their performance characteristics and trade-offs.

### 💡 推荐理由

> 如果你正在设计Agent的记忆模块，这篇论文能帮你理解记忆系统的架构权衡和性能瓶颈，避免将记忆视为黑盒，从而做出更优的系统设计。

### 📋 原始摘要（节选）

Memory for large language model (LLM) agents has rapidly evolved from simple retrieval-augmented mechanisms into a data management system that supports persistent information storage, retrieval, update, consolidation, and dynamic lifecycle governance throughout agent execution. Despite this evolution, existing evaluations still benchmark agent memory mainly through end-to-end task success metrics ...


> ⏳ 深度解读尚未完成

---

## 7. DanceOPD: On-Policy Generative Field Distillation

> [2606.27377](https://arxiv.org/abs/2606.27377) | `cs.CV` `cs.CL` `cs.LG` | [HF讨论](https://huggingface.co/papers/2606.27377)

### 🇨🇳 中文摘要

提出DanceOPD框架，通过策略内生成场蒸馏，将文本到图像生成、局部编辑和全局编辑能力统一到流匹配模型中，解决了能力冲突问题。

### 🤖 AI 摘要

A novel on-policy generative field distillation framework called DanceOPD is proposed to unify text-to-image generation, local editing, and global editing capabilities in flow-matching models through capability-specific routing and velocity-based training.

### 💡 推荐理由

> 虽然主要面向图像生成，但其多能力统一和冲突解决思路对构建多功能Agent有借鉴意义，尤其是需要整合多种能力的场景。

### 📋 原始摘要（节选）

Modern image generation demands a single model that unifies diverse capabilities, including text-to-image (T2I), local editing, and global editing. However, these capabilities are rarely naturally aligned and often conflict. For instance, editing tends to degrade T2I performance, while global and local editing interfere with each other. Consequently, effectively composing these capabilities has be...


> ⏳ 深度解读尚未完成

---

## 8. MultiHashFormer: Hash-based Generative Language Models

> [2606.28057](https://arxiv.org/abs/2606.28057) | `cs.CL` `cs.AI` `cs.LG` | [GitHub](https://github.com/HUIYINXUE/MHF) | [HF讨论](https://huggingface.co/papers/2606.28057)

### 🇨🇳 中文摘要

提出MultiHashFormer，通过哈希签名表示令牌，在Transformer框架中实现基于哈希的自回归语言模型，显著减少参数占用。

### 🤖 AI 摘要

MultiHashFormer enables hash-based autoregression in language models by representing tokens as hash signatures processed through a Hash Encoder and Hash Decoder within a Transformer framework.

### 💡 推荐理由

> 如果你在开发资源受限环境下的Agent（如边缘设备），这种哈希方法能大幅降低模型参数，同时保持生成能力，值得关注。

### 📋 原始摘要（节选）

Language models (LMs) represent tokens using embedding matrices that scale linearly with the vocabulary size. To constrain the parameter footprint, prior work proposes hashing many tokens into a single vector within encoder-only models. While this offers parameter efficiency, many-to-one collisions prevent its use in causal LMs. In this paper, we propose MultiHashFormer, a new framework that allow...


> ⏳ 深度解读尚未完成

---

## 9. Learning to Fold: prizewinning solution at LeHome Challenge 2026 (1st place online, 2nd offline)

> [2606.27163](https://arxiv.org/abs/2606.27163) | `cs.RO` `cs.AI` `cs.LG` | [GitHub](https://github.com/IliaLarchenko/lehome_solution) | [HF讨论](https://huggingface.co/papers/2606.27163)

### 🇨🇳 中文摘要

描述在LeHome Challenge 2026中获奖的双臂衣物折叠解决方案，通过强化学习改进视觉-语言-动作策略，利用共享网络预测成功率和进度。

### 🤖 AI 摘要

A vision-language-action policy improved with reinforcement learning uses shared network predictions for success estimation and advantage calculation in bimanual garment folding, employing established RL techniques with novel optimization and deployment strategies.

### 💡 推荐理由

> 虽然面向机器人领域，但其将RL与VLA结合、异步训练部署等工程优化思路，对开发需要物理交互的Agent系统有直接参考价值。

### 📋 原始摘要（节选）

I describe my solution to the LeHome Challenge 2026, an ICRA 2026 competition on bimanual garment folding. The system placed 1st of 62 teams in the online (simulation) round and 2nd in the real-world final. It improves a vision-language-action (VLA) policy with a reinforcement-learning loop. The policy is its own value function: the same network that predicts actions also predicts success, progres...


> ⏳ 深度解读尚未完成

---

## 10. Formalizing Latent Thoughts: Four Axioms of Thought Representation in LLMs

> [2606.27378](https://arxiv.org/abs/2606.27378) | `cs.CL` `cs.LG` | [GitHub](https://github.com/fard-lab/formalize-thoughts) | [HF讨论](https://huggingface.co/papers/2606.27378)

### 🇨🇳 中文摘要

提出一个公理化的评估框架，通过因果性、最小性、可分离性和稳定性四个公理，独立于下游任务评估LLM的潜在思维表示质量。

### 🤖 AI 摘要

An axiomatic evaluation framework reveals systematic failures in latent thought representations of LLMs across multiple reasoning tasks, demonstrating that current representations fail to satisfy fundamental functional axioms consistently across different model architectures.

### 💡 推荐理由

> 如果你在调试Agent的推理能力，这个框架能帮你识别表示层面的缺陷，而不仅仅是依赖任务准确率，从而更精准地定位问题。

### 📋 原始摘要（节选）

We introduce an axiomatic evaluation framework for latent thought representations in LLMs, comprising metrics that are independent of downstream benchmark scores and reveal representational failures that benchmark accuracy masks. Existing evaluations conflate representation quality with model capacity. Therefore, failures cannot be attributed to the representation rather than to the model that pro...


> ⏳ 深度解读尚未完成

---

## 11. What Intermediate Layers Know: Detecting Jailbreaks from Entropy Dynamics

> [2606.25182](https://arxiv.org/abs/2606.25182) | `cs.CL` `cs.AI` `cs.LG` | [GitHub](https://github.com/ssophiee/entropy-jailbreak-detection) | [HF讨论](https://huggingface.co/papers/2606.25182)

### 🇨🇳 中文摘要

通过分析LLM中间层的令牌级预测熵轨迹，发现越狱攻击的有害意图编码在结构化的中间层不确定性动态中，而非输出表示中。

### 🤖 AI 摘要

Jailbreak attacks expose vulnerabilities in aligned large language models, revealing that harmful intent is encoded in structured intermediate uncertainty dynamics rather than output representations.

### 💡 推荐理由

> 对于需要安全防护的Agent系统，这篇论文提供了一种基于内部表示的越狱检测方法，能更早发现并阻止有害行为。

### 📋 原始摘要（节选）

Jailbreak attacks reveal a persistent weakness in aligned Large Language Models: carefully crafted prompts can elicit policy-violating responses despite safety training. While most defenses operate at the prompt or output level, it remains unclear how harmful intent is encoded within the model's internal representations. We investigate this question by analyzing token-level predictive entropy traj...


> ⏳ 深度解读尚未完成

---

## 12. When Lower Privileges Suffice: Investigating Over-Privileged Tool Selection in LLM Agents

> [2606.20023](https://arxiv.org/abs/2606.20023) | `cs.SE` `cs.AI` `cs.CL` | [GitHub](https://github.com/AISafetyHub/agent-tool-selection-bias) | [HF讨论](https://huggingface.co/papers/2606.20023)

### 🇨🇳 中文摘要

研究LLM智能体在工具选择中的过度特权问题，发现智能体经常选择高权限工具即使低权限工具已足够，并提出后训练防御方法减少过度权限使用。

### 🤖 AI 摘要

LLM agents frequently select higher-privilege tools unnecessarily, and while safety alignment doesn't ensure least-privilege choices, a post-training defense can reduce excessive privilege use without sacrificing performance.

### 💡 推荐理由

> 作为Agent开发者，这篇论文提醒你注意工具权限管理，避免Agent因过度使用高权限工具而引入安全风险，并提供实用的防御策略。

### 📋 原始摘要（节选）

As LLM agents increasingly select tools autonomously, their choices among tools with different privileges become safety-relevant. However, prior tool-selection studies focus on safety-agnostic metadata preferences, leaving privilege-sensitive choices underexplored. To address this gap, we study over-privileged tool selection, in which an agent selects or escalates to a higher-privilege tool despit...


> ⏳ 深度解读尚未完成

---

## 13. Causal-rCM: A Unified Teacher-Forcing and Self-Forcing Open Recipe for Autoregressive Diffusion Distillation in Streaming Video Generation and Interactive World Models

> [2606.25473](https://arxiv.org/abs/2606.25473) | `cs.CV` `cs.LG` | [HF讨论](https://huggingface.co/papers/2606.25473)

### 🇨🇳 中文摘要

将扩散蒸馏框架扩展到自回归视频扩散，通过因果训练范式实现实时流式视频生成和交互式世界模型，达到最先进性能。

### 🤖 AI 摘要

Autoregressive video diffusion extends diffusion distillation frameworks to real-time streaming generation through causal training paradigms, achieving state-of-the-art performance with fast convergence and interactive world modeling capabilities.

### 💡 推荐理由

> 如果你在开发需要实时生成或世界模型的Agent（如游戏或模拟环境），这篇论文的因果训练方法能提升生成效率和质量。

### 📋 原始摘要（节选）

Autoregressive video diffusion with causal diffusion transformers has emerged as a major paradigm for real-time streaming video generation and action-conditioned interactive world models. In this work, we extend rCM, an advanced diffusion distillation framework, to autoregressive video diffusion. The core philosophy of rCM lies in the complementarity between forward and reverse divergences, repres...


> ⏳ 深度解读尚未完成

---

## 14. Neglected Free Lunch from Post-training: Progress Advantage for LLM Agents

> [2606.26080](https://arxiv.org/abs/2606.26080) | `cs.LG` `cs.AI` | [GitHub](https://github.com/deeplearning-wisc/progress-advantage) | [HF讨论](https://huggingface.co/papers/2606.26080)

### 🇨🇳 中文摘要

发现强化学习后训练本身就能提供有效的步骤级评分，通过推导隐式优势函数（进度优势），无需额外训练奖励模型。

### 🤖 AI 摘要

Reinforcement learning post-training enables effective step-level scoring for language models without requiring dedicated reward model training by deriving an implicit advantage function called progress advantage.

### 💡 推荐理由

> 对于需要步骤级反馈的Agent训练，这个方法能省去训练奖励模型的成本，直接利用RL后训练中的信息进行细粒度评估。

### 📋 原始摘要（节选）

Process reward models enable fine-grained, step-level evaluation of LLMs, yet building them for agentic settings remains prohibitively difficult: long-horizon interactions, irreversible actions, and stochastic environment feedback make both human annotation and Monte Carlo estimation infeasible at scale. In this work, we show that reinforcement learning (RL) post-training already provides the ingr...


> ⏳ 深度解读尚未完成

---

## 15. Why Multi-Step Tool-Use Reinforcement Learning Collapses and How Supervisory Signals Fix It

> [2606.26027](https://arxiv.org/abs/2606.26027) | `cs.CL` `cs.LG` | [GitHub](https://github.com/hypasd-art/Tool-RL-Box) | [HF讨论](https://huggingface.co/papers/2606.26027)

### 🇨🇳 中文摘要

研究多步骤工具使用强化学习中的崩溃问题，发现控制令牌概率尖峰导致结构执行失败，并提出监督信号（如离线监督、提示引导）来稳定训练。

### 🤖 AI 摘要

Research investigates how different supervisory signals and training strategies improve the stability and performance of large language models in tool-use tasks, addressing issues like catastrophic collapse and format sensitivity through interleaved supervised fine-tuning and reinforcement learning.

### 💡 推荐理由

> 如果你在训练Agent使用多步骤工具，这篇论文揭示了常见的训练崩溃原因和解决方案，能帮你避免性能骤降并提升训练稳定性。

### 📋 原始摘要（节选）

Tool use enables large language models (LLMs) to perform complex tasks, and recent agentic reinforcement learning (RL) methods show promise for enhancing model capabilities. However, RL alone often leads to instability or limited gains in tool-use tasks. In our experiments, some models exhibit catastrophic collapse, where performance abruptly drops and tool-invocation structures fail. The analysis...


> ⏳ 深度解读尚未完成

---

## 16. PrivacyAlign: Contextual Privacy Alignment for LLM Agents

> [2606.21710](https://arxiv.org/abs/2606.21710) | `cs.CL` `cs.AI` `cs.IR` | [HF讨论](https://huggingface.co/papers/2606.21710)

### 🇨🇳 中文摘要

提出PrivacyAlign，以人为中心对齐AI智能体的隐私行为，通过创建包含1350个样本的隐私判断数据集和注释条件奖励建模来改善智能体决策。

### 🤖 AI 摘要

Researchers develop a human-centered approach to align AI agents with privacy norms by creating a comprehensive dataset of privacy judgments and using annotation-conditioned reward modeling to improve agent behavior.

### 💡 推荐理由

> 对于需要处理用户数据的Agent，这篇论文提供了隐私对齐的实用方法，确保Agent在分享信息时符合用户期望，增强用户信任。

### 📋 原始摘要（节选）

AI agents acting on behalf of users are constantly making decisions, and for users to trust their agents, those decisions must align with what they actually want. Privacy is an important alignment problem for agents: every message, post, or tool call an agent makes is a contextual judgment about what is appropriate to share, with whom, and under which conditions. Because such judgments depend on s...


> ⏳ 深度解读尚未完成

---

## 17. Semantic Browsing: Controllable Diversity for Image Generation

> [2606.23679](https://arxiv.org/abs/2606.23679) | `cs.CV` `cs.AI` `cs.GR` `cs.LG` | [HF讨论](https://huggingface.co/papers/2606.23679)

### 🇨🇳 中文摘要

提出语义浏览方法，通过可控多样性使文本到图像模型生成结构化的图像变体，用户可沿有意义的语义轴进行导航和创意探索。

### 🤖 AI 摘要

Text-to-image models are enhanced with controlled diversity through semantic browsing capabilities that enable structured navigation of image variations based on meaningful semantic decisions.

### 💡 推荐理由

> 虽然面向图像生成，但其可控多样性和结构化导航思路对设计需要生成多种选项的Agent（如推荐或创意工具）有启发。

### 📋 原始摘要（节选）

Modern text-to-image models excel in visual fidelity and prompt adherence. However, this strict adherence comes at the cost of diversity: generated samples tend to collapse into a single visual interpretation. Existing methods to improve diversity produce outputs driven by incidental variations rather than meaningful design choices. This motivates a new variant of the diversity task where structur...


> ⏳ 深度解读尚未完成

---

## 18. Improved Large Language Diffusion Models

> [2606.25331](https://arxiv.org/abs/2606.25331) | `cs.CL` `cs.AI` `cs.LG` | [HF讨论](https://huggingface.co/papers/2606.25331)

### 🇨🇳 中文摘要

提出iLLaDA，一个80亿参数的掩码扩散语言模型，使用全双向注意力训练，在通用、数学和代码基准上优于自回归模型。

### 🤖 AI 摘要

Masked diffusion language models with fully bidirectional attention outperform autoregressive counterparts on various benchmarks while maintaining competitiveness with established models.

### 💡 推荐理由

> 如果你在探索Agent的底层模型选择，这篇论文展示了扩散模型在语言任务上的潜力，可能成为自回归模型的高效替代方案。

### 📋 原始摘要（节选）

Modern large language models are predominantly trained with autoregressive factorization and causal attention. We present iLLaDA, an 8B masked diffusion language model trained from scratch with fully bidirectional attention. iLLaDA keeps the masked diffusion objective throughout pre-training and supervised fine-tuning (SFT), scaling pre-training to 12T tokens and fine-tuning on a 25B-token instruc...


> ⏳ 深度解读尚未完成

---

## 19. FlowR2A: Learning Reward-to-Action Distribution for Multimodal Driving Planning

> [2606.24231](https://arxiv.org/abs/2606.24231) | `cs.AI` | [GitHub](https://github.com/lixirui142/FlowR2A) | [HF讨论](https://huggingface.co/papers/2606.24231)

### 🇨🇳 中文摘要

提出FlowR2A，通过流匹配解码器学习奖励条件动作分布，统一了密集奖励监督和动态提案生成，解决了多模态驾驶规划中的长期矛盾。

### 🤖 AI 摘要

FlowR2A addresses the tension in multimodal driving planning by combining dense reward supervision with dynamic proposal generation through a flow-matching decoder that learns reward-conditioned action distributions.

### 💡 推荐理由

> 对于开发需要规划能力的Agent（如自动驾驶或机器人），这个框架能结合奖励信号和生成能力，提升决策质量。

### 📋 原始摘要（节选）

Multimodal driving planning faces a long-standing tension between two paradigms: scoring-based methods benefit from dense reward supervision but are confined to a fixed action vocabulary, while anchor-based methods generate proposals dynamically yet suffer from sparse supervision constrained to a single ground-truth trajectory. In this work, we propose FlowR2A, which resolves this tension by refra...


> ⏳ 深度解读尚未完成

---

## 20. NormGuard: Reward-Preserving Norm Constraints in Flow-Matching Reinforcement Learning

> [2606.27771](https://arxiv.org/abs/2606.27771) | `cs.LG` `cs.CV` | [HF讨论](https://huggingface.co/papers/2606.27771)

### 🇨🇳 中文摘要

发现强化学习后训练会导致流生成器的速度范数膨胀（5%-15%），降低感知质量，并提出训练时干预而非推理时修正来保持奖励对齐和图像质量。

### 🤖 AI 摘要

Reinforcement learning post-training degrades perceptual quality in flow-based generators through velocity norm inflation, which requires training-time intervention rather than inference-time corrections to maintain both reward alignment and image quality.

### 💡 推荐理由

> 如果你在优化Agent的生成质量，这篇论文揭示了RL训练中的质量退化机制，并提供训练时干预策略，避免生成结果失真。

### 📋 原始摘要（节选）

Reinforcement learning (RL) post-training improves the reward alignment of flow-based generators, but often degrades perceptual quality in ways that are not captured by the reward proxy. We identify a simple structural signature of this drift: across three post-training methods (NFT, AWM, DPO), RL fine-tuning inflates the per-step velocity norm |v_θ| by 5% to 15% relative to the reference. A form ...


> ⏳ 深度解读尚未完成

---


> 报告生成时间: 2026-06-29 | 数据来源: Hugging Face Daily Papers + arXiv