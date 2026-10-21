const EXAMPLES = [
  '你好，介绍一下你自己',
  '帮我算一下 (1234 + 5678) * 3.5',
  '今天星期几？距离 2027 年元旦还有多少天？',
  '用三句话解释什么是 ReAct Agent',
]

export function EmptyState({ onPick }: { onPick: (text: string) => void }) {
  return (
    <div className="empty-state">
      <h1>有什么可以帮你？</h1>
      <p>基于 LangGraph + Ollama 本地模型的智能体</p>
      <div className="examples">
        {EXAMPLES.map((e) => (
          <button key={e} onClick={() => onPick(e)}>
            {e}
          </button>
        ))}
      </div>
    </div>
  )
}
