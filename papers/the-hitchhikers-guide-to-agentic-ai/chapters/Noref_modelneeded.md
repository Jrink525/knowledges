    # No ref_model needed!
)


trainer = DPOTrainer(
    model=model,
    ref_model=None,    # SimPO is reference-free
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[TRL 中的 SimPO]
\begin{lstlisting}[style=pythonstyle]
from trl import DPOConfig, DPOTrainer


config = DPOConfig(
    loss_type="simpo",
    simpo_gamma=0.5,   # 目标奖励边际 gamma
    beta=2.5,          # 长度归一化系数
