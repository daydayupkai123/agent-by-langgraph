from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # 会话短期记忆：同一 thread_id 下持续追加，由 Checkpoint 持久化
    messages: Annotated[list[AnyMessage], add_messages]
    # Router 识别出的本轮意图
    intent: str
    # Router 下发的本轮可用工具名（全局注册表的子集）
    active_tools: list[str]
    # 本轮 ReAct 循环中 agent 节点已执行的次数，用于硬限制
    iterations: int
