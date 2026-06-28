# MLP 推测器（IBM 风格，轻量级头部）
llm = LLM(
    model="meta-llama/Meta-Llama-3.1-70B-Instruct",
    tensor_parallel_size=4,
    speculative_config={
        "model": "ibm-ai-platform/llama3-70b-accelerator",
        "draft_tensor_parallel_size": 1,
    },
)
\end{lstlisting}

\begin{warningbox}[When NOT to Use Speculative Decoding]
\begin{警告框}[何时不应使用推测解码]
\begin{itemize}
  \item \textbf{High batch sizes}: At batch $\geq 64$, generation is already compute-efficient. Speculation adds overhead (draft generation + verification) that doesn't pay off.
  \item \textbf{大批量大小}：当批量大小 $\geq 64$ 时，生成已经计算高效。推测会增加开销（草稿生成 + 验证），得不偿失。
  \item \textbf{Very different distributions}: If draft model is too dissimilar to target, acceptance rate drops below 50\% and speculation is slower than standard decoding.
  \item \textbf{分布差异极大}：如果草稿模型与目标模型差异过大，接受率降至 50\% 以下，推测解码比标准解码更慢。
  \item \textbf{Short outputs}: For $<$20 token outputs, the setup cost of speculation exceeds savings.
  \item \textbf{短输出}：对于少于 20 个 Token 的输出，推测的设置成本超过了节省。
  \item \textbf{Rule of thumb}: Speculation helps most for latency-sensitive, single-stream generation (chatbots, interactive code completion).
  \item \textbf{经验法则}：推测解码对延迟敏感、单流生成（聊天机器人、交互式代码补全）最有效。
\end{itemize}
\end{warningbox}
\end{警告框}

\newpage
\section{Hallucination Detection}
\section{幻觉检测}
\label{sec:hallucination}

LLMs generate fluent text that may be factually incorrect—a phenomenon called \textbf{hallucination}~\cite{ji2023hallucination}. This section covers basic detection methods at the model level (without external retrieval or multi-agent verification).
LLM 会生成流畅但可能事实不准确的文本——这种现象称为 \textbf{幻觉（Hallucination）}~\cite{ji2023hallucination}。本节介绍模型级别的基本检测方法（无需外部检索或多智能体验证）。

\subsection{Types of Hallucination}
\subsection{幻觉的类型}
\label{types-of-hallucination}

\begin{keybox}[Hallucination Taxonomy]
\begin{关键框}[幻觉分类体系]
\begin{itemize}
  \item \textbf{Intrinsic}: Contradicts the provided input/context (e.g., summary says the opposite of the source)
  \item \textbf{内在幻觉（Intrinsic）}：与提供的输入/上下文矛盾（例如，摘要与源文本意思相反）
  \item \textbf{Extrinsic}: Generates claims that cannot be verified from the input and are factually wrong
  \item \textbf{外在幻觉（Extrinsic）}：生成无法从输入中验证且事实错误的断言
  \item \textbf{Faithfulness}: Output diverges from the instruction or specified constraints
  \item \textbf{忠实性（Faithfulness）}：输出偏离了指令或指定的约束条件
\end{itemize}
\end{keybox}
\end{关键框}

\subsection{Detection Methods (Model-Level)}
\subsection{检测方法（模型级别）}
\label{detection-methods-model-level}

\begin{table}[ht!]
\centering
\begin{table}[ht!]
\centering
\caption{Basic hallucination detection methods that operate at the model level.}
\caption{在模型级别运行的基本幻觉检测方法。}
\begin{tabular}{@{}lp{6.5cm}l@{}}
\toprule
\textbf{Method} & \textbf{Mechanism} & \textbf{Signal} \\
\textbf{方法} & \textbf{机制} & \textbf{信号} \\
\midrule
Token-level entropy & High entropy at generation time indicates uncertainty~\cite{kadavath2022language} & $H(P(x_t)) > \tau$ \\
Token 级熵（Token-level entropy） & 生成时的高熵表示不确定性~\cite{kadavath2022language} & $H(P(x_t)) > \tau$ \\
Sequence log-prob & Low average log-probability of the output suggests confabulation & $\frac{1}{T}\sum_t \log P(x_t)$ \\
序列对数概率（Sequence log-prob） & 输出的平均对数概率低表明虚构 & $\frac{1}{T}\sum_t \log P(x_t)$ \\
Consistency sampling & Generate $N$ responses; low agreement $=$ likely hallucination~\cite{manakul2023selfcheckgpt} & Contradiction rate \\
一致性采样（Consistency sampling） & 生成 $N$ 个响应；低一致性 $=$ 可能幻觉~\cite{manakul2023selfcheckgpt} & 矛盾率 \\
Semantic entropy & Cluster meanings (not strings); high semantic entropy $=$ uncertain~\cite{kuhn2023semantic} & Cluster diversity \\
语义熵（Semantic entropy） & 对含义（而非字符串）进行聚类；高语义熵 $=$ 不确定~\cite{kuhn2023semantic} & 聚类多样性 \\
DoLA & Contrast logits between later vs.~earlier layers; amplifies factual knowledge~\cite{chuang2024dola} & Layer divergence \\
DoLA（Decoding by Contrasting Layers） & 对比较晚层与较早层的 logits；放大事实知识~\cite{chuang2024dola} & 层差异 \\
\bottomrule
\end{tabular}
\end{table}

\paragraph{Semantic Entropy.}
\paragraph{语义熵（Semantic Entropy）}
\label{semantic-entropy.}

Kuhn et al.~\cite{kuhn2023semantic} observe that token-level entropy is unreliable (paraphrases have different tokens but same meaning). Instead, they generate multiple responses, cluster them by semantic equivalence (via NLI), and compute entropy over meaning clusters:
Kuhn 等人~\cite{kuhn2023semantic} 观察到 Token 级熵不可靠（释义具有不同的 Token 但含义相同）。因此，他们生成多个响应，通过语义等价（借助 NLI）进行聚类，并计算含义聚类上的熵：
\[
SE = -\sum_{c \in \text{clusters}} P(c) \log P(c)
\]
High SE means the model produces \emph{semantically different} answers—a strong hallucination signal.
高 SE 意味着模型产生了\emph{语义不同的}答案——这是一个强烈的幻觉信号。

\paragraph{SelfCheckGPT.}
\paragraph{SelfCheckGPT}
\label{selfcheckgpt.}

Manakul et al.~\cite{manakul2023selfcheckgpt} detect hallucinations by checking self-consistency: generate multiple responses and verify whether claims in the main response are supported by the alternatives. If the model "disagrees with itself," the claim is likely hallucinated. No external knowledge needed.
Manakul 等人~\cite{manakul2023selfcheckgpt} 通过检查自一致性来检测幻觉：生成多个响应，并验证主要响应中的断言是否得到替代响应的支持。如果模型“与自己不一致”，则该断言很可能是幻觉。不需要外部知识。

\paragraph{DoLA (Decoding by Contrasting Layers).}
\paragraph{DoLA（通过对比层进行解码）}
\label{dola-decoding-by-contrasting-layers.}

Chuang et al.~\cite{chuang2024dola} observe that factual knowledge emerges in later transformer layers while earlier layers retain more generic/uncertain representations. DoLA contrasts the logit distributions between a later ("mature") layer and an earlier ("premature") layer at each decoding step:
Chuang 等人~\cite{chuang2024dola} 观察到，事实知识出现在较晚的 Transformer 层中，而较早的层保留更通用/不确定的表示。DoLA 在每个解码步骤对比较晚（“成熟”）层和较早（“不成熟”）层之间的 logit 分布：
\[
\text{DoLA}(x_t) = \text{softmax}\!\bigl(\log P_{\text{late}}(x_t) - \log P_{\text{early}}(x_t)\bigr)
\]
By amplifying the signal from factual knowledge encoded in deeper layers, DoLA reduces hallucinations at inference time \emph{without any retraining}—requiring only a single additional forward pass through the contrasted layer. It is complementary to sampling-based methods and can be combined with them.
通过放大来自深层编码的事实知识信号，DoLA 在推理时减少幻觉，\emph{无需任何重新训练}——仅需要额外一次通过被对比层的前向传播。它与基于采样的方法互补，并且可以结合使用。

\begin{warningbox}[Limitations of Model-Level Detection]
\begin{警告框}[模型级别检测的局限性]
These methods detect \emph{uncertainty}, not \emph{incorrectness}. A model can be confidently wrong (low entropy, consistent responses—but factually false). For reliable detection, combine with retrieval-based verification (RAG) or external fact-checking tools.
这些方法检测的是\emph{不确定性}，而不是\emph{错误性}。模型可能自信地犯错（低熵、一致的响应——但事实错误）。为了可靠检测，应结合基于检索的验证（RAG）或外部事实核查工具。
\end{warningbox}
\end{警告框}

\section{LLM Safety and Responsible AI}
\section{LLM 安全与负责任的人工智能}
\label{sec:safety}

Safety is not an afterthought—it is an integral part of the LLM training pipeline. This section covers the key dimensions of LLM safety and the mechanisms used to enforce responsible behavior.
安全性不是事后才考虑的问题——它是 LLM 训练流程中不可或缺的一部分。本节涵盖 LLM 安全的关键维度以及用于强制负责任行为的机制。

\subsection{Threat Taxonomy}
\subsection{威胁分类体系}
\label{threat-taxonomy}

\begin{table}[ht!]
\centering
\caption{LLM安全威胁类别。}
\caption{LLM safety threat categories.}
\begin{tabular}{@{}lp{11cm}@{}}
\toprule
\textbf{类别} & \textbf{描述与示例} \\
\textbf{Category} & \textbf{Description and Examples} \\
\midrule
\textbf{有害内容} & 生成有毒、暴力或非法指令（生物武器、CSAM） \\
\textbf{Harmful content} & Generating toxic, violent, or illegal instructions (bioweapons, CSAM) \\
\textbf{偏见与歧视} & 延续刻板印象；跨人群的不公平对待~\cite{gallegos2024bias} \\
\textbf{Bias and discrimination} & Perpetuating stereotypes; unfair treatment across demographics~\cite{gallegos2024bias} \\
\textbf{隐私侵犯} & 从训练数据中泄露个人身份信息；记忆攻击~\cite{carlini2021extracting} \\
\textbf{Privacy violations} & Leaking PII from training data; memorization attacks~\cite{carlini2021extracting} \\
\textbf{越狱} & 绕过安全护栏的对抗性提示~\cite{zou2023universal} \\
\textbf{Jailbreaking} & Adversarial prompts that bypass safety guardrails~\cite{zou2023universal} \\
\textbf{错误信息} & 生成令人信服但虚假的声明（大规模幻觉） \\
\textbf{Misinformation} & Generating convincing but false claims (hallucination at scale) \\
\textbf{双重用途} & 合法的能力（编程、化学）被武器化用于危害 \\
\textbf{Dual-use} & Legitimate capabilities (coding, chemistry) weaponized for harm \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Safety Training Pipeline}
\subsection{安全训练管线}
\label{safety-training-pipeline}

\begin{figure}[ht!]
\centering
\includegraphics[width=0.85\textwidth]{figures/fig_015_fig15.png}
\caption{安全在每个阶段都被应用：预训练中的数据过滤，SFT中的拒绝示例，RLHF中的安全专用奖励模型，以及迭代红队测试。}
\caption{Safety is applied at every stage: data filtering in pretraining, refusal examples in SFT, safety-specific reward models in RLHF, and iterative red-teaming.}
\end{figure}

\subsection{Key Safety Mechanisms}
\subsection{关键安全机制}
\label{key-safety-mechanisms}

\begin{keybox}[安全技术]
\begin{keybox}[Safety Techniques]
\begin{itemize}
  \item \textbf{数据过滤}：从预训练语料库中移除有毒、有偏见和包含个人身份信息的文本
  \item \textbf{Data filtering}: Remove toxic, biased, and PII-containing text from pretraining corpora
  \item \textbf{安全SFT}：在恰当的拒绝示例上进行训练（“我无法帮助您，因为……”）
  \item \textbf{Safety SFT}: Train on examples of appropriate refusals (``I can’t help with that because\ldots{}'')
  \item \textbf{宪政AI}~\cite{bai2022constitutional}：使用原则进行自我批评；模型根据规则宪法自我修正输出
  \item \textbf{Constitutional AI}~\cite{bai2022constitutional}: Self-critique using principles; model revises its own outputs against a constitution of rules
  \item \textbf{安全奖励模型}：在安全标注的对上训练的独立RM；在RLHF中通过加权求和与有用性RM结合
  \item \textbf{Safety reward model}: Separate RM trained on safety-annotated pairs; combined with helpfulness RM during RLHF via weighted sum
  \item \textbf{护栏}：在服务时阻止有害请求/响应的输入/输出分类器
  \item \textbf{Guardrails}: Input/output classifiers that block harmful requests/responses at serving time
  \item \textbf{红队测试}~\cite{perez2022red}：系统性的对抗性评估，在部署前发现失败模式
  \item \textbf{Red teaming}~\cite{perez2022red}: Systematic adversarial evaluation to find failure modes before deployment
\end{itemize}
\end{keybox}

\subsection{The Helpfulness--Safety Tradeoff}
\subsection{有用性——安全性的权衡}
\label{the-helpfulnesssafety-tradeoff}

\begin{intuitionbox}[平衡有用性与安全性]
\begin{intuitionbox}[Balancing Helpfulness and Safety]
过度优化安全性会产生“过度拒绝”问题：模型拒绝良性请求（例如，拒绝在教育背景下讨论历史暴力）。目标是在安全约束内实现最大有用性的帕累托最优策略：
Over-optimizing for safety creates an \emph{over-refusal} problem: the model declines benign requests (e.g., refusing to discuss historical violence in an educational context). The goal is a Pareto-optimal policy that is maximally helpful \emph{within} safety constraints: 
\[
\max_\theta \; \mathbb{E}[R_\text{helpful}] \quad \text{subject to} \quad \mathbb{E}[R_\text{safety}] \geq \tau
\]
 在实践中，这通过加权奖励实现：$R = \alpha R_\text{helpful} + (1-\alpha) R_\text{safety}$，并仔细调整$\alpha$（通常为0.6–0.8）。Meta的Llama-3报告使用了基于边际加权的独立安全性和有用性奖励模型~\cite{grattafiori2024llama3}。
 In practice, this is implemented as a weighted reward: $R = \alpha R_\text{helpful} + (1-\alpha) R_\text{safety}$ with careful tuning of $\alpha$ (typically 0.6--0.8). Meta’s Llama-3 reports using distinct safety and helpfulness reward models with margin-based weighting~\cite{grattafiori2024llama3}.
\end{intuitionbox}

\subsection{Evaluation}
\subsection{评估}
\label{evaluation}

\begin{itemize}
  \item \textbf{安全基准}：ToxiGen、RealToxicityPrompts、BBQ（偏见）、CrowS-Pairs
  \item \textbf{Safety benchmarks}: ToxiGen, RealToxicityPrompts, BBQ (bias), CrowS-Pairs
  \item \textbf{越狱鲁棒性}：GCG攻击~\cite{zou2023universal}、多轮越狱、编码提示
  \item \textbf{Jailbreak robustness}: GCG attacks~\cite{zou2023universal}, multi-turn jailbreaks, encoded prompts
  \item \textbf{过度拒绝率}：测量良性提示上的假阳性拒绝（目标<5%）
  \item \textbf{Over-refusal rate}: Measure false-positive refusals on benign prompts (target $<$5\%)
  \item \textbf{红队评估}：由领域专家（生物安全、网络安全）进行的人工对抗性测试
  \item \textbf{Red team evaluations}: Human adversarial testing with domain experts (biosecurity, cybersecurity)
\end{itemize}

\begin{warningbox}[安全永无止境]
\begin{warningbox}[Safety Is Never Complete]
没有任何技术组合能提供绝对安全。新的攻击向量持续被发现（多模态越狱、微调攻击可移除安全训练、多轮提示）。安全需要持续监控、对新威胁的快速响应以及纵深防御（多层独立防御）。
No combination of techniques provides absolute safety. New attack vectors are discovered continuously (multi-modal jailbreaks, fine-tuning attacks that remove safety training, many-shot prompting). Safety requires ongoing monitoring, rapid response to new threats, and defense-in-depth (multiple independent layers).
\end{warningbox}
---

