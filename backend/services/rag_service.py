import os
import asyncio
import json
import re
from google import genai
from backend.database.chroma_client import ChromaClient
from dotenv import load_dotenv

load_dotenv()

class RAGService:
    def __init__(self):
        try:
            self.genai_client = genai.Client()
        except Exception:
            self.genai_client = None

        self.chroma_client = ChromaClient().client
        self.collection = self.chroma_client.get_or_create_collection(name="jury_ai_docs_v2")

    def _get_embedding(self, text: str) -> list[float]:
        if not self.genai_client:
            return [0.0] * 3072
        response = self.genai_client.models.embed_content(
            model='gemini-embedding-2',
            contents=text,
        )
        return response.embeddings[0].values

    def insert_document(self, doc_id: str, text: str):
        chunks = [text[i:i+1000] for i in range(0, len(text), 1000) if text[i:i+1000].strip()]
        embeddings, ids, metadatas = [], [], []
        for idx, chunk in enumerate(chunks):
            embeddings.append(self._get_embedding(chunk))
            ids.append(f"{doc_id}_chunk_{idx}")
            metadatas.append({"doc_id": doc_id, "chunk_index": idx})
        if chunks:
            self.collection.add(embeddings=embeddings, documents=chunks, metadatas=metadatas, ids=ids)

    def _sync_generate(self, prompt: str) -> str:
        if not self.genai_client:
            return f"[Simulated Response - No API Key]\n\n{prompt[:100]}..."
        try:
            response = self.genai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            return response.text
        except Exception as e:
            # Fallback to gemini-2.0-flash if 2.5-flash is experiencing high demand (503) or is otherwise unavailable
            response = self.genai_client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
            )
            return response.text

    def _get_full_text(self, doc_id: str, cap: int = 30000) -> str:
        results = self.collection.get(where={"doc_id": doc_id})
        if not results['documents']:
            return ""
        text = "\n".join(results['documents'])
        return text[:cap] if len(text) > cap else text

    # ── Query ───────────────────────────────────────────────────────────────
    async def query(self, question: str) -> dict:
        question_emb = await asyncio.to_thread(self._get_embedding, question)
        results = await asyncio.to_thread(
            self.collection.query,
            query_embeddings=[question_emb],
            n_results=3
        )
        retrieved = results['documents'][0] if results['documents'] and results['documents'][0] else []
        context = "\n---\n".join(retrieved) or "No relevant context found."
        prompt = f"""You are a Legal AI Assistant. Answer the user's question accurately using only the Context provided.

Context:
{context}

Question: {question}"""
        answer = await asyncio.to_thread(self._sync_generate, prompt)
        return {"answer": answer}

    # ── Feature 2: Summary ──────────────────────────────────────────────────
    async def summarize(self, doc_id: str) -> str:
        full_text = await asyncio.to_thread(self._get_full_text, doc_id, 8000)
        if not full_text:
            return "No document content found."
        prompt = f"""You are a legal document analyst. Write a concise 2-3 sentence plain-English summary of this legal document.
Mention: what type of agreement it is, who the parties are (if mentioned), and the key subject matter.
Be direct and factual. No bullet points.

Document:
{full_text}

Summary:"""
        summary = await asyncio.to_thread(self._sync_generate, prompt)
        return summary.strip()

    # ── Feature 10: Named Entity Extraction ────────────────────────────────
    async def extract_entities(self, doc_id: str) -> dict:
        full_text = await asyncio.to_thread(self._get_full_text, doc_id, 8000)
        if not full_text:
            return {"parties": [], "dates": [], "amounts": [], "jurisdictions": []}

        prompt = f"""Extract key named entities from this legal document. Return ONLY raw JSON, no markdown, no code blocks.
Use exactly this format:
{{
  "parties": ["list of company or person names who are parties to this agreement"],
  "dates": ["list of dates, time periods, or durations mentioned"],
  "amounts": ["list of monetary amounts, fees, or financial figures"],
  "jurisdictions": ["list of jurisdictions, governing law, courts, or arbitration locations"]
}}
If none found for a category, use an empty array [].

Document:
{full_text}"""

        raw = await asyncio.to_thread(self._sync_generate, prompt)
        cleaned = re.sub(r'```json', '', raw)
        cleaned = re.sub(r'```', '', cleaned).strip()
        try:
            entities = json.loads(cleaned)
            return entities
        except json.JSONDecodeError:
            return {"parties": [], "dates": [], "amounts": [], "jurisdictions": []}

    # ── Scoring (Feature 9: safer_alternative added) ───────────────────────
    async def score_document(self, doc_id: str) -> dict:
        full_text = await asyncio.to_thread(self._get_full_text, doc_id, 30000)
        if not full_text:
            return {"score": 100, "checklist": [], "all_clauses": [], "error": "Document not found."}

        prompt = f"""You are a legal risk algorithm. Analyze the document context below.
Identify ALL clauses and classify their risk. Return ONLY a pure JSON array. No markdown. No code blocks. JUST THE RAW JSON ARRAY.
Format:
[
  {{
    "clause_name": "Short name for the clause",
    "risk_level": "Critical" | "High" | "Medium" | "Low",
    "justification": "Brief reason for this risk level",
    "safer_alternative": "For Critical/High only: a fairer alternative clause wording. For Medium/Low: null"
  }}
]
Include ALL clauses you find — even safe ones with "Low" rating.

Context:
{full_text}"""

        raw_response = await asyncio.to_thread(self._sync_generate, prompt)
        cleaned = re.sub(r'```json', '', raw_response)
        cleaned = re.sub(r'```', '', cleaned).strip()

        all_clauses = []
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                all_clauses = parsed
        except json.JSONDecodeError:
            pass

        base_score = 100
        for item in all_clauses:
            risk = str(item.get("risk_level", "")).lower()
            if "critical" in risk:
                base_score -= 25
            elif "high" in risk:
                base_score -= 15
            elif "medium" in risk:
                base_score -= 5

        final_score = max(0, base_score)
        filtered_checklist = [i for i in all_clauses if str(i.get("risk_level", "")).lower() in ["critical", "high"]]

        return {
            "score": final_score,
            "checklist": filtered_checklist,
            "all_clauses": all_clauses,
        }
