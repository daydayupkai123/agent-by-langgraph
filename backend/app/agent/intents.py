from dataclasses import dataclass, field


@dataclass(frozen=True)
class Intent:
    name: str
    description: str
    tools: list[str] = field(default_factory=list)


# 「意图 → 工具」配置映射：Router 只输出意图标签，工具子集由这里决定
INTENTS: dict[str, Intent] = {
    i.name: i
    for i in [
        Intent(
            name="chat",
            description="闲聊、问候、常识问答、写作、翻译、解释概念等无需任何工具的请求",
        ),
        Intent(
            name="math",
            description="需要进行数值计算、公式求值、换算的请求",
            tools=["math_calculate"],
        ),
        Intent(
            name="datetime",
            description="询问当前时间、日期、星期，或计算日期间隔、倒计时等",
            tools=["datetime_now", "datetime_days_between", "math_calculate"],
        ),
        Intent(
            name="task",
            description="需要多个步骤、综合多种能力，或无法明确归入以上类别的复杂请求",
            tools=["math_calculate", "datetime_now", "datetime_days_between"],
        ),
    ]
}

DEFAULT_INTENT = "task"
