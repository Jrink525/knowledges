---
title: Spring Transaction Management
tags: [spring, spring-boot, interview, 面试, database]
---

# Spring Transaction Management

## Spring 事务抽象

核心接口：`PlatformTransactionManager`

```java
public interface PlatformTransactionManager {
    TransactionStatus getTransaction(TransactionDefinition definition);
    void commit(TransactionStatus status);
    void rollback(TransactionStatus status);
}
```

主要实现：`DataSourceTransactionManager` (JDBC)、`JpaTransactionManager` (JPA/Hibernate)

## 声明式事务：`@Transactional`

```java
@Service
public class OrderService {
    @Transactional(rollbackFor = Exception.class)
    public void createOrder(Order order) {
        orderDao.insert(order);
        inventoryService.deduct(order.getProductId(), order.getQuantity());
    }
}
```

### 传播行为 Propagation

| 类型 | 行为 |
|------|------|
| `REQUIRED` | 加入当前事务，没有则新建 |
| `REQUIRES_NEW` | 挂起当前，新建独立事务 |
| `NESTED` | 嵌套事务（savepoint）|
| `MANDATORY` | 必须在事务中，否则抛异常 |

### 隔离级别

| 级别 | 脏读 | 不可重复读 | 幻读 |
|------|:---:|:---------:|:---:|
| READ_COMMITTED (默认) | ❌ | ✅ | ✅ |
| REPEATABLE_READ (MySQL) | ❌ | ❌ | ❌ (MVCC) |
| SERIALIZABLE | ❌ | ❌ | ❌ |

## 事务失效的常见原因

1. **自调用不走代理** — 类内部方法调 `@Transactional` 无效
2. **try-catch 吞掉异常** — 异常被捕获后不抛，事务不会回滚
3. **只捕获了非 RuntimeException** — 需要 `rollbackFor = Exception.class`
4. **private / protected 方法** — 默认 JDK 代理只支持 public

## 实现原理

```
@EnableTransactionManagement
  → TransactionInterceptor (AOP 环绕通知)
  → 调用前 getTransaction()
  → 执行目标方法
  → 异常 → rollback
  → 正常 → commit
```
