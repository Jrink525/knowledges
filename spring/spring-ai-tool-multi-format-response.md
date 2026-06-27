# 超越 JSON：Spring AI 多格式工具响应指南

> **原文来源**: Spring Boot 实战案例合集（微信公众号）  
> **核心主题**: Spring AI 工具响应格式转换 — JSON / **TOON** / XML / CSV / YAML  
> **环境**: Spring Boot 3.5.0 + Spring AI + DeepSeek

---

## 1. 背景：为什么需要替代 JSON？

JSON 是 LLM 工具响应的默认格式，但 **TOON**（Token-Oriented Object Notation，面向 Token 的对象表示法）的讨论日益增多，声称其在 Token 效率和性能方面有潜在优势。

目前行业辩论仍在继续，但关键问题在于：**如何在 Spring AI 应用程序中实验这些格式？**

本文提供完整的实战方法，让你能够在 JSON、TOON、XML、CSV、YAML 之间自由切换工具响应格式。

---

## 2. Spring AI 工具调用快速回顾

### 工作流程

```
工具定义（名称、描述、参数 Schema）→ 加入聊天请求
  ↓
模型决定调用某个工具 → 发送工具名称和输入参数
  ↓
Spring AI 识别并执行该工具
  ↓
Spring AI 处理工具结果
  ↓
工具结果作为对话历史的一部分返回
  ↓
模型利用工具结果生成最终响应
```

### 核心接口：ToolCallback

每个工具都被包装在一个 `ToolCallback` 中，负责序列化和执行逻辑。我们可以在**两个关键节点**拦截并转换响应格式：

| 层级 | 时机 | 适用范围 |
|------|------|---------|
| **工具结果层** | 工具执行后、JSON 序列化前 | 仅本地工具（`@Tool`、`FunctionToolCallback`、`MethodToolCallback`） |
| **响应层** | JSON 序列化后 | 全局通用（含 MCP 工具） |

---

## 3. 环境配置

### Maven 依赖

```xml
<!-- TOON 格式支持 -->
<dependency>
    <groupId>dev.toonformat</groupId>
    <artifactId>jtoon</artifactId>
    <version>0.1.4</version>
</dependency>

<!-- 其他格式的 Jackson 扩展 -->
<dependency>
    <groupId>com.fasterxml.jackson.dataformat</groupId>
    <artifactId>jackson-dataformat-yaml</artifactId>
</dependency>
<dependency>
    <groupId>com.fasterxml.jackson.dataformat</groupId>
    <artifactId>jackson-dataformat-xml</artifactId>
</dependency>
<dependency>
    <groupId>com.fasterxml.jackson.dataformat</groupId>
    <artifactId>jackson-dataformat-csv</artifactId>
</dependency>
```

### application.yml

```yaml
spring:
  ai:
    deepseek:
      api-key: ${API_KEY}
      base-url: https://api.deepseek.com
      chat:
        model: deepseek-v4-flash
```

### 工具类示例：泰坦尼克号数据

```java
public class TitanicData {
    private static List<Map<String, Object>> titanicPassengers = 
        fileToList("classpath:/data/titanic.json");

    public static List<Map<String, Object>> getRandomTitanicPassengers(int count) {
        var start = new Random().nextInt(titanicPassengers.size() - count - 1);
        return titanicPassengers.subList(start, start + count);
    }

    private static List<Map<String, Object>> fileToList(String uri) {
        // 读取 JSON 文件并反序列化
    }
}
```

---

## 4. 两种方法实现格式转换

### 方法 1：自定义 ToolCallResultConverter（细粒度控制）

**适用**：仅本地工具（`@Tool`、`FunctionToolCallback`、`MethodToolCallback`）

```java
public static class ToonToolCallResultConverter implements ToolCallResultConverter {
    private ToolCallResultConverter delegate = new DefaultToolCallResultConverter();

    @Override
    public String convert(@Nullable Object result, @Nullable Type returnType) {
        // 1. 先转 JSON
        String json = this.delegate.convert(result, returnType);
        // 2. JSON → TOON
        return JToon.encodeJson(json);
    }
}
```

**注册方式**（`@Tool` 属性）：

```java
@Tool(description = "获取泰坦尼克号乘客", resultConverter = ToonToolCallResultConverter.class)
public List<String> randomTitanicToon(@ToolParam(description = "数量") int count) {
    return TitanicData.getTitanicPassengersInRange(30, count);
}
```

也可通过 `FunctionToolCallback` / `MethodToolCallback` 的 Builder 编程式注册。

**执行流程**：
```
工具执行 → 默认转换器创建 JSON → TOON 转换器转换 JSON → LLM 接收到 TOON 响应
```

**局限性**：
- ❌ 不兼容 MCP 工具（`@McpTool`）
- ❌ 每个工具需单独实现和注册
- ❌ 维护开销大

---

### 方法 2：全局工具响应配置（推荐）

使用 **委派模式（Delegator Pattern）** 包裹现有的 `ToolCallbackProvider`，统一应用到所有工具。

#### 架构

```
原始 ToolCallbackProvider
  ↓ 被 DelegatorToolCallbackProvider 包裹
创建包裹后的回调：DelegatorToolCallback（每个工具一个）
  ↓ 拦截 call() 方法
将响应从 JSON 转换为目标格式（TOON / XML / CSV / YAML）
```

#### 组件 1：DelegatorToolCallbackProvider

```java
public class DelegatorToolCallbackProvider implements ToolCallbackProvider {
    private final ToolCallbackProvider delegate;
    private final ResponseConverter.Format format;

    public DelegatorToolCallbackProvider(
            ToolCallbackProvider delegate, 
            ResponseConverter.Format format) {
        this.delegate = delegate;
        this.format = format;
    }

    @Override
    public ToolCallback[] getToolCallbacks() {
        return Stream.of(this.delegate.getToolCallbacks())
            .map(callback -> new DelegatorToolCallback(callback, this.format))
            .toArray(ToolCallback[]::new);
    }
}
```

#### 组件 2：DelegatorToolCallback

拦截 `call()` 方法，允许原始工具正常执行，然后转换 JSON 响应为目标格式。

#### 组件 3：ResponseConverter 工具类

```java
public class ResponseConverter {
    public enum Format { TOON, YAML, XML, CSV, JSON }

    public static String convert(String json, Format format) {
        switch (format) {
            case JSON: return json;
            case YAML: return jsonToYaml(toJsonNode(json));
            case XML:  return jsonToXml(toJsonNode(json));
            case CSV:  return jsonToCsv(toJsonNode(json));
            case TOON: return jsonToToon(json);
        }
        throw new IllegalStateException("Unsupported format: " + format);
    }
}
```

#### 完整示例

```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

    @Bean
    CommandLineRunner runner(
            ChatClient.Builder chatClientBuilder,
            ToolCallbackProvider toolCallbackProvider) {

        // 使用 TOON 格式包裹 Provider
        var provider = new DelegatorToolCallbackProvider(
            toolCallbackProvider, 
            ResponseConverter.Format.TOON);

        var chatClient = chatClientBuilder
            .defaultToolCallbacks(provider)
            .build();

        return args -> {
            var response = chatClient
                .prompt("Please show me 10 Titanic passengers?")
                .call()
                .chatResponse();
            System.out.println(response.getResult().getOutput().getText());
        };
    }

    @Bean
    MethodToolCallbackProvider methodToolCallbackProvider() {
        return MethodToolCallbackProvider.builder()
            .toolObjects(new MyTools())
            .build();
    }
}
```

**执行流程**：
```
用户提示词 → LLM 调用工具 → 包装器拦截 → 工具执行 
→ 创建 JSON → 格式转换器转换 → LLM 接收转换后响应
```

---

## 5. 五种格式对比

### JSON（默认）

```json
[
  {"name": "John", "age": 30, "survived": true},
  {"name": "Mary", "age": 25, "survived": false}
]
```

- ✅ 标准兼容性最好
- ❌ Token 开销最高（括号、引号、逗号密集）

### TOON（面向 Token 的对象表示法）

TOON 是专为 LLM 设计的轻量格式，大幅减少结构冗余 Token。

- ✅ **Token 效率最高**（减少了大量结构字符）
- ✅ LLM 更容易解析
- ⚠️ 需要 jtoon 库（0.1.4）
- **推荐用于 Token 成本敏感场景**

### CSV

```
name,age,survived
John,30,true
Mary,25,false
```

- ✅ 扁平数据极简
- ❌ 不支持嵌套结构
- ❌ 复杂数据需要扁平化

### XML

```xml
<root>
  <item><name>John</name><age>30</age><survived>true</survived></item>
</root>
```

- ✅ 语义丰富
- ❌ Token 开销最大（大量标签）
- ❌ JSON 到 XML 转换需包裹数组节点

### YAML

```yaml
- name: John
  age: 30
  survived: true
```

- ✅ 相比 JSON 更简洁
- ❌ 缩进敏感
- ❌ 嵌套深时仍有一定 Token 开销

---

## 6. Token 使用实测结果

根据文章给出的实测数据（趋势总结）：

| 格式 | Token 消耗 | 相对 JSON 节省 | 推荐场景 |
|------|:---------:|:-------------:|---------|
| **TOON** | ⭐ **最低** | **~40-60%** | 生产环境、Token 成本敏感 |
| CSV | 较低 | ~20-40% | 扁平数据批量查询 |
| YAML | 中等 | ~10-20% | 配置文件风格数据 |
| JSON | 基准 | — | 兼容性、通用开发 |
| XML | 最高 ❌ | 倒挂 | 遗留系统集成 |

> **注意**：实际 Token 节省取决于数据结构复杂度和嵌套深度。TOON 在数组和嵌套对象上优势最明显。

---

## 7. 测试与验证

```java
@Component
public class ToolReturnFormatRunner implements CommandLineRunner {
    private final ChatClient chatClient;
    private final DelegatorToolCallbackProvider provider;

    public ToolReturnFormatRunner(
            ChatClient.Builder chatClientBuilder,
            ToolCallbackProvider toolCallbackProvider,
            @Value("${spring.ai.tool.response.format:JSON}") String responseFormat) {
        
        this.provider = new DelegatorToolCallbackProvider(
            toolCallbackProvider,
            ResponseConverter.Format.valueOf(responseFormat));
        
        this.chatClient = chatClientBuilder
            .defaultTools(provider)
            .defaultAdvisors(
                ToolCallingAdvisor.builder().build(),
                new MyLogAdvisor())
            .build();
    }

    @Override
    public void run(String... args) throws Exception {
        var response = chatClient
            .prompt("显示5个乘客信息")
            .call()
            .chatResponse();
        System.out.printf("RESPONSE: %s%nUSAGE: %s%n",
            response.getResult().getOutput().getText(),
            response.getMetadata().getUsage());
    }
}
```

通过 `application.yml` 配置格式：

```yaml
spring:
  ai:
    tool:
      response:
        format: TOON  # 可切换为 JSON/YAML/XML/CSV
```

---

## 8. 方案对比总结

| 维度 | 方法1：ToolCallResultConverter | 方法2：Delegator 委派模式 |
|------|:-----:|:-----:|
| 粒度 | 单个工具 | 全局统一 |
| 兼容 MCP | ❌ | ✅ |
| 配置复杂度 | 中（每个工具注册） | 低（一次配置） |
| 动态切换 | 需修改代码 | 支持配置驱动 |
| 推荐场景 | 特定工具特殊格式 | **生产标准方案** |

---

## 9. 生产建议

1. **优先使用方法 2（委派模式）** — 一次配置全局生效，兼容 MCP 工具
2. **TOON 是当前 Token 效率最优解** — 大批量数据响应降本显著
3. **JsonNode 配置参考** — 格式转换中的 JsonNode 配置项可以进一步优化输出
4. **灵活切换** — 通过 `application.yml` 的 `spring.ai.tool.response.format` 配置，可在不同环境使用不同格式
5. **辅助日志组件** — 使用 `ToolCallAdvisor` 和自定义 `MyLogAdvisor` 查看不同格式的实际工具响应

---

## 10. 参考资源

- **TOON 格式 & JToon**: `dev.toonformat:jtoon:0.1.4`
- **Jackson 扩展**: `jackson-dataformat-yaml`、`jackson-dataformat-xml`、`jackson-dataformat-csv`
- **Spring AI 版本**: Spring Boot 3.5.0 配套版本
