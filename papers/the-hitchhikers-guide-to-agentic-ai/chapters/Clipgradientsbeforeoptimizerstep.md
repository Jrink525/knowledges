    # Clip gradients before optimizer step
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

    optimizer.step()
    scheduler.step()
    optimizer.zero_grad()
```

```python
for batch in train_dataloader:
    outputs = model(**batch)
    loss = outputs.loss
    loss.backward()

