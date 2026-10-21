from langchain_core.messages import AIMessage

from app.agent.edges import route_after_agent


def test_route_to_tools_when_tool_calls_present():
    msg = AIMessage("", tool_calls=[{"id": "1", "name": "math_calculate", "args": {}}])
    assert route_after_agent({"messages": [msg]}) == "tools"


def test_route_to_end_without_tool_calls():
    assert route_after_agent({"messages": [AIMessage("done")]}) == "end"
