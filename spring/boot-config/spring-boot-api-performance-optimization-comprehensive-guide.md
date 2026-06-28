---
title: "Spring Boot API 性能优化完全指南 —— 从毫秒到微秒的实战手册"
tags:
  - spring-boot
  - performance
  - optimization
  - guide
date: 2026-06-28
source: "https://mp.weixin.qq.com/s/Cpx7VdjYsxwVbyNOM81EKg"
authors: "Spring全家桶实战案例源码"
---

# Spring Boot API 性能优化完全指南

> **来源：** [Spring Boot API 性能优化：9 个技巧榨干每一毫秒](https://mp.weixin.qq.com/s/Cpx7VdjYsxwVbyNOM81EKg)  
> 本文在原文章基础上大幅扩展，补充了 Virtual Threads、JVM 调优、启动加速、监控链路、熔断限流等进阶内容，形成一份完整的性能优化手册。

---

## 目录

1. [引言](#1-引言)
2. [异步处理](#2-异步处理)
3. [缓存策略](#3-缓存策略)
4. [数据库查询优化](#4-数据库查询优化)
5. [数据压缩](#5-数据压缩)
6. [响应式编程（WebFlux）](#6-响应式编程-webflux)
7. [日志优化](#7-日志优化)
8. [数据库索引设计](#8-数据库索引设计)
9. [连接池管理](#9-连接池管理)
10. [CDN 加速静态资源](#10-cdn-加速静态资源)
11. [Virtual Threads（虚拟线程）](#11-virtual-threads虚拟线程)
12. [JVM 调优](#12-jvm-调优)
13. [启动加速——零成本优化](#13-启动加速零成本优化)
14. [API 监控与性能剖析](#14-api-监控与性能剖析)
15. [熔断、限流与重试](#15-熔断限流与重试)
16. [最佳实践清单](#16-最佳实践清单)
17. [总结](#17-总结)

---

## 1. 引言

随着微服务架构的普及，API 已成为系统性能的核心瓶颈。一次接口调用背后涉及：

- 数据库查询 → 对象映射 → JSON 序列化 → 网络传输 → 线程调度

任何一个环节的损耗都可能让响应时间从 **毫秒级** 膨胀到 **秒级**。在高并发（>1000 QPS）场景下，单次接口节省 5ms，整体吞吐就能提升 30% 以上。

**本文的目标：** 提供一个可落地的优化知识体系，覆盖从代码层到基础设施层、从单体到微服务的完整链路。每个技巧都会给出：

- 原理说明（为什么慢？）
- Spring Boot 实现（怎么改？）
- 最佳实践（什么场景用？什么场景别用？）

---

## 2. 异步处理

### 2.1 为什么需要异步？

默认情况下，Tomcat 的工作线程是有限的（`server.tomcat.threads.max=200`）。如果某个接口内部调用了耗时操作——比如发送邮件、生成 PDF、调用外部 API——那么线程就会被阻塞等待，其他请求只能排队。

**异步的核心思想：** 把耗时任务丢到后台线程池，立刻释放 Tomcat 线程，让请求先返回。

### 2.2 @Async 注解

最简单的做法：

```java
@Service
public class AsyncService {

    @Async
    public CompletableFuture<String> longRunningTask() {
        // 模拟耗时操作
        Thread.sleep(5000);
        return CompletableFuture.completedFuture("完成");
    }
}
```

启用异步需要在配置类上加 `@EnableAsync`：

```java
@Configuration
@EnableAsync
public class AsyncConfig {
}
```

**自定义线程池（强烈推荐）：**

```java
@Configuration
@EnableAsync
public class AsyncConfig {

    @Bean("taskExecutor")
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(50);
        executor.setQueueCapacity(200);
        executor.setThreadNamePrefix("async-");
        executor.setWaitForTasksToCompleteOnShutdown(true);
        executor.setAwaitTerminationSeconds(60);
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();
        return executor;
    }
}
```

> **陷阱：** 同一个类内部调用 `@Async` 方法不会生效（AOP 代理限制）。必须从外部注入调用。

### 2.3 DeferredResult——非阻塞异步响应

`DeferredResult` 是 Spring MVC 提供的异步返回机制——Servlet 线程立即返回，结果由另一个线程设置：

```java
@GetMapping("/deferred")
@ResponseBody
public DeferredResult<Map<String, Object>> deferred() {
    long start = System.currentTimeMillis();
    System.out.printf("%s - 开始时间：%d%n", Thread.currentThread().getName(), start);

    DeferredResult<Map<String, Object>> deferredResult = new DeferredResult<>();

    new Thread(() -> {
        try {
            TimeUnit.SECONDS.sleep(3);
            Map<String, Object> result = new HashMap<>();
            result.put("code", 1);
            result.put("data", "你的业务数据");
            deferredResult.setResult(result);
        } catch (InterruptedException ignored) {}
    }).start();

    long end = System.currentTimeMillis();
    System.out.printf("总耗时：%d毫秒%n", (end - start));
    return deferredResult;
}
```

典型耗时约 **0ms**（Tomcat 线程立即释放），而实际业务在后台线程中跑 3 秒后异步写回。

### 2.4 WebAsyncTask——带超时/回调

```java
@GetMapping("/web-async")
public WebAsyncTask<String> webAsyncTask() {
    Callable<String> callable = () -> {
        Thread.sleep(3000);
        return "异步结果";
    };
    WebAsyncTask<String> task = new WebAsyncTask<>(5000, callable);
    task.onTimeout(() -> "超时了！");
    return task;
}
```

### 2.5 适用场景

| 适用 ✅ | 不适用 ❌ |
|---------|----------|
| 发送邮件/短信 | 需要实时返回结果 |
| 生成报表/PDF | 事务内的写操作 |
| 日志异步写入 | 用户等待的查询接口 |
| 消息推送 | 依赖当前线程上下文的代码 |
| 调用外部慢 API | |

---

## 3. 缓存策略

### 3.1 缓存为什么有效？

数据库的瓶颈通常在磁盘 I/O。一次全表扫描 = 几十毫秒，而一次内存读取 = **纳秒级**。对于"读多写少"的数据（配置、字典、用户信息），缓存是 ROI 最高的优化手段。

### 3.2 Spring Cache 抽象

Spring 提供了统一缓存抽象，支持多种实现（Redis、Caffeine、EhCache、JCache）：

```java
@Service
@CacheConfig(cacheNames = {"userCache"})
public class UserService {

    @Cacheable(key = "#id")
    public User queryById(Long id) {
        // 只有缓存未命中时才执行
        return userRepository.findById(id).orElse(null);
    }

    @CacheEvict(key = "#id")
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
        // 同时清除缓存
    }

    @CachePut(key = "#user.id")
    public User updateUser(User user) {
        return userRepository.save(user);
    }
}
```

启用：

```java
@EnableCaching
@Configuration
public class CacheConfig {
}
```

### 3.3 选择缓存实现

| 实现 | 场景 | 特点 |
|------|------|------|
| **Caffeine** | 本地缓存，单机 | 极致性能，内存可控，支持过期策略 |
| **Redis** | 分布式缓存 | 共享数据，适合微服务间同步 |
| 混合（Caffeine + Redis） | 两级缓存 | Caffeine 做 L1（毫秒级），Redis 做 L2（保证一致） |

**Caffeine 配置最佳实践：**

```java
@Bean
public CacheManager cacheManager() {
    CaffeineCacheManager manager = new CaffeineCacheManager();
    manager.setCaffeine(Caffeine.newBuilder()
        .expireAfterWrite(10, TimeUnit.MINUTES)
        .maximumSize(10_000)
        .recordStats());
    return manager;
}
```

### 3.4 缓存穿透、击穿、雪崩

| 问题 | 场景 | 解决方案 |
|------|------|---------|
| **穿透** | 查询不存在的 key，每次都打 DB | 缓存空值（`null`）+ 短过期时间；布隆过滤器 |
| **击穿** | 热点 key 过期瞬间，大量并发打 DB | 互斥锁（`@Cacheable(sync=true)`）；缓存预热 |
| **雪崩** | 大量 key 同时过期 | 过期时间加随机偏移；多级缓存 |

```java
// sync=true 开启本地锁，防止缓存击穿
@Cacheable(key = "#id", sync = true)
public User queryById(Long id) { ... }
```

### 3.5 缓存更新的三种模式

1. **Cache-Aside（最常用）：** 读 → 未命中 → 查 DB → 写缓存
2. **Read-Through：** 缓存层自动加载（如 Caffeine LoadingCache）
3. **Write-Behind：** 先更新缓存，异步写 DB（适合写少场景）

> ⚠️ **过期的缓存更新策略**：先更新 DB 再删缓存（而不是先删缓存再更新 DB），可以避免并发读写导致的数据不一致。

---

## 4. 数据库查询优化

### 4.1 只查询需要的字段

最直观的优化：**不要 SELECT \***。JPA 和 MyBatis 都支持投影查询：

**JPA 接口投影：**

```java
public interface UserProjection {
    Long getId();
    String getUsername();
    String getPhone();
}

public interface UserRepository extends JpaRepository<User, Long> {

    @Query("SELECT u.id as id, u.username as username, u.phone as phone " +
           "FROM User u WHERE u.status = 1")
    List<UserProjection> findUserProjection();
}
```

**JPA EntityManager：**

```java
public List<Object[]> optimizedQuery() {
    Query query = entityManager.createQuery(
        "SELECT u.id, u.username FROM User u WHERE u.status = :status");
    query.setParameter("status", 1);
    return query.getResultList();
}
```

### 4.2 N+1 查询问题

**这是 JPA 最常见的性能坑。** 当查询一个实体集合时，如果实体有关联实体（`@OneToMany`、`@ManyToOne`），懒加载会导致每个实体被访问时额外执行一条 SQL。

**症状：** 1 条主查询 + N 条关联查询

**解决方案：**

```java
// 方案一：JOIN FETCH（推荐）
@Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.customerId = :customerId")
List<Order> findOrdersWithItems(@Param("customerId") Long customerId);

// 方案二：Entity Graph
@EntityGraph(attributePaths = {"items", "address"})
List<Order> findByCustomerId(Long customerId);

// 方案三：@BatchSize
@Entity
public class Order {
    @OneToMany(mappedBy = "order")
    @BatchSize(size = 20)  // 批量加载，一次加载 20 个关联集合
    private List<OrderItem> items;
}
```

### 4.3 分页查询

永远不要用 `findAll()` 获取大量数据。Spring Data 内置分页支持：

```java
@Query("SELECT u FROM User u WHERE u.status = 1")
Page<User> findActiveUsers(Pageable pageable);

// 调用
Page<User> page = userRepository.findActiveUsers(
    PageRequest.of(0, 20, Sort.by("createTime").descending()));
```

> **注意：** 对超大结果集，`Page` 的 `count` 查询可能成为新瓶颈。可以考虑改用 `Slice`（不执行 count）。

### 4.4 批处理操作

避免循环内逐条执行 SQL：

```java
// ❌ 错误：N 条 insert
for (User user : userList) {
    userRepository.save(user);
}

// ✅ 正确：批处理
userRepository.saveAll(userList);

// 还需要配置 JPA 批处理
spring.jpa.properties.hibernate.jdbc.batch_size=50
spring.jpa.properties.hibernate.order_inserts=true
spring.jpa.properties.hibernate.order_updates=true
```

---

## 5. 数据压缩

### 5.1 为什么需要压缩？

API 响应的主要延迟中，**网络传输** 占很大比重，尤其是大数据量接口（如列表、报表）。GZIP 压缩可以将 JSON 体积减少 **70-90%**，显著缩短传输时间。

### 5.2 全局配置（推荐）

Spring Boot 支持通过 `application.yml` 一键开启 GZIP 压缩：

```yaml
server:
  compression:
    enabled: true
    min-response-size: 1024        # 大于 1KB 才压缩
    mime-types:
      - text/html
      - text/xml
      - text/plain
      - text/css
      - text/javascript
      - application/javascript
      - application/json
      - application/xml
```

### 5.3 手动压缩（需要更细粒度控制时）

```java
@RestController
public class CompressionController {

    @GetMapping("/compressedData")
    public void getCompressedData(HttpServletResponse response) throws IOException {
        String data = "This is a large amount of data...";

        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        GZIPOutputStream gzipOutputStream = new GZIPOutputStream(baos);
        gzipOutputStream.write(data.getBytes());
        gzipOutputStream.close();

        response.addHeader("Content-Encoding", "gzip");
        response.getOutputStream().write(baos.toByteArray());
    }
}
```

### 5.4 注意事项

- **CPU vs 网络权衡：** GZIP 会消耗 CPU 做压缩，但网络带宽节省通常远大于 CPU 开销
- **小负载不压缩：** 小于 1KB 的响应，压缩头本身可能让体积更大
- **浏览器兼容性：** 所有现代浏览器都支持 gzip 解压
- **Nginx 代理：** 如果前面有 Nginx，考虑在代理层做压缩

---

## 6. 响应式编程（WebFlux）

### 6.1 WebFlux 解决的问题

传统 Servlet 模型是**⼀线程-⼀请求**。当线程阻塞在 I/O 上（数据库查询、远程调用）时，线程就被浪费了。WebFlux 基于 Reactor 库，使用**事件驱动 + 非阻塞 I/O**，同样的资源可以处理更多并发。

### 6.2 依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>
```

### 6.3 基本示例

```java
@RestController
public class WebFluxController {

    @GetMapping("/reactiveData")
    public Mono<String> getReactiveData() {
        return Mono.just("Reactive programming data");
    }

    @GetMapping("/users/{id}")
    public Mono<User> getUser(@PathVariable Long id) {
        return userRepository.findById(id);  // 需要 Reactive 的 Repository
    }

    @GetMapping("/users")
    public Flux<User> listUsers() {
        return userRepository.findAll();
    }
}
```

### 6.4 响应式数据库访问

需要配合响应式数据库驱动：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-r2dbc</artifactId>
</dependency>
```

```java
public interface ReactiveUserRepository extends ReactiveCrudRepository<User, Long> {
    Flux<User> findByStatus(int status);
}
```

### 6.5 什么时候用 WebFlux？

| 场景 | 推荐 |
|------|------|
| 高并发 I/O 密集型（网关、代理） | ✅ WebFlux |
| CPU 密集型计算 | ❌ 传统 Servlet |
| 简单 CRUD，请求不密集 | ❌ 没必要 |
| 底层技术栈已全部异步 | ✅ WebFlux |
| 团队不熟悉响应式编程 | ❌ 引入复杂度 > 收益 |

> **面试高频题：** "WebFlux 比 MVC 快吗？"  
> 答案：WebFlux 的**单请求延迟**并不比 MVC 快。它的优势是**同样资源下更高的并发吞吐**。如果只有 100 QPS，两者的区别可以忽略。

---

## 7. 日志优化

### 7.1 日志为什么慢？

日志 I/O 是同步操作。在 DEBUG 级别下，`log.debug("用户信息：" + user)` 这句看起来无害的代码，实际上：

1. 拼接字符串（即使是 `{}` 占位符也需要内部格式化）
2. 分配对象（`LoggingEvent`、`LogRecord` 等）
3. I/O 写入（文件、控制台）

当并发足够大时，日志能成为吞吐量的隐形杀手。

### 7.2 生产环境日志最佳实践

```yaml
logging:
  level:
    root: WARN
    com.yourpackage: INFO
    org.springframework: WARN
    org.hibernate: WARN
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
  file:
    path: /var/log/app
    max-size: 100MB
    max-history: 30
```

### 7.3 异步日志（Logback）

```xml
<!-- logback-spring.xml -->
<configuration>
    <!-- 异步 Appender -->
    <appender name="ASYNC" class="ch.qos.logback.classic.AsyncAppender">
        <queueSize>512</queueSize>
        <discardingThreshold>0</discardingThreshold>
        <appender-ref ref="FILE" />
    </appender>

    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_PATH}/app.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${LOG_PATH}/app.%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>

    <root level="INFO">
        <appender-ref ref="ASYNC"/>
    </root>
</configuration>
```

### 7.4 条件打日志

```java
if (logger.isInfoEnabled()) {
    logger.info("查询用户: {}", userId);
}
```

> 现代日志框架（Logback、Log4j2）使用 `{}` 占位符时，如果日志级别不满足，**不会拼接字符串**。但如果你写 `logger.info("用户：" + user)`，字符串拼接总是会发生。

**日志性能对比（生产环境）：**

```java
// ❌ 最差：字符串拼接 + 无级别检查
logger.debug("用户登录: " + user + ", 时间: " + now);

// ❌ 中等：占位符，但仍然创建 lambda 参数
logger.debug("用户登录: {}, 时间: {}", user, now);

// ✅ 最佳：级别检查 + 占位符（但仅当拼接开销真的很高时）
if (logger.isDebugEnabled()) {
    logger.debug("用户登录: {}, 时间: {}", user, now);
}
```

### 7.5 日志对性能影响有多大？

参考文章"天天打 Log"中的实测：一个 Spring Boot 应用中，不合理的日志配置（控制台输出 + DEBUG 级别 + 字符串拼接）可以让吞吐量从 5000 TPS **降到 2500 TPS**——损失 50%。

---

## 8. 数据库索引设计

### 8.1 索引的核心原则

数据库优化中，**索引是最立竿见影的手段**。一个正确的索引能让查询时间从 **几秒到几毫秒**。

**基本原则：**

1. **区分度高**的列在前（如用户 ID）
2. **查询条件 `WHERE` 中的列 → 联合索引前缀列**
3. **排序 `ORDER BY` 中的列 → 索引的后缀列**
4. **避免索引列上的计算**：`WHERE age * 2 > 30` 无法使用索引

### 8.2 联合索引

```sql
-- 创建联合索引
CREATE INDEX idx_username_email_age ON user (username, email, age);
```

这个索引能匹配的查询：

```java
// ✅ 能用到索引（最左前缀）
User findByUsername(String username);
User findByUsernameAndEmail(String username, String email);
User findByUsernameAndEmailAndAge(String username, String email, Integer age);

// ❌ 无法使用索引（跳过最左列）
User findByEmail(String email);
```

### 8.3 覆盖索引

如果查询的所有字段都在索引中，数据库可以直接从索引返回结果，**无需回表**：

```sql
CREATE INDEX idx_covering ON user (username, email, phone, status);
```

```java
@Query("SELECT u.username, u.email, u.phone FROM User u WHERE u.status = 1")
List<Object[]> findUserBasicInfo();
```

### 8.4 索引不是越多越好

| 索引的代价 | 说明 |
|-----------|------|
| 写性能下降 | 每次 INSERT/UPDATE/DELETE 都要维护索引 |
| 磁盘占用 | 一个索引可以占数百 MB |
| 查询优化器困惑 | 过多冗余索引可能导致优化器选择错误 |

**检查冗余索引：**

```sql
-- MySQL
SELECT TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX, COLUMN_NAME
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = 'your_db'
ORDER BY TABLE_NAME, INDEX_NAME;
```

### 8.5 慢查询监控

```yaml
# 开启慢 SQL 日志
spring.jpa.properties.hibernate.generate_statistics=true
spring.jpa.show-sql=false                # 关掉 show-sql，用统计信息代替
logging.level.org.hibernate.stat=DEBUG
```

MySQL 端开启慢查询：

```sql
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;          -- 超过 1 秒
```

---

## 9. 连接池管理

### 9.1 为什么需要连接池？

创建数据库连接是一个昂贵的操作（TCP 握手 + MySQL 认证 ≈ 几十毫秒）。连接池维护一组已建立的连接，复用它们。

### 9.2 HikariCP 配置

HikariCP 是 Spring Boot 2.x+ 的默认连接池，也是 **性能最好的连接池**（没有之一）。

**关键参数详解：**

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/testjpa
    username: root
    password: ${DB_PASSWORD}
    type: com.zaxxer.hikari.HikariDataSource
    hikari:
      minimum-idle: 20               # 最小空闲连接数
      maximum-pool-size: 50          # 最大连接数
      connection-timeout: 30000      # 等待连接超时(ms)
      idle-timeout: 600000           # 空闲连接存活时间(ms)
      max-lifetime: 1800000          # 连接最大存活时间(ms)
      auto-commit: true
      pool-name: MyHikariPool
      connection-test-query: SELECT 1
```

### 9.3 连接池大小公式

**这是一个反直觉的结论：** 连接池不是越大越好。

```
连接池大小 = Tn × (Cm - 1) + 1
```

其中：
- Tn = 线程数量（通常 CPU 核心数）
- Cm = 单个任务等待数据库的时间 / 单个任务总耗时

**经验法则：**

| CPU 核心数 | 建议最大连接数 |
|-----------|--------------|
| 4 （单核） | 10 ~ 20 |
| 8 （中配） | 20 ~ 50 |
| 16+（高配）| 30 ~ 100 |

> 为什么不要超过 100？超过 100 个连接时，数据库上下文切换的开销反而超过并发收益。

### 9.4 连接泄漏检测

```yaml
spring.datasource.hikari.leak-detection-threshold: 60000  # 60 秒未归还→告警
```

### 9.5 批量业务专用连接池

对于有批量导入场景的应用，可以为批量操作配置独立的连接池：

```java
@Bean
@Qualifier("batchDataSource")
@ConfigurationProperties(prefix = "spring.datasource.batch")
public DataSource batchDataSource() {
    return DataSourceBuilder.create()
        .type(HikariDataSource.class)
        .build();
}
```

```yaml
spring:
  datasource:
    batch:
      jdbc-url: jdbc:mysql://localhost:3306/testjpa
      username: root
      password: ${DB_PASSWORD}
      hikari:
        maximum-pool-size: 10
        connection-timeout: 60000    # 批量任务可以多等一会
```

---

## 10. CDN 加速静态资源

### 10.1 CDN 的原理

CDN（内容分发网络）将静态资源缓存到离用户最近的边缘节点，减少网络跳数。

### 10.2 使用方式

**在 HTML 或代码中直接引用公共 CDN：**

```html
<!-- Vue.js - 从 CDN 加载 -->
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>

<!-- Bootstrap CSS -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
```

**自有静态资源上 CDN：**

![CDN 加速](../image/spring-boot-api-performance-cdn.jpg)

### 10.3 Spring Boot 静态资源配置

```yaml
spring:
  web:
    resources:
      static-locations: classpath:/static/, file:/opt/static/
      cache:
        period: 604800  # 7 天
      chain:
        enabled: true
        strategy:
          content:
            enabled: true
            paths: /**
```

**注意：** 静态资源放 CDN 后建议关闭 Spring Boot 的应用层静态资源处理（减少无用的请求消耗）。

---

## 11. Virtual Threads（虚拟线程）

### 11.1 什么是虚拟线程？

Java 21 引入的虚拟线程（Project Loom）是一个**颠覆性的并发模型**。传统平台线程是 OS 线程的 1:1 映射——创建成本高、切换开销大、数量受限。虚拟线程是 JVM 管理的轻量级线程（M:N 映射），可以创建**百万级**而几乎没有开销。

### 11.2 Spring Boot 3.2+ 启用虚拟线程

Spring Boot 3.2（配合 Spring Framework 6.1）正式支持虚拟线程。

```yaml
spring:
  threads:
    virtual:
      enabled: true
```

就一行配置。Tomcat 接收到请求后将使用虚拟线程来处理，而不是线程池。

### 11.3 代码级验证

```java
@GetMapping("/thread-info")
public Map<String, String> threadInfo() {
    Thread t = Thread.currentThread();
    return Map.of(
        "name", t.getName(),
        "isVirtual", String.valueOf(t.isVirtual()),
        "toString", t.toString()
    );
}
```

返回示例（平台线程）：
```json
{"name":"http-nio-8080-exec-1","isVirtual":"false","toString":"Thread[http-nio-8080-exec-1,5,main]"}
```

返回示例（虚拟线程）：
```json
{"name":"","isVirtual":"true","toString":"VirtualThread[#57]/ForkJoinPool-1-worker-1"}
```

### 11.4 虚拟线程的踩坑指南

| 陷阱 | 说明 | 解决方案 |
|------|------|---------|
| **ThreadLocal 滥用** | 虚拟线程数量巨大，ThreadLocal 可能导致 OOM | 改用 `ScopedValue`（Java 21 Preview）或严格控制使用量 |
| **synchronized 钉住** | 虚拟线程在 `synchronized` 块中会钉住平台线程 | 改用 `ReentrantLock` |
| **连接池配置冲突** | 虚拟线程下盲目放大连接池参数 | 保持默认，虚拟线程可以等待 |
| **线程池嵌套** | 虚拟线程再提交到线程池 | 直接调用，不要嵌套 |

### 11.5 性能对比

| 指标 | 平台线程（Tomcat 200） | 虚拟线程 |
|------|-----------------------|---------|
| 最大并发 | ~200 | 数十万 |
| 1000 QPS 平均延迟 | 45ms | 12ms |
| 内存占用（1000 线程）| ~10MB | ~1MB |
| 上下文切换开销 | 高（OS 级） | 极低（JVM 级） |

> **推荐：** 新项目（Java 21+）直接启用虚拟线程。这是 Spring Boot 性能优化中**性价比最高**的改变——一行配置就能获得显著提升。

---

## 12. JVM 调优

### 12.1 JVM 内存模型速览

```
┌──────────────┐
│   Young Gen  │  Eden + S0 + S1    → 新对象
│   Old Gen    │                     → 长期存活对象
│   Metaspace  │                     → 类元数据
│   Direct     │                     → NIO 缓冲区
└──────────────┘
```

### 12.2 推荐的 JVM 参数

```bash
# 堆内存（根据服务器配置调整 -Xms 和 -Xmx 设为相同值避免动态调整）
-Xms4g -Xmx4g

# 年轻代（堆的 1/3 ~ 1/2）
-Xmn1.5g

# Metaspace（类加载空间）
-XX:MetaspaceSize=256m
-XX:MaxMetaspaceSize=256m

# GC 选择（推荐 G1GC）
-XX:+UseG1GC
-XX:MaxGCPauseMillis=100       # 目标 GC 暂停时间
-XX:InitiatingHeapOccupancyPercent=45  # G1 触发混合回收的堆占用率

# GC 日志（诊断用）
-Xlog:gc*:file=/var/log/app/gc.log:time,level,tags:filecount=5,filesize=10m

# 其他
-XX:+DisableExplicitGC          # 禁用 System.gc()
-Djava.awt.headless=true        # 无 GUI 环境
```

### 12.3 垃圾回收调优步骤

1. **默认启动 → 监控 GC 频率和暂停时间**
   ```bash
   jstat -gcutil <pid> 1000 10   # 每 1 秒输出一次，共 10 次
   ```

2. **如果 Full GC 频繁 → 堆太小或对象泄漏**，增加 `-Xmx`
3. **如果 YGC 暂停时间过长 → 减小年轻代大小或改用 G1**
4. **如果 MetaSpace 频繁 GC → 增大 MetaspaceSize**

### 12.4 OOM 诊断

```bash
# 自动 dump 堆转储
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/app/heapdump.hprof

# 分析（离线）
jhat /var/log/app/heapdump.hprof
# 或用 Eclipse MAT 可视化分析
```

### 12.5 减少对象创建（微优化）

```java
// ❌ 每次请求创建新对象
List<String> result = new ArrayList<>();
for (int i = 0; i < 1000; i++) {
    result.add(String.valueOf(i));   // 每次创建 String
}

// ✅ 复用 StringBuilder
StringBuilder sb = new StringBuilder(4096);
for (int i = 0; i < 1000; i++) {
    sb.append(i).append(",");
}
```

> **原则：** 避免在热点路径上频繁创建短期对象。对象创建 → GC 标记 → 清理，形成"内存抖动"。

---

## 13. 启动加速（零成本优化）

### 13.1 延迟初始化

Spring Boot 默认组件是立即初始化的。对于非关键 Bean，可以推迟到第一次使用时才初始化。

```yaml
spring:
  main:
    lazy-initialization: true    # 全局延迟初始化
```

**注意：** 全局开启后，第一个请求的响应时间会变慢（初始化开销）。

**更精细的做法：**

```java
@Component
@Lazy(false)    // 核心 Bean 立即初始化
public class CriticalService { ... }
```

### 13.2 Spring AOT（Spring Boot 3.0+）

AOT 编译在构建期完成反射分析、代理配置等，减少运行时开销：

```xml
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <configuration>
        <jvmArguments>-Dspring.aot.enabled=true</jvmArguments>
    </configuration>
</plugin>
```

### 13.3 精简自动配置

移除不需要的 Starter：

```yaml
spring:
  autoconfigure:
    exclude:
      - org.springframework.boot.autoconfigure.data.elasticsearch.ElasticsearchAutoConfiguration
      - org.springframework.boot.autoconfigure.data.redis.RedisAutoConfiguration
      - org.springframework.boot.autoconfigure.jms.activemq.ActiveMQAutoConfiguration
```

### 13.4 运行模式选择

```
生产环境 → jar（打包体积大但启动快） > exploded（开发用）
```

---

## 14. API 监控与性能剖析

### 14.1 链路追踪（Micrometer + Zipkin）

Spring Boot Actuator + Micrometer 可以精确测量每个端点的性能：

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,metrics,prometheus
  metrics:
    tags:
      application: ${spring.application.name}
```

```java
// 自定义指标
@Autowired
private MeterRegistry meterRegistry;

public void processOrder() {
    Timer.Sample sample = Timer.start(meterRegistry);
    try {
        // 业务逻辑
    } finally {
        sample.stop(Timer.builder("order.processing.time")
            .description("订单处理耗时")
            .register(meterRegistry));
    }
}
```

接入 Prometheus + Grafana 可以实时监控每个接口的 **P50 / P95 / P99 延迟**。

### 14.2 接口耗时代理（AOP 实现）

```java
@Aspect
@Component
public class PerformanceAspect {

    private static final Logger log = LoggerFactory.getLogger(PerformanceAspect.class);

    @Around("@annotation(org.springframework.web.bind.annotation.RequestMapping) || " +
            "@annotation(org.springframework.web.bind.annotation.GetMapping) || " +
            "@annotation(org.springframework.web.bind.annotation.PostMapping)")
    public Object measureTime(ProceedingJoinPoint joinPoint) throws Throwable {
        long start = System.nanoTime();
        String methodName = joinPoint.getSignature().toShortString();
        try {
            return joinPoint.proceed();
        } finally {
            long elapsed = System.nanoTime() - start;
            long ms = TimeUnit.NANOSECONDS.toMillis(elapsed);
            if (ms > 500) {  // 超过 500ms 告警
                log.warn("SLOW API: {} took {}ms", methodName, ms);
            }
        }
    }
}
```

### 14.3 监控指标解读

| 指标 | 关注点 | 阈值 |
|------|--------|------|
| P50 延迟 | 用户体验 | < 100ms |
| P95 延迟 | 尾部延迟 | < 500ms |
| P99 延迟 | 极端情况 | < 2000ms |
| 错误率 | 稳定性 | < 1% |
| GC 暂停时间 | JVM 健康 | < 200ms |

---

## 15. 熔断、限流与重试

### 15.1 Resilience4j 集成

Spring Cloud 2020.x 之后推荐使用 Resilience4j（替代 Hystrix）：

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-circuitbreaker-resilience4j</artifactId>
</dependency>
```

**限流配置：**

```yaml
resilience4j:
  ratelimiter:
    instances:
      userService:
        limit-for-period: 100           # 每周期限制 100 次
        limit-refresh-period: 1s        # 周期 1 秒
        timeout-duration: 500ms         # 等待令牌超时
```

**熔断配置：**

```yaml
resilience4j:
  circuitbreaker:
    instances:
      externalApi:
        sliding-window-size: 10         # 统计窗口大小
        failure-rate-threshold: 50      # 50% 失败 → 熔断
        wait-duration-in-open-state: 10s # 半开后等待 10s
        permitted-number-of-calls-in-half-open-state: 3
```

**代码使用：**

```java
@Service
public class PaymentService {

    @RateLimiter(name = "userService", fallbackMethod = "fallback")
    public PaymentResult processPayment(PaymentRequest request) {
        return paymentGateway.call(request);
    }

    public PaymentResult fallback(PaymentRequest request, Exception e) {
        log.warn("支付限流，使用兜底策略", e);
        return PaymentResult.fallback("系统繁忙，请稍后重试");
    }
}
```

### 15.2 重试机制

```java
@Retryable(
    value = {IOException.class, TimeoutException.class},
    maxAttempts = 3,
    backoff = @Backoff(delay = 1000, multiplier = 1.5)
)
public String callExternalService() {
    return restTemplate.getForObject("http://external/api", String.class);
}
```

> **重试的代价：** 不加退避的重试只会让系统故障雪崩。务必使用指数退避 + 随机抖动的重试策略。

---

## 16. 最佳实践清单

### 16.1 优先级排序

性能优化的投资回报率排序（从高到低）：

| 优先级 | 优化手段 | 难度 | 效果 |
|--------|---------|------|------|
| 🔴 P0 | 数据库索引 + SQL 优化 | ⭐ | 10x ~ 100x |
| 🔴 P0 | 缓存（Caffeine / Redis） | ⭐⭐ | 5x ~ 50x |
| 🟠 P1 | 异步处理 + Virtual Threads | ⭐⭐ | 2x ~ 10x |
| 🟠 P1 | 连接池调优 | ⭐ | 1.5x ~ 3x |
| 🟠 P1 | 数据压缩 | ⭐ | 1.5x ~ 5x（传输阶段） |
| 🟡 P2 | JVM 调优 | ⭐⭐⭐ | 1.2x ~ 2x |
| 🟡 P2 | 日志优化 | ⭐ | 1.2x ~ 2x |
| 🟢 P3 | WebFlux | ⭐⭐⭐ | 高并发场景显著 |
| 🟢 P3 | CDN 加速 | ⭐ | 前端体验提升 |
| 🟢 P3 | AOT/启动加速 | ⭐⭐ | 冷启动/扩缩容场景 |

### 16.2 通用原则

1. **先测量，后优化**——不测量就优化是猜测
2. **做对的事比做好更重要**——索引 > 缓存 > JVM 调优
3. **不要过早优化**——除非你能证明这是瓶颈
4. **每次只改一个变量**——同时改多个变量无法归因
5. **关注 P99 而不是平均值**——平均值掩盖了尾部延迟问题
6. **性能是功能需求**——上线前就要定好 SLA 指标

### 16.3 自检清单

```
□ 数据库：所有高频查询都有合适的索引？
□ 缓存：读多写少的数据是否已缓存？
□ SQL：是否存在 N+1 查询？
□ 线程：耗时任务是否已异步化？
□ 日志：生产环境日志级别是否恰当？
□ 连接池：最大连接数是否符合 QPS 需求？
□ 压缩：大数据量接口是否开启 GZIP 压缩？
□ JVM：堆内存是否合理？GC 频率是否过高？
□ 监控：是否接入耗时追踪和慢查询？
□ 容错：是否配置了熔断/限流/重试？
```

---

## 17. 总结

Spring Boot API 性能优化是一个**系统工程**，不是单点突破就能解决的。

本文从 **9 个基础技巧**（异步、缓存、SQL、压缩、WebFlux、日志、索引、连接池、CDN）出发，补充了 **6 个进阶实战方向**（Virtual Threads、JVM 调优、启动加速、监控、熔断限流），最终形成一个完整的技术栈覆盖。

**最重要的三个建议：**

1. **先从数据库优化开始**——这是性价比最高的投入，一个复合索引可能比调 10 个 JVM 参数效果更好
2. **性能监控是第一生产力**——没有链路追踪和慢查询日志，你永远是在"盲人摸象"
3. **Spring Boot 3.2+ 的项目务必开启 Virtual Threads**——一行配置换一个数量级的并发提升

---

*整理时间：2026-06-28*  
*来源：[Spring Boot API 性能优化：9 个技巧榨干每一毫秒](https://mp.weixin.qq.com/s/Cpx7VdjYsxwVbyNOM81EKg)*  
*补充参考：javaguides.net, springjavalab.com, javacodegeeks.com, 腾讯云开发者社区*
