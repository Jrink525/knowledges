---
title: "Spring 事件机制完全指南：从入门到生产级事件驱动架构"
tags:
  - spring
  - spring-events
  - event-driven
  - architecture
  - transactional-events
date: 2026-05-28
source: "综合整理自 mp.weixin.qq.com, Medium, Dev.to, Baeldung, Spring Framework 源码"
authors: "综合整理"
---

# Spring 事件机制完全指南：从入门到生产级事件驱动架构

> **遵循观察者模式**：发布者不知道谁会消费，消费者不知道谁在发布——这是 Spring 事件机制的设计哲学。

本文将**循序渐进**地覆盖：
1. 事件机制的基础概念与入门
2. Spring 事件底层源码原理
3. 同步/异步/事务事件三大模式
4. 线程模型与线程池治理
5. 生产级架构（Outbox 模式 + MQ 演进）
6. 高并发事故治理
7. 可观测性与监控
8. 架构决策与反模式

---

## 目录

- [一、为什么需要事件机制](#一为什么需要事件机制)
- [二、Spring 事件机制入门](#二spring-事件机制入门)
- [三、底层原理与源码剖析](#三底层原理与源码剖析)
- [四、同步事件详解](#四同步事件详解)
- [五、异步事件详解](#五异步事件详解)
- [六、事务事件详解](#六事务事件详解)
- [七、线程模型与线程池治理](#七线程模型与线程池治理)
- [八、高级特性：条件监听、事件链、泛型事件](#八高级特性条件监听事件链泛型事件)
- [九、生产级事件架构：领域事件与集成事件分层](#九生产级事件架构领域事件与集成事件分层)
- [十、可靠事件：Outbox 模式](#十可靠事件outbox-模式)
- [十一、从 Spring 事件到 MQ 的演进路径](#十一从-spring-事件到-mq-的演进路径)
- [十二、高并发下五类生产事故与治理](#十二高并发下五类生产事故与治理)
- [十三、可观测性与监控](#十三可观测性与监控)
- [十四、Spring 内置事件一览](#十四spring-内置事件一览)
- [十五、工程治理与最佳实践](#十五工程治理与最佳实践)
- [十六、架构决策指南](#十六架构决策指南)
- [十七、常见反模式清单](#十七常见反模式清单)
- [十八、总结](#十八总结)

---

## 一、为什么需要事件机制

### 1.1 问题场景

在一个典型业务系统中，一个"订单创建成功"往往不只是写一条订单记录，而会连带触发一系列后续动作：

- 扣减库存
- 发站内信、短信或邮件
- 写审计日志
- 推送推荐系统
- 触发履约或采购流程
- 通知 CRM、营销、风控等外围系统

### 1.2 直接调用的四大缺陷

很多项目一开始会这样写：

```java
@Service
public class OrderService {
    private final OrderRepository orderRepository;
    private final InventoryService inventoryService;
    private final NotificationService notificationService;
    private final AuditService auditService;
    private final RecommendationService recommendationService;

    @Transactional
    public Long createOrder(CreateOrderCommand command) {
        Order order = Order.create(command.userId(), command.amount(), command.items());
        orderRepository.save(order);

        inventoryService.deduct(order.getId(), command.items());
        notificationService.sendOrderCreated(order.getUserId(), order.getId());
        auditService.recordOrderCreated(order.getId(), order.getUserId());
        recommendationService.pushOrderBehavior(order.getUserId(), order.getId());

        return order.getId();
    }
}
```

这段代码在架构上存在四个根本缺陷：

| 缺陷 | 说明 |
|------|------|
| **核心流程与外围流程强耦合** | 新增一个后置动作就要修改主业务代码，违反开闭原则 |
| **整条调用链同步阻塞** | 吞吐量由最慢的下游决定，邮件慢 → 订单接口也慢 |
| **事务时间被拉长** | 数据库连接与锁持有时间变长，高并发下快速耗尽连接池 |
| **故障蔓延** | 一个外围动作失败，把本该成功的核心交易一起拖垮 |

### 1.3 事件机制的价值

> **核心思想**：把"业务已发生"与"后续如何响应"拆开。

通过事件机制，主流程只负责发布事件，所有后续动作由监听器处理，实现：

- **解耦**：发布者与消费者互不感知
- **可扩展**：新增功能只需要新增监听器
- **弹性**：异步处理防止慢操作拖垮主流程
- **可测试**：独立测试发布和消费逻辑

### 1.4 事件机制 vs 消息队列

| 维度 | Spring 事件 | 消息队列 (Kafka/RocketMQ) |
|------|-------------|--------------------------|
| **进程范围** | 同进程内 | 跨进程、跨服务 |
| **持久化** | 无（内存） | 有（磁盘） |
| **可靠投递** | 无 | 有（ACK + 重试） |
| **重播回溯** | 不支持 | 支持 |
| **吞吐量** | 受限于 JVM 内存 | 独立集群，吞吐量高 |
| **运维依赖** | 无 | 需要独立中间件 |
| **延迟** | 微秒级 | 毫秒级 |
| **适用场景** | 单体模块解耦、领域事件 | 跨服务集成、事件溯源 |

---

## 二、Spring 事件机制入门

### 2.1 三个核心角色

| 角色 | 作用 | 默认实现 |
|------|------|----------|
| **`ApplicationEventPublisher`** | 事件发布入口 | `AbstractApplicationContext` |
| **`ApplicationEventMulticaster`** | 事件分发器 | `SimpleApplicationEventMulticaster` |
| **`ApplicationListener` / `@EventListener`** | 事件监听器 | `ApplicationListenerMethodAdapter` |

### 2.2 快速上手示例

#### Step 1: 定义事件

```java
// 方式一：继承 ApplicationEvent（Spring 4.2 前必须）
public class OrderCreatedEvent extends ApplicationEvent {
    private final Long orderId;
    private final Long userId;

    public OrderCreatedEvent(Object source, Long orderId, Long userId) {
        super(source);
        this.orderId = orderId;
        this.userId = userId;
    }

    public Long getOrderId() { return orderId; }
    public Long getUserId() { return userId; }
}

// 方式二：纯 POJO（Spring 4.2+，推荐）
public record OrderCreatedEvent(Long orderId, Long userId, BigDecimal amount) {}
```

> **推荐使用 POJO/Record 方式**：不强制继承 `ApplicationEvent`，代码更简洁，且 `ApplicationEventPublisher.publishEvent()` 会自动包装为 `PayloadApplicationEvent`。

#### Step 2: 发布事件

```java
@Service
public class OrderService {
    private final ApplicationEventPublisher publisher;

    // 构造器注入（推荐，取代 @Autowired）
    public OrderService(ApplicationEventPublisher publisher) {
        this.publisher = publisher;
    }

    @Transactional
    public Long createOrder(CreateOrderCommand command) {
        // 1. 核心业务逻辑
        Order order = Order.create(command.userId(), command.items());
        orderRepository.save(order);

        // 2. 发布事件
        publisher.publishEvent(new OrderCreatedEvent(order.getId(), order.getUserId(), order.getPayableAmount()));

        return order.getId();
    }
}
```

> **关键**：`ApplicationContext` 接口继承了 `ApplicationEventPublisher`，所以容器内的任意 Bean 都可以注入并发布事件。

#### Step 3: 监听事件

```java
@Component
public class InventoryReservationListener {

    private final InventoryService inventoryService;

    public InventoryReservationListener(InventoryService inventoryService) {
        this.inventoryService = inventoryService;
    }

    @EventListener
    public void handle(OrderCreatedEvent event) {
        inventoryService.deduct(event.orderId());
        System.out.println("库存已扣减，订单: " + event.orderId());
    }
}
```

### 2.3 两种监听方式对比

#### 方式 A：注解式（推荐）

```java
@Component
public class EmailNotificationListener {

    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        // 处理事件
    }
}
```

#### 方式 B：接口式

```java
@Component
public class EmailNotificationListener implements ApplicationListener<OrderCreatedEvent> {

    @Override
    public void onApplicationEvent(OrderCreatedEvent event) {
        // 处理事件
    }
}
```

| 维度 | `@EventListener` | `ApplicationListener` |
|------|-----------------|----------------------|
| **简洁性** | ✅ 方法级别，灵活 | ❌ 需要实现接口 |
| **多事件处理** | ✅ 一个类多个方法 | ❌ 一个类只能监听一种类型 |
| **条件过滤** | ✅ `condition` 属性 | ❌ 需要手写 if |
| **返回值发布** | ✅ 返回值自动发布为新事件 | ❌ 不支持 |
| **Spring 版本** | 4.2+ | 任意版本 |

---

## 三、底层原理与源码剖析

理解 Spring 事件机制的底层源码，才能真正理解为什么生产环境经常踩坑。

### 3.1 核心类关系

```
ApplicationEventPublisher
        ↑ 继承
ApplicationContext
        ↑ 实现
AbstractApplicationContext
        ├── 维护一个 ApplicationEventMulticaster
        └── publishEvent() 委托给 multicaster

ApplicationEventMulticaster
        ↑ 实现
SimpleApplicationEventMulticaster
        ├── 持有 Listener 注册表
        ├── 可配置 TaskExecutor
        └── 负责遍历并调用监听器
```

### 3.2 事件发布完整链路

当调用 `publisher.publishEvent(event)` 时，底层执行链路如下：

```
1. ApplicationEventPublisher.publishEvent(event)
   └─ AbstractApplicationContext.publishEvent(Object event)
      ├─ 2. 如果 event 不是 ApplicationEvent 子类
      │      → 包装为 PayloadApplicationEvent
      │      → 解析 ResolvableType（泛型信息）
      ├─ 3. 获取 ApplicationEventMulticaster
      ├─ 4. 调用 multicaster.multicastEvent(event, eventType)
      └─ 5. SimpleApplicationEventMulticaster 执行分发
```

### 3.3 SimpleApplicationEventMulticaster 核心源码

```java
// SimpleApplicationEventMulticaster.java（简化版）
public class SimpleApplicationEventMulticaster extends AbstractApplicationEventMulticaster {

    @Nullable
    private Executor taskExecutor;

    @Nullable
    private ErrorHandler errorHandler;

    @Override
    public void multicastEvent(ApplicationEvent event, @Nullable ResolvableType eventType) {
        ResolvableType type = (eventType != null) ? eventType : resolveDefaultEventType(event);
        // 获取所有匹配该事件类型的监听器（有缓存）
        for (ApplicationListener<?> listener : getApplicationListeners(event, type)) {
            Executor executor = getTaskExecutor();
            if (executor != null) {
                // 如果有 TaskExecutor → 异步执行
                executor.execute(() -> invokeListener(listener, event));
            } else {
                // 默认 → 同步执行（同一线程）
                invokeListener(listener, event);
            }
        }
    }

    private void invokeListener(ApplicationListener<?> listener, ApplicationEvent event) {
        ErrorHandler errorHandler = getErrorHandler();
        if (errorHandler != null) {
            try {
                listener.onApplicationEvent(event);
            } catch (Throwable err) {
                errorHandler.handleError(err);
            }
        } else {
            listener.onApplicationEvent(event);
        }
    }
}
```

> **两个关键事实**：
> 1. **默认是同步执行** — 如果没有设置 `taskExecutor`，所有监听器在当前线程串行执行
> 2. **默认没有 ErrorHandler** — 监听器抛异常会直接往外传播

### 3.4 @EventListener 的注册机制

`@EventListener` 的监听器并不是自动"魔法"生效的，而是通过 `EventListenerMethodProcessor` 完成的：

```
Spring 容器启动
  └─ refresh() → finishBeanFactoryInitialization()
      └─ EventListenerMethodProcessor（实现了 SmartInitializingSingleton）
          ├─ 扫描所有单例 Bean
          ├─ 找到标注 @EventListener 的方法
          ├─ 包装为 ApplicationListenerMethodAdapter
          └─ 注册到 ApplicationEventMulticaster
```

核心代码路径：

```java
// EventListenerMethodProcessor.java
@Override
public void afterSingletonsInstantiated() {
    for (String beanName : beanNames) {
        Class<?> type = beanFactory.getType(beanName);
        if (type != null && isEligible(type)) {
            // 处理 @EventListener 方法
            processBean(beanName, type);
        }
    }
}

private void processBean(String beanName, Class<?> targetType) {
    for (Method method : targetType.getDeclaredMethods()) {
        EventListener ann = method.getAnnotation(EventListener.class);
        if (ann != null) {
            // 包装为 ApplicationListenerMethodAdapter
            ApplicationListener<?> listener = createApplicationListener(beanName, targetType, method);
            // 注册到 multicaster
            context.addApplicationListener(listener);
        }
    }
}
```

### 3.5 监听器匹配与缓存

`AbstractApplicationEventMulticaster` 内部通过 `ListenerRetriever` 缓存匹配结果：

```java
// AbstractApplicationEventMulticaster.java
private final ConcurrentHashMap<ListenerCacheKey, ListenerRetriever> retrievalCache = new ConcurrentHashMap<>();

private class ListenerCacheKey {
    private final ResolvableType eventType;
    private final Class<?> sourceType;

    // equals/hashCode 基于 eventType 和 sourceType
}
```

- **首次匹配**：遍历全部监听器，进行 `instanceof` / `ResolvableType` 匹配，缓存结果
- **后续匹配**：直接从缓存获取，O(1) 复杂度

这意味着：
- 监听器数量增加会影响**首轮**匹配成本
- 高频事件类型在稳定运行后开销会下降
- 但事件分发本身依然在应用进程内完成，不具备中间件级隔离能力

### 3.6 @TransactionalEventListener 的底层实现

`@TransactionalEventListener` 不是 Spring 事件分发器的原生能力，而是通过**事务同步管理器** `TransactionSynchronizationManager` 实现的：

```java
// TransactionalApplicationListenerMethodAdapter（简化）
@Override
public void onApplicationEvent(ApplicationEvent event) {
    if (TransactionSynchronizationManager.isSynchronizationActive()) {
        // 注册事务同步回调
        TransactionSynchronizationManager.registerSynchronization(
            new TransactionSynchronization() {
                @Override
                public void beforeCommit(boolean readOnly) {
                    if (phase == BEFORE_COMMIT) invokeListener(event);
                }

                @Override
                public void afterCommit() {
                    if (phase == AFTER_COMMIT) invokeListener(event);
                }

                @Override
                public void afterCompletion(int status) {
                    if (phase == AFTER_COMPLETION ||
                        (phase == AFTER_COMMIT && status == STATUS_COMMITTED) ||
                        (phase == AFTER_ROLLBACK && status == STATUS_ROLLED_BACK)) {
                        invokeListener(event);
                    }
                }
            }
        );
    } else {
        // 没有活跃事务 → 立即执行
        invokeListener(event);
    }
}
```

> **关键**：如果当前没有活跃事务，`@TransactionalEventListener` 会**立即执行**，而不是等待"不存在的事务提交"。这是容易被忽略的 bug 来源。

---

## 四、同步事件详解

### 4.1 默认行为

Spring 事件**默认是同步的**。`publishEvent()` 在当前线程阻塞，直到所有匹配的监听器执行完毕才返回。

```java
@EventListener
public void sendEmail(OrderCreatedEvent event) {
    // 如果这里耗时 2 秒，主流程也会阻塞 2 秒
    remoteEmailClient.send(event.userId(), "订单已创建");
}
```

### 4.2 同步事件的影响

```java
@Transactional
public Long createOrder(CreateOrderCommand command) {
    Order order = orderRepository.save(Order.create(command));
    publisher.publishEvent(new OrderCreatedEvent(order.getId(), order.getUserId()));
    return order.getId();
}
```

如果监听器是同步的且耗时 2 秒：
- **事务多持有 2 秒** — 数据库连接被长时间占用
- **Web 线程多阻塞 2 秒** — Tomcat 线程池被快速填满
- **高并发下** — 连接池和线程池会被快速压满

### 4.3 同步事件的正确用途

**适合**：
- 必须与主事务一起成功/失败的本地校验
- 轻量且确定性的同步动作（内存状态刷新、本地缓存更新）
- 监听器内也需参与当前事务的场景

**不适合**：
- 发短信、发邮件、调用三方接口
- 需要独立失败重试的外围动作
- 会长时间阻塞的 I/O 操作

### 4.4 保持监听器顺序

```java
@Component
public class OrderEventListeners {

    @Order(1)
    @EventListener
    public void validateInventory(OrderCreatedEvent event) {
        // 先执行：库存校验
    }

    @Order(2)
    @EventListener
    public void calculateDiscount(OrderCreatedEvent event) {
        // 后执行：计算折扣
    }

    @Order(3)
    @EventListener
    public void notifyWarehouse(OrderCreatedEvent event) {
        // 最后执行：通知仓库
    }
}
```

> **注意**：`@Order` 只能保证同步模式下同一分发器的顺序。如果用了 `@Async`，顺序语义会弱化。

---

## 五、异步事件详解

### 5.1 开启异步

```java
@Configuration
@EnableAsync
public class AsyncConfig {
}
```

### 5.2 在监听器上标注 @Async

```java
@Component
public class CouponIssueListener {

    @Async
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handle(OrderCreatedEvent event) {
        couponService.issueNewUserCoupon(event.userId(), event.orderId());
    }
}
```

### 5.3 @Async + @TransactionalEventListener 组合的意义

这套组合是生产环境中最常见的写法：
- **主事务里发布事件**
- **`AFTER_COMMIT`** 确保数据已落库
- **`@Async`** 保证不阻塞交易线程

### 5.4 异步事件的限制

| 限制 | 说明 |
|------|------|
| **无返回值** | `@Async` + `@EventListener` 方法只能返回 `void` |
| **异常不传播** | 异步线程中的异常不会抛回发布者线程 |
| **事务不传播** | 异步监听器不参与发布者的事务上下文 |

### 5.5 异步异常处理

由于异步异常不会传播到调用方，必须显式处理：

```java
@Configuration
@EnableAsync
public class AsyncEventConfig implements AsyncConfigurer {

    @Override
    public Executor getAsyncExecutor() {
        // 自定义线程池...
    }

    @Override
    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
        return (ex, method, params) -> {
            String methodName = method.getDeclaringClass().getSimpleName() + "#" + method.getName();
            LoggerFactory.getLogger(method.getDeclaringClass())
                .error("Async event execution failed, method={}, params={}", methodName, params, ex);
        };
    }
}
```

---

## 六、事务事件详解

### 6.1 @EventListener 的事务语义

如果在事务方法中发布事件：

```java
@Transactional
public void createOrder(CreateOrderCommand command) {
    Order order = orderRepository.save(Order.create(command));
    publisher.publishEvent(new OrderCreatedEvent(order.getId(), order.getUserId()));
}
```

普通 `@EventListener` 的执行时机：
- 发生在**当前事务内部**
- 与发布者共用**同一线程**
- 监听器抛异常会**影响主事务**

### 6.2 @TransactionalEventListener 的执行时机

```java
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
public void onOrderCreated(OrderCreatedEvent event) {
    auditService.record(event.orderId());
}
```

| 阶段 | 说明 | 典型用途 |
|------|------|----------|
| `BEFORE_COMMIT` | 提交前执行 | 提交前补充状态 |
| `AFTER_COMMIT` | 提交成功后执行 | 通知、日志、集成事件（**最常用**） |
| `AFTER_ROLLBACK` | 回滚后执行 | 回滚补偿、失败告警 |
| `AFTER_COMPLETION` | 完成后执行，不关心提交或回滚 | 资源清理 |

### 6.3 为什么事务提交后再通知更安全

假设在事务内发了短信：

```java
@EventListener  // 默认：在事务内部执行
public void sendSms(OrderCreatedEvent event) {
    smsService.send("下单成功");
}
```

如果后面主事务因为唯一键冲突、死锁或超时回滚：
- ❌ 用户已经收到"下单成功"的短信
- ❌ 但数据库里订单并不存在

这是典型的**数据与副作用不一致**。

```java
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)  // 提交后才执行
public void sendSms(OrderCreatedEvent event) {
    smsService.send("下单成功");
}
```

> 只有订单真的提交成功，通知才会发出。

### 6.4 事务事件的核心源码机制

`@TransactionalEventListener` 通过 `TransactionSynchronization` 机制实现：

```java
// 概念源码
TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
    @Override
    public void afterCommit() {
        // 这里执行业务逻辑
        listener.invoke(event);
    }
});
```

`TransactionSynchronization` 的 `afterCommit()` 是在**事务提交成功之后、资源释放之前**回调的。此时数据库连接还没关闭，但事务已经通过 `commit`（数据已落盘）。

### 6.5 事务事件的注意事项

```java
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
public void handle(OrderCreatedEvent event) {
    // ⚠️ 事务已提交，此处做的任何数据库操作都是在新事务中执行的
    // ⚠️ 如果此处也使用了 @Transactional，是新事务
    auditService.record(event.orderId());
}
```

- **没有活跃事务时**：`@TransactionalEventListener` 会**立即执行**（fallback 行为）
- **嵌套事务**：只对最外层事务生效
- **只读事务**：`AFTER_COMMIT` 仍会触发（尽管没有实际写操作）

---

## 七、线程模型与线程池治理

### 7.1 默认线程模型

```
发布者线程
  ├── 监听器 1（同步）
  ├── 监听器 2（同步）
  └── 监听器 3（同步）
```

所有监听器串行执行，任何一个慢都会阻塞后续全部。

### 7.2 自定义 ApplicationEventMulticaster（全局异步）

```java
@Configuration
public class EventMulticasterConfig {

    @Bean(name = "applicationEventMulticaster")
    public ApplicationEventMulticaster applicationEventMulticaster() {
        SimpleApplicationEventMulticaster multicaster = new SimpleApplicationEventMulticaster();
        multicaster.setTaskExecutor(Executors.newFixedThreadPool(5));
        return multicaster;
    }
}
```

> **配置了 `TaskExecutor` 后，所有事件都会异步执行**。但这样会失去同步事件的能力，不推荐。建议按需使用 `@Async` 做细粒度控制。

### 7.3 生产级线程池配置

```java
@Configuration
@EnableAsync
public class AsyncEventConfig implements AsyncConfigurer {

    @Bean("orderEventExecutor")
    public Executor orderEventExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();

        // 常驻线程数
        executor.setCorePoolSize(8);
        // 最大线程数（队列满后才扩容到此值）
        executor.setMaxPoolSize(16);
        // 队列容量
        executor.setQueueCapacity(2000);
        // 空闲线程存活时间
        executor.setKeepAliveSeconds(60);
        // 线程名前缀（方便排查）
        executor.setThreadNamePrefix("order-event-");

        // 优雅停机：等待已提交任务完成
        executor.setWaitForTasksToCompleteOnShutdown(true);
        executor.setAwaitTerminationSeconds(30);

        // 拒绝策略：让调用者线程自己执行（回压）
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());

        // TaskDecorator：传递 MDC 上下文（TraceId 透传）
        executor.setTaskDecorator(runnable -> {
            Map<String, String> contextMap = MDC.getCopyOfContextMap();
            return () -> {
                if (contextMap != null) {
                    MDC.setContextMap(contextMap);
                }
                try {
                    runnable.run();
                } finally {
                    MDC.clear();
                }
            };
        });

        executor.initialize();
        return executor;
    }

    @Override
    public Executor getAsyncExecutor() {
        return orderEventExecutor();
    }

    @Override
    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
        return (ex, method, params) -> {
            String methodName = method.getDeclaringClass().getSimpleName() + "#" + method.getName();
            LoggerFactory.getLogger(method.getDeclaringClass())
                .error("Async event execution failed, method={}, params={}", methodName, params, ex);
        };
    }
}
```

### 7.4 参数设计的工程考量

| 参数 | 含义 | 配置建议 |
|------|------|----------|
| `corePoolSize` | 稳定运行时常驻线程数 | 过小 → 任务积压；过大 → 上下文切换开销 |
| `maxPoolSize` | 最大线程数（队列满后扩容） | 不要配太大，否则故障时抖动放大 |
| `queueCapacity` | 队列容量 | 不是越大越好：延迟失控、故障堆积不可见、内存被大量占用 |
| `CallerRunsPolicy` | 拒绝策略 | 回压到调用线程，主流程延迟增加但可接受 |
| `TaskDecorator` | 任务装饰器 | 用于传递 TraceId、安全上下文等 |

### 7.5 线程池隔离原则

```java
@Bean("orderEventExecutor")   // 订单事件用独立池
@Bean("notificationExecutor") // 通知事件用独立池
@Bean("auditExecutor")        // 审计用独立池
```

> **不要让所有异步任务共用一个"万能线程池"**。不同优先级、不同延迟容忍度的事件应该用不同的线程池隔离。

### 7.6 CPU 密集 vs I/O 密集

| 任务类型 | 线程数建议 |
|----------|-----------|
| CPU 密集 | 接近 CPU 核数（通常是 `N+1`） |
| I/O 密集 | 可适度放大，但必须压测验证 |

---

## 八、高级特性：条件监听、事件链、泛型事件

### 8.1 条件监听

通过 `condition` 属性使用 SpEL 表达式过滤事件：

```java
@Component
public class LargeOrderHandler {

    @EventListener(condition = "#event.amount().compareTo(T(java.math.BigDecimal).valueOf(10000)) > 0")
    public void handleLargeOrder(OrderCreatedEvent event) {
        riskService.markForManualReview(event.orderId());
    }
}
```

**适合**：
- 高价值订单特殊处理
- 分渠道差异逻辑
- 低频条件化旁路

**不适合**：
- 复杂业务规则（SpEL 过多会让规则散落在注解里，不利于治理）

### 8.2 事件链（返回值自动发布）

`@EventListener` 方法如果有非 `void` 返回值，会被自动当成新事件再次发布：

```java
@EventListener
public PaymentRequiredEvent onOrderCreated(OrderCreatedEvent event) {
    // 返回一个新事件 → Spring 自动发布
    return new PaymentRequiredEvent(event.orderId(), event.amount());
}

@EventListener
public void onPaymentRequired(PaymentRequiredEvent event) {
    // 处理支付请求
}
```

甚至支持返回集合：

```java
@EventListener
public List<Object> onOrderCreated(OrderCreatedEvent event) {
    return List.of(
        new PaymentRequiredEvent(event.orderId(), event.amount()),
        new InventoryCheckEvent(event.orderId())
    );
}
```

> **推荐原则**：一到两跳的轻量事件链可以接受。三跳以上就应该评估是否改为显式编排（Saga、状态机、工作流引擎）。

### 8.3 泛型事件

```java
// 定义泛型事件
public class GenericEvent<T> extends ApplicationEvent implements ResolvableTypeProvider {
    private final T payload;

    public GenericEvent(Object source, T payload) {
        super(source);
        this.payload = payload;
    }

    public T getPayload() { return payload; }

    @Override
    public ResolvableType getResolvableType() {
        return ResolvableType.forClassWithGenerics(
            getClass(),
            ResolvableType.forInstance(payload)
        );
    }
}

// 监听具体泛型类型
@Component
public class UserCreatedListener {

    @EventListener
    public void handleUserCreated(GenericEvent<User> event) {
        User user = event.getPayload();
        // 处理用户创建
    }
}
```

> 如果泛型事件不实现 `ResolvableTypeProvider`，Spring 无法区分类型参数，会导致所有泛型类型都匹配所有监听器。

### 8.4 按优先级排序

```java
@Order(1)
@EventListener
public void first(OrderCreatedEvent event) { }

@Order(2)
@EventListener
public void second(OrderCreatedEvent event) { }
```

> **注意**：优先级只能保证**同一事件分发器下**的执行顺序。如果用了异步执行器，顺序语义会弱化。

---

## 九、生产级事件架构：领域事件与集成事件分层

### 9.1 为什么需要分层

项目中很多问题的根源不是不会写监听器，而是事件语义混乱。建议将事件明确分为两层：

### 9.2 领域内事件

用于当前进程内部的业务解耦：

```java
// 领域事件：承载丰富的业务语义
public record OrderCreatedDomainEvent(
    Long orderId,
    Long userId,
    BigDecimal amount,
    Instant occurredAt
) {}

public record OrderPaidDomainEvent(
    Long orderId,
    Long paymentId,
    Instant paidAt
) {}
```

**特点**：
- 生命周期短
- 只在单服务内部传播
- 可承载丰富的领域语义

### 9.3 集成事件

用于跨服务传播：

```java
// 集成事件：稳定、版本化、含基础设施字段
public record OrderCreatedIntegrationEvent(
    String eventId,
    String eventType,
    Long orderId,
    Long userId,
    BigDecimal amount,
    Instant occurredAt,
    String traceId,
    int version
) {}
```

**特点**：
- 要考虑版本兼容
- 要考虑字段裁剪和稳定性
- 要考虑序列化协议、幂等键、追踪字段

### 9.4 核心转换策略

不要把 JPA 实体、领域对象原样丢到 MQ 或监听器里。在事务提交后，把领域事件转换成稳定的集成事件：

```java
// 在集成事件监听器中做转换
@Component
public class OrderIntegrationEventListener {

    private final KafkaTemplate<String, Object> kafkaTemplate;

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onOrderCreated(OrderCreatedDomainEvent domainEvent) {
        // 领域事件 → 集成事件 转换
        OrderCreatedIntegrationEvent integrationEvent = new OrderCreatedIntegrationEvent(
            UUID.randomUUID().toString(),
            "OrderCreated",
            domainEvent.orderId(),
            domainEvent.userId(),
            domainEvent.amount(),
            domainEvent.occurredAt(),
            MDC.get("traceId"),
            1
        );

        kafkaTemplate.send("order-events", integrationEvent);
    }
}
```

### 9.5 推荐目录结构

```
order-service/
├── application/
│   ├── service/
│   │   └── OrderApplicationService.java
│   └── event/
│       ├── OrderDomainEventPublisher.java
│       └── listener/
│           ├── InventoryReservationListener.java
│           ├── OrderAuditListener.java
│           ├── CouponIssueListener.java
│           └── OrderIntegrationEventListener.java
├── domain/
│   ├── model/
│   │   └── Order.java
│   └── event/
│       └── OrderCreatedDomainEvent.java
├── infrastructure/
│   ├── config/
│   │   ├── AsyncEventConfig.java
│   │   ├── EventMulticasterConfig.java
│   │   └── JacksonConfig.java
│   ├── outbox/
│   │   ├── OutboxEvent.java
│   │   ├── OutboxEventRepository.java
│   │   └── OutboxRelayJob.java
│   └── messaging/
│       ├── KafkaEventPublisher.java
│       └── OrderEventConsumer.java
└── interfaces/
    └── rest/
        └── OrderController.java
```

---

## 十、可靠事件：Outbox 模式

### 10.1 为什么需要 Outbox

Spring 本地事件有一个根本缺陷：事件发布在内存中，没有持久化。如果：
- 在 `publishEvent()` 之后、监听器执行之前应用崩溃
- 异步监听器在执行过程中失败且未重试

事件就会**丢失**。

> **核心问题**：保证"数据库事务提交"和"事件发布"的原子性。

### 10.2 Outbox 模式原理

```
主流程：
  1. 在业务事务中，同时写入业务表和 Outbox 表（同一个数据库事务）
  2. 事务提交成功
  3. Outbox Relay 从 Outbox 表中读取未发送的记录
  4. 发送到消息队列
  5. 发送成功后删除 Outbox 记录

              ┌──────────────────────┐
              │   同一个事务           │
  用户请求 →  │  ├─ 业务表 INSERT     │
              │  └─ Outbox 表 INSERT  │
              └─────────┬────────────┘
                        │ 事务提交
                        ▼
              ┌──────────────────────┐
              │   Outbox Relay Job   │
              │   (定时或 CDC 触发)    │
              └─────────┬────────────┘
                        │
                        ▼
              ┌──────────────────────┐
              │   Kafka / MQ         │
              └──────────────────────┘
```

### 10.3 Outbox 表设计

```sql
CREATE TABLE outbox_events (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    event_id        VARCHAR(64)  NOT NULL UNIQUE,
    aggregate_type  VARCHAR(64)  NOT NULL,   -- 聚合类型，如 "Order"
    aggregate_id    VARCHAR(64)  NOT NULL,   -- 聚合 ID，如 "orderId=12345"
    event_type      VARCHAR(128) NOT NULL,   -- 事件类型，如 "OrderCreated"
    payload         JSON         NOT NULL,   -- 事件体（JSON 序列化）
    trace_id        VARCHAR(64),             -- 追踪 ID
    status          VARCHAR(16)  NOT NULL DEFAULT 'PENDING', -- PENDING / SENT / FAILED
    retry_count     INT          DEFAULT 0,
    created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_at         TIMESTAMP
);

CREATE INDEX idx_outbox_status_created ON outbox_events(status, created_at);
```

### 10.4 领域事件发布器 + Outbox

```java
@Component
public class OrderDomainEventPublisher {
    private final ApplicationEventPublisher publisher;
    private final OutboxEventRepository outboxRepository;

    public OrderDomainEventPublisher(ApplicationEventPublisher publisher,
                                     OutboxEventRepository outboxRepository) {
        this.publisher = publisher;
        this.outboxRepository = outboxRepository;
    }

    @Transactional
    public void publishOrderCreated(Order order) {
        // 1. 写 Outbox 表（和业务在同一个事务）
        OutboxEvent outboxEvent = new OutboxEvent();
        outboxEvent.setEventId(UUID.randomUUID().toString());
        outboxEvent.setAggregateType("Order");
        outboxEvent.setAggregateId(String.valueOf(order.getId()));
        outboxEvent.setEventType("OrderCreated");
        outboxEvent.setPayload(toJson(new OrderCreatedIntegrationEvent(/*...*/)));
        outboxEvent.setTraceId(MDC.get("traceId"));
        outboxRepository.save(outboxEvent);

        // 2. 发布领域事件（进程内）
        publisher.publishEvent(new OrderCreatedDomainEvent(
            order.getId(), order.getUserId(), order.getPayableAmount(), Instant.now()
        ));
    }
}
```

### 10.5 Outbox Relay 实现

```java
@Component
public class OutboxRelayJob {

    private final OutboxEventRepository outboxRepository;
    private final KafkaTemplate<String, String> kafkaTemplate;

    @Scheduled(fixedDelay = 5000)  // 每 5 秒轮询一次
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void relayPendingEvents() {
        List<OutboxEvent> pendingEvents = outboxRepository.findTop100ByStatusOrderByCreatedAtAsc("PENDING");

        for (OutboxEvent event : pendingEvents) {
            try {
                // 发送到 Kafka
                kafkaTemplate.send("order-events", event.getPayload()).get(5, TimeUnit.SECONDS);

                // 标记为已发送
                event.setStatus("SENT");
                event.setSentAt(Instant.now());
                outboxRepository.save(event);
            } catch (Exception e) {
                event.setRetryCount(event.getRetryCount() + 1);
                if (event.getRetryCount() >= 3) {
                    event.setStatus("FAILED");
                }
                outboxRepository.save(event);
                log.error("Failed to relay outbox event: {}", event.getEventId(), e);
            }
        }
    }
}
```

### 10.6 Outbox 的变体方案

| 方案 | 原理 | 优缺点 |
|------|------|--------|
| **定时轮询** | @Scheduled 定时查询 Outbox 表 | 简单，有延迟 |
| **CDC (Change Data Capture)** | Debezium 监听 MySQL binlog | 实时、零侵入，但需额外运维 |
| **事务消息（RocketMQ）** | MQ 提供事务消息 API | 少了一张表，但依赖 MQ 特性 |
| **Spring 事务同步** | 事务提交后发 MQ | 简单但窗口期丢消息 |

---

## 十一、从 Spring 事件到 MQ 的演进路径

### 11.1 三阶段渐进式演进

```
阶段一：进程内解耦
    @EventListener → 同步/异步监听器

阶段二：事务边界补齐
    @TransactionalEventListener + @Async + 独立线程池

阶段三：可靠集成事件
    Outbox + Kafka/RocketMQ + 幂等重试
```

### 11.2 第一阶段：纯 Spring 事件

```java
// 进程内解耦，单体应用适用
@Service
public class OrderService {
    @Transactional
    public void createOrder(CreateOrderCommand cmd) {
        // 业务逻辑
        publisher.publishEvent(new OrderCreatedDomainEvent(...));
    }
}
```

### 11.3 第二阶段：Spring 事件 + 事务事件

```java
@Component
public class AuditListener {

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    @Async
    public void onOrderCreated(OrderCreatedDomainEvent event) {
        // 事务提交后的异步处理
        auditService.record(event.orderId());
    }
}
```

### 11.4 第三阶段：Spring 事件 + Outbox + MQ

```java
// 1. 写 Outbox 表（和业务同一事务）
// 2. 进程内事件处理
// 3. Outbox Relay 推送到 Kafka
// 4. 跨服务消费
```

### 11.5 什么时候该直接上 MQ

| 决策条件 | 建议 |
|----------|------|
| 单体项目、模块解耦 | Spring 本地事件 |
| 偶尔的异步后置动作 | Spring 事件 + @Async |
| 需要事务提交后的可靠通知 | Spring 事件 + Outbox + MQ |
| 分布式协作、事件溯源 | 直接上 Kafka/RocketMQ |
| 高吞吐量、流处理 | 直接上 Kafka |
| 对顺序性和一致性要求高 | 使用 MQ 的严格顺序 + 幂等 |

---

## 十二、高并发下五类生产事故与治理

### 12.1 事故一：同步监听器导致长事务

**表现**：
- 数据库连接池耗尽
- 接口 RT 飙升
- 大量线程阻塞在外部 I/O

**根因**：
慢监听器仍在主事务内同步执行。

**治理**：
- 交易主链路只保留必要的同步动作
- 所有外围 I/O 改成 `AFTER_COMMIT` + `@Async`

### 12.2 事故二：监听器异常把主交易回滚

```java
@EventListener
public void handle(OrderCreatedDomainEvent event) {
    throw new IllegalStateException("inventory system failure");
}
```

**后果**：主事务跟着回滚，订单创建失败。

**治理**：
- 把非核心动作移到 `@TransactionalEventListener(AFTER_COMMIT)`
- 对异步监听器做异常捕获、重试和告警

### 12.3 事故三：异步异常静默丢失

**场景**：`void` 返回值的 `@Async` 方法抛出异常，只留在线程池里，业务方毫无感知。

**治理**：
- 统一配置 `AsyncUncaughtExceptionHandler`
- 将失败打到监控、日志、告警平台
- 对关键监听器增加失败持久化

### 12.4 事故四：监听器里直接查刚提交的数据却读不到

**场景**：使用了普通 `@EventListener`（仍在事务内），监听器去查数据库，但数据还没提交。

**治理**：
- 明确使用 `@TransactionalEventListener(phase = AFTER_COMMIT)`
- 不在普通 `@EventListener` 里假设"数据库已经提交"

### 12.5 事故五：事件风暴

```java
@EventListener
public void onOrderCreated(OrderCreatedDomainEvent event) {
    publisher.publishEvent(new OrderCreatedDomainEvent(/*...*/));
}
```

**后果**：没有清晰边界 → 事件链闭环 → 重复触发 → 事件风暴 → 系统雪崩。

**治理**：
- 事件命名语义清晰
- 监听器只做单向流转
- 复杂编排交给 Saga、状态机或工作流引擎

---

## 十三、可观测性与监控

### 13.1 自定义 ApplicationEventMulticaster 添加指标

```java
@Configuration
public class EventMulticasterConfig {

    @Bean("applicationEventMulticaster")
    public SimpleApplicationEventMulticaster applicationEventMulticaster(
            MeterRegistry meterRegistry) {
        SimpleApplicationEventMulticaster multicaster = new SimpleApplicationEventMulticaster() {
            @Override
            public void multicastEvent(ApplicationEvent event, ResolvableType eventType) {
                String eventName = event.getClass().getSimpleName();

                // 计数
                Counter.builder("application.event.publish.total")
                    .tag("event", eventName)
                    .register(meterRegistry)
                    .increment();

                // 耗时
                Timer.Sample sample = Timer.start(meterRegistry);
                try {
                    super.multicastEvent(event, eventType);
                } finally {
                    sample.stop(Timer.builder("application.event.publish.latency")
                        .tag("event", eventName)
                        .register(meterRegistry));
                }
            }
        };
        return multicaster;
    }
}
```

### 13.2 日志字段建议

所有事件日志尽量统一带上：

```
traceId     — 追踪链路 ID
eventId     — 事件唯一 ID
eventType   — 事件类型
aggregateId — 聚合根 ID
listener    — 监听器名称
retryCount  — 重试次数
status      — 处理状态
```

```java
log.info("Event processed, eventId={}, eventType={}, aggregateId={}, listener={}, status={}",
    event.getEventId(), event.getClass().getSimpleName(), orderId,
    this.getClass().getSimpleName(), "SUCCESS");
```

### 13.3 需要监控的关键指标

| 指标 | 意义 | 告警阈值 |
|------|------|----------|
| `application.event.publish.total` | 事件发布总数 | 异常突增/突降 |
| `application.event.publish.latency` | 事件处理耗时 | P99 > 1s |
| `thread.pool.queue.size` | 事件线程池队列积压 | > 500 |
| `kafka.consumer.lag` | 消费者积压 | > 1000 |
| `outbox.pending.count` | Outbox 待发送数量 | > 100 |
| `outbox.failed.count` | Outbox 失败数量 | > 0 |

---

## 十四、Spring 内置事件一览

Spring 容器在生命周期中会发布一系列内置事件：

| 事件 | 触发时机 |
|------|----------|
| `ContextRefreshedEvent` | ApplicationContext 刷新完成时 |
| `ContextStartedEvent` | 调用 `start()` 方法时 |
| `ContextStoppedEvent` | 调用 `stop()` 方法时 |
| `ContextClosedEvent` | ApplicationContext 关闭时 |
| `RequestHandledEvent` | HTTP 请求处理完成时（仅 Web 应用） |
| `ServletRequestHandledEvent` | Servlet 请求处理完成时（更详细） |

```java
@Component
public class ContextReadyListener {

    @EventListener
    public void onContextRefreshed(ContextRefreshedEvent event) {
        System.out.println("容器初始化完毕，可以执行预热逻辑");
        // 加载缓存、初始化连接池等
    }

    @EventListener
    public void onContextClosed(ContextClosedEvent event) {
        System.out.println("容器关闭，执行资源清理");
        // 关闭连接、释放资源等
    }
}
```

---

## 十五、工程治理与最佳实践

### 15.1 事件设计原则

#### 不要把实体对象直接作为事件体

```java
// ❌ 错误：把 JPA 实体直接发布
publisher.publishEvent(orderEntity);

// ✅ 正确：独立建模事件
publisher.publishEvent(new OrderCreatedDomainEvent(order.getId(), order.getUserId(), order.getAmount()));
```

**问题**：
- 暴露过多内部字段
- 容易引入懒加载问题（LazyInitializationException）
- 事件结构不稳定
- 跨服务序列化风险高

#### 事件对象必备字段

```java
public record OrderCreatedIntegrationEvent(
    String eventId,          // 唯一事件 ID（UUID）
    String eventType,        // 事件类型
    Long orderId,            // 业务 ID
    Long userId,
    BigDecimal amount,
    Instant occurredAt,      // 事件发生时间
    String traceId,          // 追踪 ID
    int version              // 事件版本号
) {}
```

#### 版本演进原则

- 新增字段优先，少做破坏性修改
- 保持旧消费者兼容（添加字段而非修改字段类型）
- 大变更时升级 `version`
- 事件契约和 API 一样需要治理

### 15.2 监听器设计原则

#### 监听器逻辑要轻量

```java
// ❌ 不要在监听器里写大量业务逻辑
@EventListener
public void handle(OrderCreatedEvent event) {
    // 大量复杂计算...
    // 多个外部调用...
    // 复杂的条件分支...
}

// ✅ 监听器只做"桥接"，逻辑委托给 Service
@EventListener
public void handle(OrderCreatedEvent event) {
    notificationService.sendWelcomeEmail(event.userId());
}
```

#### 幂等性考虑

```java
// 消费端必须幂等
@EventListener
public void handleCouponIssue(CouponIssuedEvent event) {
    // 幂等检查：消费记录表做唯一键约束
    if (couponConsumptionLog.existsByEventId(event.eventId())) {
        log.info("Duplicate event, skipping: {}", event.eventId());
        return;
    }
    couponService.issue(event.userId(), event.couponId());
}
```

### 15.3 事件命名规范

| 类型 | 命名规范 | 示例 |
|------|----------|------|
| 领域事件 | `{Aggregate}{Action}DomainEvent` | `OrderCreatedDomainEvent` |
| 集成事件 | `{Aggregate}{Action}IntegrationEvent` | `OrderCreatedIntegrationEvent` |
| 过去时态 | 事件是已经发生的事，用过去式 | `Created`, `Paid`, `Cancelled` |

### 15.4 测试事件监听器

```java
@SpringBootTest
class OrderEventTest {

    @Autowired
    private ApplicationEventPublisher publisher;

    @Autowired
    private InventoryService inventoryService;

    @Test
    void shouldDeductInventoryWhenOrderCreated() {
        // 发布事件
        publisher.publishEvent(new OrderCreatedEvent(1L, 100L, new BigDecimal("99.99")));

        // 验证效果
        verify(inventoryService).deduct(1L);
    }
}
```

---

## 十六、架构决策指南

```java
需要解耦？
├─ 同进程内 → Spring 本地事件
│   ├─ 需要事务边界控制 → @TransactionalEventListener
│   ├─ 需要异步 → @Async
│   └─ 需要链式处理 → 事件链（控制在 1-2 跳）
├─ 需要跨服务可靠投递 → MQ
│   ├─ 需要事务原子性 → Outbox 模式
│   ├─ 需要严格顺序 → Kafka 分区有序 + 幂等
│   └─ 需要延迟/死信 → RabbitMQ / RocketMQ
└─ 复杂编排 → Saga / 状态机 / 工作流引擎
    ├─ 需要补偿 → Choreography Saga
    └─ 需要集中控制 → Orchestration Saga
```

### 用 Spring 本地事件
- 单体项目
- 同服务模块解耦
- 后置动作不要求跨进程可靠投递
- 想快速引入事件抽象

### 用 Spring 事件 + Outbox + MQ
- 已经开始服务化
- 需要事务提交后的可靠通知
- 需要重试、死信、补偿
- 需要跨团队消费同类业务事件

### 直接用 MQ
- 系统本身就是分布式协作
- 事件吞吐量很高
- 需要重放、回溯、流处理
- 消费者数量多、职责边界清晰

---

## 十七、常见反模式清单

以下做法在真实项目里非常常见，也最容易埋雷：

| # | 反模式 | 正确做法 |
|---|--------|----------|
| 1 | 用 `@EventListener` 处理所有事务后逻辑，却没意识到它仍在事务内 | 明确使用 `@TransactionalEventListener(AFTER_COMMIT)` |
| 2 | 在监听器里直接发 HTTP、发短信、调第三方接口 | 使用 `@Async` + 独立线程池 |
| 3 | 没有独立事件线程池，直接复用公共异步线程池 | 按业务域隔离线程池 |
| 4 | 没有幂等控制，消费者重复扣库存、重复发券 | 消费记录表唯一约束 + 幂等键 |
| 5 | 直接把 JPA Entity 当事件体 | 独立建模事件对象 |
| 6 | 用大量注解条件和优先级替代明确的业务编排 | 复杂逻辑用服务编排，事件只做桥接 |
| 7 | 指望 Spring 本地事件承担分布式消息总线职责 | 明确边界：本地事件 ≠ 消息队列 |
| 8 | 没有事件指标、没有告警、没有补偿机制 | 接入 Micrometer + 定时补偿 |
| 9 | 异步方法不处理异常，异常静默丢失 | 配置 `AsyncUncaughtExceptionHandler` |
| 10 | 事件递归发布导致事件风暴 | 只做单向流转，复杂编排用 Saga |

> 如果你的系统里出现**三项以上**，说明已经不是"优化一下"能解决的问题，而是需要做一次事件架构治理。

---

## 十八、总结

### 一句话记住

> 在生产环境里，事件机制的核心不是"能不能发"，而是"什么时候发、失败怎么办、能不能恢复、是否可观测"。

### 能力边界矩阵

| 技术 | 解决的问题 | 不解决的 |
|------|-----------|----------|
| `@EventListener` | 进程内解耦 | 分布式可靠消息 |
| `@TransactionalEventListener` | 事务时机控制 | 消息持久化 |
| `@Async` | 主线程不阻塞 | 容量无限 |
| `Outbox` | 事务与事件原子发布 | 消费者幂等 |
| `Kafka/RocketMQ` | 跨服务传播 | 业务一致性万能药 |

### 推荐演进路线

```
第一步：进程内解耦
   把订单、支付等核心服务中的"后置动作"抽成事件
   明确区分主链路和外围逻辑

第二步：补齐事务边界
   所有通知、日志、积分等副作用改成 AFTER_COMMIT
   所有慢逻辑异步化

第三步：补齐生产能力
   独立线程池 + 异常处理 + Micrometer 指标 + TraceId 透传

第四步：演进到可靠集成事件
   引入 Outbox + 接入 Kafka/RocketMQ
   消费端做幂等、重试、死信
```

这条路径的优势：
- 对现有代码侵入小
- 迭代成本低
- 每一步都能独立交付价值
- 不会一上来就把系统复杂度拉满

---

*整理于 2026-05-28，综合自微信公众号文章、Medium、Dev.to、Baeldung 及 Spring Framework 源码分析。*
