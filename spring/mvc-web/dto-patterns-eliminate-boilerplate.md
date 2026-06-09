---
title: "告别冗余 DTO：从入门到精通，6 种 Spring Boot 高效模式彻底取代样板代码"
date: 2026-05-24
tags: [spring-boot, dto, mapstruct, java-records, projections, jsonview, jackson]
category: spring
source: "综合整理自公众号《Spring Boot实战案例锦集》及 Medium 多篇高赞文章"
---

# 告别冗余 DTO：从入门到精通，6 种 Spring Boot 高效模式彻底取代样板代码

> **综合整理自：**
> - 公众号《Spring Boot实战案例锦集》—《告别冗余 DTO：5 种 Spring Boot 高效模式彻底取代样板代码》
> - Ramesh Fadatare — *Stop Writing Boilerplate DTOs: Use Java Records Instead*
> - Ondrej Kvasnovsky — *How to avoid DTOs in Spring JPA*
> - Akash Padir — *Stop Writing Boilerplate Code — Use MapStruct Instead*
> - Alexander Obregon — *Using Java Records with Spring Boot DTOs*
> - Harjeet Kaur — *Avoiding DTOs in Spring JPA: Smarter Alternatives*
>
> **环境：** Spring Boot 3.5+，Java 17+

---

## 一、基础篇：DTO 是什么，为什么需要它

### 1.1 DTO 的基本概念

DTO（Data Transfer Object，数据传输对象）是一种设计模式，用于在应用程序的不同层之间传输数据。在 Spring Boot 项目中，DTO 主要用于：

- **隔离领域模型与 API 层** — 内部实体结构变化不影响外部接口契约
- **控制数据传输粒度** — 按需返回字段，避免过度暴露
- **提升安全性** — 隐藏敏感字段（密码、内部 ID 等）
- **解耦版本管理** — API 版本演进时，后端实体变更不影响客户端

### 1.2 手动 DTO 的痛点

大多数开发者最初的做法是这样的：

```java
// 实体
@Entity
public class User {
    private Long id;
    private String firstName;
    private String lastName;
    private String email;
    private String password;
    private LocalDateTime createdAt;
    // getters, setters...
}

// DTO
public class UserDTO {
    private Long id;
    private String firstName;
    private String lastName;
    private String email;
    // getters, setters...
}

// 手动映射
public class UserMapper {
    public UserDTO toDTO(User user) {
        UserDTO dto = new UserDTO();
        dto.setId(user.getId());
        dto.setFirstName(user.getFirstName());
        dto.setLastName(user.getLastName());
        dto.setEmail(user.getEmail());
        return dto;
    }

    public User toEntity(UserDTO dto) {
        User user = new User();
        user.setId(dto.getId());
        user.setFirstName(dto.getFirstName());
        user.setLastName(dto.getLastName());
        user.setEmail(dto.getEmail());
        return user;
    }
}
```

这段代码的问题非常明显：

| 问题 | 影响 |
|------|------|
| 每个字段手动映射 | 容易遗漏或写错字段 |
| 增删字段需改 3-4 处 | 维护成本高，违背 DRY 原则 |
| 无编译期类型安全 | 运行时才能发现映射错误 |
| 代码量膨胀 | 3 个实体 × 5 个 DTO = 30+ 映射方法 |
| 测试繁琐 | 每个映射方法都要写单元测试 |

> 3 个实体，每个 5 个 DTO，就是 15 个 DTO 类和 30 多个映射方法——欢迎来到样板代码地狱。— 公众号原文

---

## 二、入门篇：最简单有效的改进

### 2.1 模式一：Java 17+ Record 作为 DTO

**核心思想：** 用 Java 的 Record 类型替代传统 POJO 类，一行搞定 DTO 定义。

**传统 DTO（50+ 行）：**

```java
public class UserDTO {
    private Long id;
    private String firstName;
    private String lastName;
    private String email;

    public UserDTO() {}
    public UserDTO(Long id, String firstName, String lastName, String email) {
        this.id = id;
        this.firstName = firstName;
        this.lastName = lastName;
        this.email = email;
    }
    // 40+ 行 getter / setter / equals / hashCode / toString ...
}
```

**Record DTO（1 行核心定义）：**

```java
public record UserDTO(
    Long id,
    String firstName,
    String lastName,
    String email
) {}
```

#### Record 支持 Bean Validation

```java
public record CreateUserRequest(
    @NotBlank(message = "firstName 必须填写")
    String firstName,

    @NotBlank(message = "lastName 必须填写")
    String lastName,

    @Email(message = "必须是有效的邮箱")
    @NotBlank(message = "邮箱必须填写")
    String email,

    @Size(min = 8, message = "密码必须大于等于 8 位")
    String password
) {}

// 控制器直接使用
@PostMapping("/users")
public ResponseEntity<UserDTO> createUser(
        @Valid @RequestBody CreateUserRequest request) {
    User user = userService.create(request);
    return ResponseEntity.ok(userMapper.toDTO(user));
}
```

#### Record 的核心优势

| 特性 | 传统 DTO | Record DTO |
|------|---------|-----------|
| 代码行数 | 50+ | 5 |
| 可变性 | 可变（可修改） | 不可变（线程安全） |
| equals/hashCode | 需手动实现 | 基于字段自动生成 |
| toString | 需手动实现 | 自动生成 |
| 构造方法 | 需手动编写 | 全参构造自动生成 |
| 解构模式匹配 | 不支持 | Java 21+ 支持 |

> **注意：** Record 的不可变特性在某些场景（如 partial update、ORM 双向绑定）可能受限，需要配合 Builder 或其他模式使用。

---

### 2.2 模式二：@JsonNaming 与 @JsonProperty 控制 API 命名

**问题场景：** Java 代码使用驼峰命名（camelCase），但 API 要求蛇形命名（snake_case）。

**传统做法——每个字段加注解：**

```java
public class UserApiDTO {
    @JsonProperty("user_id")
    private Long userId;

    @JsonProperty("first_name")
    private String firstName;

    @JsonProperty("last_name")
    private String lastName;
}
```

**优化做法——全局命名策略：**

```java
@Configuration
public class JacksonConfig {
    @Bean
    public Jackson2ObjectMapperBuilder objectMapperBuilder() {
        return new Jackson2ObjectMapperBuilder()
            .propertyNamingStrategy(PropertyNamingStrategies.SNAKE_CASE);
    }
}
```

**或针对单个类配置：**

```java
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public record UserDTO(
    Long userId,
    String firstName,
    String lastName,
    String email
) {}
// JSON 输出：{"user_id": 1, "first_name": "John", "last_name": "Doe", "email": "..."}
```

**混合使用：**

```java
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public record OrderDTO(
    Long orderId,
    BigDecimal totalAmount,

    @JsonProperty("customer_email")  // 局部覆盖
    String email,

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    LocalDateTime createdAt
) {}
```

---

## 三、进阶篇：消除映射样板代码

### 3.1 模式三：MapStruct — 编译期安全的自动映射

**核心思想：** 用注解驱动的方式定义映射规则，MapStruct 在编译期自动生成高效的映射代码。

#### 引入依赖

```xml
<dependency>
    <groupId>org.mapstruct</groupId>
    <artifactId>mapstruct</artifactId>
    <version>1.6.3</version>
</dependency>
<dependency>
    <groupId>org.mapstruct</groupId>
    <artifactId>mapstruct-processor</artifactId>
    <version>1.6.3</version>
    <scope>provided</scope>
</dependency>
```

Maven 编译插件配置：

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.10.1</version>
    <configuration>
        <annotationProcessorPaths>
            <path>
                <groupId>org.mapstruct</groupId>
                <artifactId>mapstruct-processor</artifactId>
                <version>1.6.3</version>
            </path>
        </annotationProcessorPaths>
    </configuration>
</plugin>
```

#### 基本用法

```java
@Mapper(componentModel = "spring")
public interface UserMapper {

    UserDTO toDTO(User user);

    User toEntity(UserDTO dto);

    // 集合映射自动生成
    List<UserDTO> toDTOList(List<User> users);
}
```

编译后自动生成实现类：

```java
@Component
public class UserMapperImpl implements UserMapper {
    public UserDTO toDTO(User user) {
        // 类型安全的字段赋值，无反射开销
        UserDTO dto = new UserDTO();
        dto.setId(user.getId());
        dto.setFirstName(user.getFirstName());
        dto.setLastName(user.getLastName());
        dto.setEmail(user.getEmail());
        return dto;
    }
    // ...
}
```

#### 高级映射技巧

**① 字段名不匹配时的映射：**

```java
@Mapper(componentModel = "spring")
public interface OrderMapper {

    @Mapping(source = "user.email", target = "customerEmail")
    @Mapping(source = "totalAmount", target = "total")
    @Mapping(target = "items", ignore = true)
    OrderDTO toDTO(Order order);
}
```

**② 多源合并映射：**

```java
@Mapping(source = "order.id", target = "orderId")
@Mapping(source = "user.email", target = "email")
OrderSummaryDTO toSummary(Order order, User user);
```

**③ 自定义后处理逻辑：**

```java
@AfterMapping
default void calculateTotalItems(@MappingTarget OrderDTO dto, Order order) {
    dto.setTotalItems(order.getItems().size());
}
```

**④ 表达式映射：**

```java
@Mapping(target = "createdAt",
         expression = "java(java.time.LocalDateTime.now())")
Order toOrder(OrderDto dto);
```

#### 为什么选择 MapStruct 而非 ModelMapper？

| 对比维度 | MapStruct | ModelMapper |
|---------|-----------|-------------|
| 实现方式 | 编译期代码生成 | 运行时反射 |
| 性能 | 零反射开销，≈ 手写代码 | 反射调用，有额外开销 |
| 类型安全 | 编译期检查 | 运行时才暴露问题 |
| 调试难度 | 可直接查看生成的代码 | 黑盒映射，难以追踪 |
| 复杂映射 | 注解灵活配置 | 需要配置 Converter |

> **Netflix、Uber、Google 都在用 MapStruct。** — 公众号原文

---

### 3.2 模式四：Spring Data Projections — 零 DTO 的只读查询

**核心思想：** 对于只读查询，用 Spring Data 的投影接口直接在 Repository 层按需取字段，完全跳过 DTO。

#### 痛点场景

```java
@GetMapping("/users")
public List<UserDTO> getAllUsers() {
    // 查询所有字段 → 浪费内存
    List<User> users = userRepository.findAll();
    return users.stream()
        .map(user -> new UserDTO(user.getId(),
             user.getFirstName(), user.getLastName(), user.getEmail()))
        .collect(Collectors.toList());
}
```

#### 投影接口方案

```java
// ✅ 投影接口——不需要 DTO 类
public interface UserSummary {
    Long getId();
    String getFirstName();
    String getLastName();
    String getEmail();
}

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    // Spring 自动生成只查询这些字段的 SQL
    List<UserSummary> findAllBy();

    // 也支持自定义查询
    @Query("""
        SELECT u.id as id, u.firstName as firstName, u.email as email
        FROM User u WHERE u.createdAt > :date
        """)
    List<UserSummary> findRecentUsers(@Param("date") LocalDateTime date);
}

// ✅ 控制器直接返回
@GetMapping("/users")
public List<UserSummary> getAllUsers() {
    return userRepository.findAllBy();
}
```

#### 嵌套投影

```java
public interface OrderSummary {
    Long getId();
    BigDecimal getTotal();
    OrderStatus getStatus();

    // 嵌套投影——Spring 自动处理 JOIN
    CustomerInfo getCustomer();

    interface CustomerInfo {
        String getEmail();
        String getFullName();
    }
}

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<OrderSummary> findAllBy();
}
```

#### 投影 vs 传统 DTO 对比

| 维度 | 传统 DTO | 投影接口 |
|------|---------|---------|
| 类定义 | 需要额外 DTO 类 | 仅需接口声明 |
| 数据库查询 | 加载所有字段再过滤 | 仅查所需字段（性能优势） |
| 手动映射 | 需要手动或 MapStruct 映射 | 零映射 |
| 嵌套数据 | 需要额外 DTO + 映射 | 接口嵌套，自动 JOIN |
| 适用场景 | 读写混合 | 纯只读查询 |

> **Ondrej Kvasnovsky 的观点：** 投影不仅可以消除 DTO 样板代码，还能从根本上解决**N+1 查询问题**和**内存过度获取**（over-fetching）。

---

## 四、高级篇：零 DTO 场景的进阶方案

### 4.1 模式五：@JsonView — 单实体应对多视图

**问题场景：** 同一个实体在不同 API 端点需要返回不同字段组合。例如公开接口只显示基本信息，管理接口显示全部字段，摘要接口只显示 ID。

**传统方案 —— DTO 爆炸：**

```java
// 需要 3 个 DTO 类
public class UserPublicDTO   { /* 部分字段 */ }
public class UserAdminDTO    { /* 全部字段 */ }
public class UserSummaryDTO  { /* 最少字段 */ }
// + 3 个映射器
```

**@JsonView 方案：**

```java
public class User {

    // 视图层级定义
    public static class Views {
        public static class Public {}     // 公开视图
        public static class Admin extends Public {}  // 管理员视图（继承公开）
        public static class Summary {}    // 摘要视图（独立）
    }

    @JsonView(Views.Summary.class)     private Long id;
    @JsonView(Views.Public.class)      private String firstName;
    @JsonView(Views.Public.class)      private String lastName;
    @JsonView(Views.Public.class)      private String email;
    @JsonView(Views.Admin.class)       private String password;
    @JsonView(Views.Admin.class)       private LocalDateTime lastLoginAt;

    // getters, setters...
}
```

**控制器使用：**

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    // 公开资料 → 返回：id, firstName, lastName, email
    @GetMapping("/{id}")
    @JsonView(User.Views.Public.class)
    public User getPublicProfile(@PathVariable Long id) {
        return userService.findById(id);
    }

    // 管理员接口 → 返回全部字段
    @GetMapping("/admin/{id}")
    @JsonView(User.Views.Admin.class)
    @PreAuthorize("hasRole('ADMIN')")
    public User getAdminProfile(@PathVariable Long id) {
        return userService.findById(id);
    }

    // 摘要 → 仅返回 id
    @GetMapping("/summary")
    @JsonView(User.Views.Summary.class)
    public List<User> getUserSummary() {
        return userService.findAll();
    }
}
```

#### @JsonView 的核心优势

- **消灭 DTO 爆炸** — 一个实体服务多个 API 契约
- **视图继承** — Admin 视图自动包含 Public 视图的所有字段
- **声明式控制** — 通过注解声明字段可见性，逻辑集中

---

### 4.2 模式六：Record 结合 MapStruct + Projections — 三剑客组合

这三种模式并不互斥，可以组合使用：

```java
// Entity
@Entity
public class Product {
    private Long id;
    private String name;
    private String description;
    private BigDecimal price;
    private Integer stock;
    private String internalCode;
    // getters, setters...
}

// Record DTO
public record ProductDTO(
    Long id,
    String name,
    BigDecimal price
) {}

// MapStruct 实现 Record ↔ Entity 映射
@Mapper(componentModel = "spring")
public interface ProductMapper {
    ProductDTO toDTO(Product product);
    List<ProductDTO> toDTOList(List<Product> products);
}

// Projection 用于只读场景，直接跳过 DTO
public interface ProductSummary {
    Long getId();
    String getName();
}
```

---

## 五、实战篇：模式选型与最佳实践

### 5.1 模式决策树

```
你的场景是什么？
│
├─ 纯只读查询，不需要写回？
│   └─ ✅ 投影接口（最简，性能最优）
│
├─ 需要复杂的双向映射（DTO ↔ Entity）？
│   ├─ 字段名一致 → ✅ MapStruct
│   └─ 字段名不一致 → ✅ MapStruct + @Mapping
│
├─ 同一实体需要多种视图输出？
│   └─ ✅ @JsonView（比创建 N 个 DTO 强得多）
│
├─ 简单不可变的 DTO，无复杂映射？
│   └─ ✅ Java Record（最简洁）
│
├─ API 命名与 Java 不一致？
│   └─ ✅ @JsonNaming 全局策略
│
└─ 复杂场景（混合多种需求）？
    └─ ✅ Record + MapStruct + @JsonView 组合
```

### 5.2 不同场景推荐组合

| 业务场景 | 推荐方案 | 理由 |
|---------|---------|------|
| CRUD 简单接口 | Record + MapStruct | 定义即用，映射自动 |
| 列表查询（只读） | 投影接口 | 性能最优，零 DTO |
| 分角色多视图接口 | @JsonView | 单实体多视图，无需 N 个 DTO |
| 复杂聚合查询 | 投影接口 + @Query | 数据库层聚合，避免内存计算 |
| 微服务间数据传输 | Record + MapStruct | 不可变+类型安全 |
| 内部层间传递 | Record | 简洁，纯数据传输 |

### 5.3 @JsonView 与投影的取舍

@JsonView 和投影接口都能减少 DTO，但适用场景不同：

| 场景 | @JsonView | 投影接口 |
|------|-----------|---------|
| 同一个实体返回不同字段 | ✅ 天然适合 | ❌ 需要定义多个投影 |
| 减少数据库查询字段 | ❌ 仍查询全部字段 | ✅ 仅查所需字段 |
| 数据需要写回 | ✅ 有完整实体引用 | ❌ 只读 |
| 复杂嵌套报表 | ❌ 不适用 | ✅ 嵌套投影 + JPQL |

> **一句话：** @JsonView 解决的是"返回什么"的问题（序列化控制），投影解决的是"查什么"的问题（查询优化）。

### 5.4 性能对比

```
性能（高 → 低）：
投影接口 > MapStruct（编译期） > 手写映射 > ModelMapper（运行时反射）

代码量（少 → 多）：
投影接口 / @JsonView < MapStruct / Record < 传统 DTO

维护成本（低 → 高）：
Record / @JsonView < 投影接口 < MapStruct < 传统 DTO
```

### 5.5 完整示例：混合模式实战

一个典型的 REST API，综合运用多种模式：

```java
// ========== 实体 ==========
@Entity
public class Order {
    private Long id;
    private String orderNo;
    private BigDecimal amount;
    private String status;
    private LocalDateTime createdAt;
    private String customerName;
    private String customerPhone;
    private String customerEmail;
    private String internalNote;
    // getters, setters...
}

// ========== Record DTO（用于创建请求）==========
public record CreateOrderRequest(
    @NotBlank String orderNo,
    @NotNull @Positive BigDecimal amount,
    @NotBlank String customerName,
    @Pattern(regexp = "^1[3-9]\\d{9}$") String customerPhone
) {}

// ========== MapStruct 映射器 ==========
@Mapper(componentModel = "spring")
public interface OrderMapper {
    Order toEntity(CreateOrderRequest request);

    @Mapping(target = "createdAt", expression = "java(java.time.LocalDateTime.now())")
    @Mapping(target = "status", constant = "PENDING")
    Order toNewEntity(CreateOrderRequest request);
}

// ========== 投影接口（列表查询）==========
public interface OrderSummary {
    Long getId();
    String getOrderNo();
    BigDecimal getAmount();
    String getStatus();
}

// ========== @JsonView（详情接口权限控制）==========
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class OrderDetail {
    public static class Views {
        public static class Public {}
        public static class Internal extends Public {}
    }

    @JsonView(Views.Public.class)   private Long id;
    @JsonView(Views.Public.class)   private String orderNo;
    @JsonView(Views.Public.class)   private BigDecimal amount;
    @JsonView(Views.Public.class)   private String status;
    @JsonView(Views.Public.class)   private String customerName;
    @JsonView(Views.Internal.class) private String internalNote;
    @JsonView(Views.Internal.class) private String customerPhone;
    @JsonView(Views.Internal.class) private String customerEmail;
}

// ========== 控制器 ==========
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    // 创建 - Record + MapStruct
    @PostMapping
    public ResponseEntity<Void> create(@Valid @RequestBody CreateOrderRequest request) {
        Order order = orderMapper.toNewEntity(request);
        orderRepository.save(order);
        return ResponseEntity.created(...).build();
    }

    // 列表 - 投影（零 DTO）
    @GetMapping
    public List<OrderSummary> list() {
        return orderRepository.findAllProjectedBy();
    }

    // 详情 - @JsonView 分角色
    @GetMapping("/{id}")
    @JsonView(OrderDetail.Views.Public.class)
    public OrderDetail detail(@PathVariable Long id) {
        // ...
    }

    @GetMapping("/internal/{id}")
    @JsonView(OrderDetail.Views.Internal.class)
    @PreAuthorize("hasRole('ADMIN')")
    public OrderDetail internalDetail(@PathVariable Long id) {
        // ...
    }
}
```

---

## 六、总结

### 6.1 六种模式总览

| # | 模式 | 核心思想 | DTO 代码量 | 适用阶段 |
|---|------|---------|-----------|---------|
| 1 | Java Record DTO | 不可变数据载体，一行搞定 | ~5 行 | 入门 |
| 2 | @JsonNaming 命名策略 | 全局/局部控制 API 命名 | 零额外代码 | 入门 |
| 3 | MapStruct | 编译期代码生成，零反射 | 接口定义 ~10 行 | 进阶 |
| 4 | 投影接口 | 数据库按需查字段，完全跳过 DTO | 零 DTO（仅接口） | 进阶 |
| 5 | @JsonView | 单实体多视图，消灭 DTO 爆炸 | 零 DTO（注解控制） | 高级 |
| 6 | 组合模式 | Record + MapStruct + 投影 + @JsonView | 最小化 | 实战 |

### 6.2 核心原则

1. **只读用投影** — 不要为了只读查询造 DTO
2. **映射用 MapStruct** — 不要手写映射，不要用运行时反射映射库
3. **视图用 @JsonView** — 不要为接口差异造 N 个 DTO
4. **DTO 用 Record** — 不要写传统 POJO 风格的 DTO
5. **命名用 @JsonNaming** — 不要在每个字段上加 @JsonProperty

> 真正的 Spring 资深开发者从不亲手编写 DTO 样板代码。他们依靠经过验证的设计模式，彻底将其剔除。

---

## 参考资料

1. [告别冗余 DTO：5 种 Spring Boot 高效模式彻底取代样板代码](https://mp.weixin.qq.com/s/UjhQzOoP4xZNjn5ayVPIVQ) — 公众号《Spring Boot 实战案例锦集》
2. [Stop Writing Boilerplate DTOs: Use Java Records Instead](https://rameshfadatare.medium.com/stop-writing-boilerplate-dtos-use-java-records-instead-818976f37c0d) — Ramesh Fadatare
3. [How to avoid DTOs in Spring JPA](https://ondrej-kvasnovsky.medium.com/how-to-avoid-dtos-in-spring-jpa-53f34189c3bc) — Ondrej Kvasnovsky
4. [Stop Writing Boilerplate Code — Use MapStruct Instead](https://medium.com/@akashpadir10/stop-writing-boilerplate-code-in-spring-boot-use-mapstruct-instead-c49289948fea) — Akash Padir
5. [Using Java Records with Spring Boot DTOs](https://medium.com/@AlexanderObregon/using-java-records-with-spring-boot-dtos-619ff1484495) — Alexander Obregon
6. [Avoiding DTOs in Spring JPA: Smarter Alternatives](https://medium.com/@kaurharjeet122/avoiding-dtos-in-spring-jpa-smarter-alternatives-for-cleaner-code-e41d3d9d6a7e) — Harjeet Kaur
