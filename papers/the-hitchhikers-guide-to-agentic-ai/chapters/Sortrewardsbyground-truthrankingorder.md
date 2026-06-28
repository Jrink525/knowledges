    # Sort rewards by ground-truth ranking order
    sorted_rewards = torch.gather(rewards, 1, rankings)  # (batch, K)
    
