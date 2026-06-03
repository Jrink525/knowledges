# AI Coding 基础设施全景：Chromium vs Warp
## 从两个标杆项目中提炼可实践的 AI Coding 体系搭建方法

> **来源**：[腾讯程序员《深入解析 Chromium 的 AI Coding 开发体系》](https://mp.weixin.qq.com/s/sCmRKJjTpdB4k3145OzZMg) + Warp 团队公开分享（OpenAI 案例研究、X/Twitter、官方博客、开源仓库）
>
> **整理日期**：2026-06-01
>
> **目标读者**：想为自己的团队/项目搭建 AI Coding 基础设施的工程师和工程管理者

---

## 目录

- [1. 开场：AI Coding 基础设施到底是什么](#1-开场ai-coding-基础设施到底是什么)
- [2. Chromium 完整实践指南](#2-chromium-完整实践指南)
  - [2.1 整体架构速览](#21-整体架构速览)
  - [2.2 AI Policy：先立规矩](#22-ai-policy先立规矩)
  - [2.3 四层 Prompt 体系：从零搭建](#23-四层-prompt-体系从零搭建)
  - [2.4 8 步工作流详解：每步做什么、为什么](#24-8-步工作流详解每步做什么为什么)
  - [2.5 Skills 系统：把复杂任务编码为可复用的 SKILL.md](#25-skills-系统把复杂任务编码为可复用的-skillmd)
  - [2.6 Knowledge Base：Agentic RAG 三层实践](#26-knowledge-baseagentic-rag-三层实践)
  - [2.7 Eval：给 AI Agent 写单元测试](#27-eval给-ai-agent-写单元测试)
  - [2.8 Projects：大规模自动化代码改造](#28-projects大规模自动化代码改造)
  - [2.9 完整案例推演：实现页面分屏](#29-完整案例推演实现页面分屏)
- [3. Warp 完整实践指南](#3-warp-完整实践指南)
  - [3.1 核心哲学：Open Agentic Development](#31-核心哲学open-agentic-development)
  - [3.2 Warp 的产品能力图谱](#32-warp-的产品能力图谱)
  - [3.3 Oz 编排平台：Agent 控制面](#33-oz-编排平台agent-控制面)
  - [3.4 Agent-First 开源协作模式](#34-agent-first-开源协作模式)
  - [3.5 多 Agent 协同工作流](#35-多-agent-协同工作流)
  - [3.6 代码库索引与上下文管理](#36-代码库索引与上下文管理)
  - [3.7 GPT-5.5 使用策略](#37-gpt-55-使用策略)
  - [3.8 Warp 基础架构与自建参考](#38-warp-基础架构与自建参考)
- [4. 核心对比与交叉启示](#4-核心对比与交叉启示)
- [5. 行动框架：给你的团队落地 AI Coding](#5-行动框架给你的团队落地-ai-coding)
  - [5.1 第一阶段：打好基础（1-2 周）](#51-第一阶段打好基础1-2-周)
  - [5.2 第二阶段：构建基础设施（1-2 个月）](#52-第二阶段构建基础设施1-2-个月)
  - [5.3 第三阶段：规模化（3-6 个月）](#53-第三阶段规模化3-6-个月)
  - [5.4 避坑指南](#54-避坑指南)
- [6. 附录](#6-附录)
  - [6.1 Chromium agents/ 目录文件清单与用途](#61-chromium-agents-目录文件清单与用途)
  - [6.2 Warp 仓库关键入口点](#62-warp-仓库关键入口点)
  - [6.3 可复用的模板和脚本](#63-可复用的模板和脚本)

---

## 1. 开场：AI Coding 基础设施到底是什么

AI Coding 基础设施不是"装个 Copilot 插件"或"买个 Claude Pro"。它是**让 AI 在你的代码库里稳定、可控、高效地产出代码的一整套系统**。

Chromium 和 Warp 代表了两种不同的答案：

| | Chromium 路线 | Warp 路线 |
|---|---|---|
| **核心理念** | 用严格的流程和规则约束 AI 行为 | 用编排平台管理 Agent 集群 |
| **适用场景** | 大型遗留代码库、质量敏感型项目 | 快速迭代的开源/闭源产品开发 |
| **关键挑战** | 文档积累、流程遵守 | 编排可靠性、Agent 协调 |
| **可复用的核心资产** | Policy + Prompt 分层 + Eval | Oz 编排 + Agent-First 协作流程 |

**本文的目标**：不是告诉你"Chromium 和 Warp 多厉害"，而是把它们的每个模块拆解成**你可以照着做的步骤**。

---

## 2. Chromium 完整实践指南

### 2.1 整体架构速览

Chromium 的 AI Coding 体系集中在 `src/agents/` 目录下：

```
chromium/src/agents/
├── ai_policy.md                 # AI 使用政策（底线约束）
├── prompts/                     # 提示词系统（四层分层组合）
│   ├── common.minimal.md        # 第一层：核心指令（所有开发者共享）
│   ├── common.md                # 第二层：8 步标准工作流
│   ├── knowledge_base.md        # RAG 知识库路由表
│   ├── templates/               # 第三层：平台模板
│   │   ├── desktop.md
│   │   ├── android.md
│   │   └── ios.md
│   └── eval/                    # 评估测试用例（15+ 场景）
├── skills/                      # 技能系统（18+ 专业模块）
│   ├── feature-flag-removal/
│   ├── fuzzing/
│   ├── histograms/
│   ├── chromium-docs/
│   └── ...
├── extensions/                  # MCP 扩展
├── projects/                    # AI 驱动的大型项目
│   ├── bedrock/modularize-chrome-browser/
│   ├── code-health/
│   └── modernization/
└── testing/                     # Prompt 评估测试框架
    ├── eval_prompts.py
    ├── gemini_provider.py
    ├── workers.py
    └── asserts/
```

**核心机制之间的关系**：

```
          ┌─────────────────────────┐
          │      AI Policy          │  ← 所有机制的底线约束
          │  (人类始终是最终责任人)    │
          └──────────┬──────────────┘
                     │
          ┌──────────▼──────────────┐
          │        Prompts          │  ← 定义"怎么做"（工作流引擎）
          │  (四层分层组合架构)       │
          └────┬───────────┬────────┘
               │           │
     ┌─────────▼─┐   ┌─────▼────────┐
     │ Knowledge │   │    Skills    │
     │ (知识增强)  │   │  (专业模块)   │
     │ 告诉 AI   │   │  告诉 AI     │
     │"去哪找信息"│   │"如何做特定任务"│
     └───────────┘   └──────┬───────┘
                            │
          ┌─────────────────▼──────────────┐
          │            Eval                │  ← 保证迭代不退化
          │  (AI Agent 的回归测试套件)        │
          └────────────────────────────────┘
```

---

### 2.2 AI Policy：先立规矩

**文件**：`agents/ai_policy.md`

**核心原则**：AI 是辅助工具，人类开发者始终是最终责任人。

#### 2.2.1 完整规则表

| 规则 | 详细要求 | 违规后果 | 实践要点 |
|------|---------|---------|---------|
| **自审义务** | 作者必须在发送 Review 前自行审查并理解所有代码，确保正确性、设计、安全性和风格达标 | 提交不理解代码 → 剥夺 Committer 权限 → 再犯封禁账号 | 这条是最关键的。不要为了速度跳过这一步 |
| **原创声明** | 无论是否使用 AI，作者必须声明代码为自己的原创作品 | — | 法律层面，AI 生成的代码版权归操作者 |
| **人类回复人类** | Agent 创建的任务收到人类反馈，必须由人类操作者亲自回复 | 违反项目行为准则 | Agent 不应扮演"人类"的角色在 Review 中回复 |
| **推荐：CL 标注** | 在 CL 描述中说明 AI 工具的使用方式和 Prompt | — | 方便回溯；团队可以总结经验优化 Prompt |
| **推荐：提交设计文档** | 如果是通过设计文档 + Prompt 驱动的代码，将设计文档一并提交 | — | 设计文档本身就是最好的上下文 |

#### 2.2.2 在你的项目中抄作业

创建一个 `AI_POLICY.md` 放到项目根目录（或 `.github/`）：

```markdown
# AI Coding Policy

## 基本原则
- AI 是辅助工具，不是作者。所有代码的作者是提交者本人。
- 提交者必须理解每一行代码的含义、作用和影响。
- AI 生成的代码质量由提交者负全责。

## 强制规则
1. 自审义务：PR/CL 发出前，必须完整审查所有 AI 生成的代码
2. 原创声明：所有提交的代码，无论是否使用 AI，均声明为作者原创
3. 人类回复：Agent 收到 Review 意见，必须由人类亲自回复
4. 禁止绕过：不得使用 AI 自动批准 Review 或合并 PR

## 推荐做法
- 在 PR 描述中标注 AI 工具和 Prompt（可附在正文中）
- 重要的架构设计文档一并提交到代码库
- 定期回顾 AI 生成代码的 Review 意见，总结经验
```

---

### 2.3 四层 Prompt 体系：从零搭建

#### 2.3.1 整体设计思路

```
┌─────────────────────────────────────────────────────┐
│                   第四层：Task Prompts                │
│                   一次性任务命令                       │
│        /cr:gerrit/cl-description                    │
├─────────────────────────────────────────────────────┤
│                   第三层：Templates                   │
│                   平台模板                           │
│         desktop.md / android.md / ios.md             │
├─────────────────────────────────────────────────────┤
│                   第二层：common.md                   │
│                   8 步标准工作流 + 知识库引用            │
├─────────────────────────────────────────────────────┤
│                   第一层：common.minimal.md            │
│                   核心指令（构建/测试/编码/预提交规范）    │
└─────────────────────────────────────────────────────┘
```

**关键设计原则**：
- **分层**：每层只管自己的事，上层引用下层
- **组合**：开发者按需组合，而不是一个巨大的单体 Prompt
- **可维护**：.tmpl.md（带注释的源文件） → process_prompts.py → .md（最终文件）

#### 2.3.2 第一层：common.minimal.md — 核心指令（所有开发者共享）

**作用**：定义 AI 在你项目中的"基本守则"，无论做什么任务都生效。

**Chromium 原文的 5 个规范领域**：

| 领域 | 规则 | 为什么 |
|------|------|--------|
| **构建** | 必须先确认构建目录和目标，未确认前禁止构建 | AI 猜错构建目录的代价太大（浪费时间+产生错误） |
| **测试** | 使用 `tools/autotest.py` 而不是手动调用 `autoninja`（autotest 会自动构建） | 避免重复构建 |
| **编码** | Stay on task：不修无关的 TODO 和 code health；注释只写"为什么"不写"做了什么" | AI 有"顺手修 TODO"和"写废话注释"的倾向 |
| **JNI** | 定义 Java↔C++ 的 JNI 方法识别规则 | 即使非 Android 开发者也可能遇到 |
| **预提交** | 完成后运行 `git cl format` + `git cl presubmit`，只修自己改动引入的问题 | 避免 AI 修复不相关的预存警告 |

**模板（可复用）**：

```markdown
# common.minimal.md — 项目 AI Coding 核心指令

## 构建
- 开始任何构建前，先确认输出目录和构建目标
- 未确认前禁止执行构建命令
- 优先使用项目的构建脚本（如 `./build.sh`），而非手动调用构建工具

## 测试
- 使用项目统一的测试运行器
- 不要跳过测试步骤

## 编码规范
- Stay on task：只做需求要求的事情
- 不要顺手修复不相关的 TODO、code health 或风格问题
- 注释只写"为什么这么做"，不写"做了什么"（代码本身已经说明了后者）
- 不要添加调试日志或 print 语句

## 预提交
- 完成后运行：`<项目格式化命令>` + `<项目预提交检查命令>`
- 只修自己改动引入的问题，不修复预存的 lint 警告
```

#### 2.3.3 第二层：common.md — 8 步标准工作流（核心）

**这是 Chromium AI Coding 最重要的设计**。所有代码编辑任务都必须遵循这 8 步。

详见 [2.4 节](#24-8-步工作流详解每步做什么为什么)。

**在你的项目中：**

```markdown
# common.md — 标准代码编辑工作流

@agents/prompts/common.minimal.md

<!-- 知识库路由表 -->
@agents/prompts/knowledge_base.md

## 工作流

你必须严格按照以下 8 步流程执行所有代码编辑任务。

[Step 1-8 的具体内容，见下一节]
```

#### 2.3.4 第三层：Templates — 平台模板

**作用**：为不同平台/子项目的开发者提供特定上下文。

**Chromium 的 desktop.md 模板样例**：

```markdown
Before starting any tasks, you MUST read the following files:

- //docs/chrome_browser_design_principles.md
- //docs/ui/views/overview.md

Build Targets:
- chrome                 - 桌面 Chrome 主二进制
- unit_tests             - 单元测试
- browser_tests          - 集成测试
- interactive_ui_tests   - 需要独占窗口管理器的 UI 交互测试
```

**在你的项目中**：

如果你的项目有多个子模块（前端/后端/移动端），为每个模块创建一个模板：

```markdown
# backend.md — 后端模块模板

Before starting any tasks, you MUST read:

- docs/ARCHITECTURE.md
- docs/DATABASE_SCHEMA.md
- docs/API_CONVENTIONS.md

Build Targets:
- server                 - 主服务二进制
- server_tests           - 测试套件
- migration_tool         - 数据库迁移工具
```

#### 2.3.5 第四层：Task Prompts — 快捷命令

**作用**：封装高频操作的标准 Prompt，一键调用。

**Chromium 预定义的命令**：

| 命令 | 功能 | 核心逻辑 |
|------|------|----------|
| `/cr:gerrit/fix-review-comments` | 自动修复 Review 意见 | 获取未解决评论 → 逐条判断是否有信心修复 → 修复或标记 |
| `/cr:test/gen-gtests` | 自动生成单元测试 | 分析 git diff → 定位测试文件 → 读取现有 fixture → 生成用例 → 验证 |
| `/cr:gerrit/cl-description` | 自动生成 CL 描述 | 分析 diff → 按 Chromium 规范生成标题/正文/Bug/Test 标签 |
| `/cr:git/pre-upload-checklist` | 一键预提交检查 | 同步依赖 → 风格检查 → 移除调试日志 → 格式化 → presubmit |
| `/cr:test/disable-test` | 禁用失败的测试 | 定位测试 → 添加 DISABLED_ 前缀 → 更新 BUILD.gn |

**你的项目的 Task Prompts 框架**：

在你的项目中创建一个 `.gemini/commands/` 或 `.claude/commands/` 目录：

```markdown
# commands/fix-review-comments.md

## 重置 Review 意见
1. 获取当前 PR/CL 的所有未解决评论
2. 逐条判断：
   - 如果有信心修复：理解评论意图后修改代码
   - 如果没信心：在评论下方回复"请给出具体修改建议"并解释原因
3. 修复完成后，逐条标记为已解决
4. 如果修改涉及文件变更，重新运行测试
```

#### 2.3.6 Prompt 维护机制

Chromium 的做法（可直接复用）：

```
源文件：common.tmpl.md       # 包含 HTML 注释形式的设计意图说明
         │
         ▼  process_prompts.py 脚本自动去除注释
         │
最终文件：common.md          # 无注释的最终版本
         │
         ▼  PRESUBMIT 检查 .md 是否与 .tmpl.md 同步
```

**设计意图注释示例**：

```markdown
<!-- common.tmpl.md -->
<!-- 设计意图：所有开发者共享的最底层指令，定义 AI 在项目中工作的基本规范 -->
<!-- 为什么在 Step 1 之前不构建：AI 猜错构建目录的代价太大，强制先确认 -->
```

**你的项目的维护脚本**（Python，可直接用）：

```python
# process_prompts.py
import re, os

def process_tmpl(tmpl_path, md_path):
    """去除 HTML 注释，生成最终 .md 文件"""
    with open(tmpl_path, 'r') as f:
        content = f.read()
    # 移除 HTML 注释
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    # 清理多余空行
    content = re.sub(r'\n{3,}', '\n\n', content)
    with open(md_path, 'w') as f:
        f.write(content)
    print(f"Generated {md_path} from {tmpl_path}")

# 遍历 agents/prompts/ 下所有 .tmpl.md 文件
for root, dirs, files in os.walk('agents/prompts/'):
    for f in files:
        if f.endswith('.tmpl.md'):
            tmpl_path = os.path.join(root, f)
            md_path = tmpl_path.replace('.tmpl.md', '.md')
            process_tmpl(tmpl_path, md_path)
```

---

### 2.4 8 步工作流详解：每步做什么、为什么

这是 Chromium AI Coding **最核心的可复用资产**。每个步骤都有明确的输入、动作、输出和检查点。

#### Step 1：深度理解代码（强制第一步，不可跳过）

> **为什么不可跳过**：AI 最常见的错误是"读了个函数名就开始写代码"。Chromium 发现，充分的上下文理解是保证代码质量的关键，也是减少幻觉的核心手段。

```
输入：用户的任务描述
输出：向开发者确认理解的陈述

执行步骤：
├── 1a. 定位核心文件
│   ├── 找出任务涉及的所有文件
│   └── 包括：头文件、实现文件、测试文件、配置文件
│
├── 1b. 完整审计
│   ├── 读取每个相关文件的完整源码（不跳过任何部分）
│   ├── 总结控制流（函数的调用链）
│   ├── 总结所有权语义（谁持有什么、生命周期是怎样的）
│   └── 标注关键设计决策
│
├── 1c. 陈述理解（向开发者确认）
│   ├── 用自然语言总结理解
│   ├── 列出准备修改的文件和修改方式
│   └── **等待开发者确认后再继续**
│
└── 1d. 反模式规避
    ├── 绝不从函数名猜测行为 — 必须读源码实现
    ├── 必须检查至少一个调用点来理解函数用法
    └── 绝不假设未读过的文件的结构
```

**检查清单（AI 自检）**：
- [ ] 我是否读了所有相关文件？
- [ ] 我是否向开发者确认了理解？
- [ ] 我是否检查了至少一个调用点？

#### Step 2：编写代码

```
输入：开发者确认的理解
输出：修改后的代码

规则：
└── 只做需求要求的事
    ├── 不添加未要求的额外功能
    ├── 不顺手重构不相关的代码
    └── 不添加调试代码
```

#### Step 3：编写/更新测试

```
输入：修改后的代码
输出：测试代码

优先级：
├── 优先向已有测试文件添加用例（避免创建过多新文件）
└── 没有合适的已有文件则创建新测试文件

要求：
├── 新功能必须有对应的新测试
├── 修改的行为必须在已有测试中体现变更（必要时追加断言）
└── 测试应覆盖：正常路径、边界条件、错误路径
```

#### Step 4：构建

```
输入：代码 + 测试
输出：编译结果

规则：
├── 使用项目的标准构建命令
├── 明确指定构建目标和输出目录
└── 记录编译错误（如果有）
```

#### Step 5：修复编译错误

```
输入：编译错误列表
输出：修复后的代码

流程：
├── 为每个编译错误至少读取一个新文件（找到问题的根因）
├── 找到并理解所有相关文件
├── 检查历史对话中是否出现过相同错误（避免重复问）
└── 绝不做投机性修复（必须理解错误原因再修）
```

**AI 自检**：
- [ ] 我是否为每个编译错误读了新文件？
- [ ] 我是否理解了错误的根因，而不仅仅是修了表面症状？

#### Step 6：运行测试

```
输入：编译通过的代码
输出：测试结果

要求：
├── 运行所有相关测试（不仅仅是新增的）
└── 记录测试失败（如果有）
```

#### Step 7：修复测试错误

```
输入：测试失败列表
输出：通过测试的代码

要求：
├── 先理解测试失败的原因，再修改代码
├── 如果测试自身有问题（不合理的断言），先和开发者确认再修改
└── 不为了通过测试而绕过断言
```

#### Step 8：迭代（循环 Step 4-7 直到全部通过）

```
条件：
├── 编译通过
├── 所有测试通过
└── 开发者确认结果
```

---

### 2.5 Skills 系统：把复杂任务编码为可复用的 SKILL.md

**与 Prompts 的区别**：
- **Prompts**：始终加载的通用指令（所有对话都有）
- **Skills**：按需激活 — 只有当用户的请求与某个 Skill 相关时，AI 才自动加载对应的 `SKILL.md`

#### 2.5.1 Chromium 的 18+ Skills 列表

| Skill | 功能 | 复杂度 | 适合迁移到你的项目吗？ |
|-------|------|--------|----------------------|
| `feature-flag-removal` | 移除 Feature Flag（17 步 checklist） | 高 | ✅ 适合有 Feature Flag 的项目 |
| `fuzzing` | 编写 Fuzz 测试 | 中 | ⚠️ 需要 fuzz 基础设施 |
| `histograms` | 管理 UMA 指标 | 中 | ✅ 适合有埋点/监控的项目 |
| `cl-description` | 生成 CL 描述 | 低 | ✅ 极适合 |
| `git-cl-helper` | Git CL 操作辅助 | 低 | ✅ 极适合 |
| `chromium-docs` | 文档搜索 | 中 | ✅ 适合有大量文档的项目 |
| `network-traffic-annotations` | 网络流量注解 | 中 | ⚠️ 需要网络层 |
| `nullaway` | NullAway 空指针检查 | 低 | ✅ 适合 Java/Kotlin 项目 |
| `policy-creation` | 企业策略创建 | 高 | ⚠️ 需要策略系统 |
| `webui-lit-migration` | WebUI Lit 迁移 | 高 | ⚠️ 特殊场景 |
| `trace-analysis` | 性能 Trace 分析 | 中 | ✅ 适合需要性能分析的项目 |
| `utr` | 通用测试运行器 | 中 | ✅ 极适合 |

#### 2.5.2 Skill 文件的结构（可复用模板）

```markdown
# SKILL.md — <技能名称>

## 描述
<!-- 一句话说明这个 Skill 解决什么问题 -->

## 触发条件
<!-- AI 在检测到什么模式时应自动加载此 Skill -->
当用户请求涉及以下内容时，自动加载本 SKILL.md：
- <关键词1>
- <关键词2>

## 前置条件
<!-- 执行前必须满足的条件 -->
- [ ] 必要的文件存在
- [ ] 必要的环境变量设置
- [ ] ...

## 执行步骤

### Step N: <步骤名称>
详细描述每一步做什么。

### 验证
- [ ] 验证点 1
- [ ] 验证点 2

## 示例
### 示例 1: ...
输入描述和预期输出。

## 常见错误
- 错误 1：问题描述 → 解法

## 参考
- 相关文档链接
```

#### 2.5.3 实操例子：`feature-flag-removal` Skill 的 17 步 checklist（精简版）

```markdown
# SKILL.md — feature-flag-removal

## 触发条件
当用户提到"移除 Feature Flag"、"清理 Flag"、"删除 feature flag"时激活。

## 执行步骤

Step 1: 确认 Feature Flag 名称和作用域
Step 2: 搜索代码中所有引用
Step 3: 检查 Flag 是否在 about:flags 中注册
Step 4: 移除 about_flags.cc 中的注册
Step 5: 移除 flag_descriptions.h 和 .cc 中的描述
Step 6: 更新 flag-metadata.json
Step 7: 检查 enums.xml 中的枚举值
Step 8: 搜索所有 #if BUILDFLAG(FLAG_NAME) 并替换逻辑
Step 9: 决定保留哪个分支（enabled 还是 disabled 状态）
Step 10: 移除旧分支代码
Step 11: 确认所有引用已清理
Step 12: 清理 BUILD.gn 中的依赖
Step 13: 运行相关测试
Step 14: 移除测试中的 flag 引用
Step 15: 编译检查
Step 16: 代码 Review
Step 17: 提交
```

#### 2.5.4 在你的项目中应该先写哪几个 Skill

**优先级排序**（从最能立即见效的开始）：

1. **`git-pr-helper`** — PR 操作自动化
2. **`cl-description`** — PR 描述自动生成
3. **`code-review-checklist`** — Review 时 AI 自动检查清单
4. **`test-generator`** — 测试生成
5. **`migration-checklist`** — 代码迁移/重构步骤

---

### 2.6 Knowledge Base：Agentic RAG 三层实践

Chromium 的知识库不是传统向量检索，而是一套**让 AI 自主判断该读什么文档**的 Agentic RAG。

核心哲学在 `knowledge_base.md` 开头：

```
## Core Principle: Consult, then Answer

You MUST NOT answer from your general knowledge alone.
Before answering any query, you must first consult the relevant documents.
```

#### 2.6.1 三层架构详解

```
┌──────────────────────────────────────────────────────┐
│  第三层：MCP 扩展 — 外部知识源                          │
│  · blink-spec（GitHub API 查 W3C/CSS 规范）            │
│  · build-information（当前构建配置）                     │
│  · depot-tools（工具命令帮助）                          │
├──────────────────────────────────────────────────────┤
│  第二层：chromium-docs Skill — 本地文档检索工具              │
│  · Python 脚本在 2000+ md 文件索引中搜索                  │
│  · 按标题/路径/关键词/内容权重打分                        │
│  · 毫秒级响应                                          │
├──────────────────────────────────────────────────────┤
│  第一层：knowledge_base.md — 静态路由表                  │
│  · 任务关键词 → 文档路径的 if-then 规则引擎               │
│  · 被引用在 common.md 末尾，始终在 AI 上下文中             │
│  · 覆盖常见任务模式                                     │
└──────────────────────────────────────────────────────┘
```

#### 2.6.2 第一层：knowledge_base.md 静态路由表（最重要）

**工作原理**：`knowledge_base.md` 被引用在 `common.md` 末尾，因此始终在 AI 的上下文里。它本质上是"当遇到 X 情况时，去读 Y 文档"的规则引擎。

**Chromium 的路由规则分类**：

```
# ========== 核心编程模式路由 ==========

## IPC (进程间通信)
browser-to-renderer → 找对应 .mojom 文件，理解 Mojo IPC 接口

## 异步/线程
异步操作或线程相关 → 读取 docs/threading_and_tasks.md

## 回调
base::OnceCallback 等 → 读取 docs/callback.md

## Blink 代码
third_party/blink/renderer/ 下的代码 →
  - 必须使用 WTF 容器（blink::Vector, blink::String）
  - 必须使用 Oilpan GC（Member<>, Persistent<>）
  - 禁止使用 STL 容器

# ========== 功能开发路由 ==========

## 用户偏好
pref / PrefService → components/prefs/README.md

## UMA 指标
histograms → docs/metrics/uma/README.md

## UKM 指标
ukm → tools/metrics/ukm/README.md

## 构建文件
BUILD.gn → docs/imported/gn/style_guide.md

# ========== 调试路由（最精细） ==========

## "header file not found"
1. 验证 deps 在 BUILD.gn 中
2. 验证 #include 路径
3. 重新生成构建文件: gn gen <out_dir>
4. 确认 GN 可以看到依赖: gn desc <out_dir> //failing:target deps
5. 检查是否有问题: gn check <out_dir> //failing:target

## Linker error ("undefined symbol")
→ 检查 deps (gn desc) 和 is_component_build

## Visibility error
→ 将依赖目标加到 visibility 列表
```

**路由表执行示例**：
当开发者说"帮我在 Blink 中添加一个 CSS 属性并追踪 UMA 指标"时：
1. AI 分析任务关键词
2. 检测到"Blink" → 路由触发：必须用 WTF 容器 + Oilpan GC → AI 读取 Blink C++ Style Guide
3. 检测到"UMA 指标" → 路由触发 → AI 读取 docs/metrics/uma/README.md
4. AI 基于读取的权威文档生成实现方案

#### 2.6.3 第二层：chromium-docs Skill（本地文档搜索）

当静态路由不够时，AI 激活 `chromium-docs` skill 进行动态搜索。

**搜索流程**：

```
AI 判断需要查文档
    ↓
调用 `python chromium_docs.py "mojo ipc"`
    ↓
Python 脚本在本地 JSON 索引中做字符串匹配 + 关键词匹配
    ↓
按权重排序，返回文档路径列表
    ↓
AI 拿到路径后，自己去读取这些文档文件
```

**索引设计（三索引架构，可直接复用）**：

| 索引文件 | 结构 | 用途 | 优势 |
|---------|------|------|------|
| `doc_index.json` | `{"path": {title, summary, content, keywords, category, mtime}}` | 主索引，存储完整元信息 | 提供文档详细信息用于打分 |
| `keyword_index.json` | `{"keyword": ["path1", "path2"]}` | 关键词倒排索引 | O(1) 定位，速度快 1000+ 倍 |
| `category_index.json` | `{"category": ["path1", "path2"]}` | 分类索引 | O(1) 获取分类文档 |

**搜索打分权重**：
- 标题匹配：×4.0
- 路径匹配：×2.5
- 关键词匹配：×2.0
- 内容匹配：×1.0-1.5（长度越长权重越高）
- 近期修改：小幅加分

**实践：给你的项目实现一个 chromium_docs.py**：

```python
#!/usr/bin/env python3
"""
chromium_docs.py — 本地文档检索工具
复用了 Chromium 的设计：三索引架构 + 字符串匹配权重打分
"""
import json, os, glob, sys, time
from pathlib import Path

DOCS_INDEX_DIR = ".docs_index"
INDEX_FILE = os.path.join(DOCS_INDEX_DIR, "doc_index.json")
KEYWORD_FILE = os.path.join(DOCS_INDEX_DIR, "keyword_index.json")
CATEGORY_FILE = os.path.join(DOCS_INDEX_DIR, "category_index.json")

EXCLUDED_DIRS = {"node_modules", "venv", "__pycache__", ".git", "build", "dist"}

def _is_text_file(path):
    """简单判断是否为文本文件"""
    text_exts = {'.md', '.rst', '.txt', '.py', '.js', '.ts', '.java', '.go', '.rs'}
    return os.path.splitext(path)[1].lower() in text_exts

def _extract_title(content):
    """提取文档标题（第一个 H1 或 H2）"""
    for line in content.split('\n'):
        if line.startswith('# '):
            return line[2:].strip()
    for line in content.split('\n'):
        if line.startswith('## '):
            return line[3:].strip()
    return ""

def _extract_keywords(content, max_keywords=20):
    """提取关键词（你的项目专有术语）"""
    # 根据你的项目调整
    terms = {"api", "database", "config", "deploy", "migration",
             "ci/cd", "monitoring", "auth", "middleware", "cache"}
    found = []
    content_lower = content.lower()
    for term in terms:
        if term in content_lower:
            found.append(term)
    return found[:max_keywords]

def build_index(docs_path="docs/"):
    """扫描文档目录，构建三个索引文件"""
    os.makedirs(DOCS_INDEX_DIR, exist_ok=True)
    doc_index = {}
    keyword_index = {}
    category_index = {}

    for root, dirs, files in os.walk(docs_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for f in files:
            if f.endswith('.md'):
                path = os.path.join(root, f)
                rel_path = os.path.relpath(path, docs_path)
                with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                    content = fh.read()

                title = _extract_title(content)
                summary = content[:300]
                keywords = _extract_keywords(content)
                category = os.path.dirname(rel_path).split('/')[0] or "general"
                mtime = os.path.getmtime(path)

                doc_index[rel_path] = {
                    "title": title,
                    "summary": summary,
                    "content": content,
                    "keywords": keywords,
                    "category": category,
                    "mtime": mtime
                }

                # 更新 keyword_index
                for kw in keywords:
                    if kw not in keyword_index:
                        keyword_index[kw] = []
                    keyword_index[kw].append(rel_path)

                # 更新 category_index
                if category not in category_index:
                    category_index[category] = []
                category_index[category].append(rel_path)

    with open(INDEX_FILE, 'w') as f:
        json.dump(doc_index, f)
    with open(KEYWORD_FILE, 'w') as f:
        json.dump(keyword_index, f)
    with open(CATEGORY_FILE, 'w') as f:
        json.dump(category_index, f)
    print(f"Built index: {len(doc_index)} documents, "
          f"{len(keyword_index)} keywords, "
          f"{len(category_index)} categories")

def search(query, top_k=5):
    """在索引中搜索文档，返回按权重排序的路径列表"""
    if not os.path.exists(INDEX_FILE):
        print("Index not found. Run 'python chromium_docs.py --build-index' first.")
        return []

    with open(INDEX_FILE, 'r') as f:
        doc_index = json.load(f)

    query_lower = query.lower()
    results = []

    for path, meta in doc_index.items():
        score = 0.0
        content_lower = meta.get("content", "").lower()

        # 标题匹配（权重 ×4.0）
        if query_lower in meta.get("title", "").lower():
            score += 4.0

        # 路径匹配（权重 ×2.5）
        if query_lower in path.lower():
            score += 2.5

        # 关键词匹配（权重 ×2.0）
        for kw in meta.get("keywords", []):
            if query_lower in kw:
                score += 2.0

        # 内容匹配（权重 ×1.0-1.5）
        count = content_lower.count(query_lower)
        if count > 0:
            score += min(1.5, 1.0 + count * 0.1)

        if score > 0:
            results.append((path, score, meta.get("title", "")))

    results.sort(key=lambda x: -x[1])
    return [{"path": r[0], "score": r[1], "title": r[2]} for r in results[:top_k]]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--build-index":
        build_index()
    elif len(sys.argv) > 1:
        results = search(" ".join(sys.argv[1:]))
        for r in results:
            print(f"  [{r['score']:.1f}] {r['title']} → {r['path']}")
    else:
        print("Usage:")
        print("  python chromium_docs.py --build-index")
        print("  python chromium_docs.py <query>")
```

#### 2.6.4 第三层：MCP 扩展（外部知识源）

对于需要实时外部信息的场景：
- **外部 API 规范** → MCP 工具抓取
- **构建配置信息** → MCP 工具查询
- **第三方库文档** → MCP 工具获取

MCP 的实现超出了本文范围，但概念上就是给 AI 一组"可以调用的外部工具"。

#### 2.6.5 传统 RAG vs Chromium Agentic RAG

| 维度 | 传统 RAG | Chromium 的 Agentic RAG |
|------|----------|------------------------|
| **检索方式** | 用户 query → 向量检索 → 返回 chunks | AI 自主判断 → 按规则读取文件 → 按需搜索 |
| **知识来源** | 预构建的向量数据库 | 源码树中的原始文档（实时读取） |
| **路由机制** | 纯语义相似度 | 静态规则表 + 动态搜索 + MCP 外部查询 |
| **更新方式** | 需要重新 embedding | 文档随代码同步更新，索引按需重建 |
| **核心理念** | **被动检索**（开发者提问） | **AI 主动查阅**（"Consult, then Answer"） |

**为什么 Agentic RAG 更适合 Coding**：
- 代码文档的特点是"精确"比"相似"更重要
- 向量检索可能返回"语义相近但完全不对"的文档
- 静态路由表可以精确控制 AI 在什么情况下去读什么文档
- 开发者对文档的路径有预期，字符串匹配更可靠

#### 2.6.6 给你的项目建立 knowledge_base.md

```markdown
## Core Principle: Consult, then Answer
You MUST NOT answer from your general knowledge alone.
Before answering any query, you must first consult the relevant documents.

## 核心编程模式路由

### 涉数据库操作
→ 读取 docs/DATABASE_SCHEMA.md
→ 读取 docs/QUERY_CONVENTIONS.md

### 涉 API 设计
→ 读取 docs/API_DESIGN.md
→ 读取对应服务的 README.md

### 涉配置
→ 读取 docs/CONFIGURATION.md

## 调试路由

### 500 错误
1. 检查应用日志
2. 检查最近代码变更
3. 确认数据库连接状态

### 测试失败
1. 确认测试环境配置
2. 查看测试输出中的错误堆栈
3. 检查依赖的服务是否可用
```

---

### 2.7 Eval：给 AI Agent 写单元测试

**核心思想**：AI Agent 也需要回归测试。当你修改了 Prompt（如 `common.md`），你怎么知道 AI 的行为没有退化？答案就是 Eval。

#### 2.7.1 Chromium 的 15+ 评估用例

```
eval/
├── adapt_builder/              # 构建配置
├── add_browser_test_coverage/  # 测试生成（浏览器测试）
├── add_gtest_coverage/         # 测试生成（单元测试）
├── class_refactor/             # 重构
├── fix_broken_test/            # 修复测试
├── fuzzing/                    # Fuzz 测试
├── cl-description/             # CL 描述生成
├── feature_flags_add/          # 添加 Feature Flag
├── find_function/              # 代码搜索（函数）
├── search_class/               # 代码搜索（类）
├── build_file/                 # 构建（文件）
├── build_target/               # 构建（目标）
└── ...
```

#### 2.7.2 一个 Eval 用例的结构

每个用例由两个核心文件组成：

```
fix_broken_test/
├── prompt.md              # 模拟用户输入的任务指令
└── eval.promptfoo.yaml    # 自动化断言配置
```

**prompt.md**（模拟用户输入）：

```markdown
I have a broken test called "DummyTest" in
third_party/blink/renderer/core/css/css_math_expression_node_test.cc.
Can you compile and run the test to figure out why it is failing,
then attempt to fix it?
```

**eval.promptfoo.yaml**（自动化断言）：

```yaml
tests:
  - assert:
      # 检查是否修改了正确的文件
      - type: python
        value: check_files_changed
        config:
          files:
            - services/network/public/cpp/schemeful_site_mojom_traits_unittest.cc

      # 检查文件内容：必须包含 FUZZ_TEST，不能包含旧式 API
      - type: python
        value: check_file_content
        config:
          files:
            - path: '...unittest.cc'
              present: ['FUZZ_TEST', 'SchemefulSite']
              absent: ['LLVMFuzzerTestOneInput']

      # 检查是否调用了正确的构建命令
      - type: python
        value: check_tool_used_with_args_match
        config:
          tool_names: [run_shell_command]
          args_regexes: ['autoninja', 'out/fuzz']
```

#### 2.7.3 测试框架核心组件

| 组件 | 文件 | 职责 |
|------|------|------|
| **主入口** | `eval_prompts.py` | 一键发现、过滤、调度、执行所有评估用例 |
| **Provider** | `gemini_provider.py` | 驱动 Gemini CLI（写入 GEMINI.md → 设置 system prompt → stdin 传入 user prompt → 流式捕获输出） |
| **执行引擎** | `workers.py` | 并行执行，每个 Worker 创建独立 WorkDir |
| **断言脚本** | `asserts/` | `check_changes.py`（检查文件变更）、`check_tool_calls.py`（检查工具调用）等 |

**关键设计**：

| 设计 | 说明 |
|------|------|
| **隔离执行** | 每个测试在独立 WorkDir 中运行（btrfs 快照或 gclient-new-workdir），互不干扰 |
| **Pass@K 机制** | 一个用例运行 N 次，K 次通过即成功。适应 LLM 输出的非确定性 |
| **CI 集成** | 支持 Swarming 分片并行、Docker 沙箱隔离、ResultDB 上报、Skia Perf 性能看板 |
| **Telemetry 采集** | 从 CLI 输出的 OpenTelemetry 中提取 token 用量和工具调用记录 |

#### 2.7.4 在你的项目中建一个简化版 Eval

**目录结构**：

```
evals/
├── run_evals.py              # 执行器
├── assert_helpers.py         # 断言工具
└── cases/
    ├── gen_pr_description/   # PR 描述生成
    │   ├── prompt.md
    │   └── assertions.json
    └── fix_broken_test/      # 修复测试
        ├── prompt.md
        └── assertions.json
```

**断言 JSON 结构**：

```json
{
  "checks": [
    {
      "type": "files_changed",
      "params": {
        "files": ["src/server/handler.go"]
      }
    },
    {
      "type": "content_checks",
      "params": {
        "file": "src/server/handler.go",
        "present": ["error handling", "log"],
        "absent": ["fmt.Println"]
      }
    }
  ]
}
```

**简化执行器**：

```python
#!/usr/bin/env python3
"""run_evals.py — 简化版 Eval 执行器"""
import json, os, sys, subprocess

EVALS_DIR = "evals/cases"

def run_eval(eval_name):
    """运行单个 Eval 用例"""
    prompt_file = os.path.join(EVALS_DIR, eval_name, "prompt.md")
    assert_file = os.path.join(EVALS_DIR, eval_name, "assertions.json")

    if not os.path.exists(prompt_file):
        return {"name": eval_name, "status": "SKIP", "reason": "no prompt.md"}

    # 1. 读取 prompt
    with open(prompt_file) as f:
        prompt = f.read()

    # 2. 用 AI CLI 执行
    print(f"  Running: {eval_name}")
    print(f"  Prompt: {prompt[:100]}...")

    # 实际调用 AI CLI 的逻辑在这里
    # result = subprocess.run(["claude", "-p", prompt], capture_output=True, text=True)

    # 3. 执行断言
    if os.path.exists(assert_file):
        with open(assert_file) as f:
            assertions = json.load(f)
        # 执行断言检查...
        print(f"  Checks: {len(assertions.get('checks', []))}")

    return {"name": eval_name, "status": "PASS"}

def main():
    eval_dirs = [d for d in os.listdir(EVALS_DIR)
                 if os.path.isdir(os.path.join(EVALS_DIR, d))]
    print(f"Found {len(eval_dirs)} eval cases")
    results = []
    for d in sorted(eval_dirs):
        results.append(run_eval(d))
    passed = sum(1 for r in results if r["status"] == "PASS")
    print(f"\nResults: {passed}/{len(results)} passed")

if __name__ == "__main__":
    main()
```

---

### 2.8 Projects：大规模自动化代码改造

**Skills vs Projects 的定位差异**：

| 维度 | Skills | Projects |
|------|--------|----------|
| **粒度** | 单个任务（如"移除一个 Feature Flag"） | 大规模工程项目（如"模块化整个 chrome/browser"） |
| **自动化程度** | AI 辅助，人类确认 | 高度自动化，含发现脚本、验证流水线、自动提交 |
| **复杂度** | 一个 SKILL.md | 完整项目结构（SKILL.md + 参考文档 + Python 脚本 + 测试） |

#### 2.8.1 Chromium 的 3 个 Projects

**Project 1：modularize-chrome-browser**
- 目标：将 `chrome/browser/` 的巨型单体构建目标拆分为独立模块
- 6 阶段流程：
  1. 盘点文件
  2. 选择构建模式
  3. 生成 BUILD.gn
  4. 更新父级 BUILD
  5. 修复 include 错误
  6. 验证提交
- SKILL.md 长达 **344 行**

**Project 2：code-health**
- 目标：代码健康自动化治理
- Hub 调度中心 + 子任务
- AI 自动：发现候选项 → 置信度评估 → 创建分支 → 修改代码 → 验证 → 提交到 Gerrit

**Project 3：modernization**
- 目标：代码现代化自动修复
- Python 框架 AutoFixer
- 流程：错误信息喂给 Gemini → 自动修复 → 验证 → 重试（最多 3 轮）→ 通过/失败报告

#### 2.8.2 Projects 的目录结构（可复用模板）

```
projects/<project-name>/
├── README.md           # 项目说明
├── SKILL.md           # 执行步骤
├── discovery.py       # 发现候选修改点的脚本
├── fixer.py           # 自动修复脚本
├── verifier.py        # 验证修复正确性的脚本
├── submitter.py       # 自动创建 PR/CL 的脚本
└── tests/             # 测试
    └── test_fixer.py
```

---

### 2.9 完整案例推演：实现页面分屏

下面以"在桌面版 Chrome 中实现同一窗口左右并排显示两个 Tab"为例，完整展示 Prompts、Skills、Knowledge 如何协同工作。

> ⚠️ **重要**：以下是从实际提交记录逆向推演的流程。实际操作中，直接将产品需求输入 AI，AI 并不能自主完成这样的拆解。**人类工程师必须在前面做需求拆解**。

#### 2.9.1 人类先拆解（这一步 AI 做不了）

原始需求 → 拆解为 **6 个 CL**（ChangeList，约等于 PR）：

| CL | 内容 | 涉及机制 |
|----|------|---------|
| CL 1 | 添加 Feature Flag（kSplitView） | Prompts + Skills |
| CL 2 | 修改窗口布局模型（BrowserView 支持双 ContentsWebView） | Knowledge 深度参与 |
| CL 3 | 实现分屏控制器（SplitViewController） | Knowledge 深度参与 |
| CL 4 | 添加 UI 入口（Tab 右键菜单 + 工具栏按钮） | Prompts |
| CL 5 | 添加 UMA 指标追踪 | Skills 主导 |
| CL 6 | 编写 Browser Tests | Prompts |

#### 2.9.2 CL 1：添加 Feature Flag — Prompts + Skills 协同

**开发者对 AI 说：**

> 帮我添加一个 feature flag 叫 kSplitView，放在 //chrome/browser 组件下，默认 DISABLED_BY_DEFAULT，需要暴露到 about:flags。

**AI 的响应流程：**

1. **Prompts 层面**：`common.md` 的 8 步工作流启动
   - Step 1：AI 理解代码（定位相关文件、审计源码、向开发者确认）
2. **Knowledge 层面**：`knowledge_base.md` 中没有 Feature Flag 的直接路由规则
   - 但 `eval/feature_flags_add/` 目录下有预定义的评估用例可供参考
3. **Skills 层面**：虽然没有"添加 Feature Flag"的 Skill，但 `feature-flag-removal` Skill 可以反向参考
4. **AI 确定需要修改的文件**：
   - `chrome/browser/about_flags.cc`
   - `chrome/browser/flag_descriptions.h` / `.cc`
   - `chrome/browser/flag-metadata.json`
   - `tools/metrics/histograms/enums.xml`

#### 2.9.3 CL 3：实现分屏控制器 — Knowledge 深度参与

**开发者给 AI 技术描述后，三层知识增强机制同时工作：**

**第一层（knowledge_base.md 静态路由）：**

| AI 检测到的特征 | 触发的路由 | AI 的动作 |
|---------------|-----------|-----------|
| 代码在 `chrome/browser/ui/views/` | `desktop.md` 模板 | 读取 `docs/ui/views/overview.md` 和 `docs/chrome_browser_design_principles.md` |
| 需要修改 BUILD.gn | `knowledge_base.md` 规则 | 读取 `docs/imported/gn/style_guide.md` |

**第二层（chromium-docs 本地检索工具）：**

如果 AI 需要了解 BrowserView 的布局机制但静态路由没有覆盖：

```
# AI 调用
python chromium_docs.py "BrowserView layout ContentsWebView"

# 脚本返回
- chrome/browser/ui/views/frame/README.md
- docs/ui/views/overview.md

# AI 自行读取这些文档
```

**第三层（Prompts 工作流执行）：**

```
AI 按 8 步工作流：
1. 读取 browser_view.h、contents_web_view.h、tab_strip_model.h 的完整源码
2. 向开发者陈述理解并确认
3. 编写 split_view_controller.h/.cc
4. 修改 browser_view.h/.cc 和 BUILD.gn
5. 构建
6. 修复编译错误
7. 运行测试
8. 修复测试错误
9. 迭代直到全部通过
```

#### 2.9.4 CL 5：添加 UMA 指标 — Skills 主导

**开发者对 AI 说：**

> 给分屏功能添加 UMA 指标追踪。

**AI 的响应流程：**

1. **Skills 层面**：`histograms` Skill 自动激活，指导 AI：
   ```
   1. 确定指标名称（如 SplitView.Activated）
   2. 定位元数据目录（tools/metrics/histograms/metadata/split_view/）
   3. 更新 histograms.xml（添加 <histogram> 条目）
   4. 更新 enums.xml（定义枚举值）
   5. 设置过期时间（3 个月后）
   6. 添加至少两个 owner
   ```

2. **Knowledge 层面**：`knowledge_base.md` 检测到"UMA"关键词，路由到 `docs/metrics/uma/README.md`

#### 2.9.5 提交阶段 — Task Prompts 加速

```
# 一键预提交检查
/cr:git/pre-upload-checklist

# 自动生成 CL 描述
/cr:gerrit/cl-description

# 自动修复 Review 意见
/cr:gerrit/fix-review-comments
```

#### 2.9.6 三大机制的协同关系图

```
           ┌─────────────┐
           │  开发者需求   │
           └──────┬──────┘
                  │
           ┌──────▼──────┐
           │   Prompts    │  ← 定义"怎么做"（8 步工作流）
           │  (工作流引擎) │
           └──────┬──────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
   ┌──▼─────┐ ┌──▼───┐ ┌──────▼──────┐
   │Knowledge│ │Skills│ │   Task      │
   │(知识增强)│ │(专业 │ │  Prompts    │
   │         │ │ 技能)│ │  (快捷命令)   │
   │告诉 AI  │ │告诉  │ │             │
   │"去哪找  │ │AI    │ │  加速关键    │
   │ 信息"   │ │"如何 │ │  环节执行    │
   │         │ │做特定│ │             │
   │         │ │任务" │ │             │
   └─────────┘ └──────┘ └─────────────┘
```

---

## 3. Warp 完整实践指南

### 3.1 核心哲学：Open Agentic Development

Warp 提出了一个范式转变：

> **传统模式：** 人类写代码 → AI 辅助
> **Open Agentic Development：** 人类定义目标 + 监督产出 → Agent 写代码、测试、开 PR

**CEO Zach Lloyd 的原话：**
> "We think we can ship a better Warp, more quickly, by working with our community to supervise a fleet of agents."

**对开发者的影响：**
- 你不再需要从零写代码，而是需要：写 spec → 验证 Agent 产出 → 决策
- 你在代码审查中的角色从"审查代码实现"变为"审查是否满足 spec"
- 你的决策和判断成为 Agent 可复用的上下文

### 3.2 Warp 的产品能力图谱

```
Warp (Agentic Development Environment)
├── 内置 Coding Agent
│   ├── AI Command Generation (自然语言→CLI 命令)
│   ├── 代码生成与修改
│   ├── 错误诊断与修复
│   └── 上下文感知（代码库索引）
│
├── BYO CLI Agent 支持
│   ├── Claude Code
│   ├── Codex (OpenAI)
│   ├── Gemini CLI
│   ├── OpenCode
│   └── 其他
│
├── 协作能力
│   ├── Warp Drive（云同步工作流/Prompts/环境配置）
│   ├── Session Sharing（实时协同终端）
│   ├── 多模型切换（OpenAI / Kimi / MiniMax / Qwen）
│   └── 团队 Agent 可见性
│
├── 开发者体验
│   ├── Block-based 输出（命令分组显示）
│   ├── 命令补全与历史
│   ├── IDE 化的终端体验
│   └── GPU 加速 UI（Rust + 自研 WarpUI 框架）
│
└── Oz 编排平台（核心差异化能力）
    ├── Agent 控制面
    ├── 本地/云端统一编排
    ├── 持久内存与上下文管理
    ├── 子 Agent 委派
    └── 可观测性
```

### 3.3 Oz 编排平台：Agent 控制面

**Oz** 是 Warp 构建的 Agent 编排控制平面。它解决的核心问题是：**当 Agent 需要长时间、多步骤工作时，怎么协调、怎么看着、怎么切换？**

#### 3.3.1 Oz 的能力矩阵

| 能力 | 说明 | 实践中有什么用 |
|------|------|---------------|
| **跨环境部署** | Agent 可以在本地、云端或两者间切换运行 | 本地开发时快速迭代，云端跑时释放机器 |
| **Web 管理界面** | 选择预定义技能、环境、模型、宿主配置 | 不用记命令行参数，可视化启动 Agent |
| **远程持久运行** | Agent 远程持续运行，开发者可以随时查看状态 | 提交一个任务后去做别的事，回来查看结果 |
| **定时任务** | 支持类似 cron 的定期 Agent 工作流 | 每天凌晨自动跑代码健康检查 |
| **上下文紧缩** | 长时间运行后，Agent 的上下文不会膨胀到崩溃 | 避免"Agent 聊了 2 小时后忘了一开始的上下文" |
| **持久内存** | Agent 跨会话保持重要状态 | Agent 记住"这个项目用 Go 1.22"不需要重复问 |
| **子 Agent 委派** | 为代码搜索、文件分析等任务创建子 Agent | 主 Agent 专注于规划，子 Agent 独立执行具体任务 |
| **可观测性** | 实时查看 Agent session，审查产出，切换环境 | 发现 Agent 跑偏了可以及时干预 |

#### 3.3.2 Oz 的工作流程

```
1. 开发者定义任务（通过 Web UI 或 API）
2. 选择 skill、环境、模型
3. 启动 Agent
   ├── Agent 在云端或本地运行
   ├── 开发者可以查看实时状态
   ├── 可以切换运行环境（本地↔云端）
   └── 也可以离开让 Agent 继续跑
4. Agent 完成任务
   ├── 生成产出（代码、文档、PR）
   ├── 产出关联到原始任务
   └── 开发者审查、确认、修改
```

#### 3.3.3 关键技术的实现思路（如果你要自建）

**上下文紧缩（Context Compaction）：**
```
问题：Agent 在长对话中，对话历史越来越长，token 成本越来越高，对模型的理解力造成影响。
解法：定期对历史对话做摘要，用摘要替换历史，只保留最近的 N 轮完整对话。
实现：每 M 条消息或每 N tokens 执行一次。
```

**持久内存（Persistent Memory）：**
```
问题：Agent 每次启动对项目一无所知。
解法：用文件或数据库存储 Agent 学到的关键信息。
实现：
  - 项目的配置、约定、架构 → agents/memory.md
  - Agent 自己的经验 → agents/experience.md
  - 跨会话状态 → JSON 文件持久化
```

---

### 3.4 Agent-First 开源协作模式

**这是 Warp 在开源领域的最大创新。**

#### 3.4.1 传统开源 vs Warp Agent-First

| 阶段 | 传统开源 | Warp Agent-First |
|------|---------|-----------------|
| **找事做** | 扫 issue 列表找适合自己的 | 扫 issue 列表看哪些是 `ready-to-implement` |
| **理解需求** | 读 issue 描述，在评论中问问题 | issue 已经有 spec，Agent 直接可以执行 |
| **写代码** | 自己写实现 | Agent 写实现（@oss-maintainers 即可） |
| **提 PR** | 提交 PR，等审查 | Agent 提交 PR，附上执行日志 |
| **Review** | 人类审查代码 | 人类审查 spec 满足度 + Agent 行为 |
| **合并** | 人类合并 | 人类合并 |

#### 3.4.2 完整的 Issue → PR 流程

```mermaid
1. 贡献者发现或创建 issue
       │
2. 维护者审查 issue
       │
       ├── 设计不够清晰 → 标记 ready-to-spec
       │   └── 社区/Agent 写 spec 并在 issue 中确认
       │
       └── 设计已确认 → 标记 ready-to-implement
           │
3. 贡献者（或 Agent）认领
       │
4. 执行：
   ├── Agent 读 spec、读代码库
   ├── Agent 写实现
   ├── Agent 写/更新测试
   ├── Agent 运行测试
   └── Agent 创建 PR
       │
5. 人类维护者 Review
   ├── 审查 spec 是否满足
   ├── 审查代码质量
   └── 批准或要求修改
       │
6. 合并
```

#### 3.4.3 降低门槛的关键设计

- **不熟悉 Rust/Warp 代码库也能贡献**：只要你描述清楚需求和验证标准，Agent 负责实现
- **Agent 执行免费**：Warp 为开源贡献者提供 Oz 额度
- **结构化流程保证质量**：Agent 强制遵循项目规则、编码标准、测试策略
- **并行执行**：多个 Agent 可以同时处理不同的 issue，突破人类瓶颈

#### 3.4.4 在你的团队中实践 Agent-First

你不一定需要 Oz，可以用 Claude Code、Codex 或 Gemini CLI 实现类似流程：

```bash
# 在 ready-to-implement 的 issue 上执行：

# 1. Agent 读 spec 和代码库
claude -p "Read docs/SPEC.md and understand the requirements"

# 2. Agent 生成实现方案
claude -p "Draft implementation plan for issue #123"

# 3. 人类确认方案 → Agent 实现
claude -p "Implement the plan described above"

# 4. Agent 测试
claude -p "Write tests and run them"

# 5. Agent 创建 PR
claude -p "Create a PR with the changes"
```

---

### 3.5 多 Agent 协同工作流

Warp 的内部数据：**约 90% 的 PR 由 Agent 共同创建**。

#### 3.5.1 Warp 的多 Agent 模式

```
               ┌──────────────────┐
               │  Orchestrator    │
               │  (Oz 或主 Agent)  │
               └────────┬─────────┘
                        │
          ┌─────────────┼─────────────┐
          │             │             │
    ┌─────▼────┐  ┌────▼─────┐  ┌────▼────┐
    │  Code    │  │  Test    │  │  Code   │
    │  Agent 1 │  │  Agent   │  │  Review │
    └──────────┘  └──────────┘  │  Agent  │
                                └─────────┘
```

**每种 Agent 的职责**：

| Agent 类型 | 职责 | 输入 | 输出 |
|-----------|------|------|------|
| **Orchestrator** | 接收任务、拆分子任务、协调执行、汇总结果 | 用户需求 | 汇总结果报告 |
| **Code Agent** | 写实现代码、搜索代码库 | spec | 代码 diff |
| **Test Agent** | 生成/更新测试、运行测试 | 代码 diff | 测试结果 |
| **Code Review Agent** | Review 代码质量、风格、安全 | 代码 diff | Review 意见 |
| **Documentation Agent** | 更新文档、生成变更日志 | 代码 diff | 文档更新 PR |

#### 3.5.2 多 Agent 协同的挑战（Warp 的经验）

1. **上下文共享**：Agent A 做了什么，Agent B 需要知道
   - 解法：共享工作区 + 统一的状态文件
2. **冲突解决**：两个 Agent 可能同时修改同一个文件
   - 解法：细粒度任务拆分 + 文件级锁
3. **质量保障**：各 Agent 产出的一致性
   - 解法：统一的标准 + Review Agent 兜底
4. **错误传播**：Agent A 出错 → Agent B 基于错误继续
   - 解法：每个 Agent 输出的结果都做验证，验证不通过不回传

---

### 3.6 代码库索引与上下文管理

Warp 的一个重要能力：**索引 Git 仓库，让 Agent 生成上下文感知的响应**。

#### 3.6.1 索引的内容

- 代码结构（目录树、文件关系）
- 符号定义和引用（函数、类、变量）
- Git 历史（最近修改的文件、作者）
- 依赖关系（模块间的引用）

#### 3.6.2 在你的项目中实现类似功能

```bash
# 用 claude 或 Copilot 的代码索引功能
# 或者自己实现一个简化的索引脚本：

#!/bin/bash
# code-index.sh — 生成代码库的摘要信息供 Agent 使用

echo "# Project Structure"
find . -type f -name "*.go" -o -name "*.py" -o -name "*.js" | head -50

echo -e "\n# Recent Changes (last 30 days)"
git log --since="30 days ago" --oneline --shortstat

echo -e "\n# Key Files"
find . -type f \( -name "go.mod" -o -name "package.json" -o -name "Dockerfile" -o -name "Makefile" \)
```

---

### 3.7 GPT-5.5 使用策略

Warp 与 OpenAI 的合作提供了模型选择和使用的具体经验。

#### 3.7.1 多模型分层路由

```
任务到来
    │
    ├── 简单任务（格式化、简单重构、小函数生成）
    │   → 小模型（快速、便宜）
    │
    ├── 中等任务（测试生成、代码审查、中等复杂度功能）
    │   → 中等模型
    │
    └── 复杂任务（跨文件重构、大规模代码生成、架构设计）
        → GPT-5.5 级别（强推理、跨问题空间能力）
```

#### 3.7.2 GPT-5.5 的实测效果（Warp 内部数据）

| 指标 | GPT-5.4 | GPT-5.5 | 改进 |
|------|---------|---------|------|
| 每 Agentic Coding Task 的 Token 用量 | 基准 | 减少 30% | 更少的重复推理 |
| 长任务成功率 | 基准 | 显著提升 | 跨问题空间推理更强 |
| 代码合理性（内部评估） | 基准 | 更好 | 更好的架构直觉 |

**CEO 评价：**
> "OpenAI models regularly provide frontier-level intelligence while taking fewer tokens and turns to complete the same tasks."

#### 3.7.3 LLM-as-a-Judge 评估（可复用）

Warp 在评估 pipeline 中使用 OpenAI 模型作为"评判者"：

```python
# 流程
1. Agent 完成任务 → 产出代码
2. 将代码 + spec 提交给"Judge"模型
3. Judge 模型评估：
   a. 是否满足 spec
   b. 代码质量（可读性、性能、安全性）
   c. 是否有潜在问题
4. 根据 Judge 结果决定接受/修改/拒绝
```

---

### 3.8 Warp 基础架构与自建参考

#### 3.8.1 仓库结构

```
warpdotdev/warp/
├── app/                      # 主应用（终端仿真、Shell 管理、AI 集成）
├── crates/
│   ├── warp_core/           # 核心工具和平台抽象
│   ├── editor/              # 文本编辑功能
│   ├── warpui/              # 自研 UI 框架（MIT 许可）
│   ├── warpui_core/         # UI 框架核心
│   ├── ipc/                 # 进程间通信
│   └── graphql/             # GraphQL 客户端和 schema
├── .agents/skills/          # Agent 技能配置
├── .claude/                 # Claude 配置
├── .warp/                   # Warp 配置
├── scripts/                 # 构建脚本
└── specs/                   # 规范文档
```

#### 3.8.2 本地构建命令

```bash
# 初始化
./script/bootstrap

# 运行
./script/run
# 或
cargo run
cargo bundle --bin warp

# 测试
cargo nextest run --no-fail-fast --workspace --exclude command-signatures-v2

# 格式化 + lint
cargo fmt
cargo clippy --workspace --all-targets --all-features --tests -- -D warnings

# 预提交（必做）
./script/presubmit
```

#### 3.8.3 如果你要自建类似 Warp 的环境

**最小可行方案（不需要 Rust 和 GPU 加速 UI）：**

```
.project-root/
├── .agents/
│   ├── skills/              # 技能系统（参考 Chromium）
│   │   ├── pr-description/
│   │   ├── test-generation/
│   │   └── ...
│   ├── prompts/             # 分层 Prompts
│   │   ├── common.md
│   │   ├── knowledge_base.md
│   │   └── templates/
│   │       ├── backend.md
│   │       └── frontend.md
│   ├── memory/              # Agent 跨会话记忆
│   │   ├── project_context.md
│   │   └── decisions.md
│   └── config.yaml          # Agent 配置（模型、上下文长度等）
├── docs/                    # 文档（chromium-docs 索引目标）
│   ├── ARCHITECTURE.md
│   ├── DATABASE_SCHEMA.md
│   └── API_CONVENTIONS.md
├── evals/                   # Eval 用例
│   └── cases/
└── .github/
    └── commands/            # Task Prompts 快捷命令
```

---

## 4. 核心对比与交叉启示

### 4.1 设计哲学对比

| 维度 | Chromium | Warp |
|------|----------|------|
| **AI 的角色** | 辅助工具，永远不能替代人类判断 | Agent 是主力编码者，人类退到编排/监督层 |
| **安全策略** | 政策和流程约束（剥夺权限、封禁） | 技术约束（Oz 平台门槛、可观测性） |
| **对 Agent 产出的信任度** | 低 — 每行代码必须人类审查理解 | 高 — 约 90% PR 由 Agent 协同创建 |
| **人类核心价值** | 代码理解和责任 | 产品判断和愿景 |
| **Agent 的工作模式** | 单 Agent 对话式（一个 AI 从头到尾做） | 多 Agent 协作式（不同 Agent 分工） |
| **质量保障手段** | 8 步工作流强制 + Eval 回归测试 | Oz 平台约束 + LLM-as-a-Judge 评估 |
| **对文档的依赖** | 极高（11 年积累的文档体系） | 中等（代码库索引 + 上下文管理） |

### 4.2 Chromium → Warp 能学到的

| 建议 | 具体做法 |
|------|---------|
| **Prompt 分层设计** | Warp 可以用 Chromium 的四层架构来组织它的 Agent 指令，特别是"最小指令 + 工作流"的分层 |
| **Eval 回归测试** | Warp 的 LLM-as-a-Judge 可以结合 Chromium 的体系化 Eval，形成更完备的回归机制 |
| **知识库静态路由表** | 对于 Warp 自研的 Rust 库（WarpUI、编辑器等），建立类似路由表可以帮助 Agent 快速掌握 |
| **Policy 文化** | Warp 的 Agent-First 模式更需要清晰的安全护栏——Agent 在什么情况下不能做什么 |
| **Step 1 深度理解** | 任何 Agent 写代码前，都应该强制先读源码再确认——这适用于所有场景 |

### 4.3 Warp → Chromium 能学到的

| 建议 | 具体做法 |
|------|---------|
| **Agent 编排平台** | Chromium 目前只有 prompt 组合 + eval 保证质量，缺少统一编排控制面。一个轻量版 Oz 可以补齐 |
| **Agent-First 协作模式** | Chromium 的开源协作同样面临维护瓶颈，可以尝试 "issue → spec → Agent implement" 流程 |
| **跨模型灵活性** | Chromium 限定三款工具，Warp 的 BYO Agent 姿态更灵活，特别是开源社区可能有更多样需求 |
| **持久化 Agent 记忆** | Chromium 的每次 Agent 对话都是全新的——让 Agent 记忆项目的"常识"可以大幅减少重复沟通 |
| **可观测性** | 看到 Agent 的每一步操作和 Token 消耗，比"只看到结果"更可控 |

### 4.4 它们共同的认知

1. **Agent 需要结构和流程约束，不能依赖 AGI 级推理** — 再强的模型也需要规则
2. **可观测性必不可少** — 能看到 Agent 在干什么、用了多少 token、有没有跑偏
3. **文档是 Agent 能力的上限** — Agent 无法超越它所读到的文档质量。你的文档质量 = Agent 能交付的质量上限
4. **人类始终需要参与** — 不管是 Chromium 的"每行代码都审查"还是 Warp 的"定义目标 + 验证产出"
5. **这是长期投入** — Chromium 花了 11 年积累文档，Warp 的 Oz 也不是一天建成的

---

## 5. 行动框架：给你的团队落地 AI Coding

### 5.1 第一阶段：打好基础（1-2 周）

> **目标**：让 AI 在你的代码库中产生可用的代码，而不是胡言乱语。

**Day 1-2：创建 AI Policy**
- [ ] 写一份 AI_POLICY.md（复用 [2.2 节的模板](#222-在你的项目中抄作业)）
- [ ] 在团队中同步政策
- [ ] 在 PR 模板中增加一个 checkbox："我理解并审查了所有 AI 生成的代码"

**Day 3-5：建立分层 Prompt 体系**
- [ ] 创建 `agents/prompts/common.minimal.md`（核心指令）
- [ ] 创建 `agents/prompts/common.md`（8 步工作流）
- [ ] 为你的项目创建平台/模块模板（至少 1 个）
- [ ] 创建 `GEMINI.md` 或 `.claude/CLAUDE.md` 或 `.github/COPILOT_INSTRUCTIONS.md`，引用你的 Prompt

**Day 6-7：创建第一个 Skill**
- [ ] 选择一个高频、重复性高的任务（如"生成 PR 描述"）
- [ ] 编码为 SKILL.md（复用 [2.5 节的模板](#252-skill-文件的结构可复用模板)）
- [ ] 实测验证

**Day 8-10：建立 Knowledge Base**
- [ ] 创建 `agents/prompts/knowledge_base.md`（至少 5-10 条路由规则）
- [ ] 运行文档索引脚本（复用 [2.6.3 节的 chromium_docs.py](#263-第二层chromium-docs-skill本地文档搜索)）

**Day 11-14：建立 Eval 体系**
- [ ] 选择 3-5 个典型场景创建 Eval 用例（prompt.md + assertions）
- [ ] 写一个简化版执行器
- [ ] 在每次 Prompt 修改后运行 Eval

### 5.2 第二阶段：构建基础设施（1-2 个月）

> **目标**：让 AI 成为团队日常开发的可靠伙伴。

**Skills 系统扩容**
- [ ] 从 [2.5.4 节](#254-在你的项目中应该先写哪几个-skill)的优先级列表中选择 3-5 个 Skill 实现
- [ ] 建立 Skill 的版本管理和更新机制

**Knowledge Base 完善**
- [ ] 将 knowledge_base.md 的规则扩展到 20+ 条
- [ ] 每周从 Review 中总结新的路由规则
- [ ] 建立文档随代码更新的机制（可以触发在 CI 中文档索引重建）

**Eval 回归测试**
- [ ] 将 Eval 用例扩展到 10+
- [ ] 集成到 CI Pipeline（每次 Prompt 修改自动触发）
- [ ] 引入 Pass@K 机制

**Agent 记忆系统**
- [ ] 创建 `agents/memory/project_context.md`
- [ ] Agent 每次完成重要任务后，更新记忆文件
- [ ] 让新 Agent 每次启动先读记忆文件

### 5.3 第三阶段：规模化（3-6 个月）

> **目标**：开始探索 Agent-First 协作模式。

**多 Agent 协作**
- [ ] 尝试两个 Agent 分工（如 Code Agent + Review Agent）
- [ ] 实现简单的共享上下文机制
- [ ] 尝试长时间运行的 Agent 任务

**大规模自动化（Projects）**
- [ ] 识别一个适合自动化的长期工程治理目标
- [ ] 构建 discovery + fixer + verifier + submitter 流水线

**Agent-First 协作试点**
- [ ] 在非关键模块试行"写 spec → Agent 实现 → 人类验收"
- [ ] 积累流程经验
- [ ] 逐步扩展到更多模块

**Oz 轻量版（可选）**
- [ ] 实现 Agent 控制面：启动、停止、状态查看
- [ ] 实现远程执行：Agent 可以在云端运行
- [ ] 实现 Agent 调度：简单的任务队列

### 5.4 避坑指南

#### 坑 1：单体 Prompt — 一改全崩

**表现**：所有指令写在一个巨大的 Prompt 文件里，改一条规则可能导致整个行为异常。
**解法**：Chromium 的四层分层 + .tmpl.md / .md 分离。每层只管自己的事。

#### 坑 2：跳过上下文理解直接写代码

**表现**：AI 写了大量代码但完全不符合你的架构设计。
**解法**：强制 8 步工作流中的 Step 1。AI 必须先读相关源码，再向你确认理解，然后才能动手。

#### 坑 3：忽视文档建设

**表现**：AI 只能用通用知识回答，产出的代码没有项目特色。
**解法**：建立"Consult, then Answer"文化。没有文档的地方，Agent 就是盲人摸象。

#### 坑 4：没有回归测试

**表现**：改了 Prompt 后，有些场景的表现默默退化了一周才发现。
**解法**：Eval 是基础设施，不是可选项。15 个用例比 0 个好，5 个也比 0 个好。

#### 坑 5：AI 产出替代人类思考

**表现**：开发者不再理解自己提交的代码，Review 流于形式。
**解法**：Policy 明确 + 团队文化强调：提交者必须理解每一行代码。

#### 坑 6：期待一次投入终身受益

**表现**：花 2 周搭了基础设施，以为就完事了，3 个月后 Prompt 文档都过时了。
**解法**：AI Coding 基础设施是活的，需要持续维护。参考 Chromium 11 年的文档积累。

---

## 6. 附录

### 6.1 Chromium agents/ 目录文件清单与用途

| 路径 | 用途 | 对你的项目的参考价值 |
|------|------|---------------------|
| `agents/ai_policy.md` | AI 使用政策 | ⭐ 高 — 直接复用 |
| `agents/prompts/common.minimal.md` | 核心指令 | ⭐ 高 — 直接复用 |
| `agents/prompts/common.md` | 8 步工作流 | ⭐ 高 — 按项目调整 |
| `agents/prompts/knowledge_base.md` | 静态知识路由表 | ⭐ 高 — 需要项目定制 |
| `agents/prompts/templates/desktop.md` | 桌面平台模板 | ⭐ 中 — 为你的模块建模板 |
| `agents/prompts/templates/android.md` | Android 平台模板 | ⭐ 中 |
| `agents/prompts/templates/ios.md` | iOS 平台模板 | ⭐ 中 |
| `agents/prompts/eval/` (15 子目录) | 评估用例 | ⭐ 高 — 可参考用例设计 |
| `agents/skills/` (18+ skills) | 技能系统 | ⭐ 高 — 可参考 SKILL.md 设计 |
| `agents/extensions/` | MCP 扩展 | ⭐ 中 — 高级话题 |
| `agents/projects/` | 大规模项目 | ⭐ 高 — 参考 Projects 模型 |
| `agents/testing/eval_prompts.py` | Eval 执行器 | ⭐ 高 — 可重构 |
| `agents/testing/gemini_provider.py` | AI CLI 驱动 | ⭐ 高 — 需要适配你的工具 |
| `agents/testing/workers.py` | 并行执行引擎 | ⭐ 中 |
| `agents/testing/asserts/` | 断言工具 | ⭐ 高 — 可直接复用逻辑 |

### 6.2 Warp 仓库关键入口点

| 路径 | 用途 |
|------|------|
| [GitHub 仓库](https://github.com/warpdotdev/Warp) | 主源码 |
| [OpenAI 案例研究](https://openai.com/index/warp/) | Warp × OpenAI 合作详情 |
| [Warp 官网](https://www.warp.dev/) | 产品主页 |
| [Warp 开源博客](https://www.warp.dev/blog/warp-is-now-open-source) | 开源公告 |
| [Zach Lloyd 的 X/Twitter](https://x.com/zachlloydtweets) | CEO 的分享 |
| [Warp 官方 X/Twitter](https://x.com/warpdotdev) | 产品动态 |

### 6.3 可复用的模板和脚本

本文提供了以下可直接用的模板和脚本：

1. **AI_POLICY.md 模板** → [2.2.2 节](#222-在你的项目中抄作业)
2. **common.minimal.md 模板** → [2.3.2 节](#232-第一层commonminimalmd--核心指令所有开发者共享)
3. **平台模板示例** → [2.3.4 节](#234-第三层templates--平台模板)
4. **Task Prompt 框架** → [2.3.5 节](#235-第四层task-prompts--快捷命令)
5. **process_prompts.py** → [2.3.6 节](#236-prompt-维护机制)
6. **SKILL.md 模板** → [2.5.2 节](#252-skill-文件的结构可复用模板)
7. **chromium_docs.py** → [2.6.3 节](#263-第二层chromium-docs-skill本地文档搜索)
8. **knowledge_base.md 模板** → [2.6.6 节](#266-给你的项目建立-knowledge_basemd)
9. **Eval 执行器** → [2.7.4 节](#274-在你的项目中建一个简化版-eval)
10. **Projects 目录结构** → [2.8.2 节](#282-projects-的目录结构可复用模板)
11. **代码索引脚本** → [3.6.2 节](#362-在你的项目中实现类似功能)
12. **团队落地检查清单** → [5.1 节](#51-第一阶段打好基础1-2-周)

---

> **最后的话**：AI Coding 基础设施不是一蹴而就的。Chromium 的文档从 2015 年开始积累，跨越 11 年，Warp 的 Oz 也是从终端一步步演进过来的。**关键不是"一下子建好"，而是"开始建，然后持续建"。**
>
> 本文提供的所有模板和脚本，你都是从今天开始可以用的。选一个最小的切入点（比如 AI Policy + common.minimal.md），先让 AI 在你的项目里做对一件事，然后逐步扩张。
