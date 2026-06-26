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
