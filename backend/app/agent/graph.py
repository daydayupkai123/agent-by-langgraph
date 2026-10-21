from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agent.edges import route_after_agent
from app.agent.nodes import agent_node, router_node, tools_node
from app.agent.state import AgentState


def thread_config(thread_id: str) -> RunnableConfig:
    return {"configurable": {"thread_id": thread_id}, "recursion_limit": 50}


def build_graph(checkpointer: BaseCheckpointSaver | None = None) -> CompiledStateGraph:
    """START → router → agent ⇄ tools → END"""
    builder = StateGraph(AgentState)

    builder.add_node("router", router_node)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tools_node)

    builder.add_edge(START, "router")
    builder.add_edge("router", "agent")
    builder.add_conditional_edges("agent", route_after_agent, {"tools": "tools", "end": END})
    builder.add_edge("tools", "agent")

    return builder.compile(checkpointer=checkpointer)
