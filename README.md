# AI Research Assistant

A full-stack RAG (Retrieval-Augmented Generation) application for research paper ingestion, Q&A, summarization, and note-taking. Built with FastAPI, LangGraph, Qdrant, PostgreSQL, and Next.js.

## Architecture

```
                    ┌─────────────┐
                    │  Next.js 14  │  (Frontend - MUI v5)
                    │  localhost:3000
                    └──────┬──────┘
                           │ HTTP/REST
                    ┌──────▼──────┐
                    │  FastAPI     │  (Backend API)
                    │  localhost:8000
                    └──┬───────┬──┘
                       │       │
            ┌──────────▼──┐ ┌─▼──────────┐
            │  PostgreSQL  │ │   Qdrant    │
            │  (Users,     │ │ (Vector DB  │
            │   Notes,     │ │  for chunks)│
            │   Papers)    │ │             │
            └─────────────┘ └─────────────┘
```

## Features

- **PDF Ingestion** — Upload research papers (PDF), extract text, chunk, embed, and store in Qdrant
- **Q&A on Papers** — Ask questions about a paper; answers include citations from retrieved chunks
- **Summarization** — Auto-generated paper summaries from extracted text
- **Related Papers** — Semantic search across all ingested papers
- **Notes** — Create, edit, delete notes linked to specific papers
- **OTP Email Verification** — Register with email, verify via SMTP OTP before accessing
- **JWT Authentication** — Secure login with access tokens
- **Docker Compose** — One-command local setup
- **Kubernetes Manifests** — Ready-to-deploy YAML files
- **CI Pipeline** — GitHub Actions for linting and testing

## Tech Stack

| Layer   | Technology                                    |
| ------- | --------------------------------------------- |
| Backend | Python 3.11, FastAPI, SQLAlchemy (async), Alembic |
| AI      | LangGraph, Google Gemini API, Sentence Transformers |
| Vector DB | Qdrant                                      |
| Database | PostgreSQL 16                                |
| Frontend | Next.js 14, TypeScript, MUI v5              |
| Auth    | JWT (python-jose), bcrypt, aiosmtplib (OTP)  |
| Infra   | Docker Compose, Kubernetes, GitHub Actions   |

## Prerequisites

- Docker & Docker Compose
- A Gemini API key (or OpenAI key)
- (Optional) SMTP credentials for OTP emails

## Quick Start

1. **Clone the repo**

```bash
git clone https://github.com/ayax-khan/AI-Research-Assistant.git
cd AI-Research-Assistant
```

2. **Configure environment**

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and set at minimum:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

If you want OTP email verification, also set:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
```

3. **Start all services**

```bash
docker compose up --build
```

4. **Access the application**

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API: [http://localhost:8000](http://localhost:8000)
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Qdrant Dashboard: [http://localhost:6333](http://localhost:6333)

## API Endpoints

### Authentication
| Method | Endpoint             | Description              |
| ------ | -------------------- | ------------------------ |
| POST   | `/api/auth/register` | Register (OTP sent via email) |
| POST   | `/api/auth/verify-otp` | Verify OTP & activate account |
| POST   | `/api/auth/resend-otp` | Resend OTP email        |
| POST   | `/api/auth/login`    | Login, returns JWT token |
| GET    | `/api/auth/me`       | Get current user profile |

### Papers
| Method | Endpoint              | Description                  |
| ------ | --------------------- | ---------------------------- |
| POST   | `/api/papers/upload`  | Upload a PDF paper           |
| GET    | `/api/papers/`        | List all papers              |
| GET    | `/api/papers/{id}`    | Get paper details + summary  |
| DELETE | `/api/papers/{id}`    | Delete a paper               |

### Q&A & Search
| Method | Endpoint                         | Description                          |
| ------ | -------------------------------- | ------------------------------------ |
| POST   | `/api/papers/{id}/ask`           | Ask a question about a paper         |
| GET    | `/api/search?q=...`              | Semantic search across all papers    |

### Notes
| Method | Endpoint               | Description             |
| ------ | ---------------------- | ----------------------- |
| GET    | `/api/notes/`          | List user's notes       |
| POST   | `/api/notes/`          | Create a note           |
| PUT    | `/api/notes/{id}`      | Update a note           |
| DELETE | `/api/notes/{id}`      | Delete a note           |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/           # Route handlers (auth, papers, notes, search)
│   │   ├── core/          # Dependencies, security utilities
│   │   ├── graphs/        # LangGraph workflows (ingestion, QA)
│   │   ├── models/        # SQLAlchemy models (User, Paper, Note, OTP)
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── services/      # Business logic (PDF, chunker, LLM, Qdrant, RAG, email, OTP)
│   │   ├── utils/         # Prompt templates
│   │   ├── config.py      # Settings (env vars)
│   │   ├── database.py    # Async DB engine & session
│   │   └── main.py        # FastAPI app entry point
│   ├── alembic/           # Database migrations
│   ├── tests/             # Pytest tests
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js pages & layouts
│   │   ├── components/    # UI components (Navbar)
│   │   ├── lib/           # API client, auth helpers
│   │   └── types/         # TypeScript type definitions
│   └── Dockerfile
├── k8s/                   # Kubernetes deployment manifests
├── .github/workflows/     # CI pipeline
├── docker-compose.yml     # Local orchestration
└── README.md
```

## Development

### Backend (without Docker)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend (without Docker)

```bash
cd frontend
npm install
npm run dev
```

## Testing

```bash
cd backend
pytest
```

## Deployment

### Kubernetes

```bash
kubectl apply -f k8s/
```

Update the ConfigMap and Secrets in `k8s/backend-deployment.yaml` with your environment values.

## License

MIT
