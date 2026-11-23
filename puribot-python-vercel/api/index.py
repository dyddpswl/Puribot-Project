"""Python FastAPI backend for Vercel serverless deployment."""
import json
import os
import re
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "questions.json"
QUESTIONS = json.loads(DATA_FILE.read_text(encoding="utf-8"))
BY_ID = {q["id"]: q for q in QUESTIONS}
app = FastAPI(title="푸리봇 Python API", version="1.0.0")

class CoachRequest(BaseModel):
    question_id: str
    mode: Literal["analyze", "hint", "recommend"]
    attempt: str = Field(default="", max_length=4000)
    hint_level: int = Field(default=1, ge=1, le=3)
    goal: str = Field(default="스스로 문제 풀기", max_length=100)
    confidence_before: int = Field(default=50, ge=0, le=100)
    confidence_after: int = Field(default=50, ge=0, le=100)
    reflection: str = Field(default="", max_length=500)
    error_type: str = Field(default="", max_length=100)
    hint_count: int = Field(default=0, ge=0, le=100)

class CoachResult(BaseModel):
    title: str
    feedback: str
    next_question: str
    strategy: str
    recommended_id: str | None = None
    source: str

@app.get("/api/health")
def health():
    return {"ok": True, "python": True, "question_count": len(QUESTIONS), "ai_configured": bool(os.getenv("OPENAI_API_KEY"))}

@app.get("/api/questions")
def questions(q: str = ""):
    term = q.strip().lower()[:100]
    items = [x for x in QUESTIONS if term in (x.get("id", "") + " " + x.get("topic", "") + " " + x.get("question", "")).lower()]
    return [{"id": x["id"], "topic": x.get("topic", ""), "unit": x.get("unit", ""), "hasImage": x.get("hasImage", False)} for x in items[:30]]

@app.get("/api/questions/{question_id}")
def question(question_id: str):
    item = BY_ID.get(question_id)
    if not item:
        raise HTTPException(404, "문항을 찾을 수 없습니다")
    return {k: item.get(k) for k in ["id", "topic", "unit", "question", "correctAnswer", "explanation", "videoUrl", "hasImage", "missingImages"]}

def find_next(item):
    for q in QUESTIONS:
        if q["id"] != item["id"] and q.get("topic") == item.get("topic") and not q.get("hasImage"):
            return q["id"]
    return None

def fallback(item, req):
    next_id = find_next(item)
    if req.mode == "hint":
        messages = [
            ("개념 확인", f"'{item.get('topic','해당 단원')}'의 핵심 개념을 떠올리고 문제에서 주어진 조건을 표시해 보세요."),
            ("조건 연결", "어떤 조건 때문에 가능한 경우가 제한되는지 확인해 보세요. 먼저 고정할 수 있는 대상을 찾아보세요."),
            ("풀이 전략", "경우를 중복 계산하지 않도록 기준을 정하고, 남은 선택지를 순서대로 세어 보세요."),
        ]
        title, feedback = messages[req.hint_level - 1]
        return CoachResult(title=title, feedback=feedback, next_question="지금까지 정리한 조건을 한 문장으로 설명해 볼까요?", strategy="조건 표시 → 전략 선택 → 계산 확인", source="기본 안내")
    if req.mode == "analyze":
        return CoachResult(title="풀이 점검", feedback="AI 연결이 없어 풀이의 수학적 정확성을 판정할 수 없습니다. 공식 해설과 비교하며 조건과 계산 과정을 점검해 보세요.", next_question="문제의 모든 조건을 풀이에 반영했나요?", strategy="조건과 풀이 단계 대조", source="기본 안내")
    return CoachResult(title="다음 학습 추천", feedback=f"'{req.error_type or '현재 학습'}'에 집중해 같은 개념의 문제를 다시 풀어 보세요.", next_question="이번에는 어떤 전략을 먼저 적용할까요?", strategy="학습 목표 설정 → 독립 풀이 → 자기평가", recommended_id=next_id, source="기본 안내")

SYSTEM = """당신은 한국 고등학생의 수학 자기조절학습을 돕는 푸리봇 코치다. Zimmerman의 사전사고-수행-자기성찰 순환을 지원한다.
반드시 제공된 문항과 공식 해설에 근거하라. 학생의 풀이가 없거나 불충분하면 오류를 단정하지 말라.
학생이 요청한 단계에 맞춰 힌트를 제공하되 정답이나 전체 풀이를 미리 누설하지 마라.
잘한 점은 근거가 있을 때만 말하고, 오류는 특정 단계와 이유를 설명하며 스스로 고칠 질문을 제공하라.
추천 문항은 후보 목록에서만 선택하라. 학생 개인정보를 요청하지 마라.
JSON 객체만 반환하라. 키는 title, feedback, next_question, strategy, recommended_id.
"""

@app.post("/api/coach", response_model=CoachResult)
def coach(req: CoachRequest):
    item = BY_ID.get(req.question_id)
    if not item:
        raise HTTPException(404, "문항을 찾을 수 없습니다")
    if not os.getenv("OPENAI_API_KEY"):
        return fallback(item, req)
    candidates = [q["id"] for q in QUESTIONS if q["id"] != item["id"] and q.get("topic") == item.get("topic") and not q.get("hasImage")]
    context = {
        "mode": req.mode, "hint_level": req.hint_level,
        "question": item.get("question"), "topic": item.get("topic"),
        "official_explanation": item.get("explanation"), "official_answer": item.get("correctAnswer"),
        "student_attempt": req.attempt, "goal": req.goal,
        "confidence_before": req.confidence_before, "confidence_after": req.confidence_after,
        "reflection": req.reflection, "error_type": req.error_type,
        "hint_count": req.hint_count, "candidate_ids": candidates,
    }
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=18.0, max_retries=0)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": json.dumps(context, ensure_ascii=False)}],
            response_format={"type": "json_object"}, temperature=0.2, max_tokens=650,
        )
        data = json.loads(response.choices[0].message.content or "{}")
        recommended = data.get("recommended_id")
        if recommended not in candidates:
            recommended = find_next(item) if req.mode == "recommend" else None
        def clean(key, default):
            value = data.get(key)
            return str(value)[:1200] if isinstance(value, str) and value.strip() else default
        return CoachResult(title=clean("title", "AI 학습 코치"), feedback=clean("feedback", "풀이를 다시 확인해 보세요."), next_question=clean("next_question", "다음 단계는 무엇일까요?"), strategy=clean("strategy", "조건 확인 후 재도전"), recommended_id=recommended, source="OpenAI API")
    except Exception:
        # Do not leak API keys or provider error details to students.
        return fallback(item, req)
