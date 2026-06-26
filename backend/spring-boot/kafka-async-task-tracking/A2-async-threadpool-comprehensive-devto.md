# Optimizing Spring Boot Async: Thread Pool Configuration Guide

> 来源：Dev.to / Jacky
> 原文：[Optimizing Spring Boot Asynchronous Processing: A Comprehensive Guide](https://dev.to/jackynote/optimizing-spring-boot-asynchronous-processing-a-comprehensive-guide-147h)
> 收录维度：**A — 异步任务执行基础**

---

## 核心概念

### Core Pool Size（核心线程数）
- 保持活动的线程数量（即使空闲）
- **CPU 影响**：越大并发越高，CPU 利用率越高
- **内存影响**：每个线程占用栈空间，核心数越大内存消耗越多
- **选值建议**：
  - 短频任务 → 较大的 corePoolSize
  - 长任务 → 注意不要过度预留线程

### Maximum Pool Size（最大线程数）
- 线程池允许创建的线程上限（含活跃+空闲）
- **什么时候生效**：核心线程全忙 + 队列满 → 创建额外线程
- **选值建议**：
  - 根据峰值负载估算
  - 设置过低 → 任务排队积压
  - 设置过高 → 资源耗尽

### Task Queue Capacity（任务队列容量）
- 当所有核心线程忙时，任务先入队列等待
- **内存影响**：队列中每个待执行任务占用内存
- **选值建议**：
  - 根据预期峰值任务的到达速率 × 处理时间估算
  - 队列太小 → 高峰时频繁触发拒绝策略
  - 队列太大 → 内存压力 + 响应延迟

### 三者配合关系

```
提交任务 → 线程 < core? → 创建新线程执行
         → 线程 ≥ core? → 入队列等待
                        → 队列满 → 线程 < max? → 创建新线程
                                → 队列满 → 线程 ≥ max? → 拒绝策略
```

## 实践示例

```java
@Configuration
@EnableAsync
public class AsyncConfig implements AsyncConfigurer {

    @Override
    @Bean(name = "asyncExecutor")
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(3);      // 核心 3 个线程
        executor.setMaxPoolSize(10);      // 最多 10 个线程
        executor.setQueueCapacity(25);    // 队列 25 个位置
        executor.setThreadNamePrefix("custom-async-");
        executor.initialize();
        return executor;
    }
}

@Service
public class YourService {
    @Async
    public void performAsyncTask() {
        System.out.println("Async task executed in thread: " +
            Thread.currentThread().getName());
    }
}
```

## 调优建议

- **监控优先**：上线前做好指标采集（active count, queue size, rejected count）
- **从合理默认值开始**：core=4, max=8, queue=50，观察后调整
- **区分 I/O 密集型 vs CPU 密集型**：
  - CPU 密集型：core = CPU 核心数
  - I/O 密集型：core = CPU 核心数 × 2（或更高）
- **避免频繁调整**：每次改一个参数，观察稳定后继续

## 常见陷阱

1. **无界队列**：queueCapacity=Integer.MAX_VALUE → maxPoolSize 永不生效
2. **线程数设置过大**：上下文切换开销吞噬性能
3. **忽略拒绝策略**：生产环境一定设置拒绝策略
4. **不监控**：不知道线程池处于什么状态
