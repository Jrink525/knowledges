---
title: "Spring Controller 返回类型完全指南：从入门到源码解析"
tags:
  - spring
  - spring-mvc
  - controller
  - responseentity
  - responsebody
  - async
  - streaming
  - sse
date: 2026-05-28
source: "综合整理自 mp.weixin.qq.com, dev.to, Medium, Spring Framework 官方文档"
---

# Spring Controller 返回类型完全指南：从入门到源码解析

---

## 目录

- [第一章：基石篇 — 最常用的 3 种返回方式](#第一章基石篇--最常用的-3-种返回方式)
  - [1.1 @ResponseBody + POJO — 自动 JSON 序列化](#11-responsebody--pojo--自动-json-序列化)
  - [1.2 ResponseEntity — 完全控制 HTTP 响应](#12-responseentity--完全控制-http-响应)
  - [1.3 @RestController — 全注解简化](#13-restcontroller--全注解简化)
- [第二章：传统 Web 应用篇](#第二章传统-web-应用篇)
  - [2.1 String — 视图名解析](#21-string--视图名解析)
  - [2.2 ModelAndView — 模型+视图](#22-modelandview--模型视图)
  - [2.3 Map/Model — 隐式视图 + 模型属性](#23-mapmodel--隐式视图--模型属性)
  - [2.4 void — 无返回值](#24-void--无返回值)
  - [2.5 View — 直接返回 View 对象](#25-view--直接返回-view-对象)
- [第三章：精细化控制篇](#第三章精细化控制篇)
  - [3.1 HttpEntity](#31-httpentity)
  - [3.2 HttpHeaders — 只返回头](#32-httpheaders--只返回头)
  - [3.3 @ModelAttribute — 模型属性注入](#33-modelattribute--模型属性注入)
  - [3.4 ErrorResponse / ProblemDetail — RFC 9457 错误响应](#34-errorresponse--problemdetail--rfc-9457-错误响应)
  - [3.5 FragmentsRendering — HTML 片段渲染](#35-fragmentsrendering--html-片段渲染)
  - [3.6 其他返回类型 — 兜底规则](#36-其他返回类型--兜底规则)
- [第四章：异步篇](#第四章异步篇)
  - [4.1 DeferredResult — 异步结果的基石](#41-deferredresult--异步结果的基石)
  - [4.2 Callable — Spring 托管的异步](#42-callable--spring-托管的异步)
  - [4.3 CompletableFuture / CompletionStage — 现代异步](#43-completablefuture--completionstage--现代异步)
- [第五章：流式响应篇](#第五章流式响应篇)
  - [5.1 ResponseBodyEmitter — 对象流](#51-responsebodyemitter--对象流)
  - [5.2 SseEmitter — 服务端推送（SSE）](#52-sseemitter--服务端推送sse)
  - [5.3 StreamingResponseBody — 原生流输出](#53-streamingresponsebody--原生流输出)
- [第六章：响应式编程篇（WebFlux）](#第六章响应式编程篇webflux)
  - [6.1 Mono — 单值响应](#61-mono--单值响应)
  - [6.2 Flux — 多值流](#62-flux--多值流)
  - [6.3 背压机制](#63-背压机制)
- [第七章：资源与文件下载篇](#第七章资源与文件下载篇)
  - [7.1 Resource — 文件下载](#71-resource--文件下载)
  - [7.2 byte[] — 原始字节](#72-byte--原始字节)
- [第八章：底层原理剖析](#第八章底层原理剖析)
  - [8.1 RequestMappingHandlerAdapter 处理流程](#81-requestmappinghandleradapter-处理流程)
  - [8.2 HttpMessageConverter 机制](#82-httpmessageconverter-机制)
  - [8.3 AbstractMessageConverterMethodProcessor](#83-abstractmessageconvertermethodprocessor)
  - [8.4 异步请求处理全过程](#84-异步请求处理全过程)
- [第九章：生产实践](#第九章生产实践)
  - [9.1 统一响应格式封装](#91-统一响应格式封装)
  - [9.2 全局异常处理 + ProblemDetail](#92-全局异常处理--problemdetail)
  - [9.3 响应类型选择树](#93-响应类型选择树)
  - [9.4 反模式清单](#94-反模式清单)

---

# 第一章：基石篇 — 最常用的 3 种返回方式

## 1.1 @ResponseBody + POJO — 自动 JSON 序列化

### 使用方式

```java
@Controller
@RequestMapping("/api/users")
public class UserController {

    @GetMapping("/{id}")
    @ResponseBody
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
    }

    @GetMapping
    @ResponseBody
    public List<User> getAllUsers() {
        return userService.findAll();
    }

    @GetMapping("/count")
    @ResponseBody
    public long getUserCount() {
        return userService.count();
    }

    @GetMapping("/message")
    @ResponseBody
    public String getMessage() {
        return "Hello World";
    }
}
```

### 返回结果

```json
// GET /api/users/123
{
  "id": 123,
  "name": "张三",
  "email": "zhangsan@example.com"
}
```

### 处理流程（底层）

```
1. 请求到达 DispatcherServlet
       ↓
2. HandlerAdapter 找到 UserController.getUser()
       ↓
3. 方法执行，返回 User 对象
       ↓
4. @ResponseBody 注解触发 StringHttpMessageConverter / MappingJackson2HttpMessageConverter
       ↓
5. Jackson 将 User 序列化为 JSON
       ↓
6. 设置 Content-Type: application/json，状态码 200
       ↓
7. 写入 HttpResponse 输出流
```

### 关键源码解析

```java
// RequestMappingHandlerAdapter 中处理 @ResponseBody 的核心代码：
// 使用 RequestResponseBodyMethodProcessor 作为返回值处理器

// RequestResponseBodyMethodProcessor.java (Spring 6.x)
public class RequestResponseBodyMethodProcessor
        extends AbstractMessageConverterMethodProcessor {

    @Override
    public boolean supportsReturnType(MethodParameter returnType) {
        // 检查方法是否有 @ResponseBody 注解
        // 或者类级别有 @RestController 注解
        return (AnnotatedElementUtils.hasAnnotation(
                returnType.getContainingClass(), ResponseBody.class) ||
                returnType.hasMethodAnnotation(ResponseBody.class));
    }

    @Override
    public void handleReturnValue(Object returnValue,
            MethodParameter returnType, ModelAndViewContainer mavContainer,
            NativeWebRequest webRequest) throws Exception {

        mavContainer.setRequestHandled(true);  // 标记：不再解析视图

        // 创建消息转换输入
        ServletServerHttpResponse outputMessage = createOutputMessage(webRequest);

        // 写入响应体 — 核心在这里
        writeWithMessageConverters(returnValue, returnType, outputMessage);
    }
}
```

### 优缺点

| 优点 | 缺点 |
|------|------|
| ✅ 代码最简洁 | ❌ 状态码固定 200 |
| ✅ Spring 自动序列化 | ❌ 无法设置自定义 Header |
| ✅ 零配置 | ❌ 异常场景难以精细控制 |

---

## 1.2 ResponseEntity — 完全控制 HTTP 响应

### 使用方式

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    // 完整控制状态码、Header、Body
    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        return userService.findById(id)
            .map(user -> ResponseEntity.ok()
                .header("X-Response-Time", String.valueOf(System.currentTimeMillis()))
                .body(user))
            .orElse(ResponseEntity.notFound().build());
    }

    // 201 Created + Location Header
    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody User user) {
        User created = userService.save(user);
        URI location = ServletUriComponentsBuilder
            .fromCurrentRequest()
            .path("/{id}")
            .buildAndExpand(created.getId())
            .toUri();
        return ResponseEntity.created(location).body(created);
    }

    // 204 No Content
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        if (!userService.exists(id)) {
            return ResponseEntity.notFound().build();
        }
        userService.delete(id);
        return ResponseEntity.noContent().build();  // 204
    }

    // 自定义状态码 + Header + Body
    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(@PathVariable Long id, @RequestBody User user) {
        // ...
        return ResponseEntity
            .status(HttpStatus.ACCEPTED)
            .header("X-Audit-Trace", UUID.randomUUID().toString())
            .body(updated);
    }
}
```

### 类层次结构

```
java.lang.Object
 └── org.springframework.http.HttpEntity<T>           ← 基础类：headers + body
      └── org.springframework.http.RequestEntity<T>    ← HTTP 请求：method + URI + headers + body
      └── org.springframework.http.ResponseEntity<T>   ← HTTP 响应：status + headers + body
```

### 核心源码

```java
// ResponseEntity.java (简化版)
public class ResponseEntity<T> extends HttpEntity<T> {

    private final HttpStatusCode status;

    public ResponseEntity(T body, HttpHeaders headers, HttpStatusCode status) {
        super(body, headers);
        this.status = status;
    }

    // 静态工厂方法（推荐使用）
    public static BodyBuilder ok() { return status(HttpStatus.OK); }

    public static <T> ResponseEntity<T> ok(T body) {
        return ok().body(body);
    }

    public static BodyBuilder created(URI location) {
        return status(HttpStatus.CREATED).location(location);
    }

    public static BodyBuilder noContent() {
        return status(HttpStatus.NO_CONTENT);
    }

    // 泛型通配符风格
    public static BodyBuilder status(HttpStatusCode status) {
        return new DefaultBuilder(status);
    }

    // ResponseEntity.BodyBuilder 内部接口
    public interface BodyBuilder extends HeadersBuilder<BodyBuilder> {
        <T> ResponseEntity<T> body(T body);
    }
}
```

### Spring 处理 ResponseEntity 的流程

```java
// HttpEntityMethodProcessor.java
public class HttpEntityMethodProcessor
        extends AbstractMessageConverterMethodProcessor {

    @Override
    public boolean supportsReturnType(MethodParameter returnType) {
        // 处理 HttpEntity / ResponseEntity 返回值
        return HttpEntity.class.isAssignableFrom(
            returnType.getParameterType());
    }

    @Override
    public void handleReturnValue(Object returnValue, ...) {

        HttpEntity<?> httpEntity = (HttpEntity<?>) returnValue;
        mavContainer.setRequestHandled(true);

        // 1. 提取 HTTP 状态码（ResponseEntity 特有）
        if (httpEntity instanceof ResponseEntity) {
            int statusCode = ((ResponseEntity<?>) httpEntity).getStatusCodeValue();
            servletResponse.setStatus(statusCode);
        }

        // 2. 写入响应头
        HttpHeaders entityHeaders = httpEntity.getHeaders();
        if (entityHeaders != null) {
            for (Map.Entry<String, List<String>> entry : entityHeaders.entrySet()) {
                String headerName = entry.getKey();
                for (String headerValue : entry.getValue()) {
                    servletResponse.addHeader(headerName, headerValue);
                }
            }
        }

        // 3. 写入响应体（如果有）
        if (httpEntity.getBody() != null) {
            writeWithMessageConverters(httpEntity.getBody(), returnType,
                createOutputMessage(webRequest));
        }
    }
}
```

---

## 1.3 @RestController — 全注解简化

```java
// @RestController = @Controller + @ResponseBody
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Controller
@ResponseBody
public @interface RestController {

    @AliasFor(annotation = Controller.class)
    String value() default "";
}
```

**所有方法默认带 @ResponseBody 语义**，相当于传统模式下每个方法都加 `@ResponseBody`。

---

# 第二章：传统 Web 应用篇

> 以下返回类型适用于服务端渲染（Thymeleaf / JSP / Freemarker）场景

## 2.1 String — 视图名解析

### 使用方式

```java
// 注意：必须是 @Controller，而不是 @RestController
// 因为在 @RestController 下，String 会被当作 JSON 字符串序列化

@Controller
@RequestMapping("/web")
public class WebController {

    @GetMapping("/home")
    public String home(Model model) {
        model.addAttribute("message", "欢迎光临");
        model.addAttribute("today", LocalDate.now());
        return "home";  // 解析为 /templates/home.html (Thymeleaf)
    }

    // 重定向：redirect: 前缀
    @GetMapping("/old-path")
    public String redirect() {
        return "redirect:/web/home";
    }

    // 转发：forward: 前缀
    @GetMapping("/legacy")
    public String forward() {
        return "forward:/web/home";
    }
}
```

### 处理流程

```
1. String "home" 返回
       ↓
2. ViewResolver 开始工作
       ↓
3. InternalResourceViewResolver / ThymeleafViewResolver
       ↓
4. 拼接前缀后缀：/templates/home.html
       ↓
5. 解析模板，合并 Model 数据
       ↓
6. 返回 HTML 页面
```

### 源码解析

```java
// ViewNameMethodReturnValueHandler.java
public class ViewNameMethodReturnValueHandler implements HandlerMethodReturnValueHandler {

    @Override
    public boolean supportsReturnType(MethodParameter returnType) {
        // 处理 String 类型返回值（且没有 @ResponseBody）
        return CharSequence.class.isAssignableFrom(returnType.getParameterType());
    }

    @Override
    public void handleReturnValue(Object returnValue,
            MethodParameter returnType, ModelAndViewContainer mavContainer,
            NativeWebRequest webRequest) throws Exception {

        if (returnValue instanceof CharSequence) {
            // 把 String 设置为 view name
            mavContainer.setViewName(returnValue.toString());
        }
        // 注意这里不设置 setRequestHandled(true)
        // DispatcherServlet 会继续执行视图解析
    }
}
```

> **关键区别**：String 作为视图名返回时，`mavContainer.setRequestHandled(false)`（默认值），  
> DispatcherServlet 会继续执行 ViewResolver 解析；  
> 而 @ResponseBody + String 返回时，`mavContainer.setRequestHandled(true)`，跳过视图解析。

---

## 2.2 ModelAndView — 模型+视图

> ModelAndView 是传统 Spring MVC 时代的"完全体"返回类型，一次性包含视图名和数据。

### 使用方式

```java
@Controller
public class ProductController {

    @GetMapping("/products")
    public ModelAndView getProducts() {
        ModelAndView mav = new ModelAndView();
        mav.setViewName("products");  // 视图名
        mav.addObject("products", productService.findAll());
        mav.addObject("total", productService.count());
        return mav;
    }

    // 更简洁的写法
    @GetMapping("/product/{id}")
    public ModelAndView getProduct(@PathVariable Long id) {
        return new ModelAndView("product-detail", "product",
            productService.findById(id));
    }

    // 带状态码（虽然 REST 中用 ResponseEntity 更好）
    @GetMapping("/error-page")
    public ModelAndView error() {
        ModelAndView mav = new ModelAndView("error");
        mav.setStatus(HttpStatus.INTERNAL_SERVER_ERROR);
        mav.addObject("code", 500);
        return mav;
    }
}
```

### 核心源码

```java
// ModelAndView.java
public class ModelAndView {

    /** View 实例或视图名 */
    private Object view;

    /** 模型数据 */
    private ModelMap model;

    /** 可选的状态码 */
    private HttpStatus status;

    /** 是否已清空 */
    private boolean cleared = false;

    public ModelAndView() {
        // 空的 ModelAndView，后续通过 setter 设置
    }

    public ModelAndView(String viewName) {
        this.view = viewName;
    }

    public ModelAndView(String viewName, String modelName, Object modelObject) {
        this.view = viewName;
        addObject(modelName, modelObject);
    }

    public ModelAndView(String viewName, Map<String, ?> model) {
        this.view = viewName;
        addAllObjects(model);
    }

    // 链式调用
    public ModelAndView addObject(String attributeName, Object attributeValue) {
        getModelMap().addAttribute(attributeName, attributeValue);
        return this;
    }

    public void setViewName(String viewName) {
        this.view = viewName;
    }

    public void setStatus(HttpStatus status) {
        this.status = status;
    }
}
```

### 处理流程

```java
// ModelAndViewMethodReturnValueHandler.java
public class ModelAndViewMethodReturnValueHandler
        implements HandlerMethodReturnValueHandler {

    @Override
    public boolean supportsReturnType(MethodParameter returnType) {
        return ModelAndView.class.isAssignableFrom(returnType.getParameterType());
    }

    @Override
    public void handleReturnValue(Object returnValue,
            MethodParameter returnType, ModelAndViewContainer mavContainer,
            NativeWebRequest webRequest) throws Exception {

        ModelAndView mav = (ModelAndView) returnValue;
        if (mav.isReference()) {
            // view 是 String 视图名 → 设置到 mavContainer
            String viewName = mav.getViewName();
            mavContainer.setViewName(viewName);
        } else {
            // view 是 View 对象 → 直接设置
            mavContainer.setView(mav.getView());
        }

        // 合并模型数据
        mavContainer.addAllAttributes(mav.getModel());

        // 设置状态码（如果有）
        if (mav.getStatus() != null) {
            ((HttpServletResponse) webRequest.getNativeResponse())
                .setStatus(mav.getStatus().value());
        }
    }
}
```

---

## 2.3 Map/Model — 隐式视图 + 模型属性

### 使用方式

```java
@Controller
public class DashboardController {

    @GetMapping("/dashboard")
    public Map<String, Object> dashboard() {
        Map<String, Object> model = new HashMap<>();
        model.put("stats", dashboardService.getStats());
        model.put("recentActivities", dashboardService.getRecent());
        model.put("alerts", dashboardService.getAlerts());
        // 视图名由 RequestToViewNameTranslator 推断
        // 从请求路径 /dashboard 推断出视图名 "dashboard"
        return model;
    }

    // 或者直接用 Model 参数
    @GetMapping("/dashboard2")
    public Model dashboard2(Model model) {
        model.addAttribute("stats", dashboardService.getStats());
        // 同样，视图名由路径推断
        return model;
    }
}
```

### 视图名推断机制

```java
// RequestToViewNameTranslator 接口
public interface RequestToViewNameTranslator {
    String getViewName(HttpServletRequest request);
}

// 默认实现：DefaultRequestToViewNameTranslator
// GET /dashboard → 推断视图名: "dashboard"
// GET /user/profile → 推断视图名: "user/profile"
```

---

## 2.4 void — 无返回值

### 使用方式

```java
@RestController
public class LogController {

    // 1. void + 输出流参数 — 完全自行处理响应
    @GetMapping("/download")
    public void download(HttpServletResponse response) throws IOException {
        response.setContentType("application/pdf");
        response.getOutputStream().write(Files.readAllBytes(Paths.get("doc.pdf")));
    }

    // 2. void + @ResponseStatus — 只返回状态码
    @PostMapping("/log")
    @ResponseStatus(HttpStatus.ACCEPTED)  // 202
    public void logEvent(@RequestBody LogRequest request) {
        logService.log(request);
        // 返回 202 Accepted，无响应体
    }

    // 3. void — 默认 200 空响应
    @PostMapping("/fire-forget")
    public void fireAndForget(@RequestBody Event event) {
        eventService.processAsync(event);
        // 返回 200 OK，空 body
    }
}
```

### Spring 的 void 处理规则

> 来自官方文档：void 方法被认为"已完全处理响应"，如果它同时有：
> - `ServletResponse` / `OutputStream` 参数，或者
> - `@ResponseStatus` 注解，或者
> - Controller 设置了 ETag / lastModified

否则，void 方法有两种含义：
- REST Controller → "无响应体"（空 body + 200）
- HTML Controller → 推断默认视图名

```java
// 源码：ServletInvocableHandlerMethod 中判断是否已处理响应
private boolean isRequestHandled(Object returnValue, MethodParameter returnType) {
    // void 或 null
    if (returnValue == null) return true;

    // 检查方法参数中是否有 ServletResponse / OutputStream
    for (MethodParameter param : returnType.getMethod().getParameters()) {
        if (ServletResponse.class.isAssignableFrom(param.getParameterType())
                || OutputStream.class.isAssignableFrom(param.getParameterType())) {
            return true;
        }
    }

    // 检查是否有 @ResponseStatus
    if (AnnotatedElementUtils.hasAnnotation(returnType.getMethod(), ResponseStatus.class)) {
        return true;
    }

    return false;
}
```

---

## 2.5 View — 直接返回 View 对象

```java
@Controller
public class PdfController {

    @GetMapping("/report")
    public View generateReport(Model model) {
        model.addAttribute("data", reportService.getReport());

        // 返回自定义 View（PDF、Excel 等）
        return new PdfReportView();  // 自定义 AbstractView 子类
    }
}
```

适用于需要直接控制 View 对象的场景（如生成 PDF 报表、Excel 导出）。

---

# 第三章：精细化控制篇

## 3.1 HttpEntity

> ResponseEntity 的父类，**只能设置 Header 和 Body，不能设置状态码**。

```java
@RestController
public class HttpEntityController {

    @GetMapping("/data")
    public HttpEntity<User> getData() {
        HttpHeaders headers = new HttpHeaders();
        headers.add("X-Custom-Header", "value");

        // 状态码固定 200 OK（没有 setStatus 方法）
        return new HttpEntity<>(userService.findById(1L), headers);
    }
}
```

**实际使用较少** — ResponseEntity 提供了更多控制能力。

---

## 3.2 HttpHeaders — 只返回头

```java
@RestController
public class HeaderController {

    @GetMapping("/resource-info")
    public HttpHeaders getResourceInfo() {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setContentLength(1024);
        headers.setLastModified(System.currentTimeMillis());
        headers.setETag("\"abc123\"");
        headers.setCacheControl(CacheControl.maxAge(3600, TimeUnit.SECONDS));
        return headers;
    }
}
```

**返回值**：纯响应头，无 Body。

---

## 3.3 @ModelAttribute — 模型属性注入

```java
@Controller
public class ModelAttributeController {

    // 直接返回一个对象作为模型属性
    @GetMapping("/profile")
    @ModelAttribute("userProfile")
    public UserProfile getProfile() {
        return userService.getCurrentUserProfile();
    }
    // 视图名由 RequestToViewNameTranslator 从 /profile 推断
    // 模型中的属性名 = "userProfile"
}
```

如果方法没有 @ModelAttribute 但返回非简单类型，也会被当作模型属性处理（"其他返回类型"兜底规则）。

---

## 3.4 ErrorResponse / ProblemDetail — RFC 9457 错误响应

> Spring 6 / Spring Boot 3+ 引入的标准错误响应格式，详见 RFC 9457（替代旧的 RFC 7807）。

### 使用方式

```java
@RestController
@RequestMapping("/api")
public class ProblemDetailController {

    @GetMapping("/resource/{id}")
    public ResponseEntity<ProblemDetail> getResource(@PathVariable Long id) {
        try {
            return ResponseEntity.ok(resourceService.findById(id));
        } catch (ResourceNotFoundException e) {
            // 构建标准错误响应
            ProblemDetail problemDetail = ProblemDetail.forStatusAndDetail(
                HttpStatus.NOT_FOUND,
                "Resource with ID " + id + " not found"
            );
            problemDetail.setTitle("Resource Not Found");
            problemDetail.setProperty("errorCategory", "DATA_NOT_FOUND");
            problemDetail.setProperty("timestamp", Instant.now());

            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(problemDetail);
        }
    }

    // 直接返回 ProblemDetail（Spring 自动处理状态码）
    @ExceptionHandler(ResourceNotFoundException.class)
    public ProblemDetail handleNotFound(ResourceNotFoundException ex) {
        ProblemDetail pd = ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND, ex.getMessage());
        pd.setTitle("Resource Not Found");
        pd.setProperty("errorId", UUID.randomUUID().toString());
        pd.setProperty("category", "NOT_FOUND");
        return pd;
    }
}
```

### 响应示例

```json
// HTTP 404
{
  "type": "about:blank",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "Resource with ID 999 not found",
  "instance": "/api/resource/999",
  "errorCategory": "DATA_NOT_FOUND",
  "timestamp": "2026-05-28T10:00:00Z"
}
```

---

## 3.5 FragmentsRendering — HTML 片段渲染

> Spring 6+ 引入，用于渲染 HTML 片段（例如 HTMX 风格的 partial 页面更新）。

```java
@Controller
public class FragmentController {

    @GetMapping("/user-list-fragment")
    public FragmentRendering getFragment() {
        // 只渲染模板中的某个片段
        return FragmentsRendering
            .with("users :: user-table")
            .modelAttribute("users", userService.findAll())
            .build();
    }
}
```

---

## 3.6 其他返回类型 — 兜底规则

> Spring 对**无法识别的返回类型**做了兜底处理。

```java
// 如果返回值不是以上任何一种已知类型：

// 1. 简单类型（isSimpleProperty == true）：String, Number, Boolean, Date 等
//    → 保留不处理（最终可能报错）

// 2. 非简单类型（Domain Object, DTO 等）
//    → 放入 Model 作为属性，属性名由 Conventions.getVariableName() 推断
//    → 视图名由 RequestToViewNameTranslator 推断

// 例如：
@Controller
public class UserController {

    @GetMapping("/user")
    public UserProfile getUserProfile() {
        // UserProfile 不是已知返回类型
        // → 放入 model，属性名 "userProfile"
        // → 视图名推断为 "user"
        return userService.getProfile();
    }
}
```

---

# 第四章：异步篇

> 用于将请求线程与业务处理线程分离，提升 Web 容器的线程利用率。

## 4.1 DeferredResult — 异步结果的基石

### 核心概念

**DeferredResult** 是 Spring 3.2 引入的异步返回类型。关键在于：
- Controller 方法**立即返回** DeferredResult 对象
- 请求线程被**释放**，可以处理其他请求
- 业务在**任意线程**完成后，调用 `setResult()` 触发响应

### 使用方式

```java
@RestController
@RequestMapping("/async")
public class DeferredResultController {

    private final ExecutorService executor = Executors.newFixedThreadPool(10);

    // 基本用法
    @GetMapping("/data")
    public DeferredResult<String> getData() {
        // 1. 创建 DeferredResult（可指定超时时间）
        DeferredResult<String> result = new DeferredResult<>(5000L); // 5s 超时

        // 2. 在另一个线程中处理
        executor.submit(() -> {
            try {
                String data = expensiveOperation();
                result.setResult(data);  // 设置成功结果
            } catch (Exception e) {
                result.setErrorResult(e);  // 设置错误结果
            }
        });

        // 3. 立即返回，请求线程释放
        return result;
    }

    // 超时和错误回调
    @GetMapping("/data-with-callbacks")
    public DeferredResult<String> getDataWithCallbacks() {
        DeferredResult<String> result = new DeferredResult<>(5000L, "timeout-default");

        // 超时回调
        result.onTimeout(() -> {
            log.warn("Request timed out");
        });

        // 完成回调
        result.onCompletion(() -> {
            log.info("Request completed");
        });

        // 错误回调
        result.onError((Throwable ex) -> {
            log.error("Request failed", ex);
        });

        // ... async processing
        return result;
    }
}
```

### 核心源码

```java
// DeferredResult.java (Spring 源码核心片段)
public class DeferredResult<T> {

    private final Long timeout;           // 超时毫秒数
    private final T timeoutResult;         // 超时时的默认结果
    private T result;                      // 最终结果
    private Throwable error;               // 错误

    private Runnable timeoutCallback;      // 超时回调
    private Runnable completionCallback;   // 完成回调
    private Consumer<Throwable> errorCallback;  // 错误回调

    private volatile boolean expired;      // 是否已过期

    public DeferredResult(Long timeout) {
        this.timeout = timeout;
        this.timeoutResult = null;
    }

    public DeferredResult(Long timeout, T timeoutResult) {
        this.timeout = timeout;
        this.timeoutResult = timeoutResult;
    }

    /**
     * 设置成功结果 — 在业务线程中调用！
     */
    public boolean setResult(T result) {
        if (isSetOrExpired()) return false;  // 只能设置一次
        this.result = result;
        // 触发异步处理器的回调
        if (this.deferredResultHandler != null) {
            this.deferredResultHandler.handleResult(this);
        }
        return true;
    }

    /**
     * 设置错误结果
     */
    public boolean setErrorResult(Object error) {
        if (isSetOrExpired()) return false;
        if (error instanceof Throwable) {
            this.error = (Throwable) error;
        } else {
            this.error = new DeferredResultProcessingException("...", (Throwable) error);
        }
        if (this.deferredResultHandler != null) {
            this.deferredResultHandler.handleResult(this);
        }
        return true;
    }
}
```

### 处理流程

```
请求到达 → DispatcherServlet
    ↓
HandlerAdapter 调用 Controller 方法
    ↓
Controller 创建 DeferredResult 并立即返回
    ↓
HandlerAdapter 发现返回类型是 DeferredResult
    ↓
启动异步处理（request.startAsync()）
    ↓
请求线程释放 → 回到 Tomcat 线程池处理其他请求
    ↓
... 时间流逝 ...
    ↓
业务线程完成，调用 result.setResult(...)
    ↓
Spring 从 Servlet 容器获取异步上下文
    ↓
获取结果数据 → 走正常的消息转换流程 → 写入响应
    ↓
请求完成，Tomcat 发送响应给客户端
```

---

## 4.2 Callable — Spring 托管的异步

```java
@RestController
public class CallableController {

    @GetMapping("/async-greeting")
    public Callable<String> getGreeting() {
        return () -> {
            // 在 Spring 管理的 TaskExecutor 中运行
            Thread.sleep(2000);  // 模拟耗时操作
            return "Hello, Async World!";
        };
    }

    @GetMapping("/async-users")
    public Callable<List<User>> getUsersAsync() {
        return () -> userService.findAll();  // 后台线程执行
    }
}
```

### Callable vs DeferredResult

| 对比维度 | Callable | DeferredResult |
|---------|----------|---------------|
| **线程管理** | Spring 自动管理 | 开发者自行管理 |
| **代码复杂度** | 简单 | 更灵活 |
| **超时控制** | 依赖 Spring 配置 | 支持在构造器中设置 |
| **回调** | 无 | onTimeout, onCompletion, onError |
| **适用场景** | 简单异步操作 | 复杂异步编排、外部系统集成 |
| **异常处理** | 直接抛异常 | setErrorResult() |

---

## 4.3 CompletableFuture / CompletionStage — 现代异步

> Spring 4.3+ 将 CompletableFuture 视为 DeferredResult 的替代品。

### 使用方式

```java
@RestController
public class CompletableFutureController {

    @GetMapping("/future-data")
    public CompletableFuture<ResponseEntity<String>> getFutureData() {
        return CompletableFuture
            .supplyAsync(() -> expensiveOperation())
            .thenApply(result -> ResponseEntity.ok(result))
            .exceptionally(ex ->
                ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error: " + ex.getMessage())
            );
    }

    // 多个异步操作编排
    @GetMapping("/composed")
    public CompletableFuture<OrderDetail> getOrderDetail(
            @RequestParam Long orderId) {

        CompletableFuture<Order> orderFuture =
            CompletableFuture.supplyAsync(() -> orderService.findById(orderId));
        CompletableFuture<List<Payment>> paymentFuture =
            CompletableFuture.supplyAsync(() -> paymentService.findByOrder(orderId));

        return orderFuture.thenCombine(paymentFuture, (order, payments) ->
            new OrderDetail(order, payments));
    }
}
```

### Spring 如何处理 CompletableFuture

```java
// 内部适配：CompletableFuture → DeferredResult
// 使用 ListenableFutureAdapter / CompletableFutureAdapter 做转换

class CompletableFutureAdapter<T> extends DeferredResult<T> {

    private final CompletableFuture<T> future;

    public CompletableFutureAdapter(CompletableFuture<T> future) {
        this.future = future;
        future.whenComplete((result, ex) -> {
            if (ex != null) {
                setErrorResult(ex);
            } else {
                setResult(result);
            }
        });
    }
}
```

---

# 第五章：流式响应篇

> 本章内容主要来自微信公众号文章《Spring Boot 接口异步流式响应：3种核心实现方案》并扩展。

## 5.1 ResponseBodyEmitter — 对象流

> ResponseBodyEmitter 允许多次异步发送序列化后的对象到同一个 HTTP 响应。

### 使用方式

```java
@RestController
@RequestMapping("/streams")
public class AsyncStreamController {

    // 内存存储 emitter，用于后续推送
    private final Map<String, ResponseBodyEmitter> emitters = new ConcurrentHashMap<>();

    /**
     * 客户端订阅流（建立连接）
     */
    @GetMapping("/subscribe/{id}")
    public ResponseBodyEmitter subscribe(@PathVariable String id) {
        ResponseBodyEmitter emitter = this.emitters.computeIfAbsent(id, key -> {
            ResponseBodyEmitter rbe = new ResponseBodyEmitter();

            rbe.onCompletion(() -> this.emitters.remove(id));
            rbe.onTimeout(() -> this.emitters.remove(id));

            return rbe;
        });
        return emitter;
    }

    /**
     * 向已订阅的客户端推送数据
     */
    @GetMapping("/send/{id}")
    public void send(@PathVariable String id) throws Exception {
        ResponseBodyEmitter emitter = this.emitters.get(id);
        if (emitter != null) {
            emitter.send(
                Map.of("code", 0, "data", "T - " + System.currentTimeMillis()),
                MediaType.APPLICATION_JSON
            );
        }
    }

    /**
     * 结束流
     */
    @GetMapping("/complete/{id}")
    public void complete(@PathVariable String id) {
        ResponseBodyEmitter emitter = this.emitters.remove(id);
        if (emitter != null) {
            emitter.complete();
        }
    }
}
```

### 客户端测试（curl）

```bash
# 1. 建立连接（持续等待）
curl -N http://localhost:8080/streams/subscribe/pack

# 2. 另一个终端发送数据
curl http://localhost:8080/streams/send/pack

# 3. 结束后
curl http://localhost:8080/streams/complete/pack
```

### 核心源码

```java
// ResponseBodyEmitter.java
public class ResponseBodyEmitter {

    private final Long timeout;     // 超时时间
    private final List<DataWithMediaType> earlySendAttempts;  // 对列缓冲

    public ResponseBodyEmitter() {
        this(null);  // 无超时
    }

    public ResponseBodyEmitter(Long timeout) {
        this.timeout = timeout;
        this.earlySendAttempts = Collections.synchronizedList(new ArrayList<>());
    }

    /**
     * 发送一个对象到响应流
     * 每个对象会经过 HttpMessageConverter 序列化
     */
    public void send(Object object, MediaType mediaType) throws IOException {
        send(object, mediaType, null);  // 无额外转换器
    }

    public void send(Object object, MediaType mediaType, HttpHeaders headers)
            throws IOException {

        if (this.handler != null) {
            // 已建立连接 → 直接发送
            handler.send(object, mediaType, headers);
        } else {
            // 连接还未就绪 → 放入缓冲队列
            this.earlySendAttempts.add(new DataWithMediaType(object, mediaType, headers));
        }
    }

    /** 正常完成 */
    public void complete() {
        if (this.handler != null) {
            handler.complete();
        }
    }

    /** 异常完成 */
    public void completeWithError(Throwable ex) {
        if (this.handler != null) {
            handler.completeWithError(ex);
        }
    }

    // 内部类：存储待发送的数据条目
    static class DataWithMediaType {
        final Object data;
        final MediaType mediaType;
        final HttpHeaders headers;
        // constructor...
    }
}
```

> **工作原理**：`ResponseBodyEmitter` 内部在每个 `send()` 调用时，都会走一遍 `HttpMessageConverter` 的序列化链路（如同标准 `@ResponseBody` 流程），然后将序列化结果 flush 到 OutputStream。响应被设置为 `Transfer-Encoding: chunked`，所以客户端会以"块"的方式收到每个对象。

---

## 5.2 SseEmitter — 服务端推送（SSE）

> SseEmitter 是 ResponseBodyEmitter 的子类，按 **W3C SSE 规范**格式化事件流。

### 服务端实现

```java
@RestController
@RequestMapping("/streams")
public class SseController {

    private final Map<String, SseEmitter> emitters = new ConcurrentHashMap<>();

    @GetMapping(path = "/sse/{id}", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter handle(@PathVariable String id) {
        SseEmitter emitter = this.emitters.computeIfAbsent(id, key -> {
            SseEmitter sse = new SseEmitter(Long.MAX_VALUE);  // 超长超时
            sse.onCompletion(() -> this.emitters.remove(id));
            sse.onError(err -> {
                this.emitters.remove(id);
                System.err.println("SSE Error: " + err.getMessage());
            });
            return sse;
        });
        return emitter;
    }

    @GetMapping("/send-sse/{id}")
    public void send(@PathVariable String id) throws Exception {
        SseEmitter emitter = this.emitters.get(id);
        if (emitter != null) {
            // 方案 1: 直接发送 JSON
            emitter.send(
                Map.of("code", 0, "data", "T - " + System.currentTimeMillis()),
                MediaType.APPLICATION_JSON
            );

            // 方案 2: 使用 SseEmitter.event() Builder（更结构化的 SSE）
            emitter.send(SseEmitter.event()
                .name("message")               // event: message
                .data("Hello via SSE!")         // data: Hello via SSE!
                .id(String.valueOf(counter++))  // id: 1
                .reconnectTime(3000)            // retry: 3000
            );
        }
    }

    @GetMapping("/complete-sse/{id}")
    public void complete(@PathVariable String id) {
        SseEmitter emitter = this.emitters.remove(id);
        if (emitter != null) {
            emitter.complete();
        }
    }
}
```

### 前端实现（JavaScript）

```html
<body>
  <h1>SSE 实时消息演示</h1>
  <div>
    <input type="text" id="username" placeholder="请输入用户名">
    <button onclick="connect()">连接</button>
    <button onclick="closeSse()" disabled id="disconnectBtn">关闭</button>
  </div>
  <div id="status">等待连接...</div>
  <ul id="list"></ul>

  <script>
    const statusEl = document.querySelector("#status");
    const eventList = document.querySelector("#list");
    const disconnectBtn = document.querySelector("#disconnectBtn");
    const userName = document.querySelector("#username");
    let eventSource;

    function connect() {
      eventSource = new EventSource(`/streams/sse/${userName.value}`);

      eventSource.onmessage = (event) => {
        const li = document.createElement("li");
        li.innerHTML = "<strong>收到消息:</strong> " + event.data;
        eventList.appendChild(li);
      };

      eventSource.onopen = (event) => {
        statusEl.textContent = "连接已建立 ✓";
        statusEl.style.color = "#27ae60";
        disconnectBtn.disabled = false;
      };

      eventSource.onerror = (event) => {
        statusEl.textContent = "连接错误 ✗";
        statusEl.style.color = "#e74c3c";
        disconnectBtn.disabled = true;
      };
    }

    function closeSse() {
      eventSource.close();
      statusEl.textContent = "连接已关闭";
      statusEl.style.color = "#e74c3c";
      disconnectBtn.disabled = true;
    }
  </script>
</body>
```

### SSE 协议格式

```
// 服务端发送的原始数据格式（HTTP 响应体）：
id: 1
event: message
data: {"code":0,"data":"T - 1700000000000"}
retry: 3000

id: 2
event: message
data: {"code":0,"data":"T - 1700000001000"}

id: 3
event: message
data: {"code":0,"data":"T - 1700000002000"}
```

### SSE vs WebSocket

| 对比维度 | SSE | WebSocket |
|---------|-----|-----------|
| **协议** | HTTP（单向） | TCP（双向） |
| **方向** | 服务端 → 客户端 | 双向 |
| **浏览器支持** | 原生 EventSource API | WebSocket API |
| **自动重连** | 内置（retry） | 需自行实现 |
| **传输类型** | 文本 | 文本 + 二进制 |
| **最大连接数** | 浏览器限制（通常 6/域名） | 无特殊限制 |
| **适用场景** | 通知、推送、实时数据 | 聊天、游戏、双向实时 |

---

## 5.3 StreamingResponseBody — 原生流输出

> 直接操作 OutputStream，完全绕过 HttpMessageConverter 的序列化。适合超大文件下载、数据导出等场景。

### 使用方式

```java
@RestController
public class StreamingResponseBodyController {

    private final ObjectMapper objectMapper = new ObjectMapper();

    // 逐条输出 JSON（每行一条记录，类似 NDJSON）
    @GetMapping("/stream/users")
    public ResponseEntity<StreamingResponseBody> streamUsers() {
        List<User> users = List.of(
            new User("张三", 22),
            new User("李四", 23),
            new User("王五", 24)
        );

        StreamingResponseBody responseBody = os -> {
            for (User user : users) {
                String json = objectMapper.writeValueAsString(user) + "\n";
                os.write(json.getBytes(StandardCharsets.UTF_8));
                os.flush();
                TimeUnit.MILLISECONDS.sleep(500);  // 模拟延迟
            }
        };

        return ResponseEntity.ok()
            .contentType(MediaType.TEXT_PLAIN)
            .header("X-Stream-Type", "user-export")
            .body(responseBody);
    }

    // 大文件流式下载
    @GetMapping("/download/big-file")
    public ResponseEntity<StreamingResponseBody> downloadBigFile() {
        Path file = Paths.get("/data/large-report.csv");

        StreamingResponseBody stream = os -> {
            try (InputStream is = Files.newInputStream(file)) {
                byte[] buffer = new byte[8192];
                int bytesRead;
                while ((bytesRead = is.read(buffer)) != -1) {
                    os.write(buffer, 0, bytesRead);
                }
            }
        };

        return ResponseEntity.ok()
            .contentType(MediaType.APPLICATION_OCTET_STREAM)
            .header(HttpHeaders.CONTENT_DISPOSITION,
                "attachment; filename=\"large-report.csv\"")
            .body(stream);
    }

    // 数据库大数据导出（避免 OOM）
    @GetMapping("/export/orders")
    public ResponseEntity<StreamingResponseBody> exportOrders() {
        StreamingResponseBody stream = os -> {
            BufferedWriter writer = new BufferedWriter(
                new OutputStreamWriter(os, StandardCharsets.UTF_8));

            writer.write("ID,Customer,Amount,Date\n");
            orderRepository.streamAll().forEach(order -> {
                try {
                    writer.write(String.format("%d,%s,%.2f,%s\n",
                        order.getId(), order.getCustomer(),
                        order.getAmount(), order.getCreatedAt()));
                    writer.flush();
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            });
        };

        return ResponseEntity.ok()
            .contentType(MediaType.TEXT_PLAIN)
            .header(HttpHeaders.CONTENT_DISPOSITION,
                "attachment; filename=\"orders.csv\"")
            .body(stream);
    }

    record User(String name, Integer age) {}
}
```

### 核心原理

```java
// StreamingResponseBody.java
@FunctionalInterface
public interface StreamingResponseBody {

    /**
     * 写入响应 OutputStream
     * 在异步线程池中执行（不阻塞 Servlet 容器线程）
     */
    void writeTo(OutputStream outputStream) throws IOException;
}

// 处理流程（StreamingResponseBodyMethodProcessor）
public class StreamingResponseBodyMethodProcessor
        implements HandlerMethodReturnValueHandler {

    @Override
    public void handleReturnValue(Object returnValue, ...) {
        StreamingResponseBody streamingBody = (StreamingResponseBody) returnValue;

        // 1. 启动异步处理
        Callable<Void> callable = () -> {
            // 2. 获取 OutputStream
            OutputStream os = ((HttpServletResponse) servletResponse).getOutputStream();
            // 3. 调用业务 lambda 写入
            streamingBody.writeTo(os);
            return null;
        };

        // 4. 在异步线程中执行
        taskExecutor.submit(callable);

        // 5. 主线程立即返回
        // 注意：不调用 writeWithMessageConverters()
        // 完全绕过 HttpMessageConverter
    }
}
```

---

# 第六章：响应式编程篇（WebFlux）

> 需要 `spring-boot-starter-webflux` 依赖，且应用必须运行在 **Netty** 而非 Tomcat 上。

## 6.1 Mono — 单值响应

```java
@RestController
public class ReactiveController {

    // Mono 单值：类似异步的 Optional
    @GetMapping("/user/{id}")
    public Mono<User> getUser(@PathVariable Long id) {
        return reactiveUserRepository.findById(id);
    }

    // Mono + ResponseEntity
    @GetMapping("/user2/{id}")
    public Mono<ResponseEntity<User>> getUser2(@PathVariable Long id) {
        return reactiveUserRepository.findById(id)
            .map(user -> ResponseEntity.ok(user))
            .defaultIfEmpty(ResponseEntity.notFound().build());
    }

    // Mono + 延迟
    @GetMapping("/delayed")
    public Mono<String> getDelayed() {
        return Mono.just("Hello")
            .delayElement(Duration.ofSeconds(2));
    }
}
```

## 6.2 Flux — 多值流

```java
@RestController
public class FluxController {

    // 作为列表返回
    @GetMapping("/users")
    public Flux<User> getAllUsers() {
        return reactiveUserRepository.findAll();
    }

    // SSE 流
    @GetMapping(value = "/users/stream",
                produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<User> streamUsers() {
        return reactiveUserRepository.findAll()
            .delayElements(Duration.ofSeconds(1));  // 每秒 emit 一个
    }

    // 无限流
    @GetMapping(value = "/clock",
                produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> streamClock() {
        return Flux.interval(Duration.ofSeconds(1))
            .map(tick -> "Tick: " + Instant.now());
    }
}
```

## 6.3 背压机制

> 响应式编程的核心优势：消费者可以通过 `request(n)` 告诉生产者自己的处理能力，防止积压。

```java
@GetMapping(value = "/stream", produces = MediaType.APPLICATION_NDJSON)
public Flux<String> getStream() {
    return Flux.generate(() -> 0, (i, sink) -> {
        if (i > 1000) {
            sink.complete();
        } else {
            sink.next("Item " + i);
        }
        return i + 1;
    })
    .onBackpressureBuffer(256)  // 背压缓存
    .delayElements(Duration.ofMillis(100));
}
```

---

# 第七章：资源与文件下载篇

## 7.1 Resource — 文件下载

### 使用方式

```java
@RestController
@RequestMapping("/download")
public class FileDownloadController {

    // 文件系统文件
    @GetMapping("/file")
    public ResponseEntity<Resource> downloadFile() {
        File file = new File("/data/report.pdf");
        Resource resource = new FileSystemResource(file);

        return ResponseEntity.ok()
            .contentType(MediaType.APPLICATION_PDF)
            .contentLength(file.length())
            .header(HttpHeaders.CONTENT_DISPOSITION,
                "attachment; filename=\"" + file.getName() + "\"")
            .body(resource);
    }

    // classpath 中的文件
    @GetMapping("/template")
    public ResponseEntity<Resource> downloadTemplate() {
        Resource resource = new ClassPathResource("static/template.xlsx");

        return ResponseEntity.ok()
            .contentType(MediaType.parseMediaType(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
            .header(HttpHeaders.CONTENT_DISPOSITION,
                "attachment; filename=\"template.xlsx\"")
            .body(resource);
    }

    // InputStreamResource — 动态生成的文件流
    @GetMapping("/dynamic")
    public ResponseEntity<InputStreamResource> downloadDynamic() {
        ByteArrayInputStream stream = generateCsvStream();

        return ResponseEntity.ok()
            .contentType(MediaType.TEXT_PLAIN)
            .body(new InputStreamResource(stream));
    }
}
```

## 7.2 byte[] — 原始字节

```java
@RestController
public class ByteController {

    @GetMapping("/image/{id}")
    public ResponseEntity<byte[]> getImage(@PathVariable Long id) {
        ImageData image = imageService.findById(id);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.valueOf(image.getMimeType()));
        headers.setContentLength(image.getData().length);

        return new ResponseEntity<>(image.getData(), headers, HttpStatus.OK);
    }
}
```

---

# 第八章：底层原理剖析

## 8.1 RequestMappingHandlerAdapter 处理流程

```java
// RequestMappingHandlerAdapter.java — 核心处理流程

protected ModelAndView invokeHandlerMethod(HttpServletRequest request,
        HttpServletResponse response, HandlerMethod handlerMethod) throws Exception {

    // 1. 创建 MethodInvocation 上下文
    ServletInvocableHandlerMethod invocableMethod = createInvocableHandlerMethod(handlerMethod);

    // 2. 注册 ReturnValueHandler（关键！）
    List<HandlerMethodReturnValueHandler> returnValueHandlers = getReturnValueHandlers();
    invocableMethod.setHandlerMethodReturnValueHandlers(returnValueHandlers);

    // 3. 创建 ModelAndViewContainer（存储模型和视图信息）
    ModelAndViewContainer mavContainer = new ModelAndViewContainer();

    // 4. 执行方法（反射调用）
    invocableMethod.invokeAndHandle(webRequest, mavContainer);

    // 5. 如果返回类型不是异步且请求已处理 → 返回 null
    if (!invocableMethod.isAsync() || mavContainer.isRequestHandled()) {
        return getModelAndView(mavContainer);
    }

    return null;  // 异步场景：返回值由其他线程处理
}
```

### ReturnValueHandler 注册链（判断顺序至关重要）

```java
// RequestMappingHandlerAdapter.getDefaultReturnValueHandlers()
private List<HandlerMethodReturnValueHandler> getDefaultReturnValueHandlers() {
    List<HandlerMethodReturnValueHandler> handlers = new ArrayList<>();

    // 1. ModelAndView
    if (hasModelAndView) handlers.add(new ModelAndViewMethodReturnValueHandler());
    // 2. Model
    if (hasModel) handlers.add(new ModelMethodProcessor());
    // 3. View
    if (hasView) handlers.add(new ViewMethodReturnValueHandler());
    // 4. ResponseEntity / HttpEntity（带 @ResponseBody 语义）
    handlers.add(new HttpEntityMethodProcessor(converters, ...));
    // 5. RequestBody 相关
    handlers.add(new RequestResponseBodyMethodProcessor(converters, ...));
    // 6. 异步：DeferredResult
    handlers.add(new DeferredResultMethodReturnValueHandler());
    // 7. 异步：Callable
    handlers.add(new CallableMethodReturnValueHandler());
    // 8. 异步：CompletableFuture
    handlers.add(new CompletionStageReturnValueHandler());
    // 9. 流式：ResponseBodyEmitter / SseEmitter
    handlers.add(new ResponseBodyEmitterReturnValueHandler(converters));
    // 10. 流式：StreamingResponseBody
    handlers.add(new StreamingResponseBodyReturnValueHandler());
    // 11. 其他异步（Reactive types）
    handlers.add(new ReactiveAdapterReturnValueHandler());
    // 12. String 视图名
    handlers.add(new ViewNameMethodReturnValueHandler());
    // 13. Map / Model
    handlers.add(new MapMethodProcessor());
    // 14. @ModelAttribute
    handlers.add(new ModelAttributeMethodProcessor(false));
    // 15. Resource
    handlers.add(new HttpEntityMethodProcessor(converters, ...)); // 复用
    // 16. void / null
    // 17. 其他兜底（非简单类型 → 模型属性）
    handlers.add(new ModelAttributeMethodProcessor(true));

    return handlers;
}
```

> **重要**：处理器的注册顺序决定了匹配优先级。例如，`HttpEntityMethodProcessor` 排在 `RequestResponseBodyMethodProcessor` 前面，所以 `ResponseEntity` 总是先于普通 `@ResponseBody` 被处理。

## 8.2 HttpMessageConverter 机制

### Converter 接口定义

```java
// HttpMessageConverter.java
public interface HttpMessageConverter<T> {

    /** 是否能读取指定类 + Content-Type */
    boolean canRead(Class<?> clazz, MediaType mediaType);

    /** 是否能写入指定类 + Content-Type */
    boolean canWrite(Class<?> clazz, MediaType mediaType);

    /** 获取支持的 MediaType */
    List<MediaType> getSupportedMediaTypes();

    /** 反序列化请求体 */
    T read(Class<? extends T> clazz, HttpInputMessage inputMessage)
            throws IOException, HttpMessageNotReadableException;

    /** 序列化对象到响应体 */
    void write(T t, MediaType contentType, HttpOutputMessage outputMessage)
            throws IOException, HttpMessageNotWritableException;
}
```

### 内置 Converter 列表

| Converter | 序列化格式 | 优先级 |
|-----------|-----------|--------|
| `MappingJackson2HttpMessageConverter` | JSON | 高 |
| `MappingJackson2XmlHttpMessageConverter` | XML | 高 |
| `StringHttpMessageConverter` | text/plain | 中 |
| `ByteArrayHttpMessageConverter` | application/octet-stream | 中 |
| `ResourceHttpMessageConverter` | 文件/资源 | 中 |
| `SourceHttpMessageConverter` | XML Source | 低 |
| `AllEncompassingFormHttpMessageConverter` | form data | 低 |

### Converter 选择过程

```java
// AbstractMessageConverterMethodProcessor.writeWithMessageConverters()
protected <T> void writeWithMessageConverters(T value, MethodParameter returnType,
        ServletServerHttpResponse outputMessage) throws ... {

    ServletServerHttpResponse serverHttpResponse = outputMessage;
    HttpServletRequest request = getRequest(webRequest);

    // 1. 确定目标 MediaType
    MediaType acceptedMediaType = getAcceptableMediaType(request);
    MediaType producibleMediaType = getProducibleMediaType(request, valueType, targetType);

    Set<MediaType> compatibleMediaTypes = new LinkedHashSet<>();
    for (MediaType accepted : acceptedMediaTypes) {
        for (MediaType producible : producibleMediaTypes) {
            if (accepted.isCompatibleWith(producible)) {
                compatibleMediaTypes.add(getMostSpecificMediaType(accepted, producible));
            }
        }
    }

    // 2. 遍历已注册的 Converter，找第一个 canWrite()
    for (HttpMessageConverter<?> converter : this.messageConverters) {
        GenericHttpMessageConverter genericConverter =
            (converter instanceof GenericHttpMessageConverter)
                ? (GenericHttpMessageConverter) converter : null;

        if (genericConverter != null ?
                genericConverter.canWrite(targetType, valueType, selectedMediaType) :
                converter.canWrite(valueType, selectedMediaType)) {

            // 3. 写入响应
            converter.write(value, selectedMediaType, outputMessage);
            return;
        }
    }

    // 4. 没有合适的 Converter → 抛 406 Not Acceptable
    throw new HttpMediaTypeNotAcceptableException(producibleMediaTypes);
}
```

## 8.3 AbstractMessageConverterMethodProcessor

这是处理 `@ResponseBody` / `ResponseEntity` / `HttpEntity` 返回类型的核心基类：

```java
// AbstractMessageConverterMethodProcessor.java
public abstract class AbstractMessageConverterMethodProcessor
        extends AbstractMessageConverterMethodArgumentResolver
        implements HandlerMethodReturnValueHandler {

    protected final List<HttpMessageConverter<?>> messageConverters;

    protected <T> void writeWithMessageConverters(T value, ...) {
        // ...（见上节 8.2 的 Converter 选择过程）
    }

    /**
     * 将输出和处理结果写入 HttpServletResponse
     * 对于 ResponseEntity，会先设置状态码和 Header
     * 然后调用 writeWithMessageConverters 写 body
     */
    protected ServletServerHttpResponse createOutputMessage(NativeWebRequest webRequest) {
        HttpServletResponse response = webRequest.getNativeResponse(HttpServletResponse.class);
        return new ServletServerHttpResponse(response);
    }
}
```

## 8.4 异步请求处理全过程

以 DeferredResult 为例：

```java
// 1. 请求到达
// DispatcherServlet.doDispatch() 中：

// 1a. 找到 HandlerMethod 和 HandlerAdapter
HandlerAdapter ha = getHandlerAdapter(mappedHandler.getHandler());

// 1b. 调用拦截器的 preHandle
if (!mappedHandler.applyPreHandle(processedRequest, response)) {
    return;
}

// 1c. 执行 Controller 方法，获取返回值
ModelAndView mv = ha.handle(processedRequest, response, mappedHandler.getHandler());

// 1d. 检查是否是异步请求
if (asyncManager.hasConcurrentResult()) {
    // 异步场景：这里只返回 null，不执行后续
    // 真正的渲染在异步线程的 callableProcessingInterceptor 中
    return;
}

// 1e. 应用拦截器的 postHandle
mappedHandler.applyPostHandle(processedRequest, response, mv);

// 1f. 同步渲染视图
processDispatchResult(processedRequest, response, mappedHandler, mv, dispatchException);

// ============ 异步请求的延迟处理 ============

// 2. 异步线程中调用 setResult() 后
// WebAsyncManager 的 ConcurrentResult 会被设置

// 3. Servlet 容器（Tomcat）检测到 AsyncContext 有数据
// → 重新调用 DispatcherServlet

// 4. DispatcherServlet 再次进入 doDispatch()
// → asyncManager.hasConcurrentResult() 返回 true

// 5. 获取并发结果
Object result = asyncManager.getConcurrentResult();
ModelAndView mv = (ModelAndView) asyncManager.getConcurrentResultModelAndView();

// 6. 正常渲染（走同一个返回值处理器链）
processDispatchResult(processedRequest, response, mappedHandler, mv, dispatchException);
```

---

# 第九章：生产实践

## 9.1 统一响应格式封装

```java
// 统一响应包装
public record ApiResult<T>(
    int code,
    String message,
    T data,
    Instant timestamp
) {

    public static <T> ApiResult<T> success(T data) {
        return new ApiResult<>(200, "success", data, Instant.now());
    }

    public static <T> ApiResult<T> success(String message, T data) {
        return new ApiResult<>(200, message, data, Instant.now());
    }

    public static <T> ApiResult<T> error(int code, String message) {
        return new ApiResult<>(code, message, null, Instant.now());
    }
}

// 使用方式
@RestController
@RequestMapping("/api/users")
public class UserApiController {

    // 统一格式：ResponseEntity<ApiResult<T>>
    @GetMapping("/{id}")
    public ResponseEntity<ApiResult<User>> getUser(@PathVariable Long id) {
        return userService.findById(id)
            .map(user -> ResponseEntity.ok(ApiResult.success(user)))
            .orElse(ResponseEntity
                .status(HttpStatus.NOT_FOUND)
                .body(ApiResult.error(404, "用户不存在")));
    }
}
```

## 9.2 全局异常处理 + ProblemDetail

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    // 通用异常 → ProblemDetail（RFC 9457）
    @ExceptionHandler(ResourceNotFoundException.class)
    public ProblemDetail handleNotFound(ResourceNotFoundException ex) {
        ProblemDetail pd = ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND, ex.getMessage());
        pd.setTitle("Resource Not Found");
        pd.setProperty("errorId", UUID.randomUUID().toString());
        pd.setProperty("timestamp", Instant.now());
        return pd;
    }

    @ExceptionHandler(ValidationException.class)
    public ProblemDetail handleValidation(ValidationException ex) {
        ProblemDetail pd = ProblemDetail.forStatusAndDetail(
            HttpStatus.BAD_REQUEST, ex.getMessage());
        pd.setTitle("Validation Failed");
        pd.setProperty("errors", ex.getErrors());  // 详细验证错误
        return pd;
    }

    @ExceptionHandler(Exception.class)
    public ProblemDetail handleGeneral(Exception ex) {
        log.error("Unhandled exception", ex);
        ProblemDetail pd = ProblemDetail.forStatusAndDetail(
            HttpStatus.INTERNAL_SERVER_ERROR, "Internal server error");
        pd.setTitle("Internal Error");
        return pd;
    }
}
```

## 9.3 响应类型选择树

```
开始：你的 Controller 返回什么？
        │
        ├─ 在 @RestController 中？
        │   ├─ 需要完全控制状态码 / Header / Body？
        │   │   └─ ResponseEntity<T>
        │   ├─ 只需要 Body？
        │   │   └─ T (POJO/List/String) — 自动 @ResponseBody
        │   ├─ 需要异步、自己控制线程？
        │   │   ├─ 单次异步返回 → DeferredResult / CompletableFuture
        │   │   └─ 多次流式返回 → ResponseBodyEmitter
        │   ├─ 需要 SSE 推送？
        │   │   └─ SseEmitter
        │   ├─ 需要大文件流？
        │   │   └─ StreamingResponseBody
        │   ├─ 文件下载？
        │   │   └─ ResponseEntity<Resource>
        │   ├─ 只返回头、无体？
        │   │   └─ HttpHeaders
        │   └─ 标准错误响应？
        │       └─ ProblemDetail
        │
        ├─ 在 @Controller 中（服务端渲染）？
        │   ├─ 返回视图名 + 数据？
        │   │   └─ ModelAndView
        │   ├─ 只返回视图名？
        │   │   └─ String
        │   ├─ 只返回模型数据？
        │   │   └─ Map<String, Object>
        │   └─ 自定义 View？
        │       └─ View
        │
        └─ 返回 void？
            ├─ 自己写 HttpServletResponse → void + ServletResponse 参数
            └─ 空响应 + 状态码 → void + @ResponseStatus
```

## 9.4 反模式清单

### ❌ 反模式 1：混用 @RestController 和 String 视图返回

```java
@RestController  // 所有方法带 @ResponseBody
public class BadController {

    @GetMapping("/home")
    public String home() {
        return "home";  // ❌ 这不是视图名！它被序列化为 JSON 字符串
        // 客户端收到: "home" — 不是 HTML 页面
    }
}
```

**正确做法**：用 `@Controller`（非 `@RestController`）+ 明确区分 REST 方法和视图方法。

### ❌ 反模式 2：大文件直接用 byte[] 返回

```java
@GetMapping("/download/{id}")
public byte[] downloadFile(@PathVariable String id) {
    // ❌ 整个文件读入内存！如果文件 2GB → OOM
    return Files.readAllBytes(Paths.get("/data/" + id + ".zip"));
}
```

**正确做法**：使用 `StreamingResponseBody` 或 `Resource`。

### ❌ 反模式 3：手动创建 ResponseEntity 做统一包装

```java
// ❌ 每个方法都手动包装 ApiResult
@GetMapping("/{id}")
public ResponseEntity<ApiResult<User>> getUser(@PathVariable Long id) {
    return ResponseEntity.ok(ApiResult.success(userService.findById(id)));
}

@GetMapping
public ResponseEntity<ApiResult<List<User>>> getUsers() {
    return ResponseEntity.ok(ApiResult.success(userService.findAll()));
}
// ... 100 个方法重复这个模式
```

**正确做法**：使用 `ResponseBodyAdvice` 全局包装：

```java
@ControllerAdvice
public class ApiResultWrapper implements ResponseBodyAdvice<Object> {

    @Override
    public boolean supports(MethodParameter returnType, Class converterType) {
        // 排除已经包装过的、避免双层包装
        return !returnType.getParameterType().equals(ApiResult.class);
    }

    @Override
    public Object beforeBodyWrite(Object body, ...) {
        if (body == null) {
            return ApiResult.success(null);
        }
        if (body instanceof ProblemDetail) {
            return body;  // 错误响应不包装
        }
        return ApiResult.success(body);
    }
}
```

### ❌ 反模式 4：返回类型混用导致歧义

```java
@PostMapping("/create")
public ResponseEntity<Order> createOrder(@RequestBody OrderReq req) {
    Order order = orderService.create(req);
    // ❌ 有些分支返回 ResponseEntity，有些直接返回对象
    if (order.isFraud()) {
        return ResponseEntity.badRequest().build();  // ok
    }
    return order;  // ❌ 编译错误！返回类型是 ResponseEntity<Order>
}
```

### ❌ 反模式 5：不合理的超时设置

```java
// ❌ DeferredResult 不设超时 → 连接永远不释放
DeferredResult<String> result = new DeferredResult<>();

// ✅ 设置合理超时 + 兜底值
DeferredResult<String> result = new DeferredResult<>(5000L, "timeout");
```

### ❌ 反模式 6：SSE 连接数无限膨胀

```java
// ❌ 没有清除机制，用户刷新一次就多一个 emitter
@GetMapping("/subscribe")
public SseEmitter subscribe() {
    SseEmitter emitter = new SseEmitter();
    emitters.add(emitter);  // emitters 集合无限增长
    return emitter;
}
```

**正确做法**：
```java
emitter.onCompletion(() -> emitters.remove(emitter));
emitter.onTimeout(() -> emitters.remove(emitter));
```

---

> **扩展阅读**：
> - [Spring 官方文档：Controller Return Types](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-methods/return-types.html)
> - [Spring 官方文档：Async Requests](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-methods/return-types.html#mvc-ann-async)
> - [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457) — Problem Details for HTTP APIs
> - [Spring Boot 实战案例集锦](https://mp.weixin.qq.com/s/-EjZdtZGwUTQJOm7Jp0tOg) — 源微信公众号文章
