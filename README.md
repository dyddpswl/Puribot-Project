# 푸리봇

저장소 루트의 React 학습 코치는 `POST /api/chat`을 호출합니다. Vercel Function이 서버 환경 변수 `OPENAI_API_KEY`를 읽고 OpenAI에 요청을 보냅니다. 모델은 서버 환경 변수 `OPENAI_MODEL`로 바꿀 수 있습니다.

## React 학습 코치 실행

```powershell
npm.cmd ci
Copy-Item .env.local.example .env.local
```

이미 `.env.local`이 있으면 기존 파일에 `OPENAI_API_KEY`를 설정합니다. 키는 `.env.local`에 저장하고 파일을 Git에 추가하지 않습니다.

```powershell
npx.cmd --yes vercel@54.4.1 dev --local
```

CLI에 표시된 주소에서 학습 코치를 열 수 있습니다. React 학습 코치를 Vercel에 배포하려면 **Root Directory**를 저장소 루트로 지정하고, 해당 Vercel 프로젝트의 **Settings → Environment Variables**에 `OPENAI_API_KEY`를 추가한 뒤 배포합니다.

기존 Zimmerman 6단계 학습 앱은 [Python 프로젝트 안내](puribot-python-vercel/README.md)를 따릅니다. 해당 Vercel 프로젝트의 Root Directory는 `puribot-python-vercel`입니다.

## React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])

```

You can also install [eslint-plugin-react-x](https://npmx.dev/package/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://npmx.dev/package/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])

```
