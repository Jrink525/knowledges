# PPO配置，包含所有关键超参数
ppo_config = PPOConfig(
    learning_rate=1.5e-6,        # Low LR for stability
    learning_rate=1.5e-6,        # 低学习率以保证稳定性
    batch_size=128,              # Prompts per step
    batch_size=128,              # 每步的提示词数量
    mini_batch_size=16,          # Gradient accumulation unit
    mini_batch_size=16,          # 梯度累积单元
    ppo_epochs=4,                # Epochs per batch (reuse data)
    ppo_epochs=4,                # 每个批次的epoch数（重用数据）
    gamma=1.0,                   # No discounting (single turn)
    gamma=1.0,                   # 无折扣（单轮交互）
    lam=0.95,                    # GAE lambda
    lam=0.95,                    # 广义优势估计lambda
    cliprange=0.2,               # PPO epsilon
    cliprange=0.2,               # PPO epsilon
    cliprange_value=0.2,         # Value function clipping
    cliprange_value=0.2,         # 价值函数裁剪
    vf_coef=0.1,                 # Value loss coefficient
    vf_coef=0.1,                 # 价值损失系数
    init_kl_coef=0.05,           # Initial KL penalty
    init_kl_coef=0.05,           # 初始KL惩罚
    target_kl=6.0,               # Adaptive KL target
    target_kl=6.0,               # 自适应KL目标
    whiten_rewards=True,         # Normalize advantages
    whiten_rewards=True,         # 标准化优势
    gradient_accumulation_steps=4,
    gradient_accumulation_steps=4,
    max_grad_norm=1.0,
)

ppo_trainer = PPOTrainer(config=ppo_config, model=model, tokenizer=tokenizer,
    dataset=prompt_dataset, data_collator=collator)
```

## Training loop
## 训练循环

```latex
