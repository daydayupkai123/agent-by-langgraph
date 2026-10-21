import { useChat } from '../chat/useChat'
import { Composer } from './Composer'
import { EmptyState } from './EmptyState'
import { MessageList } from './MessageList'

interface Props {
  threadId: string
  hasHistory: boolean
  onSend: (threadId: string, text: string) => void
}

export function ChatPanel({ threadId, hasHistory, onSend }: Props) {
  const { messages, loading, streaming, send, stop } = useChat(threadId, hasHistory)

  const handleSend = (text: string) => {
    onSend(threadId, text)
    void send(text)
  }

  return (
    <>
      {messages.length === 0 && !loading ? (
        <EmptyState onPick={handleSend} />
      ) : (
        <MessageList messages={messages} />
      )}
      <div className="composer-wrap">
        <Composer streaming={streaming} onSend={handleSend} onStop={stop} />
      </div>
    </>
  )
}
