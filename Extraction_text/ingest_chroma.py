
import json
from pathlib import Path

import chromadb
import numpy as np


# ---------- Configuration ----------

EMBEDDING_DIR = Path("data/embeddings")
VECTOR_PATH = EMBEDDING_DIR / "vectors.npy"
METADATA_PATH = EMBEDDING_DIR / "metadata.json"

DB_PATH = "data/chroma_db"
COLLECTION_NAME = "academic_rag_chunks_v1"
BATCH_SIZE = 100


def main():
    # Load the existing embedding artifacts.
    vectors = np.load(VECTOR_PATH, allow_pickle=False)

    with METADATA_PATH.open("r", encoding="utf-8") as f:
        records = json.load(f)

    if not isinstance(records, list) or not records:
        raise ValueError("metadata.json must contain chunk records.")

    if vectors.ndim != 2:
        raise ValueError("Expected a 2D embedding array.")

    if vectors.shape[0] != len(records):
        raise ValueError("Vector and metadata counts do not match.")

    if not np.isfinite(vectors).all():
        raise ValueError("Vectors contain invalid numeric values.")

    required = [
        "chunk_id", "document_id", "source",
        "page_start", "page_end", "text",
    ]

    ids = []

    for record in records:
        missing = [key for key in required if key not in record]
        if missing:
            raise ValueError(
                f"Missing required metadata fields: {missing}"
            )

        if not isinstance(record["text"], str) or not record["text"].strip():
            raise ValueError(f"Empty text: {record['chunk_id']}")

        start = record["page_start"]
        end = record["page_end"]

        if (
            not isinstance(start, int)
            or isinstance(start, bool)
            or not isinstance(end, int)
            or isinstance(end, bool)
            or start < 1
            or end < start
        ):
            raise ValueError(
                f"Invalid page range for {record['chunk_id']}"
            )

        if not record["source"] or not record["document_id"]:
            raise ValueError(
                f"Missing source information: {record['chunk_id']}"
            )

        ids.append(str(record["chunk_id"]))

    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate chunk IDs found.")

    # PersistentClient saves data locally between runs.
    client = chromadb.PersistentClient(path=DB_PATH)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Upsert makes rerunning this script safe for the same IDs.
    # It updates matching IDs without adding duplicate copies.
    for start in range(0, len(records), BATCH_SIZE):
        end = min(start + BATCH_SIZE, len(records))

        batch_records = records[start:end]
        batch_vectors = vectors[start:end]

        documents = [r["text"] for r in batch_records]
        batch_ids = [str(r["chunk_id"]) for r in batch_records]

        metadatas = []

        for r in batch_records:
            meta = {
                "document_id": str(r["document_id"]),
                "source": str(r["source"]),
                "page_start": int(r["page_start"]),
                "page_end": int(r["page_end"]),
                "embedding_model": str(
                    r.get("embedding_model", "BAAI/bge-small-en-v1.5")
                ),
            }

            # Chroma metadata values must be supported scalar types.
            section = r.get("section")
            if isinstance(section, str) and section.strip():
                meta["section"] = section

            metadatas.append(meta)

        collection.upsert(
            ids=batch_ids,
            embeddings=batch_vectors.tolist(),
            documents=documents,
            metadatas=metadatas,
        )

    # Verify all imported IDs exist.
    stored = collection.get(ids=ids, include=["metadatas"])

    if set(stored["ids"]) != set(ids):
        raise RuntimeError("Not all expected chunks were stored.")

    print("\nChroma ingestion completed.")
    print(f"Input chunks: {len(records)}")
    print(f"Collection count: {collection.count()}")
    print(f"Vector dimensions: {vectors.shape[1]}")
    print(f"Storage path: {DB_PATH}")
    print(f"Collection: {COLLECTION_NAME}")


if __name__ == "__main__":
    main()
    
