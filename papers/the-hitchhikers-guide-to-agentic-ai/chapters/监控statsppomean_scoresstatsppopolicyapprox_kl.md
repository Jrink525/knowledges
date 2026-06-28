    # 监控：stats["ppo/mean_scores"], stats["ppo/policy/approx_kl"]
\end{lstlisting}
```

## Critical Hyperparameters
## 关键超参数

\label{critical-hyperparameters}

\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{Parameter} & \textbf{Typical} & \textbf{Effect of Getting It Wrong} \\
\midrule
\texttt{cliprange} & 0.2 & Too low: no learning. Too high: instability. \\
\texttt{init\_kl\_coef} & 0.01--0.1 & Too low: reward hacking. Too high: stuck at SFT. \\
\texttt{target\_kl} & 4--8 & Adaptive controller target. Lower = conservative. \\
\texttt{ppo\_epochs} & 4 & Too many: overfits to batch. Too few: wastes gen compute. \\
\texttt{learning\_rate} & $1{-}5 \times 10^{-6}$ & Too high: catastrophic forgetting. \\
\texttt{batch\_size} & 64--256 & Larger = smoother gradients, more gen compute. \\
\texttt{temperature} & 0.7--1.0 & Lower: less exploration. Higher: noisier advantages. \\
\bottomrule
\end{tabular}

\begin{tabular}{@{}lp{5cm}p{8cm}@{}}
\toprule
\textbf{参数} & \textbf{典型值} & \textbf{参数设置错误的后果} \\
\midrule
\texttt{cliprange} & 0.2 & 过低：无法学习。过高：不稳定。 \\
\texttt{init\_kl\_coef} & 0.01--0.1 & 过低：奖励欺骗（reward hacking）。过高：停留在 SFT 阶段。 \\
\texttt{target\_kl} & 4--8 & 自适应控制器的目标值。越小越保守。 \\
\texttt{ppo\_epochs} & 4 & 过多：对批次过拟合。过少：浪费生成计算资源。 \\
\texttt{learning\_rate} & $1{-}5 \times 10^{-6}$ & 过高：灾难性遗忘。 \\
\texttt{batch\_size} & 64--256 & 越大：梯度越平滑，但生成计算量更大。 \\
\texttt{temperature} & 0.7--1.0 & 越低：探索越少。越高：优势估计噪声越大。 \\
\bottomrule
\end{tabular}
---

