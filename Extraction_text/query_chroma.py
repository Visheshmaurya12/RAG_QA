
import chromadb
from sentence_transformers import SentenceTransformer


DB_PATH = "data/chroma_db"
COLLECTION_NAME = "academic_rag_chunks_v1"
MODEL_NAME = "BAAI/bge-small-en-v1.5"
TOP_K = 5


def main():
    client = chromadb.PersistentClient(path=DB_PATH)

    collection = client.get_collection(
        name=COLLECTION_NAME
    )

    if collection.count() == 0:
        raise ValueError("The Chroma collection is empty.")

    model = SentenceTransformer(MODEL_NAME)

    print(f"Loaded {collection.count()} stored chunks.")

    while True:
        question = input(
            "\nAsk a question (or type 'exit'): "
        ).strip()

        if question.lower() == "exit":
            break

        if not question:
            print("Please enter a question.")
            continue

        query_vector = model.encode(
            question,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        results = collection.query(
            query_embeddings=[query_vector.tolist()],
            n_results=min(TOP_K, collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        print("\n===== RETRIEVED EVIDENCE =====")

        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for rank, (chunk_id, text, meta, distance) in enumerate(
            zip(ids, documents, metadatas, distances),
            start=1,
        ):
            print(f"\nResult {rank}")
            print(f"Chunk ID: {chunk_id}")
            print(f"Source: {meta['source']}")
            print(
                f"Original PDF pages: "
                f"{meta['page_start']}-{meta['page_end']}"
            )

            if meta.get("section"):
                print(f"Section: {meta['section']}")

            # Cosine distance is lower for closer vectors.
            print(f"Cosine distance: {distance:.4f}")
            print(f"Text:\n{text}")

        print("\n===============================")


if __name__ == "__main__":
    main()
    