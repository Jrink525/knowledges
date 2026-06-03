---
title: Spring Boot 极具价值的8个代码片段 — 可直接使用
tags: [spring, spring-boot, code-snippets, mapstruct, validation, jpa, auditing, 来源:公众号]
category: spring/code-snippets
source: https://mp.weixin.qq.com/s/7gizyxsYyCFmWIO_B1SeZw
date: 2026-05-21
---

# Spring Boot 极具价值的8个代码片段 — 可直接用于生产

> **环境：** Spring Boot 3.5.0
> **来源：** Spring Boot 3实战案例锦集

---

## 目录

1. [MapStruct 类型转换 + 基础类型映射](#1-mapstruct-类型转换)
2. [嵌入式集合 @Embeddable](#2-嵌入式集合-embeddable)
3. [国际化资源辅助类](#3-国际化资源辅助类)
4. [安全随机字符串生成器](#4-安全随机字符串生成器)
5. [领域特定运行时异常](#5-领域特定运行时异常)
6. [类型安全的配置（Duration + DataSize）](#6-类型安全的配置)
7. [JPA 自动审计](#7-jpa-自动审计)
8. [自定义注解验证](#8-自定义注解验证)

---

## 1. MapStruct 类型转换

MapStruct 不仅用于 DTO/Entity 转换，还能处理基础类型映射。

### 基础类型转换器

```java
@Mapper(componentModel = "spring")
public interface CommonMapper {

    @Named("stringToList")
    default List<String> stringToList(String source) {
        if (!StringUtils.hasText(source)) return new ArrayList<>();
        return Arrays.stream(source.split(","))
                .map(String::trim)
                .filter(StringUtils::hasText)
                .collect(Collectors.toList());
    }

    @Named("listToString")
    default String listToString(List<String> source) {
        if (source == null || source.isEmpty()) return "";
        return String.join(",", source);
    }
}
```

### 在 DTO→Entity 映射中使用

```java
@Mapper(componentModel = "spring", uses = CommonMapper.class)
public interface MyEntityMapper {

    @Mapping(source = "tags", target = "tags", qualifiedByName = "stringToList")
    MyEntity dtoToEntity(MyDto dto);
}
```

### 🚀 增强：通用类型转换器集

```java
@Mapper(componentModel = "spring")
public interface TypeConverters {

    String SPLITTER = ",";

    // ====== 字符串 ↔ 集合 ======

    @Named("toStrList")
    default List<String> toStrList(String source) {
        if (!StringUtils.hasText(source)) return List.of();
        return Arrays.stream(source.split(SPLITTER))
                .map(String::trim)
                .filter(StringUtils::hasText)
                .toList();
    }

    @Named("fromStrList")
    default String fromStrList(List<String> source) {
        if (source == null || source.isEmpty()) return "";
        return String.join(SPLITTER, source);
    }

    // ====== 字符串 ↔ Long 集合 ======

    @Named("toLongList")
    default List<Long> toLongList(String source) {
        if (!StringUtils.hasText(source)) return List.of();
        return Arrays.stream(source.split(SPLITTER))
                .map(String::trim)
                .filter(StringUtils::hasText)
                .map(Long::valueOf)
                .toList();
    }

    @Named("fromLongList")
    default String fromLongList(List<Long> source) {
        if (source == null || source.isEmpty()) return "";
        return source.stream().map(String::valueOf).collect(Collectors.joining(SPLITTER));
    }

    // ====== 枚举 ↔ 字符串 ======

    @Named("enumToStr")
    default String enumToStr(Enum<?> source) {
        return source != null ? source.name() : null;
    }

    @Named("strToEnum")
    default <T extends Enum<T>> T strToEnum(String source, @Context Class<T> enumClass) {
        if (!StringUtils.hasText(source)) return null;
        return Enum.valueOf(enumClass, source.toUpperCase());
    }

    // ====== 时间戳 / LocalDateTime ======

    @Named("localDateTimeToLong")
    default Long localDateTimeToLong(LocalDateTime source) {
        return source != null ? source.toInstant(ZoneOffset.UTC).toEpochMilli() : null;
    }

    @Named("longToLocalDateTime")
    default LocalDateTime longToLocalDateTime(Long source) {
        return source != null
                ? LocalDateTime.ofInstant(Instant.ofEpochMilli(source), ZoneOffset.UTC)
                : null;
    }
}
```

---

## 2. 嵌入式集合 @Embeddable

当不需要独立关联表时，用 `@Embeddable` + 转换器将集合存入单列：

```java
@Embeddable
public class EmailEmbeddable {

    private String value;  // 逗号分隔存储

    public EmailEmbeddable() {}

    public EmailEmbeddable(Set<String> values) {
        if (values == null) {
            this.value = null;
        } else {
            Set<String> validated = values.stream()
                    .filter(StringUtils::hasText)
                    .map(String::trim)
                    .collect(Collectors.toSet());
            this.value = String.join(",", validated);
        }
    }

    public Set<String> getValues() {
        if (!StringUtils.hasText(value)) return new HashSet<>();
        return Arrays.stream(value.split(","))
                .map(String::trim)
                .filter(StringUtils::hasText)
                .collect(Collectors.toSet());
    }
}
```

### 实体中使用

```java
@Entity
@Table(name = "x_customer")
public class Customer {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @Embedded
    private EmailEmbeddable emails;  // 单列存储 Set<String>
}
```

> 适用于标签列表、邮件列表等简单集合场景，避免多对多关联表的开销。

---

## 3. 国际化资源辅助类

封装 `MessageSource`，无需在每个 Service 中重复注入：

```java
@Component
public class MessageHelper {

    private final MessageSource messageSource;

    public MessageHelper(MessageSource messageSource) {
        this.messageSource = messageSource;
    }

    /** 获取国际化消息 */
    public String get(String code, Object... args) {
        return messageSource.getMessage(code, args, LocaleContextHolder.getLocale());
    }

    /** 获取国际化消息，不存在时返回默认值 */
    public String getOrDefault(String code, String defaultMsg, Object... args) {
        try {
            return messageSource.getMessage(code, args, LocaleContextHolder.getLocale());
        } catch (NoSuchMessageException e) {
            return defaultMsg;
        }
    }
}
```

### 🚀 增强：带参国际化 + 错误码枚举

```java
/**
 * 错误码枚举，配合 MessageHelper 使用
 */
public enum ErrorCode {
    USER_NOT_FOUND("user.not.found"),
    ORDER_EXPIRED("order.expired"),
    INVALID_PARAM("invalid.param");

    private final String key;
    ErrorCode(String key) { this.key = key; }
    public String getKey() { return key; }
}

// 使用
@Service
public class UserService {
    private final MessageHelper msg;

    public UserService(MessageHelper msg) {
        this.msg = msg;
    }

    public void checkUser(Long id) {
        throw new BadRequestException(msg.get(ErrorCode.USER_NOT_FOUND.getKey(), id));
    }
}
```

国际化配置文件 `messages.properties`：
```properties
user.not.found=用户 {0} 不存在
order.expired=订单已过期
invalid.param=参数无效: {0}
```

---

## 4. 安全随机字符串生成器

使用 `SecureRandom`（而非 `Random`）生成密码学安全的随机字符串：

```java
@Component
public class RandomUtil {

    private static final SecureRandom SECURE_RANDOM = new SecureRandom();
    private static final String ALPHANUMERIC =
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

    /** 生成指定长度的字母数字随机字符串 */
    public static String generateReference(int length) {
        StringBuilder sb = new StringBuilder(length);
        for (int i = 0; i < length; i++) {
            sb.append(ALPHANUMERIC.charAt(SECURE_RANDOM.nextInt(ALPHANUMERIC.length())));
        }
        return sb.toString();
    }

    /** 生成 Base64 URL 安全的 Token（32 字符） */
    public static String generateToken() {
        byte[] randomBytes = new byte[24];
        SECURE_RANDOM.nextBytes(randomBytes);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(randomBytes);
    }

    /** 生成数字验证码（6 位） */
    public static String generateCode(int digits) {
        int min = (int) Math.pow(10, digits - 1);
        int max = (int) Math.pow(10, digits) - 1;
        return String.valueOf(SECURE_RANDOM.nextInt(max - min + 1) + min);
    }
}
```

---

## 5. 领域特定运行时异常

创建异常层次结构，与 `@ControllerAdvice` 配合返回精确的 HTTP 状态码：

```java
/**
 * 资源不存在 — HTTP 404
 */
public class ResourceNotFoundException extends RuntimeException {
    public ResourceNotFoundException(String resourceName, String fieldName, Object fieldValue) {
        super(String.format("%s not found with %s : '%s'", resourceName, fieldName, fieldValue));
    }

    public ResourceNotFoundException(String message) {
        super(message);
    }
}

/**
 * 资源冲突 — HTTP 409
 */
public class DuplicateResourceException extends RuntimeException {
    public DuplicateResourceException(String message) {
        super(message);
    }
}

/**
 * 请求参数错误 — HTTP 400
 */
public class BadRequestException extends RuntimeException {
    public BadRequestException(String message) {
        super(message);
    }
    public BadRequestException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

### 业务中使用

```java
@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;

    public User getUserById(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("User", "id", id));
    }

    public User createUser(User user) {
        if (userRepository.existsByEmail(user.getEmail())) {
            throw new DuplicateResourceException("Email already registered: " + user.getEmail());
        }
        return userRepository.save(user);
    }
}
```

---

## 6. 类型安全的配置

使用 `Duration` 和 `DataSize` 替代 `int`/`long`：

```java
@Configuration
@ConfigurationProperties(prefix = "pack.app.upload")
public class UploadConfig {
    private Duration timeout = Duration.ofSeconds(30);
    private DataSize maxFileSize = DataSize.ofMegabytes(10);
    // getters & setters
}
```

```yaml
pack:
  app:
    upload:
      timeout: 10s       # Duration.parse("PT10S")
      maxFileSize: 10MB   # DataSize.parse("10MB")
```

支持的时间格式：`ns`, `us`, `ms`, `s`, `m`, `h`, `d`
支持的数据大小格式：`B`, `KB`, `MB`, `GB`, `TB`

---

## 7. JPA 自动审计

### 审计基类

```java
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class AuditEntity {

    @CreatedDate
    @Column(updatable = false)
    protected LocalDateTime createdAt;

    @LastModifiedDate
    protected LocalDateTime updatedAt;

    @CreatedBy
    @Column(updatable = false)
    protected String createdBy;

    @LastModifiedBy
    protected String updatedBy;

    // getters & setters...
}
```

### 实体继承

```java
@Entity
@Table(name = "t_product")
public class Product extends AuditEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;
    private BigDecimal price;
    // 自动拥有 createdAt / updatedAt / createdBy / updatedBy
}
```

### 启用审计

```java
@Configuration
@EnableJpaAuditing(auditorAwareRef = "auditorProvider")
public class JpaConfig {

    @Bean
    public AuditorAware<String> auditorProvider() {
        // 实际项目从 SecurityContext 获取当前用户
        return () -> Optional.ofNullable(SecurityContextHolder.getContext())
                .map(ctx -> ctx.getAuthentication())
                .map(auth -> auth.getName())
                .or(() -> Optional.of("SYSTEM"));
    }
}
```

### 🚀 增强：带乐观锁的审计基类

```java
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // ====== 审计字段 ======

    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;

    @CreatedBy
    @Column(updatable = false)
    private String createdBy;

    @LastModifiedBy
    private String updatedBy;

    // ====== 乐观锁 ======

    @Version
    private Long version;

    // ====== 逻辑删除 ======

    @Column(name = "is_deleted")
    private Boolean deleted = false;

    // ====== 公共方法 ======

    public void markDeleted() {
        this.deleted = true;
    }

    // getters...
}
```

---

## 8. 自定义注解验证

### 自定义 @ValueOfEnum 验证

```java
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Constraint(validatedBy = ValueOfEnumValidator.class)
public @interface ValueOfEnum {
    Class<? extends Enum<?>> enumClass();
    String message() default "必须是 {enumClass} 枚举类型";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

### 验证器

```java
public class ValueOfEnumValidator implements ConstraintValidator<ValueOfEnum, CharSequence> {

    private List<String> acceptedValues;

    @Override
    public void initialize(ValueOfEnum annotation) {
        acceptedValues = Stream.of(annotation.enumClass().getEnumConstants())
                .map(Enum::name)
                .collect(Collectors.toList());
    }

    @Override
    public boolean isValid(CharSequence value, ConstraintValidatorContext context) {
        if (value == null) return true;  // 空值由 @NotNull 处理
        return acceptedValues.contains(value.toString().toUpperCase());
    }
}
```

### 使用

```java
public class OrderDTO {
    @ValueOfEnum(enumClass = OrderStatus.class, message = "无效状态")
    private String status;

    @NotNull
    private String orderNo;
}
```

### 🚀 增强：更多自定义验证注解

```java
// ====== 手机号验证 ======
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = PhoneValidator.class)
public @interface Phone {
    String message() default "手机号格式不正确";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}

public class PhoneValidator implements ConstraintValidator<Phone, String> {
    private static final Pattern PATTERN = Pattern.compile("^1[3-9]\\d{9}$");

    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        if (value == null) return true;
        return PATTERN.matcher(value).matches();
    }
}

// ====== 枚举值验证（兼容大小写） ======
public class LenientEnumValidator implements ConstraintValidator<ValueOfEnum, CharSequence> {
    private Set<String> acceptedValues;

    @Override
    public void initialize(ValueOfEnum annotation) {
        acceptedValues = Stream.of(annotation.enumClass().getEnumConstants())
                .map(e -> e.name().toLowerCase())
                .collect(Collectors.toSet());
    }

    @Override
    public boolean isValid(CharSequence value, ConstraintValidatorContext context) {
        if (value == null) return true;
        return acceptedValues.contains(value.toString().trim().toLowerCase());
    }
}
```

---

*本文整理自公众号「Springboot实战案例锦集」，代码片段经增强和补充注释。*
