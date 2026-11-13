import {
  PlusOutlined,
  RobotOutlined,
  SendOutlined,
} from '@ant-design/icons'
import {
  Alert,
  Avatar,
  Button,
  Flex,
  Input,
  Popconfirm,
  Spin,
  Typography,
  theme,
  type GetRef,
} from 'antd'
import { useEffect, useRef, useState } from 'react'
import { chatStream, fetchChatHistory, type ChatTurn } from '@/lib/api.ts'

const SESSION_ID = 'bba78e28-6f6a-4d61-b23f-12d40f9021df'

type ChatMessage = ChatTurn & { id: string }

const SUGGESTIONS = [
  '用三句话解释什么是大语言模型',
  '帮我写一个数组去重的 TypeScript 函数',
  '如何排查前端接口跨域问题？',
  '给今天的学习列一个 30 分钟计划',
]

export default function Home() {
  const { token } = theme.useToken()
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [error, setError] = useState<string>()
  const [loading, setLoading] = useState(false)
  const [historyLoading, setHistoryLoading] = useState(true)
  const listRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<GetRef<typeof Input.TextArea>>(null)
  const abortRef = useRef<AbortController | null>(null)
  const sessionRef = useRef<string | undefined>(SESSION_ID)

  useEffect(() => {
    let cancelled = false

    async function loadHistory() {
      try {
        const history = await fetchChatHistory(SESSION_ID)
        if (cancelled) return
        const ordered = [...history].sort(
          (a, b) => Number(a.created_at) - Number(b.created_at),
        )
        setMessages(
          ordered.map((item, index) => ({
            id: `${item.created_at}-${index}`,
            role: item.role,
            content: item.content,
          })),
        )
      } catch (error) {
        if (cancelled) return
        setError(
          error instanceof Error && error.message
            ? error.message
            : '历史记录加载失败，请确认后端已在 8000 端口运行。',
        )
      } finally {
        if (!cancelled) {
          setHistoryLoading(false)
          inputRef.current?.focus()
        }
      }
    }

    void loadHistory()
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => () => {
    abortRef.current?.abort()
  }, [])

  useEffect(() => {
    const list = listRef.current
    if (!list) return
    list.scrollTo({ top: list.scrollHeight, behavior: loading ? 'auto' : 'smooth' })
  }, [messages, loading, error])

  async function requestReply(prompt: string) {
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller
    const assistantId = crypto.randomUUID()
    const sessionId = sessionRef.current

    setMessages((prev) => [
      ...prev,
      { id: assistantId, role: 'assistant', content: '' },
    ])
    setLoading(true)
    setError(undefined)

    try {
      const nextSessionId = await chatStream(
        prompt,
        (chunk) => {
          setMessages((prev) =>
            prev.map((message) =>
              message.id === assistantId
                ? { ...message, content: message.content + chunk }
                : message,
            ),
          )
        },
        { sessionId, signal: controller.signal },
      )
      if (!controller.signal.aborted && nextSessionId) {
        sessionRef.current = nextSessionId
      }
    } catch (error) {
      if (controller.signal.aborted) return
      setMessages((prev) =>
        prev.filter(
          (message) => message.id !== assistantId || message.content.length > 0,
        ),
      )
      setError(
        error instanceof Error && error.message && error.message !== 'stream failed'
          ? error.message
          : '请求失败，请确认后端已在 8000 端口运行。',
      )
    } finally {
      if (abortRef.current === controller) {
        abortRef.current = null
        setLoading(false)
        inputRef.current?.focus()
      }
    }
  }

  function send(text?: string) {
    const trimmed = (text ?? input).trim()
    if (!trimmed || loading || historyLoading) return

    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: 'user', content: trimmed },
    ])
    setInput('')
    void requestReply(trimmed)
  }

  function retry() {
    if (loading) return
    const lastUserIndex = messages.findLastIndex((message) => message.role === 'user')
    if (lastUserIndex < 0) return
    const prompt = messages[lastUserIndex].content
    setMessages(messages.slice(0, lastUserIndex + 1))
    void requestReply(prompt)
  }

  function clearChat() {
    abortRef.current?.abort()
    sessionRef.current = undefined
    setMessages([])
    setError(undefined)
    setInput('')
    setLoading(false)
    inputRef.current?.focus()
  }

  const userBubble = {
    maxWidth: 'min(78%, 36rem)',
    padding: '10px 14px',
    borderRadius: 18,
    borderBottomRightRadius: 6,
    background: token.colorPrimary,
    color: token.colorTextLightSolid,
    lineHeight: token.lineHeight,
    whiteSpace: 'pre-wrap' as const,
    wordBreak: 'break-word' as const,
  }

  const assistantBubble = {
    maxWidth: 'min(78%, 36rem)',
    padding: '10px 14px',
    borderRadius: 18,
    borderBottomLeftRadius: 6,
    background: token.colorBgContainer,
    color: token.colorText,
    border: `1px solid ${token.colorBorderSecondary}`,
    boxShadow: token.boxShadowTertiary,
    lineHeight: token.lineHeight,
    whiteSpace: 'pre-wrap' as const,
    wordBreak: 'break-word' as const,
  }

  return (
    <Flex vertical className="min-h-0 flex-1" style={{ minHeight: 0 }} gap={12}>
      <Flex align="center" justify="space-between" gap={12}>
        <div>
          <Typography.Title level={4} style={{ margin: 0 }}>
            对话
          </Typography.Title>
          <Typography.Text type="secondary">
            同一会话会使用服务端保存的历史
          </Typography.Text>
        </div>
        {messages.length > 0 ? (
          <Popconfirm
            title="开始新对话？"
            description="当前消息会被清空，下一条会开启新会话。"
            okText="清空"
            cancelText="取消"
            onConfirm={clearChat}
          >
            <Button icon={<PlusOutlined />} disabled={loading}>
              新对话
            </Button>
          </Popconfirm>
        ) : (
          <Button icon={<PlusOutlined />} disabled>
            新对话
          </Button>
        )}
      </Flex>

      <div
        ref={listRef}
        style={{
          flex: 1,
          minHeight: 0,
          overflowY: 'auto',
          padding: '8px 4px',
        }}
      >
        {historyLoading ? (
          <Flex align="center" justify="center" style={{ minHeight: '100%' }}>
            <Spin />
          </Flex>
        ) : messages.length === 0 ? (
          <Flex
            vertical
            align="center"
            justify="center"
            gap={16}
            style={{ minHeight: '100%', textAlign: 'center', padding: '24px 8px' }}
          >
            <Avatar
              size={64}
              icon={<RobotOutlined />}
              style={{
                background: token.colorFillSecondary,
                color: token.colorText,
              }}
            />
            <div>
              <Typography.Title level={3} style={{ margin: 0 }}>
                今天想聊点什么？
              </Typography.Title>
              <Typography.Paragraph
                type="secondary"
                style={{ margin: '8px 0 0' }}
              >
                输入问题开始对话，或从下面选一个。
              </Typography.Paragraph>
            </div>
            <Flex wrap gap={8} justify="center" style={{ maxWidth: 560 }}>
              {SUGGESTIONS.map((suggestion) => (
                <Button
                  key={suggestion}
                  disabled={loading}
                  onClick={() => send(suggestion)}
                >
                  {suggestion}
                </Button>
              ))}
            </Flex>
          </Flex>
        ) : (
          <Flex vertical gap={16}>
            {messages.map((message) => {
              const isUser = message.role === 'user'
              return (
                <Flex
                  key={message.id}
                  justify={isUser ? 'flex-end' : 'flex-start'}
                  gap={8}
                  align="flex-start"
                >
                  {isUser ? null : (
                    <Avatar
                      icon={<RobotOutlined />}
                      style={{
                        background: token.colorFillSecondary,
                        color: token.colorText,
                        flex: 'none',
                      }}
                    />
                  )}
                  {message.role === 'assistant' &&
                  message.content.length === 0 &&
                  loading ? (
                    <Flex
                      align="center"
                      gap={8}
                      style={{ ...assistantBubble, maxWidth: 'none' }}
                    >
                      <Spin size="small" />
                      <Typography.Text type="secondary">正在思考…</Typography.Text>
                    </Flex>
                  ) : (
                    <Typography.Paragraph
                      style={{
                        margin: 0,
                        ...(isUser ? userBubble : assistantBubble),
                      }}
                    >
                      {message.content}
                    </Typography.Paragraph>
                  )}
                </Flex>
              )
            })}
          </Flex>
        )}
      </div>

      {error ? (
        <Alert
          type="error"
          showIcon
          message={error}
          action={
            <Button size="small" onClick={retry}>
              重试
            </Button>
          }
        />
      ) : null}

      <form
        onSubmit={(event) => {
          event.preventDefault()
          send()
        }}
      >
        <Flex
          vertical
          gap={8}
          style={{
            padding: 12,
            borderRadius: 16,
            background: token.colorBgContainer,
            border: `1px solid ${token.colorBorder}`,
            boxShadow: token.boxShadowTertiary,
          }}
        >
          <Input.TextArea
            ref={inputRef}
            value={input}
            variant="borderless"
            autoSize={{ minRows: 1, maxRows: 6 }}
            placeholder="输入消息，Enter 发送，Shift + Enter 换行"
            onChange={(event) => setInput(event.target.value)}
            onPressEnter={(event) => {
              if (event.shiftKey || event.nativeEvent.isComposing) return
              event.preventDefault()
              send()
            }}
          />
          <Flex justify="space-between" align="center">
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              Enter 发送 · Shift + Enter 换行
            </Typography.Text>
            <Button
              type="primary"
              htmlType="submit"
              shape="circle"
              icon={<SendOutlined />}
              loading={loading || historyLoading}
              disabled={input.trim().length === 0 || historyLoading}
              aria-label="发送"
            />
          </Flex>
        </Flex>
      </form>
    </Flex>
  )
}
