import { useState } from 'react'

export function ReasoningBlock({ text, active }: { text: string; active: boolean }) {
  // 用户未手动切换时：思考中自动展开，结束后自动收起
  const [manualOpen, setManualOpen] = useState<boolean | null>(null)
  const open = manualOpen ?? active

  return (
    <div className={`reasoning ${open ? 'open' : ''}`}>
      <button className="reasoning-toggle" onClick={() => setManualOpen(!open)}>
        <span className={`dot ${active ? 'pulse' : ''}`} />
        {active ? '思考中…' : '思考过程'}
        <span className="chevron">{open ? '▾' : '▸'}</span>
      </button>
      {open && <div className="reasoning-body">{text.trim()}</div>}
    </div>
  )
}
