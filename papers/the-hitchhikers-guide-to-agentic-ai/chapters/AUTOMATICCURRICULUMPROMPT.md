# === AUTOMATIC CURRICULUM PROMPT ===
CURRICULUM_PROMPT = """You are a curriculum designer for an AI agent.


Agent's current skill inventory:
- mine_wood(): Mines nearby oak/birch trees
- craft_planks(): Converts logs to planks
- craft_sticks(): Converts planks to sticks
- mine_stone(): Mines stone with wooden pickaxe


Propose the next task that:
1. Builds on existing skills (reachable from current abilities)
2. Introduces exactly ONE new concept or challenge
3. Is concrete and verifiable (clear success condition)


Next task proposal:"""
