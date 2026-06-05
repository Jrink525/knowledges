---
title: "Benedict Evans 的 AI 理性思考：工作、竞争与采纳"
tags:
  - ai
  - benedict-evans
  - job-automation
  - openai-strategy
  - ai-adoption
date: 2026-06-04
source: "https://www.lennysnewsletter.com/p/a-rational-conversation-on-where"
authors: "Benedict Evans"
---

# Benedict Evans 的 AI 理性思考

> **提炼来源：** Lenny's Podcast (2026.5.31) + Benedict Evans 博客文章  
> Benedict Evans 是独立分析师、前 a16z 合伙人，被誉为硅谷"最清醒的 AI 思考者"

---

## 一、核心论调：AI 是 1997 年的互联网

> "AI is as big a deal as the internet or mobile—and only as big."

核心观点：AI 的变革尺度跟互联网和移动互联网是一个级别的，但**也只是**这个级别。这意味着：
- 市场极大，但早期极度不确定
- 真正的价值分布还很模糊
- 现在看起来"输"或"赢"的，最终都可能反转

---

## 二、AI 与工作的关系（最新文章，2026.5.24）

**标题：Predicting AI Job Exposure**

### 核心主张：你无法预测

Benedict 尖锐地指出——大量研究报告/咨询报告试图用 O*NET 等数据建模"哪些岗位受 AI 影响最大"，但这**基本不可能**。他用三个反例证明：

### 反例 1：三磅测试（CPA 测试）

> "We spent a century automating accounting — yet the number of accountants kept going up."

过去 50 年，财务领域经历了：计算器 → 打孔卡 → 大型机 → 数据库 → PC → 电子表格 → ERP → 云——半个科技行业都在自动化会计。结果会计师数量不降反升。

三个原因：
1. **法规变化**：新监管创造新需求（经济学的 *ceteris paribus* 不成立）
2. **Jevons 悖论**：某件事变便宜了，你不会少做——你会做更多。DCF 从一周变成 30 秒 → 你做更多 DCF
3. **岗位本质变了一样，title 没变**：今天的"会计师"和 1970 年的"会计师"干的是不同的活，但 Census 把他们归在同一类

### 反例 2：报纸测试

互联网没有改变"当一个好记者需要什么技能"，但它改变了商业形态——记者的工资是靠"印刷 + 卡车运输 + 分类广告垄断"的生意模式付的。

**关键洞察：** 很多人的工作本身不受 AI 影响，但他们公司依赖于另外一些高度受 AI 影响的岗位。反向也一样。

### 反例 3：Uber 测试

> "If you'd been calculating 'internet exposure' by occupation in 1995, are you confident you'd have put taxi drivers on the list?"

2000 年代所有人都在讨论 LBS，但没人想到这会让出租车行业天翻地覆。如果你在 2005 年做"智能手机影响分析"，你能把出租车司机排在受影响列表上吗？

### 核心论点

> "You don't know what jobs are today, and you don't know how they will change."

三条判断原则（你的分析模型必须能通过这些测试）：
1. **Newspaper test** — 能预测互联网对报业的影响吗？
2. **Uber test** — 能预测智能手机对出租车的影响吗？
3. **CPA test** — 能预测自动化反而增加会计师人数吗？

如果不能，那你的模型就是"方向正确但毫无预测价值"。

> "On average, we're all dead. Half the jobs might be entirely unaffected."

---

## 三、OpenAI 如何竞争？（2026.2.19）

### 四个战略问题

**1. 没有护城河**
- 有 800-900M 月活用户，但 80% 每天发不到 3 条消息
- 市场上有 6+ 家竞争前沿模型，能力大致持平，每几周互相追赶
- 没有任何已知的网络效应让某一家甩开对手

**2. 真正的价值在上层**
- 大部分价值和利润将来自还没被发明出来的新体验
- OpenAI 不能自己发明所有东西

**3. 没有现有业务支撑**
- 不像 Google/Meta/Apple 有现金牛业务做靠山
- 史上最资本密集的行业之一，烧钱靠融资

**4. 产品团队不掌控路线图**
- 引述 OpenAI CPO Fidji Simo："研究人员晚上发消息说'我搞出了很酷的东西'，我的工作就是把它变成按钮"
- Product strategy 发生在别处

### ChatGPT = Netscape？

很多人说 ChatGPT 是 AI 时代的 Netscape —— 开路先锋但最后被平台巨头的分发能力碾压。Google 有搜索分发、Meta 有社交分发、Apple 有设备分发。

### 平台梦想 vs 现实

Sam Altman 的策略：砸资本 → 建基础设施 → 构建全栈平台 → 形成生态系统 → 网络效应锁定。

但 Benedict 一针见血：

> "PSA: a 1:1 relationship between capex and revenue is not a flywheel."

TSMC 有垄断但没往上层的 leverage。没有人说"我 build TSMC apps"。同样，最终用户不关心你用的是 AWS 还是 GCP。

### 分布才是终极护城河

> "When you have an undifferentiated product, competition shifts to brand and distribution."

结论：OpenAI 需要在模型之外找到真正的护城河——可能是 agent 协议（MCP、agent-to-agent）、可能是用户场景深度、也可能是最直观的终端产品体验。

---

## 四、GenAI 的采纳之谜（2025.5.25）

### 核心矛盾

ChatGPT 的公开采用数据：
- 全球约 30% 的人尝试过（远快于 PC/Web/智能手机的早期采用）
- 但 DAU/WAU 比例极差——大部分用户每周用 1 次或更少

### 两种解释

| 解释 | 乐观方 | 悲观方 |
|------|--------|--------|
| **时间问题** | 模型会更好，用户会养成习惯，S-curve 会向上 | 3 年了还没改变日常习惯，可能不是时间问题 |
| **产品问题** | AI 需要像 iPhone 那样的"结晶时刻" | Chatbot 本身可能就是错误的产品形态 |

### 核心洞察

> "Most people will experience this technology as features wrapped inside other things."

就像 3G 的 killer app 不是"视频通话"而是"把互联网放口袋里"——AI 的 killer app 可能不是 chatbot，而是**嵌入到现有产品中的 AI 功能**。

提醒：如果你每天用 5 个不同的 LLM、今年没用过 Google 搜索、你的朋友也是这样的……那你处于一个巨大的 bubble 里。

---

## 五、综合提炼：Benedict Evans 的 AI 世界观

### 他反复回到的几个母题

1. **历史类比法** — 不依赖模型预测，而是用前几轮技术变革的格局来理解当前
2. **"it depends" 不是软弱** — 在技术早期，任何具体的预测都可能是运气
3. **敬畏复杂性** — 工作和商业的形态无法被简单量化（反对 O*NET 式的自动化敞口分析）
4. **分发 > 技术** — 当技术商品化后，赢家由分发渠道决定
5. **AI 不是魔法** — 它是一项跟互联网和移动同级别的平台转变，不会消灭工作，但会改变商业模式

### 对工程师/创业者的启示

- **别焦虑工作被取代** — 问自己"这是一个任务还是一个 job？"任务可以被自动化，job 是复杂的任务网格
- **AI 降低了软件的准入成本** — 但也让"你"变得更重要——你的判断、品味、domain knowledge 不会贬值
- **看 Jevons 悖论** — AI 让分析变便宜 → 你该做更多/更深的分析，而不是更少

---

*整理时间：2026-06-04 | 源于 Lenny's Podcast + Benedict Evans 博客*
