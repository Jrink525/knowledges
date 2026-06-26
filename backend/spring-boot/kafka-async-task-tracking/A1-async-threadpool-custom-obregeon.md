# Spring Boot Custom Thread Pools for Async Processing

> 来源：Medium / Alexander Obregon
> 原文：[How Spring Boot Configures Custom Thread Pools for Async Processing](https://medium.com/@AlexanderObregon/how-spring-boot-configures-custom-thread-pools-for-async-processing-2f05d6fb3e42)
> 收录维度：**A — 异步任务执行基础**

---

## 1. @Async 基础

`@EnableAsync` 开启异步支持后，Spring Boot 自动配置 `ThreadPoolTaskExecutor`。

默认配置（Spring Boot 自动配置）：
- Core Pool Size: 8
- Max Pool Size: Integer.MAX_VALUE
- Queue Capacity: Integer.MAX_VALUE (无界)
- Keep Alive: 60s

⚠️ **默认配置的陷阱**：无界队列意味着 maxPoolSize 永远不会生效——任务会一直排队，不会创建超过 corePoolSize 的线程。

## 2. 自定义 ThreadPoolTaskExecutor

```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {

    @Override
    @Bean(name = "asyncExecutor")
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);          // 核心线程数
        executor.setMaxPoolSize(10);          // 最大线程数
        executor.setQueueCapacity(25);        // 队列容量
        executor.setThreadNamePrefix("async-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();
        return executor;
    }
}
```

### 参数关系（关键理解）

当任务提交时，ThreadPoolTaskExecutor 的行为：
1. 线程数 < corePoolSize → 创建新线程执行
2. 线程数 ≥ corePoolSize → 任务入队列
3. 队列满且线程数 < maxPoolSize → 创建新线程
4. 队列满且线程数 ≥ maxPoolSize → 触发拒绝策略

**所以：如果 QueueCapacity 很大（如默认无界），maxPoolSize 几乎没有意义。**

## 3. 拒绝策略 (RejectedExecutionHandler)

| 策略 | 行为 | 适用场景 |
|------|------|---------|
| AbortPolicy (默认) | 抛出 RejectedExecutionException | 必须保证任务不丢失时告警 |
| CallerRunsPolicy | 调用者线程直接运行任务 | 自然背压，降低任务提交速度 |
| DiscardPolicy | 静默丢弃 | 非关键任务 |
| DiscardOldestPolicy | 丢弃最旧任务 | 优先处理最新任务 |

**推荐**：`CallerRunsPolicy` 对长时间运行任务最友好——让上游感知压力。

## 4. 自定义 ThreadPoolTaskExecutor 的 Bean 命名

- 命名 `@Bean("taskExecutor")` → 被 Spring Boot 自动发现，替换默认 executor
- 命名其他名称 → 需要在 `@Async("asyncExecutor")` 中显式指定

**注意**：Spring MVC 使用名为 `applicationTaskExecutor` 的 bean。如果覆盖了 `taskExecutor`，Spring MVC 的异步请求不受影响。

## 5. 安全上下文传播

如果异步任务需要访问 SecurityContext，需要自定义 TaskDecorator：

```java
public class ContextCopyingDecorator implements TaskDecorator {
    @Override
    public Runnable decorate(Runnable runnable) {
        RequestAttributes context = RequestContextHolder.currentRequestAttributes();
        return () -> {
            try {
                RequestContextHolder.setRequestAttributes(context);
                runnable.run();
            } finally {
                RequestContextHolder.resetRequestAttributes();
            }
        };
    }
}

// 在 executor 上设置
executor.setTaskDecorator(new ContextCopyingDecorator());
```

同样可以用于传播 SecurityContext、MDC（日志追踪 ID）等。

## 6. CompletableFuture 进阶

```java
@Service
public class TaskService {
    @Async
    public CompletableFuture<TaskResult> processTask(String taskId) {
        // 长期运行任务
        return CompletableFuture.completedFuture(new TaskResult(taskId, "done"));
    }
}

// 组合多个异步任务
CompletableFuture<TaskResult> future1 = taskService.processTask("task-1");
CompletableFuture<TaskResult> future2 = taskService.processTask("task-2");
CompletableFuture.allOf(future1, future2).join();
```

## 7. 异常处理

```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {
    @Override
    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
        return (ex, method, params) -> {
            System.err.println("Async error in " + method.getName() + ": " + ex.getMessage());
            // 报警、记录日志、发送到死信队列等
        };
    }
}
```

**注意**：只有返回 void 的 `@Async` 方法会走这个 handler；返回 Future/CompletableFuture 的异常由调用方处理。

---

## 最佳实践总结

1. **永远自定义线程池**，不依赖默认（无界队列风险）
2. **队列容量设合理值**（几十~几百），让 maxPoolSize 生效
3. **使用 CallerRunsPolicy** 作为生产环境拒绝策略
4. **传播上下文**（RequestAttributes、SecurityContext、MDC）
5. **为不同业务创建不同线程池**，避免互相影响
6. **监控线程池**（Micrometer 的 `executor.*` 指标）
