from app.tools.datetime_tools import DATETIME_TOOLS
from app.tools.math_tools import MATH_TOOLS
from app.tools.registry import ToolRegistry, registry

registry.register(*MATH_TOOLS, *DATETIME_TOOLS)

__all__ = ["ToolRegistry", "registry"]
