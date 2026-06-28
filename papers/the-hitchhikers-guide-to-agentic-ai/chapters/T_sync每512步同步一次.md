                                # T_sync: 每 512 步同步一次
    beta=0.1,
)


trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\begin{keybox}[When to Use TR-DPO]
\begin{itemize}
  \item Long training runs where the policy drifts far from the initial reference.
  \item When you observe the DPO loss plateauing early due to KL penalty domination.
  \item Iterative DPO pipelines where new preference data is collected from the current policy.
  \item Set $\alpha$ close to 1 for fast reference updates; close to 0 for slow updates.
\end{itemize}
\begin{keybox}[何时使用 TR-DPO]
\begin{itemize}
  \item 长时间训练，策略与初始参考模型偏差较大时。
  \item 当观察到 DPO 损失因 KL 惩罚主导而过早趋于平稳时。
  \item 迭代式 DPO 流程中，需要从当前策略收集新的偏好数据时。
  \item 将 $\alpha$ 设为接近 1 以快速更新参考模型；接近 0 以缓慢更新。
\end{itemize}
\end{keybox}

\subsection{EXO -- Exact Optimisation}
\subsection{EXO——精确优化}
\label{sec:exo}

\begin{intuitionbox}[DPO’s KL Direction Problem]
DPO is derived by solving for the optimal policy under a reverse KL constraint. However, the resulting loss actually optimises a \emph{forward} KL objective in the reward space, which is the wrong direction. EXO~\cite{ji2024exo} corrects this by using reverse KL probability matching, which is the theoretically correct objective for alignment.
\begin{intuitionbox}[DPO 的 KL 方向问题]
DPO 通过在逆向 KL 约束下求解最优策略推导得出。然而，最终的损失函数实际上在奖励空间中优化的是 \emph{正向} KL 目标，这是错误的方向。EXO（精确优化）~\cite{ji2024exo} 通过使用逆向 KL 概率匹配来修正这一问题，这是对齐任务中理论上正确的目标。
\end{intuitionbox}

EXO minimises the reverse KL between the model distribution and the target (reward-optimal) distribution:
EXO 最小化模型分布与目标（奖励最优）分布之间的逆向 KL：

\[
\mathcal{L}_{\text{EXO}} = \mathbb{E}_{y \sim \pi_\theta}\!\left[
    \log \frac{\pi_\theta(y|q)}{p^*(y|q)}
  \right],
\]

where $p^*(y|q) \propto \pi_{\text{ref}}(y|q) \exp(r(y,q)/\beta)$ is the optimal policy. In practice, EXO approximates this using the available preference pairs:
其中 $p^*(y|q) \propto \pi_{\text{ref}}(y|q) \exp(r(y,q)/\beta)$ 是最优策略。实践中，EXO 利用可用的偏好对进行近似：

\[
\mathcal{L}_{\text{EXO}} \approx -\mathbb{E}\!\left[
    \log \sigma\!\left(
      \beta \log \frac{\pi_{\text{ref}}(y_w|q)}{\pi_\theta(y_w|q)}
      - \beta \log \frac{\pi_{\text{ref}}(y_l|q)}{\pi_\theta(y_l|q)}
    \right)
  \right].
\]

Note the \emph{swapped} roles of $\pi_\theta$ and $\pi_{\text{ref}}$ compared to DPO.
注意与 DPO 相比，$\pi_\theta$ 和 $\pi_{\text{ref}}$ 的角色发生了 \emph{互换}。

\begin{examplebox}[EXO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


config = DPOConfig(
    loss_type="exo_pair",
    beta=0.1,
)


trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\subsection{NCA -- Noise Contrastive Alignment}
\subsection{NCA——噪声对比对齐}
\label{sec:nca}

\begin{intuitionbox}[Likelihood Collapse in DPO]
A known failure mode of DPO is \emph{likelihood collapse}: the model learns to decrease the probability of the losing response but also decreases the probability of the winning response (since the loss only cares about the \emph{difference}). NCA~\cite{chen2024nca} adds an absolute likelihood term to prevent this.
\begin{intuitionbox}[DPO 中的似然坍塌]
DPO 的一个已知失败模式是 \emph{似然坍塌}：模型学会降低失败回复的概率，但同时也会降低获胜回复的概率（因为损失函数只关心 \emph{差值}）。NCA（噪声对比对齐）~\cite{chen2024nca} 通过添加一个绝对似然项来防止这一问题。
\end{intuitionbox}

NCA reframes alignment as noise-contrastive estimation. The loss has three terms:
NCA 将对齐重新定义为噪声对比估计。损失函数包含三项：

\[
\boxed{
    \mathcal{L}_{\text{NCA}} =
      -\log \sigma(r_w)
      - \tfrac{1}{2}\log \sigma(-r_w)
      - \tfrac{1}{2}\log \sigma(-r_l),
  }
\]

where $r_y = \beta \log(\pi_\theta(y|q)/\pi_{\text{ref}}(y|q))$ is the implicit reward. The first term encourages high reward for $y_w$; the second and third terms penalise high reward for both $y_w$ and $y_l$ (preventing collapse).
其中 $r_y = \beta \log(\pi_\theta(y|q)/\pi_{\text{ref}}(y|q))$ 是隐式奖励。第一项鼓励 $y_w$ 获得高奖励；第二项和第三项惩罚 $y_w$ 和 $y_l$ 两者的高奖励（防止坍塌）。

\begin{examplebox}[NCA in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


config = DPOConfig(
    loss_type="nca_pair",
    beta=0.01,   # small beta: absolute likelihood term dominates
