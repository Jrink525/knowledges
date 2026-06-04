---
category: ai-tools
---

# Claude Code Routines 完整教程：让 Agent 在云端帮你 7×24 小时干活

> **来源：** [How to Set Up Claude Code Routines to Automate Any Workflow (Full Course)](https://x.com/eng_khairallah1/status/2054494450009932110)
> **作者：** Khairallah AL-Awady (@eng_khairallah1)
> **日期：** 2026-05-13
> **数据：** 38 ❤️ · 45 🔖（刚发布 1 小时的抢先内容）

---

Anthropic 发布了一个功能，几乎没人讨论。

叫 **Claude Code Routines**。这可能是 Anthropic 今年最重要的功能。

**原因如下：**

在此之前，每次 Claude Code 自动化都需要你开着电脑。你可以用 `/loop` 轮询变更。可以用 `/schedule` 设置定时任务。但一旦你关掉终端或合上笔记本，一切就停了。

**Routines 彻底解决了这个问题。**

一个 Routine 是你配置一次的 Claude Code 自动化——一个 prompt、一个仓库、一组连接器——然后它在 **Anthropic 的云基础设施上运行**。按计划。从 API 调用。或由 GitHub 事件触发。

你的电脑可以关机。终端可以关闭。Routine 照跑不误。

> 这是从"你使用的 AI 工具"到"为你工作的 AI 系统"的转变。

---

## 一、Routines 和以前有什么不同？

Claude Code 之前就有调度功能。那有什么变化？

**区别是基础设施。**

旧的 `/schedule` 和 `/loop` 命令在你的本地 Claude Code 会话中运行。它们依赖你的机器开机、终端打开、网络稳定。任何一个出问题，自动化就死了。

**Routines 在 Anthropic 的云上运行。** 它们是持久化的自主 agent——能扛过重启、终端关闭、通宵运行。它们可以直接访问你的仓库和连接器——Slack、Linear、Google Drive、GitHub——你不需要管理任何基础设施。

> 把旧系统看作你手机上的提醒。它响了，你还是得做事。
> **Routines 是那个在你睡觉时干活的员工，等你醒来时给你一份总结。**

---

## 二、第一步：决定自动化什么

最好的 Routines 自动化的是那些：

- **重复性**——它们按可预测的时间表发生（每日、每周、或由事件触发）
- **明确定义的**——你能毫无歧义地说出"完成"长什么样
- **低判断需求的**——不需要你独特的创造性思维或决策，只需要执行

**早期用户正在运行的模式：**

| 场景 | 描述 |
|---|---|
| **代办事项管理** 🌙 | 每晚午夜拉取 Linear 新 issue，按类型和严重程度分类，打标签，发摘要到 Slack。负责人醒来看到一张干净的看板 |
| **文档漂移检测** 📝 | 每周五扫描合并的 PR，识别改了 API/接口的，交叉比对文档，为过时文档开更新 PR |
| **部署验证** 🚀 | 每次部署后通过 webhook 触发，跑冒烟测试、扫描错误日志、关联最近代码变更，发 go/no-go 结论到发布频道 |
| **每日代码审查** 🔍 | 每天早上 9 点拿起最旧的公开 PR，审查安全问题、逻辑错误和风格违规，发内联评论 |

> **设置 3-4 个 Routines 的人，和不把它们当一回事的人，已经不在同一个操作层面了。**

---

## 三、第二步：创建你的第一个 Routine

有两种创建方式：

### Web 界面
打开 `claude.ai/code/routines`，点击"New routine"。这里有完整的配置选项——计划触发、API 触发、GitHub 事件触发。

### CLI 方式
如果你已经在终端使用 Claude Code，输入：
```
/schedule 每天早上9点做 PR 审查
```
CLI 只创建基于计划的触发器。API 和 GitHub 触发器需要 Web 界面。

### 创建时配置四件事：

**1. Prompt（最关键）**
Routine 自动运行，你看着。prompt 必须是**完全自包含**的。agent 需要知道的一切都必须写在 prompt 里。没有"之前的对话上下文"。每次运行从零开始。

**2. 仓库**
Routine 操作哪个代码库。默认对 `claude/` 前缀的分支有读权限和推送权限。

**3. 连接器**
Routine 可访问的外部服务——Slack（发更新）、Linear（读写 issue）、Google Drive（读写文档）、GitHub（监控事件、开 PR）。

**4. 触发方式**
- **定期**：每小时、每晚、每周
- **API**：你以编程方式调用
- **GitHub 事件**：仓库中特定事件触发

---

## 四、第三步：写一个防弹 Prompt

大多数人在这一步失败。

Routine 运行的时候没人看着。如果 prompt 模糊，agent 每次会以不同方式解读，你会得到不一致的结果。

### 最佳 Routine Prompt 结构：

```
角色定义：你是一名高级代码审查者，专精安全和性能。
任务定义：审查此仓库中最旧的公开 PR。
分步流程：
  1. 读取 PR 描述
  2. 查看分支
  3. 读取变更的文件
  4. 分析安全漏洞、逻辑错误、性能问题
  5. 对每个发现的问题写内联评论
输出规范：
  在 PR 上发一条总结评论，包括：
  - 按严重程度的总问题数
  - 一段总体评估
  - 明确的 approve/request-changes 裁决
错误处理：
  - 如果没有公开 PR，在 Slack 的 #engineering 发"今天没有 PR 需要审查"
  - 如果 PR 改了超过 50 个文件，跳过并标记为需要人工审查
约束：
  - 绝不批准含 Critical 级别问题的 PR
  - 绝不直接修改代码——只评论
  - 每个文件最多 3 条内联评论以免噪声
```

> prompt 越精确，routine 越可靠。

---

## 五、第四步：了解限制

Routines 很强大，但也有约束：

| 限制 | 说明 |
|---|---|
| **每日运行上限** | 研究预览期间每个账号 15 次/天。如需更多在组织设置中启用额外使用（按量计费） |
| **Token 消耗** | 与交互式 Claude Code 会话共享同一订阅额度。复杂 routine（读多文件+多 API 调用）消耗显著更多 |
| **分支安全** | 默认只能推送到 `claude/` 前缀的分支。不要禁用此限制，除非下游有完善的审查流程 |
| **GitHub 事件限制** | 预览期间有每 routine 和每账号的小时级限制。如果仓库很活跃，过滤触发事件避免浪费 |
| **时间精度** | 定时 routine 在指定时间运行，但高峰期可能有偏差。不要构建依赖精确到秒的工作流 |

---

## 六、第五步：构建 Routine 栈

一个 routine 有用。一整套是系统。

一个小团队完成的 Routine 栈：

| 时间 | 任务 | 做什么 |
|---|---|---|
| 🕘 早上 9 点 | **每日 PR 审查** | 审查所有公开 PR，发内联评论，汇总优先级列表到 Slack |
| 🚀 部署后（webhook） | **部署验证** | 跑测试套件，扫描日志错误，数分钟内发 go/no-go |
| 🌙 凌晨 2 点 | **夜间代办分类** | 处理当天所有新 issue，打标签，排优，生成长早报 |
| 📅 周五下午 5 点 | **文档检查** | 扫描本周合并的 PR，识别需更新文档，开草稿 PR |
| 📅 周一早上 8 点 | **技术债报告** | 扫描 TODO 注释、过时依赖、测试覆盖缺口，生成排序后的技术债清单 |

每个 routine 配置 10-15 分钟。整套一个下午。时间节省**每周都在复利**。

---

## 七、第六步：监控和改进

每次 routine 运行都会生成日志。审查它们。

找这些模式：
- **输出质量稳定吗？** 如果不稳定，prompt 哪部分模糊？
- **某些运行太久了？** 可能需要缩小范围
- **遇到错误了？** 在 prompt 中添加显式错误处理
- **产生了太多噪音？** 收紧约束

### Dreaming 功能
5 月 6 日的 Code with Claude 上宣布的 **Dreaming** 功能将此推向上了一层。启用 Dreaming 后，Claude 在两次运行之间**审查自己过去的 routine 会话**，识别什么做得好什么不好，然后**自我改进**下次的方法。

> 你的 routines 运行得越多，它们就越聪明。

---

## 八、Routines vs GitHub Actions

很多人会问：为什么用 Claude routines 付费，不用免费的 GitHub Actions？

**答案是：GitHub Action 是一个脚本。你写每一步。你定义每个条件。你自己处理每个边缘情况。它精确执行你编写的代码，不多不少。**

**Claude Routine 是一个 agent。你给它一个目标。它自己决定如何达到。它适应意外情况。它推理问题。它验证自己的工作。**

| | GitHub Actions | Claude Routines |
|---|---|---|
| **本质** | 脚本 | Agent |
| **你给** | 每一步的指令 | 一个目标 |
| **它做** | 精确执行 | 推理、适应、验证 |
| **故障处理** | 你写 try/catch | 它理解失败原因并调整 |
| **输出** | 告诉你错了什么 | 理解为什么错，建议修复，开 PR |

> 脚本遵循规则。Agent 解决问题。

对于简单自动化（跑测试、检查格式、发通知）——GitHub Actions 够了。任何需要**判断、分析、适应**的事情——Routines 在另一个层级。

---

## 九、5 个可以直接抄的 Recipe

### Recipe 1：早报机器人
```
计划：每天 8:30
Prompt：
  检查 GitHub 仓库昨天提交的所有 commit。
  检查 Linear 新创建和更新的 issue。
  检查 Slack #engineering 中提及阻塞项的任意消息。
  编译一份站会简报：
    1. 昨天做了什么
    2. 正在进行什么
    3. 什么被阻塞了
  发简报到 #daily-standup
```

### Recipe 2：依赖审计员
```
计划：每周一 6:00
Prompt：
  扫描 package.json 和 requirements.txt 的全部依赖。
  对每个依赖检查已知漏洞。
  识别落后当前版本超过 2 个 major 版本的依赖。
  生成按严重程度排序的报告。
  如发现 Critical 漏洞，开 GitHub issue。
```

### Recipe 3：Changelog 生成器
```
触发：GitHub 事件——新 release tag 推送
Prompt：
  当新 release tag 推送时，读取上一 tag 以来的所有 commit。
  按 feature/fix/improvement/chore 分类。
  在 CHANGELOG.md 生成格式化的 changelog。
  开一个 PR。
```

### Recipe 4：测试覆盖率监控
```
计划：每晚 1:00
Prompt：
  跑测试套件。按模块计算覆盖率百分比。
  对比 coverage-config.json 中的基线。
  如果任何模块下降超过 2%：
  开 GitHub issue——含模块名、旧覆盖率、新覆盖率、导致下降的 commit。
```

### Recipe 5：PR 描述执行器
```
触发：GitHub 事件——新 PR 打开
Prompt：
  当新 PR 打开时，检查描述是否满足模板要求：
  - 必须有 Summary 部分
  - 必须有 Testing 部分
  - 如果涉及 UI 变更，必须有 Screenshots 部分
  如缺少任何部分，发礼貌评论请申请者更新。
```

每个 recipe 配置不到 10 分钟。团队一起用，每月省下几十小时。

---

## 十、底线

**旧方式：** 醒来 → 打开终端 → 启动 Claude Code 会话 → 输入命令 → 等结果 → 做下一件事。明天重复。

**新方式：** 配置一次 routines，让它们在 Anthropic 的云上运行，醒来直接看结果。

这不是理论上的改进。人们已经在运行整条 routine 栈，整夜处理他们的全部运维工作流。

> 用 Claude 当聊天机器人的人，和让 Claude 全天候自主工作的人——差距每周都在拉大。
>
> Routines 是跨越鸿沟的方式。

大多数人会读这篇文章，想"我回头应该设置一下"。
**真正今天就去创建第一个 routine 的人，下周就会有一个每周省下几小时的系统在跑。**

---

**关联阅读：**
- [Claude Code 高级使用指南](./agent-engineering/claude-code-advanced-tips-guide.md)
- [AI Agent 学习路线图 2026：Harness 即产品](./agent-engineering/ai-agent-roadmap-2026-what-to-learn-build-skip.md)
- [Thin Harness, Fat Skills：YC CEO 论 Agent 架构哲学](./agent-engineering/thin-harness-fat-skills-garry-tan.md)
