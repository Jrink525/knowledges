# Spring Boot 日志从入门到精通 —— SLF4J/Logback 配置、实战与最佳实践

> **来源**：Vlad Mihalcea《Log SQL with Spring Boot》、Spring Boot Official Docs、katyella.com《Spring Boot Logging Best Practices》、last9.io《Guide to Spring Boot Logging》以及网络搜索补充
> **整理**：Jarvis II
> **目标读者**：有 Spring Boot 基础的开发者，从零搭建生产级日志体系

---

# 前言：为什么日志是第一公民？

凌晨 3 点，支付失败告警响起。你的第一反应是什么？

> "看日志。"

一个好的日志体系，能让 5 分钟的排查变成 5 秒。坏的日志，让你在一堆无意义的 text 里 grep 到天亮。

日志不是 afterthought——它是你的"飞行记录仪"。这篇文章从 **Hello World 级别的入门案例** 讲起，一路深入到 **生产级结构化 JSON 日志、MDC 全链路追踪、AsyncAppender 性能优化、Actuator 动态调级别**，力求一篇读懂 Spring Boot 日志全貌。

---

# 第一章：日志基础 —— SLF4J 与 Logback 是什么

## 1.1 先搞清楚几个概念

在你的 Spring Boot 项目里，打印一行日志只需要：

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Service
public class OrderService {
    private static final Logger log = LoggerFactory.getLogger(OrderService.class);

    public void createOrder(String orderId) {
        log.info("Creating order: {}", orderId);
    }
}
```

这里你接触到了两个重要的东西：

| 概念 | 角色 | 类比 |
|------|------|------|
| **SLF4J** (Simple Logging Facade for Java) | **API 接口**：定义 Logger、LoggerFactory 等接口 | 充电口的 USB 标准 |
| **Logback** | **接口实现**：真正写日志的代码 | 充电头本身 |
| **Log4j2** | 另一个实现（可选） | 另一个品牌的充电头 |

**关键理解**：你的代码只依赖 SLF4J 接口。底层用 Logback 还是 Log4j2，改一行依赖配置就行，代码不用改。

> SLF4J 的设计哲学：**面向接口编程**。运行时，由 classpath 上的具体实现决定日志去哪、格式什么样。

## 1.2 依赖从哪里来

当你引入 `spring-boot-starter` 时，**它会传递引入** `spring-boot-starter-logging`。这个 starter 包含：

- `slf4j-api` — SLF4J 接口
- `logback-classic` — Logback 实现
- `log4j-to-slf4j` — 把 Log4j 的调用桥接到 SLF4J
- `jul-to-slf4j` — 把 Java Util Logging 桥接到 SLF4J
- `jcl-over-slf4j` — 把 Apache Commons Logging 桥接到 SLF4J

> 这意味着项目中所有依赖（Hibernate 用 JBoss Logging、Spring 用 JCL、某些库用 Log4j）最终都会**统一输出**到 Logback。**你只需要管理一个日志框架。**

## 1.3 五个日志级别

| 级别 | 何时使用 | 生产环境建议 |
|------|---------|-------------|
| **ERROR** | 系统无法继续，需要立即介入 | ✅ 需要告警 |
| **WARN** | 发生了意外但自动恢复（如重试成功） | ✅ 需要监控 |
| **INFO** | 正常业务事件（订单创建、启动完成） | ✅ 默认级 |
| **DEBUG** | 诊断信息，开发调试用 | ❌ 不要全局开启 |
| **TRACE** | 极详细日志，wire-level data | ❌ 只在极小范围使用 |

**黄金法则**：

1. `log.info("Order: " + orderId)` ❌ — 字符串拼接不管是否开启都执行
2. `log.info("Order: {}", orderId)` ✅ — `{}` 占位符，级别不够时不格式化

> DEBUG 在热点路径里每秒可能产生几千行。即使被过滤掉，字符串参数构造的开销也肉眼可见。**始终使用 `{}` 占位符。**

---

# 第二章：快速上手 —— Spring Boot 默认日志

创建一个全新的 Spring Boot 项目，什么配置都不用做，启动时就能看到：

```
2024-12-04 10:23:45.123  INFO 12345 --- [main] c.e.Application        : Starting Application
```

这个格式包含：

| 部分 | 含义 |
|------|------|
| `2024-12-04 10:23:45.123` | 时间戳 |
| `INFO` | 日志级别（左对齐 5 字符宽） |
| `12345` | 进程 PID |
| `---` | 分隔符 |
| `[main]` | 线程名 |
| `c.e.Application` | Logger 名（缩写） |
| `Starting Application` | 日志消息 |

Spring Boot 默认行为：
- 只输出到 **console**
- 默认级别：**root → INFO**（DEBUG 和 TRACE 被过滤）
- 没有文件输出
- 在 `application.properties` 中即可做大部分配置

---

# 第三章：入门配置 —— application.properties / YAML

绝大多数场景，你不需要写 XML，Spring Boot 的 properties 配置就够了：

## 3.1 设置日志级别

```properties
# root 级别（影响所有未特别配置的包）
logging.level.root=WARN

# 你自己的包
logging.level.com.yourcompany=INFO

# 第三方库
logging.level.org.springframework.web=DEBUG
logging.level.org.springframework.security=WARN
logging.level.org.hibernate.SQL=DEBUG
```

YAML 版本：

```yaml
logging:
  level:
    root: WARN
    com.yourcompany: INFO
    org.springframework.web: DEBUG
    org.hibernate.SQL: WARN
```

> 推荐的生产基线：root=WARN，自己包=INFO。这样抑制框架噪音，同时保留业务日志可见。

## 3.2 输出到文件

```properties
# 文件路径
logging.file.name=logs/myapp.log
# 或 logging.file.path=/var/logs/（只指定目录，文件名自动为 spring.log）
```

配合 Spring Boot 的默认轮转策略（**缺省是 10MB 大小轮转**），这样配置就能自动生成滚动文件。

Spring Boot 3.x 还支持在 properties 中配置日志轮转：

```properties
logging.logback.rollingpolicy.max-file-size=100MB
logging.logback.rollingpolicy.max-history=30
logging.logback.rollingpolicy.total-size-cap=3GB
logging.logback.rollingpolicy.file-name-pattern=${LOG_FILE}.%d{yyyy-MM-dd}.%i.gz
```

## 3.3 自定义日志格式

```properties
logging.pattern.console=%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n
logging.pattern.file=%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n
logging.pattern.dateformat=yyyy-MM-dd HH:mm:ss.SSS
```

## 3.4 日志分组

Spring Boot 支持用 logging.group 把多个包归为一组：

```properties
logging.group.tomcat=org.apache.catalina, org.apache.coyote, org.apache.tomcat
logging.level.tomcat=WARN

logging.group.sql=org.hibernate.SQL, org.springframework.jdbc
logging.level.sql=DEBUG
```

## 3.5 按 Profile 配置

```yaml
# application-dev.yml
logging:
  level:
    root: INFO
    com.yourcompany: DEBUG

---
# application-prod.yml
logging:
  level:
    root: WARN
    com.yourcompany: INFO
```

**properties 的好处**：简单场景不需要 XML，一行搞定。**局限**：无法细粒度控制 appender、encoder、filter 等。

---

# 第四章：进阶 —— logback-spring.xml 配置

当 properties 无法满足时（比如不同 profile 不同 appender、JSON 格式化、异步日志），你需要写 XML。

## 4.1 logback.xml vs logback-spring.xml

| 文件名 | 特点 |
|--------|------|
| `logback.xml` | Logback 原生配置，Spring Boot 自动加载 |
| **`logback-spring.xml`** | **推荐！** 支持 Spring 扩展标签：`<springProfile>`、`<springProperty>` |
| `logback-spring.groovy` | Groovy DSL，不常用 |

> **规则**：文件名带 `-spring` 后缀，才能使用 `<springProfile>` 和 `<springProperty>`。

放到 `src/main/resources/` 即可，Spring Boot 会自动加载。

## 4.2 XML 核心组件

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <!-- 可以先用 Spring Boot 提供的默认配置 -->
    <include resource="org/springframework/boot/logging/logback/defaults.xml"/>

    <!-- 从 application.properties 读取 spring.application.name -->
    <springProperty scope="context" name="APP_NAME" source="spring.application.name" defaultValue="app"/>

    <!-- ====== Appender 1: Console ====== -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
            <charset>UTF-8</charset>
        </encoder>
    </appender>

    <!-- ====== Appender 2: Rolling File ====== -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/${APP_NAME}.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <fileNamePattern>logs/${APP_NAME}-%d{yyyy-MM-dd}.%i.log.gz</fileNamePattern>
            <maxFileSize>100MB</maxFileSize>
            <maxHistory>30</maxHistory>
            <totalSizeCap>3GB</totalSizeCap>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>

    <!-- ====== Root Logger ====== -->
    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="FILE"/>
    </root>
</configuration>
```

## 4.3 用 springProfile 区分环境

```xml
<!-- 开发环境：console + DEBUG -->
<springProfile name="dev,local">
    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
    </root>
    <logger name="com.yourcompany" level="DEBUG"/>
</springProfile>

<!-- 生产环境：file + INFO -->
<springProfile name="prod,staging">
    <root level="WARN">
        <appender-ref ref="FILE"/>
    </root>
    <logger name="com.yourcompany" level="INFO"/>
</springProfile>
```

> 核心思想：**用 `spring.profiles.active` 驱动日志行为**，一份配置文件管所有环境。

## 4.4 常用 pattern 转换符参考

| 占位符 | 含义 | 示例 |
|--------|------|------|
| `%d` | 日期 | `2024-12-04 10:23:45.123` |
| `%thread` | 线程名 | `http-nio-8080-exec-3` |
| `%-5level` | 级别（左对齐5宽） | `INFO ` |
| `%logger{36}` | Logger 名（缩写） | `c.y.OrderService` |
| `%msg` | 日志消息 | `Creating order 123` |
| `%n` | 换行 | |
| `%X{traceId}` | MDC 中的 key | `abc123` |
| `%replace(%msg){'password=\w+', 'password=***'}` | 正则脱敏 | 敏感信息屏蔽 |

---

# 第五章：SLF4J 最佳实践 —— 日常开发必知

## 5.1 声明 Logger 的正确方式

```java
// 方式1：标准写法
private static final Logger log = LoggerFactory.getLogger(OrderService.class);

// 方式2：Lombok（零样板代码）
@Slf4j
@Service
public class OrderService {
    public void process(String id) {
        log.info("Processing {}", id);  // 直接用 log 变量
    }
}
```

## 5.2 占位符 vs 字符串拼接

```java
// ❌ 差 —— 每次拼接字符串，即使不输出
log.debug("User: " + user.getName() + " ordered " + amount);

// ✅ 好 —— 不输出时不构造字符串
log.debug("User: {} ordered {}", user::getName, () -> amount);

// ✅ 最好 —— Lambda 延迟求值（SLF4J 2.0+）
log.atDebug()
   .addKeyValue("userId", user.getId())
   .log("Processing order");
```

## 5.3 异常日志的正确姿势

```java
// ❌ 丢失堆栈
log.error("Payment failed: " + e.getMessage());

// ✅ 包括完整 stack trace（SLF4J 约定：最后一个 Throwable 参数自动处理）
log.error("Payment failed for order {}", orderId, e);
```

> SLF4J 规则：如果最后一个参数是 `Throwable`，自动输出堆栈。**永远不要把异常塞进消息字符串里。**

## 5.4 条件日志（避免不必要的方法调用）

```java
// ❌ 即使 DEBUG 没开，expensiveCalculation() 也会执行
log.debug("Result: {}", expensiveCalculation());

// ✅ 先检查级别
if (log.isDebugEnabled()) {
    log.debug("Result: {}", expensiveCalculation());
}

// ✅ SLF4J 2.0 的 Fluent API 自动延迟求值
log.atDebug()
   .setMessage("Result: {}")
   .addArgument(this::expensiveCalculation)
   .log();
```

---

# 第六章：SQL 日志 —— 从 show-sql 到 DataSource-Proxy

> 本章核心来源：[Vlad Mihalcea《The best way to log SQL statements with Spring Boot》](https://vladmihalcea.com/log-sql-spring-boot/)

## 6.1 新手做法：spring.jpa.show-sql=true

```properties
spring.jpa.show-sql=true
```

**为什么不要用？** 这个配置本质是调用 `System.out.println()` —— 和你在代码里写 `System.out.println` 没有区别。**无法**：
- 控制日志级别
- 输出到文件
- 格式化
- 实现 JDBC batch 清晰可见

## 6.2 中级做法：Hibernate 日志

```properties
logging.level.org.hibernate.SQL=DEBUG
# Hibernate 6
logging.level.org.hibernate.orm.jdbc.bind=TRACE
# Hibernate 5
logging.level.org.hibernate.type.descriptor.sql=TRACE
```

输出示例：

```
org.hibernate.SQL :
    SELECT u.id, u.email, u.first_name
    FROM users u
    WHERE u.email = ?

o.h.t.d.sql.BasicBinder :
    binding parameter [1] as [VARCHAR] - [john@acme.com]
```

**局限**：
- 参数绑定和 SQL 语句分开输出，不易对应
- Batch 场景下，无法确认多少条语句实际发送到数据库
- 只支持 Hibernate Core Types，不支持 Hibernate Types 扩展项目

## 6.3 高级做法：DataSource-Proxy（推荐）

```xml
<dependency>
    <groupId>com.github.gavlyukovskiy</groupId>
    <artifactId>datasource-proxy-spring-boot-starter</artifactId>
    <version>1.9.2</version>
</dependency>
```

```properties
logging.level.net.ttddyy.dsproxy.listener=DEBUG
```

输出示例：

```
Name:dataSource, Connection:5, Time:1, Success:True
Type:Prepared, Batch:False, QuerySize:1, BatchSize:0
Query:["
    SELECT u.id, u.email, u.first_name
    FROM users u
    WHERE u.email = ?
"]
Params:[(
    john@acme.com
)]
```

**优势**：
- SQL 和参数在一起，一目了然
- **Batch 语句也能清晰看到**（BatchSize 显示实际合并数）
- 兼容 JPA + jOOQ 混用场景
- 可以**在单元测试中 assert SQL 数量**，自动检测 N+1 问题

> **[进阶]** 在测试中检测 N+1：
> ```java
> // 配置 DataSource-Proxy 的 CountQuery 监听器
> // 如果一条请求产生的查询超过了预期，自动 fail 测试
> ```

---

# 第七章：结构化 JSON 日志 —— 生产环境的必备技能

人类阅读 `[%thread] %-5level %logger{36}` 很方便。但 ELK / Splunk / Datadog 更喜欢 JSON。

## 7.1 方式一：logstash-logback-encoder（最常用）

```xml
<dependency>
    <groupId>net.logstash.logback</groupId>
    <artifactId>logstash-logback-encoder</artifactId>
    <version>7.4</version>
</dependency>
```

```xml
<springProfile name="prod">
    <appender name="JSON_CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
            <includeCallerData>false</includeCallerData>
            <customFields>{"service":"${APP_NAME}","environment":"${SPRING_PROFILES_ACTIVE}"}</customFields>
            <!-- MDC 中哪些 key 包含到 JSON -->
            <includeMdcKeyName>traceId</includeMdcKeyName>
            <includeMdcKeyName>userId</includeMdcKeyName>
            <includeMdcKeyName>requestId</includeMdcKeyName>
        </encoder>
    </appender>

    <root level="WARN">
        <appender-ref ref="JSON_CONSOLE"/>
    </root>
    <logger name="com.yourcompany" level="INFO"/>
</springProfile>
```

输出示例：

```json
{
    "@timestamp": "2024-12-04T10:23:45.451Z",
    "level": "INFO",
    "logger_name": "com.yourcompany.OrderService",
    "message": "Processing order ORD-9821",
    "service": "order-service",
    "environment": "prod",
    "traceId": "4bf92f3577b34da6",
    "userId": "usr-123"
}
```

> **现在你可以在 Kibana 中 `traceId: 4bf92f35` 一键过滤出该请求的所有日志。** 跨服务链路追踪从此不再是噩梦。

## 7.2 方式二：Spring Boot 3.4+ 原生结构化日志

从 Spring Boot 3.4 开始，**不再需要 logstash 依赖**，内置三种 JSON 格式：

```yaml
logging:
  structured:
    format:
      console: logstash   # 或 ecs / gelf
      # file: logstash
```

支持的三种格式：
- **logstash** — Logstash 兼容格式（`@timestamp`, `@version`, `logger_name` 等）
- **ecs** — Elastic Common Schema（与 Elastic Stack 完美集成）
- **gelf** — Graylog Extended Log Format

自定义 JSON 字段：

```yaml
logging:
  structured:
    json:
      exclude: log.level          # 移除某字段
      rename:
        process.id: procid        # 重命名字段
      add:
        corpname: mycorp          # 添加固定字段
      stacktrace:
        root: first
        max-length: 1024
```

也可以通过 Java 接口 `StructuredLogFormatter<ILoggingEvent>` 实现完全自定义格式：

```java
class MyCustomFormat implements StructuredLogFormatter<ILoggingEvent> {
    @Override
    public String format(ILoggingEvent event) {
        return "time=" + event.getInstant()
             + " level=" + event.getLevel()
             + " message=" + event.getMessage() + "\n";
    }
}
```

```yaml
logging.structured.format.console=com.example.MyCustomFormat
```

> **选择建议**：
> - 使用 Spring Boot 3.4+：优先用原生 structured logging，零依赖
> - 使用 Spring Boot < 3.4：使用 logstash-logback-encoder
> - 容器化部署（K8s）：JSON → Console → 由容器运行时收集
> - 裸机 / VM：JSON → File → Filebeat/Fluentd 转发

---

# 第八章：MDC —— 全链路请求追踪

## 8.1 什么是 MDC

**MDC (Mapped Diagnostic Context)** 是 SLF4J 的**线程本地 Map**。你在 MDC 中放入 key-value，**这个线程后续所有日志都会自动包含该值**。

```java
MDC.put("traceId", "abc123");
log.info("Creating order");  // JSON 输出自动包含 "traceId": "abc123"
MDC.clear();
```

## 8.2 Filter 自动注入 Trace ID

```java
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class TraceIdFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain)
            throws ServletException, IOException {

        // 优先接受上游传来的 trace ID（API Gateway 传入的 X-Trace-Id）
        String traceId = request.getHeader("X-Trace-Id");
        if (traceId == null || traceId.isBlank()) {
            traceId = UUID.randomUUID().toString().replace("-", "").substring(0, 16);
        }

        MDC.put("traceId", traceId);
        MDC.put("method", request.getMethod());
        MDC.put("path", request.getRequestURI());

        long start = System.currentTimeMillis();
        try {
            chain.doFilter(request, response);
        } finally {
            long duration = System.currentTimeMillis() - start;
            MDC.put("status", String.valueOf(response.getStatus()));
            MDC.put("duration", String.valueOf(duration));
            log.info("Request completed in {}ms", duration);
            MDC.clear();  // 必须！线程池复用会导致 MDC 泄露
        }
    }
}
```

## 8.3 日志配置包含 MDC

```xml
<!-- 普通版 -->
<pattern>%d [%X{traceId}] [%X{userId}] %-5level %logger - %msg%n</pattern>

<!-- JSON 版（自动包含）已通过 includeMdcKeyName 配置 -->
```

## 8.4 在 logback-spring.xml 中使用 MDC

```xml
<encoder>
    <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%X{traceId:-no-trace}] %-5level %logger{36} - %msg%n</pattern>
</encoder>
```

> **`[%X{traceId:-no-trace}]`**：显示 MDC 中 traceId 的值，如果不存在则显示 "no-trace"。

## 8.5 异步线程如何传递 MDC

```java
// 捕获当前线程的 MDC
Map<String, String> contextMap = MDC.getCopyOfContextMap();

executor.submit(() -> {
    try {
        if (contextMap != null) {
            MDC.setContextMap(contextMap);  // 传递给异步线程
        }
        // ... 执行业务
    } finally {
        MDC.clear();  // 防止线程池复用泄露
    }
});
```

## 8.6 Spring Boot 3.2+ Virtual Threads 兼容性

SLF4J 2.0 + Logback 1.4+ 已正确支持 Virtual Thread 的 MDC。即使 `spring.threads.virtual.enabled=true`，MDC 也能正常工作。

---

# 第九章：AOP 切面日志

## 9.1 为什么要用 AOP

手写 `log.info("Entering method xxx")` 又丑又容易遗漏。AOP 让你**自动拦截包下的所有方法**，无需侵入业务代码。

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-aop</artifactId>
</dependency>
```

## 9.2 一个通用的日志切面

```java
@Aspect
@Component
public class LoggingAspect {

    private static final Logger log = LoggerFactory.getLogger(LoggingAspect.class);

    // 拦截 service 包下的所有方法
    @Before("execution(* com.yourcompany.service.*.*(..))")
    public void logBefore(JoinPoint jp) {
        log.info("→ {}.{}() args={}",
            jp.getTarget().getClass().getSimpleName(),
            jp.getSignature().getName(),
            jp.getArgs());
    }

    @AfterReturning(pointcut = "execution(* com.yourcompany.service.*.*(..))", returning = "result")
    public void logAfter(JoinPoint jp, Object result) {
        log.info("← {}.{}() returned={}",
            jp.getTarget().getClass().getSimpleName(),
            jp.getSignature().getName(),
            result);
    }

    @AfterThrowing(pointcut = "execution(* com.yourcompany.service.*.*(..))", throwing = "ex")
    public void logError(JoinPoint jp, Throwable ex) {
        log.error("✗ {}.{}() exception: {}",
            jp.getTarget().getClass().getSimpleName(),
            jp.getSignature().getName(),
            ex.getMessage(), ex);
    }
}
```

## 9.3 带性能监控的 AOP

```java
@Around("execution(* com.yourcompany.service.*.*(..))")
public Object logExecutionTime(ProceedingJoinPoint jp) throws Throwable {
    long start = System.nanoTime();
    try {
        return jp.proceed();
    } finally {
        long ms = TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - start);
        if (ms > 1000) {  // 超过 1 秒的慢调用
            log.warn("Slow operation: {}.{}() took {}ms",
                jp.getTarget().getClass().getSimpleName(),
                jp.getSignature().getName(), ms);
        }
    }
}
```

> **使用建议**：AOP 适合 service 层的统一日志。Controller 层的 request/response 日志用 Interceptor + Filter 更合适（详见第十章）。

---

# 第十章：HTTP 请求/响应日志

## 10.1 HandlerInterceptor 方式

```java
@Component
public class RequestLoggingInterceptor implements HandlerInterceptor {

    private static final Logger log = LoggerFactory.getLogger(RequestLoggingInterceptor.class);

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        MDC.put("requestURI", request.getRequestURI());
        MDC.put("method", request.getMethod());
        MDC.put("startTime", String.valueOf(System.currentTimeMillis()));
        return true;
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response,
                                 Object handler, Exception ex) {
        long duration = System.currentTimeMillis() - Long.parseLong(MDC.get("startTime"));
        log.info("{} {} → {} ({}ms)",
            MDC.get("method"), MDC.get("requestURI"),
            response.getStatus(), duration);
        MDC.clear();
    }
}
```

注册：

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new RequestLoggingInterceptor()).addPathPatterns("/**");
    }
}
```

## 10.2 Spring Boot 内置 ContentCachingRequestWrapper

Spring Boot 提供了 `AbstractRequestLoggingFilter`，一行配置就能记录 request：

```properties
spring.http.log-request-details=true
```

但想记录 response body 需要自己写 Filter + Wrapper。

---

# 第十一章：异步日志 —— AsyncAppender

## 11.1 为什么要异步

同步日志写磁盘：
- 每次 I/O 操作 3-5ms
- 高并发下，日志写入成为瓶颈

异步日志：放入内存队列，后台线程批量写入 → < 1ms 返回。

## 11.2 配置 AsyncAppender

```xml
<appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
    <!-- ... 同前 ... -->
</appender>

<appender name="ASYNC_FILE" class="ch.qos.logback.classic.AsyncAppender">
    <queueSize>1024</queueSize>          <!-- 队列容量 -->
    <discardingThreshold>20</discardingThreshold>  <!-- 队列80%满时丢弃TRACE/DEBUG/INFO -->
    <neverBlock>false</neverBlock>        <!-- true=队列满时丢弃而非阻塞 -->
    <includeCallerData>false</includeCallerData>  <!-- 生产环境关掉 -->
    <appender-ref ref="FILE"/>
</appender>

<root level="INFO">
    <appender-ref ref="ASYNC_FILE"/>
</root>
```

**参数详解**：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `queueSize` | 256 | 阻塞队列容量 |
| `discardingThreshold` | 20 | 队列容量剩余百分比，低于此值丢弃低级日志（WARN/ERROR 不丢弃） |
| `neverBlock` | false | 队列满时，false=阻塞等待，true=丢弃 |
| `includeCallerData` | false | 是否包含调用者行号信息（获取行号涉及 stack trace，很贵） |

> **生产建议**：`discardingThreshold=20`，队列满时丢弃 DEBUG/INFO 但保留 WARN/ERROR。**你在意的是告警，不是流量高峰时的 debug 信息。**

## 11.3 性能对比

| 指标 | 同步 | 异步 |
|------|------|------|
| 单次日志延迟 | ~3-5ms | < 1ms |
| 高并发吞吐 | 随 I/O 压力下降 | 接近无影响 |
| 宕机时日志丢失 | 无 | 队列中未刷新的可能丢失 |

---

# 第十二章：Actuator —— 运行时动态调整日志级别

## 12.1 启用 Actuator Loggers Endpoint

```yaml
management:
  endpoints:
    web:
      exposure:
        include: loggers
  endpoint:
    loggers:
      enabled: true
```

## 12.2 查询和修改

```bash
# 查询当前级别
curl http://localhost:8080/actuator/loggers/com.yourcompany.OrderService
# → {"configuredLevel":"INFO","effectiveLevel":"INFO"}

# 临时改为 DEBUG（不用重启！）
curl -X POST http://localhost:8080/actuator/loggers/com.yourcompany.OrderService \
  -H 'Content-Type: application/json' \
  -d '{"configuredLevel":"DEBUG"}'

# 重置为默认
curl -X POST http://localhost:8080/actuator/loggers/com.yourcompany.OrderService \
  -H 'Content-Type: application/json' \
  -d '{"configuredLevel":null}'

# 查看所有 logger 层级
curl http://localhost:8080/actuator/loggers | jq '.levels'
```

> **这是排查生产问题的神器**：发现问题 → 单独对某个包开启 DEBUG → 捕获日志 → 改回 INFO。全程零重启。

## 12.3 安全提醒

生产环境这个端点需要认证，否则攻击者可开启 DEBUG 日志耗尽磁盘。

```yaml
spring:
  security:
    user:
      name: admin
      password: ${ACTUATOR_PASSWORD}
```

---

# 第十三章：全局异常处理的日志

## 13.1 @ControllerAdvice + 统一日志

```java
@ControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(ResourceNotFoundException ex) {
        log.warn("Resource not found: {}", ex.getMessage());
        return ResponseEntity.status(404).body(new ErrorResponse("NOT_FOUND", ex.getMessage()));
    }

    @ExceptionHandler(InvalidInputException.class)
    public ResponseEntity<ErrorResponse> handleInvalidInput(InvalidInputException ex) {
        log.warn("Invalid input: {}", ex.getMessage());
        return ResponseEntity.status(400).body(new ErrorResponse("BAD_REQUEST", ex.getMessage()));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleUnexpected(Exception ex, HttpServletRequest request) {
        log.error("Unexpected error on {} {}: {}",
            request.getMethod(), request.getRequestURI(), ex.getMessage(), ex);
        return ResponseEntity.status(500).body(new ErrorResponse("INTERNAL_ERROR", "请稍后重试"));
    }
}
```

**关键原则**：
- `ResourceNotFoundException` → `log.warn`（预期行为，不用告警）
- `Exception` → `log.error` + **完整 stack trace**（需要告警）
- 永远不要在 catch 里**吃了异常又不打印日志**

---

# 第十四章：敏感信息脱敏

## 14.1 自定义 Logback Filter

```java
public class SensitiveDataFilter extends ch.qos.logback.core.filter.Filter<ILoggingEvent> {
    private static final Pattern SENSITIVE_PATTERN =
        Pattern.compile("(password|token|secret|authorization)=[^&\\s,}]+",
            Pattern.CASE_INSENSITIVE);

    @Override
    public FilterReply decide(ILoggingEvent event) {
        String formatted = event.getFormattedMessage();
        if (SENSITIVE_PATTERN.matcher(formatted).find()) {
            return FilterReply.DENY;
        }
        return FilterReply.NEUTRAL;
    }
}
```

```xml
<appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
    <filter class="com.yourcompany.filter.SensitiveDataFilter"/>
    <encoder>...</encoder>
</appender>
```

## 14.2 Properties 级别的 Logging Pattern 脱敏

```properties
logging.pattern.console=%replace(%msg){'password=\w+', 'password=***'}
```

> **团队纪律**：Code review 时检查每个 log 语句——如果包含用户对象，确认哪些字段被记录了。绝对不要把密码、token、信用卡号写入日志。

---

# 第十五章：Per-Appender 日志级别分离

> **来源**：[Baeldung《Different Log Level for File and Console Appender》](https://www.baeldung.com/spring-boot-different-log-level-file-console-appender)

## 15.1 场景

很多团队希望：
- **Console**（开发看）只显示 INFO 及以上（清爽）
- **File**（留存排查）记录 DEBUG 及以上（详细）

Spring Boot 的 `logging.level.*` 控制的是**全局日志级别**，无法按 appender 分别设置。解决方案是 Logback 的 **ThresholdFilter**。

## 15.2 ThresholdFilter 工作原理

`ThresholdFilter` 是一个简单过滤器——它允许**等于或高于**设定级别的日志通过，低于的丢弃。

```xml
<filter class="ch.qos.logback.classic.filter.ThresholdFilter">
    <level>INFO</level>  <!-- 低于 INFO 的 TRACE/DEBUG 被丢弃 -->
</filter>
```

> 关键理解：Root logger 的 `level="DEBUG"` 决定了**所有级别**的日志都到达 appender，但每个 appender 的 ThresholdFilter 独立决定哪些级别的日志被**输出**。

## 15.3 完整配置示例

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <property name="LOGS" value="./logs"/>
    <property name="CONSOLE_PATTERN" value="%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n"/>
    <property name="FILE_PATTERN" value="%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n"/>

    <!-- Console：只显示 INFO 及以上 -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>${CONSOLE_PATTERN}</pattern>
        </encoder>
        <filter class="ch.qos.logback.classic.filter.ThresholdFilter">
            <level>INFO</level>
        </filter>
    </appender>

    <!-- File：记录 DEBUG 及以上 -->
    <appender name="FILE" class="ch.qos.logback.core.FileAppender">
        <file>${LOGS}/my-app.log</file>
        <encoder>
            <pattern>${FILE_PATTERN}</pattern>
        </encoder>
        <filter class="ch.qos.logback.classic.filter.ThresholdFilter">
            <level>DEBUG</level>
        </filter>
    </appender>

    <!-- Root 设为 DEBUG，让所有级别都能到达 appender -->
    <root level="DEBUG">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="FILE"/>
    </root>
</configuration>
```

**运行效果**：

Controller 日志：
```
  TRACE This is a TRACE message    → console ❌   file ❌
  DEBUG This is a DEBUG message    → console ❌   file ✅
  INFO  This is an INFO message    → console ✅   file ✅
  WARN  This is a WARN message     → console ✅   file ✅
  ERROR This is an ERROR message   → console ✅   file ✅
```

## 15.4 结合 RollingFileAppender

```xml
<appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
    <file>${LOGS}/my-app.log</file>
    <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
        <fileNamePattern>${LOGS}/my-app-%d{yyyy-MM-dd}.%i.log.gz</fileNamePattern>
        <maxFileSize>100MB</maxFileSize>
        <maxHistory>30</maxHistory>
        <totalSizeCap>3GB</totalSizeCap>
    </rollingPolicy>
    <encoder>
        <pattern>${FILE_PATTERN}</pattern>
    </encoder>
    <filter class="ch.qos.logback.classic.filter.ThresholdFilter">
        <level>DEBUG</level>
    </filter>
</appender>
```

> **生产建议**：Console 用 `ThresholdFilter` 设到 INFO/WARN，减少噪音；File 设到 DEBUG 保留完整诊断信息。

---

# 第十六章：调试技巧——打印配置属性

> **来源**：[Baeldung《Log Properties in a Spring Boot Application》](https://www.baeldung.com/spring-boot-log-properties)

有时候你想确认应用程序启动时到底加载了哪些配置——`@Value` 是否生效、`application.properties` 是否被正确读取。

## 16.1 方式一：@PostConstruct + Environment（最简单）

```java
@Component
public class ConfigLogger {

    private static final Logger log = LoggerFactory.getLogger(ConfigLogger.class);

    @Autowired
    private Environment env;

    @PostConstruct
    public void logKeyProperties() {
        log.info("app.name = {}", env.getProperty("app.name"));
        log.info("app.description = {}", env.getProperty("app.description"));
        log.info("{}", env.getProperty("bael.property"));
    }
}
```

**局限**：必须知道属性名，无法列出所有属性。

## 16.2 方式二：ContextRefreshedEvent + 列出所有属性

```java
@Component
public class AllPropertiesLogger {

    private static final Logger log = LoggerFactory.getLogger(AllPropertiesLogger.class);

    @EventListener
    public void handleContextRefreshed(ContextRefreshedEvent event) {
        ConfigurableEnvironment env = (ConfigurableEnvironment)
            event.getApplicationContext().getEnvironment();

        env.getPropertySources().stream()
            .filter(ps -> ps instanceof MapPropertySource)
            .map(ps -> ((MapPropertySource) ps).getSource().keySet())
            .flatMap(Collection::stream)
            .distinct()
            .sorted()
            .forEach(key -> log.info("{} = {}", key, env.getProperty(key)));
    }
}
```

启动时会打印出**所有**配置来源的属性（环境变量、JVM 参数、application.properties 等），按字母排序。

**过滤到只显示 application.properties 中的配置**：

```java
.filter(ps -> ps instanceof MapPropertySource
    && ps.getName().contains("application.properties"))
```

## 16.3 方式三：Spring Boot Actuator /actuator/env

```properties
management.endpoints.web.exposure.include=env
```

打开 `http://localhost:8080/actuator/env`，返回包含所有配置属性的 JSON，带 origin（来源文件和行号）：

```json
{
  "propertySources": [
    {
      "name": "Config resource 'class path resource [application.properties]'",
      "properties": {
        "app.name": {
          "value": "MyApp",
          "origin": "class path resource [application.properties] - 10:10"
        },
        "bael.property": {
          "value": "defaultValue",
          "origin": "class path resource [application.properties] - 13:15"
        }
      }
    }
  ]
}
```

> **最推荐方式**：Actuator。零代码，带原点信息，环境变量和配置文件的属性一目了然。

---

# 第十七章：综合实战 —— 一个生产级配置模板

下面是一个可以直接用于 Spring Boot 3.4+ 项目的完整配置。

## 17.1 application.yml

```yaml
spring:
  application:
    name: order-service

logging:
  # 开发环境使用人类可读格式
  # 生产环境使用 JSON
  structured:
    format:
      console: ${LOGGING_STRUCTURED_FORMAT:}  # 默认空 = 人类可读格式
  level:
    root: WARN
    com.yourcompany: INFO
    org.springframework.web: WARN
    org.hibernate.SQL: WARN

---
spring:
  config:
    activate:
      on-profile: prod

logging:
  structured:
    format:
      console: logstash
  level:
    root: WARN
    com.yourcompany: INFO
```

## 17.2 logback-spring.xml（如需更细控制）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <include resource="org/springframework/boot/logging/logback/defaults.xml"/>

    <springProperty scope="context" name="APP_NAME" source="spring.application.name" defaultValue="app"/>
    <springProperty scope="context" name="PROFILE" source="spring.profiles.active" defaultValue="dev"/>

    <!-- ====== Console Appender ====== -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%X{traceId:-no-trace}] [%thread] %-5level %logger{36} - %msg%n</pattern>
            <charset>UTF-8</charset>
        </encoder>
    </appender>

    <!-- ====== JSON Appender (Logstash) ====== -->
    <appender name="JSON_CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
            <includeCallerData>false</includeCallerData>
            <customFields>{"service":"${APP_NAME}","env":"${PROFILE}"}</customFields>
            <includeMdcKeyName>traceId</includeMdcKeyName>
            <includeMdcKeyName>userId</includeMdcKeyName>
            <includeMdcKeyName>requestId</includeMdcKeyName>
        </encoder>
    </appender>

    <!-- ====== Rolling File ====== -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/${APP_NAME}.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <fileNamePattern>logs/${APP_NAME}-%d{yyyy-MM-dd}.%i.log.gz</fileNamePattern>
            <maxFileSize>100MB</maxFileSize>
            <maxHistory>30</maxHistory>
            <totalSizeCap>3GB</totalSizeCap>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%X{traceId:-no-trace}] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>

    <!-- ====== Async Wrapper ====== -->
    <appender name="ASYNC_FILE" class="ch.qos.logback.classic.AsyncAppender">
        <queueSize>1024</queueSize>
        <discardingThreshold>20</discardingThreshold>
        <neverBlock>false</neverBlock>
        <appender-ref ref="FILE"/>
    </appender>

    <!-- ====== Profiles ====== -->
    <springProfile name="dev,local">
        <root level="INFO">
            <appender-ref ref="CONSOLE"/>
        </root>
        <logger name="com.yourcompany" level="DEBUG"/>
    </springProfile>

    <springProfile name="prod,staging">
        <root level="WARN">
            <appender-ref ref="JSON_CONSOLE"/>
            <appender-ref ref="ASYNC_FILE"/>
        </root>
        <logger name="com.yourcompany" level="INFO"/>
    </springProfile>
</configuration>
```

---

# 常见问题 (FAQ)

## Q1：SLF4J 和 Logback 有什么区别？

SLF4J 是接口（抽象层），Logback 是实现。你的代码只依赖 SLF4J 接口（`LoggerFactory.getLogger()`），运行时 SLF4J 路由到 classpath 上的 Logback 实现。这样做的好处是——你可以通过改 Maven 依赖切换到 Log4j2，不用改一行 Java 代码。

## Q2：如何在生产环境输出 JSON 日志？

**方案 A (Spring Boot 3.4+)**：`logging.structured.format.console=logstash`（零依赖，官方内置）

**方案 B (Spring Boot < 3.4)**：引入 `logstash-logback-encoder`，配置 `LogstashEncoder`。

**方案 C**：直接输出到容器 stdout，由容器运行时（如 K8s 的 fluentd sidecar）收集并结构化。

## Q3：如何在生产环境动态调日志级别？

用 Spring Boot Actuator 的 `/actuator/loggers/{package}` 端点。POST 请求设置 DEBUG，排查完再改回 INFO。全程零重启。**但务必放在认证之后。**

## Q4：MDC 如何跨线程传递？

```java
Map<String, String> ctx = MDC.getCopyOfContextMap();
executor.submit(() -> {
    MDC.setContextMap(ctx);
    try { /* ... */ } finally { MDC.clear(); }
});
```

或者使用 Spring 的 `ThreadPoolTaskExecutor` 配合 `TaskDecorator` 自动传递。

## Q5: 日志占用太多磁盘怎么办？

1. 配置 `SizeAndTimeBasedRollingPolicy` + `totalSizeCap` 限制总大小
2. 生产环境不要在 root 开启 DEBUG
3. 使用 AsyncAppender 降低 I/O
4. 使用 JSON 格式配合日志采集平台（ELK/Datadog），本地不留或只保留3天

## Q6: 如何在测试中验证日志？

```java
@SpringBootTest
@ExtendWith(OutputCaptureExtension.class)
class OrderServiceTest {
    @Test
    void shouldLogOrderCreation(CapturedOutput output) {
        orderService.createOrder("ORD-001");
        assertThat(output).contains("Creating order ORD-001");
    }
}
```

## Q7: 到底怎么选日志框架？

| 场景 | 推荐 |
|------|------|
| 新 Spring Boot 3.4+ 项目 | **Logback（默认）+ 原生 structured logging** |
| 需要极高性能的异步日志 | **Logback + AsyncAppender** |
| 需要 Log4j2 的 RoutingAppender | **Log4j2**（需要额外配置） |
| 纯记录，不想碰 XML | **application.properties 即可** |

---

# 快速决策对照表

| 你的需求 | 最低配置量 | 核心配置 |
|----------|-----------|---------|
| 只想看一下程序在干嘛 | 0 行 | 默认日志就够了 |
| 调整日志级别 | 1 行 | `logging.level.com.xxx=DEBUG` |
| 输出到文件 | 1 行 | `logging.file.name=logs/app.log` |
| 文件轮转 | 1-3 行 | `logging.logback.rollingpolicy.*` |
| 不同环境不同配置 | 2 个 yml | `application-dev.yml` + `application-prod.yml` |
| JSON 结构化日志 | 1 行 | `logging.structured.format.console=logstash` |
| SQL 语句和参数一起看 | 1 个依赖 | `datasource-proxy-spring-boot-starter` |
| 全链路 trace ID 追踪 | 1 个 Filter | MDC + Filter 注入 |
| 方法级自动日志 | 1 个 Aspect | AOP 切面 |
| 运行时动态调级别 | 1 个依赖 | `spring-boot-starter-actuator` |
| 异步日志保性能 | 3-5 行 XML | `AsyncAppender` |
| 敏感信息脱敏 | 1 个 Filter | 自定义 Pattern 或 Filter |
| Console/File 不同级别 | 5 行 XML | `ThresholdFilter` 分别设 INFO(console) 和 DEBUG(file) |
| 打印应用配置属性 | 0-1 行 config | `Actuator /actuator/env` 或 `@EventListener` |

---

*✏️ 来源：Vlad Mihalcea《Log SQL with Spring Boot》| Spring Boot Official Docs | katyella.com | last9.io | Baeldung《Log Properties》《Different Log Level for File and Console Appender》| 各项网络资料补充整理*
