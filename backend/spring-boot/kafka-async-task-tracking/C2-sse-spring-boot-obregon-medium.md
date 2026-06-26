# Implementing Server-Sent Events (SSE) in Spring Boot

> 来源：Medium / Alexander Obregon
> 原文：[How to Implement Server-Sent Events (SSE) in Spring Boot](https://medium.com/@AlexanderObregon/how-to-implement-server-sent-events-sse-in-spring-boot-620024272ccb)
> 收录维度：**C — 实时推送 vs 轮询**

---

## 1. SSE 简介

Server-Sent Events (SSE) 允许服务器通过单个、长连接的 HTTP 连接向客户端推送数据。

### 优点
- **简单**：纯 HTTP，不需要特殊协议（如 WebSocket）
- **自动重连**：浏览器 EventSource API 自带断线重连
- **事件类型**：支持自定义事件名，客户端可区分处理
- **兼容 HTTP/2**：无缝集成现有基础设施

### 局限
- 单向通信：仅服务端→客户端
- 浏览器兼容：不支持 IE
- 二进制数据需要编码（如 base64）

## 2. 基础实现：SseEmitter

### Maven 依赖

只需 Spring Web Starter（spring-boot-starter-web），SSE 内置于 Servlet 容器。

### 基础 SSE 端点

```java
@Controller
public class SSEController {

    private final ExecutorService executor = Executors.newCachedThreadPool();

    @GetMapping("/stream-sse")
    public SseEmitter streamSseEvents() {
        SseEmitter emitter = new SseEmitter(Long.MAX_VALUE); // 长连接

        executor.execute(() -> {
            try {
                for (int i = 0; i < 10; i++) {
                    Thread.sleep(1000);
                    emitter.send("SSE MVC - " + System.currentTimeMillis());
                }
                emitter.complete();
            } catch (IOException | InterruptedException e) {
                emitter.completeWithError(e);
            }
        });

        return emitter;
    }
}
```

### 测试

```bash
curl -N http://localhost:8080/stream-sse
```

## 3. 带事件类型的 SSE

```java
emitter.send(SseEmitter.event()
    .name("NEWS")           // 事件名称，客户端可区分
    .data(newsItem.toString()));
```

## 4. 多客户端广播模式

```java
@RestController
public class NewsController {

    private final List<SseEmitter> emitters = new CopyOnWriteArrayList<>();
    private final NewsService newsService;

    @GetMapping("/news")
    public SseEmitter subscribeToNews() {
        SseEmitter emitter = new SseEmitter(Long.MAX_VALUE);
        emitters.add(emitter);

        emitter.onCompletion(() -> emitters.remove(emitter));
        emitter.onTimeout(() -> emitters.remove(emitter));
        emitter.onError(e -> emitters.remove(emitter));

        // 订阅时发送已有新闻
        newsService.getNewsItems().forEach(newsItem -> {
            try {
                emitter.send(SseEmitter.event().name("NEWS").data(newsItem));
            } catch (Exception e) {
                emitter.completeWithError(e);
            }
        });

        return emitter;
    }

    public void dispatchNewsItem(NewsItem newsItem) {
        List<SseEmitter> deadEmitters = new ArrayList<>();
        emitters.forEach(emitter -> {
            try {
                emitter.send(SseEmitter.event().name("NEWS").data(newsItem));
            } catch (Exception e) {
                deadEmitters.add(emitter);
            }
        });
        emitters.removeAll(deadEmitters);
    }
}
```

**关键**：使用 `CopyOnWriteArrayList` 避免并发问题。

## 5. SSE 与任务进度追踪整合

结合引子文章的任务进度追踪：

```java
@RestController
@RequestMapping("/api/tasks")
public class TaskProgressSSEController {

    private final Map<String, List<SseEmitter>> taskEmitters = new ConcurrentHashMap<>();

    @GetMapping("/{taskId}/stream")
    public SseEmitter streamTaskProgress(@PathVariable String taskId) {
        SseEmitter emitter = new SseEmitter(Long.MAX_VALUE);

        taskEmitters.computeIfAbsent(taskId, k -> new CopyOnWriteArrayList<>())
            .add(emitter);

        emitter.onCompletion(() -> removeEmitter(taskId, emitter));
        emitter.onTimeout(() -> removeEmitter(taskId, emitter));

        return emitter;
    }

    private void removeEmitter(String taskId, SseEmitter emitter) {
        List<SseEmitter> emitters = taskEmitters.get(taskId);
        if (emitters != null) {
            emitters.remove(emitter);
            if (emitters.isEmpty()) {
                taskEmitters.remove(taskId);
            }
        }
    }

    // 当 Kafka 消费者收到进度事件，推送至 SSE
    @KafkaListener(topics = "task-progress")
    public void onProgress(ProgressEvent event) {
        List<SseEmitter> emitters = taskEmitters.get(event.getTaskId());
        if (emitters != null) {
            emitters.forEach(emitter -> {
                try {
                    emitter.send(SseEmitter.event()
                        .name("PROGRESS")
                        .data(event));
                } catch (IOException e) {
                    removeEmitter(event.getTaskId(), emitter);
                }
            });
        }
    }
}
```

**客户端（浏览器）**：

```javascript
const eventSource = new EventSource(`/api/tasks/${taskId}/stream`);

eventSource.addEventListener('PROGRESS', (event) => {
    const data = JSON.parse(event.data);
    updateProgressBar(data.progress);
    updateStatus(data.message);
});

eventSource.addEventListener('COMPLETED', (event) => {
    const data = JSON.parse(event.data);
    showResult(data.result);
    eventSource.close();
});

eventSource.addEventListener('FAILED', (event) => {
    const data = JSON.parse(event.data);
    showError(data.error);
    eventSource.close();
});
```

## 6. SSE vs WebSocket vs Polling 对比

| 特性 | Polling | SSE | WebSocket |
|------|---------|-----|-----------|
| 通信方向 | 客户端→服务端（请求驱动） | 服务端→客户端 | 双向 |
| 协议 | HTTP | HTTP | ws:// / wss:// |
| 自动重连 | 需手动实现 | 浏览器内置 | 需手动实现 |
| 浏览器支持 | 全部 | 现代浏览器（不支持 IE） | 主流浏览器 |
| 服务器资源 | 低 | 中（需保持长连接） | 高（双向通道） |
| 实现复杂度 | 低 | 中 | 高 |
| 最佳场景 | 低频、非实时 | 服务端推送 | 实时互动 |

## 7. SSE 生产注意事项

1. **连接超时**：SseEmitter 有默认超时（30s），设置 `Long.MAX_VALUE` 或合理超时
2. **线程泄漏**：客户端断开后必须 cleanup（onCompletion/onTimeout/onError）
3. **负载均衡**：SSE 连接有粘性问题，需 session affinity（sticky session）
4. **连接数限制**：浏览器每域名最多 6 个 SSE 连接（HTTP/1.1）
5. **心跳**：定期发送注释行（`: heartbeat`）防止代理 / 负载均衡器断开空闲连接

### 心跳保活

```java
// 每 30s 发送空注释
executor.scheduleAtFixedRate(() -> {
    emitters.forEach(emitter -> {
        try {
            emitter.send(SseEmitter.event().comment("heartbeat").name(""));
        } catch (IOException e) {
            // client disconnected
        }
    });
}, 0, 30, TimeUnit.SECONDS);
```

## 8. 渐进式升级路径

对于引子文章的轮询方案，建议：

1. **阶段 1**：保留轮询 API，添加 SSE 端点作为补充
2. **阶段 2**：前端优先使用 SSE，下降为轮询
3. **阶段 3**：轮询作为 SSE 断开时的 fallback
