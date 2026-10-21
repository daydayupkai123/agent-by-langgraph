"""Router 节点：识别意图，按「意图 → 工具」映射下发本轮可用工具子集。"""

import logging

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel

from app.agent.intents import DEFAULT_INTENT, INTENTS
from app.agent.prompts import router_system_prompt
from app.agent.state import AgentState
from app.llm import get_router_llm

logger = logging.getLogger(__name__)

ROUTER_CONTEXT_MESSAGES = 6
ROUTER_CONTEXT_CHARS = 300


class RouterDecision(BaseModel):
    intent: str


def _router_context(state: AgentState) -> str:
    """把最近几轮对话压成简短文本，让 Router 能理解“那再乘以 2 呢”这类追问。"""
    lines: list[str] = []
    for msg in state["messages"][-ROUTER_CONTEXT_MESSAGES:]:
        if isinstance(msg, HumanMessage):
            role = "用户"
        elif isinstance(msg, AIMessage) and msg.content:
            role = "助手"
        else:
            continue
        lines.append(f"{role}: {msg.text[:ROUTER_CONTEXT_CHARS]}")
    return "\n".join(lines)


async def router_node(state: AgentState) -> dict:
    intent = DEFAULT_INTENT
    try:
        llm = get_router_llm().with_structured_output(RouterDecision)
        decision = await llm.ainvoke(
            [
                SystemMessage(router_system_prompt()),
                HumanMessage(_router_context(state)),
            ]
        )
        if decision.intent in INTENTS:
            intent = decision.intent
        else:
            logger.warning("Router 返回未知意图 %r，回退到 %s", decision.intent, DEFAULT_INTENT)
    except Exception:
        logger.exception("Router 调用失败，回退到 %s", DEFAULT_INTENT)

    return {
        "intent": intent,
        "active_tools": INTENTS[intent].tools,
        "iterations": 0,
    }
