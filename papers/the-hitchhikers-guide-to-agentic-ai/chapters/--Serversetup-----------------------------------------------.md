# -- Server setup --------------------------------------------------------------
mcp = FastMCP("notes-server")
NOTES_DIR = Path.home() / ".notes"
NOTES_DIR.mkdir(exist_ok=True)


