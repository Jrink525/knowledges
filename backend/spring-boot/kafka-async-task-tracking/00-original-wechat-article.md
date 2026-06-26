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
