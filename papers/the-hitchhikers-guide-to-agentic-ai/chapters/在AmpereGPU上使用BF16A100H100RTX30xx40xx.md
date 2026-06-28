# 在Ampere+ GPU上使用BF16（A100, H100, RTX 30xx/40xx）
args_bf16 = TrainingArguments(
    output_dir="./out",
    bf16=True,               # BF16前向/反向；FP32主权重
    bf16_full_eval=True,     # 评估时也使用BF16
