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
