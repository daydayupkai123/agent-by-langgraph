from datetime import datetime
from zoneinfo import ZoneInfo

from app.agent.intents import INTENTS


def router_system_prompt() -> str:
    intent_lines = "\n".join(f"- {i.name}: {i.description}" for i in INTENTS.values())
    return f"""你是一个意图分类器。根据对话上下文，判断【用户最新一条消息】属于哪个意图。

可选意图：
{intent_lines}

只输出 JSON，格式为 {{"intent": "<意图名>"}}，不要输出任何其他内容。"""


def agent_system_prompt(tool_names: list[str], tools_exhausted: bool) -> str:
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    lines = [
        "你是一个可靠、专业的中文智能助手。",
        f"- 今天是 {now:%Y-%m-%d}（星期{'一二三四五六日'[now.weekday()]}）。",
        "- 回答准确、简洁、有条理，不确定的内容要明确说明，不要编造。",
    ]
    if tools_exhausted:
        lines.append("- 已达到本轮工具调用上限，请基于已有信息直接给出最终答案。")
    elif tool_names:
        lines.append(f"- 你可以使用以下工具：{', '.join(tool_names)}。")
        lines.append("- 需要计算、查询实时信息时必须调用工具，并以工具返回结果为准，不要自行猜测结果。")
        lines.append("- 如果某个工具的参数依赖另一个工具的返回结果，必须先调用前者、拿到结果后再调用后者，不要臆造参数。")
        lines.append("- 拿到足够信息后，直接给出最终答案。")
    else:
        lines.append("- 本轮不需要使用工具，直接回答即可。")
    return "\n".join(lines)
