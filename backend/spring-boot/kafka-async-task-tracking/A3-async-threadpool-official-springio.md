# Spring Boot Task Execution & Scheduling 官方文档摘录

> 来源：[docs.spring.io](https://docs.spring.io/spring-boot/reference/features/task-execution-and-scheduling.html) (Spring Boot 3.x 参考文档)
> 收录维度：**A — 异步任务执行基础**

---

## 1. 自动配置的 AsyncTaskExecutor

当上下文中没有 `Executor` bean 时，Spring Boot 自动配置一个 `AsyncTaskExecutor`：

- **Virtual Thread 启用时**（Java 21+ + `spring.threads.virtual.enabled=true`）
  → `SimpleAsyncTaskExecutor`（每个任务一个虚拟线程）

- **其他情况** → `ThreadPoolTaskExecutor`（带合理的默认值）

## 2. 自动配置 Executor 的使用场景

`AsyncTaskExecutor` 被以下集成使用（除非自定义 `Executor` bean）：

| 场景 | 说明 |
|------|------|
| `@EnableAsync` 异步任务 | `@Async` 方法执行 |
| Spring MVC `Callable` 返回值 | 控制器异步请求处理 |
| Spring GraphQL 异步处理 | Callable 返回值 |
| Spring WebFlux 阻塞执行 | 阻塞操作支持 |
| Spring WebSocket 消息通道 | 入站/出站通道 |
| JPA 启动执行器 | 基于 JPA 仓库的启动模式 |
| ApplicationContext 后台初始化 | Bean 的异步加载 |

## 3. 自定义 Executor 的行为规则

### 规则一：自定义 `Executor` bean → 自动配置退避

```java
@Bean(name = "taskExecutor")
public Executor taskExecutor() {
    return new ThreadPoolTaskExecutor();
}
```

注册自定义 `Executor` 后，自动配置的 `AsyncTaskExecutor` 退避，自定义 executor 用于 `@EnableAsync` 常规任务执行。

### 规则二：Spring MVC/WebFlux/GraphQL 需要 `applicationTaskExecutor` bean

Spring MVC、WebFlux、GraphQL 都要求一个名为 `applicationTaskExecutor` 的 `AsyncTaskExecutor`。

```java
@Bean("applicationTaskExecutor")
SimpleAsyncTaskExecutor applicationTaskExecutor() {
    return new SimpleAsyncTaskExecutor("app-");
}
```

### 规则三：多 Executor 共存

```java
@Bean("applicationTaskExecutor")
SimpleAsyncTaskExecutor applicationTaskExecutor() {
    return new SimpleAsyncTaskExecutor("app-");
}

@Bean("taskExecutor")
ThreadPoolTaskExecutor taskExecutor() {
    ThreadPoolTaskExecutor tpte = new ThreadPoolTaskExecutor();
    tpte.setThreadNamePrefix("async-");
    return tpte;
}
```

- `applicationTaskExecutor` → Spring MVC, WebFlux, WebSocket, JPA, 后台初始化
- `taskExecutor` → `@EnableAsync` 常规任务执行

### 规则四：`@Primary` 和 `AsyncConfigurer`

如果不想用 `taskExecutor` 名称，可以用 `@Primary` 标注或定义 `AsyncConfigurer`：

```java
@Bean
AsyncConfigurer asyncConfigurer(ExecutorService executorService) {
    return new AsyncConfigurer() {
        @Override
        public Executor getAsyncExecutor() {
            return executorService;
        }
    };
}
```

### 规则五：`defaultCandidate=false` 保留自动配置

想自定义 Executor 又保留自动配置的 AsyncTaskExecutor 给其他集成用：

```java
@Bean(defaultCandidate = false)
@Qualifier("scheduledExecutorService")
ScheduledExecutorService scheduledExecutorService() {
    return Executors.newSingleThreadScheduledExecutor();
}
```

### 规则六：`spring.task.execution.mode=force` 强制保留自动配置

即使有自定义 Executor（含 `@Primary`），仍然强制使用自动配置的 `AsyncTaskExecutor`：

```yaml
spring:
  task:
    execution:
      mode: force
```

## 4. 使用 `SimpleAsyncTaskExecutorBuilder` / `ThreadPoolTaskExecutorBuilder`

Spring Boot 提供 builder 方便构造：

```java
@Bean
SimpleAsyncTaskExecutor taskExecutor(SimpleAsyncTaskExecutorBuilder builder) {
    return builder.build();
}
```

## 最佳实践

1. **明确你的 `Executor` 命名策略**，理解各个集成用哪个
2. **区分 `applicationTaskExecutor` 和 `taskExecutor`**，两者用途不同
3. **Virtual Thread 场景**：Java 21+ 启用 `spring.threads.virtual.enabled=true`
4. **复杂场景使用独立命名**，避免命名冲突导致意外行为
