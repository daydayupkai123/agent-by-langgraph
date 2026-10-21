from app.tools.builtin import BUILTIN_TOOLS
from app.tools.registry import ToolRegistry, registry

registry.register(*BUILTIN_TOOLS)

__all__ = ["ToolRegistry", "registry"]
