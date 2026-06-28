                           # 对应 epsilon = 0.1
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

\subsection{TR-DPO -- Trust Region DPO}
\subsection{TR-DPO——信任区域 DPO}
\label{sec:tr-dpo}

\begin{intuitionbox}[Stale Reference Model Problem]
Standard DPO uses a fixed reference model $\pi_{\text{ref}}$ throughout training. As the policy $\pi_\theta$ improves, the KL penalty $\beta \log(\pi_\theta/\pi_{\text{ref}})$ grows, eventually dominating the loss and preventing further improvement. TR-DPO~\cite{gorbatenko2024trdpo} periodically updates the reference model to track the current policy.
\begin{intuitionbox}[过时参考模型问题]
标准 DPO 在整个训练过程中使用固定的参考模型 $\pi_{\text{ref}}$。随着策略 $\pi_\theta$ 的提升，KL 惩罚项 $\beta \log(\pi_\theta/\pi_{\text{ref}})$ 不断增大，最终主导损失函数，阻碍进一步改进。TR-DPO（信任区域DPO）~\cite{gorbatenko2024trdpo} 定期更新参考模型以跟踪当前策略。
\end{intuitionbox}

TR-DPO updates the reference model using an exponential moving average (EMA):
TR-DPO 使用指数移动平均（EMA）更新参考模型：

\[
\pi_{\text{ref}}^{(t+1)} \leftarrow
    \alpha \cdot \pi_\theta^{(t)} + (1-\alpha) \cdot \pi_{\text{ref}}^{(t)},
\]

where $\alpha \in (0,1)$ is the mixup coefficient. This is applied every $T_{\text{sync}}$ gradient steps.
其中 $\alpha \in (0,1)$ 是混合系数。该更新每 $T_{\text{sync}}$ 个梯度步执行一次。

\begin{examplebox}[TR-DPO in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


config = DPOConfig(
    loss_type="sigmoid",        # standard DPO loss
