# Deep Reading Report: Learning Agent-Compatible Context Management for Long-Horizon Tasks

> **论文**: *Learning Agent-Compatible Context Management for Long-Horizon Tasks* (AdaCoM)
> **作者**: Lu Yi, Runlin Lei, Liuyi Yao, Yuexiang Xie, Yuyang Li, Wenhao Zhang, Zhewei Wei, Yaliang Li, Jian-Yun Nie
> **机构**: 中国人民大学 + 阿里通义实验室 + 北京邮电大学 + 蒙特利尔大学
> **状态**: arXiv 2026-05-29 (ACL 投稿级)
> **阅读模式**: LaTeX-primary（主文 + 附录完整获取）

---

## 1. 论文识别与源文件

### Anchored Points
- [C1.0] **Paper**: *Learning Agent-Compatible Context Management for Long-Horizon Tasks* — **AdaCoM**
- [C1.1] **Authors**: Lu Yi, Runlin Lei (co-first), Zhewei Wei & Yaliang Li (corresponding)
- [C1.2] **Source**: 完整 LaTeX 包（main.tex 60KB + appendix.tex 56KB + symbol.tex + custom.bib）
- [C1.3] **模式**: LaTeX-primary，80 个段落锚点

---

## 2. 一句话核心与研究方程

### Anchored Points
- [C2.1] **一句话**: AdaCoM 用一个外部小 LLM 作为上下文管理器，通过强化学习为每个"冻住"的 Agent 发现专属的上下文管理策略，揭示了"保真度-可靠性权衡"（强 Agent 保留更多原始上下文，弱 Agent 需要更激进压缩）
- [C2.2] **研究方程**:
  - **过去成功**: ReAct 风格的 Agent 在短任务中工作良好
  - **被打破的假设**: Agent 可以无限累积上下文而不退化
  - **困难场景**: 长程任务（35+ 步的 Web 搜索和深度研究）
  - **借用的工具**: 外部小 LLM + 强化学习（GRPO）
  - **不可用的机制**: 直接训练 Agent 本身的内建上下文管理能力（因为闭源 Agent 拿不到梯度）
  - **替代机制**: 外部的可学习管理器通过结构化 JSON 操作修改上下文，在不接触 Agent 的情况下发现专属策略

**紧凑形式**: `A(ReAct) ∩ ¬C(无限上下文假设) ∩ T(长程任务) ∩ M(外部管理器+RL) => Z≈Y(保真度-可靠性权衡)`

---

## 3. 标题解读

### Anchored Points
- [C3.1] **Learning** → 管理器是通过 RL 训练出来的，不是手工设计的。这是关键：让 AI 自己发现 Agent 需要什么样的上下文，而不是人告诉它
- [C3.2] **Agent-Compatible** → 管理策略必须适配**特定 Agent** 的推理风格。不同 Agent（Qwen vs Kimi vs DeepSeek）需要不同的压缩策略
- [C3.3] **Context Management** → 不是做更好的向量检索或长期记忆，而是管理单个会话内的**工作记忆**（working memory），核心操作是保留/删除/改写
- [C3.4] **Long-Horizon Tasks** → 35+ 步交互的 Web 搜索和深度研究。不是 RAG 的"大海捞针"，而是多步推理中上下文逐渐膨胀的退化问题

**更具体的标题应该是什么**: "Training an External LLM to Discover Agent-Specific Context Modification Strategies via Reinforcement Learning for Frozen Agents on Long-Horizon Web Search Tasks"

---

## 4. 论文真正解决的问题

### Anchored Points
- [C4.1] **直接问题**: 长程 LLM Agent 的上下文累积导致性能退化（约束遗忘、过早放弃、冗余搜索）
- [C4.2] **实际痛点**: 现有方法要么要求训练 Agent 本身（对闭源 Agent 不可行），要么使用固定的压缩策略（对多种 Agent 不兼容）
- [C4.3] **科学问题**: 对于不可训练的 Agent，如何自动发现最适合它的上下文管理策略？
- [C4.4] **母领域压力**: 随着 OpenClaw、Hermes、Claude Code 等 Agent 产品落地，长任务可靠性成为关键瓶颈，但主流 Agent 都不可训练

---

## 5. 科学问题阶梯

### Anchored Points
- [C5.1] **论文层级**: 外部管理器 + RL → 为冻结 Agent 发现最佳上下文管理策略
- [C5.2] **上层 1 — Agent 系统设计**: 如何在不改变 Agent 本身的情况下提升其长程能力？
- [C5.3] **上层 2 — AI 工程化**: 如何让 AI 系统稳定可靠地运行长周期任务？
- [C5.4] **方法引入的新瓶颈**: 管理器本身需要训练 → 在闭源 Agent 场景没有训练数据 → 只能用 Agent 的最终结果作为 RL 信号 → 稀疏奖励问题突出

---

## 6. 作者可能如何发现这个方向

### Anchored Points
- [C6.1] **合理推演**: 作者可能来自 Agent 框架开发团队（通义实验室），在日常工作中反复遇到长任务退化问题。尝试过 ReSum/IterResearch 等加速方法后发现不稳定。注意到"不同 Agent 对同一任务的失败模式不同"，意识到需要个性化策略
- [C6.2] **关键转移**: 提出"既然 Agent 不能训练，那就在外面放一个管理器"。把问题从"让 Agent 学会管理上下文"重新定义为"让管理器学会理解 Agent"

| 有价值领域 | 痛苦的假设 | 借用/新兴工具 | 阻塞约束 | 概念替代 |
|-----------|-----------|-------------|---------|---------|
| Agent 系统设计 | Agent 必须自己管理上下文 | 外部 LLM + RL ✅ | Agent 不可训练 | "从内到外" → "从外到内" |
| 长上下文推理 | 固定策略对所有 Agent 都有效 | 结构化 JSON 操作 ✅ | 无法预知最佳策略 | "手工设计" → "RL 发现" |
| 闭源 Agent 部署 | 每个 Agent 需要单独优化 | GRPO + 过程奖励 ✅ | 训练成本 | 用 4B 管理器 + 跨 Agent 迁移 |

---

## 7. 作者如何构建故事

### Anchored Points
- [C7.1] **故事结构清晰**: 问题（长上下文退化）→ 现有方案的不足（训练依赖+一刀切）→ 核心想法（外部管理器+RL）→ 实验验证 → 新发现（保真度-可靠性权衡+跨 Agent 迁移）
- [C7.2] **形成闭环**: 每个设计模块都对应一个具体的失败模式（见下表）

| 挑战 | 失败模式 | 设计原则 | 模块 | 证据 |
|------|---------|---------|------|------|
| 上下文累积退化 | 约束遗忘、过早放弃 | 架构解耦 | 外部管理器 + 冻结 Agent | C1.1 |
| 不同 Agent 需要不同策略 | Summarization 会伤害部分 Agent | 操作级灵活性 | JSON 动作空间 | C1.3, C3.3 |
| 管理器需要训练 | 未训练的管理器降低性能(-8.9%) | RL 训练 | GRPO + 双层优势估计 | C3.1 |
| 训练成本高 | 每个 Agent 都训练不现实 | 跨 Agent 迁移 | 迁移实验 | C5.1 |

---

## 8. 相关工作与引文分析

### Anchored Points
- [C8.1] **引文群分类**:
  - **领域锚点**: OpenClaw、Hermes Agent → 证明长程 Agent 场景的现实重要性
  - **限制证据**: Attention Sink, Lost in the Middle, Distraction → 为什么需要上下文管理
  - **方法先祖**: MEM1, IterResearch, ReSum, MemAct → 现有方法，均需 Agent 训练
  - **基线压力**: BrowseComp-Plus, MCP-Bench → 评估框架
  - **协议论证**: GRPO, Trinity-RFT → 为什么用 RL
  - **对比边界**: Mem0, A-Mem, Memory-R1, G-Memory → 长期记忆 vs 工作记忆

- [C8.2] **关键空白**: 所有相关工作要么需要 Agent 训练，要么使用固定操作。没有工作探索过"为冻结 Agent 学习个性化上下文管理策略"

---

## 9. 核心思想

### Anchored Points
- [C9.1] **概念替代**: 把"上下文管理"从 Agent 的自带能力重新定义为 **"可训练的外部过滤器"**，它对 Agent 的操作空间完全不可见
- [C9.2] **协调逻辑**: 管理器不是理解"上下文哪里不好"，而是理解"这个 Agent 在什么样的上下文下表现更好"。管理器学到的不是"怎么压缩内容"，而是"这个 Agent 需要什么样的信息呈现方式"

---

## 10. 符号、假设与记法

### Anchored Points
- [C10.1] **关键符号**:

| 符号 | 含义 | 备注 |
|------|------|------|
| $q$ | 任务查询 |  |
| $c_t^{\mathrm{vanilla}}$ | 第 t 步的原始累积上下文 | $(q, a_1, o_1, ..., a_t, o_t)$ |
| $\tilde{c}_t$ | 第 t 步的管理后上下文 | 管理器修改后的版本 |
| $m_t$ | 第 t 步的管理器动作 | 结构化 JSON 操作列表 |
| $p_t$ | 第 t 步的管理器提示词 | $\mathcal{P}(c_t)$ 构造 |
| $\pi_\theta$ | 管理器策略 | Qwen3-4B-Instruct |
| $A^R_i$ | 任务级优势 | 归一化的结果奖励 |
| $A^Q_{i,t}$ | 步骤级优势 | 归一化的过程奖励 |
| $\alpha$ | 过程奖励权重 | 设为 0.1 |

- [C10.2] **隐藏假设**: 过程奖励（token 惩罚、冗余动作惩罚）是上下文质量的良好代理信号

---

## 11. 关键公式详解

### Anchored Points
- [C11.1] **管理动作**:

$$m_t = [\delta_t^{(1)}, \delta_t^{(2)}, ..., \delta_t^{(n_t)}]$$

每个 $\delta_t^{(j)}$ 包含 4 个字段：`ids`（目标消息）、`role`（system/user/assistant）、`justification`（推理理由，最终从上下文中移除）、`new_content`（新内容，空则表示删除）。

**说明**: 四种基本操作（保留不变、重写、合并、删除）通过这个统一格式表达。`justification` 字段是关键设计：它迫使管理器在修改前进行推理，但推理过程不会被 Agent 看到。

**脆弱点**: 动作空间仅支持当前步骤的操作，不支持跨步骤规划。管理器在做第 t 步决策时不知道未来几步会怎样。

- [C11.2] **双层优势估计**:

任务级：$A^R_i = \frac{R_i - \mu_R}{\sigma_R + \varepsilon}$

步骤级：$A^Q_{i,t} = \frac{Q_{i,t} - \mu_Q}{\sigma_Q + \varepsilon}$

组合：$A_{i,t} = A^R_i + \alpha A^Q_{i,t}$

重新归一化：$\hat A_{i,t} = \frac{A_{i,t} - \mu_A}{\sigma_A + \varepsilon}$

**说明**: 关键设计是"先分别归一化再组合"，而不是直接相加。这解决了结果奖励和过程奖励数值范围的差异。当 $\sigma_R = 0$（同一组所有 rollout 结果相同），任务级信号消失，只剩下过程级信号。

**脆弱点**: $\alpha = 0.1$ 没有参数扫描论证。不同任务可能需要不同的 $\alpha$。

- [C11.3] **策略优化目标**:

$$\mathcal{J}(\theta) = \mathbb{E}\left[\frac{1}{Z}\sum_{i,t,u} \min\left(r_{i,t,u}(\theta)\hat A_{i,t}, \bar r_{i,t,u}(\theta)\hat A_{i,t}\right)\right]$$

标准 PPO clip 目标，作用在管理器发出的所有 token 上。$Z$ 是管理器 token 总数，用于归一化。

---

## 12. 理论-实践映射

### Anchored Points
- [C12.1] **理论 vs 实践**: 本文没有新的理论贡献。GRPO 和 PPO-clip 都是现有方法。创新在**问题设定**（冻结 Agent + 外部管理器）和**实验发现**（保真度-可靠性权衡）
- [C12.2] **经验性发现**: 保真度-可靠性权衡不是定理，而是实验观察到的经验模式。它可能随着模型规模、任务类型、管理器能力变化

---

## 13. 算法/模块走查

### Anchored Points
- [C13.1] **AdaCoM 工作流**:

```
输入: 任务 q → 初始上下文 c_0 = (q)

  第 t 步循环:
    1. Agent 在管理后上下文上行动: a_t ~ A(č_{t-1})
    2. 环境返回观察 o_t
    3. 构建管理前上下文: c_t = Append(č_{t-1}, a_t, o_t)
    4. 管理器采样动作: m_t ~ π_θ(·|P(c_t))
    5. 应用动作: č_t = Apply(m_t, c_t)
    6. 回到第 1 步

  终止: Agent 调用 finish 工具或达到迭代上限
```

- [C13.2] **具体例子（简化版）**:

```python
# 假设 Agent 刚执行了一次搜索，返回了 10 个文档结果
pre_context = [
    {"id": 0, "role": "user", "content": "任务: 找到人物 X"},
    {"id": 1, "role": "assistant", "content": "Thought: 我需要搜索..."},
    {"id": 2, "role": "tool_result", "content": "文档A: ...\n文档B: ...\n..."},  # ~5000 tokens
]

# 管理器的动作:
m_t = [
    {
        "ids": [2],                    # 只修改工具结果消息
        "role": "user",                # 改为 user 角色
        "justification": "工具结果包含大量不相关内容，压缩为关键线索摘要",
        "new_content": "搜索结果摘要: 文档A(关键线索: X 出生于1953年), 文档B(不相关)"
    }
]

# 管理后上下文 (约 500 tokens, vs 原始 5000+)
```

---

## 14. 方法深度解读

### Anchored Points
- [C14.1] **模块分解**:

| 模块 | 修复的失败 | 理想的但不可用的解法 | 可用的代理信号 | 隐藏假设 | 破坏后的风险 | 未来方向 |
|------|-----------|-------------------|--------------|---------|-------------|---------|
| **外部管理器 (4B)** | Agent 不可训练 | 内建上下文管理 | 外挂 LLM 拦截上下文 | 4B 容量足够 | 强 Agent 被容量限制 | 分层管理（小+大） |
| **JSON 动作空间** | 固定策略不兼容 | 最优策略已知 | RL 探索发现 | 操作都是局部的、单步的 | 需要跨步规划时失效 | 带规划的管理器 |
| **GRPO + 双层优势** | 稀疏结果奖励 | 密集人工标注 | 规则过程奖励 | 过程奖励是好代理 | 管理器学会投机取巧 | 学得的过程奖励模型 |
| **保真度-可靠性权衡** | 一个策略走天下 | 每类 Agent 的最优策略 | 按 Agent 能力自动匹配 | 能力=ReAct 分数 | 风格不同而能力相同 | 风格自适应管理器 |

---

## 15. 图表解释

### Anchored Points
- [C15.1] **Figure 1 (AdaCoM Overview)**: 每个 Agent 步骤前，外部管理器修改上下文。任务反馈只更新管理器，不更新 Agent。架构清晰，但缺少细节（管理器是生成式还是选择式？）
- [C15.2] **Figure 2 (Failure Mode Shifts)**: AdaCoM 减少了"错误答案"和"过早放弃"。Kimi 最显著的改进是减少了"达到迭代上限"（因为减少了冗余搜索）。但对于不同 Agent，改进来源不同——这是重要的发现
- [C15.3] **Figure 3 (Context Length):** 关键发现！DS 1.9K → Kimi 3.4K → Qwen 5.2K → GLM 7.0K 与 ReAct 表现完全正相关。两种策略：GLM/Qwen 使用"分层管理"（偶尔批量压缩），DS/Kimi 使用"急于蒸馏"（几乎每步都压缩）
- [C15.4] **Figure 4 (Cross-Agent Transfer)**: 32 对组合（4 源 × 8 目标），23 对交叉正收益。能力强弱匹配是主导因素，但风格匹配也会影响

**缺失**: 没有热力图显示哪些转移特别成功/失败。图 4 的可读性一般——条形图叠加太多信息。

---

## 16. 实验设计

### Anchored Points
- [C16.1] **Benchmarks**:
  - **BrowseComp-Plus**: 680 训练 + 150 测试，多约束 Web 搜索，35 步迭代上限
  - **MCP-Wiki**: 自建深度研究基准（9 个 Wikipedia MCP 工具），1000 RL 训练 + 150 测试
- [C16.2] **Agent 选择**: Qwen3-Max (强), GLM-4.5-Air (强), Kimi-K2-Instruct (中), DeepSeek-V3 (弱) — 覆盖了广泛的能力范围
- [C16.3] **Baselines**: ReAct, SumAgent (MEM1/IterResearch), MemAct, SumCoM (固定 summarization), AdaCoM w/o training
- [C16.4] **实现细节**: 管理器=Qwen3-4B-Instruct, 32K 上下文窗口, 4K 输出上限。SFT 暖身（GPT-5/Claude Opus 生成轨迹）→ GRPO (G=8)

**缺失的控制**:
- 没有报告每次实验的 GPU 小时数或成本
- 没有对 $\alpha$（过程奖励权重）做参数扫描
- MCP-Wiki 只测试了 2 个 Agent
- 没有测试代码类 Agent

---

## 17. 实验作为故事证据

### Anchored Points
- [C17.1] **主结果映射**:

| 实验 | 支持的 Claim | 排除的反事实 | 评估指标 | 压力条件 | 证据强度 |
|------|-------------|-------------|---------|---------|---------|
| Table 1 (BCP 主结果) | AdaCoM 一致提升多样 Agent (+39% avg) | 未训练管理器失败；固定 summarization 伤害部分 Agent | Mean@3 | 4 个 Agent, 6 个设置 | 强 |
| Figure 2 (失败模式) | 减少约束遗忘/过早放弃/冗余搜索 | 提升不仅是"更多正确答案" | 结果分布变化 | 4 个 Agent | 强 |
| Figure 3 (上下文分析) | 策略因 Agent 能力系统地不同 | 策略是 RL 涌现的，非手工设计 | 上下文长度分布 | 4 个自训练管理器 | 强 |
| Figure 4 (跨 Agent 迁移) | 管理器广泛可迁移；能力相近预测最好 | 管理器不绑定源 Agent | Mean@3 × 32 pairs | 4 源 × 8 目标 | 强 |
| Table 2 (MCP-Wiki) | AdaCoM 扩展到深度研究 | 效果不是 benchmark 特定 | Mean@3 | 2 个 Agent, 深度研究 | 中 |
| 附表 5 (过程奖励消融) | 过程奖励提供有用中间监督 | 仅结果奖励的 RL 不足 | Mean@3 | 2 个 Agent | 中 |

- [C17.2] **未充分排除的反事实**:
  - 可能更简单的方法（如"每 K 步自动压缩最旧消息"）效果如何？
  - 如果管理器使用更大的模型（14B），GLM 的 8.5% 相对增益能否更高？
  - 固定 summarization 在 MCP-Wiki 上表现如何？没有在 Table 2 中报告

---

## 18. Reviewer 视角审查

### Anchored Points
- [C18.1] **新颖性**: 中高。第一个系统地探索"训练外部管理器来为冻结 Agent 管理上下文"的工作，操作级灵活性的定义和保真度-可靠性权衡是新的
- [C18.2] **重要性**: 高。直接对接实际部署需求（OpenClaw, Hermes, Claude Code）
- [C18.3] **技术稳健性**: 好。多基线、多次运行、消融实验。但统计显著性检验缺失
- [C18.4] **方法学严谨性**: 好。3 次运行 Mean@3, 32 对迁移分析, 异常案例分析
- [C18.5] **可复现性**: 良好。代码开源（匿名仓库），详细超参数，数据集构建文档化
- [C18.6] **最可能的 Reviewer 反对意见**:
  1. 只测试了一种管理器规模 (4B) — 规模缩放行为未知
  2. 只测试了搜索类任务 — 代码/具身 Agent 未评估
  3. 推理开销没有被量化测量
  4. 过程奖励消融仅对比 $\alpha=0$ 和 $\alpha=0.1$，没有系统扫描

---

## 19. 创新点与逐 Claim 支持审计

### Anchored Points
- [C19.1] **贡献 1: AdaCoM 框架** — 理论支持（框架设计合理）+ 实验支持（主结果一致提升）✅
- [C19.2] **贡献 2: 性能提升** — 实验支持（Table 1 + Table 2 + 失败模式分析）✅
- [C19.3] **贡献 3: 保真度-可靠性权衡 + 迁移** — 实验支持（Figure 3 + Figure 4 + 异常案例）✅ 用"权衡"这个词可能过强——更像是一个观察到的经验模式，而非经过严格因果验证的权衡

---

## 20. 可复用的写作模式

### Anchored Points
- [C20.1] **模式: 隐藏假设突破 + 替代机制替换**
  - **公式**: "已有的 X 方法有效，但需要不可用的条件 Y → 用外部替代物 Z 来近似，并通过 RL 发现最优行为"
  - **教训**: 系统设计的常见困境是"需要访问不可访问的组件"。这是如何通过"从外到内"思路找到替代方案的典范

---

## 21. 弱点与限制

### Anchored Points
- [C21.1] **工程限制（可修复）**:
  - 仅一种管理器规模 (4B)
  - 推理开销和 KV 缓存效率问题未被测量和优化
  - 代码/具身 Agent 未测试
  - 过程奖励权重 $\alpha$ 未做参数扫描
- [C21.2] **结构限制（更根本）**:
  - 保真度-可靠性权衡是否需要正式建模？目前只是一个观察
  - 管理器的动作空间是否遗漏了重要的跨步骤操作？
  - 4B 管理器能否真的"无损保存"任何有价值的信息？

---

## 22. 创新类型与科学边界判断

### Anchored Points
- [C22.1] **类型**: **交叉授粉式创新**（把一个领域的方法应用到另一个设置）+ **实证发现**（保真度-可靠性权衡）
- [C22.2] **边界判断**: 不推动 LLM 本身的能力边界，但推动**Agent 系统设计的实用边界**。对实际部署有直接指导意义

---

## 23. 未来方向

### Anchored Points
- [C23.1] **方向种子总览**（详见 `direction_board.json`）:

| ID | 标题 | 类型 | 评估分 | 风险 |
|----|------|------|--------|------|
| D1 | 学习式过程奖励模型 | 证据缺口 | 8 | 中 |
| D2 | 推理时自适应管理器选择 | 后继论文缺口 | 7 | 中 |
| D3 | 管理器规模缩放 | 假设违背 | 8 | 低 |
| D4 | 前瞻规划管理器 | 假设违背 | 7 | 中 |
| D5 | 风格自适应管理器（提示词条件化） | Reviewer 反对 | 6 | 中 |
| D6 | AdaCoM 用于代码 Agent | 证据缺口 | 7 | 中高 |

- [C23.2] **最有价值的三个方向**:

**D1 — 学习式过程奖励模型**: 当前规则过程奖励（token 惩罚、冗余检测）是启发式的。一个在人类上下文质量评估上训练的学习奖励模型可能会显著改善训练效果。

**D3 — 管理器规模缩放**: 论文明确暗示 4B 管理器可能是 GLM 仅提升 8.5% 的瓶颈。直接测试 4B vs 14B vs 72B 管理器就填补了最明显的空白。

**D6 — 代码 Agent**: 将 AdaCoM 应用到 SWE-bench 可以大幅扩展范围，并测试保真度-可靠性权衡在代码任务中是否显现不同的模式。

---

## 24. 生动摘要

想象你有一个超级聪明的实习生（Agent）。通常情况下，你给他一个任务，他做得很好。但如果任务太长（复杂的 Web 搜索需要 35+ 步），他的办公桌上会堆满越来越多的文件（上下文），直到他在混乱中迷路（上下文退化）。

现有解决方案可以帮他整理文件，但有个问题：你必须**教会他自己整理**——这就像要求一个很忙的外包员工重新接受培训。更糟的是，整理策略只有一种（"把所有东西都总结成三句话"），但不同的人需要不同的整理方式——有人需要保留原始数据，有人只需要关键结论。

AdaCoM（我们的方法）的策略是：**你不需要培训实习生。我们在他的办公桌边放一个专门的档案管理员**。档案管理员看着实习生工作，观察他什么时候被文件淹没了，然后自动决定保留哪些、删掉哪些、改写成什么格式。档案管理员不替实习生思考——只负责保持办公桌整洁。

关键发现：档案管理员会自动学会对不同能力的人使用不同策略。对于能力强的人（GLM, Qwen），他尽量保留原始文件，偶尔批量整理。对于能力弱的人（DeepSeek, Kimi），他几乎每步都在压缩，只留下最精炼的关键信息。这叫**保真度-可靠性权衡**——强人能处理更多原始细节，弱者需要更精炼的输入来保持可靠。

而且，给一个 Agent 训练好的档案管理员，可以给另一个能力相近的 Agent 用——节省了大量训练成本。

---

## 25. 使用的源文件

- `/tmp/2605.30785/main.tex` — 主文章（60KB）
- `/tmp/2605.30785/appendix.tex` — 附录（56KB，含详细实验设置、数据集构造、额外结果、案例分析、提示词）
- `/tmp/2605.30785/symbol.tex` — 符号定义
- `/tmp/2605.30785/custom.bib` — 参考文献
- `/tmp/2605.30785/plots/` — 图表（未直接查看，通过 LaTeX 描述理解）

**缺失**: 无 PDF 图片（已通过 LaTeX 理解内容）；无 OpenReview 讨论（论文尚未进入审稿流程？）

---

# Appendix: Claim → Evidence Index

## C1.1 — 长上下文退化是长期 Agent 任务的核心瓶颈
- **类型**: evidence-backed interpretation
- **来源文件**: main.tex
- **路径**: Introduction, paragraph 4
- **引文**: "A central bottleneck for LLMs in such long-horizon tasks is long-context degradation."

## C1.3 — 固定策略对多种 Agent 不兼容
- **类型**: evidence-backed interpretation
- **来源文件**: main.tex
- **路径**: Introduction, paragraph 5
- **引文**: "predefined operations such as summarization impose a one-size-fits-all strategy despite substantial variation in agents' architectures, training data, and reasoning styles."

## C2.1 — 架构解耦
- **类型**: evidence-backed interpretation
- **来源文件**: main.tex
- **路径**: Introduction, paragraph 6
- **引文**: "architectural decoupling: context management is handled by an external manager, typically a smaller LLM, while the agent itself remains unchanged."

## C2.2 — 操作级灵活性
- **类型**: evidence-backed interpretation
- **来源文件**: main.tex, Method section
- **引文**: "the manager can freely modify any part of the context" + JSON action space definition

## C2.3 — 保真度-可靠性权衡
- **类型**: evidence-backed interpretation
- **来源文件**: main.tex, Introduction paragraph 7
- **引文**: "managers for stronger agents preserve more raw trajectory context to maintain fidelity, whereas managers for weaker agents compress more aggressively to keep reasoning reliable."

## C3.1 — 平均 +39% 增益
- **类型**: evidence-backed interpretation
- **来源文件**: main.tex, Table 1
- **值**: ReAct 24.17 → AdaCoM 33.60 (+39.0%)

## C3.3 — Summarization 伤害 GLM
- **类型**: evidence-backed interpretation
- **来源文件**: main.tex, Table 1
- **值**: GLM ReAct 32.56 → SumCoM 26.44 (-18.8%)

## C3.4 — 减少约束遗忘/过早放弃/冗余搜索
- **类型**: evidence-backed interpretation
- **来源文件**: main.tex, Section 4.2
- **引文**: "AdaCoM increases the proportion of correct answers across all backbones"

## C3.5 — Kimi 42.6% 冗余调用
- **类型**: evidence-backed interpretation
- **来源文件**: main.tex, Section 4.2
- **引文**: "an average of 42.6% of Kimi's tool-use steps per task are repetitive"

## C4.1 — 分层管理 vs 急于蒸馏
- **类型**: evidence-backed interpretation
- **来源文件**: main.tex, Section 4.3
- **引文**: "For GLM and Qwen, AdaCoM follows a tiered management strategy... For DeepSeek and Kimi, AdaCoM follows an eager distillation strategy"

## C4.2 — 上下文长度: DS 1.9K → GLM 7.0K
- **类型**: evidence-backed interpretation
- **来源文件**: main.tex, Section 4.3 (Figure 3)

## C5.1 — 23/28 交叉对正收益
- **类型**: evidence-backed interpretation
- **来源文件**: main.tex, Section 5 (Figure 4)

## C5.2 — 能力相近预测迁移效果
- **类型**: evidence-backed interpretation
- **来源文件**: main.tex, Section 5

## C5.3 — 风格兼容性影响迁移
- **类型**: evidence-backed interpretation
- **来源文件**: appendix.tex, Section app:transfer_exception
- **引文**: "DS prefers concise working memories... whereas AdaCoM(Kimi) tends to record detailed search histories"

## C7.1 — 过程奖励有用
- **类型**: evidence-backed interpretation
- **来源文件**: appendix.tex, Table 5
- **值**: DS 26.19→24.38 (-6.9%), Qwen 36.67→33.33 (-9.1%) 当移除过程奖励

## C8.1 — 推理开销 + KV 缓存问题
- **类型**: evidence-backed interpretation
- **来源文件**: main.tex, Limitations section

## C8.2 — 4B 管理器容量限制
- **类型**: evidence-backed interpretation
- **来源文件**: main.tex, Limitations section
