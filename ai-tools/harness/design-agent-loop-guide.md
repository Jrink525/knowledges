# Agent 循环设计指南：如何搭建一个自动提示 Agent 的循环系统

> 原文：[How to design a loop that prompts your agent?](https://x.com/amitiitbhu/status/2063983640535847093)
> 作者：Amit Shekhar（@amitiitbhu，Outcome School 创始人）
> 日期：2026-06-08

## 核心思想

**Prompt 是一步棋，Loop 是整盘棋的策略。**

大多数人认为用 AI Agent 就是写好一个 prompt。但真实场景需要多步协作——写代码 → 跑测试 → 失败 → 读错误 → 修复 → 再次测试 → 直到通过。手动敲每一轮 prompt 不可扩展。于是需要设计一个循环系统（loop），让系统自动生成 prompt，一轮接一轮，直到任务完成。

---

## 循环的五大部分

### Step 1：定义「完成」的标准

在写任何代码之前，先回答：循环怎么知道任务结束了？

用代码写一个 `is_done` 检查函数，而不是记在脑子里。例如：
- 测试全部通过
- 输出匹配某个 schema
- 分数超过某个阈值

每次循环结束后调用这个函数，返回 True 则停止。

### Step 2：构建上下文，而非指令

大多数人犯的错：每次手动输入指令。正确做法是**从系统状态自动拼装 prompt**。

上下文包括：
- 当前处理中的文件
- 可用工具
- 上次运行的错误日志
- 已尝试的历史记录

核心思路：**循环本身不变，只有状态变了，prompt 也随之变化。**

### Step 3：让 Agent 执行并捕获一切

发送 prompt → Agent 执行 → 捕获完整输出：
- 代码 diff
- 标准输出
- 错误信息
- 系统新状态

**关键：输出不是终点，而是下一轮 prompt 的原料。**

### Step 4：反馈闭环

把结果送入 `is_done` 检查：
- ✅ 通过 → 停止，任务完成
- ❌ 失败 → 自动将失败信息转化为下一轮的 prompt

Agent 自我重提示：失败信息自动成为下一轮指令，无需人工干预。

### Step 5：设置终止条件

没有出口的循环是无限烧钱。设置护栏：
- **重试上限** — 超过固定次数即使未完成也停止
- **成本上限** — 超出预算立即停止
- **人工检查点** — 删除文件、转账、推送到生产等不可逆操作前暂停，等人确认

---

## 完整循环

```python
def agent_loop(goal, files, max_turns=10, budget=None):
    state = {"goal": goal, "files": files, "error": None, "turns": 0}
    cost = 0

    while state["turns"] < max_turns and cost < budget:
        prompt = build_prompt(state)
        result = run_agent(prompt)
        state = update_state(state, result)
        cost += result.cost

        if is_done(result):
            return result

    return {"status": "max_turns_exceeded", "state": state}
```

**永远有出口** — 任务完成、超限、超预算，三者必有其一。

---

## 一次运行示例

目标：「修复登录 bug」
- **Turn 1**：Agent 修改代码 → 测试失败（"password check returns true for empty password"）→ 记录错误到 state
- **Turn 2**：`build_prompt` 自动包含该错误信息 → Agent 修复对应行 → 测试通过
- **Turn 3**：不存在。`is_done` 返回 True，循环自动停止。

全程未手动输入任何 prompt。

---

## 循环的运行成本

写代码便宜，但循环跑一轮又一轮不便宜。

- 每一轮都调用模型，都有成本
- 跑一整夜的循环可能成千上万轮
- **成本控制比写好一个 prompt 更重要**

所以 Step 5 的终止条件至关重要。

---

## 可复用技能（Skills）

循环只是「管道」，真正价值在于它调用的 skills。

**规则**：当发现重复做同一件事 → 把它抽取为独立的 skill。破解一个难题后 → 保存为 skill。后续循环几乎零成本调用。

- 无 skills 的循环：每轮从零开始解决问题
- 有 skills 的循环：随积累越变越强，而不是单纯烧钱

---

## 常见错误

| 错误 | 后果 |
|------|------|
| 没有 done 检查 | 循环永不停 |
| 手动输入 prompt | 不是循环，是在替 Agent 干活 |
| 丢掉输出 | 下一轮没有原料 |
| 没有终止条件 | 无限循环、无限烧钱 |
| 对一次性任务也用循环 | 简单 prompt 就够 |
| 循环内无 skills | 每轮重算，浪费 token |

---

**总结：不要一步一步下棋。设计一套规则，让它自己下完一盘棋。**
