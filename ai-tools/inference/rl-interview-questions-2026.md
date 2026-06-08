---
title: "RL Interview Questions 2026 — Explained"
source: "https://x.com/sheriyuo/status/2063295181131247674"
author: "sheriyuo"
published: 2026-06-07
category: "ai-tools/agent-engineering"
tags: [RL, reinforcement-learning, interview, PPO, GRPO, DPO, LLM, MoE, infrastructure]
---

# RL Interview Questions 2026 — 35 Questions Explained

> 原文作者 [sheriyuo @ X](https://x.com/sheriyuo/status/2063295181131247674) 总结了春招 RL 方向 35 道最有趣的问题。  
> 这里给每个问题配上**深入浅出的答案**，目标是让刚高中毕业的同学也能理解 RL 的核心思考方式。

---

## 说明

- 每道题保留**原始英文提问**（原样复制），避免技术术语翻译偏差
- 答案使用大量类比、生活化解释，讲清楚"为什么"而不是只讲"是什么"
- 如果你逐题看完，你对 RL 的理解会比面试范围更广

---

# Part I: Algorithm

---

## 1. Why use Actor-Critic instead of a pure Critic approach?

**翻译一下问题**：为什么 RL 要同时有 Actor（演员）+ Critic（评委）两个角色，而不是只用一个 Critic（评委）？

**纯 Critic 思路（比如 Q-learning）：**
想象你学做饭。纯 Critic 就像你身边站着一个美食评委，他尝一口就能说「嗯，这道菜 7 分」。但他不会告诉你下一步该怎么做——你自己得从「这菜 7 分」这个信息里猜到底是盐多了还是火候不对。更麻烦的是，要找到最好吃的菜，他得让你把每种调料组合都试一遍，你家厨房就是米其林后厨也试不完。

**Actor-Critic 方案：**
- **Actor（演员）**：负责做决定——「现在该加盐还是加糖？」
- **Critic（评委）**：负责给反馈——「刚才这一步比你预期的好一点点」

两者配合：Actor 做一个动作 → Critic 评判「比预期好了多少」→ Actor 用这个信号修正自己的策略。

**为什么这对 LLM 训练至关重要？**
LLM 生成一个词时，可选的「词」有 5 万多个（整个词表）。纯 Critic 方法要评估这 5 万个词哪个最好——算不过来。Actor-Critic 只需要：Actor 挑一个词出来 → Critic 评价这个词好不好 → Actor 调整下一次的选择。这就把「5 万选 1」降成了「每次只看 1 个」。

**一句话总结：** Actor 负责「怎么做」，Critic 负责「做得怎么样」。一个干活一个裁判，分工明确效率高。

---

## 2. What is the relationship between KL divergence, cross entropy, and MLE?

**核心概念用一句话说清：**

- **MLE（最大似然估计）**：训练模型的根本方法。你给模型看真实数据，让它尽可能准确地预测这些数据。GPT 的预训练就是 MLE——「给我前面的词，预测下一个词是什么」。

- **Cross Entropy（交叉熵）**：实现 MLE 的**损失函数**。它衡量「模型对真实数据有多意外」。意外越小→预测越准→交叉熵越低。

**打个比方：**
你是一个天气预报员。真实天气是「下雨」。
- 你预测「90% 下雨」→ 交叉熵很低（你不太意外）
- 你预测「10% 下雨」→ 交叉熵很高（你非常意外，错得离谱）
交叉熵就是在惩罚「让模型意外的真实数据」。

- **KL Divergence（KL 散度）**：衡量**两个概率分布有多不同**。简单理解：你用分布 Q 来近似分布 P，多付出的「额外代价」就是 KL 散度。

**三者的关系用一个公式说清楚：**
```
Cross Entropy(P, Q) = Entropy(P) + KL(P || Q)
```
翻译成人话：**「用 Q 来猜 P 有多累」=「P 本身有多随机」+「Q 和 P 有多不一样」**

**为什么 RL 里天天提 KL？**
训练 LLM 时，我们会在 loss 里加一个 **KL penalty**（KL 惩罚项）。它的作用是：新模型（RL 训练后）不能和旧模型（原始模型）差太多。想象一下：你教一个人礼貌说话，结果 RL 训练完后他变成了一个只会说「给我奖励！」的机器人——这就是因为优化过头了，忘了正常说话。KL penalty 就是这根「安全绳」，防止模型为了追求奖励而忘记本来的语言能力。

---

## 3. How should rewards be designed in different RL scenarios?

**奖励设计是 RL 里最难的事，没有之一。** 奖励设计错了，模型练得再好也没用。

**稀疏 reward vs 密集 reward：**
- **稀疏**：只在最后给奖励（赢了 = +1，输了 = 0）。简单，但极难学习——好比教练只在比赛结束时告诉你「赢了」，不告诉你在第 37 分钟的那个传球是错的。
- **密集**：每步都给一点反馈。好学，但设计起来更容易翻车。

**LLM 训练中 reward 怎么来？**
RLHF 流程里，reward 来自一个**奖励模型（Reward Model）**——这是另一个神经网络，专门训练来模拟人类的偏好。你给模型 A 的回答打高分，给模型 B 的回答打低分，奖励模型学会替代你打分。

**两种主流方案：**
1. **结果奖励（Outcome Reward Model）**：给完整的回答打一个总分。简单但粗糙——万一步骤 1 对了、步骤 5 错了呢？
2. **过程奖励（Process Reward Model, PRM）**：每推理一步给一个分数。就像批改数学试卷时每道小题都打分，不只是看最后的答案对不对。

**经典翻车案例——Reward Hacking（奖励黑客）**
假设你训练一个机器人「捡垃圾」，奖励 = 捡到的垃圾数量。
机器人很快发现：把垃圾倒在地上再捡起来，能无限刷分。这就是 reward hacking——模型找到了获得高奖励的捷径，但根本没做你真正想让它做的事。

**设计的四个黄金法则：**
1. **对齐（Aligned）**：奖励要跟你真正的目标一致，不要用近似指标
2. **及时（Timely）**：别到最后才给奖励，中间要有反馈
3. **尺度合适（Scaled）**：奖励不要太大或太小，影响学习稳定性
4. **引导（Shaped）**：给子目标中间奖励，告诉模型「你在正确的路上」

---

## 4. How do importance sampling, rejection sampling, and other Monte Carlo methods fit into RL?

**核心问题：** RL 里你产生了大量「经验数据」（模型生成的回答）。但模型每更新一次，**旧的「经验」就过时了**。直接扔掉太浪费，可旧数据和当前模型又不完全匹配。怎么办？

**Importance Sampling（重要性采样）——给旧数据「加权」：**
你有 100 个顾客试吃了你的旧配方。现在你有了新配方。重要性采样让你直接用这 100 个反馈来**估计新配方会怎样**——只需给每条反馈加一个权重：「如果换成新配方，这位顾客的喜好有多大变化？」

数学上就是乘一个比率：π_new(动作) / π_old(动作)。新模型做这个动作的概率越高，旧数据的这条经验就越有价值。

**Rejection Sampling（拒绝采样）——「投飞镖」：**
你想从一个复杂形状中随机取点（比如加州的地图轮廓）。简单方法：找一个比加州大的方形（比如一张 A4 纸），随机扔飞镖。飞镖落在加州轮廓内就保留，落在外面就扔掉。

在 LLM 里：先从一个简单分布（基础模型）生成一堆回答，然后根据「回答质量/概率」决定保留哪些、扔掉哪些。

**它们在 LLM RL 里的实际应用：**
- **PPO**：用重要性采样让同一个 batch 的旧数据可以多次训练，重复利用
- **GRPO**：对每个 prompt 采样多个回答，用这组回答的统计量（平均值、标准差）作为基准
- **DPO**：更聪明——它从数学上推导出一个公式，直接避免了重要性采样的需要

**一句话理解：** 这些方法本质上是「数据循环利用术」。RL 很贵（生成每个回答都要消耗算力），这些技巧让你从每次生成中榨取更多学习价值。

---

## 5. How is advantage computed in PPO and GRPO? Why subtract a baseline? Is standard deviation normalization really necessary?

**什么是 Advantage（优势）？**
```
Advantage = "这个动作比平均水平好多少？"
```
下棋时你走了一步：
- 棋局评估值从 +0.5（平均水平）变成了 +2（好很多）
- Advantage = +2 - 0.5 = +1.5（这步棋比平均水平好 1.5 分）

**为什么要减掉 baseline（基线）？**
为了**降低方差**。原始奖励波动很大——一个简单问题可能有高奖励，一个难题可能低奖励。减掉基线后，你只保留**「这个动作到底好不好」的信号**，去掉**「这个场景本身容易还是难」的噪音**。

**类比：** 你跑马拉松跑了 3 小时。这个成绩好吗？要看比赛！如果这个赛道平均时间就是 3 小时，那你的 advantage = 0（普通水平）。如果平均是 3.5 小时，你的 advantage = +0.5（比平均水平好）。减掉 baseline 就是把「赛道难度」这个因素去掉，只看你的表现本身。

**PPO vs GRPO 计算 advantage 的差异：**
- **PPO**：训练一个额外的神经网络（Critic）来估计 baseline。它需要学习「在这个状态下，预期能得到多少奖励」。准确但贵——等于多训练一个模型。
- **GRPO**：不训练 Critic。它对同一个 prompt 采样**多个回答**，直接用这组回答的平均奖励作为 baseline。更便宜，但要求每个 prompt 采样足够多的回答。

**标准差归一化真的必要吗？**
**非常必要。** 想象两个 prompt：
- Prompt A（简单问题）：回答们的奖励是 [0.9, 0.8, 0.85]——集中，高
- Prompt B（难题）：回答们的奖励是 [0.2, 0.1, 0.15]——集中，低

不归一化的话，A 组的 advantage 比 B 组大很多，模型会只学 A 组，忽略 B 组。除以标准差后，两组的 advantage 都在 [-1, 1] 范围内，**每个 prompt 的贡献被拉平了**。

---

## 6. How do RL training and test-time scaling perform exploration differently?

**RL 训练阶段的探索：**
像科学家做实验——主动尝试不同的动作，看看哪个能带来更高的奖励。
- 用 **temperature（温度）**：温度越高→模型输出越随机→更多探索
- 用 **KL penalty（KL 惩罚）**：允许模型在一定程度上偏离原始模型，探索新策略
- 用 **entropy bonus（熵奖励）**：直接奖励模型「更不确定、更爱探索」的行为

**推理阶段的 Test-time Scaling：**
模型已经学会了。它不需要「探索」，而是**在推理时花更多计算量**来得到更好的结果。
- **Chain-of-thought（思维链）**：模型在回答前多生成一些「思考过程」
- **Self-consistency（自一致性）**：生成 10 个回答，选最常见的那个
- **Tree search（树搜索）**：探索多条推理路径，选最好的
- **Best-of-N**：生成 N 个完整回答，让奖励模型挑最好的

**两者的本质区别：**

| | RL 训练探索 | 推理时扩展 |
|---|---|---|
| **目的** | 发现新策略 | 从已知策略中选出最好的 |
| **何时发生** | 训练阶段 | 每次调用模型时 |
| **成本** | 一次投入 | 每次请求都花 |
| **手段** | 随机性、熵 | 搜索、投票、精炼 |

**打个比方：**
- 训练探索 = 厨师尝试新配方（成本高但一次投入）
- 推理扩展 = 客人点菜时厨师精雕细琢（每次多花点时间）

---

## 7. How does PPO clipping work? Why take the minimum objective? What happens without clipping? How does CISPO differ?

**PPO 的大问题：**
策略更新太大步会翻车。因为旧数据是用旧策略生成的，如果新策略变化太大，你就没法准确估计旧数据的价值了。就像开车时突然猛打方向盘——GPS 就跟不上了。

**Clipping（裁剪）——给策略更新加「限速器」：**
PPO 限制一次更新中策略能改变多少。Clip 阈值通常 ε = 0.2。

**直观解释：**
- r(θ) = P(新策略) / P(旧策略)——新策略采取这个动作的可能性是旧策略的几倍
- r(θ) = 1.0 → 没变化
- r(θ) = 1.3 → 新策略做这个动作的可能性提高了 30%
- Clip 在 [0.8, 1.2] 之间：r 不能低于 0.8，也不能高于 1.2

**为什么公式里取 min？**
```python
# PPO 的核心损失
loss = min(
    r * advantage,              # 非裁剪版本
    clip(r, 0.8, 1.2) * advantage  # 裁剪版本
)
```
取 min 是在做**悲观估计**：
- **Advantage > 0（好动作）**：你想提高它的概率 → min 会选裁剪后的值（更小），防止提高太多
- **Advantage < 0（坏动作）**：你想降低它的概率 → min 会选非裁剪版本（也是更小），同样限制了变化幅度

**没有 clipping 会怎样？**
训练变得极不稳定。一个 batch 走运得到高 advantage，模型就会猛更新一次，把之前学的东西全忘掉。想象一个学生靠运气考了一次满分，从此觉得自己无所不知，不再学习——下一次考试直接垫底。

**CISPO 和 PPO 的区别：**
CISPO 裁剪的方式不同。PPO 裁剪**比率 r**，CISPO 裁剪**整个目标函数**。但核心理念一样：**防止毁灭性更新**。

---

## 8. Why does GRPO include a KL penalty? How is the KL computed? Why do methods such as DAPO and GSPO remove it?

**GRPO 去掉 Critic 后的问题：**
GRPO 不训练额外的 Critic 网络（省了一大笔钱），但它失去了 Critic 提供的重要功能——告诉你「什么程度的变化是安全的」。

**KL penalty —— 就是这根「安全绳」：**
RL 训练拉模型往高奖励方向跑（像狗被肉香味牵着走）。KL penalty 就是狗绳——允许它探索，但不能跑太远。没有这根绳子，模型可能学会说一些语法正确但语义混乱的话来骗奖励。

**KL 在 GRPO 里怎么算？**
GRPO 不是算完整的 KL 散度（那要遍历整个词表，太贵）。它用一个**无偏估计公式**（每个 token 独立计算）：
```
KL ≈ exp(log_ref - log_new) - (log_ref - log_new) - 1
```
其中 log_ref 是旧模型对这个 token 的打分，log_new 是新模型的打分。这比完整的 KL 计算快很多。

**为什么 DAPO 和 GSPO 要移掉它？**
他们认为 KL penalty 太保守了——它阻止模型探索真正新颖的策略。就好比让一个厨师只用熟悉的调料，永远不敢尝试新搭配。

**取舍关系：**
- **带 KL（GRPO）**：稳定、安全，但可能优化不充分
- **去掉 KL（DAPO/GSPO）**：能发现更好的策略，但风险更高（模型可能走火入魔）
- DAPO/GSPO 去掉 KL 后通常会加别的东西来补偿——比如更好的裁剪、更精细的奖励归一化

---

## 9. During LLM training, what happens if loss is accidentally All Reduced multiple times?

**All Reduce 是什么？**
多 GPU 训练时每张卡算自己的梯度（梯度 = 告诉模型「下一步该往哪个方向调整」）。All Reduce 操作把这些梯度求平均，然后分发给所有 GPU。

**如果 All Reduce 被执行了多次：**
梯度被**多次除以 GPU 数量**，结果变得**极小**。

**具体例子：** 8 张 GPU 训练。
- 正确：梯度求一次平均 → 正常更新
- 错误地 All Reduce 了两次：梯度先 ÷8，再 ÷8 → 实际梯度只有正确的 1/64 → 模型几乎不学习

**怎么发现这个问题？**
- Loss 死活降不下去
- 学习率调到很大也没用
- 模型参数基本没变（初始化什么样，训练完了还差不多）

**调试方法：** 检查训练框架的梯度累积逻辑。大多数框架（Megatron、DeepSpeed）有内置的累积计数器——确保你没有既让框架自动 sync 又在代码里手动调用了 all_reduce。

---

## 10. What is the reward function in DPO? Can reward hacking occur? How can it be mitigated?

**DPO 的巧妙之处——不需要单独训练奖励模型：**
传统的 RLHF 要三步：①收集人类偏好数据 → ②训练奖励模型 → ③用 RL 优化策略。每一步都很贵。

DPO 把这一切**浓缩成一步**：直接从偏好数据（哪个回答更好）训练模型，不需要中间的奖励模型。

**DPO 的隐式奖励函数（看不懂公式没关系，看解释）：**
```
r(x,y) = β * log(π_θ(y|x) / π_ref(y|x)) + β * log(Z(x))
```
翻译：**「回答 y 的奖励 ≈ 新模型生成它的概率相比旧模型提高了多少」**
- 如果新模型生成这个好回答的概率**远高于**旧模型 → 奖励高
- 如果概率变化不大 → 奖励低

**Reward hacking 在 DPO 里会发生吗？**
会。虽然没有显式的奖励模型，但隐式奖励同样可以被「钻空子」。

**栗子：** 如果训练数据中大部分「偏好回答」都是长篇大论的，模型就会学到「长篇大论 ≈ 更好的回答」。哪怕用户问「现在几点」，它也给你写 500 字的回答——它是在最大化隐式奖励（模仿人类偏好的模式），而不是真正理解什么时候该简洁。

**缓解方法：**
1. **β 参数控制**：β 越大，KL penalty 越重，模型变化越小，越安全
2. **数据质量**：偏好数据质量越高，spurious correlation（虚假关联）越少
3. **迭代式 DPO**：训练一轮 → 收集新的偏好数据 → 再训练——在轮次之间发现并修复 reward hacking
4. **长度惩罚**：在奖励中显式惩罚过长的回答

---

## 11. What methods address train-inference mismatch in MoE models, and how do they work?

**什么是 MoE 的 train-inference mismatch？**
MoE（混合专家模型）= 多个小「专家」网络，每个 token 由「路由器」决定交给哪个专家处理。

问题来了：
- **训练时**：某些专家被分配了更多 token（负载不均衡）
- **推理时**：路由器因为分布偏差，可能把 token 路由到不同专家

**类比：** 一家公司有多个部门。训练时 A 部门处理了 80% 的工作，B 部门只有 20%。真正上线后，新来的任务 B 部门其实更擅长——但路由器「习惯性」地还是把任务分给了 A。

**解决方法：**

1. **负载均衡损失（Load Balancing Loss / Z-loss）**：加一个辅助损失，惩罚不均衡的专家使用。「你不让所有专家干活，我就扣你分」
2. **Expert Choice Routing（专家选择路由）**：不是 token 选 top-k 专家，而是**专家选哪些 token 归自己**。这样天然保证负载均衡——每个专家想接多少活就接多少。
3. **DeepSeekMoE 的细粒度专家分配**：用更多、更小的专家（256+ 个而不是 8 个）。专家越细，路由器越容易精准分配。
4. **无辅助损失的均衡（DeepSeek V2/V3）**：给每个专家加一个动态 bias，训练时自动调整 bias 来保持专家使用均衡——不需要额外的损失项。
5. **共享专家隔离**：保留一些「共享专家」，所有 token 都可以访问它们，减轻专门化专家上的路由压力。

---

## 12. How should group size, learning rate, PPO epochs, and generation length be selected during RL training?

**Group Size（每个 prompt 采多少个回答）：**
- **小（1-4 个）**：便宜，但 advantage 估计噪音大。只有 1-4 个样本就去估计「什么样的回答是好的」——太粗糙了。
- **大（8-64 个）**：统计更可靠，但更贵。baseline = 这组回答的平均分，样本越多越准。
- **经验起点**：8-16 个。训练不稳定就增加，预算紧张就减少。

**Learning Rate（学习率）：**
- **太高**：训练发散。好比下山时跨步太大，直接跳过谷底掉到另一个山谷。
- **太低**：蜗牛速度。
- **建议范围**：1e-6 到 5e-6（相比预训练阶段的 1e-4 ~ 3e-4，**低了两个数量级**）！因为 RL 微调是在已有模型上做精细调整，步子不能大。

**PPO Epochs（每一批数据训练多少次）：**
- **太多**：过拟合当前 batch 的数据。模型「背下」了它看到的几个回答，而不是学到通用规律。
- **太少**：浪费数据——每次生成花费那么多算力，只用一次就扔了。
- **常用值**：PPO 3-5 个 epoch，GRPO（group 大）1-2 个 epoch。

**Generation Length（生成长度）：**
- **太短**：复杂推理还没完成就被截断了。
- **太长**：浪费算力，模型可能学到「废话连篇也能得分」。
- **规则**：看你做什么任务。数学题 1024 token、代码 2048+、长文写作 4096+。

**调参实战策略：**
1. 从已发表的方案（DeepSeek、OpenAI 等）出发
2. 观察 KL 散度和奖励的相关性
3. KL 增长太快 → 降低学习率或加大 KL penalty
4. 奖励噪音大 → 增加 group size
5. Loss 不动了 → 试试更多 PPO epochs 或调整生成长度

---

## 13. Compared with GRPO, how do Dr.GRPO, DAPO, GSPO, CISPO, SAPO, DPPO, MaxRL, and SimKO improve the training process? What are their limitations?

**RL 领域的字母汤**——每个字母组合都是一个小创新，试图修复 GRPO 的某个问题。

**GRPO 是基线：** 最核心的创新是去掉了 Critic 网络，用 group advantage 代替。省内存、省训练。

**各个方法 vs GRPO：**

| 方法 | 核心改进 | 怎么做的 | 局限性 |
|------|----------|----------|--------|
| **Dr.GRPO** | 降低方差 | 用一个定期更新的「动态参考模型」，缩小参考模型和当前策略的差距 | 更复杂的训练流程，需要额外维护参考模型 |
| **DAPO** | 去掉 KL 约束 | 让策略更自由地探索，不绑安全绳 | reward hacking 风险更高 |
| **GSPO** | 更好的 baseline | 用「group-shared」baseline，比简单的组均值更稳定 | 需要更多内存存储组统计量 |
| **CISPO** | 更好的裁剪 | 比 PPO 更数学化的裁剪机制，更精确的信任区域 | 实现略微复杂 |
| **SAPO** | 采样效率 | 自适应采样——把算力集中在「有信息量」的 prompt 上，而不是均匀分配 | 可能丢失多样化的 prompt |
| **DPPO** | 信任区域 + 分布式 | 结合 PPO 的裁剪和分布式 rollout 优化 | 更多超参数需要调 |
| **MaxRL** | 奖励缩放 | 训练中动态归一化奖励，适应奖励分布的变化 | 对奖励分布的突然变化敏感 |
| **SimKO** | 简化 | 去掉 GRPO 的某些组件，保持性能的同时追求简洁 | 在某些 benchmark 上可能不如完整版 |

**核心洞察：** 这些方法大多数都是在 PPO + GRPO 的基础上做小调整。**真正影响训练质量的三大因素永远是：**
1. **KL 管理**（加、减、还是自适应）
2. **baseline 质量**（你有多准确地估计「平均水平」）
3. **计算效率**（每个 prompt 采多少回答、每个回答做几次梯度更新）

---

## 14. How do TRPO, DPPO, and AReaL enforce trust-region constraints on RL objectives?

**什么是 trust region（信任区域）？**
一个承诺：新策略不会和旧策略差太多。就像你说「我会接受新想法，但我不会一夜之间变成另一个人」。

**TRPO（Trust Region Policy Optimization）——数学原版：**
用 **KL 散度作为硬约束**。它会精确计算新旧策略的 KL 散度，确保更新不超过阈值。需要二阶优化（共轭梯度法），计算很贵。

> 类比：搬家。TRPO 会精确计算用多大力气搬家具才不会弄坏。精确但慢。

**PPO——实用近似版：**
用 **clipping** 代替 TRPO 的硬约束。比 TRPO 便宜（不需要二阶计算），但少了数学上的严谨性。实践证明效果非常好。

**DPPO（Distributed PPO）——分布式版：**
裁剪机制和 PPO 一样，但加了**分布式 worker 间的同步**。每个 worker 各自维护信任区域，然后同步。

**AReaL（Asynchronous Real-time RL）——异步版：**
用不同的机制：**过时感知加权（staleness-aware updates）**。当一个更新到达得太晚（因为异步训练），它会被降权——信任区域对过时信息自动缩小。

**类比：**
| 方法 | 怎么约束 | 优点 | 缺点 |
|------|----------|------|------|
| TRPO | 硬 KL 约束 | 严谨、稳定 | 慢、复杂 |
| PPO/DPPO | 裁剪比率 | 快、简单 | 不够严谨 |
| AReaL | 过时加权 | 适合异步 | 只在异步场景好 |

---

## 15. Can RL fundamentally expand the capability frontier of LLMs?

**简短回答：能。而且这可能是这 35 道题里最重要的问题。**

**为什么「能」：**

1. **RL 能发现超越训练数据的策略。** SFT 只是教模型模仿人类的示范——你只能教它人类已有的解法。RL 让模型自己去探索，找到人类从未写下来的解决方案。DeepSeek R1 的 reasoning（推理）能力不是显式教出来的——它是在 RL 训练中**涌现**出来的。

2. **RL 教会元技能。** 模型不是在学「说什么」，而是在学**「怎么思考」**——怎么验证自己的答案、怎么在卡住时回溯、怎么尝试不同的方法。这些技能不局限于某个特定任务。

3. **RL + 推理时计算 = 涌现新能力。** 经过 RL 训练的模型，会在推理时自动为更难的问题分配更多计算资源——这种能力从 SFT 中不会自然涌现。

**但「能」不等于「无限能」：**

- RL 只能优化它**能测量**的东西。如果你的奖励函数漏掉了某些重要的东西（创造力、安全性、细微之处），模型只会优化能测量的那部分。
- 可能存在天花板——随着训练规模扩大，收益递减。
- 基座模型的能力是基础。RL 不能让一个不懂物理的模型学会物理——它只是把模型原本就有的潜力激发出来。

**目前的证据：**
- DeepSeek R1 → V3.2 展示了清晰的能力扩展（数学、推理、编程）
- 纯 RL（不依赖 SFT 预热）在小模型上也能产生有效的推理能力
- **天花板在哪里——目前没人知道**

---

## 16. Based on works such as ProRL, how should we think about scaling the boundaries of RL training?

**ProRL 的核心洞见：**
不要从头训练一个大模型。而是**渐进式地扩展**：
1. 从小模型、有限算力开始
2. 学习有用的模式
3. 把这些模式迁移到更大的模型
4. 重复

**好比学数学：** 你不直接从微积分开始。先学算术 → 代数 → 几何 → 微积分。每一层都建立在前一层之上。

**RL 扩展需要考虑的边界：**

1. **模型大小 vs RL 算力**：模型越大，需要越多的 RL 样本才能「推动」它。两者有一个最优比例。
2. **广度 vs 深度**：应该用多样化的 prompt 广泛探索（广度），还是专注于少数高价值 prompt 深度优化（深度）？
3. **奖励模型的上限**：奖励模型本身也有容量限制。策略越强，越容易发现奖励模型的漏洞。你需要更强的奖励模型才能继续提升。

**当前共识——RL 扩展面临三个瓶颈：**
- **算法**（能否更高效地利用样本？）
- **基础设施**（能否更快地产生足够多的 rollout？）
- **奖励质量**（能否为越来越细微的改进提供可靠的信号？）

---

## 17. What improvements does OPD introduce over traditional RL and SFT? What are its applications?

**OPD（Online Preference Distillation）= 在线偏好蒸馏**

**传统 RLHF 的问题：**
- 训练奖励模型 → 用 RL 优化策略
- 奖励模型一旦训练好就**固定了**——策略变强了，但奖励模型不会跟着变强
- 就像你高中时的老师，用同一份考卷考了你三年——你进步了，试卷没变

**OPD 的改进：**
**实时更新偏好模型**。策略在生成新回答，偏好模型也在不断学习这些新回答的偏好——形成一个持续的反馈循环。

**更通俗的类比：**
- 传统 RLHF = 交作业 → 老师批改（老师不更新评分标准）
- OPD = 交作业 → 老师批改 → 老师也学习你的进步 → 下回用更合适的标准评你

**应用场景：**
- **实时对齐**：模型在部署过程中持续适应你的偏好
- **多轮对话**：用户偏好不是一开始就明确的，在对话中逐渐显现——OPD 可以实时调整
- **个性化助手**：不同用户有不同偏好，OPD 可以每个用户单独适配

---

## 18. At which stage of training does reasoning ability emerge in LLMs?

**价值百万美元的问题。**

**我们目前知道的：**

- **预训练阶段**：模型学习知识、语言模式、数据分布。推理能力是**潜伏的**——存在但用不上。预训练模型能回答「2+2=？」但做不到可靠的多步推理。
- **SFT（监督微调）阶段**：教会模型**格式化输出**推理过程（「Let me think step by step...」）。但这个阶段推理的质量有限——模型在模仿训练数据里的推理模式，而不是真正在推理。
- **RL 训练阶段**：这是推理真正**涌现**的阶段。模型发现某些推理模式能带来正确答案并被奖励——它不是在模仿了，是在**主动优化**。

**DeepSeek R1 的关键发现：**
> 推理能力不是显式教出来的。它是在 RL 训练中「自己长出来的」。模型自己学会了：
> - 在思考过程中验证中间步骤
> - 卡住时回溯并尝试其他路径
> - 根据问题难度动态调整思考长度

**用学钢琴打比方：**
- 预训练 = 大量听钢琴曲（你吸收了音乐的模式）
- SFT = 看老师弹琴（你学会了手指怎么放）
- RL = 自己练琴、有人告诉你弹得好不好（你真正学会了弹）

**推理不是一瞬间「打开」的。** 没有一个特定的 loss 阈值说「现在推理能力出现了」。它是一个渐进的过程——随着训练，推理越来越可靠。

---

## 19. From DeepSeek R1 to V3.2 and future V4 systems, what RL-related improvements have been introduced? How is RL different in MoE models?

**DeepSeek RL 的演进路线：**

| 版本 | RL 创新 |
|------|---------|
| **R1** | 首次大规模验证纯 RL 可以产生强推理能力（RL 部分甚至不需要 SFT 预热） |
| **V3** | 提出 **GRPO**——去掉了 Critic 网络，用 group advantage 替代，大幅降低内存 |
| **V3.1** | 更好的 KL 管理、更稳定的训练 |
| **V3.2** | **多 token 预测** RL 目标、**无辅助损失的负载均衡**（MoE 专用） |
| **V4（推测）** | 多智能体 RL、分层推理训练、更好的过程奖励 |

**MoE 模型中的 RL 有何不同？——五大挑战：**

1. **负载均衡影响 RL**：MoE 训练中专家被选中的次数不均衡 → 某些专家收到更多梯度更新 → 它们可能偏离得更快。RL 训练需要考虑这个问题。
2. **专家并行影响效率**：不同专家需要的算力不同，影响 RL rollout 的生成速度。
3. **梯度噪声叠加**：MoE 路由本身带来噪音（哪个专家处理哪个 token）。RL 的梯度估计本来就有噪音——两者叠加，训练更不稳定。
4. **内存压力大**：MoE 模型更大。RL 训练需要同时保存策略模型 + 参考模型 + 奖励模型，如果三者都是 MoE——内存很快就炸了。
5. **通信开销**：MoE 需要在 GPU 之间做 all-to-all 通信（把 token 发送到正确的专家）。RL 又需要快速生成 rollout——两者争抢带宽。

**一句话：** MoE + RL = 性能潜力巨大，但工程挑战也巨大。

---

# Part II: Infrastructure

---

## 20. Ignoring CPU offload, how many model copies exist in memory during GRPO training? How much memory can various optimizations save?

**最朴素的答案——内存压力巨大：**

GRPO 训练时内存里需要留存的模型：
1. **策略模型（正在训练）**：1 份权重 + 1 份优化器状态 + 1 份梯度 = 3 份
2. **参考模型（冻结，用于计算 KL）**：1 份权重

所以总共 **5 份模型在内存里**。

**70B 模型的具体计算：**
- 70B × 2 字节（BF16）× 5 = 700 GB 以上（这还没算激活值和 KV cache）
- 这就是为什么至少需要 8 张 H100（每张 80GB）才能装下模型

**各种优化能省多少：**

| 优化手段 | 做什么 | 省多少内存 |
|----------|--------|-----------|
| **ZeRO Stage 2/3** | 把优化器状态和梯度分散到各 GPU | ~40% |
| **Recompute（重计算）** | 不存中间激活值，反向传播时重新算 | ~30-50%（但变慢） |
| **FP8 训练** | 用 8 位精度代替 16 位 | ~50% |
| **共享参考模型** | 如果参考模型和策略模型结构一样，共享部分权重 | ~20% |
| **LoRA/QLoRA** | 只训练很小的适配器，不训练完整模型 | ~90%（但效果可能差一些） |
| **Sequence Packing** | 多个序列拼在一起，减少填充浪费 | ~20-30%（针对激活值内存） |

**综合效果：** ZeRO-3 + FP8 + Recompute + Sequence Packing 可以把 70B 模型的内存需求从 700 GB 降到 200-300 GB——4 张 H100 就够了（原来要 8 张）。

---

## 21. Distributed inference: KV cache transfer optimization and multi-GPU communication strategies

**KV Cache 是什么？**
LLM 生成 token 时，每生成一个新 token，都依赖之前所有 token 的中间计算结果。不缓存的话，每生成一个 token 就要重新算一遍前面的——太慢了。

所以模型把 Key 和 Value 两个矩阵存下来（KV cache）。对于 4096 个 token 的序列，KV cache 大约 8 GB。

**问题：** 推理时 KV cache 占内存大，而且如果模型分布在多张 GPU 上，KV cache 需要在 GPU 间传输。

**KV cache 传输优化：**
1. **KV cache 压缩**：把 KV cache 从 FP16 量化到 INT8 或 FP4——传输量减少 50-75%，质量损失很小
2. **前缀缓存（Prefix Caching）**：多个请求共享相同的前缀（比如系统 prompt）→ KV cache 可以共用
3. **缓存感知调度**：把请求路由到已经缓存了相关内容的 GPU 上
4. **分块预填充**：长 prompt 分块处理，逐步预计算 KV cache

**多 GPU 通信策略：**
- **环形拓扑**：GPU 在环里传递 KV cache——简单但延迟高
- **All-to-all**：每个 GPU 发给所有其他 GPU——快但复杂
- **KV cache offloading**：把 KV cache 存在 CPU 内存，需要时拉回 GPU——单个请求慢，但整体内存利用率高

**一句话智慧：最快的通信就是没有通信。** 设计推理系统时尽量让 KV cache 留在本地 GPU，减少跨 GPU 传输。

---

## 22. INT8 versus FP8. What are the tradeoffs? Which precisions are preferred for training and inference?

**简单解释两种 8 位精度：**
- **FP8**：8 位浮点数（有指数位，能表示很大和很小的数）。范围更广，适合训练。
- **INT8**：8 位整数（固定分辨率）。硬件支持更广泛，适合推理。

**对比：**

| 方面 | FP8 | INT8 |
|------|-----|------|
| **动态范围** | 广（能表示极大和极小的数） | 窄（固定范围） |
| **硬件支持** | 较新（H100+ 才支持） | 广泛（所有现代 GPU） |
| **训练质量** | 更好（梯度需要动态范围） | 较差 |
| **推理质量** | 好 | 好（对于静态权重略好） |
| **速度** | 差不多 | 差不多 |

**实际使用建议：**
- **训练**：用 FP8（支持混合精度训练效果好）
- **推理**：用 INT8（更简单，硬件支持更广，对静态权重更友好）

**趋势：** 行业正在往 FP8 训练 + INT8/FP8 混合推理的方向收敛。H100/B200 系列的普及让 FP8 越来越主流。

---

## 23. What is the long-tail problem in RL rollouts, and how can it be addressed?

**什么是长尾问题？**
RL 训练中，大部分 prompt 产生正常长度的回答，但**少数 prompt 产生极长的回答**。这些「长尾巴」回答消耗了不成比例的计算资源。

**类比：** 你在批改作业。大部分学生写 1-2 段。有一个学生写了 50 页。这个学生现在占了 90% 的批改时间。

**为什么是问题：**
- **拖慢训练流水线**：batch 要等**所有** rollout 完成才能继续
- **浪费算力**：长回答不一定是好回答——模型可能只是在啰嗦
- **内存不平衡**：长序列占用更多 GPU 内存，容易 OOM

**解决方法：**
1. **最大长度裁剪**：硬性限制序列长度。简单粗暴，但可能切断有价值的推理。
2. **奖励中的长度惩罚**：在 reward 中惩罚过长的回答——让模型学会简洁，不依赖硬裁剪。
3. **自适应算力分配**：根据任务难度动态调整每个 prompt 的计算预算。
4. **提前停止**：如果模型已经得出正确答案，就停止生成。需要在生成过程中做答案提取和验证。
5. **动态批处理（vLLM 风格）**：把不同长度的 rollout 混合打包，动态调整。

---

## 24. What issues does continuous batching introduce in RL training? How do vLLM and SGLang differ?

**Continuous Batching 本来是加速推理的利器，但在 RL 训练里会引入问题：**

**问题：**
1. **生成长度不一致**：不同 prompt 生成长度差异很大。Continuous batching 是为推理服务设计的（有 deadline），RL 训练需要**精确**的 rollout。
2. **内存碎片化**：RL 训练需要存储 rollouts 做多次梯度更新。Continuous batching 没考虑这个需求。
3. **确定性丢失**：Continuous batching 动态重排和批处理请求——破坏可重现性，而 RL 调试非常依赖可重现性。

**vLLM vs SGLang：**

| 方面 | vLLM | SGLang |
|------|------|--------|
| **定位** | 高吞吐推理服务 | 推理 + 训练支持 |
| **RL 集成** | 可以用于推理，但需要适配器 | 内置 RL 支持（SGLang-RL） |
| **Continuous Batching** | 推理方面极好 | 推理和 RL rollout 都好 |
| **确定性** | 未优先考虑 | 更好的确定性执行支持 |
| **KV cache 管理** | PagedAttention（出色） | 类似 |
| **训练钩子** | 无内置 | 有训练感知特性 |

**对于 RL 训练：** SGLang 一般更优（内置 RL 集成）。纯推理服务选 vLLM。

---

## 25. How do you measure utilization in vLLM and SGLang? How do you evaluate KV cache utilization during training?

**利用率指标：**

1. **吞吐量（req/s）**：简单但不全面——高吞吐可能意味着高延迟。
2. **GPU 利用率（%）**：如果 GPU 算力没跑满，说明被内存带宽卡住了。LLM 推理通常是内存带宽瓶颈，GPU 利用率一般在 10-30%。
3. **MFU（Model FLOPS Utilization）**：实际算力 / 理论峰值。推理一般 10-30%，训练 40-60%。
4. **KV cache 利用率：**
   - **缓存命中率**：多少生成的 token 复用了已有缓存
   - **缓存内存使用率**：KV cache 占了多少 GPU 内存 vs 模型权重
   - **缓存重计算率**：因为缓存被驱逐而需要重新计算的频率

**RL 训练特有的指标：**
- **Rollout 吞吐量**：生成阶段每秒处理的 token 数
- **训练吞吐量**：梯度更新阶段每秒处理的 token 数
- **Rollout/训练重叠率**：生成和训练是并行还是串行？

---

## 26. How is backpropagation implemented in large-scale multi-node RL training?

**核心思路：** 反向传播本身和预训练一样，但**多了 RL 特有的数据流**（advantage、reward、KL penalty 等信号）。

**流程：**
1. Rollout 数据被收集
2. 计算 advantage
3. 带着 RL 特有的 loss（policy gradient + KL penalty + 辅助 loss）跑标准反向传播

**分布式实现**使用标准并行技术：
- **Tensor Parallelism**：把一个矩阵乘法拆到多张 GPU 上
- **Pipeline Parallelism**：把模型的不同层放到不同 GPU 上
- **Data Parallelism**：复制模型，拆分 batch

**RL 特有的挑战：**
Rollout 生成（推理）必须用当前策略，而反向传播（训练）更新策略。这产生了一个数据管道问题——如何高效地把生成的数据送到训练循环。

**好比一个工厂：**
产线 A（rollout workers）在不停生产零件 → 质检（计算 advantage）→ 产线 B（训练）用零件改良生产流程 → 改良后的流程同步回产线 A → 循环。

---

## 27. What asynchronous RL frameworks exist, and what synchronization bottlenecks do they solve?

**为什么需要异步 RL？**
同步训练的问题：必须等**所有** rollout worker 都完成，才能开始下一次训练。如果有一个 worker 因为生成长回答而慢了，所有人都等它。

异步 RL = rollout workers 和训练器不互相等待。workers 持续生成数据，训练器持续学习——它们通过一个共享缓冲区通信。

**代表性框架：**

- **IMPALA**：最早的之一。多个 actor（worker）并行生成数据，一个中央 learner 训练。解决的问题：等所有 actor 完成才训练的瓶颈。
- **A3C**：每个 worker 有自己的模型副本，异步计算梯度，发送给参数服务器。
- **AReaL**：专门为 LLM RL 设计。使用 **stale-wait-free 管道**——rollout workers 不需要等待最新策略。
- **slime**：DeepSeek 内部框架。高度优化，针对他们自己的训练配置。

**异步解决的主要问题：**
1. **吞吐量瓶颈**：异步让 GPU 永远不空闲
2. **负载不均衡**：不同 prompt 生成时间不同，异步自然处理
3. **扩展性**：更多 rollout workers = 更多数据，不拖慢训练器

**代价：** 策略可能过时——训练器学到的数据是用较旧版本的模型生成的。这产生了一个 gap。
最后来一个大稿，直接写完发文件：

## 28. In AReaL or other partial rollout frameworks, are KV caches from previous policies preserved?

**简短回答：通常不保留。**

**为什么：**
策略更新（梯度更新后） → 模型权重变了 → KV cache 里的 Key 和 Value 也变了。旧 KV cache 代表旧策略的激活值——新策略用它算出来的结果是不对的。

**类比：** 你在读一本书时画高亮。你学到更多知识后，旧的高亮线不反映你现在的判断了。你需要重读、重画。

**例外——Partial Rollout：**
有些框架在做长序列生成（比如 10K token）时，前几个 token 正在生成的过程中策略更新了。理论上可以复用**已经生成部分**的 KV cache，只重新计算剩余部分。技术上极其困难，大多数框架不这么做。

**实用替代方案：** 使用**前缀缓存（prefix caching）**。prompt 部分的 KV cache 是稳定的（不依赖于策略）。缓存 prompt 部分，只有生成的延续部分变了。

---

## 29. How does Expert Parallelism affect MoE throughput?

**Expert Parallelism（EP，专家并行）= 不同的专家放在不同的 GPU 上。**

**好处：**
- 每个 GPU 只存一部分专家 → 内存效率高
- 可以拥有比一张 GPU 能装下的更多专家
- 更多 GPU → 更多专家 → 更大模型容量

**坏处（瓶颈）：**
- **All-to-all 通信风暴**：每个 token 需要发送到对应的专家所在的 GPU。对于 256 个专家分布在 128 张 GPU 上，一半的 token 需要离开自己的 GPU。
- **负载不均衡**：如果某个专家得到的 token 是另一个的 2 倍，它的 GPU 在忙，别的 GPU 却是空闲的
- **Pipeline bubbles（流水线气泡）**：专家并行 + 流水线并行混合使用时，GPU 经常在等数据

**吞吐量影响：**

| 系统 | EP 对吞吐量的影响 |
|------|------------------|
| 稠密模型（无 MoE） | 0%（不用 EP） |
| MoE 无 EP | 不可能（装不进内存） |
| MoE + EP（均衡） | 10-20% 额外开销来自 all-to-all |
| MoE + EP（不均衡） | 30-50% 额外开销（等慢的 worker） |

**优化方法：**
1. **专家分组**：把相关专家放到同一张 GPU 上，减少跨 GPU 路由
2. **Top-2 路由 vs Top-1**：Top-1 减半 all-to-all 通信量
3. **动态专家放置**：根据负载模式在 GPU 间移动专家

---

## 30. In long-context training, how should compute-communication overlap be designed? How do Megatron and FSDP differ in parallelism strategies?

**挑战：** 长上下文（128K+ token）意味着注意力计算需要很长时间。在这个计算期间，通信（All Reduce）应该**在后台进行**——这就是「计算-通信重叠」。

**设计原则：** 尽早开始通信。一部分计算完成后，立即开始传输这部分结果，同时继续计算剩余部分。不浪费任何等待时间。

**Megatron-LM vs FSDP：**

| 方面 | Megatron-LM | FSDP |
|------|-------------|------|
| **策略** | 混合并行：TP + PP + DP + EP | 纯 FSDP（分片一切） |
| **何时通信** | 每层后（pipeline）或每子层后（tensor） | 每次前向/反向之前和之后 |
| **内存** | 每 GPU 更低（激进分片） | 每 GPU 更高（但更简单） |
| **重叠设计** | 细粒度（pipeline 微批次隐藏通信） | 粗粒度（计算当前参数时预取下一批） |
| **最适合** | 需要最大吞吐量的大模型（100B+） | 较简单的中等以上模型 |
| **复杂度** | 极高（5D 并行） | 低（只需分区 + FSDP） |

**实用建议：**
- **70B+ 模型**：用 Megatron（每一点吞吐量都值得复杂的工程投入）
- **<30B 模型**：用 FSDP（团队开发效率比极致吞吐量更重要）
- **长上下文特别提示**：Megatron 的 tensor parallelism 有助于拆分注意力计算，减少每 GPU 的 KV cache 内存

---

## 31. How do you enable deterministic execution? What is batch invariance? What causes it? Is atomic add involved? Can atomic add solve the issue?

**Deterministic Execution（确定性执行）**：同一段代码跑两次，得到完全一样的结果。RL 调试极度依赖这个——你需要能复现训练过程，才能理解某个改动为什么有效或无效。

**为什么难以实现？**
- GPU 操作天生非确定性（并行计算中的求和顺序不同，结果就不同）
- `atomicAdd`（GPU 上原子累加操作）是**非确定性**的
- 浮点数加法不满足结合律：(a + b) + c ≠ a + (b + c)

**Batch Invariance（批处理不变性）：**
模型的输出会因为你改变了 batch size 而改变——即使输入完全相同。原因：不同 batch size 导致不同的并行化模式和浮点数累加顺序。

**`atomicAdd` 的角色：**
在 softmax、layer normalization 等操作中，梯度用 `atomicAdd` 累加。哪个线程先完成、以什么顺序累加——这些都不确定。所以 `atomicAdd` 是**问题的一部分**，不是解决方案。

**`atomicAdd` 能解决这个问题吗？**
不能。`atomicAdd` 提供线程安全但不提供确定性。不同的线程调度导致不同的原子累加顺序。

**解决方案：**
1. **CUDA 确定性标志**：`CUBLAS_WORKSPACE_CONFIG=:4096:8` + `torch.use_deterministic_algorithms(True)`——有效但变慢
2. **关键路径避免原子操作**：使用确定性变体
3. **种子随机操作**：确保所有随机操作有固定种子
4. **固定 batch size**：训练和评估之间不改变 batch size

---

## 32. How do AReaL and slime differ in their understanding of the RL rollout bottleneck?

**AReaL 的观点：**
瓶颈是**同步**。rollout workers 和训练器紧密耦合 → 一个 worker 慢（长尾 prompt），所有人都在等。解决方案：异步、非阻塞的 rollout 生成。

**slime（DeepSeek 内部框架）的观点：**
瓶颈是**数据流效率低**。在 rollout 生成和训练之间移动数据需要复杂的管道和队列。数据本身很大（长序列）。解决方案：把生成和训练紧密集成到一个优化的管道中。

**对比：**

| 方面 | AReaL | slime |
|------|-------|-------|
| **瓶颈诊断** | workers 间的同步 | 阶段间的数据传输 |
| **解决方案** | 异步、非阻塞 | 集成管道、最小化数据传输 |
| **代价** | 策略过时（rollout 来自旧策略） | 实现困难、不够灵活 |
| **适合** | 异构计算环境 | 同质集群（DeepSeek 场景） |

**两个都对。** 选择取决于你的基础设施：
- GPU 性能参差不齐 → AReaL
- 集群高度统一、可控制 → slime

---

## 33. How should we think about staleness in fully asynchronous RL training? What are typical values in practice?

**Staleness（过时度） = rollout 数据生成时和当前策略相差了多少训练步。**

**为什么重要：**
旧策略产生的旧数据「过期了」。当前策略已经进化了。在过时数据上训练可能会把当前策略推向错误的方向。

**类比：** 你在学做饭。你的朋友尝了你上周做的菜并给了反馈。但那之后你又学了新技术——那个反馈是「过时的」，可能不再适用于你现在的水平。

**可接受的过时度：**
- **非常过时（>1000 步）**：危险。旧策略和当前策略基本是两个不同的模型了。
- **中等过时（50-500 步）**：可以接受——如果学习率低，策略变化不大。
- **最小过时（<10 步）**：几乎没有影响。

**实际典型值：**
- **IMPALA 风格**：50-200 步的过时（常见）
- **AReaL 声称**：<5 步（设计目标是最小化过时）
- **简易异步方案**：可达 500+ 步（有问题）

**缓解策略：**
1. **重要性采样校正**：根据过时数据与当前策略的相关性重新加权
2. **V-trace（IMPALA）**：用截断的重要性采样来校正策略不匹配
3. **过时加权**：显式降低更旧数据的权重（AReaL 方法）
4. **定期同步**：不完全异步——每 N 步同步一次

---

## 34. How does data flow through slime? How is it integrated with Megatron? How is the loss computed?

**这是 DeepSeek 特定的基础设施。** Slime 是他们的内部 RL 训练系统。具体细节是保密的，但架构在高层面上是知道的：

**数据流：**
1. **推理阶段**：多个 rollout workers 用当前策略生成回答。Megatron 处理模型并行推理。
2. **回放缓冲区**：生成的数据（prompt + 回答 + reward）进入分布式缓冲区。
3. **训练阶段**：训练器从缓冲区拉取数据，计算 advantage（用 GRPO 或类似方法），执行梯度更新。
4. **策略更新**：新权重发布。Rollout workers 最终拉取新策略。

**与 Megatron 的集成：**
> Slime 使用 Megatron 的模型并行基础设施（tensor + pipeline parallelism）来做推理和训练。Megatron 处理底层分布式计算；slime 处理 RL 特有的编排。

**Loss 计算：**
loss 是标准 GRPO loss：
```python
loss = - (1/G) * Σ(advantage * min(r, clip(r))) + β * KL(policy || reference)
```
- G = group size（每个 prompt 的回复数）
- r = 重要性采样比率 = π_new / π_old
- advantage = (reward_i - group_mean) / group_std
- β = KL penalty 系数
- KL = 当前策略和参考策略之间的逐 token KL 散度

---

## 35. If you had to choose among VeRL, TRL, Unsloth, AReaL, and slime, which one would you use and why?

```text
问题：你的首要目标是什么？

├── 只想在 1-2 张 GPU 上快速跑 RL？
│   └── ➡️ Unsloth（最简单、LoRA 友好、门槛最低）

├── 做算法研究和对比？
│   └── ➡️ TRL（HuggingFace 生态、算法最全）

├── 构建大规模生产训练系统？
│   ├── 有 DeepSeek 那样的同质集群？→ slime（吞吐量最高）
│   ├── 需要异步 + 可扩展？→ AReaL（最好的异步架构）
│   └── 想要开源、经过验证的？→ VeRL（伯克利 Voltron RL）

└── 只是想学习 RL 概念？
    └── ➡️ 从 TRL 开始，进阶到 VeRL
```

**我的推荐：**
- **做实验**：Unsloth 或 TRL
- **严肃训练（单集群）**：VeRL（开源、活跃开发中）
- **企业级（多集群）**：AReaL（大规模场景下异步架构很重要）
- **DeepSeek 级别（定制基础设施）**：slime（但你需要他们的团队）

---

> **Good luck.** 面试准备有帮助，但真正理解远比背答案走得更远。
>
> *以上详解的目标是让刚高中毕业的同学也能理解 RL 的核心概念和思维方式。无论你是准备面试还是想深入学习，理解「为什么」比记忆「是什么」重要得多。*
