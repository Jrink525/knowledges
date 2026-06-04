---
title: "Claude Code 22 Hacks — mvanhorn 的 Agentic Engineering 实战心法"
tags:
  - claude-code
  - agentic-engineering
  - compound-engineering
  - codex
  - mvanhorn
  - workflow
  - agent-workflow
date: 2026-06-03
source: "https://x.com/mvanhorn/status/2061877533885473181"
authors: mvanhorn
---

# Claude Code 22 Hacks — Agentic Engineering 实战心法

> **来源：** [mvanhorn 的 X 长文](https://x.com/mvanhorn/status/2061877533885473181)  
> **中文整理：** 根据原文归纳，保留核心 Hack 和实操细节

mvanhorn 三个月前的 "Every Claude Code Hack I Know" 达到 91.3 万阅读。如今更新了 22 条新 Hack，涵盖从 daily workflow 到深度非工程工作的全场景。本文是其完整中文整理。

---

## 核心哲学：计划驱动 + 人类信号

> *"Traditional dev is 80% coding, 20% planning. This flips it. The thinking goes in the plan. The execution is mechanical."*

mvanhorn 的工作流核心：**任何想法先做 plan，plan 给 Agent 读（而不是人读），然后让 Agent 执行。** 他今年用这个模式做出了 last30days（27K stars）、Printing Press（4K+ stars）、Agent Cookie，并成为 Python、Go、GStack、Paperclip 等顶级开源项目的核心贡献者。

---

## 一、Hack 1-3：Plan 是一切

### 1. 有想法就 /ce-plan

规则一：任何时候想到一个点子，马上 `/ce-plan` 生成 `plan.md`。

- 疯狂的产品想法 → `/ce-plan`
- GitHub bug → 复制 issue URL，粘贴，`/ce-plan`
- 终端报错 → Cmd+Shift+4 截图，Ctrl+V 粘贴，`/ce-plan fix this`
- 截图、错误信息、设计稿、Slack 对话：任何东西都能扔进去
- 想法模糊时：先 `/ce-brainstorm` 和 Agent 讨论，梳理清楚后再 `/ce-plan`

> **工具：** [Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin) by @kieranklaassen & @trevin  
> **安装：** `/plugin marketplace add EveryInc/compound-engineering-plugin`

`/ce-plan` 背后运行多个并行 research agent：
1. 一个读你的代码库，找模式，检查你的约定
2. 一个搜索你过去的解决方案
3. 更多 agent 去查外部文档和最佳实践
4. 最终合并输出结构化的 `plan.md`：当前问题、方案、文件清单、验收标准、代码惯例

`/ce-work` 拿 plan 开始构建。context 太大？新开 session，指向 plan，继续干活。

### 2. 别读 plan.md

> *"I always make the plan.md. I almost never read it. Plans are for agents, you silly human."*

强制存在 plan 让 Agent 不能偷懒——它会研究、承诺方案、写出验收标准、然后真正达成。没有 plan 的 coding agent 会走捷径，提前停下。

所以：让 Agent 写 plan，你 skim 标题，然后跑 `/ce-work`。有疑问就 inline 问："wait, why this approach?" 或 "eli5 this plan"。

**关键心法：** Make the plan. Trust the plan. Don't read the plan.

### 3. 非工程工作也用 /ce-plan，先做 plan for the plan

`/ce-plan` 和 `/ce-work` 不只是写给代码的。策略文档、产品规格、竞争分析、董事会更新——全部可以用同一个循环。

**核心技巧：先让 Agent 规划如何规划。**

真实案例：mvanhorn 见了 Michael Margolis（前 GV 研究合伙人），对方让他读一本免费 PDF。他不是去 skim，而是打开 Claude Code：

> "/ce-plan make a plan for the plan. 我将给你两样东西：Margolis 的书 PDF，和我跟他的两小时对话转录。我想要一个深思熟虑的 plan，关于我的业务问题、那次对话、书中教训如何融合成能用的东西。但*现在不要写。*规划本身才是第一步。"

结果 Agent 花了 45 分钟生成了一个超详细的 plan。

**原理：** 直接要交付物 → Agent 走捷径。先要它规划怎么做 → 再来执行 → 每次都得到深度版本。

---

## 二、Hack 4-6：日常工作流

### 4. 语音输入

> *"Voice-to-LLM is different from voice-to-anything-else."*

语音转 LLM 不需要完美转录，因为 LLM 能根据上下文自动补齐。你可以含糊、断句、重新开始句子。

- **Mac：** Monologue（Every 出品）或 [Wispr Flow](https://wisprflow.ai)
- **Phone：** Apple 内置听写就够了（LLM 能理解残缺的句子）
- **硬件：** 办公室用鹅颈麦克风
- **痛点：** 在共享办公室用语音还是不太舒服

### 5. 大量 cmux 标签页

日常工作：4-6 个 cmux 标签页，每个一个独立 session：

```
Tab 1: 在写 plan
Tab 2: 在按另一个 plan 构建
Tab 3: 在跑 last30days
Tab 4: 在修测试发现的 bug
```

当 `/ce-plan` 在并行跑 research 时，切到另一个 tab 执行 `/ce-work`；当这个在构建时，第三个 tab 又收到了新 bug。

> 终端推荐：cmux（mvanhorn 之前用 Ghostty，但说总是错过通知）

### 6. 终端默认直接进入 Claude Code

新标签页应该直接打开 Claude Code，而不是 shell。一步到位。

**配置方法（paste 给 Claude Code）：**
> "Make every new terminal tab open directly into Claude Code. In ~/.config/ghostty/config, add `command = ~/.local/bin/claude-launcher.sh`. Then create `~/.local/bin/claude-launcher.sh` that runs `claude --dangerously-skip-permissions`, and when Claude exits prints a short note and drops me into zsh. chmod +x the script. This works for both Ghostty and cmux."

---

## 三、Hack 7-8：远程控制 + 权限

### 7. 远程控制 + 给 Claude 一个邮箱

**远程控制：**
- 每次打开新窗口都开启 remote control
- 设置 `"remoteControlAtStartup": true` 到 `~/.claude/settings.json`
- 在桌面开始 session，走开，在手机 Claude app 上接力继续

**邮箱接入（AgentMail）：**
- 用 [AgentMail](https://agentmail.com) 给 Claude 一个邮箱地址
- 发邮件到 inbox → 新 session 自动启动并处理邮件内容
- bug 出现在晚饭时？从手机发邮件，你回到桌前时 session 已经在跑了

> **开源项目：** github.com/mvanhorn/agentmail-to-claude-code  
> 三个组件：WebSocket 监听 daemon、终端后端（cmux/Ghostty）、发送器

### 8. 跳过权限确认（大胆用）

6 个 session 同时跑，不可能每个都手动点确认。

```json
// ~/.claude/settings.json
{
  "permissions": {
    "allow": [ "WebSearch", "WebFetch", "Bash", "Read", "Write", "Edit", "Glob", "Grep", "Task", "TodoWrite" ],
    "deny": [],
    "defaultMode": "bypassPermissions"
  },
  "skipDangerousModePermissionPrompt": true
}
```

**声音钩子**（非必须但强烈推荐——6 个 session 需要知道哪个完成了）：

```json
{
  "hooks": {
    "Stop": [{ "hooks": [{ "type": "command", "command": "afplay /System/Library/Sounds/Blow.aiff" }] }]
  }
}
```

**Codex 同样 YOLO：**
```toml
# ~/.codex/config.toml
approval_policy = "never"
sandbox_mode = "danger-full-access"
```
或 `codex --yolo`

> GitHub 在那里，搞砸了能回滚。

---

## 四、Hack 9-10：Claude + Codex 双引擎

### 9. Claude 规划，Codex 构建

mvanhorn 全天把工作交给 Codex，但几乎不打开 Codex CLI。三种方式：

1. **Codex IDE extension：** 发送任务，应用结果，不离开 Claude session
2. **`/ce-work --codex`：** 从 Compound Engineering 循环中直接把构建委托给 Codex
3. **Printing Press Codex 模式：** prompt 末尾加 `codex`，构建直接转到 Codex

**配置（双引擎开到最高 reasoning）：**
- Codex：reasoning xhigh, fast mode on
- Claude Code：reasoning xhigh, fast mode off
- 两个 $200 plan 并行 = 两个完整引擎

> 大并行构建给 Codex，规划和审美判断留给 Claude。也有人反过来用（Codex 构建，Claude 审核）。

### 10. Research 前置：last30days

在 `/ce-plan` 之前，先跑 `/last30days <topic>`

**真实案例：** 在 Vercel's agent-browser 和 Playwright 之间选择。不是去读文档，而是：
```
/last30days Vercel agent browser vs Playwright
```
几分钟内得到数十条 Reddit 讨论、X 帖子、YouTube 视频、HN 讨论。然后喂给 `/ce-plan integrate agent-browser`。plan 基于社区当下实际认知，而不是六个月前的训练数据。

> **开源：** last30days（27K+ stars）并行搜索 Reddit、X、YouTube、TikTok、Instagram、HN、Polymarket、GitHub、web。需要 ScrapeCreators key。

---

## 五、Hack 11-12：转录研判 + 人类信号

### 11. Granola 转录 + Raw 文本丢给 LLM

> *"The trick is raw. I don't summarize first."*

和候选人吃饭 90 分钟——聊产品、食物、孩子，中间穿插产品想法。Granola 一直在录。结束后把完整 raw 转录扔给 Claude Code：
```
/ce-plan turn this into a product proposal
```
Claude 基于实际代码库和过往策略文档做提取——自动忽略无关的餐厅闲聊，一次性生成了提案。

> **进阶：** Printing Press Granola CLI（最新升级，堪比魔术）
> - 任何会议直接获取结构化数据
> - 跨所有会议搜索
> - 找到三周前某人说过的一句话 → pipe 进 plan
> - 不再需要复制粘贴

### 12. Human Signal — 你是 taste，不是 hand

> *"Your job is not to do the work. Your job is to be the signal."*

Agent 提供产出量，你提供 taste、方向、反馈循环：
- "方案二更接近，但用方案一的语言"
- "先解决最大风险"
- "这段太长了"

**循环中稀缺的、有价值的东西是你的判断力，不是你的打字速度。**

> 越把自己定位为 human signal，而不是也在干活的手，产出越快。

---

## 六、Hack 13-15：视频 + 知识库 + 远程

### 13. HyperFrames 做视频

视频曾是外包或跳过的东西。现在用和代码一样的方式产出：**说话 → Agent 构建 → 反馈**。

HyperFrames 把视频构建为 HTML，这样 Agent 可以写。循环和代码一模一样，输出是 MP4：

- 每个视频是一个文件夹，包含 `script.md`，逐场景
- Agent 把脚本转成 composition 并渲染
- 没有编辑器、没有时间线

**作品：** Granola CLI demo、Agent Cookie launch  
**使用场景：** launch reels、产品演示、动画解说、加字幕的片段  
**GitHub GIF 技巧：** 上传到 catbox，在 PR、README、issues 中渲染精美

### 14. 笔记就是 Agent 的知识库

> *"Compounding context."*

策略文件夹技巧（从 3 月版本扩展）：Claude 能访问每个历史 plan，所以 plan 越来越聪明。把整个大脑都指向它：

- **Bear + Bear CLI：** 十年笔记、会议记录、半成品想法、决策 → Agent 可读写。个人 RAG，只是不这么叫它。
- **Obsidian：** mvanhorn 不用，但很多人喜欢
- **gbrain：** 跨机器和 Agent 的同步记忆层
- **supermemory：** 很多人推荐的 Agent 记忆层

**关键：** 选一个带 CLI/API 的笔记工具，指向你的 Agent，让知识复利。

### 15. 远程工作标准配置

- **Mosh：** 代替 SSH。在 bad wifi 和漫游时保持 session 响应。普通 SSH 下 Claude Code 会变得难以忍受
- **Tmux：** 飞机上用。SSH 到远程机器内的 tmux session，断网 20 分钟重连后一切照旧
- **Hermes + OpenClaw：** 同时跑。Hermes 做自学习重复任务，OpenClaw 用社区构建的 skills
- **Agent Cookie：** 在 Mac mini 和主 Mac 之间同步 cookies 和 .env

---

## 七、Hack 16-18：分享 + 技能 + 开源

### 16. Proof — 把 plan 分享给同事

`plan.md` 对终端里的人完美，但对不活在终端里的人没法用。

[Proof](https://proof)（Every 出品）填补了这个 gap：

- 打开 plan 像读文档
- 发送链接给同事，非终端人类也能清晰阅读
- 内联评论，评论回流到 Agent 工作循环
- 再也不用把 markdown 贴进 Slack 然后看着它渲染成垃圾

**mvanhorn 这篇文章就是在 cmux 里写的，Proof review 开在旁边。**

### 17. 写自己的 Skill

> *"Anything you do more than twice, turn into a skill."*

最大升级不是用 Agent，而是教它们可复用的技巧。

**技巧：** 不用从零写。指着已有的 skill 让 Agent 复制结构：
> "look at the Compound Engineering skill and help me make one like this for [X]."

mvanhorn 的开源贡献也都是这样来的：
- last30days：从自己想要的 skill 开始 → 开源 27K stars
- Printing Press：最常用的个人工具，320+ merged PRs
- Compound Engineering 第三大贡献者

### 18. 贡献开源项目

同样的 `/ce-plan` + `/ce-work` 循环不仅用于自己的项目，也用于别人的项目。mvanhorn 已有数百个 PR 被合并到 Python、Go、OpenCV、Vercel's Agent Browser、OpenClaw ——不是 typo fix，是真正的功能。

> **贡献排名：** #3 Compound Engineering / Superpowers / Emdash | #4 GStack / Paperclip | #6 Vercel Agent Browser | #2 Camoufox

**社交技巧：** 在 X 上花 $1-3/月订阅你尊重的人。提交 PR 时发 X post 给对方，对方会收到付费用户的特殊通知。

---

## 八、Hack 19-22：硬件 + 自动化 + 反思

### 19. 笔记本配置

原来两年的旧笔记本扛不住 6 个 Claude session + Codex。升级到 **M5 Max 64GB RAM**——依然被 workload 干废（全新机器电池只能撑一小时）。

**配件：**
- Anker 电池砖随身带
- Tesla 里放 Anker 充电器
- `sudo pmset -a disablesleep 1`（永不休眠）

### 20. Printing Press — 跑现实生活的 CLI

> *"CLIs that wrap real-world services so an agent can just do the errand."*

Printing Press（@ppressdev，3.7K+ stars）是一个 CLI 工具集，让 Agent 能直接跑现实世界的任务。

**关键组件：Agent Cookie**
- 把手持浏览器 session 传递给 CLI，CLI 以你的身份行事
- 不需要粘贴密码，不需要重新认证

**真实一个下午：**
```
- Tesla 预热（儿童上车前 10 分钟）
- Instacart 加购
- ESPN 比赛实时监控（快结束时才 ping 你）
- Alaska Airlines 查票价、查 Atmos 余额、/ce-plan 出订票策略（从足球场上操作）
```

### 21. AI Psychosis — 坦诚的反思

> *"Agents were supposed to do all the work for us. Instead, every friend I have is working the hardest they ever have in their lives."*

不是简单的"take a break, touch grass"。这是成瘾。用 Agent 构建是史上最好的电子游戏，循环就是那么好。

关键警示：
- 有人精力全在构建上，其他什么都不做了
- 然后 launch 了，没有用户——这没问题。圈套不是空 launch，而是消失在构建中，失去身边的人
- 问问自己：真的有任何人想要你做的东西吗？

### 22. 这篇文章就是这样写的

这是一个 markdown 文件。Claude Code in cmux，mvanhorn 对 Monologue 说话：
- "evolve the no-IDE opener"
- "make the don't-read-the-plan section spicier"
- "add the Tesla and Instacart story"

Agent 重写，他反馈，然后 Proof 里审阅。last30days 提供新鲜素材。没有 IDE。没有打字。**Talk, plan, build.**

---

## 总结：mvanhorn 的完整技术栈

| 类别 | 工具 |
|------|------|
| **规划** | Compound Engineering (`/ce-plan`, `/ce-brainstorm`, `/ce-work`) |
| **语音** | Monologue / Wispr Flow / Apple Dictation |
| **终端** | cmux（6+ tabs），Ghostty 配置直接进 Claude |
| **双引擎** | Claude Code（规划+taste）+ Codex（高速构建） |
| **预热研究** | last30days（并行搜索社区最新讨论） |
| **笔记/记忆** | Bear + Bear CLI / gbrain / supermemory |
| **会议转录** | Granola + Printing Press Granola CLI |
| **分享** | Proof（plan 文档化 + 评论回流） |
| **现实任务** | Printing Press CLI 集 + Agent Cookie |
| **远程** | Mosh + Tmux + Hermes/OpenClaw + Mac mini |
| **视频** | HyperFrames（HTML → MP4） |
| **技能** | 自己写 skill，复制优秀 skill 的结构 |

**一句话总结：** Talk → Research → Plan → Build → React。所有打字由 Agent 完成，人类只做判断和反馈。

---

*整理于 2026-06-03，基于 [mvanhorn 的 X 长文](https://x.com/mvanhorn/status/2061877533885473181)*
