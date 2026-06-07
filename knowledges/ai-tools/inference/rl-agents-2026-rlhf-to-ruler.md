---
title: "2026 年顶级 AI 实验室如何构建 RL Agent——从 RLHF 到 RULER"
tags:
  - reinforcement-learning
  - agents
  - rl-agent
  - grpo
  - ruler
  - reward-function
date: 2026-06-06
source: "https://x.com/_avichawla/status/2049037299334472015"
authors: "Avichawla"
---

# 2026 年顶级 AI 实验室如何构建 RL Agent——从 RLHF 到 RULER

> **来源：** [Avichawla 的 X 长文](https://x.com/_avichawla/status/2049037299334472015)
>
> 深入解析 Anthropic、OpenAI、DeepSeek 如何趋同于一个核心思想：**把 System Prompt 当作 Reward Function**。从 RLHF 到 RULER 的完整进化脉络，附代码。

![封面：RL Agent Evolution](../image/rl-agents-2026-cover.jpg)

---

## 一、强化学习的核心框架

强化学习的本质很简单：**系统采取行动 → 环境给予奖励 → Agent 更新行为以最大化长期奖励。**

在每个时间步，三个事件按顺序发生：

1. **Agent 观察当前状态 (S)**——比如国际象棋中的棋盘局面，或对话模型中的对话历史
2. **Agent 根据观察选择行动 (A)**——对于 LLM 来说，就是生成的响应
3. **环境做两件事**：转移到新状态 (S')，并发出标量奖励 (R)

把这些步骤串起来就构成了一个**轨迹（Trajectory）**：

```
S0 → A0 → R1 → S1 → A1 → R2 → S2 → ...
```

**每个 (S, A, R, S') 四元组是一次转移**，RL 很大程度上就是学习如何从这些转移中优化。

![RL 基础框架](../image/rl-agents-2026-1.jpg)

---

## 二、RLHF 时代：人类的偏好作为奖励信号（2022 年）

当 RL 首次应用于 LLM 时，**环境就是人类的偏好**。

OpenAI 的 InstructGPT（2022）引入 RLHF（Reinforcement Learning from Human Feedback），核心流程如下：

1. **人类对模型输出进行排序**
2. 这些排序用来训练一个**奖励模型（Reward Model）**
3. **PPO（Proximal Policy Optimization）** 用这个奖励模型来微调 LLM

ChatGPT 正是基于这条管线构建的。

![RLHF 流程](../image/rl-agents-2026-2.jpg)

### 两个阶段分离

但人类不可能坐在训练循环中实时评价每一次输出——如果每轮生成 16 个响应，成千上万个训练步，那就是数十万次评估。

OpenAI 将其分为两个阶段：

- **离线阶段（Offline）**：人类对相对小规模的模型输出进行排序，生成两两比较数据。昂贵的人力成本，但一次性投入。
- **训练阶段**：基于这些排序训练一个奖励模型（独立的 LLM），学会预测人类偏好。这样你就有了一个神经网络，能瞬间为任何输出打分，无需等待人类。

![两阶段分离](../image/rl-agents-2026-3.jpg)

### PPO 的代价：四个模型同时驻留内存

有了奖励模型，PPO 就能以 GPU 速度运行实际 RL 训练。但代价是 PPO 需要**四个完整模型同时在内存中**：

| 模型 | 作用 |
|------|------|
| **Policy**（主策略） | 正在训练的 LLM |
| **Reference Policy**（参考策略） | 原始模型的冻结副本，通过 KL 散度惩罚防止训练偏离太远 |
| **Reward Model**（奖励模型） | 上面讨论的人类偏好近似器 |
| **Critic / Value Model**（评判器） | 评估「这个奖励相对于该提示的预期是好是坏」 |

为什么需要 Critic？因为原始奖励 0.7 单独看没有意义。

- 对于简单事实性问题（通常得 0.9），0.7 是**低于平均**
- 对于复杂开放性问题（通常得 0.4），0.7 是**优秀**

Critic 通过学习数千个 (prompt, reward) 对来建立这个基线，PPO 的实际训练信号是 **Advantage = Reward − Critic 基线**。

代价是：Critic 本身也是一个完整的 LLM。对于一个 7B 参数的 LLM，意味着同时约 **28B 参数在内存中**。

![PPO 架构](../image/rl-agents-2026-4.jpg)

---

## 三、DeepSeek R1 的突破：可验证奖励（2025 年 1 月）

2025 年 1 月，DeepSeek 发布 R1，从根本上改变了奖励信号的来源。

**不再训练基于人类偏好的奖励模型**，而是使用 **RLVR（Reinforcement Learning with Verifiable Rewards）**——一种简单的、基于规则的验证方式，由环境本身提供信号：

| 领域 | 验证方式 |
|------|----------|
| 数学问题 | 验证器检查模型的答案是否与已知解匹配 |
| 代码 | 编译器运行输出，返回通过/失败 |

**没有人类排序，没有显式的奖励模型**——因为真实答案可用（或可推断）作为奖励。

奖励是二元的：正确=1，错误=0。

### GRPO：大幅简化架构

优化器是 **GRPO（Group Relative Policy Optimization）**，去掉了 PPO 的大部分基础设施：

**它移除了 Critic 模型。**

不再训练一个单独的模型来预测每轮提示的预期奖励，GRPO 对**同一提示生成多个响应（通常 16 个）**，然后在每组内归一化奖励值。

- 如果 16 个响应中有 4 个答对了数学题，这 4 个获得正 Advantage，其余 12 个获得负 Advantage

这一刀切掉了整整一个完整模型的内存。GRPO 也移除了学习型奖励模型，因为 RLVR 的验证器直接处理打分。

于是，PPO 的**四模型架构（Policy + Reference + Critic + Reward Model）**坍缩为**两个（Policy + Reference）**。实际上，有些实现甚至将 Reference 折叠进 Policy 的检查点，接近**单模型设置**。

![PPO vs GRPO](../image/rl-agents-2026-5.jpg)

### 效果

DeepSeek R1-Zero（仅用 GRPO + 可验证奖励训练，没有做监督微调）：

- AIME 2024 数学：从 15.6% 提升到 **77.9%**
- 加上 Majority Voting：**86.7%**，与 OpenAI o1 持平

**模型自动发展出自我验证、反思和思维链推理能力**，纯粹来自二元的正确/错误信号——没有人教它一步步推理。RL 训练循环发现「推理能提高奖励」，于是模型学会了推理。

RLVR + GRPO 成为 2025 年训练推理模型的主导方法，每个大实验室都发布了遵循这个配方的推理变体。

---

## 四、问题：Agent 工作流没有可验证的奖励

GRPO 本身就是通用型优化器——它不关心奖励来自数学验证器、代码编译器、人类还是 Python 脚本。它只需要每个响应有一个数字，然后在组内归一化。

真正的瓶颈在于：**这些奖励从哪里来？**

对于数学和代码来说没问题——环境提供确定性信号。但对于与真实世界工具和数据交互的 Agent：

| 场景 | 问题 |
|------|------|
| **RAG Agent** | 检索上下文后生成响应，没有一个标准答案可以字符串匹配 |
| **客户支持 Agent** | 起草回复，没有编译器来检测 |
| **摘要 Agent** | 压缩 20 页文档，许多有效的摘要，没有验证器能区分好坏 |

![Agent 的奖励困境](../image/rl-agents-2026-3.jpg)

对于这些任务，环境不会像数学题那样直接提供奖励信号。RLVR 对可验证的任务仍然有效，但对于大多数 Agent 工作流，**产出是主观或多维的**。

### 一种中间方案：自定义奖励函数

一种思路是用 Python 代码为每个输出打分：

```python
def reward_function(response, context):
    score = 0.0
    if uses_context(response, context):
        score += 0.4
    if not has_hallucination(response, context):
        score += 0.3
    if is_complete(response, context):
        score += 0.2
    if is_concise(response):
        score += 0.1
    return score
```

但这引入了一系列问题：

| 问题 | 说明 |
|------|------|
| **开发周期长** | 写好一个奖励函数需要数天的迭代 |
| **脆弱性** | 改变检索管线、添加新工具、修改 system prompt 都需重写 |
| **调试困难** | Agent 学到不良行为时，无法确定是奖励函数、超参数还是数据的问题 |
| **权重校准** | 过分强调格式合规而低估忠实度，会训练出一个产出「格式精美的幻觉」的 Agent |

**正是这个原因导致 RL 在可验证任务（数学、代码、逻辑）中被广泛采用，但对 Agent 工作流（RAG、客服、工具使用、摘要）却一直未能大规模落地。**

核心区分不在于模型（同一个 Qwen 2.5 14B 可以充当两种角色），而在于**任务本身**：Agent 的产出能否被自动检查？

---

## 五、各大 AI 实验室的趋同方向

各大 AI 实验室从不同方向汇聚到同一个问题上。

### Anthropic：Constitutional AI

Anthropic 证明你**根本不需要人类在 RL 循环中**。

他们的 **Constitutional AI** 表明：写下一套原则（一部「宪法」），AI 就能根据这些原则自行评估输出，生成用于 RL 训练的偏好数据。

> AI 自己判断输出是否符合书面原则，并将这些判断作为 RL 信号。
>
> 这是一个重要的概念转变：**一纸规则取代了人类评估大军。**

### OpenAI：Universal Verifiers

OpenAI 在内部开发 **"Universal Verifiers"（通用验证器）**，将 RL 扩展到数学和代码之外的领域（生物、医药、通用知识），在这些领域无法用简单的字符串匹配来检查答案。

细节未公开，但方向明确——**我们需要跨领域通用的奖励信号**，而不仅仅是有确定性验证器的那些领域。

### Karpathy：System Prompt Learning

Karpathy 在 2025 年指出，我们缺少 LLM 的一个重大学习范式，他暂时称之为 **"System Prompt Learning"**。

核心思想是：**System Prompt 携带的信号比标量奖励更丰富**，RL 训练应该找到利用这一信号的方法，而不是仅仅依赖手工打造的奖励函数。

---

## 六、RULER：通用奖励函数

**RULER** 构建于 OpenPipe 的 **ART 框架**（开源，9000+ Star），是一个通用奖励函数，用**单个函数调用**替代了所有自定义打分代码。

### 核心原理

RULER 使用 **LLM-as-Judge** 对多条轨迹进行**相对排序**。它利用的是 GRPO 的同一个特性：**只有相对排名才重要。**

工作流程：

1. 每个训练步，对同一场景生成 N 条轨迹（通常 4-8 条）
2. RULER 将所有 N 条发送给 Judge LLM（如 o3、o4-mini，甚至是本地 Qwen3 32B）
3. Judge 读取 Agent 的 System Prompt，理解 Agent 应该做什么，然后对各条轨迹进行 0-1 的相对打分

**为什么有效？两个关键特性：**

#### 特性 1：相对打分比绝对打分更容易

LLM 在绝对打分上表现不佳，因为没有共享校准基准。但问「这 4 个响应中哪个最符合 System Prompt 的指令」是一个**比较任务**，LLM 在这方面表现始终不错。

RULER 把全部轨迹放在一起，让 Judge 相互比较排序。

#### 特性 2：GRPO 本来就在组内归一化

最优轨迹在绝对意义上得了 0.9 还是 0.3 都无关紧要——GRPO 在组内计算均值标准差并归一化。训练信号来自**相对排序**（哪些高于平均、哪些低于平均）。RULER 的相对排名直接映射到 GRPO 的期望上。

### 一个简单的例子

以训练一个 RAG Agent 为例。传统方式需要分别实现 `uses_context()`、`has_hallucination()`、`is_complete()`、`is_concise()`，每个都是独立的工程。

用 RULER：

```python
from art.rewards import ruler

# System Prompt 已经隐含了评估标准
system_msg = {
    "role": "system",
    "content": (
        "You are a RAG-based support agent. "
        "Answer user queries using ONLY the retrieved context. "
        "Do not add information that is not in the context."
    ),
}

user_msg = {
    "role": "user",
    "content": (
        "What is the refund policy?\n\n"
        "[Retrieved context]: Refunds are available within 30 days ..."
    ),
}

# 三条轨迹：忠实的、编造的、忽略上下文的
message_lists = [...]

scores = await ruler(message_lists, "openai/o3")
```

输出示例：

```
Faithful（忠实）:           → 0.97
Hallucinated（编造）:       → 0.45
Ignored context（忽略上下文）:→ 0.05
```

注意这里**没有编写任何忠实度检查器或幻觉检测函数**。System Prompt 提到 "Use the retrieved context to answer accurately"，Judge 将其作为评估标准。

- 编造的响应得了 0.45（不是 0），因为它部分使用了上下文（30 天退款部分正确）
- Judge 给出了**部分分数**——这种细微差别用基于规则的奖励函数需要大量工程才能实现
- 分数覆盖 0-1 的梯度（0.97、0.45、0.05），不是二元通过/失败
- GRPO 能用这个梯度做比例更新：强烈强化忠实行为，适度抑制编造模式，强烈抑制忽略上下文

### 完整的训练循环

```python
for step in range(num_steps):
    groups = await art.gather_trajectory_groups(
        (
            art.TrajectoryGroup(
                rollout(model, scenario) for _ in range(4)
            )
            for scenario in scenarios
        ),
        after_each=lambda g: ruler_score_group(
            g, "openai/o3"),
    )
    await model.train(groups)  # GRPO updates LoRA weights
```

每步：模型用当前权重生成 4 个响应 → RULER 相对排名 → GRPO 强化高分行为、抑制低分行为。整个过程中没有定义任何奖励函数。

### Trajectory 和 TrajectoryGroup

```python
import art
from openai.types.chat.chat_completion import Choice
from openai.types.chat import ChatCompletionMessage

trajectories = []
for resp in responses:
    traj = art.Trajectory(
        messages_and_choices=[
            system_msg, user_msg,
            Choice(
                finish_reason="stop", index=0,
                message=ChatCompletionMessage(role="assistant", content=resp),
            ),
        ],
        reward=0.0,  # RULER fills this in
    )
    trajectories.append(traj)

group = art.TrajectoryGroup(trajectories=trajectories)

# RULER 打分
judged_group = await ruler_score_group(group, "openai/o3", debug=True)
```

Debug 模式下输出：

```json
{
    "scores": [
        {
            "trajectory_id": "1",
            "explanation": "Accurately answers the question using only the retrieved context, concisely and completely.",
            "score": 0.98
        },
        {
            "trajectory_id": "2",
            "explanation": "Includes unsupported details about store credit and a hotline that are not in the retrieved context.",
            "score": 0.2
        },
    ]
}
```

### 自定义 Rubric

如果需要更具体的评估标准：

```python
custom_rubric = """
- Prioritize responses that are concise and clear
- Penalize responses that include emojis or informal language
- Reward responses that cite sources
"""

await ruler_score_group(group, "openai/o3", rubric=custom_rubric)
```

Rubric 是自然语言，不是 Python——迭代非常快。改一个句子，重新跑，检查分数。相比修改奖励函数（一个错误的权重或条件缺陷可能在训练过程中悄悄教给 Agent 不良行为，直到训练结束后才发现），这要高效得多。

### 与确定性验证结合

RULER 是通用的。对于可以同时用两种方法的场景：

```python
judged_group = await ruler_score_group(group, "openai/o3")

for traj in judged_group.trajectories:
    independent_reward = verify_correctness(traj)  # binary 0/1
    traj.reward += independent_reward
```

RULER 在 rollout 期间会保留你指定的任何奖励作为独立的 metric，所以你可以将 LLM-Judge 打分叠在确定性验证之上，两个信号都不会丢失。

### 实用建议

| 参数 | 建议 |
|------|------|
| **Judge 模型选择** | 不需要最昂贵的模型。Qwen3 32B 通常表现也不错。Claude、通过 Ollama 的本地模型、或 LiteLLM 支持的任何模型均可 |
| **每组轨迹数量** | 推荐 **4-8 条**。少于 4 条，Judge 可比较的样本太少；多于 8 条可能混淆 Judge 且成本不成比例增加 |
| **Token 优化** | 当所有轨迹共享同一 System Prompt 和用户消息时，RULER 自动去重公共前缀，只让 Judge 看到共享上下文一次 + 不同响应 |
| **缓存** | RULER 将 Judge 响应缓存到磁盘。调试时重复跑相同轨迹不会重复调用 API |

---

## 七、总结：RL for Agent 的瓶颈已解

```
应用于 Agent 的 RL 瓶颈从来不在优化算法上（GRPO 处理得很好），
而是一直在奖励信号上。
```

| 阶段 | 奖励信号 | 瓶颈 |
|------|----------|------|
| **RLHF（2022）** | 人类偏好 → 奖励模型 | 人类速度慢，四模型内存 |
| **RLVR + GRPO（2025）** | 环境验证（数学/代码） | 仅限可验证任务 |
| **RULER（2026）** | System Prompt → LLM Judge 相对打分 | 通用，适用于一切 |

RLVR 为可验证任务解决了问题——让环境直接打分。**RULER 为所有任务（可验证或不可验证）解决了问题——让 LLM Judge 相对打分。**

完整实现在 [OpenPipe/ART](https://github.com/OpenPipe/ART) 仓库中，包含详尽的 Colab Notebook。

---

*整理于 2026-06-06，基于 Avichawla 的 X 长文[《How top AI labs are building RL agents in 2026》](https://x.com/_avichawla/status/2049037299334472015)*
