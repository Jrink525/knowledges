# pi_new/pi_old exceeds [1-eps, 1+eps]
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[DPPO – 概念性实现]
DPPO 尚未作为内置 TRL 训练器提供。自定义实现将使用 GRPOTrainer，并修改损失函数，使其基于分布散度（TV 或 KL）而非标准概率比率进行裁剪：

\begin{lstlisting}[style=pythonstyle]
