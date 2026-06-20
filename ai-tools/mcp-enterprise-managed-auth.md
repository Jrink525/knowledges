---
title: "MCP 企业托管授权 (EMA)：零接触 OAuth"
tags:
  - mcp
  - auth
  - enterprise
  - oauth
  - sso
  - okta
date: 2026-06-20
source: "https://blog.modelcontextprotocol.io/posts/enterprise-managed-auth/"
authors: "MCP Blog"
---

# MCP 企业托管授权：零接触 OAuth

> **来源：** [Enterprise-Managed Authorization: Zero-touch OAuth for MCP](https://blog.modelcontextprotocol.io/posts/enterprise-managed-auth/) — MCP Blog

---

MCP 的 **Enterprise-Managed Authorization (EMA)** 扩展已正式稳定。企业可以集中管理 MCP 服务器的授权，最终用户只需一次登录即可访问所有已连接的 MCP 服务器。

Anthropic、Microsoft、Okta 以及越来越多的 MCP 服务器正在采用此扩展。

---

## 痛点：按用户逐级授权摩擦太大

MCP 的标准授权模型面向个人消费者场景设计的——由用户个体决定谁碰他们的数据。但在企业部署中根本跑不通：

| 问题 | 后果 |
|------|------|
| 每个员工需要逐个授权每个服务器 | 入职就是手动连服务的马拉松 |
| 安全团队无法执行统一策略 | 访问权限由每个用户各自授权，无中央控制，无审计 |
| 工作账号和个人账号混在一起 | 用户可能拿个人账号连工作工具，无法强制使用企业身份 |

这导致 MCP 在企业落地缓慢，各团队被迫自造脆弱的变通方案。

---

## 核心方案：一次授权，全局继承

EMA 让企业的**身份提供商（IdP）** 成为 MCP 服务器访问的权威决策者：

1. 管理员统一配置策略
2. 用户用已有企业身份登录 MCP Host
3. IdP 基于群组、角色和条件访问规则决定授权结果

### 技术细节

底层流程核心是 **ID-JAG（Identity Assertion JWT Authorization Grant）**——一个 OAuth 扩展标准：

```
用户单点登录 MCP Host
  → Host 从 IdP 获取 Identity Assertion JWT
    → Host 用此 JWT 向 MCP 服务器的授权服务器换取 access token
      → 用户直接获得访问权限，无需经过每个 server 的同意页面
```

### 三个天然优势

1. **一次授权，全局继承** — 管理员启用服务器的同时，用户自动获得基于其群组和角色的访问权限
2. **集中策略和审计** — 所有访问决策在 IdP 管理控制台，单个审计轨迹覆盖所有连接器
3. **消除公私混用** — 去掉交互式账号选择步骤，防止个人/企业账户之间的数据误流

---

## 首批采用者

### 身份提供商
- **Okta** 是第一个支持的身份提供商。组织可通过 Okta 的 Cross App Access (XAA) 配置 MCP 访问

### 客户端
- **Anthropic** 已在 Claude 的共享 MCP 层中实现 EMA。管理员可以在 Claude、Claude Code、Cowork 中统一授权
- **Visual Studio Code** 已在 v1.123 中添加 EMA 支持

### 服务器
| 支持 | 正在接入 |
|------|---------|
| Asana | Slack |
| Atlassian | 更多 |
| Canva | |
| Figma | |
| Granola | |
| Linear | |
| Supabase | |

---

## 关键引述

> "MCP 的势头非常惊人，但当我们迈向互联的 AI 协作时，安全不能是事后诸葛。将 Cross App Access 协议嵌入 MCP 作为 EMA 扩展，我们把身份变成了一个集中治理层。"
> — Aaron Parecki, Director of Identity Standards, Okta

> "一键登录后所有 MCP 连接器自动配置好了——这相当 magic。"
> — Tom Moor, Head of Engineering, Linear

---

## 如果你想做集成

- **规格文档：** [Enterprise-Managed Authorization 页面](https://modelcontextprotocol.io/extensions/auth/enterprise-managed-authorization)
- **源码 & 草案：** [ext-auth 仓库](https://github.com/modelcontextprotocol/ext-auth)
- **讨论群：** [EMA Interest Group](https://modelcontextprotocol.io/community/interest-groups/enterprise-managed-authorization)

---

## 对你 Agent 开发的意义

你的 Agent（Spring AI / Pydantic AI / Claude Agent SDK）都可能通过 MCP 对接外部服务。EMA 的出现意味着：

- **用户不用每次开新工具都弹 OAuth 授权页** —— 比如投研 Agent 需要同时读 Linear + Figma + Supabase，一次登录全搞定
- **安全团队能管住 Agent 的访问范围** —— Agent 只能访问其角色允许的数据
- **Agent 部署时不用自己处理凭证** —— 企业 IdP 已经做好了

这指向一个趋势：**MCP 正在从"单机插件协议"演变为"企业级 Agent 基础设施协议"**。

---

> *Processed on 2026-06-20 from https://blog.modelcontextprotocol.io/posts/enterprise-managed-auth/*
