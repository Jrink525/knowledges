    # Connect to the notes server via stdio
    server_params = StdioServerParameters(
        command="python",
        args=["notes_server.py"],
        env=None  # inherit environment
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
