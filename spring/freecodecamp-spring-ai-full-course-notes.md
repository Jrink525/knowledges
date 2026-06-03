# freeCodeCamp — Spring AI Full Course with Projects 精要

> **视频**: [Spring AI Full Course with Projects – Build Smarter Spring Boot Applications](https://youtu.be/9Crrhz0pm8s)  
> **主讲**: Faasil Muhammed | **时长**: 4h 32min  
> **内容**: 5 个 Spring AI 实战项目，涵盖聊天机器人、RAG、图像生成、语音转文字  
> **中文整理**: 根据字幕归纳核心内容

---

## 一、课程概览

> "In this course you'll go beyond just theory — we'll build real-world applications with Spring AI."

**5 个实战项目：**

1. **Project 1** — AI 聊天机器人（Spring AI ChatClient + 前端）
2. **Project 2** — PDF 知识库问答（RAG + 向量存储）
3. **Project 3** — 图像生成应用（Image Generation）
4. **Project 4** — 语音转文字（Audio Transcription）
5. **Project 5** — 集成项目（Combined多种能力）

---

## 二、Project 1：AI 聊天机器人

### 2.1 依赖配置

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
</dependency>
```

### 2.2 ChatClient 构建

```java
@RestController
@RequestMapping("/api/chat")
public class ChatController {
    
    private final ChatClient chatClient;
    
    public ChatController(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }
    
    @PostMapping
    public String chat(@RequestBody String message) {
        return chatClient.prompt()
            .user(message)
            .call()
            .content();
    }
}
```

### 2.3 前端集成

该项目包含完整的 Thymeleaf 前端界面，用于展示聊天交互。

---

## 三、Project 2：PDF 知识库 RAG

### 3.1 架构

```
用户提问 → PDF文档分块 → 嵌入向量 → 存入 VectorStore
  → 用户提问 → 向量检索 → Top-K 上下文 → LLM 回答
```

### 3.2 PDF 文档处理

```java
// 读取 PDF 文档
var pdfResource = new ClassPathResource("documents/knowledge-base.pdf");
var pdfReader = new PagePdfDocumentReader(pdfResource);

// 分块
var textSplitter = new TokenTextSplitter();
var chunks = textSplitter.apply(pdfReader.get());
```

### 3.3 向量存储

```java
@Bean
public VectorStore vectorStore(EmbeddingModel embeddingModel) {
    return new SimpleVectorStore(embeddingModel);
}
```

**中文解读：** `SimpleVectorStore` 适用于开发和测试。生产环境推荐 PGVector、Pinecone、Chroma 等持久化向量库。

---

## 四、Project 3：图像生成

### 4.1 Image Model 配置

```java
@RestController
@RequestMapping("/api/image")
public class ImageController {
    
    private final ImageModel imageModel;
    
    public ImageController(ImageModel imageModel) {
        this.imageModel = imageModel;
    }
    
    @PostMapping("/generate")
    public String generateImage(@RequestBody String prompt) {
        var options = ImageOptionsBuilder.builder()
            .withWidth(1024)
            .withHeight(1024)
            .build();
        
        var response = imageModel.call(
            new ImagePrompt(prompt, options));
        
        return response.getResult().getOutput().getUrl();
    }
}
```

**中文解读：** Spring AI 统一了不同图像生成模型的 API（OpenAI DALL-E、Stability AI 等），开发者只需切换配置即可更换模型。

---

## 五、Project 4：语音转文字

### 5.1 Audio Transcription

```java
@RestController
@RequestMapping("/api/transcribe")
public class TranscriptionController {
    
    private final AudioTranscriptionModel transcriptionModel;
    
    public TranscriptionController(
            AudioTranscriptionModel transcriptionModel) {
        this.transcriptionModel = transcriptionModel;
    }
    
    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public String transcribe(@RequestParam("file") MultipartFile file) {
        var audio = new AudioResource(file.getResource());
        var response = transcriptionModel.call(audio);
        return response.getText();
    }
}
```

**中文解读：** 一个 Controller 即可完成语音转文字。模型层支持 OpenAI Whisper 等服务，对业务代码完全透明。

---

## 六、Project 5：综合集成项目

### 6.1 多能力组合

将前面 4 个项目的功能整合到一个应用中：

- Chat + 知识库 RAG
- 图像生成能力
- 语音输入转文字
- 统一前端界面

---

## 七、核心技术要点

### 7.1 Spring AI 核心抽象

| 抽象 | 用途 | 支持模型 |
|------|------|---------|
| `ChatModel` | 文本对话 | OpenAI, Bedrock, Ollama, Anthropic... |
| `ImageModel` | 图像生成 | OpenAI DALL-E, Stability AI |
| `AudioTranscriptionModel` | 语音转文字 | OpenAI Whisper |
| `EmbeddingModel` | 文本嵌入 | OpenAI Ada, 本地模型 |
| `VectorStore` | 向量检索 | PGVector, Pinecone, Simple |

### 7.2 RAG 实现关键步骤

1. **加载**：`PdfDocumentReader` 等读取器加载非结构化数据
2. **分块**：`TokenTextSplitter` 控制块大小
3. **嵌入**：`EmbeddingModel` 将文本转为向量
4. **存储**：`VectorStore` 持久化向量数据
5. **检索**：用户查询 → 嵌入 → 向量相似度搜索
6. **生成**：检索结果注入 prompt → LLM 回答

### 7.3 配置示例

```properties
# OpenAI 配置
spring.ai.openai.api-key=${OPENAI_API_KEY}
spring.ai.openai.chat.model=gpt-4
spring.ai.openai.image.model=dall-e-3

# Ollama 本地模型（可选）
spring.ai.ollama.base-url=http://localhost:11434
spring.ai.ollama.chat.model=llama3.2
```

---

## 八、实战经验总结

### 8.1 项目管理理念

**Faasil:** "Each project is full-stack — we'll build frontend, backend, and everything in between. You can adapt these projects to your own needs."

**中文解读：** 该课程强调完整的全栈项目实践，而非单独的 API 调用示例。适合想要一个完整参考项目的开发者。

### 8.2 最佳实践

1. **配置外部化** — API Key 等敏感信息使用环境变量
2. **前端分离** — 后端只管 API，前端可选择 Thymeleaf 或 SPA
3. **渐进式构建** — 从简单 chat 开始，逐步叠加 RAG、图像、语音能力
4. **模型切换灵活** — Spring AI 的抽象层使更换模型只需改配置

### 8.3 适用场景

| 项目 | 最佳用途 |
|------|---------|
| Project 1 (Chat) | 智能客服、FAQ 机器人 |
| Project 2 (RAG) | 企业内部知识库、法律文档分析 |
| Project 3 (Image) | 创意工具、营销内容生成 |
| Project 4 (Audio) | 会议纪要、语音笔记 |
| Project 5 (集成) | 全功能 AI 助手平台 |

---

> **整理说明**：本文基于 4.5h 课程字幕提炼，原课程包含完整的前后端代码实现和实机演示。**注意**：该课程语音非英语母语演讲者，自动字幕准确性可能有一定偏差，关键代码和概念已在整理时核实。
