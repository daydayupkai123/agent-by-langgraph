from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agent.nodes import agent_node, route_after_agent, router_node, tools_node
from app.agent.state import AgentState


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
