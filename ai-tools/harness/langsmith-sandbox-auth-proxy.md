---
title: "LangSmith Sandbox Auth Proxy：Agent 沙箱网络安全的生产级方案"
tags:
  - langsmith
  - langchain
  - sandbox
  - security
  - auth-proxy
  - agent-infrastructure
  - credential-management
  - egress-policy
date: 2026-05-22
source: "https://x.com/hwchase17/status/2057506580447510889"
authors: "Harrison Chase (LangChain CEO)"
---

# LangSmith Sandbox Auth Proxy：Agent 沙箱网络安全的生产级方案

> **来源：** [Harrison Chase](https://x.com/hwchase17/status/2057506580447510889) — LangChain CEO
> **核心观点：** Agent 沙箱的网络安全是 Harness 的一等公民，凭证应留在运行时之外，基础设施层控制网络策略。

---

## 一、问题：一个 Agent = 一个不受信任的开发者

企业给开发者配的笔记本电脑上有一整套安全工具：端点保护、浏览器过滤、设备管理、网络控制、密钥扫描……所有这些是为了让一个**受信的**员工不会意外泄漏凭证。

Agent 把问题放大了几个数量级。你可能正在生成**成千上万甚至上百万个"不受信任的开发者"**——它们能写代码、跑命令、装包、发网络请求，而且完全由 AI 驱动。

对于人类开发者，环境通常需要默认开放（需要探索、调试、装工具）。但对于 Agent，默认可以不同：

> 如果任务已知，网络可以更窄。如果 Agent 只需要 GitHub 和一个 LLM provider，它就不应该能访问互联网上的任意主机。

这就是沙箱网络成为 Harness 一等公民的原因。

---

## 二、Auth Proxy 架构

LangSmith Sandboxes 给 Agent 提供隔离环境来运行代码和操作文件，但隔离只是一部分——Agent 还需要调用外部 API（模型 provider、GitHub、包注册表、内部服务等）。

Auth Proxy 是控制**沙箱出口边界**的中间层：

```
沙箱内代码 → Auth Proxy → 外部服务（OpenAI/GitHub/内部API等）
                    ↓
              策略引擎（拦截/放行/注入Header）
```

**三个核心改进：**

1. **凭证不出运行时。** Agent 可以用 API 但读不到 API key，减少 prompt injection、恶意依赖、意外日志等泄露途径。
2. **网络访问显式化。** 如果 Agent 只应该和 OpenAI、Anthropic、GitHub 通信，这应该是基础设施策略，而非交给 Agent 判断。
3. **职责分离。** Agent 管任务，沙箱管隔离，Proxy 管网络授权和凭证注入，Auth Service 管用户级权限和 token 刷新。

这个分离之所以重要，是因为 Agent 本质上是**不受信的**——你不可能提前审查它们将会走的所有分支。更安全的模式是给它们约束环境，让基础设施来界定允许的行为边界。

---

## 三、凭证注入 vs 凭证暴露

### 传统做法的问题

将 API key 作为环境变量或文件放进沙箱。Agent 的每个工具调用、包安装、日志行、文件写入都可能暴露凭证。

### Auth Proxy 的做法

拦截匹配规则的出站请求并自动注入 header：

```
规则示例：
  sandbox 调用 api.openai.com     → 注入 Authorization: Bearer <workspace_secret>
  sandbox 调用 api.github.com/*   → 注入 GitHub Token
```

### Header 类型

| 类型 | 说明 |
|------|------|
| `workspace_secret` | 引用 LangSmith workspace 中存储的密钥 |
| `plaintext` | 明文存储，非敏感 header |
| `opaque` | 只写、加密存储，API 永不返回，无法通过 API 读取 |

因为控制了沙箱的网络层，这个注入是全透明的——不依赖 `HTTP_PROXY` 环境变量、不依赖语言运行时、不依赖 SDK。

> Agent 需要的是凭证的效果——调用特定 API 的能力——而不是拥有凭证本身。

### 凭证规模效应

单个沙箱泄漏 key 问题已经很大，但对于**成百上千个沙箱组成的集群**，直接把凭证放进运行时是重大的安全风险。每一次工具调用、包安装、日志记录、文件写入都是可能的凭证暴露路径。Header 注入将凭证移出了这个爆炸半径。

---

## 四、网络出口策略（Egress Policy）

凭证只是网络问题的一半。Agent 还可能安装依赖、fetch 脚本、调用 API、跟踪不受信内容中的指令。

Auth Proxy 可以在同一层定义出口策略：

| 策略 | 说明 |
|------|------|
| 放行 LLM provider API，**阻止其他一切** | 最小网络权限 |
| 仅放行 GitHub API 路径，阻止关联域名 | 精确范围控制 |
| 只允许内部包镜像，拒绝外网注册表 | 依赖供应链安全 |
| 阻止已知恶意包注册表 | 防御性策略 |
| 阻止未授权的第三方服务调用 | 数据防泄漏 |

> 如果 Agent 能 `pip install`、`npm install` 或 `curl | bash`，安全问题不只是沙箱能否隔离执行，还包括你是否能控制**代码的来源和数据的去向**。

### 包管理的特殊风险

对于 Coding Agent，这是最关键的维度。Agent 可以 `pip install`、`npm install`、`curl | bash`，这意味着它可以 fetch 并执行任意代码。安全问题是两面的：

- **输入侧：** 你能控制代码从哪里来吗？（阻止恶意注册表、强制内部镜像）
- **输出侧：** 代码能把数据发到哪里去？（阻止数据外泄）

---

## 五、动态凭证：生产级 OAuth

对于更复杂的场景——短期 OAuth 访问 token、每用户范围 token、需要刷新的凭证——Auth Proxy 支持**动态凭证回调**：

```
沙箱请求匹配 host
  → Proxy 无缓存凭证 → 调用你的回调端点 (host, port)
  → 端点返回 {"headers": {"Authorization": "Bearer xxx"}}
  → Proxy 注入并缓存（TTL 内复用）
  → 回调失败时 fail closed（拒绝请求）
```

**回调合约：**

| 场景 | JSON 响应 |
|------|-----------|
| 成功 | `{"headers": {"Authorization": "Bearer xxx"}}` |
| 失败 | 非 2xx 状态码或格式错误 → 拒绝请求 |

这允许沙箱网络层参与认证流程，而无需向沙箱暴露 refresh token 或长期凭证。回调端点返回的 headers 会在配置的 TTL 内缓存复用。

---

## 六、未来扩展方向

一旦控制了沙箱网络路径，Proxy 可以做得更多：

| 能力 | 说明 |
|------|------|
| **DNS 重映射** | 将 `pypi.org` 解析到内部 Artifactory，LLM API 指向内部网关。Agent 跑正常 install 命令，网络层自动路由到经过审批的基础设施 |
| **网络日志** | 记录 Agent 调用了哪些服务、获取了哪些包、尝试了哪些域名 → 审计追踪 |
| **请求转换** | 脱敏 PII、添加组织元数据、阻止违规负载 |

> **更广泛的洞见：** Agent 基础设施需要**位于运行时之外的、不受 Agent 指令/决策影响**的控制平面。凭证管理、网络策略、请求路由这些事，不应该交给 Agent 自己做决定。

---

## 七、架构设计原则提炼

### 原则 1：凭证即策略，而非凭证即数据

传统安全模型把凭证看作"数据"——放一个变量文件、一个 `.env` 就行。但在 Agent 沙箱场景，凭证应该是**策略**——由基础设施根据目标自动注入。

### 原则 2：Fail Closed 而非 Fail Open

当回调端点失败、格式错误、超时时，代理应该**拒绝请求**，而非不加凭证放行。安全失误应该倾向于锁死而非开放。

### 原则 3：运行时之外的信任边界

日志、凭证、网络策略、路由——这些东西如果在 Agent 运行时内部，就可能在 prompt injection 或恶意依赖中失守。把它们移到**Agent 无法影响的基础设施层**。

### 原则 4：最小网络权限

> Agent 只应该能到达它需要的目标。不是"默认允许、例外阻止"，而是"默认阻止、例外放行"。

---

> **关联：** 这与 Harness Engineering 中的 Guardrails & Safety 组件直接对应。沙箱网络是 Agent 的基础设施安全带——你可以把最强大的 Agent 放进去，只要网络出口控制住，风险就是可控的。
>
> *整理于 2026-05-22*
