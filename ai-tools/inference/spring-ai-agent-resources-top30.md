---
title: Spring AI Agent 精选资源 Top 30 — 教程/仓库/视频
tags: [spring, spring-ai, agent, ai, tutorial, github, youtube, curated-list, 来源:公众号+web]
category: spring/ai-agent
source: "web_search + GitHub API + YouTube 搜索"
date: 2026-05-21
---

# Spring AI Agent 精选资源 Top 30

> 综合微信、GitHub、Medium、YouTube、B站等多平台搜索，筛选出阅读量/播放量高、可实践性强、干货满满的学习资源。
> **数据采集时间：** 2026-05-21

---

## 📖 内容分类

- [📦 GitHub 仓库 (10个)](#-github-仓库)
- [📝 文章/教程 (10篇)](#-文章教程)
- [🎬 视频 (10个)](#-视频)
- [🧠 推荐学习路径](#-推荐学习路径)

---

## 📦 GitHub 仓库

### 1. [spring-projects/spring-ai](https://github.com/spring-projects/spring-ai) ⭐8.8k
> Spring 官方 AI 框架，Agent 核心底座
- 内置 ChatClient、Tool Calling、Chat Memory、Prompt Templates
- 支持 OpenAI / Ollama / Azure / Anthropic 等多模型
- **MCP 集成**：官方 SDK 支持，Agent 与外部工具交互
- **适用**：基础框架学习，自定义 Agent 开发

### 2. [alibaba/spring-ai-alibaba](https://github.com/alibaba/spring-ai-alibaba) ⭐9.7k
> 阿里官方 Agentic AI 框架，Spring AI 增强扩展
- **Agent Framework**：ReAct 模式、多 Agent 编排
- **MCP 插件**、RAG 检索增强、ChatMemory
- 中文文档完善，社区活跃
- **适用**：企业级 Java Agent 开发首选

### 3. [spring-ai-alibaba/examples](https://github.com/spring-ai-alibaba/examples) ⭐2.7k
> Spring AI & Spring AI Alibaba 官方示例合集
- 含 Agent、RAG、Tool Calling、MCP 多场景
- 每个示例都是完整可运行项目
- **适用**：对照学习的最佳代码参考

### 4. [liyupi/yu-ai-agent](https://github.com/liyupi/yu-ai-agent) ⭐2.3k
> 编程导航 2025 AI 开发实战项目（鱼皮）
- Spring Boot 3 + Java 21 + Spring AI
- AI 恋爱大师应用 + **ReAct 模式自主规划智能体 YuManus**
- 覆盖：Prompt 工程、RAG、向量数据库、Tool Calling、MCP
- **适用**：从零到一的完整项目实战

### 5. [spring-ai-alibaba/DataAgent](https://github.com/spring-ai-alibaba/DataAgent) ⭐1.9k
> 数据智能体，NL2SQL + 数据分析
- 自然语言查询数据库，自动生成 SQL 并执行
- 适合**企业数据查询**场景
- **适用**：数据分析 Agent 开发参考

### 6. [Atmosphere/atmosphere](https://github.com/Atmosphere/atmosphere) ⭐3.8k
> Java AI Agent 实时传输层框架
- `@Agent` 注解开发生命周期管理
- 支持 WebSocket、SSE、gRPC、WebTransport/HTTP3
- 兼容 MCP 和 A2A 协议
- **适用**：需要实时通信的 Agent 场景

### 7. [modelcontextprotocol/java-sdk](https://github.com/modelcontextprotocol/java-sdk) ⭐3.4k
> MCP Java SDK（Spring AI 团队共同维护）
- MCP Server / Client 完整实现
- 支持多种传输方式（STDIO、SSE、gRPC）
- **适用**：自定义 MCP 工具开发

### 8. [ModelEngine-Group/fit-framework](https://github.com/ModelEngine-Group/fit-framework) ⭐2.1k
> FIT 企业级 AI 开发框架
- Java 生态 LangChain 替代方案
- 函数引擎（FIT）+ 流式编排引擎（WaterFlow）
- 原生 / Spring 双模运行
- **适用**：高灵活度 AI 应用框架对比学习

### 9. [duongminhhieu/springboot-ai-mcp-example](https://github.com/duongminhhieu/springboot-ai-mcp-example)
> Spring AI + MCP 最小可运行示例
- MCP Server + Client 完整代码
- MongoDB、PostgreSQL 集成
- **适用**：MCP 入门实践

### 10. [Lunaan0/spring-ai-agent](https://github.com/Lunaan0/spring-ai-agent)
> 编程导航 AI Agent 实战项目
- 覆盖 Tool Calling、MCP、RAG 全流程
- **适用**：配合鱼皮项目对比学习

---

## 📝 文章/教程

### 中文篇

#### 11. [Spring AI 实战：Agent 基础搭建与核心能力解析](https://cloud.tencent.com/developer/article/2625331)
- **来源：** 腾讯云开发者社区
- **内容：** 任务规划 Agent 完整 Demo，含意图识别、工具调用，代码可运行
- **推荐：** ⭐⭐⭐⭐⭐ 入门首选

#### 12. [用 Spring AI 构建智能 Agent：从理论到实战落地](https://blog.csdn.net/u012012134/article/details/149000689)
- **来源：** CSDN（2026 最新）
- **内容：** RAG + Agent + MCP 三位一体架构，企业级落地思路
- **推荐：** ⭐⭐⭐⭐ 架构设计参考

#### 13. [Spring AI 完整学习路线：从 Java 开发到 AI Agent](https://jishuzhan.net/article/2055911752479117314)
- **来源：** 技术站（2026 终极指南）
- **内容：** 13 篇深度实战系列，Spring Boot 3.5.9 + Spring AI 1.1.4
- **推荐：** ⭐⭐⭐⭐⭐ 系统学习路线图

#### 14. [AI 实践｜基于 Spring AI 从0到1构建 AI Agent](https://jimo.studio/blog/building-ai-agent-from-scratch-using-spring-ai/)
- **来源：** jimo.studio / 阿里云开发者社区
- **内容：** 六大核心模块（意图识别、记忆管理、工具调用）架构解析
- **推荐：** ⭐⭐⭐⭐⭐ 架构清晰，代码完整

#### 15. [Spring Boot 一行代码实现 AI 大模型 Agent 开发](https://blog.51cto.com/u_16163452/14290032)
- **来源：** 51CTO
- **内容：** 查天气示例，SSE 流式响应 + 多轮记忆
- **推荐：** ⭐⭐⭐⭐ 入门简单，快速上手

### 英文篇

#### 16. [Spring AI Reference — Building Effective Agents](https://docs.spring.io/spring-ai/reference/api/effective-agents.html)
- **来源：** 官方文档
- **内容：** 基于 Anthropic 研究成果的 Agent 模式实现
- **推荐：** ⭐⭐⭐⭐⭐ **最权威，必读**

#### 17. [Spring AI Tutorial: How to Develop AI Agents](https://www.infoworld.com/article/4150199/spring-ai-tutorial-building-ai-agents-with-spring-ai.html)
- **来源：** InfoWorld
- **内容：** Step by Step 构建 Spring AI Agent，含完整代码
- **推荐：** ⭐⭐⭐⭐ 媒体精品教程

#### 18. [Baeldung — Building Effective Agents with Spring AI](https://www.baeldung.com/spring-ai-building-effective-agents)
- **来源：** Baeldung
- **内容：** Anthropic 简单可组合 Agent 模式的 Spring AI 实现
- **推荐：** ⭐⭐⭐⭐⭐ Baeldung 出品必属精品

#### 19. [Baeldung — MCP with Spring AI](https://www.baeldung.com/spring-ai-model-context-protocol-mcp)
- **来源：** Baeldung
- **内容：** MCP 协议 + Spring AI 集成，Agent 与外部工具交互
- **推荐：** ⭐⭐⭐⭐⭐ 学习 MCP 最佳教程

#### 20. [A Practical Guide — Building AI Agents with Java and Spring AI (Part 1-5)](https://dev.to/yuriybezsonov/series/33948)
- **来源：** dev.to
- **作者：** Yuriy Bezsonov
- **内容：** 5 篇系列，Part1→Part5 循序：创建 Agent → Tool Calling → Memory → MCP
- **推荐：** ⭐⭐⭐⭐⭐ 系列最完整

---

## 🎬 视频

### YouTube 视频

#### 21. [Building Agents with Spring AI, MCP, Java & Bedrock | Workshop](https://www.youtube.com/watch?v=G9PD6ANza70)
- **UP主：** FunctionalTV (James Ward + **Josh Long** 🏆)
- **时长：** 2h06m
- **内容：** Spring 大牛 Josh Long + James Ward Workshop，MCP + Agent 全流程
- **推荐：** ⭐⭐⭐⭐⭐ **必看！Spring 社区含金量最高**

#### 22. [AI for Java Developers — Full Course / Workshop](https://www.youtube.com/watch?v=FzLABAppJfM)
- **UP主：** Dan Vega
- **时长：** 5h38m
- **内容：** 最完整的 Spring AI Workshop，覆盖 Agent 开发
- **推荐：** ⭐⭐⭐⭐⭐ 地毯式覆盖

#### 23. [Spring AI Full Course with Projects](https://www.youtube.com/watch?v=9Crrhz0pm8s)
- **UP主：** freeCodeCamp.org
- **时长：** 4h33m
- **内容：** 从零到项目实战，Spring AI + Agent
- **推荐：** ⭐⭐⭐⭐⭐ 免费完整课程

#### 24. [Build a Deep Research Agent with Spring AI & Browserbase](https://www.youtube.com/watch?v=_amdeuCM-aY)
- **UP主：** Dan Vega
- **时长：** 16m
- **内容：** **最新！** 深度研究 Agent，浏览器操控，实操性极强
- **推荐：** ⭐⭐⭐⭐ 最新场景

#### 25. [Spring AI Orchestrator-Workers Pattern Tutorial](https://www.youtube.com/watch?v=NyJbDkY14fY)
- **UP主：** BootcampToProd
- **时长：** 21m
- **内容：** 编排器-工作流 Agent 模式，生产级架构
- **推荐：** ⭐⭐⭐⭐ 架构设计参考

#### 26. [Building Agentic Applications with Spring AI — GOTO 2025](https://www.youtube.com/watch?v=LsMXl1jbnvs)
- **UP主：** GOTO Conferences
- **时长：** 24m
- **内容：** GOTO 大会演讲，企业级 Agent 应用工程实践
- **推荐：** ⭐⭐⭐⭐ 会议演讲精华

#### 27. [How to Build Agents with Spring AI](https://www.youtube.com/watch?v=d7m6nJxfi0g)
- **UP主：** Microsoft for Java Developers
- **时长：** 30m
- **内容：** 微软官方 Step by Step Agent 构建
- **推荐：** ⭐⭐⭐⭐ 微软官方出品

#### 28. [Building Agents with AWS — Java, Spring AI, Bedrock & MCP](https://www.youtube.com/watch?v=Y291afdLroQ)
- **UP主：** AWS Developers
- **时长：** 27m
- **内容：** Bedrock + MCP 集成 Spring AI Agent
- **推荐：** ⭐⭐⭐⭐ AWS 云端部署参考

### B站视频

#### 29. [Spring AI 零基础到实战全套教程 — Tools + MCP + Agent](https://www.bilibili.com/video/BV1QCkYBnEtc/)
- **UP主：** B站
- **时长：** 48 集
- **内容：** 全流程覆盖，含大模型选型、LangChain4j 对比
- **推荐：** ⭐⭐⭐⭐⭐ B站最全 Spring AI 视频

#### 30. [Java AI Agent + Spring AI Alibaba Agent Framework](https://www.bilibili.com/video/BV1g49KBqE1g)
- **UP主：** 图灵官方
- **时长：** 9h39m
- **内容：** 整体结构 + Skill 全架构，7.3万播放
- **推荐：** ⭐⭐⭐⭐ 中文视频首选

---

## 🧠 推荐学习路径

```
阶段一：认知体系
├── 📖 Spring AI 官方文档 - Building Effective Agents (#16)
├── 🎬 Josh Long Workshop — Spring AI + MCP + Bedrock (#21)
├── 🎬 Dan Vega — AI for Java Developers 完整课程 (#22)

阶段二：动手实战
├── 📦 yu-ai-agent — 鱼皮实战项目 (#4)
├── 📦 spring-ai-alibaba/examples — 官方示例 (#3)
├── 📝 腾讯云 — Agent 核心能力解析 (#11)

阶段三：深度进阶
├── 📦 spring-ai-alibaba — 阿里 Agent 框架 (#2)
├── 📦 MCP Java SDK — 外部工具集成 (#7)
├── 📦 DataAgent — 数据智能体 (#5)
├── 📝 dev.to 系列 — Part1 到 Part5 (#20)

阶段四：架构设计
├── 🎬 Orchestrator-Workers Pattern (#25)
├── 🎬 GOTO 2025 — Agentic Applications (#26)
├── 📦 Atmosphere — 实时 Agent 传输层 (#6)
├── 📦 FIT Framework — Java LangChain 替代 (#8)
```

---

*资源持续更新中。如需将某篇具体文章读取整理到知识库，请告知。*
