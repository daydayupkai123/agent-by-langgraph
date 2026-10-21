import type { AssistantMessage, Part, StreamEvent } from '../types'

function appendText(parts: Part[], type: 'reasoning' | 'text', delta: string): Part[] {
  const last = parts.at(-1)
  if (last && last.type === type) {
    return [...parts.slice(0, -1), { ...last, text: last.text + delta }]
  }
  return [...parts, { type, text: delta }]
}

/** 把一条流式事件合并进当前的 assistant 消息（纯函数，便于测试和复用）。 */
export function applyEvent(msg: AssistantMessage, ev: StreamEvent): AssistantMessage {
  switch (ev.event) {
    case 'route':
      return { ...msg, route: ev.data }
    case 'reasoning':
      return { ...msg, parts: appendText(msg.parts, 'reasoning', ev.data.delta) }
    case 'token':
      return { ...msg, parts: appendText(msg.parts, 'text', ev.data.delta) }
    case 'tool_call':
      return {
        ...msg,
        parts: [...msg.parts, { type: 'tool', ...ev.data, status: 'running' }],
      }
    case 'tool_result':
      return {
        ...msg,
        parts: msg.parts.map((p) =>
          p.type === 'tool' && p.id === ev.data.id
            ? { ...p, status: ev.data.status, result: ev.data.content }
            : p,
        ),
      }
    case 'done':
      return { ...msg, status: 'done' }
    case 'error':
      return { ...msg, status: 'error', error: ev.data.message }
  }
}
