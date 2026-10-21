import type { ChatMessage, Meta, StreamEvent } from '../types'
import { readSSE } from './sse'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, init)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json() as Promise<T>
}

export async function* streamChat(
  threadId: string,
  message: string,
  signal: AbortSignal,
): AsyncGenerator<StreamEvent> {
  const res = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ thread_id: threadId, message }),
    signal,
  })
  if (!res.ok) throw new Error(`请求失败：${res.status} ${res.statusText}`)

  for await (const raw of readSSE(res)) {
    yield { event: raw.event, data: JSON.parse(raw.data) } as StreamEvent
  }
}

export async function fetchHistory(threadId: string): Promise<ChatMessage[]> {
  const data = await request<{ messages: ChatMessage[] }>(
    `/api/threads/${encodeURIComponent(threadId)}/messages`,
  )
  return data.messages.map((m) => (m.role === 'assistant' ? { ...m, status: 'done' } : m))
}

export function deleteThread(threadId: string): Promise<{ ok: boolean }> {
  return request(`/api/threads/${encodeURIComponent(threadId)}`, { method: 'DELETE' })
}

export function fetchMeta(): Promise<Meta> {
  return request('/api/meta')
}

export function fetchHealth(): Promise<{ ok: boolean; ollama: boolean }> {
  return request('/api/health')
}
