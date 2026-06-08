---
title: "Every Agentic Engineering Hack I Know (June 2026)"
source: "https://x.com/mvanhorn/status/2061877533885473181"
author: "Matt Van Horn (@mvanhorn)"
published: 2026-06-02
category: "ai-tools/agent-engineering"
tags: [agentic-engineering, claude-code, ce-plan, compound-engineering, voice, workflow]
---

# Matt Van Horn: 我所知道的所有 Agentic Engineering 技巧 (2026.6)

> 原文：[Matt Van Horn @mvanhorn](https://x.com/mvanhorn/status/2061877533885473181)  
> 浏览量：858K | 书签：8.8K | 点赞：2.9K

---

## 背景

三个月前 Matt 发了"Every Claude Code Hack I Know"（913K 浏览量）。当时 @kevinrose 问用什么 IDE，Matt 的回答是："没有 IDE。只有 plan.md 文件和语音。" 

这一年他做出了 **last30days (27K stars)**、**Printing Press (4K+ stars)**、**Agent Cookie**，成为 Python、Go、GStack、Paperclip 等顶级开源项目的核心贡献者。这些都是他 Agentic Engineering 实践经验的结晶。

---

## Hack 1: 有想法的一刻 → 立刻做 /ce-plan

**核心规则：** 有想法 → `/ce-plan` 生成 plan.md，不犹豫、不直接写代码。

- 疯狂的产品想法：`/ce-plan`
- GitHub bug：复制 issue URL，粘贴，`/ce-plan`
- 终端报错：截图 → 粘贴 → `/ce-plan fix this`
- 模糊想法：先用 `/ce-brainstorm` 梳理，再 `/ce-plan`

**背后机制：** `/ce-plan` 并行派出 research agent——一个读你的代码库找模式，一个搜历史解决方案，需要的话查外部文档和最佳实践——然后写出结构化的 plan.md（含 checkboxes 验收标准）。

`/ce-work` 按计划执行。上下文爆炸时启动新 session，指向 plan.md 继续干。**plan 是穿越一切的检查点。**

> 传统开发 80% 编码 + 20% 规划。这里反过来了：思考在 plan 里，执行是机械的。

**工具：** Compound Engineering 插件（[@kieranklaassen](https://x.com/kieranklaassen) 和 [@trevin](https://x.com/trevin) 开发）

---

## Hack 2: 不要读 plan.md

> **Plan 是给 Agent 看的，你这个愚蠢的人类。**

写 plan 是为了让 agent 不偷懒——它必须先研究、承诺方法、写下验收标准、然后逐一打勾。有 plan 的 coding agent 交得出成品，没有的就偷工减料半途而废。

做法：写 plan → 只看标题 → 运行 `/ce-work`。有疑问在 session 里内联提问："wait, why this approach?"，或者让它 TL;DR 或 eli5。

> **写 plan。信任 plan。别读 plan。**

---

## Hack 3: 用于最深层的非工程工作——先做 Plan for the Plan

这是 Matt 三月以来最大的领悟。`/ce-plan` 和 `/ce-work` **不只用于代码**，它有通用规划模式。

技巧：**先做 plan for the plan**。

真实案例：Matt 见了前 GV 研究合伙人 Michael Margolis，对方让他读一本书。他没有直接开干，而是打开 Claude Code 说：

> "`/ce-plan make a plan for the plan`。我马上给你两样东西：Margolis 的书 PDF，和我跟他两小时谈话的转录。我想得到一个把这三件事结合起来的方案。**现在别写那份文档。写作是后面的工作。我现在只想要你规划如何读书、挖掘转录、产出一份好文档的方案。**"

它花了 45 分钟做了一份 EPIC plan。

> **让 LLM 不偷懒的最佳技巧：不要让它直接产出，先让它规划如何产出，再执行。**

---

## Hack 4: 拥抱语音（Get Voice-Pilled）

语音转 LLM 和语音转其他东西不一样。转录不需要完美，因为听的一方能猜上下文。模糊、中断、重说都不怕。

**Matt 的方案：**
- **Mac 版：** MacWhisper（Fast Whisper 模型）+ BetterTouchTool → global hotkey 录制并转文字→ 发送到 Claude Code
- **Windows 版：** SuperWhisper + AutoHotkey 实现同样流程
- 键盘快捷键比点开 App 打字快太多，适合洗澡、跑步时突然来的灵感

---

## Hack 5: 不要写代码，读代码

**不要告诉模型怎么编码，告诉它你要什么，让它自己读你的代码库来找答案。**

Matt 说现在的 LLM 太强了，你完全不需要说"用 React 18 + Next.js 14 + Tailwind...它的中间层用这个模式...token 管理用这个方案"。你只需要说"我要 XXX"，框架就自己读代码学习了。

用法：粘贴截图、报错信息、issue URL，或者简单描述，"add feature X"。

> **最好的 prompt 不是告诉你 LLM 怎么编码，而是你怎么省话。**

---

## Hack 6: 一次只让 Agent 处理一个 Topic

Claude Code 一个 session 内同时接入多个 topic 时表现下降明显。Matt 用一个名为 **Session Switcher** 的 Claude Code 自定义 slash command（属于 Compound Engineering 插件）来管理：

- `/list-sessions` 或 `ls-sessions` → 列出所有活跃 session 及其 topic
- `/switch-session <name>` → 切换到目标 session，自动加载该 topic 的上下文
- `/close-session <name>` → 关闭旧的

> 用 Session Switcher 保持每个 session 单一 topic 粒度，上下文保持新鲜可管理。

---

## Hack 7: 让 Agent 自由使用你的 App，不要用 API

当 Agent 需要与非官方 API 的网页应用交互时，不要写解析器或爬虫，**直接让它用自然语言操作 UI**。

**Matt 的实战：**
- Google Analytics 的新 GA4 界面无法通过 API 获取他想要的指标 → 让 Claude Code 开着电脑使用 GA4 网页 → 让它问"有多少人在用我们的 app？"→ 它会打开浏览器、登录、导航、找到表格、截图或读取显示的内容
- Grammarly 同理：让它操作 Grammarly UI 检查错误，而不是调用不存在的 API
- 快递追踪、航班查询、任何没有开放 API 的场景，agent 操作网页 UI 更靠谱

**关键技巧：** 如果用 screenshot-based 的电脑调用工具，确保写一个 CLAUDE.md 文件加入 agentic rules，列出你常用的应用 URL、认证方式、登录步骤和导航指引。

---

## Hack 8: VSCode 的 Agent Mode 正在改变一切

Matt 用 VS Code Insiders 的 Agent Mode（在 Github Copilot 里）做日常深度编码。他对 VS Code Agent Mode 的评价：

- 强模式：Agent 能按要求创建、编辑、读取多个文件，运行命令，读终端输出
- **它比 IDE 更强** — Agent Mode 不关心你的项目结构，只要告诉它最终目标，它找到路径

Matt 的 setup：他把 **Compound Engineering** 的 slash commands 也带进 VS Code，通过 [Cline](https://cline.biz) 插件以 MCP 服务器的形式运行。

> VS Code Agent Mode 的 killer feature：IDE UI 不变，但你在和一个能调用任意 MCP 工具的 AI 交谈。Compound Engineering 的 /ce-plan 在 VS Code 里也完美工作。

---

## Hack 9: 把桌面当 MCP 服务器

Matt 有一个被称为 **Desktop MCP** 的专用 Claude Code session，它把整个桌面暴露为 MCP 服务器。这个 session 的功能：

- **运行任何桌面应用：** 打开 Chrome、Safari、Finder、终端、系统设置
- **系统集成：** 截屏、读剪贴板、获取 RDP 控制、Ollama 本地模型
- **浏览器控制：** 打开网页、点击按钮、阅读 DOM 内容、截屏
- **内容提取：** 访问 Slack、邮件、日历，读取你需要的内容

**典型案例：** 启动一个 app → 打开 Slack → 截取某频道消息 → 整理成周报 → 发送邮件。

这个桌面 MCP session 是让 agent 操作你电脑的终极方式。

---

## Hack 10: 两个 Hotkey 绑定所有 Agent

Matt 只用两个全局快捷键 (hotkey) 控制所有 Agent：

1. **Hotkey 1（Mac: Cmd+Shift+Space）** → 打开 Claude Code 终端（"随时随地召唤"）
2. **Hotkey 2（Mac: Cmd+Shift+`）** → 激活 VS Code Agent Mode（"深度编码"）

通过 Raycast/Alfred 把热键绑定到对应的 App/终端命令。Matt 坚持使用快捷键而非任何点按操作。

---

## Hack 11: 用计算机控制 Agent 调试 CI

当 CI 失败时，不要让 agent 只看日志猜测。**让 Agent 打开浏览器登录 CI → 找到失败任务 → 点击查看详细输出。** 看不清楚的日志？让 Agent 打开 CI 的"原始日志"模式（纯文本）。

Matt 关于浏览器调试的使用场景：
- CI 失败 → 让它自己去 CI 平台看
- 生产告警 → 让它去 Datadog 或 Sentry 自己查

**如果不用 Computer Control：** 把错误日志完整粘贴过来，但不如让它自己去看来得快。

---

## Hack 12: 不要补丁，要 Plan 回退

当某个实现方向不对时，永远不要修改已有的 plan.md（它会累积损坏的上下文）。正确的做法：

```
# 检查所有 plan 文件的可疑目录，找到当前 plan
/ce-plan revise this: the current approach isn't working because [原因]
# 它写一个新 plan 修复问题
/ce-work
```

**关键：** `revise` 是 `/ce-plan` 的内置动词。它会做对的事：
1. 读当前 plan
2. 理解发生了什么
3. 写一个新的修正 plan 覆盖旧的
4. 你运行 `/ce-work` 执行修正

不要手动修改 plan 文件。让 agent 用 `revise` 自己处理。

---

## 最终 TL;DR

Matt 的全栈可以一句话总结：

> **语音进 → /ce-plan 出 → /ce-work 干 → Session Switcher 维护 → Computer Control 救急 → 一个 hotkey 搞定一切。**

把这些技巧逐个设置好，然后让 Agent 按 plan 执行。这就是 Matt 从高中生水平的软件交付到顶级开源核心贡献者的完整路径。
