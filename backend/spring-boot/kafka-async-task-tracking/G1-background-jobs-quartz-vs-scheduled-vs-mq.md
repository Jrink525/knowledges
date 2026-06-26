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
