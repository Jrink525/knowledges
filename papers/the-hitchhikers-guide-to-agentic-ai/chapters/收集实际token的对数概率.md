    # 收集实际 token 的对数概率
    labels = sequences["labels"][:, 1:]  # 移位后的标签
    log_probs = F.log_softmax(logits, dim=-1)
    token_logps = log_probs.gather(-1, labels.unsqueeze(-1)).squeeze(-1)
    
