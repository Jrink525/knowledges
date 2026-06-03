---
tags: [openclaw, weixin, wechat, clawbot, network, firewall, ilink, 网络配置, 白名单, 防火墙, 微信接入, 企业网络]
description: openclaw-weixin 插件接入微信 ClawBot 所需的网络策略、域名白名单、通信模式详解
created: 2026-05-11
author: Jarvis II
---

# openclaw-weixin 网络配置要求

> 公司 OpenClaw 接入微信 ClawBot（`@tencent-weixin/openclaw-weixin`）所需的网络策略。

---

## 协议

| 协议 | 用途 |
|------|------|
| **HTTPS (TCP 443)** | 所有 API 通信、CDN 传输 |
| **HTTP (TCP 80)** | 二维码显示（终端本地，通常不需要代理放行） |
| **DNS** | 域名解析 |

## 需要放行的域名

### 🎯 核心（必须）

| 域名 | 用途 |
|------|------|
| `ilinkai.weixin.qq.com` | **iLink API 基址** — 登录、长轮询收消息、发消息、获取上传参数等全部核心 API |
| `novac2c.cdn.weixin.qq.com` | **微信媒体 CDN** — 图片、视频、文件的上传和下载（不开则媒体功能不可用，文字正常） |

### 🛠️ 安装部署（仅在首次安装/升级时需要）

| 域名 | 用途 |
|------|------|
| `registry.npmjs.org` | 安装 npm 包 `@tencent-weixin/openclaw-weixin` |
| `www.npmjs.com` | 查询包信息（可选） |

### 📖 参考（可选）

| 域名 | 用途 |
|------|------|
| `github.com` | 查看插件源码 / README |
| `docs.openclaw.ai` | 官方文档 |

## 通信模式

**不是 WebSocket，也不是 Webhook，而是长轮询（Long-Polling）：**

1. 客户端发起 HTTPS POST 请求到 `ilinkai.weixin.qq.com/getupdates`
2. 服务端挂起连接，最长 **35 秒**
3. 有新消息或超时后返回响应
4. 客户端收到后立即发起下一个请求

**对网络的要求：**
- 只需要**出站** HTTPS 连接，不需要入站端口映射
- 需要保持长期连接不断开
- 如果走 HTTP 代理，代理超时时间建议设为 **> 60 秒**，避免长轮询被提前掐断

## 详细 API 端点

基址：`https://ilinkai.weixin.qq.com`

| 路径 | 方法 | 说明 |
|------|------|------|
| `/get_bot_qrcode?bot_type=3` | GET | 获取登录二维码 |
| `/get_qrcode_status?qrcode=...` | GET | 轮询微信扫码状态 |
| `/getupdates` | POST | 长轮询拉取新消息 |
| `/sendmessage` | POST | 发送文本 / 图片 / 视频 / 文件 |
| `/getconfig`  | POST | 获取账号配置（typing ticket 等） |
| `/sendtyping` | POST | 显示/取消「对方正在输入」 |
| `/getuploadurl` | POST | 获取 CDN 上传预签名参数 |

## 请求头说明（后端对接用）

所有业务请求需携带以下 HTTP Headers：

```
Content-Type: application/json
AuthorizationType: ilink_bot_token
Authorization: Bearer <bot_token>
X-WECHAT-UIN: <随机 uint32 的 base64 编码>
```

## 最低防火墙配置（公司 IT 申请单用）

```
出站 HTTPS (443) 放行：
  ilinkai.weixin.qq.com
  novac2c.cdn.weixin.qq.com

附加：首次安装时临时放行（安装后可关）：
  registry.npmjs.org

备注：
  - 不需入站端口
  - 长轮询连接可能持续挂起 35 秒，代理需支持长连接
  - 本服务使用腾讯 iLink Bot API，是微信官方开放协议，非第三方逆向手段
```

---

## 参考来源

- OpenClaw 微信频道文档：<https://docs.openclaw.ai/zh-CN/channels/wechat>
- 腾讯 iLink Bot API 协议说明：<https://www.wechatbot.dev/zh/protocol>
- GitHub 仓库：<https://github.com/Tencent/openclaw-weixin>
