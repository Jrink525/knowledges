---
title: "6 Workflows, 6 Lessons, 60 Days with Hermes Analyst"
tags:
  - hermes-agent
  - ai-agent
  - agent-architecture
  - skills-system
  - feedback-loop
date: 2026-06-01
source: "https://x.com/0xjeff/status/2061361760968560887"
authors: "0xJeff"
---

# Hermes Agent 60 天实战：6 个工作流、6 条教训

> **来源：** [@0xJeff on X/Twitter](https://x.com/0xjeff/status/2061361760968560887)
>
> **摘要：** 作者使用 Hermes Agent（类似 OpenClaw 的 AI Agent）进行投资/数据分析工作 60 天后的深度复盘。核心结论：Agent 失败在架构不在智商，工具和技能设计才是关键。

---

## 核心结论（一句话）

> **Agent 90% 是架构，10% 是 AI。** 人人都有同样的模型，区分有用 Agent 和无用 Agent 的是工具/技能设计、记忆持久性、反馈/学习循环，以及让运行可持续的单位经济模型。

---

## 一、Lesson 1：模型选择——换来换去不如 One Provider 到底

### 实践过程

60 天内经历了 5-6 套 Provider 切换：

| Provider | 使用的模型 |
|----------|-----------|
| OpenRouter | Kimi-k2.6, Qwen 3.6 27B, DeepSeek v4 Flash & Pro, Gemma |
| Opencode Go Subscription | Mini Max 2.5-2.7, GLM5.1, Kimi-k2.6 |
| DeepSeek 直连 API | DeepSeek v4 |
| Venice AI (DIEM credits) | 私有推理栈 |
| Grok Subscription | x_search |

### 每次切换的代价

每次切换消耗 **2-3 个 Session** 用于调试：
- API 兼容性问题
- Auth 认证流程
- Timeout 设置

### 核心教训

1. **模型之间的智力差距在缩小** — 开源权重模型正在逼近前沿实验室水平，同时保持低成本
2. **选一个 Provider 然后坚持用** — 换来换去的时间成本远高于模型差异本身
3. **直连 API 拿到的折扣和连接质量更好**
   - 例：DeepSeek 给直连 API 75% 折扣，之后才在 OpenRouter 上永久生效
4. **中转路由性能衰减明显**
   - Opencode Go $5/月套餐体验不如直连 DeepSeek API
   - Multi-hop 推理导致每次多 5-10 秒等待时间

### 实践建议

```
你的项目选 Provider 的 checklist：
□ 找一个主力 Provider（DeepSeek/OpenAI/Anthropic）
□ 直连 API 优先于中转服务
□ 选好后至少用 1 个月再评估是否切换
□ 保留一个备选 Provider（只切换关键模型，不切换全部）
```

---

## 二、Lesson 2：工具和技能比模型智商重要得多

### 核心矛盾

> "Many say having too many skills bloat up the context. I say having too many skills = a lot better than not having enough skills."

### Hermes 的 Skill 自动创建机制

Hermes 会在检测到你重复执行同一个工作流时，**自动创建一个 Skill**。效果：
- 第一次手动执行：3 分钟
- 第二次自动执行：10 秒
- 节省时间和推理成本

### 工具选择的最佳实践

| 场景 | 推荐工具 | 为什么 |
|------|---------|--------|
| 结构化 Web 搜索 | Exa | 比手动搜索效果好得多 |
| JS 重站抓取 | Firecrawl | 也能处理 JS 渲染 |
| 浏览器自动化 | CDP | Playwright 等被 Cloudflare 频繁拦截 |
| 工具调用 | 直连 API / MCP / Markdown Skill 文件 | 远优于手动搜索或 Browser CDP |
| 定时任务 | 专用工具 | 用对的工具比通用的好 |
| 一次性抓取 | Browser CDP + Agentic 搜索 | 灵活轻量 |

### 你的项目能做什么

1. **为每个重复工作流创建 Skill** — 如果同一个操作出现 3 次以上，就写成 Skill
2. **Skill 自动创建机制** — 可以实现一个"重复工作流检测"的自动 Skill 创建器
3. **优先用直连工具** — API/MCP/Markdown Skill 文件比 Browser 操作可靠得多

---

## 三、Lesson 3：记忆系统是关键差异化

### 三层记忆架构

| 层 | 机制 | 作用 |
|----|------|------|
| 原生记忆 | User.md, Memory.md, Soul.md | 理解用户偏好、世界观 |
| 外部记忆 Provider | Hindsight（高精度外部记忆） | 跨会话回忆 + 事实/事件关系推演 |
| Cron 记忆 | Recall（快速） vs Reflect（深度） | 按场景选择的两种记忆模式 |

### 踩坑记录

**坑：Reflect 太贵 + 太慢**
- 把 Hindsight 通过 OpenRouter 连到 Kimi-k2.6
- 把 "Hindsight reflect" 插到多个 cron 任务
- 结果：**连续几天烧掉 $20-30/天**
- 原因：Reflect 经常跑 240 秒然后超时

**解决：区分场景用不同的记忆模式**

| 场景 | 用哪种 | 原因 |
|------|--------|------|
| 定时报告、早晨简报 | **Recall** | 快，适合时间敏感的任务 |
| 深度分析、跨事件关系推演 | **Reflect** | 慢但深度好，适合非实时场景 |

### 实践建议

```
记忆系统的配置原则：
1. 原生记忆（User.md/Memory.md/Soul.md）— 基础配置，必须维护
2. 外部记忆 Provider — 选一个靠谱的，别换
3. 区分 Recall 和 Reflect 的使用场景
4. 不要把所有 cron job 都挂上 Reflect
```

---

## 四、Lesson 4：反馈循环 = 训练个人 Agent 的最佳方式

### 每天最期待的工作流：Morning Briefs

每天早上 10 点的固定流程：

```
□ 抓取所有关注的 X 账号和新闻源的更新
□ 检查投资组合公司当天的动态
□ 合成 Top 10 核心洞察
□ 作者亲自阅读、反馈、修正
```

### 6 步反馈循环

```
Step 1: Hermes 产出内容
Step 2: 作者即时阅读，标记错误/不相关的内容
Step 3: 给出具体的纠正指令/下一步
Step 4: Hermes 把纠正编码为永久规则
Step 5: 下次产出更精准
Step 6: 重复
```

### 效果

作者持续迭代后，输出格式越来越贴合自己的阅读习惯，不相关的内容越来越少。

### 最大痛点：回声室效应

> "The biggest problem right now is echo chamber + self-reinforcing loop."

问题表现：
- "Why it matters" 分析倾向于推荐现有的持仓
- 来源和分析师总是提那些大盘股（NVIDIA, TSMC, MU, VRT, SIVE）
- Agent 会自我强化，导致视野变窄

**尚未解决**，作者在公开寻求解法。

### 实践建议

```
反馈循环在你的 Agent 中的应用：
1. 给自己设一个固定的"反馈时间"（比如每天 10AM）
2. 每次反馈要具体 —— 不要说"不好"，要说"把 X 部分改为 Y"
3. 让 Agent 把每次纠正编码为持久规则
4. 注意回声室 —— 定期检查 Agent 的分析来源是否过于集中
```

---

## 五、Lesson 5：x402 解决了大问题

### 背景

> "The last 2 weeks was an eye opener for me — x402-integrated tools + x402 tools aggregator is one of the biggest innovations of crypto."

### x402 之前的痛点

```
找到一个好工具
→ 查有没有 MCP
→ 没有？去注册免费 API
→ 不免费？纠结值不值得花钱
→ 循环...
```

### x402 之后的体验

```
1 条命令设置 Agentic Wallet
存入 $5-10 USDC
开始探索上百个付费工具
每个工具只要几美分
```

具体用到的工具：Nansen（链上数据）、Exa/Firecrawl（Web 搜索）、Surf、BlockRun 等

### 对你自建 Agent 的启示

虽然不一定要用加密货币方案，但原则是一样的：**让你的 Agent 能方便地访问付费工具**。可以：
- 预充值一个 API 聚合平台账户
- 在 Skill 中预配置好 API key
- 让 Agent 能自动选择最佳工具，而不是每次都从零开始找

---

## 六、Lesson 6：Skill 打包——从 Prompt 到目录

### 原始错误做法

最初每个工作流是一个巨大的单体 Prompt：

```
onchain-dump-investigation → 一份 2000+ 单词的 Prompt
├── Dexscreener 的用法
├── Nansen 的用法
├── RPC 端点的配置
├── Cookie MCP 的查询模板
├── 输出合成格式
├── ... 还不断增长
```

问题：
- 每次出 bug → Prompt 更长
- 每 Session 从头开始 → AI 要从"巨型 Spaghetti 墙"中重推导
- 新增内容越多，质量越差

### 正确做法：Skill 是目录，不是 Prompt

```markdown
onchain-dump-investigation/
├── SKILL.md                 # 管道逻辑（保持 ~100 行）
├── references/
│   ├── nansen-agentcash.md  # API 端点形状 + 字段注意事项
│   ├── base-rpc-endpoints.md # 可用的 RPC 列表 + 频率限制模式
│   └── cookie-mcp-queries.md # 查询模板 + 交叉引用矩阵
└── scripts/
    └── check_wallets.sh     # 可执行的检查脚本
```

### 效果对比

| 维度 | 单体 Prompt | 目录 Skill |
|------|-----------|-----------|
| 加载成本 | 2000+ tokens 每次 | ~500 tokens（SKILL.md + 2-3 参考文件） |
| 维护性 | 改一条影响所有 | 分层修改，接口稳定 |
| 新 Session 效率 | 从零重推导 | 完整上下文直接加载 |
| 噪音 | 大量端点 URL、字段名、错误码混在一起 | 在 reference 文件中按需加载 |

**600 tokens → 2-3 reference files + 1 SKILL.md** 是推荐的配置。

> "A well-bundled skill costs ~500 tokens to load but saves 5000+ tokens of re-explaining context in every session."

---

## 总结：Agent 架构的核心要素

### 90% 架构 vs 10% AI

| 维度 | 权重 | 核心问题 |
|------|------|----------|
| **工具/技能设计** | 最高 | Agent 用哪些工具？技能怎么组织？ |
| **记忆持久性** | 高 | 跨 Session 怎么记住用户偏好和历史？ |
| **反馈/学习循环** | 高 | Agent 如何从用户的纠正中持续改进？ |
| **单位经济模型** | 中 | 跑一次任务要多少钱？可持续吗？ |
| **模型选择** | 低 | 开源模型已逼近前沿水平，差异不大 |

### 作者的状态

- 运行 Hermes Agent 超过 60 天
- 已有 **10+ 工具** 集成（大部分免费或低成本）
- 正在进行的新实验：给 Hermes 一小笔资金，让其**自主进行预测市场交易**
- 当前遇到大量 bug —— 借此表达对构建可靠 Agent 的开发者的敬意

### 入手指南（给想尝试的人）

```
hermes install
→ 配置模型 Provider
→ 开始输入你的偏好和需求
→ 每天早上看输出 → 反馈 → 迭代
```

---

*原帖作者 0xJeff，整理于 2026-06-01。初学 Agent 架构搭建的必读经验帖，所有教训都可绕过。*
