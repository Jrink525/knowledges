# 使用检查点器编译，并在 human_review 之前中断
graph = builder.compile(
    checkpointer=memory,
    interrupt_before=["human_review"]
)


