---
title: "Claude Code 高阶用法：10 个插件搭起完整开发工作流"
tags:
  - claude-code
  - plugins
  - skills
  - mcp
  - development-workflow
  - productivity
date: 2026-06-05
source: "https://x.com/vincemask/status/2062046811301568726"
authors: "Vince 聊开发 (@vincemask)"
series: "claude-code-plugins"
---

# Claude Code 高阶用法：10 个插件搭起完整开发工作流

> **来源：** X.com 长文 by Vince 聊开发  
> **发布时间：** 2026-06-03  
> **数据：** 102 ❤️ · 21 🔁 · 14 💬

---

## 背景

裸装的 Claude Code 有几个明显问题：
- 跨 session 没有记忆
- 不能实时访问网络
- 没法做浏览器测试
- 缺少一道安全门槛挡住危险代码

插件就是来补这些洞的。ClaudePluginHub、Claude-Plugins.dev 和 Anthropic 的 Marketplace 加起来有超过 **9000 个插件**，生态已经不小了。

以下 10 个是作者实际用下来觉得有帮助的，每个解决一个具体痛点。

---

## 1. Ralph Loop — 自主编程代理

Anthropic 官方插件，借用了《辛普森一家》的角色名。

**原理：** 一套 stop-hook 模式，让 Claude 跑长时间、多任务的自主编程 session。你写一份 PRD，启动循环，Claude 逐个拾取任务、实现、commit，每完成一个就用**干净的 context** 开始下一个。

**最适合：** CRUD 生成、数据库迁移、测试覆盖、需求规格写清楚就能自动推进的重复性工作。

**警告：** PRD 越清晰效果越好。模棱两可的需求 Claude 会反复兜圈子浪费时间。

---

## 2. Context7 — 实时文档注入器

**问题：** Claude 用废弃 API 写代码。

**解法：** 把实时、版本准确的文档直接塞进 Claude 的上下文。按需查询 Context7 的 MCP 服务器，拿到 Next.js 15、React 19、Tailwind CSS 4 等框架的最新 API 信息。

**结果：** 幻觉大幅减少，生成的代码更贴近当前写法。

**最适合：** 跟更新频繁的类库和框架打交道的人。

---

## 3. Firecrawl — Web 数据提取

Web 数据提取评分最高的插件。一站式解决：
- JavaScript 渲染问题
- 裸 HTML 噪声太大
- 静态抓取内容很快过时

自动渲染 JS，把页面转成干净的 Markdown 或结构化 JSON。

**核心命令：**
- `/firecrawl:scrape` — 抓取单个页面
- `/firecrawl:crawl` — 爬全站
- `/firecrawl:search` — 搜索网页
- `/firecrawl:interact` — 填表单
- `/firecrawl:map` — 画网站结构图

**最适合：** 市场调研、竞品分析、文档聚合、需要实时网页数据的自动化工作流。

---

## 4. Playwright MCP — 自然语言驱动浏览器测试

写前端测试脚本很耗时。Playwright MCP 让 Claude 直接操控一个你能在屏幕上看到的 Chrome 窗口。

**关键能力：**
- 不用写脚本，告诉 Claude「测试结账流程」就执行
- 操作在浏览器里**实时执行**
- 可以在浏览器打开时**手动登录**，然后把已登录的 session 交给 Claude 接手

**最适合：** 前端工程师测试 UI 流程、调试线上页面、抓异步行为问题，但不想写测试代码。

---

## 5. Security Guidance — AI 代码安全护栏

每次文件编辑前做安全扫描，检查 **9 种关键漏洞模式**：

| 漏洞 | 说明 |
|------|------|
| 命令注入 | shell 命令拼接 |
| XSS | 跨站脚本 |
| `eval()` 使用 | 动态执行代码 |
| 危险 HTML | 不安全的内联 |
| Pickle 反序列化 | Python 反序列化攻击 |
| `os.system` | 系统命令调用 |

检测到风险时，插件**拦截编辑并弹出警告**，附带解释和修复建议。每种模式每个 session 只提醒一次，不频繁打断。

**建议：** 考虑第一个装。所有开发者的基础安全设施。

---

## 6. Figma MCP — 设计稿直接转代码

Claude 直接读取真实的 Figma 文件——真正的设计数据（frame、组件、布局数据），不是截图，不是文字描述。

**效果：** 生成的代码更贴近设计稿，跟设计师来回改的次数减少，早期开发速度明显加快。

**最适合：** 经常从设计文件实现 UI 的前端和全栈工程师。

---

## 7. Frontend Design — 去掉 AI UI 的同质感

AI 生成的 UI 有股明显味道：安全的配色、通用字体、到处都是 placeholder 组件。

**本 skill 推动 Claude 做更有辨识度的设计决策：**
- 避开被用烂的默认选项（Inter、Roboto、紫色渐变）
- 走一套有凝聚力的审美方向
- 用更重的排版、有氛围的背景、不对称布局
- 从视觉辨识度角度思考，不只是组件排列

**最适合：** 做产品 UI、落地页、dashboard，希望效果看起来像有设计师参与过。

---

## 8. Linear — issue tracker 搬进终端

在终端和 issue tracker 之间来回切窗口消耗注意力。Linear 插件直接把 Claude Code 连到 Linear 工作区。

**用法举例：**
- "总结 sprint 24 里所有 open ticket"
- "开始处理 ticket ENG-482，拆成子任务"
- "把 ENG-391 标记为 in progress"

**最适合：** 团队用 Linear 做项目管理，想保持编程不被打断的工程师。

---

## 9. Code Review — 多智能体并行 PR 审查

不是走马观花地扫一遍。它拉起**多个专门的 AI agent 并行审查**代码：测试、类型、错误处理、代码质量、可简化的重复逻辑各管一摊。

**每个发现都标注 confidence score：**
```
High Confidence:
  - Missing error handling in api/users.ts:45
Medium Confidence:
  - Consider extracting duplicate logic in utils/format.ts
```

**最适合：** 想在人类 reviewer 看 PR 之前，先走一遍结构化审查。

---

## 10. Chrome DevTools MCP — 真实浏览器调试

截图和日志文件只能搞一半。Chrome DevTools MCP 让 Claude 拿到你**真实浏览器的完整运行时状态**：网络请求、控制台报错、性能指标，用的就是你现有的已登录 Chrome session。

**可以直接问：** "这个请求为什么失败了？" 或 "什么在拖 LCP 分数？"

**最适合：** 调试复杂、需要登录态、前端 JS 很重的应用。静态分析搞不定时是最好的后手。

---

## 推荐安装顺序

**首批（补足 Claude Code 最要命的三个短板）：**

1. **MemClaw（或类似项目记忆系统）** — 跨 session 保留长期上下文，让 AI 记住架构、决策、约定和历史工作
2. **Firecrawl 或 Context7** — 获取当前文档、API 和网页内容，少依赖过时的训练数据
3. **Security Guidance** — 在代码部署之前拦住风险变更、漏洞、密钥泄露

**之后按需添加：** Playwright（前端测试）、Code Review（PR 审查）、Linear（项目管理）

> 每个插件都会往 context window 里加工具定义，装太多了反而拖慢响应速度。从小开始，装一个用一周，有用留着，没用卸掉。

---

# 附：开发提效插件 / Skill 补充指南

以下为 Vince 文章之外的额外补充，涵盖不同角度。

---

## 一、Skill vs Plugin vs MCP Server 区分

| 类型 | 本质 | 存放位置 | 复杂度 |
|------|------|---------|--------|
| **Skill** | 教学行为的 markdown 指令文件 | `~/.claude/skills/` | 低 — 纯文本 |
| **Plugin** | 打包的 skill + 支持文件 | `~/.claude/skills/` 或项目根 | 中 — 文本+文件 |
| **MCP Server** | 连接外部工具的运行时服务 | 本地进程或远程 URL | 高 — 需运行服务 |

简单理解：
- **Skill** = 小抄（cheat sheet）
- **Plugin** = 工具箱
- **MCP Server** = 通往其他应用的桥

---

## 二、Skill 安装路径

```bash
mkdir -p ~/.claude/skills/your-skill-name
# 把 skill.md 放进去即可
# Claude Code 在 session 启动时自动检测
```

你也放项目级 skill：`project-root/.claude/skills/`

---

## 三、按类别推荐的额外 Skill/Plugin

### 开发与学习

| Skill | 说明 |
|-------|------|
| **Git Dojo** | 交互式 git 训练，生成场景挑战、评分、跨 session 追踪进度 |
| **Commit Helper** | 强制执行 conventional commit 格式、禁止 force push 到 main |
| **Code Review** | 结构化代码审查模式：安全、性能、风格 |
| **Test Writer** | 匹配项目测试框架和约定的测试生成 skill |
| **Project Bootstrap** | 用你的偏好栈快速脚手架新项目，节省 30-60 分钟/项目 |

### 文档与写作

| Skill | 说明 |
|-------|------|
| **Napkin** | 从代码库快速生成 README、API 文档和 changelog |
| **Brand Voice** | 教会 Claude 你的品牌写作风格、禁用词和语气偏好 |
| **Content Pipeline** | 用特定模板和 SEO 规则生成博客/社媒/邮件序列 |
| **Localization** | 多语言 i18n 文件生成和一致性维护 |

### 设计与前端

| Skill | 说明 |
|-------|------|
| **Component Builder** | 按设计系统模式生成 React/Vue/Svelte 组件 |
| **Design System Auditor** | 对照设计 token 检查组件一致性 |
| **Accessibility Checker** | WCAG 合规检查、aria 标签生成、对比度修复 |

### SEO 与分析

| Skill | 说明 |
|-------|------|
| **SEO Audit** | 分析 meta tags、heading 结构、schema markup、Core Web Vitals |
| **Schema Generator** | 生成 JSON-LD 结构化数据 |

---

## 四、额外推荐 MCP Server

来自实际日用的精选（按分类排列）：

### 数据连接（已有数据读取）

| MCP | 安装 | 频率 | 说明 |
|-----|------|------|------|
| **Notion** | `claude mcp add --transport http notion https://mcp.notion.com/mcp` | 🟢 日频 | 读取 workspace 内容日历/项目数据库 |
| **Slack** | `claude mcp add --transport http slack https://mcp.slack.com` | 🟢 日频 | 读取消息、搜索频道、拉 thread 上下文 |
| **Google Drive** | 自建 (Google Cloud OAuth) | 🔴 周频 | 读取 Drive 文件（非官方，社区版） |
| **Supabase** | `claude mcp add supabase` (Claude Code 内建) | 🟢 每次 | 查数据库、运行迁移、部署 edge functions |

### 调研与搜索

| MCP | 说明 |
|-----|------|
| **Perplexity** | Web 搜索+多模型答案，带引用。最常用 MCP，无需切浏览器标签 |
| **NotebookLM** | 深度研究综合。种子资料→Claude 查询综合结果，可生成 audio overviews |
| **Whois** | 域名可用性查询，每秒比价 10 个域名，无需开浏览器 |

### 记忆（最被低估的类别）

**Memory MCP** 改变了整个关系：Claude 从"每 session 都需要解释"→"认识你的项目、你的声音、你的决定"。

这使**所有其他 MCP 都更强大**。

### 行动（写数据/部署）

| MCP | 说明 |
|-----|------|
| **Vercel** | 部署、查看日志、管理项目 |
| **GitHub** | 创建 PR、查看 issues、管理仓库 |
| **Stripe** | 查询交易、管理产品、处理退款 |
| **Gumroad** | 查看销售、管理产品、连接支付 |

---

## 五、如何自建 Skill

最小结构：

```markdown
# Skill Name

## Trigger
/your-command

## Description
一句话说明这个 skill 做什么。

## Instructions
Claude 被调用时应遵循的逐步行为。

## Rules
- 约束和护栏
- 输出格式要求
- 禁止做的事

## Examples
Input: [示例输入]
Output: [示例输出]
```

**最佳实践：**
- Skill 不超过 2000 tokens（越长越吃 context）
- 越具体越好：❌"帮我写代码" → ✅"用 Zod 验证 + 错误处理 + 匹配项目模式的测试文件生成 Next.js API 路由"
- Skill 和 `CLAUDE.md` 的区别：CLAUDE.md = 全局"始终开启"的上下文；Skill = "按需调用"的工具。CLAUDE.md 里可以引用 skill

---

## 六、推荐起步的三个问题

选择装什么插件/skill/MCP 时，问自己三个问题：

1. **我在反复复制粘贴什么？**
2. **我经常在哪些标签页之间切换？**
3. **哪里每次都会浪费 10 分钟？**

每个 MCP 要能杀死一个明确的摩擦点，否则不装。

---

## 七、与已有知识库的关联

- [Agent Memory System](/ai-tools/agent-memory-system-from-basics-to-production.md) — MemClaw / memory MCP 的底层原理
- [Skillify: Skill Engineering Guide](/ai-tools/skillify-skill-engineering-guide.md) — 自建 skill 的方法论
- [CREAO Cloud Agent Infrastructure](/ai-tools/agent-engineering/cloud-agent-infrastructure-creao-peter-pang.md) — Agent 运行时与工具层的分离设计
- [Trading Agent Skills with Claude SDK](/ai-tools/agent-engineering/trading-agent-skills-claude-sdk-zostaff.md) — Tool/Skill/Hook/Subagent 四种机制的深入

---

*整理于 2026-06-05，来自 Vince 聊开发 (@vincemask) X.com 长文 + 多来源补充*
