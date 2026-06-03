---
title: Java JVM Memory Model and Garbage Collection
tags: [java, jvm, interview, 面试, performance]
---

# Java JVM Memory Model and Garbage Collection

## JVM Memory Regions (JDK 8+)

```
┌─────────────────────────────────┐
│         Metaspace               │  ← Native memory (no OOM in most cases)
├─────────────────────────────────┤
│            Heap                  │
│  ┌──────────┬──────────┐       │
│  │  Young   │   Old    │       │
│  │  (Eden+  │          │       │
│  │   S0/S1) │          │       │
│  └──────────┴──────────┘       │
├─────────────────────────────────┤
│       Thread Stacks             │  ← Each thread ~1MB (default)
├─────────────────────────────────┤
│  Code Cache / Direct Buffer     │
└─────────────────────────────────┘
```

**Heap regions:**
- **Young Gen (1/3 heap by default):** Eden + two Survivor spaces (S0/S1)
- **Old Gen (2/3 heap):** Promoted long-lived objects

## Common GC Algorithms

| GC | 适用场景 | 特点 |
|---|---|---|
| **G1** (默认) | 多核大内存，低延迟 | Region-based，可预测暂停时间 |
| **ZGC** | 超大堆(几TB)，亚毫秒暂停 | 并发染色指针，读屏障 |
| **Parallel** | 高吞吐批处理 | 吞吐优先，STW 时间长 |
| **CMS** (Deprecated) | 低延迟 | 并发标记，碎片问题 |

### Key G1 Concepts

- **Region:** Heap 分成 ~2048 个 1-32MB region
- **RSet (Remembered Set):** 记录跨 region 引用，避免全堆扫描
- **SATB (Snapshot At The Beginning):** 并发标记保证正确性
- **Mixed GC:** 同时回收 young + 部分 old region

### GC 调优常用参数

```bash
-Xms4g -Xmx4g                    # 堆大小（建议设相等避免扩容）
-XX:+UseG1GC                     # 使用 G1（JDK 9+ 默认）
-XX:MaxGCPauseMillis=200         # 目标最大 GC 暂停
-XX:ParallelGCThreads=4          # 并行线程数
-XX:ConcGCThreads=2              # 并发线程数
-Xlog:gc*:file=gc.log:time,tags  # GC 日志
```

## 对象分配流程

```
new Obj()
  → TLAB (Thread Local Allocation Buffer)
  → 失败 → Eden
  → MinGC → 存活对象 → S0/S1
  → age++ → AgeThreshold(默认15) → Old
  → 大对象 → 直接进 Old (Humongous in G1)
```

## OOM 排查

1. **类型:** Java heap space / Metaspace / Direct buffer / Unable to create native thread
2. **工具:** `jmap -dump:live,format=b,file=heap.hprof <pid>`
3. **分析:** MAT / JProfiler / JHAT，找 dominator tree 最大对象
4. **常用手段:** 增大堆、降 QPS、查内存泄漏（ThreadLocal、ClassLoader、集合类未清除）

## 引用类型

| 类型 | GC 回收时机 | 使用场景 |
|----|-----------|--------|
| Strong | 永不 | 普通 new |
| Soft | OOM 前 | 缓存 |
| Weak | 下次 GC | WeakHashMap, ThreadLocal |
| Phantom | 回收后 | 资源释放监控 |

## 相关面试题

- JVM 堆内存分代设计为什么是新生代/老年代？
- G1 为什么能控制暂停时间？
- 什么是 SafePoint？哪些场景会进入？
- 一个对象从 new 到 GC 回收的完整过程
- 线上 CPU 100% 怎么查？
