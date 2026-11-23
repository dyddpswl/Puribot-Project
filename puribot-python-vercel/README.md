# 푸리봇 AI 학습 코치 — Python + Vercel

**Python FastAPI**로 문제 조회, AI 풀이 분석, 3단계 힌트, 개인화 추천 API를 구현했습니다. 브라우저 화면은 정적 HTML/CSS/JavaScript이며, **주요 서버 기능은 Python**입니다. Vercel에 배포할 수 있는 구조입니다.

## 실행

Python 3.11+ 권장.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

환경변수 `OPENAI_API_KEY`를 설정하면 AI를 사용합니다. 키가 없으면 데모용 기본 안내가 표시되며 실제 풀이 분석이 아닙니다.

로컬에서는 두 개의 터미널로 실행할 수 있습니다.

```bash
# 터미널 1 — Python API
uvicorn api.index:app --reload --port 8000
# 터미널 2 — 정적 화면 (API와 동일 출처가 아니므로 프록시 필요)
```

**권장 로컬 실행:** Vercel CLI를 설치하고 `vercel dev`를 실행하면 정적 화면과 `/api/*` 경로를 함께 테스트할 수 있습니다.

```bash
npm install -g vercel
vercel login
vercel dev
```

## GitHub → Vercel

1. GitHub **Private** 저장소 생성. `.env`, `.env.local`, API 키, 학생 개인정보를 업로드하지 마세요.
2. 프로젝트 폴더 전체를 GitHub에 push합니다.
3. Vercel의 Add New Project에서 해당 저장소를 Import합니다.
4. Root Directory는 이 프로젝트의 최상위 폴더로 설정합니다.
5. Vercel Environment Variables에 `OPENAI_API_KEY`, `OPENAI_MODEL`을 등록합니다.
6. 배포 후 `/api/health`가 `ok: true`를 반환하는지 확인합니다.
7. `/`에서 문항 검색, AI 분석, 힌트, 자기성찰, 추천을 확인합니다.

## 주요 경로

- `api/index.py`: Python FastAPI 앱과 OpenAI 호출
- `data/questions.json`: 기존 20문항 데이터
- `public/index.html`, `public/style.css`, `public/app.js`: 반응형 웹 화면
- `vercel.json`: `/api/*`를 Python 서버리스 함수로 전달
- `tests/test_api.py`: 기본 API 테스트

## 주의

- **AI 정확도:** OpenAI 응답이 수학적으로 정확하다고 보장할 수 없습니다. 공식 해설 기반 프롬프트를 사용하나 교사 검증이 필요합니다.
- **문항 그림:** 원본에서 그림이 누락된 문항은 안내 문구를 표시합니다. 그림과 수식 원본 검증이 필요합니다.
- **저장:** 현재 브라우저 localStorage에만 학습 상태를 저장합니다. 서버에 학생 기록을 저장하지 않습니다. 운영용으로는 인증·외부 DB·개인정보 보호 설계가 필요합니다.
- **보안:** 공개 배포 전 인증, 서버측 사용자별 rate limit, 비용 상한, 모니터링을 추가하세요. 서버리스 인스턴스 메모리만 사용하는 제한은 불충분합니다.
- **저작권:** 문항과 영상 링크를 공개 배포할 권한을 확인하세요. 승인 전에는 비공개 개발/접근 제한 환경에서 테스트하세요.
- **PWA:** 홈 화면에 추가할 수 있는 manifest는 제공하지만 오프라인 캐싱이나 앱스토어 배포는 포함하지 않습니다.
- **테스트:** 로컬 API 테스트와 배포 빌드 검증은 별개입니다. Vercel 배포 후 실환경 검증이 필요합니다.
