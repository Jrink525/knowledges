# === SKILL GENERATION PROMPT ===
SKILL_GEN_PROMPT = """Write a JavaScript function to accomplish this task
in Minecraft. Use the bot API (bot.dig, bot.craft, bot.equip, etc.)


Task: Smelt 5 iron ingots using a furnace.
Prerequisites available: mine_stone(), craft_furnace(), mine_iron_ore()


Error from previous attempt: "Cannot smelt without fuel in furnace"
\end{lstlisting}
\end{examplebox}

\begin{examplebox}[Voyager：课程与技能生成提示词]
\begin{lstlisting}[style=pythonstyle]
