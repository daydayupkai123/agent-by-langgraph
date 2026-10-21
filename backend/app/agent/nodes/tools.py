"""Tools 节点：校验工具白名单并并发执行，把结果作为 Observation 写回消息。"""

import asyncio
import logging

from langchain_core.messages import ToolMessage
from langchain_core.messages.tool import ToolCall

from app.agent.state import AgentState
from app.tools import registry

logger = logging.getLogger(__name__)


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
