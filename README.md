<div align="center">

# ⚖️ JURY-AI

### Intelligent Legal Document Analysis Platform

**Powered by Retrieval-Augmented Generation · Google Gemini · ChromaDB**

[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Python-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-orange)](https://www.trychroma.com/)
[![Gemini](https://img.shields.io/badge/Google-Gemini_AI-4285F4?logo=google)](https://deepmind.google/technologies/gemini/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Upload a legal document. Get an instant AI-powered risk analysis in seconds.*

</div>

---

## 🌟 What is JURY-AI?

JURY-AI is a full-stack AI-powered legal intelligence platform that helps **individuals, freelancers, and small businesses** understand the risks hidden inside legal contracts — without needing an expensive lawyer.

Simply upload a **PDF, DOCX, or TXT** contract and JURY-AI will:

- 🧠 **Summarize** the document in plain English
- 🔍 **Extract** key entities (parties, dates, amounts, jurisdictions)
- ⚠️ **Identify** risky clauses (Critical / High / Medium / Low)
- 📊 **Score** the contract's overall safety from 0–100
- 💬 **Answer** your specific legal questions about the document
- 📄 **Export** a professional PDF risk report

---

## ✨ Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | 📂 **Multi-Format Upload** | Drag & drop PDF, DOCX, or TXT files |
| 2 | 📝 **AI Document Summary** | Plain-English 2–3 sentence overview |
| 3 | 📊 **Safety Score (0–100)** | Animated radial gauge with color coding |
| 4 | ⚠️ **Risk Clause Detection** | Critical / High / Medium / Low severity cards |
| 5 | 🎯 **Risk Distribution** | Visual breakdown of all clause risk levels |
| 6 | 💬 **RAG-Powered Q&A** | Ask questions, get grounded answers from the doc |
| 7 | 📄 **PDF Report Export** | Download a professional risk analysis report |
| 8 | 🕓 **Document History** | Persistent analysis history in browser |
| 9 | 🛡️ **Safer Alternatives** | AI suggests fairer clause rewrites for high-risk items |
| 10 | 🏷️ **Named Entity Extraction** | Parties, dates, amounts & jurisdictions |
| 11 | 📋 **Full Report Page** | Dedicated `/report/[doc_id]` with bar charts & full clause table |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│               CLIENT LAYER (Browser)                     │
│   Next.js 16 + React 19 + Framer Motion + TailwindCSS   │
│   Split-View: Document Viewer | AI Analysis Panel        │
└─────────────────────┬────────────────────────────────────┘
                      │  HTTP REST (JSON / FormData)
┌─────────────────────▼────────────────────────────────────┐
│              APPLICATION LAYER (FastAPI)                  │
│  /api/upload  →  Parse + Chunk + Embed + Store           │
│  /api/summary →  Document Summarization                  │
│  /api/entities→  Named Entity Extraction                 │
│  /api/query   →  RAG Retrieval + LLM Generation         │
│  /api/score   →  Risk Clause Detection + Scoring         │
└──────────┬──────────────────────────┬─────────────────────┘
           │                          │
  ┌────────▼────────┐      ┌──────────▼──────────┐
  │   ChromaDB      │      │  Google Gemini API   │
  │ (Vector Store)  │      │  gemini-embedding-2  │
  │ Persistent      │      │  gemini-2.5-flash    │
  │ Local Storage   │      │  (+ 2.0-flash backup)│
  └─────────────────┘      └─────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 16, React 19, Framer Motion, TailwindCSS, jsPDF |
| **Backend** | FastAPI, Python 3.10+, Uvicorn (ASGI) |
| **AI / LLM** | Google Gemini (`gemini-2.5-flash`, fallback `gemini-2.0-flash`) |
| **Embeddings** | `gemini-embedding-2` (3,072 dimensions) |
| **Vector DB** | ChromaDB (persistent local storage) |
| **File Parsing** | PyMuPDF (PDF), python-docx (DOCX) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- A [Google Gemini API Key](https://aistudio.google.com/apikey)

### 1. Clone the Repository

```bash
git clone https://github.com/pokerito/my-project.git
cd my-project
```

### 2. Set Up the Backend

```bash
# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install fastapi uvicorn chromadb google-genai pymupdf python-docx python-dotenv
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 4. Set Up the Frontend

```bash
cd frontend
npm install
```

### 5. Run the Application

**Option A — Use the batch launcher (Windows):**
```bash
START_JURY_AI.bat
```

**Option B — Run manually:**

Terminal 1 (Backend):
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

Open your browser at **http://localhost:3000** 🎉

---

## 📁 Project Structure

```
JURY-AI/
├── .env                          # API key (not committed)
├── START_JURY_AI.bat             # One-click Windows launcher
├── README.md
│
├── backend/
│   ├── main.py                   # FastAPI app + route definitions
│   ├── services/
│   │   ├── rag_service.py        # RAG pipeline (embed, retrieve, generate, score)
│   │   └── file_parser.py        # Multi-format document parser
│   ├── database/
│   │   └── chroma_client.py      # ChromaDB Singleton PersistentClient
│   └── data/chroma/              # Persistent vector store (auto-created)
│
└── frontend/
    ├── src/app/
    │   ├── page.js               # Main dashboard (all 11 features)
    │   ├── report/[doc_id]/
    │   │   └── page.js           # Full report page
    │   ├── globals.css           # Design system tokens
    │   └── layout.js             # Root layout
    ├── next.config.mjs
    └── package.json
```

---

## ⚙️ How It Works

### RAG Pipeline

1. **Upload** → File is parsed (PDF/DOCX/TXT) and split into 1,000-character chunks
2. **Embed** → Each chunk is embedded via `gemini-embedding-2` (3,072-dim vectors)
3. **Store** → Vectors and text chunks are saved to ChromaDB with metadata
4. **Query** → User question is embedded, top-3 similar chunks are retrieved
5. **Generate** → Gemini generates an answer grounded *only* in retrieved context

### Risk Scoring Algorithm

| Risk Level | Points Deducted |
|-----------|----------------|
| 🔴 Critical | −25 per clause |
| 🟠 High | −15 per clause |
| 🟡 Medium | −5 per clause |
| 🟢 Low | 0 |

Starting from **100**, the final score is floored at **0**.

---

## 🧑‍💻 Team

| Name | Role |
|------|------|
| Ms. Vijaylaxmi Inamdar | Project Guide / Supervisor |
| Gaurav Jha | Full-Stack Developer |
| Kalash Verma | Backend & AI Integration |
| Komal Raj | Frontend & UI/UX |
| Krish Patel | RAG Pipeline & Testing |

**Department of Computer Science and Engineering**
Dayananda Sagar Academy of Technology and Management (DSATM), Bengaluru

---

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload` | Upload and embed a document |
| `POST` | `/api/summary` | Generate a plain-English summary |
| `POST` | `/api/entities` | Extract named entities (JSON) |
| `POST` | `/api/query` | RAG-powered legal Q&A |
| `POST` | `/api/score` | Risk clause detection + safety score |
| `GET` | `/` | Health check |

---

## ⚠️ Disclaimer

JURY-AI is an **AI-assisted tool** intended to help users understand legal documents more easily. It is **not a substitute for professional legal advice**. Always consult a qualified attorney for important legal matters.

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Made with ❤️ by Team JURY-AI · DSATM Bengaluru

</div>
