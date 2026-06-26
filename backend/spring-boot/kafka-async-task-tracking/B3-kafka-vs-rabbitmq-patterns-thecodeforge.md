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
