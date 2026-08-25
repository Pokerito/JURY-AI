<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js"/>
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis"/>
  <img src="https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
</p>

<h1 align="center">⚖️ JURY-AI</h1>
<p align="center"><strong>AI-Powered Legal Document Intelligence Platform</strong></p>
<p align="center">Upload a legal contract. Get an instant risk analysis with safety scoring, clause detection, entity extraction, and AI-powered Q&A — all in seconds.</p>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    JURY-AI Platform                      │
├──────────────────────┬──────────────────────────────────┤
│    Next.js Frontend  │       FastAPI Backend            │
│    (Port 3000)       │       (Port 8000)                │
│                      │                                  │
│  ┌────────────────┐  │  ┌──────────┐  ┌──────────────┐ │
│  │ Auth Pages     │  │  │ API v1   │  │ Middleware    │ │
│  │ Dashboard      │──┼──│ Routes   │──│ JWT Auth     │ │
│  │ Analysis View  │  │  │          │  │ Rate Limit   │ │
│  │ RAG Q&A Chat   │  │  │          │  │ Idempotency  │ │
│  └────────────────┘  │  └────┬─────┘  └──────────────┘ │
│                      │       │                          │
│                      │  ┌────┴─────┐                    │
│                      │  │ Services │                    │
│                      │  │ Auth     │  ┌──────────────┐  │
│                      │  │ Document │──│ Gemini API   │  │
│                      │  │ RAG      │  │ (LLM + Embed)│  │
│                      │  │ Risk     │  └──────────────┘  │
│                      │  │ Entity   │                    │
│                      │  └────┬─────┘                    │
│                      │       │                          │
│                      │  ┌────┴───────────┐              │
│                      │  │  Repositories  │              │
│                      │  └──┬──────┬──────┘              │
│                      │     │      │                     │
│                      │  ┌──┴──┐ ┌─┴────────┐            │
│                      │  │ PG  │ │ ChromaDB │            │
│                      │  │ RDS │ │ (Vectors)│            │
│                      │  └─────┘ └──────────┘            │
└──────────────────────┴──────────────────────────────────┘
```

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **Document Upload** | Upload PDF, DOCX, TXT contracts with automatic text extraction |
| 🔍 **Risk Analysis** | AI-powered clause detection with Critical/High/Medium/Low severity |
| 📊 **Safety Score** | 0-100 safety score with interactive radial gauge visualization |
| 🏷️ **Entity Extraction** | Automatic detection of parties, dates, amounts, jurisdictions |
| 💬 **RAG Q&A** | Ask natural language questions about any uploaded document |
| 📝 **AI Summary** | One-click 2-3 sentence plain-English document summaries |
| 🔐 **JWT + RBAC** | Role-based access control (Admin, Analyst, Viewer) |
| 🏢 **Multi-tenant** | Organization-scoped data isolation |
| 🛡️ **Idempotency** | `X-Idempotency-Key` header prevents duplicate analysis runs |
| ⚡ **Rate Limiting** | Token-bucket rate limiter via Redis |

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL 16 + SQLAlchemy 2.0 (async)
- **Vector Store**: ChromaDB (per-org collections)
- **Cache**: Redis 7 (rate limiting, idempotency, sessions)
- **LLM**: Google Gemini 2.5-flash (with 2.0-flash fallback)
- **Auth**: JWT (access + refresh tokens) with bcrypt password hashing
- **Migrations**: Alembic (async-compatible)
- **Logging**: structlog (structured JSON)
- **Architecture**: Clean Architecture (Routes → Schemas → Services → Repositories → Models)

### Frontend
- **Framework**: Next.js 16 (App Router)
- **UI**: TailwindCSS 4 + Glassmorphism design system
- **Animations**: Framer Motion
- **Charts**: Recharts
- **Icons**: Lucide React
- **State**: React Context (AuthProvider)

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Target Deployment**: AWS (ECS, RDS, ElastiCache, S3)

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 16
- Redis 7
- Google Gemini API key

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/jury-ai.git
cd jury-ai

# Set your Gemini API key
echo "GOOGLE_API_KEY=your_key_here" > .env

# Start all services
docker compose up --build

# In another terminal, run migrations and seed data
docker compose exec backend python -m alembic upgrade head
docker compose exec backend python -m scripts.seed
```

Open http://localhost:3000 and login with:
- **Admin**: `admin@juryai.demo` / `DemoPass123!`
- **Analyst**: `analyst@juryai.demo` / `DemoPass123!`
- **Viewer**: `viewer@juryai.demo` / `DemoPass123!`

### Option 2: Local Development

```bash
# ── Backend ──────────────────────────────────────────────
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# Run migrations
python -m alembic upgrade head

# Seed demo data
python -m scripts.seed

# Start backend
uvicorn app.main:app --reload --port 8000

# ── Frontend (new terminal) ──────────────────────────────
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
jury-ai/
├── docker-compose.yml          # Full-stack orchestration
│
├── backend/
│   ├── Dockerfile              # Multi-stage production build
│   ├── pyproject.toml          # Python dependencies
│   ├── alembic.ini             # Migration config
│   ├── alembic/
│   │   ├── env.py              # Async migration environment
│   │   └── versions/
│   │       └── 0001_initial_schema.py
│   ├── scripts/
│   │   ├── seed.py             # Demo data seeder
│   │   └── migrate.py          # Migration runner
│   ├── tests/
│   │   └── test_core.py        # Unit tests (25+ tests)
│   └── app/
│       ├── main.py             # FastAPI app factory + /health
│       ├── config.py           # Pydantic settings
│       ├── dependencies.py     # DI container
│       ├── core/
│       │   ├── constants.py    # Enums (UserRole, RiskLevel, etc.)
│       │   ├── exceptions.py   # Custom exception hierarchy
│       │   └── security.py     # JWT + bcrypt utilities
│       ├── integrations/
│       │   ├── gemini_client.py  # Gemini LLM wrapper
│       │   ├── chroma_client.py  # ChromaDB vector store
│       │   ├── redis_client.py   # Async Redis pool
│       │   └── s3_client.py      # S3/local storage
│       ├── models/             # SQLAlchemy ORM (6 tables)
│       ├── schemas/            # Pydantic request/response DTOs
│       ├── repositories/       # Data access layer
│       ├── services/           # Business logic layer
│       ├── middleware/         # Auth, rate limit, idempotency, logging
│       └── api/v1/            # Versioned REST endpoints
│
└── frontend/
    ├── Dockerfile              # Multi-stage Next.js build
    ├── package.json
    └── src/
        ├── lib/api.js          # API client with JWT auto-refresh
        ├── contexts/AuthContext.js
        ├── components/
        │   ├── Navbar.js
        │   ├── ProtectedRoute.js
        │   ├── SafetyGauge.js
        │   ├── RiskClauseCard.js
        │   └── Skeleton.js
        └── app/
            ├── layout.js       # Root layout with AuthProvider
            ├── page.js         # Landing page
            ├── login/page.js
            ├── register/page.js
            └── dashboard/
                ├── page.js     # Document list + upload
                └── [docId]/page.js  # Analysis view
```

## 🔌 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/auth/register` | ❌ | Register user + org |
| `POST` | `/api/v1/auth/login` | ❌ | Login, get JWT tokens |
| `POST` | `/api/v1/auth/refresh` | ❌ | Refresh access token |
| `GET` | `/api/v1/auth/me` | ✅ | Get current user |
| `POST` | `/api/v1/documents/upload` | ✅ | Upload a document |
| `GET` | `/api/v1/documents` | ✅ | List documents (paginated) |
| `GET` | `/api/v1/documents/:id` | ✅ | Get document details |
| `DELETE` | `/api/v1/documents/:id` | ✅ | Soft-delete document |
| `POST` | `/api/v1/documents/:id/analyze` | ✅ | Trigger risk analysis |
| `GET` | `/api/v1/documents/:id/summary` | ✅ | Get AI summary |
| `GET` | `/api/v1/documents/:id/entities` | ✅ | Extract entities |
| `GET` | `/api/v1/documents/:id/risk-score` | ✅ | Get safety score + clauses |
| `POST` | `/api/v1/documents/:id/query` | ✅ | RAG Q&A |
| `GET` | `/health` | ❌ | System health check |

Interactive docs: http://localhost:8000/docs

## 🧪 Testing

```bash
cd backend
pytest tests/ -v
```

## 👥 Team

| Name | Role |
|------|------|
| **Gaurav Jha** | Lead Developer, System Architect |
| **Kalash Verma** | Backend Developer |
| **Komal Raj** | Frontend Developer |
| **Krish Patel** | ML/AI Integration |

## 📜 License

This project is developed as a final-year capstone project at DSATM, Bengaluru.

---

<p align="center">
  <strong>Built with ❤️ using FastAPI, Next.js, and Google Gemini</strong>
</p>
