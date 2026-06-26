# Netty 深度解析：从入门到 RPC 框架设计

> 一篇贯通 Netty 核心原理、源码技巧、RPC 框架设计与生产级最佳实践的全栈指南
>
> 综合来源：蚂蚁金服技术博客 · Medium 多篇 · Netty 官方文档 · Baeldung · 开源 RPC 框架源码分析

---

## 目录

1. [Netty 是什么](#1-netty-是什么)
2. [网络 IO 模型演进：从 BIO 到 epoll](#2-网络-io-模型演进从-bio-到-epoll)
3. [Netty 核心架构](#3-netty-核心架构)
4. [Netty 实战入门](#4-netty-实战入门)
5. [基于 Netty 设计 RPC 框架](#5-基于-netty-设计-rpc-框架)
6. [传输层协议栈设计](#6-传输层协议栈设计)
7. [RPC 框架关键特性](#7-rpc-框架关键特性)
8. [客户端代理与调用模型](#8-客户端代理与调用模型)
9. [负载均衡策略](#9-负载均衡策略)
10. [集群容错机制](#10-集群容错机制)
11. [序列化/反序列化深度优化](#11-序列化反序列化深度优化)
12. [Epoll 深度解析：从原理到 Netty 集成](#12-epoll-深度解析从原理到-netty-集成)
13. [Netty 内存管理揭秘](#13-netty-内存管理揭秘)
14. [Netty Native Transport](#14-netty-native-transport)
15. [Netty 最佳实践（13 条生产级）](#15-netty-最佳实践13-条生产级)
16. [从 Netty 源码学到的代码技巧](#16-从-netty-源码学到的代码技巧)
17. [性能压榨：压测驱动的极致优化](#17-性能压榨压测驱动的极致优化)
18. [完整 RPC 框架实战](#18-完整-rpc-框架实战)
19. [常见问题与排查指南](#19-常见问题与排查指南)
20. [总结与学习路径](#20-总结与学习路径)
21. [更多真实场景代码案例](#21-更多真实场景代码案例)

---

## 1. Netty 是什么

Netty 是一个致力于创建高性能网络应用程序的**异步事件驱动网络框架**。它构建在 Java NIO 之上，但大幅降低了 NIO 的使用门槛：

- **不需要先成为网络专家**就可以构建复杂的网络应用
- **业界共识**：涉及网络通信的中间件大部分基于 Netty

### 谁在用 Netty？

| 项目 | 领域 | 用途 |
|------|------|------|
| Apache Dubbo | RPC 框架 | 底层网络通信 |
| Apache Kafka | 消息队列 | 高吞吐网络层 |
| Elasticsearch | 搜索引擎 | 节点间通信 |
| gRPC-Java | RPC 框架 | HTTP/2 实现 |
| Apache RocketMQ | 消息队列 | 网络传输层 |
| Spring WebFlux | Web 框架 | Reactor Netty 底层 |
| Hadoop / HBase | 大数据 | RPC 层 |
| Sofa-Bolt | RPC 框架 | 蚂蚁金服自研 |

### 核心定位

Netty 横跨**传输层**和**应用层**：

- **作为传输层引擎**：封装 TCP/UDP 的复杂性，提供统一的 Channel 抽象
- **作为应用层容器**：通过 Pipeline 架构灵活处理 HTTP、WebSocket、自定义 RPC 等协议

> Netty = 数据传输的"高速公路" + 协议执行的"交通规则"

---

## 2. 网络 IO 模型演进：从 BIO 到 epoll

### 2.1 BIO（Blocking IO）— 一连接一线程

```java
// 传统 BIO Server — 每个线程只能处理一个连接
ServerSocket serverSocket = new ServerSocket(8080);
while (true) {
    Socket socket = serverSocket.accept();      // 阻塞直到连接到来
    new Thread(() -> handle(socket)).start();   // 每个连接一个线程
}
```

**问题**：C10K（一万连接）时线程数爆炸，上下文切换开销灾难。

### 2.2 NIO（Non-blocking IO）— 多路复用

Java NIO 引入了 Selector，一个线程可以监控多个 Channel：

```java
Selector selector = Selector.open();
channel.register(selector, SelectionKey.OP_READ);
while (true) {
    selector.select();   // 阻塞直到有事件就绪
    Set<SelectionKey> keys = selector.selectedKeys();
    // 处理就绪事件
}
```

**但 Java NIO 原生 API 有大量痛点**（详见第 2.3 节）。

### 2.3 Java NIO 的"坑"— 为什么需要 Netty

| 问题 | 说明 | Netty 解决方案 |
|------|------|---------------|
| API 复杂难懂 | Buffer、Channel、Selector 配合繁琐 | 统一 Channel/Pipeline 抽象 |
| 粘包/半包 | TCP 流式无边界 | `LengthFieldBasedFrameDecoder` 等 |
| Epoll 空轮询 Bug | linux 下 `epollWait` 直接返回导致 CPU 100% | 自动 rebuilding selector |
| `SelectKey` 垃圾多 | `Set` 迭代器产生大量临时对象 | 双数组替换 HashSet |
| `synchronized` 锁争用 | allocate direct buffer、`Selector.wakeup()` 等 | `PooledByteBuf` 的 TLAB 优化 |
| `wakeup()` 开销大 | linux 用 pipe 通信，windows 用两个 TCP 连接 | 内置优化逻辑 |
| `fdToKey` HashMap rehash | 单机几十万连接时 rehash 频繁 | Netty Native Transport 减少锁 |
| epoll LT 模式 | 水平触发可能重复通知 | Native Transport 支持 ET |
| Direct Buffer GC 问题 | `Cleaner` 虚引用延迟释放堆外内存 | `UnpooledUnsafeNoCleanerDirectByteBuf` |

### 2.4 多路复用对比

| 机制 | 时间复杂度 | fd 复制 | 模式 | 连接数扩展性 |
|------|-----------|---------|------|-------------|
| select | O(n) | 每次拷贝全部 fd_set | LT | 差（1024 限制） |
| poll | O(n) | 每次拷贝全部 | LT | 一般（无数量限制） |
| epoll | O(1) | 只拷贝就绪 fd | LT+ET | 优秀 |

---

## 3. Netty 核心架构

### 3.1 四大核心组件

```
┌─────────────────────────────────────────────────┐
│                  ChannelPipeline                 │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌───────────────┐ │
│  │Decoder│ │Encoder│ │Handler│ │...More Handlers│ │
│  └──────┘ └──────┘ └──────┘ └───────────────┘ │
├─────────────────────────────────────────────────┤
│                    Channel                       │
│           (代表一个网络连接)                       │
├─────────────────────────────────────────────────┤
│                   EventLoop                      │
│     ┌──────────────┬────────────────────┐       │
│     │   Selector   │  mpsc_queue        │       │
│     │              │ (Task Queue)       │       │
│     └──────────────┴────────────────────┘       │
│     ┌────────────────────────────────────┐       │
│     │   delay_queue (定时任务, O(log n)) │       │
│     └────────────────────────────────────┘       │
│             绑定一个 Thread                        │
└─────────────────────────────────────────────────┘
```

#### Channel
代表一个网络连接（Socket/File Descriptor），负责管理底层 socket 并提供读写接口。

类型：
- `NioServerSocketChannel` — 服务端监听套接字
- `NioSocketChannel` — 客户端/服务端通信套接字
- `NioDatagramChannel` — UDP 数据报

#### EventLoop
EventLoop 是 Netty 的核心线程模型：

- **一个 Selector** — IO 事件多路复用
- **一个任务队列** — MPSC（多生产者单消费者）无锁队列
- **一个延迟任务队列** — 二叉堆优先级队列，O(log n)
- **绑定一个 Thread** — 这直接避免了 Pipeline 中的线程竞争

**Boss vs Worker**：
- **Boss（mainReactor）**：处理 accept 事件，将以轮询方式将 channel 分配给 Worker
- **Worker（subReactor）**：处理 read/write 等 IO 事件

```
Boss EventLoopGroup (通常 1 个)     Worker EventLoopGroup (N 个)
┌─────────────┐                    ┌─────────────┐
│  Boss       │──accept──→         │  Worker #1  │
│  EventLoop  │                    ├─────────────┤
│  (Selector) │    channel 轮询     │  Worker #2  │
└─────────────┘    分配             ├─────────────┤
                                   │  ... n个    │
                                   └─────────────┘
```

**配置经验**：Worker 线程数经验值为 `cpu cores × 2`，但最好通过压测找出最佳值。

#### Handler
处理器，处理入站/出站数据及异常：
- `ChannelInboundHandler` — 处理入站事件（read, active, inactive, exception）
- `ChannelOutboundHandler` — 处理出站事件（write, connect, close）

#### Pipeline
Handler 的责任链：

```
入站数据 → Head → Decoder1 → Decoder2 → BusinessHandler → Tail
出站数据 ← Head ← Encoder1 ← Encoder2 ←                      Tail
```

### 3.2 Netty 线程模型（4.x）

```
IO Thread (Worker)
   │
   ├─ IO 事件处理 (ioRatio = 50%，默认)
   │   ├─ epoll_wait → 获取就绪事件
   │   └─ 处理每个 channel 的 read/write
   │
   └─ 非 IO 任务
       ├─ mpsc_queue 中的普通任务
       └─ delay_queue 中的定时任务
```

**ioRatio**：控制 EventLoop 执行 IO 任务和非 IO 任务的时间比例（默认 50%）。

---

## 4. Netty 实战入门

### 4.1 Maven 依赖

```xml
<dependency>
    <groupId>io.netty</groupId>
    <artifactId>netty-all</artifactId>
    <version>4.1.116.Final</version>
</dependency>
```

### 4.2 Echo Server

```java
public class EchoServer {
    public static void main(String[] args) {
        EventLoopGroup boss = new NioEventLoopGroup(1);
        EventLoopGroup worker = new NioEventLoopGroup();

        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(boss, worker)
             .channel(NioServerSocketChannel.class)
             .option(ChannelOption.SO_BACKLOG, 128)
             .childOption(ChannelOption.SO_KEEPALIVE, true)
             .childHandler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 protected void initChannel(SocketChannel ch) {
                     ch.pipeline().addLast(new EchoServerHandler());
                 }
             });

            ChannelFuture f = b.bind(8080).sync();
            f.channel().closeFuture().sync();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            boss.shutdownGracefully();
            worker.shutdownGracefully();
        }
    }
}

class EchoServerHandler extends ChannelInboundHandlerAdapter {
    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) {
        ctx.write(msg);  // 原样写回
    }

    @Override
    public void channelReadComplete(ChannelHandlerContext ctx) {
        ctx.flush();
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
        cause.printStackTrace();
        ctx.close();
    }
}
```

### 4.3 Echo Client

```java
public class EchoClient {
    public static void main(String[] args) {
        EventLoopGroup group = new NioEventLoopGroup();

        try {
            Bootstrap b = new Bootstrap();
            b.group(group)
             .channel(NioSocketChannel.class)
             .handler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 protected void initChannel(SocketChannel ch) {
                     ch.pipeline().addLast(new EchoClientHandler());
                 }
             });

            ChannelFuture f = b.connect("localhost", 8080).sync();
            f.channel().closeFuture().sync();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            group.shutdownGracefully();
        }
    }
}

class EchoClientHandler extends SimpleChannelInboundHandler<String> {
    @Override
    public void channelActive(ChannelHandlerContext ctx) {
        ctx.writeAndFlush("Hello, Netty!");
    }

    @Override
    protected void channelRead0(ChannelHandlerContext ctx, String msg) {
        System.out.println("Server says: " + msg);
    }
}
```

### 4.4 HTTP Server 示例

```java
public class HttpServer {
    public static void main(String[] args) {
        EventLoopGroup boss = new NioEventLoopGroup(1);
        EventLoopGroup worker = new NioEventLoopGroup();

        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(boss, worker)
             .channel(NioServerSocketChannel.class)
             .childHandler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 protected void initChannel(SocketChannel ch) {
                     ch.pipeline()
                       .addLast(new HttpServerCodec())          // HTTP 编解码
                       .addLast(new HttpObjectAggregator(65536)) // 聚合 HTTP 报文
                       .addLast(new HttpServerHandler());
                 }
             });

            ChannelFuture f = b.bind(8080).sync();
            f.channel().closeFuture().sync();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            boss.shutdownGracefully();
            worker.shutdownGracefully();
        }
    }
}

class HttpServerHandler extends SimpleChannelInboundHandler<FullHttpRequest> {
    @Override
    protected void channelRead0(ChannelHandlerContext ctx, FullHttpRequest req) {
        String response = "Hello, World!";
        FullHttpResponse resp = new DefaultFullHttpResponse(
            HTTP_1_1, OK, Unpooled.wrappedBuffer(response.getBytes()));
        resp.headers().set(CONTENT_TYPE, "text/plain");
        resp.headers().set(CONTENT_LENGTH, response.length());
        ctx.writeAndFlush(resp);
    }
}
```

### 4.5 粘包/半包处理

```java
// 方式一：固定长度帧
ch.pipeline().addLast(new FixedLengthFrameDecoder(1024));

// 方式二：分隔符帧
ch.pipeline().addLast(new DelimiterBasedFrameDecoder(8192, Delimiters.lineDelimiter()));

// 方式三：长度字段前缀（推荐，RPC 协议常用）
ch.pipeline().addLast(new LengthFieldBasedFrameDecoder(65536, 0, 4, 0, 4));
// 说明：前 4 字节 = 报文长度，后面跟着报文内容
```

---

## 5. 基于 Netty 设计 RPC 框架

### 5.1 整体架构

```
┌──────────────┐          ┌─────────────────┐
│  Consumer    │          │    Provider      │
│  (客户端)    │          │   (服务端)        │
├──────────────┤          ├─────────────────┤
│  Proxy       │          │  Service Dict    │
│  (动态代理)   │          │  ┌─svcA──┐       │
│  集群容错     │          │  │svcB  │       │
│  → 负载均衡   │          │  │svcC  │       │
│  → 网络发送   │          │  └──────┘       │
└──────┬───────┘          └──────┬──────────┘
       │                         │
       │     注册中心           │
       │   (ZooKeeper/   )     │
       │    Nacos/Etcd         │
       └─────────┬─────────────┘
                 │
         ┌───────┴───────┐
         │  Netty 传输层  │
         │   (TCP长连接)  │
         └───────────────┘
```

### 5.2 远程调用完整流程

1. **服务端启动**：Provider 启动，将服务注册到注册中心（如 ZK/Nacos）
2. **客户端启动**：Consumer 启动，从注册中心订阅感兴趣的服务列表
3. **地址推送**：注册中心将 Provider 地址列表推送给 Consumer
4. **发起调用**：Consumer 的 Proxy 从可用地址列表中选择一个地址
5. **请求序列化**：将调用信息序列化为字节数组
6. **网络传输**：通过 Netty TCP 长连接发送到目标 Provider
7. **服务端接收**：Provider 收到请求后反序列化
8. **服务查找**：从本地 Service Dict 找到对应 Provider Object
9. **反射调用**：根据方法名和参数通过反射调用目标方法
10. **结果返回**：将返回值序列化后通过网络返回 Consumer
11. **Consumer 接收**：反序列化为 Java 对象，返回给调用方

**对调用者透明**：以上 11 步对方法调用者完全不可见，看起来就像本地调用一样。

### 5.3 RPC 三元组

```java
// 每个 RPC 请求的核心三元组
public class RpcTriplet {
    private long invokeId;      // 唯一请求 ID（用于关联请求和响应）
    private RpcRequest request; // 请求对象
    private RpcResponse response; // 响应对象（异步填充）
}
```

**Netty 4.x 优化**：IO Thread（Worker）使用 `Map<InvokeId, Future>` 代替全局 Map，避免线程竞争。

```java
// 每个 Channel 关联自己的 pending 请求
public class RpcClientHandler extends SimpleChannelInboundHandler<RpcResponse> {
    private final Map<Long, CompletableFuture<RpcResponse>> pending = 
        new ConcurrentHashMap<>();

    @Override
    protected void channelRead0(ChannelHandlerContext ctx, RpcResponse resp) {
        CompletableFuture<RpcResponse> future = pending.remove(resp.getInvokeId());
        if (future != null) {
            future.complete(resp);
        }
    }

    public CompletableFuture<RpcResponse> send(RpcRequest req) {
        CompletableFuture<RpcResponse> future = new CompletableFuture<>();
        pending.put(req.getInvokeId(), future);
        ctx.writeAndFlush(req);
        return future;
    }
}
```

---

## 6. 传输层协议栈设计

### 6.1 协议头设计

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
├───────────────────────────────────────────────────────────────┤
│                         Magic Number                          │
│                          (4 bytes)                            │
├───────────────────┬───────────┬───────────────┬───────────────┤
│   Serializer Type  │  Msg Type │    Status     │   Body Size   │
│     (1 byte)      │  (1 byte) │   (1 byte)    │   (4 bytes)   │
├───────────────────┴───────────┴───────────────┴───────────────┤
│                        Request ID                              │
│                         (8 bytes)                              │
├───────────────────────────────────────────────────────────────┤
│                       Protocol Body                            │
│                    (Body Size bytes)                            │
└───────────────────────────────────────────────────────────────┘
```

```java
public class RpcProtocol {
    public static final int HEADER_LENGTH = 19;
    public static final short MAGIC_NUMBER = 0xABCD;

    // Header fields
    private byte serializerType;   // 0:kryo, 1:protostuff, 2:hessian, 3:json
    private byte msgType;          // 0:request, 1:response, 2:heartbeat
    private byte status;           // 0:ok, 1:error
    private int bodyLength;        // 协议体长度
    private long requestId;        // 请求 ID
    private byte[] body;           // 协议体
}
```

### 6.2 协议体设计

```java
public class RpcRequest {
    private String group;          // 服务分组
    private String providerName;   // 服务名（接口全限定名）
    private String version;        // 服务版本
    private String methodName;     // 方法名
    private Object[] args;         // 参数列表
    private String traceId;        // 链路追踪 ID
    private String appName;        // 应用名
}
```

### 6.3 parameterTypes[] — 需要吗？

**问题**：
1. 反序列化时 `ClassLoader.loadClass()` 有锁竞争
2. 协议体码流体积增大
3. 泛化调用时参数类型增多

**解决方案**：利用 Java 方法的静态分派规则

Java 方法重载解析遵循 JLS §15.12.2.5（Choosing the Most Specific Method）：
- 不用传 `parameterTypes[]`，服务端可以根据方法名和参数个数 + 类型匹配
- **前提**：重载方法必须能通过参数类型唯一区分

```java
// 服务端查找方法逻辑（省去 parameterTypes[] 传输）
public Method findMethod(Class<?> serviceClass, String methodName, Object[] args) {
    for (Method m : serviceClass.getMethods()) {
        if (m.getName().equals(methodName) 
            && m.getParameterCount() == args.length) {
            // 再按类型匹配
            if (matchParameterTypes(m.getParameterTypes(), args)) {
                return m;
            }
        }
    }
    throw new NoSuchMethodException(methodName);
}
```

**最佳实践**：传输 overload 索引（int 值）代替完整类型字符串——体积小且无锁。

---

## 7. RPC 框架关键特性

### 7.1 序列化/反序列化

协议 header 标记 serializer type，支持同时多种序列化方式：

```java
public class RpcDecoder extends ByteToMessageDecoder {
    @Override
    protected void decode(ChannelHandlerContext ctx, ByteBuf in, List<Object> out) {
        if (in.readableBytes() < RpcProtocol.HEADER_LENGTH) return;

        in.markReaderIndex();
        short magic = in.readShort();
        if (magic != RpcProtocol.MAGIC_NUMBER) {
            in.resetReaderIndex();
            throw new RuntimeException("Magic number mismatch");
        }

        byte serializerType = in.readByte();
        byte msgType = in.readByte();
        byte status = in.readByte();
        int bodyLength = in.readInt();
        long requestId = in.readLong();

        if (in.readableBytes() < bodyLength) {
            in.resetReaderIndex();
            return; // 半包，等待更多数据
        }

        byte[] body = new byte[bodyLength];
        in.readBytes(body);

        // 根据 serializerType 选择反序列化器
        Serializer serializer = SerializerFactory.get(serializerType);
        if (msgType == 0) { // request
            RpcRequest req = serializer.deserialize(body, RpcRequest.class);
            req.setRequestId(requestId);
            out.add(req);
        } else { // response
            RpcResponse resp = serializer.deserialize(body, RpcResponse.class);
            resp.setRequestId(requestId);
            out.add(resp);
        }
    }
}
```

### 7.2 可扩展性（Java SPI）

```java
// META-INF/services/com.example.Serializer
// com.example.KryoSerializer
// com.example.ProtostuffSerializer
// com.example.HessianSerializer

public class SerializerFactory {
    private static final Map<Byte, Serializer> SERIALIZERS = new HashMap<>();

    static {
        ServiceLoader<Serializer> loader = ServiceLoader.load(Serializer.class);
        byte index = 0;
        for (Serializer s : loader) {
            SERIALIZERS.put(index++, s);
        }
    }

    public static Serializer get(byte type) {
        Serializer s = SERIALIZERS.get(type);
        if (s == null) throw new IllegalArgumentException("Unknown serializer: " + type);
        return s;
    }
}
```

### 7.3 服务级别线程池隔离

```java
public class ProviderThreadPoolManager {
    // 每个服务使用独立的线程池
    private final Map<String, ExecutorService> servicePools = new ConcurrentHashMap<>();

    public void submit(String serviceName, Runnable task) {
        ExecutorService pool = servicePools.computeIfAbsent(serviceName, 
            k -> createIsolatedPool(k));
        pool.submit(task);
    }

    private ExecutorService createIsolatedPool(String serviceName) {
        return new ThreadPoolExecutor(
            10, 20, 60, TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(1000),
            new ThreadFactoryBuilder().setNameFormat("rpc-" + serviceName + "-%d").build(),
            new ThreadPoolExecutor.CallerRunsPolicy()
        );
    }
}
```

**要挂你先挂，别拉着我**：高负载服务慢吞吞，但不会拖垮其他服务。

### 7.4 责任链拦截器

```java
public interface Filter {
    void invoke(RpcInvocation invocation, FilterChain chain);
}

public class FilterChain {
    private final List<Filter> filters;
    private int index = 0;

    public FilterChain(List<Filter> filters) {
        this.filters = filters;
    }

    public void doFilter(RpcInvocation invocation) {
        if (index >= filters.size()) {
            invocation.invoke(); // 执行真实调用
            return;
        }
        filters.get(index++).invoke(invocation, this);
    }
}
```

典型拦截器用途：鉴权、限流、日志、Metrics 采集、链路透传。

### 7.5 流控

```java
public class RateLimitFilter implements Filter {
    private final Map<String, RateLimiter> limiters = new ConcurrentHashMap<>();

    @Override
    public void invoke(RpcInvocation invocation, FilterChain chain) {
        RateLimiter limiter = limiters.computeIfAbsent(
            invocation.getServiceName(), k -> RateLimiter.create(1000));
        
        if (limiter.tryAcquire()) {
            chain.doFilter(invocation);
        } else {
            // 快速失败或降级
            invocation.fail(new RpcException("Rate limited"));
        }
    }
}
```

**要点**：流控接口设计要方便接入第三方中间件（Sentinel、Resilience4j 等）。

### 7.6 Provider 线程池满了怎么办

策略选择：
1. **拒绝策略**：返回 RPC 异常（快速失败）
2. **降级**：返回缓存结果（适合读多写少场景）
3. **排队等待**：设置合理超时，避免业务线程无限阻塞
4. **自动扩容**（动态线程池）：根据负载自动调整线程池大小

```java
// 动态线程池方案
public class DynamicThreadPool {
    private static final int CORE = 10;
    private static final int MAX = 200;
    
    // 基于队列深度动态调整
    public void adjustPoolSize() {
        int queueSize = executor.getQueue().size();
        if (queueSize > 100 && executor.getPoolSize() < MAX) {
            executor.setCorePoolSize(Math.min(
                executor.getPoolSize() + 10, MAX));
        } else if (queueSize == 0 && executor.getPoolSize() > CORE) {
            executor.setCorePoolSize(Math.max(
                executor.getPoolSize() - 5, CORE));
        }
    }
}
```

---

## 8. 客户端代理与调用模型

### 8.1 Proxy 职责

```
Consumer 调用 → Proxy → 集群容错 → 负载均衡 → 网络 → Provider
```

### 8.2 多种 Proxy 实现对比

| 方式 | 性能 | 复杂度 | 是否需要字节码 |
|------|------|--------|--------------|
| JDK Proxy | 一般 | 低 | 否（接口代理） |
| Javassist | 较快 | 中 | 是 |
| CGLib | 较快 | 中 | 是 |
| ASM | 极快 | 高 | 是 |
| **ByteBuddy** | **极快** | **低** | **是（推荐）** |

```java
// ByteBuddy 创建动态代理（推荐方案）
public class RpcProxyFactory {
    @SuppressWarnings("unchecked")
    public static <T> T createProxy(Class<T> interfaceClass, RpcClient client) {
        try {
            return (T) new ByteBuddy()
                .subclass(Object.class)
                .implement(interfaceClass)
                .method(ElementMatchers.anyOf(interfaceClass.getMethods()))
                .intercept(MethodDelegation.to(new RpcInvocationHandler(client)))
                .make()
                .load(interfaceClass.getClassLoader())
                .getLoaded()
                .newInstance();
        } catch (Exception e) {
            throw new RuntimeException("Failed to create proxy for " + interfaceClass, e);
        }
    }
}

public class RpcInvocationHandler {
    private final RpcClient client;

    public RpcInvocationHandler(RpcClient client) {
        this.client = client;
    }

    @RuntimeType
    public Object invoke(@Origin Method method, @AllArguments Object[] args) {
        // 1. 过滤 Object 方法（toString, equals, hashCode）
        if (isObjectMethod(method)) {
            return invokeObjectMethod(method, args);
        }
        // 2. 构造 RPC 请求
        RpcRequest req = RpcRequest.builder()
            .serviceName(method.getDeclaringClass().getName())
            .methodName(method.getName())
            .args(args)
            .build();
        // 3. 通过容错和负载均衡发送
        return client.invoke(req);
    }

    private boolean isObjectMethod(Method method) {
        String name = method.getName();
        return "toString".equals(name) || 
               "equals".equals(name) || 
               "hashCode".equals(name);
    }
}
```

### 8.3 同步/异步调用

```java
// 同步调用（包装异步 Future）
public class RpcClient {
    public Object invokeSync(RpcRequest req, long timeoutMs) {
        CompletableFuture<RpcResponse> future = invokeAsync(req);
        try {
            RpcResponse resp = future.get(timeoutMs, TimeUnit.MILLISECONDS);
            if (resp.isError()) {
                throw new RpcException(resp.getError());
            }
            return resp.getResult();
        } catch (TimeoutException e) {
            throw new RpcTimeoutException("Request timeout: " + req.getRequestId());
        }
    }

    // 异步调用
    public CompletableFuture<RpcResponse> invokeAsync(RpcRequest req) {
        CompletableFuture<RpcResponse> future = new CompletableFuture<>();
        Channel channel = loadBalancer.select(req);
        RpcClientHandler handler = channel.pipeline().get(RpcClientHandler.class);
        handler.send(req).whenComplete((resp, err) -> {
            if (err != null) future.completeExceptionally(err);
            else future.complete(resp);
        });
        return future;
    }
}
```

### 8.4 单播/组播

```java
// 消息派发器
public class MsgDispatcher {
    // 单播：选择一个 Provider 发送
    public CompletableFuture<RpcResponse> unicast(RpcRequest req) {
        Channel ch = loadBalancer.select(req);
        return send(ch, req);
    }

    // 组播：发送给多个 Provider 并等待全部返回
    public FutureGroup multicast(RpcRequest req, List<Channel> channels) {
        List<CompletableFuture<RpcResponse>> futures = channels.stream()
            .map(ch -> send(ch, req))
            .collect(Collectors.toList());
        return new FutureGroup(futures);
    }
}

// FutureGroup：聚合多个 CompletableFuture
public class FutureGroup {
    private final List<CompletableFuture<RpcResponse>> futures;

    public FutureGroup(List<CompletableFuture<RpcResponse>> futures) {
        this.futures = futures;
    }

    // 等待所有完成
    public List<RpcResponse> all() {
        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
        return futures.stream().map(CompletableFuture::join).collect(Collectors.toList());
    }

    // 返回第一个成功的
    public CompletableFuture<RpcResponse> any() {
        return (CompletableFuture<RpcResponse>) CompletableFuture.anyOf(
            futures.toArray(new CompletableFuture[0]));
    }
}
```

### 8.5 泛化调用

适用于**泛化调用**（Generic Invocation）场景：Consumer 没有服务接口的 class，只有方法名和参数。

```java
// 泛化调用接口
public interface GenericService {
    Object $invoke(String methodName, Object... args);
}

// 泛化调用实现
public class GenericServiceImpl implements GenericService {
    private final String interfaceName;

    @Override
    public Object $invoke(String methodName, Object... args) {
        // 通过 methodName + args 类型推断参数类型
        // 通过泛化序列化器处理
        return genericRpcClient.invoke(interfaceName, methodName, args);
    }
}

// 使用例
GenericService svc = (GenericService) RpcProxyFactory.createProxy(
    GenericService.class, client);
Object result = svc.$invoke("findUser", 123L);  // 不需要 UserService 接口
```

---

## 9. 负载均衡策略

### 9.1 加权随机（二分查找法）

```java
public class WeightedRandomLoadBalancer implements LoadBalancer {
    // 二分查找替代遍历 —— 时间复杂度 O(log n)
    @Override
    public Provider select(List<Provider> providers) {
        int[] prefixSum = new int[providers.size()];
        prefixSum[0] = providers.get(0).getWeight();
        for (int i = 1; i < providers.size(); i++) {
            prefixSum[i] = prefixSum[i - 1] + providers.get(i).getWeight();
        }

        int total = prefixSum[prefixSum.length - 1];
        int rand = ThreadLocalRandom.current().nextInt(total);
        int idx = Arrays.binarySearch(prefixSum, rand);
        if (idx < 0) idx = -idx - 1;
        return providers.get(idx);
    }
}
```

### 9.2 加权轮训（最大公约数优化）

```java
public class WeightedRoundRobinLoadBalancer implements LoadBalancer {
    private final AtomicInteger counter = new AtomicInteger(0);
    private volatile int gcd;  // 权重最大公约数

    @Override
    public Provider select(List<Provider> providers) {
        gcd = gcd(providers);
        int index = counter.getAndIncrement() % gcd;
        // 每个 provider 有 weight / gcd 个槽位
        for (int i = 0; i < providers.size(); i++) {
            if (index < providers.get(i).getWeight() / gcd) {
                return providers.get(i);
            }
            index -= providers.get(i).getWeight() / gcd;
        }
        return providers.get(0);
    }

    private int gcd(List<Provider> providers) {
        int result = providers.get(0).getWeight();
        for (int i = 1; i < providers.size(); i++) {
            result = gcd(result, providers.get(i).getWeight());
        }
        return result;
    }
}
```

### 9.3 最小负载

```java
public class LeastActiveLoadBalancer implements LoadBalancer {
    @Override
    public Provider select(List<Provider> providers) {
        // 选择当前活跃请求数最少的 Provider
        return providers.stream()
            .min(Comparator.comparingInt(Provider::getActiveCount))
            .orElseThrow(() -> new RpcException("No available providers"));
    }
}
```

### 9.4 一致性 Hash（有状态服务）

```java
public class ConsistentHashLoadBalancer implements LoadBalancer {
    private final TreeMap<Long, Provider> ring = new TreeMap<>();
    private static final int VIRTUAL_NODES = 160;  // 每个节点 160 个虚拟节点

    public void buildRing(List<Provider> providers) {
        ring.clear();
        for (Provider p : providers) {
            for (int i = 0; i < VIRTUAL_NODES; i++) {
                long hash = hash(p.getAddress() + "#" + i);
                ring.put(hash, p);
            }
        }
    }

    @Override
    public Provider select(RpcRequest req) {
        long hash = hash(req.getArgs()[0].toString());  // 按第一个参数 hash
        Map.Entry<Long, Provider> entry = ring.ceilingEntry(hash);
        if (entry == null) entry = ring.firstEntry();
        return entry.getValue();
    }
}
```

### 9.5 预热逻辑

新启动的服务应当从低权重开始，逐步提升到满载——避免冷启动时 JIT 未预热导致超时雪崩。

```java
public class WarmUpLoadBalancer implements LoadBalancer {
    private static final long WARMUP_DURATION_MS = 10 * 60 * 1000; // 10 分钟

    @Override
    public Provider select(List<Provider> providers) {
        Provider candidate = ...; // 选出一个 provider
        long uptime = System.currentTimeMillis() - candidate.getStartTime();
        if (uptime < WARMUP_DURATION_MS) {
            // 线性提升权重（0% → 100%）
            double ratio = (double) uptime / WARMUP_DURATION_MS;
            candidate.setWeight((int) (candidate.getMaxWeight() * ratio));
        }
        return candidate;
    }
}
```

---

## 10. 集群容错机制

### 10.1 Fail-fast

```java
public class FailFastCluster implements Cluster {
    @Override
    public RpcResponse invoke(RpcInvocation invocation) {
        Provider provider = loadBalancer.select(invocation.getProviders());
        try {
            return doInvoke(provider, invocation);
        } catch (Exception e) {
            // 只尝试一次，立即失败
            throw new RpcException("Fail-fast: " + e.getMessage(), e);
        }
    }
}
```

### 10.2 Failover（重试）

```java
public class FailoverCluster implements Cluster {
    private static final int DEFAULT_RETRIES = 2;

    @Override
    public RpcResponse invoke(RpcInvocation invocation) {
        List<Provider> providers = new ArrayList<>(invocation.getProviders());
        RpcException lastEx = null;

        for (int i = 0; i <= DEFAULT_RETRIES; i++) {
            if (providers.isEmpty()) break;
            Provider provider = loadBalancer.select(providers);
            try {
                return doInvoke(provider, invocation);
            } catch (RpcException e) {
                lastEx = e;
                providers.remove(provider);
                log.warn("Failover retry {}/{} for {} on {}: {}", 
                    i + 1, DEFAULT_RETRIES, invocation.getServiceName(), 
                    provider.getAddress(), e.getMessage());
            }
        }
        throw new RpcException("Failover exhausted, last error: " + lastEx.getMessage(), lastEx);
    }
}
```

### 10.3 Failover 异步调用

**❌ Bad**：异步重试在 callback 中发起新调用，逻辑混乱且难以跟踪。

```java
// Bad: callback 嵌套引发混乱
future.whenComplete((resp, err) -> {
    if (err != null) {
        // 在这里发起另一个异步调用再回调...
        nestedAsyncInvoke();
    }
});
```

**✅ Better**：使用 CompletableFuture 的组合能力。

```java
public class AsyncFailoverCluster implements Cluster {
    @Override
    public CompletableFuture<RpcResponse> invokeAsync(RpcInvocation invocation) {
        List<Provider> providers = new ArrayList<>(invocation.getProviders());

        CompletableFuture<RpcResponse> future = new CompletableFuture<>();
        tryInvoke(future, providers, invocation, 0);
        return future;
    }

    private void tryInvoke(CompletableFuture<RpcResponse> future,
                           List<Provider> providers,
                           RpcInvocation invocation, int attempt) {
        if (providers.isEmpty()) {
            future.completeExceptionally(
                new RpcException("All providers exhausted"));
            return;
        }

        Provider provider = loadBalancer.select(providers);
        doInvokeAsync(provider, invocation)
            .whenComplete((resp, err) -> {
                if (err != null) {
                    log.warn("Attempt {} failed on {}: {}", 
                        attempt + 1, provider.getAddress(), err.getMessage());
                    providers.remove(provider);
                    tryInvoke(future, providers, invocation, attempt + 1);
                } else {
                    future.complete(resp);
                }
            });
    }
}
```

### 10.4 Fail-safe

```java
public class FailSafeCluster implements Cluster {
    @Override
    public RpcResponse invoke(RpcInvocation invocation) {
        try {
            Provider provider = loadBalancer.select(invocation.getProviders());
            return doInvoke(provider, invocation);
        } catch (Exception e) {
            log.error("Fail-safe ignored error: ", e);
            return null;  // 静默失败，不抛异常
        }
    }
}
```

**适用场景**：日志上报、统计打点等非关键路径。

### 10.5 Fail-back

```java
public class FailBackCluster implements Cluster {
    private final ScheduledExecutorService executor = Executors.newScheduledThreadPool(4);
    private final Queue<RpcInvocation> retryQueue = new ConcurrentLinkedQueue<>();

    @Override
    public RpcResponse invoke(RpcInvocation invocation) {
        try {
            Provider provider = loadBalancer.select(invocation.getProviders());
            return doInvoke(provider, invocation);
        } catch (Exception e) {
            retryQueue.offer(invocation); // 入重试队列
            scheduleRetry(invocation);
            return null; // 或返回默认值
        }
    }

    private void scheduleRetry(RpcInvocation invocation) {
        executor.schedule(() -> {
            RpcInvocation task = retryQueue.poll();
            if (task != null) {
                try { 
                    // 定期重试直到成功
                    Provider p = loadBalancer.select(task.getProviders());
                    doInvoke(p, task);
                } catch (Exception ignored) {}
            }
        }, 10, TimeUnit.SECONDS);
    }
}
```

### 10.6 Forking

```java
public class ForkingCluster implements Cluster {
    private static final int FORK_COUNT = 2;  // 同时发 2 个节点

    @Override
    public RpcResponse invoke(RpcInvocation invocation) {
        List<Provider> providers = invocation.getProviders();
        List<CompletableFuture<RpcResponse>> futures = providers.stream()
            .limit(FORK_COUNT)
            .map(p -> doInvokeAsync(p, invocation))
            .collect(Collectors.toList());

        // 谁先返回用谁，其余取消
        CompletableFuture<RpcResponse> future = 
            (CompletableFuture<RpcResponse>) CompletableFuture.anyOf(
                futures.toArray(new CompletableFuture[0]));

        try {
            RpcResponse resp = future.get(500, TimeUnit.MILLISECONDS);
            // 取消其他未完成的请求
            futures.forEach(f -> f.cancel(true));
            return resp;
        } catch (Exception e) {
            throw new RpcException("Forking failed", e);
        }
    }
}
```

**适用场景**：对延迟极敏感的读操作（如首页推荐），用资源换速度。

---

## 11. 序列化/反序列化深度优化

### 11.1 在业务线程中序列化

```java
// ❌ 错误：在 IO 线程序列化
public class RpcEncoder extends MessageToByteEncoder<RpcRequest> {
    @Override
    protected void encode(ChannelHandlerContext ctx, RpcRequest req, ByteBuf out) {
        byte[] bytes = serializer.serialize(req);  // 占用 IO 线程！
        out.writeBytes(bytes);
    }
}

// ✅ 正确：提前序列化，IO 线程只做内存拷贝
public class RpcClientProxy {
    public Object invoke(RpcRequest req) {
        // 在业务线程中序列化
        byte[] bytes = serializerFactory.get(req.getSerializerType())
            .serialize(req);
        // IO 线程只写 ByteBuf
        channel.writeAndFlush(Unpooled.wrappedBuffer(bytes));
    }
}
```

### 11.2 String 编码/解码优化

```java
// 使用正确的编码，避免 Charset.forName 每次查表
public class SerializerConstants {
    public static final Charset UTF_8 = StandardCharsets.UTF_8;
    public static final Charset ISO_8859_1 = StandardCharsets.ISO_8859_1;
}
```

### 11.3 Varint 编码优化

```java
// 合并多次 writeByte 成 writeShort/writeInt/writeLong
public class VarintOptimizer {
    // Before: 4 次 writeByte
    public void writeInt32(ByteBuf buf, int value) {
        // After: 1 次 writeInt
        buf.writeInt(value);
    }

    // Before: 8 次 writeByte  
    public void writeInt64(ByteBuf buf, long value) {
        // After: 1 次 writeLong
        buf.writeLong(value);
    }
}
```

### 11.4 直接读写堆外内存

传统流程：
```
Java Object → byte[] → 堆外内存 (Direct Buffer)
堆外内存 → byte[] → Java Object
```

优化：**省去 byte[] 中间环节**

```java
// 使用 Protostuff 扩展：UnsafeNioBufInput/Output 直接读写堆外内存
public class ProtostuffNioSerializer implements Serializer {
    @Override
    public void serialize(Object obj, ByteBuf buf) {
        // LinkedBuffer 使用 Netty 的 ByteBuf 分配
        LinkedBuffer buffer = LinkedBuffer.use(ByteBufAllocator.DEFAULT.buffer());
        try {
            // 直接写 ByteBuf，跳过 byte[] 中间拷贝
            ProtostuffIOUtil.writeTo(buf.nioBuffer(), obj, SCHEMA, buffer);
        } finally {
            buffer.clear();
        }
    }
}
```

### 11.5 序列化框架对比

| 框架 | 速度 | 码流大小 | 跨语言 |
|------|------|---------|--------|
| **Kryo** | 极快 | 小 | 否（Java only） |
| **Protostuff** | 极快 | 小 | 是 |
| **Protobuf** | 快 | 小 | 是 |
| **Hessian** | 中等 | 中 | 是 |
| **Fastjson** | 中等 | 大 | 是 |

**推荐**：无跨语言需求用 Kryo，有跨语言用 Protobuf。

---

## 12. Epoll 深度解析：从原理到 Netty 集成

### 12.1 select/poll 的局限

- **轮询检测**就绪事件，每次都要遍历全部 fd，O(n)
- 每次将整个 fd_set 在**用户空间和内核空间**之间拷贝
- select 有最大 fd 数限制（1024）
- poll 取消数量限制但本质相同

### 12.2 Epoll 三大系统调用

```c
// 1. epoll_create — 创建 epoll 实例
int epoll_create(int size);
// 创建红黑树 (rb-tree) + 就绪链表 (ready-list)
// 红黑树 O(log n)，平衡效率和内存占用
// size 参数已无意义（早期 hash 表实现时需要）

// 2. epoll_ctl — 注册/修改/删除关注的事件
int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event);
// 将 epitem 放入 rb-tree
// 向内核中断处理程序注册 ep_poll_callback

// 3. epoll_wait — 等待事件就绪
int epoll_wait(int epfd, struct epoll_event *events, int maxevents, int timeout);
// 从 ready-list 拷贝到 events[] 数组
// 返回就绪 fd 数量
```

### 12.3 Epoll 数据结构

```
┌─────────────────────────────────────────────────┐
│                  Epoll Instance                   │
│  ┌─────────────────────────────────────────────┐ │
│  │              Red-Black Tree                  │ │
│  │  (存储所有注册的 fd，按 fd 排序)              │ │
│  │  ┌───────────┐  ┌───────────┐               │ │
│  │  │ fd=3      │  │ fd=7      │               │ │
│  │  │ epitem    │  │ epitem    │               │ │
│  │  │ callback  │  │ callback  │               │ │
│  │  └───────────┘  └───────────┘               │ │
│  └─────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────┐ │
│  │               Ready List                     │ │
│  │          (就绪的双向链表)                      │ │
│  │  ┌───────────┐  ┌───────────┐               │ │
│  │  │ fd=3      │  │ fd=12     │               │ │
│  │  └───────────┘  └───────────┘               │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### 12.4 Epoll LT（水平触发）vs ET（边沿触发）

| 特性 | LT（Level-Triggered） | ET（Edge-Triggered） |
|------|---------------------|---------------------|
| 触发条件 | buffer 不为空/有空间 | 状态发生变化时 |
| 通知频率 | 一直通知直到数据读完 | 只通知一次 |
| 处理要求 | 可以分批读取 | 必须一次性读完 |
| 使用难度 | 简单 | 复杂（容易丢数据） |
| 性能 | 可能重复通知 | 更高 |

**Netty NIO 默认 LT**（Java NIO Selector 的 epoll 实现是 LT）

**Netty Native Transport 支持 ET**，需要在 Handler 中实现非阻塞读取：

```java
// Netty Native Transport 使用 ET 模式
public class EpollEtServer {
    public static void main(String[] args) {
        EventLoopGroup boss = new EpollEventLoopGroup(1);
        EventLoopGroup worker = new EpollEventLoopGroup();

        ServerBootstrap b = new ServerBootstrap();
        b.group(boss, worker)
         .channel(EpollServerSocketChannel.class)
         .option(EpollChannelOption.EPOLL_MODE, EpollMode.EDGE_TRIGGERED)  // ET mode
         .childHandler(...);
    }
}
```

### 12.5 Epoll 工作流程

```
1. epoll_wait 调用 ep_poll
   │
   ├─ rdlist 为空 → 挂起当前线程
   │               ↓
   │               fd events 状态变化（buffer 可读/可写）
   │               ↓
   │               ep_poll_callback 被触发
   │               ↓
   │               将 epitem 加入 rdlist
   │               ↓
   │               线程被唤醒
   │               ↓
   └─ rdlist 不为空 → 继续执行

2. ep_events_transfer
   └─ rdlist → txlist（拷贝）
   └─ rdlist 清空
   └─ 如果是 LT：epitem 重新放回 rdlist（如果 events 状态没变）

3. ep_send_events
   └─ 扫描 txlist 中每个 epitem
   └─ 调用 fd 关联的 poll 方法取得最新 events
   └─ 将 events + fd 发送到用户空间
```

---

## 13. Netty 内存管理揭秘

### 13.1 PooledByteBufAllocator

基于 **jemalloc 3.x** 论文实现的内存分配器：

```
PooledByteBufAllocator
├─ ThreadLocal Cache （无锁分配，最优先）
│   ├─ tiny (0-512 bytes, 16 sub sizes)
│   ├─ small (512B-8KB, 16 sub sizes)
│   └─ normal (8KB-16MB, 64 sub sizes)
├─ Arena（多区域，减少竞争）
│   ├─ PoolChunkList（Chunk 管理）
│   │   ├─ qInit
│   │   ├─ q000
│   │   ├─ q025
│   │   ├─ q050
│   │   └─ q075
│   └─ PoolSubPage（小对象管理）
└─ 全局 Pool（兜底）
```

**注意坑**：申请线程与归还线程不是同一个导致内存泄漏。Netty 后来用 mpsc_queue 解决，代价是牺牲了一点性能。

### 13.2 Recycler

**轻量级对象池**，ThreadLocal + Stack 实现：

```
Recycler
└─ ThreadLocal → Stack（主栈）
    └─ 归还实现
        └─ 同线程归还 → 直接 push 到 stack（无锁）
        └─ 不同线程归还 → push 到关联的 WeakOrderQueue
            └─ WeakOrderQueue 是多个数组的链表
            └─ 每个数组默认 size=16
            └─ 下次 pop 时，如果 stack 为空
               → 先扫描所有关联的 WeakOrderQueue
```

**GC 隐患**：年老者引用新生代——老年代对象持有年轻代对象的引用，minor GC 时无法回收年轻代（跨代引用问题）。

### 13.3 堆外内存管理

**JDK 的问题**：
- `DirectByteBuffer` 的 `Cleaner` 虚引用负责释放 direct memory
- `DirectByteBuffer` 如果晋升到老年代，堆外内存就会被延迟释放
- `Bits.reserveMemory()` 在分配失败时会显式触发 `System.gc()`（sleep 100ms 后重试）
- 如果设置了 `-XX:+DisableExplicitGC`，直接 OOM

**Netty 的解决方案**：

```java
// 使用 UnpooledUnsafeNoCleanerDirectByteBuf
// 去掉 cleaner，框架维护引用计数来实时释放

// 配置方式
-Dio.netty.maxDirectMemory=0

// 参数含义：
// < 0:  不使用 cleaner，继承 JDK 的最大 direct memory 设置
// == 0: 使用 cleaner，Netty 不设上限
// > 0:  不使用 cleaner，这个值直接限制 Netty 的最大 direct memory
```

---

## 14. Netty Native Transport

### 14.1 为什么用 Native Transport

相比 NIO：
- **创建更少的对象**，更小 GC 压力
- **针对 linux 平台深度优化**
- **锁更少**，Java NIO 的 `synchronized` 调用大幅减少

### 14.2 使用方式

```xml
<dependency>
    <groupId>io.netty</groupId>
    <artifactId>netty-transport-native-epoll</artifactId>
    <version>4.1.116.Final</version>
    <classifier>linux-x86_64</classifier>
</dependency>
```

```java
// 使用 EpollEventLoopGroup 代替 NioEventLoopGroup
EventLoopGroup boss = new EpollEventLoopGroup(1);
EventLoopGroup worker = new EpollEventLoopGroup();

ServerBootstrap b = new ServerBootstrap();
b.channel(EpollServerSocketChannel.class);  // 代替 NioServerSocketChannel
```

### 14.3 Linux 专属特性

**SO_REUSEPORT** — 端口复用

```java
b.option(EpollChannelOption.SO_REUSEPORT, true);
```

允许多个 socket 监听同一个 IP+端口，配合 RPS/RFS（Receive Packet Steering / Flow Steering），在软件层面模拟多队列网卡，避免网卡中断集中在某个 CPU core 上。

**TCP_FASTOPEN**

```java
b.option(EpollChannelOption.TCP_FASTOPEN, 5);
// 3 次握手时也用来交换数据，减少 1 个 RTT
```

**EDGE_TRIGGERED**

```java
b.childOption(EpollChannelOption.EPOLL_MODE, EpollMode.EDGE_TRIGGERED);
```

**Unix Domain Socket**

```java
b.channel(EpollServerDomainSocketChannel.class);
// 同一台机器上进程间通信，比 TCP loopback 更快
// Service Mesh 场景常用
```

---

## 15. Netty 最佳实践（13 条生产级）

### 15.1 业务线程池必要性

```java
// ❌ 错误：在 IO 线程处理业务
public class BadHandler extends ChannelInboundHandlerAdapter {
    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) {
        // 阻塞业务逻辑！占用 IO 线程！
        Thread.sleep(1000);
        processBusiness(msg);
    }
}

// ✅ 正确：分发给业务线程池
public class GoodHandler extends ChannelInboundHandlerAdapter {
    private final ExecutorService bizPool = Executors.newFixedThreadPool(16);

    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) {
        bizPool.submit(() -> {
            processBusiness(msg);
            ctx.writeAndFlush(result);
        });
    }
}
```

**原则**：业务逻辑尤其是阻塞时间较长的逻辑，不要占用 Netty 的 IO 线程。

### 15.2 WriteBufferWaterMark

```java
// 默认高低水位：32K ~ 64K
// WriteBufferWaterMark.DEFAULT = new WriteBufferWaterMark(32768, 65536);

// 根据场景调整
b.childOption(ChannelOption.WRITE_BUFFER_WATER_MARK,
    new WriteBufferWaterMark(512 * 1024, 1024 * 1024));  // 512K ~ 1M
```

**利用水位线实现背压**：
```java
// 当写缓冲超过高水位时，停止读取
public class BackPressureHandler extends ChannelInboundHandlerAdapter {
    @Override
    public void channelWritabilityChanged(ChannelHandlerContext ctx) {
        if (!ctx.channel().isWritable()) {
            ctx.channel().config().setAutoRead(false);  // 暂停读取
        } else {
            ctx.channel().config().setAutoRead(true);   // 恢复读取
        }
    }
}
```

### 15.3 重写 MessageSizeEstimator

```java
// 默认实现不能正确计算对象大小（write 时还没开始 encode）
// 建议根据业务对象重写
b.childOption(ChannelOption.MESSAGE_SIZE_ESTIMATOR,
    new MessageSizeEstimator() {
        @Override
        public MessageHandle newHandle() {
            return msg -> {
                if (msg instanceof ByteBuf) {
                    return ((ByteBuf) msg).readableBytes();
                }
                return 256;  // 估算值
            };
        }
    });
```

### 15.4 ioRatio 设置

```java
// EventLoop 执行 IO 和非 IO 任务的时间比例
// 默认 50（各占一半）
EventLoopGroup worker = new NioEventLoopGroup(4, new DefaultThreadFactory("worker"));
// 可以在 EventLoop 中调整
```

**调优建议**：
- **高 IO 负载**（如网关）：`ioRatio = 70`，IO 占更多时间
- **高计算负载**：`ioRatio = 30`，减少 IO 时间占比

### 15.5 空闲链路检测

```java
// 默认：使用 IO 线程调度（EventLoop 的 delayQueue，O(log n)）
// 连接数 < 几万：这种方式没问题

// 连接数很大时：使用 HashedWheelTimer（O(1)）
HashedWheelTimer timer = new HashedWheelTimer(
    new DefaultThreadFactory("idle-check"), 
    100, TimeUnit.MILLISECONDS, 512);

// 注：HashedWheelTimer 使 IO 和 idle 互不影响，但有上下文切换开销
```

**经验法则**：连接数 < 30000 用默认方式；超过用 HashedWheelTimer。

### 15.6 ctx.writeAndFlush vs channel.writeAndFlush

```java
// ctx.writeAndFlush — 从下一个 outbound handler 开始
ctx.writeAndFlush(msg);  // 跳过当前 handler 之前的所有 handler

// channel.writeAndFlush — 从 pipeline 末尾倒着向前
channel.writeAndFlush(msg);  // 经过所有 outbound handler（包括空闲检测等）
```

**👉 注意**：`ctx.write` 可能会绕过空闲链路检测等 handler，要确保不会违背设计意图。

### 15.7 ByteBuf.forEachByte()

```java
// ❌ 避免：循环 readByte，每次触发 rangeCheck()
for (int i = 0; i < length; i++) {
    byte b = buf.readByte();
    process(b);
}

// ✅ 推荐：forEachByte()，避免 rangeCheck()
buf.forEachByte(new ByteProcessor() {
    @Override
    public boolean process(byte value) {
        process(value);
        return true;
    }
});
```

### 15.8 CompositeByteBuf

```java
// ❌ 需要多次 copy 的场景
ByteBuf header = ...;
ByteBuf body = ...;
ByteBuf merged = Unpooled.buffer(header.readableBytes() + body.readableBytes());
merged.writeBytes(header);
merged.writeBytes(body);

// ✅ CompositeByteBuf：避免内存拷贝
CompositeByteBuf composite = Unpooled.compositeBuffer();
composite.addComponents(true, header, body);  // true: auto increase writer index
```

**缺点**：索引计算时间复杂度从 O(1) 变为 O(n)，根据场景衡量是否值得。

### 15.9 readInt() 代替 readBytes()

```java
// ❌ 读 4 字节再转 int — 多一次 memory copy
byte[] buf = new byte[4];
byteBuf.readBytes(buf, 0, 4);
int value = ((buf[0] & 0xFF) << 24) | ...;

// ✅ 直接 readInt()
int value = byteBuf.readInt();  // long/Short 同理
```

### 15.10 配置 UnpooledUnsafeNoCleanerDirectByteBuf

```java
-Dio.netty.maxDirectMemory=0
```

参数含义见第 13.3 节。让 Netty 框架基于引用计数实时释放堆外内存，不受 JDK Cleaner 虚引用延迟释放的影响。

### 15.11 最佳连接数

```
一条连接 → 无法有效利用多核 CPU
太多连接 → 浪费文件描述符，上下文切换增加
```

**最佳实践**：通过压测找到最优值。通常 `Worker 线程数 × (1~3)` 条连接即可。

### 15.12 泄漏检测

```java
// 启动参数（推荐开发环境用 ADVANCED，生产用 SIMPLE）
-Dio.netty.leakDetection.level=SIMPLE

// 级别：
// DISABLED  — 禁用（生产环境确认无泄漏后可开）
// SIMPLE    — 采样模式，<1% 采样（默认），日志出现 "LEAK:" 字样
// ADVANCED  — 采样模式，报告泄漏发生位置
// PARANOID  — 100% 采样，测试环境使用
```

**定期 grep 日志 `LEAK:`**，如果发现立刻改为 ADVANCED 重新跑。

### 15.13 Channel.attr()

```java
// 定义 AttributeKey
public static final AttributeKey<String> SESSION_KEY = 
    AttributeKey.valueOf("sessionKey");

// 在连接建立时存入
@Override
public void channelActive(ChannelHandlerContext ctx) {
    ctx.channel().attr(SESSION_KEY).set(generateSessionId());
}

// 在其他 handler 中读取
String sessionId = ctx.channel().attr(SESSION_KEY).get();
```

**实现原理**：拉链法 + 分段锁（只锁链表头），类似 `ConcurrentHashMap V8`。默认只有 4 个桶，不要太任性。

---

## 16. 从 Netty 源码学到的代码技巧

### 16.1 AtomicIntegerFieldUpdater 代替 AtomicInteger

```java
// ❌ 海量对象场景：每个对象多 16 bytes
public class BadNode {
    private final AtomicInteger refCount = new AtomicInteger(1); // +16 bytes
}

// ✅ 使用 AtomicIntegerFieldUpdater：节省对象内存
public class GoodNode {
    private static final AtomicIntegerFieldUpdater<GoodNode> REF_UPDATER =
        AtomicIntegerFieldUpdater.newUpdater(GoodNode.class, "refCount");

    @SuppressWarnings("unused")
    private volatile int refCount = 1;

    public boolean release() {
        return REF_UPDATER.decrementAndGet(this) == 0;
    }
}
```

**原因**：Java 对象头 12 bytes（开启压缩指针），按 8 字节对齐最小 16 bytes。`AtomicInteger` 本身又是一个 16 bytes 的对象。

### 16.2 FastThreadLocal

```java
// Netty 的 FastThreadLocal 比 JDK 的 ThreadLocal 更快
// 实现：线性探测 Hash 表 → index 原子自增的裸数组

// 使用方式
private static final FastThreadLocal<MessageBuf> LOCAL_BUF = 
    new FastThreadLocal<MessageBuf>() {
        @Override
        protected MessageBuf initialValue() {
            return MessageBuf.newInstance();
        }
    };
```

**注意**：`FastThreadLocal` 需要配合 `FastThreadLocalThread` 使用。

### 16.3 IntObjectHashMap

```java
// Netty 实现的 Int → Object 映射，比 HashMap<Integer, V> 更高效
// 优化点：
// 1. int 代替 Integer（避免装箱）
// 2. Node[] 裸数组代替 Entry 对象（减少对象数量）

IntObjectHashMap<Provider> map = new IntObjectHashMap<>();
```

### 16.4 RecyclableArrayList

```java
// 频繁创建 ArrayList 的场景使用 RecyclableArrayList
// 基于 Recycler 实现

RecyclableArrayList list = RecyclableArrayList.newInstance();
try {
    list.add(item);
    // ... 使用 list
} finally {
    list.recycle();  // 归还到对象池
}
```

### 16.5 JCTools

Netty 依赖 JCTools 提供的无锁队列：

| 队列 | 描述 | 适用场景 |
|------|------|---------|
| `MPSC` | 多生产者单消费者 | Netty EventLoop 的任务队列 |
| `SPSC` | 单生产者单消费者 | 最高性能 |
| `SPMC`/`MPMC` | 多生产者多消费者 | 少用 |
| `NonblockingHashMap` | 无锁 HashMap | 高性能缓存 |

---

## 17. 性能压榨：压测驱动的极致优化

### 17.1 ASM FastMethodAccessor

```java
// ❌ 服务端反射调用性能差
Method method = serviceClass.getMethod(methodName, paramTypes);
Object result = method.invoke(serviceObject, args);

// ✅ ASM 写入一个 FastMethodAccessor 代替反射
public class FastMethodAccessor {
    // 用 ASM 动态生成，直接调用目标方法
    // 性能接近直接调用，跳过反射校验
    public Object invoke(Object target, Object[] args) {
        // 生成的字节码等同于：
        // ((UserServiceImpl)target).findUser((Long)args[0]);
    }
}
```

**原则**：Don't trust it, test it — 所有优化都必须通过压测验证。

### 17.2 IO 线程绑定 CPU

```java
// Linux 上可以将 IO 线程绑定到特定 CPU core
// 避免线程上下文切换

// 方案一：使用 taskset
// taskset -c 0-3 java -jar rpc-server.jar

// 方案二：通过 JNI 调用 sched_setaffinity
// 将 Worker IO 线程固定到特定核
```

### 17.3 客户端协程

同步阻塞调用的客户端容易成为瓶颈，但 Java 协程选择不多：

| 方案 | 描述 | 优缺点 |
|------|------|--------|
| **Kilim** | 编译期字节码增强 | 成熟但较老 |
| **Quasar** | agent 动态字节码增强 | 功能强大但调试困难 |
| **Alibaba Wisp** | Ali JVM 底层直接实现 | 对应用透明，但需定制 JVM |
| **Project Loom** (JDK 21+) | JDK 官方虚拟线程 | 现代方案，推荐 |

### 17.4 尽快释放 IO 线程

```java
// 核心原则：IO 线程只做 IO，不做业务
// 1. 在业务线程中序列化/反序列化
// 2. 在业务线程中执行业务逻辑
// 3. IO 线程只负责：读/写 ByteBuf

// 减少线程上下文切换 = 高性能
```

---

## 18. 完整 RPC 框架实战

下面一步步实现一个迷你 RPC 框架，综合前面所有知识点。

### 18.1 项目结构

```
mini-rpc/
├── api/
│   ├── HelloService.java          # 服务接口
│   └── HelloResponse.java         # 响应对象
├── provider/
│   ├── HelloServiceImpl.java      # 服务实现
│   └── RpcServer.java             # 服务端启动类
├── consumer/
│   └── RpcClient.java             # 客户端启动类
└── rpc-core/
    ├── protocol/
    │   ├── RpcProtocol.java       # 协议定义
    │   ├── RpcRequest.java        # 请求对象
    │   └── RpcResponse.java       # 响应对象
    ├── codec/
    │   ├── RpcEncoder.java        # 编码器
    │   └── RpcDecoder.java        # 解码器
    ├── serializer/
    │   └── KryoSerializer.java    # 序列化
    ├── registry/
    │   └── LocalRegistry.java     # 注册中心
    ├── loadbalance/
    │   └── RandomLoadBalancer.java
    ├── cluster/
    │   └── FailoverCluster.java   # 集群容错
    └── proxy/
        └── RpcProxyFactory.java   # 代理工厂
```

### 18.2 服务端代码

```java
// rpc-core/protocol/RpcProtocol.java
public class RpcProtocol {
    public static final int HEADER_LENGTH = 19;
    public static final short MAGIC = 0xABCD;
    
    public static ByteBuf encode(RpcRequest req) {
        ByteBuf buf = Unpooled.buffer();
        buf.writeShort(MAGIC);
        buf.writeByte(req.getSerializerType());
        buf.writeByte(req.getMsgType());
        buf.writeByte(0);  // status
        // body 先用 kryo 序列化
        byte[] body = KryoSerializer.serialize(req.getBody());
        buf.writeInt(body.length);
        buf.writeLong(req.getRequestId());
        buf.writeBytes(body);
        return buf;
    }
}

// provider/RpcServer.java
public class RpcServer {
    private final int port;
    private final Map<String, Object> services = new ConcurrentHashMap<>();

    public RpcServer(int port) {
        this.port = port;
    }

    public void register(Class<?> interfaceClass, Object impl) {
        services.put(interfaceClass.getName(), impl);
    }

    public void start() throws InterruptedException {
        EventLoopGroup boss = new NioEventLoopGroup(1);
        EventLoopGroup worker = new NioEventLoopGroup();

        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(boss, worker)
             .channel(NioServerSocketChannel.class)
             .childHandler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 protected void initChannel(SocketChannel ch) {
                     ch.pipeline()
                       .addLast(new RpcDecoder())        // 解码
                       .addLast(new RpcEncoder())        // 编码
                       .addLast(new RpcServerHandler(services));  // 业务处理
                 }
             });

            ChannelFuture f = b.bind(port).sync();
            System.out.println("RPC Server started on port " + port);
            f.channel().closeFuture().sync();
        } finally {
            boss.shutdownGracefully();
            worker.shutdownGracefully();
        }
    }
}

// rpc-core/codec/RpcDecoder.java
public class RpcDecoder extends ByteToMessageDecoder {
    @Override
    protected void decode(ChannelHandlerContext ctx, ByteBuf in, List<Object> out) {
        if (in.readableBytes() < RpcProtocol.HEADER_LENGTH) return;

        in.markReaderIndex();
        short magic = in.readShort();
        if (magic != RpcProtocol.MAGIC) {
            in.resetReaderIndex();
            throw new RuntimeException("Bad magic number: " + magic);
        }

        byte serializerType = in.readByte();
        byte msgType = in.readByte();
        byte status = in.readByte();
        int bodyLength = in.readInt();
        long requestId = in.readLong();

        if (in.readableBytes() < bodyLength) {
            in.resetReaderIndex();
            return;  // 半包，等待更多数据
        }

        byte[] body = new byte[bodyLength];
        in.readBytes(body);

        if (msgType == 0) { // request
            RpcRequest.ProtocolBody reqBody = KryoSerializer.deserialize(body, 
                RpcRequest.ProtocolBody.class);
            reqBody.setRequestId(requestId);
            out.add(reqBody);
        } else { // response
            RpcResponse.ProtocolBody respBody = KryoSerializer.deserialize(body,
                RpcResponse.ProtocolBody.class);
            respBody.setRequestId(requestId);
            out.add(respBody);
        }
    }
}

// rpc-core/RpcServerHandler.java
public class RpcServerHandler extends SimpleChannelInboundHandler<RpcRequest.ProtocolBody> {
    private final Map<String, Object> services;

    @Override
    protected void channelRead0(ChannelHandlerContext ctx, RpcRequest.ProtocolBody req) {
        // 在业务线程池中执行
        ctx.executor().parent().next().submit(() -> {
            try {
                // 查找服务
                Object service = services.get(req.getProviderName());
                // 查找方法
                Method method = findMethod(service.getClass(), req);
                // 反射调用
                Object result = method.invoke(service, req.getArgs());
                
                // 构造响应
                RpcResponse.ProtocolBody resp = new RpcResponse.ProtocolBody();
                resp.setRequestId(req.getRequestId());
                resp.setResult(result);
                
                ctx.writeAndFlush(resp);
            } catch (Exception e) {
                log.error("Invoke error", e);
                RpcResponse.ProtocolBody error = new RpcResponse.ProtocolBody();
                error.setRequestId(req.getRequestId());
                error.setError(e.getMessage());
                ctx.writeAndFlush(error);
            }
        });
    }
}
```

### 18.3 客户端代码

```java
// rpc-core/proxy/RpcProxyFactory.java
public class RpcProxyFactory {
    @SuppressWarnings("unchecked")
    public static <T> T create(Class<T> interfaceClass, RpcClient client) {
        // 使用 ByteBuddy 创建动态代理
        return (T) new ByteBuddy()
            .subclass(Object.class)
            .implement(interfaceClass)
            .method(ElementMatchers.not(ElementMatchers.isDeclaredBy(Object.class)))
            .intercept(MethodDelegation.to(new InvocationHandler(client)))
            .make()
            .load(interfaceClass.getClassLoader())
            .getLoaded()
            .newInstance();
    }
}

// consumer/RpcClient.java
public class RpcClient {
    private final String host;
    private final int port;
    private Channel channel;
    private final Map<Long, CompletableFuture<RpcResponse.ProtocolBody>> pending =
        new ConcurrentHashMap<>();
    private final AtomicLong requestIdGen = new AtomicLong(0);

    public RpcClient(String host, int port) {
        this.host = host;
        this.port = port;
    }

    public void connect() throws InterruptedException {
        EventLoopGroup worker = new NioEventLoopGroup();
        Bootstrap b = new Bootstrap();
        b.group(worker)
         .channel(NioSocketChannel.class)
         .handler(new ChannelInitializer<SocketChannel>() {
             @Override
             protected void initChannel(SocketChannel ch) {
                 ch.pipeline()
                   .addLast(new RpcDecoder())
                   .addLast(new RpcEncoder())
                   .addLast(new RpcClientHandler(pending));
             }
         });

        channel = b.connect(host, port).sync().channel();
    }

    public CompletableFuture<RpcResponse.ProtocolBody> invoke(RpcRequest.ProtocolBody req) {
        long requestId = requestIdGen.incrementAndGet();
        req.setRequestId(requestId);
        
        CompletableFuture<RpcResponse.ProtocolBody> future = new CompletableFuture<>();
        pending.put(requestId, future);
        channel.writeAndFlush(req);
        return future;
    }
}

// 使用示例
public static void main(String[] args) {
    // 客户端
    RpcClient client = new RpcClient("localhost", 8888);
    client.connect();

    HelloService svc = RpcProxyFactory.create(HelloService.class, client);
    HelloResponse resp = svc.sayHello("Netty");
    System.out.println(resp.getMessage());

    // 服务端
    RpcServer server = new RpcServer(8888);
    server.register(HelloService.class, new HelloServiceImpl());
    server.start();
}
```

---

## 19. 常见问题与排查指南

### 19.1 连接已建立但无法收发数据

**可能原因**：
- Pipeline 中 Handler 顺序错误（Decoder 应在业务 Handler 之前）
- `channelRead` 没有调用 `ctx.fireChannelRead()` 传递消息
- write 后没有 flush

### 19.2 内存泄漏

**排查步骤**：
```bash
# 1. 开启泄漏检测
-Dio.netty.leakDetection.level=ADVANCED

# 2. 定期 grep 日志
grep "LEAK:" app.log

# 3. 使用 PARANOID 在测试环境 100% 采样
-Dio.netty.leakDetection.level=PARANOID
```

### 19.3 CPU 100%

**可能原因**：
- Epoll 空轮询 Bug（已由 Netty 自动 workaround，但检查是否在用老版本）
- IO 线程被阻塞（业务逻辑未分派到业务线程池）
- `channel.writeAndFlush` 频繁导致的内核态切换

### 19.4 Direct Memory OOM

```bash
# 检查参数冲突
-XX:MaxDirectMemorySize=512m
-Dio.netty.maxDirectMemory=0
# 不要同时设置

# 堆外内存泄露排查
-Dio.netty.leakDetection.level=ADVANCED
jcmd <pid> VM.native_memory
pmap -x <pid> | head
```

### 19.5 连接数多后性能下降

**排查方向**：
- `fdToKey` HashMap rehash（使用 Native Transport 缓解）
- `Selector.keys()` 遍历（Netty 已优化为双数组）
- HashedWheelTimer 是否生效（见 15.5）

---

## 20. 总结与学习路径

### 20.1 核心知识点回顾

```
Netty 学习路线
├── 第一阶段：基础入门
│   ├── BIO/NIO/AIO 模型理解
│   ├── Netty Echo Server/Client
│   ├── ChannelHandler & Pipeline
│   └── 粘包/半包处理
├── 第二阶段：进阶架构
│   ├── EventLoop 线程模型
│   ├── ByteBuf & PooledBuffer
│   ├── Netty Native Transport
│   └── 内存管理（Recycler, Leak Detection）
├── 第三阶段：RPC 框架设计
│   ├── RPC 三元组 & 调用流程
│   ├── 协议栈设计（编解码器）
│   ├── 负载均衡 & 集群容错
│   └── SPI & 拦截器链
├── 第四阶段：极致性能
│   ├── ASM FastMethodAccessor
│   ├── 序列化优化（直接读写堆外）
│   ├── IO 线程绑定 CPU
│   └── 协程化（Virtual Threads）
└── 第五阶段：底层原理
    ├── Epoll LT vs ET
    ├── JCTools 无锁队列
    ├── FastThreadLocal 实现
    └── jemalloc 内存分配
```

### 20.2 推荐资源

| 资源 | 类型 | 链接 |
|------|------|------|
| Netty 官方 Wiki | 文档 | https://netty.io/wiki/ |
| Netty in Action | 书籍 | Norman Maurer 著 |
| jemalloc paper | 论文 | https://jemalloc.net/ |
| Linux Epoll 源码 | 源码 | `linux/fs/eventpoll.c` |
| JCTools | 工具库 | https://github.com/JCTools/JCTools |

### 20.3 最终原则

> **Don't trust it, test it.**

Netty 的每一个优化、每一条最佳实践，都应该通过压测验证。理论上的优化方案不一定在你的场景下生效——真正的高速公路是用里程压出来的。

---

## 21. 更多真实场景代码案例

### 21.1 Netty + Spring Boot 集成

```java
@SpringBootApplication
public class NettyServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(NettyServerApplication.class, args);
    }
}

// 服务端配置
@Component
public class NettyServerRunner implements CommandLineRunner {
    @Autowired private NettyServerConfig config;
    @Autowired private List<ChannelHandler> handlers;

    @Override
    public void run(String... args) {
        EventLoopGroup boss = new NioEventLoopGroup(1);
        EventLoopGroup worker = new NioEventLoopGroup();
        
        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(boss, worker)
             .channel(NioServerSocketChannel.class)
             .childHandler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 protected void initChannel(SocketChannel ch) {
                     ChannelPipeline p = ch.pipeline();
                     handlers.forEach(p::addLast);
                 }
             });

            ChannelFuture f = b.bind(config.getPort()).sync();
            f.channel().closeFuture().addListener(future -> {
                boss.shutdownGracefully();
                worker.shutdownGracefully();
            });
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}

@Component
@ConfigurationProperties(prefix = "netty.server")
public class NettyServerConfig {
    private int port = 8080;
    private int bossThreads = 1;
    private int workerThreads = Runtime.getRuntime().availableProcessors() * 2;
    // getters/setters
}
```

```yaml
# application.yml
netty:
  server:
    port: 8888
    boss-threads: 1
    worker-threads: 8
```

### 21.2 WebSocket 完整示例

```java
// WebSocket 服务端
public class WebSocketServer {
    public static void main(String[] args) {
        EventLoopGroup boss = new NioEventLoopGroup(1);
        EventLoopGroup worker = new NioEventLoopGroup();

        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(boss, worker)
             .channel(NioServerSocketChannel.class)
             .childHandler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 protected void initChannel(SocketChannel ch) {
                     ch.pipeline()
                       .addLast(new HttpServerCodec())
                       .addLast(new HttpObjectAggregator(65536))
                       .addLast(new WebSocketServerProtocolHandler("/ws"))
                       .addLast(new WebSocketFrameHandler());
                 }
             });

            ChannelFuture f = b.bind(8080).sync();
            f.channel().closeFuture().sync();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            boss.shutdownGracefully();
            worker.shutdownGracefully();
        }
    }
}

class WebSocketFrameHandler extends SimpleChannelInboundHandler<WebSocketFrame> {
    @Override
    public void channelActive(ChannelHandlerContext ctx) {
        System.out.println("Client connected: " + ctx.channel().remoteAddress());
    }

    @Override
    protected void channelRead0(ChannelHandlerContext ctx, WebSocketFrame frame) {
        if (frame instanceof TextWebSocketFrame) {
            String msg = ((TextWebSocketFrame) frame).text();
            System.out.println("Received: " + msg);
            ctx.channel().writeAndFlush(
                new TextWebSocketFrame("Echo: " + msg));
        } else if (frame instanceof PingWebSocketFrame) {
            ctx.writeAndFlush(new PongWebSocketFrame(frame.content().retain()));
        } else if (frame instanceof CloseWebSocketFrame) {
            ctx.close();
        }
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
        cause.printStackTrace();
        ctx.close();
    }
}

// WebSocket 客户端
public class WebSocketClient {
    public static void main(String[] args) {
        EventLoopGroup group = new NioEventLoopGroup();

        try {
            Bootstrap b = new Bootstrap();
            b.group(group)
             .channel(NioSocketChannel.class)
             .handler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 protected void initChannel(SocketChannel ch) {
                     ch.pipeline()
                       .addLast(new HttpClientCodec())
                       .addLast(new HttpObjectAggregator(65536))
                       .addLast(new WebSocketClientProtocolHandler(
                           URI.create("ws://localhost:8080/ws"),
                           WebSocketClientProtocolHandler.ClientHandshakerFactory
                               .newHandshaker(
                                   URI.create("ws://localhost:8080/ws"),
                                   WebSocketVersion.V13, null, false, null, 65536)))
                       .addLast(new WebSocketClientHandler());
                 }
             });

            Channel ch = b.connect("localhost", 8080).sync().channel();
            ch.writeAndFlush(new TextWebSocketFrame("Hello WebSocket!"));
            ch.closeFuture().sync();
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            group.shutdownGracefully();
        }
    }
}

class WebSocketClientHandler extends SimpleChannelInboundHandler<Object> {
    @Override
    protected void channelRead0(ChannelHandlerContext ctx, Object msg) {
        if (msg instanceof TextWebSocketFrame) {
            System.out.println("Server: " + ((TextWebSocketFrame) msg).text());
        }
    }
}
```

### 21.3 UDP 单播/组播

```java
// UDP 单播服务器
public class UdpServer {
    public static void main(String[] args) {
        EventLoopGroup group = new NioEventLoopGroup();

        try {
            Bootstrap b = new Bootstrap();
            b.group(group)
             .channel(NioDatagramChannel.class)
             .option(ChannelOption.SO_BROADCAST, true)
             .handler(new ChannelInitializer<NioDatagramChannel>() {
                 @Override
                 protected void initChannel(NioDatagramChannel ch) {
                     ch.pipeline().addLast(new UdpServerHandler());
                 }
             });

            b.bind(8080).sync().channel().closeFuture().await();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            group.shutdownGracefully();
        }
    }
}

class UdpServerHandler extends SimpleChannelInboundHandler<DatagramPacket> {
    @Override
    protected void channelRead0(ChannelHandlerContext ctx, DatagramPacket packet) {
        String msg = packet.content().toString(StandardCharsets.UTF_8);
        System.out.println("Received from " + packet.sender() + ": " + msg);

        // 原路返回
        ByteBuf echo = Unpooled.copiedBuffer("Echo: " + msg, StandardCharsets.UTF_8);
        ctx.writeAndFlush(new DatagramPacket(echo, packet.sender()));
    }
}

// UDP 组播服务器
public class UdpMulticastServer {
    public static void main(String[] args) {
        EventLoopGroup group = new NioEventLoopGroup();

        try {
            Bootstrap b = new Bootstrap();
            b.group(group)
             .channel(NioDatagramChannel.class)
             .option(ChannelOption.IP_MULTICAST_IF, NetworkInterface.getByName("eth0"))
             .option(ChannelOption.SO_REUSEADDR, true)
             .handler(new ChannelInitializer<NioDatagramChannel>() {
                 @Override
                 protected void initChannel(NioDatagramChannel ch) {
                     ch.pipeline().addLast(new UdpMulticastHandler());
                 }
             });

            NioDatagramChannel ch = (NioDatagramChannel) b.bind(0).sync().channel();

            // 每秒发送一次组播消息
            ScheduledFuture<?> task = ch.eventLoop().scheduleAtFixedRate(() -> {
                ByteBuf buf = Unpooled.copiedBuffer(
                    "Heartbeat " + System.currentTimeMillis(), StandardCharsets.UTF_8);
                ch.writeAndFlush(new DatagramPacket(buf,
                    new InetSocketAddress("230.0.0.1", 8080)));
            }, 0, 1, TimeUnit.SECONDS);

            ch.closeFuture().sync();
            task.cancel(true);
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            group.shutdownGracefully();
        }
    }
}

// UDP 组播接收者
public class UdpMulticastSubscriber {
    public static void main(String[] args) throws Exception {
        EventLoopGroup group = new NioEventLoopGroup();

        Bootstrap b = new Bootstrap();
        b.group(group)
         .channel(NioDatagramChannel.class)
         .option(ChannelOption.SO_REUSEADDR, true)
         .handler(new SimpleChannelInboundHandler<DatagramPacket>() {
             @Override
             protected void channelRead0(ChannelHandlerContext ctx, DatagramPacket pkt) {
                 String msg = pkt.content().toString(StandardCharsets.UTF_8);
                 System.out.println("Multicast: " + msg);
             }
         });

        NioDatagramChannel ch = (NioDatagramChannel) b.bind(8080).sync().channel();
        ch.joinGroup(InetAddress.getByName("230.0.0.1"), 
            NetworkInterface.getByName("eth0")).sync();
        System.out.println("Joined multicast group 230.0.0.1");

        ch.closeFuture().sync();
    }
}
```

### 21.4 SSL/TLS 配置

```java
public class SslNettyServer {
    public static void main(String[] args) throws Exception {
        // 自签名证书（生产环境用 CA 签发）
        // keytool -genkey -alias netty -keyalg RSA -keysize 2048 \
        //   -validity 365 -keystore server.keystore \
        //   -dname "CN=localhost,OU=Dev,O=Example,C=CN"

        SelfSignedCertificate ssc = new SelfSignedCertificate();
        SslContext sslCtx = SslContextBuilder.forServer(ssc.certificate(), ssc.privateKey())
            .sslProvider(SslProvider.JDK)   // 或 SslProvider.OPENSSL（推荐生产）
            .ciphers(null, IdentityCipherSuiteFilter.INSTANCE)
            .build();

        EventLoopGroup boss = new NioEventLoopGroup(1);
        EventLoopGroup worker = new NioEventLoopGroup();

        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(boss, worker)
             .channel(NioServerSocketChannel.class)
             .childHandler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 protected void initChannel(SocketChannel ch) {
                     ch.pipeline()
                       .addLast(sslCtx.newHandler(ch.alloc()))  // SSL handler 必须第一
                       .addLast(new HttpServerCodec())
                       .addLast(new HttpObjectAggregator(65536))
                       .addLast(new SimpleChannelInboundHandler<FullHttpRequest>() {
                           @Override
                           protected void channelRead0(ChannelHandlerContext ctx,
                                                       FullHttpRequest req) {
                               FullHttpResponse resp = new DefaultFullHttpResponse(
                                   HTTP_1_1, OK,
                                   Unpooled.wrappedBuffer("HTTPS OK!".getBytes()));
                               resp.headers().set(CONTENT_TYPE, "text/plain");
                               resp.headers().set(CONTENT_LENGTH, resp.content().readableBytes());
                               ctx.writeAndFlush(resp);
                           }
                       });
                 }
             });

            ChannelFuture f = b.bind(8443).sync();
            System.out.println("HTTPS Server running on 8443");
            f.channel().closeFuture().sync();
        } finally {
            boss.shutdownGracefully();
            worker.shutdownGracefully();
        }
    }
}

// SSL 客户端
public class SslNettyClient {
    public static void main(String[] args) throws Exception {
        SslContext sslCtx = SslContextBuilder.forClient()
            .trustManager(InsecureTrustManagerFactory.INSTANCE) // 生产用 CA 证书
            .build();

        EventLoopGroup group = new NioEventLoopGroup();

        try {
            Bootstrap b = new Bootstrap();
            b.group(group)
             .channel(NioSocketChannel.class)
             .handler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 protected void initChannel(SocketChannel ch) {
                     ch.pipeline()
                       .addLast(sslCtx.newHandler(ch.alloc(), "localhost", 8443))
                       .addLast(new HttpClientCodec())
                       .addLast(new HttpObjectAggregator(65536))
                       .addLast(new SimpleChannelInboundHandler<FullHttpResponse>() {
                           @Override
                           protected void channelRead0(ChannelHandlerContext ctx,
                                                       FullHttpResponse resp) {
                               System.out.println(resp.content()
                                   .toString(StandardCharsets.UTF_8));
                           }

                           @Override
                           public void channelActive(ChannelHandlerContext ctx) {
                               FullHttpRequest req = new DefaultFullHttpRequest(
                                   HTTP_1_1, GET,
                                   Unpooled.wrappedBuffer("/".getBytes()));
                               req.headers().set(HOST, "localhost");
                               ctx.writeAndFlush(req);
                           }
                       });
                 }
             });

            b.connect("localhost", 8443).sync().channel().closeFuture().sync();
        } finally {
            group.shutdownGracefully();
        }
    }
}
```

**生产级 SSL 注意点：**
- 不要在 JDK 参数中设置 `-Djavax.net.ssl.keyStore`，不同 SSL 连接需要不同证书时无法区分
- 每个 SSL Handler 指定各自的 `SslContext`，Spring Boot 配置 `server.ssl.*` 无法用于 Netty
- 验证 `SSLSession` 的 peer principal

```java
// 获取客户端证书信息
@Override
public void channelActive(ChannelHandlerContext ctx) {
    SSLEngine engine = ctx.pipeline().get(SslHandler.class).engine();
    SSLSession session = engine.getSession();
    System.out.println("Cipher Suite: " + session.getCipherSuite());
    try {
        java.security.cert.Certificate[] certs = session.getPeerCertificates();
        System.out.println("Client Cert CN: " + 
            ((X509Certificate) certs[0]).getSubjectX500Principal());
    } catch (SSLPeerUnverifiedException e) {
        // 无客户端证书
    }
}
```

### 21.5 心跳检测与断线重连

```java
// 服务端：使用 IdleStateHandler 检测空闲
public class HeartbeatServer {
    public static void main(String[] args) {
        EventLoopGroup boss = new NioEventLoopGroup(1);
        EventLoopGroup worker = new NioEventLoopGroup();

        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(boss, worker)
             .channel(NioServerSocketChannel.class)
             .childHandler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 protected void initChannel(SocketChannel ch) {
                     ch.pipeline()
                       // 读空闲 60s, 写空闲 30s, 全部空闲 0 (disabled)
                       .addLast(new IdleStateHandler(60, 30, 0))
                       .addLast(new HeartbeatServerHandler());
                 }
             });

            b.bind(8080).sync().channel().closeFuture().sync();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            boss.shutdownGracefully();
            worker.shutdownGracefully();
        }
    }
}

class HeartbeatServerHandler extends ChannelInboundHandlerAdapter {
    @Override
    public void userEventTriggered(ChannelHandlerContext ctx, Object evt) {
        if (evt instanceof IdleStateEvent) {
            IdleStateEvent e = (IdleStateEvent) evt;
            switch (e.state()) {
                case READER_IDLE:
                    // 读超时：客户端可能挂了
                    System.out.println("Client " + ctx.channel().remoteAddress() 
                        + " read idle, closing");
                    ctx.close();
                    break;
                case WRITER_IDLE:
                    // 写超时：发送心跳 ping
                    ctx.writeAndFlush(new HeartbeatPacket(PING))
                        .addListener(future -> {
                            if (!future.isSuccess()) {
                                ctx.close();  // 发送失败，关闭
                            }
                        });
                    break;
            }
        }
    }
}

// 客户端：带重连逻辑
public class ReconnectingClient {
    private final String host;
    private final int port;
    private EventLoopGroup group;
    private Channel channel;
    private volatile boolean running = true;

    public ReconnectingClient(String host, int port) {
        this.host = host;
        this.port = port;
    }

    public void start() {
        group = new NioEventLoopGroup();
        connect();
    }

    private void connect() {
        Bootstrap b = new Bootstrap();
        b.group(group)
         .channel(NioSocketChannel.class)
         .handler(new ChannelInitializer<SocketChannel>() {
             @Override
             protected void initChannel(SocketChannel ch) {
                 ch.pipeline()
                   .addLast(new IdleStateHandler(0, 15, 0))
                   .addLast(new HeartbeatClientHandler());
             }
         });

        b.connect(host, port).addListener((ChannelFutureListener) future -> {
            if (future.isSuccess()) {
                channel = future.channel();
                channel.closeFuture().addListener(closeFuture -> {
                    if (running) {
                        reconnect();  // 连接断开后自动重连
                    }
                });
                System.out.println("Connected to " + host + ":" + port);
            } else {
                System.out.println("Failed to connect, retrying in 5s...");
                future.channel().eventLoop().schedule(this::connect, 5, TimeUnit.SECONDS);
            }
        });
    }

    private void reconnect() {
        if (!running) return;
        System.out.println("Reconnecting in 5s...");
        group.schedule(this::connect, 5, TimeUnit.SECONDS);
    }

    /**
     * 指数退避重连
     */
    public static class ExponentialBackoffReconnector {
        private static final int MAX_RETRIES = 10;
        private static final long BASE_DELAY_MS = 1000;
        private int retries = 0;

        public void reconnect(Runnable connectTask) {
            if (retries >= MAX_RETRIES) {
                System.err.println("Max retries reached, giving up");
                return;
            }
            long delay = BASE_DELAY_MS * (1L << retries);  // 1s, 2s, 4s, 8s...
            delay = Math.min(delay, 60_000);  // 上限 60s
            retries++;

            System.out.println("Reconnecting in " + delay + "ms (attempt " + retries + ")");
            new Timer().schedule(new TimerTask() {
                @Override
                public void run() {
                    connectTask.run();
                }
            }, delay);
        }

        public void reset() {
            retries = 0;
        }
    }
}

class HeartbeatClientHandler extends ChannelInboundHandlerAdapter {
    @Override
    public void userEventTriggered(ChannelHandlerContext ctx, Object evt) {
        if (evt instanceof IdleStateEvent) {
            // 15 秒没写数据了，发心跳
            ctx.writeAndFlush(new HeartbeatPacket(PONG));
        }
    }

    @Override
    public void channelInactive(ChannelHandlerContext ctx) {
        System.out.println("Connection closed");
    }
}
```

### 21.6 RPC 客户端连接池管理

```java
// 多路复用：每个 Provider 维护多个 Channel
public class RpcChannelPool {
    private final LoadBalancer loadBalancer;
    private final Map<ProviderAddress, ChannelPool> pools = new ConcurrentHashMap<>();

    public Channel acquire(ProviderAddress addr) {
        return pools.computeIfAbsent(addr, this::createPool).acquire();
    }

    private ChannelPool createPool(ProviderAddress addr) {
        return new ChannelPool(addr, 4, 16);  // 核心 4, 最大 16
    }
}

class ChannelPool {
    private final ProviderAddress addr;
    private final int minConnections;
    private final int maxConnections;
    private final AtomicInteger activeCount = new AtomicInteger(0);
    private final BlockingQueue<Channel> idle = new LinkedBlockingQueue<>();
    private final EventLoopGroup group = new NioEventLoopGroup(1);

    ChannelPool(ProviderAddress addr, int min, int max) {
        this.addr = addr;
        this.minConnections = min;
        this.maxConnections = max;
        initMinConnections();
    }

    private void initMinConnections() {
        for (int i = 0; i < minConnections; i++) {
            createChannel();
        }
    }

    private void createChannel() {
        Bootstrap b = new Bootstrap();
        b.group(group)
         .channel(NioSocketChannel.class)
         .handler(new RpcClientInitializer());

        b.connect(addr.getHost(), addr.getPort()).addListener((ChannelFutureListener) f -> {
            if (f.isSuccess()) {
                idle.offer(f.channel());
                activeCount.incrementAndGet();
            }
        });
    }

    public Channel acquire() {
        Channel ch = idle.poll();
        if (ch != null && ch.isActive()) {
            return ch;
        }

        // 池为空，创建新连接
        while (activeCount.get() < maxConnections) {
            CountDownLatch latch = new CountDownLatch(1);
            createChannel();
            // 简单等待连接建立（生产用 CompletableFuture）
        }

        try {
            return idle.poll(1, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RpcException("No available channel");
        }
    }

    public void release(Channel ch) {
        if (ch.isActive()) {
            idle.offer(ch);
        }
    }
}

// 连接池管理下的 RPC 调用
public class PooledRpcClient {
    private final RpcChannelPool pool = new RpcChannelPool();
    private final Map<Long, CompletableFuture<RpcResponse>> pending = new ConcurrentHashMap<>();
    private final AtomicLong idGen = new AtomicLong(0);

    public CompletableFuture<RpcResponse> invoke(ProviderAddress addr, RpcRequest req) {
        CompletableFuture<RpcResponse> future = new CompletableFuture<>();
        long requestId = idGen.incrementAndGet();
        req.setRequestId(requestId);
        pending.put(requestId, future);

        try {
            Channel ch = pool.acquire(addr);
            ch.writeAndFlush(req).addListener(f -> {
                if (!f.isSuccess()) {
                    pending.remove(requestId);
                    future.completeExceptionally(
                        new RpcException("Write failed", f.cause()));
                    pool.release(ch);
                }
            });
            // 响应在 handler 中完成 future 并归还连接
        } catch (Exception e) {
            pending.remove(requestId);
            future.completeExceptionally(e);
        }

        return future;
    }
}

// 动态上下线：监听注册中心服务变更
@Component
public class DynamicProviderManager {
    private final RpcChannelPool pool;
    private final Set<ProviderAddress> currentProviders = new CopyOnWriteArraySet<>();

    @EventListener
    public void onProviderChange(ProviderChangeEvent event) {
        if (event.getType() == ProviderChangeEvent.Type.ADD) {
            currentProviders.add(event.getAddress());
        } else if (event.getType() == ProviderChangeEvent.Type.REMOVE) {
            currentProviders.remove(event.getAddress());
            // 清理该 provider 的连接池
            pool.remove(event.getAddress());
        }
    }
}
```

### 21.7 流量整形（Rate Limiting）

```java
// Netty 内置的 GlobalTrafficShapingHandler
public class TrafficShapingServer {
    public static void main(String[] args) {
        EventLoopGroup boss = new NioEventLoopGroup(1);
        EventLoopGroup worker = new NioEventLoopGroup();

        // 全局限流：写入 1MB/s，读取 512KB/s
        GlobalTrafficShapingHandler trafficHandler =
            new GlobalTrafficShapingHandler(worker, 1024 * 1024, 512 * 1024);

        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(boss, worker)
             .channel(NioServerSocketChannel.class)
             .childHandler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 protected void initChannel(SocketChannel ch) {
                     ch.pipeline()
                       .addLast(trafficHandler)
                       .addLast(new EchoServerHandler());
                 }
             });

            b.bind(8080).sync().channel().closeFuture().sync();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            boss.shutdownGracefully();
            worker.shutdownGracefully();
        }
    }
}

// 自定义令牌桶限流器
public class TokenBucketLimiter extends ChannelInboundHandlerAdapter {
    private final RateLimiter rateLimiter;

    public TokenBucketLimiter(double permitsPerSecond) {
        this.rateLimiter = RateLimiter.create(permitsPerSecond);
    }

    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) {
        if (rateLimiter.tryAcquire()) {
            ctx.fireChannelRead(msg);  // 通过
        } else {
            // 拒绝或返回错误
            ctx.writeAndFlush(Unpooled.wrappedBuffer("Rate limited\n".getBytes()));
            // 注意：不调用 fireChannelRead，消息被消费
        }
    }
}

// 使用方式
ch.pipeline()
    .addLast(new TokenBucketLimiter(1000.0))  // 每秒 1000 个请求
    .addLast(new BusinessHandler());

// 基于 Channel 维度的限流
public class PerChannelLimiter extends ChannelInboundHandlerAdapter {
    private final RateLimiter perChannelLimiter;

    public PerChannelLimiter(double permitsPerSecond) {
        this.perChannelLimiter = RateLimiter.create(permitsPerSecond);
    }

    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) {
        if (!perChannelLimiter.tryAcquire()) {
            ctx.writeAndFlush("Too many requests, slow down\r\n");
            return;
        }
        ctx.fireChannelRead(msg);
    }
}
```

### 21.8 文件传输

```java
// 大文件下载：零拷贝发送
public class FileServer {
    public static void main(String[] args) {
        EventLoopGroup boss = new NioEventLoopGroup(1);
        EventLoopGroup worker = new NioEventLoopGroup();

        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(boss, worker)
             .channel(NioServerSocketChannel.class)
             .childHandler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 protected void initChannel(SocketChannel ch) {
                     ch.pipeline()
                       .addLast(new StringDecoder())
                       .addLast(new FileServerHandler());
                 }
             });

            b.bind(8080).sync().channel().closeFuture().sync();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            boss.shutdownGracefully();
            worker.shutdownGracefully();
        }
    }
}

class FileServerHandler extends SimpleChannelInboundHandler<String> {
    private static final String FILE_DIR = "/data/share";

    @Override
    protected void channelRead0(ChannelHandlerContext ctx, String fileName) {
        File file = new File(FILE_DIR, fileName);
        if (!file.exists()) {
            ctx.writeAndFlush("File not found\r\n");
            return;
        }

        // 方案一：使用 DefaultFileRegion 零拷贝
        try {
            FileRegion region = new DefaultFileRegion(
                new FileInputStream(file).getChannel(), 0, file.length());
            ctx.writeAndFlush(region).addListener((ChannelFutureListener) future -> {
                if (future.isSuccess()) {
                    ctx.writeAndFlush("\r\n");  // 传输完成标记
                }
            });
        } catch (IOException e) {
            ctx.writeAndFlush("Error reading file\r\n");
        }
    }

    // 方案二：ChunkedWriteHandler 分块传输（稳妥）
    public void sendLargeFile(ChannelHandlerContext ctx, File file) {
        ctx.writeAndFlush(new ChunkedFile(
            new RandomAccessFile(file, "r"),
            8192  // chunk size
        ));
    }
}

// 文件上传
public class FileUploadHandler extends ChannelInboundHandlerAdapter {
    private static final String UPLOAD_DIR = "/data/uploads";
    private FileOutputStream out;
    private String fileName;

    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) {
        if (msg instanceof String) {
            // 第一个消息是文件名
            fileName = (String) msg;
            try {
                out = new FileOutputStream(new File(UPLOAD_DIR, fileName));
            } catch (FileNotFoundException e) {
                ctx.close();
            }
        } else if (msg instanceof ByteBuf) {
            // 后续是文件内容
            ByteBuf buf = (ByteBuf) msg;
            try {
                buf.readBytes(out, buf.readableBytes());
            } catch (IOException e) {
                ctx.close();
            } finally {
                buf.release();
            }
        } else if (msg instanceof LastHttpContent) {
            // 传输完成
            try {
                out.close();
                ctx.writeAndFlush("Upload complete\r\n");
            } catch (IOException e) {
                ctx.writeAndFlush("Upload error\r\n");
            }
        }
    }

    @Override
    public void channelInactive(ChannelHandlerContext ctx) {
        if (out != null) {
            try { out.close(); } catch (IOException ignored) {}
        }
    }
}
```

### 21.9 优雅关闭

```java
// 生产环境必须实现优雅关闭，让进行中的请求完成
public class GracefulShutdown {
    private final EventLoopGroup boss;
    private final EventLoopGroup worker;
    private volatile boolean shuttingDown = false;

    public GracefulShutdown(EventLoopGroup boss, EventLoopGroup worker) {
        this.boss = boss;
        this.worker = worker;
    }

    public void registerShutdownHook() {
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("Shutting down gracefully...");
            shuttingDown = true;

            // 1. 停止接受新连接
            boss.shutdownGracefully(0, 5, TimeUnit.SECONDS);

            // 2. 等待处理中的请求完成（最多 30 秒）
            worker.shutdownGracefully(1, 30, TimeUnit.SECONDS);

            // 3. 等待所有 EventLoop 完全终止
            try {
                boss.terminationFuture().sync();
                worker.terminationFuture().sync();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }

            System.out.println("Shutdown complete");
        }));
    }

    /**
     * 在 Handler 中使用：判断是否正在关闭
     */
    public class GracefulHandler extends SimpleChannelInboundHandler<Object> {
        @Override
        protected void channelRead0(ChannelHandlerContext ctx, Object msg) {
            if (shuttingDown) {
                ctx.writeAndFlush("Server shutting down, try later\r\n");
                ctx.close();
                return;
            }
            ctx.fireChannelRead(msg);  // 正常处理
        }
    }
}

// 使用方式
public class ProductionServer {
    public static void main(String[] args) {
        EventLoopGroup boss = new NioEventLoopGroup(1);
        EventLoopGroup worker = new NioEventLoopGroup();

        // 注册 JVM shutdown hook
        new GracefulShutdown(boss, worker).registerShutdownHook();

        ServerBootstrap b = new ServerBootstrap();
        b.group(boss, worker)
         .channel(NioServerSocketChannel.class)
         .childHandler(...);

        try {
            b.bind(8080).sync().channel().closeFuture().sync();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}

// RPC 客户端优雅关闭：等待 pending 请求
public void shutdownRpcClient(RpcClient client) {
    // 1. 拒绝新请求
    client.setAcceptRequests(false);

    // 2. 等待 pending 请求完成（最多 10 秒）
    long deadline = System.currentTimeMillis() + 10_000;
    while (client.getPendingCount() > 0 && System.currentTimeMillis() < deadline) {
        try { Thread.sleep(100); } catch (InterruptedException e) { break; }
    }

    // 3. 超时后关闭 channel
    client.close();
}
```

### 21.10 Micrometer 指标集成

```java
// 添加 Micrometer 依赖
// <dependency>
//     <groupId>io.micrometer</groupId>
//     <artifactId>micrometer-core</artifactId>
// </dependency>

public class MetricsHandler extends ChannelDuplexHandler {
    private final Counter msgReceived;
    private final Counter msgSent;
    private final Timer processTimer;
    private final Gauge activeConnections;

    public MetricsHandler(MeterRegistry registry) {
        this.msgReceived = registry.counter("netty.messages.received");
        this.msgSent = registry.counter("netty.messages.sent");
        this.processTimer = registry.timer("netty.message.process.time");
        this.activeConnections = registry.gauge("netty.connections.active", 
            new AtomicInteger(0), AtomicInteger::get);
    }

    @Override
    public void channelActive(ChannelHandlerContext ctx) {
        activeConnections.incrementAndGet();
        ctx.fireChannelActive();
    }

    @Override
    public void channelInactive(ChannelHandlerContext ctx) {
        activeConnections.decrementAndGet();
        ctx.fireChannelInactive();
    }

    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) {
        msgReceived.increment();
        Timer.Sample sample = Timer.start();

        ctx.fireChannelRead(msg);

        // 在 write 回调中记录处理时间
        ctx.channel().writeAndFlush(msg).addListener(future -> {
            if (future.isSuccess()) {
                sample.stop(processTimer);
            }
        });
    }

    @Override
    public void write(ChannelHandlerContext ctx, Object msg, ChannelPromise promise) {
        msgSent.increment();
        ctx.write(msg, promise);
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
        registry.counter("netty.errors", 
            "type", cause.getClass().getSimpleName()).increment();
        ctx.fireExceptionCaught(cause);
    }
}

// RPC 调用耗时追踪
public class RpcMetricsInterceptor extends ChannelDuplexHandler {
    private static final Map<Long, Long> invokeTimes = new ConcurrentHashMap<>();

    @Override
    public void write(ChannelHandlerContext ctx, Object msg, ChannelPromise promise) {
        if (msg instanceof RpcRequest) {
            RpcRequest req = (RpcRequest) msg;
            invokeTimes.put(req.getRequestId(), System.nanoTime());
        }
        ctx.write(msg, promise);
    }

    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) {
        if (msg instanceof RpcResponse) {
            RpcResponse resp = (RpcResponse) msg;
            Long start = invokeTimes.remove(resp.getRequestId());
            if (start != null) {
                long elapsed = System.nanoTime() - start;
                // 上报到 Metrics 系统
                reportLatency(resp.getServiceName(), elapsed / 1_000_000);
            }
        }
        ctx.fireChannelRead(msg);
    }
}
```

### 21.11 Virtual Threads 集成（JDK 21+）

```java
// ServerBootstrap 仍然用 Netty EventLoop 处理 IO（非阻塞）
// 但业务 handler 可以用虚拟线程执行

// 配置方式 1：用 virtual thread 执行阻塞业务
public class VirtualThreadHandler extends ChannelInboundHandlerAdapter {
    private final ExecutorService virtualExecutor = 
        Executors.newVirtualThreadPerTaskExecutor();

    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) {
        virtualExecutor.submit(() -> {
            try {
                // 看似阻塞的 JDBC/HTTP 调用，实际不阻塞 OS 线程
                Object result = doBlockingBusiness(msg);
                ctx.writeAndFlush(result);
            } catch (Exception e) {
                ctx.fireExceptionCaught(e);
            }
        });
    }
}

// 配置方式 2：EventLoop 使用虚拟线程
public class VirtualThreadNettyServer {
    public static void main(String[] args) {
        // 注意：EventLoop 本身不适合用虚拟线程（非阻塞 IO 调用 epoll_wait）
        // 虚拟线程的场景在：业务逻辑中的阻塞调用

        EventLoopGroup boss = new NioEventLoopGroup(1);
        EventLoopGroup worker = new NioEventLoopGroup();

        try (ExecutorService vtExec = Executors.newVirtualThreadPerTaskExecutor()) {
            ServerBootstrap b = new ServerBootstrap();
            b.group(boss, worker)
             .channel(NioServerSocketChannel.class)
             .childHandler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 protected void initChannel(SocketChannel ch) {
                     ch.pipeline()
                       .addLast(new RpcDecoder())
                       .addLast(new RpcEncoder())
                       .addLast(new SimpleChannelInboundHandler<RpcRequest>() {
                           @Override
                           protected void channelRead0(ChannelHandlerContext ctx,
                                                       RpcRequest req) {
                               // 虚拟线程执行阻塞业务，不占用 IO 线程
                               vtExec.submit(() -> {
                                   try {
                                       // 这个 sleep 不会阻塞 OS 线程
                                       Thread.sleep(100);
                                       ctx.writeAndFlush(buildResponse(req));
                                   } catch (Exception e) {
                                       ctx.fireExceptionCaught(e);
                                   }
                               });
                           }
                       });
                 }
             });

            b.bind(8080).sync().channel().closeFuture().sync();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            boss.shutdownGracefully();
            worker.shutdownGracefully();
        }
    }
}

// 配置方式 3：ScheduledExecutorService 改用虚拟线程
ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(4,
    Thread.ofVirtual().factory());  // JDK 21+ 虚拟线程工厂
```

---

**参考来源：**
- 蚂蚁金服技术博客 · Netty 深度解析
- Netty 官方用户指南 (4.x)
- Mastering Netty (Medium, @ujjawalr)
- Netty Architecture Analysis (Medium, @umeshcapg)
- How Netty Uses epoll (Medium, @sathishkumar99ch)
- Baeldung · Introduction to Netty
- Netty 源码 (github.com/netty/netty)
- Linux Kernel Source (fs/eventpoll.c)

---

*本指南由多篇中文技术博客 + Medium 文章综合整理，结合生产实践经验编写。*
