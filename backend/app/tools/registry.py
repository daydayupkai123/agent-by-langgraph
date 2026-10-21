from langchain_core.tools import BaseTool


class ToolRegistry:
    """全局工具注册表。

    Runtime 持有全部工具，模型每轮只能看到 Router 下发的子集；
    工具名采用 `命名空间_动作` 的形式，避免重名与语义混淆。
    """

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, *tools: BaseTool) -> None:
        for tool in tools:
            if tool.name in self._tools:
                raise ValueError(f"工具重名: {tool.name}")
            self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def get_many(self, names: list[str]) -> list[BaseTool]:
        return [self._tools[n] for n in names if n in self._tools]

    def names(self) -> list[str]:
        return list(self._tools)

    def all(self) -> list[BaseTool]:
        return list(self._tools.values())


registry = ToolRegistry()
