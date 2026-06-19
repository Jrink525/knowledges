# 高并发下的 Java 池化技术：从入门到开源源码

> 来源: [Mastering Concurrency: Why Thread Pooling Is Critical for High-Performance Java Applications](https://medium.com/@idiotN/mastering-concurrency-why-thread-pooling-is-critical-for-high-performance-java-applications-e9de0e90fa96) (Medium)  
> 已增强: 循序渐进的 Step-by-Step 教程 + 开源项目源码设计剖析

---

## 🎯 第一章：池化到底解决了什么问题？

### 1.1 没有池的世界

想象一个电商系统，每秒要处理 1000 个下单请求：

```
每次下单流程：
  1. 创建线程去处理
  2. 从数据库获取连接查库存
  3. 关闭连接
  4. 调度线程跑扣库存
  5. 线程结束 → 销毁

每次 new Thread()：          ~1ms 的开销 + 1MB+ 栈内存
每次创建数据库连接：         TCP握手 + MySQL认证 ≈ 20~100ms
每次关闭数据库连接：         TCP挥手 + 连接回收
系统线程上下文切换：         CPU 花在切换上的时间 > 花在干活上的时间
```

1000 QPS × (1ms + 20ms + 10ms) = **每秒浪费 31 秒**在创建和销毁上。

### 1.2 有池的世界

```
应用启动时：
  ┌──────────────────────────────────────────┐
  │         线程池 (8 个线程)                  │
  ├──────────────────────────────────────────┤
  │         连接池 (8 个连接)                  │
  └──────────────────────────────────────────┘

请求来了 → 从线程池拿一个空闲线程 → 从连接池拿一个空闲连接
         → 干活 → 还回连接池 → 线程回池等下一个任务
```

**开箱即用，零创建开销。**

### 1.3 核心等式

```
池化的收益 = 创建代价 × 复用次数 - 池维护成本

当 复用次数 > 维护成本 / 创建代价 时，池化才值得。
```

---

## 📘 第二章：先动手做一个最简单的对象池

理解池的最快方式：从零写一个。

### Step 1 — 定义接口

```java
public interface Pool<T> {
    T borrow();              // 借出
    void release(T obj);     // 归还
    int idleCount();         // 空闲数量
    int activeCount();       // 活跃数量
}
```

### Step 2 — 实现一个固定大小的池

```java
public class SimplePool<T> implements Pool<T> {
    private final BlockingQueue<T> idle = new LinkedBlockingQueue<>();
    private final AtomicInteger activeCount = new AtomicInteger(0);
    private final int maxSize;
    private final Supplier<T> factory;

    public SimplePool(int maxSize, Supplier<T> factory) {
        this.maxSize = maxSize;
        this.factory = factory;
        // 预热：提前创建 minIdle 个对象
        for (int i = 0; i < Math.min(2, maxSize); i++) {
            idle.add(factory.get());
            activeCount.incrementAndGet();
        }
    }

    @Override
    public T borrow() {
        T obj = idle.poll();                    // 先看看有没有空闲
        if (obj != null) return obj;
        if (activeCount.get() < maxSize) {       // 没超上限？新建
            synchronized (this) {
                if (activeCount.get() < maxSize) {
                    T newObj = factory.get();
                    activeCount.incrementAndGet();
                    return newObj;
                }
            }
        }
        try {
            return idle.poll(5, TimeUnit.SECONDS); // 等别人归还
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Pool timeout");
        }
    }

    @Override
    public void release(T obj) {
        idle.offer(obj);  // 归还到空闲队列
    }
    // ...
}
```

### Step 3 — 用你的池跑一次

```java
Pool<HttpClient> pool = new SimplePool<>(8, () -> HttpClient.newHttpClient());
HttpClient client = pool.borrow();
// ... 发 HTTP 请求 ...
pool.release(client);
```

**这个简单的池已经跑了完整的 borrow → use → release 流程。**  
但它有很多问题：没有空闲淘汰、没有连接校验、没有监控…… 接下来看看开源项目怎么解决这些问题的。

---

## 🔧 第三章：线程池深度剖析

### 3.1 ThreadPoolExecutor 七参数全解

```java
new ThreadPoolExecutor(
    int corePoolSize,            // 常驻线程数（核心线程）
    int maximumPoolSize,         // 最大线程数（含临时线程）
    long keepAliveTime,          // 临时线程空闲多久后销毁
    TimeUnit unit,               // keepAliveTime 的时间单位
    BlockingQueue<Runnable> workQueue,  // 任务队列
    ThreadFactory threadFactory,        // 线程工厂（命名友好就靠它）
    RejectedExecutionHandler handler    // 队列满了 + 线程满了怎么办
);
```

**执行流程（涨跌规律）：**

```
         任务来了
             ↓
   核心线程 < corePoolSize?
    是 → 创建核心线程处理
    否 ↓
   队列 workQueue 能放进去？
    是 → 排队等
    否 ↓
   当前线程数 < maximumPoolSize?
    是 → 创建临时线程处理（紧急加班）
    否 ↓
   → 触发拒绝策略
```

这个流程容易误解的一个点：**新任务到来时，会先填满核心线程，再把任务丢队列，队列满了才开临时线程**。不是"核心满了就开临时线程"。

### 3.2 拒绝策略怎么选？

| 策略 | 行为 | 适用场景 |
|------|------|----------|
| `AbortPolicy` ★默认 | 抛 `RejectedExecutionException` | 调用方能感知失败 |
| `CallerRunsPolicy` | 让提交任务的线程自己跑 | 降级、慢速反馈 |
| `DiscardPolicy` | 静默丢弃 | 日志丢了也无所谓 |
| `DiscardOldestPolicy` | 丢弃队列里最老的任务 | 实时性要求高的场景 |

**最佳实践：** `CallerRunsPolicy` 常见——当池子满了，把压力直接反馈给调用方，让调用方慢下来，形成**自然背压**。

### 3.3 开源实现：Dubbo 的线程池怎么设计？

Dubbo 的 `EagerThreadPool` 调整了默认的"先排队再开临时线程"的策略：

```java
// Dubbo 源码：先把队列占满，迫使快速创建临时线程
public class EagerThreadPoolExecutor extends ThreadPoolExecutor {
    @Override
    public void execute(Runnable command) {
        if (command == null) throw new NullPointerException();
        if (getActiveCount() >= getPoolSize()  // 活跃数 ≥ 当前线程数
            && !this.submitQueue.offer(command)) {
            // 队列也满了 → 让父类去创建临时线程
            super.execute(command);
        } else {
            super.execute(command);
        }
    }
}
```

**设计意图：** Dubbo 是 RPC 框架，一个请求就是一次远程调用，希望请求**尽量不被排队**，而是快速开线程处理。这和它的 I/O 密集型特性匹配。

### 3.4 开源实现：Tomcat 的线程池怎么控制过载？

```java
// Tomcat 的 ThreadPoolExecutor 子类
public void execute(Runnable command, long timeout, TimeUnit unit) {
    submittedCount.incrementAndGet();
    try {
        super.execute(command); // 先尝试交给父类处理
    } catch (RejectedExecutionException rx) {
        // 拒绝后不是立刻放弃，而是阻塞等待队列有空位
        if (taskQueue.offer(command, timeout, unit)) {
            // 等待成功，任务入队
        } else {
            submittedCount.decrementAndGet();
            throw new RejectedExecutionException("...");
        }
    }
}
```

**设计意图：** Web 服务器不希望因为瞬时峰值就丢掉请求。先尝试快速处理，如果被拒绝了就**阻塞等一会儿**而不是直接丢。这种"软拒绝"在高并发下保护服务的同时尽量不丢失流量。

### 3.5 最佳实践

```java
// 推荐的生产配置
@Bean
public ThreadPoolExecutor orderExecutor() {
    int cores = Runtime.getRuntime().availableProcessors();
    return new ThreadPoolExecutor(
        cores,              // core = CPU核心数
        cores * 2,          // max = 2倍（I/O多一些）
        60, TimeUnit.SECONDS,
        new LinkedBlockingQueue<>(500),  // 有界队列，防OOM
        new ThreadFactoryBuilder()
            .setNameFormat("order-pool-%d")
            .setDaemon(true)
            .build(),
        new ThreadPoolExecutor.CallerRunsPolicy()
    );
}
```

---

## 🗄️ 第四章：连接池深度剖析

### 4.1 数据库连接池：为什么比线程池更"娇气"？

数据库连接池和线程池的区别：

| 特性 | 线程池 | 连接池 |
|------|--------|--------|
| 资源外部性 | 资源在 JVM 内 | 资源在 MySQL/Redis 服务端 |
| 连接有效性 | 始终有效 | MySQL 8h 空闲断开 |
| 资源泄露后果 | 线程无法归还 | 连接泄露 → 数据库连接耗尽 |

### 4.2 开源实现：HikariCP 的设计哲学

HikariCP（Spring Boot 默认连接池）为什么是最快的？

**核心设计一：ConcurrentBag（并发背包）**

```java
// 简化版 HikariCP ConcurrentBag
public class ConcurrentBag<T> {
    private final CopyOnWriteArrayList<T> sharedList;  // 共享列表
    private final ThreadLocal<List<T>> threadLocalList; // 线程本地缓存

    public T borrow(long timeout, TimeUnit timeUnit) {
        // 1. 先从线程本地（ThreadLocal）拿——无锁，最快
        List<T> localBag = threadLocalList.get();
        for (int i = localBag.size() - 1; i >= 0; i--) {
            T entry = localBag.remove(i);
            if (state == STATE_NOT_IN_USE) {
                return entry;
            }
        }

        // 2. 线程本地的用完了 → 从共享列表拿（有锁）
        for (T entry : sharedList) {
            if (CAS 标记为"已借出"成功) {
                return entry;
            }
        }

        // 3. 实在没有 → 阻塞等别人归还或用 handoff queue 新建
        return handoffQueue.poll(timeout, unit);
    }
}
```

**为什么快？**
- **无锁优先**：ThreadLocal 没有竞争，直接取
- **共享列表用 CopyOnWriteArrayList**：遍历远远多于修改
- **hand-off queue**：别人释放连接时，直接转给等待线程，不需要 notifyAll

**核心设计二：FastList**

HikariCP 自己写了个 ArrayList 替代 JDK 的 ArrayList——移除了边界检查、RangeCheck。

```java
public class FastList<T> {
    private T[] elementData;
    private int size;

    // JDK ArrayList.remove(element) 会从头遍历
    // HikariCP 的 remove 从 TAIL 开始遍历（刚归还的通常在末尾）
    public boolean remove(Object element) {
        for (int index = size - 1; index >= 0; index--) {
            if (elementData[index] == element) {  // 用 == 而非 equals
                int numMoved = size - index - 1;
                if (numMoved > 0) {
                    System.arraycopy(elementData, index + 1,
                                     elementData, index, numMoved);
                }
                elementData[--size] = null;
                return true;
            }
        }
        return false;
    }
}
```

**快在哪里？**
- JDK 的 ArrayList 从 index=0 遍历 → 平均 O(n/2)
- HikariCP 猜测刚归还的连接在末尾 → 平均 O(1)
- 用 `==` 不用 `equals` → 省了一次方法调用

**核心设计三：Connection 有效性检查，只发 `/* ping */`**

```java
// HikariCP 的 isConnectionAlive
try (Statement stmt = connection.createStatement()) {
    stmt.execute("/* ping */ SELECT 1");  // MySQL 看到注释直接返回
}
```

有的连接池发 `SELECT 1`，HikariCP 发 `/* ping */ SELECT 1`——注释让 MySQL 解析器跳过完整解析，更快。

### 4.3 开源实现：Druid 的监控哲学

阿里 Druid 和 HikariCP 走不同路线：**宁可慢一点，也要看得清**。

```java
// Druid 的 Filter 链
public abstract class Filter {
    // 前置钩子
    PreparedStatementProxy 
        prepareStatement(Chain chain, ConnectionProxy connection, String sql) 
            throws SQLException {
        // before 统计
        long startNano = System.nanoTime();
        try {
            return chain.prepareStatement(connection, sql);
        } finally {
            // after 统计：慢SQL日志、执行耗时、连接等待时间
            JdbcSqlStat stat = connection.getConnectionInfo().getSqlStat();
            if (stat != null) {
                stat.addExecuteTime(System.nanoTime() - startNano);
            }
        }
    }
}
```

**Druid 独有的能力：**
- 慢 SQL 自动检测 + 日志
- SQL 防火墙（防注入）
- 连接泄露检测（借出不还 → 输出堆栈）
- Web 监控页面（`/druid/index.html`）

### 4.4 开源实现：Tomcat JDBC Pool 的设计差异

Tomcat 自带了一个独立的 JDBC 连接池实现（`tomcat-jdbc`），和 HikariCP、Druid 走的是**完全不同的设计路线**。

#### 4.4.1 和 HikariCP 的根本区别

| 对比维度 | HikariCP | Tomcat JDBC Pool |
|----------|----------|------------------|
| 核心容器 | ConcurrentBag（无锁化） | `FairBlockingQueue` + synchronized |
| 队列策略 | ThreadLocal + CAS | `ReentrantLock` + `Condition`（公平锁） |
| 并发处理 | 尽量无锁 | 基于锁的同步 |
| 设计哲学 | 极致速度 | 功能丰富 + 兼容性强 |
| 内存占用 | 极致精简 | 更多特性支持 |

#### 4.4.2 FairBlockingQueue：Tomcat 的公平机制

```java
// Tomcat JDBC Pool 的 FairBlockingQueue（简化版）
public class FairBlockingQueue<T> {
    private final ReentrantLock lock = new ReentrantLock(true);  // 🔑 公平锁
    private final Condition notEmpty = lock.newCondition();
    private final AtomicInteger size = new AtomicInteger(0);
    // 内部实际使用 ConcurrentLinkedQueue
    private final Queue<T> queue = new ConcurrentLinkedQueue<>();

    public T poll(long timeout, TimeUnit unit) throws InterruptedException {
        long nanos = unit.toNanos(timeout);
        lock.lockInterruptibly();
        try {
            while (queue.isEmpty()) {
                if (nanos <= 0) return null;
                nanos = notEmpty.awaitNanos(nanos);  // 公平等待
            }
            T element = queue.poll();
            if (element != null) size.decrementAndGet();
            return element;
        } finally {
            lock.unlock();
        }
    }

    public boolean offer(T t) {
        queue.add(t);
        size.incrementAndGet();
        lock.lock();  // 通知等待线程
        try {
            notEmpty.signal();
        } finally {
            lock.unlock();
        }
        return true;
    }
}
```

**为什么 Tomcat 用公平锁？**

Tomcat 是 Web 容器，需要公平对待每个请求。如果某个请求一直在等连接而其他请求后来居上，用户体验会很差。公平锁保证了**先等待的请求先拿到连接**，避免线程饿死。

> 而 HikariCP 的观点是：公平锁的性能开销大于饿死的概率。
> — 这就是两种设计哲学的差异。

#### 4.4.3 Tomcat JDBC Pool 的独特能力

Tomcat JDBC Pool 有几个 HikariCP 没有的内置功能：

```java
// 1. 连接借出前执行 SQL 初始化
ResourcePool pool = new ResourcePool(props);
pool.setInitSQL("SET time_zone='+08:00', sql_mode=''");
// 每次新连接建立后，自动执行这段 SQL

// 2. 拦截器链
// 内置拦截器：
//   - SlowQueryReport（慢查询报告）
//   - ConnectionState（自动缓存只读/隔离级别设置，减少 SQL 发送）
//   - StatementCache（预编译语句缓存，提升热点查询性能）
//   - ResetAbandonedTimer（防止连接被误标记为泄露）
```

#### 4.4.4 连接池对比：HikariCP vs Tomcat vs Druid

```
性能排行：     HikariCP  >  Tomcat JDBC  >  Druid
功能丰富度：   Druid  >  Tomcat JDBC  >  HikariCP
运维监控：     Druid（Web 监控）> Tomcat（JMX）> HikariCP（基础 JMX）

选型建议：
  - 追求极致性能、微服务 → HikariCP（Spring Boot 默认，基本不用改）
  - 需要慢 SQL 日志、SQL 防火墙 → Druid（适合 DBA 运维）
  - 已经深度使用 Tomcat、需要拦截器 → Tomcat JDBC Pool
```

### 4.5 Tomcat 连接器（Connector）的线程池是怎么工作的

除了数据库连接池，Tomcat 自身还有一个**处理 HTTP 请求的线程池**——这才是每个 Java Web 应用背后最关键的池。

#### 4.5.1 Tomcat 请求处理生命周期

```
客户端请求
    ↓
┌─────────────────────────────────┐
│  Acceptor 线程（少量）            │
│  从 TCP 连接上接收请求 socket     │
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│  Poller 线程（少量）              │
│  检查 socket 可读/可写            │
│  注册到 EventLoop                 │
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│  Worker 线程池（默认 200）        │
│  执行业务逻辑：Servlet → Filter  │
│  → 最终执行你的 Controller        │
└─────────────────────────────────┘
```

**3 层池化：**
1. **Acceptor** — 接收连接的线程（通常 1~2 个就够了）
2. **Poller** — 事件轮询线程（NIO，少量，取决于 CPU）
3. **Worker** — 执行 Servlet 业务的线程池

#### 4.5.2 NIO vs NIO2 vs APR 三种连接器

| 连接器 | 线程模型 | Worker 池 | 适用场景 |
|--------|---------|-----------|----------|
| **BIO**（已废弃） | 1 请求 = 1 线程 | 线程池直接处理 | ❌ 不要用 |
| **NIO** (默认) | Acceptor + Poller + Worker | 最小 10，最大 200 | 通用，长连接 |
| **NIO2** | 异步 I/O (AIO) | Worker 池更灵活 | 大文件上传/下载 |
| **APR** | 原生 OS 事件驱动 | Worker 池 | 高性能 Linux |

#### 4.5.3 生产配置：Tomcat 线程池调优

```yaml
server:
  tomcat:
    threads:
      max: 200                    # Worker 最大线程数
      min-spare: 10               # 常驻最小线程数
    accept-count: 100             # 排队上限（超过 = 拒绝连接）
    max-connections: 10000        # 最大 TCP 连接数（NIO 下很大）
    connection-timeout: 5000      # 5s 连不上就关掉
```

**关键参数详解：**

| 参数 | 说人话 | 调优建议 |
|------|--------|----------|
| `max-threads` | 同时处理多少个请求 | 一般 CPU×2 ~ CPU×4，超过 200 通常说明业务慢了 |
| `accept-count` | 排队的请求上限 | 宁可拒绝也不让请求等太久（设 100~200） |
| `max-connections` | 同时保持多少 TCP 连接 | NIO 下可以设很大（10K+），实际受 fd 限制 |
| `min-spare-threads` | 多少线程常驻 | 设成预期的基线 QPS 所需线程数 |

#### 4.5.4 Tomcat 线程池和 Spring Boot 的关系

```
Tomcat Connector (Worker 线程池)
    ↓ 收到请求后，从 Worker 池拿出一个线程
    ↓ 执行 Servlet API 调用链
    ↓ 最终到达 Spring DispatcherServlet
        ↓
    Spring 自己还会用 async 线程池或 TaskExecutor
        去执行异步任务（如 @Async）
```

**关键认知：** Tomcat 的 Worker 线程池处理的是**请求 IO 线程**。如果你的业务里有异步操作（@Async、CompletableFuture），那些操作跑的是**应用线程池**而不是 Tomcat Worker 池。两个池之间要独立监控。

#### 4.5.5 实战案例：高并发下 Tomcat 调优

```yaml
# 情景：电商秒杀系统，峰值 5000 QPS
server:
  tomcat:
    threads:
      max: 200                    # 够用就行
      min-spare: 50               # 预热线程数多一些
    accept-count: 200             # 允许排队 200 个
    max-connections: 5000         # NIO 下可支撑大并发连接
    connection-timeout: 3000      # 3s 连不上就放弃
```

**监控指标：**
- `tomcat.threads.current` 是否接近 `maxThreads`？→ 线程不够了
- `tomcat.threads.active` 是否长时间占满？→ 业务逻辑太慢
- `connection-count` 是否远大于线程数？→ 正常（NIO 特性）

### 4.6 HTTP 连接池最佳实践

```java
// OkHttp 连接池配置
OkHttpClient client = new OkHttpClient.Builder()
    .connectionPool(new ConnectionPool(         // 连接池
        20,                                     // 最大空闲连接数
        5, TimeUnit.MINUTES                     // 空闲存活时间
    ))
    .connectTimeout(5, TimeUnit.SECONDS)
    .build();

// 连接复用原理
// GET /api HTTP/1.1
// Host: example.com
// Connection: keep-alive           ← 这个 header 告诉服务端别关连接
//
// 下次请求同一个 host:port → OkHttp 复用这条 TCP 连接
// 省掉了 TCP 三次握手 + TLS 握手 ≈ 50~200ms
```

---

## 📦 第五章：通用对象池深度剖析

### 5.1 Apache Commons Pool 2 架构

这是 Java 生态最通用的对象池框架，HikariCP、Jedis（Redis）、Druid 都基于它。

```
┌─────────────────────────────────────────────────┐
│  GenericObjectPool                               │
│  ├── PooledObjectFactory (用户实现)               │
│  │   ├── makeObject()     ← 创建新对象            │
│  │   ├── activateObject() ← 激活（借出前初始化）    │
│  │   └── passivateObject()← 钝化（归还后清理）      │
│  │   └── validateObject() ← 校验是否可用           │
│  ├── PooledObject (对象包装)                      │
│  │   └── 状态机：IDLE → ALLOCATED → EVICTION → ...│
│  ├── LinkedBlockingDeque (空闲对象双端队列)         │
│  └── EvictionTimer (空闲淘汰定时器)                │
└─────────────────────────────────────────────────┘
```

### 5.2 LIFO 为什么比 FIFO 好？

```java
// LIFO（后进先出）—— Commons Pool 2 默认策略
// 刚归还的对象热度和 CPU 亲和度最高
// 
// 时间轴：
// t=0: A借出, B借出
// t=1: B归还 → 空闲队列: [B]
// t=2: A归还 → 空闲队列: [A, B]
// t=3: 需要对象 → 取出A（刚归还，L1/2 cache 还在）
//
// 如果 FIFO: 取出B（最老的，cache 大概率已过期）
```

**LIFO 收益：** 对象的热度更高，cache miss 更低。

### 5.3 状态机设计

Commons Pool 2 给每个对象维护一个严谨的状态机：

```
                  ┌──────────────────┐
                  │      IDLE        │ ← 空闲状态，在池中等待
                  └──────┬───────────┘
                         │ borrowObject()
                         ↓
                  ┌──────────────────┐
                  │    ALLOCATED     │ ← 已借出，正在使用
                  └──────┬───────────┘
              ┌──────────┼────────────┐
              │          │            │
              ↓          ↓            ↓
          returnObject()  废弃       校验失败
              │          │            │
              ↓          ↓            ↓
          ┌─────────┐  ┌────────┐  ┌─────────┐
          │  IDLE   │  │EVICTION│  │ INVALID │
          └─────────┘  └────────┘  └─────────┘
```

这个状态机解决了：
- **双重借出**：同一个对象不会被两个线程同时借走
- **空闲淘汰**：Eviction 线程周期扫描 IDLE 池，超过 `minEvictableIdleTime` 的标记为 EVICTION 然后销毁
- **软引用/弱引用包装**：允许 GC 在内存紧张时回收空闲对象

### 5.4 从零实现 Redis 连接池 (Jedis 的设计)

```java
// 这里模拟 Jedis 连接池如何工作
public class JedisPool {
    private final GenericObjectPool<Jedis> internalPool;

    public JedisPool(String host, int port) {
        GenericObjectPoolConfig<Jedis> config = new GenericObjectPoolConfig<>();
        config.setMaxTotal(16);           // 最多16个连接
        config.setMaxIdle(8);             // 最多8个空闲
        config.setMinIdle(2);             // 最少保留2个空闲
        config.setTestOnBorrow(true);     // 借出前校验（发 PING）
        config.setTestOnReturn(true);     // 归还前校验

        this.internalPool = new GenericObjectPool<>(
            new JedisFactory(host, port), config);
    }

    // 借出
    public Jedis getResource() {
        // borrowObject 内部做：
        // 1. 空闲队列有？→ LIFO 取一个 → activateObject → validateObject → 返回
        // 2. 没有空闲但没超上限？→ makeObject → activate → 返回
        // 3. 超上限了？→ 阻塞等待 maxWaitMillis 毫秒
        // 4. 超时还没等到 → 抛 NoSuchElementException
        return internalPool.borrowObject();
    }

    // 归还
    public void returnResource(Jedis jedis) {
        // returnObject 内部做：
        // 1. passivateObject（清空旧数据）
        // 2. 检查空闲数是否 < maxIdle
        // 3. 是 → 放回空闲队列（LIFO）
        // 4. 否 → 销毁对象
        internalPool.returnObject(jedis);
    }
}
```

### 5.5 异常恢复：对象的健康检查

```java
// 问题：MySQL 8h 会断开空闲连接，重新借出时校验失败
// 解决：借出前 validateObject
//
// HikariCP 的实现（测试连接是否活着）：
public boolean validateObject(PoolEntry entry) {
    // 如果上次使用超过 validationTimeout → 才真的检查
    // 否则直接返回 true（节约一次网络往返）
    if (System.currentTimeMillis() - entry.lastAccess > 
            validationTimeout) {
        return pingConnection(entry.connection);
    }
    return true;
}
```

这块是刚入坑最容易踩的雷：**连接池里的连接不是永生的。**

---

## 🧠 第六章：Netty 的缓冲区池

### 6.1 问题：字节缓冲区的分配太频繁

Netty 是一个高并发网络框架，每秒可能要分配/释放几十万个 `byte[]`。

没有池化时：

```
每次收到 1KB 的数据包：
  new byte[1024]      → GC 分配
  复制数据
  处理完 byte[] 变成垃圾
  GC 回收 byte[]      → 触发 Young GC
```

频繁 GC → STW (Stop The World) → 延迟飙升。

### 6.2 Netty Recycler：对象回收器

```java
// 简化版 Netty Recycler
public class Recycler<T> {
    // 每个线程维护自己的 Stack
    private final FastThreadLocal<Stack<T>> threadLocal = 
        new FastThreadLocal<>() {
        @Override
        protected Stack<T> initialValue() {
            return new Stack<>(Recycler.this, Thread.currentThread());
        }
    };

    public T get() {
        Stack<T> stack = threadLocal.get();
        // 优先从线程本地拿（无锁！）
        T obj = stack.pop();
        if (obj != null) return obj;
        return newInstance(); // 没有了才新建
    }

    public boolean recycle(T obj, Handle<T> handle) {
        Stack<T> stack = handle.getStack();
        // 归还的线程和借出的线程是同一个？
        if (stack == threadLocal.get()) {
            stack.push(obj);     // 相同线程 → 直接放回
        } else {
            // 不同线程 → 放到 WeakOrderQueue（跨线程归还的缓冲区）
            WeakOrderQueue queue = getWeakOrderQueue(stack);
            queue.add(obj, handle);
        }
    }
}
```

**核心设计：**
- **ThreadLocal Stack**：无锁，每个线程用自己的回收站
- **WeakOrderQueue**：跨线程归还时的缓冲队列（避免锁竞争）
- 用 `WeakReference` 包装，防止 OOM（GC 可以回收回收站本身）

### 6.3 零拷贝 + 池化 = Netty 性能的核心

```java
// 从池中分配 ByteBuf
ByteBuf buf = ctx.alloc().directBuffer(1024);
// ↑ 从 Netty 的 PoolArena 中获取一段预分配的堆外内存
//    而不是 byte[] = new byte[1024]
//    → 不需要 GC 管理
//    → 零拷贝 IO（直接写入到 Socket 的 DMA 区域）

// 使用完自动归还
buf.release();
// → 回到 PoolArena 中等待下一次分配
```

这段代码就是 Netty 比直接使用 JDK NIO 快的核心原因之一。

---

## 📋 第七章：手把手实战——从需求到落地

### 场景：做一个图片上传服务的连接池配置

**需求：** 图片上传 API，用户上传→存储到 OSS（对象存储）

**分析：**
- 大量 I/O 等待（上传→写OSS）
- 数据库查询较少（主要查用户信息）
- 需要 HTTP 连接池连 OSS

### Step 1 — 配置线程池

```java
// 分析：I/O 密集（上传、OSS 写入）
// 经验公式：core = CPU * 2 或更大
@Configuration
public class ThreadPoolConfig {

    @Bean("uploadTaskExecutor")
    public ThreadPoolExecutor uploadExecutor() {
        int cores = Runtime.getRuntime().availableProcessors(); // 8核
        return new ThreadPoolExecutor(
            16,                         // corePoolSize
            32,                         // maxPoolSize（上了虚线程可更大）
            60, TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(200), // 队列上限
            new ThreadFactoryBuilder()
                .setNameFormat("upload-pool-%d")
                .build(),
            new ThreadPoolExecutor.CallerRunsPolicy()
            // ↑ 拒绝时让 tomcat 线程自己上传 → 减缓请求进入速度
        );
    }
}
```

### Step 2 — 配置数据库连接池 (HikariCP)

```yaml
# application.yml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20           # 极限连接数
      minimum-idle: 5                 # 常驻空闲连接
      idle-timeout: 300000            # 空闲超时 5min（比 MySQL wait_timeout 短！）
      max-lifetime: 600000            # 连接最长生存 10min（定期换新连接）
      connection-timeout: 5000        # 等连接超时 5s
      leak-detection-threshold: 10000 # 超过 10s 没归还 → 告警栈
      pool-name: UploadAppPool
```

### Step 3 — 配置 OSS HTTP 连接池

```java
@Configuration
public class OssClientConfig {

    @Bean
    public OkHttpClient ossHttpClient() {
        return new OkHttpClient.Builder()
            .connectionPool(new ConnectionPool(
                20,                     // 最大空闲连接
                5, TimeUnit.MINUTES     // 空闲存活
            ))
            .connectTimeout(5, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(chain -> {
                // 监控：记录每次请求耗时
                long start = System.nanoTime();
                Response resp = chain.proceed(chain.request());
                long cost = (System.nanoTime() - start) / 1_000_000;
                if (cost > 2000) {
                    log.warn("OSS slow: {}ms {}", cost, chain.request().url());
                }
                return resp;
            })
            .build();
    }
}
```

### Step 4 — 监控

```java
@Component
public class PoolMonitor {
    private final ThreadPoolExecutor uploadExecutor;
    private final HikariDataSource dataSource;

    public PoolMonitor(ThreadPoolExecutor ue, DataSource ds) {
        this.uploadExecutor = ue;
        this.dataSource = (HikariDataSource) ds;
        // 启动监控线程
        Executors.newSingleThreadScheduledExecutor()
            .scheduleAtFixedRate(this::report, 0, 30, TimeUnit.SECONDS);
    }

    public void report() {
        // 线程池指标
        log.info("""
            线程池: active={}, queued={}, completed={}, maxPool={}
            连接池: active={}, idle={}, waiting={}, total={}""",
            uploadExecutor.getActiveCount(),
            uploadExecutor.getQueue().size(),
            uploadExecutor.getCompletedTaskCount(),
            uploadExecutor.getMaximumPoolSize(),
            dataSource.getHikariPoolMXBean().getActiveConnections(),
            dataSource.getHikariPoolMXBean().getIdleConnections(),
            dataSource.getHikariPoolMXBean().getThreadsAwaitingConnection(),
            dataSource.getHikariPoolMXBean().getTotalConnections()
        );
    }
}
```

---

## ⚠️ 第八章：常见坑 + 排查工具

### 坑 1：线程池拿不到，一直卡住

```
现象：接口偶尔超时
排查：看看 queueSize 是不是满了 → activeCount = maxPoolSize
原因：远程调用慢了，线程全卡住等响应
解决：
  - 给远程调用加超时（connectionTimeout + readTimeout）
  - 监控线程池的 activeCount / completedTaskCount
```

### 坑 2：数据库连接泄露

```
现象：一天运行后，接口全部报 "无法获取连接"
排查：activeConnections = maxPoolSize，但服务没跑满
原因：代码里 borrow 了连接，异常分支没 release
解决：
  - 开启 HikariCP 的 leakDetectionThreshold
  - 规定所有 JDBC 操作都用 try-with-resources
```

### 坑 3：连接断开但池不知情

```
现象：偶发 "Connection is not available"
原因：MySQL wait_timeout=28800（8h），连接空闲超时断开
解决：
  - 连接池的 maxLifetime < MySQL wait_timeout（设 30min 就够）
  - 开启 testOnBorrow / testWhileIdle
```

### 调试与排查命令

```bash
# 查看线程池状态（堆栈）
jstack <pid>

# 查看 GC 情况
jstat -gcutil <pid> 1000

# 查看连接池 JMX 指标
jconsole <pid>
# HikariPool-1: Active / Idle / Pending / Total

# 压测
wrk -t8 -c200 -d60s http://localhost:8080/api/upload
# 监控指标同时输出
```

---

## 📚 总结：四种池的对比

| 池类型 | 共享资源 | 代表实现 | 核心挑战 |
|--------|---------|---------|---------|
| 线程池 | CPU 时间片 | ThreadPoolExecutor, Dubbo ETP | 上下文切换、拒绝策略 |
| 连接池 | 网络连接 | HikariCP, Druid, Jedis | 连接有效性、资源泄露 |
| 对象池 | 重型对象 | Commons Pool 2 | 状态管理、空闲淘汰 |
| 缓冲区池 | 内存块 | Netty PoolArena/Recycler | GC 压力、内存碎片 |

**一句话记住：**
- Thread Pool → 管线程（别 new 太多）
- Connection Pool → 管连接（别反复打开）
- Object Pool → 管重型对象（复用以省创建）
- Buffer Pool → 管内存（少 GC，零拷贝）

---

## 参考

- [Oracle ExecutorService 文档](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ExecutorService.html)
- [HikariCP GitHub](https://github.com/brettwooldridge/HikariCP) — ConcurrentBag + FastList 源码
- [Commons Pool 2](https://commons.apache.org/proper/commons-pool/) — GenericObjectPool 状态机
- [Netty Recycler 源码](https://github.com/netty/netty/blob/4.1/common/src/main/java/io/netty/util/internal/Recycler.java)
- [Dubbo EagerThreadPool 源码](https://github.com/apache/dubbo)
- [Druid GitHub](https://github.com/alibaba/druid) — SQL 防火墙 + 监控
- Medium: [Mastering Concurrency - Why Thread Pooling Is Critical](https://medium.com/@idiotN/mastering-concurrency-why-thread-pooling-is-critical-for-high-performance-java-applications-e9de0e90fa96)
