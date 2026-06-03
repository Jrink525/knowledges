---
title: "How To Be A World-Class Agentic Engineer — 世界级 Agentic 工程师修炼指南"
tags:
  - agentic-engineering
  - best-practices
  - claude-code
  - codex
  - ai-agents
date: 2026-05-30
source: "https://www.systematiclongshort.com/p/how-to-be-a-world-class-agentic-engineer"
authors: "SystematicLS"
---

# How To Be A World-Class Agentic Engineer

> **来源：** [SystematicLS Substack](https://www.systematiclongshort.com/p/how-to-be-a-world-class-agentic-engineer)
> **作者：** SystematicLS（X: @systematicls）
> **日期：** 2026-05

---

这篇文章的核心理念可以用一句话概括：

**Less is more. 保持极简，不要被工具和插件绑架。**

作者有丰富的实战经验（从 agent 几乎不会写代码的时代就开始用，在 production 中跑过信号系统、基础设施和数据管道），最终回归到几乎 barebones 的 CLI 环境（Claude Code + Codex），靠理解几条基本原则就能做出最 groundbreaking 的工作。

---

## 一、核心哲学：世界在狂奔，别追

> "Every new generation of agents will force you to rethink what is optimal, which is why less is more."

**要点：**
- Frontier 公司（Anthropic、OpenAI）的创新速度极快，每一代 agent 都会让你重新思考什么是最优方案
- 当你使用了大量第三方库和 harness，你其实是在"锁定"自己对某个问题的解决方案——而这个方案可能在下一代 agent 中就不需要了
- **🤯 关键洞察**：frontier 公司的员工自己就是最狂热的 agent 用户（无限 token 预算 + 最新模型）。如果某个问题真的有好的第三方解决方案，他们会是最大的用户——然后他们就会把它吸收进产品里
- 看历史：skills、memory、subagents、planning... 全都是先从社区发明的解决方案，最终被官方吸收
- 所以结论很简单：**如果它真的重要，Claude 和 Codex 会自己实现它。** 你不需要疯狂追逐新工具。

**实操建议：** 定期更新 CLI 工具，看看 release notes 里新增了什么功能，这就够了。

---

## 二、Context Is Everything — 上下文是命脉

> "You want to give your agents only the exact amount of information they need to do their tasks and nothing more!"

### 上下文膨胀（Context Bloat）—— 最大的敌人

- 使用太多插件、memory 系统、技能文件会导致 agent 的 context 被不相关信息污染
- 你让 agent 写一个 hangman 游戏，但它却在读 26 个 session 前的"内存管理"笔记。这就是 context bloat

### 核心方法论：分离研究与实现

- **不精确的指令**："去建一个 auth 系统" → agent 需要用 context 做研究、比较方案 → 实现时 context 已经被污染
- **精确的指令**："实现 JWT 认证，bcrypt-12 密码哈希，7 天过期 refresh token rotation" → agent 的 context 全部用于实现细节

### 实用流程

1. 如果你不确定实现细节 → 创建一个**研究任务**，让 agent 调研各种方案
2. 自己或让 agent 决定选哪个方案
3. 让另一个 agent 用**全新的 context** 来实现

> 你有一个非常聪明、但容易跑偏的团队成员。如果你不告诉它聚焦在设计舞池，它会一直跟你讲球的物理特性。

---

## 三、Sycophancy（讨好倾向）的设计限制与利用

Agent 被设计成取悦用户、服从指令。这意味着：

- 你说"帮我找个 bug" → 它真的会"找"一个出来，哪怕需要编一个
- 大多数人不该抱怨 LLM 在瞎编，而是应该反思自己的 prompt

### 策略 1：用中性提示

- ❌ "Find me a bug in the database"
- ✅ "Search through the database, try to follow along with the logic of each component, and report back all findings"

### 策略 2：用 Multi-Agent 对抗来利用讨好性

作者提出的**三方 bug 发现框架**，非常精巧：

1. **Bug Finder**（找 Bug 的 agent） → 给予评分激励（低影响+1、中+5、严重+10）→ 它会极度亢奋地找出所有"可能"的 bug（包含假阳性）→ 这是 **superset**
2. **Adversarial Agent**（对抗 agent） → 每驳倒一个 bug 得该 bug 的分数，但错判就扣 2 倍分 → 它会激进地试图"证伪"所有 bug（甚至包括真的 bug）→ 这是 **subset**
3. **Referee Agent**（裁判 agent） → 告诉它"我有 ground truth"，判对+1、判错-1 → 它会审慎裁决

最终结果：**惊人的高准确率**。偶尔仍有错误，但接近无瑕。

---

## 四、Compaction 与假设问题

> "They are still atrocious at 'connecting the dots', 'filling in the gaps' or making assumptions."

- Agent 在不需要做假设时表现像最聪明的存在
- 一旦需要"连点成线"或"填补空白"，立刻智商掉线
- **必须教 agent 重新抓取上下文的规则**——这是 CLAUDE.md 里最重要的规则之一：

**Compaction 后**，agent 应该自动：
1. 重新读取任务计划
2. 重新读取相关文件

---

## 五、教会 Agent 如何结束任务

> "The biggest problem of current intelligence is that it knows how to start a task, but not how to end the task."

- Agent 天然不会"结束任务"——它经常做个 stub 就收工
- **最佳里程碑：测试（Tests）**——测试是有确定性的，你可以设置清晰的完成条件
  - 规则：除非 X 个测试全部通过，否则任务**没有完成**
  - 规则：不许修改测试本身
- **新的结束方式：截图 + 验证** —— agent 做完后截图，验证 UI 设计/行为是否符合预期

### Task Contract 模式

创建 `{TASK}_CONTRACT.md`，在其中指定：
- 需要通过的测试
- 需要验证的截图
- 其他验证条件

只有 contract 里的所有条件都满足，agent 才被允许结束 session。

---

## 六、长期运行的 Agent：不推荐单 session 跑 24 小时

> "I've not found long-running, 24 hour sessions to be optimal."

24 小时不间断 session 的问题：
- 强制引入 context bloat（不相关的 contract 上下文混在一起）

**推荐方案：每个 contract 一个 session**
1. 创建合约来描述"需要做的事情"
2. 用一个编排层来在需要时创建新 contract
3. 每个 contract 启动一个全新的 session
4. 各自独立，上下文纯净

---

## 七、迭代式构建：从最简开始

> "Start bare-bones. Give the basic CLI a chance."

就像你不会指望一个新行政助理第一天就知道你的全部偏好一样——你也应该让 agent 逐步学习。

### Rules（规则）

- 看到 agent 做你不喜欢的事 → 写成 rule
- 在 CLAUDE.md 中告诉 agent 何时读取哪些 rule 文件
- **CLAUDE.md = 路由目录**：包含的是"在什么情况下该去哪里找上下文"的 IF-ELSE 逻辑
  - 如果要写代码 → 读 coding-rules.md
  - 如果要写测试 → 读 coding-test-rules.md
  - 如果测试失败 → 读 coding-test-failing-rules.md
- 规则可以任意嵌套和条件化

### Skills（技能）

- 规则 = 偏好编码
- 技能 = 流程/配方编码
- 如果不知道 agent 会怎么解决某个问题 → 让 agent 自己研究并**把方案写成 skill**
- 这样你可以在它真正遇到那个问题之前就审查和修正它的做法

### 当性能开始下降时...

当你加了足够多的 rules 和 skills 后，一切感觉像魔法——然后性能又开始下降。

原因是：规则之间互相矛盾，或 context 又开始膨胀。**解决方案：定期清理。**

让 agent 去"度假"——合并规则、技能、消除矛盾，向你确认最新的偏好。然后魔法就又回来了。

---

## 八、Own The Outcome（对结果负责）

> "No agent today is perfect. You can relegate much of the design and implementation to the agents, but you will need to own the outcome."

最终信条：你可以把大量设计和实现委托给 agent，但**你需要为最终结果负责**。

---

## 总结

| 原则 | 核心要点 |
|------|---------|
| **Less is more** | 别装一堆插件，官方会吸收真正好用的功能 |
| **Context 是命脉** | 分离研究与实现，精确指定需求 |
| **利用讨好性** | 用 neutral prompt 或 multi-agent 对抗 |
| **任务要有终止条件** | 测试通过、截图验证、task contract |
| **一个 contract 一个 session** | 别跑 24 小时 session，context 会污染 |
| **CLAUDE.md 是路由目录** | 只放 IF-ELSE 逻辑，不要放具体内容 |
| **规则 + 技能 = 训练 agent** | 逐步积累，定期清理冗余 |
| **Own the outcome** | 你最终要对结果负责 |

---

*Processed on 2026-05-30 from [SystematicLS Substack](https://www.systematiclongshort.com/p/how-to-be-a-world-class-agentic-engineer)*
