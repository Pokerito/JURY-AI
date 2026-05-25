from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.services.rag_service import RAGService
from backend.services.file_parser import parse_file
import uuid

app = FastAPI(title="Jury-AI API", description="Legal Intelligence Platform API v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_service = RAGService()

@app.get("/")
def read_root():
    return {"status": "Jury-AI is running", "version": "2.0"}

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
    rag_service.insert_document(doc_id=doc_id, text=text)
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
    """Feature 10 — Extract named entities from the document."""
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
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
