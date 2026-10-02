
import json
import os
import re
import time
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai
from groq import Groq
from sentence_transformers import SentenceTransformer


# ---------- Configuration ----------
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

DATASET_PATH = Path("data/evaluation/evaluation_questions.json")
RESULTS_PATH = Path("data/evaluation/evaluation_results.json")
CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "academic_rag_chunks_v1"

TOP_K = 5

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from your .env file.")

client = Groq(api_key=API_KEY)


def load_collection():
    db = chromadb.PersistentClient(path=CHROMA_PATH)
    return db.get_collection(name=COLLECTION_NAME)


def retrieve(question, collection, embedder):
    query_vector = embedder.encode(
        [question],
        normalize_embeddings=True
    )[0].tolist()

    result = collection.query(
        query_embeddings=[query_vector],
        n_results=TOP_K,
        include=["documents", "metadatas", "distances"]
    )

    documents = result["documents"][0] or []
    metadatas = result["metadatas"][0] or []
    distances = result["distances"][0] or []

    sources = []

    for i, (document, metadata) in enumerate(
        zip(documents, metadatas)
    ):
        sources.append({
            "label": f"S{i + 1}",
            "text": document or "",
            "source": metadata.get("source", "Unknown"),
            "page_start": metadata.get("page_start"),
            "page_end": metadata.get("page_end"),
            "distance": distances[i] if i < len(distances) else None
        })

    return sources


def generate_answer(question, sources):
    if not sources:
        return "INSUFFICIENT_EVIDENCE: No passages were retrieved."

    evidence = []

    for source in sources:
        evidence.append(
            f"[{source['label']}]\n"
            f"PDF: {source['source']}\n"
            f"Pages: {source['page_start']}-"
            f"{source['page_end']}\n"
            f"Text: {source['text']}"
        )

    prompt = f"""
You are an academic question-answering assistant.

Answer the question using ONLY the evidence below.

Rules:
1. Do not invent facts or use outside knowledge.
2. Cite supporting evidence using labels such as [S1] or [S2].
3. Put citations next to the claims they support.
4. If the evidence is insufficient, say:
   "INSUFFICIENT_EVIDENCE: The provided PDFs do not
   contain enough information to answer this question."
5. Do not cite a source that does not support your claim.

QUESTION:
{question}

RETRIEVED EVIDENCE:
{chr(10).join(evidence)}
"""

    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=2048,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            msg = str(exc)
            # Parse retryDelay from error payload when present
            retry_match = re.search(r"retryDelay.*?(\d+)s", msg)
            wait = int(retry_match.group(1)) + 2 if retry_match else 20
            is_retryable = (
                "429" in msg
                or "503" in msg
                or "RESOURCE_EXHAUSTED" in msg
                or "UNAVAILABLE" in msg
            )
            if attempt == 0 and is_retryable:
                print(f"  Retryable error ({msg[:60]}…). Waiting {wait}s then retrying.")
                time.sleep(wait)
            else:
                raise


def page_matches(expected, source):
    """Check whether a retrieved chunk overlaps an expected page."""
    if expected.get("source") != source.get("source"):
        return False

    expected_page = expected.get("page")

    if not isinstance(expected_page, int):
        return False

    start = source.get("page_start")
    end = source.get("page_end")

    if not isinstance(start, int) or not isinstance(end, int):
        return False

    return start <= expected_page <= end


def main():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Evaluation dataset not found: {DATASET_PATH}"
        )

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        questions = json.load(file)

    collection = load_collection()
    embedder = SentenceTransformer(EMBEDDING_MODEL)

    results = []

    # Load existing results to allow continuing safely
    if RESULTS_PATH.exists():
        with RESULTS_PATH.open("r", encoding="utf-8") as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                pass

    # Only skip questions that were previously answered successfully (not API failures)
    processed_ids = {
        r.get("id") for r in results
        if r.get("id") and not r.get("api_failure")
    }
    # Remove failed entries from results list so they can be re-added cleanly
    results = [r for r in results if not r.get("api_failure")]

    for index, item in enumerate(questions, start=1):
        question_id = item["id"]
        if question_id in processed_ids:
            continue

        question = item["question"]

        print(f"\n[{index}/{len(questions)}] {question_id}: {question}")

        sources = retrieve(question, collection, embedder)

        api_failure = False
        if sources:
            try:
                answer = generate_answer(question, sources)
                # Throttle to stay within 5 RPM free-tier limit
                time.sleep(13)
            except Exception as e:
                answer = f"API_FAILURE: {e}"
                api_failure = True
        else:
            answer = (
                "INSUFFICIENT_EVIDENCE: No passages were retrieved."
            )

        # Check whether cited labels exist among retrieved sources.
        cited_labels = sorted(set(
            re.findall(r"\[(S\d+)\]", answer)
        ))

        available_labels = {
            source["label"] for source in sources
        }

        invalid_labels = [
            label for label in cited_labels
            if label not in available_labels
        ]

        # Check if any retrieved chunk overlaps a manually
        # verified expected source page.
        expected_pages = item.get("expected_source_pages", [])

        retrieval_hit = None

        if item.get("answerable") and expected_pages:
            retrieval_hit = any(
                page_matches(expected, source)
                for expected in expected_pages
                for source in sources
            )

        # A basic signal only, not proof of correct abstention.
        answer_lower = answer.lower()

        abstention_phrases = [
            "insufficient_evidence",
            "not enough information",
            "do not contain enough information",
            "cannot determine from the provided",
            "cannot answer from the provided"
        ]

        appears_to_abstain = any(
            phrase in answer_lower
            for phrase in abstention_phrases
        )

        result = {
            "id": question_id,
            "question": question,
            "answerable": item.get("answerable"),
            "api_failure": api_failure,
            "answer": answer,
            "cited_labels": cited_labels,
            "invalid_citation_labels": invalid_labels,
            "citation_labels_valid": len(invalid_labels) == 0,
            "retrieval_hit_expected_page": retrieval_hit,
            "appears_to_abstain": appears_to_abstain,
            "expected_concepts": item.get("expected_concepts", []),
            "expected_source_pages": expected_pages,
            "retrieved_sources": [
                {
                    "label": source["label"],
                    "source": source["source"],
                    "page_start": source["page_start"],
                    "page_end": source["page_end"],
                    "distance": source["distance"]
                }
                for source in sources
            ],
            "manual_answer_support_check": "NOT_REVIEWED",
            "manual_citation_support_check": "NOT_REVIEWED"
        }

        results.append(result)

        print("Answer:", answer)
        print("Cited labels:", cited_labels)
        print("Invalid citation labels:", invalid_labels)
        print("Expected page retrieved:", retrieval_hit)

        # Save incrementally
        RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with RESULTS_PATH.open("w", encoding="utf-8") as file:
            json.dump(results, file, indent=2, ensure_ascii=False)

    print("\n========== EVALUATION SUMMARY ==========")
    total_questions = len(results)

    api_failures = sum(1 for r in results if r.get("api_failure"))
    print(f"Total questions tested: {total_questions}")
    print(f"API failures: {api_failures}")

    # Retrieval success: hits / answerable questions
    answerable_total = sum(1 for r in results if r.get("answerable"))
    retrieval_hits = sum(1 for r in results if r.get("answerable") and r.get("retrieval_hit_expected_page"))
    print(f"Retrieval success: {retrieval_hits}/{answerable_total}")

    # Citation validity: valid labels / (answerable & non-failed & hit)
    citation_valid_candidates = [
        r for r in results 
        if r.get("answerable") and not r.get("api_failure") and r.get("retrieval_hit_expected_page")
    ]
    citation_valid_count = sum(1 for r in citation_valid_candidates if r.get("citation_labels_valid"))
    print(f"Citation validity (only labels exist): {citation_valid_count}/{len(citation_valid_candidates) if citation_valid_candidates else 0}")

    # Abstention: (unanswerable OR retrieval miss) -> did it abstain?
    abstention_candidates = [
        r for r in results
        if not r.get("api_failure") and (not r.get("answerable") or r.get("retrieval_hit_expected_page") is False)
    ]
    abstention_success = sum(1 for r in abstention_candidates if r.get("appears_to_abstain"))
    print(f"Abstention success (fallback/insufficient): {abstention_success}/{len(abstention_candidates) if abstention_candidates else 0}")

    print("\nReminder: 'valid labels' means [S#] exists in context.")
    print("Verify claim support (evidence support) and page accuracy manually.")
    print("Results saved to:", RESULTS_PATH)


if __name__ == "__main__":
    main()