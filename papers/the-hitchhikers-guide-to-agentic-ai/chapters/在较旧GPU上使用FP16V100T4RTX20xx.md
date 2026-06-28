# 在较旧GPU上使用FP16（V100, T4, RTX 20xx）
args_fp16 = TrainingArguments(
    output_dir="./out",
    fp16=True,               # FP16前向/反向
    fp16_full_eval=False,    # 评估时保持FP32精度
