---
title: Five Common Service Registries — ZK, Eureka, Nacos, Consul, ETCD (CN)
tags: [spring, microservices, service-discovery, eureka, nacos, zookeeper, consul, etcd, distributed-system, interview]
---

# 5 种常用注册中心对比：Zookeeper / Eureka / Nacos / Consul / ETCD

> 原文：楼仔（微信公众号「楼仔」）  
> 来源：https://mp.weixin.qq.com/s/NvI-3d9lgoGfxvCTJX541Q  
> 整理增强：Jarvis II

---

## 一、注册中心基本概念

### 三种角色

| 角色 | 英文 | 职责 |
|------|------|------|
| 服务提供者 | RPC Server | 启动时向 Registry 注册服务，定期发送心跳汇报存活状态 |
| 服务消费者 | RPC Client | 启动时向 Registry 订阅服务，缓存节点列表到本地，基于负载均衡选择节点发起调用 |
| 服务注册中心 | Registry | 保存 RPC Server 注册信息，节点变更时同步通知 Client |

### 注册中心核心功能

- **服务注册**：服务启动时注册自身信息（IP、端口、协议等）
- **服务发现**：消费者获取可用服务列表
- **健康检查**：定期检测服务状态，剔除不可用节点
- **变更通知**：节点上下线时通知所有订阅方
- **高可用**：自身集群化部署，防止单点故障

---

## 二、CAP 理论与一致性协议

### CAP 理论

| 属性 | 说明 |
|------|------|
| **一致性（Consistency）** | 所有节点同一时刻数据相同 |
| **可用性（Availability）** | 每个请求都有响应（成功或失败） |
| **分区容错性（Partition Tolerance）** | 部分节点故障不影响系统运行 |

**只能取其二**：网络分区是分布式系统的必然现实（P 必须选），所以实际是 **CP vs AP** 的取舍。

### 一致性协议对比

| 协议 | 所属产品 | 特点 |
|------|---------|------|
| **Paxos** | 通用 | 莱斯利·兰波特提出，极难理解。超半数副本在线即可持续可用 |
| **Raft** | ETCD, Consul | Paxos 的简化版，强调易理解易实现。超半数节点正常即可服务 |
| **ZAB** | Zookeeper | ZK 专用原子广播协议，支持崩溃恢复，专为强一致性设计 |

---

## 三、5 种注册中心详解

### 1️⃣ Zookeeper

**核心机制：**
- 用 znode 树形结构存储服务信息：`/{service}/{version}/{ip:port}`
- **Watch 机制**（推拉结合）：ZK 推送事件类型和节点信息，客户端拉取详细变更数据
- 心跳检测基于长连接（socket）

**注册/发现流程：**
1. 服务提供者启动 → 在 ZK 创建临时 znode 节点（存储 IP、端口、协议）
2. 服务消费者第一次调用 → 从 ZK 获取 IP 列表，缓存到本地
3. 后续调用 → 直接走本地缓存 + 负载均衡，不请求 ZK
4. 节点宕机 → ZK 心跳超时 → 删除对应 znode → Watch 通知消费者刷新列表

**CP 模型的问题：**
- ZK 遵循 CP（强一致性），核心算法 ZAB 设计目标就是强一致
- **致命缺陷**：Leader 选举期间（30~120s）整个集群不可用！
- 注册中心场景下，宁可读到过期数据，也不能完全不可用 → CP 不适合服务发现

> **总结**：ZK 作为分布式协调服务非常优秀，但作为注册中心不合适。国内 Dubbo 初期大量使用 ZK 当注册中心是历史原因。

---

### 2️⃣ Eureka

**核心特点（AP 原则）：**
- **AP 模型**：只要有一台 Eureka 存活就能注册/发现，数据可能不是最新的
- **去中心化**：Peer to Peer 对等架构，无 Master/Slave，所有节点互相注册
- **自我保护模式**：15 分钟内 >85% 节点失联 → 不再剔除过期服务，网络恢复后自动退出

**工作流程：**
1. Eureka Server 启动，集群间通过 Replicate 同步注册表
2. Client 启动 → 向 Server 注册服务
3. Client 每 **30s** 发送心跳
4. Server **90s** 未收到心跳 → 剔除该实例
5. Client 定时全量/增量拉取注册表，缓存到本地
6. 调用时先查本地缓存，找不到再从 Server 刷新

**为什么 Eureka 适合做注册中心？**
- 容忍数据不一致，保障服务可用
- 跨机房部署友好
- 设计初衷就是为了服务发现场景

---

### 3️⃣ Nacos

**位置：** 阿里开源

**核心能力：**
- **服务发现 + 动态配置**：Nacos = Spring Cloud 注册中心 + Spring Cloud 配置中心
- **CP/AP 可切换**：一条命令切换，灵活性极强
- 支持 DNS 和 RPC 两种服务发现方式
- 支持传输层（PING/TCP）和应用层（HTTP/MySQL/自定义）健康检查
- 支持 agent 上报 + 服务端主动检测两种模式
- 配置管理：版本跟踪、金丝雀发布、一键回滚

**为什么 Nacos 在国内流行？**
- 功能全面：注册中心 + 配置中心二合一
- 与 Spring Cloud Alibaba 生态深度集成
- 支持从其他注册中心迁移到 Nacos

---

### 4️⃣ Consul

**来源：** HashiCorp 公司（Go 语言编写）

**核心特点：**
- **CP 模型**，使用 Raft 保证强一致性
- **一站式**：服务发现 + 健康检查 + KV Store + 多数据中心
- **多数据中心**：Server 节点跨 DC 通信，Client 节点负责健康检查和请求转发
- **Gossip 协议**：维护集群成员关系
- 支持 TLS 证书生成（服务间安全通信）
- 仅一个可执行文件，部署极简

**调用流程：**
1. Producer 启动 → 向 Consul POST 注册（IP + Port）
2. Consul 每 10s 健康检查
3. Consumer 请求时 → 从 Consul 获取健康节点临时表 → 再从 Producer 获取数据

---

### 5️⃣ ETCD

**来源：** Go 语言编写，分布式高可用 KV 存储

**核心特点：**
- **CP 模型**，Raft 算法保证强一致
- **接口简单**：基于 HTTP+JSON 的 API，curl 即可操作
- **高性能**：单实例 10K QPS 写
- **持久化**：WAL（预写日志）+ Snapshot
- **Watch 机制**：支持事件监听

**框架分层：**
```
HTTP Server → Store → Raft → WAL
```
- **HTTP Server**：处理 API 请求 + 节点间同步/心跳
- **Store**：数据索引、节点状态变更、事件处理
- **Raft**：核心一致性算法
- **WAL**：持久化存储

**应用场景：** Kubernetes 的服务发现底层就是 etcd

---

## 四、核心对比

| 维度 | Zookeeper | Eureka | Nacos | Consul | ETCD |
|------|-----------|--------|-------|--------|------|
| **CAP** | CP | **AP** | **CP/AP 可切换** | CP | CP |
| **语言** | Java | Java | Java | **Go** | **Go** |
| **健康检查** | 长连接心跳 | 30s 心跳 | 多种模式（TCP/HTTP/自定义） | 详细（内存/磁盘） | 长连接 |
| **多数据中心** | ❌ | ❌ | ✅ | ✅ | ❌ |
| **KV 存储** | ✅ | ❌ | ✅ | ✅ | ✅ |
| **Watch 机制** | 服务端推送 | 长轮询 | 长轮询 | 长轮询 | Watch |
| **自带监控** | ❌ | ❌ | ❌ | ✅ (metrics) | ✅ (metrics) |
| **Spring Cloud** | ✅ starter | ✅ starter | ✅ starter | ✅ starter | ❌ |
| **配置中心** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Leader 选举** | ✅ (ZAB, 30~120s) | ❌ (去中心化) | ✅ (Raft) | ✅ (Raft) | ✅ (Raft) |
| **适合注册中心** | ❌ | ✅✅ | ✅✅ | ⚠️ | ⚠️ |

---

## 五、选型建议

### 核心原则

> **注册中心的可用性高于一致性**——宁可读到过期数据，也不能完全不可用 ❗

所以在 CAP 中应该选 **AP**。

### 推荐选择

| 场景 | 推荐 | 理由 |
|------|------|------|
| Spring Cloud Alibaba 生态 | **Nacos** | 注册中心 + 配置中心二合一，AP/CP 可切换，功能最全面 |
| Spring Cloud Netflix 旧项目 | Eureka | AP 模型，成熟稳定，但已进入维护模式 |
| 非 Java 技术栈 | Consul / ETCD | Go 语言，部署简单 |
| Kubernetes 原生 | ETCD | K8s 标配，但不是单独部署为注册中心 |
| 追求一站式治理 | Nacos | 功能最全面 |

### 我的选择（个人建议）

1. **首选 Nacos** — 功能最全，Spring Cloud Alibaba 生态成熟，AP/CP 可切换
2. **备选 Eureka** — 简单可靠，AP 原则，适合不需要配置中心的场景
3. **Consul / ETCD / ZK** — 不适合作为注册中心（CP 模型在服务发现场景有先天缺陷）

---

## 六、面试 Q&A

> **Q:** 为什么 Zookeeper 不适合做注册中心？
> **A:** ZK 遵循 CP（强一致性），Leader 选举期间（30~120s）集群不可用。注册中心的首要要求是可服务（AP），而不是强一致。ZK 更适合做分布式协调（如分布式锁、配置管理），而不是服务发现。

> **Q:** Eureka 的自我保护模式是什么？为什么需要？
> **A:** 15 分钟内 >85% 节点心跳丢失 → Eureka 认为网络故障，进入自我保护模式：不剔除过期服务，只提供当前节点数据。网络恢复后自动退出。目的是防止因网络抖动导致大量服务被误剔除。

> **Q:** Nacos 和 Eureka 的核心区别是什么？
> **A:** (1) Nacos 支持 CP/AP 切换，Eureka 只有 AP；(2) Nacos 内置配置中心，Eureka 只做注册；(3) Nacos 健康检查方式更丰富（TCP/HTTP/自定义）；(4) Nacos 仍有活跃维护，Eureka 已进入维护模式。

> **Q:** ETCD 和 Zookeeper 的差异？
> **A:** 两者都是 CP 模型，但 ETCD 使用 Raft 协议（更易理解），支持 gRPC 通信，单实例 10K QPS 写性能。ETCD 是 K8s 标配存储后端。ZK 使用 ZAB 协议，社区更成熟但性能低于 ETCD。

> **Q:** 微服务中服务调用到底经过几次注册中心？
> **A:** 只有第一次。服务消费者第一次调用时从注册中心拉取服务列表并缓存到本地，后续调用直接走本地缓存 + 负载均衡，不再请求注册中心。注册中心只在节点变更时推送更新。

---

## 七、参考

- 原文：[楼仔 - 5 种常用注册中心对比](https://mp.weixin.qq.com/s/NvI-3d9lgoGfxvCTJX541Q)
- Nacos 官方：https://nacos.io
- Eureka 文档：https://github.com/Netflix/eureka
- ETCD 官方：https://etcd.io
- Consul 官方：https://www.consul.io

---

## 八、手写一个简易注册中心（实战）

> 纸上得来终觉浅。理解了原理后，自己实现一个极简版注册中心，才能真正吃透注册/发现/健康检查的核心逻辑。

### 设计目标

用 Spring Boot 实现一个 **极简注册中心**，包含：
- ✅ 服务注册（register）
- ✅ 服务发现（discover）
- ✅ 心跳续约（heartbeat）
- ✅ 健康检查 & 剔除过期节点
- ✅ 客户端自动注册 + 心跳（Spring Boot Starter）
- ✅ 客户端负载均衡（随机策略）
- ❌ 不实现集群/CAP（单机即可，重在理解流程）

### 8.1 数据模型

```java
@Data
@AllArgsConstructor
@NoArgsConstructor
public class ServiceInstance {
    private String serviceName;    // 服务名，如 user-service
    private String instanceId;     // 实例 ID，唯一标识
    private String host;           // IP
    private int port;              // 端口
    private Map<String, String> metadata;  // 扩展元数据
    private long lastHeartbeat;    // 最后心跳时间戳
    private boolean healthy;       // 是否健康
}
```

### 8.2 注册中心核心逻辑

```java
@Component
public class SimpleRegistry {

    private final ConcurrentHashMap<String, Map<String, ServiceInstance>> registry = new ConcurrentHashMap<>();

    // ========== 服务注册 ==========
    public synchronized ServiceInstance register(String serviceName, String host, int port, Map<String, String> metadata) {
        String instanceId = UUID.randomUUID().toString().replace("-", "");
        ServiceInstance inst = new ServiceInstance();
        inst.setServiceName(serviceName);
        inst.setInstanceId(instanceId);
        inst.setHost(host);
        inst.setPort(port);
        inst.setMetadata(metadata);
        inst.setLastHeartbeat(System.currentTimeMillis());
        inst.setHealthy(true);
        registry.computeIfAbsent(serviceName, k -> new ConcurrentHashMap<>()).put(instanceId, inst);
        System.out.println("[Registry] 注册 " + serviceName + " / " + host + ":" + port);
        return inst;
    }

    // ========== 服务发现 ==========
    public List<ServiceInstance> discover(String serviceName) {
        Map<String, ServiceInstance> instances = registry.get(serviceName);
        if (instances == null) return Collections.emptyList();
        return instances.values().stream()
                .filter(ServiceInstance::isHealthy)
                .collect(Collectors.toList());
    }

    // ========== 心跳续约 ==========
    public boolean heartbeat(String instanceId) {
        for (Map<String, ServiceInstance> instances : registry.values()) {
            ServiceInstance inst = instances.get(instanceId);
            if (inst != null) {
                inst.setLastHeartbeat(System.currentTimeMillis());
                inst.setHealthy(true);
                return true;
            }
        }
        return false;
    }

    // ========== 剔除过期节点 ==========
    @Scheduled(fixedRate = 5000)  // 每 5s 检查
    public void evictExpiredInstances() {
        long now = System.currentTimeMillis();
        long threshold = 10_000;  // 10s 无心跳视为过期
        registry.forEach((name, instances) -> {
            instances.values().removeIf(inst -> {
                if (now - inst.getLastHeartbeat() > threshold) {
                    System.out.println("[Registry] 剔除 " + inst.getInstanceId() + " (" + inst.getHost() + ":" + inst.getPort() + ")");
                    return true;
                }
                return false;
            });
        });
    }

    // ========== 获取全部（监控用） ==========
    public Map<String, List<ServiceInstance>> getAllServices() {
        Map<String, List<ServiceInstance>> result = new HashMap<>();
        registry.forEach((name, instances) -> result.put(name, new ArrayList<>(instances.values())));
        return result;
    }
}
```

### 8.3 REST API

```java
@RestController
@RequestMapping("/registry")
public class RegistryController {

    @Autowired private SimpleRegistry registry;

    @PostMapping("/register")
    public ServiceInstance register(@RequestBody RegisterRequest req) {
        return registry.register(req.getServiceName(), req.getHost(), req.getPort(), req.getMetadata());
    }

    @GetMapping("/discover/{serviceName}")
    public List<ServiceInstance> discover(@PathVariable String serviceName) {
        return registry.discover(serviceName);
    }

    @PostMapping("/heartbeat/{instanceId}")
    public String heartbeat(@PathVariable String instanceId) {
        return registry.heartbeat(instanceId) ? "OK" : "INSTANCE_NOT_FOUND";
    }

    @GetMapping("/services")
    public Map<String, List<ServiceInstance>> getAllServices() {
        return registry.getAllServices();
    }
}
```

### 8.4 客户端 Starter（自动注册 + 心跳）

```java
@Component
public class ServiceRegistration {

    private final RegistryClientProperties props;
    private final RestTemplate restTemplate;
    private String instanceId;

    public ServiceRegistration(RegistryClientProperties props, RestTemplate restTemplate) {
        this.props = props;
        this.restTemplate = restTemplate;
    }

    @PostConstruct
    public void register() {
        RegisterRequest req = new RegisterRequest();
        req.setServiceName(props.getServiceName());
        req.setHost(props.getHost());
        req.setPort(props.getPort());

        String url = "http://" + props.getRegistryHost() + ":" + props.getRegistryPort() + "/registry/register";
        ServiceInstance inst = restTemplate.postForObject(url, req, ServiceInstance.class);
        this.instanceId = inst.getInstanceId();
        System.out.println("[Client] 注册成功 instanceId=" + instanceId);
        startHeartbeat();
    }

    private void startHeartbeat() {
        Executors.newSingleThreadScheduledExecutor().scheduleAtFixedRate(() -> {
            String url = "http://" + props.getRegistryHost() + ":" + props.getRegistryPort()
                    + "/registry/heartbeat/" + instanceId;
            try {
                if ("INSTANCE_NOT_FOUND".equals(restTemplate.postForObject(url, null, String.class)))
                    System.err.println("[Client] 心跳失败，实例已被移除");
            } catch (Exception e) {
                System.err.println("[Client] 心跳异常: " + e.getMessage());
            }
        }, 0, 3, TimeUnit.SECONDS);
    }

    @PreDestroy
    public void deregister() {
        System.out.println("[Client] 下线 instanceId=" + instanceId);
    }
}
```

### 8.5 消费者负载均衡

```java
@Component
public class ServiceConsumer {

    @Autowired private RestTemplate restTemplate;
    @Autowired private RegistryClientProperties props;

    private final Map<String, List<ServiceInstance>> cache = new ConcurrentHashMap<>();
    private final Random random = new Random();

    public List<ServiceInstance> refreshServiceList(String serviceName) {
        String url = "http://" + props.getRegistryHost() + ":" + props.getRegistryPort()
                + "/registry/discover/" + serviceName;
        List<ServiceInstance> list = Arrays.asList(restTemplate.getForObject(url, ServiceInstance[].class));
        cache.put(serviceName, list);
        return list;
    }

    public ServiceInstance pickInstance(String serviceName) {
        List<ServiceInstance> instances = cache.get(serviceName);
        if (instances == null || instances.isEmpty()) instances = refreshServiceList(serviceName);
        if (instances == null || instances.isEmpty())
            throw new RuntimeException("No available instance for " + serviceName);
        return instances.get(random.nextInt(instances.size()));
    }

    @Scheduled(fixedRate = 15_000)
    public void refreshCache() { cache.clear(); }
}
```

### 8.6 运行演示

```bash
# 启动注册中心
$ java -jar registry-server.jar --server.port=8761

# 启动两个服务提供者
$ java -jar user-service.jar --server.port=8081
# → [Registry] 注册 user-service / 127.0.0.1:8081

$ java -jar user-service.jar --server.port=8082
# → [Registry] 注册 user-service / 127.0.0.1:8082

# 服务发现
$ curl http://localhost:8761/registry/discover/user-service
# → [{instanceId: abc..., host: 127.0.0.1, port: 8081, healthy: true},
#    {instanceId: def..., host: 127.0.0.1, port: 8082, healthy: true}]

# 停掉 8081 后等待 10s
$ curl http://localhost:8761/registry/discover/user-service
# → [{instanceId: def..., host: 127.0.0.1, port: 8082, healthy: true}]
# ✅ 8081 已自动剔除
```

### 8.7 与生产级注册中心对比

| 特性 | 简易版 | Eureka | Nacos |
|------|--------|--------|-------|
| 集群 | ❌ 单机 | ✅ Peer to Peer | ✅ Raft |
| CAP | N/A | AP | CP/AP 可切换 |
| 自我保护 | ❌ | ✅ | ✅ |
| 配置中心 | ❌ | ❌ | ✅ |
| 心跳周期 | 3s | 30s | 5s |
| 剔除阈值 | 10s | 90s | 15s |
| 变更推送 | ❌ 轮询 | ✅ 长轮询 | ✅ 长轮询 |
| 监控 UI | ❌ | ✅ | ✅ |

### 8.8 代码量

| 模块 | 行数 |
|------|------|
| SimpleRegistry（存储 + 注册发现 + 心跳 + 剔除） | ~70 行 |
| RegistryController（4 个 REST 端点） | ~40 行 |
| ServiceRegistration（自动注册 + 心跳线程） | ~60 行 |
| ServiceConsumer（发现 + 负载均衡 + 缓存） | ~50 行 |
| 模型 + 配置 POJO | ~40 行 |
| **合计** | **~260 行** |

> 260 行 Java 就写出来了一个麻雀虽小五脏俱全的注册中心。理解了这个，再看 Eureka 源码就会清晰很多——Eureka 做的就是把每个点做到极致：集群复制、自我保护、长轮询推送、监控面板…
