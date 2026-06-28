# 微信公众号：方云智能AI

import re
from datetime import datetime
from typing import List, Optional, Tuple

from memory import HierarchicalMemoryManager, MemoryEntry, MemoryTier

class MemoryAugmentedAgent:
    """A minimal agent that uses hierarchical memory to augment an LLM.
       It reads relevant memories before generating responses,
       writes important information automatically,
       and reflects periodically to consolidate knowledge."""

    """一个使用层级记忆增强LLM的最小化代理。
       它在生成响应前读取相关记忆，
       自动写入重要信息，
       并定期反思以巩固知识。"""

    SYSTEM_PROMPT = """You are an AI assistant with hierarchical memory.
    You can remember information across sessions and use past experiences
    to inform your responses. Always think step by step. Use memory to avoid repeating mistakes
    and to personalize your responses."""

    SYSTEM_PROMPT = """你是一个拥有层级记忆的人工智能助手。
    你能够跨会话记住信息，并利用过去的经验
    来指导你的回答。始终逐步思考。利用记忆避免重复错误
    并个性化你的回应。"""

    def __init__(
        self,
        llm_fn,                         # callable: messages -> str
        memory_manager: HierarchicalMemoryManager,
        importance_threshold: float = 0.6,
        max_memory_tokens: int = 1500,
    ):
        self.llm = llm_fn
        self.memory = memory_manager
        self.importance_threshold = importance_threshold
        self.max_memory_tokens = max_memory_tokens
        self.conversation_history: list[dict] = []

    def __init__(
        self,
        llm_fn,                         # 可调用: messages -> str
        memory_manager: HierarchicalMemoryManager,
        importance_threshold: float = 0.6,
        max_memory_tokens: int = 1500,
    ):
        self.llm = llm_fn
        self.memory = memory_manager
        self.importance_threshold = importance_threshold
        self.max_memory_tokens = max_memory_tokens
        self.conversation_history: list[dict] = []

