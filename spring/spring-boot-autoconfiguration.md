---
title: Spring Boot Auto-Configuration Principle
tags: [spring, spring-boot, framework, interview, 面试]
---

# Spring Boot Auto-Configuration 原理

## 核心注解：`@SpringBootApplication`

```java
@SpringBootApplication  // 组合了以下三个注解
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

等价于：
```java
@Configuration
@EnableAutoConfiguration
@ComponentScan
```

## 自动配置入口：`@EnableAutoConfiguration`

```java
@Import(AutoConfigurationImportSelector.class)
public @interface EnableAutoConfiguration {}
```

关键方法 `AutoConfigurationImportSelector#selectImports()`:

```
SpringFactoriesLoader.loadFactoryNames(EnableAutoConfiguration.class, classLoader)
  → 读取 META-INF/spring.factories
  → 返回所有 EnableAutoConfiguration 全限定类名
  → 按 @Conditional 条件过滤
  → 只加载条件匹配的配置类
```

## 条件过滤：`@Conditional` 体系

| 注解 | 生效条件 |
|------|---------|
| `@ConditionalOnClass` | classpath 存在指定类 |
| `@ConditionalOnMissingClass` | classpath 不存在指定类 |
| `@ConditionalOnBean` | 容器已有指定 Bean |
| `@ConditionalOnMissingBean` | 容器没有指定 Bean |
| `@ConditionalOnProperty` | 配置项存在 |
| `@ConditionalOnExpression` | SpEL 表达式为 true |
| `@ConditionalOnWebApplication` | 当前是 Web 应用 |

### 示例：Redis 自动配置

```java
@Configuration
@ConditionalOnClass(RedisOperations.class)      // 有 Jedis/Lettuce
@EnableConfigurationProperties(RedisProperties.class)
public class RedisAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean(StringRedisTemplate.class)
    public StringRedisTemplate stringRedisTemplate(RedisConnectionFactory factory) {
        return new StringRedisTemplate(factory);
    }
}
```

## 自动配置覆盖优先级

```
@Bean 手动配置 > spring.factories 自动配置
```

## 启动流程

```
SpringApplication.run()
  → 确定 Web 类型（Servlet/Reactive/None）
  → 加载 ApplicationContextInitializer + ApplicationListener
  → 准备 Environment（application.properties/yml）
  → 创建 ApplicationContext
  → 执行 AutoConfigurationImportSelector
    → 加载 spring.factories
    → @Conditional 过滤
    → 排序（@AutoConfigureOrder, @AutoConfigureBefore/After）
    → 注册 BeanDefinition
  → 刷新容器
```

## 自定义 Starter

```java
// 1. 配置类
@Configuration
@ConditionalOnClass(MyService.class)
@EnableConfigurationProperties(MyProperties.class)
public class MyAutoConfiguration {
    @Bean
    @ConditionalOnMissingBean
    public MyService myService(MyProperties props) {
        return new MyService(props.getUrl());
    }
}

// 2. spring.factories
// META-INF/spring.factories:
// org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
//   com.example.MyAutoConfiguration

// 3. 属性绑定
@ConfigurationProperties(prefix = "my.service")
public class MyProperties { ... }
```

## 相关面试题

- Spring Boot 如何自动装配？和 Spring XML 方式的区别？
- 如何调试自动配置为什么不生效？(debug=true)
- 怎么自定义一个 Starter？
