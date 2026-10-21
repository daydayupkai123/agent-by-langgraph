import { useCallback, useEffect, useState } from 'react'
import type { Thread } from '../types'

const STORAGE_KEY = 'agent.threads'

function loadThreads(): Thread[] {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]') as Thread[]
  } catch {
    return []
  }
}

/**
 * 会话列表保存在 localStorage，会话内容由后端 Checkpoint 按 thread_id 持久化。
 * activeId 始终有值：「新对话」是一个尚未加入列表的草稿 id，首次发送时才写入列表。
 */
export function useThreads() {
  const [threads, setThreads] = useState<Thread[]>(loadThreads)
  const [activeId, setActiveId] = useState<string>(() => threads[0]?.id ?? crypto.randomUUID())

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(threads))
  }, [threads])

  const startNew = useCallback(() => setActiveId(crypto.randomUUID()), [])

  /** 发送消息时调用：草稿会话加入列表，已有会话更新时间并置顶。 */
  const recordActivity = useCallback((id: string, message: string) => {
    setThreads((prev) => {
      const existing = prev.find((t) => t.id === id)
      const title = message.replace(/\s+/g, ' ').trim().slice(0, 30) || '新对话'
      const thread = existing ? { ...existing, updatedAt: Date.now() } : { id, title, updatedAt: Date.now() }
      return [thread, ...prev.filter((t) => t.id !== id)]
    })
  }, [])

  const remove = useCallback(
    (id: string) => {
      setThreads((prev) => prev.filter((t) => t.id !== id))
      if (id === activeId) startNew()
    },
    [activeId, startNew],
  )

  return { threads, activeId, setActiveId, startNew, recordActivity, remove }
}
