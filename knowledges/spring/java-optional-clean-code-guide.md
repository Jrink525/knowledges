---
title: "Java Optional 清洁代码指南：示例、最佳实践与练习"
tags:
  - java
  - optional
  - null-safety
  - best-practices
  - clean-code
date: 2026-05-23
source: "https://blog.devgenius.io/cleaner-code-with-java-optional-examples-best-practices-and-exercises-005f2a9a6a7d"
authors: "Ani Talakhadze"
---

# Java Optional 清洁代码指南：示例、最佳实践与练习

> **原文：** [Cleaner Code with Java Optional: Examples, Best Practices and Exercises](https://blog.devgenius.io/cleaner-code-with-java-optional-examples-best-practices-and-exercises-005f2a9a6a7d) by Ani Talakhadze / Dev Genius
> **中文整理：** 翻译 + 扩展 + 整合

---

## 为什么需要 Optional？

你在调试时多少次遇到来历不明的 `NullPointerException`？多少次看到 `if (x == null && y != null && z == null ...)` 这样的冗长空判断？

Java 的 `Optional<T>` 类通过将值的存在/缺失显式化，让 API 更清晰，减少运行时意外，提高可维护性。

---

## 七种实战重构模式

### 🟢 模式一：条件语句中的空判断

```java
// ❌ 传统做法
public int getDiscount(Customer customer) {
    if (customer != null && customer.discount() != null) {
        return customer.discount();
    }
    return 0;
}

// ✅ 使用 Optional
public int getDiscount(Customer customer) {
    return Optional.ofNullable(customer)
        .map(Customer::discount)
        .orElse(0);
}
```

**关键点：** `Optional.ofNullable()` 安全处理可能为 null 的值，`orElse(0)` 提供默认值。

---

### 🟢 模式二：方法返回 null

```java
// ❌ 返回 null —— 调用方必须自己判空
public Address getAddress(User user) {
    if (user != null && user.address() != null) {
        return user.address();
    }
    return null;
}

// ✅ 返回 Optional<Address> —— 签名诚实告知可能为空
public Optional<Address> getAddress(User user) {
    return Optional.ofNullable(user)
        .map(User::address);
}
```

**关键点：** `Optional<Address>` 作为返回类型，迫使调用方显式处理缺失情况。

---

### 🟢 模式三：链式调用

```java
// ❌ 嵌套空判断金字塔
public String getCountryName(User user) {
    if (user != null && user.address() != null
        && user.address().country() != null) {
        return user.address().country().name();
    }
    return "Unknown";
}

// ✅ 扁平链式调用
public String getCountryName(User user) {
    return Optional.ofNullable(user)
        .map(User::address)
        .map(Address::country)
        .map(Country::name)
        .orElse("Unknown");
}
```

---

### 🟢 模式四：用 Optional 抛异常

```java
// ❌ 手写 if-null 抛异常
public User findUserById(Long id) {
    User user = userRepository.findById(id);
    if (user == null) {
        throw new RuntimeException("User not found for id: " + id);
    }
    return user;
}

// ✅ 用 orElseThrow
public User findUserById(Long id) {
    return Optional.ofNullable(userRepository.findById(id))
        .orElseThrow(() -> new RuntimeException("User not found for id: " + id));
}
```

---

### 🟢 模式五：用空 Optional 表达明确意图

```java
// ❌ 返回 null —— 调用方 get() 会 NPE
public Optional<Product> findProductByName(String name) {
    Product product = productRepository.findByName(name);
    if (product == null) {
        return null; // 危险！调用方调用 .get() 会崩
    }
    return Optional.of(product);
}

// ✅ 明确返回 Optional.empty()
public Optional<Product> findProductByName(String name) {
    return Optional.ofNullable(productRepository.findByName(name))
        .or(Optional::empty);
}
```

> **关键原则：** 如果方法返回 `Optional<T>`，永远不要返回 `null`。返回 `Optional.empty()`。

---

### 🟢 模式六：用 `filter()` 做条件逻辑

```java
// ❌ 手写 null + 条件判断
public Optional<User> getActiveUser(User user) {
    if (user != null && user.isActive()) {
        return Optional.of(user);
    }
    return Optional.empty();
}

// ✅ 用 filter —— 意图一目了然
public Optional<User> getActiveUser(User user) {
    return Optional.ofNullable(user)
        .filter(User::isActive);
}
```

---

### 🟢 模式七：按条件执行操作

```java
// ❌ if-null 检查
public void notifyUser(User user) {
    if (user != null) {
        sendNotification(user);
    }
}

// ✅ ifPresent
public void notifyUser(User user) {
    Optional.ofNullable(user)
        .ifPresent(this::sendNotification);
}
```

```java
// ❌ if-else 两种分支
public void processOrder(Long orderId) {
    Optional<Order> orderOpt = orderRepository.findLatestByCustomerId(orderId);
    if (orderOpt.isPresent()) {
        handleOrder(orderOpt.get());
    } else {
        handleMissingOrder();
    }
}

// ✅ ifPresentOrElse (Java 9+)
public void processOrder(Long orderId) {
    orderRepository.findLatestByCustomerId(orderId)
        .ifPresentOrElse(this::handleOrder, this::handleMissingOrder);
}
```

---

## 🟡 最佳实践（Do's and Don'ts）

### ❌ 不要在字段中使用 Optional

```java
// ❌ 错误：Optional 做字段 —— 破坏序列化/JPA
public class User {
    private Optional<String> email;

    public User(Optional<String> email) {
        this.email = email;
    }
}

// ✅ 正确：直接存字段
public class User {
    private String email;

    public User(String email) {
        this.email = email;
    }
}
```

**原因：** Optional 设计为返回类型，不是字段类型。用作字段会破坏 Jackson 序列化、JPA 映射和 `equals/hashCode`。

---

### ❌ 不要在集合中使用 Optional

```java
// ❌ 错误：List<Optional<User>>
List<Optional<User>> users = ...;
List<User> validUsers = users.stream()
    .filter(Optional::isPresent)
    .map(Optional::get)
    .collect(Collectors.toList()); // 冗余且低效

// ✅ 正确：直接过滤 null
List<User> validUsers = userIds.stream()
    .map(userService::findById)
    .filter(Objects::nonNull)
    .collect(Collectors.toList());
```

**原因：** Optional 表示单个可能缺失的值。在集合里用 `Optional` 增加不必要的复杂度，每个 Optional 创建还有性能开销。

---

### 🟢 明智选择 `orElse` 和 `orElseGet`

```java
// 昂贵计算
private String generateDefaultUsername() {
    TimeUnit.SECONDS.sleep(1); // 模拟耗时操作
    return "GuestUser";
}

// ❌ orElse —— 无论 Optional 是否有值，都计算默认值
public String getUsername(String userId) {
    Optional<String> username = findUsername(userId);
    // 即使 username 存在，也执行了生成逻辑
    return username.orElse(generateDefaultUsername());
}

// ✅ orElseGet —— 惰性求值，仅在 Optional 为空时执行
public String getUsername(String userId) {
    Optional<String> username = findUsername(userId);
    return username.orElseGet(this::generateDefaultUsername);
}
```

**规则：** 默认值计算昂贵时 → 用 `orElseGet()`；简单常量 → 用 `orElse()`。

---

### ❌ 不过度使用 Optional

```java
// ❌ 过度包装 —— 没必要的 Optional
public Optional<Integer> getProductCount() {
    return Optional.of(100); // 永远有值，何必用 Optional
}

// ✅ 简单明确
public int getDefaultDiscount() {
    return 10;
}
```

**原则：** 方法预期一定返回值的，不要用 Optional 包装。Optional 仅用于**可能缺失**的场景。

---

## 对比：与先前文章的关系

这篇文章的 7 个模式 + 4 条最佳实践覆盖了：

| 模式 | 这篇 | 之前 WeChat 文章 |
|------|------|-----------------|
| map() 链式判空 | ✅ | ✅ |
| Optional 作为返回值 | ✅ | ✅ |
| orElseThrow | ✅ | ✅ |
| flatMap 处理嵌套 Optional | ✗ | ✅ |
| Optional 不用于参数/字段 | ✅ | ✅ |
| filter() 条件筛选 | ✅ | ✗ |
| ifPresent / ifPresentOrElse | ✅ | ✗ |
| 集合中不用 Optional | ✅ | ✗ |
| orElse vs orElseGet | ✅ | ✗ |
| 不过度使用 Optional | ✅ | ✗ |

**建议两篇都看：** WeChat 那篇有 `flatMap` 的精讲（处理 `Optional<Optional<T>>` 反模式），这篇有 `filter`、`ifPresentOrElse`、`orElseGet` 等更多实用模式。

---

## 练习

原文作者提供了包含练习题的 GitHub 仓库：
[https://github.com/anitalakhadze/refactor-using-optional](https://github.com/anitalakhadze/refactor-using-optional)

---

*Processed on 2026-05-23 from Dev Genius (Medium)*
