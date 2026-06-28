# Proportional mixing (default)
mixed_dataset = concatenate_datasets([
    dataset_math,
    dataset_code,
    dataset_general,
]).shuffle(seed=42)

\end{lstlisting}
\end{examplebox}
\begin{examplebox}[TRL 中的数据混合]
\begin{lstlisting}[style=pythonstyle]
from datasets import concatenate_datasets, interleave_datasets


