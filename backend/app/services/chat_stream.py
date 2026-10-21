"""把 LangGraph 的执行流转换为与传输无关的事件流，供 SSE 接口和命令行共用。

事件协议：route / reasoning / token / tool_call / tool_result / done / error
"""

import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, ToolMessage
from langgraph.graph.state import CompiledStateGraph

from app.agent import thread_config

logger = logging.getLogger(__name__)

# 只把这些节点里的 LLM token 推给前端（Router 的分类输出不展示）
STREAM_TOKEN_NODES = {"agent"}


@dataclass(frozen=True)
class AgentEvent:
    event: str
    data: dict = field(default_factory=dict)


def _message_events(msg: object, meta: dict) -> list[AgentEvent]:
    if meta.get("langgraph_node") not in STREAM_TOKEN_NODES or not isinstance(msg, AIMessageChunk):
        return []
    events: list[AgentEvent] = []
    reasoning = msg.additional_kwargs.get("reasoning_content")
    if reasoning:
        events.append(AgentEvent("reasoning", {"delta": reasoning}))
    if msg.text:
        events.append(AgentEvent("token", {"delta": msg.text}))
    return events


def _update_events(node: str, update: dict) -> list[AgentEvent]:
    if node == "router":
        return [AgentEvent("route", {"intent": update["intent"], "tools": update["active_tools"]})]

    if node == "agent":
        last = update["messages"][-1]
        if not isinstance(last, AIMessage):
            return []
        return [
            AgentEvent("tool_call", {"id": c["id"], "name": c["name"], "args": c["args"]})
            for c in last.tool_calls
        ]

    if node == "tools":
        return [
            AgentEvent(
                "tool_result",
                {
                    "id": tm.tool_call_id,
                    "name": tm.name,
                    "content": tm.text,
                    "status": "error" if tm.status == "error" else "done",
                },
            )
            for tm in update["messages"]
            if isinstance(tm, ToolMessage)
        ]

    return []


async def stream_chat(
    graph: CompiledStateGraph, thread_id: str, message: str
) -> AsyncIterator[AgentEvent]:
    inputs = {"messages": [HumanMessage(message)]}
    try:
        async for mode, chunk in graph.astream(
            inputs, thread_config(thread_id), stream_mode=["messages", "updates"]
        ):
            if mode == "messages":
                for ev in _message_events(*chunk):
                    yield ev
            elif mode == "updates":
                for node, update in chunk.items():
                    if update:
                        for ev in _update_events(node, update):
                            yield ev
        yield AgentEvent("done")
    except Exception as e:
        logger.exception("对话执行失败")
        yield AgentEvent("error", {"message": str(e) or e.__class__.__name__})
