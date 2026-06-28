    # Margin loss
    center_rewards_coefficient=0.01,
)


trainer = RewardTrainer(
    model=model,
    args=config,
    train_dataset=dataset,  # must have chosen/rejected columns
)
trainer.train()
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[TRL 中的奖励模型训练]
\begin{lstlisting}[style=pythonstyle]
from trl import RewardConfig, RewardTrainer
from transformers import AutoModelForSequenceClassification


