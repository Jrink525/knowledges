---
title: "Spring Boot 运行时根据动态参数创建 Bean 高阶实现"
tags:
  - spring-boot
  - spring
  - bean
  - prototype
  - dependency-injection
date: 2026-05-31
source:
  - "https://mp.weixin.qq.com/s/1-pZ9QzhrFpM6FiuwsJxxw"
  - "https://www.baeldung.com/spring-prototype-bean-runtime-arguments"
  - "https://medium.com/@AlexanderObregon/dynamic-bean-registration-in-spring-boot-at-runtime-011503fef3db"
authors: "Spring Boot 实战案例锦集 / Baeldung / Alexander Obregon"
---

# Spring Boot 运行时根据动态参数创建 Bean 高阶实现

> Spring 中 Bean 默认作用域为单例（singleton），容器中只会有这一个实例。如果需要每次返回新实例，使用原型作用域（prototype）。
> 但在实践中，**从单例 bean 实例化原型 bean，或向原型 bean 传递动态参数**，往往会出现问题。
> 本文深入 6 种实现方式 + 注册机制，涵盖实战和原理层面。

---

## 一、预备：创建带参数的原型 Bean

```java
public class Employee {
    private String name;

    public Employee(String name) {
        this.name = name;
    }

    public void printName() {
        System.out.println(this.name);
    }
}
```

配置原型 bean（Spring Boot 3.5.0+）：

```java
@Configuration
public class AppConfig {
    @Bean
    @Scope(BeanDefinition.SCOPE_PROTOTYPE)
    public Employee employee(String name) {
        return new Employee(name);
    }
}
```

---

## 二、5 种运行时获取带参数原型 Bean 的方式

### 方式 1：ApplicationContext.getBean() — 最基础

直接注入 `ApplicationContext`，通过重载的 `getBean(String name, Object... args)` 传入构造参数。

```java
@Component
public class UseEmployeePrototype implements ApplicationContextAware {
    private ApplicationContext context;

    public void usePrototype() {
        Employee employee = (Employee) context.getBean("employee", "pack_xg");
        employee.printName();
    }

    @Override
    public void setApplicationContext(ApplicationContext context) {
        this.context = context;
    }
}
```

**优点：** 简单直接，无需额外配置  
**缺点：** 与 `ApplicationContext` 紧耦合，Bean 实现变更时影响较大

---

### 方式 2：使用 @Lookup 注解

`@Lookup` 注解的方法会被 Spring CGLIB 覆盖，容器将返回方法对应的命名 Bean。**类和方法不能是 final 的。**

```java
@Component
public class EmployeeLookup {
    @Lookup
    public Employee getEmployee(String arg) {
        return null;  // Spring 会通过 CGLIB 生成字节码覆盖此方法
    }
}
```

测试：

```java
@Component
public class PrototypeRunner implements CommandLineRunner {
    private final EmployeeLookup el;

    public PrototypeRunner(EmployeeLookup el) {
        this.el = el;
    }

    @Override
    public void run(String... args) {
        Employee e1 = el.getEmployee("pack");
        Employee e2 = el.getEmployee("xg");
        System.err.println(e1);
        System.err.println(e2);
        // 输出不同实例：com.pack.Employee@526e8108 / com.pack.Employee@4dcbae55
    }
}
```

**优点：** 无耦合，类型安全，Spring 官方推荐方式之一  
**缺点：** 依赖 CGLIB 代理，不能用于 final 方法/类

---

### 方式 3：使用 ObjectFactory<T>

Spring 提供了 `ObjectFactory<T>` 接口来按需生成对象。每次调用 `getObject()` 返回新实例。

```java
public class EmployeeBeanUsingObjectFactory {
    @Autowired
    private ObjectFactory<Employee> employeeObjectFactory;

    public Employee getEmployee() {
        return employeeObjectFactory.getObject();
    }
}
```

> ⚠️ **注意：** 基本 `ObjectFactory` 的 `getObject()` **不带参数**。如果需要传参，用下面的 ObjectProvider 或 Function。

---

### 方式 4：使用 Function<T, R>

通过 `java.util.function.Function` 作为工厂方法，在运行时传参创建原型 bean。

**组件类：**

```java
@Component
public class EmployeeFunction {
    private final Function<String, Employee> employeeFactory;

    public EmployeeFunction(Function<String, Employee> employeeFactory) {
        this.employeeFactory = employeeFactory;
    }

    public Employee getEmployee(String name) {
        return this.employeeFactory.apply(name);
    }
}
```

**配置类中添加 Function Bean：**

```java
@Configuration
public class AppConfig {
    @Bean
    @Scope(BeanDefinition.SCOPE_PROTOTYPE)
    Employee employee(String name) {
        return new Employee(name);
    }

    @Bean
    Function<String, Employee> ef() {
        return name -> employee(name);
    }
}
```

**优点：** 函数式风格，编译期类型安全  
**缺点：** 需要额外配置 Function Bean，相对隐式

---

### 方式 5：使用 ObjectProvider<T>

`ObjectProvider<T>` 是 `ObjectFactory` 的扩展，提供了 `getObject(Object... args)` 重载，支持传入参数。

```java
@Component
public class EmployeeObjectProvider {
    private final ObjectProvider<Employee> objectProvider;

    public EmployeeObjectProvider(ObjectProvider<Employee> objectProvider) {
        this.objectProvider = objectProvider;
    }

    public Employee getEmployee(String name) {
        return objectProvider.getObject(name);
    }
}
```

测试：

```java
@Component
public class PrototypeRunner implements CommandLineRunner {
    private final EmployeeObjectProvider employeeProvider;

    public void run(String... args) {
        Employee e1 = employeeProvider.getEmployee("pack");
        Employee e2 = employeeProvider.getEmployee("xg");
        // e1 != e2，每次都是新实例
    }
}
```

**优点：** 带参数创建、类型安全、Spring 原生支持  
**缺点：** 仅适用于 prototype scope bean

---

## 三、补充：动态 Bean 注册（更底层的方式）

除了上述给已有 prototype bean 传参的方式，有时需要在**运行时从零注册全新的 Bean 定义**。这通过 `BeanDefinitionRegistry` 实现。

### 3.1 通过 BeanDefinitionRegistry 编程注册

```java
@Component
public class RuntimeBeanRegistrar {
    private final ConfigurableApplicationContext context;

    public RuntimeBeanRegistrar(ConfigurableApplicationContext context) {
        this.context = context;
    }

    public void registerRuntimeBean() {
        BeanDefinitionRegistry registry = (BeanDefinitionRegistry) context.getBeanFactory();

        GenericBeanDefinition def = new GenericBeanDefinition();
        def.setBeanClass(RuntimeLogger.class);
        def.setScope(BeanDefinition.SCOPE_SINGLETON);
        registry.registerBeanDefinition("runtimeLogger", def);
    }
}
```

### 3.2 使用 BeanDefinitionBuilder（更简洁）

```java
BeanDefinitionBuilder builder = BeanDefinitionBuilder
    .genericBeanDefinition(OrderService.class)
    .addPropertyValue("region", "US-East")
    .setScope(BeanDefinition.SCOPE_SINGLETON);
registry.registerBeanDefinition("orderService", builder.getBeanDefinition());
```

**循环注册多实例：**

```java
String[] regions = {"US-East", "EU-West", "AP-South"};
for (String region : regions) {
    BeanDefinitionBuilder b = BeanDefinitionBuilder
        .genericBeanDefinition(OrderService.class)
        .addPropertyValue("region", region);
    registry.registerBeanDefinition("orderService_" + region, b.getBeanDefinition());
}
```

### 3.3 提前注册：BeanFactoryPostProcessor

如果需要在 Bean 创建**之前**注册，使用 `BeanFactoryPostProcessor`，你的 bean 会被视为配置的一部分：

```java
@Component
public class EarlyBeanRegistrar implements BeanFactoryPostProcessor {
    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory factory) {
        GenericBeanDefinition def = new GenericBeanDefinition();
        def.setBeanClass(StartupService.class);
        ((BeanDefinitionRegistry) factory).registerBeanDefinition("startupService", def);
    }
}
```

### 3.4 注册单例实例（已有对象）

已经构造好的对象，可以直接注册为 Spring 管理的单例：

```java
ExternalService ext = new ExternalService("Config A");
context.getBeanFactory().registerSingleton("externalService", ext);
```

适用于：**第三方集成、插件系统、多租户动态数据源**

### 3.5 ⚠️ 刷新问题

容器 refresh 后注册的 bean：
- ✅ 可通过 `context.getBean()` 直接获取
- ❌ **不会自动注入到已有 bean 中**（已有 bean 已装配完毕）
- 如需完整 DI，需在 `BeanFactoryPostProcessor` 阶段注册

---

## 四、实战场景

### 场景 1：多租户动态数据源

```java
public void registerTenantDatasource(String tenantId, DataSource ds) {
    ConfigurableListableBeanFactory factory = context.getBeanFactory();
    factory.registerSingleton("datasource_" + tenantId, ds);
}
// 租户登录时注册 → 可注入到服务中
```

### 场景 2：插件系统 / 服务发现

运行时扫描 classpath 或 SPI，将发现的实现类注册为 bean。

### 场景 3：特性开关（Feature Toggle）

配置中心下发新开关后，动态注册特性所需的 service bean，无需重启。

---

## 五、方法对比总结

| 方式 | 传参支持 | 耦合度 | 类型安全 | 复杂度 | 推荐场景 |
|------|---------|--------|---------|--------|---------|
| `ApplicationContext.getBean()` | ✅ | ❌ 高 | ❌ | ⭐ | 快速原型 |
| `@Lookup` | ✅ | ✅ 低 | ✅ | ⭐⭐ | 日常推荐 |
| `ObjectFactory<T>` | ❌ | ✅ | ✅ | ⭐ | 无参场景 |
| `Function<T,R>` | ✅ | ✅ | ✅ | ⭐⭐ | 函数式风格 |
| `ObjectProvider<T>` | ✅ | ✅ | ✅ | ⭐ | **最推荐** |
| `BeanDefinitionRegistry` | ✅（定义级） | ✅ | ✅ | ⭐⭐⭐ | 动态注册新 bean |

### 个人推荐优先级

1. **首选 `ObjectProvider<T>`** — 原生支持、传参方便、类型安全、最少的模板代码
2. **备选 `@Lookup`** — 也对，但需要 CGLIB，final 约束需要注意
3. **`Function<T,R>`** — 函数式偏好时使用
4. **`BeanDefinitionRegistry`** — 当需要在运行时动态**创建新的 Bean 定义**（而非只是传参）时使用

---

## 六、参考来源

1. [Spring Boot 实战案例锦集 — 运行时根据动态参数创建 Bean](https://mp.weixin.qq.com/s/1-pZ9QzhrFpM6FiuwsJxxw)
2. [Baeldung — Create Spring Prototype Scope Bean with Runtime Arguments](https://www.baeldung.com/spring-prototype-bean-runtime-arguments)
3. [Medium / Alexander Obregon — Dynamic Bean Registration in Spring Boot at Runtime](https://medium.com/@AlexanderObregon/dynamic-bean-registration-in-spring-boot-at-runtime-011503fef3db)
4. [Spring Framework — BeanDefinitionRegistry Docs](https://docs.spring.io/spring-framework/reference/core/beans/definition.html)
5. [Spring Framework — ObjectProvider Javadoc](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/beans/factory/ObjectProvider.html)

---

*整理于 2026-05-31，综合 WeChat、Baeldung 和 Medium 三篇同主题文章补充增强*
