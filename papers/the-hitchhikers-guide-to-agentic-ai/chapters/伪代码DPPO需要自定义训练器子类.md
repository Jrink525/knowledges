# 伪代码：DPPO 需要自定义训练器子类
from trl import GRPOConfig, GRPOTrainer


config = GRPOConfig(
    num_generations=8,
    beta=0.04,
)
