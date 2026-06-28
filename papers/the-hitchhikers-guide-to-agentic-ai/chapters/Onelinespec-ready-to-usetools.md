# One line: spec -> ready-to-use tools
toolset = OpenAPIToolset(spec_str=spec, spec_str_type="yaml")
tools = toolset.get_tools()  # [RestApiTool("get_forecast", ...)]

