import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb

DATASET_PATH = Path("data/evaluation/evaluation_questions.json")
CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "academic_rag_chunks_v1"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
TOP_K = 5

def main():
    if not DATASET_PATH.exists():
        print("Dataset not found")
        return
        
    with DATASET_PATH.open("r", encoding="utf-8") as f:
        questions = json.load(f)
        
    db = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = db.get_collection(name=COLLECTION_NAME)
    embedder = SentenceTransformer(EMBEDDING_MODEL)
    
    selected_ids = ["Q01", "Q02", "Q03", "Q13", "Q14"]
    selected_questions = [q for q in questions if q["id"] in selected_ids]
    
    audit_data = []
    
    for q in selected_questions:
        query_vector = embedder.encode([q["question"]], normalize_embeddings=True)[0].tolist()
        result = collection.query(
            query_embeddings=[query_vector],
            n_results=TOP_K,
            include=["documents", "metadatas", "distances"]
        )
        
        docs = result["documents"][0] if result["documents"] else []
        metas = result["metadatas"][0] if result["metadatas"] else []
        
        sources = []
        for d, m in zip(docs, metas):
            sources.append({
                "source": m.get("source"),
                "page_start": m.get("page_start"),
                "page_end": m.get("page_end"),
                "text_preview": d[:100].replace("\n", " ") + "..." if d else ""
            })
            
        audit_data.append({
            "id": q["id"],
            "question": q["question"],
            "answerable": q.get("answerable", True),
            "expected_pages": q.get("expected_source_pages", []),
            "retrieved_sources": sources
        })
        
    with open("data/evaluation/offline_audit.json", "w") as f:
        json.dump(audit_data, f, indent=2)
        
    print("Offline retrieval audit complete")

if __name__ == "__main__":
    main()
