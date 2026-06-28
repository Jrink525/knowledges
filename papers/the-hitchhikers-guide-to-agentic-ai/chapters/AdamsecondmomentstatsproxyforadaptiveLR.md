    # Adam second moment stats (proxy for adaptive LR)
    v_norms = []
    for group in optimizer.param_groups:
        for p in group['params']:
            state = optimizer.state[p]
            if 'exp_avg_sq' in state:
                v_norms.append(state['exp_avg_sq'].mean().item())

    print(f"Step {step}: grad_norm={total_norm:.3f}, "
          f"mean_v={sum(v_norms)/len(v_norms):.6f}")

