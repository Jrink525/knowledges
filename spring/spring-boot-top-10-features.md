---
title: Spring Boot 实践中最有价值的10个核心功能
tags: [spring, spring-boot, core, exception-handling, interceptor, bean-lifecycle, scope, 来源:公众号]
category: spring/core
source: https://mp.weixin.qq.com/s/hrwZTGiAj9kvKNRYtwD76w
date: 2026-05-21
---

# Spring Boot 实践中最有价值的10个核心功能

> **环境：** Spring Boot 3.5.0
> **来源：** Spring Boot 3实战案例锦集

---

## 目录

1. [全局异常处理](#1-全局异常处理)
2. [拦截器](#2-拦截器)
3. [获取容器对象](#3-获取容器对象)
4. [导入配置（@Import）](#4-导入配置import)
5. [应用启动时附加功能](#5-应用启动时附加功能)
6. [修改 BeanDefinition](#6-修改-beandefinition)
7. [Bean 初始化方法](#7-bean-初始化方法)
8. [Bean 初始化前后添加逻辑](#8-bean-初始化前后添加逻辑)
9. [容器关闭时给 Bean 添加回调方法](#9-容器关闭时给-bean-添加回调方法)
10. [自定义作用域](#10-自定义作用域)

---

## 1. 全局异常处理

### 问题

未做异常处理时，系统抛出原始异常会直接暴露给用户，体验极差：

```java
@GetMapping("/users/{id}")
public User getUser(@PathVariable Long id) {
    return userRepository.findById(id).orElseThrow();
    // 抛出 NoSuchElementException → 500 + 堆栈信息 → 用户懵逼
}
```

### 方案：@RestControllerAdvice + @ExceptionHandler

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(NoSuchElementException.class)
    public Result<Void> handleNotFound(NoSuchElementException e) {
        return Result.error(404, "数据不存在");
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result<Void> handleValidation(MethodArgumentNotValidException e) {
        String msg = e.getBindingResult().getFieldErrors().stream()
                .map(f -> f.getField() + ": " + f.getDefaultMessage())
                .collect(Collectors.joining("; "));
        return Result.error(400, msg);
    }

    @ExceptionHandler(Exception.class)
    public Result<Void> handleException(Exception e) {
        log.error("未知异常", e);
        return Result.error(500, "服务内部异常");
    }
}
```

### 🚀 增强：统一响应体 + 国际化

```java
@RestControllerAdvice
public class EnhancedGlobalExceptionHandler {

    private final MessageSource messageSource;

    // ====== 通用异常 ======

    @ExceptionHandler(ResourceNotFoundException.class)
    public Result<Void> handleResourceNotFound(ResourceNotFoundException e) {
        return Result.error(HttpStatus.NOT_FOUND.value(), e.getMessage());
    }

    @ExceptionHandler(BadRequestException.class)
    public Result<Void> handleBadRequest(BadRequestException e) {
        return Result.error(HttpStatus.BAD_REQUEST.value(), e.getMessage());
    }

    @ExceptionHandler(AccessDeniedException.class)
    public Result<Void> handleAccessDenied(AccessDeniedException e) {
        return Result.error(HttpStatus.FORBIDDEN.value(), "权限不足");
    }

    // ====== 参数校验 ======

    @ExceptionHandler(ConstraintViolationException.class)
    public Result<Void> handleConstraintViolation(ConstraintViolationException e) {
        String msg = e.getConstraintViolations().stream()
                .map(v -> v.getPropertyPath() + ": " + v.getMessage())
                .collect(Collectors.joining("; "));
        return Result.error(400, msg);
    }

    @ExceptionHandler(BindException.class)
    public Result<Void> handleBind(BindException e) {
        String msg = e.getFieldErrors().stream()
                .map(f -> f.getField() + "=" + f.getRejectedValue() + ": " + f.getDefaultMessage())
                .collect(Collectors.joining("; "));
        return Result.error(400, msg);
    }

    // ====== 数据访问 ======

    @ExceptionHandler(DataIntegrityViolationException.class)
    public Result<Void> handleDataIntegrity(DataIntegrityViolationException e) {
        return Result.error(409, "数据冲突，违反唯一约束");
    }

    // ====== 兜底 ======

    @ExceptionHandler(Exception.class)
    public Result<Void> handleUnknown(Exception e, HttpServletRequest request) {
        String errorId = UUID.randomUUID().toString().substring(0, 8);
        log.error("[{}] 请求 {} {} 异常", errorId, request.getMethod(), request.getRequestURI(), e);
        return Result.error(500, "系统异常，错误编号: " + errorId);
    }
}
```

---

## 2. 拦截器

Spring MVC 拦截器顶层接口 `HandlerInterceptor`，三个核心方法：

| 方法 | 执行时机 | 典型用途 |
|------|---------|---------|
| `preHandle` | Controller 方法执行前 | 权限校验、Token 验证 |
| `postHandle` | 方法执行后、视图渲染前 | 修改响应/添加公共数据 |
| `afterCompletion` | 请求完成（视图渲染后） | 请求耗时统计、资源清理 |

### 定义拦截器

```java
public class CustomInterceptor implements HandlerInterceptor {

    private static final Logger log = LoggerFactory.getLogger(CustomInterceptor.class);

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response,
                             Object handler) {
        // 权限校验逻辑（如检查 Token）
        String token = request.getHeader("Authorization");
        if (token == null || !token.startsWith("Bearer ")) {
            response.setStatus(401);
            return false; // 中断请求
        }
        return true;
    }

    @Override
    public void postHandle(HttpServletRequest request, HttpServletResponse response,
                           Object handler, ModelAndView modelAndView) {
        // 添加公共数据到 Model
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response,
                                Object handler, Exception ex) {
        // 记录请求耗时
    }
}
```

### 注册拦截器

```java
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

    private final CustomInterceptor customInterceptor;

    public WebMvcConfig(CustomInterceptor customInterceptor) {
        this.customInterceptor = customInterceptor;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(customInterceptor)
                .addPathPatterns("/api/**")
                .excludePathPatterns("/api/auth/**", "/api/public/**");
    }
}
```

### 🚀 增强：请求耗时统计拦截器

```java
@Component
public class TimeCostInterceptor implements HandlerInterceptor {

    private static final String START_TIME_ATTR = "_startTime";

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response,
                             Object handler) {
        request.setAttribute(START_TIME_ATTR, System.nanoTime());
        return true;
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response,
                                Object handler, Exception ex) {
        Long startTime = (Long) request.getAttribute(START_TIME_ATTR);
        if (startTime != null) {
            long costMs = (System.nanoTime() - startTime) / 1_000_000;
            String method = request.getMethod();
            String uri = request.getRequestURI();
            int status = response.getStatus();
            if (costMs > 1000) {
                log.warn("[慢请求] {} {} → {} ({}ms)", method, uri, status, costMs);
            }
            // 可将耗时持久化到日志系统 / Prometheus / ES
        }
    }
}
```

---

## 3. 获取容器对象

### 方式一：实现 Aware 接口

```java
@Component
public class CommonComponent implements ApplicationContextAware {
    private ApplicationContext context;

    @Override
    public void setApplicationContext(ApplicationContext context) {
        this.context = context;
    }

    public <T> T getBean(String name, Class<T> requiredType) {
        return context.getBean(name, requiredType);
    }
}
```

### 方式二：构造函数注入（推荐）

```java
@Component
public class CommonComponent {
    private final ApplicationContext context;

    public CommonComponent(ApplicationContext context) {
        this.context = context;
    }
}
```

> ⚠️ 尽量避免在业务代码中直接获取容器，这会破坏 IoC 风格。仅在**框架级组件**（如自定义 Starter）需要动态获取 Bean 时使用。

---

## 4. 导入配置（@Import）

@Import 支持 4 种导入方式：

| 方式 | 说明 | 适用场景 |
|------|------|---------|
| 导入普通类 | 直接注册为 Bean | 引入无注解的第三方类 |
| 导入 @Configuration 类 | 递归引入其所有相关注解 | 引入完整配置模块 |
| ImportSelector | 编程式返回类名数组 | 条件化引入多个类 |
| ImportBeanDefinitionRegistrar | 自定义注册 BeanDefinition | 需要精细控制 Bean 定义 |

### 示例：ImportSelector

```java
public class LogAspectSelector implements ImportSelector {
    @Override
    public String[] selectImports(AnnotationMetadata metadata) {
        boolean enabled = metadata.getAnnotationAttributes(EnableLog.class.getName())
                .get("enabled").equals(true);
        return enabled ? new String[]{"com.example.LogAspect"} : new String[0];
    }
}
```

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Import(LogAspectSelector.class)
public @interface EnableLog {
    boolean enabled() default true;
}
```

---

## 5. 应用启动时附加功能

Spring Boot 提供两个启动回调接口：

```java
@Component
public class StartupRunner implements CommandLineRunner {
    @Override
    public void run(String... args) {
        System.out.println("以 main 方法参数启动：" + Arrays.toString(args));
    }
}
```

```java
@Component
public class AppRunner implements ApplicationRunner {
    @Override
    public void run(ApplicationArguments args) {
        System.out.println("选项参数: " + args.getOptionNames());
        System.out.println("非选项参数: " + args.getNonOptionArgs());
    }
}
```

> `ApplicationRunner` 优于 `CommandLineRunner`，因为能区分选项参数（`--key=value`）和非选项参数。

### 🚀 增强：带 Order 的批量初始化

```java
@Component
@Order(1)
public class CacheWarmer implements CommandLineRunner {
    @Override
    public void run(String... args) {
        log.info("预热热门数据缓存...");
        // cacheService.warmUp(Arrays.asList("hot-keys"));
    }
}

@Component
@Order(2)
public class SystemConfigLoader implements CommandLineRunner {
    @Override
    public void run(String... args) {
        log.info("加载系统配置到内存...");
    }
}
```

---

## 6. 修改 BeanDefinition

在 Bean 实例化前，通过 `BeanFactoryPostProcessor` 修改 Bean 定义：

```java
@Component
public class MyBeanFactoryPostProcessor implements BeanFactoryPostProcessor {
    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) {
        DefaultListableBeanFactory df = (DefaultListableBeanFactory) beanFactory;
        BeanDefinition bd = df.getBeanDefinition("commonComponent");
        bd.getPropertyValues().addPropertyValue("name", "pack_xg");
    }
}
```

---

## 7. Bean 初始化方法

```java
// 方式一：@PostConstruct（推荐）
@Service
public class AService {
    @PostConstruct
    public void init() {
        System.out.println("init...");
    }
}

// 方式二：InitializingBean
@Service
public class BService implements InitializingBean {
    @Override
    public void afterPropertiesSet() {
        System.out.println("init...");
    }
}
```

> `@PostConstruct` 优先于 `InitializingBean`。两者结合时执行顺序：`@PostConstruct` → `InitializingBean.afterPropertiesSet()` → 自定义 `init-method`。

---

## 8. Bean 初始化前后添加逻辑

```java
@Component
public class MyBeanPostProcessor implements BeanPostProcessor {
    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) {
        if (bean instanceof User) {
            log.info("User Bean 初始化前: {}", beanName);
        }
        return bean;
    }

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) {
        if (bean instanceof User) {
            ((User) bean).setName("pack_xg");
        }
        return bean;
    }
}
```

---

## 9. 容器关闭时给 Bean 添加回调方法

```java
// 方式一：@PreDestroy（推荐）
@Service
public class DService {
    @PreDestroy
    public void close() {
        System.out.println("释放资源...");
    }
}

// 方式二：DisposableBean
@Service
public class EService implements DisposableBean {
    @Override
    public void destroy() {
        System.out.println("DisposableBean destroy");
    }
}
```

---

## 10. 自定义作用域

### Spring Boot 默认作用域

| 作用域 | 说明 |
|--------|------|
| singleton | 默认，每个容器一个实例 |
| prototype | 每次获取创建新实例 |
| request | 每个 HTTP 请求一个实例 |
| session | 每个 HTTP Session 一个实例 |
| application | ServletContext 生命周期 |
| websocket | WebSocket 生命周期 |

### 自定义：ThreadLocal 作用域

```java
public class ThreadLocalScope implements Scope {
    private final ThreadLocal<Map<String, Object>> threadScope =
            ThreadLocal.withInitial(HashMap::new);

    @Override
    public Object get(String name, ObjectFactory<?> objectFactory) {
        Map<String, Object> scope = threadScope.get();
        return scope.computeIfAbsent(name, k -> objectFactory.getObject());
    }

    @Override
    public Object remove(String name) {
        return threadScope.get().remove(name);
    }

    @Override
    public void registerDestructionCallback(String name, Runnable callback) {
        // Web 应用需要时实现
    }

    @Override
    public Object resolveContextualObject(String key) {
        return null;
    }

    @Override
    public String getConversationId() {
        return Thread.currentThread().getName();
    }
}
```

### 注册 & 使用

```java
@Component
public class ScopeRegistrar implements BeanFactoryPostProcessor {
    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) {
        beanFactory.registerScope("thread", new ThreadLocalScope());
    }
}

@Scope("thread")
@Service
public class RequestContextService {
    // 同一线程内始终是同一个实例
}
```

---

*本文整理自公众号「Springboot实战案例锦集」，代码经增强和补充注释。*
