# 加载 Llama-3 分词器（128K 词表，字节级 BPE）
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")

text = "Reinforcement learning optimizes long-term rewards."
text = "强化学习优化长期奖励。"

