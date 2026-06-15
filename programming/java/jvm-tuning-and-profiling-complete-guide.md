# JVM 调优与性能剖析：Java 内存管理完全指南

> 本文从理论到实战，涵盖 JDK 8 → 11 → 17 → 21 → 23 各个版本的差异与演进，
> 包含完整的调优知识体系、生产级配置模板、GC 选型决策、深入性能剖析工具链
> 以及大量实战案例和代码级优化技巧。

---

## 目录

1. [JDK 版本差异速查](#一jdk-版本差异速查)
2. [为什么需要 JVM 调优？](#二为什么需要-jvm-调优)
3. [JVM 内存区域详解](#三jvm-内存区域详解)
4. [JVM 对象模型与内存布局](#四jvm-对象模型与内存布局)
5. [垃圾回收算法与 GC 选型](#五垃圾回收算法与-gc-选型)
6. [JIT 编译原理与调优](#六jit-编译原理与调优)
7. [JVM 参数优化实战](#七jvm-参数优化实战)
8. [容器环境 JVM 调优](#八容器环境-jvm-调优)
9. [JVM 性能剖析工具链](#九jvm-性能剖析工具链)
10. [代码级性能优化与反模式](#十代码级性能优化与反模式)
11. [实战案例分析](#十一实战案例分析)
12. [JVM 调优黄金法则](#十二jvm-调优黄金法则)

---

## 一、JDK 版本差异速查

### 1.1 大版本关键变化

| 特性 | JDK 8 | JDK 11 (LTS) | JDK 17 (LTS) | JDK 21 (LTS) | JDK 23 (最新) |
|------|-------|-------------|-------------|-------------|--------------|
| **发布年份** | 2014 | 2018 | 2021 | 2023 | 2024 |
| **默认 GC** | Parallel GC | G1 GC | G1 GC | G1 GC (ZGC可选) | G1 GC (ZGC可选) |
| **可用 GC 选项** | Serial, Parallel, CMS, G1 | Serial, Parallel, G1, ZGC(E), Epsilon(E) | + Shenandoah(E→P) | + 分代ZGC, + 分代Shenandoah | + 统一日志 |
| **CMS** | ✅ 主力 | ⚠️ 已废弃 | ❌ 已移除 | ❌ | ❌ |
| **ZGC** | ❌ | ⚠️ 实验 | ✅ 正式 | ✅ 分代化 | ✅ 分代化 |
| **Shenandoah** | ❌ | ❌ (OpenJDK 12+) | ✅ 正式 | ✅ 分代化 | ✅ 分代化 |
| **Metaspace** | ✅ 替代PermGen | ✅ | ✅ | ✅ | ✅ |
| **JFR** | ❌ (商业版) | ✅ 开源免费 | ✅ | ✅ | ✅ |
| **JMC** | ❌ (商业版) | ✅ 开源免费 | ✅ | ✅ | ✅ |
| **CDS/AppCDS** | AppCDS(商业) | ✅ 开源 | ✅ 默认CDS | ✅ | ✅ |
| **容器支持** | ⚠️ 需显式 | ✅ cgroup v1 | ✅ cgroup v2 | ✅ cgroup v2 | ✅ |
| **Loom 虚拟线程** | ❌ | ❌ | ❌ | ✅ 正式 | ✅ |
| **Valhalla(值类型)** | ❌ | ❌ | ❌ | ❌ | ⚠️ 预览 |
| **GraalVM Native Image** | ❌ | ❌ | ⚠️ 实验 | ✅ 正式 | ✅ |
| **安全/加密** | TLS 1.2 | TLS 1.3 | 默认禁用RC4等 | 更强默认 | 量子安全候选 |
| **字符串去重** | ❌ | ✅ (G1) | ✅ | ✅ | ✅ |
| **紧凑字符串** | ❌ (char[] 2字节) | ✅ byte[] | ✅ | ✅ | ✅ |
| **var 类型推断** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **记录类/密封类/模式匹配** | ❌ | ❌ | ✅ 部分 | ✅ 完善 | ✅ |

### 1.2 JDK 8 → 11 迁移要点

```bash
# JDK 8 常用配置（CMS 时代）
-XX:+UseConcMarkSweepGC        # JDK 9+ 已废弃
-XX:+CMSParallelRemarkEnabled
-XX:CMSInitiatingOccupancyFraction=70
-XX:+UseCMSInitiatingOccupancyOnly

# JDK 11+ 等效 G1 配置
-XX:+UseG1GC
-XX:MaxGCPauseMillis=100
-XX:InitiatingHeapOccupancyPercent=45
# 或切换 ZGC
-XX:+UseZGC
```

**关键迁移注意事项：**
- CMS 在 JDK 9 废弃、JDK 14 移除 → 必须迁移到 G1/ZGC/Shenandoah
- PermGen 在 JDK 8 已存在但 JDK 8 兼容 → JDK 11 完全移除
- `-XX:+PrintGCDetails` 等旧 GC 日志格式在 JDK 9+ 用 `-Xlog:gc*` 替代
- 默认 Class Data Sharing (CDS) 在 JDK 12+ 已启用
- 字符串内部表示从 `char[]` (2字节) 改为 `byte[]` + 编码标记

### 1.3 JDK 11 → 17 迁移要点

```bash
# 新增的 ZGC / Shenandoah 参数
-XX:+UseZGC                     # JDK 15+ 正式
-XX:ZCollectionInterval=120     # ZGC 强制 GC 间隔
-XX:ZAllocationSpikeTolerance=2.0

-XX:+UseShenandoahGC            # JDK 15+ 正式
-XX:ShenandoahGCMode=adaptive

# 容器感知参数增强
-XX:ActiveProcessorCount=N
-XX:InitialRAMPercentage=75.0
-XX:MaxRAMPercentage=75.0
-XX:MinRAMPercentage=50.0
```

### 1.4 JDK 17 → 21 迁移要点

```bash
# JDK 21 分代式 ZGC
-XX:+UseZGC
-XX:+ZGenerational              # 启用分代 ZGC（JDK 21+）
# 分代 ZGC 相比非分代 ZGC 可降低约 25% 的 GC CPU 开销

# JDK 21 分代式 Shenandoah
-XX:+UseShenandoahGC
-XX:+ShenandoahGenerational     # 启用分代 Shenandoah

# 虚拟线程（Project Loom）
--enable-preview                # JDK 21 正式
-Djdk.traceVirtualThreadLocals=true
```

---

## 二、为什么需要 JVM 调优？

JVM 自动管理内存，这很好。但"自动"不等于"最优"。

默认情况下，JVM 做出通用决策。每个应用都有特定的需求：

- **批处理任务**：吞吐量优先，GC 暂停时间可以更长
- **Web/API 服务**：低延迟优先，GC 暂停必须控制在毫秒级
- **大内存应用**（>32GB）：需要特殊配置来处理巨型堆
- **微服务**：通常堆较小（256MB–2GB），需要快速启动和低资源占用

**JVM 调优的本质是告诉它：**

- 使用多少内存？（`-Xms`, `-Xmx`）
- 何时运行 GC？（新生代大小、晋升阈值）
- 使用哪种 GC 算法？（G1 GC / ZGC / Shenandoah / Parallel）
- 在负载下如何表现？（并发线程、GC 日志）

### 2.1 需要调优的典型信号

| 信号 | 可能原因 | 紧急程度 |
|------|---------|---------|
| 频繁 Full GC (>1次/小时) | 堆太小 / 内存泄漏 | 🔴 高 |
| GC 暂停 > 200ms | GC 选型不当 / 参数不合理 | 🟡 中 |
| CPU 持续 90%+ | 对象分配速率过高 | 🟡 中 |
| OOM 偶发 | 内存区域上限配置不当 | 🔴 高 |
| 启动慢 | 类加载 / CDS 未配置 | 🟢 低 |
| P99 延迟抖动 | GC 暂停 / JIT 编译 | 🟡 中 |

---

## 三、JVM 内存区域详解

在调优之前，先要知道我们在调什么。JVM 内存主要分为以下几大区域：

```
JVM Memory
├── Heap（堆）
│   ├── Young Generation（新生代）
│   │   ├── Eden
│   │   └── Survivor（S0 / S1）
│   └── Old Generation（老年代）
├── Metaspace（元空间）← Java 8+ 替代 PermGen
├── Code Cache（代码缓存）
├── Stack（线程栈）
└── Native Memory（直接内存 / Off-Heap）
```

### 3.1 堆内存 (Heap)

所有对象实例和数组都在这里分配。堆是 JVM 管理的最大内存区域，也是 GC 的主要战场。

**关键参数：**
- `-Xms<size>`：初始堆大小（例如 `-Xms4g`）
- `-Xmx<size>`：最大堆大小（例如 `-Xmx8g`）
- **经验法则**：`-Xms` = `-Xmx` 避免运行时动态调整
- `-XX:+AlwaysPreTouch`：启动时预分配并初始化物理内存

> **`-XX:+AlwaysPreTouch` 详解**：启动时一次性申请并 touch 所有堆内存页。
> 好处：避免运行时因缺页中断（page fault）导致的性能抖动。
> 代价：启动时间变长（堆越大越明显）。
> 推荐：生产环境的大内存应用。

### 3.2 新生代 (Young Generation)

大多数对象在新生代中"出生、死亡"（朝生夕灭）。

- **Eden**：新对象首先分配在这里
- **Survivor 区 (S0 / S1)**：经过一次 Minor GC 后存活的对象从 Eden 移至 Survivor
- 每次 Minor GC 后存活对象在 S0/S1 之间复制，年龄 +1

**关键参数：**
- `-Xmn<size>` 或 `-XX:NewSize` / `-XX:MaxNewSize`：新生代大小
- `-XX:SurvivorRatio`：Eden 与 Survivor 的比例（默认 8:1）
- `-XX:MaxTenuringThreshold`：晋升老年代的最大年龄阈值（默认 15）

**🔬 调优要点：**
```
Eden 太大致使 Young GC 间隔长但每次暂停时间长
Eden 太小导致频繁 Young GC → 晋升加速 → Old 过快填满 → Full GC
一般建议新生代占堆的 1/3 ~ 1/2
```

### 3.3 老年代 (Old Generation)

长期存活的对象最终从新生代晋升到这里。Full GC 发生时，老年代会被回收，通常比 Minor GC 慢得多。

**关键参数：**
- `-XX:PretenureSizeThreshold`：超过此大小的对象直接在老年代分配（避免在新生代频繁复制）
- `-XX:MaxTenuringThreshold`：影响晋升速度
- `-XX:TargetSurvivorRatio`：目标 Survivor 使用率（默认 50%，控制晋升触发时机）

### 3.4 元空间 (Metaspace)

Java 8 开始，**永久代 (PermGen)** 被移除，由元空间取代。最大的区别：元空间使用**本地内存（Native Memory）**，不再受 JVM 堆大小限制。

**关键参数：**
- `-XX:MetaspaceSize`：初始元空间大小（默认约 21MB）
- `-XX:MaxMetaspaceSize`：最大元空间大小（默认无限制，但**强烈建议设置上限**）
- `-XX:CompressedClassSpaceSize`：压缩类空间大小

> ⚠️ 不设 `MaxMetaspaceSize` 可能导致元空间无限制增长，最终 OOM。
> 典型场景：动态类加载（CGLIB 代理、Groovy 脚本、热部署等）极易撑爆元空间。

**JDK 8 中的 PermGen vs JDK 11+ 的 Metaspace：**

| 特性 | PermGen (JDK 7-) | Metaspace (JDK 8+) |
|------|------------------|-------------------|
| 位置 | 堆内 | 本地内存 |
| 默认大小 | 固定 64M-82M | 自动扩展 |
| 上限 | `-XX:MaxPermSize` | `-XX:MaxMetaspaceSize` |
| Full GC 影响 | 参与 Full GC | 通过 CMS/G1 处理 |
| OOM 概率 | 高（尤其动态代理） | 低（但无限增长风险） |

### 3.5 线程栈 (Stack)

每个线程拥有独立的栈，存储局部变量、方法调用帧和操作数栈。

**关键参数：**
- `-Xss<size>`：每个线程的栈大小（通常 256k–1m，过度增大会浪费内存）

**调优经验：**
- 微服务 + 高并发（上千线程）：`-Xss256k` 可以显著节省内存
- 深度递归调用：可能需要 `-Xss2m` 或更大
- 虚拟线程（JDK 21+）：默认使用更小的栈，通常无需调整

### 3.6 直接内存 (Direct Memory / Off-Heap)

NIO 使用 `DirectByteBuffer` 直接在堆外分配内存，常用于高性能 I/O 和网络框架（Netty）。

**关键参数：**
- `-XX:MaxDirectMemorySize`：最大直接内存（默认等于 `-Xmx`）

**⚠️ 注意：**
- `DirectByteBuffer` 的回收依赖 GC 触发 `Cleaner`（Reference 机制）
- Netty 等框架提供了 `PooledByteBufAllocator` 优化直接内存分配
- 直接内存不参与 GC 统计，容易被忽略而 OOM

### 3.7 代码缓存 (Code Cache)

JIT 编译器生成的本地代码存储在此区域。

**关键参数：**
- `-XX:InitialCodeCacheSize`：初始代码缓存（默认约 160KB 起，自动增长）
- `-XX:ReservedCodeCacheSize`：最大代码缓存（JDK 8 默认 240M，JDK 11+ 默认 240M）

**典型问题：** Code Cache 满了 → JIT 编译被禁用 → 性能大幅下降
```bash
# 监控代码缓存使用率
jcmd <pid> Compiler.codecache
# 或看 GC 日志中的 "CodeCache: full"
```

---

## 四、JVM 对象模型与内存布局

### 4.1 对象头 (Object Header)

HotSpot 中一个 Java 对象在堆中的布局：

```
Object (HotSpot x64, 无压缩指针)
┌──────────────────────────────┐
│      Mark Word (8 bytes)     │ ← 锁状态/GC标记/hashCode
├──────────────────────────────┤
│  Klass Pointer (8 bytes)     │ ← 指向方法区的类元数据
├──────────────────────────────┤
│  Instance Fields (N bytes)   │ ← 实例字段
├──────────────────────────────┤
│      Padding (对齐)          │ ← 8字节对齐
└──────────────────────────────┘
```

**Mark Word 的结构（随状态变化）：**

| 状态 | 标志位 | Mark Word 内容 |
|------|--------|---------------|
| 未锁定 | 01 | identity_hashcode + 分代年龄 + 0 |
| 偏向锁 | 01 | 线程ID + 偏向纪元 + 分代年龄 + 1 |
| 轻量锁 | 00 | 指向栈中 Lock Record 的指针 |
| 重量锁 | 10 | 指向 Monitor(管程) 的指针 |
| GC 标记 | 11 | forwarding pointer |

### 4.2 压缩指针 (Compressed OOPs)

JDK 6u23+ 默认开启的优化，用 32 位引用寻址 64 位堆。

```bash
-XX:+UseCompressedOops   # 默认开启（堆 < 32GB 时）
-XX:-UseCompressedOops   # 手动关闭（不推荐）
```

**压缩指针规则：**
- 堆 < 4GB：32位指针，无缩放
- 堆 4GB–32GB：32位 << 3 = 35位地址空间（8字节对齐）
- 堆 > 32GB：64位指针，**关闭压缩**（内存自动膨胀约 10-20%）

```bash
# 所以 32GB 是 JVM 的分水岭
-Xms31g -Xmx31g   # 压缩指针开启 ✅
-Xms33g -Xmx33g   # 压缩指针关闭 ❌（内存占用增加）
# 经验：卡在 31GB 比跨过 32GB 可能更省内存
```

### 4.3 TLAB (Thread Local Allocation Buffer)

每个线程在 Eden 中拥有一块私有的分配缓冲区，避免线程间竞争。

```
TLAB 工作原理：
┌──────────────────────────────┐
│  Class A (size=64)           │ ← 线程1的TLAB
│  Class B (size=128)          │
│  ...                         │
│  TLAB Bump Pointer →         │ ← 当前分配位置
│  空闲空间                    │
└──────────────────────────────┘
```

```bash
-XX:+UseTLAB                    # 默认开启
-XX:TLABSize=2m                 # TLAB 大小
-XX:TLABRefillWasteFraction=16  # TLAB 浪费容忍度（1/16）
-XX:ResizeTLAB                  # 允许动态调整 TLAB 大小
```

**有什么用？**
- 减少锁竞争（每个线程在自己的 TLAB 中分配）
- 提升分配吞吐量（bump-the-pointer 极快）
- 过大 TLAB 浪费 Eden 空间，过小频繁填充

### 4.4 PLAB (Promotion Local Allocation Buffer)

与 TLAB 类似，PLAB 用于 GC 时在老年代中为每个 GC 线程分配晋升对象。

```bash
-XX:+UsePLAB          # 默认开启
-XX:PLABSize=1k       # PLAB 大小
-XX:ResizePLAB        # 允许动态调整
```

### 4.5 对象晋升的完整流程

```java
public class ObjectPromotion {
    // 展示对象从创建到晋升的完整路径
    
    void allocationFlow() {
        // 1. 尝试在 TLAB 中分配
        // 2. TLAB 不够 → 直接在 Eden 分配
        // 3. Eden 不够 → 触发 Young GC
        // 4. Young GC 后存活对象 → Survivor (年龄 +1)
        // 5. 年龄 > MaxTenuringThreshold → 晋升 Old
        // 6. Survivor 空间满 → 提前晋升（过早晋升）
        // 7. Old 空间满 → 触发 Full GC
    }
}
```

### 4.6 卡表 (Card Table) 与记忆集 (Remembered Set)

G1 和 CMS 需要追踪新生代→老年代的跨代引用，避免扫描整个老年代。

```
卡表 Card Table (字节数组)：
┌──┬──┬──┬──┬──┬──┬──┬──┐
│1 │0 │0 │1 │0 │0 │1 │0 │ ...  ← 512字节一张卡片
└──┴──┴──┴──┴──┴──┴──┴──┘
  每个 bit/byte 表示对应 512B 堆空间是否包含指向新生代的引用
```

**写屏障 (Write Barrier)**：每次对象引用赋值时，JVM 插入一小段代码更新卡表。

```java
// 伪代码：JVM 自动为引用赋值插入的写屏障
void writeBarrier(Object ref, Object target) {
    ref.field = target;  // 原始赋值
    if (target is in Young Gen && ref is in Old Gen) {
        dirty_card_table(ref);  // 标记脏卡片
    }
}
```

---

## 五、垃圾回收算法与 GC 选型

### 5.1 GC 核心评判指标

| 指标 | 含义 | 关键指标 |
|------|------|----------|
| **吞吐量** | 应用运行时间 / (应用运行时间 + GC 时间) | 通常希望 >99% |
| **暂停时间** | 每次 GC 时应用暂停的时长 | 通常希望 <10ms |
| **内存占用** | GC 运行的额外内存开销（如记忆集） | 通常希望 <20% |
| **响应速度** | GC 对请求延迟的影响 | 尾延迟 (P99) |
| **分配速率** | 应用每秒分配的对象字节数 | 影响 GC 频率 |
| **对象存活率** | Young GC 后存活对象比例 | 高存活率 → G1/Shenandoah 更优 |

### 5.2 分配速率与对象存活率

这两个指标决定了你的 GC 行为，也决定了你应该选什么 GC：

```bash
# 如何测量分配速率？
jstat -gcutil <pid> 1000

# 或用 JFR
jcmd <pid> JFR.start duration=60s filename=alloc.jfr
# 在 JMC 中查看 Allocation Pressure 事件
```

```
分配速率高 + 存活率低 = 典型微服务模式（大量临时对象）
  → G1 或 Parallel GC 即可
  → 确保新生代足够大

分配速率高 + 存活率高 = 缓存/中间件/状态服务
  → ZGC 或 Shenandoah
  → 考虑 Off-Heap 缓存

分配速率低 + 存活率高 = 批处理/计算密集
  → Parallel GC 吞吐量最高
```

### 5.3 GC 根 (GC Roots) 详解

GC 从根出发，标记所有可达对象。根的类型：

```
GC Roots：
├── 线程栈上的局部变量
├── 静态字段（类变量）
├── JNI 引用（全局/局部）
├── 活跃线程
├── 同步监视器（synchronized 对象）
└── JVM 内部引用（系统类加载器、JIT 编译相关）
```

### 5.4 GC 算法基础：三种核心算法

**1️⃣ 标记-清除 (Mark-Sweep)**

```
标记阶段：从 GC Roots 遍历，标记所有存活对象
清除阶段：扫描堆，回收未被标记的对象
├── 优点：不需要额外空间
└── 缺点：产生内存碎片
```

**2️⃣ 标记-复制 (Mark-Copy)**

```
将可用内存分为两块 From 和 To
只在 From 上分配，GC 时将存活对象复制到 To
切换 From/To 角色
├── 优点：无碎片，分配快（bump-the-pointer）
└── 缺点：可用内存减半，存活对象多时效率低
```

**3️⃣ 标记-整理 (Mark-Compact)**

```
标记阶段：标记存活对象
整理阶段：将所有存活对象向一端移动
├── 优点：无碎片
└── 缺点：移动大对象慢，STW 时间长
```

**各 GC 使用的算法组合：**

| GC | 新生代 | 老年代 |
|----|--------|--------|
| **Serial** | 标记-复制 (STW) | 标记-整理 (STW) |
| **Parallel** | 标记-复制 (STW) | 标记-整理 (STW) |
| **CMS** | 标记-复制 (STW) | 并发标记-清除 |
| **G1** | 标记-复制 (STW) | 并发标记 + 复制 |
| **ZGC** | 并发标记 + 并发复制 | 并发标记 + 并发复制 |
| **Shenandoah** | 并发标记 + 并发整理 | 并发标记 + 并发整理 |

### 5.5 各 GC 算法对比

| GC 算法 | Java 版本 | 核心思想 | 暂停 | 吞吐量 | 适用场景 |
|---------|-----------|---------|------|--------|---------|
| **Serial GC** | JDK 1.3+ | 单线程 STW | 高 | 低 | 小型应用、单核、客户端 |
| **Parallel GC** | JDK 1.4+ (JDK 8 默认) | 多线程并行 GC | 中 | **高** | 批处理、数据仓库 |
| **CMS** | JDK 1.5+ → JDK 9 废弃 → JDK 14 移除 | 并发标记-清除 | 低 | 中 | ⛔ 已停止使用 |
| **G1 GC** | JDK 7+ (JDK 9+ 默认) | 分代区域化 | 可控 | 高 | **通用默认选型** |
| **ZGC** | JDK 11 (实验) → JDK 15 (正式) | 并发+染色指针 | **极低** (<1ms) | 高 | 大内存、超低延迟 |
| **ZGC (分代)** | JDK 21+ | 分代+并发 | 极低 | **更高** | 替代原版ZGC |
| **Shenandoah** | JDK 12 (实验) → JDK 15 (正式) | 并发整理 | 极低 | 高 | 大内存、低延迟 |
| **Shenandoah (分代)** | JDK 21+ | 分代+并发 | 极低 | **更高** | 替代原版Shenandoah |
| **Epsilon GC** | JDK 11+ | 不回收（实验） | 无 | N/A | 极短生命周期应用 |

### 5.6 G1 GC 深入解析

#### 5.6.1 核心设计：Region

G1 将堆划分为等大小的 Region（1MB–32MB），通常在 2048 个左右。

```
Heap（~8GB, 每个 Region 4MB）：
┌──┬──┬──┬──┬──┬──┬──┬──┐
│ E│ E│ S│ E│ O│ O│ H│ E│  E = Eden
├──┼──┼──┼──┼──┼──┼──┼──┤  S = Survivor
│ O│ O│ E│ E│ E│ H│ O│ O│  O = Old
├──┼──┼──┼──┼──┼──┼──┼──┤  H = Humongous (超大对象)
│ E│ S│ E│ O│ O│ O│ E│ E│
└──┴──┴──┴──┴──┴──┴──┴──┘
```

**Humerous Region**：对象超过 Region 大小一半时，直接分配到连续的 H 区。

**Region 大小计算：**
```bash
# 默认：堆大小 / 2048 ≈ Region 大小（向上取整到 1M 倍数）
-Xmx8g → Region ≈ 4MB
-Xmx16g → Region ≈ 8MB
# 手动指定：
-XX:G1HeapRegionSize=4m  # 可选 1M, 2M, 4M, 8M, 16M, 32M
```

#### 5.6.2 Remembered Set (RSet)

G1 中每个 Region 维护一个 RSet，记录从其他 Region 指向本 Region 的引用。

```
Region N (老年代) 的 RSet：
┌─────────────────────────┐
│ Region 5 (Eden) → {ref1} │
│ Region 12 (Old) → {ref2} │
│ Region 7  (Eden) → {ref3} │
└─────────────────────────┘
```

**为什么重要：** Young GC 时只需要扫描 RSet 就能知道跨代引用，不需要扫描整个老年代。

**G1 RSet 的代价：** 占用大约堆大小的 5% 左右（大堆时不可忽略）。

#### 5.6.3 SATB (Snapshot-At-The-Beginning)

G1 并发标记使用 SATB 算法确保正确性：

```
并发标记开始 → 拍照快照（逻辑上的堆快照）
并发标记期间 → 所有新分配的对象的引用都被记录（通过 SATB 队列）
并发标记结束 → 处理 SATB 队列，完成标记
```

**优点：** 并发标记期间应用可以继续运行修改引用。

#### 5.6.4 G1 的六个阶段

```
1. 年轻代 GC (Young GC)
   ├── 当 Eden 区满时触发
   ├── STW, 但只新生代 → 时间短
   └── 存活对象复制到 Survivor 或晋升 Old

2. 并发标记 (Concurrent Marking)
   ├── 当堆占用达到 IHOP 阈值触发
   ├── 与应用并发运行
   └── 标记全堆中的存活对象

3. 最终标记 (Final Marking / Remark)
   ├── STW, 短暂停
   └── 处理 SATB 队列，完成标记

4. 清理 (Cleanup)
   ├── STW, 统计存活对象
   └── 决定哪些 Region 最有回收价值

5. 混合回收 (Mixed GC)
   ├── STW, 回收多个 Region（Eden + 选中的 Old）
   ├── G1 混合标记过的老年代 Region
   └── 逐步回收，控制暂停时间

6. Full GC (退路)
   ├── 单线程 Full STW
   ├── 晋升失败 / 并发标记无法完成时触发
   └── 通常是配置问题
```

#### 5.6.5 G1 调优参数详解

```bash
# 核心参数
-XX:+UseG1GC                        # 启用 G1
-XX:MaxGCPauseMillis=100            # 目标暂停时间（默认 200ms）
                                    # 设太小 → GC 频率增高，吞吐量下降
                                    # 设太大 → 暂停时间失控

# Region 大小
-XX:G1HeapRegionSize=4m             # Region 大小，影响大对象分配

# 并发标记触发
-XX:InitiatingHeapOccupancyPercent=45  # 触发并发 GC 的阈值（默认 45%）
                                       # 设更低 → 更早开始标记（预留空间）
                                       # 设更高 → 延迟标记（可能晋升失败）

# 暂停预测
-XX:G1NewSizePercent=5              # 新生代初始占比（默认 5%）
-XX:G1MaxNewSizePercent=60          # 新生代最大占比（默认 60%）
-XX:G1HeapWastePercent=5            # 混合回收可浪费的堆百分比（默认 5%）

# 混合回收
-XX:G1MixedGCLiveThresholdPercent=85   # 混合回收阈值（默认 85%）
-XX:G1MixedGCCountTarget=8             # 混合回收分几轮进行（默认 8）
-XX:G1OldCSetRegionThresholdPercent=5  # 每轮回收 Old Region 上限（默认 5%）

# 并行与并发线程
-XX:ParallelGCThreads=4                 # STW 并行线程
-XX:ConcGCThreads=2                     # 并发线程（通常 = ParallelGCThreads / 4）

# 引用处理
-XX:+ParallelRefProcEnabled             # 并行处理软/弱/虚引用
-XX:+UseStringDeduplication             # 字符串去重（G1 专用）
```

#### 5.6.6 G1 调优策略

```bash
# 场景 1：Full GC 频繁（晋升失败）
# 诊断：GC 日志中看到 "To-space overflow" 或 "Evacuation Failure"
-XX:InitiatingHeapOccupancyPercent=35   # 提前开始并发标记
-XX:G1ReservePercent=20                 # 增加预留空间
-XX:+UnlockExperimentalVMOptions
-XX:G1MixedGCLiveThresholdPercent=60    # 降低混合回收阈值

# 场景 2：暂停时间高于目标
-XX:MaxGCPauseMillis=50                 # 降低目标暂停
-XX:ConcGCThreads=4                     # 增加并发线程
-XX:G1HeapWastePercent=10               # 增加浪费容忍度

# 场景 3：吞吐量优先（批处理）
-XX:MaxGCPauseMillis=500                # 容忍更长暂停
-XX:G1NewSizePercent=30                 # 初始新生代更大
-XX:ParallelGCThreads=8                 # 增加并行线程
```

### 5.7 ZGC 深入解析

#### 5.7.1 染色指针 (Colored Pointers)

ZGC 的核心创新：利用 64 位指针的高位（硬件未使用的 bit）存储元数据。

```
ZGC 染色指针结构 (x86-64, Linux)：
┌─────────────────────────────────────────────────────┐
│ 63  62  61  60  59-48    47-42   41-0                │
│─────────────────────────────────────────────────────│
│ M0  M1  Remapped  ?   Unused   Object Offset         │
│  │   │    │                                           │
│  └───┴────┘── 3 位元数据位                            │
└─────────────────────────────────────────────────────┘
```

- **M0 / M1**：两代标记位（支持并发标记）
- **Remapped**：重映射位（支持并发整理）
- **43-47 bits**：未使用（ZGC 利用它们做额外优化）

**优势：** 不需要 RSet、Card Table、Write Barrier 等额外结构，减少内存开销。

#### 5.7.2 负载屏障 (Load Barrier)

ZGC 使用**读屏障**而不是**写屏障**：

```java
// 应用代码
Object x = obj.field;

// JIT 编译后的实际代码（伪代码，插入 Load Barrier）
Object x = obj.field;
if (is_bad_color(x)) {        // 检查指针染色位
    x = relocate_or_remap(x); // 如果颜色不对，修复指针
}
```

**为什么是读屏障？** ZGC 在对象移动后，通过染色指针标记"已移动"，应用读取时自动修复。

#### 5.7.3 ZGC 的阶段

```
1. 并发标记 (Concurrent Mark)
   ├── 设置 M0/M1 位
   └── 遍历对象图

2. 并发处理引用 (Concurrent Reference Processing)
   └── 处理软/弱/虚引用（JDK 21+ 支持并发）

3. 并发重映射 (Concurrent Relocation)
   ├── 选择要整理的 Region（基于碎片率）
   └── 移动对象，更新 forwarding 表

4. 并发重映射修复 (Concurrent Remap)
   └── 读取时通过 Load Barrier 延迟修复指针
```

#### 5.7.4 ZGC 关键参数

```bash
# 基础启用
-XX:+UseZGC

# JDK 21+ 分代模式（强烈推荐）
-XX:+ZGenerational

# 并发线程
-XX:ConcGCThreads=N             # 默认 = CPU 核数 * 0.25，但不超过 4

# 分配尖峰容忍度
-XX:ZAllocationSpikeTolerance=2.0  # 默认 2.0，越高越提前 GC

# GC 间隔（秒）
-XX:ZCollectionInterval=120     # 强制触发 GC（默认 0 = 不强制）

# 非分代 ZGC 专属（JDK 15-20）
-XX:ZUncommitDelay=300          # 未提交内存保留时间（秒）
```

#### 5.7.5 分代 ZGC (JDK 21+)

JDK 21 引入分代 ZGC，增加新生代/老年代概念：

```
非分代 ZGC                                分代 ZGC
┌──────────────────────┐         ┌──────────────────────┐
│    整个堆同时GC      │         │  ┌─── Young ───┐     │ ← 频繁但廉价
│                      │   →    │  │  并发复制    │     │
│  每次需要全量标记    │         │  └─────────────┘     │
│                      │         │  ┌─── Old ─────┐     │ ← 较少标记
│  暂停 <1ms           │         │  │  并发标记    │     │
└──────────────────────┘         │  │  并发整理    │     │
                                 │  └─────────────┘     │
                                 └──────────────────────┘
```

**提升：** 分代 ZGC 相比非分代减少约 25% 的 GC CPU 开销，Young 代 GC 更轻量。

### 5.8 Shenandoah GC 深入解析

#### 5.8.1 核心设计：Brooks Pointer

Shenandoah 在每个对象头前插入一个额外的指针（Brooks Pointer/转发指针）：

```
Shenandoah 对象布局：
┌─────────────────────┐
│ Brooks Pointer (8B)  │ ← 指向自己或转发地址
├─────────────────────┤
│   Mark Word (8B)     │
├─────────────────────┤
│  Klass Pointer (8B)  │
├─────────────────────┤
│    Fields ...        │
└─────────────────────┘
```

**为什么不是染色指针？** Shenandoah 设计时 64 位 ARM 尚不支持染色指针，所以选择通用性更好的 Brooks Pointer。

#### 5.8.2 三个阶段的 GC

```
1. 并发标记
   └── 标记存活对象（类似 G1/ZGC）

2. 并发整理
   ├── 移动对象
   ├── 更新 Brooks Pointer 指向新地址
   └── 通过写屏障更新引用

3. 并发更新引用
   └── 遍历堆，将旧引用更新为新地址
```

#### 5.8.3 关键参数

```bash
-XX:+UseShenandoahGC
-XX:ShenandoahGCHeuristics=adaptive  # 自适应/static/compact/aggressive
-XX:ShenandoahAllocationThreshold=10 # 分配阈值（触发 GC）
-XX:ShenandoahUncommitDelay=30000    # 未提交内存保留（ms）
```

### 5.9 Parallel GC 深入

Parallel GC 是 JDK 8 默认 GC，吞吐量最高。

```bash
-XX:+UseParallelGC                   # 启用
-XX:+UseParallelOldGC                # 老年代并行（JDK 8 默认开启）
-XX:ParallelGCThreads=N              # 并行线程数
-XX:+UseAdaptiveSizePolicy           # 自适应大小调整（默认开启）
-XX:GCTimeRatio=99                   # 目标吞吐量 99%（默认 99）
-XX:MaxGCPauseMillis=100             # 目标暂停时间（仅做提示）
```

**适应式调整 (Adaptive Size Policy)：**
Parallel GC 会根据历史 GC 行为动态调整新生代大小、Survivor 比例等。

### 5.10 GC 选型决策树

```
你的应用需要什么？
│
├── 堆 < 2GB ?
│   └── → Serial GC 或 Parallel GC
│
├── 批处理 / 离线计算 ?
│   └── → Parallel GC（吞吐量最高）
│
├── Web 服务 / API ?
│   ├── 堆 2G-32G, P99 < 50ms →
│   │   └── G1 GC（通用默认）
│   ├── 堆 > 32G, P99 < 10ms →
│   │   └── ZGC（JDK 15+）或 Shenandoah（JDK 15+）
│   └── 堆 > 32G, P99 < 50ms →
│       └── G1 GC 或 ZGC
│
├── 微服务 (<2GB 堆) ?
│   └── → G1 GC 或 Serial GC
│
├── 低延迟金融/高频交易 ?
│   └── → ZGC 或 Shenandoah
│
├── 缓存服务（对象存活率高）?
│   └── → ZGC（Shenandoah 也可）
│
└── 极短生命周期（一次性的 CLI 工具）?
    └── → Epsilon GC（不作 GC，节约 CPU）
```

### 5.11 JDK 版本间 GC 行为差异

```bash
# JDK 8 Parallel GC
-XX:+UseParallelGC -XX:+UseParallelOldGC
# 默认 Auto 模式，根据硬件计算线程数

# JDK 11 G1 GC
-XX:+UseG1GC
# 不再需要显式设置 ParallelGCThreads（自动优化）

# JDK 17 G1 GC (改进)
# 默认 -XX:ParallelGCThreads 的计算方式改变
# G1 的 Full GC 现在支持并行（JDK 12+）

# JDK 21 G1 GC + ZGC (分代)
-XX:+UseZGC -XX:+ZGenerational
# Shenandoah 也支持分代
-XX:+UseShenandoahGC -XX:+ShenandoahGenerational
```

---

## 六、JIT 编译原理与调优

### 6.1 解释执行 vs JIT 编译

Java 的混合执行模式：

```
Java 源码 → bytecode → 解释执行（启动快）
               │
        热点检测（方法调用计数 / 回边计数）
               │
         ┌─────┴─────┐
         │           │
       C1 编译    C2 编译
    (客户端)    (服务端/优化级别更高)
         │           │
         └─────┬─────┘
               │
          切换执行点
          (On-Stack Replacement)
```

**JDK 8+ 默认：Tiered Compilation（分层编译）**

```
Level 0: 解释执行
Level 1: C1 简单编译（无 profiling）
Level 2: C1 受限 profiling
Level 3: C1 完全 profiling（使用频率计数确定热点）
Level 4: C2 编译（激进的优化）
```

### 6.2 JIT 触发阈值

```bash
# 方法编译阈值（调用次数）
-XX:CompileThreshold=10000          # 默认 10000（C2）
                                    # 分层编译时此值的工作方式不同
-XX:Tier3InvocationThreshold=200    # L3 调用阈值
-XX:Tier4InvocationThreshold=5000   # L4 调用阈值
-XX:Tier3MinInvocationThreshold=100
-XX:Tier4MinInvocationThreshold=600

# 回边阈值（循环触发）
-XX:BackEdgeThreshold               # 回边计数
-XX:Tier3BackEdgeThreshold=40000    # L3 回边
-XX:Tier4BackEdgeThreshold=40000    # L4 回边

# 编译线程
-XX:CICompilerCount=N               # 编译器线程数（默认 = CPU 核数）
                                    # JDK 21+ 动态调整
```

### 6.3 OSR (On-Stack Replacement)

长时间运行的循环在编译完成后，直接在栈上替换执行栈帧：

```java
public void hotLoop() {
    // 这个循环执行足够多次后触发 OSR
    for (int i = 0; i < 1_000_000; i++) {
        // JIT 编译完成后，OSR 直接在此替换执行
        compute(i);
    }
}
```

**影响：** 长运行循环在被 JIT 优化前性能较差。预热不足时第一个请求的性能会差很多。

### 6.4 JIT 主要优化技术

#### 6.4.1 方法内联 (Inlining)

```java
// 原始代码
int result = add(a, b);

// 内联后
int result = a + b;
```

```bash
-XX:MaxInlineSize=35              # 内联的 bytecode 大小（默认 35 bytes）
-XX:FreqInlineSize=325            # 热点方法内联大小（默认 325 bytes）
-XX:InlineSmallCode=2000          # 已编译代码太大时不内联
-XX:+PrintInlining                # 打印内联决策（调试用）
```

**内联是 JIT 最重要的优化，几乎所有其他优化都依赖内联后的更大视角。**

#### 6.4.2 逃逸分析 (Escape Analysis)

```java
// 如果 point 不逃逸，JIT 可以将其分配在栈上甚至完全消除
public int computeSum(int a, int b) {
    Point p = new Point(a, b);
    return p.x + p.y;
    // 优化后：直接 return a + b，不创建任何对象
}
```

```bash
-XX:+DoEscapeAnalysis      # 默认开启
-XX:+EliminateAllocations  # 标量替换（默认开启）
-XX:+EliminateLocks        # 锁消除（默认开启）
-XX:+PrintEscapeAnalysis   # 打印逃逸分析结果（调试用）
```

#### 6.4.3 锁优化

**偏向锁 (Biased Locking)** — JDK 8~15 默认开启，JDK 15+ 默认关闭并最终移除：

```java
// JDK 8: 假设锁不会被竞争 → 偏向锁
// JDK 15+: 偏向锁维护成本高于收益 → 废弃
synchronized (obj) {
    // ...
}
```

```bash
-XX:+UseBiasedLocking   # JDK 8 开启 / JDK 15+ 废弃
-XX:BiasedLockingStartupDelay=4000  # 偏向锁延迟启动（JDK 8）
```

**为什么移除偏向锁？** 偏向锁的撤销操作需要全局安全点，在高并发场景下反而降低性能。

#### 6.4.4 循环优化

- 循环展开 (Loop Unrolling)
- 循环剥离 (Loop Peeling)
- 循环向量化 (Auto-Vectorization) — 将标量操作转换为 SIMD 指令
- 循环不变量外提 (Loop Invariant Code Motion)

```java
// JDK 16+ 自动向量化：编译器可能将循环转为 SIMD 指令
for (int i = 0; i < length; i++) {
    result[i] = a[i] + b[i];
}
```

#### 6.4.5 死代码消除

```java
// 如果 computeFlag() 永远返回 false，JIT 会消除 if 块
if (computeFlag()) {
    expensiveComputation();
}
```

### 6.5 编译日志与调优

```bash
# 打印被编译的方法
-XX:+PrintCompilation

# 输出示例：
# 128  1 % b3! com.example.MyClass::hotMethod @ 23 (32 bytes)
# │   │ │ │               │                        │
# │   │ │ │               │                       方法大小 (bytecode)
# │   │ │ │               方法名
# │   │ │ 编译等级
# │   │ 线程编号
# │  编译 ID
# 时间戳 (ms)

# 更详细的编译日志
-Xlog:class+load:file=classload.log
-Xlog:jit+compilation=debug:file=jit.log
-Xlog:int+compilation=debug:file=int.log
```

**常见编译问题诊断：**

```bash
# 1. 编译过多占用 CPU
-XX:CICompilerCount=2   # 减少编译线程
-XX:-TieredCompilation  # 关闭分层编译（不推荐，但调试用）

# 2. 方法不被内联（调用次数不够）
-XX:FreqInlineSize=500   # 增大热点方法内联大小

# 3. Code Cache 溢出（编译停止）
# 症状：日志中出现 "CodeCache: full"
-XX:ReservedCodeCacheSize=512m  # 增大代码缓存
```

### 6.6 JDK 版本间 JIT 差异

| 特性 | JDK 8 | JDK 11 | JDK 17 | JDK 21 | JDK 23 |
|------|-------|--------|--------|--------|--------|
| 分层编译 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 逃逸分析 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 偏向锁 | ✅ | ✅ | ❌ 废弃 | ❌ | ❌ |
| 自动向量化 | 有限 | ✅ 增强 | ✅ 增强 | ✅ (AVX-512) | ✅ (SVE) |
| 内联缓存 | 单态 | 单态 | 单态 | 多态改进 | ✅ |
| 置换类指针 | ❌ | ❌ | ❌ | ✅ | ✅ |
| C2 去式化 | 不在计划中 | 不在计划中 | 讨论中 | 讨论中 | ✅ Graal JIT |

**JDK 21+ 的显式内联提示：**
```java
// JDK 16+ 提供了 -XX:InlineMixinCount
// JDK 17+ 可以间接通过 JIT 编译日志优化
```

---

## 七、JVM 参数优化实战

### 7.1 JVM 参数分类

```
标准参数（所有 JVM 实现通用）
├── -server, -client
├── -jar
├── -Dproperty=value
└── -verbose:class / gc / jni

-X 参数（非标准但稳定）
├── -Xms, -Xmx
├── -Xss
├── -Xmn
├── -Xloggc:file
└── -XshowSettings

-XX 参数（非标准，不稳定，可能变更）
├── -XX:+UseG1GC       (+ 开启)
├── -XX:-UseBiasedLocking  (- 关闭)
├── -XX:MaxGCPauseMillis=100  (= 数值)
└── -XX:+PrintFlagsFinal  (打印所有 JVM 参数)
```

### 7.2 生产环境基线配置

#### JDK 8（Parallel GC → 批处理）

```bash
java -Xms8g -Xmx8g \
     -Xmn3g \
     -XX:+UseParallelGC \
     -XX:+UseParallelOldGC \
     -XX:ParallelGCThreads=8 \
     -XX:+UseAdaptiveSizePolicy \
     -XX:GCTimeRatio=99 \
     -Xss512k \
     -XX:MetaspaceSize=256m \
     -XX:MaxMetaspaceSize=256m \
     -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/opt/app/dumps/ \
     -XX:+PrintGCDetails \
     -XX:+PrintGCDateStamps \
     -Xloggc:/var/log/app/gc.log \
     -jar app.jar
```

#### JDK 11+（G1 GC → Web 服务）

```bash
java -Xms4g -Xmx4g \
     -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=100 \
     -XX:G1HeapRegionSize=4m \
     -XX:InitiatingHeapOccupancyPercent=45 \
     -XX:+ParallelRefProcEnabled \
     -XX:+UseStringDeduplication \
     -XX:+AlwaysPreTouch \
     -Xss512k \
     -XX:MetaspaceSize=256m \
     -XX:MaxMetaspaceSize=256m \
     -XX:MaxDirectMemorySize=512m \
     -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/opt/app/dumps/ \
     -Xlog:gc*:file=/var/log/app/gc.log:time,pid,tid:filecount=10,filesize=10M \
     -jar app.jar
```

#### JDK 17+（ZGC → 超低延迟）

```bash
java -Xms8g -Xmx8g \
     -XX:+UseZGC \
     -XX:ConcGCThreads=4 \
     -XX:+AlwaysPreTouch \
     -Xss512k \
     -XX:MetaspaceSize=256m \
     -XX:MaxMetaspaceSize=256m \
     -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/opt/app/dumps/ \
     -Xlog:gc*:file=/var/log/app/gc.log:time,pid:filecount=10,filesize=10M \
     -jar app.jar
```

#### JDK 21+（分代 ZGC + 虚拟线程）

```bash
java -Xms8g -Xmx8g \
     -XX:+UseZGC \
     -XX:+ZGenerational \
     -XX:ConcGCThreads=4 \
     -XX:+AlwaysPreTouch \
     -Xss512k \
     -XX:MetaspaceSize=256m \
     -XX:MaxMetaspaceSize=256m \
     -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/opt/app/dumps/ \
     -Xlog:gc*:file=/var/log/app/gc.log:time,pid:filecount=10,filesize=10M \
     -jar app.jar
```

### 7.3 内存相关参数详解

```bash
# 堆
-Xms<size>                # 初始堆（4g, 1024m, 2g）
-Xmx<size>                # 最大堆（建议 = Xms）
-XX:+AlwaysPreTouch       # 启动时预分配物理内存
-XX:+UseTransparentHugePages  # 使用透明大页（Linux）

# 新生代
-Xmn<size>                # 新生代大小
-XX:NewRatio=N            # 老年代/新生代比例（默认 2）
-XX:SurvivorRatio=N       # Eden/Survivor 比例（默认 8）
-XX:TargetSurvivorRatio=N # 目标 Survivor 使用率（默认 50%）
-XX:MaxTenuringThreshold=N # 最大分代年龄（默认 15）
-XX:+AlwaysTenure         # 始终晋升到老年代（调试用）

# 元空间
-XX:MetaspaceSize=<size>
-XX:MaxMetaspaceSize=<size>
-XX:CompressedClassSpaceSize=<size>

# 直接内存
-XX:MaxDirectMemorySize=<size>
```

### 7.4 OOM 相关参数

```bash
# 自动堆转储
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/path/to/dumps/
-XX:+ExitOnOutOfMemoryError       # OOM 时直接退出进程

# 可用选项的版本差异
# JDK 8: -XX:OnOutOfMemoryError="kill -9 %p"
# JDK 11+: 推荐使用 -XX:+ExitOnOutOfMemoryError
```

### 7.5 常用诊断参数

```bash
# 打印所有 JVM 参数
-XX:+PrintFlagsFinal

# 打印命令行参数
-XX:+PrintCommandLineFlags

# GC 日志（JDK 8 及更早）
-XX:+PrintGCDetails
-XX:+PrintGCDateStamps
-XX:+PrintTenuringDistribution
-XX:+PrintHeapAtGC
-XX:+PrintReferenceGC
-Xloggc:/path/to/gc.log

# GC 日志（JDK 9+ 统一格式）
-Xlog:gc*:file=/path/to/gc.log:time,pid,tid:filecount=5,filesize=10M

# JFR
-XX:StartFlightRecording=duration=60s,filename=recording.jfr
```

### 7.6 大内存（>32GB）配置注意事项

```bash
# 当堆 > 32GB 时，压缩指针自动关闭，内存占用增加 10-20%
# 两种选择：

# 选项 A：保持在 31GB（推荐，使用压缩指针）
-Xms31g -Xmx31g

# 选项 B：跨过 32GB（接受指针膨胀）
-Xms64g -Xmx64g
# 这时可以考虑：
-XX:+UseZGC            # 大堆专用
# 如果必须用 G1:
-XX:G1HeapRegionSize=16m   # 增大 Region，减少 RSet 开销
```

### 7.7 字符串去重 (String Deduplication)

JDK 8u20+ 引入的一个隐藏特性，在 JDK 11+ 对 G1 默认可用：

```bash
-XX:+UseStringDeduplication   # G1 专用，将相同内容的字符串共享底层 char[]
# JDK 8 需要在支持此特性的版本
# JDK 11+ G1 默认支持
```

```java
// 没有字符串去重：
String a = new String("hello"); // char[] @100
String b = new String("hello"); // char[] @200

// 有字符串去重（GC 时触发）：
String a = new String("hello"); // char[] @100
String b = new String("hello"); // char[] → @100 (引用合并)
```

### 7.8 大页面 (Large Pages / Huge Pages)

操作系统的大页面（Linux 2MB 或 1GB）可以降低 TLB miss：

```bash
# 透明大页（THP）— 最简单
-XX:+UseTransparentHugePages

# 显式大页（需要系统配置）— 性能更好但需要提前分配
-XX:+UseLargePages
-XX:LargePageSizeInBytes=2m
```

**系统配置显式大页：**
```bash
# 查看当前大页状态
cat /proc/meminfo | grep Huge

# 分配大页（以 2MB 为例，分配 1024 个 = 2GB）
sudo sysctl vm.nr_hugepages=1024

# 永久配置
echo "vm.nr_hugepages=1024" >> /etc/sysctl.conf
```

---

## 八、容器环境 JVM 调优

### 8.1 JDK 版本容器感知能力

| JDK 版本 | CGroup v1 | CGroup v2 | CPU 感知 | 内存感知 | 推荐配置 |
|----------|-----------|-----------|----------|----------|---------|
| **JDK 8u131-** | ❌ | ❌ | ❌ | ❌ | 必须手动指定 |
| **JDK 8u131+** | ✅ | ❌ | ✅ | ✅ | 添加 `-XX:-UseContainerSupport` 实验标志 |
| **JDK 8u191+** | ✅ | ❌ | ✅ | ✅ | 添加 `-XX:ActiveProcessorCount` 等 |
| **JDK 10+** | ✅ | ❌ | ✅ | ✅ | 自动感知 |
| **JDK 11.0.12+** | ✅ | ✅ | ✅ | ✅ | 自动感知 |
| **JDK 15+** | ✅ | ✅ | ✅ | ✅ (增强) | 自动感知 |
| **JDK 17+** | ✅ | ✅ | ✅ | ✅ (全面) | 默认即可 |

**JDK 8 在容器中的正确配置：**

```bash
# JDK 8u131+：需要显式开启
-XX:+UnlockExperimentalVMOptions
-XX:+UseCGroupMemoryLimitForHeap
-XX:InitialRAMFraction=1
-XX:MaxRAMFraction=1

# JDK 8u191+：改进的参数
-XX:+UseContainerSupport          # 启用容器支持
-XX:InitialRAMPercentage=75.0     # 初始堆占比 75%
-XX:MaxRAMPercentage=75.0         # 最大堆占比 75%
-XX:MinRAMPercentage=50.0
```

### 8.2 CPU 限制

```bash
# Docker 中限制 CPU
docker run --cpus=2 ...
# JDK 11+ 自动感知到只有 2 个 CPU

# 手动覆盖感知到的 CPU 数量
-XX:ActiveProcessorCount=4        # 告诉 JVM 只看到 4 个核
                                  # 即使容器实际有 8 个核

# ParallelGCThreads 与 CICompilerCount 的自动计算
# JDK 11+：基于 ActiveProcessorCount 自动计算
# 公式（JDK 11+）：
# ParallelGCThreads = ActiveProcessorCount * 5/8 + 1 (if >1)
# CICompilerCount = ActiveProcessorCount (clamped to 2-16)
```

### 8.3 内存限制

```bash
# Docker 中限制内存
docker run --memory=4g ...

# JDK 11+ 自动感知：
-Xmx
# 等价于：MaxRAM * MaxRAMPercentage
# 其中 MaxRAM 是容器可用内存（cgroup 限制）

# 推荐配置（容器中）：
-XX:InitialRAMPercentage=75.0
-XX:MaxRAMPercentage=75.0
-XX:MinRAMPercentage=50.0
```

**⚠️ 容器内存陷阱：**

```
错误配置 1：在容器内显式设置 -Xmx4g，但容器内存限制只有 2g
→ 容器 OOMKilled

错误配置 2：在 2GB 限制的容器中不设置任何参数
→ JDK 11+ 默认 MaxRAMPercentage=25%，只用了 512MB
→ 堆太小，频繁 GC

正确做法：
-XX:MaxRAMPercentage=75.0  # 让 JVM 留 25% 给 OS/元空间/直接内存
```

### 8.4 Kubernetes 环境调优

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: java-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: openjdk:17-slim
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        env:
        - name: JAVA_TOOL_OPTIONS
          value: >
            -XX:+UseContainerSupport
            -XX:InitialRAMPercentage=75.0
            -XX:MaxRAMPercentage=75.0
            -XX:+UseZGC
            -XX:+AlwaysPreTouch
            -Djava.security.egd=file:/dev/./urandom
            -XX:+HeapDumpOnOutOfMemoryError
            -XX:HeapDumpPath=/dumps/
```

**K8s 内存申请/限制的经验：**
```
request.memory = 堆 (Xmx) / 0.7     # 留 30% 给元空间、栈、直接内存
例如：-Xmx=2g → request.memory ≈ 2.9g → 设为 3Gi
limit 建议 = request * 1.2 ~ 1.5（临时突增保护）
```

### 8.5 CPU Throttling 问题

容器中 CPU 限制过小时，JVM 的 GC 线程会与业务线程竞争：

```bash
# 症状：CPU throttling 导致 GC 暂停时间长
# 解决：
-XX:ParallelGCThreads=1     # 压制 GC 线程数
# 或减少 ActiveProcessorCount
-XX:ActiveProcessorCount=1
```

### 8.6 Spring Boot 容器化配置

```bash
# Spring Boot 3.x + JDK 21 + 虚拟线程
java -XX:+UseContainerSupport \
     -XX:InitialRAMPercentage=75.0 \
     -XX:MaxRAMPercentage=75.0 \
     -XX:+UseZGC \
     -XX:+ZGenerational \
     -XX:+AlwaysPreTouch \
     -Dspring.threads.virtual.enabled=true \
     -jar app.jar
```

---

## 九、JVM 性能剖析工具链

### 9.1 JDK 内置命令行工具

| 工具 | 用途 | 示例 |
|------|------|------|
| `jps` | 列出 Java 进程 | `jps -lvm` |
| `jstat` | JVM 统计信息 | `jstat -gcutil <pid> 1s` |
| `jcmd` | 万能诊断命令 | `jcmd <pid> GC.heap_dump dump.hprof` |
| `jstack` | 线程转储 | `jstack <pid>` / `jcmd <pid> Thread.print` |
| `jinfo` | JVM 配置信息 | `jinfo -flags <pid>` / `jcmd <pid> VM.flags` |
| `jmap` | 堆直方图/转储 | `jmap -dump:live,file=heap.hprof <pid>` |

**常用 jstat 命令：**

```bash
# GC 统计（每秒刷新）
jstat -gcutil <pid> 1000

# 输出示例：
S0    S1    E     O     M      YGC   YGCT  FGC  FGCT   GCT
0.00  0.00  45.2  38.7  92.3   124   2.345 3    0.567  2.912
S0/S1: Survivor 使用率
E: Eden 使用率
O: 老年代使用率
M: 元空间使用率
YGC: 年轻代 GC 次数
YGCT: 年轻代 GC 总时间
FGC: Full GC 次数
FGCT: Full GC 总时间
GCT: 所有 GC 总时间

# 类加载统计
jstat -class <pid> 1000
Loaded  Bytes  Unloaded  Bytes     Time
  4528  8766.5        0    0.0      4.29

# 编译统计
jstat -compiler <pid> 1000
Compiled Failed Invalid   Time   FailedType FailedMethod
    2457      0       0    12.45          0
```

### 9.2 jcmd 万能工具

JDK 7+ 引入，逐渐替代 jstack/jmap/jinfo：

```bash
# 查看可用子命令
jcmd <pid> help

# 常用命令
jcmd <pid> VM.version                    # JVM 版本
jcmd <pid> VM.flags                      # JVM 参数
jcmd <pid> VM.uptime                     # 运行时间
jcmd <pid> VM.summary                    # 全面概览
jcmd <pid> VM.system_properties          # 系统属性
jcmd <pid> Thread.print                  # 线程转储
jcmd <pid> GC.heap_dump /path/dump.hprof # 堆转储
jcmd <pid> GC.heap_info                  # 堆信息
jcmd <pid> GC.class_histogram            # 类直方图
jcmd <pid> GC.run                        # 强制 Full GC
jcmd <pid> GC.reasons                    # G1 专用：GC 原因统计
jcmd <pid> Compiler.codecache            # 代码缓存
jcmd <pid> Compiler.directives_add       # JIT 编译指令
```

### 9.3 JDK Flight Recorder (JFR)

JFR 是 Oracle JDK 内置的低开销事件记录框架，**适合生产环境**。

**启动方式：**

```bash
# 命令行启动时开启
-XX:StartFlightRecording=duration=60s,filename=recording.jfr

# 运行时动态
jcmd <pid> JFR.start duration=60s filename=recording.jfr
jcmd <pid> JFR.check                   # 检查录制状态
jcmd <pid> JFR.dump filename=recording.jfr
jcmd <pid> JFR.stop
```

**JFR 事件类型：**

| 事件 | 用途 | 开销 |
|------|------|------|
| GC 事件 | GC 暂停、GC 原因、GC 各阶段耗时 | 极低 |
| Allocation | TLAB 分配、堆外分配 | 极低 |
| 锁 | 同步锁定争、偏向锁撤销 | 极低 |
| 方法分析 | 热点方法栈 | 中（可配置） |
| I/O | 文件/网络读写 | 低 |
| 类加载 | 类加载/卸载 | 极低 |
| 编译 | JIT 编译、内联决策 | 极低 |
| 异常 | 异常抛出/捕获 | 低 |
| 线程 | 线程状态、死锁检测 | 极低 |

**配置 JFR 分析级别：**

```bash
# 默认配置（低开销，适合生产）
-XX:StartFlightRecording=settings=default

# Profile 配置（更多细节，适合预发/压测环境）
-XX:StartFlightRecording=settings=profile

# 自定义配置
# 1. 复制 $JAVA_HOME/lib/jfr/default.jfc
# 2. 修改事件阈值
# 3. 使用 -XX:FlightRecorderOptions=settings=myprofile.jfc
```

**JFR 分析工具：**
- **JDK Mission Control (JMC)** — 官方分析工具，JDK 11+ 开源免费
- **JFR 日志转 GC 日志** — `jfr print --events gc* recording.jfr`
- **自定义分析** — `jfr print --json recording.jfr > recording.json`

**版本差异：** JFR 在 JDK 8 仅限 Oracle JDK 商业版，JDK 11 起 OpenJDK 也免费可用。

### 9.4 堆转储分析 (Heap Dump)

```bash
# 自动 OOM 时生成堆转储
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/path/to/dumps/

# 手动触发
jcmd <pid> GC.heap_dump /path/to/dump.hprof

# 或使用 jmap
jmap -dump:live,format=b,file=dump.hprof <pid>
# live 参数：只 dump 存活对象（会触发 Full GC）
```

**推荐分析工具：**

| 工具 | 特点 | 适用场景 |
|------|------|----------|
| **Eclipse MAT** | 最强大的堆分析器，自动检测内存泄漏嫌疑 | 定位内存泄漏 |
| **VisualVM** | 可视化监控 + 堆分析，JDK 8/11 内置 | 日常监控分析 |
| **JProfiler** | 商业级全功能剖析器 | 深度性能分析 |
| **IntelliJ Profiler** | IDE 集成，IntelliJ Ultimate | 开发调试 |
| **GCeasy / HeapHero** | 在线自动分析 | 快速排查 |

**MAT 快速入门：**

```bash
# 下载 MAT: https://eclipse.dev/mat/
./MemoryAnalyzer -vm $JAVA_HOME/bin/java

# 命令行模式自动分析泄漏
./MemoryAnalyzer -consoleLog -application org.eclipse.mat.hprof.RefParser dump.hprof

# 常见分析报告：
# - Leak Suspects Report（泄漏嫌疑报告）
# - Top Components（最大对象/类）
# - GC Roots 路径追踪
# - Dominator Tree（支配树）
```

### 9.5 GC 日志分析

**GC 日志格式（JDK 11+ 统一日志）：**

```
[2024-01-15T10:30:42.123+0000][pid=12345][gc,start] GC(0) Pause Young (G1 Evacuation Pause)
[2024-01-15T10:30:42.145+0000][pid=12345][gc]      GC(0) Eden regions: 128->0(256)
[2024-01-15T10:30:42.145+0000][pid=12345][gc]      GC(0) Survivor regions: 16->16(32)
[2024-01-15T10:30:42.145+0000][pid=12345][gc]      GC(0) Old regions: 512->512
[2024-01-15T10:30:42.146+0000][pid=12345][gc]      GC(0) Metaspace: 128M->128M
[2024-01-15T10:30:42.146+0000][pid=12345][gc,ref]   GC(0) SoftReference: 0
[2024-01-15T10:30:42.146+0000][pid=12345][gc,ref]   GC(0) WeakReference: 123
[2024-01-15T10:30:42.146+0000][pid=12345][gc,ref]   GC(0) FinalReference: 45
[2024-01-15T10:30:42.147+0000][pid=12345][gc,phases] GC(0) Pre Evacuate Collection Set: 0.5ms
[2024-01-15T10:30:42.147+0000][pid=12345][gc,phases] GC(0) Evacuate Collection Set: 20.3ms
[2024-01-15T10:30:42.148+0000][pid=12345][gc,phases] GC(0) Post Evacuate Collection Set: 1.2ms
[2024-01-15T10:30:42.148+0000][pid=12345][gc,phases] GC(0) Other: 0.8ms
[2024-01-15T10:30:42.148+0000][pid=12345][gc]      GC(0) Pause Young 22.8ms
```

**常用日志标签组合：**

```bash
# 最小化生产日志（安全配置）
-Xlog:gc*,gc+ref*,gc+phases:file=gc.log:time,pid

# 调试日志
-Xlog:gc*=debug:file=gc.log:time,pid

# 包含所有细节
-Xlog:gc*=trace,gc+phases*=trace:file=gc.log:time,pid
```

**推荐 GC 日志分析工具：**

| 工具 | 特点 |
|------|------|
| **GCeasy (gceasy.io)** | 在线工具，可视化最佳，自动告警 |
| **GCViewer** | 开源，离线分析 |
| **JClarity (jclarity.com)** | 机器学习驱动的 GC 分析 |
| **GarbageCat** | 命令行的轻量 GC 分析工具 |

### 9.6 Async Profiler (async-profiler)

基于 Linux `perf` + Java `AsyncGetCallTrace`，零安全点的采样剖析器。

```bash
# 安装
# 从 https://github.com/async-profiler/async-profiler 下载

# CPU 采样（30 秒）
./profiler.sh -d 30 -o flamegraph <pid>

# 分配采样
./profiler.sh -d 30 -e alloc -o flamegraph <pid>

# 锁剖析
./profiler.sh -d 30 -e lock -o flamegraph <pid>

# 输出火焰图 SVG
# -o flamegraph → 火焰图
# -o jfr → JFR 格式（可用 JMC 打开）
```

**火焰图解读：**

```
火焰图从上到下是调用栈
宽度代表采样比例（越宽越热点）
颜色无特殊含义（通常暖色 = CPU）

关键观察：
1. 栈顶的函数是真正的热点
2. 查找"平顶"（顶部宽度大）→ 可以优化的函数
3. 查找 Java 代码中调用 native/内核 方法 → 可能需要不同策略
```

### 9.7 JMH (Java Microbenchmark Harness)

JDK 内置微基准测试框架，用于精确测量小段代码的性能。

```xml
<!-- Maven 依赖 -->
<dependency>
    <groupId>org.openjdk.jmh</groupId>
    <artifactId>jmh-core</artifactId>
    <version>1.37</version>
</dependency>
```

```java
import org.openjdk.jmh.annotations.*;

@BenchmarkMode(Mode.Throughput)
@OutputTimeUnit(TimeUnit.MILLISECONDS)
@State(Scope.Thread)
public class StringConcatBenchmark {

    private String a = "Hello";
    private String b = "World";

    @Benchmark
    public String concatPlus() {
        return a + ", " + b;
    }

    @Benchmark
    public String concatBuilder() {
        return new StringBuilder(a).append(", ").append(b).toString();
    }

    @Benchmark
    public String concatFormat() {
        return String.format("%s, %s", a, b);
    }
}
```

```bash
# 运行
java -jar benchmarks.jar StringConcatBenchmark

# 输出示例
Benchmark                            Mode  Cnt     Score    Error   Units
StringConcatBenchmark.concatPlus    thrpt    5  4562.344 ± 78.91  ops/ms
StringConcatBenchmark.concatBuilder thrpt    5  4321.567 ± 65.43  ops/ms
StringConcatBenchmark.concatFormat  thrpt    5   321.456 ± 12.34  ops/ms
```

**JMH 最佳实践：**
- 使用 `@Fork(2)` 避免前一次测试影响后一次
- 使用 `@Warmup(iterations=5, time=1)` 充分预热
- 不要在 `@Benchmark` 中创建太多新对象（影响 GC）
- 编译器优化可能消除你测的代码（`Blackhole.consume()` 防止）

### 9.8 perf + perf-map-agent（Linux 原生剖析）

```bash
# 安装 perf（Linux）
sudo apt install linux-tools-common linux-tools-generic

# perf-map-agent 将 JIT 编译的 Java 方法映射到 perf
# 安装：git clone https://github.com/jvm-profiling-tools/perf-map-agent

# 生成 Java 符号表
sudo java -agentpath:/path/to/libperfmap.so -jar app.jar

# 使用 perf 采样
sudo perf record -F 99 -g -p <pid> -- sleep 30
sudo perf script | FlameGraph/stackcollapse-perf.pl > out.folded
FlameGraph/flamegraph.pl out.folded > flamegraph.svg
```

### 9.9 APM 与监控平台

| 平台 | 特点 | 适用场景 |
|------|------|----------|
| **Prometheus + Grafana** | 通过 JMX Exporter 采集 JVM 指标 | 自建监控体系 |
| **Micrometer** | 统一指标 SDK，Spring Boot 集成 | Java 应用指标 |
| **Datadog** | 全栈 APM，JVM 集成完善 | 商业 APM |
| **New Relic** | Java Agent 深度集成 | 商业 APM |
| **Pinpoint** | 开源 APM，分布式追踪 | 调用链追踪 |
| **SkyWalking** | 国产开源 APM，调用链 + 指标 | 调用链追踪 |
| **Alibaba Arthas** | 在线诊断神器 | 快速生产诊断 |

**Arthas 常用命令：**

```bash
# 安装
curl -O https://arthas.aliyun.com/arthas-boot.jar
java -jar arthas-boot.jar

# 常用命令
dashboard          # 实时面板（线程/内存/GC）
thread -b          # 查看死锁
thread <id>        # 查看线程栈
jad com.example.MyClass       # 反编译类
watch com.example.MyClass method "{params,returnObj}" -x 2  # 观测方法调用
monitor com.example.MyClass method  # 监控方法调用频率/耗时
heapdump /tmp/dump.hprof      # 触发堆转储
vmtool --action getInstances --className java.lang.String --limit 10  # 获取实例
```

---

## 十、代码级性能优化与反模式

### 10.1 对象分配优化

**反模式：频繁创建临时对象**

```java
// ❌ 反模式：每次循环都创建 StringBuilder
for (int i = 0; i < 100000; i++) {
    StringBuilder sb = new StringBuilder();
    sb.append("prefix").append(i).append("suffix");
    process(sb.toString());
}

// ✅ 优化：重用 StringBuilder（但要注意线程安全）
StringBuilder sb = new StringBuilder(100);
for (int i = 0; i < 100000; i++) {
    sb.setLength(0);
    sb.append("prefix").append(i).append("suffix");
    process(sb.toString());
}
```

**反模式：不必要的装箱**

```java
// ❌ 反模式：隐式装箱/拆箱
Map<Integer, Long> map = new HashMap<>();
for (int i = 0; i < 1000000; i++) {
    map.put(i, (long) i);  // 每次自动装箱
}

// ✅ 优化：使用原始类型集合（如 Eclipse Collections）
IntLongMap map = new IntLongHashMap(1_000_000);
for (int i = 0; i < 1000000; i++) {
    map.put(i, i);  // 无装箱
}
```

**⚠️ 关于对象池：**
```java
// 老派优化：对象池 → 在 JDK 8+ 大多已不必要
// 原因：现代 JVM 的逃逸分析和 TLAB 使短期对象分配几乎免费
// 不要为小对象（无 I/O 连接）创建对象池，弊大于利

// 何时仍需要对象池：
// 1. 数据库连接池（创建耗时长）
// 2. 线程池（线程创建开销大）
// 3. DirectByteBuffer 池（Netty 的 PooledByteBufAllocator）
```

### 10.2 字符串优化

**JDK 8 vs JDK 11+ 的字符串布局：**

```java
// JDK 8: String 内部是 char[]
// JDK 9+: String 内部是 byte[] + coder 标记
// 英文/数字字符串占内存减半

// JDK 11+ Compact Strings
// 如果字符串所有字符在 Latin-1 范围内（0-255），用 1 字节存储
// 否则退化到 2 字节（UTF-16）
```

**性能对比代码：**

```java
import org.openjdk.jmh.annotations.*;

@BenchmarkMode(Mode.Throughput)
public class StringBenchmark {

    String[] strings;

    @Setup
    public void setup() {
        strings = new String[10000];
        for (int i = 0; i < 10000; i++) {
            strings[i] = "key_" + i;  // 都是 ASCII
        }
    }

    @Benchmark
    public Map<String, String> internTest() {
        Map<String, String> map = new HashMap<>();
        for (String s : strings) {
            map.put(s.intern(), s);  // intern 可能省内存，但增加 GC 压力
        }
        return map;
    }

    @Benchmark
    public Map<String, String> noIntern() {
        Map<String, String> map = new HashMap<>();
        for (String s : strings) {
            map.put(s, s);
        }
        return map;
    }
}
```

**字符串拼接的 JDK 版本差异：**
```java
// JDK 8: "a" + "b" → StringBuilder 显式创建
// JDK 9+: "a" + "b" → invokedynamic + StringConcatFactory
//       JIT 可以内联并做更激进的优化

// 所以 JDK 9+ 中简单的 + 拼接已经很快，
// 不需要手动改为 StringBuilder
```

### 10.3 异常性能

```java
// ❌ 反模式：用异常控制流程
try {
    Integer.parseInt(value);
} catch (NumberFormatException e) {
    // 预期情况当异常处理
}

// ✅ 正确：先判断
if (value != null && value.matches("\\d+")) {
    Integer.parseInt(value);
}
```

**性能数据（现代 JDK）：**
```
抛出并捕获一个异常 ≈ 1-5 µs（取决于栈深度）
普通条件判断 ≈ 1-10 ns
异常开销 ≈ 普通判断的 100-1000 倍
```

**JDK 17+ 异常性能改进：** JDK 17 优化了异常栈的构建，减少了空异常栈的开销。

### 10.4 Stream vs 循环

```java
// JDK 8-16: Stream 通常比手动循环慢 10-30%
// JDK 17+: Stream 的 JIT 优化大幅提升，差距缩小到 5-10%
// JDK 21+: 几乎无差距

// ✅ 建议：优先用 Stream 的可读性，除非在极端热点代码中
```

### 10.5 同步优化

```java
// ❌ 反模式：方法级同步
public synchronized void update(Counter c) {
    c.increment();
}

// ✅ 优化：缩小同步范围
public void update(Counter c) {
    if (c.shouldUpdate()) {
        synchronized (c) {
            c.increment();
        }
    }
}
```

**锁的状态演进（JDK 8）：**
```
无锁 → 偏向锁 → 轻量锁 → 重量锁（锁膨胀，不可逆）
```
**JDK 15+ 移除了偏向锁**，所以现在是：
```
无锁 → 轻量锁 → 重量锁
```

### 10.6 反射与方法句柄

```java
// ❌ 旧方法：cached Method (每调一次检查 access)
private static final Method GET_NAME;
static {
    GET_NAME = Person.class.getDeclaredMethod("getName");
    GET_NAME.setAccessible(true);
}
String name = (String) GET_NAME.invoke(person);

// ✅ 优化：MethodHandle（JDK 7+）
private static final MethodHandle GET_NAME;
static {
    MethodHandles.Lookup lookup = MethodHandles.lookup();
    GET_NAME = lookup.findGetter(Person.class, "name", String.class);
}
String name = (String) GET_NAME.invokeExact(person);

// ✅ 最优：VarHandle（JDK 9+，比 MethodHandle 更快）
private static final VarHandle NAME_HANDLE;
static {
    NAME_HANDLE = MethodHandles.lookup()
        .findVarHandle(Person.class, "name", String.class);
}
String name = (String) NAME_HANDLE.get(person);
```

**性能对比（JDK 21）：**
```
直接调用:         1x
VarHandle:        1.1x-1.3x
MethodHandle:     1.5x-2x
反射:             2x-10x
```

### 10.7 Lambda 与匿名内部类

```java
// JDK 8-10: Lambda 编译成 invokedynamic + -indy 自举方法
// JDK 11+: Lambda 的 invokedynamic 做更激进的 JIT 内联
// JDK 16+: Lambda 捕获的变量不再强制 final（effectively final）

// 性能结论：Lambda 通常比匿名内部类快
// 原因：匿名内部类会产生独立的 class 文件，Lambda 使用 invokedynamic
```

### 10.8 内存泄漏常见模式

```java
// 模式 1：ThreadLocal 未清理
private static final ThreadLocal<byte[]> BIG_DATA = new ThreadLocal<>();
// 在线程池中使用后不 remove() → 线程复用导致内存泄漏
// 解决：try { BIG_DATA.set(data); ... } finally { BIG_DATA.remove(); }

// 模式 2：集合中无效引用
static List<byte[]> cache = new ArrayList<>();
// 无上限 → OOM
// 解决：使用 WeakHashMap / Guava Cache / Caffeine

// 模式 3：内部类持有外部类引用
class Outer {
    class Inner {
        void doSomething() {
            // Inner 隐含持有 Outer.this 引用
        }
    }
}
// 解决：Inner 用静态内部类

// 模式 4：未关闭的资源
InputStream is = new FileInputStream("file.txt");
// 忘记 close() → FileDescriptor 泄漏
// 解决：try-with-resources (JDK 7+)
try (InputStream is = new FileInputStream("file.txt")) {
    // ...
}

// 模式 5：String.substring() 的内存泄漏（JDK 7- 特有）
// JDK 6-: substring() 共享原 char[]
// JDK 7+: substring() 复制新 char[]（已修复）
```

### 10.9 JDK 性能演进精华

```java
// JDK 8: Lambda, Stream, Optional, CompletableFuture
// JDK 9: 不可变集合工厂 (List.of), 接口私有方法
// JDK 11: var, HttpClient, Flight Recorder 开源
// JDK 14: Records (预览), instanceof pattern matching (预览)
// JDK 15: Records, Text Blocks, ZGC 正式, Shenandoah 正式
// JDK 16: Records 正式, Pattern matching for instanceof 正式
// JDK 17: Sealed Classes, 恢复 Always-Strict 浮点语义
// JDK 18: Simple Web Server, UTF-8 by default
// JDK 19: Virtual Threads (预览), Structured Concurrency (孵化)
// JDK 20: Scoped Values (孵化), Record Patterns (预览)
// JDK 21: Virtual Threads 正式, Record Patterns 正式, Pattern Matching for switch 正式
// JDK 22: Statements before super (预览), Stream Gatherers (预览)
// JDK 23: 模块导入声明 (预览), 灵活构造函数体 (预览)
```

---

## 十一、实战案例分析

### 案例 1：G1 GC 暂停时间优化（电商订单服务）

**场景：** 电商订单处理服务，堆 8GB，GC 暂停 300ms+，远超 SLO 50ms

**诊断步骤：**
```bash
# 1. 查看 GC 日志
# 发现频繁的 "G1 Evacuation Pause" 暂停 ~300ms
# 以及 "Initial Mark" 暂停 ~150ms

# 2. jstat 查看内存
jstat -gcutil <pid> 1000
# O (Old) 使用率一直在 85-90% 波动

# 3. jcmd 查看 GC 原因
jcmd <pid> GC.reasons
# 发现大部分 GC 由 Young 区满触发
# 混合回收速度跟不上老年代增长速度

# 4. 关键指标
# 分配速率: ~500 MB/s
# 每次 Young GC 晋升 ~100 MB
```

**解决方案：**
```bash
# 降低 IHOP 阈值，提前开始并发标记
-XX:InitiatingHeapOccupancyPercent=35

# 增加并发线程，加速标记
-XX:ConcGCThreads=4

# 降低目标暂停，让 G1 更积极地调整
-XX:MaxGCPauseMillis=50

# 增大新生代，减少 Young GC 频率
# 由默认 5% 改为 15%
-XX:G1NewSizePercent=15

# 增加混合回收轮次
-XX:G1MixedGCCountTarget=12

# 结果：暂停从 300ms 降至 40-60ms，P99 从 500ms 降至 80ms
```

### 案例 2：Parallel GC 吞吐量优化（批处理任务）

**场景：** 离线数据批处理任务，堆 32GB，总运行时间 5 小时

**诊断：**
```bash
# GC 时间占总 CPU 的 12%
# Full GC 每 30 分钟一次，每次 ~10 秒
```

**解决方案：**
```bash
# 使用 Parallel GC，最大化吞吐量
-XX:+UseParallelGC
-XX:+UseParallelOldGC
-XX:ParallelGCThreads=8

# 增大堆，减少 GC 频率
-Xms48g -Xmx48g       # 从 32G 加到 48G

# 增大新生代，减少 Full GC
-Xmn18g

# 结果：吞吐量提升 15%，总运行时间减少至 4 小时 10 分
```

### 案例 3：ZGC 在微服务中的应用

**场景：** 高 QPS Web 服务（QPS 5000+），要求 P99 < 5ms

**初始配置：**
```bash
-Xms4g -Xmx4g -XX:+UseG1GC -XX:MaxGCPauseMillis=50
# 实测 P99 = 12ms，不达标
```

**迁移到 ZGC：**
```bash
-XX:+UseZGC
-Xms4g -Xmx4g
-XX:ConcGCThreads=2
```

**结果对比：**
```
指标        G1 GC        ZGC
GC 暂停:    20-60ms      <1ms
P99 延迟:   12ms         3ms
P999 延迟:  50ms         5ms
CPU 开销:   基准          +5%（并发标记）
```

### 案例 4：内存泄漏排查（MAT 实战）

**场景：** 应用运行 48 小时后 OOM，堆 4GB

**步骤：**
```bash
# 1. OOM 时自动生成堆转储
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/opt/app/dumps/

# 2. 用 MAT 打开 dump
# Leak Suspects Report → 发现 HashMap 占 85% 内存

# 3. 追踪 GC Root 路径
# HashMap 被一个静态的 CacheManager 持有
# 键是 HttpSession ID

# 4. 根因
// 代码中 session 监听器未正确清理
// 用户登出时未调用 cache.remove(sessionId)

# 5. 修复
// 在 LogoutFilter 中添加缓存清理
// 改用 Caffeine 缓存，配置自动过期
```

### 案例 5：JIT 编译问题（启动预热）

**场景：** 批处理服务，每次处理 100 万条记录，约 5 分钟。
前 30 秒的处理速度明显慢于后面的。

**诊断：**
```bash
# 打印编译日志
-XX:+PrintCompilation
# 发现前 30 秒大量方法正在被编译（C1 → C3 → C4 逐级提升）

# 使用 JFR 查看 JIT 阶段
jcmd <pid> JFR.start filename=warmup.jfr
```

**解决：**
```bash
# 方案 A：缩短预热时间
-XX:TieredStopAtLevel=1    # 只到 C1（跳过 C2 优化，不适合长运行）
-XX:CICompilerCount=4      # 增加编译线程

# 方案 B：CDS + AppCDS 减少启动时间
-Xshare:auto
-XX:+UseAppCDS              # JDK 11+ 免费
# 第一次运行生成共享归档：
java -Xshare:dump -XX:+UseAppCDS -XX:ArchiveClassesAtExit=app.jsa -jar app.jar
# 后续运行：
java -Xshare:auto -XX:+UseAppCDS -XX:SharedArchiveFile=app.jsa -jar app.jar
```

### 案例 6：字符串去重节省内存

**场景：** 用户数据服务，缓存 500 万条用户记录，每条包含重复的地址字符串（城市名重复率高）

**配置：**
```bash
-XX:+UseStringDeduplication
```

**结果：** 字符串部分内存减少 40%，堆占用从 4.2GB 降至 3.1GB

### 案例 7：容器 CPU Throttling

**场景：** K8s 中运行的服务，CPU limit = 2，频繁出现 GC 暂停 200ms+

**诊断：**
```bash
# 查看容器 CPU 限制
cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us
# 200000 (2个核)
cat /sys/fs/cgroup/cpu/cpu.cfs_period_us
# 100000 (100ms)

# 默认 JVM 看到 8 个核（主机核数）→ 启动 8 个 GC 线程
# 容器限 2 个核 → 频繁 CPU throttling
```

**解决方案：**
```bash
# 手动指定处理器数量
-XX:ActiveProcessorCount=2
-XX:ParallelGCThreads=1
-XX:ConcGCThreads=1
# 或使用 JDK 11+ 自动容器感知
-XX:+UseContainerSupport
```

---

## 十二、JVM 调优黄金法则

1. **不要过早优化** — 先确保代码正确，再用工具量化性能
2. **一次只改一个参数** — 否则你不知道什么起了作用
3. **始终监控** — 没有监控就没有调优
4. **了解你的应用** — GC 行为取决于对象分配模式
5. **使用最新 JDK** — JDK 17/21 的 GC 性能远超 JDK 8
6. **GC 日志是免费的宝藏** — 始终开启 GC 日志
7. **内存泄漏先用 MAT 分析** — 别盲目加大 `-Xmx`
8. **容器中务必用容器感知参数** — `-XX:+UseContainerSupport`
9. **生产环境建议 `-Xms` = `-Xmx`** — 避免运行时动态扩展
10. **不要为了"优化"牺牲可读性** — 现代 JVM 已经非常聪明

### 推荐工具链

```bash
# 最小化生产配置（JDK 21 + 分代 ZGC）
java -Xms4g -Xmx4g \
     -XX:+UseZGC \
     -XX:+ZGenerational \
     -XX:+AlwaysPreTouch \
     -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/opt/app/dumps/ \
     -Xlog:gc*:file=/var/log/app/gc.log:time,pid:filecount=10,filesize=10M \
     -jar app.jar
```

**日常监控命令速查：**
```bash
# 实时 GC 状态
jstat -gcutil <pid> 1s

# 线程使用情况
jstack <pid> | grep -c "java.lang.Thread.State"

# 堆使用概览
jcmd <pid> VM.summary

# GC 原因（G1/ZGC 专用）
jcmd <pid> GC.reasons

# 实时性能面板
# Arthas: dashboard

# 30 秒 CPU 采样火焰图
profiler.sh -d 30 -o flamegraph <pid>
```

### JVM 参数快速查询表

```bash
# 查看所有当前 JVM 参数
jcmd <pid> VM.flags

# 查看所有可用参数及其默认值
java -XX:+PrintFlagsFinal -version | grep -i gc
java -XX:+PrintFlagsFinal -version | grep -i heap

# 查看参数是否被修改过
java -XX:+PrintFlagsFinal -version | grep ":= "   # := 表示被修改过
java -XX:+PrintFlagsFinal -version | grep "= "    # = 表示默认值
```

---

## 参考资源

- [Oracle 官方 JVM 调优指南](https://docs.oracle.com/en/java/javase/21/gctuning/)
- [G1 GC 官方文档](https://docs.oracle.com/en/java/javase/21/gctuning/)
- [ZGC 官方文档](https://docs.oracle.com/en/java/javase/21/gctuning/zgc.html)
- [Shenandoah GC 文档](https://wiki.openjdk.org/display/shenandoah)
- [Async Profiler](https://github.com/async-profiler/async-profiler)
- [Eclipse MAT 官方教程](https://eclipse.dev/mat/)
- [GCeasy 在线分析](https://gceasy.io/)
- [JDK Flight Recorder 指南](https://docs.oracle.com/en/java/javase/21/jfapi/)
- [JMH 官方示例](https://github.com/openjdk/jmh/tree/master/jmh-samples)
- [Alibaba Arthas](https://arthas.aliyun.com/)
- [JVM Performance Optimization (JEP Candidacy)](https://openjdk.org/projects/jeps/)

---

*本文基于 Saquib Aftab 在 Javarevisited 发表的 "Everything You Must Know About JVM Tuning & Profiling: Java Memory Management" 大纲扩展编写。在原作基础上大幅补充了 JDK 版本差异、容器调优、JIT 编译、代码级优化、更多工具链和实战案例。*
