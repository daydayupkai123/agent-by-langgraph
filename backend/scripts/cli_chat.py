"""命令行调试入口：不启动 Web 服务，直接跑 LangGraph 图并打印事件流。

用法：
    uv run python -m scripts.cli_chat                   # 交互模式
    uv run python -m scripts.cli_chat "123*456 等于多少"  # 单次提问
"""

import asyncio
import sys
import uuid

from langgraph.checkpoint.memory import InMemorySaver

from app.agent import build_graph
from app.services.chat_stream import stream_chat

DIM, CYAN, YELLOW, GREEN, RED, RESET = (
    "\033[2m",
    "\033[36m",
    "\033[33m",
    "\033[32m",
    "\033[31m",
    "\033[0m",
)


async def ask(graph, thread_id: str, text: str) -> None:
    in_reasoning = False
    async for ev in stream_chat(graph, thread_id, text):
        if ev.event == "reasoning":
            if not in_reasoning:
                print(f"\n{DIM}[思考] ", end="")
                in_reasoning = True
            print(ev.data["delta"], end="", flush=True)
            continue

        if in_reasoning:
            print(RESET)
            in_reasoning = False

        match ev.event:
            case "token":
                print(ev.data["delta"], end="", flush=True)
            case "route":
                print(f"{CYAN}[router] intent={ev.data['intent']} tools={ev.data['tools']}{RESET}")
            case "tool_call":
                print(f"\n{YELLOW}[tool_call] {ev.data['name']}({ev.data['args']}){RESET}")
            case "tool_result":
                print(f"{GREEN}[tool_result] {ev.data['name']} -> {ev.data['content']}{RESET}")
            case "error":
                print(f"{RED}[error] {ev.data['message']}{RESET}")
    print(RESET)


async def main() -> None:
    graph = build_graph(InMemorySaver())
    thread_id = str(uuid.uuid4())
    if len(sys.argv) > 1:
        for question in sys.argv[1:]:
            print(f"\n>>> {question}")
            await ask(graph, thread_id, question)
        return
    while True:
        try:
            text = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text:
            await ask(graph, thread_id, text)


if __name__ == "__main__":
    asyncio.run(main())
