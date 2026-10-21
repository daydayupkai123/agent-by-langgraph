import { useState } from 'react'
import type { ToolStatus } from '../types'

const STATUS_LABEL: Record<ToolStatus, string> = {
  running: '执行中',
  done: '完成',
  error: '失败',
}

interface Props {
  name: string
  args: Record<string, unknown>
  status: ToolStatus
  result?: string
}

export function ToolCallCard({ name, args, status, result }: Props) {
  const [open, setOpen] = useState(false)

  return (
    <div className={`tool-card ${status}`}>
      <button className="tool-header" onClick={() => setOpen((v) => !v)}>
        <span className="tool-icon">⚙</span>
        <code className="tool-name">{name}</code>
        <span className={`tool-status ${status}`}>{STATUS_LABEL[status]}</span>
        <span className="chevron">{open ? '▾' : '▸'}</span>
      </button>
      {open && (
        <div className="tool-body">
          <div className="tool-section-title">参数</div>
          <pre>{JSON.stringify(args, null, 2)}</pre>
          {result !== undefined && (
            <>
              <div className="tool-section-title">结果</div>
              <pre>{result}</pre>
            </>
          )}
        </div>
      )}
    </div>
  )
}
