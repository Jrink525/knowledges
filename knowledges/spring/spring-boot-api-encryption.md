---
title: Spring Boot API Encryption — RSA-based Auto Encrypt/Decrypt
tags: [spring, spring-boot, security, api-encryption, rsa, interview, 面试]
---

# Spring Boot API 加密：基于注解的 RSA 自动加解密方案

## 背景

API 接口数据在传输过程中面临两大风险：
- **数据泄露** — 中间人截获请求/响应明文
- **数据篡改** — 中间人修改请求/响应内容

通用解决方案：**加密**（防泄露）+ **签名**（防篡改）

## RSA 加密 vs 签名

RSA 是非对称加密：一对密钥（公钥 + 私钥）。

| 场景 | 操作 | 目的 |
|------|------|------|
| **公钥加密，私钥解密** | 发送方用接收方公钥加密，接收方用自己私钥解密 | 防**泄露** |
| **私钥签名，公钥验签** | 发送方用自己的私钥签名，接收方用发送方公钥验签 | 防**篡改** |

### 常用组合

```
A → B 发送消息
  step 1: A 用 B 的公钥加密消息       → 防泄露（只有 B 能解密）
  step 2: A 用 A 的私钥对加密结果签名  → 防篡改（B 用 A 公钥验签）
```

## 轮子：`rsa-encrypt-body-spring-boot`

Gitee 上的开源项目，通过注解自动完成 API 加解密。

### 核心依赖

```xml
<dependency>
    <groupId>cn.shuibo</groupId>
    <artifactId>rsa-encrypt-body-spring-boot</artifactId>
    <version>1.0.1.RELEASE</version>
</dependency>
```

### 启用加密

```java
@SpringBootApplication
@EnableSecurity  // 开启 RSA 加解密支持
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

### 配置密钥

```yaml
rsa:
  encrypt:
    open: true          # 是否开启加密
    showLog: true       # 打印加解密日志
    publicKey: MIIBI... # RSA 公钥（Base64）
    privateKey: MIIEv... # RSA 私钥（Base64）
```

### 响应加密：`@Encrypt`

```java
@Encrypt
@GetMapping("/encryption")
public TestBean encryption() {
    TestBean testBean = new TestBean();
    testBean.setName("shuibo.cn");
    testBean.setAge(18);
    return testBean;
}
```

返回结果自动被公钥加密为密文字符串，前端用私钥解密（注：此处逻辑是**私钥解密**，即后端用公钥加密，前端用私钥解密，需要前端持有私钥——要注意私钥分发安全问题）。

### 请求解密：`@Decrypt`

```java
@Decrypt
@PostMapping("/decryption")
public String Decryption(@RequestBody TestBean testBean) {
    return testBean.toString();
}
```

前端用公钥加密请求体，后端 `@Decrypt` 自动用私钥解密注入到 `@RequestBody` 参数。

### 前端 JS 加密（使用 jsencrypt）

```html
<script src="https://cdn.bootcdn.net/ajax/libs/jsencrypt/3.0.0-rc.1/jsencrypt.js"></script>
<script>
    var PUBLIC_KEY = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...';

    function RSA_encryption(jsonData) {
        var encrypt = new JSEncrypt();
        encrypt.setPublicKey('-----BEGIN PUBLIC KEY-----' + PUBLIC_KEY + '-----END PUBLIC KEY-----');
        return encrypt.encrypt(JSON.stringify(jsonData));
    }

    $.ajax({
        url: "/decryption",
        type: "POST",
        contentType: "application/json;charset=utf-8",
        data: RSA_encryption(str),
        success: function(data) { alert(data); }
    });
</script>
```

> 坑点 1：`contentType` 必须设为 `application/json;charset=utf-8`
> 坑点 2：`@Decrypt` 方法的参数必须有 `@RequestBody`

## 深入分析

### 加密流程

```
请求方向：
  Client (公钥加密)  ──→  Server (`@Decrypt` 私钥解密) → @RequestBody

响应方向：
  Server (`@Encrypt` 公钥加密) ──→  Client (私钥解密)
```

### 设计思路

该方案提供一个 Starter (`rsa-encrypt-body-spring-boot-starter`)，通过 Spring Boot 的自动配置 + 拦截器/过滤器/`RequestBodyAdvice`/`ResponseBodyAdvice` 机制：

1. `RequestBodyAdvice` — 拦截带有 `@Decrypt` 注解的请求，在反序列化前做 RSA 解密
2. `ResponseBodyAdvice` — 拦截带有 `@Encrypt` 注解的响应，在序列化后做 RSA 加密
3. 配置开关 `rsa.encrypt.open` 控制是否启用，便于本地开发调试

### 优缺点

| 优点 | 缺点 |
|------|------|
| 基于注解，使用简单 | RSA 加解密性能较差（不适合高频接口） |
| 配置灵活，可开关 | 前端需持有私钥（安全风险） |
| 与 Spring Boot 深度集成 | 不支持 HTTPS + 加密叠加（浪费） |
| 支持响应和请求双向 | 密钥需预分发，不支持动态轮换 |

## 替代方案 & 最佳实践

### 1. HTTPS 是基础，RSA 加密是增强

```
HTTPS (TLS) 已经提供传输层加密，绝大多数场景够用
是否需要应用层 RSA 加密？
  ├── 金融/支付类敏感接口 → YES
  ├── 内部服务间调用 → 用 mTLS 更简单
  └── 常规业务接口 → HTTPS 即可
```

### 2. AES + RSA 混合加密（推荐）

```
流程：
  Client → 生成随机 AES Key
  Client → 用 AES 加密请求体（对称加密，速度快）
  Client → 用 Server 公钥加密 AES Key
  Client → 发送 {密文, 加密后的 AES Key}
  Server → 用私钥解密出 AES Key
  Server → 用 AES Key 解密密文

优点：RSA 只加密 AES Key（短数据），正文用 AES 加密（快）
```

### 3. 使用 Spring Cloud Gateway 做统一加密层

将加密/解密逻辑下沉到网关层，业务服务无需感知。

### 4. 密钥管理

```yaml
# ❌ 不推荐：密钥写死在 yml/配置文件中
rsa:
  encrypt:
    privateKey: xxx...
    publicKey: xxx...

# ✅ 推荐：使用密钥管理服务 (Vault / KMS / 配置中心加密存储)
rsa:
  encrypt:
    privateKey: ${RSA_PRIVATE_KEY}   # 从环境变量或 Vault 注入
    publicKey: ${RSA_PUBLIC_KEY}
```

## 相关面试题

- 为什么 API 加密不能用对称加密（AES）代替 RSA？
  > 密钥分发难题。对称加密需要提前共享密钥，RSA 的非对称性解决密钥配送问题。
- HTTPS 已经加密了，为什么还需要应用层加密？
  > 防内网攻击、防中间人代理、端到端加密（HTTPS 只保传输链路，不保中间节点）。
- `@Encrypt` / `@Decrypt` 的实现原理？
  > RequestBodyAdvice + ResponseBodyAdvice 拦截注解，在序列化前后做加解密。
- 高并发下 RSA 加密有什么问题？如何优化？
  > RSA 慢（千级 TPS），用 AES + RSA 混合加密，只对 AES Key 做 RSA。
