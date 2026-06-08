# 六大 Agent 上下文压缩策略分析

> 来源：腾讯技术工程 —— 《Claude Code、Codex、OpenCode 们到底怎么压上下文？分析完 6 家，我们做了第 7 个》
> 2026-06-08

---

## 测试场景

> 15,400 tokens 的登录 Bug 修复对话（26 条消息），其中工具结果占 81%。

## 三剑客对比

### 1. Codex CLI

**策略：单层摘要替换（"工作交接单"）**

- 本地路径（compact.rs）：客户端构造 Summarization Prompt → LLM 生成摘要
- 远程路径（compact_remote.rs）：调用 OpenAI 内部端点
- 4 个核心要点：当前进展 / 关键决策 / 约束和偏好 / 剩余待办
- 物理删除所有 Assistant 回复和 Tool 消息，原封不动保留所有 User 消息
- 自动触发 → 如果空间还不够 → 头部修剪

**优缺点：**
✅ 直觉性强，交接摘要概念易懂
❌ 一刀切，摘要遗漏关键细节就找不回来

---

### 2. Claude Code

**策略：三层递进机制**

#### 第一层：工具结果修剪（无 LLM 开销）
- 规则引擎，纯本地，每次请求前自动执行
- 始终保护最近若干个工具调用
- 超出范围 → 替换为 `[Old tool result content cleared]` 占位符
- **"选择性失忆"**：记得做过操作，不记得具体内容，需要时会重新发起

#### 第二层：Prompt Cache 友好
- 保持消息序列前缀不变（只在尾部裁减）
- 让 Anthropic API 的 Prompt Cache 命中率最大化

#### 第三层：9 部分结构化 LLM 总结（最后手段）
- 自动压缩触发阈值：有效上下文窗口 - 13,000 tokens
- 先尝试 Session Memory Compact（无需 LLM 调用）
- 回退到 LLM 总结：9 个固定部分，要求直接引用原文短语
- **善后处理（"状态重构"）**：注入引导语 + 自动重新读取最近编辑的文件（最多 5 个，50,000 tokens）+ 重新声明工具和技能定义
- 被动兜底：API 返回 prompt_too_long → 自动反应式压缩并重试

**优缺点：**
✅ 最省钱：大多数情况只需第一层或 Session Memory
✅ Prompt Cache 深度优化
❌ 实现最复杂

---

### 3. OpenCode

**策略：先修剪再摘要（"阶梯治理"）**

#### 第一步：Prune（标记隐藏，非物理删除）
- 释放 < 20,000 tokens 不执行
- 始终保留最近 40,000 tokens
- skill 类型输出永不修剪
- 保护最近 2 个用户回合

#### 第二步：LLM 5 标题摘要
- 隐藏的 Agent 调用 LLM（不干扰用户）
- 5 个固定标题：目标、已发现的代码和文件、已创建的修改、关键决策、待办事项
- **自动重放最后一条用户消息**（用户感知不到压缩）
- 跟随用户语言

**优缺点：**
✅ 代码全开源，TypeScript，Effect-TS 架构现代
✅ 非物理删除为历史回溯留空间
✅ 对开发者最友好，易定制

---

## 总对比

| 维度 | Codex CLI | Claude Code | OpenCode |
|------|-----------|-------------|----------|
| 压缩层次 | 单层（摘要） | 三层（修剪/缓存/摘要） | 两层（隐藏/摘要） |
| LLM 调用 | 必须 | 仅在第三层 | 仅在第二步 |
| 用户消息 | 永久保留原始 | 摘要化（第三层） | 摘要化 + 重放最后一条 |
| 工具结果 | 物理删除 | 占位符替换 | 时间戳标记隐藏 |
| 缓存优化 | 无 | 深度集成 Prompt Cache | 侧重减少重复读取 |
| 压缩后行为 | 被动等待 | 主动重读相关文件 | 自动重放最后指令 |

## 核心洞察

> **最好的上下文管理不是无限扩大记忆容量，而是学会精密地遗忘。**

## 参考来源

- Codex CLI: https://github.com/openai/codex
- Claude Code 社区资料: https://github.com/Piebald-AI/claude-code-system-prompts
- Claude Code's Compaction Engine: https://barazany.dev/blog/claude-codes-compaction-engine
- OpenCode: https://github.com/anomalyco/opencode
