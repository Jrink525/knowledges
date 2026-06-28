# Define the response template (tokens after which loss is computed)
response_template = "<|start_header_id|>assistant<|end_header_id|>"
collator = DataCollatorForCompletionOnlyLM(
    response_template=response_template,
    tokenizer=tokenizer,
)


config = SFTConfig(
    max_seq_length=2048,
    output_dir="sft_model",
)


trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    args=config,
    train_dataset=dataset,
    data_collator=collator,   # completion-only masking
    formatting_func=formatting_func,
)
\end{lstlisting}
\end{examplebox}
\begin{examplebox}[TRL 中的仅完成掩码]
\begin{lstlisting}[style=pythonstyle]
from trl import SFTConfig, SFTTrainer, DataCollatorForCompletionOnlyLM
from transformers import AutoTokenizer


tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")


