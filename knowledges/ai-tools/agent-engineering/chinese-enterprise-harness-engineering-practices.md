---
title: "中国企业 Harness Engineering 实践集锦：从团队治理到本地基建"
tags:
  - harness-engineering
  - agent-engineering
  - enterprise
  - monorepo
  - context-engineering
  - ai-governance
  - qqmusic
  - tencent
  - java
  - microservices
  - local-development
  - best-practices
  - china-enterprise
  - code-as-agent-harness
date: 2026-05-21
source: "腾讯云开发者公众号 × 阿里云开发者公众号 × AlphaSignal AI"
authors: "黄欣欣（QQ音乐） & 阿里云工程师（Java Harness） & AlphaSignal AI（Three Harness Layers 框架）"
---

# 中国企业 Harness Engineering 实践集锦：从团队治理到本地基建

> 本文持续积累国内企业的 Harness Engineering 实践经验，覆盖不同公司、不同技术栈、不同业务场景的落地案例。

---

## 概览：Harness Engineering 在中国企业的两个战场

Harness Engineering 在国内企业落地时，面临两个核心问题：

| 维度 | 问题 | 对应案例 | 核心方法论 |
|------|------|---------|-----------|
| **团队治理** | 大团队、多服务、多仓库如何让 AI 协作可治理 | QQ音乐（50+ 微服务） | L5 工程治理层 → 流程门禁 + 知识体系 + 服务矩阵 |
| **本地基建** | Java 微服务项目依赖云端，AI 无法自主验证 | Java Agent 运行时平台 | 依赖倒置 + Profile 隔离 + CLI 工具化 + 最小可运行子集 |

两篇案例互为补充：QQ音乐解决的是"多人在大系统上怎么用 AI"，Java 案例解决的是"AI 怎么能在本地验证自己的代码"。

---

## 案例一：QQ音乐 Harness Engineering — 团队级 L5 治理层

> **来源：** [腾讯云开发者公众号](https://mp.weixin.qq.com/s/yw3DvqKBIV5fIZkSG12zdA) · 黄欣欣
> **场景：** QQ音乐音乐商业化团队，50+ 微服务，单仓多服务 + 多仓协同

![QQ音乐 Harness Engineering 封面](../image/qqmusic-harness-engineering-1.jpg)
*(封面图：腾讯云开发者公众号)*

![Harness Engineering 架构图](../image/qqmusic-harness-engineering-3.jpeg)
*(架构图：Harness 四大组件与 L5 治理层)*

### 核心矛盾：生成快、验证慢、错误累积

AI 能显著提升编码效率，但有一个容易被忽略的配套事实：**生成速度在提升，验证能力却没有同步提升。** 代码出得越快，错误积累得也越快；AI 自主性越强，偏离正确轨道时的修正成本就越高。

这就是 AI 时代软件工程的核心矛盾。解决的思路不是更长更复杂的 prompt，而是 **工程化**。

### 核心公式：代码产出 = AI 能力 × 上下文质量

这个乘号至关重要。当上下文质量趋近于零时，模型再强，产出也是零。

在真实业务仓里，AI 拿不到的上下文缺口主要有五类：

| 缺口类型 | 典型问题 | Harness 的解 |
|---------|---------|-------------|
| **隐性规范** | 锁机制、埋点规则、错误码空间 | `context/team/` |
| **历史决策** | 为什么选了 A 方案没选 B | `context/project/{module}/experience/` |
| **服务契约** | IDL 字段冻结状态、下游依赖 | `.service-matrix/dependencies.yaml` |
| **跨服务依赖** | 同一个需求要改哪几个服务 | 服务矩阵自动解析 |
| **演进轨迹** | 模块上次大改的坑、灰度策略 | Self-Refinement 闭环 |

提升上下文质量，是比提升模型能力更高效的杠杆。

### 业务约束的四类工程化

| 约束类型 | 技术落点 |
|---------|---------|
| **流程约束** | 五阶段主流程 + 四道门禁 + `main-process-numbering.md` |
| **拓扑约束** | `.service-matrix/dependencies.yaml` + 影响面分析 |
| **契约约束** | 三仓联动 + `idl_required` + 服务仓库检查门禁 |
| **知识约束** | `context/team/`、`context/harness-framework/`、`context/project/` 三层知识 |
| **演进约束** | Self-Refinement + `experience/*.md` 版本化沉淀 |

### 五阶段 + 四道门禁：让错误死在最便宜的地方

```
阶段 1 初始化 → 阶段 2 需求定义⭐ → 阶段 3 设计⭐ → 阶段 4 开发⭐⭐ → 阶段 5 交付
                    ↑需求评审       ↑设计评审       ↑Dev进入 + 服务仓库检查
```

| 门禁 | 位置 | 阻塞条件 |
|------|------|---------|
| 需求评审 | 阶段 2.2 | 需求文档不合格 |
| 设计评审 | 阶段 3.3 | 方案漏了关键约束、追溯链不达标 |
| Dev 进入 | 阶段 4.2 | `tasks/features.json` 缺失或不合法 |
| 服务仓库检查 | 阶段 4.3 | 三仓分支不一致、服务仓库未就位 |

**核心理念：错误越早被拦住，代价越低。** 门禁尽量少、尽量靠前。

### 三层知识体系

```
团队级 (最稳定)          context/team/          Git规范、错误码空间、日志规范
框架工程级 (中频更新)    context/harness-framework/  五阶段流程、门禁规则、模板
服务级 (高频演进)        context/project/{项目}/{模块}/{服务}/  架构图、API、踩坑经验
```

### `.service-matrix/dependencies.yaml` — 服务拓扑单一真相源

```yaml
workspace: ".."
business_repo: "music_commercial_go_proj"
idl_repo: "qqmusicjce"
default_team: "music-commercial"

services:
  vipapi:
    module: vip
    repo_path: "{business-repo}/vipapi"
    idl_required: true
  assetcardmallcgi:
    module: assetcard
    repo_path: "{business-repo}/assetcard/mall/assetcardmallcgi"
```

路径从不硬编码，用 `{business-repo}` / `{idl-repo}` 占位符。当前管理 **57 个服务**。

### 三仓联动

每个需求，Harness 仓、业务仓、IDL 契约仓共用**完全相同的分支名**，一条 TAPD 单 ID 对应一个分支名，追溯链整洁。阶段 4.3 门禁自动校验三仓分支一致性。

### Skill / Agent / Command 三件套

| 组件 | 数量 | 用途 |
|------|------|------|
| **Skills** | 34 个 | 可复用的工作流单元 |
| **Agents** | 24 个 | 自主子任务执行者（按阶段组织） |
| **Commands** | 35 个 | 标准化入口（`/requirement:new` `/service:deps` 等） |

全部是版本化的 markdown 文件 → 可 code review、可 diff、可回滚。**Knowledge as Code**。

**亮点：** 阶段 4.4 的代码审查拆成 8 个维度的独立 Agent 并行执行（设计一致性、复杂度、并发安全、错误处理、安全漏洞、契约一致性、追溯链、辅助检查），再聚合为 review 报告。

### Self-Refinement：让 AI 从错误中沉淀经验

LLM 没有跨会话记忆。团队的每一个"纠正"，都是一次宝贵的信号。

```
① 用户纠正 AI → ② AI 识别是"模式性教训"还是"一次性 diff"
  → ③ 模式性教训 → 提出沉淀层级（团队级/框架级/服务级）
  → ④ 用户确认 → 生成 experience 文档 / 更新 Skill
  → ⑤ 下次同类场景，新会话/新模型/新人自动受益
```

### 与 AI 编程工具的关系

Harness Engineering 治理层位于执行层之上，不替代任何工具：

```
治理层：Harness Engineering（L5）→ 流程、门禁、知识、服务矩阵、经验沉淀
执行层：Claude Code / Gemini CLI / Codex CLI / Continue / CodeBuddy → 读改测
```

**多运行时适配：** `.codebuddy/skills/` / `agents/` / `commands/` 是真相源，`scripts/install.sh` 渲染到各 CLI 本地目录（`.claude/` `.gemini/` `.codex/` `.continue/`）。改一次规范，所有 CLI 受益。

### 为什么必须自研

通用产品无法替团队定义：
1. **服务矩阵语义** — 谁依赖谁、路径如何解析
2. **需求生命周期语义** — 阶段、门禁、产物、追溯关系
3. **IDL 契约语义** — 哪些字段冻结、哪些变更需同步业务仓
4. **团队经验语义** — 某个服务过去的分页无上限打爆下游
5. **工具解耦语义** — 不被任何运行时锁定

> **Context Engineering + Spec-First + Knowledge as Code，构成了可验证、可演进的 AI 协作工程基线。**

---

## 案例二：Java 微服务的本地 Harness 改造 —— 让 AI 在微服务项目中拥有自主验证能力

> **来源：** [阿里云开发者公众号](https://mp.weixin.qq.com/s/3-hQ4vHYErfpIzYPC6wJwg)
> **场景：** Java 微服务项目，重度依赖云端基础设施（OSS、远程沙箱、HSF、TDDL）

![Java 本地 Harness 封面](../image/java-harness-local-harness-1.jpg)

### 问题：微服务架构天然不 AI 友好

在依赖比较轻的项目里（前端、CLI 工具、Python 脚本），AI Coding 的闭环是这样的：

```
编辑代码 → 本地运行 → 测试验证 → AI 读取结果 → 自动修复 → 再次验证 → ...
```

但在 Java 微服务项目里，这个闭环基本是断的。

Java 项目重度依赖云端基础设施：**HSF**（服务调用）、**TDDL**（数据库路由）、**Diamond/Switch**（配置下发）、**MetaQ**（消息队列）。一个 `@Autowired` 背后可能牵着一整套分布式基础设施。这些东西在云端跑得很好，但在本地全部不可用。

结果是：

```
本地 Vibe Coding → 推预发部署（等5分钟） → 人工验证结果
→ 截图贴回给AI → AI改两行 → 再推预发 → 再等5分钟 → ...
人在每个环节都是阻塞点
```

同样是 150 行代码的 bug fix，本地能跑的项目 AI 30 秒自愈；依赖云端环境的项目，3-4 轮人工推预发，半小时起步。

### 三条改造原则

#### 原则一：依赖倒置，接口先行

上层逻辑依赖抽象接口，不依赖具体实现。云端和本地只是接口的不同实现。

**改造前：**

```
FilesystemService → OssStorageAdapter (具体类，直接调 OSS SDK)
AgentWorkspace → SandboxCommandExecutor (具体类，调远程沙箱 API)
```

**改造后：**

```
StorageAdapter (接口)
  ├── OssStorageAdapter (线上，走 OSS SDK)
  └── LocalStorageAdapter (本地，走 java.nio.file)

CommandExecutor (接口)
  ├── SandboxCommandExecutor (线上，调远程沙箱 API)
  └── LocalCommandExecutor (本地，ProcessBuilder + bash -c)
```

上层代码完全不用改。切换环境就是换一个接口实现。

#### 原则二：零侵入，Profile 隔离

本地改造不能影响线上代码路径。

- **Spring Profile 隔离**：本地 Bean 用 `@Profile("local")`，线上用 `@Profile("!local")`，编译期彼此不可见
- **`@Nullable` 参数注入**：可选依赖标 `@Nullable`，不存在时 Spring 注入 null
- **条件守卫**：运行时通过 null 检查决定走哪条路径
- **`@ComponentScan` excludeFilters**：线上专属包（远程沙箱、OpenTelemetry 观测）整个排除

> **检验标准：删掉所有本地相关代码后，线上行为完全不变。**

#### 原则三：工具 AI 化，CLI 优先

AI Agent 的能力边界 = 它能调用的工具的边界。GUI 对 AI 不可见，CLI 才是 AI 能用的东西。

**工具 AI 化优先级：**

| 优先级 | 工具形态 | AI 可用性 | 示例 |
|--------|---------|-----------|------|
| 1 | CLI | 直接可用 | mw-cli, mvn, git, arthas |
| 2 | MCP Server | 协议适配 | 数据库查询、监控数据 |
| 3 | Skill / Tool | 自定义封装 | 配置查询、服务诊断 |
| 4 | GUI | 不可用 | Web 管理台、IDE 插件 |

### 改造效果

| 对比项 | 改造前 | 改造后 |
|--------|-------|--------|
| 文件操作验证 | 推预发，通过 OSS 控制台查看 | 本地直接 `ls` 查看 |
| Bash 执行验证 | 推预发，登录沙箱查看 | 本地 Terminal 直接看 |
| AI 自主验证 | 做不到 | ReadFile 验证 WriteFile 结果 |
| 单次迭代耗时 | 5-10 分钟（含部署等待） | 秒级 |
| AI 自主修复轮数 | 0（每轮人工介入） | 平均 3-5 轮后自行收敛 |

### 代码示例

```java
// @Profile("local") — 本地专属 Bean，线上完全不加载
@Configuration
@Profile("local")
public class LocalRepositoryConfig {
    @Bean
    CommandExecutor localCommandExecutor() {
        return new LocalCommandExecutor();
    }
    @Bean("localFsBasePath")
    String localFsBasePath() { return "/tmp/agentfs"; }
    // 用 AtomicLong 替代 TDDL GroupSequence
    @Bean("sessionSequence")
    Sequence sessionSequence() { return new LocalSequence(); }
}
```

```java
// @Nullable 参数注入 — 本地有值就走本地，线上没有就走 OSS
public AgentRunner(@Nullable @Qualifier("localFsBasePath") String localFsBasePath, ...) {
    // 线上环境：localFsBasePath = null，走 OSS 路径
    // 本地环境：localFsBasePath = "/tmp/agentfs"，走本地路径
}
```

### 实践案例：AI Agent 运行时平台的本地化改造

**线上架构：**

```
文件操作：AgentFs → OSS 对象存储
命令执行：远程 Sandbox（容器沙箱）
文件共享：Sandbox 通过 OSS Mount 挂载 Agent 的 OSS 存储桶
```

**改造方案：** 一个接口，两套实现，Profile 条件装配。

改造后本地环境：
- 文件系统 → `LocalStorageAdapter`，文件存到 `/tmp/agentfs/{sessionId}/...`
- Bash 执行 → `LocalCommandExecutor`，用 ProcessBuilder 在本机执行 `bash -c`
- 数据库 → H2 替代 TDDL MySQL（H2 MODE=MySQL 兼容 MySQL 语法）
- 分布式 ID → AtomicLong 替代 GroupSequence
- 配置中心 → `switch-config-local.properties` 脚本从预发拉取
- 中间件 → `spring.autoconfigure.exclude` 排除 EagleEye/HSF/Sunfire 等

### 配合 Harness Engineering 落地

**CLAUDE.md：给 AI 一张地图**

```markdown
# 项目简介
AI Agent 运行时平台，支持 ReadFile/WriteFile/Bash 等 Tool。
# 本地开发
- 启动：`mvn spring-boot:run -Dspring.profiles.active=local`
- 测试：`mvn test`
- 本地文件系统根目录：`/tmp/agentfs/`
# 架构约束
- 上层模块只依赖接口，不依赖具体实现类
- 本地专属代码通过 @Profile("local") 隔离
- 新增本地适配不得修改线上代码路径
```

**验证脚本 `scripts/verify-local.sh`：让 AI 自己检查**

AI 改完代码后跑一次 `bash scripts/verify-local.sh`，自动完成编译检查 → 单元测试 → 本地启动健康检查 → 文件系统闭环验证。不需要人工介入。

### Harness Engineering Checklist（Java 版）

**可运行性：**
- [ ] 项目能否在本地通过一条命令启动？
- [ ] 启动是否依赖外部中间件？有没有本地替代？
- [ ] 外部依赖是否通过接口抽象？能否通过 Profile 切换？

**可测试性：**
- [ ] AI 能否在本地运行测试并读取结果？
- [ ] 核心逻辑是否有单元测试？AI 改完代码后能否立即验证？
- [ ] 端到端验证能否通过 API 调用 + 断言自动完成？

**可观测性：**
- [ ] 日志是否结构化（JSON 格式）、可 grep？
- [ ] 是否集成 CLI 化的 JVM 诊断工具（Arthas、jstack 脚本）？
- [ ] AI 能否通过命令行获取运行时状态？

**工具 AI 化：**
- [ ] 运维工具是否有 CLI 入口？（配置管理、服务诊断等）
- [ ] 是否有 MCP Server 或 Skill 暴露内部系统能力？

**隔离性：**
- [ ] 本地改造是否通过 `@Profile` 隔离？
- [ ] 本地代码是否对线上代码路径零侵入？
- [ ] 删除所有本地相关代码后，线上行为完全不变？

### 五个可复用方法论

1. **找到最小可运行子集。** 不需要把所有线上能力搬到本地，只跑通核心链路即可。
2. **替代而非模拟。** H2 不是在"模拟"MySQL，它就是真实数据库。LocalCommandExecutor 不是在"模拟"沙箱，它就是真实的 bash 执行。替代方案要能真实运行。
3. **脚本化一切人工操作。** 但凡需要人登录管理台的操作，都应该有一个对应的脚本。脚本就是 AI 的手。
4. **分层隔离，逐层验证。** 先能编译 → 再能启动 → 再核心接口调通 → 再端到端测试。每层都有对应验证手段。
5. **让 AI 成为改造的参与者。** 一旦 AI 能跑测试、能看到报错，它的效率就上来了。每完成一步改造，AI 能做的事情就多一点。

### 后续方向

- **JVM 诊断工具化**：通过 Skill 封装 Arthas 的 `watch`、`trace`、`tt` 命令，让 AI 实时观测方法调用
- **AI 理解测试失败**：AI 不仅跑测试，还能解析 Surefire 报告 → 定位失败用例 → 读取源码 → 定位原因 → 修复 → 验证 → ...
- **理想态**：AI 在本地完全自主地跑完"发现问题→定位原因→修复代码→验证修复"的完整循环

### 改造全景图

| 线上依赖 | 本地替代 | 改动方式 |
|---------|---------|---------|
| OSS 对象存储 | 本地文件系统 (java.nio.file) | 新增接口 + 本地实现 |
| 远程沙箱 | 本机 bash 执行 (ProcessBuilder) | 新增本地实现 |
| TDDL + MySQL | H2 文件数据库 (MODE=MySQL) | application-local.properties |
| TDDL GroupSequence | AtomicLong 本地序号 | 新增本地实现 |
| Switch Center | switch-config-local.properties | 脚本从预发拉取 |
| Diamond 配置中心 | application-local.properties | Spring Profile |
| EagleEye / HSF / Sunfire | 排除自动配置 | spring.autoconfigure.exclude |
| Pandora 启动器 | 标准 java -cp 启动 | start-local.sh |
| OpenTelemetry | 排除观测包 | ComponentScan excludeFilters |

---

## Harness Engineering Checklist（通用版）

结合两个案例的实践经验，这里给出一份通用的 Harness Engineering 成熟度检查清单：

### L1：个人开发环境

- [ ] 项目能否在本地一条命令启动？
- [ ] AI 能否跑测试并读取结构化的测试结果？
- [ ] CLAUDE.md 是否包含启动命令、测试命令和架构约束？

### L2：项目上下文

- [ ] 关键规则是否从"人脑/口头"变成了文件？
- [ ] 编码规范、技术栈、常用命令是否在 CLAUDE.md 中？
- [ ] 团队特有的"隐性知识"（踩坑经验）是否已显式化？

### L3：团队治理

- [ ] CLAUDE.md / .claude/rules/ 是否进 git，走 PR + Code Review？
- [ ] 个人级、项目级、本地级的分层是否清晰？
- [ ] `context/team/` 团队规范是否建立？

### L4：服务治理

- [ ] 服务拓扑是否有单一真相源？
- [ ] AI 能否正确分析跨服务影响面？
- [ ] 同一个需求涉及多个仓库时，是否有联动机制？

### L5：持续演进

- [ ] AI 错误是否能沉淀为团队经验？
- [ ] 是否有 Self-Refinement 闭环？
- [ ] 规范是否在持续迭代，而非一次配置永不更新？

---

## 理论框架：Code as Agent Harness — Three Harness Layers 🔥

> **来源：** [AlphaSignal AI](https://x.com/alphasignalai/status/2057153343081111582) · 论文 "Code as Agent Harness" — UIUC × Meta × Stanford，40+ 作者，400+ 文献综述
> **核心观点：** 大多数 Agent 失败不是推理失败，而是 **Harness 失败**。

### 问题：为什么 Agent 总在看似简单的地方卡住

一个通过所有测试却在两个失败策略间无限循环的 Agent？问题不在模型，在 harness 没有死局检测。一个在新仓库上无法复现的 Bug？问题不在模型，在 harness 没有可用的执行环境。一篇 100 页的 UIUC × Meta × Stanford 联合调查揭示了根源。

### 三层拆解：模型、基础设施、自生产件

论文将任何 Agent 系统拆解为三个耦合部分：

| 层 | 组成 | 说明 |
|----|------|------|
| **模型内部能力** | 推理、规划、感知 | 模型本身的认知能力 |
| **系统基础设施** | 工具、沙箱、内存、权限层级、遥测 | Harness 提供的运行时支持 |
| **Agent 自生产件** 🆕 | 回归测试、临时工具、DSL 程序、可执行工作流、可复用技能 | Agent 在执行中自行产出的代码制品 |

### 三层 Harness 架构

```
┌─────────────────────────────────────┐
│  3. Scaling the Harness            │  ← 多 Agent 在共享代码制品上协调
│  多 Agent 协调、共享制品、冲突策略    │
├─────────────────────────────────────┤
│  2. Harness Mechanisms             │  ← 计划-执行-验证循环
│  规划、记忆、工具使用、验证器链       │
├─────────────────────────────────────┤
│  1. Harness Interface              │  ← 代码作为推理/行动/环境的介质
│  Agent-Computer Interface、可执行中间表示 │
└─────────────────────────────────────┘
```

### 诊断你的 Stack 的三问

**第一层：Interface** — Agent 的推理、行动和环境状态是否都是**可执行、可检查的代码**？

| 健康 | 不健康 |
|------|--------|
| Agent 输出可执行代码作为推理中间件，工具调用、生成程序、仓库状态、轨迹、测试结果构成闭环 | Agent 输出自然语言描述，没有可执行的中间表示，失败完全靠人工复现 |

**修复：** 让模型输出可执行代码作为推理中间件，给 Agent 一个 SWE-agent 风格的 shell + edit + search 结构化接口，操作真实仓库而非伪代码。

**第二层：Mechanisms** — 当某件事失败时，harness 会做什么？

| 健康 | 不健康 |
|------|--------|
| 运行 plan-execute-verify 循环，使用具名验证器（单元测试、类型检查、lint、运行时监控），跨会话持久记忆，拓扑排序执行 | 只有单次生成，验证只到最后才做，记忆只靠当前 prompt 里的 working memory |

**修复：** 在各生成步骤之间（而非仅在最后）插入具名验证器作为门控。引入**四种记忆类型**：

| 记忆类型 | 说明 | 国内案例映射 |
|---------|------|-------------|
| **Semantic Memory** | 对仓库语义的理解（架构、API、约定） | QQ音乐 `context/team/` + `.service-matrix/` |
| **Experiential Memory** | 过去的轨迹经验 | QQ音乐 `experience/*.md`（Self-Refinement 沉淀） |
| **Long-term Memory** | 带压缩-检索策略的持久化历史 | — |
| **Working Memory** | 当前 prompt 上下文 | CLAUDE.md / 约束说明 |

**第三层：Scaling** — 当两个 Agent 协作同一任务时，共享介质是什么？

| 健康 | 不健康 |
|------|--------|
| 共享代码制品（仓库、测试、轨迹、结构化工作流），有冲突解决策略 | Agent 之间直接传消息，没有可检查的共享状态 |

**修复：** 用共享制品替代直接消息传递。AgentCoder 的 programmer-tester-executor 分工模式、MetaGPT 的基于共享消息总线的角色分工，是典型案例。

### 三名值得关注的开放性发现

**1. Oracle Adequacy（评估隐瞒）**

如果你的 Agent 评估只是 pass/fail 单元测试，你在衡量错误的东西。每个 Agent 评估都在将**模型质量、工具可靠性和 Harness 质量**揉成一个端到端数字。

> **中文解读：** 当你的 Agent 突然表现变好，不一定是模型升级了，可能是 harness 的容错机制更完善了。两者混在一起，你永远不知道真正原因。

**2. The Verification Gap（验证鸿沟）**

绿色测试通过 ≠ 正确的规格。每次 Agent 的执行动作都应该附带**证据包**：哪些检查跑了、哪些假设成立、代码哪些部分未被测试、残留了什么风险。

> **中文解读：** QQ音乐 8 维度并行代码审查就是这个思想的实践——不是问"能用吗"而是问"哪里可能出问题"。

**3. Approvals That Don't Reset（审批不重置）**

如果审批在会话结束后消失，Agent 下次会重复同样不安全的行为。权限规则应该根据人的决策**持续进化**，而非每次重置。

> **中文解读：** 一次性审批是常见架构缺陷。你拒绝了 Agent 删除某个目录，但下个会话它不记得。权限系统需要持久化人的决策痕迹。

### 与中国企业实践的映射

Three Harness Layers 框架为 QQ音乐和 Java 微服务实践提供了理论锚点：

| 论文层 | QQ音乐实践 | Java 微服务实践 |
|--------|-----------|----------------|
| **Interface** | 三仓联动 + 服务矩阵（代码作为资产和桥接介质） | 依赖倒置 + 接口抽象（代码可执行验证） |
| **Mechanisms** | 五阶段四门禁（具名验证器链）+ 8维并行审查 + Self-Refinement | CLI 工具化 + verify-local.sh 脚本（自动化验证器） |
| **Scaling** | 24 Agents 编排 + 多服务拓扑分析 | — |
| **四种记忆** | `context/team/`（Semantic）+ `experience/*.md`（Experiential） | CLAUDE.md（Objective + Working Memory） |

### Harness 成熟度快速诊断（Three Layers 版）

| 层级 | 诊断问题 | 国内实践参考 |
|------|---------|-------------|
| **Interface** | Agent 的推理中间件是可执行代码吗？失败能自动复现吗？ | Java 微服务的本地验证闭环 |
| **Mechanisms** | 有具名验证器流水线吗？记忆跨会话持久吗？ | QQ音乐 8维审查 + Self-Refinement |
| **Scaling** | 多 Agent 共享代码制品吗？有冲突策略吗？ | QQ音乐 24 Agents 编排 |

### 快速自检七问

1. 你的 Agent 失败时，是模型问题还是 harness 问题？（你能分清吗？）→ Oracle Adequacy
2. 每次 Agent 执行能产出可复现的证据包吗？→ Verification Gap
3. 审批权限是否会随会话结束归零？→ Approvals Reset
4. Agent 的推理通过代码（可执行）还是文字（不可执行）表达？→ Interface
5. 验证发生在流程中还是流程末？→ Mechanisms
6. 多 Agent 通过共享制品还是直接消息协作？→ Scaling
7. 你的评估指标知道自己在测什么吗？→ Oracle Adequacy

> **总结：** "把这篇论文当词汇表，别当路线图。Harness 是团队现在正在投入优化的层。这个 taxonomy 会让你更精确地描述你的 stack，但它不会告诉你周一该建什么。"

---

## 生产级 Harness 组件深度拆解 🧩

> **来源：** [potatoloogs](https://x.com/potatoloogs/status/2057391224592667051) · Agent Harness 深度拆解

### 基础类比：裸 LLM = 没有操作系统的 CPU

> "We have reinvented the Von Neumann architecture." — Beren Millidge

| 计算机组件 | Harness 对应物 |
|-----------|---------------|
| CPU | 裸 LLM |
| RAM | 上下文窗口（速度快但容量有限） |
| 硬盘 | 外部数据库/向量存储（容量大但读写慢） |
| 设备驱动 | 工具集成 |
| **操作系统** 🎯 | **Harness** |

### 围绕 LLM 的三层工程层级

| 层级 | 职责 | 范围 |
|------|------|------|
| **Prompt Engineering** | 写模型收到的指令，告诉模型怎么做 | 最窄 |
| **Context Engineering** | 管理模型能看到什么、什么时候看到 | 中等 |
| **Harness Engineering** 🎯 | Prompt + Context + 整套应用基础设施 | **最宽** |

> "只要做的东西不属于模型本身，那就属于 harness。" — LangChain Vivek Trivedy

### 生产级 Harness 的 12 个核心组件

| # | 组件 | 核心问题 | 核心实践 |
|---|------|---------|---------|
| 1 | **Orchestration Loop** | 如何让系统持续运转？ | Thought-Action-Observation (TAO/ReAct) 循环 |
| 2 | **Tools** | 如何操作外部世界？ | 工具 schema 定义、注册、执行、结果格式化 |
| 3 | **Memory** | 如何跨 Token 保留信息？ | 短期记忆 + 长期记忆 + CLAUDE.md/MEMORY.md |
| 4 | **Context Management** | 如何防止上下文腐烂？ | 压缩、遮蔽、即时检索、子 Agent 委派 |
| 5 | **Prompt Construction** | 模型每次看到什么？ | 优先级栈：system → tools → 指令 → 历史 |
| 6 | **Output Parsing** | 如何理解模型输出？ | 原生 tool_calls / 结构化输出 / 重试解析 |
| 7 | **State Management** | 如何保持任务状态？ | typed dict / checkpoints / progress files |
| 8 | **Error Handling** | 失败时怎么办？ | transient retry → LLM 自愈 → 请求人工 → 抛异常 |
| 9 | **Guardrails & Safety** | 如何防止越界？ | input/output/tool 三层 guardrails + tripwire |
| 10 | **Verification Loops** | Agent 怎么知道自己做对了？ | 规则验证 + 视觉验证 + LLM-as-Judge |
| 11 | **Subagent Orchestration** | 如何拆分复杂任务？ | Fork / Teammate / Worktree / Handoff |
| 12 | **Prompt Construction** | 谁控制模型行为？ | 优先级栈决定控制权分配 |

### 一次完整的 Harness 循环（7 步）

```
Step 1: Prompt Assembly      → 拼 system + tools + memory + history
Step 2: LLM Inference        → 发请求给模型 API
Step 3: Output Classification → text=结束 / tool_calls=执行 / handoff=切换
Step 4: Tool Execution       → 校验参数 → 检查权限 → 执行 → 捕获结果
Step 5: Result Packaging     → 格式化为 model-readable message
Step 6: Context Update       → 追加历史 / 触发压缩
Step 7: Loop                 → 回到 Step 1，直到终止条件
```

**终止条件：** 最终回答 / 超 max turns / token 耗尽 / guardrail 触发 / 用户中断 / 安全拒答

### 跨上下文窗口的长任务：Ralph Loop 模式

对于跨多个 session 的长期任务，Anthropic 提出两阶段模式：

```
Initializer Agent          Coding Agent
  ├─ init script            ├─ 读取 git logs
  ├─ progress file          ├─ 读取 progress files
  ├─ feature list           ├─ 定位当前状态
  └─ initial git commit     ├─ 选最高优先级 feature
                            ├─ 继续工作 → 提交
                            └─ 写入总结
```

> 文件系统提供了跨上下文窗口的连续性。长期任务不能只靠聊天记录续命。

### 主流框架对比

| 特性 | Anthropic SDK | OpenAI SDK | LangGraph | CrewAI | AutoGen |
|------|-------------|-----------|-----------|--------|--------|
| **Loop 模型** | Gather-Act-Verify | Code-first runner | State graph | Role-based Crew | Conversation-driven |
| **结构** | query() async iterator | Runner 3 种模式 | Nodes + Conditional Edges | Agent + Task + Crew | Core + AgentChat + Extensions |
| **子 Agent** | Fork / Teammate / Worktree | agents-as-tools + handoffs | 嵌套 state graphs | Multiple Agents | 5 种编排模式 |
| **State** | git commits + progress files | 4 种互斥策略 | typed dict + reducers | — | — |
| **验证** | Rules + Visual + LLM-as-Judge | Guardrails 三层 | — | — | — |

> 框架实现不同但思路趋同：dumb loop + 智能留给模型 + 可插拔组件

### Harness 架构师的 7 个核心选择

**1. Single-Agent vs Multi-Agent**

Anthropic 和 OpenAI 一致建议：先把**单 Agent 做到极限**。多 Agent 带来额外 LLM 调用 + 路由成本 + handoff 上下文损失。只在工具超 10 个或任务领域明显分离时再拆分。

**2. ReAct vs Plan-and-Execute**

| | ReAct | Plan-and-Execute |
|---|------|-----------------|
| 特点 | 每步交织推理和行动 | 规划和执行分离 |
| 性能 | 灵活，但每步成本高 | LLMCompiler 报告 3.6x 提速 |
| 适用 | 探索性任务 | 确定性流水线 |

**3. 上下文窗口管理策略**

| 策略 | 说明 |
|------|------|
| 基于时间清理 | 删除最旧消息 |
| 对话总结 | 压缩历史为摘要 |
| Observation Masking | 隐藏旧工具输出，保留调用可见 |
| 结构化记笔记 | 优先保留 reasoning traces（ACON：减 26-54% token，保 95%+ 准确率） |
| 子 Agent 委派 | 探索大量上下文，返浓缩摘要 |

**4. 验证循环设计**

| 类型 | 示例 | 特点 |
|------|------|------|
| **计算型验证** | tests / linters / type checkers | 确定性真值 |
| **推理型验证** | LLM-as-Judge | 发现语义问题，但增加延迟 |
| **引导 (Guides)** 🆕 | 行动前引导模型 | 前馈机制 |
| **感知 (Sensors)** 🆕 | 行动后观察结果 | 反馈机制 |

**5. 权限与安全架构**

| | Permissive | Restrictive |
|---|-----------|------------|
| 风格 | 多数操作自动批准 | 关键操作逐一确认 |
| 优点 | 更快 | 更安全 |
| 适用 | 个人本地工具 | 金融/医疗/生产系统 |

**6. 工具范围策略**

> 工具不是越多越好。Vercel 从 v0 中移除了 80% 工具，结果表现变好了。

核心原则：**当前步骤只暴露最少、最必要的工具。** Claude Code 通过 lazy loading 实现 95% 上下文压缩。

**7. Harness 厚度 — 多少逻辑放 harness vs 交模型**

Anthropic 倾向 **thin harness**（相信模型持续变强），定期随新版本删除规划步骤。图式框架更倾向显式控制。

> 模型和 harness 之间存在紧耦合。Claude Code 的模型学会了它训练时绑定的那套 harness。随意更换工具实现，可能导致性能下降。

### 脚手架 (Scaffolding) 比喻为什么准确

- 脚手架不会自己建楼，但没有它工人够不到高层。Harness 不直接产生智能，但没有它模型无法完成复杂任务。
- 建筑完成后脚手架会被拆掉。模型变强后 harness 的复杂度也应**逐渐下降**。
- Manus 在六个月重写了五次，每次都在删除复杂性。
- **Co-Evolution Principle：** 模型和 harness 共同进化。好的 harness 在模型能力提升时能自然吃到红利，而不需要继续增加复杂度。

### 与国内实践的结合

| 12 组件 | QQ音乐实践 | Java 微服务实践 |
|---------|-----------|----------------|
| **Tools** | Skills (34) + Agents (24) | CLI 工具化 + MCP 适配 |
| **Memory** | 三层知识体系 + Self-Refinement | CLAUDE.md + switch-config |
| **Verification** | 8 维并行审查 + 四道门禁 | verify-local.sh 自动验证 |
| **Error Handling** | 门禁让错误死在最便宜处 | — |
| **Guardrails** | 五阶段流程门禁 | Profile 隔离 + 契约检查 |
| **Context Management** | 三层知识体系 + 服务矩阵 | 依赖倒置 + 上下文最小化 |

---

## 关联文章

- [Agent Harness Engineering — AI Agent 的脚手架才是真正的工程](../agent-harness-engineering.md) — Addy Osmani（Harness 通用理论）
- [Agentic Harness Engineering (AHE)](../agentic-harness-engineering-ahe.md) — AlphaSignal（自动演化 Coding Agent 组件）
- [瘦 Harness，胖技能](../agent-engineering/thin-harness-fat-skills-garry-tan.md) — Garry Tan（Harness 架构哲学）
- [CLAUDE.md 完全指南：从个人哲学到团队工程化](../claude/claudemd-21-config-rules.md) — 多层次 CLAUDE.md 配置
- [AI Evaluation 完全入门](../ai-evals-explained.md) — 评估方法与 evals

---

*整理于 2026-05-21*
*案例一来源：腾讯云开发者公众号 · 黄欣欣（QQ音乐）*
*案例二来源：阿里云开发者公众号 · 工程师（Java 微服务 Harness）*
*理论框架来源：AlphaSignal AI × "Code as Agent Harness" 论文（UIUC × Meta × Stanford）*
