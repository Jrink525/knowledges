---
title: "从零搭建 HTTP 服务器完全指南"
tags:
  - java
  - http
  - tcp
  - networking
  - backend
  - tutorial
date: 2026-03-02
source: "https://x.com/avrldotdev/status/2028398714071490972"
authors: "avrl (@avrldotdev)"
---

# 从零搭建 HTTP 服务器完全指南

> **来源：** [A Beginner's Guide to building an HTTP Server from Scratch](https://x.com/avrldotdev/status/2028398714071490972) — @avrldotdev

![cover](../image/http-server-from-scratch-1.jpg)

用 Java 从零写一个 HTTP/1.1 服务器，500 行代码搞定。

---

## 前置知识

- 需要了解 Java（但概念可迁移到任何语言）
- 基本的编程和 OOP 知识
- 不建议用 JS/TS 跟学

---

## 核心概念

### 1. TCP

TCP（传输控制协议）是构建在 IP 之上的可靠、有序、字节流协议。

- TCP 只理解字节，其他什么都不懂
- **关键点：** TCP **不保证**一次 `read()` 调用就能拿到完整消息——你可能会分多次拿到字节流中的片段
- 三次握手：SYN → SYN-ACK → ACK
- 保证有序送达、无重复、通过 checksum 防篡改

### 2. UDP

UDP 是另一种传输层协议，但无连接、不保证送达、不保证顺序、没有重复保护。更快但更不可靠。

适用场景：视频通话、直播等允许丢包的应用——**延迟比完整性更重要**。

### 3. HTTP

HTTP 是**基于文本的应用层协议**，运行在 TCP 之上。

核心元素：**请求、响应、头部、正文、状态码、语义**

**HTTP 请求的结构（RFC 9112 §1.2）：**

```
METHOD /path HTTP/1.1\r\n
Header1: value1\r\n
Header2: value2\r\n
\r\n
body content...
```

> `CRLF = \r\n`，是 HTTP 请求和响应各部分之间的分隔符。

---

## 项目结构

```
src/
  cmd/
    HTTPServerMain.java          # 入口
  internal/
    server/
      Server.java                # TCP 服务器核心
      Handler.java               # 处理器接口
    request/
      Request.java               # 请求对象 + 状态机解析
      RequestLine.java           # 请求行
      RequestParser.java         # 请求行解析器
      ParserState.java           # 解析状态枚举
    headers/
      Headers.java               # 头部（大小写不敏感 Map）
      HeadersResult.java         # 解析结果
    response/
      ResponseWriter.java        # 响应工具类
      Writer.java                # 状态化写入器
      StatusCode.java            # 状态码枚举
```

---

## 12 步搭建 HTTP 服务器

### Step 1：建立项目结构

按上述目录创建各大文件夹和包。

### Step 2：创建 TCP 服务器

**Server.java 骨架：** 使用 `ServerSocket`（Java 的 TCP socket）+ `AtomicBoolean`（多线程安全地追踪服务器状态）。

- 每个连接创建新线程——简单场景够用，但高并发不扩展
- 使用静态工厂方法 `createAndStart(port, handler)` 启动服务器
- `accept()` 循环持续接受连接，每个连接分配新线程
- 优雅关闭：先设 flag，再关闭 socket

**Handler.java（接口）：** 解耦路由处理——服务器只负责连接和状态，路由交给 Handler。

```java
@FunctionalInterface
public interface Handler {
    void handle(Writer writer, Request request) throws Exception;
}
```

> 这就是 **SOLID 单一职责原则**——服务器不该处理路由。

### Step 3：解析 HTTP 请求——状态机架构

**关键前提：** TCP 给的是字节流片段，必须正确处理部分读取。

**解析状态机：** `INITIALIZED → PARSING_HEADERS → PARSING_BODY → DONE`

**ParserState.java（枚举）：**

```java
public enum ParserState {
    INITIALIZED,
    PARSING_HEADERS,
    PARSING_BODY,
    DONE
}
```

**RequestLine.java：** 存储 method、requestTarget、httpVersion
**RequestParser.java：** 按空格分割请求行，严格验证 3 部分、method 必须大写、版本为 HTTP/1.1

### Step 4：解析头部

Headers 本质上是一个大小写不敏感的 Map：

- 所有 key 归一化为小写——"Content-Type" 和 "content-type" 是同一个 header
- 字节以 CRLF 分割行，空行表示头部结束
- 重复 key 合并值：`key: "value1, value2,..."`
- header name 只能包含规范允许的特殊字符

### Step 5：Request 对象——状态机串联

把各部分组合成一个完整的**状态机**：

| 方法 | 作用 | 状态转换 |
|------|------|---------|
| `setRequestLine()` | 设置请求行 | INITIALIZED → PARSING_HEADERS |
| `setHeaders()` | 设置头部 | PARSING_HEADERS → PARSING_BODY |
| 累积 body | 按 Content-Length 累积字节 | PARSING_BODY → DONE |

**Body 解析要点：** 分多次 `read()` 累积字节，body 必须精确等于 Content-Length 的长度——不多不少。GET 请求没有 Content-Length（没有 body）。

### Step 6：从流中读取

**RequestFromReader.java：** 从 TCP 输入流读字节 → 喂给 Request 解析器。

- 缓冲区从 1KB 开始，按需倍增到 64KB 上限
- 每次读取后，将已解析字节移到缓冲区前端
- EOF 在解析完成前到达 → 错误

### Step 7：响应——状态码

**StatusCode.java（枚举）：** HTTP 状态码 → 对应原因短语（OK、BAD_REQUEST、INTERNAL_SERVER_ERROR 等）。

### Step 8：响应——ResponseWriter 工具

静态工具方法，遵循 HTTP 响应格式：

- `writeStatusLine()` — `HTTP/1.1 200 OK\r\n`
- `getDefaultHeaders()` — 默认 header（`connection: close` 简化实现，每个连接一个请求）
- `writeHeaders()` — 每个 header 一行，空行结束

### Step 9：状态化 Writer

**Writer.java——又是一个状态机：**

| 状态 | 允许的操作 |
|------|-----------|
| INITIALIZED | `writeStatus()` |
| STATUS_WRITTEN | `writeHeaders()` |
| HEADERS_WRITTEN | `writeBody()` |
| BODY_WRITTEN | 结束 |

> 确保响应按正确顺序写出——状态行 → 头部 → 正文。

### Step 10：完善 Server 的 handle 方法

把请求解析和响应写入串联起来：

1. 从 socket 获取 InputStream
2. 用 `RequestFromReader` 解析请求
3. 解析失败 → 400 Bad Request
4. 调用 Handler 处理请求
5. Handler 抛异常 → 500 Internal Server Error

### Step 11：主入口

**HTTPServerMain.java：**

- 创建 Server 并传入 Handler（方法引用）
- 注册关闭钩子优雅处理 Ctrl+C
- Handler 中根据 path 分发路由（`/` → 主页、`/yourproblem` → 404、`/myproblem` → 200）
- 用 Writer 按序写出响应

### Step 12：运行测试

```bash
curl -v http://localhost:42069/
curl -v http://localhost:42069/yourproblem
curl -v http://localhost:42069/myproblem
```

---

## Bonus：分块传输编码

现实中服务器不能一次性把整个 response body 写出去——body 可能太大。HTTP 支持分块传输编码（Chunked Transfer Encoding），把数据切成块发送，每块前带有十六进制大小前缀。

在 Writer 中新增状态：
- `writeChunkedBody()` — 写入一块数据（`<hex-size>\r\n<data>\r\n`）
- `writeChunkedBodyDone()` — 写入终止块（0 大小）

---

## 最终项目目录

```
src/
  cmd/
    HTTPServerMain.java
  internal/
    headers/
      Headers.java
      HeadersResult.java
    request/
      ParserState.java
      Request.java
      RequestLine.java
      RequestParser.java
      RequestFromReader.java
    response/
      ResponseWriter.java
      StatusCode.java
      Writer.java
    server/
      Handler.java
      Server.java
```

> 完整代码约 **500 行**——一个可以工作的 HTTP/1.1 服务器。

---

## 拓展方向

- Keep-alive 连接
- 更多 HTTP 方法（POST、PUT、DELETE）
- 更好的错误处理
- 连接池

**完整代码仓库：** [github.com/viralcodex/http-server](https://github.com/viralcodex/http-server)

**推荐学习资源：**
- Lane（@wagslane）和 ThePrimeagen 的 YouTube 课程：[https://youtu.be/FknTw9bJsXM](https://youtu.be/FknTw9bJsXM)
- boot.dev 免费课程：[https://www.boot.dev/lessons/b0cebf37](https://www.boot.dev/lessons/b0cebf37-7151-48db-ad8a-0f9399f94c58)

---

*整理于 2026-06-23，来自 @avrldotdev 的 X 长文*
