from fastapi import APIRouter

from app.api.deps import GraphDep
from app.services import threads as thread_service

router = APIRouter(prefix="/threads", tags=["threads"])


@router.get("/{thread_id}/messages")
async def get_thread_messages(thread_id: str, graph: GraphDep) -> dict:
    messages = await thread_service.get_thread_history(graph, thread_id)
    return {"thread_id": thread_id, "messages": messages}


@router.delete("/{thread_id}")
async def delete_thread(thread_id: str, graph: GraphDep) -> dict:
    await thread_service.delete_thread(graph, thread_id)
    return {"ok": True}
