    # With G=2, batch size must be at least 2 * num_prompts_per_step
    per_device_train_batch_size=2,
)


trainer = GRPOTrainer(
    model=model,
    reward_funcs=[reward_fn],
    args=config,
    train_dataset=dataset,
)
\end{lstlisting}
\end{examplebox}
\begin{examplebox}[TRL 中的 2-GRPO]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    num_generations=2,      # 关键变化——仅两次生成
    loss_type="grpo",       # 标准 GRPO 损失即可
    epsilon=0.2,
