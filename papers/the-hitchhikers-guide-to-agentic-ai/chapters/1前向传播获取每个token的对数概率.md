    # 1. 前向传播：获取每个 token 的对数概率
    logps_chosen = get_sequence_logprob(model, batch["chosen"])
    logps_rejected = get_sequence_logprob(model, batch["rejected"])
    
