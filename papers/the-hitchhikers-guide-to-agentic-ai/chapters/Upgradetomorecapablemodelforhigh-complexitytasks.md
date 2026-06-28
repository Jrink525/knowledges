        # Upgrade to more capable model for high-complexity tasks
        if complexity > 0.8 and base_model == "gpt-4o-mini":
            return "gpt-4o"
