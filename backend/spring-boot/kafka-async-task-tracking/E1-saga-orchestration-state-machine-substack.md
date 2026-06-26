# Implementing SAGA Orchestration with Spring State Machine + Kafka

> 来源：Substack / CodeExperts
> 原文：[Implementing SAGA Orchestration with Spring Boot State Machine + Kafka](https://codeexperts07.substack.com/p/implementing-saga-orchestration-with)
> 收录维度：**E — 任务编排与状态机**

---

## 概述

将简单 TaskStatus 枚举升级为完整状态机驱动的 Saga 编排模式，使用 Kafka 作为事件总线。

## 1. 从 TaskStatus 到状态机

### 原始设计（引子文章）

```java
public enum TaskStatus {
    PENDING, PROCESSING, COMPLETED, FAILED
}
```

### 升级为状态机

```java
public enum TaskState {
    CREATED,
    VALIDATING,
    VALIDATED,
    EXECUTING,
    TRANSFORMING,
    REPORTING,
    COMPLETED,
    FAILED,
    COMPENSATING,     // 补偿中
    COMPENSATED,      // 已完成补偿
    CANCELLED
}

public enum TaskEvent {
    SUBMIT,
    VALIDATE,
    VALIDATE_FAIL,
    EXECUTE,
    TRANSFORM,
    REPORT,
    COMPLETE,
    FAIL,
    COMPENSATE,
    CANCEL
}
```

## 2. Spring Statemachine 配置

```java
@Configuration
@EnableStateMachineFactory
public class TaskStateMachineConfig
        extends StateMachineConfigurerAdapter<TaskState, TaskEvent> {

    @Override
    public void configure(StateMachineStateConfigurer<TaskState, TaskEvent> states)
            throws Exception {
        states
            .withStates()
                .initial(TaskState.CREATED)
                .state(TaskState.EXECUTING)
                .end(TaskState.COMPLETED)
                .end(TaskState.FAILED)
                .end(TaskState.COMPENSATED)
                .end(TaskState.CANCELLED);
    }

    @Override
    public void configure(StateMachineTransitionConfigurer<TaskState, TaskEvent> transitions)
            throws Exception {
        transitions
            .withExternal()
                .source(TaskState.CREATED).target(TaskState.VALIDATING)
                .event(TaskEvent.SUBMIT)
            .and()
            .withExternal()
                .source(TaskState.VALIDATING).target(TaskState.EXECUTING)
                .event(TaskEvent.VALIDATE)
            .and()
            .withExternal()
                .source(TaskState.VALIDATING).target(TaskState.FAILED)
                .event(TaskEvent.VALIDATE_FAIL)
            .and()
            .withExternal()
                .source(TaskState.EXECUTING).target(TaskState.COMPLETED)
                .event(TaskEvent.COMPLETE)
            .and()
            .withExternal()
                .source(TaskState.EXECUTING).target(TaskState.FAILED)
                .event(TaskEvent.FAIL)
            .and()
            .withExternal()
                .source(TaskState.EXECUTING).target(TaskState.COMPENSATING)
                .event(TaskEvent.COMPENSATE)
            .and()
            .withExternal()
                .source(TaskState.COMPENSATING).target(TaskState.COMPENSATED)
                .event(TaskEvent.COMPLETE);
    }

    @Override
    public void configure(StateMachineConfigurationConfigurer<TaskState, TaskEvent> config)
            throws Exception {
        config
            .withConfiguration()
                .listener(new TaskStateMachineListener());
    }
}
```

## 3. 与 Kafka 集成：事件驱动状态变更

### 状态变更事件发布

```java
@Component
public class TaskStateEventPublisher {

    private final KafkaTemplate<String, StateChangeEvent> kafkaTemplate;
    private final StateMachineFactory<TaskState, TaskEvent> stateMachineFactory;

    @Transactional
    public StateChangeEvent handleEvent(String taskId, TaskEvent event, Map<String, Object> context) {
        StateMachine<TaskState, TaskEvent> sm = stateMachineFactory.getStateMachine(taskId);
        sm.start();

        // 发送事件到状态机
        Message<TaskEvent> message = MessageBuilder
            .withPayload(event)
            .setHeader("taskId", taskId)
            .copyHeaders(context)
            .build();

        sm.sendEvent(message);

        // 构建状态变更事件
        StateChangeEvent changeEvent = StateChangeEvent.builder()
            .taskId(taskId)
            .fromState(sm.getState().getId().name())
            .toState(getNewState(sm))
            .event(event.name())
            .timestamp(Instant.now())
            .build();

        // 发布到 Kafka
        kafkaTemplate.send("task-state-changes", taskId, changeEvent);

        return changeEvent;
    }
}
```

### 消费者监听状态变更

```java
@Component
public class TaskStateChangeConsumer {

    @KafkaListener(topics = "task-state-changes", groupId = "task-orchestrator")
    public void onStateChange(StateChangeEvent event) {
        switch (TaskEvent.valueOf(event.getEvent())) {
            case VALIDATE -> validateTask(event);
            case EXECUTE -> executeTask(event);
            case COMPLETE -> completeTask(event);
            case FAIL -> handleFailure(event);
            case COMPENSATE -> compensateTask(event);
        }
    }

    private void executeTask(StateChangeEvent event) {
        // 将任务发送到执行队列
        kafkaTemplate.send("task-execution", event.getTaskId(), event);
    }

    private void compensateTask(StateChangeEvent event) {
        // 发送补偿命令到各个子服务
        kafkaTemplate.send("task-compensation", event.getTaskId(),
            CompensationEvent.of(event.getTaskId()));
    }
}
```

## 4. SAGA 模式对比

### 编排 (Choreography)

每个服务在完成本地事务后发布事件，其他服务监听事件并做出反应。

**优点**：松耦合，无需中央协调器
**缺点**：流程隐式，难以追踪和治理

```
Service A → "OrderCreated" → Service B → "PaymentProcessed" → Service C
     ↑                                                              ↓
     └──────────────── "InventoryReleased" ←─────────────────────────
```

### 编排 (Orchestration)

由中央协调器（Orchestrator）控制 Saga 中每一步的参与者。

**优点**：流程显式，易于管理和监控
**缺点**：协调器可能成为单点

```
                    Orchestrator
                  /      |       \
                 ↓       ↓        ↓
            Service A  Service B  Service C
                 ↑       ↑         ↑
                  └──────┴─────────┘
                     事件反馈
```

**推荐**：对于复杂的长任务编排，使用 Orchestration 模式。

## 5. 补偿事务设计

```java
// 正向事务步骤
@Component
public class OrderSagaSteps {

    // Step 1: 创建订单
    @KafkaListener(topics = "saga-create-order")
    public void createOrder(OrderEvent event) {
        orderRepository.save(Order.create(event));
        kafkaTemplate.send("saga-reserve-inventory", event.getOrderId(), event);
    }

    // Step 1 补偿: 取消订单
    @KafkaListener(topics = "saga-compensate-order")
    public void compensateOrder(OrderEvent event) {
        orderRepository.findById(event.getOrderId()).ifPresent(order -> {
            order.cancel();
            orderRepository.save(order);
        });
    }

    // Step 2: 预留库存
    @KafkaListener(topics = "saga-reserve-inventory")
    public void reserveInventory(OrderEvent event) {
        inventoryService.reserve(event.getProductId(), event.getQuantity());
        kafkaTemplate.send("saga-process-payment", event.getOrderId(), event);
    }

    // Step 2 补偿: 释放库存
    @KafkaListener(topics = "saga-compensate-inventory")
    public void compensateInventory(OrderEvent event) {
        inventoryService.release(event.getProductId(), event.getQuantity());
    }
}
```

## 6. Kafka 在 Saga 中的角色

```
Topic: saga-state-changes
  ├── 消费者: orchestrator   → 控制流程路由
  ├── 消费者: audit-logger   → 审计日志（长期保留）
  └── 消费者: monitor        → 实时监控

Topic: saga-commands
  ├── saga-create-order      → 创建订单的命令队列
  ├── saga-reserve-inventory → 预留库存的命令队列
  ├── saga-process-payment   → 处理支付的命令队列
  └── saga-compensate-*      → 补偿命令队列
```

## 7. 架构演进路径

```
阶段 1: 简单枚举状态
  TaskStatus: PENDING → PROCESSING → COMPLETED | FAILED
  ↓

阶段 2: 状态机
  TaskState: 更多状态 + 显式流转规则
  TaskEvent: 事件驱动状态变更
  ↓

阶段 3: 事件驱动 Saga
  Kafka 作为事件总线
  多个服务监听状态变更
  独立补偿逻辑
  ↓

阶段 4: 集中式工作流编排
  Orchestrator 控制完整流程
  补偿步骤与正向步骤一一对应
  可观测性完善
  ↓

阶段 5: 专业工作流引擎
  Temporal / Camunda / Zeebe
  更复杂的工作流、定时、人工审批
```

## 最佳实践

1. **状态机保证状态流转合法**（不允许非法跳转）
2. **每个 Saga 步骤都必须有补偿实现**
3. **幂等是所有步骤的设计前提**
4. **使用 `@Transactional` 保证本地事务与消息发送原子性**
5. **监控 Saga 执行状态**（进行中、挂起、失败）
6. **设定 Saga 超时**，超时触发自动补偿
7. **所有补偿操作也必须是幂等的**
