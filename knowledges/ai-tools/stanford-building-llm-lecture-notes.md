# How to Build LLMs —— 从预训练到后训练的完整指南

> **来源**：Stanford Lecture "How AI Works"（Building LLMs）
> **时长**：约 104 分钟
> **整理**：Jarvis II（转写 + 翻译 + 网络资料补充）
> **目标读者**：有高中知识即可看懂，专业术语保留英文

---

# 引言

你有没有想过，ChatGPT 是怎么做出来的？

当你向它问一个问题，它为什么能像人一样回答你？它真的会"思考"吗？它到底是怎样从一堆服务器变成能和你聊天的"AI 助手"的？

今天我们就来一步步拆解：**building a Large Language Model (LLM)，到底需要做什么。**

## 先认识几个明星模型

你肯定听说过这些名字：
- **ChatGPT** — OpenAI，让全世界认识了什么是 AI 聊天
- **Claude** — Anthropic，以安全和诚实著称
- **Gemini** — Google
- **LLaMA** — Meta（Facebook），免费开源

这些模型虽然名字不同、公司不同，但底层技术原理是**一样的**。我们今天要学的，就是它们背后的共同配方。

## 训练 LLM 的五大 Components

想象你在造一辆赛车。你不能只盯着引擎，你还需要轮胎、刹车、方向盘和车身。Building an LLM 也一样，有五个同样重要的部分：

| Component | 是什么 | 谁主要在做 |
|-----------|--------|-----------|
| ① **Architecture** | 神经网络长什么样（几层？每层多宽？） | Academia（学术界） |
| ② **Training Loss / Algorithm** | 怎么调整 weights 让模型学会预测下一个 token | Academia（学术界） |
| ③ **Data** | 喂给模型什么样的文字 | **Industry（工业界）— 最重要** |
| ④ **Evaluation** | 怎么知道模型变好了还是变差了 | **Industry（工业界）— 很重要** |
| ⑤ **Systems** | 怎么让 16,000 块 GPU 一起高效干活 | **Industry（工业界）— 非常重要** |

> **讲者核心观点**：Academia 喜欢研究 architecture 和 training algorithm，因为设计新结构看起来很酷。但在 industry（比如 OpenAI、Google、Meta），**真正决定模型好坏的是 Data quality、Evaluation methodology 和 Systems efficiency**。一个小的 architecture change，可能还不如让模型多 train 10 小时来得有效。

## Training 的两步法

训练一个能做对话的 LLM，分两个大阶段：

### Stage 1: Pre-training（预训练）
- **目标**：让模型学会"人是怎么说话的"
- **方法**：把整个互联网的文字（数万亿 tokens）喂给模型，让它学会 predict next token
- **结果**：一个 language model——它知道语法、知道很多知识，但**不会和人类对话**

### Stage 2: Post-training（后训练）
- **目标**：让 language model 变成 "AI 助手"
- **方法**：用人类对话数据进一步 training，用 human preference 优化回答
- **结果**：你用的 ChatGPT

> GPT-3 是纯 pre-training 模型，ChatGPT 是 GPT-3 做了 post-training 之后的产品。**Post-training 是 ChatGPT 如此受欢迎的关键创新。**

---

# 第一部分：Pre-training（预训练）

Pre-training 是 building an LLM 的第一步，也是最费钱的一步。我们来一点一点拆解。

---

## 1.1 什么是 Language Model？

### 核心概念

Language Model，简单说，就是能**计算一句话出现在互联网上的概率**的 model。

比如给你三个句子：

| Sentence | Probability on the Internet |
|----------|---------------------------|
| "The mouse ate the cheese." | ✅ High |
| "The the mouse ate cheese."（语法错误） | ❌ Low |
| "The cheese ate the mouse."（奶酪吃了老鼠——荒谬） | ❌ Very low |

一个好的 language model 应该能区分这三个句子：第一个 likely，第二、三个 unlikely。

### Autoregressive Language Model——今天所有 LLM 都在用的方法

目前所有主流 LLM（ChatGPT、Claude、Gemini 等）都是一种叫做 autoregressive language model 的东西。思想很简单：

**把一个句子的 probability，分解成一个个 token 的 conditional probability 的乘积。**

$$P(x_1, x_2, ..., x_L) = P(x_1) \cdot P(x_2|x_1) \cdot P(x_3|x_1, x_2) \cdot ... \cdot P(x_L|x_1, ..., x_{L-1})$$

Chain rule of probability——高中概率课上应该学过。没有 approximation，只是 distribution 的一种建模方式。

### Training 的时候做什么？

1. 给 model 一段 text："the mouse ate"
2. 让 model predict next token："the"？"cheese"？
3. 看正确答案："cheese" ✅
4. 用 **Cross Entropy Loss** 比较 prediction 和 ground truth
5. Backpropagation → 更新 model weights，让 model 下次更倾向于 predict "cheese"

### Inference 的时候做什么？

1. 给 model："explain the theory of relativity"
2. Model predicts 第一个 token："the"
3. 把 "the" 加回 context，再 predict 下一个 token："theory"
4. 继续 auto-regressive loop，直到生成完整回答

> **缺点**：因为要逐个 token 地 generate，**长文本很慢**。这也解释了为什么 ChatGPT 打字是一字一字"蹦"出来的。

---

## 1.2 Tokenizer——模型怎么"读"文字

### 为什么需要 Tokenizer？

你可能会想：为什么不直接把每个 word 当作基本单位？

| Approach | Problem |
|----------|---------|
| **Word-level** | "猫"是一个词，"猫猫"（typo）又是另一个词？Spelling error 模型就不认识。像泰语这种没有空格的文字，没法按 word 分。 |
| **Character-level** | "the mouse ate the cheese" 会变成 19 个 character，sequence 太长。Transformer 处理长 sequence 的复杂度是 $O(L^2)$，吃不消。 |

**Solution**：取中间值——**Tokenizer**，把文字切分成 subword。一个 token 大约 3-4 个 character。

### BPE 算法——最常用的 Tokenization 方法

**Byte Pair Encoding (BPE)**，2016 年提出，至今是所有 GPT 系列 tokenizer 的基础。

算法很简单：

1. 从 character-level token 开始（约 256 个基础 token）
2. 在语料中统计最频繁的 token pair
3. 把这对 merge 成一个新 token
4. Repeat until 达到预设的 vocabulary size（通常 32K ~ 100K）

**实际例子**：
- "tokenization" → GPT tokenizer 分成 "token" + "ization"
- "playing" → "play" + "ing"
- "unhappiness" → "un" + "happiness"

最终 vocabulary 里有：
- 最常用的词：一个完整 word 作为一个 token
- 不常用的词：分成 2-3 个 subword token
- 生僻词 / spelling error：fallback 到 character level

### Tokenizer 的核心局限：数学不好

**关键问题**："327" 在 tokenizer 里是一个独立的 token，"328" 是另一个 token。

Model 看到 327 时，它看到的不是三个数字 3、2、7，而是一个 symbol 🏷️ "327"。

这就意味着：**模型不知道 327 + 1 = 328**。它没有数字的 compositional 概念！

> 这就是为什么大语言模型在做简单数学题时经常出错。GPT-4 花了很大功夫改进 code 的 tokenization——比如把 Python 的 4-space indentation 编码成独立 token，这样 model 写代码时生成速度和质量都有提升。

### 未来方向

很多研究者希望在 5-10 年内抛弃 tokenizer，直接用 character-level 或 byte-level。但这需要新的 architecture 解决 sequence 长度问题。在那之前，tokenizer 还会一直存在。

**关于 Vocabulary 的一个关键点**：vocabulary size 决定了 model output layer 的维度——所以**一旦训练开始，vocab size 就基本固定了**，很难增加新 token。

---

## 1.3 Data——模型"吃"什么长大

> "People often say we train on 'the internet'. But what exactly is the internet?"

你可能以为训练数据就是 Wikipedia 那种干净整洁的 article。错。**真实的互联网很脏。**

### Data 从哪里来？

最常用的来源是 **Common Crawl**——一个非营利组织的每月互联网快照。

- Pages：约 **250 billion (2500 亿) 个网页**
- Data volume：约 **1 Petabyte（1 PB = 100 万 GB）**
- 里面什么都有：blog、forum、spam、code、porn、machine-generated nonsense

### 从 Raw Data 到 Clean Data 的 Pipeline

讲者团队约 70 人中，约 15 人专门做 data 工作。

```
Common Crawl (250B pages ≈ 1PB text)
    ↓
① Text Extraction
   - 从 HTML 中提取正文
   - 数学公式（LaTeX）提取很难
   - 去掉重复的 header/footer/navigation
    ↓
② NSFW / Toxic Content Filtering
   - Porn、暴力、hate speech
   - PII（个人身份信息）
   - 每个公司都有一份很长的 blacklist（不公开）
    ↓
③ Deduplication（去重）
   - 同一 URL 多次出现 → 只留一次
   - 相同 paragraph 多次出现 → 只留一次
   - 比如《三体》的盗版在网上出现了一万次 → 只留一份
    ↓
④ Heuristic Filtering（规则过滤）
   - Token distribution 异常（非目标语言占比过高）
   - 词长异常（全是超短或超长词）
   - Page 太短 <500 char 或太长 >500K char → drop
    ↓
⑤ Model-based Filtering
   - Train 一个 binary classifier：
     - Positive：Wikipedia 引用的来源网站
     - Negative：随机网页
   - 给所有网页打分，只保留 high-quality pages
    ↓
⑥ Domain Classification & Weighting
   - 把数据分为 code、论文、books、news、entertainment、social media
   - 人为调整 sampling ratio：
     - Code ↑ → 推理能力提升
     - Books ↑ → 语言质量和 long-form 理解提升
     - Entertainment / social media ↓ → 减少废话
    ↓
⑦ High-Quality Annealing（高质收尾）
   - Training 结束时降低 learning rate
   - 只在 Wikipedia、精选图书等高质数据上继续 train 一段
   - 相当于考前"刷重点"——在极高质量数据上做 controlled overfitting
```

### Data Scale 的演化

| 时期 | Model | Training Data | 增长倍数 |
|------|-------|--------------|---------|
| 2018-2020 | 早期学术模型 | ~150B tokens (≈800GB) | baseline |
| 2020 | GPT-3 | ~300B tokens | ×2 |
| 2023 | LLaMA | 1.4T tokens | ×9 |
| 2023 | LLaMA 2 | 2T tokens | |
| 2024 | LLaMA 3 | **15.6T tokens** | **×100** |

**1 token ≈ 0.75 个英文 word**，15.6T tokens ≈ 12 万亿英文单词。

> 数据是 AI 公司的核心 competitive advantage，所以很少有公司公开 data processing 细节。

---

## 1.4 Evaluation——怎么知道模型在变好？

### Method 1: Perplexity（困惑度）

这是 pre-training 阶段**最常用的 evaluation metric**。

$$\text{perplexity} = 2^{\text{average cross entropy loss}}$$

**怎么理解**：
- 范围：**1 ~ vocabulary size**（比如 1 ~ 32,000）
- 1 分：model perfect——永远知道下一个 token 是什么
- 32,000 分：model 完全 random guessing
- GPT-3 级别：约 **10**——model 在 10 个候选 token 间犹豫
- 2017 年 model：约 **70**

**局限**：不同 model 用不同的 tokenizer，perplexity 不能 cross-model comparison。尺度不同。

### Method 2: Academic Benchmarks

因为 perplexity 不能跨模型比较，学术界设计了各种 standardized benchmark。

**MMLU（Massive Multitask Language Understanding）** 是最常用的：
- 覆盖 57 个学科：college medicine、astronomy、law……
- 四选一 multiple choice
- Evaluation method：看 model 选 A/B/C/D 哪个 token 的 probability 最高
- **但评测方法有歧义**——不同实现可能给出不同结果

**两个综合 benchmark suite**：
- **HELM**：Stanford 出品
- **Open LLM Leaderboard**：Hugging Face 出品

### Evaluation 的两大坑

**坑 1：Evaluation methodology 不统一**

同一个 model，用了不同的 evaluation method，结果可以差很多。

> LLaMA 65B 在 HELM 上 accuracy **63.7%**，但在另一个 benchmark 上只有 **48.8%**——差了 15 个点！

**坑 2：Data Contamination（数据污染）**

如果 training data 里包含了 test set，那 model 等于"考试前看过了答案"。

**Detection method**：如果将 test set 的 token 顺序随机 shuffle 后，model 的 perplexity 显著上升 → 很可能 data leakage。

---

## 1.5 Scaling Laws——为什么"大"就是好？

### Core Discovery

从 2017 年起，研究者发现了一个非常稳定的规律：**Model performance 和 scale 之间存在 power-law relationship。**

$$\text{Loss} \propto \text{Compute}^{-\alpha}$$

在 log-log scale 上，这条线是直的——说明规律非常稳定。

**Key Conclusions**：
- ✅ 增加 compute → predictable loss 下降
- ✅ 增大 model（更多 parameters）→ loss 下降
- ✅ 增加 training tokens → loss 下降
- 📍 **至今未见 plateau**——意味着模型还可以继续变大

### Practical Use：实验设计新范式

**Scenario**：假如给你 10,000 块 H100 GPU，训练一个月，你怎么选 model architecture？

**❌ Old pipeline（academia 常见）**：
- 30 天 → train 30 个不同配置的大 model 各 1 天 → 挑最好的
- **Problem**：最终 model 只训了 1 天！

**✅ New pipeline（industry 做法）**：
1. 先找到 scaling recipe（比如：增大模型时，learning rate 要怎么调整）
2. 前 3 天：train 不同 size 的小 model（每个训几小时），调 hyperparameters
3. Fit scaling law → predict 最优配置
4. 后 27 天：按 predict 训最终大 model
5. **最终 model 训了 27 天，而非 1 天**

**具体例子：Transformer vs LSTM 选择**
- Train transformers 和 LSTMs 在不同 scale 下的多个 model
- Fit scaling law curves（x=params, y=test loss）
- 外推到更大 scale → 清晰看出 Transformer 胜出

**两个关键参数**：
- **Slope（scaling rate）**：决定了随着 scale 扩大 loss 下降的速度
- **Intercept**：决定了小 scale 下的初始表现
- 某些 architecture 在小 scale 下较差，但 slope 更高 → 大 scale 下反超

> **讲者观察**：绝大多数 architecture 改进，最终只是改变了 intercept（初始化优势）。随着 compute 增长，这些优势很快被抹平。真正改变 slope 的是 **data quality**。

### Chinchilla Law（DeepMind, 2022）

**Question**：给定 fixed compute budget，应该用更多 parameters 还是更多 data？

**Method**：
1. 画 **isoFLOP curves**（等 FLOPs 曲线）
2. 每条 curve 上的不同点代表不同的 params/tokens 组合，但 total compute 相同
3. 找到每条 curve 上的 optimal point
4. Fit scaling law："最优参数量 vs 总 FLOPs"
5. 结论：**每 1 个 parameter 需要 20 个 training token**

**Ratio 是 1 : 20**
- 如果 model 有 100B parameters，需要 2T tokens 的数据
- 这是 **training-optimal** 比例

**⚠️ 但考虑 inference cost 时**：
- 上线后每次回答都要花钱，你倾向于用更小的 model
- **Inference-optimal ratio** 约 **1 : 150**
- LLaMA 3 405B 的 ratio 是 1 : 40（介于两者之间，偏向 training optimality）

### Bitter Lesson（苦味教训）

> **Richard Sutton (2019)**：过去 70 年 AI 研究的教训——唯一确定在增长的就是 compute。所以我们应该做的是设计**能 leverage computation 的 architecture**，而不是花时间研究那些看似聪明但 scale 不上的小技巧。

**对 LLM 的启示**：
- 别花太多时间在 activation function 或 attention variant 上
- 真正重要的是：**Systems optimization + Data quality + Scale**
- OpenAI 的成功不是因为 architecture innovation，而是**把简单的事情做到了极致**（大规模、高质量 data、工程优化）

---

## 1.6 到底要花多少钱？——以 LLaMA 3 405B 为例

### FLOPs Formula

一个简单的 back-of-envelope 估算：

$$\text{FLOPs} \approx 6 \times \text{#parameters} \times \text{#tokens}$$

- FLOPs = floating point operations（算力的基本单位）
- ×6 是因为：forward pass（3 ops）+ backward pass（3 ops）

**代入 LLaMA 3 405B**：
$$6 \times 405B \times 15.6T = 3.8 \times 10^{25} \text{ FLOPs}$$

> 🏛️ **Biden 行政令**（Executive Order）：如果 FLOPs > 1 × 10²⁶，model 将受到政府特殊 scrutiny（审查）。LLaMA 3 405B 的 3.8×10²⁵ 刚好低一个数量级，避开了这条线。

### Benchmarking on reference benchmarks

| Item | Detail | Note |
|------|--------|------|
| Parameters | **405B** | |
| Training data | **15.6T tokens** | |
| Total FLOPs | $3.8 \times 10^{25}$ | |
| GPU model | **NVIDIA H100** | 当时最好的 AI 训练卡，约 $30K/块 |
| GPU count | **16,000** | |
| Training time | **~70 days** | Actual reported: ~30M GPU hours |
| GPU hours | ~30 million | 16,000 × 24 × 70 |
| GPU rent cost | **~$52M** | $2/H100-hour (market rate) |
| Staff cost | **~$25M** | 50-person team × $500K/yr (Silicon Valley rate) |
| **Total cost** | **~$75M** | ≈ 5.4 亿 RMB |
| Carbon emission | ~**4,400 tons CO₂** | ≈ 2,000 次 JFK↔LHR round trips |

> **讲者点评**：目前碳排放还不是 global 大问题。但到 GPT-6/GPT-7（scale 再扩大 100×）时，就会成为真正的环境问题。每次新 model generation，FLOPs 约增加 10×。

---

# 第二部分：Post-training（后训练）

Pre-training 结束后，你有了一个 language model。它能续写文字，但**不会和人对话**。

举个例子：

> **Ask GPT-3**："explain the moon landing to a six year old"
> **GPT-3 completion**："explain the theory of gravity to a six year old"
>
> 为什么？因为在 internet data 中，这种问题是 list 形式的：
> - explain the moon landing to a six year old
> - explain photosynthesis to a six year old
> - explain gravity to a six year old
>
> Model 以为你在"续写 list"——它只是在做 next token prediction！

Post-training 的目标就是：**让 language model 变成 AI assistant**。

---

## 2.1 SFT（Supervised Fine-Tuning）——教模型"好好说话"

### 做法

做法很简单：收集一批高质量的 instruction → ideal response pairs，然后用**和 pre-training 完全一样的 loss function（cross entropy loss）**，继续 train。

**关键区别**：
- Pre-training 后期 learning rate 已 decay 到接近 0
- SFT 时使用**更高的 learning rate**（约 $1 \times 10^{-5}$ 级别）

> **本质就是 language model fine-tuning**，只不过用了不同的 data。

### Data 从哪里来？

**Method 1：Human-written（人工收集）**
- 贵！要让人类写完整的高质量答案
- 示例：OpenAssistant dataset

**Method 2：LLM-generated Synthetic Data（Alpaca——milestone innovation）**
- 2023 年，Stanford Alpaca 团队只写了 **175 条 seed data**
- 让 GPT-3.5 **自动生成了 52,000 条 QA pairs**
- 用这 52K 条 fine-tune LLaMA 7B → 效果惊人！
- 从此开创了"**用 LLM train LLM**"的 self-distillation 时代

**Method 3：Human-in-the-loop（未来方向）**
- 让 LLM 先生成回答
- Human 只做少量 edit（比从头写快得多）
- 关键：active learning——只在 model 最不确定的地方让 human 介入
- 信息论角度：edit 仍然在注入新信息（seed distribution ≠ training distribution）

### LIMA 论文的关键发现

**2,000 条 SFT data → 32,000 条 → 性能几乎无提升。**

**Why?**：
- Pre-train model 已经见过所有类型的人类说话方式（list 党、QA 党、blog 党……）
- SFT 的本质是告诉 model："你现在要 optimize 这一种 user style"
- **SFT 不教新知识**——知识在 pre-training 时已经在了
- "All you learn is formatting."

**对 synthetic data 的启示**：
> "如果你一直从同样的 distribution 生成数据，最终你不会学到新的 distribution。你只是在 self-play。"

所以纯用 LLM-generated text 做多代 training，很可能不会持续提升。关键还是人机协作。

### SFT 的三大 Issue

**Issue 1：Bounded by human ability**
> 我能判断一本书好不好看，但我写不出那本书。
> 同样，人类 judge answer quality 的能力 ≥ 写出 best answer 的能力。
> SFT 让 model 模仿"人类能写出来的答案"——而不是"人类能想象出来的最好答案"。

**Issue 2：May exacerbate Hallucination**

假设 SFT data 里，human 给了这样一个回答：
> Q: "What is the reference for the book xxx?"
> A: "A seminal work in the field, see [Paper A, 2019]."

回答本身没问题——但它提到的 paper 可能在 pre-training 时**从未出现过**。Model 会学到："哦，当我不确定时，编造一个看起来合理的 reference 是可以的。"

**这是 hallucination 的一个重要来源！**

**Issue 3：Expensive**
- 让人写出完整的、最优的 answer
- 比让人做个 binary preference label 贵得多
- 这就引出了下一个方法：RLHF

---

## 2.2 RLHF——用 Human Preference 优化 Model

> **RLHF = Reinforcement Learning from Human Feedback**

### Core Idea

不 clone human behavior（SFT 的做法），而是**maximize human preference**。

1. 对每个 instruction，让 model generate **两个 responses**
2. Human labeler 选**哪个更好**（preferred vs dispreferred）
3. 用算法让 model 多 generate preferred、少 generate dispreferred

### 2.2.1 Step 1：Train a Reward Model

为什么不能直接用 binary reward（好/坏）？

因为信息太少——Response A 比 B 好一点点 VS 好非常多，都是"好"。

**Solution**：Train a **Reward Model** $R(x, y)$，输出 continuous value。

**Bradley-Terry Model**：

$$P(y_1 \succ y_2 | x) = \frac{\exp(R(x, y_1))}{\exp(R(x, y_1)) + \exp(R(x, y_2))}$$

简单理解：把"回答 A 比 B 好多少"转化成 0%~100% 的 softmax probability。然后用 cross entropy loss 训练。

Reward model 本身也是一个 large transformer classifier。

### 2.2.2 Step 2：Optimize with PPO

> **PPO = Proximal Policy Optimization**

1. 把 LLM 看作 RL 中的 policy $\pi$
2. Rollout — 从当前 policy sample responses
3. Reward model 给 responses 打分
4. PPO update — 更新 LLM weights
5. 加 **KL regularization** 防止 reward hacking（因为 reward model 本身不完美）

**PPO 的痛点**：
> "RL theory 很漂亮，但 anyone who has used it knows how messy it is."

- Rollout（sampling responses）
- Clipping（防止 policy update 过大）
- Out-of-distribution issues
- 实现极其复杂，hyperparameters 极多，文档不全

### ⚠️ PPO 后的一个重要 Change

PPO-optimized model **不再是 maximum likelihood** 训练的。它的目标是 generate **best response**，而不是 cover all possible responses。

**Consequences**：
- Model 输出的 likelihood **不再有 probabilistic meaning**
- Model 倾向于给出单一最佳 response（entropy 极小化）
- **Perplexity 完全不可靠**

> "Think about the optimal policy after PPO: it essentially gives you a delta distribution — only one sentence that can be generated for that question."

---

## 2.3 DPO——PPO 的简化版

> **DPO = Direct Preference Optimization** (Stanford, 2023)

### Core Idea

不用 RL，直接做两件事：

1. **Preferred response** → increase its probability
2. **Dispreferred response** → decrease its probability

$$\mathcal{L}_{\text{DPO}} = -\log \sigma(\beta \cdot (\log P(y_w|x) - \log P(y_l|x)))$$

**不需要 reward model！不需要 rollout！不需要 clipping！**

### DPO vs PPO

| Dimension | PPO | DPO |
|-----------|-----|-----|
| Complexity | High (RL, rollout, clipping) | Low (just MLE) |
| Extra model needed | Reward model | None |
| Can use unlabeled data | ✅ Yes (reward model scores it) | ❌ Only labeled preference data |
| Performance | ✅ Good | ✅ At least as good |

> **Experimental result**（in summarization task）：
> Pre-trained → SFT → **PPO ≈ DPO** → 某些 benchmark 上甚至超过 human reference

> **Why OpenAI used PPO instead of DPO?**
> "The ChatGPT team had a lot of RL experts — including the original author of PPO. For them, RL was the intuitive approach."

**PPO 的独特优势**：
- 如果你有 100 万条 unlabeled data + 1 万条 labeled data
- PPO 可以先 train reward model → 用它给 100 万条 unlabeled data 打分
- DPO 只能用已标注的 1 万条

---

## 2.4 Human Feedback Data 的现实困难

### 标注一个"好回答"有多难？

想象你在 label 两个 ChatGPT responses，哪个更好：

> **Prompt**: "Tell me about self-driving cars"
>
> Response A: "Self-driving cars are vehicles capable of detecting their surroundings..."
>
> Response B: "Self-driving cars are cars equipped with sensors to navigate without driver..."
>
> "Both seem OK. Which one is better? It's actually hard to say at a glance."

### 五大 Challenges

**1. Slow & Expensive**
- Mechanical Turk：1,000 labels ≈ $300
- 每条都需要仔细阅读两个 responses 并做出 judgment

**2. Human Bias——Prefer Longer Responses**
- Labelers 下意识地选**更长的 response**（即使内容更差）
- **Length bias**
- 结果：ChatGPT 的回答越来越长——**这就是 RLHF 的副作用**

**3. Low Annotator Agreement**
- 两个人 label 同一对 response，agreement 仅约 **66%**
- 论文五个作者花了 3 小时讨论 labeling guidelines 后，self-consistency 也才 **67-68%**
- "这不是人类水平差——是这个 task 本身就难。"

**4. Annotator Distribution Shift**
- 不同文化、不同教育水平的人 preference 不同
- 你让哪些人来 label？他们代表了谁的观点？

**5. Labeling Ethics**
- Labelers 工资低
- 还要大量接触 toxic/harmful content（为了教会 model 避免这些）

### Solution：LLM-as-Judge

用另一个 LLM（如 GPT-4）替代人类做 preference judgment。

**Cost**：比人类便宜约 **50×**
**Agreement with human mode**：比人类之间的一致性更高

原因：Human 有 high variance（随机性大），LLM 几乎无 variance（虽可能有 bias，但 extremely stable）。

> 开源社区和 industry 已广泛采用 LLM + human hybrid labeling。

---

## 2.5 Post-training Evaluation——比想象中更难

### Traditional Methods All Fail

| Method | 为什么不能用 |
|--------|-------------|
| ❌ Validation loss | PPO 和 DPO model 之间不可比——训练目标不同 |
| ❌ Perplexity | Model 不再是 MLE-trained，likelihood 无意义 |
| ❌ Traditional ML benchmarks | Responses 高度 open-ended，无法 automated judgment |

### Chatbot Arena——目前最可信的 Method

**做法**：
1. 在网站上匿名并排放两个 chatbot
2. Random users 随意提问，blind judge 哪个更好
3. 收集**数十万用户**的 blind voting
4. 生成 Elo ranking（和 chess match 一样的计分方式）

**Pros**：接近 real-world usage
**Cons**：
- User base 偏向 tech-savvy（提问内容多与 tech 相关）
- 慢且贵——不适合 dev process 中的快速迭代

### LM-as-Judge for Evaluation

用 GPT-4 替代 human 做 evaluation：

1. 对 N 个 test instructions，model A 和 model B 各 generate response
2. 让 GPT-4 judge 哪个更好
3. Calculate win rate

**Result**：
- 与 Chatbot Arena 的 Pearson correlation 高达 **98%**
- 3 分钟内完成，cost < $10
- 几乎免费替代了数万人的投票

**⚠️ Length Bias 问题**：

Experiment：
- GPT-4 with "be concise" prompt → win rate **20%**
- GPT-4 with "be verbose" prompt → win rate **64.4%**
- 同一个 model，只是改了说话长短！

**Solution**：用 causal inference / regression analysis 把"response length"这个 confounder 控制掉。

---

# 第三部分：Systems（系统优化）

> **（由于时间限制，讲者只讲了约 8 分钟）**

## 3.1 为什么 Systems Optimization 如此重要？

> "Why not just buy more GPUs? — They're expensive, but also even if you have $10M right now, you can't buy the best GPUs."

GPU 多了以后，还有一个 physical limitation：**GPU 之间需要 communication**。GPU 越多，communication 时间越长。

**Current bottleneck**：Compute 性能提升速度 > Memory + Communication 性能提升速度。大部分 GPU 在跑 unoptimized code 时，大部分时间处于 idle。

## 3.2 GPU vs CPU

| Dimension | CPU | GPU |
|-----------|-----|-----|
| Optimized for | Latency（低延迟） | Throughput（高吞吐） |
| Core architecture | Few cores, complex each | Thousands of small cores (SMs / streaming multiprocessors) |
| Golden operation | 各种指令 | **Matrix multiplication**（比其它 ops 快 10× 以上） |

## 3.3 两个关键 Optimization Techniques

### Technique 1：Mixed Precision Training

**Intuition**：用更少的 bits 表示 float → 更快 transmission → 更低 memory consumption → 更快处理

Standard practice：
- **Weight storage**：FP32（32-bit float）
- **Matrix computation**：转为 FP16 / BF16（16-bit）
- **Weight update**：转回 FP32
- 原因：如果 learning rate 很小（如 $1 \times 10^{-7}$），FP16 无法表示这么小的 delta

这叫 **Automatic Mixed Precision (AMP)**。

### Technique 2：Operator Fusion

**Problem**：PyTorch 每行 code 都会将 data 从 GPU global memory（DRAM）搬到 compute unit，算完再搬回去。

```python
x = torch.cos(x)  # move data → compute cos → move back
x = torch.sin(x)  # move data → compute sin → move back
```

每次 data movement 都开销巨大！

**Solution**：Fused Kernel

```python
# Move data once → compute all → move back once
x = fused_cos_sin(x)
```

**In practice**：`torch.compile(model)` → 自动将 PyTorch code 编译为 optimized CUDA C++ kernel → **约 2× speedup**。

### MFU（Model FLOP Utilization）

衡量 GPU 被利用了多少的 metric：

$$MFU = \frac{\text{Observed throughput}}{\text{Theoretical peak FLOPs}}$$

- **50%** 已经不错了
- Meta 训练 LLaMA 时 MFU 约 **45%**
- 意味着 GPU 有一半时间在空等——还有很大 optimization 空间

---

# 第四部分：现场 Q&A 精选

### Q：Post-training fine-tuning 是改全部 parameters，还是只改一部分？

> **A**：Industry 做法——**fine-tune all parameters**。Open-source community 常用 **LoRA**（只加少量 low-rank 差值来近似 full fine-tuning），但公司在 production 环境全量微调。

### Q：为什么 2,000 条 SFT data 就能撼动 15T tokens 的 pre-training？

> **A**：关键要换一个思路——**把 pre-training 看作 model 的 initialization**。Pre-training 给了 model 一个 good starting point（好的 weight initialization），post-training 才真正定义了 model 的 behavior。
>
> "If I use a large enough learning rate, training on just one sentence repeatedly, eventually the model will only generate that sentence. So the number of tokens doesn't matter — it's how you train."

### Q：PPO 微调时实际会跑几个 epoch？

> **A**：在实验中，大约做了 **3 个 epoch**。但 repetition number 不重要——**effective learning rate** 才是关键。

### Q：Post-training data 的规模有多大？

> **A**：对比一下就知道多夸张了：
> - SFT data：约 **5,000 ~ 50,000 条**
> - RLHF data：约 **1M（100 万）条**
> - Pre-training data：**15T tokens**
>
> 15T ÷ 1M = **15 million 倍**。但 post-training 用不同的 learning rate 和 training strategy，对 model behavior 的影响巨大。

### Q：为什么会有人选择 PPO 而不是更简单的 DPO？

> **A**：PPO 有一个独特 advantage——可以用 reward model 给**unlabeled data** 打分。如果你有 1M unlabeled + 10K labeled，PPO 可以先 train reward model → 用它给 1M 条 unlabeled data 打分。DPO 只能用已标注的 10K 条。
>
> 但 DPO 胜在 simplicity。现在 open-source community 基本都在用 DPO。

---

# 第五部分：还有哪些没讲到？

这场 lecture 只是一个 overview。还有很多重要 topic 没有展开：

1. **Inference optimization**：Model training 好后，怎么让它快速、廉价地 serve 上亿用户？
2. **Multimodality**：怎么做 visual understanding + language generation？
3. **Data scarcity**：互联网上的 high-quality text 可能有上限，未来怎么办？
4. **AI Safety**：怎么防止 model 被滥用？
5. **Synthetic data**：能否让 AI 自己产生 training data 来不断提升（self-play / self-improvement）？
6. **Mixture of Experts (MoE)**：怎么用 multiple sub-networks 提高 capacity 而不增加 compute？

## 想继续深入学习？推荐这三门课

| Course | Content | Workload |
|--------|---------|----------|
| **CS 224N** (Stanford) | NLP foundations，LLM 内容较少 | ⭐⭐ |
| **CS 324** (Stanford) | **Large Language Models**，更深度的 lectures 和 readings | ⭐⭐⭐ |
| **CS 336** (Stanford) | **Building LLMs from Scratch**，超级实战（讲者是两位 instructor 的学生） | 🔥🔥🔥🔥🔥 |

> **讲者警告**：CS 336 的 workload 极其大，请做好准备。

---

# 附录：Key Papers Quick Reference

| Paper | Year | Institution | One-sentence summary |
|-------|------|-------------|----------------------|
| **Scaling Laws** | 2020 | OpenAI | Model performance 与 compute/data/params 呈 power-law relationship，未见 plateau |
| **Chinchilla** | 2022 | DeepMind | Optimal compute allocation：20 tokens per parameter；isoFLOP curves methodology |
| **LLaMA** | 2023 | Meta | Open-source strong foundation model series，推动开源社区爆发 |
| **Alpaca** | 2023 | Stanford | 用 LLM 生成 synthetic SFT data（175 seeds → 52K） |
| **LIMA** | 2023 | Meta | 2K SFT data suffices；pre-training 已有知识，SFT is just formatting |
| **PPO** | 2017 | OpenAI (Schulman et al.) | ChatGPT 的原始 RLHF algorithm |
| **DPO** | 2023 | Stanford | PPO 的 simplification，same performance, much easier to implement |
| **Constitutional AI** | 2023 | Anthropic | 用 AI self-critique 代替 human feedback |
| **Bitter Lesson** | 2019 | Richard Sutton | Compute 才是唯一确定增长的，architecture 的小改进不重要 |

---

# 后记

这篇文章从一次 Stanford lecture 出发，补充了大量相关知识和技术背景。

**你到底学到了什么？**

1. **LLM 不是魔法**，它背后是一系列清晰的 engineering steps
2. Training 一个 LLM 需要做**五件事**：Architecture, Training Algorithm, Data, Evaluation, Systems
3. 分为**两大阶段**：Pre-training（学语言建模）和 Post-training（学对话对齐）
4. 最贵的 stage 是 **Pre-training**（百万到亿美元级别）
5. 最影响 performance 的是 **Data quality 和 Systems efficiency**
6. 最前沿的方向是 **RLHF / DPO** 和 **如何高效利用 human preference**
7. Industry 和 academia 的 focus 完全不同——**真正决定模型好坏的是 Data、Eval 和 Systems，而非 Architecture 的小改动**

---

*✏️ Source：Stanford Lecture ~104 min audio | Transcription：Volcengine STT (bigmodel API) | Compiled by：Jarvis II*
