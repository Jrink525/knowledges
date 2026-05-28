---
title: "Spring @Transactional 完全指南：从 JDBC 到源码"
tags:
  - spring
  - transaction
  - jdbc
  - jpa
  - hibernate
  - aop
date: 2026-05-28
source: "综合整理自 vladmihalcea.com, marcobehler.com, javarevisited.blogspot.com, medium.com, docs.spring.io"
---

# Spring @Transactional 完全指南：从 JDBC 到源码

> **核心原则**：Spring 的所有事务管理，归根结底只是 JDBC 的 `setAutoCommit(false)` → 执行 SQL → `commit()` / `rollback()`。

---

## 目录

- [第一章：从零开始 — JDBC 事务的本质](#第一章从零开始--jdbc-事务的本质)
  - [1.1 4 行代码搞懂数据库事务](#11-4-行代码搞懂数据库事务)
  - [1.2 ACID 到底在说什么](#12-acid-到底在说什么)
  - [1.3 隔离级别与 Savepoint](#13-隔离级别与-savepoint)
- [第二章：Spring 事务抽象层](#第二章spring-事务抽象层)
  - [2.1 PlatformTransactionManager 接口](#21-platformtransactionmanager-接口)
  - [2.2 DataSourceTransactionManager 源码](#22-datasourcetransactionmanager-源码)
  - [2.3 TransactionTemplate — 编程式事务](#23-transactiontemplate--编程式事务)
- [第三章：@Transactional 详解](#第三章transactional-详解)
  - [3.1 声明式事务的三种配置方式](#31-声明式事务的三种配置方式)
  - [3.2 @Transactional 所有属性全解](#32-transactional-所有属性全解)
  - [3.3 类级别 vs 方法级别](#33-类级别-vs-方法级别)
  - [3.4 在 Spring Boot 中的自动配置](#34-在-spring-boot-中的自动配置)
- [第四章：代理机制（底层实现）](#第四章代理机制底层实现)
  - [4.1 Spring 如何用 AOP 实现事务](#41-spring-如何用-aop-实现事务)
  - [4.2 CGLib 代理 vs JDK 动态代理](#42-cglib-代理-vs-jdk-动态代理)
  - [4.3 事务拦截器的完整流程](#43-事务拦截器的完整流程)
- [第五章：传播行为（Propagation）详解](#第五章传播行为propagation详解)
  - [5.1 REQUIRED — 默认行为](#51-required--默认行为)
  - [5.2 REQUIRES_NEW — 独立事务](#52-requires_new--独立事务)
  - [5.3 NESTED — 嵌套事务（Savepoint）](#53-nested--嵌套事务savepoint)
  - [5.4 SUPPORTS / MANDATORY / NOT_SUPPORTED / NEVER](#54-supports--mandatory--not_supported--never)
  - [5.5 传播行为决策树](#55-传播行为决策树)
- [第六章：隔离级别详解](#第六章隔离级别详解)
  - [6.1 四种隔离级别](#61-四种隔离级别)
  - [6.2 脏读 / 不可重复读 / 幻读](#62-脏读--不可重复读--幻读)
  - [6.3 实战：生成报表时选什么隔离级别](#63-实战生成报表时选什么隔离级别)
- [第七章：readOnly 优化深度解析](#第七章readonly-优化深度解析)
  - [7.1 Spring 5.1 之前：只改 FlushMode](#71-spring-51-之前只改-flushmode)
  - [7.2 Spring 5.1 之后：Hibernate Session 级别的优化](#72-spring-51-之后hibernate-session-级别的优化)
  - [7.3 内存节省实测](#73-内存节省实测)
  - [7.4 读写分离路由](#74-读写分离路由)
- [第八章：回滚规则详解](#第八章回滚规则详解)
  - [8.1 默认回滚行为：RuntimeException 才回滚](#81-默认回滚行为runtimeexception-才回滚)
  - [8.2 自定义回滚规则](#82-自定义回滚规则)
  - [8.3 Spring 6.2 新增：全局回滚策略](#83-spring-62-新增全局回滚策略)
- [第九章：最佳实践](#第九章最佳实践)
  - [9.1 类级别 readOnly=true + 方法级别覆盖](#91-类级别-readonlytrue--方法级别覆盖)
  - [9.2 Propagation.NEVER 隔离非事务代码](#92-propagationnever-隔离非事务代码)
  - [9.3 事务边界在 Service 层](#93-事务边界在-service-层)
  - [9.4 多个 TransactionManager 管理多个数据源](#94-多个-transactionmanager-管理多个数据源)
- [第十章：常见陷阱与解决方案](#第十章常见陷阱与解决方案)
  - [10.1 同一类内部调用 @Transactional 失效](#101-同一类内部调用-transactional-失效)
  - [10.2 自注入 @Lazy 解决](#102-自注入-lazy-解决)
  - [10.3 Checked Exception 不回滚](#103-checked-exception-不回滚)
  - [10.4 事务不锁数据 — 并发问题](#104-事务不锁数据--并发问题)
  - [10.5 两个数据源只有一个是事务的](#105-两个数据源只有一个是事务的)
  - [10.6 @PostConstruct 中开启事务](#106-postconstruct-中开启事务)
  - [10.7 public 方法才生效的限制](#107-public-方法才生效的限制)
- [第十一章：源码深度解析](#第十一章源码深度解析)
  - [11.1 TransactionInterceptor 完整源码分析](#111-transactioninterceptor-完整源码分析)
  - [11.2 事务同步机制（TransactionSynchronization）](#112-事务同步机制transactionsynchronization)
  - [11.3 物理事务 vs 逻辑事务](#113-物理事务-vs-逻辑事务)
  - [11.4 完整的请求处理时序图](#114-完整的请求处理时序图)

---

# 第一章：从零开始 — JDBC 事务的本质

> **重要**：不要跳过这一节。Spring 所做的一切都基于这 4 行 JDBC 代码。

## 1.1 4 行代码搞懂数据库事务

无论你用 Spring @Transactional、纯 Hibernate、jOOQ 还是任何其他数据库库，底层都是在做同一件事：

```java
import java.sql.Connection;

// 1. 获取数据库连接
Connection connection = dataSource.getConnection();

try (connection) {
    // 2. ⭐ 这才是"开启事务"的唯一方式
    connection.setAutoCommit(false);

    // 执行你的 SQL 语句...
    // INSERT INTO users ... 或 UPDATE accounts ...

    // 3. 提交事务
    connection.commit();

} catch (SQLException e) {
    // 4. 回滚事务
    connection.rollback();
}
```

**关键理解**：

- `setAutoCommit(true)` — 每一条 SQL 自动在一个独立事务中执行（默认行为）
- `setAutoCommit(false)` — 你掌控事务，必须手动调用 `commit()` 或 `rollback()`
- 这个设置对整个连接生命周期有效，只需设置一次，无需重复调用
- Spring @Transactional 底层就是帮你自动调用这 4 行代码

### 真实场景演示

```java
// 场景：用户注册 + 发送欢迎邮件 + 积分初始化
// 如果不用事务，第三步失败时无法回滚前两步
Connection conn = dataSource.getConnection();
try {
    conn.setAutoCommit(false);

    // 步骤 1：插入用户
    PreparedStatement ps1 = conn.prepareStatement(
        "INSERT INTO users(name, email) VALUES(?, ?)");
    ps1.setString(1, "张三");
    ps1.setString(2, "zhangsan@example.com");
    ps1.executeUpdate();

    // 步骤 2：初始化积分
    PreparedStatement ps2 = conn.prepareStatement(
        "INSERT INTO points(user_id, balance) VALUES(?, ?)");
    ps2.setLong(1, generatedUserId);
    ps2.setInt(2, 100);
    ps2.executeUpdate();

    // 步骤 3：发送欢迎邮件（假设这里是数据库记录）
    PreparedStatement ps3 = conn.prepareStatement(
        "INSERT INTO notifications(user_id, content) VALUES(?, ?)");
    ps3.setLong(1, generatedUserId);
    ps3.setString(2, "欢迎加入！");
    ps3.executeUpdate();

    conn.commit();  // ✅ 三步全部成功
} catch (SQLException e) {
    conn.rollback();  // ❌ 任何一步失败，全部回滚
    throw e;
} finally {
    conn.close();
}
```

## 1.2 ACID 到底在说什么

| 属性 | 含义 | JDBC 层面的实现 |
|------|------|-----------------|
| **Atomicity** 原子性 | 全部成功或全部失败 | `commit()` / `rollback()` |
| **Consistency** 一致性 | 数据库完整性约束永远不被破坏 | 由数据库约束 + 事务保证 |
| **Isolation** 隔离性 | 并发事务互不干扰 | `setTransactionIsolation()` |
| **Durability** 持久性 | 已提交事务永久保存 | `commit()` 后的 WAL 日志 |

**注意**：Spring 无法保证 ACID。它只是 JDBC 的封装，ACID 最终由数据库提供。

## 1.3 隔离级别与 Savepoint

```java
// 隔离级别 — 对应 @Transactional(isolation = ...)
connection.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
// 可选值：
//   TRANSACTION_READ_UNCOMMITTED   = 1
//   TRANSACTION_READ_COMMITTED     = 2  （PostgreSQL/默认）
//   TRANSACTION_REPEATABLE_READ    = 4  （MySQL/InnoDB 默认）
//   TRANSACTION_SERIALIZABLE       = 8

// Savepoint — 对应 @Transactional(propagation = Propagation.NESTED)
Savepoint savepoint = connection.setSavepoint();
try {
    // 尝试执行子操作...
    connection.releaseSavepoint(savepoint);  // ✅ 子操作成功
} catch (SQLException e) {
    connection.rollback(savepoint);  // ❌ 只回滚到 savepoint
    // 主事务可以继续
}
```

---

# 第二章：Spring 事务抽象层

## 2.1 PlatformTransactionManager 接口

```java
// PlatformTransactionManager.java — Spring 事务管理的核心接口
public interface PlatformTransactionManager {

    // 根据 TransactionDefinition 获取事务状态
    TransactionStatus getTransaction(TransactionDefinition definition)
            throws TransactionException;

    // 提交事务
    void commit(TransactionStatus status) throws TransactionException;

    // 回滚事务
    void rollback(TransactionStatus status) throws TransactionException;
}

// TransactionDefinition — 定义事务的元数据
public interface TransactionDefinition {
    int PROPAGATION_REQUIRED     = 0;
    int PROPAGATION_SUPPORTS     = 1;
    int PROPAGATION_MANDATORY    = 2;
    int PROPAGATION_REQUIRES_NEW = 3;
    int PROPAGATION_NOT_SUPPORTED = 4;
    int PROPAGATION_NEVER        = 5;
    int PROPAGATION_NESTED       = 6;

    int ISOLATION_DEFAULT                = -1;
    int ISOLATION_READ_UNCOMMITTED       = 1;
    int ISOLATION_READ_COMMITTED         = 2;
    int ISOLATION_REPEATABLE_READ        = 4;
    int ISOLATION_SERIALIZABLE           = 8;

    int TIMEOUT_DEFAULT = -1;

    int getPropagationBehavior();
    int getIsolationLevel();
    int getTimeout();
    boolean isReadOnly();
    String getName();
}

// TransactionStatus — 当前事务的状态
public interface TransactionStatus {

    boolean isNewTransaction();    // 是否新开启的事务
    boolean hasSavepoint();        // 是否有 savepoint
    void setRollbackOnly();        // 标记回滚
    boolean isRollbackOnly();      // 是否被标记为回滚
    boolean isCompleted();         // 是否已完成（提交或回滚）
    void flush();                  // 刷新底层会话
}
```

## 2.2 DataSourceTransactionManager 源码

```java
// DataSourceTransactionManager.java — 简化后的核心源码
public class DataSourceTransactionManager
        extends AbstractPlatformTransactionManager
        implements ResourceTransactionManager {

    private DataSource dataSource;

    @Override
    protected Object doGetTransaction() {
        DataSourceTransactionObject txObject = new DataSourceTransactionObject();

        // 从当前线程绑定的资源中获取 ConnectionHolder
        // (同一线程连续调用时复用连接)
        ConnectionHolder holder =
            (ConnectionHolder) TransactionSynchronizationManager
                .getResource(this.dataSource);
        txObject.setConnectionHolder(holder, false);
        return txObject;
    }

    @Override
    protected void doBegin(Object transaction, TransactionDefinition definition) {
        DataSourceTransactionObject txObject = (DataSourceTransactionObject) transaction;
        Connection newCon = null;

        try {
            // ⭐ 获取数据库连接
            newCon = obtainDataSource().getConnection();

            // ⭐ setAutoCommit(false) — 这才是"开启事务"！
            if (newCon.getAutoCommit()) {
                newCon.setAutoCommit(false);
            }

            // ⭐ 设置隔离级别
            if (definition.getIsolationLevel() != TransactionDefinition.ISOLATION_DEFAULT) {
                newCon.setTransactionIsolation(definition.getIsolationLevel());
            }

            // ⭐ 设置只读提示
            if (definition.isReadOnly()) {
                newCon.setReadOnly(true);
            }

            // 将连接绑定到当前线程
            txObject.setConnectionHolder(new ConnectionHolder(newCon), true);
            TransactionSynchronizationManager.bindResource(
                obtainDataSource(), txObject.getConnectionHolder());

        } catch (Throwable ex) {
            if (newCon != null) {
                newCon.close();
            }
            throw new CannotCreateTransactionException(ex);
        }
    }

    @Override
    protected void doCommit(DefaultTransactionStatus status) {
        // ⭐ 这就是 JDBC 的 connection.commit()
        DataSourceTransactionObject txObject =
            (DataSourceTransactionObject) status.getTransaction();
        Connection con = txObject.getConnectionHolder().getConnection();

        con.commit();
    }

    @Override
    protected void doRollback(DefaultTransactionStatus status) {
        // ⭐ 这就是 JDBC 的 connection.rollback()
        DataSourceTransactionObject txObject =
            (DataSourceTransactionObject) status.getTransaction();
        Connection con = txObject.getConnectionHolder().getConnection();

        con.rollback();
    }

    @Override
    protected void doSetRollbackOnly(DefaultTransactionStatus status) {
        DataSourceTransactionObject txObject =
            (DataSourceTransactionObject) status.getTransaction();
        txObject.setRollbackOnly();
    }
}
```

**关键洞察**：DataSourceTransactionManager 的核心 `doBegin` / `doCommit` / `doRollback`，底层就是我们在第一章看到的 4 行 JDBC 代码。

## 2.3 TransactionTemplate — 编程式事务

编程式事务提供了比 JDBC 更优雅的方式，适合需要精细化控制的场景。

```java
@Service
public class PaymentService {

    @Autowired
    private TransactionTemplate transactionTemplate;

    @Autowired
    private DataSource dataSource;

    /**
     * 编程式事务：适合需要精确控制边界的场景
     * 避免了 @Transactional 的 AOP 代理限制
     */
    public Long transferMoney(TransferRequest request) {

        return transactionTemplate.execute(status -> {
            // ✅ 自动包含在事务中
            // ✅ SQLException 自动转为运行时异常 → 自动回滚
            // ✅ 返回的结果作为 execute() 方法的返回值

            long txId = paymentDao.insertTransaction(request);

            // 扣款
            if (!accountDao.deduct(request.getFromAccount(), request.getAmount())) {
                // 手动标记回滚（Spring 不强制，但加了更明确）
                status.setRollbackOnly();
                return null;
            }

            // 入账
            accountDao.credit(request.getToAccount(), request.getAmount());

            return txId;
        });
    }

    /**
     * TransactionTemplate 还支持 Lambda 无返回值版本
     */
    public void executeWithoutResult() {
        transactionTemplate.executeWithoutResult(status -> {
            // 不需要返回值的编程式事务
        });
    }
}
```

**编程式 vs 声明式对比**：

| 对比维度 | TransactionTemplate (编程式) | @Transactional (声明式) |
|---------|------------------------------|------------------------|
| 代理要求 | 无，直接调用 | 需要 AOP 代理 |
| 同一类内部调用 | ✅ 有效 | ❌ 失效 |
| 精细化控制 | ✅ 任意粒度 | ❌ 方法级 |
| 代码侵入性 | 中 | 低 |
| 适用场景 | 复杂事务边界、重试逻辑 | 80% 的标准场景 |

---

# 第三章：@Transactional 详解

## 3.1 声明式事务的三种配置方式

### 方式 1：XML 声明（历史遗留）

```xml
<!-- 纯 XML 时代，现在基本不用了 -->
<tx:advice id="txAdvice" transaction-manager="txManager">
    <tx:attributes>
        <tx:method name="get*" read-only="true"/>
        <tx:method name="find*" read-only="true"/>
        <tx:method name="*" />
    </tx:attributes>
</tx:advice>

<aop:config>
    <aop:pointcut id="serviceOperation"
        expression="execution(* com.example.service.*.*(..))"/>
    <aop:advisor advice-ref="txAdvice" pointcut-ref="serviceOperation"/>
</aop:config>
```

### 方式 2：@EnableTransactionManagement + Java 配置

```java
@Configuration
@EnableTransactionManagement  // 启用注解式事务管理
public class AppConfig {

    @Bean
    public DataSource dataSource() {
        // 配置数据源...
    }

    @Bean
    public PlatformTransactionManager txManager(DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }
}
```

### 方式 3：Spring Boot 自动配置（最推荐）

```java
// 只需这 1 个依赖 → 自动配置全部完成
// build.gradle
// implementation 'org.springframework.boot:spring-boot-starter-data-jpa'

// Spring Boot 自动完成：
// 1. ⭐ 自动注册 PlatformTransactionManager Bean
// 2. ⭐ 自动注册 @EnableTransactionManagement
// 3. ⭐ 自动配置 DataSource (HikariCP)
// 4. ⭐ 自动配置 JpaTransactionManager / DataSourceTransactionManager
```

## 3.2 @Transactional 所有属性全解

```java
@Target({ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Inherited
@Documented
public @interface Transactional {

    // 指定 TransactionManager Bean 的名称（适用于多数据源场景）
    @AliasFor("transactionManager")
    String value() default "";

    @AliasFor("value")
    String transactionManager() default "";

    // 传播行为（默认 REQUIRED）
    Propagation propagation() default Propagation.REQUIRED;

    // 隔离级别（默认使用数据库的默认级别）
    Isolation isolation() default Isolation.DEFAULT;

    // 超时时间（秒），默认 -1 = 使用数据库超时
    int timeout() default TransactionDefinition.TIMEOUT_DEFAULT;

    // 超时时间（字符串形式，支持占位符）
    String timeoutString() default "";

    // 是否只读事务（默认 false）
    boolean readOnly() default false;

    // 哪些异常触发回滚
    Class<? extends Throwable>[] rollbackFor() default {};

    // 哪些异常触发回滚（类名模式）
    String[] rollbackForClassName() default {};

    // 哪些异常不触发回滚
    Class<? extends Throwable>[] noRollbackFor() default {};

    // 哪些异常不触发回滚（类名模式）
    String[] noRollbackForClassName() default {};
}
```

### 属性详解对照表

| 属性 | 默认值 | 说明 | 典型场景 |
|------|--------|------|---------|
| `propagation` | `REQUIRED` | 事务传播行为 | 独立审计日志用 `REQUIRES_NEW` |
| `isolation` | `DEFAULT` | 事务隔离级别 | 生成报表用 `REPEATABLE_READ` |
| `timeout` | `-1`（无超时） | 超时秒数 | 大查询限制 30s 避免死锁 |
| `readOnly` | `false` | 只读优化 | 查询方法用 `readOnly = true` |
| `rollbackFor` | `{}` | 指定回滚异常 | 将 checked exception 加入回滚 |
| `noRollbackFor` | `{}` | 指定不回滚异常 | 某些业务异常不想回滚 |

## 3.3 类级别 vs 方法级别

```java
// 类级别：默认事务设置
@Service
@Transactional(readOnly = true)   // 该类所有方法默认只读
public class UserService {

    // 继承类级别的 @Transactional(readOnly = true)
    public User findById(Long id) {
        return userRepository.findById(id).orElse(null);
    }

    // ⭐ 方法级别覆盖类级别设置
    @Transactional(readOnly = false)  // 写操作覆盖为读写事务
    public User createUser(User user) {
        return userRepository.save(user);
    }

    // 隔离级别也可以在方法级别覆盖
    @Transactional(isolation = Isolation.SERIALIZABLE)
    public boolean addUniqueEmail(String email) {
        // 串行化级别防止并发重复
    }
}
```

**最佳实践**（来自 Vlad Mihalcea）：

```java
@Service
@Transactional(readOnly = true)      // 类级别：默认只读
public class UserService implements UserDetailsService {

    @Override
    public UserDetails loadUserByUsername(String username) {
        // 只读方法 → 自动优化
    }

    @Transactional                     // 方法级别：读写（覆盖只读）
    public void createUser(User user) {
        // 写操作 → 正常事务
    }
}
```

## 3.4 在 Spring Boot 中的自动配置

```java
// 以下在 Spring Boot 中自动完成，一般不需要手动配置

// JpaTransactionManager（使用 JPA 时）
@Bean
@ConditionalOnMissingBean(PlatformTransactionManager.class)
public PlatformTransactionManager transactionManager(
        EntityManagerFactory entityManagerFactory) {
    return new JpaTransactionManager(entityManagerFactory);
}

// DataSourceTransactionManager（仅使用 JDBC/MyBatis 时）
@Bean
@ConditionalOnMissingBean(PlatformTransactionManager.class)
public PlatformTransactionManager transactionManager(DataSource dataSource) {
    return new DataSourceTransactionManager(dataSource);
}
```

---

# 第四章：代理机制（底层实现）

## 4.1 Spring 如何用 AOP 实现事务

> Spring 无法修改你的 Java 类来插入事务代码。但它有一个优势：**IoC 容器**。

```
用户代码：UserRestController
    │
    ▼  (实际持有的是 Proxy，不是 UserService)
ProxyUserService (CGLib 代理)
    │  ┌──────────────────────────────┐
    │  │ proxy 负责：                  │
    │  │ 1. getConnection()            │
    │  │ 2. setAutoCommit(false)       │
    │  │ 3. 调用真实 UserService       │
    │  │ 4. commit() / rollback()      │
    │  └──────────────────────────────┘
    │
    ▼
真实 UserService (你写的代码)
    │
    ▼
userDao.save(user)  ← 只做业务，无需关心事务
```

## 4.2 CGLib 代理 vs JDK 动态代理

```java
// 两种代理模式的对比
public class ProxyDemo {

    // JDK 动态代理 — 要求实现接口
    // Spring 默认：如果类实现了接口，用 JDK Proxy
    public interface UserService {
        void createUser(User user);
    }

    public class UserServiceImpl implements UserService {
        @Transactional
        public void createUser(User user) {
            // ...
        }
    }

    // CGLib 代理 — 通过子类实现（不要求接口）
    // Spring 默认：如果没有接口，用 CGLib
    // Spring Boot 2.x+ 默认使用 CGLib
    @Service
    public class NoInterfaceService {
        @Transactional
        public void doSomething() {
            // ...
        }
    }
}
```

| 对比维度 | JDK 动态代理 | CGLib 代理 |
|---------|-------------|-----------|
| 实现方式 | 实现接口 | 继承子类 |
| 要求 | 必须实现接口 | 无需接口 |
| final 方法 | 不涉及 | ❌ 无法代理 |
| Spring Boot 默认 | ❌ | ✅ |
| 性能 | 略高（反射） | 略低（字节码） |

## 4.3 事务拦截器的完整流程

```java
// TransactionInterceptor.java — 核心源码
public class TransactionInterceptor extends TransactionAspectSupport
        implements MethodInterceptor {

    @Override
    @Nullable
    public Object invoke(MethodInvocation invocation) throws Throwable {
        // 获取目标方法的事务属性（从 @Transactional 注解解析）
        Class<?> targetClass = invocation.getThis() != null
            ? AopUtils.getTargetClass(invocation.getThis())
            : null;

        Method specificMethod = ReflectionUtils
            .getMostSpecificMethod(invocation.getMethod(), targetClass);

        // ⭐ 获取 @Transactional 注解的完整属性
        TransactionAttribute txAttr = getTransactionAttributeSource()
            .getTransactionAttribute(specificMethod, targetClass);

        // ⭐ 确定事务管理器
        PlatformTransactionManager tm = determineTransactionManager(txAttr);

        // ⭐ 核心：这里调用 TransactionAspectSupport 的模板方法
        return invokeWithinTransaction(invocation.getMethod(), targetClass,
            invocation::proceed, txAttr, tm);
    }
}

// TransactionAspectSupport — 真正的模板方法
@Nullable
protected Object invokeWithinTransaction(Method method,
        @Nullable Class<?> targetClass,
        final InvocationCallback invocation,
        @Nullable TransactionAttribute txAttr,
        @Nullable PlatformTransactionManager tm) throws Throwable {

    PlatformTransactionManager actualTm = determineTransactionManager(txAttr);

    // ⭐ 1. 获取事务 — 这里调用 PlatformTransactionManager.getTransaction()
    TransactionInfo txInfo = createTransactionIfNecessary(actualTm, txAttr, joinpoint);

    Object retVal;

    try {
        // ⭐ 2. 执行目标方法（你写的业务代码）
        retVal = invocation.proceedWithInvocation();
    } catch (Throwable ex) {
        // ⭐ 3. 异常时 — 根据规则决定是否回滚
        completeTransactionAfterThrowing(txInfo, ex);
        throw ex;
    } finally {
        cleanupTransactionInfo(txInfo);
    }

    // ⭐ 4. 正常返回 — 提交事务
    commitTransactionAfterReturning(txInfo);
    return retVal;
}
```

---

# 第五章：传播行为（Propagation）详解

## 5.1 REQUIRED — 默认行为

```java
// REQUIRED：如果存在事务则加入，否则新建
// 这是最常用的传播行为

@Service
public class UserService {

    @Autowired
    private AuditService auditService;

    @Transactional(propagation = Propagation.REQUIRED)  // 默认值
    public void createUser(User user) {
        userDao.save(user);                     // 主业务
        auditService.log("USER_CREATED", user);  // 同一事务
    }
}

@Service
public class AuditService {

    @Transactional(propagation = Propagation.REQUIRED)  // 加入已有事务
    public void log(String action, Object target) {
        auditDao.insert(new AuditLog(action, target));
    }
}
```

**物理行为**：
```
createUser() 开启事务 T1 ──────► auditorService.log() 加入 T1 ──────► commit T1
getConnection()                                                   setAutoCommit(false) 一次
```

## 5.2 REQUIRES_NEW — 独立事务

```java
// REQUIRES_NEW：无论是否存在事务，都新建一个独立事务
// 外部事务会被挂起（suspend），新事务执行完后再恢复

@Service
public class PaymentService {

    @Autowired
    private AuditService auditService;

    @Transactional(propagation = Propagation.REQUIRED)
    public void processPayment(Payment payment) {
        // ... 主业务逻辑
        paymentDao.update(payment);

        // ⭐ 独立事务：即使主事务回滚，审计日志也要保留
        auditService.logAudit("PAYMENT", payment.getId());
    }
}

@Service
public class AuditService {

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logAudit(String action, Long targetId) {
        auditDao.insert(new AuditLog(action, targetId));
        // 这个事务 commit/rollback 独立于调用者
    }
}
```

**物理行为**：
```
createUser() T1 ──► auditorService 开始 T2（T1 挂起）──► commit T2 ──► 恢复 T1 ──► commit/rollback T1
      连接1                                连接2
```

**真实案例 — 审计日志的独立性**：

```java
// 业务场景：即使支付失败，也要记录尝试
@Service
public class PaymentService {

    @Transactional
    public void transfer(Account from, Account to, BigDecimal amount) {
        try {
            // 扣款
            accountDao.debit(from.getId(), amount);
            accountDao.credit(to.getId(), amount);

            auditService.log("TRANSFER_SUCCESS", from, to, amount);
        } catch (Exception e) {
            // 即使转账失败，也要记录失败日志
            // ⭐ REQUIRES_NEW 确保日志事务独立提交
            auditService.log("TRANSFER_FAILED", from, to, amount);
            throw e;
        }
    }
}
```

## 5.3 NESTED — 嵌套事务（Savepoint）

> NESTED 使用 JDBC Savepoint 实现，不是真正的独立事务。

```java
// NESTED：使用 Savepoint 实现部分回滚
// 外部事务回滚时，嵌套事务也回滚
// 但嵌套事务可以独立回滚到 savepoint，不影响外部事务

@Service
public class BatchImportService {

    @Transactional(propagation = Propagation.REQUIRED)
    public void batchImport(List<Record> records) {
        for (Record record : records) {
            try {
                // ⭐ 每个记录独立保保存点
                importSingleRecord(record);
            } catch (DataIntegrityViolationException e) {
                // 只回滚这一条，继续下一条
                log.warn("Skipping invalid record: {}", record.getId());
            }
        }
    }

    @Transactional(propagation = Propagation.NESTED)
    public void importSingleRecord(Record record) {
        // 这个 Savepoint 回滚不影响 batchImport
        dao.insert(record);
    }
}
```

**Savepoint 底层实现**：

```java
// JDBC 层：
// batchImport 开始事务 T1
//   importSingleRecord(record1) → Savepoint sp1
//     失败 → rollback to Savepoint sp1 ← 只回滚这一条
//   importSingleRecord(record2) → Savepoint sp2
//     成功 → release Savepoint sp2
// commit T1
```

**⚠️ 依赖数据库支持**：SQL Server、Oracle、PostgreSQL 支持 Savepoint；MySQL 部分支持。

### 传播行为对比演练

```java
// 完整案例：展示 REQUIRED vs REQUIRES_NEW vs NESTED 的区别

@Service
public class DemoService {

    public void showDifferences() {
        // 场景：外部方法 + 内部方法都失败
        // 两种情况：内部失败 / 外部失败

        // 1. REQUIRED + REQUIRED
        //    内部失败 → 整体回滚
        //    外部失败 → 整体回滚
        //    结果：A 和 B 都回滚

        // 2. REQUIRED + REQUIRES_NEW
        //    内部失败 → 内部回滚，外部可继续
        //    外部失败 → 外部回滚，内部已提交，不受影响
        //    结果：A 回滚，B 已提交 ✅

        // 3. REQUIRED + NESTED
        //    内部失败 → rollback to savepoint，外部可继续
        //    外部失败 → 外部回滚，嵌套也回滚
        //    结果：B 回滚，A 可继续，但外部失败时都回滚
    }
}
```

## 5.4 SUPPORTS / MANDATORY / NOT_SUPPORTED / NEVER

```java
// SUPPORTS — 有事务则加入，没有则无事务执行
@Transactional(propagation = Propagation.SUPPORTS)
public void optionalTransaction() {
    // 被事务方法调用时 = 加入事务
    // 被非事务方法调用时 = 没有事务
}

// MANDATORY — 强制要求已有事务，否则抛异常
@Transactional(propagation = Propagation.MANDATORY)
public void requireExistingTransaction() {
    // 必须从事务上下文中调用 → 否则 IllegalTransactionStateException
}

// NOT_SUPPORTED — 挂起当前事务，以非事务方式执行
@Transactional(propagation = Propagation.NOT_SUPPORTED)
public void runWithoutTransaction() {
    // 适用于不需要事务的耗时操作（如文件处理）
}

// NEVER — 强制要求没有事务，否则抛异常
@Transactional(propagation = Propagation.NEVER)
public void neverInTransaction() {
    // 确保不在事务中执行
}
```

## 5.5 传播行为决策树

```
当前方法被调用时，是否存在事务？
        │
        ├─ REQUIRED ─── 有事务 → 加入 | 无事务 → 新建
        │
        ├─ SUPPORTS ─── 有事务 → 加入 | 无事务 → 无事务执行
        │
        ├─ MANDATORY ── 有事务 → 加入 | 无事务 → 抛异常
        │
        ├─ REQUIRES_NEW ── 总是新建事务（挂起旧的）
        │
        ├─ NOT_SUPPORTED ── 挂起事务，无事务执行
        │
        ├─ NEVER ────────── 有事务 → 抛异常 | 无事务 → 正常执行
        │
        └─ NESTED ───────── 有事务 → Savepoint | 无事务 → 类似 REQUIRED
```

---

# 第六章：隔离级别详解

## 6.1 四种隔离级别

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 默认场景 |
|---------|:----:|:---------:|:----:|---------|
| `READ_UNCOMMITTED` | ✅ 可能 | ✅ 可能 | ✅ 可能 | 极少使用 |
| `READ_COMMITTED` | ❌ 避免 | ✅ 可能 | ✅ 可能 | PostgreSQL / SQL Server 默认 |
| `REPEATABLE_READ` | ❌ 避免 | ❌ 避免 | ✅ 可能 | MySQL/InnoDB 默认 |
| `SERIALIZABLE` | ❌ 避免 | ❌ 避免 | ❌ 避免 | 极端一致性场景 |

## 6.2 脏读 / 不可重复读 / 幻读

```java
// 脏读（Dirty Read）— 读到未提交的数据
// Transaction A: UPDATE account SET balance=0 WHERE id=1  (未提交)
// Transaction B: SELECT balance FROM account WHERE id=1 → 0
// Transaction A: ROLLBACK  ← 数据实际还是 100！
// ❌ B 读到了不存在的数据

// 不可重复读（Non-repeatable Read）
// Transaction A: SELECT balance FROM account WHERE id=1 → 100
// Transaction B: UPDATE account SET balance=0 WHERE id=1 → COMMIT
// Transaction A: SELECT balance FROM account WHERE id=1 → 0 (变了！)
// ❌ 同一次事务中，同一条查询结果不同

// 幻读（Phantom Read）
// Transaction A: SELECT * FROM orders WHERE amount > 100 → 10 条
// Transaction B: INSERT INTO orders ... → COMMIT
// Transaction A: SELECT * FROM orders WHERE amount > 100 → 11 条 (多了一条)
// ❌ 同一次事务中，范围查询结果数量不同
```

## 6.3 实战：生成报表时选什么隔离级别

```java
@Service
@Transactional(readOnly = true)
public class ReportService {

    /**
     * 问题场景：默认 READ_COMMITTED 下，生成报表时
     * 多次查询可能看到不同的数据（因为其他事务在提交）
     */
    @Transactional(isolation = Isolation.REPEATABLE_READ)
    public Report generateDailyReport(LocalDate date) {
        // 第一步：查询汇总
        BigDecimal totalRevenue = orderDao.sumRevenueByDate(date);

        // 第二步：查询明细（此时如果有其他事务提交了新的订单）
        // ❌ 如果使用 READ_COMMITTED，明细可能比汇总多
        List<Order> orders = orderDao.findByDate(date);

        // ⭐ REPEATABLE_READ 保证整个事务中看到的快照一致
        // 汇总和明细永远对得上

        return new Report(date, totalRevenue, orders);
    }
}
```

---

# 第七章：readOnly 优化深度解析

> 来源：Vlad Mihalcea — Spring read-only transaction Hibernate optimization

## 7.1 Spring 5.1 之前：只改 FlushMode

```java
// Spring 5.1 之前，@Transactional(readOnly = true) 只做了一件事：
// 将 Hibernate Session 的 flush mode 设置为 MANUAL

// HibernateFlushMode.java
public enum FlushMode {
    AUTO,       // 每次查询前自动 flush（默认）
    MANUAL,     // 不自动 flush，必须手动调用 session.flush()
    COMMIT,     // 提交时 flush
    ALWAYS      // 每次查询前都 flush
}

// 效果：
// - 禁止 dirty checking 自动发 UPDATE
// - ❌ 仍然保留实体的 loaded state（快照数据）→ 占用内存
// - ❌ 没有告诉 Hibernate 这个 Session 是"只读"的
```

## 7.2 Spring 5.1 之后：Hibernate Session 级别的优化

Vlad Mihalcea 向 Spring 提交了 PR（SPR-16956），在 Spring 5.1 中做了额外优化：

```java
// Spring 5.1+ 中，JpaTransactionManager 的 doBegin 方法新增：

@Override
protected void doBegin(Object transaction, TransactionDefinition definition) {
    // ... 原有的连接准备代码 ...

    // ⭐ 新增：如果 readOnly=true，设置 Hibernate Session.defaultReadOnly=true
    if (definition.isReadOnly()) {
        // 调用 session.setDefaultReadOnly(true)
        // 这样所有新加载的实体都不会保存 loaded state
        try {
            Session session = entityManager.unwrap(Session.class);
            session.setDefaultReadOnly(true);
        } catch (PersistenceException ex) {
            // 非 JPA 场景忽略
        }
    }
}
```

**效果**：

```java
@Transactional(readOnly = true)  // ← 这行代码现在做了更多
public List<Post> findByTitle(String title) {
    List<Post> posts = postDAO.findByTitle(title);

    // 🔍 验证：Hibernate PersistenceContext 中没有 loaded state
    SharedSessionContractImplementor session =
        entityManager.unwrap(SharedSessionContractImplementor.class);
    PersistenceContext persistenceContext = session.getPersistenceContext();

    for (Post post : posts) {
        EntityEntry entry = persistenceContext.getEntry(post);
        // ⭐ Spring 5.1 前：entry.getLoadedState() != null
        // ⭐ Spring 5.1+：entry.getLoadedState() == null ← 已丢弃快照！
    }
    return posts;
}

@Transactional  // readOnly=false（默认）
public Post findById(Long id) {
    Post post = postDAO.findById(id);

    SharedSessionContractImplementor session =
        entityManager.unwrap(SharedSessionContractImplementor.class);
    EntityEntry entry = session.getPersistenceContext().getEntry(post);

    // ⭐ 读写模式：loaded state 保留（可供 dirty checking 使用）
    assertNotNull(entry.getLoadedState());
    return post;
}
```

## 7.3 内存节省实测

```java
/**
 * 内存优化示例：大批量只读查询
 *
 * 场景：每天凌晨生成 10 万条报表数据
 * 加载的实体都是只读的，不需要 dirty checking
 */
@Service
@Transactional(readOnly = true)  // ← 节省大量内存
public class BatchReadService {

    public void processLargeRead() {
        List<Order> orders = orderDao.findAll();  // 10 万条

        // 在 Spring 5.1+ 中：
        // 每条 Order 实体只存储当前数据（约 200 字节）
        // ✅ 10 万 × 200B = 20MB 堆内存

        // 在 Spring 5.1 之前：
        // 每条 Order 还额外保留一份 loaded state 快照（约 200 字节）
        // ❌ 10 万 × 400B = 40MB 堆内存（翻倍！）
    }
}
```

## 7.4 读写分离路由

另一个 readOnly 的优势：可以路由到只读数据库从库：

```java
/**
 * 结合 readOnly 实现读写分离路由
 * 数据源路由到不同的数据库节点
 */
@Service
@Transactional(readOnly = true)
public class ReadOnlyService {

    // 此处的查询路由到数据库从库（Replica）
    public List<User> findAll() { ... }
}

@Service
@Transactional
public class ReadWriteService {

    // 此处的写入路由到数据库主库（Primary）
    public void save(User user) { ... }
}
```

实现方式：自定义 `AbstractRoutingDataSource`，根据 `TransactionSynchronizationManager.isCurrentTransactionReadOnly()` 切换数据源。详细实现见 [Vlad Mihalcea 的文章](https://vladmihalcea.com/read-write-read-only-transaction-routing-spring/)。

---

# 第八章：回滚规则详解

## 8.1 默认回滚行为：RuntimeException 才回滚

```java
// ⭐ 这是最常被误解的地方！
// 默认规则：只有 RuntimeException 和 Error 才触发回滚
// Checked Exception 不会触发回滚！

@Transactional
public void transferMoney(Account from, Account to, BigDecimal amount)
        throws InsufficientBalanceException {  // ⚠️ Checked Exception

    accountDao.debit(from.getId(), amount);  // 扣款成功
    accountDao.credit(to.getId(), amount);    // 入账成功

    // ... 业务逻辑发现余额不足
    throw new InsufficientBalanceException("余额不足");
    // ❌ 不会回滚！扣款和入账都提交了！
}
```

## 8.2 自定义回滚规则

```java
@Transactional(
    rollbackFor = InsufficientBalanceException.class,        // ⭐ 指定要回滚
    noRollbackFor = BusinessWarningException.class            // ⭐ 指定不回滚
)
public void transferMoney(Account from, Account to, BigDecimal amount) {
    try {
        accountDao.debit(from.getId(), amount);
        accountDao.credit(to.getId(), amount);
    } catch (InsufficientBalanceException e) {
        // ✅ 现在会回滚了（通过 rollbackFor 指定）
        throw e;
    }
}

// 也可以使用类名模式
@Transactional(rollbackForClassName = {"InsufficientBalance", "AccountFrozen"})
public void transfer() {
    // 匹配类名包含 InsufficientBalance 或 AccountFrozen 的异常
}
```

## 8.3 Spring 6.2 新增：全局回滚策略

```java
// Spring 6.2+ 支持全局默认回滚行为
// 将所有异常（包括 Checked Exception）默认纳入回滚

@Configuration
@EnableTransactionManagement(rollbackOn = ALL_EXCEPTIONS)
public class AppConfig {
    // 所有 @Transactional 方法中，任何异常都回滚
}
```

---

# 第九章：最佳实践

## 9.1 类级别 readOnly=true + 方法级别覆盖

```java
@Service
@Transactional(readOnly = true)   // 所有查询默认只读
public class UserService {

    @Transactional(readOnly = true)  // 可省略（继承类级别）
    public User findById(Long id) { ... }

    @Transactional(readOnly = false) // 写方法覆盖
    public User createUser(User user) { ... }

    @Transactional(readOnly = false)
    public User updateUser(User user) { ... }

    @Transactional
    public void deleteUser(Long id) { ... }  // 不写 readOnly = 默认 false
}
```

## 9.2 Propagation.NEVER 隔离非事务代码

```java
/**
 * 场景：解析 CSV 文件 + 生成报表（纯内存操作）
 * 不应占用数据库连接资源
 */
@Service
public class StatementService {

    @Transactional(propagation = Propagation.NEVER)  // 绝不在事务中
    public Report processStatement(MultipartFile file) {
        // 1. 解析文件（纯 CPU/内存操作，不需要 DB 连接）
        StatementModel model = parser.parse(file);

        // 2. 生成报表（纯内存）
        Report report = generateReport(model);

        // ⭐ 只有这里是 DB 操作，由 OperationService 管理自己的事务
        operationService.addStatementReportOperation(report);

        return report;
    }
}

@Service
@Transactional(readOnly = true)
public class OperationService {

    @Transactional(isolation = Isolation.SERIALIZABLE)  // 最严格隔离
    public boolean addStatementReportOperation(Report report) {
        // 在独立的事务（SERIALIZABLE）中
        // 确保没有重复提交
    }
}
```

## 9.3 事务边界在 Service 层

> ⭐ **不要把 @Transactional 放在 Controller 层**。

```java
// ❌ 错误：事务在 Controller 层
@RestController
@Transactional  // 危险！事务会覆盖整个 HTTP 请求
public class UserController {
    // 事务时间 = HTTP 请求处理时间
    // 长连接占用数据库连接池
    // 延迟增长 → 连接池耗尽
}

// ✅ 正确：事务在 Service 层
@RestController
public class UserController {
    @Autowired
    private UserService userService;

    @PostMapping("/users")
    public ResponseEntity<User> createUser(@RequestBody UserRequest req) {
        return ResponseEntity.ok(userService.createUser(req));
    }
}

@Service
@Transactional
public class UserService {
    // 事务只覆盖 Service 方法执行期间
    // Controller 的 JSON 解析、校验等不包括在内
}
```

## 9.4 多个 TransactionManager 管理多个数据源

```java
// 多个数据源需要多个 TransactionManager
@Configuration
public class MultiDataSourceConfig {

    @Primary
    @Bean
    public PlatformTransactionManager orderTxManager(
            @Qualifier("orderDataSource") DataSource ds) {
        return new DataSourceTransactionManager(ds);
    }

    @Bean
    public PlatformTransactionManager reportTxManager(
            @Qualifier("reportDataSource") DataSource ds) {
        return new DataSourceTransactionManager(ds);
    }
}

// 通过 value 或 transactionManager 指定使用哪个
@Service
public class MultiDbService {

    @Transactional("orderTxManager")
    public void saveOrder(Order order) {
        orderDbDao.save(order);
    }

    @Transactional("reportTxManager")
    public void saveReport(Report report) {
        reportDbDao.save(report);
    }

    // ⚠️ 注意：不支持跨数据源的分布式事务（需要 JTA/ChainedTransactionManager）
}
```

---

# 第十章：常见陷阱与解决方案

## 10.1 同一类内部调用 @Transactional 失效

```java
// ❌ 经典错误：同一类中 A 方法调用 B 方法
@Service
public class UserService {

    @Transactional
    public void registerAccount(User user) {
        // 1. 保存用户
        saveUser(user);

        // 2. 创建默认团队
        createTeam(user);  // ❌ @Transactional 不会生效！
    }

    @Transactional
    public void saveUser(User user) {
        userDao.save(user);
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void createTeam(User user) {
        teamDao.createDefaultTeam(user.getId());
    }
}
```

**为什么失效？**
```
UserService.registerAccount() 调用 saveUser()
    │
    ▼
this.saveUser(user)  ← this 是原始对象，不是代理

要经过代理需要：
userService.saveUser(user)  ← userService 是从容器注入的代理对象
```

## 10.2 自注入 @Lazy 解决

```java
// ✅ 方案 1：自注入（Self Injection）
@Service
public class UserService {

    @Autowired
    @Lazy  // ⭐ 使用 @Lazy 避免循环依赖
    private UserService self;  // 注入的是代理对象

    @Transactional
    public void registerAccount(User user) {
        self.saveUser(user);        // ✅ 通过代理调用
        self.createTeam(user);      // ✅ 通过代理调用
    }

    @Transactional
    public void saveUser(User user) { ... }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void createTeam(User user) { ... }
}

// ✅ 方案 2：提取到另一个 Service
@Service
public class InternalUserService {
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void createTeam(User user) { ... }
}

// ✅ 方案 3：使用 TransactionTemplate（编程式）
@Service
public class UserService {

    @Autowired
    private TransactionTemplate transactionTemplate;

    public void registerAccount(User user) {
        saveUser(user);
        transactionTemplate.execute(status -> {
            teamDao.createDefaultTeam(user.getId());
            return null;
        });
    }
}
```

## 10.3 Checked Exception 不回滚

```java
// ❌ 错误：Checked Exception 不回滚
@Transactional
public void processOrder(Order order) throws IOException {
    orderDao.save(order);
    // 文件操作失败
    throw new IOException("File not found");
    // ❌ order 已提交！因为有该异常是 Checked Exception
}

// ✅ 修正
@Transactional(rollbackFor = IOException.class)
public void processOrder(Order order) throws IOException {
    orderDao.save(order);
    throw new IOException("File not found");
    // ✅ 现在会回滚了
}

// 或者将异常包装为 RuntimeException
@Transactional
public void processOrder(Order order) {
    try {
        orderDao.save(order);
        Files.readAllBytes(path);
    } catch (IOException e) {
        throw new RuntimeException(e);  // ✅ 自动触发回滚
    }
}
```

## 10.4 事务不锁数据 — 并发问题

```java
// ❌ 错误认知："事务 = 数据锁定"
// 事务的隔离性不等于数据锁定！

@Transactional
public void processPendingOrders() {
    List<Order> orders = orderDao.findAllByStatus(OrderStatus.PENDING);
    // 同时另一个实例也执行这个查询
    // ⚠️ 两个实例都查到同样的数据！
    for (Order order : orders) {
        process(order);
        order.setStatus(OrderStatus.PROCESSED);
    }
    // ❌ 同一批数据被处理了两次！
}
```

### 解决方案 1：悲观锁（SELECT ... FOR UPDATE）

```java
@Transactional
public void processPendingOrders() {
    // ✅ 使用悲观锁：锁定这些行，其他事务必须等待
    List<Order> orders = orderDao.findAllByStatusWithLock(
        OrderStatus.PENDING, LockModeType.PESSIMISTIC_WRITE);

    for (Order order : orders) {
        process(order);
        order.setStatus(OrderStatus.PROCESSED);
    }
}

// Repository
@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("SELECT o FROM Order o WHERE o.status = :status")
List<Order> findAllByStatusWithLock(@Param("status") OrderStatus status);
```

### 解决方案 2：乐观锁（@Version）

```java
@Entity
@Table(name = "orders")
public class Order {

    @Id
    private Long id;

    // ✅ 乐观锁：每次更新时检查版本号
    @Version
    private Long version;

    private OrderStatus status;
    // ...
}

// 更新 SQL：
// UPDATE orders SET status = ?, version = version + 1
// WHERE id = ? AND version = ?   ← 版本匹配才更新
// 如果 version 不匹配 → OptimisticLockException → 回滚事务
```

## 10.5 两个数据源只有一个是事务的

```java
// ❌ 默认只管理一个数据源的事务
@Service
public class MixedDataService {

    @Transactional  // 只管理 primary 数据源
    public void transferBetweenDatabases() {
        mysqlDao.save(order);          // ✅ 事务管理
        redisTemplate.opsForValue()... // ❌ Redis 不在事务中
        mongoTemplate.save(log);       // ❌ MongoDB 不在事务中
    }
}

// ✅ 方案：ChainedTransactionManager（链式事务管理器）
// 按序提交，异常时反向回滚
// ⚠️ 非 2PC，不能保证原子性！
@Bean
public ChainedTransactionManager chainedTxManager(
        DataSourceTransactionManager mysqlTxManager,
        MongoTransactionManager mongoTxManager) {
    return new ChainedTransactionManager(mysqlTxManager, mongoTxManager);
}

// ✅ 更可靠的方案：JTA（2PC 分布式事务）
// 需要 JTA 提供者（Atomikos、Bitronix 等）
// 完整的两阶段提交保证原子性
```

## 10.6 @PostConstruct 中开启事务

```java
@Component
public class DataInitializer {

    @Autowired
    private UserService userService;

    // ❌ @PostConstruct 时代理还未完全初始化
    @PostConstruct
    public void init() {
        userService.createAdminUser();
        // ❌ 没有事务！代理未就绪
    }
}

// ✅ 方案：使用 @EventListener(ApplicationReadyEvent.class)
@Component
public class DataInitializer {

    @Autowired
    private UserService userService;

    @EventListener(ApplicationReadyEvent.class)  // ✅ 应用完全启动后
    @Transactional
    public void init() {
        userService.createAdminUser();  // ✅ 事务生效
    }
}
```

## 10.7 public 方法才生效的限制

```java
// Spring 6.0 之前：只有 public 方法支持 @Transactional
// Spring 6.0+：protected/package-private 也支持（CGLib 代理）

// ❌ private 方法永远不行
@Service
public class DemoService {
    @Transactional
    private void secretMethod() {  // ❌ 不会生效
        // Spring 无法代理 private 方法
    }
}
```

---

# 第十一章：源码深度解析

## 11.1 TransactionInterceptor 完整源码分析

```java
// TransactionInterceptor.java — Spring-tx 模块核心
public class TransactionInterceptor extends TransactionAspectSupport
        implements MethodInterceptor, Serializable {

    // ⭐ 切入点：任何被 @Transactional 标记的方法被调用时先进入这里
    @Override
    @Nullable
    public Object invoke(MethodInvocation invocation) throws Throwable {
        Class<?> targetClass = AopUtils.getTargetClass(invocation.getThis());

        // 推断目标方法（考虑接口和实现类）
        Method specificMethod = ReflectionUtils
            .getMostSpecificMethod(invocation.getMethod(), targetClass);

        // 从 @Transactional 注解解析事务属性
        TransactionAttribute txAttr = getTransactionAttributeSource()
            .getTransactionAttribute(specificMethod, targetClass);

        // 确定使用哪个 TransactionManager
        PlatformTransactionManager tm = determineTransactionManager(txAttr);

        // ⭐ 调用父类的模板方法
        return invokeWithinTransaction(invocation.getMethod(), targetClass,
            invocation::proceed, txAttr, tm);
    }
}

// TransactionAspectSupport.invokeWithinTransaction()
// — 这是事务管理的"模板方法"核心
@Nullable
protected Object invokeWithinTransaction(Method method,
        @Nullable Class<?> targetClass,
        final InvocationCallback invocation,
        @Nullable TransactionAttribute txAttr,
        @Nullable PlatformTransactionManager tm) throws Throwable {

    final TransactionAttribute transactionAttribute = txAttr;

    // ⭐ 1. 获取 TransactionManager
    if (tm == null) {
        tm = getTransactionManager(transactionAttribute, method.getDeclaringClass());
    }

    // ⭐ 2. 通过 TransactionManager 获取/创建事务
    //     这触发 PlatformTransactionManager.getTransaction()
    TransactionInfo txInfo = createTransactionIfNecessary(tm, transactionAttribute, joinpoint);

    Object retVal;

    try {
        // ⭐ 3. 执行真实方法（你的业务代码）
        retVal = invocation.proceedWithInvocation();
    } catch (Throwable ex) {
        // ⭐ 4. 异常处理：检查是否需要回滚
        completeTransactionAfterThrowing(txInfo, ex);
        throw ex;
    } finally {
        // 清理事务上下文
        cleanupTransactionInfo(txInfo);
    }

    // ⭐ 5. 提交事务
    commitTransactionAfterReturning(txInfo);
    return retVal;
}

// ⭐ 异常处理的核心逻辑
protected void completeTransactionAfterThrowing(
        TransactionInfo txInfo, Throwable ex) {

    if (txInfo != null && txInfo.getTransactionStatus() != null) {
        if (txInfo.transactionAttribute != null &&
                txInfo.transactionAttribute.rollbackOn(ex)) {
            // ⭐ 符合回滚条件 → 回滚
            txInfo.getTransactionManager().rollback(txInfo.getTransactionStatus());
        } else {
            // 不符合回滚条件 → 还是提交！
            txInfo.getTransactionManager().commit(txInfo.getTransactionStatus());
        }
    }
}

// ⭐ rollbackOn 的判断逻辑（DefaultTransactionAttribute）
public boolean rollbackOn(Throwable ex) {
    // ⭐ 默认：RuntimeException 或 Error 才回滚
    return (ex instanceof RuntimeException || ex instanceof Error);
}
```

## 11.2 事务同步机制（TransactionSynchronization）

```java
// ⭐ 事务同步：允许在事务的生命周期中注册回调
// 用于连接管理、资源绑定等

// TransactionSynchronizationManager — 线程级别的事务资源绑定
public abstract class TransactionSynchronizationManager {

    // ⭐ 每个线程维护自己的事务资源
    private static final ThreadLocal<Map<Object, Object>> resources =
        new NamedThreadLocal<>("Transactional resources");

    private static final ThreadLocal<Set<TransactionSynchronization>> synchronizations =
        new NamedThreadLocal<>("Transaction synchronizations");

    private static final ThreadLocal<String> currentTransactionName =
        new NamedThreadLocal<>("Current transaction name");

    private static final ThreadLocal<Boolean> currentTransactionReadOnly =
        new NamedThreadLocal<>("Current transaction read-only status");

    private static final ThreadLocal<Integer> currentTransactionIsolationLevel =
        new NamedThreadLocal<>("Current transaction isolation level");

    private static final ThreadLocal<Boolean> actualTransactionActive =
        new NamedThreadLocal<>("Actual transaction active");

    // 绑定资源到当前线程（例如：ConnectionHolder）
    public static void bindResource(Object key, Object value) {
        Map<Object, Object> map = resources.get();
        if (map == null) {
            map = new HashMap<>();
            resources.set(map);
        }
        // key = DataSource, value = ConnectionHolder
        map.put(key, value);  // 同一个线程的后续操作复用同一个 Connection
    }

    // 获取当前线程的资源
    public static Object getResource(Object key) {
        Map<Object, Object> map = resources.get();
        if (map == null) return null;
        return map.get(key);
    }

    // 当前是否在事务中
    public static boolean isActualTransactionActive() {
        return (actualTransactionActive.get() != null);
    }

    // 当前事务是否为只读
    public static boolean isCurrentTransactionReadOnly() {
        return (currentTransactionReadOnly.get() != null);
    }

    // 注册同步回调
    public static void registerSynchronization(TransactionSynchronization synchronization) {
        Set<TransactionSynchronization> synchs = synchronizations.get();
        if (synchs == null) {
            synchs = new LinkedHashSet<>();
            synchronizations.set(synchs);
        }
        synchs.add(synchronization);
        // 回调在事务提交/回滚时触发
    }

    // 清理当前线程的所有事务上下文
    public static void clear() {
        synchronizations.remove();
        currentTransactionName.remove();
        currentTransactionReadOnly.remove();
        currentTransactionIsolationLevel.remove();
        actualTransactionActive.remove();
    }
}
```

## 11.3 物理事务 vs 逻辑事务

```java
// AbstractPlatformTransactionManager — 物理/逻辑事务的核心管理

public abstract class AbstractPlatformTransactionManager
        implements PlatformTransactionManager, Serializable {

    @Override
    public final TransactionStatus getTransaction(
            @Nullable TransactionDefinition definition) throws TransactionException {

        // ⭐ 尝试获取已有事务（检查当前线程是否已绑定连接）
        Object transaction = doGetTransaction();

        boolean newSuspension = false;

        if (definition == null) {
            definition = TransactionDefinition.withDefaults();
        }

        String name = definition.getName();

        // ⭐ 检查当前线程是否已经存在一个事务
        if (isExistingTransaction(transaction)) {
            // 已有事务 → 根据传播行为处理
            return handleExistingTransaction(definition, transaction, debugEnabled);
        }

        // ⭐ 没有已有事务 → 根据传播行为决定是否新建
        switch (definition.getPropagationBehavior()) {
            case TransactionDefinition.PROPAGATION_REQUIRED:
            case TransactionDefinition.PROPAGATION_REQUIRES_NEW:
            case TransactionDefinition.PROPAGATION_NESTED:
                // ⭐ 新建物理事务
                // doBegin() → setAutoCommit(false)
                doBegin(transaction, definition);
                newSuspension = false;
                break;
            default:
                // SUPPORTS / NOT_SUPPORTED / NEVER → 无事务
                break;
        }

        // 返回事务状态
        return newTransactionStatus(
            definition, transaction, true,  // newTransaction=true → 新事务
            newSynchronization,             // 是否注册同步
            debugEnabled, suspendedResources
        );
    }

    // ⭐ 处理已有事务的关键逻辑
    private TransactionStatus handleExistingTransaction(
            TransactionDefinition definition, Object transaction,
            boolean debugEnabled) throws TransactionException {

        // 根据传播行为处理
        switch (definition.getPropagationBehavior()) {
            case TransactionDefinition.PROPAGATION_NEVER:
                // ⭐ 已有事务 + Propagation.NEVER → 抛异常
                throw new IllegalTransactionStateException(
                    "Existing transaction found for transaction marked with propagation 'never'");

            case TransactionDefinition.PROPAGATION_NOT_SUPPORTED:
                // ⭐ 挂起当前事务
                Object suspendedResources = suspend(transaction);
                // 无事务执行...

            case TransactionDefinition.PROPAGATION_REQUIRES_NEW:
                // ⭐ 挂起当前事务，新建一个物理事务
                Object suspendedResources = suspend(transaction);
                doBegin(transaction, definition);
                // 两个物理事务！

            case TransactionDefinition.PROPAGATION_NESTED:
                // ⭐ 嵌套事务：使用 Savepoint
                if (useSavepointForNestedTransaction()) {
                    // 创建 Savepoint
                    DefaultTransactionStatus status =
                        (DefaultTransactionStatus) getTransaction(definition);
                    status.createAndHoldSavepoint();
                } else {
                    // 不支持 Savepoint 的数据库 → 新建物理事务
                    doBegin(transaction, definition);
                }

            case TransactionDefinition.PROPAGATION_REQUIRED:
            case TransactionDefinition.PROPAGATION_SUPPORTS:
            case TransactionDefinition.PROPAGATION_MANDATORY:
                // ⭐ 加入已有事务（逻辑事务嵌套，物理事务相同）
                // 不调用 doBegin，复用已有连接
                return newTransactionStatus(
                    definition, transaction, false,  // newTransaction=false
                    // ...
                );
        }
    }
}
```

**图解：REQUIRED + REQUIRED 的物理/逻辑关系**：

```
物理事务 T1（单次 setAutoCommit(false)、commit()）
│
├─ 逻辑事务 A（UserService.createUser()）
│  ├─ userDao.save(user)         ← JDBC 连接复用
│  └─ auditDao.log("CREATE")     ← 同一连接
│
└─ 逻辑事务 B（AuditService.log()）— 加入逻辑事务 A
   └─ auditDao.insert(...)
```

**图解：REQUIRED + REQUIRES_NEW 的物理/逻辑关系**：

```
物理事务 T1              物理事务 T2
│                       │
├─ 逻辑事务 A            ├─ 逻辑事务 B
│  (挂起)                │  (新)
│  userDao.save()        │  auditDao.insert()
│                       │  commit T2 → 释放连接2
│       恢复 T1 ←────────┘
│  commit/rollback T1
│

连接1：T1 整个期间持有
连接2：T2 期间持有
```

## 11.4 完整的请求处理时序图

```
Client                  DispatcherServlet         TransactionInterceptor          Service              Database
  │                           │                          │                         │                     │
  │  HTTP POST /api/users     │                          │                         │                     │
  │──────────────────────────►│                          │                         │                     │
  │                           │  findHandler + 调用      │                         │                     │
  │                           │─────────────────────────►│                         │                     │
  │                           │                          │                         │                     │
  │                           │    getTransaction()      │                         │                     │
  │                           │────────────────────────────────────────────────────────────────────►│
  │                           │                          │                         │                 getConnection()
  │                           │                          │                         │◄────────────────────│
  │                           │                          │                         │                     │
  │                           │    doBegin()             │                         │                     │
  │                           │────────────────────────────────────────────────────────────────────►│
  │                           │                          │                         │              setAutoCommit(false)
  │                           │                          │                         │                     │
  │                           │    invocation.proceed()  │                         │                     │
  │                           │─────────────────────────►│─────────────────────────►│                     │
  │                           │                          │                         │                     │
  │                           │                          │                    service.save(user)         │
  │                           │                          │                         │────────────────────►│
  │                           │                          │                         │                    INSERT
  │                           │                          │                         │◄────────────────────│
  │                           │                          │                         │                     │
  │                           │                          │                    service.sendEmail()        │
  │                           │                          │                         │────────────────────►│
  │                           │                          │                         │                    INSERT INTO emails
  │                           │                          │                         │◄────────────────────│
  │                           │                          │                         │                     │
  │                           │                          │   ← 正常返回             │                     │
  │                           │    commit()              │                         │                     │
  │                           │────────────────────────────────────────────────────────────────────►│
  │                           │                          │                         │              commit()
  │                           │                          │                         │                     │
  │                           │                          │                         │                     │
  │                           │  HTTP 201 Created        │                         │                     │
  │◄──────────────────────────│                          │                         │                     │
  │                           │                          │                         │                     │

  // 异常路径：
  │                           │                          │                         │                     │
  │                           │                    ← Exception                     │                     │
  │                           │    rollback()            │                         │                     │
  │                           │────────────────────────────────────────────────────────────────────►│
  │                           │                          │                         │            rollback()
```

---

> **扩展阅读**：
> - [官方文档：Using @Transactional](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)
> - [官方文档：Transaction Management](https://docs.spring.io/spring-framework/reference/data-access/transaction.html)
> - [Vlad Mihalcea — Spring read-only transaction Hibernate optimization](https://vladmihalcea.com/spring-read-only-transaction-hibernate-optimization/)
> - [Vlad Mihalcea — The best way to use @Transactional](https://vladmihalcea.com/spring-transactional-annotation/)
> - [Marcobehler — Spring Transaction Management In-Depth](https://www.marcobehler.com/guides/spring-transaction-management-transactional-in-depth)
> - [Medium — Spring @Transactional mistakes everyone did](https://medium.com/javarevisited/spring-transactional-mistakes-everyone-did-31418e5a6d6b)
