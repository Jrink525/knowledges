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
