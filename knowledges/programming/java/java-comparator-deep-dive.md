---
category: programming/java
---

# Comparator 深入用法 — 从青铜到王者

> If you can't sort it, you can't trust it.
> 排序是程序世界的基本盘，Comparator 是 Java 给排序配的瑞士军刀。

---

## 目录

1. [为什么需要 Comparator？](#1-为什么需要-comparator)
2. [Comparable vs Comparator — 两种排序哲学](#2-comparable-vs-comparator--两种排序哲学)
3. [Comparator 进化史 — 从匿名类到 Lambda](#3-comparator-进化史--从匿名类到-lambda)
4. [Comparator 的工厂方法军团](#4-comparator-的工厂方法军团)
5. [链式组合 — 多条件排序的艺术](#5-链式组合--多条件排序的艺术)
6. [null 安全排序 — 写给强迫症](#6-null-安全排序--写给强迫症)
7. [Stream + Comparator = 剔透的数据管线](#7-stream--comparator--剔透的数据管线)
8. [类型推断与泛型约束 — 为什么有时要写 `<T, U>`](#8-类型推断与泛型约束--为什么有时要写-t-u)
9. [性能考量 — Comparator 真的慢吗？](#9-性能考量--comparator-真的慢吗)
10. [实战：从简单到复杂的排序场景](#10-实战从简单到复杂的排序场景)
11. [陷阱与最佳实践](#11-陷阱与最佳实践)
12. [高级技巧与洞见](#12-高级技巧与洞见)

---

## 1. 为什么需要 Comparator？

想象一下：你有一个 `List<User>`，想按名字排序。

```java
list.sort((a, b) -> a.getName().compareTo(b.getName()));
```

5 个字符的 Lambda，搞定。但现实从来不会这么简单：

- 先按角色排序（ADMIN > MOD > USER）
- 相同角色按注册时间正序
- 相同时间按年龄倒序
- null 值排到最后

等你写完这个比较器，你可能会怀疑人生。Comparator 就是专门解决这种"比较复杂"的场景设计的。

### 排序需求金字塔

```
         ╱  多条件 +  null   ╲
        ╱    链式组合排序      ╲
       ╱────────────────────────╲
      ╱    类型安全 + 泛型       ╲
     ╱────────────────────────────╲
    ╱     单字段排序 + Lambda      ╲
   ╱────────────────────────────────╲
  ╱       基础 compareTo              ╲
 ╱──────────────────────────────────────╲
```

本文带你从底层爬上塔尖。

---

## 2. Comparable vs Comparator — 两种排序哲学

### Comparable — "你本身就应该是可比的"

```java
public class User implements Comparable<User> {
    private String name;
    private int age;

    @Override
    public int compareTo(User o) {
        return this.age - o.age;  // ⚠️ 有整数溢出风险，后面会讲
    }
}
```

**哲学：** 一个类有"自然顺序"。`String`, `Integer`, `LocalDate` 都实现了 `Comparable`。

**用途：** `TreeSet`, `TreeMap`, `Collections.sort()` 的默认行为。

### Comparator — "我来定义你们的比较规则"

```java
// 按名字长度排序（不改变 User 类）
Comparator<User> byNameLength = (a, b) -> a.getName().length() - b.getName().length();
```

**哲学：** 你可能无法（或者不应该）修改类本身，但你仍然需要排序。

**用途：** 同一个类有多种排序需求；你控制不了的第三方类。

### 一句话区分

> **Comparable** = "我天生可以比较"（类内部）
> **Comparator** = "我来制定规则"（类外部）

| | Comparable | Comparator |
|---|---|---|
| 包 | `java.lang` | `java.util` |
| 函数式接口？ | 否（抽象方法 1 个但不是 @FunctionalInterface） | 是（@FunctionalInterface） |
| 修改原类？ | 是 | 否 |
| 排序维度 | 单一自然顺序 | 任意多维度 |
| Lambda 友好？ | 构造时定死 | 现用现写 |

---

## 3. Comparator 进化史 — 从匿名类到 Lambda

先来看同一个需求的三代写法，感受 Java 的进化：

### 石器时代：匿名内部类

```java
list.sort(new Comparator<User>() {
    @Override
    public int compare(User a, User b) {
        return Integer.compare(a.getAge(), b.getAge());
    }
});
```

**痛感：** 6 行模板代码，就为了写一个减法。

### 青铜时代：Lambda

```java
list.sort((a, b) -> Integer.compare(a.getAge(), b.getAge()));
```

**进化：** 编译器帮你做类型推断，`a` 和 `b` 的类型自动识别为 `User`。

### 黄金时代：方法引用 + 静态工厂

```java
list.sort(Comparator.comparingInt(User::getAge));
```

**质变：** 从"描述怎么做"变成"描述要什么"。声明式编程的魅力。

> 这三行代码完全等价。但每次进化都减少了犯错空间。

---

## 4. Comparator 的工厂方法军团

Java 8 给 `Comparator` 接口加了一大波静态方法。记住它们 ≈ 记住了一整本排序手册。

### 4.1 基础工厂

```java
// 按某个 key 排序
Comparator.comparing(Function<? super T, ? extends U> keyExtractor)
Comparator.comparingInt(ToIntFunction<? super T> keyExtractor)
Comparator.comparingLong(ToLongFunction<? super T> keyExtractor)
Comparator.comparingDouble(ToDoubleFunction<? super T> keyExtractor)
```

**为什么要有 `comparingInt` 而不是只用 `comparing`？**

因为 `comparing` 要求 key 本身是 `Comparable`，并且中间会经历装箱。`comparingInt` 直接操作原始 `int`，省一个拆装箱。

```java
// ❌ 会装箱
Comparator.comparing(User::getAge);

// ✅ 无装箱
Comparator.comparingInt(User::getAge);
```

### 4.2 自然顺序/逆序

```java
Comparator.naturalOrder()   // 自然顺序，等效于 Comparable.compareTo
Comparator.reverseOrder()   // 自然逆序
```

**冷知识：** `naturalOrder()` 返回的是 `Comparator` 内部的一个单例，不重复创建对象。

### 4.3 链式扩展

```java
Comparator.thenComparing(Function<? super T, ? extends U> keyExtractor)
// 还有 thenComparingInt, thenComparingLong, thenComparingDouble
Comparator.thenComparing(Comparator<? super T> other)
```

### 4.4 null 处理

```java
Comparator.nullsFirst(Comparator<T> comparator)   // null 值排最前
Comparator.nullsLast(Comparator<T> comparator)    // null 值排最后
```

**`nullsFirst(null)` 是合法的：** 传 `null` = 所有非 null 视为相等。

### 4.5 其他

```java
// 不对等比较——小心使用
Comparator.naturalOrder().reversed()
```

现在把这些方法画成一张关系图：

```
                    comparing + thenComparing + nullsFirst/nullsLast
                  ╱                    ╲
       声明式工厂方法              命令式 Lambda
      (comparing, thenComparing)   ((a,b) -> ...)
                  │                    │
                  ╲                    ╱
               compare(T o1, T o2) — 函数式接口的唯一抽象方法
```

---

## 5. 链式组合 — 多条件排序的艺术

这是 Comparator 最强大的地方——像搭积木一样组装排序规则。

### 5.1 基础链式

```java
Comparator<User> comparator = Comparator
        .comparing(User::getRole)          // 第一级：按角色
        .thenComparing(User::getCreatedAt) // 第二级：按创建时间
        .thenComparing(User::getAge);      // 第三级：按年龄
```

每一级只在上一级判定相等时才触发。这叫 **字典序**（lexicographic order），和 String 的 `compareTo` 逻辑一样。

### 5.2 混合正序/倒序

```java
Comparator<User> comparator = Comparator
        .comparing(User::getRole)
        .thenComparing(User::getCreatedAt)
        .thenComparing(Comparator.comparingInt(User::getAge).reversed());
```

`reversed()` 会反转整个 Comparator，包括之前所有已定义的规则吗？

**重要：** 看这个方法在谁身上调用的。

```java
// ⚠️ 这会反转全部三级规则
Comparator<User> allReversed = Comparator
        .comparing(User::getRole)
        .thenComparing(User::getCreatedAt)
        .thenComparingInt(User::getAge)
        .reversed();

// ✅ 这只反转年龄这一级
Comparator<User> onlyAgeReversed = Comparator
        .comparing(User::getRole)
        .thenComparing(User::getCreatedAt)
        .thenComparing(Comparator.comparingInt(User::getAge).reversed());
```

### 5.3 复杂业务排序

**需求：** 一个任务列表，排序规则：
1. `COMPLETED` 状态的排到最后（无论其他字段）
2. 其余任务：按优先级 HIGH > MEDIUM > LOW
3. 同优先级：按截止时间（越近越前）
4. 截止时间为 null 的排最后（同优先级内）

```java
Comparator<Task> comparator = Comparator
        .<Task, Boolean>comparing(t -> t.getStatus() == Status.COMPLETED)
        .thenComparing(Comparator.comparingInt(t -> priorityRank(t.getPriority())))
        .thenComparing(Comparator.nullsLast(Comparator.comparing(Task::getDeadline)));
```

**注意技巧：** `<Task, Boolean>comparing` 这种显式类型声明是为了帮助编译器推断类型参数。`Boolean` 的 `compareTo` 中 `false < true`，所以 `COMPLETED`（返回 `true`）会自动排到最后。

---

## 6. null 安全排序 — 写给强迫症

NullPointerException 是排序的第一杀手。

### 6.1 场景分析

```java
List<User> users = Arrays.asList(
    new User("Alice", 30),
    null,
    new User(null, 25),
    new User("Bob", null)
);
```

这里有三种 null：
- **元素本身为 null** → `nullsFirst()` / `nullsLast()`
- **key 为 null**（名字为 null）→ `Comparator.nullsLast(Comparator.comparing(User::getName))`
- **key 包装类型为 null**（年龄 Integer 为 null）→ 同上

### 6.2 实战：最安全的排序

```java
// 元素 null 到最后，名字 null 到最后，年龄 null 到最前
List<User> sorted = users.stream()
        .sorted(Comparator.nullsLast(Comparator
                .comparing(User::getName, Comparator.nullsLast(Comparator.naturalOrder()))
                .thenComparing(Comparator.comparingInt(u -> u.getAge() == null ? Integer.MAX_VALUE : u.getAge()))
        ))
        .collect(Collectors.toList());
```

**提问：** `Comparator.comparing(User::getName, Comparator.nullsLast(Comparator.naturalOrder()))` 中的第二个参数是什么意思？

**答：** `comparing` 有两个重载版本：
- `comparing(keyExtractor)` — key 本身必须实现 `Comparable`
- `comparing(keyExtractor, keyComparator)` — 用自定义 `keyComparator` 来比较 key

第二个参数让你可以在 key 层面也使用 `nullsFirst/nullsLast`。

### 6.3 一个更简洁的模式（Java 16+）

```java
// 用 records 消除 null 问题
record SafeUser(String name, int age) {}

List<SafeUser> safeUsers = users.stream()
        .filter(Objects::nonNull)
        .map(u -> new SafeUser(
                u.getName() != null ? u.getName() : "",
                u.getAge() != null ? u.getAge() : 0
        ))
        .sorted(Comparator.comparing(SafeUser::name)
                .thenComparing(SafeUser::age))
        .toList();  // Java 16+ Stream.toList()
```

**哲学：** 与其到处处理 null，不如在进入排序前的一刻做好防御性转换。

---

## 7. Stream + Comparator = 剔透的数据管线

### 7.1 Top-N 问题

```java
// 年龄最大的 5 个人
List<User> top5 = users.stream()
        .sorted(Comparator.comparingInt(User::getAge).reversed())
        .limit(5)
        .collect(Collectors.toList());
```

**⚠️ 性能警告：** `sorted()` 会全量排序再取前 5。如果 users 很大（>10 万），用以下方案：

```java
// 更高效：只维护大小为 5 的最小堆
PriorityQueue<User> heap = new PriorityQueue<>(
        5, Comparator.comparingInt(User::getAge)
);
for (User u : users) {
    heap.offer(u);
    if (heap.size() > 5) heap.poll();
}
List<User> top5 = new ArrayList<>(heap);
```

### 7.2 分组内排序

```java
// 按角色分组，每组内按年龄排序
Map<String, List<User>> sortedByRole = users.stream()
        .collect(Collectors.groupingBy(
                User::getRole,
                Collectors.collectingAndThen(
                        Collectors.toList(),
                        list -> list.stream()
                                .sorted(Comparator.comparingInt(User::getAge))
                                .collect(Collectors.toList())
                )
        ));
```

**优雅升级版（使用 Java 16+ `toList`）：**

```java
Map<String, List<User>> sortedByRole = users.stream()
        .collect(Collectors.groupingBy(
                User::getRole,
                Collectors.toCollection(ArrayList::new)
        ));
sortedByRole.values().forEach(
        list -> list.sort(Comparator.comparingInt(User::getAge))
);
```

### 7.3 联合排序 + 去重

```java
// 按 name 去重，取每个 name 中 age 最大的
List<User> uniqueByName = users.stream()
        .collect(Collectors.toMap(
                User::getName,
                Function.identity(),
                BinaryOperator.maxBy(Comparator.comparingInt(User::getAge))
        ))
        .values().stream()
        .sorted(Comparator.comparing(User::getName))
        .collect(Collectors.toList());
```

**注意：** `BinaryOperator.maxBy(Comparator)` 是 `Comparator` 在 `Stream` 中的一个冷门用法，返回的是两个元素中"更大"的那个。

---

## 8. 类型推断与泛型约束 — 为什么有时要写 `<T, U>`

### 8.1 编译器"不够聪明"的时刻

```java
// ❌ 编译错误：无法推断类型
Comparator<User> c = Comparator.comparing(u -> u.getName());
```

**为什么？** `comparing` 的签名是：

```java
public static <T, U extends Comparable<? super U>> Comparator<T> comparing(
        Function<? super T, ? extends U> keyExtractor
)
```

Lambda `u -> u.getName()` 需要同时推断 `T=User` 和 `U=String`。在赋值给 `Comparator<User>` 时，`T` 能推断出来，但 `U` 需要 Lambda 的返回类型推理，而 Lambda 的返回类型又从 `U` 的边界推断……这就成了死锁。

**解决：**

```java
// ✅ 方法 1：显式类型
Comparator<User> c = Comparator.<User, String>comparing(u -> u.getName());

// ✅ 方法 2：方法引用（推荐）
Comparator<User> c = Comparator.comparing(User::getName);
```

方法引用 `User::getName` 有明确的返回类型 `String`，编译器不需要死锁推理。

### 8.2 多级链式推断

```java
// 这种链式调用中，每一步的类型推断是独立的
Comparator<User> c = Comparator
        .<User, String>comparing(User::getName)  // 这里告诉编译器 T=User, U=String
        .thenComparingInt(User::getAge);         // 这里自动推断
```

初学时可以不写 `<User, String>`，用方法引用让编译器自己推。只有遇到编译失败时才加显式类型。

---

## 9. 性能考量 — Comparator 真的慢吗？

### 9.1 Lambda 有额外开销吗？

```java
// 选项 A：Lambda
list.sort((a, b) -> Integer.compare(a.getAge(), b.getAge()));

// 选项 B：方法引用
list.sort(Comparator.comparingInt(User::getAge));
```

**答案：** 二者在运行期性能几乎一致。

- Lambda 表达式编译为 `invokedynamic`，JVM 第一次调用时生成一个匿名函数对象，之后缓存
- `Comparator.comparingInt()` 内部也是返回一个 Lambda（或匿名类）

**两种写法在实际 benchmark 中差 < 5%，选你读着顺的。**

### 9.2 sorted() + limit(N) 会全排序吗？

**会！** `Stream.sorted()` 是**有状态中间操作**，它会消费整个流、内部数组排序、然后产生排序后的流。后续 `limit(N)` 只是取前 N 个。

```java
// 100 万个元素 → 全排序 → 取前 10
stream.sorted().limit(10).collect(...)
```

**对大数据集的建议：**

| 数据量 | 方案 |
|---|---|
| < 1 万 | 直接 sorted() + limit()，无所谓 |
| 1 万 ~ 10 万 | 注意一点，但通常还能接受 |
| > 10 万 | 考虑 PriorityQueue / 数据库 ORDER BY + LIMIT |
| > 100 万 | 绝对不要全量排序，用外部排序或数据库 |

### 9.3 Comparator 对象复用

Comparator 是不可变的，可以安全地缓存为 `static final` 常量复用。

```java
public class UserService {
    private static final Comparator<User> DEFAULT_SORT = Comparator
            .comparing(User::getRole)
            .thenComparing(Comparator.comparingInt(User::getAge).reversed())
            .thenComparing(User::getName);
    
    public List<User> getSortedUsers() {
        return users.stream()
                .sorted(DEFAULT_SORT)
                .collect(Collectors.toList());
    }
}
```

**为什么值得做：** 避免每次调用都创建新的 Comparator 对象链。虽然开销很小，但在高频调用路径上（比如每秒上千次查询），对象分配也是成本。

---

## 10. 实战：从简单到复杂的排序场景

### 场景 1：按分数排名（最基础）

```java
students.sort(Comparator.comparingInt(Student::getScore).reversed());
```

### 场景 2：先按通过率降序，再按提交数降序

```java
problems.sort(Comparator
        .comparingDouble(Problem::getPassRate).reversed()
        .thenComparingInt(Problem::getSubmissionCount).reversed());
```

### 场景 3：自定义权重排序

```java
// 风险等级：CRITICAL > HIGH > MEDIUM > LOW
Map<RiskLevel, Integer> weight = Map.of(
    RiskLevel.CRITICAL, 4,
    RiskLevel.HIGH, 3,
    RiskLevel.MEDIUM, 2,
    RiskLevel.LOW, 1
);

alerts.sort(Comparator
        .comparingInt(a -> weight.getOrDefault(a.getRiskLevel(), 0))
        .reversed()
        .thenComparing(Alert::getCreatedAt));
```

### 场景 4：多字段 + 业务规则

**需求：** 会议室预定列表：
1. 状态排序：CONFIRMED > PENDING > CANCELLED
2. 同状态按开始时间正序
3. 同时间按会议室容量倒序
4. 容量 null 视为 0

```java
List<Booking> sorted = bookings.stream()
        .sorted(Comparator
                .comparingInt(b -> statusRank(b.getStatus()))
                .thenComparing(Booking::getStartTime)
                .thenComparing(
                        Comparator.comparingInt(b -> b.getCapacity() != null ? b.getCapacity() : 0)
                                .reversed()
                ))
        .collect(Collectors.toList());

// 辅助方法
private static int statusRank(BookingStatus s) {
    return switch (s) {
        case CONFIRMED -> 0;
        case PENDING   -> 1;
        case CANCELLED -> 2;
    };
}
```

### 场景 5："接近度"排序（非传统比较）

```java
// 按坐标距离某个点由近到远排序
Point target = new Point(0, 0);
points.sort(Comparator.comparingDouble(
        p -> Math.sqrt(Math.pow(p.x() - target.x(), 2) + Math.pow(p.y() - target.y(), 2))
));
```

注意：每次比较都会重新计算距离。如果列表很大，考虑先计算并缓存距离：

```java
points.stream()
        .map(p -> new AbstractMap.SimpleEntry<>(p, distance(p, target)))
        .sorted(Entry.comparingByValue())
        .map(Entry::getKey)
        .collect(Collectors.toList());
```

---

## 11. 陷阱与最佳实践

### 陷阱 1：整数减法溢出

```java
// ❌ 危险！
Comparator.comparingInt(u -> u.getAge() - u2.getAge());
// 或者 compareTo 用减法：
@Override public int compareTo(User o) { return this.age - o.age; }
```

当 `this.age = Integer.MAX_VALUE` 而 `o.age = -1` 时，`MAX_VALUE - (-1) = Integer.MIN_VALUE`（溢出），结果是负数！

```java
// ✅ 安全写法
Comparator.comparingInt(User::getAge);  // 内部用 Integer.compare
// 或者
(a, b) -> Integer.compare(a.getAge(), b.getAge());
// 或者（Java 7+）
(a, b) -> Integer.compare(a.getAge(), b.getAge());
```

### 陷阱 2：compare 方法不满足传递性

Comparator 要求：`compare(a, b) < 0` 且 `compare(b, c) < 0` ⇒ `compare(a, c) < 0`

```java
// ❌ 破坏传递性！
Comparator<Double> bad = (a, b) -> {
    if (Math.abs(a - b) < 0.01) return 0;  // 近似相等
    return Double.compare(a, b);
};
```

`0.005` 和 `0.012` 近似相等（差 0.007 < 0.01），`0.012` 和 `0.019` 近似相等。但 `0.005` 和 `0.019` 的差是 0.014 > 0.01，不相等。这样传递性就断了。

**后果：** 某些排序算法会**抛出异常**（TimSort 会检测到 inconsistent comparator），或者产生不可预期的结果。

### 陷阱 3：Comparator 不一致与 equals

`TreeSet`, `TreeMap` 使用 Comparator 判断相等，而不是 `equals()`。

```java
Set<User> set = new TreeSet<>(Comparator.comparing(User::getId));
set.add(new User(1, "Alice"));
set.add(new User(1, "Bob"));  // ⚠️ 被认为相等（id 相同），不会加入！

System.out.println(set.size());  // 1
System.out.println(set.contains(new User(1, "Charlie")));  // true（只比 id）
```

**最佳实践：** 确保 Comparator 的相等定义和业务语义一致。如果希望用 `equals()`，那就只用 `HashSet` 不用 `TreeSet`。

### 陷阱 4：sorted() 的稳定性

`Stream.sorted()` 是**稳定排序**吗？**不是。根据规范：**

> For ordered streams, the sort is stable. For unordered streams, no stability guarantees are made.

但 `List.sort()` 用的是 `TimSort`，是稳定排序。

```java
// 稳定排序的典型应用：先按 A 排，再按 B 排，保留 A 的相对顺序
list.sort(Comparator.comparing(Item::getCategory));  // 第一轮
list.sort(Comparator.comparingInt(Item::getPriority).reversed());  // 第二轮
// 结果：同优先级内，类别顺序保持第一轮的排序
```

### 陷阱 5：重复比较非幂等

**问题**：某些场景下，比较器内读取的字段可能在排序过程中被其他线程修改，导致比较结果不一致。

```java
// ❌ 排序过程中 score 可能被修改
list.sort(Comparator.comparingInt(Player::getScore));
```

**应对：** 敏感场景下快照排序——先复制一份不可变数据再排序。

---

## 12. 高级技巧与洞见

### 12.1 Comparator 和排序算法的关系

Java 的 `List.sort()` 和 `Arrays.sort()` 使用 **TimSort**（归并排序 + 插入排序的混合体，Python 发明的，Java 移植了）。

TimSort 是：
- **稳定排序** → 所以链式多级排序的"先排 A 再排 B"技巧才有效
- **自适应** → 对接近有序的数组 O(n)，对乱序 O(n log n)
- **空间复杂度** O(n) → 需要额外的数组做合并

**对你写 Comparator 的影响：**

TimSort 会检测 `compare(a, b)` 的结果是否自洽。如果检测到不一致（比如违反传递性），会抛：

```
java.lang.IllegalArgumentException: Comparison method violates its general contract!
```

> 这个异常是 Java 7 引入的，当时导致无数项目崩溃（包括 JDK 自己的 `TimSort.sort()`）。**这是 Java 历史上最著名的排序 bug 之一。**

### 12.2 自定义 Comparator 的几种模式

#### 模式 A：枚举排序

```java
enum Priority {
    HIGH, MEDIUM, LOW;  // ordinal: 0, 1, 2
}

// 直接用 ordinal —— 但别改枚举顺序！
tasks.sort(Comparator.comparingInt(t -> t.getPriority().ordinal()));
```

**风险：** 在枚举中新增一个 `CRITICAL`，如果写在 `HIGH` 前面，所有已有排序逻辑全乱。

**推荐做法：** 用 `Map` 或显式权重：

```java
private static final Map<Priority, Integer> PRIORITY_WEIGHT = Map.of(
    Priority.HIGH, 3,
    Priority.MEDIUM, 2,
    Priority.LOW, 1
);
tasks.sort(Comparator.comparingInt(t -> PRIORITY_WEIGHT.getOrDefault(t.getPriority(), 0)).reversed());
```

#### 模式 B：链式 if-else 到 Comparator 的转换

```java
// ❌ 命令式 if-else
list.sort((a, b) -> {
    int roleCmp = Integer.compare(a.getRoleRank(), b.getRoleRank());
    if (roleCmp != 0) return roleCmp;
    int timeCmp = a.getCreatedAt().compareTo(b.getCreatedAt());
    if (timeCmp != 0) return timeCmp;
    return Integer.compare(b.getAge(), a.getAge());  // age desc
});

// ✅ 声明式链式
list.sort(Comparator
        .comparingInt(User::getRoleRank)
        .thenComparing(User::getCreatedAt)
        .thenComparing(Comparator.comparingInt(User::getAge).reversed()));
```

声明式更短、更安全、更可读。当逻辑复杂到需要 if-else 时，先想想能不能拆成链式。

#### 模式 C：比较器组合混搭

```java
@SafeVarargs
public static <T> Comparator<T> chain(Comparator<T>... comparators) {
    return (a, b) -> {
        for (Comparator<T> c : comparators) {
            int result = c.compare(a, b);
            if (result != 0) return result;
        }
        return 0;
    };
}

// 使用
Comparator<User> c = chain(
    Comparator.comparingInt(User::getRoleRank),
    Comparator.comparing(User::getCreatedAt),
    Comparator.comparingInt(User::getAge).reversed()
);
```

`thenComparing` 本质上就是做这个。除非你需要**动态组合**（运行时决定走哪几条规则），否则直接用 `thenComparing`。

### 12.3 Comparator + Optional 的优雅联动

```java
// 找到列表中年龄最大的人
users.stream()
    .max(Comparator.comparingInt(User::getAge))
    .ifPresent(System.out::println);

// 找到列表中名字最短的人
users.stream()
    .min(Comparator.comparingInt(u -> u.getName().length()))
    .ifPresent(System.out::println);
```

`Stream.max()` 和 `Stream.min()` 底层调用的就是 `reduce` 配合 `BinaryOperator.maxBy/minBy`，而这两个方法接受的是 `Comparator`。

### 12.4 函数式 Comparator 的数学之美

Comparator 是一个**半群**（Semigroup）——即两个 Comparator 可以"合并"成一个新的 Comparator（`thenComparing`），并且这个操作是**结合的**：

```
(A.thenComparing(B)).thenComparing(C) == A.thenComparing(B.thenComparing(C))
```

```java
Comparator<User> c1 = Comparator.comparing(User::getName);
Comparator<User> c2 = Comparator.comparingInt(User::getAge);
Comparator<User> c3 = Comparator.comparing(User::getRole);

// 三者等价
Comparator<User> combined = c1.thenComparing(c2).thenComparing(c3);
Comparator<User> combined2 = c1.thenComparing(c2.thenComparing(c3));
```

这意味着你可以把多个 Comparator 积木自由组合，顺序不影响最终结果。

### 12.5 反向思考：什么情况下不要用 Comparator？

- **数据在数据库里** → ORDER BY + LIMIT 比全量加载再排序快 100 倍
- **元素很少（< 20）** → 手写插入排序可能更快（避免 Lambda 调用开销）
- **只需要取最大/最小** → `stream().max()` 或 PriorityQueue，不需要全排序
- **排序规则极复杂（> 5 级条件）** → 考虑封装成 `Comparable` 实现一个 `compareTo` 方法，或者拆成多个步骤

---

## 附录：快速参考卡

### Comparator 工厂方法速查

| 方法 | 用途 | 示例 |
|---|---|---|
| `comparing(keyExtractor)` | 按 key 排序 | `comparing(User::getName)` |
| `comparingInt(keyExtractor)` | 按 int 排序 | `comparingInt(User::getAge)` |
| `comparingLong(keyExtractor)` | 按 long 排序 | `comparingLong(Order::getId)` |
| `comparingDouble(keyExtractor)` | 按 double 排序 | `comparingDouble(Item::getPrice)` |
| `naturalOrder()` | 自然顺序 | `naturalOrder()` |
| `reverseOrder()` | 自然逆序 | `reverseOrder()` |
| `nullsFirst(comp)` | null 在最前 | `nullsFirst(comparing(...))` |
| `nullsLast(comp)` | null 在最后 | `nullsLast(comparing(...))` |
| `thenComparing(...)` | 追加次级排序 | `.thenComparing(User::getAge)` |
| `reversed()` | 反转全部 | `.reversed()` |

### 常见陷阱清单

1. ❌ `a.getAge() - b.getAge()` → ✅ `Integer.compare(a.getAge(), b.getAge())`
2. ❌ 近似相等破坏传递性 → ✅ 精确比较或使用宽容度可控的方案
3. ❌ 忽略 `reversed()` 的作用范围 → ✅ 局部反转用 `Comparator.comparing(...).reversed()`
4. ❌ null 字段 → ✅ `nullsFirst` / `nullsLast` 或防御性转换
5. ❌ 全量排序取 Top-N → ✅ PriorityQueue 或数据库 LIMIT
6. ❌ 排序过程中对象被修改 → ✅ 快照排序或不可变快照

### 一句话终极总结

> **写 Comparator 的最高境界不是会写 `compare` 方法，而是会组合——从最简单的小积木搭出最复杂的排序逻辑。**

---

*这篇文章是 Java 知识体系的一部分。关联阅读：*
- [Java 8 函数式接口完全指南](./java-8-function-complete-guide.md)
- [Java 并发基础](./java-concurrency-fundamentals.md)
- [JVM 内存模型](./java-jvm-memory-model.md)
