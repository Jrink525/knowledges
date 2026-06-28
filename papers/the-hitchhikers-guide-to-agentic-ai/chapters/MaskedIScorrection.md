# Masked IS correction
config_mis = GRPOConfig(
    use_vllm=True,
    vllm_importance_sampling_correction=True,
    vllm_importance_sampling_mode="sequence_mask",      # MIS
    vllm_importance_sampling_cap=3.0,
)
\end{lstlisting}
\end{examplebox}
\begin{examplebox}[TRL 中的 TIS 和 MIS]
\begin{lstlisting}[style=pythonstyle]
from trl import GRPOConfig, GRPOTrainer


