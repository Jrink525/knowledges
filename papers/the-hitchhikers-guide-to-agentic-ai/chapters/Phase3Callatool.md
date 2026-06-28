            # Phase 3: Call a tool
            result = await session.call_tool(
                "create_note",
                arguments={
                    "title": "MCP Architecture Notes",
                    "content": "MCP uses JSON-RPC 2.0 over stdio or HTTP+SSE.",
                    "tags": ["mcp", "architecture"]
                }
            )
            print(f"\nTool result: {result.content[0].text}")

