# 别再用 Java 8！Java 21 这 8 个特性很强

> **来源：** [Spring Boot 3 实战案例锦集 · 微信公众号](https://mp.weixin.qq.com/s/Tfp9fmDMDuW-g3ovslObaw)  
> **整理 & 增强：** 2026-05-22

---

## 一、背景：为什么是 Java 21？

尽管 Java 8 已发布超过十二年（2014 年 GA），据统计超 70% 的企业项目仍停留在 Java 8。核心原因并非 Java 8 够好，而是**迁移成本认知偏差**——很多团队低估了新版本带来的效率收益，高估了迁移风险。

**关键事实：**
- Java 21（2023.09 GA）是继 Java 17 后的最新 LTS 版本
- Java 25 已于 2025.09 GA，但 21 是当前企业迁移的主流目标（LTS 基线）
- 从 Java 8 到 21，跨越了 13 个版本，引入了数十项重量级特性

**升级收益远大于成本。** 虚拟线程让高并发成本归零、模式匹配简化冗余代码、Record + Sealed Class 重构数据模型，直接让开发效率与代码可维护性飙升。

---

## 二、8 大核心特性详解

### 2.1 Records — 告别 POJO 模板代码

**引入版本：** Java 14（预览）→ Java 16（正式）

Record 是一种专门用于存储不可变数据的特殊类。如果你的类只是为了：存数据、提供 getter、实现 `equals/hashCode/toString`——Record 就是为你量身打造的。

**传统 POJO（冗长且重复）：**

```java
public class User {
    private final String name;
    private final int age;

    public User(String name, int age) {
        this.name = name;
        this.age = age;
    }
    public String getName() { return name; }
    public int getAge() { return age; }
    @Override public boolean equals(Object o) { /* 20+ 行 */ }
    @Override public int hashCode() { /* 10+ 行 */ }
    @Override public String toString() { /* 5+ 行 */ }
}
```

**现代写法（一行）：**

```java
public record User(String name, int age) {}
```

**核心优势：**
- 自动生成 `constructor`、`accessor`、`equals()`、`hashCode()`、`toString()`
- 所有字段默认为 `private final`，天然不可变，线程安全
- 完美适用于 DTO、API 响应、值对象

**Spring Boot 实战：**

```java
// Controller 返回 Record
@RestController
public class UserController {
    @GetMapping("/user/{id}")
    public UserResponse getUser(@PathVariable Long id) {
        return new UserResponse(id, "Pack_xg", "pack@example.com");
    }
}

public record UserResponse(Long id, String name, String email) {}
// Jackson 自动序列化，无需任何注解
```

**增强提示：** 可通过在 Record 内部添加 compact constructor 做校验：

```java
public record User(String name, int age) {
    public User {
        if (age < 0) throw new IllegalArgumentException("Age must be positive");
        if (name == null || name.isBlank()) throw new IllegalArgumentException("Name required");
    }
}
```

---

### 2.2 密封类（Sealed Classes）— 精确控制继承

**引入版本：** Java 15（预览）→ Java 17（正式）

密封类让你精确控制哪些类可以继承或实现某个类型。在此之前，继承只有两种模式：
- 完全开放（`public`）：任何类都能继承
- 笨拙限制（私有构造器）：根本上无法扩展

**典型场景——支付方式类型：**

```java
// 密封接口，明确允许的子类型
public sealed interface IPaymentService permits WeiXinService, AliPayService, BankPayService {}

// 子类必须是 final / sealed / non-sealed
public final class WeiXinService implements IPaymentService {}
public final class AliPayService implements IPaymentService {}
public final class BankPayService implements IPaymentService {}
```

编译期强制约束——如果有人尝试 `class OtherPay implements IPaymentService`，会直接编译报错。这在领域驱动设计（DDD）中配合密封 + pattern matching 能做到**穷举匹配**，编译器帮你检查是否遗漏了某个分支。

**Spring Boot 实战：**

```java
// 策略模式 + 密封类 = 编译器安全的策略分发
public sealed interface PaymentStrategy permits WeChatPay, AliPay, BankPay {
    PayResult pay(PayRequest request);
}

// 结合 Switch 模式匹配使用（见 2.4）
```

---

### 2.3 instanceof 模式匹配 — 一行搞定类型检查+转换

**引入版本：** Java 14（预览）→ Java 16（正式）

**传统写法：**

```java
if (obj instanceof String) {
    String s = (String) obj;
    System.out.println(s.length());
}
```

**现代写法：**

```java
if (obj instanceof String s) {
    System.out.println(s.length());
}
```

变量 `s` 的作用域仅限于 if 块内，且**支持更复杂的条件逻辑**：

```java
// 还可以与条件运算符结合
if (obj instanceof String s && s.length() > 5) {
    System.out.println(s.toUpperCase());
}
```

**Spring Boot 实战：** 在处理多种消息类型时特别有用：

```java
public void handleMessage(Object message) {
    if (message instanceof OrderCreatedEvent e) {
        orderService.process(e);
    } else if (message instanceof PaymentConfirmedEvent e) {
        paymentService.confirm(e);
    } else {
        log.warn("Unknown message type: {}", message.getClass());
    }
}
```

---

### 2.4 Switch 模式匹配 — 最强大的 Switch 进化

**引入版本：** Java 12（预览）→ Java 21（正式，与模式匹配整合）

现代 switch 可以处理：
- **类型匹配**— 直接根据对象类型分发
- **条件表达式**— 无需 break 的箭头语法
- **密封类层次**— 编译器穷举检查

**传统 → 现代对比：**

```java
// 传统 switch（容易遗漏 break，不支持类型模式）
String result;
switch (fruit) {
    case APPLE: result = "Apple"; break;
    case ORANGE: result = "Orange"; break;
    default: result = "Unknown";
}

// 现代 switch（箭头语法，无 fall-through）
String result = switch (fruit) {
    case APPLE -> "Apple";
    case ORANGE -> "Orange";
    default -> "Unknown";
};
```

**类型模式匹配：**

```java
static String processPayment(IPaymentService payment) {
    return switch (payment) {
        case WeiXinService wx -> "微信支付";
        case AliPayService as -> "支付宝支付";
        case BankPayService bps -> "银联支付";
        // 如果 IPaymentService 是密封类，此处不需要 default
        // 编译器强制穷举，遗漏任一子类直接编译报错
    };
}
```

**增强要点：** 用 `yield` 返回值（而非 `break`）：

```java
int result = switch (status) {
    case "SUCCESS" -> 1;
    case "FAILED" -> {
        log.warn("Operation failed");
        yield -1;  // 多行代码用 yield 返回值
    }
    default -> 0;
};
```

---

### 2.5 文本块（Text Blocks）— 告别字符串拼接

**引入版本：** Java 13（预览）→ Java 15（正式）

**传统写法（JSON/HTML/SQL 噩梦）：**

```java
String json = "{\n" +
    "  \"name\": \"Pack_xg\",\n" +
    "  \"title\": \"Spring Boot 3 实战案例 300 讲\"\n" +
    "}";
```

**现代写法：**

```java
String json = """
    {
      "name": "Pack_xg",
      "title": "Spring Boot 3 实战案例 300 讲"
    }
    """;
```

**实用技巧：**
- 起始 `"""` 后的换行被自动忽略
- 尾随空白自动去除（可用 `\s` 保留）
- 可用 `\` 继续行（类似 shell 续行符）

```java
// SQL 查询更清晰
String query = """
    SELECT u.name, o.order_date, o.total
    FROM users u
    JOIN orders o ON u.id = o.user_id
    WHERE u.status = 'ACTIVE'
    ORDER BY o.order_date DESC
    LIMIT 10
    """;
```

---

### 2.6 虚拟线程（Virtual Threads）— 本世纪 Java 最重磅特性

**引入版本：** Java 19（预览）→ Java 21（正式）

虚拟线程是由 JVM 而非操作系统管理的轻量级线程，每个虚拟线程成本约 **1KB**（vs 平台线程约 2MB），单服务器轻松支撑百万级并发。

**传统方案的痛点：**
- **线程池**：受限于 OS 线程数量（通常数千个），高并发需复杂调优
- **响应式框架**：通过回调/Future/Reactive Streams，代码可读性差
- **回调地狱**：嵌套回调导致逻辑碎片化

**虚拟线程示例：**

```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> {
        Thread.sleep(1000);  // 阻塞但不占用 OS 线程
        System.out.println("执行网络IO、数据库查询等耗时操作");
    });
}
```

**更常见的模式——简单替换：**

```java
// 以前
ExecutorService executor = Executors.newFixedThreadPool(200);

// 现在
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
```

原来的代码一行不改，立即获得**无上限的并发能力**。

**Spring Boot 配置：**

```yaml
# application.yaml — Spring Boot 3.2+ 会自动使用虚拟线程
spring:
  threads:
    virtual:
      enabled: true
```

开启后，所有 @Async、TaskExecutor、HTTP 请求处理线程都由虚拟线程承载。

**性能真相：**
- 虚拟线程**不加速计算密集型任务**（CPU 仍是瓶颈）
- 虚拟线程**极大提升 I/O 密集型任务的吞吐**（网络请求、数据库查询、文件读写）
- 搭配结构化并发（2.7）使用，效果更佳

---

### 2.7 结构化并发（Structured Concurrency）— 任务级的编排

**引入版本：** Java 19（孵化）→ Java 21（预览）

结构化并发将多个并行任务视为一个逻辑工作单元。核心思想：**线程的生命周期不应超过创建它的代码块**。

**非结构化写法（传统）：**

```java
ExecutorService es = Executors.newFixedThreadPool(2);
Future<Object> userInfo = es.submit(this::queryUserInfo);
Future<Object> stock = es.submit(this::queryStock);

// 两个 get 分开处理错误——如果一个失败，另一个仍在跑
Object userInfoRet = userInfo.get();
Object stockRet = stock.get();
```

**结构化写法（Java 21）：**

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Future<String> userInfo = scope.fork(this::queryUserInfo);
    Future<String> stock = scope.fork(this::queryStock);

    scope.join();            // 等待所有任务
    scope.throwIfFailed();   // 任一异常，统一抛出

    return new Response(userInfo.resultNow(), stock.resultNow());
}
```

**核心优势：**
- 任一任务失败，自动取消其余任务（避免资源泄漏和悬空线程）
- 统一处理错误，无需分散的异常捕获
- 所有任务在同一个 try 块的生命周期内完成

---

### 2.8 增强的 API — 日常编码的"隐形升级"

这些特性虽小，但每天都能省几行代码：

**Optional.ifPresentOrElse()：**

```java
// 以前
if (user.isPresent()) {
    process(user.get());
} else {
    log.warn("User not found");
}

// 现在
user.ifPresentOrElse(
    this::process,
    () -> log.warn("User not found")
);
```

**Stream.toList()：**（Java 16）

```java
// 以前
List<String> list = stream.collect(Collectors.toList());

// 现在
List<String> list = stream.toList();  // 返回不可变 List
```

**Collectors.teeing()：** 一次遍历做两件事

```java
// 同时求最大值和最小值
var result = numbers.stream().collect(
    Collectors.teeing(
        Collectors.maxBy(Integer::compareTo),
        Collectors.minBy(Integer::compareTo),
        (max, min) -> "Max: " + max.get() + ", Min: " + min.get()
    )
);
```

**清晰的 NPE 消息：**（Java 14+）

```java
// 以前
Exception in thread "main" java.lang.NullPointerException
    at com.example.Main.main(Main.java:5)

// 现在
Exception in thread "main" java.lang.NullPointerException: 
    Cannot invoke "String.length()" because "user.name" is null
```

**List.of() / Map.of() / Set.of()：**（Java 9+）

```java
// 创建不可变集合——线程安全、防篡改
List<String> roles = List.of("ADMIN", "USER", "VIEWER");
Map<String, Integer> config = Map.of(
    "timeout", 5000,
    "retries", 3
);
// 尝试 add/put 会抛出 UnsupportedOperationException
```

---

## 三、迁移指南（Java 8 → 21）

### 3.1 依赖兼容性清单

升级前检查以下依赖是否支持 Java 21：

| 组件 | 最低版本要求 | 备注 |
|------|-------------|------|
| Spring Boot | 3.0+（推荐 3.2+） | 3.0 开始基础 Java 17 |
| Spring Cloud | 2022.0.x+ | 配合 Spring Boot 3.x |
| Hibernate | 6.1+ | 6.0 基础 Java 11+ |
| MyBatis | 3.5.x | 兼容性较好 |
| Tomcat | 10.x | Spring Boot 内嵌 |
| Maven | 3.6+ | 推荐 3.9+ |
| Gradle | 7.5+ | 推荐 8.x |
| Lombok | 1.18.30+ | 需更新以兼容 Record |
| Jackson | 2.15+ | Record 序列化支持 |
| Mockito | 5.x | 测试框架 |
| JUnit | 5.10+ | |

### 3.2 模块系统注意事项

如果项目使用 Java 9+ 模块系统（module-info.java），注意：
- 反射访问内部 API 会失败（`--add-opens` 可临时绕过）
- `sun.misc.Unsafe` 部分功能受限
- 推荐使用 `java.lang.foreign.MemorySegment` 替代

### 3.3 逐步升级策略

```
步骤 1：Java 8 → 11
  - 添加 java.se.ee 模块（如有 CORBA/JAXB 依赖）
  - 替换 Nashorn 引擎
  - 测试所有第三方库兼容性

步骤 2：Java 11 → 17
  - 启用 sealed class、record、pattern matching 预览特性（可选）
  - 移除 --illegal-access 参数
  - 替换被移除的 API（如 Applet、安全管理器）

步骤 3：Java 17 → 21
  - 启用虚拟线程（预览 → 正式）
  - 使用 Record 重构 DTO
  - 使用 Switch 模式匹配替代老旧 switch
  - 享受结构化并发
```

### 3.4 Maven 配置

```xml
<properties>
    <maven.compiler.source>21</maven.compiler.source>
    <maven.compiler.target>21</maven.compiler.target>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
</properties>
```

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <configuration>
        <source>21</source>
        <target>21</target>
        <release>21</release>
        <compilerArgs>
            <arg>--enable-preview</arg>  <!-- 如使用预览特性 -->
        </compilerArgs>
    </configuration>
</plugin>
```

---

## 四、最佳实践与注意事项

### 4.1 什么场景应该优先使用

| 特性 | 最佳使用场景 | 优先级 |
|------|-------------|--------|
| 虚拟线程 | I/O 密集型服务（API、网关、数据管道） | ⭐⭐⭐⭐⭐ |
| Record | DTO、请求/响应对象、配置对象 | ⭐⭐⭐⭐⭐ |
| Switch 模式匹配 | 策略分发、状态机、类型判断 | ⭐⭐⭐⭐ |
| 密封类 | 领域模型、有限状态类型 | ⭐⭐⭐ |
| 文本块 | SQL、JSON、HTML、XML 字面量 | ⭐⭐⭐ |
| 结构化并发 | 并行数据获取、扇出查询 | ⭐⭐⭐ |
| 增强 API | 日常编码质量改进 | ⭐⭐ |

### 4.2 常见陷阱

- **虚拟线程不适用计算密集型任务** — 用平台线程池处理 CPU 密集操作
- **Record 不是 JPA 实体** — Hibernate/JPA 需要可变实体，Record 不可变
- **密封类增加模块耦合** — 子类需与密封类在同一模块或同一包（Java 17 规则）
- **模式匹配 + null** — `switch (null)` 会抛 NPE，需前置 null-check
- **文本块缩进处理** — 缩进由结束 `"""` 位置决定，容易搞错

### 4.3 推荐阅读

- [Java 8 到 21 的主要新特性及示例代码](https://www.cnblogs.com/little-lunatic/p/18712787)
- [一口气读完 Java 8 ~ Java 21 所有新特性](https://zhuanlan.zhihu.com/p/673938152)
- [JDK 8 钉子户进阶指南：Java 21 升级盛宴](https://juejin.cn/post/7559216817463361571)
- JEP 441: Pattern Matching for Switch
- JEP 444: Virtual Threads (正式化)
- JEP 453: Structured Concurrency (预览)

---

*整理自微信公众号「Spring Boot 实战案例锦集」文章，结合官方 JEP 文档及工程实践拓展补充*
