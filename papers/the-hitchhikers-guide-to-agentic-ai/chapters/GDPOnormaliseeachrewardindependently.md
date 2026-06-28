    # GDPO: normalise each reward independently
    multi_objective_aggregation="normalize_then_sum",
    reward_weights=[1.0, 0.3, 0.1],  # correctness, format, length
    num_generations=8,
)


config = GRPOConfig(
