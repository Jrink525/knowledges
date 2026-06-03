---
title: "Prompt Master — 跨工具精准提示词生成技能工作手册"
author: "nidhinjs"
source: "GitHub / Open Source Projects"
date: 2026-05-17
url: "https://github.com/nidhinjs/prompt-master"
tags:
  - prompt-engineering
  - claude-skills
  - prompt-master
  - ai-tools
  - midjourney
  - cursor
  - claude-code
  - chatgpt
category: "prompt-engineering"
description: "Prompt Master 的深入分析和工作手册。一个 Claude Skill，能够为任何 AI 工具编写精准提示词（prompt），支持 20+ 工具、9 维度意图提取、多框架自动路由、Token 效率审计和记忆块系统。MIT 协议开源。"
---

# Prompt Master — 让 AI 为你写出更好的提示词

## 项目概述

[Prompt Master](https://github.com/nidhinjs/prompt-master) 是一个 **Claude Skill**，它的使命是：**为任何 AI 工具编写精准的提示词**。它不是一个独立的 App 或 API wrapper，而是一个可以直接加载到 Claude 的系统提示词（system prompt），让 Claude 瞬间变成你的提示词工程师。

> "The best prompt is not the longest. It's the one where every word is load-bearing."

### 核心理念

大多数 AI 用户的资源浪费方式完全相同：
1. 写模糊的提示 → 得到错误输出
2. 重新提示 → 更接近一些
3. 再提示一次 → 终于在第 4 次得到正确答案

**3 次浪费的 API 调用。每天 50 个提示——那就是真金白银和时间在流失。**

Prompt Master 的解法：**一次命中，零浪费。** 它不是让提示变得更长，而是让它们更**锋利**。

### 适用工具（20+）

| 类别 | 工具 |
|------|------|
| 推理型 LLM | Claude, ChatGPT/GPT-5.x, Gemini 2.x, DeepSeek-R1, MiniMax, Qwen |
| 思考型 LLM | o1/o3/o4-mini |
| 本地 / 开源 LLM | Ollama, Llama, Mistral, Qwen |
| IDE 型 AI | Cursor, Windsurf, GitHub Copilot, Cline, Antigravity |
| Agent 型 AI | Claude Code, Devin, SWE-agent, Manus, OpenClaw |
| 全栈生成器 | Bolt, v0, Lovable, Figma Make, Google Stitch |
| 图像 AI | Midjourney, DALL-E 3, Stable Diffusion, SeeDream, ComfyUI |
| 3D AI | Meshy, Tripo, Rodin, BlenderGPT, Unity AI |
| 视频 AI | Sora, Runway, LTX, Dream Machine, Kling |
| 语音 AI | ElevenLabs |
| 工作流自动化 | Zapier, Make, n8n |
| 搜索 AI | Perplexity, SearchGPT |

---

## 价值与洞察

### 价值 1：工具感知能力

**核心洞察：** 不同 AI 工具有截然不同的"性情"。Claude 喜欢 XML 结构，Midjourney 需要逗号分隔的描述符 + 参数，Ollama 需要 Modelfile 格式的系统提示，而 o1/o3 根本不需要 Chain-of-Thought（它们自己会思考）。

Prompt Master 自动检测目标工具，**静默路由**到正确的提示结构。你只需描述目标，它负责格式转换。

### 价值 2：9 维度意图提取

每次请求，Prompt Master 会系统化提取 9 个维度：

1. **Task（任务）** — 具体做什么
2. **Input（输入）** — 提供什么数据
3. **Output（输出）** — 期望什么格式
4. **Constraints（约束）** — 有什么限制
5. **Context（上下文）** — 相关背景
6. **Audience（受众）** — 写给谁看的
7. **Memory（记忆）** — 之前的决策
8. **Success Criteria（成功标准）** — 怎么算完成
9. **Examples（示例）** — 参考样本

### 价值 3：多重框架自动路由

Prompt Master 内置多个提示框架，根据任务类型自动选择：

| 框架 | 最佳场景 |
|------|---------|
| **RTF** (Role, Task, Format) | 快速一次性任务 |
| **CO-STAR** (Context, Objective, Style, Tone, Audience, Response) | 专业文档、报告、商务写作 |
| **RISEN** (Role, Instructions, Steps, End Goal, Narrowing) | 复杂多步骤项目 |
| **CRISPE** (Capacity, Role, Insight, Statement, Personality, Experiment) | 创意工作、品牌调性 |
| **Chain of Thought** | 数学、逻辑、调试、多步骤分析 |
| **Few-Shot** | 一致性结构化输出、模式复制 |
| **File-Scope Template** | Cursor/Windsurf/Copilot — 任何代码编辑 AI |
| **ReAct + Stop Conditions** | Claude Code/Devin/AutoGPT — 自主 Agent |
| **Visual Descriptor** | Midjourney/DALL-E/Stable Diffusion/Sora |
| **Reference Image Editing** | 编辑已有图片，自动检测编辑 vs 生成 |
| **ComfyUI** | 基于节点的图像工作流 |
| **Prompt Decompiler** | 拆解、适配、简化、分割已有提示 |

框架选择是**静默的**——你永远看不到框架名，只看到提示词。

### 价值 4：Token 效率审计

Prompt Master 在输出前执行 Token 审计：**移除每一个不影响输出的词。** 不以长短论英雄，以"每个词都对结果有贡献"为标准。

输出带有一个简洁的策略说明，例如：
```
🎯 Target: Midjourney · ⚡ Framework: Visual Descriptor · 💰 Tokens: Light (~60) · 💡 Strategy: Comma-separated descriptors over prose, lighting and mood anchored early...
```

### 价值 5：记忆块系统（Memory Block）

**会话间记忆断层**是大型项目中最大的浪费源。Prompt Master 会从对话历史中提取之前的决策，生成 **Memory Block** 附加到新提示前：

```markdown
## Memory (Carry Forward from Previous Context)
- Stack: React 18 + TypeScript + Supabase
- Auth uses JWT stored in httpOnly cookies, not localStorage
- Component naming convention: PascalCase, no default exports
- Design system: Tailwind only, no custom CSS files
- Architecture: no Redux, context API only
```

> "这是长会话中最大的修复项。大多数浪费的 re-prompt 都来自 AI 忘记你已经决定的事情。"

### 价值 6：安全技术限定

Prompt Master **只使用**效果可靠且边界可控的技术：

| ✅ 使用 | ❌ 排除 |
|---------|---------|
| Role Assignment（角色分配） | Tree of Thought（思维树） |
| Few-Shot Examples（少样本示例） | Graph of Thought（思维图） |
| XML Structural Tags（XML 结构标签） | Universal Self-Consistency |
| Grounding Anchors（锚定接地） | Prompt Chaining（提示链） |
| Chain of Thought（思维链） | |

排除的技术因为**已知会产生幻觉或不可预测输出**。

---

## 结构化处理管线

每次请求，Prompt Master 执行以下管线（完全静默）：

```
用户输入（自然语言）
    ↓
① 工具检测
   检测目标 AI 工具，静默路由到对应方案
    ↓
② 9 维度意图提取
   任务 / 输入 / 输出 / 约束 / 上下文 / 受众 / 记忆 / 成功标准 / 示例
    ↓
③ 针对性追问（最多 3 个）
   只在关键信息缺失时问，绝不超 3 个
    ↓
④ 框架自动路由
   选择并应用正确的提示架构（用户不可见）
    ↓
⑤ 应用安全技术
   角色分配 / Few-Shot / XML 结构 / 锚定 / CoT（按需）
    ↓
⑥ Token 效率审计
   移除所有不影响输出的词
    ↓
⑦ 交付提示
   一个干净的可复制块 + 一行策略说明
```

---

## 针对各工具的专属优化

### 推理型 LLM（Claude / ChatGPT / Gemini / DeepSeek）

- **Claude：** 移除 padding，添加 XML 结构，指定长度
- **ChatGPT / GPT-5.x：** 输出契约（Output Contract），冗长度控制，完成标准
- **Gemini 2.x：** 接地锚定（Grounding Anchors），引用规则，格式锁定
- **DeepSeek-R1 / o1/o3：** **仅短而干净的指令** — 绝对不添加 CoT（它们内部已集成思维过程），添加 CoT 反而会**降低**输出质量
- **MiniMax：** Temperature 钳制，思考标签控制，结构化输出优化

### IDE 型 AI（Cursor / Windsurf / Copilot）

- 必须包含**文件路径 + 函数名 + 勿动清单**
- Cursor 需要顺序化提示引导
- Copilot 需要精确的函数签名为 docstring

### Agent 型 AI（Claude Code / Devin / Manus）

- 需要**停止条件**（Stop Conditions）— Agent 知道什么时候该停
- 需要**起始状态 + 目标状态** — 明确从哪开始、到哪结束
- 需要**文件范围锁定** — 只编辑哪些文件
- 需要检查点（checkpoint output）— 每步后输出进度

### 图像 AI（Midjourney / DALL-E / SD）

| 工具 | 提示风格 | 额外元素 |
|------|---------|---------|
| **Midjourney** | 逗号分隔描述符 | `--ar 16:9 --v 6 --style raw` + negative prompt |
| **DALL-E 3** | 散文式描述 | 自动检测编辑 vs 生成，排除文字（text exclusion） |
| **Stable Diffusion** | 权重语法 `(word:1.3)` | CFG guidance，必须的 negative prompt |
| **ComfyUI** | 正/负面节点拆分 | Checkpoint 特定语法 |

### 视频 AI（Sora / Runway / Dream Machine）

- 需要指定**镜头运动**（camera movement）
- 需要**时长**（duration）
- 需要**剪辑风格**（cut style）
- 需要**画面风格参考**（style reference）

---

## 35 个常见提示错误与一键修复

Prompt Master 内置了 30+ 个"浪费模式"的检测和修复策略：

### 任务表达类

| # | 错误模式 | 典型写法 → Prompt Master 修复 |
|---|---------|------------------------------|
| 1 | 模糊动词 | "帮我写代码" → "重构 `getUserData()` 为 async/await 并处理 null 返回" |
| 2 | 一个提示塞两个任务 | "解释并重写这个函数" → 拆为两个提示 |
| 3 | 无成功标准 | "让它更好" → "Done when 函数通过现有单元测试并处理 null 输入" |
| 4 | Agent 权限过大 | "随便做" → 明确允许/禁止的操作列表 |
| 5 | 情绪化描述 | "全坏了，修好一切" → "第 43 行当 user 为 null 时抛出未捕获 TypeError" |
| 6 | 一次性建全部 | "建整个应用" → 拆为 Prompt 1（脚手架）+ Prompt 2（功能）+ Prompt 3（打磨） |
| 7 | 隐式引用 | "加上我们讨论的那个东西" → 总是完整重述任务 |

### 上下文类

| # | 错误模式 | 修复 |
|---|---------|------|
| 8 | 假设已共享知识 | "继续我们停下的地方" → 附带 Memory Block |
| 9 | 无项目背景 | "写一封求职信" → "B2B 金融科技 PM 岗，2 年 SWE 经验..." |
| 10 | 前后矛盾 | 新提示与之前的技术选型冲突 → 必须包含 Memory Block |
| 11 | 邀请幻觉 | "专家对 X 怎么说？" → "只引用你确信的来源，不确定就说不知道" |
| 12 | 未定义受众 | "给用户写点东西" → "非技术 B2B 买家，无编程知识，决策者级别" |
| 13 | 不提之前失败 | 空白 → "我已经尝试过 X，但因为 Y 失败了。不要再提 X。" |

### 输出格式类

| # | 错误模式 | 修复 |
|---|---------|------|
| 14 | 缺少输出格式 | "解释这个概念" → "3 个要点，每个不超过 20 词，开头一句摘要" |
| 15 | 隐式长度 | "写摘要" → "写出恰好 3 句话的摘要" |
| 16 | 未分配角色 | 空白 → "你是一位资深后端工程师，专攻 Node.js 和 PostgreSQL" |
| 17 | 模糊审美形容词 | "让它看起来专业" → "单色调色板，16px 基准字体，24px 行高，无装饰元素" |
| 18 | 图像无负面提示 | "女人肖像" → 添加 "无水印、无模糊、无多余手指、无失真、无文字" |
| 19 | Midjourney 用散文 | 完整描述句 → "subject, style, mood, lighting, --ar 16:9 --v 6" |

### Agent 控制类

| # | 错误模式 | 修复 |
|---|---------|------|
| 20 | 无范围边界 | "修我的 App" → "只修 `src/auth.js` 中的登录表单验证，不动任何其他文件" |
| 21 | 无技术栈约束 | "建一个 React 组件" → "React 18, TypeScript strict, 无外部库, Tailwind only" |
| 22 | 无停止条件 | "建完整功能" → 显式停止条件 + 每步后检查点 |
| 23 | 无文件路径 | "更新登录函数" → "只更新 `src/pages/Login.tsx` 中的 `handleLogin()`" |
| 24 | 工具模板错误 | Cursor 里用 GPT 风格的散文提示 → 改为 File-Scope Template |
| 25 | 粘贴整个代码库 | 每次提示都带上完整仓库 → 只带相关函数和文件 |

### 思维模式类

| # | 错误模式 | 修复 |
|---|---------|------|
| 26 | 逻辑任务缺 CoT | "哪个方法更好？" → "一步步思考两种方法后再推荐" |
| 27 | 给 o1/o3 加 CoT | "一步步思考"发给 o1 → 移除，思考型模型内部已思考，加 CoT 会降低输出质量 |
| 28 | 复杂输出无自检 | 空白 → "完成前，对照上述约束验证输出" |
| 29 | 跨会话记忆 | "你已知我的项目" → 总是重新提供 Memory Block |
| 30 | 前后决策矛盾 | 新提示忽略之前架构 → Memory Block 包含所有已有事实 |

### Agent 安全类

| # | 错误模式 | 修复 |
|---|---------|------|
| 31 | 无起始状态 | "建一个 REST API" → "空 Node.js 项目，Express 已安装，`src/app.js` 存在" |
| 32 | 无目标状态 | "添加认证" → "`src/middleware/auth.js` 含 JWT 验证。`POST /login` 和 `POST /register`" |
| 33 | 静默 Agent | 无进度输出 → "每步后输出：✅ [已完成内容]" |
| 34 | 文件系统无锁 | 无文件限制 → "只编辑 `src/` 内的文件。不碰 package.json、.env、任何配置文件" |
| 35 | 无人审核触发点 | Agent 决定一切 → "删文件前、加依赖前、改数据库 schema 前，停下问我" |

---

## 安装与使用

### 方式 1：手动加载（最简单）
```bash
# 下载仓库 ZIP
# 打开 claude.ai → 侧边栏 → Customize → Skills → Upload a Skill
# 选择解压后的文件夹
```

### 方式 2：Claude Code 加载
```bash
mkdir -p ~/.claude/skills
git clone https://github.com/nidhinjs/prompt-master.git ~/.claude/skills/prompt-master
```

### 使用示例

自然语言调用（最推荐）：
```
帮我写给 Cursor 的提示词，我要重构 auth 模块
给我一个 Claude Code 的提示词来建一个 REST API——问你需要知道什么
这是我给 GPT-4o 写的烂提示，帮我修： [粘贴提示]
生成一个赛博朋克城市的 Midjourney 提示词
我有一张参考图片——帮我写个提示词，只改头部角度
```

显式调用：
```
/prompt-master
我想让 Claude Code 用 React + Supabase 建一个 todo App
```

---

## 实际输出对比

### 示例 1：Midjourney 提示

**用户输入：**
> 写一个 realistic samurai standing in the rain at night 的 Midjourney 提示

**Prompt Master 输出：**
```
lone samurai standing in heavy rain at night, traditional armor,
neon reflections on wet cobblestone street, cinematic lighting,
dramatic shadows, fog, ultra detailed, photorealistic,
shallow depth of field --ar 16:9 --v 6 --style raw

negative: blurry, low quality, watermark, cartoon, anime, extra limbs

🎯 Target: Midjourney · ⚡ Framework: Visual Descriptor · 💰 Tokens: Light (~60) · 💡 Strategy: Comma-separated descriptors over prose, lighting and mood anchored early, aspect ratio and version locked, negative prompt prevents style drift.
```

### 示例 2：Claude Code 提示

**用户输入：**
> 写一个 Claude Code 提示词，为一个业务仪表盘建一个 landing page，样式和感觉像 Notion——平滑动画、干净 UI

**Prompt Master 输出：**
一个 380 token 的完整提示词，包含：
- 详细的设计规格（精确的 hex 颜色值、字体、间距、阴影）
- 8 个部分的构建顺序
- 5 种动画的具体实现方式（IntersectionObserver、stagger、过渡）
- 约束条件
- Done When 标准

> 💡 **Strategy：** 每一个模糊的 Notion 审美线索都被翻译成了精确的 hex 值和像素规格——Claude Code 不会猜错。动画用精确的计时、方法和触发器定义，不需要任何解释。

---

## 版本历史

| 版本 | 内容 |
|------|------|
| **1.6.0** | Opus 4.7 更新。新增 Template M (Opus 4.7 Task Brief)。更新 Claude 和 Claude Code 路由。新增 pattern 36-37 |
| **1.5.0** | 新增 Agentic AI 和 3D 模型路由。修复 description。Token 估算从输出中移除。新增指令层和文案占位符 |
| **1.4.0** | 新增参考图片编辑检测、ComfyUI 支持、Prompt Decompiler 模式。修复 Claude Code 中的触发描述。3 个新模板 |
| **1.3.0** | 围绕 PAC2026 位置结构 (30/55/15) 重建。静默路由取代用户可见框架选择。引入 references 文件夹 |
| **1.2.0** | 针对注意力架构重构。移除易产生幻觉的技术 (ToT, GoT, USC, prompt chaining)。模板与 pattern 移入 references |
| **1.1.0** | 扩展工具覆盖，新增记忆块系统，35 个浪费模式修复 |
| **1.0.0** | 初始发布 |

---

## 工作手册：日常使用流程

### 流程 1：新任务 — 从想法到精准提示

```
① 说清楚"我要做什么"
   → "写一个 Cursor 提示，建一个 React 表单组件，带验证"
    ↓
② Prompt Master 会追问（最多 3 个）关键缺失信息
   → "技术栈？文件路径？验证规则？"
    ↓
③ 回答追问
    ↓
④ Prompt Master 输出：
   - 一个可直接粘贴使用的精准提示
   - 一行策略说明（目标工具、框架、Token 数、策略）
```

### 流程 2：修复已有烂提示

```
① 粘贴你的烂提示
   → "这是我给 ChatGPT 的提示，但输出总是太长且不相关..."
    ↓
② Prompt Master 自动检测问题：
   - 检测目标工具
   - 分析犯了哪些"浪费模式"
   - 应用对应的修复
    ↓
③ 输出优化后的提示 + 修复了什么
```

### 流程 3：跨工具转换

```
① 你有一个 Claude 提示，想转为 Midjourney 使用
   → "把这个 prompt 拆解并适配为 Stable Diffusion 能用的格式"
    ↓
② Prompt Master 会：
   - 使用 Prompt Decompiler 分析原提示结构
   - 提取关键信息
   - 按目标工具格式重新组装
```

### 流程 4：长会话记忆管理

```
① 工作一段时间后开始新任务
   → "继续我们的项目，加一个新的 API 端点"
    ↓
② Prompt Master 自动：
   - 从历史中提取之前决策
   - 生成 Memory Block
   - 附加到新提示前
    ↓
③ 新提示不会和之前决策矛盾
```

---

## 关键原则总结

| 原则 | 含义 |
|------|------|
| **每个词都承重** | 移除不改变输出的所有填充词 |
| **工具感知** | 不同工具有不同的"语言"，自动适配 |
| **静默路由** | 用户只需要描述目标，框架选择在幕后自动完成 |
| **安全技术优先** | 只使用边界可控的技术，排除已知产生幻觉的方法 |
| **记忆保持** | 最长会话中最大的修复：永不遗忘之前的决策 |
| **少即多** | 最多 3 个追问，短而干净的指令优于长而模糊的提示 |
| **一次命中** | 目标是第一次尝试就得到正确输出，零浪费 |

## 相关资源

- [GitHub 仓库](https://github.com/nidhinjs/prompt-master)
- [Open Source Projects 文章](https://www.opensourceprojects.dev/post/9e6f74f2-0e48-4422-ab1d-27e7c6558a46)
- [安装命令](https://skills.sh/)（Skills.sh 平台）
- MIT 协议开源
