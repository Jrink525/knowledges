    # 4. DPO 损失 = -log(sigmoid(chosen_reward - rejected_reward))
    loss = -F.logsigmoid(chosen_rewards - rejected_rewards).mean()
    return loss


def get_sequence_logprob(model, sequences):
    """仅对响应 token 的对数概率求和。"""
    outputs = model(sequences["input_ids"], attention_mask=sequences["mask"])
    logits = outputs.logits[:, :-1, :]  # 为下一个 token 预测进行移位
    
