# DanceOPD: On-Policy Generative Field Distillation — 深度解读报告

> **论文**: DanceOPD: On-Policy Generative Field Distillation  
> **arXiv ID**: 2606.27377  
> **链接**: [https://arxiv.org/abs/2606.27377](https://arxiv.org/abs/2606.27377)  
> **基座模型**: Z-Image (DiT LoRA) + SD3.5-M  
> **核心方法**: On-Policy Generative Field Distillation  
> **解读日期**: 2026-06-26

---

## 目录

1. [问题陈述](#1-问题陈述)
2. [背景与动机](#2-背景与动机)
3. [核心洞见](#3-核心洞见)
4. [方法总览：三问框架](#4-方法总览三问框架)
5. [问题一：哪个能力场监督哪个样本？—— Hard-Routed Field Matching](#5-问题一哪个能力场监督哪个样本hard-routed-field-matching)
6. [问题二：场应该在状态空间的哪里查询？—— On-Policy Field Querying](#6-问题二场应该在状态空间的哪里查询on-policy-field-querying)
7. [问题三：一条轨迹上应该使用多少个状态？—— Semantic-Side Single Query](#7-问题三一条轨迹上应该使用多少个状态semantic-side-single-query)
8. [目标函数设计](#8-目标函数设计)
9. [理论分析：估计器与失配界](#9-理论分析估计器与失配界)
10. [Algorithm 1：训练步骤](#10-algorithm-1训练步骤)
11. [计算复杂度分析](#11-计算复杂度分析)
12. [实验设置](#12-实验设置)
13. [T2I + 编辑能力组合](#13-t2i--编辑能力组合)
14. [局部 + 全局编辑能力组合](#14-局部--全局编辑能力组合)
15. [现实主义场吸收](#15-现实主义场吸收)
16. [CFG 引导吸收](#16-cfg-引导吸收)
17. [多教师扩展诊断](#17-多教师扩展诊断)
18. [消融研究](#18-消融研究)
19. [定性结果](#19-定性结果)
20. [与现有方法的对比](#20-与现有方法的对比)
21. [局限性](#21-局限性)
22. [讨论与开放问题](#22-讨论与开放问题)
23. [声明索引](#23-声明索引)
24. [相关论文谱系](#24-相关论文谱系)
25. [总结与展望](#25-总结与展望)

---

## 1. 问题陈述

**核心问题**: 如何将多个异构的生成式视觉能力（文本到图像、图像编辑、现实主义增强、分类器自由引导等）组合到一个单一的流匹配（flow-matching）学生模型中？

**现有方案的不足**:
- **联合训练（Joint Training）**: 混合训练数据 → 能力稀释（capability dilution）
- **权重合并（Weight Merging）**: 假设参数空间的近似线性，约束过强
- **数据比例调优（Data-Ratio Tuning）**: 仅沿一条权衡曲线移动模型，不是真正的组合
- **推理时分数组合（Inference-time Score Composition）**: 需要同时加载多个模型，计算成本高，CFG 等算子的组合有额外约束

**DanceOPD 的切入点**: 将能力组合重新定义为**场查询问题（field-query problem）**，通过 on-policy 蒸馏在状态空间层面实现能力组合。

---

## 2. 背景与动机

### 2.1 流匹配生成模型
流匹配（Flow Matching, FM）[Lipman et al., 2022; Albergo et al., 2025] 将生成过程视为在连续状态空间上学习一个速度场（velocity field）$v(z_t, t, c)$。与扩散模型相比，流匹配提供了确定性的 ODE 轨迹和更灵活的调度（scheduler）。

### 2.2 On-Policy 蒸馏
On-policy 蒸馏（OPD）[Agarwal et al., 2024] 解决了标准知识蒸馏中的分布不匹配问题：教师不是评价固定训练状态，而是评价学生当前策略产生的状态。DanceOPD 将其从语言模型扩展到了视觉生成模型的速度场蒸馏。

### 2.3 生成场蒸馏
生成场蒸馏（Generative Field Distillation）将每个冻结的能力源视为一个速度场 $v_m(z_t, t, c)$。能力组合就变成了场对齐问题：学生应该在哪一个状态、对齐哪一个场？

### 2.4 三个关键设计问题
从场的视角出发，能力组合暴露了三个耦合的设计问题：
1. **哪个**能力场应当监督这个样本？（目标场歧义）
2. **在哪里**查询这个场？（状态分布不匹配）
3. **多少个**状态应当提供监督？（轨迹查询相关性）

---

## 3. 核心洞见

DanceOPD 的核心见解可以概括为三句话：

1. **场才是能力**：每个冻结的生成模型（T2I、编辑、现实主义、CFG）都可以看作定义在共享状态空间上的速度场。
2. **对齐才是组合**：能力组合不是参数的加权平均，而是让学生在不同的状态点上对齐不同的场。
3. **学生状态才是好状态**：在学生的 rollout 状态上查询教师场，而不是在数据分布或教师轨迹上查询。

这四个设计选择（硬路由、on-policy 查询、单语义查询、MSE 目标）本身都不新鲜，首次被系统性地组合成一个统一框架。

---

## 4. 方法总览：三问框架

DanceOPD 处理 $M \ge 2$ 个冻结的能力源 $\\{v_m\\}_{m=1}^M$，训练一个学生 $v_\theta$。

$$
\mathcal{L}_{\text{DanceOPD}} = \mathbb{E}_{m\sim\pi, (x,c)\sim\mathcal{D}_m, z_T\sim p_T, s\sim q_{\text{sem}}} \left[ \| v_\theta(\bar{z}_t, t, c) - v_m(\bar{z}_t, t, c) \|_2^2 \right]
$$

其中：
- $m \sim \pi$: 硬路由选择能力场
- $(x, c) \sim \mathcal{D}_m$: 从对应数据分布中采样
- $z_T \sim p_T$: 初始噪声
- $s \sim q_{\text{sem}}$: 语义端（低噪声侧）查询坐标
- $\bar{z}_t = \text{sg}(z_t^\theta)$: 学生 rollout 状态（stop-gradient）

---

## 5. 问题一：哪个能力场监督哪个样本？—— Hard-Routed Field Matching

### 设计
每个训练样本**只路由到一个**能力场。路由概率 $\pi(m)$ 默认对活跃场均匀。

### 为什么
- 软混合（soft all-teacher mixing）会产生语义模糊的目标——一个样本不应该同时收到 "把猫变成狗" 和 "把白天变成夜晚" 的监督信号
- 多任务优化文献 [Chen et al., 2018; Yu et al., 2020] 表明：当任务梯度方向不一致时，在优化器中平均梯度会产生妥协方向

### 实验支持（Table 7）
- Hard routing 比 soft mixing 在 MSE 下平均提升 **15.2%**（背景变更提升 20.8%，主题移除提升 26.8%）
- Hard routing 在 KL 目标下也提升 10.6%

### 关键性质
- 跨不同更新步骤实现统计性的能力组合
- 每个样本保持了语义上定义清晰的目标
- 与 multi-task optimization 的梯度冲突观察一致

---

## 6. 问题二：场应该在状态空间的哪里查询？—— On-Policy Field Querying

### 设计
冻结的能力场在**学生自己生成的状态**上被查询：

$$
z_{0:T}^\theta = \text{Rollout}(v_\theta; z_T, c), \quad \bar{z}_t = \text{sg}(z_t^\theta)
$$

然后在 $\bar{z}_t$ 上查询教师场 $v_m(\bar{z}_t, t, c)$。

### 为什么
- 如果只在数据状态（off-policy）上查询，训练和推理之间存在**协变量偏移**（covariate shift）
- 学生组合多个能力后，轨迹与单个教师不同，off-policy 状态不能覆盖学生访问的状态
- 这与 on-policy 模仿学习 [Ross et al., 2011] 和 OPD [Agarwal et al., 2024] 的动机一致

### 实验支持
- Off-policy 蒸馏在 T2I+Edit 上与 DanceOPD 相比分布更宽，且 T2I 保留和编辑精度都更低（Table 2）
- On-policy 查询在现实主义吸收实验中关闭教师-学生差距的 **85.3%**，而 off-policy 只关闭了部分

---

## 7. 问题三：一条轨迹上应该使用多少个状态？—— Semantic-Side Single Query

### 设计
每条学生 rollout 轨迹只查询 **1 个状态**，从语义端（低噪声侧）采样：

$$
K = 1, \quad s \sim q_{\text{sem}}(s), \quad s \sim \text{Beta}(5, 2) \text{（偏向低噪声侧）}
$$

### 为什么
- **轨迹查询相关性**：同一条 rollout 上的多个状态共享相同的初始噪声、提示词、条件和学生动力学，它们的梯度不是独立的
- **低噪声侧更富含能力信号**：风格、美学、局部属性、编辑信息集中在最终图像附近的状态
- 高噪声状态主导着通用去噪，能力特定信号密度低

### 实验支持（Table 7, Table 8）
- Single-query ($K=1$) 优于所有 dense-query 变体（$K=2,4,8,16$），GEditBench 平均提升 **7.9%-16.6%**
- 低噪声查询（low-$t$）比中/高噪声查询分别提升 **23.7%** 和 **19.5%**
- SDE 去相关实验（$\eta=0.3$）部分恢复了 dense-query 性能，验证了相关性确实是失败原因

---

## 8. 目标函数设计

### 默认：Plain Velocity MSE

$$
\mathcal{L} = \| v_\theta(\bar{z}_t, t, c) - v_m(\bar{z}_t, t, c) \|_2^2
$$

### 为什么 MSE 足够
- 目标是确定性的速度场，MSE 在 Gaussian velocity-likelihood 视角下就是自然回归目标
- KL 散度的 velocity-matching 形式在相同假设下退化为加权 MSE

### 实验支持（Fig. 10, Table 7）
- MSE 比 KL-$\bar{\sigma}^2$ 匹配提升 **4.5%**
- 比一致性匹配提升 **4.1%**
- 比 DMD2 变体提升 **15.6%-21.1%**

### 扩展：CFG 引导场吸收
将 CFG 引导速度场看作一个能力场：

$$
v_\alpha(z_t, t, c) = v_\emptyset(z_t, t) + \alpha(v_{\text{cond}}(z_t, t, c) - v_\emptyset(z_t, t))
$$

学生通过 MSE 吸收这个引导效果，从而使一次前向传播就获得部分引导效果。

---

## 9. 理论分析：估计器与失配界

（附录第 7.2 节）

### 路由场匹配的估计器

DanceOPD 的路由场匹配估计器在硬路由和单查询下是无偏的。关键性质：

**命题 1**（状态分布失配界）：设 $p_{\text{off}}(z_t)$ 是 off-policy 查询的状态分布，$p_{\text{on}}^\theta(z_t)$ 是学生 roll-out 的状态分布。如果速度场 $v_m$ 在 $L$ 上是 $L$-Lipschitz 的，则场上 on-policy 和 off-policy 估计之间的期望误差受限于 Wasserstein-1 距离：

$$
\mathbb{E}_{p_{\text{on}}^\theta}[\|v_m(z_t) - v_\theta(z_t)\|] \le \mathbb{E}_{p_{\text{off}}}[\|v_m(z_t) - v_\theta(z_t)\|] + L \cdot W_1(p_{\text{on}}^\theta, p_{\text{off}})
$$

当 $p_{\text{on}}^\theta \neq p_{\text{off}}$ 时（即学生轨迹偏离数据分布），off-policy 的误差有界劣于 on-policy。

### KL 到 MSE 的约简（附录第 7.1 节）

在假设 velocity 预测误差服从各向同性高斯分布的条件下，最小化 KL 散度等价于最小化加权的 MSE。这解释了为什么 MSE 表现如此好——它不是在牺牲信息论上的最优性，而是在速度场匹配的子问题中本身就是自然目标。

---

## 10. Algorithm 1：训练步骤

```
Algorithm 1 One DanceOPD Training Step

输入: 冻结能力场 {v_m}, 学生 v_θ, 路由概率 π, 查询分布 q_sem
输出: 更新后的学生参数 θ

1: A. 路由一个能力查询
2:   m ~ π(m), (x, c) ~ D_m        ▷ 保存样本身份
3: B. 在学生轨迹上查询
4:   z_T ~ p_T, z_{0:T}^θ ← Rollout(v_θ; z_T, c)  ▷ 学生 rollout
5:   s ~ q_sem(s), t ← t(s), z̄_t ← sg(z_t^θ)     ▷ 一个语义端状态
6:   u ← v_m(z̄_t, t, c)            ▷ 冻结的路由场
7: C. 匹配局部速度场
8:   L ← ||v_θ(z̄_t, t, c) - u||²₂
9:   θ ← OptStep(θ, ∇_θ L)
```

**关键点**:
- Rollout 是 stop-gradient 的 → 梯度只通过当前时间步回传
- 每步只有 1 个状态参与损失计算
- 路由、查询位置、损失计算三者相互独立，但通过统一框架整合

---

## 11. 计算复杂度分析

### 每步成本分解

| 方法 | 查询状态 | Rollout | K | 批因子 | 主导每步成本 |
|------|---------|---------|---|-------|------------|
| Off-Policy | 离线加噪状态 | 无 | 1 | 1 | $K_{\text{off}} C_{\text{grad}}$ |
| DiffusionOPD | 学生 rollout | N-step ODE | N | 1 | $N C_{\text{roll}} + N C_{\text{grad}}$ |
| Flow-OPD | 学生 rollout 分组 | N-step SDE | N | $\gamma_{\text{flow}}$ | $\gamma_{\text{flow}}(N C_{\text{roll}} + N C_{\text{grad}}) + \text{PPO开销}$ |
| **DanceOPD** | **学生 rollout** | **N-step ODE** | **1** | **1** | **$N C_{\text{roll}} + 1 C_{\text{grad}}$** |

### 关键洞察
- DanceOPD 支付 $N$ 步 rollout 成本（$N=16$），但只有 **1 个状态的梯度计算**
- 相比 DiffusionOPD 的 16 个状态梯度，DanceOPD 的 $C_{\text{grad}}$ 部分减少到 1/16
- 相比 Flow-OPD 的 PPO 开销 + 分组批大小翻倍，DanceOPD 显著更简单、更快
- Fig. 1 验证了速度层次：Off-Policy > DanceOPD > DiffusionOPD > Flow-OPD

---

## 12. 实验设置

### 基座模型
- **Z-Image** [Cai et al., 2025]: 单流 DiT，LoRA rank 128
- **SD3.5-M** [Esser et al., 2024]: 现实主义教师等

### 训练细节
- Rollout: 16-step Euler ODE
- 学习率: $2 \times 10^{-4}$, AdamW
- 梯度累积: 4
- 路由: 默认均匀分布
- 查询分布: $\text{Beta}(5, 2)$（偏向低噪声侧）

### 评估指标
- **GEditBench-EN** [Sheynin et al., 2024]: 6 类图像编辑（主题添加、替换、背景变更、风格变更、颜色变更、主题移除）
- **GenEval** [Ghosh et al., 2023]: T2I 对齐评估
- **Realism Reward**: 专有评分模型

### 对比方法
- **Off-Policy Distillation**: 相同路由 + MSE，但在离线加噪状态上查询
- **DiffusionOPD** [Li et al., 2026]: 完整的轨迹监督
- **Flow-OPD** [Fang et al., 2026b]: PPO 风格的密集奖励优化
- **Joint Training**: 数据混合训练

---

## 13. T2I + 编辑能力组合

### Table 2 主结果

| 方法 | Subj-Add | Subj-Rep | Bg-Chg | Style-Chg | Color-Alt | Subj-Rem | Avg | GenEval |
|------|---------|---------|--------|-----------|-----------|---------|-----|---------|
| Δ教师（oracle） | 6.379 | 6.389 | 5.883 | 5.970 | 6.394 | 6.422 | 6.239 | - |
| 联合训练 | 3.895 | 5.320 | 3.784 | 5.478 | 5.210 | 1.665 | 4.225 | 0.821 |
| Off-Policy | 4.772 | 5.075 | 4.336 | 4.736 | 4.543 | 4.683 | 4.691 | - |
| DiffusionOPD | 4.502 | 4.977 | 4.462 | 4.661 | 4.012 | 5.310 | 4.654 | - |
| Flow-OPD | 4.610 | 5.037 | 4.025 | 4.679 | 4.524 | 5.232 | 4.685 | - |
| **DanceOPD** | **5.549** | **5.812** | **4.348** | **5.498** | **5.944** | **6.153** | **5.551** | **0.848** |

### 分析
- DanceOPD 在 **5/6** 个编辑类别上显著领先
- 全局平均比次优方法提升 **~18%**
- GenEval 同时提升，说明 T2I 基础能力没有因为编辑训练而退化（**无能力稀释**）

---

## 14. 局部 + 全局编辑能力组合

### 设置
- 两个活跃场：局部编辑（属性教师）、全局编辑（风格教师）
- 1:1 路由比例

### 结果
- DanceOPD 在局部和全局编辑任务上都实现了最佳平衡
- 定性结果（Fig. 11-13）显示 DanceOPD 在保持场景身份的同时执行大幅度的风格和场景变换
- 对比方法要么 "未充分变换"，要么 "过度变换导致结构丢失"

---

## 15. 现实主义场吸收

### 设置
- 基座: SD3.5-M
- 现实主义教师: 在 100K 步全参数训练后获得
- 目的: 吸收更真实的纹理、光照、视觉统计

### 结果
- DanceOPD 关闭了 **85.3%** 的学生-教师奖励差距
- 现实主义奖励比 off-policy 提升 **9.9%**
- T2I 得分改进 **7.6%**，与 off-policy 在 0.1% 内匹配
- 定性结果（Fig. 7）显示 DanceOPD 在保持布局的同时提升了光照、纹理、清晰度

---

## 16. CFG 引导吸收

### 设置
- 将 CFG 引导速度场 $v_\alpha$ 作为冻结目标场
- 训练后学生单次前向传播就能获得部分引导效果

### 关键发现
- 吸收的引导和推理时的 CFG **不是独立的**：有效引导强度约为 $\alpha\beta$
- 最佳组合（$\alpha=3.5, \beta=2$，有效 CFG=7）比仅训练吸收提升 **7.6%**，比仅评估 CFG 提升 **1.4%**
- 过度组合（有效 CFG=49）会降低 **31.2%** 的分数

---

## 17. 多教师扩展诊断

### 硬路由 vs 软教师混合 (Table 7)
- MSE + 硬路由比软混合提升 **15.2%**（背景变更 20.8%，主题移除 26.8%）
- KL + 硬路由提升 **10.6%**（风格变更 14.5%）

### 步交替 vs 同步累积 (Table 7)
- 同一步累积多个场（$G=3, K=1$）损失 **4.6%** 平均性能
- 加上密集监督（$G=3, K=2$）后在主题移除上损失 **46.0%**

### SDE 去相关诊断
- 在 $G=3, K=2$ 压力测试中，SDE rollout（$\eta=0.3$）平均恢复 **18.4%**
- 主题移除恢复 **62.0%**，主题添加恢复 **29.0%**
- 但仍低于单查询默认 **8.6%** → 最佳方案是避免密集查询

---

## 18. 消融研究

### Rollout 步数 (Table 9)
- **16 步**最优：GEditBench 平均 5.751，优于 8 步（5.739）、20 步（5.583）、28 步（5.697）
- 更长的 rollout 不是更好——因为 Beta(5,2) 的 mass 在更多候选状态上分散

### 时间步查询 (Table 8)
- **低噪声查询**在 2000 步时达到 5.751
- 比中噪声（4.649）提升 **23.7%**
- 比高噪声（4.813）提升 **19.5%**
- 最显著：主题添加 46.1% 比高噪声，主题移除 42.3% 比中噪声

### 查询数量 (Table 7)
- $K=1$（单查询）是明确的赢家
- $K=2,4,8,16$ 全部低于单查询

### 目标函数 (Table 7)
- **Plain MSE** > Timestep-weighted MSE (+2.8%) > Consistency (+4.1%) > KL (+4.5%) > DMD2 (+15.6%)

### 初始化 (Table 8)
- **局部编辑 SFT 初始化** > 合并初始化 (+37.2%) > 全局编辑初始化 (+112.8%) > T2I 初始化 (+204.4%)

---

## 19. 定性结果

### 全局场景与风格编辑 (Fig. 11)
- 威尼斯运河黄昏→雪夜：DanceOPD 保持运河几何结构，同时完成大幅度的季节和光照变换
- 肖像→赛博朋克：保留面部、姿势、头发布局，同时应用荧光霓虹效果

### 局部属性编辑 (Fig. 12)
- 晚礼服颜色/材质变换：从深红丝绸到祖母绿天鹅绒，同时保持人体姿势和室内背景
- 租房整理：有效去除杂乱的物品，产生更整洁的房间布局

### 同一物体的多样编辑 (Fig. 13)
- 水瓶的 6 种编辑：冷凝、玫瑰金金属、樱花装饰、登山场景、爆炸图、透明玻璃
- 水瓶身份保持：整体形状、瓶盖、居中布局不变
- 表明学生没有记忆单一编辑模式，而是在共享物体表征上灵活适应

---

## 20. 与现有方法的对比

| 维度 | Joint Training | Weight Merging | Off-Policy | DiffusionOPD | Flow-OPD | **DanceOPD** |
|------|---------------|---------------|------------|-------------|---------|--------------|
| 能力组合方式 | 数据混合 | 参数插值 | 离线场匹配 | 轨迹监督 | PPO 优化 | **On-policy 场匹配** |
| 样本级语义 | ✓ | - | ✓ | ✗（多状态稀释） | ✗（组级聚合） | **✓** |
| On-policy 查询 | - | - | ✗ | ✓ | ✓ | **✓** |
| 密集查询相关 | - | - | - | ✓（问题） | ✓（问题） | **✗（单查询）** |
| 目标函数 | 标准训练 | - | MSE | KL 轨迹 | PPO clip | **Plain MSE** |
| 推理代价 | 1x | 1x | 1x | 1x | 1x | **1x** |
| CFG 吸收 | - | - | - | - | - | **✓** |

### 为什么 DanceOPD 更好
- **样本级语义保持**：硬路由确保每个样本只有一个明确的训练目标
- **去相关监督**：单查询避免了密集轨迹状态之间的相关性
- **简洁性**：Plain MSE 比 PPO 或 KL 轨迹更简单、更稳定
- **灵活扩展**：同样的框架可吸收现实主义、CFG 引导等非标准能力

---

## 21. 局限性

### 21.1 共享场支持
- 要求所有冻结能力源使用**兼容的速度场参数化**
- 相同骨干网络、潜空间表示、调度器约定、速度参数化
- 这并非 DanceOPD 独有：LLM OPD 和流匹配 OPD 方法也有类似约束

### 21.2 预定义路由
- 路由不灵活（硬编码为已知任务桶）
- 用户不能在推理时控制能力组合的平衡
- 未探索自适应路由

### 21.3 计算成本
- 虽然优于 DiffusionOPD 和 Flow-OPD，但仍需要完整的 16 步 rollout
- 比 Off-policy 多一个 $N C_{\text{roll}}$ 因子

### 21.4 多任务冲突
- 当路由概率偏差过于极端时可能重新引入能力稀释
- 同一步累积多个场时观察到性能下降

### 21.5 扩展性
- 实验最多处理 3 个场（T2I + 属性 + 风格）
- 扩展到 10+ 个场时的行为尚未验证

---

## 22. 讨论与开放问题

### 22.1 路由策略改进
- 当前路由是固定的均匀分布。自适应路由（根据任务难度、学生当前能力动态调整）可能更好。

### 22.2 实时用户控制
- 能否通过推理时的路由权重控制实现用户对能力组合的细粒度调节？

### 22.3 更多能力类型
- 能否吸收额外的能力：inpainting、outpainting、超分辨率、视频生成等？

### 22.4 跨模态扩展
- 框架是否适用于文本、语音、3D 等模态的能力组合？

### 22.5 多步 roll-in
- 多个 rollout 查询位置能否通过某种去相关机制实现互补？

---

## 23. 声明索引

| ID | 声明 | 证据 |
|----|------|------|
| C1.1 | 硬路由比软混合提升 15.2% | Table 7, Sec. 4.2 |
| C1.2 | 低噪声查询比中/高噪声提升超过 19% | Table 8, Sec. 4.3 |
| C1.3 | 单查询优于所有密集查询变体 | Table 7, Sec. 4.3 |
| C1.4 | Plain MSE 优于 KL、一致性、DMD2 等变体 | Table 7, Fig. 10 |
| C2.1 | On-policy 查询关闭 85.3% 现实主义教师差距 | Fig. 6(a), Sec. 4.1-C |
| C2.2 | DanceOPD 在 T2I+Edit 上比 DiffusionOPD/Flow-OPD 提升 ~18% | Table 2, Sec. 4.1-A |
| C2.3 | 局部编辑初始化优于合并/T2I/全局编辑初始化 | Table 8, Sec. 4.3 |
| C3.1 | SDE 去相关恢复 18.4% 的密集查询损失 | Table 7, Sec. 4.2 |
| C3.2 | 16 步训练 rollout 在 2000 步时最优 | Table 9, Sec. 4.3 |
| C3.3 | 有效 CFG = $\alpha\beta$，过度组合降低 31.2% | Fig. 6(b), Table 6 |
| C4.1 | 同一步累积多场导致性能下降 4.6%-22.8% | Table 7, Sec. 4.2 |
| C4.2 | DanceOPD 定性保持在各种编辑中一致 | Fig. 11-13, Sec. 9 |

---

## 24. 相关论文谱系

```
Diffusion Models [Ho et al., 2020; Sohl-Dickstein et al., 2015]
  └─ Score-based Generative Models [Song & Ermon, 2019; Song et al., 2021]
      └─ Flow Matching [Lipman et al., 2022; Albergo et al., 2025]
          ├─ Rectified Flow [Liu et al., 2022b]
          │   └─ SD3 [Esser et al., 2024]
          │       └─ Z-Image [Cai et al., 2025]  ← DanceOPD 基座
          └─ Flow-based OPD
              ├─ DiffusionOPD [Li et al., 2026]  ← 密集轨迹 ODE 监督
              ├─ D-OPSD [Jiang et al., 2026]     ← On-policy 自蒸馏
              ├─ Flow-OPD [Fang et al., 2026b]    ← PPO 密集奖励
              └─ DanceOPD [本文]                  ← 单查询场蒸馏

Knowledge Distillation [Hinton et al., 2015]
  └─ On-Policy Distillation [Agarwal et al., 2024]
      ├─ LLM OPD: MiniLLM [Gu et al., 2024], SeqKD [Kim & Rush, 2016]
      └─ Visual OPD
          ├─ DPO [Wallace et al., 2024]
          ├─ Flow-OPD [Fang et al., 2026b]
          └─ DanceOPD [本文]

Multi-Task Learning
  ├─ Gradient conflict: GradNorm [Chen et al., 2018], PCGrad [Yu et al., 2020]
  └─ Task routing: MoE [Jacobs et al., 1991]
       └─ DanceOPD 的硬路由继承此理念

Image Editing with Diffusion
  ├─ InstructPix2Pix [Brooks et al., 2023]
  ├─ OmniEdit [Chow et al., 2026a]
  ├─ TINO-Edit [Chen et al., 2024]
  └─ Step1x-Edit [Liu et al., 2025]
```

---

## 25. 总结与展望

### 贡献总结

DanceOPD 提出了一个统一且简洁的框架，用于通过 on-policy 生成场蒸馏来组合异构的视觉生成能力。核心贡献包括：

1. **公式化**：将能力组合重新定义为场查询问题，暴露了三个耦合的设计挑战
2. **方法**：硬路由 + on-policy 查询 + 单语义端查询 + MSE 的简洁组合
3. **验证**：在 T2I+编辑、局部+全局编辑、现实主义吸收、CFG 吸收等多样化场景中实现了最佳结果
4. **诊断**：系统地分析了多教师、密集查询、目标函数等设计选择的交互

### 未来方向

- **自适应路由**：根据样本或学生能力动态选择场
- **更多能力**：扩展到 inpainting、outpainting、超分辨率、3D 生成
- **更高效 rollout**：用更少的 rollout 步数获得同等质量的查询状态
- **推理时控制**：通过路由权重的连续调节平衡多种能力
- **跨模态**：扩展到文本、语音、代码生成等领域
