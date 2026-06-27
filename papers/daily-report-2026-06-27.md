# 📄 每日论文日报 — 2026-06-27

> 共 20 篇论文，按热度排序

---

## 🥇 Top 1 (Score: 25) — Do Thinking Tokens Help with Safety?

- **ID**: 2606.25013
- **类别**: cs.LG, cs.AI, cs.CL
- **链接**: [arXiv](https://arxiv.org/abs/2606.25013) | [GitHub](https://github.com/narutatsuri/lrm_safety_deliberation)
- **核心发现**:
  - 推理模型的安全行为远不如想象中"深思熟虑"
  - 第一个 token 的隐藏表征就能以 0.84-0.95 AUROC 预测最终的拒绝/顺从结果
  - 思考过程更像是前缀补全而非真正的修正性思考
  - 现存的推理阶段和训练安全干预手段反而抑制了本来就稀缺的 deliberation 信号

---

## 🥇 Top 2 (Score: 21) — When Does Combining Language Models Help?

- **ID**: 2606.27288
- **类别**: cs.AI, cs.LG
- **链接**: [arXiv](https://arxiv.org/abs/2606.27288)
- **核心发现**:
  - 多模型系统的准确率上限由"所有模型同时出错"的比率 β 决定
  - 在 67 个前沿模型上，数学题的 β=0.052，代码的 β=0.079
  - 平均配对误差相关系数 ρ 无法识别 β
  - 组合模型很少能超过单模型最佳效果，除非有强力的查询级路由信号

---

## 🥇 Top 3 (Score: 21) — Multi4D: High-Fidelity Dynamic Gaussian Splatting

- **ID**: 2606.22197
- **类别**: cs.CV
- **链接**: [arXiv](https://arxiv.org/abs/2606.22197) | [GitHub](https://github.com/BatFaceWayne/Multi4D) | [Project](https://batfacewayne.github.io/Multi4D.io/)
- **核心发现**:
  - 解决动态 3D Gaussian Splatting 中运动一致性与视觉保真度的基本矛盾
  - 三级竞争分配：静态结构、持久动态几何、瞬态外观
  - 在显著减少动态 primitives 的同时达到 SOTA 渲染质量
  - 支持 4D 语义分割，实现数量级加速

---

## 📋 其余论文速览

| 排名 | 论文 | 分数 | 类别 |
|------|------|:----:|------|
| 4 | **DanceOPD** — On-Policy 生成场蒸馏统一文生图与编辑能力 | 19 | cs.CV |
| 5 | **Why Multi-Step Tool-Use RL Collapses** — 监督信号如何稳定工具使用 RL 训练 | 17 | cs.CL |
| 6 | **Semantic Browsing** — 通过语义控制实现可控多样性的图像生成 | 17 | cs.CV |
| 7 | **JetSpec** — 并行树草稿突破推测解码扩展上限，可达 9.64x 加速 | 16 | cs.CL |
| 8 | **Hallucination in World Models is Predictable** — 世界模型幻觉可预测可预防 | 16 | cs.LG |
| 9 | **FlowR2A** — 流匹配解码器实现多模态驾驶规划 | 16 | cs.AI |
| 10 | **Holistic Data Scheduler** — 多目标 RL 优化 LLM 预训练数据混合 | 16 | cs.LG |
| 11 | **LLM-Assisted Refactoring in Game Dev** — GPT-4o 重构成功但新功能集成困难 | 16 | cs.SE |
| 12 | **How Post-Training Shapes Bio Reasoning Models** — 生物学推理模型后训练各阶段分析 | 15 | cs.LG |
| 13 | **ReNIO** — 负轨迹重加权提升 on-policy 蒸馏 | 15 | cs.LG |
| 14 | **V-Zero** — 无答案标签的细粒度视觉推理框架 | 15 | cs.CV |
| 15 | **Autodata** — AI 代理作为数据科学家生成高质量合成数据 | 15 | cs.AI |
| 16 | **QG-MIL** — Gated Transformer 聚合器用于医学图像 MIL | 15 | cs.CV |
| 17 | **EDV** — 执行-蒸馏-验证框架打破代理经验学习自确认陷阱 | 15 | cs.CL |
| 18 | **The Verification Horizon** — 编码代理奖励设计无银弹 | 14 | cs.AI |
| 19 | **OPID** — On-Policy 技能蒸馏用于代理 RL | 14 | cs.CL |
| 20 | **DREAM** — 自回归建模训练稠密检索嵌入 | 14 | cs.CL |

---

## 🔥 热点主题速览

- **推理与安全**: Top 1 论文揭示推理模型的安全机制比以前认为的要浅得多
- **多模型系统**: Top 2 系统性上限分析说明组合模型收益有限
- **RL 稳定性**: 多篇论文（#5, #13, #15, #17, #19）聚焦 RL/蒸馏训练的稳定性问题
- **3D/CV**: Multi4D (Top 3) + DanceOPD + Semantic Browsing 构成 CV 子主题
- **世界模型幻觉**: #8 展示数据覆盖度是关键

---

*生成时间: 2026-06-27 17:00 UTC*
