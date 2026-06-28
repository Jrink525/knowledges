# === ATTEMPT 2 PROMPT (after first failure) ===


SYSTEM = """You are a coding agent. You can run bash commands and edit files.
Complete the task below. Learn from your previous reflections."""


USER = """Task: Fix the failing test in auth_service.py


=== REFLECTIONS FROM PREVIOUS ATTEMPTS ===
[Attempt 1 reflection]: I tried to modify the authenticate() function
directly but forgot that it depends on token_validator(). The test
failed because token_validator() was still returning the old format.
I should trace the dependency chain FIRST: check what authenticate()
calls, then fix the root cause (token_validator), not the symptom.
=== END REFLECTIONS ===


The repository is in /workspace/. The failing test is:
  test_auth.py::test_expired_token_returns_401


Begin by reading the relevant files, then fix the issue."""
\end{lstlisting}
\end{examplebox}

\begin{lstlisting}[style=pythonstyle]
