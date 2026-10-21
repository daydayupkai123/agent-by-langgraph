import asyncio
import logging

from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.messages.tool import ToolCall
from pydantic import BaseModel

from app.agent.intents import DEFAULT_INTENT, INTENTS
from app.agent.prompts import agent_system_prompt, router_system_prompt
from app.agent.state import AgentState
from app.config import get_settings
from app.llm import get_agent_llm, get_router_llm
from app.tools import registry

logger = logging.getLogger(__name__)

ROUTER_CONTEXT_MESSAGES = 6
ROUTER_CONTEXT_CHARS = 300


class RouterDecision(BaseModel):
    intent: str


def _router_context(state: AgentState) -> str:
    """把最近几轮对话压成简短文本，让 Router 能理解“那再乘以 2 呢”这类追问。"""
    lines: list[str] = []
    for msg in state["messages"][-ROUTER_CONTEXT_MESSAGES:]:
        if isinstance(msg, HumanMessage):
            role = "用户"
        elif isinstance(msg, AIMessage) and msg.content:
            role = "助手"
        else:
            continue
        lines.append(f"{role}: {msg.text[:ROUTER_CONTEXT_CHARS]}")
    return "\n".join(lines)


async def router_node(state: AgentState) -> dict:
    intent = DEFAULT_INTENT
    try:
        llm = get_router_llm().with_structured_output(RouterDecision)
        decision = await llm.ainvoke(
            [
                SystemMessage(router_system_prompt()),
                HumanMessage(_router_context(state)),
            ]
        )
        if decision.intent in INTENTS:
            intent = decision.intent
        else:
            logger.warning("Router 返回未知意图 %r，回退到 %s", decision.intent, DEFAULT_INTENT)
    except Exception:
        logger.exception("Router 调用失败，回退到 %s", DEFAULT_INTENT)

    return {
        "intent": intent,
        "active_tools": INTENTS[intent].tools,
        "iterations": 0,
    }


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


async def _run_tool_call(call: ToolCall, allowed: set[str]) -> ToolMessage:
    name = call["name"]
    if name not in allowed:
        return ToolMessage(
            content=f"错误：工具 {name} 在当前任务中不可用。",
            tool_call_id=call["id"],
            name=name,
            status="error",
        )
    tool = registry.get(name)
    try:
        output = await tool.ainvoke(call["args"])
        return ToolMessage(content=str(output), tool_call_id=call["id"], name=name)
    except Exception as e:
        logger.exception("工具 %s 执行失败", name)
        return ToolMessage(
            content=f"错误：工具执行失败（{e}）",
            tool_call_id=call["id"],
            name=name,
            status="error",
        )


async def tools_node(state: AgentState) -> dict:
    last = state["messages"][-1]
    allowed = set(state.get("active_tools", []))
    results = await asyncio.gather(*(_run_tool_call(c, allowed) for c in last.tool_calls))
    return {"messages": list(results)}


def route_after_agent(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return "end"
