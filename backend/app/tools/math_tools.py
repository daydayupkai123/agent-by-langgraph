import ast
import math
import operator

from langchain_core.tools import tool

_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCS = {
    "sqrt": math.sqrt,
    "abs": abs,
    "round": round,
    "log": math.log,
    "log10": math.log10,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
}
_CONSTS = {"pi": math.pi, "e": math.e}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id in _CONSTS:
        return _CONSTS[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        if isinstance(node.op, ast.Pow):
            exponent = _safe_eval(node.right)
            if abs(exponent) > 1000:
                raise ValueError("指数过大")
            return operator.pow(_safe_eval(node.left), exponent)
        return _BIN_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_safe_eval(node.operand))
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in _FUNCS
        and not node.keywords
    ):
        return _FUNCS[node.func.id](*(_safe_eval(a) for a in node.args))
    raise ValueError(f"不支持的表达式片段: {ast.dump(node)[:60]}")


@tool
def math_calculate(expression: str) -> str:
    """计算数学表达式并返回精确结果。支持 + - * / // % ** 括号，
    以及 sqrt/abs/round/log/log10/sin/cos/tan 函数和常量 pi、e。
    例如: "(3 + 5) * 2 ** 3"、"sqrt(2) * pi"。涉及数值计算时必须使用本工具，不要心算。
    """
    try:
        result = _safe_eval(ast.parse(expression, mode="eval"))
    except ZeroDivisionError:
        return "错误：除数不能为 0"
    except (ValueError, SyntaxError, TypeError) as e:
        return f"错误：无法计算该表达式（{e}）"
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    return f"{expression} = {result}"


MATH_TOOLS = [math_calculate]
