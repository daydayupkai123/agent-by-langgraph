import json
from collections.abc import AsyncIterator

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.api.deps import GraphDep
from app.schemas.chat import ChatRequest
from app.services.chat_stream import AgentEvent, stream_chat

router = APIRouter(prefix="/chat", tags=["chat"])


async def _to_sse(events: AsyncIterator[AgentEvent]) -> AsyncIterator[dict]:
    async for ev in events:
        yield {"event": ev.event, "data": json.dumps(ev.data, ensure_ascii=False)}


@router.post("/stream")
async def chat_stream(req: ChatRequest, graph: GraphDep) -> EventSourceResponse:
    return EventSourceResponse(_to_sse(stream_chat(graph, req.thread_id, req.message)), ping=15)
