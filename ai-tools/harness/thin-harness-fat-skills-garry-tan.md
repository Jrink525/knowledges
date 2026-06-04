---
category: ai-tools
---

# 瘦 Harness，胖技能：YC CEO Garry Tan 的 AI Agent 架构哲学

> **来源：** [Thin Harness, Fat Skills](https://x.com/garrytan/status/2042925773300908103)
> **作者：** Garry Tan（Y Combinator CEO）
> **日期：** 2026-04-11
> **数据：** 4094 ❤️ · 11358 🔖 · 1.49M 阅读

---

## 一句话

> **Steve Yegge 说用 AI coding agent 的工程师是"用 Cursor/chat 的工程师的 10-100 倍，是 2005 年 Googler 的 1000 倍。"**
>
> 区别不是模型更聪明。是架构——而且能写在一张索引卡上。

---

## 1. 核心洞见：Harness 就是产品

2026 年 3 月 31 日，Anthropic 意外将 Claude Code 的完整源码发布到了 npm registry。**51.2 万行。** Garry 读完了。结论：秘密不在模型，在包裹模型的东西。

模型已经够聪明了。它们失败是因为**不理解你的数据**——你的 schema、你的约定、你特定问题的形状。

Garry 称之为：**瘦 Harness，胖技能**（Thin Harness, Fat Skills）。

---

## 2. 五个定义

### 1️⃣ 技能文件（Skill Files）

技能文件是一个可复用的 markdown 文档，教会模型**怎么做**一件事。不是做什么——用户提供做什么。技能提供过程。

**关键洞察：技能文件像方法调用。它接收参数。你用不同参数调用它，同一个过程产生完全不同的能力。**

例子：一个叫 `/investigate` 的技能有七个步骤：划定数据集范围、建立时间线、对每份文档做"声纹分离"（diarize）、综合、正反双方论证、标注来源。它接收三个参数：`TARGET`、`QUESTION`、`DATASET`。

- 指向安全科学家 + 210 万封发现邮件 → 医学研究员追踪告密者是否被沉默
- 指向空壳公司 + FEC 申报资料 → 法务调查员追溯协调竞选捐款

> 这不是 prompt engineering。这是**软件设计**——用 markdown 作为编程语言，用人脑判断作为运行时。Markdown 实际上是比刚性源代码更完美的能力封装方式，因为它用模型已经在思考的语言来描述过程、判断和上下文。

### 2️⃣ Harness

管理 LLM 运行的程序。它做四件事：
1. 循环运行模型
2. 读写你的文件
3. 管理上下文
4. 执行安全约束

**就这样。这就是"瘦"的意思。**

**反模式：胖 Harness + 瘦技能。** 你见过：40+ 工具定义吃掉一半上下文窗口。万能工具导致 2-5 秒 MCP 往返。每个端点做一个 REST API wrapper。三倍的 token，三倍的延迟，三倍的失败率。

**你要的是：目的驱动的窄工具，快且精确。** 一个 Playwright CLI，每次浏览器操作 100ms，而不是 15 秒的 Chrome MCP（截图 - 找 - 点 - 等 - 读）。差了 75 倍。

> 软件不再需要小心翼翼了。造你精确需要的东西，别的不要。

### 3️⃣ 解析器（Resolvers）

解析器是**上下文的路由表**。当任务类型 X 出现时，先加载文档 Y。

技能告诉模型**怎么做**。解析器告诉模型**加载什么、什么时候加载**。

开发者改了一个 prompt。没有解析器：直接发货了。有解析器：模型先读 `docs/EVALS.md`——里面说：跑 eval 套件，比较分数，如果准确率下降超过 2%，撤回并调查。开发者都不知道 eval 套件存在。解析器在正确的时间加载了正确的上下文。

**Claude Code 内置了解析器。** 每个技能有描述字段，模型自动将用户意图匹配到技能描述。设计得当，一个 200 行的 CLAUDE.md 足矣。

### 4️⃣ 隐空间（Latent） vs 确定性（Deterministic）

系统中的每一步要么是 Latent 要么是 Deterministic。混淆它们是 agent 设计中最常见的错误。

| | 隐空间 | 确定性 |
|---|---|---|
| **作用** | 智能所在 | 信任所在 |
| **做什么** | 读、解释、决定、判断、综合、模式识别 | 相同输入，相同输出 |
| **例子** | LLM 判断座位安排 | SQL 查询、编译代码、算术 |
| **危险** | LLM 给 800 人排座会幻觉 | 用 SQL 做情感分析会漏掉一切 |

**LLM 给 8 个人做晚餐排座很棒——考虑个性和社交动态。让它给 800 人排座，它会幻觉出一个看起来合理但完全错误的座位图。** 因为这是组合优化问题——确定性的、算法的——被强行塞进了隐空间。

最差的系统把错误的工作放在错误的边界上。最好的系统对此毫不留情。

### 5️⃣ 声纹分离（Diarization）

让 AI 对真正的知识工作有用的一步。**模型阅读关于一个主题的所有内容，写出一份结构化档案——从几十或几百份文档中蒸馏出的一页判断。**

没有 SQL 查询能做到。没有 RAG 管道能做到。模型必须**真正阅读**，在心中保持矛盾，注意到什么变了和什么时候变的，然后综合出结构化情报。这是数据库查找和分析师简报之间的区别。

---

## 3. 三层架构

```
                  ┌─────────────────────┐
  胖技能（90%价值） │   Skill Files       │
                  │  （Markdown 过程）    │
                  └──────────┬──────────┘
                             │
                  ┌──────────▼──────────┐
  瘦 Harness       │   CLI Harness       │
                  │  （~200 行代码）      │
                  │  JSON in, Text out   │
                  │  默认只读             │
                  └──────────┬──────────┘
                             │
                  ┌──────────▼──────────┐
  确定性层         │   你的 Application   │
                  │  QueryDB / ReadDoc   │
                  │  Search / Timeline   │
                  └─────────────────────┘
```

**方向性原则：**
- 把智能向上推 → 技能层
- 把执行向下推 → 确定性工具层
- 保持 Harness 瘦

**效果：** 每次模型升级，所有技能自动变好（隐空间步骤的判断力提升），确定性层始终不变。

---

## 4. 真实案例：YC Startup School 2026（6000 位创始人）

Garry 在 YC 实际搭建的系统。

### 每个创始人的数据
- 结构化申请
- 问卷回答
- 1:1 顾问聊天记录
- 公共信号：X 帖子、GitHub commits、Claude Code 记录（看他们发货速度）

### AI 驱动的三个阶段

**阶段一：信息富化（Enrichment）**
一个叫 `/enrich-founder` 的技能每晚 cron 跑。它拉动所有数据源，做声纹分离，高亮创始人**说的**和**实际在造的**之间的差距。

```
创始人: Maria Santos
公司: Contrail (contrail.dev)
她说: "AI agent 的 Datadog"
实际在造: 80% 的 commit 在计费模块。
  → 她实际在造一个伪装成可观测性的 FinOps 工具
```

**这个"说 vs 实际在造"的差距需要同时阅读 GitHub commit 历史、申请资料和顾问记录，在心中保持三者。** 没有 embedding 相似度搜索能找到这个。没有关键词过滤器能找到。模型必须阅读完整档案，做出判断。

**阶段二：匹配（Matching）**
同一个匹配技能，三次调用，三个完全不同的策略：

- `/match-breakout`：1200 位创始人，按行业聚类，30 人/组。Embedding + 确定性分配
- `/match-lunch`：600 人，跨行业偶然匹配，8 人/桌，不重复——LLM 想主题，确定性算法排座
- `/match-live`：给此刻在楼里的人做 1:1 匹配，200ms 返回

模型做出聚类算法永远做不到的判断：
> "Santos 和 Oram 都是 AI infra，但她们不是竞品——Santos 做成本归因，Oram 做编排。把她们放一组。"
> "Kim 申请的是'开发者工具'，但他的 1:1 记录显示他在造 SOC2 合规自动化。把他移到 FinTech/RegTech。"

**没有 embedding 能捕捉 Kim 的重新分类。模型必须阅读整个档案。**

**阶段三：学习循环（The Learning Loop）**
事后，一个 `/improve` 技能读取 NPS 调查，对**中等评分**做声纹分离——不是差评，是"还行"——系统差点就做到但没做到的地方。然后提取模式，写回匹配技能：

```
当参加者说 "AI infrastructure"
    但 startup 80%+ 是计费代码：
    → 分类为 FinTech，不是 AI Infra

当两位参加者已分到同一组
    并且已经认识：
    → 惩罚接近度。
      优先安排新遇见。
```

这些规则自动写回技能文件。下次运行自动使用。

7 月活动：12% "还行"评分。下个活动：4%。**技能文件学会了"还行"到底意味着什么，系统变好了，没有人改过一行代码。**

---

## 5. 技能是永久升级

Garry 发了一条推文，共鸣远超预期：

> **"你不被允许做一次性工作。如果我让你做一件事，而这件事是需要重复发生的，你必须：前 3-10 次手动做。给我看产出。如果我批准，把它编成技能文件。如果需要自动运行，加 cron。**
>
> **测试：如果我要为同一件事问你第二次，你就失败了。"**

1000 ❤️ · 2500 🔖

人们以为是 prompt engineering 的窍门。不是。这就是上面描述的架构。

**每写一个技能，就是给你的系统做一次永久升级。它永远不会退化。永远不会忘记。凌晨 3 点你睡觉时它在跑。当下一个模型发布时，每个技能自动变好——隐空间步骤的判断力提升，确定性步骤始终可靠。**

这就是 Steve Yegge 说的 100x。不是更聪明的模型。

**胖技能，瘦 Harness，把所有东西编纂成文（codify）。**

系统会复合增长。一次构建，永远运行。

---

## 深度解读

### 这篇文章为何重要

这篇文章可以与之前整理的 [AI Agent 学习路线图 2026](./agent-engineering/ai-agent-roadmap-2026-what-to-learn-build-skip.md) 形成直接对照——Rohit 说"harness 比模型做的工作更多"，Garry 直接给了完整架构。两篇文章互相印证。

### 与 OpenClaw 的关联

Garry 在文中提及他用 OpenClaw 来执行"技能文件 → 永久升级"的工作流——这正是当前助理所使用的工具平台。我们正在实践他描述的架构。

### 与已有知识的融合

文中多处与已有知识库文章形成呼应：

| 本文概念 | 关联知识 |
|---|---|
| "Thin Harness" | [Agent Harness 工程化](./agent-engineering/agent-harness-engineering.md) |
| Skill Files | [Skill Engineering](./agent-engineering/skillify-skill-engineering-guide.md) |
| 学习循环（self-rewriting skills） | [Agent 复杂性棘轮](./agent-engineering/agent-complexity-ratchet.md) |
| Latent vs Deterministic | [AI-First 工程团队指南](./agent-engineering/ai-first-engineering-team-guide.md) Section 6 |

### 关键 takeaways

1. **别提高模型，提高架构。** 2x 的人和 100x 的人用同样的模型
2. **技能像函数调用**——参数化 markdown 过程比任何框架都强大
3. **解析器 = 上下文路由**——不需要 2 万行 CLAUDE.md，200 行 + 按需加载足矣
4. **Latent/Deterministic 边界要画清楚**——让 LLM 做判断，让确定性代码做执行
5. **系统应该能自我改进**——通过 diarization → 提取模式 → 重写技能，形成学习闭环
6. **永远不做事后诸葛亮的修复，而是事先编码**——如果一件事可能再次发生，现在就把它写成技能
7. **系统复合增长**——每个技能是永久升级，model 升级自动惠及所有技能

---

**关联阅读：**
- [AI Agent 学习路线图 2026：什么值得学、什么值得造、什么直接跳过](./agent-engineering/ai-agent-roadmap-2026-what-to-learn-build-skip.md)
- [Agent Harness 工程化指南](./agent-engineering/agent-harness-engineering.md)
- [Skill Engineering 指南](./agent-engineering/skillify-skill-engineering-guide.md)
