---
title: "从 Prompt Engineer 到 Full Stack AI Engineer — @hooeem 完整指南"
tags:
  - ai
  - prompt-engineering
  - ai-engineering
  - llm
  - agents
  - mcp
  - guardrails
  - workflow
date: 2026-05-28
source: "https://x.com/hooeem/status/2059640615344754947"
authors: "@hooeem"
---

# 从 Prompt Engineer 到 Full Stack AI Engineer

> 原文：[@hooeem on X](https://x.com/hooeem/status/2059640615344754947)  
> 本文为中文翻译整理，保留原文语气和结构。

---

## 核心观点

> **"Prompt engineering 从未死亡，但 prompt-only thinking 确实死了。"**

Prompt 仍然是你和模型之间的接口——
- 糟糕的 prompt 产生糟糕的输出
- 模糊的指令产生模糊的答案
- 缺少上下文导致模型胡乱猜测

但**只懂 prompt 只是触及表面**。真正的 AI engineer 会设计可重复的系统，让 AI 输出**每周都可靠**。

---

## 第 1 章：改变你使用 AI 的方式

### ❌ 错误思维
> 我有一个任务 → 我输入任务 → 模型给答案 → 我凭感觉判断

### ✅ AI Engineer 思维
> 我有一个任务 → 我定义预期结果 → 我决定需要什么信息 → 我选择合适模型 → 我定义输出结构 → 我决定是否需要工具或检索 → 我定义什么算成功 → 我用标准验证结果 → 我改进系统

### 🎯 终极问题
- ❌ "我现在该用什么 prompt？"
- ✅ **"我怎样让这个输出每周都可靠？"**

---

## 第 2 章：Specificity（具体性）

模糊的 prompt 迫使模型自行填补细节——有时猜对，但更多时候猜错。

| 旧方式 | 更好方式 |
|--------|---------|
| "Make this better." | "Rewrite this newsletter introduction to make it sharper, more direct, and more credible. Constraints: Keep core argument unchanged. Remove vague claims. Add a strong first sentence. Keep it under 180 words." |

具体性应该能回答这些问题：
- 这是什么任务？
- 目标是什么？
- 受众是谁？
- 预期输出是什么？
- 成功标准是什么？
- 约束是什么？

---

## 第 3 章：Roles（角色）

> 为什么 Karpathy 对所有任务都用同一个 role prompt？**因为它真的有效。**

Role 帮助定义模型的行为边界和判断标准。一个可复用的 role prompt 模板：

```
You are an AI assistant. Your task is to...
Key principles:
- ...
- ...
- ...
Think carefully before answering.
```

---

## 第 4 章：Using Examples（使用示例）

示例用来告诉模型你想要的**模式**，包括：
- **结构**（structure）
- **语气**（tone）
- **推理模式**（reasoning pattern）
- **分类方式**（categorisation）
- **输出形状**（output shape）
- **细节程度**（level of detail）

> **关键原则**：
> - 坏示例 → 毒化模型
> - 不一致示例 → 得到垃圾输出
> - 与指令矛盾的示例 → 模型困惑、全部搞砸

---

## 第 5 章：Reasoning（推理）

### ❌ 旧方式
> "think step-by-step" 和 "show your full reasoning"

### ✅ 更好方式
> "reason carefully, then give me the useful audit trail"

对推理模型来说，只需要：
1. **Final answer**（最终答案）
2. **Key reasoning checkpoints**（关键推理检查点）
3. **Assumptions**（假设）
4. **Uncertainties**（不确定性）
5. **How I can verify this**（如何验证）

---

## 第 6 章：Output Control（输出控制）

根据任务选择合适的输出格式：

| 受众 | 输出格式 |
|------|---------|
| 直接阅读 | Markdown / 结构化文本 |
| 系统解析 | JSON Schema（Structured Outputs） |

> **不要混淆"好看"和"可靠"。**
> 输出要为当前任务服务。

---

## 第 7 章：Iteration & Follow-up（迭代与跟进）

| ❌ 旧方式 | ✅ 更好方式 |
|----------|-----------|
| "Try again. Make it better." | 明确指出哪里不对、需要怎么改、保持什么不变 |

想提修改意见时，问自己：
- 哪些部分需要改变？
- 改成什么样？
- 哪些部分必须保持不变？
- 修改到什么程度算满意？

---

## 第 8 章：Constraints（约束）

**约束不是可选的——它们是任务的一部分。** 模型不知道边界在哪里，必须由你定义。

### ❌ 烂约束
- "Do not sound like AI"
- "Do not be boring"

### ✅ 好的约束框架

**要避免的具体内容：**
- "In today's fast-paced world"
- "It's important to note"
- "it's not X, it's Y"
- 无示例的模糊声称
- em dashes（——）
- 鸡汤式结尾

**需要设置的边界：**
1. **Style**（风格）
2. **Scope**（范围）
3. **Evidence**（证据要求）
4. **Authority**（权威性）
5. **Safety**（安全性）
6. **Output**（输出格式）
7. **Time**（时间）
8. **Quality**（质量标准）

---

## 第 9 章：Context Engineering（上下文工程）

> **Prompting 问的是：** "我应该对模型说什么？"  
> **Context Engineering 问的是：** "模型需要知道什么才能做好工作？"

如果不提供目标、偏好、示例、源材料、约束、评分标准、过往决策——模型就会猜，然后搞砸。

一个完整的上下文包应包括：
- 任务目标
- 用户/受众
- 项目背景
- 源材料
- 偏好设置
- 约束条件
- 已锁定的决策
- 已知失败模式

> **注意：上下文是昂贵的。** 过长的不必要上下文会稀释注意力、增加成本、制造冲突。  
> **More context ≠ better context.**

---

## 第 10 章：Retrieval（检索）

> 如果答案依赖事实，模型需要外部来源。**只靠措辞无法解决事实不确定性。**

检索包括：
- 网络搜索
- 文件搜索
- 数据库查询
- 文档检索
- 向量搜索
- 关键词搜索
- 知识库查询
- 引用检索

**检索前的自检清单：**
- 什么问题需要外部证据？
- 允许哪些来源？
- 优先哪些来源？
- 信息需要多新？
- 模型应该引用、引用+引用还是总结？
- 来源冲突时怎么办？
- 找不到来源时怎么办？

---

## 第 11 章：Tool Use & Function Calling（工具使用与函数调用）

> 这是 AI 开始**做事情**而不是**说事情**的地方。

Function Calling 让模型能通过自然语言连接到外部工具和 API。

**工具层设计需要考虑：**
- 哪些工具可用？
- 什么条件下使用工具？
- 什么条件下不使用工具？
- 工具失败时的行为？

---

## 第 12 章：MCP 与连接的 AI 工作流

Model Context Protocol（MCP）是 Anthropic 在 2024 年推出的开放标准，用于连接 AI 应用到外部数据源和工具。

**MCP 安全最佳实践：**
1. 不要连接到一切
2. 不要信任每一个工具
3. 不允许悄无声息的高风险操作
4. 不要假设工具描述是无害的

---

## 第 13 章：任务链、工作流与 Agents

> **你不一定需要 agent。**

| | Workflow | Agent |
|---|---|---|
| **适用场景** | 步骤可预测 | 步骤需要动态发现 |
| **路径** | 固定序列 | 动态规划 |
| **自主性** | 低 | 高 |

**决策指南：**
- 用 **workflow** 当步骤是确定的
- 用 **agent** 当步骤必须动态发现

---

## 第 14 章：Testing（测试）

创建 **evals（评估集）** 来监控 prompt 性能。随着 prompt 变复杂或模型版本变化，eval 能帮你保持质量。

---

## 第 15 章：Guardrails（护栏）

Guardrails 是伴随 agent 运行的**输入 + 输出检查**。

**Guardrail 检查清单：**
1. 识别系统的目的
2. 识别它能执行的操作
3. 对每个操作分类风险等级
4. 决定哪些操作无需审批
5. 决定哪些操作需要审批
6. 决定哪些操作禁止
7. 添加输入 guardrails
8. 添加输出 guardrails
9. 添加工具 guardrails
10. 添加数据/隐私 guardrails
11. 添加范围 guardrails
12. 添加成本/用量 guardrails
13. 添加停止条件
14. 添加不确定性规则
15. 添加升级规则

> 你总不希望你的 agent 莫名其妙把你所有邮件删掉吧。

---

## 第 16 章：Image Prompting（图像提示）

作为 AI engineer，图像生成能力也很重要。

- prompt 应该**描述交付物**，而不是描述场景
- 使用结构化模板：目标 → 交付物 → 画布 → 受众 → 主体 → 构图 → 风格 → 文字 → 约束 → 迭代说明

---

## 第 17 章：Multimodal Prompting（多模态提示）

不再只给 AI 文本。还可以给：
- 截图
- 图表
- PDF
- 电子表格
- 图片
- 图表
- 音频转录
- UI 原型
- 代码文件
- 文档
- 幻灯片

然后告诉模型**执行什么类型的阅读**。

---

## 第 18 章：构建你的 AI Engineering Stack

> 这是整篇文章最精华的部分——目标是构建**可复用的 AI 系统**。

### 如何开始？

先问自己：
1. 这个系统是为哪个任务服务的？
2. 应该产生什么结果？
3. 需要什么上下文？
4. 什么输出格式有用？
5. 是否需要外部来源？
6. 是否需要工具？
7. 应该是 workflow 还是 agent？
8. 如何评估质量？
9. 哪些需要审批？
10. 应该记录什么并如何改进？

### Step 1：定义 Purpose Layer（目的层）

> 这个 AI 系统究竟是做什么的？

**模板：**
```
System name: [名称]
Primary job: 帮助我 [做什么] 通过 [怎样做]
User: 为 [我 / 我的团队 / 我的客户 / 我的受众] 服务
Main output: 产出 [简报 / 草稿 / 分析 / 计划 / 报告 / 图片 / 决策 / 摘要]
Success looks like: 好的输出是 [准确 / 有用 / 结构化 / 有来源 / 可直接发布]
This system does not: 它不做 [发送 / 发布 / 删除 / 花钱 / 做出最终决定 / 伪造来源 / 未经审批操作]
```

### Step 2：定义 Prompt Layer（提示层）

定义模型应该如何表现。不只是 "Act as an expert"，而是：

**需要定义：**
- Role（角色）
- Job（任务）
- Standards（标准）
- Decision rights（决策权限）
- Boundaries（边界）
- Uncertainty behaviour（不确定性行为）

### Step 3：定义 Context Layer（上下文层）

大多数人在这里做得不够。他们要求高质量输出却不给模型任何有用的上下文。

**包括：**
- 目标上下文
- 用户/受众上下文
- 项目上下文
- 源材料
- 偏好
- 约束
- 决策历史
- 已知失败模式

### Step 4：定义 Output Layer（输出层）

控制模型返回的内容。不要模糊。

**必要部分：**
- 主要格式（Markdown / JSON / 表格 / 清单）
- 必需章节
- 置信度
- 不确定性标记
- 可操作性（下一步行动）

### Step 5：定义 Retrieval Layer（检索层）

当模型需要超出 prompt 的信息时使用。

**源优先级：**
1. 最高权威来源
2. 次优来源
3. 第三来源
4. 弱信号来源

**冲突规则**：如果来源冲突，解释冲突并优先最高权威来源。

### Step 6：定义 Tool Layer（工具层）

工具不仅包括"哪些可用"，还包括**什么条件下、需要什么审批**。

**权限模型：**
- 无需审批的安全操作
- 需要审批的风险操作
- 禁止的操作
- 工具失败时的行为

### Step 7：决定 Workflow 还是 Agent

不要默认用 agent。Workflow 更好当路径可预测时。

### Step 8：定义 Evaluation Layer（评估层）

**评分标准（1-5 分）：**
- 准确性
- 完整性
- 有用性
- 格式遵循
- 来源质量
- 具体性
- 风险控制

### Step 9：定义 Guardrail Layer（护栏层）

定义系统**绝对不能做的事**。

### Step 10：定义 Logging Layer（日志层）

记录：任务、输入、prompt 版本、工具调用、来源、输出、评分、失败、改进点。

### Step 11：定义 Improvement Layer（改进层）

把一次性 prompt 转化为不断进化的系统。每次使用后问：什么有效？什么无效？下次怎么改进？

---

## 第 19 章：总结

### AI Engineer 清单

**Prompt 质量清单：**
- [ ] 明确的任务
- [ ] 明确的目标
- [ ] 定义了受众
- [ ] 提供了上下文
- [ ] 包含了约束
- [ ] 指定了输出格式
- [ ] 列出了失败模式
- [ ] 定义了成功标准

**上下文质量清单：**
- [ ] 包含目标
- [ ] 包含相关背景
- [ ] 提供了源材料
- [ ] 包含了偏好
- [ ] 包含了约束
- [ ] 移除了无关上下文
- [ ] 解决了上下文冲突

**输出 Schema 清单：**
- [ ] 选择了正确格式
- [ ] 定义了必填字段
- [ ] 处理了可选字段
- [ ] 定义了空状态
- [ ] 需要时包含置信度
- [ ] 处理了错误

**检索清单：**
- [ ] 外部事实需要来源
- [ ] 定义了源优先级
- [ ] 声明了时效性要求
- [ ] 处理来源冲突
- [ ] 标记缺失证据
- [ ] 需要引用时包含引用

**工具使用清单：**
- [ ] 工具用途明确
- [ ] 参数已定义
- [ ] 定义何时使用
- [ ] 定义何时不使用
- [ ] 定义工具失败行为
- [ ] 定义审批规则
- [ ] 记录日志

**Workflow vs Agent 决策：**
- 用 Workflow 如果：步骤可预测、来源已知、工具固定、风险低、可靠性优先
- 用 Agent 如果：步骤未知、工具选择动态、需要开放式搜索、需要迭代规划

**Eval 清单：**
- [ ] 正常用例
- [ ] 脏数据用例
- [ ] 边界用例
- [ ] 对抗性用例
- [ ] 需要澄清的用例
- [ ] 拒绝回答的用例
- [ ] 评分规则
- [ ] 失败日志
- [ ] 回归测试

**Guardrail 清单：**
- [ ] 定义了允许的操作
- [ ] 定义了需审批的操作
- [ ] 定义了禁止的操作
- [ ] 处理了敏感数据
- [ ] 定义了停止条件
- [ ] 定义了升级规则
- [ ] 工具权限已限定

**AI Engineering Stack 清单：**
- [ ] Prompt layer
- [ ] Context layer
- [ ] Output layer
- [ ] Retrieval layer
- [ ] Tool layer
- [ ] Workflow / Agent layer
- [ ] Evaluation layer
- [ ] Guardrail layer
- [ ] Logging layer
- [ ] Improvement loop

---

> 🎪 **三个 BOOM！**  
> 原作者花了大量时间写这篇文章。如果你读到这里，**别忘了给个赞或回复** 🙏

---

*译文整理于 2026-05-28，保留原文语气和风格。*
