# 前言与引言（Preamble & Introduction）
\label{preamble}

---

## 扉页（Title Page）
\label{title-page}

**The Hitchhiker's Guide to Agentic AI**
\label{book-title}
**《Agentic AI 漫游指南》**

*From Foundations to Systems*
*从基础到系统*

**Haggai Roitman**
**Haggai Roitman**

*2026*
*2026 年*

Version 1.2.2
版本 1.2.2

---

## 献辞（Dedication）
\label{dedication}

*To my beloved wife Janna and daughters Inbar and Einav.*
*献给我挚爱的妻子 Janna 以及女儿 Inbar 和 Einav。*

---

## 目录（Table of Contents）
\label{table-of-contents}

（目录略。全书共 29 章，分为六个部分：Part I 基础（1–3 章）、Part II LLM 的 RL 方法（4–12 章）、Part III 推理（13 章）、Part IV 评估（14 章）、Part V Agentic AI（15–26 章）、Part VI 评估与参考（27–29 章）。）

---

## 声明（Disclaimer）
\label{disclaimer}

This document is an independent survey and educational resource prepared solely by the author. The views, opinions, and conclusions expressed herein are those of the author alone and do not necessarily reflect the views of any employer, organization, or institution with which the author is or has been affiliated.
本文档是由作者独立编写的综述和教育资源。本文表达的观点、意见和结论仅代表作者个人，不一定反映作者现任或曾任雇主的观点。

This work does not contain any proprietary, confidential, or trade-secret information. All referenced material is drawn from publicly available sources, including peer-reviewed publications, open-access preprints, official documentation, and open-source repositories.
本作品不包含任何专有、机密或商业秘密信息。所有引用资料均来自公开来源，包括同行评审出版物、开放获取预印本、官方文档和开源仓库。

The content is provided "as is" without warranty of any kind, express or implied. The author makes no representations regarding the accuracy, completeness, or suitability of the information for any particular purpose. Readers should independently verify any claims, formulas, or implementation details before applying them in production systems.
内容按"原样"提供，不附带任何明示或暗示的保证。作者不对信息的准确性、完整性或适用性做任何陈述。读者应在应用于生产系统之前独立验证任何声明、公式或实现细节。

**Feedback welcome.** If you find any mistakes, inaccuracies, or have suggestions for improvement, you are encouraged to send feedback to `[first_name]r@gmail.com`.
**欢迎反馈。** 如果您发现任何错误、不准确之处或有改进建议，欢迎发送反馈至 `[first_name]r@gmail.com`。

**AI Disclosure.** Large language models were used as a research and drafting aid. All content was edited and verified by the author on a best-effort basis.
**AI 声明。** 大型语言模型被用作研究和起草辅助工具。所有内容均由作者尽力编辑和验证。

**License.** This work is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License** (CC BY-SA 4.0). You are free to share (copy and redistribute) and adapt (remix, transform, and build upon) this material for any purpose, including commercially, provided you give appropriate credit, provide a link to the license, indicate if changes were made, and distribute any derivative works under the same license. Full license text: <https://creativecommons.org/licenses/by-sa/4.0/>.
**许可协议。** 本作品采用**知识共享署名-相同方式共享 4.0 国际许可协议**（CC BY-SA 4.0）授权。您可以自由分享（复制和重新分发）和改编（重新混编、转换和在此基础上构建）本材料用于任何目的（包括商业用途），前提是您给予适当的署名，提供许可协议链接，指明是否做了修改，并在相同许可协议下分发衍生作品。完整许可文本：<https://creativecommons.org/licenses/by-sa/4.0/>。

---

## 关于作者（About the Author）
\label{about-the-author}

**Haggai Roitman** has spent over two decades at the intersection of AI research and large-scale production systems. His work bridges theory and practice---from publishing foundational research to shipping systems that serve millions of users.
**Haggai Roitman** 在 AI 研究与大规模生产系统的交叉领域工作了二十余年。他的工作连接理论与实践——从发表基础研究到交付服务数百万用户的系统。

His research interests span information retrieval, recommender systems, natural language processing, large language models, reinforcement learning for LLMs, and agentic AI. He has authored more than 100 peer-reviewed publications and holds approximately 100 patents. He earned his BSc (*Cum Laude*) and PhD from the Technion --- Israel Institute of Technology.
他的研究兴趣涵盖信息检索、推荐系统、自然语言处理、大型语言模型、LLM 强化学习以及 Agentic AI。他已发表 100 多篇同行评审论文，并持有约 100 项专利。他在以色列理工学院（Technion）获得了学士学位（*Cum Laude*）和博士学位。

When not thinking about gradient flows and KV caches, he can be found behind a set of turntables, mixing progressive trance and deep house.
当他不思考梯度流和 KV 缓存时，你会看到他站在唱机转盘后面，混音渐进迷幻和深浩室音乐。

---

## 前言（Preface）
\label{preface}

### 为什么写这本指南（Why This Guide Exists）
\label{why-this-guide-exists}

Building intelligent AI systems in 2026 requires mastering an extraordinary breadth of knowledge --- from how transformers process language internally, through the hardware and systems that make training possible, the optimization techniques that make it efficient, the reinforcement learning algorithms that teach models to reason and align with human intent, all the way to multi-agent architectures that coordinate autonomous systems at scale.
在 2026 年构建智能 AI 系统需要掌握极其广泛的知识——从 Transformer 如何内部处理语言，到使训练成为可能的硬件和系统，使其高效的优化技术，教会模型推理和与人类意图对齐的强化学习算法，再到协调大规模自主系统的多智能体架构。

This knowledge is scattered across hundreds of papers, blog posts, GitHub repositories, and tribal knowledge within a handful of labs. This guide exists because **practitioners need a single, unified reference** that covers the entire stack --- not just the theory, but the implementation details that make things actually work.
这些知识分散在数百篇论文、博客文章、GitHub 仓库和少数实验室的内部经验中。这本指南的存在是因为**实践者需要一个统一的参考**来覆盖整个技术栈——不仅是理论，还包括使事情真正工作的实现细节。

### 通往 Agentic AI 的个人旅程（A Personal Journey to Agentic AI）
\label{a-personal-journey-to-agentic-ai}

My fascination with intelligent agents began two decades ago, when I still studied for my first degree in information systems engineering. I took courses on Agent-Oriented Software Engineering (AOSE) [Wooldridge 2000] and learned to build multi-agent systems using JADE (Java Agent DEvelopment Framework) [Bellifemine 2007]—a FIPA-compliant [FIPA 2002] platform where agents communicated via structured protocols, negotiated over shared resources, and coordinated autonomously. Around the same time, Berners-Lee, Hendler, and Lassila's seminal paper "The Semantic Web" [Berners-Lee 2001] painted a vision of machine-readable knowledge that agents could reason over. These two threads---autonomous agent architectures and semantic knowledge representation---planted a seed that has guided my career ever since. One early project that crystallized this vision was an attempt to build a *shopping agent*---developed with OntoBuilder [Gal 2006] under the guidance of my respected future academic advisor Prof. Avigdor Gal---a system that could automatically fill product search queries and orders across different heterogeneous websites, understanding their varied schemas through ontology matching and mapping. The Semantic Web promised that such agents would thrive in a world of structured, machine-readable data. In practice, the brittleness of hand-crafted ontologies, the messiness of real-world product data, and the lack of robust natural language understanding made the vision perpetually "five years away."
我对智能体的迷恋始于二十年前，当时我还在攻读信息系统工程本科学位。我修读了面向 Agent 的软件工程（AOSE）课程 [Wooldridge 2000]，并学会了使用 JADE（Java Agent DEvelopment Framework）[Bellifemine 2007] 构建多智能体系统——这是一个符合 FIPA [FIPA 2002] 标准的平台，在其中智能体通过结构化协议通信、协商共享资源并自主协调。大约在同一时间，Berners-Lee、Hendler 和 Lassila 的开创性论文"语义网" [Berners-Lee 2001] 描绘了一幅机器可读知识的愿景，智能体可以在其上推理。这两条线索——自主智能体架构和语义知识表示——播下了一颗种子，从此指引着我的职业生涯。一个早期项目让这一愿景变得具体化：我尝试构建一个*购物智能体*——在我尊敬的未来学术导师 Avigdor Gal 教授的指导下使用 OntoBuilder [Gal 2006] 开发——这个系统可以自动跨不同的异构网站填写产品搜索查询和订单，通过本体匹配和映射理解它们不同的模式。语义网曾承诺，这样的智能体将在结构化、机器可读数据的世界中繁荣发展。然而在实践中，手工构建本体的脆弱性、真实世界产品数据的混乱以及缺乏稳健的自然语言理解，使得这一愿景始终"遥不可及"。

Over the following years, I tracked each wave of AI progress as it arrived: neural networks and heuristic search for combinatorial optimization; deep learning and representation learning; information retrieval and personalization at scale; and most recently, the revolution of large language models. Each wave brought powerful new tools, but the dream remained the same: systems that *understand*, *reason*, and *act* autonomously in complex environments.
在随后的岁月里，我跟随着 AI 进步的每一波浪潮：用于组合优化的神经网络和启发式搜索；深度学习和表示学习；大规模信息检索和个性化；以及最近的大型语言模型革命。每一波浪潮都带来了强大的新工具，但梦想始终未变：在复杂环境中*理解*、*推理*和*行动*的自主系统。

What makes 2024--2026 remarkable is that these threads have finally converged. LLMs provide the language understanding and generation; reinforcement learning teaches them to reason and align with human intent; tool-use protocols (MCP) give them hands to act in the world; and agent orchestration frameworks provide the coordination layer that JADE envisioned twenty years ago---now powered by foundation models instead of hand-coded ontologies. This guide is, in many ways, the reference I wish I had at each step of that journey.
2024–2026 年之所以非凡，是因为这些线索终于汇聚在一起。LLM 提供了语言理解和生成；强化学习教会它们推理和与人类意图对齐；工具使用协议（MCP）赋予它们在世界中行动的能力；而智能体编排框架提供了 JADE 二十年前设想的协调层——现在由基础模型驱动，而非手工编码的本体。这本指南在许多方面都是我在这段旅程的每一步都希望拥有的参考。

### 2026 年的格局（The Landscape in 2026）
\label{the-landscape-in-2026}

The journey to today's agentic AI systems spans three decades of compounding breakthroughs across architecture, training, and deployment:
通往今天 Agentic AI 系统的旅程跨越了三十年，在架构、训练和部署方面积累了突破：

1. **Architectural foundations (2017--2020)**: The Transformer [Vaswani 2017] introduced self-attention as a universal sequence-processing primitive. Scaling laws revealed that larger models trained on more data reliably improve. GPT-2 and GPT-3 demonstrated that decoder-only transformers, scaled sufficiently, become capable few-shot learners.
   **架构基础（2017–2020）**：Transformer [Vaswani 2017] 引入了自注意力作为通用序列处理原语。缩放定律揭示了在更多数据上训练的更大模型会可靠地改进。GPT-2 和 GPT-3 证明了，足够大的纯解码器 Transformer 成为有能力的少样本学习器。

2. **Systems and efficiency (2020--2023)**: Flash Attention [Dao 2022] made training 2–4× faster by eliminating memory bottlenecks. LoRA [Hu 2022] enabled fine-tuning 70B+ models on a single node. Mixture-of-Experts (MoE) decoupled model capacity from compute cost. Inference engines like vLLM brought throughput within reach of real-time applications.
   **系统和效率（2020–2023）**：Flash Attention [Dao 2022] 通过消除内存瓶颈使训练速度提升 2–4 倍。LoRA [Hu 2022] 使得在单个节点上微调 70B+ 模型成为可能。混合专家（MoE）将模型容量与计算成本解耦。vLLM 等推理引擎使实时应用的吞吐量触手可及。

3. **Alignment via RL (2022--2024)**: RLHF [Ouyang 2022] transformed capable-but-unhelpful base models into useful assistants---the recipe behind ChatGPT. DPO [Rafailov 2023] collapsed the reward model and RL loop into a single supervised loss, democratizing alignment. Variants proliferated: KTO [Ethayarajh 2024], IPO [Azar 2024], ORPO [Hong 2024], GRPO [Shao 2024].
   **通过 RL 对齐（2022–2024）**：RLHF [Ouyang 2022] 将有能力但不实用的基础模型转变为有用的助手——这便是 ChatGPT 背后的配方。DPO [Rafailov 2023] 将奖励模型和 RL 循环压缩为单个监督损失，使对齐民主化。变体大量涌现：KTO [Ethayarajh 2024]、IPO [Azar 2024]、ORPO [Hong 2024]、GRPO [Shao 2024]。

4. **Reasoning and autonomy (2024--2026)**: DeepSeek-R1 [DeepSeek 2025] and OpenAI's o1/o3 demonstrated that RL could teach *reasoning itself*---models spontaneously discover chain-of-thought, backtracking, and self-verification. Simultaneously, the Model Context Protocol (MCP) standardized tool access, Agent-to-Agent (A2A) enabled inter-agent communication, and production-grade orchestration frameworks matured.
   **推理和自主性（2024–2026）**：DeepSeek-R1 [DeepSeek 2025] 和 OpenAI 的 o1/o3 证明了 RL 可以教会*推理本身*——模型自发地发现思维链、回溯和自我验证。同时，模型上下文协议（MCP）标准化了工具访问，智能体间（A2A）协议实现了智能体间通信，生产级编排框架也趋于成熟。

### 本指南面向谁（Who This Guide Is For）
\label{who-this-guide-is-for}

This document is written for **practitioners who build things**:
本文档面向**构建东西的实践者**：

- **ML engineers** who need to understand transformer internals, training infrastructure, optimization, and why things diverge.
  **ML 工程师**——需要理解 Transformer 内部原理、训练基础设施、优化以及训练发散的原因。

- **Applied researchers** evaluating architectures, fine-tuning strategies, and RL methods for their specific domains.
  **应用研究员**——为其特定领域评估架构、微调策略和 RL 方法。

- **Agent developers** building production systems who need orchestration patterns, memory architectures, tool integration (MCP), and multi-agent coordination (A2A).
  **智能体开发者**——构建生产系统，需要编排模式、记忆架构、工具集成（MCP）和多智能体协调（A2A）。

- **Systems engineers** responsible for training infrastructure, GPU clusters, distributed training, and inference deployment.
  **系统工程师**——负责训练基础设施、GPU 集群、分布式训练和推理部署。

- **Technical leaders** making architectural and resourcing decisions across the full stack.
  **技术领导者**——在完整技术栈上做出架构和资源配置决策。

We assume familiarity with neural networks and basic probability. **No prior LLM, RL, or systems knowledge is required**---the guide builds from first principles.
我们假设读者熟悉神经网络和基础概率论。**不需要先验的 LLM、RL 或系统知识**——本指南从基本原理开始构建。

### 你将获得什么（What You Will Gain）
\label{what-you-will-gain}

After reading this guide, you will be able to:
阅读本指南后，你将能够：

- **Understand LLM internals**---attention mechanisms, positional encodings, MoE routing, Flash Attention, and why architectural choices matter for downstream capability.
  **理解 LLM 内部原理**——注意力机制、位置编码、MoE 路由、Flash Attention，以及架构选择为何对下游能力重要。

- **Reason about systems**---GPU memory budgets, distributed training strategies (FSDP, tensor/pipeline parallelism), inference optimization, and production deployment with vLLM.
  **推理系统设计**——GPU 内存预算、分布式训练策略（FSDP、张量/流水线并行）、推理优化以及使用 vLLM 的生产部署。

- **Train and fine-tune efficiently**---LoRA/QLoRA, quantization, knowledge distillation, optimizer selection, and learning rate scheduling.
  **高效训练和微调**——LoRA/QLoRA、量化、知识蒸馏、优化器选择和学习率调度。

- **Align models with human preferences**---implement RLHF/DPO/GRPO/KTO pipelines, debug reward hacking and mode collapse, choose the right algorithm among 20+ methods.
  **使模型与人类偏好对齐**——实现 RLHF/DPO/GRPO/KTO 流程，调试奖励黑客和模式崩溃，在 20 多种方法中选择合适的算法。

- **Build reasoning models**---understand how DeepSeek-R1, o1/o3, and QwQ discover chain-of-thought through RL without explicit demonstrations.
  **构建推理模型**——理解 DeepSeek-R1、o1/o3 和 QwQ 如何通过 RL 在不需要显式示范的情况下发现思维链。

- **Architect agentic systems**---select orchestration patterns, design memory, integrate tools via MCP, coordinate agents via A2A, evaluate with production benchmarks.
  **架构 Agentic 系统**——选择编排模式、设计记忆系统、通过 MCP 集成工具、通过 A2A 协调智能体、使用生产基准进行评估。

- **Evaluate rigorously**---apply appropriate metrics, benchmarks, and LLM-as-Judge patterns for both model quality and agent capability.
  **严格评估**——对模型质量和智能体能力应用适当的指标、基准和 LLM 即裁判模式。

### 本指南的组织结构（How This Guide Is Organized）
\label{how-this-guide-is-organized}

The guide spans 29 chapters organized in five parts:
本指南共 29 章，分为五个部分：

1. **Part I --- Foundations** (Chapters 1--3): LLM architecture and optimization (transformers, attention, positional encodings, Flash Attention, LoRA, MoE), systems foundations (GPU hierarchies, distributed training, vLLM), and classical RL theory (MDPs, policy gradients, actor-critic).
   **Part I —— 基础**（第 1–3 章）：LLM 架构与优化（Transformer、注意力、位置编码、Flash Attention、LoRA、MoE）、系统基础（GPU 层次结构、分布式训练、vLLM）和经典 RL 理论（MDP、策略梯度、Actor-Critic）。

2. **Part II --- RL Methods for LLMs** (Chapters 4--12): The complete RL-for-LLMs toolkit. RL foundations for language models, then full mathematical treatment of PPO, DPO, GRPO, and preference optimization variants (Online DPO, KTO, IPO, ORPO, SimPO), reward model training, SFT best practices, system architecture at scale, and agentic training with trajectory-level RL.
   **Part II —— LLM 的 RL 方法**（第 4–12 章）：完整的 LLM 强化学习工具包。语言模型的 RL 基础，然后全面数学处理 PPO、DPO、GRPO 及偏好优化变体（Online DPO、KTO、IPO、ORPO、SimPO）、奖励模型训练、SFT 最佳实践、大规模系统架构以及轨迹级 RL 的 Agentic 训练。

3. **Part III --- Reasoning** (Chapter 13): Large reasoning models --- DeepSeek-R1, OpenAI o1/o3/o4-mini, QwQ --- how RL discovers chain-of-thought, MCTS, process reward models, and test-time compute scaling.
   **Part III —— 推理**（第 13 章）：大型推理模型——DeepSeek-R1、OpenAI o1/o3/o4-mini、QwQ——RL 如何发现思维链、MCTS、过程奖励模型和测试时计算缩放。

4. **Part IV --- Evaluation** (Chapter 14): Comprehensive LLM evaluation methodology --- metrics, LLM-as-Judge, human annotation, benchmark suites, contamination detection, and agentic evaluation.
   **Part IV —— 评估**（第 14 章）：全面的 LLM 评估方法——指标、LLM 即裁判、人工标注、基准套件、污染检测和 Agentic 评估。

5. **Part V --- Agentic AI** (Chapters 15--26): The complete agentic stack --- introduction to agentic AI, RAG and retrieval, memory systems, orchestration and context management, design patterns, agentic environments and benchmarks, Model Context Protocol (MCP), agent skills, Agent-to-Agent communication (A2A), multi-agent systems, development frameworks, and agentic UI.
   **Part V —— Agentic AI**（第 15–26 章）：完整 Agentic 技术栈——Agentic AI 导论、RAG 与检索、记忆系统、编排与上下文管理、设计模式、Agentic 环境与基准、模型上下文协议（MCP）、智能体技能、智能体间通信（A2A）、多智能体系统、开发框架和 Agentic UI。

6. **Part VI --- Assessment \& Reference** (Chapters 27--29): 108 detailed quiz questions with comprehensive answers spanning all topics, a quick-reference chapter consolidating key equations, API references, and failure mode diagnostics, and a conclusion with future directions.
   **Part VI —— 评估与参考**（第 27–29 章）：108 道涵盖所有主题的详细测验题与全面解答，一个整合了关键公式、API 参考和故障诊断的速查章节，以及结论与未来方向。

The guide includes over 100 detailed quiz questions with comprehensive answers spanning all topics, plus a quick-reference chapter consolidating key equations, API references, and failure mode diagnostics.
本指南包含 100 多道涵盖所有主题的详细测验题与解答，以及一个整合关键公式、API 参考和故障诊断的速查章节。

### 设计理念（Design Philosophy）
\label{design-philosophy}

Three principles guide this document:
三个原则指导本文件：

1. **Intuition first, formalism second**. Every equation is preceded by a plain-English explanation of what it means and why it matters.
   **直觉优先，形式化第二**。每个公式之前都有通俗易懂的解释，说明其含义和重要性。

2. **Implementation-aware**. Theory is useless without knowing how to make it work. We include code, hyperparameter tables, memory budgets, architecture diagrams, and debugging strategies throughout.
   **注意实现**。不知道如何让理论工作，理论就是无用的。我们在全文中包含代码、超参数表、内存预算、架构图和调试策略。

3. **Honest about what works**. We clearly state which approaches are production-tested and which are research explorations.
   **诚实地说明什么可行**。我们明确说明哪些方法经过生产测试，哪些是研究探索。

### 范围与有意省略（Scope and Deliberate Omissions）
\label{scope-and-deliberate-omissions}

This guide focuses on **text-in, text-out language models** and the RL, systems, and agentic infrastructure built around them. Several important areas are intentionally excluded:
本指南聚焦于**文本输入、文本输出的语言模型**以及围绕它们构建的 RL、系统和 Agentic 基础设施。几个重要领域被有意排除：

- **Multimodal models** (vision--language, audio, video). Multimodal architectures introduce distinct training pipelines (contrastive pre-training, cross-modal alignment, modality-specific encoders), data curation challenges, and evaluation protocols that each merit book-length treatment. Including them would double the scope without deepening the RL and agentic core that unifies this guide.
  **多模态模型**（视觉-语言、音频、视频）。多模态架构引入了不同的训练流程（对比预训练、跨模态对齐、模态特定编码器）、数据策划挑战和评估协议，每一项都值得用一本书的篇幅来讨论。包含它们会使范围加倍，而不会加深统一本指南的 RL 和 Agentic 核心。

- **Domain-specific deployments** (healthcare, legal, finance, scientific discovery). Domain adaptation introduces regulatory constraints, specialized evaluation, and data-access issues that are orthogonal to the general methods presented here. The algorithms and architectures we cover *are* the building blocks practitioners adapt to these domains, but the adaptation details are better served by dedicated references.
  **特定领域部署**（医疗、法律、金融、科学发现）。领域适配引入了监管约束、专门评估和数据访问问题，这些问题与本文介绍的一般方法是正交的。我们涵盖的算法和架构*正是*实践者适应这些领域的构建块，但适配细节更适合由专门的参考资料处理。

- **Personalization and recommendation systems.** Personalization relies on user modeling, collaborative filtering, and interaction-history architectures that form a parallel research tradition. While LLMs are increasingly used *within* recommender systems, the core techniques (sequential models, bandit-based exploration, cold-start handling) are sufficiently distinct to warrant separate coverage.
  **个性化和推荐系统。** 个性化依赖于用户建模、协同过滤和交互历史架构，这些形成了平行的研究传统。虽然 LLM 越来越多地被用于推荐系统*内部*，但核心技术（序列模型、基于赌博机的探索、冷启动处理）足够不同，值得单独覆盖。

By maintaining this boundary, we keep a single coherent thread---*from architectural foundations and systems infrastructure, through the training algorithms that produce aligned and reasoning models, to the orchestration and deployment of autonomous agents*---without fragmenting the narrative across modalities and verticals.
通过保持这个边界，我们保持了一条连贯的主线——*从架构基础和系统基础设施，经过产生对齐和推理模型的训练算法，到自主智能体的编排和部署*——不会因跨模态和垂直领域而使叙述碎片化。

--- *Haggai Roitman, 2026*

---

## 引言（Introduction）
\label{introduction}

### 大图景（The Big Picture）
\label{the-big-picture}

This guide takes you from **first principles to production systems**. It is written for practitioners --- researchers, engineers, and applied scientists --- who want to understand and build the full stack of modern AI: from transformer architectures and the hardware that runs them, through the training algorithms that align models with human intent and teach them to reason, to the agentic architectures that deploy them as autonomous systems.
本指南带你从**第一原理到生产系统**。它面向实践者——研究员、工程师和应用科学家——他们希望理解和构建现代 AI 的完整技术栈：从 Transformer 架构及其运行的硬件，到使模型与人类意图对齐并教会它们推理的训练算法，再到将它们部署为自主系统的 Agentic 架构。

The core thesis is simple: *building great AI systems requires understanding the entire pipeline, not just one layer*. An engineer debugging a training run needs to understand GPU memory hierarchies and optimizer dynamics. A fine-tuning practitioner needs to know when LoRA suffices and when full-parameter training is worth the cost. An agent developer needs to understand how the underlying model was trained. A technical leader evaluating frameworks needs to understand what trade-offs each one makes. This guide provides that complete picture.
核心论点很简单：*构建优秀 AI 系统需要理解整个流水线，而不仅仅是一个层面*。调试训练运行的工程师需要理解 GPU 内存层次结构和优化器动态。微调实践者需要知道何时 LoRA 足够，何时全参数训练值得投入成本。智能体开发者需要理解底层模型是如何训练的。评估框架的技术领导者需要理解每种框架所做的权衡。这本指南提供了完整的图景。

### 通往 Agentic AI 之路：简史（The Road to Agentic AI: A Brief History）
\label{the-road-to-agentic-ai-a-brief-history}

Today's agentic AI systems did not emerge in a vacuum. They stand on decades of milestone systems --- each solving a narrower problem but collectively building the techniques, hardware, and ambition that made autonomous agents possible.
今天的 Agentic AI 系统并非凭空出现。它们建立在数十年的里程碑式系统之上——每个系统解决一个较窄的问题，但共同构建了使自主智能体成为可能的技术、硬件和雄心。

1. **Deep Blue (1997)** [Campbell 2002] --- IBM's chess engine defeated world champion Garry Kasparov using brute-force search (200 million positions/second) with handcrafted evaluation functions. It proved machines could exceed human performance in well-defined adversarial domains, but generalized to nothing else.
   **深蓝（1997）** [Campbell 2002]——IBM 的国际象棋引擎使用暴力搜索（每秒 2 亿个局面）和手工评估函数击败了世界冠军卡斯帕罗夫。它证明了机器可以在明确定义的对抗领域超越人类表现，但无法推广到其他任何领域。

2. **IBM Watson --- Jeopardy! (2011)** [Ferrucci 2010] --- Watson combined information retrieval, NLP, and massive parallelism to defeat human champions at open-domain question answering. It demonstrated that AI could process unstructured text at scale, but required years of domain-specific engineering and couldn't learn new domains without substantial human effort.
   **IBM Watson —— 危险边缘！（2011）** [Ferrucci 2010]——Watson 结合了信息检索、NLP 和大规模并行计算，在开放领域的问答中击败了人类冠军。它证明了 AI 可以大规模处理非结构化文本，但需要多年的领域特定工程，且无法在不投入大量人力的情况下学习新领域。

3. **AlexNet and the Deep Learning Revolution (2012)** [Krizhevsky 2012] --- Krizhevsky et al.'s CNN won ImageNet by a stunning margin, proving that deep neural networks trained on GPUs could learn representations from raw data. This single result triggered the modern deep learning era and the hardware investment that eventually made LLMs possible.
   **AlexNet 与深度学习革命（2012）** [Krizhevsky 2012]——Krizhevsky 等人的 CNN 以惊人的优势赢得了 ImageNet，证明了在 GPU 上训练的深度神经网络可以从原始数据中学习表示。这一结果引发了现代深度学习时代和最终使 LLM 成为可能的硬件投资。

4. **AlphaGo (2016)** [Silver 2016] --- DeepMind's system defeated Go world champion Lee Sedol using deep RL (policy networks + value networks + Monte Carlo Tree Search). Unlike Deep Blue's brute force, AlphaGo *learned* to play---demonstrating that RL could master domains where search alone was intractable ($10^{170}$ board states). AlphaGo Zero (2017) [Silver 2017] later learned entirely from self-play, needing no human games at all.
   **AlphaGo（2016）** [Silver 2016]——DeepMind 的系统使用深度 RL（策略网络 + 价值网络 + 蒙特卡洛树搜索）击败了围棋世界冠军李世石。与深蓝的暴力搜索不同，AlphaGo *学会*了下棋——证明了 RL 可以掌握仅靠搜索无法处理的领域（$10^{170}$ 个棋盘状态）。AlphaGo Zero（2017）[Silver 2017] 后来完全通过自对弈学习，完全不需要人类棋谱。

5. **GPT-2/GPT-3 (2019--2020)** [Brown 2020] --- OpenAI showed that scaling decoder-only transformers to billions of parameters produced emergent few-shot learning. GPT-3 (175B parameters) could perform tasks it was never explicitly trained for---translation, arithmetic, code generation---simply from in-context examples. The era of foundation models began.
   **GPT-2/GPT-3（2019–2020）** [Brown 2020]——OpenAI 展示了将纯解码器 Transformer 扩展到数十亿参数可以产生涌现的少样本学习能力。GPT-3（175B 参数）可以执行从未明确训练过的任务——翻译、算术、代码生成——仅仅通过上下文中的示例。基础模型时代开始了。

6. **AlphaFold (2020)** [Jumper 2021] --- DeepMind solved the 50-year protein folding problem, predicting 3D protein structures with atomic accuracy. AlphaFold demonstrated that deep learning could crack fundamental scientific problems previously considered decades away. It also showcased the power of architecture innovation (attention over residue pairs) combined with massive compute.
   **AlphaFold（2020）** [Jumper 2021]——DeepMind 解决了长达 50 年的蛋白质折叠问题，以原子精度预测了 3D 蛋白质结构。AlphaFold 证明了深度学习可以攻克此前被认为几十年后才能解决的基础科学问题。它还展示了架构创新（残基对上的注意力）与大规模计算相结合的力量。

7. **ChatGPT and RLHF (2022)** [Ouyang 2022] --- InstructGPT/ChatGPT proved that a capable base model, when aligned via RLHF, becomes a genuinely useful assistant. This was the inflection point: AI went from a research tool to a consumer product used by hundreds of millions. The alignment techniques (reward models, PPO) became the template for all subsequent LLM post-training.
   **ChatGPT 与 RLHF（2022）** [Ouyang 2022]——InstructGPT/ChatGPT 证明了一个有能力的基座模型，当通过 RLHF 对齐后，变成了一个真正有用的助手。这是一个转折点：AI 从研究工具变成了数亿人使用的消费产品。对齐技术（奖励模型、PPO）成为所有后续 LLM 后训练的模板。

8. **GPT-4 and Multimodal Models (2023)** [OpenAI 2023] --- Multimodal capabilities (vision + language), longer contexts, and improved reasoning pushed LLMs toward general-purpose cognition. Tool use (code interpreter, web browsing) hinted at agentic capabilities.
   **GPT-4 与多模态模型（2023）** [OpenAI 2023]——多模态能力（视觉 + 语言）、更长的上下文和改进的推理将 LLM 推向了通用认知。工具使用（代码解释器、网页浏览）暗示了 Agentic 能力。

9. **Reasoning Models (2024)** [DeepSeek 2025] --- OpenAI's o1 and DeepSeek-R1 showed that RL could teach models to *reason*: chain-of-thought, backtracking, self-verification emerged spontaneously from reward signals alone. Models began solving competition-level mathematics and complex coding tasks.
   **推理模型（2024）** [DeepSeek 2025]——OpenAI 的 o1 和 DeepSeek-R1 表明 RL 可以教会模型*推理*：思维链、回溯、自我验证仅从奖励信号中自发涌现。模型开始解决竞赛级别的数学和复杂编码任务。

10. **Agentic AI (2025--present)** --- The convergence point: LLMs with reasoning capabilities, equipped with standardized tool access (MCP), inter-agent communication (A2A), persistent memory, and sophisticated orchestration frameworks. Agents now autonomously write code, conduct research, manage workflows, and coordinate with other agents---the subject of this guide.
    **Agentic AI（2025–至今）**——汇聚点：具有推理能力的 LLM，配备标准化工具访问（MCP）、智能体间通信（A2A）、持久记忆和复杂的编排框架。智能体现在自主编写代码、进行研究、管理工作流以及与其他智能体协调——这正是本指南的主题。

\begin{intuitionbox}
Each milestone shares a common arc: **architecture innovation** $+$ **scale** $+$ **learning signal** $=$ **breakthrough**. Deep Blue used handcrafted search. AlphaGo learned from self-play. GPT-3 learned from internet text. Today's agentic systems learn from human feedback, verifiable rewards, and environment interaction. The learning signal has expanded from game outcomes to open-ended human preferences---and the architectures have grown to match.
每个里程碑都遵循相同的路径：**架构创新** $+$ **规模** $+$ **学习信号** $=$ **突破**。深蓝使用手工搜索；AlphaGo 通过自对弈学习；GPT-3 从互联网文本学习。今天的 Agentic 系统从人类反馈、可验证奖励和环境交互中学习。学习信号已从游戏结果扩展到开放式的人类偏好——架构也随之成长。
\end{intuitionbox}

This guide picks up the story at the foundation model era and carries it forward through alignment, reasoning, and autonomous agency.
本指南从基础模型时代开始讲述，并通过对齐、推理和自主智能体向前推进。

### 你应该期待什么（What You Should Expect）
\label{what-you-should-expect}

**Part I: Foundations** (Chapters 1--3) builds the base knowledge the rest of the guide depends on. We start with how LLMs work internally --- the architecture decisions that determine capability --- then cover the hardware and systems that make training and inference possible, and finally introduce reinforcement learning from first principles.
**Part I：基础**（第 1–3 章）构建了指南其余部分依赖的基础知识。我们从 LLM 如何内部工作开始——决定能力的架构决策——然后涵盖使训练和推理成为可能的硬件和系统，最后从第一原理介绍强化学习。

- **Chapter 1 --- LLM Architecture and Optimization**: Transformer internals (self-attention, multi-head attention, RoPE, GQA), Flash Attention, optimization methods (AdamW, learning rate schedules, gradient clipping), mixed precision, LoRA/QLoRA, quantization, knowledge distillation, and Mixture of Experts.
  **第 1 章 —— LLM 架构与优化**：Transformer 内部原理（自注意力、多头注意力、RoPE、GQA）、Flash Attention、优化方法（AdamW、学习率调度、梯度裁剪）、混合精度、LoRA/QLoRA、量化、知识蒸馏和混合专家。

- **Chapter 2 --- Systems Foundations**: GPU architecture (A100/H100/B200), memory hierarchies, NVLink/NVSwitch, distributed training (FSDP, DeepSpeed ZeRO, tensor/pipeline parallelism), and vLLM for high-throughput inference.
  **第 2 章 —— 系统基础**：GPU 架构（A100/H100/B200）、内存层次结构、NVLink/NVSwitch、分布式训练（FSDP、DeepSpeed ZeRO、张量/流水线并行）以及用于高吞吐推理的 vLLM。

- **Chapter 3 --- Introduction to RL**: MDPs, Bellman equations, TD learning, Q-learning, policy gradients (REINFORCE), actor-critic methods, GAE --- the algorithmic toolkit that underpins Part II.
  **第 3 章 —— RL 导论**：MDP、Bellman 方程、TD 学习、Q 学习、策略梯度（REINFORCE）、Actor-Critic 方法、GAE——支撑 Part II 的算法工具包。

**Part II: RL Methods for LLMs** (Chapters 4--12) is the training and alignment core. Here you learn how to align, improve, and fine-tune language models --- from full mathematical derivations to working code.
**Part II：LLM 的 RL 方法**（第 4–12 章）是训练和对齐核心。在这里你将学习如何对齐、改进和微调语言模型——从完整的数学推导到可工作的代码。

- **Chapters 4--8**: Every major RL/preference algorithm with math, intuition, and TRL code --- PPO, DPO, GRPO, and preference optimization variants (Online DPO, KTO, IPO, ORPO, SimPO, Best-of-N).
  **第 4–8 章**：每个主要的 RL/偏好算法及其数学、直觉和 TRL 代码——PPO、DPO、GRPO 及偏好优化变体（Online DPO、KTO、IPO、ORPO、SimPO、Best-of-N）。

- **Chapters 9--10**: Reward model training (Bradley--Terry, scaling laws, reward hacking) and SFT best practices (data quality, curriculum, formatting).
  **第 9–10 章**：奖励模型训练（Bradley–Terry、缩放定律、奖励黑客）和 SFT 最佳实践（数据质量、课程、格式化）。

- **Chapters 11--12**: System architecture at scale (decoupled training, fault tolerance, GPU allocation) and LLM agentic training --- how to train agents end-to-end with trajectory-level RL.
  **第 11–12 章**：大规模系统架构（解耦训练、容错、GPU 分配）和 LLM Agentic 训练——如何使用轨迹级 RL 端到端训练智能体。

**Part III: Reasoning** (Chapter 13) covers the frontier of model capability --- teaching LLMs to reason through multi-step problems.
**Part III：推理**（第 13 章）涵盖了模型能力的前沿——教会 LLM 通过多步问题进行推理。

- **Chapter 13 --- RL for Large Reasoning Models**: DeepSeek-R1, OpenAI o1/o3/o4-mini, QwQ --- how RL discovers chain-of-thought, MCTS, process reward models, and test-time compute scaling.
  **第 13 章 —— 大型推理模型的 RL**：DeepSeek-R1、OpenAI o1/o3/o4-mini、QwQ——RL 如何发现思维链、MCTS、过程奖励模型和测试时计算缩放。

**Part IV: Evaluation** (Chapter 14) provides the methodology for measuring whether any of this actually works.
**Part IV：评估**（第 14 章）提供了衡量这些是否真正起作用的方法论。

- **Chapter 14 --- LLM Evaluation**: Metrics (perplexity, pass@k, ELO), LLM-as-Judge patterns, contamination detection, benchmark suites, and agentic evaluation methodology.
  **第 14 章 —— LLM 评估**：指标（困惑度、pass@k、ELO）、LLM 即裁判模式、污染检测、基准套件和 Agentic 评估方法。

**Part V: Agentic AI** (Chapters 15--26) takes you from a trained model to a deployed autonomous system. This is the largest part, covering everything an agent needs to operate in the real world.
**Part V：Agentic AI**（第 15–26 章）带你从训练好的模型到部署的自主系统。这是最大的部分，涵盖了智能体在现实世界中运行所需的一切。

- **Chapter 15 --- Introduction to Agentic AI**: What makes a system agentic, the spectrum from chatbots to autonomous agents, and the foundational concepts for the rest of Part V.
  **第 15 章 —— Agentic AI 导论**：什么让系统具有 Agent 性，从聊天机器人到自主智能体的谱系，以及 Part V 其余部分的基础概念。

- **Chapter 16 --- RAG**: Retrieval methods, chunking, embedding models, hybrid search, reranking, and production architectures.
  **第 16 章 —— RAG**：检索方法、分块、嵌入模型、混合搜索、重排序和生产架构。

- **Chapter 17 --- Memory Systems**: Working, episodic, semantic, and procedural memory for persistent agent knowledge.
  **第 17 章 —— 记忆系统**：用于持久智能体知识的工作记忆、情景记忆、语义记忆和程序记忆。

- **Chapter 18 --- Orchestration**: ReAct, Plan-and-Execute, LLM Compiler, reflexion patterns, context management, and harness design.
  **第 18 章 —— 编排**：ReAct、Plan-and-Execute、LLM Compiler、反思模式、上下文管理和 Harness 设计。

- **Chapter 19 --- Design Patterns**: Prompt chaining, routing, parallelization, evaluation-driven orchestration, and the simplicity principle.
  **第 19 章 —— 设计模式**：提示词链、路由、并行化、评估驱动的编排和简约原则。

- **Chapter 20 --- Environments and Benchmarks**: WebArena, SWE-bench, OSWorld, GAIA --- evaluation environments for agentic capability.
  **第 20 章 —— 环境与基准**：WebArena、SWE-bench、OSWorld、GAIA——用于 Agentic 能力评估的环境。

- **Chapter 21 --- Model Context Protocol (MCP)**: Architecture, transport layers, tool/resource/prompt primitives, security, and deployment.
  **第 21 章 —— 模型上下文协议（MCP）**：架构、传输层、工具/资源/提示原语、安全和部署。

- **Chapter 22 --- Agent Skills**: Skill libraries, tool composition, and capability abstraction.
  **第 22 章 —— 智能体技能**：技能库、工具组合和能力抽象。

- **Chapter 23 --- A2A Communication**: Google's Agent-to-Agent protocol --- Agent Cards, task lifecycle, streaming, enterprise patterns.
  **第 23 章 —— A2A 通信**：Google 的 Agent-to-Agent 协议——Agent Cards、任务生命周期、流式传输、企业模式。

- **Chapter 24 --- Multi-Agent Systems**: Hierarchical, debate, marketplace, and swarm architectures --- coordination at scale.
  **第 24 章 —— 多智能体系统**：层次化、辩论、市场和群体架构——大规模协调。

- **Chapter 25 --- Development Frameworks**: LangGraph, CrewAI, AutoGen, OpenAI Agents SDK, Google ADK --- comparative analysis with code.
  **第 25 章 —— 开发框架**：LangGraph、CrewAI、AutoGen、OpenAI Agents SDK、Google ADK——包含代码的比较分析。

- **Chapter 26 --- Agentic UI**: Streaming interfaces, generative UI, canvas paradigms, tool visualization, human-in-the-loop patterns.
  **第 26 章 —— Agentic 用户界面**：流式接口、生成式 UI、Canvas 范式、工具可视化、人在回路模式。

### 现代 AI 流水线（The Modern AI Pipeline）
\label{the-modern-ai-pipeline}

The full pipeline from base model to deployed agent:
从基础模型到部署智能体的完整流水线：

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_001_pipeline.png}
\caption{The modern LLM development pipeline: from pre-trained base model through alignment and reasoning to autonomous agentic capability. Each stage maps to a part of this guide.}
\label{fig:pipeline}
\end{figure}

*图：现代 LLM 开发流水线：从预训练基础模型经过对齐和推理到自主 Agentic 能力。每个阶段对应本指南的一个部分。*

---
*Part I: Foundations / 第一部分：基础*