# === VALUE ESTIMATION PROMPT (used during simulation) ===
VALUE_PROMPT = """You are evaluating an agent's progress on a task.


Task: Book a flight from NYC to London for under \$500, departing Dec 15.


Current state (after 3 actions):
- Searched flights on Kayak: found 12 results
- Filtered by price < \$500: 4 options remain
- Clicked on British Airways \$489 option: viewing details page


On a scale of 0.0 to 1.0, how likely is the agent to successfully
complete the task from this state? Consider:
- How close is the agent to the goal?
- Are there remaining obstacles (payment, seat selection)?
- Has the agent made any errors that need correction?


Score: """  # Model outputs e.g. "0.75"


