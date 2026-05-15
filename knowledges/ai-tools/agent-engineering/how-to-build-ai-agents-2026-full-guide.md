---
category: ai-tools
---

# 2026 年如何构建生产级 AI Agent（完整指南）

> **来源：** [How to Build AI Agents in 2026 (Full Guide)](https://x.com/av1dlive/status/2054238056090325492)
> **作者：** Avid (@Av1dlive)
> **日期：** 2026-05-12
> **数据：** 180 ❤️ · 303 🔖 · 55.9K 阅读
> **参考代码库：** [agentic-harness](https://github.com/codejunkie99/agentic-harness)（Rust）

---

## 核心问题

大多数 AI 工程师想认真做 agent 时，根本不知道到底该造什么。

- 有人拿 LangChain 做多 agent 演示，两周后因为 Python 互操作和异步运行时冲突放弃
- 有人试图从零写编排层——循环、会话存储、上下文组装——结果基础设施吃掉全部时间
- 有人复制 hello-world webhook 示例，以为懂了，结果 session 运行超 10 分钟就崩

最终结果都一样：大量管道代码，没有生产 agent，没有生产 agent 运行时的**心智模型**。

> TL;DR：读这个太长了？把链接给 Claude，让它回答你的问题：
> https://github.com/codejunkie99/agentic-harness

---

## 一、项目结构

两个 crate，一个 binary。每个执行目标都是配置选择，不是重写。

```
SDK   → 你引入任何 Rust 项目的库
CLI   → 包装 SDK
Agent → 从 `use agentic_harness::prelude::*` 开始的 Rust binary
```

**设计约束：** 同一个 agent binary 应该能在笔记本上交互模式运行、在 GitHub Actions 中克隆新仓库运行、通过 HTTP 对远程 E2B sandbox 运行、在 Cloudflare Worker 边界运行——**不改一行 agent 逻辑**。

---

## 二、三层架构

```
┌─────────────────────────────────────┐
│ 外层：你的 Rust 代码                │
│  写 handlers → 接收 AgentContext    │
│  调 sessions → 调模型/读写/shell    │
│  从不动 HTTP 客户端或解析模型响应    │
├─────────────────────────────────────┤
│ 中层：Harness                       │
│  管理：agent 注册、会话持久化、      │
│  上下文压缩、角色/技能发现、         │
│  模型选择、provider-neutral 适配     │
│  所有生产环境会崩的东西都在这里处理   │
├─────────────────────────────────────┤
│ 内层：执行目标（Execution Target）   │
│  本地文件系统 / CI / HttpSessionEnv │
│  / Cloudflare Worker                │
│  Handler 调 session.shell()         │
│  Harness 翻译到底层目标所需操作      │
└─────────────────────────────────────┘
```

**核心原则：** 当 E2B 发布新 API 版本 → 更新 connector，不动 agent 逻辑。当 Anthropic 发新模型 → 更新 runtime.json，不动 handler。

---

## 三、运行时配置（runtime.json）

写任何 handler 之前，先在工作区放 `agentic-harness.json`：

```json
{
  "defaultModel": "anthropic/claude-sonnet-4-6",
  "models": {
    "anthropic/claude-sonnet-4-6": { "apiKeyEnv": "ANTHROPIC_API_KEY" },
    "anthropic/claude-opus-4-7": { "apiKeyEnv": "ANTHROPIC_API_KEY" }
  }
}
```

**模型选择优先级（从高到低）：**
1. `PromptOptions::model(...)` — 单次调用覆盖
2. 选定 role 的 model metadata — 按角色默认
3. `defaultModel` — 工作区默认

> **安全要点：** 绝不在 runtime.json 中写 API key 字面量。用 `apiKeyEnv` 从环境变量读。Harness 在请求时读取环境变量，不是在启动时——你可以轮换 key 而无需重启服务器。

---

## 四、Agent 身份 = URL 路径

没有 agent ID 系统。没有注册表 key。没有你自己生成的 UUID。

**Agent 的身份就是 `POST /agents/<name>/<id>`。**

每个系统调用者都知道如何从上下文中构造一个有意义的 ID：PR 号、run ID、时间戳+任务名、用户 handle。

不需要 session 创建端点。不需要单独存 session ID。**URL 就是 session。**

---

## 五、Session：有状态的执行上下文

Session 不仅仅是一个对话线程。它是 agent 调用的**完整执行上下文**。

它持有：
- 与模型的消息历史
- 工作区文件访问（读、写、编辑、grep、glob、stat、readdir）
- Shell 执行（cwd 和 env 控制）
- 工具注册（MCP servers、自定义工具）
- 分配的角色和系统 prompt 覆盖
- 压缩预算和历史水位线

**关键行为：**
- 同一 ID 调用同一 agent 端点三次 → 模型看到三次连续的对话
- 历史自动累积，你不需要管理
- Session 管理 token 计数，防止上下文窗口溢出

---

## 六、Task：保持父 session 干净的聚焦子 session

> **这是我希望第一天就理解的原语。** 它是 agent 在长作业中保持连贯和半路开始幻觉之间的区别。

Task 是一次性的子 session。**新历史。共享工作区。向父 session 返回结果。父 session 的历史从未看到 task 的任何中间推理。**

```rust
let research = ctx.task("research-auth-libraries")
    .prompt("Analyze these three auth libraries...").await?;
// 父 session 只收到 clean summary
```

**为什么重要：** 当你在长 session 中直接做探索性分析，历史充满了中间工具调用、部分答案、模型对不相关事情的推理。模型会锚定在那些噪音上。Task 是精确的修复。

**规则：** 如果子问题有明确的 deliverables 且不需要父 session 的历史来完成 → 做成 task。"做成 task"的阈值比你想象的低。

---

## 七、Role 和 Skill：不重编译就改变行为

**Role** 在 `.agentic-harness/roles/` → 系统 prompt 叠加，调用时应用，调用后丢弃，不存入历史。

```yaml
# .agentic-harness/roles/security-auditor.yaml
name: security-auditor
model: anthropic/claude-opus-4-7
prompt: |
  You are a security auditor. Be thorough...
```

**Skill** 在 `.agents/skills/` → 行为描述文件，agent 在每个 session 开始时读取。

```
commit-message.md：
  Write conventional commits:
  feat(frontend): ... / fix(api): ... / chore(deps): ...
```

> 编辑 markdown → 下次运行行为更新。**不重编译。**

---

## 八、Coding Agent 循环详解

完整命令：

```bash
agentic-harness run --workspace . \
  --llm anthropic/claude-sonnet-4-6 \
  --deny-path secrets/ \
  --approve-dependencies \
  --commit "feat: add auth flow" \
  --pr
```

**循环：Inspect → Brief → LLM+Tools → Edit+Test → Commit/PR**

1. **Inspect：** 读工作区结构，加载 skills 和 roles，识别最相关的文件。先写 `coding-brief.md` 再碰任何代码
2. **Brief：** 模型承诺一个计划。中途可读 `.agentic-harness/runs/<id>/coding-brief.md` 看它决定做什么。如果 brief 不对 → kill run，重来
3. **LLM+Tools：** 编辑-测试循环。做修改 → 跑测试 → 读输出 → 继续。直到测试通过或达到迭代上限
4. **Commit/PR：** 暂存、提交、推送、开 PR

**每次运行生成 6 个 artifact：**
| 文件 | 内容 |
|---|---|
| `coding-brief.md` | 动代码前承诺的计划 |
| `summary.md` | 做了什么、试过什么、为什么 |
| `run.json` (~2KB) | 模型、耗时、token 数、迭代次数、退出状态 |
| `events.jsonl` | 每次工具调用（完整输入输出） |
| `diff.patch` | 全部文件变更的完整 diff |
| `checks.json` | 最终测试和 lint 结果 |

> **建议：** 把 run artifacts 提交到仓库。需要复现时，run.json 和 events.jsonl 就是证据链。

---

## 九、HttpSessionEnv：本地跑 binary，远程执行

**agent binary 在你本机或 CI 上运行，文件系统和 shell 操作在远程 sandbox 里执行。Agent 不知道也不关心它在哪个环境。**

```rust
use agentic_harness::HttpSessionEnv;
let env = HttpSessionEnv::new("https://e2b.dev/sandbox/my-sandbox");
```

**我最高频的用例：** 在干净的 Linux 环境中复现 CI 失败。Agent 在精确的失败 commit 克隆仓库，运行精确的失败命令，读完整输出，诊断失败，写报告。我读报告，从没碰过本地机器。Sandbox 在 session 结束时丢弃。

**⚠️ 性能陷阱：** 每次 shell 调用都是网络往返。40 次迭代 × 每次 3 个 shell 调用 = 数分钟纯网络延迟。

**修复：批处理 shell 工作：**

```bash
cat > agent-check.sh << 'SCRIPT'
cargo test && cargo clippy -- -D warnings
SCRIPT
# 一次调用跑完所有内容
```

---

## 十、构建目标：同一代码库，三种部署形态

| 目标 | 场景 |
|---|---|
| **native** | 默认。一个 binary，一个 manifest。能跑 Linux binary 的地方都能跑 |
| **node** | 用于 Railway/Render 等需要 Node 入口的平台。生成 `server.mjs`（30 行 HTTP shim），代理到 Rust binary |
| **cloudflare** | 用于 webhook 处理、路由元数据、小控制端点。**不支持长命令、真实文件系统、build 工具** |

**决策矩阵：**
- 作为 API 给其他服务调用 → **native**
- 托管在 Railway/Render → **node**
- Webhook 摄入、轻量路由 → **cloudflare**
- 其他一切 → **native**

---

## 十一、Schema 引导输出：从模型响应到类型安全

```rust
#[derive(Deserialize)]
struct ReviewResult { approved: bool, risk_level: String }

let result: ReviewResult = session
    .prompt_with_schema("Review this PR...", None)
    .await?;
```

模型可以在同一响应中输出推理散文 + 类型化数据。Harness 在 `---RESULT_START---` 和 `---RESULT_END---` 标记之间提取结果块。你得到 Rust struct。**编译时类型安全。**

如果模型返回不符合 schema 的内容，你得到 `PromptError::SchemaValidationFailed`，不是在三个调用点后访问缺失字段时才 panic。

---

## 十二、MCP Tools：延伸到 sandbox 之外

```rust
session.connect_mcp("sentry", "npx @sentry/mcp").await?;
```

Agent 获取 MCP server 的完整工具集。无需写工具定义。描述来自 server。模型根据描述决定何时调用哪个工具。

**关键技巧：** 如果你控制 MCP server，写**规定性**的描述——告诉模型什么时候调用，不只是它返回什么：
- ❌ "Search sentry" → 调用不一致
- ✅ "在回答任何关于错误、事故或生产问题之前调用这个" → 可靠调用

---

## 十三、Connector：生成适配器而非手写

把 connector recipe 丢给你的 coding agent：

```markdown
## Connector Recipe: Daytona
Protocol: HttpSessionEnv
Auth: Bearer token from Daytona API
Endpoint: https://api.daytona.io/v1/sandboxes
Lifecycle: create → exec → read → destroy
```

Agent 读它，写 Rust adapter module，处理认证，包装 provider 生命周期，暴露为 HttpSessionEnv。你 review diff，合并。Adapter 现在在你的项目里，是你的代码了。

> 作者说用这个方法花了约 20 分钟（含完整 review）接入了 Daytona。从头对着文档写，需要大半个下午+至少两个关于 refresh token 流的错误假设。

---

## 十四、自动压缩：处理长 session 不丢上下文

```json
{
  "compaction": {
    "context_window_tokens": 180000,
    "reserve_tokens": 8000,
    "keep_recent_messages": 10
  }
}
```

历史超过预算时，harness 让模型**总结 system prompt 和保留尾部之间的全部内容**。总结替换中间部分。尾部消息保持原样。压缩后的 session 更小，下次调用能塞进预算。

**权衡：** 总结会损失精度。50 条消息前做出的具体决定"我们选了 authlib 因为它是唯一支持 PKCE 且兼容 axum 中间件的库"可能变成"我们选了 authlib 做认证"。

**修复策略：**

```rust
session.write_file("decisions/auth-library.md",
    "Chose authlib because...").await?;
```

把决策写到文件里。**文件在压缩中幸存。** 模型可以随时按需读回来。历史不需要承载一切——如果工作区能承载的话。

> **golden rule：** 用 `agentic-harness doctor` 查看模型的实际报告上下文窗口。设 `context_window_tokens` 为那个值的 80-90%。

---

## 十五、9 个要当心的事项

| # | 问题 | 修复 |
|---|---|---|
| 1 | **Session 历史污染** — 探索性分析污染后续 prompt | 用 task。task 历史从不碰 parent |
| 2 | **Role 优先级惊喜** — 调用级 role 遮蔽了 session role | Session role 设身份，call role 缩范围 |
| 3 | **`--deny-path` 漏洞** — 你没意识到的秘密文件也在其他地方 | 拒绝前缀不是文件名：`--deny-path config/` |
| 4 | **CI 中 detached HEAD** — commit 因为没分支失败 | `git checkout -b agent-run-$RUN_ID` |
| 5 | **HttpSessionEnv 延迟** — 40 次迭代 × 3 次 shell 调用 = 几分钟 | 批处理：`agent-check.sh` 一次搞定 |
| 6 | **上下文预算低估** — 压缩在任务中触发，模型丢失计划 | 先跑 doctor，设 budget 为 80-90% |
| 7 | **Handler 注册后才加载 runtime config** — 错误看起来不像配置问题 | 总是在 `app()` 中先调 `load_workspace_context()` |
| 8 | **`--llm auto` 运行间变化** — 两次运行不可比 | 在 runtime.json 中锁定模型 |
| 9 | **删除 run artifacts** — 三周后要复现却找不到 | 提交 run artifacts（run.json 才 2KB） |

---

## 十六、作者事后反思

1. 碰任何东西之前先跑 `agentic-harness guide`
2. 写 handler 逻辑之前先写 session 级测试
3. 任何有子交付物的东西都用 task
4. 从第一次 serious run 就锁定模型
5. 把决策存在文件里，不在 session 历史里
6. 用远程 sandbox 时从第一天就开始批处理 shell 操作

---

## 底线

> 大多数 agent 框架是 API 调用的 wrapper。这是一个**运行时**。

- Wrapper 解决"让模型回答"
- 运行时解决"把 agent 部署到生产环境，并在模型变了、sandbox 变了、代码库变了、session 跑了两个小时溢出上下文窗口之后仍然保持工作"

**让你能拥有一个端到端生产 agent 的核心**：从第一个 handler 到 sandbox 到无人值守运行的 CI job。

不变化的：handler 逻辑、session 结构、task 模式、role 定义、skill 文件。
变化的：模型、provider、sandbox 厂商、部署目标。

架构的设计就是：**变化的永远不碰那些不变化的。**

---

**关联阅读：**
- [Thin Harness, Fat Skills：三层架构哲学](./agent-engineering/thin-harness-fat-skills-garry-tan.md)
- [Agent Harness 工程化指南](./agent-engineering/agent-harness-engineering.md)
- [AI Agent 学习路线图 2026：什么该学、什么该造、什么该跳过](./agent-engineering/ai-agent-roadmap-2026-what-to-learn-build-skip.md)
- [AI-First 工程团队构建指南](./agent-engineering/ai-first-engineering-team-guide.md)
