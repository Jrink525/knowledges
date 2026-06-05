---
title: "Spring Boot 动态 JSON 请求处理：5 种方案 + 安全校验"
author: "lybgeek (Springboot实战案例锦集)"
source: "https://mp.weixin.qq.com/s/8I9HwPLE95EMdQm97-vfFA"
references:
  - https://cloud.tencent.com/developer/article/2553972
date: 2026-06-05
tags: [spring-boot, jackson, json, validation, security, java]
category: spring
---

# Spring Boot 动态 JSON 请求处理：5 种方案 + 安全校验

> 前后端分离模式下，前端传的 JSON 字段与后端 Java 类属性对不上号，是每个 Spring 开发者都会遇到的痛点。本文详解 5 种处理方案，并补充安全校验最佳实践。

---

## 场景痛点

前端提交的 JSON 常常带有实体类未定义的额外字段：

```json
{
  "name": "lybgeek",
  "mobile": "13800000000",
  "email": "lybgeek@163.com",
  "age": 18
}
```

但后端只有：

```java
@Data
public class User {
    private String name;
    private String mobile;
}
```

怎么优雅地拿到 `email` 和 `age`？以下 5 种方案从简单到高级，各有取舍。

---

## 方案一：Map 字段接收

直接在实体类中加一个 `Map<String, Object>` 字段：

```java
@Data
public class User {
    private String name;
    private String mobile;
    private Map<String, Object> extFields;  // 所有未映射字段打包到这里
}
```

前端 JSON 需要这样传：

```json
{
  "name": "lybgeek",
  "mobile": "13800000000",
  "extFields": {
    "email": "lybgeek@163.com",
    "age": 18
  }
}
```

**优点：** 实现最简单，零额外依赖。
**缺点：** 前端需要主动把额外字段包裹进 extFields，对调用方不透明。

---

## 方案二：JsonNode 类型字段

利用 Jackson 的 `JsonNode` 类型接收任意 JSON 结构：

```java
@Data
public class User {
    private String name;
    private String mobile;
    private JsonNode extFields;
}
```

提取字段：

```java
String email = user.getExtFields().get("email").asText();
int age = user.getExtFields().get("age").asInt();
```

**优点：** 可以处理任意嵌套结构，Jackson 原生支持。
**缺点：** 对调用方仍不透明，且 `JsonNode` 操作代码繁琐。

---

## 方案三：@JsonAnySetter / @JsonAnyGetter（推荐）

最优雅的方式：不需要前端配合，不认识的字段自动收集：

```java
@Data
public class User {
    private String name;
    private String mobile;
    protected Map<String, Object> extFields;

    @JsonAnySetter
    public void addFields(String key, Object value) {
        if (extFields == null) {
            extFields = new HashMap<>();
        }
        extFields.put(key, value);
    }

    @JsonAnyGetter
    public Map<String, Object> getExtFields() {
        return extFields;
    }
}
```

前端直接发：

```json
{
  "name": "lybgeek",
  "mobile": "13800000000",
  "email": "lybgeek@163.com",
  "age": 18
}
```

Jackson 自动把 `email` 和 `age` 通过 `@JsonAnySetter` 注入到 `extFields`。

**优点：** 对调用方完全透明，代码简洁。
**缺点：** 只能处理简单键值对，复杂嵌套需要额外逻辑。

---

## 方案四：自定义序列化/反序列化

完全掌控 JSON 与 Java 对象的转换过程：

```java
public class UserJsonDeserializer extends JsonDeserializer<User> {
    @Override
    public User deserialize(JsonParser p, DeserializationContext ctxt) throws IOException {
        JsonNode node = p.getCodec().readTree(p);
        Map<String, Object> ext = new HashMap<>();
        ext.put("email", getValue(node, "email"));
        ext.put("age", getValue(node, "age"));

        User user = new User();
        user.setName(getValue(node, "name"));
        user.setMobile(getValue(node, "mobile"));
        user.setExtFields(ext);
        return user;
    }
}
```

实体类上声明：

```java
@Data
@JsonDeserialize(using = UserJsonDeserializer.class)
@JsonSerialize(using = UserJsonSerializer.class)
public class User { ... }
```

**优点：** 完全控制序列化/反序列化逻辑，适合复杂业务。
**缺点：** 代码量大，每新增一个实体类都要写一套。

---

## 方案五：@JsonComponent 全局注册（终极方案）

把自定义序列化器注册到全局 `ObjectMapper`，一处定义全局生效：

```java
@JsonComponent
public class UserJsonComponent {

    public static class UserDeserializer extends JsonDeserializer<User> {
        // ... 同方案四
    }

    public static class UserSerializer extends JsonSerializer<User> {
        // ... 同方案四
    }
}
```

**优点：** 全局统一配置，不需要在每个实体类上加注解。
**缺点：** 如果不同实体类需要不同策略，会导致类膨胀。

---

## 方案对比总览

| 方案 | 前端配合 | 代码量 | 灵活度 | 适用场景 |
|------|----------|--------|--------|----------|
| Map 字段 | 需要（嵌套 extFields） | 低 | 低 | 临时快速处理 |
| JsonNode | 需要 | 中 | 中 | 结构复杂的嵌套 JSON |
| **@JsonAnySetter** | **不需要** | **低** | **高** | **大多数日常场景 ✅** |
| 自定义序列化 | 不需要 | 高 | 最高 | 复杂业务映射 |
| @JsonComponent 全局 | 不需要 | 高 | 全局 | 统一规范的大型项目 |

---

## ⚠️ 安全校验：处理动态 JSON 的必知风险

动态 JSON 接收额外字段带来了**三个安全风险**，必须配套处理：

### 1. 字段注入攻击（Mass Assignment / 批量赋值）

攻击者可能通过额外字段注入不该修改的属性。例如 User 类有 `role` 字段没暴露但被 `@JsonAnySetter` 捕获到：

```json
{
  "name": "attacker",
  "role": "admin"
}
```

**防御策略：**
- **字段白名单**：在 `@JsonAnySetter` 中过滤只允许的 key：

```java
private static final Set<String> ALLOWED_EXTRA_FIELDS = Set.of("email", "age", "nickname");

@JsonAnySetter
public void addFields(String key, Object value) {
    if (!ALLOWED_EXTRA_FIELDS.contains(key)) {
        throw new IllegalArgumentException("非法字段: " + key);
    }
    extFields.put(key, value);
}
```

- **DTO 隔离**：永远不要直接把 JPA Entity 当作请求体接收，使用单独的 DTO 类。

### 2. XSS 注入

通过 JSON 字段传入 `<script>` 标签或其他恶意内容：

```json
{
  "name": "lybgeek",
  "comment": "<script>alert('xss')</script>"
}
```

**防御策略：**
- **Jackson 全局配置 HTML 转义**：

```java
@Bean
public Jackson2ObjectMapperBuilderCustomizer xssSanitizer() {
    return builder -> builder.postConfigurer(mapper -> {
        mapper.getFactory().setCharacterEscapes(new HtmlCharacterEscapes());
    });
}
```

- **输出时做 HTML 编码**（Thymeleaf 等模板引擎默认会做）
- **输入校验**：对字符串字段做 XSS 过滤

### 3. 数据大小与类型攻击

攻击者可能传入超长字符串或超深嵌套结构耗尽内存：

```json
{
  "name": "正常",
  "bio": "a".repeat(1000000)
}
```

**防御策略：**
- **Jackson 配置限制**：

```yaml
spring:
  jackson:
    deserialization:
      max-string-length: 10000
```

- **@Size 注解**（对已知字段）：

```java
@Size(max = 500)
private String bio;
```

- **Spring Boot 全局 JSON 请求大小限制**：

```yaml
spring:
  servlet:
    multipart:
      max-request-size: 1MB
  jackson:
    parser:
      max-nesting-depth: 10
```

### 4. 动态字段的 Validation

`@JsonAnySetter` 收集的字段不走标准的 Bean Validation。解决方案：

```java
@JsonAnySetter
public void addFields(String key, Object value) {
    // 手动校验
    if (value instanceof String && ((String) value).length() > 1000) {
        throw new IllegalArgumentException(key + " 超过长度限制");
    }
    if (value instanceof Number && ((Number) value).doubleValue() > 1000000) {
        throw new IllegalArgumentException(key + " 数值超过上限");
    }
    extFields.put(key, value);
}
```

---

## 最佳实践总结

1. **默认方案：`@JsonAnySetter`**，对调用方透明、代码最少
2. **必须加白名单**：杜绝字段注入攻击
3. **DTO 与 Entity 分离**：绝对不要用 JPA Entity 直接接收请求
4. **配置全局 JSON 安全**：大小限制、嵌套深度、XSS 转义
5. **手动校验动态字段**：Bean Validation 管不到 `Map` 里的值
6. **日志记录**：记录被拒绝的字段名，便于排查异常请求

---

## 参考代码

完整示例代码：[lyb-geek/springboot-learning - springboot-dynamics-json](https://github.com/lyb-geek/springboot-learning/tree/master/springboot-dynamics-json)

---

*注：本文核心内容来自微信公众号"Springboot实战案例锦集"的原文，安全校验部分为补充增强内容。*
