---
title: "Java并发性能调优 - 5个实战技巧及其Medium补充资料"
tags:
  - java
  - concurrency
  - performance-tuning
  - completablefuture
  - virtual-threads
  - stampedlock
  - thread-pool
date: 2026-06-05
source: "https://mp.weixin.qq.com/s/78kh2lcLxuXZmfBjNx69BQ"
---

# Java 并发性能调优：5个高级技巧 + Medium 补充

> **来源：** 微信公众号文章  
> **环境：** Java 21

---

## 一、WeChat 原文：5 个实战技巧

### 1.1 CompletableFuture 构建非阻塞流水线（Fan-out + Join）

大多数开发者只用 `supplyAsync` 就止步。高级开发会构建完整的依赖流水线：

```java
public CompletableFuture<UserDashboard> buildDashboard(long userId) {
    CompletableFuture<User> user = getUser(userId)
        .exceptionally(ex -> fallbackUser(userId));
    CompletableFuture<List<Order>> orders = getOrders(userId)
        .exceptionally(ex -> Collections.emptyList());
    CompletableFuture<List<Notification>> notifications = getNotifications(userId)
        .exceptionally(ex -> Collections.emptyList());

    return user
        .thenCombine(orders, (u, o) -> new UserContext(u, o))
        .thenCombine(notifications, (ctx, n) -> {
            ctx.setNotifications(n);
            return new UserDashboard(ctx);
        })
        .exceptionally(ex -> {
            log.error("Failed to build dashboard", ex);
            return new UserDashboard(fallbackContext(userId));
        });
}
```

**要点：**
- 全程无阻塞（避免 `get()` 阻塞调用）
- 并行分发 + 聚合模式（fan-out + join）
- 利用 ForkJoinPool 的工作窃取机制
- 通过 `exceptionally/handle` 使错误局部化且可恢复

---

### 1.2 StampedLock 替代传统锁

`ReentrantReadWriteLock` 仍有写线程饥饿和高争用问题。读多写少场景用 `StampedLock`：

```java
private final StampedLock lock = new StampedLock();
private double x, y;

public double distanceFromOrigin() {
    long stamp = lock.tryOptimisticRead();
    double currentX = x, currentY = y;
    if (!lock.validate(stamp)) {
        stamp = lock.readLock();
        try {
            currentX = x;
            currentY = y;
        } finally {
            lock.unlockRead(stamp);
        }
    }
    return Math.hypot(currentX, currentY);
}
```

**要点：**
- 乐观读模式，减少内核调用开销（上下文切换）
- 缓存友好性设计
- 初级开发者极少能判断何时应用此优化

---

### 1.3 有界队列 + CallerRunsPolicy 避免系统崩溃

**不要**这样创建线程池：
```java
ExecutorService pool = Executors.newFixedThreadPool(10);
// 问题：无界队列 → 请求无限缓冲 → JVM 崩溃
```

**应该这样：**
```java
public static ExecutorService createExecutor() {
    int corePoolSize = Runtime.getRuntime().availableProcessors() + 1;
    int maxPoolSize = corePoolSize;
    BlockingQueue<Runnable> queue = new ArrayBlockingQueue<>(500);
    RejectedExecutionHandler policy = new ThreadPoolExecutor.CallerRunsPolicy();
    return new ThreadPoolExecutor(
        corePoolSize, maxPoolSize, 0L, TimeUnit.MILLISECONDS, queue, policy);
}
```

**要点：**
- 背压机制：队列满时由调用方直接执行任务
- 防止下游服务过载
- 确保突发流量下内存不会无限增长
- 大多数"生产过载崩溃"源于缺少此技巧

---

### 1.4 ConcurrentHashMap.computeIfAbsent 的正确用法

**错误做法（双重初始化竞争）：**
```java
if (!cache.containsKey(key)) {
    cache.put(key, loadValue(key));
}
```

**正确做法：**
```java
var value = cache.computeIfAbsent(key, k -> loadValue(k));
```

**陷阱：** `computeIfAbsent` 内部持有桶级锁（bucket-level lock）。如果 `loadValue()` 是慢操作（数据库查询），会长时间持有锁，引发锁争用。

**优化：**
```java
cache.computeIfAbsent(key, k ->
    CompletableFuture.supplyAsync(() -> getFromDb(k))
);
```

将耗时操作放到异步线程执行。

---

### 1.5 虚拟线程的正确使用

**错误做法：** 在虚拟线程中卸载阻塞任务到其他线程池
```java
// ❌ 丧失虚拟线程的扩展性优势
executor.submit(() -> {
    CompletableFuture.supplyAsync(() -> getFromDb()); // 无意义
});
```

**正确做法：** 直接让虚拟线程阻塞
```java
ExecutorService vts = Executors.newVirtualThreadPerTaskExecutor();
vts.submit(() -> {
    // 虚拟线程阻塞时会释放底层平台线程
    String data = getFromDb();
    writeToDisk(data);
});
```

**原理：**
- 虚拟线程阻塞时释放平台线程，JVM 可复用
- 挂起成本接近零，可轻松支持百万级并发

---

## 二、Medium 补充资料

### 2.1 CompletableFuture 进阶：Composition（Medium @mortitech, Feb 2026）

原文：[Mastering Java CompletableFuture Part 2: Composition](https://medium.com/@mortitech/mastering-java-completablefuture-from-basics-to-production-part-2-composition-83e1a3d49c18)

**thenApply vs thenCompose 核心区别：**

| 方法 | 用途 | 类比 |
|------|------|------|
| `thenApply` | 同步变换（函数返回普通值） | `Stream.map()` |
| `thenCompose` | 异步链接（函数返回 `CompletableFuture`） | `Stream.flatMap()` |

**常见错误：嵌套 Future**
```java
// ❌ thenApply 返回 CompletableFuture → 嵌套
CompletableFuture<CompletableFuture<List<Order>>> nested =
    fetchUserAsync(userId).thenApply(user -> fetchOrdersAsync(user.getId()));
// 结果：CompletableFuture<CompletableFuture<List<Order>>> 🤮

// ✅ 用 thenCompose 自动展平
CompletableFuture<List<Order>> flat =
    fetchUserAsync(userId).thenCompose(user -> fetchOrdersAsync(user.getId()));
```

**并行模式对比（性能提升 2.5x）：**
```java
// ❌ 顺序执行：100 + 150 + 120 = 370ms
return fetchUser(userId)
    .thenCompose(user -> fetchOrders(userId)
        .thenCompose(orders -> fetchPayments(userId)
            .thenApply(payments -> new Dashboard(user, orders, payments))));

// ✅ 并行执行：max(100, 150, 120) = 150ms
CompletableFuture<User> userF = fetchUser(userId);
CompletableFuture<List<Order>> ordersF = fetchOrders(userId);
CompletableFuture<List<Payment>> paymentsF = fetchPayments(userId);
return CompletableFuture.allOf(userF, ordersF, paymentsF)
    .thenApply(v -> new Dashboard(userF.join(), ordersF.join(), paymentsF.join()));
```

**组合方法速查：**

| 方法 | 用途 |
|------|------|
| `thenCombine` | 合并两个独立的 Future |
| `allOf` | 等待三个以上 Future 全部完成 |
| `anyOf` | 多个 Future 中第一个完成即返回 |

**生产环境警告：为什么不用 ForkJoinPool.commonPool()**
- 共享于整个 JVM——一个依赖出问题就影响全局
- 池大小 = CPU 核心数 - 1，对 IO 密集型太小
- 线程名是 `ForkJoinPool.commonPool-worker-N`，调试困难

**解决方案：自定义线程池 + 有意义的线程名**
```java
ExecutorService ioExecutor = Executors.newFixedThreadPool(
    Runtime.getRuntime().availableProcessors() * 2,
    new ThreadFactory() {
        private final AtomicInteger counter = new AtomicInteger(0);
        @Override
        public Thread newThread(Runnable r) {
            Thread t = new Thread(r, "io-pool-" + counter.incrementAndGet());
            t.setDaemon(true);
            return t;
        }
    }
);
CompletableFuture.supplyAsync(() -> database.query(), ioExecutor);
```

**虚拟线程的 CompletableFuture 用法（Java 21+）：**
```java
Executor virtualExecutor = Executors.newVirtualThreadPerTaskExecutor();
CompletableFuture.supplyAsync(() -> database.query(), virtualExecutor);
// 虚拟线程阻塞 I/O 时，carrier thread 被释放
```

---

### 2.2 虚拟线程的 10 个常见错误（Medium @ntiinsd, Jun 2025）

原文：[10 Common Java Virtual Thread Mistakes You Must Avoid in 2025](https://medium.com/@ntiinsd/10-common-java-virtual-thread-mistakes-you-must-avoid-in-2025-c849b46864a8)

**关键错误 1：对 CPU 密集型任务使用虚拟线程**
- 虚拟线程的优势在 IO-bound，对 CPU-bound 无益
- 修复：CPU-intensive 用平台线程或 parallel streams

**其他核心陷阱（部分提取）：**

| 错误 | 说明 |
|------|------|
| 用于 CPU-bound | 虚拟线程不增加计算能力 |
| 使用 `synchronized` 锁 | 会导致 pinned carrier thread，丧失轻量优势 |
| 未设置 `-Djdk.tracePinnedThreads` | 应开启以检测 pinned 情况 |
| 与 ThreadLocal 滥用 | 虚拟线程数巨大时 ThreadLocal 内存膨胀 |
| 依赖池化 | 虚拟线程不用池化，每次创建新建即可 |

---

### 2.3 现代 Java 并发：虚拟线程 + 结构化并发（Medium @gopi_ck, Feb 2025）

原文：[Mastering Java Concurrency: Virtual Threads, Structured Concurrency & Best Practices](https://medium.com/javarevisited/mastering-java-concurrency-virtual-threads-structured-concurrency-best-practices-16d04d755f57)

强调 Java 并发的演进路径：
1. **传统模型**：手动管理线程、`synchronized`、`wait/notify`、`ReentrantLock`
2. **`java.util.concurrent` 时代**：线程池、`ConcurrentHashMap`、`ForkJoinPool`
3. **CompletableFuture 阶段**：异步编排，声明式组合
4. **虚拟线程 + 结构化并发**（Project Loom）：百万级轻量线程，结构化任务范围

核心建议：
- IO-bound 任务优先虚拟线程
- CPU-bound 任务保留平台线程 + parallel streams
- 启用 `-Djdk.tracePinnedThreads` 发现虚拟线程 pinned 问题
- 结构化并发（`StructuredTaskScope`）将在未来版本中成为主流

---

### 2.4 锁深度对比：synchronized vs ReentrantLock vs StampedLock（Medium @kolheankita15, Sep 2025）

原文：[Deep Comparison: synchronized vs ReentrantLock vs StampedLock in Java](https://medium.com/mastering-java-core-concepts-and-advanced/deep-comparison-synchronized-vs-reentrantlock-vs-stampedlock-in-java-7564a6eefe91)

| 锁类型 | 适用场景 | 性能 | 特点 |
|--------|---------|------|------|
| `synchronized` | 简单互斥 | 基础 | 最简洁，死锁风险低 |
| `ReentrantLock` | 需要超时/中断/公平性 | 中等 | 灵活但不防死锁 |
| `ReentrantReadWriteLock` | 读多写少 | 较高 | 写线程可能饥饿 |
| `StampedLock` | 极高读比例 | **最高** | 乐观读，不可重入 |

选择框架：问三个问题
1. 是读多写少？→ 考虑 StampedLock
2. 需要超时或可中断？→ ReentrantLock
3. 只是简单互斥？→ synchronized 就够

---

## 三、交叉对比与总结

### 三个主题与 WeChat 文章的比较

| WeChat 技巧 | Medium 补充内容 | 是否覆盖 |
|-------------|----------------|---------|
| CompletableFuture 流水线 | thenApply vs thenCompose, allOf/anyOf, 自定义线程池, 虚拟线程集成 | ✅ 大幅度增强 |
| StampedLock | synchronized/ReentrantLock/StampedLock 深度对比 + 选择框架 | ✅ 增强 |
| CallerRunsPolicy 背压 | 文中部分提到（虚拟线程替换线程池场景） | 🔶 需自行结合 |
| computeIfAbsent 陷阱 | 未直接覆盖 | ❌ 可自行搜索 'ConcurrentHashMap computeIfAbsent deadlock' |
| 虚拟线程 | 10 大错误 + 结构化并发 + CompletableFuture 集成 | ✅ 大幅度增强 |

### 关键工程决策速查

**错误处理策略：**
- CompletableFuture: `exceptionally` / `handle` / `whenComplete`
- 含重试设计
- 对 parallel 操作中的部分失败处理

---

## 四、相关知识库链接

- [Java 并发基础知识](/database/java-concurrency-fundamentals.md)
- [Java 并发完整导图](/database/java-concurrency-complete-graph.md)
- [JDK21 虚拟线程详解](/knowledges/ai-tools/)（需自行搜索更新）

---

*整理于 2026-06-05，来自 WeChat 文章 + Medium 文章增强*
