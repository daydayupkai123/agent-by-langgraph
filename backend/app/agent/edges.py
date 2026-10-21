"""条件边：决定节点执行完后的下一步流向。"""

from langchain_core.messages import AIMessage

from app.agent.state import AgentState


def route_after_agent(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return "end"
