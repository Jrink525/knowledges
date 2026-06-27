# The Hitchhiker's Guide to Agentic AI: From Foundations to Systems
# 漫游星际的智能体人工智能指南：从基础到系统

**作者：** Haggai Roitman，2026，版本 1.2.2

---

# 免责声明

This document is an independent survey and educational resource prepared solely by the author. The views, opinions, and conclusions expressed herein are those of the author alone and do not necessarily reflect the views of any employer, organization, or institution with which the author is or has been affiliated.

本文档是由作者独立编写的综述和教育资源。文中表达的观点、意见和结论仅代表作者本人，并不一定反映作者现在或曾经所属的任何雇主、组织或机构的观点。

This work does not contain any proprietary, confidential, or trade-secret information. All referenced material is drawn from publicly available sources, including peer-reviewed publications, open-access preprints, official documentation, and open-source repositories.

本作品不包含任何专有、机密或商业秘密信息。所有参考材料均来自公开来源，包括同行评审出版物、开放获取预印本、官方文档和开源仓库。

The content is provided "as is" without warranty of any kind, express or implied. The author makes no representations regarding the accuracy, completeness, or suitability of the information for any particular purpose. Readers should independently verify any claims, formulas, or implementation details before applying them in production systems.

本内容按"原样"提供，不附带任何明示或暗示的担保。作者不对信息的准确性、完整性或适用于任何特定目的做出任何陈述。读者应在生产系统中应用任何声明、公式或实现细节之前，独立核实它们。

**Feedback welcome.** If you find any mistakes, inaccuracies, or have suggestions for improvement, you are encouraged to send feedback to \texttt{[first\_name]r@gmail.com}.

**欢迎反馈。** 如果您发现任何错误、不准确之处或有改进建议，请发送反馈至 \texttt{[first\_name]r@gmail.com}。

**AI Disclosure.** Large language models were used as a research and drafting aid. All content was edited and verified by the author on a best-effort basis.

**AI 披露声明。** 大型语言模型被用作研究和起草辅助工具。所有内容均由作者在尽力而为的基础上进行编辑和核实。

**License.** This work is licensed under the \textbf{Creative Commons Attribution-ShareAlike 4.0 International License} (CC~BY-SA~4.0). You are free to share (copy and redistribute) and adapt (remix, transform, and build upon) this material for any purpose, including commercially, provided you give appropriate credit, provide a link to the license, indicate if changes were made, and distribute any derivative works under the same license. Full license text: \href{https://creativecommons.org/licenses/by-sa/4.0/}{https://creativecommons.org/licenses/by-sa/4.0/}.

**许可协议。** 本作品采用 \textbf{知识共享署名-相同方式共享 4.0 国际许可协议}（CC~BY-SA~4.0）授权。您可以自由地共享（复制和重新分发）以及改编（混编、转换和在此基础上构建）本材料用于任何目的，包括商业用途，前提是您提供适当的署名、提供许可协议链接、注明是否做出修改，并在相同的许可协议下分发衍生作品。完整许可协议文本：\href{https://creativecommons.org/licenses/by-sa/4.0/}{https://creativecommons.org/licenses/by-sa/4.0/}。

---

# 关于作者

**Haggai Roitman** has spent over two decades at the intersection of AI research and large-scale production systems. His work bridges theory and practice---from publishing foundational research to shipping systems that serve millions of users.

**Haggai Roitman** 在 AI 研究与大规模生产系统的交叉领域深耕了二十余年。他的工作连接了理论与实践——从发表基础研究到交付服务数百万用户的系统。

His research interests span information retrieval, recommender systems, natural language processing, large language models, reinforcement learning for LLMs, and agentic AI. He has authored more than 100 peer-reviewed publications and holds approximately 100 patents. He earned his BSc (\emph{Cum Laude}) and PhD from the Technion --- Israel Institute of Technology.

他的研究兴趣涵盖信息检索、推荐系统、自然语言处理、大型语言模型、面向 LLM 的强化学习以及智能体 AI。他撰写了 100 多篇同行评审出版物，并拥有约 100 项专利。他在以色列理工学院——以色列理工学院获得了学士学位（\emph{优等成绩}）和博士学位。

When not thinking about gradient flows and KV caches, he can be found behind a set of turntables, mixing progressive trance and deep house.

当不思考梯度流动和 KV 缓存时，你可以在唱盘机后面找到他，混音着渐进迷幻和深屋音乐。

---

# 序言

## 这本指南为何存在

Building intelligent AI systems in 2026 requires mastering an extraordinary breadth of knowledge --- from how transformers process language internally, through the hardware and systems that make training possible, the optimization techniques that make it efficient, the reinforcement learning algorithms that teach models to reason and align with human intent, all the way to multi-agent architectures that coordinate autonomous systems at scale.

在 2026 年构建智能 AI 系统需要掌握极其广泛的知识——从 Transformer 如何在内部处理语言，到使其训练成为可能的硬件和系统，再到使其高效运行的优化技术，以及教导模型进行推理并与人类意图对齐的强化学习算法，一直到协调大规模自主系统的多智能体架构。

This knowledge is scattered across hundreds of papers, blog posts, GitHub repositories, and tribal knowledge within a handful of labs. This guide exists because \textbf{practitioners need a single, unified reference} that covers the entire stack --- not just the theory, but the implementation details that make things actually work.

这些知识分散在数百篇论文、博客文章、GitHub 仓库以及少数实验室中的隐性知识中。这本指南的存在是因为 \textbf{实践者需要一个统一的参考}来覆盖整个技术栈——不仅仅是理论，还有让事情真正起作用的实现细节。

## 走向智能体 AI 的个人旅程

My fascination with intelligent agents began two decades ago, when I still studied for my first degree in information systems engineering. I took courses on Agent-Oriented Software Engineering (AOSE)~\cite{wooldridge2000gaia} and learned to build multi-agent systems using JADE~\cite{bellifemine2007jade} (Java Agent DEvelopment Framework)---a FIPA-compliant~\cite{fipa2002acl} platform where agents communicated via structured protocols, negotiated over shared resources, and coordinated autonomously. Around the same time, Berners-Lee, Hendler, and Lassila's seminal paper "The Semantic Web"~\cite{bernerslee2001semantic} painted a vision of machine-readable knowledge that agents could reason over. These two threads---autonomous agent architectures and semantic knowledge representation---planted a seed that has guided my career ever since. One early project that crystallized this vision was an attempt to build a \emph{shopping agent}---developed with OntoBuilder~\cite{gal2006ontobuilder} under the guidance of my respected future academic advisor Prof.~Avigdor Gal---a system that could automatically fill product search queries and orders across different heterogeneous websites, understanding their varied schemas through ontology matching and mapping. The Semantic Web promised that such agents would thrive in a world of structured, machine-readable data. In practice, the brittleness of hand-crafted ontologies, the messiness of real-world product data, and the lack of robust natural language understanding made the vision perpetually "five years away."

我对智能体的迷恋始于二十年前，当时我还在攻读信息系统工程的第一学位。我学习了面向智能体的软件工程（Agent-Oriented Software Engineering, AOSE）~\cite{wooldridge2000gaia}课程，并学会了使用 JADE~\cite{bellifemine2007jade}（Java Agent DEvelopment Framework）构建多智能体系统——这是一个符合 FIPA 标准~\cite{fipa2002acl}的平台，智能体通过结构化协议进行通信，就共享资源进行协商，并自主协调。大约在同一时间，Berners-Lee、Hendler 和 Lassila 的开创性论文"语义网"~\cite{bernerslee2001semantic}描绘了一个智能体可在其上推理的机器可读知识的愿景。这两条线索——自主智能体架构和语义知识表示——播下了一颗种子，至今指引着我的职业生涯。一个具体化了这一愿景的早期项目是尝试构建一个\emph{购物智能体}——在未来的学术导师 Avigdor Gal 教授的指导下，使用 OntoBuilder~\cite{gal2006ontobuilder}开发——一个能够自动在不同异构网站上填写产品搜索查询和订单的系统，通过本体匹配和映射理解它们各自不同的模式。语义网曾承诺这样的智能体将在结构化、机器可读数据的世界中蓬勃发展。但实践中，手工构建本体的脆弱性、真实世界产品数据的混乱以及缺乏鲁棒的自然语言理解，使得这个愿景永远"还有五年。"

Over the following years, I tracked each wave of AI progress as it arrived: neural networks and heuristic search for combinatorial optimization; deep learning and representation learning; information retrieval and personalization at scale; and most recently, the revolution of large language models. Each wave brought powerful new tools, but the dream remained the same: systems that \emph{understand}, \emph{reason}, and \emph{act} autonomously in complex environments.

在接下来的几年里，我追踪了每一波 AI 进步的浪潮：用于组合优化的神经网络和启发式搜索；深度学习和表示学习；大规模信息检索和个性化；以及最近的大型语言模型革命。每一波浪潮都带来了强大的新工具，但梦想始终如一：能够\emph{理解}、\emph{推理}并\emph{行动}于复杂环境中的自主系统。

What makes 2024--2026 remarkable is that these threads have finally converged. LLMs provide the language understanding and generation; reinforcement learning teaches them to reason and align with human intent; tool-use protocols (MCP) give them hands to act in the world; and agent orchestration frameworks provide the coordination layer that JADE envisioned twenty years ago---now powered by foundation models instead of hand-coded ontologies. This guide is, in many ways, the reference I wish I had at each step of that journey.

2024--2026 年的非凡之处在于这些线索终于汇聚了。LLM 提供了语言理解和生成能力；强化学习教会它们推理并与人类意图对齐；工具使用协议（MCP）赋予了它们在世界中行动的能力；而智能体编排框架提供了 JADE 二十年前就设想的协调层——现在由基础模型驱动，而不是手写编码的本体。这本指南在很多方面都是我希望在那段旅程的每一步都能拥有的参考。

## 2026 年的格局

The journey to today's agentic AI systems spans three decades of compounding breakthroughs across architecture, training, and deployment:

通往当今智能体 AI 系统的旅程跨越了三十年，在架构、训练和部署方面积累了众多突破：

\begin{enumerate}
  \item \textbf{Architectural foundations (2017--2020)}: The Transformer~\cite{vaswani2017attention} introduced self-attention as a universal sequence-processing primitive. Scaling laws revealed that larger models trained on more data reliably improve. GPT-2 and GPT-3 demonstrated that decoder-only transformers, scaled sufficiently, become capable few-shot learners.
  \item \textbf{架构基础（2017--2020）}：Transformer~\cite{vaswani2017attention} 引入了自注意力作为通用的序列处理原语。缩放定律揭示，在更多数据上训练更大的模型可以可靠地提高性能。GPT-2 和 GPT-3 证明，充分扩展的解码器专用 Transformer 能够成为出色的少样本学习器。
  \item \textbf{Systems and efficiency (2020--2023)}: Flash Attention~\cite{dao2022flashattention} made training 2--4$\times$ faster by eliminating memory bottlenecks. LoRA~\cite{hu2022lora} enabled fine-tuning 70B+ models on a single node. Mixture-of-Experts (MoE) decoupled model capacity from compute cost. Inference engines like vLLM brought throughput within reach of real-time applications.
  \item \textbf{系统与效率（2020--2023）}：Flash Attention~\cite{dao2022flashattention} 通过消除内存瓶颈使训练速度提升 2--4$\times$。LoRA~\cite{hu2022lora} 使在单节点微调 700 亿参数以上的模型成为可能。混合专家（Mixture-of-Experts, MoE）将模型容量与计算成本解耦。像 vLLM 这样的推理引擎使吞吐量达到了实时应用的水平。
  \item \textbf{Alignment via RL (2022--2024)}: RLHF~\cite{ouyang2022training} transformed capable-but-unhelpful base models into useful assistants --- the recipe behind ChatGPT. DPO~\cite{rafailov2023direct} collapsed the reward model and RL loop into a single supervised loss, democratizing alignment. Variants proliferated: KTO~\cite{ethayarajh2024kto}, IPO~\cite{azar2024general}, ORPO~\cite{hong2024orpo}, GRPO~\cite{shao2024deepseekmath}.
  \item \textbf{通过 RL 进行对齐（2022--2024）}：RLHF~\cite{ouyang2022training} 将有能力但不实用的基础模型转变为有用的助手——这是 ChatGPT 背后的配方。DPO~\cite{rafailov2023direct} 将奖励模型和 RL 循环压缩为单一的监督损失，使对齐民主化。各种变体不断涌现：KTO~\cite{ethayarajh2024kto}、IPO~\cite{azar2024general}、ORPO~\cite{hong2024orpo}、GRPO~\cite{shao2024deepseekmath}。
  \item \textbf{Reasoning and autonomy (2024--2026)}: DeepSeek-R1~\cite{deepseek2025r1} and OpenAI's o1/o3 demonstrated that RL could teach \emph{reasoning itself} --- models spontaneously discover chain-of-thought, backtracking, and self-verification. Simultaneously, the Model Context Protocol (MCP) standardized tool access, Agent-to-Agent (A2A) enabled inter-agent communication, and production-grade orchestration frameworks matured.
  \item \textbf{推理与自主性（2024--2026）}：DeepSeek-R1~\cite{deepseek2025r1} 和 OpenAI 的 o1/o3 证明，RL 可以教会\emph{推理本身}——模型自发地发现了思维链、回溯和自我验证。同时，模型上下文协议（Model Context Protocol, MCP）标准化了工具访问，智能体间通信协议（Agent-to-Agent, A2A）实现了智能体间通信，生产级编排框架也趋于成熟。
\end{enumerate}

## 这本指南适合谁

This document is written for \textbf{practitioners who build things}:

本文档是为\textbf{构建东西的实践者}而写的：

\begin{itemize}
  \item \textbf{ML engineers} who need to understand transformer internals, training infrastructure, optimization, and why things diverge.
  \item \textbf{机器学习工程师}——需要了解 Transformer 内部机制、训练基础设施、优化以及为什么会发散。
  \item \textbf{Applied researchers} evaluating architectures, fine-tuning strategies, and RL methods for their specific domains.
  \item \textbf{应用研究人员}——为其特定领域评估架构、微调策略和 RL 方法。
  \item \textbf{Agent developers} building production systems who need orchestration patterns, memory architectures, tool integration (MCP), and multi-agent coordination (A2A).
  \item \textbf{智能体开发者}——构建生产系统，需要编排模式、记忆架构、工具集成（MCP）和多智能体协调（A2A）。
  \item \textbf{Systems engineers} responsible for training infrastructure, GPU clusters, distributed training, and inference deployment.
  \item \textbf{系统工程师}——负责训练基础设施、GPU 集群、分布式训练和推理部署。
  \item \textbf{Technical leaders} making architectural and resourcing decisions across the full stack.
  \item \textbf{技术领导者}——做出贯穿整个技术栈的架构和资源决策。
\end{itemize}

We assume familiarity with neural networks and basic probability. \textbf{No prior LLM, RL, or systems knowledge is required} --- the guide builds from first principles.

我们假设读者熟悉神经网络和基本概率。\textbf{不需要事先了解 LLM、RL 或系统知识}——本指南从第一性原理开始构建。

## 你将获得什么

After reading this guide, you will be able to:

阅读本指南后，你将能够：

\begin{itemize}
  \item \textbf{Understand LLM internals} --- attention mechanisms, positional encodings, MoE routing, Flash Attention, and why architectural choices matter for downstream capability.
  \item \textbf{理解 LLM 内部机制}——注意力机制、位置编码、MoE 路由、Flash Attention，以及架构选择为何对下游能力至关重要。
  \item \textbf{Reason about systems} --- GPU memory budgets, distributed training strategies (FSDP, tensor/pipeline parallelism), inference optimization, and production deployment with vLLM.
  \item \textbf{系统推理能力}——GPU 内存预算、分布式训练策略（FSDP、张量/管道并行）、推理优化以及使用 vLLM 进行生产部署。
  \item \textbf{Train and fine-tune efficiently} --- LoRA/QLoRA, quantization, knowledge distillation, optimizer selection, and learning rate scheduling.
  \item \textbf{高效训练和微调}——LoRA/QLoRA、量化、知识蒸馏、优化器选择和学习率调度。
  \item \textbf{Align models with human preferences} --- implement RLHF/DPO/GRPO/KTO pipelines, debug reward hacking and mode collapse, choose the right algorithm among 20+ methods.
  \item \textbf{使模型与人类偏好对齐}——实现 RLHF/DPO/GRPO/KTO 流水线，调试奖励黑客和模式坍塌，在 20 多种方法中选择正确的算法。
  \item \textbf{Build reasoning models} --- understand how DeepSeek-R1, o1/o3, and QwQ discover chain-of-thought through RL without explicit demonstrations.
  \item \textbf{构建推理模型}——理解 DeepSeek-R1、o1/o3 和 QwQ 如何在没有显式示范的情况下通过 RL 发现思维链。
  \item \textbf{Architect agentic systems} --- select orchestration patterns, design memory, integrate tools via MCP, coordinate agents via A2A, evaluate with production benchmarks.
  \item \textbf{架构智能体系统}——选择编排模式、设计记忆、通过 MCP 集成工具、通过 A2A 协调智能体、使用生产基准进行评估。
  \item \textbf{Evaluate rigorously} --- apply appropriate metrics, benchmarks, and LLM-as-Judge patterns for both model quality and agent capability.
  \item \textbf{严格评估}——应用适当的指标、基准和 LLM-as-Judge 模式来评估模型质量和智能体能力。
\end{itemize}

## 本指南的组织方式

The guide spans 29 chapters organized in five parts:

本指南涵盖 29 章，分为五个部分：

\begin{enumerate}
  \item \textbf{Part I --- Foundations} (Chapters 1--3): LLM architecture and optimization (transformers, attention, positional encodings, Flash Attention, LoRA, MoE), systems foundations (GPU hierarchies, distributed training, vLLM), and classical RL theory (MDPs, policy gradients, actor-critic).
  \item \textbf{第一部分——基础}（第 1--3 章）：LLM 架构与优化（Transformer、注意力、位置编码、Flash Attention、LoRA、MoE）、系统基础（GPU 层次结构、分布式训练、vLLM）和经典 RL 理论（MDP、策略梯度、Actor-Critic）。
  \item \textbf{Part II --- RL Methods for LLMs} (Chapters 4--12): The complete RL-for-LLMs toolkit. RL foundations for language models, then full mathematical treatment of PPO, DPO, GRPO, and preference optimization variants (Online DPO, KTO, IPO, ORPO, SimPO), reward model training, SFT best practices, system architecture at scale, and agentic training with trajectory-level RL.
  \item \textbf{第二部分——面向 LLM 的 RL 方法}（第 4--12 章）：完整的 LLM 强化学习工具包。语言模型的 RL 基础，然后对 PPO、DPO、GRPO 和偏好优化变体（Online DPO、KTO、IPO、ORPO、SimPO）进行完整的数学处理、奖励模型训练、SFT 最佳实践、大规模系统架构以及使用轨迹级 RL 进行智能体训练。
  \item \textbf{Part III --- Reasoning} (Chapter 13): Large reasoning models --- DeepSeek-R1, OpenAI o1/o3/o4-mini, QwQ --- how RL discovers chain-of-thought, MCTS, process reward models, and test-time compute scaling.
  \item \textbf{第三部分——推理}（第 13 章）：大型推理模型——DeepSeek-R1、OpenAI o1/o3/o4-mini、QwQ——RL 如何发现思维链、蒙特卡洛树搜索、过程奖励模型和测试时计算扩展。
  \item \textbf{Part IV --- Evaluation} (Chapter 14): Comprehensive LLM evaluation methodology --- metrics, LLM-as-Judge, human annotation, benchmark suites, contamination detection, and agentic evaluation.
  \item \textbf{第四部分——评估}（第 14 章）：全面的 LLM 评估方法——指标、LLM-as-Judge、人工标注、基准测试套件、污染检测和智能体评估。
  \item \textbf{Part V --- Agentic AI} (Chapters 15--26): The complete agentic stack --- introduction to agentic AI, RAG and retrieval, memory systems, orchestration and context management, design patterns, agentic environments and benchmarks, Model Context Protocol (MCP), agent skills, Agent-to-Agent communication (A2A), multi-agent systems, development frameworks, and agentic UI.
  \item \textbf{第五部分——智能体 AI}（第 15--26 章）：完整的智能体技术栈——智能体 AI 简介、RAG 与检索、记忆系统、编排与上下文管理、设计模式、智能体环境与基准、模型上下文协议（MCP）、智能体技能、智能体间通信（A2A）、多智能体系统、开发框架和智能体 UI。
  \item \textbf{Part VI --- Assessment \& Reference} (Chapters 27--29): 108 detailed quiz questions with comprehensive answers spanning all topics, a quick-reference chapter consolidating key equations, API references, and failure mode diagnostics, and a conclusion with future directions.
  \item \textbf{第六部分——评估与参考}（第 27--29 章）：108 道详细的测验题及其涵盖所有主题的全面答案、汇总关键方程、API 参考和故障模式诊断的快速参考章节，以及包含未来方向的结论。
\end{enumerate}

The guide includes over 100 detailed quiz questions with comprehensive answers spanning all topics, plus a quick-reference chapter consolidating key equations, API references, and failure mode diagnostics.

本指南包括超过 100 道详细的测验题，涵盖所有主题的全面答案，以及一个汇总关键方程、API 参考和故障模式诊断的快速参考章节。

## 设计理念

Three principles guide this document:

三条原则指导本文档：

\begin{enumerate}
  \item \textbf{Intuition first, formalism second}. Every equation is preceded by a plain-English explanation of what it means and why it matters.
  \item \textbf{直觉优先，形式其次}。每个方程之前都有一个自然语言解释，说明它的含义和为什么重要。
  \item \textbf{Implementation-aware}. Theory is useless without knowing how to make it work. We include code, hyperparameter tables, memory budgets, architecture diagrams, and debugging strategies throughout.
  \item \textbf{实现意识}。不知道如何使之工作，理论就是无用的。我们在全文中包含代码、超参数表、内存预算、架构图和调试策略。
  \item \textbf{Honest about what works}. We clearly state which approaches are production-tested and which are research explorations.
  \item \textbf{如实陈述}。我们明确说明哪些方法经过生产测试，哪些是研究探索。
\end{enumerate}

## 范围与有意省略

This guide focuses on \textbf{text-in, text-out language models} and the RL, systems, and agentic infrastructure built around them. Several important areas are intentionally excluded:

本指南侧重于\textbf{文本输入、文本输出的语言模型}以及围绕它们构建的 RL、系统和智能体基础设施。以下几个重要领域被有意省略：

\begin{itemize}
  \item \textbf{Multimodal models} (vision--language, audio, video). Multimodal architectures introduce distinct training pipelines (contrastive pre-training, cross-modal alignment, modality-specific encoders), data curation challenges, and evaluation protocols that each merit book-length treatment. Including them would double the scope without deepening the RL and agentic core that unifies this guide.
  \item \textbf{多模态模型}（视觉-语言、音频、视频）。多模态架构引入了不同的训练流水线（对比预训练、跨模态对齐、特定模态编码器）、数据整理挑战和评估协议，每项都值得整本书的篇幅。包含它们会使范围加倍，而不会加深贯穿本指南的 RL 和智能体核心。
  \item \textbf{Domain-specific deployments} (healthcare, legal, finance, scientific discovery). Domain adaptation introduces regulatory constraints, specialized evaluation, and data-access issues that are orthogonal to the general methods presented here. The algorithms and architectures we cover \emph{are} the building blocks practitioners adapt to these domains, but the adaptation details are better served by dedicated references.
  \item \textbf{特定领域部署}（医疗、法律、金融、科学发现）。领域自适应引入了与本指南所呈现的一般方法正交的监管约束、专用评估和数据访问问题。我们涵盖的算法和架构\emph{正是}实践者调整以适用于这些领域的构建模块，但适应细节更适合由专门的参考资料来服务。
  \item \textbf{Personalization and recommendation systems.} Personalization relies on user modeling, collaborative filtering, and interaction-history architectures that form a parallel research tradition. While LLMs are increasingly used \emph{within} recommender systems, the core techniques (sequential models, bandit-based exploration, cold-start handling) are sufficiently distinct to warrant separate coverage.
  \item \textbf{个性化和推荐系统。}个性化依赖于用户建模、协同过滤和交互历史架构，这些构成了一个平行的研究传统。虽然 LLM 越来越多地被用\emph{于}推荐系统内部，但核心技术（序列模型、基于 bandit 的探索、冷启动处理）足够不同，值得单独覆盖。
\end{itemize}

By maintaining this boundary, we keep a single coherent thread---\emph{from architectural foundations and systems infrastructure, through the training algorithms that produce aligned and reasoning models, to the orchestration and deployment of autonomous agents}---without fragmenting the narrative across modalities and verticals.

通过保持这一边界，我们维持了一条单一连贯的线索——\emph{从架构基础和系统基础设施，通过产生对齐和推理模型的训练算法，到自主智能体的编排和部署}——而不会使叙事在模态和垂直领域之间碎片化。

--- \emph{Haggai Roitman, 2026}

---

# 引言

## 大局观

This guide takes you from \textbf{first principles to production systems}. It is written for practitioners --- researchers, engineers, and applied scientists --- who want to understand and build the full stack of modern AI: from transformer architectures and the hardware that runs them, through the training algorithms that align models with human intent and teach them to reason, to the agentic architectures that deploy them as autonomous systems.

这本指南带你从\textbf{第一性原理走向生产系统}。它是为实践者——研究人员、工程师和应用科学家——而写的，他们希望理解并构建现代 AI 的完整技术栈：从 Transformer 架构和运行它们的硬件，到使模型与人类意图对齐并教会它们推理的训练算法，再到将其部署为自主系统的智能体架构。

The core thesis is simple: \emph{building great AI systems requires understanding the entire pipeline, not just one layer}. An engineer debugging a training run needs to understand GPU memory hierarchies and optimizer dynamics. A fine-tuning practitioner needs to know when LoRA suffices and when full-parameter training is worth the cost. An agent developer needs to understand how the underlying model was trained. A technical leader evaluating frameworks needs to understand what trade-offs each one makes. This guide provides that complete picture.

核心论点是简单的：\emph{构建优秀的 AI 系统需要理解整个流水线，而不仅仅是一个层面}。调试训练运行的工程师需要理解 GPU 内存层次结构和优化器动态。微调实践者需要知道什么时候 LoRA 足够，什么时候全参数训练值得成本。智能体开发者需要理解底层模型是如何被训练的。评估框架的技术领导者需要理解每个框架所做的权衡。本指南提供了完整的图景。

## 通向智能体 AI 之路：简史

Today's agentic AI systems did not emerge in a vacuum. They stand on decades of milestone systems --- each solving a narrower problem but collectively building the techniques, hardware, and ambition that made autonomous agents possible.

当今的智能体 AI 系统并非凭空出现。它们建立在数十年的里程碑式系统之上——每个系统解决了更狭义的问题，但共同构建了使自主智能体成为可能的技术、硬件和雄心。

\begin{enumerate}
  \item \textbf{Deep Blue (1997)}~\cite{campbell2002deep} --- IBM's chess engine defeated world champion Garry Kasparov using brute-force search (200 million positions/second) with handcrafted evaluation functions. It proved machines could exceed human performance in well-defined adversarial domains, but generalized to nothing else.
  \item \textbf{深蓝（1997）}~\cite{campbell2002deep}——IBM 的国际象棋引擎使用暴力搜索（每秒 2 亿个局面）和手工制作的评估函数击败了世界冠军 Garry Kasparov。它证明了机器可以在定义良好的对抗领域中超越人类表现，但无法推广到其他任何领域。
  \item \textbf{IBM Watson --- Jeopardy! (2011)}~\cite{ferrucci2010building} --- Watson combined information retrieval, NLP, and massive parallelism to defeat human champions at open-domain question answering. It demonstrated that AI could process unstructured text at scale, but required years of domain-specific engineering and couldn't learn new domains without substantial human effort.
  \item \textbf{IBM Watson——Jeopardy!（2011）}~\cite{ferrucci2010building}——Watson 结合了信息检索、NLP 和大规模并行化，在开放领域问答中击败了人类冠军。它证明了 AI 可以大规模处理非结构化文本，但需要多年的领域特定工程，且没有大量人力投入就无法学习新领域。
  \item \textbf{AlexNet and the Deep Learning Revolution (2012)}~\cite{krizhevsky2012imagenet} --- Krizhevsky et al.'s CNN won ImageNet by a stunning margin, proving that deep neural networks trained on GPUs could learn representations from raw data. This single result triggered the modern deep learning era and the hardware investment that eventually made LLMs possible.
  \item \textbf{AlexNet 与深度学习革命（2012）}~\cite{krizhevsky2012imagenet}——Krizhevsky 等人的卷积神经网络以惊人的优势赢得了 ImageNet，证明了在 GPU 上训练的深度神经网络可以从原始数据中学习表示。这单一结果引发了现代深度学习时代和硬件投资，最终使 LLM 成为可能。
  \item \textbf{AlphaGo (2016)}~\cite{silver2016mastering} --- DeepMind's system defeated Go world champion Lee Sedol using deep RL (policy networks + value networks + Monte Carlo Tree Search). Unlike Deep Blue's brute force, AlphaGo \emph{learned} to play --- demonstrating that RL could master domains where search alone was intractable ($10^{170}$ board states). AlphaGo Zero (2017)~\cite{silver2017mastering} later learned entirely from self-play, needing no human games at all.
  \item \textbf{AlphaGo（2016）}~\cite{silver2016mastering}——DeepMind 的系统使用深度 RL（策略网络 + 价值网络 + 蒙特卡洛树搜索）击败了围棋世界冠军 Lee Sedol。与深蓝的暴力方法不同，AlphaGo \emph{学习}下棋——证明了 RL 可以掌握仅靠搜索无法处理的领域（$10^{170}$ 个棋盘状态）。后来的 AlphaGo Zero（2017）~\cite{silver2017mastering} 完全从自我对弈中学习，完全不需要人类棋局。
  \item \textbf{GPT-2/GPT-3 (2019--2020)}~\cite{brown2020language} --- OpenAI showed that scaling decoder-only transformers to billions of parameters produced emergent few-shot learning. GPT-3 (175B parameters) could perform tasks it was never explicitly trained for --- translation, arithmetic, code generation --- simply from in-context examples. The era of foundation models began.
  \item \textbf{GPT-2/GPT-3（2019--2020）}~\cite{brown2020language}——OpenAI 证明，将解码器专用 Transformer 扩展到数十亿参数可以产生涌现的少样本学习能力。GPT-3（1750 亿参数）可以执行从未被明确训练过的任务——翻译、算术、代码生成——仅仅通过上下文中的示例。基础模型时代开始了。
  \item \textbf{AlphaFold (2020)}~\cite{jumper2021alphafold} --- DeepMind solved the 50-year protein folding problem, predicting 3D protein structures with atomic accuracy. AlphaFold demonstrated that deep learning could crack fundamental scientific problems previously considered decades away. It also showcased the power of architecture innovation (attention over residue pairs) combined with massive compute.
  \item \textbf{AlphaFold（2020）}~\cite{jumper2021alphafold}——DeepMind 解决了 50 年的蛋白质折叠问题，以原子精度预测了 3D 蛋白质结构。AlphaFold 证明了深度学习可以攻克此前被认为还需数十年的基础科学问题。它同时展示了架构创新（残基对注意力）与大规模计算相结合的力量。
  \item \textbf{ChatGPT and RLHF (2022)}~\cite{ouyang2022training} --- InstructGPT/ChatGPT proved that a capable base model, when aligned via RLHF, becomes a genuinely useful assistant. This was the inflection point: AI went from a research tool to a consumer product used by hundreds of millions. The alignment techniques (reward models, PPO) became the template for all subsequent LLM post-training.
  \item \textbf{ChatGPT 与 RLHF（2022）}~\cite{ouyang2022training}——InstructGPT/ChatGPT 证明了一个有能力的基础模型，当通过 RLHF 对齐时，能变成一个真正有用的助手。这是转折点：AI 从研究工具变成了数亿人使用的消费产品。对齐技术（奖励模型、PPO）成为了所有后续 LLM 后训练的标准模板。
  \item \textbf{GPT-4 and Multimodal Models (2023)}~\cite{openai2023gpt4} --- Multimodal capabilities (vision + language), longer contexts, and improved reasoning pushed LLMs toward general-purpose cognition. Tool use (code interpreter, web browsing) hinted at agentic capabilities.
  \item \textbf{GPT-4 与多模态模型（2023）}~\cite{openai2023gpt4}——多模态能力（视觉 + 语言）、更长的上下文和改进的推理将 LLM 推向通用认知。工具使用（代码解释器、网页浏览）暗示了智能体能力。
  \item \textbf{Reasoning Models (2024)}~\cite{deepseek2025r1} --- OpenAI's o1 and DeepSeek-R1 showed that RL could teach models to \emph{reason}: chain-of-thought, backtracking, self-verification emerged spontaneously from reward signals alone. Models began solving competition-level mathematics and complex coding tasks.
  \item \textbf{推理模型（2024）}~\cite{deepseek2025r1}——OpenAI 的 o1 和 DeepSeek-R1 表明，RL 可以教会模型\emph{推理}：思维链、回溯、自我验证仅从奖励信号中自发涌现。模型开始解决竞赛级数学问题和复杂编码任务。
  \item \textbf{Agentic AI (2025--present)} --- The convergence point: LLMs with reasoning capabilities, equipped with standardized tool access (MCP), inter-agent communication (A2A), persistent memory, and sophisticated orchestration frameworks. Agents now autonomously write code, conduct research, manage workflows, and coordinate with other agents --- the subject of this guide.
  \item \textbf{智能体 AI（2025 至今）}——汇聚点：具有推理能力的 LLM，配备了标准化的工具访问（MCP）、智能体间通信（A2A）、持久化记忆和复杂的编排框架。智能体现