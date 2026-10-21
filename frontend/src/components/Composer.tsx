import { useState, type KeyboardEvent } from 'react'

interface Props {
  streaming: boolean
  disabled?: boolean
  onSend: (text: string) => void
  onStop: () => void
}

export function Composer({ streaming, disabled, onSend, onStop }: Props) {
  const [text, setText] = useState('')

  const submit = () => {
    const value = text.trim()
    if (!value || streaming || disabled) return
    onSend(value)
    setText('')
  }

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // 中文输入法组词时按回车不应发送
    if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className="composer">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={onKeyDown}
        placeholder="输入消息，Enter 发送，Shift + Enter 换行"
        rows={1}
        disabled={disabled}
      />
      {streaming ? (
        <button className="btn-stop" onClick={onStop}>
          停止
        </button>
      ) : (
        <button className="btn-send" onClick={submit} disabled={!text.trim() || disabled}>
          发送
        </button>
      )}
    </div>
  )
}
