# Spring Boot + Kafka 长时间任务进度跟踪 — 完全合辑

> 本文件由 `kafka-async-task-tracking/` 目录下所有独立文档自动合并生成。
> 每篇原文作为独立章节保留全部内容。
> 合并日期：2026-06-26

---

## 目录

- [第 1 章：引子文章 — Spring Boot + Kafka 实时跟踪长时间运行任务](#引子文章 — Spring Boot + Kafka 实时跟踪长时间运行任务)
- [第 2 章：A1 — 自定义线程池异步处理](#A1 — 自定义线程池异步处理)
- [第 3 章：A2 — 异步线程池优化全面指南](#A2 — 异步线程池优化全面指南)
- [第 4 章：A3 — Spring Boot Task Execution 官方文档](#A3 — Spring Boot Task Execution 官方文档)
- [第 5 章：B1 — REST API + Kafka 长时间任务进度追踪](#B1 — REST API + Kafka 长时间任务进度追踪)
- [第 6 章：B2 — Kafka 流式长任务处理架构](#B2 — Kafka 流式长任务处理架构)
- [第 7 章：B3 — 异步消息模式：Kafka vs RabbitMQ](#B3 — 异步消息模式：Kafka vs RabbitMQ)
- [第 8 章：B4 — KRaft + Docker + Kafka-UI 环境搭建](#B4 — KRaft + Docker + Kafka-UI 环境搭建)
- [第 9 章：B5 — Spring Kafka 底层深度：Consumer API、线程安全与动态 Topic](#B5 — Spring Kafka 底层深度：Consumer API、线程安全与动态 Topic)
- [第 10 章：B6 — 生产级可靠性：Offset 管理与重启恢复](#B6 — 生产级可靠性：Offset 管理与重启恢复)
- [第 11 章：C1 — 长任务 REST API 设计模式](#C1 — 长任务 REST API 设计模式)
- [第 12 章：C2 — SSE 实时推送实战指南](#C2 — SSE 实时推送实战指南)
- [第 13 章：D1 — Kafka 重试与死信队列](#D1 — Kafka 重试与死信队列)
- [第 14 章：E1 — SAGA 编排与状态机](#E1 — SAGA 编排与状态机)
- [第 15 章：F1 — Spring Kafka 可观测性：Micrometer 监控](#F1 — Spring Kafka 可观测性：Micrometer 监控)
- [第 16 章：G1 — 调度方案全景对比：Quartz vs @Scheduled vs MQ](#G1 — 调度方案全景对比：Quartz vs @Scheduled vs MQ)

---



---

# 卷首：MECE 知识体系概览与阅读路线

# Spring Boot + Kafka 实时跟踪长时间运行任务 — MECE 知识体系

> 引子文章：[Spring Boot + Kafka，实时跟踪长时间运行任务](./00-original-wechat-article.md)（程序猿DD / SpringBoot实战案例锦集）
> 原文：<https://mp.weixin.qq.com/s/ibxkVE2ButhJPtUJ8txJ4A>
> Spring Boot 3.5.0 + Kafka 实现异步长时间任务进度跟踪（轮询 API 方案）

---

## 七大维度详解

### A — 异步任务执行基础

> 引子文章用了 @Async + ThreadPoolTaskExecutor，但未深入线程池配置。本维度补全异步执行底层知识。

| # | 文章 | 来源 | 关键内容 |
|---|------|------|---------|
| A1 | [Custom Thread Pools for Async Processing](./A1-async-threadpool-custom-obregeon.md) | Medium / Alexander Obregon | ThreadPoolTaskExecutor 的 core/max/queue 配置，AsyncConfigurer 实现，RejectedExecutionHandler 选择 |
| A2 | [Optimizing Async: A Comprehensive Guide](./A2-async-threadpool-comprehensive-devto.md) | Dev.to / Jacky | 线程池参数对 CPU/RAM 的影响，实践调参指南 |
| A3 | [Spring Boot Task Execution & Scheduling 官方文档](./A3-async-threadpool-official-springio.md) | docs.spring.io | Spring Boot 3.x 自动配置的 AsyncTaskExecutor 行为，与 Spring MVC/WebFlux/WebSocket/JPA 的交互 |

**最佳实践要点**：
- 始终自定义 ThreadPoolTaskExecutor，不要依赖默认（无界队列）
- corePoolSize 设 CPU 核心数~2×核心数，maxPoolSize 视峰值
- QueueCapacity 控制背压，避免 OOM
- 通过 AsyncConfigurer 实现集中管理
- Spring Boot 3.2+ 支持 Virtual Thread（SimpleAsyncTaskExecutor）
- 注意 @Async 的 self-invocation 陷阱（AOP 代理失效）

---

### B — 消息队列集成深度

> 引子文章使用了 Kafka 生产-消费模式，本维度深入 Kafka 集成细节，并提供 RabbitMQ 对比。

| # | 文章 | 来源 | 关键内容 |
|---|------|------|---------|
| B1 | [REST API for Long-Running Tasks](./B1-kafka-rest-api-long-tasks-howtodoinjava.md) | howtodoinjava | Spring Boot Kafka 进度追踪 REST API：TaskStatus 模型、KafkaTemplate 生产者、@KafkaListener 消费者、轮询端点 |
| B2 | [Dealing with Long-Running Jobs Using Kafka](./B2-kafka-long-running-jobs-codex-medium.md) | Medium / Codex | Kafka 流式处理长任务架构：分区策略、消费者组协调、进度事件设计 |
| B3 | [Async Messaging Patterns: Kafka vs RabbitMQ](./B3-kafka-vs-rabbitmq-patterns-thecodeforge.md) | TheCodeForge | 异步消息模式全面对比：Pub/Sub、Fire-and-Forget、Request-Reply、Dead Letter Queue；Kafka vs RabbitMQ 选型决策树 |
| **B4** | [KRaft + Docker + Kafka-UI 环境搭建](./B4-kafka-kraft-docker-kafka-ui-setup.md) | 实战总结 | ✅ 匹配引子文章：Docker Kafka KRaft 安装、Kafka-UI 配置、逐行参数解析、多节点部署 |
| **B5** | [底层 Consumer API、线程安全与动态 Topic](./B5-spring-kafka-consumer-raw-api-thread-safety.md) | Spring Kafka Docs / 实战 | ✅ 匹配引子文章：原始 KafkaConsumer vs @KafkaListener 三层 API、线程安全问题（ConcurrentModificationException）、AdminClient 动态 Topic 创建、Json 序列化、单任务一个 Topic 的架构权衡 |
| **B6** | [Offset 管理与重启恢复](./B6-kafka-offset-restart-recovery.md) | 实战总结 | ✅ 匹配引子文章：重启后数据丢失根因分析（H2 内存 + offset 未提交）、4 种修复方案、compact topic、Idempotent Consumer |

**最佳实践要点**：
- 使用 String 或 Avro/Protobuf 序列化，避免 Java 序列化
- Producer: 启用 `acks=all`, `enable.idempotence=true`
- Consumer: 使用 `@Transactional` + `AckMode.MANUAL_IMMEDIATE` 保证 exactly-once
- 为每个消费者组指定独立 `group.id`
- 合理设置 `concurrency`（分区数 ≤ 消费者数）
- 生产环境避免 `KafkaConsumer` 底层 API（线程不安全），优先 `@KafkaListener`
- 重启恢复设计：compact topic + earliest offset + Idempotent Consumer

---

### C — 实时推送 vs 轮询

> 引子文章采用 REST 轮询获取任务进度。本维度探讨更实时推送方案。

| # | 文章 | 来源 | 关键内容 |
|---|------|------|---------|
| C1 | [REST API Design for Long-Running Tasks](./C1-rest-api-design-long-tasks-restfulapi.md) | restfulapi.net | 长任务 REST API 设计模式：异步响应 202 Accepted、Location header 轮询、回调 URL、Webhook 模式 |
| C2 | [SSE in Spring Boot: A Practical Guide](./C2-sse-spring-boot-obregon-medium.md) | Medium / Alexander Obregon | SseEmitter 实现、WebSocket vs SSE vs Polling 对比、自动重连、事件类型设计 |

**方案对比**：

| 方案 | 通信方向 | 复杂度 | 适用场景 |
|------|---------|--------|---------|
| 轮询 (Polling) | 客户端驱动 | 低 | 低频度检查，非实时要求 |
| SSE | 服务端→客户端 | 中 | 单向实时推送，任务进度更新 |
| WebSocket | 双向 | 高 | 双向通信需求，复杂交互 |
| 回调/Webhook | 服务端→服务端 | 中 | 异步任务完成后通知 |

---

### D — 生产级错误处理与重试

> 引子文章未涉及错误处理。本维度聚焦 Kafka 故障恢复与重试机制。

| # | 文章 | 来源 | 关键内容 |
|---|------|------|---------|
| D1 | [Kafka Retry & DLT in Spring Boot](./D1-kafka-retry-dlt-spring-boot-medium.md) | Medium / MoshDev | @RetryableTopic 注解使用、@DltHandler 实现、退避策略（Fixed/Fixed/ExponentialBackOff）、死信队列管理 |

**最佳实践要点**：
- 使用 `@RetryableTopic` + `@DltHandler` 处理消费失败
- 设置指数退避，避免重试风暴
- 区分可重试（临时网络故障）与不可重试（数据格式错误）
- DLQ 消息需要手动处理/监控报警
- 结合 `DefaultErrorHandler` / `CommonErrorHandler` 做全局兜底

---

### E — 任务编排与状态机

> 引子文章使用简单的 TaskStatus 枚举。本维度扩展到复杂工作流编排。

| # | 文章 | 来源 | 关键内容 |
|---|------|------|---------|
| E1 | [SAGA Orchestration with Spring State Machine + Kafka](./E1-saga-orchestration-state-machine-substack.md) | Substack / CodeExperts | SAGA 编排模式、Spring Statemachine 实现、事件驱动补偿事务、Kafka 作为事件总线 |

**架构演进路径**：
1. 简单枚举状态 → 2. 状态机（允许更复杂流转） → 3. SAGA 模式（跨服务分布式事务） → 4. 编排工作流（Temporal/Camunda）

---

### F — 可观测性与监控

> 引子文章未涉及监控。本维度聚焦 Kafka 消费者指标与链路追踪。

| # | 文章 | 来源 | 关键内容 |
|---|------|------|---------|
| F1 | [Spring Kafka Metrics with Micrometer](./F1-kafka-metrics-micrometer-javacodegeeks.md) | JavaCodeGeeks | Micrometer Observation 集成、KafkaConsumerMetrics、Consumer Lag 监控、Prometheus/Grafana 配置 |

**关键指标**：
- `kafka.consumer.fetch.manager.records.lag` — 消费堆积
- `kafka.consumer.fetch.manager.records.consumed.total` — 消费速率
- `kafka.producer.outgoing.byte.total` — 生产流量
- Micrometer + MicrometerTracing 实现分布式追踪

---

### G — 调度方案全景对比

> 全景式了解 Spring Boot 中所有后台任务调度方式的适用场景。

| # | 文章 | 来源 | 关键内容 |
|---|------|------|---------|
| G1 | [Quartz vs @Scheduled vs Message Queues](./G1-background-jobs-quartz-vs-scheduled-vs-mq.md) | Medium / Turkcell | 三种调度方案的功能矩阵对比、选型决策框架 |

**决策框架**：
- 简单定时任务 → `@Scheduled` + `@Async`
- 需要持久化/集群/CRON 表达式 → Quartz
- 需要异步编排/解耦 → Kafka/RabbitMQ
- 复杂工作流 → 考虑 Temporal/Camunda

---

## 阅读路线推荐

```
入门篇（有引子文章基础）
├── B1 → Kafka REST API 进度追踪（与引子互补）
├── A1 → 线程池配置最好实践
└── C2 → SSE 实时推送替代轮询

进阶篇
├── D1 → 重试与死信队列（生产必备）
├── F1 → Micrometer 监控（生产必备）
└── B3 → Kafka vs RabbitMQ 选型

高级篇
├── E1 → Saga 编排与状态机
├── C1 → REST API 长任务设计模式
└── G1 → 调度方案全景对比
```

---

> 创建日期: 2026-06-26
> 收集自：Medium、Dev.to、howtodoinjava、restfulapi.net、TheCodeForge、JavaCodeGeeks、Substack、Spring 官方文档、Turkcell Engineering、Apache Kafka 官方文档

---

## 附：引子文章知识点覆盖检查

以下是对照 [00-original-wechat-article.md](./00-original-wechat-article.md) 的完全覆盖检查：

| # | 引子文章知识点 | 覆盖文章 | 覆盖情况 |
|---|---------------|---------|---------|
| 1 | @Async 异步方法 | A1, A2, A3 | ✅ 深入覆盖 |
| 2 | Kafka 生产者 `KafkaTemplate.send()` | B1, B2 | ✅ 深入覆盖 |
| 3 | Kafka 消费者模式（`@KafkaListener`） | B1, B2 | ✅ 深入覆盖 |
| 4 | 轮询 REST API 查进度 | C1, C2 | ✅ 深入覆盖 |
| 5 | Task 数据模型设计 | B1 | ✅ 等效 |
| 6 | UUID taskId | B1 | ✅ 等效 |
| 7 | 状态枚举 SUBMITTED→STARTED→RUNNING→FINISHED | E1 | ✅ 更深入（状态机） |
| **8** | **Docker KRaft 安装 Kafka** | **B4** | ✅ **新增覆盖** |
| **9** | **Kafka-UI 安装配置** | **B4** | ✅ **新增覆盖** |
| **10** | **序列化配置细节（JsonSerializer/Deserializer/trusted packages）** | **B5** | ✅ **新增覆盖** |
| **11** | **原始 `KafkaConsumer` 手动 poll 模式** | **B5** | ✅ **新增覆盖（三层 API 对比）** |
| **12** | **KafkaConsumer 线程不安全（ConcurrentModificationException）** | **B5** | ✅ **新增覆盖** |
| **13** | **AdminClient 动态创建 Topic** | **B5** | ✅ **新增覆盖** |
| **14** | **每条任务一个 Topic 的架构权衡** | **B5** | ✅ **新增覆盖（含 3 种替代方案）** |
| **15** | **重启后数据丢失 + offset 恢复** | **B6** | ✅ **新增覆盖** |
| **16** | **H2 内存数据库局限** | **B6** | ✅ **新增覆盖** |
| 17 | UriComponentsBuilder 构建 URL | (Spring MVC 知识) | 基础 Spring 知识，不需独立文章 |
| 18 | 错误处理 | D1 | ✅ 深度覆盖 |
| 19 | 可观测性/监控 | F1 | ✅ 深度覆盖 |
| 20 | 调度方案 | G1 | ✅ 全景覆盖 |

**修复前覆盖 7/20 → 修复后覆盖 20/20** 🎉


---

# 第 1 章：引子文章 — Spring Boot + Kafka 实时跟踪长时间运行任务

# Spring Boot + Kafka，实时跟踪长时间运行任务

> **来源：** [mp.weixin.qq.com](https://mp.weixin.qq.com/s/ibxkVE2ButhJPtUJ8txJ4A)
> **作者：** Spring Boot 实战案例锦集（程序猿DD）
> **收录维度：** 引子文章 — 本知识体系的源起
> **保存日期：** 2026-06-26

---

**《Spring Boot 3实战案例锦集》PDF 电子书已更新至 130 篇！**
**《Spring Boot实战案例合集》目前已更新 231 个案例**

> 环境：Spring Boot 3.5.0

## 1. 简介

长时间运行的任务是指需要消耗大量服务器资源和/或时间的操作。为了避免阻塞客户端，任务必须以异步方式完成，且客户端与服务器之间不需要保持持久连接。在提交任务后，客户端需要轮询一个提供的 URL 来获取任务的执行进度。

在本篇文章中，我们将基于 Kafka（作为高吞吐量的分布式消息队列）充当任务进度信息传输的桥梁。通过将长时间运行任务异步化处理，避免客户端阻塞。任务执行过程中，服务器将进度信息实时发布到 Kafka 主题，客户端按需轮询特定接口获取进度，实现实时、可靠的任务跟踪，提升用户体验与系统稳定性。

## 2. 实战案例

### 2.1 环境准备

**Docker 安装 Kafka（KRaft 模式，无需 ZooKeeper）：**

```bash
docker run -d \
  --name kafka \
  --ulimit nofile=65536:65536 \
  -e TZ=Asia/Shanghai \
  -e KAFKA_ENABLE_KRAFT=yes \
  -e KAFKA_CFG_NODE_ID=0 \
  -e KAFKA_CFG_PROCESS_ROLES=controller,broker \
  -e KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@127.0.0.1:9093 \
  -e KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
  -e KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
  -e KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT \
  -e KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER \
  -p 9092:9092 \
  --memory=512m \
  --cpus="1.0" \
  bitnami/kafka
```

**安装 Kafka-UI：**

```bash
docker run -d \
  --name kafka-ui \
  -e KAFKA_CLUSTERS_0_NAME=kraft-kafka \
  -e KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS=localhost:9092 \
  -e DYNAMIC_CONFIG_ENABLED=true \
  -p 8080:8080 \
  provectuslabs/kafka-ui
```

**应用配置：**

```yaml
spring:
  kafka:
    bootstrap-servers:
      - localhost:9092
    consumer:
      group-id: task-group
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      auto-offset-reset: earliest
      properties:
        '[spring.json.trusted.packages]': '*'
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
      properties:
        '[spring.json.trusted.packages]': '*'
```

### 2.2 定义数据模型

**任务状态：**

```java
public record TaskStatus(
    String taskId,
    String taskName,
    float percentageComplete,
    Status status,
    String resultUrl) {

    public enum Status {
        SUBMITTED, STARTED, RUNNING, FINISHED, TERMINATED
    }
}
```

**任务请求对象：**

```java
public record TaskRequest(String name) { }
```

### 2.3 生产者/消费者服务

**生产者：**

```java
@Service
public class KafkaProducerService {
    private final Logger logger = LoggerFactory.getLogger(KafkaProducerService.class);
    private final KafkaTemplate<String, TaskStatus> kafkaTemplate;

    public KafkaProducerService(KafkaTemplate<String, TaskStatus> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void send(String topicName, String key, TaskStatus value) {
        var future = kafkaTemplate.send(topicName, key, value);
        future.whenComplete((sendResult, exception) -> {
            if (exception != null) {
                future.completeExceptionally(exception);
            } else {
                future.complete(sendResult);
            }
            logger.info("Task status send to Kafka topic: " + value);
        });
    }
}
```

**消费者：**

```java
@Service
public class KafkaConsumerService {
    private final Logger logger = LoggerFactory.getLogger(KafkaConsumerService.class);
    private final KafkaConsumer<String, TaskStatus> kafkaConsumer;

    public KafkaConsumerService(KafkaConsumer<String, TaskStatus> kafkaConsumer) {
        this.kafkaConsumer = kafkaConsumer;
    }

    public TaskStatus getLatestTaskStatus(String taskId) {
        ConsumerRecord<String, TaskStatus> latestUpdate = null;
        // KafkaConsumer 不是线程安全的，如果上一次调用没有结束，
        // 其它线程再访问将会出现 ConcurrentModificationException
        ConsumerRecords<String, TaskStatus> consumerRecords =
            kafkaConsumer.poll(Duration.ofMillis(200));

        if (!consumerRecords.isEmpty()) {
            Iterator<ConsumerRecord<String, TaskStatus>> it =
                consumerRecords.records(taskId).iterator();
            while (it.hasNext()) {
                latestUpdate = it.next();
            }
            logger.info("任务【{}】执行状态: {}", taskId, latestUpdate.value());
        }
        return latestUpdate != null ? latestUpdate.value() : null;
    }
}
```

### 2.4 异步任务服务

```java
@Service
public class TaskService {

    private final KafkaConsumer<String, TaskStatus> kafkaConsumer;
    private final KafkaProducerService kafkaProducerService;
    private final KafkaAdmin kafkaAdmin;

    @Async
    public void process(String taskId, TaskRequest taskRequest, UriComponentsBuilder b) {
        try {
            createNewTopic(taskId);
            updateTaskExecutionProgess(new TaskStatus(
                taskId, taskRequest.name(), 0.0f, Status.SUBMITTED, null));

            Thread.sleep(2000l);
            updateTaskExecutionProgess(new TaskStatus(
                taskId, taskRequest.name(), 10.0f, Status.STARTED, null));

            Thread.sleep(5000l);
            float progress = 10.0f;
            for (int i = 0; i < 10; i++) {
                TimeUnit.MILLISECONDS.sleep(new Random().nextLong(4000));
                progress += new Random().nextInt(9);
                updateTaskExecutionProgess(new TaskStatus(
                    taskId, taskRequest.name(), progress, Status.RUNNING, null));
            }

            UriComponents resultURL = b.path("/tasks/{id}/result")
                .buildAndExpand(taskId);
            updateTaskExecutionProgess(new TaskStatus(
                taskId, taskRequest.name(), 100.0f, Status.FINISHED,
                resultURL.toUriString()));

        } catch (InterruptedException | ExecutionException e) {
            updateTaskExecutionProgess(new TaskStatus(
                taskId, taskRequest.name(), 100.0f, Status.TERMINATED, null));
            throw new RuntimeException(e);
        }
    }

    private void createNewTopic(String topicName)
            throws ExecutionException, InterruptedException {
        Map<String, String> topicConfig = new HashMap<>();
        topicConfig.put(TopicConfig.RETENTION_MS_CONFIG,
            String.valueOf(24 * 60 * 60 * 1000)); // 保留24小时

        NewTopic newTopic = new NewTopic(topicName, 1, (short) 1)
            .configs(topicConfig);
        try (AdminClient adminClient =
                AdminClient.create(kafkaAdmin.getConfigurationProperties())) {
            adminClient.createTopics(Collections.singletonList(newTopic))
                .all().get();
        }
        kafkaConsumer.subscribe(Collections.singletonList(topicName));
    }

    private void updateTaskExecutionProgess(TaskStatus taskStatus) {
        kafkaProducerService.send(
            taskStatus.taskId(), taskStatus.taskId(), taskStatus);
    }
}
```

> 注意：每次调用 process 都会创建一个新的 Topic。

**KafkaConsumer Bean 定义：**

```java
@Configuration
public class KafkaConfig {

    @Bean
    KafkaConsumer<String, TaskStatus> kafkaConsumer(
            ConsumerFactory<String, TaskStatus> consumerFactory) {
        return (KafkaConsumer<String, TaskStatus>) consumerFactory.createConsumer();
    }
}
```

### 2.5 Controller 接口

```java
@RestController
@RequestMapping("/tasks")
public class TaskController {

    private final TaskService taskService;
    private final KafkaConsumerService kafkaConsumerService;

    @GetMapping
    public ResponseEntity<String> processAsync(
            TaskRequest task, UriComponentsBuilder b) {
        String taskId = UUID.randomUUID().toString().replace("-", "");
        UriComponents progressURL = b.path("/tasks/{id}/progress")
            .buildAndExpand(taskId);
        taskService.process(taskId, task, b.cloneBuilder());
        return ResponseEntity.ok("任务进度查看地址: " + progressURL.toUriString());
    }

    @GetMapping("{taskId}/progress")
    public ResponseEntity<?> processAsync(@PathVariable String taskId) {
        TaskStatus taskStatus = kafkaConsumerService.getLatestTaskStatus(taskId);
        if (taskStatus == null) {
            return ResponseEntity.ok("");
        }
        return ResponseEntity.ok().body(taskStatus);
    }
}
```

### 2.6 测试

1. **创建任务** — 调用 `GET /tasks` 返回进度查看地址
2. **查看任务进度** — 轮询 `GET /tasks/{taskId}/progress`
   - 运行中：返回当前进度百分比
   - 任务完成：返回 `FINISHED` 状态和结果 URL
3. **通过 Kafka-UI** 查看该任务 topic 产生的消息

> ⚠️ 注意：当你重启了服务以后，是无法再获取进度信息的，你需要特殊处理。

---

## 知识体系索引

本文章是本知识体系的引子。完整的 MECE（Mutually Exclusive, Collectively Exhaustive）七维框架，请参阅同目录下的 [README.md](README.md)：

| 维度 | 内容 | 文件 |
|------|------|------|
| A — 异步执行基础 | ThreadPoolTaskExecutor, @Async | `A1-*`, `A2-*`, `A3-*` |
| B — Kafka 集成深度 | 生产者/消费者模式, 选型, 环境搭建, 底层 API, Offset 管理 | `B1-*` ~ `B6-*` |
| C — 实时推送 | SSE 替代轮询 | `C1-*`, `C2-*` |
| D — 错误处理 | Retry, DLT | `D1-*` |
| E — 任务编排 | Saga, 状态机 | `E1-*` |
| F — 可观测性 | Micrometer, 监控 | `F1-*` |
| G — 调度方案 | Quartz, @Scheduled, MQ | `G1-*` |

> B4-B6 是新增的底层覆盖，专门匹配本文章的 Docker、底层 Consumer API、线程安全和重启恢复问题。

---

> 保存日期：2026-06-26
> 关键要点：每条任务创建一个独立 Kafka Topic，任务执行过程通过 Kafka 发送进度事件，客户端通过轮询获取最新状态
> 局限性：重启后进度丢失（详见 [B6](./B6-kafka-offset-restart-recovery.md)）、每条任务一个 Topic 可能变成 Topic 爆炸（详见 [B5 §4](./B5-spring-kafka-consumer-raw-api-thread-safety.md)）、KafkaConsumer 非线程安全需注意（详见 [B5 §3](./B5-spring-kafka-consumer-raw-api-thread-safety.md)）


---

# 第 2 章：A1 — 自定义线程池异步处理

# Spring Boot Custom Thread Pools for Async Processing

> 来源：Medium / Alexander Obregon
> 原文：[How Spring Boot Configures Custom Thread Pools for Async Processing](https://medium.com/@AlexanderObregon/how-spring-boot-configures-custom-thread-pools-for-async-processing-2f05d6fb3e42)
> 收录维度：**A — 异步任务执行基础**

---

## 1. @Async 基础

`@EnableAsync` 开启异步支持后，Spring Boot 自动配置 `ThreadPoolTaskExecutor`。

默认配置（Spring Boot 自动配置）：
- Core Pool Size: 8
- Max Pool Size: Integer.MAX_VALUE
- Queue Capacity: Integer.MAX_VALUE (无界)
- Keep Alive: 60s

⚠️ **默认配置的陷阱**：无界队列意味着 maxPoolSize 永远不会生效——任务会一直排队，不会创建超过 corePoolSize 的线程。

## 2. 自定义 ThreadPoolTaskExecutor

```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {

    @Override
    @Bean(name = "asyncExecutor")
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);          // 核心线程数
        executor.setMaxPoolSize(10);          // 最大线程数
        executor.setQueueCapacity(25);        // 队列容量
        executor.setThreadNamePrefix("async-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();
        return executor;
    }
}
```

### 参数关系（关键理解）

当任务提交时，ThreadPoolTaskExecutor 的行为：
1. 线程数 < corePoolSize → 创建新线程执行
2. 线程数 ≥ corePoolSize → 任务入队列
3. 队列满且线程数 < maxPoolSize → 创建新线程
4. 队列满且线程数 ≥ maxPoolSize → 触发拒绝策略

**所以：如果 QueueCapacity 很大（如默认无界），maxPoolSize 几乎没有意义。**

## 3. 拒绝策略 (RejectedExecutionHandler)

| 策略 | 行为 | 适用场景 |
|------|------|---------|
| AbortPolicy (默认) | 抛出 RejectedExecutionException | 必须保证任务不丢失时告警 |
| CallerRunsPolicy | 调用者线程直接运行任务 | 自然背压，降低任务提交速度 |
| DiscardPolicy | 静默丢弃 | 非关键任务 |
| DiscardOldestPolicy | 丢弃最旧任务 | 优先处理最新任务 |

**推荐**：`CallerRunsPolicy` 对长时间运行任务最友好——让上游感知压力。

## 4. 自定义 ThreadPoolTaskExecutor 的 Bean 命名

- 命名 `@Bean("taskExecutor")` → 被 Spring Boot 自动发现，替换默认 executor
- 命名其他名称 → 需要在 `@Async("asyncExecutor")` 中显式指定

**注意**：Spring MVC 使用名为 `applicationTaskExecutor` 的 bean。如果覆盖了 `taskExecutor`，Spring MVC 的异步请求不受影响。

## 5. 安全上下文传播

如果异步任务需要访问 SecurityContext，需要自定义 TaskDecorator：

```java
public class ContextCopyingDecorator implements TaskDecorator {
    @Override
    public Runnable decorate(Runnable runnable) {
        RequestAttributes context = RequestContextHolder.currentRequestAttributes();
        return () -> {
            try {
                RequestContextHolder.setRequestAttributes(context);
                runnable.run();
            } finally {
                RequestContextHolder.resetRequestAttributes();
            }
        };
    }
}

// 在 executor 上设置
executor.setTaskDecorator(new ContextCopyingDecorator());
```

同样可以用于传播 SecurityContext、MDC（日志追踪 ID）等。

## 6. CompletableFuture 进阶

```java
@Service
public class TaskService {
    @Async
    public CompletableFuture<TaskResult> processTask(String taskId) {
        // 长期运行任务
        return CompletableFuture.completedFuture(new TaskResult(taskId, "done"));
    }
}

// 组合多个异步任务
CompletableFuture<TaskResult> future1 = taskService.processTask("task-1");
CompletableFuture<TaskResult> future2 = taskService.processTask("task-2");
CompletableFuture.allOf(future1, future2).join();
```

## 7. 异常处理

```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {
    @Override
    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
        return (ex, method, params) -> {
            System.err.println("Async error in " + method.getName() + ": " + ex.getMessage());
            // 报警、记录日志、发送到死信队列等
        };
    }
}
```

**注意**：只有返回 void 的 `@Async` 方法会走这个 handler；返回 Future/CompletableFuture 的异常由调用方处理。

---

## 最佳实践总结

1. **永远自定义线程池**，不依赖默认（无界队列风险）
2. **队列容量设合理值**（几十~几百），让 maxPoolSize 生效
3. **使用 CallerRunsPolicy** 作为生产环境拒绝策略
4. **传播上下文**（RequestAttributes、SecurityContext、MDC）
5. **为不同业务创建不同线程池**，避免互相影响
6. **监控线程池**（Micrometer 的 `executor.*` 指标）


---

# 第 3 章：A2 — 异步线程池优化全面指南

# Optimizing Spring Boot Async: Thread Pool Configuration Guide

> 来源：Dev.to / Jacky
> 原文：[Optimizing Spring Boot Asynchronous Processing: A Comprehensive Guide](https://dev.to/jackynote/optimizing-spring-boot-asynchronous-processing-a-comprehensive-guide-147h)
> 收录维度：**A — 异步任务执行基础**

---

## 核心概念

### Core Pool Size（核心线程数）
- 保持活动的线程数量（即使空闲）
- **CPU 影响**：越大并发越高，CPU 利用率越高
- **内存影响**：每个线程占用栈空间，核心数越大内存消耗越多
- **选值建议**：
  - 短频任务 → 较大的 corePoolSize
  - 长任务 → 注意不要过度预留线程

### Maximum Pool Size（最大线程数）
- 线程池允许创建的线程上限（含活跃+空闲）
- **什么时候生效**：核心线程全忙 + 队列满 → 创建额外线程
- **选值建议**：
  - 根据峰值负载估算
  - 设置过低 → 任务排队积压
  - 设置过高 → 资源耗尽

### Task Queue Capacity（任务队列容量）
- 当所有核心线程忙时，任务先入队列等待
- **内存影响**：队列中每个待执行任务占用内存
- **选值建议**：
  - 根据预期峰值任务的到达速率 × 处理时间估算
  - 队列太小 → 高峰时频繁触发拒绝策略
  - 队列太大 → 内存压力 + 响应延迟

### 三者配合关系

```
提交任务 → 线程 < core? → 创建新线程执行
         → 线程 ≥ core? → 入队列等待
                        → 队列满 → 线程 < max? → 创建新线程
                                → 队列满 → 线程 ≥ max? → 拒绝策略
```

## 实践示例

```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {

    @Override
    @Bean(name = "asyncExecutor")
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(3);      // 核心 3 个线程
        executor.setMaxPoolSize(10);      // 最多 10 个线程
        executor.setQueueCapacity(25);    // 队列 25 个位置
        executor.setThreadNamePrefix("custom-async-");
        executor.initialize();
        return executor;
    }
}

@Service
public class YourService {
    @Async
    public void performAsyncTask() {
        System.out.println("Async task executed in thread: " +
            Thread.currentThread().getName());
    }
}
```

## 调优建议

- **监控优先**：上线前做好指标采集（active count, queue size, rejected count）
- **从合理默认值开始**：core=4, max=8, queue=50，观察后调整
- **区分 I/O 密集型 vs CPU 密集型**：
  - CPU 密集型：core = CPU 核心数
  - I/O 密集型：core = CPU 核心数 × 2（或更高）
- **避免频繁调整**：每次改一个参数，观察稳定后继续

## 常见陷阱

1. **无界队列**：queueCapacity=Integer.MAX_VALUE → maxPoolSize 永不生效
2. **线程数设置过大**：上下文切换开销吞噬性能
3. **忽略拒绝策略**：生产环境一定设置拒绝策略
4. **不监控**：不知道线程池处于什么状态


---

# 第 4 章：A3 — Spring Boot Task Execution 官方文档

# Spring Boot Task Execution & Scheduling 官方文档摘录

> 来源：[docs.spring.io](https://docs.spring.io/spring-boot/reference/features/task-execution-and-scheduling.html) (Spring Boot 3.x 参考文档)
> 收录维度：**A — 异步任务执行基础**

---

## 1. 自动配置的 AsyncTaskExecutor

当上下文中没有 `Executor` bean 时，Spring Boot 自动配置一个 `AsyncTaskExecutor`：

- **Virtual Thread 启用时**（Java 21+ + `spring.threads.virtual.enabled=true`）
  → `SimpleAsyncTaskExecutor`（每个任务一个虚拟线程）

- **其他情况** → `ThreadPoolTaskExecutor`（带合理的默认值）

## 2. 自动配置 Executor 的使用场景

`AsyncTaskExecutor` 被以下集成使用（除非自定义 `Executor` bean）：

| 场景 | 说明 |
|------|------|
| `@EnableAsync` 异步任务 | `@Async` 方法执行 |
| Spring MVC `Callable` 返回值 | 控制器异步请求处理 |
| Spring GraphQL 异步处理 | Callable 返回值 |
| Spring WebFlux 阻塞执行 | 阻塞操作支持 |
| Spring WebSocket 消息通道 | 入站/出站通道 |
| JPA 启动执行器 | 基于 JPA 仓库的启动模式 |
| ApplicationContext 后台初始化 | Bean 的异步加载 |

## 3. 自定义 Executor 的行为规则

### 规则一：自定义 `Executor` bean → 自动配置退避

```java
@Bean(name = "taskExecutor")
public Executor taskExecutor() {
    return new ThreadPoolTaskExecutor();
}
```

注册自定义 `Executor` 后，自动配置的 `AsyncTaskExecutor` 退避，自定义 executor 用于 `@EnableAsync` 常规任务执行。

### 规则二：Spring MVC/WebFlux/GraphQL 需要 `applicationTaskExecutor` bean

Spring MVC、WebFlux、GraphQL 都要求一个名为 `applicationTaskExecutor` 的 `AsyncTaskExecutor`。

```java
@Bean("applicationTaskExecutor")
SimpleAsyncTaskExecutor applicationTaskExecutor() {
    return new SimpleAsyncTaskExecutor("app-");
}
```

### 规则三：多 Executor 共存

```java
@Bean("applicationTaskExecutor")
SimpleAsyncTaskExecutor applicationTaskExecutor() {
    return new SimpleAsyncTaskExecutor("app-");
}

@Bean("taskExecutor")
ThreadPoolTaskExecutor taskExecutor() {
    ThreadPoolTaskExecutor tpte = new ThreadPoolTaskExecutor();
    tpte.setThreadNamePrefix("async-");
    return tpte;
}
```

- `applicationTaskExecutor` → Spring MVC, WebFlux, WebSocket, JPA, 后台初始化
- `taskExecutor` → `@EnableAsync` 常规任务执行

### 规则四：`@Primary` 和 `AsyncConfigurer`

如果不想用 `taskExecutor` 名称，可以用 `@Primary` 标注或定义 `AsyncConfigurer`：

```java
@Bean
AsyncConfigurer asyncConfigurer(ExecutorService executorService) {
    return new AsyncConfigurer() {
        @Override
        public Executor getAsyncExecutor() {
            return executorService;
        }
    };
}
```

### 规则五：`defaultCandidate=false` 保留自动配置

想自定义 Executor 又保留自动配置的 AsyncTaskExecutor 给其他集成用：

```java
@Bean(defaultCandidate = false)
@Qualifier("scheduledExecutorService")
ScheduledExecutorService scheduledExecutorService() {
    return Executors.newSingleThreadScheduledExecutor();
}
```

### 规则六：`spring.task.execution.mode=force` 强制保留自动配置

即使有自定义 Executor（含 `@Primary`），仍然强制使用自动配置的 `AsyncTaskExecutor`：

```yaml
spring:
  task:
    execution:
      mode: force
```

## 4. 使用 `SimpleAsyncTaskExecutorBuilder` / `ThreadPoolTaskExecutorBuilder`

Spring Boot 提供 builder 方便构造：

```java
@Bean
SimpleAsyncTaskExecutor taskExecutor(SimpleAsyncTaskExecutorBuilder builder) {
    return builder.build();
}
```

## 最佳实践

1. **明确你的 `Executor` 命名策略**，理解各个集成用哪个
2. **区分 `applicationTaskExecutor` 和 `taskExecutor`**，两者用途不同
3. **Virtual Thread 场景**：Java 21+ 启用 `spring.threads.virtual.enabled=true`
4. **复杂场景使用独立命名**，避免命名冲突导致意外行为


---

# 第 5 章：B1 — REST API + Kafka 长时间任务进度追踪

# REST API for Long-Running Tasks with Spring Boot + Kafka

> 来源：howtodoinjava.com
> 原文：[Spring Boot REST API for Long Running Tasks](https://howtodoinjava.com/spring-boot/rest-api-for-long-running-tasks/)
> 收录维度：**B — 消息队列集成深度**

---

## 概述

本文演示了 Spring Boot REST API 配合 Kafka 跟踪长时间运行任务的进度，与引子文章思路一致。

## 架构设计

```
客户端 → POST /api/tasks → Controller → TaskService.submit()
                                     → KafkaTemplate.send(progress)
                                     → @KafkaListener 更新 DB
                                     → GET /api/tasks/{id} 查询状态
```

- 客户端提交任务 → 获得 taskId
- 后台异步执行 + 通过 Kafka 发送进度事件
- 消费者更新数据库状态
- 客户端轮询查询结果

## 核心实现

### 1. TaskStatus 模型

```java
public enum TaskStatus {
    PENDING, PROCESSING, COMPLETED, FAILED
}

@Entity
public class Task {
    @Id
    private String taskId;
    private TaskStatus status;
    private int progress;       // 0-100
    private String result;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    // getters/setters
}
```

### 2. Kafka 进度事件

```java
public class ProgressEvent {
    private String taskId;
    private TaskStatus status;
    private int progress;
    private String message;
    private LocalDateTime timestamp;
}

@Component
public class TaskProgressProducer {

    @Autowired
    private KafkaTemplate<String, ProgressEvent> kafkaTemplate;

    public void sendProgress(ProgressEvent event) {
        kafkaTemplate.send("task-progress", event.getTaskId(), event);
    }
}
```

### 3. 任务提交端点

```java
@RestController
@RequestMapping("/api/tasks")
public class TaskController {

    @Autowired
    private TaskService taskService;

    @PostMapping
    public ResponseEntity<TaskResponse> submitTask(@RequestBody TaskRequest request) {
        String taskId = taskService.submit(request);
        return ResponseEntity.accepted()
            .header("Location", "/api/tasks/" + taskId)
            .body(new TaskResponse(taskId, TaskStatus.PENDING));
    }

    @GetMapping("/{taskId}")
    public ResponseEntity<Task> getTaskStatus(@PathVariable String taskId) {
        return taskService.findById(taskId)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
}
```

### 4. Kafka 消费者

```java
@Component
public class TaskProgressConsumer {

    @Autowired
    private TaskRepository taskRepository;

    @KafkaListener(topics = "task-progress", groupId = "task-service")
    public void handleProgress(ProgressEvent event) {
        taskRepository.findById(event.getTaskId()).ifPresent(task -> {
            task.setStatus(event.getStatus());
            task.setProgress(event.getProgress());
            task.setUpdatedAt(LocalDateTime.now());
            if (event.getStatus() == TaskStatus.COMPLETED) {
                task.setResult(event.getMessage());
            }
            taskRepository.save(task);
        });
    }
}
```

### 5. 异步任务处理器

```java
@Service
public class TaskProcessor {

    @Async("taskExecutor")
    public CompletableFuture<Void> processTask(String taskId) {
        for (int i = 0; i <= 100; i += 10) {
            // 模拟长时间处理
            Thread.sleep(1000);

            // 发送进度事件
            ProgressEvent event = new ProgressEvent();
            event.setTaskId(taskId);
            event.setStatus(i < 100 ? TaskStatus.PROCESSING : TaskStatus.COMPLETED);
            event.setProgress(i);
            event.setMessage("Processing step " + i/10 + "/10");
            producer.sendProgress(event);
        }
        return CompletableFuture.completedFuture(null);
    }
}
```

## 配置

```yaml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
    consumer:
      group-id: task-service
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      properties:
        spring.json.trusted.packages: "*"
```

## 生产优化建议

1. **使用 Avro/Protobuf** 而不是 JSON 序列化
2. **分区策略**：按 taskId hash 分区，保证同一任务的有序性
3. **消费者并发**：`@KafkaListener(concurrency = "3")` 匹配分区数
4. **错误处理**：配置 `ErrorHandler` / `@RetryableTopic`
5. **超时**：设置合理的 Kafka 生产/消费超时时间
6. **幂等性**：进度事件幂等，消费者多次处理无副作用


---

# 第 6 章：B2 — Kafka 流式长任务处理架构

# Dealing with Long-Running Jobs Using Apache Kafka

> 来源：Medium / Codex
> 原文：[Dealing with Long-Running Jobs Using Apache Kafka](https://medium.com/codex/dealing-with-long-running-jobs-using-apache-kafka-192f053e1691)
> 收录维度：**B — 消息队列集成深度**

---

## 概述

本文从架构角度探讨如何使用 Kafka 处理长时间运行任务的进度跟踪，重点在事件驱动设计和分区策略。

## 核心架构模式

### 事件驱动进度追踪

```
[Job Scheduler] → Kafka Topic "job-events"
                       ↓
              [Job Worker] (consumer group)
                       ↓
              [Progress Reporter] → Kafka Topic "job-progress"
                                        ↓
                              [Status Service] → DB
                                        ↓
                              [Notification] → Client (SSE/WS/Polling)
```

### 关键设计原则

1. **不可变事件日志**：每个进度事件是一次不可变记录，只能追加
2. **一次写入，多次消费**：监控、审计、通知都可以消费同一事件流
3. **有序保证**：分区内有序，同一 job 的 hash key 路由到同一分区
4. **重放能力**：事件日志可重放，重建任意时间点的状态

## 进度事件设计

```json
{
  "eventId": "evt-001",
  "jobId": "job-123",
  "type": "PROGRESS",
  "sequence": 5,
  "timestamp": "2026-06-25T10:30:00Z",
  "data": {
    "progress": 50,
    "phase": "DATA_PROCESSING",
    "message": "Processing batch 5/10"
  }
}
```

### 事件类型分类

| 事件类型 | 说明 | 重要性 |
|----------|------|--------|
| JOB_CREATED | 任务创建 | 高 |
| JOB_STARTED | 开始处理 | 高 |
| PROGRESS | 进度更新（可选频率） | 中 |
| PHASE_CHANGE | 阶段切换 | 高 |
| JOB_COMPLETED | 完成 | 高 |
| JOB_FAILED | 失败 | 高 |
| HEARTBEAT | 心跳保持活跃（防止超时误判） | 低 |

## 分区策略

```java
// 按 jobId hash 分区，保证同一任务事件有序
producer.send(new ProducerRecord<>("job-progress",
    jobId.hashCode() % partitionCount,
    jobId,
    event));
```

### 分区数规划

- **原则**：分区数 ≥ 最大并发消费者数
- **经验**：单分区吞吐 ~1MB/s，根据预估事件量计算
- **分区扩容**：Kafka 支持 topic 扩展分区，但会改变 hash 映射

## 消费者组设计

```
Topic: job-progress (12 partitions)
Consumer Group: job-status-updater
  ├── Consumer-1: partitions 0-3
  ├── Consumer-2: partitions 4-7
  └── Consumer-3: partitions 8-11
```

### 多消费者组的灵活性

```
job-progress topic
  ├── Group: status-updater  → 更新数据库
  ├── Group: monitor         → 监控/报警
  └── Group: notification    → 实时推送客户端
```

## 与 REST API 结合

Kafka 事件流 + REST API 结合：

```java
// 状态服务通过 Kafka Streams 维护物化视图
@Bean
public KStream<String, JobProgress> buildMaterializedView(StreamsBuilder builder) {
    KStream<String, JobProgress> stream = builder
        .stream("job-progress",
            Consumed.with(Serdes.String(), jsonSerde));

    stream.groupByKey()
        .reduce((oldVal, newVal) -> newVal)  // 保留最新进度
        .toStream()
        .to("job-latest-status",
            Produced.with(Serdes.String(), jsonSerde));

    return stream;
}
```

## 生产环境考虑

### 1. 事件膨涨控制

- 进度更新频率太高 → 选择性地发送（如每 5% 一次）
- 使用压缩 (`compression.type=snappy`)
- 设置日志保留期 (`retention.ms=604800000` 7天)

### 2. Exactly-Once 语义

```java
// Producer 端
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
props.put(ProducerConfig.ACKS_CONFIG, "all");

// Consumer 端
@KafkaListener
@Transactional
public void onMessage(ConsumerRecord<String, JobProgress> record) {
    // 处理并写入 DB（与 Kafka 事务绑定）
}
```

### 3. 消费者滞后监控

Kafka Consumer Lag 是最重要的生产指标：
- Lag 持续增长 → 消费者处理能力不足
- Lag 突然增加 → 生产者突发流量
- Lag=0 → 消费者追上生产者

### 4. 反压与限流

进度事件的频率需要设计：
- 太频繁：Consumer Lag 增加，存储压力大
- 太低：客户端体验差
- 建议：固定频率（如每 5 秒），或按百分比步进（每 5%）


---

# 第 7 章：B3 — 异步消息模式：Kafka vs RabbitMQ

# Spring Boot Async Messaging Patterns: Kafka vs RabbitMQ

> 来源：TheCodeForge
> 原文：[Spring Boot Async Messaging Patterns](https://thecodeforge.io/java/spring-boot-async-messaging/)
> 收录维度：**B — 消息队列集成深度**

---

## 概述

全面对比 Kafka 和 RabbitMQ 在 Spring Boot 中实现异步消息的模式差异和选型决策。

## 四种消息模式对比

### 1. Fire-and-Forget（即发即忘）

**适用**：日志、监控事件、非关键通知

**RabbitMQ**：
```java
// Producer
rabbitTemplate.convertAndSend("logs.exchange", "log.info", logEntry);

// Consumer
@RabbitListener(queues = "logs.queue")
public void handleLog(LogEntry log) { ... }
```

**Kafka**：
```java
// Producer
kafkaTemplate.send("logs-topic", logEntry);

// Consumer
@KafkaListener(topics = "logs-topic")
public void handleLog(LogEntry log) { ... }
```

**对比**：RabbitMQ 更适合即发即忘的路由模式（支持通配符 routing key），Kafka 则适合需要长期保存日志事件的场景。

### 2. Pub/Sub（发布/订阅）

**适用**：事件广播、多消费者独立处理

**RabbitMQ**（Fanout Exchange）：
```java
// Producer
rabbitTemplate.convertAndSend("fanout.exchange", "", event);

// Consumer (创建独立匿名队列绑定到 exchange)
@RabbitListener(queues = "#{autoDeleteQueue.name}")
public void handleEvent(Event event) { ... }
```

**Kafka**（Consumer Group）：
```java
// Producer
kafkaTemplate.send("events-topic", event);

// Consumer (每个独立应用使用不同 group.id)
@KafkaListener(topics = "events-topic", groupId = "service-a")
public void handleEvent(Event event) { ... }
```

**对比**：两种都支持 Pub/Sub。RabbitMQ 通过 exchange binding 实现灵活路由，Kafka 通过 consumer group 实现弹性伸缩。

### 3. Request-Reply（请求-回复）

**适用**：RPC 风格需同步等待响应的场景

**RabbitMQ**（原生支持 Direct Reply-to）：
```java
// Producer
Message reply = rabbitTemplate
    .convertSendAndReceive("rpc.queue", request, correlationData);

// Consumer
@RabbitListener(queues = "rpc.queue")
public Response handle(MyRequest request) { ... }
```

**Kafka**（需要额外实现 Correlation ID + Reply Topic）：
```java
// Producer
String replyTopic = "reply-topic";
String correlationId = UUID.randomUUID().toString();
// 在 headers 中设置 correlationId 和 replyTopic
kafkaTemplate.send("request-topic", correlationId, request);

// 等待响应（需要 Listener 消费 reply-topic）
```

**对比**：**RabbitMQ 明显胜出**。Kafka 不是为 RPC 设计的，实现 request-reply 需要更多脚手架。

### 4. Dead Letter Queue（死信队列）

**适用**：消息消费失败后的处理

**RabbitMQ**（DLX - Dead Letter Exchange）：
```java
// 队列绑定 DLX
Map<String, Object> args = new HashMap<>();
args.put("x-dead-letter-exchange", "dlx.exchange");
args.put("x-dead-letter-routing-key", "dlx.routing-key");
Queue queue = new Queue("work.queue", true, false, false, args);
```

**Kafka**（DLT - @DltHandler）：
```java
@RetryableTopic(
    attempts = "4",
    backoff = @Backoff(delay = 1000, multiplier = 2.0))
@KafkaListener(topics = "work-topic")
public void handleMessage(WorkEvent event) { ... }

@DltHandler
public void handleDlt(WorkEvent event) { ... }
```

**对比**：两者都有 DLQ 能力。Kafka 的 `@RetryableTopic` 让重试+DLQ 配置更简洁。

## 选型决策树

```
需要消息跟踪/可溯源性高？
├── 是 → Kafka（不可变日志、重放能力）
└── 否 → 继续判断

需要 RPC / Request-Reply？
├── 是 → RabbitMQ（原生支持 Direct Reply-to）
└── 否 → 继续判断

需要消息持久化保留较长时间？
├── 是 → Kafka（按配置保留，适合审计）
└── 否 → RabbitMQ（ACK 后删除，适合任务队列）

需要复杂路由（Topic/Header Exchange）？
├── 是 → RabbitMQ（灵活 Exchange 绑定）
└── 否 → Kafka（简单 Topic 模型）

吞吐量 > 100k msg/s？
├── 是 → Kafka（顺序写入，高吞吐）
└── 否 → RabbitMQ 完全够用

团队对哪种技术更熟悉？
├── Kafka → Kafka
└── RabbitMQ → RabbitMQ
```

## RabbitMQ 在 Spring Boot 中的效率优化

### 批量发送

```java
@Bean
public BatchingRabbitTemplate batchingRabbitTemplate(
        ConnectionFactory connectionFactory) {
    BatchingStrategy batching = new SimpleBatchingStrategy(
        100,    // batchSize
        1024,   // bufferLimit (bytes)
        10000   // timeout (ms)
    );
    return new BatchingRabbitTemplate(connectionFactory, batching);
}
```

### 消费者并发

```java
@RabbitListener(queues = "work.queue", concurrency = "3-10")
public void handleMessage(WorkEvent event) { ... }
```

## Spring Boot 消息堆栈全景

| 消息类型 | 技术选择 | 场景 |
|----------|---------|------|
| 同步 RPC | gRPC / REST | 低延迟、强一致性 |
| 异步消息 | Kafka / RabbitMQ | 解耦、削峰、事件驱动 |
| 实时推送 | WebSocket / SSE | 浏览器实时更新 |
| 任务调度 | Quartz / @Scheduled | 定时任务、Cron |

## 推荐

- **新项目优先 Kafka**：云原生生态更好，吞吐量高，Spring Boot 3.x 集成完善
- **已有 RabbitMQ 基础设施**：没必要迁移，满足大多数业务场景
- **两者都能用时**：Kafka 适合事件溯源/流式处理，RabbitMQ 适合任务队列/RPC


---

# 第 8 章：B4 — KRaft + Docker + Kafka-UI 环境搭建

# B4 — Kafka 开发环境搭建：KRaft + Docker + Kafka-UI

> **匹配引子文章知识点：** ✅ Docker Kafka 安装 ✅ Kafka-UI 配置 ✅ KRaft 模式
> 来源：Medium / Bitnami 官方文档 / 实战总结
> 收录维度：**B — 消息队列集成深度（环境篇）**

---

## TL;DR

引子文章使用的 `docker run bitnami/kafka` + `KAFKA_ENABLE_KRAFT=yes` 是 Kafka 3.3+ 引入的 **KRaft 模式**（替代 ZooKeeper）。本文章深入这个环境搭建到底做了什么、有什么坑、以及生产部署建议。

---

## 1. 为什么是 KRaft？

Kafka 历史上依赖 ZooKeeper 管理元数据（broker 注册、Topic 分区分配、Controller 选举）。从 Kafka 2.8 开始引入 KRaft（Kafka Raft）模式，用 Kafka 自己的 Raft 共识协议取代 ZooKeeper。

**关键时间线：**
- Kafka 3.3.1（2022-10）→ KRaft 生产可用
- Kafka 3.7（2024-01）→ **最后支持 ZooKeeper 的版本**
- Kafka 4.0 → **彻底移除 ZooKeeper**

也就是说，如果你现在新项目用 Kafka，**应该直接上 KRaft**。

### 架构差异

```
ZooKeeper 模式：         KRaft 模式：
┌──────────┐            ┌──────────────────┐
│ Producer │            │    Producer      │
└────┬─────┘            └──────┬───────────┘
     │                         │
┌────▼──────────┐      ┌──────▼───────────┐
│   Kafka       │      │   Kafka           │
│   Broker      │      │   Broker +        │
│ (Controller)  │      │   Controller      │
└────┬──────────┘      │   (二合一)        │
     │                 └──────────────────┘
┌────▼──────────┐
│   ZooKeeper   │      ❌ 移除
│   Ensemble    │
└───────────────┘
```

**优势**：
- 少部署一个中间件（ZooKeeper 集群通常 3 节点）
- 单节点 Kafka 就能跑，开发调试极简
- Controller 故障恢复从数十秒降到 ~10 秒
- 元数据直接存在 Kafka Topic 里，强一致

**注意**：
- KRaft 的 Controller 和 Broker 可以部署在同一个进程（`PROCESS_ROLES=broker,controller`）或分开
- 开发环境用二合一最方便；生产环境建议分开以隔离职责

---

## 2. 逐行解析引子文章的 Docker 命令

```bash
docker run -d \
  --name kafka \
  --ulimit nofile=65536:65536 \           # 打开文件数限制（Kafka 需要大量 socket）
  -e KAFKA_ENABLE_KRAFT=yes \             # 🔑 启用 KRaft 模式
  -e KAFKA_CFG_NODE_ID=0 \                # 节点的唯一 ID
  -e KAFKA_CFG_PROCESS_ROLES=controller,broker \  # 同时承担 Controller + Broker
  -e KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@127.0.0.1:9093 \  # 选举投票者列表
  -e KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \  # 监听器
  -e KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \  # 客户端连接地址
  -e KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT \
  -e KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER \
  -p 9092:9092 \
  bitnami/kafka
```

### 核心参数详解

| 参数 | 值 | 含义 |
|------|-----|------|
| `KAFKA_ENABLE_KRAFT` | `yes` | 强制 KRaft 模式（Bitnami 镜像的开关） |
| `KAFKA_CFG_PROCESS_ROLES` | `broker,controller` | 单进程同时做数据存储+元数据管理 |
| `KAFKA_CFG_CONTROLLER_QUORUM_VOTERS` | `{id}@{host}:{port}` | 选举集群成员列表；单节点只需一个 |
| `KAFKA_CFG_LISTENERS` | `PLAINTEXT://:9092,CONTROLLER://:9093` | 内部监听分离：9092 数据端口，9093 控制端口 |
| `KAFKA_CFG_ADVERTISED_LISTENERS` | `PLAINTEXT://localhost:9092` | **关键**：告诉客户端连接哪个地址（Docker 内外不一致时容易翻车） |

### ⚠️ Docker 内外网络模式

这是 Kafka Docker 部署的头号坑：

```
容器内部: localhost:9092 → 本容器进程
其他容器: kafka:9092 → Docker 网络别名
宿主机:   localhost:9092 → port mapping
外部机器: <host-ip>:9092 → 需要 external listener
```

引子文章用 `PLAINTEXT://localhost:9092` 在宿主机调试没问题，但如果：
- **其他 Docker 容器**需要连接 → 要加 `EXTERNAL` 监听器：
  ```yaml
  KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093,EXTERNAL://:9094
  KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092,EXTERNAL://kafka:9094
  KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,EXTERNAL:PLAINTEXT
  ```

---

## 3. 完整版 Docker Compose（与引子一致 + Kafka-UI）

```yaml
version: '3.8'

services:
  kafka:
    image: bitnami/kafka:latest
    container_name: kafka
    ports:
      - "9092:9092"
    environment:
      - KAFKA_ENABLE_KRAFT=yes
      - KAFKA_CFG_NODE_ID=0
      - KAFKA_CFG_PROCESS_ROLES=broker,controller
      - KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@kafka:9093
      - KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093
      - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      - KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER
      - ALLOW_PLAINTEXT_LISTENER=yes
      - KAFKA_AUTO_CREATE_TOPICS_ENABLE=true
      - KAFKA_CFG_NUM_PARTITIONS=2
    volumes:
      - kafka_data:/bitnami/kafka

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    ports:
      - "8080:8080"
    environment:
      - DYNAMIC_CONFIG_ENABLED=true
      - KAFKA_CLUSTERS_0_NAME=kraft-kafka
      - KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS=kafka:9092
    depends_on:
      - kafka

volumes:
  kafka_data:
```

### Kafka-UI 使用说明

1. 启动后访问 `http://localhost:8080`
2. Kafka-UI 自动发现 `KAFKA_CLUSTERS_0_*` 配置的集群
3. 功能亮点：
   - Topic 浏览（消息查看、offset 管理）
   - Consumer Group 监控（Lag 可视化）
   - Schema Registry 集成
   - 动态配置管理（`DYNAMIC_CONFIG_ENABLED=true` 时可在 UI 修改集群配置）

---

## 4. 生产环境 KRaft 部署注意事项

### 多节点集群

```yaml
services:
  kafka-1:
    # KAFKA_CFG_NODE_ID=1
    # KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@kafka-1:9093,2@kafka-2:9093,3@kafka-3:9093
  kafka-2:
    # KAFKA_CFG_NODE_ID=2
  kafka-3:
    # KAFKA_CFG_NODE_ID=3
```

Controller 推荐奇数节点（3 或 5），与 ZooKeeper 时代的奇数法定要求一致。

### KRaft 集群初始化

首次启动时需要 **生成 Cluster ID**：

```bash
# Bitnami 镜像自动生成，无需手动指定
# 如果手动指定：
KAFKA_KRAFT_CLUSTER_ID=$(kafka-storage.sh random-uuid)
```

**所有节点必须使用相同的 Cluster ID**。

### Bitnami Mirror Node 的警告

Bitnami 官方宣布 Kafka 镜像已迁移，`bitnami/kafka` 旧 tag 可能停止更新。建议切换到 `docker.io/bitnami/kafka:3.9` 或使用官方 Apache/Confluent 镜像。

---

## 5. 引子文章中的环境准备（对照解读）

```
引子文章用 docker run（单行命令）
推荐改用 docker-compose.yml（本文章的三服务编排）
```

**为什么引子用 `docker run` 而非 compose？**
- 简洁演示：聚焦代码逻辑而非基础设施
- 但真实项目都应该用 compose 管理

**`KAFKA_AUTO_CREATE_TOPICS_ENABLE=true`**：允许 Producer/Consumer 自动创建 Topic。引子的 TaskService.createNewTopic() 中又用 AdminClient 手动创建，两者互补：
- 自动创建：`@KafkaListener` 监听不存在的 Topic 时会自动触发
- 手动创建（AdminClient）：更精细的控制（分区数、副本数、配置）

---

## 6. 常见 Docker Kafka 问题排查

### 容器启动失败，日志为空
```bash
# 开启 Bitnami 调试模式
BITNAMI_DEBUG=yes
```

### 客户端连接超时 / Connection refused
```bash
# 检查 advertised.listeners 是否正确
kafka-console-producer.sh --bootstrap-server localhost:9092 --topic test
# 如果报错，八成是 advertised 地址不对
```

### Topic 创建报 "not controller for this partition"
```
KRaft 模式需要几秒完成 Controller 选举。等 5-10 秒再重试即可。
```

### 重启后之前的数据还在吗？
```
容器内数据在 /bitnami/kafka 目录，如果用了 volume 映射则持久化。
引子文章用的是 H2 内存数据库 + Kafka 内存数据。两个都重启会丢失进度信息。
→ 详见 B6（Consumer Offset 管理与数据持久化）
```

---

> **延伸阅读**：[B5 — Spring Kafka 底层深度：Consumer API、线程安全与动态 Topic](./B5-spring-kafka-consumer-raw-api-thread-safety.md)
> **延伸阅读**：[B6 — 生产级可靠性：Offset 管理与重启恢复](./B6-kafka-offset-restart-recovery.md)


---

# 第 9 章：B5 — Spring Kafka 底层深度：Consumer API、线程安全与动态 Topic

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


---

# 第 10 章：B6 — 生产级可靠性：Offset 管理与重启恢复

# B6 — 生产级可靠性：Offset 管理与重启恢复

> **匹配引子文章知识点：** ✅ 重启后数据丢失 ✅ Consumer offset ✅ 内存数据库局限性
> 收录维度：**B — 消息队列集成深度（可靠性篇）**

---

## TL;DR

引子文章结尾说：
```
⚠️ 注意：当你重启了服务以后，是无法再获取进度信息的，你需要特殊处理。
```

**为什么会丢失？** 两个原因：
1. H2 内存数据库（`jdbc:h2:mem:taskdb`）——应用重启后 Task 表清空
2. Consumer offset 没有正确提交——新 Consumer 实例从最新 offset 开始消费，旧消息不见了

本文章分析这两个问题并给出 4 种修复方案。

---

## 1. 数据丢失的两层原因

### 原因一：H2 内存数据库

```yaml
spring:
  datasource:
    url: jdbc:h2:mem:taskdb    # ← 这是内存数据库！
    # url: jdbc:h2:file:./data/taskdb  # ← 文件数据库，重启后数据保留
```

`mem:taskdb` 意味着数据只存在应用进程内存中。应用重启后，所有 Task 记录（taskId, status, progress）全部消失。

**连带的后果**：
- `GET /api/tasks/{taskId}` 返回 404
- 即使 Kafka 中有进度消息，Consumer 也找不到对应 Task 记录来更新

### 原因二：Consumer Offset 行为

```yaml
spring:
  kafka:
    consumer:
      auto-offset-reset: earliest  # 新 group 从最早开始
```

引子代码中，Consumer 的 group 是硬编码的 `"task-group"`。每次重启，Consumer 的 offset 行为取决于：

1. **如果 Consumer 提交了 offset** → 重启后从上次提交的 offset 继续
2. **如果 Consumer 没有提交 offset** → 新的 Consumer 实例可能从 `auto-offset-reset` 决定的位置开始
3. **但引子文章的 Consumer 在重启前已经被销毁了** → Kafka 判断该 Consumer Group 为 dead → 运行一段时间后 offset 被清理（取决于 `offsets.retention.minutes`，默认 7 天或更长新版本中会有调整）

**关键**：引子文章用的是手动 `KafkaConsumer` + 自己管理 `poll()` 循环——**没有调用 `commitSync()` 或 `commitAsync()`**！说明 offset 根本就没提交。重启后 Consumer Group 起始位置取决于 `auto-offset-reset`。

---

## 2. Consumer Offset 图解

```
时间线 →
                        应用重启
                          │
消息: [A0][A1][A2][A3]   │   新消息: [A4][A5]
       ↑                 │
      上次提交 offset=3   │   auto-offset-reset:
                          │   - latest: 从 A4 开始（丢失 A0-A3）
                          │   - earliest: 从 A0 开始（重复消费）
                          │   - none: 报错（offset 不存在）
```

### auto-offset-reset 三种模式

| 模式 | 行为 | 适用场景 |
|------|------|---------|
| `latest`（默认） | 从 Topic 最新消息开始消费 | 容忍丢失历史消息 |
| `earliest` | 从最旧消息开始消费 | 需要回溯所有消息 |
| `none` | Group 初次加入时如果无 offset → 抛异常 | 强制要求 offset 存在 |

引子文章设为 `earliest`，重启后会**重复消费**所有已有进度消息。但 Task 表已经重建了（H2 内存擦除），新的 Task ID 和旧的 KEY 对不上 → 进度消息找不到对应的 Task 记录 → 静默丢弃。

---

## 3. 方案对比与选择

### 方案 A：最简单最小改动 — 文件数据库

```yaml
spring:
  datasource:
    url: jdbc:h2:file:./data/taskdb    # 只需改这一行
    # url: jdbc:h2:file:./data/taskdb;AUTO_RECONNECT=TRUE  # 可选
```

**做了什么**：H2 把数据写到文件而非内存。重启后 Task 记录保留。

**代价**：
- 仍然需要 `offsets.retention.minutes` 内启动，否则 Kafka 会清理 offset
- H2 文件不是为高并发设计的
- 仍然丢失已经结束的任务的进度（Task 记录在，但 Kafka 消息可能已经被删除）

### 方案 B：正确提交 Offset + 持久化数据库

```java
// 在 consumer.poll() 之后，显式提交 offset
private Map<String, TaskStatus> latestStatuses = new HashMap<>();

public TaskStatus getLatestTaskStatus(String taskId) {
    ConsumerRecords<String, TaskStatus> records = kafkaConsumer.poll(Duration.ofMillis(200));
    
    for (ConsumerRecord<String, TaskStatus> record : records) {
        latestStatuses.put(record.key(), record.value());
    }

    // 手动提交 offset
    kafkaConsumer.commitSync(Duration.ofSeconds(5));
    
    return latestStatuses.get(taskId);
}
```

**为什么这样不行**？因为引子文章的设计是每个请求 `poll()` 一次 → 如果不在 `poll()` 后提交，offset 就不会前进。但加上后，每次查进度都 commit offset，性能极差。

### 方案 C：使用 @KafkaListener + 重放历史（最佳实践）

```java
@Component
public class TaskProgressConsumer {

    @Autowired
    private TaskRepository taskRepository;

    @KafkaListener(topics = "task-progress-topic", groupId = "task-progress-group")
    public void onProgress(TaskProgressEvent event) {
        // 幂等更新
        taskRepository.findById(event.taskId()).ifPresentOrElse(
            task -> {
                task.setProgress(event.percentageComplete());
                task.setStatus(TaskStatus.valueOf(event.status()));
                taskRepository.save(task);
            },
            () -> {
                // 如果 Task 记录不存在（重启后 DB 丢失），重新创建
                Task newTask = new Task();
                newTask.setTaskId(event.taskId());
                newTask.setProgress(event.percentageComplete());
                newTask.setStatus(TaskStatus.valueOf(event.status()));
                taskRepository.save(newTask);
            }
        );
    }
}
```

**配合配置**：
```yaml
spring:
  kafka:
    consumer:
      auto-offset-reset: earliest        # 重启后从最早开始重放
      enable-auto-commit: false          # 手动 commit
    listener:
      ack-mode: RECORD                   # 每处理一条消息 ack 一次
```

**做了什么**：重启后 Consume 从最早的 offset 开始，把所有已发送的进度消息重新消费一遍。`Idempotent Consumer` 模式确保重复消费不影响最终状态。

**代价**：主题中消息量大时启动慢（需要重放所有历史）。

### 方案 D：压缩主题（Compact Topic）+ 最新状态读取

```java
// Producer 侧
@Bean
public NewTask taskProgressTopic() {
    return TopicBuilder.name("task-progress-compact")
        .partitions(1)
        .replicas(1)
        .compact()  // 🔑 压缩模式，保留每个 key 的最新消息
        .build();
}
```

**Compact Topic 行为**：
```
topic: task-progress-compact  (cleanup.policy=compact)

初始消息:
  task-001 → 10%
  task-002 → 20%
  task-001 → 50%
  task-003 → 0%
  task-001 → 100%    ← task-001 最新状态
  task-002 → 80%     ← task-002 最新状态
  task-003 → 40%     ← task-003 最新状态

压缩后:
  task-001 → 100%
  task-002 → 80%
  task-003 → 40%
```

**好处**：Compact Topic 自动清理旧版本消息。即使在重启后，Consumer 也能从 Topic 中通过 `earliest` 拿到每个 task 的最新状态。

---

## 4. 引子文章增强版（修复重启丢失问题）

在保持原有架构（底层 KafkaConsumer + 轮询）不变的前提下，最小改动修复方案：

### 改动 1：改用文件数据库
```yaml
spring.datasource.url: jdbc:h2:file:./data/taskdb
```

### 改动 2：Consumer 每次 poll 后提交 offset
```java
// KafkaConsumerService.java
public TaskStatus getLatestTaskStatus(String taskId) {
    synchronized (this) {
        ConsumerRecords<String, TaskStatus> records = kafkaConsumer.poll(Duration.ofMillis(200));
        if (!records.isEmpty()) {
            // 将所有进度更新到 TaskRepository
            records.forEach(record -> {
                TaskStatus status = record.value();
                taskRepository.findById(status.taskId()).ifPresent(task -> {
                    task.setProgress((int) status.percentageComplete());
                    task.setStatus(status.status().name());
                    taskRepository.save(task);
                });
            });
            kafkaConsumer.commitSync(Duration.ofSeconds(5));  // 🔑 commit
        }
        return taskRepository.findById(taskId)
            .map(Task::toTaskStatus)
            .orElse(null);
    }
}
```

### 改动 3：auto-offset-reset 设为 earliest
```yaml
spring.kafka.consumer.auto-offset-reset: earliest
```

### 改动 4：增加 Group ID 独立性
```yaml
spring.kafka.consumer.group-id: task-progress-${random.int}  # 每次启动新 group
```
或者固定 group id + 重复消费设计（方案 C）。

---

## 5. 架构建议总结

| 问题 | 引子文章 | 修复方案 |
|------|---------|---------|
| Task 表丢失 | H2 内存数据库 | 文件数据库 / MySQL / PostgreSQL |
| Offset 不持久 | 未 commit | 定期 commitSync |
| 重启后无法回溯 | auto-offset-reset 不匹配 | earliest + compact topic |
| 线程安全 | 原始 KafkaConsumer 多线程 | synchronized / @KafkaListener |
| Topic 膨胀 | 每条任务一个 Topic | 单 Topic + partition 或 compact |

**最佳实践组合**：`MySQL + @KafkaListener + compact topic + ack-mode=RECORD + Idempotent Consumer`

---

> **延伸阅读**：[B4 — KRaft + Docker + Kafka-UI 环境搭建](./B4-kafka-kraft-docker-kafka-ui-setup.md)
> **延伸阅读**：[B5 — Spring Kafka 底层深度：Consumer API、线程安全与动态 Topic](./B5-spring-kafka-consumer-raw-api-thread-safety.md)


---

# 第 11 章：C1 — 长任务 REST API 设计模式

# REST API Design for Long-Running Tasks

> 来源：restfulapi.net
> 原文：[REST API Design for Long-Running Tasks](https://restfulapi.net/rest-api-design-for-long-running-tasks/)
> 收录维度：**C — 实时推送 vs 轮询**

---

## 概述

当 REST API 需要处理长时间运行的操作（无法在 HTTP 请求超时内完成）时，需要异步响应模式。本文介绍多种标准设计模式。

## 核心原则

HTTP 请求应有合理的超时（通常 30-60s）。对于耗时更久的操作，不使用同步等待，而是采用异步模式。

## 四种设计模式

### 1. Polling（轮询模式）

最常用的模式，与引子文章一致。

**流程**：
```
POST /api/tasks → 202 Accepted + Location: /api/tasks/{id}
                     ↓
Client 定期 GET /api/tasks/{id}
                     ↓
                    200 OK + 当前状态
```

**实现**：

```http
# 客户端提交
POST /api/tasks
Content-Type: application/json

{"name": "data-export", "params": {...}}

# 响应
HTTP/1.1 202 Accepted
Location: /api/tasks/abc-123
Retry-After: 5

# 客户端轮询
GET /api/tasks/abc-123

# 响应（处理中）
HTTP/1.1 200 OK
Content-Type: application/json
{
  "taskId": "abc-123",
  "status": "PROCESSING",
  "progress": 45,
  "message": "Processing step 5/11"
}

# 响应（完成）
HTTP/1.1 200 OK
Content-Type: application/json
{
  "taskId": "abc-123",
  "status": "COMPLETED",
  "progress": 100,
  "result": { "downloadUrl": "/files/export-abc-123.csv" }
}
```

**HTTP 状态码**：
- `202 Accepted` — 任务已接受，尚未完成
- `200 OK` — 任务完成，响应体包含结果
- `303 See Other` — 可选方案，重定向到结果资源

**最佳实践**：
- `Retry-After` header 指示建议轮询间隔
- 指数退避，不要固定频率
- 任务完成后可返回 303 重定向到结果资源

### 2. Callback / Webhook（回调模式）

**流程**：
```
POST /api/tasks + callbackUrl
→ 202 Accepted
→ 处理完成后，服务器 POST 结果到 callbackUrl
```

**实现**：

```http
# 客户端提交 + 注册回调
POST /api/tasks
Content-Type: application/json

{
  "name": "data-export",
  "params": {...},
  "callbackUrl": "https://client.example.com/webhook/task-complete"
}

# 响应
HTTP/1.1 202 Accepted
Location: /api/tasks/abc-123
```

任务完成后，服务器调用 callback URL：

```http
POST /webhook/task-complete
Content-Type: application/json

{
  "taskId": "abc-123",
  "status": "COMPLETED",
  "result": { "downloadUrl": "/files/export-abc-123.csv" }
}
```

**最佳实践**：
- 回调 URL 应为 HTTPS
- 回调签名验证（HMAC 或 JWT）
- 重试机制（回调失败后重试）
- 超时后备（回调未达时提供轮询端点）

### 3. Long Polling（长轮询）

客户端保持连接打开，服务器在有数据时立即返回，否则等待。

```
GET /api/tasks/abc-123/poll?timeout=30

→ 服务器保持连接打开（最多 30s）
→ 任务完成时立即返回
→ 超时则返回 304 Not Modified，客户端重新发起
```

**优点**：比轮询更实时，比 WebSocket 简单
**缺点**：服务器资源占用较高，不适合高频场景
**适用**：低频度但需要即时性的场景

### 4. Server-Sent Events (SSE)

**流程**：
```
GET /api/tasks/abc-123/stream
Accept: text/event-stream
→ 服务器持续推送事件
```

详见：C2-sse-spring-boot-obregon-medium.md

## 模式对比

| 模式 | 实时性 | 服务器开销 | 客户端复杂度 | 适用场景 |
|------|--------|-----------|-------------|---------|
| 轮询 | 低 | 低 | 低 | 简单场景，低频检查 |
| 回调 | 中 | 中 | 中 | 任务完成后通知 |
| 长轮询 | 中 | 中 | 中 | 需要轻度实时 |
| SSE | 高 | 中 | 低 | 单向实时推送 |
| WebSocket | 高 | 高 | 高 | 双向实时通信 |

## REST API 最佳实践

### 统一的任务资源模型

```json
{
  "taskId": "uuid",
  "status": "PENDING|PROCESSING|COMPLETED|FAILED|CANCELLED",
  "progress": 0-100,
  "message": "当前状态描述",
  "createdAt": "ISO-8601",
  "updatedAt": "ISO-8601",
  "result": {},
  "error": {}
}
```

### GET /api/tasks 多条件查询

```http
GET /api/tasks?status=PROCESSING&createdAfter=2026-06-01&page=0&size=20
```

### 取消任务

```http
DELETE /api/tasks/{id}
→ 204 No Content
```

或使用幂等更新（推荐）：

```http
PATCH /api/tasks/{id}
Content-Type: application/json

{"action": "CANCEL"}
```

---

## 适用于引子文章的建议

引子文章使用轮询模式，考虑渐进式演进：

1. **短期**：保持轮询，加入 `Retry-After` + 指数退避
2. **中期**：增加 SSE 端点（/api/tasks/{id}/stream）作为轮询的补充
3. **长期**：根据业务需要决定是否需要回调/WebSocket


---

# 第 12 章：C2 — SSE 实时推送实战指南

# Implementing Server-Sent Events (SSE) in Spring Boot

> 来源：Medium / Alexander Obregon
> 原文：[How to Implement Server-Sent Events (SSE) in Spring Boot](https://medium.com/@AlexanderObregon/how-to-implement-server-sent-events-sse-in-spring-boot-620024272ccb)
> 收录维度：**C — 实时推送 vs 轮询**

---

## 1. SSE 简介

Server-Sent Events (SSE) 允许服务器通过单个、长连接的 HTTP 连接向客户端推送数据。

### 优点
- **简单**：纯 HTTP，不需要特殊协议（如 WebSocket）
- **自动重连**：浏览器 EventSource API 自带断线重连
- **事件类型**：支持自定义事件名，客户端可区分处理
- **兼容 HTTP/2**：无缝集成现有基础设施

### 局限
- 单向通信：仅服务端→客户端
- 浏览器兼容：不支持 IE
- 二进制数据需要编码（如 base64）

## 2. 基础实现：SseEmitter

### Maven 依赖

只需 Spring Web Starter（spring-boot-starter-web），SSE 内置于 Servlet 容器。

### 基础 SSE 端点

```java
@Controller
public class SSEController {

    private final ExecutorService executor = Executors.newCachedThreadPool();

    @GetMapping("/stream-sse")
    public SseEmitter streamSseEvents() {
        SseEmitter emitter = new SseEmitter(Long.MAX_VALUE); // 长连接

        executor.execute(() -> {
            try {
                for (int i = 0; i < 10; i++) {
                    Thread.sleep(1000);
                    emitter.send("SSE MVC - " + System.currentTimeMillis());
                }
                emitter.complete();
            } catch (IOException | InterruptedException e) {
                emitter.completeWithError(e);
            }
        });

        return emitter;
    }
}
```

### 测试

```bash
curl -N http://localhost:8080/stream-sse
```

## 3. 带事件类型的 SSE

```java
emitter.send(SseEmitter.event()
    .name("NEWS")           // 事件名称，客户端可区分
    .data(newsItem.toString()));
```

## 4. 多客户端广播模式

```java
@RestController
public class NewsController {

    private final List<SseEmitter> emitters = new CopyOnWriteArrayList<>();
    private final NewsService newsService;

    @GetMapping("/news")
    public SseEmitter subscribeToNews() {
        SseEmitter emitter = new SseEmitter(Long.MAX_VALUE);
        emitters.add(emitter);

        emitter.onCompletion(() -> emitters.remove(emitter));
        emitter.onTimeout(() -> emitters.remove(emitter));
        emitter.onError(e -> emitters.remove(emitter));

        // 订阅时发送已有新闻
        newsService.getNewsItems().forEach(newsItem -> {
            try {
                emitter.send(SseEmitter.event().name("NEWS").data(newsItem));
            } catch (Exception e) {
                emitter.completeWithError(e);
            }
        });

        return emitter;
    }

    public void dispatchNewsItem(NewsItem newsItem) {
        List<SseEmitter> deadEmitters = new ArrayList<>();
        emitters.forEach(emitter -> {
            try {
                emitter.send(SseEmitter.event().name("NEWS").data(newsItem));
            } catch (Exception e) {
                deadEmitters.add(emitter);
            }
        });
        emitters.removeAll(deadEmitters);
    }
}
```

**关键**：使用 `CopyOnWriteArrayList` 避免并发问题。

## 5. SSE 与任务进度追踪整合

结合引子文章的任务进度追踪：

```java
@RestController
@RequestMapping("/api/tasks")
public class TaskProgressSSEController {

    private final Map<String, List<SseEmitter>> taskEmitters = new ConcurrentHashMap<>();

    @GetMapping("/{taskId}/stream")
    public SseEmitter streamTaskProgress(@PathVariable String taskId) {
        SseEmitter emitter = new SseEmitter(Long.MAX_VALUE);

        taskEmitters.computeIfAbsent(taskId, k -> new CopyOnWriteArrayList<>())
            .add(emitter);

        emitter.onCompletion(() -> removeEmitter(taskId, emitter));
        emitter.onTimeout(() -> removeEmitter(taskId, emitter));

        return emitter;
    }

    private void removeEmitter(String taskId, SseEmitter emitter) {
        List<SseEmitter> emitters = taskEmitters.get(taskId);
        if (emitters != null) {
            emitters.remove(emitter);
            if (emitters.isEmpty()) {
                taskEmitters.remove(taskId);
            }
        }
    }

    // 当 Kafka 消费者收到进度事件，推送至 SSE
    @KafkaListener(topics = "task-progress")
    public void onProgress(ProgressEvent event) {
        List<SseEmitter> emitters = taskEmitters.get(event.getTaskId());
        if (emitters != null) {
            emitters.forEach(emitter -> {
                try {
                    emitter.send(SseEmitter.event()
                        .name("PROGRESS")
                        .data(event));
                } catch (IOException e) {
                    removeEmitter(event.getTaskId(), emitter);
                }
            });
        }
    }
}
```

**客户端（浏览器）**：

```javascript
const eventSource = new EventSource(`/api/tasks/${taskId}/stream`);

eventSource.addEventListener('PROGRESS', (event) => {
    const data = JSON.parse(event.data);
    updateProgressBar(data.progress);
    updateStatus(data.message);
});

eventSource.addEventListener('COMPLETED', (event) => {
    const data = JSON.parse(event.data);
    showResult(data.result);
    eventSource.close();
});

eventSource.addEventListener('FAILED', (event) => {
    const data = JSON.parse(event.data);
    showError(data.error);
    eventSource.close();
});
```

## 6. SSE vs WebSocket vs Polling 对比

| 特性 | Polling | SSE | WebSocket |
|------|---------|-----|-----------|
| 通信方向 | 客户端→服务端（请求驱动） | 服务端→客户端 | 双向 |
| 协议 | HTTP | HTTP | ws:// / wss:// |
| 自动重连 | 需手动实现 | 浏览器内置 | 需手动实现 |
| 浏览器支持 | 全部 | 现代浏览器（不支持 IE） | 主流浏览器 |
| 服务器资源 | 低 | 中（需保持长连接） | 高（双向通道） |
| 实现复杂度 | 低 | 中 | 高 |
| 最佳场景 | 低频、非实时 | 服务端推送 | 实时互动 |

## 7. SSE 生产注意事项

1. **连接超时**：SseEmitter 有默认超时（30s），设置 `Long.MAX_VALUE` 或合理超时
2. **线程泄漏**：客户端断开后必须 cleanup（onCompletion/onTimeout/onError）
3. **负载均衡**：SSE 连接有粘性问题，需 session affinity（sticky session）
4. **连接数限制**：浏览器每域名最多 6 个 SSE 连接（HTTP/1.1）
5. **心跳**：定期发送注释行（`: heartbeat`）防止代理 / 负载均衡器断开空闲连接

### 心跳保活

```java
// 每 30s 发送空注释
executor.scheduleAtFixedRate(() -> {
    emitters.forEach(emitter -> {
        try {
            emitter.send(SseEmitter.event().comment("heartbeat").name(""));
        } catch (IOException e) {
            // client disconnected
        }
    });
}, 0, 30, TimeUnit.SECONDS);
```

## 8. 渐进式升级路径

对于引子文章的轮询方案，建议：

1. **阶段 1**：保留轮询 API，添加 SSE 端点作为补充
2. **阶段 2**：前端优先使用 SSE，下降为轮询
3. **阶段 3**：轮询作为 SSE 断开时的 fallback


---

# 第 13 章：D1 — Kafka 重试与死信队列

# Kafka Retry & DLT in Spring Boot: A Practical Guide

> 来源：Medium / MoshDev
> 原文：[Kafka Retry & DLT in Spring Boot](https://medium.com/@moshdev2213/kafka-retry-dlt-in-spring-boot-a-practical-guide-4b2b5e931710)
> 收录维度：**D — 生产级错误处理**

---

## 概述

Spring Kafka 提供了开箱即用的重试和死信队列支持。本文深入 `@RetryableTopic` 和 `@DltHandler` 的完整配置。

## 1. @RetryableTopic 快速入门

```java
@RetryableTopic(
    attempts = "4",           // 初始 1 次 + 3 次重试
    backoff = @Backoff(
        delay = 1000,         // 初始延迟 1s
        multiplier = 2.0      // 指数退避：1s → 2s → 4s
    ),
    autoCreateTopics = "false", // 自动创建 topic（用于开发）
    topicSuffixingStrategy = TopicSuffixingStrategy.SUFFIX_WITH_INDEX_VALUE,
    dltTopicSuffix = "-dlt"
)
@KafkaListener(topics = "task-progress")
public void handleProgress(ProgressEvent event) {
    // 处理逻辑
    processEvent(event);
}

@DltHandler
public void handleDlt(ProgressEvent event) {
    // 死信处理：记录日志、报警、存到专门错误表
    log.error("Event processing failed after retries: {}", event);
    errorRepository.save(new DeadLetterEvent(event, "All retries exhausted"));
}
```

## 2. 自动创建的 Topic 结构

```
task-progress           ← 原始 topic
task-progress-retry-0   ← 第一次重试 topic
task-progress-retry-1   ← 第二次重试 topic
task-progress-retry-2   ← 第三次重试 topic
task-progress-dlt       ← 死信 topic
```

当 `autoCreateTopics=true` 时，Spring 会自动创建这些 topics。生产环境推荐 `autoCreateTopics=false`，由基础设施团队预创建。

## 3. 退避策略详解

```java
// 固定延迟
@Backoff(delay = 2000)      // 每次重试固定等 2s

// 指数退避
@Backoff(delay = 1000, multiplier = 2.0)    // 1s, 2s, 4s, 8s...

// 带随机抖动（避免重试风暴）
@Backoff(delay = 1000, multiplier = 2.0, randomExpression = "${retry.jitter:0.5}")
```

**生产推荐**：指数退避 + 随机抖动，防止多个消费者同时重试。

## 4. 手动配置：不使用注解

```java
@Configuration
public class KafkaRetryConfig {

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, ProgressEvent>
            kafkaListenerContainerFactory(ConsumerFactory<String, ProgressEvent> cf) {

        ConcurrentKafkaListenerContainerFactory<String, ProgressEvent> factory =
            new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(cf);

        // 创建重试模板
        RetryTemplate retryTemplate = new RetryTemplate();
        retryTemplate.setRetryOperationsMap(Map.of(
            ProgressEvent.class, new SimpleRetryPolicy(3)  // 最多重试 3 次
        ));
        retryTemplate.setBackOffPolicy(new ExponentialBackOffPolicy());

        // 创建死信恢复器
        DeadLetterPublishingRecoverer recoverer =
            new DeadLetterPublishingRecoverer(kafkaTemplate,
                (record, exception) -> new TopicPartition(
                    record.topic() + "-dlt", record.partition()));

        factory.setCommonErrorHandler(
            new DefaultErrorHandler(recoverer, retryTemplate));

        return factory;
    }
}
```

## 5. 自定义死信 Topic 名称

```java
@DltHandler
public void handleDlt(
        ProgressEvent event,
        @Header(KafkaHeaders.RECEIVED_TOPIC) String topic,
        @Header(KafkaHeaders.OFFSET) long offset,
        @Header(KafkaHeaders.EXCEPTION_MESSAGE) String errorMessage) {

    log.error("DLT received from topic: {}, offset: {}, error: {}",
        topic, offset, errorMessage);
    // 将死信保存到数据库
    deadLetterService.save(event, new ErrorDetail(topic, offset, errorMessage));
}
```

## 6. 错误分类：可重试 vs 不可重试

```java
@Configuration
public class KafkaErrorClassificationConfig {

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, ProgressEvent>
            kafkaListenerContainerFactory(ConsumerFactory<String, ProgressEvent> cf) {
        // ...

        // 自定义可重试异常
        Map<Class<? extends Throwable>, Boolean> exceptions = new HashMap<>();
        exceptions.put(RetryableException.class, true);     // 可重试
        exceptions.put(NetworkException.class, true);       // 可重试
        exceptions.put(DataIntegrityViolationException.class, false); // 不可重试
        exceptions.put(SerializationException.class, false); // 不可重试

        RetryPolicy retryPolicy = new SimpleRetryPolicy(3, exceptions, true);

        // ...
    }
}
```

**原则**：
- **可重试**：临时异常（网络超时、数据库乐观锁冲突、下游服务 503）
- **不可重试**：固定异常（数据格式错误、业务校验失败、权限不足）

## 7. 生产最佳实践

### 幂等消费者

```java
@Component
public class IdempotentProgressConsumer {

    private final Set<String> processedIds = ConcurrentHashMap.newKeySet();

    @KafkaListener(topics = "task-progress")
    public void handle(@Payload ProgressEvent event,
                       @Header(KafkaHeaders.RECEIVED_MESSAGE_KEY) String key) {
        // 基于 eventId 去重
        if (!processedIds.add(event.getEventId())) {
            log.info("Duplicate event: {}, skipping", event.getEventId());
            return;
        }

        processSafely(event);
    }
}
```

### 监控重试状态

```java
@Component
public class RetryMetricsRecorder {

    private final MeterRegistry meterRegistry;

    @EventListener
    public void onRetry(ConsumerRetryEvent event) {
        meterRegistry.counter("kafka.retry",
            "topic", event.getTopic(),
            "attempt", String.valueOf(event.getAttempt()))
            .increment();
    }

    @EventListener
    public void onDlt(ConsumerDltEvent event) {
        meterRegistry.counter("kafka.dlt",
            "topic", event.getTopic())
            .increment();
    }
}
```

### 生产 checklist

- [ ] 幂等消费者（防止重试导致重复处理）
- [ ] @RetryableTopic 退避策略，避免重试风暴
- [ ] DLT 监控和告警
- [ ] 区分可重试/不可重试异常
- [ ] 自动创建 topics 仅用于开发环境
- [ ] 配置足够的重试间隔，给下游系统恢复时间
- [ ] DLT 处理：人工介入 / 自动重放 / 数据分析

## 8. 与引子文章的结合

在 Spring Boot + Kafka 任务追踪中加入重试机制：

```java
@Service
public class TaskProgressConsumer {

    @RetryableTopic(
        attempts = "5",
        backoff = @Backoff(delay = 2000, multiplier = 2.0, maxDelay = 60000),
        exclude = {NonRetryableException.class}
    )
    @KafkaListener(topics = "task-progress", concurrency = "3")
    public void updateTaskProgress(ProgressEvent event) {
        taskRepository.findById(event.getTaskId()).ifPresent(task -> {
            task.setProgress(event.getProgress());
            task.setStatus(event.getStatus());
            taskRepository.save(task);
        });
    }

    @DltHandler
    public void handleDltProgress(ProgressEvent event, Exception ex) {
        log.error("Task progress update failed for task {} after retries: {}",
            event.getTaskId(), ex.getMessage());
        alertService.sendAlert("Kafka progress update failed", event, ex);
    }
}
```


---

# 第 14 章：E1 — SAGA 编排与状态机

# Implementing SAGA Orchestration with Spring State Machine + Kafka

> 来源：Substack / CodeExperts
> 原文：[Implementing SAGA Orchestration with Spring Boot State Machine + Kafka](https://codeexperts07.substack.com/p/implementing-saga-orchestration-with)
> 收录维度：**E — 任务编排与状态机**

---

## 概述

将简单 TaskStatus 枚举升级为完整状态机驱动的 Saga 编排模式，使用 Kafka 作为事件总线。

## 1. 从 TaskStatus 到状态机

### 原始设计（引子文章）

```java
public enum TaskStatus {
    PENDING, PROCESSING, COMPLETED, FAILED
}
```

### 升级为状态机

```java
public enum TaskState {
    CREATED,
    VALIDATING,
    VALIDATED,
    EXECUTING,
    TRANSFORMING,
    REPORTING,
    COMPLETED,
    FAILED,
    COMPENSATING,     // 补偿中
    COMPENSATED,      // 已完成补偿
    CANCELLED
}

public enum TaskEvent {
    SUBMIT,
    VALIDATE,
    VALIDATE_FAIL,
    EXECUTE,
    TRANSFORM,
    REPORT,
    COMPLETE,
    FAIL,
    COMPENSATE,
    CANCEL
}
```

## 2. Spring Statemachine 配置

```java
@Configuration
@EnableStateMachineFactory
public class TaskStateMachineConfig
        extends StateMachineConfigurerAdapter<TaskState, TaskEvent> {

    @Override
    public void configure(StateMachineStateConfigurer<TaskState, TaskEvent> states)
            throws Exception {
        states
            .withStates()
                .initial(TaskState.CREATED)
                .state(TaskState.EXECUTING)
                .end(TaskState.COMPLETED)
                .end(TaskState.FAILED)
                .end(TaskState.COMPENSATED)
                .end(TaskState.CANCELLED);
    }

    @Override
    public void configure(StateMachineTransitionConfigurer<TaskState, TaskEvent> transitions)
            throws Exception {
        transitions
            .withExternal()
                .source(TaskState.CREATED).target(TaskState.VALIDATING)
                .event(TaskEvent.SUBMIT)
            .and()
            .withExternal()
                .source(TaskState.VALIDATING).target(TaskState.EXECUTING)
                .event(TaskEvent.VALIDATE)
            .and()
            .withExternal()
                .source(TaskState.VALIDATING).target(TaskState.FAILED)
                .event(TaskEvent.VALIDATE_FAIL)
            .and()
            .withExternal()
                .source(TaskState.EXECUTING).target(TaskState.COMPLETED)
                .event(TaskEvent.COMPLETE)
            .and()
            .withExternal()
                .source(TaskState.EXECUTING).target(TaskState.FAILED)
                .event(TaskEvent.FAIL)
            .and()
            .withExternal()
                .source(TaskState.EXECUTING).target(TaskState.COMPENSATING)
                .event(TaskEvent.COMPENSATE)
            .and()
            .withExternal()
                .source(TaskState.COMPENSATING).target(TaskState.COMPENSATED)
                .event(TaskEvent.COMPLETE);
    }

    @Override
    public void configure(StateMachineConfigurationConfigurer<TaskState, TaskEvent> config)
            throws Exception {
        config
            .withConfiguration()
                .listener(new TaskStateMachineListener());
    }
}
```

## 3. 与 Kafka 集成：事件驱动状态变更

### 状态变更事件发布

```java
@Component
public class TaskStateEventPublisher {

    private final KafkaTemplate<String, StateChangeEvent> kafkaTemplate;
    private final StateMachineFactory<TaskState, TaskEvent> stateMachineFactory;

    @Transactional
    public StateChangeEvent handleEvent(String taskId, TaskEvent event, Map<String, Object> context) {
        StateMachine<TaskState, TaskEvent> sm = stateMachineFactory.getStateMachine(taskId);
        sm.start();

        // 发送事件到状态机
        Message<TaskEvent> message = MessageBuilder
            .withPayload(event)
            .setHeader("taskId", taskId)
            .copyHeaders(context)
            .build();

        sm.sendEvent(message);

        // 构建状态变更事件
        StateChangeEvent changeEvent = StateChangeEvent.builder()
            .taskId(taskId)
            .fromState(sm.getState().getId().name())
            .toState(getNewState(sm))
            .event(event.name())
            .timestamp(Instant.now())
            .build();

        // 发布到 Kafka
        kafkaTemplate.send("task-state-changes", taskId, changeEvent);

        return changeEvent;
    }
}
```

### 消费者监听状态变更

```java
@Component
public class TaskStateChangeConsumer {

    @KafkaListener(topics = "task-state-changes", groupId = "task-orchestrator")
    public void onStateChange(StateChangeEvent event) {
        switch (TaskEvent.valueOf(event.getEvent())) {
            case VALIDATE -> validateTask(event);
            case EXECUTE -> executeTask(event);
            case COMPLETE -> completeTask(event);
            case FAIL -> handleFailure(event);
            case COMPENSATE -> compensateTask(event);
        }
    }

    private void executeTask(StateChangeEvent event) {
        // 将任务发送到执行队列
        kafkaTemplate.send("task-execution", event.getTaskId(), event);
    }

    private void compensateTask(StateChangeEvent event) {
        // 发送补偿命令到各个子服务
        kafkaTemplate.send("task-compensation", event.getTaskId(),
            CompensationEvent.of(event.getTaskId()));
    }
}
```

## 4. SAGA 模式对比

### 编排 (Choreography)

每个服务在完成本地事务后发布事件，其他服务监听事件并做出反应。

**优点**：松耦合，无需中央协调器
**缺点**：流程隐式，难以追踪和治理

```
Service A → "OrderCreated" → Service B → "PaymentProcessed" → Service C
     ↑                                                              ↓
     └──────────────── "InventoryReleased" ←─────────────────────────
```

### 编排 (Orchestration)

由中央协调器（Orchestrator）控制 Saga 中每一步的参与者。

**优点**：流程显式，易于管理和监控
**缺点**：协调器可能成为单点

```
                    Orchestrator
                  /      |       \
                 ↓       ↓        ↓
            Service A  Service B  Service C
                 ↑       ↑         ↑
                  └──────┴─────────┘
                     事件反馈
```

**推荐**：对于复杂的长任务编排，使用 Orchestration 模式。

## 5. 补偿事务设计

```java
// 正向事务步骤
@Component
public class OrderSagaSteps {

    // Step 1: 创建订单
    @KafkaListener(topics = "saga-create-order")
    public void createOrder(OrderEvent event) {
        orderRepository.save(Order.create(event));
        kafkaTemplate.send("saga-reserve-inventory", event.getOrderId(), event);
    }

    // Step 1 补偿: 取消订单
    @KafkaListener(topics = "saga-compensate-order")
    public void compensateOrder(OrderEvent event) {
        orderRepository.findById(event.getOrderId()).ifPresent(order -> {
            order.cancel();
            orderRepository.save(order);
        });
    }

    // Step 2: 预留库存
    @KafkaListener(topics = "saga-reserve-inventory")
    public void reserveInventory(OrderEvent event) {
        inventoryService.reserve(event.getProductId(), event.getQuantity());
        kafkaTemplate.send("saga-process-payment", event.getOrderId(), event);
    }

    // Step 2 补偿: 释放库存
    @KafkaListener(topics = "saga-compensate-inventory")
    public void compensateInventory(OrderEvent event) {
        inventoryService.release(event.getProductId(), event.getQuantity());
    }
}
```

## 6. Kafka 在 Saga 中的角色

```
Topic: saga-state-changes
  ├── 消费者: orchestrator   → 控制流程路由
  ├── 消费者: audit-logger   → 审计日志（长期保留）
  └── 消费者: monitor        → 实时监控

Topic: saga-commands
  ├── saga-create-order      → 创建订单的命令队列
  ├── saga-reserve-inventory → 预留库存的命令队列
  ├── saga-process-payment   → 处理支付的命令队列
  └── saga-compensate-*      → 补偿命令队列
```

## 7. 架构演进路径

```
阶段 1: 简单枚举状态
  TaskStatus: PENDING → PROCESSING → COMPLETED | FAILED
  ↓

阶段 2: 状态机
  TaskState: 更多状态 + 显式流转规则
  TaskEvent: 事件驱动状态变更
  ↓

阶段 3: 事件驱动 Saga
  Kafka 作为事件总线
  多个服务监听状态变更
  独立补偿逻辑
  ↓

阶段 4: 集中式工作流编排
  Orchestrator 控制完整流程
  补偿步骤与正向步骤一一对应
  可观测性完善
  ↓

阶段 5: 专业工作流引擎
  Temporal / Camunda / Zeebe
  更复杂的工作流、定时、人工审批
```

## 最佳实践

1. **状态机保证状态流转合法**（不允许非法跳转）
2. **每个 Saga 步骤都必须有补偿实现**
3. **幂等是所有步骤的设计前提**
4. **使用 `@Transactional` 保证本地事务与消息发送原子性**
5. **监控 Saga 执行状态**（进行中、挂起、失败）
6. **设定 Saga 超时**，超时触发自动补偿
7. **所有补偿操作也必须是幂等的**


---

# 第 15 章：F1 — Spring Kafka 可观测性：Micrometer 监控

# Spring Kafka Metrics with Micrometer

> 来源：JavaCodeGeeks
> 原文：[Spring Kafka Metrics with Micrometer](https://www.javacodegeeks.com/spring-kafka-metrics-with-micrometer.html)
> 收录维度：**F — 可观测性与监控**

---

## 概述

Micrometer 是 Spring Boot 3.x 推荐的指标收集框架。Spring for Apache Kafka 从 3.0 开始原生集成 Micrometer，提供开箱即用的指标。

## 1. 快速集成

### Maven 依赖

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>
```

Spring Boot 3.x 启动后，Micrometer + Prometheus 集成自动生效。

### 配置暴露端点

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus
  metrics:
    tags:
      application: ${spring.application.name}
```

## 2. Kafka Producer 指标

生产端 Micrometer 自动采集的指标：

| 指标名 | 类型 | 说明 |
|--------|------|------|
| `kafka.producer.record.send.total` | Counter | 发送总记录数 |
| `kafka.producer.record.send.rate` | Gauge | 发送速率 |
| `kafka.producer.outgoing.byte.total` | Counter | 发送字节总数 |
| `kafka.producer.request.total` | Counter | 请求总数 |
| `kafka.producer.request.latency.avg` | Gauge | 平均请求延迟 |
| `kafka.producer.response.total` | Counter | 响应总数 |
| `kafka.producer.io.rate` | Gauge | I/O 速率 |
| `kafka.producer.io.wait.time.ns.avg` | Gauge | I/O 等待时间 |

## 3. Kafka Consumer 指标

| 指标名 | 类型 | 说明 |
|--------|------|------|
| `kafka.consumer.fetch.manager.records.lag` | Gauge | **消费堆积数（最核心指标）** |
| `kafka.consumer.fetch.manager.records.consumed.total` | Counter | 已消费记录总数 |
| `kafka.consumer.fetch.manager.records.lag.max` | Gauge | 最大分区的消费堆积 |
| `kafka.consumer.fetch.size.avg` | Gauge | 平均每次 fetch 大小 |
| `kafka.consumer.fetch.rate` | Gauge | fetch 频率 |
| `kafka.consumer.coordination.assigned.partitions` | Gauge | 分配的分区数 |
| `kafka.consumer.coordination.join.time.avg` | Gauge | 平均加入组时间 |

## 4. 自动暴露 MicrometerObservation

Spring for Apache Kafka 3.0+ 使用 Micrometer Observation 记录生产与消费操作：

```yaml
spring:
  kafka:
    producer:
      properties:
        spring.kafka.producer.observation-enabled: true
    consumer:
      properties:
        spring.kafka.consumer.observation-enabled: true
```

启用后，每个生产/消费操作都会产生 spans，可与分布式追踪系统集成。

## 5. 在引子文章中的应用

在 TaskProgressConsumer 中添加 Micrometer 指标：

```java
@Component
public class MonitoredTaskProgressConsumer {

    private final MeterRegistry meterRegistry;

    public MonitoredTaskProgressConsumer(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
    }

    @KafkaListener(topics = "task-progress", groupId = "task-service")
    public void onProgress(ProgressEvent event) {
        Timer.Sample sample = Timer.start(meterRegistry);

        try {
            processEvent(event);
            sample.stop(Timer.builder("task.progress.process.time")
                .tag("status", event.getStatus().name())
                .register(meterRegistry));

            meterRegistry.counter("task.progress.events",
                "status", event.getStatus().name()).increment();

        } catch (Exception e) {
            sample.stop(Timer.builder("task.progress.process.time")
                .tag("status", "FAILED")
                .register(meterRegistry));

            meterRegistry.counter("task.progress.errors",
                "errorType", e.getClass().getSimpleName()).increment();
            throw e;  // 让框架层面的 retry/DLT 处理
        }
    }
}
```

## 6. Consumer Lag 监控

Consumer Lag 是 Kafka 最重要的生产指标。以下是在 Prometheus 中的查询：

```promql
# 按消费者组查看堆积
kafka_consumer_fetch_manager_records_lag{
    group_id="task-service"
}

# 按 Topic 查看堆积
kafka_consumer_fetch_manager_records_lag{
    topic="task-progress"
}

# 堆积增长率（报警用）
rate(kafka_consumer_fetch_manager_records_lag[5m]) > 0
```

### Prometheus 告警规则

```yaml
groups:
  - name: kafka-consumer
    rules:
      - alert: KafkaConsumerLag
        expr: kafka_consumer_fetch_manager_records_lag{group_id="task-service"} > 10000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Kafka consumer lag > 10k for task-service"
      - alert: KafkaConsumerLagCritical
        expr: kafka_consumer_fetch_manager_records_lag > 50000
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Kafka consumer lag > 50k, immediate attention needed"
```

## 7. 自定义业务指标

```java
@Component
public class TaskMetricsRecorder {

    private final MeterRegistry meterRegistry;

    // 任务状态分布
    public void recordTaskStatus(String status) {
        meterRegistry.counter("tasks.by.status", "status", status).increment();
    }

    // 任务处理用时
    public void recordTaskDuration(String taskType, long durationMs) {
        meterRegistry.timer("task.duration", "type", taskType)
            .record(Duration.ofMillis(durationMs));
    }

    // 实时进度
    public Gauge trackProcessingTasks(String taskType) {
        return Gauge.builder("tasks.processing.current", this, TaskMetricsRecorder::getProcessingCount)
            .tag("type", taskType)
            .register(meterRegistry);
    }

    // 任务成功率
    public void recordTaskResult(String taskType, boolean success) {
        meterRegistry.counter("tasks.result",
            "type", taskType,
            "result", success ? "success" : "failure"
        ).increment();
    }
}
```

## 8. Grafana 面板建议

监控 Kafka 任务追踪系统至少包含以下面板：

1. **消费者 Lag** — 按 group/topic 的堆积数时间序列
2. **消息吞吐量** — 生产/消费速率
3. **任务状态分布** — PIE/饼图（各状态任务数）
4. **任务处理延迟** — P50/P95/P99 处理时间
5. **错误率** — 按错误类型分类
6. **线程池状态** — active/max/pool size, queue depth

## 9. 生产环境 checklist

- [ ] 配置 Prometheus registry 并暴露 `/actuator/prometheus`
- [ ] 启用 `observation-enabled=true` 获得 tracing
- [ ] 配置 Consumer Lag 告警阈值
- [ ] 添加自定义业务指标（任务处理时间、状态分布）
- [ ] 配置线程池指标监控
- [ ] 记录 DLT 错误数量
- [ ] 设置 Grafana 面板


---

# 第 16 章：G1 — 调度方案全景对比：Quartz vs @Scheduled vs MQ

# Quartz vs @Scheduled vs Message Queues: 调度方案全景对比

> 来源：Medium / Turkcell Engineering
> 原文：[Managing Background Jobs in Spring Boot: Quartz vs Scheduled vs Message Queues](https://medium.com/turkcell/managing-background-jobs-in-spring-boot-quartz-vs-scheduled-vs-message-queues-e2dc5d4cfc2b)
> 收录维度：**G — 调度方案全景对比**

---

## 概述

Spring Boot 生态中管理后台任务的三种主要方案对比：`@Scheduled`、Quartz、消息队列。

## 三种方案详解

### 1. @Scheduled 注解

```java
@Component
public class ScheduledTaskService {

    @Scheduled(fixedRate = 5000)       // 每 5 秒执行一次（不考虑上次执行时间）
    public void runEvery5Seconds() { }

    @Scheduled(fixedDelay = 5000)      // 上次执行完后，等 5 秒再执行
    public void runWithDelay() { }

    @Scheduled(cron = "0 0 19 * * ?")  // 每天 19:00 执行（北京时区通过 @PostConstruct 设置）
    public void runDaily() { }

    @Scheduled(initialDelay = 10000, fixedRate = 60000) // 启动后 10s 开始，之后每 60s
    public void delayedStart() { }
}
```

**特点**：
- 零配置，开箱即用
- 单 JVM 内运行
- 不支持集群（多实例下会重复执行）
- 不支持持久化
- 适合简单、单机、非关键定时任务

**适用场景**：
- 定时清理缓存
- 定时生成报表（单实例）
- 定期健康检查

### 2. Quartz Scheduler

```java
// 1. 添加依赖
implementation 'org.springframework.boot:spring-boot-starter-quartz'

// 2. 定义 Job
public class ReportGenerationJob extends QuartzJobBean {
    @Override
    protected void executeInternal(JobExecutionContext context) {
        // 报表生成逻辑
    }
}

// 3. 配置 Trigger + JobDetail
@Configuration
public class QuartzConfig {

    @Bean
    public JobDetail reportJobDetail() {
        return JobBuilder.newJob(ReportGenerationJob.class)
            .withIdentity("report-job")
            .storeDurably()
            .build();
    }

    @Bean
    public Trigger reportTrigger() {
        return TriggerBuilder.newTrigger()
            .forJob(reportJobDetail())
            .withIdentity("report-trigger")
            .withSchedule(CronScheduleBuilder.cronSchedule("0 0 19 * * ?"))
            .build();
    }
}
```

**特点**：
- 支持持久化（JDBC JobStore）
- 支持集群（通过数据库锁协调）
- 失败重试
- 丰富的 Trigger 类型（Cron、Simple、Calendar）
- 监听器支持（Job/Trigger/Scheduler 生命周期）

**适用场景**：
- 分布式环境需保证定时任务单次执行
- 需要任务持久化（重启后恢复）
- 复杂调度需求（跳过节假日、等）

### 3. 消息队列 (Kafka/RabbitMQ)

```java
// 生产者：提交任务
kafkaTemplate.send("task-execution", taskPayload);

// 消费者：处理任务
@KafkaListener(topics = "task-execution", concurrency = "3")
public void executeTask(TaskPayload task) {
    execute(task);
}
```

**特点**：
- 天然异步、解耦
- 支持分布式处理（消费者组水平扩展）
- 消息持久化、重试、死信
- 不提供定时/CRON 模型
- 适用于**异步编排**而非定时调度

**适用场景**：
- 任务解耦与异步处理
- 事件驱动架构
- 需要消息可靠投递与重试

## 功能矩阵对比

| 功能 | @Scheduled | Quartz | 消息队列 |
|------|-----------|--------|---------|
| 配置复杂度 | 极低 | 中 | 高 |
| CRON 表达式 | ✓ | ✓ | ✗ |
| 单机定时 | ✓ | ✓ | ✗（需外部调度器辅助） |
| 集群支持 | ✗（重复执行） | ✓（数据库锁） | ✓（消费者组） |
| 任务持久化 | ✗ | ✓ | ✓（消息持久化） |
| 失败重试 | ✗ | ✓ | ✓ |
| 动态调度 | ✗ | ✓（API） | ✓（发送消息即可） |
| 延迟执行 | ✗（除非配合 Thread.sleep） | ✓ | ✓（Kafka 不支持延迟，RabbitMQ 支持 TTL） |
| 监控 | Spring Actuator | Quartz Monitor | Kafka Lag/Micrometer |
| 适用规模 | 小 | 中-大 | 大 |

## 选型决策

```
需要分布式协调/集群？
├── 是 → 继续
└── 否 → 
  ├── 简单定时 → @Scheduled
  └── 复杂调度 → Quartz

需要任务持久化/重启恢复？
├── 是 → Quartz 或 消息队列
└── 否 → @Scheduled

需要异步解耦/事件驱动？
├── 是 → 消息队列（如果需要定时特性，配合 Quartz 触发）
└── 否 → Quartz

需要延迟消息？
├── 是 → RabbitMQ（TTL）或 消息队列+定时器
└── 否 → 看其他需求
```

## 混合推荐架构

将多种方案组合起来：

```
Cron 触发层 (@Scheduled / Quartz)
    ↓
消息分发层 (Kafka / RabbitMQ)
    ↓
任务执行层 (@Async + ThreadPool / 消费者组)
    ↓
进度追踪层 (Kafka progress events)
    ↓
状态持久层 (DB / TaskStatus)
    ↓
实时推送层 (SSE / WebSocket / Polling)
```

这种分层架构的好处：
- 各层职责清晰
- 每层独立扩缩容
- 技术选型灵活（每层可用不同方案）

## 对引子文章的启示

引子文章的 Spring Boot + Kafka 方案，如果增加定时触发能力：

1. **简单场景**：`@Scheduled` 定期提交任务到 Kafka
2. **复杂场景**：Quartz 管理调度，Kafka 管理执行和编排
3. **分布式场景**：Quartz（集群模式） + Kafka（任务队列 + 进度事件）
