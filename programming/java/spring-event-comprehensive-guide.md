---
title: "Spring Event 深度指南：从入门到生产实战"
date: 2026-05-13
category: "programming/java"
tags:
  - spring
  - spring-event
  - event-driven
  - @EventListener
  - @TransactionalEventListener
  - async
  - transaction
  - best-practices
  - production
source:
  - title: "Spring Event 别瞎用！被它坑的绩效都没了！"
    url: "https://mp.weixin.qq.com/s/U2ykL0k1mXopnvDlA325cw"
    author: "芋道源码"
  - title: "Mastering Event-Driven Architecture with Spring"
    url: "https://medium.com/@AlexanderObregon/mastering-event-driven-architecture-with-spring-events-listeners-and-application-context-658ebe184e89"
    author: "Alexander Obregon"
  - title: "Understanding the Mechanics of Spring Boot's Event System"
    url: "https://medium.com/@AlexanderObregon/understanding-the-mechanics-of-spring-boots-event-system-4295597bcca5"
    author: "Alexander Obregon"
  - title: "Spring Events & Transactions: The Hidden Traps"
    url: "https://medium.com/javarevisited/spring-events-part-2-the-transaction-traps-most-developers-never-notice-23b9077d079e"
  - title: "Understanding TransactionEventListener in Spring Boot"
    url: "https://dev.to/haraf/understanding-transactioneventlistener-in-spring-boot-use-cases-real-time-examples-and-4aof"
    author: "Araf"
desc: "Spring Event 从基础原理到生产踩坑的全方位指南。涵盖事件驱动架构基础、@EventListener/@TransactionalEventListener 注解、异步事件、事务绑定事件、生产环境常见陷阱（优雅关闭、事件丢失、可靠性保证）、以及与 MQ 的选型对比。融合国内一线生产经验与国际最佳实践。"
---

# Spring Event 深度指南：从入门到生产实战

## 目录

1.  [事件驱动架构与 Spring Event 概述](#1-事件驱动架构与-spring-event-概述)
2.  [Spring Event 核心 API](#2-spring-event-核心-api)
3.  [注解驱动的事件处理](#3-注解驱动的事件处理)
4.  [异步事件处理](#4-异步事件处理)
5.  [事务绑定事件（@TransactionalEventListener）](#5-事务绑定事件transactionaleventlistener)
6.  [Spring 内置生命周期事件](#6-spring-内置生命周期事件)
7.  [生产踩坑实录（核心）](#7-生产踩坑实录核心)
    - [7.1 优雅关闭：使用 Spring Event 的前置条件](#71-优雅关闭使用-spring-event-的前置条件)
    - [7.2 启动阶段事件丢失](#72-启动阶段事件丢失)
    - [7.3 强一致性场景不适合订阅发布模式](#73-强一致性场景不适合订阅发布模式)
    - [7.4 最终一致性场景的正确使用](#74-最终一致性场景的正确使用)
8.  [可靠性保证与重试策略](#8-可靠性保证与重试策略)
9.  [幂等性：重试的基石](#9-幂等性重试的基石)
10. [Spring Event vs 消息队列（MQ）](#10-spring-event-vs-消息队列mq)
11. [综合最佳实践与建议](#11-综合最佳实践与建议)
12. [参考资源](#12-参考资源)

---

## 1. 事件驱动架构与 Spring Event 概述

### 1.1 什么是事件驱动架构

事件驱动架构（EDA）是一种通过事件在组件之间进行异步通信的架构模式。其核心思想是"发布"和"订阅"的解耦：

- **发布者**触发事件，但不需要知道谁会处理它
- **订阅者**监听事件，但不需要知道谁触发了它

这种模式带来了更好的**可扩展性**、**可维护性**和**灵活性**。

### 1.2 Spring Event 是什么

Spring Framework 提供了**内置的事件驱动机制**——Spring Event，它基于 JDK 的观察者模式，在 `ApplicationContext` 之上构建了一套完整的发布-订阅基础设施。

**核心特性：**

- **应用内通信**：适用于同一个 JVM 进程内的组件间解耦
- **类型匹配分发**：根据事件类型自动路由到对应的监听器
- **同步/异步双模**：默认同步，可配置异步执行
- **事务感知**：通过 `@TransactionalEventListener` 与事务生命周期绑定
- **轻量无依赖**：零外部依赖，Spring Framework 自带

### 1.3 适用场景

| 场景 | 适合 Spring Event | 说明 |
|------|------------------|------|
| 应用内模块解耦 | ✅ | 同一进程内的服务间事件通知 |
| 最终一致性业务 | ✅ | 如提单成功后通知释放资源 |
| 强一致性业务 | ❌ | 如库存扣减与订单提必须完全一致 |
| 跨应用通信 | ❌ | 应使用 MQ 或 RPC |
| 高吞吐量场景 | ⚠️ | 需谨慎，注意同步阻塞风险 |

---

## 2. Spring Event 核心 API

Spring Event 体系由三个核心角色组成，理解它们之间的关系是掌握 Spring Event 的基础。

### 2.1 ApplicationEvent —— 事件本体

`ApplicationEvent` 是所有事件类的基类，继承自 `java.util.EventObject`。

```java
// 自定义事件——方式一：继承 ApplicationEvent
public class OrderCreatedEvent extends ApplicationEvent {
    private final String orderId;
    private final String customerEmail;

    public OrderCreatedEvent(Object source, String orderId, String customerEmail) {
        super(source);
        this.orderId = orderId;
        this.customerEmail = customerEmail;
    }

    public String getOrderId() { return orderId; }
    public String getCustomerEmail() { return customerEmail; }
}
```

**Spring 4.2+ 简化：** 可以不必继承 `ApplicationEvent`，直接使用 POJO 作为事件，Spring 会自动包装为 `PayloadApplicationEvent`。

```java
// 方式二：POJO 事件（推荐，更轻量）
public record OrderCreatedEvent(String orderId, String customerEmail) {}
```

### 2.2 ApplicationEventPublisher —— 事件发布者

`ApplicationEventPublisher` 是发布事件的核心接口，Spring 会自动注入到任何受管理的 Bean 中。

```java
@Service
public class OrderService {
    private final ApplicationEventPublisher eventPublisher;

    // 构造器注入
    public OrderService(ApplicationEventPublisher eventPublisher) {
        this.eventPublisher = eventPublisher;
    }

    public void createOrder(String orderId, String email) {
        // 业务逻辑：保存订单到数据库
        orderRepository.save(new Order(orderId, email));

        // 发布事件
        eventPublisher.publishEvent(new OrderCreatedEvent(this, orderId, email));
        // publishEvent 也接受 POJO：
        // eventPublisher.publishEvent(new OrderCreatedEvent(orderId, email));
    }
}
```

**关键点：**
- `publishEvent()` 默认是**同步阻塞**的——发布者会等待所有监听器执行完毕后才返回
- 事件在发布线程中同步广播，所有监听器按注册顺序执行
- 可以通过 `@Async` 改为异步执行

### 2.3 ApplicationListener —— 事件监听器（接口方式）

传统方式需要实现 `ApplicationListener` 接口：

```java
@Component
public class OrderEventListener implements ApplicationListener<OrderCreatedEvent> {
    @Override
    public void onApplicationEvent(OrderCreatedEvent event) {
        System.out.println("Processing order: " + event.getOrderId());
        // 业务逻辑：发送通知邮件、更新缓存等
    }
}
```

### 2.4 ApplicationEventMulticaster —— 事件分发器

`ApplicationEventMulticaster` 是 Spring 内部的**事件分发引擎**，它负责：

1. **注册监听器**：在应用启动时，Spring 扫描所有 `ApplicationListener` 实现和 `@EventListener` 注解方法，注册到 multicaster
2. **事件路由**：当 `publishEvent()` 被调用时，multicaster 根据事件类型匹配对应的监听器
3. **调用监听器**：默认使用同步方式逐个调用，可通过配置启用异步

```
publishEvent(event)
       │
       ▼
ApplicationEventMulticaster
       │
       ├──→ Listener 1 (OrderEventListener)  ← 匹配 OrderCreatedEvent
       ├──→ Listener 2 (EmailNotification)   ← 匹配 OrderCreatedEvent
       └──→ Listener 3 (InventoryListener)    ← 不匹配，跳过
```

---

## 3. 注解驱动的事件处理

### 3.1 @EventListener —— 注解方式（推荐）

Spring 4.2 引入的 `@EventListener` 注解，让事件处理更加简洁：

```java
@Component
public class OrderEventHandlers {

    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        // 处理订单创建事件
        emailService.sendConfirmation(event.getOrderId(), event.getCustomerEmail());
    }
}
```

**优势：** 无需实现接口，方法可自定义名称，一个类可包含多个监听方法。

### 3.2 条件过滤

`@EventListener` 支持 SpEL 条件表达式，只在满足条件时才执行：

```java
@Component
public class CriticalEventLogger {

    @EventListener(condition = "#event.orderId().startsWith('VIP')")
    public void handleVipOrder(OrderCreatedEvent event) {
        // 只处理 VIP 客户的订单
        vipService.priorityProcess(event.getOrderId());
    }
}
```

### 3.3 多事件监听

同一个方法可以监听多种事件类型：

```java
@Component
public class OrderLifecycleHandler {

    @EventListener({OrderCreatedEvent.class, OrderShippedEvent.class, OrderDeliveredEvent.class})
    public void onOrderStatusChange(Object event) {
        if (event instanceof OrderCreatedEvent e) {
            log.info("Order created: {}", e.getOrderId());
        } else if (event instanceof OrderShippedEvent e) {
            log.info("Order shipped: {}", e.getOrderId());
        }
    }
}
```

### 3.4 事件监听器执行顺序

使用 `@Order` 注解控制多个监听器的执行顺序：

```java
@Component
public class OrderEventHandlers {

    @EventListener
    @Order(1)
    public void updateInventory(OrderCreatedEvent event) {
        // 最先执行：更新库存
    }

    @EventListener
    @Order(2)
    public void sendNotification(OrderCreatedEvent event) {
        // 其次执行：发送通知
    }

    @EventListener
    @Order(3)
    public void auditLog(OrderCreatedEvent event) {
        // 最后执行：审计日志
    }
}
```

---

## 4. 异步事件处理

### 4.1 为什么需要异步

默认情况下，Spring Event 是**同步**的——发布者等待所有监听器执行完毕后才会返回。这对以下场景可能成为问题：

- 监听器执行耗时的 IO 操作（发送邮件、调用外部 API）
- 监听器无需等待返回结果
- 事件处理不应阻塞主业务流程

### 4.2 使用 @Async 实现异步

**第一步：启用异步支持**

```java
@Configuration
@EnableAsync
public class AsyncConfig {
}
```

**第二步：在监听器上添加 @Async**

```java
@Component
public class AsyncEventHandler {

    @Async
    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        // 此方法在独立线程中执行，不会阻塞发布者
        emailService.sendConfirmation(event.getOrderId(), event.getCustomerEmail());
    }
}
```

### 4.3 自定义线程池配置

生产环境中，**务必配置专用的线程池**，避免使用 Spring 默认的 `SimpleAsyncTaskExecutor`（它为每个任务创建新线程）。

```java
@Configuration
@EnableAsync
public class EventAsyncConfig {

    @Bean(name = "eventTaskExecutor")
    public Executor eventTaskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(2);       // 核心线程数
        executor.setMaxPoolSize(5);        // 最大线程数
        executor.setQueueCapacity(500);    // 任务队列容量
        executor.setThreadNamePrefix("Event-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();
        return executor;
    }
}
```

**配置说明：**
- **CorePoolSize (2)**：始终保持 2 个线程存活
- **MaxPoolSize (5)**：任务高峰期最多可扩展到 5 个线程
- **QueueCapacity (500)**：超过核心线程的任务先进入队列，队列满后才创建新线程
- **CallerRunsPolicy**：拒绝策略——由发布者线程执行，防止任务丢失

然后在 `@Async` 中指定使用的线程池：

```java
@Component
public class AsyncEventHandler {

    @Async("eventTaskExecutor")
    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        // 使用自定义的 eventTaskExecutor 线程池
    }
}
```

### 4.4 异步事件的注意事项

| 问题 | 说明 | 解决方案 |
|------|------|---------|
| 事务边界 | 异步监听器在独立线程中运行，不再在发布者的事务内 | 使用 `@TransactionalEventListener` 配合 `@Async` |
| 异常传播 | 异步监听器的异常不会传播到发布者 | 监听器内部必须 try-catch 处理所有异常 |
| 上下文传播 | 子线程无法访问父线程的请求上下文 | 手动传递 RequestContextHolder 等 |
| 事件丢失 | 异步监听器失败后不会被重试（默认） | 实现重试机制（见第 8 节） |

---

## 5. 事务绑定事件（@TransactionalEventListener）

### 5.1 核心问题：事件何时触发？

先看一个常见场景：

```java
@Service
public class OrderService {

    @Transactional
    public void createOrder(String orderId) {
        // 1. 保存订单
        orderRepository.save(new Order(orderId));

        // 2. 发布事件
        publisher.publishEvent(new OrderCreatedEvent(orderId));
    }
}
```

**问题：** `@EventListener` 监听器会在 `publishEvent` 调用时**立即执行**，而此时事务还未提交！

后果示例：
- 监听器发送邮件，邮件中附带了订单号——用户收到邮件点击链接查询，但订单**还未提交到数据库**，查不到！
- 监听器更新缓存——但数据库回滚了，缓存却已经被更新，造成数据不一致！

### 5.2 @TransactionalEventListener 登场

`@TransactionalEventListener` 将事件监听器绑定到事务的**生命周期阶段**：

```java
@Component
public class TransactionAwareHandler {

    @TransactionalEventListener
    public void handleAfterCommit(OrderCreatedEvent event) {
        // 默认 AFTER_COMMIT：事务成功提交后才执行
        emailService.sendConfirmation(event.getOrderId());
        cacheService.refreshOrderCache(event.getOrderId());
    }
}
```

### 5.3 事务阶段详解

`phase` 参数控制监听器在事务的哪个阶段触发：

```java
@Component
public class TransactionPhaseHandler {

    // BEFORE_COMMIT：事务提交前执行（仍在事务内）
    @TransactionalEventListener(phase = TransactionPhase.BEFORE_COMMIT)
    public void beforeCommit(OrderCreatedEvent event) {
        // 仍在事务中，任何异常都会触发事务回滚
        // 适合在提交前做最后的校验或准备
    }

    // AFTER_COMMIT（默认）：事务成功提交后执行
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void afterCommit(OrderCreatedEvent event) {
        // 事务已成功提交
        // 适合发送通知、更新缓存、发布 MQ 消息
    }

    // AFTER_ROLLBACK：事务回滚后执行
    @TransactionalEventListener(phase = TransactionPhase.AFTER_ROLLBACK)
    public void afterRollback(OrderCreatedEvent event) {
        // 事务被回滚
        log.warn("Transaction rolled back for order: {}", event.getOrderId());
        auditService.logFailedOrder(event);
    }

    // AFTER_COMPLETION：事务完成时（无论提交还是回滚）
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMPLETION)
    public void afterCompletion(OrderCreatedEvent event) {
        // 事务结束（提交或回滚）
        // 适合做清理操作
    }
}
```

### 5.4 实际应用场景

**场景 1：提交成功后发送确认邮件**

```java
@Component
public class EmailNotificationListener {

    @TransactionalEventListener  // 默认 AFTER_COMMIT
    public void sendOrderConfirmation(OrderCreatedEvent event) {
        // 订单已成功提交到数据库，可以安全发送邮件
        emailService.sendConfirmation(event.getOrderId(), event.getCustomerEmail());
    }
}
```

**场景 2：提交后更新缓存**

```java
@Component
public class CacheUpdateListener {

    @TransactionalEventListener
    public void refreshProductCache(ProductUpdatedEvent event) {
        // 确保数据已持久化，再更新缓存
        cacheManager.evict("products", event.getProductId());
    }
}
```

**场景 3：回滚时执行补偿操作**

```java
@Component
public class RollbackListener {

    @TransactionalEventListener(phase = TransactionPhase.AFTER_ROLLBACK)
    public void handleRollback(OrderCreatedEvent event) {
        // 记录失败的订单，准备后续补偿
        auditService.logFailedOrder(event);
        // 注意：此时系统处于异常状态，避免在此继续修改数据库
    }
}
```

**场景 4：代码模板（完整链条）**

```java
@Service
public class OrderService {

    private final OrderRepository orderRepository;
    private final ApplicationEventPublisher publisher;

    public OrderService(OrderRepository orderRepository,
                        ApplicationEventPublisher publisher) {
        this.orderRepository = orderRepository;
        this.publisher = publisher;
    }

    @Transactional
    public void createOrder(String orderId, String email) {
        // 1. 业务逻辑：保存订单（事务内）
        orderRepository.save(new Order(orderId, email));

        // 2. 发布事件
        publisher.publishEvent(new OrderCreatedEvent(orderId, email));

        // 3. 方法返回后，Spring 提交事务
        // 4. 事务提交后，@TransactionalEventListener 才会被触发
    }
}

// 监听器：事务提交后才执行
@Component
public class PostCommitHandler {

    @TransactionalEventListener
    @Async("eventTaskExecutor")
    public void handleAfterCommit(OrderCreatedEvent event) {
        // 事务已提交 + 异步执行，不会阻塞主流程
        emailService.sendConfirmation(event.orderId(), event.customerEmail());
        cacheService.refreshCache(event.orderId());
    }
}
```

### 5.5 局限与陷阱

| 陷阱 | 说明 | 建议 |
|------|------|------|
| **必须运行在事务内** | 如果在非 `@Transactional` 方法中发布事件，`@TransactionalEventListener` 不会触发 | 确保发布者方法有 `@Transactional` |
| **嵌套事务行为不确定** | 嵌套事务（REQUIRES_NEW）下，监听器行为可能不符合预期 | 避免在嵌套事务中使用 |
| **BEFORE_COMMIT 仍在事务中** | 监听器抛异常会触发回滚 | 确认逻辑确实需要在该阶段执行 |
| **AFTER_ROLLBACK 处于错误状态** | 系统状态异常，不应在此阶段修改数据 | 只做日志记录或消息投递 |
| **测试复杂** | 需要模拟事务提交和回滚行为 | 使用 `@Transactional` 测试配合 `@Commit` |

---

## 6. Spring 内置生命周期事件

Spring 本身会发布一系列生命周期事件，监听这些事件可以在应用的特定阶段执行自定义逻辑。

```java
@Component
public class ApplicationLifecycleListener {

    // 应用启动完成
    @EventListener
    public void onApplicationReady(ApplicationReadyEvent event) {
        // 所有 Bean 初始化完成，HTTP 端口已打开
        // 适合做启动后的初始化工作：预热缓存、开启定时任务
        log.info("Application is ready. Starting data warmup...");
        cacheService.warmup();
    }

    // 上下文刷新完成
    @EventListener
    public void onContextRefreshed(ContextRefreshedEvent event) {
        // ApplicationContext 已刷新
        // 适合在此开启 RPC/MQ 入口流量
    }

    // 上下文关闭
    @EventListener
    public void onContextClosed(ContextClosedEvent event) {
        // 应用开始关闭
        log.info("Application shutting down...");
    }
}
```

**实用建议：** 利用 `ContextRefreshedEvent` 控制入口流量的开启时机——等 Spring 完全启动后再开启 MQ 和 RPC 流量（详见第 7.2 节）。

---

## 7. 生产踩坑实录（核心）

> 以下内容基于**一线生产环境真实踩坑**的宝贵经验。很多开发者只学了 Spring Event 的 API 用法就上线了，结果在线上环境栽了大跟头。

### 7.1 优雅关闭：使用 Spring Event 的前置条件

**🔴 核心规则：使用 Spring Event 前，必须确保服务实现了优雅关闭！**

#### 问题现象

线上系统出现异常日志：

```
Do not request a bean from a BeanFactory in a destroy method implementation
```

调用堆栈指向 `ApplicationContext` 关闭期间的事件发布。日志发生在**服务关闭阶段**。

#### 根本原因

Spring 广播事件时，会在 `ApplicationContext` 中查找所有监听器——这需要 `getBean()`。但 Spring 有个严格的限制：

> **ApplicationContext 关闭期间，不得调用 getBean()，否则会报错。**

当服务在高并发下关闭时：

```
服务开始关闭 ──→ ApplicationContext 开始关闭
       │
       ├──→ 仍有少量 HTTP/RPC/MQ 请求正在处理
       ├──→ 这些请求中发布了 Spring Event
       ├──→ Spring 尝试 getBean 查找监听器 → ❌ 失败！
       └──→ 异常日志：找不到 Bean
```

#### 解决方案

**必须实现优雅关闭（Graceful Shutdown）流程：**

```
1. 先切断入口流量（HTTP、MQ、RPC）
       │
2. 等待已在处理中的请求完成（draining）
       │
3. 最后关闭 Spring ApplicationContext
```

**Spring Boot 2.3+ 优雅关闭配置：**

```yaml
# application.yml
server:
  shutdown: graceful

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```

对于 **Kubernetes** 环境，还需要配合 Pod 生命周期：

```yaml
apiVersion: v1
kind: Pod
spec:
  terminationGracePeriodSeconds: 60
  lifecycle:
    preStop:
      exec:
        command:
          - /bin/sh
          - -c
          - "sleep 5 && curl -X POST http://localhost:8080/actuator/shutdown"
```

> **教训：** 这是线上故障反复验证的知识点。日订单几百万的系统，即便低峰期单机并发度也较高，服务关闭期间仍有流量进来。如果使用 Spring Event，一定会出现此异常，导致处理失败！

### 7.2 启动阶段事件丢失

**🔴 核心规则：服务启动阶段，Spring Event 事件可能静默丢失！**

#### 问题现象

某公司线上系统遇到：Kafka Consumer 已经在消费消息，但 Spring Event 监听器还没注册完成，导致部分消息处理丢失——**没有任何异常日志，就是丢了**。

#### 根本原因

```
服务启动时间线：

Kafka Consumer 开始消费 ────────→ 消息处理中 → publishEvent(event)
                                          │
                                          ├──→ EventListener 还未注册到 Spring!
                                          └──→ 事件静默丢失（不报错！）
               ↑                 ↑
               EventListener 注册完成的时间点
```

核心问题：Kafka Consumer 在 `@KafkaListener` 解析阶段就开始消费，但 `EventListener` 注册进 Spring 的时间点**滞后于** Consumer 开始消费的时间点。

#### 解决方案

**在 `ContextRefreshedEvent` 事件中开启入口流量：**

```java
@Component
public class TrafficController {

    private final KafkaConsumerService kafkaConsumerService;
    private final RpcServer rpcServer;

    public TrafficController(KafkaConsumerService kafkaConsumerService,
                             RpcServer rpcServer) {
        this.kafkaConsumerService = kafkaConsumerService;
        this.rpcServer = rpcServer;
    }

    @EventListener(ContextRefreshedEvent.class)
    public void onApplicationReady() {
        // Spring 已完全启动 → 开启入口流量
        kafkaConsumerService.startConsuming();
        rpcServer.start();
        log.info("All listeners registered. Traffic flow started.");
    }
}
```

**启示：** Spring Boot 默认会在 Spring 完全启动后才开启 HTTP 流量，这是同样道理。RPC 和 MQ 也应该如此处理。

### 7.3 强一致性场景不适合订阅发布模式

**🔴 核心规则：强一致性业务绝对不能用 Spring Event！**

#### 反例：提单场景

假设提单流程如下：

```
1. 发布提单前置事件 ──→ 扣减库存 ──→ 锁定优惠券 ──→ 锁定库存
                                  │
2. 提单成功 ──→ 提交订单
```

如果库存扣减成功，但锁定优惠券失败：

- ❌ 事件发布者**无法感知**哪个订阅者失败
- ❌ 无法准确触发回滚流程
- ❌ 已扣减的库存无法复原
- ❌ 数据不一致！

**为什么会这样？** `publishEvent()` 同步执行时，如果有监听器抛异常，发布者确实能捕获到异常。但问题在于：

1. 多个监听器可能按顺序执行，前面的已经改写了数据库
2. 事务边界不清晰（跨多个资源/服务）
3. 缺少全局的"两阶段提交"能力

#### Spring Event 不适合的强一致性场景

| 业务场景 | 为什么不适合 |
|---------|-------------|
| 订单提交流程 | 库存、优惠券、账户余额需原子性操作 |
| 转账交易 | 扣减和增加必须同时成功 |
| 资源分配 | 多个资源的分配不能部分成功 |

### 7.4 最终一致性场景的正确使用

**🔴 核心规则：最终一致性场景 = Spring Event 的 sweet spot！**

#### 正例：提单成功后的收尾工作

```
提单成功 ──→ 发布 OrderCreatedEvent
                  │
                  ├──→ 发送 MQ 消息（通知下游服务）
                  ├──→ 释放分布式锁
                  ├──→ 清理本地缓存
                  └──→ 发送确认通知
```

**为什么这样是安全的？**

- 提单已经成功，主业务已完成
- 后续操作失败不应回滚整个提单——只需重试
- 每个操作都是"可重试 + 幂等"的

#### 实战案例：订单消息处理

某电商公司处理履约完成的业务流程：

```java
// 履约完成后发布事件
@Service
public class FulfillmentService {

    @Transactional
    public void completeFulfillment(String orderId, BigDecimal amount) {
        // 1. 更新订单状态为"履约完成"
        orderRepository.updateStatus(orderId, "FULFILLED");

        // 2. 发布履约完成事件
        publisher.publishEvent(new FulfillmentCompletedEvent(orderId, amount));
    }
}

// 多个监听器分别处理不同的业务逻辑
@Component
public class FulfillmentEventHandlers {

    // 通知结算系统
    @TransactionalEventListener
    public void notifySettlement(FulfillmentCompletedEvent event) {
        settlementService.notify(event.getOrderId(), event.getAmount());
        // 通知结算失败可重试，无需回滚履约过程
    }

    // 更新订单统计
    @TransactionalEventListener
    public void updateOrderStats(FulfillmentCompletedEvent event) {
        statsService.incrementCompletedOrders();
    }

    // 释放预占资源
    @TransactionalEventListener
    public void releaseReservedResources(FulfillmentCompletedEvent event) {
        resourceService.releaseReservation(event.getOrderId());
    }
}
```

**关键判断标准：** 在提单成功事件的订阅者中，只有一种执行结果——成功。即使出现失败，也应该**重试直至成功**。

---

## 8. 可靠性保证与重试策略

使用 Spring Event 时，默认的 `publishEvent()` 是同步且**没有重试机制**的——监听器抛异常则事件处理失败。生产环境中，必须有可靠性保证！

### 8.1 方案一：@Retryable 注解

Spring Retry 提供了声明式的重试支持：

**第一步：引入依赖**

```xml
<dependency>
    <groupId>org.springframework.retry</groupId>
    <artifactId>spring-retry</artifactId>
</dependency>
```

**第二步：启用重试**

```java
@Configuration
@EnableRetry
public class RetryConfig {
}
```

**第三步：在监听器上使用 @Retryable**

```java
@Component
public class RetryableEventHandler {

    @Async("eventTaskExecutor")
    @TransactionalEventListener
    @Retryable(
        value = {Exception.class},
        maxAttempts = 3,
        backoff = @Backoff(delay = 1000, multiplier = 2)
    )
    public void handleWithRetry(OrderCreatedEvent event) {
        // 失败时会自动重试，最多 3 次
        // 重试间隔：1s → 2s → 4s（指数退避）
        notificationService.sendNotification(event.getOrderId());
    }

    // 所有重试都失败后的兜底
    @Recover
    public void recover(Exception e, OrderCreatedEvent event) {
        log.error("All retries failed for order: {}", event.getOrderId(), e);
        // 发送到死信队列或告警平台
        deadLetterService.send(event, e);
    }
}
```

### 8.2 方案二：Kafka 消费组重试

如果在 Kafka Consumer 中使用 Spring Event，处理重试非常直接：

```java
@Component
public class KafkaOrderConsumer {

    @KafkaListener(topics = "order-events")
    public void onMessage(ConsumerRecord<String, String> record) {
        try {
            // 解析消息
            OrderMessage message = objectMapper.readValue(record.value(), OrderMessage.class);

            // 发布 Spring Event
            publisher.publishEvent(new KafkaOrderEvent(message));

        } catch (Exception e) {
            log.error("Failed to process message, will retry via Kafka", e);
            // 返回消费失败 → Kafka 自动重试
            throw new KafkaException("Processing failed", e);
        }
    }
}

@Component
public class KafkaEventHandler {

    @EventListener
    public void handleOrderEvent(KafkaOrderEvent event) {
        // 业务处理
        orderService.process(event.getMessage());
    }
}
```

### 8.3 方案三：故障管理平台（企业级）

对于**超过最大重试次数**仍然失败的事件，需要上报到故障管理平台：

```
监听器重试失败（超过最大次数）
       │
       ▼
上报到故障 MQ
       │
       ▼
故障管理平台消费 MQ，收集并落库
       │
       ▼
研发收到故障通知，开始排查
       │
       ▼
修复问题后，在管理后台点击"重试"
       │
       ▼
后台通过 RPC SPI 调用业务系统重试故障
       │
       ▼
返回成功/失败结果
```

**关键设计点：**

- **故障持久化：** 故障信息存入数据库，不会丢失
- **人工介入：** 研发排查原因，修复后触发重试
- **可观测性：** 所有故障有列表、有详情、有追踪
- **重试隔离：** 重试通过 RPC SPI 独立调用，不影响正常业务

---

## 9. 幂等性：重试的基石

**这是重试策略的前提——没有幂等，就不要做重试！**

### 9.1 为什么幂等如此重要

Spring 不知道哪些订阅者成功、哪些失败。当重试发生时，**所有订阅者都会被重新执行**：

```
第一次执行：
OrderCreatedEvent ──→ Listener A (成功) ──→ 新增积分 100
                 └──→ Listener B (失败) ──→ 发送邮件失败

重试：
OrderCreatedEvent ──→ Listener A (再次执行) ──→ 又新增 100 积分！  ❌ 重复！
                 └──→ Listener B (再次执行) ──→ 发送邮件成功
```

### 9.2 幂等实现方案

**方案一：业务键去重**

```java
@Component
public class IdempotentEventHandler {

    private final IdempotentService idempotentService;

    @TransactionalEventListener
    public void handleOrderEvent(OrderCreatedEvent event) {
        // 通过业务键检查是否已处理
        if (idempotentService.isProcessed("order", event.getOrderId())) {
            log.info("Event already processed, skipping: {}", event.getOrderId());
            return;
        }

        // 执行业务逻辑
        pointsService.addPoints(event.getOrderId(), 100);

        // 标记已处理
        idempotentService.markProcessed("order", event.getOrderId());
    }
}
```

**方案二：数据库唯一约束**

```java
@Entity
@Table(uniqueConstraints = @UniqueConstraint(columnNames = "eventId"))
public class ProcessedEvent {
    @Id private Long id;
    private String eventId;  // 唯一键
    private String status;
}
```

**方案三：幂等键 + INSERT ... ON CONFLICT**

```java
@Repository
public interface ProcessedEventRepository extends JpaRepository<ProcessedEvent, String> {
    // INSERT INTO processed_event (event_key, status) VALUES (?, 'PROCESSED')
    // ON CONFLICT (event_key) DO NOTHING
    @Modifying
    @Query(value = "INSERT INTO processed_event (event_key, status) " +
                   "VALUES (:eventKey, 'PROCESSED') " +
                   "ON CONFLICT (event_key) DO NOTHING", nativeQuery = true)
    int tryInsert(@Param("eventKey") String eventKey);
}

// 返回值 = 1 表示首次处理，= 0 表示已处理过
```

**方案四：自然幂等（update 操作）**

对于 `update` 类的操作（如"将订单状态改为已通知"），SQL 本身是幂等的——第二次 UPDATE 不会产生副作用。

---

## 10. Spring Event vs 消息队列（MQ）

### 10.1 对比总览

| 维度 | Spring Event | MQ（Kafka/RocketMQ） |
|------|-------------|---------------------|
| **作用范围** | 应用内（同一 JVM） | 跨应用、跨服务 |
| **复杂度** | 低，零外部依赖 | 高，需要搭建和维护中间件 |
| **通信模式** | 同步（默认）/异步 | 完全异步 |
| **持久化** | 无（进程重启丢失） | 内置磁盘持久化 |
| **可靠性** | 需自行实现重试 | 自带 ACK + 重试机制 |
| **顺序保证** | 线程内有序 | 分区内有序 |
| **吞吐量** | 受限于 JVM 线程 | 高吞吐、高堆积能力 |
| **事务集成** | 原生支持（@TransactionalEventListener） | 需分布式事务 |
| **适用场景** | 应用内模块解耦 | 服务间解耦、削峰填谷 |

### 10.2 选型决策树

```
需要通知其他微服务吗？
├── 是 → 使用 MQ
└── 否 → 需要跨 JVM 通信吗？
         ├── 是 → 使用 MQ
         └── 否 → 需要持久化确保事件不丢失吗？
                  ├── 是 → 使用 MQ
                  └── 否 → 使用 Spring Event ✅
```

### 10.3 典型组合：Spring Event + MQ

实践中，二者经常**配合使用**：

```text
【应用内解耦】                【服务间解耦】
┌──────────────┐            ┌──────────────┐
│ Controller    │            │ Service A    │
│    ↓          │            │    ↓          │
│ Spring Event │◄───应用内───│ Spring Event │
│ (监听器)     │            │ (MQ 发送器)  │
└──────┬───────┘            └──────┬───────┘
       │                            │
       │ 应用内事件                  │ MQ 消息
       ▼                            ▼
┌──────────────┐            ┌──────────────┐
│ Service B    │            │ Service C    │
│ 同步处理      │            │ 异步消费     │
└──────────────┘            └──────────────┘
```

**示例：** 订单完成时，先用 `@TransactionalEventListener` 做应用内的收尾工作（释放锁、清理缓存等），同时通过 MQ 通知下游服务：

```java
@Component
public class OrderCompletedHandler {

    @TransactionalEventListener
    public void onOrderCompleted(OrderCompletedEvent event) {
        // 应用内收尾
        lockService.release(event.getOrderId());
        cacheService.cleanup(event.getOrderId());

        // 推送 MQ 通知下游服务
        mqProducer.send("order.completed", event.getOrderId());
    }
}
```

### 10.4 什么时候仍然需要 Spring Event

掘友留言：MQ 比 Spring Event 更强大，为什么还要用 Spring Event？

原因如下：

1. **更轻量：** Spring Event 是框架内建机制，无需引入中间件
2. **同步可控：** 发布者可以等待监听器返回结果（MQ 是完全异步的）
3. **事务集成自然**：`@TransactionalEventListener` 与 Spring 事务无缝集成
4. **适合应用内解耦：** 如果只是同一应用内不同模块之间的通知，用 MQ 是大炮打蚊子

> **一句话总结：MQ 解决的是"应用间"通信，Spring Event 解决的是"应用内"解耦。两者是互补关系，而非替代关系。**

---

## 11. 综合最佳实践与建议

### 11.1 生产检查清单

使用 Spring Event 前，逐条确认以下事项：

- [ ] 是否实现了优雅关闭（Graceful Shutdown）？
- [ ] 入口流量（HTTP/MQ/RPC）是否在 Spring 完全启动后才开启？
- [ ] 业务场景是"最终一致性"还是"强一致性"？
- [ ] 监听器是否有重试机制？
- [ ] 监听器是否做了幂等处理？
- [ ] 异步监听器是否配置了专用线程池？
- [ ] 是否需要 `@TransactionalEventListener` 绑定事务？
- [ ] 是否需要异常监控和告警？

### 11.2 典型配置模板

```yaml
# application.yml
server:
  shutdown: graceful

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
  task:
    execution:
      pool:
        core-size: 4
        max-size: 8
        queue-capacity: 1000
```

```java
@Configuration
@EnableAsync
@EnableRetry
public class EventInfraConfig {

    @Bean("eventExecutor")
    public Executor eventExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(2);
        executor.setMaxPoolSize(4);
        executor.setQueueCapacity(500);
        executor.setThreadNamePrefix("event-");
        executor.setWaitForTasksToCompleteOnShutdown(true);
        executor.setAwaitTerminationSeconds(30);
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();
        return executor;
    }
}
```

### 11.3 事件设计规范

1. **事件命名**：`{实体}{动作}Event`，如 `OrderCreatedEvent`、`PaymentCompletedEvent`
2. **事件内容**：携带足够的信息让监听器独立工作，但不携带敏感数据
3. **事件粒度**：一个事件对应一个业务含义，避免"万能事件"
4. **监听器职责**：一个监听器只做一件事（单一职责）
5. **异步策略**：耗时操作一律异步，同步监听器应快速完成

### 11.4 监控与告警

```java
@Component
@Slf4j
public class MonitoredEventHandler {

    private final MeterRegistry meterRegistry;

    @EventListener
    public void handleOrderEvent(OrderCreatedEvent event) {
        // 记录事件处理耗时
        var timer = meterRegistry.timer("spring.event.processing", "event", "OrderCreatedEvent");

        timer.record(() -> {
            try {
                process(event);
                meterRegistry.counter("spring.event.success", "event", "OrderCreatedEvent").increment();
            } catch (Exception e) {
                meterRegistry.counter("spring.event.failure", "event", "OrderCreatedEvent").increment();
                throw e;
            }
        });
    }

    private void process(OrderCreatedEvent event) {
        // 实际业务处理
    }
}
```

---

## 12. 参考资源

| 资源 | 链接 |
|------|------|
| Spring Framework Event 文档 | https://docs.spring.io/spring-framework/reference/core/beans/context-introduction.html#context-functionality-events |
| Spring Transaction-bound Events | https://docs.spring.io/spring-framework/reference/data-access/transaction/event.html |
| Baeldung Guide to Spring Events | https://www.baeldung.com/spring-events |
| Spring Retry 文档 | https://docs.spring.io/spring-retry/docs/current/reference/ |
| Spring Boot Graceful Shutdown | https://docs.spring.io/spring-boot/docs/current/reference/html/web.html#web.graceful-shutdown |

---

> **生产法则：使用 Spring Event 前，先治理好你的服务关闭流程和流量接入时机。没有优雅关闭和幂等重试，Spring Event 就是一柄会反伤自己的利刃。**
