    # GDPO: 独立归一化每个奖励
    multi_objective_aggregation="normalize_then_sum",
    reward_weights=[1.0, 0.3, 0.1],  # 正确性，格式，长度
    num_generations=8,
)


trainer = GRPOTrainer(
    model=model,
    reward_funcs=[
        correctness_reward,
        format_reward,
        length_penalty_reward,
    ],
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}


\section{Listwise Rank-Based Rewards}
\label{listwise-rank-based-rewards}
## 基于列表排名的奖励
## \label{listwise-rank-based-rewards}

While the Bradley-Terry model handles \emph{pairwise} preferences ($y_w \succ y_l$), many practical scenarios involve ranking multiple responses simultaneously. Listwise reward models learn from complete orderings, providing richer training signal and enabling better calibration.
虽然Bradley-Terry模型处理的是\textit{成对}偏好（$y_w \succ y_l$），但许多实际场景需要对多个响应同时进行排序。列表奖励模型从完整的排序中学习，提供更丰富的训练信号并实现更好的校准。

\subsubsection*{Motivation: Beyond Pairwise}
\label{motivation-beyond-pairwise}
## 动机：超越成对
## \label{motivation-beyond-pairwise}

\begin{intuitionbox}[Why Listwise?]
\begin{intuitionbox}[为何使用列表排序？]
\begin{itemize}
  \item \textbf{Richer signal}: A ranking of $K$ responses contains $\binom{K}{2}$ implicit pairwise comparisons, but also captures \emph{relative margins} (how much better rank 1 is vs.~rank 3).
  \item \textbf{更丰富的信号}：$K$个响应的排序包含$\binom{K}{2}$个隐式成对比较，还捕捉了\textit{相对差距}（排名1比排名3好多少）。
  \item \textbf{Better calibration}: Pairwise BT models only learn \emph{differences} in reward; listwise models learn absolute reward scale.
  \item \textbf{更好的校准}：成对BT模型仅学习奖励的\textit{差异}；列表模型学习绝对的奖励尺度。
  \item \textbf{Natural fit for GRPO}: GRPO generates $N$ responses per prompt and ranks them --- listwise rewards align directly with this workflow.
  \item \textbf{与GRPO自然契合}：GRPO对每个提示生成$N$个响应并排序——列表奖励直接与该工作流程对齐。
  \item \textbf{Annotator efficiency}: Ranking 5 responses is faster than labeling all 10 possible pairs independently.
  \item \textbf{标注效率}：对5个响应排序比独立标注所有10个可能对更快。
\end{itemize}
\end{intuitionbox}


\subsubsection*{Plackett-Luce Model}
\label{plackett-luce-model}
## Plackett-Luce模型
## \label{plackett-luce-model}

The Plackett-Luce (PL) model~\cite{plackett1975analysis} is the standard extension of Bradley-Terry to full rankings. Given $K$ responses $y_1, \ldots, y_K$ with ranking $\pi$ (where $\pi(1)$ is the best):
Plackett-Luce（PL）模型~\cite{plackett1975analysis}是Bradley-Terry模型到完整排序的标准扩展。给定$K$个响应$y_1, \ldots, y_K$及其排序$\pi$（其中$\pi(1)$是最优的）：

\begin{keybox}[Plackett-Luce Likelihood]
\begin{keybox}[Plackett-Luce似然]
\[
P(\pi \mid q) = \prod_{i=1}^{K} \frac{e^{r_\phi(y_{\pi(i)}, q)}}{\sum_{j=i}^{K} e^{r_\phi(y_{\pi(j)}, q)}}
\]
 \textbf{Intuition}: Sequentially select the best remaining item. At each step, the probability of selecting item $\pi(i)$ is softmax over the remaining items.
 \textbf{直觉}：依次选择剩余的最佳项。每一步，选择项$\pi(i)$的概率是剩余项上的softmax。

\textbf{Loss function}: 
\textbf{损失函数}：
\[
\mathcal{L}_{\text{PL}}(\phi) = -\frac{1}{|\mathcal{D}|} \sum_{(q, \pi) \in \mathcal{D}} \sum_{i=1}^{K-1} \left[ r_\phi(y_{\pi(i)}, q) - \log \sum_{j=i}^{K} e^{r_\phi(y_{\pi(j)}, q)} \right]
\]
\end{keybox}


\begin{intuitionbox}[Plackett-Luce Reduces to Bradley-Terry]
\begin{intuitionbox}[Plackett-Luce退化为Bradley-Terry]
For $K=2$, the PL model gives: $P(y_1 \succ y_2) = \frac{e^{r(y_1)}}{e^{r(y_1)} + e^{r(y_2)}} = \sigma(r(y_1) - r(y_2))$ --- exactly the Bradley-Terry model. PL is a strict generalization.
对于$K=2$，PL模型给出：$P(y_1 \succ y_2) = \frac{e^{r(y_1)}}{e^{r(y_1)} + e^{r(y_2)}} = \sigma(r(y_1) - r(y_2))$ —— 正是Bradley-Terry模型。PL是其严格推广。
\end{intuitionbox}


\subsubsection*{ListMLE and Rank-Based Losses}
\label{listmle-and-rank-based-losses}
## ListMLE与基于排序的损失
## \label{listmle-and-rank-based-losses}

\begin{keybox}[Listwise Loss Functions]
\begin{itemize}
  \item \textbf{ListMLE}~\cite{xia2008listwise}: Directly maximizes the PL likelihood of the ground-truth ranking. Simple and effective.
  \item \textbf{ListMLE}~\cite{xia2008listwise}：直接最大化真实排序的PL似然。简单且有效。
  \item \textbf{ListNet}~\cite{cao2007listnet}: Minimizes KL divergence between the model’s top-1 probability distribution and the ground-truth: 
\[
\mathcal{L}_{\text{ListNet}} = -\sum_{i=1}^{K} P_{\text{true}}(y_i \text{ is best}) \cdot \log P_{\text{model}}(y_i \text{ is best})
\]
 where $P_{\text{model}}(y_i \text{ is best}) = \frac{e^{r_\phi(y_i)}}{\sum_j e^{r_\phi(y_j)}}$.
  \item \textbf{ListNet}~\cite{cao2007listnet}：最小化模型top-1概率分布与真实分布之间的KL散度：
\[
\mathcal{L}_{\text{ListNet}} = -\sum_{i=1}^{K} P_{\text{true}}(y_i \text{ is best}) \cdot \log P_{\text{model}}(y_i \text{ is best})
\]
 其中 $P_{\text{model}}(y_i \text{ is best}) = \frac{e^{r_\phi(y_i)}}{\sum_j e^{r_\phi(y_j)}}$。
  \item \textbf{LambdaRank}~\cite{burges2006lambdarank}: Weights pairwise gradients by the change in ranking metric (e.g., NDCG). Useful when ranking quality matters more at the top.
  \item \textbf{LambdaRank}~\cite{burges2006lambdarank}：通过排序指标（如NDCG）的变化加权成对梯度。当排名质量在顶部更为重要时非常有用。
  \item \textbf{RankNet}~\cite{burges2005ranknet}: Pairwise cross-entropy summed over all pairs --- equivalent to BT on all $\binom{K}{2}$ pairs extracted from the ranking.
  \item \textbf{RankNet}~\cite{burges2005ranknet}：对所有配对求和成对交叉熵——等价于在从排序中提取的所有$\binom{K}{2}$个配对上应用Bradley-Terry模型。
\end{itemize}
\end{keybox}

\subsubsection*{Listwise Rewards for GRPO and Rejection Sampling}
\subsubsection*{用于GRPO和拒绝采样的列表式奖励}
\label{listwise-rewards-for-grpo-and-rejection-sampling}

\begin{keybox}[Integration with GRPO]
GRPO naturally produces ranked groups: for each prompt, $N$ responses are scored and ranked. A listwise reward model can be trained directly on these rankings:

GRPO自然产生排序组：对每个提示，对$N$个响应进行评分和排序。列表式奖励模型可以直接在这些排序上训练：

\begin{enumerate}
  \item \textbf{Generate}: Sample $N=8$ responses per prompt from the policy.
  \item \textbf{生成}：从策略中为每个提示采样$N=8$个响应。
  \item \textbf{Rank}: Use an existing reward model (or human annotators) to produce a full ranking $\pi$.
  \item \textbf{排序}：使用现有的奖励模型（或人工标注员）产生完整排序$\pi$。
  \item \textbf{Train listwise RM}: Optimize the PL loss on $(q, \pi)$ tuples.
  \item \textbf{训练列表式RM}：在$(q, \pi)$元组上优化PL损失。
  \item \textbf{Use in GRPO}: The listwise RM assigns scalar rewards $r(y_i, q)$ to each response; GRPO computes advantages as $\hat{A}_i = (r_i - \mu) / \sigma$.
  \item \textbf{在GRPO中使用}：列表式RM为每个响应分配标量奖励$r(y_i, q)$；GRPO计算优势为$\hat{A}_i = (r_i - \mu) / \sigma$。
\end{enumerate}

\textbf{Advantage over pairwise}: The listwise RM sees all $N$ responses simultaneously, learning that rank-1 should have much higher reward than rank-$N$ (not just ``slightly better than one other response'').

\textbf{相对于成对方法的优势}：列表式RM同时看到所有$N$个响应，学习到排名第1的奖励应远高于排名第$N$的奖励（而不仅仅是“比另一个响应稍好”）。
\end{keybox}

\subsubsection*{Practical Considerations}
\subsubsection*{实践考虑}
\label{practical-considerations}

\begin{warningbox}[Listwise Training Challenges]
\begin{itemize}
  \item \textbf{Annotation cost}: Full rankings are expensive. Partial rankings (top-3 out of 8) reduce cost with minimal quality loss.
  \item \textbf{标注成本}：完整排序成本高昂。部分排序（如8个中取前3）在质量损失极小的情况下降低成本。
  \item \textbf{Ties}: Real rankings often have ties. Use the Plackett-Luce extension for ties: assign equal probability mass to tied items.
  \item \textbf{平局}：实际排序中常有平局。使用Plackett-Luce的平局扩展：为平局项分配相等概率质量。
  \item \textbf{Position bias}: Annotators tend to prefer items shown first. Randomize presentation order and train debiasing.
  \item \textbf{位置偏差}：标注员倾向于偏好先显示的项。随机化呈现顺序并训练去偏。
  \item \textbf{List length}: Training on $K=4$--8 is typical. Longer lists ($K>16$) add noise without much benefit.
  \item \textbf{列表长度}：通常在$K=4$--8上训练。更长的列表（$K>16$）增加噪声而收益不大。
  \item \textbf{Consistency}: Rankings from different annotators may disagree. Use inter-annotator agreement ($\kappa > 0.6$) as a quality filter.
  \item \textbf{一致性}：不同标注员的排序可能不一致。使用标注员间一致性（$\kappa > 0.6$）作为质量过滤器。
\end{itemize}
\end{warningbox}

\begin{examplebox}[Plackett-Luce Training Code]
\begin{lstlisting}[style=pythonstyle]
import torch
import torch.nn.functional as F


def plackett_luce_loss(rewards, rankings):
    """
    Args:
        rewards: (batch, K) - predicted scalar rewards for K responses
        rankings: (batch, K) - ground-truth ranking indices (0 = best)
    Returns:
        scalar loss
    """
