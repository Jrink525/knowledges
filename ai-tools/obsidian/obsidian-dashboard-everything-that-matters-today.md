---
title: "如何构建一个 Obsidian 仪表盘：每天一切尽在掌握"
tags:
  - obsidian
  - dataview
  - productivity
  - dashboard
  - claude-code
  - mcp
  - workflow
date: 2026-05-20
source: "https://x.com/cyrilxbt/status/2056555832805089310"
authors: "CyrilXBT"
---

# 如何构建一个 Obsidian 仪表盘：每天一切尽在掌握

> **来源：** [How to Build an Obsidian Dashboard That Shows You Everything That Matters Today](https://x.com/cyrilxbt/status/2056555832805089310) — CyrilXBT

![Obsidian Dashboard封面](../../image/obsidian-dashboard-1.jpg)

---

大多数人每天的开工方式都一样：

打开邮件 → 检查 Slack → 翻项目文件夹试图回忆进展 → 看日历 → 看任务列表 → 试图在脑子里拼出今天到底要做什么。

45分钟后，你对优先级有了个模糊的概念，早上已经废了一半。

**问题不在于信息不存在。** 信息就在你的项目笔记、客户文件、每日笔记、任务列表和日历里。

**问题在于你自己就是信息之间的集成层。** 你是那个负责连接所有信息的系统。

Obsidian 仪表盘把你从这个角色中解放出来——它从 Vault 各处抓取所有相关信息，在你打开任何一个项目文件之前，就已经把它们呈现在一个界面上。

你打开一篇笔记。看到今天所有重要的事。然后开始工作。

这篇指南将从零开始，带你构建一个完全自动化的仪表盘，并能连接到 Claude Code，实现智能晨间简报。

---

## 核心原则：只读不存

在写任何查询之前，先理解 Obsidian 仪表盘是什么、不是什么。

**仪表盘不是另一个存放信息的地方。** 它是一篇从 Vault 其他各处读取数据、只展示当下相关内容的笔记。

这个区别决定了仪表盘的价值。因为它从其他笔记读取而非自己存储信息，所以你永远不需要手动维护它——你按习惯更新项目文件、客户笔记和每日笔记，仪表盘每次打开都会自动反映这些变化。

仪表盘没有自己的内容。**它有查询。** 每条查询根据你定义的规则，从 Vault 的特定部分拉取特定信息。底层笔记改变，仪表盘随之改变。一处更新，全局生效。

---

## 仪表盘展示的内容

一个完整的商业仪表盘展示六大类信息：

1. **今日优先事项** — 今天到期或已逾期的任务，按优先级排序。最需要立即行动的十件事
2. **活跃项目状态** — 每个活跃项目的完成百分比、截止日期和下一步具体行动
3. **未来七天截止** — 未来七天内所有类型笔记的截止事项（项目、任务、客户交付物）
4. **客户健康度** — 每个活跃客户的关係健康状态、最后联系日期和下次计划接触点。风险客户自动置顶
5. **开放回路** — 昨天每日笔记中未完成的事项，需要继续跟进的
6. **收入脉搏** — 按月度收入贡献排序的活跃客户，附带实时总计

六个板块。一篇笔记。一切尽在掌握。

---

## 技术基础

两个 Obsidian 功能让实时仪表盘成为可能：

- **Dataview** — 社区插件，充当 Vault 的查询引擎。你可以在任何笔记中编写查询，从其他笔记中基于属性、标签或内容拉取信息。每次打开笔记时结果实时渲染
- **Properties（属性）** — 每篇笔记顶部的结构化元数据字段，YAML 格式。任务笔记有截止日期属性、状态属性、优先级属性。Dataview 读取这些属性，仪表盘展示它们

安装方式：Obsidian 设置 → 社区插件 → 浏览，搜索 Dataview，安装并启用。

这是核心仪表盘唯一需要的插件。

---

## 为仪表盘查询准备笔记结构

在构建仪表盘之前，每种笔记类型都需要一致的属性供 Dataview 读取。

**不一致的属性导致不完整的查询结果。** 对每种笔记类型保持一致的结构，才使仪表盘变得可靠。

关键要点：

- 属性名称必须在笔记和查询之间**完全匹配**。`type`、`status`、`priority`、`due`、`deadline`——这些字串两处都要一致。属性名一个拼写错误，那篇笔记就对查询"隐身"了
- 从**最小可用属性集**开始，随着你发现需要仪表盘展示什么信息再逐步添加

---

## 逐板块构建仪表盘

在 Vault 根目录创建一篇名为 `Dashboard.md` 的新笔记。这篇笔记在初始构建后永远不需要手动输入内容——它只有标题和从 Vault 其他部分拉取实时信息的 Dataview 查询。

### 板块 1：今日优先事项

```dataview
TABLE WITHOUT ID
  file.link as "Task",
  due as "Due",
  project as "Project",
  priority as "Priority"
FROM "02 - TASKS"
WHERE type = "task"
AND status != "complete"
AND (due = date(today) OR due < date(today))
SORT priority DESC, due ASC
LIMIT 10
```

这条查询拉取所有在今天或之前到期、尚未完成的任务。按优先级排序，最高杠杆项在最上面。**LIMIT 10 是有意为之**——显示 40 条逾期任务只会制造焦虑而非清晰度。限制 10 条迫使你在属性层面做优先级管理：如果今天有超过 10 个任务到期，没出现在仪表盘上的那些就需要调整截止日期或重新评估优先级。

### 板块 2：活跃项目

```dataview
TABLE WITHOUT ID
  file.link as "Project",
  client as "Client",
  completion + "%" as "Done",
  deadline as "Deadline",
  next_action as "Next Action",
  priority as "Priority"
FROM "01 - PROJECTS"
WHERE type = "project"
AND status = "active"
SORT priority DESC, deadline ASC
```

`next_action` 属性是这个表格最有价值的一列——它展示了每个项目当前需要什么，无需你打开任何项目文件。配合截止日期和完成度列，你可以在两分钟内评估所有活跃项目的完整状态。

### 板块 3：未来七天

```dataview
TABLE WITHOUT ID
  file.link as "Item",
  type as "Type",
  deadline as "Deadline",
  status as "Status",
  client as "Client"
FROM ""
WHERE (deadline >= date(today) AND deadline <= date(today) + dur(7 days))
AND status != "complete"
SORT deadline ASC
```

查询 Vault 中未来七天内有截止日期的所有内容，不限笔记类型。项目、任务和客户交付物按日期排列在一起。七天窗口足够短，确保列表中的每项都对短期规划有实际意义；也足够长，让你能提前行动而非仅被动应对截止日期。

### 板块 4：客户健康监控

```dataview
TABLE WITHOUT ID
  file.link as "Client",
  health as "Health",
  mrr as "MRR ($)",
  last_contact as "Last Contact",
  next_touchpoint as "Next Touchpoint"
FROM "03 - CLIENTS"
WHERE type = "client"
AND status = "active"
SORT health ASC, last_contact ASC
```

按 health 升序排序，风险客户自动出现在最上面。在每个健康层次内按 `last_contact` 升序排序，最久未联系的客户优先出现。`health` 属性使用三个值：`healthy`、`attention`、`atrisk`。保持一致，仪表盘就自动成为一个 CRM 审查工具。

### 板块 5：开放回路

日常笔记中需要一个简单约定：任何你想在第二天仪表盘上展示的事项，就在笔记中用 `OPEN:` 前缀写下来。

示例：
```
OPEN: 跟進客户的修订提案
OPEN: Q3 内容支柱决策
OPEN: 周四通话前审阅合同条款
```

查询：

```dataview
LIST
FROM "04 - DAILY"
WHERE type = "daily"
AND date = date(today) - dur(1 day)
FLATTEN file.lists AS item
WHERE contains(string(item), "OPEN:")
```

昨天每日笔记中所有以 `OPEN:` 开头的事项自动出现在今天的仪表盘上。这捕捉了那些足够重要需要记录、但又不夠正式成为任务的事项——大多数系统中容易掉入裂缝的事情。

### 板块 6：收入脉搏

```dataview
TABLE WITHOUT ID
  file.link as "Client",
  mrr as "MRR ($)",
  health as "Health",
  status as "Status"
FROM "03 - CLIENTS"
WHERE type = "client"
AND status = "active"
SORT mrr DESC
```

在表格下方添加这个内联查询以显示总计：

```
**Total MRR:** `$= dv.pages('"03 - CLIENTS"').where(p => p.type === "client" && p.status === "active").map(p => p.mrr).array().reduce((a,b) => a + b, 0)`
```

无需电子表格，无需手动计算。每次你更改客户属性，数字自动更新。

---

## 完整仪表盘模板

```markdown
# Dashboard
> `$= dv.date("today").toFormat("EEEE, MMMM d, yyyy")`

---

## Today's Priorities

[DATAVIEW QUERY — SECTION 1]

---

## Active Projects

[DATAVIEW QUERY — SECTION 2]

---

## Next 7 Days

[DATAVIEW QUERY — SECTION 3]

---

## Client Health

[DATAVIEW QUERY — SECTION 4]

---

## Open Loops

[DATAVIEW QUERY — SECTION 5]

---

## Revenue Pulse

[DATAVIEW QUERY — SECTION 6]

**Total MRR:** [INLINE QUERY]
```

将每个占位符替换为上方对应板块的查询。顶部的内联日期会自动渲染今天的日期。

---

## 通过 MCP 连接 Claude Code

上述仪表盘已经比大多数业务管理方案更有用。通过 Filesystem MCP 连接到 Claude Code，它能获得两项改变早晨体验的能力：

### 1. 智能晨间简报

Claude 不再展示六张原始数据表格，而是读取仪表盘、综合六个板块的信息，生成自然语言简报——**不是数据是什么，而是数据对今天意味着什么**。

晨间简报提示词：

```
Read my Obsidian dashboard note and every file it references.

Synthesize a morning briefing that tells me:
1. The single most important thing to accomplish today
2. What requires my attention before noon and why
3. What is at risk if I do not act on it today
4. The client relationship that most needs attention right now
5. One decision sitting open that I should make before I start

Do not describe the tables. Tell me what they mean.
Keep the briefing under 300 words. Start with the most urgent thing.
```

这份简报通过 **N8N** 每天早上 6 点自动运行，读取实时仪表盘数据，在你打开笔记本之前就将简报写入你的每日笔记。

### 2. 自动属性更新

当你完成工作时，Claude 自动更新对应的项目和任务文件属性。

每日笔记中的完成约定：

```
DONE: [项目名] — [具体交付物]
UPDATE: [项目名] — completion: 65
```

Claude 读取这些条目，在 Vault 中找到对应文件，更新属性并记录变更。仪表盘立即反映更新。

---

## 开启仪表盘后的日常流程

这是你一天头十分钟的样子：

- **6:00 AM** — 手机收到 Telegram 通知。晨间简报已就绪，在你的每日笔记中
- **6:02 AM** — 阅读简报。它告诉你今天最重要的那件事、哪个客户关系需要关注。大约 180 字
- **6:05 AM** — 打开仪表盘，确认简报提到的优先级与表格展示一致。添加任何新任务，填入正确的属性
- **6:10 AM** — 开始工作

不先看邮件。不先看 Slack。不花 45 分钟在五个工具间来回切换。**你直接开始工作，因为你知道什么最重要。**

---

## 让仪表盘长期保持准确

仪表盘的好坏取决于其底层数据。三个习惯确保数据可靠：

1. **一有变化就更新属性** — 项目从 active 变为 complete 时立刻更新 status。客户健康度变化当天更新 health。陈旧的属性产生陈旧的仪表盘数据
2. **始终使用 OPEN: 约定** — 每次有事需要延续到明天，就在每日笔记中用 OPEN: 前缀写下来。不要依赖记忆手动结转
3. **日终也看仪表盘，不只在日初看** — 每天 3 分钟日终仪表盘审查，在明早简报运行前更新好数据。下午 5 点做 5 个属性更新，比早上读简报时做 5 个更新更有效

---

## 常见问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 查询返回空结果 | 属性名不完全匹配 | 检查拼写、大小写差异、缺少引号 |
| 属性不显示 | YAML frontmatter 位置不对 | frontmatter 必须在笔记最顶部，开头的 `---` 前不能有任何字符 |
| 日期查询不工作 | 日期格式不对 | 必须用 YYYY-MM-DD 格式：`2026-05-18`（不是 `2026-5-18`） |
| 仪表盘加载缓慢 | 匹配查询条件的笔记太多 | 添加文件夹筛选缩小范围，FROM "01 - PROJECTS" 比 FROM "" 快得多 |
| 内联计算报错 | MRR 属性类型错误 | mrr 必须是数字：`mrr: 3000`（不是 `mrr: "$3,000"`） |

---

## 30 天后的变化

仪表盘从第一天早上就用得上的价值。**复合效应在第二个月显现：**

- 每个属性更新都在训练保持 Vault 数据最新的习惯，这种习惯会复合，最终让仪表盘真正准确
- 每个 OPEN: 项都弥合了你**打算做**和**实际跟踪**之间的差距。30 天后，那些重要但不紧急、曾经总会掉进裂缝的事项，不再丢失
- Claude 从仪表盘数据生成的每份晨间简报，随着底层数据越来越丰富，对你的实际工作模式也越来越精准

到第二个月，你会想不起没有仪表盘时的早晨是怎样的。到第三个月，你无法想象没有它就开始一天。

**构建只需一个下午。复合效应从第一个早晨开始。今天就做。**

---

> 关注 [@cyrilXBT](https://x.com/cyrilxbt) 获取精确的 Dataview 查询、Claude 提示词和 Vault 模板，让这套系统完整运行。

---

*Processed on 2026-05-20 from https://x.com/cyrilxbt/status/2056555832805089310*
