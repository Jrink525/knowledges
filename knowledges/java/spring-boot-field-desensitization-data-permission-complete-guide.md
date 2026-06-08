---
title: "Spring Boot 字段级响应处理完全指南：脱敏、数据权限、动态过滤"
source: "https://mp.weixin.qq.com/s/v-FcRFpYt6Hcf9Wqz7kuCw"
author: "Spring Boot 实战案例锦集"
category: "java"
tags: [spring-boot, desensitization, field-masking, data-permission, jackson, responsebodyadvice, jsonpath]
---

# Spring Boot 字段级响应处理完全指南

> 基于微信公众号文章《代码零改动！Spring Boot 字段动态脱敏》扩展补充。  
> 覆盖场景：字段脱敏、字段级数据权限控制、动态字段过滤。

---

## 第一部分：原文方案 — 基于 ResponseBodyAdvice + JsonPath 的动态脱敏

### 核心思路

在 Spring Boot 的响应出口（`ResponseBodyAdvice`）统一拦截，通过 JsonPath 表达式匹配 JSON 节点，运行时动态替换敏感字段值。

### 架构图

```
Controller 返回 POJO
       ↓
ResponseBodyAdvice.supports()
  ├─ 检查 @Masking 注解（指定字段路径）
  └─ 检查 yml 配置（类名.方法名 → JsonPath 列表）
       ↓
ResponseBodyAdvice.beforeBodyWrite()
  ├─ POJO → JSON (Jackson)
  ├─ JsonPath.modify() 匹配并脱敏
  └─ JSON → POJO (Jackson, 保留泛型)
       ↓
返回脱敏后的响应
```

### 关键组件

**1. 配置类 `MaskingProperties`**

```yaml
pack:
  masking:
    enabled: true
    masks:
      '[queryUser]': $..phone,$..idNo
      '[com.pack.masking.test.UserController.getUserList]': $..cardNo,$..email
```

**2. 自定义注解 `@Masking`**

用在 Controller 方法上，支持硬编码指定字段或引用配置 key。

**3. ResponseBodyAdvice 拦截器**

- `supports()` 方法决定是否需要对当前响应做脱敏
- `beforeBodyWrite()` 将 POJO 转 JSON → JsonPath 替换 → 恢复为 POJO
- 脱敏结果通过 `RequestAttributes` 跨方法传递

**4. JsonModifier 工具类**

基于 Jayway JsonPath 的 `DocumentContext.map()` 对匹配节点做替换。

**5. StringMaskUtils 掩码工具**

按字符串长度智能脱敏（2 字符 → `X*`，3 字符 → `X*Z`，长字符串保留首尾）。

---

## 第二部分：扩展 — 字段级脱敏的 5 种主流实现方案

> 原文的 ResponseBodyAdvice + JsonPath 是方案一。以下是其他可行方案及对比。

### 方案一：ResponseBodyAdvice + 注解（原文的延伸）

**适用场景：** 需要统一拦截、配置驱动、零业务侵入。

**优点：**
- 一处配置全局生效
- 支持运行时动态匹配
- 不侵入业务代码

**缺点：**
- POJO → JSON → POJO 有序列化开销（大对象明显）
- JsonPath 字符串表达式无法编译期校验
- 泛型恢复可能丢失类型信息

### 方案二：Jackson 序列化过滤器（@JsonFilter + FilterProvider）

**原理：** 在 Jackson 序列化时动态决定哪些字段可见。

```java
@JsonFilter("permissionFilter")
public class User {
    private String name;
    private String phone;   // 敏感字段
    private String idNo;    // 敏感字段
}
```

在 Controller 或拦截器中设置 FilterProvider：

```java
@GetMapping("/users")
public MappingJacksonValue getUsers() {
    List<User> users = userService.findAll();
    MappingJacksonValue value = new MappingJacksonValue(users);
    
    // 根据当前用户角色动态决定显示哪些字段
    Set<String> allowedFields = getPermissionFields();
    SimpleFilterProvider filter = new SimpleFilterProvider()
        .addFilter("permissionFilter",
            SimpleBeanPropertyFilter.filterOutAllExcept(allowedFields));
    value.setFilters(filter);
    return value;
}
```

**优点：**
- Jackson 原生支持，零额外依赖
- 编译期类型安全（字段名是 Java 属性名）
- 无序列化开销（不经过 JSON → 反序列化）

**缺点：**
- 每类需要声明 `@JsonFilter` 注解
- 动态逻辑在 Controller 层，难以统一管理
- 不适合嵌套复杂对象的深度控制

### 方案三：Jackson 自定义序列化器（@JsonSerialize + 自定义 StdSerializer）

**原理：** 为每个敏感字段类型定义专用序列化器。

```java
public class PhoneDesensitizer extends StdSerializer<String> {
    public PhoneDesensitizer() { this(null); }
    public PhoneDesensitizer(Class<String> t) { super(t); }
    
    @Override
    public void serialize(String value, JsonGenerator gen, SerializerProvider provider) 
            throws IOException {
        if (value == null || value.length() < 7) {
            gen.writeString(value);
            return;
        }
        gen.writeString(value.substring(0, 3) + "****" + value.substring(7));
    }
}
```

在实体字段上标注：

```java
public class User {
    private String name;
    
    @JsonSerialize(using = PhoneDesensitizer.class)
    private String phone;
    
    @JsonSerialize(using = IdNoDesensitizer.class)
    private String idNo;
}
```

**优点：**
- 声明式，用法最简洁
- 序列化时直接处理，零运行时开销
- 可复用（PhoneDesensitizer 可到处使用）

**缺点：**
- 静态绑定——编译期决定要脱敏，无法运行时根据用户角色开关
- 每个敏感类型要写一个序列化器类
- 如果既要脱敏又要做数据权限（决定是否返回该字段），需要叠加更多机制

### 方案四：Spring AOP + 自定义注解

**原理：** AOP 环绕 Controller 方法，对返回值做后处理。

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface MaskResult {
    MaskRule[] value() default {};
    String[] excludeFields() default {};
    Class<?>[] groups() default {};
}

@Aspect
@Component
public class MaskResultAspect {
    @Around("@annotation(maskResult)")
    public Object maskResult(ProceedingJoinPoint pjp, MaskResult maskResult) 
            throws Throwable {
        Object result = pjp.proceed();
        // 通过反射或 Jackson 处理 result 中的字段
        return doMask(result, maskResult);
    }
}
```

**优点：**
- AOP 语义清晰，注解驱动
- 可以同时处理入参验证和返回值脱敏
- 适合需要二次加工（脱敏 + 格式转换 + 权限过滤）的场景

**缺点：**
- 反射操作有性能开销
- 如果要处理深层嵌套，需要手写递归遍历逻辑

### 方案五：MyBatis / JPA 结果映射层处理（ORM 侧）

**原理：** 在数据查询阶段就处理敏感字段，而不是等到响应阶段。

```java
@ColumnType(typeHandler = MaskingTypeHandler.class)
private String phone;
```

**适用场景：** 数据库层面的字段始终需要脱敏（如日志系统、审计系统），不管谁查都一样。

**优缺点：**
- 防止敏感信息出现在任何输出渠道（不只是 HTTP，还包括日志、MQ、导出）
- 缺点是粒度粗——同一个字段在管理端可能不需要脱敏，在用户端需要脱敏，ORM 层无法区分

---

## 第三部分：扩展 — 字段级数据权限控制

> 脱敏只解决了「显示成 xxx」，但很多场景需要的是「这个字段根本不出现」。

### 场景

| 角色 | 返回的 User 对象 |
|------|----------------|
| 管理员 | `{name: "张三", phone: "13812345678", idNo: "110101...", salary: 50000}` |
| 部门经理 | `{name: "张三", phone: "138****5678", salary: 50000}` |
| 普通员工 | `{name: "张三", phone: "138****5678"}` — idNo 和 salary 不返回 |

### 实现方式：Jackson PropertyFilter + 上下文角色

```java
@Component
public class DynamicFieldFilter {
    
    private static final Map<String, Set<String>> ROLE_FIELDS = Map.of(
        "ADMIN",    Set.of("name", "phone", "idNo", "salary", "email"),
        "MANAGER",  Set.of("name", "phone", "salary"),
        "USER",     Set.of("name", "phone")
    );
    
    public MappingJacksonValue apply(Object value, String role) {
        MappingJacksonValue jacksonValue = new MappingJacksonValue(value);
        Set<String> allowed = ROLE_FIELDS.getOrDefault(role, Set.of("name"));
        
        SimpleFilterProvider filterProvider = new SimpleFilterProvider()
            .setFailOnUnknownId(false);
        
        // 为所有带 @JsonFilter 的类型注册同一个过滤器
        filterProvider.addFilter("dynamicFilter",
            SimpleBeanPropertyFilter.filterOutAllExcept(allowed));
        
        jacksonValue.setFilters(filterProvider);
        return jacksonValue;
    }
}
```

### 更灵活的方案：SpEL + Permission 注解

```java
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
public @interface FieldPermission {
    String[] roles() default {};
    String spel() default "";  // 更灵活的规则
    MaskType mask() default MaskType.NONE;  // 脱敏方式
}

public class User {
    private String name;
    
    @FieldPermission(roles = {"ADMIN", "MANAGER"}, mask = MaskType.PHONE)
    private String phone;
    
    @FieldPermission(roles = {"ADMIN"})
    private String idNo;
    
    @FieldPermission(roles = {"ADMIN", "MANAGER"})
    private BigDecimal salary;
}
```

配合 Jackson 的 `BeanSerializerModifier` 运行时动态决定字段可见性和序列化方式。

---

## 第四部分：扩展 — 综合架构设计

### 分层职责

```
Controller
  ↓ 原始 POJO 返回
ResponseBodyAdvice / AOP / Jackson Filter
  ├── 第一层：数据权限过滤（哪些字段可见）
  │    读取 SecurityContext 中的用户角色
  │    移除无权访问的字段（或置 null）
  │
  ├── 第二层：字段脱敏（可见字段的显示形式）
  │    按注解/配置执行脱敏策略
  │    PHONE → 138****5678
  │    ID_CARD → 110**************X
  │    EMAIL → z***@kongming.com
  │    BANK_CARD → 6222*******7890
  │
  └── 第三层：通用后处理（排序、分页包装、traceId 注入）
```

### 完整脱敏策略定义

```java
public enum MaskStrategy {
    PHONE {
        public String mask(String raw) {
            return raw != null && raw.length() >= 7
                ? raw.substring(0, 3) + "****" + raw.substring(7)
                : raw;
        }
    },
    ID_CARD {
        public String mask(String raw) {
            return raw != null && raw.length() >= 10
                ? raw.substring(0, 3) + "**********" + raw.substring(raw.length() - 4)
                : raw;
        }
    },
    EMAIL {
        public String mask(String raw) {
            if (raw == null || !raw.contains("@")) return raw;
            int at = raw.indexOf("@");
            return raw.charAt(0) + "***" + raw.substring(at);
        }
    },
    BANK_CARD {
        public String mask(String raw) {
            return raw != null && raw.length() >= 8
                ? raw.substring(0, 4) + "****" + raw.substring(raw.length() - 4)
                : raw;
        }
    },
    NAME {
        public String mask(String raw) {
            if (raw == null || raw.length() < 2) return raw;
            return raw.charAt(0) + "*".repeat(raw.length() - 1);
        }
    },
    CUSTOM {
        // 保留前缀和后缀各 N 位
        public String mask(String raw) { return raw; }
    };
    
    public abstract String mask(String raw);
}
```

### 通用脱敏注解

```java
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Sensitive {
    MaskStrategy strategy() default MaskStrategy.PHONE;
    String[] roles() default {};          // 哪些角色可见原始值
    boolean hideCompletely() default false; // 是否完全删除该字段
}
```

### 复杂场景处理

**嵌套对象：**
```java
public class Order {
    @Sensitive(strategy = MaskStrategy.NAME)
    private User buyer;       // User 中的 name 字段需要脱敏
    @Sensitive(strategy = MaskStrategy.PHONE)
    private User receiver;    // User 中的 phone 需要脱敏
    private List<OrderItem> items;  // OrderItem 可能也有敏感字段
}
```

→ 需要递归处理，对每个字段检查是否有 `@Sensitive` 注解。

**集合 / 分页：**
```java
// Page 对象包装一层，内部数据的字段也要脱敏
public class PageResult<T> {
    private List<T> data;       // 需要脱敏
    private long total;
    private int page;
}
```

→ `ResponseBodyAdvice` 需要处理泛型类型，使用 Jackson 的 `TypeFactory.constructParametricType()` 正确反序列化。

---

## 第五部分：性能与安全注意事项

### 性能
| 方案 | 额外开销 | 适合场景 |
|------|---------|---------|
| ResponseBodyAdvice + JSON 序列化 | 高（POJO ↔ JSON 2 次） | 低频接口、配置驱动 |
| Jackson @JsonSerialize | 无（序列化直接处理） | 高频接口、固定脱敏规则 |
| Jackson @JsonFilter | 低（仅额外 filter 判定） | 需要动态角色过滤 |
| AOP + 反射 | 中 | 需要二次加工 |

### 安全
- `ResponseBodyAdvice` 中的 `ObjectMapper` 应该与应用主 `ObjectMapper` 隔离，避免配置冲突
- JSON 反序列化时注意泛型擦除（List<User> 反序列化后可能变成 List<Map>）
- 脱敏策略需要统一管理，不应散落在各个 Controller 中
- 脱敏日志应当记录（哪个字段被脱敏、谁触发了请求），但日志本身也要脱敏

---

## 第六部分：总结

字段级响应处理在 Spring Boot 中有多种实现路径，选择取决于你的需求层次：

| 层次 | 需求 | 推荐方案 |
|------|------|---------|
| L1 | 固定字段统一脱敏 | `@JsonSerialize` + 自定义 StdSerializer |
| L2 | 不同接口不同脱敏规则 | `@Masking` + `ResponseBodyAdvice` |
| L3 | 脱敏 + 数据权限（字段可见性） | Jackson `@JsonFilter` + `FilterProvider` |
| L4 | 全量灵活控制 | AOP + 注解 + FieldPermission 架构 |
| L5 | 不为 HTTP 专属（MQ、日志、导出也适用） | ORM 层 typeHandler + 通用脱敏工具 |

**本文内容覆盖：**
- ✅ 原文方案：ResponseBodyAdvice + JsonPath 动态脱敏
- ✅ 5 种脱敏实现方案对比
- ✅ 数据权限控制（角色动态字段过滤）
- ✅ 脱敏策略枚举 + 通用注解
- ✅ 嵌套对象 / 分页 / 集合处理
- ✅ 性能与安全注意事项

> **核心原则：脱敏和数据权限是系统安全的一部分，不是业务逻辑的一部分。** 它应该在基础设施层统一处理，而不是散落在每个 Service 或 Controller 中。
