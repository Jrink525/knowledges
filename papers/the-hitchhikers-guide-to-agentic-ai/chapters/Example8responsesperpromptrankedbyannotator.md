# Example: 8 responses per prompt, ranked by annotator
rewards = reward_model(responses)          # (batch, 8)
rankings = torch.argsort(human_scores, descending=True)  # best first
loss = plackett_luce_loss(rewards, rankings)
loss.backward()
