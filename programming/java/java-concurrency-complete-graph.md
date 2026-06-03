---
title: "Java 并发编程完全知识图谱 — 从硬件到最佳实践"
author: "Jarvis II"
date: 2026-05-17
tags:
  - java
  - concurrency
  - jmm
  - aqs
  - juc
  - multi-threading
  - interview-prep
category: "java"
description: "Java 并发编程从底层到上层的完整知识体系。覆盖 JMM、锁升级、AQS、JUC 包、线程池、并发容器、新特性（虚拟线程/结构化并发）等全部核心节点，含代码示例、面试要点和原理图解。"
---

# Java 并发编程完全知识图谱

> 从硬件到 JVM 到 JUC 到最佳实践，一张图覆盖 90%+ 并发知识点

---

## 一、硬件与内存模型基础（第 1 层）

### 1.1 CPU 缓存结构

```
CPU Core ─→ L1 (32KB 指令+数据) ─→ L2 (256KB) ─→ L3 (共享, ~MB) ─→ 主存
  线程A                                  线程B
```

**关键概念：**
- **L1/L2 每核私有**，L3 多核共享
- **缓存行（Cache Line）**：最小缓存单元，通常 64 字节
- **伪共享（False Sharing）**：两个无关变量恰好在同一缓存行，各自核独立修改却互相 invalidate → 性能暴跌
- **`@Contended` 注解**（JDK 8）：填充 padding 隔离缓存行，`-XX:-RestrictContended` 开启

```java
// 伪共享举例：两个 counter 在不同线程中被反复写，实际在同一缓存行
@Contended  // JDK 8 注解，自动填充 128 字节 padding
public class PaddedCounter {
    volatile long count1;
    // padding 自动插入
    volatile long count2;
}
```

### 1.2 缓存一致性协议（MESI）

| 状态 | 含义 |
|------|------|
| **M** (Modified) | 本核独有，已修改，内存未同步 |
| **E** (Exclusive) | 本核独有，与内存一致 |
| **S** (Shared) | 多核持有，与内存一致 |
| **I** (Invalid) | 已失效，需要重新读取 |

**关键流程：** 写一个缓存行 → 发 Invalidate 广播 → 其他核将对应缓存行标记为 I → 下次读取时从内存或他核同步。

**MESI 协议缺陷**：store buffer + invalidate queue 导致可见性问题 → JMM 用 happens-before 约束。

### 1.3 重排序

```java
// 经典例子：没有正确同步可能看到 x=0,y=0
int a = 0, b = 0;
int x = 0, y = 0;

// 线程1          // 线程2
a = 1;             b = 1;
x = b;             y = a;

// 可能的诡异结果：x=0, y=0（因为重排序）
```

**重排序来源：**

| 来源 | 说明 |
|------|------|
| 编译器重排 | 编译器优化指令顺序 |
| 处理器乱序执行 | CPU 动态调度（Tomasulo 算法） |
| 内存重排 | store buffer 导致写提交顺序与程序顺序不同 |

### 1.4 JMM — Java Memory Model（happens-before 规则）

JMM 通过 **8 条 happens-before 规则** 确保有序性和可见性：

#### 规则 1：程序次序规则（Program Order Rule）
同一线程中，写在前面的操作 happens-before 后面的操作。

#### 规则 2：监视器锁规则（Monitor Lock Rule）
解锁操作 happens-before 对同一把锁的加锁操作。

```java
synchronized (lock) {
    // 写共享变量
    shared = 42;
}
// 解锁 happens-before 另一个线程的加锁
synchronized (lock) {
    // 一定能看到 shared = 42
    System.out.println(shared);
}
```

#### 规则 3：volatile 变量规则
对 volatile 变量的写 happens-before 后续对同一变量的读。

```java
volatile boolean flag = false;
int data = 0;

// 线程 A
data = 42;         // 普通写
flag = true;       // volatile 写

// 线程 B
if (flag) {        // volatile 读
    System.out.println(data);  // 保证能看到 42
}
```

#### 规则 4：线程启动规则（Thread Start）
线程对象的 `start()` 方法 happens-before 该线程的任何操作。

```java
int x = 0;
Thread t = new Thread(() -> {
    System.out.println(x);  // 保证能看到 42
});
x = 42;     // happens-before start()
t.start();
```

#### 规则 5：线程终止规则（Thread Join）
线程中所有操作 happens-before 其他线程对该线程的 `join()` 成功返回。

#### 规则 6：线程中断规则
对线程的 `interrupt()` 调用 happens-before 被中断线程检测到中断事件。

#### 规则 7：对象终结规则
对象构造函数结束 happens-before `finalize()` 方法。

#### 规则 8：传递性
如果 A happens-before B，B happens-before C，则 A happens-before C。

### 1.5 内存屏障（Memory Barrier）

| 屏障类型 | 作用 |
|---------|------|
| **LoadLoad** | Load1 → Load2：禁止 Load1 后的读操作重排到 Load1 前 |
| **StoreStore** | Store1 → Store2：禁止 Store1 后的写操作重排到 Store1 前（保证写提交顺序） |
| **LoadStore** | Load1 → Store2：禁止 Load1 后的写操作重排到 Load1 前 |
| **StoreLoad** | Store1 → Load2：禁止 Store1 后的读操作重排到 Store1 前（**最重**，x86 只有这个需要显式，其他通过 CPU 保证） |

```java
// volatile 写 → 插入 StoreStore + StoreLoad 屏障
// volatile 读 → 插入 LoadLoad + LoadStore 屏障
```

---

## 二、JVM 基础设施（第 2 层）

### 2.1 CAS（Compare And Swap）

```java
// Unsafe 层面的 CAS
public final native boolean compareAndSwapInt(
    Object o, long offset, int expected, int x
);

// 使用示例
AtomicInteger ai = new AtomicInteger(0);
ai.compareAndSet(0, 1);  // 期望=0, 更新=1 → true
```

**CAS 三大问题：**

| 问题 | 说明 | 解法 |
|------|------|------|
| **ABA** | A→B→A 回环，检测不出变化 | `AtomicStampedReference`（版本号） |
| **自旋开销** | 高竞争下空转 | `LongAdder`（分段计数），自适应自旋 |
| **只能操一个变量** | CAS 只支持单个地址 | 封装成对象，`AtomicReference` |

```java
// ABA 问题演示
AtomicInteger a = new AtomicInteger(1);
// 线程1: a 1 → 2 → 1
// 线程2: CAS(1, 3) → true，但不知道中间变了

// 解法：AtomicStampedReference
AtomicStampedReference<Integer> ref = new AtomicStampedReference<>(1, 0);
int[] stamp = new int[1];
ref.compareAndSet(ref.get(stamp), 3, stamp[0], stamp[0] + 1);
```

### 2.2 对象头与锁升级

**Java 对象内存布局（64 位 JVM）：**

```
|------ mark word (8 bytes) ------|------ klass pointer (4/8 bytes) ------|-- 实例数据 --|-- padding --|
```

**mark word 结构（非 GC 状态）：**

```
无锁态：    | unused:25 | identity_hashcode:31 | unused:1 | age:4 | biased_lock:1 | lock:01 |
偏向锁：    | thread:54 | epoch:2 | unused:1 | age:4 | biased_lock:1 | lock:01 |
轻量级锁：  | ptr_to_lock_record:62 | lock:00 |
重量级锁：  | ptr_to_heavyweight_monitor:62 | lock:10 |
GC 标记：   | (空) | lock:11 |
```

**锁升级过程（不可逆）：**

```
无锁 → 偏向锁（同一个线程反复获取）
  → 轻量级锁（有竞争时，CAS 自旋）
    → 重量级锁（自旋超过阈值，进入内核互斥）
```

```java
// JVM 参数控制
-XX:+UseBiasedLocking      // JDK 8 默认开启，JDK 15+ 默认关闭
-XX:BiasedLockingStartupDelay=0  // 立即启用偏向锁（默认 4s 延迟）
-XX:PreBlockSpin=10        // 自旋次数阈值
```

### 2.3 Java 线程模型

```java
// 平台线程（传统 1:1 映射）
Thread t = new Thread(() -> { /* ... */ });
t.start();

// 虚拟线程（JDK 21+，M:N 映射）
Thread vt = Thread.startVirtualThread(() -> { /* ... */ });
```

| 对比 | 平台线程 | 虚拟线程 |
|------|---------|---------|
| 映射 | 1:1 到 OS 内核线程 | M:N 到平台线程（载体线程） |
| 创建成本 | 高（~1MB 栈，内核调用） | 极低（~KB 级） |
| 上下文切换 | OS 调度 | JVM 内部 yield/挂起 |
| 适用场景 | CPU 密集型 | IO 密集型（大量等待） |
| JDK | 始终可用 | ≥ 21（预览在 19） |

---

## 三、并发工具框架（第 3 层 — 面试核心）

### 3.1 AQS — AbstractQueuedSynchronizer

**AQS 是 JUC 的骨架**，基于一个 volatile int state + CLH 变体队列。

```java
// AQS 核心字段
private volatile int state;  // 同步状态（0=空闲, ≥1=占用）

// 三个核心方法（子类重写）
protected boolean tryAcquire(int arg);   // 尝试获取锁
protected boolean tryRelease(int arg);   // 尝试释放锁
protected int tryAcquireShared(int arg); // 共享模式获取

// 入队/出队（AQS 实现）
private Node enq(final Node node);  // CAS 入队
private void unparkSuccessor(Node node); // 唤醒后继
```

**CLH 队列变体：**

```
                    tail
                     ↓
head → Node{prev→null, thread=null} ↔ Node{thread=线程2, waitStatus=-1} ↔ Node{thread=线程3, waitStatus=-1}
  ↑                                                                        ↑
 dummy node (已获取锁)                                              正在等待

每个 Node 被前一个节点唤醒（而非轮询前驱状态），比经典 CLH 更高效。
```

**独占模式 vs 共享模式：**

| 模式 | 方法 | 使用场景 |
|------|------|---------|
| 独占 | `acquire()` / `release()` | ReentrantLock |
| 共享 | `acquireShared()` / `releaseShared()` | Semaphore, CountDownLatch |

**Condition 实现：**

```java
// AQS 内部维护一个 Condition 队列
// await() → 释放锁 → 入 condition 等待队列 → 挂起
// signal() → 将 condition 队列头节点转移到 AQS 同步队列 → 唤醒
```

**面试常问：**
- Q：`ReentrantLock` 的非公平锁 vs 公平锁实现差异？
  - 公平：`!hasQueuedPredecessors()` — 检查队列中是否有等待者
  - 非公平：直接 `compareAndSetState(0, 1)` 插队
- Q：`ReentrantLock` 的可重入如何实现？
  - 同一线程再次 acquire：`currentThread == exclusiveOwnerThread` → state + 1

### 3.2 基于 AQS 的同步器详解

#### ReentrantLock

```java
ReentrantLock lock = new ReentrantLock();  // 默认非公平
ReentrantLock fairLock = new ReentrantLock(true);  // 公平锁

lock.lock();
try {
    // 临界区
} finally {
    lock.unlock();
}

// 可中断获取
if (lock.tryLock(1, TimeUnit.SECONDS)) {
    try { /* ... */ } finally { lock.unlock(); }
}
```

**与 synchronized 对比：**

| 特性 | synchronized | ReentrantLock |
|------|-------------|---------------|
| 实现 | JVM 级别（锁升级） | AQS（Java 代码） |
| 性能（低竞争） | 好（偏向锁） | 略高（无偏向锁开销） |
| 性能（高竞争） | 重量级锁阻塞 | 可配置 |
| 可中断 | ❌ | ✅ |
| 超时 | ❌ | ✅ |
| 公平性 | 非公平 | 可配置 |
| 条件等待 | `wait/notify`（单一） | `newCondition()`（多个） |

#### Semaphore

```java
Semaphore sem = new Semaphore(3);  // 3 个许可证

// 限流场景
for (int i = 0; i < 10; i++) {
    sem.acquire();  // 获取许可证（阻塞）
    executor.submit(() -> {
        try { /* 并发不超过3个 */ } finally { sem.release(); }
    });
}
```

#### CountDownLatch vs CyclicBarrier vs Phaser

| 特性 | CountDownLatch | CyclicBarrier | Phaser |
|------|---------------|---------------|--------|
| 重用 | ❌（一次性） | ✅（reset） | ✅（自动） |
| 等待点 | count 减到 0 | 所有线程到达 barrier | phase 推进 |
| 动态注册 | ❌ | ❌ | ✅ |
| 主线程等待 | ✅ | ❌ | ✅ |
| 超时 | ✅ | ✅ | ✅ |

```java
// CountDownLatch：主线程等待 N 个任务完成
CountDownLatch latch = new CountDownLatch(3);
// 每个任务完成后 latch.countDown();
latch.await();  // 主线程阻塞直到 3 个任务完成

// CyclicBarrier：N 个线程互相等待到齐后继续
CyclicBarrier barrier = new CyclicBarrier(3, () -> {
    System.out.println("所有人到达，继续执行");
});
// 每个线程中 barrier.await();
```

### 3.3 原子类（Atomic*）

```java
// 基础 CAS 封装
AtomicInteger count = new AtomicInteger(0);
count.incrementAndGet();   // 等价于 ++i
count.getAndIncrement();   // 等价于 i++
count.addAndGet(5);        // += 5

// 引用类型
AtomicReference<User> ref = new AtomicReference<>(user);

// 字段原子更新（反射方式，无需额外对象）
AtomicIntegerFieldUpdater<User> ageUpdater =
    AtomicIntegerFieldUpdater.newUpdater(User.class, "age");
ageUpdater.incrementAndGet(user);

// LongAdder（高竞争下优于 AtomicLong）
LongAdder adder = new LongAdder();
adder.increment();    // 分段累加
adder.sum();          // 汇总各段
```

**LongAdder 原理：**

```
                    ┌─ Cell[0] (线程 1、2 争用)
base + Cell[] ──────├─ Cell[1] (线程 3、4 争用)
                    └─ Cell[2] ...（扩容）

无竞争 → 累加 base
有竞争 → 创建 Cell 分段（以 hash 分配）
sum()  → base + 汇总所有 Cell 值
```

### 3.4 并发容器

#### ConcurrentHashMap（重中之重）

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

// JDK 7：Segment 数组（分段锁，默认 16 段）
// 每段继承 ReentrantLock，写锁段，读不加锁（volatile）

// JDK 8：bin 粒度锁（Node 数组 + CAS + synchronized）
```

**JDK 8 实现要点：**

| 操作 | 机制 |
|------|------|
| **get** | volatile 读 Node 数组，无锁 |
| **put （首次）** | CAS 初始化数组或 bin 头节点 |
| **put （冲突）** | `synchronized` 锁住 bin 头节点 |
| **扩容** | 多线程协助迁移（每个线程负责一段 bucket） |
| **树化** | bin ≥ 8 → 转红黑树（查询 O(n) → O(log n)） |
| **退化** | 树 size ≤ 6 → 转回链表 |

**面试常问：**
- Q：`size()` 方法在 JDK 8 怎么实现的？
  - 用 `sumCount()`：`baseCount` + `CounterCell[]` 各段之和（类似 LongAdder）
- Q：并发扩容时读线程怎么办？
  - `ForwardingNode`：标记已迁移，读线程看到后在新表中继续查找
- Q：`ConcurrentHashMap` 的 key/value 为什么不能为 null？
  - 避免歧义（containsKey 返回 false 时无法区分 key不存在 vs value 为 null）

#### 其他并发容器

```java
// 无锁队列
ConcurrentLinkedQueue<String> clq = new ConcurrentLinkedQueue<>();
// 基于 CAS 的 Michael-Scott 队列

// 写时复制
CopyOnWriteArrayList<String> cow = new CopyOnWriteArrayList<>();
// 写时复制整个底层数组（适合读多写极少，如配置监听器）
// 写操作 O(n)，迭代器快照（弱一致性）

// 跳表
ConcurrentSkipListMap<String, String> skipMap = new ConcurrentSkipListMap<>();
// 无锁，O(log n) 查找，按 key 有序
```

#### BlockingQueue 详解

```java
// 有界阻塞队列（数组实现）
BlockingQueue<String> queue = new ArrayBlockingQueue<>(100);

// 无界（链表实现，可设容量）
BlockingQueue<String> linkedQueue = new LinkedBlockingQueue<>();

// 延迟队列（元素需实现 Delayed）
DelayQueue<DelayedTask> delayQueue = new DelayQueue<>();

// 优先级队列
BlockingQueue<Task> pq = new PriorityBlockingQueue<>();

// 阻塞方法
queue.put("item");       // 满时阻塞
String item = queue.take();  // 空时阻塞
queue.offer("item", 1, TimeUnit.SECONDS);  // 超时返回 false
```

**线程池的核心参数：**

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    corePoolSize,        // 核心线程数（存活保障）
    maximumPoolSize,     // 最大线程数（含临时线程）
    keepAliveTime,       // 临时线程空闲超时
    TimeUnit.SECONDS,
    new LinkedBlockingQueue<>(100),  // 工作队列
    Executors.defaultThreadFactory(),
    new ThreadPoolExecutor.AbortPolicy()  // 拒绝策略
);
```

**执行流程：**

```
提交任务
  ↓
corePool 有空闲 → 分配核心线程执行
  ↓ (core 满)
入工作队列 → 队列未满 → 等待核心线程处理
  ↓ (队列满)
创建临时线程 → 不超过 maxPool → 执行任务
  ↓ (队列满 && 线程数 = maxPool)
执行拒绝策略
```

**四种拒绝策略：**

| 策略 | 行为 |
|------|------|
| `AbortPolicy` | 抛 `RejectedExecutionException`（默认） |
| `CallerRunsPolicy` | 提交者线程自己执行（背压效果） |
| `DiscardPolicy` | 静默丢弃 |
| `DiscardOldestPolicy` | 丢弃队列中最早的任务 |

**Executors 工厂陷阱：**

```java
// ❌ 危险！无界队列
ExecutorService es = Executors.newFixedThreadPool(10);
// → LinkedBlockingQueue 无容量上限，任务堆积 OOM

// ❌ 危险！最大线程无限
ExecutorService es = Executors.newCachedThreadPool();
// → SynchronousQueue + maxPool=MAX_INT，请求突增时创建大量线程 OOM

// ✅ 推荐：手动 new
new ThreadPoolExecutor(
    corePoolSize, maxPoolSize,
    60, TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(capacity),
    new ThreadPoolExecutor.CallerRunsPolicy()
);
```

#### CompletableFuture（异步编排）

```java
// 异步任务
CompletableFuture<String> future =
    CompletableFuture.supplyAsync(() -> {
        return fetchData();
    });

// 链式组合
CompletableFuture<String> result =
    CompletableFuture.supplyAsync(() -> fetchUser())
        .thenApply(user -> enrichUser(user))
        .thenCompose(enriched -> fetchOrders(enriched))
        .exceptionally(ex -> {
            log.error("Error", ex);
            return "fallback";
        });

// 多任务聚合
CompletableFuture<Integer> f1 = CompletableFuture.supplyAsync(() -> 1);
CompletableFuture<Integer> f2 = CompletableFuture.supplyAsync(() -> 2);
CompletableFuture<Void> all = CompletableFuture.allOf(f1, f2);
all.thenRun(() -> {});

// 超时控制（JDK 9+）
future.orTimeout(1, TimeUnit.SECONDS);
```

### 3.5 LockSupport

```java
// 比 wait/notify 更灵活
LockSupport.park();           // 挂起
LockSupport.unpark(thread);   // 唤醒（不需要在同步块内）

// 支持超时
LockSupport.parkNanos(1000L);

// AQS 底层依赖 LockSupport.park()/unpark()
// 与 Object.wait 的区别：
//   1. 不需要 synchronized 块
//   2. unpark 可以先于 park 调用（类似令牌机制）
//   3. 对线程精准唤醒（不需要 notifyAll 全部唤醒）
```

### 3.6 ThreadLocal

```java
ThreadLocal<String> tl = new ThreadLocal<>();
tl.set("value");    // 写入当前线程的 ThreadLocalMap
tl.get();           // 从当前线程读取
tl.remove();        // 防止内存泄漏

// InheritableThreadLocal：子线程继承父线程的 ThreadLocal 值
InheritableThreadLocal<String> itl = new InheritableThreadLocal<>();

// TransmittableThreadLocal（阿里的 TTL）：线程池场景下传递
// 解决线程池复用线程时 InheritableThreadLocal 失效的问题
```

**内存泄漏分析：**

```
Thread ──→ ThreadLocalMap
                  ├── Entry(key=WeakReference<ThreadLocal>, value="大对象")
                  │
                  key 可能被 GC（弱引用），value 永远不被清理

防止泄漏：每次用完后必须 tlr.remove()
最佳实践：try { tl.set(x); } finally { tl.remove(); }
```

---

## 四、并发编程范式与最佳实践（第 4 层）

### 4.1 安全发布对象的四种方式

```java
// 1. 静态初始化（JVM 保证 final 安全）
public static Holder holder = new Holder();

// 2. volatile
private volatile Holder holder;

// 3. AtomicReference
private AtomicReference<Holder> holder = new AtomicReference<>();

// 4. 锁保护（synchronized / ReentrantLock）
private final Lock lock = new ReentrantLock();
```

### 4.2 常见并发陷阱

```java
// 1. Check-Then-Act（竞态条件）
if (!map.containsKey(key)) {     // 检查
    map.put(key, value);         // 可能另一个线程已插入
}
// 正确：ConcurrentHashMap.computeIfAbsent()

// 2. 动态锁顺序死锁
void transfer(Account from, Account to, int amount) {
    synchronized (from) {
        synchronized (to) {      // 可能和另一个 transfer(from, to) 死锁
            from.debit(amount);
            to.credit(amount);
        }
    }
}
// 正确：System.identityHashCode 固定锁顺序

// 3. 逸出（Escape）
public class Escape {
    private int secret;
    public Escape() {
        new Thread(() -> System.out.println(secret)).start();
        // 线程可能看到 secret 未初始化（this 逸出）
        secret = 42;
    }
}
```

### 4.3 线程数估算

```java
// CPU 密集型
int threads = Runtime.getRuntime().availableProcessors();  // N + 1

// IO 密集型
// threads = N * (1 + 等待时间 / 计算时间)
// 如果 IO 等待占 90%，则 N * (1 + 9) = N * 10
```

### 4.4 JDK 21+ 新特性

```java
// ===== 虚拟线程 =====
// 创建方式
Thread vt = Thread.startVirtualThread(() -> handleRequest());

// Executors API
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();

// 与传统线程对比
// 平台线程 1000 个可能 1GB 栈内存已 OOM
// 虚拟线程 100 万个都轻松

// ===== 结构化并发（JDK 21+ 预览） =====
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Future<String> user = scope.fork(() -> fetchUser());
    Future<Integer> order = scope.fork(() -> fetchOrder());
    scope.join();              // 等待所有子任务完成
    scope.throwIfFailed();     // 任一失败则抛异常
    return new Result(user.resultNow(), order.resultNow());
}

// ===== ScopedValue（替代 ThreadLocal） =====
// final static ScopedValue<String> TOKEN = ScopedValue.newInstance();
// ScopedValue.where(TOKEN, "abc-token", () -> {
//     // 这里可以读取 TOKEN，子任务也可见
//     String token = TOKEN.get();
// });
```

---

## 五、性能调优与诊断

### 调优方向

| 方向 | 方法 |
|------|------|
| 锁粒度 | 缩小锁范围，不要锁方法，锁最小代码块 |
| 锁分段 | 类似 ConcurrentHashMap，降低锁争用 |
| 无锁 | CAS 替代锁（Atomic* / LongAdder） |
| 读写分离 | CopyOnWriteArrayList / ReentrantReadWriteLock |
| 伪共享 | `@Contended` 注解或手动填充 64 字节 padding |

### 诊断工具

```bash
# 线程堆栈（死锁检测）
jstack <pid>

# 内存/GC 分析
jstat -gcutil <pid> 1000

# 火焰图（async-profiler）
profiler.sh -e cpu -d 30 -f flamegraph.html <pid>

# 并发正确性测试
# JCStress: https://github.com/openjdk/jcstress
```

### 死锁检测

```bash
jstack <pid> | grep -A 10 "deadlock"
# 输出类似：
# Found one Java-level deadlock:
# "Thread-1":
#   waiting to lock monitor 0x00007f... (object 0x...)
# "Thread-0":
#   waiting to lock monitor 0x...
```

或者在代码中使用有超时的锁：
```java
if (lock.tryLock(1, TimeUnit.SECONDS)) {
    try { /* ... */ } finally { lock.unlock(); }
} else {
    // 获取锁超时，避免死锁
}
```

---

## 六、全知识依赖图（面试复习路线）

```
┌──────────────────────────────────────────────────────┐
│                  面试高频面试题                         │
├──────────────────────────────────────────────────────┤
│ 第1题: volatile 原理 → 第2题: synchronized 原理        │
│ → 第3题: CAS + ABA → 第4题: AQS 原理                   │
│ → 第5题: ReentrantLock 源码 → 第6题: ConcurrentHashMap │
│ → 第7题: 线程池参数 + 拒绝策略 → 第8题: 死锁与避免      │
│ → 第9题: ThreadLocal + 内存泄漏 → 第10题: 虚拟线程     │
├──────────────────────────────────────────────────────┤
│                复习建议（由底到顶）                      │
├──────────────────────────────────────────────────────┤
│  第1步: 看懂 JMM + happens-before                      │
│  第2步: volatile + synchronized 原理 + 锁升级           │
│  第3步: CAS + Unsafe + Atomic* + LongAdder              │
│  第4步: AQS 骨架（CLH 队列 + state）                    │
│  第5步: ReentrantLock + Semaphore + CountDownLatch       │
│  第6步: ConcurrentHashMap（JDK 7 vs 8）                 │
│  第7步: ThreadPoolExecutor（参数 + 流程）               │
│  第8步: CompletableFuture + 虚拟线程                     │
│  第9步: ThreadLocal + 安全发布                           │
│  第10步: 实战案例 + 性能调优                             │
└──────────────────────────────────────────────────────┘
```

---

## 参考资源

- **《Java 并发编程的艺术》** — 方腾飞（最好的中文书）
- **《Java Concurrency in Practice》** — Goetz（业内圣经）
- **《深入理解 Java 虚拟机》** — 周志明（第 12 章 + 第 13 章）
- **[AQS 源码解读](https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/concurrent/locks/AbstractQueuedSynchronizer.java)**
- **[JCStress](https://github.com/openjdk/jcstress)** — 并发正确性测试框架
- **[async-profiler](https://github.com/async-profiler/async-profiler)** — Java 火焰图
