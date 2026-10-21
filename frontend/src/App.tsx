import { useEffect, useState } from 'react'
import { deleteThread, fetchHealth, fetchMeta } from './api/client'
import { useThreads } from './chat/useThreads'
import { ChatPanel } from './components/ChatPanel'
import { Sidebar } from './components/Sidebar'
import type { Meta } from './types'

export default function App() {
  const { threads, activeId, setActiveId, startNew, recordActivity, remove } = useThreads()
  const [meta, setMeta] = useState<Meta | null>(null)
  const [ollamaOk, setOllamaOk] = useState<boolean | null>(null)

  useEffect(() => {
    fetchMeta().then(setMeta).catch(() => setMeta(null))
    fetchHealth()
      .then((h) => setOllamaOk(h.ollama))
      .catch(() => setOllamaOk(false))
  }, [])

  const handleDelete = (id: string) => {
    deleteThread(id).catch(() => undefined)
    remove(id)
  }

  return (
    <div className="app">
      <Sidebar
        threads={threads}
        activeId={activeId}
        onSelect={setActiveId}
        onNew={startNew}
        onDelete={handleDelete}
      />
      <main className="main">
        <header className="header">
          <span className={`status-dot ${ollamaOk === null ? '' : ollamaOk ? 'ok' : 'bad'}`} />
          <span className="model-name">{meta?.agent_model ?? '未连接到后端'}</span>
          {ollamaOk === false && <span className="header-warn">Ollama 或后端不可用</span>}
        </header>
        <ChatPanel
          key={activeId}
          threadId={activeId}
          hasHistory={threads.some((t) => t.id === activeId)}
          onSend={recordActivity}
        />
      </main>
    </div>
  )
}
