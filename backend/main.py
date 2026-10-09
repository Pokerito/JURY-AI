from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uuid
import asyncio

from backend.services.rag_service import RAGService
from backend.services.file_parser import parse_file
from backend.database import db

app = FastAPI(title="Jury-AI API", description="Legal Intelligence Platform API v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_service = RAGService()

# ── Schemas ──────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = ""
    org_name: Optional[str] = ""

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class ChangePasswordRequest(BaseModel):
    current_password: Optional[str] = None
    new_password: str

class UpdateProfileRequest(BaseModel):
    full_name: str
    org_name: str

class QueryRequest(BaseModel):
    question: str

# ── Auth Helper ──────────────────────────────────────────────────────────────
async def get_current_user_optional(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    return db.get_user_by_token(token)

async def get_current_user(authorization: Optional[str] = Header(None)):
    user = await get_current_user_optional(authorization)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return user

# ── Base Health ──────────────────────────────────────────────────────────────
@app.get("/")
@app.get("/health")
@app.get("/api/v1/health")
def read_root():
    return {"status": "Jury-AI is running", "version": "2.0"}

# ── V1 Auth Endpoints ────────────────────────────────────────────────────────
@app.post("/api/v1/auth/register")
async def register(req: RegisterRequest):
    try:
        user = db.create_user(
            email=req.email,
            password=req.password,
            full_name=req.full_name,
            org_name=req.org_name
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    tokens = db.create_tokens(user["id"])
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer",
        "user": user
    }

@app.post("/api/v1/auth/login")
async def login(req: LoginRequest):
    user = db.authenticate_user(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    tokens = db.create_tokens(user["id"])
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer",
        "user": user
    }

@app.get("/api/v1/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.post("/api/v1/auth/refresh")
async def refresh_token(req: RefreshRequest):
    tokens = db.refresh_tokens(req.refresh_token)
    if not tokens:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return tokens

@app.post("/api/v1/auth/change-password")
async def change_password(req: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
    success = db.update_user_password(current_user["id"], req.new_password, req.current_password)
    if not success:
        raise HTTPException(status_code=400, detail="Incorrect current password")
    return {"message": "Password updated successfully"}

@app.put("/api/v1/auth/profile")
async def update_profile(req: UpdateProfileRequest, current_user: dict = Depends(get_current_user)):
    updated = db.update_user_profile(current_user["id"], req.full_name, req.org_name)
    return {"message": "Profile updated successfully", "user": updated}

# ── V1 Document Endpoints ────────────────────────────────────────────────────
@app.post("/api/v1/documents/upload")
async def upload_doc_v1(
    file: UploadFile = File(...),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    content = await file.read()
    try:
        text = parse_file(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    doc_id = str(uuid.uuid4())
    try:
        rag_service.insert_document(doc_id=doc_id, text=text)
    except Exception as e:
        print(f"Warning: RAG indexing skipped/deferred during upload ({e})")
    
    ext = file.filename.split('.')[-1].lower() if '.' in file.filename else 'txt'
    user_id = current_user["id"] if current_user else None
    
    doc = db.add_document(
        doc_id=doc_id,
        filename=file.filename,
        file_type=ext,
        file_size=len(content),
        text_content=text,
        user_id=user_id
    )
    return doc

@app.get("/api/v1/documents")
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    user_id = current_user["id"] if current_user else None
    return db.get_documents(user_id=user_id, page=page, page_size=page_size)

@app.get("/api/v1/documents/{doc_id}")
async def get_document_by_id(doc_id: str):
    doc = db.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@app.delete("/api/v1/documents/{doc_id}")
async def delete_document_by_id(doc_id: str):
    db.delete_document(doc_id)
    return {"message": "Document deleted"}

# ── V1 Models Endpoint ───────────────────────────────────────────────────────
@app.get("/api/v1/models")
async def get_available_models():
    import os
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    has_google = bool(os.getenv("GOOGLE_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_grok = bool(os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY"))
    
    return [
        {
            "id": "gemini-2.5-flash",
            "name": "Google Gemini 2.5 Flash",
            "provider": "Google DeepMind",
            "badge": "Fast & Large Context",
            "configured": has_google,
            "is_default": True
        },
        {
            "id": "gpt-4o",
            "name": "OpenAI GPT-4o",
            "provider": "OpenAI",
            "badge": "High Accuracy & Structured",
            "configured": has_openai,
            "is_default": False
        },
        {
            "id": "gpt-4o-mini",
            "name": "OpenAI GPT-4o Mini",
            "provider": "OpenAI",
            "badge": "Fast & Efficient",
            "configured": has_openai,
            "is_default": False
        },
        {
            "id": "claude-3-5-sonnet",
            "name": "Claude 3.5 Sonnet",
            "provider": "Anthropic",
            "badge": "Best Legal Nuance",
            "configured": has_anthropic,
            "is_default": False
        },
        {
            "id": "grok-2",
            "name": "xAI Grok-2",
            "provider": "xAI",
            "badge": "Direct & Unfiltered",
            "configured": has_grok,
            "is_default": False
        }
    ]

# ── V1 Document Analysis Endpoints ──────────────────────────────────────────
@app.post("/api/v1/documents/{doc_id}/analyze")
async def analyze_document_v1(doc_id: str, model: Optional[str] = Query("gemini-2.5-flash")):
    doc = db.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Run scoring, summary, entities concurrently
    try:
        summary_task = rag_service.summarize(doc_id, model=model)
        entities_task = rag_service.extract_entities(doc_id, model=model)
        score_task = rag_service.score_document(doc_id, model=model)
        
        summary, entities, score_data = await asyncio.gather(summary_task, entities_task, score_task)
        
        db.update_document_analysis(
            doc_id=doc_id,
            summary=summary,
            entities=entities,
            score_data=score_data,
            status="analyzed"
        )
        return {
            "status": "analyzed",
            "summary": summary,
            "entities": entities,
            "risk_score": score_data,
            "model_used": model
        }
    except Exception as e:
        db.update_document_analysis(doc_id=doc_id, status="failed")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/v1/documents/{doc_id}/summary")
async def get_summary_v1(doc_id: str, model: Optional[str] = Query("gemini-2.5-flash")):
    doc = db.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.get("summary"):
        return {"summary": doc["summary"]}
    
    summary = await rag_service.summarize(doc_id, model=model)
    db.update_document_analysis(doc_id=doc_id, summary=summary)
    return {"summary": summary}

@app.get("/api/v1/documents/{doc_id}/entities")
async def get_entities_v1(doc_id: str, model: Optional[str] = Query("gemini-2.5-flash")):
    doc = db.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.get("entities"):
        return doc["entities"]
    
    entities = await rag_service.extract_entities(doc_id, model=model)
    db.update_document_analysis(doc_id=doc_id, entities=entities)
    return entities

@app.get("/api/v1/documents/{doc_id}/risk-score")
async def get_risk_score_v1(doc_id: str, model: Optional[str] = Query("gemini-2.5-flash")):
    doc = db.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.get("risk_score"):
        return doc["risk_score"]
    
    score_data = await rag_service.score_document(doc_id, model=model)
    db.update_document_analysis(doc_id=doc_id, score_data=score_data)
    return score_data

@app.post("/api/v1/documents/{doc_id}/query")
async def query_document_v1(doc_id: str, req: QueryRequest, model: Optional[str] = Query("gemini-2.5-flash")):
    if not req.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        response_data = await rag_service.query(question=req.question, doc_id=doc_id, model=model)
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Query Error: {str(e)}")

# ── Legacy Root API Endpoints (Backward Compatible) ─────────────────────────
@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    content = await file.read()
    try:
        text = parse_file(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    doc_id = str(uuid.uuid4())
    try:
        rag_service.insert_document(doc_id=doc_id, text=text)
    except Exception as e:
        print(f"Warning: Legacy upload RAG indexing skipped/deferred ({e})")
    
    ext = file.filename.split('.')[-1].lower() if '.' in file.filename else 'txt'
    db.add_document(
        doc_id=doc_id,
        filename=file.filename,
        file_type=ext,
        file_size=len(content),
        text_content=text
    )
    return {"message": "Document parsed and embedded successfully", "doc_id": doc_id, "filename": file.filename}

@app.post("/api/summary")
async def summarize_document(doc_id: str = Form(...)):
    if not doc_id:
        raise HTTPException(status_code=400, detail="Missing doc_id")
    try:
        summary_text = await rag_service.summarize(doc_id)
        return {"summary": summary_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary Error: {str(e)}")

@app.post("/api/entities")
async def extract_entities(doc_id: str = Form(...)):
    if not doc_id:
        raise HTTPException(status_code=400, detail="Missing doc_id")
    try:
        entities = await rag_service.extract_entities(doc_id)
        return {"entities": entities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Entity Extraction Error: {str(e)}")

@app.post("/api/query")
async def query_model(query: str = Form(...)):
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        response_data = await rag_service.query(query)
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")

@app.post("/api/score")
async def score_document(doc_id: str = Form(...)):
    if not doc_id:
        raise HTTPException(status_code=400, detail="Missing doc_id")
    try:
        score_data = await rag_service.score_document(doc_id)
        return score_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
