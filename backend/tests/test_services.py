from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, ToolMessage

from app.services.chat_stream import AgentEvent, _message_events, _update_events
from app.services.threads import serialize_history

TOOL_CALL = {"id": "call-1", "name": "math_calculate", "args": {"expression": "2 ** 10"}}


def test_message_events_only_stream_agent_node():
    chunk = AIMessageChunk("hi", additional_kwargs={"reasoning_content": "thinking"})
    assert _message_events(chunk, {"langgraph_node": "router"}) == []
    assert _message_events(chunk, {"langgraph_node": "agent"}) == [
        AgentEvent("reasoning", {"delta": "thinking"}),
        AgentEvent("token", {"delta": "hi"}),
    ]


def test_update_events_for_each_node():
    assert _update_events("router", {"intent": "math", "active_tools": ["math_calculate"]}) == [
        AgentEvent("route", {"intent": "math", "tools": ["math_calculate"]})
    ]
    assert _update_events("agent", {"messages": [AIMessage("", tool_calls=[TOOL_CALL])]}) == [
        AgentEvent("tool_call", TOOL_CALL)
    ]
    tool_msg = ToolMessage("2 ** 10 = 1024", tool_call_id="call-1", name="math_calculate")
    assert _update_events("tools", {"messages": [tool_msg]}) == [
        AgentEvent(
            "tool_result",
            {"id": "call-1", "name": "math_calculate", "content": "2 ** 10 = 1024", "status": "done"},
        )
    ]


def test_serialize_history_groups_react_steps_into_one_assistant_message():
    history = serialize_history(
        [
            HumanMessage("2 的 10 次方", id="h1"),
            AIMessage("", id="a1", tool_calls=[TOOL_CALL], additional_kwargs={"reasoning_content": "想一想"}),
            ToolMessage("2 ** 10 = 1024", tool_call_id="call-1", name="math_calculate"),
            AIMessage("结果是 1024", id="a2"),
        ]
    )
    assert [m["role"] for m in history] == ["user", "assistant"]
    parts = history[1]["parts"]
    assert [p["type"] for p in parts] == ["reasoning", "tool", "text"]
    assert parts[1]["status"] == "done"
    assert parts[1]["result"] == "2 ** 10 = 1024"
