# 第 28 章：速查参考（Quick Reference）
\label{quick-reference}

This chapter consolidates key equations, architecture specifications, API references, and failure mode diagnostics for rapid lookup during development and debugging.
本章整合了关键公式、架构规格、API 参考和故障诊断，便于在开发和调试过程中快速查阅。

---

## 核心 RL 和对齐公式（Core RL & Alignment Equations）
\label{core-rl-alignment-equations}

\begin{align}
\text{PPO Clip:}&\quad L = \mathbb{E}[\min(r_t\hat{A}_t, \text{clip}(r_t,1{\pm}\epsilon)\hat{A}_t)], \quad r_t = \pi_\theta(a_t|s_t)/\pi_{\text{old}}(a_t|s_t) \\
\text{DPO:}&\quad L = -\mathbb{E}[\log\sigma(\beta\log\tfrac{\pi_\theta(y_w|x)}{\pi_\text{ref}(y_w|x)} - \beta\log\tfrac{\pi_\theta(y_l|x)}{\pi_\text{ref}(y_l|x)})] \\
\text{GRPO:}&\quad \hat{A}_i = (r_i - \mu_G)/\sigma_G, \quad \text{then PPO clip update (no critic)} \\
\text{KTO:}&\quad L = \lambda_w(1 - v(y_w)) + \lambda_l \cdot v(y_l), \quad v = \sigma(\beta\log(\pi_\theta/\pi_\text{ref}) - z) \\
\text{IPO:}&\quad L = \mathbb{E}[(\log(\pi_\theta(y_w)/\pi_\text{ref}(y_w)) - \log(\pi_\theta(y_l)/\pi_\text{ref}(y_l)) - 1/(2\beta))^2] \\
\text{ORPO:}&\quad L = L_\text{SFT}(y_w) - \lambda\log\sigma(\log(\text{odds}(y_w)/\text{odds}(y_l))) \\
\text{GAE:}&\quad \hat{A}_t = \textstyle\sum_{l=0}^{T-t}(\gamma\lambda)^l\delta_{t+l}, \quad \delta_t = r_t + \gamma V(s_{t+1}) - V(s_t) \\
\text{KL Penalty:}&\quad R_\text{total} = r_\phi(x,y) - \beta D_\text{KL}[\pi_\theta(y|x)\|\pi_\text{ref}(y|x)] \\
\text{RM (Bradley-Terry):}&\quad L = -\mathbb{E}[\log\sigma(r_\phi(x,y_w)-r_\phi(x,y_l))] \\
\text{Best-of-N:}&\quad y^* = \arg\max_{y_i \sim \pi_\theta(\cdot|x),\, i=1..N} r_\phi(x, y_i)
\end{align}

**公式说明 / Formula Description:**
- **PPO Clip**: 裁剪替代损失，$r_t$ 为概率比，$\hat{A}_t$ 为优势估计，$\epsilon$ 为裁剪范围
- **DPO**: 直接偏好优化，$\beta$ 控制对齐强度，$\pi_\theta$ 为策略，$\pi_\text{ref}$ 为参考策略
- **GRPO**: 组相对策略优化，$\mu_G$ 和 $\sigma_G$ 为组的均值和标准差
- **KTO**: KTO 损失，基于二元反馈（赞/踩）
- **IPO**: 身份偏好优化，将 DPO 转化为回归问题
- **ORPO**: 赔率比偏好优化，结合 SFT 和偏好损失
- **GAE**: 广义优势估计，$\gamma$ 为折扣因子，$\lambda$ 为 GAE 参数
- **KL Penalty**: KL 正则化，防止策略偏离参考策略太远
- **RM (Bradley-Terry)**: 奖励模型训练，使用 Bradley-Terry 偏好模型
- **Best-of-N**: 从 N 个采样中选择最优一个

---

## Transformer 和架构公式（Transformer & Architecture Formulas）
\label{transformer-architecture-formulas}

\begin{align}
\text{Self-Attention:}&\quad \text{Attn}(Q,K,V) = \text{softmax}(QK^\top / \sqrt{d_k}) \cdot V \\
\text{Multi-Head:}&\quad \text{MHA}(X) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h)W^O,\quad \text{head}_i = \text{Attn}(XW_i^Q, XW_i^K, XW_i^V) \\
\text{RoPE:}&\quad f(x_m, m) = x_m e^{im\theta_j}, \quad \theta_j = 10000^{-2j/d} \\
\text{LoRA:}&\quad W' = W_0 + (\alpha/r) \cdot BA, \quad B \in \mathbb{R}^{d \times r},\; A \in \mathbb{R}^{r \times k} \\
\text{KD (soft targets):}&\quad L_\text{KD} = (1{-}\alpha)L_\text{CE}(y, \hat{y}) + \alpha\, T^2 \cdot \text{KL}(p_T^\text{teacher} \| p_T^\text{student}) \\
\text{FFN (SwiGLU):}&\quad \text{FFN}(x) = (\text{Swish}(xW_1) \odot xW_3) W_2
\end{align}

**公式说明 / Formula Description:**
- **Self-Attention**: 自注意力机制，$d_k$ 为键维度缩放因子
- **Multi-Head**: 多头注意力，$h$ 为头数，$W^O$ 为输出投影
- **RoPE**: 旋转位置编码，$m$ 为位置，$\theta_j$ 为旋转频率
- **LoRA**: 低秩适配，$r$ 为秩，$\alpha$ 为缩放因子
- **KD**: 知识蒸馏，$T$ 为温度，$\alpha$ 控制软/硬标签权重
- **FFN (SwiGLU)**: 带 SwiGLU 激活的前馈网络，$\odot$ 为逐元素相乘

---

## 解码方法（Decoding Methods）
\label{decoding-methods}

| **方法 (Method)** | **公式/规则 (Formula / Rule)** | **关键参数 (Key Param)** |
|---|---|---|
| Greedy (贪心) | $y_t = \arg\max_v P(v\|y_{<t})$ | --- |
| Beam search (束搜索) | 按联合概率保留前 $B$ 条部分序列 | $B=4$–$8$ |
| Temperature (温度) | $P'(v) = \text{softmax}(\text{logit}_v / T)$ | $T \in [0.1, 1.5]$ |
| Top-$k$ | 仅保留前 $k$ 个 logits，重新归一化 | $k=40$–$100$ |
| Top-$p$ (nucleus) | 保留最小集合 $V'$ 使 $\sum_{v \in V'} P(v) \geq p$ | $p=0.9$–$0.95$ |
| Min-$p$ | 保留 $P(v) \geq p_\text{min} \cdot P(v_\text{max})$ 的令牌 | $p_\text{min}=0.05$–$0.1$ |
| Repetition penalty (重复惩罚) | $\text{logit}_v \leftarrow \text{logit}_v / \theta$ 若 $v$ 之前出现过 | $\theta=1.1$–$1.3$ |

---

## 系统与并行（Systems & Parallelism）
\label{systems-parallelism}

| **公式 (Formula)** | **值（70B, BF16）** | **描述 (Description)** |
|---|---|---|
| Model memory (模型内存) | $2P$ bytes | $140$ GB（仅权重） |
| Adam optimizer (Adam 优化器) | $2P \times 4$ bytes (m + v) | $280$ GB |
| Full training footprint (完整训练占用) | $\sim 8P$ bytes | $560$ GB（权重 + 优化器 + 梯度） |
| FSDP memory/GPU (FSDP 每 GPU 内存) | $8P / N_\text{GPUs}$ | $70$ GB（8 GPU） |
| Gen arithmetic intensity (生成计算强度) | $2P / 2P = 1$ FLOP/byte | 严重内存受限 |
| Token rate (gen) (令牌生成率) | HBM\_BW $/ (2P)$ | $\sim$14 tok/s（A100, batch=1） |
| TP AllReduce / layer (TP 全规约/层) | $2 \times 2 \cdot \frac{T-1}{T} \cdot bsd$ bytes | $\sim$188 MB（70B, TP=8） |
| PP bubble fraction (PP 气泡占比) | $(P-1)/(P+M-1)$ | $P$=流水线级数，$M$=微批次 |
| MFU (模型流畅利用率) | observed\_toks $\times$ 6$P$ / peak\_FLOPS | 目标: $>40\%$ |

---

## GPU 硬件规格（GPU Hardware Specs）
\label{gpu-hardware-specs}

| **GPU** | **内存 (Memory)** | **带宽 (BW, HBM)** | **BF16 TFLOPS** | **NVLink** | **备注 (Notes)** |
|---|---|---|---|---|---|
| A100-80GB | 80 GB HBM2e | 2.0 TB/s | 312 | 600 GB/s | 主力型号，广泛可用 |
| H100-80GB | 80 GB HBM3 | 3.35 TB/s | 989 | 900 GB/s | 当前代，支持 FP8 |
| H200-141GB | 141 GB HBM3e | 4.8 TB/s | 989 | 900 GB/s | 大上下文/更少 GPU |
| B200 | 192 GB HBM3e | 8.0 TB/s | 2250 | 1800 GB/s | 下一代（2025） |

---

## 超参数范围（Hyperparameter Ranges）
\label{hyperparameter-ranges}

| **参数 (Parameter)** | **典型范围 (Typical Range)** | **默认 (Default)** | **备注 (Notes)** |
|---|---|---|---|
| $\beta$ (DPO/KTO) | 0.05–0.5 | 0.1 | 越高越保守 |
| $\epsilon$ (PPO clip) | 0.1–0.3 | 0.2 | 越高更新越激进 |
| $\gamma$ (GAE discount) | 0.99–1.0 | 1.0 | 周期性任务使用 1.0 |
| $\lambda$ (GAE) | 0.9–0.99 | 0.95 | 越低偏差越大、方差越小 |
| KL coeff ($\beta_\text{KL}$) | 0.01–0.2 | 0.05 | 自动适配目标 KL $\approx$ 5–8 |
| LR (RLHF) | 1e-7 – 5e-6 | 5e-7 | 远低于预训练 |
| LR (SFT) | 1e-5 – 5e-5 | 2e-5 | 标准微调范围 |
| LoRA rank $r$ | 8–128 | 16–64 | $r$ 越高容量越大、内存越多 |
| LoRA alpha $\alpha$ | $r$ – $2r$ | $2r$ | 缩放因子；$\alpha/r$ 为有效缩放 |
| Temperature (gen) | 0.6–1.0 | 0.7 | 越低候选多样性越小 |
| Num generations $K$ | 4–64 | 4–16 | 用于 GRPO/Online DPO/Best-of-N |
| Grad clip norm | 0.5–2.0 | 1.0 | 防止梯度爆炸 |

---

## TRL API 速查（TRL API Quick Reference）
\label{trl-api-quick-reference}

| **Trainer** | **方法 (Method)** | **关键配置 (Key Config)** | **数据格式 (Data Format)** |
|---|---|---|---|
| `SFTTrainer` | Supervised FT (有监督微调) | `packing, max_seq_length` | prompt + completion |
| `RewardTrainer` | Reward model (奖励模型) | `center_rewards_coefficient` | prompt + chosen + rejected |
| `PPOTrainer` | PPO | `init_kl_coef, target_kl, cliprange` | prompts（在线生成） |
| `DPOTrainer` | DPO/IPO | `beta, loss_type="sigmoid"/"ipo"` | prompt + chosen + rejected |
| `GRPOTrainer` | GRPO | `num_generations, beta, use_vllm` | prompts + reward_fn |
| `OnlineDPOTrainer` | Online DPO (在线DPO) | `num_generations, reward_model_path` | prompts（在线生成） |
| `KTOTrainer` | KTO | `desirable_weight, undesirable_weight` | prompt + completion + label |
| `ORPOTrainer` | ORPO | `beta` | prompt + chosen + rejected |
| Best-of-N (manual) | Best-of-N | `n_samples` | prompts（推理） |

---

## RAG 流水线公式（RAG Pipeline Formulas）
\label{rag-pipeline-formulas}

\begin{align}
\text{Cosine similarity:}&\quad \text{sim}(q, d) = \frac{q \cdot d}{\|q\| \cdot \|d\|} \\
\text{Retrieval:}&\quad \mathcal{D}_k = \text{top-}k_{d \in \mathcal{C}} \; \text{sim}(\text{embed}(q),\; \text{embed}(d)) \\
\text{RAG generation:}&\quad P(y|q) = P_\text{LLM}(y \;|\; q, \mathcal{D}_k) \\
\text{Chunking overlap:}&\quad \text{stride} = \text{chunk\_size} - \text{overlap} \\
\text{Reranker (cross-enc):}&\quad \text{score}(q, d) = \text{MLP}(\text{BERT}([q; d]))
\end{align}

**公式说明 / Formula Description:**
- **Cosine similarity**: 余弦相似度，衡量查询 $q$ 与文档 $d$ 的语义距离
- **Retrieval**: 从语料库 $\mathcal{C}$ 中检索前 $k$ 个最相似文档
- **RAG generation**: 在给定查询和检索文档的条件下生成回答
- **Chunking overlap**: 分块时的滑动步长
- **Reranker (cross-enc)**: 使用交叉编码器重新排序，获得更精准的相似度评分

---

## Agent 设计模式（Agentic Design Patterns）
\label{agentic-design-patterns}

| **模式 (Pattern)** | **结构 (Structure)** | **适合场景 (Best For)** |
|---|---|---|
| ReAct | 思考 $\to$ 行动 $\to$ 观察 $\to$ 循环 | 通用工具使用智能体 |
| Plan-and-Execute | 计划 $\to$ 执行步骤 $\to$ 修订 | 长期、结构化任务 |
| Supervisor | 路由器 $\to$ 专业智能体 | 多领域、明确子任务边界 |
| Swarm (handoffs) | 智能体转移控制权 + 上下文 | 客服、升级流转 |
| Hierarchical | 委派智能体的树形结构 | 复杂分解 |
| Human-in-the-loop | 智能体 $\to$ 审批门 $\to$ 继续 | 高风险、不可逆操作 |

---

## 智能体通信协议（Agent Communication Protocols）
\label{agent-communication-protocols}

| **协议 (Protocol)** | **范围 (Scope)** | **传输 (Transport)** | **核心概念 (Key Concept)** |
|---|---|---|---|
| MCP | 工具集成 | stdio / HTTP+SSE | 服务端暴露工具；客户端发现并调用 |
| A2A | 智能体间通信 | HTTP + JSON-RPC | 具有生命周期（已提交$\to$进行中$\to$完成）的任务 |
| OpenAI Function Calling | 工具使用 | API payload | `tools[]` 数组中的 JSON schema |

---

## 上下文窗口预算（Context Window Budget）
\label{context-window-budget}

\begin{equation}
C \geq \underbrace{S}_{\text{system}} + \underbrace{M}_{\text{memory/RAG}} + \underbrace{T}_{\text{tool defs}} + \underbrace{H}_{\text{history}} + \underbrace{R}_{\text{reserved output}}
\end{equation}

**经验法则（128K 上下文） / Rule of thumb**:

- System prompt (系统提示): 1–4K tokens (固定)
- Tool definitions (工具定义): 2–8K（随工具数量扩展）
- RAG context (RAG 上下文): 4–16K（top-$k$ 块）
- History (历史): 无界增长 $\to$ 摘要/截断
- Reserved output (保留输出): 2–8K

---

## 常见故障模式与修复（Common Failure Modes & Fixes）
\label{common-failure-modes-fixes}

| **症状 (Symptom)** | **可能原因 (Likely Cause)** | **修复 (Fix)** |
|---|---|---|
| 奖励上升，质量下降 | 奖励黑客 (Reward hacking) | RM 集成、长度惩罚、增加 $\beta$ |
| KL 爆炸（$>$15） | 学习率过高或模式崩溃 | 降低 LR、回滚检查点 |
| 熵崩溃 | 过早收敛 | 增加熵系数、提高温度 |
| 训练损失 NaN | 梯度爆炸 | 降低 LR、增加梯度裁剪、检查数据 |
| 5K 步后无改善 | 提示分布不佳 | 金发姑娘过滤（20–80% 通过率） |
| 基准回归 | 对齐税 | 减少 RL 预算、使用 LoRA、混合 SFT 数据 |
| 长度单调增长 | RM 中的长度利用 | 长度惩罚、用长度控制重新训练 RM |
| 生成过程中 OOM | KV 缓存溢出 | 减少 batch、增加 TP、PagedAttention |
| 智能体无限循环 | 缺少最大迭代保护 | 设置 `max_iterations`、添加循环检测 |
| 工具调用解析失败 | 输出格式不一致 | 少样本示例、受约束解码 |
| RAG 返回不相关文档 | 嵌入/分块不佳 | 重排序、混合搜索、更小的块 |
| 多智能体死锁 | 循环依赖 | DAG 强制、每智能体超时 |

---

## 方法选择决策树（Method Selection Decision Tree）
\label{method-selection-decision-tree}

1. **有配对偏好（chosen + rejected）？**
   - 标签有噪声 $\to$ **IPO**
   - 内存受限、未做 SFT $\to$ **ORPO**
   - 数据干净、计算有限 $\to$ **DPO**
   - DPO 达到瓶颈、需要探索 $\to$ **Online DPO**

2. **只有二元反馈（赞/踩）？** $\to$ **KTO**

3. **有可验证奖励（数学/代码）？** $\to$ **GRPO**

4. **需要最高质量，不计成本？** $\to$ **PPO**

5. **想要无需训练的改进？** $\to$ **Best-of-N**

---

## 评估指标（Evaluation Metrics）
\label{evaluation-metrics}

| **指标 (Metric)** | **范围 (Range)** | **衡量内容 (What It Measures)** |
|---|---|---|
| Perplexity (困惑度) | $[1, \infty)$ | 模型惊讶度；越低语言建模越好 |
| Win Rate (胜率 vs. 基线) | $[0, 1]$ | 裁判/人类偏好的输出比例 |
| BLEU | $[0, 1]$ | 与参考答案的 $n$-gram 重叠（精确率导向） |
| ROUGE-L | $[0, 1]$ | 与参考答案的最长公共子序列 |
| Pass@$k$ | $[0, 1]$ | $k$ 个代码样本中至少 1 个通过测试的概率 |
| MMLU / GPQA | $[0, 1]$ | 知识/推理基准的多选题准确率 |
| HumanEval | $[0, 1]$ | 生成代码的功能正确性 |
| Faithfulness (RAG) | $[0, 1]$ | 检索上下文支持的主张比例 |
| Context Relevancy | $[0, 1]$ | 检索内容与查询相关的比例 |
| Answer Relevancy | $[0, 1]$ | 答案回答问题的程度 |

---

## 推理与测试时计算缩放（Reasoning & Test-Time Scaling）
\label{reasoning-test-time-scaling}

| **方法 (Method)** | **计算成本 (Compute Cost)** | **机制 (Mechanism)** |
|---|---|---|
| Chain-of-Thought (CoT, 思维链) | 1.5–3$\times$ tokens | 提示中"逐步思考" |
| Self-Consistency (自一致性) | $N \times$ generation | 采样 $N$ 条 CoT 路径，对最终答案多数投票 |
| Tree-of-Thought (ToT, 思维树) | $B \times D \times$ generation | 对推理树进行 BFS/DFS；评估分支 |
| Best-of-$N$ | $N \times$ generation | 采样 $N$ 条，用 RM 评分，选最高 |
| Beam search (on reasoning) | $B \times$ generation | 维护前 $B$ 条部分推理链 |
| Budget forcing (预算强制) | 可变 | 对更难问题动态分配更多令牌 |
| Verification (ORM/PRM) | $N \times$ gen + scoring | 生成 $N$ 个解答，按结局/过程 RM 排序 |

---

## 记忆系统类型（Memory System Types）
\label{memory-system-types}

| **类型 (Type)** | **存储 (Storage)** | **使用场景 (Use Case)** |
|---|---|---|
| Working memory (工作记忆) | 上下文窗口 | 当前对话、即时工具结果 |
| Episodic memory (情景记忆) | 向量存储 | 过往交互、用户偏好、会话历史 |
| Semantic memory (语义记忆) | 知识图谱/嵌入 | 事实、概念、领域知识 |
| Procedural memory (程序记忆) | 技能库/代码 | 操作步骤、习得的工作流 |

---

## MCP 速查（MCP Quick Reference）
\label{mcp-quick-reference}

| **原语 (Primitive)** | **方向 (Direction)** | **副作用 (Side Effects)?** | **目的 (Purpose)** |
|---|---|---|---|
| Tools (工具) | 客户端 $\to$ 服务端 | 是 | 执行操作（创建、修改、删除） |
| Resources (资源) | 客户端 $\to$ 服务端 | 否（只读） | 读取数据（文件、数据库记录、配置） |
| Prompts (提示) | 客户端 $\to$ 服务端 | 否 | 常见任务的可复用模板 |
| Sampling (采样) | 服务端 $\to$ 客户端 | 否 | 服务端请求客户端进行 LLM 生成 |

**传输 / Transport**: `stdio`（本地子进程）或 `HTTP+SSE`（远程、可流式）。

**发现 / Discovery**: 客户端在连接初始化时调用 `tools/list`、`resources/list`、`prompts/list`。

**工具注解 / Tool annotations**: `readOnlyHint`、`destructiveHint`、`idempotentHint`、`openWorldHint`。

---

## A2A 协议速查（A2A Protocol Quick Reference）
\label{a2a-protocol-quick-reference}

| **概念 (Concept)** | **描述 (Description)** |
|---|---|
| Agent Card | `/.well-known/agent.json` 的 JSON——名称、技能、支持的内容类型 |
| Task (任务) | 工作单元：`id`、`status`、`artifacts`。生命周期：已提交 $\to$ 进行中 $\to$ 已完成/失败 |
| Message (消息) | 任务内的通信单元（角色：user/agent，部分：text/file/data） |
| Artifact (产物) | 智能体产生的输出（结构化数据、文件、生成内容） |
| Push Notifications (推送通知) | 基于 Webhook 的长时间任务更新（通过 `tasks/pushNotification/set`） |

**关键端点 / Key endpoints**: `tasks/send`（创建/更新）、`tasks/get`（轮询状态）、`tasks/sendSubscribe`（SSE 流）。

---

## 智能体框架比较（Agent Framework Comparison）
\label{agent-framework-comparison}

| **框架 (Framework)** | **编排 (Orchestration)** | **多智能体 (Multi-Agent)** | **适合场景 (Best For)** |
|---|---|---|---|
| LangGraph | 显式状态图 | 条件路由 | 生产：持久化、人在回路、精细控制 |
| OpenAI Agents SDK | 声明式移交 | 基于移交 | 简洁：护栏、追踪、快速启动 |
| AutoGen (AG2) | 对话驱动 | GroupChat | 原型设计：代码执行、研究 |
| CrewAI | 基于角色的团队 | 顺序/并行 | 低代码：快速演示、简单流水线 |
| Google ADK | 会话 + 事件 | A2A 原生 | 企业：产物管理、多模态 |

---

## Agentic RL 公式（Agentic RL Formulas）
\label{agentic-rl-formulas}

\begin{align}
\text{Trajectory GRPO:}&\quad \hat{A}_i = (R(\tau_i) - \mu_G)/\sigma_G, \quad R(\tau_i) = \sum_{t} r_t^{(\tau_i)} \\
\text{Agent reward:}&\quad R = w_1 R_\text{task} + w_2 R_\text{efficiency} + w_3 R_\text{safety}, \quad R_\text{eff} = \max(0, 1 - \text{steps}/N_\text{max}) \\
\text{Masking:}&\quad \mathcal{L} = \sum_{t \in \text{agent tokens}} \min(r_t \hat{A}_t,\; \text{clip}(r_t) \hat{A}_t) \quad \text{(mask env outputs)} \\
\text{Pass@}k:&\quad 1 - \frac{\binom{n-c}{k}}{\binom{n}{k}}, \quad n = \text{total samples},\; c = \text{correct}
\end{align}

**公式说明 / Formula Description:**
- **Trajectory GRPO**: 轨迹级 GRPO，$\tau_i$ 为第 $i$ 条轨迹，$R(\tau_i)$ 为轨迹总回报
- **Agent reward**: 组合奖励函数，$R_\text{task}$ 为任务完成奖励，$R_\text{efficiency}$ 为效率奖励，$R_\text{safety}$ 为安全奖励
- **Masking**: 掩码损失，仅在智能体令牌上计算梯度，屏蔽环境输出
- **Pass@$k$**: $n$ 个总样本中 $c$ 个正确，$k$ 次尝试至少一次通过的概率

---

## 智能体安全检查清单（Agent Security Checklist）
\label{agent-security-checklist}

| **威胁 (Threat)** | **层 (Layer)** | **缓解措施 (Mitigation)** |
|---|---|---|
| 提示注入（直接） | 输入 | 输入验证、指令层级、分隔符 |
| 提示注入（间接） | 工具输出 | 将工具输出视为不可信；不遵循检索文档中的指令 |
| 工具滥用 | 执行 | 最小权限原则；`destructiveHint` 门控；沙箱化 |
| 数据泄露 | 输出 | 输出过滤；限制工具访问允许域 |
| 过度自主性 | 架构 | 最大迭代次数；成本预算；人工审批门控 |
| 糊涂代理 | 多智能体 | 验证任务来源；基于能力的访问控制 |

---

## 智能体评估指标（Agent Evaluation Metrics）
\label{agent-evaluation-metrics}

| **指标 (Metric)** | **公式/定义 (Formula / Definition)** | **目标 (Target)** |
|---|---|---|
| Task Success Rate (TSR, 任务成功率) | 正确完成数 / 总任务数 | $>85\%$（生产） |
| Steps to completion (完成步数) | 每成功任务的平均智能体动作数 | 越低越高效 |
| Cost per task (每任务成本) | 总 token $\times$ 单价 | 取决于预算 |
| Latency (TTFC, 延迟) | 从请求到首个有用输出的时间 | $<5$s（交互式） |
| Tool call accuracy (工具调用准确率) | 正确工具选择 / 总调用数 | $>90\%$ |
| Recovery rate (恢复率) | 成功重试 / 初始失败数 | $>60\%$ |
| Human escalation rate (人工升级率) | 需人工干预的任务 / 总任务数 | $<15\%$ |

---

## 关键 Agentic 基准（Key Agentic Benchmarks）
\label{key-agentic-benchmarks}

| **基准 (Benchmark)** | **领域 (Domain)** | **指标 (Metric)** | **SOTA (2025)** |
|---|---|---|---|
| SWE-bench Verified | 软件工程 | % resolved issues | $\sim$70\% |
| WebArena | 网页浏览 | 任务成功率 | $\sim$40\% |
| OSWorld | 桌面计算机使用 | 任务成功率 | $\sim$25\% |
| GAIA | 通用 AI 助手 | 精确匹配准确率 | $\sim$75\% (L1) |
| Tau-bench | 工具使用可靠性 | 通过率（5 次尝试） | $\sim$65\% |
| HumanEval / MBPP | 代码生成 | Pass@1 | $>95\%$ |
