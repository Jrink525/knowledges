# The LLM evaluates partial reasoning states:
EVAL_PROMPT = """Evaluate if this partial solution can reach 24.


Numbers remaining: [4, 4, 10]
Steps so far: 13 - 9 = 4


Can these remaining numbers (4, 4, 10) be combined using +,-,*,/
to make 24?


Analysis: 4 * (10 - 4) = 4 * 6 = 24. Yes!


Judge: sure/maybe/impossible
Answer: sure"""


