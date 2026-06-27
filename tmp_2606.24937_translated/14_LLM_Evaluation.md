## \chapter{LLM Evaluation}
## \chapter{LLM 评估（大语言模型评估）}

Evaluation is the backbone of any rigorous machine learning pipeline, yet it is perhaps the most underappreciated component in the development of large language models. Unlike classical supervised learning, where a held-out test set with ground-truth labels provides a clean signal, evaluating LLMs requires grappling with open-ended generation, subjective quality judgments, multi-step reasoning chains, and the ever-present risk of benchmark contamination. This section provides a systematic treatment of the evaluation landscape: from the taxonomy of evaluation types and the mechanics of human annotation, through the mathematics of ranking metrics and the practicalities of LLM-as-judge, to the pitfalls that silently corrupt evaluation pipelines.
评估是任何严谨机器学习流程的支柱，然而它可能是大语言模型开发中最被低估的环节。与经典监督学习（其中保留的测试集和真实标签提供清晰的信号）不同，评估 LLM 需要应对开放式生成、主观质量判断、多步推理链以及始终存在的基准污染风险。本节系统性地阐述了评估领域：从评估类型的分类法和人工标注的机制，到排名指标的数学原理和 LLM-as-judge（大模型作为裁判）的实践，再到那些悄然破坏评估流程的陷阱。

\begin{keybox}[Why Evaluation is Hard for LLMs]
\begin{keybox}[为什么 LLM 评估是困难的]

\textbf{Three fundamental challenges} distinguish LLM evaluation from classical ML evaluation:
\textbf{三大根本挑战} 将 LLM 评估与经典机器学习评估区分开来：

\begin{enumerate}
  \item \textbf{Output space is unbounded.} A language model can produce any string; there is rarely a single correct answer.
  \item \textbf{输出空间是无界的。}语言模型可以生成任意字符串；很少存在唯一正确答案。
  \item \textbf{Quality is multidimensional.} Helpfulness, factuality, safety, coherence, and style are distinct axes that may trade off against each other.
  \item \textbf{质量是多维的。}有用性、事实性、安全性、连贯性和风格是不同的维度，它们之间可能相互权衡。
  \item \textbf{Evaluation is itself a language task.} Judging whether a response is good requires understanding, which means evaluation is susceptible to the same failure modes as generation.
  \item \textbf{评估本身也是一项语言任务。}判断一个回复是否良好需要理解，这意味着评估容易受到与生成相同的故障模式的影响。
\end{enumerate}
\end{keybox}

\section{Evaluation Scheme Design}
\section{评估方案设计}
\label{subsec:eval-scheme}

Before collecting a single data point, practitioners must decide \emph{what} to measure and \emph{how} to measure it. A principled taxonomy prevents the common mistake of choosing metrics by convenience rather than by alignment with the deployment objective.
在收集任何一个数据点之前，从业者必须决定\emph{衡量什么}以及\emph{如何衡量}。一个原则性的分类法可以防止常见的错误：即为了方便而非与部署目标对齐来选择指标。

\subsection{Taxonomy of Evaluation Types}
\subsection{评估类型分类法}
\label{taxonomy-of-evaluation-types}

\paragraph{Intrinsic vs.~Extrinsic Evaluation.}
\paragraph{内在评估 vs. 外在评估。}
\label{intrinsic-vs.-extrinsic-evaluation.}

\emph{Intrinsic} evaluation measures properties of the model output in isolation, without reference to a downstream application. Perplexity on a held-out corpus, BLEU score against reference translations, and pass@$k$ on coding benchmarks are all intrinsic. \emph{Extrinsic} evaluation measures the impact of the model on a real-world task or system: does integrating the LLM into a customer-service pipeline reduce ticket escalation rates? Does the coding assistant increase developer velocity?
\emph{内在评估}孤立地衡量模型输出的属性，不参考下游应用。在保留语料库上的困惑度（Perplexity）、与参考翻译对照的 BLEU 分数、以及在编程基准上的 pass@$k$ 都属于内在评估。\emph{外在评估}衡量模型对真实任务或系统的影响：将 LLM 集成到客服流程中是否能降低工单升级率？编程助手是否能提高开发者的速度？

\begin{intuitionbox}[The Intrinsic–Extrinsic Gap]
\begin{intuitionbox}[内在-外在差距]

Intrinsic metrics are cheap and reproducible but often poorly correlated with real-world utility. A model with lower perplexity is not necessarily more helpful. Extrinsic metrics are expensive and slow but directly measure what we care about. A mature evaluation strategy uses intrinsic metrics for rapid iteration and extrinsic metrics for final validation.
内在指标成本低、可重复，但通常与实际效用相关性较差。一个困惑度较低的模型不一定更有用。外在指标成本高、速度慢，但直接衡量我们所关心的内容。成熟的评估策略使用内在指标进行快速迭代，使用外在指标进行最终验证。
\end{intuitionbox}

\paragraph{Automatic vs.~Human Evaluation.}
\paragraph{自动评估 vs. 人工评估。}
\label{automatic-vs.-human-evaluation.}

\emph{Automatic} evaluation uses deterministic functions (BLEU, exact match) or learned models (BERTScore, LLM-as-judge) to score outputs without human involvement. \emph{Human} evaluation involves annotators rating or ranking model outputs. Table~\ref{tab:eval-taxonomy} summarises the trade-offs.
\emph{自动评估}使用确定性函数（BLEU、精确匹配）或学习模型（BERTScore、LLM-as-judge）对输出进行评分，无需人工参与。\emph{人工评估}由标注者评分或对模型输出进行排名。表~\ref{tab:eval-taxonomy} 总结了权衡。

\begin{table}[ht!]
\centering
\caption{Taxonomy of evaluation approaches with key trade-offs.}
\caption{评估方法分类及关键权衡}
\label{tab:eval-taxonomy}
\begin{tabular}{@{}lp{3cm}p{3.2cm}p{3.2cm}p{3.5cm}@{}}
\toprule
\textbf{Type} & \textbf{Cost} & \textbf{Speed} & \textbf{Reproducibility} & \textbf{Validity} \\
\textbf{类型} & \textbf{成本} & \textbf{速度} & \textbf{可复现性} & \textbf{有效性} \\
\midrule
Automatic (rule-based) & Very low & Very fast & Perfect & Low--Medium \\
自动（基于规则） & 非常低 & 非常快 & 完美 & 低-中 \\
Automatic (model-based) & Low & Fast & High & Medium--High \\
自动（基于模型） & 低 & 快 & 高 & 中-高 \\
Crowdsourced human & Medium & Days & Medium & Medium \\
众包人工 & 中 & 数天 & 中 & 中 \\
Expert human & High & Weeks & Low--Medium & High \\
专家人工 & 高 & 数周 & 低-中 & 高 \\
Extrinsic / A/B test & Very high & Months & Low & Very high \\
外在 / A/B 测试 & 非常高 & 数月 & 低 & 非常高 \\
\bottomrule
\end{tabular}
\end{table}

\paragraph{Reference-Based vs.~Reference-Free Evaluation.}
\paragraph{基于参考的评估 vs. 无参考的评估。}
\label{reference-based-vs.-reference-free-evaluation.}

Reference-based metrics (BLEU, ROUGE, BERTScore) compare model output to one or more gold-standard references. Reference-free metrics (perplexity, LLM-as-judge, human preference) assess quality without a reference. Reference-free approaches are essential when the output space is too large for exhaustive reference collection, as in open-ended dialogue.
基于参考的指标（BLEU、ROUGE、BERTScore）将模型输出与一个或多个黄金标准参考进行比较。无参考指标（困惑度、LLM-as-judge、人工偏好）无需参考即可评估质量。当输出空间太大而无法收集详尽的参考时（例如开放式对话），无参考方法至关重要。

\subsection{When to Use What}
\subsection{何时使用何种评估}
\label{when-to-use-what}

\begin{examplebox}[Evaluation Strategy for a Dialogue Assistant]
\begin{examplebox}[对话助手的评估策略]

\textbf{Development phase:} Use automatic metrics (perplexity, ROUGE on summarisation sub-tasks, pass@$k$ on tool-use) for rapid iteration. Run nightly benchmarks on standard suites (MMLU, HellaSwag, HumanEval).
\textbf{开发阶段：}使用自动指标（困惑度、摘要子任务的 ROUGE、工具使用的 pass@$k$）进行快速迭代。在标准套件（MMLU、HellaSwag、HumanEval）上运行夜间基准测试。

\textbf{Pre-release phase:} Conduct a human preference study comparing the new model to the previous checkpoint. Use LLM-as-judge for scalable pairwise comparison on a diverse prompt set.
\textbf{预发布阶段：}进行人工偏好研究，将新模型与之前的检查点进行比较。使用 LLM-as-judge 在多样化的提示集上进行可扩展的成对比较。

\textbf{Post-release phase:} Monitor extrinsic metrics (user satisfaction scores, task completion rates) and watch for distribution shift in production prompts.
\textbf{发布后阶段：}监控外在指标（用户满意度分数、任务完成率），并留意生产环境中提示的分布偏移。
\end{examplebox}

A useful decision framework:
一个有用的决策框架：

\begin{itemize}
  \item If the task has a clear correct answer (math, code, factual QA): use exact match or execution-based metrics.
  \item 如果任务有明确的正确答案（数学、代码、事实问答）：使用精确匹配或基于执行的指标。
  \item If the task is open-ended but has reference outputs: use reference-based metrics as a lower bound, supplement with LLM-as-judge.
  \item 如果任务是开放式的但有参考输出：使用基于参考的指标作为下限，并用 LLM-as-judge 补充。
  \item If the task is subjective (helpfulness, tone, creativity): use human evaluation or a well-calibrated LLM judge.
  \item 如果任务是主观的（有用性、语气、创造力）：使用人工评估或经过良好校准的 LLM 裁判。
  \item If the task involves multi-step agent behaviour: use task success rate and trajectory efficiency (Section~\ref{subsec:agentic-metrics}).
  \item 如果任务涉及多步智能体行为：使用任务成功率和轨迹效率（第~\ref{subsec:agentic-metrics}节）。
\end{itemize}

\section{Data Collection for Evaluation}
\section{评估数据收集}
\label{subsec:data-collection}

High-quality evaluation data is the foundation of trustworthy benchmarks. This section covers the design of human annotation pipelines, statistical measures of annotation quality, and the choice between crowdsourcing and expert annotation.
高质量的评估数据是可信基准的基础。本节涵盖人工标注流程的设计、标注质量的统计度量，以及众包与专家标注之间的选择。

\subsection{Human Annotation Pipelines}
\subsection{人工标注流程}
\label{human-annotation-pipelines}

A robust annotation pipeline consists of five stages:
一个稳健的标注流程包含五个阶段：

\begin{enumerate}
  \item \textbf{Task definition.} Specify the annotation task precisely: what is being rated, on what scale, and with what criteria. Ambiguity at this stage propagates into noisy labels.
  \item \textbf{任务定义。}精确指定标注任务：评什么内容、使用什么尺度、依据什么标准。此阶段的歧义会传播成噪声标签。
  \item \textbf{Guideline development.} Write annotation guidelines with worked examples covering edge cases. Iterate with a small pilot group before full deployment.
  \item \textbf{指南制定。}编写标注指南，包含覆盖边缘案例的实例。在全面部署之前与一个小型试点小组进行迭代。
  \item \textbf{Annotator recruitment and training.} Select annotators with appropriate background knowledge. Conduct a calibration session where annotators label the same examples and discuss disagreements.
  \item \textbf{标注者招募与培训。}选择具有适当背景知识的标注者。举办校准会议，让标注者对相同示例进行标注并讨论分歧。
  \item \textbf{Quality control.} Embed gold-standard examples with known labels into the annotation queue. Flag annotators whose accuracy on gold examples falls below a threshold.
  \item \textbf{质量控制。}将带有已知标签的黄金标准示例嵌入标注队列中。对黄金示例准确率低于阈值的标注者进行标记。
  \item \textbf{Aggregation.} Combine multiple annotations per item using majority vote, averaging, or a probabilistic model (e.g., Dawid--Skene).
  \item \textbf{聚合。}通过多数投票、平均或概率模型（例如 Dawid--Skene）合并每个项目的多个标注。
\end{enumerate}

\subsection{Inter-Annotator Agreement}
\subsection{标注者间一致性}
\label{inter-annotator-agreement}

Raw agreement (fraction of items where all annotators agree) is an inadequate measure because it does not account for chance agreement. Two standard chance-corrected measures are Cohen’s $\kappa$~\cite{cohen1960coefficient} (two annotators) and Fleiss’ $\kappa$~\cite{fleiss1971measuring} (multiple annotators).
原始一致性（所有标注者一致同意的项目比例）是一个不充分的度量，因为它没有考虑随机一致性。两种标准的校正了随机一致性的度量是 Cohen 的 $\kappa$~\cite{cohen1960coefficient}（适用于两位标注者）和 Fleiss 的 $\kappa$~\cite{fleiss1971measuring}（适用于多位标注者）。

\paragraph{Cohen’s Kappa.}
\paragraph{Cohen 的 Kappa。}
\label{cohens-kappa.}

## Evaluation Scheme Design
## 评估方案设计

Given two annotators labelling $N$ items into $k$ categories, let $p_o$ be the observed agreement and $p_e$ be the expected agreement under independence: 
给定两个标注者对 $N$ 个项进行 $k$ 类别标注，设 $p_o$ 为观测一致率，$p_e$ 为独立假设下的期望一致率：
\begin{equation}
    \kappa = \frac{p_o - p_e}{1 - p_e}
\label{eq:cohens-kappa}
\end{equation}
 where 
其中
\begin{equation}
    p_o = \frac{1}{N}\sum_{i=1}^{N} \mathbf{1}[\text{annotator 1 agrees with annotator 2 on item } i]
\end{equation}
 and 
以及
\begin{equation}
    p_e = \sum_{c=1}^{k} p_{1c} \cdot p_{2c}
\end{equation}
 with $p_{jc}$ being the proportion of items assigned to category $c$ by annotator $j$. Cohen’s $\kappa$ ranges from $-1$ (perfect disagreement) through $0$ (chance agreement) to $1$ (perfect agreement). Values above $0.6$ are generally considered acceptable; above $0.8$ is strong agreement.
其中 $p_{jc}$ 是标注者 $j$ 将项分配给类别 $c$ 的比例。Cohen’s $\kappa$ 的取值范围从 $-1$（完全不一致）经 $0$（随机一致）到 $1$（完全一致）。大于 $0.6$ 的值通常认为可接受；大于 $0.8$ 则为强一致。

\paragraph{Fleiss’ Kappa.}
\paragraph{Fleiss’ Kappa（弗莱斯 Kappa）.}
\label{fleiss-kappa.}


For $n$ annotators labelling $N$ items into $k$ categories, let $n_{ij}$ be the number of annotators who assigned item $i$ to category $j$. Define: 
对于 $n$ 个标注者对 $N$ 个项进行 $k$ 类别标注，设 $n_{ij}$ 是将项 $i$ 分配给类别 $j$ 的标注者数量。定义：
\begin{equation}
    \bar{P}_i = \frac{1}{n(n-1)} \sum_{j=1}^{k} n_{ij}(n_{ij} - 1), \qquad \bar{P} = \frac{1}{N}\sum_{i=1}^{N}\bar{P}_i
\end{equation}
 
\begin{equation}
    \bar{P}_j^e = \frac{1}{Nn}\sum_{i=1}^{N} n_{ij}, \qquad P_e = \sum_{j=1}^{k} \left(\bar{P}_j^e\right)^2
\end{equation}
 
\begin{equation}
    \kappa_F = \frac{\bar{P} - P_e}{1 - P_e}
\end{equation}


\begin{warningbox}[Kappa Limitations]
\begin{warningbox}[Kappa 的局限性]
Kappa is sensitive to the prevalence of categories: when one category dominates, kappa can be low even when raw agreement is high (the \emph{kappa paradox}). For ordinal scales, weighted kappa (which penalises disagreements proportionally to their distance) is more appropriate. For LLM evaluation, where ratings are often on a 1--5 Likert scale, always report weighted kappa.
Kappa 对类别的 prevalence（流行率）敏感：当某个类别占主导时，即使原始一致率很高，kappa 也可能很低（即 \emph{kappa 悖论}）。对于有序量表，加权 kappa（按距离比例惩罚不一致）更为合适。在 LLM 评估中，评分通常采用 1--5 的 Likert 量表，应始终报告加权 kappa。
\end{warningbox}


\subsection{Annotation Guideline Design}
\subsection{标注指南设计}
\label{annotation-guideline-design}


Effective annotation guidelines share several properties:
有效的标注指南具有以下几个共同特性：

\begin{itemize}
  \item \textbf{Operationalised criteria.} Replace vague terms like ``helpful'' with concrete, observable behaviours: ``The response directly addresses the user’s question and provides all information needed to complete the stated task.''
  \item \textbf{操作化标准。} 用具体、可观察的行为替换模糊术语（如“有帮助”）： “回答直接回应用户的问题，并提供完成所述任务所需的所有信息。”
  \item \textbf{Worked examples.} Provide at least two examples per rating level, including borderline cases.
  \item \textbf{示例说明。} 每个评分等级至少提供两个示例，包括边界情况。
  \item \textbf{Decision trees.} For complex tasks, a flowchart that guides annotators through a sequence of binary decisions reduces cognitive load and improves consistency.
  \item \textbf{决策树。} 对于复杂任务，使用流程图引导标注者通过一系列二元决策，可减少认知负荷并提高一致性。
  \item \textbf{Explicit scope.} State what annotators should \emph{not} consider (e.g., ``Do not penalise for stylistic preferences; focus only on factual accuracy'').
  \item \textbf{明确范围。} 说明标注者 \emph{不应} 考虑哪些因素（例如，“不要因风格偏好而扣分；只关注事实准确性”）。
\end{itemize}


\subsection{Crowdsourcing vs.~Expert Annotation}
\subsection{众包 vs. 专家标注}
\label{crowdsourcing-vs.-expert-annotation}


\begin{table}[ht!]
\centering
\caption{Comparison of crowdsourcing and expert annotation for LLM evaluation.}
\caption{众包与专家标注在 LLM 评估中的比较。}
\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Dimension} & \textbf{Crowdsourcing} & \textbf{Expert Annotation} \\
\textbf{维度} & \textbf{众包} & \textbf{专家标注} \\
\midrule
Cost per item & Low (\$0.01--\$0.10) & High (\$1--\$50) \\
每项成本 & 低（\$0.01--\$0.10） & 高（\$1--\$50） \\
Throughput & Very high & Low \\
吞吐量 & 非常高 & 低 \\
Domain knowledge & Low & High \\
领域知识 & 低 & 高 \\
Consistency & Variable & High \\
一致性 & 可变 & 高 \\
Suitable tasks & Simple preference, fluency & Technical accuracy, safety \\
适用任务 & 简单偏好、流畅性 & 技术准确性、安全性 \\
Platforms & MTurk, Prolific, Scale AI & Domain specialists, in-house \\
平台 & MTurk, Prolific, Scale AI & 领域专家、内部人员 \\
Quality control & Gold examples, attention checks & Calibration sessions, peer review \\
质量控制 & 黄金样本、注意力检查 & 校准会议、同行评审 \\
\bottomrule
\end{tabular}
\end{table}


For safety-critical evaluation (e.g., detecting harmful outputs, evaluating medical advice), expert annotation is non-negotiable. For large-scale preference collection (e.g., building a reward model training set), crowdsourcing with rigorous quality control is often the only feasible option.
对于安全关键的评估（例如检测有害输出、评估医疗建议），专家标注是不可妥协的。对于大规模偏好收集（例如构建奖励模型训练集），采用严格质量控制的众包通常是唯一可行的选择。

\section{Synthetic Data Generation for Evaluation}
\section{用于评估的合成数据生成}
\label{subsec:synthetic-data}


Human annotation is expensive and slow. Synthetic data generation uses LLMs themselves to produce evaluation data at scale. This section covers the major paradigms.
人工标注昂贵且缓慢。合成数据生成利用 LLM 自身来大规模生成评估数据。本节介绍主要范式。

\subsection{LLM-as-Judge for Calibration}
\subsection{基于 LLM 作为评估者的校准}
\label{llm-as-judge-for-calibration}


When using an LLM to generate evaluation labels, calibration is essential: the judge’s scores must be aligned with human judgments. Let $h_i \in [0,1]$ be the human preference score for item $i$ and $\hat{h}_i$ be the judge’s predicted score. Calibration error is measured by the Expected Calibration Error (ECE)~\cite{guo2017calibration}: 
当使用 LLM 生成评估标签时，校准至关重要：评估者的分数必须与人类判断一致。设 $h_i \in [0,1]$ 为项 $i$ 的人类偏好分数，$\hat{h}_i$ 为评估者的预测分数。校准误差通过期望校准误差（Expected Calibration Error, ECE）~\cite{guo2017calibration} 度量：
\begin{equation}
    \text{ECE} = \sum_{b=1}^{B} \frac{|B_b|}{n} \left| \text{acc}(B_b) - \text{conf}(B_b) \right|
\end{equation}
 where $B_b$ is the $b$-th confidence bin, $\text{acc}(B_b)$ is the fraction of items in the bin where the judge agrees with humans, and $\text{conf}(B_b)$ is the mean judge confidence in that bin.
其中 $B_b$ 是第 $b$ 个置信区间，$\text{acc}(B_b)$ 是该区间内评估者与人类一致的项目比例，$\text{conf}(B_b)$ 是该区间内评估者的平均置信度。


A well-calibrated judge satisfies $\mathbb{E}[\hat{h}_i \mid \hat{h}_i = p] = p$ for all $p \in [0,1]$. Calibration can be improved by temperature scaling: replacing the judge’s raw logit $z$ with $z/T$ where $T$ is tuned on a held-out calibration set to minimise negative log-likelihood.
一个良好校准的评估者满足 $\mathbb{E}[\hat{h}_i \mid \hat{h}_i = p] = p$ 对所有 $p \in [0,1]$ 成立。可以通过温度缩放（temperature scaling）改善校准：将评估者的原始 logit $z$ 替换为 $z/T$，其中 $T$ 在保留的校准集上调整以最小化负对数似然。

\subsection{Self-Instruct}
\subsection{Self-Instruct（自指导）}
\label{self-instruct}


Self-Instruct~\cite{wang2022selfinstruct} bootstraps instruction-following data from a seed set of human-written tasks. The algorithm:
Self-Instruct~\cite{wang2022selfinstruct} 从一组人工编写的种子任务中引导生成指令遵循数据。算法如下：

\begin{enumerate}
  \item Maintain a task pool initialised with $175$ seed tasks.
  \item 维护一个初始包含 $175$ 个种子任务的任务池。
  \item Sample $8$ tasks from the pool; use them as few-shot examples to prompt the LLM to generate new tasks.
  \item 从池中采样 $8$ 个任务；将它们作为少样本示例，提示 LLM 生成新任务。
  \item Filter generated tasks: remove near-duplicates (ROUGE-L similarity $> 0.7$ with any existing task), classify as classification vs.~non-classification, and generate input--output instances.
  \item 过滤生成的任务：移除近重复项（与任何现有任务的 ROUGE-L 相似度 $> 0.7$），分类为分类任务或非分类任务，并生成输入-输出实例。
  \item Add accepted tasks to the pool.
  \item 将接受的任务添加到池中。
  \item Repeat until the desired pool size is reached.
  \item 重复直到达到所需的池大小。
\end{enumerate}


\begin{examplebox}[Self-Instruct Prompt Template]
\begin{examplebox}[Self-Instruct 提示模板]
\begin{lstlisting}[style=pythonstyle]
system_prompt = """
Come up with a series of tasks:
Task 1: {seed_task_1_instruction}
Task 2: {seed_task_2_instruction}
...
Task 8: {seed_task_8_instruction}
Task 9:"""
\end{lstlisting}


The model completes the prompt, generating a new task instruction. A separate prompt then generates input--output pairs for the new task.
模型补全提示，生成新的任务指令。随后使用另一个提示为新任务生成输入-输出对。
\end{examplebox}


\subsection{Evol-Instruct}
\subsection{Evol-Instruct（进化指导）}
\label{evol-instruct}


Evol-Instruct~\cite{xu2023wizardlm} evolves a seed instruction set by iteratively rewriting instructions to be more complex or diverse. Two evolution operators are applied:
Evol-Instruct~\cite{xu2023wizardlm} 通过迭代重写指令使其更复杂或更多样化，从而进化种子指令集。应用两种进化算子：

\begin{itemize}
  \item \textbf{In-depth evolution:} Add constraints, increase reasoning steps, concretise abstractions, deepen domain knowledge requirements.
  \item \textbf{深度进化：} 增加约束、增加推理步骤、具体化抽象概念、加深领域知识要求。
  \item \textbf{In-breadth evolution:} Generate a new instruction on a related but different topic, increasing topic diversity.
  \item \textbf{广度进化：} 在相关但不同的主题上生成新指令，增加主题多样性。
\end{itemize}


An instruction is accepted if it passes an elimination filter: the evolved instruction must not be a simple copy, must not contain ``I’m sorry'' or similar refusals, and must not be shorter than the original.
指令通过消除过滤器后才被接受：进化后的指令不能是简单的复制，不能包含“I’m sorry”或类似的拒绝语句，并且不能比原始指令更短。

\subsection{Constitutional AI Data Generation}
\subsection{Constitutional AI（宪法式 AI）数据生成}
\label{constitutional-ai-data-generation}


Constitutional AI (CAI)~\cite{bai2022constitutional} generates preference data by having the model critique and revise its own outputs according to a set of principles (the ``constitution''). The pipeline:
Constitutional AI（CAI）~\cite{bai2022constitutional} 通过让模型根据一组原则（“宪法”）对自己的输出进行批评和修订来生成偏好数据。流程如下：

\begin{enumerate}
  \item \textbf{Supervised learning phase:} Sample a harmful prompt, generate an initial response, then prompt the model to critique the response according to a constitutional principle and revise it. Use the revised response as a supervised fine-tuning target.
  \item \textbf{监督学习阶段：} 抽样一个有害提示，生成初始回复，然后提示模型根据宪法原则批评并修订该回复。将修订后的回复作为监督微调目标。
  \item \textbf{RL phase:} Generate pairs of responses (original vs.~revised), use the model to label which is more constitutional, and train a preference model on these labels. Use the preference model as a reward signal for RLHF.
  \item \textbf{强化学习阶段：} 生成回复对（原始 vs. 修订版），使用模型标记哪个更符合宪法，并基于这些标签训练偏好模型。将偏好模型作为 RLHF 的奖励信号。
\end{enumerate}


This approach generates preference data without human labelling of harmful content, reducing annotator exposure to distressing material.
这种方法无需人工标注有害内容即可生成偏好数据，减少了标注者接触令人不适的材料。

\subsection{Distillation for Evaluation Data}
\subsection{用于评估数据的蒸馏}
\label{distillation-for-evaluation-data}

## Evaluation Scheme Design
## 评估方案设计

A powerful teacher model (e.g., GPT-4) can generate high-quality evaluation data for training a smaller judge model. The distillation pipeline:
一个强大的教师模型（例如 GPT-4）可以生成高质量的评价数据，用于训练较小的评判模型。其蒸馏流程如下：

\begin{enumerate}
  \item Collect a diverse set of prompts and model responses.
  \item Use the teacher to generate detailed judgments (scores + rationales).
  \item Fine-tune a smaller model on (prompt, response, judgment) triples.
  \item Validate the student judge against held-out human annotations.
\end{enumerate}

\begin{enumerate}
  \item 收集多样化的提示词和模型响应。
  \item 使用教师模型生成详细的评判（分数+理由）。
  \item 在（提示词、响应、评判）三元组上微调一个较小的模型。
  \item 将学生评判模型与保留的人工标注进行验证。
\end{enumerate}

\begin{warningbox}[Distillation Bias]
A student judge distilled from a single teacher inherits the teacher’s biases, including verbosity bias (preferring longer responses), self-enhancement bias (if the teacher is also the model being evaluated), and positional bias. Always validate distilled judges against independent human annotations.
\end{warningbox}

\begin{warningbox}[蒸馏偏差]
从单一教师模型中蒸馏得到的学生评判模型会继承教师模型的偏差，包括冗长偏差（偏好更长的响应）、自我增强偏差（如果教师模型同时也是被评估的模型）以及位置偏差。务必使用独立的人工标注来验证蒸馏得到的评判模型。
\end{warningbox}

\subsection{Arena-Style Pairwise Generation}
\label{arena-style-pairwise-generation}

## Arena 风格的成对生成
## \label{arena-style-pairwise-generation}

Chatbot Arena~\cite{zheng2023judging} generates evaluation data through a crowdsourced battle platform where users submit prompts and vote on which of two anonymised model responses they prefer. This produces a large-scale, naturally diverse dataset of pairwise preferences. The key design choices:
Chatbot Arena~\cite{zheng2023judging} 通过众包对战平台生成评估数据，用户提交提示词，然后对两个匿名模型响应中更偏好的一个进行投票。这产生了大规模、自然多样的成对偏好数据集。关键设计选择如下：

\begin{itemize}
  \item \textbf{Anonymisation:} Model identities are hidden to prevent brand bias.
  \item \textbf{User-submitted prompts:} Ensures prompt diversity and real-world relevance.
  \item \textbf{Tie handling:} Users can declare a tie or indicate that both responses are bad.
  \item \textbf{Deduplication:} Near-duplicate prompts are filtered to prevent over-representation of common queries.
\end{itemize}

\begin{itemize}
  \item \textbf{匿名化：} 隐藏模型身份以防止品牌偏见。
  \item \textbf{用户提交的提示词：} 确保提示词的多样性和现实相关性。
  \item \textbf{平局处理：} 用户可以声明平局或指出两个响应都不好。
  \item \textbf{去重：} 过滤近似重复的提示词，防止常见查询的过度代表。
\end{itemize}

\section{Metrics for Ranking Tasks}
\label{subsec:ranking-metrics}

## 排名任务指标
## \label{subsec:ranking-metrics}

When the goal is to rank models by quality, pairwise comparison data is more reliable than absolute scores. This section derives the major ranking systems used in LLM evaluation.
当目标是按质量对模型进行排名时，成对比较数据比绝对分数更可靠。本节推导了LLM评估中使用的主要排名系统。

\subsection{ELO Rating System}
\label{elo-rating-system}

## ELO 评分系统
## \label{elo-rating-system}

The ELO system~\cite{elo1978rating}, originally developed for chess, assigns each player (model) a scalar rating $R$ such that the expected score of player $A$ against player $B$ is: 
\begin{equation}
    E_A = \frac{1}{1 + 10^{(R_B - R_A)/400}}
\end{equation}
ELO系统~\cite{elo1978rating}最初为国际象棋开发，为每位玩家（模型）分配一个标量评分 $R$，使得玩家 $A$ 对阵玩家 $B$ 的期望得分为：
\begin{equation}
    E_A = \frac{1}{1 + 10^{(R_B - R_A)/400}}
\end{equation}

\paragraph{Derivation.}
\label{derivation.}

\paragraph{推导.}
\label{derivation.}

The ELO model assumes that each player’s performance on a given game is a random variable drawn from a logistic distribution centred at their rating. The probability that $A$ beats $B$ is: 
\begin{equation}
    P(A \succ B) = \sigma\!\left(\frac{R_A - R_B}{s}\right) = \frac{1}{1 + e^{-(R_A - R_B)/s}}
\end{equation}
 where $s = 400/\ln(10) \approx 173.7$ is a scale parameter chosen so that a 400-point difference corresponds to a $10:1$ odds ratio. After each game with outcome $S_A \in \{0, 0.5, 1\}$ (loss, draw, win), ratings are updated: 
\begin{equation}
    R_A \leftarrow R_A + K(S_A - E_A), \qquad R_B \leftarrow R_B + K(S_B - E_B)
\end{equation}
 where $K$ is the $K$-factor controlling the learning rate. In Chatbot Arena, $K = 4$ is used.
ELO模型假设每位玩家在单场比赛中的表现是一个随机变量，取自以其评分为中心的逻辑分布。$A$ 击败 $B$ 的概率为：
\begin{equation}
    P(A \succ B) = \sigma\!\left(\frac{R_A - R_B}{s}\right) = \frac{1}{1 + e^{-(R_A - R_B)/s}}
\end{equation}
其中 $s = 400/\ln(10) \approx 173.7$ 是一个尺度参数，选择它使得400分的差异对应 $10:1$ 的赔率。每场比赛结束后，根据结果 $S_A \in \{0, 0.5, 1\}$（输、平、赢），评分更新如下：
\begin{equation}
    R_A \leftarrow R_A + K(S_A - E_A), \qquad R_B \leftarrow R_B + K(S_B - E_B)
\end{equation}
其中 $K$ 是控制学习速率的 $K$ 因子。在Chatbot Arena中，使用 $K = 4$。

\begin{intuitionbox}[ELO Intuition]
ELO is a stochastic gradient descent update on the log-likelihood of the observed outcomes under the logistic model. Each game provides a noisy gradient signal; the $K$-factor controls the step size. A large $K$ adapts quickly but is noisy; a small $K$ is stable but slow to reflect true skill changes.
\end{intuitionbox}

\begin{intuitionbox}[ELO 直觉理解]
ELO是对逻辑模型下观测结果的似然对数进行随机梯度下降更新。每场比赛提供一个带噪声的梯度信号；$K$因子控制步长。大的$K$值适应迅速但噪声大；小的$K$值稳定但反映真实技能变化缓慢。
\end{intuitionbox}

\paragraph{Bootstrap Confidence Intervals for ELO.}
\label{bootstrap-confidence-intervals-for-elo.}

\paragraph{ELO 的 Bootstrap 置信区间.}
\label{bootstrap-confidence-intervals-for-elo.}

Because ELO ratings depend on the order in which games are processed, confidence intervals are computed by bootstrap resampling: resample the battle log with replacement $B = 1000$ times, recompute ELO ratings from scratch for each resample, and report the 2.5th and 97.5th percentiles as the 95\% confidence interval.
由于ELO评分依赖于比赛处理的顺序，置信区间通过Bootstrap重采样计算：对对战日志进行有放回的重采样 $B = 1000$ 次，对每个重采样样本从头重新计算ELO评分，并将第2.5百分位和第97.5百分位报告为95%置信区间。

\subsection{Bradley--Terry Model}
\label{bradleyterry-model}

## Bradley--Terry 模型
## \label{bradleyterry-model}

The Bradley--Terry (BT) model~\cite{bradley1952rank} is a maximum-likelihood alternative to ELO. Given $n$ models with strength parameters $\beta_1, \ldots, \beta_n > 0$, the probability that model $i$ beats model $j$ is: 
\begin{equation}
    P(i \succ j) = \frac{\beta_i}{\beta_i + \beta_j}
\end{equation}
Bradley--Terry (BT) 模型~\cite{bradley1952rank} 是ELO的一种最大似然替代方法。给定 $n$ 个模型，其强度参数 $\beta_1, \ldots, \beta_n > 0$，模型 $i$ 击败模型 $j$ 的概率为：
\begin{equation}
    P(i \succ j) = \frac{\beta_i}{\beta_i + \beta_j}
\end{equation}

Given a set of pairwise outcomes $\{(i_k, j_k, y_k)\}_{k=1}^{M}$ where $y_k = 1$ if $i_k$ beats $j_k$ and $y_k = 0$ otherwise, the log-likelihood is: 
\begin{equation}
    \ell(\boldsymbol{\beta}) = \sum_{k=1}^{M} \left[ y_k \log \frac{\beta_{i_k}}{\beta_{i_k} + \beta_{j_k}} + (1-y_k) \log \frac{\beta_{j_k}}{\beta_{i_k} + \beta_{j_k}} \right]
\end{equation}
给定一组成对结果 $\{(i_k, j_k, y_k)\}_{k=1}^{M}$，其中如果 $i_k$ 击败 $j_k$ 则 $y_k = 1$，否则 $y_k = 0$，对数似然为：
\begin{equation}
    \ell(\boldsymbol{\beta}) = \sum_{k=1}^{M} \left[ y_k \log \frac{\beta_{i_k}}{\beta_{i_k} + \beta_{j_k}} + (1-y_k) \log \frac{\beta_{j_k}}{\beta_{i_k} + \beta_{j_k}} \right]
\end{equation}

The MLE $\hat{\boldsymbol{\beta}}$ is found by iterative scaling or gradient ascent. The BT model is identifiable only up to a multiplicative constant; a common normalisation is $\sum_i \log \beta_i = 0$. Working in log-space with $\theta_i = \log \beta_i$ gives: 
\begin{equation}
    P(i \succ j) = \sigma(\theta_i - \theta_j)
\end{equation}
 which is equivalent to a logistic regression with item-specific intercepts. The BT model is preferred over ELO when the full battle history is available, as it uses all data simultaneously rather than processing games sequentially.
MLE $\hat{\boldsymbol{\beta}}$ 通过迭代缩放或梯度上升求得。BT模型仅在乘以一个常数时是可识别的；常用的归一化是 $\sum_i \log \beta_i = 0$。在对数空间中使用 $\theta_i = \log \beta_i$ 可得：
\begin{equation}
    P(i \succ j) = \sigma(\theta_i - \theta_j)
\end{equation}
这等价于具有项目特定截距的逻辑回归。当完整的对战历史可用时，BT模型优于ELO，因为它同时使用所有数据，而不是顺序处理比赛。

\subsection{TrueSkill}
\label{trueskill}

## TrueSkill
## \label{trueskill}

TrueSkill~\cite{herbrich2006trueskill} is a Bayesian skill rating system that models each player’s skill as a Gaussian random variable $s_i \sim \mathcal{N}(\mu_i, \sigma_i^2)$. The performance of player $i$ in a game is $p_i = s_i + \epsilon_i$ where $\epsilon_i \sim \mathcal{N}(0, \beta^2)$ is game-specific noise. Player $i$ beats player $j$ if $p_i > p_j$.
TrueSkill~\cite{herbrich2006trueskill} 是一个贝叶斯技能评分系统，将每位玩家的技能建模为高斯随机变量 $s_i \sim \mathcal{N}(\mu_i, \sigma_i^2)$。玩家 $i$ 在比赛中的表现为 $p_i = s_i + \epsilon_i$，其中 $\epsilon_i \sim \mathcal{N}(0, \beta^2)$ 是特定比赛的噪声。如果 $p_i > p_j$，则玩家 $i$ 击败玩家 $j$。

The posterior update after observing $i \succ j$ is computed via expectation propagation (EP). The key update equations for the winner are: 
\begin{equation}
    \mu_i \leftarrow \mu_i + \frac{\sigma_i^2}{c} \cdot v\!\left(\frac{\mu_i - \mu_j}{c}\right)
\end{equation}
 
\begin{equation}
    \sigma_i^2 \leftarrow \sigma_i^2 \left[1 - \frac{\sigma_i^2}{c^2} \cdot w\!\left(\frac{\mu_i - \mu_j}{c}\right)\right]
\end{equation}
 where $c = \sqrt{2\beta^2 + \sigma_i^2 + \sigma_j^2}$, and $v(t) = \phi(t)/\Phi(t)$, $w(t) = v(t)(v(t) + t)$ are the truncated Gaussian correction factors ($\phi$ and $\Phi$ are the standard normal PDF and CDF). TrueSkill’s uncertainty estimate $\sigma_i$ is particularly useful for identifying models that need more evaluation data.
观测到 $i \succ j$ 后的后验更新通过期望传播 (EP) 计算。获胜者的关键更新公式为：
\begin{equation}
    \mu_i \leftarrow \mu_i + \frac{\sigma_i^2}{c} \cdot v\!\left(\frac{\mu_i - \mu_j}{c}\right)
\end{equation}
\begin{equation}
    \sigma_i^2 \leftarrow \sigma_i^2 \left[1 - \frac{\sigma_i^2}{c^2} \cdot w\!\left(\frac{\mu_i - \mu_j}{c}\right)\right]
\end{equation}
其中 $c = \sqrt{2\beta^2 + \sigma_i^2 + \sigma_j^2}$，而 $v(t) = \phi(t)/\Phi(t)$, $w(t) = v(t)(v(t) + t)$ 是截断高斯校正因子（$\phi$ 和 $\Phi$ 为标准正态的概率密度函数和累积分布函数）。TrueSkill的不确定性估计 $\sigma_i$ 对于识别需要更多评估数据的模型特别有用。

\subsection{Win Rate with Confidence Intervals}
\label{win-rate-with-confidence-intervals}

## 胜率与置信区间
## \label{win-rate-with-confidence-intervals}

The simplest ranking metric is the win rate: the fraction of pairwise comparisons in which model $A$ is preferred. Given $n$ comparisons with $w$ wins, the win rate is $\hat{p} = w/n$. A Wilson score confidence interval~\cite{wilson1927probable} is preferred over the naive Wald interval because it has better coverage near $p = 0$ and $p = 1$: 
\begin{equation}
    \text{CI} = \frac{\hat{p} + \frac{z^2}{2n} \pm z\sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}
\end{equation}
 where $z = 1.96$ for a 95\% interval. For multi-way comparisons, win rate should be computed against a fixed baseline model to ensure comparability.
最简单的排名指标是胜率：模型 $A$ 被偏好的成对比较比例。给定 $n$ 次比较，其中 $w$ 次获胜，胜率为 $\hat{p} = w/n$。Wilson得分置信区间~\cite{wilson1927probable} 优于朴素的Wald区间，因为它在 $p=0$ 和 $p=1$ 附近具有更好的覆盖范围：
\begin{equation}
    \text{CI} = \frac{\hat{p} + \frac{z^2}{2n} \pm z\sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}
\end{equation}
其中 $z = 1.96$ 对应95%置信区间。对于多方比较，胜率应针对固定的基线模型计算，以确保可比性。

\subsection{Chatbot Arena Methodology}
\label{chatbot-arena-methodology}

## Chatbot Arena 方法论
## \label{chatbot-arena-methodology}

Chatbot Arena~\cite{zheng2023judging} combines the above elements into a production-scale evaluation system:
Chatbot Arena~\cite{zheng2023judging} 将上述要素结合成一个生产规模的评估系统：

\begin{enumerate}
  \item Users submit prompts and receive responses from two anonymised models.
  \item Users vote for the preferred response (or declare a tie).
  \item Votes are aggregated using the BT model to produce a leaderboard.
  \item Bootstrap confidence intervals are reported for each model’s score.
  \item Models with overlapping confidence intervals are considered statistically indistinguishable.
\end{enumerate}

\begin{enumerate}
  \item 用户提交提示词，并从两个匿名模型接收响应。
  \item 用户对偏好的响应进行投票（或声明平局）。
  \item 使用BT模型聚合投票，生成排行榜。
  \item 报告每个模型得分的Bootstrap置信区间。
  \item 置信区间重叠的模型被视为统计上不可区分。
\end{enumerate}

As of 2024, Chatbot Arena has collected over one million human preference votes, making it the largest publicly available LLM preference dataset.
截至2024年，Chatbot Arena已收集超过一百万个人类偏好投票，使其成为最大的公开可用LLM偏好数据集。

\section{Metrics for Generation Tasks}
\label{subsec:generation-metrics}

## 生成任务指标
## \label{subsec:generation-metrics}

Generation metrics quantify the quality of model outputs for tasks with reference answers or well-defined correctness criteria.
生成任务指标量化模型在具有参考答案或明确定义的正确性标准的任务中的输出质量。

## BLEU
## BLEU

BLEU (Bilingual Evaluation Understudy)~\cite{papineni2002bleu} measures $n$-gram precision between a hypothesis $h$ and one or more references $\mathcal{R}$:
BLEU（双语评估替补）~\cite{papineni2002bleu} 衡量假设 $h$ 与一个或多个参考 $\mathcal{R}$ 之间的 $n$-gram 精确率：
\begin{equation}
    \text{BLEU} = \text{BP} \cdot \exp\!\left(\sum_{n=1}^{N} w_n \log p_n\right)
\end{equation}
 where $p_n$ is the modified $n$-gram precision, $w_n = 1/N$ are uniform weights, and BP is the brevity penalty:
其中 $p_n$ 是修正的 $n$-gram 精确率，$w_n = 1/N$ 是均匀权重，BP 是简短惩罚：
\begin{equation}
    \text{BP} = \begin{cases} 1 & \text{if } |h| > |r| \\ e^{1 - |r|/|h|} & \text{if } |h| \leq |r| \end{cases}
\end{equation}
 with $|r|$ being the length of the closest reference. Modified $n$-gram precision clips each $n$-gram count to its maximum count in any reference:
其中 $|r|$ 是最近参考的长度。修正的 $n$-gram 精确率将每个 $n$-gram 计数裁剪到它在任何参考中的最大计数：
\begin{equation}
    p_n = \frac{\sum_{\text{ngram} \in h} \min\!\left(\text{count}(\text{ngram}, h),\, \max_{r \in \mathcal{R}} \text{count}(\text{ngram}, r)\right)}{\sum_{\text{ngram} \in h} \text{count}(\text{ngram}, h)}
\end{equation}

\begin{warningbox}[BLEU Limitations]
BLEU Limitations
BLEU was designed for machine translation with multiple references. For open-ended generation with a single reference, BLEU scores are often near zero even for high-quality outputs. BLEU does not capture semantic similarity, penalises valid paraphrases, and is sensitive to tokenisation. Use BLEU only when multiple diverse references are available and the task has low output diversity.
BLEU 的局限性
BLEU 是为多参考的机器翻译设计的。对于只有一个参考的开放式生成，即使输出质量很高，BLEU 分数也常常接近零。BLEU 不能捕获语义相似性，会惩罚有效的释义，并且对分词敏感。仅当有多个多样化的参考且任务输出多样性较低时才使用 BLEU。
\end{warningbox}

## ROUGE
## ROUGE

ROUGE (Recall-Oriented Understudy for Gisting Evaluation)~\cite{lin2004rouge} is a family of recall-oriented metrics designed for summarisation:
ROUGE（面向召回率的摘要评估替补）~\cite{lin2004rouge} 是一组面向召回率的度量，专为摘要而设计：
\begin{align}
    \text{ROUGE-N} &= \frac{\sum_{r \in \mathcal{R}} \sum_{\text{ngram} \in r} \min(\text{count}(\text{ngram}, h), \text{count}(\text{ngram}, r))}{\sum_{r \in \mathcal{R}} \sum_{\text{ngram} \in r} \text{count}(\text{ngram}, r)} \\[6pt]
    \text{ROUGE-L} &= \frac{\text{LCS}(h, r)}{|r|}
\end{align}
 where LCS denotes the longest common subsequence. ROUGE-1 and ROUGE-2 measure unigram and bigram recall; ROUGE-L captures sentence-level structure. The F-measure variant balances precision and recall:
其中 LCS 表示最长公共子序列。ROUGE-1 和 ROUGE-2 衡量一元和二元召回率；ROUGE-L 捕获句子级结构。F 度量变体平衡精确率和召回率：
\begin{equation}
    \text{ROUGE-N}_F = \frac{(1+\beta^2) \cdot P \cdot R}{\beta^2 P + R}
\end{equation}
 with $\beta = 1$ for equal weighting.
其中 $\beta = 1$ 表示等权重。

## BERTScore
## BERTScore

BERTScore~\cite{zhang2020bertscore} computes token-level similarity using contextual embeddings from a pre-trained BERT model. Given hypothesis tokens $\hat{\mathbf{x}} = \langle \hat{x}_1, \ldots, \hat{x}_m \rangle$ and reference tokens $\mathbf{x} = \langle x_1, \ldots, x_n \rangle$ with embeddings $\hat{\mathbf{e}}_i$ and $\mathbf{e}_j$:
BERTScore~\cite{zhang2020bertscore} 使用预训练 BERT 模型的上下文嵌入计算词元级相似度。给定假设词元 $\hat{\mathbf{x}} = \langle \hat{x}_1, \ldots, \hat{x}_m \rangle$ 和参考词元 $\mathbf{x} = \langle x_1, \ldots, x_n \rangle$，其嵌入分别为 $\hat{\mathbf{e}}_i$ 和 $\mathbf{e}_j$：
\begin{align}
    R_{\text{BERT}} &= \frac{1}{|x|} \sum_{x_j \in \mathbf{x}} \max_{\hat{x}_i \in \hat{\mathbf{x}}} \frac{\hat{\mathbf{e}}_i^\top \mathbf{e}_j}{\|\hat{\mathbf{e}}_i\| \|\mathbf{e}_j\|} \\[4pt]
    P_{\text{BERT}} &= \frac{1}{|\hat{x}|} \sum_{\hat{x}_i \in \hat{\mathbf{x}}} \max_{x_j \in \mathbf{x}} \frac{\hat{\mathbf{e}}_i^\top \mathbf{e}_j}{\|\hat{\mathbf{e}}_i\| \|\mathbf{e}_j\|} \\[4pt]
    F_{\text{BERT}} &= 2 \cdot \frac{P_{\text{BERT}} \cdot R_{\text{BERT}}}{P_{\text{BERT}} + R_{\text{BERT}}}
\end{align}

BERTScore correlates better with human judgments than BLEU and ROUGE, particularly for paraphrases and semantically equivalent but lexically different outputs. Importance weighting using inverse document frequency (IDF) further improves correlation:
BERTScore 与人类判断的相关性优于 BLEU 和 ROUGE，尤其是对于释义和语义等价但词汇不同的输出。使用逆文档频率（IDF）进行重要性加权进一步提高了相关性：
\begin{equation}
    R_{\text{BERT}}^{\text{idf}} = \frac{\sum_{x_j \in \mathbf{x}} \text{idf}(x_j) \max_{\hat{x}_i} \cos(\hat{\mathbf{e}}_i, \mathbf{e}_j)}{\sum_{x_j \in \mathbf{x}} \text{idf}(x_j)}
\end{equation}

## METEOR
## METEOR

METEOR~\cite{banerjee2005meteor} addresses BLEU’s recall blindness by computing an F-score over unigram matches, with additional modules for stemming and synonym matching:
METEOR~\cite{banerjee2005meteor} 通过计算一元匹配的 F 分数来解决 BLEU 的召回率盲区，并附加了词干提取和同义词匹配模块：
\begin{equation}
    \text{METEOR} = F_{\text{mean}} \cdot (1 - \text{Pen})
\end{equation}
 where $F_{\text{mean}} = \frac{10PR}{R + 9P}$ (recall-weighted harmonic mean) and the fragmentation penalty $\text{Pen} = 0.5 \cdot (c/u_m)^3$ penalises non-contiguous matches ($c$ = number of chunks, $u_m$ = number of matched unigrams).
其中 $F_{\text{mean}} = \frac{10PR}{R + 9P}$（召回率加权调和平均），碎片惩罚 $\text{Pen} = 0.5 \cdot (c/u_m)^3$ 惩罚非连续匹配（$c$ = 块数，$u_m$ = 匹配的一元数量）。

## Perplexity
## 困惑度

Perplexity measures how well a language model predicts a held-out text sequence $w_1, w_2, \ldots, w_T$:
困惑度衡量语言模型预测一个保留文本序列 $w_1, w_2, \ldots, w_T$ 的效果：
\begin{equation}
    \text{PPL}(w_{1:T}) = \exp\!\left(-\frac{1}{T}\sum_{t=1}^{T} \log P_\theta(w_t \mid w_{1:t-1})\right)
\end{equation}

Lower perplexity indicates better predictive performance. Perplexity is useful for comparing models on the same tokenisation and test set, but is not directly comparable across models with different vocabularies or tokenisers. For evaluation purposes, perplexity is most useful as a sanity check and for detecting distribution shift.
较低的困惑度表示更好的预测性能。困惑度适用于在相同分词和测试集上比较模型，但对于具有不同词汇表或分词器的模型不能直接比较。在评估中，困惑度最常用作合理性检查以及检测分布漂移。

## Pass@k for Code
## 代码的 Pass@k

For code generation, functional correctness is measured by executing generated code against test cases. The pass@$k$ metric~\cite{chen2021evaluating} estimates the probability that at least one of $k$ generated samples passes all tests:
对于代码生成，功能正确性是通过对测试用例执行生成的代码来衡量的。pass@$k$ 度量~\cite{chen2021evaluating} 估计 $k$ 个生成样本中至少有一个通过所有测试的概率：
\begin{equation}
    \text{pass@}k = \mathbb{E}_{\text{problems}}\!\left[1 - \frac{\binom{n-c}{k}}{\binom{n}{k}}\right]
\end{equation}
 where $n$ is the total number of samples generated per problem and $c$ is the number that pass. This unbiased estimator avoids the high variance of the naive estimator (which samples exactly $k$ solutions and checks if any pass). In practice, $n = 200$ samples are generated and pass@1, pass@10, pass@100 are reported.
其中 $n$ 是每个问题生成的样本总数，$c$ 是通过的样本数。这个无偏估计避免了朴素估计器（即正好采样 $k$ 个解并检查是否有任何通过）的高方差。实践中，生成 $n = 200$ 个样本，并报告 pass@1、pass@10 和 pass@100。

\begin{examplebox}[Pass@k Computation]
Pass@k 计算
\begin{lstlisting}[style=pythonstyle]
import numpy as np
from scipy.special import comb


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased estimator for pass@k.
    无偏的 pass@k 估计器。
    
    Args:
        n: total samples generated per problem
        n: 每个问题生成的样本总数
        c: number of samples that pass all tests
        c: 通过所有测试的样本数
        k: number of samples to consider
        k: 要考虑的样本数
    """
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k, exact=True) / comb(n, k, exact=True)


# Example: 200 samples, 15 pass, compute pass@1, pass@10, pass@100
# 示例：200 个样本，15 个通过，计算 pass@1, pass@10, pass@100
for k in [1, 10, 100]:
    score = pass_at_k(n=200, c=15, k=k)
    print(f"pass@{k}: {score:.4f}")
# pass@1:   0.0750
# pass@10:  0.5391
# pass@100: 0.9999
\end{lstlisting}
\end{examplebox}

## Exact Match and F1
## 精确匹配和 F1

For extractive question answering (e.g., SQuAD), two standard metrics are:
对于抽取式问答（例如 SQuAD），有两个标准度量：

\begin{itemize}
  \item \textbf{Exact Match (EM):} Binary indicator of whether the predicted answer string exactly matches any gold answer after normalisation (lowercasing, removing articles and punctuation).
  \item \textbf{Exact Match (EM)：} 预测答案字符串在归一化（小写化、去除冠词和标点）后是否与任何标准答案完全匹配的二进制指示。
  \item \textbf{Token-level F1:} Treats prediction and gold answer as bags of tokens and computes the F1 score:
  \item \textbf{词元级 F1：} 将预测和标准答案视为词元袋，并计算 F1 分数：
\begin{equation}
        F1 = \frac{2 \cdot |\text{pred} \cap \text{gold}|}{|\text{pred}| + |\text{gold}|}
\end{equation}
\end{itemize}

For multi-answer settings, the maximum F1 over all gold answers is reported.
对于多答案设置，报告所有标准答案中的最大 F1。

\begin{table}[ht!]
\centering
\caption{Summary of generation metrics: applicability and key properties.}
\caption{生成度量概览：适用性和关键属性。}
\begin{tabular}{@{}lp{3.5cm}p{3.5cm}p{6cm}@{}}
\toprule
\textbf{Metric} & \textbf{Task} & \textbf{Reference-free?} & \textbf{Human correlation} \\
\textbf{度量} & \textbf{任务} & \textbf{无需参考？} & \textbf{与人类的相关性} \\
\midrule
BLEU & Translation & No & Low--Medium \\
BLEU & 翻译 & 否 & 低--中 \\
ROUGE & Summarisation & No & Medium \\
ROUGE & 摘要 & 否 & 中 \\
BERTScore & General NLG & No & High \\
BERTScore & 通用 NLG & 否 & 高 \\
METEOR & Translation & No & Medium--High \\
METEOR & 翻译 & 否 & 中--高 \\
Perplexity & LM quality & Yes & Low \\
困惑度 & 语言模型质量 & 是 & 低 \\
Pass@k & Code generation & No (tests) & Very high \\
Pass@k & 代码生成 & 否（有测试） & 非常高 \\
Exact Match & Extractive QA & No & Very high \\
精确匹配 & 抽取式问答 & 否 & 非常高 \\
Token F1 & Extractive QA & No & High \\
词元 F1 & 抽取式问答 & 否 & 高 \\
\bottomrule
\end{tabular}
\end{table}

## Metrics for Agentic Tasks
## 智能体任务的度量

Agentic LLMs operate in environments, take sequences of actions, and must complete multi-step tasks. Standard generation metrics are insufficient; agentic evaluation requires metrics that capture task completion, efficiency, and the quality of intermediate steps.
智能体 LLM 在环境中运行，采取一系列行动，并且必须完成多步骤任务。标准的生成度量是不够的；智能体评估需要能够捕获任务完成度、效率以及中间步骤质量的度量。

## Task Success Rate
## 任务成功率

The primary metric for agentic tasks is the task success rate (TSR): the fraction of tasks for which the agent achieves the specified goal state: 
智能体任务的主要指标是任务成功率 (TSR)：智能体达成指定目标状态的任务占比：
\begin{equation}
    \text{TSR} = \frac{1}{|\mathcal{T}|} \sum_{\tau \in \mathcal{T}} \mathbf{1}[\text{goal}(\tau) \text{ achieved}]
\end{equation}

Goal achievement is typically verified by a deterministic oracle (e.g., checking database state, file system state, or test case execution). For tasks with partial credit, a graded success metric can be defined: 
目标达成通常由确定性验证器（oracle）验证（例如检查数据库状态、文件系统状态或测试用例执行）。对于可以部分得分的任务，可以定义分级成功率指标：
\begin{equation}
    \text{TSR}_{\text{graded}} = \frac{1}{|\mathcal{T}|} \sum_{\tau \in \mathcal{T}} \text{score}(\tau) \in [0, 1]
\end{equation}

## Trajectory Efficiency
## 轨迹效率

A successful agent should complete tasks with minimal unnecessary actions. Trajectory efficiency measures the ratio of the optimal trajectory length to the agent’s actual trajectory length: 
一个成功的智能体应该以最少的无关动作完成任务。轨迹效率衡量的是最优轨迹长度与智能体实际轨迹长度的比值：
\begin{equation}
    \eta = \frac{L^*}{L_{\text{agent}}}
\end{equation}
 where $L^*$ is the length of the shortest successful trajectory (computed by an oracle or human expert) and $L_{\text{agent}}$ is the number of actions taken by the agent. $\eta \in (0, 1]$ with $\eta = 1$ indicating optimal efficiency. For failed trajectories, $\eta = 0$.
其中 $L^*$ 是最短成功轨迹的长度（由验证器或人类专家计算得出），$L_{\text{agent}}$ 是智能体执行的动作数量。$\eta \in (0, 1]$，$\eta = 1$ 表示最优效率。对于失败的轨迹，$\eta = 0$。

A complementary metric is the \emph{redundancy rate}: the fraction of agent actions that are not present in any optimal trajectory.
一个互补的指标是 \emph{冗余率 (redundancy rate)}：智能体动作中未出现在任何最优轨迹中的比例。

## Tool-Use Accuracy
## 工具使用准确率

For agents that invoke external tools (APIs, code interpreters, search engines), tool-use accuracy measures the correctness of tool calls: 
对于调用外部工具（API、代码解释器、搜索引擎）的智能体，工具使用准确率衡量的是工具调用的正确性：
\begin{equation}
    \text{TUA} = \frac{\text{\# correct tool calls}}{\text{\# total tool calls}}
\end{equation}
 A tool call is correct if (a) the correct tool is selected, (b) the arguments are valid, and (c) the call is made at the appropriate point in the trajectory. Partial credit can be assigned for correct tool selection with incorrect arguments.
一个工具调用被认为是正确的，如果：(a) 选择了正确的工具，(b) 参数有效，(c) 调用发生在轨迹中的适当位置。对于工具选择正确但参数错误的情况，可以给予部分分数。

## Multi-Step Reasoning Accuracy
## 多步推理准确率

For tasks requiring chains of reasoning (e.g., multi-hop QA, mathematical problem solving), step-level accuracy measures the fraction of reasoning steps that are correct: 
对于需要推理链的任务（例如多跳问答、数学问题求解），步骤级准确率衡量的是正确推理步骤的占比：
\begin{equation}
    \text{SRA} = \frac{1}{|\mathcal{T}|} \sum_{\tau \in \mathcal{T}} \frac{1}{|S_\tau|} \sum_{s \in S_\tau} \mathbf{1}[s \text{ is correct}]
\end{equation}
 where $S_\tau$ is the set of reasoning steps in trajectory $\tau$. Step correctness can be verified by a process reward model (PRM) or by human annotation.
其中 $S_\tau$ 是轨迹 $\tau$ 中推理步骤的集合。步骤正确性可以通过过程奖励模型（PRM）或人工标注来验证。

## SWE-bench Methodology
## SWE-bench 方法论

SWE-bench~\cite{jimenez2024swebench} evaluates LLMs on real-world software engineering tasks: given a GitHub issue description and the repository codebase, the model must generate a patch that resolves the issue. Evaluation proceeds as follows:
SWE-bench~\cite{jimenez2024swebench} 在真实世界的软件工程任务上评估 LLM：给定一个 GitHub 问题描述和仓库代码库，模型必须生成一个补丁来解决问题。评估过程如下：

\begin{enumerate}
  \item The model is given the issue description and relevant code context.
  \item 模型获得问题描述和相关代码上下文。
  \item The model generates a patch (unified diff format).
  \item 模型生成补丁（统一差异格式）。
  \item The patch is applied to the repository.
  \item 补丁被应用到仓库。
  \item The repository’s test suite is executed; the task is successful if all tests pass.
  \item 执行仓库的测试套件；如果所有测试通过，则任务成功。
\end{enumerate}

The primary metric is \textbf{\% Resolved}: the fraction of issues for which the generated patch passes all tests. SWE-bench Verified is a curated subset of 500 problems verified by human annotators to be solvable and unambiguous. SWE-bench Lite is a 300-problem subset designed for faster evaluation.
主要指标是 \textbf{\% 已解决 (\% Resolved)}：生成的补丁通过所有测试的问题占比。SWE-bench Verified 是一个精选子集，包含 500 个由人工标注者验证为可解且无歧义的问题。SWE-bench Lite 是一个包含 300 个问题的子集，旨在加快评估速度。

\begin{keybox}[SWE-bench Key Statistics (as of 2024)]
\begin{itemize}
  \item \textbf{Full benchmark:} 2,294 tasks from 12 popular Python repositories.
  \item \textbf{完整基准:} 来自 12 个流行 Python 仓库的 2,294 个任务。
  \item \textbf{Best open-source agent:} $\sim$43\% resolved (SWE-bench Verified).
  \item \textbf{最佳开源智能体:} $\sim$43\% 已解决 (SWE-bench Verified)。
  \item \textbf{Human performance:} $\sim$87\% resolved (with 15 minutes per task).
  \item \textbf{人类表现:} $\sim$87\% 已解决（每任务 15 分钟）。
  \item \textbf{Evaluation cost:} $\sim$\$0.25 per task for API-based models.
  \item \textbf{评估成本:} 基于 API 的模型约 $\sim$\$0.25 每任务。
\end{itemize}
\end{keybox}

## WebArena Methodology
## WebArena 方法论

WebArena~\cite{zhou2024webarena} evaluates agents on realistic web navigation tasks in a sandboxed browser environment. The benchmark includes 812 tasks across five web applications (e-commerce, social forum, collaborative development, content management, and maps). Evaluation:
WebArena~\cite{zhou2024webarena} 在沙盒浏览器环境中评估智能体在真实网页导航任务上的表现。该基准包含 812 个任务，涵盖五个网页应用（电子商务、社交论坛、协作开发、内容管理和地图）。评估方法：

\begin{itemize}
  \item \textbf{Functional evaluation:} The task outcome is verified by checking the application state (e.g., ``Was the item added to the cart?'', ``Was the post created?'').
  \item \textbf{功能评估:} 通过检查应用状态来验证任务结果（例如，“物品是否添加到购物车？”，“帖子是否已创建？”）。
  \item \textbf{URL-based evaluation:} For navigation tasks, the final URL is compared to the expected URL.
  \item \textbf{基于 URL 的评估:} 对于导航任务，将最终 URL 与预期 URL 进行比较。
  \item \textbf{Program-based evaluation:} A custom evaluator script checks complex conditions (e.g., ``Is the price less than \$50?'').
  \item \textbf{基于程序的评估:} 自定义评估脚本检查复杂条件（例如，“价格是否低于 \$50？”）。
\end{itemize}

The primary metric is task success rate. Human performance is approximately 78\%; state-of-the-art agents achieve approximately 35--45\%.
主要指标是任务成功率。人类表现约为 78%；最先进的智能体达到约 35–45%。

\begin{table}[ht!]
\centering
\caption{Comparison of agentic evaluation benchmarks.}
\caption{智能体评估基准比较。}
\begin{tabular}{@{}lp{3cm}p{3.2cm}p{3.2cm}p{3.5cm}@{}}
\toprule
\textbf{Benchmark} & \textbf{Domain} & \textbf{\# Tasks} & \textbf{Eval Method} & \textbf{SOTA (\%)} \\
\textbf{基准} & \textbf{领域} & \textbf{任务数} & \textbf{评估方法} & \textbf{最佳表现 (\%)} \\
\midrule
SWE-bench & Software engineering & 2,294 & Test execution & $\sim$43 \\
SWE-bench & 软件工程 & 2,294 & 测试执行 & $\sim$43 \\
SWE-bench Lite & Software engineering & 300 & Test execution & $\sim$50 \\
SWE-bench Lite & 软件工程 & 300 & 测试执行 & $\sim$50 \\
WebArena & Web navigation & 812 & State/URL/program & $\sim$40 \\
WebArena & 网页导航 & 812 & 状态/URL/程序 & $\sim$40 \\
ALFWorld~\cite{shridhar2021alfworld} & Household tasks & 3,553 & Simulator state & $\sim$90 \\
ALFWorld~\cite{shridhar2021alfworld} & 家庭任务 & 3,553 & 模拟器状态 & $\sim$90 \\
AgentBench~\cite{liu2023agentbench} & Multi-domain & 1,091 & Task-specific & $\sim$45 \\
AgentBench~\cite{liu2023agentbench} & 多领域 & 1,091 & 任务特定 & $\sim$45 \\
\bottomrule
\end{tabular}
\end{table}

## LLM-as-Judge
## LLM 作为评判者 (LLM-as-Judge)

LLM-as-judge~\cite{zheng2023judging} uses a capable LLM to evaluate the outputs of other (or the same) LLMs. This approach scales to large evaluation sets without human annotation and can provide detailed rationales for its judgments.
LLM 作为评判者~\cite{zheng2023judging} 使用一个能力较强的 LLM 来评估其他（或同一）LLM 的输出。这种方法可以扩展到大型评估集而无需人工标注，并且能够为其判断提供详细的理由。

## Setup and Prompt Templates
## 设置与提示模板

The judge is presented with a prompt, one or more model responses, and an evaluation rubric. Three common formats:
评判者会收到一个提示、一个或多个模型响应以及一个评估标准。三种常见格式：

### Pointwise scoring.
### 逐点评分 (Pointwise scoring)

The judge assigns an absolute score to a single response:
评判者给单个响应分配一个绝对分数：

\begin{examplebox}[Pointwise Judge Prompt]
\begin{lstlisting}[style=pythonstyle]
POINTWISE_PROMPT = """
You are an expert evaluator. Rate the following response on a scale 
of 1-10 for helpfulness, accuracy, and clarity.


[Question]
{question}


[Response]
{response}


Provide your evaluation in the following format:
Reasoning: <step-by-step analysis>
Score: <integer from 1 to 10>
"""
\end{lstlisting}
\end{examplebox}

### Pairwise comparison.
### 逐对比较 (Pairwise comparison)

The judge compares two responses and selects the better one:
评判者比较两个响应并选择更好的一个：

\begin{examplebox}[Pairwise Judge Prompt]
\begin{lstlisting}[style=pythonstyle]
PAIRWISE_PROMPT = """
You are an expert evaluator. Compare the two responses below and 
determine which is better. Consider helpfulness, accuracy, and 
depth of explanation.


[Question]
{question}


[Response A]
{response_a}


[Response B]
{response_b}


Output exactly one of: [[A]], [[B]], or [[C]] (tie).
Reasoning: <your analysis>
Verdict: <[[A]], [[B]], or [[C]]>
"""
\end{lstlisting}
\end{examplebox}

### Reference-guided scoring.
### 参考引导评分 (Reference-guided scoring)

The judge is provided with a reference answer and rates the response relative to it. This is particularly useful for factual tasks where the judge may not have reliable knowledge.
评判者会获得一个参考答案，并据此对响应进行评分。这对于评判者可能缺乏可靠知识的事实性任务尤其有用。

## Position Bias Mitigation
## 位置偏差缓解 (Position Bias Mitigation)

LLM judges exhibit \emph{position bias}: a systematic preference for the response appearing in a particular position (first or last). This bias can be as large as 10--15 percentage points. Mitigation strategies:
LLM 评判者表现出 \emph{位置偏差 (position bias)}：对出现在特定位置（第一个或最后一个）的响应有系统性偏好。这种偏差可能高达 10–15 个百分点。缓解策略：

```markdown
\begin{enumerate}
  \item \textbf{Swap augmentation:} Evaluate each pair in both orders (A vs.~B and B vs.~A). A consistent judgment is accepted; an inconsistent judgment is recorded as a tie.
  \item \textbf{交换增强：} 以两种顺序（A 对 B 和 B 对 A）评估每一对。一致的判断被接受；不一致的判断记为平局。
  \item \textbf{Calibration prompting:} Explicitly instruct the judge: ``Your evaluation should not be influenced by the order in which the responses are presented.''
  \item \textbf{校准提示：} 明确指示评估者：“你的评估不应受回复呈现顺序的影响。”
  \item \textbf{Ensemble judging:} Use multiple judges with different position orderings and aggregate their verdicts.
  \item \textbf{集成评判：} 使用多个具有不同位置顺序的评估者，并汇总他们的裁决。
  \item \textbf{Chain-of-thought forcing:} Require the judge to produce a detailed rationale before the verdict, which reduces reliance on superficial positional cues.
  \item \textbf{思维链强制：} 要求评估者在做出裁决前给出详细理由，从而减少对表面位置线索的依赖。
\end{enumerate}

\begin{warningbox}[Verbosity Bias]
LLM judges also exhibit verbosity bias: longer responses are systematically preferred, even when the additional content is irrelevant or repetitive. To mitigate this, instruct the judge to penalise unnecessary length and to focus on the quality of information rather than quantity. Alternatively, truncate responses to a fixed length before judging.
\end{warningbox}
\begin{warningbox}[冗长偏差]
LLM 评估者还表现出冗长偏差：系统性地偏好较长的回复，即使额外内容不相关或重复。为缓解此问题，应指示评估者惩罚不必要的长度，并关注信息质量而非数量。另一种方法是在评判前将回复截断为固定长度。
\end{warningbox}

\subsection{Multi-Judge Panels}
\label{multi-judge-panels}
\subsection{多评估者面板}
\label{multi-judge-panels}

A single judge may have systematic biases. A panel of judges from different model families provides more robust evaluations. Given $J$ judges with verdicts $v_1, \ldots, v_J \in \{A, B, \text{tie}\}$, the panel verdict is determined by majority vote. The panel agreement rate is: 
\begin{equation}
    \text{Agreement} = \frac{1}{\binom{J}{2}} \sum_{i < j} \mathbf{1}[v_i = v_j]
\end{equation}
单一评估者可能存在系统偏差。由来自不同模型家族的评估者组成的小组能提供更稳健的评估。给定 $J$ 个评估者及其裁决 $v_1, \ldots, v_J \in \{A, B, \text{tie}\}$，小组裁决由多数投票决定。小组一致率为：
\begin{equation}
    \text{Agreement} = \frac{1}{\binom{J}{2}} \sum_{i < j} \mathbf{1}[v_i = v_j]
\end{equation}

For a three-judge panel, a unanimous verdict (all three agree) is treated as high-confidence; a 2--1 split as medium-confidence; and a three-way tie as low-confidence.
对于三人评估小组，一致裁决（三人均同意）被视为高置信度；2-1 分歧视为中等置信度；三向平局视为低置信度。

\subsection{Agreement Metrics for LLM Judges}
\label{agreement-metrics-for-llm-judges}
\subsection{LLM 评估者的一致性指标}
\label{agreement-metrics-for-llm-judges}

To validate an LLM judge, its verdicts are compared to human annotations on a held-out set. Key metrics:
为验证一个 LLM 评估者，将其裁决与预留集上的人工标注进行比较。关键指标：

\begin{itemize}
  \item \textbf{Agreement rate:} Fraction of items where judge and human agree.
  \item \textbf{一致率：} 评估者与人工一致的样本比例。
  \item \textbf{Cohen’s $\kappa$:} Chance-corrected agreement (Equation~\ref{eq:cohens-kappa}).
  \item \textbf{Cohen's $\kappa$：} 去除了偶然因素的一致性（公式~\ref{eq:cohens-kappa}）。
  \item \textbf{Spearman’s $\rho$:} Rank correlation between judge scores and human scores, appropriate for ordinal ratings.
  \item \textbf{Spearman's $\rho$：} 评估者分数与人工分数之间的秩次相关性，适用于有序评分。
  \item \textbf{Kendall’s $\tau$:} Alternative rank correlation that is more robust to ties.
  \item \textbf{Kendall's $\tau$：} 另一种秩次相关性，对平局更稳健。
\end{itemize}

A judge is considered reliable if it achieves $\kappa > 0.6$ and agreement rate $> 80\%$ with human annotators on a representative sample.
如果一个评估者在代表性样本上与人工标注者达到 $\kappa > 0.6$ 且一致率 $> 80\%$，则被认为是可靠的。

\subsection{G-Eval Framework}
\label{g-eval-framework}
\subsection{G-Eval 框架}
\label{g-eval-framework}

G-Eval~\cite{liu2023geval} is a structured framework for LLM-based evaluation that uses chain-of-thought prompting and token probability weighting to produce more reliable scores. The framework:
G-Eval~\cite{liu2023geval} 是一个用于基于 LLM 评估的结构化框架，它使用思维链提示和标记概率加权来产生更可靠的分数。该框架：

\begin{enumerate}
  \item \textbf{Generate evaluation steps:} Prompt the LLM to generate a detailed rubric for the evaluation task (e.g., ``List the steps you would take to evaluate the coherence of a summary'').
  \item \textbf{生成评估步骤：} 提示 LLM 生成评估任务的详细评分准则（例如，“列出你将采取哪些步骤来评估摘要的连贯性”）。
  \item \textbf{Score with probability weighting:} For each score value $s \in \{1, 2, 3, 4, 5\}$, obtain the log-probability $\log P_\theta(s \mid \text{prompt, steps, response})$ from the judge model. The final score is the probability-weighted average: 
\begin{equation}
        \text{G-Eval score} = \sum_{s=1}^{5} s \cdot \frac{e^{\log P_\theta(s)}}{\sum_{s'=1}^{5} e^{\log P_\theta(s')}}
\end{equation}
  \item \textbf{用概率加权评分：} 对于每个分数值 $s \in \{1, 2, 3, 4, 5\}$，从评估者模型获取对数概率 $\log P_\theta(s \mid \text{prompt, steps, response})$。最终分数是概率加权平均值：
\begin{equation}
        \text{G-Eval 分数} = \sum_{s=1}^{5} s \cdot \frac{e^{\log P_\theta(s)}}{\sum_{s'=1}^{5} e^{\log P_\theta(s')}}
\end{equation}
  \item \textbf{Normalise:} Map the score to $[0, 1]$ by dividing by the maximum score.
  \item \textbf{归一化：} 将分数除以最大值，映射到 $[0, 1]$ 区间。
\end{enumerate}

G-Eval achieves higher correlation with human judgments than direct prompting, particularly for nuanced dimensions like coherence and consistency, because the probability weighting captures the judge’s uncertainty rather than forcing a discrete choice.
G-Eval 在与人评判的相关性上优于直接提示，尤其是在连贯性和一致性等细致维度上，因为概率加权捕捉了评估者的不确定性，而非强制进行离散选择。

\begin{intuitionbox}[Why G-Eval Works]
Standard prompting asks the judge to output a single token (e.g., ``4''), which discards the model’s uncertainty. G-Eval reads the probability distribution over all score tokens, effectively computing the expected score under the judge’s belief. This is analogous to using the mean of a posterior distribution rather than the mode.
\end{intuitionbox}
\begin{intuitionbox}[G-Eval 为何有效]
标准提示要求评估者输出单个标记（例如“4”），这丢弃了模型的不确定性。G-Eval 读取所有分数标记上的概率分布，有效计算了评估者信念下的期望分数。这类似于使用后验分布的均值而非众数。
\end{intuitionbox}

\section{Evaluation Pitfalls}
\label{subsec:eval-pitfalls}
\section{评估陷阱}
\label{subsec:eval-pitfalls}

Even carefully designed evaluation pipelines can produce misleading results. This section catalogues the most common failure modes.
即使精心设计的评估流水线也可能产生误导性结果。本节列举了最常见的失败模式。

\subsection{Benchmark Contamination}
\label{benchmark-contamination}
\subsection{基准污染}
\label{benchmark-contamination}

Benchmark contamination occurs when evaluation data appears in the model’s training set, either directly (verbatim inclusion) or indirectly (paraphrased or semantically similar content). Contaminated models achieve inflated scores that do not reflect true generalisation ability.
当评估数据出现在模型的训练集中时，就会发生基准污染，可能是直接（逐字包含）或间接（释义或语义相似的内容）。受污染的模型会获得虚高的分数，这些分数并不反映真正的泛化能力。

\paragraph{Detection methods:}
\label{detection-methods}
\paragraph{检测方法：}
\label{detection-methods}

\begin{itemize}
  \item \textbf{$n$-gram overlap:} Compute the fraction of evaluation examples with high $n$-gram overlap (e.g., ROUGE-L $> 0.8$) with the training corpus.
  \item \textbf{$n$-gram 重叠：} 计算与训练语料库具有高 $n$-gram 重叠（例如 ROUGE-L $> 0.8$）的评估样例的比例。
  \item \textbf{Membership inference:} Use a membership inference attack to estimate the probability that each evaluation example was in the training set.
  \item \textbf{成员推断：} 使用成员推断攻击来估计每个评估样例在训练集中的概率。
  \item \textbf{Canary strings:} Embed unique, randomly generated strings in evaluation examples and check if the model can complete them.
  \item \textbf{金丝雀字符串：} 在评估样例中嵌入唯一的随机生成字符串，并检查模型是否能完成它们。
  \item \textbf{Temporal holdout:} Use evaluation data created after the model’s training cutoff date.
  \item \textbf{时间预留：} 使用在模型训练截止日期之后创建的评估数据。
\end{itemize}

\paragraph{Mitigation:}
\label{mitigation}
\paragraph{缓解措施：}
\label{mitigation}

\begin{itemize}
  \item Maintain a private test set that is never released publicly.
  \item 维护一个从未公开的私有测试集。
  \item Regularly refresh benchmarks with new examples.
  \item 定期用新样例更新基准。
  \item Report training data cutoff dates and decontamination procedures.
  \item 报告训练数据截止日期和去污染流程。
\end{itemize}

\subsection{Overfitting to Benchmarks}
\label{overfitting-to-benchmarks}
\subsection{对基准过拟合}
\label{overfitting-to-benchmarks}

Even without direct contamination, models can be implicitly optimised for specific benchmarks through repeated evaluation and hyperparameter tuning. This is a form of \emph{adaptive overfitting}: the benchmark leaks information into model development decisions.
即使没有直接污染，模型也可能通过反复评估和超参数调优隐式地针对特定基准进行优化。这是一种 \emph{适应性过拟合}：基准将信息泄漏到模型开发决策中。

\begin{warningbox}[The Benchmark Lifecycle]
A benchmark’s utility degrades over time as the research community optimises for it. MMLU~\cite{hendrycks2021measuring}, once a challenging test of world knowledge, now has models achieving near-human performance, yet these models still fail on novel knowledge tasks. New benchmarks should be treated as temporary signal sources, not permanent ground truth.
\end{warningbox}
\begin{warningbox}[基准生命周期]
随着研究社区针对某一基准进行优化，其效用会随时间下降。MMLU~\cite{hendrycks2021measuring} 曾是世界知识的一项挑战性测试，如今已有模型达到接近人类的表现，但这些模型在新颖的知识任务中仍然失败。新基准应被视为临时信号源，而非永久性的地面真实。
\end{warningbox}

\subsection{Goodhart’s Law in Evaluation}
\label{goodharts-law-in-evaluation}
\subsection{评估中的古德哈特定律}
\label{goodharts-law-in-evaluation}

Goodhart’s Law states: \emph{``When a measure becomes a target, it ceases to be a good measure.''}~\cite{goodhart1984problems} In LLM evaluation, this manifests in several ways:
古德哈特定律指出：\emph{“当一个指标成为目标时，它就不再是一个好指标。”}~\cite{goodhart1984problems} 在 LLM 评估中，这体现在以下几个方面：

\begin{itemize}
  \item \textbf{Reward hacking:} Models trained with RLHF learn to exploit the reward model rather than genuinely improving. A model may learn to produce verbose, confident-sounding responses that score highly on the reward model but are factually incorrect.
  \item \textbf{奖励漏洞：} 使用 RLHF 训练的模型学会利用奖励模型而非真正改进。模型可能学会生成冗长、听起来自信的回复，这些回复在奖励模型上得分很高，但事实上是错误的。
  \item \textbf{Metric gaming:} Models fine-tuned to maximise BLEU or ROUGE may produce outputs that score well on these metrics but are less useful to humans.
  \item \textbf{指标投机：} 为最大化 BLEU 或 ROUGE 而微调的模型可能产生在这些指标上得分高但对人类用处不大的输出。
  \item \textbf{Judge gaming:} Models trained with LLM-as-judge feedback may learn the judge’s biases (e.g., verbosity bias) rather than genuinely improving quality.
  \item \textbf{评估者投机：} 使用 LLM 作为评估者反馈训练的模型可能学会评估者的偏见（例如冗长偏差），而非真正改进质量。
\end{itemize}

\begin{keybox}[Defences Against Goodhart’s Law]
\begin{enumerate}
  \item \textbf{Metric diversity:} Use multiple metrics from different families; a model that games one metric will likely not game all simultaneously.
  \item \textbf{指标多样性：} 使用来自不同家族的多个指标；能投机一个指标的模型不太可能同时投机所有指标。
  \item \textbf{Held-out evaluation:} Maintain evaluation metrics that are not used in training or model selection.
  \item \textbf{预留评估：} 维护在训练或模型选择中未使用的评估指标。
  \item \textbf{Human spot-checks:} Regularly sample model outputs for human review, independent of automated metrics.
  \item \textbf{人工抽查：} 定期抽取模型输出进行人工审查，独立于自动化指标。
  \item \textbf{Adversarial evaluation:} Actively probe for failure modes that automated metrics miss.
  \item \textbf{对抗性评估：} 主动探测自动化指标遗漏的失败模式。
  \item \textbf{Extrinsic validation:} Periodically validate intrinsic metrics against extrinsic outcomes.
  \item \textbf{外部验证：} 定期针对外部结果验证内部指标。
\end{enumerate}
\end{keybox}
\begin{keybox}[对抗古德哈特定律的防御措施]
\begin{enumerate}
  \item \textbf{指标多样性：} 使用来自不同家族的多个指标；能投机一个指标的模型不太可能同时投机所有指标。
  \item \textbf{预留评估：} 维护在训练或模型选择中未使用的评估指标。
  \item \textbf{人工抽查：} 定期抽取模型输出进行人工审查，独立于自动化指标。
  \item \textbf{对抗性评估：} 主动探测自动化指标遗漏的失败模式。
  \item \textbf{外部验证：} 定期针对外部结果验证内部指标。
\end{enumerate}
\end{keybox}

\subsection{Additional Pitfalls}
\label{additional-pitfalls}
\subsection{其他陷阱}
\label{additional-pitfalls}

（此处原英文内容为空，故不输出翻译）
```

\paragraph{Prompt sensitivity.}
\label{prompt-sensitivity.}

LLM performance can vary dramatically with small changes to the evaluation prompt (e.g., adding ``Think step by step'' or changing the answer format). Always report the exact prompt used and consider evaluating across multiple prompt variants.

\paragraph{提示敏感性。}
\label{prompt-sensitivity.}

LLM 的性能可能会因评估提示的微小变化而发生剧烈变化（例如，添加“逐步思考”或更改答案格式）。始终报告所使用的确切提示，并考虑在多个提示变体上进行评估。

\paragraph{Aggregation artefacts.}
\label{aggregation-artefacts.}

Averaging scores across tasks with different difficulty levels and score distributions can produce misleading aggregate metrics. A model that excels at easy tasks but fails at hard tasks may have the same average score as a model with uniform performance.

\paragraph{聚合伪影。}
\label{aggregation-artefacts.}

对具有不同难度级别和分数分布的任务的得分进行平均可能会产生误导性的聚合指标。一个擅长简单任务但在困难任务上失败的模型，可能与一个性能均匀的模型具有相同的平均分数。

\paragraph{Selection bias in human evaluation.}
\label{selection-bias-in-human-evaluation.}

Human evaluators are not a random sample of end users. Annotators on crowdsourcing platforms may have different preferences, cultural backgrounds, and domain knowledge than the target user population.

\paragraph{人工评估中的选择偏差。}
\label{selection-bias-in-human-evaluation.}

人工评估者并非最终用户的随机样本。众包平台上的标注者可能具有与目标用户群体不同的偏好、文化背景和领域知识。

\paragraph{Evaluation--deployment mismatch.}
\label{evaluationdeployment-mismatch.}

Evaluation prompts are often shorter, cleaner, and more well-formed than real user queries. A model that performs well on benchmark prompts may degrade significantly on the noisy, ambiguous, multi-turn conversations that occur in production.

\paragraph{评估与部署不匹配。}
\label{evaluationdeployment-mismatch.}

评估提示通常比真实用户查询更短、更简洁、更规范。在基准提示上表现良好的模型，可能会在真实生产环境中出现的嘈杂、模糊、多轮对话中性能显著下降。

\begin{questionbox}[Key Questions for Evaluation Design]
Before deploying an evaluation pipeline, ask:

\begin{enumerate}
  \item Does the evaluation metric align with the deployment objective?
  \item Is the evaluation data representative of the target distribution?
  \item Have contamination and overfitting risks been assessed?
  \item Are confidence intervals reported for all metrics?
  \item Is the evaluation reproducible (fixed seeds, versioned prompts, public test sets)?
  \item Has the evaluation been validated against human judgments or extrinsic outcomes?
\end{enumerate}
\end{questionbox}

\begin{questionbox}[评估设计的关键问题]
在部署评估流程之前，请问：

\begin{enumerate}
  \item 评估指标是否与部署目标一致？
  \item 评估数据是否代表目标分布？
  \item 是否已评估了数据污染和过拟合的风险？
  \item 是否报告了所有指标的置信区间？
  \item 评估是否可复现（固定随机种子、版本化提示、公开测试集）？
  \item 评估是否已根据人工判断或外部结果进行了验证？
\end{enumerate}
\end{questionbox}

\part{Agentic AI}

\part{智能体人工智能}