---
title: Java Concurrency Fundamentals
tags: [java, interview, 面试, high-concurrency, 高并发, concurrency]
---

# Java Concurrency Fundamentals

## synchronized 原理

### 使用方式

| 方式 | 锁对象 |
|------|--------|
| 同步实例方法 | 当前实例 `this` |
| 同步静态方法 | `Class` 对象 |
| 同步代码块 | 指定对象 |

### Monitor 机制

每个对象关联一个 Monitor 结构：
- `_owner` — 持有锁的线程
- `_EntryList` — 等待获取锁的线程
- `_WaitSet` — 调用了 `wait()` 的线程

## JUC 核心

### ReentrantLock vs synchronized

| | synchronized | ReentrantLock |
|---|---|---|
| 锁超时 | ❌ | `tryLock(timeout, unit)` |
| 可中断 | ❌ | `lockInterruptibly()` |
| 公平性 | ❌ 非公平 | 支持公平/非公平 |
| 条件等待 | `wait/notify` | `Condition.await/signal` |

### ConcurrentHashMap (JDK 8+)

- Node 数组 + CAS + synchronized
- 链表 >8 → 红黑树
- 读操作无锁完全并发

### 线程池

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    corePoolSize, maximumPoolSize, keepAliveTime,
    TimeUnit.SECONDS, new LinkedBlockingQueue<>(queueSize),
    new ThreadPoolExecutor.AbortPolicy()
);
```

**运行流程:** 核心线程 → 工作队列 → 非核心线程 → 拒绝策略

**常见问题:** 线程池用完不调优可能导致 OOM 或死锁

## volatile 原理

- **可见性:** 每次读/写直接操作主存（Lock 前缀 + MESI 缓存一致性）
- **禁止重排:** 内存屏障（LoadLoad / StoreStore / LoadStore / StoreLoad）
- **不保证原子性:** n++ 仍需同步机制

## ThreadLocal 内存泄漏

ThreadLocalMap 的 key 是 `WeakReference<ThreadLocal>`，但 value 是强引用。线程池场景下不 `remove()` 会导致 value 永不释放。
