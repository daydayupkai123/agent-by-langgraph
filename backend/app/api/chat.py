import json
import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, Request
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, ToolMessage
from langgraph.graph.state import CompiledStateGraph
from sse_starlette.sse import EventSourceResponse

from app.api.schemas import ChatRequest
from app.api.serializers import serialize_history

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])

# 只把这些节点里的 LLM token 推给前端（Router 的分类输出不展示）
STREAM_TOKEN_NODES = {"agent"}


def _graph(request: Request) -> CompiledStateGraph:
    return request.app.state.graph


def _thread_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}, "recursion_limit": 50}


def _sse(event: str, data: dict) -> dict:
    return {"event": event, "data": json.dumps(data, ensure_ascii=False)}


async def _stream_events(graph: CompiledStateGraph, req: ChatRequest) -> AsyncIterator[dict]:
    """把 LangGraph 的流转换为前端事件协议：

    route / reasoning / token / tool_call / tool_result / done / error
    """
    inputs = {"messages": [HumanMessage(req.message)]}
    try:
        async for mode, chunk in graph.astream(
            inputs,
            _thread_config(req.thread_id),
            stream_mode=["messages", "updates"],
        ):
            if mode == "messages":
                msg, meta = chunk
                if meta.get("langgraph_node") not in STREAM_TOKEN_NODES:
                    continue
                if not isinstance(msg, AIMessageChunk):
                    continue
                reasoning = msg.additional_kwargs.get("reasoning_content")
                if reasoning:
                    yield _sse("reasoning", {"delta": reasoning})
                if msg.text:
                    yield _sse("token", {"delta": msg.text})

            elif mode == "updates":
                for node, update in chunk.items():
                    if not update:
                        continue
                    if node == "router":
                        yield _sse(
                            "route",
                            {"intent": update["intent"], "tools": update["active_tools"]},
                        )
                    elif node == "agent":
                        last = update["messages"][-1]
                        if isinstance(last, AIMessage):
                            for call in last.tool_calls:
                                yield _sse(
                                    "tool_call",
                                    {"id": call["id"], "name": call["name"], "args": call["args"]},
                                )
                    elif node == "tools":
                        for tm in update["messages"]:
                            if isinstance(tm, ToolMessage):
                                yield _sse(
                                    "tool_result",
                                    {
                                        "id": tm.tool_call_id,
                                        "name": tm.name,
                                        "content": tm.text,
                                        "status": "error" if tm.status == "error" else "done",
                                    },
                                )
        yield _sse("done", {})
    except Exception as e:
        logger.exception("对话执行失败")
        yield _sse("error", {"message": str(e) or e.__class__.__name__})


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest, request: Request) -> EventSourceResponse:
    return EventSourceResponse(_stream_events(_graph(request), req), ping=15)


@router.get("/threads/{thread_id}/messages")
async def get_thread_messages(thread_id: str, request: Request) -> dict:
    snapshot = await _graph(request).aget_state(_thread_config(thread_id))
    messages = snapshot.values.get("messages", []) if snapshot.values else []
    return {"thread_id": thread_id, "messages": serialize_history(messages)}


@router.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str, request: Request) -> dict:
    await _graph(request).checkpointer.adelete_thread(thread_id)
    return {"ok": True}
