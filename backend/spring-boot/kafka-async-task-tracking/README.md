# Spring Boot + Kafka 实时跟踪长时间运行任务 — MECE 知识体系

> 引子文章：[Spring Boot + Kafka，实时跟踪长时间运行任务](https://mp.weixin.qq.com/s/ibxkVE2ButhJPtUJ8txJ4A)（程序猿DD / SpringBoot实战案例锦集）
> Spring Boot 3.5.0 + Kafka 实现异步长时间任务进度跟踪（轮询 API 方案）

---

## 目录结构 (MECE 七维框架)

```
kafka-async-task-tracking/
├── README.md                                ← 本索引文件
├── A1-async-threadpool-custom-obregeon.md   ← 维度A: 自定义线程池
├── A2-async-threadpool-comprehensive-devto.md ← 维度A: 线程池优化全面指南
├── A3-async-threadpool-official-springio.md ← 维度A: Spring Boot 官方 Task Execution 文档
├── B1-kafka-rest-api-long-tasks-howtodoinjava.md ← 维度B: REST API + Kafka 进度追踪
├── B2-kafka-long-running-jobs-codex-medium.md ← 维度B: Kafka 长任务模式
├── B3-kafka-vs-rabbitmq-patterns-thecodeforge.md ← 维度B: Kafka vs RabbitMQ 选型
├── C1-rest-api-design-long-tasks-restfulapi.md ← 维度C: 长任务 REST API 设计模式
├── C2-sse-spring-boot-obregon-medium.md     ← 维度C: SSE 实时推送
├── D1-kafka-retry-dlt-spring-boot-medium.md ← 维度D: 重试与死信队列
├── E1-saga-orchestration-state-machine-substack.md ← 维度E: Saga 编排与状态机
├── F1-kafka-metrics-micrometer-javacodegeeks.md ← 维度F: Micrometer 可观测性
└── G1-background-jobs-quartz-vs-scheduled-vs-mq.md ← 维度G: 调度全景对比
```

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

**最佳实践要点**：
- 使用 String 或 Avro/Protobuf 序列化，避免 Java 序列化
- Producer: 启用 `acks=all`, `enable.idempotence=true`
- Consumer: 使用 `@Transactional` + `AckMode.MANUAL_IMMEDIATE` 保证 exactly-once
- 为每个消费者组指定独立 `group.id`
- 合理设置 `concurrency`（分区数 ≤ 消费者数）

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
> 收集自：Medium、Dev.to、howtodoinjava、restfulapi.net、TheCodeForge、JavaCodeGeeks、Substack、Spring 官方文档、Turkcell Engineering
