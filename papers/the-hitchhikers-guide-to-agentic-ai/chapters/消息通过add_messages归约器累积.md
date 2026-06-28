    # 消息通过 add_messages 归约器累积
    messages: Annotated[List[BaseMessage], add_messages]
