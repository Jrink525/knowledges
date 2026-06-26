# REST API Design for Long-Running Tasks

> 来源：restfulapi.net
> 原文：[REST API Design for Long-Running Tasks](https://restfulapi.net/rest-api-design-for-long-running-tasks/)
> 收录维度：**C — 实时推送 vs 轮询**

---

## 概述

当 REST API 需要处理长时间运行的操作（无法在 HTTP 请求超时内完成）时，需要异步响应模式。本文介绍多种标准设计模式。

## 核心原则

HTTP 请求应有合理的超时（通常 30-60s）。对于耗时更久的操作，不使用同步等待，而是采用异步模式。

## 四种设计模式

### 1. Polling（轮询模式）

最常用的模式，与引子文章一致。

**流程**：
```
POST /api/tasks → 202 Accepted + Location: /api/tasks/{id}
                     ↓
Client 定期 GET /api/tasks/{id}
                     ↓
                    200 OK + 当前状态
```

**实现**：

```http
# 客户端提交
POST /api/tasks
Content-Type: application/json

{"name": "data-export", "params": {...}}

# 响应
HTTP/1.1 202 Accepted
Location: /api/tasks/abc-123
Retry-After: 5

# 客户端轮询
GET /api/tasks/abc-123

# 响应（处理中）
HTTP/1.1 200 OK
Content-Type: application/json
{
  "taskId": "abc-123",
  "status": "PROCESSING",
  "progress": 45,
  "message": "Processing step 5/11"
}

# 响应（完成）
HTTP/1.1 200 OK
Content-Type: application/json
{
  "taskId": "abc-123",
  "status": "COMPLETED",
  "progress": 100,
  "result": { "downloadUrl": "/files/export-abc-123.csv" }
}
```

**HTTP 状态码**：
- `202 Accepted` — 任务已接受，尚未完成
- `200 OK` — 任务完成，响应体包含结果
- `303 See Other` — 可选方案，重定向到结果资源

**最佳实践**：
- `Retry-After` header 指示建议轮询间隔
- 指数退避，不要固定频率
- 任务完成后可返回 303 重定向到结果资源

### 2. Callback / Webhook（回调模式）

**流程**：
```
POST /api/tasks + callbackUrl
→ 202 Accepted
→ 处理完成后，服务器 POST 结果到 callbackUrl
```

**实现**：

```http
# 客户端提交 + 注册回调
POST /api/tasks
Content-Type: application/json

{
  "name": "data-export",
  "params": {...},
  "callbackUrl": "https://client.example.com/webhook/task-complete"
}

# 响应
HTTP/1.1 202 Accepted
Location: /api/tasks/abc-123
```

任务完成后，服务器调用 callback URL：

```http
POST /webhook/task-complete
Content-Type: application/json

{
  "taskId": "abc-123",
  "status": "COMPLETED",
  "result": { "downloadUrl": "/files/export-abc-123.csv" }
}
```

**最佳实践**：
- 回调 URL 应为 HTTPS
- 回调签名验证（HMAC 或 JWT）
- 重试机制（回调失败后重试）
- 超时后备（回调未达时提供轮询端点）

### 3. Long Polling（长轮询）

客户端保持连接打开，服务器在有数据时立即返回，否则等待。

```
GET /api/tasks/abc-123/poll?timeout=30

→ 服务器保持连接打开（最多 30s）
→ 任务完成时立即返回
→ 超时则返回 304 Not Modified，客户端重新发起
```

**优点**：比轮询更实时，比 WebSocket 简单
**缺点**：服务器资源占用较高，不适合高频场景
**适用**：低频度但需要即时性的场景

### 4. Server-Sent Events (SSE)

**流程**：
```
GET /api/tasks/abc-123/stream
Accept: text/event-stream
→ 服务器持续推送事件
```

详见：C2-sse-spring-boot-obregon-medium.md

## 模式对比

| 模式 | 实时性 | 服务器开销 | 客户端复杂度 | 适用场景 |
|------|--------|-----------|-------------|---------|
| 轮询 | 低 | 低 | 低 | 简单场景，低频检查 |
| 回调 | 中 | 中 | 中 | 任务完成后通知 |
| 长轮询 | 中 | 中 | 中 | 需要轻度实时 |
| SSE | 高 | 中 | 低 | 单向实时推送 |
| WebSocket | 高 | 高 | 高 | 双向实时通信 |

## REST API 最佳实践

### 统一的任务资源模型

```json
{
  "taskId": "uuid",
  "status": "PENDING|PROCESSING|COMPLETED|FAILED|CANCELLED",
  "progress": 0-100,
  "message": "当前状态描述",
  "createdAt": "ISO-8601",
  "updatedAt": "ISO-8601",
  "result": {},
  "error": {}
}
```

### GET /api/tasks 多条件查询

```http
GET /api/tasks?status=PROCESSING&createdAfter=2026-06-01&page=0&size=20
```

### 取消任务

```http
DELETE /api/tasks/{id}
→ 204 No Content
```

或使用幂等更新（推荐）：

```http
PATCH /api/tasks/{id}
Content-Type: application/json

{"action": "CANCEL"}
```

---

## 适用于引子文章的建议

引子文章使用轮询模式，考虑渐进式演进：

1. **短期**：保持轮询，加入 `Retry-After` + 指数退避
2. **中期**：增加 SSE 端点（/api/tasks/{id}/stream）作为轮询的补充
3. **长期**：根据业务需要决定是否需要回调/WebSocket
