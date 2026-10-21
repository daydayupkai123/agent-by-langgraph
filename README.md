# LangGraph Agent

基于 **LangGraph + Ollama 本地模型** 的智能体基础工程，配套 React 对话前端。
作为垂直化、私有化 Agent 的底座，后续在此之上迭代工具、记忆、Skills、RAG、HITL、PlanView 等能力。

## 架构

```
用户输入
   │
   ▼
┌────────┐   意图标签    ┌──────────────────┐
│ router │ ───────────▶ │ 意图→工具 配置映射 │ ──▶ 本轮可用工具子集写入 State
└────────┘              └──────────────────┘
   │
   ▼
┌────────┐  tool_calls  ┌────────┐
│ agent  │ ───────────▶ │ tools  │   ReAct 循环（原生 Tool Calling）
│ (LLM)  │ ◀─────────── │        │   Runtime 控制循环 + 最大轮次硬限制
└────────┘  Observation └────────┘
   │ 无 tool_calls
   ▼
  END        ── 全程状态由 Checkpoint(SQLite) 按 thread_id 持久化
```

## 后端目录结构

依赖方向自上而下：`api → services → agent → tools / llm / memory → core`，下层不引用上层。

```
backend/
├── app/
│   ├── main.py                 # 应用入口：生命周期、中间件、挂载路由
│   ├── core/                   # 基础设施
│   │   ├── config.py           #   配置（读取 .env）
│   │   └── logging.py          #   日志
│   ├── llm/                    # 模型接入
│   │   └── factory.py          #   ChatOllama 实例工厂（Agent / Router 模型）
│   ├── agent/                  # LangGraph 智能体核心
│   │   ├── state.py            #   State 定义
│   │   ├── intents.py          #   「意图 → 工具」配置映射
│   │   ├── prompts.py          #   提示词
│   │   ├── nodes/              #   节点（每个节点一个文件）
│   │   │   ├── router.py       #     意图识别、下发工具子集
│   │   │   ├── agent.py        #     ReAct 单次推理
│   │   │   └── tools.py        #     工具白名单校验 + 并发执行
│   │   ├── edges.py            #   条件边（路由函数）
│   │   └── graph.py            #   组装 Node + Edge，编译图
│   ├── tools/                  # 工具（按命名空间分文件）
│   │   ├── registry.py         #   全局工具注册表
│   │   ├── math_tools.py       #   math_*
│   │   └── datetime_tools.py   #   datetime_*
│   ├── memory/                 # 记忆与持久化
│   │   └── checkpointer.py     #   会话 Checkpoint（SQLite）
│   ├── services/               # 业务逻辑（与传输协议无关）
│   │   ├── chat_stream.py      #   LangGraph 流 → 事件流（SSE 与 CLI 共用）
│   │   └── threads.py          #   会话历史读取 / 删除 / 序列化
│   ├── schemas/                # 请求 / 响应模型
│   │   └── chat.py
│   └── api/                    # HTTP 层（只做参数解析与协议转换）
│       ├── deps.py             #   依赖注入（获取 graph）
│       └── routes/
│           ├── chat.py         #   POST /api/chat/stream
│           ├── threads.py      #   /api/threads/*
│           └── system.py       #   /api/health、/api/meta
├── scripts/cli_chat.py         # 命令行调试入口
└── tests/                      # 单元测试
```

## 快速开始

前置条件：Python 3.12+、[uv](https://docs.astral.sh/uv/)、Node.js 20+、已运行的 Ollama，并拉取一个支持 tools 的模型（默认 `qcwind/qwen3-8b-instruct-Q4-K-M`）。

```powershell
# 后端（http://127.0.0.1:8000，接口文档见 /docs）
cd backend
uv sync
copy .env.example .env      # 可选，按需修改模型等配置
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# 前端（http://localhost:5173，/api 自动代理到后端）
cd frontend
npm install
npm run dev
```

不启动 Web 服务、直接在命令行调试图：

```powershell
cd backend
uv run python -m scripts.cli_chat                       # 交互模式
uv run python -m scripts.cli_chat "123*456 等于多少"     # 单次提问
uv run pytest                                           # 运行单元测试
```

## 接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/chat/stream` | 发送消息，SSE 流式返回，body：`{thread_id, message}` |
| GET | `/api/threads/{thread_id}/messages` | 从 Checkpoint 读取会话历史 |
| DELETE | `/api/threads/{thread_id}` | 删除会话 |
| GET | `/api/meta` | 模型、意图、工具清单 |
| GET | `/api/health` | 服务与 Ollama 连通性 |

SSE 事件协议：

| event | data | 含义 |
| --- | --- | --- |
| `route` | `{intent, tools}` | Router 识别的意图与下发的工具子集 |
| `reasoning` | `{delta}` | 模型思考过程增量 |
| `token` | `{delta}` | 回答文本增量 |
| `tool_call` | `{id, name, args}` | 模型发起工具调用 |
| `tool_result` | `{id, name, content, status}` | 工具执行结果 |
| `done` / `error` | `{}` / `{message}` | 结束 / 出错 |

## 扩展指南

**新增工具**：在 `backend/app/tools/` 下按命名空间新建或复用 `xxx_tools.py`，用 `@tool` 定义函数（命名用 `命名空间_动作`，docstring 写清楚用途和边界），
在 `backend/app/tools/__init__.py` 中 `registry.register(...)`，再到 `backend/app/agent/intents.py` 把工具挂到对应意图下。

**新增节点**：在 `backend/app/agent/nodes/` 下新建文件，在 `graph.py` 中注册节点和边；如需推送给前端，在 `services/chat_stream.py` 的 `_update_events` 中补充事件。

**新增意图**：在 `INTENTS` 中添加 `Intent(name, description, tools)`，Router 的提示词会自动包含它；
前端可在 `frontend/src/components/AssistantMessageView.tsx` 的 `INTENT_LABEL` 中补中文名。

## 路线图

- [x] Router + LangGraph 状态机 + ReAct（Tool Calling）+ 最大轮次限制
- [x] SQLite Checkpoint 会话持久化、SSE 流式输出、思考过程/工具调用可视化
- [ ] 记忆：会话摘要压缩（token 阈值触发）、跨会话长期记忆
- [ ] RAG：向量检索封装为独立 Tool，按需召回
- [ ] HITL：高危工具执行前 `interrupt` 暂停，前端审批卡片 + resume 接口
- [ ] PlanView：State 中维护结构化 plan，前端渲染任务面板
- [ ] Skills / 外部工具（HTTP、OpenAPI、数据库、MCP）、动态 Router
