# Pseudocode: DPPO requires a custom trainer subclass
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    num_generations=8,
    beta=0.04,
)
