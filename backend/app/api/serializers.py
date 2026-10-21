"""把 LangGraph 的消息转换成前端使用的结构。

前端的一条 assistant 消息由有序的 parts 组成（思考 / 文本 / 工具调用），
一次 ReAct 循环中多次 agent 输出与工具结果会合并到同一条 assistant 消息里。
"""

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, ToolMessage


def serialize_history(messages: list[AnyMessage]) -> list[dict]:
    result: list[dict] = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            result.append({"id": msg.id, "role": "user", "content": msg.text})
            continue

        if not result or result[-1]["role"] != "assistant":
            result.append({"id": msg.id, "role": "assistant", "parts": []})
        parts: list[dict] = result[-1]["parts"]

        if isinstance(msg, AIMessage):
            reasoning = msg.additional_kwargs.get("reasoning_content")
            if reasoning:
                parts.append({"type": "reasoning", "text": reasoning})
            if msg.text:
                parts.append({"type": "text", "text": msg.text})
            for call in msg.tool_calls:
                parts.append(
                    {
                        "type": "tool",
                        "id": call["id"],
                        "name": call["name"],
                        "args": call["args"],
                        "status": "running",
                    }
                )
        elif isinstance(msg, ToolMessage):
            for part in parts:
                if part["type"] == "tool" and part["id"] == msg.tool_call_id:
                    part["result"] = msg.text
                    part["status"] = "error" if msg.status == "error" else "done"
    return result
