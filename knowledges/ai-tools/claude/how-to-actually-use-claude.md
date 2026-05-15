---
title: "如何真正用好 Claude：18 个步骤解锁全部潜力"
tags:
  - claude
  - prompt-engineering
  - productivity
date: 2026-05-13
source: "https://x.com/anatolikopadze/status/2054568935274549597"
authors: "Anatoli Kopadze"
---

# 如何真正用好 Claude：18 个步骤解锁全部潜力

> **来源：** [How to Actually Use Claude. 18 steps that unlock 100% of its potential](https://x.com/anatolikopadze/status/2054568935274549597) — Anatoli Kopadze

![How to Actually Use Claude](../image/how-to-actually-use-claude-1.jpg)

Claude 发布两年了。每天使用它的人，大多数只用了它 10% 的能力。

不是因为它复杂。而是没人展示过剩下的 90% 长什么样。

这份指南会改变这一点。读完后，你的 Claude 会变成记住你、理解你、按照你思维方式工作的工作伙伴。

---

## 开始之前

### 1 — 创建 Project，而不是 Chat

每次你打开一个新的 Claude 对话，它从零记忆开始。不知道你的名字、你的工作、你的目标、你喜欢怎么沟通。你花前几条消息重新介绍自己——或者你干脆不介绍——然后 Claude 给了你一份跟你的工作方式完全不匹配的通用回答。

**Project 解决了这个问题。** Project 是一个持久工作空间，Claude 在里面每一次对话之间都保留上下文。你一次性设置好，之后每次对话 Claude 都已经知道你是谁。

去 Claude 侧边栏点击 Projects，创建一个新的。根据使用场景取名叫"工作"或"个人"。后续所有步骤都在这个 Project 内进行。

### 2 — 告诉 Claude 你是谁

在 Claude 能帮好你之前，它需要理解你。大多数人都跳过了这一步，然后奇怪为什么 Claude 给的答案总有点"不对劲"。

把你自己的背景信息粘贴到 Project 的 Knowledge Base 中，每个字段都如实填写。你越是具体，每一次回复的质量就越高。

模板参考：

```
## 关于我

- **角色 / 职业：** [你的职位、行业]
- **工作核心内容：** [你每天实际做什么]
- **技术栈 / 领域：** [你使用的工具、语言、框架]
- **沟通风格偏好：** [喜欢简洁/详尽、正式/随意]
- **常见目标：** [你希望 Claude 帮你解决的核心问题类型]
- **我不想要的：** [你不喜欢 Claude 做的——比如过度道歉、废话、列举模式]
```

把这个保存到 Project 的 Knowledge Base（知识库）中。Claude 会在该 Project 的每次对话开始时自动阅读。

### 3 — 把背景转化为自定义指令（Custom Instructions）

粘贴背景信息是个好的开始。但 **Custom Instructions** 更进一步。它们告诉 Claude 不仅是你是谁，还包括默认情况下如何与你互动。

把以下提示词发给 Claude（在你填完上面的模板之后）：

```
Based on the background information I shared, generate Custom Instructions for Claude that define:
1. How I want Claude to communicate with me (tone, length, level of detail)
2. Default behaviors (e.g., always ask clarifying questions before complex tasks)
3. Things to always do
4. Things to never do

Format this as something I can paste directly into Project Instructions.
```

把输出粘贴到 Project Instructions 中。这就成了 Claude 在这个 Project 中所有对话的永久操作模式。

---

## Claude 不是你想的那样

### 4 — Claude 不是搜索引擎

大多数人用 Claude 就像用 Google。输入一个问题，等待一个答案。这是**价值最低**的使用方式。

Claude 不是一个检索工具。它是一个**思考伙伴**。它不只是提取信息——它推理、综合、辩论、建立在上下文之上。如果你把它当搜索引擎用，就把它的价值砍掉了 80%。

**别再问 Claude "这是什么"了。开始让 Claude 帮你"思考"。**

不要这样问：
> 「What is prompt caching?」

要这样问：
> 「I'm building a workflow that calls Claude 20 times per session. Walk me through how prompt caching works and whether it would actually reduce my costs given that context.」

第二个提示给了 Claude 一个具体问题来解决。第一个只是让它背诵定义。

### 5 — 让 Claude 先问你问题

这是最强大的技巧之一，却几乎没人用。在 Claude 开始任何复杂任务之前，**让它先收集信息。**

当 Claude 在开始之前向你提问时，输出质量显著提升，因为它是建立在正确的基础上的。否则，Claude 只能做假设，然后你花时间纠正它本可以在第一次就做对的事情。

在重要任务前使用这个提示：

```
Before you start, ask me questions to gather the information you need. Don't begin until you have everything.

Ask me about:
- What I'm trying to achieve
- What constraints I'm working with
- What I've already tried
- What success looks like
- Anything else that would help you give me the best possible answer
```

或者针对特定任务：

```
I need you to [写一份架构设计文档/分析这段代码/...]. Before you start, ask me 3-5 questions that will help you tailor your response. Don't proceed until I've answered them.
```

---

## 连常规用户都不知道的

### 6 — 风格克隆（Style Cloning）

当 Claude 用你的声音写作却没有示例时，它用的是它自己的声音。输出语法正确，但语气完全不对。听起来像 AI，因为它本来就是。

给 Claude 3-5 份你自己的写作样本。让它分析你的**模式**，而不仅仅是描述你的风格。经过分析后，它能写出像你的文字，而不是像一个抛光过的企业助手。

```
Here are 3-5 samples of my writing. Analyze them to understand my patterns:

[sample 1]
[sample 2]
[sample 3]

After analyzing, write a brief style guide that captures:
- My typical sentence structure and length
- My vocabulary patterns
- My tone (formal/casual, direct/elaborate)
- Things I consistently do or avoid

Then use this style guide whenever you write for me.
```

### 7 — 把 Claude 当成你的"陪练"

大多数人让 Claude 帮他们"完善"想法。这意味着 Claude 在你说的基础上补充、扩展。你得到的是赞同和细化。

这在某些时候有用，但这不是测试想法的方法。

在做出任何计划、决定或写作之前，让 Claude **攻击**它。不是批评，是攻击。区别很重要。

```
I need you to attack this idea. Not critique it — attack it.

[your idea, plan, or writing]

Find every weakness. Tell me why this won't work. What assumptions am I making that aren't true? What blind spots does this have? What would a smart person who disagrees with me say?

Be ruthless. I need to find the real problems before they cost me.
```

### 8 — 扩展思维（Extended Thinking）

大多数 Claude 用户从未打开过这个功能。**Extended Thinking** 是一种模式，Claude 在给出答案之前会逐步推理问题，而不是直接跳到输出。

简单任务不需要它。但对于复杂决策、分析或任何你想让 Claude 真正思考（而不是模式匹配）的问题，打开它。

在 Claude 界面中，发送消息前点击大脑图标。或者在提示词中加入：

```
Take a deep breath and work through this step by step. Think through multiple angles before arriving at your answer. Show your reasoning.
```

在困难问题上，输出质量的差距是显著的。

### 9 — 让 Claude 为 Claude 写提示词

这是最被低估的技巧。如果你不确定如何为特定任务提示 Claude，**让 Claude 替你写提示词。**

Claude 知道什么样的指令会产生更好的结果。让它为你利用这个知识。

```
I need to get Claude to [你想完成的任务]. Write a prompt for me that will get the best possible result. Include:
- What context to provide
- How to structure the request
- Any specific instructions or constraints to include
- What tone/format to request

Explain why each element matters.
```

---

## 如何花更少的 Token，获得更多

### 10 — 指定输出长度

Claude 的默认行为是写它认为合适的长度。通常比你需要的长——这意味着更多的 token 消耗、更多的阅读时间、更多的噪音。

在 Claude 开始之前，告诉它你想要的答案有多长。

```
Keep your answer concise — no more than [3 paragraphs / 200 words / 5 bullet points]. I only need the key information, not the full context.
```

或者：

```
Start with a one-sentence summary, then provide up to 3 bullet points of detail. That's all I need.
```

这一条指令就能把大部分任务的 token 消耗降低 **40%-60%**，同时不损失你实际需要的价值。

### 11 — 去掉开场白

每次 Claude 的回复默认会以一些你没要求的东西开始：「好问题，让我为你分析一下。」或者完整复述你刚说过的内容。或者免责声明。或者总结一遍刚刚告诉你的东西。

你从没要求过这些。它消耗 token，浪费你的时间。

加到你的 Custom Instructions 中：

```
When responding:
- Do not start with phrases like "Great question" or "Let me break this down"
- Do not restate my question back to me
- Do not add disclaimers unless there's a genuine risk of harm
- Do not end with a summary that repeats your key points
- Just give me the answer I asked for, directly
```

### 12 — 不要每次对话都重新解释

如果你每次新对话都在粘贴同样的背景信息——你每次都在浪费 token，还在培养一个随着 Claude 用量增加而成本递增的坏习惯。

这就是 **Projects** 和 **Custom Instructions** 的目的。一次性放入上下文。让 Claude 每次自动读取。永远不要再粘贴你的背景。

如果你还没开始用 Projects，在读完这篇文章的其他部分之前，先从那里开始。

### 13 — 新话题开新对话

Claude 会带上同一个对话中之前说过的所有上下文。当你在一个长对话中切换话题时，Claude 仍然加载着之前的内容。这意味着每次回复消耗更多 token，处理变慢，还可能发生上下文污染——早期对话的内容影响你的新话题。

当你要切换到一个不相关的话题时，在同一个 **Project** 内开一个新的对话。你保留了 Project 的记忆，甩掉了无关的 baggage。

---

## 立即可用的提示词

这些是你可以直接复制使用的完整提示词。

### 14 — 用类比理解任何东西（费曼学习法）

Claude 默认的解释通常技术上正确，但实际无用。它们使用和你试图理解的内容相同的词汇——你得到了定义，但没有真正的理解。

费曼方法通过简洁来强迫理解。如果 Claude 不能通过类比用平实的语言解释，说明这个解释本身还不够清楚。这个提示适用于从投资到量子物理、再到某个 API 如何工作的所有问题。

```
Explain [topic] to me using the Feynman technique:
1. Start with a simple analogy a 10-year-old could understand
2. Build on that analogy layer by layer
3. For each new concept, check if I understand by asking me to explain it back
4. If I get something wrong, use a different analogy

The goal is not to be technically exhaustive. The goal is for me to genuinely understand.
```

### 15 — 围绕你的旅行习惯制定旅行计划

大多数旅行计划从目的地开始，以你在任何旅行博客上都能找到的通用行程结束。Claude 可以做得不同：围绕你的具体旅行风格、节奏、预算和对你来说真正重要的东西来制定计划。

关键在于给它关于你的真实信息，而不仅仅是日期和地点。

```
Help me plan a trip to [destination] from [dates]. But don't give me a generic itinerary.

Instead:
First, ask me questions about how I actually travel:
- Do I prefer packed schedules or slow days?
- Do I want famous landmarks or hidden local spots?
- Budget range and where I'm willing to splurge vs save
- Food preferences (fine dining vs street food vs cooking)
- Energy levels — am I the type to do 8 walks in a day or 2 with a long lunch?

Then build an itinerary that fits how I actually travel, not how travel blogs think I should.
```

### 16 — 月度开支分析，带真实结论

大多数人看一眼银行账单，感到一种模糊的不好，但并不真正了解自己的钱花在了哪里。Claude 可以把原始数据变成清晰的画面——并告诉你应该怎么做。

用真实数据，不要估算。

```
I'm going to paste my bank statement / expense data. I need you to:
1. Categorize every expense (you may need to make reasonable guesses)
2. Show me what percentage of my income goes to each category
3. Identify patterns — recurring expenses I might have forgotten about, categories that are higher than typical
4. Give me 2-3 specific, actionable recommendations

Here's my data:
[paste expenses]

Be honest. I need real analysis, not reassurance.
```

### 17 — 把 Claude 当成个人思考伙伴

大多数人生活中没有一个会不带评判地倾听、问对的问题、帮你理清思路而不推销自己议程的人。Claude 可以填补这个角色——但你必须给它正确的指令。

这不是治疗。这是结构化的自我反思，加上一个外部视角，帮助你更清晰地思考。

```
I need you to be my thinking partner. Not an advisor, not a therapist — a partner.

Here's what I'm struggling with:
[describe the situation or decision]

Now:
- Ask me questions to help me clarify what I actually think
- Point out any contradictions or assumptions in my thinking
- Help me see angles I might be missing
- Don't tell me what to do — help me figure out what I want to do

Start by asking me the first question.
```

### 18 — 在你投入之前先测试任何商业想法

大多数商业想法死掉是因为人们在测试之前就爱上了它们。他们花了几个月去构建没人想要的东西——因为他们从未诚实地问过这个想法是否真的好。

Claude 可以充当一个冷酷的第一层过滤器。不是为了杀死想法，而是为了在它们花费你的时间和金钱之前找到真正的问题。

```
I have a business idea I want to stress-test. Be completely honest — I need to know if this is worth pursuing before I invest time and money.

Here's the idea:
[describe your idea]

Now I need you to:
1. What problem does this solve? Is it a real problem people would pay for?
2. Who is the customer? Is this a big enough market?
3. What alternatives already exist? Why would someone choose this instead?
4. What's the hardest part of making this work?
5. What would you tell me if I were your friend asking for honest advice?

Don't soften anything. The most valuable thing you can give me right now is the truth.
```

---

## 真正的重点

Claude 不比你聪明。它的想法也不比你的好。它拥有的是：**无限的耐心**、**广博的知识**、以及从你没想到的角度思考问题的能力。

从 Claude 获得最多的人，不是那些问题最好的人。他们是那些已经设置好 Claude 来理解自己、给了它真实上下文、并知道如何把它当作伙伴而不是自动售货机来用的人。

大部分人读完这篇文章，还是会和以前一样打开 Claude。

**一次性设置好。永久改变你的工作方式。**

---

*整理于 2026-05-13，来源：[X/Twitter @AnatoliKopadze](https://x.com/anatolikopadze/status/2054568935274549597)*
