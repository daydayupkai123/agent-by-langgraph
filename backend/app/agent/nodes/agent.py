"""Agent 节点：ReAct 循环中的单次 LLM 推理，决定直接回答还是发起工具调用。"""

from langchain_core.messages import AIMessage, AnyMessage, SystemMessage

from app.agent.prompts import agent_system_prompt
from app.agent.state import AgentState
from app.core.config import get_settings
from app.llm import get_agent_llm
from app.tools import registry


def _without_reasoning(messages: list[AnyMessage]) -> list[AnyMessage]:
    """历史中的思考内容只用于展示，回传给模型会导致重复思考、浪费上下文。"""
    cleaned: list[AnyMessage] = []
    for msg in messages:
        if isinstance(msg, AIMessage) and "reasoning_content" in msg.additional_kwargs:
            kwargs = {k: v for k, v in msg.additional_kwargs.items() if k != "reasoning_content"}
            msg = msg.model_copy(update={"additional_kwargs": kwargs})
        cleaned.append(msg)
    return cleaned


async def agent_node(state: AgentState) -> dict:
    max_iterations = get_settings().max_iterations
    tools = registry.get_many(state.get("active_tools", []))
    tools_exhausted = state.get("iterations", 0) >= max_iterations

    llm = get_agent_llm()
    if tools and not tools_exhausted:
        llm = llm.bind_tools(tools)

    system = SystemMessage(agent_system_prompt([t.name for t in tools], tools_exhausted))
    response = await llm.ainvoke([system, *_without_reasoning(state["messages"])])
    return {"messages": [response], "iterations": state.get("iterations", 0) + 1}
