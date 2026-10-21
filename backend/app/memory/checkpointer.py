"""会话短期记忆的持久化（Checkpoint）。切换 Postgres 等存储时只需改这里。"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.core.config import get_settings


@asynccontextmanager
async def open_checkpointer() -> AsyncIterator[BaseCheckpointSaver]:
    db_path = get_settings().checkpoint_db
    db_path.parent.mkdir(parents=True, exist_ok=True)
    async with AsyncSqliteSaver.from_conn_string(str(db_path)) as saver:
        yield saver
