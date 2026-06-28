# Re-run the failing step with a modified prompt or model
from openai import OpenAI
client = OpenAI()
failing_run = child_runs[4]  # e.g., step that errored
