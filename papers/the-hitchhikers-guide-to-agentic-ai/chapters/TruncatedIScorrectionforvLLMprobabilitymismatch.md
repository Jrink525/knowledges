# Truncated IS correction for vLLM probability mismatch
config_tis = GRPOConfig(
    use_vllm=True,
    vllm_importance_sampling_correction=True,
    vllm_importance_sampling_mode="sequence_truncate",  # TIS
    vllm_importance_sampling_cap=5.0,                   # C threshold
)


