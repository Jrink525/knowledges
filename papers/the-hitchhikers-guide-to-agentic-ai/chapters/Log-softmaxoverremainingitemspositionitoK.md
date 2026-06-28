        # Log-softmax over remaining items (position i to K)
        remaining = sorted_rewards[:, i:]           # (batch, K-i)
        log_probs = remaining[:, 0] - torch.logsumexp(remaining, dim=1)
        loss -= log_probs.mean()
    
    return loss / (K - 1)


