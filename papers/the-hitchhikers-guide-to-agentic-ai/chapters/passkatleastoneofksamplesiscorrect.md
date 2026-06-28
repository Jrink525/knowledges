        # pass@k: at least one of k samples is correct
        pass_at_k_scores.append(correct >= 1)

    print(f"Pass@1 (estimated): {np.mean(pass_at_1_scores):.2%}")
    print(f"Pass@{k}: {np.mean(pass_at_k_scores):.2%}")
    print(f"RL viability: {'Good' if np.mean(pass_at_1_scores) > 0.05 else 'Poor'}")


estimate_pass_at_k(sft_model, tokenizer, eval_dataset)
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[在RL之前检查SFT质量]
\begin{lstlisting}[style=pythonstyle]
import numpy as np
from tqdm import tqdm


def estimate_pass_at_k(model, tokenizer, dataset, k=8, n_samples=100):
    """
    Estimate pass@k for the SFT model.  # 估计SFT模型的pass@k
    If pass@1 < 5%, RL will likely fail.  # 如果pass@1 < 5%，RL很可能失败
    If pass@k < 20%, RL will struggle.    # 如果pass@k < 20%，RL将举步维艰
    """
    pass_at_1_scores = []
    pass_at_k_scores = []

    for example in tqdm(dataset.select(range(n_samples))):
        prompt = example["prompt"]
        ground_truth = example["answer"]

