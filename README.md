# 🤖 AI Code Reviewer

A code review platform that combines **static analysis** (Ruff, Bandit, Radon) with an
optional **LLM review** to give developers feedback on correctness, security,
complexity and maintainability — in a browser editor, with issues underlined on the
exact lines.

---

## ✨ Features

- **Monaco code editor** with issues underlined in the code (red / yellow / blue by severity)
- **Click a line number** in the results to jump straight to it in the editor
- **Python static analysis**
  - Syntax checks and common pitfalls (unused imports, mutable default arguments, empty `except`)
  - **Ruff** — correctness and style (pyflakes, pycodestyle errors, bugbear)
  - **Bandit** — security issues, with CWE references
  - **Radon** — cyclomatic complexity and maintainability index, shown as metrics
- **AI review** through any OpenAI-compatible API — optional, and the only way to review
  JavaScript, Java and C++
- **0–100 quality score** and a plain-language summary
- Duplicate findings from different tools are merged; a tool that fails or is missing
  shows a *warning* and never lowers your score

---

## 🧠 How a review works

```
code ─► syntax / AST checks ─► (syntax error? stop here)
              │
              ├─► Ruff ──┐
              ├─► Bandit ─┼─► merge duplicates ─► + AI findings ─► score + summary
              └─► Radon ──┘                        (optional)
```

**Scoring:** start at 100, subtract 5 / 15 / 30 for each low / medium / high finding.
AI findings count **half** as much, because a model can be wrong.

---

## 🛠️ Tech stack

| Layer    | Tools                                           |
| -------- | ----------------------------------------------- |
| Frontend | React 19, Vite, Monaco Editor, Axios            |
| Backend  | FastAPI, Pydantic, Uvicorn, httpx               |
| Analysis | Ruff, Bandit, Radon                             |
| AI       | Any OpenAI-compatible chat completions endpoint |
| Tests    | pytest                                          |

---

## 🚀 Getting started

### 1. Clone

```bash
git clone https://github.com/Nihita21/AI-code-reviewer.git
cd AI-code-reviewer
```

### 2. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt

# optional: enable AI review and tweak settings
cp .env.example .env        # Windows: copy .env.example .env

uvicorn app.main:app --reload
```

- API: <http://127.0.0.1:8000>
- Interactive docs: <http://127.0.0.1:8000/docs>

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. If your backend is not at `http://127.0.0.1:8000`, copy
`frontend/.env.example` to `frontend/.env` and set `VITE_API_URL`.

---

## ⚙️ Configuration (`backend/.env`)

All settings are optional.

| Variable         | Default                     | Purpose                                              |
| ---------------- | --------------------------- | ---------------------------------------------------- |
| `OPENAI_API_KEY` | *(empty)*                   | Turns on AI review                                   |
| `OPENAI_MODEL`   | `gpt-4o-mini`               | Model used for AI review                             |
| `OPENAI_BASE_URL`| `https://api.openai.com/v1` | Point at any OpenAI-compatible provider              |
| `CORS_ORIGINS`   | `localhost:5173` + `127.0.0.1:5173` | Comma-separated frontend origins             |
| `MAX_CODE_CHARS` | `50000`                     | Largest submission accepted                          |

> 🔒 **Privacy:** when AI review is on, the submitted code is sent to the configured
> AI provider. Leave `OPENAI_API_KEY` empty to keep everything local.

---

## 📡 API

### `POST /review`

```json
{ "language": "python", "code": "import os\n...", "use_ai": true }
```

Example response (values are illustrative):

```json
{
  "score": 65,
  "summary": "Found 3 issue(s): 2 medium, 1 low.",
  "issues": [
    {
      "severity": "low",
      "title": "Unused import: os",
      "line": 1,
      "suggestion": "Remove the import of 'os' if it is not needed.",
      "source": "ast"
    }
  ],
  "metrics": {
    "lines_of_code": 6, "functions": 1, "average_complexity": 2.0,
    "max_complexity": 2, "maintainability_index": 100.0
  },
  "ai_summary": null,
  "warnings": []
}
```

`source` is one of `ast`, `ruff`, `bandit`, `radon`, `ai`. Errors: `400` empty code /
unsupported language / non-Python without AI, `413` code too large, `502` AI provider
failed (non-Python only).

### `GET /capabilities`

Reports whether AI review is enabled and which languages are available, so the UI never
offers an option that would fail.

### `GET /health`

`{"status": "ok"}`

---

## 🧪 Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

The suite never calls a real AI provider. Tests that need the real Ruff / Bandit / Radon
are skipped automatically when those are not installed.

---

## 📂 Project structure

```
AI-code-reviewer/
├── backend/
│   ├── app/
│   │   ├── api/review.py            # /review and /capabilities
│   │   ├── schemas/review.py        # request / response models
│   │   ├── services/
│   │   │   ├── analyzer.py          # AST checks
│   │   │   ├── ruff_analyzer.py
│   │   │   ├── bandit_analyzer.py
│   │   │   ├── radon_analyzer.py
│   │   │   ├── ai_reviewer.py       # LLM review
│   │   │   └── pipeline.py          # merge, dedupe, score
│   │   ├── config.py                # environment settings
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    └── src/
        ├── components/              # editor, selector, button, review card
        ├── pages/Home.jsx
        └── services/api.js
```

---

## 🎯 Roadmap

- [x] Project setup, React frontend, FastAPI backend
- [x] Connect frontend to backend
- [x] Ruff, Bandit and Radon integration
- [x] AI-powered review engine
- [x] Code quality scoring, complexity analysis, security detection
- [ ] GitHub repository review
- [ ] Review history dashboard
- [ ] Downloadable PDF reports
- [ ] Static analysis for more languages (ESLint, etc.)
- [ ] Authentication
- [ ] Deployment

---

## 🤝 Contributing

Contributions, suggestions, and bug reports are welcome.

## 📄 License

This project is licensed under the MIT License.
