# 基于 LLM 的发言者选择的群聊
groupchat = autogen.GroupChat(
    agents=[user_proxy, planner, coder, critic],
    messages=[],
    max_round=20,
    speaker_selection_method="auto",
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)


