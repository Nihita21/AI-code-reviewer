# 🤖 AI Code Reviewer

An AI-powered code review platform that analyzes source code using static analysis tools and Large Language Models (LLMs). The goal is to provide developers with detailed feedback on code quality, security, performance, and maintainability.

---

## ✨ Features

### Current
- Code editor interface
- FastAPI backend
- React frontend
- REST API for code review

### Planned
- AI-powered code reviews
- Static analysis using Ruff, Bandit, and Radon
- Multi-language support
- GitHub repository analysis
- Code quality scoring
- Security vulnerability detection
- Performance suggestions
- Code complexity analysis
- Downloadable PDF reports
- Review history dashboard

---

## 🛠️ Tech Stack

### Frontend
- React
- Vite
- Tailwind CSS
- Monaco Editor

### Backend
- FastAPI
- Python
- Pydantic
- Uvicorn

### AI
- OpenAI API *(planned)*

### Static Analysis
- Ruff *(planned)*
- Bandit *(planned)*
- Radon *(planned)*

---

## 📂 Project Structure

```
AI-Code-Reviewer/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── analyzers/
│   │   ├── services/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── utils/
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── frontend/
│
└── README.md
```

---

## 🚀 Installation

### Clone the repository

```bash
git clone https://github.com/Nihita21/AI-code-reviewer.git
cd AI-code-reviewer
```

### Backend

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Backend runs at:

```
http://127.0.0.1:8000
```

Swagger API:

```
http://127.0.0.1:8000/docs
```

---

### Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

## 🎯 Roadmap

- [x] Project setup
- [x] React frontend
- [x] FastAPI backend
- [ ] Connect frontend to backend
- [ ] Integrate Ruff
- [ ] Integrate Bandit
- [ ] Integrate Radon
- [ ] AI-powered review engine
- [ ] GitHub repository review
- [ ] Authentication
- [ ] Deployment

---

## 🤝 Contributing

Contributions, suggestions, and bug reports are welcome.

---

## 📄 License

This project is licensed under the MIT License.
