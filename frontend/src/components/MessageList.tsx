import { useEffect, useRef } from 'react'
import type { ChatMessage } from '../types'
import { AssistantMessageView } from './AssistantMessageView'

const STICK_THRESHOLD = 120

export function MessageList({ messages }: { messages: ChatMessage[] }) {
  const containerRef = useRef<HTMLDivElement>(null)
  const stickRef = useRef(true)

  const onScroll = () => {
    const el = containerRef.current
    if (!el) return
    stickRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < STICK_THRESHOLD
  }

  useEffect(() => {
    const el = containerRef.current
    if (el && stickRef.current) el.scrollTop = el.scrollHeight
  }, [messages])

  return (
    <div className="message-list" ref={containerRef} onScroll={onScroll}>
      <div className="message-list-inner">
        {messages.map((m) =>
          m.role === 'user' ? (
            <div key={m.id} className="message user">
              <div className="bubble">{m.content}</div>
            </div>
          ) : (
            <AssistantMessageView key={m.id} message={m} />
          ),
        )}
      </div>
    </div>
  )
}
