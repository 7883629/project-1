import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  timeout: 10_000,
})

export type MessageResponse = {
  message: string
}

export type ChatResponse = {
  reply: string
}

export type ChatTurn = {
  role: 'user' | 'assistant'
  content: string
}

export type HistoryMessage = {
  session_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export async function fetchRoot() {
  const { data } = await api.get<MessageResponse>('/')
  return data
}

export async function fetchHello(name: string) {
  const { data } = await api.get<MessageResponse>(
    `/hello/${encodeURIComponent(name)}`,
  )
  return data
}


export async function fetchChatHistory(sessionId: string) {
  const { data } = await api.get<HistoryMessage[]>('/chat/history', {
    params: { session_id: sessionId },
  })
  return data
}

export async function chat(prompt: string, history: ChatTurn[]) {
  const { data } = await api.post<ChatResponse>(
    '/chat',
    { prompt, history },
    { timeout: 120_000 },
  )
  return data
}

type ChatStreamEvent = {
  result?: string
  error?: string
  session_id?: string
}

export async function chatStream(
  prompt: string,
  onDelta: (chunk: string) => void,
  options: {
    sessionId?: string
    signal?: AbortSignal
  } = {},
) {
  const baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api'
  const response = await fetch(`${baseURL}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    },
    body: JSON.stringify({
      prompt,
      ...(options.sessionId ? { session_id: options.sessionId } : {}),
    }),
    signal: options.signal,
  })

  if (!response.ok || !response.body) {
    throw new Error('stream failed')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let sessionId = options.sessionId
  let finished = false

  const consume = (frame: string) => {
    const data = frame
      .split('\n')
      .filter((line) => line.startsWith('data:'))
      .map((line) => line.slice(line.startsWith('data: ') ? 6 : 5))
      .join('\n')
      .trim()

    if (!data) return
    if (data === '[DONE]') {
      finished = true
      return
    }

    const payload = JSON.parse(data) as ChatStreamEvent
    if (payload.session_id) sessionId = payload.session_id
    if (payload.error) throw new Error(payload.error)
    if (payload.result) onDelta(payload.result)
  }

  while (true) {
    const { value, done } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, '\n')
    const frames = buffer.split('\n\n')
    buffer = frames.pop() ?? ''

    for (const frame of frames) consume(frame)
    if (finished) return sessionId
  }

  buffer += decoder.decode().replace(/\r\n/g, '\n')
  if (buffer.trim()) consume(buffer)
  if (!finished) throw new Error('stream interrupted')
  return sessionId
}
