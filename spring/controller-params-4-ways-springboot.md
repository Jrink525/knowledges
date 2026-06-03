---
title: "Spring Boot Controller 接口参数及返回值 4 种获取方式 (HandlerAdapter 方案性能最佳)"
authors: ["Springboot实战案例锦集（公众号）"]
tags: ["spring-boot", "spring-mvc", "aop", "handler-adapter", "controller-advice", "filter", "requestbody-advice", "java", "web-development"]
source: "https://mp.weixin.qq.com/s/ggLthqowxHzandU1_0GlqQ"
date: 2026-06-01
---

# Spring Boot Controller 接口参数及返回值 4 种获取方式

> 在企业级开发中，对接口入参及返回值进行统一审计、加解密或日志记录是刚需。  
> 虽然 AOP 是多数开发者的首选，但面对大并发、全量流吞吐时，单一技术往往会在性能与灵活性上遭遇瓶颈。

环境：**Spring Boot 3.5.0**

---

## 四种方案横向对比

| 方案 | 原理 | 适用范围 | 性能 | 代码入侵 | 典型场景 |
|------|------|---------|:---:|:--------:|---------|
| **AOP** | @Aspect + @Around 切面拦截 | 标注了指定注解的方法 | 中等 | 低 | 请求日志、权限校验、耗时统计 |
| **Filter + Wrapper** | Servlet 容器最外层通过 ContentCachingWrapper 缓存流 | 所有 Web 请求（含静态资源） | 较高 | 低 | 全量流量日志审计、底层 HTTP 日志 |
| **Advice** | RequestBodyAdvice + ResponseBodyAdvice | **仅** @RequestBody / @ResponseBody 接口 | 较高 | 低 | 全局加解密、统一返回值包装 |
| **重写 HandlerAdapter** | 继承 RequestMappingHandlerAdapter 重写 createInvocableHandlerMethod | 所有 Controller 接口 | **最高** | 中 | 大并发全量日志、底层框架扩展 |

---

## 方案详解

### 1. 传统 AOP 方式（最常用）

**原理**：通过 `@Aspect` + `@Around` 环绕通知拦截 controller 方法。

```java
@Component
@Aspect
public class RequestAspect {
    @Pointcut("@annotation(org.springframework.web.bind.annotation.GetMapping) "
            + "|| @annotation(org.springframework.web.bind.annotation.PostMapping) "
            + "&& within(com.pack..*)")
    private void pcc() {}

    @Around("pcc()")
    public Object around(ProceedingJoinPoint pjp) throws Throwable {
        Object[] args = pjp.getArgs();
        Object ret = pjp.proceed();
        System.err.println("AOP, 请求参数: %s, 返回值: %s"
            .formatted(Arrays.toString(args), ret));
        return ret;
    }
}
```

**特点**：
- 对业务代码侵入性最低
- 但如果切入点定义不当容易遗漏接口（如例中 `@Pointcut("@annotation(mapping)")` 只匹配 GetMapping，漏掉 PostMapping）
- 需要精确控制切入点表达式

---

### 2. Filter + Wrapper 方案（最外层）

**原理**：利用 `OncePerRequestFilter` + Spring 内置的 `ContentCachingRequestWrapper` / `ContentCachingResponseWrapper` 缓存 IO 流解决"流只能读一次"的问题。

```java
@WebFilter("/api/*")
public class RequestArgFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest request,
            HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        ContentCachingRequestWrapper requestWrapper =
            new ContentCachingRequestWrapper((HttpServletRequest) request);
        ContentCachingResponseWrapper responseWrapper =
            new ContentCachingResponseWrapper((HttpServletResponse) response);
        String id = request.getParameter("id");
        try {
            filterChain.doFilter(requestWrapper, responseWrapper);
        } finally {
            String requestBody = new String(
                requestWrapper.getContentAsByteArray(),
                requestWrapper.getCharacterEncoding());
            String responseBody = new String(
                responseWrapper.getContentAsByteArray(),
                responseWrapper.getCharacterEncoding());
            System.err.println("Filter, 请求参数: %s, 返回值: %s"
                .formatted(List.of(requestBody, id), responseBody));
            responseWrapper.copyBodyToResponse();
        }
    }
}
```

**关键细节**：
- `responseWrapper.copyBodyToResponse()` **必须调用**，否则客户端收不到响应
- 位置在 Servlet 容器最外层，能捕获静态资源、Filter 抛出的异常
- 适合底层全量流量日志审计
- 但只获取原始 HTTP 字符串，不感知 Spring MVC 的反序列化结果

---

### 3. Request/Response Advice 方案（Spring MVC 内置钩子）

**原理**：同时实现 `RequestBodyAdviceAdapter`（解析前/后拦截）和 `ResponseBodyAdvice`（返回前拦截），通过 `RequestContextHolder` 跨 Advice 传递数据。

```java
@ControllerAdvice
public class RequestResponseAdvice extends RequestBodyAdviceAdapter
        implements ResponseBodyAdvice<Object> {

    @Override
    public boolean supports(MethodParameter methodParameter,
            Type targetType, Class<? extends HttpMessageConverter<?>> converterType) {
        return true;
    }

    @Override
    public boolean supports(MethodParameter returnType,
            Class<? extends HttpMessageConverter<?>> converterType) {
        return true;
    }

    @Override
    public HttpInputMessage beforeBodyRead(HttpInputMessage inputMessage,
            MethodParameter parameter, Type targetType,
            Class<? extends HttpMessageConverter<?>> converterType) throws IOException {
        String body = StreamUtils.copyToString(inputMessage.getBody(),
            StandardCharsets.UTF_8);
        HttpInputMessage finalInputMessage = new HttpInputMessage() {
            public HttpHeaders getHeaders() { return inputMessage.getHeaders(); }
            public InputStream getBody() {
                return new ByteArrayInputStream(body.getBytes(StandardCharsets.UTF_8));
            }
        };
        ServletRequestAttributes attrs = (ServletRequestAttributes)
            RequestContextHolder.getRequestAttributes();
        attrs.getRequest().setAttribute("req_body", body);
        return super.beforeBodyRead(finalInputMessage, parameter, targetType, converterType);
    }

    @Override
    public Object beforeBodyWrite(Object body, MethodParameter returnType,
            MediaType selectedContentType,
            Class<? extends HttpMessageConverter<?>> selectedConverterType,
            ServerHttpRequest request, ServerHttpResponse response) {
        ServletRequestAttributes attrs = (ServletRequestAttributes)
            RequestContextHolder.getRequestAttributes();
        String reqBody = (String) attrs.getRequest().getAttribute("req_body");
        System.err.println("Advice, 请求参数: %s, 返回值: %s"
            .formatted(reqBody, body));
        return body;
    }
}
```

**优势**：这是专门为 RequestBody 解析/ResponseBody 返回设计的拦截点，适合全局参数加解密、统一返回值包装。

**限制**：**仅对 @RequestBody / @ResponseBody（含 @RestController）的接口生效**。传统的 Form 表单调、QueryParam 无法获取。

---

### 4. 重写底层 HandlerAdapter（性能最佳 ⭐）

**原理**：继承 `RequestMappingHandlerAdapter`，重写 `createInvocableHandlerMethod` 返回自定义的 `ServletInvocableHandlerMethod` 子类，在 `doInvoke` 方法中获取完整的参数和返回值。

```java
public class RequestArgsHandlerAdapter extends RequestMappingHandlerAdapter {
    @Override
    protected ServletInvocableHandlerMethod createInvocableHandlerMethod(
            HandlerMethod handlerMethod) {
        return new ArgsInvocationHandler(handlerMethod);
    }

    private static class ArgsInvocationHandler extends ServletInvocableHandlerMethod {
        public ArgsInvocationHandler(HandlerMethod handlerMethod) {
            super(handlerMethod);
        }

        @Override
        protected Object doInvoke(Object... args) throws Exception {
            Object ret = super.doInvoke(args);
            System.err.println("HandlerAdapter, 请求参数: %s, 返回值: %s"
                .formatted(Arrays.toString(args), ret));
            return ret;
        }
    }
}
```

**注册方式**（替换默认 HandlerAdapter）：
```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void configureHandlerAdapters(
            List<HandlerMapping> handlerMappings) {
        // 替换默认的 RequestMappingHandlerAdapter
    }
}
```

**为什么性能最佳**：
- AOP 通过代理生成拦截器链（CGLIB/JDK Proxy），每次调用都有方法分派开销
- Filter 依赖 Servlet 容器级包装（Wrapper），涉及流的拷贝
- Advice 涉及两次反序列化 + RequestContextHolder 跨组件传递
- HandlerAdapter 直接插入 Spring MVC 的调用链，**只在真正调用方法的前后插入逻辑，不修改底层行为**，零额外代理开销

**覆盖范围**：所有 Controller 接口（无需区分 GetMapping/PostMapping、@RequestBody/QueryParam）

---

## 方案选择指南

```
简单日志、小并发 → AOP（零侵入，够用）
全量流量审计     → Filter + Wrapper（最底层，完整 HTTP 信息）
全局加解密       → RequestBodyAdvice（天然设计为此而生）
大并发全量日志   → 重写 HandlerAdapter（性能最优）
```

---

## 相比 AI Agent 上下文的视角

这篇文章虽然是传统 Spring Boot 开发技巧，但其核心问题——**如何在框架的调用链中拦截和增强请求/响应**——与 Agent Harness 中"如何在 harness 的上下文窗口边界拦截和持久化信息"本质上是同一类问题：

- AOP ≈ Agent 的 middleware 拦截（中间件链）
- Filter ≈ Agent 的 harness 最外层入口（raw requests/响应）
- Advice ≈ Agent 的 message interceptor（按类型的拦截钩子）
- **重写 HandlerAdapter ≈ Agent 框架的底层 SPI 扩展点**（性能最高，直接插入调用栈）

这也是 Agent Harness 设计中需要反复面对的模式：**拦截位置决定性能上限和适用边界**。

---

## 相关技巧

- `responseWrapper.copyBodyToResponse()` 是 Filter 方案中**最容易忘的坑**（不调用客户端收不到响应体）
- `RequestContextHolder` 在不同线程间传递 request 属性是跨 Advice 传递数据的关键
- AOP 切入点表达式用 `||` 组合多注解时，注意 `within()` 的包过滤范围
- 重写 HandlerAdapter 时需确保是**唯一实现**，或通过 order 控制优先级，避免多个 HandlerAdapter 冲突
