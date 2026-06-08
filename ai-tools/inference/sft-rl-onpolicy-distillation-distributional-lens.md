---
title: SFT, RL, and On-Policy Distillation — A Distributional Lens (CN)
tags: [llm, post-training, sft, rl, distillation, machine-learning, ai-research]
---

# SFT、RL 与 On-Policy Distillation：从分布视角理解

> 原文作者：wh（@nrehiew_）
> 原文链接：https://x.com/nrehiew_/status/2053482349300797526
> 译者整理：Jarvis II
>
> 一篇深入探讨 LLM 后训练方法（SFT、RL、On-Policy Distillation）之间**定性差异**的技术文章。
> 核心观点：**on-policy 数据**是让 RL 在抗遗忘和泛化上优于 SFT 的关键——不是 KL 惩罚，也不是 RL 算法本身有什么特殊。

---

## 核心理念：分布视角下的后训练

LLM 本质上是**序列上的一个概率分布**。后训练就是**重塑这个分布**。不同方法的区别在于：

1. **目标分布是什么？**
2. **如何定义这个目标？**
3. **优化的直接程度如何？**

这不是严格的数学框架——作者将其视为一个**有用的思维模型**。

---

## 方法对比矩阵

| 维度 | SFT | RL | On-Policy Distillation (OPD) |
|------|-----|-----|------|
| 目标分布 | 固定的外部数据集分布 | 隐含最优策略分布 | 教师模型的分布 |
| 训练数据来源 | 外部（人工/强模型标注） | 模型自身采样 | 模型自身采样 |
| 梯度信号 | 交叉熵（每个 token） | 优势函数（episode 级别） | 反向 KL（token 级别教师信号） |
| KL 方向 | Forward KL（mode-covering） | Reverse KL（mode-seeking） | Reverse KL |
| 抗遗忘 | ❌ 差（灾难性遗忘） | ✅ 好 | ✅ 好 |
| 泛化 | ❌ 差（exposure bias） | ✅ 好 | ✅ 好 |
| 是否模仿特定 token 序列 | ✅ 是 | ❌ 否（只关注任务成功） | 介于两者之间 |

---

## SFT：固定外部目标分布

**机制**：有标注数据集 → 交叉熵训练 → 将模型拉向数据集分布。

**关键特性**：
- 由于负对数似然的性质，**起始分布不重要**——模型只是被拉向标注的 token 序列
- 自然导致**灾难性遗忘**：如果数据集分布远离模型原始分布，模型没有内在理由去靠近解空间中的近邻解
- 适合"冷启动"任务：需要大幅改变输出格式时很有效

---

## RL：期望奖励最大化的方向

**机制**：模型从自身采样 → 奖励函数打分 → Policy Gradient 更新提高期望奖励。

**关键特性**：
- 目标分布更难精确定义——它是**隐含的**
- 奖励信号的质量决定一切：
  - **RLVR（可验证奖励）**：奖励是质量的良好代理 → 沿奖励方向移动得到好模型
  - **RLHF（奖励模型）**：奖励模型不完美 → 情况更复杂

**抗遗忘的解释**：

RL 可以看作**拒绝采样**（REINFORCE + 0/1 奖励）：

> 奖励为 1 → 正向信号 | 奖励为 0 → 无信号

如果定义最优策略是所有采样都为 1 的策略，那么存在多个最优策略。**但由于训练在 on-policy 采样上进行**，学习到的最优策略是那些**距离当前策略最近**的。每个梯度更新步骤，模型都是在拟合一个**隐式具有低 KL** 的最优策略。

→ **On-policy 数据在每一步都约束训练朝向靠近起始策略的分布**。

---

## On-Policy Distillation：伪 RL

**机制**：学生对自身采样 → 最小化与教师分布的 KL 散度。

可以近似理解为：RL 用优势函数加权，OPD 用学生-教师 log 比率加权。

### On-Policy Self Distillation (OPSD)

- 教师和学生是同一个模型
- 但教师计算 log probability 时，prefix 包含**参考答案**（privileged information）
- 问题：两者输出太相似 → 非关键 token（如"wait"、"alright"）的 KL 可能比数学 token（如"power"、"exponent"）更高
- 解决方案：per-token clipping 防止过度更新

**与 RLVR 的对比**：

| 维度 | RLVR | OPSD / RLHF |
|------|------|-------------|
| 奖励信号 | 低偏置（可验证） | 高偏置（教师/logits） |
| 风格 | 放心移除 KL 惩罚（如 GRPO） | 需要 KL 惩罚 + 裁剪 |
| Token 级信号 | O(1) bits/episode（粗粒度） | 每个 token 有独特信号（细粒度但有噪） |

---

## 实验：Minimal Code Editing

**环境**：给模型一个带 bug 的函数 → 要求只修 bug，不改变其他部分。

**为什么要选这个环境？**
- **泛化测试**：在一种 corruption 类型上训练，在另一种上评估
- **遗忘测试**：同时在 LiveCodeBench 上评估代码生成能力

### 实验结果

1. 先训练 2 个教师模型（SFT 教师、RL 教师）
   - 两者都学会了最小编辑行为
   - **RL 教师泛化更好，无明显遗忘**
   - **SFT 教师代码生成能力退化**

2. 用 OPD 从两个教师分别蒸馏学生
   - **两个 OPD 学生表现极其相似** ← 出乎意料
   - **两个 OPD 学生都略超 RL 教师、大幅超越 SFT 教师**
   - **OPD 学生的遗忘程度低于 SFT 教师**——即使该教师本身就是退化的 SFT 模型

**结论**：数据来源（on-policy sampling）的重要性远超教师模型的选择。这意味着你可以先"过训练"一个专用模型（甚至用暴力 SFT），再用 OPD 蒸馏回通用模型。

---

## 学生为什么能超越教师？

1. **OPD 的监督更精准**——教师对学生自身前缀给出建议，而学生对教师不常访问的状态域更不擅长
2. **KL 匹配 ≠ 奖励最大化**
   - 教师分布包含风格、不确定性、替代延续、推理结构等信息
   - 匹配它可以重塑学生分布，改善采样行为
   - 学生采样时可能不复制教师的 greedy 行为，但反而更好

### 分布重塑的直观理解

> 即使训练数据是**乱码**（高温度下的自我蒸馏），性能仍然提升。——Zhang et al.

这个反直觉的结果说明：模型在新能力上经历了**模式坍缩**（mode collapse）。OPD 和 RL 的熵坍缩比 SFT 显著更剧烈——反向 KL 训练的模式寻找行为导致多样性下降。

---

## RL 和 OPD 为什么泛化更好？

**核心原因**：RL 不像 SFT 那样**模仿具体 token 序列**——监督信号附加在任务成功上，而不是特定的 token 路径。

**Exposure Bias（暴露偏差）**：SFT 只在教师访问过的状态下训练。测试时，自回归中学生的**一次错误**可能将其带到教师从未访问过的状态 → 复合误差（compounding errors）。

On-policy 数据聚合可以减少这种不匹配：学生在训练时就已经在自己的分布上学习。

---

## 完整 Pipeline：Pretrain → SFT → RL → OPD

当前主流开源模型的流程：

1. **Pre-training**：基础能力
2. **SFT**：必须的"冷启动"——格式对齐 + 基本指令遵循。没有 SFT 就没法高效做 RL
3. **RL**：数学/编程等可验证领域效果好
4. **OPD**：创意写作/知识密集型任务需要（因为奖励噪声大）

### 实证数据（MiMo-V2 Flash）

| 领域 | 最佳方法 | 原因 |
|------|----------|------|
| 数学、编程 | RL | RLVR 效果好 |
| 创意写作 | Self-distillation / OPD | 奖励噪声大 |
| 知识密集型 | 蒸馏类方法 | LLM Judge 有偏 |

注意：最终合并模型（expert merging）几乎**在所有领域都优于各专家教师**，唯一的例外是自蒸馏教师本身。

---

## 终极思考：什么是最好的算法？

**文章核心结论：未来算法的关键不是 RL 本身，而是 on-policy 数据。**

> 让你在不炸 KL 预算的前提下提升能力的关键 ingredient 是 **on-policy training**。

悬而未决的问题（Credit Assignment Problem）：
- 结果奖励太稀疏 → RL 成本高
- Process Reward Models → 大规模训练效率低
- Logit 蒸馏 → 信号密集但有偏 → 需要复杂的 clipping 方案

**理想的算法**应该同时具备：
1. ✅ 蒸馏的密集信号密度
2. ✅ RL 的无偏性
3. ✅ 两者的 on-policy 特性

具体是什么——**还不知道**。

---

## 关键引用

- Shenfeld et al. — RL as rejection sampling, implicit optimal policy close to current
- Schulman et al., 2025 — O(1) bits per episode in outcome RL
- Agarwal et al. — Distilled students surpass teacher on GSM8K
- Zhang et al. — Self-distillation with gibberish data still improves performance
- Brown, 2026 — Post-training as capability-KL tradeoff frontier
- Ross et al. — Exposure bias / compounding errors in SFT
- Lu et al., 2025 — On-policy data as key ingredient (origin)
