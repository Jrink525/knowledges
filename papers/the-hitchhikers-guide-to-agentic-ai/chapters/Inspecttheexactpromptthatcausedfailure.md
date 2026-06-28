        # Inspect the exact prompt that caused failure
        if run.run_type == "llm":
            print(f"  Model: {run.extra.get('invocation_params', {}).get('model')}")
