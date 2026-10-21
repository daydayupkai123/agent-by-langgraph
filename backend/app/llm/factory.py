from functools import lru_cache

from langchain_ollama import ChatOllama

from app.core.config import get_settings


@lru_cache
def get_agent_llm() -> ChatOllama:
    s = get_settings()
    return ChatOllama(
        model=s.agent_model,
        base_url=s.ollama_base_url,
        temperature=s.agent_temperature,
        reasoning=s.agent_reasoning,
    )


@lru_cache
def get_router_llm() -> ChatOllama:
    s = get_settings()
    return ChatOllama(
        model=s.router_model,
        base_url=s.ollama_base_url,
        temperature=0,
        reasoning=False,
    )
