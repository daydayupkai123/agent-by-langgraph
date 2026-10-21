from app.tools import registry
from app.tools.datetime_tools import datetime_days_between
from app.tools.math_tools import math_calculate


def test_math_calculate_basic():
    assert math_calculate.invoke({"expression": "(1234 + 5678) * 3.5"}) == "(1234 + 5678) * 3.5 = 24192"


def test_math_calculate_rejects_unsafe_expression():
    assert math_calculate.invoke({"expression": "__import__('os')"}).startswith("错误")


def test_math_calculate_division_by_zero():
    assert math_calculate.invoke({"expression": "1 / 0"}) == "错误：除数不能为 0"


def test_datetime_days_between():
    result = datetime_days_between.invoke({"start_date": "2026-10-21", "end_date": "2027-01-01"})
    assert "72 天" in result


def test_registry_contains_builtin_tools():
    assert {"math_calculate", "datetime_now", "datetime_days_between"} <= set(registry.names())
