---
title: "RL Interview Questions 2026"
source: "https://x.com/sheriyuo/status/2063295181131247674"
author: "sheriyuo"
published: 2026-06-07
category: "ai-tools/agent-engineering"
tags: [RL, reinforcement-learning, interview, PPO, GRPO, DPO, LLM, MoE, infrastructure]
---

# RL 面试题 2026 — 35 道核心问题

> 原文：[sheriyuo @x.com](https://x.com/sheriyuo/status/2063295181131247674)  
> 作者观察到不少人拿 PhD offer 后立即转工业界高薪岗位，于是汇总知乎面经 + 近期讨论 + 个人观察，提炼出 35 道最有趣的 RL 面试题。

---

## 说明

- 不严格区分 LLM RL 和 Agentic RL——有些问题在不同设定下答案截然不同
- 不提供参考答案，每道题都可以无限深挖
- 现代 RL 招聘越来越要求全栈理解：算法研究者也会被问基础设施问题
- Data 相关问题未包含，因为高度依赖实际经验
- **背题不够，深度理解才重要**

---

## 一、算法篇

### 1. 为什么用 Actor-Critic 而不是纯 Critic？
### 2. KL 散度、交叉熵、MLE 之间是什么关系？
### 3. 不同 RL 场景下 reward 应该如何设计？
### 4. Importance sampling、rejection sampling 和其他 Monte Carlo 方法如何融入 RL？
### 5. PPO 和 GRPO 中的 advantage 如何计算？为什么要减 baseline？标准差归一化真的必要吗？
### 6. RL 训练和 test-time scaling 如何以不同方式做 exploration？
### 7. PPO 的 clipping 如何工作？为什么要取 min 目标？没有 clipping 会怎样？CISPO 有什么区别？
### 8. GRPO 为什么包含 KL 惩罚？KL 如何计算？DAPO 和 GSPO 为什么移除它？
### 9. LLM 训练中如果 loss 被多次 All Reduce 会发生什么？
### 10. DPO 的 reward function 是什么？reward hacking 可能发生吗？如何缓解？
### 11. MoE 模型中如何解决 train-inference mismatch？方法有哪些？
### 12. RL 训练中如何选择 group size、learning rate、PPO epochs、generation length？
### 13. Dr.GRPO、DAPO、GSPO、CISPO、SAPO、DPPO、MaxRL、SimKO 相比 GRPO 有哪些改进？各自的局限性？
### 14. TRPO、DPPO、AReaL 如何在 RL 目标上施加 trust-region 约束？
### 15. RL 能否从根本上扩展 LLM 的能力边界？
### 16. 基于 ProRL 等工作，如何思考 RL 训练的 scaling boundaries？
### 17. OPD 对比传统 RL 和 SFT 有哪些改进？应用场景？
### 18. LLM 训练过程中推理能力在哪个阶段涌现？
### 19. 从 DeepSeek R1 到 V3.2 再到 V4，RL 有哪些改进？MoE 模型中的 RL 有何不同？

---

## 二、基础设施篇

### 20. 忽略 CPU offload，GRPO 训练中内存里有多少份模型拷贝？各种优化能省多少内存？
### 21. 分布式推理：KV cache 传输优化和多 GPU 通信策略
### 22. INT8 vs FP8：tradeoffs？训练和推理各自偏好的精度？
### 23. RL rollout 中的长尾问题是什么？如何解决？
### 24. Continuous batching 在 RL 训练中引入什么问题？vLLM 和 SGLang 有何不同？
### 25. 如何衡量 vLLM/SGLang 的利用率？训练中如何评估 KV cache 利用率？
### 26. 大规模多节点 RL 训练中 backpropagation 如何实现？
### 27. 有哪些异步 RL 框架？它们解决了什么同步瓶颈？
### 28. AReaL 等 partial rollout 框架中，之前的策略的 KV cache 是否保留？
### 29. Expert Parallelism 如何影响 MoE 吞吐量？
### 30. 长上下文训练中如何设计 compute-communication overlap？Megatron 和 FSDP 的并行策略有何不同？
### 31. 如何实现确定性执行？什么是 batch invariance？什么导致的？atomic add 能否解决？
### 32. AReaL 和 slime 对 RL rollout 瓶颈的理解有何不同？
### 33. 全异步 RL 训练中的 staleness 如何思考？实际典型值是多少？
### 34. data 在 slime 中如何流动？如何与 Megatron 集成？loss 如何计算？
### 35. VeRL、TRL、Unsloth、AReaL、slime 中选哪个？为什么？

---

> **Good luck.** 面试准备有帮助，但真正理解远比背答案走得更远。
