import type { Thread } from '../types'

interface Props {
  threads: Thread[]
  activeId: string | null
  onSelect: (id: string) => void
  onNew: () => void
  onDelete: (id: string) => void
}

export function Sidebar({ threads, activeId, onSelect, onNew, onDelete }: Props) {
  return (
    <aside className="sidebar">
      <div className="brand">LangGraph Agent</div>
      <button className="btn-new" onClick={onNew}>
        + 新对话
      </button>
      <nav className="thread-list">
        {threads.length === 0 && <div className="thread-empty">暂无会话</div>}
        {threads.map((t) => (
          <div
            key={t.id}
            className={`thread-item ${t.id === activeId ? 'active' : ''}`}
            onClick={() => onSelect(t.id)}
          >
            <span className="thread-title">{t.title}</span>
            <button
              className="thread-delete"
              title="删除会话"
              onClick={(e) => {
                e.stopPropagation()
                onDelete(t.id)
              }}
            >
              ×
            </button>
          </div>
        ))}
      </nav>
    </aside>
  )
}
