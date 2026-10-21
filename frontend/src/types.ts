export type ToolStatus = 'running' | 'done' | 'error'

export type Part =
  | { type: 'reasoning'; text: string }
  | { type: 'text'; text: string }
  | {
      type: 'tool'
      id: string
      name: string
      args: Record<string, unknown>
      status: ToolStatus
      result?: string
    }

export interface RouteInfo {
  intent: string
  tools: string[]
}

export interface UserMessage {
  id: string
  role: 'user'
  content: string
}

export interface AssistantMessage {
  id: string
  role: 'assistant'
  parts: Part[]
  route?: RouteInfo
  status?: 'streaming' | 'done' | 'error' | 'aborted'
  error?: string
}

export type ChatMessage = UserMessage | AssistantMessage

export interface Thread {
  id: string
  title: string
  updatedAt: number
}

export type StreamEvent =
  | { event: 'route'; data: RouteInfo }
  | { event: 'reasoning'; data: { delta: string } }
  | { event: 'token'; data: { delta: string } }
  | { event: 'tool_call'; data: { id: string; name: string; args: Record<string, unknown> } }
  | { event: 'tool_result'; data: { id: string; name: string; content: string; status: ToolStatus } }
  | { event: 'done'; data: Record<string, never> }
  | { event: 'error'; data: { message: string } }

export interface Meta {
  agent_model: string
  router_model: string
  max_iterations: number
  intents: { name: string; description: string; tools: string[] }[]
  tools: { name: string; description: string }[]
}
