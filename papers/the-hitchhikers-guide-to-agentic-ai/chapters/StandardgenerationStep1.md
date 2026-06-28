# Standard generation (Step 1):
PROMPT = """Solve the following problem step by step.
Problem: A store has 45 apples. It sells 3/5 of them. How many remain?
Let's think step by step:"""
\end{lstlisting}
\end{examplebox}

\begin{intuitionbox}[STaR Variants for Agents]
\begin{intuitionbox}[STaR的智能体变体]
\begin{itemize}
  \item \textbf{Quiet-STaR}~\cite{zelikman2024quietstar}: Inserts ``thinking tokens'' between every token of generation. The model learns to reason \emph{implicitly} without explicit CoT prompting. Training objective: predict next tokens better when thinking tokens are included.
  \item \textbf{Quiet-STaR}~\cite{zelikman2024quietstar}：在每个生成令牌之间插入“思考令牌”。模型学习在不显式使用CoT提示的情况下进行\textit{隐式}推理。训练目标：当包含思考令牌时，更好地预测下一个令牌。
  \item \textbf{STaR for Code Agents}: Replace answer verification with test execution. ``Correct'' = all tests pass. Rationalization = generate a new approach conditioned on the error message.
  \item \textbf{代码智能体的STaR}：用测试执行替代答案验证。“正确”=所有测试通过。合理化（Rationalization）=根据错误信息生成新的方法。
  \item \textbf{V-STaR}~\cite{hosseini2024vstar}: Adds a verifier model trained on $(z, y, \text{correct/incorrect})$ triples. The verifier provides process-level supervision, filtering bad reasoning traces that accidentally reach correct answers.
  \item \textbf{V-STaR}~\cite{hosseini2024vstar}：添加一个在$(z, y, \text{正确/错误})$三元组上训练的验证器模型。验证器提供过程级监督，过滤那些偶然得到正确答案的糟糕推理轨迹。
\end{itemize}
\end{intuitionbox}
\end{intuitionbox}

\subsection{Reflexion: Verbal Reinforcement Learning (Detailed)}
\subsection{Reflexion：基于语言模型的强化学习（详细）}
\label{reflexion-verbal-reinforcement-learning-detailed}

Reflexion~\cite{shinn2023reflexion} introduces a radical paradigm: \textbf{RL without weight updates}. Instead of gradient-based learning, the agent improves through natural-language self-critique stored in an episodic memory.

Reflexion~\cite{shinn2023reflexion} 引入了一个激进的范式：\textbf{不更新权重的强化学习}。智能体不是通过基于梯度的学习，而是通过存储在情景记忆中的自然语言自我批评来改进。

\textbf{Full Architecture}:

\textbf{完整架构}：

\begin{enumerate}
  \item \textbf{Actor}: The LLM agent $\pi$ that executes actions in the environment.
  \item \textbf{Actor（行动者）}：在环境中执行动作的LLM智能体 $\pi$。
  \item \textbf{Evaluator}: A binary signal (task success/failure) or a scalar heuristic (e.g., number of test cases passed).
  \item \textbf{Evaluator（评估器）}：一个二元信号（任务成功/失败）或一个标量启发式（例如，通过的测试用例数量）。
  \item \textbf{Self-Reflection Generator}: Given the failed trajectory $\tau_{\text{fail}}$ and environment feedback, generates a natural-language reflection $r_{\text{text}}$: 
  \item \textbf{Self-Reflection Generator（自我反思生成器）}：给定失败轨迹 $\tau_{\text{fail}}$ 和环境反馈，生成一个自然语言反思 $r_{\text{text}}$：
\begin{equation}
r_{\text{text}} = \text{LLM}_{\text{reflect}}\!\left(\tau_{\text{fail}}, \text{feedback}, \text{task}\right)
\end{equation}
  \item \textbf{Episodic Memory}: A sliding window buffer $\mathcal{M} = [r_1, r_2, \ldots, r_m]$ of past reflections (typically $m \leq 3$ to fit in context).
  \item \textbf{Episodic Memory（情景记忆）}：一个滑动窗口缓冲区 $\mathcal{M} = [r_1, r_2, \ldots, r_m]$，用于存储过去的反思（通常 $m \leq 3$ 以适应上下文）。
  \item \textbf{Retry Loop}: On the next attempt, reflections are injected into the prompt: 
  \item \textbf{Retry Loop（重试循环）}：在下次尝试时，将反思注入到提示中：
\begin{equation}
a_{t+1} \sim \pi\!\left(\cdot\; |\; \text{task},\; \mathcal{M},\; \text{current\_state}\right)
\end{equation}
\end{enumerate}

\textbf{Example reflection}: \emph{``In my previous attempt, I called the search API before validating the input format, which caused a 400 error. Next time, I should validate the JSON schema first, then make the API call.''}

\textbf{示例反思}：\emph{“在之前的尝试中，我在验证输入格式之前调用了搜索API，导致400错误。下次我应该先验证JSON模式，然后再调用API。”}

\begin{examplebox}[Reflexion: Agent Prompt with Injected Memory]
\begin{examplebox}[Reflexion：注入记忆的智能体提示]
\begin{lstlisting}[style=pythonstyle]
