---
title: "到底什么是 Loop？Part 2：15 个真实运行的 AI 循环（附可直接复制的命令）"
tags:
  - ai-loop
  - agent
  - claude-code
  - codex
  - automation
  - workflow
date: 2026-06-21
source: "https://x.com/mvanhorn/status/2068426104088748331"
authors: "Matt Van Horn"
---

# 到底什么是 Loop？Part 2：15 个真实运行的 AI 循环（附可直接复制的命令）

> **来源：** [WTF Is a Loop? Part 2: The 15 Loops People Are Actually Running (and the Commands to Steal Them)](https://x.com/mvanhorn/status/2068426104088748331) by Matt Van Horn (@mvanhorn)
>
> 上篇"WTF Is a Loop?"获得了 360 万阅读量。这是续篇，回答下一个问题：人们**实际在跑**哪些 Loop？

---

## 先搞清楚三个命令（这是所有人搞错的地方）

TikTok 创作者 inyourhandmedia 给出了最清晰的区分：

- **Goal** — 持续工作直到目标达成
- **Loop** — 我在场时重复执行任务
- **Routine** — 我不在时持续运行

对应的实际命令：

### `/goal <条件>` 
持续运行直到可验证的条件为真。每一步用独立快速模型检查是否真正完成。这是"修复直到测试通过"的那个。两个工具都支持：
- **Claude Code** — v2.1.139 版本发布
- **Codex** — CLI v0.128.0 发布，带 set/pause/resume/clear 控制

### `/loop <间隔> <提示词>`
在会话打开时按定时器重复，如 `/loop 5m check the deploy`。用于实时监控。Codex 没有 `/loop` 命令，其等价方式是 `codex exec` 套 shell 循环，或 Codex 应用中的分钟级 Thread Automation。

### `/schedule <描述>`
创建云 Routine，在你合上电脑时运行，如 `/schedule daily PR review at 9am`。"我在睡觉时"运行的那个。Codex 的等价方式是 Codex 应用中的 Automations：独立/项目/线程自动化，支持每日/每周/自定义 cron 调度，结果投递到 Triage 收件箱。

> ⚠️ **一个常见陷阱**：两个工具中都没有 `/routine` 命令。Claude Code 中用 `/schedule`；Codex 中用 Automations。

---

## 15 个真实运行的 Loop

> 以下 11 个来自 X、TikTok、Reddit 和 GitHub，附带了原始互动数据；最后 4 个来自精心筛选的目录。

### 1. 构建-测试-修复对（loop）

**来源：** raycfu 的教程（Instagram，43,587 次观看，1,040 条评论）

**模式：** 两个 agent——一个写代码的构建者 + 一个运行测试、类型检查和 lint 的检查者，报告哪些地方出错了。它们来回传递工作直到所有检查通过。

**价值：** 一次性的 agent 发布的是带 bug 的代码。这个对解决了它。

### 2. Boris 的验证器循环（loop）

**来源：** Boris Cherny 本人的描述（@bcherny，781 个赞）

**模式：** 同时运行 Claude Code + 高级模型 + 验证器，循环执行任务，不断移除瓶颈。**验证器是所有人都跳过的环节**。没有它你只是在盲目信任 agent。

### 3. Loop-engineer 入门包（harness）

**来源：** AI Jason（15,436 次观看，537 个赞），提供免费 loop-engineer 模板

**模式：** 一个代码库 harness + 知识模板，克隆后指向你的仓库即可运行。无需从零搭建 build/observe/verify/stop 基础设施。

**价值：** 如果你想今晚就跑起来，这是最快的入口。

### 4. 五分钟仓库维护者（loop）

**来源：** Peter Steinberger（过去 30 天合并 859 个 PR，接受率 95%）

**模式：** 工作时每五分钟运行一次。agent 自主决定做什么维护，不是硬编码脚本。**这个决策是整个要点**。

### 5. 计划-生成-验证-修复循环（goal）

**来源：** qbuilder（TikTok，4,560 次观看，125 个赞）

**模式：** plan → generate → verify → fix → repeat，所有输出保存到文件，**硬上限 5 次迭代**。你只读最终版本。上限让它离开时也安全。

### 6. roborev：提交后审查者（已发布工具）

**来源：** Dan Kornas 贡献的开源工具

**模式：** 免费开源 Go 二进制程序（roborev.io）。安装一个 git hook，每次提交触发后台审查，将发现反馈到 agent 修复循环（趁上下文还热）。发布推只有 20 个赞，但仓库有 **1,410 颗星**，提交活跃度极高。

**关键：** 它是本文最终论点的可安装版本——**一个活在你的 Loop 内部的验证器**。

### 7. Goal-meta-skill（goal）

**来源：** evgenii.arsentev（32 个赞，950 次观看），数天内获得 600+ 星

**模式：** 一个技能，唯一工作是将模糊需求转化为**严谨的目标**，指定：结果、如何验证、不要碰什么、何时停止。

> 如作者所说："你的 agent 不笨，你的指令只是太模糊。"

### 8. 日处理 15,000 封邮件的循环（routine）

**来源：** r/LangChain 上的一个构建者

**模式：** 完整架构：循环检查收件箱、分类和起草回复、仅将需要人工处理的升级。是 Reddit 上罕见的**完整生产级** Loop，不是 Demo。

### 9. 反旋转循环（loop）

**来源：** r/claudeskills 上的 Claude Code 技能

**模式：** 自主 build/audit/verify 循环，直到机器可检查的合约通过。包含**明确的防旋转停止**：无进展检测、重试上限、来回摇摆检测、预算控制。

> "大多数 agent 循环从不问自己是否真的取得进展——它们要么重试同一个失败的方法，要么悄悄地编辑测试让它通过。"

### 10. 写循环而不是写代码的 routine

**来源：** 构建 Claude Code 的人（Peter Steinberger 本人）

**模式：** 他不写代码了。他写 loop，loop 在他睡觉时写代码。最高流传版本（@0xMovez，984 个赞）给出了数字：他 **30% 的代码现在完全由 loop 编写**。形状是一个定时 routine，监控 PRs，夜间自动落地可修复的。

### 11. 人工审核批准队列（loop）

**来源：** r/n8n 上的讨论

**模式：** 工作流运行 → 暂停 → 给你发送消息，带 approve/revise/skip 按钮。将人工审核视为自己的队列，附带提醒和截止时间。Loop 形状相同，但停止条件是**你的批准**而不是测试通过。

---

### 从目录中值得偷用的 4 个

以下来自 **Matthew Berman 的 Forward Future Loop Library**——一个精选目录，其中信号是**筛选质量**而非点赞数。

### 12. 生产错误扫描（goal，catalog）

Berman 最高实用性的 goal。读取生产日志，区分真实可操作的错误和噪音，修复可操作的（附测试），打开 PR。价值在**分类**；告诉它"可操作"是什么意思，否则它会追幽灵。

### 13. 质量连续成功循环（goal，catalog）

同样来自 Berman。不满足于第一次绿色运行。它测试真实场景，只有在**连续通过一定次数**后才宣告胜利。一次绿色运行是运气，连续成功才是可靠。

### 14. 对抗性审查工具（已发布命令，catalog）

**Lukas Kucinski 的 Clodex**：让 Codex 在合并前审查 Claude 的 PR，两个不同模型系列必须达成一致代码才能落地。

```bash
claude-codex pr review --model claude-sonnet --max-iter 5 --threshold medium
```

`--max-iter 5` 和 `--threshold medium` 是整个要点。它最多跟自己争论五次，只有通过门槛的工作才通过。

### 15. 完成合约工具（已发布命令，catalog）

**3goblack 的 Loop**（@Dis_Trackted）：修复最常见的失败——agent 说"完成"但实际上没完成。开始工作前写一份合约，定义"完成"意味着什么以及每个需求需要什么证据，然后拒绝在无证据的情况下声称成功。

---

## 光环之外：Loop 是带验证器的钱坑

> 每篇相同的地方，两个警告反复出现。

### 第一：成本

浪漫版：一千个 agent 一夜之间建起我的公司。生产版：一张账单。

- **Uber 将其工程师的工具使用限制在每人每月 1500 美元**——在四个月内烧完了年度 AI 预算
- 一个 Reddit 用户一夜之间用一个命令烧掉了约 **6,000 美元**（1,273 个赞）
- YouTube 评论的精辟总结：

```
while (you have tokens):
    Burn them in a loop!
```

所以每个 goal 都要设预算，每个 loop 都要有上限。Goal 条件可以带"N 轮后停止"。Routine 在每日上限的计划上运行。**离开前设置上限，不要等邮件到了再设。**

### 第二：验证

> "一个无法分辨好坏输出的 loop 不会节省你的工作——它只是更快地产生错误答案。" —— @ahmetbilicanxyz

这就是为什么 `/goal` 使用独立模型作为**裁判**，而不是让 worker 给自己的作业打分。也是为什么上面最强的 loop（Boris 的验证器、build-test-fix 对、Clodex）都在 loop 内部放了一个**第二个独立的审视者**。

一个自己打分的 agent 会删除失败的测试然后宣布完成。怀疑论者的底线是对的。

> "又一个新趋势：Loop Engineering。你还在写提示词？你太落后了。"
> — Maximilian Schwarzmuller, YouTube（2,036 个赞）

他**说对了一半**。调度层确实只是 cron 的变体。但 cron 从未有过的是**一个在主体中的决策者**——读取状态、行动、检查是否有效、决定是否继续。**那个决策才是全新的东西**。其他一切都是管道。

---

## 今晚如何开始

你不需要全部 15 个。研究不断收敛到三个动作，每种一个：

1. 以 **loop** 运行 build-test-fix 对，在你看着的时候能有所改善
2. 工作时以 **loop** 运行五分钟仓库维护者
3. 以 **schedule** 运行写循环 PR routine 过夜，早上醒来收获完成的工作

**为每一个设预算和验证器。** 明天早上之前你就能拥有一个可工作的 loop 栈。

然后去逛逛 **Matthew Berman 的 Forward Future Loop Library**（[catalog](https://github.com/BermanForwardFuture/loop-library)），它收录了可复制粘贴的 loop，附上作者署名，loop 在开放仓库中可安装。

> 转变是真实的，而且比讨论的简单。**停止成为循环中的那个环节。** 写 goal、loop 或 routine，给它预算和检查自己的能力，然后去决定下一步构建什么。

当有人问 agent 工作时你该做什么时，一位疲倦的实践者的回答：

> "出去走走。给你妈打个电话。做一顿健康的饭。照顾好自己。"
> — justinkthornton, Reddit, r/codex

---

*处理时间：2026-06-21 | 来源：X/Twitter @mvanhorn*
