---
title: "Spring Boot + Netty + WebSocket 实战：从原理到项目，一篇文章彻底搞懂"
tags:
  - spring-boot
  - netty
  - websocket
  - real-time
  - java
date: 2026-06-12
source: "综合整理自多个来源"
authors: "综合整理"
---

# Spring Boot + Netty + WebSocket 实战指南

> 从原理到完整项目，让你真正掌握 Netty 和 WebSocket，而不是只会调 API。

---

## 一、为什么需要 Netty + WebSocket？

### 1.1 WebSocket 解决了什么问题

传统 HTTP 是"请求-响应"模式——客户端不请求，服务端不能主动推数据。WebSocket 提供**全双工持久连接**，服务端可以随时主动推送。

常见场景：

| 场景 | 为什么需要 WebSocket | 不用它的代价 |
|------|---------------------|-------------|
| **即时聊天** | 消息需要毫秒级送达对方 | 轮询延迟高、浪费带宽 |
| **协作编辑** | 操作变换需要实时同步 | 冲突无法及时解决 |
| **实时仪表盘** | 监控指标秒级刷新 | 页面需要手动刷新或频繁轮询 |
| **游戏同步** | 状态更新需<100ms | 玩家体验卡顿 |
| **流式 AI 响应** | LLM 输出 token 逐步推送 | 用户等待完整响应 |
| **行情推送** | 股价/币价实时变动 | 丢失交易机会 |
| **通知推送** | 后台事件主动告知用户 | 用户必须手动刷新 |

### 1.2 为什么用 Netty，而不是 Spring 自带的 WebSocket

Spring Boot 自带两种 WebSocket 方案：

**方式一：原生 WebSocketHandler（基于 Tomcat NIO）**
- 简单，适合小规模
- Tomcat 默认线程池 200，每个连接占 1MB 线程栈
- 百万连接场景直接爆炸

**方式二：STOMP over WebSocket**
- 提供了 pub/sub 路由、@MessageMapping 注解
- 适合有消息代理（RabbitMQ）的多实例部署
- 但底层仍是 Tomcat 线程模型

**Netty 的核心优势：**

| 对比项 | Spring Boot 原生 (Tomcat) | Netty |
|--------|--------------------------|-------|
| 线程模型 | 1 连接 1 线程（或 NIO 复用） | Reactor 模式，Boss-Worker 组 |
| 百万连接 | 需要 1000+ GB 线程栈 | 几十个线程即可支撑 |
| 吞吐量 | 中等 | 极高（零拷贝、池化缓冲区） |
| 控制力 | 封装层次高，难调优 | pipeline 完全可控 |
| 生态系统 | 仅 Web | Dubbo/RocketMQ/gRPC 共用 |

**一句话总结：Spring Boot 原生的 WebSocket 适合小项目快速开发；Netty 适合高并发、低延迟、需要精细控制的生产系统。**

---

## 二、Netty 核心概念速通（够用就行）

### 2.1 Reactor 线程模型

Netty 用的是"多线程 Reactor"模式：

```
                  ┌──────────────┐
                  │   Boss Group  │  (1个线程，负责 accept)
                  │  NioEventLoop │
                  └──────┬───────┘
                         │ 接受连接
                         ▼
                  ┌──────────────┐
    ┌────────────▶│ Worker Group  │◀────────────┐
    │             │ NioEventLoop1 │             │
    │             ├──────────────┤             │
    │             │ NioEventLoop2 │             │
    │             ├──────────────┤             │
    │             │ NioEventLoop3 │             │
    │             │    ......     │             │
    │             └──────────────┘             │
    │                                          │
    │  每个 EventLoop 绑定一个 Thread           │
    │  每个 Channel 绑定一个 EventLoop           │
    │  一个 EventLoop 可管理多个 Channel          │
    └──────────────────────────────────────────┘
```

- **Boss Group**：只做 accept（接受新连接），然后把连接注册到 Worker
- **Worker Group**：处理连接的读写事件，默认 CPU 核数 * 2 个线程
- 每个连接（Channel）固定在一个 EventLoop 上，避免了并发问题

### 2.2 Pipeline 与 Handler

Netty 最核心的设计思想：**把数据处理拆成一串 handler，像流水线一样**。

```
  ┌──────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────┐
  │ HttpServer │────▶│ HttpObject   │────▶│ WebSocket    │────▶│ ChatHandler │
  │ Codec     │     │ Aggregator  │     │ Protocol     │     │ (你的逻辑) │
  └──────────┘     └─────────────┘     └──────────────┘     └──────────┘
```

- `HttpServerCodec`：HTTP 编解码
- `HttpObjectAggregator`：把 HTTP 请求片段组装成完整请求
- `WebSocketServerProtocolHandler`：处理 WebSocket 握手升级（HTTP Upgrade）
- 你的业务 handler：处理文本帧、管理用户映射

### 2.3 零拷贝

Netty 的 ByteBuf 可以直接访问堆外内存（Direct Memory），在文件传输时避免内核态↔用户态的数据拷贝。这是 Netty 高性能的关键之一。

*不需要深究实现细节，记住"Netty 的网络 IO 比其他 Java 框架快"的根本原因之一是零拷贝就行。*

---

## 三、实战项目设计：从零构建一个即时消息系统

### 项目概述

我们构建一个通用消息推送服务，支持：
1. ✅ WebSocket 连接管理（认证、心跳、断线重连）
2. ✅ 点对点私信
3. ✅ 群发广播
4. ✅ REST API 手动推送（从后端任意位置发消息）
5. ✅ 在线用户查询

### 技术栈

| 组件 | 用途 |
|------|------|
| Spring Boot 3.2+ | 应用框架 |
| Netty 4.1+ | 高性能网络层 |
| Redis | Token 校验 + 多实例消息广播 |
| Vue.js / Uni-app | 前端（简写） |

---

## 四、STEP 1：项目初始化

### 4.1 Maven 依赖

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>netty-ws-demo</artifactId>
    <version>1.0.0</version>

    <properties>
        <java.version>17</java.version>
        <netty.version>4.1.108.Final</netty.version>
    </properties>

    <dependencies>
        <!-- Spring Boot -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-redis</artifactId>
        </dependency>

        <!-- Netty -->
        <dependency>
            <groupId>io.netty</groupId>
            <artifactId>netty-all</artifactId>
            <version>${netty.version}</version>
        </dependency>

        <!-- Utils -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
        </dependency>
    </dependencies>
</project>
```

### 4.2 application.yml 配置

```yaml
server:
  port: 8080

netty:
  ws:
    port: 8111
    path: /ws
    boss-threads: 1
    worker-threads: 8   # 通常 = CPU核数 * 2

spring:
  redis:
    host: localhost
    port: 6379
```

---

## 五、STEP 2：Netty 基础架构

### 5.1 配置类 —— 定义 Pipeline

```java
package com.example.nettyws.config;

import com.example.nettyws.handler.WebSocketFrameHandler;
import com.example.nettyws.handler.WebSocketPathParamHandler;
import com.example.nettyws.service.ChannelManager;
import io.netty.bootstrap.ServerBootstrap;
import io.netty.channel.*;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.SocketChannel;
import io.netty.channel.socket.nio.NioServerSocketChannel;
import io.netty.handler.codec.http.HttpObjectAggregator;
import io.netty.handler.codec.http.HttpServerCodec;
import io.netty.handler.codec.http.websocketx.WebSocketServerProtocolHandler;
import io.netty.handler.logging.LogLevel;
import io.netty.handler.logging.LoggingHandler;
import io.netty.handler.timeout.IdleStateHandler;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.concurrent.TimeUnit;

@Slf4j
@Configuration
public class NettyConfig {

    @Value("${netty.ws.boss-threads:1}")
    private int bossThreads;

    @Value("${netty.ws.worker-threads:8}")
    private int workerThreads;

    @Value("${netty.ws.path:/ws}")
    private String wsPath;

    /**
     * Boss Group：接收新连接
     */
    @Bean(destroyMethod = "shutdownGracefully")
    public EventLoopGroup bossGroup() {
        return new NioEventLoopGroup(bossThreads);
    }

    /**
     * Worker Group：处理 IO 读写
     */
    @Bean(destroyMethod = "shutdownGracefully")
    public EventLoopGroup workerGroup() {
        return new NioEventLoopGroup(workerThreads);
    }

    /**
     * Channel 初始化器 —— 定义 Pipeline
     */
    @Bean
    public ChannelInitializer<SocketChannel> channelInitializer(
            ChannelManager channelManager) {
        return new ChannelInitializer<>() {
            @Override
            protected void initChannel(SocketChannel ch) {
                ChannelPipeline pipeline = ch.pipeline();

                // 1. HTTP 编解码（握手阶段需要）
                pipeline.addLast(new HttpServerCodec());

                // 2. HTTP 请求聚合（把分片的请求组合成完整消息）
                pipeline.addLast(new HttpObjectAggregator(65536));

                // 3. 空闲检测（40秒无读 → 触发心跳事件）
                pipeline.addLast(new IdleStateHandler(40, 0, 0, TimeUnit.SECONDS));

                // 4. 握手参数提取（解析 URL 中的 token / userId）
                pipeline.addLast(new WebSocketPathParamHandler(channelManager));

                // 5. WebSocket 协议处理（核心！处理 HTTP Upgrade → WS）
                pipeline.addLast(new WebSocketServerProtocolHandler(
                        wsPath,    // 路径
                        null,      // 子协议
                        true,      // 允许扩展
                        65536      // 最大帧长度
                ));

                // 6. 业务处理
                pipeline.addLast(new WebSocketFrameHandler(channelManager));
            }
        };
    }

    /**
     * ServerBootstrap —— Netty 服务的启动配置
     */
    @Bean
    public ServerBootstrap serverBootstrap(
            EventLoopGroup bossGroup,
            EventLoopGroup workerGroup,
            ChannelInitializer<SocketChannel> channelInitializer) {
        return new ServerBootstrap()
                .group(bossGroup, workerGroup)
                .channel(NioServerSocketChannel.class)
                .handler(new LoggingHandler(LogLevel.INFO))
                .childHandler(channelInitializer)
                .option(ChannelOption.SO_BACKLOG, 128)
                .childOption(ChannelOption.SO_KEEPALIVE, true)
                .childOption(ChannelOption.TCP_NODELAY, true);
    }

    @Bean
    public ChannelManager channelManager() {
        return new ChannelManager();
    }
}
```

### 5.2 启动器 —— 让 Netty 随 Spring Boot 一起启停

```java
package com.example.nettyws.config;

import io.netty.bootstrap.ServerBootstrap;
import io.netty.channel.Channel;
import io.netty.channel.EventLoopGroup;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.SmartLifecycle;
import org.springframework.stereotype.Component;

/**
 * 实现 SmartLifecycle，让 Netty 与 Spring 生命周期联动。
 * Spring 启动后自动 start(), 关闭前自动 stop()。
 */
@Slf4j
@Component
public class NettyWebSocketServer implements SmartLifecycle {

    private final ServerBootstrap serverBootstrap;
    private final EventLoopGroup bossGroup;
    private final EventLoopGroup workerGroup;

    @Value("${netty.ws.port:8111}")
    private int port;

    private Channel channel;
    private volatile boolean running = false;

    public NettyWebSocketServer(ServerBootstrap serverBootstrap,
                                @Qualifier("bossGroup") EventLoopGroup bossGroup,
                                @Qualifier("workerGroup") EventLoopGroup workerGroup) {
        this.serverBootstrap = serverBootstrap;
        this.bossGroup = bossGroup;
        this.workerGroup = workerGroup;
    }

    @Override
    public void start() {
        if (running) return;
        try {
            channel = serverBootstrap.bind(port).sync().channel();
            running = true;
            log.info("🚀 Netty WebSocket server started on port: {}", port);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Failed to start Netty server", e);
        }
    }

    @Override
    public void stop() {
        if (channel != null) {
            channel.close().addListener(future ->
                    log.info("Netty server channel closed"));
        }
        running = false;
    }

    @Override
    public boolean isRunning() {
        return running;
    }

    @Override
    public int getPhase() {
        return Integer.MAX_VALUE; // 最后启动，最先关闭
    }
}
```

---

## 六、STEP 3：核心组件

### 6.1 ChannelManager —— 连接管理器（最重要）

这是整个系统的核心状态管理。它维护三层映射：

```
用户ID ──→ 多个 ChannelID ──→ Channel 实例
Token   ──→ ChannelID
```

```java
package com.example.nettyws.service;

import io.netty.channel.Channel;
import io.netty.handler.codec.http.websocketx.TextWebSocketFrame;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

/**
 * 连接管理器：线程安全地管理所有 WebSocket 连接。
 * 
 * 核心数据结构：
 * CHANNEL_MAP       : channelId → Channel（所有活跃连接）
 * TOKEN_CHANNEL_MAP  : token → channelId（按 token 查找连接）
 * USERID_CHANNEL_MAP : userId → Set<channelId>（一个用户可能有多个设备）
 */
@Slf4j
@Component
public class ChannelManager {

    /** channelId → Channel */
    private final ConcurrentMap<String, Channel> CHANNEL_MAP = new ConcurrentHashMap<>();

    /** token → channelId（用于按 token 发送） */
    private final ConcurrentMap<String, String> TOKEN_CHANNEL_MAP = new ConcurrentHashMap<>();

    /** userId → Set<channelId>（一个用户多端登录） */
    private final ConcurrentMap<String, Set<String>> USERID_CHANNEL_MAP = new ConcurrentHashMap<>();

    /**
     * 绑定连接：建立 token / userId / channel 三者关系
     */
    public void bind(String token, String userId, String channelId, Channel channel) {
        log.debug("Bind token={}, userId={}, channelId={}", token, userId, channelId);

        // 如果这个 token 已有连接，先踢掉旧的
        String oldChannelId = TOKEN_CHANNEL_MAP.get(token);
        if (oldChannelId != null && !oldChannelId.equals(channelId)) {
            Channel oldChannel = CHANNEL_MAP.get(oldChannelId);
            if (oldChannel != null && oldChannel.isActive()) {
                oldChannel.writeAndFlush(new TextWebSocketFrame(
                        "{\"type\":\"kick\",\"reason\":\"duplicate_login\"}"));
                oldChannel.close();
                log.info("Kicked duplicate connection, token={}, oldChannel={}", token, oldChannelId);
            }
        }

        TOKEN_CHANNEL_MAP.put(token, channelId);
        USERID_CHANNEL_MAP.computeIfAbsent(userId, k -> ConcurrentHashMap.newKeySet()).add(channelId);
        CHANNEL_MAP.put(channelId, channel);
    }

    /**
     * 解绑连接：连接断开时清理
     */
    public void unbind(String token, String userId, String channelId) {
        log.debug("Unbind token={}, userId={}, channelId={}", token, userId, channelId);

        CHANNEL_MAP.remove(channelId);
        TOKEN_CHANNEL_MAP.remove(token);

        Set<String> userChannels = USERID_CHANNEL_MAP.get(userId);
        if (userChannels != null) {
            userChannels.remove(channelId);
            if (userChannels.isEmpty()) {
                USERID_CHANNEL_MAP.remove(userId);
                log.info("User {} fully offline", userId);
            }
        }
    }

    /**
     * 广播给所有人
     */
    public void broadcast(String message) {
        if (CHANNEL_MAP.isEmpty()) return;
        TextWebSocketFrame frame = new TextWebSocketFrame(message);
        CHANNEL_MAP.values().forEach(ch -> {
            if (ch.isActive()) {
                ch.writeAndFlush(frame.retainedDuplicate());
            }
        });
        log.debug("Broadcast to {} channels", CHANNEL_MAP.size());
    }

    /**
     * 发送给指定 tokens
     */
    public void sendToTokens(String message, String... tokens) {
        TextWebSocketFrame frame = new TextWebSocketFrame(message);
        for (String token : tokens) {
            String channelId = TOKEN_CHANNEL_MAP.get(token);
            if (channelId != null) {
                Channel ch = CHANNEL_MAP.get(channelId);
                if (ch != null && ch.isActive()) {
                    ch.writeAndFlush(frame.retainedDuplicate());
                }
            }
        }
    }

    /**
     * 发送给指定用户（支持多设备）
     */
    public void sendToUserIds(String message, String... userIds) {
        TextWebSocketFrame frame = new TextWebSocketFrame(message);
        for (String userId : userIds) {
            Set<String> ids = USERID_CHANNEL_MAP.get(userId);
            if (ids != null) {
                for (String cid : ids) {
                    Channel ch = CHANNEL_MAP.get(cid);
                    if (ch != null && ch.isActive()) {
                        ch.writeAndFlush(frame.retainedDuplicate());
                    }
                }
            }
        }
    }

    /**
     * 获取在线用户数
     */
    public int onlineUserCount() {
        return USERID_CHANNEL_MAP.size();
    }

    /**
     * 获取在线用户 ID 列表
     */
    public Set<String> onlineUserIds() {
        return USERID_CHANNEL_MAP.keySet();
    }
}
```

### 6.2 握手处理器 —— 解析参数 + Token 校验

**这是理解 Netty pipeline 的关键**：在 `WebSocketServerProtocolHandler` 之前，我们通过 `HttpServerCodec` + `HttpObjectAggregator` 拿到了完整的 HTTP 升级请求，可以从中提取 token、userId 等参数。

```java
package com.example.nettyws.handler;

import com.example.nettyws.config.NettyConfig;
import com.example.nettyws.service.ChannelManager;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.ChannelInboundHandlerAdapter;
import io.netty.handler.codec.http.FullHttpRequest;
import io.netty.handler.codec.http.websocketx.TextWebSocketFrame;
import io.netty.handler.timeout.IdleStateEvent;
import lombok.extern.slf4j.Slf4j;

import java.util.HashMap;
import java.util.Map;

/**
 * HTTP 握手阶段处理器。
 * 
 * 核心作用：
 * 1. 从 WS 连接 URL 中提取参数：ws://host/ws?token=xxx&userId=xxx
 * 2. 校验 token（可对接 Redis / JWT）
 * 3. 把 userId、token 存入 Channel 的 attributes（后续 handler 能取到）
 * 4. 处理心跳消息
 */
@Slf4j
public class WebSocketPathParamHandler extends ChannelInboundHandlerAdapter {

    private final ChannelManager channelManager;
    private int lostHeartbeatCount = 0;

    private static final int MAX_LOST_HEARTBEAT = 3;
    private static final String HEARTBEAT_MSG = "{\"type\":\"heartbeat\"}";

    public WebSocketPathParamHandler(ChannelManager channelManager) {
        this.channelManager = channelManager;
    }

    @Override
    public void userEventTriggered(ChannelHandlerContext ctx, Object evt) {
        if (evt instanceof IdleStateEvent) {
            // 40 秒没收到数据 → 检查心跳
            lostHeartbeatCount++;
            if (lostHeartbeatCount >= MAX_LOST_HEARTBEAT) {
                String userId = ctx.channel().attr(NettyConfig.USERID_KEY).get();
                log.warn("Heartbeat timeout, closing channel. userId={}", userId);
                ctx.close();
            }
        } else {
            ctx.fireUserEventTriggered(evt);
        }
    }

    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) throws Exception {
        if (msg instanceof FullHttpRequest request) {
            // ===== HTTP Upgrade 阶段：解析参数 =====
            String uri = request.uri();
            if (uri.contains("?")) {
                Map<String, String> params = parseQueryParams(uri);
                String token = params.get("token");
                String userId = params.get("userId");

                // 存入 Channel attributes（后续 handler 可取）
                ctx.channel().attr(NettyConfig.TOKEN_KEY).set(token);
                ctx.channel().attr(NettyConfig.USERID_KEY).set(userId);

                // TODO: 校验 token（Redis / JWT）
                // if (!validateToken(token)) {
                //     ctx.writeAndFlush(new TextWebSocketFrame("Auth failed"));
                //     ctx.close();
                //     return;
                // }

                // 绑定连接
                channelManager.bind(token, userId,
                        ctx.channel().id().asShortText(), ctx.channel());

                // 重写 URI（删除参数，让 WebSocketServerProtocolHandler 能工作）
                request.setUri("/ws");
            }
        }

        if (msg instanceof TextWebSocketFrame frame) {
            // ===== WebSocket 阶段：心跳检测 =====
            if (HEARTBEAT_MSG.equals(frame.text())) {
                lostHeartbeatCount = 0; // 重置心跳计数器
                ctx.writeAndFlush(new TextWebSocketFrame(HEARTBEAT_MSG));
                return;
            }
        }

        // 交给 pipeline 后续 handler
        super.channelRead(ctx, msg);
    }

    private Map<String, String> parseQueryParams(String uri) {
        Map<String, String> map = new HashMap<>();
        String query = uri.contains("?") ? uri.substring(uri.indexOf("?") + 1) : "";
        for (String param : query.split("&")) {
            String[] kv = param.split("=", 2);
            if (kv.length == 2) map.put(kv[0], kv[1]);
        }
        return map;
    }
}
```

### 6.3 业务处理器 —— 处理消息帧

```java
package com.example.nettyws.handler;

import com.example.nettyws.config.NettyConfig;
import com.example.nettyws.service.ChannelManager;
import io.netty.channel.ChannelHandler;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.SimpleChannelInboundHandler;
import io.netty.handler.codec.http.websocketx.TextWebSocketFrame;
import lombok.extern.slf4j.Slf4j;

/**
 * WebSocket 消息处理器（业务层）
 *
 * @ChannelHandler.Sharable 表示该 handler 可被多个 pipeline 共享
 */
@Slf4j
@ChannelHandler.Sharable
public class WebSocketFrameHandler extends SimpleChannelInboundHandler<TextWebSocketFrame> {

    private final ChannelManager channelManager;

    public WebSocketFrameHandler(ChannelManager channelManager) {
        this.channelManager = channelManager;
    }

    @Override
    protected void channelRead0(ChannelHandlerContext ctx, TextWebSocketFrame msg) {
        String text = msg.text();
        String userId = ctx.channel().attr(NettyConfig.USERID_KEY).get();
        log.debug("Message from userId={}: {}", userId, text);

        // 这里接入你的业务逻辑，例如：
        // 1. 解析 JSON 消息体
        // 2. 根据 type 分发：私信、群发、系统消息...
        // 3. 调用 channelManager.sendToUserIds 转发

        // 简单回复确认
        ctx.writeAndFlush(new TextWebSocketFrame(
                "{\"type\":\"ack\",\"content\":\"received\"}"));
    }

    @Override
    public void channelActive(ChannelHandlerContext ctx) {
        log.info("New connection: channelId={}",
                ctx.channel().id().asShortText());
    }

    @Override
    public void channelInactive(ChannelHandlerContext ctx) {
        String token = ctx.channel().attr(NettyConfig.TOKEN_KEY).get();
        String userId = ctx.channel().attr(NettyConfig.USERID_KEY).get();
        String channelId = ctx.channel().id().asShortText();

        // 清理连接
        channelManager.unbind(token, userId, channelId);
        log.info("Connection closed: userId={}, channelId={}", userId, channelId);
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
        log.error("Channel error: userId={}, error={}",
                ctx.channel().attr(NettyConfig.USERID_KEY).get(),
                cause.getMessage());
        ctx.close();
    }
}
```

### 6.4 属性常量定义

```java
package com.example.nettyws.config;

import io.netty.util.AttributeKey;

import java.util.Map;

public class NettyConstants {

    public static final String WEBSOCKET_PATH = "/ws";
    public static final String HEARTBEAT_MSG = "{\"type\":\"heartbeat\"}";

    // Channel 属性 Key —— 用于在 pipeline 不同 handler 间传数据
    public static final AttributeKey<String> TOKEN_KEY =
            AttributeKey.valueOf("token");
    public static final AttributeKey<String> USERID_KEY =
            AttributeKey.valueOf("userId");
    public static final AttributeKey<Map<String, String>> URL_PARAMS_KEY =
            AttributeKey.valueOf("urlParams");
}
```

---

## 七、STEP 4：REST API 推送接口

通过 REST API 从后端任意位置向 WebSocket 客户端推送消息。

```java
package com.example.nettyws.service;

import com.example.nettyws.vo.TextMsgVO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Set;
import java.util.concurrent.ConcurrentMap;

@Service
@RequiredArgsConstructor
public class MessagePushService {

    private final ChannelManager channelManager;

    /**
     * 广播给所有人
     */
    public void broadcast(String message) {
        channelManager.broadcast(message);
    }

    /**
     * 发送给指定 tokens
     */
    public void sendToTokens(String message, String... tokens) {
        channelManager.sendToTokens(message, tokens);
    }

    /**
     * 发送给指定用户
     */
    public void sendToUsers(String message, String... userIds) {
        channelManager.sendToUserIds(message, userIds);
    }

    /**
     * 在线用户列表
     */
    public Set<String> getOnlineUserIds() {
        return channelManager.onlineUserIds();
    }

    /**
     * 在线用户数
     */
    public int getOnlineCount() {
        return channelManager.onlineUserCount();
    }
}
```

```java
package com.example.nettyws.controller;

import com.example.nettyws.service.MessagePushService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Set;

@RestController
@RequestMapping("/api/ws")
@RequiredArgsConstructor
public class WebSocketController {

    private final MessagePushService messagePushService;

    @GetMapping("/online/count")
    public int onlineCount() {
        return messagePushService.getOnlineCount();
    }

    @GetMapping("/online/users")
    public Set<String> onlineUsers() {
        return messagePushService.getOnlineUserIds();
    }

    @PostMapping("/broadcast")
    public String broadcast(@RequestBody String message) {
        messagePushService.broadcast(message);
        return "Broadcast sent to " + messagePushService.getOnlineCount() + " users";
    }

    @PostMapping("/send")
    public String sendToUsers(@RequestParam String userIds,
                              @RequestBody String message) {
        String[] ids = userIds.split(",");
        messagePushService.sendToUsers(message, ids);
        return "Message sent to " + ids.length + " users";
    }
}
```

---

## 八、STEP 5：前端 WebSocket 客户端

```javascript
// websocket-client.js —— 带自动重连的心跳客户端

class WebSocketClient {
    constructor(options) {
        this.url = options.url;             // ws://host:port/ws
        this.token = options.token;
        this.userId = options.userId;
        this.onMessage = options.onMessage || (() => {});
        this.onStatusChange = options.onStatusChange || (() => {});

        this.ws = null;
        this.reconnectInterval = 5000;       // 断线重连间隔
        this.heartbeatInterval = 30000;      // 心跳间隔（30s）
        this.heartbeatTimer = null;
        this.forceClosed = false;
    }

    connect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) return;

        const wsUrl = `${this.url}?token=${this.token}&userId=${this.userId}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('[WS] Connected');
            this.onStatusChange('connected');
            this.startHeartbeat();
        };

        this.ws.onmessage = (event) => {
            // 过滤心跳回包
            if (event.data === '{"type":"heartbeat"}') return;
            this.onMessage(JSON.parse(event.data));
        };

        this.ws.onclose = () => {
            console.log('[WS] Disconnected');
            this.onStatusChange('disconnected');
            this.stopHeartbeat();
            if (!this.forceClosed) {
                console.log(`[WS] Reconnecting in ${this.reconnectInterval}ms...`);
                setTimeout(() => this.connect(), this.reconnectInterval);
            }
        };

        this.ws.onerror = (err) => {
            console.error('[WS] Error:', err);
            this.ws.close();
        };
    }

    disconnect() {
        this.forceClosed = true;
        this.stopHeartbeat();
        if (this.ws) {
            this.ws.onclose = null; // 阻止自动重连
            this.ws.close();
            this.ws = null;
        }
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(typeof data === 'string' ? data : JSON.stringify(data));
        }
    }

    startHeartbeat() {
        this.stopHeartbeat();
        this.heartbeatTimer = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send('{"type":"heartbeat"}');
            }
        }, this.heartbeatInterval);
    }

    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }
}

// 使用示例
const client = new WebSocketClient({
    url: 'ws://localhost:8111/ws',
    token: 'your-jwt-token',
    userId: 'user123',
    onMessage: (msg) => console.log('收到消息:', msg),
    onStatusChange: (status) => console.log('连接状态:', status)
});

client.connect();
```

---

## 九、Netty 进阶：你必须知道的 5 个关键点

### 9.1 为什么 `retainedDuplicate()` 是必须的

发送消息时使用了 `frame.retainedDuplicate()`，原因如下：

```java
// ❌ 错误写法：多个 channel 共享同一个 frame 引用计数
ch1.writeAndFlush(frame);
ch2.writeAndFlush(frame);  // 第二次已被释放！

// ✅ 正确写法：每个 channel 独立增加引用计数
ch1.writeAndFlush(frame.retainedDuplicate());
ch2.writeAndFlush(frame.retainedDuplicate());
```

Netty 使用**引用计数**管理 ByteBuf/Frame。每个 writeAndFlush 后 Netty 会自动释放 frame 的引用计数，如果不 retain，第二个 channel 会拿到已释放的对象。

### 9.2 空闲检测 + 心跳机制

```java
// 服务端：40 秒无读触发 IdleStateEvent
pipeline.addLast(new IdleStateHandler(40, 0, 0, TimeUnit.SECONDS));

// 客户端：每 30 秒发一次心跳
setInterval(() => ws.send('{"type":"heartbeat"}'), 30000);
```

**为什么要心跳？**
- TCP 长连接在中间网络设备（NAT 路由器、防火墙）可能被静默切断
- 服务端无法感知客户端崩溃或网络断开
- 心跳 = 应用层的「我还活着」信号

**心跳机制流程：**
1. 客户端每 30s 发心跳
2. 服务端 40s 无读 → 触发 IdleStateEvent → 记录一次丢失
3. 连续 3 次（120s 无响应）→ 关闭连接

### 9.3 Netty 的线程模型陷阱

```java
// ❌ 千万不要在 IO 线程中执行耗时操作
@Override
protected void channelRead0(ChannelHandlerContext ctx, TextWebSocketFrame msg) {
    Thread.sleep(5000);  // 这会阻塞 worker 线程！
    // 这个 worker 管理的所有其他连接都会卡住
}

// ✅ 正确做法：异步处理
@Override
protected void channelRead0(ChannelHandlerContext ctx, TextWebSocketFrame msg) {
    // 方式一：提交到业务线程池
    businessExecutor.execute(() -> {
        // 耗时操作
    });

    // 方式二：用 Netty 提供的 EventExecutorGroup
    // 在 endpoint 配置中设置 useEventExecutorGroup=true 即可
}
```

**如果你用 netty-websocket-spring-boot-starter**，配置里 `useEventExecutorGroup=true`（默认就是 true），框架会自动用另一个线程池执行你的 handler 方法，IO 线程不会被阻塞。

### 9.4 pipeline 中 handler 的顺序为什么重要

```
HttpServerCodec → HttpObjectAggregator → IdleStateHandler 
→ PathParamHandler → WebSocketServerProtocolHandler → FrameHandler
```

顺序决定了谁能先处理消息。关键要点：

1. **`HttpServerCodec` 必须在最前面**：因为它负责把字节流解码成 HTTP 请求
2. **`HttpObjectAggregator` 必须在 Codec 之后**：因为要先解码成 chunk，才能聚合
3. **`PathParamHandler` 必须在 `WebSocketServerProtocolHandler` 之前**：因为握手阶段是 HTTP 请求，我们要在它变成 WebSocket 之前读取到参数
4. **`WebSocketServerProtocolHandler` 执行 HTTP Upgrade**：把 /ws 路径的 HTTP 请求升级为 WebSocket
5. **业务 handler 在最后**：此时连接已升级为 WebSocket，收到的已经是 TextWebSocketFrame 了

### 9.5 多实例部署怎么搞？

单机 Netty 用 ConcurrentHashMap 管理连接就够了。多实例需要**外部消息总线**：

```
          ┌──────────┐
          │  Client A │
          └────┬─────┘
               │ WebSocket
               ▼
         ┌──────────┐          ┌──────────────┐
         │ Server 1  │ ◄──────► │              │
         │ (Netty)   │          │   Redis      │
         └──────────┘          │   Pub/Sub    │
               │               │  (Channel)   │
         ┌────▼─────┐          │              │
         │  Client B│          └──────────────┘
         └──────────┘
                                 ┌──────────────┐
         ┌──────────┐            │              │
         │  Client C│───────►    │   RabbitMQ   │
         └──────────┘           │  (STOMP)     │
               │                │              │
         ┌────▼─────┐           └──────────────┘
         │ Server 2 │                 │
         │ (Netty)   │────────────────┘
         └──────────┘
               │
         ┌────▼─────┐
         │  Client D│
         └──────────┘
```

**方案一：Redis Pub/Sub（推荐）**

```java
// Server 1 收到消息 → 发布到 Redis Channel
redisTemplate.convertAndSend("ws:messages", messageJson);

// 所有 Server 都订阅这个 Channel
@Bean
public MessageListener listener(ChannelManager channelManager) {
    return (msg, pattern) -> {
        // 解析消息，找到目标 userId
        WsMessage wsMsg = parse(msg.toString());
        // 只发给本机上的目标用户
        channelManager.sendToUserIds(wsMsg.getContent(), wsMsg.getTargetUserId());
    };
}
```

**方案二：STOMP Broker Relay（RabbitMQ）**
Spring 的 STOMP + `enableStompBrokerRelay` 可以做到，但要依赖外部消息队列。

---

## 十、用 netty-websocket-spring-boot-starter 简化开发

如果不想手写所有 Netty 配置，可以用开源 starter 快速上手：

### Maven 依赖

```xml
<dependency>
    <groupId>org.yeauty</groupId>
    <artifactId>netty-websocket-spring-boot-starter</artifactId>
    <version>0.13.0</version>
</dependency>
```

### 一个 POJO 搞定 WebSocket

```java
@ServerEndpoint(path = "/ws/{userId}")
@Component
public class MyWebSocket {

    @BeforeHandshake
    public void handshake(Session session, HttpHeaders headers,
                          @RequestParam String token,
                          @PathVariable String userId) {
        // 校验 token
        if (!validateToken(token)) {
            session.close();
        }
        session.setSubprotocols("stomp");  // 可选子协议
    }

    @OnOpen
    public void onOpen(Session session,
                       @PathVariable String userId,
                       @RequestParam String token) {
        System.out.println("用户 " + userId + " 上线了");
        // 保存 session 到缓存
        SessionHolder.put(userId, session);
    }

    @OnClose
    public void onClose(Session session,
                        @PathVariable String userId) {
        System.out.println("用户 " + userId + " 下线了");
        SessionHolder.remove(userId);
    }

    @OnMessage
    public void onMessage(Session session, String message) {
        System.out.println("收到消息: " + message);
        session.sendText("Hello Netty!");
    }

    @OnError
    public void onError(Session session, Throwable error) {
        error.printStackTrace();
    }

    @OnEvent
    public void onEvent(Session session, Object evt) {
        if (evt instanceof IdleStateEvent) {
            IdleStateEvent e = (IdleStateEvent) evt;
            switch (e.state()) {
                case READER_IDLE -> System.out.println("读空闲");
                case WRITER_IDLE -> System.out.println("写空闲");
                case ALL_IDLE -> System.out.println("全空闲");
            }
        }
    }

    @OnBinary
    public void onBinary(Session session, byte[] bytes) {
        // 处理二进制消息（文件传输等）
    }
}
```

### 配置项（@ServerEndpoint 支持完整配置）

```java
@ServerEndpoint(
    path = "/ws",
    port = 8111,
    host = "0.0.0.0",
    bossLoopGroupThreads = 1,
    workerLoopGroupThreads = 8,
    useCompressionHandler = true,
    readerIdleTimeSeconds = 40,
    maxFramePayloadLength = 65536,
    useEventExecutorGroup = true,
    eventExecutorGroupThreads = 16,
    optionSoBacklog = 128,
    childOptionTcpNodelay = true
)
```

---

## 十一、常见坑总结

### 🕳️ 坑 1：setAllowedOrigins("*")
```java
// ❌ 生产环境禁止
.setAllowedOrigins("*");

// ✅ 写实际域名
.setAllowedOrigins("https://yourdomain.com");
```
`*` 意味着任何网站都可以向你的服务端开 WebSocket 发送请求。

### 🕳️ 坑 2：WebSocket 和 HTTP Session 混用
HTTP Session 在 WebSocket 握手完成后可能过期，不要从 HttpSession 读数据。**在握手阶段把需要的信息存到 WebSocketSession 的属性里**。

### 🕳️ 坑 3：多个 Channel 复用同一个 Frame
用 `retainedDuplicate()` 或 `copy()`，否则引用计数归零后第二个 channel 写失败。

### 🕳️ 坑 4：在 IO 线程中阻塞
不要在 `channelRead0` 中执行数据库查询、HTTP 调用等阻塞操作。用 `EventExecutorGroup` 或异步线程池。

### 🕳️ 坑 5：忘记处理异常
`exceptionCaught` 中至少要 `ctx.close()`，否则连接泄漏。

### 🕳️ 坑 6：单机 `ConcurrentHashMap` 在多实例下失效
跨实例部署必须用 Redis Pub/Sub 或消息队列做路由。

---

## 十二、从入门到精通的路径

```
               ┌─────────────────────────────┐
               │   第1周：会用就行            │
               │   - 用 native starter 写一个  │
               │     简单的 echo 服务          │
               │   - 理解 @OnOpen/@OnMessage   │
               └──────────┬──────────────────┘
                          ▼
               ┌─────────────────────────────┐
               │   第2周：理解原理            │
               │   - 手写 Netty 配置          │
               │   - 理解 Boss-Worker 模型    │
               │   - 写自己的 ChannelManager  │
               └──────────┬──────────────────┘
                          ▼
               ┌─────────────────────────────┐
               │   第3周：生产化              │
               │   - 加入 Token 校验         │
               │   - 心跳 + 断线重连         │
               │   - REST API 推动态推送     │
               └──────────┬──────────────────┘
                          ▼
               ┌─────────────────────────────┐
               │   第4周：进阶                │
               │   - 多实例 + Redis Pub/Sub   │
               │   - 消息持久化（离线消息）    │
               │   - 性能压测与调优           │
               └─────────────────────────────┘
```

---

## 十三、参考资料

- [netty-websocket-spring-boot-starter (GitHub)](https://github.com/YeautyYE/netty-websocket-spring-boot-starter) — 轻量级注解式开发
- [Spring Boot WebSocket Guide (websocket.org)](https://websocket.org/guides/frameworks/spring-boot/) — 原生方案与 STOMP
- [Building a Scalable WebSocket Service with Netty (BestHub)](https://www.besthub.dev/articles/how-to-build-a-scalable-websocket-service-with-netty-spring-boot-and-vue2-79a4ea98c1e5) — 完整全栈案例
- [Netty 官方文档](https://netty.io/wiki/user-guide-for-4.x.html)
- [Spring Boot 虚拟线程支持](https://spring.io/blog/2023/09/11/virtual-threads-in-spring-boot-32)

---

*整理于 2026-06-12，综合 selfhub.dev、websocket.org、GitHub 等多个高质量来源*
