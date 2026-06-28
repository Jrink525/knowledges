        # Base case: context fits in one call
        return model.call(f"{query}\n\nContext:\n{context}")

