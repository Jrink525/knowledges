# 数据集格式: {"prompt": str, "chosen": str, "rejected": str}
dataset = load_dataset("argilla/ultrafeedback-binarized-preferences")

lora_config = LoraConfig(r=64, lora_alpha=16, lora_dropout=0.05,
    target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"])

dpo_config = DPOConfig(
    output_dir="./dpo_output",
    beta=0.1,                    # KL 正则化强度
    learning_rate=5e-7,          # 极低学习率以保证稳定性
    loss_type="sigmoid",         # 标准 DPO 损失
    max_length=2048,             # 最大序列长度
    max_prompt_length=1024,      # 提示截断
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,  # 有效批次大小 = 16
    gradient_checkpointing=True,
    bf16=True,
    num_train_epochs=1,          # DPO 容易过拟合——只跑 1 轮！
    warmup_ratio=0.1,
    logging_steps=10,
    eval_strategy="steps",
    eval_steps=200,
    save_strategy="steps",
    save_steps=500,
)

trainer = DPOTrainer(
    model=model,
    ref_model=None,             # 使用 LoRA 时，ref = 基模型（无需拷贝！）
    args=dpo_config,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    tokenizer=tokenizer,
    peft_config=lora_config,
)
trainer.train()
