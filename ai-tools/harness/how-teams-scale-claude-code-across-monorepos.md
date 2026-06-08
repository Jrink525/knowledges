---
title: "团队如何在大仓库和 Monorepo 中规模化 Claude Code——13 个模式"
tags:
  - claude
  - claude-code
  - monorepo
  - harness
  - agent-engineering
  - enterprise
date: 2026-05-29
source: "https://generativeprogrammer.com/p/how-teams-scale-claude-code-across"
authors: "Generative Programmer (swyx)"
related:
  - "ai-tools/claude/claude-code-large-codebase-best-practices.md"
  - "ai-tools/claude/claudemd-21-config-rules.md"
  - "ai-tools/agent-engineering/harness/agent-hooks-deterministic-control.md"
  - "ai-tools/agent-engineering/harness/thin-harness-fat-skills-garry-tan.md"
  - "ai-tools/agent-engineering/harness/build-your-own-mcp-server.md"
  - "ai-tools/agent-engineering/agentic-search-context-engineering.md"
  - "ai-tools/agent-engineering/patterns/agent-memory-system-from-basics-to-production.md"
  - "ai-tools/claude/claude-code-hooks-automation-workflow.md"
---

# 团队如何在大仓库和 Monorepo 中规模化 Claude Code

> **来源：** [How Teams Scale Claude Code Across Monorepos and Large Codebases](https://generativeprogrammer.com/p/how-teams-scale-claude-code-across)
> **作者：** Generative Programmer（swyx）
> **前文：** [12 Agentic Harness Patterns](https://generativeprogrammer.com/p/12-agentic-harness-patterns-from)
> **整理日期：** 2026-05-29

大型代码库暴露出 AI 编码助手不同的失败模式：跨越团队、约定、构建系统和命名规则。生成的文件数量可能超过源文件，最有用的答案往往存在于仓库之外。

**13 个模式分为三组：**
1. Claude 如何找到正确的代码上下文
2. Harness 如何保持会话有效
3. 配置如何覆盖到每个开发者并持续维护

---

## Group 1：Claude 找到正确代码上下文（4 个模式）

### Pattern 1: Context Cascade（上下文级联）

任何 monorepo 的根目录如果只有一个巨型 `CLAUDE.md`，要么膨胀要么太模糊。**Context Cascade** 把 `CLAUDE.md` 放在目录树的多个层级：

- **根目录**：全局规则、指针、关键注意事项
- **子目录**：局部命令、约定、领域术语

Claude 沿工作目录到根目录的路径逐级加载，越靠近被编辑的代码，指导越具体。

> **适用场景：** 任何有多个团队约定的 monorepo，或子目录遵循不同规则的大仓库。
> **权衡：** 级联的前提是各层级保持聚焦。根文件里塞 session 级笔记，或者叶目录里埋全局规则，都会破坏效果。

**关联：** [[claudemd-21-config-rules|21 条 CLAUDE.md 配置规则]]

---

### Pattern 2: Repo Map（仓库地图）

当目录名含义模糊时，Claude 无法推断从哪开始。旧分区、内部代号、按领域拆分、多年重组的目录——代码存在，但目录树只给微弱线索。

**Repo Map** 在仓库根目录加一个轻量级 Markdown 文件，列出每个顶层文件夹和一行描述。Claude 在打开文件夹前先扫描这份地图，减少盲目搜索。

```markdown
# Repo Map

- `/services/` — 微服务代码（每个服务一个子目录）
- `/libs/` — 共享库
- `/tools/` — CLI 工具和脚本
- `/docs/` — 技术文档和 ADR
- `/configs/` — 全局构建和部署配置
```

> **适用场景：** 布局非常规的仓库、旧分区、内部代号、超多顶层目录的 repo。对新入职的工程师也有帮助。
> **权衡：** 多了一个文件要维护。过时的条目会误导 Claude，让它信心满满地走到错误路径上。

---

### Pattern 3: Noise Filter（噪声过滤器）

生成的文件、构建产物、vendor 代码在每个 session 都会分散 Claude 的注意力。全局排除规则能帮到多数开发者，但可能阻碍需要检查这些文件的团队。

**Noise Filter** 通过 `.claude/settings.json` 提交默认排除项。每个开发者 clone 后继承相同的搜索和读取默认值。需要特例的开发者可以在本地覆盖，不影响团队基线。

```json
{
  "excludePaths": ["build/", "dist/", "node_modules/", "vendor/", "generated/"]
}
```

> **适用场景：** 任何生成代码、vendor 文件夹或构建产物会污染 Claude 搜索的 repo。
> **权衡：** 激进的排除项会隐藏下游代码依赖的文件。本地覆盖是安全阀，但只有知道它存在的开发者才会用。

---

### Pattern 4: Symbol Lookup（符号查找）

在百万行仓库里用文本搜索 `handleRequest` 可能返回数千个匹配。Claude 然后浪费 context 去逐个打开文件找真正相关的符号。它还可能选错——比如两个模块里的 `User` 类，或者不同语言里两个同名函数。

**Symbol Lookup** 把 Language Server Protocol (LSP) 的能力暴露给 Claude。文本匹配变成符号解析，过滤发生在 Claude 读文件之前。对于强类型、多语言仓库尤为宝贵，因为这些生态系统已经有成熟的语言服务器。

> **适用场景：** 多语言代码库、有通用函数名的 repo、以及有成熟 LSP 支持的生态（C, C++, Java, C#, TypeScript）。
> **权衡：** 设置成本确实存在。每种语言需要正确的 code-intelligence 插件和语言服务器二进制文件，LSP 支持弱的生态回报不大。

---

## Group 2：让会话保持有效（5 个模式）

### Pattern 5: Just-in-Time Skill（按需技能）

大型代码库有众多任务类型：安全审查、文档、部署、迁移、发布检查等。每次 session 只涉及一两种，把所有工作流塞进 `CLAUDE.md` 意味着每次 session 都为不需要的知识付 token 费。

**Just-in-Time Skill** 把每个专项工作流封装为一个 skill，只在任务需要时才加载。基础上下文保持小巧，任务特定知识随需出现。

> **每个 skill 保持狭窄**：何时触发、执行什么步骤、跑什么命令、常见失败的含义。
> **适用场景：** 有超过少量任务类型的代码库，特别是工作流远远超过普通编码上下文的场景。
> **权衡：** 触发逻辑需要小心设计。触发太积极的 skill 膨胀上下文；触发太保守的 skill 在该出力时闲置。

**关联：** [[thin-harness-fat-skills-garry-tan|Thin Harness, Fat Skills 模式]]

---

### Pattern 6: Scoped Skill（作用域技能）

在 monorepo 里，支付服务的部署技能不应该在有人编辑库存服务时加载。通用激活忽略了工作位置，把有用的专业知识变成噪声。

**Scoped Skill** 将技能绑定到特定子树。团队可以把 skill 文件放在子目录的 `.claude/skills/` 下，或使用路径 glob 在 skill 的 frontmatter 中声明作用域。支付部署技能仅在支付目录的 session 中可见。

> **适用场景：** 多 team monorepo，子目录之间操作流程差异大到交叉加载会有害处。
> **权衡：** 技能的所有权可能超过团队所有权。当路径易主时，技能绑定也需要审查。

---

### Pattern 7: Scout Subagent（侦察子 Agent）

了解一个子系统和编辑代码是不同的事。在同一 session 中同时进行会严重消耗 context window——用在了探索、笔记和实现上。等到开始编辑时，上下文可能已经被无关细节污染。

**Scout Subagent** 使用只读子 agent 进行探索。侦察兵在自己的上下文里绘制子系统地图，把发现写入文件，返回路径。主 agent 随后读取发现，用（相对）干净的上下文进行编辑。

```
主 Agent → 创建 Scout 子 Agent → Scout 探索文件系统
  → Scout 写入 findings.md → 主 Agent 读取 findings → 开始编辑
```

> **好的侦察输出是具体的**：相关文件、所有权边界、关键调用路径、要跑的测试、要避免的风险。
> **适用场景：** 重构、跨域修复、安全审计、或与 Claude 没见过的代码集成。
> **权衡：** 多了一轮往返，侦察结果只是快照。如果后续编辑使某个假设失效，主 agent 需要注意到并重新检查。

---

### Pattern 8: Search-as-a-Tool（搜索即工具）

Claude 的默认工具只在仓库内工作，但开发者需要的知识很大一部分不在仓库里。设计文档、事故报告、运行手册、工单、仪表盘——这些往往包含 Claude 需要的答案。

**Search-as-a-Tool** 把组织已有的搜索基础设施包装成 Claude 可调用的工具。搜索后端可能是 Elasticsearch、Glean、内部知识图谱或其他系统。MCP 只是实现机制，核心模式是**让机构知识在编码 session 中可访问**。

> **适用场景：** Claude 经常需要仓库之外的信息，且组织已有内部搜索。
> **权衡：** 搜索工具变成关键基础设施，它的故障会影响依赖它的每个 session。访问控制也很重要——Claude 继承了工具背后的权限。

**关联：** [[agentic-search-context-engineering|Agentic Search for Context Engineering]] [[build-your-own-mcp-server|自己动手建 MCP 服务器]]

---

### Pattern 9: Deterministic Checks（确定性检查）

"在 commit 之前一定要跑 linter"这种指令很容易被忘记。它们和其他每条指令竞争上下文空间，导致不同 session 的行为不一致。

**Deterministic Checks** 把质量保障从指令移到 hooks。Lint、格式化、类型检查、目标测试在定义的事件上自动执行——不管 Claude 是否记得。

```yaml
# .claude/hooks/
# - pre-commit: lint, format-check, type-check
# - post-file-write: run focused tests
# - pre-push: full test suite
```

> **适用场景：** 任何可以表述为"此检查必须在某个事件上始终运行"的规则：保存时 lint、commit 前格式化、写文件后类型检查、或生成变更后跑目标测试。
> **权衡：** 慢的 hook 拖慢每个 session；hook 失败时大声报错会中断 Claude 的流畅度。检查应该快速、专注、结果容易理解。

**关联：** [[agent-hooks-deterministic-control|Agent Hooks: 确定性控制]] [[claude-code-hooks-automation-workflow|Claude Code Hooks 自动化工作流]]

---

## Group 3：配置推广到全员并维护（4 个模式）

### Pattern 10: Harness Bundle（Harness 包）

好的 Claude Code 配置常常是部落知识。一个工程师在自己机器上搭了一套酷炫的技能、hooks、MCP 服务器组合。另一个团队几个月后重新造轮子，通常造得更差。新入职工程师从零开始。

**Harness Bundle** 把技能、hooks、MCP 配置打包成一个可安装的插件。新工程师第一天装上就继承团队的成熟配置。更新通过托管渠道推送，而不是复制粘贴的本地配置。

> **适用场景：** 当一台上出现有用的配置，团队可以从中受益。大多数团队在采用 Claude Code 几周内就会达到这个阶段。
> **权衡：** 包会僵化。每个开发者都安装的插件变得难以变更——就像任何共享库一样，需要协调各方消费者。

**关联：** [[agent-harness-engineering|Agent Harness 工程化]]

---

### Pattern 11: Day-One Harness（第一天 Harness）

开发者第一次使用 Claude Code 的体验很大程度上决定了要不要继续用。如果他们必须先搭 harness 再看到价值，很多人会放弃。

**Day-One Harness** 在开放广泛使用之前就把 harness 建好。一个小团队准备好核心插件、MCP 服务器、技能、hooks 和文档，让开发者的第一次 session 就能与代码库协作，而不是对抗。

> **适用场景：** 任何将 Claude Code 推广出试点范围的组织，特别是代码库有非显而易见约定时。
> **权衡：** 上线前的工作需要时间和人力资源。跳过它短期更便宜，但通常会留下需要后期清理的分裂配置。

---

### Pattern 12: Curated Starter Set（策展起始集）

完全开放所有技能和插件会带来安全、治理和一致性问题。配置不当的 MCP 服务器可能读取过多数据。未审核的技能可能把开发者推向不安全的工作流。但封锁一切也会扼杀采用。

**Curated Starter Set** 从窄开始：经过审批的技能和插件、必要的审核流程、有限的初始访问权限。随着信心增长和边界场景变得清晰，集合逐步扩大。

> **适用场景：** 金融、医疗、国防等受监管行业。也适合任何安全审核先于广泛采用的大型组织。
> **权衡：** 过于保守的起始集会挫伤早期倡导者。扩展的节奏和起始集同样重要——缓慢的审核让推广感觉受阻。

**关联：** [[agent-sandbox-infrastructure|Agent 沙箱基础设施]]

---

### Pattern 13: Self-Improving Hook（自我改进 Hook）

Claude 的出错在 session 中是可见的，但 session 结束后很容易被忘记。下一个 session 会重复同样错误。`CLAUDE.md` 只有在某人记住更新时才会改进。

**Self-Improving Hook** 在 session 结束时跑一个 stop hook。Hook 审查 transcript，提议 `CLAUDE.md` 更新——包括添加和淘汰。它还会发现模型的漂移：以前帮旧模型绕路的工作流在当前更强的模型上可能变成约束；为缺失工具的补丁一旦原生支持落地，就成了死代码。

> **适用场景：** 活跃维护 CLAUDE.md 的团队，能从少量频繁的改进中受益。特别适配 Context Cascade 模式。
> **权衡：** 没有人工审核，建议会堆积，噪声淹没信号。Hook 提议变更，但人类决定合并什么。

**关联：** [[harness-from-theory-to-practice|Harness 从理论到实践]] [[evo-self-improving-agent-harness-autoresearch|Evo: 自我改进的 Agent Harness]]

---

## 全文总结

Claude Code 能在大型代码库中跑得很好，这并非因为它神奇地理解整个仓库。**它之所以有效，是因为代码库给了它好工程师拥有的同样优势：**

- 清晰的起点（Session Start Point）
- 靠近代码的局部约定（Context Cascade）
- 结构不明显时的地图（Repo Map）
- 暴露仓库外知识的工具（Search-as-a-Tool）

**实际操作方案不是一个大号 `CLAUDE.md`：**
- 小巧的根文件
- 多级本地 `CLAUDE.md`
- Repo 地图
- 路径作用域技能
- 快速的 hooks
- LSP 符号查找
- 内部知识搜索工具

**最终目标不是更多的 Agent 基础设施。** 而是一个 Claude Code 可以在正确的位置进入、用正确提示阅读、不用把整个仓库拖入 session 就能修改的代码库。

---

## 13 个模式速查表

| 编号 | 模式 | 所属组 | 一句话 |
|------|------|--------|--------|
| 1 | Context Cascade | 上下文 | 多级 CLAUDE.md 层级加载，越靠近代码越具体 |
| 2 | Repo Map | 上下文 | 根目录 Markdown 地图，减少盲目搜索 |
| 3 | Noise Filter | 上下文 | `.claude/settings.json` 默认排除构建/Vendor |
| 4 | Symbol Lookup | 上下文 | LSP 符号解析替代文本搜索 |
| 5 | JIT Skill | 会话 | 按需加载技能，基础上下文保持小巧 |
| 6 | Scoped Skill | 会话 | 技能绑定到特定子树 |
| 7 | Scout Subagent | 会话 | 只读子 agent 探索→主 agent 编辑 |
| 8 | Search-as-a-Tool | 会话 | 内部搜索作为工具暴露给 Claude |
| 9 | Deterministic Checks | 会话 | Hooks 强制执行检查 |
| 10 | Harness Bundle | 推广 | 配置打包成可安装插件 |
| 11 | Day-One Harness | 推广 | 推广前先建好成熟配置 |
| 12 | Curated Starter Set | 推广 | 从窄开始，逐步放权 |
| 13 | Self-Improving Hook | 推广 | Stop hook 审查会话并提议更新 |

---

**参考资源：**
- [Anthropic: Claude Code in Large Codebases](https://claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start)
- [12 Agentic Harness Patterns](https://generativeprogrammer.com/p/12-agentic-harness-patterns-from)
- [[claude-code-large-codebase-best-practices|Claude Code 大型代码库最佳实践（知识库）]]

*整理于 2026-05-29，来源：Generative Programmer (swyx)*
