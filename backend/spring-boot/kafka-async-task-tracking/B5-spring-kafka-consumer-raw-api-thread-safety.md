# B5 — Spring Kafka 底层深度：Consumer API、线程安全与动态 Topic

> **匹配引子文章知识点：** ✅ 原始 KafkaConsumer ✅ 线程安全 ✅ AdminClient 动态创建 Topic ✅ 序列化配置
> 来源：Spring Kafka 官方文档 / Apache Kafka 源码 / 实战踩坑
> 收录维度：**B — 消息队列集成深度（底层篇）**

---

## TL;DR

引子文章使用**底层 **`KafkaConsumer`（非 `@KafkaListener`）+ **手动 `poll()`** + **KafkaAdmin + AdminClient 动态 `createTopics()`**。这是 Spring Kafka 生态中的"低层 API"用法。现有 B1 文章都用 `@KafkaListener` 高层 API，中间差了一个理解层次——本文章补上这个断层。

---

## 1. Spring Kafka 的三层 API

```
┌─────────────────────────────────────────────┐
│  Layer 3: 声明式                              │
│  @KafkaListener / @RetryableTopic            │ ← B1, D1 覆盖
│  (注解驱动, Spring 管理生命周期)              │
├─────────────────────────────────────────────┤
│  Layer 2: 编程式                              │
│  MessageListenerContainer / KafkaTemplate    │
│  (Spring 封装, 可控)                          │
├─────────────────────────────────────────────┤
│  Layer 1: 底层 API                            │
│  KafkaConsumer / KafkaProducer / AdminClient │ ← 引子文章使用
│  (Apache Kafka 原生, 完全控制)                │
└─────────────────────────────────────────────┘
```

引子文章跳过 Layer 2/3，直接用了 Layer 1。**为什么？**

- 每个任务需要**独立的 Consumer 订阅独立的 Topic** — `@KafkaListener` 在注解绑定时 Topic 是静态的
- 需要**按 taskId 过滤** — 用 `consumer.records(taskId)` 按 key 提取
- 展示最底层机制 — 教程意图

---

## 2. 原始 KafkaConsumer vs @KafkaListener 对比

| 特性 | 原始 KafkaConsumer | @KafkaListener |
|------|-------------------|----------------|
| Topic 绑定 | 运行时 `subscribe()` | 注解时静态指定 |
| 消息拉取 | 手动 `poll(Duration)` | 自动拉取 + 分发 |
| Ack / Offset | 手动管理 | `AckMode` 配置 |
| 线程安全 | ❌ 非线程安全 | ✅ 容器管理 |
| 并发处理 | 需自行管理 | `concurrency` 属性 |
| 错误处理 | try-catch | `ErrorHandler` / `@RetryableTopic` |
| 复杂度 | **高** | 低 |
| 控制粒度 | **最大** | 适度 |

### 引子文章原始写法

```java
@Bean
KafkaConsumer<String, TaskStatus> kafkaConsumer(
        ConsumerFactory<String, TaskStatus> consumerFactory) {
    return (KafkaConsumer<String, TaskStatus>) consumerFactory.createConsumer();
}

// 在 TaskService 中
@Async
public void process(...) {
    kafkaConsumer.subscribe(Collections.singletonList(topicName));
}

// 在 KafkaConsumerService 中
public TaskStatus getLatestTaskStatus(String taskId) {
    ConsumerRecords<String, TaskStatus> records = kafkaConsumer.poll(Duration.ofMillis(200));
    Iterator<ConsumerRecord<String, TaskStatus>> it = records.records(taskId).iterator();
    while (it.hasNext()) {
        latestUpdate = it.next();  // 只取最新一条
    }
    return latestUpdate != null ? latestUpdate.value() : null;
}
```

### 等效的 @KafkaListener 写法

```java
@Component
public class TaskProgressListener {

    @Autowired
    private TaskRepository taskRepository;

    @KafkaListener(
        topics = "#{'${task.topics}'.split(',')}",
        groupId = "task-progress-group",
        containerFactory = "taskKafkaListenerContainerFactory"
    )
    public void onProgress(TaskProgressEvent event) {
        taskRepository.findById(event.taskId()).ifPresent(task -> {
            task.setProgress(event.percentageComplete());
            task.setStatus(event.status().name());
            taskRepository.save(task);
        });
    }
}
```

**核心区别**：引子文章的做法需要你自己管理 Consumer 的线程安全、poll 循环、offset 提交。`@KafkaListener` 把这些都封装好了。

---

## 3. KafkaConsumer 线程安全（引子文章划重点）

### 问题：ConcurrentModificationException

引子文章在 `KafkaConsumerService` 中明确注释：

```java
// KafkaConsumer 不是线程安全的，如果上一次调用没有结束，
// 其它线程再访问将会出现 ConcurrentModificationException
```

**原因**：KafkaConsumer 在设计上就不是线程安全的。当多个线程（或多个 Controller 请求）同时调用同一个 Consumer 实例的 `poll()` 方法时，会抛出：

```
java.util.ConcurrentModificationException: KafkaConsumer is not safe for multi-threaded access
```

### 解决方法

**方案 A：synchronized（适合低并发）**
```java
public synchronized TaskStatus getLatestTaskStatus(String taskId) {
    ConsumerRecords<String, TaskStatus> records = kafkaConsumer.poll(Duration.ofMillis(200));
    // ...
}
```
→ 但这会串行化所有查请求，多个用户查进度会相互阻塞。

**方案 B：每个线程一个 Consumer 实例**
```java
// 使用 ConcurrentHashMap 缓存 Consumer 实例
private final ConcurrentHashMap<String, KafkaConsumer<String, TaskStatus>> consumers = new ConcurrentHashMap<>();

public TaskStatus getLatestTaskStatus(String taskId) {
    KafkaConsumer<String, TaskStatus> consumer = consumers.computeIfAbsent(taskId, this::createConsumer);
    synchronized(consumer) {
        ConsumerRecords<String, TaskStatus> records = consumer.poll(Duration.ofMillis(200));
        // ...
    }
}
```
→ 更适用但 Topic 太多时 OOM。

**方案 C：改用 @KafkaListener（推荐）**
```java
// Spring Kafka 的 ConcurrentMessageListenerContainer 管理
// 每个 Consumer 只有一个线程访问 → 天生安全
```

### Spring Kafka 官方线程安全指南

从 [Spring Kafka Docs - Thread Safety](https://docs.spring.io/spring-kafka/reference/kafka/thread-safety.html)：

> 使用 `concurrent message listener container` 时，**单个 Listener 实例在所有 Consumer 线程上共享调用**。
> 
> 因此 Listener 需要是线程安全的，最好是**无状态**的。
>
> 如果无法实现线程安全，可选方案：
> 1. 使用 n 个 `concurrency=1` 的容器 + prototype-scoped Listener bean
> 2. 将状态存在 `ThreadLocal` 中
> 3. Delegate 到 `SimpleThreadScope` bean

**Virtual Thread 警告（Spring Kafka 4.x）**：

> 当启用 Virtual Thread 时，如果并发超过可用平台线程数，Virtual Thread 可能被 pin 到平台线程，导致 **race condition**。
>
> **建议**：concurrency 保持 ≤ 平台线程数。

---

## 4. AdminClient 动态创建 Topic

### 引子文章的做法

```java
private void createNewTopic(String topicName) {
    NewTopic newTopic = new NewTopic(topicName, 1, (short) 1)
        .configs(Map.of(TopicConfig.RETENTION_MS_CONFIG, "86400000")); // 24h

    try (AdminClient adminClient =
            AdminClient.create(kafkaAdmin.getConfigurationProperties())) {
        adminClient.createTopics(Collections.singletonList(newTopic)).all().get();
    }
    kafkaConsumer.subscribe(Collections.singletonList(topicName));
}
```

### Spring Kafka 提供的动态 API

从 Spring Kafka 2.7 起，KafkaAdmin 提供了运行时创建/修改/删除 Topic 的方法：

```java
@Autowired
private KafkaAdmin admin;

public void createTopicRuntime(String topicName, int partitions, short replicas) {
    NewTopic newTopic = TopicBuilder.name(topicName)
        .partitions(partitions)
        .replicas(replicas)
        .config(TopicConfig.RETENTION_MS_CONFIG, "86400000")
        .build();

    admin.createOrModifyTopics(newTopic);
}

// 删除 Topic（Spring Kafka 4.0+）
public void deleteTopic(String topicName) {
    admin.deleteTopics(Set.of(topicName));
}

// 查询 Topic
public Set<String> listTopics() {
    try (AdminClient client = AdminClient.create(admin.getConfigurationProperties())) {
        return client.listTopics().names().get();
    }
}
```

### 三种 Topic 创建方式对比

| 方式 | 时机 | 适用场景 |
|------|------|---------|
| `NewTopic @Bean` | 应用启动时 | 静态已知的 Topic |
| `AdminClient.createTopics()` | 运行时 | 动态 Topic（如引子文章的任务专属 Topic） |
| 自动创建 (`auto.create.topics.enable=true`) | Producer/Consumer 首次读写时 | 开发环境快速测试 |

### ⚠️ 每条任务一个 Topic 的架构分析

引子文章的 `createNewTopic(taskId)` 导致**每个任务创建一个独立 Topic**。这是要点评的：

**好处：**
- ✅ 完全隔离：一个任务失败不影响其他任务
- ✅ Topic 级别的权限/保留策略控制
- ✅ 消费进度按 Topic 隔离

**坏处：**
- ❌ **Topic 爆炸**：10000 个任务 = 10000 个 Topic → ZooKeeper/KRaft 元数据压力
- ❌ Consumer 需要 `subscribe()` 新 Topic → 可能导致 rebalance
- ❌ 管理复杂度：Kafka-UI 列表里全是单消息 Topic

**更好的架构方案：**

```java
// ✅ 方案 1：单个 Topic + 分区
// Topic: task-progress (partitioned by taskId)
// 每个分区处理一批任务
producer.send(new ProducerRecord<>("task-progress", taskId, event));

// ✅ 方案 2：按业务域划分 Topic
// Topic: task-progress-import
// Topic: task-progress-export
// Topic: task-progress-report
// 每个 Topic 处理一类任务

// ✅ 方案 3：单 Topic + 压缩策略
// Topic: task-progress (compact=true)
// 用 taskId 作为 key，Kafka 自动保留每个 key 的最新消息
// → 重启后还可以拿到最新进度！
```

**引子文章选择每条任务一个 Topic 的原因**：教程演示代码，用最简单的隔离方式。生产环境建议改用**方案 2 或 3**。

---

## 5. Json 序列化配置深度解析

引子文章的配置：

```yaml
spring:
  kafka:
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
    consumer:
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      properties:
        spring.json.trusted.packages: "*"
        spring.json.value.default.type: com.example.tasktracker.event.TaskProgressEvent
```

### 为什么需要 `trusted.packages: "*"`?

JsonDeserializer 反序列化时会检查目标类型是否在白名单内。Trusted packages 告诉 Spring "信任这些包中的类"。`"*"` 信任所有——生产环境应该指定具体包名。

### 为什么需要 `spring.json.value.default.type`?

当消息没有 `__typeId__` header 时，JsonDeserializer 需要用这个配置知道目标类型。引子文章的生产者设置了 `value-serializer: JsonSerializer` 但未显式指定类型信息——JsonSerializer 默认会把全类名写入 `__typeId__` header。

### JsonSerializer 写入的 Header

```
Headers:
  __typeId__: "com.example.tasktracker.event.TaskProgressEvent"
```

Consume 时 JsonDeserializer 根据这个 header 确定反序列化目标类。如果 Producer 和 Consumer 不在同一个 Framework 下（如跨语言），需要自己管理这个 header。

---

## 6. 引子文章 vs 本文章的知识对照表

| 引子文章代码 | 底层原理 | 本文章的章节 |
|-------------|---------|-------------|
| `new KafkaConsumer(...)` | KafkaConsumer 线程不安全 | §3 线程安全 |
| `consumer.poll(200ms)` | 手动 poll 循环 | §2 三层 API |
| `AdminClient.createTopics()` | 动态 Topic 管理 | §4 AdminClient |
| `JsonSerializer/Deserializer` | 序列化机制 | §5 Json 序列化 |
| 每条任务一个 Topic | 架构权衡 | §4 Topic 对比 |

---

> **延伸阅读**: [B6 — 生产级可靠性：Offset 管理与重启恢复](./B6-kafka-offset-restart-recovery.md)
> **延伸阅读**: [B4 — KRaft + Docker + Kafka-UI 环境搭建](./B4-kafka-kraft-docker-kafka-ui-setup.md)
