export interface RawSSEEvent {
  event: string
  data: string
}

/**
 * 解析 fetch 返回的 SSE 流。
 * 浏览器原生 EventSource 只支持 GET，而对话接口是 POST，所以这里手动解析。
 */
export async function* readSSE(response: Response): AsyncGenerator<RawSSEEvent> {
  if (!response.body) throw new Error('响应没有 body')
  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader()
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer = (buffer + value).replace(/\r\n/g, '\n')

    let sep: number
    while ((sep = buffer.indexOf('\n\n')) !== -1) {
      const block = buffer.slice(0, sep)
      buffer = buffer.slice(sep + 2)

      let event = 'message'
      const dataLines: string[] = []
      for (const line of block.split('\n')) {
        if (line.startsWith(':')) continue
        if (line.startsWith('event:')) event = line.slice(6).trim()
        else if (line.startsWith('data:')) dataLines.push(line.slice(5).replace(/^ /, ''))
      }
      if (dataLines.length) yield { event, data: dataLines.join('\n') }
    }
  }
}
