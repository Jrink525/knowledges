---
title: "A Harness for Every Task: Dynamic Workflows in Claude Code"
authors: ["Thariq Shihipar (@trq212)", "Sid Bidasaria (@sidbid)"]
tags: ["claude-code", "dynamic-workflows", "agent-harness", "anthropic", "agent-orchestration", "subagents", "harness-design", "agent-patterns", "multi-agent"]
source: "https://x.com/trq212/status/2061907337154367865"
date: 2026-06-02
views: 414278
bookmarks: 5702
likes: 2458
---

# A Harness for Every Task: Dynamic Workflows in Claude Code

> Claude Code 现在可以在运行时**自己写自己的 harness**，为手头任务量身定制。
>
> 默认的 Claude Code harness 是为编程设计的——但"许多任务都像编程任务"。对于研究、安全分析、agent 团队、代码审查等任务，需要构建自定义 harness 以达到最佳性能。

---

## 动态 Workflows 解决的问题

### 默认单上下文窗口的失败模式

当默认的 Claude Code harness 处理复杂长任务时，单个上下文窗口会暴露三种特定故障：

| 故障模式 | 表现 | 根因 |
|---------|------|------|
| **Agentic Laziness**（Agent 懒惰） | 处理 20/50 项安全审查后就宣布完成 | 复杂多部分任务缺少结构化终止条件 |
| **Self-preferential Bias**（自我偏好偏差） | 验证自身结果时倾向于说好—而非客观 | 缺乏独立验证者隔离 |
| **Goal Drift**（目标漂移） | 原始目标逐渐丢失：边缘用例要求、"不要做 X" 约束在压缩中丢失 | 多次压缩是信息有损的 |

**Workflow 的解法**：编排多个独立的 Claude，每个有自己的上下文窗口和聚焦的隔离目标。

### 静态 vs 动态 Workflows

| 类型 | 特点 | 问题 |
|------|------|------|
| **静态 Workflow**（Claude Agent SDK / `claude -p`） | 需要预写，应对所有边缘场景 | 过于通用，无法针对特定任务优化 |
| **动态 Workflow** | Claude Opus 4.8 在运行时自己写 JavaScript harness | **定制化**：tailor-made for your use case |

> 触发词：**"ultracode"** 确保 Claude Code 生成 workflow。

---

## 技术机制

动态 Workflows 是**在运行时生成的 JavaScript 文件**，包含用于 spawn 和协调子 agent 的特殊函数。

**关键特性**：
- 包含标准 JS 能力（JSON、Math、Array 等数据处理）
- 子 agent 可以**选择不同的模型**（Intelligence routing）
- 子 agent 可以**在自己的 worktree 中运行**（隔离）
- **会话中断后恢复时 workflow 可以从中断点继续**

---

## 核心模式（Composable Patterns）

### 1. Classify-and-Act（分类后路由）
一个分类 agent 决定任务类型，然后路由到不同的 agent 或行为。
也可以在结尾使用分类器决定输出格式。

### 2. Fan-out-and-Synthesize（扇出并合成）⭐
将任务拆分为多个小步骤，每个步骤运行一个 agent，然后合成结果。
- 适合：大量小步骤，或每个步骤需要干净上下文无交叉污染
- 合成步骤是**屏障（barrier）**——等待所有扇出 agent 完成，然后合并结构化输出为一个结果

### 3. Adversarial Verification（对抗验证）
每个被 spawn 的 agent 之外，再 spawn 一个独立的**对抗验证 agent**，根据 rubric 检查输出。

### 4. Generate-and-Filter（生成后过滤）
先生成一批想法/方案，然后按 rubric 或验证过滤、去重，只返回最高质量的。

### 5. Tournament（锦标赛）
- 不是分工，而是**让 agent 竞争**
- Spawn N 个 agent，都用不同方法尝试同一任务
- 用评判 agent 做两两比较，直到选出胜者
- **对比评判（pairwise comparison）比绝对评分（absolute scoring）更可靠**

### 6. Loop Until Done（迭代直到完成）
对于工作量未知的任务：循环 spawn agent，直到满足停止条件（没有再发现、没有更多错误），而不是固定轮次。

---

## 11 个典型用例

### 1. 迁移和重构
*Bun 使用 workflows 从 Zig 重写到 Rust*（Jarred 的 X thread）。

**模式**：将任务分解为一系列步骤 → 每个修复在独立的 worktree 中用子 agent 执行 → 对抗验证 agent 审查 → 合并。注意告诉 agent 不要用资源密集型命令以便最大化并行。

### 2. 深度研究
Anthropic 发布的 `/deep-research` skill 使用动态 workflows：
**扇出** web 搜索 → **抽取**来源 → **对抗验证**声明 → **合成**带引用的报告

### 3. 深度验证
对于报告/文档：一个 agent 识别所有事实声明 → 分别 spawn 子 agent 检查每个声明 → 验证 agent 检查来源质量。

### 4. 定性排序
1000+ 行的支持工单按严重性排序——一次放入上下文质量下降。
**解法**：用锦标赛（两两比较更可靠）或并行分桶后合并。每个比较是独立 agent，确定性循环只保留比赛进程。

### 5. Memory & 规则遵守
当某些规则即使写入 CLAUDE.md 模型仍然忽略时：
- 创建 workflow：每条规则一个验证 agent（独立验证者）
- 一个"怀疑论者"子 agent 审查规则本身，避免过多误报
- **反向**：挖掘最近的会话和代码审查意见 → 并行聚类 → 对抗验证每个候选规则（这个规则能否阻止真实错误？）→ 蒸馏回 CLAUDE.md

### 6. 根因调查
调试时独立假设的生成：
- 分离 agent：日志分析 / 文件分析与 / 数据分析
- 每个假设面对验证者和反驳者面板
- 不限于代码——可以用于销售分析（为什么三月销售下降？）、数据管道等

### 7. 大规模 Triage
支持队列、bug 报告分类：
- Classify → 去重 → 执行（尝试修复或升级到人类）
- **Quarantine 模式**：读取不可信公共内容的 agent 被禁止执行高权限操作，实际行动由另一个 agent 完成
- 配合 `/loop` 实现持续工作

### 8. 探索与品味
设计、命名等品味驱动的任务：生成多种方案 → 评委 agent 按 rubric 评判 → 锦标赛选出最佳。

### 9. Evals（轻量评估）
为特定任务运行轻量 eval：在 worktree 中 spawn agent → 比较 agent 按 rubric 评分输出 → 迭代改进 skill。

### 10. 模型与智能路由
分类 agent 研究任务复杂度后选择 model（Sonnet vs Opus）：
> "解释 auth 模块工作原理"需要的模型取决于 auth 模块实际有多少文件与调用的复杂度

### 11. 即时代码审查
*"quick workflow"* 概念——不限于大任务。可以对一个假设做快速对抗审查。

---

## 使用建议

### 何时使用
- 需要并行执行（大量小步骤）
- 需要隔离避免交叉污染
- 需要对抗验证/结构化评判
- 需要超过单上下文窗口范围的推理

### 何时不用
- 常规编码任务（不需要 5 个 reviewer）
- 简单单步任务
- 问自己：**"真的需要更多算力吗？"**

### 技巧
- **Prompting 是关键**：详细描述模式比简单指令效果好
- **配合 `/loop` 和 `/goal`**：可重复任务配合 loop 定时运行，/goal 设置硬性完成要求
- **Token budget**：可设置显式 token 预算（`"use 10k tokens"`）

### 保存与分享
- Workflows 按 `s` 键保存到 `~/.claude/workflows/`
- 通过 skill 分发：将 JS workflow 文件放入 skill 文件夹，在 SKILL.md 中引用
- 建议将 workflow 视为**模板**而非需要逐字执行的脚本—这样更灵活

---

## 与已读内容的连接

### 1. Rohit "The Harness Is Everything" — 理论到工程实践的闭环
Rohit 提出 Harness 是 Agent 的产品边界（BREADS 原则）。**Dynamic Workflows 是这个理论的工程实现**——Harness 不再是固定的运行时，而是由 Agent 本身在运行时动态生成和编排的。这是从"Harness 作为基础设施"到"Harness 作为生成过程"的跃迁。

### 2. Garry Tan "Stop Building Foxconn Factories" — 灵活 vs 僵化
Garry Tan 批评将 agent 环境建成"富士康工厂"——僵化、流水线化。动态 Workflows 是**反向**：每个 task 生成自己的 harness，按需定制、灵活组合。Foxconn 的反面是 IKEA。

### 3. SkillOpt — Shared Skills 与自进化
SkillOpt 来自微软，目标是让 agent skill 自我进化。Dynamic Workflows 提供了**保存和分享 workflows 作为 skill** 的路径——这是 SkillOpt 理念在 Anthropic 生态中的实践：workflows 作为 skill 存储在 `~/.claude/workflows/`，通过 skill 分发，可以作为模板被复用和迭代。

### 4. 论文 2605.30621 "Harness Evolution" — 三阶段模型的终点
该论文描述了三阶段（固定→灵活→自适应）。**Dynamic Workflows 就是第三阶段**：Harness 在运行时根据任务自适应生成。论文说"最终目标"，Thariq 这里说"我们已经发货了"。

### 5. Perplexity "Rethinking Search as Code Generation" — Fan-out 模式的共鸣
Perplexity 的 SaC 架构本质上是一个 **fan-out-and-synthesize**：搜索请求扇出到多个 source，结果合成后返回。Anthropic 的 `/deep-research` skill 用的完全相同模式。**Fan-out 正在成为 agent 系统的通用原语**。

### 6. Mem0 "State of Memory in Agent Harness" — 记忆与 orchestration 的分离
Mem0 文章揭示了每个 harness 的记忆实现各不相同。Dynamic Workflows 提出了新的挑战：**动态生成的 harness 如何继承记忆？** 如果每个 workflow 是新的独立 harness，跨 workflow 的记忆连续性需要更高级的模式——这强化了 Mem0 的论点：记忆必须是 harness 无关的基础设施。

### 7. Businessbarista "What the hell is a Software Factory?"
软件工厂追求可复用的模板化和标准化流程。Dynamic Workflows 提供的是"按需定制的软件工厂"——每个 task 动态生成自己的标准化流程，而不是用一套模具应付所有任务。

---

## 关键洞察

### "Composable Patterns" 取代 Monolithic Agent
这 6 种模式（Classify-and-Act, Fan-out-and-Synthesize, Adversarial Verification, Generate-and-Filter, Tournament, Loop Until Done）构成了 agent 编排的**原语语言**。这些模式可以嵌套组合，形成任意复杂的 agent 拓扑。

### 从 "Agent" 到 "Agent Topology"
之前讨论 agent 时，单位是一个 agent。Dynamic Workflows 引入了一个更高的抽象单位：**agent 拓扑**（agent topology）——多个 agent 之间的连接方式、通信模式、验证链。设计 agent 系统不再是选模型，而是设计拓扑。

### Quick Workflow 概念 —— 低摩擦的动态 harness
大任务用 workflow 好理解，但 Thariq 也提到 **"quick workflow"**——对单个假设做快速对抗验证。这意味着动态 harness 生成的摩擦已经低到可以一次性地用于小任务，用完即弃。

### 对 Agent 平台的设计启示
Dynamic Workflows 揭示了一个平台设计原则：**灵活性来自于让 agent 自身具备元编程能力**。与其预置所有可能的 harness，不如让 agent 自己写 harness。这需要模型足够强（Opus 4.8）——但随着模型能力增长，这个模式必然普及。
