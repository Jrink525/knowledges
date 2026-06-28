    # Gather log-prob of actual tokens
    labels = sequences["labels"][:, 1:]  # Shifted labels
    log_probs = F.log_softmax(logits, dim=-1)
    token_logps = log_probs.gather(-1, labels.unsqueeze(-1)).squeeze(-1)
    
