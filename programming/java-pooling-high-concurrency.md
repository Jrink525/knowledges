# 高并发下的 Java 池化技术

> 来源: [Mastering Concurrency: Why Thread Pooling Is Critical for High-Performance Java Applications](https://medium.com/@idiotN/mastering-concurrency-why-thread-pooling-is-critical-for-high-performance-java-applications-e9de0e90fa96) (Medium)  
> 收录: knowledge base `programming/`

## 🎯 核心理念：池化的本质

池化技术的核心思想只有一句话：**复用而非创建**。

在高并发场景下，对象的创建和销毁是昂贵的。线程、数据库连接、HTTP 连接——每次 new 和 close 都在消耗系统资源。池化就是提前准备好一批资源，随取随还，避免频繁的创建/销毁开销。

---

## 1. 线程池（Thread Pool）

### 为什么需要线程池

> 就像咖啡店在高峰期不应该是"来一个客人招一个咖啡师"——那样店里很快就会挤满人，谁都做不了咖啡。

Java 中每次 `new Thread()` 都会：
- 分配线程栈（默认 1MB+）
- 触发系统调用
- 线程切换时增加上下文切换成本

### Java 21 虚拟线程（Virtual Threads）

```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> {
        // 每个任务一个虚拟线程，轻量级
    });
}
```

- 适合 I/O 密集型任务
- 虚拟线程由 JVM 调度，非 OS 线程
- 代价极低，可创建百万级

### 传统固定线程池

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    4,              // corePoolSize = CPU核心数
    8,              // maxPoolSize
    60, TimeUnit.SECONDS,
    new LinkedBlockingQueue<>(1000)  // 有界队列防OOM
);
```

- **CPU 密集型** → 池大小 = CPU 核心数
- **I/O 密集型** → 池大小可更大，或直接用虚拟线程

### 关键配置陷阱

| 陷阱 | 后果 | 解决 |
|------|------|------|
| `Executors.newCachedThreadPool()` | 无限创建 → OOM | 用自定义 `ThreadPoolExecutor` |
| 无界队列 | 任务堆积 → OOM | 用 `ArrayBlockingQueue` 设定上限 |
| 不 `shutdown()` | 内存泄漏 | `finally` 块中确保关闭 |
| 任务内无异常处理 | 异常吞没 → 静默失败 | `try-catch` 包裹任务逻辑 |

---

## 2. 连接池（Connection Pool）

### 数据库连接池

高并发下最关键的池化场景：

```
每次新建连接: TCP 三次握手 + MySQL 认证 + SSL 握手 ≈ 20~100ms
连接池复用: ≈ 0.1ms
```

**主流方案：**
- **HikariCP** (Spring Boot 2.x+ 默认) — 性能最强，微秒级获取
- **Druid** (阿里) — 监控完善，慢 SQL 拦截
- **DBCP2** — 传统方案，功能完整

> 经验值：核心线程 4~8 个，最大连接 16~32（压测后微调）

### HTTP 连接池

- **Apache HttpClient** 默认内置连接池
- **OkHttp** 自带连接复用
- 连接池 + Keep-Alive 避免每次请求都建 TCP 连接

---

## 3. 通用对象池（Object Pool）

`Apache Commons Pool 2` 提供通用对象池框架：

```java
GenericObjectPool<MyExpensiveObject> pool = 
    new GenericObjectPool<>(new MyPooledObjectFactory());

// 借出
MyExpensiveObject obj = pool.borrowObject();
// 使用...
// 归还
pool.returnObject(obj);
```

适用：创建代价大、可复用的对象（如数据库连接、Socket 连接）。

---

## 4. 缓存池（Buffer Pool）

- Netty 的 `ByteBuf` 池化 —— 避免频繁分配/回收堆外内存
- String 常量池 —— JVM 内置
- Integer 缓存 —— `-128~127` 自动 cache

---

## 5. 实战建议

1. **不要万能池化** — 只有创建代价 > 复用时才用池
2. **池要有上限** — 避免无界资源耗尽
3. **监控池状态** — `activeCount`, `queueSize`, `waitingCount`
4. **优雅关闭** — `shutdown()` + `awaitTermination()`
5. **虚拟线程优先** — Java 21+ 新项目直接上虚拟线程替代线程池

---

## 参考

- [Oracle ExecutorService 文档](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ExecutorService.html)
- [HikariCP GitHub](https://github.com/brettwooldridge/HikariCP)
- [Commons Pool 2](https://commons.apache.org/proper/commons-pool/)
- Medium: [Mastering Concurrency - Why Thread Pooling Is Critical](https://medium.com/@idiotN/mastering-concurrency-why-thread-pooling-is-critical-for-high-performance-java-applications-e9de0e90fa96)
