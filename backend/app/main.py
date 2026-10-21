from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent import build_graph
from app.api import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.memory import open_checkpointer

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with open_checkpointer() as checkpointer:
        app.state.graph = build_graph(checkpointer)
        yield


app = FastAPI(title="LangGraph Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
