---
title: Java Backend Security Concepts — Core Guide (CN)
category: programming/java
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

### 目录

1. 常见攻击与防御 — XSS、SQL 注入、CSRF
2. 认证机制 — Session vs JWT、Spring Security 实现
3. 授权模型 — RBAC、ACL、OAuth2 资源服务器
4. 数据保护 — HTTPS/TLS、加密算法、密码存储
5. 安全实践 — Content Security Policy、CORS、Rate Limiting

---

## 1. 常见攻击与防御

### 1.1 XSS（跨站脚本攻击）

攻击者通过输入框提交恶意代码，浏览器将其渲染执行。核心防御：输出编码 + CSP + HttpOnly Cookie。

### 1.2 SQL 注入

参数化查询（PreparedStatement / JPA @Query）是最佳防御。永远不要拼接 SQL 字符串。

### 1.3 CSRF（跨站请求伪造）

Spring Security 默认开启 CSRF 保护，POST/PUT/DELETE 要求携带 CSRF token。

---

## 2. 认证机制：Session vs JWT

Session：服务端有状态，吊销即时，需要共享存储。
JWT：无状态，天然支持分布式，吊销困难（需黑名单或短 TTL）。

Spring Security 配置示例：

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(sm -> sm.sessionCreationPolicy(STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .anyRequest().authenticated()
            );
        return http.build();
    }
}
```

---

## 3. 授权模型：RBAC vs ACL

RBAC（角色基础控制）：`@PreAuthorize("hasRole('ADMIN')")` 
ACL（访问控制列表）：细粒度控制，用户 A 可编辑订单 123 但不可编辑订单 456。

---

## 4. 数据保护

HTTPS/TLS 在 Spring Boot 中通过 `server.ssl.*` 配置。密码存储使用 BCrypt（自动加盐）。

---

## 5. 安全实践清单

CSP | CORS | Rate Limiting | Input Validation | Dependency Check | 审计日志

---

## 面试重点

Q: Session 和 JWT 怎么选？
→ 单体选 Session（简单），分布式微服务选 JWT（无状态）。

Q: @PreAuthorize 和 @Secured 的区别？
→ @Secured 只检查角色字符串，@PreAuthorize 支持 SpEL 表达式。

---

## 与知识库其他文章的关联

- **[Spring Boot API Encryption](spring/spring-boot-api-encryption.md)** — 本文中的 API 加密在 Spring Boot 中有完整的 Auto Configuration 实现。

---

*Processed on 2026-05-11 from Medium article*
