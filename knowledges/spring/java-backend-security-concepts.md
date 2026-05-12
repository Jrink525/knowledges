---
title: Java Backend Security Concepts — Core Guide (CN)
tags: [java, spring, security, jwt, authentication, authorization, interview, 面试]
---

# Java 后端开发者必掌握的安全概念

> 原文：Every Java Backend Developer Should Master These Security Concepts  
> 作者：Saquib Aftab（@saquibdev）  
> 原文链接：https://medium.com/javarevisited/every-java-backend-developer-should-master-these-security-concepts-d71e2a9082b3  
> 译者增强：Jarvis II

---

## 概述

作为 Java 后端开发者，我们写 API、处理用户数据、构建用户信任的系统——**安全漏洞一个就够了**。

本文覆盖了核心的安全概念及其在 Spring Boot 中的实际应用。

---

## 1. Authentication vs. Authorization（认证 vs. 授权）

这两个概念经常混淆。

| 概念 | 英文 | 问题 | 对应 |
|------|------|------|------|
| 认证 | Authentication | 你是谁？ | 登录验证 |
| 授权 | Authorization | 你能做什么？ | 权限检查 |

**认证在前，授权在后**。用户先登录（认证），系统再判断能否访问某资源（授权）。

### Spring Security 中的配置

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(AbstractHttpConfigurer::disable)
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            );
        return http.build();
    }
}
```

**关键点**：
- `/api/public/**` — 任何人都可访问
- `/api/admin/**` — 需要 ADMIN 角色
- 其他请求 — 需要认证
- `STATELESS` — 无状态（适合 REST API）

### 增强：常见认证方式对比

| 方式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| Session-Cookie | 简单、服务端控制 | 需共享 session 存储 | 单体应用 |
| JWT | 无状态、跨服务 | Token 吊销困难 | 微服务/分布式 |
| OAuth2 + JWT | 第三方集成 | 实现复杂 | 开放平台 / SSO |
| API Key | 极简 | 安全性低 | 内部服务 / 第三方简单集成 |

### 面试 Q&A

> **Q:** JWT 无状态，如何实现 token 吊销？
> **A:** 三种方案：黑名单（存 Redis）、短时效 + refresh token 机制、轮换秘钥。

---

## 2. Password Hashing（密码哈希）

**绝不存储明文密码！**

### 🔴 错误示范

```java
// ⚠️ 明文存储 - 数据库泄露后所有密码暴露
user.setPassword(userRequest.getPassword());  // 危险！
```

### 🟢 正确做法：BCrypt

```java
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12); // strength factor = 12
}
```

- **strength factor** 控制计算成本，默认 10，推荐 10~12
- 每次调用 `encode()` 生成不同的哈希（内置随机 salt）
- 验证使用 `matches()`

```java
// 注册
String rawPassword = userRequest.getPassword();
String hashedPassword = passwordEncoder.encode(rawPassword);
user.setPassword(hashedPassword);
userRepository.save(user);

// 登录
boolean isValid = passwordEncoder.matches(rawPassword, storedHash);
```

### 增强：常用哈希算法对比

| 算法 | 类型 | Salt | 是否推荐 | 原因 |
|------|------|------|----------|------|
| BCrypt | 自适应 | 内置 | ✅ 推荐 | 可调强度、抗暴力破解 |
| SCrypt | 内存硬 | 内置 | ✅ 推荐 | 内存+CPU 双重困难 |
| Argon2 | 内存硬 | 内置 | ✅ 最新标准 | OWASP 首选 |
| PBKDF2 | 迭代 | 需显式 | ⚠️ 可用 | GPU 可并行，较脆弱 |
| MD5/SHA-1 | 简单 | 无 | ❌ 不要用 | 秒级破解 |
| SHA-256 | 简单 | 需显式 | ❌ 不要用 | 计算太快，暴力破解成本低 |

### 面试 Q&A

> **Q:** BCrypt 的 strength factor 是什么意思？
> **A:** 以 2^cost 次迭代计算哈希。从 10 到 11 计算时间翻倍。12 大约需要 250ms + 。作用是让暴力破解变得极慢，但用户登录验证只慢一次。

> **Q:** BCrypt 生成的哈希字符串各段含义？
> **A:** `$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy`
> - `$2a$` — 算法版本（2a/2b/2y）
> - `10$` — cost factor
> - 后 22 字符 — 随机 salt（Base64 编码）
> - 最后 31 字符 — 哈希值

---

## 3. JSON Web Tokens（JWT）

用户认证后，后端需要在每个请求中识别用户身份——**JWT 是无状态 API 的标准方案**。

### JWT 结构

```
header.payload.signature
```

- **Header** — token 类型 + 签名算法（如 `{"alg":"HS256","typ":"JWT"}`）
- **Payload** — 声明（claims）：用户 ID、角色、过期时间等
- **Signature** — 防篡改签名

### Spring Boot 3.x 中使用 jjwt 库

```java
@Component
public class JwtService {

    @Value("${jwt.secret}")
    private String secretKey;

    @Value("${jwt.expiry-ms}")
    private long expiryMs;

    public String generateToken(String username, List<String> roles) {
        return Jwts.builder()
            .subject(username)
            .claim("roles", roles)
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + expiryMs))
            .signWith(getSigningKey())
            .compact();
    }

    public Claims extractClaims(String token) {
        return Jwts.parser()
            .verifyWith(getSigningKey())
            .build()
            .parseSignedClaims(token)
            .getPayload();
    }

    private SecretKey getSigningKey() {
        byte[] keyBytes = Decoders.BASE64.decode(secretKey);
        return Keys.hmacShaKeyFor(keyBytes);
    }
}
```

### JWT 安全最佳实践

| 规则 | 说明 |
|------|------|
| ✅ 必须设置过期时间 | 短时效 token（15~30 min）更安全 |
| ✅ 使用 refresh token | 无需频繁重新登录 |
| ❌ Payload 不存敏感数据 | 仅 Base64 编码，不是加密 |
| ✅ 每个请求都验证 | JWT Filter 中检查签名 + 过期 |
| ✅ 使用 RS256（微服务） | 见下节 |

### 面试 Q&A

> **Q:** JWT 和普通 Session 有什么区别？
> **A:** Session 是服务端状态，需要存储（内存/Redis），适合单体。JWT 是自包含的，服务端无需存储，适合无状态/分布式架构。但 JWT 无法被服务端主动吊销（除非用黑名单）。

> **Q:** Refresh Token 和 Access Token 的关系？
> **A:** Access Token 短期（15~30 分钟），Refresh Token 长期（7~30 天）。Access Token 过期时用 Refresh Token 换新的。Refresh Token 需要服务端存储（通常存 Redis 并设置 TTL）。

---

## 4. 非对称加密：Public Key & Private Key

JWT 默认用 HMAC（HS256）需要一个共享密钥。**单体应用没问题，但微服务中风险很大**——十个服务共享一个密钥，任一服务被攻破就能伪造任意 token。

### 解决方案：非对称加密（RS256 / ES256）

```
┌─────────────┐         ┌──────────────┐
│ Auth Service │ ────▶  │ 微服务 A      │
│ (持有私钥)   │ 签名     │ (持有公钥)    │
│              │ 发 JWT  │ 只验证不签名  │
└─────────────┘         └──────────────┘
```

- 私钥永远不离开 Auth Service
- 所有其他微服务只用公钥验证

### 生成 RSA 密钥对

```bash
# 生成私钥（2048 位）
openssl genrsa -out private.pem 2048

# 提取公钥
openssl rsa -in private.pem -pubout -out public.pem
```

### Java 中使用 RS256 签名

```java
private RSAPrivateKey loadPrivateKey() throws Exception {
    String key = new String(Files.readAllBytes(Path.of("private.pem")))
        .replace("-----BEGIN PRIVATE KEY-----", "")
        .replace("-----END PRIVATE KEY-----", "")
        .replaceAll("\\s", "");
    byte[] decoded = Base64.getDecoder().decode(key);
    PKCS8EncodedKeySpec spec = new PKCS8EncodedKeySpec(decoded);
    return (RSAPrivateKey) KeyFactory.getInstance("RSA").generatePrivate(spec);
}

public String generateToken(String username) throws Exception {
    return Jwts.builder()
        .subject(username)
        .expiration(new Date(System.currentTimeMillis() + 900_000))  // 15 min
        .signWith(loadPrivateKey(), Jwts.SIG.RS256)
        .compact();
}
```

### 增强：HS256 vs RS256 选型

| 维度 | HS256（HMAC） | RS256（RSA） | ES256（EC） |
|------|---------------|--------------|-------------|
| 密钥类型 | 对称（一个密钥） | 非对称（公私钥） | 非对称（公私钥） |
| 性能 | ✅ 快 | ❌ 慢（3-10x） | ✅ 快 |
| 安全性 | ✅ 足够 | ✅ 强 | ✅ 强（较短的密钥等安全） |
| 密钥分发 | ❌ 需安全通道共享 | ✅ 公钥可公开分发 | ✅ 公钥可公开分发 |
| Token 大小 | ✅ 小 | ❌ 较大 | ✅ 小 |
| 适用 | 单体/内部 | 微服务/跨组织 | 微服务/移动端/JWT紧凑 |

### 面试 Q&A

> **Q:** JWT 的 Payload 能用 Base64 解码看到内容，那安全吗？
> **A:** JWT 的 Payload 只是 Base64 编码（不是加密），任何人都可以解码读取。安全靠的是签名——接收方验证签名确保 token 未被篡改。敏感数据不要放 Payload，或者对 Payload 再加密（JWE）。

---

## 5. SQL Injection 防护

SQL 注入是最古老也最危险的攻击之一——当用户输入直接拼接到 SQL 查询中时发生。

### 🔴 绝对不要这样做

```java
// ❌ 极其危险！攻击者可构造恶意输入
String query = "SELECT * FROM users WHERE email = '" + email + "'";
```

攻击者输入 `' OR '1'='1'` → 查询变为：
```sql
SELECT * FROM users WHERE email = '' OR '1'='1'
```
**直接绕过认证，返回所有用户。**

### 🟢 正确做法

```java
// Spring Data JPA — 自动参数化
Optional<User> findByEmail(String email);

// 或使用 JdbcTemplate + NamedParameter
String sql = "SELECT * FROM users WHERE email = :email";
MapSqlParameterSource params = new MapSqlParameterSource("email", email);
namedJdbcTemplate.queryForObject(sql, params, userRowMapper);
```

### 增强：各框架的 SQL 注入防护

| 框架/方式 | 是否参数化 | 说明 |
|-----------|-----------|------|
| Spring Data JPA | ✅ 自动 | 方法名查询 + @Query 自动参数化 |
| MyBatis ${} | ❌ 不 | `${}` 直接拼接，**绝对禁止** |
| MyBatis #{} | ✅ 是 | `#{}` 使用 PreparedStatement |
| JPA Native Query | ⚠️ 需参数化 | 用 `?1` 或 `:name` 参数占位 |
| JPA Entity | ✅ 自动 | 只查询已定义 entity，天然安全 |

### MyBatis 正确示范

```xml
<!-- ✅ 安全：使用 #{} -->
<select id="findByEmail" resultType="User">
    SELECT * FROM users WHERE email = #{email}
</select>

<!-- ❌ 危险：使用 ${} 直接拼接 -->
<select id="findByTableName" resultType="User">
    SELECT * FROM ${tableName}  <!-- 仅在动态表名场景谨慎使用 -->
</select>
```

### 面试 Q&A

> **Q:** MyBatis 中 `${}` 和 `#{}` 的区别？
> **A:** `#{}` 使用 PreparedStatement 参数化，自动加引号，防注入。`${}` 直接字符串替换，不防注入。`${}` 只在动态表名/列名等少数场景使用，且必须严格校验输入。

---

## 总结：Java 后端安全清单

```
□ 认证与授权分离
   - 使用 Spring Security SecurityFilterChain
   - 配置正确的访问规则 per role

□ 密码存储
   - 使用 BCryptPasswordEncoder（strength 12）
   - 绝不存明文

□ API 鉴权
   - JWT 实现无状态认证
   - 短时效 + Refresh Token
   - 微服务用 RS256 非对称签名

□ 数据查询
   - Spring Data JPA / MyBatis #{} 参数化
   - 永远不要拼接 SQL
```

> 本文是 **Part 1**，作者计划发布更多安全相关内容。

### 参考

- Original Article: [Every Java Backend Developer Should Master These Security Concepts](https://medium.com/javarevisited/every-java-backend-developer-should-master-these-security-concepts-d71e2a9082b3) by Saquib Aftab
- Spring Security Reference: https://docs.spring.io/spring-security/reference/
- JJWT Library: https://github.com/jwtk/jjwt
- OWASP Cheat Sheet: https://cheatsheetseries.owasp.org/
