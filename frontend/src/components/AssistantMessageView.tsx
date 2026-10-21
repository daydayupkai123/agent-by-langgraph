import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { AssistantMessage } from '../types'
import { ReasoningBlock } from './ReasoningBlock'
import { ToolCallCard } from './ToolCallCard'

const INTENT_LABEL: Record<string, string> = {
  chat: '闲聊问答',
  math: '数学计算',
  datetime: '时间日期',
  task: '综合任务',
}

export function AssistantMessageView({ message }: { message: AssistantMessage }) {
  const { parts, route, status, error } = message
  const streaming = status === 'streaming'

  return (
    <div className="message assistant">
      <div className="avatar">AI</div>
      <div className="message-content">
        {route && (
          <div className="route-badge" title={`可用工具：${route.tools.join(', ') || '无'}`}>
            <span className="route-intent">{INTENT_LABEL[route.intent] ?? route.intent}</span>
            <span className="route-tools">
              {route.tools.length ? `${route.tools.length} 个工具可用` : '无需工具'}
            </span>
          </div>
        )}

        {parts.map((part, i) => {
          const isLast = i === parts.length - 1
          switch (part.type) {
            case 'reasoning':
              return <ReasoningBlock key={i} text={part.text} active={streaming && isLast} />
            case 'text':
              return (
                <div key={i} className="markdown">
                  <Markdown remarkPlugins={[remarkGfm]}>{part.text}</Markdown>
                </div>
              )
            case 'tool':
              return <ToolCallCard key={part.id} {...part} />
          }
        })}

        {streaming && parts.length === 0 && (
          <div className="typing">
            <span />
            <span />
            <span />
          </div>
        )}
        {status === 'aborted' && <div className="message-note">已停止生成</div>}
        {status === 'error' && <div className="message-error">出错了：{error}</div>}
      </div>
    </div>
  )
}
