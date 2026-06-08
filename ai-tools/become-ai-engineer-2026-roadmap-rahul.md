---
title: "How To Become an AI Engineer in 2026 (Without a CS Degree)"
tags:
  - ai-engineering
  - roadmap
  - harness
  - agent-building
  - langgraph
  - production
  - career
date: 2026-06-05
source: "https://x.com/sairahul1/status/2062809249064141017"
authors: "Rahul (@sairahul1)"
series: "ai-engineering-roadmap"
---

# 2026 年成为 AI 工程师的完整路线图

> **来源：** X.com 长文 by Rahul  
> **发布时间：** 2026-06-05  
> **数据：** 200 ❤️ · 41 🔁 · 14 💬

---

## 一、残酷真相

> "Most developers building AI right now are building toys."

2026 年市场充斥的是 LLM 之上的薄层包装，不是企业。它们只是 feature，等着被 Big Tech 吞噬。

**2026 年公司真正愿意付钱的：**
- 周五凌晨 2 点**不会挂**的 Agent
- 你能**测量和证明没有回归退化**的系统
- 让同一个模型表现**好 86%** 的 Harness

最后一个不是虚构。Anthropic 用同一个模型（Opus 4.5）在两个不同 harness 上跑：
- **Claude Code harness：78%** on CORE benchmark
- **Smolagents harness：42%** on CORE benchmark
- **差 36 个百分点。** 模型远不如 harne ss 重要。

---

## 二、AI 工程师 2026 年实际在做什么

> "The harness is the job."

不是写 prompt，不是选模型。AI 工程师**构建和运维模型周围的整个系统**：

| 职责 | 说明 |
|------|------|
| Agent 循环和工具分发 | 设计 loop + tool dispatch 机制 |
| 上下文工程 | 每一步什么 tokens 放在模型前 |
| 编写模型能正确选中的工具 | tool 设计和 schema |
| 存储/持久化/沙箱 | 应对生产流量 |
| Eval + CI 回归门 | 让"变好"变成可测量的 |
| 发布能生存的 Agent | 应对真实用户和真实成本 |

### 四个上下文原语

| 原语 | 含义 |
|------|------|
| **Write** | scratchpad、agent 读写更新的 memory 文件 |
| **Select** | 使用时刻检索，不是一次性全 dump |
| **Compress** | 在 context window 的 85-95% 处做摘要 |
| **Isolate** | sub-agent 各自独立的 context window |

> **Prompt engineering 作为独立技能已死。Context engineering 取代了它。**

---

## 三、6 阶段路线图

### Phase 0：建立正确的心理模型（第 1-2 周）

先不写一行 agent 代码。理解三件事：

**1. Workflow vs Agent**
- Workflow = 你写死了控制流
- Agent = 自己的控制流决策（在 loop 内）
- 需要 workflow 时建 agent：贵 10 倍、坏两倍

**2. Anthropic 的 5 种 Workflow 模式**
- **Prompt chaining** — 上一个调用的输出给下一个
- **Routing** — 不同任务用不同模型
- **Parallelization** — 同时跑多个任务
- **Orchestrator-worker** — 一个大脑多双手
- **Evaluator-optimizer** — 生成→评判→改进

**3. Harness（类比操作系统）**
- 模型 = CPU（原始算力）
- RAM = Context window
- OS = Harness
- 应用 = Agent 的 skills

> OS 决定 CPU 能做什么。Harness 决定模型能做什么。

**Phase 0 项目：** 用你自己的话写 2 页文档，定义 workflow vs agent、5 种 workflow 模式、4 种上下文原语、orchestrator-worker 模式。

---

### Phase 1：从零构建第一个 Agent（第 3-5 周）

写两次 agent。

**Build #1 — 原始 loop（~100 行 Python）**
```python
# 核心 loop 自己写
# 调模型 → 解析 tool_use → 执行 tool → 追加 tool_result → 循环
# 给 3 个工具: web_search, read_file, write_file
```

做过一次之后，所有框架都变得可读了。

**Build #2 — Claude Agent SDK**
增加：
- CLAUDE.md（项目约定）
- 一个 Skill（定义 research-summary 输出格式）
- 一个 PostToolUse hook（自动格式化每个 write）
- 一个 sub-agent（通过 Task tool 生成）

**Phase 1 项目：** 每日简报 agent。读 markdown 笔记 + RSS feeds → 写摘要到磁盘。跑一周，看它怎么挂，修它。

---

### Phase 2：构建有真实架构的 Agent（第 6-9 周）

用 **LangGraph + Deep Agents**，这是生产环境堆栈。

**LangGraph 提供：**
- 状态机（nodes + edges）
- PostgresSaver 检查点（进程杀死后恢复）
- Time-travel 调试（回退到任何步骤）
- 人机协同中断（Human-in-the-loop）
- 通过 LangSmith 的顶级可观测性

**Deep Agents（LangChain 的打包 harness）提供：**
- Planning middleware（规划中间件）
- 虚拟文件系统
- Sub-agent 生成
- 自动上下文压缩
- Skills

**关键概念：middleware**
```python
# 4 个关键 hook
before_agent  — loop 启动前
wrap_model_call — 每次 LLM 调用时
before_tools  — 任何工具执行前
after_tools   — 任何工具执行后
```

**Phase 2 项目：** Research Analyst Agent
- 主 agent 规划 → 写 TODO 到虚拟文件系统
- 生成 3 个搜索 sub-agent（并行、隔离上下文）
- Citation sub-agent 验证声明
- Writer agent 生成带内联引用的 markdown
- 状态通过 PostgresSaver 持久化
- 人机协同：超过 $1 token 前确认
- 附带 LangSmith trace URL

---

### Phase 3：自己构建 Harness 层（第 10-13 周）

> "You will never make the right harness trade-offs in production until you've built one once."

**现代 Harness 的 10 个组件：**

| 组件 | 说明 |
|------|------|
| **Loop control** | while 循环：模型→工具→模型 |
| **Tool dispatch** | 注册表、schema 校验、并行调用、重试 |
| **Context management** | system prompt 组装、85% window 时压缩 |
| **Persistence** | 每节点检查点，支持恢复/回退/fork |
| **Sub-agent orchestration** | 隔离上下文子 agent，压缩摘要返回 |
| **Skills & progressive disclosure** | 仅相关时才加载能力 |
| **Hooks** | PreToolUse/PostToolUse/PreCompact/Stop |
| **Observability** | 每个模型调用/工具调用/sub-agent 调用的 OTEL span |
| **Sandboxing** | 代码在容器中执行，模型永远没有 creds |
| **Auth brokering** | 凭据永远不进入模型上下文 |

**Phase 3 项目：** ~1500 行 Python 的 mini harness，包含：
- 带 `@tool` decorator + JSON schema 生成 + tool registry
- CLAUDE.md 风格 system prompt 加载器
- SKILL.md progressive-disclosure 加载器
- Sub-agent spawn 原语（隔离上下文）
- Filesystem offload：>20K token 的工具结果写磁盘，context 中只留路径+10 行预览
- 85% context window 自动压缩
- 可插拔 hook 系统（pre_tool/post_tool/stop）
- OpenTelemetry tracing
- 持久化：每步后写入 SQLite，按 run ID 恢复

**真正交付物：** 1000 字 post-mortem，对比你的 mini harness vs Claude Agent SDK vs Deep Agents。

---

### Phase 4：构建 Eval 和回归 Harness（第 14-17 周）

> "Without this, every 'improvement' is vibes."

**4 种 eval 类型：**

| 类型 | 含义 | 频率 |
|------|------|------|
| **Single-turn evals** | 给定输入，输出对不对？确定性 grader 最佳 | 持续运行 |
| **Trajectory evals** | agent 调用的工具序列和参数是否正确？ | 测试单步/全轮/多轮 |
| **LLM-as-judge** | 开放输出场景：研究报告、代码审查 | 每周校准人类标注 |
| **End-state evals** | 对于有状态的 agent：数据库是否正确写入？文件修改对不对？ | 针对最终状态 |

**尴尬事实：** 模型能检测到自己被 eval，表现会不同。设计 eval 要用**真实生产查询**而非合成数据。

**Phase 4 项目：** Phase 2 项目的回归 harness
- Golden dataset：30-50 个手工评分的研究问题（3 个难度级别）
- 事实查询用确定性 grader
- LLM-as-judge 用 5 标准 rubric
- Trajectory eval：是否规划、生成 2+ sub-agent、引用来源、预算内完成
- 接入 GitHub Actions：golden set 通过率下降 3+ 分时阻止 merge
- 生产采样：1% 的实时 trace 每晚自动评分

---

### Phase 5：生产硬化（永远）

5 件永远重要的事：

**1. 成本控制**
- 缓存 CLAUDE.md、system prompt、tool definitions（节省高达 90%）
- 按难度路由：Haiku（简单）/ Sonnet（大多数）/ Opus（困难推理）
- Batch API：非实时工作降 50%
- 多 agent 消耗~15x 单 agent token——只在价值明确超过这个成本时用

**2. 延迟**
- 始终并行工具调用（甚至 Anthropic 自己的 research agent 的 system prompt 里就写死了"you MUST use parallel tool calls"）
- 流式部分输出到 UI
- Sub-agent fan-out：60 步串行 agent → 10 步主 agent + 5 个并行的 10 步 sub-agent

**3. 安全与沙箱**
- 所有代码执行在沙箱里（Modal / E2B）：永远不在主进程中 exec() 模型输出
- 凭据在模型上下文之外代理：模型永远看不到它正在用的 API key
- 任何不可逆操作前要进行人机协同中断

**4. 监控与漂移**
- 警报：每次请求的 token 成本、tool call 失败率、LLM-as-judge 分数、p95 延迟
- 每次模型升级后重新 baseline eval——harness 编码了模型不能做什么的假设，这些假设会过时

**5. 韧性**
- 超过 60 秒的 agent → Inngest / Temporal / PostgresSaver 的持久化执行
- 每节点后检查点
- 始终可回退和 fork

---

## 四、5 个生产级项目（选一个这周末建）

| # | 项目 | 等级 | 说明 |
|---|------|------|------|
| 1 | **SLM 移动应用** | 初级 | 离线小模型，4/8-bit 量化，滑动上下文窗口，零 API 成本 |
| 2 | **自改进编码 Agent** | 中级 | Plan→Execute→Test→Reflect 循环，三级记忆（短期/长期/失败） |
| 3 | **视频编辑版 Cursor** | 高级 | Fork Shotcut，视觉模型分析帧+音频，意图转参数 |
| 4 | **个人生活 OS Agent** | 专家 | 日历/财务/健康管理，个人知识图谱，价值对齐，用户控制密钥 |
| 5 | **企业工作流 Agent** | 大师 | Slack/Jira 事件驱动，多 agent 委派，不可变审计日志，自愈 |

---

## 五、推荐技术栈

| 层 | 推荐 | 说明 |
|----|------|------|
| **Framework** | LangGraph 1.0 + Deep Agents | 状态机+PostgresSaver+time-travel+model-agnostic |
| **Harness 参考** | Claude Agent SDK | 和 Claude Code 同一个 harness |
| **可观测性** | LangSmith 或 Braintrust 或 Arize Phoenix | 一个就够了 |
| **2026 年跳过** | OpenAI Swarm（非生产）/Assistants API（年中 sunsetting）/自建 vector store（先测 recall 问题）/No-code 平台（除非一次性） |

**选 CrewAI / AutoGen / Swarm 不行：**
- **CrewAI**：demo 最快，生产脆弱。仅 hackathon。
- **AutoGen**：合并进 Microsoft Agent Framework，未来不明确。
- **OpenAI Swarm**：README 自己写着"not production-ready"。

---

## 六、关键基准数字（2026 年 5 月）

| 基准 | 领先者 | 得分 |
|------|--------|------|
| SWE-bench Verified（编程） | GPT-5.5 / Claude Opus 4.7 | ~88.7% / ~87.6% |
| GAIA（通用 agent 任务） | Claude Sonnet 4.5 | 74.6% |
| τ-bench（客服 agent） | Claude Mythos Preview | 89.2% |

**关键洞察：** 同一基准不同 harness = 10-36 分的差距。模型远不如 harness 重要。

---

## 七、时间线

| 时间 | 里程碑 |
|------|--------|
| 第 2 周 | Phase 0 完成——能用简单语言解释 harness |
| 第 5 周 | Phase 1 完成——用 Claude Agent SDK 发布含 1 Skill + 1 hook + 1 sub-agent 的 agent |
| 第 9 周 | Phase 2 完成——LangGraph deep-agent 运行中，带 PostgresSaver + LangSmith traces |
| 第 13 周 | Phase 3 完成——1500 行 mini harness 写好了并带文档 |
| 第 17 周 | Phase 4 完成——Golden dataset、CI gates、benchmark 运行 |
| 17 周+ | Phase 5 永远持续 |

**兼职（每周 10-15 小时）：** 所有时间 × 2.5

---

## 八、三个在生产的统计数据

- **57%** 的团队已有 agent 在生产中
- **89%** 的团队已接好可观测性
- **质量**是 #1 瓶颈（32% 的团队提到）

> 这意味着整个领域被能构建 **eval 和 harness** 的工程师瓶颈了。而不是能调 LLM API 的工程师。

**可替换的：** 建薄 GPT wrapper  
**不可替换的：** 交付带 eval 和持久化的自主系统  
**差距 = 5 个项目 + 17 周的专注工作**

---

## 九、与已有知识库的关联

- [Claude Agent SDK 构建指南](/ai-tools/agent-engineering/trading-agent-skills-claude-sdk-zostaff.md) — Tool/Skill/Hook/Subagent 四种机制的实践
- [Agent Memory System](/ai-tools/agent-memory-system-from-basics-to-production.md) — Context engineering 的支撑
- [CREAO Cloud Agent Infrastructure](/ai-tools/agent-engineering/cloud-agent-infrastructure-creao-peter-pang.md) — Harness 设计中的凭证代理和沙箱原理
- [Second Brain with gbrain](/ai-tools/agent-engineering/second-brain-gbrain-openclaw-hermes-vox.md) — 知识层与记忆的分离思路
- [10 Claude Code Plugins](/ai-tools/agent-engineering/claude-code-10-plugins-vince.md) — 开发提效工具补充

---

*整理于 2026-06-05，来自 Rahul (@sairahul1) X.com 长文*
