# 生产环境 vLLM 生成设置
from vllm import LLM, SamplingParams


engine = LLM(
    model="./policy_checkpoint",
    tensor_parallel_size=4,           # TP=4 per instance
