import { useState } from 'react'
import type { FormEvent } from 'react'
import './App.css'

function App() {
  const [message, setMessage] = useState('')
  const [reply, setReply] = useState('')
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)

  async function sendMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const question = message.trim()
    if (!question || pending) return

    setPending(true)
    setReply('')
    setError('')
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: question }),
      })
      const data = await response.json()
      if (!response.ok || typeof data?.reply !== 'string') {
        setError(typeof data?.error === 'string' ? data.error : '답변을 불러오지 못했습니다.')
        return
      }
      setReply(data.reply)
    } catch {
      setError('AI 코치에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요.')
    } finally {
      setPending(false)
    }
  }

  return (
    <main className="coach">
      <h1>푸리봇 AI 학습 코치</h1>
      <form className="coach-form" onSubmit={sendMessage}>
        <label htmlFor="question">어떤 수학 문제를 풀고 있나요?</label>
        <textarea
          id="question"
          rows={5}
          maxLength={4000}
          required
          disabled={pending}
          value={message}
          onChange={(event) => setMessage(event.target.value)}
        />
        <button type="submit" disabled={pending || !message.trim()}>
          {pending ? '답변 기다리는 중…' : '질문 보내기'}
        </button>
      </form>
      {error && <p className="coach-error" role="alert">{error}</p>}
      <div aria-live="polite">
        {reply && (
          <section className="coach-reply">
            <h2>푸리봇 답변</h2>
            <p>{reply}</p>
          </section>
        )}
      </div>
    </main>
  )
}

export default App
