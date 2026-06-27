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

### 数据工具类：泰坦尼克号乘客

```java
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.json.JsonMapper;
import com.fasterxml.jackson.core.json.JsonReadFeature;
import org.springframework.core.io.DefaultResourceLoader;

import java.nio.charset.Charset;
import java.util.*;

public class TitanicData {
    private static List<Map<String, Object>> titanicPassengers =
            fileToList("classpath:/data/titanic.json");

    public static List<Map<String, Object>> getRandomTitanicPassengers(int count) {
        var start = new Random().nextInt(titanicPassengers.size() - count - 1);
        return titanicPassengers.subList(start, start + count);
    }

    private static List<Map<String, Object>> fileToList(String uri) {
        try {
            var json = new DefaultResourceLoader()
                    .getResource(uri)
                    .getContentAsString(Charset.defaultCharset());
            JsonMapper mapper = JsonMapper.builder()
                    .enable(JsonReadFeature.ALLOW_NON_NUMERIC_NUMBERS)
                    .build();
            TypeReference<List<Map<String, Object>>> type =
                    new TypeReference<List<Map<String, Object>>>() {};
            return mapper.readValue(json, type);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    public static List<String> getTitanicPassengersInRange(int range, int count) {
        // 返回指定范围+数量的乘客信息（字符串列表形式）
        if (range < 0) range = 0;
        return getRandomTitanicPassengers(count).stream()
                .map(p -> {
                    StringBuilder sb = new StringBuilder();
                    p.forEach((k, v) -> sb.append(k).append(": ").append(v).append(", "));
                    return sb.toString();
                })
                .toList();
    }
}
```

---

## 4. 两种方法实现格式转换

### 方法 1：自定义 ToolCallResultConverter（细粒度控制）

**适用**：仅本地工具（`@Tool`、`FunctionToolCallback`、`MethodToolCallback`）

```java
import org.springframework.ai.tool.ToolCallResultConverter;
import org.springframework.ai.tool.DefaultToolCallResultConverter;
import org.springframework.lang.Nullable;
import java.lang.reflect.Type;

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
@Tool(description = "获取泰坦尼克号乘客",
      resultConverter = ToonToolCallResultConverter.class)
public List<String> randomTitanicToon(
        @ToolParam(description = "数量") int count) {
    return TitanicData.getTitanicPassengersInRange(30, count);
}
```

也可通过 `FunctionToolCallback` / `MethodToolCallback` 的 Builder 编程式注册。

**执行流程**：
```
工具执行 → 默认转换器→ JSON → TOON 转换器→ TOON → LLM 接收 TOON 响应
```

**局限性**：
- ❌ 不兼容 MCP 工具（`@McpTool`）
- ❌ 每个工具需单独实现并配置 resultConverter
- ❌ 维护开销大

---

### 方法 2：全局委派模式（推荐）

使用 **Delegator Pattern** 包裹现有 `ToolCallbackProvider`，统一应用到所有工具。

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
import org.springframework.ai.tool.ToolCallback;
import org.springframework.ai.tool.ToolCallbackProvider;
import java.util.stream.Stream;

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

```java
import org.springframework.ai.tool.ToolCallback;
import org.springframework.ai.tool.metadata.ToolMetadata;
import reactor.core.publisher.Flux;

public class DelegatorToolCallback implements ToolCallback {
    private final ToolCallback delegate;
    private final ResponseConverter.Format format;

    public DelegatorToolCallback(ToolCallback delegate, ResponseConverter.Format format) {
        this.delegate = delegate;
        this.format = format;
    }

    @Override
    public ToolMetadata getToolMetadata() {
        return delegate.getToolMetadata();
    }

    @Override
    public String call(String toolInput) {
        // 执行原始工具
        String jsonResult = delegate.call(toolInput);
        // 将 JSON 结果转换为目标格式
        return ResponseConverter.convert(jsonResult, this.format);
    }

    @Override
    public Flux<String> stream(String toolInput) {
        return delegate.stream(toolInput)
                .map(json -> ResponseConverter.convert(json, this.format));
    }
}
```

#### 组件 3：ResponseConverter 工具类（完整版）

```java
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.dataformat.csv.CsvMapper;
import com.fasterxml.jackson.dataformat.csv.CsvSchema;
import com.fasterxml.jackson.dataformat.xml.XmlMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLMapper;
import dev.toonformat.jtoon.JToon;

import java.util.LinkedHashSet;
import java.util.Set;

public class ResponseConverter {
    public enum Format {
        TOON, YAML, XML, CSV, JSON
    }

    private static final ObjectMapper objectMapper = new ObjectMapper();

    public static String convert(String json, Format format) {
        switch (format) {
            case JSON:
                return json;
            case YAML:
                return jsonToYaml(toJsonNode(json));
            case XML:
                return jsonToXml(toJsonNode(json));
            case CSV:
                return jsonToCsv(toJsonNode(json));
            case TOON:
                return jsonToToon(json);
        }
        throw new IllegalStateException("Unsupported format: " + format);
    }

    // —— YAML 转换 ——

    private static String jsonToYaml(JsonNode jsonNode) {
        try {
            return new YAMLMapper().writeValueAsString(jsonNode);
        } catch (Exception e) {
            throw new RuntimeException("YAML conversion failed", e);
        }
    }

    // —— XML 转换 ——

    public static String jsonToXml(JsonNode jsonNode) {
        try {
            XmlMapper xmlMapper = new XmlMapper();
            if (jsonNode.isArray()) {
                // 数组需要用根元素包裹，否则 XML 解析会失败
                ObjectNode wrapper = xmlMapper.createObjectNode();
                wrapper.set("root", jsonNode);
                return xmlMapper.writeValueAsString(wrapper);
            }
            return xmlMapper.writeValueAsString(jsonNode);
        } catch (Exception e) {
            throw new RuntimeException("XML conversion failed", e);
        }
    }

    // —— CSV 转换 ——

    public static String jsonToCsv(JsonNode jsonNode) {
        try {
            CsvMapper csvMapper = new CsvMapper();

            // 确保输入是数组
            ArrayNode arrayNode;
            if (jsonNode.isArray()) {
                arrayNode = (ArrayNode) jsonNode;
            } else if (jsonNode.isObject()) {
                arrayNode = csvMapper.createArrayNode();
                arrayNode.add(jsonNode);
            } else {
                throw new IllegalArgumentException("JSON must be an object or array for CSV");
            }

            if (arrayNode.isEmpty()) {
                return "";
            }

            // 动态构建 CSV Schema：从所有对象的字段名推断列
            CsvSchema.Builder schemaBuilder = CsvSchema.builder();
            Set<String> columns = new LinkedHashSet<>();
            for (JsonNode node : arrayNode) {
                if (node.isObject()) {
                    node.fieldNames().forEachRemaining(columns::add);
                }
            }
            columns.forEach(schemaBuilder::addColumn);
            CsvSchema schema = schemaBuilder.build().withHeader();

            return csvMapper.writer(schema).writeValueAsString(arrayNode);
        } catch (Exception e) {
            throw new RuntimeException("CSV conversion failed", e);
        }
    }

    // —— TOON 转换 ——

    private static String jsonToToon(String jsonString) {
        return JToon.encodeJson(jsonString);
    }

    // —— 工具方法 ——

    private static JsonNode toJsonNode(String jsonString) {
        try {
            return objectMapper.readTree(jsonString);
        } catch (Exception e) {
            throw new RuntimeException("Invalid JSON string", e);
        }
    }
}
```

#### 完整使用示例

```java
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import java.util.List;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

    @Bean
    CommandLineRunner commandLineRunner(
            ChatClient.Builder chatClientBuilder,
            ToolCallbackProvider toolCallbackProvider) {

        // 使用 TOON 格式包裹 Provider
        var provider = new DelegatorToolCallbackProvider(
                toolCallbackProvider,
                ResponseConverter.Format.TOON);

        // 使用包裹后的 Provider 配置 ChatClient
        var chatClient = chatClientBuilder
                .defaultToolCallbacks(provider)
                .build();

        return args -> {
            var response = chatClient
                    .prompt("Please show me 10 Titanic passengers?")
                    .call()
                    .chatResponse();

            System.out.println(String.format("""
                    RESPONSE: %s
                    USAGE: %s
                    """,
                    response.getResult().getOutput().getText(),
                    response.getMetadata().getUsage()));
        };
    }

    @Bean
    MethodToolCallbackProvider methodToolCallbackProvider() {
        return MethodToolCallbackProvider.builder()
                .toolObjects(new MyTools())
                .build();
    }

    static class MyTools {
        @Tool(description = "Get titanic passengers")
        public List<String> randomTitanicToon(
                @ToolParam(description = "Number of records to return") int count) {
            return TitanicData.getTitanicPassengersInRange(30, count);
        }
    }
}
```

**执行流程**：
```
用户提示词 → LLM 调用工具 → DelegatorToolCallback 拦截
  → 原始工具执行 → 返回 JSON
  → ResponseConverter 转换 → TOON/XML/CSV/YAML
  → LLM 接收转换后的响应
```

---

## 5. 可配置的 Runner：支持动态切换格式

通过 `application.yml` 配置驱动，无需改代码即可切换格式。

### 自定义 Log Advisor（辅助调试）

```java
import org.springframework.ai.chat.client.advisor.api.*;
import reactor.core.publisher.Flux;

public class MyLogAdvisor implements CallAroundAdvisor {
    @Override
    public String getName() {
        return "MyLogAdvisor";
    }

    @Override
    public int getOrder() {
        return 0;
    }

    @Override
    public AdvisedResponse aroundCall(AdvisedRequest advisedRequest,
                                       CallAroundAdvisorChain chain) {
        // 打印请求中的工具响应格式
        System.out.println("=== [MyLogAdvisor] Request ===");
        System.out.println("User text: " + advisedRequest.userText());

        AdvisedResponse response = chain.nextAroundCall(advisedRequest);

        System.out.println("=== [MyLogAdvisor] Response ===");
        System.out.println("Response: " +
                response.chatResponse().getResult().getOutput().getText());

        return response;
    }

    @Override
    public Flux<AdvisedResponse> aroundStream(AdvisedRequest advisedRequest,
                                               StreamAroundAdvisorChain chain) {
        return chain.nextAroundStream(advisedRequest);
    }
}
```

### ToolReturnFormatRunner

```java
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.ToolCallingAdvisor;
import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

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

        System.out.println(String.format("""
                RESPONSE: %s
                USAGE: %s
                """,
                response.getResult().getOutput().getText(),
                response.getMetadata().getUsage()));
    }
}
```

### application.yml 配置

```yaml
spring:
  ai:
    tool:
      response:
        format: TOON   # 可切换：JSON / YAML / XML / CSV / TOON
```

---

## 6. 五种格式对比与实测 Token 消耗

### 格式对比

| 格式 | 特点 | Token 开销 | 推荐场景 |
|------|------|:---------:|---------|
| **JSON** | 标准兼容性最好，但括号/引号/逗号密集 | 基准 | 兼容性、通用开发 |
| **TOON** 🏆 | 面向 Token 的紧凑格式，大幅减少结构字符 | **~40-60% ↓** | 生产环境、Token 成本敏感 |
| **CSV** | 扁平数据极简，不支持嵌套 | ~20-40% ↓ | 批量扁平数据查询 |
| **YAML** | 比 JSON 简洁，缩进敏感 | ~10-20% ↓ | 配置文件风格数据 |
| **XML** | 语义丰富，标签开销最大 | 倒挂 | 遗留系统集成 |

### 实测结果（文章数据）

**JSON 输出** — 标准格式，详细的键值对结构，Token 最多

**CSV 输出** — 扁平的表格形式，大幅减少结构 Token，但丢失了嵌套信息

**TOON 输出** — 去除了所有冗余的引号、括号和逗号，结构紧凑，Token 最少

**XML 输出** — 标签包裹增加了额外 Token，在简单数据集上比 JSON 还重

**YAML 输出** — 介于 JSON 和 TOON 之间，有缩进开销但在嵌套结构上比 JSON 好

> **实际 Token 节省取决于数据结构的复杂度和嵌套深度。TOON 在数组和嵌套对象上优势最明显。**

---

## 7. 方案对比总结

| 维度 | 方法1：ToolCallResultConverter | 方法2：Delegator 委派模式 |
|------|:-----:|:-----:|
| 粒度 | 单个工具 | 全局统一 |
| 兼容 MCP（@McpTool） | ❌ | ✅ |
| 配置复杂度 | 中（每个工具注册） | 低（一次配置） |
| 动态切换 | 需修改代码 | 配置驱动 |
| 实现一致性 | 各工具可能不同 | 统一 |
| 推荐场景 | 特定工具特殊格式 | **生产标准方案** |

---

## 8. 生产建议

1. **优先方法 2（委派模式）**
   — 一次配置全局生效，兼容 MCP 工具，统一维护

2. **TOON 是当前 Token 效率最优解**
   — 大批量数据响应降本显著，实测在深度嵌套的数据集上节省可达 60%

3. **配置驱动灵活切换**
   ```yaml
   spring:
     ai:
       tool:
         response:
           format: TOON  # 不同环境可用不同格式
   ```
   开发环境用 JSON（调试友好），生产环境用 TOON（Token 高效）

4. **日志辅助调试**
   — 使用 `ToolCallingAdvisor` + 自定义 `MyLogAdvisor`
   — 可以清晰看到工具实际返回的原始格式内容

5. **注意 CSV 限制**
   — JSON 转 CSV 只支持对象和对象数组，且嵌套字段会丢失层级信息
   — `LinkedHashSet` 保证列顺序与 JSON 中首次出现的顺序一致

---

## 9. 参考资源

- **TOON 格式 & JToon**: `dev.toonformat:jtoon:0.1.4`
- **Jackson 扩展**: `jackson-dataformat-yaml`, `jackson-dataformat-xml`, `jackson-dataformat-csv`
- **Spring AI 版本**: Spring Boot 3.5.0 配套版本
