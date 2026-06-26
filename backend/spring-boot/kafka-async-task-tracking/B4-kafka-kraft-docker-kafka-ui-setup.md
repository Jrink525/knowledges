# B4 — Kafka 开发环境搭建：KRaft + Docker + Kafka-UI

> **匹配引子文章知识点：** ✅ Docker Kafka 安装 ✅ Kafka-UI 配置 ✅ KRaft 模式
> 来源：Medium / Bitnami 官方文档 / 实战总结
> 收录维度：**B — 消息队列集成深度（环境篇）**

---

## TL;DR

引子文章使用的 `docker run bitnami/kafka` + `KAFKA_ENABLE_KRAFT=yes` 是 Kafka 3.3+ 引入的 **KRaft 模式**（替代 ZooKeeper）。本文章深入这个环境搭建到底做了什么、有什么坑、以及生产部署建议。

---

## 1. 为什么是 KRaft？

Kafka 历史上依赖 ZooKeeper 管理元数据（broker 注册、Topic 分区分配、Controller 选举）。从 Kafka 2.8 开始引入 KRaft（Kafka Raft）模式，用 Kafka 自己的 Raft 共识协议取代 ZooKeeper。

**关键时间线：**
- Kafka 3.3.1（2022-10）→ KRaft 生产可用
- Kafka 3.7（2024-01）→ **最后支持 ZooKeeper 的版本**
- Kafka 4.0 → **彻底移除 ZooKeeper**

也就是说，如果你现在新项目用 Kafka，**应该直接上 KRaft**。

### 架构差异

```
ZooKeeper 模式：         KRaft 模式：
┌──────────┐            ┌──────────────────┐
│ Producer │            │    Producer      │
└────┬─────┘            └──────┬───────────┘
     │                         │
┌────▼──────────┐      ┌──────▼───────────┐
│   Kafka       │      │   Kafka           │
│   Broker      │      │   Broker +        │
│ (Controller)  │      │   Controller      │
└────┬──────────┘      │   (二合一)        │
     │                 └──────────────────┘
┌────▼──────────┐
│   ZooKeeper   │      ❌ 移除
│   Ensemble    │
└───────────────┘
```

**优势**：
- 少部署一个中间件（ZooKeeper 集群通常 3 节点）
- 单节点 Kafka 就能跑，开发调试极简
- Controller 故障恢复从数十秒降到 ~10 秒
- 元数据直接存在 Kafka Topic 里，强一致

**注意**：
- KRaft 的 Controller 和 Broker 可以部署在同一个进程（`PROCESS_ROLES=broker,controller`）或分开
- 开发环境用二合一最方便；生产环境建议分开以隔离职责

---

## 2. 逐行解析引子文章的 Docker 命令

```bash
docker run -d \
  --name kafka \
  --ulimit nofile=65536:65536 \           # 打开文件数限制（Kafka 需要大量 socket）
  -e KAFKA_ENABLE_KRAFT=yes \             # 🔑 启用 KRaft 模式
  -e KAFKA_CFG_NODE_ID=0 \                # 节点的唯一 ID
  -e KAFKA_CFG_PROCESS_ROLES=controller,broker \  # 同时承担 Controller + Broker
  -e KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@127.0.0.1:9093 \  # 选举投票者列表
  -e KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \  # 监听器
  -e KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \  # 客户端连接地址
  -e KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT \
  -e KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER \
  -p 9092:9092 \
  bitnami/kafka
```

### 核心参数详解

| 参数 | 值 | 含义 |
|------|-----|------|
| `KAFKA_ENABLE_KRAFT` | `yes` | 强制 KRaft 模式（Bitnami 镜像的开关） |
| `KAFKA_CFG_PROCESS_ROLES` | `broker,controller` | 单进程同时做数据存储+元数据管理 |
| `KAFKA_CFG_CONTROLLER_QUORUM_VOTERS` | `{id}@{host}:{port}` | 选举集群成员列表；单节点只需一个 |
| `KAFKA_CFG_LISTENERS` | `PLAINTEXT://:9092,CONTROLLER://:9093` | 内部监听分离：9092 数据端口，9093 控制端口 |
| `KAFKA_CFG_ADVERTISED_LISTENERS` | `PLAINTEXT://localhost:9092` | **关键**：告诉客户端连接哪个地址（Docker 内外不一致时容易翻车） |

### ⚠️ Docker 内外网络模式

这是 Kafka Docker 部署的头号坑：

```
容器内部: localhost:9092 → 本容器进程
其他容器: kafka:9092 → Docker 网络别名
宿主机:   localhost:9092 → port mapping
外部机器: <host-ip>:9092 → 需要 external listener
```

引子文章用 `PLAINTEXT://localhost:9092` 在宿主机调试没问题，但如果：
- **其他 Docker 容器**需要连接 → 要加 `EXTERNAL` 监听器：
  ```yaml
  KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093,EXTERNAL://:9094
  KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092,EXTERNAL://kafka:9094
  KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,EXTERNAL:PLAINTEXT
  ```

---

## 3. 完整版 Docker Compose（与引子一致 + Kafka-UI）

```yaml
version: '3.8'

services:
  kafka:
    image: bitnami/kafka:latest
    container_name: kafka
    ports:
      - "9092:9092"
    environment:
      - KAFKA_ENABLE_KRAFT=yes
      - KAFKA_CFG_NODE_ID=0
      - KAFKA_CFG_PROCESS_ROLES=broker,controller
      - KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@kafka:9093
      - KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093
      - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      - KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER
      - ALLOW_PLAINTEXT_LISTENER=yes
      - KAFKA_AUTO_CREATE_TOPICS_ENABLE=true
      - KAFKA_CFG_NUM_PARTITIONS=2
    volumes:
      - kafka_data:/bitnami/kafka

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    ports:
      - "8080:8080"
    environment:
      - DYNAMIC_CONFIG_ENABLED=true
      - KAFKA_CLUSTERS_0_NAME=kraft-kafka
      - KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS=kafka:9092
    depends_on:
      - kafka

volumes:
  kafka_data:
```

### Kafka-UI 使用说明

1. 启动后访问 `http://localhost:8080`
2. Kafka-UI 自动发现 `KAFKA_CLUSTERS_0_*` 配置的集群
3. 功能亮点：
   - Topic 浏览（消息查看、offset 管理）
   - Consumer Group 监控（Lag 可视化）
   - Schema Registry 集成
   - 动态配置管理（`DYNAMIC_CONFIG_ENABLED=true` 时可在 UI 修改集群配置）

---

## 4. 生产环境 KRaft 部署注意事项

### 多节点集群

```yaml
services:
  kafka-1:
    # KAFKA_CFG_NODE_ID=1
    # KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@kafka-1:9093,2@kafka-2:9093,3@kafka-3:9093
  kafka-2:
    # KAFKA_CFG_NODE_ID=2
  kafka-3:
    # KAFKA_CFG_NODE_ID=3
```

Controller 推荐奇数节点（3 或 5），与 ZooKeeper 时代的奇数法定要求一致。

### KRaft 集群初始化

首次启动时需要 **生成 Cluster ID**：

```bash
# Bitnami 镜像自动生成，无需手动指定
# 如果手动指定：
KAFKA_KRAFT_CLUSTER_ID=$(kafka-storage.sh random-uuid)
```

**所有节点必须使用相同的 Cluster ID**。

### Bitnami Mirror Node 的警告

Bitnami 官方宣布 Kafka 镜像已迁移，`bitnami/kafka` 旧 tag 可能停止更新。建议切换到 `docker.io/bitnami/kafka:3.9` 或使用官方 Apache/Confluent 镜像。

---

## 5. 引子文章中的环境准备（对照解读）

```
引子文章用 docker run（单行命令）
推荐改用 docker-compose.yml（本文章的三服务编排）
```

**为什么引子用 `docker run` 而非 compose？**
- 简洁演示：聚焦代码逻辑而非基础设施
- 但真实项目都应该用 compose 管理

**`KAFKA_AUTO_CREATE_TOPICS_ENABLE=true`**：允许 Producer/Consumer 自动创建 Topic。引子的 TaskService.createNewTopic() 中又用 AdminClient 手动创建，两者互补：
- 自动创建：`@KafkaListener` 监听不存在的 Topic 时会自动触发
- 手动创建（AdminClient）：更精细的控制（分区数、副本数、配置）

---

## 6. 常见 Docker Kafka 问题排查

### 容器启动失败，日志为空
```bash
# 开启 Bitnami 调试模式
BITNAMI_DEBUG=yes
```

### 客户端连接超时 / Connection refused
```bash
# 检查 advertised.listeners 是否正确
kafka-console-producer.sh --bootstrap-server localhost:9092 --topic test
# 如果报错，八成是 advertised 地址不对
```

### Topic 创建报 "not controller for this partition"
```
KRaft 模式需要几秒完成 Controller 选举。等 5-10 秒再重试即可。
```

### 重启后之前的数据还在吗？
```
容器内数据在 /bitnami/kafka 目录，如果用了 volume 映射则持久化。
引子文章用的是 H2 内存数据库 + Kafka 内存数据。两个都重启会丢失进度信息。
→ 详见 B6（Consumer Offset 管理与数据持久化）
```

---

> **延伸阅读**：[B5 — Spring Kafka 底层深度：Consumer API、线程安全与动态 Topic](./B5-spring-kafka-consumer-raw-api-thread-safety.md)
> **延伸阅读**：[B6 — 生产级可靠性：Offset 管理与重启恢复](./B6-kafka-offset-restart-recovery.md)
