# ⚖️ JURY-AI — Final Review & Cloud Deployment Master Guide

> **Prepared for:** Final Project Review & Defense  
> **Project:** JURY-AI (Intelligent Legal Document Analysis Platform Using Retrieval-Augmented Generation)  
> **Institution:** Department of Computer Science and Engineering, DSATM, Bengaluru  

---

## 📌 Executive Summary

**JURY-AI** is an end-to-end, multi-model legal intelligence platform that demystifies complex legal contracts for laypersons, startups, and legal professionals. It leverages **Retrieval-Augmented Generation (RAG)**, ChromaDB vector indexing, and frontier LLMs (Google Gemini 3.5 Flash, OpenAI GPT-4o, Anthropic Claude 3.5 Sonnet, and xAI Grok-2) to deliver:

1. **Automated Risk Scoring (0–100 Gauge)** with mathematical deductions.
2. **Clause-Level Risk Categorization** (Critical, High, Medium, Low).
3. **AI-Generated Safer Alternatives** (fair, renegotiated contract clauses).
4. **Named Entity Extraction (NER)** (Parties, Dates, Amounts, Jurisdictions).
5. **Plain-English Executive Summaries**.
6. **RAG-Powered Interactive Contract Q&A** (grounded in document context).
7. **Full Audit Reports with 1-Click PDF Export** (via jsPDF & autoTable).
8. **Multi-Model Engine Selection** (switch between Gemini, GPT-4o, Claude, Grok live).
9. **Secure Multi-User Organization Dashboard** (SQLite / JWT authentication).

---

## 🚀 1. How to Run Locally for Tomorrow's Review

### Method A: The 1-Click Launcher (Recommended for Presentation)
Inside the project root:
```text
C:\Users\Gaurav Jha\OneDrive\Desktop\jury_AI
```
1. Simply double-click **`START_JURY_AI.bat`**.
2. It automatically:
   - Activates Python virtual environment.
   - Boots FastAPI Backend on **`http://localhost:8000`**.
   - Boots Next.js 16 Frontend on **`http://localhost:3000`**.
   - Opens Google Chrome directly to the app.

---

### Method B: Manual Commands (Terminal / VS Code)

**Terminal 1 — Backend:**
```powershell
cd "C:\Users\Gaurav Jha\OneDrive\Desktop\jury_AI"
.\venv\Scripts\activate
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**
```powershell
cd "C:\Users\Gaurav Jha\OneDrive\Desktop\jury_AI\frontend"
npm run dev
```

---

## 🎬 2. Step-by-Step Live Review Presentation Script (5-Minute Winning Demo)

Follow this exact sequence in front of the review committee for maximum impact:

### Step 1: Login & Organization Dashboard (30 seconds)
1. Open **`http://localhost:3000`**.
2. If already logged in, you'll see the **Dashboard**. If not, log in with:
   - **Email:** `gjha5757@gmail.com` | **Password:** `password123` (or register a fresh account in 5 seconds).
3. Point out the sleek dark-cyber glassmorphic interface, organization branding, and clean document metrics (`Total Documents`, `Analyzed`, `Avg. Safety Score`).

### Step 2: Upload the Trap Contract (30 seconds)
1. Click **`Upload Document`**.
2. Drag and drop the engineered sample file:
   ```text
   demo_contract.txt
   ```
   *(Located right in your project root! It contains deliberate legal traps: $1.00 liability cap, 5-year non-compete, 24% compound interest).*
3. The file appears immediately in your dashboard table with status `UPLOADED`.

### Step 3: Run Full Analysis & Highlight Multi-Model Selector (1 minute)
1. Click the uploaded document to open its workspace.
2. **Show the Panel the Top Navigation Bar:**
   - Point out the **`LLM ENGINE`** dropdown selector:
   - *"Our architecture supports Google Gemini 3.5 Flash, OpenAI GPT-4o, Claude 3.5 Sonnet, and xAI Grok-2."*
3. Click **`Run Full Analysis`**.
4. In ~3 seconds:
   - The animated **Safety Gauge** drops to ~25–35 (High Risk).
   - The **Severity Breakdown Bar Chart** updates live (showing Critical, High, Medium clauses).
   - The **Executive AI Summary** generates a 2-sentence plain-English breakdown.
   - The **Extracted Entities Grid** displays Parties, Dates, Amounts ($50,000, 24% interest), and Jurisdiction.

### Step 4: Show the "Safer Alternative" Re-drafting Feature (1 minute)
1. Scroll to the **Identified Clauses** section.
2. Open a **Critical** clause card (e.g., *Indemnification & Unlimited Liability*).
3. Click **`View Safer Alternative`**.
4. Show the panel the proposed fairer renegotiation clause:
   - *"Notice how JURY-AI doesn't just flag danger — it acts as an automated legal negotiator by drafting fair, balanced language."*

### Step 5: Test the RAG Contract Chatbot (1 minute)
1. In the right-hand **Document Q&A** chat box, type:
   > *"What happens if I terminate the agreement early?"*
2. JURY-AI retrieves the exact termination clause from ChromaDB and answers strictly grounded in the document text without hallucination.

### Step 6: 1-Click Professional PDF Report Export (1 minute)
1. Click the **`Full Audit Report & PDF`** button next to the status badge.
2. The page loads the complete executive audit view.
3. Click **`Export PDF`**.
4. A professional, publication-ready PDF report downloads instantly with charts, risk tables, and legal recommendations!

---

## 🌐 3. Cloud Deployment Guide (Vercel & Render)

You can deploy the complete platform online so anyone can access it via a live URL:

### Part A: Deploy Backend to Render (Free Tier)

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Production release ready for deployment"
   git push origin master
   ```
2. **Create Web Service on Render**:
   - Go to [render.com](https://render.com) and log in with GitHub.
   - Click **New +** → **Web Service**.
   - Select your `JURY-AI` GitHub repository.
3. **Configure Build Settings**:
   - **Name:** `jury-ai-backend`
   - **Language:** `Python 3`
   - **Region:** `Oregon (US West)` or `Singapore`
   - **Branch:** `master`
   - **Build Command:**
     ```bash
     pip install -r backend/requirements.txt
     ```
   - **Start Command:**
     ```bash
     uvicorn backend.main:app --host 0.0.0.0 --port $PORT
     ```
4. **Add Environment Variables on Render**:
   - Click **Environment Variables** tab:
     - `GOOGLE_API_KEY` = `your_gemini_api_key_here`
     - `PYTHON_VERSION` = `3.12.0`
5. Click **Create Web Service**. Render will deploy it and give you a public URL like:
   ```text
   https://jury-ai-backend.onrender.com
   ```

---

### Part B: Deploy Frontend to Vercel (Free Tier)

1. Go to [vercel.com](https://vercel.com) and log in with GitHub.
2. Click **Add New...** → **Project**.
3. Import your `JURY-AI` repository.
4. **Configure Project Settings**:
   - **Root Directory:** Click `Edit` and select **`frontend`**.
   - **Framework Preset:** `Next.js` (automatically detected).
5. **Add Environment Variable on Vercel**:
   - **Key:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://jury-ai-backend.onrender.com` *(your Render backend URL)*
6. Click **Deploy**!
7. In ~60 seconds, your site is live with a global SSL URL like:
   ```text
   https://jury-ai-frontend.vercel.app
   ```

---

## 💡 4. Top Review Defense Questions & Model Answers

### Q1: "Why did you use RAG instead of simply feeding the entire contract into ChatGPT/Gemini?"
> **Answer:**  
> *"Full-prompt LLM feeding suffers from the 'Lost-in-the-Middle' phenomenon where critical clauses in long contracts get overlooked, and it introduces higher latency and hallucination risks. Our RAG pipeline chunks the document into 1,000-character segments, embeds them with 3,072-dimensional vectors using ChromaDB, and performs cosine similarity retrieval. This guarantees that our Q&A answers are strictly grounded in verified clauses with exact context citations."*

### Q2: "How is the Safety Score calculated?"
> **Answer:**  
> *"We designed a deterministic scoring formula:*  
> $$Score = \max\left(0,\, 100 - (25 \times N_{critical}) - (15 \times N_{high}) - (5 \times N_{medium})\right)$$  
> *Critical clauses (like unlimited liability or total IP surrender) deduct 25 points each; High-risk clauses deduct 15 points; Medium clauses deduct 5 points. A score below 50 flags High Risk, 50–79 is Medium Risk, and 80–100 is Low/Safe."*

### Q3: "How does your system handle multiple LLM providers?"
> **Answer:**  
> *"We implemented an abstraction layer in `rag_service.py`. The frontend allows selecting Google Gemini, OpenAI GPT-4o, Anthropic Claude 3.5 Sonnet, or xAI Grok-2. The backend dynamically routes the prompt to the selected provider's SDK while maintaining consistent JSON parsing and error fallbacks."*

### Q4: "What happens if there is no internet or an API quota limit is hit?"
> **Answer:**  
> *"The backend includes intelligent heuristic fallbacks. If an external API is momentarily rate-limited, the system falls back to regex-based entity identification and rule-based legal clause classification, ensuring the UI and presentation never crash."*

---

## 🏆 Project Checklist for Tomorrow

- [x] All 29 unit tests pass in `backend/tests/`
- [x] Frontend compiles with **0 build errors** (`npm run build`)
- [x] Live Google Gemini 3.5 Flash integration active
- [x] Multi-model selector (Gemini / GPT-4o / Claude / Grok) connected
- [x] SQLite zero-config local database working
- [x] Document upload, scoring, NER, and RAG Q&A verified
- [x] Full Audit Report page with PDF export connected
- [x] 1-Click `START_JURY_AI.bat` tested and functional
- [x] Render & Vercel deployment blueprints ready
