# LedgerAgent: Structured State for Policy-Adherent Tool-Calling Agents

## 1. 论文标识信息

| 字段 | 内容 |
|------|------|
| **标题** | LedgerAgent: Structured State for Policy-Adherent Tool-Calling Agents |
| **作者** | Md Nayem Uddin (ASU), Amir Saeidi (ASU), Eduardo Blanco (UArizona), Chitta Baral (ASU) |
| **发表** | arXiv:2606.20529 [cs.AI], 2026-06-18 (Work in Progress) |
| **链接** | https://arxiv.org/abs/2606.20529 |
| **代码** | 未公开 |
| **许可证** | CC BY 4.0 |

---

## 2. 摘要

Policy-adherent tool-calling agents in customer-service domains must maintain task states across turns while calling tools and obeying domain policies. In standard agents, task states are not represented separately — observations, tool returns, and policy instructions are placed in the prompt, leaving agents to reconstruct relevant states from the prompt each time. This creates two failure modes: (1) agents may retrieve the right facts but later ground decisions in stale/missing/incorrect information; (2) syntactically valid tool calls may still violate domain policies. LedgerAgent introduces an inference-time method that maintains observed task states in a separate ledger and renders the states into the prompt. The ledger is also used to check state-dependent policy constraints before environment-changing tool calls are executed, blocking violations. Across four customer-service domains and mixed open-/closed-weight models, LedgerAgent improves average pass^k, with largest gains under stricter multi-trial consistency metrics.

---

## 3. 问题陈述

**State grounding failure**: 在标准工具调用智能体中，任务状态没有独立表示。每次决策时，智能体必须从不断增长的对话历史中重新构建相关状态。这导致两个核心问题：

**C1.1 — 状态回溯失败**: 智能体可能通过工具调用获取了正确的记录，但在后续决策时却使用了过时、缺失或不正确的事实信息。由于状态隐式地散布在提示词中，模型难以在关键时刻准确定位到最相关、最新的状态。

**C1.2 — 策略违规**: 即使工具调用的语法完全正确，仍可能违反依赖于当前任务状态的领域策略。例如，退款必须退回到原始支付方式——如果智能体在提出退款调用时没有明确的状态引用，可能选择错误的支付方式。

这两个问题在客服领域尤为突出，因为智能体需要跨多轮交互维持状态（对话、信息检索、工具调用、策略约束），且环境变更操作（退款、改签、取消订单）不可逆。

---

## 4. 动机

现有方法（微调、强化学习、推理时增强框架如 ReAct/Reflexion/ToT）主要改进模型的推理能力或训练数据，但保留了相同的"纯提示词驱动"状态表示方式。获取的记录和策略规则仍然嵌入在不断增长的对话转写中，任务状态在行动时刻仍隐式存在。因此需要一种方法：

1. **不改变模型权重** — 推理时方法，无需额外训练
2. **显式表示状态** — 把观察到的环境状态从提示词中分离出来
3. **可验证的策略执行** — 在环境修改类调用执行前进行策略检查

---

## 5. 背景：工具调用智能体

工具调用智能体（tool-calling agents）的发展经历了从单次 API 调用到多轮交互的演进。早期工作如 API-Bank (Li et al., 2023) 和 ToolLLM (Qin et al., 2023) 关注模型是否能规划和产生有效的工具调用。近期客服基准如 τ-Bench (Yao et al., 2024) 和 τ²-Bench (Barres et al., 2025) 组合了对话、结构化记录、领域 API 和运营策略，揭示出智能体失败往往不是简单的工具选择错误——模型可能检索到正确的信息，但后来因相关记录深埋在交互历史中而做出错误决策。

---

## 6. 相关工作：推理时增强方法

推理时（inference-time）增强方法改变模型周围的程序而非模型本身：

| 方法类别 | 代表性工作 | 核心思想 | 局限 |
|---------|-----------|---------|------|
| 规划与推理 | ReAct, ToT | 分解任务后再行动 | 仍未改变状态表示方式 |
| 反思修正 | Reflexion, Self-Refine | 利用前次尝试反馈 | 依赖模型从转写恢复状态 |
| 输入重格式化 | IRMA (Mishra et al., 2025) | 添加领域规则和工具建议 | 仍有 >50% token 开销 |
| 多智能体 | FAMA (Saeidi et al., 2026) | 按失败模式动态选择助手 | 需多个额外 LLM 调用 |

这些方法仍主要依赖语言模型从对话记录中恢复当前任务状态，在后来的行动依赖精确记录、标识符、状态或有效工具参数时可能不可靠。

---

## 7. 相关工作：策略遵守

策略遵守（policy adherence）是一个独立的挑战。现有基准强调策略遵循的重要性（τ-Bench, τ²-Bench），但大多数智能体实现仍然将规则放在提示词中或依赖模型推理某个行动是否被允许。当规则适用性依赖于对话过程中获取的记录时，这种方法可能失败。LedgerAgent 在模型与环境的接口处解决这一差距——提供一个来自工具观测的结构化状态对象，并使用该状态在执行前检查建议的写操作。

---

## 8. 方法总览

LedgerAgent 是一个推理时方法，为标准策略遵守型工具调用智能体添加两个**确定性**组件：

1. **Ledger（账本）**: 存储成功工具调用的观测状态的类型化字典
2. **Policy Gate（策略门）**: 在环境变更调用执行前进行检查

核心循环：读取新工具返回 → 吸收到账本 → 渲染账本到提示词 → 模型生成回复或工具调用 → 策略门检查 → 执行或拦截。

### 关键设计原则

- **零额外 LLM 调用**: 账本更新（确定性解析）、账本渲染（确定性字符串格式化）、策略门（可执行谓词检查）都不引入额外模型调用
- **模型权重的零侵入**: 模型权重、工具 schema 和解码过程保持不变
- **Observe-not-assume**: 账本仅从成功的读取工具返回中更新，写操作后必须重新读取才能观测新状态

---

## 9. Ledger 状态与更新

**形式化定义**: Ledger 是一个类型化字典 L: 𝒫 → 𝒱，其中 𝒫 是规范 schema 路径的集合，𝒱 是工具返回值的集合。

**路径示例**: `user`, `orders.*`, `products.*`, `reservations.*`，带键的搜索结果等。

**更新规则**:
- 只从**成功的读取型工具返回**更新
- 失败的调用和写操作不更新状态
- 写操作成功后，代理必须发起新的读取调用才能观察到新状态
- 每个领域提供固定的工具路径映射（tool path map），将完整的成功返回路由到规范账本位置
- 路径映射遵循工具接口和策略相关实体，**不由 LLM 生成**

**确定性的渲染**: 每次模型调用前，完整的账本块被添加到提示词中，列出每个在规范路径下已观测的记录及其存储的返回值。对话历史、策略文本和工具 schema 仍然提供。

---

## 10. Ledger-Grounded Generation

在每次模型调用前，LedgerAgent 将完整账本块添加到提示词中。该块是从 L 确定性生成的，列出通过读工具实际观测到的每条记录。每条目在规范路径下显示（如 `orders.1234` 或 `products.5678`），附带存储的返回值。

**目的**: 使当前观测状态对模型**容易找到**。例如，在读取订单和产品后，账本块显示 `orders.1234` 已交付、属于当前用户且包含物品 `sku_a`；`products.5678` 列出观测到的替代方案。用户说"我要换那个"时，模型可直接使用这些稳定路径和标识符，而不是从早期 JSON 返回中搜索。

---

## 11. Policy Gate

策略门在任何环境变更调用执行前立即运行，评估建议调用相对于当前账本 L 的可执行谓词 Π。

### 三种返回结果

| 结果 | 含义 | 行为 |
|------|------|------|
| **allow** | 所有谓词通过 | 调用不变地执行 |
| **revise** | 可恢复的违规 | 移除违规调用，反馈给模型下次使用 |
| **block** | 不可恢复的违规 | 调用被拦截，拒绝请求的操作 |

### 谓词设计

- 每个领域指定一次，作为账本字段上的**代码谓词**
- 总共 28 个确定性门谓词：Airline 10 个、Retail 12 个、Telecom 6 个、Telehealth 0 个
- 检查类型：所有权、实体状态前置条件、参数接地、退款/支付一致性、循环预防

### 谓词示例

**Retail**:
- 订单属于已验证用户
- 退货目标是已交付的订单
- 退款使用已观测的支付方式
- 换货物品和替代方案出现在观测记录中

**Airline**:
- 所选航班来自先前的搜索结果，然后才能用于预订更新

**门不是规划器**: 它不选择工具、修复参数、获取缺失记录或规划新轨迹。模型仍负责任务进度。

---

## 12. 智能体循环

```
Algorithm 1 LedgerAgent Loop

输入: m=消息, H=历史, L=账本, T=工具, P=策略, Π=谓词

1: 将 m 追加到 H
2: if m 是工具返回消息 then
3:     L ← Absorb(L, m)          // 成功的已知读取更新类型化状态
4: end if
5: C ← Render(L)                 // 渲染账本块
6: a ← Generate(H, P, C, T)      // 模型生成
7: if a 提出环境变更调用 then
8:     (a', g) ← GateFilter(a, L, Π)
9:     if g = allow then
10:         return a'             // 调用不变保留
11:     else if g = revise then
12:         return a'             // 拒绝的调用移除；反馈添加
13:     else if g = block then
14:         return 拒绝
15:     end if
16: end if
17: return a
```

**成本不变性**: 默认配置下，Ledger 更新、渲染和策略检查包装基本模型调用，但**不引入额外 LLM 调用**。

---

## 13. 实验设置

### 基准域

| 域 | 基准 | 任务数 | 控制模式 |
|----|------|--------|---------|
| Airline | τ²-Bench | 50 | 单控制 |
| Retail | τ²-Bench | 114 | 单控制 |
| Telecom | τ²-Bench | 114 | 双控制 |
| Telehealth | τ-Trait | 20 | 单控制 |

**单控制**: 只有智能体修改数据库。
**双控制**: 用户模拟器也可以改变共享状态。

### 基线比较

Ledger 与标准函数调用（FC）对比。**使用相同**的策略、工具、对话历史、解码设置和模型调用次数。基线从转写中恢复任务状态，Ledger 额外渲染账本并在策略门前进行检查。

### 骨干模型

6 个模型：GPT-5.2, GPT-4.1, Kimi K2.5, GLM-5, MiniMax M2.5, Qwen3-30B。

所有智能体运行使用 temperature 0.0。用户模拟器固定为 GPT-5-mini。

### 评估指标

**pass^k**: 每个任务执行 k 次独立试验，所有 k 次都通过才算通过。

- **pass^1**: 单次成功的主要指标
- **pass^4**: 跨试验一致性的严格指标

---

## 14. 主要结果

### 非 GPT 骨干模型

| 模型 | 条件 | Airline Avg | Retail Avg | Telecom Avg | Telehealth Avg |
|------|------|-------------|------------|-------------|----------------|
| Kimi K2.5 | FC | 54.4% | 38.3% | 80.9% | 11.3% |
| Kimi K2.5 | Ledger | **62.3%** | **53.9%** | 69.9% | **18.8%** |
| GLM-5 | FC | 51.3% | 40.9% | 63.7% | 16.9% |
| GLM-5 | Ledger | **64.6%** | **48.5%** | 68.7% | **17.6%** |
| MiniMax M2.5 | FC | 46.2% | 16.7% | 66.1% | 10.7% |
| MiniMax M2.5 | Ledger | **49.9%** | **36.6%** | 66.3% | **20.7%** |

**关键发现**:
- Kimi K2.5: 平均 pass^1 提升 3.4 点，pass^4 提升 5.6 点
- GLM-5: 平均 pass^1 提升 4.7 点，pass^4 提升 7.6 点
- MiniMax M2.5: 平均 pass^1 提升 7.3 点，pass^4 提升 8.3 点
- 注意：Kimi 和 GLM 在 Telecom 的 pass^4 上略有下降

### GPT 骨干模型（仅 Airline + Retail）

- GPT-4.1: 平均 pass^1 提升 12.2 点
- GPT-5.2: 平均 pass^1 提升 15.5 点
- pass^4 也有类似幅度的提升

---

## 15. 与 IRMA 对比

| 方法 | Pass^1 | Pass^4 | Token 开销 |
|------|--------|--------|-----------|
| IRMA | 23.4% | 9.6% | +53.1% |
| **Ledger (ours)** | **27.2%** | **17.1%** | **0.0%** |

Ledger 在 pass^1 上比 IRMA 高 3.7 点，在 pass^4 上高 7.4 点，**且不引入额外 token 开销**（IRMA 因使用三个助手智能体而增加超过 50% token 开销）。

---

## 16. 环境变更任务性能

在需要至少一个环境变更工具调用的任务子集上（Airline 26/50, Retail 104/114, Telecom 94/114, Telehealth 19/20），Ledger 持续优于基线。

**Telecom 双控制环境**尤为敏感——智能体和用户模拟器都可能修改共享数据库——Ledger 在通过将写操作锚定在观测的账本状态上来提升动作级可靠性。

---

## 17. 消融分析

### 贡献分解

消融实验表明改进来自两个组件的组合：
1. **类型化账本**: 使当前观测状态在生成时可见
2. **策略门**: 在执行前拦截违规操作

两者在 Telehealth 上的分离尤为重要（Telehealth 没有策略门谓词），说明账本本身的贡献是可衡量的。

---

## 18. 错误分析

对 Kimi K2.5、MiniMax M2.5 和 GLM-5 在 Ledger 设置下的失败轨迹分析（跨 4 个域）：

### 失败分布

| 失败类别 | 占比 | 说明 |
|---------|------|------|
| 遗漏必要动作 | **70.3%** | 智能体完成初始查找但终止或转人工 |
| 错误参数 | **20.4%** | 调用了正确工具但参数错误 |
| 其他（违规/循环/通信/鉴权） | 9.3% | 策略违规、推理循环等 |

### 域级差异

| 域 | 主要失败模式 | 建议改进方向 |
|---|-------------|-------------|
| **Retail** | 69.9% 遗漏动作，20.0% 错误参数 | 多件修改时易转人工；支付限制后的有效替代路径 |
| **Telecom** | 98.7% 遗漏动作 | 未调用权限授权工具或转移步骤 |
| **Airline** | 47.7% 遗漏，33.9% 错误参数；最多的额外/未授权动作 | 用户施加压力后做出策略不允许的航班变更或降舱 |
| **Telehealth** | 25.9% 最高错误参数；唯一有鉴权失败 | 复杂 schemas（provider_id, appointment_type 等）；未尝试病历查询就转人工 |

---

## 19. 分析与讨论

### 为什么 Ledger 有效

1. **状态的显式表示降低了模型负担**: 模型不需要从提示词中查找和提取，可直接使用模板化的账本块
2. **策略门提供了安全边界**: 即使模型犯错，门会捕获违规操作
3. **Observe-not-assume 保持一致性**: 账本总是反映实际观测到的环境状态
4. **低开销**: 零额外 LLM 调用，仅增加提示词长度

### 关键结论

- 最大收益出现在 pass^4（**一致性**指标），表明 Ledger 减少随机性带来的失败
- 改进在 GPT 骨干模型上尤为显著，但跨所有模型都有收益
- 相比 IRMA 等同方法，Ledger 更简单、更便宜、更有效

---

## 20. 局限性

1. **结构化域依赖**: 假设工具返回暴露稳定的模式化字段，不适用于非结构化/视觉/潜在状态任务
2. **只观测状态**: 账本只包含已观测的信息，不能证明未检索的事实
3. **域级规范**: 开发者需定义读工具路径映射和谓词，不是自动策略归纳
4. **评估范围**: 4 个客服域、固定用户模拟器、每个任务 4 次试验，不覆盖全范围的真实用户、对抗行为或生产流量
5. **Token 成本**: 虽然零额外 LLM 调用，但账本渲染增加提示词内容，对简单任务可能不划算
6. **与多智能体/记忆系统的比较有限**: 仅与 IRMA 一种代表性方法对比

---

## 21. 未来方向

基于论文的局限和错误分析，有多个有前景的方向：

1. **自动策略归纳**: 从自然语言策略文档自动编译可执行谓词，消除手动编码
2. **长期对话支持**: 超越 4-8 轮交互，处理超长对话中的状态管理
3. **多层账本**: 支持不同类型的状态层（观测、推断、假设）
4. **混合记忆**: 结合账本与长期记忆（如 RAG）管理更复杂的状态
5. **自适应策略门**: 根据任务难度或不确定性动态调整门的严格程度
6. **开放域泛化**: 从结构化的客服 API 扩展到更开放的工具使用场景

---

## 22. 声明索引

| 编号 | 声明 | 章节 | 证据 |
|------|------|------|------|
| C1.1 | 状态接地是关键失败模式：代理可能检索正确记录但后来使用过时/缺失/错误重构的状态 | §1, §3.1 | Introduction, Ledger State and Updates |
| C1.2 | 语法正确的工具调用仍可能违反依赖于当前任务状态的策略 | §1 | Introduction |
| C3.1 | Ledger 是类型化字典 L: 𝒫 → 𝒱，更新仅来自成功读取工具返回 | §3.1 | Ledger State and Updates |
| C3.2 | 策略门在环境变更调用执行前检查，返回 allow/revise/block | §3.3 | Policy Gate |
| C3.3 | 默认配置不引入额外 LLM 调用 | §3.4 | Algorithm 1, Agent Loop |
| C3.4 | 28 个确定性门谓词：Airline 10, Retail 12, Telecom 6, Telehealth 0 | §3.3 | Policy Gate |
| C4.1 | 评估覆盖 4 个客服域和 298 个任务 | §4.1 | Benchmark Domains |
| C5.1 | Ledger 跨非 GPT 骨干改进平均 pass^1 和 pass^4 | §5, Table 2 | Cross-Model Generalization |
| C5.2 | Ledger 在 GPT 骨干上平均 pass^1 提升 12.2 (GPT-4.1) 和 15.5 (GPT-5.2) | §5 | Cross-Model Generalization |
| C5.3 | Ledger 比 IRMA 高 3.7 点 pass^1 和 7.4 点 pass^4，零 token 开销 | §5, Table 3 | Comparison with IRMA |
| C6.1 | 遗漏必要动作占失败 70.3%，错误参数占 20.4% | §6 | Error Analysis |
| C6.2 | Telecom 98.7% 失败是遗漏动作；Telehealth 25.9% 是错误参数 | §6 | Domain-level analysis |

---

## 23. 个人评价

**贡献**: LedgerAgent 提出了一个简洁而有效的设计思路——将隐式的任务状态管理显式化。其核心洞察是：状态不应该由模型从提示词中推断，而应以结构化形式独立维护并在行动时提供。

**优点**:
- 方法简单，易于复现和现有系统集成
- 零额外 LLM 调用的成本优势明显
- 策略门 allow/revise/block 的设计优雅且实用
- 错误分析透彻，不回避失败案例

**不足**:
- 需要手动编写的路径映射和谓词是应用瓶颈
- 评估局限于结构化 API 客服场景
- 没有分析账本对提示词长度的影响
- 与更复杂的记忆系统（如 MemGPT）的对比缺失
- Telehealth 没有策略门谓词，削弱了对 Telehealth 结果的整体论证

**影响预测**: 如果作者提供开源实现，该方法可能成为工具调用智能体的基础设施级贡献——就像 ReAct 或 Toolformer 一样，Ledger 式的显式状态管理可能成为标准做法。
