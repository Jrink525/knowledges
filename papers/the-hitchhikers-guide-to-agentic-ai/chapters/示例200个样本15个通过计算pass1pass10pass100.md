# 示例：200 个样本，15 个通过，计算 pass@1, pass@10, pass@100
for k in [1, 10, 100]:
    score = pass_at_k(n=200, c=15, k=k)
    print(f"pass@{k}: {score:.4f}")
