---
title: "方法别再返回 null 了！Optional 的 4 种高级模式"
tags:
  - java
  - optional
  - null-safety
  - best-practices
  - spring-boot
date: 2026-05-23
source: "https://mp.weixin.qq.com/s/7U1zg2fMuaYzwDnLg_iJiw"
authors: "Spring Boot 实战案例锦集"
category: spring-boot
---

# 方法别再返回 null 了！Optional 的 4 种高级模式

> **来源：** 微信公众号「Spring Boot 实战案例锦集」
> **环境：** Spring Boot 3.5.0

---

## 概述

在 Java 业务开发中，查询方法直接返回 `null` 是引发空指针异常（NPE）的核心隐患，调用方易遗漏非空校验，导致程序崩溃；嵌套对象空判断还会形成冗余的「防御式判断金字塔」，降低可读性。同时错误使用 `Optional`（如作为参数、类字段）会破坏框架兼容性、让 API 设计混乱。

**本文的 4 种模式：** 统一用 `Optional` 作为查询返回值，结合链式调用、`flatMap` 优化代码，且仅将 `Optional` 用于返回类型，让空值处理更安全、代码更简洁规范。

---

## 模式一：Optional 替代 null 作为查询返回值

### ❌ 错误做法

```java
// 调用方完全不知道该方法可能返回 null
public User findByEmail(String email) {
    return userRepository.findByEmail(email); // 可能返回 null
}

// 调用方忘记做非空校验 —— 导致生产环境程序崩溃
User user = userService.findByEmail("packxg@gmail.com");
sendWelcomeEmail(user.getEmail()); // 空指针异常！
```

### ✅ 正确做法

```java
// 方法签名明确告知：返回值可能为空
public Optional<User> findByEmail(String email) {
    return userRepository.findByEmail(email); // 返回 Optional 类型
}

// 调用方必须处理「存在/不存在」两种情况
public void sendWelcomeEmailIfExists(String email) {
    // 方案 A：ifPresent —— 仅当值存在时执行操作
    userService.findByEmail(email)
        .ifPresent(user -> emailService.sendWelcome(user.getEmail()));

    // 方案 B：orElseThrow —— 无值时抛出清晰明确的异常
    User user = userService.findByEmail(email)
        .orElseThrow(() -> new UserNotFoundException(
            "未找到该邮箱对应的用户：%s".formatted(email)));

    // 方案 C：orElse —— 无值时提供合理的默认值
    User user = userService.findByEmail(email)
        .orElse(User.anonymous());
}
```

### 要点

- 方法签名**诚实清晰** —— 调用方明确知道可能查询不到结果
- `orElseThrow` 用**有意义的异常**替代静默空指针崩溃
- 强制所有调用方**主动决策**如何处理结果缺失的情况
- Spring Data 已原生返回 `Optional` —— 避免用 `orElse(null)` 把它拆包回 null

---

## 模式二：Optional 链式调用 —— 简化嵌套对象空值判断

### ❌ 防御式空判断金字塔

```java
public String getCustomerCity(Long orderId) {
    Order order = orderRepository.findById(orderId);
    if (order != null) {
        Customer customer = order.getCustomer();
        if (customer != null) {
            Address address = customer.getAddress();
            if (address != null) {
                return address.getCity();
            }
        }
    }
    return "Unknown";
}
```

### ✅ 扁平化链式调用

```java
public String getCustomerCity(Long orderId) {
    return orderRepository.findById(orderId)    // Optional<Order>
        .map(Order::getCustomer)                // Optional<Customer>
        .map(Customer::getAddress)              // Optional<Address>
        .map(Address::getCity)                  // Optional<String>
        .orElse("Unknown");                      // 任意一步为空则返回默认值
}
```

### 深度嵌套配置项示例

```java
public int getTimeoutMillis() {
    return Optional.ofNullable(appConfig)
        .map(AppConfig::getHttp)
        .map(HttpConfig::getTimeout)
        .map(TimeoutConfig::getMillis)
        .orElse(3000); // 合理的默认值
}
```

### 要点

- **消除了空判断金字塔** —— 代码逻辑从上到下流畅可读
- 任意一步为空时，每个 `map()` 都会**自动短路**（不再执行后续操作）
- 默认值**显式可见**，不会隐藏在 else 分支中
- 与方法引用完美配合，代码简洁、表意清晰

---

## 模式三：使用 flatMap 处理返回 Optional 的方法

### ❌ 错误做法 —— 产生嵌套的 Optional

```java
// map() 会包裹内部的 Optional — 产生嵌套的 Optional<Optional<Address>>
public Optional<String> getPrimaryCity(Long userId) {
    return userRepository.findById(userId)
        .map(user -> user.getPrimaryAddress()); // 结果：Optional<Optional<Address>>
}

// 被迫用笨拙的方式拆包
Optional<Optional<Address>> nested = userRepository.findById(userId)
    .map(User::getPrimaryAddress);
String city = nested.isPresent() && nested.get().isPresent()
    ? nested.get().get().getCity()
    : "Unknown";
// 又退回到了空判断的麻烦境地
```

### ✅ 正确做法

```java
// flatMap 将 Optional<Optional<T>> 展平为 Optional<T>
public Optional<String> getPrimaryCity(Long userId) {
    return userRepository.findById(userId)      // Optional<User>
        .flatMap(User::getPrimaryAddress)        // Optional<Address>
        .map(Address::getCity);                  // Optional<String>
}

// 真实业务示例：为订单计算折扣
public Optional<BigDecimal> resolveDiscount(Long orderId) {
    return orderRepository.findById(orderId)     // Optional<Order>
        .flatMap(Order::getPromoCode)            // Optional<PromoCode>
        .flatMap(promoCodeService::findDiscount); // Optional<BigDecimal>
}

// 调用方可以简洁地处理最终的 Optional
BigDecimal discount = resolveDiscount(orderId).orElse(BigDecimal.ZERO);
```

### 要点

- **避免双层 Optional 反模式**，这种写法会让所有代码审核者困惑
- **经验法则：** 处理普通值用 `map()`，处理返回 `Optional` 的方法用 `flatMap()`
- 无论链式调用包含多少个返回 `Optional` 的步骤，代码始终保持**扁平化、可读性强**
- 体现了对函数式组合的理解 —— 这是**资深 Java 代码的标志性特征**

---

## 模式四：Optional 仅用于服务层 —— 不要用于方法参数或类字段

### ❌ 错误用法

```java
// 将 Optional 用作方法参数 — 绝对禁止
public void updateUser(Long id, Optional<String> name, Optional<String> email) {
    // 调用方必须手动包装值：updateUser(1L, Optional.of("John"), Optional.empty())
    // 这种写法比直接传 null 更糟糕
}

// 将 Optional 用作类字段 — 会导致序列化、Hibernate 异常
public class User {
    private Optional<String> middleName; // 破坏 Jackson、JPA 框架
}

// 不做检查直接调用 .get() — 比空判断更糟糕
Optional<User> user = userRepository.findById(id);
String email = user.get().getEmail(); // Optional 为空时抛出 NoSuchElementException！
```

### ✅ 正确做法

```java
@Service
public class UserService {
    // ✅ 值可能不存在时，返回 Optional 类型
    public Optional<User> findById(Long id) {
        return userRepository.findById(id);
    }

    // ✅ 可选参数使用 @Nullable — 而非 Optional
    public void updateUser(Long id, @Nullable String name, @Nullable String email) {
        User user = userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));
        if (name != null) user.setName(name);
        if (email != null) user.setEmail(email);
        userRepository.save(user);
    }

    // ✅ 使用 ifPresentOrElse 处理分支逻辑 — Java 9+
    public UserResponse resolveUserResponse(Long id) {
        return userRepository.findById(id)
            .map(user -> UserResponse.found(user))
            .orElseGet(() -> UserResponse.notFound(id));
    }
}

// ✅ 类字段使用 @Nullable 注解，而非 Optional
public class User {
    @Nullable
    private String middleName; // 简洁、可序列化、兼容 JPA
}
```

### 要点

- `Optional` 作为类字段会破坏 **Jackson 序列化、JPA 映射以及 equals/hashCode** 方法
- `Optional` 类型参数会让调用方代码变得丑陋 —— `@Nullable` 更简洁、更符合 Java 惯用写法
- 绝不直接调用 `.get()` —— 这是规范、成熟的 `Optional` 使用习惯
- **仅将 `Optional` 用于返回类型**，API 设计意图极其清晰明确

---

## 总结 — 四条铁律

| # | 规则 | 简记 |
|---|------|------|
| 1 | 查询方法返回 `Optional<T>` 而非 `T` | 签名诚实，调用方必须决策 |
| 2 | 用 `map()` 链式调用替代嵌套 if-null | 扁平化代码，天然短路 |
| 3 | 当嵌套方法也返回 `Optional` 时用 `flatMap()` | 避免 `Optional<Optional<T>>` |
| 4 | `Optional` 仅作为返回类型，不用于参数或字段 | 用 `@Nullable` 替代 |

---

*Processed on 2026-05-23 from 微信公众号「Spring Boot 实战案例锦集」*
