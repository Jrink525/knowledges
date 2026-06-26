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
