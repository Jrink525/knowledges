# apply_chat_template 处理所有特殊令牌的插入
prompt = tokenizer.apply_chat_template(messages, tokenize=False)
print(prompt)
