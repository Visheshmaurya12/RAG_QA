
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


# ---------- Configuration ----------

EMBEDDING_DIR = Path("data/embeddings")
VECTORS_PATH = EMBEDDING_DIR / "vectors.npy"
METADATA_PATH = EMBEDDING_DIR / "metadata.json"

MODEL_NAME = "BAAI/bge-small-en-v1.5"
TOP_K = 5


# ---------- Load saved artifacts ----------

def load_artifacts():
    if not VECTORS_PATH.exists():
        raise FileNotFoundError(f"Missing file: {VECTORS_PATH}")

    if not METADATA_PATH.exists():
        raise FileNotFoundError(f"Missing file: {METADATA_PATH}")

    vectors = np.load(VECTORS_PATH, allow_pickle=False)

    with METADATA_PATH.open("r", encoding="utf-8") as f:
        metadata = json.load(f)

    if not isinstance(metadata, list):
        raise ValueError("metadata.json must contain a JSON list.")

    if vectors.ndim != 2:
        raise ValueError("vectors.npy must be a 2D array.")

    if len(metadata) != vectors.shape[0]:
        raise ValueError(
            "Vector count and metadata count do not match."
        )

    if vectors.shape[0] == 0:
        raise ValueError("No vectors found.")

    if not np.isfinite(vectors).all():
        raise ValueError("Vectors contain invalid numeric values.")

    required = [
        "chunk_id",
        "document_id",
        "source",
        "page_start",
        "page_end",
        "text",
    ]

    for i, record in enumerate(metadata):
        missing = [key for key in required if key not in record]

        if missing:
            raise ValueError(
                f"Metadata row {i} is missing: {missing}"
            )

        if not isinstance(record["text"], str) or not record["text"].strip():
            raise ValueError(
                f"Empty text for chunk {record['chunk_id']}"
            )

    # The model used to create the stored vectors must match.
    recorded_models = {
        record.get("embedding_model") for record in metadata
    }

    if recorded_models != {MODEL_NAME}:
        raise ValueError(
            f"Stored embedding model mismatch: {recorded_models}"
        )

    if vectors.shape[1] != 384:
        raise ValueError(
            f"Expected 384 dimensions, got {vectors.shape[1]}"
        )

    # Embeddings from our generation script were normalized.
    norms = np.linalg.norm(vectors, axis=1)

    if not np.allclose(norms, 1.0, atol=1e-4):
        raise ValueError(
            "Stored vectors are not normalized as expected."
        )

    return vectors, metadata


# ---------- Retrieve relevant chunks ----------

def retrieve(question, model, vectors, metadata, top_k=TOP_K):
    if not question.strip():
        raise ValueError("Please enter a non-empty question.")

    # Embed the question with the same model.
    query_vector = model.encode(
        question,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    query_vector = np.asarray(query_vector, dtype=np.float32)

    if query_vector.shape != (vectors.shape[1],):
        raise ValueError(
            "Question vector dimensions do not match stored vectors."
        )

    # Normalized vectors: dot product equals cosine similarity.
    scores = vectors @ query_vector

    # Sort scores from highest to lowest.
    top_k = min(max(1, top_k), len(metadata))
    indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for index in indices:
        record = metadata[int(index)]

        results.append({
            "chunk_id": record["chunk_id"],
            "document_id": record["document_id"],
            "source": record["source"],
            "page_start": record["page_start"],
            "page_end": record["page_end"],
            "section": record.get("section"),
            "text": record["text"],
            "similarity": float(scores[index]),
        })

    return results


# ---------- Display results ----------

def main():
    vectors, metadata = load_artifacts()

    print(f"Loaded {len(metadata)} chunks.")
    print(f"Vector dimensions: {vectors.shape[1]}")
    print(f"Embedding model: {MODEL_NAME}")

    print("\nLoading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    while True:
        question = input(
            "\nEnter an academic question (or type 'exit'): "
        ).strip()

        if question.lower() == "exit":
            break

        if not question:
            print("Please enter a question.")
            continue

        results = retrieve(
            question,
            model,
            vectors,
            metadata,
        )

        print("\n========== RETRIEVAL RESULTS ==========")

        for rank, result in enumerate(results, start=1):
            print(f"\nResult {rank}")
            print(f"Chunk ID: {result['chunk_id']}")
            print(f"Source: {result['source']}")
            print(
                f"Original PDF pages: "
                f"{result['page_start']}-{result['page_end']}"
            )
            print(f"Similarity: {result['similarity']:.4f}")

            if result["section"]:
                print(f"Section: {result['section']}")

            print(f"\nText:\n{result['text']}")

        print("\n=======================================")


if __name__ == "__main__":
    main()