import httpx
from fastapi import APIRouter

from app.agent.intents import INTENTS
from app.config import get_settings
from app.tools import registry

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/health")
async def health() -> dict:
    s = get_settings()
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(f"{s.ollama_base_url}/api/tags")
            resp.raise_for_status()
        ollama_ok = True
    except httpx.HTTPError:
        ollama_ok = False
    return {"ok": True, "ollama": ollama_ok}


@router.get("/meta")
async def meta() -> dict:
    s = get_settings()
    return {
        "agent_model": s.agent_model,
        "router_model": s.router_model,
        "max_iterations": s.max_iterations,
        "intents": [
            {"name": i.name, "description": i.description, "tools": i.tools}
            for i in INTENTS.values()
        ],
        "tools": [{"name": t.name, "description": t.description} for t in registry.all()],
    }
