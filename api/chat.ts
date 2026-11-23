const maxMessageLength = 4000

function json(body: { reply: string } | { error: string }, status: number, headers: Record<string, string> = {}) {
  return Response.json(body, { status, headers: { ...headers, 'Cache-Control': 'no-store' } })
}

export default {
  async fetch(request: Request) {
    if (request.method !== 'POST') {
      return json({ error: 'POST 요청만 지원합니다.' }, 405, { Allow: 'POST' })
    }

    const contentType = request.headers.get('Content-Type')?.split(';')[0].trim().toLowerCase()
    if (contentType !== 'application/json') {
      return json({ error: 'JSON 형식으로 요청해 주세요.' }, 415)
    }

    const body = await request.json().catch(() => null)
    const message = body && typeof body === 'object' && 'message' in body && typeof body.message === 'string'
      ? body.message.trim()
      : ''
    if (!message || message.length > maxMessageLength) {
      return json({ error: '질문은 1~4000자로 입력해 주세요.' }, 400)
    }

    const apiKey = process.env.OPENAI_API_KEY?.trim()
    if (!apiKey) {
      return json({ error: '서버에 AI 코치가 설정되지 않았습니다.' }, 503)
    }

    try {
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: process.env.OPENAI_MODEL?.trim() || 'gpt-5.4-mini',
          messages: [
            {
              role: 'system',
              content: '당신은 푸리봇 수학 학습 코치입니다. 학생이 스스로 해결할 수 있도록 질문과 힌트로 안내하세요.',
            },
            { role: 'user', content: message },
          ],
          max_completion_tokens: 600,
          store: false,
        }),
        redirect: 'error',
        signal: AbortSignal.timeout(15_000),
      })
      if (response.ok) {
        const data = await response.json() as { choices?: Array<{ message?: { content?: unknown } }> } | null
        const reply = data?.choices?.[0]?.message?.content
        if (typeof reply === 'string' && reply.trim()) {
          return json({ reply: reply.trim() }, 200)
        }
      }
    } catch {
      return json({ error: 'AI 코치에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요.' }, 502)
    }

    return json({ error: 'AI 코치가 답변을 생성하지 못했습니다. 잠시 후 다시 시도해 주세요.' }, 502)
  },
}
