    # 3. PPO 更新（内部处理 KL、GAE、裁剪）
    stats = ppo_trainer.step(query_tensors, response_tensors, rewards)
