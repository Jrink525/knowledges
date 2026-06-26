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
