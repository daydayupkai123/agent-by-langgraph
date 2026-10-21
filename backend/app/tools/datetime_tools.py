from datetime import date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from langchain_core.tools import tool


@tool
def datetime_now(timezone: str = "Asia/Shanghai") -> str:
    """获取当前的日期、时间和星期。timezone 为 IANA 时区名，默认 Asia/Shanghai。"""
    try:
        tz = ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        return f"错误：未知时区 {timezone}"
    now = datetime.now(tz)
    weekday = "一二三四五六日"[now.weekday()]
    return f"{now:%Y-%m-%d %H:%M:%S}（星期{weekday}，时区 {timezone}）"


@tool
def datetime_days_between(start_date: str, end_date: str) -> str:
    """计算两个日期之间相差的天数。日期格式为 YYYY-MM-DD，结果为 end_date - start_date。"""
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        return "错误：日期格式应为 YYYY-MM-DD"
    return f"从 {start} 到 {end} 相差 {(end - start).days} 天"


DATETIME_TOOLS = [datetime_now, datetime_days_between]
