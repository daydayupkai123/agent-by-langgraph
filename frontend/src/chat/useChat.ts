import { useCallback, useEffect, useRef, useState } from 'react'
import { fetchHistory, streamChat } from '../api/client'
import type { AssistantMessage, ChatMessage } from '../types'
import { applyEvent } from './applyEvent'

/** 单个会话的消息状态。组件以 threadId 作为 key 挂载，切换会话即重建。 */
export function useChat(threadId: string, hasHistory: boolean) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(hasHistory)
  const [streaming, setStreaming] = useState(false)
  const abortRef = useRef<AbortController | null>(null)
  const shouldLoadRef = useRef(hasHistory)

  useEffect(() => {
    if (!shouldLoadRef.current) return
    let cancelled = false
    fetchHistory(threadId)
      .then((history) => !cancelled && setMessages(history))
      .catch(() => undefined)
      .finally(() => !cancelled && setLoading(false))
    return () => {
      cancelled = true
    }
  }, [threadId])

  useEffect(() => () => abortRef.current?.abort(), [])

  const send = useCallback(
    async (text: string) => {
      const controller = new AbortController()
      abortRef.current = controller
      const assistantId = crypto.randomUUID()

      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: 'user', content: text },
        { id: assistantId, role: 'assistant', parts: [], status: 'streaming' },
      ])
      setStreaming(true)

      const update = (fn: (m: AssistantMessage) => AssistantMessage) => {
        if (controller.signal.aborted) return
        setMessages((prev) =>
          prev.map((m) => (m.id === assistantId && m.role === 'assistant' ? fn(m) : m)),
        )
      }

      try {
        for await (const ev of streamChat(threadId, text, controller.signal)) {
          update((m) => applyEvent(m, ev))
        }
        update((m) => (m.status === 'streaming' ? { ...m, status: 'done' } : m))
      } catch (e) {
        update((m) => ({ ...m, status: 'error', error: e instanceof Error ? e.message : String(e) }))
      } finally {
        if (abortRef.current === controller) {
          abortRef.current = null
          setStreaming(false)
        }
      }
    },
    [threadId],
  )

  const stop = useCallback(() => {
    if (!abortRef.current) return
    abortRef.current.abort()
    abortRef.current = null
    setStreaming(false)
    setMessages((prev) =>
      prev.map((m) =>
        m.role === 'assistant' && m.status === 'streaming' ? { ...m, status: 'aborted' } : m,
      ),
    )
  }, [])

  return { messages, loading, streaming, send, stop }
}
