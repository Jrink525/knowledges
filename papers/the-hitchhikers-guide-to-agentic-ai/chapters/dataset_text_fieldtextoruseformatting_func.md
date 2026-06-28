    # dataset_text_field="text",  # or use formatting_func
)
trainer.train()
\end{lstlisting}
\end{examplebox}
\begin{examplebox}[TRL 中的序列打包]
\begin{lstlisting}[style=pythonstyle]
from trl import SFTConfig, SFTTrainer


config = SFTConfig(
    max_seq_length=4096,
    packing=True,           # 启用序列打包
    output_dir="sft_model",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-5,
    num_train_epochs=3,
)


trainer = SFTTrainer(
    model=model,
    args=config,
    train_dataset=dataset,
