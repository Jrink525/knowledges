                 # KL 惩罚系数
)

trainer = GRPOTrainer(
    model=model,
    ref_model=ref_model,   # required for token weighting
