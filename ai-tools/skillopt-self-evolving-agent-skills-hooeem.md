---
title: "I want to create self-evolving agent skills — SkillOpt 完全指南"
authors: ["hoeem (@hooeem)"]
tags: ["skillopt", "agent-skills", "self-evolving", "microsoft", "prompt-optimization", "text-space-optimizer", "agent-engineering"]
source: "https://x.com/hooeem/status/2061528919786791154"
date: 2026-06-01
---

# SkillOpt：自进化 agent skill——从"手写"到"训练"

> **来源：** hoeem (@hooeem) 于 X 发布的长文  
> **核心论文：** [arXiv 2605.23904](https://arxiv.org/pdf/2605.23904)  
> **仓库：** [github.com/microsoft/SkillOpt](https://github.com/microsoft/SkillOpt)  
> **官网：** [microsoft.github.io/SkillOpt](https://microsoft.github.io/SkillOpt/)  
> **数据：** 13.7 万 followers，511 bookmarks，6.8 万 views

---

## 一句话概括

> **SkillOpt 是一个文本空间优化器（text-space optimizer）。** 它把你的 skill 文件当作可以"训练"的东西——像训练模型一样，跑一遍你的 agent 在一批任务上的表现，看哪些做对了、哪些错了，让另一个模型提议一小段编辑，只在验证集上分数提高时才接受。

---

## 背景：手写 skill 的痛点

目前人们调试 skill 的方式：手动加规则、删行、跑 eval、再测、再看 agent 表现、再重复。全是靠猜。

SkillOpt 把"猜"这一步去掉了。

### 什么是 skill？

一个 "skill" 就是一段自然语言指令，在 agent 开始工作前塞给它：流程、输出规则、do's and don'ts。SkillOpt 把这个文件当作可以训练的资产——训练的是文本，不是权重。

---

## SkillOpt 原理：四个组件（模仿神经网络训练循环）

1. **Frozen target model**：用当前的 skill 在任务上跑，收集成功与失败
2. **Optimizer model**（第二个 LLM，仅在训练时使用）：分析结果，提议结构化编辑（加这条规则、删那条、替换这行）
3. **Bounded edit budget**（"文本学习率"）：每步只改少量内容，避免大幅重写导致退化。默认预算 `L_t` = 4（逐步衰减到 2）
4. **Validation gate**：在 held-out 集上验证编辑，只有分数严格提升才接受。失败的编辑被记录在拒绝缓存中，优化器不会再提议

**输出**：一个很小的文件。论文中六项基准的最终 `best_skill.md` 只有 380 到 2,000 token，来自仅 1 到 4 次被接受的编辑。几分钟就能读完并审计。

---

## 为什么 SkillOpt 厉害（两个原因）

### 1. 它真的有效

在六项基准（搜索 QA、电子表格、文档、多模态 QA、数学、具身 agent 任务）× 七个 target 模型 × 三种执行模式（direct chat、Codex harness、Claude Code harness）上，**SkillOpt 在全部 52 个 (model, benchmark, harness) 测试单元中，要么最佳要么并列最佳**。

- GPT-5.5 + direct chat 上，六项基准平均从 58.8（无 skill）跃升至 82.3，**+23.5 分**
- 比最强对比基线平均高出 **+5.4 分**
- SpreadsheetBench：41.8 → 80.7
- OfficeQA：33.1 → 72.1

> **最关键的模式**：最大增益落在**程序性任务**（procedural tasks）上——那些需要模型在工具使用和输出格式上守纪律的任务，而不是需要更多原始知识的任务。模型有能力但马虎——SkillOpt 专治这种。

### 2. 它可移植

输出是纯文本，调用的是冻结模型。因此它可以跨环境移植：

- 在 Codex harness 中训练的电子表格 skill，迁移到 Claude Code harness：**+59.7 分**增益
- 在较大 GPT 上训练的 skill 可以改进较小的型号
- 在一个数学基准上训练的 skill 对另一个数学基准也有正增益

---

## 你需要准备什么

### 最重要的输入：答案密钥（answer key）

> SkillOpt 提供评分机制。你提供正确答案。循环负责评分、门控、编辑。仓库不知道你的任务正确输出长什么样——只有你知道。

你需要：
1. 一个包含 `train/`、`val/`、`test/` 三个子文件夹的目录，每个里面一个 `items.json`
2. 每个条目包含 `id`、`question`、`context`（可选）、`answers`（正确答案数组）

最简单的格式（SearchQA）：
```json
[
  {
    "id": "unique_item_id",
    "question": "Who wrote the novel ...",
    "context": "relevant passage text ...",
    "answers": ["expected answer"]
  }
]
```

### 多少样本？

论文完整跑需要上百条，但分析显示在最简单的程序性任务上少量样本就有明显收益，搜索类任务在 ~20% 训练池后饱和。

**建议**：从 20-40 条开始，按 4:1:5 切分 train/val/test。先跑小规模验证循环确实有效，再扩展。

### 内置支持的任务类型（6 种，可直接复用）

- SearchQA
- SpreadsheetBench
- DocQA
- MultiModalQA
- Math
- EmbodiedAgent

**最快路径**：借用 SearchQA 的配置和评分器，把你的任务格式化为 question + answers JSON——零 Python 代码。

### 当精确匹配不够时

如果正确答案不是短规范字符串，退路是用 LLM-as-judge 评分器（接受 OpenAI/Anthropic key）。**但这是更难、更不可靠的路**——噪声明码器会接受错误编辑、拒绝正确编辑，整个循环就会漂移。首选方案：选择一个可以客观评分的任务，完全避免 LLM-as-judge。

> **答案密钥就是整场游戏。下游的一切都信任它。**

---

## 运行流程

### 安装

```bash
git clone https://github.com/microsoft/SkillOpt
cd SkillOpt
pip install -e ".[webui]"
```

### 核心命令

```bash
python scripts/train.py \
    --config configs/searchqa/default.yaml \
    --split_dir /path/to/your/my_split \
    --optimizer_model gpt-5.5 \
    --target_model gpt-5.5 \
    --num_epochs 4 \
    --batch_size 40 \
    --out_root outputs/my_first_run
```

### 两个角色理解

| 参数 | 角色 | 说明 |
|------|------|------|
| `--target_model` | 使用 skill 的模型 | 你最终部署时用的模型，设成生产环境实际使用的 |
| `--optimizer_model` | 提议编辑的模型 | 仅在训练时运行，部署时不携带，**零部署成本**。越强越好但只影响训练质量 |

### 先跑便宜的首次验证

在投入真金白银之前，用小规模低成本运行验证循环是否有效：

1. 两个角色用同一个模型（`--optimizer_model = --target_model`），论文证明同模型优化器仍能恢复大部分增益
2. 把 `--num_epochs` 降到 1 或 2，`--batch_size` 降到数据集大小
3. 用 20-40 条样本
4. 观察验证分数是否移动——如果动了就扩展，没动就回溯检查样本质量

### 从已有 skill 开始

如果你已经有手写的 skill（比如 Claude Skill 文档），不必从默认开始。找到 `configs/<benchmark>/default.yaml` 中的初始 skill 文本，用你的替换。SkillOpt 会在你已有 skill 上演进——保留有效的，修复无效的。

### 输出结构

```
outputs/my_first_run/
├── best_skill.md           # ← 部署用的文件
├── history.json            # 每步训练历史
├── skills/skill_vXXXX.md   # 每步的 skill 快照
├── steps/step_XXXX/        # 每步的编辑和评估结果
├── slow_update/epoch_XX/   # 跨 epoch 的整合日志
└── meta_skill/epoch_XX/    # optimizer 侧笔记（不部署）
```

自动恢复：重新运行相同命令会从最后完成步骤自动继续。

### 监控仪表盘

```bash
pip install -e ".[webui]"
python -m skillopt_webui.app  # --share 可生成公开链接
```

---

## 部署

部署过程只有三步：

1. **阅读 `best_skill.md`** — 它是简短的纯英文。你会看到它将通用指令转化为具体的、经过实战检验的规则。比如在 SpreadsheetBench 案例中，模糊的 "use Python and preserve the workbook" 演化为具体规则：检查实际工作簿而非预览、即使在提示提到公式时也写入计算后的静态值。因为只有少数几次被接受的编辑，你可以逐条阅读并决定是否信任。
2. **在 held-out 测试集上验证增益**：`python scripts/eval_only.py ...`
3. **部署**：`best_skill.md` 就是纯文本。放到 agent 的指令位置（system prompt 前置、或 skill/procedural-memory 文件），**没有权重变化，没有推理时 optimizer，没有额外的循环成本。**

---

## 调优参数（进阶）

每个参数都是训练概念的类比：

| 参数 | 类比 | 说明 |
|------|------|------|
| **Bounded edits** | 学习率 | 每步最多 4 次编辑（衰减到 2），避免大幅度重写导致波动 |
| **Validation gate** | 验证损失 | 每次编辑在 held-out 集上验证，分数严格提高才接受——避免模型"觉得"好但实际差 |
| **Rejected-edit buffer** | 优化器状态 | 失败的编辑被记忆，优化器不会再提议同样的改动。去掉后会显著降低结果 |
| **Slow / Meta update** | 动量 | 每 epoch 结束时，对比当前 skill 和前一个版本，写入一个 "what's durably working" 笔记到 skill 的受保护区域（快速编辑不能覆盖）。去掉这两个更新导致 ablation 中最大的单项降幅 |

---

## 诚实的局限性

1. **成本是真实的，且一次性预付**：两个模型在多个 epoch 和 batch 上跑消耗 API tokens。论文测量每单点测试集增益需要约 0.6M（简单程序性任务）到 46M（长多模态任务）token。好消息：一次训练，永久部署，使用 `best_skill.md` 不会增加任何推理成本。
2. **垃圾答案密钥 = 垃圾 skill**：门控信任你的答案。如果样本错了或不一致，SkillOpt 会忠实地朝错误方向优化。精力花在样本集上，它是一切的基础。
3. **无法制造"正确"**：如果你的任务没有可检验的正确答案，这不是你的工具。

---

## 长期价值：从"手写"到"训练"的范式转变

SkillOpt 真正改变的是构建 skill 的方式：

- **skill 不再是每次出问题就凭直觉重写的 disposable prompt**，而是变成经过训练、验证、保留、携带的资产（asset）
- **一段纯文本，不是黑盒**。可读、可手工修改、可版本控制、可交给队友
- **可移植**：跨模型大小、跨执行 harness、跨相近任务，无需重新训练
- **不再猜测改动是否有帮助**——你是在测量它，然后只保留胜出的

> 曾经只用于模型的优化工具包（数据证据、学习率、验证检查、动量）现在可以应用于 agent stack 中那个原本纯手工的层面。

---

## 与已读内容的连接

1. **与 Perplexity SaC 文章**：SaC 也用 Agent Skills + Autoresearch Loop 来优化 SDK 的"可消费性"，SkillOpt 提供了一个更通用的框架——它定义了从手写 SKILL 到 Auto-improving Skill 的基础设施模式。两者都在回答同一个问题：**如何让 LLM 写的代码/指令变得更好？** SaC 用 autoresearch 做 SDK-level 的优化，SkillOpt 做 skill-level 的优化。

2. **与 Businessbarista "Software Factory"**：SkillOpt 是 Software Factory 质量工程理念的终极体现——不再依靠人工质量保障，而是用自动化闭环（作业生成→执行→评分→编辑→验证）来持续改进 prompt/skill 质量。

3. **与 Rohit "The Harness Is Everything"**：SkillOpt 明确指出其方法在三种执行模式下工作（direct chat、Codex harness、Claude Code harness）。这就是 harness 的价值——它让"训练 skill"这个操作对 harness 本身透明，你可以在一种 harness 里训练，在另一种里部署。

4. **与 Garry Tan "Stop Building Foxconn Factories"**：SkillOpt 是"自由"方向的一个强力实践——它让 skill 成为持续进化的活文档，而不是被锁死在固定提示里的铁笼子。但反过来，SkillOpt 的 validation gate 是一种"控制的自由"：自由不是无约束地改 skill，而是有数据支撑、有验证门控的改进。

5. **与论文 2605.30621 "Harness Evolution"**：SkillOpt 完美契合该论文的三阶段演进框架——它代表了第三阶段（code-native harness）的 skill 管理范式，其中 skill 本身成为可训练、可移植、可验证的资产。
