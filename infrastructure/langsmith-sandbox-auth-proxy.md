# LangSmith Agent 沙箱外部网络安全访问控制：工程实践与技术综述

> 本文系统梳理了 2025-2026 年业界关于 AI Agent 沙箱访问外部网络的**安全控制策略**，聚焦于网络出口（Egress）代理、域名白名单、TLS 拦截、凭据注入等工程实践，以及相关学术研究与开源项目的最佳实践。

---

## 目录

1. [问题背景：为什么需要沙箱外部网络访问控制](#1-问题背景)
2. [控制层面总览：四层隔离体系](#2-控制层面总览)
3. [工程实践一：基于 K8s NetworkPolicy 的 Egress 控制](#3-基于-k8s-networkpolicy-的-egress-控制)
4. [工程实践二：Forward Proxy + 域名白名单实现](#4-forward-proxy--域名白名单实现)
5. [工程实践三：MITM 代理 + 凭据注入 + 内容检查](#5-mitm-代理--凭据注入--内容检查)
6. [工程实践四：Agent Workflow Firewall（AWF）实践](#6-agent-workflow-firewall-awf-实践)
7. [工程实践五：Kubernetes Agent Sandbox + gVisor](#7-kubernetes-agent-sandbox--gvisor)
8. [域名白名单策略与风险评估](#8-域名白名单策略与风险评估)
9. [开源项目与学术研究汇总](#9-开源项目与学术研究汇总)
10. [总结与推荐架构](#10-总结与推荐架构)

---

## 1. 问题背景

AI Agent（编码代理、浏览器代理、API 调用代理等）与传统应用的最大区别在于其**非确定性**——LLM 生成的代码和工具调用在运行时才能决定。这种动态性放大了安全风险：

- **Prompt Injection 攻击**：恶意注入可让代理向攻击者控制的服务泄露凭据和数据
- **数据泄露**：无约束的出口流量可能将内部代码、配置文件、API Key 发送到外部
- **命令执行**：恶意代码可能通过砂箱子进程逃逸到宿主机
- **第三方 MCP Server 投毒**：工具描述可在运行中被篡改，隐藏恶意指令

根据 HiddenLayer 2026 AI 威胁报告，已有 **1/8 的 AI 安全事故涉及 Agent 系统**；OWASP Agentic Top 10 将 ASI05（非预期代码执行）列为最高风险等级。这些威胁直接推动了**沙箱外部网络访问控制**成为 Agent 基础设施的关键能力。

---

## 2. 控制层面总览

来自 NVIDIA 2026 年实践指南、OWASP Agentic AI Top 10 以及微软 Agent Governance Toolkit 的共识——Agent 沙箱需要**四层强制隔离**：

| 层 | 控制目标 | 典型实现 |
|---|---|---|
| **1. 网络出口 (Egress)** | 代理只能访问白名单域名/端口 | Forward Proxy、K8s NetworkPolicy、MITM 代理 |
| **2. 文件系统边界 (Filesystem)** | 代理只能读写特定目录 | Landlock、Seatbelt、只读根文件系统 |
| **3. 进程隔离 (Process)** | 子进程不逃逸沙箱边界 | gVisor syscall 拦截、Firecracker microVM |
| **4. 凭据作用域 (Secrets)** | 仅注入任务所需凭据 | 运行时凭据注入、Outbound Worker 替换 |

本文重点探讨**第 1 层——网络出口控制**的工程实践与技术细节。

---

## 3. 基于 K8s NetworkPolicy 的 Egress 控制

### 3.1 gobii.ai：Per-Actor 沙箱 + K8s NetworkPolicy

**来源**：gobii.ai 在生产环境中为每个用户创建独立 K8s 命名空间，利用 **NetworkPolicy** 实现 Egress 控制。

**核心设计**：

- **Per-Actor 隔离**：每个用户/Agent 拥有独立命名空间，资源完全隔离
- **NetworkPolicy 强制 Egress**：仅允许出口流量到白名单域名解析的 IP 段
- **Proxy-only 出口**：所有外部网络请求必须经过代理（Squid / mitmproxy），代理执行域名白名单检查
- **确定性文件同步**：文件系统仅同步源代码变更，不暴露无关文件
- **审计日志**：所有出口请求记录到审计数据库

**优势**：利用 K8s 原生 NetworkPolicy 无需额外组件，结合默认拒绝策略实现最小权限。

**配置示例**：

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: agent-egress-proxy-only
  namespace: agent-{actor-id}
spec:
  podSelector:
    matchLabels:
      app: agent-sandbox
  policyTypes:
    - Egress
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: egress-proxy
      ports:
        - protocol: TCP
          port: 3128   # Proxy 端口
    - to:
        - namespaceSelector: {}
      ports:
        - protocol: UDP
          port: 53     # DNS 解析
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
          except:
            - 10.0.0.0/8      # 禁止内网访问
            - 172.16.0.0/12
            - 192.168.0.0/16
```

---

## 4. Forward Proxy + 域名白名单实现

### 4.1 INNOQ：Squid 转发代理 + nftables 强制

**来源**：INNOQ 工程师博客系列，解决开发沙箱的网络控制问题。

**架构**：

```
Agent (Lima VM)
   ↓ 所有出口流量必须通过代理
   ↓ nftables 规则：拒绝一切非代理流量
Squid Forward Proxy (host, :8888)
   ├── CONNECT 拦截（仅 TLS :443）
   ├── 域名白名单检查（dstdomain）
   └── 仅允许匹配的域名通过
```

**Squid 配置核心**：

```conf
# CONNECT-only allowlist proxy
http_port 8888
acl SSL_ports port 443
acl CONNECT method CONNECT
http_access deny CONNECT !SSL_ports
acl vmnet src 127.0.0.1/32
acl allowed_domains dstdomain "/opt/homebrew/etc/squid/allowed_domains.txt"
http_access allow vmnet CONNECT allowed_domains
http_access deny all
```

**nftables 强制**：

```nft
table inet sandbox {
    chain output {
        type filter hook output priority 0; policy drop;
        oif "lo" accept
        ct state established,related accept
        udp dport 53 accept             # DNS
        ip daddr <Host IP> tcp dport 8888 accept  # 代理
    }
}
```

**关键点**：
- 代理层工作于**域名级别**而非 IP 级别——避免 IP 变化导致规则失效
- nftables 做**强制出口代理**——即使 Agent 不认环境变量 `HTTPS_PROXY`，也无法直出
- 使用 systemd 服务确保重启后规则依然生效
- 规则加载失败时提供告警通知（PS1 提示 + 日志）

---

## 5. MITM 代理 + 凭据注入 + 内容检查

### 5.1 Cloudflare Outbound Workers

**来源**：Cloudflare 2026 年 4 月 GA 的 Sandboxes 产品，Outbound Workers 提供零信任出口控制。

**核心能力**：

| 能力 | 说明 |
|---|---|
| **出站 Worker** | 可编程 egress 代理，拦截沙箱所有出口流量 |
| **域名允许/拒绝** | Glob 模式匹配，默认拒绝模式 |
| **TLS 拦截** | 每个沙箱实例生成独立临时 CA 证书，私钥**从不进入沙箱** |
| **凭据注入** | 凭据存储在 Worker 层，沙箱只持有代理 token，Worker 在出口替换为真实值 |
| **动态策略** | 通过 `setOutboundHandler()` 运行时更改规则，无需重启沙箱 |
| **Per-request 审计** | 每次出口请求记录：沙箱 ID、目标域名、凭据注入情况、判决结果 |

**安全收益**：即使沙箱被攻破，攻击者拿到的只是无用的代理 token，而非真实凭据。

### 5.2 Project AX：MITM Proxy 凭据替换架构

**来源**：开源项目 [project-ax/ax](https://github.com/project-ax/ax) 的 `ax-web-proxy` 组件。

**架构**：

```
Agent sandbox pod（无端口 443 出口）
  ↓ HTTP_PROXY / HTTPS_PROXY
MITM Proxy (host, port 3128)
  ├── 接收 CONNECT host:443
  ├── 检查域名（session 级冻结白名单）
  ├── 终止 TLS（动态签发域名证书）
  ├── 扫描解密后流量中的 `ax-cred:<hex>` 占位符
  ├── 替换为真实凭据值
  └── 通过上游 TLS 转发到真实服务器
```

**关键设计**：

- **Session 级白名单冻结**：一次计算，会话期内不变。中间管理员的审批在**下一次会话**生效
- **凭据注册/注销**：`SharedCredentialRegistry.register(sessionId, map)` + `deregister(sessionId)`
- **双代理实例**：K8s 环境使用共享代理、Docker/local 使用 per-session 代理
- **Node.js fetch 不支持 HTTP_PROXY** 问题需要通过代理层强制

### 5.3 Pipelock：双层出口架构（基础设施层 + 内容检查层）

**来源**：Pipelab 提出的双层架构，补足 Cloudflare Outbound Worker 在内容层的不足。

**双层架构**：

```
Agent Code (Cloudflare Sandbox 内)
  ↓
Pipelock (内容扫描层)
  ├── DLP：请求体中凭据模式匹配（48 种模式）
  ├── 注入检测：响应中的 Prompt Injection 模式（25 种，6-pass）
  ├── MCP 工具投毒/漂移检测：指纹并对比每次 tools/list 响应
  └── SSRF：私有 IP + 元数据 + DNS rebinding 防护
  ↓
Cloudflare Outbound Worker (基础设施层)
  ├── 域名允许/拒绝
  ├── TLS 拦截
  ├── 凭据注入
  └── Per-request 审计
  ↓
External Service / MCP Server
```

**为何需要两层**：域名白名单只检查"去哪"，内容层检查"带了什么"和"收到了什么"。三个典型场景：
1. Agent 向 `api.github.com` 发送请求体中夹带 `~/.ssh/id_rsa`——域名白名单通过，内容 DLP 拦截
2. MCP Server 返回 `[SYSTEM] ignore previous instructions`——域名已批准，但注入检测拦截
3. MCP Server 在审查后更换工具描述——内容层指纹对比可检测漂移

---

## 6. Agent Workflow Firewall（AWF）实践

### 6.1 GitHub Agentic Workflows（gh-aw）的网络控制

**来源**：GitHub 2026 年推出的 Agentic Workflows 功能及其内置防火墙 AWF。

**配置模型**：

```yaml
network:
  allowed:
    - defaults        # GitHub, npm, PyPI 等内置域名
    - python
    - github
    - "api.my-service.com"
```

**Strict 模式的安全层级（默认开启）**：

| 层级 | 说明 |
|---|---|
| `strict: true` | 拒绝写权限（强制 safe-outputs）|
| `sandbox.agent: true` | AWF 容器沙箱 + 防火墙 |
| `network.firewall: true` | 域名级别访问控制 |
| `threat-detection: true` | 输出阶段扫描注入/密钥泄露/恶意补丁 |

**如何关闭防火墙（不推荐生产）**：

```yaml
strict: false
sandbox:
  agent: false
network:
  firewall: false
threat-detection: false
```

**注意**：关闭防火墙必须关闭 strict 模式，这将导致工作流**无法在公开仓库运行**。威胁检测依赖 AWF 沙箱，禁用沙箱时必须同时禁用威胁检测。

**设计哲学**：安全层是"连环骨牌"——每层默认开启，关闭时需每层显式确认。

---

## 7. Kubernetes Agent Sandbox + gVisor

### 7.1 Google GKE Agent Sandbox

**来源**：Google 在 KubeCon NA 2025 发布的 K8s Agent Sandbox 项目。

**核心特性**：

| 特性 | 说明 |
|---|---|
| **Sandbox CRD** | 自定义资源，表示单例、有状态、长生命周期的 Pod |
| **隔离机制** | 底层基于 gVisor（syscall 拦截），可选 Kata Containers（硬件级 VM）|
| **预热池** | SandboxTemplate + SandboxClaim 管理预启动沙箱池 |
| **Pod Snapshots** | GKE 独有，支持 CPU/GPU 工作负载的 checkpoint/restore，启动从分钟降至秒级 |
| **子秒启动** | 预热 + Pod Snapshot 实现冷启动 90% 延迟改善 |
| **网络策略集成** | 原生支持 K8s NetworkPolicy 做 Egress 控制 |

**设计转变**：

Agent 沙箱与传统容器不同：
- **有状态运行**：代理会话需要持续的内存/磁盘状态
- **暂停/恢复**：可 checkpoint 状态、挂起闲置沙箱、需要时快速唤醒
- **稳定身份**：每个沙箱有稳定 Pod 身份和持久化存储
- **大规模弹性**：数万沙箱并行调度

### 7.2 Alibaba OpenSandbox 的 Egress Sidecar

**来源**：Alibaba 的 OpenSandbox 开源项目，其中 Egress 组件提供 FQDN 级别出口控制。

Egress sidecar 与沙箱应用容器共享网络命名空间，通过声明式网络策略实现精确的域名级出口控制。这是业内少数针对 Agent 场景构建的通用沙箱出口控制组件。

---

## 8. 域名白名单策略与风险评估

### 8.1 PromptArmor 风险评估框架

**来源**：PromptArmor LLM Threat Research Team 发布的域名白名单评估指南。

核心原则：**白名单上的域名是 Agent 在 Prompt Injection 条件下会信任的域名**。加入白名单一个域名，意味着**允许被污染的 Agent 向该域名发送数据**。

**高风险模式**：

| 域名类型 | 风险 | 缓解策略 |
|---|---|---|
| `*.npmjs.org` | 用户上传内容，攻击者可发布包接收数据 | 用精确域名，限制写入 |
| `github.com` / `raw.githubusercontent.com` | 任何人都可发布内容，即是 C2 通道 | 只允许读取仓库，拒绝 API 写入 |
| `docs.google.com` | Google Forms 提交 URL 可做数据泄露通道 | 仅允许特定路径 |
| `*.amazonaws.com` | 攻击者可注册 `attacker.s3.amazonaws.com` | 精确到单个 bucket |
| CDN / 托管服务 | 用户生成内容 = 恶意软件分发/命令控制 | 评估内容可信度 |

**评估 checklist**：

1. 该服务是否允许用户生成可写的 URL？→ 攻击者可注册可控站点
2. 是否有 API 可被攻击者利用上传数据？→ 提供凭据即提供泄露通道
3. 是否有表单提交功能可用于数据泄露？→ 如 Google Forms
4. 域名本身是否被可信方控制？→ 个人网站不应进入敏感环境白名单

**原则**：避免过度通配符 (`*.azure.com` 恶化到 `attacker.cloudapp.azure.com`)；偏向精确域名；拒绝一切不必要的。

### 8.2 NVIDIA 指导原则

- 使用 HTTP 代理 + IP 地址 + 端口的三重控制
- 精确定义 Agent 允许调用的外部 API
- 通过 egress 代理或网络策略强制执行
- 对所有非白名单出口流量发出告警

---

## 9. 开源项目与学术研究汇总

### 9.1 开源沙箱/出口控制项目

| 项目 | 分类 | 隔离边界 | 出口控制方式 |
|---|---|---|---|
| **[K8s Agent Sandbox](https://github.com/kubernetes-sigs/agent-sandbox)** | K8s 原生 | gVisor/Kata VM | K8s NetworkPolicy + CRD |
| **[Alibaba OpenSandbox](https://github.com/alibaba/OpenSandbox)** | 通用沙箱 | 容器隔离 | Egress Sidecar（FQDN 级别） |
| **[E2B](https://github.com/e2b-dev/E2B)** | 云端沙箱 | 容器/VM 隔离 | SDK 控制 + 云环境网络隔离 |
| **[Project AX](https://github.com/project-ax/ax)** | Agent 平台 | 容器沙箱 | MITM Proxy + 凭据替换 |
| **[LLM Sandbox](https://github.com/vndee/llm-sandbox)** | 轻量代码沙箱 | 容器隔离 | 可配置安全策略 |
| **[Microsandbox](https://github.com/zerocore-ai/microsandbox)** | microVM | 硬件隔离 microVM | 网络策略配置 |
| **[ERA](https://github.com/BinSquare/ERA)** | 本地 microVM | 硬件隔离 | 本地 egress 控制 |
| **[Pipedream Code Sandbox](https://github.com/alex000kim/skypilot-code-sandbox)** | 自托管执行 | Docker 沙箱 | 域名白名单 + Token 认证 |

### 9.2 学术研究

| 研究 | 年份 | 核心贡献 |
|---|---|---|
| **ToolSandbox (Apple)** | 2024 | 状态化工具执行 + 用户模拟器，评估 LLM 工具使用安全性 |
| **ToolEmu** | 2024 | LM 模拟沙箱，可扩展的 Agent 风险测试框架 |
| **HAICOSYSTEM** | 2025 | Agent Agent 系统的安全组织结构研究 |
| **Eunomia 架构综述** | 2026 | 系统性综述 Agent 隔离/集成/治理三大方向，含 Table 1 项目对比 |

### 9.3 OS 级别沙箱

| 机制 | 平台 | 特点 |
|---|---|---|
| **macOS Seatbelt** | macOS | 默认拒绝策略，策略文件控制文件/网络/系统调用 |
| **Linux Landlock + Seccomp** | Linux | 基于 capability 的文件系统限制 + syscall 过滤，粒度更细 |
| **Codex CLI 权限模式** | 跨平台 | Read-Only / Auto / Full Access 三级映射到 Seatbelt/Landlock |

---

## 10. 总结与推荐架构

### 10.1 整体架构建议

对于生产环境 Agent 沙箱外部网络访问控制，推荐采用**多层防御**架构：

```
┌──────────────────────────────────────────────────┐
│                  Agent 沙箱                         │
│  (gVisor / Firecracker / K8s Sandbox CRD)        │
│   - 无直接外部网络（默认拒绝）                      │
└────────────────────┬─────────────────────────────┘
                     │ HTTPS_PROXY=127.0.0.1:8888
                     ▼
┌──────────────────────────────────────────────────┐
│           内容检查层 (可选，高安全场景)              │
│  Pipelock / 自建 DLP 代理                          │
│   - 凭据泄露检测 (48+ patterns)                    │
│   - Prompt Injection 检测                          │
│   - MCP 工具描述指纹/漂移检测                      │
│   - SSRF/私有IP防护                                │
└────────────────────┬─────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────┐
│          基础设施层 Egress Proxy                   │
│  Squid / Cloudflare Outbound Worker / mitmproxy   │
│   - 域名白名单（精确，避免通配符）                  │
│   - TLS 拦截（MITM 模式）                          │
│   - 凭据注入（沙箱内仅有 proxy token）              │
│   - 每请求审计日志                                │
└────────────────────┬─────────────────────────────┘
                     │
                     ▼
              External Services
          (GitHub, npm, PyPI, API...)
```

### 10.2 不同场景的推荐方案

| 场景 | 推荐方案 | 安全等级 |
|---|---|---|
| 本地开发环境（单人） | Lima VM + nftables + Squid allowlist | ⭐⭐⭐ |
| 小型团队（K8s 轻量） | K8s NetworkPolicy + 容器内 Squid proxy | ⭐⭐⭐⭐ |
| 中等规模生产 | K8s Agent Sandbox + gVisor + NetworkPolicy + Outbound Proxy | ⭐⭐⭐⭐⭐ |
| 金融/医疗（强合规） | Firecracker microVM + MITM Proxy + 内容 DLP + 每一层审计 | ⭐⭐⭐⭐⭐⭐ |
| SaaS 平台（多租户） | Per-actor Namespace + Egress Proxy + Cloudflare Outbound Worker | ⭐⭐⭐⭐⭐ |

### 10.3 核心原则总结

1. **默认拒绝**：所有 egress 默认 block，仅显式允许的域名可通过
2. **精确而非通配**：`api.specific-service.com` 好于 `*.amazonaws.com`
3. **多层而非单点**：基础设施层（去哪）+ 内容检查层（是什么）+ 凭据层（用谁的凭据）
4. **凭据永不进沙箱**：使用 proxy token 机制，沙箱内仅持有代理凭据
5. **Session 级策略冻结**：白名单在会话开始时确定，中间不变
6. **审计先行**：所有出口请求记录到审计系统，便于事后追踪和合规
7. **强制路由**：用 nftables/iptables 强制所有出口使用代理，不依赖 Agent 配合

---

## 参考来源

1. [gobii.ai - How We Sandbox AI Agents in Production](https://gobii.ai/blog/agent-sandbox)
2. [NVIDIA - Practical Security Guidance for Sandboxing Agentic Workflows](https://developer.nvidia.com/blog/practical-security-guidance-for-sandboxing-agentic-workflows-and-managing-execution-risk/)
3. [Google Cloud - Agentic AI on Kubernetes and GKE](https://cloud.google.com/blog/products/containers-kubernetes/agentic-ai-on-kubernetes-and-gke)
4. [GitHub Agentic Workflows AWF Reference](https://github.github.com/gh-aw/reference/sandbox/)
5. [INNOQ - I sandboxed my coding agents. Now I control their network.](https://www.innoq.com/en/blog/2026/03/dev-sandbox-network/)
6. [Cloudflare Sandboxes Outbound Workers](https://developers.cloudflare.com/changelog/post/2026-04-13-sandbox-outbound-workers-tls-auth/)
7. [Pipelab - Cloudflare Sandboxes and Pipelock: Two-Layer Egress Control](https://pipelab.org/learn/cloudflare-sandboxes-pipelock/)
8. [PromptArmor - What domains should I add to my allowlist?](https://www.promptarmor.com/resources/what-domains-should-i-add-to-my-allowlist)
9. [Project AX - ax-web-proxy MITM Proxy Architecture](https://github.com/project-ax/ax)
10. [BeyondScale - AI Agent Sandboxing: Enterprise Security Guide 2026](https://beyondscale.tech/blog/ai-agent-sandboxing-enterprise-security-guide)
11. [Eunomia.dev - Architectures for Agent Systems: A Survey](https://eunomia.dev/blog/2026/01/11/architectures-for-agent-systems-a-survey-of-isolation-integration-and-governance/)
12. [Alibaba OpenSandbox - Egress Sidecar](https://github.com/alibaba/OpenSandbox)
13. [OWASP Agentic AI Top 10 (Dec 2025)](https://genai.owasp.org/)
14. [Codex CLI Sandbox - macOS Seatbelt + Linux Landlock](https://pierce.dev/notes/a-deep-dive-on-agent-sandboxes)
15. [HiddenLayer 2026 AI Threat Landscape Report](https://hiddenlayer.com/)
