from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_base_url: str = "http://localhost:11434"

    # 主 Agent 模型：负责 ReAct 推理与工具调用
    agent_model: str = "qcwind/qwen3-8b-instruct-Q4-K-M:latest"
    agent_temperature: float = 0.6
    # 是否开启模型的 thinking（仅对支持 thinking 的模型生效）
    agent_reasoning: bool = True

    # Router 模型：只做意图分类，可换成更小更快的模型
    router_model: str = "qcwind/qwen3-8b-instruct-Q4-K-M:latest"

    # ReAct 循环的硬上限（一次用户提问内 agent 节点最多执行的次数）
    max_iterations: int = 6

    checkpoint_db: Path = BACKEND_DIR / "data" / "checkpoints.sqlite"

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
