# 📄 每日论文日报 — 2026-06-19

共筛选出 **10** 篇感兴趣的论文。

---

## 1. Selective Synergistic Learning for Video Object-Centric Learning

- **arXiv ID**: [2606.15527](https://arxiv.org/abs/2606.15527)
- **分类**: `cs.CV` `cs.AI`
- **GitHub**: [https://github.com/wjun0830/SSync](https://github.com/wjun0830/SSync)
- **HF 讨论**: [https://huggingface.co/papers/2606.15527](https://huggingface.co/papers/2606.15527)

### 🤖 AI 摘要

Selective Synergistic Learning (SSync) addresses limitations in video object-centric learning by selectively distilling reliable cues through pseudo-labeling and transitive merging to improve object decomposition quality and robustness.

### 📋 原始摘要（节选）

Typical video object-centric learning (VOCL) approaches employ slot-based frameworks that rely on reconstruction-driven encoder-decoder architectures, where learning is mediated by two spatial maps: attention maps from the encoder and object maps from the decoder. As these two distinct maps exhibit different properties, a recent dense alignment strategy attempted to reconcile this discrepancy by enforcing agreement across all spatio-temporal patches via contrastive learning. However, this indisc...


> ⏳ 深度解读尚未完成或尚未加入知识库

---

## 2. ImageWAM: Do World Action Models Really Need Video Generation, or Just Image Editing?

- **arXiv ID**: [2606.19531](https://arxiv.org/abs/2606.19531)
- **分类**: `cs.CV` `cs.RO`
- **GitHub**: [https://github.com/yuyangalin/ImageWAM](https://github.com/yuyangalin/ImageWAM)
- **HF 讨论**: [https://huggingface.co/papers/2606.19531](https://huggingface.co/papers/2606.19531)

### 🤖 AI 摘要

ImageWAM demonstrates that pretrained image editing models can effectively replace video generation in world action models for robot control, achieving better performance with reduced computational costs.

### 📋 原始摘要（节选）

World Action Models (WAMs) commonly rely on video generation to bridge visual world modeling and robot control. However, video-based WAMs face three coupled limitations: dense multi-frame future tokens make inference costly, full video prediction spends capacity on action-irrelevant temporal and appearance details, and long-horizon future imagination may introduce errors that mislead action prediction. These issues raise a simple question: Does world action model really need video generation? We...


> ⏳ 深度解读尚未完成或尚未加入知识库

---

## 3. FAPO: Fully Autonomous Prompt Optimization of Multi-Step LLM Pipelines

- **arXiv ID**: [2606.19605](https://arxiv.org/abs/2606.19605)
- **分类**: `cs.SE` `cs.AI`
- **GitHub**: [https://github.com/cisco-foundation-ai/fully-automated-prompt-optimization](https://github.com/cisco-foundation-ai/fully-automated-prompt-optimization)
- **HF 讨论**: [https://huggingface.co/papers/2606.19605](https://huggingface.co/papers/2606.19605)

### 🤖 AI 摘要

FAPO optimizes LLM pipelines by combining prompt editing with structural changes, demonstrating superior performance across multiple benchmarks and security tasks.

### 📋 原始摘要（节选）

Multi-step LLM pipelines fail through interactions among retrieval, reasoning, and formatting steps, so prompt-only optimization can miss bottlenecks in the chain. We present FAPO (Fully Autonomous Prompt Optimization), a framework that lets Claude Code optimize an LLM pipeline inside a standardized codebase. FAPO evaluates a pipeline, inspects intermediate steps, diagnoses failures, proposes scoped changes, and validates variants repeatedly to optimize against a score function. It first tries p...

### 🔍 深度解读

- 📖 [深度解读报告](https://github.com/Jrink525/knowledges/tree/master/papers/fapo-fully-autonomous-prompt-optimization-of-multi-step-llm-pipelines-2606.19605/report.md) — 可直接打开
- 📂 [完整解读目录](https://github.com/Jrink525/knowledges/tree/master/papers/fapo-fully-autonomous-prompt-optimization-of-multi-step-llm-pipelines-2606.19605)
- 🧭 [研究方向挖掘](https://github.com/Jrink525/knowledges/tree/master/papers/fapo-fully-autonomous-prompt-optimization-of-multi-step-llm-pipelines-2606.19605/direction_board.json)
- 🔬 [问题重构分析](https://github.com/Jrink525/knowledges/tree/master/papers/fapo-fully-autonomous-prompt-optimization-of-multi-step-llm-pipelines-2606.19605/research_lens.json)

---

## 4. Beyond Static Leaderboards: Predictive Validity for the Evaluation of LLM Agents

- **arXiv ID**: [2606.19704](https://arxiv.org/abs/2606.19704)
- **分类**: `cs.AI`
- **HF 讨论**: [https://huggingface.co/papers/2606.19704](https://huggingface.co/papers/2606.19704)

### 🤖 AI 摘要

Aggregate-score leaderboards in agent benchmarks fail to capture deployment-relevant dimensions and show rank instability, necessitating new evaluation frameworks based on predictive validity and out-of-distribution criteria.

### 📋 原始摘要（节选）

Agent benchmarks are growing fast, but no single benchmark touches more than four or five of the dimensions that deployment exposes. This paper aggregates the largest coordinated deep-dive of one MCP-based industrial-agent benchmark to date: fourteen parallel implementation studies covering new asset classes (including a multi-modal visual extension), alternative orchestrations, retrieval strategies, reasoning modes, infrastructure optimizations, and evaluation-methodology probes. Consolidating ...

### 🔍 深度解读

- 📖 [深度解读报告](https://github.com/Jrink525/knowledges/tree/master/papers/beyond-static-leaderboards-predictive-validity-for-the-evaluation-of-llm-agents-2606.19704/report.md) — 可直接打开
- 📂 [完整解读目录](https://github.com/Jrink525/knowledges/tree/master/papers/beyond-static-leaderboards-predictive-validity-for-the-evaluation-of-llm-agents-2606.19704)
- 🧭 [研究方向挖掘](https://github.com/Jrink525/knowledges/tree/master/papers/beyond-static-leaderboards-predictive-validity-for-the-evaluation-of-llm-agents-2606.19704/direction_board.json)
- 🔬 [问题重构分析](https://github.com/Jrink525/knowledges/tree/master/papers/beyond-static-leaderboards-predictive-validity-for-the-evaluation-of-llm-agents-2606.19704/research_lens.json)

---

## 5. ENPIRE: Agentic Robot Policy Self-Improvement in the Real World

- **arXiv ID**: [2606.19980](https://arxiv.org/abs/2606.19980)
- **分类**: `cs.AI`
- **HF 讨论**: [https://huggingface.co/papers/2606.19980](https://huggingface.co/papers/2606.19980)

### 🤖 AI 摘要

ENPIRE framework enables autonomous robotics research through a closed-loop system that automates policy improvement via environment feedback, policy refinement, and evolutionary code optimization.

### 📋 原始摘要（节选）

Achieving dexterous robotic manipulation in the real world heavily relies on human supervision and algorithm engineering, which becomes a central bottleneck in the pursuit of general physical intelligence. Although emerging coding agents can generate code to automate algorithm search, their successes remain largely confined in digital environments. We conjecture that the missing abstraction to automate robotics research is a repeatable feedback loop for real-world policy improvement: reset the s...


> ⏳ 深度解读尚未完成或尚未加入知识库

---

## 6. Thinking with Visual Grounding

- **arXiv ID**: [2606.16122](https://arxiv.org/abs/2606.16122)
- **分类**: `cs.AI`
- **GitHub**: [https://github.com/Jun-Kai-Zhang/visually_grounded_thinking](https://github.com/Jun-Kai-Zhang/visually_grounded_thinking)
- **HF 讨论**: [https://huggingface.co/papers/2606.16122](https://huggingface.co/papers/2606.16122)

### 🤖 AI 摘要

Visually grounded thinking integrates natural-language reasoning with explicit visual evidence grounding in vision-language models, improving reasoning accuracy through scalable synthesis and reinforcement learning techniques.

### 📋 原始摘要（节选）

Visual thinking should not only sound right; it should show its evidence. While recent vision-language models (VLMs) can produce natural-language reasoning traces, these traces often leave the supporting image regions implicit, making them hard to verify and difficult to supervise. We introduce visually grounded thinking, a reasoning process in which models interleave natural-language thoughts with explicit point or box groundings of the visual evidence used at each step. This lets the model exp...


> ⏳ 深度解读尚未完成或尚未加入知识库

---

## 7. JAMER: Project-Level Code Framework Dataset and Benchmark on Professional Game Engines

- **arXiv ID**: [2606.19830](https://arxiv.org/abs/2606.19830)
- **分类**: `cs.SE` `cs.CL`
- **HF 讨论**: [https://huggingface.co/papers/2606.19830](https://huggingface.co/papers/2606.19830)

### 🤖 AI 摘要

Game development frameworks and benchmarks were created using data from game jam competitions to evaluate code generation and project-level programming capabilities.

### 📋 原始摘要（节选）

Current AI-driven game development has made substantial progress in asset generation, gameplay design, and web-based game coding, yet project-level code engineering on professional game engines remains largely unexplored due to the absence of large-scale datasets and deterministic evaluation methods. We present JamSet and JamBench, the first project-level game code framework dataset and benchmark built on a professional game engine. Our key insight is that Game Jam competitions, community events...


> ⏳ 深度解读尚未完成或尚未加入知识库

---

## 8. Understanding the Behaviors of Environment-aware Information Retrieval

- **arXiv ID**: [2606.16817](https://arxiv.org/abs/2606.16817)
- **分类**: `cs.CL` `cs.IR`
- **GitHub**: [https://github.com/LCO-Embedding/Envs-aware-Information-Retrieval](https://github.com/LCO-Embedding/Envs-aware-Information-Retrieval)
- **HF 讨论**: [https://huggingface.co/papers/2606.16817](https://huggingface.co/papers/2606.16817)

### 🤖 AI 摘要

Large language models can be trained via reinforcement learning to adapt query formulation strategies for different retrievers, with distinct optimal query styles and improved performance through retriever-specific guidance and model scaling.

### 📋 原始摘要（节选）

Recent retrieval-augmented generation (RAG) approaches have demonstrated strong capability in handling complex queries, yet current research overlooks a critical challenge: different retrievers require fundamentally different query formulation strategies for optimal performance. In this work, we present the first systematic analysis of how LLMs can learn to adapt their query formulation strategies for different retrievers via reinforcement learning (RL). Our empirical study reveals that RL effec...


> ⏳ 深度解读尚未完成或尚未加入知识库

---

## 9. DF3DV-1K: A Large-Scale Dataset and Benchmark for Distractor-Free Novel View Synthesis

- **arXiv ID**: [2604.13416](https://arxiv.org/abs/2604.13416)
- **分类**: `cs.CV` `cs.AI`
- **GitHub**: [https://github.com/johnnylu305/DF3DV](https://github.com/johnnylu305/DF3DV)
- **HF 讨论**: [https://huggingface.co/papers/2604.13416](https://huggingface.co/papers/2604.13416)

### 🤖 AI 摘要

A large-scale real-world dataset called DF3DV-1K is introduced to address the lack of clean and cluttered image sets for distractor-free radiance field research, containing 1,048 scenes with 89,924 images across 128 distractor types and 161 scene themes, along with a curated subset DF3DV-41 for robustness evaluation, and demonstrates improved performance when used to fine-tune a diffusion-based 2D enhancer for radiance field methods.

### 📋 原始摘要（节选）

Advances in radiance fields have enabled photorealistic novel view synthesis. In several domains, large-scale real-world datasets have been developed to support comprehensive benchmarking and to facilitate progress beyond scene-specific reconstruction. However, for distractor-free radiance fields, a large-scale dataset with clean and cluttered images per scene remains lacking, limiting the development. To address this gap, we introduce DF3DV-1K, a large-scale real-world dataset comprising 1,048 ...


> ⏳ 深度解读尚未完成或尚未加入知识库

---

## 10. Playful Agentic Robot Learning

- **arXiv ID**: [2606.19419](https://arxiv.org/abs/2606.19419)
- **分类**: `cs.RO` `cs.AI`
- **GitHub**: [https://github.com/Playful-RATs/rats](https://github.com/Playful-RATs/rats)
- **HF 讨论**: [https://huggingface.co/papers/2606.19419](https://huggingface.co/papers/2606.19419)

### 🤖 AI 摘要

Embodied robots learn reusable skills through self-directed play and exploration, then apply these skills to improve performance on downstream tasks without additional training.

### 📋 原始摘要（节选）

Current agentic robot systems can write executable Code-as-Policy programs, observe feedback, and revise behavior across multiple attempts, but they remain largely task-driven: reusable skills are acquired only after explicit instructions. We study Playful Agentic Robot Learning, where an embodied coding agent uses self-directed play as a continual skill-learning stage before downstream tasks arrive. We introduce RATs, Robotics Agent Teams designed for play-time skill acquisition. During play, R...


> ⏳ 深度解读尚未完成或尚未加入知识库

---


> 报告生成时间: 2026-06-19 | 数据来源: Hugging Face Daily Papers + arXiv