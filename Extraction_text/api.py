import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from dotenv import load_dotenv
from groq import Groq
import chromadb
from sentence_transformers import SentenceTransformer

# Import existing RAG utilities
from answer import retrieve_evidence, build_prompt

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
DB_PATH = "data/chroma_db"
COLLECTION_NAME = "academic_rag_chunks_v1"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
TOP_K = 5

if not API_KEY:
    raise RuntimeError("GROQ_API_KEY is missing in .env")

client = Groq(api_key=API_KEY)

db = chromadb.PersistentClient(path=DB_PATH)
collection = db.get_collection(name=COLLECTION_NAME)
if collection.count() == 0:
    raise RuntimeError("The Chroma collection is empty.")

embedding_model = SentenceTransformer(EMBEDDING_MODEL)

app = FastAPI(title="Academic RAG API", version="1.0")

class AskRequest(BaseModel):
    question: str

class Source(BaseModel):
    label: str
    filename: str
    page_start: int | None = None
    page_end: int | None = None
    text: str

class AnswerResponse(BaseModel):
    answer: str
    sources: List[Source]

@app.post("/ask", response_model=AnswerResponse)
async def ask(request: AskRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # Retrieve evidence using the existing logic
    evidence = retrieve_evidence(question, collection, embedding_model)
    if not evidence:
        raise HTTPException(status_code=404, detail="No evidence retrieved for the question")

    prompt = build_prompt(question, evidence)
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=4096,
        )
        answer_text = response.choices[0].message.content or ""
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Groq request failed: {exc}")

    # Build source list preserving labels and PDF metadata
    sources = [
        Source(
            label=item["source_id"],
            filename=item["source"],
            page_start=item.get("page_start"),
            page_end=item.get("page_end"),
            text=item.get("text", ""),
        )
        for item in evidence
    ]

    return AnswerResponse(answer=answer_text, sources=sources)
