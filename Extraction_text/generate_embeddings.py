
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


# ---------- Configuration ----------

INPUT_DIR = Path("data/processed_chunks")
OUTPUT_DIR = Path("data/embeddings")

MODEL_NAME = "BAAI/bge-small-en-v1.5"
BATCH_SIZE = 16

REQUIRED_FIELDS = [
    "chunk_id",
    "document_id",
    "source",
    "page_start",
    "page_end",
    "text",
]

# ---------- Load chunk records ----------

def extract_records(data, file_path):
    """Accept common JSON structures without guessing page numbers."""

    if isinstance(data, list):
        records = data

    elif isinstance(data, dict):
        records = None

        for key in ("chunks", "records", "data"):
            if isinstance(data.get(key), list):
                records = data[key]
                break

        if records is None and "text" in data:
            records = [data]

        if records is None:
            raise ValueError(
                f"Unsupported JSON structure in {file_path}"
            )
    else:
        raise ValueError(f"Invalid JSON structure in {file_path}")

    for record in records:
        if not isinstance(record, dict):
            raise ValueError(
                f"Non-object chunk found in {file_path}"
            )

        missing = [
            field for field in REQUIRED_FIELDS
            if field not in record
        ]

        if missing:
            raise ValueError(
                f"{file_path}: missing fields {missing}"
            )

    return records


def load_chunks():
    files = sorted(INPUT_DIR.rglob("*.json"))

    if not files:
        raise FileNotFoundError(
            f"No JSON files found in {INPUT_DIR}"
        )

    all_chunks = []

    for file_path in files:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        records = extract_records(data, file_path)

        for record in records:
            # Keep all original metadata and text.
            all_chunks.append(dict(record))

    if not all_chunks:
        raise ValueError("No chunks were loaded.")

    ids = [c["chunk_id"] for c in all_chunks]

    if len(ids) != len(set(ids)):
        raise ValueError(
            "Duplicate chunk_id values found. "
            "Resolve them before generating embeddings."
        )

    for chunk in all_chunks:
        if not isinstance(chunk["text"], str) or not chunk["text"].strip():
            raise ValueError(
                f"Empty text in chunk {chunk['chunk_id']}"
            )

        start = chunk["page_start"]
        end = chunk["page_end"]

        if (
            not isinstance(start, int)
            or isinstance(start, bool)
            or not isinstance(end, int)
            or isinstance(end, bool)
            or start < 1
            or end < start
        ):
            raise ValueError(
                f"Invalid original page range for "
                f"{chunk['chunk_id']}: {start}-{end}"
            )

        if not chunk["source"] or not chunk["document_id"]:
            raise ValueError(
                f"Missing source metadata for {chunk['chunk_id']}"
            )

    return files, all_chunks


# ---------- Load model and check token limits ----------

def main():
    if not INPUT_DIR.exists():
        raise FileNotFoundError(
            f"Input directory does not exist: {INPUT_DIR}"
        )

    files, chunks = load_chunks()

    print(f"Input JSON files: {len(files)}")
    print(f"Chunks loaded: {len(chunks)}")
    print(f"Loading model: {MODEL_NAME}")

    model = SentenceTransformer(MODEL_NAME)
    tokenizer = model.tokenizer
    max_length = model.max_seq_length

    # Check the actual model tokenizer BEFORE encoding.
    oversized = []

    for chunk in chunks:
        token_ids = tokenizer.encode(
            chunk["text"],
            add_special_tokens=True,
            truncation=False,
        )

        if len(token_ids) > max_length:
            oversized.append(
                (chunk["chunk_id"], len(token_ids))
            )

    if oversized:
        examples = oversized[:10]
        raise ValueError(
            f"{len(oversized)} chunks exceed the model's "
            f"{max_length}-token input limit. "
            f"Example chunk IDs and token counts: {examples}. "
            "Adjust chunking for these records before retrying. "
            "No embedding files have been saved."
        )

    # ---------- Generate vectors ----------

    texts = [chunk["text"] for chunk in chunks]

    vectors = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    vectors = np.asarray(vectors, dtype=np.float32)

    # ---------- Validate vectors ----------

    if vectors.ndim != 2:
        raise ValueError("Embeddings must be a 2D array.")

    if vectors.shape[0] != len(chunks):
        raise ValueError(
            "Embedding count does not match chunk count."
        )

    if not np.isfinite(vectors).all():
        raise ValueError(
            "Embeddings contain NaN or infinite values."
        )

    if not np.allclose(
        np.linalg.norm(vectors, axis=1),
        1.0,
        atol=1e-4,
    ):
        raise ValueError(
            "Expected normalized vectors; norm check failed."
        )

    # ---------- Save separate artifacts ----------

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Row i in this array belongs to record i in the manifest.
    np.save(OUTPUT_DIR / "vectors.npy", vectors)

    manifest = []

    for chunk in chunks:
        record = dict(chunk)
        record["embedding_model"] = MODEL_NAME
        record["embedding_dimension"] = int(vectors.shape[1])
        record["normalized"] = True
        manifest.append(record)

    with (OUTPUT_DIR / "metadata.json").open(
        "w", encoding="utf-8"
    ) as f:
        json.dump(
            manifest,
            f,
            ensure_ascii=False,
            indent=2,
        )

    summary = {
        "model": MODEL_NAME,
        "chunk_count": len(chunks),
        "vector_count": int(vectors.shape[0]),
        "dimension": int(vectors.shape[1]),
        "normalized": True,
        "source_json_files": len(files),
        "outputs": [
            str(OUTPUT_DIR / "vectors.npy"),
            str(OUTPUT_DIR / "metadata.json"),
        ],
    }

    with (OUTPUT_DIR / "summary.json").open(
        "w", encoding="utf-8"
    ) as f:
        json.dump(summary, f, indent=2)

    print("\nEmbedding generation completed.")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
