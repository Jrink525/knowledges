        # Break correlation by selecting random experiences
        return random.sample(self.buffer, batch_size)
        
    def __len__(self):
        return len(self.buffer)
\end{lstlisting}
\begin{lstlisting}[style=pythonstyle]
import random
from collections import deque


class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)  # 有界队列
    
    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
        
    def sample(self, batch_size):
