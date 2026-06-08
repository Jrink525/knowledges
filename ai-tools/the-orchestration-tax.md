---
title: "The Orchestration Tax — 编排税：当你的注意力成为系统的瓶颈"
tags:
  - agentic-engineering
  - orchestration
  - cognitive-load
  - productivity
  - addy-osmani
date: 2026-05-30
source: "https://x.com/addyosmani/status/2059844244907696186"
authors: "Addy Osmani (Google Cloud AI Director)"
---

# The Orchestration Tax（编排税）

> **作者：** Addy Osmani（Google Cloud AI Director）
> **来源：** X/Twitter 长文（2026-05-28）
> **相关链接：**
> - Google I/O Panel：[Panel](https://www.youtube.com/watch?v=VTYx7Ex-0bA)
> - 前一篇：[Your Parallel Agent Limit](https://addyosmani.com/blog/cognitive-parallel-agents/)
> - Cognitive Surrender：[cognitive-surrender](https://addyosmani.com/blog/cognitive-surrender/)
> - Cognitive Debt：[Margaret-Anne Storey](https://margaretstorey.com/blog/2026/02/09/cognitive-debt/)

---

## 核心洞察

> "Starting more AI agents is easy now. However, more agents running doesn't mean there's more of you available — your cognitive bandwidth doesn't parallelize."

**Orchestration Tax** = 你忘记了自己是串行处理器，却用并发系统的方式工作所付出的代价。

---

## 一、不对称性：启动廉价，闭环昂贵

| 操作 | 成本 |
|------|------|
| 启动一个 agent | 极低（一次按键或一句话） |
| 闭环（检查结果 + 合并 + 排错） | 极高（需要你的判断力） |

**关键认识：** 启动 agent 简单，但**关闭 loop** 的成本才是真正的瓶颈。检查结果是否正确、与其它 agent 的改动 reconcile——这些都必须通过你。而你只有一个。

> "Starting an agent is very cheap... But closing the loop on the agent is not cheap at all."

---

## 二、你就是 GIL（全局解释器锁）

> "You are the GIL of your AI agents."

Python 的 GIL：你可以开无数线程，但同一时间只有一个能执行字节码。**你就是你 agent 系统的 GIL。**

- Agent 可以同时运行
- 但任何需要**真正理解架构**或**解决合并冲突**的工作，都必须"获得锁"
- **那个锁只有一把。你拿着它。**

### Amdahl's Law（阿姆达尔定律）

> "The speedup you get from parallelizing is capped by the fraction of work that stays serial."

加速比受**串行部分**的比例上限约束：
- 在 agent 开发中，串行部分 = **你的判断力**
- 启动 8 个 agent 不会加速你的判断时间——只是让等在你面前的队列变深
- **优化非瓶颈部分不增加吞吐量**——你只是在瓶颈前堆了一堆未完成的工作

**瓶颈是你的审阅步骤。你的系统吞吐量 = 这一步的吞吐量。**

---

## 三、"更努力"无法解决结构性瓶颈

> "I never felt more productive with my tools but I am also more tired than I ever been."

两句话都是真的，且根源相同。

**疲劳的具体原因：** 每一分钟你都是一个串行处理器跑到 100% 且没有任何 slack。

- 每次你检查一个 agent，都付出一次**上下文切换成本**
  - CPU 做上下文切换：微秒级，架构师仍在努力避免
  - 你做上下文切换：分钟级，而且永远无法完美 reload
- 5 个 agent 不是 1 倍工作量的 5 倍——它是 **5 次冷启动 + 一个后台焦虑进程**（"我该检查哪个？"）

### Cognitive Surrender（认知投降）

> "You either pay the tax deliberately or you let it quietly destroy your understanding of your own system."

如果你硬扛结构限制，它只会以另一种形式出现：
- 浅层 code review
- **认知投降**：你接受 agent 的代码，因为形成自己的判断需要你根本没有的注意力

---

## 四、像架构系统一样架构你的注意力

> "You are a component in that system. Your attention has a known, low serial throughput."

### 策略 1：Scale fleet to review rate（按审阅率扩容）

好的并发系统使用**背压（backpressure）**来防止队列无限增长。
- Producer（agent 数量）应该匹配 Consumer（你的审阅速度）
- 正确的并行 agent 数量 = **你能好好 code review 的数量**
  - 对大多数人来说：**低个位数**
- AI 工具让你随便开 20 个——但那只是一个 UI 功能，不代表你应该用它

### 策略 2：Sort the work（分类任务）

| 分类 | 特征 | 处理方式 |
|------|------|---------|
| **隔离任务** | 可放心委托给后台 | 异步运行，最后审阅 |
| **复杂任务** | 判断本身就是工作 | **不要并行！** 复杂任务并行只是"摔打锁"，所有输出都会变差 |

> "The big mistake is trying to parallelize the second pile."

### 策略 3：Batch your reviews（批量审阅）

- 同时审阅 4 个 agent 的产出比"检查一个 → 去做别的 → 冷启动回来"便宜得多
- 给 agent 更长缰绳，让工作堆积一点，批量处理

### 策略 4：Only spend the lock on judgement（只在判断上消耗锁）

不要浪费大脑在机器能自己验证的事情上：
- → 让 agent 写通过的测试
- → 让 agent 生成截图
- Agent 自己证明那 80% 的枯燥部分
- 你只花那 20% 真正需要人类的注意力

### 策略 5：Protect your serial time（保护你的串行时间）

> "Sometimes the highest leverage move is to stop orchestrating entirely, close the laptop full of agents and just think hard about one single problem with the lock held the whole time."

- 瓶颈需要你**最好的时间**，而不是 agent 检查之间的碎时间
- 最高杠杆操作：**停止编排**，关掉满是 agent 的电脑，用整块时间使劲想一个问题
- 编排不是真正的工作——它是**工作之上的开销**

---

## 五、忙 ≠ 高产

> "You can be maximally busy and barely produce anything. From the inside it feels identical."

**危险在于失败模式对你不可见：**
- 20 个 agent 在跑 → 给人类似"大规模产出"的感觉
- 仪表盘满了，一切都在动
- 但感觉与实际产出是解耦的

### 认知债务（Cognitive Debt）

Ciera Jaspan 引用了 Margaret-Anne Storey 关于债务的研究：
- 技术债务 + 认知债务
- 未偿还的编排税 = **两者同时累积**
- 你合并了你没好好读的代码
- 你的心智模型完全落后于代码库
- 今天不会暴露在仪表盘上——**它会在生产环境宕机时暴露**

---

## 六、关键总结

| 原则 | 一句话 |
|------|--------|
| **你是瓶颈** | 你就是 agent 系统的 GIL，唯一的串行资源 |
| **不对称性** | 启动 agent 极便宜，闭环极贵 |
| **Amdahl's Law** | 加速比受串行部分（你的判断）约束 |
| **背压** | 按审阅率扩容 agent，不是按 UI 允许的最大数 |
| **分类** | 隔离任务可并行，复杂任务必须串行思考 |
| **批量** | 集中审阅，减少上下文切换 |
| **锁只花在判断上** | 让机器证明 80%，你花注意力在 20% 上 |
| **保护串行时间** | 有时最高杠杆 = 关掉 agent 专心思考一个问题 |
| **忙 ≠ 产** | 20 个 agent 在跑的感觉和实际产出是解耦的 |

---

> "Spawning agents is not the skill. Anyone can run 20. The real skill is designing the system around the one serial resource that cannot be cloned or parallelized. That resource is your attention. Architect it the way you architect anything else you depend on in production."

---

*Processed on 2026-05-30 from [Addy Osmani's X thread](https://x.com/addyosmani/status/2059844244907696186)*
