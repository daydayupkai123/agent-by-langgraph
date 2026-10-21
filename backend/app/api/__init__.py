from fastapi import APIRouter

from app.api.routes import chat, system, threads

api_router = APIRouter(prefix="/api")
api_router.include_router(chat.router)
api_router.include_router(threads.router)
api_router.include_router(system.router)

__all__ = ["api_router"]
