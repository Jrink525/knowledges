# Llama 3 format
template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{system_message}<|eot_id|><|start_header_id|>user<|end_header_id|>
{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
{assistant_message}<|eot_id|>"""
\end{lstlisting}

\begin{examplebox}[Applying Chat Templates in TRL]
\begin{lstlisting}[style=pythonstyle]
from transformers import AutoTokenizer
from trl import SFTConfig, SFTTrainer


tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")


def formatting_func(example):
    """Apply chat template to a dataset example."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": example["instruction"]},
        {"role": "assistant", "content": example["response"]},
    ]
    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
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
    formatting_func=formatting_func,
)
\end{lstlisting}
\end{examplebox}
\begin{examplebox}[在 TRL 中应用聊天模板]
\begin{lstlisting}[style=pythonstyle]
from transformers import AutoTokenizer
from trl import SFTConfig, SFTTrainer


tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")


def formatting_func(example):
    """将聊天模板应用于数据集样本。"""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": example["instruction"]},
        {"role": "assistant", "content": example["response"]},
    ]
    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
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
    formatting_func=formatting_func,
)
\end{lstlisting}
\end{examplebox}

## Completion-Only Masking
## 仅完成掩码

\label{sec:completion-masking}

\begin{intuitionbox}[Why Mask the Prompt?]
In instruction fine-tuning, the model should learn to generate the assistant’s response, not to predict the user’s question or the system prompt. Computing loss on the prompt tokens wastes gradient signal and can cause the model to ``memorise'' prompts rather than learning to respond to them. Completion-only masking sets the loss to zero for all non-assistant tokens.
\end{intuitionbox}
\begin{intuitionbox}[为什么要掩码提示？]
在指令微调中，模型应该学习生成助手的响应，而不是预测用户的问题或系统提示。在提示 token 上计算损失会浪费梯度信号，并可能导致模型“记忆”提示而不是学习如何响应。仅完成掩码将所有非助手 token 的损失设为零。
\end{intuitionbox}

\begin{examplebox}[Completion-Only Masking in TRL]
\begin{lstlisting}[style=pythonstyle]
from trl import SFTConfig, SFTTrainer, DataCollatorForCompletionOnlyLM
from transformers import AutoTokenizer


tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")


