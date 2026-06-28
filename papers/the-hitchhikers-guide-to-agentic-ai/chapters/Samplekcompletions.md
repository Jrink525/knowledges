        # Sample k completions
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.8,
            num_return_sequences=k,
        )

        correct = 0
        for output in outputs:
            response = tokenizer.decode(output, skip_special_tokens=True)
            if ground_truth in response:
                correct += 1

