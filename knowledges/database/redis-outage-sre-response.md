---
tags: [sre, redis, cache, system-design, interview, fault-tolerance, circuit-breaker, rate-limiting, 故障处理, 缓存, 降级, 熔断, 限流]
description: Redis 宕机后的 15 分钟应急响应流程 + 系统容灾设计，适用于 SRE 面试和实战
created: 2026-05-11
author: Jarvis II
---

# Redis 宕机应急响应 —— 15 分钟 SRE 实战

> 场景：Redis 缓存突然挂掉，DB CPU 飙到 100%，API 开始超时。

---

## ⏱ 15 分钟应急响应时间线

### 第 0-2 分钟：止损（不要查根因）

先止血，核心目标是**防止雪崩**：

1. **降级读请求** — 关闭非核心功能（推荐位、热搜、个性化）
   - 如果 DB 扛不住，直接返回**过期缓存数据**或**降级页/静态兜底页**
2. **限流** — 在网关层（Nginx/API Gateway）快速开启限流，保护 DB 不被打死
3. **熔断** — 确认 Redis client 侧的熔断器已打开（Hystrix / Resilience4j），避免请求持续重试堆积
4. **切流** — 如果有多机房/备集群，切一部分流量到备用链路

### 第 2-5 分钟：止血恢复

快速排查能否恢复 Redis：

```bash
# 快速诊断三板斧
redis-cli ping
dmesg | grep -i oom
systemctl status redis
```

- 如果是 **OOM killed** → 临时加大 `maxmemory` + 重启
- 不追求完美，先让缓存回来
- **如果一时半会起不来** → 全面进入降级模式

### 第 5-10 分钟：解决 DB 尖峰

短时间内 DB 100% + API timeout，典型连锁反应：

| 问题 | 原因 | 措施 |
|------|------|------|
| **请求穿透** | 无缓存全打 DB | 加本地缓存兜底 |
| **连接池爆满** | 请求堆积 → 连接耗尽 → timeout → 重试 → 更堵 | 临时减小 timeout、降低最大连接数 |
| **读压力** | 写库被打满 | 读流量切到 read replica |

### 第 10-15 分钟：稳定

- 确认缓存功能恢复，流量逐步回切
- 确认 DB CPU 降到安全水位
- API 延迟恢复正常
- 通知相关方（on-call、业务团队）

---

## 🧠 系统容灾设计（面试加分）

### 1. 多级缓存，不依赖单点

```
L1: 本地进程缓存 (Caffeine/Guava) — 毫秒级，零网络开销
L2: Redis 集群
L3: DB
```

即使 Redis 挂了，L1 还能扛住大部分热点请求，DB 不会被穿透。

### 2. Redis 高可用方案

| 方案 | 适用场景 |
|------|---------|
| **Redis Sentinel** | 主从自动切换，分钟级恢复 |
| **Redis Cluster** | 分片 + 自动 failover，单分片挂了不影响整体 |
| **Redis Enterprise / 云服务** | 托管高可用 + 快照恢复 |

### 3. 缓存穿透保护

- **布隆过滤器（Bloom Filter）**：不存在的 key 直接挡在 Redis 之前
- **空值缓存**：DB 查询结果为 null 也缓存短时间（~30s），防止反复穿透

### 4. 熔断与优雅降级（代码示例）

```java
// Netflix Hystrix 模式
@HystrixCommand(fallbackMethod = "getDefaultFeed")
public Feed getUserFeed(String userId) {
    String cached = redis.get("feed:" + userId);
    if (cached != null) return parse(cached);
    return db.query(userId);  // 缓存 miss 才查 DB
}

// 降级：返回过期缓存结果或默认页
public Feed getDefaultFeed(String userId) {
    return Feed.EMPTY;  // 或从本地缓存取
}
```

### 5. 容量规划与告警

- 监控 Redis **内存使用率 + OOM kill count** → 提前告警
- 设置 `maxmemory-policy allkeys-lru`，防止 Redis 内存满了直接拒绝写入
- 大 key 定期清理（`redis-cli --bigkeys` 扫描）

---

## 💡 核心原则

> **前 5 分钟降级止血，后 10 分钟恢复排查。**
>
> 更关键的是平时把**多级缓存、熔断、限流、降级**都配好——这样 Redis 挂了也不会炸。
